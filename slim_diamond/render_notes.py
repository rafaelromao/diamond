"""Label engineering views and regenerate the pad guide from unchanged half inputs."""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon, box

import design


def main():
    d = json.loads(Path("design.json").read_text())
    c = math.cos(math.radians(d["tent_deg"]))
    to_floor = lambda p: (d["wall_in"] + (p[0] - d["wall_in"]) * c, p[1])
    foot = Polygon([to_floor(p) for p in d["case_outline"]])
    foot = foot.buffer(d["girdle"], join_style=2, mitre_limit=10).buffer(-d["chamfer"], join_style=2, mitre_limit=10)
    seam = d["wall_in"] + d["wall"]
    foot = foot.intersection(box(-1000, -1000, seam - d["chamfer"], 1000))
    design.pad_guide(foot, d["pads"]["slots"], [to_floor((p["x"], p["y"])) for p in d["keys"].values()], seam, plt)
    plt.close("all")
    font = ImageFont.truetype("/usr/share/fonts/liberation/LiberationSans-Regular.ttf", 26)
    notes = {
        "structure": "THE PRINTED PARTS | grey: lid | blue: tray | orange: four M3 x 8 screws, from the top",
        "seam": "CLOSED | grey lid on the blue tray | four M3 x 8 flat heads",
        "tray": "IN THE TRAY | main board in place, lid off | no wires shown",
        "stack": "IN THE TRAY | battery, sensor board, nice!nano go in first, main board on top | no wires shown",
        "reset": "RESET | press from below through the floor with the pin (orange) | take the module out of the dock first",
        "rear": "BACK | power slider above USB-C, the same on every module",
    }
    for kind in ("trackball", "trackball_choc", "trackpad"):
        for view, text in notes.items():
            path = Path(f"renders/{kind}_{view}.png")
            if not path.exists():
                continue
            image = Image.open(path).convert("RGB")
            out = Image.new("RGB", (image.width, image.height + 80), "white")
            out.paste(image, (0, 0))
            ImageDraw.Draw(out).text((24, image.height + 22), text, fill="#1d3340", font=font)
            out.save(path)


if __name__ == "__main__":
    main()
