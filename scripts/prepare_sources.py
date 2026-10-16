#!/usr/bin/env python3
"""Phase 1 helper: turn raw course material into page images + a manifest.

Usage:
    python3 prepare_sources.py OUT_DIR INPUT [INPUT ...]

INPUT may be PDF files or images (jpg, png, heic if Pillow supports it, tiff, webp).
For every page it writes, in OUT_DIR:
    pNN.png          full page, 200 dpi for PDFs, auto-oriented for photos
    pNN-text.txt     text layer of a PDF page (empty for scans and photos)
    pNN-tiles/       2x2 overlapping zoom tiles (photos and scanned pages only)
    pNN-grid.png     the page with a labelled 10 % grid, to read off the region of a mark
    manifest.json    one entry per page: id, origin file, page, kind, text chars

Page ids (p01, p02, ...) are the anchors used in \\src{...} tags, so keep them
stable once transcription has started. Inputs are numbered in the order given.

PDF backend: poppler (pdftoppm, pdfinfo, pdftotext) when installed, otherwise PyMuPDF
(`pip install pymupdf`). With neither, PDFs cannot be rasterised: the script stops and says so;
ask the user for page images instead. Images only need Pillow (optional).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:  # the script still handles PDFs with poppler alone
    Image = None

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp", ".heic"}
TEXT_LAYER_MIN_CHARS = 200  # below this, treat a PDF page as a scan


def pdf_backend():
    if all(shutil.which(t) for t in ("pdftoppm", "pdfinfo", "pdftotext")):
        return "poppler"
    for mod in ("pymupdf", "fitz"):
        try:
            __import__(mod)
            return mod
        except ImportError:
            pass
    return None


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def pdf_pages(pdf: Path) -> int:
    out = run(["pdfinfo", str(pdf)])
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    raise RuntimeError(f"cannot read page count of {pdf}")


def make_grid(png: Path, out: Path):
    """Copy of the page with a labelled 10 % grid, to read off mark regions [pNN@x0,y0,x1,y1]."""
    if Image is None:
        return
    from PIL import ImageDraw
    im = Image.open(png).convert("RGB")
    w, h = im.size
    d = ImageDraw.Draw(im)
    for k in range(1, 10):
        x, y = w * k // 10, h * k // 10
        d.line([(x, 0), (x, h)], fill=(220, 40, 40), width=max(1, w // 800))
        d.line([(0, y), (w, y)], fill=(220, 40, 40), width=max(1, w // 800))
        d.text((x + 3, 3), f"{k / 10:.1f}", fill=(220, 40, 40))
        d.text((3, y + 3), f"{k / 10:.1f}", fill=(220, 40, 40))
    im.save(out)


def make_tiles(png: Path, tile_dir: Path):
    """2x2 tiles with 12% overlap: zoom on dense handwriting without losing context."""
    if Image is None:
        return
    tile_dir.mkdir(exist_ok=True)
    im = Image.open(png)
    w, h = im.size
    ox, oy = int(w * 0.12), int(h * 0.12)
    boxes = {
        "top-left": (0, 0, w // 2 + ox, h // 2 + oy),
        "top-right": (w // 2 - ox, 0, w, h // 2 + oy),
        "bottom-left": (0, h // 2 - oy, w // 2 + ox, h),
        "bottom-right": (w // 2 - ox, h // 2 - oy, w, h),
    }
    for name, box in boxes.items():
        im.crop(box).save(tile_dir / f"{name}.png")


def image_quality(src: Path):
    """Hints for phase 0 triage (the decision is made by looking at the page)."""
    if Image is None:
        return {}
    im = ImageOps.exif_transpose(Image.open(src))
    w, h = im.size
    return {"pixels": f"{w}x{h}", "low_resolution": max(w, h) < 1600}


def clean_photo(src: Path, dst: Path):
    """Auto-orient from EXIF, grey, autocontrast. Never crops or redraws content."""
    if Image is None:
        shutil.copy(src, dst.with_suffix(src.suffix))
        return
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    im = ImageOps.grayscale(im)
    im = ImageOps.autocontrast(im, cutoff=1)
    longest = max(im.size)
    if longest > 3000:  # keep files light while staying readable
        im = im.resize((im.width * 3000 // longest, im.height * 3000 // longest))
    im.save(dst)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    manifest, n = [], 0
    for arg in sys.argv[2:]:
        f = Path(arg)
        if not f.exists():
            sys.exit(f"not found: {f}")
        if f.suffix.lower() == ".pdf":
            backend = pdf_backend()
            if backend is None:
                sys.exit(f"Cannot rasterise {f.name}: neither poppler-utils nor PyMuPDF is available. "
                         "Install one (apt install poppler-utils, or pip install pymupdf), or ask the "
                         "user for page images (exports or screenshots) and say so in the report.")
            if backend == "poppler":
                count = pdf_pages(f)
            else:
                mupdf = __import__(backend)
                doc = mupdf.open(str(f))
                count = len(doc)
            for p in range(1, count + 1):
                n += 1
                pid = f"p{n:02d}"
                if backend == "poppler":
                    run(["pdftoppm", "-r", "200", "-png", "-singlefile", "-f", str(p), "-l", str(p),
                         str(f), str(out / pid)])
                    text = run(["pdftotext", "-layout", "-f", str(p), "-l", str(p), str(f), "-"])
                else:
                    page = doc[p - 1]
                    page.get_pixmap(dpi=200).save(str(out / f"{pid}.png"))
                    text = page.get_text()
                (out / f"{pid}-text.txt").write_text(text)
                make_grid(out / f"{pid}.png", out / f"{pid}-grid.png")
                chars = len(text.strip())
                kind = "pdf-text" if chars >= TEXT_LAYER_MIN_CHARS else "pdf-scan"
                if kind == "pdf-scan":
                    make_tiles(out / f"{pid}.png", out / f"{pid}-tiles")
                manifest.append({"id": pid, "file": f.name, "page": p, "kind": kind, "text_chars": chars})
        elif f.suffix.lower() in IMAGE_EXT:
            n += 1
            pid = f"p{n:02d}"
            clean_photo(f, out / f"{pid}.png")
            make_grid(out / f"{pid}.png", out / f"{pid}-grid.png")
            (out / f"{pid}-text.txt").write_text("")
            make_tiles(out / f"{pid}.png", out / f"{pid}-tiles")
            manifest.append({"id": pid, "file": f.name, "page": 1, "kind": "photo", "text_chars": 0,
                             **image_quality(f)})
        else:
            print(f"skipped (unsupported type): {f}", file=sys.stderr)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    kinds = {}
    for m in manifest:
        kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
    print(f"{len(manifest)} pages -> {out}  ({', '.join(f'{v} {k}' for k, v in kinds.items())})")
    low = [m["id"] for m in manifest if m.get("low_resolution")]
    if low:
        print(f"Low resolution (longest side < 1600 px): {', '.join(low)} — check readability first.")
    print("Text layers are a hint only: math in PDF text layers is usually mangled. "
          "Transcribe from the page images.")


if __name__ == "__main__":
    main()
