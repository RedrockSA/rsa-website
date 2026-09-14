#!/usr/bin/env node
/**
 * One-off prep: optimise the book covers for the web.
 *
 * Masters live in source-covers/ and total ~33 MB across 110 PNGs - too heavy
 * to serve raw. This writes a WebP set capped at MAX_W wide into
 * public/books/covers/, which is what actually ships.
 *
 * Never upscales: the median source cover is only ~330px wide, so asking for
 * more than the source has would just inflate bytes for no detail. Cards are
 * designed around ~180px display width, so MAX_W gives a 2x retina image for
 * the covers that can support it.
 *
 * Re-run after adding covers to the source folder.
 *   node scripts/prepare-covers.mjs [sourceDir]
 */
import { readdirSync, mkdirSync, existsSync, statSync } from 'node:fs';
import { join, parse } from 'node:path';
import sharp from 'sharp';

const SRC = process.argv[2] || 'source-covers';
const OUT = 'public/books/covers';
const MAX_W = 400;
const QUALITY = 82;

if (!existsSync(SRC)) {
  console.error(`[prepare-covers] source not found: ${SRC}`);
  process.exit(1);
}
mkdirSync(OUT, { recursive: true });

const files = readdirSync(SRC).filter((f) => /\.(png|jpe?g)$/i.test(f));
let srcBytes = 0;
let outBytes = 0;
let upscaleSkipped = 0;

for (const file of files) {
  const from = join(SRC, file);
  const to = join(OUT, `${parse(file).name}.webp`);
  srcBytes += statSync(from).size;

  const meta = await sharp(from).metadata();
  const width = Math.min(meta.width ?? MAX_W, MAX_W);
  if ((meta.width ?? 0) < MAX_W) upscaleSkipped++;

  await sharp(from)
    .resize({ width, withoutEnlargement: true })
    .webp({ quality: QUALITY })
    .toFile(to);

  outBytes += statSync(to).size;
}

const mb = (n) => (n / 1e6).toFixed(1);
console.log(`[prepare-covers] ${files.length} covers -> ${OUT}`);
console.log(`  ${mb(srcBytes)} MB PNG -> ${mb(outBytes)} MB WebP ` +
  `(${Math.round((1 - outBytes / srcBytes) * 100)}% smaller)`);
console.log(`  ${upscaleSkipped} were narrower than ${MAX_W}px and kept at source width`);
