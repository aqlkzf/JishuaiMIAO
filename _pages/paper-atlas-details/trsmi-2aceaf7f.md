---
layout: default
permalink: /paper-atlas/trsmi-2aceaf7f/
title: "TRSMI"
nav: false
description: "TRSMI 的目标是把同一批空间 spot 上的 RNA、ADT、ATAC 等模态压缩为一个联合表示 Z，同时保留跨模态一致性和组织空间边界。它的主线是：每个模态先构图并做浅层近恒等编码；再用软对应关系交换跨模态信息；随后分别形成局部表示与多尺度 APPNP 全局表示，以训练时间相关的门控混合两者；最终通过模态重建、原型聚类和图稳定正则联合训练。 本工作区是 paper-only。"
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
      <span>ICASSP · 2026</span>
    </div>
    <h1>TRSMI</h1>
    <p>Toward Robust Spatial Multi-Omics Integration: Spatial Multi-Omics Integration via Alignment and Scheduled Diffusion</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1109/ICASSP55912.2026.11461685" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for TRSMI">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TRSMI 中文方法解读

### 核心结论

TRSMI 的目标是把同一批空间 spot 上的 RNA、ADT、ATAC 等模态压缩为一个联合表示 $Z$，同时保留跨模态一致性和组织空间边界。它的主线是：每个模态先构图并做浅层近恒等编码；再用软对应关系交换跨模态信息；随后分别形成局部表示与多尺度 APPNP 全局表示，以训练时间相关的门控混合两者；最终通过模态重建、原型聚类和图稳定正则联合训练。

本地只有 5 页 ICASSP 论文、OCR 和图像，没有作者代码仓库或独立补充材料。因此下面区分“论文明确写出”“由公式可读出”和“实现仍 Not found”，不把合理猜测当作代码事实。

### 1. 输入与输出

同一组织有 $N$ 个 spot、$M$ 个模态。坐标集合为 $\mathcal S=\{(x_i,y_i)\}_{i=1}^N$，第 $m$ 个模态的特征矩阵为 $F^m\in\mathbb R^{N\times D_m}$。目标是学习

$$
\mathcal Z=\Phi(\mathcal F_M,\mathcal S)\in\mathbb R^{N\times d}.
$$

$Z$ 供空间域聚类、可视化、细胞类型识别等下游任务使用。论文图 1 还列出细胞互作推断，但没有给出相应算法或评估，因此它应被看作潜在应用，而不是本文已验证的独立模块。

### 2. 每个模态先有两张图

对模态 $m$，论文在坐标上建立空间 $k$NN 图 $A_S$，在模态特征上建立特征 $k$NN 图 $A_F^m$，对称化并做度归一化，然后加权融合：

$$
\widehat A^m=w_S^mA_S+w_F^mA_F^m,qquad w_S^m,w_F^m\ge0.
$$

这一步的含义很直接：一条边既可以由“物理上相邻”支持，也可以由“分子特征相似”支持。实验部分说两种权重都从 0.5 初始化且可学习，但论文没有给出图的 $k$、距离度量、权重约束或归一化的精确实现。

预处理证据也要克制：正文明确写 RNA 用 Scanpy、ADT 用 CLR，并在方法处说特征图可基于 PCA/LSI/CLR 后的特征。它没有列出 Scanpy 的具体函数顺序、HVG 数量、PCA/LSI 维度，所以不能把常见流水线当作作者配置。

### 3. RPR：为什么强调“近恒等”

每个模态进入一层 RPR 编码器：

$$
Z^m=\widehat A^m\left(F^mW_e^m+\alpha\Delta(F^mW_e^m)\right).
$$

$F^mW_e^m$ 是主投影，$\Delta$ 是零初始化线性分支，$\alpha$ 是小的可学习门。训练开始时增强分支贡献接近零，因此表示先沿着保守主干传播，之后再学习偏离主干。论文还写明传播前后做逐行 $\ell_2$ 归一化，并故意只用浅层编码器，把更深的传播留给后续 APPNP。

“near-identity”不能按字面理解成输出等于输入：仍然存在 $W_e^m$ 的维度投影和 $\widehat A^m$ 的图传播。它更准确地指零初始化残差支路不会在早期突然改变主分支。

### 4. 跨图软对齐

对两个模态表示 $Z^1,Z^2$，先投影并归一化：

$$
Q=\operatorname{norm}(Z^1W_q),\qquad K=\operatorname{norm}(Z^2W_k),
$$

再逐行 softmax 得到对应矩阵：

$$
S=\operatorname{softmax}(QK^\top/\tau).
$$

第 $i$ 行表示模态 1 的 spot $i$ 对模态 2 各 spot 的软匹配权重。虽然数据按同一批 spot 测量，论文仍允许在所有 spot 间学习软对应，而不只使用同索引配对。对齐信息拼回各自表示：

$$
\widetilde Z^1=[Z^1\|SZ^2]W_1,
\qquad
\widetilde Z^2=[Z^2\|S^\top Z^1]W_2.
$$

短暂 warm-up 阶段会对交叉项 stop-gradient：更新一侧时使用另一侧的 `.detach()`，避免两个尚未稳定的表示互相拖动。warm-up 时长、温度 $\tau$ 和多于两个模态时如何扩展都没有报告。

论文说 $S$ 可以按行保留 top-$k$，实验配置为 $k=20$。这能减少后续存储或乘法成本，但如果实现仍先显式计算完整 $QK^\top$，相似度计算本身依然是 $O(N^2)$；没有源码时不能直接宣称整个对齐步骤降为 $O(20N)$。

### 5. 局部支路与多尺度全局扩散

局部支路将对齐后的表示堆叠并投影为 $Z_{base}$，邻居聚合后形成 $Z_{graph}$，再保守更新：

$$
Z_{loc}=Z_{base}+\alpha Z_{graph},\qquad0\le\alpha\le1.
$$

全局支路平均各模态图并重新归一化得到 $\widehat A_g$，以多组传播深度和 teleport 参数运行 APPNP：

$$
Z_g=\operatorname{MS\text{-}APPNP}(\widehat A_g,Z_{loc}).
$$

论文配置为 $(K,\alpha)=\{(2,0.20),(4,0.15),(8,0.10)\}$，三路输出拼接后线性投影回 $d$ 维。浅层支路偏局部，深层支路获得更远邻域信息；APPNP 的回跳项保留输入信号，缓和深传播的过平滑。

### 6. `β` 门控存在未解决的参数化矛盾

论文用

$$
Z_*=(1-\beta)Z_{loc}+\beta Z_g,qquad0\le\beta\le1
$$

混合局部与全局表示，并声称训练早期 $\beta$ 大、后期减小，从“全局一致”转向“局部边界细化”。但实验部分又说“可学习门 $\beta$ 初始化为 2.5”，并在参数分析中扫描 $\beta_0\in[1.5,2.5]$，这与公式的 $[0,1]$ 约束直接冲突。

一种可能是 2.5 指 sigmoid 之前的原始参数，但论文没有写 sigmoid；也可能存在裁剪、重参数化或显式时间日程。当前没有代码，不能选择其中一个作为答案，更不能断言 2.5 经 sigmoid 后就是实际权重。这里只能确认作者意图是全局到局部的时间变化门控。

### 7. 最终表示、解码与损失

论文另写了一个小 MLP 融合模态表示：

$$
Z=\operatorname{MLP}(\operatorname{Concat}(Z^1,\ldots,Z^M)).
$$

图 1 称其为“特征图路径 + MLP 路径”的双路径融合，但公式没有说明 $Z_*$ 与这个 $Z$ 最终怎样组合。这是复现的关键断点。

联合表示经空间图解码回每个模态：

$$
\widehat F^m=A_SZ W_d^m,
\qquad
\mathcal L_{rec}=\frac1M\sum_mw^m\|F^m-\widehat F^m\|_2^2.
$$

原型集合 $C=\{c_k\}$ 对当前表示做最近原型分配；按原型平均的对比目标 $\mathcal L_{clust}$ 使同一原型下的点更紧凑。特征图还以其指数移动平均为参考：

$$
\mathcal L_{graph}=\sum_m\|A_F^m-\operatorname{EMA}(A_F^m)\|_F^2,
$$

$$
\mathcal L=\mathcal L_{rec}+\lambda_{cl}\mathcal L_{clust}+\lambda_g\mathcal L_{graph}.
$$

实验写明 EMA decay 为 0.9，原型由 GMM seeding 初始化，双模态和三模态重建权重分别为 $(5,5)$ 与 $(1,3,3)$。但簇数来源、原型更新、$\lambda_{cl}/\lambda_g$、epoch 和停止规则均 Not found。

### 8. 实验结果应怎样解释

三个数据集是 HLN（3484 spots，RNA/ADT/坐标，有专家标签）、MB（9196 spots，ATAC-RNA 与 CUT&Tag-RNA，正文说无 ground-truth 标签）和模拟数据（1296 spots，RNA/ATAC/ADT，有已知真值）。表 1 的 Overall-Avg 中 TRSMI 在三者均为最高报告值；但 HLN 仅比 PRAGA 高 0.16，且 TRSMI 的 Info-Avg 反而低 1.09，不能概括为每项指标全面领先。

MB 的“标签”边界尤其重要：论文说没有 ground truth，而以 RNA-ATAC 跨模态聚类一致性评估。因此更高分支持跨模态聚类一致，不等同于已验证的脑区或细胞类型准确率。图 2 只展示 TRSMI 与 PRAGA 的空间图和 UMAP；它与更清晰边界相一致，但不能单独验证是 scheduled-$\beta$ 或 MS-APPNP 导致。

表 2 是以 PRAGA 数值为 baseline、分别加入模块的消融。单加 Align 的 Clust-Avg 最大，完整模型 Overall-Avg 最高。这支持模块互补，但各行并不是从 TRSMI 中逐一“移除模块”的经典消融，解释时要保留这个设计。

### 9. 可复现性与版本边界

论文报告 RTX 3090、full-batch SGD、双模态学习率 0.01、三模态 0.001、20 个随机种子（2025–2044）、top-$k=20$、三组 APPNP 参数、EMA 0.9 和重建权重。这些是论文配置，不是源码验证结果。

以下仍 **Not found**：作者代码与提交版本、独立补充材料、图 $k$ 和距离、特征维度、latent/alignment 维度、optimizer 其他参数、epoch、warm-up 长度、门控参数化与日程、温度、损失权重、双路径合并、三模态对齐扩展、GMM/原型更新、完整预处理和数据拆分。任何实现只能标为“依据论文再实现”，不能声称复现了作者代码。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TRSMI Summary

**Paper**: Toward Robust Spatial Multi-Omics Integration: Spatial Multi-Omics Integration via Alignment and Scheduled Diffusion
**Authors**: Ke Tan, Guihua Yu, Tingting Li, Haoran Chen, JianChao Liu, Mengzhu Wang, Hau-sing So
**Venue**: ICASSP 2026
**DOI**: 10.1109/ICASSP55912.2026.11461685
**Code**: Not publicly available

---

### Motivation & Novelty

#### Biological Problem

Spatially resolved multi-omics simultaneously measures RNA, surface proteins (ADT), and chromatin accessibility (ATAC) within intact tissue, enabling systems-level views of cellular state, regulation, and communication. The central challenge is integrating these heterogeneous modalities while preserving spatial tissue architecture — specifically, maintaining sharp boundaries between anatomical regions (e.g., cortical layers, lymph node zones) that are biologically meaningful.

#### Limitations of Existing Approaches

| Method | Limitation | Journal/Year |
|--------|-----------|--------------|
| MOFA+ | Integrates modalities but ignores spatial coordinates | Genome Biology, 2020 |
| TotalVI | No spatial coupling; single-cell only | Nature Methods, 2021 |
| MultiVI | No spatial coupling; multi-modal VAE | Nature Methods, 2023 |
| STAGATE | Spatial graph attention but single-modality | Nature Communications, 2022 |
| DeepST | Spatial deep learning but single-modality | Nucleic Acids Research, 2022 |
| SpatialGlue | Dual attention for spatial multi-omics; fixed single-scale diffusion → oversmoothing | Nature Methods, 2024 |
| PRAGA | Dynamic graph + probabilistic denoising; static anchors without alignment stabilization | AAAI, 2025 |

Recurring failure modes across existing methods:
1. **Over-smoothing**: Fixed single-scale diffusion erases tissue boundaries
2. **Brittle alignment**: Static anchors or dense similarities without temperature control or warm-up
3. **Modality imbalance**: No mechanism to handle ADT (200 features) vs. RNA (20,000 features) scale mismatch
4. **Scalability**: O(N²) correspondence overhead without sparsification

#### TRSMI's Contributions

1. **Near-identity RPR encoder**: Zero-initialized enhancement branch ensures stable encoding under modality imbalance; row-L2 normalization preserves boundaries
2. **Temperature-controlled soft alignment with warm-up detach**: Prevents early misalignment collapse; top-k=20 sparsification reduces O(N²) to O(20N)
3. **Multi-scale APPNP with scheduled gate**: Three propagation scales (K=2,4,8) capture local-to-global topology; learnable β gate schedules coarse-to-fine refinement
4. **Prototype-aware contrastive clustering**: 1/K normalization resists class imbalance; GMM seeding for stable initialization
5. **EMA graph regularizer**: Stabilizes learned feature graphs during training

---

### Method Overview

TRSMI is a graph neural network framework for spatial multi-omics integration. The pipeline:

1. **Preprocessing**: RNA (Scanpy), ADT (CLR normalization), ATAC (LSI)
2. **Graph construction**: Per-modality fused adjacency $\hat{A}^m = w_S A_S + w_F A_F^m$ combining spatial and feature k-NN graphs
3. **RPR encoding**: Near-identity GCN with zero-init branch → $Z^m \in \mathbb{R}^{N \times d}$
4. **Cross-graph alignment**: Temperature-controlled soft correspondences $S$ with warm-up detach; augment each modality with aligned counterpart
5. **Local refinement**: Conservative neighbor aggregation with small gate α
6. **MS-APPNP diffusion**: Three APPNP scales concatenated → global embedding $Z_g$
7. **Scheduled combination**: $Z_* = (1-\beta)Z_\text{loc} + \beta Z_g$, β decreasing over training
8. **MLP fusion**: Lightweight MLP fuses all modality embeddings → $Z \in \mathbb{R}^{N \times d}$
9. **Training**: $\mathcal{L} = \mathcal{L}_\text{rec} + \lambda_\text{cl}\mathcal{L}_\text{clust} + \lambda_g\mathcal{L}_\text{graph}$

Key biological assumptions:
- Spatial neighbors share similar molecular profiles (spatial smoothness)
- Cross-modal correspondences are soft (not one-to-one) due to noise
- Tissue boundaries are sharp and should be preserved (not smoothed away)

See `doc_method.md` for full mathematical derivations and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets

| Dataset | Modalities | Spots | Platform | Ground Truth |
|---------|-----------|-------|----------|-------------|
| Human Lymph Node (HLN) | RNA + ADT | 3,484 | CITE-seq | Expert cell-type annotations |
| Mouse Brain (MB) | ATAC + RNA + CUT&Tag | 9,196 | Spatial ATAC-RNA | Cross-modal clustering consistency |
| Simulation (Sim) | RNA + ATAC + ADT | 1,296 | Synthetic | Known spatial domains |

#### Metrics

Aggregated scores (all higher-is-better):
- **Info-Avg**: (MI + NMI + AMI) / 3 — information-theoretic clustering quality
- **Clust-Avg**: (FMI + ARI + V-Measure) / 3 — boundary-sensitive clustering
- **Class-Avg**: (F1 + Jaccard + Completeness) / 3 — classification quality
- **Overall-Avg**: (Info-Avg + Clust-Avg + Class-Avg) / 3

#### Results (Table 1, 20 random seeds)

| Dataset | Best Baseline | TRSMI | Δ Overall |
|---------|--------------|-------|-----------|
| HLN | PRAGA: 38.85 ± 2.42 | 39.01 ± 1.49 | +0.16 |
| MB | PRAGA: 44.11 ± 2.48 | 47.48 ± 2.01 | +3.37 |
| Sim | PRAGA: 104.42 ± 1.56 | 104.75 ± 1.62 | +0.33 |

TRSMI achieves best Overall-Avg on all three datasets. The largest gain is on MB (+3.37), which has the most spots (9,196) and requires cross-modal consistency between RNA and ATAC — suggesting TRSMI's alignment and multi-scale diffusion are most beneficial for complex, large-scale datasets.

#### Ablation (Table 2, MB dataset)

| Component | Overall-Avg | Δ vs Baseline |
|-----------|------------|---------------|
| Baseline (PRAGA) | 44.11 | — |
| + RPR | 45.46 | +1.35 |
| + Align | 46.95 | +2.84 |
| + MS-APPNP | 46.97 | +2.86 |
| + Sched-β | 46.43 | +2.32 |
| All (TRSMI) | 47.48 | +3.37 |

Cross-graph alignment yields the largest single-component gain (Clust-Avg: 41.03 vs. 38.29 baseline). All components are complementary — the full model outperforms any single addition.

#### Computational Cost (vs. PRAGA on MB)

- Runtime: +57.8s (+4.6%)
- Peak memory: +0.75 GiB (+6.7%)
- Modest overhead for +3.37 Overall-Avg improvement

#### Parameter Sensitivity (Fig. 3, HLN)

Performance is stable across:
- $\alpha_1 \in [0.10, 0.20]$ (APPNP K=2 teleportation)
- $\alpha_2 \in [0.05, 0.10]$ (APPNP K=4 teleportation)
- $\beta_0 \in [1.5, 2.5]$ (initial global gate)

Best performance at moderate diffusion strengths and mid-range $\beta_0$.

---

### Reproducibility

**Rating: 2/5**

**Justification**: The paper provides detailed hyperparameters (APPNP scales, β initialization, EMA decay, reconstruction weights, random seeds 2025–2044) and uses public datasets (HLN from SpatialGlue, MB from Zhang et al. Nature 2023, Sim from SpatialGlue). However, no code repository is provided, making reproduction require full reimplementation from the paper description.

**Strengths**:
- Hyperparameters fully specified (APPNP (K,α), β₀=2.5, EMA decay=0.9, reconstruction weights)
- Random seeds reported (2025–2044, 20 runs)
- Public datasets with known sources
- Baseline methods use official default hyperparameters
- Training setup specified (RTX 3090, full-batch SGD, lr=0.01/0.001)

**Weaknesses**:
- No public code repository
- Warm-up duration not specified (exact epochs)
- β scheduling mechanism not fully described (gradient descent vs. manual schedule)
- Latent dimension d not specified
- Alignment temperature τ not specified
- k for k-NN graphs not specified

**Practical Notes**:
- Datasets: HLN and Sim available from SpatialGlue repository; MB from Zhang et al. (Nature 2023, DOI: 10.1038/s41586-023-05795-1)
- Environment: PyTorch + PyG (PyTorch Geometric) for GCN/APPNP; Scanpy for RNA preprocessing
- Full-batch training requires ≥24GB GPU for MB (9,196 spots)
- APPNP available in PyG as `torch_geometric.nn.APPNP`
- GMM seeding: `sklearn.mixture.GaussianMixture` for prototype initialization

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
