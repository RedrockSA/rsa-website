/**
 * Amazon affiliate link helper.
 *
 * IMPORTANT CONTEXT (verify current terms at https://affiliate-program.amazon.com
 * before relying on this — Amazon's program rules do change):
 *
 * - Amazon's old Product Advertising API (PA-API 5.0), which could pull live
 *   price/availability/image data, was deprecated in 2026 in favor of a new
 *   "Creators API." As of this writing, the Creators API requires an approved
 *   Associates account AND at least 10 qualifying sales in the trailing 30
 *   days just to register for API access - a real barrier for a brand-new
 *   site with no traffic yet.
 * - Scraping Amazon product pages directly is against Amazon's Terms of
 *   Service and is not something this codebase does or should do.
 *
 * Practical path for now: construct affiliate links manually from an ASIN
 * you already have (no API needed for this — just your Associates tag), and
 * source cover/metadata from Google Books or Open Library instead. Once the
 * site qualifies for Creators API access, a `getLiveOffer(asin)` function
 * can be added here to layer in live price/availability without touching
 * the rest of the site.
 */

// The Associates tag is public - it appears in every affiliate URL on the
// site - so it is the default rather than a required environment variable.
// Making it env-only meant a build without that variable silently shipped
// 'your-tag-20' and earned nothing. AMAZON_ASSOCIATE_TAG still overrides,
// which is useful for a staging site that should not report as production.
const ASSOCIATE_TAG = import.meta.env.AMAZON_ASSOCIATE_TAG || 'redrock07-20';

/** Builds a standards-compliant Amazon affiliate link from an ASIN. */
export function buildAffiliateLink(asin: string, marketplace: 'com' | 'co.uk' | 'ca' = 'com'): string {
  return `https://www.amazon.${marketplace}/dp/${asin}/?tag=${ASSOCIATE_TAG}`;
}

// Future: once Creators API access is granted, add something like
//
//   export async function getLiveOffer(asin: string) { ... }
//
// and call it at build time (or behind a cached edge function) to show
// live price/availability next to the static affiliate link — but treat
// it as an enhancement, not a dependency, since eligibility can lapse if
// qualifying sales drop off.
