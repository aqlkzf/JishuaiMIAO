---
layout: default
permalink: /paper-atlas/popari-6557e5f3/
title: "POPARI"
nav: false
description: "多样本空间转录组常需要比较疾病与对照、不同年龄或不同患者。许多整合方法重点消除批次或对齐坐标，但 POPARI 的问题不同：是否能找到一组可解释的共享基因程序，并量化这些程序在每个样本中如何相邻、共现或分隔。 输入是多个样本的表达矩阵、二维坐标和样本分组；空间实体可以是成像平台的细胞，也可以是测序平台的 spots。"
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
      <span>Domain Clustering</span>
      <span>preprint · 2025</span>
    </div>
    <h1>POPARI</h1>
    <p>POPARI: Modeling multisample variation in spatial transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## POPARI：比较多个空间转录组样本中的空间基因程序

### 1. 它回答的不是“把样本对齐到同一坐标”

多样本空间转录组常需要比较疾病与对照、不同年龄或不同患者。许多整合方法重点消除批次或对齐坐标，但 POPARI 的问题不同：是否能找到一组可解释的共享基因程序，并量化这些程序在每个样本中如何相邻、共现或分隔。

输入是多个样本的表达矩阵、二维坐标和样本分组；空间实体可以是成像平台的细胞，也可以是测序平台的 spots。输出包括共享 metagenes、每个实体的非负权重、每个样本的空间交互能量矩阵，以及由此派生的 accordance、趋势和样本聚类。

### 2. 共享 metagene 分解

对样本 $t$：

$$
Y^t=MX^t+E^t.
$$

$Y^t\in\mathbb R_+^{G\times N_t}$ 是表达，$M\in\mathbb R_+^{G\times K}$ 的每一列是一个 metagene，$X^t\in\mathbb R_+^{K\times N_t}$ 是实体权重。$M$ 在样本间共享，使同一列可以跨样本比较；$X^t$ 保留每个样本的空间分布。

代码默认把 $M$ 的每列投影到 simplex，即非负且和为 1。这消除了 $M$ 放大、$X$ 缩小但乘积不变的尺度歧义，也使列内基因权重易于排序。公开代码还支持 `metagene_mode="differential"`，但论文主叙事和构造器默认都是共享 metagenes。

### 3. 空间图与交互能量

论文用坐标做 Delaunay 三角剖分，再按距离阈值删除异常长边。代码 `PopariDataset.compute_spatial_neighbors()` 实现相同思路，默认以 Delaunay 边距离的 94.5 百分位作为截断。

对邻居 $(i,j)$，先归一化 $x_i$ 与 $x_j$ 的 L1 范数，再计算：

$$
U_x(x_i^t,x_j^t)=z_i^{t\top}\Lambda^t z_j^t.
$$

关键是概率势为 $\exp(-U_x)$。所以：

- $\Lambda_{kl}>0$ 会提高两个 metagenes 相邻的能量，降低该邻接配置概率；
- $\Lambda_{kl}<0$ 会降低能量，更接近“正向亲和/共现”；
- 论文图 3 因而画 $-\Delta\Lambda$ 来让正值直观表示增加的亲和。

代码把这一参数命名为 `Sigma_x_inv` 或 spatial affinity。阅读结果时必须记住它在数学上是能量/精度型参数，原始符号的正负方向与日常“affinity 越大越相吸”的语言相反。

### 4. 为什么需要 differential prior

完全共享一个 $\Lambda$ 会抹掉样本差异；每个样本独立拟合又容易把噪声当差异。POPARI 让每个样本拥有 $\Lambda^t$，并使用两项 Gaussian 型先验：

$$
\lambda_\Lambda\lVert\Lambda^t\rVert_F^2,
\qquad
\lambda_{\bar\Lambda}\lVert\Lambda^t-\bar\Lambda\rVert_F^2.
$$

第一项抑制极端能量，第二项把样本拉向组均值。`lambda_Sigma_x_inv` 对应幅度惩罚，`lambda_Sigma_bar` 对应样本差异收缩。

但 v1.3.4 构造器默认 `spatial_affinity_mode="shared lookup"`，不会自动为每个重复学习独立矩阵。要执行论文重点强调的差异分析，必须显式设置 `"differential lookup"`，定义正确的 `spatial_affinity_groups`，或使用 `from_pretrained()` 从共享模型转换。默认运行不等同于论文差异模式。

### 5. 交替优化

训练先做若干 NMF preiterations：更新 $M$、噪声和 $X$，但关闭空间矩阵并忽略邻居。随后进入空间阶段，交替执行：

1. 用 Adam 更新每组/每样本 `Sigma_x_inv`；
2. 用带 Nesterov 加速的投影优化更新 $M$；
3. 闭式更新表达噪声；
4. 用带非负约束的坐标下降更新 $X$。

空间矩阵优化还计算 simplex 上指数函数的配分函数近似/积分，这是普通“在 NMF 后加一个邻接正则”没有的概率模型部分。代码提供边子采样和独立集更新来降低计算成本。

### 6. 层级分辨率：论文公式与代码运行方式

低分辨率表达通过 bin assignment $B_h$ 求和：

$$
Y_h=Y_{h-1}B_h.
$$

论文把每层的 $M_h,X_h^t,\Lambda_h^t$ 都写入层级模型。代码的实际执行更具体：构造整个 hierarchy 后，把最粗层设为 active/base view，在该层完成主训练；调用 `superresolve()` 时，再把参数从粗层向细层传播，逐级优化高分辨率 $X$，随后可重新估计该层空间矩阵。

因此 POPARI 的 multiscale 是**粗到细的级联估计**，不是所有分辨率在每一步同时联合更新。并且默认 `hierarchical_levels=1`，若不显式增加层数，就没有层级下采样。

### 7. Accordance 不是直接观测到的细胞互作

POPARI 的 accordance 衡量学习到的 metagene 能量与空间图边上权重模式的一致程度。置换 $X$ 可以建立 null distribution，再把 metagene层面的信号汇总到细胞类型或空间域。

它描述统计空间邻近/排斥，不证明配体–受体作用、物理接触因果或疾病机制。AD、胸腺与卵巢癌案例通过病理蛋白、TCR 和已知 gene sets 提供外部一致性，但仍应称“关联”或“空间组织变化”。

### 8. 五幅主图

- 图 1：共享 $M$、样本特异 $X^t/\Lambda^t$、层级下采样及下游 accordance/趋势分析。
- 图 2：20 个模拟重复、每次取五个初始化中的最佳结果；POPARI 在 mSWD 和 ASC 上占优。这个 best-of-five 设计应保留在复现说明中。
- 图 3：STARmap PLUS AD 数据；8 月龄的胶质细胞 accordance 和 $-\Delta\Lambda$ 变化更强，metagene 与 Aβ/p-tau 空间模式相关。
- 图 4：Slide-TCR-seq 胸腺时间序列；展示 metagene pair 的年龄趋势和 TCR V(D)J/增殖程序变化。
- 图 5：CosMx 卵巢癌；用 metagene gene-set overlap、样本 $\Lambda$ 相关与组织图比较患者间 malignant–immune compartmentalization。

### 9. 论文—代码匹配和复现边界

核心公式、Delaunay 图、simplex、交替 MAP、差异先验、层级 binning、模拟与下游分析都有直接实现，匹配度为 **High/Partial**。之所以不是完全 Exact：本地只能确认 v1.3.4、没有上游 commit；默认 shared affinity 不直接等于论文 differential 配置；层级执行是 coarse-first superresolution；部分真实数据预处理与超参数依赖论文补充材料。

正式复现至少记录：共同基因集合、表达缩放、Delaunay 截断、$K$、初始化与 seed、NMF/空间迭代数、模式与 group mapping、两个正则强度、层数、downsample rate、backend，以及是否报告 best-of-five。

### 源证据

- 论文与主图：`paper source/Alam et al. - 2025 - Popari Modeling multisample variation in spatial transcriptomics/`
- 模型/训练：`popari/model.py`、`popari/train.py`
- 参数与嵌入优化：`popari/_parameter_optimizer.py`、`popari/_embedding_optimizer.py`
- 层级与空间图：`popari/_hierarchical_view.py`、`popari/_popari_dataset.py`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## POPARI Summary

### Answer First

POPARI is an interpretable multisample spatial-transcriptomics model built from nonnegative matrix factorization and a spatial hidden Markov random field. It learns metagenes shared across samples, nonnegative sample-specific entity embeddings, and metagene interaction-energy matrices for each sample. A differential prior shrinks sample-specific matrices toward a group mean, while hierarchical spatial binning supports coarse-to-fine analysis.

The local source is package v1.3.4 and strongly matches the paper's core factorization, Delaunay spatial graph, alternating MAP updates, differential regularization and downstream analyses. Fidelity is **high at the mechanism level**, with important operational differences: the constructor defaults to shared rather than differential spatial affinities, and hierarchy is trained coarse-first then superresolved rather than jointly optimizing every resolution at once.

### Model

For sample $t$, POPARI decomposes expression as:

$$Y^t=MX^t+E^t,$$

where columns of shared $M$ are simplex-constrained metagenes and $X^t$ contains nonnegative entity weights. A Delaunay graph with distance pruning defines spatial neighbors. For an edge $(i,j)$, normalized embeddings interact through an energy matrix $\Lambda^t$:

$$U_x(x_i^t,x_j^t)=z_i^{t\top}\Lambda^t z_j^t,\qquad z_i^t=x_i^t/\lVert x_i^t\rVert_1.$$

Because the probability contains $\exp(-U_x)$, a positive matrix entry raises energy and discourages adjacency; negative values correspond to positive association. This is why paper figures often plot $-\Delta\Lambda$. Calling raw $\Lambda$ an “affinity” without this sign convention is misleading.

### Optimization and hierarchy

Training alternates metagene, spatial-energy/noise and embedding updates. The implementation begins with NMF-only preiterations, then enables spatial updates. Metagenes use projected optimization, embeddings use projected coordinate descent with acceleration, spatial matrices use Adam, and noise has a closed-form update.

At multiple resolutions, expression is summed into spatial bins. The v1.3.4 implementation activates the coarsest level for main fitting, propagates parameters downward, and superresolves embeddings from coarse to fine. Thus “multiscale” does not mean every level is optimized simultaneously in one objective call.

### Evidence

Simulation Figure 2 reports improved recovery under structured dropout and sample variation, evaluated with spatial Wasserstein distance and affinity Spearman correlation over 20 replicates, selecting the best of five initializations. Real-data applications cover eight STARmap PLUS AD sections (72,165 cells), five Slide-TCR-seq thymus ages, and 27 CosMx ovarian-cancer samples (161,962 cells). These demonstrate metagene/pathology associations, temporal interaction trends and patient-specific malignant–immune compartmentalization. They are application evidence, not causal validation of inferred interactions.

### Reproducibility

Rating: **4/5**. The package, tests, tutorials, simulation code and analysis utilities are present. Exact manuscript reproduction still depends on supplement-specific preprocessing and hyperparameters, unavailable upstream commit provenance, and best-of-five initialization selection in simulations. The workspace records v1.3.4 but not an immutable Git commit.

Important defaults are `lambda_Sigma_x_inv=1e-4`, `lambda_Sigma_bar=1e-3`, `hierarchical_levels=1`, `spatial_affinity_mode="shared lookup"`, `metagene_mode="shared"`, `binning_downsample_rate=0.2`, and `random_state=0`. Old documentation claiming fixed GPU time/memory numbers was not retained because those values were not verified from the manuscript evidence.

### Evidence pointers

- Paper: `paper source/Alam et al. - 2025 - Popari Modeling multisample variation in spatial transcriptomics/Alam et al. - 2025 - Popari Modeling multisample variation in spatial transcriptomics.md`
- Figures: same directory, `_page_*_Figure_1.jpeg`
- Model/training: `popari/model.py`, `popari/train.py`
- Optimizers: `popari/_parameter_optimizer.py`, `popari/_embedding_optimizer.py`
- Hierarchy/graphs: `popari/_hierarchical_view.py`, `popari/_popari_dataset.py`

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
