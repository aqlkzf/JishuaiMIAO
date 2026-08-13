---
layout: default
permalink: /paper-atlas/tsvelo-73b9ed7e/
title: "TSvelo"
nav: false
description: "TSvelo 是一个 RNA velocity 方法，用 scRNA-seq 的 unspliced/spliced RNA 层来推断细胞未来状态，但它不只看传统的二维 u-s 相图，而是把 TF 调控、转录和剪接串成一个可解释的 Neural ODE。它的输入是 unspliced/spliced 表达矩阵和 ENCODE/ChEA TF-target 先验，输出包括 pseudotime、RNA velocity、转录率表示 alp…"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>TSvelo</h1>
    <p>TSvelo: Comprehensive RNA velocity by modeling the cascade of gene regulation, transcription and splicing</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1101/2024.12.24.630058" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for TSvelo">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/lijc0804/TSvelo" target="_blank" rel="noopener noreferrer" aria-label="Open code for TSvelo">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TSvelo 方法中文解读

### 一句话概览

TSvelo 是一个 RNA velocity 方法，用 scRNA-seq 的 unspliced/spliced RNA 层来推断细胞未来状态，但它不只看传统的二维 `u-s` 相图，而是把 TF 调控、转录和剪接串成一个可解释的 Neural ODE。它的输入是 unspliced/spliced 表达矩阵和 ENCODE/ChEA TF-target 先验，输出包括 pseudotime、RNA velocity、转录率表示 `alpha`、动力学参数、TF-target 权重和多谱系分支动态。

### 1. 生物学问题与建模目标

RNA velocity 的目标是从单细胞静态测序快照中估计细胞状态变化方向。传统方法主要依赖每个基因的 unspliced-spliced 相图，但单基因信号常常稀疏、噪声高，而且不同细胞类型会混在同一个相图里。TSvelo 的核心假设是：如果把 TF 调控引入转录率，再把转录率、unspliced RNA、spliced RNA 放进同一个 ODE，就能更稳健地拟合基因动态和细胞命运。

需要注意，TSvelo 学到的 TF 权重更适合作为调控假设生成，不是实验层面的因果验证。它依赖 ENCODE/ChEA 先验；先验里没有的边在代码中会被固定为 0。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| unspliced RNA | $U$, `Mu`, `U` | 未成熟 RNA，代表较新的转录信号 | `doc_method.md`, `code/TSvelo/TSvelo_model.py:64-70` |
| spliced RNA | $S$, `Ms`, `S` | 成熟 RNA，代表表达状态 | `doc_method.md`, `code/TSvelo/TSvelo_model.py:64-70` |
| 转录率 | $\alpha_g(t)`, `alpha` | TF 调控生成的转录信号 | `code/TSvelo/TSvelo_model.py:117` |
| 剪接/降解率 | $\beta_g$, $\gamma_g` | unspliced 到 spliced、spliced 降解 | `code/TSvelo/TSvelo_model.py:107-118` |
| TF 权重 | $W$, $W'`, `W`, `W_0_mask` | 稀疏 TF-target 调控权重 | `code/TSvelo/TSvelo_model.py:40-62` |
| 时间 | $t_c`, `t_steps`, `t` | 每个细胞的潜在时间位置 | `code/TSvelo/TSvelo_model.py:84-95` |
| velocity | $v_c`, `adata.layers['velocity']` | 细胞未来状态方向 | `code/TSvelo/TSvelo_utils.py:10-20` |

### 3. 方法主流程

1. 读取 scRNA-seq 数据，保留 unspliced 和 spliced 层。
2. 用 scVelo 风格做过滤、归一化、log transform、KNN smoothing 和 moments。
3. 对每个基因构建 `u-s` 相图邻接图，并与全局细胞邻接图比较，选择相图结构更可靠的 velocity genes。
4. 从 ENCODE/ChEA 读取 TF-target 先验，构建稀疏调控 mask。
5. 用 Leiden/PAGA/DPT 和 U-to-S delay 初始化谱系方向与 pseudotime。
6. 用 TF 表达计算转录率 $\alpha_g(t)$，再用 ODE 描述转录到 unspliced、spliced 的动态。
7. 用 EM 优化：M-step 训练 Neural ODE 参数，E-step 把每个细胞重新分配到最接近的 ODE 时间点。
8. 从拟合后的 ODE 计算 RNA velocity，并用 scVelo 生成 velocity graph/stream。
9. 多谱系数据中，先分支拟合，再把分支结果加权合并。

### 4. 数学目标与直觉

核心动力学是：

$$
\frac{d u_g(t)}{dt} = \alpha_g(t) - \beta_g u_g(t)
$$

$$
\frac{d s_g(t)}{dt} = \beta_g u_g(t) - \gamma_g s_g(t)
$$

第一式表示转录产生 unspliced RNA，剪接消耗 unspliced RNA。第二式表示剪接产生 spliced RNA，降解消耗 spliced RNA。

TSvelo 的关键扩展是：

$$
\alpha_g(t)=ReLU\left(\sum_{i\in TFs(g)} w_{gi}s_i(t)\right)
$$

也就是说，目标基因的转录率由 TF 的 spliced 表达和 TF-target 权重决定。代码可验证的是 `alpha = ReLU(W_masked @ s + W_bias)`，所以实现里多了论文公式没有写出的 `W_bias`。

优化目标是让 ODE 预测的 $\widehat U,\widehat S,\widehat S'$ 尽量接近观测的 $U,S,S'$。E-step 在 0 到 999 的时间网格中为每个细胞找最近时间点；M-step 用 Adam 更新 ODE 参数。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| scVelo 预处理 | `code/TSvelo/TSvelo_pp.py:53-83` | filter/normalize、moments、neighbors/UMAP | ✓ Exact |
| velocity gene selection | `code/TSvelo/TSvelo_pp_utils.py:157-212` | 比较 gene-specific `u-s` graph 与全局 graph | ~ Partial |
| TF 先验 | `code/TSvelo/TSvelo_pp_utils.py:23-153` | 读取 ENCODE/ChEA 并计算 TF-target correlation | ~ Partial |
| ODE RHS | `code/TSvelo/TSvelo_model.py:103-124` | 实现 `du_dt`, `ds_dt`, ReLU 参数约束 | ~ Partial |
| EM 训练 | `code/TSvelo/TSvelo_model.py:127-214`, `233-265` | Neural ODE 训练和时间点重分配 | ✓ Exact |
| velocity 输出 | `code/TSvelo/TSvelo_utils.py:10-40` | 写入 velocity layer 并调用 scVelo | ✓ Exact |
| 多谱系合并 | `code/TSvelo/TSvelo_concate.py:27-123` | branch-size 加权合并，但有额外 downweight | ~ Partial |

### 6. 结果如何解读

Fig. 1 展示整体框架。Fig. 2 的 pancreas 结果支持 3D `alpha-u-s` 相图比传统 2D `u-s` 相图更能分离细胞状态。Fig. 3 的 gastrulation erythroid 结果展示 velocity consistency、in-cluster coherence、cross-boundary direction correctness，并给出 KLF1 及其 targets 的模型权重和时间延迟。Fig. 4 用 mouse brain 数据与 MultiVelo 做可视化对比。Fig. 5 和 Fig. 6 主要说明 TSvelo 可以处理 dentate gyrus 和 LARRY 这类多谱系数据，并给出谱系特异基因动态。

这些图支持 TSvelo 在多个数据集上产生生物学合理的 pseudotime、velocity stream 和 gene dynamics。但其中一些强评价依赖 supplementary figures/tables；

### 7. 局限性与未验证部分

- 代码中没有找到 CBDir、ICCoh 和 2D-vs-3D kNN accuracy 的直接实现；核心代码只实现了 scVelo 的 velocity consistency。
- `alpha` 的代码实现有 `W_bias`，论文公式没有写出这一项。
- 论文写成显式 block matrix $A$，代码是直接写 ODE RHS，不显式构造完整矩阵。
- 多谱系 merge 代码有早期时间点 downweighting，论文 Eq. 17 没有说明。
- TF 权重是 prior-constrained model weight，更适合生成调控假设，不应解读为实验验证的因果关系。

### 8. 快速阅读路线

1. `summary.md`：快速了解动机、结果和复现评分。
2. `doc_method.md`：系统读方法、公式和计算流程。
3. `doc_code.md`：看论文步骤和源码是否匹配，尤其是 partial/missing 项。
4. `figure_analysis.md`：逐图理解每个 panel 支持什么结论。
5. `claude_notes.md`：查详细证据、公式表、claim 表和源码行号。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TSvelo

### Motivation and Novelty

TSvelo addresses a central weakness of RNA velocity: many methods infer cell fate from gene-wise unspliced-spliced phase portraits, but those portraits are sparse, noisy, short-timescale, and often mix multiple cell types. The paper argues that splicing dynamics alone are insufficient for robust gene-level modeling and downstream trajectory interpretation.

The novelty is a high-dimensional, interpretable Neural ODE that models a cascade of gene regulation, transcription, and splicing. Instead of estimating each gene independently, TSvelo uses ENCODE/ChEA TF-target priors to build a sparse regulatory layer, learns transcription-rate representations, and fits selected velocity genes under a unified latent time. The method is also designed for multilineage data by segmenting lineages, fitting them independently, and merging branch-specific outputs.

### Method Overview

TSvelo takes scRNA-seq unspliced and spliced RNA layers as input. It first applies scVelo-style preprocessing, including highly variable gene selection, normalization, log transformation, nearest-neighbor smoothing, and moments. It then selects velocity genes by comparing global cell-neighborhood structure with gene-specific unspliced-spliced phase portraits.

The model uses TF-target priors from ENCODE and ChEA. For a target gene, transcription rate is modeled as a ReLU-transformed weighted sum of TF spliced expression. This transcription signal feeds an ODE for unspliced and spliced RNA, with learned splicing and degradation rates. The implementation uses `torchdiffeq` and an EM loop: the M-step trains ODE parameters, while the E-step reassigns each cell to the closest predicted time step.

For multilineage datasets, TSvelo runs lineage detection with Leiden/PAGA/DPT plus U-to-S delay orientation. It fits branches separately and merges branch outputs into a final AnnData object.

### Evaluation

The paper evaluates TSvelo on six scRNA-seq datasets:

| Dataset | Main use | Evidence |
|---|---|---|
| Pancreas | single-lineage endocrine differentiation | pseudotime, velocity stream, 3D phase portrait separability, gene fits |
| Gastrulation erythroid | blood progenitor to erythroid differentiation | GO enrichment, VCon/ICCoh/CBDir metrics, TF-weight analysis |
| 10x mouse brain | comparison with MultiVelo processed multi-omics data | qualitative stream and gene-dynamics comparison |
| Dentate gyrus | three-lineage neural differentiation | GO terms, TSvelo/scVelo/cellDancer stream comparison, lineage-specific gene patterns |
| LARRY | large multilineage hematopoiesis | lineage detection, pseudotime, neutrophil GO terms, gene trajectories |
| Pons | supplementary dataset | mentioned in text; supplementary figure not available in workspace |

Baselines include Velocyto (Nature, 2018), scVelo (Nature Biotechnology, 2020), UniTVelo (Nature Communications, 2022), Dynamo (Cell, 2022), cellDancer (Nature Biotechnology, 2023), DeepVelo (Genome Biology, 2024), LatentVelo (Nature Computational Science, 2023), MultiVelo (Nature Biotechnology, 2023), TFvelo (Nature Communications, 2024), PHOENIX (Genome Biology, 2024), scKINETICS (Bioinformatics, 2023), scPN (Briefings in Bioinformatics, 2025), VeloVI (Nature Methods, 2024), Pyrovelocity (preprint, 2022), and BayVel (preprint, 2025).

The strongest main-figure quantitative evidence is in the gastrulation erythroid benchmark, where TSvelo is shown with high velocity consistency, in-cluster coherence, and cross-boundary direction correctness. The pancreas figure supports the 3D `alpha-u-s` representation through kNN separability. The multilineage figures emphasize biological plausibility and gene-level interpretability rather than full benchmark statistics.

### Code Match and Reproducibility

Public code is available at `https://github.com/lijc0804/TSvelo` and was cloned at commit `9981478885e1ab7e655ede5c0c4664ab9bb3d516`. The code implements the core TSvelo pipeline: preprocessing, TF-prior loading, velocity-gene selection, lineages, Neural ODE fitting, velocity writeback, and multilineage merging.

The match is medium. Major paper claims are implemented, but there are important differences:

- The transcription-rate equation includes a code-only learned `W_bias`.
- The paper's explicit block matrix is implemented as an ODE RHS rather than a literal matrix.
- Extra TFs are handled as retained nonselected genes rather than a separately named `S'` block.
- Velocity-gene selection includes extra TF/non-sparsity filters.
- Multilineage merging includes an extra early-time downweighting rule.
- CBDir/ICCoh and 2D-vs-3D kNN evaluation scripts were not found in the acquired core source.
- Supplementary figures/tables and runtime/memory analyses were not acquired.

### Reproducibility Rating

**Rating: 3 / 5.**

The repository contains a runnable-looking Python implementation with clear entry point, dependencies, demo script, and core method modules. It also provides ChEA and ENCODE resources, though ENCODE must be unzipped before use. The main modeling pipeline is substantially verifiable from source. Reproducibility is limited by missing supplementary material, unavailable benchmark scripts for several reported metrics, reliance on external datasets, and code-paper deviations that affect exact reimplementation of the paper equations.

### Recommended Reading Order

1. `doc_method.md` for the method and math.
2. `doc_code.md` for exact code-paper matches and mismatches.
3. `figure_analysis.md` for panel-level evidence.
4. `Chinese method notes` for a compact Chinese explanation.
5. `claude_notes.md` for detailed evidence ledgers and source line ranges.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
