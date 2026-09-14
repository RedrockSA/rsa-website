"""Third pass: retry Open Library search using the CLEAN title.

The first pass searched with the raw Goodreads title, which carries subtitles
and series suffixes ("The Fellowship of the Ring (The Lord of the Rings, #1)").
Open Library's title= parameter matches poorly against those, so many books
fell through to 'missing' despite having a perfectly good cover on file.

This pass re-queries with title_short + author, walks the returned docs for a
cover id, and keeps the image only if it is wider than what we already have.
"""

import csv
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image

REPORT = os.path.join("covers", "hires_report.csv")
OUT_DIR = "covers_hires"

UA = "RedRockSA-book-covers/1.0 (gloos@redrocksa.com)"
DELAY = 0.6
TARGET = 300


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


def search_covers(title, author):
    """Yield candidate cover ids for a clean title + author, best docs first."""
    q = urllib.parse.urlencode({
        "title": title, "author": author, "limit": "5",
        "fields": "title,author_name,cover_i,edition_key",
    })
    try:
        data, _ = get("https://openlibrary.org/search.json?" + q)
        docs = json.loads(data.decode("utf-8")).get("docs", [])
    except Exception:
        return []
    return [d["cover_i"] for d in docs if d.get("cover_i")]


def current(path):
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

    todo = [r for r in rows if int(r["width"] or 0) < TARGET]
    print("retrying %d covers under %dpx\n" % (len(todo), TARGET))

    improved = 0
    for i, r in enumerate(todo, 1):
        name = r["final_filename"]
        dest = os.path.join(OUT_DIR, name)
        have = current(dest)

        best = None
        for cid in search_covers(r["title_short"], r["author"]):
            time.sleep(DELAY)
            im = load_image("https://covers.openlibrary.org/b/id/%d-L.jpg" % cid)
            if im and (best is None or im.width > best[0].width):
                best = (im, "https://covers.openlibrary.org/b/id/%d-L.jpg" % cid)
            if best and best[0].width >= TARGET:
                break
        time.sleep(DELAY)

        if best and best[0].width > have:
            best[0].convert("RGB").save(dest, "PNG")
            w, h = best[0].size
            r["width"], r["height"] = w, h
            r["source_url"] = best[1]
            r["via"] = "ol-search2"
            r["status"] = "ok" if w >= TARGET else "small"
            improved += 1
            print("[%2d/%d] %-6s %4dx%-4d  (was %s)  %s"
                  % (i, len(todo), r["status"], w, h, have or "-", name), flush=True)
        else:
            print("[%2d/%d] %-6s  no better  (have %s)  %s"
                  % (i, len(todo), r["status"], have or "-", name), flush=True)

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
