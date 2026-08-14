---
layout: default
permalink: /paper-atlas/hcmi-nextgen-patient-derived-cancer-models-7f3b7968/
title: "HCMI_NextGen_Patient_Derived_Cancer_Models"
nav: false
wide: true
description: "传统癌细胞系资源促进了基因依赖性研究，但常缺少与原始肿瘤的系统配对验证、罕见癌种覆盖和临床治疗背景。本文建立 Human Cancer Models Initiative (HCMI)：665 个患者来源模型，覆盖 25 类恶性肿瘤，并将模型、亲本肿瘤、部分正常样本、临床信息和多组学表征连接起来。 模型包括 3D 类器官、3D 球体及 2D 贴壁培养；论文也记录治疗史、随访和人群信息。"
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
      <span>Nature · 2026</span>
    </div>
    <h1>HCMI_NextGen_Patient_Derived_Cancer_Models</h1>
    <p>A compendium of next-generation patient-derived models for diverse cancers</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-026-10806-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for HCMI_NextGen_Patient_Derived_Cancer_Models">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/broadinstitute/DepMap-NextGen-Public" target="_blank" rel="noopener noreferrer" aria-label="Open code for HCMI_NextGen_Patient_Derived_Cancer_Models">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## HCMI 下一代患者来源癌症模型图谱

### 研究解决什么问题？

传统癌细胞系资源促进了基因依赖性研究，但常缺少与原始肿瘤的系统配对验证、罕见癌种覆盖和临床治疗背景。本文建立 Human Cancer Models Initiative (HCMI)：665 个患者来源模型，覆盖 25 类恶性肿瘤，并将模型、亲本肿瘤、部分正常样本、临床信息和多组学表征连接起来。

### 整体流程

```text
患者肿瘤/血液或正常组织
  -> 按癌种优化培养、连续传代、认证和建库
  -> 全基因组/外显子组、甲基化、bulk RNA 和部分单核 RNA 测量
  -> 将模型与亲本肿瘤逐对比较
  -> 输出可分发模型、注释数据和探索工具
```

模型包括 3D 类器官、3D 球体及 2D 贴壁培养；论文也记录治疗史、随访和人群信息（`paper.md:54-63`）。

### 如何定义“忠实”

DNA 层面比较 SNV/indel、LOH、全基因组倍增、突变特征、驱动改变和 ecDNA。LOH 用每个基因组 bin 的少数拷贝数是否为零判断；配对一致率是所有 bin 一致性的平均值（`paper.md:334-340`）。突变特征由 SignatureAnalyzer 分解，肿瘤和模型的暴露向量用余弦相似度比较（`paper.md:343`）。

对于纯度 $\rho$、肿瘤拷贝数 $T$ 和正常细胞拷贝数 $N$，文章用于功效计算的预期变异等位基因频率为：

$$
\mathrm{VAF}=\frac{\rho}{\rho T+(1-\rho)N}.
$$

甲基化层面从癌相关 CpG 位点计算模型与肿瘤的 Pearson 相似度，并以与不匹配肿瘤比较的 FDR 判断是否一致。转录组层面使用 Celligner，加上五种独立相似性方法、TMP 分型及 MOMA 调控逻辑验证（`paper.md:98-115`）。

单核 RNA 流程为：Scanpy 质控、归一化/PCA/邻居图/UMAP，再用 inferCNV 结合 bulk WGS 定义恶性细胞；GBM、PAAD 和 COAD 分别用已发表状态或亚型签名赋值（`paper.md:550-595`）。

### 主要结论

经低纯度样本筛除后，97.8% 的优先 HCMI 模型至少保留四类 DNA 特征中的两类；201 对可测甲基化样本中 190 对一致；多指标 RNA 评价中大部分模型仍与亲本肿瘤相符。HCMI 还增加了罕见癌、癌前病变和部分传统资源不足的癌种覆盖（`paper.md:92`, `:98-124`, `:127-141`）。

### 应如何使用这些结论？

“患者来源”并不自动保证所有层面的忠实。GBM 的培养基可显著改变细胞状态，因此实验设计需要保留培养条件、传代和肿瘤纯度等信息。ecDNA 也比多数 DNA 指标更容易出现差异。HCMI 更适合作为带条件和证据等级的转化研究资源，而不是把每个模型视为原始肿瘤的完全复制品。

### 代码状态

提供的 DepMap 代码库能直接复现部分 Celligner 和功能依赖性分析，例如 kNN 谱系分类及 NextGen/传统模型比较（`src/generate.py:561-644`; `src/celligner.py:383-481`）。在该快照中未找到本文 WGS、甲基化、ecDNA、单核分析和 HCMI Explorer 的完整实现，因此不能把它视为全文分析管线。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Contribution

This Nature 2026 paper presents the Human Cancer Models Initiative (HCMI), a patient-derived cancer-model atlas created to address the limited diversity, uncertain fidelity and sparse clinical annotation of conventional cell-line collections. It provides 665 accessible organoid, neurosphere and cell-line models from 637 patients spanning 25 malignancies, with matched molecular and clinical evidence where available (`paper.md:12`, `:34`, `:54-63`). It is an atlas/resource, not a review article.

### Why Existing Collections Were Insufficient

Large cancer-cell-line compendia have enabled dependency mapping but typically have restricted phenotypic complexity, uncertain relation to the originating tumour and inadequate clinical context (`paper.md:25-31`). HCMI pairs new culture approaches with standardized banking, clinical capture and multi-omic tumour/model assessment.

### Main Approach

The paper derives and quality-controls models, then tests tumour-model fidelity with WGS/exome calls, copy number/LOH/WGD, mutation signatures, drivers and ecDNA; DNA methylation; Celligner and additional RNA similarity methods; subtype/regulatory analyses; and selected single-nucleus state comparisons. It compares the resource with CCLE and uses treatment history and model profiling to support translational applications.

### Evidence and Results

- 421 matched tumour-model pairs were available for core DNA analysis; 97.8% of prioritized models retained at least two of four DNA feature classes after prolonged culture (`paper.md:69-92`).
- 190/201 methylation pairs and 242/297 Celligner RNA pairs met the paper's concordance criteria; 263/286 models tested by at least four RNA metrics were discordant by no more than one (`paper.md:98-124`).
- The resource adds rare, pre-malignant and underrepresented-patient models, and expands several disease areas relative to CCLE (`paper.md:127-141`).
- GBM culture medium can alter cell states, so fidelity is conditional on culture context rather than a universal property (`paper.md:118-124`).

### Reproducibility

Paper data are available through the HCMI/GDC/cBioPortal ecosystem, with controlled raw sequencing in dbGaP (`paper.md:628-637`). The supplied `DepMap_NextGen_Public` snapshot is at commit `5c6f1e0` and contains reproducible Celligner and dependency-analysis components, but it is only a partial paper-code match: it does not contain direct implementations for the flagship WGS, methylation, ecDNA, single-nucleus or explorer workflows. Its README requires a named DepMap Portal data release plus Poetry/R dependencies. The resulting code-paper fidelity is **medium**, with the absent analyses explicitly marked `Not found` in `doc_code.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
