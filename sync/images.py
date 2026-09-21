"""Relevant free images via Pixabay (key) with Openverse (no key) fallback.

All photos are free-license; each carries a credit line rendered on the site.
"""
from __future__ import annotations

import re
import urllib.parse

import requests

from config import load_pixabay_key

_UA = {"User-Agent": "research-blog-sync/1.0 (personal blog enrichment)"}


def _keywords_from_text(text: str, max_kw: int = 5) -> list[str]:
    """Cheap keyword extraction: drop stopwords, keep longest content words."""
    stopwords = {
        "the", "and", "for", "from", "with", "that", "this", "into", "over",
        "what", "when", "where", "why", "how", "who", "its", "their", "about",
        "which", "have", "has", "had", "not", "are", "was", "were", "will",
        "would", "could", "should", "than", "then", "they", "them", "these",
        "those", "there", "here", "been", "being", "does", "did", "done",
    }
    words = re.findall(r"[A-Za-z\u00C0-\u024F]{4,}", text.lower())
    seen, out = set(), []
    for w in sorted(set(words), key=len, reverse=True):
        if w in stopwords or w in seen:
            continue
        seen.add(w)
        out.append(w)
        if len(out) >= max_kw:
            break
    return out or ["mountains", "river", "village"]


def _download(url: str, assets_dir, stem: str, ext: str = "jpg") -> str | None:
    try:
        resp = requests.get(url, timeout=30, headers=_UA)
        resp.raise_for_status()
        if len(resp.content) < 10_000:  # too small to be a usable photo
            return None
        assets_dir.mkdir(parents=True, exist_ok=True)
        path = assets_dir / f"{stem}.{ext}"
        path.write_bytes(resp.content)
        return f"/assets-sync/{path.name}"
    except Exception:
        return None


def _pixabay_search(query: str, key: str, per_page: int, safe: bool) -> list[dict]:
    try:
        r = requests.get(
            "https://pixabay.com/api/",
            params={"key": key, "q": query, "image_type": "photo",
                    "per_page": per_page, "safesearch": "true" if safe else "false"},
            timeout=20, headers=_UA)
        if r.status_code != 200:
            return []
        hits = r.json().get("hits", [])
        return [{"url": h.get("webformatURL") or h.get("largeImageURL"),
                 "credit": f"Pixabay / {h.get('user', 'unknown')}",
                 "page": h.get("pageURL", "")} for h in hits]
    except Exception:
        return []


def _openverse_search(query: str, per_page: int) -> list[dict]:
    try:
        r = requests.get(
            "https://api.openverse.org/v1/images/",
            params={"q": query, "page_size": per_page, "license_type": "all-cc"},
            timeout=20, headers=_UA)
        if r.status_code != 200:
            return []
        hits = r.json().get("results", [])
        return [{"url": h.get("url"), "credit": f"Openverse / {h.get('creator') or 'unknown'} ({h.get('license')})",
                 "page": h.get("foreign_landing_url", "")} for h in hits]
    except Exception:
        return []


def enrich_article_images(title: str, body_md: str, tags: list[str],
                          assets_dir, cfg: dict) -> dict:
    """Return {hero, credits[]} — hero inserted at top, others after headings.

    Never fails the pipeline: any error just means no images.
    """
    result = {"hero": None, "credits": []}
    try:
        provider_order = cfg.get("images", {}).get("provider_order", ["pixabay", "openverse"])
        max_body = int(cfg.get("images", {}).get("max_per_post", 3))
        per_page = int(cfg.get("images", {}).get("per_page", 12))
        safe = bool(cfg.get("images", {}).get("safe_search", True))

        query_terms = " ".join(_keywords_from_text(title + " " + " ".join(tags), 4))
        key = load_pixabay_key()
        pool: list[dict] = []
        for provider in provider_order:
            if provider == "pixabay" and key:
                pool = _pixabay_search(query_terms, key, per_page, safe)
            elif provider == "openverse":
                pool = _openverse_search(query_terms, per_page)
            if pool:
                break
        if not pool:
            return result

        result["hero"], pool = pool[0], pool[1:]
        if result["hero"]:
            result["credits"].append(result["hero"]["credit"])
            local = _download(result["hero"]["url"], assets_dir, "hero")
            if local:
                result["hero"]["local"] = local

        body_imgs = []
        for i, hit in enumerate(pool[:max_body]):
            local = _download(hit["url"], assets_dir, f"body-{i + 1}")
            if not local:
                continue
            result["credits"].append(hit["credit"])
            body_imgs.append((i, local, hit["credit"]))

        if body_imgs:
            lines = body_md.split("\n\n")
            heading_slots = [i for i, line in enumerate(lines) if line.startswith("## ")]
            for slot_i, (orig_i, local, credit) in enumerate(body_imgs):
                insert_at = heading_slots[slot_i] if slot_i < len(heading_slots) else None
                figure = (f"\n\n![relevant image]({local})\n\n"
                          f"*Photo: {credit} (free license)*\n\n")
                if insert_at:
                    lines[insert_at] = figure + lines[insert_at]
                else:
                    lines.append(figure)
            body_md = "\n\n".join(lines)

        result["body_md"] = body_md
        return result
    except Exception:
        result["body_md"] = body_md
        return result
