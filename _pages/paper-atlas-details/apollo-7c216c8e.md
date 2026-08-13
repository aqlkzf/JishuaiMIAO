---
layout: default
permalink: /paper-atlas/apollo-7c216c8e/
title: "APOLLO"
nav: false
description: "APOLLO 通过为每个成对样本直接优化一个共享 latent 和各模态特异 latent，再固定这些表示训练新样本 encoder，把“多模态共同细胞状态”“单一模态额外信息”和“从一种模态可预测的另一种模态信息”显式分开；这种分解为解释和缺失模态预测提供了结构，但其生物含义仍受配对数据、潜空间维数、网络/损失选择与非线性可辨识性边界约束。"
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
      <span>bioRxiv · 2024</span>
    </div>
    <h1>APOLLO</h1>
    <p>Partially Shared Multi-Modal Embedding Learns Holistic Representation of Cell State</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1101/2024.10.01.615977" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for APOLLO">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/uhlerlab/APOLLO" target="_blank" rel="noopener noreferrer" aria-label="Open code for APOLLO">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## APOLLO：把多模态细胞状态拆成共享信息与模态特异信息

### 它要解决的核心问题

同一个细胞的 RNA、染色质可及性、表面蛋白或显微图像是对细胞状态的不同观察窗口。它们既有共同信息，例如细胞类型，也有某一模态独有的信息，例如 RNA 数据中的批次效应、ATAC 中的调控可及性，或某种蛋白定位的特殊形态。常见联合嵌入把这些信息全部混进同一个空间，能做整合，却不直接回答“哪些是共享的，哪些只属于某个模态”。

APOLLO 的全名是 Autoencoder with a Partially Overlapping Latent space learned through Latent Optimization。其关键不是简单拼接两种数据，而是为成对测量显式规定潜空间的重叠结构：

$$
z^{(1)}=(z_S,z_{S_1}),\qquad z^{(2)}=(z_S,z_{S_2}).
$$

$z_S$ 是两个模态共用的坐标，$z_{S_1}$ 和 $z_{S_2}$ 分别是模态 1、2 的特异坐标。对同一细胞，两个 decoder 使用同一个 $z_S$，但各自只看到自己的特异部分。这种结构迫使模型把能同时帮助两种模态重建的信息放进共享空间，把剩余信息留给各自空间。

论文是 2024 年 10 月 3 日发布的 bioRxiv 预印本，DOI 为 `10.1101/2024.10.01.615977`，PDF 明确标注未经过同行评审。因此结果应作为预印本方法证据解读，不能写成已由期刊同行评审确认。

### 第一阶段：不先训练 encoder，而是直接学习 latent

普通 autoencoder 同时训练 encoder $E$ 和 decoder $D$，每个样本的 latent 是 $E(x)$。APOLLO 第一阶段反过来：为训练集中的每个成对样本直接建立可优化的 latent 向量，并与 decoder 一起通过反向传播更新。双模态完整重建目标可写为

$$
\mathcal{L}_{full}=
\mathcal{L}(x^{(1)},D_1(z_S,z_{S_1}))+
\mathcal{L}(x^{(2)},D_2(z_S,z_{S_2})).
$$

模型还可以加入只使用共享 latent 的两个 decoder $D'_1,D'_2$：

$$
\mathcal{L}_{shared}=
\mathcal{L}(x^{(1)},D'_1(z_S))+
\mathcal{L}(x^{(2)},D'_2(z_S)).
$$

共享 decoder 让 $z_S$ 单独保留足以跨模态预测的内容。完整目标再加入 latent 的 $L_2$ 正则和高斯扰动：

$$
\mathcal{L}=
\mathcal{L}_{full}+\mathcal{L}_{shared}
+\lambda(\|z_S\|_2^2+\|z_{S_1}\|_2^2+\|z_{S_2}\|_2^2).
$$

论文说明共享维度通常设得远大于特异维度，以鼓励优先使用共享容量；这是一种结构偏置，不是从数据中自动识别“真实维数”的定理。若共享空间过大，它仍可能吸收特异信息；若过小，则共享信号会泄漏到特异空间。论文通过多个维度组合做鲁棒性检查，但不能证明任意数据都唯一可辨识。

代码的主训练不在一个统一 Python API 中，而在数据集专用 notebook。导出的第一阶段 notebook 显式建立 `Embedding` 形式的逐样本 `latent_shared` 和两个 `latent_*`，将它们与 decoder 参数一起优化。图像模型的共享/特异通道和 decoder 基础结构可在 `code/model/model_cnnvae.py:270-402` 看到；条件图像模型在 `code/model/model_cnnvae_conditional.py:7-103` 把 protein ID embedding 拼到 encoder/decoder 输入。

### 第二阶段：为新样本学习 encoder

直接优化 latent 只能表示训练集中已有细胞。为处理未见样本，第二阶段固定第一阶段学到的 latent 和 decoder，再训练每个模态的 encoder：

$$
E_j(x^{(j)})\approx (z_S,z_{S_j}).
$$

源码 notebook 中能看到加载第一阶段 latent、设置 `requires_grad=False`，随后只用 Adam 更新两个 encoder。这一步将“如何解释训练集”与“如何把新样本映射进该解释空间”分开。优点是 decoder 与 latent 的分解不必同时受 encoder 容量限制；代价是流程更复杂，且第二阶段只能逼近第一阶段形成的坐标系。

跨模态预测时，从输入模态 $j$ 编码出共享坐标，再交给目标模态的共享 decoder：

$$
\hat{x}^{(k)}=D'_k(E_j(x^{(j)})_S).
$$

这里预测的是与输入模态共享、并被训练数据支持的目标信息；目标模态真正独有的随机或不可辨识部分不可能从另一模态恢复。生成一幅看起来合理的蛋白图像也不表示每个细胞的细粒度蛋白定位都被准确恢复。

### 为什么不同数据使用不同网络

APOLLO 规定潜空间和两阶段训练原则，但 encoder/decoder 可按模态替换：

- SHARE-seq 的 RNA 与 ATAC 使用全连接网络，相关结构在 `code/atac_rna/model_lord.py:5-41`。
- 染色质/蛋白图像使用卷积 encoder 和反卷积 decoder；`CNN_VAE_split` 将卷积特征通道切成共享与特异两部分（`code/model/model_cnnvae.py:270-360`）。
- 多种蛋白图像通过可学习 protein-ID embedding 条件化，从而让一套模型区分目标蛋白（`code/model/model_cnnvae_conditional.py:7-103`）。

图像类中还保留类似 VAE 的 `mu/logvar` 和重参数采样（例如 `model_cnnvae.py:343-350`），而论文公式把随机性写成对直接优化 latent 添加高斯噪声。两者都提供随机扰动，但代码的具体噪声尺度和 notebook 损失组合必须按对应实验读取，不能假定全仓库只有一个完全统一实现。

### 如何解释共享和特异空间

论文不是直接把 latent 每一维命名为一个生物过程，而是在各 latent block 内做 PCA，将细胞按 PC 位置分组，再比较两端与中心的基因、peak 或手工形态特征，并做 GO 富集或分类。由此得到的“共享/特异信息”是：某项特征的变化主要能由哪个 latent block 的主方向解释。

需要区分三层结论：

1. 架构层：某坐标被放在共享或特异 block，这是模型定义。
2. 统计层：某些基因、peak 或形态特征随该 block 的 PC 显著变化。
3. 生物层：这些变化可能对应转录调控、细胞周期或蛋白定位机制。

前两层不能自动推出第三层的因果关系。论文引用的可辨识性结果依赖线性 decoder、非高斯边缘等简化假设，而实际模型是深度非线性网络；因此“可解释/潜在因果特征”的理论动机不能被写成对所有实际 APOLLO latent 的因果保证。

### 图 1–5 的证据链

- **图 1** 定义部分重叠潜空间、两阶段训练、跨模态预测和从 latent 到生物特征解释的整体框架。
- **图 2** 在 SHARE-seq 与 CITE-seq 上检验共享/特异拆分。共享+特异空间提升细胞类型分类；RNA 特异空间可捕获批次，shared 空间保留跨模态细胞类型信号。PC/GO 结果把 RNA 特异部分联系到细胞周期，把 ATAC/shared 部分联系到转录调控。
- **图 3** 转向成对染色质–蛋白图像，引入 protein-ID 条件化，并展示从染色质预测未测蛋白。与一步 autoencoder、无特异空间、无 shared decoder 等消融比较，支持两阶段和潜空间拆分的作用。
- **图 4** 将 shared/特异 latent PC 同人工形态特征和表型分类连接，用于解释染色质组织与蛋白定位之间共享和独有的形态变化。
- **图 5** 在 Human Protein Atlas 的细胞核、微管、内质网和蛋白图像上展示可扩展性，并提出蛋白亚细胞定位与细胞器形态的关联。

同一 29 页 PDF 还内嵌 SI 图 S1–S20 和扩展材料，覆盖模拟、维度鲁棒性、重建、消融、更多形态特征与蛋白案例；本地没有独立补充 PDF 或补充 Markdown。它们增强了论文内验证，但仍共享相同数据拆分、网络选择和评估设计。

### 四类应用不要混成一个结论

1. **SHARE-seq（RNA+ATAC）**：重点是调控信息与细胞周期等共享/特异解释。
2. **CITE-seq（RNA+表面蛋白）**：重点是 shared 空间保留细胞类型、RNA-specific 空间捕获批次；该实验不以跨模态预测为目标，因此可移除 shared-only decoder。
3. **PBMC multiplexed imaging**：重点是条件化多蛋白重建、缺失蛋白预测和疾病表型分类。
4. **Human Protein Atlas imaging**：重点是细胞器形态与蛋白定位变异的关联。

这些数据都要求样本层面的配对或可定义的成对模态。APOLLO 本身不是把两个完全不配对数据集自动对应起来的匹配算法。

### 版本与复现边界

2. 仓库没有 package version、setup 或 pyproject；`code/requirements.txt` 是很长的 Linux conda 显式环境清单，含 Python 3.10、CUDA 和大量间接依赖。它比无依赖记录更好，但平台绑定且文件名与 README 中的 `requirement.txt` 单复数不一致。
3. 训练、预处理、评估和作图分散在大量 notebook，并使用数据路径、inline 超参数与中间 checkpoint；没有统一 CLI、配置合同或自动化测试。
4. 本地 `paper.pdf` 与 `paper_v2.pdf` 内容/大小均为 29 页版本；没有转换后的 `paper source`。本轮直接用 PDF 文本与逐页图像核查，不伪造 Markdown 路径。
5. 本轮没有重建 conda/CUDA 环境、执行 notebook、下载原始数据或数值重现图表；完成的是静态论文–代码证据映射。

### 一句话总结

APOLLO 通过为每个成对样本直接优化一个共享 latent 和各模态特异 latent，再固定这些表示训练新样本 encoder，把“多模态共同细胞状态”“单一模态额外信息”和“从一种模态可预测的另一种模态信息”显式分开；这种分解为解释和缺失模态预测提供了结构，但其生物含义仍受配对数据、潜空间维数、网络/损失选择与非线性可辨识性边界约束。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## APOLLO — Executive Summary

**Title:** Partially Shared Multi-Modal Embedding Learns Holistic Representation of Cell State
**Authors:** Xinyi Zhang, GV Shivashankar, Caroline Uhler
**Journal:** Nature Computational Science (2026)
**DOI:** 10.1038/s43588-025-00948-w
**Preprint:** bioRxiv 10.1101/2024.10.01.615977
**Code:** https://github.com/uhlerlab/APOLLO

---

### Motivation & Novelty

**Biological problem:** Single-cell technologies (scRNA-seq, scATAC-seq, multiplexed imaging, CITE-seq) each capture different aspects of cell state, but no single modality reveals the complete picture. Understanding which information is shared between modalities versus unique to each modality is essential for interpreting multi-modal measurements.

**Limitations of existing methods:** Current multi-modal integration methods (e.g., Seurat WNN, standard multi-modal autoencoders) learn a *union* of information from all modalities into a single latent space. This conflates shared biological signal (e.g., cell type identity captured by both RNA and protein) with modality-specific information (e.g., batch effects in RNA-seq, chromatin-specific features). No existing method automatically disentangles shared from modality-specific information.

**Unique contributions:**
1. **Partially overlapping latent space:** APOLLO introduces a VAE architecture where the latent space is explicitly partitioned into shared dimensions $z_S$ (common across modalities) and modality-specific dimensions $z_{S_j}$ (unique to each modality $j$)
2. **Two-step latent optimization training:** Step 1 trains decoders while directly optimizing latent embeddings; Step 2 trains modality-specific encoders to map new data into the learned latent space. This procedure, inspired by LORD (Gong et al., NeurIPS 2019), enables disentanglement that standard end-to-end training cannot achieve
3. **Cross-modality prediction:** The shared latent space enables predicting unmeasured modalities (e.g., protein localization from chromatin images alone)
4. **Theoretical grounding:** Builds on identifiability results showing that shared and modality-specific factors are provably recoverable under linear decoders and non-Gaussian marginals

---

### Method Overview

#### Algorithmic Framework

APOLLO uses one autoencoder per modality with a **partially overlapping latent space**:

$$\mathcal{L} = \mathbb{E}\left[L(x^{(1)}, D_1(z_S + \epsilon_S, z_{S_1} + \epsilon_{S_1})) + L(x^{(2)}, D_2(z_S + \epsilon_S, z_{S_2} + \epsilon_{S_2})) + L(x^{(1)}, D'_1(z_S + \epsilon_S)) + L(x^{(2)}, D'_2(z_S + \epsilon_S))\right] + \lambda(\|z_S\|_2 + \|z_{S_1}\|_2 + \|z_{S_2}\|_2)$$

- $D_1$, $D_2$: Modality-specific decoders (from full latent)
- $D'_1$, $D'_2$: Shared decoders (from shared latent only, for cross-modality prediction)
- $\epsilon$: Gaussian noise for generalization (implemented as VAE reparameterization)
- $\lambda$: $\ell_2$ regularization strength

#### Key Technical Components

- **Encoder architecture:** 5-layer CNN for images; 4-layer FC network for sequencing data
- **Channel splitting:** Convolutional feature maps split at the channel dimension — first $k$ channels → shared path, remaining → modality-specific path
- **Protein ID conditioning:** For multi-protein imaging (chromark, HPA), learned protein ID embeddings are concatenated at encoder and decoder
- **Latent space interpretation:** PCA on each sub-space, followed by differential expression/feature analysis at PC extremes

#### Biological Assumptions

- Some cell state information is shared across modalities (e.g., cell type)
- Some information is modality-specific (e.g., chromatin accessibility details not reflected in RNA)
- The shared dimension $|S|$ should be larger than modality-specific dimensions to encourage shared information capture

#### Computational Pipeline

1. **Preprocess** each modality (normalize images to [0,1]; filter/normalize sequencing counts)
2. **Step 1 — Latent optimization:** Train decoders + directly optimize latent embeddings $z_S$, $z_{S_j}$ to minimize reconstruction loss
3. **Step 2 — Encoder training:** Freeze decoders, train modality-specific encoders $E_j$ to map new samples into the learned latent space
4. **Downstream:** Cell type classification, cross-modality prediction, PCA-based latent interpretation, phenotype classification

---

### Evaluation

#### Datasets

| Dataset | Modalities | Cells | Source |
|---------|-----------|-------|--------|
| SHARE-seq (mouse skin) | scRNA-seq + scATAC-seq | ~34,000 | Ma et al., Cell 2020 |
| CITE-seq (murine spleen/lymph node) | scRNA-seq + surface protein | ~8,000 | Stoeckius et al., Nat Methods 2017 |
| Chromatin-protein imaging (PBMCs) | Chromatin + protein stains | 32,345 | Kalita-de Croft et al. 2023 |
| Human Protein Atlas (U2OS cells) | Nucleus + microtubule + ER | 11,657 | Thul et al. 2017 |
| Simulated data | 5 synthetic scenarios | Variable | Authors |

#### Key Results

- **SHARE-seq:** Adding modality-specific latent spaces improves cell type classification accuracy over shared-only (Fig 2a). Shared latent captures transcriptional regulators; RNA-specific captures cell cycle genes; ATAC-specific captures promoter accessibility
- **CITE-seq:** APOLLO correctly separates cell types in shared space and batch effects in RNA-specific space; Seurat WNN and standard autoencoders cannot disentangle these (Fig 2f)
- **Chromatin imaging:** Cross-modality protein prediction from chromatin achieves comparable phenotype classification accuracy to real protein images (Fig 3d). L1 loss significantly lower than inpainting baseline and standard autoencoder (Fig 3c)
- **HPA:** Identifies that intra-nuclear protein localization variability is captured by modality-specific latent spaces of different cellular compartments (Fig 5a)

#### Compared Methods

| Method | Journal/Year | Result |
|--------|-------------|--------|
| Seurat WNN | Cell 2021 | Cannot disentangle shared/specific |
| Standard multi-modal autoencoder | Zhang et al., Nat Commun 2021 | Merges all info into single space |
| Image inpainting (Cang & Bhatt, 2021) | Cell Systems 2021 | Blurry predictions, higher L1 loss |

---

### Reproducibility

**Rating: 3/5**

**Strengths:**
- All code publicly available on GitHub
- All datasets publicly available
- Clear two-step training procedure
- Multiple application notebooks with detailed workflow

**Weaknesses:**
- **No standalone training scripts** — all training in Jupyter notebooks, making exact reproduction cumbersome
- **No configuration files** — hyperparameters hardcoded in notebook cells
- **Large dependency list** — requires PyTorch 1.13.1, TensorFlow 2.10.0, CUDA 11.6, many bioinformatics packages
- **Nuclear segmentation dependency** — chromark application requires pre-computed nuclear masks from external tools (StarDist)
- **No automated evaluation** — metrics computed inline in notebooks
- **Large data downloads** — imaging datasets are substantial in size

**Practical notes:**
- Environment setup: `conda create --name <env> --file requirements.txt`
- GPU required for image-based applications
- SHARE-seq and CITE-seq applications are simpler to reproduce (smaller data, FC models)
- Chromark application is the most complex (requires image preprocessing pipeline)

---

### Strengths and Weaknesses

**Strengths:**
- Elegant architectural solution to a fundamental problem in multi-modal biology
- Theoretically motivated by identifiability results
- Demonstrates genuine biological insight (e.g., γH2AX foci count as protein-specific feature)
- General framework applicable to any paired multi-modal data
- Cross-modality prediction is a compelling and practical downstream application

**Weaknesses:**
- Requires paired measurements (same cell, multiple modalities)
- Latent space dimension ratio (shared vs specific) is a hyperparameter that must be chosen
- Two-step training is slower than end-to-end approaches
- Limited to two modalities at a time (pairwise application to HPA with 3 stains)
- No formal benchmark against recent multi-modal integration methods (e.g., MultiVI, scMM, totalVI)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
