#!/usr/bin/env node
/**
 * Regenerates src/content/books/*.md from data/books.csv.
 *
 * Reads YOUR actual CSV columns directly (title_short/title_full,
 * topics, secondary_category, type, etc.) rather than forcing a reshaped
 * format - see README for the full column reference and the reasoning
 * behind each mapping.
 *
 * Full regeneration each run, not a merge: the books directory is cleared
 * and rewritten from the current CSV every time, so removed/renamed rows
 * propagate too. Generated .md files are build output - don't hand-edit
 * them, edit the CSV.
 *
 * Usage: node scripts/generate-books.mjs [path/to/books.csv]
 */
import { parse } from 'csv-parse/sync';
import { readFileSync, writeFileSync, mkdirSync, readdirSync, unlinkSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const CSV_PATH = process.argv[2] || 'src/data/books.csv';
const OUT_DIR = 'src/content/books';

// Covers are deterministically named <book_id>.webp by scripts/prepare-covers.mjs,
// so the path is derived rather than carried as a CSV column - one less thing to
// keep in sync by hand. MAX_COVER_W must match prepare-covers.mjs.
const COVER_DIR = 'public/books/covers';
const COVER_URL = '/books/covers';
const MAX_COVER_W = 400;
let missingCovers = 0;

function slugify(input) {
  return input.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

function splitList(value) {
  return String(value ?? '')
    .split(';')
    .map((s) => s.trim())
    .filter(Boolean);
}

function toInt(value) {
  const n = parseInt(String(value ?? '').trim(), 10);
  return Number.isFinite(n) ? n : undefined;
}

// Amazon URLs in this CSV already carry the affiliate tag and, embedded in
// the path, the ASIN itself - e.g. https://www.amazon.com/dp/0307719219?tag=...
function extractAsinFromUrl(url) {
  const match = String(url ?? '').match(/\/dp\/([A-Z0-9]{10})/i);
  return match?.[1];
}

// YAML double-quoted scalar: escape backslashes/quotes, keep it one line.
function yamlString(value) {
  return `"${String(value).replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`;
}

function yamlList(values) {
  return `[${values.map(yamlString).join(', ')}]`;
}

if (!existsSync(CSV_PATH)) {
  console.error(`[generate-books] No CSV at ${CSV_PATH} - leaving src/content/books untouched.`);
  process.exit(0);
}

const rows = parse(readFileSync(CSV_PATH, 'utf-8'), {
  columns: true,
  skip_empty_lines: true,
  trim: true,
  bom: true,
});

mkdirSync(OUT_DIR, { recursive: true });
// Files are overwritten in place and only genuinely stale ones removed, at
// the end. Clearing the directory up front used to fail with EPERM on
// Windows whenever `astro dev` held a lock, leaving the collection emptied
// half way through. Overwriting is safe under a lock; a failed delete of one
// stale file is not worth aborting the run for.
const existingFiles = readdirSync(OUT_DIR).filter((f) => f.endsWith('.md'));

let written = 0;
let skipped = 0;
const seenSlugs = new Set();
const genreTally = new Map();
const subjectTally = new Map();
const shelfTally = new Map();

rows.forEach((row, i) => {
  const line = i + 2; // header is line 1
  const title = (row.title_short || row.title_full)?.trim();
  const author = row.author?.trim();

  if (!title || !author) {
    console.warn(`[generate-books] Row ${line}: missing title or author - skipped.`);
    skipped++;
    return;
  }

  const slug = row.book_id?.trim() || slugify(title);
  if (seenSlugs.has(slug)) {
    console.warn(`[generate-books] Row ${line} ("${title}"): slug "${slug}" collides with an earlier row - skipped.`);
    skipped++;
    return;
  }
  seenSlugs.add(slug);

  const subtitle =
    row.title_full?.trim() && row.title_full.trim().toLowerCase() !== title.toLowerCase()
      ? row.title_full.trim()
      : undefined;

  if (!row.primary_category?.trim()) {
    console.warn(`[generate-books] Row ${line} ("${title}"): no primary_category set - will land in "Unshelved" on the homepage.`);
  } else {
    shelfTally.set(row.primary_category.trim(), (shelfTally.get(row.primary_category.trim()) || 0) + 1);
  }

  const genres = splitList(row.topics);
  const subjects = splitList(row.secondary_category);
  genres.forEach((g) => genreTally.set(g, (genreTally.get(g) || 0) + 1));
  subjects.forEach((s) => subjectTally.set(s, (subjectTally.get(s) || 0) + 1));
  if (genres.length === 0) {
    console.warn(`[generate-books] Row ${line} ("${title}"): no topics value - will only show up under Fiction/no-genre filtering.`);
  }

  const asin = row.asin?.trim() || extractAsinFromUrl(row.amazon_url);

  // Derive the cover path, and report rather than silently shipping a blank card.
  const coverFile = `${slug}.webp`;
  const coverImage = existsSync(join(COVER_DIR, coverFile)) ? `${COVER_URL}/${coverFile}` : undefined;
  if (!coverImage) {
    console.warn(`[generate-books] Row ${line} ("${title}"): no cover at ${COVER_DIR}/${coverFile}`);
    missingCovers++;
  }

  // The CSV records the ORIGINAL dimensions; what ships is capped at
  // MAX_COVER_W. Scale so width/height attributes match the served file and
  // the browser reserves the right box.
  const srcW = toInt(row.cover_width);
  const srcH = toInt(row.cover_height);
  const shipped = {};
  if (srcW !== undefined && srcH !== undefined) {
    shipped.width = Math.min(srcW, MAX_COVER_W);
    shipped.height = Math.round(srcH * (shipped.width / srcW));
  }

  const frontmatterLines = [
    '---',
    `title: ${yamlString(title)}`,
    subtitle ? `subtitle: ${yamlString(subtitle)}` : null,
    `author: ${yamlString(author)}`,
    row.author_lastname?.trim() ? `authorLastName: ${yamlString(row.author_lastname.trim())}` : null,
    row.isbn13?.trim() ? `isbn13: ${yamlString(row.isbn13.trim())}` : null,
    row.isbn10?.trim() ? `isbn10: ${yamlString(row.isbn10.trim())}` : null,
    asin ? `asin: ${yamlString(asin)}` : null,
    row.amazon_url?.trim() ? `amazonUrl: ${yamlString(row.amazon_url.trim())}` : null,
    row.publisher?.trim() ? `publisher: ${yamlString(row.publisher.trim())}` : null,
    toInt(row.pages) !== undefined ? `pages: ${toInt(row.pages)}` : null,
    toInt(row.year_published) !== undefined ? `yearPublished: ${toInt(row.year_published)}` : null,
    toInt(row.original_pub_year) !== undefined ? `originalPublicationYear: ${toInt(row.original_pub_year)}` : null,
    `type: ${row.type?.trim() === 'fiction' ? 'fiction' : 'non-fiction'}`,
    row.primary_category?.trim() ? `primaryCategory: ${yamlString(row.primary_category.trim())}` : null,
    `topics: ${yamlList(genres)}`,
    `secondaryCategories: ${yamlList(subjects)}`,
    row.geography?.trim() ? `geography: ${yamlString(row.geography.trim())}` : null,
    coverImage ? `coverImage: ${yamlString(coverImage)}` : null,
    shipped.width !== undefined ? `coverWidth: ${shipped.width}` : null,
    shipped.height !== undefined ? `coverHeight: ${shipped.height}` : null,
    `oneLiner: ${yamlString(row.notes?.trim() || '')}`,
    toInt(row.my_rating) !== undefined ? `myRating: ${toInt(row.my_rating)}` : null,
    row.date_read?.trim() ? `dateRead: ${row.date_read.trim()}` : null,
    `dateAdded: ${row.date_added?.trim() || row.dateAdded?.trim() || new Date().toISOString().slice(0, 10)}`,
    '---',
  ].filter(Boolean);

  const notice = `<!-- Auto-generated from ${CSV_PATH} - edit the CSV, not this file. Regenerate with \`npm run generate:books\`. -->`;

  writeFileSync(join(OUT_DIR, `${slug}.md`), `${frontmatterLines.join('\n')}\n\n${notice}\n`);
  written++;
});

// Remove .md files for rows that are no longer in the CSV.
let stale = 0;
for (const file of existingFiles) {
  if (seenSlugs.has(file.replace(/\.md$/, ''))) continue;
  try {
    unlinkSync(join(OUT_DIR, file));
    stale++;
  } catch (err) {
    console.warn(`[generate-books] Could not remove stale ${file}: ${err.code}. ` +
      `Stop \`astro dev\` and re-run if it lingers.`);
  }
}

console.log(`[generate-books] Wrote ${written} book file(s) from ${CSV_PATH}${skipped ? `, skipped ${skipped} row(s) - see warnings above` : ''}${stale ? `, removed ${stale} stale file(s)` : ''}.`);
console.log(`[generate-books] Covers: ${written - missingCovers}/${written} found${missingCovers ? `, ${missingCovers} MISSING` : ''}.`);
console.log(`[generate-books] Home shelves (${shelfTally.size}):`, Object.fromEntries([...shelfTally.entries()].sort()));
console.log(`[generate-books] Distinct genres seen (${genreTally.size}):`, Object.fromEntries([...genreTally.entries()].sort()));
console.log(`[generate-books] Distinct subjects seen (${subjectTally.size}):`, Object.fromEntries([...subjectTally.entries()].sort()));
