---
layout: default
permalink: /paper-atlas/openproblemssinglecell-3c49cf3d/
title: "OpenProblemsSingleCell"
nav: false
description: "《Defining and benchmarking open problems in single-cell analysis》是 Nature Biotechnology 的 Correspondence / perspective，而不是提出一个新的预测算法。它总结单细胞分析中仍未解决的任务，并提出 Open Problems 平台作为持续更新的 benchmark 基础设施。"
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
      <span>Machine Learning Algorithm</span>
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>OpenProblemsSingleCell</h1>
    <p>Defining and benchmarking open problems in single-cell analysis</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-025-02694-w" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 单细胞分析中的开放问题：为什么需要“活基准”

### 文章类型与主张

《Defining and benchmarking open problems in single-cell analysis》是 *Nature Biotechnology* 的 Correspondence / perspective，而不是提出一个新的预测算法。它总结单细胞分析中仍未解决的任务，并提出 Open Problems 平台作为持续更新的 benchmark 基础设施。仓库实现可以说明平台如何运行，但不能把本文改写成某个代码模型的 paper–code 对照。

### 为什么静态 benchmark 不够

传统 benchmark 在发表时冻结方法、数据集、指标和软件版本；新方法出现后，旧排名很快过时，不同论文又使用不同数据与指标，难以横向比较。作者主张把任务拆成标准合同：数据生成、方法、控制基线、指标和资源都由可测试组件描述，通过持续集成自动运行并发布结果。

```text
开放科学问题
  ↓ 明确输入、目标与真值
任务合同 ─ 数据集 ─ 方法/控制 ─ 指标
  ↓ 统一容器与工作流执行
跨数据集结果 → 基线归一化 → 排名/不确定性
  ↓
持续加入新方法、新数据和新指标
```

这里的“开放”有两层：科学上尚无满意解法；工程上允许社区持续贡献组件。基准平台本身不能保证任务定义正确，也不能消除 ground truth、数据代表性、指标选择和计算预算造成的偏倚。

### 任务谱系

正文和 61 页补充材料覆盖多类问题，包括降维与可视化、批次整合、细胞类型注释、轨迹/动态、空间与多模态分析、扰动预测、细胞间通信等。每类任务的关键不是统一成一个分数，而是明确预测对象、可用真值、适当负对照和多维评价。

细胞间通信示例说明这一点：方法可能预测 ligand–receptor 对、发送/接收细胞类型或有方向的相互作用；不同输出粒度不能直接混成同一排名。补充材料进一步记录数据集、指标、控制方法与尚缺真值的边界。

### 图怎样读

- **图 1** 对比静态 benchmark 与持续更新平台，强调版本化组件、自动测试和可追溯结果。
- **图 2** 展示开放问题版图，并用 cell–cell communication 说明任务定义、数据、方法与指标必须共同设计。

图中结构是平台理念与任务地图，不是“所有任务已被解决”的证据。源数据表和补充说明用于追踪 benchmark/方法版本；它们反映作者整理时的生态快照。

### 如何解释排名

Open Problems 使用控制方法和基线归一化，使不同数据集上的指标更可比。但综合分数仍依赖权重、缺失结果处理、运行失败和资源限制。一个方法排名靠前不等于在所有生物条件下最可靠；应同时检查数据集分层、各指标、运行稳定性和计算成本。

### 复现与证据边界

本次重新阅读了 349 行正文、两张主图及 61 页补充 Markdown。OpenProblems、历史 v1/v2 快照和论文制图仓库是平台/稿件伴随实现，不是一个需要声称 Exact/Partial 的单一模型代码。文章 DOI 为 `10.1038/s41587-025-02694-w`，2025 年发表。

真正可复现一个 benchmark 需要固定任务版本、数据资源、容器、方法提交、指标与工作流引擎；“living”也意味着当前在线结果可能已不同于论文快照。本文最重要的学习结果不是某个冠军方法，而是把 benchmark 当作版本化、可测试、持续维护的科学对象。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## OpenProblemsSingleCell

### Motivation and Novelty

"Defining and benchmarking open problems in single-cell analysis" presents Open Problems as a living benchmark platform for single-cell analysis. The motivating problem is that single-cell methods evolve faster than static benchmarks: different benchmark papers test different methods, datasets, and metrics, and their results become outdated as new tools appear.

The novelty is a standardized, community-updatable benchmark system. Each analysis challenge is encoded as a task with datasets, methods, metrics, baselines, tests, automated execution, result aggregation, and a public website. The paper reports the platform design and illustrates it through multiple single-cell tasks, with cell-cell communication as the main worked example.

Compared with static resources and benchmarks such as scRNA-tools (PLOS Computational Biology, 2018), single-cell best-practices guidance (Molecular Systems Biology, 2019), batch-correction benchmarks by Tran et al. (Genome Biology, 2020), Mereu et al. (Nature Biotechnology, 2020), BatchBench (Nucleic Acids Research, 2021), and the atlas-scale integration benchmark by Luecken et al. (Nature Methods, 2022), Open Problems makes the benchmark definition and ranking process continuously extensible.

### Method Overview

Open Problems turns a biological analysis task into executable components. Dataset components load data and expose labels, simulated truth, held-out observations, or proxy truth. Method components produce task-specific outputs such as labels, embeddings, graphs, denoised matrices, cell-type proportions, communication-event scores, perturbation responses, or gene rankings. Metric components compute raw scores. Control methods define random-like and optimal-like reference behavior.

The central scoring step is baseline normalization. For each metric, raw method scores are scaled relative to baseline/control methods and then averaged across datasets and metrics to produce an overall ranking. This makes heterogeneous metrics easier to compare, but also makes rankings sensitive to baseline choice and metric weighting.

### Key Results

Figure 1 shows that previous batch-integration benchmarks overlap unevenly in methods and metrics and are tied to static publication timelines. Open Problems addresses this by making benchmark definitions, code, tests, and rankings updateable.

Figure 2 shows the breadth of tasks and analyzes cell-cell communication in detail. The CCC benchmark uses mouse-brain spatial source-target proxy labels and TNBC cytokine ligand-target proxy labels, scored by AUPRC and top-hit odds ratio. Under these labels, magnitude-focused methods, especially CellPhoneDB and LIANA magnitude-rank variants with max aggregation, rank highly. The result supports the benchmark-specific recommendation that magnitude and max aggregation are strong for these CCC subtasks.

The supplement reports additional task-level findings across named datasets and metrics: label projection evaluates pancreas, Tabula Muris Senis lung, CeNGEN, and zebrafish splits with accuracy and weighted/macro F1; dimensionality reduction evaluates PBMC, mouse blood, mouse HSPC, and zebrafish with trustworthiness, distance, density, and neighborhood metrics; denoising uses molecular cross-validation with MSE and Poisson loss; modality matching uses paired CITE-seq and sciCAR with kNN-AUC and MSE; and SVG detection uses scDesign3-based simulation with Kendall correlation. These evaluations show that logistic regression is strong for label projection, densMAP's advantage is partly density-metric driven, graph outputs are easier to score well in batch integration, MAGIC reverse-normalization variants dominate denoising under current metrics, Procrustes is strong but limited for modality matching, and simpler perturbation models outperformed more complex ensembles in the reported competition setting.

### Reproducibility

**Rating: 3/5 for exact paper reproduction; 4/5 for platform auditability.**

The public code strongly supports the platform architecture, task APIs, CI checks, normalization logic, and many task-specific metrics and methods. The v1 and v2 Open Problems snapshots contain the implementations behind much of the supplement, and the manuscript repository contains figure scripts.

Exact paper-number reproduction from a clean clone is less complete. The manuscript scripts expect website result JSON not bundled in the cloned repo, CCC proxy-truth generation scripts for SPOTlight/CytoSig thresholds were not found locally, and the perturbation-prediction task implementation was not found in the cloned snapshots. These are documented gaps rather than hidden failures.

### Practical Takeaway

Open Problems is most useful as transparent benchmark infrastructure. Users should read rankings as task-specific guidance under explicit datasets, metrics, controls, and proxy-truth assumptions. Developers can use the same structure as a contribution path: implement a method component, pass API tests, run the benchmark, and compare against current baselines.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
