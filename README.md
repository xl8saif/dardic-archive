# The Dardic Archive

**Language research · preservation · translation & localization · digital language work**
*Saif Ullah — https://xl8saif.github.io/dardic-archive/*

A trilingual (English · العربية · اردو) research and publishing platform focused on the
endangered languages of the Indus Kohistan — above all **Indus-Kohistani** and **Shina** —
alongside professional translation & localization work (Arabic ↔ Urdu, Arabic ↔ English,
Persian) and digital language technology (multilingual publishing, RTL systems, Urdu
Nastaliq typography, digital preservation).

> **Editorial rule:** nothing is invented. Scale figures are marked *reported*, only
> verified DOIs are published, and nothing goes live without the editor's review.

---

## Site sections

| Route | Section |
|---|---|
| `/` · `/ar/` · `/ur/` | Localized homepages (language switcher in the header) |
| `/research/` | Research index (Indus-Kohistani, Shina, Urdu, Arabic, …) |
| `/languages/…` | Language profiles incl. dialects, orthography tables, typography |
| `/research/indus-kohistani-resources/` | **IK Translation & Written Resources** archive — searchable/filterable catalogue of written-resource works (schema-ready; records imported via JSON) |
| `/publications/` | Verified publication records (DOIs) |
| `/projects/` | Professional & research projects (PUBG MOBILE, iFLYTEK, Hajj & Umrah, CloudTrans, FiKR&CD …) |
| `/translation/` | Translation & localization experience |
| `/digital/` · `/folklore/` | Digital language work · folklore & oral traditions |
| `/contribute/` · `/ar/contribute/` · `/ur/contribute/` | **Publish with us** — contributor platform with editorial review gate and file-upload form |
| `/archive/` | Everything, filterable by year / language / category |
| `/articles/…` | Blog articles; chrome follows the article language |

## Tech stack

- **Astro** (static, zero-JS by default) — `npm run dev` / `npm run build`
- **UI i18n** — `src/i18n/ui.ts` (EN/AR/UR dictionaries; typed — a missing key fails the build)
- **Fonts** — Noto Nastaliq Urdu, Amiri, Scheherazade New (for ڇ څ ݜ ڙ ݨ), Inter — all self-hosted via fontsource
- **RSS + sitemap + robots.txt** generated at build
- **SEO** — canonical URLs, hreflang alternates, Open Graph/Twitter, Person & Article JSON-LD

## Project structure

```
src/
├── i18n/ui.ts                  ← UI translations (en / ar / ur)
├── data/
│   ├── profile.ts              ← authoritative master profile (identity, SITE, links)
│   ├── professional.ts         ← projects, publications, language profiles (verified facts)
│   ├── ik-resources.json       ← IK Written Resources dataset (batch-import works here)
│   ├── ikResources.ts          ← schema + loader for the archive above
│   ├── bookTranslations.ts     ← book-translation records (added only when verified)
│   ├── contribute.ts           ← contributor platform config (upload endpoint, limits)
│   └── site.ts                 ← language codes, directions, fonts, date formatting
├── content/
│   ├── articles/               ← markdown posts; frontmatter `status:` controls visibility
│   └── books/                  ← books (folder = book, files = chapters)
├── components/pages/           ← locale-aware Home & Contribute page components
├── layouts/Base.astro          ← SEO head, nav, language switcher, footer
└── pages/                      ← routes (see table above)
sync/                           ← Google Drive → blog pipeline (Python, read-only)
scripts/google-apps-script-submissions.gs  ← contributor-upload receiver (Apps Script)
.github/workflows/deploy.yml    ← build & deploy to GitHub Pages on push to main
```

## Local development

```bash
npm install          # Node 22+
npm run dev          # http://127.0.0.1:4321
npm run build        # production build → dist/
```

The Python sync pipeline (optional — only for Drive publishing) needs
`python -m venv .venv && pip install -r requirements-sync.txt` plus OAuth setup
described below.

## Content workflow: Google Drive → review → publish

Nothing publishes without approval. Drive is only ever **read**.

```
Google Drive (Blog/Articles, Blog/Books)      ← write in Docs / Word / PDF
        │  python sync/pull.py                ← converts to drafts, fetches free images
        ▼
src/content/…  (status: draft)
        │  python sync/review.py → http://127.0.0.1:5555
        ▼  [Approve & Publish]
status: published  →  git commit & push  →  live in ~1 min
```

One-time setup (details in the original docs / `sync/config.yaml`):

1. Google Cloud project with the **Drive API** enabled; OAuth **Desktop** client saved as
   `sync/client_secret.json` (gitignored).
2. Drive folder `Blog/Articles/<Language>/` (subfolder sets the language, or tag the
   filename: `My Column [ur].docx`).
3. `.env` with a free Pixabay key (optional — falls back to Openverse).

Languages: `en`, `ur` (Nastaliq), `ar`, `mvb` (Indus-Kohistani), `scl` (Shina) —
direction and typography switch automatically per piece.

## Contributor submissions (Publish with us)

`/contribute/` hosts a review-gated upload form (files ≤ 15 MB ×3). Submissions are
received by a **Google Apps Script Web App** (`scripts/google-apps-script-submissions.gs`)
that files them into your Drive under `Blog/Submissions`. To activate:

1. Create the script at script.google.com from the `.gs` file (steps in its header).
2. Deploy as Web App (Execute as: Me · Access: Anyone) and copy the `/exec` URL.
3. Paste it into `src/data/contribute.ts` → `upload.endpoint` (`enabled: true` is already set).

## Deployment

GitHub Actions (`.github/workflows/deploy.yml`) builds and deploys to **GitHub Pages**
on every push to `main` (~1 minute). Requires the repo variable `SITE_URL`
(Actions → Variables) — set to `https://xl8saif.github.io/dardic-archive/`.

To publish changes: commit and push `main`. To publish Drive drafts: run the sync +
review flow above first, then push.

## Adding content

- **Article** — drop a `.md` file into `src/content/articles/` with frontmatter
  (`title`, `description`, `pubDate`, `lang`, `category`, `tags`, `status: published`,
  optionally `translations`, `references`, `doi`, `featured`).
- **IK archive work** — append an object to `works` in `src/data/ik-resources.json`
  (a documented `$schema` example ships inside the file). Dialects are preserved
  verbatim; private files stay private via `visibility`.
- **Language profile / project / publication fact** — edit `src/data/professional.ts`
  (or `profile.ts` for identity). Unverified items must stay flagged.
- **UI translation** — `src/i18n/ui.ts`; all three locales must stay key-complete.

## License & attribution

Site content © Saif Ullah. Third-party images carry per-item credits (e.g. cover
photos from free-license providers); files marked private in the IK archive are
deliberately not exposed.
