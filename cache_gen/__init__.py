"""facsim: generate an LLM-optimized static mirror of a website.

For every source page it emits a clean HTML copy (noindex/nofollow + canonical to
the original + Schema.org breadcrumbs) and a content.md markdown copy, plus the
root discovery files: llms.txt, sitemap.xml, robots.txt, and an index.html.
"""

__version__ = "1.0.0"
