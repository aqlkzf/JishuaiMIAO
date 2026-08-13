---
layout: default
permalink: /paper-atlas/spotdiff-34755e12/
title: "SpotDiff"
nav: false
description: "SpotDiff 用条件扩散模型补全空间转录组（ST）表达。它先准备三类条件：被遮蔽的 ST 数值、由基因名和表达值构造的文本表示、同组织 scRNA-seq 经对齐与聚合后的表示；再让 DiT 风格网络预测扩散噪声并恢复表达矩阵。 本工作区是 paper-only：有论文 PDF、OCR 和论文图，但没有作者代码快照，也没有独立补充材料。所以下文解释的是论文写出的计算合同，不能确认实际张量、网络层级与超参数。"
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
      <span>AAAI · 2025</span>
    </div>
    <h1>SpotDiff</h1>
    <p>SpotDiff: Spatial Gene Expression Imputation Diffusion with Single-Cell RNA Sequencing Data Integration</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpotDiff 中文方法解读

### 先说结论

SpotDiff 用条件扩散模型补全空间转录组（ST）表达。它先准备三类条件：被遮蔽的 ST 数值、由基因名和表达值构造的文本表示、同组织 scRNA-seq 经对齐与聚合后的表示；再让 DiT 风格网络预测扩散噪声并恢复表达矩阵。

所以下文解释的是论文写出的计算合同，不能确认实际张量、网络层级与超参数。

### 1. 问题与评估边界

原始 ST 矩阵为 $\mathbf{X}_{st}\in\mathbb{R}^{c_1\times g_{st}}$。论文随机遮蔽 30% 得到训练输入：

$$
\mathbf{X}_{mst}=\mathcal{M}(\mathbf{X}_{st},\phi),\qquad \phi=0.3.
$$

scRNA-seq 参考为 $\mathbf{X}_{rna}\in\mathbb{R}^{c_2\times g_{rna}}$。两种数据归一化、对数变换并取基因交集后，只保留 $g_o$ 个重叠基因。模型从 $\mathbf{X}_{mst}$ 生成 $\hat{\mathbf{X}}_{st}$。

要注意，定量实验是把原本观测到的值人工隐藏，再用隐藏前的值作答案。PCC、SSIM、RMSE 和 COSSIM 因而衡量“恢复人工隐藏的已观测值”，不能直接证明模型恢复了现实中从未测得的稀有生物信号。

### 2. 文本条件：把表达表改写成提示

论文从每个 spot 取 $n_1$ 个最高表达基因与 $n_2$ 个低表达的非零基因，把基因名及表达值填入模板得到 $T_{spot}$，同时把基因名作为 $T_{gene}$。T5 编码后得到 $f_{spot}$ 和 $f_{gene}$，再计算

$$
f_{text}=\operatorname{Attn}(f_{spot},f_{gene},f_{gene}),
$$

$$
\operatorname{Attn}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^T}{\sqrt d}\right)V.
$$

从左到右看：spot 描述作查询，每个基因 token 作键和值，注意力结果成为扩散网络的文本条件。论文的消融支持“移除 $f_{text}$ 后结果变差”，但不能区分收益来自基因语义、数值的二次编码还是额外模型容量，也不能据此声称 T5 自动引入了可靠的外部生物知识。

论文未报告 $n_1$、$n_2$、完整模板、T5 版本、是否冻结、token 长度和投影维度。

### 3. scRNA-seq 条件：先对齐，再为 spot 聚合邻居

一个堆叠的 6 层 U-Net 式网络 $\omega$ 将 scRNA-seq 映射到 ST 空间：

$$
\widetilde{\mathbf{X}}_{st}=\omega(\mathbf{X}_{rna}).
$$

训练目标是

$$
\min_{\omega}\mathcal{L}_{MSE}+\lambda_1\mathcal{L}_{LOC}+\lambda_2\mathcal{L}_{PEA}.
$$

$\mathcal{L}_{MSE}$ 对齐数值，$\mathcal{L}_{PEA}$ 用 $1-$平均 Pearson 相关约束逐基因相关性，$\mathcal{L}_{LOC}$ 试图利用空间距离。原文印刷的空间项是

$$
\mathcal{L}_{LOC}=\mathbb{E}^{i,j,k}_{\omega}\left[
\|\mathbf{X}_{mst_i}-\mathbf{X}_{mst_j}\|_2^2e^{d(i,j)/\sigma}
+\|\mathbf{X}_{mst_i}-\mathbf{X}_{mst_k}\|_2^2e^{d(i,k)/\sigma}
\right],
$$

其中 $j$ 是近邻，$k$ 是远处 spot。这里必须保留证据冲突：文字说该损失让近邻互补、远处表达分离；但公式两项都是正号，距离越远权重越大，最小化反而更强地惩罚远处差异。式中显式出现的还是固定输入 $\mathbf{X}_{mst}$，没有清楚显示 $\omega$ 输出如何进入梯度。这可能是排版遗漏，也可能依赖未公开实现；不能自行改写成标准 triplet loss。

随后，对每个 ST spot 计算与对齐后候选点的余弦相似度，选择 top-$\mathcal N$ 并加权：

$$
\mathbf{X}_{rna}^{pair}=\sum_{n=1}^{\mathcal N}w_n\widetilde{\mathbf{X}}_{st_n},
\qquad f_{rna}=\operatorname{Linear}(\mathbf{X}_{rna}^{pair}).
$$

直观上，一个 spot 聚合多个相似单细胞表示，以降低对单个稀疏细胞的依赖。但 $\mathcal N$、权重归一化、U-Net 结构，以及细胞数与 spot 数不同情况下的训练配对都未报告。

### 4. 条件扩散：预测加入的噪声

前向扩散为

$$
\mathbf{X}_t=\sqrt{\bar\alpha_t}\mathbf{X}_0+
\sqrt{1-\bar\alpha_t}\epsilon,qquad \epsilon\sim\mathcal N(0,\mathbf I).
$$

DiT 风格网络同时读取时间步、文本条件、RNA 条件和被遮蔽 ST，预测噪声：

$$
\mathcal{L}_{DIFF}=\mathbb{E}_{\epsilon,t}\left[
\left\|\epsilon-\epsilon_{\psi}(\mathbf{X}_t,t,f_{text},f_{rna},
\widetilde{\mathbf{X}}_{mst})\right\|_2^2\right].
$$

论文只明确两网络顺序训练：先 $\omega$，再 $\psi$；没有明确说第二阶段冻结 $\omega$。它也没有解释损失式中 $\widetilde{\mathbf{X}}_{mst}$ 的波浪号对应什么额外变换。扩散时间步、噪声日程、采样器、DiT 深度/宽度/头数和条件注入位置均 Not found。

### 5. 完整数据流

1. ST 与 scRNA-seq 归一化、对数变换并取重叠基因。
2. 随机遮蔽 ST 的 30%，形成 $\mathbf{X}_{mst}$。
3. 高低表达基因构造文本，经 T5 与交叉注意力得到 $f_{text}$。
4. $\omega$ 将 scRNA-seq 映射至 ST 空间，以 MSE、空间项和 Pearson 项训练。
5. 每个 spot 聚合 top-$\mathcal N$ 相似表示，经线性层得到 $f_{rna}$。
6. 用 $f_{text}$、$f_{rna}$ 和 masked ST 条件化噪声预测网络。
7. 反向扩散得到补全矩阵，在人工遮蔽位置与原始观测值比较。

### 6. 结果应怎样读

论文在 osmFISH、FISH、STARmap、MERFISH、10x_BA 与 10x_HBC 上评估。表 1 中 SpotDiff 在六个数据集的四项指标均给出最佳报告值。表 3 显示同时使用 $f_{rna}$ 与 $f_{text}$ 的版本最好；图 5 显示去掉 $f_{text}$ 或 $\mathcal L_{LOC}$ 后三个 FISH 标记基因的分布发生变化。图 6 与空间对齐有效相一致，但未单独隔离 $\mathcal L_{LOC}$，不能仅凭该图宣称空间损失已被独立验证。

### 7. 复现边界

论文足以重建高层流程，但以下关键项 **Not found**：随机种子和拆分、$n_1/n_2/\mathcal N$、$\lambda_1/\lambda_2/\sigma$、近远邻采样规则、T5 版本与训练方式、U-Net/DiT 详细结构、优化器、学习率、batch、epoch、扩散日程、采样步数、硬件，以及配对 scRNA-seq 的泄漏控制。

因此，新增代码只能称为“基于论文的再实现”，不能称为“代码验证后的作者实现”。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpotDiff — Spatial Gene Expression Imputation Diffusion with scRNA-seq Integration

### Motivation & Novelty

Spatial transcriptomics captures gene expression with spatial context but suffers from severe sparsity due to low mRNA capture rates. Existing imputation methods face fundamental limitations: traditional statistical approaches (KNN, matrix factorization) cannot model complex nonlinear gene relationships; generative models (GANs, VAEs) can only replicate observed distributions without recovering unobserved biological signals; and prior scRNA-seq-integration methods either use the sparse scRNA-seq data directly (introducing noise) or neglect multi-modal complementarity.

**Compared methods and their limitations:**
- **gimVI** (Lopez et al., arXiv 2019): Joint VAE model for unpaired scRNA-seq and ST, but assumes simple latent structure
- **Tangram** (Biancalani et al., *Nature Methods* 2021): Alignment-based mapping of scRNA-seq to ST, but does not generate new expression values
- **GraphST** (Long et al., *Nature Communications* 2023): Graph-based spatial integration, primarily designed for clustering not imputation
- **SpaFormer** (Wen et al., arXiv 2023): Transformer-based with positional encoding, but uses only ST data without scRNA-seq integration
- **stMCDI** (Li et al., arXiv 2024): Masked conditional diffusion with GNN, but lacks text-modal conditioning and scRNA-seq integration
- **stDiff** (Li et al., *Briefings in Bioinformatics* 2024): Diffusion model using scRNA-seq, but does not pre-align modalities or use prompt learning
- **STEM** (Hao et al., *Communications Biology* 2024): Transfer learning approach, but struggles with highly sparse data

**SpotDiff's unique contributions:**
1. **Spot-gene prompt learning** — a novel text-modal conditioning approach that uses T5 to encode natural-language descriptions of spot expression profiles, capturing gene-spot associations that numerical representations alone miss
2. **scRNA-seq integration network** — a 6-layer UNet that pre-aligns scRNA-seq data into the ST space before nearest-neighbor matching, with a spatial location loss that encodes the biological prior of spatial autocorrelation
3. **Multi-modal conditional diffusion** — combines text features, integrated scRNA-seq features, and masked ST data as conditions for a DiT-based diffusion model, enabling high-fidelity imputation that leverages complementary information sources

### Method Overview

SpotDiff is a two-stage pipeline:

**Stage 1 — scRNA-seq Integration**: A 6-layer UNet ($\omega$) maps scRNA-seq data into the ST expression space, trained with MSE loss, spatial location loss ($\mathcal{L}_{LOC}$, encouraging nearby spots to have similar expressions), and gene-wise Pearson correlation loss ($\mathcal{L}_{PEA}$). After training, cosine similarity identifies the top-$\mathcal{N}$ nearest integrated scRNA-seq points per ST spot, which are fused via normalized weights to create stable per-spot representations.

**Stage 2 — Conditional Diffusion**: A DiT (Diffusion Transformer) model ($\psi$) performs iterative denoising conditioned on three sources: (1) $f_{text}$ from spot-gene prompt learning via T5 encoder + cross-attention, (2) $f_{rna}$ from the integrated scRNA-seq nearest neighbors, and (3) the masked ST data itself. The standard DDPM noise-prediction objective is used.

See `doc_method.md` for full mathematical derivations and algorithm walkthrough.

### Evaluation

#### Datasets
Six datasets spanning single-cell resolution (osmFISH, FISH, STARmap, MERFISH) and 10X Visium resolution (10x_BA, 10x_HBC), covering mouse somatosensory cortex, embryo, primary visual cortex, brain anterior, and human breast cancer tissues.

#### Metrics
- **PCC** (Pearson Correlation Coefficient): gene-wise correlation between imputed and original
- **SSIM** (Structural Similarity Index): perceptual similarity metric
- **RMSE** (Root Mean Square Error): reconstruction accuracy
- **COSSIM** (Cosine Similarity): directional similarity of expression profiles

#### Key Results
- SpotDiff achieves best performance across **all 6 datasets** on **all 4 metrics**
- osmFISH: PCC 0.3721 vs 0.3020 (SpaFormer, 2nd best) — 23% relative improvement
- FISH: PCC 0.6215 vs 0.5876 (stMCDI, 2nd best)
- 10x_BA: COSSIM 0.6651 vs 0.5142 (stDiff, 2nd best) — 29% relative improvement
- Largest gains on MERFISH and 10x datasets where scRNA-seq integration has more impact

#### Biological Validation
- **Marker gene recovery** (Fig 3): SpotDiff accurately recovers spatial expression patterns of marker genes (Efnb2, COL6A1) in 10x_BA and 10x_HBC, while other methods show spatial bias or overestimation
- **Distribution matching** (Fig 4): UMAP visualization on STARmap shows SpotDiff's imputed data best matches the real ST data distribution, with minimal distribution shift
- **Cell population identification** (Table 4): On Mop dataset, SpotDiff achieves ARI=0.7336, AMI=0.8440, NMI=0.8561, outperforming all baselines and raw ST data clustering

#### Ablation Study
- Removing $f_{rna}$ (scRNA-seq condition) causes the largest drop (PCC decreases by ~0.06-0.07), confirming scRNA-seq integration is the most important component
- Removing $f_{text}$ (text condition) causes moderate drops (~0.01-0.02 PCC)
- Both conditions together yield the best results, confirming their complementarity
- Removing $\mathcal{L}_{LOC}$ leads to bimodal gene expression distributions (Fig 5), confirming spatial regularization prevents mode collapse

### Reproducibility

**Rating: 2/5** (Low)

**Strengths:**
- Clear mathematical formulation with well-defined loss functions
- Comprehensive evaluation on 6 datasets with 4 metrics
- Ablation study validates each component's contribution
- Datasets are publicly available

**Weaknesses:**
- **No public code repository** — the most significant barrier to reproduction
- **Many critical hyperparameters unspecified**: $n_1, n_2$ (prompt template genes), $\mathcal{N}$ (nearest neighbors), $\lambda_1, \lambda_2$ (loss weights), $\sigma$ (distance decay), diffusion schedule parameters, DiT architecture details (layers, dimensions, heads), T5 model variant
- **No training details**: learning rate, optimizer, batch size, number of epochs, hardware requirements not reported
- **Ambiguous definitions**: "nearby" vs "distant" spots in $\mathcal{L}_{LOC}$ selection, how spatial coordinates are used for non-grid technologies
- **No code availability statement** in the paper

**Practical notes:**
- The T5 encoder and DiT framework are both well-documented in the deep learning community, making the architecture reproducible in principle
- The preprocessing pipeline follows Li et al. (2022), which is a standard benchmark
- The two-stage training simplifies implementation compared to joint training
- Estimated GPU memory: likely substantial due to T5 encoder + DiT backbone + UNet integration network

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
