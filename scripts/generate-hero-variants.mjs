/**
 * Generates responsive width variants for the large images in public/.
 *
 * Run: npm run generate:heroes   (also runs automatically via prebuild)
 *
 * WHY: every hero was a single 2400px file between 285KB and 1.26MB, served at
 * that size to every device. Core Web Vitals put LCP P99 at 4,208ms, and the
 * dashboard's debug view named these files directly. A phone needs ~800px, not
 * 2400px — that is a 75-88% saving on the byte that gates the largest paint.
 *
 * Variants land in public/heroes/<name>-<width>.webp and are referenced by
 * src/components/HeroImage.astro through a srcset. Originals stay in place:
 * they are the source of truth here, and the 2400px variant is the top of the
 * srcset for large desktop displays.
 *
 * Quality rises slightly as width falls. A small image is scrutinised more per
 * pixel, so holding quality flat makes the narrow variants look soft.
 */
import sharp from 'sharp';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { HERO_WIDTHS, widthsFor, CROP_OVERRIDES } from '../src/utils/heroImages.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PUBLIC = path.join(root, 'public');
const OUT = path.join(PUBLIC, 'heroes');
// Pre-cropped, high-resolution intermediates for the CROP_OVERRIDES images.
// Committed, and not served (src/ is not copied to dist/). Built by
// scripts/prepare-hero-masters.mjs. See that file for why.
const MASTERS = path.join(root, 'src', 'assets', 'hero-masters');

fs.mkdirSync(OUT, { recursive: true });

const sources = fs
  .readdirSync(PUBLIC)
  .filter((f) => f.toLowerCase().endsWith('.webp'))
  .sort();

let totalOriginal = 0;
let totalLargest = 0;
let totalSmallest = 0;

/**
 * Real intrinsic dimensions per source, written out for HeroImage.astro.
 * Hardcoding 2400x1600 would be wrong for several of these: iStock-1281536292
 * is 1518x2699 portrait, iStock-2251646674-Adj is 2400x1024. The <img> needs
 * its true aspect ratio so the attributes do not lie.
 */
const manifest = {};

for (const file of sources) {
  const src = path.join(PUBLIC, file);
  const base = file.replace(/\.webp$/i, '');
  const meta = await sharp(src).metadata();
  const originalKb = Math.round(fs.statSync(src).size / 1024);
  totalOriginal += originalKb;

  const widths = widthsFor(file);
  const made = [];
  const crop = CROP_OVERRIDES[file];

  // A cropped image resizes from its committed master, which is already
  // cropped and at a far higher resolution than the public/ copy. Only fall
  // back to cropping here if the master is missing.
  const master = path.join(MASTERS, `${base}.webp`);
  const hasMaster = crop && fs.existsSync(master);
  const input = hasMaster ? master : src;
  const inputMeta = hasMaster ? await sharp(master).metadata() : meta;

  let region = null;
  if (crop && !hasMaster) {
    const cropW = Math.round((meta.height ?? 0) * crop.ratio);
    region = {
      left: Math.round(((meta.width ?? 0) - cropW) / 2),
      top: 0,
      width: cropW,
      height: meta.height ?? 0,
    };
  }

  const deliveredWidth = region ? region.width : (inputMeta.width ?? 0);
  const deliveredHeight = region ? region.height : (inputMeta.height ?? 0);

  for (const [w, q] of widths) {
    // withoutEnlargement: never upscale past the source's real resolution.
    if (deliveredWidth < w && w !== widths[0][0]) continue;
    const out = path.join(OUT, `${base}-${w}.webp`);
    let pipeline = sharp(input);
    if (region) pipeline = pipeline.extract(region);
    await pipeline
      .resize({ width: w, withoutEnlargement: true })
      .webp({ quality: q, effort: 6 })
      .toFile(out);
    made.push([w, Math.round(fs.statSync(out).size / 1024)]);
  }

  if (made.length) {
    totalSmallest += made[0][1];
    totalLargest += made[made.length - 1][1];
  }

  // Record the DELIVERED dimensions, not the source's: a cropped image has a
  // different aspect ratio, and the <img> must declare what it actually is.
  manifest[file] = {
    width: deliveredWidth,
    height: deliveredHeight,
    widths: made.map(([w]) => w),
    ...(crop ? { cropped: true } : {}),
  };

  const summary = made.map(([w, kb]) => `${w}px:${kb}KB`).join('  ');
  console.log(`${file.padEnd(32)} ${String(originalKb).padStart(5)}KB -> ${summary}`);
}

console.log(
  `\n${sources.length} sources. Originals ${totalOriginal}KB total; ` +
    `narrowest variants ${totalSmallest}KB (${Math.round(100 - (totalSmallest / totalOriginal) * 100)}% smaller), ` +
    `widest ${totalLargest}KB.`,
);
const manifestPath = path.join(root, 'src', 'data', 'heroManifest.json');
fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + String.fromCharCode(10));

console.log(`Variants written to public/heroes/.`);
console.log(`Manifest written to src/data/heroManifest.json.`);
