"""Optional LLM enrichment: per-page TL;DR + FAQ.

Entirely optional. When `enrich.enabled` is false (the default) this module does
nothing — the generator runs with zero extra dependencies and makes no API calls.

When enabled, it calls the Anthropic API (key read from the ANTHROPIC_API_KEY
environment variable) and caches every result keyed by a content hash, so a
rebuild never re-bills pages whose content (or the enrichment settings) haven't
changed. If the key or the `anthropic` package is missing, enrichment disables
itself with a notice rather than failing the build.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Enrichment:
    summary: str = ""
    faqs: list[dict] = field(default_factory=list)  # [{"q": ..., "a": ...}]

    @property
    def is_empty(self) -> bool:
        return not self.summary and not self.faqs


EMPTY = Enrichment()


class Enricher:
    """Generates (and caches) TL;DR + FAQ for a page. No-op unless enabled."""

    def __init__(self, config: dict):
        ecfg = config.get("enrich") or {}
        self.enabled = bool(ecfg.get("enabled", False))
        self.want_summary = bool(ecfg.get("summary", True))
        self.want_faq = bool(ecfg.get("faq", True))
        self.faq_count = int(ecfg.get("faq_count", 4))
        self.model = ecfg.get("model", "claude-haiku-4-5-20251001")
        self.cache_dir = Path(ecfg.get("cache_dir", ".enrich-cache"))
        self.max_chars = int(ecfg.get("max_input_chars", 12000))
        self._client = None
        self._ready = False
        self.hits = 0
        self.calls = 0
        if self.enabled:
            self._init_client()

    def _init_client(self) -> None:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            print(
                "  [enrich] enabled, but ANTHROPIC_API_KEY is not set "
                "- continuing without enrichment."
            )
            self.enabled = False
            return
        try:
            import anthropic  # lazy + optional
        except ImportError:
            print(
                "  [enrich] enabled, but the 'anthropic' package isn't installed "
                "(pip install anthropic) - continuing without enrichment."
            )
            self.enabled = False
            return
        self._client = anthropic.Anthropic(api_key=key)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._ready = True

    def _cache_key(self, markdown: str) -> str:
        h = hashlib.sha256()
        h.update(self.model.encode())
        h.update(b"\x00")
        h.update(f"{self.want_summary}:{self.want_faq}:{self.faq_count}".encode())
        h.update(b"\x00")
        h.update(markdown.encode("utf-8"))
        return h.hexdigest()

    def enrich(self, title: str, markdown: str) -> Enrichment:
        if not (self.enabled and self._ready) or not markdown.strip():
            return EMPTY

        cache_file = self.cache_dir / f"{self._cache_key(markdown)}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                self.hits += 1
                return Enrichment(
                    summary=data.get("summary", ""),
                    faqs=data.get("faqs", []),
                )
            except Exception:
                pass  # corrupt cache entry — regenerate

        result = self._call(title, markdown)
        try:
            cache_file.write_text(
                json.dumps({"summary": result.summary, "faqs": result.faqs}),
                encoding="utf-8",
            )
        except Exception:
            pass
        return result

    def _call(self, title: str, markdown: str) -> Enrichment:
        body = markdown[: self.max_chars]
        wants = []
        if self.want_summary:
            wants.append("a 1-2 sentence plain-language TL;DR")
        if self.want_faq:
            wants.append(
                f"up to {self.faq_count} frequently-asked question/answer pairs a "
                "reader might have, each answered only from the content"
            )
        ask = " and ".join(wants)
        prompt = (
            f'You are preparing an LLM/RAG content-cache entry for the page titled "{title}". '
            f"From the page content below, produce {ask}. "
            "Answer ONLY from the content provided; never invent facts, metrics, names, or claims. "
            "If the content is too thin to support FAQs, return an empty faqs array. "
            'Respond with a single JSON object of the form '
            '{"summary": "...", "faqs": [{"q": "...", "a": "..."}]} and nothing else.\n\n'
            "---\n" + body
        )
        self.calls += 1
        try:
            msg = self._client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(
                b.text for b in msg.content if getattr(b, "type", "") == "text"
            )
            data = _parse_json(text)
            summary = (data.get("summary") or "").strip() if self.want_summary else ""
            faqs = []
            if self.want_faq:
                for f in data.get("faqs") or []:
                    q = str(f.get("q", "")).strip()
                    a = str(f.get("a", "")).strip()
                    if q and a:
                        faqs.append({"q": q, "a": a})
            return Enrichment(summary=summary, faqs=faqs)
        except Exception as e:  # network, parse, API error — never fail the build
            print(f"  [enrich] call failed for '{title}' ({e}) - skipping this page.")
            return EMPTY

    def report(self) -> str | None:
        if not self.enabled:
            return None
        return f"enrichment: {self.calls} API calls, {self.hits} cache hits"


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        # ```json ... ``` fence
        text = text.split("```", 2)[1] if "```" in text[3:] else text[3:]
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        text = m.group(0)
    return json.loads(text)
