"""Render the two per-page artifacts: clean HTML and content.md."""

from __future__ import annotations

import html as html_lib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

import markdown as md_lib

from .extract import Extracted
from .enrich import Enrichment, EMPTY
from .theme import FONT_LINK, LOGO_DEFS, wordmark as _wordmark


@dataclass
class RenderedPage:
    path: str                 # source path (leading slash)
    title: str
    canonical_url: str        # original source URL
    html: str
    markdown: str             # full content.md file body (frontmatter + markdown)
    description: str = ""
    breadcrumbs: list[str] = field(default_factory=list)
    word_count: int = 0
    body_md: str = ""         # clean markdown body only (no frontmatter)
    summary: str = ""         # optional LLM TL;DR
    faqs: list[dict] = field(default_factory=list)  # optional LLM FAQ pairs
    section: str = "Pages"    # content-type group for the index (from sitemap)


def _output_subpath(path: str) -> str:
    """Map a source path to the cache output directory (without filename)."""
    if path in ("", "/"):
        return ""
    return path.strip("/")


def breadcrumb_jsonld(breadcrumbs: list[str], source_base: str, path: str) -> dict:
    items = []
    acc = source_base.rstrip("/")
    segments = [s for s in path.strip("/").split("/") if s]
    # First crumb ("Home") maps to the source root.
    items.append(
        {
            "@type": "ListItem",
            "position": 1,
            "name": breadcrumbs[0],
            "item": source_base.rstrip("/") + "/",
        }
    )
    for i, seg in enumerate(segments, start=1):
        acc = f"{acc}/{seg}"
        name = breadcrumbs[i] if i < len(breadcrumbs) else seg
        items.append(
            {"@type": "ListItem", "position": i + 1, "name": name, "item": acc}
        )
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


def webpage_jsonld(title: str, description: str, canonical_url: str) -> dict:
    data = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "url": canonical_url,
    }
    if description:
        data["description"] = description
    return data


def faqpage_jsonld(faqs: list[dict]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f["q"],
                "acceptedAnswer": {"@type": "Answer", "text": f["a"]},
            }
            for f in faqs
        ],
    }


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{canonical}">
{description_meta}{font_link}
<link rel="stylesheet" href="/cache.css">
<script type="application/ld+json">
{webpage_ld}
</script>
<script type="application/ld+json">
{breadcrumb_ld}
</script>
{faq_ld}</head>
<body>
{logo_defs}
<header class="site-head wrap">
  <a class="brandline" href="/" aria-label="{brand} LLM Cache home">
    {wordmark}
    <span class="divider"></span>
    <span class="brand-sub">LLM Cache</span>
  </a>
</header>
<main class="wrap reader">
<nav class="breadcrumb" aria-label="Breadcrumb">{breadcrumb_text}</nav>
<div class="page-meta">{meta_box}</div>
{tldr_block}<article>
{body}
</article>
{faq_block}</main>
<footer class="site-foot">
<div class="wrap">
<p class="fine">Cached copy for LLM / RAG use &middot;
canonical source: <a href="{canonical}">{canonical}</a> &middot;
<a href="content.md">markdown version</a></p>
</div>
</footer>
</body>
</html>
"""


def _markdown_to_html(markdown: str) -> str:
    return md_lib.markdown(
        markdown,
        extensions=["extra", "sane_lists", "smarty", "tables"],
        output_format="html",
    )


def _meta_box(ext: Extracted, canonical_url: str) -> str:
    esc = html_lib.escape
    built = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    parts = [f"{ext.word_count:,} words", f"cached {built}"]
    parts.append(f'<a href="content.md">markdown</a>')
    parts.append(f'<a href="{esc(canonical_url)}">source &#8599;</a>')
    return " &middot; ".join(parts)


def _tldr_block(summary: str) -> str:
    if not summary:
        return ""
    return (
        '<aside class="tldr">'
        '<p class="label">TL;DR</p>'
        f"<p>{html_lib.escape(summary)}</p>"
        "</aside>\n"
    )


def _faq_block(faqs: list[dict]) -> str:
    if not faqs:
        return ""
    esc = html_lib.escape
    items = "".join(
        f"<dt>{esc(f['q'])}</dt><dd>{esc(f['a'])}</dd>" for f in faqs
    )
    return (
        '<section class="faq" aria-label="Frequently asked questions">'
        "<h2>Frequently asked</h2>"
        f"<dl>{items}</dl>"
        "</section>\n"
    )


def render_page(
    ext: Extracted,
    path: str,
    canonical_url: str,
    source_base: str,
    enrichment: Enrichment = EMPTY,
    section: str = "Pages",
    brand: str = "LLM Cache",
    logo_svg: str | None = None,
) -> RenderedPage:
    description_meta = (
        f'<meta name="description" content="{html_lib.escape(ext.description)}">\n'
        if ext.description
        else ""
    )
    breadcrumb_text = " &rsaquo; ".join(html_lib.escape(c) for c in ext.breadcrumbs)
    body_html = _markdown_to_html(ext.markdown)

    faq_ld = ""
    if enrichment.faqs:
        faq_ld = (
            '<script type="application/ld+json">\n'
            + json.dumps(faqpage_jsonld(enrichment.faqs), indent=2)
            + "\n</script>\n"
        )

    page_html = HTML_TEMPLATE.format(
        title=html_lib.escape(ext.title),
        canonical=html_lib.escape(canonical_url),
        description_meta=description_meta,
        font_link=FONT_LINK,
        logo_defs=LOGO_DEFS,
        brand=html_lib.escape(brand),
        wordmark=_wordmark(brand, "dark", logo_svg),
        webpage_ld=json.dumps(
            webpage_jsonld(ext.title, ext.description, canonical_url), indent=2
        ),
        breadcrumb_ld=json.dumps(
            breadcrumb_jsonld(ext.breadcrumbs, source_base, path), indent=2
        ),
        faq_ld=faq_ld,
        breadcrumb_text=breadcrumb_text,
        meta_box=_meta_box(ext, canonical_url),
        tldr_block=_tldr_block(enrichment.summary),
        body=body_html,
        faq_block=_faq_block(enrichment.faqs),
    )

    # content.md: YAML frontmatter + clean markdown body.
    frontmatter = [
        "---",
        f"title: {_yaml_str(ext.title)}",
        f"source_url: {canonical_url}",
    ]
    if ext.description:
        frontmatter.append(f"description: {_yaml_str(ext.description)}")
    frontmatter.append(f"breadcrumbs: {json.dumps(ext.breadcrumbs)}")
    frontmatter.append(f"word_count: {ext.word_count}")
    if enrichment.summary:
        frontmatter.append(f"summary: {_yaml_str(enrichment.summary)}")
    if enrichment.faqs:
        frontmatter.append(f"faqs: {json.dumps(enrichment.faqs, ensure_ascii=False)}")
    frontmatter.append("---")
    md_doc = "\n".join(frontmatter) + "\n\n" + ext.markdown + "\n"

    return RenderedPage(
        path=path,
        title=ext.title,
        canonical_url=canonical_url,
        html=page_html,
        markdown=md_doc,
        description=ext.description,
        breadcrumbs=ext.breadcrumbs,
        word_count=ext.word_count,
        body_md=ext.markdown,
        summary=enrichment.summary,
        faqs=enrichment.faqs,
        section=section or "Pages",
    )


def _yaml_str(s: str) -> str:
    """Quote a YAML scalar safely."""
    return json.dumps(s, ensure_ascii=False)


def output_paths(path: str) -> tuple[str, str]:
    """Return (html_relpath, md_relpath) for a source path."""
    sub = _output_subpath(path)
    if sub:
        return f"{sub}/index.html", f"{sub}/content.md"
    return "index.html", "content.md"
