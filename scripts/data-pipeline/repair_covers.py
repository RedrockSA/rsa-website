"""Undo the bad substitutions the title-search pass made.

Open Library's search-by-title returned, for some books, a wrong book, a
foreign-language edition, a library scan with a barcode sticker over the art,
a blank cloth board, or a 'cover coming soon' placeholder. Those were caught
by eye, not by any metric, so the list is explicit and hand-checked.

For each, prefer a fresh ISBN-keyed fetch (edition-accurate) and fall back to
the original screenshot crop if that fails.
"""

import csv
import io
import os
import sys
import time
import urllib.error
import urllib.request

from PIL import Image

REPORT = os.path.join("covers", "hires_report.csv")
ISBN_SRC = os.path.join("covers", "manifest_isbn.csv")
OUT_DIR = "covers_hires"
CUR_DIR = "covers"
UA = "RedRockSA-book-covers/1.0 (gloos@redrocksa.com)"

# filename -> what was wrong with the image the title-search pass installed
REJECT = {
    "mckeown_essentialism.png": "'cover coming soon' placeholder",
    "watson_the-double-helix.png": "wrong book (Discovering the Double Helix)",
    "liu_the-three-body-problem.png": "wrong book (The Dark Forest)",
    "rowling_harry-potter-and-the-sorcerers-stone.png": "Scholastic study guide, not the novel",
    "hinton_the-outsiders.png": "Portuguese edition, 3D mockup render",
    "rowling_harry-potter-and-the-chamber-of-secrets.png": "Korean edition",
    "isaacson_steve-jobs.png": "Portuguese edition",
    "chapman_the-5-love-languages.png": "Singles Edition, a different book",
    "tolkien_the-two-towers.png": "blank cloth board, no cover art",
    "tolkien_the-fellowship-of-the-ring.png": "blank cloth board, no cover art",
    "collins_the-woman-in-white.png": "blank board, no cover art",
    "rand_the-fountainhead.png": "blank board, no cover art",
    "mukherjee_the-gene.png": "library scan with barcode sticker over the art",
    "mukherjee_the-emperor-of-all-maladies.png": "library scan with barcode sticker",
    "goodwin_team-of-rivals.png": "library scan with barcode overlay",
}


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
    with open(REPORT, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    with open(ISBN_SRC, encoding="utf-8-sig") as fh:
        isbns = {r["final_filename"]: r for r in csv.DictReader(fh)}

    fixed = reverted = 0
    for r in rows:
        name = r["final_filename"]
        if name not in REJECT:
            continue

        best = None
        src = isbns.get(name, {})
        for isbn in (src.get("isbn13", ""), src.get("isbn", "")):
            if isbn:
                im = load_image("https://covers.openlibrary.org/b/isbn/%s-L.jpg"
                                "?default=false" % isbn)
                time.sleep(0.6)
                if im:
                    best = (im, "https://covers.openlibrary.org/b/isbn/%s-L.jpg" % isbn,
                            "isbn-refetch")
                    break

        if best is None:
            orig = os.path.join(CUR_DIR, name)
            if os.path.exists(orig):
                with Image.open(orig) as im:
                    best = (im.convert("RGB").copy(), "local:covers/" + name, "reverted")

        if best is None:
            print("  !! no replacement for %s" % name)
            continue

        im, url, via = best
        im.convert("RGB").save(os.path.join(OUT_DIR, name), "PNG")
        r["width"], r["height"] = im.size
        r["source_url"] = url
        r["via"] = via
        r["status"] = "ok" if im.width >= 300 else "small"
        r["notes"] = "title-search result rejected: " + REJECT[name]
        if via == "isbn-refetch":
            fixed += 1
        else:
            reverted += 1
        print("  %-10s %4dx%-4d %-46s %s"
              % (via, im.size[0], im.size[1], name[:46], REJECT[name]))

    fields = list(rows[0].keys())
    if "notes" not in fields:
        fields.append("notes")
    with open(REPORT, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    print("\nre-fetched by ISBN: %d   reverted to original crop: %d" % (fixed, reverted))
    print("status now:", dict(Counter(r["status"] for r in rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
