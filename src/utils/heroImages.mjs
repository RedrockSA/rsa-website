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
 * src/content/pages/services.md. The column is only 240px wide but stretches
 * to the height of the prose beside it — roughly 630-900px.
 *
 * That combination is a trap. `object-fit: cover` on a box TALLER than the
 * image's aspect ratio scales the image to fill the HEIGHT and crops the
 * sides, so the resolution actually needed is displayHeight * sourceRatio,
 * not the 240px layout width. A first attempt served 480px here and the
 * browser upscaled it about 2.1x, which was visibly soft.
 */
export const INLINE_OVERRIDES = {
  'iStock-1281536292.webp': [
    [280, 86],
    [420, 86],
    [560, 86],
  ],
};

/**
 * Sources pre-cropped to a target aspect ratio before resizing.
 *
 * Cropping first is what makes the small widths above sufficient. The source
 * is 0.562 wide-to-tall; the slot it renders in is about 0.31. Roughly 45% of
 * every pixel we shipped was being thrown away by the CSS crop. Cropping to
 * 0.30 up front means the delivered image nearly matches the box, so `sizes`
 * describes the need honestly again and 560px covers a 934px-tall box at 2x
 * for 400KB — against 639KB for an uncropped 1080px version.
 *
 * 0.30 is deliberately a little narrower than the measured box: if the prose
 * beside it grows, `cover` crops the sides slightly rather than running out
 * of pixels.
 */
export const CROP_OVERRIDES = {
  'iStock-1281536292.webp': { ratio: 0.3 },
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
