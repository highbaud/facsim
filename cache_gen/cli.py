"""End-to-end orchestration: crawl -> extract -> render -> write + indexes."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import yaml

from .crawl import Crawler
from .extract import extract
from .enrich import Enricher
from .render import render_page, output_paths
from . import indexes
from .theme import STYLESHEET


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _print_diff(old_manifest: Path, new_files: dict[str, str]) -> None:
    """Compare the freshly built file set against a previous manifest and print
    a new / changed / removed summary."""
    try:
        prev = json.loads(old_manifest.read_text(encoding="utf-8")).get("files", {})
    except Exception:
        print("  diff: previous manifest unreadable — skipping diff")
        return
    new_keys, old_keys = set(new_files), set(prev)
    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = sorted(k for k in (new_keys & old_keys) if new_files[k] != prev[k])
    print(f"  diff vs previous build: {len(added)} new, {len(changed)} changed, "
          f"{len(removed)} removed")
    for label, items in (("+", added), ("~", changed), ("-", removed)):
        for k in items[:15]:
            print(f"    {label} {k}")
        if len(items) > 15:
            print(f"    {label} ... and {len(items) - 15} more")


def build(
    config: dict,
    *,
    limit: int | None = None,
    clean: bool = False,
    output: str | None = None,
    diff_against: str | None = None,
) -> int:
    src_base = config["source"]["base_url"].rstrip("/")
    out_dir = Path(output or config["output"]["dir"])

    if limit is not None:
        config["crawl"]["max_pages"] = limit

    print(f"Crawling {src_base} (max {config['crawl']['max_pages']} pages)...")
    crawler = Crawler(config)
    result = crawler.run()
    print(f"  fetched {len(result.pages)} pages, {len(result.errors)} errors")

    if clean and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Record every file written, mapped to a content hash, for the manifest.
    written: dict[str, str] = {}

    def write(rel: str, content: str) -> None:
        dest = out_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = content.encode("utf-8")
        dest.write_bytes(data)
        written[rel] = hashlib.sha256(data).hexdigest()

    content_selectors = config["extract"]["content_selectors"]
    strip_selectors = config["extract"]["strip_selectors"]
    min_words = int(config["extract"].get("min_content_words", 0) or 0)

    enricher = Enricher(config)
    if enricher.enabled:
        print(f"  enrichment on (model {enricher.model}) - TL;DR + FAQ per page")

    rendered = []
    skipped_thin = 0
    for page in result.pages:
        canonical = page.url  # original source URL is the canonical
        ext = extract(
            page.html, page.path, content_selectors, strip_selectors, url=page.url
        )
        # Drop shell/near-empty pages (e.g. JS-only stubs) to keep the corpus clean.
        if min_words and ext.word_count < min_words:
            skipped_thin += 1
            continue
        enr = enricher.enrich(ext.title, ext.markdown)
        rp = render_page(
            ext, page.path, canonical, src_base,
            enrichment=enr, section=page.section,
        )
        rendered.append(rp)

        html_rel, md_rel = output_paths(page.path)
        write(html_rel, rp.html)
        write(md_rel, rp.markdown)

    # Shared stylesheet for the index + reading views.
    write("cache.css", STYLESHEET)

    # Root discovery files.
    write("llms.txt", indexes.build_llms_txt(rendered, config))
    write("sitemap.xml", indexes.build_sitemap_xml(rendered, config))
    write("robots.txt", indexes.build_robots_txt(config))
    write("llms-full.txt", indexes.build_llms_full_txt(rendered, config))
    write("corpus.jsonl", indexes.build_corpus_jsonl(rendered, config))

    # index.html only if the source root wasn't itself captured at "/".
    toc_name = "cache-index.html" if "index.html" in written else "index.html"
    write(toc_name, indexes.build_index_html(rendered, config))

    if (config.get("deploy") or {}).get("emit_htaccess", True):
        write(".htaccess", indexes.build_htaccess(config))

    # Diff against a previous build before we overwrite that build's manifest.
    if diff_against:
        prev = Path(diff_against)
        if prev.exists():
            _print_diff(prev, written)
        else:
            print(f"  diff: no previous manifest at {prev} (first build?)")

    # Manifest is written last; it fingerprints everything above (not itself).
    write("manifest.json", indexes.build_manifest(config, written, len(rendered)))

    print(f"Wrote {len(rendered)} pages + {len(written) - 2 * len(rendered)} "
          f"root files to {out_dir}/")
    if skipped_thin:
        print(f"  skipped {skipped_thin} thin pages (< {min_words} words)")
    enrich_report = enricher.report()
    if enrich_report:
        print(f"  {enrich_report}")
    if result.errors:
        print("Errors:")
        for url, reason in result.errors[:20]:
            print(f"  {reason}: {url}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cache_gen", description="Generate an LLM content cache mirror of a site."
    )
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--limit", type=int, help="Override crawl.max_pages")
    parser.add_argument(
        "--clean", action="store_true", help="Wipe the output dir before building"
    )
    parser.add_argument(
        "--output", help="Override output.dir (where the cache is written)"
    )
    parser.add_argument(
        "--diff-against",
        dest="diff_against",
        metavar="MANIFEST",
        help="Path to a previous build's manifest.json; print a new/changed/removed summary",
    )
    parser.add_argument(
        "--enrich",
        dest="enrich",
        action="store_true",
        default=None,
        help="Force LLM enrichment on (needs ANTHROPIC_API_KEY)",
    )
    parser.add_argument(
        "--no-enrich",
        dest="enrich",
        action="store_false",
        help="Force LLM enrichment off (overrides config)",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)
    if args.enrich is not None:
        config.setdefault("enrich", {})["enabled"] = args.enrich
    return build(
        config,
        limit=args.limit,
        clean=args.clean,
        output=args.output,
        diff_against=args.diff_against,
    )


if __name__ == "__main__":
    sys.exit(main())
