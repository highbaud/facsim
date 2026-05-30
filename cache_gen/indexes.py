"""Generate the four root discovery files: llms.txt, sitemap.xml, robots.txt,
and the HTML index (table of contents)."""

from __future__ import annotations

import html as html_lib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from xml.sax.saxutils import escape as xml_escape

from .render import RenderedPage, output_paths
from .theme import FONT_LINK, LOGO_DEFS, wordmark as _wordmark


def _tree(pages: list[RenderedPage]) -> dict:
    """Build a nested folder tree keyed by path segment."""
    root: dict = {"_pages": [], "_folders": {}}
    for p in sorted(pages, key=lambda x: x.path):
        segs = [s for s in p.path.strip("/").split("/") if s]
        node = root
        for seg in segs[:-1]:
            node = node["_folders"].setdefault(seg, {"_pages": [], "_folders": {}})
        node["_pages"].append(p)
    return root


def _short_desc(p: RenderedPage, limit: int = 140) -> str:
    """A one-line description for a page: prefer the LLM summary, then the meta
    description. Collapsed to a single line and truncated."""
    text = (p.summary or p.description or "").strip()
    if not text:
        return ""
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def build_llms_txt(pages: list[RenderedPage], cfg: dict) -> str:
    cache = cfg["cache"]
    base = cache["base_url"].rstrip("/")
    lines: list[str] = []
    lines.append(f"# LLM-Optimized Content Cache: {cache['site_name']}")
    lines.append("")
    lines.append(f"> Source: {cfg['source']['base_url']}")
    lines.append(f"> Cache: {cache['base_url']}")
    lines.append(f"> Pages: {len(pages)}")
    lines.append(f"> Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    lines.append(f"> Formats: HTML (/path/index.html), Markdown (/path/content.md)")
    lines.append(f"> Audiences: {', '.join(cache.get('audiences', []))}")
    lines.append("")

    def emit(node: dict, depth: int):
        for p in node["_pages"]:
            html_rel, _ = output_paths(p.path)
            indent = "  " * depth
            desc = _short_desc(p)
            suffix = f": {desc}" if desc else ""
            lines.append(f"{indent}- [{p.title}]({html_rel}){suffix}")
        for name in sorted(node["_folders"]):
            indent = "  " * depth
            lines.append(f"{indent}### {name}/")
            emit(node["_folders"][name], depth + 1)

    emit(_tree(pages), 0)

    # Trailing guidance sections — how to consume the cache.
    lines.append("")
    lines.append("## Access & formats")
    lines.append("- Every page is mirrored as clean HTML (`/path/index.html`) and "
                 "Markdown (`/path/content.md`).")
    lines.append(f"- Full corpus in one file: {base}/llms-full.txt")
    lines.append(f"- RAG-ready records (one JSON per line): {base}/corpus.jsonl")
    lines.append(f"- Sitemap: {base}/sitemap.xml")
    lines.append(f"- Crawler policy: {base}/robots.txt")
    lines.append("")
    lines.append("## Recommended use")
    lines.append("- For retrieval/RAG: ingest `corpus.jsonl` or fetch `content.md` per page.")
    lines.append("- For a single-pass read of the whole site: fetch `llms-full.txt`.")
    lines.append("- Each page embeds Schema.org JSON-LD (WebPage, BreadcrumbList, "
                 "and FAQPage where available).")
    lines.append("")
    lines.append("## Notes")
    lines.append("- All pages carry `noindex,nofollow` plus a canonical link to the "
                 "original source, so this cache is search-neutral.")
    lines.append(f"- Content is mirrored from {cfg['source']['base_url']} and may lag "
                 "the live site.")
    lines.append("")
    return "\n".join(lines)


def build_llms_full_txt(pages: list[RenderedPage], cfg: dict) -> str:
    cache = cfg["cache"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out: list[str] = []
    out.append(f"# {cache['site_name']} — full content cache")
    out.append(
        f"> Source: {cfg['source']['base_url']} · Pages: {len(pages)} · Generated: {now}"
    )
    out.append("")
    for p in sorted(pages, key=lambda x: x.path):
        out.append("=" * 72)
        out.append(f"## {p.title}")
        out.append(f"Source: {p.canonical_url}")
        if p.breadcrumbs:
            out.append("Path: " + " > ".join(p.breadcrumbs))
        if p.summary:
            out.append(f"TL;DR: {p.summary}")
        out.append("")
        out.append(p.body_md.strip())
        out.append("")
    return "\n".join(out) + "\n"


def build_corpus_jsonl(pages: list[RenderedPage], cfg: dict) -> str:
    base = cfg["cache"]["base_url"].rstrip("/")
    rows: list[str] = []
    for p in sorted(pages, key=lambda x: x.path):
        html_rel, md_rel = output_paths(p.path)
        record = {
            "url": p.canonical_url,
            "cache_html": f"{base}/{html_rel}",
            "cache_markdown": f"{base}/{md_rel}",
            "title": p.title,
            "breadcrumbs": p.breadcrumbs,
            "description": p.description,
            "word_count": p.word_count,
            "summary": p.summary,
            "faqs": p.faqs,
            "text": p.body_md,
        }
        rows.append(json.dumps(record, ensure_ascii=False))
    return "\n".join(rows) + "\n"


def build_sitemap_xml(pages: list[RenderedPage], cfg: dict) -> str:
    base = cfg["cache"]["base_url"].rstrip("/")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = ['<?xml version="1.0" encoding="UTF-8"?>']
    out.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for p in sorted(pages, key=lambda x: x.path):
        html_rel, _ = output_paths(p.path)
        loc = f"{base}/{html_rel}"
        out.append("  <url>")
        out.append(f"    <loc>{xml_escape(loc)}</loc>")
        out.append(f"    <lastmod>{now}</lastmod>")
        out.append("  </url>")
    out.append("</urlset>")
    out.append("")
    return "\n".join(out)


def build_robots_txt(cfg: dict) -> str:
    base = cfg["cache"]["base_url"].rstrip("/")
    return (
        "# Cache mirror. Welcomes AI crawlers and search engines.\n"
        "# Pages carry noindex/nofollow + canonical to the original source,\n"
        "# so search engines attribute ranking to the canonical site.\n"
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )


def build_htaccess(cfg: dict) -> str:
    d = cfg.get("deploy") or {}
    html_s = int(d.get("cache_html_seconds", 3600))
    asset_s = int(d.get("cache_asset_seconds", 86400))
    return f"""# Generated by facsim — correct content types + caching for Apache.
AddDefaultCharset utf-8
AddType text/markdown .md
AddType application/x-ndjson .jsonl
AddCharset utf-8 .txt .md .jsonl

Options -Indexes
DirectoryIndex index.html

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus {html_s} seconds"
  ExpiresByType text/markdown "access plus {html_s} seconds"
  ExpiresByType application/x-ndjson "access plus {html_s} seconds"
  ExpiresByType text/plain "access plus {html_s} seconds"
  ExpiresByType application/xml "access plus {html_s} seconds"
  ExpiresByType text/css "access plus {asset_s} seconds"
</IfModule>
"""


def build_manifest(cfg: dict, files: dict[str, str], page_count: int) -> str:
    """A build fingerprint: every output file mapped to its content hash, used
    by --diff-against to report what changed between rebuilds."""
    manifest = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": cfg["source"]["base_url"],
        "cache": cfg["cache"]["base_url"],
        "pages": page_count,
        "files": dict(sorted(files.items())),
    }
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


# Preferred display order for content-type sections; anything else sorts
# after these, alphabetically.
_SECTION_ORDER = ["Pages", "Insights & Articles", "Services", "Docs",
                  "Products", "Team", "Funnels"]

# Per-section emoji + one-line subtitle for the index
# (emoji-prefixed section headers with a descriptive subtitle + page count).
_SECTION_META: dict[str, tuple[str, str]] = {
    "Pages": ("📑", "Core institutional and informational pages."),
    "Insights & Articles": ("📝", "Long-form articles, insights, and editorial pieces."),
    "Services": ("🧭", "Service lines and what the firm offers."),
    "Docs": ("📚", "Documentation and reference material."),
    "Products": ("🛍️", "Product and offering pages."),
    "Team": ("👥", "People, advisors, and team profiles."),
    "Funnels": ("🎯", "Campaign and conversion pages."),
}
_DEFAULT_META = ("🗂️", "")


def _section_label(p: RenderedPage) -> str:
    return getattr(p, "section", "") or "Pages"


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "section"


def build_index_html(
    pages: list[RenderedPage], cfg: dict, logo_svg: str | None = None
) -> str:
    cache = cfg["cache"]
    esc = html_lib.escape
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    site_name = cache["site_name"]
    brand = cache.get("brand") or site_name
    source_url = cfg["source"]["base_url"]

    # Group pages by content-type section (derived from the source sitemap).
    groups: dict[str, list[RenderedPage]] = defaultdict(list)
    for p in pages:
        groups[_section_label(p)].append(p)

    def order_key(name: str) -> tuple[int, str]:
        return (_SECTION_ORDER.index(name) if name in _SECTION_ORDER
                else len(_SECTION_ORDER), name.lower())
    ordered = sorted(groups, key=order_key)

    # If everything landed in a single section, the section headers add noise —
    # render a flat list instead.
    show_headers = len(ordered) > 1

    # Build the page tree (folder headers + rows) and, in parallel, the list of
    # content-section entries for the table of contents.
    blocks: list[str] = []
    toc_sections: list[tuple[str, str, int, str]] = []  # emoji, name, count, anchor
    for section in ordered:
        items = sorted(groups.get(section, []), key=lambda x: x.title.lower())
        if not items:
            continue
        emoji, subtitle = _SECTION_META.get(section, _DEFAULT_META)
        anchor = "sec-" + _slug(section)
        if show_headers:
            toc_sections.append((emoji, section, len(items), anchor))
            sub_html = (
                f'<span class="folder-sub">{esc(subtitle)}</span>' if subtitle else ""
            )
            blocks.append(
                f'<li class="folder" id="{anchor}" data-folder>'
                f'<span class="sec-ico" aria-hidden="true">{emoji}</span>'
                f'<span class="f-name">{esc(section)}</span>'
                f'<span class="count">{len(items)}</span>{sub_html}</li>'
            )
        for p in items:
            html_rel, md_rel = output_paths(p.path)
            desc = _short_desc(p, 150)
            desc_html = f'<span class="desc">{esc(desc)}</span>' if desc else ""
            blocks.append(
                f'<li class="row" data-search="{esc((p.title + " " + p.path).lower())}">'
                f'<a class="title" href="{esc(html_rel)}">{esc(p.title)}</a>'
                f"{desc_html}"
                f'<span class="meta">'
                f'<a href="{esc(md_rel)}">markdown</a>'
                f'<a href="{esc(p.canonical_url)}">source &#8599;</a>'
                f"</span></li>"
            )

    n = len(pages)
    folder_count = len(ordered)
    total_words = sum(p.word_count for p in pages)
    with_tldr = sum(1 for p in pages if p.summary)
    tldr_pct = round(100 * with_tldr / n) if n else 0

    # ---- Table of contents -------------------------------------------------
    toc_items = ['<li><a href="#about"><span>📂 About this cache</span></a></li>']
    for emoji, name, cnt, anchor in toc_sections:
        toc_items.append(
            f'<li><a href="#{anchor}"><span>{emoji} {esc(name)}</span>'
            f'<span class="n">{cnt}</span></a></li>'
        )
    toc_items.append('<li><a href="#index"><span>🗂️ Full page index</span></a></li>')
    toc_items.append('<li><a href="#resources"><span>🤖 Machine-readable resources</span></a></li>')
    toc_items.append('<li><a href="#seo"><span>🛡️ SEO-neutral design</span></a></li>')
    toc_items.append('<li><a href="#methodology"><span>🔬 Optimization methodology</span></a></li>')
    toc_items.append('<li><a href="#usage"><span>📖 Usage guidelines</span></a></li>')
    toc_items.append('<li><a href="#statistics"><span>📊 Cache statistics</span></a></li>')
    toc_html = "\n      ".join(toc_items)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LLM-Optimized Content Cache: {esc(site_name)}</title>
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{esc(source_url)}">
<meta name="description" content="LLM-optimized content cache of {esc(site_name)} — clean HTML + markdown for AI and RAG.">
{FONT_LINK}
<link rel="stylesheet" href="/cache.css">
</head>
<body>
{LOGO_DEFS}
<main class="wrap">
  <header class="masthead">
    <div class="brandline">
      {_wordmark(brand, "dark", logo_svg)}
      <span class="divider"></span>
      <span class="brand-sub">LLM Cache</span>
    </div>
    <p class="eyebrow">LLM-Optimized Content Cache</p>
    <h1>LLM-Optimized <span class="accent">Content Cache</span></h1>
    <p class="masthead-site">{esc(site_name)}</p>
    <p class="lede">Every page from the live site, republished as clean HTML and raw
      markdown for large-language-model and RAG consumption. Canonical tags point
      back to the source, so this cache is search-neutral.</p>
    <nav class="index-pill" aria-label="Machine indexes">
      <a href="llms.txt">llms.txt</a>
      <a href="llms-full.txt">llms-full.txt</a>
      <a href="corpus.jsonl">corpus.jsonl</a>
      <a href="sitemap.xml">sitemap.xml</a>
      <a href="robots.txt">robots.txt</a>
    </nav>
  </header>

  <section class="stats" aria-label="Cache summary">
    <div class="stat"><div class="num">{n}</div><div class="label">Pages cached</div></div>
    <div class="stat"><div class="num">{total_words:,}</div><div class="label">Total words</div></div>
    <div class="stat"><div class="num">{folder_count}</div><div class="label">Sections</div></div>
    <div class="stat"><div class="num">{updated}</div><div class="label">Last built (UTC)</div></div>
  </section>

  <section class="doc-section" id="about">
    <h2><span class="sec-ico" aria-hidden="true">📂</span> About this cache</h2>
    <p>This is an LLM-optimized mirror of <a href="{esc(source_url)}">{esc(site_name)}</a>.
      Every page from the live site is republished as clean, semantic HTML and as raw
      Markdown, with structured data and machine indexes, so AI systems can read it
      without wading through navigation, scripts, and layout noise.</p>
    <p>Built for:</p>
    <ul>
      <li>Retrieval-augmented generation (RAG) and semantic search</li>
      <li>Model training and fine-tuning corpora</li>
      <li>Knowledge-graph construction and content analysis</li>
    </ul>
  </section>

  <nav class="toc" id="toc" aria-label="Table of contents">
    <h2><span class="sec-ico" aria-hidden="true">📋</span> Table of contents</h2>
    <ul>
      {toc_html}
    </ul>
  </nav>

  <section class="index-card" id="index">
    <div class="index-head">
      <h2><span class="sec-ico" aria-hidden="true">🗂️</span> Full page index</h2>
      <input class="search" id="filter" type="search" placeholder="Filter pages…"
        aria-label="Filter pages by title" autocomplete="off">
    </div>
    <ul class="tree" id="tree">
{chr(10).join(blocks)}
      <li class="empty" id="noresults" hidden>No pages match that filter.</li>
    </ul>
  </section>

  <section class="doc-section" id="resources">
    <h2><span class="sec-ico" aria-hidden="true">🤖</span> Machine-readable resources</h2>
    <ul class="resources">
      <li><a class="r-name" href="llms.txt">llms.txt</a>
        <span class="r-desc">Hierarchical index of every page with per-link descriptions and consumption guidance.</span></li>
      <li><a class="r-name" href="llms-full.txt">llms-full.txt</a>
        <span class="r-desc">The entire corpus concatenated into one file for a single-pass read.</span></li>
      <li><a class="r-name" href="corpus.jsonl">corpus.jsonl</a>
        <span class="r-desc">One RAG-ready JSON record per page — title, URLs, breadcrumbs, summary, FAQs, and text.</span></li>
      <li><a class="r-name" href="sitemap.xml">sitemap.xml</a>
        <span class="r-desc">Machine sitemap of every cached page.</span></li>
      <li><a class="r-name" href="robots.txt">robots.txt</a>
        <span class="r-desc">Permissive crawler policy welcoming AI and search bots.</span></li>
    </ul>
  </section>

  <section class="doc-section" id="seo">
    <h2><span class="sec-ico" aria-hidden="true">🛡️</span> SEO-neutral design</h2>
    <p>This mirror is built to add zero search-ranking pressure to the source. Every
      page carries <code>noindex, nofollow</code> and a <code>canonical</code> link
      pointing back to the original URL, so search engines attribute all authority to
      {esc(site_name)} rather than to the cache.</p>
  </section>

  <section class="doc-section" id="methodology">
    <h2><span class="sec-ico" aria-hidden="true">🔬</span> Optimization methodology</h2>
    <ul>
      <li><strong>Noise removal.</strong> Navigation, headers, footers, forms, and
        cookie banners are stripped — only the main content is kept.</li>
      <li><strong>Clean dual format.</strong> Each page is published as semantic HTML
        and as raw Markdown (<code>content.md</code>).</li>
      <li><strong>Structured data.</strong> Every page embeds Schema.org WebPage and
        BreadcrumbList JSON-LD, plus FAQPage where a FAQ is generated.</li>
      <li><strong>Per-page LLM layer.</strong> An optional TL;DR and FAQ summarise each
        page for faster retrieval — a layer the source site does not expose.</li>
    </ul>
  </section>

  <section class="doc-section" id="usage">
    <h2><span class="sec-ico" aria-hidden="true">📖</span> Usage guidelines</h2>
    <ul>
      <li><strong>Intended use.</strong> Training data, retrieval-augmented generation,
        semantic search, and content analysis.</li>
      <li><strong>Attribution.</strong> Cite the canonical source URL shown on each page,
        not the cache URL.</li>
      <li><strong>Freshness.</strong> Content is mirrored periodically and may lag the
        live site; verify time-sensitive details against the source.</li>
    </ul>
  </section>

  <section class="doc-section" id="statistics">
    <h2><span class="sec-ico" aria-hidden="true">📊</span> Cache statistics</h2>
    <div class="stat-tables">
      <table class="stat-table">
        <caption>Collection overview</caption>
        <tbody>
          <tr><th>Total pages</th><td>{n}</td></tr>
          <tr><th>Sections</th><td>{folder_count}</td></tr>
          <tr><th>Total words</th><td>{total_words:,}</td></tr>
          <tr><th>Last built (UTC)</th><td>{updated}</td></tr>
        </tbody>
      </table>
      <table class="stat-table">
        <caption>Quality &amp; coverage</caption>
        <tbody>
          <tr><th>Formats per page</th><td>2</td></tr>
          <tr><th>Structured data (JSON-LD)</th><td>100%</td></tr>
          <tr><th>SEO-neutral (noindex + canonical)</th><td>100%</td></tr>
          <tr><th>Pages with TL;DR</th><td>{tldr_pct}%</td></tr>
        </tbody>
      </table>
    </div>
  </section>
</main>

<footer class="site-foot">
  <div class="wrap">
    <p class="statement">Built for machines to read, attributed to the source to rank.</p>
    <p class="fine">Mirror of <a href="{esc(source_url)}">{esc(site_name)}</a>
      &middot; {n} pages &middot; {total_words:,} words &middot; all pages
      noindex/nofollow with canonical to source &middot; built {updated} UTC.</p>
    <p class="fine poweredby">Powered by <strong><a href="https://github.com/highbaud/facsim">Facsim</a></strong>.</p>
  </div>
</footer>

<script>
(function () {{
  var input = document.getElementById('filter');
  var tree = document.getElementById('tree');
  var empty = document.getElementById('noresults');
  var rows = Array.prototype.slice.call(tree.querySelectorAll('.row'));
  var folders = Array.prototype.slice.call(tree.querySelectorAll('.folder'));
  input.addEventListener('input', function () {{
    var q = input.value.trim().toLowerCase();
    var shown = 0;
    rows.forEach(function (r) {{
      var hit = !q || r.getAttribute('data-search').indexOf(q) !== -1;
      r.hidden = !hit;
      if (hit) shown++;
    }});
    // Hide a folder header when all its rows are hidden.
    folders.forEach(function (f) {{
      var el = f.nextElementSibling, anyVisible = false;
      while (el && !el.classList.contains('folder') && el.id !== 'noresults') {{
        if (el.classList.contains('row') && !el.hidden) anyVisible = true;
        el = el.nextElementSibling;
      }}
      f.hidden = !anyVisible;
    }});
    empty.hidden = shown !== 0;
  }});
}})();
</script>
</body>
</html>
"""
