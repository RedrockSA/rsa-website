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

/** Display names for shelf slugs. Anything absent is title-cased. */
export const SHELF_LABELS: Record<string, string> = {
  'leadership': 'Leadership',
  'corporate-history': 'Corporate History',
  'economics': 'Economics',
  'technology-and-science': 'Technology & Science',
  'operations': 'Operations',
  'psychology': 'Psychology',
  'strategy': 'Strategy',
  'teamwork': 'Teamwork',
  'health': 'Health',
  'personal-effectiveness': 'Personal Effectiveness',
  'social-commentary': 'Social Commentary',
  'history': 'History',
  'memoir-biography': 'Memoirs & Biography',
  'relevant-fiction': 'Relevant Fiction',
};

export function shelfLabel(slug: string): string {
  return (
    SHELF_LABELS[slug] ||
    slug.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
  );
}

/** The three shelves given their own 2x2 block across the top. */
export const FEATURED_SHELVES = ['leadership', 'corporate-history', 'economics'];

/** Covers shown per featured shelf before "More..." - two sits the three
 *  shelves side by side in one row rather than wrapping. */
export const FEATURED_PREVIEW = 2;

/**
 * Full-width rows beneath. `shelves` may merge several slugs under one
 * heading - "Histories" in the mockup's label is why memoir-biography and
 * history sit together here.
 */
export const SHELF_BANDS: { label: string; shelves: string[]; slug: string }[] = [
  {
    label: 'Biographies, Memoirs & Histories',
    slug: 'biographies-memoirs-histories',
    shelves: ['memoir-biography', 'history'],
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
 * The Reading List with nothing filtered. Needed because a bare
 * /insights/books opens on the default category - this opts out of that.
 */
export const READING_LIST_ALL = '/insights/books/?all=1';
