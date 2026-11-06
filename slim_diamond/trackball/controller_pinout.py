"""Wiring of the common carrier: GPIO labels are NOT interchangeable between MCUs.

nice!nano v2: https://nicekeyboards.com/docs/nice-nano/pinout-schematic
XIAO nRF52840 (plain): https://wiki.seeedstudio.com/XIAO_BLE/#hardware-overview
"""

GPIO = {
    "nice_nano": {"D2": (0, 17), "D3": (0, 20), "D4": (0, 22),
                  "D5": (0, 24), "D6": (1, 0), "D7": (0, 11),
                  "D8": (1, 4), "D9": (1, 6)},
    "xiao": {"D1": (0, 3), "D2": (0, 28), "D3": (0, 29),
             "D4": (0, 4), "D5": (0, 5), "D8": (1, 13), "D9": (1, 14), "D10": (1, 15)},
}
SIGNALS = {
    "trackball": {
        "nice_nano": dict(SCLK="D7", SDIO="D6", NCS="D5", MOTION="D4", K1="D8", K2="D2"),
        "xiao": dict(SCLK="D8", SDIO="D10", NCS="D1", MOTION="D2", K1="D3", K2="D4"),
    },
    "trackpad": {
        "nice_nano": dict(SDA="D2", SCL="D3", DR="D7", K1="D8", K2="D9"),
        "xiao": dict(SDA="D4", SCL="D5", DR="D2", K1="D3", K2="D1"),
    },
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
