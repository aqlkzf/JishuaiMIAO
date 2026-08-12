#!/usr/bin/env python3
"""Export a public, summary-only PaperCode page for the personal website.

The exporter deliberately writes one rendered Jekyll page. It never copies
analysis Markdown, code snapshots, workspace paths, or a machine-readable
JSON catalog into the website repository.
"""

from __future__ import annotations

import argparse
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
SOURCE_CITATION_RE = re.compile(
    r"[（(][^（）()]{0,180}(?:\.md|\.py|\.R|\.ipynb|PAPER_MD|CODE_DIR)[^（）()]{0,180}[）)]",
    flags=re.IGNORECASE,
)
FORBIDDEN_OUTPUT = (
    "/workspace/",
    "/home/shuai/",
    "analysis_meta.json",
    "method_explained_zh.md",
    "output_paper_md",
    "CODE_DIR",
)


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
    summary: str
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


def summary_section(markdown: str) -> str:
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if not match or len(match.group(1)) > 2 or not SUMMARY_HEADING_RE.search(match.group(2)):
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


def clip(text: str, limit: int = 220) -> str:
    text = WHITESPACE_RE.sub(" ", text).strip()
    if len(text) <= limit:
        return text
    prefix = text[: limit + 1]
    boundary = max(prefix.rfind(mark) for mark in "。！？；.!?")
    if boundary >= int(limit * 0.58):
        return prefix[: boundary + 1]
    return prefix[:limit].rstrip("，、；,:： ") + "…"


def normalize_doi(value: Any) -> str:
    doi = first_text(value)
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.IGNORECASE)
    return doi.rstrip(".").strip()


def normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9\u3400-\u9fff]+", "", value.casefold())


def collect_papers(root: Path, categories: list[Category]) -> tuple[list[Paper], dict[str, int]]:
    papers: dict[str, Paper] = {}
    skipped = {"not_ready": 0, "private_category": 0, "missing_summary": 0, "duplicate": 0}
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
        readme = meta.get("readme") if isinstance(meta.get("readme"), dict) else {}
        method = first_text(meta.get("paper_short_name"), readme.get("method"), workspace.name)
        title = first_text(meta.get("paper_title"), readme.get("title"), method)
        source = workspace / "method_explained_zh.md"
        source_text = source.read_text(encoding="utf-8", errors="replace") if source.is_file() else ""
        summary = clip(summary_section(source_text) if source_text else first_text(readme.get("summary")))
        if not summary:
            skipped["missing_summary"] += 1
            continue
        doi = normalize_doi(meta.get("doi"))
        year_raw = first_text(meta.get("year"), readme.get("year"))
        year_match = re.search(r"(?:19|20)\d{2}", year_raw)
        paper = Paper(
            method=method,
            title=title,
            summary=summary,
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


def render_page(papers: list[Paper], categories: list[Category]) -> str:
    used_ids = {paper.category_id for paper in papers}
    used_categories = [item for item in categories if item.id in used_ids]
    years = sorted({paper.year for paper in papers if paper.year}, reverse=True)
    code_count = sum(paper.has_code for paper in papers)
    category_options = "\n".join(
        f'          <option value="{esc(item.id)}">{esc(item.title)}</option>' for item in used_categories
    )
    year_options = "\n".join(f'          <option value="{year}">{year}</option>' for year in years)
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
        cards.append(
            f'''      <article class="atlas-card" data-category="{esc(paper.category_id)}" data-year="{esc(paper.year)}" data-code="{"yes" if paper.has_code else "no"}">
        <div class="atlas-card__chips">
          <span class="atlas-chip">{esc(paper.category_title)}</span>{code_badge}
        </div>
        <h2>{esc(paper.method)}</h2>
        <p class="atlas-card__title">{esc(paper.title)}</p>
        <p class="atlas-card__summary" lang="zh-CN">{esc(paper.summary)}</p>
        <footer>
          <span>{esc(metadata)}</span>
          {paper_link}
        </footer>
      </article>'''
        )
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

<!-- Generated locally. This page contains public summaries only; no source workspace data is embedded. -->
<section class="paper-atlas" id="paper-atlas" data-page-size="36">
  <header class="atlas-hero">
    <p class="atlas-kicker">Literature notes · computational biology</p>
    <h1>Paper Atlas</h1>
    <p class="atlas-lead">A compact, searchable map of methods and papers I have read. 每篇仅展示中文短摘要；完整笔记、分析文件、代码快照和数据不在本网站中。</p>
    <div class="atlas-stats" aria-label="Atlas statistics">
      <div><strong>{len(papers)}</strong><span>papers</span></div>
      <div><strong>{len(used_categories)}</strong><span>topics</span></div>
      <div><strong>{code_count}</strong><span>with code</span></div>
    </div>
  </header>

  <aside class="atlas-privacy" aria-label="Public data boundary">
    <i class="fa-solid fa-shield-halved" aria-hidden="true"></i>
    <div><strong>Public summary layer only.</strong> This page has no bulk-download endpoint and does not contain the underlying PaperCode workspaces. Public HTML can still be read or scraped, so no static site can promise copy prevention.</div>
  </aside>

  <form class="atlas-controls" id="atlas-controls" role="search">
    <label class="atlas-search">
      <span class="sr-only">Search papers</span>
      <i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
      <input id="atlas-query" type="search" placeholder="Search method, title, journal or summary…" autocomplete="off">
    </label>
    <label>
      <span class="sr-only">Filter by topic</span>
      <select id="atlas-category">
        <option value="">All topics</option>
{category_options}
      </select>
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
    <button id="atlas-reset" type="reset">Reset</button>
  </form>

  <div class="atlas-results-bar">
    <p id="atlas-count" aria-live="polite">Showing {min(36, len(papers))} of {len(papers)} papers</p>
    <p>Newest first</p>
  </div>

  <div class="atlas-grid" id="atlas-grid">
{os.linesep.join(cards)}
  </div>

  <p class="atlas-empty" id="atlas-empty" hidden>No papers match these filters.</p>
  <div class="atlas-more-wrap">
    <button class="atlas-more" id="atlas-more" type="button">Show more</button>
  </div>
</section>

<script defer src="{{{{ '/assets/js/paper-atlas.js' | relative_url | bust_file_cache }}}}"></script>
'''
    for token in FORBIDDEN_OUTPUT:
        if token.casefold() in page.casefold():
            raise ValueError(f"refusing to publish forbidden source marker: {token}")
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
    print(json.dumps({"published": len(papers), "output": str(output), "skipped": skipped}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
