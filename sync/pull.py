"""Pull articles and books from Google Drive into the blog as DRAFTS.

Usage:
    python sync/pull.py            # full sync (authenticates on first run)
    python sync/pull.py --no-images

Nothing is published: everything is written with `status: draft`. Approve
drafts in the review dashboard (python sync/review.py).
"""
from __future__ import annotations

import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import load_config, project_root  # noqa: E402
import converters  # noqa: E402
import drive  # noqa: E402
import images as images_mod  # noqa: E402
import languages as lang_mod  # noqa: E402

ROOT = project_root()
DOC_MIME = "application/vnd.google-apps.document"
SKIP_MIMES_PREFIX = ("application/vnd.google-apps.spreadsheet",
                     "application/vnd.google-apps.presentation")


def log(msg: str) -> None:
    print(msg, flush=True)


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_frontmatter(path: Path) -> dict:
    """Return existing YAML frontmatter of a generated file ({} if absent)."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        try:
            end = text.index("\n---", 3)
            return yaml.safe_load(text[3:end]) or {}
        except (ValueError, yaml.YAMLError):
            return {}
    return {}


def dump_frontmatter(meta: dict) -> str:
    return "---\n" + yaml.safe_dump(
        meta, allow_unicode=True, sort_keys=False, width=100).rstrip() + "\n---\n"


def snippet_from_md(md_text: str, limit: int = 170) -> str:
    for block in md_text.split("\n\n"):
        line = block.replace("\n", " ").strip()
        line = line.lstrip(">-*# ").strip()
        if len(line) >= 40:
            if len(line) > limit:
                line = line[: limit - 1].rstrip() + "…"
            return line
    return ""


class Syncer:
    def __init__(self, cfg: dict, use_images: bool):
        self.cfg = cfg
        self.use_images = use_images
        self.service = None
        self.cache = drive.load_cache()
        self.report: list[tuple[str, str, str]] = []  # (action, item, note)
        self.articles_out = ROOT / cfg["paths"]["articles_out"]
        self.books_out = ROOT / cfg["paths"]["books_out"]
        self.assets_out = ROOT / cfg["paths"]["assets_out"]

    # -------------------------------------------------- articles
    def sync_articles(self) -> None:
        cfg = self.cfg
        articles_cfg = cfg["drive"]
        root_id = drive.find_folder_by_name(self.service, articles_cfg["root"])
        if not root_id:
            self.report.append(("ERROR", "Drive root", f"folder '{articles_cfg['root']}' not found"))
            return
        art_folder = drive.find_folder_by_name(self.service, articles_cfg["articles"], root_id)
        if not art_folder:
            self.report.append(("ERROR", "Articles", f"folder '{articles_cfg['articles']}' not found"))
            return

        folder_map = {k.lower(): v for k, v in
                      cfg["languages"]["folders"].items()}
        allowed_tags = cfg["languages"]["filename_tags"]

        for child in drive.list_children(self.service, art_folder):
            if child["mimeType"] == "application/vnd.google-apps.folder":
                sub_id, sub_name = child["id"], child["name"]
                hint = folder_map.get(sub_name.lower())
                for f in drive.list_children(self.service, sub_id):
                    self.sync_article_file(f, folder_hint=hint, allowed_tags=allowed_tags)
            elif child["mimeType"] in (DOC_MIME,) or child["name"].lower().endswith((".docx", ".pdf")):
                self.sync_article_file(child, folder_hint=None, allowed_tags=allowed_tags)
            else:
                self.report.append(("SKIP", child["name"], "unsupported type"))

    def sync_article_file(self, f: dict, folder_hint: str | None, allowed_tags: list[str]) -> None:
        name = f["name"]
        mime = f["mimeType"]
        if mime.startswith(SKIP_MIMES_PREFIX):
            self.report.append(("SKIP", name, "spreadsheets/drawings not supported"))
            return
        if mime != DOC_MIME and not name.lower().endswith((".docx", ".pdf")):
            self.report.append(("SKIP", name, "not doc/docx/pdf/gdoc"))
            return

        tag = lang_mod.filename_tag(name, allowed_tags)
        raw = self._fetch_content(f)
        if raw is None:
            return
        checksum = md5(raw[0])
        cached = self.cache.get(f["id"], {})
        if (cached.get("hash") == checksum
                and cached.get("mtime") == f.get("modifiedTime")):
            self.report.append(("unchanged", name, "already synced"))
            return

        if mime == DOC_MIME:
            body_md, embedded = converters.html_to_markdown(
                raw[0].decode("utf-8", "replace"), self.assets_out)
        elif name.lower().endswith(".docx"):
            body_md, embedded = converters.convert_docx(raw[0], self.assets_out)
        else:
            body_md, embedded = converters.convert_pdf(raw[0])

        title = converters.derive_title(body_md, Path(name).stem)
        clean_title = tag_re.sub("", title).strip() or title
        lang = lang_mod.detect_lang(body_md + " " + title, folder_hint, tag)
        slug = lang_mod.slugify(clean_title)

        # PDFs: keep the original file as a downloadable attachment
        if name.lower().endswith(".pdf"):
            self.assets_out.mkdir(parents=True, exist_ok=True)
            orig_name = f"orig-{slug}.pdf"
            (self.assets_out / orig_name).write_bytes(raw[0])
            body_md += f"\n\n📄 [Download the original PDF](/assets-sync/{orig_name})\n"

        meta = {
            "title": clean_title,
            "description": snippet_from_md(body_md),
            "pubDate": (f.get("modifiedTime") or now_iso())[:10],
            "lang": lang,
            "tags": [],
            "status": "draft",
            "driveFile": f["id"],
            "syncedAt": now_iso(),
        }

        # preserve fields a human may have set on a previous sync
        out_path = self.articles_out / f"{slug}.md"
        old = parse_frontmatter(out_path)
        if old:
            for key in ("pubDate", "tags", "status", "description"):
                if old.get(key):
                    meta[key] = old[key]

        if self.use_images:
            hero = images_mod.enrich_article_images(
                clean_title, body_md, meta["tags"], self.assets_out, self.cfg)
            body_md = hero.get("body_md", body_md)
            if hero.get("hero"):
                meta["cover"] = hero["hero"].get("local") or hero["hero"].get("url")
                meta["coverCredit"] = hero["hero"]["credit"]
            if hero.get("credits"):
                meta["imageCredits"] = hero["credits"]

        meta["dir"] = lang_mod.dir_for(lang)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(dump_frontmatter(meta) + "\n" + body_md + "\n", encoding="utf-8")

        self.cache[f["id"]] = {"hash": checksum, "mtime": f.get("modifiedTime"),
                               "out": str(out_path.relative_to(ROOT))}
        action = "updated" if old else "NEW"
        note = f"lang={lang} dir={meta['dir']}" + (
            f" cover=yes" if meta.get("cover") else "")
        self.report.append((action, clean_title, note))

    def _fetch_content(self, f: dict) -> tuple[bytes, str] | None:
        try:
            if f["mimeType"] == DOC_MIME:
                return drive.export_google_doc(self.service, f["id"], "text/html"), "html"
            return drive.download_file(self.service, f["id"]), "binary"
        except Exception as exc:  # network, permissions…
            self.report.append(("ERROR", f["name"], str(exc)[:120]))
            return None

    # -------------------------------------------------- books
    def sync_books(self) -> None:
        cfg = self.cfg
        root_id = drive.find_folder_by_name(self.service, cfg["drive"]["root"])
        if not root_id:
            return
        books_folder = drive.find_folder_by_name(self.service, cfg["drive"]["books"], root_id)
        if not books_folder:
            self.report.append(("ERROR", "Books", f"folder '{cfg['drive']['books']}' not found"))
            return

        folder_map = {k.lower(): v for k, v in cfg["languages"]["folders"].items()}
        allowed_tags = cfg["languages"]["filename_tags"]

        for book_folder in drive.list_children(self.service, books_folder):
            if book_folder["mimeType"] != "application/vnd.google-apps.folder":
                continue
            self.sync_book(book_folder, folder_map, allowed_tags)

    def sync_book(self, book_folder: dict, folder_map: dict, allowed_tags: list[str]) -> None:
        name = book_folder["name"]
        tag = lang_mod.filename_tag(name, allowed_tags)
        book_slug = lang_mod.slugify(tag_re.sub("", name).strip() or name)
        hint = folder_map.get(name.lower())

        children = [c for c in drive.list_children(self.service, book_folder["id"])
                    if c["mimeType"] in (DOC_MIME,)
                    or c["name"].lower().endswith((".docx", ".pdf", ".jpg", ".jpeg", ".png"))]
        files = [c for c in children if not c["name"].lower().endswith((".jpg", ".jpeg", ".png"))]
        files.sort(key=lambda c: c["name"])
        cover_file = next((c for c in children
                           if c["name"].lower().endswith((".jpg", ".jpeg", ".png"))), None)

        book_dir = self.books_out / book_slug
        book_dir.mkdir(parents=True, exist_ok=True)

        # cover -> public assets
        cover_url = None
        if cover_file:
            data = drive.download_file(self.service, cover_file["id"])
            ext = Path(cover_file["name"]).suffix.lstrip(".").lower() or "jpg"
            self.assets_out.mkdir(parents=True, exist_ok=True)
            cover_name = f"cover-{book_slug}.{ext}"
            (self.assets_out / cover_name).write_bytes(data)
            cover_url = f"/assets-sync/{cover_name}"

        chapters_meta = []
        any_body = ""
        book_lang = tag or hint
        for order, f in enumerate(files):
            raw = self._fetch_content(f)
            if raw is None:
                continue
            checksum = md5(raw[0])
            cached = self.cache.get(f["id"], {})
            if (cached.get("hash") == checksum
                    and cached.get("mtime") == f.get("modifiedTime")):
                self.report.append(("unchanged", f["name"], "chapter already synced"))
                continue

            if f["mimeType"] == DOC_MIME:
                body_md, _ = converters.html_to_markdown(
                    raw[0].decode("utf-8", "replace"), self.assets_out)
            elif f["name"].lower().endswith(".docx"):
                body_md, _ = converters.convert_docx(raw[0], self.assets_out)
            else:
                body_md, _ = converters.convert_pdf(raw[0])

            chapter_title = tag_re.sub("", converters.derive_title(
                body_md, Path(f["name"]).stem)).strip() or Path(f["name"]).stem
            chapter_lang = lang_mod.detect_lang(
                body_md + " " + chapter_title, hint, lang_mod.filename_tag(f["name"], allowed_tags))
            book_lang = book_lang or chapter_lang
            any_body = any_body or body_md
            ch_slug = f"{order:02d}-{lang_mod.slugify(chapter_title, f'chapter-{order}')}"
            ch_meta = {
                "book": book_slug,
                "title": chapter_title,
                "order": order,
                "lang": chapter_lang,
                "status": "draft",
                "driveFile": f["id"],
            }
            ch_path = book_dir / f"{ch_slug}.md"
            old = parse_frontmatter(ch_path)
            if old.get("status"):
                ch_meta["status"] = old["status"]
            ch_path.write_text(dump_frontmatter(ch_meta) + "\n" + body_md + "\n", encoding="utf-8")
            self.cache[f["id"]] = {"hash": checksum, "mtime": f.get("modifiedTime"),
                                   "out": str(ch_path.relative_to(ROOT))}
            self.report.append(("updated" if old else "NEW", f"📖 {name} → {chapter_title}",
                                f"lang={chapter_lang}"))

        if not files:
            self.report.append(("SKIP", name, "no chapter documents in folder"))
            return

        book_meta = {
            "title": tag_re.sub("", name).strip() or name,
            "description": snippet_from_md(any_body) if any_body else "",
            "author": self.cfg.get("review", {}).get("author", "Saif Ullah"),
            "lang": book_lang or "en",
            "tags": [],
            "status": "draft",
            "pubDate": (book_folder.get("modifiedTime") or now_iso())[:10],
            "driveFolder": book_folder["id"],
        }
        if cover_url:
            book_meta["cover"] = cover_url
        old_book = parse_frontmatter(book_dir / "book.yaml")
        if old_book.get("status"):
            book_meta["status"] = old_book["status"]
        (book_dir / "book.yaml").write_text(
            yaml.safe_dump(book_meta, allow_unicode=True, sort_keys=False, width=100),
            encoding="utf-8")
        self.report.append(("updated" if old_book else "NEW", f"📕 {name}",
                            f"{len(files)} chapters, lang={book_meta['lang']}"))

    # -------------------------------------------------- report
    def write_report(self) -> Path:
        report_path = ROOT / self.cfg["paths"]["report"]
        lines = [f"# Pull report — {now_iso()}", ""]
        for action, item, note in self.report:
            icon = {"NEW": "🟢", "updated": "🟡", "unchanged": "⚪",
                    "SKIP": "⚪", "ERROR": "🔴"}.get(action, "•")
            lines.append(f"- {icon} **{action}** — {item}  \n  {note}")
        lines.append("")
        lines.append("Drafts are NOT published. Run `python sync/review.py` to approve.")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines), encoding="utf-8")
        drive.save_cache(self.cache)
        return report_path


tag_re = __import__("re").compile(r"\s*\[[a-z]{2,3}\]\s*", re.IGNORECASE)


def main() -> int:
    use_images = "--no-images" not in sys.argv
    cfg = load_config()
    syncer = Syncer(cfg, use_images)

    log("🔑 Authenticating with Google Drive (browser opens on first run)…")
    try:
        syncer.service = drive.get_service()
    except SystemExit as exc:
        log(str(exc))
        return 2

    log("📚 Syncing books…")
    syncer.sync_books()
    log("📝 Syncing articles…")
    syncer.sync_articles()

    report = syncer.write_report()
    counts: dict[str, int] = {}
    for action, _, _ in syncer.report:
        counts[action] = counts.get(action, 0) + 1
    log("")
    log("Summary: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    log(f"Report:  {report}")
    log("Next:    python sync/review.py  →  http://127.0.0.1:5555")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
