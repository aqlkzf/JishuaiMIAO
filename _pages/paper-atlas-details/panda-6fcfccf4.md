---
layout: default
permalink: /paper-atlas/panda-6fcfccf4/
title: "PANDA"
nav: false
description: "Visium、早期 Spatial Transcriptomics 等测序型空间技术的一个 spot 往往包含多个细胞。常规反卷积把 spot 表达解释成若干固定细胞类型 signature 的线性混合，只输出每种细胞类型的比例。问题是同一类型的细胞会随肿瘤边界、皮层深度或发育阶段改变状态；用一个全局均值 signature 既可能降低比例估计，也无法回答“这个 spot 中的 B 细胞在表达什么”。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>Nucleic Acids Research · 2024</span>
    </div>
    <h1>PANDA</h1>
    <p>Dual decoding of cell types and gene expression in spatial transcriptomics with PANDA</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1093/nar/gkae876" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PANDA：同时解码空间 spot 的细胞类型比例与类型特异表达

### 方法要解决的缺口

Visium、早期 Spatial Transcriptomics 等测序型空间技术的一个 spot 往往包含多个细胞。常规反卷积把 spot 表达解释成若干固定细胞类型 signature 的线性混合，只输出每种细胞类型的比例。问题是同一类型的细胞会随肿瘤边界、皮层深度或发育阶段改变状态；用一个全局均值 signature 既可能降低比例估计，也无法回答“这个 spot 中的 B 细胞在表达什么”。

PANDA（ProbAbilistic-based decoNvolution with spot-aDaptive cell type signAtures）把任务拆为两步：先从带标签的 scRNA-seq 参考中为每个细胞类型学习多个 archetype，近似该类型的状态空间；再让每个空间 spot 对每个细胞类型选择不同的 archetype 组合。最终同时得到 spot×cell-type 比例和每个 cell type 的 spot×gene 表达矩阵。

### 输入和输出

输入有三项：scRNA-seq 原始 count 矩阵（cell×gene）、每个细胞的 cell-type label、空间转录组原始 count 矩阵（spot×gene）。空间坐标不进入 PANDA 的概率模型；坐标只用于后续画图和解释。因此 PANDA 是 reference-based expression deconvolution，不是利用邻接图或组织图像的空间平滑模型。

主要输出包括：

- `proportion[s,k]`：spot $s$ 中 cell type $k$ 的归一化比例；
- `beta[s,k]`：未归一化 abundance；
- `alpha[s,a]`：spot 对各 cell-type archetype 的组合权重；
- `mu[[k]][s,g]`：spot $s$ 中类型 $k$ 的表达 signature；
- `gamma[g]`：空间平台与 scRNA 参考之间的 gene-specific platform effect。

### 第一步：在每个细胞类型内部学习 archetype

#### 为什么用表达率而不是原始 count

对类型 $k$ 的细胞 $c$、基因 $g$，PANDA 假设

$$
X_{cg}^{(k)}\sim\operatorname{Poisson}\left(N_c^{(k)}\lambda_{cg}^{(k)}\right),
$$

$N_c$ 是 library size，$\lambda_{cg}$ 是表达率。代码先计算 `Z <- sc_counts / N`（`PANDA/R/PANDA.R:460-468`），避免 archetype 主要沿测序深度排列。Poisson 假设把均值和方差绑定，计算简洁但不能显式描述负二项式式过度离散，这是论文承认的模型边界。

#### archetype 是参考细胞的凸组合

对类型 $k$ 的 archetype $a$：

$$
\varphi_{ag}^{(k)}=\sum_{c'=1}^{C_k}W_{ac'}^{(k)}Z_{c'g}^{(k)},
\qquad W_{ac'}^{(k)}\ge0,\quad\sum_{c'}W_{ac'}^{(k)}=1.
$$

每个 archetype 位于该类型已观察细胞的凸包内，而不是任意自由参数。反过来，每个参考细胞也由 archetype 凸组合：

$$
\lambda_{cg}^{(k)}=\sum_{a=1}^{A_k}\alpha_{ca}^{(k)}\varphi_{ag}^{(k)},
\qquad \alpha_{ca}^{(k)}\ge0,\quad\sum_a\alpha_{ca}^{(k)}=1.
$$

默认每个类型 $A_k=10$。多个 archetype 不是预先命名的亚型，而是包围类型内表达状态的极端代表；它们能表达连续变化，也可能在 archetype 太多时吸收噪声。

代入后得到完整生成均值 $N_c(\alpha WZ)_g$。`sc_model()` 的 loss 使用该 Poisson rate，并对 $\alpha$ 与 $W$ 的行和施加软约束（`PANDA.R:262-272`）。两者通过乘法更新保持非负（`:275-280`），相对 loss 变化低于 $10^{-8}$ 或达到 2,000 iteration 停止（`:281-292`），最后 `phi <- W %*% Z`（`:294`）。

实现有一个主文未显式强调的正则强度 `tau <- var(X) * 20 / n_genes`（`:247`），控制软凸组合约束。补充 Notes 给出目标与乘法更新推导，因此它不是任意后处理，但复现时必须保留这项代码参数。

#### 初始化和下采样

随机初始化容易把多个 archetype 放到相近位置。PANDA 先用 max-min sampling 选互相远离的参考细胞：从范数最大的点起，每次选择到已选集合最小距离最大的点（`PANDA/R/utils.R:48-58`）。再用标准化后的 cosine similarity 初始化 $W$ 和 $\alpha$ 并按行归一化（`PANDA.R:319-335`）。

预处理过滤 library size <200 的细胞；选择 2,000 HVG 与每个类型 top 20 positive marker 的并集；超过 500 个细胞的类型用 max-min 而非随机抽样降至 500（`PANDA.R:456-514`）。这样保留状态空间边缘，但抽样结果仍由参考数据覆盖决定。

`sc_train()` 可按 cell type 并行训练，默认最多 20 cores，并同时保存 selected-gene archetype 与 all-gene archetype（`PANDA.R:34-113`）。archetypal analysis 只依赖参考，一种组织的结果可复用于多个空间切片。

### 第二步：用 spot-adaptive signature 反卷积空间数据

#### spot count 的生成模型

对 spot $s$、基因 $g$：

$$
Y_{sg}\sim\operatorname{Poisson}\left(N_s\lambda_{sg}e^{\gamma_g}\right),
$$

$N_s$ 是 spot library size，$e^{\gamma_g}$ 是跨平台 gene effect。spot 表达率由细胞类型混合：

$$
\lambda_{sg}=\sum_{k=1}^K\beta_{sk}\mu_{sg}^{(k)}.
$$

$\beta_{sk}\ge0$ 在拟合时不强制和为 1，以吸收 spot-specific scale；训练后才做

$$
p_{sk}=\frac{\beta_{sk}}{\sum_{k'}\beta_{sk'}}.
$$

关键是类型 $k$ 的 signature 也随 spot 变化：

$$
\mu_{sg}^{(k)}=\sum_{a=1}^{A_k}\alpha_{sa}^{(k)}\varphi_{ag}^{(k)},
\qquad \sum_a\alpha_{sa}^{(k)}=1.
$$

因此同一细胞类型在 tumor core 和 immune border 可以用不同 archetype 权重；signature 仍被约束在 scRNA 参考所定义的凸包里，不能生成参考中完全不存在的状态。

完整模型为

$$
Y_{sg}\sim\operatorname{Poisson}\left[
N_s\sum_k\beta_{sk}\left(\sum_a\alpha_{sa}^{(k)}\varphi_{ag}^{(k)}\right)e^{\gamma_g}
\right],
$$

并给平台效应先验

$$
\gamma_g\sim\mathcal N(0,\sigma^2),\qquad \sigma=0.3/\sqrt S.
$$

较小 $\sigma$ 抑制把生物差异全部解释成平台差异；若平台偏差很强又会校正不足。

#### omega 重参数化

代码没有直接交替优化每个 $\beta_{sk}$ 和 $\alpha_{sa}^{(k)}$，而是把乘积编码为 spot×archetype 辅助矩阵 $\omega$。`Q[k,a]` 是 archetype 到 cell type 的 one-hot 对应。拟合后：

$$
\beta=\omega Q^T,
\qquad
\alpha=\omega\oslash(\beta Q).
$$

`st_model()` 在 `PANDA.R:420-423` 直接恢复 beta、alpha 和 proportion。这个参数化用一个非负矩阵同时表达类型 abundance 与类型内状态，减少显式约束操作。

#### 两阶段优化和 platform-effect 基因过滤

初始化用 spot expression rate 与 archetype 的 cosine similarity。Phase 1 固定 $\gamma=0$，只乘法更新 $\omega$ 到收敛（`PANDA.R:379-396`）。随后比较每个基因的总观测量与初始模型期望，只保留比例在 0.4–2.5 的基因（`:398-402`），避免极端平台差异在初始化阶段主导模型。

Phase 2 在保留基因上交替：乘法更新 $\omega$，对无约束 $\gamma$ 做 gradient/Hessian Newton step（`:404-418`）。目标函数就是 Poisson negative log-likelihood 加 $\gamma^2/(2\sigma^2)$ MAP penalty（`:369-376`）。补充 Algorithm 2 和式 53 与这条代码路径一致。

过滤只影响用于拟合 platform effect 的基因。类型特异表达输出不乘 $e^\gamma$：作者选择直接返回 scRNA-derived spot-adaptive signature，以减少空间技术低检测效率并允许 all-gene 恢复。`st_train()` 用已学的 $W$ 乘完整参考表达率得到 `phi_all`，再计算 `alpha %*% diag(Q[k,]) %*% phi_all`（`PANDA.R:157-194`）。因此 `mu` 是参考状态空间中的估计表达率，不是把 spot raw counts 严格拆成每类的实际 UMI count。

### 图 1 和图 2：方法与 benchmark 的直接证据

图 1A 依次画出 scRNA reference、每类 archetype 凸包、spot-specific 组合和双输出；图 1B 展示比例定位、类型内空间/时间异质性和细胞通信等用途。它准确表达了方法边界：PANDA 的直接产物是比例与 `mu`，GO、NicheNet、聚类和空间统计是后续工具。

图 2 构造 paired 与 unpaired scRNA 模拟，又分别设置 ST-like 10–30 cells/spot、Visium-like 1–10 cells/spot，以及 uniform/non-uniform state sampling。横轴是比例准确度，纵轴是 signature 准确度，用 PCC、RMSE、JSD 同时比较。PANDA 在总体 rank 上领先，尤其 unpaired/batch-effect 场景中 spot-adaptive archetype 比固定 signature 更有优势。

这些 pseudo-spot 共享已知 scRNA 数据生成机制，仍不能完全模拟真实空间捕获、RNA diffusion、组织损伤和 reference 缺失状态。补充材料还用 MERFISH 聚合伪 spot 验证，并做 archetype 数、$\sigma$、reference 选择和计算资源敏感性。

### 三个真实组织应用怎样使用双输出

#### 黑色素瘤

图 3 的 proportions 把 malignant、B/T、CAF/Endo 对应到病理标注的 melanoma-rich、lymphoid-rich、stromal-rich 区域。随后使用 B-cell-specific `mu` 比较淋巴区与肿瘤区 B 细胞：前者富集增殖功能，后者偏免疫反应调节/分化。恶性细胞 `mu` 与免疫比例相关得到边界正相关 G1、core 负相关 G2，再把这些基因作为 NicheNet targets 分析 CXCL12–CXCR4 等配体链。

相关性和 NicheNet regulatory potential 是候选通信证据，不证明空间邻近细胞之间发生了直接因果信号。对应分析代码不在本地 R package，而在论文所列 Zenodo analysis 工件。

#### 小鼠脑皮层

图 4 的 proportions 重建 L2/3 IT→L4→L5 IT→L6 CT/IT→L6b 的层状顺序。筛选对应类型比例 >0.3 的 spots 后，对 L2/3 IT-specific 与 L5 IT-specific `mu` 分别聚类/PCA，发现随 cortical depth 的离散层与连续 PC1 梯度。这说明固定 cell type label 内仍有空间转录变化；阈值、PCA 和相关分析是 application-specific，不是 PANDA 核心模型的内置空间 prior。

#### 发育中人心脏

图 5 分析 4.5–5、6.5、9 PCW 共 19 个切片。proportion 显示 ventricular cardiomyocyte 增加、epicardial 减少而 epicardium-derived 增加。ventricular-cardiomyocyte-specific `mu` 被归纳成 Stable-Increase、Decrease-Increase、Stable-Decrease、Increase-Decrease 四类时序模式并做 GO enrichment。跨切片比较使用参考 derived signatures，有助于减轻平台检测差异，但仍需要控制切片批次、供体和发育阶段混杂。

### 补充材料提供了什么

本地 `gkae876_supplemental_file.pdf` 包含完整目标函数与乘法/Newton 更新推导、Algorithm 1/2、七种对比方法设置、模拟细节、真实数据下游流程、Supplementary Figures S1–S53 和表。关键补充证据包括：0.4–2.5 平台基因筛选、四组 archetype/$\sigma$ 敏感性、不同 reference 下 likelihood–accuracy 关系和资源消耗。

高 average log-likelihood 往往对应更准确 reference，但这是同一模型/候选 reference 范围内的经验关系，不是无需 ground truth 的绝对质量认证。PANDA 还显示 archetypal analysis 是主要内存/时间成本；其优点是每个 tissue/reference 只训练一次，可复用到多个空间数据集。

### 本地代码覆盖与缺口

固定代码快照为 `https://github.com/Zhangxf-ccnu/PANDA` commit `e060b044b5fb019e6bcd7b4195b83f76663185dc`，R package version 1.1.0。

**直接覆盖**：`sc_train/sc_model` 实现参考预处理、archetype 初始化、Poisson MLE 和 all-gene archetype；`st_train/st_model` 实现 gene intersection/HVG、omega 两阶段优化、platform MAP、beta/proportion/alpha 和 cell-type-specific `mu`。九个主文公式与关键补充更新均能映射到 R 源码。

**不在本地包**：pseudo-spot 生成、PCC/RMSE/JSD benchmark、七种比较方法运行、真实组织的 pie plot/聚类/PCA/GO/NicheNet/时序检验。论文将 source、processed data、model results 和 analysis results 分别放在 Zenodo；当前 workspace 只有 reusable R package 与 paper/supplement，不能从本地包一键复现所有图。

**实现细节**：包依赖 Seurat，论文实验固定 4.3.0；乘法更新使用 `eps=1e-12`，soft convex penalty 而非每轮显式 simplex projection；多核默认 20；没有 unit tests 或环境锁文件。重跑应固定 R/Seurat 版本、gene ordering、cell labels 和随机/parallel 设置。

### 使用和解释时的关键边界

1. archetype 是参考细胞凸包的极端表达模式，不是自动发现的真实亚型标签。
2. 若目标组织包含参考中没有的 cell type/state，PANDA 只能用已有 archetype 错配或混合，无法凭空创建缺失状态。
3. `mu` 是 scRNA-derived expression rate signature；它不是实际分配到该类型的 spot UMI count，也不包含估计的 platform correction。
4. 每个 spot 内同一 cell type 被假设共享一个状态；同一 spot 内该类型多个不同亚状态会被压成一个凸组合。
5. 模型不使用坐标，空间连续性来自数据本身而不是邻域正则；噪声 spot 不会自动向邻居借力。
6. reference 选择、cell-type label 粒度、archetype 数和平台偏差会共同影响比例与 signature；likelihood 应与生物 marker、组织结构和其他 reference 对照使用。
7. 下游相关、GO 和 ligand-target 分析建立在估计量上，应传播不确定性并用独立实验验证，不能把解卷积结果直接当作单细胞原位测量。

PANDA 的真正贡献是把“一个类型只有一个固定 signature”的线性反卷积扩展成“每个类型有一个由 archetype 构成的状态空间”，并让每个 spot 在该空间中自适应选择位置。这样比例估计和类型内表达互相约束，得到比单一 composition 更丰富的空间生物学视图；代价是更强的 reference 依赖、更多计算和对估计表达边界更严格的解释要求。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## PANDA - Comprehensive Paper Analysis

### Paper Information

- **Title**: Dual decoding of cell types and gene expression in spatial transcriptomics with PANDA
- **Authors**: Meng-Guo Wang, Luonan Chen, Xiao-Fei Zhang
- **Journal**: Nucleic Acids Research, 52(20), 2024
- **DOI**: 10.1093/nar/gkae876
- **Affiliation**: Central China Normal University; Chinese Academy of Sciences

### Problem Statement

Sequencing-based spatial transcriptomics (ST) technologies (e.g., Visium, ST) profile whole transcriptomes at spot level, but each spot captures a mixture of multiple cells from different cell types. Existing deconvolution methods estimate cell type proportions per spot but ignore **cell-type-specific gene expression**, which is essential for understanding intra-type heterogeneity. Furthermore, most methods use a single fixed signature vector per cell type across all spots, failing to account for the fact that cells of the same type can exist in different transcriptional states depending on spatial context.

### Method Overview

PANDA (ProbAbilistic-based decoNvolution with spot-aDaptive cell type signAtures) simultaneously estimates:
1. **Cell type proportions** ($\beta_{sk}$) for each spot
2. **Cell-type-specific gene expression** ($\mu^{(k)}_{sg}$) for each spot and cell type

#### Two-Step Pipeline

**Step 1: Archetypal Analysis on scRNA-seq Reference**

For each cell type $k$, PANDA identifies $A_k$ archetypes (extreme cell states) from the scRNA-seq reference using probabilistic archetypal analysis under a Poisson model:

$$X^{(k)}_{cg} \sim \text{Poisson}\left(N^{(k)}_c \cdot \sum_{a=1}^{A_k} \alpha^{(k)}_{ca} \left(\sum_{c'=1}^{C_k} W^{(k)}_{ac'} Z^{(k)}_{c'g}\right)\right)$$

where:
- $Z^{(k)}_{c'g} = X^{(k)}_{c'g} / N^{(k)}_{c'}$ is the expression rate
- $W^{(k)}_{ac'}$ are archetype-to-cell coefficients (convex: non-negative, sum to 1)
- $\alpha^{(k)}_{ca}$ are cell-to-archetype coefficients (convex)
- Archetypes: $\varphi^{(k)}_{ag} = \sum_{c'} W^{(k)}_{ac'} Z^{(k)}_{c'g}$

Parameters are estimated by MLE using multiplicative update rules. Initialization uses max-min sampling for diverse archetype seeds, followed by cosine similarity-based initialization of W and alpha.

**Step 2: Deconvolution of ST Data**

The observed spot expression is modeled as:

$$Y_{sg} \sim \text{Poisson}\left(N_s \cdot \sum_{k=1}^K \beta_{sk} \left(\sum_{a=1}^{A_k} \alpha^{(k)}_{sa} \varphi^{(k)}_{ag}\right) \cdot e^{\gamma_g}\right)$$

where:
- $\beta_{sk}$ is the abundance of cell type $k$ in spot $s$ (not constrained to sum to 1)
- $\alpha^{(k)}_{sa}$ are spot-specific archetype weights (convex)
- $\gamma_g \sim \text{Normal}(0, \sigma^2)$ captures gene-specific platform effects
- $\sigma = 0.3 / \sqrt{S}$ by default

The spot-adaptive cell type signature is: $\mu^{(k)}_{sg} = \sum_a \alpha^{(k)}_{sa} \varphi^{(k)}_{ag}$

Cell type proportions are obtained by normalizing $\beta_{sk}$ to sum to 1 per spot.

#### Key Design Choices

1. **Poisson distribution** for count data (both scRNA-seq and ST)
2. **Archetypal analysis** captures the convex hull of each cell type's state space, not just the centroid
3. **Spot-adaptive signatures** allow the same cell type to have different expression profiles at different spots
4. **Two-phase optimization** in deconvolution: first without platform effects, then with (after filtering extreme-ratio genes)
5. **All-gene recovery**: archetypes computed on selected genes, but cell-type-specific expression can be extrapolated to all genes by substituting the full expression rate matrix

#### Preprocessing

- **scRNA-seq**: filter cells with <200 total counts; select union of 2000 HVGs (Seurat vst) and top 20 DE markers per cell type; downsample cell types with >500 cells via max-min sampling
- **ST data**: select top 5000 HVGs from the intersection of ST genes and scRNA-seq genes

### Validation

#### Simulation (scRNA-seq-based)

- **Paired scenario**: reference and pseudo-spots from same dataset (NSCLC scRNA-seq, TISCH)
- **Unpaired scenario**: reference and pseudo-spots from different platforms (PBMC: 10x Chromium v2 vs inDrops)
- **4 settings**: ST-like (10-30 cells/spot) vs Visium-like (1-10 cells/spot), crossed with uniform vs non-uniform (extreme-state-biased) sampling
- **1000 pseudo-spots** per setting
- **Metrics**: PCC, RMSE, JSD (all at spot level, for both proportions and signatures)

#### Simulation (imaging-based)

- MERFISH mouse isocortex data aggregated into pseudo-spots (100 um diameter, 200 um spacing)
- scRNA-seq reference from mouse brain atlas (10x Chromium v2)

#### Compared Methods

cell2location, DestVI, RCTD, SpatialDWLS, SPOTlight, stereoscope, STRIDE (7 methods)

#### Key Results

- PANDA ranked **first** in both cell type proportion and cell type signature estimation across all scenarios and settings
- Statistically significant improvement over second-ranked method in nearly all comparisons (Wilcoxon rank sum test, P <= 0.05)
- In unpaired scenario with batch effects, PANDA maintained superiority while other methods degraded more
- DestVI (also learns spot-specific signatures) performed well on signatures but worse on proportions
- RCTD and cell2location competitive on proportions but limited by fixed signatures

### Applications

#### 1. Cutaneous Malignant Melanoma (ST technology)

- Tissue regions: lymphoid-rich, melanoma-rich, stromal-rich
- PANDA correctly mapped cell types to expected regions (malignant cells in melanoma region, B/T cells in lymphoid region)
- **B cell heterogeneity**: B cells in lymphoid region enriched for proliferation functions; B cells in melanoma region enriched for immune response modulation/differentiation
- **Immune-tumor communication**: identified two gene groups in malignant cells correlated with immune cell proportion (G1: positively correlated, expressed at melanoma border; G2: negatively correlated, expressed in core). NicheNet analysis identified CXCL12-CXCR4 axis and other ligands

#### 2. Mouse Brain (Visium)

- Frontal cortex region of sagittal brain section
- Glutamatergic neurons formed expected layered structure (L2/3 IT -> L4 -> L5 IT -> L6 CT -> L6 IT -> L6b)
- **L2/3 IT heterogeneity**: 3 clusters with layered spatial organization along cortical depth; PC1 of cell-type-specific expression showed significant negative correlation with cortical depth
- **L5 IT heterogeneity**: 4 clusters with layered structure; PC1 showed significant positive correlation with cortical depth
- Colocalization patterns confirmed expected layer relationships

#### 3. Developing Human Heart (ST technology)

- 19 tissue sections across 3 developmental stages (4.5-5, 6.5, 9 PCW)
- Temporal changes: ventricular cardiomyocyte abundance increased; epicardial cells decreased while epicardium-derived cells increased
- **Gene expression dynamics in ventricular cardiomyocytes**: 4 patterns identified (Stable-Increase, Decrease-Increase, Stable-Decrease, Increase-Decrease)
- Stable-Increase and Decrease-Increase patterns enriched for cardiac muscle development functions
- Stable-Decrease pattern enriched for ERK1/ERK2 cascade; Increase-Decrease enriched for nuclear division

### Hyperparameters

| Parameter | Default | Role |
|---|---|---|
| Number of archetypes ($A_k$) | 10 (same for all cell types) | Balance between model complexity and data fidelity |
| $\sigma$ | $0.3/\sqrt{S}$ | Standard deviation of platform effect prior |
| Convergence tolerance | $10^{-8}$ | Relative change threshold |
| Max iterations | 2000 | Per optimization phase |
| n_hvgs (scRNA-seq) | 2000 | Highly variable genes for archetypal analysis |
| n_markers | 20 | DE markers per cell type |
| n_sample_cells | 500 | Max cells per cell type after downsampling |
| n_hvgs (ST) | 5000 | HVGs for deconvolution |

Sensitivity analysis (Supplementary Figures S45-S50) showed robustness across a range of hyperparameter values.

### Limitations

1. **Higher computational cost** for archetypal analysis compared to methods using single signature vectors per cell type (but only needs to run once per tissue type)
2. **Reference dependence**: different scRNA-seq references can yield varying results; likelihood values may serve as a reference selection criterion
3. **Poisson assumption** may not capture overdispersion (negative binomial planned for future work)
4. **No spatial prior**: does not incorporate spatial coordinates, tissue domains, or histological images (future enhancement planned)

### Strengths

1. **Dual output**: simultaneously provides cell type proportions AND cell-type-specific gene expression
2. **Within-cell-type heterogeneity**: archetypal analysis captures the full state space, not just centroids
3. **Spot-adaptive signatures**: each spot gets tailored cell type signatures
4. **All-gene recovery**: can extrapolate cell-type-specific expression to the entire transcriptome
5. **Principled probabilistic framework**: Poisson model with interpretable parameters
6. **Strong empirical performance**: ranked first across all benchmarks

### Reproducibility

- All code and data deposited on Zenodo with separate repositories for: source code, processed data, model results (simulations, sensitivity analysis, applications), and analysis results
- R package available on GitHub with documentation and tutorials
- Experiments based on Seurat v4.3.0

### Key References

- Archetypal analysis: Cutler & Breiman 1994 (original), Seth & Eugster 2016 (probabilistic)
- Compared methods: cell2location (Kleshchevnikov 2022), DestVI (Lopez 2022), RCTD (Cable 2022), SpatialDWLS (Dong 2021), SPOTlight (Elosua-Bayes 2021), stereoscope (Andersson 2020), STRIDE (Sun 2022)
- Applications: melanoma ST (Thrane 2018), mouse brain cortex (Tasic 2016), developing heart (Asp 2019)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
