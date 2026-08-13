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
    "git rev-parse",
    "PaperCode",
)

CODE_HOST_RE = re.compile(
    r"https?://(?:www\.)?(github\.com|gitlab\.com)/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)",
    flags=re.IGNORECASE,
)
CODE_HOST_SKIP = {"topics", "orgs", "features", "settings", "marketplace", "explore"}
INTERNAL_HEADING_RE = re.compile(
    r"provenance|来源合同|采集记录|工作区|local notes|证据入口|可复现性状态",
    flags=re.IGNORECASE,
)
INTERNAL_TEXT_RE = re.compile(
    r"工作区保存|工作区保留|工作区含|本工作区|当前工作区|"
    r"PaperCode|"
    r"git\s+rev-parse|"
    r"acquisition\s+元数据|获取合同|旧合同|采集清单|采集提交|"
    r"\.repo_source|\.repo_commit|"
    r"Provenance|provenance 文件|"
    r"外层\s*PaperCode|外层仓库|"
    r"没有独立\s*`?\.git|嵌套\s*`?\.git|没有独立嵌套|"
    r"源码目录没有|源码目录当前没有|代码目录没有独立|当前代码目录嵌在|模型目录嵌在|"
    r"local metadata|local_dir|"
    r"不能由当前目录|不能用外层|不能拿返回值当作|"
    r"setup\.py 标记版本|"
    r"因此该提交来自|外层 PaperCode 提交不是|"
    r"本次将来源标记|本次以 provenance|本次以采集|"
    r"精确代码 provenance|不能伪造",
    flags=re.IGNORECASE,
)
SENTENCE_RE = re.compile(r".+?(?:[。！？；]|[.!?](?=\s|$)|$)", flags=re.DOTALL)
JOURNAL_YEAR_RE = re.compile(r"\s*·\s*(?:19|20)\d{2}\s*$")

# Topics currently shown on the public Paper Atlas. Other PaperCode trees
# (foundation models, GRN / causal networks, LLM agents, za) stay local.
ALLOWED_CATEGORY_PREFIXES = {
    "communication_interaction",
    "computational_tools",
    "datasource",
    "deconvolution_mapping",
    "domain_clustering",
    "dynamics_fate_trajectory",
    "integration_multimodal",
    "machine_learning_algorithm",
    "protein_sequence_models",
    "representation_models",
    "scATAC",
    "segmentation_annotation",
    "svg_patterning",
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
    code_url: str = ""


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


def normalize_code_url(value: str) -> str:
    match = CODE_HOST_RE.search(value or "")
    if not match:
        return ""
    host, owner, repo = match.group(1).lower(), match.group(2), match.group(3)
    if owner.casefold() in CODE_HOST_SKIP:
        return ""
    repo = re.sub(r"\.git$", "", repo, flags=re.IGNORECASE)
    return f"https://{host}/{owner}/{repo}"


def read_repo_source_url(workspace: Path) -> str:
    """Read the first GitHub/GitLab URL from a workspace .repo_source file."""
    for path in iter_repo_source_files(workspace):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.casefold().startswith("url:"):
                url = normalize_code_url(stripped.split(":", 1)[1])
                if url:
                    return url
        url = normalize_code_url(text)
        if url:
            return url
    return ""


def iter_repo_source_files(workspace: Path) -> Iterable[Path]:
    for current, dirnames, filenames in os.walk(workspace):
        dirnames[:] = sorted(
            name for name in dirnames if name not in SKIP_DIRS and not name.startswith(".")
        )
        if ".repo_source" in filenames:
            yield Path(current) / ".repo_source"
        relative = Path(current).relative_to(workspace)
        if len(relative.parts) >= 2:
            dirnames[:] = []


def resolve_code_url(meta: dict[str, Any], workspace: Path, method: str, *note_texts: str) -> str:
    """Prefer analysis_meta.code_repo_url, then .repo_source, then note text."""
    for key in ("code_repo_url", "code_url", "repo", "github", "code"):
        url = normalize_code_url(first_text(meta.get(key)))
        if url:
            return url
    url = read_repo_source_url(workspace)
    if url:
        return url
    return extract_code_url(*note_texts, method=method)


def extract_code_url(*texts: str, method: str = "") -> str:
    """Prefer provenance mentions, then a repo whose name matches the method."""
    method_key = re.sub(r"[^a-z0-9]+", "", (method or "").casefold())
    internal_urls: list[str] = []
    matching_urls: list[str] = []
    for text in texts:
        if not text:
            continue
        for match in CODE_HOST_RE.finditer(text):
            url = normalize_code_url(match.group(0))
            if not url:
                continue
            window = text[max(0, match.start() - 180) : min(len(text), match.end() + 80)]
            if is_internal_text(window):
                internal_urls.append(url)
            repo = re.sub(r"[^a-z0-9]+", "", url.rstrip("/").split("/")[-1].casefold())
            if method_key and len(method_key) >= 4 and (method_key[:4] in repo or repo[:4] in method_key):
                matching_urls.append(url)
    if internal_urls:
        return internal_urls[0]
    if matching_urls:
        return matching_urls[0]
    return ""


def journal_key(value: str) -> str:
    label = journal_label(value)
    folded = label.casefold()
    if "arxiv" in folded:
        return "arxiv"
    if "proceedings of machine learning research" in folded or folded.startswith("pmlr"):
        return "pmlr"
    return re.sub(r"[^a-z0-9]+", "-", folded).strip("-")


def journal_label(value: str) -> str:
    text = JOURNAL_YEAR_RE.sub("", html.unescape(value or "")).strip()
    folded = text.casefold()
    if not text or re.fullmatch(r"(?:19|20)\d{2}", text):
        return ""
    if "arxiv" in folded:
        return "arXiv"
    if "biorxiv" in folded:
        return "bioRxiv"
    if (
        "proceedings of machine learning research" in folded
        or "pmlr" in folded
        or re.search(r"\bicml\b", folded)
        or "international conference on machine learning" in folded
    ):
        return "PMLR"
    if "neurips" in folded or "neural information processing" in folded:
        return "NeurIPS"
    if "iclr" in folded or "international conference on learning representations" in folded:
        return "ICLR"
    if "aistats" in folded:
        return "AISTATS"
    if "aaai" in folded:
        return "AAAI"
    if folded in {"pnas"} or "national academy of sciences" in folded:
        return "PNAS"
    return text


def is_internal_text(value: str) -> bool:
    return bool(INTERNAL_TEXT_RE.search(value or ""))


def strip_internal_sentences(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    if re.match(r"^(?:[-*+]|\d+[.)])\s", stripped):
        items = re.split(r"\n(?=(?:[-*+]|\d+[.)])\s)", stripped)
        kept = [item for item in items if not is_internal_text(item)]
        return "\n".join(kept).strip()
    pieces = [match.group(0) for match in SENTENCE_RE.finditer(stripped)]
    if not pieces:
        return "" if is_internal_text(stripped) else stripped
    return "".join(piece for piece in pieces if not is_internal_text(piece)).strip()


def strip_internal_notes(markdown: str) -> str:
    """Drop workspace / provenance sentences that should not ship publicly."""
    lines = markdown.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    in_fence = False
    skipping_level: int | None = None

    def flush() -> None:
        if not paragraph:
            return
        cleaned = strip_internal_sentences("\n".join(paragraph))
        if cleaned:
            out.append(cleaned)
        paragraph.clear()

    for line in lines:
        if FENCE_RE.match(line):
            flush()
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        heading = HEADING_RE.match(line)
        if heading:
            flush()
            level = len(heading.group(1))
            if skipping_level is not None:
                if level > skipping_level:
                    continue
                skipping_level = None
            if INTERNAL_HEADING_RE.search(heading.group(2)):
                skipping_level = level
                continue
            out.append(line)
            continue
        if skipping_level is not None:
            continue
        if not line.strip():
            flush()
            if out and out[-1] != "":
                out.append("")
            continue
        paragraph.append(line)
    flush()
    text = "\n".join(out).strip()
    return re.sub(r"\n{3,}", "\n\n", text)


def category_allowed(category_id: str) -> bool:
    return any(
        category_id == prefix or category_id.startswith(f"{prefix}/")
        for prefix in ALLOWED_CATEGORY_PREFIXES
    )


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
        if not category_allowed(category.id):
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
        detail_zh = strip_internal_notes(public_markdown(source_zh_text)) or summary_zh or summary_en
        detail_en = strip_internal_notes(public_markdown(source_en_text)) or summary_en or summary_zh
        code_url = resolve_code_url(meta, workspace, method, source_zh_text, source_en_text)
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
            journal=journal_label(first_text(meta.get("journal"), readme.get("journal"))),
            doi=doi,
            has_code=meta.get("has_code") is True or bool(code_url),
            code_url=code_url,
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


def hero_links(paper: Paper, doi_class: str, code_class: str) -> str:
    links: list[str] = []
    if paper.doi:
        doi_url = "https://doi.org/" + quote(paper.doi, safe="/():;._-")
        links.append(
            f'<a class="{doi_class}" href="{esc(doi_url)}" target="_blank" '
            f'rel="noopener noreferrer" aria-label="Open DOI for {esc(paper.method)}">'
            f'{"Open paper" if doi_class.startswith("paper-detail") else "DOI"} '
            f'<i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>'
        )
    if paper.code_url:
        links.append(
            f'<a class="{code_class}" href="{esc(paper.code_url)}" target="_blank" '
            f'rel="noopener noreferrer" aria-label="Open code for {esc(paper.method)}">'
            f'Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>'
        )
    return "".join(links)


def render_detail_page(paper: Paper) -> str:
    metadata = " · ".join(part for part in (paper.journal, paper.year) if part)
    metadata_chip = f"\n      <span>{esc(metadata)}</span>" if metadata else ""
    links = hero_links(paper, "paper-detail__doi", "paper-detail__code")
    links_line = f'    <div class="paper-detail__links">{links}</div>\n' if links else ""
    page = f'''---
layout: default
permalink: /paper-atlas/{paper.detail_slug}/
title: {json.dumps(paper.method, ensure_ascii=False)}
nav: false
wide: true
description: {json.dumps(paper.summary_zh, ensure_ascii=False)}
robots: noindex, nofollow
sitemap: false
---

<!-- Generated locally by bin/export_paper_atlas.py. -->
<section class="paper-detail" id="paper-detail">
  <a class="paper-detail__back" href="{{{{ '/paper-atlas/' | relative_url }}}}" data-atlas-back>
    <i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Back to Paper Atlas
  </a>
  <header class="paper-detail__hero">
    <div class="paper-detail__chips">
      <span>{esc(paper.category_title)}</span>{metadata_chip}
    </div>
    <h1>{esc(paper.method)}</h1>
    <p>{esc(paper.title)}</p>
{links_line}  </header>

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
    code_count = sum(1 for paper in papers if paper.has_code or paper.code_url)
    year_options = "\n".join(f'          <option value="{year}">{year}</option>' for year in years)
    journal_counts: dict[str, tuple[str, int]] = {}
    for paper in papers:
        key = journal_key(paper.journal)
        if not key:
            continue
        label, count = journal_counts.get(key, (journal_label(paper.journal), 0))
        journal_counts[key] = (label, count + 1)
    journal_options = "\n".join(
        f'          <option value="{esc(key)}">{esc(label)} ({count})</option>'
        for key, (label, count) in sorted(
            journal_counts.items(), key=lambda item: (-item[1][1], item[1][0].casefold())
        )
    )
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
        metadata = " · ".join(part for part in (paper.journal, paper.year) if part)
        paper_links = hero_links(paper, "atlas-doi", "atlas-code-link")
        has_code = paper.has_code or bool(paper.code_url)
        # Every card carries the same visible link text, so the accessible name
        # names the paper: a screen reader listing links would otherwise hear
        # "完整解读" once per paper with nothing to tell them apart.
        detail_link = (
            f'<a class="atlas-details-link" href="{{{{ \'/paper-atlas/{paper.detail_slug}/\' | relative_url }}}}"'
            f' aria-label="完整解读：{esc(paper.method)}">'
            '完整解读 <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>'
        )
        code_mark = (
            '<span class="atlas-code-mark">code</span>'
            if has_code
            else ""
        )
        cards.append(
            f'''      <article class="atlas-card" data-category="{esc(paper.category_id)}" data-year="{esc(paper.year)}" data-code="{"yes" if has_code else "no"}" data-journal="{esc(journal_key(paper.journal))}" data-journal-label="{esc(journal_label(paper.journal))}" data-method="{esc(paper.method)}">
        <div class="atlas-card__chips">
          <span class="atlas-chip">{esc(paper.category_title)}</span>{code_mark}
        </div>
        <h2 aria-label="{esc(paper.method)}">{esc_method(paper.method)}</h2>
        <p class="atlas-card__title">{esc(paper.title)}</p>
        <div class="atlas-card__summary-panel" data-atlas-summary="zh" lang="zh-CN">
          <p class="atlas-card__summary">{esc(paper.summary_zh)}</p>
        </div>
        <div class="atlas-card__summary-panel" data-atlas-summary="en" lang="en" hidden>
          <p class="atlas-card__summary">{esc(paper.summary_en)}</p>
        </div>
        <footer>
          <span>{esc(metadata)}</span>
          <span class="atlas-card__links">{paper_links}{detail_link}</span>
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
wide: true
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
        <button class="atlas-stat" type="button" id="atlas-code-shortcut" aria-pressed="false"><strong>{code_count}</strong><span>with code</span></button>
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
      <input id="atlas-query" name="q" type="search" placeholder="Search method, title, journal or note…" autocomplete="off">
      <kbd aria-hidden="true">/</kbd>
    </label>
    <label>
      <span class="sr-only">Filter by year</span>
      <select id="atlas-year" name="year">
        <option value="">All years</option>
{year_options}
      </select>
    </label>
    <label>
      <span class="sr-only">Filter by journal</span>
      <select id="atlas-journal" name="journal">
        <option value="">All journals</option>
{journal_options}
      </select>
    </label>
    <label>
      <span class="sr-only">Filter by code availability</span>
      <select id="atlas-code" name="code">
        <option value="">Any code status</option>
        <option value="yes">Code available</option>
        <option value="no">No public code found</option>
      </select>
    </label>
    <label>
      <span class="sr-only">Note language</span>
      <select id="atlas-view" name="lang">
        <option value="zh">中文解读</option>
        <option value="en">English summary</option>
      </select>
    </label>
    <label>
      <span class="sr-only">Sort order</span>
      <select id="atlas-sort" name="sort">
        <option value="newest">Newest first</option>
        <option value="oldest">Oldest first</option>
        <option value="name">Method A–Z</option>
      </select>
    </label>
    <button id="atlas-reset" type="reset">Reset</button>
  </form>

  <div class="atlas-results-bar">
    <p id="atlas-count" aria-live="polite">Showing <strong>{min(36, len(papers))}</strong> of <strong>{len(papers)}</strong> paper{plural}</p>
    <div class="atlas-results-actions">
      <p id="atlas-active-filters"></p>
      <div class="atlas-layout" role="group" aria-label="Result layout">
        <button type="button" data-atlas-layout="cards" class="is-active" aria-pressed="true">Cards</button>
        <button type="button" data-atlas-layout="list" aria-pressed="false">List</button>
      </div>
    </div>
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


def panel_markdown(page: str, lang: str) -> str:
    marker = f'data-detail-panel="{lang}"'
    start = page.find(marker)
    if start < 0:
        return ""
    open_end = page.find(">", start)
    close = page.find("</article>", open_end)
    if open_end < 0 or close < 0:
        return ""
    return page[open_end + 1 : close].strip()


def parse_published_paper(path: Path, index_meta: dict[str, dict[str, str]]) -> Paper | None:
    page = path.read_text(encoding="utf-8", errors="replace")
    if "Generated locally by bin/export_paper_atlas.py" not in page[:2000]:
        return None
    slug = path.stem
    method = html.unescape(
        re.search(r"<h1>(.*?)</h1>", page, flags=re.DOTALL).group(1)
        if re.search(r"<h1>(.*?)</h1>", page, flags=re.DOTALL)
        else slug
    )
    title_match = re.search(
        r'<header class="paper-detail__hero">.*?<p>(.*?)</p>', page, flags=re.DOTALL
    )
    title = html.unescape(title_match.group(1)).strip() if title_match else method
    chips = re.findall(
        r'<div class="paper-detail__chips">\s*(.*?)\s*</div>', page, flags=re.DOTALL
    )
    spans = re.findall(r"<span>(.*?)</span>", chips[0]) if chips else []
    category_title = html.unescape(spans[0]).strip() if spans else ""
    journal, year = "", ""
    if len(spans) > 1:
        meta = html.unescape(spans[1])
        year_match = re.search(r"(?:19|20)\d{2}", meta)
        year = year_match.group(0) if year_match else ""
        journal = journal_label(meta)
    doi_match = re.search(r'https://doi\.org/([^"\s]+)', page)
    doi = html.unescape(doi_match.group(1)) if doi_match else ""
    detail_zh = strip_internal_notes(panel_markdown(page, "zh"))
    detail_en = strip_internal_notes(panel_markdown(page, "en"))
    code_url = extract_code_url(page, method=method)
    card = index_meta.get(slug, {})
    return Paper(
        method=method,
        title=title,
        summary_zh=card.get("summary_zh") or clip(summary_section(detail_zh) or detail_zh, 220),
        summary_en=card.get("summary_en") or clip(english_summary_section(detail_en) or detail_en, 240),
        detail_zh=detail_zh or card.get("summary_zh") or title,
        detail_en=detail_en or card.get("summary_en") or title,
        detail_slug=slug,
        category_id=card.get("category_id") or re.sub(r"[^a-z0-9_/]+", "", category_title.casefold()),
        category_title=card.get("category_title") or category_title,
        year=card.get("year") or year,
        journal=card.get("journal") or journal,
        doi=doi,
        has_code=card.get("has_code") == "yes" or bool(code_url),
        code_url=code_url,
    )


def parse_index_cards(index_path: Path) -> dict[str, dict[str, str]]:
    text = index_path.read_text(encoding="utf-8", errors="replace")
    cards: dict[str, dict[str, str]] = {}
    for match in re.finditer(
        r'<article class="atlas-card" data-category="([^"]*)" data-year="([^"]*)" data-code="([^"]*)"[^>]*>\s*'
        r'<div class="atlas-card__chips">\s*<span class="atlas-chip">(.*?)</span>.*?</div>\s*'
        r"<h2 aria-label=\"([^\"]*)\">.*?</h2>\s*"
        r'<p class="atlas-card__title">(.*?)</p>\s*'
        r'<div class="atlas-card__summary-panel" data-atlas-summary="zh"[^>]*>\s*'
        r'(?:<p class="atlas-card__summary-label">.*?</p>\s*)?'
        r'<p class="atlas-card__summary">(.*?)</p>.*?'
        r'<div class="atlas-card__summary-panel" data-atlas-summary="en"[^>]*>\s*'
        r'(?:<p class="atlas-card__summary-label">.*?</p>\s*)?'
        r'<p class="atlas-card__summary">(.*?)</p>.*?'
        r'<a class="atlas-details-link" href="\{\{ \'/paper-atlas/([^/]+)/\'',
        text,
        flags=re.DOTALL,
    ):
        slug = match.group(9)
        cards[slug] = {
            "category_id": html.unescape(match.group(1)),
            "year": html.unescape(match.group(2)),
            "has_code": html.unescape(match.group(3)),
            "category_title": html.unescape(match.group(4)),
            "method": html.unescape(match.group(5)),
            "title": html.unescape(match.group(6)),
            "summary_zh": html.unescape(match.group(7)),
            "summary_en": html.unescape(match.group(8)),
            "journal": "",
        }
    return cards


def categories_from_papers(papers: list[Paper]) -> list[Category]:
    seen: dict[str, Category] = {}
    for paper in papers:
        if paper.category_id in seen:
            continue
        seen[paper.category_id] = Category(
            id=paper.category_id,
            title=paper.category_title,
            path=paper.category_id,
            order=len(seen) + 1,
        )
    return list(seen.values())


def rebuild_published(output: Path) -> tuple[list[Paper], int]:
    details_dir = output.parent / "paper-atlas-details"
    index_meta = parse_index_cards(output) if output.is_file() else {}
    papers: list[Paper] = []
    for path in sorted(details_dir.glob("*.md")):
        paper = parse_published_paper(path, index_meta)
        if paper:
            papers.append(paper)
    papers.sort(key=lambda item: (-(int(item.year) if item.year else 0), item.method.casefold()))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_page(papers, categories_from_papers(papers)), encoding="utf-8")
    return papers, write_detail_pages(papers, details_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Local PaperCode repository root")
    parser.add_argument("--output", required=True, type=Path, help="Generated Jekyll page path")
    parser.add_argument(
        "--rebuild-published",
        action="store_true",
        help="Rebuild from already published index and detail pages",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if args.rebuild_published:
        papers, detail_count = rebuild_published(output)
        print(
            json.dumps(
                {
                    "published": len(papers),
                    "details": detail_count,
                    "output": str(output),
                    "with_code_url": sum(bool(paper.code_url) for paper in papers),
                },
                ensure_ascii=False,
            )
        )
        return 0
    if not args.source:
        parser.error("either --source or --rebuild-published is required")
    source = args.source.resolve()
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
