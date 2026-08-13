---
layout: default
permalink: /paper-atlas/dpt-6d12aafe/
title: "DPT"
nav: false
wide: true
description: "Diffusion pseudotime (DPT) 解决的是单细胞快照数据中如何重建发育顺序和分支的问题。输入是细胞 x 基因表达矩阵，输出是以某个 root cell 为起点的 pseudotime、branch labels、未决/decision cells，以及由基因动态支持的生物学解释。"
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
      <span>Nature Methods · 2016</span>
    </div>
    <h1>DPT</h1>
    <p>Diffusion pseudotime robustly reconstructs lineage branching</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/nmeth.3971" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for DPT">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DPT 方法中文解读

### 一句话概览

Diffusion pseudotime (DPT) 解决的是单细胞快照数据中如何重建发育顺序和分支的问题。输入是细胞 x 基因表达矩阵，输出是以某个 root cell 为起点的 pseudotime、branch labels、未决/decision cells，以及由基因动态支持的生物学解释。核心思想是把细胞图上的 diffusion transition matrix 转换成“所有长度随机游走”的距离，而不是只在低维 diffusion map 图上画轨迹。

### 1. 生物学问题与建模目标

单细胞 qPCR 或 scRNA-seq 测量会破坏细胞，因此我们看到的是许多细胞处在不同发育阶段的静态混合，而不是同一个细胞的时间序列。DPT 假设表达相近的细胞在发育流形上相邻，用随机游走刻画细胞状态之间的可达性，再用从 root 到每个细胞的距离作为发育进程。它能支持“哪些细胞更早/更晚”“哪里可能分支”“哪些区域像 metastable states”“哪些基因先后变化”等解释，但不能直接证明真实时间轨迹或因果调控。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| 表达矩阵 | cells x genes, `data`, `Y` | 每个细胞的表达状态 | `doc_method.md`, `doc_code.md` |
| 转移矩阵 | $T$, `T`, `ts@transitions` | 细胞图上的 diffusion/random-walk 转移 | `doc_method.md`, `code/Software/DPT_inMatlab/dpt/transition_matrix.m:1` |
| 稳态分量 | $\psi_0$, `phi0` | 主要反映采样密度的 stationary component | `doc_method.md`, `doc_code.md` |
| 累积转移矩阵 | $M$ | 去掉稳态后所有长度随机游走的闭式和 | `code/Software/DPT_inR/R/propagation_matrix.r:3` |
| DPT 距离 | $dpt(x,y)$ | 两个细胞在 $M$ 中行向量的欧氏距离 | `code/Software/DPT_inR/R/dpt_to_cell.r:9` |
| 分支标签 | `Branch` | terminal branches、uncertain/unassigned cells | `code/Software/DPT_inR/R/organize_branches.r:1` |

### 3. 方法主流程

1. 对 qPCR 或 scRNA-seq 表达矩阵做数据集相关预处理，例如 qPCR 的 LOD/housekeeping normalization，或 inDrop 数据的 library-size normalization 与 scLVM cell-cycle/batch correction。
2. 在细胞之间构建 Gaussian affinity graph。论文给出 classic kernel 和 locally scaled kernel；MATLAB 代码还提供 kNN 版本用于较大数据。
3. 用密度项 $Z(x)$ 对 affinity 做归一化，减少采样密度不均对 pseudotime 排序的影响。
4. 形成 transition matrix $T$，并识别稳态分量 $\psi_0$。
5. 计算 $M=(I-T+\psi_0\psi_0^T)^{-1}-I$，即去掉稳态后的所有长度随机游走累积矩阵。
6. 选定 root cell 后，对每个细胞计算 $dpt(root,x)$，得到 pseudotime 排序。
7. 对分支数据，先找距离最远的 tip cells，再用 tip-rooted DPT orderings 的 Kendall correlation/anticorrelation 找 branch cut。
8. 最后结合 marker gene smoothing、DE、heatmap 和 GO enrichment，把计算结果解释为发育分支、metastable states 和候选调控事件。

### 4. 数学目标与直觉

关键量是累积转移矩阵：

$$
M=(I-(T-\psi_0\psi_0^T))^{-1}-I.
$$

这里 $T$ 表示细胞图上的随机游走，$\psi_0\psi_0^T$ 是稳态/密度分量。减掉它以后再求所有长度随机游走的和，目的是保留从一个细胞到其他细胞的多尺度可达性，而不是被采样密度或固定 diffusion time 控制。

DPT 距离定义为：

$$
dpt(x,y)=\|M(x,\cdot)-M(y,\cdot)\|.
$$

直觉上，每个细胞由“从它出发最终能以多大概率到达其他细胞”的向量表示；两个细胞如果通向各个 fate/state 的随机游走模式相似，就有较小 DPT 距离。分支识别则利用几何性质：在 trunk 上，两个 tip-rooted distances 往往 anticorrelated；进入某个旁支后会变成 correlated。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| Supplementary Software 含 R/MATLAB 实现 | `code/Software/readme.txt:2` | 明确列出 `DPT_inMatlab`、`DPT_inR`、heatmaps、inDrop scLVM | ✓ Exact |
| classic/local/kNN transition matrix | `code/Software/DPT_inMatlab/dpt/transition_matrix.m:1` | 按 `classic`、`loc`、`nn` 路由到不同构图函数 | ✓ Exact |
| R transition object | `code/Software/DPT_inR/R/transitions.r:28` | 调用 `destiny::DiffusionMap`，再保存 transition matrix 和 `phi0` | ~ Partial |
| 累积矩阵 $M$ | `code/Software/DPT_inR/R/propagation_matrix.r:3`; `code/Software/DPT_inMatlab/dpt/dpt_input.m:9` | 直接实现 $(I-T+\phi_0\phi_0^T)^{-1}-I$ | ✓ Exact |
| DPT 距离 | `code/Software/DPT_inR/R/dpt_to_cell.r:9` | 对 $M$ 的行向量做欧氏距离 | ✓ Exact |
| branch tips | `code/Software/DPT_inR/R/find_tips.r:9` | root -> farthest -> farthest -> max distance sum | ✓ Exact |
| finite Kendall branch cut | `code/Software/DPT_inR/R/branchcut.r:34` | 计算 correlation/anticorrelation cut score 并平滑 | ✓ Exact |
| baseline robustness scripts | `doc_code.md` | 未找到 Monocle/Wishbone/Wanderlust bootstrap benchmark 脚本 | ✗ Not found |

### 6. 结果如何解读

Fig. 1 显示 DPT 在 early blood qPCR 数据中恢复两个主要分支，并把 Ikaros、Erg 等 marker gene 放到 pseudotime 动态中。Fig. 1d 的 heatmap 还把高密度区域解释为 precursor、decision、terminal branch states。这里支持的是“DPT 排序与已知 marker biology 一致”，不是因果验证。

Fig. 2 显示 mESC inDrop 数据中 day labels 很粗糙，DPT 能在 day 内部给出更连续的发育顺序，并识别小的 side branches。Fig. 2e/f 支持 DPT 比 Monocle 和 Wanderlust/Wishbone 更稳健、更贴近实验 day labels；但这些 baseline benchmark 的复现脚本没有在本地 Supplementary Software 中找到，所以在代码层面不能算完全验证。

### 7. 局限性与未验证部分

- DPT 是 snapshot manifold distance，不是真实时间，也不是 lineage tracing。
- root cell 选择会决定方向；root 错了，解释也会偏。
- density normalization 帮助排序抵抗采样不均，但 metastable state detection 又依赖 density，因此会受 gating、细胞增殖/死亡和采样设计影响。
- R 代码的 transition construction 依赖 `destiny::DiffusionMap`；论文中的 kernel 公式主要由 MATLAB 代码直接体现。
- 多 root DPT 在 MATLAB 中可验证，R exported API 更偏 single-root。
- 未找到 Monocle/Wishbone/Wanderlust 的 robustness benchmark 脚本，也未找到完整 MARS-seq 复现 pipeline。

### 8. 快速阅读路线

1. `summary.md`：先看方法解决什么问题、结果和复现评分。
2. `doc_method.md`：看完整数学推导和从输入到输出的计算流程。
3. `doc_code.md`：看论文-代码对照、哪些匹配、哪些未找到。
4. `figure_analysis.md`：看 Fig. 1/2 每个 panel 支持什么结论。
5. `claude_notes.md`：看更细的证据 ledger、assumptions、evaluation map 和开放问题。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Diffusion pseudotime robustly reconstructs lineage branching - Summary

**Paper:** Haghverdi, Büttner, Wolf, Buettner & Theis (2016), *Nature Methods*
**DOI:** 10.1038/nmeth.3971
**Method:** Diffusion pseudotime (DPT)
**Code:** Nature Supplementary Software ZIP with R and MATLAB implementations
**Category:** dynamics_fate_trajectory

### Motivation and Novelty

Single-cell expression experiments measure each cell once, so developmental dynamics must be inferred from a population snapshot. Existing pseudotime methods before DPT had two major limitations: they were often fragile to noise and sampling density, and they struggled with branching lineages. Monocle (Trapnell et al., *Nature Biotechnology*, 2014) uses a minimum-spanning tree on a reduced embedding; Wanderlust (Bendall et al., *Cell*, 2014) samples graph paths for mostly nonbranching trajectories; Wishbone (Setty et al., *Nature Biotechnology*, 2016) adds branch detection but depends on waypoint and preprocessing choices.

DPT's novelty is to turn diffusion maps from a visualization tool into a full pseudotime distance. It builds a density-normalized transition matrix on cells, removes the stationary component, sums random walks over all lengths in closed form, and defines pseudotime as distance between accumulated transition-probability profiles. Branches are detected by comparing how DPT orderings from different tip cells switch from anticorrelation on the trunk to correlation on off-branches.

### Method Overview

DPT starts from a normalized cells x genes expression matrix and constructs a Gaussian cell-cell graph. In the locally scaled version, each cell's kernel width is set by its nearest-neighbor distance, making the graph adaptive to dense and sparse regions. The graph is density-normalized to reduce sampling bias, then converted to a diffusion transition matrix $T$.

The method defines

$$
M=(I-(T-\psi_0\psi_0^T))^{-1}-I,
$$

where $\psi_0$ is the stationary component. DPT between cells $x$ and $y$ is

$$
dpt(x,y)=\|M(x,\cdot)-M(y,\cdot)\|.
$$

With a selected root cell, this gives a pseudotime order. For branching, DPT selects tip cells by maximal DPT distances and cuts branches using finite Kendall correlation/anticorrelation between tip-rooted orderings. High-density pseudotime regions are interpreted as candidate metastable or decision states, but this interpretation depends on sampling and cell-state assumptions.

### Evaluation

The main qPCR evaluation uses 3,934 early blood-development cells with 42 genes. DPT recovers two major branches corresponding to blood/erythroid and endothelial-like development, orders marker dynamics such as Ikaros and Erg, and identifies four high-density/metastable regions: precursor, decision, terminal branch 1, and terminal branch 2. Differential expression between DPT-inferred metastable states gives clearer marker separation than comparisons between experimentally sorted populations; the paper reports 32 of 42 genes significant for decision versus precursor states.

The main scRNA-seq evaluation uses the Klein et al. mESC inDrop dataset after LIF withdrawal. After cell-cycle/batch correction, DPT resolves a main differentiation path and small side populations, including a 151-cell apoptosis-related side branch and later primitive-endoderm-like and epiblast-like groups. The paper reports DPT pseudotime correlates better with experimental day than Wanderlust/Wishbone: Kendall correlation 0.77 +/- 1e-3 versus 0.70 +/- 1e-3.

The supplement also analyzes myeloid progenitor MARS-seq data and simulations. Robustness is evaluated by bootstrap self-concordance across artificial, qPCR, mESC, and MARS-seq datasets. Fig. 2e shows DPT generally has higher and tighter robustness distributions than Monocle and Wanderlust/Wishbone. However, the local supplementary software bundle does not include the baseline benchmark scripts, so these robustness claims are paper-level evidence rather than locally code-verified reproduction.

### Reproducibility

**Rating: 3.5 / 5.**

Evidence for reproducibility is substantial but incomplete. The Nature article provides a Supplementary Software ZIP with R and MATLAB DPT implementations, qPCR and inDrop example scripts, heatmap code, and scLVM preprocessing scripts. Core DPT math is directly implemented: MATLAB computes transition matrices and $M$, and both R and MATLAB compute DPT as row distances in $M$ and implement branch cutting.

The main gaps are practical and evaluative. The code is an old source snapshot with no Git commit history; the R implementation depends on `destiny`, and the preprocessing scripts use aged dependencies, hardcoded local paths, and Python 2-era scLVM code. I did not find scripts for Monocle/Wishbone/Wanderlust robustness benchmarks or the full MARS-seq reproduction. Therefore the core method is reproducible in principle, but reproducing all figures and comparisons would require dependency repair and additional scripts or manual reconstruction.

### Scope and Limitations

DPT is best interpreted as a graph-manifold pseudotime and branch detector for snapshot single-cell expression data. It does not observe actual cell histories, prove causal gene regulation, or guarantee correct direction without a meaningful root cell. The density-normalized DPT ordering is designed to resist sampling density effects, but the paper's metastable-state interpretation deliberately uses density and is therefore sensitive to gating, proliferation, death, and sampling design.

The strongest output is a structured hypothesis: which cells lie along a developmental progression, where branches may split, which regions look metastable, and which genes change early or late. Experimental lineage tracing or perturbation is still needed for causal claims.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
