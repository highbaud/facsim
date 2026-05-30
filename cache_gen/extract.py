"""Extract main content from a page and convert it to markdown.

Primary extraction uses trafilatura (purpose-built boilerplate removal). If that
yields nothing usable, fall back to explicit CSS-selector + markdownify.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin

import trafilatura
from bs4 import BeautifulSoup
from markdownify import markdownify as md


@dataclass
class Extracted:
    title: str
    description: str          # meta description, may be ""
    markdown: str            # clean markdown body
    breadcrumbs: list[str]   # human-readable trail derived from the path
    word_count: int = 0      # approximate word count of the markdown body


def _meta(soup: BeautifulSoup, name: str, attr: str = "name") -> str:
    tag = soup.find("meta", attrs={attr: name})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return ""


def page_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return re.sub(r"\s+", " ", h1.get_text(" ", strip=True)).strip()
    og = _meta(soup, "og:title", attr="property")
    if og:
        return og
    if soup.title and soup.title.get_text(strip=True):
        # Strip a trailing " | Site Name" style suffix.
        return re.split(r"\s+[|\-–—]\s+", soup.title.get_text(strip=True))[0]
    return "Untitled"


def breadcrumbs_from_path(path: str) -> list[str]:
    if path in ("", "/"):
        return ["Home"]
    parts = [p for p in path.strip("/").split("/") if p]
    crumbs = ["Home"]
    for p in parts:
        label = re.sub(r"[-_]+", " ", p).strip()
        label = re.sub(r"\.html?$", "", label, flags=re.I)
        crumbs.append(label.title() if label else p)
    return crumbs


def _collapse(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _trafilatura_markdown(html: str, url: str | None = None) -> str | None:
    try:
        out = trafilatura.extract(
            html,
            url=url,  # lets trafilatura resolve relative links/images to absolute
            output_format="markdown",
            include_links=True,
            include_images=True,
            include_tables=True,
            favor_recall=True,
        )
    except Exception:
        return None
    if out and len(out.strip()) >= 60:
        return _collapse(out)
    return None


def _absolutize(container, base_url: str) -> None:
    """Rewrite relative href/src attributes to absolute against base_url, in
    place. Used for the markdownify fallback (trafilatura handles its own via
    the url= param)."""
    if not base_url:
        return
    for el in container.select("a[href]"):
        el["href"] = urljoin(base_url, el["href"])
    for el in container.select("img[src]"):
        el["src"] = urljoin(base_url, el["src"])


def _selector_markdown(
    soup: BeautifulSoup, content_selectors, strip_selectors, base_url: str = ""
) -> str:
    container = None
    for sel in content_selectors:
        found = soup.select_one(sel)
        if found:
            container = found
            break
    if container is None:
        container = soup.body or soup
    for sel in strip_selectors:
        for el in container.select(sel):
            el.decompose()
    _absolutize(container, base_url)
    out = md(
        str(container),
        heading_style="ATX",
        strip=["script", "style"],
        escape_asterisks=False,
        escape_underscores=False,
    )
    return _collapse(out)


def extract(
    html: str, path: str, content_selectors, strip_selectors, url: str = ""
) -> Extracted:
    soup = BeautifulSoup(html, "lxml")
    title = page_title(soup)
    description = _meta(soup, "description") or _meta(
        soup, "og:description", attr="property"
    )

    markdown = _trafilatura_markdown(html, url=url or None) or _selector_markdown(
        soup, content_selectors, strip_selectors, base_url=url
    )

    return Extracted(
        title=title,
        description=description,
        markdown=markdown,
        breadcrumbs=breadcrumbs_from_path(path),
        word_count=len(re.findall(r"\w+", markdown)),
    )
