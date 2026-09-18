/**
 * Builds committed "masters" for the images that need a pre-crop.
 *
 * Run: npm run prepare:masters   (locally, only when an original changes)
 *
 * WHY THIS EXISTS
 *
 * source-images/heroes/ holds the full-resolution originals (116MB) and is
 * gitignored, so the Cloudflare build never sees it. But the cropped images
 * genuinely need that resolution: iStock-2206368893's public copy is
 * 2400x1600, and because it renders in a tall narrow column where object-fit
 * cover fills the HEIGHT, 1600px of height caps a crisp render at an 800px
 * box. The original is 3864x2576, which reaches 1288px.
 *
 * So the crop is done once here, from the original, and the result is
 * committed to src/assets/hero-masters/ — small enough to version, high
 * enough resolution to matter, and present in CI. src/ is not copied to
 * dist/, so masters are never served; generate-hero-variants.mjs resizes them
 * into the public/heroes/ variants that are.
 *
 * Falls back to the public/ copy with a loud warning when an original is
 * missing, so a fresh clone still produces a working (if softer) result.
 */
import sharp from 'sharp';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { CROP_OVERRIDES } from '../src/utils/heroImages.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ORIGINALS = path.join(root, 'source-images', 'heroes');
const PUBLIC = path.join(root, 'public');
const OUT = path.join(root, 'src', 'assets', 'hero-masters');

fs.mkdirSync(OUT, { recursive: true });

let warned = false;

for (const [file, { ratio }] of Object.entries(CROP_OVERRIDES)) {
  const base = file.replace(/\.webp$/i, '');

  // Prefer the full-resolution original; fall back to the public copy.
  const original = path.join(ORIGINALS, `${base}.jpg`);
  const fallback = path.join(PUBLIC, file);
  const src = fs.existsSync(original) ? original : fallback;

  if (src === fallback) {
    warned = true;
    console.warn(
      `  WARNING  ${base}.jpg not found in source-images/heroes/ — ` +
        `falling back to the lower-resolution public copy.`,
    );
  }

  const meta = await sharp(src).metadata();
  const cropW = Math.round((meta.height ?? 0) * ratio);
  const out = path.join(OUT, `${base}.webp`);

  await sharp(src)
    .extract({
      left: Math.round(((meta.width ?? 0) - cropW) / 2),
      top: 0,
      width: cropW,
      height: meta.height ?? 0,
    })
    // q92 because this is an intermediate: every delivered variant is resized
    // down from it, and compression artefacts introduced here would be baked
    // into all of them.
    .webp({ quality: 92, effort: 6 })
    .toFile(out);

  const kb = Math.round(fs.statSync(out).size / 1024);
  console.log(
    `  ${base.padEnd(26)} ${meta.width}x${meta.height} -> ${cropW}x${meta.height}  ${kb}KB` +
      `   (crisp to a ${Math.round((meta.height ?? 0) / 2)}px-tall box @2x)`,
  );
}

console.log(`\nMasters written to src/assets/hero-masters/. Commit them.`);
if (warned) {
  console.warn('Some masters used a fallback source — see warnings above.');
}
