# Research Blog — Google Drive → Polished, Multilingual Blog

A personal research blog where articles, columns and books written in **Google Docs / Word / PDF** on Google Drive are converted into beautifully formatted posts — with automatically fetched, freely licensed images — and published after **your explicit review**.

Languages supported with full right-to-left layout and per-script typography:

| Code | Language | Direction | Font |
|---|---|---|---|
| `en` | English | LTR | Charter (serif) |
| `ur` | اردو (Urdu) | RTL | **Noto Nastaliq Urdu** |
| `ar` | العربية (Arabic) | RTL | Amiri |
| `mvb` | Indus-Kohistani | RTL | Amiri |
| `scl` | Shina | RTL | Amiri |

---

## How publishing works

```
Google Drive (Blog/Articles, Blog/Books)      ← you write here
        │  python sync/pull.py                 read-only, one command
        ▼
src/content/… (status: draft)                 ← converted, images fetched
        │  python sync/review.py → :5555       review dashboard
        ▼  [Approve & Publish]
src/content/… (status: published)
        │  git add . && git commit && git push
        ▼
GitHub Actions → astro build → GitHub Pages   ← live site
```

**Nothing publishes without your approval.** Drive is only ever read; your originals are untouched.

---

## Quick start

```powershell
cd research-blog

# 1. Site dependencies (Node 22+)
npm install

# 2. Pipeline dependencies (Python 3.10+)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-sync.txt

# 3. Pixabay (optional but recommended)
copy .env.example .env    # then paste your free key from https://pixabay.com/api/docs/
```

### One-time Google Cloud setup (~5 minutes, free)

1. Go to [console.cloud.google.com](https://console.cloud.google.com/) → create a project (any name, e.g. `research-blog`).
2. **APIs & Services → Library** → search **Google Drive API** → **Enable**.
3. **APIs & Services → OAuth consent screen** → External → fill only your email → add yourself as a **Test user**.
4. **Credentials → Create credentials → OAuth client ID** → type **Desktop app** → **Download JSON**.
5. Save it as `research-blog/sync/client_secret.json` (gitignored).

### Google Drive layout

Create a folder named **`Blog`** in your Drive:

```
Blog/
├── Articles/
│   ├── English/           ← subfolder name sets the language
│   ├── Urdu/
│   ├── Arabic/
│   └── Shina/
└── Books/
    └── My Book Title/     ← one folder = one book
        ├── 00 - Introduction.gdoc / .docx / .pdf
        ├── 01 - First Chapter.docx
        ├── 02 - ...
        └── cover.jpg      ← optional
```

Language is chosen by (in priority order):
1. **Filename tag** — `My Column [ur].docx` (also `[en]`, `[ar]`, `[mvb]`, `[scl]`)
2. **Text detection** — Arabic-script content defaults to Urdu; refine per folder
3. **Subfolder name** — `English/`, `Urdu/`, `Arabic/`, `Kohistani/`, `Shina/`

### Daily workflow

```powershell
cd research-blog

python sync/pull.py        # 1. pull + convert + fetch images (drafts only)
python sync/review.py      # 2. review at http://127.0.0.1:5555 → Approve
                           # 3. publish what you approved:
git add . && git commit -m "Publish" && git push
```

The dev server (`npm run dev`) shows approved posts immediately; the GitHub Actions workflow deploys to Pages on every push.

---

## File-by-file map

| Path | Purpose |
|---|---|
| `sync/pull.py` | Orchestrator: scans Drive, converts, enriches images, writes drafts, writes `sync/pull-report.md` |
| `sync/drive.py` | OAuth + read-only Drive access (token cached in `sync/token.json`) |
| `sync/converters.py` | Google Docs HTML / `.docx` (mammoth) / PDF → clean markdown; extracts embedded images |
| `sync/images.py` | Pixabay (with key) → Openverse (no key) image search, downloads, credits |
| `sync/languages.py` | Language/direction detection, transliterating slugs |
| `sync/review.py` | Flask dashboard at `127.0.0.1:5555` — preview drafts as they will render, approve/revert |
| `src/content/` | Articles & books as markdown; `status:` controls visibility |
| `.github/workflows/deploy.yml` | Build & deploy to GitHub Pages |

## Configuration (`sync/config.yaml`)

- `drive.root` — name of the root folder in Drive (`Blog`)
- `images.provider_order` — `[pixabay, openverse]`; falls back automatically
- `images.max_per_post` — in-body images placed after major headings
- `review.port` — dashboard port (default 5555)

## Notes & limits

- PDFs are text-extracted (headings/formatting are lost) and the original file is saved as a download link at the end of the post; prefer Docs/Word for the reading body.
- Re-running `pull.py` is **idempotent** — unchanged files are skipped via content hash + modified time; your `tags`, `pubDate` and `status` survive re-syncs.
- The review dashboard binds to `127.0.0.1` only — nothing is reachable from the network.
- Books publish as a whole (cover + all chapters); chapter-level approval comes later.

## Roadmap ideas

- Newsletter signup, public search, comments (giscus)
- CI-side auto-sync via a Drive service account
- PDF downloads per book, per-chapter audio embedding
