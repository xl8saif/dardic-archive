/**
 * Indus-Kohistani Book Translations
 * ------------------------------------------------------------------
 * A dedicated record of book-length translation work INTO Indus-Kohistani,
 * part of the language documentation / preservation portfolio (not a
 * commercial localization category).
 *
 * VERIFIED BASIS (project record):
 *  - The translator is Saif Ullah.
 *  - Target language: Indus-Kohistani; established orthography uses the
 *    additional Arabic-script characters documented on this site
 *    (ڇ څ ݜ ڙ ݨ) and is rendered in Scheherazade New / Noto Nastaliq Urdu.
 *  - The work connects to FiKR&CD (Forum for Indus-Kohistani Research &
 *    Cultural Development), whose research areas include written
 *    resources, educational resources and children's literature.
 *
 * NO book titles, dates, publishers, dialects or statuses have been
 * provided or verified yet — BOOK_TRANSLATIONS is therefore empty by
 * design. Fill records ONLY from verified sources; every field below
 * can stay undefined until confirmed.
 */

export interface BookTranslation {
  /** Indus-Kohistani translated title */
  title: string;
  /** original work */
  originalTitle?: string;
  originalAuthor?: string;
  originalLanguage?: string;
  /** fixed provenance — kept for record completeness */
  translator: 'Saif Ullah';
  /** verified translation year only; leave undefined otherwise */
  year?: number;
  /** verified variety/dialect only (Duber-Kandia, Seo-Patan, Jijal-Kayal, Ranolia, Bankad) */
  dialect?: string;
  /** e.g. "Established Indus-Kohistani orthography (Arabic script, Extended-A)" */
  script: string;
  status: 'in-preparation' | 'completed' | 'published';
  publisher?: string;
  audience?: string;
  description?: string;
  edition?: 'digital' | 'physical' | 'digital + physical';
  cover?: string;
  /** PDF or external resource link — only where legitimately available */
  resourceUrl?: string;
  resourceLabel?: string;
  relatedTopics?: string[];
  relatedProject?: 'FiKR&CD';
  /** evidence/source note for the record */
  evidence?: string;
}

export const BOOK_TRANSLATIONS: BookTranslation[] = [];

export const BOOK_PROGRAM = {
  title: 'Indus-Kohistani Book Translations',
  targetLanguage: 'Indus-Kohistani',
  translator: 'Saif Ullah',
  script: 'Established Indus-Kohistani orthography — Arabic script with Extended-A characters (ڇ څ ݜ ڙ ݨ)',
  typography: ['Scheherazade New', 'Noto Nastaliq Urdu'],
  significance:
    'Book-length translation into Indus-Kohistani expands the language’s written and digital presence: it exercises the orthography at scale, builds terminology, and produces readable extended text for education and cultural transmission — core aims of the preservation effort.',
  relatedProject: {
    name: 'FiKR&CD',
    url: 'https://fikrcd.vercel.app/',
    repo: 'https://github.com/xl8saif/FiKR-CD',
  },
  emptyStateNote:
    'Individual book records will be published here as their details (titles, source works, dates, publication status, editions) are verified against the original records. Fields are not estimated or pre-filled.',
} as const;
