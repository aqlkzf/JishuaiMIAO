---
layout: default
permalink: /paper-atlas/membranolyticpeptide-0931a08b/
title: "MembranolyticPeptide"
nav: false
wide: true
description: "作者不是单纯追求“把肿瘤细胞杀死”，而是用酸响应膜裂解肽 aMPC16-CA50 把死亡过程编排成“先溶酶体膜破裂、后质膜破裂”，让肿瘤抗原和危险信号在更有利的时空顺序中释放，从而增强树突状细胞呈递、T 细胞激活和 anti-PD-L1 疗效。"
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
      <span>Technology Platforms</span>
      <span>Nature · 2026</span>
    </div>
    <h1>MembranolyticPeptide</h1>
    <p>Membranolytic peptide programs immunogenic cell death for cancer therapy</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 中文方法解释：用膜裂解肽编程免疫原性细胞死亡

### 一句话

作者不是单纯追求“把肿瘤细胞杀死”，而是用酸响应膜裂解肽 aMP~C16~-CA~50~ 把死亡过程编排成“先溶酶体膜破裂、后质膜破裂”，让肿瘤抗原和危险信号在更有利的时空顺序中释放，从而增强树突状细胞呈递、T 细胞激活和 anti-PD-L1 疗效。

### 输入、过程、输出

```text
酸响应肽 + 肿瘤细胞
        ↓ pH 6.8 条件下摄取
溶酶体酸化/肽激活
        ↓
LMR（溶酶体膜破裂）
        ↓ 时间延迟
PMR（质膜破裂）→ LDH/HMGB1/抗原释放
        ↓
树突状细胞交叉呈递 → OT-I/T 细胞反应
        ↓
小鼠肿瘤模型中增强 anti-PD-L1
```

### 怎么验证

细胞活性用 MTT/CCK-8，摄取用 FITC 流式；Gal3-GFP、CTSB-mCherry、PI/DRAQ7 和活细胞共聚焦记录 LMR/PMR 顺序。Western blot 检测 RIPK1/RIPK3/MLKL、GSDME/GSDMD、PARP1/caspase-3、NINJ1；LDH、HMGB1 和银染检测胞内物释放。Mlkl、Gsdme、Ninj1 敲除用于区分“细胞毒性”与“免疫原性”所需机制。RNA-seq 采用 SOAPnuke、Bowtie2、RSEM、DESeq2、DAVID 和 GSEA；scRNA-seq 分析 CD45+ 肿瘤免疫细胞。

### 体内评价

双侧 MC38/EMT6、Panc02 和 MC38-Luc 模型检验局部、远端和静脉给药效果；aMP~C16~-CA~50~ 静脉剂量为 15 mg kg−1，anti-PD-L1 按模型设定。另以血清生化、器官 H&E 和最大耐受剂量评估毒性。

### 证据边界

本地 Nature 页面主要开放摘要、图注和补充入口；详细方法来自官方 Supplementary Information。未发现公开 GitHub/代码仓库，因此这是 `paper-only` 分析，不能把流程描述误写成已验证的可运行软件。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem and contribution

Conventional lytic tumour-cell death can be immunologically weak or poorly timed. Yuan et al. design a synthetic acid-responsive membranolytic peptide, aMP~C16~-CA~50~, to program immunogenic membranolytic cell death (mLCD): lysosomal membrane rupture occurs before delayed plasma-membrane rupture.

### Method and evidence

The study combines peptide chemistry and biophysical characterization with pH-dependent cell assays, live confocal rupture timing, LDH/HMGB1 release, regulated-death markers, CRISPR knockouts, dendritic-cell/OT-I assays, bulk and single-cell RNA-seq, and mouse tumour models. The abstract reports inflammatory transcription, enhanced MHC-I antigen presentation and stronger anti-PD-L1 responses; captions and supplementary methods specify the experimental controls and analysis tools.

### Reproducibility

The Nature HTML exposes no public code repository, and no end-to-end implementation was found. Sequencing data are deposited under PRJNA1091224, PRJNA1413508 and PRJNA1417626, while source data and supplementary files are linked by Nature. Reproduction therefore requires external data, peptide synthesis and the documented experimental workflow. Main-text quantitative details are partly inaccessible from the local publisher page.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
