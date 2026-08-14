---
layout: default
permalink: /paper-atlas/rxngraphormer-reusability-report-42375f37/
title: "RXNGraphormer_Reusability_Report"
nav: false
wide: true
description: "这不是提出新模型的原始方法论文，而是对 RXNGraphormer 的复现与外部数据可迁移性评估。摘要称该框架把预训练图-Transformer 编码器与 delta-molecular reaction 表示结合，用于反应产率预测和合成规划两个任务；报告重新运行公开实现、检查点和基准数据，并测试高通量实验数据与非 USPTO 序列数据。"
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
      <span>Machine Learning Algorithm</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>RXNGraphormer_Reusability_Report</h1>
    <p>Reusability report: Assessment of reproducibility and applicability to external datasets for RXNGraphormer</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/TheLiaoGroup/RXNGraphormer-Reproduction" target="_blank" rel="noopener noreferrer" aria-label="Open code for RXNGraphormer_Reusability_Report">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## RXNGraphormer 可复用性报告解读

### 这篇文章研究什么？

这不是提出新模型的原始方法论文，而是对 RXNGraphormer 的复现与外部数据可迁移性评估。摘要称该框架把预训练图-Transformer 编码器与 delta-molecular reaction 表示结合，用于反应产率预测和合成规划两个任务；报告重新运行公开实现、检查点和基准数据，并测试高通量实验数据与非 USPTO 序列数据（`paper.md:9-12`）。

### 证据边界

当前 Nature HTML 是订阅预览，只提供摘要、图注、数据/代码可用性和参考文献，没有完整方法、结果表或补充方法（`paper.md:15-89`）。因此，delta-molecular 表示的精确定义、损失函数、训练超参数、数据划分和文章中的精确数值均应标为 **MISSING**，不能从图或摘要反推。

### 可验证的计算流程

```text
parameters.json + checkpoint + 反应数据
             |
  RXNGraphormer.get_model(task_type, config, vocab)
       /              |                    \
  regression      classification       sequence_generation
       |                                      |
  pair/triple 数据集                    词表 + beam search
       |                                      |
  R2 / MAE                         canonical SMILES 的 top-k accuracy
```

代码中的 `get_model` 根据任务类型返回 `RXNGRegressor`、`RXNGClassifier` 或 `RXNG2Sequencer`（`code/repo/rxngraphormer/model.py:1272-1345`）。Transformer 编码器顺序执行多层带残差的注意力/前馈模块（`model.py:71-89`）。回归评估读取 `parameters.json` 和检查点，按 `use_mid_inf`、`specific_val` 选择 pair 或 triple 反应数据集，输出 R² 与 MAE（`code/repo/rxngraphormer/eval.py:93-261`）。序列评估加载词表和检查点，调用 `infer` 做 beam search，再将候选反应 SMILES 规范化并计算累计 top-k accuracy（`eval.py:13-91`）。

### 外部数据与图中结论

文章列出 sulfoxonium-ylide、受阻 meta-C–H 芳基化、酰胺偶联 HTE、文献酰胺偶联和 ORDerly 数据集（`paper.md:80-83`）。图 2 的柱状图、分布图和 top-k 曲线显示复现结果跟随基准结果；图 3 显示不同化学数据集的产率迁移效果差异明显，且 forward prediction 的外部表现优于 retrosynthesis。图像支持“相对模式”而非可复核的精确表格数值。

### 如何理解可复现性

代码仓库公开了预处理、复现、微调、评估和可视化脚本；代码可直接检查任务工厂、检查点加载以及 R²/MAE 和 top-k 的实现。总体证据评级为中等（3/5）：软件入口清楚，但文章正文方法和运行资产仍缺失。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

Reaction-yield prediction and synthesis planning often use different models and reaction representations. This reusability report asks whether RXNGraphormer, a pretrained graph-transformer framework described by Xu et al., can be independently reproduced and transferred to reaction datasets beyond its original setting (`paper source/nature_html/paper.md:9-12`).

### What This Report Adds

Rather than proposing a new architecture, the study re-runs the released implementation, checkpoint and benchmark workflow, then tests reuse on standardized high-throughput reaction-yield datasets and an external sequence-prediction benchmark. The abstract reports consistent reproduction of major regression and sequence-generation results, strong forward prediction outside USPTO, and greater retrosynthetic sensitivity to distribution shift (`paper.md:12`).

### Evaluation

The named external resources include sulfoxonium-ylide HTE, hindered meta-C-H arylation HTE, amide-coupling HTE, a literature-derived amide-coupling benchmark and ORDerly (`paper.md:80-83`). Figure 2 visually shows close benchmark/reproduction distributions and top-k curves. Figure 3 shows dataset-dependent yield transfer, with the strongest visible R² for sulfoxonium and weakest for literature amide coupling, and a clear forward-versus-retrosynthesis gap. Exact sample counts, splits, confidence intervals and table values are unavailable in the accessible article body.

### Reproducibility

The reproduction repository is public and pinned locally to `main` commit `8db818e0b2331e23404a720cb300617b54eca2a0`. The paper links scripts through Zenodo and the repository, and states that no architecture modifications were made (`paper.md:86-89`). The local code directly exposes task construction, checkpoint loading, pair/triple regression evaluation with R²/MAE, and beam-search sequence evaluation with top-k accuracy (`code/repo/rxngraphormer/model.py:1272-1345`; `code/repo/rxngraphormer/eval.py:13-91,93-261`).

Reproducibility rating: **3/5 (moderate)**. Source and code availability are strong, but this workspace could not verify the report's full methods, numerical results, pretrained assets, dataset payloads or runtime outputs. The rating reflects the evidence available here, not a negative judgment about the authors' complete archive.

### Main Caveat

The acquired Nature HTML is subscription-preview content. It contains the abstract, figure captions, availability statements and references but not the methods/results narrative (`paper.md:15-89`). Exact delta-molecular equations, training details and paper-code fidelity therefore remain `MISSING` or `PARTIAL` and are retained as such in the detailed documents.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
