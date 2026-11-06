"""Wiring of the common carrier: GPIO labels are NOT interchangeable between MCUs.

nice!nano v2: https://nicekeyboards.com/docs/nice-nano/pinout-schematic
XIAO nRF52840 (plain): https://wiki.seeedstudio.com/XIAO_BLE/#hardware-overview
"""

GPIO = {
    "nice_nano": {"D2": (0, 17), "D3": (0, 20), "D4": (0, 22), "D19": (0, 2), "D20": (0, 29), "D21": (0, 31)},
    "xiao": {"D3": (0, 29), "D4": (0, 4), "D5": (0, 5), "D8": (1, 13), "D9": (1, 14), "D10": (1, 15)},
}
# Carrier pad -> controller pin. The same on both modules: only what lands on the pad differs.
# The nano's clock and data stay on its high-frequency pins (D2-D4).
PADS = {
    "nice_nano": dict(MO="D2", CK="D3", IO="D4", CS="D21", K1="D19", K2="D20"),
    "xiao": dict(MO="D3", CK="D4", IO="D5", CS="D10", K1="D8", K2="D9"),
}
# XIAO pin rows, 1 at the USB end, on each side of the carrier (the board hangs face down, so its
# D0-D6 column is on the carrier's right). Pads sit level with the pin of the same row.
ROWS = {"left": dict(VBAT=1, GND=2, VCC=3, NCS=4, K2=5, K1=6, RST=7), "right": dict(MOTION=4, SCLK=5, SDIO=6)}
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
