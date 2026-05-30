"""Same-host BFS crawler."""

from __future__ import annotations

import re
import time
from collections import deque
from dataclasses import dataclass, field
from urllib.parse import urljoin, urldefrag, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class Page:
    url: str            # absolute, normalized source URL
    path: str           # URL path (leading slash, no trailing slash except root "/")
    html: str           # raw HTML of the page
    section: str = ""   # content-type label derived from the source sitemap


# Map a WordPress/Yoast child-sitemap filename stem to a friendly section
# label for the index. Unknown post types fall through to a title-cased name.
_SECTION_LABELS = {
    "post": "Insights & Articles",
    "page": "Pages",
    "product": "Products",
    "docs": "Docs",
    "doc": "Docs",
    "ex_team": "Team",
    "team": "Team",
    "wpfunnels": "Funnels",
    "wpfunnel_steps": "Funnels",
}


def _section_from_sitemap(sitemap_url: str) -> str:
    """'.../post-sitemap.xml' -> 'Insights & Articles'. Best-effort label."""
    stem = urlparse(sitemap_url).path.rsplit("/", 1)[-1]
    stem = re.sub(r"-?sitemap.*\.xml$", "", stem) or stem
    if stem in _SECTION_LABELS:
        return _SECTION_LABELS[stem]
    return stem.replace("_", " ").replace("-", " ").strip().title() or "Pages"


@dataclass
class CrawlResult:
    pages: list[Page] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)  # (url, reason)


def normalize_url(base_host: str, url: str) -> str | None:
    """Return an absolute, fragment-stripped URL if it is on base_host, else None."""
    url, _frag = urldefrag(url)
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return None
    if parsed.netloc != base_host:
        return None
    # Drop trailing slash on the path for stable dedupe, keep root as "/".
    path = parsed.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return f"{parsed.scheme}://{parsed.netloc}{path}" + (
        f"?{parsed.query}" if parsed.query else ""
    )


def path_of(url: str) -> str:
    p = urlparse(url).path or "/"
    if len(p) > 1 and p.endswith("/"):
        p = p.rstrip("/")
    return p


class Crawler:
    def __init__(self, config: dict):
        src = config["source"]
        crawl = config["crawl"]
        self.base_url = src["base_url"].rstrip("/")
        self.base_host = urlparse(self.base_url).netloc
        self.seeds = src.get("seeds") or []
        self.use_sitemap = src.get("use_sitemap", True)
        # Some sites publish the sitemap under a non-standard name (e.g.
        # /sitemaps.xml). Configurable; defaults to the conventional path.
        self.sitemap_path = "/" + str(src.get("sitemap_path", "/sitemap.xml")).lstrip("/")
        self.max_pages = crawl["max_pages"]
        self.delay = crawl["request_delay_seconds"]
        self.timeout = crawl["timeout_seconds"]
        self.exclude = [re.compile(p) for p in crawl.get("exclude_patterns", [])]
        self.session = requests.Session()
        self.session.headers["User-Agent"] = crawl["user_agent"]
        # Retry transient failures (connection drops, 429/5xx) with backoff so a
        # single blip doesn't permanently drop a page from a long crawl.
        retry = Retry(
            total=crawl.get("max_retries", 3),
            backoff_factor=crawl.get("retry_backoff_seconds", 0.5),
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        # Populated by _sitemap_urls(): normalized URL -> section label.
        self.url_section: dict[str, str] = {}

    def _sitemap_urls(self) -> list[str]:
        """Fetch the source sitemap (following one level of sitemap index) and
        return all <loc> page URLs. Also records a per-URL section label in
        self.url_section, keyed off which child sitemap each URL came from.
        Best-effort; failures return []."""
        found: list[str] = []

        def record(url: str, section: str) -> None:
            n = normalize_url(self.base_host, url)
            if n:
                self.url_section.setdefault(n, section)

        try:
            resp = self.session.get(self.base_url + self.sitemap_path, timeout=self.timeout)
            if resp.status_code != 200:
                return found
            soup = BeautifulSoup(resp.content, "xml")
            child_maps = [
                loc.get_text(strip=True) for loc in soup.select("sitemap > loc")
            ]
            if child_maps:
                for sm in child_maps[:50]:
                    section = _section_from_sitemap(sm)
                    try:
                        r = self.session.get(sm, timeout=self.timeout)
                        if r.status_code == 200:
                            child = BeautifulSoup(r.content, "xml")
                            for l in child.select("url > loc"):
                                u = l.get_text(strip=True)
                                found.append(u)
                                record(u, section)
                    except requests.RequestException:
                        continue
            else:
                for l in soup.select("url > loc"):
                    u = l.get_text(strip=True)
                    found.append(u)
                    record(u, "Pages")
        except requests.RequestException:
            return []
        return found

    def _excluded(self, url: str) -> bool:
        target = urlparse(url).path + (
            f"?{urlparse(url).query}" if urlparse(url).query else ""
        )
        return any(rx.search(target) for rx in self.exclude)

    def run(self) -> CrawlResult:
        result = CrawlResult()
        start = normalize_url(self.base_host, self.base_url + "/")
        queue: deque[str] = deque([start] if start else [])
        sitemap_seeds = self._sitemap_urls() if self.use_sitemap else []
        for s in list(self.seeds) + sitemap_seeds:
            n = normalize_url(self.base_host, s)
            if n and n not in queue:
                queue.append(n)
        seen: set[str] = set(queue)

        while queue and len(result.pages) < self.max_pages:
            url = queue.popleft()
            if self._excluded(url):
                continue
            try:
                resp = self.session.get(url, timeout=self.timeout)
            except requests.RequestException as e:
                result.errors.append((url, str(e)))
                continue
            if resp.status_code != 200:
                result.errors.append((url, f"HTTP {resp.status_code}"))
                continue
            ctype = resp.headers.get("Content-Type", "")
            if "text/html" not in ctype:
                continue

            html = resp.text
            section = self.url_section.get(url, "Pages")
            result.pages.append(
                Page(url=url, path=path_of(url), html=html, section=section)
            )

            soup = BeautifulSoup(html, "lxml")
            for a in soup.find_all("a", href=True):
                nxt = normalize_url(self.base_host, urljoin(url, a["href"]))
                if nxt and nxt not in seen and not self._excluded(nxt):
                    seen.add(nxt)
                    queue.append(nxt)

            if self.delay:
                time.sleep(self.delay)

        return result
