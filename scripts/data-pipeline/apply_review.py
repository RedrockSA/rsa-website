"""Apply the reviewed books_master.csv: repair, adopt new covers, cut deletions.

Excel coerces long digit strings to floats, so most isbn13 cells came back as
'9.78125E+12' with only six significant digits left. Those are restored from
covers/manifest_isbn.csv, which was never opened in a spreadsheet. ISBNs typed
with dashes survived as text and are kept as authored.

Writes covers/books_final.csv. books_master.csv is left untouched, and no
image files are deleted - rows marked DELETE simply do not carry forward.
"""

import csv
import os
import re
import shutil
import sys

from PIL import Image

MASTER = os.path.join("covers", "books_master.csv")
AUTH = os.path.join("covers", "manifest_isbn.csv")
FOUND_DIR = "FOUND"
HIRES = "covers_hires"
OUT = os.path.join("covers", "books_final.csv")

SCI = re.compile(r"^\d+\.?\d*E\+\d+$", re.I)
GOOD, USABLE = 300, 200


def clean_isbn(s):
    s = re.sub(r"(?i)\bisbn[-\s]*1[03]\s*:?", " ", (s or "").replace("\xa0", " "))
    return re.sub(r"[^0-9]", "", s)


def valid13(d):
    if len(d) != 13 or not d.isdigit():
        return False
    t = sum((3 if i % 2 else 1) * int(c) for i, c in enumerate(d[:12]))
    return str((10 - t % 10) % 10) == d[12]


def isbn13_to_10(d):
    if len(d) != 13 or not d.startswith("978"):
        return ""
    core = d[3:12]
    t = sum((10 - i) * int(c) for i, c in enumerate(core))
    c = (11 - t % 11) % 11
    return core + ("X" if c == 10 else str(c))


def quality(w):
    w = int(w or 0)
    return "good" if w >= GOOD else ("usable" if w >= USABLE else "weak")


def main():
    with open(MASTER, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    with open(AUTH, encoding="utf-8-sig") as fh:
        auth = {r["final_filename"][:-4]: r for r in csv.DictReader(fh)}

    found = {os.path.splitext(f)[0]: os.path.join(FOUND_DIR, f)
             for f in os.listdir(FOUND_DIR)}

    repaired = adopted = dropped = 0
    kept = []
    problems = []

    for r in rows:
        if (r["DELETE"] or "").strip():
            dropped += 1
            continue

        bid = r["book_id"]
        a = auth.get(bid, {})

        # --- ISBN: repair Excel damage, keep anything newly typed ---
        raw = (r["isbn13"] or "").strip()
        if SCI.match(raw):
            d = clean_isbn(a.get("isbn13", ""))
            repaired += 1
        else:
            d = clean_isbn(raw)
        if d and not valid13(d):
            problems.append((bid, "isbn13 fails check digit: %r" % raw))
            d = ""
        r["isbn13"] = d
        r["isbn10"] = isbn13_to_10(d) if d else ""
        if not r["asin"].strip():
            r["asin"] = (a.get("asin", "") or "").strip()

        # --- Cover: adopt a hand-sourced file if one was supplied ---
        if bid in found:
            with Image.open(found[bid]) as im:
                rgb = im.convert("RGB")
                rgb.save(os.path.join(HIRES, bid + ".png"), "PNG")
                w, h = rgb.size
            r["cover_width"], r["cover_height"] = w, h
            r["cover_quality"] = quality(w)
            r["cover_source"] = "hand-sourced"
            r["cover_source_url"] = "FOUND/" + os.path.basename(found[bid])
            r["cover_notes"] = ""
            adopted += 1

        if not r["isbn10"] and not r["asin"].strip():
            problems.append((bid, "no ISBN-10 and no ASIN - link stays a search URL"))
        r["NEEDS_ISBN"] = "YES" if (not r["isbn10"] and not r["asin"].strip()) else ""
        r["NEEDS_BETTER_COVER"] = "YES" if r["cover_quality"] == "weak" else ""
        kept.append(r)

    kept.sort(key=lambda r: r["title_short"].lower())
    with open(OUT, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(kept)

    from collections import Counter
    print("dropped (DELETE=yes):      %d" % dropped)
    print("carried forward:           %d" % len(kept))
    print("ISBNs repaired from manifest: %d" % repaired)
    print("hand-sourced covers adopted:  %d" % adopted)
    print("cover_quality:", dict(Counter(r["cover_quality"] for r in kept)))
    if problems:
        print("\nneeds your attention:")
        for bid, msg in problems:
            print("   %-44s %s" % (bid, msg))
    print("\nWrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
