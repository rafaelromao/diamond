"""Fail on stale/missing images, then hash all published PNGs and source inputs."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def main():
    root = Path(".")
    sources = sorted({*root.glob("*.py"), *root.glob("*.json"), root / "render.sh",
                      root / "trackball/trackball.py", root / "trackpad/trackpad.py",
                      root / "trackball/pcb/trackball.kicad_pcb", root / ".render/scenes.json",
                      *root.glob('trackball/models/*'), root / 'trackball/controllers.py'})
    # Test/doc helper edits do not invalidate unchanged imagery. The rendered
    # scene and both final boards do; every PNG is regenerated after these.
    scene_stamp = (root / ".render/scenes.json").stat().st_mtime
    pcb_stamp = (root / "trackball/pcb/trackball.kicad_pcb").stat().st_mtime
    half_stamp = (root / "pcb/slim_diamond.kicad_pcb").stat().st_mtime
    images = sorted((root / "renders").glob("*.png"))
    stale = [str(p) for p in images if p.name not in ("modules.png",) and
             p.stat().st_mtime < (pcb_stamp if p.name.startswith("trackball_board_") else
                                  max(scene_stamp, half_stamp))]
    if stale:
        raise RuntimeError("Stale renders: " + ", ".join(stale))
    required = [f"{k}_{v}.png" for k in ("trackball", "trackball_choc", "trackpad")
                for v in ("structure", "seam", "tray", "stack", "reset")]
    required += [f"{k}_{v}.png" for k in ("trackball", "trackpad")
                 for v in ("rear", "assembly", "under", "usb", "usb_open", "usb_dock")]
    required += ['trackball_xiao_stack.png', 'trackball_xiao_usb_open.png', 'trackball_board_stack.png',
                 'trackball_board_stack_exploded.png', 'trackball_board_stack_top.png', 'stack_alignment.png']
    assert all((root / "renders" / n).is_file() for n in required)
    font = ImageFont.truetype("/usr/share/fonts/liberation/LiberationSans-Regular.ttf", 22)
    sheet = Image.new("RGB", (1800, ((len(required) + 2) // 3) * 500), "white")
    draw = ImageDraw.Draw(sheet)
    for i, name in enumerate(required):
        image = Image.open(root / "renders" / name).convert("RGB")
        tile = ImageOps.contain(image, (580, 450))
        x, y = (i % 3) * 600, (i // 3) * 500
        sheet.paste(tile, (x + (600 - tile.width) // 2, y + 35))
        draw.text((x + 12, y + 8), name.removesuffix(".png"), font=font, fill="#263b46")
    sheet.save(root / "renders/modules.png")
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    inventory = []
    for p in sorted((root / "renders").glob("*.png")):
        with Image.open(p) as image:
            inventory.append(dict(path=str(p), size=list(image.size), sha256=digest(p)))
    result = dict(images=inventory, inputs=[dict(path=str(p), sha256=digest(p)) for p in sources],
                  note="Freshness checked against the final scene and both final PCBs.")
    (root / "renders/manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{len(inventory)} PNGs current, sized and SHA-256 inventoried")


if __name__ == "__main__":
    main()
