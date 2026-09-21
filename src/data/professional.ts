/**
 * Verified professional record. Facts only — from the master profile
 * document and project content. Scale figures are flagged `reported`.
 * External profile links (LinkedIn/ProZ etc.) are NOT included: none
 * have been provided — add them here when available.
 */

export interface Project {
  id: string;
  name: string;
  kind: 'professional' | 'research' | 'digital';
  role?: string;
  org?: string;
  description: string;
  points: string[];
  languages: string[];
  status: 'completed' | 'ongoing';
  url?: string;
  repo?: string;
  reportedScale?: string;
}

export const PROJECTS: Project[] = [
  {
    id: 'pubg-mobile',
    name: 'PUBG MOBILE — Urdu game localization',
    kind: 'professional',
    org: 'Level Infinite',
    role: 'Urdu localization, MTPE, LQA',
    description:
      'Urdu localization for PUBG MOBILE covering UI, system strings, events and promotional content, with machine-translation post-editing, language quality assurance and live-ops localization.',
    points: [
      'UI and system string localization',
      'Events and promotional content',
      'MTPE (machine-translation post-editing)',
      'LQA (language quality assurance)',
      'Live-ops localization',
    ],
    languages: ['Urdu', 'English'],
    status: 'completed',
  },
  {
    id: 'iflytek',
    name: 'iFLYTEK — multilingual linguistic QA',
    kind: 'professional',
    role: 'Linguistic QA across Arabic, Persian, Urdu, English',
    description:
      'Speech and transcription quality work across four languages for iFLYTEK speech technology.',
    points: [
      'Speech quality evaluation',
      'Transcription quality work',
      'Linguistic QA in Arabic, Persian, Urdu and English',
    ],
    languages: ['Arabic', 'Persian', 'Urdu', 'English'],
    status: 'completed',
  },
  {
    id: 'productive-playhouse',
    name: 'Productive Playhouse — Shina language verification',
    kind: 'professional',
    role: 'Shina language verifier',
    description:
      'Verification of Shina-language media — language work on a large corpus of recorded video material in Shina.',
    points: ['Shina-language media verification'],
    languages: ['Shina'],
    status: 'completed',
    reportedScale: '1,500+ Shina-language videos (reported)',
  },
  {
    id: 'hajj-umrah',
    name: 'Saudi Ministry of Hajj & Umrah — translation program',
    kind: 'professional',
    role: 'Translator, large-scale government-domain project',
    description:
      'Large-scale translation project for the Saudi Ministry of Hajj & Umrah in the government domain.',
    points: ['Government-domain translation at scale'],
    languages: ['Arabic', 'Urdu'],
    status: 'completed',
    reportedScale: '≈500,000 words (reported)',
  },
  {
    id: 'cloudtrans',
    name: 'CloudTrans',
    kind: 'professional',
    role: 'Founder & manager',
    description:
      'A large-scale multilingual translation operation founded and managed by Saif Ullah.',
    points: ['Multilingual translation operation at scale'],
    languages: ['Arabic', 'Urdu', 'English', 'Persian'],
    status: 'completed',
    reportedScale: '5M+ words (reported)',
  },
  {
    id: 'fikrcd',
    name: 'FiKR&CD',
    kind: 'research',
    org: 'Forum for Indus-Kohistani Research & Cultural Development',
    role: 'Co-founder',
    description:
      'Forum for Indus-Kohistani Research & Cultural Development — established 2024 with Dr Hussain Ahmad Faizy for the research, documentation, preservation and digital development of the Indus-Kohistani language and culture.',
    points: [
      'Indus-Kohistani research and documentation',
      'Language preservation and cultural documentation',
      'Digital archive and language-technology development',
    ],
    languages: ['Indus-Kohistani', 'Urdu', 'English'],
    status: 'ongoing',
    url: 'https://fikrcd.vercel.app/',
    repo: 'https://github.com/xl8saif/FiKR-CD',
  },
  {
    id: 'research-blog',
    name: 'This research blog — multilingual publishing pipeline',
    kind: 'digital',
    role: 'Design & implementation',
    description:
      'A multilingual publishing platform for language research: RTL/LTR-aware layouts, per-script typography (Nastaliq, Amiri, Scheherazade New), Google Drive → draft → review pipeline, and structured content collections.',
    points: [
      'RTL/LTR language systems',
      'Urdu Nastaliq / Arabic / Indus-Kohistani typography',
      'Drive → review → publish content pipeline',
      'Structured multilingual content model',
    ],
    languages: ['English', 'Urdu', 'Arabic', 'Indus-Kohistani', 'Shina'],
    status: 'ongoing',
  },
];

/* ------------------------------------------------------------------ */

export interface Publication {
  title: string;
  doi: string;
  lang?: string;
  type?: string;
  relatedLanguages?: string[];
  requiresVerification?: boolean;
}

export const PUBLICATIONS: Publication[] = [
  {
    title: 'Shari',
    doi: '10.5281/zenodo.16939807',
    relatedLanguages: ['Indus-Kohistani'],
    requiresVerification: true,
  },
  {
    title: 'Sawaat-e-Nabi',
    doi: '10.5281/zenodo.15834110',
    relatedLanguages: ['Urdu'],
    requiresVerification: true,
  },
];

export const PUBLICATIONS_NOTE =
  'Only verified records are listed. Details (dates, abstracts, types) are marked for verification and will be completed against the original records. Further publications exist but are held back until their metadata is verified.';

/* ------------------------------------------------------------------ */

export interface LanguageProfile {
  code: string;
  name: string;
  native?: string;
  dir: 'ltr' | 'rtl';
  font: string;
  tagline: string;
  /** sections rendered as placeholder structure until verified content exists */
  sections: { overview: string; status: string };
  dialects?: { name: string; documented: boolean }[];
  orthography?: { char: string; codepoint: string; usage: string }[];
  /** Optional reference figure (image) with visible source credit */
  figure?: { src: string; alt: string; caption: string; credit: string };
  typography: string[];
  professionalRole?: string;
}

export const LANGUAGES: LanguageProfile[] = [
  {
    code: 'mvb',
    name: 'Indus-Kohistani',
    native: 'کوہستانی',
    dir: 'rtl',
    font: 'scheherazade',
    tagline: 'Documentation, preservation and digital development of Indus-Kohistani.',
    sections: {
      overview:
        'A Dardic language of the Indus Kohistan, and the central research focus of this site — documented through FiKR&CD across its dialect areas, its oral traditions and its writing system.',
      status: 'Documented through ongoing FiKR&CD fieldwork; speaker numbers and vitality ratings are deliberately not stated here — they require verified sources.',
    },
    dialects: [
      { name: 'Duber-Kandia', documented: false },
      { name: 'Seo-Patan', documented: false },
      { name: 'Jijal-Kayal', documented: false },
      { name: 'Ranolia', documented: false },
      { name: 'Bankad', documented: false },
    ],
    orthography: [
      { char: 'ڇ', codepoint: 'U+067B', usage: 'established orthographic character — usage note pending verification' },
      { char: 'څ', codepoint: 'U+0685', usage: 'established orthographic character — usage note pending verification' },
      { char: 'ݜ', codepoint: 'U+075C', usage: 'established orthographic character — usage note pending verification' },
      { char: 'ڙ', codepoint: 'U+0699', usage: 'established orthographic character — usage note pending verification' },
      { char: 'ݨ', codepoint: 'U+0768', usage: 'established orthographic character — usage note pending verification' },
    ],
    typography: ['Scheherazade New', 'Noto Nastaliq Urdu'],
  },
  {
    code: 'scl',
    name: 'Shina',
    native: 'شینا',
    dir: 'rtl',
    font: 'amiri',
    tagline: 'Research, verification and digital visibility for Shina.',
    sections: {
      overview:
        'A Dardic language of Gilgit-Baltistan. Work to date includes large-scale media language verification and research on Shina’s digital presence and future.',
      status: 'Media verification work is documented; broader documentation coverage varies and is not claimed here.',
    },
    typography: ['Amiri', 'Noto Naskh Arabic'],
  },
  {
    code: 'ur',
    name: 'Urdu',
    native: 'اردو',
    dir: 'rtl',
    font: 'nastaliq',
    tagline: 'A major professional working language and a digital-language interest.',
    sections: {
      overview:
        'Working language of twelve years of professional practice — translation, localization, MTPE, LQA, legal, religious and government domains — and a language-research interest in terminology, digital publishing and RTL systems.',
      status: 'Professional experience documented across multiple projects; research output pending verification.',
    },
    typography: ['Noto Nastaliq Urdu'],
    professionalRole:
      'Game localization (PUBG MOBILE), government translation, religious translation, legal and technical domains.',
  },
  {
    code: 'ar',
    name: 'Arabic',
    native: 'العربية',
    dir: 'rtl',
    font: 'amiri',
    tagline: 'Translation, interpretation and Arabic-script typography.',
    sections: {
      overview:
        'Major professional working language — Arabic ↔ Urdu and Arabic ↔ English across religious, government, legal and corporate registers, plus Arabic-script typography and RTL publishing.',
      status: 'Professional experience documented across multiple projects.',
    },
    typography: ['Amiri', 'Noto Naskh Arabic'],
    figure: {
      src: '/images/script-evolution-736.jpg',
      alt: 'Comparative chart of Semitic scripts: Arabic, Hebrew, two Assyrian variants, Phoenician and Ancient Aramaic, letter by letter',
      caption:
        'Evolution and comparison of signs across Semitic scripts — Arabic, Hebrew, Assyrian, Phoenician and Ancient Aramaic. Shown here as context for the Arabic script tradition; original author unknown.',
      credit: 'Pinterest (Ancient Script Evolution collection), author unverified',
    },
    professionalRole:
      'Government translation (Hajj & Umrah program), speech-technology linguistic QA (iFLYTEK), religious material.',
  },
];

export const DIGITAL_WORK_NOTE =
  'Digital language work concentrates on multilingual publishing systems, RTL/LTR infrastructure, Urdu and Arabic-script typography, and digital preservation — not general software development.';

/* ------------------------------------------------------------------ */

export const DIALECT_NOTE =
  'Dialect areas are listed as known varieties. Documentation coverage differs between varieties; the site does not claim equal coverage.';
