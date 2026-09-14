# Reading list — where everything lives

Everything for the book feature is inside this repo. Nothing outside it is
needed to build, edit, or rebuild the reading list.

## The one file you edit

```
src/data/books.csv
```

110 rows, 27 columns, keyed on `isbn13`. Tags, titles, authors, Amazon links,
shelf assignments — all of it. Change this, run one command, and the site
follows.

**Opening it in Excel is safe**: ISBNs are stored hyphenated (`978-0-307719218`)
precisely so Excel can't mangle them into `9.78125E+12` or strip a leading zero.

**One thing Excel does still change**: `date_read` and `date_added` are ISO
(`2024-01-28`). Excel rewrites them as `1/28/2024` on save. That is cosmetic
and one command fixes it — just say so after an edit.

### Columns that drive the site

| column | what it does |
|---|---|
| `home_shelf` | the **Category** filter, and the shelves on /insights |
| `business_genre` | the **Topic** filter (semicolon-separated) |
| `subject` | the **Subject** filter (semicolon-separated) |
| `geography` | the **Geography** filter |
| `type` | the **Type** filter — fiction / non-fiction |
| `amazon_url` | the affiliate link; the ASIN is read from the `/dp/` segment |
| `date_added` | default sort order (newest first) |
| `original_pub_year` | the "Published date" sort |
| `book_id` | URL slug and cover filename — changing it renames the page |
| `notes` | becomes `oneLiner`, the pitch text on a card. Currently empty for all 110 |

`era_subject` and `era_published` are still in the CSV but no longer surfaced
as filters. Harmless to leave.

## After editing

```bash
npm run dev      # regenerates and serves
npm run build    # regenerates and builds
```

Both run `generate-books.mjs` first, so the CSV is always the source of truth.
To regenerate without starting a server: `npm run generate:books`.

> **Stop the dev server before running `generate:books` by hand.** It clears and
> rewrites `src/content/books/`, and on Windows a running dev server holds locks
> on those files — the run fails partway and empties the collection. Recovery is
> just to stop the server and re-run.

## Adding or replacing a cover

1. Drop the image into `source-covers/` named `<book_id>.png` (or `.jpg`)
2. `npm run prepare:covers`
3. `npm run build`

`prepare:covers` writes a WebP set capped at 400px into `public/books/covers/`
— about 33 MB of masters down to 2.7 MB shipped. It never upscales, and it
preserves aspect ratio exactly, which matters because eight covers are nearly
square rather than the usual 1:1.5.

## Layout

```
src/data/books.csv              THE source of truth - edit this
src/content/books/*.md          GENERATED from the CSV - never edit by hand
src/components/reading/         CoverTile, ShelfBand, ReadingModule
src/utils/shelves.ts            shelf labels, featured shelves, bands
src/pages/insights.astro        the module at the bottom of Insights
src/pages/insights/books/       the Reading List page + 110 detail pages

public/books/covers/            GENERATED webp - what actually ships
source-covers/                  master images (build input, ~35 MB)
source-covers/hand-sourced/     originals sourced by hand

data/provenance.csv             where each cover and identification came from
data/goodreads_library_export_*.csv   the original Goodreads export
data/archive/                   superseded working files from the build
scripts/data-pipeline/          the one-shot scripts that produced the data
```

## Things worth knowing

- **`AMAZON_ASSOCIATE_TAG` must be set in Cloudflare's environment**, not just
  local `.env`. The helper falls back to `your-tag-20`, so production would
  silently ship links that earn nothing.
- `source-covers/` is ~35 MB. It is the input for regenerating every cover, so
  it belongs in the repo — but if the clone size ever becomes a problem it can
  be gitignored, at the cost of needing it back to re-run `prepare:covers`.
- The old `sandbox/bookcovers/` project still holds the build intermediates:
  the 8 grid screenshots, 173 raw crops, and 173 fetched images (~57 MB). None
  are needed any more; they are evidence of how the list was assembled.
