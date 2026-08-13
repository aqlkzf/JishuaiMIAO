---
layout: default
permalink: /paper-atlas/scot-64da306e/
title: "SCOT"
nav: false
wide: true
description: "当 RNA、染色质可及性或 DNA 甲基化分别测在不同细胞上时，两张数据矩阵既没有逐细胞对应，也可能没有可直接比较的特征。SCOT（Single-Cell alignment using Optimal Transport）不尝试比较“某个基因”和“某个 ATAC peak”的数值，而是假设同一细胞群在不同模态中保留相似的细胞—细胞几何结构：若两个 RNA 细胞在本模态流形上相近，它们对应的 ATAC 细胞也应在 ATAC 流形上相近。"
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
      <span>Journal of Computational Biology · 2022</span>
    </div>
    <h1>SCOT</h1>
    <p>SCOT: Single-Cell Multi-Omics Alignment with Optimal Transport</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1089/cmb.2021.0446" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SCOT">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/rsinghlab/SCOT" target="_blank" rel="noopener noreferrer" aria-label="Open code for SCOT">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SCOT 方法解读：不依赖共享特征的单细胞多组学对齐

### 1. SCOT 解决的核心困难

当 RNA、染色质可及性或 DNA 甲基化分别测在不同细胞上时，两张数据矩阵既没有逐细胞对应，也可能没有可直接比较的特征。SCOT（Single-Cell alignment using Optimal Transport）不尝试比较“某个基因”和“某个 ATAC peak”的数值，而是假设同一细胞群在不同模态中保留相似的细胞—细胞几何结构：若两个 RNA 细胞在本模态流形上相近，它们对应的 ATAC 细胞也应在 ATAC 流形上相近。

方法先分别把两个模态变成细胞图距离矩阵，再用 Gromov–Wasserstein（GW）最优传输寻找能最大程度保存两边内部距离关系的概率耦合，最后用重心投影把一个模态映射到另一个模态的特征空间。

### 2. 从原始矩阵到模态内几何

设两个输入分别为 $X\in\mathbb R^{n_x\times p_x}$ 与 $Y\in\mathbb R^{n_y\times p_y}$。行是细胞，列可完全不同。`scotv1.py` 默认对每个细胞做 L2 归一化；也支持 L1、max 或 z-score。归一化会直接影响近邻，因此使用已经预处理的潜在表示时，应显式决定是否关闭 SCOT 内部归一化。

随后在每个模态内独立构造 $k$ 近邻图。论文和 v1 默认使用 correlation metric 与二值 connectivity 图。代码在 connectivity 模式设置 `include_self=True`，所以图结构的实际细节还包含自环。再用无向 Dijkstra 最短路将局部近邻连接扩展成任意细胞对之间的图测地距离：

$$
C^x_{ii'}=d_{G_x}(x_i,x_{i'}),\qquad
C^y_{jj'}=d_{G_y}(y_j,y_{j'}).
$$

若图不连通，代码把无穷距离截断为该图的最大有限距离，然后把整个距离矩阵除以其最大值。这是工程启发式：它让 GW 可计算，但不能恢复断开分量之间真实的相对距离。$k$ 太小会产生大量断开点，太大又会把图变得接近完全图、抹平局部几何。

### 3. GW 耦合比较的是“关系的关系”

默认边缘分布在两边细胞上均匀：$p_i=1/n_x$、$q_j=1/n_y$。SCOT 求非负耦合 $\Gamma$，满足 $\Gamma\mathbf1=p$、$\Gamma^\top\mathbf1=q$，并最小化平方损失的 GW 目标：

$$
\operatorname{GW}(C^x,C^y,p,q)=
\min_{\Gamma}
\sum_{ii'jj'}
\left(C^x_{ii'}-C^y_{jj'}\right)^2
\Gamma_{ij}\Gamma_{i'j'}.
$$

若 $x_i$ 与 $x_{i'}$ 在 RNA 图上接近，那么高质量耦合倾向于把它们映到在另一模态图上也接近的 $y_j,y_{j'}$。这里完全不需要 $p_x=p_y$，也不需要已知共享特征。

代码调用 POT 的 `entropic_gromov_wasserstein()`，额外使用熵正则系数 $\varepsilon$。较大的 $\varepsilon$ 通常产生更平滑、分散的耦合；较小值允许更集中映射，但更易出现数值不收敛。v1 用 NaN、全零行列和总质量不足 0.95 作为失败检查，并提示调大 $\varepsilon$。

$\Gamma_{ij}$ 是运输质量，不是已验证的一一细胞身份。均匀边缘还隐含两边总质量同等分配；当细胞类型比例明显不相等或某模态缺失一个群体时，平衡 GW 可能被迫产生生物学上不合理的匹配。这正是后续 SCOTv2 研究扩展到不平衡、多模态设置的动机，但它不属于本篇 SCOT v1 方法。

### 4. 重心投影怎样得到可比较的坐标

SCOT 默认把 $X$ 投到 $Y$ 的原始特征空间。对每个 $x_i$：

$$
\hat x_i=
\frac{\sum_j\Gamma_{ij}y_j}{\sum_j\Gamma_{ij}}.
$$

于是 $\hat X$ 和 $Y$ 都有 $p_y$ 列，可以共同可视化或计算对应指标；反向投影则用 $\Gamma^\top X$。这不是学习一个对新细胞可直接推理的神经网络映射，而是当前样本耦合的加权平均。因此，投影坐标可能被平滑，且换一批细胞需要重新求耦合。

论文补充表报告投影方向对其评估性能影响不显著，但这只是所测数据的经验结论；不同特征维度、噪声和细胞比例下仍需检查方向敏感性。

### 5. 两个关键超参数及“无监督自调参”

$k$ 决定图的局部尺度，$\varepsilon$ 决定耦合的熵平滑。论文提出用最终 GW distance 作为没有真对应标签时的代理分数：在候选 $(k,\varepsilon)$ 中选择收敛且 GW distance 最小的组合。图 4 显示这个代理在各数据集内部总体与 FOSCTTM 同向，但散点并不落在一条曲线上，所以它不是可靠的真实匹配误差估计。

论文补充 Algorithm 2 描述分阶段搜索：先固定初始 $k$ 搜 $\varepsilon$，再固定 $\varepsilon$ 搜 $k$，最后局部细化。当前 `scotv1.py:228-254` 则定义 12 个 $\varepsilon$ 与 5 个 $k$，通过 `search_scot()` 做二维网格搜索，共至多 60 次 GW 求解。这是论文算法与当前快照的实现差异。

更严重的是，v1 的公开自调参入口当前不可直接使用：`align(selfTune=True)` 试图解包两个返回值，但 `unsupervised_scot()` 第 254 行只返回单元素元组 `(X_aligned,)`，因此会抛出解包错误。手动调用 `search_scot()` 并使用返回的最优参数，或修复返回语句，才可执行对应流程。文档中的“自调参可用”不能视为此 commit 上已验证的接口行为。

### 6. 如何阅读实验图

图 1 从左到右展示：两个不共享特征的模态、各自的 kNN/最短路几何、GW 耦合、重心投影。图 2 的模拟包括分叉、Swiss roll、环状结构与合成 RNA-seq；图 3 在 scGEM 和 SNARE-seq 上比较真实多组学对齐。评价指标 FOSCTTM 需要已知配对细胞：对每个细胞，统计“比真实配对更近”的异域细胞比例，越低越好。它仅用于带真对应的评估，不能用于一般未配对数据的训练。

图 4 支持“GW distance 可用于无监督选参”的经验依据并比较运行时间；图 5 显示 $\varepsilon$ 往往比 $k$ 更敏感；图 6 的消融说明 kNN+Dijkstra 图距离比直接欧氏或 correlation 距离更有效。论文结论是 SCOT 与当时 MMD-MA、UnionCom 达到相当或更好的表现，同时超参数更少；这不是对所有后来方法或任意细胞组成的普遍领先声明。

### 7. 版本与代码证据边界

论文应对应 `code_repo/src/scotv1.py`，不是 2023 年更新的 `scotv2.py`。v2 接受至少两个模态、使用 PyTorch，并加入不平衡/多域设计；将 v2 行为写回 v1 论文会造成版本混淆。

v1 的核心路径与论文一致：L2 归一化、correlation kNN connectivity 图、Dijkstra、距离归一化、均匀边缘、POT 熵正则 GW 和重心投影。需要保留的边界包括：

- `align()` 的 `mode` 与 `metric` 参数没有传给 `construct_graph()`，调用处硬编码为 connectivity/correlation；用户传入其他值在普通路径中不会生效。
- z-score 分别对两个模态各自拟合 `StandardScaler`，不是共享尺度标准化。
- 无随机种子或求解日志锁定；GW 非凸，依赖 POT 版本与数值条件。
- 当前仓库 requirements 未形成现代锁文件，论文环境和当前 Python/POT API 兼容性没有在本轮重建。
- 工作区没有保存官方 60.5 KB 补充 DOC；主文保留官方补充入口和对 Algorithm 1/2、Supplementary Table S1 的引用。本轮核对了官方补充条目元数据，但不能把未本地归档的附件当作本地可复现证据。
- 大规模数据需要存储两张平方距离矩阵和跨域耦合，内存与 GW 计算随细胞数快速增长；论文的运行时间不等于任意规模的保证。

### 8. 实际使用的判断顺序

先确保每个模态内部预处理能够表达相同生物变化，再检查不同 $k$ 下图连通性；然后在一组 $\varepsilon$ 上检查收敛、耦合熵、已知细胞类型混合和 GW distance。若两边细胞比例明显不同，应避免把 v1 的均匀平衡耦合当作可信细胞对应，并考虑允许不平衡质量的后续方法。最终应把耦合作为概率对齐假设，而不是细胞身份真值。

一句话概括：SCOT 把“跨模态特征不可比较”转换成“各模态内部的细胞几何可以比较”，以 GW 求概率耦合，再用重心投影得到共同特征空间；其优势是无需配对或共享特征，主要风险来自图构建、熵参数、平衡质量假设与当前 v1 自调参接口缺陷。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SCOT: Single-Cell Multi-Omics Alignment with Optimal Transport

**Journal**: Journal of Computational Biology, Vol. 29 No. 1 (RECOMB 2021)
**DOI**: 10.1089/cmb.2021.0446
**Authors**: Pinar Demetci, Rebecca Santorella, Björn Sandstede, William Stafford Noble, Ritambhara Singh (Brown University / University of Washington)
**Code**: https://github.com/rsinghlab/SCOT

---

### Motivation & Novelty

**Biological problem**: Single-cell multi-omics data integration is essential for understanding joint regulatory mechanisms (e.g., how chromatin accessibility governs gene expression), but most sequencing assays cannot be applied simultaneously to the same cell. Researchers must split cell populations, measure different modalities separately, and then computationally align the resulting datasets — despite having no guaranteed correspondence between individual cells or features across modalities.

**Limitations of existing methods**:
- **Seurat** (Stuart et al., *Nature Methods* 2019): requires feature-level correspondences (e.g., mapping ATAC peaks to gene bodies) — impossible for modality pairs with incomparable features (e.g., methylation and expression).
- **MMD-MA** (Liu et al., *Bioinformatics* 2019): projects both datasets into a shared latent space using maximum mean discrepancy; requires three hyperparameters and provides no hyperparameter selection strategy in unsupervised settings.
- **UnionCom** (Cao et al., *Bioinformatics* 2020): extends topological manifold alignment; requires four hyperparameters, relies on user-specified defaults in unsupervised settings, GPU-intensive.
- **GUMA/joint Laplacian** (Cui et al., *NeurIPS* 2014; Wang & Mahadevan, 2009): earlier manifold alignment methods shown to perform poorly on single-cell data.

**SCOT's unique contributions**:
1. First application of Gromov–Wasserstein (GW) optimal transport to single-cell multi-omics alignment — enables cross-modal alignment by comparing *intra-domain* distances rather than requiring cross-domain feature correspondence.
2. Only **two hyperparameters** ($k$ and $\varepsilon$), compared to three (MMD-MA) and four (UnionCom).
3. **Self-tuning heuristic**: uses GW distance as a proxy for alignment quality, allowing hyperparameter selection without any orthogonal correspondence information.
4. CPU-only implementation that scales comparably to GPU-based MMD-MA.

---

### Method Overview

SCOT is an unsupervised algorithm that aligns two single-cell datasets by finding a probabilistic coupling $\Gamma$ that preserves local geometry across modalities.

**Pipeline** (see `doc_method.md` for full derivations):
1. **Normalize**: L2 row-normalize each domain (or Z-score for simulations)
2. **Build intra-domain graphs**: k-NN graphs using Pearson correlation distances, binary connectivity (not weighted)
3. **Compute distance matrices**: Dijkstra shortest-path distances on each graph, normalized to $[0,1]$
4. **Solve entropy-regularized GW**: Find coupling $\Gamma^* \in \mathbb{R}^{n_x \times n_y}$ minimizing $\langle L(D^x, D^y) \otimes \Gamma, \Gamma \rangle - \varepsilon H(\Gamma)$ via POT library
5. **Barycentric projection**: Map domain X cells onto domain Y space as $\hat{x}_i = (1/p_i) \sum_j \Gamma^*_{ij} y_j$

**Hyperparameter selection**: When ground-truth correspondences are unavailable, Algorithm 1 searches a grid of $(k, \varepsilon)$ values and returns the pair with the lowest GW distance. Empirically, this consistently finds alignments near the supervised optimum.

**Key technical choices**:
- GW distance handles non-comparable feature spaces by working with pairwise *distances within* each domain
- Graph-based (not Euclidean) intra-domain distances for robustness and denoising
- POT library's efficient $L_2$ loss implementation reduces 4th-order tensor operation from $O(n^4)$ to $O(n^3)$

---

### Evaluation

#### Datasets

| Dataset | Type | Modalities | Cells | Source |
|---------|------|-----------|-------|--------|
| Simulation 1–3 | Simulated | Bifurcation / Swiss roll / Circular frustum | 300 | MMD-MA benchmark (Noble lab, UW) |
| Synthetic RNA-seq | Simulated | 50-dim / 500-dim projections of scRNA | 5000 | Splatter (Zappia et al., 2017) |
| scGEM | Real (co-assay) | Gene expression + DNA methylation | 177 | Cheow et al., *Nat. Methods* 2016; SRA: SRP077853 |
| SNAREseq | Real (co-assay) | ATAC-seq + RNA-seq | 1047 | Chen et al., *Nat. Biotechnol.* 2019; GEO: GSE126074 |

#### Metrics

- **FOSCTTM** (fraction of samples closer than the true match): lower = better; 0 = perfect 1-to-1 alignment
- **LTA** (label transfer accuracy, $k=5$ NN classifier): higher = better; 1.0 = perfect cell-type transfer

#### Results (Supervised Hyperparameter Tuning)

| Method | Sim1 FOSCTTM | Sim2 | Sim3 | RNA-seq | scGEM | SNAREseq |
|--------|-------------|------|------|---------|-------|---------|
| SCOT | 0.085 | 0.022 | **0.009** | **0.001** | **0.192** | **0.150** |
| MMD-MA | 0.124 | 0.023 | 0.012 | 0.112 | 0.201 | **0.150** |
| UnionCom | **0.083** | **0.016** | 0.152 | 0.038 | 0.209 | 0.265 |

SCOT achieves the best or tied-best performance on 4/6 datasets; UnionCom fails substantially on Sim3 and SNAREseq.

#### Results (Fully Unsupervised)

SCOT (GW self-tuning) maintains near-optimal performance across all datasets. MMD-MA and UnionCom with default parameters fail dramatically on Sim3 (FOSCTTM 0.739, 0.684) and all real datasets.

#### Runtime

SCOT (CPU) scales similarly to MMD-MA (GPU) and better than UnionCom (GPU) on synthetic RNA-seq at growing sample sizes.

#### Ablation Study

Both (1) entropic regularization and (2) graph-based (vs. Euclidean) intra-domain distances individually improve alignment quality across both real datasets, confirming the importance of each design choice.

---

### Reproducibility: 4/5

**Rating justification**: Data is publicly available and included in the repo; core algorithm is self-contained; POT library version sensitivity is a minor risk.

**Environment setup**:
```bash
pip install numpy scipy scikit-learn POT Cython torch
# or: pip install -r requirements.txt
cd src/
python -c "from scotv1 import SCOT; print('OK')"
```

**Data availability**:
- Simulations: included in `data/simulations/` (pre-generated)
- scGEM: included in `data/scGEM/`; original SRA accession SRP077853
- SNAREseq: included as `.npy` arrays in `data/SNARE/`; original GEO: GSE126074

**Practical notes**:
- Import `from scotv1 import SCOT` (not `from scot import *` as autoTuning_example.py shows — the original file was renamed)
- **CRITICAL BUG**: `scot.align(selfTune=True)` crashes with `ValueError: not enough values to unpack` due to truncated `return X_aligned,` at `scotv1.py:253` (missing `y_aligned`)
- To reproduce paper results, use the Jupyter notebooks in `replication/` which likely call an older version
- For z-score normalization (simulations), explicitly pass `norm="zscore"` to `.align()` — default is L2
- POT library API may differ between versions; paper used POT from ~2020

**Strengths**: Self-contained, minimal dependencies, data included, notebooks for each dataset.
**Weaknesses**: selfTune bug prevents unsupervised use; no version pinning; `scotv2.py` exists but isn't covered by the paper.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
