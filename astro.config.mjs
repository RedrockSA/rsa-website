// @ts-check
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  site: 'https://redrocksa.com',
  integrations: [
    tailwind({
      configFile: './tailwind.config.mjs',
      applyBaseStyles: false,
    }),
  ],
});
