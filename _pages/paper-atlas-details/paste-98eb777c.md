---
layout: default
permalink: /paper-atlas/paste-98eb777c/
title: "PASTE"
nav: false
description: "空间转录组（ST）的一张切片给出两类观测：每个 spot 的基因表达向量，以及该 spot 在本切片内的二维坐标。相邻切片来自同一块三维组织，但组织放到芯片上的平移、旋转、覆盖范围、spot 数量和测序深度都可能不同。因此，两张切片的原始坐标没有共同坐标系，单靠图像刚体配准或按表达最近邻匹配都不够。 PASTE 提供两个相关但不同的任务： 成对对齐：求两张切片 spot 之间的概率耦合，再把连续切片变换到共同坐标系，用于三维堆叠。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Methods · 2022</span>
    </div>
    <h1>PASTE</h1>
    <p>Alignment and integration of spatial transcriptomics data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-022-01459-6" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PASTE 方法解读：同时利用表达与空间结构对齐多张空间转录组切片

### 1. 问题不是“把坐标叠起来”

空间转录组（ST）的一张切片给出两类观测：每个 spot 的基因表达向量，以及该 spot 在本切片内的二维坐标。相邻切片来自同一块三维组织，但组织放到芯片上的平移、旋转、覆盖范围、spot 数量和测序深度都可能不同。因此，两张切片的原始坐标没有共同坐标系，单靠图像刚体配准或按表达最近邻匹配都不够。

PASTE 提供两个相关但不同的任务：

1. **成对对齐**：求两张切片 spot 之间的概率耦合，再把连续切片变换到共同坐标系，用于三维堆叠。
2. **中心切片整合**：从多张切片推断一张低秩共识表达切片，以降低稀疏性、提高聚类和差异表达的统计功效。

这两种输出不能混为一谈。成对模式保留每张原始切片；中心模式生成一个统计意义上的共识切片，并不声称重建真实存在的某个物理切面。

### 2. 成对对齐：FGW 如何同时比较表达和形状

设切片 $A$ 有 $n$ 个 spot，切片 $B$ 有 $n'$ 个 spot。$X,X'$ 是表达矩阵，$D,D'$ 是各切片内部 spot 两两之间的欧氏距离矩阵。PASTE 求一个非负耦合矩阵 $\Pi\in\mathbb{R}_+^{n\times n'}$。默认每张切片的 spot 质量均匀，因此

$$
\Pi\mathbf 1=\frac1n\mathbf 1,
\qquad
\Pi^\top\mathbf 1=\frac1{n'}\mathbf 1.
$$

目标是 fused Gromov–Wasserstein（FGW）代价：

$$
\min_{\Pi}
(1-\alpha)\sum_{ij}c(X_i,X'_j)\pi_{ij}
+
\alpha\sum_{ii'jj'}(D_{ii'}-D'_{jj'})^2\pi_{ij}\pi_{i'j'}.
$$

第一项要求被配对 spot 的表达相似；第二项不直接比较两张切片的绝对坐标，而是要求“切片内的相对距离关系”在映射后相似。因此，即使一张切片被整体旋转或平移，第二项仍能比较其内部几何结构。

$\alpha$ 控制两种证据的权衡。$\alpha=0$ 只看表达，$\alpha=1$ 只看内部几何；论文默认并主要使用 $\alpha=0.1$，模拟实验显示联合两者通常优于两个极端。它不是普适最优常数，组织间差异大、表达噪声高或预处理改变时仍需做敏感性分析。

默认表达代价采用带 0.01 伪计数、按 spot 归一化后的 KL 型散度；代码也允许欧氏距离。源码 `pairwise_align()` 先取共同基因，计算 $D,D'$ 和表达代价 $M$，再把它们交给自定义 FGW 求解器。底层通过 POT 的条件梯度（Frank–Wolfe）算法求局部数值解。

### 3. 为什么输出是“概率耦合”而非一一对应

$\Pi_{ij}$ 表示切片 A 的 spot $i$ 与切片 B 的 spot $j$ 之间分配了多少运输质量。它一般不是置换矩阵：两张切片的 spot 数和组织覆盖不同，一个 spot 也可能包含多个细胞类型，所以一个 spot 可以把质量分到另一张切片的多个 spot。论文在多个数据集中观察到耦合较稀疏，但“稀疏”是实验结果，不是接口保证的一一匹配。

因此，解释 $\Pi$ 时应看加权对应关系，不能简单把每行最大值当成已证实的同一细胞。跨切片 spot 标签一致率也是基于已有区域或层标签的评估代理，不是真实逐 spot 配准金标准。

### 4. 从概率耦合到三维堆叠

FGW 产生的是 spot 间耦合，不会直接修改二维坐标。`stack_slices_pairwise()` 对连续切片的耦合做加权 Procrustes/Kabsch 对齐：先计算耦合加权质心，再通过 SVD 求旋转矩阵和平移量，把下一张切片变换到前一张切片的坐标系。连续应用这些变换后，可以把切片按已知的切片顺序放在不同 $z$ 高度形成堆叠。

这个三维结果恢复的是切片间的二维刚体关系，而不是自由形变的三维组织模型。它不能校正组织撕裂、局部伸缩或切片间真实形态变化；连续配准还可能累积误差。论文的 DLPFC 结果显示相距 10 μm 的切片通常比相距 300 μm 的切片更容易对齐，这正反映了该边界。

### 5. 中心切片：FGW barycenter 与 NMF 的交替优化

中心模式选一张输入切片作为空间模板，固定其 spot 数与坐标，推断共识表达矩阵 $X_c=WH$。其中 $W,H\ge0$，秩默认 $m=15$。目标是让中心切片到所有输入切片的 FGW 代价加权和最小：

$$
R(W,H,\Pi^{(1)},\ldots,\Pi^{(t)})
=\sum_{q=1}^{t}\lambda_q
F(WH,D_c,X^{(q)},D^{(q)},\Pi^{(q)}),
$$

默认 $\lambda_q=1/t$。代码进行块式交替：

1. 固定 $W,H$，将当前 $WH$ 作为中心表达，分别调用 `pairwise_align()` 更新中心到每张输入切片的 $\Pi^{(q)}$。
2. 固定耦合，将各切片表达按 $\Pi^{(q)}$ 拉回中心 spot，形成加权聚合矩阵 $B$。
3. 对 $B$ 重新做 NMF，更新 $W,H$。
4. 直到加权 FGW 目标变化小于阈值或达到最大迭代数。

默认 KL 情况下，scikit-learn NMF 使用 multiplicative update 与 KL beta loss。低秩 `center_slice.X=WH` 适合聚类和降噪；代码还把未做低秩压缩的加权表达保存为 `center_slice.uns['full_rank']`，论文建议差异表达等需要保留基因细节的分析使用全秩结果。

### 6. 代码跟论文一致在哪里，又有哪些边界

当前代码快照为 `5f0d58c67c7ad2b51ccdf67bad3c31df761fd9bc`。`paste/src/paste/PASTE.py` 直接实现论文的主要对象：共同基因筛选、空间距离、KL/欧氏表达代价、均匀边缘分布、FGW 条件梯度、中心切片的 FGW/NMF 交替，以及低秩与全秩输出。`visualization.py` 实现由耦合驱动的刚体堆叠。核心算法对应度高。

仍有几个不能被“高对应度”掩盖的实现边界：

- 中心迭代每轮用 `NMF.fit_transform(B)` 重新拟合，没有把上一轮 $W,H$ 作为 warm start；NMF 非凸，若不设置 `random_seed`，重复运行可能不同。
- KL 辅助函数的参数方向与论文符号书写需要谨慎对照；代码行为应以实际 `kl_divergence_backend()` 为准，不能只凭符号名称断言方向完全相同。
- 包中没有论文全部模拟、比较方法和空间一致性评分脚本；这些属于论文复现分析层，不是核心 Python API。
- `build/lib` 是构建产物，真正应阅读和修改的是 `src/paste`。当前工作区还包含打包的 1.4.0 wheel/sdist，但嵌套 Git HEAD 是本次静态核对的版本标识。
- GPU 只在选择 Torch backend 且 CUDA 可用时启用；默认是 NumPy CPU。高分辨率切片需要存储 $n\times n$、$n'\times n'$ 以及 $n\times n'$ 矩阵，内存随 spot 数快速增长。

### 7. 如何读论文的实验图

图 1 给出两条模式：左侧由相邻切片耦合生成三维堆叠，右侧由多切片生成低稀疏度中心切片。图 2 的模拟实验分别改变噪声和 $\alpha$，支持“表达与空间共同使用”的设计，而不是证明 $\alpha=0.1$ 对所有数据都最佳。

SCC 实验显示低测序深度会同时降低聚类空间一致性和标签一致的对齐比例，补充分析通过下采样揭示测序深度这一混杂因素。DLPFC 实验以皮层层级标签评估配准，并展示中心切片可提高聚类 ARI、恢复 MFGE8、TRABD2A 等层特异标志。这里的提升来自跨切片聚合和空间约束；它不说明中心切片中的每个数值是额外测得的独立分子计数。

补充材料还展开了算法推导、模拟设置、不同 $\alpha$、表达代价、空间一致性、低覆盖下采样和额外组织案例。它们支持参数与评估解释，但没有消除数据预处理、切片选择、模板选择和随机初始化对复现的影响。

### 8. 实际使用时的最小检查清单

输入 AnnData 至少要保证：不同切片基因名可正确求交集；`X` 是与所选表达距离相容的非负矩阵；二维坐标位于 `obsm['spatial']`；切片确实来自可比较的相邻组织。运行后应同时检查目标值、耦合稀疏性、已知解剖结构、不同 $\alpha$ 的稳定性和多随机种子结果，而不是只看叠图是否“看起来对齐”。

PASTE 的关键思想可以概括为：不要求跨切片绝对坐标一致，而是用 FGW 同时寻找表达相似且能保存两张切片内部几何关系的概率映射；随后，这些映射既可以驱动刚体三维堆叠，也可以在 NMF 约束下汇聚成一张共识表达切片。

### 证据入口

- 主论文与图注：`paper source/paper/auto/paper.md`
- 补充材料：`paper_supp1.pdf`、`paper_supp2.pdf`、`paper_supp3.pdf`
- 图逐项解释：`figure_analysis.md`
- 成对与中心算法：`paste/src/paste/PASTE.py`
- KL 与数据辅助函数：`paste/src/paste/helper.py`
- 刚体堆叠：`paste/src/paste/visualization.py`
- 代码—论文映射：`doc_code.md`

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## PASTE: Probabilistic Alignment of Spatial Transcriptomics Experiments

**Paper**: Alignment and integration of spatial transcriptomics data
**Authors**: Ron Zeira, Max Land, Alexander Strzalkowski, Benjamin J. Raphael
**Journal**: Nature Methods, 2022 (Published online May 16, 2022)
**DOI**: 10.1038/s41592-022-01459-6
**Code**: https://github.com/raphael-group/paste

---

### Motivation & Novelty

#### Biological Problem

Spatial transcriptomics (ST) measures gene expression while preserving 2D spatial coordinates of tissue spots, enabling mapping of cell types and gene expression patterns within tissues. However, most ST studies collect multiple adjacent slices from the same tissue to increase statistical power, and these slices cannot be compared directly:

1. **Coordinate mismatch**: Each slice is placed on the array at a different position/orientation, so raw spatial coordinates across slices are incomparable
2. **Low coverage per spot**: ~5,000 UMIs per spot leads to high sparsity (≥75% zeros), making rare cell-type markers undetectable in any single slice
3. **No spot-level correspondence**: Without explicit alignment, pooling expression data across slices ignores spatial context

#### Limitations of Existing Approaches

- **STUtility** (BMC Genomics 2020): Aligns H&E stained images only; ignores gene expression data; fails with orientation differences between slices
- **Splotch** (bioRxiv 2019): Requires manual tissue region annotation; designed for old low-resolution ST platforms
- **Seurat** (Cell 2019): scRNA-seq integration that completely ignores spatial coordinates
- **Scanorama** (Nature Biotechnology 2019): Similarly expression-only; designed for scRNA-seq, not ST alignment
- **Tangram** (Nature Methods 2021): Maps scRNA-seq onto ST, not designed for slice-to-slice alignment

#### Unique Contributions

1. **Fused Gromov-Wasserstein optimal transport** for joint expression + spatial alignment: uses within-slice spatial distances (rotation-invariant) alongside transcriptional similarity, eliminating dependence on absolute coordinates
2. **Two complementary modes**: pairwise slice alignment (→ 3D tissue reconstruction) and center slice integration (→ improved statistical power in 2D)
3. **NMF-integrated barycenter**: center slice integration produces a low-rank expression matrix with Poisson likelihood model, appropriate for count data with dropouts
4. **Full-rank integration matrix** for downstream analysis: prevents inflated test statistics from low-rank imputation

---

### Method Overview

PASTE operates on AnnData objects containing the gene expression matrix $X \in \mathbb{N}^{p \times n}$ and spatial coordinates $Z \in \mathbb{R}^{2 \times n}$. See `doc_method.md` for full mathematical derivations and `doc_code.md` for implementation details.

#### Mode 1: Pairwise Slice Alignment

Computes a probabilistic mapping $\Pi \in \mathbb{R}^{n \times n'}_+$ between spots of two slices by minimizing the **Fused Gromov-Wasserstein (FGW) cost**:
$$F(\Pi) = (1-\alpha)\underbrace{\sum_{i,j}c(x_{\cdot i}, x'_{\cdot j})\pi_{ij}}_{\text{expression dissimilarity}} + \alpha\underbrace{\sum_{i,j,k,l}(d_{ik}-d'_{jl})^2\pi_{ij}\pi_{kl}}_{\text{spatial consistency}}$$

The spatial term ensures that pairs of aligned spots preserve their relative distances within each slice. Solved via Frank-Wolfe conditional gradient algorithm (POT library). Default $\alpha=0.1$ and KL divergence expression cost. Pairwise alignments are combined into 3D reconstructions via the Kabsch/Procrustes algorithm.

#### Mode 2: Center Slice Integration

Finds a single center slice with low-rank expression matrix $X = WH$ ($W \in \mathbb{R}^{p \times 15}_+$, $H \in \mathbb{R}^{15 \times n}_+$) that minimizes the weighted sum of FGW costs to all input slices. Solved via block coordinate descent alternating between:
- **Transport step**: compute pairwise alignments from center to each slice
- **NMF step**: update $W, H$ to minimize reconstruction error given current alignments

The full-rank integration matrix $\bar{X} = n\sum_q \lambda_q X^{(q)}\Pi^{(q)T}$ is used for differential expression analysis.

---

### Evaluation

#### Datasets

| Dataset | Source | Technology | Slices | Spots/Slice | Application |
|---------|--------|-----------|--------|-------------|-------------|
| Breast cancer | Ståhl et al., Science 2016 | ST | 4 | 251-264 | Simulation |
| Squamous cell carcinoma (SCC) | Ji et al., Cell 2020 | ST + Visium | 4 patients × 3 slices | 600-700 | Alignment accuracy |
| Spinal cord | Maniatis et al., Science 2019 | ST | 2 | — | Generalization |
| Her2 breast cancer | Andersson et al., Nat. Commun. 2021 | ST | — | — | Fine spatial structures |
| DLPFC | Maynard et al., Nat. Neurosci. 2021 | Visium | 3 individuals × 4 slices | 3,431-4,786 | Benchmarking |

#### Key Results

**Simulation (breast cancer)**: PASTE ($\alpha=0.1$) achieves highest accuracy and correctly aligns ~86% of spots (the maximum possible, limited by tissue boundary differences). Using only expression ($\alpha=0$) degrades with increasing noise; using only spatial data ($\alpha=1$) fails completely when tissue is rotated.

**SCC pairwise alignment**: 20-70% of aligned spots share published cluster labels. Patient 2 (highest coverage, 2× more UMIs) achieves 70%; patients 5, 9, 10 achieve only 20-50%, likely due to lower sequencing coverage. PASTE center integration improves spatial coherence scores for all 4 patients.

**DLPFC benchmarking** (Table: pairwise alignment accuracy):

| Method | Close pairs (AB, CD, 10 μm) | Middle pairs (BC, 300 μm) |
|--------|------------------------|--------------------------|
| PASTE ($\alpha=0.1$) | **>81%** (5/9 best) | 21-82% |
| Seurat (Cell 2019) | Lower than PASTE | Highest on 2/3 middle pairs |
| Tangram (Nat. Methods 2021) | 0.28-0.53 | Similar |
| STUtility (BMC Genomics 2020) | ~PASTE (+0.007) | Much lower (mirroring error) |

**DLPFC center integration (Sample III)**:
- Single slice clustering: ARI = 0.21-0.24 (including Maynard et al. 0.2-0.4)
- Scanorama integration: ARI = 0.16-0.18
- Seurat integration: ARI = 0.24-0.31
- **PASTE center integration: ARI = 0.53** (2-3× improvement)

**Differential expression (DLPFC)**:
- PASTE recovers 80/126 known marker genes (adjusted P<0.01)
- Single slice analysis: 44-58/126
- Median marker gene rank: PASTE=427 vs Maynard et al.=1,147 vs Scanorama=3,381 vs Seurat=1,852

#### Parameter Sensitivity

- Performance is robust across $0 < \alpha < 1$ for intermediate values
- KL divergence + all genes outperforms log-normalized + HVG for alignment
- Uniform spot weights comparable to cell-number-weighted spots

---

### Reproducibility

**Rating: 3/5**

**Justification**: Core algorithm is open source and well-documented. The main package (`paste`) is pip-installable. However, the supplementary analyses (spatial coherence score, simulation code, comparison methods) live in a separate `paste_reproducibility` repo. Processed data is deposited at Zenodo (https://doi.org/10.5281/zenodo.6334774). GPU support exists since v1.2.0. NMF random initialization can cause non-deterministic results unless `random_seed` is set.

**Environment setup**:
```bash
pip install paste-bio  # or
pip install git+https://github.com/raphael-group/paste
# Dependencies: POT==0.9.0, anndata>=0.7.6, scanpy>=1.7.2, scikit-learn>=0.24.0
```

**Common pitfalls**:
1. **POT version sensitivity**: The custom `my_fused_gromov_wasserstein()` patches POT's FGW solver to support G_init. POT 0.9.0 is tested; newer versions may have API changes
2. **Memory for large Visium slices**: ~200 MB per 5,000-spot pair for distance and cost matrices; plan ~2-4 GB RAM for 4-slice center alignment
3. **NMF non-determinism**: Set `random_seed` in `center_align()` for reproducibility
4. **Center template selection**: The slice with the most spots should be used as the template `A` in `center_align()`; code does not enforce this automatically
5. **Sparse expression matrices**: Pass `to_dense_array()` if AnnData.X is scipy sparse — helper handles this automatically

**Data availability**: All benchmark datasets (breast cancer, SCC, spinal cord, Her2, DLPFC) taken from original publications; preprocessed versions at Zenodo.

**Strengths**: Clean Python API; AnnData/Scanpy compatible; GPU support; clear mathematical formulation; two complementary modes addressing different biological questions.

**Weaknesses**: Quadratic in number of spots (not scalable to high-resolution technologies like Slide-seq2 with >50,000 spots); NMF in center mode is re-initialized at each iteration (not warm-started, though transport maps are warm-started); spatial coherence evaluation metric not in main package; does not use histological images.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
