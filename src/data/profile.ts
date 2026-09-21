/**
 * Authoritative content base — transcribed from the
 * "SAIF ULLAH — MASTER PROFESSIONAL & RESEARCH PROFILE" document.
 *
 * EDITORIAL RULES ENCODED HERE:
 *  - Nothing is invented. Unverified items carry `verify: true`
 *    and are rendered with a "requires verification" note.
 *  - Reported/estimated figures stay marked as reported
 *    (`reported: true`) — never presented as verified facts.
 *  - Interpretation is separated from documented evidence.
 */

export const IDENTITY = {
  name: 'Saif Ullah',
  fullName: 'Saif Ullah Jailani',
  location: 'Gilgit-Baltistan, Pakistan',
  roles: [
    'Translator & Localization Specialist',
    'Language Researcher',
    'Endangered-Language Preservation Advocate',
    'Language Technology / Digital Preservation Practitioner',
  ],
  yearsExperience: { value: '12+', reported: true },
} as const;

export const SITE = {
  /** Public site brand — rendered in the header, hero and metadata */
  brand: 'The Dardic Archive',
  /** The person — author, bylines, JSON-LD */
  name: 'Saif Ullah',
  title: 'Language Research · Preservation · Localization',
  tagline:
    'Research, documentation and digital preservation of the languages of the Indus Kohistan — Indus-Kohistani, Shina, Urdu and Arabic — alongside twelve years of professional translation and localization work.',
  taglineUr:
    'تحقیق، دستاویز اور ڈیجیٹل تحفظ — کوہستانی، شینا، اردو اور عربی کے ساتھ ساتھ پیشہ ورانہ ترجمہ اور مقامی کاری۔',
  author: 'Saif Ullah',
} as const;

export const LINKS = {
  fikrcdSite: 'https://fikrcd.vercel.app/',
  fikrcdGitHub: 'https://github.com/xl8saif/FiKR-CD',
} as const;

/* ------------------------------------------------------------------ */
/* Languages of work                                                    */
/* ------------------------------------------------------------------ */

export interface WorkLanguage {
  code: string;
  name: string;
  native?: string;
  summary: string;
  scopes: string[];
}

export const WORK_LANGUAGES: WorkLanguage[] = [
  {
    code: 'mvb',
    name: 'Indus-Kohistani',
    native: 'کوہستانی',
    summary:
      'Documentation, preservation and digital development of the Indus-Kohistani language and its varieties.',
    scopes: [
      'Language documentation',
      'Endangered-language preservation',
      'Dialect variation',
      'Oral traditions & folklore',
      'Cultural vocabulary & terminology',
      'Orthography & script development',
      'Unicode / digital representation',
      'Educational resources & children’s literature',
      'Multilingual documentation & digital archives',
      'Language technology',
    ],
  },
  {
    code: 'scl',
    name: 'Shina',
    native: 'شینا',
    summary:
      'Research, documentation and language verification, with attention to Shina’s digital presence and future in Gilgit-Baltistan.',
    scopes: [
      'Language documentation & preservation',
      'Linguistic research',
      'Digital language presence',
      'Media & language verification',
      'Multilingual communities',
      'Future of Shina in Gilgit-Baltistan',
    ],
  },
  {
    code: 'ur',
    name: 'Urdu',
    native: 'اردو',
    summary:
      'Professional translation, localization and language-quality work, including Urdu digital typography and RTL.',
    scopes: [
      'Professional translation & MTPE',
      'Legal, religious & government translation',
      'Technical localization',
      'Urdu digital typography & RTL localization',
      'LQA & linguistic verification',
    ],
  },
  {
    code: 'ar',
    name: 'Arabic',
    native: 'العربية',
    summary:
      'Translation, interpretation and localization across religious, government, legal and corporate registers.',
    scopes: [
      'Translation & interpretation',
      'Religious & government material',
      'Legal / corporate communication',
      'Arabic–Urdu cross-cultural communication',
    ],
  },
  {
    code: 'fa',
    name: 'Persian',
    native: 'فارسی',
    summary: 'Advanced translation and localization capability.',
    scopes: ['Translation', 'Localization'],
  },
  {
    code: 'en',
    name: 'English',
    summary: 'Professional translation, research writing and international communication.',
    scopes: [
      'Professional translation',
      'Research & technical writing',
      'Localization',
      'International communication',
    ],
  },
];

/* ------------------------------------------------------------------ */
/* Professional projects — only those documented in the profile         */
/* ------------------------------------------------------------------ */

export interface Project {
  org: string;
  role: string;
  points: string[];
  /** scale figure as stated in the profile — shown as reported, not verified */
  reportedScale?: string;
}

export const PROJECTS: Project[] = [
  {
    org: 'Level Infinite / PUBG MOBILE',
    role: 'Urdu game localization',
    points: [
      'UI, system, events and promotional content',
      'MTPE (machine-translation post-editing)',
      'LQA (language quality assurance)',
      'Live-ops localization',
    ],
  },
  {
    org: 'iFLYTEK',
    role: 'Arabic, Persian, Urdu, English',
    points: [
      'Speech and transcription quality work',
      'Linguistic QA across four languages',
    ],
  },
  {
    org: 'Productive Playhouse',
    role: 'Shina language verification',
    points: ['Verification of Shina-language media'],
    reportedScale: '1,500+ Shina-language videos',
  },
  {
    org: 'Saudi Ministry of Hajj & Umrah',
    role: 'Large-scale translation project',
    points: ['Government-domain translation at scale'],
    reportedScale: 'approximately 500,000 words',
  },
  {
    org: 'CloudTrans',
    role: 'Founder & manager',
    points: ['Large-scale multilingual translation operation'],
    reportedScale: '5M+ words (reported)',
  },
];

/* ------------------------------------------------------------------ */
/* FiKR&CD                                                              */
/* ------------------------------------------------------------------ */

export const FIKRCD = {
  fullName: 'Forum for Indus-Kohistani Research & Cultural Development',
  abbrev: 'FiKR&CD',
  established: 2024,
  founders: ['Saif Ullah Jailani', 'Dr Hussain Ahmad Faizy'],
  mission:
    'Research, documentation, preservation and digital development of the Indus-Kohistani language and culture.',
  languageScope: ['Indus-Kohistani', 'Urdu', 'English'],
  relatedResearch: 'Shina and other Dardic languages',
  researchAreas: [
    'Language',
    'Culture',
    'Folklore',
    'Oral traditions',
    'Linguistics',
    'Documentation',
    'Digital preservation',
    'Educational resources',
    'Language technology',
  ],
} as const;

/* ------------------------------------------------------------------ */
/* Dialects & orthography                                               */
/* ------------------------------------------------------------------ */

export const DIALECTS = [
  { name: 'Duber-Kandia', note: 'variety documented under FiKR&CD fieldwork' },
  { name: 'Seo-Patan', note: 'variety documented under FiKR&CD fieldwork' },
  { name: 'Jijal-Kayal', note: 'variety documented under FiKR&CD fieldwork' },
  { name: 'Ranolia', note: 'variety documented under FiKR&CD fieldwork' },
  { name: 'Bankad', note: 'variety documented under FiKR&CD fieldwork' },
] as const;

/**
 * Established Indus-Kohistani orthographic characters.
 * Names/usage descriptions are placeholders pending verification —
 * the code profile itself renders correctly only with a font that
 * covers the Arabic Extended-A block (Scheherazade New / Noto Nastaliq).
 */
export const ORTHOGRAPHY = [
  { char: 'ڇ', codepoint: 'U+067B', usage: 'established orthographic character — usage note pending verification' },
  { char: 'څ', codepoint: 'U+0685', usage: 'established orthographic character — usage note pending verification' },
  { char: 'ݜ', codepoint: 'U+075C', usage: 'established orthographic character — usage note pending verification' },
  { char: 'ڙ', codepoint: 'U+0699', usage: 'established orthographic character — usage note pending verification' },
  { char: 'ݨ', codepoint: 'U+0768', usage: 'established orthographic character — usage note pending verification' },
] as const;

/* ------------------------------------------------------------------ */
/* Publications — verified DOI records only                             */
/* ------------------------------------------------------------------ */

export interface Publication {
  title: string;
  doi: string;
  /** true when the profile explicitly marks the record as needing verification */
  requiresVerification?: boolean;
  lang?: string;
}

export const PUBLICATIONS: Publication[] = [
  { title: 'Shari', doi: '10.5281/zenodo.16939807' },
  { title: 'Sawaat-e-Nabi', doi: '10.5281/zenodo.15834110' },
];

export const PUBLICATIONS_NOTE =
  'Only verified records are listed. Further publications exist but are held back from this page until their dates, titles and DOIs can be verified against the original records.';
