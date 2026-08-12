#!/usr/bin/env python3
"""Export a public PaperCode atlas and sanitized reading pages."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

import yaml


SKIP_DIRS = {
    ".codegraph",
    ".git",
    ".pytest_cache",
    ".qmd-cache",
    ".venv",
    "SearchDatabase",
    "SearchResults",
    "__pycache__",
    "assets",
    "auto",
    "data",
    "datasets",
    "docs",
    "graphify-out",
    "logs",
    "node_modules",
    "output_paper_figures",
    "output_paper_md",
    "output_paper_supp_md",
    "output_supp_md",
    "paper-atlas",
    "results",
    "scratch",
    "tmp",
    "tools",
    "vendor",
    "wiki",
}
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
WHITESPACE_RE = re.compile(r"\s+")
CHINESE_RE = re.compile(r"[\u3400-\u9fff]")
SUMMARY_HEADING_RE = re.compile(r"一句话|先说结论|一句话理解|抓住核心|核心结论")
ENGLISH_SUMMARY_HEADING_RE = re.compile(
    r"quick take|overview|bottom line|summary|motivation|problem",
    flags=re.IGNORECASE,
)
SOURCE_CITATION_RE = re.compile(
    r"[（(][^（）()]{0,180}(?:\.md|\.py|\.R|\.ipynb|PAPER_MD|CODE_DIR)[^（）()]{0,180}[）)]",
    flags=re.IGNORECASE,
)
FRONT_MATTER_RE = re.compile(r"\A\ufeff?---\s*\n.*?\n---\s*(?:\n|\Z)", flags=re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", flags=re.DOTALL)
DANGEROUS_HTML_RE = re.compile(
    r"<(script|iframe|object|embed)\b[^>]*>.*?</\1\s*>|<(?:script|iframe|object|embed)\b[^>]*/?>",
    flags=re.IGNORECASE | re.DOTALL,
)
MARKDOWN_LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)\n]+)\)")
PRIVATE_PATH_RE = re.compile(
    r"(?<![:\w])/(?:workspace|home/(?:shuai|lin)|mnt|datahdd)(?:/[^\s`'\"<>{}\]\)]*)?",
    flags=re.IGNORECASE,
)
FORBIDDEN_OUTPUT = (
    "/workspace/",
    "/home/shuai/",
    "/home/lin/",
    "/mnt/",
    "file://",
    "analysis_meta.json",
    "method_explained_zh.md",
    "output_paper_md",
    "CODE_DIR",
)

EXCLUDED_CATEGORY_PREFIXES = {
    "foundationmodel",
    "regulation_causal_networks",
}


@dataclass(frozen=True)
class Category:
    id: str
    title: str
    path: str
    order: int


@dataclass(frozen=True)
class Paper:
    method: str
    title: str
    summary_zh: str
    summary_en: str
    detail_zh: str
    detail_en: str
    detail_slug: str
    category_id: str
    category_title: str
    year: str
    journal: str
    doi: str
    has_code: bool


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def first_text(*values: Any) -> str:
    for value in values:
        if value is not None and not isinstance(value, (dict, list, bool)):
            text = str(value).strip()
            if text and text.casefold() not in {"missing", "not found", "none", "null", "n/a"}:
                return text
    return ""


def load_categories(root: Path) -> list[Category]:
    raw = yaml.safe_load((root / "taxonomy.yml").read_text(encoding="utf-8")) or {}
    categories: list[Category] = []
    for item in raw.get("categories", []):
        if not isinstance(item, dict) or item.get("public", True) is False:
            continue
        path = first_text(item.get("path"), item.get("id"))
        if not path:
            continue
        categories.append(
            Category(
                id=first_text(item.get("id"), path),
                title=first_text(item.get("title"), path.replace("_", " ").title()),
                path=path.strip("/"),
                order=int(item.get("display_order", 9999)),
            )
        )
    return sorted(categories, key=lambda item: (item.order, item.title.casefold()))


def iter_workspaces(root: Path) -> Iterable[Path]:
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            name for name in dirnames if name not in SKIP_DIRS and not name.startswith(".")
        )
        if "analysis_meta.json" not in filenames:
            continue
        yield Path(current)
        dirnames[:] = []


def category_for(relative_workspace: str, categories: list[Category]) -> Category | None:
    candidates = [
        item
        for item in categories
        if relative_workspace == item.path or relative_workspace.startswith(item.path + "/")
    ]
    return max(candidates, key=lambda item: len(item.path), default=None)


def markdown_to_text(markdown: str) -> str:
    parts: list[str] = []
    in_fence = False
    in_math = False
    for line in markdown.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if line.strip() == "$$":
            in_math = not in_math
            continue
        if in_fence or in_math or HEADING_RE.match(line):
            continue
        text = line.strip()
        if not text or text.startswith("|") or re.fullmatch(r"[-:| ]+", text):
            continue
        text = re.sub(r"^\s*(?:[-+*]|\d+[.)])\s+", "", text)
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"[`*_~]+", "", text)
        text = re.sub(r"\$+([^$]+)\$+", r"\1", text)
        parts.append(text)
    text = WHITESPACE_RE.sub(" ", " ".join(parts)).strip()
    return WHITESPACE_RE.sub(" ", SOURCE_CITATION_RE.sub("", text)).strip()


def section_text(markdown: str, heading_pattern: re.Pattern[str]) -> str:
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if not match or len(match.group(1)) > 2 or not heading_pattern.search(match.group(2)):
            continue
        level = len(match.group(1))
        body: list[str] = []
        for candidate in lines[index + 1 :]:
            next_heading = HEADING_RE.match(candidate)
            if next_heading and len(next_heading.group(1)) <= level:
                break
            body.append(candidate)
        text = markdown_to_text("\n".join(body))
        if text:
            return text
    return markdown_to_text(markdown)


def summary_section(markdown: str) -> str:
    return section_text(markdown, SUMMARY_HEADING_RE)


def english_summary_section(markdown: str) -> str:
    return section_text(markdown, ENGLISH_SUMMARY_HEADING_RE)


def clip(text: str, limit: int = 220) -> str:
    text = WHITESPACE_RE.sub(" ", text).strip()
    if len(text) <= limit:
        return text
    prefix = text[: limit + 1]
    boundary = max(prefix.rfind(mark) for mark in "。！？；.!?")
    if boundary >= int(limit * 0.58):
        return prefix[: boundary + 1]
    return prefix[:limit].rstrip("，、；,:： ") + "…"


def public_markdown(markdown: str) -> str:
    """Keep readable Markdown while removing local-only references and embeds."""
    text = FRONT_MATTER_RE.sub("", markdown, count=1)
    text = text.replace("\x08", r"\b").replace("\x0c", r"\f")
    text = HTML_COMMENT_RE.sub("", text)
    text = DANGEROUS_HTML_RE.sub("", text)
    text = re.sub(r"<img\b[^>]*>", "", text, flags=re.IGNORECASE)

    def clean_link(match: re.Match[str]) -> str:
        is_image, label, raw_target = match.groups()
        if is_image:
            return f"*{label}*" if label else ""
        target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
        if re.match(r"^(?:https?://|mailto:|#)", target, flags=re.IGNORECASE):
            return match.group(0)
        return label

    text = MARKDOWN_LINK_RE.sub(clean_link, text)
    text = PRIVATE_PATH_RE.sub("[local path omitted]", text)
    replacements = {
        "analysis_meta.json": "local metadata",
        "method_explained_zh.md": "Chinese method notes",
        "output_paper_md": "paper source",
        "PAPER_MD": "paper source",
        "CODE_DIR": "code source",
    }
    for private, public in replacements.items():
        text = re.sub(re.escape(private), public, text, flags=re.IGNORECASE)
    text = text.replace("{{", "&#123;&#123;").replace("{%", "&#123;%")

    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
        if not in_fence:
            heading = HEADING_RE.match(line)
            if heading and len(heading.group(1)) < 6:
                line = "#" + line
        lines.append(line.rstrip())
    return "\n".join(lines).strip()


def detail_slug(method: str, relative_workspace: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", method.casefold()).strip("-") or "paper"
    digest = hashlib.sha256(relative_workspace.encode("utf-8")).hexdigest()[:8]
    return f"{base[:64].rstrip('-')}-{digest}"


def normalize_doi(value: Any) -> str:
    doi = first_text(value)
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.IGNORECASE)
    return doi.rstrip(".").strip()


def normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9\u3400-\u9fff]+", "", value.casefold())


def collect_papers(root: Path, categories: list[Category]) -> tuple[list[Paper], dict[str, int]]:
    papers: dict[str, Paper] = {}
    skipped = {
        "not_ready": 0,
        "private_category": 0,
        "excluded_category": 0,
        "missing_summary": 0,
        "duplicate": 0,
    }
    for workspace in iter_workspaces(root):
        meta = read_json(workspace / "analysis_meta.json")
        if meta.get("ready_to_publish") is not True:
            skipped["not_ready"] += 1
            continue
        relative = workspace.relative_to(root).as_posix()
        category = category_for(relative, categories)
        if category is None:
            skipped["private_category"] += 1
            continue
        if any(
            category.id == prefix or category.id.startswith(f"{prefix}/")
            for prefix in EXCLUDED_CATEGORY_PREFIXES
        ):
            skipped["excluded_category"] += 1
            continue
        readme = meta.get("readme") if isinstance(meta.get("readme"), dict) else {}
        method = first_text(meta.get("paper_short_name"), readme.get("method"), workspace.name)
        title = first_text(meta.get("paper_title"), readme.get("title"), method)
        source_zh = workspace / "method_explained_zh.md"
        source_en = workspace / "summary.md"
        source_zh_text = source_zh.read_text(encoding="utf-8", errors="replace") if source_zh.is_file() else ""
        source_en_text = source_en.read_text(encoding="utf-8", errors="replace") if source_en.is_file() else ""
        summary_zh = clip(summary_section(source_zh_text), 220) if source_zh_text else ""
        summary_en = (
            clip(english_summary_section(source_en_text), 240)
            if source_en_text
            else clip(first_text(readme.get("summary")), 240)
        )
        if not summary_zh and not summary_en:
            skipped["missing_summary"] += 1
            continue
        doi = normalize_doi(meta.get("doi"))
        year_raw = first_text(meta.get("year"), readme.get("year"))
        year_match = re.search(r"(?:19|20)\d{2}", year_raw)
        detail_zh = public_markdown(source_zh_text) or summary_zh or summary_en
        detail_en = public_markdown(source_en_text) or summary_en or summary_zh
        paper = Paper(
            method=method,
            title=title,
            summary_zh=summary_zh or summary_en,
            summary_en=summary_en or summary_zh,
            detail_zh=detail_zh,
            detail_en=detail_en,
            detail_slug=detail_slug(method, relative),
            category_id=category.id,
            category_title=category.title,
            year=year_match.group(0) if year_match else "",
            journal=first_text(meta.get("journal"), readme.get("journal")),
            doi=doi,
            has_code=meta.get("has_code") is True,
        )
        key = "doi:" + doi.casefold() if doi else "title:" + normalize_title(title)
        if key in papers:
            skipped["duplicate"] += 1
            continue
        papers[key] = paper
    ordered = sorted(papers.values(), key=lambda item: (-(int(item.year) if item.year else 0), item.method.casefold()))
    return ordered, skipped


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def esc_method(value: Any) -> str:
    """Escape a method name and allow wrapping after underscores and hyphens.

    Method names are code identifiers such as
    ``Adaptive_Coverage_Policies_Conformal_Prediction``. Without an explicit
    break opportunity the browser either overflows the card or breaks mid-word.
    ``<wbr>`` is used rather than a zero-width space because it contributes
    nothing to ``textContent``, which the client-side search indexes.

    Chromium computes the accessible name across the ``<wbr>`` boundaries as
    "Adaptive_ Coverage_ ...", so callers pair this with an ``aria-label``
    carrying the unbroken name.
    """
    return re.sub(r"([_-])", r"\1<wbr>", esc(value))


def validate_public_output(content: str) -> None:
    for token in FORBIDDEN_OUTPUT:
        if token.casefold() in content.casefold():
            raise ValueError(f"refusing to publish forbidden source marker: {token}")


def render_detail_page(paper: Paper) -> str:
    metadata = " · ".join(part for part in (paper.journal, paper.year) if part)
    metadata_chip = f"\n      <span>{esc(metadata)}</span>" if metadata else ""
    doi_link = ""
    if paper.doi:
        doi_url = "https://doi.org/" + quote(paper.doi, safe="/():;._-")
        doi_link = (
            f'<a class="paper-detail__doi" href="{esc(doi_url)}" target="_blank" '
            'rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" '
            'aria-hidden="true"></i></a>'
        )
    doi_line = f"    {doi_link}\n" if doi_link else ""
    page = f'''---
layout: default
permalink: /paper-atlas/{paper.detail_slug}/
title: {json.dumps(paper.method, ensure_ascii=False)}
nav: false
description: {json.dumps(paper.summary_zh, ensure_ascii=False)}
robots: noindex, nofollow
sitemap: false
---

<!-- Generated locally by bin/export_paper_atlas.py. -->
<section class="paper-detail" id="paper-detail">
  <a class="paper-detail__back" href="{{{{ '/paper-atlas/' | relative_url }}}}">
    <i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Back to Paper Atlas
  </a>
  <header class="paper-detail__hero">
    <div class="paper-detail__chips">
      <span>{esc(paper.category_title)}</span>{metadata_chip}
    </div>
    <h1>{esc(paper.method)}</h1>
    <p>{esc(paper.title)}</p>
{doi_line}  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

{paper.detail_zh}

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

{paper.detail_en}

</article>
</section>

<script defer src="{{{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}}}"></script>
'''
    validate_public_output(page)
    return page


def write_detail_pages(papers: list[Paper], details_dir: Path) -> int:
    details_dir.mkdir(parents=True, exist_ok=True)
    expected = {f"{paper.detail_slug}.md" for paper in papers}
    for stale in details_dir.glob("*.md"):
        if stale.name in expected:
            continue
        try:
            prefix = stale.read_text(encoding="utf-8", errors="replace")[:240]
        except OSError:
            continue
        if "Generated locally by bin/export_paper_atlas.py" in prefix:
            stale.unlink()
    for paper in papers:
        (details_dir / f"{paper.detail_slug}.md").write_text(
            render_detail_page(paper), encoding="utf-8"
        )
    return len(expected)


def render_page(papers: list[Paper], categories: list[Category]) -> str:
    used_ids = {paper.category_id for paper in papers}
    used_categories = [item for item in categories if item.id in used_ids]
    years = sorted({paper.year for paper in papers if paper.year}, reverse=True)
    code_count = sum(paper.has_code for paper in papers)
    year_options = "\n".join(f'          <option value="{year}">{year}</option>' for year in years)
    # The taxonomy is the navigation, so topics are toggles rather than a <select>
    # duplicating the same filter. Sub-topics stay hidden until their parent is
    # active, which keeps the default row scannable.
    parents: list[tuple[Category, int]] = []
    children: list[tuple[Category, int]] = []
    for category in categories:
        count = sum(
            paper.category_id == category.id or paper.category_id.startswith(category.id + "/") for paper in papers
        )
        if not count:
            continue
        (children if "/" in category.path else parents).append((category, count))
    parents.sort(key=lambda item: (-item[1], item[0].order))
    children.sort(key=lambda item: (item[0].id.split("/")[0], -item[1], item[0].order))

    def topic_button(category: Category, count: int, child: bool) -> str:
        # Dashes in taxonomy titles are normalized for display only.
        label = esc(category.title).replace("—", "-").replace("–", "-")
        parent_attr = f' data-atlas-parent="{esc(category.id.split("/")[0])}" hidden' if child else ""
        prefix = "↳ " if child else ""
        return (
            f'      <button type="button" data-atlas-topic="{esc(category.id)}"'
            f'{parent_attr} aria-pressed="false">'
            f"<span>{prefix}{label}</span><strong>{count}</strong></button>"
        )

    topic_buttons = "\n".join(
        [topic_button(category, count, False) for category, count in parents]
        + [topic_button(category, count, True) for category, count in children]
    )
    cards: list[str] = []
    for paper in papers:
        code_badge = (
            '\n          <span class="atlas-chip atlas-chip--code">code available</span>'
            if paper.has_code
            else ""
        )
        metadata = " · ".join(part for part in (paper.journal, paper.year) if part)
        if paper.doi:
            doi_url = "https://doi.org/" + quote(paper.doi, safe="/():;._-")
            paper_link = (
                f'<a class="atlas-doi" href="{esc(doi_url)}" target="_blank" rel="noopener noreferrer" '
                f'aria-label="Open DOI for {esc(paper.method)}">DOI <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>'
            )
        else:
            paper_link = '<span class="atlas-doi atlas-doi--muted">DOI unavailable</span>'
        # Every card carries the same visible link text, so the accessible name
        # names the paper: a screen reader listing links would otherwise hear
        # "完整解读" once per paper with nothing to tell them apart.
        detail_link = (
            f'<a class="atlas-details-link" href="{{{{ \'/paper-atlas/{paper.detail_slug}/\' | relative_url }}}}"'
            f' aria-label="完整解读：{esc(paper.method)}">'
            '完整解读 <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>'
        )
        cards.append(
            f'''      <article class="atlas-card" data-category="{esc(paper.category_id)}" data-year="{esc(paper.year)}" data-code="{"yes" if paper.has_code else "no"}">
        <div class="atlas-card__chips">
          <span class="atlas-chip">{esc(paper.category_title)}</span>{code_badge}
        </div>
        <h2 aria-label="{esc(paper.method)}">{esc_method(paper.method)}</h2>
        <p class="atlas-card__title">{esc(paper.title)}</p>
        <div class="atlas-card__summary-panel" data-atlas-summary="zh" lang="zh-CN">
          <p class="atlas-card__summary-label">中文方法解读</p>
          <p class="atlas-card__summary">{esc(paper.summary_zh)}</p>
        </div>
        <div class="atlas-card__summary-panel" data-atlas-summary="en" lang="en" hidden>
          <p class="atlas-card__summary-label">English Summary</p>
          <p class="atlas-card__summary">{esc(paper.summary_en)}</p>
        </div>
        <footer>
          <span>{esc(metadata)}</span>
          <span class="atlas-card__links">{paper_link}{detail_link}</span>
        </footer>
      </article>'''
        )
    plural = "" if len(papers) == 1 else "s"
    page = f'''---
layout: default
permalink: /paper-atlas/
title: paper atlas
nav: true
nav_order: 2
description: A searchable public index of concise computational biology paper summaries.
robots: noindex, nofollow
sitemap: false
---

<!-- Generated locally by bin/export_paper_atlas.py. -->
<section class="paper-atlas" id="paper-atlas" data-page-size="36">
  <header class="atlas-hero">
    <div class="atlas-hero__top">
      <div>
        <p class="atlas-kicker">Literature notes · computational biology</p>
        <h1>Paper Atlas</h1>
      </div>
      <div class="atlas-stats">
        <span class="atlas-stat"><strong>{len(papers)}</strong><span>papers</span></span>
        <span class="atlas-stat"><strong>{len(used_categories)}</strong><span>topics</span></span>
        <button class="atlas-stat" type="button" id="atlas-code-shortcut"><strong>{code_count}</strong><span>with code</span></button>
      </div>
    </div>
    <p class="atlas-lead">Every paper I have read closely, with a short note on what the method actually does. Search by method, title, journal or note text.</p>
  </header>

  <div class="atlas-topic-list" id="atlas-topics" role="group" aria-label="Filter by topic">
    <button class="is-active" type="button" data-atlas-topic="" aria-pressed="true"><span>All papers</span><strong>{len(papers)}</strong></button>
{topic_buttons}
  </div>

  <form class="atlas-controls" id="atlas-controls" role="search">
    <label class="atlas-search">
      <span class="sr-only">Search papers</span>
      <i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
      <input id="atlas-query" type="search" placeholder="Search method, title, journal or note…" autocomplete="off">
      <kbd aria-hidden="true">/</kbd>
    </label>
    <label>
      <span class="sr-only">Filter by year</span>
      <select id="atlas-year">
        <option value="">All years</option>
{year_options}
      </select>
    </label>
    <label>
      <span class="sr-only">Filter by code availability</span>
      <select id="atlas-code">
        <option value="">Any code status</option>
        <option value="yes">Code available</option>
        <option value="no">No public code found</option>
      </select>
    </label>
    <label>
      <span class="sr-only">Note language</span>
      <select id="atlas-view">
        <option value="zh">中文解读</option>
        <option value="en">English summary</option>
      </select>
    </label>
    <label>
      <span class="sr-only">Sort order</span>
      <select id="atlas-sort">
        <option value="newest">Newest first</option>
        <option value="oldest">Oldest first</option>
        <option value="name">Method A–Z</option>
      </select>
    </label>
    <button id="atlas-reset" type="reset">Reset</button>
  </form>

  <div class="atlas-results-bar">
    <p id="atlas-count" aria-live="polite">Showing <strong>{min(36, len(papers))}</strong> of <strong>{len(papers)}</strong> paper{plural}</p>
    <p id="atlas-active-filters"></p>
  </div>

  <div class="atlas-grid" id="atlas-grid">
{os.linesep.join(cards)}
    <p class="atlas-empty" id="atlas-empty" hidden><strong>No papers match these filters.</strong>Clear the search box or reset the filters to see the full index.</p>
  </div>

  <div class="atlas-more-wrap">
    <button class="atlas-more" id="atlas-more" type="button">Show more</button>
  </div>
</section>

<script defer src="{{{{ '/assets/js/paper-atlas.js' | relative_url | bust_file_cache }}}}"></script>
'''
    validate_public_output(page)
    return page


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Local PaperCode repository root")
    parser.add_argument("--output", required=True, type=Path, help="Generated Jekyll page path")
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if not (source / "taxonomy.yml").is_file():
        parser.error(f"not a PaperCode root: {source}")
    categories = load_categories(source)
    papers, skipped = collect_papers(source, categories)
    if not papers:
        parser.error("no publishable summaries found")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_page(papers, categories), encoding="utf-8")
    details_dir = output.parent / "paper-atlas-details"
    detail_count = write_detail_pages(papers, details_dir)
    print(
        json.dumps(
            {
                "published": len(papers),
                "details": detail_count,
                "output": str(output),
                "details_dir": str(details_dir),
                "skipped": skipped,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
