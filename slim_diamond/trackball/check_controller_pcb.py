"""Check all controller-facing nets on the common routed carrier, in KiCad Python.

GPIO compatibility is checked against the four firmware overlays by test_xiao_option.
This checks the actual PCB pad assignments; DRC checks copper continuity separately.
"""
from pathlib import Path
import pcbnew

root = Path(__file__).resolve().parent
board = pcbnew.LoadBoard(str(root / 'pcb/trackball.kicad_pcb'))
footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
expected = {
    **{f'J{i}': {'1': net} for i, net in enumerate(
        ('SCLK', 'SDIO', 'NCS', 'MOTION', 'RST', 'VCC', 'GND', 'BAT+', 'GND', 'VBAT', 'K1', 'K2'), 1)},
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
assert not any('NiceNano' in str(fp.GetFPID().GetLibItemName()) or 'XIAO' in str(fp.GetFPID().GetLibItemName())
               for fp in board.GetFootprints()), 'Unexpected direct-mount controller footprint'
print('Common carrier: all signal, power, battery, switch and reset wire-pad nets match; no fixed MCU footprint')
