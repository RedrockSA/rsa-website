"""Produce the clean, deployable book database from the working file.

Keeps the fields a website actually renders or queries; everything that was
scaffolding for the build (review flags, per-cover source URLs, vision-read
confidence) moves to a separate provenance file rather than being discarded.

Two normalisations worth knowing about:
  - Goodreads writes 0 for an unrated book. That is not a rating, so it
    becomes empty.
  - Dates become ISO (YYYY-MM-DD) so they sort and query correctly.
"""

import csv
import os
import sys

SRC = os.path.join("covers", "books_final.csv")
DB = os.path.join("data", "books.csv")
PROV = os.path.join("data", "provenance.csv")

DB_FIELDS = [
    # keys
    "isbn13", "isbn10", "asin", "book_id",
    # bibliographic
    "title_short", "title_full", "author", "author_lastname",
    "publisher", "pages", "year_published", "original_pub_year",
    # classification
    "type", "business_genre", "subject", "era_subject", "era_published",
    "geography", "tags",
    # personal
    "my_rating", "date_read", "notes",
    # media / commerce
    "cover_width", "cover_height", "amazon_url",
]

PROV_FIELDS = [
    "isbn13", "book_id", "cover_file", "cover_quality", "cover_source",
    "cover_source_url", "cover_notes", "link_type", "id_confidence",
    "id_notes", "source_block", "goodreads_title", "goodreads_author",
    "date_added", "binding",
]


def iso_date(s):
    """Goodreads writes M/D/YYYY; ISO sorts correctly, that does not."""
    s = (s or "").strip()
    if not s:
        return ""
    parts = s.split("/")
    if len(parts) == 3:
        m, d, y = parts
        try:
            return "%04d-%02d-%02d" % (int(y), int(m), int(d))
        except ValueError:
            return s
    return s


def main():
    with open(SRC, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    os.makedirs("data", exist_ok=True)
    db, prov = [], []
    unrated = 0

    for r in rows:
        rating = (r.get("my_rating") or "").strip()
        if rating == "0":
            rating = ""          # Goodreads 0 means unrated, not one star
            unrated += 1

        db.append({
            "isbn13": r["isbn13"].strip(),
            "isbn10": r["isbn10"].strip(),
            "asin": r["asin"].strip(),
            "book_id": r["book_id"],
            "title_short": r["title_short"],
            "title_full": r["title_full"],
            "author": r["author"],
            "author_lastname": r["author_lastname"],
            "publisher": r.get("publisher", ""),
            "pages": r.get("pages", ""),
            "year_published": r.get("year_published", ""),
            "original_pub_year": r.get("original_pub_year", ""),
            "type": r.get("type", ""),
            "business_genre": r.get("business_genre", ""),
            "subject": r.get("subject", ""),
            "era_subject": r.get("era_subject", ""),
            "era_published": r.get("era_published", ""),
            "geography": r.get("geography", ""),
            "tags": r.get("TAGS", ""),
            "my_rating": rating,
            "date_read": iso_date(r.get("date_read")),
            "notes": r.get("NOTES_MINE", ""),
            "cover_width": r.get("cover_width", ""),
            "cover_height": r.get("cover_height", ""),
            "amazon_url": r.get("amazon_url", ""),
        })
        prov.append({k: r.get(k, "") for k in PROV_FIELDS})

    db.sort(key=lambda r: (r["author_lastname"], r["title_short"].lower()))
    prov.sort(key=lambda r: r["book_id"])

    for path, fields, data in ((DB, DB_FIELDS, db), (PROV, PROV_FIELDS, prov)):
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(data)

    print("%s   %d rows x %d cols" % (DB, len(db), len(DB_FIELDS)))
    print("%s  %d rows x %d cols (build history, not for the site)"
          % (PROV, len(prov), len(PROV_FIELDS)))
    print("\ndropped from the database: DELETE, NEEDS_BETTER_COVER, NEEDS_ISBN,"
          " cover_file, plus everything now in provenance.csv")
    print("my_rating: %d unrated books had 0 blanked" % unrated)
    print("date_read normalised to ISO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
