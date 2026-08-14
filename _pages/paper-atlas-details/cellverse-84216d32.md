---
layout: default
permalink: /paper-atlas/cellverse-84216d32/
title: "CellVerse"
nav: false
wide: true
description: "单细胞数据通常按测序模态和下游任务分别建模：scRNA-seq、CITE-seq、ASAP-seq、scATAC-seq 需要不同的预处理与模型；使用者还需要生物学和编程经验；许多模型直接把表达矩阵映射成标签，难以解释决策过程。论文以 scGPT（Nature Methods, 2024）和 Large-scale foundation model on single-cell transcriptomics（Nature Method…"
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
      <span>arXiv · 2025</span>
    </div>
    <h1>CellVerse</h1>
    <p>CellVerse : Do Large Language Models Really Understand Cell Biology?</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2505.07865" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CellVerse">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellVerse 方法中文解读

### 1. 论文要解决什么问题？

单细胞数据通常按测序模态和下游任务分别建模：scRNA-seq、CITE-seq、ASAP-seq、scATAC-seq 需要不同的预处理与模型；使用者还需要生物学和编程经验；许多模型直接把表达矩阵映射成标签，难以解释决策过程。论文以 scGPT（*Nature Methods*, 2024）和 Large-scale foundation model on single-cell transcriptomics（*Nature Methods*, 2024）等基础模型工作为背景，提出用自然语言统一数据入口，再测试大型语言模型（LLM）是否真的能处理细胞生物学问题。这里的“统一”首先是 QA 接口统一，不是把所有模态变成同一个数值模型。

### 2. CellVerse 是什么？

CellVerse 是一个语言中心的单细胞 QA 基准，而不是一个新训练的单细胞模型。它整合四类单细胞多组学数据和五个子数据集，覆盖三个层级：

| 层级 | 任务 | 数据/标签 |
|---|---|---|
| 细胞级 | 细胞类型注释（CTA） | MS scRNA-seq（3,000；18 类）、PBMC CITE-seq（17,441 genes；7 类）、PBMC ASAP-seq（17,441 genes；9 类） |
| 药物级 | 药物反应预测（DRP） | erlotinib scRNA-seq（18,380 genes；sensitive/resistant） |
| 基因级 | 扰动显著性（PSA）和扰动方向（PDA） | K562 scATAC-seq（5,060 genes；Yes/No 或 Up/Down） |

上述数据规模和标签来自论文第 3.3 节（`paper.md`，第 124-132 行）。图 3 将 PSA、PDA 分成两个评测面板，因此实验中可看到六个排行榜。

### 3. 两种语言化表示

#### 3.1 Cell2sentence（C2S）

给定单细胞矩阵 $X\in\mathbb{R}^{N\times G}$，对细胞 $x_i$ 的归一化特征按表达量排序，只保留前 $n$ 个基因名：

$$
\text{Cell Sentence}_{i}=\texttt{[}g_{i}^{(1)},g_{i}^{(2)},\dots,g_{i}^{(n)}\texttt{]}.
$$

其中 $g_i^{(j)}$ 是第 $j$ 个高表达基因（论文 Eq. 1，`paper.md` 第 74-84 行）。LLM 接收到的是基因名及其顺序，而不是完整表达数值。$n$ 也控制上下文长度；图 5 展示了 100、200、300、400 个基因的比较。

#### 3.2 基因调控网络（GRN）语言化

将基因看作有向图节点，把边 $(g^a,g^b)$ 的权重 $w_{ab}$ 转成扰动叙述：

$$
(g^{a},g^{b},w_{ab})\in\mathcal{E}^{\prime}
\Rightarrow
\begin{cases}
\delta(g^{a})\rightarrow\text{Change}(g^{b}),&w_{ab}\geq\tau,\\
\delta(g^{a})\nrightarrow\text{Change}(g^{b}),&w_{ab}<\tau.
\end{cases}
$$

这里 $\delta$ 是扰动操作，$\tau$ 是阈值（论文 Eq. 2，`paper.md` 第 87-97 行）。在数据整理的具体描述中，作者对扰动组和对照组做非参数 Wilcoxon 检验，并要求 $p<0.05$ 且 log~2~FC 超过 0.5；两组都要有超过 10 个细胞，每个源基因最多保留三个 QA 例子（第 118-121 行）。论文没有明确说明 $w_{ab},\tau$ 与 Wilcoxon/log~2~FC 规则的逐项对应，也没有说明负向变化的精确方向判定，因此这部分应视为“概念表示 + 部分给出的标注规则”。

### 4. 从数据到答案的流程

```text
原始单细胞数据
  ├─ CTA / DRP: 归一化 -> 基因降序排列 -> C2S 基因列表
  │              -> 相似度去冗余 -> 重采样平衡类别
  └─ PSA / PDA: 扰动-对照基因对 -> Wilcoxon + log2FC 筛选
                 -> >10 cells/group，源基因最多 3 个例子
                         |
                         v
       任务问题 + 候选答案 + 细胞生物学专家 system prompt
                         |
              zero-shot / few-shot LLM 推理
                         |
         解析 Final Answer -> precision/recall/F1/accuracy
```

CTA 的问题要求从候选细胞类型中选一个；DRP 要在 Resistant/Sensitive 中选择；PSA 要回答 Yes/No；PDA 要回答 Up/Down。附录表 6 给出完整模板（`paper.md` 第 385-407 行）。作者解释，开放式答案容易产生不可靠输出，所以所有评测采用封闭选项。

### 5. 评测了什么？

论文比较 9 个开源模型和 5 个闭源模型：C2S-Pythia 系列是唯一被归为单细胞专用的 specialist，其余包括 Qwen、Llama、DeepSeek 和 GPT 系列，被视为 generalist。开源模型用 vLLM 推理，闭源模型用官方 API；实验包含 zero-shot、few-shot，以及 CTA 上的上下文长度实验（`paper.md` 第 143-146 行）。指标为 precision、recall、F1 和 accuracy。

主要最高准确率为：

- CTA：scRNA-seq 42.38%，CITE-seq 61.43%，ASAP-seq 29.33%。
- DRP：55.00%。这是二分类任务，论文认为没有明显超过随机猜测。
- PSA：76.67%。但表 3 中部分模型的 `Yes` recall 为 0，说明类别比例或“全部回答 No”会显著影响 accuracy。
- PDA：62.96%，总体比显著性判断更不稳定。

图 6-8 的 scRNA-seq 细分类结果显示 oligodendrocyte C 和 phagocyte 几乎没有模型能正确识别；图 11 的 few-shot 曲线不单调，增加示例并不保证提升；图 12-13 的错误饼图显示误分类与推理错误占主导，PDA 的 factual error 比 CTA 更明显。

### 6. 如何理解论文结论？

论文支持的结论是：在这种特定的语言编码和 prompt 协议下，大型 generalist 的表现通常优于 C2S-Pythia specialist，但整体能力仍然有限。它没有证明 LLM 已经“理解”了细胞生物学，也没有隔离参数量、训练数据、模型架构和提示词等因素，因此“模型规模越大越好”更接近跨模型族的观察趋势，而不是严格的因果缩放定律。上下文变长或 few-shot 变差可能与噪声有关，但论文只提出了这一假设。

### 7. 复现边界与已知缺口

论文也没有给出可直接运行的 benchmark 文件或 split manifest。以下细节在已搜索的正文、附录、图注和本地图片中仍未找到：归一化和默认 $n$、句子相似度函数/阈值、重采样算法、GRN 来源与候选基因对生成、多重检验校正、PDA 的负向变化规则、模型快照与解码参数、few-shot 样本选择、随机种子、重复运行方差以及与随机猜测比较的显著性检验。

因此，CellVerse 适合被理解为一个重要的比较性基准和问题定义，而不是已经完全可复现的单细胞 LLM 分析系统。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellVerse

### Problem

Single-cell analyses are usually tied to a modality- and task-specific workflow, require substantial biology/programming expertise, and often expose only black-box mappings from measurements to labels. CellVerse asks whether large language models can provide a common, more user-facing interface by converting single-cell evidence into natural-language questions (`paper.md`, lines 14-39).

### What is introduced

CellVerse is a language-centric benchmark assembled from five sub-datasets spanning scRNA-seq, CITE-seq, ASAP-seq, and scATAC-seq. It covers cell type annotation (cell level), erlotinib drug-response prediction (drug level), and perturbation analysis (gene level), with the last split into significance and direction questions (`paper.md`, lines 25-31, 100-132). Cell profiles become descending ranked gene-name lists through cell2sentence (C2S); perturbation relations are represented with gene-regulatory-network language and statistical labels. Redundancy filtering and class-balancing resampling are applied to the C2S tasks.

### How the benchmark is evaluated

Each task is presented as a closed-set prompt with a common cell-biology/genomics system instruction. The authors evaluate nine open-source and five closed-source LLMs in zero-shot and few-shot settings, plus a CTA context-length study. Metrics are precision, recall, F1, and accuracy (`paper.md`, lines 143-146, 385-407). The paper reports six leaderboard panels and detailed tables for CTA across three modalities, DRP, PSA, and PDA.

### Main results

- Best CTA accuracies are 42.38% (scRNA-seq), 61.43% (CITE-seq), and 29.33% (ASAP-seq).
- Best DRP accuracy is 55.00%, which the authors describe as not materially above random guessing.
- Best PSA accuracy is 76.67%, but several models achieve that score while recalling no positive `Yes` examples, so class-wise metrics are essential.
- Best PDA accuracy is 62.96%; direction prediction is generally weaker and less stable than significance classification.
- C2S-Pythia specialist models are reported at zero on the leaderboard, while larger generalist families perform better. Context length and few-shot examples produce non-monotonic changes rather than universal gains (`paper.md`, lines 234-275).

The classwise figures show severe CTA heterogeneity: oligodendrocyte C and phagocyte have no visible correct-prediction bars in the scRNA panels, while some common immune/glial classes are much easier. GPT-4.1 and GPT-4o error pies attribute most errors to misclassification or reasoning; factual errors become more visible for gene-level tasks.

### Reproducibility and limitations

The paper supplies the benchmark concept, two formal representations (Eq. 1 C2S and Eq. 2 GRN relation), source dataset dimensions, model-source links, prompt templates, metric tables, and local result figures. It does **not** provide an implementation repository in this workspace: code is `MISSING / Not found` after paper code/data searches and GitHub URL scans (`github_links.json`, `acquisition_manifest.json`). Benchmark files, split manifests, normalization and top-$n$ defaults, similarity thresholds, resampling rules, GRN construction, candidate-pair sampling, multiple-testing treatment, direction-label logic, model snapshots, decoding parameters, few-shot selection, seeds, repeated-run variance, and statistical tests against chance are also Not found in the acquired paper.

The benchmark therefore supports a useful comparative snapshot of LLM behavior under one language encoding and prompt protocol, but it does not by itself establish faithful biological reasoning, a causal model-size law, or a fully reproducible pipeline. The paper also acknowledges missing quantitative difficulty levels and English-only prompts as future-work limitations (`paper.md`, lines 477-486).

**Reproducibility rating: 2/5.** The paper is detailed enough to understand the design and inspect reported results, but unavailable implementation/data and underspecified preprocessing/evaluation choices prevent a clean independent rerun.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
