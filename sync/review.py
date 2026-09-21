"""Local review dashboard for sync drafts.

    python sync/review.py   →  http://127.0.0.1:5555

Drafts are previewed exactly as the site will render them (article/RTL/fonts).
"Approve & Publish" flips status to published; the site picks it up on the next
build (dev server shows it immediately). "Revert to draft" undoes it.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml
from flask import Flask, jsonify, redirect, render_template_string, request, url_for

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import load_config, project_root  # noqa: E402

ROOT = project_root()
cfg = load_config()

ARTICLES = ROOT / cfg["paths"]["articles_out"]
BOOKS = ROOT / cfg["paths"]["books_out"]

app = Flask(__name__)


# ---------------------------------------------------------------- helpers
def _parse(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.index("\n---", 3)
        meta = yaml.safe_load(text[3:end]) or {}
        return meta, text[end + 4:].lstrip("\n")
    return {}, text


def _write_meta(path: Path, meta: dict, body: str) -> None:
    path.write_text(
        "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=100)
        + "---\n\n" + body, encoding="utf-8")


def collect_articles() -> list[dict]:
    items = []
    for p in sorted(ARTICLES.glob("*.md")):
        meta, _ = _parse(p)
        items.append({"path": p, "rel": str(p.relative_to(ROOT)),
                      "id": p.stem, "meta": meta})
    items.sort(key=lambda i: str(i["meta"].get("pubDate", "")), reverse=True)
    return items


def collect_books() -> list[dict]:
    out = []
    for d in sorted(BOOKS.iterdir()):
        by = d / "book.yaml"
        if not d.is_dir() or not by.exists():
            continue
        meta = yaml.safe_load(by.read_text(encoding="utf-8")) or {}
        chapters = []
        for c in sorted(d.glob("*.md")):
            cmeta, _ = _parse(c)
            chapters.append({"path": c, "rel": str(c.relative_to(ROOT)),
                             "id": c.stem, "meta": cmeta})
        chapters.sort(key=lambda c: c["meta"].get("order", 0))
        out.append({"dir": d, "meta": meta, "chapters": chapters})
    return out


def _is_rtl(meta: dict) -> bool:
    if meta.get("dir"):
        return meta["dir"] == "rtl"
    return meta.get("lang") in {"ur", "ar", "mvb", "scl"}


def _fmt_date(value) -> str:
    """Best-effort date formatting for the dashboard."""
    return str(value)[:10]


def _publish_one(path: Path, published: bool) -> dict:
    meta, body = _parse(path)
    meta["status"] = "published" if published else "draft"
    _write_meta(path, meta, body)
    return {"ok": True, "file": str(path.relative_to(ROOT)),
            "status": meta["status"]}


def _publish_book(book: dict, published: bool) -> dict:
    meta = book["meta"]
    meta["status"] = "published" if published else "draft"
    (book["dir"] / "book.yaml").write_text(
        yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")
    for ch in book["chapters"]:
        _publish_one(ch["path"], published)
    return {"ok": True, "file": str(book["dir"].relative_to(ROOT))}


# ---------------------------------------------------------------- routes
PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Review drafts — research-blog</title>
<style>
  :root { --bg:#faf7f2; --ink:#22221f; --soft:#57534a; --faint:#8a857a;
          --accent:#0f766e; --gold:#b7791f; --border:#e4ddd0; --surface:#fff;
          --danger:#b3413b; --radius:14px; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
         font-family:'Segoe UI', system-ui, sans-serif; line-height:1.6; }
  header { position:sticky; top:0; background:color-mix(in srgb, var(--bg) 92%, transparent);
           backdrop-filter:blur(8px); border-bottom:1px solid var(--border);
           padding:0.9rem 1.4rem; display:flex; gap:1rem; align-items:baseline; z-index:10;}
  h1 { font-size:1.15rem; margin:0; }
  header .hint { color:var(--faint); font-size:0.85rem; }
  main { max-width:1060px; margin:0 auto; padding:1.6rem 1.2rem 4rem; }
  .counts { display:flex; gap:0.5rem; flex-wrap:wrap; margin-bottom:1.4rem; }
  .pill { background:var(--surface); border:1px solid var(--border);
          border-radius:999px; padding:0.25rem 0.9rem; font-size:0.88rem; color:var(--soft);}
  .pill b { color:var(--accent); }
  .item { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius);
          padding:1rem 1.2rem; margin-bottom:0.9rem; display:flex; gap:1rem; align-items:center;}
  .item.grow { display:block; }
  .badge { font-size:0.72rem; letter-spacing:0.5px; text-transform:uppercase;
           border-radius:999px; padding:0.2rem 0.65rem; white-space:nowrap; }
  .badge.draft { background:#fdeed0; color:#8a5a00; border:1px solid #ecd9a8; }
  .badge.published { background:#d9efed; color:#0b4f4a; border:1px solid #b7dedb; }
  .badge.lang { background:#f1ece3; color:var(--soft); border:1px solid var(--border); }
  .t { font-weight:600; font-size:1.02rem; }
  .muted { color:var(--faint); font-size:0.86rem; }
  .actions { margin-inline-start:auto; display:flex; gap:0.5rem; flex-wrap:wrap; }
  a.btn, button.btn { border-radius:999px; padding:0.42rem 1rem; font-size:0.88rem;
        border:1px solid var(--border); background:var(--surface); color:var(--soft);
        cursor:pointer; text-decoration:none; }
  .btn.primary { background:var(--accent); border-color:var(--accent); color:#fff; }
  .btn.warn { color:var(--danger); border-color:#e3c4c1; }
  .btn:hover { filter:brightness(0.97); }
  pre.body { background:#f6f2ea; border:1px solid var(--border); border-radius:10px;
        padding:0.9rem 1.1rem; overflow:auto; max-height:420px; font-size:0.84rem; }
  iframe { width:100%; height:520px; border:1px solid var(--border); border-radius:10px; background:#fff;}
  details summary { cursor:pointer; color:var(--accent); font-size:0.9rem; }
  .urdu { font-family:'Noto Nastaliq Urdu', serif; }
  .empty { color:var(--faint); text-align:center; padding:3rem 0; }
  .error { background:#fdeaea; border:1px solid #eec4c1; color:#7c2d2a;
           border-radius:10px; padding:0.8rem 1rem; margin-bottom:1rem; }
</style>
</head>
<body>
<header>
  <h1>📝 Review drafts</h1>
  <span class="hint">local dashboard — nothing is public until approved &amp; pushed</span>
</header>
<main>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}

  <div class="counts">
    <span class="pill">Articles — <b>{{ n_draft_articles }}</b> draft(s), <b>{{ n_pub_articles }}</b> published</span>
    <span class="pill">Books — <b>{{ n_draft_books }}</b> draft(s), <b>{{ n_pub_books }}</b> published</span>
  </div>

  <h2 style="font-size:1.05rem;">Articles</h2>
  {% for a in articles %}
  <div class="item">
    <div style="flex:1; min-width:0;">
      <div class="t {{ 'urdu' if a.meta.lang in ('ur',) else '' }}" lang="{{ a.meta.lang }}">{{ a.meta.title }}</div>
      <div class="muted">
        {{ a.id }} · {{ a.meta.lang }}{% if a.meta.dir == 'rtl' %} · RTL{% endif %} · {{ a.meta.pubDate }}
      </div>
    </div>
    <span class="badge {{ a.meta.status }}">{{ a.meta.status }}</span>
    <div class="actions">
      <details>
        <summary>preview</summary>
        <p><iframe src="/preview/{{ a.rel }}"></iframe></p>
      </details>
      <a class="btn" href="/preview/{{ a.rel }}" target="_blank">open ↗</a>
      {% if a.meta.status == 'draft' %}
      <form method="post" action="/approve/article/{{ a.rel }}">
        <button class="btn primary" type="submit">Approve &amp; Publish</button>
      </form>
      {% else %}
      <form method="post" action="/revert/article/{{ a.rel }}">
        <button class="btn warn" type="submit">Revert to draft</button>
      </form>
      {% endif %}
    </div>
  </div>
  {% else %}
  <p class="empty">No articles found — run <code>python sync/pull.py</code> first.</p>
  {% endfor %}

  <h2 style="font-size:1.05rem; margin-top:2.2rem;">Books</h2>
  {% for b in books %}
  <div class="item">
    <div style="flex:1;">
      <div class="t {{ 'urdu' if b.meta.lang in ('ur',) else '' }}" lang="{{ b.meta.lang }}">{{ b.meta.title }}</div>
      <div class="muted">{{ b.chapters|length }} chapters · {{ b.meta.lang }}
        · {% if b.meta.cover %}has cover{% else %}no cover{% endif %}</div>
    </div>
    <span class="badge {{ b.meta.status }}">{{ b.meta.status }}</span>
    <div class="actions">
      {% if b.meta.status == 'draft' %}
      <form method="post" action="/approve/book/{{ b.dir.name }}">
        <button class="btn primary" type="submit">Approve &amp; Publish</button>
      </form>
      {% else %}
      <form method="post" action="/revert/book/{{ b.dir.name }}">
        <button class="btn warn" type="submit">Revert to draft</button>
      </form>
      {% endif %}
    </div>
  </div>
  {% endfor %}

  <div style="margin-top:2.2rem; color:var(--faint); font-size:0.88rem;">
    After approving, publish to the web:<br>
    <code>cd research-blog &amp;&amp; npm run build &amp;&amp; git add . &amp;&amp; git commit -m "Publish" &amp;&amp; git push</code>
  </div>
</main>
</body>
</html>
"""


@app.get("/")
def index():
    articles = collect_articles()
    books = collect_books()
    n_da = sum(1 for a in articles if a["meta"].get("status") == "draft")
    n_pa = len(articles) - n_da
    n_db = sum(1 for b in books if b["meta"].get("status") == "draft")
    n_pb = len(books) - n_db
    error = request.args.get("error")
    return render_template_string(
        PAGE, articles=articles, books=books,
        n_draft_articles=n_da, n_pub_articles=n_pa,
        n_draft_books=n_db, n_pub_books=n_pb,
        error=error)


@app.get("/preview/<path:rel>")
def preview(rel: str):
    """Render a draft markdown file with the site's real CSS in a frame."""
    p = (ROOT / rel).resolve()
    if not p.is_file() or ROOT not in p.parents:
        return "not found", 404
    meta, body = _parse(p)
    import markdown as md_mod
    html_body = md_mod.markdown(body, extensions=["tables", "fenced_code"])
    rtl = _is_rtl(meta)
    lang = meta.get("lang", "en")
    lang_class = {"ur": "nastaliq", "ar": "arabic-script",
                  "mvb": "arabic-script", "scl": "arabic-script"}.get(lang, "")
    return render_template_string(PREVIEW, meta=meta, body=html_body,
                                  rtl=rtl, lang=lang, lang_class=lang_class)


PREVIEW = """
<!doctype html>
<html lang="{{ lang }}" dir="{{ 'rtl' if rtl else 'ltr' }}" class="{{ lang_class }}">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="http://127.0.0.1:4321/src/styles/global.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-nastaliq-urdu@5/400.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-nastaliq-urdu@5/700.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/amiri@5/400.css">
<style>
  body { margin:0; background:#fff; padding: 1.6rem 1.2rem 3rem; }
  .prose-inner { max-width: 68ch; margin-inline:auto; }
  .badge { float:right; font-size:0.75rem; background:#fdeed0; color:#8a5a00;
           border-radius:999px; padding:0.15rem 0.7rem; }
</style>
</head>
<body>
  <span class="badge">draft preview</span>
  <div class="prose-inner" lang="{{ lang }}">
    <h1>{{ meta.title }}</h1>
    {{ body|safe }}
  </div>
</body>
</html>
"""


@app.post("/approve/article/<path:rel>")
def approve_article(rel: str):
    p = (ROOT / rel).resolve()
    if p.is_file() and ROOT in p.parents:
        _publish_one(p, True)
    return redirect(url_for("index"))


@app.post("/revert/article/<path:rel>")
def revert_article(rel: str):
    p = (ROOT / rel).resolve()
    if p.is_file() and ROOT in p.parents:
        _publish_one(p, False)
    return redirect(url_for("index"))


@app.post("/approve/book/<book_slug>")
def approve_book(book_slug: str):
    for book in collect_books():
        if book["dir"].name == book_slug:
            _publish_book(book, True)
            break
    return redirect(url_for("index"))


@app.post("/revert/book/<book_slug>")
def revert_book(book_slug: str):
    for book in collect_books():
        if book["dir"].name == book_slug:
            _publish_book(book, False)
            break
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(cfg.get("review", {}).get("port", 5555))
    print(f"* Review dashboard: http://127.0.0.1:{port}")
    print("* Approve drafts, then commit & push to publish.")
    app.run(host="127.0.0.1", port=port, debug=False)