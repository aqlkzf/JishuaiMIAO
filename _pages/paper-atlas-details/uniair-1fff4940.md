---
layout: default
permalink: /paper-atlas/uniair-1fff4940/
title: "UniAIR"
nav: false
wide: true
description: "UniAIR 预测突变如何改变适应性免疫识别中的结合或功能效应，例如抗体成熟、抗原逃逸和 TCR-pHLA 识别。论文摘要指出，许多已有方法只适用于单一任务或单一模态，难以在不同免疫复合物间泛化（PAPERMD:9-16）。 它不把所有任务交给一个单模型，而是将多个专家模型的预测与表示融合。仓库中的专家包括 Gearbind、RDE、PPIformer 和 ESSM。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>UniAIR</h1>
    <p>Generalizable mutation-effect prediction across adaptive immune recognition via unified multimodal framework</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-026-01243-7" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for UniAIR">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/hanrthu/UniAIR" target="_blank" rel="noopener noreferrer" aria-label="Open code for UniAIR">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## UniAIR 方法解读

### 它解决什么问题

UniAIR 预测突变如何改变适应性免疫识别中的结合或功能效应，例如抗体成熟、抗原逃逸和 TCR-pHLA 识别。论文摘要指出，许多已有方法只适用于单一任务或单一模态，难以在不同免疫复合物间泛化（`paper source:9-16`）。

### 核心想法

它不把所有任务交给一个单模型，而是将多个专家模型的预测与表示融合。仓库中的专家包括 Gearbind、RDE、PPIformer 和 ESSM。UniAIR 使用 WT 与突变体的结构表示差异，再根据这个差异和各专家嵌入，为每个样本学习不同的专家权重（`models/encoders/UniAIR/model.py:34-130`）。因此，同一系统可在不同界面、不同突变类型和不同下游任务中动态选择更合适的专家组合。

### 输入到输出的流程

```text
复合物 CSV + WT/突变体结构 + 突变字符串
             |
             v
解析链、配体/受体分组、标签和突变位点
             |
             v
构造 aa_mut 与 mut_flag，并提取序列、二面角和几何特征
             |
             +--> Gearbind
             +--> RDE
             +--> PPIformer
             +--> ESSM
             |
             v
WT 与突变体结构门控表示之差 + 专家嵌入
             |
             v
softmax 门控权重加权各专家预测
             |
             v
突变效应预测（常见为 DeltaDeltaG，也可为二分类）
```

数据层 `WithMutationDataset` 从 CSV 中读取 `path_wt`、`path_mut`、`mutation`、`Partners(A_B)`、`valid_chains` 和标签等字段；它把突变映射到氨基酸索引，得到 `aa_mut` 和 `mut_flag`（`data/unippi_dataset.py:118-166,195-241`）。`MutationDataModule` 再按 `fold_*` 列划分训练、验证和测试集（`pl_modules/data_module.py:61-80`）。

### 门控融合如何计算

代码先通过单残基编码、残基对编码和几何注意力获得 WT/突变体的表示。池化后的差为 (H_{ipa})。对第 (i) 个专家得到预测 (p_i) 和嵌入 (e_i)，再由门控网络产生权重：

$$
\alpha=\operatorname{softmax}\left(\frac{W([H_{ipa};e_1;\ldots;e_K])}{2.5}\right),\qquad
\hat y=\sum_i \alpha_i p_i.
$$

这段公式来自代码实现（`models/encoders/UniAIR/model.py:101-130`）；本地 Nature HTML 未提供论文正文中的公式，因此不能把它当作论文原文公式。默认实现会冻结专家参数，再训练融合部分（`model.py:39-51`）。

### 训练和评估

连续任务使用 MSE，二分类任务使用 binary cross-entropy with logits；不同任务的损失会按权重与可用标签掩码汇总（`utils/metrics.py:125-165`）。验证和测试计算 Pearson、Spearman、RMSE、MAE，以及按复合物汇总的指标（`pl_modules/model_module.py:185-222,257-300`）。默认 UniAIR YAML 使用 Adam，学习率 `3e-4`，并使用 plateau 学习率调度器（`config/models/train/UniAIR.yaml:29-45`）。

### 图中展示的应用

图 2 展示 SKEMPIv2 与独立测试；图 3 展示零样本突变扫描；图 4 展示少样本抗原逃逸；图 5 显示和 FEP 反馈耦合的肽优化；图 6 展示预测结构条件下的应用。六幅主图已被直接检查，但 HTML 只保留图注，精确数值、方法细节、扩展数据表和补充图尚不能核实。完整依据与限制见 `figure_analysis.md` 和 `doc_code.md`。

### 复现时需要注意

仓库保存了核心代码路径，但未包含四个专家的检查点、数据集、预训练模型和外部折叠软件。README 指向外部 Hugging Face 下载，也要求 EvoEF2、ESMfold/OpenFold 及 flash-attention。因而可以检查设计和接口，不能在当前快照中完成端到端复现。补充 PDF 有链接但未被转换为 `SUPP_MD`，其细节应保持为 `Not found`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## UniAIR

### Overview

UniAIR is a modular multimodal framework for predicting how mutations change adaptive immune recognition. The abstract positions it across antibody maturation, antigen escape, TCR-pHLA optimization and settings with no experimental structure (`paper source:9-16`). Its main release combines a standardized mutation/complex data pipeline, a sequence-structure gate, and a learned consensus over multiple specialist predictors.

### Motivation and Contribution

The paper argues that existing mutation-effect models are often specific to one task or modality and do not transfer cleanly across heterogeneous immune interfaces. UniAIR instead uses a common representation and expert-fusion design. The locally inspected framework figure depicts a shared WT/mutant interface input and parallel expert pathways, while the code loads Gearbind, RDE, PPIformer and ESSM checkpoints and learns a softmax-weighted combination (`figure_analysis.md`; `models/encoders/UniAIR/model.py:34-130`).

### Method at a Glance

The dataset layer parses a CSV row with structures, mutation strings, chain-group labels and targets; it creates mutant amino-acid states and mutation flags (`data/unippi_dataset.py:118-166,195-241`). UniAIR encodes WT and mutant structures with RDE-derived single-residue, residue-pair and geometric-attention components, takes their pooled difference, concatenates that feature with four expert embeddings, and converts learned logits into a temperature-scaled mixture of expert predictions (`models/encoders/UniAIR/model.py:54-130`). Training applies masked weighted MSE or BCE losses and validation/test calculate Pearson, Spearman, RMSE and MAE (`utils/metrics.py:125-165`; `pl_modules/model_module.py:185-222`).

### Evaluation Evidence

Fig. 2 visually contains SKEMPIv2 bars/radar comparisons, independent-test scatter plots and HER2/TCR-pMHC comparisons. Figs. 3-6 show zero-shot mutational distributions, few-shot escape scans, an iterative peptide-optimization loop and predicted-structure evaluation. These support the direction of the paper's claims, but exact numerical results cannot be verified because the acquired publisher HTML omits main-text methods and table values. See `figure_analysis.md` for panel-level evidence.

### Reproducibility Assessment

**Medium fidelity, incomplete runnable release.** The paper-linked GitHub repository is present at commit `e1b48d0` and exposes the core data, model, training and metric paths. However, it lacks the trained expert checkpoints, datasets and folding dependencies; the README points to external Hugging Face downloads and tools. The acquired paper source is valid Nature HTML (61 KB, six figures) but contains only abstract/captions rather than the main body, and supplementary content has not been converted to markdown. Therefore architecture and execution-path claims are code-verified, while full paper equations, ablations and reported values remain `Not found`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
