---
layout: default
permalink: /paper-atlas/cna-9ba6abba/
title: "CNA"
nav: false
description: "CNA（co-varying neighborhood analysis）面向多样本单细胞数据。它关心的问题不是单个细胞如何聚类，而是“哪些细胞状态在不同样本之间丰度变化，并且这种变化是否和样本级表型相关”。样本级表型可以是疾病状态、临床指标、基因型、年龄、性别、季节、祖源或实验条件。论文指出，常见做法先把细胞聚成离散簇，再检验每个簇的丰度是否和表型相关；这种做法依赖预先给定的聚类结构和分辨率，可能把连续或跨簇的生物信号切碎或抹平。"
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
      <span>Machine Learning Algorithm</span>
      <span>Nature Biotechnology · 2022</span>
    </div>
    <h1>CNA</h1>
    <p>Co-varying neighborhood analysis identifies cell populations associated with phenotypes of interest from single-cell transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-021-01066-4" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CNA">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/immunogenomics/cna" target="_blank" rel="noopener noreferrer" aria-label="Open code for CNA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CNA 方法中文解读

### 这篇文章要解决什么问题

CNA（co-varying neighborhood analysis）面向多样本单细胞数据。它关心的问题不是单个细胞如何聚类，而是“哪些细胞状态在不同样本之间丰度变化，并且这种变化是否和样本级表型相关”。样本级表型可以是疾病状态、临床指标、基因型、年龄、性别、季节、祖源或实验条件。论文指出，常见做法先把细胞聚成离散簇，再检验每个簇的丰度是否和表型相关；这种做法依赖预先给定的聚类结构和分辨率，可能把连续或跨簇的生物信号切碎或抹平（`paper source/nature_html/paper.md:21-24`）。

CNA 的核心思想是：不要先固定一个全局聚类，而是在细胞图上定义大量细粒度、概率性的转录邻域；然后用这些邻域在各个样本中的丰度组成矩阵，再从矩阵中学习“哪些邻域一起变多或变少”。论文把这种矩阵叫 NAM（neighborhood abundance matrix），即“邻域丰度矩阵”（`paper source/nature_html/paper.md:33-53`）。

### 输入、输出和基本假设

**输入。**

- 一个已经质控、必要时已做批次校正的单细胞矩阵 \(X\)，有 \(M\) 个细胞和 \(G\) 个特征（`paper source/nature_html/paper.md:231-235`）。
- 一个细胞-细胞相似性图 \(A\)，通常来自表达 PCA、CCA、多模态表示或其他用户选择的低维表示（`paper source/nature_html/paper.md:36-36`, `paper source/nature_html/paper.md:233-235`）。
- 每个细胞所属的样本 ID。
- 可选的批次、协变量、donor ID，以及要检验的样本级表型 \(y\)。

**输出。**

- 样本 x 邻域的 NAM 矩阵 \(Q\)。
- NAM 的主成分：样本侧 loadings、邻域侧 loadings，以及对应的方差/奇异值信息。
- 一个全局关联 p 值：单细胞数据整体是否与 \(y\) 相关。
- 每个邻域的局部系数和经验 FDR：哪些细胞邻域驱动了全局关联。

### 计算流程

```text
单细胞矩阵 + 细胞图 + 样本 ID
        |
        v
在图上加 self-loop，扩散样本指示矩阵
        |
        v
选择随机游走步数 s，构建 NAM
        |
        v
去除强批次邻域，残差化批次和协变量
        |
        v
对标准化 NAM 做 SVD/PCA，得到 NAM-PC
        |
        v
全局检验：用前 k 个 NAM-PC 预测样本表型，并用置换估计 p 值
        |
        v
局部检验：计算邻域系数和经验 FDR，定位关联细胞群
```

### 第一步：在细胞图上定义概率邻域

论文对每个细胞定义一个锚定邻域。另一个细胞 \(m'\) 属于锚点细胞 \(m\) 的邻域的程度，由随机游走从 \(m'\) 出发、经过 \(s\) 步到达 \(m\) 的概率给出（`paper source/nature_html/paper.md:237-255`）。

单步转移概率为：

$$\tilde A_{m\prime ,m}: = \frac&#123;&#123;\left( {I + A} \right)_{m\prime ,m}}}&#123;&#123;1 + \Sigma _{m\prime\prime }A_{m\prime ,m\prime\prime }}}.$$

\(s\) 步邻域归属概率为：

$$P^s_{m\prime \to m}: = \left( {e^{m\prime }} \right)^T\tilde A^se^m.$$

**代码实现。** `get_connectivity` 从 AnnData/Scanpy 对象读取邻接图（`cna/src/cna/tools/_nam.py:12-19`）。`diffuse_stepwise` 每一步都用稀疏矩阵传播样本指示矩阵，并通过 `self_weight` 加入 self-loop（`cna/src/cna/tools/_nam.py:21-34`）。代码不是显式计算 \(\tilde A^s\)，而是逐步迭代传播，这和论文“可用迭代稀疏矩阵乘法快速计算”的说法一致（`paper source/nature_html/paper.md:270-270`）。

### 第二步：构建 NAM

论文先定义样本 \(n\) 对邻域 \(m\) 的期望细胞数：

\(R_{n,m}: = \sum_{m' \in C(n)} P^s_{m' \to m}\)。

然后按行归一化：

$$Q_{n,m} = \frac&#123;&#123;R_{n,m}}}&#123;&#123;{\Sigma}_mR_{n,m}}}.$$

这样得到的 \(Q\) 是样本 x 邻域矩阵，每个元素代表某个样本在某个转录邻域中的相对丰度（`paper source/nature_html/paper.md:261-267`）。

**代码实现。** `_nam` 用 `pd.get_dummies(data.obs[sid_name])` 构建细胞 x 样本的 one-hot 指示矩阵，统计每个样本的细胞数 `C`，扩散这个指示矩阵，再计算 `snorm = (s / C).T` 得到样本 x 邻域矩阵（`cna/src/cna/tools/_nam.py:51-76`）。公开接口 `nam` 会进一步做批次邻域 QC，并返回过滤后的 NAM 和保留邻域的布尔掩码（`cna/src/cna/tools/_nam.py:180-194`）。

### 第三步：自动选择随机游走步数

论文希望 \(s\) 足够小，以保留细粒度邻域；但也不能太小，否则邻域可能只由少数样本主导。因此它用 NAM 每列的 kurtosis 来衡量“是否被少数样本支配”，并随着扩散步数增加观察 median kurtosis 是否下降。论文说停止条件是 median kurtosis 小于 8，或相邻步数之间下降少于 3（`paper source/nature_html/paper.md:273-276`）。

**代码实现和差异。** `_nam` 中确实逐步计算 median kurtosis，并在至少 3 步之后，如果 `prevmedkurt - medkurt < 3` 就停止（`cna/src/cna/tools/_nam.py:56-71`）。但在当前克隆的代码里，没有找到论文所述的显式 median kurtosis `< 8` 停止分支。因此这一点是部分匹配，而不是完全逐字实现。

### 第四步：去除批次主导的邻域，并残差化协变量

如果有批次信息，论文先把 NAM 按批次取平均，形成批次 x 邻域矩阵，再删除批次 kurtosis 过高的邻域；之后还会在线性模型框架中继续控制批次和协变量（`paper source/nature_html/paper.md:279-288`）。

**代码实现。** `_batch_kurtosis` 计算每个批次的 NAM 均值后再做 kurtosis（`cna/src/cna/tools/_nam.py:78-82`）。`_qc_nam` 设置阈值 `max(6, 2*np.median(kurtoses))`，保留低于阈值的邻域（`cna/src/cna/tools/_nam.py:84-99`）。这里代码比论文多了一个下限 6。

残差化由 `_resid_nam` 完成。没有批次或只有一个批次时，代码用普通线性投影去掉协变量；有多个批次时，它对批次做 one-hot 编码，把批次和协变量拼接起来，并在一组预设 ridge 参数中搜索，直到残差 NAM 的 median batch kurtosis 达到 `<= 6`（`cna/src/cna/tools/_nam.py:118-157`）。同一个残差化矩阵 `M` 也会用于表型 \(y\)，所以 NAM 和表型在同样的协变量空间中进行关联检验（`cna/src/cna/tools/_association.py:50-61`, `cna/src/cna/tools/_association.py:69-83`）。

### 第五步：对 NAM 做 PCA/SVD

论文对标准化后的 NAM 做分解：

$$\bar Q = UDV^T.$$

其中 \(U\) 是样本侧 loadings，表示每个样本有多强地呈现某个邻域共变模式；\(V\) 是邻域侧 loadings，表示哪些邻域共同构成这个模式（`paper source/nature_html/paper.md:291-300`）。

**代码实现。** `svd_nam` 先按列中心化和标准化 NAM，然后对 `NAM.dot(NAM.T)` 做 SVD/特征分解式计算，再用 `V = NAM.T.dot(U) / np.sqrt(svs)` 得到邻域侧 loadings（`cna/src/cna/tools/_nam.py:101-115`）。需要注意，代码变量 `svs` 对应的是样本-样本 Gram 矩阵的特征值，也就是常规 SVD 记法中的平方奇异值；理解论文里的 \(D\) 时不能把变量名一一硬套。

### 第六步：全局关联检验

论文用前 \(k\) 个 NAM-PC 的样本 loadings 预测样本表型 \(y\)：

$$y = U^k\beta ^k + {\it{\epsilon }}.$$

它会尝试多个 \(k\)，选择 F-test p 值最小的 \(k^*\)，然后对 \(y\) 在批次内置换，重复整个选择过程，得到经验全局 p 值（`paper source/nature_html/paper.md:309-327`）。

**代码实现。** `_association` 会标准化 \(y\)，自动生成 `ks` 网格，针对每个 \(k\) 做投影回归和 F-test，选择最小 p 值对应的 \(k\)（`cna/src/cna/tools/_association.py:20-67`）。之后它用 `conditional_permutation` 在批次内置换，或在提供 donor ID 时用 `grouplevel_permutation` 做 donor-level 置换（`cna/src/cna/tools/_association.py:79-88`, `cna/src/cna/tools/_stats.py:4-32`）。最终的全局 p 值是零假设中比观测 p 值更小或相等的比例，并加一做有限置换校正。

### 第七步：局部关联和 FDR

论文中，局部系数写成：

$$\gamma : = V^{k^ \ast }D^{k^ \ast }\beta ^{k^ \ast }.$$

也就是说，它用秩 \(k^*\) 的 NAM 表示来平滑每个邻域与表型的相关性，然后用置换得到零分布并估计经验 FDR（`paper source/nature_html/paper.md:330-339`）。

**当前代码的重要差异。** 当前克隆的代码把最终暴露的邻域系数计算为 `ncorrs = (ycond[:,None]*NAMresid).mean(axis=0)`，即残差化后全秩 NAM 与残差化表型的相关式均值（`cna/src/cna/tools/_association.py:76-78`）。局部 FDR 也基于全残差 NAM 的零假设系数 `nullncorrs` 计算（`cna/src/cna/tools/_association.py:90-120`, `cna/src/cna/tools/_stats.py:64-83`）。包 README 解释过，0.1.6 之后为了修正特殊数据中局部检验的轻微校准问题，局部系数改用 full-rank NAM，而全局检验不受影响（`cna/README.md:21-23`）。

因此，理解论文概念时可以把 F006 视为“用低秩 NAM-PC 平滑得到邻域效应”；理解当前代码结果时，应记住输出到 `AnnData.obs[key_added]` 的是 `ncorrs`，不是直接暴露的论文 \(\gamma\) 向量（`cna/src/cna/tools/_association.py:227-242`）。

### 论文结果说明了什么

仿真实验显示，CNA 对纯簇丰度信号的 power 与聚类方法接近，但对全局表达程序和簇内表达程序信号有更好的 power 和 signal recovery（`paper source/nature_html/paper.md:68-88`）。Fig. 2 的本地图片也支持这一点：蓝色 CNA 曲线在表达程序相关列明显高于绿色聚类曲线。

真实数据分析给出三个例子：

- RA/OA 滑膜成纤维细胞：NAM-PC1 对应 Notch activation 梯度，并能在 lining/sublining 簇内部继续分辨 RA 相关细胞（`paper source/nature_html/paper.md:91-114`）。
- Sepsis PBMC：CNA 找到全局 sepsis 关联和跨 MS1/MS2/MS3/MS4 的单核细胞相关群体，而单独 MS1 簇检验不显著（`paper source/nature_html/paper.md:120-146`）。
- TB 记忆 T 细胞：NAM-PC 能捕捉 innateness、性别、多模态一致结构，并发现 TB progression、年龄、季节、祖源等多个样本级属性对应的细胞群（`paper source/nature_html/paper.md:152-198`）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CNA Summary

### What Problem It Solves

Co-varying neighborhood analysis (CNA) is designed for multi-sample single-cell datasets where the biological question is about a sample-level attribute: disease status, clinical phenotype, genotype, season, age, sex, ancestry, experimental condition, or another per-sample variable. The paper argues that common workflows cluster cells first and then test cluster abundances, which makes results depend on a pre-specified transcriptional partition and often on clustering-resolution tuning (`paper source/nature_html/paper.md:21-24`).

CNA replaces that discrete cluster-first view with a fine-grained, graph-neighborhood view. Each cell anchors a probabilistic neighborhood in the cell-cell similarity graph. The method then asks which neighborhoods co-vary in abundance across samples and whether those co-varying abundance patterns associate with a sample-level attribute (`paper source/nature_html/paper.md:33-53`).

### Core Method

CNA starts from a nearest-neighbor graph over all cells. It adds self-loops, diffuses sample membership through the graph, and builds a neighborhood abundance matrix (NAM), whose rows are samples and whose columns are cell-anchored neighborhoods (`paper source/nature_html/paper.md:237-267`). It chooses the random-walk length using NAM-column kurtosis so that neighborhoods remain granular but are not dominated by a few samples (`paper source/nature_html/paper.md:273-276`).

After optional batch-neighborhood filtering and sample-level covariate residualization, CNA performs PCA/SVD on the standardized NAM (`paper source/nature_html/paper.md:279-300`). NAM-PC sample loadings describe how strongly each co-varying neighborhood pattern appears in each sample; NAM-PC neighborhood loadings describe which neighborhoods define the pattern.

For a phenotype vector \(y\), CNA fits linear models of \(y\) on the first \(k\) NAM-PC sample loadings, chooses \(k\) by the smallest F-test p-value, and estimates a global association p-value using empirical nulls produced by within-batch permutations (`paper source/nature_html/paper.md:309-327`). It then estimates local neighborhood coefficients and empirical FDRs to identify the cell populations driving the global association (`paper source/nature_html/paper.md:330-339`).

### Evaluation and Main Results

The paper evaluates CNA against a cluster-based comparator using simulated attributes in real single-cell data. In the main simulations, CNA is similar to clustering for pure cluster-abundance signals but has better power and signal recovery for global and cluster-specific expression-program signals (`paper source/nature_html/paper.md:68-88`). The local Fig. 2 image supports this visually: CNA's blue curves are comparable to clustering for causal clusters and higher for expression-program power/recovery in the global and cluster-specific columns (`figure_analysis.md`).

The real-data analyses show why the neighborhood view matters:

- In rheumatoid arthritis synovial fibroblasts, NAM-PC1 tracks Notch activation more strongly than pseudotime or naive gene-expression PC1 and reveals within-cluster variation in RA-associated cells (`paper source/nature_html/paper.md:91-114`).
- In sepsis PBMCs, CNA finds a significant global sepsis association and monocyte subpopulations spanning multiple published clusters, whereas an MS1 cluster-level test is not significant in the paper's aggregate comparison (`paper source/nature_html/paper.md:120-146`).
- In the TB memory T-cell cohort, NAM-PCs capture innateness, modality-consistent structure, sex-related axes, TB progression, age, season, ancestry, and other sample-level associations (`paper source/nature_html/paper.md:152-198`).

### Code and Reproducibility

The cloned code is the core Python package from `https://github.com/immunogenomics/cna`, with acquisition metadata recording commit `72f879a2bc2b21820f9de210b6c23a0b9ae97a1d`. The package exposes a Scanpy-like API: `cna.tl.association`, `cna.tl.nam`, `cna.tl.svd_nam`, plotting helpers, and a sample-level metadata helper (`doc_code.md`).

The method-code match is **medium**. Core NAM construction, residualization, SVD/NAM-PC extraction, global association testing, permutation nulls, and empirical FDR logic are directly implemented in the cloned source. Important differences are documented in `doc_code.md`: the walk-length code implements the consecutive-kurtosis-drop stop but not the paper's explicit median-kurtosis `< 8` stop; batch QC adds a hard minimum threshold; and current local coefficients are exposed as full residual-NAM `ncorrs`, not the paper's rank-`k*` `gamma` equation directly.

Reproducibility is partial from this workspace. The paper states that the core method package, figure/table code, and simulation code are in three repositories: `cna`, `cna-display`, and `cna-sim` (`paper source/nature_html/paper.md:477-480`). Only the core `cna` package is cloned here. Supplementary PDFs, supplementary tables/figures, source-data XLSX files, and companion repos were not acquired into this workspace, so simulation reruns and figure/table reproduction are not verified here.

### Practical Takeaway

CNA is best understood as a matrix-factorization and association-testing framework over sample-level abundance of graph neighborhoods. Its main contribution is not merely smaller clusters; it uses many probabilistic neighborhoods as a high-resolution basis, then borrows strength through inter-sample covariance in the NAM. This lets it detect broad, continuous, or cluster-splitting cell-state signals while still producing a global p-value and local FDR-controlled cell-population calls.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
