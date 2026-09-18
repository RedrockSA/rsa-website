/**
 * RSS feed for the Newsroom, served at /rss.xml and linked from every page's
 * <head> in BaseLayout.
 *
 * Item links must be absolute and must match the canonical (trailing-slash)
 * form, or subscribers and crawlers follow a redirect on every item.
 *
 * Note: item GUIDs derive from the slug, so renaming a newsroom file after
 * publication makes existing subscribers see that item a second time.
 */
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { SITE_NAME } from '../utils/seo';

export async function GET(context) {
  const news = await getCollection('news');

  const items = news
    .sort((a, b) => new Date(b.data.date) - new Date(a.data.date))
    .map((article) => ({
      title: article.data.title,
      description: article.data.description,
      // Explicit time so the date is read as local rather than UTC midnight,
      // matching how the newsroom pages render it.
      pubDate: new Date(`${article.data.date}T00:00:00`),
      link: `/about/newsroom/${article.slug}/`,
    }));

  return rss({
    title: `${SITE_NAME} — Newsroom`,
    description: 'Company news and events from Redrock Strategic Advisors.',
    site: context.site,
    items,
    customData: '<language>en-us</language>',
  });
}
