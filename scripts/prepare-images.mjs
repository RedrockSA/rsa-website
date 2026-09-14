#!/usr/bin/env node
/**
 * Optimise the site's photographic images.
 *
 * The originals are iStock downloads at full resolution - up to 14810px wide,
 * 146 megapixels, 17 MB each - for heroes that never render wider than a
 * viewport. This resizes them to MAX_W and converts to WebP, then moves the
 * originals into source-images/ so they stay available but stop shipping.
 *
 * MAX_W is 2400: enough for a full-bleed hero on a 1440p display, and for a
 * 1200px-wide layout at 2x. Beyond that a background image gains nothing a
 * viewer can see.
 *
 * Logos are left alone - they are already small, and PNG suits flat artwork
 * with transparency better than WebP's photographic tuning.
 *
 *   node scripts/prepare-images.mjs [--dry]
 */
import { readdirSync, statSync, mkdirSync, renameSync, existsSync } from 'node:fs';
import { join, parse } from 'node:path';
import sharp from 'sharp';

const SRC = 'public';
const KEEP = 'source-images/heroes';
const MAX_W = 2400;
const QUALITY = 82;
const DRY = process.argv.includes('--dry');

// Flat artwork: leave as-is.
const SKIP = new Set(['RSA_white.png', 'RSA_color.png', 'RSA_favicon.png']);

const files = readdirSync(SRC).filter(
  (f) => /\.(jpe?g|png)$/i.test(f) && !SKIP.has(f)
);

mkdirSync(KEEP, { recursive: true });

let before = 0;
let after = 0;
const renames = [];

for (const file of files) {
  const from = join(SRC, file);
  const meta = await sharp(from, { limitInputPixels: false }).metadata();
  const out = join(SRC, `${parse(file).name}.webp`);
  const srcBytes = statSync(from).size;
  before += srcBytes;

  if (DRY) {
    console.log(`  ${file}  ${meta.width}x${meta.height}  ${(srcBytes / 1e6).toFixed(1)}MB -> ${parse(out).base}`);
    continue;
  }

  await sharp(from, { limitInputPixels: false })
    .resize({ width: Math.min(meta.width ?? MAX_W, MAX_W), withoutEnlargement: true })
    .webp({ quality: QUALITY })
    .toFile(out);

  const outBytes = statSync(out).size;
  after += outBytes;
  renames.push([file, parse(out).base]);

  // Keep the original outside public/ so it no longer ships.
  renameSync(from, join(KEEP, file));

  console.log(
    `  ${file.padEnd(30)} ${String(meta.width).padStart(5)}px -> ${MAX_W}px   ` +
    `${(srcBytes / 1e6).toFixed(1)}MB -> ${(outBytes / 1e6).toFixed(2)}MB`
  );
}

if (!DRY) {
  const mb = (n) => (n / 1e6).toFixed(1);
  console.log(`\n  ${files.length} images: ${mb(before)} MB -> ${mb(after)} MB ` +
    `(${Math.round((1 - after / before) * 100)}% smaller)`);
  console.log('  originals moved to ' + KEEP);
  console.log('\n  rename map for source references:');
  for (const [a, b] of renames) console.log(`    ${a} -> ${b}`);
}
