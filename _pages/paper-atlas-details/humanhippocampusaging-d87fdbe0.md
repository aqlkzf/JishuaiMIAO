---
layout: default
permalink: /paper-atlas/humanhippocampusaging-d87fdbe0/
title: "HumanHippocampusAging"
nav: false
wide: true
description: "以往研究知道衰老脑组织会出现炎症增强、突触功能下降，但很难回答：这些表达变化由哪些细胞产生，又是染色质开放、DNA 甲基化、增强子连接还是三维基因组折叠改变造成的？本文对 40 名 20–100 岁、性别与年龄段平衡的神经正常供体进行单细胞核多组学分析，把四层调控信息放进同一套细胞类型框架。 作者先按细胞类型汇总每个供体的表达、开放性和甲基化特征，再计算特征与年龄的 Pearson 相关，并用 FDR < 0.1 筛选。"
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
      <span>Science · 2026</span>
    </div>
    <h1>HumanHippocampusAging</h1>
    <p>Epigenetic and 3D genome reprogramming during the aging of the human hippocampus</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1126/science.adt8307" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for HumanHippocampusAging">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/nrzemke/aging_human_hippocampus" target="_blank" rel="noopener noreferrer" aria-label="Open code for HumanHippocampusAging">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 人类海马衰老的表观基因组与三维基因组重编程

### 这篇论文解决什么问题？

以往研究知道衰老脑组织会出现炎症增强、突触功能下降，但很难回答：这些表达变化由哪些细胞产生，又是染色质开放、DNA 甲基化、增强子连接还是三维基因组折叠改变造成的？本文对 40 名 20–100 岁、性别与年龄段平衡的神经正常供体进行单细胞核多组学分析，把四层调控信息放进同一套细胞类型框架。

### 核心设计

```text
40 例海马组织
  ├─ 10x multiome：RNA + ATAC（295,033 个质控后细胞核）
  └─ snm3C-seq：DNA 甲基化 + 3C 接触（22,240 个细胞核）
          ↓
细胞类型整合 → cCRE/DMR → 年龄相关性与非线性模块
          ↓
ABC 增强子-基因连接 + compartment/TAD/CTCF 分析
          ↓
重点解释 microglia、astrocyte 与全局 3D 基因组衰退
```

作者先按细胞类型汇总每个供体的表达、开放性和甲基化特征，再计算特征与年龄的 Pearson 相关，并用 FDR < 0.1 筛选。为了捕捉“不是一直线变化”的衰老轨迹，他们还比较四个年龄组的所有两两组合，再将显著基因和 cCRE 聚成十个动态模块。增强子预测采用 ABC 模型：把 ATAC 活性和 10-kb 接触频率结合，只保留表达量 CPM≥1 的基因和 ABC 分数≥0.02 的连接。

### 关键发现

1. 许多调控变化在约 50 岁附近出现拐点，而不是从青年到老年匀速改变。
2. 胚胎卵黄囊样 Micro1 随年龄减少，具有外周血单核细胞样表观基因组的 Micro2 增加；Micro2 的炎症基因、增强子与三维接触更活跃。但这是“分子相似性 + 分类器”证据，不等同于直接谱系追踪。
3. 海马星形胶质细胞比例下降，尤其涉及突触支持的亚型；NRF1 motif 可及性和线粒体 ATP 合成靶基因同步下降。
4. 多种细胞的染色质长程接触和 TAD 内接触随年龄减弱，CTCF CUT&Tag 也下降，说明维持拓扑结构的 loop extrusion 边界逐渐松动。

### 如何理解代码与可复现性

公开仓库包含甲基化聚类、跨模态整合、DMR、年龄相关、ABC 和 3D 接触分析脚本/Notebook，与论文分析方向基本一致。不过代码使用作者本地绝对路径，缺少统一入口、环境锁定、测试和示例数据，因此更像“分析记录”而不是开箱即用的软件。数据已在 GEO、4DN 和 WashU 浏览器公开；完整复现仍需下载大规模原始/中间数据并人工恢复执行顺序。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Human hippocampus aging multiomic atlas

### Problem and contribution

Zemke et al. ask how transcription, chromatin accessibility, DNA methylation, and three-dimensional genome folding jointly change across normal adult aging in the human hippocampus. Earlier transcriptomic studies established inflammatory activation and synaptic decline, but did not resolve the regulatory layers or cell types that produce those signals. The study profiles 40 neurotypical postmortem donors, balanced across four 20-year age bins and sex, with 10x single-nucleus RNA+ATAC multiome and snm3C-seq (joint methylation+3C).

The result is a lifespan atlas containing 295,033 quality 10x nuclei and 22,240 snm3C nuclei. It integrates expression, accessibility, methylation and chromatin contact maps, calls 472,859 candidate cis-regulatory elements and 940,687 DMRs, and links 75,177 putative enhancer–gene pairs with the ABC model. Age associations are assessed both linearly (Pearson correlation with donor age) and nonlinearly (pairwise age-bin differential testing followed by k-means modules).

### Main findings

- Gene expression and accessibility often shift nonlinearly around age 50; 6,478 genes, 12,474 cCREs and 17,355 DMRs have significant age-correlated activity.
- A microglial state resembling peripheral-blood monocytes expands with age while the embryonic/yolk-sac-like state declines. Its methylome, accessible chromatin, transcriptional programs and 3D contacts are enriched for inflammatory regulation.
- Astrocyte abundance declines with age, including synaptic-supporting subtypes. NRF1 motif accessibility and mitochondrial ATP-synthesis programs decline, providing a regulatory explanation for impaired astrocyte energetics.
- Across cell types, chromatin contacts and intra-TAD organization erode with age. Reduced CTCF binding measured by CUT&Tag supports weakening of loop-extrusion boundaries.

### Evidence and limitations

The seven main figures directly support the cohort/design, age-associated modules, microglial transition, astrocyte loss, and 3D-genome erosion. The study combines orthogonal modalities and validates selected cellular phenotypes by immunofluorescence and CTCF CUT&Tag. It is nevertheless cross-sectional postmortem evidence rather than longitudinal lineage tracing: the proposed monocyte contribution is supported by epigenomic similarity and classifiers, not direct fate mapping. Donor-level sample size is 40, and some subtype analyses depend on sparse single-nucleus contacts.

### Reproducibility

Data are deposited under GEO GSE278576, GSE299139 and GSE299899, with 4DN and WashU browser access. The linked GitHub snapshot (commit `94d9b7a`) contains processing and analysis scripts, including methylation clustering, cross-modality integration, DMR analysis, age-correlation notebooks and 3D-genome notebooks. Code-paper fidelity is **medium**: major analysis families are represented, but the repository is path-bound, lacks a workflow manifest, environment lock, tests, input data, and a single runnable entry point. Reproduction requires rebuilding the authors' directory layout and downloading large controlled/public datasets.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
