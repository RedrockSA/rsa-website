# Red Rock book list

Book recommendations for business owners, extracted from screenshots of a
Goodreads "read" shelf, identified, tagged, and paired with Amazon Associates
links (tag `redrock07-20`).

## Layout

```
data/
  books.csv          THE DATABASE - 111 books, 25 columns, keyed on isbn13
  provenance.csv     where each cover and each identification came from
  goodreads_library_export_full_read_list_260913.csv
  archive/           superseded working files from the build

covers/              111 cover images, one per row, named <book_id>.png

source/
  screenshots/       the 8 original grid screenshots
  crops/             173 raw crops cut from those screenshots
  fetched/           173 best-available images from Open Library
  hand-sourced/      16 covers sourced by hand, highest quality in the set

scripts/             build scripts (see below)
```

## books.csv

`isbn13` is the primary key - present, unique and check-digit valid on all 111
rows. `book_id` is the URL slug and the cover filename: `covers/<book_id>.png`.

Multi-value columns are **semicolon-separated**: `business_genre`, `subject`,
`geography`, `tags`. In a real database these become a join table; the CSV keeps
them inline so the file stays editable in a spreadsheet.

| column | notes |
|---|---|
| `isbn13` | primary key |
| `isbn10` | empty for 979- prefixed books, which have no ISBN-10 |
| `asin` | Amazon id; set only where no ISBN-10 exists |
| `type` | fiction / non-fiction |
| `business_genre` | leadership, strategy, economics, operations, ... (15 values) |
| `subject` | history, biography, psychology, ... (22 values) |
| `era_subject` | the period the book is *about* |
| `era_published` | derived from the year - never edit by hand |
| `my_rating` | 1-5, or empty if unrated. Goodreads' 0 has been blanked |
| `date_read` | ISO `YYYY-MM-DD` |
| `cover_width` / `cover_height` | set these on the `<img>` tag to avoid layout shift |

### Editing it

ISBNs are stored **hyphenated** (`978-0-451526342`, `0-451526341`) precisely so
that Excel cannot coerce them. A plain digit string gets turned into
`9.78125E+12`, and a leading zero gets stripped silently - both destroy the
value. The hyphens make the cell non-numeric, so you can open, edit and save
this file in Excel normally.

Strip them wherever code needs the raw digits:

```python
isbn = row["isbn13"].replace("-", "")
```

An un-hyphenated copy is kept at `data/archive/books_plain-isbn.csv`.

One column Excel still touches: `date_read`. Excel recognises `2021-12-12` as a
date and may write it back in local format (`12/12/2021`) on save. That is
cosmetic and re-normalising is one command - just say so after an edit.

## scripts/

Only two are still live:

- `tag_books.py` - rewrites the classification columns in `data/books.csv` from
  the table inside it. Edit tags there, not in the CSV, or a re-run overwrites
  them. It does not touch `notes`.
- `build_links.py` - regenerates `amazon_url` from `isbn10`/`asin`. Pass
  `--tag` to change the Associates id.

The rest are the one-shot build pipeline, kept for reference. Their paths refer
to the pre-reorganisation layout and would need updating to re-run:
`extract_covers.py` (grid detection and cropping), `build_manifest.py`,
`match_goodreads.py`, `fetch_covers.py`, `fetch_ol_search.py`, `fetch_gbooks.py`,
`repair_covers.py`, `resolve_isbns.py`, `apply_user_isbns.py`, `apply_review.py`,
`rename_covers.py`, `build_master.py`, `build_db.py`.

## Known limits

- One cover is below 300px: `kim_a-necessary-lie` (257x385). A KDP title; a
  larger version may not exist publicly.
- Cover art is publisher copyright. Affiliate linking supports an editorial-use
  argument but is not a licence. The Product Advertising API is the route to
  licensed images, and it requires qualifying sales first.
- `Rand_Capitalism.jpg` is a different edition from the one in the screenshot.
