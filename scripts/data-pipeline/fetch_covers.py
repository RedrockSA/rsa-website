"""Fetch higher-resolution covers from Open Library into ./covers_hires/.

Lookup order per book:
  1. covers.openlibrary.org by ISBN13, then by ISBN  (exact edition)
  2. openlibrary.org/search.json by title+author, then the work's cover id

default=false is passed so a missing cover 404s instead of returning Open
Library's blank placeholder image.

Files land under covers_hires/ using the same final_filename as ./covers/,
so the two directories line up one-to-one. Nothing in ./covers/ is touched.
"""

import argparse
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

SRC = os.path.join("covers", "manifest_isbn.csv")
OUT_DIR = "covers_hires"
REPORT = os.path.join("covers", "hires_report.csv")

UA = "RedRockSA-book-covers/1.0 (gloos@redrocksa.com)"
DELAY = 0.6          # seconds between requests, to stay polite
MIN_GOOD_WIDTH = 300  # below this we flag the result as still too small


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "")


def try_image(url):
    """Return (PIL image, url) or None."""
    try:
        data, ctype = get(url)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return None
    if not data or "image" not in ctype.lower():
        return None
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
    except Exception:
        return None
    # Open Library sometimes serves a 1x1 when it has nothing.
    if im.width < 20 or im.height < 20:
        return None
    return im, url


def by_isbn(isbn):
    if not isbn:
        return None
    return try_image(
        "https://covers.openlibrary.org/b/isbn/%s-L.jpg?default=false" % isbn)


def by_search(title, author):
    """Fall back to Open Library search, then that doc's cover id."""
    q = urllib.parse.urlencode({
        "title": title, "author": author, "limit": "5",
        "fields": "cover_i,title,author_name,isbn",
    })
    try:
        data, _ = get("https://openlibrary.org/search.json?" + q)
        docs = json.loads(data.decode("utf-8")).get("docs", [])
    except Exception:
        return None
    for d in docs:
        if d.get("cover_i"):
            time.sleep(DELAY)
            hit = try_image("https://covers.openlibrary.org/b/id/%d-L.jpg"
                            % d["cover_i"])
            if hit:
                return hit
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0,
                    help="only process the first N rows (for a trial run)")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(SRC, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if args.limit:
        rows = rows[:args.limit]

    report = []
    got = small = missed = 0

    for i, r in enumerate(rows, 1):
        name = r["final_filename"]
        hit = None
        via = ""

        for isbn, label in ((r["isbn13"], "isbn13"), (r["isbn"], "isbn")):
            if isbn:
                hit = by_isbn(isbn)
                time.sleep(DELAY)
                if hit:
                    via = label
                    break
        if not hit:
            hit = by_search(r["goodreads_title"] or r["title_full"],
                            r["goodreads_author"] or r["author"])
            time.sleep(DELAY)
            if hit:
                via = "search"

        if hit:
            im, url = hit
            im.convert("RGB").save(os.path.join(OUT_DIR, name), "PNG")
            w, h = im.size
            status = "ok" if w >= MIN_GOOD_WIDTH else "small"
            got += 1
            if status == "small":
                small += 1
        else:
            w = h = 0
            url = ""
            status = "missing"
            missed += 1

        report.append({
            "final_filename": name, "title_short": r["title_short"],
            "author": r["author"], "isbn13": r["isbn13"], "isbn": r["isbn"],
            "status": status, "via": via, "width": w, "height": h,
            "source_url": url,
        })
        print("[%3d/%d] %-9s %-5s %4dx%-4d %s"
              % (i, len(rows), status, via, w, h, name), flush=True)

    with open(REPORT, "w", newline="", encoding="utf-8-sig") as fh:
        wtr = csv.DictWriter(fh, fieldnames=list(report[0].keys()))
        wtr.writeheader()
        wtr.writerows(report)

    print("\nfetched %d  (of which too small: %d)   missing: %d"
          % (got, small, missed))
    print("images -> %s/   report -> %s" % (OUT_DIR, REPORT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
