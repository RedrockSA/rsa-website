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
