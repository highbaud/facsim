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
