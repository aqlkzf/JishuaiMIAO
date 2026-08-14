---
layout: default
permalink: /paper-atlas/survey-foundation-language-models-singlecell-a54a0591/
title: "Survey_Foundation_Language_Models_SingleCell"
nav: false
wide: true
description: "The survey treats a cell as an expression-derived language object, then maps the field into two branches. A single-cell pre-trained language model (PLM) is trained from scratch on cell corpora; a single-cell LLM adapts an existing general L…"
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
      <span>Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers) · 2025</span>
    </div>
    <h1>Survey_Foundation_Language_Models_SingleCell</h1>
    <p>A Survey on Foundation Language Models for Single-cell Biology</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.18653/v1/2025.acl-long.26" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Survey_Foundation_Language_Models_SingleCell">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

The survey treats a cell as an expression-derived language object, then maps the field into two branches. A single-cell pre-trained language model (PLM) is trained from scratch on cell corpora; a single-cell LLM adapts an existing general L…

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## A Survey on Foundation Language Models for Single-cell Biology - Summary

### Review Scope

| Field | Value |
|---|---|
| Venue | ACL 2025 Long Papers, pp. 528-549 |
| DOI | `10.18653/v1/2025.acl-long.26` |
| Paper type | Narrative survey / review |
| Scope | Foundation language models (FLMs) for single-cell biology through the lenses of single-cell PLMs and LLMs |
| Main organizing dimensions | Tokenization, pre-training or tuning, and downstream tasks |
| Reproducibility of this paper | N/A: the article reviews prior work and supplies no original executable experiment |

The survey treats a cell as an expression-derived language object, then maps the field into two branches. A single-cell pre-trained language model (PLM) is trained from scratch on cell corpora; a single-cell LLM adapts an existing general LLM by converting cells to text or using text-derived gene embeddings. This is a field map, not a controlled benchmark or a new model. Source: `paper source/2025.acl-long.26/hybrid_auto/2025.acl-long.26.md:15-23`.

### Field Landscape

The paper's central abstraction is a cell-by-gene matrix transformed into a tokenized cell representation. PLMs commonly treat genes or expression states as tokens and learn cell representations by masked-language modeling (MLM), next-token prediction, or multi-task objectives. LLM approaches avoid large de novo cell-corpus pre-training: they convert a ranked gene list into a sentence, combine text-derived gene embeddings with expression weights, or use an LLM agent. The review's Figure 1 is useful because it separates the representation route from the training route rather than treating all "single-cell foundation models" as one family.

| Family | Input bridge | Main adaptation/training choices | Representative models in the survey |
|---|---|---|---|
| Single-cell PLM | Discrete gene/value tokens or continuous gene/cell embeddings | MLM, next-token prediction, multi-task pre-training | scBERT, UCE, GeneFormer, CellPLM, scFoundation, Nicheformer, tGPT, scGPT, CellLM, LangCell, scCello, scPRINT, scMulan, GeneCompass, CellFM |
| Single-cell LLM | Cell-to-sentence or text-level gene embeddings | Instruction-based tuning, embedding-based tuning, tuning-free agent | Cell2Sentence, CHATCELL, scInterpreter, GenePT, scELMo, CELLama, scChat |

The taxonomy and its named members are drawn from Figure 1 and Tables 1-2 (`paper.md:30-55`, `paper.md:115-131`). It is a snapshot of the literature covered by the survey, rather than an assertion that these models have equivalent maturity or performance.

### Key Findings

- **Tokenization is the primary biological modeling decision.** Binning and rank encoding make input discrete but discard or reshape expression magnitude; continuous embeddings retain more numerical detail and can add metadata or protein-model priors (`paper.md:107-119`).
- **MLM predominates among PLMs.** The paper reports random gene masking at roughly 15-30% for several systems, whereas only tGPT and scGPT are listed under next-token prediction (`paper.md:121-127`).
- **LLM adaptation has a narrower set of input bridges.** Cell-to-sentence uses top expressed gene names; text-level gene embeddings query or encode gene-function text and combine those embeddings using each cell's expression values (`paper.md:139-155`).
- **The application space is broad, but evidence is heterogeneous.** Tasks span annotation, novelty discovery, batch correction, clustering, integration, generation, network analysis, perturbation, prediction, drug response, and spatial analysis (`paper.md:157-181`, `paper.md:531-546`).
- **The survey's own diagnosis is cautious.** Sparse unordered measurements, batch effect, lack of non-RNA resources, no shared cell tokenizer, uncertain scaling behavior, and non-standard evaluation limit claims of universal biological representations (`paper.md:183-221`).

### Major-Method Comparison

| Group | Representation choice | Objective / tuning | What it makes easy | Main trade-off |
|---|---|---|---|---|
| Binned PLMs | Discrete expression bins | MLM or multi-task learning | BERT-style conditional representation learning | Quantization loses fine expression differences |
| Rank-token PLMs | Order genes by expression, retain a fixed top length | MLM, autoregression, or multi-task learning | Normalizes some scale variation and yields a sequence | Gene order is constructed, not biological |
| Continuous/prior-informed PLMs | Project values, use protein embeddings, metadata, or cell tokens | Mostly MLM or multi-task learning | Can preserve numeric signal and add biological context | Depends on normalization and may import prior/metadata bias |
| Cell-to-sentence LLMs | Top-ranked gene names rendered as text | Instruction or embedding-based tuning | Reuses language-model interfaces and natural-language tasks | The cell description omits much of the expression profile |
| Text-embedding LLMs | Gene-function text embeddings weighted/ranked by expression | Embedding-based supervised tuning | Leverages semantic knowledge about genes | Biological text priors and expression weights are indirect proxies |
| Agent LLMs | Raw data plus tools/prompts | No model tuning in the survey's classification | Flexible analysis interaction | Correctness depends on generated code and user validation |

### Open Problems

1. A cell is sparse and unordered: the paper notes that fewer than 10% of genes may be measured in a cell, while standard Transformers can absorb artificial positional signals (`paper.md:187-199`).
2. Cross-study pre-training must control sequencing, platform, and laboratory batch effects rather than merely aggregate cells (`paper.md:195-197`).
3. A unified tokenizer remains absent; the paper cites approximately 70,000 genes for the largest vocabulary and flags incorporation of newly discovered genes as unresolved (`paper.md:203-211`).
4. Scaling is not established: the survey states that listed PLMs remain below one billion parameters and LLM routes still need task-specific tuning (`paper.md:205-211`).
5. Cross-model comparison is not fair without open, shared datasets, metrics, and leakage-aware benchmarks (`paper.md:213-221`).

### Reproducibility And Code

No paper-specific model implementation was found. The ACL landing page provides the article/PDF and no code link; a full-PDF text search found no `github`, `code availability`, `software`, or implementation statement. GitHub repository search found `zfkarl/Awesome-Single-cell-Foundation-Models`, whose README identifies it as a paper list and whose `master` tree contains only `README.md` and `figs/scFLM.png`; it is a companion reading list, not executable survey code. The review workspace therefore remains `has_code=false`, as required for a review-paper route.

The paper's claims about individual PLMs/LLMs should be verified against their original publications and independent benchmarks before selecting a system. This review compares design categories and reported task coverage, but does not execute a common benchmark.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
