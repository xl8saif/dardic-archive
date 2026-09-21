import { SITE } from './profile';

export { SITE };

export type Dir = 'ltr' | 'rtl';
export type Font = 'latin' | 'nastaliq' | 'amiri' | 'scheherazade';

export interface LangInfo {
  name: string;
  native: string;
  dir: Dir;
  font: Font;
}

export const LANGUAGES: Record<string, LangInfo> = {
  en: { name: 'English', native: 'English', dir: 'ltr', font: 'latin' },
  ur: { name: 'Urdu', native: 'اردو', dir: 'rtl', font: 'nastaliq' },
  ar: { name: 'Arabic', native: 'العربية', dir: 'rtl', font: 'amiri' },
  // Extended-A orthographic characters (ڇ څ ݜ ڙ ݨ) — Scheherazade New covers them
  mvb: { name: 'Indus-Kohistani', native: 'کوہستانی', dir: 'rtl', font: 'scheherazade' },
  // Shina: preserve the script/orthographic conventions of the specific source
  scl: { name: 'Shina', native: 'شینا', dir: 'rtl', font: 'amiri' },
};

export function langInfo(code?: string): LangInfo {
  return (code && LANGUAGES[code]) || LANGUAGES.en;
}

/** Locale-aware long date, e.g. "14 August 2026" / "۱۴ اگست ۲۰۲۶" */
export function formatDate(date: Date, lang = 'en'): string {
  try {
    return new Intl.DateTimeFormat(lang, { dateStyle: 'long' }).format(date);
  } catch {
    return new Intl.DateTimeFormat('en', { dateStyle: 'long' }).format(date);
  }
}
