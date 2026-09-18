/**
 * Generates public/og-default.png — the 1200x630 card that LinkedIn, Facebook,
 * Slack and iMessage show when someone shares a redrocksa.com link.
 *
 * Run: npm run generate:og
 *
 * Why a dedicated file rather than reusing a hero image: the heroes in public/
 * are 300KB-1.3MB and the wrong aspect ratio, so they crop badly and load
 * slowly in a scraper. 1200x630 is the ratio every major platform expects.
 *
 * Social platforms cache scraped previews aggressively, so if you change this
 * image you may need to re-scrape the URL in LinkedIn's Post Inspector or
 * Facebook's Sharing Debugger before the new one appears.
 */
import sharp from 'sharp';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(root, 'public', 'og-default.png');

const W = 1200;
const H = 630;
const BRAND = '#C80026';

const background = await sharp(path.join(root, 'public', 'RedrockCanyon.webp'))
  .resize(W, H, { fit: 'cover', position: 'centre' })
  .modulate({ brightness: 0.62 }) // darkened so the white logo and rule read clearly
  .toBuffer();

const logo = await sharp(path.join(root, 'public', 'RSA_white.png'))
  .resize({ width: 620 })
  .toBuffer();
const logoMeta = await sharp(logo).metadata();

// A brand-red rule under the logo, echoing the red bar on the homepage hero.
const rule = await sharp({
  create: {
    width: 620,
    height: 6,
    channels: 4,
    background: BRAND,
  },
})
  .png()
  .toBuffer();

const logoTop = Math.round((H - (logoMeta.height ?? 230)) / 2) - 30;

await sharp(background)
  .composite([
    { input: logo, top: logoTop, left: Math.round((W - 620) / 2) },
    { input: rule, top: logoTop + (logoMeta.height ?? 230) + 34, left: Math.round((W - 620) / 2) },
  ])
  .png({ quality: 90, compressionLevel: 9 })
  .toFile(OUT);

const { size } = await sharp(OUT).metadata();
console.log(`og-default.png written: ${W}x${H}${size ? `, ${Math.round(size / 1024)}KB` : ''}`);
