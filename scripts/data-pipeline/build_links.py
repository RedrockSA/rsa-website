"""Add Amazon Associates affiliate links to the manifest.

For print books Amazon's ASIN is the ISBN-10, so a direct product link is
  https://www.amazon.com/dp/<isbn10>?tag=<your-associate-tag>
An ISBN-13 beginning 978 converts to ISBN-10 arithmetically, so rows that
only carry an ISBN-13 still get a direct link. Rows with no ISBN at all fall
back to a tagged Amazon search URL, which still credits the tag.

Pass your Associates tag with --tag once you have it; the default is a
placeholder so the column is reviewable before you sign up.
"""

import argparse
import csv
import os
import sys
import urllib.parse

SRC = os.path.join("covers", "manifest_isbn.csv")
OUT = os.path.join("covers", "manifest_final.csv")


def isbn13_to_isbn10(isbn13):
    """978-prefixed ISBN-13 -> ISBN-10. Returns '' if not convertible."""
    d = "".join(ch for ch in isbn13 if ch.isdigit())
    if len(d) != 13 or not d.startswith("978"):
        return ""
    core = d[3:12]
    total = sum((10 - i) * int(c) for i, c in enumerate(core))
    check = (11 - (total % 11)) % 11
    return core + ("X" if check == 10 else str(check))


def pick_isbn10(row):
    raw = (row.get("isbn") or "").strip().upper()
    if len(raw) == 10:
        return raw
    return isbn13_to_isbn10(row.get("isbn13") or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="YOURTAG-20",
                    help="your Amazon Associates tracking id, e.g. redrocksa-20")
    args = ap.parse_args()

    with open(SRC, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    direct = viaasin = search = 0
    for r in rows:
        isbn10 = pick_isbn10(r)
        r["isbn10"] = isbn10
        # An explicit ASIN wins: KDP titles (979- prefixes) and audiobooks have
        # no ISBN-10, but Amazon still addresses them by ASIN in a /dp/ link.
        asin = (r.get("asin") or "").strip().upper()
        if asin:
            r["amazon_url"] = "https://www.amazon.com/dp/%s?tag=%s" % (asin, args.tag)
            r["link_type"] = "direct-asin"
            viaasin += 1
        elif isbn10:
            r["amazon_url"] = "https://www.amazon.com/dp/%s?tag=%s" % (isbn10, args.tag)
            r["link_type"] = "direct"
            direct += 1
        else:
            q = urllib.parse.urlencode({
                "k": "%s %s" % (r["title_short"], r["author"]),
                "i": "stripbooks",
                "tag": args.tag,
            })
            r["amazon_url"] = "https://www.amazon.com/s?" + q
            r["link_type"] = "search"
            search += 1

    with open(OUT, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("rows: %d   direct /dp/ (isbn10): %d   direct /dp/ (asin): %d   search fallbacks: %d"
          % (len(rows), direct, viaasin, search))
    print("tag used: %s" % args.tag)
    if args.tag == "YOURTAG-20":
        print("  (placeholder - rerun with --tag once your Associates id is issued)")
    print("Wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
