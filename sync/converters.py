"""Convert Google Docs / Word / PDF files into clean, site-ready markdown.

- Google Docs  -> exported HTML -> whitelisted, cleaned
- .docx        -> mammoth (semantic HTML, embedded images extracted)
- .pdf         -> text extracted for the body; original kept as attachment
"""
from __future__ import annotations

import base64
import hashlib
import html as html_mod
import re
from io import BytesIO
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ALLOWED_TAGS = {
    "p", "h1", "h2", "h3", "h4", "strong", "b", "em", "i", "u", "s",
    "ul", "ol", "li", "blockquote", "table", "thead", "tbody", "tr",
    "th", "td", "a", "br", "hr", "img", "figure", "figcaption", "code",
    "pre", "sup", "sub",
}


def _img_key(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()[:12]


def _save_image(data: bytes, assets_dir: Path, ext: str = "png") -> str:
    """Persist image bytes and return the site-relative URL to use in markdown."""
    assets_dir.mkdir(parents=True, exist_ok=True)
    name = f"{_img_key(data)}.{ext}"
    path = assets_dir / name
    if not path.exists():
        path.write_bytes(data)
    return f"/assets-sync/{name}"


def _node_to_md(node, assets_dir: Path, images: list[dict]) -> str:
    if isinstance(node, NavigableString):
        return str(node)
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    inner = "".join(_node_to_md(c, assets_dir, images) for c in node.children)

    if name in ("h1", "h2", "h3", "h4"):
        level = {"h1": "##", "h2": "##", "h3": "###", "h4": "####"}[name]
        text = inner.strip()
        return f"\n\n{level} {text}\n\n" if text else ""
    if name == "p":
        text = inner.strip()
        return f"\n\n{text}\n\n" if text else ""
    if name in ("strong", "b"):
        return f"**{inner.strip()}**" if inner.strip() else ""
    if name in ("em", "i"):
        return f"*{inner.strip()}*" if inner.strip() else ""
    if name == "u":
        return inner
    if name in ("s", "del"):
        return f"~~{inner.strip()}~~" if inner.strip() else ""
    if name in ("sup", "sub", "code"):
        return inner
    if name == "br":
        return "  \n"
    if name == "hr":
        return "\n\n---\n\n"
    if name == "blockquote":
        text = inner.strip()
        if not text:
            return ""
        quoted = "\n".join(f"> {line}" for line in text.splitlines())
        return f"\n\n{quoted}\n\n"
    if name in ("ul", "ol"):
        return inner  # li handled below emits markers
    if name == "li":
        # find list index by scanning preceding siblings
        idx, marker = 1, "-"
        if node.parent and node.parent.name == "ol":
            idx = sum(1 for s in node.previous_siblings
                      if isinstance(s, Tag) and s.name == "li") + 1
            marker = f"{idx}."
        return f"\n- {inner.strip()}" if marker == "-" else f"\n{marker} {inner.strip()}"
    if name == "table":
        return _table_to_md(node, assets_dir, images)
    if name == "a":
        href = node.get("href", "")
        if href.startswith("#"):
            return inner
        return f"[{inner.strip()}]({html_mod.escape(href, quote=True)})"
    if name == "img":
        src = node.get("src", "")
        data = None
        ext = "png"
        if src.startswith("data:"):
            header, b64 = src.split(",", 1)
            if "jpeg" in header or "jpg" in header:
                ext = "jpg"
            data = base64.b64decode(b64)
        elif src.startswith("http"):
            images.append({"remote": src, "kind": "embedded-remote"})
            return f"\n\n![image]({src})\n\n"
        if data:
            url = _save_image(data, assets_dir, ext)
            images.append({"local": url, "kind": "embedded"})
            alt = node.get("alt", "image")
            return f"\n\n![{alt}]({url})\n\n"
        return ""
    return inner


def _table_to_md(table: Tag, assets_dir: Path, images: list[dict]) -> str:
    rows: list[list[str]] = []
    for tr in table.find_all("tr"):
        cells = [
            " ".join(_node_to_md(c, assets_dir, images).split()) or " "
            for c in tr.find_all(["th", "td"])
        ]
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [" "] * (width - len(r)) for r in rows]
    head = "| " + " | ".join(rows[0]) + " |"
    sep = "|" + "|".join([" --- "] * width) + "|"
    body = "\n".join("| " + " | ".join(r) + " |" for r in rows[1:])
    return f"\n\n{head}\n{sep}\n{body}\n\n"


def html_to_markdown(html: str, assets_dir: Path) -> tuple[str, list[dict]]:
    """Clean an HTML document into markdown; returns (markdown, image_refs)."""
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "meta", "link", "head", "o:p"]):
        t.decompose()
    for span in soup.find_all("span"):
        span.unwrap()
    for el in soup.find_all(True):
        keep = {k for k in el.attrs if k in ("href", "src", "alt", "colspan", "rowspan")}
        el.attrs = {k: v for k, v in el.attrs.items() if k in keep}

    body = soup.body or soup
    images: list[dict] = []
    md = "".join(_node_to_md(c, assets_dir, images) for c in body.children)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md, images


def convert_docx(data: bytes, assets_dir: Path) -> tuple[str, list[dict]]:
    """Word document -> markdown via mammoth; embedded images extracted."""
    import mammoth

    images: list[dict] = []

    def image_handler(image):
        with image.open() as img:
            data = img.read()
        ext = "jpg" if image.content_type in ("image/jpeg", "image/jpg") else "png"
        url = _save_image(data, assets_dir, ext)
        images.append({"local": url, "kind": "embedded"})
        return {"src": url}

    result = mammoth.convert_to_markdown(
        BytesIO(data), convert_image=mammoth.images.img_element(image_handler))
    return result.value, images


def convert_pdf(data: bytes) -> tuple[str, list[dict]]:
    """PDF -> plain-ish markdown text (headings lost; original stays available)."""
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(data))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    text = "\n\n".join(parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip(), []


def derive_title(md: str, fallback: str) -> str:
    """First markdown heading if present, else the filename."""
    m = re.search(r"^##\s+(.+)$", md, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r"^(.{5,80})$", md.strip(), re.MULTILINE)
    if m:
        return m.group(1).strip()
    return fallback
