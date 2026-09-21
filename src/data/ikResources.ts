/**
 * Indus-Kohistani Translation & Written Resources
 * ==================================================================
 * A research/documentation archive of written-resource production in
 * Indus-Kohistani: translation, literary translation, religious and
 * educational translation, adaptation, terminology, grammar/language
 * resources, children's material, publication and orthographic work.
 *
 * DATA SOURCE: `ik-resources.json` (same folder) — the authoritative
 * dataset, imported in one batch. NOTHING is invented here: the shipped
 * JSON contains an empty `works` array and the archive renders its
 * in-preparation state until records arrive.
 *
 * One work may carry MULTIPLE classifications (translation + publication
 * + educational resource…). Authorship roles are preserved exactly as
 * supplied — the translator is never auto-promoted to author.
 */

export type WorkKind =
  | 'translation'
  | 'adaptation'
  | 'original'
  | 'educational-resource'
  | 'language-resource'
  | 'publication';

export const WORK_KIND_LABELS: Record<WorkKind, string> = {
  'translation': 'Translation',
  'adaptation': 'Adaptation',
  'original': 'Original Indus-Kohistani work',
  'educational-resource': 'Educational resource',
  'language-resource': 'Language resource',
  'publication': 'Publication',
};

export const PUBLICATION_STATUSES = [
  'Published',
  'Digitally published',
  'Unpublished',
  'In progress',
  'Archived',
  'Private/internal',
] as const;
export type PublicationStatus = (typeof PUBLICATION_STATUSES)[number];

/** A record may set privacy on attached media, independent of the work status. */
export type MediaVisibility = 'public' | 'private';

export interface IkPerson {
  name: string;
  /** role exactly as supplied, e.g. "translator", "co-translator", "linguistic reviewer" */
  role?: string;
}

export interface IkResource {
  /** unique, URL-stable slug — required */
  slug: string;
  title: string;
  /** title language code — drives RTL/font rendering of the title */
  titleLang?: string;
  translatedTitle?: string;
  originalTitle?: string;
  authors?: IkPerson[];
  translators?: IkPerson[];
  editors?: IkPerson[];
  reviewers?: IkPerson[];
  contributors?: IkPerson[];

  originalLanguage?: string;
  targetLanguage?: string;
  publicationYear?: number;
  translationYear?: number;
  publisher?: string;
  edition?: string;
  status: PublicationStatus;
  isbn?: string;
  doi?: string;
  externalUrl?: string;
  externalUrlLabel?: string;

  /** dedicated dialect field — preserved exactly, never inferred */
  dialect?: string;
  script?: string;
  orthography?: string;
  terminologyNotes?: string;
  linguisticReview?: string;
  languageSignificance?: string;

  /** one or more of WorkKind — a translation may also be a publication */
  kinds: WorkKind[];
  subject?: string;
  researchArea?: string;
  relatedProject?: string;
  relatedOrganisation?: string;
  relatedPublication?: string;

  shortDescription?: string;
  translatorsNote?: string;
  documentationNote?: string;
  preservationSignificance?: string;
  methodology?: string;

  cover?: { src: string; alt: string; caption?: string; credit?: string };
  manuscriptPages?: { src: string; alt: string; visibility: MediaVisibility }[];
  photographs?: { src: string; alt: string; caption?: string }[];
  pdfUrl?: string;
  pdfLabel?: string;
  /** media attachment visibility — private files are never linked publicly */
  pdfVisibility?: MediaVisibility;
  relatedAudioVideo?: { url: string; label: string }[];
  references?: { label: string; url?: string; doi?: string }[];
  sourceMaterial?: string;

  relatedArticles?: string[];
  featured?: boolean;
}

import worksJson from './ik-resources.json';

export const IK_RESOURCES: IkResource[] = (worksJson as { works: IkResource[] }).works;

/* ---------------------------------------------------------------- */
/* helpers                                                            */
/* ---------------------------------------------------------------- */

export function getIkResource(slug: string): IkResource | undefined {
  return IK_RESOURCES.find((w) => w.slug === slug);
}

export const IK_RESOURCE_CATEGORIES: { id: string; label: string; kinds: WorkKind[] }[] = [
  { id: 'all', label: 'All works', kinds: ['translation', 'adaptation', 'original', 'educational-resource', 'language-resource', 'publication'] },
  { id: 'book-translations', label: 'Book Translations', kinds: ['translation'] },
  { id: 'literary', label: 'Literary Works', kinds: ['translation', 'adaptation', 'original'] },
  { id: 'educational', label: 'Educational Resources', kinds: ['educational-resource'] },
  { id: 'language-resources', label: 'Language/Grammar Resources', kinds: ['language-resource'] },
  { id: 'other', label: 'Other Written Resources', kinds: ['publication', 'adaptation', 'translation', 'original'] },
];

export function workKindLabel(kinds: WorkKind[] | undefined): string {
  if (!kinds || kinds.length === 0) return 'Work';
  return kinds.map((k) => WORK_KIND_LABELS[k]).join(' · ');
}

/** language-code → { dir, native } for record-level rendering */
const LANG_META: Record<string, { dir: 'ltr' | 'rtl'; native: string }> = {
  en: { dir: 'ltr', native: 'English' },
  ur: { dir: 'rtl', native: 'اردو' },
  ar: { dir: 'rtl', native: 'العربية' },
  mvb: { dir: 'rtl', native: 'Indus-Kohistani' },
  scl: { dir: 'rtl', native: 'Shina' },
};

export function langMeta(code?: string) {
  return LANG_META[code ?? 'en'] ?? LANG_META.en;
}

export function hasValue(v: unknown): boolean {
  if (v === undefined || v === null) return false;
  if (typeof v === 'string') return v.trim().length > 0;
  if (Array.isArray(v)) return v.length > 0;
  if (typeof v === 'object') return Object.keys(v as object).length > 0;
  return true;
}
