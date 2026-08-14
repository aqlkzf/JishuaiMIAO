---
layout: default
permalink: /paper-atlas/llm4cell-e9d0b7aa/
title: "LLM4Cell"
nav: false
wide: true
description: "LLM4Cell is a survey of language-like, foundation, multimodal, and agentic models for single-cell biology. It addresses a fragmented literature in which RNA, ATAC, spatial, multi-omic, perturbation, and text-grounded systems use incompatibl…"
robots: noindex, nofollow
sitemap: false
---

<!-- Generated locally by bin/export_paper_atlas.py. -->
<section class="paper-detail" id="paper-detail">
  <a class="paper-detail__back" href="{{ '/paper-atlas/' | relative_url }}" data-atlas-back>
    <i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Back to Paper Atlas
  </a>
  <header class="paper-detail__hero">
    <div class="paper-detail__chips">
      <span>Representation Models</span>
      <span>arXiv · 2025</span>
    </div>
    <h1>LLM4Cell</h1>
    <p>LLM4Cell: A Survey of Large Language and Agentic Models for Single-Cell Biology</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2510.07793" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for LLM4Cell">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

LLM4Cell is a survey of language-like, foundation, multimodal, and agentic models for single-cell biology. It addresses a fragmented literature in which RNA, ATAC, spatial, multi-omic, perturbation, and text-grounded systems use incompatibl…

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## LLM4Cell review summary

### Scope and problem

LLM4Cell is a survey of language-like, foundation, multimodal, and agentic models for single-cell biology. It addresses a fragmented literature in which RNA, ATAC, spatial, multi-omic, perturbation, and text-grounded systems use incompatible task definitions and evaluation practices. The paper's stated goal is to link models, datasets, tasks, and domain-level reliability concerns in one reference map rather than introduce a new predictive model (paper source:8-25, 44-54).

### What the survey contributes

- A registry of 58 representative methods, grouped into Foundation, Text-Bridge, Spatial/Multimodal, Epigenomic, and Agentic families.
- A task view covering annotation/ontology mapping, trajectory and perturbation, multi-omic integration, spatial mapping/deconvolution, regulatory inference, cross-species translation, generation/simulation, and drug-response prediction.
- A dataset view of 40+ public resources spanning RNA, ATAC, paired/tri-modal omics, spatial imaging, perturbation/drug response, and plants.
- A ten-domain rubric: biological grounding, batch effects, multi-omics alignment, trajectory/perturbation, cross-species generalization, atlas fairness, explainability, privacy/ethics, scalability, and emerging/agentic behavior (paper source:56-104, 184-249).

### Main synthesis

Foundation models dominate annotation, integration, trajectory, and generation because atlas-scale transcriptomic pretraining is relatively mature. Text-bridge systems add ontology or literature grounding and improve interpretability, but depend on curated text and usually remain non-agentic. Spatial/multimodal systems add tissue context or cross-omic alignment, at the cost of heterogeneous resolutions and limited paired benchmarks. Epigenomic systems model peaks, motifs, and enhancer-gene structure, but face sparse data and weak common ground truth. Agentic systems add an LLM controller, memory/planning, and tool or ontology interfaces; their strongest claimed differentiators are interaction and explainability, while their weakest evidence is standardized reasoning fidelity and reproducibility (paper source:71-104, 184-249, 489-542).

The task counts in the survey's first figure make annotation/labeling the dominant category (41 mentions), followed by perturbation prediction (19), generation/text (16), integration/alignment (15), retrieval/search and spatial mapping (10 each), and much smaller counts for trajectory inference, cell-cell communication, and multicellular summaries. The domain counts are similarly skewed toward biological grounding (56 models), scalability (49), explainability (45), and batch effects (42), while privacy/ethics appears for only one model (paper source; paper source:699-711).

### Evidence and limitations

The paper reports a literature search over PubMed, Google Scholar, arXiv, and Semantic Scholar, approximately 8,020 initial hits, 5,510 abstract-available English records, and manual screening to 58 methods. It includes preprints and says active GitHub or Zenodo links were cross-checked, but the article does not provide a machine-readable screening file, per-model evidence scores, or a reproducible script for the rubric (paper source:394-436).

The authors explicitly caution that reported metrics are not directly comparable, the ten-domain rubric is qualitative rather than a calibrated ranking, clinical/proprietary spatial data were excluded, non-animal data are sparse, and compute/hyperparameter sensitivity was not systematically analyzed (paper source:289-299). The converted arXiv source also has a presentation mismatch: the first local image is a domain/task-frequency chart, while the text labels it Figure 2; the taxonomy Figure 1 is captioned but has no separate local image in the conversion. This is retained as a source caveat rather than silently corrected.

### Reproducibility and implementation status

This is a review paper, so there is no single implementation to reproduce. The arXiv HTML and abstract code panel expose no official LLM4Cell GitHub repository; a focused GitHub API search for `LLM4Cell` returned only the unrelated `SmallHorseBrother/META_LLM4Celltype` repository. The paper does cite many component-model repositories and one benchmark repository (`QuKunLab/MultiomeBenchmarking` in Appendix Table 3), but cloning any of those would not reproduce the survey. `code source` is therefore intentionally absent and `has_code=false`.

### Bottom line

LLM4Cell is most useful as a landscape and evaluation-design map: it makes the modality/task/domain gaps visible and gives a practical checklist for choosing or benchmarking a model. Its strongest claims are organizational and diagnostic. Its weakest claims are quantitative comparisons across heterogeneous papers and the implicit reliability of manually assigned domain scores. The next technically valuable artifact would be a versioned benchmark with explicit inclusion records, reproducible per-model evidence, calibrated metrics, and agentic reasoning tests.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
