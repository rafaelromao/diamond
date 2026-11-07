"""Check all controller-facing nets on the routed panel, in KiCad Python.

GPIO compatibility is checked against the four firmware overlays by test_xiao_option.
This checks the actual PCB pad assignments; DRC checks copper continuity separately.
"""
import json
from pathlib import Path
import pcbnew

root = Path(__file__).resolve().parent
board = pcbnew.LoadBoard(str(root / 'pcb/trackball.kicad_pcb'))
footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
expected = {
    **{f'J{i}': {'1': net} for i, net in enumerate(
        ('SCLK', 'SDIO', 'NCS', 'MOTION', 'RST', 'VCC', 'GND', 'BAT+', 'GND', 'VBAT', 'RST'), 1)},
    'JP1': {'1': 'M_L3', '2': 'M_3V', '3': 'M_L4'},
    **{f'SJ{i}': {'1': 'S_' + net} for i, net in enumerate(
        ('VCC', 'GND', 'RST', 'SCLK', 'SDIO', 'NCS', 'MOTION'), 1)},
    'SW1': {'1': 'GND', '2': 'K1'},
    'SW2': {'1': 'GND', '2': 'K2'},
    'SW3': {'1': 'BAT+', '2': 'VBAT', '3': 'VBAT', 'SH': 'GND'},
    'S3': {'1': 'S_RST', '2': 'S_GND'},
}
for ref, nets in expected.items():
    seen = set()
    for pad in footprints[ref].Pads():
        number = pad.GetNumber()
        if number in nets:
            assert pad.GetNetname() == nets[number], (ref, number, pad.GetNetname(), nets[number])
            seen.add(number)
    assert seen == nets.keys(), (ref, seen, nets)
design = json.loads((root / 'design.json').read_text())
at = lambda p: (round(p[0], 3), round(p[1], 3))
pads = {}
for fp in board.GetFootprints():
    for pad in fp.Pads():
        c = pad.GetPosition()
        pads[at((pcbnew.ToMM(c.x) - 100, pcbnew.ToMM(c.y) - 100))] = pad.GetNetname()
names = dict(G='GND', L3='L3', L4='L4', CS='CS', K2='K2', K1='K1', CK='CK', IO='IO', MO='MO')
for name, pin in design['controller_pins'].items():
    want = 'M_' + names[pin['net']] if pin['net'] else ''
    assert pads[at(pin['xy'])] == want, (name, pads[at(pin['xy'])], want)
short = dict(NCS='CS', K2='K2', K1='K1', GND='GND', VCC='3V', SCLK='CK', SDIO='IO', MOTION='MO')
assert design['main_links'].keys() == design['controller_links'].keys()
for name, link in design['main_links'].items():
    other = design['controller_links'][name]
    assert pads[at(link['xy'])] == link['net'], (name, pads[at(link['xy'])])
    assert pads[at(other['xy'])] == 'M_' + short[other['net']], (name, pads[at(other['xy'])])
    assert link['net'] == other['net'], name
jumper = footprints['JP1']
middle = next(p for p in jumper.Pads() if p.GetNumber() == '2').GetPosition()
xiao_side = next(p for p in jumper.Pads() if p.GetNumber() == '1').GetPosition()
# The board lies a quarter turn round on the panel: its left, the XIAO's X pad, is downwards.
assert xiao_side.y > middle.y and xiao_side.x == middle.x, (xiao_side, middle)
# Both boards' stacking holes, taken back from the panel into the module's plan: they must coincide.
# The controller board lies a quarter turn round on the panel: KiCad (X, Y) = (-py + ox, -(px + oy)).
ox, oy = design['controller_offset']
def plan_of(ref):
    c = footprints[ref].GetPosition()
    X, Y = pcbnew.ToMM(c.x) - 100, pcbnew.ToMM(c.y) - 100
    return (-Y - oy, ox - X) if ref.startswith('M') else (X, -Y)
pairs = {}
for i, (name, link) in enumerate(design['main_links'].items(), 1):
    main_xy, ctrl_xy = plan_of(f'L{i}'), plan_of(f'ML{i}')
    off = ((main_xy[0] - ctrl_xy[0]) ** 2 + (main_xy[1] - ctrl_xy[1]) ** 2) ** .5
    pairs[name] = dict(net=link['net'], main=[round(v, 4) for v in main_xy], controller=[round(v, 4) for v in ctrl_xy],
                       offset=round(off, 5), main_net=next(iter(footprints[f'L{i}'].Pads())).GetNetname(),
                       controller_net=next(iter(footprints[f'ML{i}'].Pads())).GetNetname())
    assert off < 1e-3, (name, main_xy, ctrl_xy)
header = {fp.GetValue(): [round(v, 4) for v in plan_of(fp.GetReference())] for fp in footprints.values()
          if fp.GetReference().startswith('MP')}
(root / 'pcb/stack_alignment.json').write_text(json.dumps(dict(pairs=pairs, header=header), indent=1) + '\n')
print('Stacking holes: all %d pairs coincide in the module, worst %.4f mm' % (len(pairs), max(p['offset'] for p in pairs.values())))
print('All three boards: every pad, header pin, stacking pin and jumper net matches')
