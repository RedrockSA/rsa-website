"""Compile everything into one reviewable CSV: covers/books_master.csv.

Joins the cover manifest, the ISBN/affiliate data, the cover-quality report and
the original Goodreads export into a single row per book, and adds the empty
columns needed for review and for a future database (DELETE, TAGS, NOTES_MINE).

Review columns come first so the file is usable straight out of a spreadsheet.
"""

import csv
import os
import re
import sys

MANIFEST = os.path.join("covers", "manifest_final.csv")
REPORT = os.path.join("covers", "hires_report.csv")
GOODREADS = "goodreads_library_export_full_read_list_260913.csv"
OUT = os.path.join("covers", "books_master.csv")

GOOD, USABLE = 300, 200

FIELDS = [
    # --- review columns: you fill these in ---
    "DELETE",
    "NEEDS_BETTER_COVER",
    "NEEDS_ISBN",
    "TAGS",
    "NOTES_MINE",
    # --- identity ---
    "book_id",
    "title_short",
    "title_full",
    "author",
    "author_lastname",
    # --- commerce ---
    "isbn13",
    "isbn10",
    "asin",
    "amazon_url",
    "link_type",
    # --- cover ---
    "cover_file",
    "cover_width",
    "cover_height",
    "cover_quality",
    "cover_source",
    "cover_source_url",
    "cover_notes",
    # --- your reading data, from Goodreads ---
    "my_rating",
    "date_read",
    "date_added",
    "publisher",
    "binding",
    "pages",
    "year_published",
    "original_pub_year",
    # --- provenance / confidence ---
    "id_confidence",
    "id_notes",
    "source_block",
    "goodreads_title",
    "goodreads_author",
]


def quality(w):
    w = int(w or 0)
    return "good" if w >= GOOD else ("usable" if w >= USABLE else "weak")


def main():
    with open(MANIFEST, encoding="utf-8-sig") as fh:
        man = list(csv.DictReader(fh))
    with open(REPORT, encoding="utf-8-sig") as fh:
        rep = {r["final_filename"]: r for r in csv.DictReader(fh)}
    with open(GOODREADS, encoding="utf-8-sig") as fh:
        gr = [r for r in csv.DictReader(fh) if r["Title"].strip()]

    # Join back to Goodreads on the exact (Title, Author) we matched earlier.
    gidx = {}
    for g in gr:
        gidx.setdefault((g["Title"].strip(), g["Author"].strip()), g)

    out = []
    for m in man:
        name = m["final_filename"]
        r = rep.get(name, {})
        g = gidx.get((m.get("goodreads_title", "").strip(),
                      m.get("goodreads_author", "").strip()), {})

        w = r.get("width", 0)
        q = quality(w)
        # Either an ISBN-10 or an ASIN yields a direct /dp/ link.
        has_isbn = bool(m.get("isbn10")) or bool((m.get("asin") or "").strip())

        out.append({
            "DELETE": "",
            "NEEDS_BETTER_COVER": "YES" if q == "weak" else "",
            "NEEDS_ISBN": "YES" if not has_isbn else "",
            "TAGS": "",
            "NOTES_MINE": "",

            "book_id": name[:-4],
            "title_short": m["title_short"],
            "title_full": m["title_full"],
            "author": m["author"],
            "author_lastname": name.split("_", 1)[0],

            "isbn13": m.get("isbn13", ""),
            "isbn10": m.get("isbn10", ""),
            "asin": m.get("asin", ""),
            "amazon_url": m.get("amazon_url", ""),
            "link_type": m.get("link_type", ""),

            "cover_file": name,
            "cover_width": r.get("width", ""),
            "cover_height": r.get("height", ""),
            "cover_quality": q,
            "cover_source": r.get("via", ""),
            "cover_source_url": r.get("source_url", ""),
            "cover_notes": r.get("notes", "") or "",

            "my_rating": g.get("My Rating", ""),
            "date_read": g.get("Date Read", ""),
            "date_added": g.get("Date Added", ""),
            "publisher": g.get("Publisher", ""),
            "binding": g.get("Binding", ""),
            "pages": g.get("Number of Pages", ""),
            "year_published": g.get("Year Published", ""),
            "original_pub_year": g.get("Original Publication Year", ""),

            "id_confidence": m.get("confidence", ""),
            "id_notes": m.get("notes", ""),
            "source_block": m.get("filename", ""),
            "goodreads_title": m.get("goodreads_title", ""),
            "goodreads_author": m.get("goodreads_author", ""),
        })

    # Weak covers and missing ISBNs float to the top so review starts there.
    order = {"weak": 0, "usable": 1, "good": 2}
    out.sort(key=lambda r: (order[r["cover_quality"]],
                            0 if r["NEEDS_ISBN"] else 1,
                            r["title_short"].lower()))

    with open(OUT, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)

    from collections import Counter
    print("Wrote %s  (%d rows, %d columns)" % (OUT, len(out), len(FIELDS)))
    print("  cover_quality:", dict(Counter(r["cover_quality"] for r in out)))
    print("  NEEDS_BETTER_COVER=YES:", sum(1 for r in out if r["NEEDS_BETTER_COVER"]))
    print("  NEEDS_ISBN=YES:", sum(1 for r in out if r["NEEDS_ISBN"]))
    print("  both flags:", sum(1 for r in out if r["NEEDS_BETTER_COVER"] and r["NEEDS_ISBN"]))
    missing_gr = sum(1 for r in out if not r["date_read"] and not r["publisher"])
    if missing_gr:
        print("  rows with no Goodreads metadata joined:", missing_gr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
