---
layout: default
permalink: /paper-atlas/spatialcoc-91a22a5a/
title: "SpatialCOC"
nav: false
description: "空间多组学的困难不只是“不同模态维数不同”。同一组织位置的 RNA、蛋白和 ATAC 既有共享生物结构，也有各自稀疏性、测量噪声和技术偏差。SpatialCOC 把任务拆成两步： Spatial Continuous Mapping（SCM）：把二维坐标当作顶层先验，分别学习每个模态从坐标到特征的连续函数；"
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
      <span>Nature Communications · 2026</span>
    </div>
    <h1>SpatialCOC</h1>
    <p>SpatialCOC: an integrative framework for spatial continuous mapping and cross-omics correction in spatial multi-omics data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-71882-2" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpatialCOC 中文方法解读：先用坐标重建连续组学，再做跨组学相关性校正

### 1. 方法试图解决的两类问题

空间多组学的困难不只是“不同模态维数不同”。同一组织位置的 RNA、蛋白和 ATAC 既有共享生物结构，也有各自稀疏性、测量噪声和技术偏差。SpatialCOC 把任务拆成两步：

1. Spatial Continuous Mapping（SCM）：把二维坐标当作顶层先验，分别学习每个模态从坐标到特征的连续函数；
2. Cross-Omics Correction（COC）：对空间重建后的两个模态训练 DCCAE，保留各自可重构信息，同时最大化潜变量相关性，再以线性 CCA 得到成对表示。

论文证据来自 paper source/paper/auto/paper.md、主图 1–4 和三份本地补充 PDF；代码证据来自 SpatialCOC/ 固定快照。其 .repo_source 记录 commit 5f326e5c05d2a195b65240be0242c04e014d3fc4。该值与旧合同写的 0300e4de 不同，应以 .repo_source 为当前本地 provenance。

### 2. SCM：坐标如何变成组学连续函数

对第 m 个模态，输入是 spot 坐标 $s_i=(x_i,y_i)$，输出维数等于该模态特征数。每个模态独立训练一个 INR：

$$
\hat X^{(m)}=f_{\phi_m}(S).
$$

代码网络为 Linear(2,3000) 后接三个 SineLayer。每个 SineLayer 并不是三条独立子网络，而是把输入复制三份，分别乘频率 1、2、3，取正弦后拼接进一个线性层：

$$
h' = W[\sin(h),\sin(2h),\sin(3h)]+b.
$$

低频更容易表示平滑变化，高频可表示边界和细节。补充 Note 1 的敏感性实验说明频率过低会漏掉边缘，过高会拟合细节；但代码把 1/2/3 固定在层内，用户接口没有直接暴露论文讨论的连续 $\omega_0$ 参数。

#### 2.1 INR 的目标不是原始 X，而是 KX

代码先对坐标 z-score，再构造全体 spot 的 dense Gaussian kernel：

$$
K_{ij}^{code}=\exp\left(-\frac{\lVert \tilde s_i-\tilde s_j\rVert_2^2}{b}\right).
$$

随后做中心化并拟合

$$
\min_\phi\lVert f_\phi(S)-K_cX\rVert_2.
$$

所以 SCM 学的是 kernel-smoothed、centered feature target，而不是直接重建原始 $X$。这也解释了为何输出更平滑。论文主文公式对距离范数和 $2\sigma^2$ 的写法与代码 exp(-distance squared / bandwidth) 不是逐项相同；代码参数 bandwidth 不能未经换算直接叫论文 $\sigma$。

代码的 $K_c$ 使用

$$
K-\operatorname{mean}_{axis0}(K)-\operatorname{mean}_{axis1}(K)+\operatorname{mean}(K).
$$

对称 kernel 下两条均值向量数值相同，广播仍得到中心化效果，但实现没有显式写 $HKH$。论文也没有清楚突出这一中心化步骤。

#### 2.2 连续不等于真实无偏信号

SCM 输出可在任意坐标查询，故数学上是连续函数；但它仍由离散观测和 smoothing kernel 监督。真实锐利边界可能被平滑，未观测位置是模型插值而非新测量。图 3a 的 Moran's I 提升证明输出更空间自相关，不等于证明它更接近未知真值。补充材料也承认 smoothness 与 boundary definition 存在权衡。

### 3. COC：双自编码器与 CCA loss

教程先对两个 SCM 输出分别 PCA，再输入 DCCAE。每个分支实际架构由代码硬编码为：

$$
d_m\rightarrow512\rightarrow256\rightarrow q
\rightarrow256\rightarrow512\rightarrow d_m.
$$

传入的 layer_sizes1/2 列表只有最后一个元素决定 latent size；列表中前面的 256 并不控制真实隐藏层。Encoder 使用 BatchNorm、LeakyReLU(negative_slope=1)；斜率 1 使该 LeakyReLU 实际等于恒等映射，因而除 BatchNorm 外，编码器主要是线性层的组合。Decoder 的第一层后也没有 activation，第二层后 slope=1 的 LeakyReLU 同样不产生非线性。尽管论文将其描述为 deep nonlinear correction，当前代码的显式非线性能力比图示暗示的弱。

#### 3.1 Reconstruction loss

两个分支从 latent 重建各自 PCA 输入，代码用均值 MSE：

$$
L_{rec}=\tfrac12\bigl(\operatorname{MSE}(X_1,\hat X_1)
+\operatorname{MSE}(X_2,\hat X_2)\bigr).
$$

它防止只追求跨模态相关而丢掉模态特异信息。论文公式写样本级 $L_2$ 范数求和，与 mean squared error 在缩放和平方形式上并非完全相同。

#### 3.2 Correction / CCA loss：$T$ 是什么

这里要先区分两个步骤：

1. **训练中的 CCA loss**：每个 minibatch 根据当前 encoder latent 动态计算 $T$，其损失参与反向传播；
2. **训练后的 linear CCA**：在完整数据的 latent 上重新拟合线性投影，只生成最终表示，不再更新 encoder。

##### 3.2.1 从 batch latent 到协方差矩阵

设当前 batch 有 $b$ 个配对 spot，两个 encoder 输出相同维数的 latent：

$$
H_1,H_2\in\mathbb R^{b\times q}.
$$

代码先沿 spot 方向对每个 latent 维度中心化。记中心化结果为 $\bar H_1,\bar H_2$，则：

$$
\Sigma_{12}=\frac{1}{b-1}\bar H_1^T\bar H_2,
$$

$$
\Sigma_{11}=\frac{1}{b-1}\bar H_1^T\bar H_1+r_1I,
\qquad
\Sigma_{22}=\frac{1}{b-1}\bar H_2^T\bar H_2+r_2I.
$$

$\Sigma_{11}$ 和 $\Sigma_{22}$ 描述各模态 latent 内部的方差及维度间相关性，$\Sigma_{12}$ 描述两个模态之间的交叉协方差。训练代码取 $r_1=r_2=10^{-3}$，用来避免 minibatch 协方差接近奇异。

代码通过特征分解计算逆平方根。例如：

$$
\Sigma_{11}=V_1D_1V_1^T,
\qquad
\Sigma_{11}^{-1/2}=V_1D_1^{-1/2}V_1^T.
$$

计算前会删除不大于 $10^{-9}$ 的特征值，避免对接近零的数取负二分之一次方。

##### 3.2.2 $T$ 是白化后的跨模态相关矩阵

$$
\boxed{
T=\Sigma_{11}^{-1/2}\Sigma_{12}\Sigma_{22}^{-1/2}
}
\in\mathbb R^{q\times q}.
$$

它不是网络参数，也不是最终投影矩阵，而是由当前 minibatch latent 即时计算出的**白化交叉协方差矩阵**。左右两侧的逆平方根分别消除两个模态内部的尺度差异和维度相关性，因此 $T$ 保留的是标准化后的跨模态线性联系，而不是容易被高方差 latent 维度主导的原始协方差。

如果定义白化表示

$$
\widetilde H_1=\bar H_1\Sigma_{11}^{-1/2},
\qquad
\widetilde H_2=\bar H_2\Sigma_{22}^{-1/2},
$$

那么

$$
T=\frac{1}{b-1}\widetilde H_1^T\widetilde H_2.
$$

在一维情况下，$T$ 退化为带正则化的 Pearson correlation：

$$
T=
\frac{\operatorname{cov}(H_1,H_2)}
{\sqrt{(\operatorname{var}(H_1)+r_1)(\operatorname{var}(H_2)+r_2)}}.
$$

因此，可以把 $T$ 理解为 Pearson correlation 的多维、带白化推广，而不是原始 latent 各列两两相关系数组成的矩阵。当前实现实际要求两个分支具有相同 latent 维数 $q$；数学上不同维数时 $T$ 可以是矩形矩阵，但代码把两个协方差单位阵的大小都取自 $H_1$，不能直接支持这种情况。

##### 3.2.3 $T$ 如何变成 CCA loss

对 $T$ 做奇异值分解：

$$
T=U\operatorname{diag}(\sigma_1,\ldots,\sigma_q)V^T.
$$

$\sigma_r(T)$ 就是第 $r$ 对 canonical variables 的带正则化 canonical correlation。最大的奇异值对应两个模态中相关性最高的一对线性方向；后续奇异值对应与已有方向正交的下一组相关方向。

代码不直接调用 SVD，而是对 $T^TT$ 做特征分解。因为

$$
\lambda_r(T^TT)=\sigma_r(T)^2,
$$

所以对最大的 $k$ 个特征值开平方再求和，就得到 top-$k$ canonical correlations。默认 `use_all_singular_values=False` 时：

$$
L_{CCA}=k-\sum_{r=1}^k\sigma_r(T).
$$

$k$ 是常数，不影响梯度，因此最小化该损失等价于最大化 top-$k$ canonical correlations。$T$ 每个 minibatch 都会重新计算，梯度经过协方差、特征分解和 $T$ 返回两个 encoder。总损失为

$$
L=L_{rec}+L_{CCA},
$$

代码没有为两项设置额外可调权重。

论文式 (19) 写的是 $-\sqrt{\operatorname{tr}(T^TT)}$。代码只有在 `use_all_singular_values=True` 时才使用对应的

$$
\sqrt{\operatorname{tr}(T^TT)}
=\lVert T\rVert_F
=\sqrt{\sum_r\sigma_r(T)^2}.
$$

这是假定所有方向一起贡献的 Frobenius norm，不是把奇异值直接相加的 nuclear norm。代码此时返回 $k-\lVert T\rVert_F$；与论文的 $-\lVert T\rVert_F$ 相差常数 $k$，优化梯度相同。公开教程采用默认分支，实际优化的是 top-$k$ 奇异值之和，而不是论文式 (19) 展示的 Frobenius norm。

##### 3.2.4 训练后 linear CCA 的作用

网络训练结束后，代码在完整数据的 latent 上重新估计协方差，并以 $r_1=r_2=10^{-4}$ 构造类似的 $T$。对其做 SVD 后得到：

$$
W_1=\Sigma_{11}^{-1/2}U_{[:,1:k]},
\qquad
W_2=\Sigma_{22}^{-1/2}V_{[:,1:k]}.
$$

这里 $T\in\mathbb R^{q\times q}$ 是用来衡量相关性并寻找方向的中间算子，而 $W_1,W_2\in\mathbb R^{q\times k}$ 才是实际应用到 latent 的投影矩阵：

$$
Z_1^{CCA}=\bar H_1W_1,
\qquad
Z_2^{CCA}=\bar H_2W_2.
$$

两个结果各为 $n\times k$，教程再 concatenate，因此默认 $k=10$ 时：

$$
Z=[Z_1^{CCA}\Vert Z_2^{CCA}]\in\mathbb R^{n\times20}.
$$

不是每模态 20、总共 40。训练损失中的 $T$ 是 minibatch 相关性的可微估计；训练后的 linear CCA 使用全数据，负责固定最终投影。这两个步骤共享 CCA 数学结构，但作用不同。该实现只接受两个模态；论文“任意维度”指每个模态的输入特征维度可不同，不等于当前 DCCAE 可一次接收任意数量模态。

### 4. 实际教程的数据流

以 Mouse Brain tutorial 为例：

1. 读取 RNA 与 ATAC/CUT&Tag h5ad；
2. 调用 preprocessing：RNA 选 3000 HVG、normalize/log/scale；ATAC 做 51 维 LSI 并丢掉第一维；
3. 从 adata.uns['INR'] 取预存 SCM reconstruction；RNA 把它设为 X 再 PCA，ATAC 把它直接设为 obsm['X_pca']；
4. notebook 后面才重新训练 INR；
5. 因为写回逻辑是 if 'INR' not in adata.uns，预存键存在时新结果不会覆盖；
6. COC 实际继续使用第 3 步的预计算 INR/PCA；
7. DCCAE 训练 60 epochs，post-hoc CCA 两边各取 10 维并拼接；
8. 用该 20 维表示建邻居图、Leiden/PAGA 等下游分析。

这意味着公开 tutorial 的下游结果依赖 Zenodo h5ad 中预存的 INR artifact；重新运行 SCM 单元并不会驱动同一次 notebook 的 COC 输入更新。要从原始数据复现，必须显式将新 reconstruction detach/cpu/numpy 后写回，并重新执行 PCA 与 COC。

### 5. 图和补充证据支持什么

- 图 1 支持 SCM→COC 的概念顺序和两类损失，不证明代码逐层等价。
- 图 2 的 HLN augmented patterns/noise 是受控模拟：真实淋巴结表达按标签重新空间分配，再加 Gaussian/pepper noise。它提供已知真值，但不能替代真实组织中的未知噪声评估。
- 图 3 的 mouse brain/spleen 展示 smoothness 与结构分辨的权衡。SpatialCOC 并非每个纯 smoothness 指标都最好；作者主张的是在结构数量与连续性之间平衡。
- 图 4 的 thymus 展示加噪鲁棒性、跨切片空间域及 PAGA topology consistency。PAGA 相似不等于直接消除原始 batch effect，且依赖聚类/节点对齐。
- Supplementary Note 1 给出 sine/kernel 敏感性；Note 2 给出模块/损失消融；Notes 3–7 包含 benchmark、指标、模拟和数据说明。Reporting Summary列出 SpatialCOC v1.0.0 和软件版本。Peer-review file 还显示早期方法名 SpaKnit，解释了仓库 metadata/教程中的旧名。

论文结果只适用于所选数据、预处理、聚类参数和技术重复。图中对“noise removal”的归因主要通过模拟与跨模态相关性支持；它不能保证所有不相关成分都是技术噪声，因为真实模态特异生物信号也可能跨模态不相关。

### 6. 直接代码揭示的版本与复现边界

#### 6.1 SpaKnit → SpatialCOC 重命名未完全清理

setup.py 仍将包名、URL和描述写为 SpaKnit，README badge 也指向 SpaKnit，教程开头使用 SpaKnit，而正式论文/仓库标题为 SpatialCOC。Peer-review PDF确认早期稿名 SpaKnit。应视为同一方法的版本演变，而不是两个独立算法。

#### 6.2 代码 provenance 以本地记录为准

旧合同写 commit 0300e4de，但本地 .repo_source 实际是 5f326e5c05d2a195b65240be0242c04e014d3fc4。本文档只对后者的当前文件负责。仓库没有嵌套 git 历史，无法在本地证明两个 commit 之间具体改动。

#### 6.3 训练 artifact 与设备问题

- INRModel 返回带计算图的 best_INR_recon，未 detach；直接放入 AnnData uns 不适合作为持久 h5ad artifact。
- DCCAE 把模型强制移到可用 cuda:0，却把输入移到构造参数 self.device_。教程不传 device，默认 CPU；在有 CUDA 的机器上可能出现模型 GPU、输入 CPU 的 device mismatch。
- cca_loss 内部又自行选择 cuda:0/CPU，而不是忠实使用传入 device，进一步增加混合设备风险。
- 训练每个 epoch 都写当前目录固定 checkpoint.model；并行/多实例会互相覆盖。仓库还直接提交了 Tutorials/checkpoint.model，但没有 provenance 证明它对应哪次数据/参数。
- 收敛判断 if epoch == epoch_num 在 Python for range(epoch_num) 结束后永远为假，因此 warning 分支不可达。

#### 6.4 可扩展性

SCM 默认构造 n×n dense kernel，空间和计算至少二次增长。虽然有 sparse helper，但 INRModel 主路径不调用。宽度 3000、每模态完整坐标 full-batch 训练也很重。论文展示的数据规模不能推出 atlas-scale 数据无需近似。

### 7. 可信复现应如何做

首先锁定 commit 5f326e5c...、Zenodo record 与文件哈希；从原始 h5ad 重新运行 SCM，保存 detached reconstruction，并确保 COC 真正消费新结果；统一 device；为每个 run 使用独立 checkpoint；记录 bandwidth、epoch、PCA/LSI 维数、CCA k、聚类 resolution 与 seed。再分别验证：SCM reconstruction/边界，COC correlation/reconstruction，最终 clustering/PAGA。不能只因为 notebook 能打开或预存 artifact 能画图，就宣称从原始数据端到端复现。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpatialCOC Summary

### Motivation & Novelty

#### Biological Problem

Spatial multi-omics technologies co-profile two or more molecular layers (gene expression, chromatin accessibility, protein abundance) at spatially resolved spots in tissue sections. Integrating these layers is essential for understanding tissue architecture, cell-state transitions, and regulatory mechanisms. However, the integration must account for:

1. **Diverse spatial patterns**: Different omics layers exhibit distinct spatial structures (sharp boundaries in RNA, graded transitions in ATAC, vesicular patterns in protein).
2. **Nonlinear inter-omics relationships**: Chromatin accessibility does not linearly predict gene expression; post-translational regulation makes RNA-protein correlations complex.
3. **Modality-specific noise**: Spatial transcriptomics background noise, dropout events, and batch effects between replicate slices distort single-modality representations.

#### Limitations of Existing Approaches

| Method | Type | Limitation |
|--------|------|------------|
| SpatialGlue (Nat. Methods 2024) | spatial multi-omics | Graph-based, captures local neighborhoods; struggles with global patterns |
| COSMOS (Nat. Commun. 2025) | spatial multi-omics | "Bottom-up" fusion; performance fluctuates with noise |
| Seurat WNN (Cell 2021) | single-cell multi-omics | Weighted summation; linear, reduces noisy weights rather than removing noise |
| MultiVI (Nat. Methods 2023) | single-cell multi-omics | No spatial information; collapses modalities without spatial context |
| MultiMAP (Genome Biol. 2021) | single-cell multi-omics | Non-spatial; sensitive to noise |
| STAGATE (Nat. Commun. 2022) | spatial transcriptomics | Graph-based; trades off biological signal for smoothness |
| SpaGCN (Nat. Methods 2021) | spatial transcriptomics | Local neighborhood smoothing; misses global patterns |

The fundamental problem with "bottom-up" approaches: they treat spatial information as one parallel modality to be fused with omics, rather than as the prior distribution that should govern all modalities. Graph neighborhoods by construction cannot capture global patterns (e.g., arc or layered tissue structures) because they only encode local adjacency.

#### What's New

SpatialCOC introduces a **"top-down"** integration strategy:

1. **Spatial coordinates as prior** (not a modality): Each omics layer is modeled as a continuous function of space using Implicit Neural Representations (INRs) with SIREN-based periodic activations. This enables the model to learn global spatial patterns, not just local neighborhoods.

2. **"Correction" rather than "summation"**: A Deep Canonically Correlated AutoEncoder (DCCAE) captures nonlinear cross-modal relationships and removes noise that is not shared across modalities — actively eliminating modality-specific noise rather than merely downweighting it.

3. **Modality-dimension agnosticism**: Both modules accept inputs of arbitrary dimension (raw features or PCA embeddings), enabling flexible integration of modalities with vastly different feature spaces (3000-dim RNA vs. 20-dim LSI ATAC vs. 21-dim protein).

---

### Method Overview

SpatialCOC is a two-stage framework:

**Stage 1 — Spatial Continuous Mapping (SCM)**: Each omics modality is independently reconstructed from shared spatial coordinates using a SIREN network (sinusoidal activations with multi-frequency encoding ω₀=[1,2,3]). The reconstruction target is a spatially smoothed version of the input (Gaussian kernel K applied to raw features), forcing the INR to produce a continuous, smooth representation. The key benefit: the learned function can interpolate expression at any 2D coordinate, enabling truly continuous spatial representations that transcend the discrete spot grid.

**Stage 2 — Cross-Omics Correction (COC)**: The spatially smoothed representations from Stage 1 (after PCA reduction) are fed into a DCCAE — two encoder-decoder pairs jointly optimized with a reconstruction loss (preserve modality-specific signals) and a CCA-based correction loss (maximize cross-modal correlation). After training, a post-hoc linear CCA transforms the encoder latents into maximally correlated subspaces. The final embedding concatenates both modalities' CCA projections (n×20 by default).

The output embedding is used for spatial domain identification (leiden/mclust clustering), trajectory inference (PAGA), and multimodal biomarker analysis.

For full mathematical derivation, see `doc_method.md`. For code-paper mapping, see `doc_code.md`.

---

### Evaluation

#### Datasets

| Dataset | Technology | Spots | Modalities | Sections |
|---------|-----------|-------|-----------|---------|
| HLN-augmented | Simulated from 10x HLN | 1,200/pattern | RNA + protein (aug.) | 4 patterns × 3 replicates; 4 noise combos |
| Mouse brain | Spatial ATAC-RNA-seq; CUT&Tag-RNA-seq | ~9,471/section | RNA + ATAC/histone | 4 slices (ATAC, H3K27me3, H3K27ac, H3K4me3) |
| Mouse spleen | SPOTS | 2,568–2,768 | RNA + protein (21 markers) | 2 biological replicates |
| Mouse thymus | Stereo-CITE-seq | ~4,376/section | RNA + protein | 3 biological replicates |

#### Metrics

- **ARI, AMI, NMI**: clustering accuracy against ground-truth labels (simulated datasets)
- **Moran's I**: spatial autocorrelation of cluster assignments (higher = smoother domains; mouse brain)
- **CHAOS score**: spatial dispersion within clusters (lower = better; mouse spleen)
- **PAGA cosine similarity**: consistency of cell-type PAGA connectivity graphs across batch replicates (higher = more consistent)

#### Key Results

**Simulated benchmark (HLN-augmented)**:
- SpatialCOC ranked first across all 4 spatial patterns in ARI/AMI/NMI; particularly strong on complex "layered" patterns where graph-based methods (STAGATE, SpaGCN) fell below mono-omics baseline
- SpatialCOC most robust to noise: consistently outperformed others across all 4 noise combinations; MultiVI achieved ARI ~0.05-0.08 with Gaussian noise added to one modality

**Mouse brain (spatial smoothness vs. biological detail)**:
- Moran's I: SpatialCOC = 0.905 (before SCM: 0.57, after: 0.94 on single slice shown in Fig. 3a); SpatialGlue = 0.785; STAGATE sacrifices too many cell types for smoothness
- SpatialCOC identified all biologically meaningful structures (isocortex layers L1-L6, aca, cp, ls, ccg) across all 4 slices; STAGATE identified <6 cell types on average

**Mouse spleen (region-specific smoothness)**:
- SpatialCOC achieved region-specific smoothness: correctly identified vesicular germinal center (GC) structures while maintaining smoothness in macrophage-enriched peripheral areas
- SpaGCN: globally smooth but missed GC structure; STAGATE: identified GC but not smooth in peripheral regions

**Mouse thymus (batch consistency)**:
- SpatialCOC PAGA cosine similarity = 0.975 (best), vs. STAGATE = 0.942 (second); consistent linear medulla→connective tissue→cortex trajectory across all 3 replicate slices
- SpatialGlue: inconsistent topology (linear in slice 2, graph in slice 3)

---

### Reproducibility

**Rating: 3/5**

**Justification**: Core code and tutorial notebooks are provided, and datasets are deposited in GEO/Zenodo. However:

**Strengths**:
- GitHub repo contains well-organized Python modules and 5 tutorial notebooks covering all datasets
- All datasets available at Zenodo (https://doi.org/10.5281/zenodo.14854747)
- Requirements.txt pins key dependencies (scanpy 1.9.5, Python 3.11.5)
- Seed-fixing utility (`fix_seed(2024)`) for reproducibility

**Weaknesses and Pitfalls**:
- **No CLI or main script**: the pipeline lives in Jupyter notebooks, not a reproducible script. Reproducing results requires manually executing tutorial cells in order.
- **Local paths in notebooks**: Tutorials contain absolute Windows-style paths (`D:/study/learning/...`) for loading pre-computed results, making them non-executable without modification.
- **Pre-computed INR results**: Tutorial Cell 5 loads `adata.uns['INR']` from pre-existing `.h5ad` files rather than recomputing. Users must run Cell 9 first, then manually update Cell 5 references — not obvious from reading the notebook sequentially.
- **Environment**: Requires R 4.3.1 and rpy2 for mclust clustering (used for spleen/thymus). R setup is non-trivial and undocumented beyond the requirements.txt.
- **INR training is slow**: 1500 epochs on mouse brain (~9k spots, 3k genes) with a 3000-unit SIREN. Full n×n kernel matrix (360MB for n=9k) is materialized in GPU memory. ATAC modality (200 epochs) is faster. No GPU time estimates provided.
- **Package name mismatch**: setup.py still references old name "SpaKnit"; internal imports are relative; not pip-installable in current form.
- **Checkpoint file hardcoded to working directory**: `torch.save(..., 'checkpoint.model')` — running from different directories may cause issues.

**Practical setup**:
```bash
git clone https://github.com/xjtu-omics/SpatialCOC
pip install -r requirements.txt
# Download data from https://doi.org/10.5281/zenodo.14854747
# Edit absolute paths in Tutorial notebooks
# Run Tutorial_3_Mouse_Brain.ipynb cell by cell
```

**Common pitfall**: The kernel bandwidth `σ=0.002` is applied to z-score normalized coordinates. For datasets with very different spot densities, z-scoring produces different effective bandwidths. Users modifying the bandwidth should be aware it operates in standardized coordinate space, not physical micrometers.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
