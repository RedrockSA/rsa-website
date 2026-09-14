"""Merge the hand-researched ISBNs in, then re-fetch those covers by ISBN.

ISBN-keyed lookups proved reliable earlier (title search did not), so these
go straight to covers.openlibrary.org by ISBN with no title-matching guesswork.
Results are still only kept if they beat what is already on disk.
"""

import csv
import io
import os
import re
import sys
import time
import urllib.error
import urllib.request

from PIL import Image

NEEDS = os.path.join("covers", "needs_isbn.csv")
ISBN_SRC = os.path.join("covers", "manifest_isbn.csv")
REPORT = os.path.join("covers", "hires_report.csv")
OUT_DIR = "covers_hires"
UA = "RedRockSA-book-covers/1.0 (gloos@redrocksa.com)"


def parse_isbn13(raw):
    raw = (raw or "").replace("\xa0", " ")
    raw = re.sub(r"(?i)\bisbn[-\s]*1[03]\s*:?", " ", raw)   # drop the label
    d = re.sub(r"[^0-9]", "", raw)
    if len(d) != 13:
        return ""
    t = sum((3 if i % 2 else 1) * int(c) for i, c in enumerate(d[:12]))
    return d if str((10 - t % 10) % 10) == d[12] else ""


def isbn13_to_10(isbn13):
    if len(isbn13) != 13 or not isbn13.startswith("978"):
        return ""
    core = isbn13[3:12]
    t = sum((10 - i) * int(c) for i, c in enumerate(core))
    c = (11 - t % 11) % 11
    return core + ("X" if c == 10 else str(c))


def load_image(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            data, ctype = r.read(), r.headers.get("Content-Type", "")
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


def main():
    with open(NEEDS, encoding="utf-8-sig") as fh:
        needs = list(csv.DictReader(fh))
    with open(ISBN_SRC, encoding="utf-8-sig") as fh:
        man_rows = list(csv.DictReader(fh))
    with open(REPORT, encoding="utf-8-sig") as fh:
        rep_rows = list(csv.DictReader(fh))

    man = {r["final_filename"]: r for r in man_rows}
    rep = {r["final_filename"]: r for r in rep_rows}

    applied = improved = same = 0
    for n in needs:
        name = n["filename"]
        i13 = parse_isbn13(n.get("User_Provided_ISBN"))
        if not i13:
            print("  skip (unparseable ISBN): %s" % name)
            continue

        # 1. record the ISBN
        if name in man:
            man[name]["isbn13"] = i13
            man[name]["isbn"] = isbn13_to_10(i13)
            man[name]["match_method"] = (man[name]["match_method"] + "+user-isbn").strip("+")
            applied += 1

        # 2. re-fetch the cover with it
        r = rep.get(name)
        have = int(r["width"] or 0) if r else 0
        im = load_image("https://covers.openlibrary.org/b/isbn/%s-L.jpg?default=false" % i13)
        time.sleep(0.6)

        if im and im.width > have:
            im.convert("RGB").save(os.path.join(OUT_DIR, name), "PNG")
            if r:
                r["width"], r["height"] = im.size
                r["via"] = "user-isbn"
                r["status"] = "ok" if im.width >= 300 else "small"
                r["source_url"] = "https://covers.openlibrary.org/b/isbn/%s-L.jpg" % i13
                r["notes"] = ""
            improved += 1
            print("  %-46s %4dx%-4d  (was %s)" % (name[:46], im.size[0], im.size[1], have or "-"))
        else:
            same += 1
            print("  %-46s no cover at that ISBN (kept %spx)" % (name[:46], have or "-"))

    with open(ISBN_SRC, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(man_rows[0].keys()))
        w.writeheader()
        w.writerows(man_rows)
    fields = list(rep_rows[0].keys())
    with open(REPORT, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rep_rows)

    from collections import Counter
    print("\nISBNs applied: %d   covers improved: %d   no cover found: %d"
          % (applied, improved, same))
    print("status now:", dict(Counter(r["status"] for r in rep_rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
