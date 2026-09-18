// @ts-check
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://redrocksa.com',

  // Cloudflare Pages serves this site's directory-style URLs WITH a trailing
  // slash and 308-redirects the bare form (/contact -> /contact/). Declaring
  // that here rather than leaving it on the default 'ignore' makes Astro, the
  // sitemap and the canonical tag all agree on the same URL form, so search
  // engines see one address per page instead of a redirect chain.
  //
  // Consequence: internal hrefs must carry the trailing slash too, or the dev
  // server 404s on them. See src/components/nav/navData.ts and friends.
  trailingSlash: 'always',

  integrations: [
    tailwind({
      configFile: './tailwind.config.mjs',
      applyBaseStyles: false,
    }),
    sitemap({
      // The 404 route would otherwise be listed as a real page.
      filter: (page) => !page.includes('/404'),
    }),
  ],
});
