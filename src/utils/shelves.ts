/**
 * Shelf configuration for the "Redrock Reading List" module.
 *
 * Shelf slugs come from the `primary_category` column in src/data/books.csv - one
 * shelf per book, all 110 assigned. This file decides how those 14 shelves
 * are presented, which is an editorial choice, not a data one.
 *
 * Layout (from the design mockup):
 *   - FEATURED   three shelves as 2x2 cover blocks across the top, each with "More..."
 *   - BANDS      two full-width rows below, the big general-interest groups
 *   - rail       everything else, listed as filters with counts
 */

/**
 * Display name for any facet value - primary shelves, secondary categories,
 * topics, geography, type. One function for all five, so a slug never reads
 * two different ways depending on where it appears.
 *
 * Every label is derived from its slug; there is no override table. Slugs stay
 * lowercase and URL-safe because the slug is identity - it is the filter key
 * and the URL query value, not the label. An `-and-` in a slug is how a
 * two-part name asks for an ampersand: health-and-food -> Health & Food.
 *
 * So renaming a shelf is a CSV edit, not a code edit. The exception is a label
 * the rule cannot reach at all - a plural the slug does not carry, say. Spell
 * it into the slug (`memoir-and-biography`) rather than reintroducing a map.
 */
export function facetLabel(slug: string): string {
  return slug
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .replace(/\bAnd\b/g, '&')
    .replace(/\bWwii\b/g, 'WWII')
    .replace(/\bMba\b/g, 'MBA')
    .replace(/\bUs\b/g, 'US');
}

/** The three shelves given their own 2x2 block across the top. */
export const FEATURED_SHELVES = ['leadership', 'business-history', 'economics'];

/** Covers shown per featured shelf before "More..." - two sits the three
 *  shelves side by side in one row rather than wrapping. */
export const FEATURED_PREVIEW = 2;

/**
 * Full-width rows beneath. `shelves` may merge several slugs under one
 * heading - "Histories" in the mockup's label is why biography-and-memoir
 * and history sit together here.
 *
 * These slugs are the one place code names a shelf: rename one in the CSV
 * and it must be renamed here too, or the shelf drops out of the layout.
 */
export const SHELF_BANDS: { label: string; shelves: string[]; slug: string }[] = [
  {
    label: 'Biographies, Memoirs & Histories',
    slug: 'biographies-memoirs-histories',
    shelves: ['biography-and-memoir', 'history'],
  },
  {
    label: 'Relevant Fiction',
    slug: 'relevant-fiction',
    shelves: ['relevant-fiction'],
  },
];

/** Shelves that already have a visual block, so they don't repeat in the rail. */
const PLACED = new Set([
  ...FEATURED_SHELVES,
  ...SHELF_BANDS.flatMap((b) => b.shelves),
]);

/** Everything else, largest first - rendered as the filter rail. */
export function railShelves(counts: Map<string, number>): string[] {
  return [...counts.keys()]
    .filter((s) => !PLACED.has(s))
    .sort((a, b) => (counts.get(b) ?? 0) - (counts.get(a) ?? 0));
}

/** Where a book's detail page lives - a subpage of Insights. */
export function bookUrl(slug: string): string {
  return `/insights/books/${slug}/`;
}

/**
 * A Reading List link that arrives with the Primary Category filter applied.
 * Pass one shelf, or several for a merged band. The page reads these on load,
 * which is why links carry a query string rather than a #anchor - the list is
 * one filtered grid now, not a page of anchored sections.
 */
export function readingListUrl(shelves: string[] = []): string {
  if (!shelves.length) return READING_LIST_ALL;
  return `/insights/books/?primary=${shelves.map(encodeURIComponent).join(',')}`;
}

/**
 * The Reading List with nothing filtered. A bare /insights/books already
 * opens on the full list, so this is explicit rather than load-bearing.
 */
export const READING_LIST_ALL = '/insights/books/?all=1';
