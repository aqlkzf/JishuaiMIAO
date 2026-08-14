---
layout: default
permalink: /paper-atlas/largecellatlases-review-65f4e196/
title: "LargeCellAtlases_Review"
nav: false
wide: true
description: "Insights, opportunities, and challenges provided by large cell atlases (Hemberg et al., Genome Biology, 2025) is a field-level review, not a new algorithm, atlas release, benchmark, or software paper."
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
      <span>Atlases &amp; Resources</span>
      <span>Genome Biology · 2025</span>
    </div>
    <h1>LargeCellAtlases_Review</h1>
    <p>Insights, opportunities, and challenges provided by large cell atlases</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-025-03771-8" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for LargeCellAtlases_Review">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

Insights, opportunities, and challenges provided by large cell atlases (Hemberg et al., Genome Biology, 2025) is a field-level review, not a new algorithm, atlas release, benchmark, or software paper.

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Review Scope

**Insights, opportunities, and challenges provided by large cell atlases** (Hemberg et al., *Genome Biology*, 2025) is a field-level review, not a new algorithm, atlas release, benchmark, or software paper. It defines a cell atlas as a large, curated, portal-accessible collection of datasets with a coherent ingestion and processing pipeline (`paper.md:50-54`). The article's contribution is a practical roadmap: what large atlases already enable, which infrastructure and statistical choices determine whether they are reusable, and which computational problems remain before atlas-scale data can support reliable biological and biomedical discovery.

The review is paper-only. The article says that no datasets were generated or analyzed (`paper.md:220-222`), and neither the PMC/JATS source nor the publisher HTML contains a paper-owned GitHub/software availability section. A GitHub repository search by title and DOI returned zero repository matches; no implementation was cloned because there is no method implementation to reproduce. The repositories named in the paper are external atlases, databases, and cited tools, not a companion implementation.

### Central Thesis

Large cell atlases turn many individually generated single-cell datasets into a reusable, queryable research substrate. Their value is not proportional to cell count alone: it depends on FAIR access, raw and processed data levels, reproducible preprocessing, complete metadata, flexible ontologies, query-aware integration, and interfaces that let users move from a portal question to downloadable or cross-cohort analysis (`paper.md:117-135`). The review therefore treats atlas construction and atlas use as one coupled system.

The article's recurring logic is:

```text
many labs and assays
  -> standardized ingestion, QC, metadata, and representation
  -> atlas portal and APIs
  -> query-specific integration and analysis
  -> biological hypotheses, method development, and biomedical decisions
  -> new data and new modalities feed the atlas again
```

Figure 1 depicts this loop directly: data generation feeds atlas generation; atlas queries feed insights; insights motivate further data generation (`paper.md:110-115`).

### Atlas Landscape

Table 1 is a snapshot rather than a benchmark. It lists selected resources by approximate transcriptomics cell count, donors, launch/publication year, organization, species, and portal URL (`paper.md:56-107`). The largest entries include Single Cell Atlas (approximately 200 M cells), CZ CELLxGENE Discover (112.8 M), Human Cell Atlas (65.4 M), and Broad Single Cell Portal (57.6 M); other resources cover multiple species, cancer, immunity, multimodal assays, or spatially relevant collections (`paper.md:59-105`). The table demonstrates heterogeneity of scale and scope rather than declaring a single canonical atlas.

| Atlas/resource class | Examples named in the review | What the class contributes | Main caveat |
|---|---|---|---|
| Broad, cross-tissue cell portals | CZ CELLxGENE Discover, Human Cell Atlas, Broad Single Cell Portal, Single Cell Expression Atlas | Large-scale search, standardized processing, cross-study reuse (`paper.md:48,59-81`) | Metadata, annotation, API, and compute requirements grow with every cohort and modality (`paper.md:125-131`) |
| Molecular and spatial programs | HuBMAP, Allen Brain Cell Atlas, Single Cell Atlas | Organ-, tissue-, spatial-, and multimodal context (`paper.md:74-92`) | Common coordinates, cross-sample visualization, and modality standards remain difficult (`paper.md:177-181`) |
| Disease/context atlases | TISCH2, Curated Cancer Cell Atlas, PlaqView, AIDA | Disease states, treatment context, immune diversity, and compositional comparisons (`paper.md:84-105,151-153`) | Disease cells may not map to "normal" labels; donor and condition confounding can be mistaken for biology (`paper.md:133-135,151-153`) |
| Species/development/ecology resources | HCA developmental work, zebrafish and mammalian atlases, SPEED, plant atlases, Malaria Cell Atlas | Development, comparative genomics, evolution, and organismal diversity (`paper.md:191-193`) | Orthology, nomenclature, and modality coverage differ across species (`paper.md:133,177-179`) |

### Core Challenges And Opportunities

#### 2. Access, interoperability, and APIs

Portals lower the cost of finding data, but large-scale reuse still demands programming skills, computational resources, standard formats, and APIs that work across R and Python (`paper.md:125-127`). The opportunity is to make atlas access queryable and composable rather than a sequence of browser downloads. The unresolved issue is an indexing layer that can answer cross-cohort queries by tissue, donor, condition, technology, annotation, and modality (`paper.md:127-131`).

#### 3. Metadata and ontologies

Metadata is the bridge from a static archive to a hypothesis-generating resource. The review separates sample metadata (donor, collection, storage, processing), gene metadata, and cell metadata/annotations (`paper.md:129-131`). Ontologies enable structured operations and ML/AI, but cell labels are not universally settled and must remain flexible as new states and contexts are discovered (`paper.md:131-133`). Disease and cross-species use cases add label mismatch and orthology problems (`paper.md:133-135`).

#### 4. Atlas-scale representation and subsampling

The review reports that atlas data already exceed 1 TB in standard structures, making out-of-core processing, high-performance computing, disk-backed/pyramidal formats, and memory-efficient structures important (`paper.md:141-143`). Subsampling can reduce compute and representation bias but may erase rare populations or subtle effects supported by large sample sizes (`paper.md:143-145`). Biosketches, metacells, latent representations, Zarr, Parquet, and TileDB are presented as complementary strategies, each trading resolution, noise, interpretability, or compute (`paper.md:143-145`).

#### 5. Query-specific integration and meta-analysis

Integration is not a one-time preprocessing step. A useful method must let users decide which technical or biological variation to remove, scale to thousands of donor/confounder levels, behave consistently across queries, run quickly enough for interactive use, and reveal distortion or signal degradation (`paper.md:147-149`). Existing benchmarks show progress, but performance degrades in cross-species, imbalanced, and very large settings, and numeric metrics alone do not establish biological validity (`paper.md:149`).

#### 6. Context-aware inference

For disease, age, sex/gender, ancestry, treatment, or functional decline, the unit of replication is the independent biological sample, not an individual cell (`paper.md:151-153`). The review recommends enough donors across conditions and methods such as cell-type/state pseudobulking to avoid falsely treating cells as independent replicates (`paper.md:153`). This is a design constraint on atlas content, not a downstream statistical patch.

#### 7. Benchmarking and methods at tens of millions of cells

Most analysis tools were designed for much smaller datasets. The review calls for efficient approximations, mini-batch algorithms, scalable data structures, and benchmark collections that can serve as curated "gold standards" (`paper.md:155-161`). It also emphasizes that real-data curation can entrench the assumptions of the curation method, while simulations rarely capture all real complexity (`paper.md:155-157`).

#### 8. AI and foundation models

Cell atlases provide the training substrate for Geneformer, scGPT, scFoundation, scBERT, CellFM, UCE, and atlas approximations. The expected uses are annotation, latent-space projection, missing-modality inference, and perturbation-response simulation (`paper.md:161-163`). The review's caution is as important as its opportunity: memory and infrastructure costs, limited interpretability, and insufficient stress testing on noisy, rare, and disease-specific data limit trustworthy deployment (`paper.md:163`).

#### 9. Biomedical and fundamental biology applications

Atlas-scale molecular profiles can connect GWAS loci to cell types/states and context-specific molecular QTLs, support target discovery and drug-response prediction, and expose cellular states along disease trajectories (`paper.md:165-173`). Interfaces such as CELLxGENE, iSEE, Vitessce, and the Broad/Expression Atlas browsers are treated as analysis surfaces, not merely visualization layers (`paper.md:171-173`). Beyond medicine, developmental, comparative, evolutionary, plant, and parasite atlases extend the same infrastructure to fundamental biology (`paper.md:191-193`).

#### 10. Beyond dissociated scRNA-seq

The next atlas generation must incorporate TCR/BCR sequencing, ATAC-seq, long-read sequencing, methylation, CUT&Tag, proteomics, metabolomics, and spatial transcriptomics/proteomics (`paper.md:175-181,191`). This creates joint requirements for modality-specific preprocessing, ontologies, missing-view models, noise-aware integration, and visualization that toggles between molecular and physical coordinates (`paper.md:177-181`).

#### 11. Outreach and public value

The authors argue that publicly funded atlases should serve clinicians, industry, patients, students, teachers, and the general public, not only computational biologists (`paper.md:183-185`). Visual, health-grounded explanations and collaboration with science communicators are presented as infrastructure for impact, not a cosmetic add-on.

### Major Method/Tool Comparison

The paper is not a head-to-head methods benchmark. This comparison summarizes the method families and interfaces it positions within the atlas ecosystem; "trade-off" is a synthesis of the article's stated constraints, not a new experiment.

| Family | Representative methods/tools in the paper | Input/role | Strength at atlas scale | Failure mode or unresolved assumption |
|---|---|---|---|---|
| Explicit sparse-count models | Statistical models that retain sampling/noise structure (`paper.md:121-125,143`) | Raw or processed count matrices | Avoid unnecessary distortion of biological zeros | Downstream tools may not accept sparse data; model assumptions can be wrong |
| Imputation and denoising | Model-based, smoothing, reconstruction, external-reference strategies (`paper.md:143-145`) | Sparse single-cell measurements | Makes some analyses computationally convenient | Can amplify internal structure, create false positives, and obscure uncertainty |
| Metacells and biosketches | Structure-preserving summaries (`paper.md:143-145`) | Very large expression collections | Lower memory/noise and improve tractability | Sacrifice single-cell resolution and can hide rare/subtle states |
| Batch integration/harmonization | Harmony and contemporary integration methods; independent benchmarks (`paper.md:147-149`) | Multiple datasets with sample/donor covariates | Shared representations enable joint clustering and annotation | Query-specific biology may be over-corrected; scale, imbalance, species, and distortion remain |
| Reference mapping/annotation | Atlas-based annotation tools (`paper.md:131-135,151-153`) | New cells plus an annotated reference | Reduces manual labeling and supports reuse | Ontologies evolve; disease/transitional states may not have a valid reference label |
| Differential abundance/expression | Pseudobulk and cell-level comparative frameworks (`paper.md:151-153`) | Cell-by-gene data with independent samples | Can test context-dependent composition and state changes | Pseudoreplication, donor imbalance, and unmodeled confounders produce false positives |
| Spatial and multimodal integration | Shared latent spaces, graph-based integration, coordinate alignment (`paper.md:177-181`) | Multiple modalities, locations, or samples | Retains tissue context and links molecular/cellular scales | Missing modalities, differing noise, coordinate alignment, and visualization complexity |
| Foundation models | Geneformer, scGPT, scFoundation, scBERT, CellFM, UCE (`paper.md:161-163`) | Atlas-scale expression and multimodal corpora | Reusable representations and transfer to annotation/simulation | High compute, limited explainability, and weak stress tests on rare/disease data |
| Benchmarking/simulation | Simulators, curated real "gold standards," community metrics (`paper.md:155-157`) | Synthetic and reference datasets | Makes method choice and scaling claims testable | Synthetic realism, curation bias, and metric incompleteness |

### Bottom-Line Findings

1. **The atlas is a socio-technical system.** Data standards, metadata, APIs, compute, methods, and user interfaces jointly determine scientific value (`paper.md:117-135,171-173`).
2. **The query is part of the model.** Integration and correction should be selected around the biological comparison, with explicit visibility into what variation was removed (`paper.md:147-149`).
3. **Biological replication must be designed into the resource.** Millions of cells cannot substitute for independent donors and conditions (`paper.md:151-153`).
4. **Compression is a scientific decision.** Subsampling, metacells, latent representations, and lossy approximations improve scale but can remove rare or subtle signals (`paper.md:141-145,155-161`).
5. **Modalities and spatial context change the problem definition.** They require new standards, ontologies, missing-view models, and coordinate-aware interfaces (`paper.md:175-181`).
6. **AI expands the opportunity and the verification burden.** Atlas-trained models need interpretable, resource-aware, disease- and rarity-aware evaluation (`paper.md:161-163`).
7. **The paper is an agenda, not a reproducible method.** It presents no new dataset, equation, benchmark score, or software release; reproducibility here means preserving the taxonomy, evidence boundaries, and figure-grounded roadmap.

### Open Problems And Evidence Limits

- No formal equations, optimization objective, algorithm pseudocode, new data analysis, or numerical benchmark is present in the article (`paper.md:1-234`).
- The table's cell counts and donor counts are explicitly a snapshot at writing, so they should not be treated as current atlas inventories (`paper.md:56-107`).
- The review proposes needs for interactive integration, metadata standards, benchmarking, and foundation-model validation but does not specify a single implementation or acceptance test (`paper.md:125-163`).
- No paper-owned GitHub repository was found in the paper, publisher HTML, or title/DOI repository search; cited databases/tools should not be conflated with a companion implementation.
- No supplementary research dataset or analysis file is present; the paper states that no datasets were generated or analyzed (`paper.md:220-222`).

### Reproducibility Status

This workspace contains the PMC JATS-derived paper, two local main-figure images, and all required review documents. `HAS_CODE=false`, `code source=(none)`, `SUPP_MD=(none)`, and `ready_to_publish=true` is justified by the review contract: the missing code is documented as not applicable, not hidden. The primary evidence boundary remains `paper source/PMC12536537/paper.md` and the two inspected images.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
