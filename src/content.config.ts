import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * Articles: one markdown file = one post. Written by hand or by the
 * Drive sync pipeline (sync/pull.py).
 *
 * Multilingual model: each language version is its own file. The
 * ORIGINAL carries `translations: [slugs]`; each TRANSLATION carries
 * `originalLang` + `translationOf`. No assumption that every article
 * exists in every language.
 */
const articles = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/articles' }),
  schema: z.object({
    title: z.string(),
    description: z.string().default(''),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    /** language of THIS file */
    lang: z.string().default('en'),
    dir: z.enum(['ltr', 'rtl']).optional(),
    /** A–J content taxonomy (see /about): Research, Documentation, Translation,
     *  Commentary, Project report, Case study, Interview, Archival, Resource, Announcement */
    category: z.string().optional(),
    tags: z.array(z.string()).default([]),
    /** language versions of this article (slugs, this one excluded) */
    translations: z.array(z.string()).default([]),
    /** set on translations: language of the original */
    originalLang: z.string().optional(),
    /** set on translations: slug of the original */
    translationOf: z.string().optional(),
    /** Indus-Kohistani, Shina, Urdu, Arabic, Persian, English */
    relatedLanguages: z.array(z.string()).default([]),
    relatedProjects: z.array(z.string()).default([]),
    references: z.array(z.object({
      label: z.string(),
      url: z.string().optional(),
      doi: z.string().optional(),
    })).default([]),
    doi: z.string().optional(),
    cover: z.string().optional(),
    coverCredit: z.string().optional(),
    imageCredits: z.array(z.string()).optional(),
    featured: z.boolean().default(false),
    status: z.enum(['draft', 'published']).default('draft'),
    /* SEO */
    metaTitle: z.string().optional(),
    metaDescription: z.string().optional(),
    /* provenance from the Drive pipeline */
    driveFile: z.string().optional(),
    syncedAt: z.string().optional(),
  }),
});

/** Chapters: markdown files inside a book folder (books stay file-driven). */
const chapters = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/books' }),
  schema: z.object({
    book: z.string(),
    title: z.string(),
    order: z.number().default(0),
    lang: z.string().default('en'),
    status: z.enum(['draft', 'published']).default('published'),
  }),
});

export const collections = { articles, chapters };
