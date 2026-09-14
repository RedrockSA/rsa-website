"""Second pass: fill covers Open Library missed or served too small.

Reads covers/hires_report.csv, and for every row not already 'ok' tries
Google Books. Google's imageLinks default to ~128px thumbnails, so each
candidate is also retried with zoom=0 and with a fife=w1200 width hint,
keeping whichever variant actually comes back largest.

Anything still short is topped up from ./covers/ when the existing crop is
bigger (relevant for the two covers that were sourced by hand).

Only improves: a file is replaced only by a strictly wider image.
"""

import csv
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image

REPORT = os.path.join("covers", "hires_report.csv")
OUT_DIR = "covers_hires"
CUR_DIR = "covers"

UA = "RedRockSA-book-covers/1.0 (gloos@redrocksa.com)"
DELAY = 0.5
MIN_GOOD_WIDTH = 300


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "")


def load_image(url):
    try:
        data, ctype = get(url)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        return None
    if not data or "image" not in ctype.lower():
        return None
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
    except Exception:
        return None
    return im if im.width >= 20 and im.height >= 20 else None


def variants(url):
    """Google content URLs respond to zoom / fife hints; try the big ones."""
    base = url.replace("http://", "https://").replace("&edge=curl", "")
    out = [base]
    if "zoom=" in base:
        out.append(re.sub(r"zoom=\d+", "zoom=0", base))
        out.append(re.sub(r"zoom=\d+", "zoom=1", base) + "&fife=w1200")
    else:
        out.append(base + "&fife=w1200")
    return out


def best_from_volume(vol):
    links = (vol.get("volumeInfo", {}) or {}).get("imageLinks", {}) or {}
    # Prefer the explicitly large keys, then coax the thumbnail upward.
    ordered = [links[k] for k in
               ("extraLarge", "large", "medium", "small", "thumbnail", "smallThumbnail")
               if links.get(k)]
    best = None
    for link in ordered:
        for v in variants(link):
            im = load_image(v)
            time.sleep(DELAY)
            if im and (best is None or im.width > best[0].width):
                best = (im, v)
            if best and best[0].width >= 600:
                return best
        if best and best[0].width >= MIN_GOOD_WIDTH:
            return best
    return best


def gbooks(query):
    url = "https://www.googleapis.com/books/v1/volumes?" + urllib.parse.urlencode(
        {"q": query, "maxResults": "5"})
    try:
        data, _ = get(url)
        items = json.loads(data.decode("utf-8")).get("items", [])
    except Exception:
        return None
    time.sleep(DELAY)
    best = None
    for vol in items:
        hit = best_from_volume(vol)
        if hit and (best is None or hit[0].width > best[0].width):
            best = hit
        if best and best[0].width >= 600:
            break
    return best


def current_width(path):
    if not os.path.exists(path):
        return 0
    try:
        with Image.open(path) as im:
            return im.width
    except Exception:
        return 0


def main():
    with open(REPORT, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    todo = [r for r in rows if r["status"] != "ok"]
    print("rows needing a better image: %d\n" % len(todo))

    improved = 0
    for i, r in enumerate(todo, 1):
        name = r["final_filename"]
        dest = os.path.join(OUT_DIR, name)
        have = current_width(dest)

        best = None
        for q in filter(None, [
                "isbn:" + r["isbn13"] if r["isbn13"] else "",
                "isbn:" + r["isbn"] if r["isbn"] else "",
                'intitle:"%s" inauthor:"%s"' % (r["title_short"], r["author"])
                if r["author"] else 'intitle:"%s"' % r["title_short"]]):
            best = gbooks(q)
            if best and best[0].width >= MIN_GOOD_WIDTH:
                break

        # Last resort: the crop we already have, if it is wider.
        src_existing = os.path.join(CUR_DIR, name)
        if current_width(src_existing) > (best[0].width if best else have):
            with Image.open(src_existing) as im:
                best = (im.convert("RGB").copy(), "local:covers/" + name)

        if best and best[0].width > have:
            best[0].convert("RGB").save(dest, "PNG")
            w, h = best[0].size
            r["width"], r["height"] = w, h
            r["source_url"] = best[1]
            r["via"] = "local" if best[1].startswith("local:") else "gbooks"
            r["status"] = "ok" if w >= MIN_GOOD_WIDTH else "small"
            improved += 1
            print("[%3d/%d] %-6s %4dx%-4d %s" % (i, len(todo), r["status"], w, h, name),
                  flush=True)
        else:
            print("[%3d/%d] %-6s %4s      %s" % (i, len(todo), r["status"], have or "-", name),
                  flush=True)

    with open(REPORT, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    print("\nimproved: %d" % improved)
    print("status now:", dict(Counter(r["status"] for r in rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
