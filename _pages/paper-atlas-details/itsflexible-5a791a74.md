---
layout: default
permalink: /paper-atlas/itsflexible-5a791a74/
title: "ITsFlexible"
nav: false
wide: true
description: "抗体和 TCR 的 CDR3 环可能在多个构象之间转换，影响亲和力、特异性和多反应性；而常规结构预测通常只给出一个静态结构。论文把任务定义为二分类：预测环是“柔性”（存在多个构象）还是“刚性”（主要保持一个构象）。 作者从 PDB、SAbDab 和 TCR 结构数据库系统收集由两条反平行 β 链夹住的环，构建 ALL-conformations，超过 120 万个结构、10 万个以上独特序列。"
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
      <span>Protein &amp; Sequence Models</span>
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>ITsFlexible</h1>
    <p>Predicting the conformational flexibility of antibody and T cell receptor complementarity-determining regions</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-025-01131-6" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ITsFlexible">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/oxpig/ITsFlexible" target="_blank" rel="noopener noreferrer" aria-label="Open code for ITsFlexible">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ITsFlexible 方法说明

### 要解决的问题

抗体和 TCR 的 CDR3 环可能在多个构象之间转换，影响亲和力、特异性和多反应性；而常规结构预测通常只给出一个静态结构。论文把任务定义为二分类：预测环是“柔性”（存在多个构象）还是“刚性”（主要保持一个构象）。

### 数据和标签

作者从 PDB、SAbDab 和 TCR 结构数据库系统收集由两条反平行 β 链夹住的环，构建 ALL-conformations，超过 120 万个结构、10 万个以上独特序列。相同序列的结构用 Cα RMSD 做 complete-linkage 聚类，阈值为 1.25 Å；多簇标为柔性，只有在至少 5 个不同 PDB 文件中都保持单簇才标为刚性，否则标为未知（`paper.md:212-239`）。

### 计算流程

```text
PDB 结构 + 环的链/残基范围
       ↓
读取 Cα → 选取环及 10 Å 内的结构上下文
       ↓
残基图：22 维节点特征 + 局部边 + 8 个 RBF 距离特征
       ↓
三层 E(3) 等变图网络 → 图池化 → sigmoid
       ↓
柔性概率
```

节点编码包括氨基酸类型、环/上下文标记和 Cα 坐标；边编码包括共价键标记及 0–10 Å 的八个高斯径向基函数。网络对整体平移、旋转和反射不敏感，只使用相对几何关系（`paper.md:248-257`）。训练采用 70/15/15 划分、跨集合最多 80% 序列一致性、BCE 损失和 Adam（学习率 2×10⁻⁴、权重衰减 10⁻⁶），并以验证 PR-AUC 选择十个模型中的最佳者（`paper.md:260-266`）。

### 结果和边界

在 2,845 个 PDB 测试环上，PR AUC=0.62、ROC AUC=0.84，优于长度、溶剂暴露、组合生物物理特征和 AF2-pLDDT 基线。模型在 H3、L3、B3、A3 CDR 测试集上总体稳定；19 个抗体的 MD 模拟中，H3 几乎完美分离，L3 稍弱。三个冷冻电镜案例中有两个与预测一致（`paper.md:84-178`）。

公开 GitHub 仓库包含图构建、模型、训练配置、检查点和 CSV 推理入口；但未包含 PDB 挖掘/标签生成、完整基准聚合、AF2/ABB2、MD 和冷冻电镜处理脚本。因此仓库足以复现模型推理，却不足以独立重建论文全部实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ITsFlexible Summary

### Problem

Antibody and TCR CDR loops can adopt multiple conformations, affecting affinity, specificity and polyspecificity, but standard structure predictors mainly return one static structure. Experimental flexibility measurements are sparse and MD is expensive (`paper.md:25-46`).

### Proposed method

ITsFlexible is a graph-neural-network binary classifier trained on ALL-conformations, a PDB/SAbDab/TCR-derived collection of >1.2 million loop structures and >100,000 sequences. It represents a loop and its 10-A structural context as residue nodes with C-alpha geometry, amino-acid identity and loop/context labels, then predicts a flexible probability with an E(3)-equivariant network (`paper.md:66-81,248-266`).

### Results

On 2,845 held-out PDB loops it reaches PR AUC 0.62 and ROC AUC 0.84, outperforming length, solvent exposure, combined biophysical and AF2-pLDDT baselines. It generalizes to antibody/TCR CDRH3/L3/B3/A3 sets, performs strongly on MD ensembles of 19 antibodies, and two of three cryo-EM case-study predictions agree with observed conformational heterogeneity (`paper.md:84-118,136-178`).

### Reproducibility

Code and trained checkpoints are available at `https://github.com/oxpig/ITsFlexible` and the paper links the ALL-conformations data through Zenodo. The repository is a high-fidelity implementation of graph construction, training and inference, with runnable CSV examples. The PDB mining/labeling pipeline, full evaluation aggregators, AF2/ABB2 baselines, MD and cryo-EM workflows are not included, so exact benchmark reproduction is incomplete.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
