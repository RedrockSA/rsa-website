/**
 * Responsive variant definitions for the large images in public/.
 *
 * Shared deliberately: scripts/generate-hero-variants.mjs writes the files and
 * src/components/HeroImage.astro writes the srcset that points at them. If the
 * two disagreed, the srcset would reference variants that were never generated
 * and the browser would silently fall back (or 404). One list, both consumers.
 *
 * Plain .mjs rather than .ts so the build script can import it directly
 * without a TypeScript step.
 */

/** [width, webpQuality] — quality rises as width falls; small images are
 *  scrutinised more per pixel. */
export const HERO_WIDTHS = [
  [640, 80],
  [960, 78],
  [1280, 76],
  [1920, 74],
  [2400, 72],
];

/**
 * Images that are not full-width heroes and need their own width ladder.
 *
 * iStock-1281536292 renders inside a `flex: 0 0 240px` column in
 * src/content/pages/services.md, so it displays about 240px wide. The source
 * is 1518x2699 and 1.26MB — the worst size-to-display ratio on the site. 480px
 * covers a 2x display.
 */
export const INLINE_OVERRIDES = {
  'iStock-1281536292.webp': [
    [480, 82],
    [720, 80],
  ],
};

/** The width ladder that applies to a given public/ filename. */
export function widthsFor(file) {
  return INLINE_OVERRIDES[file] ?? HERO_WIDTHS;
}

/** public/ path of one generated variant. */
export function variantPath(file, width) {
  return `/heroes/${file.replace(/\.webp$/i, '')}-${width}.webp`;
}

/**
 * Builds a srcset for an original public/ path such as
 * "/iStock-1048931984.webp". Returns the descriptor string plus the widest
 * variant, which is used as the plain `src` fallback.
 */
export function heroSrcset(src) {
  const file = src.replace(/^\//, '');
  const widths = widthsFor(file);
  return {
    srcset: widths.map(([w]) => `${variantPath(file, w)} ${w}w`).join(', '),
    fallback: variantPath(file, widths[widths.length - 1][0]),
    widest: widths[widths.length - 1][0],
  };
}
