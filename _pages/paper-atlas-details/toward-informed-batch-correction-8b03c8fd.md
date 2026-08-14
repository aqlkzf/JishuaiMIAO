---
layout: default
permalink: /paper-atlas/toward-informed-batch-correction-8b03c8fd/
title: "Toward informed batch correction"
nav: false
wide: true
description: "Li et al. review why single-cell transcriptome integration remains vulnerable to batch effects and argue for informed correction: model technical and biological variation with interpretable gene- and cell-level representations rather than t…"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Computational Science · 2026</span>
    </div>
    <h1>Toward informed batch correction</h1>
    <p>Toward informed batch correction for single-cell transcriptome integration</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s43588-025-00943-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Toward informed batch correction">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

Li et al. review why single-cell transcriptome integration remains vulnerable to batch effects and argue for informed correction: model technical and biological variation with interpretable gene- and cell-level representations rather than t…

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Review Summary

### Scope and evidence

Li et al. review why single-cell transcriptome integration remains vulnerable to batch effects and argue for *informed* correction: model technical and biological variation with interpretable gene- and cell-level representations rather than treating all between-dataset variation as nuisance. The abstract is available in the acquired Nature HTML (`paper source/nature_html/paper.md:1-17`). The publisher serves the body as subscription-only; the local source therefore does not contain the Introduction, main text, Methods, Results, or full legends. Claims below are limited to the abstract, three inspected figures, and the reference list; unavailable details remain `MISSING`.

### Central message

The review frames integration as a decision problem: remove variation that is known to be technical, while retaining biological differences that may be real. Figure 1a distinguishes better-characterized cleaning targets (ambient RNA, empty droplets, capture rate and sequencing depth) from poorly characterized batch-correction factors (other technical factors and donor variability). Figure 1b illustrates the failure modes: undercorrection leaves batch structure, whereas overcorrection erases cell-state structure. The proposed direction is not a new algorithm but a research agenda for interpretable, informed models (abstract; `figure_01.png`).

### Landscape taxonomy

1. **Upstream data cleaning.** Detect or model ambient RNA, empty droplets, doublets and library/capture-quality variation before integration. These targets have comparatively explicit measurement mechanisms (Fig. 1a; refs. 5, 9, 18, 21, 22).
2. **Normalization and variance modeling.** Transform counts and model mean-variance structure before comparing cells (refs. 4, 24, 25, 31, 32).
3. **Embedding/integration.** Correct or align latent spaces using linear, graph, mutual-nearest-neighbor, matrix-factorization, or deep generative approaches. The timeline in Fig. 2 places methods from early MNN/graph and linear corrections through Harmony, Scanorama, scVI/scANVI, scArches/reference mapping and later foundation-model approaches; exact year-to-method assignments should be checked against the unavailable full text.
4. **Evaluation and biological validation.** Integration quality is multi-objective: batch mixing alone cannot establish success because cell-type/state conservation and downstream differential testing must also be preserved (refs. 3, 8, 10, 11, 95).
5. **Informed representations.** Figure 3 motivates decomposing a cell's transcriptomic signature into contributions from cell identity/state, shared housekeeping programs and nuisance programs such as stress or cell-cycle effects. This conceptual decomposition is the review's forward-looking proposal, not a specified trainable model in the accessible text.

### Major-method comparison

| Family | Representative methods cited | What is modeled | Main strength | Main risk / evidence status |
|---|---|---|---|---|
| Ambient-RNA correction | SoupX, DecontX, CellBender, scCDC | Contamination/background | Targets an explicit measurement artifact | Requires assumptions about ambient profiles; detailed comparisons are `MISSING` (refs. 5, 18, 21, 22) |
| Empty-droplet/doublet QC | EmptyDrops and doublet detectors (refs. 9, 44, 45) | Cell-calling and mixed droplets | Prevents obvious non-cell or composite profiles entering integration | Threshold and platform dependence; full review discussion `MISSING` |
| Linear/statistical correction | ComBat, limma/edgeR-style models, linear latent factors | Batch covariates and mean/variance shifts | Transparent and computationally tractable | Can remove biology when design is confounded; exact recommended use `MISSING` (refs. 24, 25, 102) |
| MNN/graph alignment | fastMNN, BBKNN, Scanorama | Local neighborhoods across datasets | Captures nonlinear local correspondences | Depends on shared populations and neighbor geometry (refs. 56, 57, 40) |
| Latent-variable/deep generative | scVI, scANVI, scGen, scPoli, scArches | Probabilistic latent state conditioned on batch/labels | Flexible uncertainty and reference mapping | Model/design assumptions and interpretability; detailed evidence `MISSING` (refs. 67, 68, 73, 75, 79) |
| Iterative embedding correction | Harmony, Seurat integration, LIGER | Cluster/embedding alignment | Broad ecosystem adoption | Mixing objectives can trade off rare-state fidelity (refs. 42, 43, 52, 103) |
| Foundation-model/reference approaches | scGPT, Geneformer, scPRINT and related models | Pretrained gene/cell representations | Potential transfer and shared representations | Review does not provide an accessible benchmark or reproducibility recipe; `MISSING` (refs. 80-90) |

### Key findings and open problems

- **Batch is not a single variable.** The review separates measurable cleaning artifacts from donor/technical factors whose causal structure is less characterized (Fig. 1a).
- **The objective is inherently constrained.** Figure 1b makes the undercorrection/overcorrection trade-off explicit; an integration score that rewards mixing alone is insufficient.
- **Feature choice matters.** The cited feature-selection study (ref. 6) signals that gene selection is part of the integration design, not a harmless preprocessing detail.
- **Biological validation must remain downstream-facing.** Differential expression, rare-cell detection, cell-state continuity and atlas transfer can disagree; the accessible source does not report a unified metric or numerical benchmark.
- **Interpretability is the proposed next step.** Figure 3 suggests attributing a gene's contribution to cell identity/state and nuisance programs, enabling informed correction. No equations, optimization objective, implementation, or code repository are supplied in the accessible article.

### Reproducibility assessment

`paper source` has no code/data-availability section and the acquisition GitHub search returned zero repository candidates. A direct GitHub API title search for “informed batch correction” also returned zero repositories. The cited tools have their own public implementations, but they are comparison references, not a repository for this review. Full-text methods, benchmark data, parameter settings, and any supplementary material are `MISSING` from the searched Nature HTML scope.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
