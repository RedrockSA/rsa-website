# Red Rock book list

Book recommendations for business owners, extracted from screenshots of a
Goodreads "read" shelf, identified, tagged, and paired with Amazon Associates
links (tag `redrock07-20`).

## Layout

```
src/data/
  books.csv          THE DATABASE - 109 books, 24 columns, keyed on isbn13
                     Hand-edited. Read by scripts/generate-books.mjs, which
                     regenerates src/content/books/*.md on dev and build.

data/
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

`isbn13` is the primary key - present, unique and check-digit valid on all 109
rows. `book_id` is the URL slug and the cover filename: `covers/<book_id>.png`.

Multi-value columns are **semicolon-separated**: `topics` and
`secondary_category`. In a real database these become a join table; the CSV
keeps them inline so the file stays editable in a spreadsheet.

Category values are lowercase slugs, and they are identity, not display text -
the same string is the filter key and the URL query value. An `-and-` in a slug
is how a two-part name asks for an ampersand when rendered:
`health-and-food` shows as "Health & Food". See `facetLabel()` in
`src/utils/shelves.ts`; `SHELF_LABELS` in the same file overrides a primary
category whose name the rule cannot produce.

A `tags` column used to sit alongside these, holding the union of the other
classification columns. Nothing read it, so it was removed.

| column | notes |
|---|---|
| `isbn13` | primary key |
| `isbn10` | empty for 979- prefixed books, which have no ISBN-10 |
| `asin` | Amazon id; set only where no ISBN-10 exists |
| `type` | fiction / non-fiction |
| `primary_category` | one per book - the shelf, and the Primary Category filter (14 values) |
| `topics` | granular, multi-value: decision-making, investing, ... (27 values) |
| `secondary_category` | broad buckets, multi-value: culture, philosophy, ... (10 values) |
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

**Nothing in this folder runs against the live site.** These are the one-shot
pipeline that built the list, kept for provenance - how covers were sourced,
how ISBNs were resolved, how rows were matched to the Goodreads export. The
only script in the build path is `scripts/generate-books.mjs`, one level up,
which runs automatically on `npm run dev` and `npm run build`.

Superseded - do not run:

- `tag_books.py`, `_regen_tag_table.py` - these rewrote the classification
  columns from a table held inside the script, and the old README said to edit
  categories there rather than in the CSV. That is no longer true: both target
  `data/books.csv` and the old column names (`business_genre`, `subject`,
  `home_shelf`), none of which exist now. **Categories are edited directly in
  `src/data/books.csv`.**
- `build_db.py` - assembled the CSV from the build's working files, including
  the `tags` column that has since been dropped.

Kept for reference. Paths refer to the pre-reorganisation layout and would need
updating to re-run: `build_links.py` (regenerates `amazon_url` from
`isbn10`/`asin`; pass `--tag` to change the Associates id), `extract_covers.py`
(grid detection and cropping), `build_manifest.py`, `match_goodreads.py`,
`fetch_covers.py`, `fetch_ol_search.py`, `fetch_gbooks.py`, `repair_covers.py`,
`resolve_isbns.py`, `apply_user_isbns.py`, `apply_review.py`,
`rename_covers.py`, `build_master.py`.

## Known limits

- One cover is below 300px: `kim_a-necessary-lie` (257x385). A KDP title; a
  larger version may not exist publicly.
- Cover art is publisher copyright. Affiliate linking supports an editorial-use
  argument but is not a licence. The Product Advertising API is the route to
  licensed images, and it requires qualifying sales first.
- `Rand_Capitalism.jpg` is a different edition from the one in the screenshot.
