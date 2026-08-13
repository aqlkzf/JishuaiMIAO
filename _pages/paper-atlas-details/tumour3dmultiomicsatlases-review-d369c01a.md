---
layout: default
permalink: /paper-atlas/tumour3dmultiomicsatlases-review-d369c01a/
title: "Tumour3DMultiOmicsAtlases_Review"
nav: false
wide: true
description: "Title: 3D multi-omics tumour atlases: from technology to biology and clinical translation DOI: 10.1038/s41568-026-00940-0 Journal/year: Nature Reviews Cancer, 2026 Local source: outputpapermd/naturehtml/paper."
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
      <span>Nature Reviews Cancer · 2026</span>
    </div>
    <h1>Tumour3DMultiOmicsAtlases_Review</h1>
    <p>3D multi-omics tumour atlases: from technology to biology and clinical translation</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41568-026-00940-0" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Tumour3DMultiOmicsAtlases_Review">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

Title: 3D multi-omics tumour atlases: from technology to biology and clinical translation DOI: 10.1038/s41568-026-00940-0 Journal/year: Nature Reviews Cancer, 2026 Local source: outputpapermd/naturehtml/paper.

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## 3D multi-omics tumour atlases: review summary

### Paper identity

- Title: 3D multi-omics tumour atlases: from technology to biology and clinical translation
- DOI: 10.1038/s41568-026-00940-0
- Journal/year: Nature Reviews Cancer, 2026
- Local source: `paper source/nature_html/paper.md`
- Analysis mode: review / paper-only; no code repository was found in the Nature acquisition manifest or GitHub sidecar.

### Scope

This Review argues that tumour biology should be studied as a spatially organized, multi-scale ecosystem rather than as disconnected 2D sections. The central object is a 3D tumour atlas that integrates molecular, cellular and morphological information in three dimensions; the paper's glossary defines it as capturing structures such as tumour budding, vessels, tertiary lymphoid structures and neural structures (`paper source/nature_html/paper.md:677-680`). The abstract frames the motivation as understanding heterogeneous cell types and interactions during pre-malignant lesion development, tumour initiation, progression, invasion and metastasis (`paper source/nature_html/paper.md:9-12`).

The review is organized around four layers:

1. Why 3D is needed: 2D histology and limited marker panels miss continuous structures, rare events and multi-omics integration; 3D views can expose volumetric burden, vasculature, neural architecture and immune neighbourhoods (`paper source/nature_html/paper.md:21-27`).
2. How to generate 3D tumour atlases: non-invasive imaging, non-destructive volumetric imaging and serial sectioning-based approaches (`paper source/nature_html/paper.md:42-63`).
3. Which spatial omics modalities matter: RNA, protein, genome/epigenome, metabolome and intracellular imaging (`paper source/nature_html/paper.md:118-190`).
4. How computation converts data into atlases and clinical use: preprocessing, registration, interpolation, foundation models, 3D pathology and data standards (`paper source/nature_html/paper.md:199-278`).

### Main thesis

The paper's practical claim is not that one technology is sufficient. It argues for a staged atlas strategy: use scalable clinical imaging and retrospective cohorts where possible, use high-resolution spatial multi-omics in selected cohorts to discover biomarkers and mechanisms, then validate and translate those signals in larger clinical datasets (`paper source/nature_html/paper.md:45-57`). The "holy grail" is a genome-scale, subcellular-resolution, multi-modal whole-tumour atlas that can support virtual tumour models and perturbation prediction (`paper source/nature_html/paper.md:36-39`).

### Taxonomy of methods

| Layer | Representative approaches | Strength | Main constraint | Evidence |
|---|---|---|---|---|
| Non-invasive clinical imaging | CT, MRI, ultrasound, PET, OCT, MSOT | Living-patient, longitudinal and retrospective cohorts | Organ-level resolution, not cellular activity | `paper source/nature_html/paper.md:48-57`; Fig. 1 |
| Non-destructive volumetric imaging | LSFM, confocal/multiphoton microscopy, microCT | Preserves 3D continuity and intact tissue context | Volume-resolution trade-off, clearing/staining complexity | `paper source/nature_html/paper.md:63-100`; Fig. 1 |
| Serial sectioning | Serial H&E, serial spatial transcriptomics/proteomics, electron microscopy | Multi-modal profiling using established 2D assays | z-axis resolution, tissue artefacts, registration burden | `paper source/nature_html/paper.md:103-115`; Fig. 2 |
| Spatial RNA biology | LCM/light-guided selection, Visium/Slide-seq/Stereo-seq/DBiT, MERFISH/seqFISH/ISS | Gene and RNA-species localization | Coverage, sensitivity, cost and 2D bias | `paper source/nature_html/paper.md:127-148`; Fig. 2 |
| Spatial proteomics | CycIF, CODEX, IMC, MIBI, spatial-CITE-seq, DBiT-seq | Cell-state and TME phenotyping beyond RNA | Panel size, antibody validation, imaging/segmentation burden | `paper source/nature_html/paper.md:151-154`; Fig. 2 |
| Spatial genomics/epigenomics | Slide-DNA-seq, Droplet Hi-C, spatial-ATAC, spatial-CUT&Tag, chromatin tracing | Clonal and regulatory mechanisms | Fewer mature platforms than transcriptomics | `paper source/nature_html/paper.md:157-163`; Fig. 2 |
| Spatial metabolomics and intracellular imaging | MALDI-MSI, DESI-MSI, nano-DESI, Raman/SRS, super-resolution microscopy | Functional metabolism and organelle-scale readouts | Spatial resolution, molecular coverage, sample prep | `paper source/nature_html/paper.md:166-184`; Fig. 2 |
| Computational construction | CODA, PIVOT, STAligner, SLAT, PASTE, Spateo, moscot, InterpolAI | Registers, interpolates and integrates serial sections | Missing sections, tissue deformation, scale | `paper source/nature_html/paper.md:222-231`; Fig. 3 |
| AI and foundation models | TriPath, LUNA, ST-Align, OmiCLIP/Loki, iSTAR, VORTEX | Clinical prediction and modality extrapolation | Training data scale, generalization, compute cost | `paper source/nature_html/paper.md:234-246`; Fig. 3 and Fig. 4 |

### Key findings and field-level takeaways

- 3D profiling can change biological interpretation. The review highlights examples where 2D Gleason pattern interpretation, tumour buds, tertiary lymphoid structures and pancreatic precursor classification are revised when full 3D continuity is reconstructed (`paper source/nature_html/paper.md:100-115`).
- Spatial multi-omics turns histology from a morphology-only readout into a layered molecular atlas. The authors explicitly connect genome/epigenome, RNA, protein and metabolite layers to the central dogma and tumour ecosystem biology (`paper source/nature_html/paper.md:121-190`).
- Computational reconstruction is a core method, not a downstream convenience. Registration, optimal transport, interpolation and foundation-model extrapolation are required because current 3D spatial multi-omics often still depends on serial 2D measurements (`paper source/nature_html/paper.md:202-231`).
- Translation has two tracks: 3D pathology/digital pathology for clinical diagnosis or prognosis, and holistic molecular atlases for discovery, biomarker validation and personalized oncology (`paper source/nature_html/paper.md:264-278`; Fig. 4).

### Open problems

- Direct volumetric 3D spatial multi-omics on a single specimen remains an aspiration; current methods still often reconstruct 3D from aligned serial 2D measurements (`paper source/nature_html/paper.md:225-228`, `paper source/nature_html/paper.md:275-278`).
- Clinical translation needs pathologist oversight, expert annotations, paired patient outcomes, and large cohorts before automated 3D pathology can be trusted (`paper source/nature_html/paper.md:264-272`).
- Atlas-scale storage and sharing remain infrastructure bottlenecks for multi-terabyte imaging and spatial data; the review points to consortium platforms such as HuBMAP, SenNet and HTAN as current scaffolding (`paper source/nature_html/paper.md:255-258`).
- The converted Markdown preserves captions for Tables 1-3, but structured table bodies were not recovered in `paper.md` (`paper source/nature_html/paper.md:66-66`, `paper source/nature_html/paper.md:124-124`, `paper source/nature_html/paper.md:205-205`). Interpretive tables in this workspace are therefore synthesized from main text and figure captions, not copied from source table bodies.

### Reproducibility and code status

This is a review article, not a primary software or benchmark paper. No repository was found by the acquisition route: `acquisition_manifest.json` has an empty `repo_url`, empty `github_repo_urls`, and no `code_availability_html`; `github_links.json` contains no candidates. No `doc_code.md` was generated.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
