import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const articles = (await getCollection('articles', ({ data }) => data.status === 'published'))
    .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

  return rss({
    title: 'The Dardic Archive — Saif Ullah',
    description: 'Language research, documentation and preservation (Indus-Kohistani, Shina) plus translation and localization work — in English, Urdu, Arabic, Indus-Kohistani and Shina.',
    site: context.site!,
    items: articles.map((a) => ({
      title: a.data.title,
      description: a.data.description,
      pubDate: a.data.pubDate,
      link: `/articles/${a.id}/`,
      lang: a.data.lang,
    })),
    customData: '<language>en</language>',
  });
}
