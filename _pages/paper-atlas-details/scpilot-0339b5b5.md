---
layout: default
permalink: /paper-atlas/scpilot-0339b5b5/
title: "scPilot"
nav: false
wide: true
description: "单细胞分析通常需要人工在 Scanpy、Monocle、SCENIC 等工具之间切换，并凭经验选择参数。普通 LLM 工具代理虽然可以写代码和调用工具，却经常只返回结果，隐藏中间数据和生物学依据。scPilot 提出“组学原生推理”（omics-native reasoning, ONR）：模型直接读取由单细胞表达矩阵压缩出的证据，提出假设，调用针对性的生物信息学操作，解释数值结果，再根据新证据修正结论。"
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
      <span>Representation Models</span>
      <span>NeurIPS · 2025</span>
    </div>
    <h1>scPilot</h1>
    <p>scPilot: Large language model reasoning toward automated single-cell analysis and discovery</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2602.11609" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scPilot">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/maitrix-org/scPilot" target="_blank" rel="noopener noreferrer" aria-label="Open code for scPilot">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scPilot 方法中文解读

### 它要解决什么问题

单细胞分析通常需要人工在 Scanpy、Monocle、SCENIC 等工具之间切换，并凭经验选择参数。普通 LLM 工具代理虽然可以写代码和调用工具，却经常只返回结果，隐藏中间数据和生物学依据。scPilot 提出“组学原生推理”（omics-native reasoning, ONR）：模型直接读取由单细胞表达矩阵压缩出的证据，提出假设，调用针对性的生物信息学操作，解释数值结果，再根据新证据修正结论（`paper.md:14-39,103-129`）。

### 核心方法

给定表达矩阵 $\mathbf{X}\in\mathbb{R}^{G\times N}$ 和问题 $\boldsymbol{q}$，先用算法映射 $\boldsymbol{\Phi}_q$ 生成可放入上下文窗口的语义摘要。每一步推理输出自然语言主张 $c_k$ 和一个原子操作 $o_k$：

$$S_k=o_k(S_{k-1}),\qquad \mathcal{R}=[(c_1,o_1),\ldots,(c_K,o_K)].$$

最终从 $S_K$ 得到预测，并保留完整的“主张 + 证据”轨迹。系统的三个模块是问题到文本转换器、标准生物工具库和 LLM planner（`paper.md:114-131`）。设计重点是先提供组织/物种等生物背景、迭代反思、尽量少用任务专属手工规则。

### 三类任务流程

#### 1. 细胞类型注释

```text
AnnData/表达矩阵
  -> Scanpy Leiden + 差异基因
  -> LLM 提出候选细胞类型和 marker
  -> 只保留数据中存在的 marker，生成 dotplot
  -> LLM 读取表达证据并输出 cluster-label
  -> 保存标签/UMAP，针对失败 cluster 再迭代
```

仓库中的 `Task1_scPilot.py:40-192` 实现了这个肝脏示例。第一次假设使用每个 cluster 的 5 个基因，后续使用 3 个；实验 agent 初始提出 10--30 种细胞类型，后续只为未解决 cluster 提出 3--5 个 marker。环境 agent 通过 Scanpy dotplot 检查 marker 是否真的存在，evaluation agent 再把表达摘要交给 LLM。`Task1_scoring.py:300-355` 用 Cell Ontology 的祖先/后代关系计算 1（完全）、0.5（部分）、0（错误）的协议感知分数。

#### 2. 发育轨迹

论文中先注释 cluster，再让 LLM 分步寻找根节点、添加叶节点、合成树；随后把 py-Monocle 的连通性和 pseudotime 报告交给模型自检，修正根、时间逆序边和 terminal state，最后做一致性合成（`paper.md:872-890`）。指标为节点 Jaccard、GED-nx 和 spectral distance。当前 GitHub 快照的具体流程在 `Traj_scPilot_1.ipynb` 到 `Traj_scPilot_3.ipynb`，Python 目录中只有 `utils/traj_util.py:1-53` 的树结构校验器，因此不能把后者误认为完整轨迹推断实现。

#### 3. GRN/TF-基因关系

```text
GRNdb + TRRUST
  -> 构造跨组织 held-out TF-gene 任务
  -> 查询 TF/基因在两个组织中的上下文
  -> 加入共享 GO biological-process 词条和 few-shot 示例
  -> LLM 输出理由及 0--1 的可能性
  -> 0.5 阈值后二分类，计算 AUROC 等指标
```

`Task3_combined.py:193-264,476-586` 直接体现了任务构造、GO overlap、正则表达式解析和 JSONL reasoning log。它与论文所说的“用功能重叠帮助推理”一致，但不是一个统一的 SCENIC JSON 工具调用框架。

### 实验结论

scBench 包含 PBMC3k、Liver、Retina 的注释，Pancreas、Liver、Neocortex 的轨迹，以及 Stomach、Liver、Kidney 的 GRN。论文报告 scPilot 在 24 个模型-数据组合中有 19 个提升；o1 的 PBMC3k 注释为 0.792、Retina 为 0.728，o1 的 GRN AUROC 为 Stomach 0.873、Liver 0.760、Kidney 0.797（`paper.md:199-254,257-294`）。去掉组织等上下文、打乱 GO 注释或破坏 Monocle 报告都会降低性能，说明模型依赖输入证据质量（`paper.md:306-324,664-720`）。

### 复现边界

代码仓库已固定在 commit `402b64ee029bd7bfb2d8b3d6296ec25d3e374a4f`。注释循环和 GRN 脚本可读，但 API key、模型、数据集、py-Monocle 输出及完整 benchmark 调度没有随仓库提供；轨迹实现主要是 notebook。因此本分析的代码-论文一致性为中等，复现等级为“部分可复现”。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scPilot Summary

### Problem

Single-cell analysis still depends on fragmented tools and analyst heuristics. Tool-using LLM agents can call Scanpy/Monocle/SCENIC, but often hide intermediate data and biological rationale. scPilot proposes *omics-native reasoning* (ONR): an LLM reads compact summaries grounded in raw expression data, states hypotheses, requests targeted operations, interprets numerical evidence, and revises conclusions (`paper.md:14-39,103-129`).

### What It Introduces

scPilot combines a problem-to-text converter, an LLM planner, and a bio-tool library for three workflows: cell-type annotation, developmental trajectory reconstruction, and TF-gene/GRN prediction. scBench supplies nine curated datasets and task-specific ground truth/metrics (`paper.md:132-167`). The intended output is both a prediction and a verbal/computational reasoning trace.

### Main Results

Across eight LLMs and three datasets per task, the paper reports:

- Annotation: scPilot improves 19 of 24 model-dataset combinations; o1 reaches 0.792 on PBMC3k and 0.728 on Retina, while Gemini-2.0-Pro reaches 0.792 and 0.763 respectively (`paper.md:199-209,257-269`).
- Trajectory: Gemini-2.5-Pro scPilot reports GED-nx 3.33 and spectral distance 0.199 in the summary comparison, versus 8.33 and 0.482 for Biomni and 20 and 0.469 for py-Monocle (`paper.md:260-275`).
- GRN: o1 reaches AUROC 0.873/0.760/0.797 on Stomach/Liver/Kidney, and the Stomach comparison is 0.873 for scPilot versus 0.827 direct, 0.727 LLM4GRN, and 0.660 BioGPT (`paper.md:243-254,278-294`).
- Ablations: removing PBMC metadata drops o1 accuracy by 0.104; randomizing GO information reduces o1 Stomach AUROC from 0.873 to 0.813; corrupting Monocle reports worsens Jaccard, GED, and spectral distance (`paper.md:306-324,664-694,697-720`).

### Reproducibility

The linked MIT GitHub repository is cloned locally at `scPilot/` (commit `402b64ee029bd7bfb2d8b3d6296ec25d3e374a4f`). The annotation loop and GRN prompt/evaluation scripts are inspectable, but trajectory execution is notebook-based and the repository lacks benchmark data, model credentials, and a single end-to-end runner. Code-paper fidelity is therefore **medium / partial**. The five local figures were read directly; the converter reported four unavailable remote image references, which are recorded in the workspace evidence.

### Limitations

The study depends on proprietary API models for its strongest results, uses prompt parsing rather than a formally typed tool protocol in the available code, and reports model/dataset averages without making every preprocessing and stochastic sampling detail executable from the snapshot. The authors' own examples show failures when GO overlap is misleading or literature/domain knowledge is missing (`paper.md:818-840`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
