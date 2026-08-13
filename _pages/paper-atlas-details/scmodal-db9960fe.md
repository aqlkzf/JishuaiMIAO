---
layout: default
permalink: /paper-atlas/scmodal-db9960fe/
title: "scMODAL"
nav: false
wide: true
description: "scMODAL 面向的是未配对单细胞多组学：两个数据集的细胞不同、特征也不同，但研究者知道少量正相关的跨模态特征链接，例如 RNA 基因表达与 ATAC gene activity，或蛋白丰度与其编码基因表达。方法不是只在这些共有特征上整合，而是让各模态编码器读取自己的完整高变特征，同时只用链接特征寻找跨模态锚点。"
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
      <span>Nature Communications · 2025</span>
    </div>
    <h1>scMODAL</h1>
    <p>scMODAL: a general deep learning framework for comprehensive single-cell multi-omics data alignment with feature links</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-60333-z" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scMODAL">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/gefeiwang/scMODAL" target="_blank" rel="noopener noreferrer" aria-label="Open code for scMODAL">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scMODAL：用少量特征链接约束跨模态分布对齐

### 核心问题

scMODAL 面向的是**未配对**单细胞多组学：两个数据集的细胞不同、特征也不同，但研究者知道少量正相关的跨模态特征链接，例如 RNA 基因表达与 ATAC gene activity，或蛋白丰度与其编码基因表达。方法不是只在这些共有特征上整合，而是让各模态编码器读取自己的完整高变特征，同时只用链接特征寻找跨模态锚点。

一句话概括其受力关系：GAN 负责把两个潜在分布混在一起，MNN 锚点告诉网络哪些细胞应当对应，几何正则防止为了混合而抹掉模态内生物结构，自编码与跨域潜在一致性则让表示还能重建和跨模态生成特征。

### 本次解释的证据边界

- 论文：`paper source/PMC12122792/paper.md`，DOI `10.1038/s41467-025-60333-z`。
- 主图：`paper source/PMC12122792/images/` 中图 1–5。
- 补充：`output_paper_supp_md/paper_supp1/vlm/paper_supp1.md`，以及工作区内三个 supplement PDF。
- 代码：`scMODAL_code/`，GitHub `https://github.com/gefeiwang/scMODAL`，本地记录提交 `7ef67e2c2494bc4b944f5de6a966ae37750ebc58`，包内版本为 `1.0.0`。
- 论文还给出归档 DOI `10.5281/zenodo.15304076`；本次没有联网比对 Zenodo 包与本地 Git 提交的逐文件同一性。因此以下 paper–code 结论严格限定于本地快照。

### 输入：完整特征与链接特征各司其职

设两个模态矩阵为

$$
X_A\in\mathbb{R}^{n_A\times p_A},\qquad
X_B\in\mathbb{R}^{n_B\times p_B}.
$$

编码器读取 $X_A,X_B$ 的全部列；另有成对链接矩阵

$$
\widetilde X_A,\widetilde X_B\in\mathbb{R}^{n\times s},
$$

其第 $j$ 列代表一个已知正相关特征对。这里的 $s$ 可以远小于 $p_A,p_B$。图 1a 用少量蓝色连线强调：特征链接是寻找锚点的先验，不是要求细胞成对，也不是要求两个模态拥有完全相同的特征空间。

代码最简单的 `preprocess()` 有一个易错契约：它把 `.X` 直接作为网络输入，并假定**前 `shared_gene_num` 列**已经按相同顺序放置链接特征（`scmodal/model.py:43-53,149-153`）。函数不按名称校验对应关系，也不自动重排。列顺序错了仍可训练，但 MNN 锚点会失去生物含义。

### 网络：两个编码器、两个生成器、一个判别器

每个模态拥有独立编码器和生成器：

$$
z_A=E_A(x_A),\quad z_B=E_B(x_B),\qquad
\hat x_A=G_A(z),\quad \hat x_B=G_B(z).
$$

本地 `scmodal/networks.py:7-41` 的编码器/生成器都是“输入 → 512 ReLU → 输出”的两层 MLP；默认潜在维数为 20。判别器为“20 → 512 ReLU → 512 ReLU → 1”，输出被截到 $[-50,50]$（`43-62`）。没有 batch normalization 或 dropout。

训练默认每个模态有放回抽 500 个细胞，固定 10,000 步，Adam 学习率 0.001、weight decay 0.001；每次生成器更新前执行五次判别器更新（`model.py:15-37,83-159`）。所以论文所说“五百万次抽样”是 $500\times10,000$ 的采样次数，不是五百万个互不重复细胞。

### 五股训练力量

#### 1. 对抗分布对齐：只保证整体分布难以区分

判别器试图区分 $z_A$ 与 $z_B$，编码器反向让这种区分变难。代码采用 softplus 形式：

$$
L_D=\mathbb{E}_{z_A}\log(1+e^{-D(z_A)})+
\mathbb{E}_{z_B}\log(1+e^{D(z_B)}),
$$

并给生成侧使用相反符号的对应项（`model.py:126-144`）。它能混合模态分布，却不知道“哪个 A 细胞应对应哪个 B 细胞”。补充图 7 的消融支持 GAN 对混合的重要性，但也说明仅靠 GAN 不足以得到正确细胞类型配对。

#### 2. 模态内自编码：保留可重建信息

$$
L_{AE}=\|G_A(E_A(x_A))-x_A\|_2^2+
\|G_B(E_B(x_B))-x_B\|_2^2.
$$

这迫使潜在表示保留各模态完整特征，而非只保留少量链接特征。代码对应 `model.py:109-114,133-136`。

#### 3. 跨域潜在一致性：翻译后仍回到同一潜在位置

先把 $A$ 的潜在表示用 $G_B$ 生成 B 空间特征，再用 $E_B$ 编回潜在空间；反向同理：

$$
L_{LA}=\|z_A-E_B(G_B(z_A))\|_2^2+
\|z_B-E_A(G_A(z_B))\|_2^2.
$$

本地代码把它独立命名为 `loss_LA`（`model.py:111-116,138-141`）。论文把模态内与跨域一致性共同放在 autoencoding consistency 叙述和公式下，本地实现却给 `L_AE` 与 `L_LA` 各一个独立权重，默认均为 10。因此复现时不能只设置一个论文里的 $\lambda_{AE}$ 就认为完全等价。

#### 4. MNN 锚点：用链接特征决定细胞对应方向

在每个 minibatch 内，代码只截取链接特征，通过 Annoy 的 angular 距离从 A 找 B 的 30 近邻、再从 B 找 A 的 30 近邻，取双向交集（`scmodal/utils.py:13-34`）。若 $S_{ij}=1$ 表示互近邻，则

$$
L_{MNN}=\frac{\sum_{ij}S_{ij}\,\operatorname{mean}(z_{A,i}-z_{B,j})^2}
{\sum_{ij}S_{ij}}.
$$

它把锚点潜在距离拉近。图 3 和补充图 7 的重点正是：只有 12 个共享蛋白时仍能对齐，但去掉锚点会出现几乎完全错误的细胞类型匹配。这也划定了方法边界——如果给定链接特征不是可靠正相关，MNN 会把错误先验传入模型。

实现还有一个数值边界：`model.py:150-153` 未检查当前随机批次是否存在 MNN；若 $\sum S=0$，除法可能产生 NaN。论文没有讨论这一失败分支。

#### 5. 几何正则：防止把不同细胞状态过度揉平

对批内每对细胞，代码在输入空间和潜在空间计算

$$
K_{ij}=\exp\left[-\frac{\operatorname{mean}_f(x_i-x_j)^2}{2}\right],\qquad
K^z_{ij}=\exp\left[-\frac{\operatorname{mean}_d(z_i-z_j)^2}{2}\right].
$$

然后最大化每个细胞对应的两行核相似向量之间的余弦相似度，即最小化其负值（`model.py:117-124,146-147`）。这保留的是批内相对几何，而不是逐点重建。代码把余弦值上截到 0.975；一旦达到阈值，继续优化不再奖励，避免该项垄断训练。

### 总目标及论文—代码超参数差异

本地生成侧总损失为

$$
L_G=\lambda_{GAN}L_{GAN}+\lambda_{AE}L_{AE}
+\lambda_{LA}L_{LA}+\lambda_{MNN}L_{MNN}
+\lambda_{Geo}L_{Geo}.
$$

`Model.__init__` 默认权重为 $(1,10,10,1,10)$（`model.py:15-37`）。论文 Methods 报告 $\lambda_{AE}=10$、$\lambda_{Anchor}=1$、$\lambda_{Geo}=1$，并未把 $L_{LA}$ 作为独立默认项列成同样的接口。因此至少有两点不能混写：代码额外拆出 $\lambda_{LA}=10$；代码默认 $\lambda_{Geo}=10$，而论文训练细节写 1。工作区没有证据证明论文各图究竟由默认构造器还是外部显式覆盖参数生成，故应标为版本/配置不确定，而不是任选一边称为唯一真值。

### 输出与跨模态插补

`eval()` 载入 checkpoint 后产生三个直接结果（`model.py:179-209`）：

- `latent = [E_A(X_A);E_B(X_B)]`：用于 UMAP、标签迁移和整合指标；
- `data_Aspace = [X_A;G_A(E_B(X_B))]`：把 B 细胞翻译到 A 特征空间；
- `data_Bspace = [G_B(E_A(X_A));X_B]`：把 A 细胞翻译到 B 特征空间。

因此正确的 A→B 插补组合是 $G_B(E_A(x_A))$，而不是把编码器/生成器次序倒置。`get_imputed_df()` 可按保存的均值与标准差反缩放，并对重复 feature name 取均值（`model.py:211-225`）。这些输出是模型预测，不是新获得的实测分子值；由插补矩阵计算出的 gene–protein、gene–peak 相关网络应视为候选关系，还需独立实验证据。

### 三模态及更多数据集

当有 $L\ge3$ 个模态时，代码为每个模态建立独立 $E_l,G_l$，只在相邻数据集 $(l,l+1)$ 之间建立 $L-1$ 个判别器、MNN 与跨域一致性项（`model.py:227-347`）。因此输入顺序定义了哪几对模态直接相连；非相邻模态通过链式共同潜在空间间接联系。补充图 18 比较了 TEA-seq 的不同顺序并报告稳定表现，但这不是数学上的完全置换不变保证。

多模态接口 `integrate_datasets_links()` 接收显式链接列索引，`integrate_datasets_feats()` 接收已提取的成对 MNN 特征，较两模态 `preprocess()` 更清楚。另一个重要实现边界是：`preprocess_additional_inputs()` 虽把替代 MNN 特征保存到 `self.feat_A_MNN/self.feat_B_MNN`，但当前两模态 `train()` 在 `model.py:150` 仍从 `self.emb_A/self.emb_B` 前若干列找 MNN，并未读取这些属性。也就是说，注释所说“网络输入用 ATAC LSI、MNN 用 gene activity layer”的两模态路径在该提交中没有真正接通；调用者若依赖它，会得到与文档意图不同的锚点。

### 主图提供了什么证据

- **图 1** 是机制图：完整特征进入网络、少量链接特征产生锚点；GAN、锚点和几何正则共同作用；输出用于整合、插补和下游分析。
- **图 2** 用配对 CITE-seq 的 RNA/ADT 作为未配对输入、真实配对仅用于评估。论文报告粗/细标签转移约 98%/86%，蛋白插补平均 Pearson 相关 0.53。它支持方法在该数据上的表现，不等于所有蛋白都可由 RNA 准确预测。
- **图 3** 检验只有 12 个共享蛋白的 CITE-seq/CyTOF，以及 TEA-seq 三模态整合；它与补充消融共同说明锚点决定正确匹配、几何项保护细胞类型结构。
- **图 4** 将 RNA 与 ATAC 对齐，并以 Fam107a 展示插补表达比简单 gene activity 更符合 RNA 图谱；随后将插补表达与局部峰可及性相关来提出 gene–peak links。这里是计算候选关系，不是因果调控证明。
- **图 5** 把 CODEX、RNA、ATAC 三模态整合，用 RNA 标签细化扁桃体 B 细胞空间亚群，再用插补基因进入 COMMOT。Visium 中相似空间结构提供外部支持，但样本和技术差异仍限制逐细胞真值验证。

补充图 1–6、8–17扩展数据集与下游结果；图 7 是组件消融；图 18 是模态顺序；图 19–20 是计算规模。论文计算基准使用单张 RTX 5000，并排除标准预处理时间，不能把其运行时直接外推到 CPU 或包含预处理的端到端流程。

### 可复现性与实现边界

#### 可以由本地代码直接确认

- 20 维潜在空间、512 隐层、独立模态编码器/生成器和对抗判别器；
- 五项生成损失与五次判别器更新；
- Annoy angular MNN、默认 $k=30$、批量 500、10,000 步；
- A→B/B→A 解码插补，以及相邻链式多模态扩展；
- Git 快照、包版本 1.0.0 和环境依赖上限 PyTorch 1.13.1。

#### 需要明确保留的不一致或缺口

- 论文把 AE/跨域一致性合并叙述，代码拆为 `lambdaAE` 与 `lambdaLA`；
- 论文写 $\lambda_{Geo}=1$，代码构造器默认 10；
- 两模态 additional-input MNN 属性在训练中未使用；
- MNN 空批次缺少除零保护；
- 代码仓只有包核心和一张 demo overview，没有论文全部分析脚本、输入处理与作图流水线；
- 此次未创建旧 PyTorch 环境、未训练模型、未复算 benchmark 或插补网络。

### 最简阅读模型

可以把 scMODAL 理解成以下顺序：

1. 各模态完整特征各自编码，少量链接特征只用来找 MNN；
2. GAN 让潜在分布难以区分；
3. MNN 约束正确的跨模态方向；
4. 自编码、跨域潜在一致性和几何核防止信息丢失与过度校正；
5. 共同潜在空间用于整合，交叉生成器用于未测特征插补。

方法真正的关键不是“用了 GAN”，而是用链接特征锚点纠正 GAN 可能产生的错误匹配，再用全特征几何保护模态独有结构。相应地，它最敏感的输入也正是链接特征的质量、顺序和批内 MNN 是否存在。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scMODAL: Single-Cell Multi-Omics Data Alignment with Feature Links

**Paper**: scMODAL: a general deep learning framework for comprehensive single-cell multi-omics data alignment with feature links
**Journal**: Nature Communications 16, 4994 (2025)
**DOI**: 10.1038/s41467-025-60333-z
**Authors**: Gefei Wang, Jia Zhao, Yingxin Lin, Tianyu Liu, Yize Zhao, Hongyu Zhao (Yale University)
**Code**: https://github.com/gefeiwang/scMODAL

---

### Motivation & Novelty

#### Biological Problem

Single-cell multi-omics technologies enable measuring transcriptomics, epigenomics, and proteomics from different cells in different experiments — but these datasets cannot simply be merged because they share no common cells and often no common features. "Diagonal integration" (aligning modalities with distinct feature spaces) is fundamental to joint multi-omics analysis of immune microenvironments, brain cell subtypes, and disease mechanisms. Without accurate integration, biologists must work with each modality in isolation, losing the cross-modal regulatory insights that reveal why different cell types have distinct functional identities.

#### Why Existing Methods Fall Short

- **Linear projection methods** (MaxFuse, Nat. Biotechnol. 2024; bindSC, Genome Biol. 2022): Use canonical correlation analysis (CCA) to learn linear projections. Cannot capture complex nonlinear batch effects, and fail when cross-modality feature correlations are weak (e.g., RNA–protein, where post-transcriptional regulation decouples mRNA from protein levels).
- **Graph-based deep learning** (GLUE, Nat. Biotechnol. 2022; Monae, Nat. Commun. 2024; CoVEL): Use knowledge graphs of gene-peak links. Work well for RNA–ATAC where links are well-characterized, but perform poorly for weakly-linked modalities like RNA–protein where regulatory circuits are incomplete.
- **Paired-cell-requiring methods** (totalVI, Nat. Methods 2021; MultiVI, Nat. Methods 2023; MIDAS, Nat. Biotechnol. 2024; scButterfly, Nat. Commun. 2024; SpatialGLUE, Nat. Methods 2024): Require (at least partially) matched cells across modalities — inapplicable when datasets come from different experiments.
- **Shared-feature-only methods** (Portal, Nat. Comput. Sci. 2022; Seurat, Cell 2019; scVI, Nat. Methods 2018; iMAP, Genome Biol. 2021): Discard modality-unique features, losing biology captured in unshared features.

#### scMODAL's Unique Contributions

1. **Flexible weak-link integration**: Uses only a limited set of positively correlated "linked" features (not a comprehensive feature graph) as weak anchors via MNN, enabling RNA–protein integration even with dozens of markers.
2. **Full feature utilization**: Encodes all modality-unique features (not just shared ones) to preserve biology.
3. **Geometric structure preservation**: A novel regularizer (L_Geo) uses Gaussian kernel geometry to prevent over-correction, maintaining subtle cell subtype distinctions.
4. **Tri-modal and beyond**: Generalizes to L modalities via L-1 pairwise discriminators; the only method achieving >70% accuracy on both RNA→ADT and RNA→ATAC in the TEA-seq benchmark.
5. **Scalability**: Fixed number of training steps (10K) with mini-batch sampling allows handling of datasets with 300K+ cells without memory overflow (unlike Monae, bindSC, and Seurat which OOM at 100K–300K cells).

---

### Method Overview

scMODAL is a **GAN-based deep learning framework** with four loss components. Two per-modality autoencoders (encoder $E_i$ + decoder $G_i$, each a 2-layer MLP with 512 hidden units) map cells to a shared 20-dimensional latent space $Z$. A discriminator $D$ is trained adversarially to distinguish the two modality embeddings in $Z$, while the encoders are trained to fool it — minimizing Jensen-Shannon divergence between the modality distributions.

Three regularizers are applied simultaneously:

1. **Autoencoder regularization** ($\lambda$=10.0): Within-domain reconstruction ($\|\mathbf{x} - G(E(\mathbf{x}))\|^2$) + cross-domain cycle consistency ($\|z_A - E_B(G_B(z_A))\|^2$). Prevents encoders from discarding information.

2. **MNN anchor regularization** ($\lambda$=1.0): From the limited set of known linked features, mutual nearest neighbor pairs are identified each mini-batch (Annoy, angular metric, k=30). These anchors guide the GAN to match biologically corresponding cell populations rather than randomly mixing distributions.

3. **Geometric structure regularization** ($\lambda$=10.0): For each mini-batch, Gaussian kernel pairwise distances are computed in both input and latent spaces. Cosine similarity between these kernel vectors is maximized (up to threshold 0.975), ensuring relative cell-cell distances are preserved after encoding.

For downstream analysis: cross-modal feature imputation via $G_B(E_A(\mathbf{x}_A))$ enables gene-protein and gene-peak correlation inference. Label transfer from one modality to another is performed by KNN in the integrated latent space.

See `doc_method.md` for mathematical derivations and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets

| Dataset | Technology | Modalities | Cells | Key Use |
|---|---|---|---|---|
| PBMC CITE-seq | 10x CITE-seq | RNA + 228 ADT | ~10K | Primary benchmark (GSE164378) |
| Bone marrow Ab-seq | Ab-seq | RNA + 97 protein | ~13K | Validation (Figshare 13397987) |
| Bone marrow CITE-seq + CyTOF | CITE-seq + mass cytometry | 29 vs 32 proteins (12 shared) | ~10K | Limited shared feature scenario (GSE128639) |
| PBMC TEA-seq | TEA-seq | RNA + 46 ADT + ATAC | ~10K | Tri-modality (GSE158013) |
| Mouse brain scRNA + scATAC | 10x | RNA + ATAC (cortex) | ~25K | Complex organ integration |
| Human tonsil CODEX+scRNA+scATAC+Visium | Multiple | 44 protein + RNA + ATAC + spatial | ~50K | Spatial multi-omics application |

#### Metrics

- **Mixing**: mixing metric (lower=better), kBET acceptance rate (higher=better)
- **Biological preservation**: average silhouette width (ASW, higher=better) at two cell-type annotation levels
- **Matching accuracy**: label transfer accuracy (KNN), pair distance (relative distance of true pairs), FOSCTTM (fraction of samples closer than true match — both lower = better)

#### Key Results

**PBMC CITE-seq (full 228 protein panel)**:
- Label transfer accuracy: ~98% (level 1), ~86% (level 2) — highest among all compared methods
- ASW: significantly improved over all other methods; only method maintaining NK, CD4 T, CD8 T as separate clusters
- Pair distance and FOSCTTM: best among all methods

**PBMC CITE-seq (30 protein reduced panel)**: scMODAL consistently best — demonstrating effectiveness with limited linked features.

**Feature imputation**: Mean Pearson correlation (206 proteins): scMODAL 0.53 vs MaxFuse 0.42 vs bindSC 0.40 vs protein-coding gene baseline 0.24. Relative improvement of 29% over MaxFuse.

**CITE-seq + CyTOF (12 shared protein markers)**: scMODAL achieves highest label transfer accuracy despite only 12 shared markers; best cell-type silhouette coefficients.

**TEA-seq tri-modality**: Only method achieving RNA→ADT 87% AND RNA→ATAC 83% accuracy (both >70%). All other methods fail at least one pair.

**Mouse brain scRNA + scATAC**: Correctly aligns 15 clusters including 9 neuron subtypes; layer-specific markers (Lamp5, Rorb, Pcp4) show consistent differential expression patterns across both modalities. Gene-peak link inference (Fam107a): only astrocyte-accessible peaks identified as regulatory, unlike gene activity scores which spuriously link oligodendrocyte/OPC peaks.

**Ablation study** (CITE-seq + CyTOF):
- Remove GAN → poor dataset mixing
- Remove L_AE → poor cell-state matching and biological variation preservation
- Remove L_MNN → label transfer accuracy near 0 (critical component)
- Remove L_Geo → reduced ASW score (biological variation loss)

#### Computational Performance

PBMC CITE-seq dataset scaling benchmark (vs Intel Xeon Gold 5222, NVIDIA RTX 5000):
- Monae OOMs at 100K cells; bindSC at 200K; Seurat at 300K
- scMODAL handles 300K+ cells within 160GB memory limit
- For large datasets, scMODAL shows faster running times than MaxFuse and GLUE

---

### Reproducibility

**Rating: 4/5**

**Strengths**:
- Complete Python package (`pip install` + `conda env`) with clear API: 3 methods, clear input format
- All 6 datasets are publicly available via GEO, Figshare, and lab websites; data availability section comprehensive
- Code archived at Zenodo (DOI: 10.5281/zenodo.15304076) with GPL-3.0 license
- Default hyperparameters are fixed and well-specified in Methods section
- Deterministic with seed=1234 (reproducible by default)

**Weaknesses**:
- **No demo notebooks in GitHub repo** — Overview.png exists but no .ipynb tutorial code
- **Preprocessing not included in library**: All normalization, dimensionality reduction, and feature selection must be done externally using scanpy/Signac, creating implicit dependencies
- **Linked feature convention undocumented**: Features must be in first K columns of input matrix — not stated in README or docstrings
- **λ_Geo discrepancy**: Paper claims λ_Geo=1.0 but code default is 10.0 — may affect reproduction of exact published results
- **Eval uses train mode** (minor bug): `integrate_datasets_links/feats` runs inference in `.train()` mode; no practical effect (no BN/dropout) but is a code quality issue

**Environment setup**:
```bash
git clone https://github.com/gefeiwang/scMODAL.git
cd scMODAL
conda env update -f environment.yml
conda activate scmodal
```
Requires PyTorch ≥1.6 (≤1.13.1 per environment.yml), scanpy ≥1.7, annoy, scipy, sklearn, anndata.

**Common pitfalls**:
1. Not placing linked features in the first K columns → incorrect MNN computation
2. Not normalizing/scaling data before calling `preprocess()` → training on raw counts
3. Running on CPU for large datasets → prohibitively slow (Gaussian kernel computation is O(B²×p))
4. Using λ values from paper (λ_Geo=1.0) instead of code defaults may degrade geometry preservation

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
