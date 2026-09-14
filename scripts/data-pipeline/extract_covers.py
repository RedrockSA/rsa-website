"""Extract individual book covers from screenshot-style grid blocks.

Detects grid structure per image by projecting whitespace, skips empty cells,
and crops tight to each cover's content bounds using a near-white tolerance
combined with gradient (edge) energy so that white-background covers survive.

Pixel data is preserved exactly: crops are slices of the source array, saved
as PNG. No resampling, no upscaling.
"""

import csv
import os
import re
import sys

import numpy as np
from PIL import Image

SRC_DIR = "."
OUT_DIR = "covers"

WHITE_TOL = 8          # channel distance from pure white that counts as content
EDGE_TOL = 10          # gradient magnitude that counts as an edge
MIN_BAND_FRAC = 0.30   # bands thinner than this * median band size are debris
MERGE_GAP = 3          # runs separated by <= this many px are one band
EMPTY_FRAC = 0.002     # occupied-pixel fraction below this => empty cell
TYPICAL_AR = 1.5       # height / width of a typical book cover
AR_TOL = 0.35          # flag cells whose aspect ratio strays this far (relative)


def load_rgb(path):
    """Load as RGB uint8, compositing any alpha over white."""
    im = Image.open(path)
    if im.mode == "RGBA":
        a = np.array(im)
        if a[..., 3].min() == 255:
            return a[..., :3].copy()
        alpha = a[..., 3:4].astype(np.float64) / 255.0
        out = a[..., :3].astype(np.float64) * alpha + 255.0 * (1.0 - alpha)
        return np.rint(out).astype(np.uint8)
    return np.array(im.convert("RGB"))


def content_mask(rgb, white_tol=WHITE_TOL, edge_tol=EDGE_TOL):
    """Pixels that are either non-white (within tolerance) or sit on an edge."""
    dist = 255 - rgb.min(axis=2).astype(np.int16)
    mask = dist > white_tol

    gray = rgb.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    gx = np.zeros_like(gray)
    gy = np.zeros_like(gray)
    gx[:, 1:-1] = np.abs(gray[:, 2:] - gray[:, :-2]) / 2.0
    gy[1:-1, :] = np.abs(gray[2:, :] - gray[:-2, :]) / 2.0
    edge = np.hypot(gx, gy) > edge_tol

    return mask | edge


def runs(counts, thresh, merge_gap=MERGE_GAP):
    """Contiguous index ranges where counts exceed thresh, small gaps merged."""
    on = counts > thresh
    spans = []
    start = None
    for i, v in enumerate(on):
        if v and start is None:
            start = i
        elif not v and start is not None:
            spans.append((start, i - 1))
            start = None
    if start is not None:
        spans.append((start, len(on) - 1))

    merged = []
    for s, e in spans:
        if merged and s - merged[-1][1] - 1 <= merge_gap:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    return merged


def find_bands(counts, axis_len):
    """Find content bands along one axis, dropping thin debris slivers."""
    thresh = max(2, int(0.004 * axis_len))
    bands = runs(counts, thresh)
    if not bands:
        return []
    sizes = [e - s + 1 for s, e in bands]
    med = float(np.median(sizes))
    return [b for b, sz in zip(bands, sizes) if sz >= MIN_BAND_FRAC * med]


def cell_bounds(bands, limit):
    """Expand each band outward to the midpoint of the adjacent gutters."""
    out = []
    for i, (s, e) in enumerate(bands):
        lo = 0 if i == 0 else (bands[i - 1][1] + s) // 2
        hi = limit - 1 if i == len(bands) - 1 else (e + bands[i + 1][0] + 1) // 2
        out.append((lo, hi))
    return out


def tight_bbox(mask):
    """Bounding box of content, ignoring rows/cols with only stray pixels."""
    h, w = mask.shape
    rows = mask.sum(axis=1)
    cols = mask.sum(axis=0)
    rthr = max(1, int(0.02 * w))
    cthr = max(1, int(0.02 * h))
    ri = np.nonzero(rows > rthr)[0]
    ci = np.nonzero(cols > cthr)[0]
    if ri.size == 0 or ci.size == 0:
        ri = np.nonzero(rows > 0)[0]
        ci = np.nonzero(cols > 0)[0]
    if ri.size == 0 or ci.size == 0:
        return None
    return int(ci[0]), int(ri[0]), int(ci[-1]) + 1, int(ri[-1]) + 1


def block_key(name):
    m = re.search(r"(\d+)", name)
    return (int(m.group(1)) if m else 0, name)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(
        (f for f in os.listdir(SRC_DIR) if re.match(r"(?i)^block.*\.png$", f)),
        key=block_key,
    )
    if not files:
        print("No Block*.png files found in", os.path.abspath(SRC_DIR))
        return 1

    rows_out = []
    flags = []

    for fname in files:
        bnum = block_key(fname)[0]
        rgb = load_rgb(os.path.join(SRC_DIR, fname))
        H, W = rgb.shape[:2]
        mask = content_mask(rgb)

        col_bands = find_bands(mask.sum(axis=0), H)
        row_bands = find_bands(mask.sum(axis=1), W)
        xcells = cell_bounds(col_bands, W)
        ycells = cell_bounds(row_bands, H)

        occupied = skipped = 0
        for r, (y0, y1) in enumerate(ycells, start=1):
            for c, (x0, x1) in enumerate(xcells, start=1):
                sub = mask[y0:y1 + 1, x0:x1 + 1]
                if sub.mean() < EMPTY_FRAC:
                    skipped += 1
                    continue
                bb = tight_bbox(sub)
                if bb is None:
                    skipped += 1
                    continue
                bx0, by0, bx1, by1 = bb
                crop = rgb[y0 + by0:y0 + by1, x0 + bx0:x0 + bx1]
                ch, cw = crop.shape[:2]
                if ch < 10 or cw < 10:
                    skipped += 1
                    continue

                name = "block%02d_r%dc%d.png" % (bnum, r, c)
                Image.fromarray(crop).save(os.path.join(OUT_DIR, name), "PNG")
                occupied += 1

                notes = []
                ch_cell, cw_cell = sub.shape
                # Only an *interior* cell boundary is meaningful: the outer cells
                # are clamped to the image border, so touching there is normal.
                touched = []
                if bx0 <= 1 and x0 > 0:
                    touched.append("left")
                if by0 <= 1 and y0 > 0:
                    touched.append("top")
                if bx1 >= cw_cell - 1 and x1 < W - 1:
                    touched.append("right")
                if by1 >= ch_cell - 1 and y1 < H - 1:
                    touched.append("bottom")
                if touched:
                    notes.append("touches cell edge: " + ",".join(touched))
                if by0 <= 1 and y0 == 0:
                    notes.append("flush with image top (may be cut off in source)")
                ar = ch / cw
                if abs(ar - TYPICAL_AR) / TYPICAL_AR > AR_TOL:
                    notes.append("aspect %.2f" % ar)
                if notes:
                    flags.append("  ! %s (%dx%d): %s" % (name, cw, ch, "; ".join(notes)))

                rows_out.append((name, fname, r, c, cw, ch, round(ar, 3)))

        print("%-20s grid %dx%d  occupied %2d  skipped %2d"
              % (fname, len(col_bands), len(row_bands), occupied, skipped))

    if flags:
        print("\nSuspicious cells:")
        for f in flags:
            print(f)
    else:
        print("\nNo suspicious cells.")

    with open(os.path.join(OUT_DIR, "_extract_log.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["filename", "source", "row", "col", "width", "height", "aspect"])
        w.writerows(rows_out)

    print("\nTotal extracted: %d -> %s/" % (len(rows_out), OUT_DIR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
