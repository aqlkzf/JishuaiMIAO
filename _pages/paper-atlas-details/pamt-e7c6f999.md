---
layout: default
permalink: /paper-atlas/pamt-e7c6f999/
title: "PAMT"
nav: false
description: "PAMT 把 bulk 表达先重组为有语义的通路 token，再让这些通路作为 query 从 WSI patch 中检索形态证据，同时用生存目标学习患者风险；它的解释性来自“通路—patch”这一可读中间关系，但解释仍是模型关联，而且公开代码的默认训练设置与论文完整方法存在若干可影响复现的差异。"
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
      <span>IEEE Transactions on Pattern Analysis and Machine Intelligence · 2025</span>
    </div>
    <h1>PAMT</h1>
    <p>Pathway-Aware Multimodal Transformer (PAMT): Integrating Pathological Image and Gene Expression for Interpretable Cancer Survival Analysis</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1109/TPAMI.2025.3611531" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PAMT 方法解读：用生物通路查询病理图像的多模态生存模型

### 1. PAMT 要解决什么问题

PAMT（Pathway-Aware Multimodal Transformer）面向癌症生存风险预测：每位患者同时有一张全切片病理图像（WSI）、一份 bulk RNA 表达谱和随访结局。图像能显示组织结构、肿瘤形态与微环境，RNA 则反映患者整体的分子状态；困难在于二者既不在同一空间尺度，也没有逐 patch 的基因标签。PAMT 的核心选择不是把两种模态简单拼接，而是先把基因表达组织成具有生物学含义的“通路 token”，再让每个通路 token 去查询哪些病理 patch 与它相关。

因此，模型输出有两层用途：一是患者级风险分数，用 Cox 生存目标训练；二是通路—patch 注意力，用来提出“某条通路可能对应哪些组织区域”的解释性线索。后者是模型关联，不等于空间转录组测量或因果证据。

### 2. 输入如何变成两组 token

#### 2.1 通路侧：186 条 KEGG 通路 × 5245 个基因

论文先建立二值通路—基因隶属矩阵，保留 186 条 KEGG 通路和 5245 个基因。对患者表达向量按该矩阵遮罩后，每条通路得到一个长度为 5245 的向量：属于该通路的基因保留表达值，其余位置为零。于是一个患者的分子输入形状是 $186\times5245$，而不是 186 个自由学习的通路嵌入。

仓库中的 `gene_expression_data_process/pathways_genes_matrix.csv` 是这一步的离线产物；生产模型在 `vit_model_gene_wsi_concat_label.py:273` 用共享的 `EmbedReduction(5245→1000→256)` 将每条通路压缩成 256 维 token。随后通路分支的 Transformer 在 186 个通路之间建模依赖。这个实现边界很重要：代码不是对通路成员做显式“软注意力池化”，而是对遮罩后的定长向量使用 MLP 压缩。

#### 2.2 图像侧：WSI patch 经 DINO 表征后选出 500 个代表

WSI 先被切为 patch，再用自监督 DINO ViT-small 提取 patch 特征。论文和代码工作流随后进行聚类，从 50 个簇各选 10 个代表 patch，得到约 500 个图像 token。主训练数据集接收的是这些已经准备好的特征，并不在生存训练循环中从原始 WSI 重新切片或重新训练 DINO。

这意味着完整复现至少包含三个外部阶段：WSI 切片、DINO 训练/特征提取、聚类选 patch。仓库提供相应脚本，但当前工作区没有论文所用 TCGA/CPTAC 数据、预处理缓存和检查点，不能仅凭一次 `train.py` 运行复现论文表格。

### 3. 模型的三步信息流

#### 3.1 模态内编码

图像 token 和通路 token 分别经过自注意力 Transformer。标准块使用 pre-LayerNorm、multi-head self-attention、残差连接和 MLP：

$$
X' = X + \operatorname{MSA}(\operatorname{LN}(X)),\qquad
X'' = X' + \operatorname{MLP}(\operatorname{LN}(X')).
$$

通路分支让一条通路吸收其他通路的上下文；图像分支让代表 patch 建模组织层面的共现关系。两条支路随后都被投影到 256 维，使跨模态点积和注意力可以计算。

#### 3.2 无 patch 标签的通路—图像对齐

代码在融合前计算

$$
S = G_0 W_0^\top,
$$

其中 $G_0\in\mathbb{R}^{186\times256}$ 是 MLP 压缩后、尚未经过通路 Transformer 的表示，$W_0\in\mathbb{R}^{500\times256}$ 是图像分支编码并降维后的表示，故 $S\in\mathbb{R}^{186\times500}$。`utils_cox.py` 对每条通路的相似度排序，以 top-$h$（训练参数默认 $h=2$）位置构造动态伪标签，再用交叉熵形成对齐损失。它不需要逐 patch 分子标注，因而论文称其为 label-free alignment。

但仓库实现不能被无条件等同于论文公式：论文写有温度参数和损失权重，生产文件中的可学习温度已被注释；训练脚本默认 `contrastive_loss_flag=0`，即这项损失默认关闭。代码中的“先排序、再构造 top-k 标签、对原始相似度用 CrossEntropyLoss”也只是对论文对比目标的部分实现。

#### 3.3 通路作 query 的单向跨注意力

融合层的实际方向可由源码直接确定。`Gene_Guided_Transformer_Fusion.forward(x1, x2)` 虽然参数名不直观，但调用处传入 `x1=wsi_features_reduction`、`x2=gene_features`；内部第 178 行从 `x2` 生成 query，第 179–180 行从 `x1` 生成 key/value：

$$
Q=G W_Q,\qquad K=W W_K,\qquad V=W W_V,
$$

$$
A=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt d}\right),\qquad Z=AV.
$$

所以每个通路 token 查询 500 个 WSI patch，得到一行注意力权重和一个图像条件化的通路表示。这是“pathway-aware”的直接机制。模型没有同时实现反向的 WSI-query-gene 双向注意力。

融合输出 $Z$ 与通路分支表示分别经过自适应平均池化，再拼成 372 维向量，由线性头输出一个患者风险分数。这里的池化实现与论文符号中的直接 token 拼接并非逐项完全一致。

### 4. 生存目标在优化什么

对患者 $i$ 的风险分数记为 $\theta_i$，事件指示为 $\delta_i$，风险集为 $R_i$。核心 Cox 负偏对数似然为

$$
\mathcal L_{\mathrm{Cox}}=-\frac{1}{N_e}\sum_{i:\delta_i=1}
\left[\theta_i-\log\sum_{j\in R_i}\exp(\theta_j)\right].
$$

它学习的是相对风险排序，而不是直接预测“还能生存多少天”。论文将 Cox 损失、正则项和通路—patch 对齐损失组合；代码训练循环也保留三部分接口，但默认行为不同：使用 `optim.Adam` 而不是论文所述 AdamW，显式正则开关和对比开关默认关闭，Adam 自身的 weight decay 也不是论文给出的 $5\times10^{-4}$，并且没有论文所述 $\alpha=\beta=0.8$ 权重。

### 5. 如何读论文图和结果

方法总览图应从左到右读：WSI 经 DINO 和聚类形成 patch token；表达谱经 KEGG 隶属矩阵形成通路 token；两支各自编码；相似度目标提供弱对齐；通路 query 再从图像 key/value 中取回信息；最终进入 Cox 风险头。

论文在 TCGA BLCA、LUAD 和 LUSC 上报告 C-index、时间依赖 AUC 与 Kaplan–Meier 分层，并用 CPTAC 作外部验证。消融图的重点不是证明任一模块在所有数据集都必然有效，而是比较去除通路表示、对齐或融合后性能如何变化。注意力热图把一条通路在不同 patch 上的权重投回 WSI；TGF-β 等案例及 HoVer-Net/组织学分析提供生物学一致性线索，但不能证明该通路在该 patch 中真实表达，更不能由注意力单独推断调控因果。

### 6. 论文与当前代码快照的关键边界

当前嵌套代码仓库 HEAD 为 `206cc19ca89d985245ca204fbc86772e5c2446d0`。静态核对得到以下边界：

1. 论文/训练参数声称 WSI 分支 6 层，但 `blocks_wsi` 的循环错误地使用 `depth_fusion`；默认实际构造 4 层，`depth_wsi` 只用于生成 stochastic-depth 日程。
2. 通路—patch 相似度使用的是 Transformer 前的 `gene_features_reduction`，跨注意力 query 使用的是 Transformer 后的 `gene_features`；两者不是同一个表示。
3. 生产模型第 375 行先返回 `(gene2wsi_feature, pred_head)`，第 376 行返回注意力的语句永远不可达。生成论文式注意力图需要专门的预测/可视化路径或修改返回接口。
4. 默认训练关闭对比损失和显式正则，使用 Adam；不能把论文完整目标视为仓库默认命令的行为。
5. 仓库没有锁定环境、数据拆分清单、全部预训练权重和论文运行日志；当前分析验证的是代码结构与论文描述的对应关系，不是数值复现实验。

### 7. 一句话把握 PAMT

PAMT 把 bulk 表达先重组为有语义的通路 token，再让这些通路作为 query 从 WSI patch 中检索形态证据，同时用生存目标学习患者风险；它的解释性来自“通路—patch”这一可读中间关系，但解释仍是模型关联，而且公开代码的默认训练设置与论文完整方法存在若干可影响复现的差异。

### 证据入口

- 论文正文与图注：`paper source/paper/auto/paper.md`
- 图像证据整理：`figure_analysis.md`
- 生产模型：`PAMT/gene_wsi_predict/vit_model_gene_wsi_concat_label.py`
- 损失与训练循环：`PAMT/gene_wsi_predict/utils_cox.py`
- 训练参数与优化器：`PAMT/gene_wsi_predict/train.py`
- 代码—论文逐项核对：`doc_code.md`

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## PAMT: Pathway-Aware Multimodal Transformer for Interpretable Cancer Survival Analysis

**Paper**: Pathway-Aware Multimodal Transformer (PAMT): Integrating Pathological Image and Gene Expression for Interpretable Cancer Survival Analysis
**Journal**: IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI), Vol. 48, Issue 1, 2025, pp. 896–913
**DOI**: 10.1109/TPAMI.2025.3611531
**Authors**: Rui Yan, Xueyuan Zhang, Zihang Jiang, Baizhi Wang, Xiuwu Bian, Fei Ren, S. Kevin Zhou
**Code**: https://github.com/YANRUI121/PAMT

---

### Motivation & Novelty

**Biological problem**: Cancer survival prediction benefits from combining two key data modalities — pathological images (phenotype) and gene expression (genotype). However, the relationship between these modalities is hierarchical: molecular pathway activity *causes* observable morphological changes in tissue. No prior method explicitly models this fine-grained, directed relationship between individual biological pathways and specific tissue regions.

**Limitations of existing approaches**:
- **MCAT** (Chen et al., ICCV 2021): co-attention between genomic categories and WSI patches, but organizes genes into only 6 coarse functional categories
- **HiMT** (Li et al., ICPR 2022): hierarchical multimodal fusion, still uses coarse genomic categories
- **SURVPATH** (Jaume et al., CVPR 2024): pathway-based tokenization for genes, but lacks explicit alignment loss between modalities
- **HFBSurv** (Li et al., Bioinformatics 2022): factorized bilinear fusion, does not model directed genotype→phenotype relationship
- **CMTA** (Zhou & Chen, ICCV 2023): cross-modal translation, no pathway-level gene organization

**What's new in PAMT**:
1. **Fine-grained pathway tokenization**: Decomposes gene expression into 186 KEGG pathway tokens (vs. 6 coarse categories in MCAT/HiMT), enabling pathway-level attention maps
2. **Label-free contrastive alignment (L3)**: First method to align WSI patches and biological pathways without requiring manual pairing labels — dynamic pseudo-labels from top-k similarity bootstrapping
3. **Unidirectional pathway→patch cross-attention**: Embeds the biological prior "genotype determines phenotype" directly in the attention architecture — gene features serve as queries, WSI serves as key/value
4. **Spatial pathway heatmaps**: 186 pathway × WSI region heatmaps (300K images, ~20TB), publicly hosted, enabling biologists to explore pathway-phenotype correlations at scale

---

### Method Overview

PAMT processes paired (WSI, gene expression) data through three stages:

**Stage 1 — Intra-modal interaction**: Separate Transformer encoders for each modality. The gene branch receives 186 pathway tokens × 5245-dim (binary pathway-gene mask × patient expression) → reduced to 256-dim via MLP. The WSI branch receives 500 representative patches × 384-dim (DINO ViT-small) → self-attention at 384-dim → reduced to 256-dim. Both branches use learnable 1D positional embeddings.

**Stage 2 — Inter-modal alignment (novel)**: A label-free contrastive loss aligns the two modalities to the same semantic space before fusion. For each patient, the similarity matrix between all 186 pathway tokens and 500 patch tokens is computed; the top-2 most similar patch tokens per pathway are treated as pseudo-positive pairs and pulled together via cross-entropy loss. This requires no manual pairing annotation.

**Stage 3 — Inter-modal fusion (novel)**: Pathway-to-patch cross-attention: gene pathway features serve as queries attending to WSI patch key-values. The attention weight $A_{m,n}$ represents how strongly pathway $m$ activates tissue patch $n$ — directly interpretable as a spatial heatmap. The concatenation of gene features and cross-attended WSI features is passed through a linear head to predict a scalar survival risk score.

The final training objective combines Cox partial log-likelihood ($\mathcal{L}_1$) + L2 regularization ($\mathcal{L}_2$) + label-free contrastive loss ($\mathcal{L}_3$).

**Key assumptions**: (1) Gene expression from bulk RNA-seq captures population-level pathway activity. (2) DINO pre-training on the same WSI dataset produces morphologically meaningful embeddings. (3) Top-2 similarity provides reliable pseudo-positive pairs for contrastive alignment.

**Computational pipeline**: WSI → 256×256 patches → DINO feature extraction (200 epochs pre-training) → K-means clustering (K=50) → 500 representative patches per WSI; Gene expression → log2 + Z-score → 186 pathway matrices → train PAMT end-to-end with Cox + contrastive losses.

---

### Evaluation

**Datasets**:
- **Internal**: TCGA-BLCA (372 patients, bladder urothelial carcinoma), TCGA-LUAD (lung adenocarcinoma), TCGA-LUSC (lung squamous cell carcinoma); 5-fold cross-validation
- **External**: CPTAC-LUAD, CPTAC-LSCC, CPTAC-UCEC for generalization testing

**Metrics**: C-index (primary), time-dependent AUC (short/long-term), Kaplan-Meier log-rank p-value

**Results (C-index, 5-fold CV)**:

| Cancer | Best prior method | PAMT | Δ |
|--------|-----------------|------|---|
| TCGA-BLCA | HFBSurv 0.710±0.028 | **0.745±0.034** | +3.5% |
| TCGA-LUAD | HFBSurv 0.711±0.021 | **0.719±0.044** | +0.8% |
| TCGA-LUSC | SeTranSurv 0.685±0.008 | **0.704±0.015** | +1.9% |

PAMT consistently outperforms all single-modal and multimodal baselines. Long-term AUC (≥3 years) shows the largest improvements over competing methods.

**Ablation highlights**:
- WSI=6 blocks + Gene=2 blocks achieves best C-index (0.745); both more and fewer blocks degrade performance
- Pathway-to-patch fusion (0.745) > patch-to-pathway (0.720) > bidirectional (0.721) → validates genotype→phenotype directionality
- L2 weight_decay=5E-4 is critical (without it: 0.728 vs. 0.745)
- Top_h=2 optimal for contrastive loss (h=0 gives 0.721, h=16 gives 0.705)
- 500 patches optimal (300: 0.691, 600: 0.740, 700: 0.735)

**Biological validation**: Using the pathway-patch attention heatmaps and HoVer-Net nuclei segmentation, PAMT discovers that Epithelial-Lymphocytes Ratio (ELR) in high-activation patches of TGF-β signaling pathway is a significant prognostic factor in LUAD and LUSC (p<0.05), consistent with known immunology literature.

**Generalization**: Training on 11 cancer types (TCGA-Cancer11) reduces the performance drop on CPTAC external validation from ~13% to ~4-5%, suggesting the contrastive alignment benefits from scale.

---

### Reproducibility

**Rating: 2/5**

**Justification**: The paper presents compelling results, but reproducibility is significantly hampered by:
1. The most expensive component (DINO pre-training, 4 GPUs × 7 days per dataset) requires substantial compute not available to most labs
2. Pre-processed features (DINO patch embeddings, gene pathway matrices) are not directly provided; authors share download links via Google Drive but availability is uncertain long-term
3. Critical code discrepancies: the production model (`vit_model_gene_wsi_concat_label.py`) has a bug in WSI block depth (4 blocks instead of claimed 6), the optimizer is Adam not AdamW, and the contrastive loss is disabled by default

**Data availability**: TCGA data publicly available at https://portal.gdc.cancer.gov/; KEGG pathways at https://www.gsea-msigdb.org/gsea/msigdb/; authors claim to provide preprocessed features via the GitHub repo (Drive links)

**Environment**: Python 3.8.3, PyTorch 1.7.0, CUDA-capable GPU (4× A100 for DINO pre-training; 1× GPU sufficient for PAMT fine-tuning), timm==0.6.12, openslide-python==1.1.2, lifelines==0.27.7

**Common pitfalls**:
- Gene preprocessing (log2+Z-score normalization) is done offline and not included in the code repository; must replicate from paper description
- The WSI branch depth bug means the published training script with default parameters does NOT reproduce the ablation study results
- No saved model checkpoints are provided for direct inference
- The ~20TB heatmap website (http://222.128.10.254:18822/#/) may not be stable long-term

**Strengths**: Clear experimental protocol (5-fold CV), multiple evaluation metrics, ablation studies for all key hyperparameters, biological interpretation validated against literature, external validation on CPTAC

**Weaknesses**: Missing intermediate results (feature files), unreproducible code defaults, high compute cost for pre-training, no Docker/environment file

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
