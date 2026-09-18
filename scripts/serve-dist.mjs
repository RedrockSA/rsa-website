/**
 * Local preview server for ./dist that mirrors how the site is actually served
 * in production.
 *
 * Run: npm run serve
 *
 * Two behaviours the simpler options get wrong:
 *
 *  - `astro preview` applies `trailingSlash: 'always'` to generated routes, so
 *    it 404s /rss.xml and /sitemap-index.xml even though both files exist.
 *  - `python -m http.server` has no concept of a 404 page, so an unknown URL
 *    returns its own plain-text error instead of dist/404.html.
 *
 * This serves flat files by exact path, redirects bare directory paths to the
 * trailing-slash form (308, as the host does), and falls back to dist/404.html
 * with a real 404 status.
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'dist');
const port = Number(process.argv[2]) || 8080;

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.xml': 'application/xml; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.webmanifest': 'application/manifest+json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
};

const isFile = (p) => fs.existsSync(p) && fs.statSync(p).isFile();

http
  .createServer((req, res) => {
    const url = decodeURIComponent((req.url || '/').split('?')[0]);
    const target = path.join(root, url);

    // An exact file wins: /rss.xml, /og-default.png, /sitemap-index.xml.
    if (isFile(target)) return send(res, target, 200);

    // A directory serves its index, but only at the trailing-slash URL.
    if (url.endsWith('/') && isFile(path.join(target, 'index.html'))) {
      return send(res, path.join(target, 'index.html'), 200);
    }
    if (!url.endsWith('/') && isFile(path.join(target, 'index.html'))) {
      res.writeHead(308, { Location: url + '/' });
      return res.end();
    }

    // Everything else: the real 404 page, with a real 404 status.
    const notFound = path.join(root, '404.html');
    if (isFile(notFound)) return send(res, notFound, 404);
    res.writeHead(404, { 'content-type': 'text/plain' });
    res.end('404');
  })
  .listen(port, '127.0.0.1', () => {
    console.log(`\n  Serving ./dist at http://localhost:${port}`);
    console.log('  Mirrors production: trailing-slash redirects and a real 404 page.');
    console.log('  Ctrl+C to stop.\n');
  });

function send(res, file, status) {
  const type = TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream';
  res.writeHead(status, { 'content-type': type });
  fs.createReadStream(file).pipe(res);
}
