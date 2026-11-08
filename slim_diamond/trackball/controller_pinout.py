"""Which pin does what on the controller board, for either controller.

Both controllers plug into the same header on the controller board, on the nice!nano's pin rows. Row
1 is the first row of a XIAO's, the nice!nano's B+ row; the rows here start at the USB end. Neither
board has the same names in the same places, but rows 5 to 7 are GPIOs on both, so the signals need
no jumpers, only different firmware. The one jumper picks the 3.3 V pin. GPIO labels are NOT interchangeable between controllers.

nice!nano v2: https://nicekeyboards.com/docs/nice-nano/pinout-schematic
XIAO nRF52840 (plain): https://wiki.seeedstudio.com/XIAO_BLE/#hardware-overview
"""

GPIO = {
    "nice_nano": {"D2": (0, 17), "D3": (0, 20), "D4": (0, 22), "D19": (0, 2), "D20": (0, 29), "D21": (0, 31)},
    "xiao": {"D4": (0, 4), "D5": (0, 5), "D6": (1, 11), "D7": (1, 12), "D8": (1, 13), "D9": (1, 14)},
}
# Pad -> controller pin. The same on both modules: only what lands on the pad differs.
PADS = {
    "nice_nano": dict(MO="D4", CK="D2", IO="D3", CS="D20", K1="D19", K2="D21"),
    "xiao": dict(MO="D6", CK="D4", IO="D5", CS="D8", K1="D7", K2="D9"),
}
# Header row of each signal, and the name each controller gives every pin in rows 2 to 7, top view
# turned over: the controllers lie face down, so the XIAO's D0-D6 column is on the board's right.
HEADER = {"left": {2: "G", 3: "L3", 4: "L4", 5: "K2", 6: "CS", 7: "K1"},
          "right": {3: None, 4: None, 5: "CK", 6: "IO", 7: "MO"}}
PINS = {
    "xiao": {"left": ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"], "right": ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]},
    "nice_nano": {"left": ["B+", "GND", "RST", "VCC", "D21", "D20", "D19"], "right": ["D1", "D0", "GND", "GND", "D2", "D3", "D4"]},
}
# The stacking pins that join the two boards, beside the controller: header row -> main board net.
LINKS = {"left": {5: "K2", 6: "NCS", 7: "K1", 8: "GND"}, "right": {5: "SCLK", 6: "SDIO", 7: "MOTION", 8: "VCC"}}
# Main board's wire pads, in header rows, for the sensor board or trackpad and the controller's
# battery and reset wires. Reset has two pads: RST for the sensor board's wire, R2 for the controller's.
ROWS = {"left": dict(GND=3, NCS=6), "right": dict(XR=2, RST=3, VBAT=4, SCLK=5, SDIO=6, MOTION=7, VCC=8)}
TRACKPAD = dict(SCL="CK", SDA="IO", DR="MO", K1="K1", K2="K2")     # module signal -> carrier pad
_ball = dict(SCLK="CK", SDIO="IO", NCS="CS", MOTION="MO", K1="K1", K2="K2")
SIGNALS = {
    "trackball": {c: {s: PADS[c][p] for s, p in _ball.items()} for c in PADS},
    "trackpad": {c: {s: PADS[c][p] for s, p in TRACKPAD.items()} for c in PADS},
}
POWER = {
    "nice_nano": dict(VBAT="B+", VCC="VCC (3.3 V)", GND="GND / B-", RST="RST"),
    "xiao": dict(VBAT="BAT+", VCC="3V3", GND="GND / BAT-", RST="RST (P0.18)"),
}


def gpio(kind, controller, signal):
    return GPIO[controller][SIGNALS[kind][controller][signal]]


def pin_description(kind, controller, signal):
    port, pin = gpio(kind, controller, signal)
    return f"{SIGNALS[kind][controller][signal]} (P{port}.{pin:02d})"


def write_pinout(path):
    import json
    from pathlib import Path

    legacy = {signal: f'P{port}.{pin:02d}' for signal in SIGNALS['trackball']['nice_nano']
              for port, pin in [gpio('trackball', 'nice_nano', signal)]}
    Path(path).write_text(json.dumps(dict(
        pins=legacy, signals=SIGNALS, gpio=GPIO, power=POWER,
        wires_main=['SCLK', 'SDIO', 'NCS', 'MOTION', 'RST', 'VCC', 'GND'],
        wires_sensor=['VCC', 'GND', 'RST', 'SCLK', 'SDIO', 'NCS', 'MOTION'],
    ), indent=1) + '\n')
