<p align="center">
  <img src="assets/facsim-logo.svg" alt="Facsim" width="220">
</p>

# facsim

Generate an LLM-optimized static mirror ("cache") of a website: clean HTML +
markdown twins of every page, plus the root discovery files (`llms.txt`,
`llms-full.txt`, `corpus.jsonl`, `sitemap.xml`, `robots.txt`) that LLM crawlers
and RAG pipelines look for. The mirror is SEO-neutral — every page carries
`noindex,nofollow` and a `<link rel="canonical">` back to the original — so it
lives happily on a subdomain (e.g. `llm.yourdomain.com`) without competing with
the real site for rankings.

## The problem

Modern websites are built for browsers and search engines, not for language
models. A typical page is a wrapper of navigation, headers, footers, cookie
banners, ad slots, and JavaScript around a small core of actual content. When an
LLM crawler or a RAG pipeline fetches that page, it has to download the whole
wrapper and then guess which part is the article. The guess is often wrong, the
markup is noisy, and JS-rendered content may not be there at all on a plain
fetch. The result: worse retrieval, wasted tokens, and content that models
either misread or skip.

The obvious fix — publish a clean, text-first copy of your site — runs straight
into an SEO problem. A second public copy of your pages looks like duplicate
content to search engines and can siphon rankings away from the real site. So
most teams never make one.

## What facsim does

facsim resolves that tension. It crawls your live site once and writes a
**separate, read-only mirror** designed for machine consumption:

- **A clean reading view** (`index.html`) for every page — just the real content,
  boilerplate stripped, with structured data baked in.
- **A markdown twin** (`content.md`) of every page, with YAML frontmatter — the
  format RAG pipelines and LLMs ingest most cheaply.
- **Root discovery files** at the mirror's root — `llms.txt` (a hierarchical
  index), `llms-full.txt` (the whole corpus in one file), `corpus.jsonl` (one
  JSON record per page for retrieval), plus `sitemap.xml` and `robots.txt`.

The objective is a single artifact you can host on a subdomain and point any LLM
tool at: *"here is our content, already clean, already indexed, in the formats
you prefer."*

## Why it works

Three design decisions do the heavy lifting:

1. **SEO-neutral by construction.** Every page in the mirror carries
   `noindex,nofollow` and a `<link rel="canonical">` pointing back to the
   original URL. Search engines are explicitly told not to index the mirror and
   that the source page is the real one — so a public mirror on
   `llm.yourdomain.com` never competes with your main site for rankings. This is
   what makes it safe to publish the clean copy at all.

2. **It speaks the conventions crawlers already look for.** `llms.txt` and
   `llms-full.txt` are the emerging root-level conventions for "here's the
   site's content for LLMs"; `corpus.jsonl` is a drop-in for RAG ingestion; the
   per-page markdown twin is the cheapest possible thing to embed. Nothing has to
   be reverse-engineered at read time because the work is already done.

3. **The content is extracted once, well.** Boilerplate removal, link
   absolutization, and markdown conversion happen at build time using
   purpose-built extraction — so every consumer gets the same clean text instead
   of each one re-deriving it (badly) from raw HTML.

A content-hash `manifest.json` makes rebuilds cheap: only pages whose content
actually changed are re-fingerprinted (and, with enrichment on, only those pages
are re-billed to the LLM). `--diff-against` reports exactly what moved between
builds.

## How it works — the pipeline

```
 crawl ──▶ extract ──▶ render ──▶ index
 (BFS)    (clean MD)   (HTML+MD)   (root files)
```

1. **Crawl** (`crawl.py`) — a same-host breadth-first crawl, seeded from your
   site's `sitemap.xml` (it follows one level of sitemap-index nesting and reads
   the child-sitemap names to label sections, e.g. `post-sitemap.xml` →
   *"Insights & Articles"*). `exclude_patterns` skip what you don't want;
   transient failures (429/5xx, dropped connections) are retried with backoff.

2. **Extract** (`extract.py`) — primary extraction uses
   [trafilatura](https://trafilatura.readthedocs.io/) for boilerplate removal,
   with a configurable CSS-selector + `markdownify` fallback. Relative links and
   images are rewritten to absolute, navigation/headers/footers/scripts are
   stripped, and pages thinner than `min_content_words` are dropped to keep the
   corpus clean.

3. **Render** (`render.py`) — each page becomes a clean HTML reading view
   (`noindex,nofollow`, canonical link, Schema.org `WebPage` + `BreadcrumbList`
   JSON-LD, a per-page meta box, and — with enrichment on — a TL;DR and FAQ with
   `FAQPage` JSON-LD) plus its `content.md` twin.

4. **Index** (`indexes.py`) — the rendered pages are assembled into the root
   discovery files (`llms.txt`, `llms-full.txt`, `corpus.jsonl`, `sitemap.xml`,
   `robots.txt`), a styled HTML table of contents, an `.htaccess`, and the
   content-hash `manifest.json`.

Optional **enrichment** (`enrich.py`) adds a per-page TL;DR and FAQ via the
Anthropic API; it's off by default and cached per content hash so it only bills
pages that changed.

## What it produces

For every crawled page:

- `path/index.html` — a clean reading view (real HTML body, brand-labelled),
  with `noindex,nofollow`, canonical link, Schema.org `WebPage` +
  `BreadcrumbList` JSON-LD, a per-page meta box (word count · build date ·
  links to the markdown and source), and — when enrichment is on — a TL;DR and
  FAQ (with `FAQPage` JSON-LD).
- `path/content.md` — YAML frontmatter (title, url, word_count, optional
  summary/faqs) followed by clean markdown.

Plus root files:

- `llms.txt` — hierarchical index with per-link descriptions and trailing
  Access / Recommended-use / Notes guidance.
- `llms-full.txt` — the whole corpus concatenated into one file.
- `corpus.jsonl` — one JSON record per page for RAG ingestion.
- `sitemap.xml`, `robots.txt`, a styled HTML table of contents
  (`index.html`, or `cache-index.html` if the homepage occupies `/`).
- `.htaccess` — correct MIME types + caching (see Deploy).
- `manifest.json` — a content-hash fingerprint of every output file, used by
  `--diff-against` to report what changed between rebuilds.

## Install

```bash
pipx install facsim          # isolated, gives you the `facsim` command
# or
pip install facsim
```

From a checkout:

```bash
pip install -e .
```

Optional LLM enrichment (per-page TL;DR + FAQ) needs one extra:

```bash
pip install "facsim[enrich]"
```

## Configure

Run the setup wizard — it asks for the site, its sitemap, and what to call the
cache, then writes `config.yaml`:

```bash
facsim init
```

Example answers produce a cache labelled **"Acme LLM Cache"**:

```
Site to mirror (base URL):   https://www.acme.com
Sitemap path:                /sitemap.xml
Cache will be served at:     https://llm.acme.com
Brand name (the "X" in "X LLM Cache"):  Acme
```

Or copy `config.yaml` and edit by hand. The fields you must set for a real run:

```yaml
source:
  base_url: "https://www.yourdomain.com"   # the live site to mirror
  sitemap_path: "/sitemap.xml"             # path to the site's sitemap
cache:
  base_url: "https://llm.yourdomain.com"   # where this cache will be served
  brand: "COMPANYNAME"                      # wordmark — renders "COMPANYNAME LLM Cache"
  logo: ""                                  # optional SVG logo (see below)
  site_name: "yourdomain.com"               # human-readable source label
```

Tune `extract.content_selectors` to your site's markup, and
`crawl.exclude_patterns` to skip what you don't want mirrored.

### Logo

By default the wordmark is the brand name set in the display face. To use your
own mark instead, point `cache.logo` at an SVG file (absolute, or relative to
where you run the build):

```yaml
cache:
  logo: "assets/logo.svg"
```

The SVG is inlined into every page, sized to the wordmark height with its own
colours preserved. If the file is missing or isn't a valid SVG, the build
prints a notice and falls back to the text wordmark — it never fails.

The repo ships its own mark in `assets/` (`facsim-logo.svg` for light
backgrounds, `facsim-logo-light.svg` for dark) if you want a reference for
sizing and palette.

## Build

```bash
facsim --config config.yaml
# or, from a checkout, equivalently:
python -m cache_gen --config config.yaml
```

Useful flags:

| Flag | Effect |
| --- | --- |
| `--limit N` | Cap the crawl at N pages (handy for a test run) |
| `--clean` | Wipe the output dir before building |
| `--output DIR` | Write to DIR instead of `output.dir` from the config |
| `--diff-against manifest.json` | Print a new/changed/removed summary vs a prior build |
| `--enrich` / `--no-enrich` | Force the LLM layer on/off (overrides config) |

### Optional enrichment

Off by default — the generator runs fully without an API key or the `anthropic`
package. To enable: set `enrich.enabled: true` (or pass `--enrich`), `export
ANTHROPIC_API_KEY=...`, and install the `enrich` extra. If the key or package
is missing the build prints a notice and continues without enrichment — it
never fails. Results are cached per content hash in `.enrich-cache/`, so a
rebuild only bills pages whose content actually changed.

## Deploy to an Apache subdomain

The `deploy/` directory has everything for a self-updating subdomain. Suggested
server layout:

```
/opt/facsim/
  src/        this repo (your checkout, with config.yaml)
  releases/   timestamped build outputs
  current ->  releases/<latest>     # symlink Apache serves
```

1. **Checkout + install on the server:**
   ```bash
   sudo mkdir -p /opt/facsim && cd /opt/facsim
   git clone <your-repo> src && cd src
   pip install .            # add [enrich] if you want the LLM layer
   ```

2. **Apache vhost** — copy `deploy/apache-vhost.conf.template`, replace
   `YOURDOMAIN`, enable it, then add HTTPS with certbot:
   ```bash
   sudo cp deploy/apache-vhost.conf.template /etc/apache2/sites-available/facsim.conf
   sudo a2enmod expires && sudo a2ensite facsim
   sudo systemctl reload apache2
   sudo certbot --apache -d llm.yourdomain.com
   ```
   The vhost's `DocumentRoot` is the `current` symlink, and it duplicates the
   MIME/caching directives so the cache serves correctly even where
   `AllowOverride None` ignores `.htaccess`.

3. **First publish:**
   ```bash
   sudo ROOT=/opt/facsim deploy/rebuild.sh
   ```
   `rebuild.sh` builds into `releases/<timestamp>`, prints a diff against the
   live release, then **atomically** repoints `current` (so visitors never see
   a half-written tree) and prunes to the most recent 5 releases.

## Keep it updated

Pick **one** scheduler.

**systemd timer (recommended):**

```bash
sudo cp deploy/facsim.{service,timer} /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now facsim.timer
systemctl list-timers facsim.timer    # confirm next run
```

Edit the `.service` to set `ROOT` and (optionally) `ANTHROPIC_API_KEY` —
prefer an `EnvironmentFile` chmod 600 for the key.

**cron:** see `deploy/crontab.example` (`crontab -u www-data
deploy/crontab.example`).

Either way the schedule just runs `rebuild.sh`, so each update is an atomic
symlink swap with a logged diff.

## Author

Built by Max Avery.

- X / Twitter: [@realmaxavery](https://x.com/realmaxavery)
- LinkedIn: [maxavery](https://www.linkedin.com/in/maxavery/)
