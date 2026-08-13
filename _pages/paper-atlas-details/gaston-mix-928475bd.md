---
layout: default
permalink: /paper-atlas/gaston-mix-928475bd/
title: "GASTON-Mix"
nav: false
wide: true
description: "GASTON-Mix 不再要求整张组织共享一把“深度尺”。它先用空间门控网络把每个位置分给一个区域，再让每个区域的专家网络学习自己的标量等深度 dp(x,y)；区域内每个基因只需沿这把局部深度尺做线性变化。这样，区域边界与区域内连续梯度可以在同一个模型中联合表示。"
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
      <span>Domain Clustering</span>
      <span>Bioinformatics · 2025</span>
    </div>
    <h1>GASTON-Mix</h1>
    <p>GASTON-Mix: a unified model of spatial gradients and domains using spatial mixture-of-experts</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1093/bioinformatics/btaf254" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GASTON-Mix">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/raphael-group/GASTON-Mix" target="_blank" rel="noopener noreferrer" aria-label="Open code for GASTON-Mix">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GASTON-Mix 中文方法解读

### 一句话理解

GASTON-Mix 不再要求整张组织共享一把“深度尺”。它先用空间门控网络把每个位置分给一个区域，再让每个区域的专家网络学习自己的标量等深度 $d_p(x,y)$；区域内每个基因只需沿这把局部深度尺做线性变化。这样，区域边界与区域内连续梯度可以在同一个模型中联合表示。

### 1. 它解决的具体矛盾

许多空间域方法把一个区域近似成表达恒定的块，因此容易把强烈的区域内梯度误当成域间差异。原始 GASTON 虽然显式学习连续等深度，却使用全组织共享的标量 $d(x,y)$。论文图 1 给出反例：左域表达沿 $x$ 方向变化，右域沿 $y$ 方向变化；若边界也必须是同一个 $d$ 的等值线，就不存在同时满足这些条件的全局标量场。

GASTON-Mix 将组织划分为 $P$ 个离散空间域，并为每个域单独学习等深度。对位置 $(x,y)$、基因 $g$ 和域 $p$，模型写成

$$
f_{p,g}(x,y)=h_{p,g}(d_p(x,y)).
$$

实现中的 $h_{p,g}$ 是线性的，因此

$$
h_{p,g}(d)=\alpha_{p,g}+\beta_{p,g}d,
\qquad
\nabla f_{p,g}=\beta_{p,g}\nabla d_p.
$$

这里 $d_p$ 决定域内共同的空间方向，$\beta_{p,g}$ 决定基因沿该方向上升还是下降、变化多快。

### 2. 空间 mixture-of-experts 如何工作

输入是二维空间坐标。门控 MLP（默认 $2\rightarrow20\rightarrow20\rightarrow P$）输出 $P$ 个软权重，随后 top-1 路由只保留最大权重，将位置硬分配给一个专家。第 $p$ 个专家包含：

1. 等深度网络 $2\rightarrow20\rightarrow1$，把坐标压缩为 $d_p(x,y)$；
2. 线性表达层 $1\rightarrow G$，从等深度预测 $G$ 个训练特征。

因此一次前向传播的顺序是：坐标 → 门控概率 → top-1 域标签 → 对应域的局部等深度 → 表达预测。图 2 正是这条数据流；右侧不同域的箭头和等值线表示各专家可以学习不同方向的局部拓扑图。

### 3. 实际训练的不是原始基因计数

论文的主流程先从计数矩阵提取高变 GLM-PC，再用这些低维分量训练 MoE。代码还会分别标准化坐标矩阵和输入分量，默认以均方误差拟合标准化后的分量。这样显著降低输出维数，但也意味着神经网络学到的是能够重构降维表示的空间结构，而不是直接对每个基因建立计数似然。

默认训练 50,000 个 epoch、全批量，并交替更新专家与门控参数。代码也提供直接对计数使用 Poisson 损失的 `--use_counts` 路径，但它不是论文主实验路径。

### 4. 初始化与域数是重要前提

GASTON-Mix 不会自动推断域数 $P$。模拟实验使用已知的真实域数并以 k-means 标签初始化；真实数据使用 CellCharter 的聚类数和标签。门控网络先以这些标签做交叉熵预训练，再进入联合/交替优化。

因此真实数据结果应理解为“在 CellCharter 提供的域数和初始化之上进行空间 MoE 精炼”，不能表述为完全无监督、无需外部聚类，或由模型自行发现最佳域数。图 5、图 6 的比较优势也受这一实验条件约束。

### 5. 训练后怎样回到基因层面

MoE 训练结束后，代码固定域标签和等深度，对每个“域 × 基因”重新拟合带测序深度 exposure 的 Poisson 回归：

$$
Y_{i,g}\sim\operatorname{Poisson}\!\left(E_i\exp(\alpha_{p,g}+\beta_{p,g}d_{p,i})\right).
$$

代码用似然比检验比较含斜率模型与零斜率模型，默认阈值为 0.1。随后按每个域内 $|\beta|$ 的 95% 分位数筛选，即选斜率绝对值最大的约 5% 基因。论文正文写成“fifth percentile”，若按字面会让几乎所有基因通过；与代码和“top 5%”语义一致的阈值是第 95 百分位。

细胞类型特异分析会用细胞类型比例对计数和 exposure 加权后再拟合。这是比例加权的模型归因，不是从混合位置中直接观测到的纯细胞类型计数，也不支持因果解释。

### 6. 六张主图说明了什么

- 图 1：构造性反例说明单一全局等深度不足；它论证模型动机，不是数据实验。
- 图 2：展示门控、top-1 路由、局部等深度瓶颈和线性表达层的完整架构。
- 图 3：在 10,000 个位置、两个棋盘域和 15 个模拟基因上，GASTON-Mix 的域恢复最接近真值，平均 ARI 约 0.85。这里域数已知，结论不能外推为自动选域能力。
- 图 4：GASTON-Mix 的等深度 Kendall $\tau$ 约 0.33，高于 GASTON 约 0.29 和 GraphST 约 0.17；图像显示它恢复了域 1 内一致的方向结构。
- 图 5：在 9,696 个 MERFISH 前脑细胞上，相对 Allen CCF 参考标签，GASTON-Mix 的 ARI 为 0.717；其余图板展示 CP 区域内 `Cnr1` 随等深度下降以及比例加权的细胞类型趋势。CCF 是解剖参考代理，不是无误差的分割真值。
- 图 6：在乳腺癌 Visium 切片上展示八个域、域特异等深度、通路富集和 `CCL2`、`ALDOA`、`CDH11` 的域内趋势。这些是空间关联与富集结果，不证明因果机制、治疗反应或药物耐受。

### 7. 论文与当前代码之间的关键边界

- 当前训练循环会计算门控 importance/load 的 CV² 正则项，但调用方把返回值丢弃，并未把它加入优化损失；不能声称默认训练实际使用了该负载均衡正则。
- `regularization_coef` 控制的是另一个“预测门控 × 专家均值”辅助项，默认值为 0。
- Fourier 位置编码和 Pearson-residual PCA 是代码提供的可选扩展，论文主方法未据此报告结果。
- `perform_regressions_and_binning` 会把调用者传入的 `t` 和 `num_cts` 覆盖为 0.1 和 5；这些参数在当前实现中并非真正可配置。
- `--use_counts` 若结合打乱的小批量训练，expression 会按随机索引取样，而 exposure 仍按连续切片取样，二者可能错位；默认全批量 GLM-PC 路径不触发此问题。
- 仓库未找到生成论文全部模拟比较、Kendall $\tau$ 汇总和图 6 富集分析的完整脚本，因此“核心方法可追踪”不等于“所有论文数值可一键复现”。

### 8. 代码阅读路线

1. `GASTON-Mix/src/gastonmix/run_moe_script.py`：门控、专家、top-1 路由、初始化与训练循环。
2. `GASTON-Mix/src/gastonmix/segmented_fit.py`：域内 Poisson 回归与似然比检验。
3. `GASTON-Mix/src/gastonmix/gene_fitting.py`：斜率矩阵、95% 分位阈值和分箱入口。
4. `GASTON-Mix/src/gastonmix/dim_reduction.py`：Pearson residual PCA 备选降维。
5. `GASTON-Mix/docs/notebooks/tutorials/striatum_tutorial.ipynb`：MERFISH 教程与预计算输入的调用方式。

### 结论

GASTON-Mix 最重要的贡献不是简单地把聚类器换成 MoE，而是把“离散域归属”和“每个域自己的连续空间坐标”放进同一可训练结构。它特别适合域内存在不同方向梯度的组织；与此同时，域数与初始化依赖、训练后基因回归、未接入损失的正则项以及不完整的论文级复现脚本，都是解释结果时必须保留的边界。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## GASTON-Mix: A Unified Model of Spatial Gradients and Domains

**Paper**: Chitra U, Dan S, Krienen F, Raphael BJ. "GASTON-Mix: a unified model of spatial gradients and domains using spatial mixture-of-experts." *Bioinformatics* 41(Suppl 1):i523–i532 (2025). DOI: 10.1093/bioinformatics/btaf254

**GitHub**: https://github.com/raphael-group/GASTON-Mix

---

### Motivation & Novelty

#### The Biological Problem

Tissues are spatially organized at two levels simultaneously:
1. **Discrete spatial domains** — regions with distinct cell type composition (e.g., brain anatomical regions, tumor clones). Gene expression is approximately constant within a domain and shows sharp discontinuities at boundaries.
2. **Continuous gradients within domains** — even within a single domain, expression varies continuously in a preferred direction, driven by cellular communication, local microenvironmental signals (e.g., oxygen gradients in tumors), or cell state variation along developmental axes (e.g., dorsolateral-ventromedial gradient in the striatum).

High-throughput SRT technologies (MERFISH, 10x Visium) measure both aspects simultaneously, but no existing method models them jointly.

#### Limitations of Existing Approaches

**Spatial domain methods** (BANKSY, *Nat Genet* 2024; CellCharter, *Nat Genet* 2024; GraphST, *Nat Commun* 2023; SpaGCN, *Nat Methods* 2021) embed cells using GNNs, VAEs, or spatial kernels and cluster the embeddings. They assume expression is constant within each domain — failing to identify domains when strong within-domain gradients exist, because cells at opposite ends of a gradient appear transcriptionally dissimilar.

**GASTON** (*Nat Methods* 2025; predecessor from same lab) learns a single continuous 1D coordinate (isodepth) across the whole tissue. The spatial domains must be level sets of this global isodepth, a severely restrictive geometric assumption. **Theorem 1** in this paper proves that this assumption fails for any biologically realistic tissue where two adjacent domains have gradients pointing in different directions — a common configuration (e.g., striatum: dorsal-ventral vs. medial-lateral gradients coexist in adjacent subregions).

#### Unique Contributions

1. **Domain-Specific Spatial Topography Problem (DS-STP)**: A formal MLE framework for jointly estimating arbitrary-geometry domain assignments $w_p(x,y)$ and per-domain isodepths $d_p(x,y)$ — with no geometric constraints.
2. **Spatial Mixture-of-Experts (Spatial MoE)**: A novel deep learning architecture combining:
   - A gating network for learning arbitrary domain boundaries
   - Per-domain "expert" neural fields, each with a 1D bottleneck representing the domain-specific isodepth
3. **Mathematical theorem** proving GASTON cannot represent certain biologically plausible expression functions (Theorem 1), formally motivating the extension.
4. Single training run (vs. GASTON's 30 restarts), trained jointly with alternating optimization.

---

### Method Overview

GASTON-Mix is an unsupervised deep learning method for SRT data. Its input is the count matrix $\mathbf{A} \in \mathbb{R}^{N \times G}$ and spatial coordinates $\mathbf{S} \in \mathbb{R}^{N \times 2}$.

**Pipeline**:
1. **Dimensionality reduction**: Compute $K=20$ GLM-PCs from raw counts (Poisson family PCA) to capture the main axes of variation across cells.
2. **Gating initialization**: Train a gating MLP to predict CellCharter/k-means cluster labels using cross-entropy loss (20,000 epochs).
3. **Spatial MoE training** (50,000 epochs, alternating optimization):
   - *Gating network* (MLP: 2→20→20→P+softmax): assigns each cell $(x,y)$ a soft probability over $P$ domains.
   - *Expert networks* (one per domain, MLP: 2→20→1 isodepth, then linear 1→G): predicts GLM-PCs from the 1D isodepth within the domain.
   - Top-1 gating routes each cell to its most likely domain expert.
   - MSE loss on standardized GLM-PCs.
4. **Post-hoc Poisson regression**: For each domain, fit a Poisson linear regression of raw counts vs. isodepth per gene. The slope $\beta_{p,g}$ measures the gene's gradient strength within domain $p$.
5. **Gradient gene identification**: Genes in the top 5% by absolute slope in their domain are classified as gradient genes.

The model simultaneously outputs: (a) spatial domain assignments, (b) domain-specific isodepth maps (topographic maps), and (c) gradient genes per domain.

---

### Evaluation

#### Datasets

| Dataset | Technology | Cells | Genes | Domains |
|---------|-----------|-------|-------|---------|
| Simulated | synthetic | 10,000 | 15 | 2 (checkerboard) |
| Mouse forebrain | MERFISH | 9,696 | 1,122 | 4+ (striatum, LS, OT, etc.) |
| Human breast cancer | 10x Visium | ~3,800 spots | ~33,000 | 8 |

#### Metrics

- **ARI (Adjusted Rand Index)**: Agreement with simulated ground truth, or with Allen CCF anatomical reference labels in the brain data. The CCF labels are a reference proxy, not error-free segmentation truth.
- **Kendall's τ**: Correlation between learned isodepth and true domain-specific isodepth (simulation only).
- **GSEA (Gene Set Enrichment Analysis)**: Biological validation of gradient genes using hallmark cancer gene sets.

#### Comparative Results

**Simulation (checkerboard pattern with 2 orthogonal gradient directions)**:
- GASTON-Mix ARI ≈ **0.85** vs. mean ARI < 0.70 for all competitors.
- GASTON specifically fails (poor ARI, predicted isodepths are spatially incoherent) because the checkerboard violates its global isodepth assumption (Theorem 1).
- Kendall's τ for isodepth recovery: GASTON-Mix ≈ **0.33** vs. GASTON ≈ 0.27 vs. GraphST ≈ 0.17.

**Mouse forebrain (MERFISH)**:
- GASTON-Mix ARI = **0.717** vs. best competitor (GASTON) ARI = 0.407, and BANKSY/GraphST/CellCharter all < 0.32.
- GASTON-Mix is the only method identifying the caudoputamen (CP) as a single domain (others fragment it), correctly because it learns the prominent dorsolateral-ventromedial gradient within CP.
- Biologically validated: identifies *Cnr1* with CP-specific gradient (known dorsolateral-ventromedial marker), confirmed as non-cell-type-attributable.
- Identifies lateral septum dorsal-ventral gradients (implicated in social behavior regulation).

**Breast cancer (10x Visium)**:
- GASTON fails domain identification (incorrect global isodepth assumption for complex tumor geometry).
- GASTON-Mix learns 8 tumor domains with domain-specific hypoxia (*ALDOA*, glycolysis pathway genes in domain 3) and TNF-α signaling (*CCL2* in domain 2, *CDH11* in domains 3 and 7) gradients validated by GSEA (FDR < 10⁻⁵).

---

### Reproducibility

**Rating: 3/5**

**Strengths**:
- Code is well-organized (`src/gastonmix/`) with clear CLI entry point (`run_moe_script.py`).
- Tutorial notebook (`striatum_tutorial.ipynb`) with pre-computed data files (GLM-PCs, CellCharter labels) enables quick reproduction of the mouse forebrain experiment.
- Modular design — preprocessing, training, gene fitting, and visualization are separate modules.

**Weaknesses**:
- CellCharter must be run separately as a preprocessing step; no wrapper script for the full end-to-end pipeline.
- No conda/pip environment specification (`requirements.txt` or `environment.yml` missing).
- The critical hyperparameter, number of experts $P$, is supplied externally and is not inferred by the model: simulations use known $P$, while real-data experiments use CellCharter's cluster count and labels.

- The current code computes a CV² routing/load-balancing value but discards it in the training loop; default results should not be described as optimized with this regularizer.
- Supplementary materials (Theorem 1 proof, simulation details, tumor details) are in a 43MB PDF not converted to text.
- No code for the simulated experiment (Section 3.1) in the repo.
- Breast cancer analysis not reproduced in public tutorial; only mouse forebrain.

**Environment setup**:
```bash
# Install gastonmix package
cd GASTON-Mix && pip install -e .

# Required packages
pip install torch numpy scanpy glmpca scikit-learn pandas matplotlib tqdm scipy seaborn

# Run CellCharter separately to get initialization labels, then:
python src/gastonmix/run_moe_script.py \
  --seed 1 \
  --data_folder striatum_1058/ \
  --folder_to_save striatum_1058_MoE_output/ \
  --coords_file striatum_1058/coords_mat.npy \
  --expression_file striatum_1058/glmpca_mat.npy \
  --manual_init striatum_1058/cellcharter_labels_4.npy \
  --num_experts 4 \
  --num_epochs 50000 \
  --gating_arch 20 20 \
  --spatial_arch 20 \
  --expression_arch \
  --alternating 1000 \
  --device cuda
```

**Common pitfalls**:
- The `glmpca` Python package can be slow; using pre-computed `glmpca_mat.npy` is strongly recommended.
- `--alternating` interval significantly affects results; the tutorial doesn't specify the value used in experiments.
- The number of experts $P$ should match the CellCharter cluster count exactly.
- On CPU: training 50,000 epochs is extremely slow; GPU is effectively required.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
