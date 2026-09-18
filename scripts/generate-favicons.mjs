/**
 * Generates the full favicon set from public/FaviconVariant.png.
 *
 * Run: npm run generate:favicons
 *
 * Why a set rather than one 32x32: browsers scale the favicon up for bookmark
 * bars, high-DPI tab strips and mobile home screens, so a lone 32x32 looks
 * soft in every one of those places. Each size here is rendered from the
 * 1254x1254 source rather than upscaled from a small file.
 *
 * Two details that matter:
 *  - The source has wide transparent padding. Trimming it and re-padding to a
 *    consistent margin makes the mark noticeably larger at 32x32, which is
 *    where legibility is tightest.
 *  - iOS ignores transparency on apple-touch-icon and composites the image
 *    onto black, so that one is flattened onto white deliberately.
 */
import sharp from 'sharp';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SRC = path.join(root, 'public', 'FaviconVariant.png');
const pub = (name) => path.join(root, 'public', name);

// Trim the transparent border so the mark itself fills the frame.
const trimmed = await sharp(SRC).trim().toBuffer();
const { width = 0, height = 0 } = await sharp(trimmed).metadata();

// Re-pad to a square, leaving a small even margin (8% of the long edge) so the
// mark does not touch the icon's edges.
const side = Math.max(width, height);
const margin = Math.round(side * 0.08);
const canvas = side + margin * 2;

const square = await sharp({
  create: {
    width: canvas,
    height: canvas,
    channels: 4,
    background: { r: 0, g: 0, b: 0, alpha: 0 },
  },
})
  .composite([
    {
      input: trimmed,
      top: Math.round((canvas - height) / 2),
      left: Math.round((canvas - width) / 2),
    },
  ])
  .png()
  .toBuffer();

/** Transparent icons, rendered straight from the square master. */
const transparent = [
  ['RSA_favicon.png', 32], // existing filename — kept so nothing else has to change
  ['favicon-16.png', 16],
  ['favicon-32.png', 32],
  ['favicon-48.png', 48],
  ['icon-192.png', 192],
  ['icon-512.png', 512],
];

for (const [name, size] of transparent) {
  await sharp(square).resize(size, size, { kernel: 'lanczos3' }).png().toFile(pub(name));
  console.log(`  ${name.padEnd(20)} ${size}x${size}`);
}

// apple-touch-icon: flattened onto white, and padded a little more generously
// because iOS rounds the corners and can clip a mark that sits too close.
await sharp(square)
  .resize(160, 160, { kernel: 'lanczos3' })
  .extend({
    top: 10,
    bottom: 10,
    left: 10,
    right: 10,
    background: { r: 255, g: 255, b: 255, alpha: 1 },
  })
  .flatten({ background: { r: 255, g: 255, b: 255 } })
  .png()
  .toFile(pub('apple-touch-icon.png'));
console.log(`  ${'apple-touch-icon.png'.padEnd(20)} 180x180 (flattened on white)`);

console.log('\nFavicon set written to public/.');
