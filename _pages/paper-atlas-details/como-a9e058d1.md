---
layout: default
permalink: /paper-atlas/como-a9e058d1/
title: "CoMo"
nav: false
description: "CoMo 接收同一批空间位置上配对的两种组学（例如 RNA+蛋白或 RNA+ATAC），分别从“物理邻近图”和“分子特征相似图”提取表示，再用跨模态注意力与 WNN 融合。第二阶段同时约束两种组学的簇语义一致，并让空间邻居在投影空间更接近，最终输出用于聚类、伪时序和差异分析的融合嵌入。 本解读依据本地论文 outputpapermd/PMC13092272/paper."
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
      <span>Briefings in Bioinformatics · 2026</span>
    </div>
    <h1>CoMo</h1>
    <p>Spatial multi-omics integration by cross-modal graph contrastive learning</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1093/bib/bbag192" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CoMo 方法解读：用双图、跨模态融合与两类对比损失寻找空间域

### 一句话理解

CoMo 接收同一批空间位置上配对的两种组学（例如 RNA+蛋白或 RNA+ATAC），分别从“物理邻近图”和“分子特征相似图”提取表示，再用跨模态注意力与 WNN 融合。第二阶段同时约束两种组学的簇语义一致，并让空间邻居在投影空间更接近，最终输出用于聚类、伪时序和差异分析的融合嵌入。

本解读依据本地论文 `paper source/PMC13092272/paper.md`、补充材料、主图 1–6，以及固定提交 `70965cba0ca7df33e426f6a1dd5626347978cdae` 的源码。尤其需要注意：论文的概念流程与源码类结构能对应，但公开入口的默认参数和跨注意力张量形状存在严重可复现性边界，不能把论文结果等同于“当前 `main.py` 默认调用即可得到”。

### 输入、输出和任务

输入是两个观测一一对应的 `AnnData`：

- `adata_omics1` 通常为转录组；
- `adata_omics2` 为蛋白组或染色质可及性；
- 二者都要有 `obsm['spatial']`，并准备低维特征 `obsm['feat']`。

RNA 按论文流程选 3000 个高变基因、总量归一化到 10,000、`log1p` 后 PCA；蛋白做逐细胞 CLR 后 PCA；ATAC 做 TF-IDF/LSI，并在代码中丢弃第一个 LSI 分量。输出的主要对象是 `adata.obsm['CoMo']`，随后可运行 mclust、Leiden 或 Louvain；默认后处理还会用 5 个空间近邻多数投票生成 `refine_CoMo`。

### 第一层：每种组学各建两张图

对每种组学 $m$，CoMo 建立：

1. 空间图 $G_{sm}$：坐标 kNN，普通数据默认 $k=3$，部分技术改为 6；
2. 特征图 $G_{fm}$：在 `feat` 上用 correlation 距离构造 $k=20$ 的 kNN。

邻接矩阵会对称化、加自环并做 $D^{-1/2}(A+I)D^{-1/2}$ 归一化。GCN 更新可写为

$$
H^{(l)}=\sigma\!\left(\widetilde A H^{(l-1)}W^{(l)}+b^{(l)}\right).
$$

空间分支保留组织局部关系，特征分支允许空间上分散但分子相似的 spot 建立联系。之后 `AttentionLayer` 对两个分支逐 spot 计算 softmax 权重并加权合并。

#### 一个关键论文—代码差异

论文文字说不同图分支的权重矩阵“不共享”，但 `Encoder_overall.forward()` 对同一组学的空间图和特征图重复调用同一个 `encoder_omics1[i]`（或 `encoder_omics2[i]`）。因此源码实际是：两种组学之间不共享编码器，但同一组学的空间/特征分支共享 GCN 参数。这个差异会改变模型容量，复现时必须按源码还是按论文二选一并明确记录。

### 第二层：论文设想的反向跨注意力

论文给出的核心思想是把标准注意力

$$
\operatorname{softmax}\left(Q_1K_2^\top/\sqrt{d_k}\right)V_2
$$

改为

$$
\operatorname{softmax}\left(-Q_1K_2^\top/\sqrt{d_k}\right)V_2,
$$

即对低相似度跨模态关系赋更高权重，以强调互补而非冗余信号。源码 `Attention.forward()` 确实执行 `dp = -1 * dp` 后再 softmax。

但当前调用点把每个 spot 的向量变成形状 `(n_spots, 1, latent_dim)`。这里 token 维长度只有 1，所以每个 attention 矩阵在最后一维都是 $1\times1$；无论分数是否取负，softmax 都恒等于 1。也就是说，当前实现中的“反向排序低亲和力 token”在该形状下没有实际选择空间。该块仍包含 value 投影、残差、MLP 和 LayerNorm，因而会变换另一模态表示，但不能把它严格解释为论文所述的跨 spot 低亲和力注意力。这个边界比“代码里有负号”更重要。

### 第三层：WNN 融合

源码可用 Seurat 风格的 Weighted Nearest Neighbors 计算每个 spot 的模态权重 $w_{i1},w_{i2}$：

$$
Z_i=w_{i1}Z_{i1}+w_{i2}Z_{i2}.
$$

WNN 不是每轮都重算：仅在 `epoch % wnn_epoch == 0` 时更新。其他轮次代码回退到构造模型时保存的标量 `self.w1/self.w2`，并不是沿用上一次计算出的每细胞 WNN 权重。因此“缓存 WNN 权重”这一旧解释不准确；真实行为是周期性使用 WNN、其余轮次使用固定模态权重。

### 两阶段优化

#### 阶段 1：重建

融合嵌入分别经两个 GCN decoder 重建两种组学的低维输入：

$$
L_{recon}=\lambda_1\|X_1-\widehat X_1\|^2+\lambda_2\|X_2-\widehat X_2\|^2.
$$

默认权重为 $1:5$。源码使用 `F.mse_loss`，优化器是 AdamW；由于 `weight_decay=0`，更新接近 Adam，但名称仍与论文“Adam”不一致。

#### 阶段 2：簇对齐与邻域对比

两个独立 cluster head 输出 $C_1,C_2$。论文写成单层 $\operatorname{Softmax}(HW_c)$，源码实际是包含两组 BN、ReLU、Dropout 和 Linear 的两层 MLP。cluster loss 让同编号跨模态簇分布作为正对，并把其他簇作为负对。

projection head 把融合表示降到 32 维并归一化。`contrastive_loss()` 的正视图不是第二次随机增强，而是

$$
P^{+}=\widetilde A_{contrast}P,
$$

即每个 spot 的空间邻域聚合表示；对比图默认使用 5 个空间近邻。两类对比损失都加入论文公式未写出的 hard-negative 重加权，cluster loss 还加入簇熵项。

第二阶段源码总损失可概括为

$$
L=L_{recon}+L_{cluster}+5L_{neighbor},
$$

同时第二模态重建仍乘 5。论文把权重记为 $\gamma_1,\gamma_2,\gamma_3$，但源码用一个五元素列表同时承载两个重建权重与两种对比权重。

### 从代码入口读完整流程

1. `main.py::run_algorithms()` 调用 `construct_neighbor_graph()`。
2. `Train_CoMo.__init__()` 把图转为 PyTorch 稀疏归一化邻接矩阵。
3. `Train_CoMo.train()` 实例化 `Encoder_overall` 和 AdamW。
4. 只有 `step_by_step_train=True` 才会调用 `step_by_step_train_model()`；否则训练分支直接 `pass`。
5. 每轮前向经过共享参数的双图 GCN、分支注意力、可选跨注意力、可选 WNN、decoder 与可选 heads。
6. 训练结束后输出 L2 归一化的两模态嵌入和融合 `CoMo`。
7. `clustering()` 先可选 PCA，再运行 mclust/Leiden/Louvain，最后默认空间多数投票精修。

### 公开入口的硬边界

`run_algorithms()` 当前默认：`step_by_step_train=False`、`use_cross_attention=False`、`use_cluster_head=False`、`use_contrastive_loss=False`、`use_WNN=False`。因此直接使用默认入口不会训练模型，也不会启用论文命名的关键模块；随后却仍会对随机初始化网络的前向输出聚类。

教程虽然显式设置 `step_by_step_train=True` 并传入正确的阶段字典，但没有显式打开跨注意力、cluster head、neighbor contrastive 或 WNN，因此仍不是图 1 所示完整 CoMo。与此同时，入口默认 `stage_epochs=1200` 是整数，而训练器 `_update_stage()` 期待包含 `recon` 和 `contrast` 的字典；若用户只打开训练而不覆盖此参数，会在索引整数时失败。可运行完整模型必须显式提供所有开关和形如 `{'recon':300,'contrast':600}` 的阶段配置。

### 主图证据怎样读

- 图 1 是概念架构，不证明当前公开入口已正确启用所有模块。
- 图 2 的模拟数据上 CoMo 报告 ARI 0.9853、NMI 0.9807，接近理想标注；模拟结构和调参条件会使它比真实组织更容易。
- 图 3 的 Human Lymph 优势较小，且对 SpatialGlue 的 ARI 差异不显著（补充统计 $p=0.19$）；Mouse Brain P22 中 COSMOS 数值更高/相近但被作者解释为过平滑。
- 图 4 用小鼠胚胎 E13 展示空间域、marker 与伪时序；伪时序是从融合表示继续运行下游方法，不是 CoMo 训练损失直接输出时间。
- 图 5 的扁桃体没有人工域真值，主要证据是空间一致性、marker 和组织学对应；高 Moran's I 也可能来自过平滑。
- 图 6 的消融支持各模块有贡献，但公开源码默认/教程并未按全模型开关运行，当前快照无法仅靠默认教程验证这些消融值。

### 论文—代码匹配结论

**总体：Medium-Low 可复现性。**

Exact/可直接定位：双图构造、GCN、组学内注意力、负号注意力代码、WNN 类、两个 decoder、cluster/projection heads、两类对比函数和三种下游聚类。

Partial/行为不等价：同一模态双图分支共享权重；跨注意力 token 长度为 1 导致 reversed-softmax 不具选择性；cluster head 与损失比论文公式更复杂；周期外 WNN 使用固定权重而非缓存每细胞权重。

Not reproducible from default path：默认入口不训练且关闭核心模块，教程也未打开完整模块，阶段参数默认类型错误。论文主图所用的确切调用参数、保存权重和从原始数据到所有结果的完整运行记录未在本地快照中得到验证。

因此，当前代码适合研究架构组件和手工修正后实验，不应被描述成“克隆后运行教程即可复现论文”。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## CoMo — Summary

**Paper**: Spatial multi-omics integration by cross-modal graph contrastive learning
**Journal**: *Briefings in Bioinformatics* 27(2), 2026-03
**DOI**: 10.1093/bib/bbag192
**Code**: https://github.com/Lab-Xu/CoMo

---

### Motivation & Novelty

#### Biological Problem

Spatial multi-omics technologies (CITE-seq, Visium+ATAC) profile tissue with multiple molecular layers at spatial resolution. The central challenge is **integrating these modalities** for accurate spatial domain identification while:
1. Preserving spatial tissue organization
2. Leveraging *complementary* signals across modalities (not just shared features)
3. Identifying both spatially coherent compact domains AND dispersed yet transcriptionally distinctive domains

#### Limitations of Existing Methods

| Method | Journal | Year | Limitation |
|--------|---------|------|------------|
| MultiVi | *Nature Methods* | 2023 | Probabilistic VAE; ignores spatial information → disorganized spatial domains |
| SpatialGlue | *Nature Methods* | 2024 | Dual-attention GNN; underutilizes cross-omics dependencies |
| COSMOS | *Nature Communications* | 2025 | Graph-based epigenome-transcriptome fusion; over-smoothing merges distinct domains |
| CANDIES | *bioRxiv* | 2025 | Diffusion model + contrastive; high compute cost; no specific spatial neighborhood processing |
| SpaGCN | *Nature Methods* | 2021 | Single modality only |
| STAGATE | *Nature Communications* | 2022 | Single modality only |
| GraphST | *Nature Communications* | 2023 | Single modality only |
| STAIG | *Nature Communications* | 2025 | Image-aided contrastive; single modality |

#### CoMo's Contributions

1. **Reversed softmax cross-attention**: Amplifies low-affinity cross-modal associations (complementary signals) while suppressing high-affinity redundant ones — mechanistically novel approach to cross-modal fusion

2. **Multi-objective contrastive optimization**: Dual contrastive losses operating at cluster level (semantic alignment) and instance level (spatial coherence) simultaneously

3. **Two-phase training**: Stage 1 reconstruction denoises individual modalities; Stage 2 contrastive learning enhances discriminative power without forgetting reconstruction quality

4. **Combined compact + dispersed domain identification**: Cluster-aware loss aligns cross-modal semantics while neighbor-aware loss enforces spatial coherence — both types of domain structure captured

---

### Method Overview

CoMo implements a **four-stage workflow**: preprocessing → pretraining → fused embedding extraction → downstream analysis.

#### Core Architecture

**Dual-branch GCN per modality**: Each modality (RNA, ATAC/protein) processed through two parallel GCN branches — spatial proximity graph (k=3 KNN) and feature similarity graph (k=20 correlation KNN) — then merged via intra-modal attention.

**Reversed cross-attention**: Cross-modal attention using negated attention scores (`-QK^T/√d_k`) before softmax. Mathematically equivalent to `softmax(-x)` ("re-softmax"), which assigns high attention weights to *low-affinity* cross-modal pairs — deliberately seeking complementary rather than redundant signals.

**WNN fusion**: Per-cell adaptive weighting of the two cross-attended modality representations, using Seurat v3 Weighted Nearest Neighbors to determine modality reliability per spot.

**Stage 2 contrastive heads**:
- *Cluster heads*: Independent MLPs predicting cluster probability distributions; aligned via cross-modal contrastive loss at cluster level
- *Projection head*: 32-dim projection for instance-level spatial contrastive learning, with spatial neighborhood aggregation as positive pairs

See `doc_method.md` for full mathematical derivation and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets

| Dataset | Spots | Modalities | Features | Task |
|---------|-------|-----------|----------|------|
| Simulation | 1,296 | RNA+ATAC | 1000+1000 | Domain ID (ground truth) |
| Human Lymph | 3,484 | RNA+protein | 18085+31 | Domain ID (expert annotation) |
| Mouse Brain P22 | 9,215 | RNA+ATAC | 24027+18005 | Domain ID (anatomical atlas) |
| Mouse Embryo E13 | 2,187 | RNA+ATAC | 24017+15748 | Domain ID + trajectory |
| Human Tonsil | 4,194 | RNA+protein | 18085+54580 | Domain ID (no ground truth → Moran's I) |

#### Baselines Compared

9 methods: MultiVi (2023), SpaGCN (2021), STAGATE (2022), GraphST (2023), STAIG (2025), SpatialGlue (2024), COSMOS (2025), CANDIES (2025) + CoMo

#### Metrics

Primary: ARI, NMI. Additional: MI, AMI, Homogeneity, V-measure (supervised); Moran's I (unsupervised).

#### Key Results

**Simulated (RNA+ATAC)**:
- CoMo: ARI=0.985, NMI=0.981 (near-perfect)
- Outperforms SpatialGlue by 5.73% ARI, CANDIES by 2.7%, GraphST by 1.84%
- Sharper boundaries, no scattered spots (Figure 2b)

**Human Lymph (RNA+protein, 3,484 spots)**:
- CoMo: ARI=0.299, Homogeneity=0.393, V-measure=0.400 (best)
- Uniquely identifies capsule/pericapsular adipose tissue distinction
- UMAP reconstructs developmental trajectory (Figure 3c)
- Statistical significance: p<0.001 vs. most methods; p=0.19 vs. SpatialGlue on ARI (not significant)

**Mouse Brain P22 (RNA+ATAC, 9,215 spots)**:
- CoMo: ARI=0.390, NMI=0.580 (best among informative methods)
- COSMOS achieves similar metrics but through over-smoothing (confirmed in paper)
- Accurately resolves L5/L6a/L6b cortical boundary (Figure 3e)

**Mouse Embryo E13 (RNA+ATAC, 2,187 spots)**:
- CoMo: ARI=0.366, all 6 metrics best
- **4.83% ARI margin** over second-best
- Marker genes validated (Snhg11, Ttyh1, Zbtb20, Six3) with adjusted p<0.05 (Figure 4d)
- Correct ventricular zone → subpallium → pallium developmental trajectory (Figure 4e)

**Human Tonsil (RNA+protein, 4,194 spots)**:
- No ground truth → Moran's I evaluation
- CoMo: Moran's I=0.601 (best balance — spatial coherence without over-smoothing)
- COSMOS: 0.780 (highest but over-smoothed, fails GC identification)
- Correctly identifies PCNA+/CD22+ germinal center core (Figure 5b,d)
- IL7R/CD22 marker genes significant (Table S11, p<10⁻¹³⁵)

#### Ablation Study (Figure 6)

All three components contribute non-redundantly across all datasets:
- Removing reversed cross-attention: ~5% ARI drop (simulation)
- Removing cluster-aware loss: ~4% ARI drop
- Removing neighbor-aware loss: ~6% ARI drop (largest contribution)

#### Computational Efficiency

| Dataset | CoMo | COSMOS | CANDIES | SpatialGlue |
|---------|------|--------|---------|-------------|
| Simulation (1296) | 131s | 30s | 190s | 30s |
| Mouse Embryo (2187) | 150s | 60s | 250s | 70s |
| Human Lymph (3484) | 194s | 70s | 440s | 30s |
| Mouse Brain (9215) | 554s | 170s | 2800s | 120s |

CoMo is faster than CANDIES by 5× (Mouse Brain); runtime scales near-linearly with spot count.

---

### Reproducibility: 1.5/5

**Justification**:

**Positives**:
- Code publicly available with MIT-compatible license
- Tutorial notebook provided with Human Tonsil example
- All hyperparameters documented (Table S5)
- All datasets publicly accessible (zenodo, UCSC cell browser, 10× Genomics)
- Deterministic seeding (`fix_seed`) implemented

**Negatives and Pitfalls**:
- **GCN weight sharing discrepancy**: Paper states "non-shared weights" but code shares them — readers implementing from paper description may get different results
- **Cluster head architecture underdescribed**: Paper's `Softmax(H W)` suggests single linear layer but code uses deep 2-layer MLP with BatchNorm and Dropout
- **Data requires manual download**: Google Drive links in repo for datasets/weights (not automated)
- **R dependency**: mclust clustering requires R + rpy2 — installation nontrivial on many systems
- **Environment requirements**: PyTorch 1.11.0+cu113, scanpy 1.9.1, old versions may conflict with modern environments
- **stage_epochs bug**: `run_algorithms` passes `stage_epochs=1200` (integer) but `Train_CoMo.__init__` expects dict — may cause silent failures
- **Hard negatives undocumented**: The bias-corrected hard negative mining in contrastive losses is not described in paper and affects loss magnitude
- **Default entry point is not the paper model**: it does not train and disables cross-attention, WNN, cluster head and neighbor loss; the tutorial turns on training but still leaves those module flags disabled
- **Reversed attention is non-selective in the current call shape**: tensors have one token per spot, so softmax is always 1 and negating the score cannot prioritize low-affinity alternatives

**Practical notes**: Users must explicitly enable training and each intended module, pass a stage-epoch dictionary, and inspect tensor shapes before treating the output as CoMo. Set `random_seed` explicitly; defaults differ across files. The `refine_CoMo` key is the post-refinement output, not the raw clustering label.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
