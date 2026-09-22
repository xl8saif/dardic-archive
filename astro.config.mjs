// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import vercel from '@astrojs/vercel/serverless';

// On GitHub Pages this becomes https://<user>.github.io/<repo>/
const site = process.env.SITE_URL || 'http://localhost:4321';

export default defineConfig({
  site,
  output: 'server',
  adapter: vercel(),
  integrations: [sitemap()],
});
