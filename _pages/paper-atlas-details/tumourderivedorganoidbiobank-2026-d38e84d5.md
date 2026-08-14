---
layout: default
permalink: /paper-atlas/tumourderivedorganoidbiobank-2026-d38e84d5/
title: "TumourDerivedOrganoidBiobank_2026"
nav: false
wide: true
description: "癌症依赖图谱通常依赖二维细胞系，但细胞系可能经过长期体外适应，罕有与患者的临床资料、配对正常样本和原发肿瘤。这样会限制“某个基因型为何对应某个脆弱性”的解释。本文建立的是一个带患者背景的三维肿瘤类器官资源，并在这些模型上做全基因组 CRISPR-Cas9 筛选，而不是提出一个全新的机器学习模型。 研究从五类癌症获得患者肿瘤、正常/血液样本和临床资料，建立 256 个可冻存复苏的类器官。"
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
      <span>Perturbation Resources</span>
      <span>Nature · 2026</span>
    </div>
    <h1>TumourDerivedOrganoidBiobank_2026</h1>
    <p>A tumour-derived organoid biobank maps cancer gene dependencies</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-026-10830-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for TumourDerivedOrganoidBiobank_2026">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/broadinstitute/DepMap-NextGen-Public" target="_blank" rel="noopener noreferrer" aria-label="Open code for TumourDerivedOrganoidBiobank_2026">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 肿瘤类器官生物样本库如何绘制癌症基因依赖图谱

### 要解决的问题

癌症依赖图谱通常依赖二维细胞系，但细胞系可能经过长期体外适应，罕有与患者的临床资料、配对正常样本和原发肿瘤。这样会限制“某个基因型为何对应某个脆弱性”的解释。本文建立的是一个带患者背景的三维肿瘤类器官资源，并在这些模型上做全基因组 CRISPR-Cas9 筛选，而不是提出一个全新的机器学习模型。

### 资源和输入

研究从五类癌症获得患者肿瘤、正常/血液样本和临床资料，建立 256 个可冻存复苏的类器官。每个模型可配合 WGS、RNA-seq 和部分配对肿瘤的 WGS；其中 162 个类器官完成并通过 CRISPR 质量控制（`paper.md:9-12,35-63,128-147`）。

```text
患者肿瘤 + 正常样本 + 临床资料
  -> 类器官建立、扩增、冻融质控和建库
  -> WGS/RNA-seq 与配对肿瘤比较
  -> Cas9 表达、sgRNA 文库转导、三维 CRISPR dropout 筛选
  -> 读数质控、基因 LFC/依赖概率
  -> 核心必需基因、差异依赖、基因型/临床生物标志物关联
  -> 药物、EGF 撤除和治疗前后配对验证
```

### CRISPR 筛选和计算步骤

类器官在 5% BME-2 悬浮培养中筛选，以降低三维培养的大规模操作难度。研究使用 MinLibCas9 或 Yusa v1.1 文库，统一到共享 sgRNA 后进行分析。低质量重复和模型会被排除；读数先由 CRISPRcleanR 校正拷贝数效应，再做跨文库批次校正；BAGEL2 估计基因适应度/依赖，LFC 相对必需与非必需对照缩放（`paper.md:351-369`）。

对每个癌种，分析先去除只在单一样本耗竭或不耗竭的基因、核心必需和对照基因、以及低表达基因。其余基因比较“依赖”和“非依赖”类器官的 LFC 差异，并以 FDR 校正后的 $P<0.05$ 保留差异依赖（`paper.md:397-407`）。随后把依赖效应与突变、拷贝数、结构变异、突变特征、表达、通路分数和临床变量放入含技术/生物协变量的线性回归中，再经似然比检验、多重校正和效应量排序（`paper.md:409-420`）。

### 主要发现

- 配对肿瘤与类器官在突变负荷、结构变异、克隆比例和 SCNA 上总体一致，但低肿瘤纯度会降低观测到的一致性（`paper.md:76-95`）。
- ADaM/CoRe 得到 751 个类器官核心必需基因，97 个不在细胞系核心集合中；这些基因富集于固醇/异戊二烯相关通路（`paper.md:148-156,372-380`）。
- 图谱发现 1,841 个显著的依赖-生物标志物关联，例如 MSI 特征与 WRN 依赖、CCNE1 扩增与 CCNE1 依赖（`paper.md:157-171`）。
- 结直肠类器官中，KRAS G12X 与 KRAS、EGFR、PTPN11 的依赖更强；Q61H 模型对 EGFR 抑制和 EGF 撤除不敏感，说明不能把所有 KRAS 突变视为同一治疗亚群（`paper.md:172-191`）。

### 代码与可复现性

后者确实包含依赖分类、表达/旁系同源基因关联、改变关联和类器官-二维比较的下游代码，但并非论文链接的同一仓库。因此可把代码对应性评为**中等**：理解分析思路有帮助，但不能声称已复现论文完整流程。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## A tumour-derived organoid biobank maps cancer gene dependencies

### Overview

This Nature 2026 study establishes a renewable, clinically linked tumour-organoid atlas and uses genome-wide CRISPR-Cas9 screens to make a patient-derived map of cancer dependencies. It reports 256 organoids across colorectal, oesophageal, ovarian, pancreatic, and gastric cancers, with WGS for all models, matched tumour WGS for 171, and 162 QC-passed CRISPR screens (`paper.md:9-12,35-63,128-147`).

### Why It Matters

Existing dependency maps are dominated by adapted 2D cell lines, have uneven tumour-subtype coverage, and often lack matched normal and clinical data. The study makes 3D models renewable and patient-linked, then uses genomics, transcriptomics, CRISPR effects, and pharmacology to resolve vulnerability context.

### Approach and Results

Organoids were derived centrally, banked only after expansion/freeze-thaw QC, genomically compared with matched tumours, and screened in 5% BME-2 suspension with MinLibCas9 or Yusa v1.1 libraries. CRISPR counts underwent quality control, CRISPRcleanR copy-number correction, cross-library batch correction, BAGEL2 scoring, and LFC scaling (`paper.md:351-380`).

The resource preserved major genomic features while revealing incomplete concordance associated partly with tumour purity. ADaM found 751 core essential genes, including 97 organoid-specific genes. Differential screening and biomarker analysis identified 1,841 significant associations, including expected MSI-WRN and CCNE1-amplification dependencies (`paper.md:148-171,372-420`). The most clinically developed result is allele-dependent EGFR-RAS-MAPK behavior: KRAS G12X organoids retained stronger KRAS/EGFR/PTPN11 dependence than other KRAS-mutant groups, whereas a Q61H model resisted EGFR targeting (`paper.md:172-191`). A paired oesophageal case connected treatment evolution with a changed dependency/drug-sensitivity profile (`paper.md:192-200`).

### Reproducibility

The paper links processed data through Cell Model Passports/DepMap Miner and figure data through Figshare, and points to `Garnett-Lab/SangerOrganoidBiobank` for paper code (`paper.md:431-440`). This workspace instead contains the user-supplied `broadinstitute/DepMap-NextGen-Public` commit `5c6f1e0ab23b132ce1a5c31ef8344cdb80e5afbb`. Its source verifies several related downstream analyses, but because it is not the paper-linked snapshot and no input matrices/supplementary Markdown were acquired, end-to-end reproduction is not verified. Overall code-paper fidelity: **medium**.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
