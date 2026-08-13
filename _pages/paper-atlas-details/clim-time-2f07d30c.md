---
layout: default
permalink: /paper-atlas/clim-time-2f07d30c/
title: "CLIM_TIME"
nav: false
description: "这篇 Cell 论文提出的问题是：肿瘤抑制基因（TSG）缺失怎样改变转移灶的肿瘤微环境（TME），进而影响 T 细胞治疗效果。传统 CRISPR 筛选可以找到免疫调节基因，但通常缺少空间微环境信息；空间组学可以看微环境，但很难一次系统筛查数百个基因扰动。论文把这个缺口概括为：缺少能够在空间复杂 TME 中高通量解析“基因扰动-免疫状态-治疗反应”的方法。"
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
      <span>Cell-Cell Communication</span>
      <span>Cell · 2026</span>
    </div>
    <h1>CLIM_TIME</h1>
    <p>CLIM-TIME identifies metastatic microenvironment modulators for T cell therapy response</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2025.12.042" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CLIM_TIME">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/sherry1000001/CLIM-TIME" target="_blank" rel="noopener noreferrer" aria-label="Open code for CLIM_TIME">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CLIM-TIME 方法中文解释

### 这篇文章解决什么问题？

这篇 Cell 论文提出的问题是：肿瘤抑制基因（TSG）缺失怎样改变转移灶的肿瘤微环境（TME），进而影响 T 细胞治疗效果。传统 CRISPR 筛选可以找到免疫调节基因，但通常缺少空间微环境信息；空间组学可以看微环境，但很难一次系统筛查数百个基因扰动。论文把这个缺口概括为：缺少能够在空间复杂 TME 中高通量解析“基因扰动-免疫状态-治疗反应”的方法（`paper.md:25-29`）。

### CLIM-TIME 的核心思想

CLIM-TIME 的全称是 CRISPR-laser-captured microdissection integration mapping of the tumor-immune microenvironment。它把体内 CRISPR 筛选、荧光标记的克隆性肺转移灶、激光捕获显微切割（LCM）、SMART-seq、sgRNA 读出、多重免疫荧光和转录组去卷积整合到同一个平台中（`paper.md:37-45`）。

可以把它理解成一个“带空间读出的体内扰动筛选”：

```text
TSG sgRNA 文库
    -> 带不同荧光颜色的 KP 肺癌细胞
    -> 小鼠体内形成克隆性肺转移灶
    -> 对每个转移灶做 LCM + SMART-seq + sgRNA 读出
    -> 对相邻切片做 CD8a/CD4/CD11b 免疫荧光
    -> 计算每个克隆的 TME 组成、免疫浸润和治疗反应关联
```

这样，每个转移灶不只是一个测序样本，而是同时带有：哪个 TSG 被敲除、肿瘤细胞转录组、免疫细胞组成、空间浸润状态和治疗反应线索。

### 关键计算步骤：两步去卷积

论文中最明确、公开代码也能对应上的计算模块是两步去卷积。第一步用 BayesPrism 把 LCM/SMART-seq 的混合 RNA-seq 表达分解为 5 类大细胞类型：癌细胞、B 细胞、NK 细胞、T 细胞和髓系细胞。第二步使用单细胞 RNA-seq 得到的 marker signature，借鉴 xCell 思路，用 ssGSEA 进一步区分相近亚群，例如单核细胞、巨噬细胞、CD4 T 和 CD8 T（`paper.md:45-45`, `paper.md:301-303`）。

公开代码中，`2-step deconvolution.r` 读取 bulk/LCM 表达和 scRNA 参考，调用 `new.prism` 和 `run.prism` 得到 broad cell type fraction，然后读取 `second.deconv.markers.for.t.mye.csv`，用 GSVA/ssGSEA 计算 marker 活性，并把 broad T cell 与 myeloid 比例拆分成 CD4T、CD8T、neutrophil、monocyte 和 macrophage（`CLIM-TIME/2-step deconvolution.r:4-63`）。

### 从 TME 类型到治疗反应

CLIM-TIME 捕获了 3,286 个 LCM 转移灶，其中大多数是单克隆，并在高质量克隆中检测到 360 个 TSG（`paper.md:37-39`）。论文把免疫丰度和浸润状态聚类成多个 TME/TIME 类型，例如 CD4-II、CD8-II、T-II、M/T-II、M-II/T-IE、B-II 和 ID（`paper.md:43-45`）。

然后，作者把这些 TME 类型与多种 CRISPR 筛选结果相连：肺转移筛选、免疫逃逸筛选、T 细胞治疗筛选，以及不同癌种模型中的 T 细胞治疗筛选。结果显示，DNA 修复和 PRC 相关 TSG 缺失更容易产生 T 细胞浸润、治疗敏感的 TME；Hippo 通路相关 TSG（如 Nf2、Arhgap35）缺失更容易产生髓系富集、T 细胞排斥的 TME，并导致治疗抵抗（`paper.md:55-63`）。

### LOXL2 机制

论文进一步追踪 Nf2 缺失为什么导致 T 细胞排斥。主要机制是 Hippo/YAP 相关改变上调 LOXL2，LOXL2 促进胶原交联和 ECM 变硬，增强 FAK 信号，吸引髓系细胞并阻碍 T 细胞进入肿瘤核心（`paper.md:77-89`）。图 5 的 Masson 染色、SHG 胶原成像、CD11b/CD8a 免疫荧光、p-FAK 染色和生存曲线共同支持这个机制。

当敲除 LOXL2、做 LOXL2 Y689F 催化失活突变、敲除或抑制 FAK 时，Nf2-KO 造成的治疗抵抗可以被部分逆转，T 细胞治疗效果提高（`paper.md:87-99`）。因此，LOXL2/FAK 是从 CLIM-TIME 图谱中挖出的可干预微环境轴。

### 免疫治疗预测模型

最后，作者把小鼠 CLIM-TIME 中得到的“调控免疫浸润的因果基因”与人类免疫检查点治疗队列的转录组差异基因整合，构建 30 基因免疫治疗响应预测模型。论文方法部分说，因果基因先用 GENIE3 随机森林框架推断，再用置换检验和 Pearson 相关判断显著性与方向；随后映射到人类同源基因，与 responder/non-responder 差异基因取交集，用随机森林训练 Immunotherapy Response Score（IRS）（`paper.md:327-337`）。

公开代码 `predictive model.r` 覆盖了模型训练的一部分：使用 `mlr3` 进行特征选择、把人类表达与 CIBERSORT TME 组成合并、定义多个候选分类器、随机搜索调参，并计算 ROC/AUC（`CLIM-TIME/predictive model.r:1-104`）。但是 GENIE3 因果基因推断、完整原始数据预处理和最终 30 基因确定过程没有在公开 GitHub 中找到。

### 代码复现边界

这篇文章的公开代码可以帮助理解两步去卷积和预测模型训练，但不是完整端到端复现包。公开仓库缺少 MAGeCK sgRNA 筛选分析、GENIE3 因果推断、CellChat 互作分析、原始数据预处理和绘图脚本。论文的数据可用性部分说明，scRNA-seq、bulk RNA-seq、CRISPR 文库和 Mageck 结果在 OMIX/GEO/ENA，GitHub 主要提供 RNA-seq 去卷积和预测模型训练代码（`paper.md:135-137`）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CLIM-TIME Summary

### What Problem Does It Solve?

CLIM-TIME studies how tumor suppressor gene (TSG) loss reshapes metastatic tumor microenvironments and changes T cell therapy response. The paper argues that standard CRISPR screens can find immune modulators but usually do not resolve spatially complex TMEs, while spatial profiling alone does not scale to hundreds of perturbations (`paper.md:25-29`).

### Method Overview

CLIM-TIME combines an in vivo TSG CRISPR perturbation screen with fluorescent clonal lung metastases, laser-capture microdissection, SMART-seq, sgRNA readout, multiplexed immunofluorescence, and computational deconvolution (`paper.md:37-45`). The main computational step is a two-stage deconvolution: BayesPrism estimates broad cancer/immune cell classes, then scRNA-derived signatures and ssGSEA refine related immune subtypes such as monocytes and macrophages (`paper.md:45-45`, `paper.md:301-303`).

The resulting clone-level map links each TSG knockout to immune-cell abundance, infiltration state, and screen response under immune evasion or T cell therapy conditions. This identifies TME states such as T cell-infiltrated, myeloid-rich/T cell-excluded, and immune desert niches (`paper.md:43-45`, `paper.md:61-63`).

### Main Biological Findings

The screen links DNA repair and Polycomb repressive complex TSG loss to T cell therapy sensitivity, while Hippo-pathway TSG loss, especially Nf2/Arhgap35, is associated with myeloid-rich, T cell-excluded TMEs and therapy resistance (`paper.md:55-63`). Mechanistically, Nf2 loss upregulates LOXL2, which promotes collagen-rich ECM, FAK signaling, myeloid recruitment, and CD8 T cell exclusion. Genetic or pharmacological disruption of LOXL2/FAK improves T cell therapy outcomes in multiple metastasis models (`paper.md:77-99`).

The paper also builds a transcriptome-based immunotherapy predictor by integrating mouse CLIM-TIME causal genes with human ICI response transcriptomes. It reports a 30-gene model with AUROC 0.865 and survival stratification across several cohorts (`paper.md:101-107`, `paper.md:333-337`).

### Code And Data Reproducibility

The paper makes datasets available through OMIX, GEO, and ENA, and points code for RNA-seq deconvolution and predictive model training to GitHub (`paper.md:135-137`). The official repository is small but relevant: `2-step deconvolution.r` implements the BayesPrism plus ssGSEA deconvolution flow (`CLIM-TIME/2-step deconvolution.r:4-63`), and `predictive model.r` implements feature selection, ensemble learner tuning, and AUC evaluation (`CLIM-TIME/predictive model.r:1-104`).

Reproducibility rating: **3/5**. The public code covers two central computational components, but the full pipeline is not directly runnable from raw data. Missing public code includes MAGeCK screen analysis, GENIE3 causal-gene inference, CellChat analysis, complete preprocessing scripts, and figure-generation notebooks. These gaps are documented in `doc_code.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
