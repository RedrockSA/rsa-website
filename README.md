# Astro Starter Kit: Minimal

```sh
npm create astro@latest -- --template minimal
```

> 🧑‍🚀 **Seasoned astronaut?** Delete this file. Have fun!

## 🚀 Project Structure

Inside of your Astro project, you'll see the following folders and files:

```text
/
├── public/
├── src/
│   └── pages/
│       └── index.astro
└── package.json
```

Astro looks for `.astro` or `.md` files in the `src/pages/` directory. Each page is exposed as a route based on its file name.

There's nothing special about `src/components/`, but that's where we like to put any Astro/React/Vue/Svelte/Preact components.

Any static assets, like images, can be placed in the `public/` directory.

## 🧞 Commands

All commands are run from the root of the project, from a terminal:

| Command                   | Action                                           |
| :------------------------ | :----------------------------------------------- |
| `npm install`             | Installs dependencies                            |
| `npm run dev`             | Starts local dev server at `localhost:4321`      |
| `npm run build`           | Build your production site to `./dist/`          |
| `npm run preview`         | Preview your build locally, before deploying     |
| `npm run astro ...`       | Run CLI commands like `astro add`, `astro check` |
| `npm run astro -- --help` | Get help using the Astro CLI                     |

## 👀 Want to learn more?

Feel free to check [our documentation](https://docs.astro.build) or jump into our [Discord server](https://astro.build/chat).

---

## SEO, icons, and analytics

Reference for the pieces that are easy to forget between edits.

### Generated assets

| Command | Produces |
| :------ | :------- |
| `npm run generate:favicons` | The icon set in `public/`, from `public/FaviconVariant.png` |
| `npm run generate:og` | `public/og-default.png`, the 1200x630 social share card |

Both are committed to the repo, so they only need rerunning when the source
art changes.

### Trailing slashes

`astro.config.mjs` sets `trailingSlash: 'always'`, because the host serves
`/contact/` with a 200 and redirects `/contact`. **Internal links must end in
a slash** (`href="/contact/"`), or every click costs a redirect hop. Asset
paths like `/RSA_color.png` must not.

Side effect: the dev server 404s on a bare URL typed by hand. Add the slash.

### AI crawlers

`public/robots.txt` currently allows everything, so the site can be cited by
ChatGPT, Claude, Perplexity, and Google's AI surfaces. To opt out, append:

```
User-agent: GPTBot
Disallow: /

User-agent: OAI-SearchBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: PerplexityBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: CCBot
Disallow: /
```

Blocking `Google-Extended` affects only Gemini and AI training use. It does
**not** remove the site from regular Google Search results.

Keep `robots.txt` ASCII-only. It is served as `text/plain` with no charset, so
browsers fall back to Latin-1 and render UTF-8 punctuation (em dashes, curly
quotes) as mojibake.

### Analytics

`src/components/Analytics.astro` renders a beacon only when
`PUBLIC_CF_BEACON_TOKEN` is set. If the beacon is instead enabled from the
hosting dashboard, leave that variable unset — otherwise it loads twice and
page views double-count.

### Sitemap

`@astrojs/sitemap` is pinned to **3.2.1**. Version 3.7.x calls an Astro 5+
build hook and fails on Astro 4 with `Cannot read properties of undefined
(reading 'reduce')`. Revisit the pin only when upgrading Astro itself.

The build emits `sitemap-index.xml` (a pointer) and `sitemap-0.xml` (the 128
actual URLs). Submit the index to Search Console; it is the standard format
and search engines follow it to the second file.

### Search engine monitoring

The site is registered with **Google Search Console** (a Domain property for
`redrocksa.com`) and **Bing Webmaster Tools** (imported from Search Console;
sign in with the `redrocksa.com` Microsoft 365 account). Google was verified by
a DNS TXT record at the Cloudflare zone root. **Never delete that record**, or
the property un-verifies and its history is lost. The sitemap was submitted as
the full URL `https://redrocksa.com/sitemap-index.xml`; a Domain property
rejects a bare path.

**Check-ins.** Next one is mid-November 2026, then mid-December (Core Web
Vitals needs 90 days of real-user data before Google shows anything).

| Where | What to look at |
| :---- | :-------------- |
| Search Console, Performance | Clicks and impressions (28 days), top queries and pages |
| Search Console, Indexing, Pages | Indexed vs not indexed, and the reason for each not-indexed group |
| Search Console, Sitemaps | Status Success, discovered page count matches the build |
| Search Console, Core Web Vitals, Breadcrumbs, Security and Manual Actions | New data, any errors, anything other than "No issues" |
| Bing, Search Performance | Clicks and impressions |
| Bing, AI Performance (beta) | Citations, and whether Grounding Queries and Pages have filled in |
| Bing, Recommendations | Anything new beyond the three known ones below |

**Baseline, 2026-10-15** (about four weeks after registration; saved with
later months in `data/metrics/monthly.csv`, which is gitignored and exists on
one machine only):

- Google: 37 clicks, 866 impressions, 208 pages indexed, 50 not, 0 external links
- Bing: 3 clicks, 44 impressions, 19 AI citations over three months

**Known and fine, do not chase:**

- *Page with redirect* (about 35 URLs): old or variant URLs (no trailing slash,
  `www`, `http`) that redirect correctly to the canonical page.
- *Duplicate without user-selected canonical*: the `?primary=` reading-list
  filter URLs. They carry the right canonical and were validated on 2026-10-15.
- *Crawled, currently not indexed*: `/rss.xml` (a feed, not a page) and stale
  pre-launch crawls of `/career-path` and `/services/capital-advisory/`; live
  tests pass.
- Breadcrumb markup exists only on some pages (team, book pages, capital
  advisory). Minor; adding it elsewhere is optional.
- Bing's "Set up IndexNow" banner: deliberately skipped. The site changes
  rarely and Bing already crawls on its own. Revisit if Bing or its AI
  citations become a meaningful channel.
- Bing's "not enough inbound links" and Google's 0 external links: only fixed
  by other sites linking here (LinkedIn, directories, press), not by code.

**Meta descriptions** feed `meta description`, `og:description` and
`twitter:description` (see `BaseLayout.astro`), so they also drive the link
preview cards in LinkedIn and Teams. Aim for 150-160 characters. Core pages
were rewritten to that length on 2026-10-15; the 109 book pages average about
97 characters and Bing has not flagged them.
