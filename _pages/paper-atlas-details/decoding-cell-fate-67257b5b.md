---
layout: default
permalink: /paper-atlas/decoding-cell-fate-67257b5b/
title: "Decoding_Cell_Fate"
nav: false
wide: true
description: "The article illustrates disease-response inference, cancer/regenerative cell-state manipulation, and non-model-organism studies (lines 165-185)."
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Bioinformatics · 2025</span>
    </div>
    <h1>Decoding_Cell_Fate</h1>
    <p>Decoding cell fate: integrated experimental and computational analysis at the single-cell level</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1093/bioinformatics/btaf603" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Decoding_Cell_Fate">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

The article illustrates disease-response inference, cancer/regenerative cell-state manipulation, and non-model-organism studies (lines 165-185).

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Decoding cell fate: integrated experimental and computational analysis at the single-cell level

### Review Scope

This Bioinformatics review surveys how single-cell experiments and computational models can be combined to study cell fate. Its central unit of analysis is a cell state: a molecular configuration observed at one time, as distinct from a fate, the eventual functional outcome. The article organizes the field from theory to measurement, inference, intervention, and application: Waddington-like landscapes and gene regulatory networks (GRNs); multimodal profiling, lineage tracing, and perturbation; state maps, trajectory inference, lineage analysis, and GRN reconstruction; then perturbation models and single-cell/spatial foundation models. The source explicitly identifies itself as a review and states that it generates no new software (paper lines 17-27).

The paper's practical thesis is that cell fate cannot be established from a single transcriptomic snapshot alone. A useful study must match its biological question to complementary evidence: multi-omics to describe state, lineage tracing to establish ancestry, perturbation to test causality, and computation to turn heterogeneous measurements into state maps and testable hypotheses (lines 65-99, 101-133, 204-212).

### Field Landscape

The review uses two compatible conceptual views. In the epigenetic-landscape view, stable fates are attractors and transitions are movements between attractors or changes to the landscape itself. In the GRN view, interacting regulators generate the dynamics that sustain or change those attractors (lines 39-64). The two views supply a vocabulary for experimental and computational work, but they do not by themselves identify a causal regulator.

The experimental side has three complementary evidence types:

| Evidence type | What it observes | Main strength | Important limitation |
|---|---|---|---|
| Single-cell and spatial multi-omics | RNA, chromatin, protein, metabolite, and/or position | Rich characterization of present states and context | Mostly destructive snapshots; unpaired modalities and batch effects complicate integration |
| Lineage tracing | Clone identity or phylogenetic history from natural or engineered barcodes | Direct ancestry and fate-distribution evidence | Barcode dropout/homoplasy and destructive sequencing can limit resolution |
| Genetic, epigenetic, or chemical perturbation | Response after an intervention | Stronger leverage for causality and dose/time studies | Starting-state uncertainty, throughput, target selection, and viability remain limiting |

This is not a replacement relationship. The review argues that the strongest programs combine these data streams: for example, a lineage record can disambiguate a transcriptomic trajectory, while an intervention can test a putative GRN regulator (lines 78-98, 118-133).

### Method Taxonomy

The computational taxonomy is organized by the question after data collection.

| Question | Representative paradigm | Inputs | Output | Key assumption or trade-off |
|---|---|---|---|---|
| What states exist? | Feature selection, reduction, clustering, marker or reference annotation | scRNA-seq, optionally multi-omics/spatial data | State map / labeled clusters | Cluster boundaries and annotation depend on parameters and reference knowledge |
| How do states change? | Pseudotime, population balance, optimal transport, RNA velocity | Snapshot or time-series transcriptomes; unspliced RNA for velocity | Ordering, transition coupling, or local direction | Expression proximity and inferred branches need not equal real time or cell division |
| What is a cell's ancestry and fate bias? | Static/mutable barcode processing, tree reconstruction, clone distributions | Barcode and optional transcriptome data | Lineage tree, clones, fate bias/coupling | Same lineage does not require similar expression; inferred trees are uncertain |
| What drives a transition? | Small-circuit dynamical models; large-scale GRN inference | TF knowledge, RNA, TF binding/accessibility, perturbation data | Regulator network, modules, candidate master regulators | Co-expression/accessibility are not direct proof of regulation |
| What happens after intervention? | Linear/ML models, autoencoders, VAEs, CPA, GEARS | Baseline state, perturbation identity, chemical descriptors, readouts | Predicted post-perturbation profile or ranked intervention | Out-of-distribution generalization and causal validity remain difficult |
| Can a pretrained representation help? | Single-cell/spatial foundation models | Large compendia, then task-specific data | Embeddings and fine-tuned/zero-shot task predictions | Attention or scale does not make a model causal or consistently better than baselines |

The paper gives a simple dynamical abstraction for a GRN: a cell state vector $S(t)=(x_1(t),...,x_n(t))$ evolves as $S(t+1)=G(x_1(t),...,x_n(t))$ (lines 52-64). Small networks can be modeled by Boolean rules or nonlinear ODEs; at low copy number, master equations can represent stochasticity. This equation is a conceptual framework in the review, not an executable method released with the article.

### Key Findings

1. State, fate, and trajectory are related but different targets. Clustering and annotation construct a state map; trajectory tools infer a relation among observed states; lineage and perturbation data are needed to increase confidence in history and causality (lines 101-133).
2. Static multi-omics is broad but not longitudinal. Lineage tracing supplies historical information, whereas paired perturbation-and-readout experiments expose responses; spatial data restores the context lost by dissociation (lines 69-98).
3. Trajectory inference has irreducible interpretive risks. Pseudotime assumes adequate sampling of transitional states; transcriptomic similarity can be confounded by cycle, stress, and spatial effects; branches need not be actual divisions or a tree (lines 112-117).
4. GRN analysis should combine evidence. RNA co-expression alone cannot establish direction; binding/accessibility priors, perturbation data, and careful treatment of post-transcriptional regulation improve but do not eliminate ambiguity (lines 126-133).
5. AI perturbation models are promising hypothesis generators, not yet a replacement for experiments. The review notes benchmarks where deep approaches do not exceed linear baselines and zero-shot predictions can approach random guessing (lines 138-153).
6. Foundation models add broad representations and can support downstream perturbation, GRN, and trajectory tasks, but the paper reports challenges in data, tokenization/nonsequential data structure, interpretability, cost, and performance consistency (lines 153-164).

### Method-Selection Guidance

- Use a state map for descriptive cell identity questions, and record feature-selection, clustering, and annotation choices.
- Use time series, RNA labeling/velocity, or optimal transport when the question is directional progression; report assumptions and validate against independent time or lineage evidence.
- Use engineered or natural lineage records when ancestry, clone expansion, or fate bias is primary; evaluate barcode quality and tree uncertainty.
- Use perturbation when asking whether a candidate regulator or pathway causes a transition. Measure the initial state, dose, and exposure time where possible.
- Use multimodal and spatial assays when regulatory, tissue-position, or microenvironmental context is biologically decisive.
- Treat AI outputs as prioritization tools. Benchmark against simple baselines and verify proposed perturbations experimentally before interpreting them as causal control programs.

### Applications And Open Problems

The article illustrates disease-response inference, cancer/regenerative cell-state manipulation, and non-model-organism studies (lines 165-185). These examples show that the common workflow is portable, but not that one model transfers without adaptation. In particular, the paper identifies intrinsic/extrinsic noise, technical variability, scale, unpaired multimodal data, batch correction, and biological-signal preservation as persistent constraints (lines 186-203).

The proposed endpoint is an iterative experimental-computational loop: analysis selects hypotheses and interventions, experiments produce new measurements, and models are revised. The envisioned AI virtual cell is explicitly aspirational; its value depends on grounded perturbation data and rigorous validation rather than representation learning alone (lines 204-212).

### Reproducibility Status

This is a paper-only review. The PMC JATS source is retained locally with five main figures. The availability statement says, "This work generates no new software" (line 25); searches of the availability statement, the complete converted article, and acquisition sidecars found no paper-linked GitHub implementation. Therefore there is no `code source`, no CodeGraph index, and no `doc_code.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
