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
actual URLs, 131 as of November 2026). Submit the index to Search Console; it is the standard format
and search engines follow it to the second file.

### Search engine monitoring

The site is registered with **Google Search Console** (a Domain property for
`redrocksa.com`) and **Bing Webmaster Tools** (imported from Search Console;
sign in with the `redrocksa.com` Microsoft 365 account). Google was verified by
a DNS TXT record at the Cloudflare zone root. **Never delete that record**, or
the property un-verifies and its history is lost. The sitemap was submitted as
the full URL `https://redrocksa.com/sitemap-index.xml`; a Domain property
rejects a bare path.

**Check-ins.** Done 2026-10-15 and 2026-11-23. Next is mid-December. Core Web
Vitals still showed "not enough data" on 2026-11-23 (the site gets only about
25 Google impressions a day), so expect it to stay blank for a while.

**Getting the data.** For clean month-by-month figures, export a custom date
range of daily data rather than the default 28 days: Search Console,
Performance, Export (Chart.csv has one row per day), and Bing, Search
Performance and AI Performance, Export. Sum by calendar month so months are
comparable. Indexing, Pages exports as .xlsx and the Links report as .xlsx;
Sitemaps has no export, so screenshot it.

| Where | What to look at |
| :---- | :-------------- |
| Search Console, Performance | Clicks and impressions (28 days), top queries and pages |
| Search Console, Indexing, Pages | Indexed vs not indexed, and the reason for each not-indexed group |
| Search Console, Sitemaps | Status Success, discovered page count matches the build |
| Search Console, Core Web Vitals, Breadcrumbs, Security and Manual Actions | New data, any errors, anything other than "No issues" |
| Bing, Search Performance | Clicks and impressions |
| Bing, AI Performance (beta) | Citations, and whether Grounding Queries and Pages have filled in |
| Bing, Recommendations | Anything new beyond the three known ones below |

**Numbers by calendar month** (saved in `data/metrics/monthly.csv`, which is
gitignored and exists on one machine only; registration was 2026-09-17, so
September covers about two weeks and November is partial, to 11/21):

| Month | Google clicks | Google impressions | Indexed / not | Bing clicks | Bing impressions | Bing AI citations |
| :---- | ---: | ---: | :---: | ---: | ---: | ---: |
| Sep (9/16-9/30) | 25 | 606 | - | 2 | 12 | 5 |
| Oct | 29 | 664 | 208 / 50 | 3 | 106 | 68 |
| Nov (to 11/21) | 28 | 515 | 203 / 61 | 2 | 174 | 57 |

Also as of 2026-11-23: sitemap 131 URLs read OK, 1 external link (the
LinkedIn company page), breadcrumbs 0 invalid / 2 valid, no manual actions or
security issues. Almost all clicks are branded ("redrock strategic advisors"
is position 1); non-brand queries such as "strategic advisory investment
banking" sit around position 87. Bing AI citations are spiky (a few days with
dozens, most with none). Earlier figures quoted in this section (37 / 866 and
3 / 44) were rolling windows, not calendar months, and are not comparable.

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
- *Redirect error* on `/career-path`: a stale 2026-10-15 crawl. The live URL
  is a clean 308 to `/career-path/`. Validate the fix in Search Console if it
  lingers.
- *Not found (404)* on `/about/`: caused by breadcrumb markup that named
  `/about/` as the parent. There is no such page, so the About Us crumb now
  points at `/about/our-focus/` (fixed 2026-11-23). Validate the fix; it should
  clear on recrawl. If a 404 or redirect error appears for any other URL, test
  it against the live site first.
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
