---
layout: default
permalink: /paper-atlas/banksy-03c9163e/
title: "BANKSY"
nav: false
wide: true
description: "BANKSY 不把空间坐标直接塞进聚类，而是先为每个细胞或 spot 计算其局部邻域的表达均值和表达梯度，再把这些邻域特征与该点自身的表达拼接。这样，两个自身转录组相近、但处在不同组织微环境中的细胞，可以在新特征空间中被分开。 本文证据来自本地论文正文 outputnollmmathtables/paper/paper.md、主图 1–6，以及本工作区 R 包的 R/computation.R、R/reduction."
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
      <span>Nature Genetics · 2024</span>
    </div>
    <h1>BANKSY</h1>
    <p>BANKSY unifies cell typing and tissue domain segmentation for scalable spatial omics data analysis</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41588-024-01664-3" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for BANKSY">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/prabhakarlab/Banksy" target="_blank" rel="noopener noreferrer" aria-label="Open code for BANKSY">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## BANKSY：把“邻居的表达”变成可聚类特征

### 一句话理解

BANKSY 不把空间坐标直接塞进聚类，而是先为每个细胞或 spot 计算其局部邻域的表达均值和表达梯度，再把这些邻域特征与该点自身的表达拼接。这样，两个自身转录组相近、但处在不同组织微环境中的细胞，可以在新特征空间中被分开。

论文分析脚本位于另一个公开仓库，未包含在本地快照中，因此本文区分“论文展示的结果”和“当前 R 包可直接验证的算法实现”。

### 问题与输入输出

输入是一个基因×细胞（或 spot）的表达矩阵，以及每个观测的二维或多维空间坐标。输出不是一种新的表达量，而是：

1. 邻域谐波矩阵 `H0`, `H1`, ...；
2. 按空间权重 $\lambda$ 拼接的 BANKSY 矩阵；
3. 该矩阵的 PCA/UMAP 表示和聚类标签。

目标有两种。小 $\lambda$ 主要保留自身表达，用于带空间信息的细胞类型聚类；大 $\lambda$ 强化邻域组成，用于组织结构域分割。$\lambda=0$ 时退化为非空间聚类，而不是仍然偷偷使用坐标。

### 核心表示

设第 $i$ 个细胞的基因表达向量为 $x_i$，空间邻居为 $j\in N(i)$，归一化距离核权重为 $w_{ij}$，邻居相对方向为 $\phi_{ij}$。

零阶谐波（局部均值）为

$$
H_i^{(0)}=\left|\sum_{j\in N(i)}w_{ij}x_j\right|.
$$

一阶谐波（论文称 AGF）为

$$
H_i^{(1)}=\left|\sum_{j\in N(i)}w_{ij}x_j e^{\mathrm{i}\phi_{ij}}\right|.
$$

$e^{\mathrm{i}\phi}$ 把邻居方向编码为复数相位；最后取模，使一阶特征反映邻域表达梯度强度，而不依赖样本整体旋转方向。代码中的 `computeNeighbors()` 先计算边、权重和 `phi`，`computeHarmonics()` 再执行上述复数加权求和并取 `abs()`。当 `M>1` 时，包还能计算更高阶的角向谐波；论文主方法重点是 $H^{(0)}$ 与 $H^{(1)}$。

当前默认 `spatial_mode="kNN_median"`、`k_geom=15`。这只是包默认值；代码还实现了按秩、距离、均匀权重和半径高斯等邻域模式，不能把“高斯核”误写成唯一实现。

### $\lambda$ 怎样真正进入距离

`getLambdas()` 不直接以 $\lambda$ 乘整个邻域块，而是先分配平方距离贡献，再开平方作为特征缩放系数。仅使用 $H^{(0)}$ 时，拼接矩阵是

$$
B_i=\begin{bmatrix}
\sqrt{1-\lambda}\,x_i\\
\sqrt{\lambda}\,H_i^{(0)}
\end{bmatrix}.
$$

同时使用 $H^{(0)}$ 和 $H^{(1)}$ 时，代码把邻域权重按 $1:1/2$ 归一化，因此

$$
B_i=\begin{bmatrix}
\sqrt{1-\lambda}\,x_i\\
\sqrt{2\lambda/3}\,H_i^{(0)}\\
\sqrt{\lambda/3}\,H_i^{(1)}
\end{bmatrix}.
$$

这与图 1 标出的三个系数一致。一个小例子：$\lambda=0.2$ 且使用 AGF 时，自身、均值、梯度块的系数约为 $0.894,0.365,0.258$。因欧氏距离会平方这些系数，三块对平方距离的名义贡献为 $0.8,0.133,0.067$。

`runBanksyPCA()` 默认先逐基因标准化各块，再构造 BANKSY 矩阵，删除零方差行，用 `irlba` 求主成分。`clusterBanksy()` 默认在 PCA 空间构造近邻/sNN 图并运行 Leiden；也提供 Louvain、k-means 和 Mclust。论文的“统一框架”因此不是同一个生成模型同时拟合细胞类型和组织域，而是同一个特征构造与聚类流水线通过改变 $\lambda$ 切换任务侧重点。

### 从左到右读完整代码路径

1. `computeBanksy()` 从 `SpatialExperiment` 的 `spatialCoords` 或指定坐标列取位置，从 assay 取表达。
2. `computeNeighbors()` 建立空间邻域，保存 `from`, `to`, `weight`, `phi`。
3. `computeHarmonics()` 逐基因聚合邻居，得到 `H0/H1/...` assay；大数据可按基因分块，并在非 Windows 系统使用 `BiocParallel`。
4. `getBanksyMatrix()` 可按样本组分别 z-score，再按 $\lambda$ 缩放并纵向拼接自身与谐波矩阵。
5. `runBanksyPCA()` 生成名为 `PCA_M{M}_lam{lambda}` 的表示。
6. `clusterBanksy()` 对参数组合逐一聚类，把标签写入 `colData`；默认算法是 Leiden。

UMAP 是可视化步骤，不是获得最终聚类的必要条件。`smoothLabels()` 也是可选后处理，不应被描述为 BANKSY 核心目标函数的一部分。

### 论文图证据说明了什么

- 图 1 给出方法机制：邻域均值补充微环境，AGF 补充方向梯度，$\lambda$ 决定三块比例。
- 图 2 在 Slide-seq 小鼠小脑中显示 BANKSY 得到更连续的层状细胞类型，并与监督式 RCTD 权重及 marker 图更一致；这是外部参照比较，不等于获得绝对真值。
- 图 3 展示 MERFISH 中空间分离的成熟少突胶质细胞亚群，以及 MERSCOPE 肿瘤中非空间聚类遗漏的增殖上皮群；独立 scRNA-seq 分群是支持证据，但使用了由空间结果选择的 DEG 和关联基因。
- 图 4 在 VeraFISH 海马周边比较多个方法，BANKSY 分开 CA3/SSC 神经元和 fornix/thalamic 少突胶质细胞；图中的空间位置、DEG 与独立 scRNA-seq 共同支持，而不是单靠“簇更平滑”。
- 图 5 表明大 $\lambda$ 的域分割在 DLPFC 上与 GraphST、STAGATE处于同一领先组，论文明确报告三者中位 ARI 无显著差异；STARmap 示例中 BANKSY 的 ARI 为 0.720。
- 图 6 的 16 CPU、128 GB 基准显示 BANKSY 可运行到 200 万细胞且约小时量级。它支持该实验条件下的可扩展性，不证明任意硬件或任意基因数下都保持同样速度。

### 论文—代码对应评估

**总体：High，但不是端到端完全复现。**

Exact：邻域图、角度、$H0/H1$、取模、$\lambda$ 权重、PCA、Leiden/Louvain/k-means/Mclust 和参数扫描均能在本地 R 源码中直接找到；图 1 的系数与 `getLambdas()` 一致。

Partial：论文说“AGF 具有旋转不变性”，代码通过复相位求和后取模实现这一性质；但完整数学证明不在包源码中。论文的默认分析设置与包当前版本默认值总体一致，但发表分析可能固定了更具体的数据集参数。

Not found：图 2–6 的数据下载、预处理、基准调参、DEG/guilt-by-association 分析和绘图脚本不在本地 R 包快照中。论文指向独立的 `jleechung/banksy-zenodo` 分析仓库；本次未获取该仓库，因此不能声称已从当前目录端到端重现主图数值。

### 使用时最容易犯的错误

- 不要把 BANKSY 说成“把 x/y 坐标与表达直接拼接”；它拼接的是由坐标定义的邻域表达特征。
- 不要把 AGF 的复数实部和虚部直接当最终特征；实现最终保存的是复加权和的模。
- 不要把小 $\lambda$ 等同于纯细胞类型真值。它仍会使用微环境，可能把同一细胞类型在不同环境中的状态拆开。
- 不要只凭空间连续性判断更准确。组织中也存在相互混合或远距离重复的细胞类型，论文因此结合 marker、外部标签、独立 scRNA-seq 和人工域注释。
- 选择 $\lambda$、邻域大小、聚类分辨率和目标簇数仍是分析者责任；统一框架并没有消除模型选择。

### 证据边界

本地 `paper.md` 是从 PDF 转换的文本，少数图注在分页处顺序错位；主图判断已同时查看原始提取图像。没有本地补充材料 Markdown，也没有论文分析仓库快照。当前结论可支持方法机制、R 包调用链和论文主图的谨慎解读，但不能支持“所有数据集均可一键复现”的结论。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## BANKSY Summary

**Paper:** BANKSY unifies cell typing and tissue domain segmentation for scalable spatial omics data analysis

**Journal/year:** Nature Genetics, 2024

**DOI:** 10.1038/s41588-024-01664-3

BANKSY represents each cell or spot by its own molecular profile plus spatial-neighborhood expression features. The zero-order feature is a weighted local mean; the first angular harmonic (AGF) measures neighborhood expression-gradient magnitude. A mixing parameter $\lambda$ controls how much these spatial features contribute: $\lambda=0$ is nonspatial clustering, lower positive values favor spatially informed cell typing, and higher values favor tissue-domain segmentation.

The local R package implements the paper's central feature construction and clustering path: `computeBanksy()` → `getBanksyMatrix()` → `runBanksyPCA()` → `clusterBanksy()`. Leiden is the default, with Louvain, k-means and Mclust alternatives. The implementation supports chunked neighborhood computation and multiple kernel modes.

Across the paper's main figures, BANKSY improves agreement with RCTD/marker patterns in Slide-seq cerebellum, identifies microenvironment-associated subtypes in MERFISH/MERSCOPE/VeraFISH data, performs competitively on annotated DLPFC domains, achieves the highest shown ARI in a STARmap example, and scales to two million cells in the authors' 16-CPU/128-GB benchmark. These claims are dataset- and benchmark-specific; DLPFC results do not show a significant difference among BANKSY, GraphST and STAGATE.

### Reproducibility assessment

The method-to-code match is **High** for the core R algorithm: neighborhood weights and angles, harmonic aggregation, $\lambda$ weighting, PCA and clustering are directly traceable. It is not an end-to-end figure reproduction package. The paper points to a separate analysis repository (`jleechung/banksy-zenodo`) for processed-data analyses and figures; that repository is not present here. Consequently, the principal mechanism is locally verifiable, while figure-specific preprocessing, tuning and numerical outputs remain paper-reported evidence.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
