---
layout: default
permalink: /paper-atlas/tokenization-deep-learning-genomics-review-3f7bf718/
title: "Tokenization_deep_learning_genomics_review"
nav: false
wide: true
description: "The review calls for context-adaptive token boundaries, tokenization-aware multimodal models, and compression-aware representations for long/repetitive sequences."
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
      <span>Computational and Structural Biotechnology Journal · 2025</span>
    </div>
    <h1>Tokenization_deep_learning_genomics_review</h1>
    <p>Tokenization and deep learning architectures in genomics: A comprehensive review</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.csbj.2025.07.038" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Tokenization_deep_learning_genomics_review">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

The review calls for context-adaptive token boundaries, tokenization-aware multimodal models, and compression-aware representations for long/repetitive sequences.

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Tokenization and deep learning architectures in genomics: A comprehensive review

### Scope and contribution

Testagrose and Boucher review how a genomic sequence becomes model input and how that representation constrains model architecture. The central argument is that tokenization is not a neutral preprocessing detail: it trades biological resolution, vocabulary size, sequence length, and interpretability against the computational properties of CNNs, transformers, and state-space or convolutional alternatives. The review spans early one-hot CNNs through `k`-mer and subword genomic language models, then long-context non-attention models. It is a narrative review, not a benchmark or a new algorithm.

Primary evidence: paper.md lines 9-13 and 27-29; Table 1 (lines 31-66); discussion and future-work sections (lines 170-208).

### Field landscape

1. **Character or one-hot input** retains base-level resolution and is the natural representation for motif-centric CNNs, but leaves a long sequence for the architecture to process.
2. **Fixed biological chunks** include codons and overlapping or non-overlapping `k`-mers. They shorten sequences or expose local context, but impose boundaries and can grow the vocabulary exponentially with `k`.
3. **Corpus-learned subwords** such as BPE, WordPiece, and SentencePiece make a compact variable-length vocabulary, but their boundaries need not correspond to biological motifs.
4. **Architecture-created tokens** arise when convolutions downsample one-hot sequence before transformer blocks, as described for Enformer and Borzoi.
5. **Long-context alternatives** such as HyenaDNA, Mamba, Caduceus, Lyra, and Evo often retain nucleotide tokens and move scalability pressure from token compression into the sequence mixer.

### Major method comparison

| Family | Representative examples in the review | Sequence representation | What it buys | Principal limitation |
|---|---|---|---|---|
| CNN | DeepBind, DeepSEA, Basset, Basenji, BPNet | One-hot | Efficient local motif extraction and parameter sharing | Weak direct access to very long-range dependencies |
| CNN plus recurrence | DanQ, DeepCpG | One-hot | Local filters plus sequential context | Recurrent cost and optimization difficulty |
| CNN plus transformer | Enformer, Borzoi | One-hot then learned/downsampled tokens | Local feature extraction and distal interaction modeling | Complex, memory-intensive long-context training |
| Transformer language model | DNABERT, Nucleotide Transformer, Geneformer, DNABERT-2 | Overlapping/non-overlapping `k`-mers, ranked genes, or BPE/SentencePiece | Self-supervised transfer and flexible global context | Attention cost; dataset hunger; tokenizer choices strongly affect coverage |
| Hierarchical/generative | GenSLM | Non-overlapping codons | Whole viral-genome hierarchy with global diffusion and local transformer context | Codon representation is not appropriate for all genomic regions |
| Non-attention long-context | HyenaDNA, Mamba, Caduceus, Lyra | Usually nucleotide-level | Avoids quadratic attention while retaining full-resolution input | Model-specific trade-offs and less mature evaluation evidence in this review |

Table sources: paper.md lines 36-65, 87-123, and 126-168.

### Key findings

- Fixed `k`-mers present an explicit three-way trade-off: small `k` can miss long motifs, large `k` creates a sparse vocabulary, and unseen variant-containing tokens require decomposition, sub-`k` vocabulary coverage, or `[UNK]` fallback (paper.md lines 142-146).
- The review identifies DNABERT-2's BPE/SentencePiece switch as a move toward data-driven tokenization and reports up to threefold efficiency relative to its predecessor; this is a paper-reported comparison rather than a reproduction in this workspace (lines 146-154).
- For Enformer/Borzoi, convolutions act as representation learning and downsampling before attention, so tokenization can be architectural rather than a fixed external vocabulary (lines 138-139).
- Long-context models do not eliminate the tokenization question. They instead make nucleotide-level processing practical for larger inputs and therefore alter the resolution-versus-cost boundary (lines 160-168).

### Open problems

The review calls for context-adaptive token boundaries, tokenization-aware multimodal models, and compression-aware representations for long/repetitive sequences. It also argues that performance benchmarks alone are inadequate: learned vocabularies should be tested for motif enrichment, biological plausibility, calibration, and generalization (lines 172-196).

### Reproducibility and code status

This is a review article with no paper-owned implementation. The PMC JATS source, all three local visual assets, and the 85-entry source reference list were inspected. Searches of the converted article and the original JATS for GitHub URLs and code/software/data-availability material found no attributable repository. Therefore `has_code=false`; no cited-model repository was cloned or used as if it implemented this review.

### Source limitations

The article is a narrative synthesis and does not supply a uniform task, dataset, split, metric, or executable comparison protocol. Reported context lengths and model descriptions are catalog entries from the review, not independently re-run results. The converted Markdown retains citation keys but omits formatted bibliography text; the OA JATS XML retained under `scratch/oa_source/PMC12356405/main.nxml` was used to verify reference metadata.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
