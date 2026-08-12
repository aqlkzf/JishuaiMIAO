---
layout: default
permalink: /paper-atlas/narmbench-dbc900f1/
title: "NaRMBench"
nav: false
description: "纳米孔 direct RNA sequencing（DRS）可以从原始电流信号中同时寻找多种 RNA 修饰，但不同软件使用的特征、训练样本、对照设计和阈值差异很大。NaRMBench 不提出一个新的 caller，而是建立统一的“赛场”，系统比较 m^6^A、Ψ、m^5^C、A-to-I、m^7^G 和 m^1^A 六类修饰的检测工具。"
robots: noindex, nofollow
sitemap: false
---

<!-- Generated locally by bin/export_paper_atlas.py. -->
<section class="paper-detail" id="paper-detail">
  <a class="paper-detail__back" href="{{ '/paper-atlas/' | relative_url }}">
    <i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Back to Paper Atlas
  </a>
  <header class="paper-detail__hero">
    <div class="paper-detail__chips">
      <span>Computational Tools</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>NaRMBench</h1>
    <p>Systematic evaluation of computational tools for multitype RNA modification detection using nanopore direct RNA sequencing</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02974-y" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## NaRMBench 方法详解

### 它解决什么问题？

纳米孔 direct RNA sequencing（DRS）可以从原始电流信号中同时寻找多种 RNA 修饰，但不同软件使用的特征、训练样本、对照设计和阈值差异很大。NaRMBench 不提出一个新的 caller，而是建立统一的“赛场”，系统比较 m^6^A、Ψ、m^5^C、A-to-I、m^7^G 和 m^1^A 六类修饰的检测工具。

### 核心设计

```text
RNA002 / RNA004 原始 DRS 数据
        ↓ 统一预处理与各工具推断
每个位点的标签、分数、深度、motif、修饰比例
        ↓ 与独立的单碱基 NGS ground truth 对齐
准确性 + 生物学合理性 + 稳健性 + 计算效率
        ↓
按修饰类型和测序 chemistry 给出工具画像
```

研究共评价 86 个工具实例：39 个原始工具，以及用 m6Anet、EpiNano、NanoSPA、Dinopore、TandemMod、SingleMod 六个框架得到的 47 个重训练模型。为了避免数据泄漏，同一比较中的工具使用相同测试集，而且测试样本与原论文训练集、本文重训练集都来自不同来源。

### 为什么重训练很重要？

仅用 100% 修饰的 IVT RNA 训练，样本虽多但与真实细胞中的信号复杂性不一致。论文发现真实生物样本训练通常更好，IVT 与多种细胞样本混合往往进一步提升泛化。例如 Ψ 的 NanoSPA 混合训练模型 AUROC 达到 0.73；TandemMod 加入 HEK293T、A549 与 IVT 后，修饰比例相关性提高到 Pearson $r=0.27$。

### 怎么评分？

分类性能使用 AUROC、AUPRC、Precision、Recall 和 F1；每个工具扫描阈值并选择 F1 最大的阈值。可定量工具还把真实修饰比例分为七档，比较每档预测中位数并计算 Pearson 相关。除此之外还检查：位点是否落在合理转录本区域和 motif、WT 与 KO 是否有预期差异、多修饰 caller 是否产生互相冲突的标签、重复间 Jaccard/相关性、深度与 motif 偏差、运行时间和内存。

### 主要结论

- m^6^A 最成熟：RNA002 中 m6Anet 的 AUROC/AUPRC 为 0.76/0.82；RNA004 中 Dorado 为 0.90/0.89。
- Ψ、m^5^C、A-to-I 的重训练模型常能提升 AUROC，但 precision–recall 仍弱；多数 Ψ 工具 F1 小于 0.2。
- m^1^A 与 m^7^G 的 held-out 表现接近随机（AUROC 约 0.5，AUPRC 约 0.01）。
- RNA004 的改进对 m^6^A 很明显，但并不会自动解决其他修饰。
- 没有一个工具在准确性、生物学合理性、稳健性和效率上全面最好，选择工具必须根据具体修饰、chemistry 和研究目标。

### 复现性判断

仓库公开了预处理/重训练教程、修改后的代码压缩包、模型权重、标准化评估命令和绘图脚本，因此评价定义可追踪；但缺少统一环境与一键工作流，部分脚本也有小错误，完整复现仍需自行准备大型数据和外部软件。总体代码—论文一致性为中等。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## NaRMBench summary

NaRMBench is a large benchmark of nanopore direct-RNA-sequencing callers for six RNA modifications. It compares 86 tool instances—39 published implementations and 47 models retrained from six reusable frameworks—across RNA002 and RNA004 chemistries using held-out, single-nucleotide ground truth. Unlike earlier comparisons focused mainly on m^6^A and accuracy alone, it measures accuracy, biological validity, robustness and computational efficiency.

The benchmark shows that training data matter at least as much as model architecture. Models trained on real biological samples outperform IVT-only models in many cross-dataset tests, and mixed IVT/biological training often generalizes best. m^6^A detection is comparatively mature: m6Anet leads RNA002 (AUROC 0.76, AUPRC 0.82) and Dorado leads RNA004 (0.90, 0.89). For Ψ, m^5^C and A-to-I, retraining can substantially improve AUROC, but most methods still have poor precision–recall balance. m^1^A and m^7^G remain especially unreliable.

The public NaRMBench repository closely supports the evaluation layer: preprocessing/retraining command guides, model artifacts, standardized evaluation recipes, normalized example data and scripts for ROC/PR, quantification, optimal thresholds, replicate robustness and radar plots. Fidelity is medium because framework internals are partly packaged as ZIPs, external datasets/tools are required, no unified environment or end-to-end workflow exists, and some downstream scripts contain execution defects. The materials are nevertheless sufficient to inspect the benchmark definitions and reproduce selected analyses after environment and data assembly.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
