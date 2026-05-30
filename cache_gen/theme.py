"""Shared visual theme for the cache front-end (served as /cache.css).

Hallmark · macrostructure: Stat-Led · genre: modern-minimal (editorial serif)
tone: editorial-technical · anchor hue: DAG gold
theme: DAG brand (warm paper · graphite ink · gold accent · Playfair Display + Inter + IBM Plex Mono)
diversification axes: light warm paper · serif display · warm gold accent
"""

# Google Fonts link injected into every page <head>. Matches the DAG brand stack.
FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?'
    "family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&"
    "family=Inter:wght@400;500;600;700&"
    "family=IBM+Plex+Mono:wght@400;500&display=swap\" rel=\"stylesheet\">"
)

# DAG wordmark — hidden <defs> block injected once per page, referenced via <use>.
# #dag-light (paper fill, for dark backgrounds) and #dag-dark (graphite, for light).
DAG_LOGO_DEFS = (
    '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
    '<symbol id="dag-light" viewBox="0 0 439.73 134.97">'
    '<path fill="#faf7f5" d="M137.59,133.1L199.37,2.06h27.52l61.78,131.04h-29.39l-37.63-79.56c-1.25-2.5-2.43-4.99-3.56-7.49-1.12-2.5-2.19-5.02-3.18-7.58-1-2.56-1.97-5.08-2.9-7.58-.94-2.5-1.78-5.05-2.53-7.68l6.36-.19c-.75,2.87-1.62,5.62-2.62,8.24-1,2.62-2.06,5.18-3.18,7.68-1.12,2.5-2.25,4.99-3.37,7.49-1.12,2.5-2.25,5.05-3.37,7.68l-37.44,79h-28.27Z"/>'
    '<path fill="#faf7f5" d="M439.63,73.48c-.06-1.43-.16-3.09-.28-4.96-.13-1.87-.25-3.68-.37-5.43h-51.17l-22.95,23.03h46.25c-.37,2.73-1.37,5.29-3.03,7.68-2.25,3.25-5.43,6.05-9.55,8.42-4.12,2.37-8.92,4.18-14.41,5.43-5.49,1.25-11.42,1.87-17.78,1.87s-12.92-.84-18.91-2.53-11.33-4.24-16.01-7.68c-4.68-3.43-8.39-7.83-11.14-13.2-2.75-5.36-4.12-11.67-4.12-18.91,0-5.99,1.28-11.54,3.84-16.66,2.56-5.12,6.15-9.55,10.76-13.29,4.62-3.74,10.02-6.67,16.19-8.8,6.18-2.12,12.82-3.18,19.94-3.18,5.86,0,11.39.69,16.57,2.06,5.18,1.37,10.04,3.25,14.6,5.62,4.41,2.3,8.49,4.89,12.25,7.77l6.76-6.78,11.3-11.46c-3.74-3.87-8.91-8.18-14.96-11.43-6.06-3.24-13.01-5.9-20.87-7.96-7.86-2.06-16.35-3.09-25.46-3.09-11.48,0-22.12,1.68-31.92,5.05-9.8,3.37-18.32,8.08-25.55,14.13-7.24,6.05-12.86,13.17-16.85,21.34-4,8.18-5.99,17.07-5.99,26.68,0,10.98,1.97,20.69,5.9,29.11,3.93,8.42,9.33,15.48,16.19,21.15,6.86,5.68,14.98,10.01,24.34,13.01,9.36,3,19.4,4.49,30.14,4.49,11.35,0,21.71-1.25,31.08-3.74,9.36-2.5,17.41-6.21,24.15-11.14,6.74-4.93,11.95-11.01,15.63-18.25,3.68-7.24,5.52-15.66,5.52-25.27,0-.62-.03-1.65-.09-3.09Z"/>'
    '<path fill="#faf7f5" d="M134.41,42.4c-3.25-7.92-8.02-14.91-14.32-20.97-6.3-6.05-14.01-10.79-23.12-14.23-9.11-3.43-19.53-5.15-31.26-5.15H0v105.76l28.08-28.2V27.33h36.69c7.86,0,14.63,1.09,20.31,3.28,5.68,2.19,10.39,5.15,14.13,8.89,3.74,3.74,6.49,8.02,8.24,12.82,1.75,4.81,2.62,9.89,2.62,15.26s-.88,10.48-2.62,15.35c-1.75,4.87-4.49,9.17-8.24,12.92-3.74,3.74-8.46,6.68-14.13,8.8-5.68,2.12-12.45,3.18-20.31,3.18H28.11v.03H0v25.24h65.71c11.73,0,22.15-1.68,31.26-5.05,9.11-3.37,16.82-8.05,23.12-14.04,6.3-5.99,11.07-12.98,14.32-20.97,3.24-7.99,4.87-16.47,4.87-25.46s-1.62-17.25-4.87-25.18Z"/>'
    '<polygon fill="#b38746" points="238.19 104.26 209.28 104.26 209.28 104.51 180.62 133.17 209.53 133.17 209.53 132.92 238.19 104.26"/>'
    '</symbol>'
    '<symbol id="dag-dark" viewBox="0 0 439.73 134.97">'
    '<path fill="#333232" d="M137.59,133.1L199.37,2.06h27.52l61.78,131.04h-29.39l-37.63-79.56c-1.25-2.5-2.43-4.99-3.56-7.49-1.12-2.5-2.19-5.02-3.18-7.58-1-2.56-1.97-5.08-2.9-7.58-.94-2.5-1.78-5.05-2.53-7.68l6.36-.19c-.75,2.87-1.62,5.62-2.62,8.24-1,2.62-2.06,5.18-3.18,7.68-1.12,2.5-2.25,4.99-3.37,7.49-1.12,2.5-2.25,5.05-3.37,7.68l-37.44,79h-28.27Z"/>'
    '<path fill="#333232" d="M439.63,73.48c-.06-1.43-.16-3.09-.28-4.96-.13-1.87-.25-3.68-.37-5.43h-51.17l-22.95,23.03h46.25c-.37,2.73-1.37,5.29-3.03,7.68-2.25,3.25-5.43,6.05-9.55,8.42-4.12,2.37-8.92,4.18-14.41,5.43-5.49,1.25-11.42,1.87-17.78,1.87s-12.92-.84-18.91-2.53-11.33-4.24-16.01-7.68c-4.68-3.43-8.39-7.83-11.14-13.2-2.75-5.36-4.12-11.67-4.12-18.91,0-5.99,1.28-11.54,3.84-16.66,2.56-5.12,6.15-9.55,10.76-13.29,4.62-3.74,10.02-6.67,16.19-8.8,6.18-2.12,12.82-3.18,19.94-3.18,5.86,0,11.39.69,16.57,2.06,5.18,1.37,10.04,3.25,14.6,5.62,4.41,2.3,8.49,4.89,12.25,7.77l6.76-6.78,11.3-11.46c-3.74-3.87-8.91-8.18-14.96-11.43-6.06-3.24-13.01-5.9-20.87-7.96-7.86-2.06-16.35-3.09-25.46-3.09-11.48,0-22.12,1.68-31.92,5.05-9.8,3.37-18.32,8.08-25.55,14.13-7.24,6.05-12.86,13.17-16.85,21.34-4,8.18-5.99,17.07-5.99,26.68,0,10.98,1.97,20.69,5.9,29.11,3.93,8.42,9.33,15.48,16.19,21.15,6.86,5.68,14.98,10.01,24.34,13.01,9.36,3,19.4,4.49,30.14,4.49,11.35,0,21.71-1.25,31.08-3.74,9.36-2.5,17.41-6.21,24.15-11.14,6.74-4.93,11.95-11.01,15.63-18.25,3.68-7.24,5.52-15.66,5.52-25.27,0-.62-.03-1.65-.09-3.09Z"/>'
    '<path fill="#333232" d="M134.41,42.4c-3.25-7.92-8.02-14.91-14.32-20.97-6.3-6.05-14.01-10.79-23.12-14.23-9.11-3.43-19.53-5.15-31.26-5.15H0v105.76l28.08-28.2V27.33h36.69c7.86,0,14.63,1.09,20.31,3.28,5.68,2.19,10.39,5.15,14.13,8.89,3.74,3.74,6.49,8.02,8.24,12.82,1.75,4.81,2.62,9.89,2.62,15.26s-.88,10.48-2.62,15.35c-1.75,4.87-4.49,9.17-8.24,12.92-3.74,3.74-8.46,6.68-14.13,8.8-5.68,2.12-12.45,3.18-20.31,3.18H28.11v.03H0v25.24h65.71c11.73,0,22.15-1.68,31.26-5.05,9.11-3.37,16.82-8.05,23.12-14.04,6.3-5.99,11.07-12.98,14.32-20.97,3.24-7.99,4.87-16.47,4.87-25.46s-1.62-17.25-4.87-25.18Z"/>'
    '<polygon fill="#b38746" points="238.19 104.26 209.28 104.26 209.28 104.51 180.62 133.17 209.53 133.17 209.53 132.92 238.19 104.26"/>'
    '</symbol>'
    '</defs></svg>'
)

# Wordmark markup. variant "dark" = graphite (on light paper), "light" = paper (on dark).
def dag_wordmark(variant: str = "dark") -> str:
    return (
        f'<svg class="dag-wordmark" viewBox="0 0 439.73 134.97" role="img" '
        f'aria-label="DAG"><use href="#dag-{variant}"/></svg>'
    )

STYLESHEET = """/* Hallmark · macrostructure: Stat-Led · tone: editorial-technical · anchor hue: DAG gold */
/* Hallmark · pre-emit critique: P5 H4 E5 S4 R5 V4 */
/* DAG LLM Cache — shared stylesheet. Palette + fonts mirror the DAG brand
   (graphite ink, warm paper, gold accent, Playfair Display + Inter). */

:root {
  --color-ink:        #333232;   /* DAG primary / graphite */
  --color-ink-soft:   #535152;   /* DAG graphite */
  --color-ink-faint:  #7a7877;   /* DAG mid */
  --color-paper:      #fbf5f2;   /* DAG bg */
  --color-paper-2:    #f5ede8;   /* DAG surface */
  --color-line:       #e2d8cd;   /* DAG line */
  --color-line-soft:  #ede4da;   /* DAG line-soft */
  --color-accent:     #ba9965;   /* DAG gold — display accents, fills, focus */
  --color-accent-ink: #8a6a28;   /* deep gold-brown — link text, hover (AA on paper) */
  --color-accent-soft:#f3ead9;   /* DAG gold-bg */
  --color-gold-deep:  #ae905c;   /* DAG gold-deep */
  --color-focus:      #ba9965;

  /* Card surfaces — lifted slightly off the warm paper for depth. */
  --color-card:       #fffdfb;   /* primary card fill (a touch lighter than paper) */
  --color-card-soft:  #fbf6f1;   /* secondary / inset fill */
  --color-card-line:  #e7ddd1;   /* card hairline (a hair darker than --line) */

  /* Soft, warm-tinted shadows — never grey/blue (those read "default/AI"). */
  --shadow-sm:   0 1px 2px rgba(74, 58, 36, 0.05);
  --shadow-card: 0 1px 2px rgba(74, 58, 36, 0.05), 0 14px 32px -18px rgba(74, 58, 36, 0.22);
  --shadow-lift: 0 2px 6px rgba(74, 58, 36, 0.07), 0 22px 48px -20px rgba(74, 58, 36, 0.30);

  --font-display: "Playfair Display", Georgia, "Times New Roman", serif;
  --font-body:    "Inter", system-ui, -apple-system, sans-serif;
  --font-mono:    "IBM Plex Mono", ui-monospace, "SF Mono", monospace;

  --space-1:  0.25rem;
  --space-2:  0.5rem;
  --space-3:  0.75rem;
  --space-4:  1rem;
  --space-5:  1.25rem;
  --space-6:  1.5rem;
  --space-8:  2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;
  --space-24: 6rem;

  --text-xs:   0.6875rem;
  --text-sm:   0.8125rem;
  --text-base: 1rem;
  --text-lg:   1.1875rem;
  --text-xl:   1.5rem;
  --text-2xl:  2rem;
  --text-3xl:  2.75rem;
  --text-display: clamp(2rem, 7.5vw, 4.25rem);

  --ease-out: cubic-bezier(0.2, 0.7, 0.2, 1);
  --dur: 160ms;
  --radius-sm: 9px;
  --radius: 12px;
  --radius-lg: 20px;
  --measure: 68ch;
}

* { box-sizing: border-box; }
html, body { overflow-x: clip; }

html { -webkit-text-size-adjust: 100%; }

body {
  margin: 0;
  /* Warm paper with a whisper of tonal depth so cards have something to lift from. */
  background:
    radial-gradient(120% 60% at 50% -10%, var(--color-paper-2) 0%, transparent 60%),
    var(--color-paper);
  background-attachment: fixed;
  color: var(--color-ink);
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: 1.65;
  font-feature-settings: "kern" 1, "liga" 1, "calt" 1;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}
/* Refined display + mono defaults applied everywhere they're used. */
h1, h2, h3, .num, .statement { font-feature-settings: "kern" 1, "liga" 1; }
.mono, .num, code, .index-pill a, .stat-table td, .stat .label,
.eyebrow, .brand-sub, .breadcrumb, .page-meta, .resources a.r-name,
.tree .row .meta a, .toc a .n, .stat-table caption {
  font-feature-settings: "kern" 1, "tnum" 1, "zero" 1;  /* tabular, slashed-zero */
}
/* Premium gold hairline along the very top of every page. */
body::before {
  content: "";
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg,
    var(--color-accent) 0%, var(--color-gold-deep) 50%, var(--color-accent) 100%);
  z-index: 50;
}

.wrap { max-width: 1040px; margin: 0 auto; padding: 0 var(--space-6); }

a { color: var(--color-accent); text-decoration: none; }
a:hover { color: var(--color-accent-ink); text-decoration: underline; text-underline-offset: 3px; }

:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
  border-radius: 3px;
}

/* ---- DAG wordmark ------------------------------------------------------ */
.dag-wordmark { height: 1.85rem; width: auto; display: block; }
.brandline {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-12);
}
.brandline .divider { width: 1px; height: 1.6rem; background: var(--color-line); }
.brandline .brand-sub {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-ink-faint);
}
a.brandline { text-decoration: none; }
a.brandline:hover { text-decoration: none; }
a.brandline:hover .dag-wordmark { opacity: 0.82; }

/* Per-page brand strip */
.site-head {
  display: flex;
  align-items: center;
  padding-top: var(--space-8);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--color-line-soft);
}
.site-head .brandline { margin-bottom: 0; }

/* ---- Masthead ---------------------------------------------------------- */
.masthead { padding: var(--space-12) 0 var(--space-8); }

.eyebrow {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-ink-faint);
  margin: 0 0 var(--space-4);
}

.masthead h1 {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--text-display);
  line-height: 1.04;
  letter-spacing: -0.01em;
  margin: 0 0 var(--space-4);
  overflow-wrap: anywhere;
  min-width: 0;
}
.masthead h1 .accent { color: var(--color-accent); font-style: italic; }

.masthead .lede {
  max-width: var(--measure);
  font-size: var(--text-lg);
  color: var(--color-ink-soft);
  margin: 0 0 var(--space-8);
}

/* N5 floating pill — the machine-index links */
.index-pill {
  display: inline-flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  padding: var(--space-2);
  background: var(--color-paper-2);
  border: 1px solid var(--color-line);
  border-radius: 999px;
}
.index-pill a {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-ink-soft);
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  transition: background var(--dur) var(--ease-out), color var(--dur) var(--ease-out);
}
.index-pill a:hover {
  background: var(--color-accent-soft);
  color: var(--color-accent-ink);
  text-decoration: none;
}

/* ---- Card primitive ---------------------------------------------------- */
.card {
  background: var(--color-card);
  border: 1px solid var(--color-card-line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: var(--space-10) var(--space-10);
}
@media (max-width: 720px) { .card { padding: var(--space-6); } }

/* ---- Stat strip (cards) ------------------------------------------------ */
.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-5);
  margin: var(--space-10) 0 var(--space-16);
}
.stat {
  position: relative;
  background: var(--color-card);
  border: 1px solid var(--color-card-line);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  padding: var(--space-6) var(--space-6) var(--space-5);
  overflow: hidden;
}
/* a quiet gold tab on each stat card */
.stat::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: linear-gradient(var(--color-accent), var(--color-gold-deep));
  opacity: 0.7;
}
.stat .num {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--text-2xl);
  line-height: 1.05;
  letter-spacing: -0.01em;
  color: var(--color-ink);
}
.stat .label {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  color: var(--color-ink-faint);
  letter-spacing: 0.08em;
  margin-top: var(--space-3);
}

/* ---- Search + index ---------------------------------------------------- */
.index-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
  margin-bottom: var(--space-6);
}
.index-head h2 {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-2xl);
  letter-spacing: -0.01em;
  margin: 0;
}
.search {
  font-family: var(--font-body);
  font-size: var(--text-base);
  padding: 0.55rem 0.9rem;
  min-width: 16rem;
  background: var(--color-paper-2);
  border: 1px solid var(--color-line);
  border-radius: var(--radius);
  color: var(--color-ink);
  transition: border-color var(--dur) var(--ease-out);
}
.search::placeholder { color: var(--color-ink-faint); }
.search:focus-visible { border-color: var(--color-focus); outline-offset: 0; }

/* ---- Page index (card) ------------------------------------------------- */
.index-card {
  background: var(--color-card);
  border: 1px solid var(--color-card-line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: var(--space-8) var(--space-10) var(--space-10);
  margin: var(--space-6) 0 0;
}
@media (max-width: 720px) { .index-card { padding: var(--space-6); } }

.tree { list-style: none; margin: 0; padding: 0; }
.tree .folder {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-xl);
  letter-spacing: -0.01em;
  color: var(--color-ink);
  padding: 0 0 var(--space-4);
  margin: var(--space-10) 0 var(--space-3);
  border-bottom: 1px solid var(--color-card-line);
}
.tree .folder:first-child { margin-top: 0; }
.tree .folder .count {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-accent-ink);
  background: var(--color-accent-soft);
  padding: 0.14rem 0.6rem;
  border-radius: 999px;
  letter-spacing: 0.02em;
}
.tree .row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  column-gap: var(--space-6);
  row-gap: var(--space-2);
  padding: var(--space-4) var(--space-4);
  margin: 0 calc(-1 * var(--space-4));
  border-radius: var(--radius-sm);
  border-top: 1px solid var(--color-line-soft);
  transition: background var(--dur) var(--ease-out);
}
.tree .row:hover { background: var(--color-card-soft); }
.tree .folder + .row { border-top: none; }
.tree .row .title {
  grid-column: 1; grid-row: 1;
  font-family: var(--font-display);
  font-weight: 500;
  font-size: var(--text-lg);
  line-height: 1.3;
  color: var(--color-ink);
  min-width: 0;
}
.tree .row a.title:hover { color: var(--color-accent-ink); text-decoration: none; }
.tree .row .desc {
  grid-column: 1; grid-row: 2;
  font-size: var(--text-sm);
  line-height: 1.55;
  color: var(--color-ink-soft);
  max-width: var(--measure);
}
.tree .row .meta {
  grid-column: 2; grid-row: 1;
  display: inline-flex;
  align-self: center;
  gap: var(--space-2);
  flex-shrink: 0;
}
.tree .row .meta a {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-ink-faint);
  padding: 0.2rem 0.55rem;
  border: 1px solid var(--color-line-soft);
  border-radius: 999px;
  white-space: nowrap;
  transition: border-color var(--dur) var(--ease-out), color var(--dur) var(--ease-out), background var(--dur) var(--ease-out);
}
.tree .row .meta a:hover {
  color: var(--color-accent-ink);
  border-color: var(--color-accent);
  background: var(--color-accent-soft);
  text-decoration: none;
}
.tree .empty { padding: var(--space-8) 0; color: var(--color-ink-faint); }

/* ---- Reading view (per-page) ------------------------------------------- */
.reader { max-width: var(--measure); margin: 0 auto; padding: var(--space-16) 0 var(--space-24); }
.breadcrumb {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-ink-faint);
  margin: 0 0 var(--space-8);
}
.reader article h1 {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: var(--text-3xl);
  line-height: 1.1;
  letter-spacing: -0.01em;
  margin: 0 0 var(--space-6);
  overflow-wrap: anywhere;
}
.reader article h2 {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-xl);
  margin: var(--space-12) 0 var(--space-4);
}
.reader article h3 { font-size: var(--text-lg); margin: var(--space-8) 0 var(--space-3); }
.reader article p { margin: 0 0 var(--space-4); }
.reader article img { max-width: 100%; height: auto; border-radius: var(--radius); }
.reader article ul, .reader article ol { padding-left: 1.25rem; }
.reader article hr { border: 0; border-top: 1px solid var(--color-line); margin: var(--space-12) 0; }
.reader article code {
  font-family: var(--font-mono);
  font-size: 0.9em;
  background: var(--color-paper-2);
  padding: 0.1rem 0.35rem;
  border-radius: 5px;
}
.reader article pre {
  background: var(--color-paper-2);
  border: 1px solid var(--color-line);
  border-radius: var(--radius);
  padding: var(--space-4);
  overflow-x: auto;
}

/* ---- Page meta + TL;DR + FAQ ------------------------------------------- */
.reader .page-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-3);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-ink-faint);
  margin: 0 0 var(--space-8);
}
.reader .page-meta a { color: var(--color-accent-ink); }

.reader .tldr {
  border-left: 3px solid var(--color-accent);
  background: var(--color-accent-soft);
  border-radius: 0 var(--radius) var(--radius) 0;
  padding: var(--space-4) var(--space-6);
  margin: 0 0 var(--space-12);
}
.reader .tldr .label {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-accent-ink);
  margin: 0 0 var(--space-2);
}
.reader .tldr p:last-child { margin: 0; color: var(--color-ink); }

.reader .faq {
  max-width: var(--measure);
  margin: var(--space-16) auto 0;
  padding-top: var(--space-8);
  border-top: 1px solid var(--color-line);
}
.reader .faq h2 {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-xl);
  margin: 0 0 var(--space-6);
}
.reader .faq dt {
  font-weight: 600;
  color: var(--color-ink);
  margin: var(--space-6) 0 var(--space-2);
}
.reader .faq dd { margin: 0; color: var(--color-ink-soft); }

/* ---- Footer (Ft5 Statement) -------------------------------------------- */
.site-foot {
  border-top: 1px solid var(--color-line);
  padding: var(--space-12) 0 var(--space-16);
  color: var(--color-ink-soft);
}
.site-foot .statement {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-lg);
  color: var(--color-ink);
  max-width: var(--measure);
  margin: 0 0 var(--space-4);
}
.site-foot .fine {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-ink-faint);
}
.site-foot .poweredby { margin-top: var(--space-4); }
.site-foot .poweredby strong { color: var(--color-accent-ink); }

/* ---- Masthead site label ----------------------------------------------- */
.masthead .masthead-site {
  font-family: var(--font-mono);
  font-size: var(--text-base);
  color: var(--color-accent-ink);
  letter-spacing: 0.02em;
  margin: 0 0 var(--space-6);
}

/* ---- Section heading + icon badge -------------------------------------- */
/* Emoji wrapped in a tinted rounded badge reads "designed", not "pasted". */
.sec-head {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin: 0 0 var(--space-6);
}
.sec-ico {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  font-size: 1.2rem;
  line-height: 1;
  background: var(--color-accent-soft);
  border: 1px solid var(--color-card-line);
  border-radius: var(--radius-sm);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
}

/* ---- Document sections (About / SEO / Methodology / Usage) ------------- */
.doc-section {
  background: var(--color-card);
  border: 1px solid var(--color-card-line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: var(--space-10);
  margin: var(--space-6) 0 0;
}
@media (max-width: 720px) { .doc-section { padding: var(--space-6); } }
.doc-section h2 {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-2xl);
  letter-spacing: -0.01em;
  margin: 0 0 var(--space-5);
}
.doc-section p { margin: 0 0 var(--space-4); color: var(--color-ink-soft); max-width: var(--measure); }
.doc-section > p:last-child { margin-bottom: 0; }
.doc-section ul { padding-left: 1.2rem; margin: 0 0 var(--space-4); color: var(--color-ink-soft); max-width: var(--measure); }
.doc-section ul:last-child { margin-bottom: 0; }
.doc-section li { margin: 0 0 var(--space-3); padding-left: var(--space-1); }
.doc-section li strong { color: var(--color-ink); font-weight: 600; }
.doc-section code {
  font-family: var(--font-mono);
  font-size: 0.88em;
  background: var(--color-card-soft);
  border: 1px solid var(--color-line-soft);
  padding: 0.08rem 0.36rem;
  border-radius: 6px;
}

/* ---- Table of contents (card) ------------------------------------------ */
.toc {
  background: var(--color-card);
  border: 1px solid var(--color-card-line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: var(--space-10);
  margin: var(--space-6) 0 0;
}
@media (max-width: 720px) { .toc { padding: var(--space-6); } }
.toc h2 {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-2xl);
  letter-spacing: -0.01em;
  margin: 0 0 var(--space-5);
}
.toc ul {
  list-style: none; padding: 0; margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 17rem), 1fr));
  gap: var(--space-1) var(--space-4);
}
.toc a {
  display: flex; align-items: center; justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  margin: 0 calc(-1 * var(--space-4));
  border-radius: var(--radius-sm);
  color: var(--color-ink);
  font-size: var(--text-base);
  transition: background var(--dur) var(--ease-out), color var(--dur) var(--ease-out);
}
.toc a:hover {
  background: var(--color-card-soft);
  color: var(--color-accent-ink);
  text-decoration: none;
}
.toc a .n {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-accent-ink);
  background: var(--color-accent-soft);
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  flex-shrink: 0;
}

/* ---- Folder subtitle (per content section) ----------------------------- */
.tree .folder { flex-wrap: wrap; scroll-margin-top: var(--space-8); }
.tree .folder .f-name { display: inline; }
.tree .folder-sub {
  flex-basis: 100%;
  font-family: var(--font-body);
  font-weight: 400;
  font-size: var(--text-sm);
  color: var(--color-ink-faint);
  margin-top: var(--space-2);
}

/* ---- Machine-readable resources list ----------------------------------- */
.resources {
  list-style: none; padding: 0;
  margin: 0;
  display: grid;
  gap: var(--space-3);
}
.resources li {
  background: var(--color-card-soft);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius);
  padding: var(--space-4) var(--space-5);
  transition: border-color var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-out);
}
.resources li:hover { border-color: var(--color-card-line); box-shadow: var(--shadow-sm); }
.resources a.r-name { font-family: var(--font-mono); font-size: var(--text-base); font-weight: 500; }
.resources .r-desc {
  display: block;
  color: var(--color-ink-soft);
  font-size: var(--text-sm);
  line-height: 1.5;
  margin-top: var(--space-2);
}

/* ---- Statistics tables (inset cards) ----------------------------------- */
.stat-tables {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
  gap: var(--space-5);
  margin-top: var(--space-2);
}
.stat-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-card-soft);
  border: 1px solid var(--color-line-soft);
  border-radius: var(--radius);
  overflow: hidden;
}
.stat-table caption {
  text-align: left;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-ink-faint);
  padding: var(--space-4) var(--space-5) var(--space-2);
}
.stat-table th, .stat-table td {
  padding: var(--space-3) var(--space-5);
  border-top: 1px solid var(--color-line-soft);
  font-size: var(--text-base);
}
.stat-table tr:first-child th, .stat-table tr:first-child td { border-top: none; }
.stat-table th { text-align: left; font-weight: 500; color: var(--color-ink-soft); }
.stat-table td {
  text-align: right;
  font-family: var(--font-mono);
  font-weight: 500;
  color: var(--color-ink);
  white-space: nowrap;
}

@media (max-width: 720px) {
  .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-8) var(--space-6); }
  .masthead { padding-top: var(--space-12); }
  .index-head { flex-direction: column; align-items: stretch; }
  .search { min-width: 0; width: 100%; }
  /* Stack the row: title, then description, then the format links. */
  .tree .row { grid-template-columns: minmax(0, 1fr); }
  .tree .row .desc { grid-row: 2; }
  .tree .row .meta { grid-column: 1; grid-row: 3; margin-top: var(--space-2); }
}

@media (prefers-reduced-motion: reduce) {
  * { transition-duration: 1ms !important; }
}
"""
