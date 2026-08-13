---
layout: default
permalink: /paper-atlas/scclassify2-9bee139f/
title: "scClassify2"
nav: false
wide: true
description: "scClassify2 把每个细胞转换为“Gene2Vec 基因节点 + 细胞特异 log-ratio 边”的稀疏图，通过 node-edge 双向消息传递提取整细胞表示，再用条件 ordinal classifiers 沿预先给定的状态顺序逐级判断，并以 masked Gene2Vec 重建约束表示学习。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>Genome Biology · 2025</span>
    </div>
    <h1>scClassify2</h1>
    <p>A message passing framework for precise cell state identification with scClassify2</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-025-03722-3" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scClassify2">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/SydneyBioX/scClassify2" target="_blank" rel="noopener noreferrer" aria-label="Open code for scClassify2">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scClassify2 方法中文解读：用基因图消息传递识别有顺序的相邻细胞状态

### 1. 为什么普通细胞类型分类不够

许多细胞注释方法把标签看成互不相关的类别，但胚胎发育、免疫分化和造血等过程具有明确顺序。相邻状态共享大量表达特征，例如 E6.75 更像 E7.0 而不是完全无关的成熟状态。若用普通 softmax，模型只知道“标签不同”，不知道错误跨越一个阶段与跨越多个阶段的区别。

scClassify2 专门面向这种 sequential cell state annotation。它结合三种信息：

1. 每个细胞内部的基因表达相对关系，用 gene-pair log-ratio 表示；
2. Gene2Vec 提供的基因共表达先验，作为基因节点初始向量；
3. 标签的生物学顺序，通过 conditional ordinal regression 写入损失与预测。

它是监督学习方法：需要带标签参考数据，也要求使用者事先给出正确的状态顺序。它不是轨迹推断，不会从无序标签自动发现时间方向。

### 2. 输入、输出与代码入口

本地 `main.py` 接受：

- 一个 H5AD 训练集，代码实际要求 `obs['cell_type']` 和 `var['feature_id']`；
- 一个 JSON 列表，如 `['E6.5','E6.75','E7.0',...]`，列表位置定义 ordinal label；
- 本地 `gene2vec_dim_200_iter_9.txt`，保存每个基因的 200 维向量。

预处理后模型输出 $K-1$ 个 logits，其中 $K$ 是状态数。代码进行五折划分、训练并逐 epoch 保存 `models/epoch_X.pth`。当前快照没有独立的查询集推断脚本或完整模型选择流程；验证预测在训练脚本内部完成。因此论文中的工具/网页服务能力不能等同于这个本地快照已经提供一条完整 CLI inference pipeline。

### 3. 数据预处理与一个重要的代码合同

`prepare_data()` 先过滤细胞和基因，再选择 600 个高变基因：

- 论文称过滤检测基因少于 100 的细胞；代码执行 `min_genes=200`；
- 论文与代码都过滤少于 10 个细胞表达的基因；
- 代码使用 `highly_variable_genes(..., flavor='seurat_v3')`；
- 只保留能在 Gene2Vec 字典中找到的基因。

代码把 `obs['cell_type']` 复制为 `CellState`，并根据 JSON 中状态次序建立

$$
\text{label\_dict}[s_k]=k.
$$

这一步决定了后面所有“大于第 $j$ 阶段”的含义。如果 JSON 次序写错，ordinal loss 仍能正常运行，却会学习错误的生物顺序。因此标签顺序是模型的一部分，不只是文件格式细节。

### 4. 一个细胞怎样变成基因图

每个细胞被表示为图 $\mathcal G_i=(\mathcal V,\mathcal E_i)$：节点是入选基因，边是该细胞内基因对的相对表达。不同细胞共享基因节点身份，但边特征随细胞表达改变。

#### 4.1 节点：Gene2Vec 生物学先验

每个基因 $g$ 有预训练 200 维向量 $v_g$。Gene2Vec 从大规模表达数据学习共表达上下文，使节点初始状态不仅是 gene ID，还带有基因间功能相似性。代码将 200 维输入线性投影并 LayerNorm 到 128 维。

训练时随机 mask 15% 基因节点：`Data_using.__getitem__()` 对对应 Gene2Vec 向量乘零，而表达仍参与建边。decoder 尝试恢复被 mask 的原始基因向量，形成自监督正则化。

#### 4.2 边：pairwise log-ratio

对细胞 $i$ 的基因 $j,k$，边的原始量为

$$
r_{i,jk}=\log\frac{X_{ij}}{X_{ik}}=\log X_{ij}-\log X_{ik}.
$$

若所有表达受同一 library-size 因子 $c_i$ 放大，则

$$
\log\frac{c_iX_{ij}}{c_iX_{ik}}=\log\frac{X_{ij}}{X_{ik}},
$$

所以 log-ratio 对细胞级乘性尺度不敏感。这解释了论文为何认为它比绝对表达更有跨数据集稳定性。但它不能消除 gene-specific bias，也不自动解决所有平台差异。

零表达无法取对数。代码只对零元素加入

$$
0.5+\epsilon\,\eta,\qquad \eta\sim\mathcal N(0,1),
$$

其中模型实际传入 `augment_eps=0.05`。这既避免 `log(0)`，也带来随机扰动；同一个零值在不同 batch 中可能略有不同。

### 5. 从稠密基因对到每个节点 16 条边

若有约 600 个基因，完整 ratio matrix 每个细胞有约 36 万个有向关系。代码先用两个 `num_genes × num_genes` 线性层与 GELU/LayerNorm 重加权完整 log-ratio matrix，然后对每个基因保留：

- 最大的 8 个 log-ratio；
- 最小的 8 个 log-ratio。

因此每个节点最终有 16 条有向边。最大/最小同时保留，是因为 $\log(X_j/X_k)$ 与 $\log(X_k/X_j)$ 符号相反，正负极端都携带方向信息。

每个标量 ratio 再通过 8 个 Gaussian RBF 编码：

$$
\phi_l(r)=\exp\left[-\left(\frac{r-\mu_l}{\sigma_l}\right)^2\right].
$$

代码中心为 $(-3.2,-1.6,-0.8,-0.2,0.2,0.8,1.6,3.2)$，尺度为 $(2.8,1.4,1.0,0.4,0.4,1.0,1.4,2.8)$。论文说 ratio 多在 $[-6,6]$ 并以 8 个 kernel 覆盖；代码中心范围更窄，故细节是 `Partial`。

### 6. 双层信息的 MPNN 如何更新节点和边

这里“双层”指 node information 与 edge information 两类信息共同进入网络，不应误读成“恰好两层 encoder”。

对中心节点 $j$、邻居节点 $k$ 和边 $e_{jk}$，代码拼接

$$
[h_j\,\Vert\,h_k\,\Vert\,e_{jk}]\in\mathbb R^{384},
$$

再经 384→128→128 的三层感知机得到 message。对 16 个邻居求和并除以 16，经过 dropout、残差与 LayerNorm 更新节点：

$$
h'_j=\operatorname{LN}\left(h_j+\operatorname{Dropout}\left(\frac1{16}\sum_k m_{jk}\right)\right).
$$

节点还经过一个 128→256→128 的 `information_mix` 残差块。随后重新拼接更新后的节点与边，另一组三层 MLP 更新 edge embedding。这样 expression-derived edge 与 Gene2Vec-derived node 互相影响，而不是只在最后简单拼接。

论文说 encoder message passing 执行三次；`scMPNN` 类默认是 2 层，但本地训练入口显式传 `num_encoder_layers=1`。因此论文架构与实际运行入口是明显 `Partial/Not found`。decoder 则为 1 层，只更新 node embedding，并映射回 200 维 Gene2Vec 空间。

### 7. 怎样把整张基因图压成状态 logits

encoder 后，代码再次拼接中心节点、邻居节点和边，依次通过：

1. `W_cell1: 384→1`，为每条 node-neighbor-edge message 打分；
2. `W_cell2: 16→1`，汇聚每个节点的 16 条边；
3. `W_cell3: num_genes→K-1`，汇聚所有基因。

最后不是 $K$ 类 softmax，而是 $K-1$ 个 ordinal logits $z_0,\ldots,z_{K-2}$。这个 cell pooling 细节在论文中没有同等明确的公式描述，主要来自直接代码证据。

### 8. CORN ordinal loss：把 K 类任务拆成有条件的二分类

对有序状态 $0,1,\ldots,K-1$，第 $j$ 个任务只在已经“通过”前面阶段的样本上训练：

$$
S_j=\{i:y_i>j-1\},
$$

并预测 $y_i>j$。`CornLoss` 用 mask `y_train > i-1` 构造条件子集，再以 `y_train > i` 生成二值目标。总损失是所有有效条件任务的 binary cross-entropy，按参与样本数归一化。

推断时，代码先计算条件 sigmoid，再做累积乘积：

$$
\widehat P(y>j)=\prod_{r=0}^{j}\sigma(z_r).
$$

最终标签索引为

$$
\hat y=\sum_{j=0}^{K-2}\mathbf 1\{\widehat P(y>j)>0.5\}.
$$

例如三个条件概率为 $(0.9,0.8,0.3)$，累积概率为 $(0.9,0.72,0.216)$，前两个超过 0.5，因此预测索引为 2。这个连乘确保越晚阶段的概率不能高于先前阶段，从结构上维持顺序一致性。

### 9. Gene embedding reconstruction 与总损失

decoder 对被 mask 的节点恢复 200 维向量。`SinkhornDistance` 在恢复向量和原 Gene2Vec 向量之间求带熵正则的最优传输：

$$
W_\varepsilon(P,Q)=\min_{\pi\in\Pi(P,Q)}\langle \pi,C\rangle+\varepsilon\,\Omega(\pi).
$$

当前代码使用 `eps=0.1`、最多 100 次迭代，cost matrix 为坐标差绝对值的平方和（`p=2`）。论文公式写法更接近未平方的距离，因此这一项是 `Partial`。

训练入口实际总损失为

$$
L=5L_{\mathrm{ord}}+0.1L_{\mathrm{rec}}.
$$

注释称缩放后两部分量级约 1:1，这是经验平衡，不是从理论推导的固定常数。Sinkhorn 实现内部硬编码 `.cuda()`，主模型和 batch 也直接 `.cuda()`，所以当前快照不是 CPU-portable。

### 10. 训练、验证与 HOPACH 分支

主入口使用 Adam，学习率 $10^{-4}$，batch size 16，固定 28 epochs，并每 10 epochs 将学习率乘 0.5。它构造一次五折交叉验证；论文写“五折、重复 5 次”，代码没有外层重复。论文还写 early stopping，代码没有停止条件，而是保存每个 epoch 的模型。

`code_with_HOPACH/` 是另一套近似重复代码，额外读取 HOPACH tree，用于具有层级关系但不一定线性有序的标签。它不是主顺序状态路径的必需组件，且依赖 R/HOPACH 生成的树文件。解释主论文算法时应把它视为扩展分支，不能与主 `label.json` ordinal 流程混成一个模型。

### 11. 五张主图提供什么证据

- 图 1 展示状态分布重叠、node/edge 双信息、MPNN、ordinal regression 和 encoder-decoder 总体结构。
- 图 2 是核心消融：Gene2Vec 双信息改善 gastrulation 状态嵌入；ordinal accuracy 约 0.93，对比普通 multi-class 约 0.82，E6.75 的识别明显改善。
- 图 3 在 8 个 sequential datasets 上比较 6 个方法。论文报告 dataset 8 中 scClassify2 为 $80.76\pm0.43\%$，scClassify 为 $67.22\pm0.82\%$；dataset 3 中为 $87.93\pm0.28\%$。
- 图 4 在 Xenium breast cancer 两个 replicate 上展示注释与空间区域稳定性，论文称与 scClassify 比较 precision 约 0.92。这里的“真值”是方法间比较，不是独立实验 gold standard。
- 图 5 是 scClassify-catalogue 网页资源与界面，不是本地训练代码的性能验证。

论文列出 Additional files 1–5（Fig. S1–S3、Table S1、Supplementary Methods），但这些独立文件未在本地找到，因此其 panel 与补充方法只能标记 `Not found locally`。

### 12. 论文—代码匹配表

| 环节 | 直接代码 | 判断 |
|---|---|---|
| 600 HVG、Gene2Vec 过滤 | `data.py:4-26` | Exact；细胞阈值论文 100、代码 200 为 mismatch |
| log-ratio、零值扰动、16 边、RBF | `utils.py:38-93` | Exact 主线；RBF 中心范围 Partial |
| node-edge message passing | `model.py:18-61,97-183` | Exact 主线；论文 3 encoder、入口 1 encoder mismatch |
| ordinal loss/预测 | `loss_function.py:6-35`; `utils.py:112-118` | Exact |
| 15% mask 与重建 | `utils.py:7-30`; `main.py:79-95` | Exact 主线；Sinkhorn cost Partial |
| 五折训练 | `data.py:28-53`; `main.py:35-128` | Partial：无 5 repeats、无 early stopping |
| 独立查询推断 | 主代码目录搜索范围 | Not found |

### 13. 使用与解释边界

1. 状态顺序必须由领域知识提供，模型不会自动推断顺序。
2. ordinal regression 最适合近似线性顺序；分支、循环或多轴状态需要其他结构。
3. log-ratio 只能抵消共同乘性尺度，不能保证跨平台完全无 batch effect。
4. Gene2Vec 未覆盖的基因被删除；不同 panel 可能改变可用节点集合和预训练模型兼容性。
5. Xenium 图支持跨平台可用性线索，但约 0.92 precision 是相对 scClassify 的比较，不是独立真值验证。
6. 论文与代码在 encoder 深度、细胞过滤、early stopping、CV repeats 和重建距离上不完全一致。
7. 当前代码硬依赖 CUDA，且缺少独立 inference CLI、测试和明确 checkpoint 选择策略。
8. 分类标签是研究者定义的离散阶段；输出不等于连续 pseudotime，也不证明谱系因果。

### 14. 一句话理解

scClassify2 把每个细胞转换为“Gene2Vec 基因节点 + 细胞特异 log-ratio 边”的稀疏图，通过 node-edge 双向消息传递提取整细胞表示，再用条件 ordinal classifiers 沿预先给定的状态顺序逐级判断，并以 masked Gene2Vec 重建约束表示学习。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scClassify2 Summary

### Paper Information

- **Title**: A message passing framework for precise cell state identification with scClassify2
- **Authors**: Wenze Ding, Yue Cao, Xiaohang Fu, Marni Torkel, Jean Yee Hwa Yang
- **Journal**: Genome Biology, 2025
- **DOI**: 10.1186/s13059-025-03722-3
- **Code**: https://github.com/SydneyBioX/scClassify2

---

### Motivation & Novelty

#### Biological Problem

Single-cell RNA sequencing enables cell-type annotation at transcriptome scale, but most annotation tools assume **discrete, non-overlapping cell populations**. This assumption breaks down for many critical biological processes involving **sequential cell state transitions**, where cells progress through adjacent states that share most of their gene expression profile (e.g., mouse gastrulation embryo stages E6.5→E6.75→E7.0→E7.25→E7.5→E7.75, or CD8+ T cell differentiation). Adjacent states have overlapping expression distributions, making them nearly impossible to distinguish with classifiers that treat labels as unordered categories.

A second challenge is **cross-platform batch effects**: individual gene expression levels shift across sequencing experiments and platforms (scRNA-seq vs. Xenium subcellular spatial transcriptomics), hurting model generalizability.

#### Why Existing Methods Fall Short

| Method | Type | Limitation |
|---|---|---|
| scClassify (*Mol Syst Biol*, 2020) | KNN + hierarchical tree | Designed for discrete cell types; adjacent states may cluster under intermediate category |
| scGCN (*Nat Commun*, 2021) | Graph convolutional network | GCN updates only node features, ignoring edge information (pairwise expression) |
| sigGCN (*Nat Commun*, 2021) | Graph convolutional + gene interaction | Same GCN limitation; no ordinal structure |
| scGPT (*Nat Methods*, 2024) | Foundation model (LLM) | Computationally intensive, generalist model not optimized for sequential states |
| scFoundation (*Nat Methods*, 2024) | Foundation model | Same as scGPT; dataset-agnostic pre-training limits specialization |

#### Unique Contributions

1. **Log-ratio edge features**: Pairwise gene expression ratios (log(X_j/X_k)) are more stable across datasets than absolute expression, enabling cross-platform transfer without explicit domain adaptation.
2. **MPNN dual-layer architecture**: First application of Message Passing Neural Networks in single-cell research. Unlike GCN/GAT, MPNN explicitly models both gene node features (Gene2Vec embeddings) and edge features (log-ratios), enabling capture of gene co-expression topology.
3. **Ordinal regression via conditional binary classifiers**: Converts K-class sequential annotation into K-1 binary classifiers with a conditional training scheme, exploiting the natural ordering of cell states and improving accuracy on adjacent states.
4. **scClassify-catalogue web server**: Pre-trained models for >1000 cell types across 30+ tissue types, making the tool accessible without GPU or computational expertise.

---

### Method Overview

scClassify2 encodes each cell as a **cell graph** where genes are nodes and pairwise log-ratio values are edges. A **Message Passing Neural Network (MPNN)** processes this graph with a dual-layer architecture:
- **Layer 1 (edges)**: Log-ratio-based pairwise gene expression relationships
- **Layer 2 (nodes)**: Gene2Vec pre-trained embeddings encoding biological gene co-expression knowledge

Cell-level features are extracted by aggregating gene-level embeddings and passed to an **ordinal regression head** that explicitly models the sequential ordering of cell states. A self-supervised **reconstruction objective** (masked autoencoding of Gene2Vec embeddings with Wasserstein-2 distance) regularizes the gene representations.

See `doc_method.md` for step-by-step algorithm and equations, and `doc_code.md` for implementation details.

**Key parameters**: 600 HVGs, Gene2Vec 200-dim, 16 edges/node (8+8 log-ratio extremes), 1 MPNN encoder layer, batch=16, 28 epochs, loss weights λ₁=5, λ₂=0.1.

---

### Evaluation

#### Datasets

Eight diverse scRNA-seq datasets from human and mouse, covering sequential biological processes:

| Dataset | Species | Process | States |
|---|---|---|---|
| Dataset 1 | Mouse | Gastrulation (GSE171588) | 6 (E6.5–E7.75) |
| Dataset 2 | Human | Preimplantation embryo (EMBL-EBI E-MTAB-3929) | sequential |
| Dataset 3 | Human | CD8+ T cell differentiation (GSE211602) | sequential |
| Dataset 4 | Mouse | Oligodendrocyte (GSE75330) | sequential |
| Dataset 5-6 | Mouse | Bone marrow erythrocyte / kidney (GSE108097) | sequential |
| Dataset 7 | Mouse | Dentate gyrus neurogenesis (GSE95753) | sequential |
| Dataset 8 | Mouse | Kidney collecting duct (GSE107585) | sequential |

Spatial validation: Xenium breast cancer dataset (10x Genomics).

#### Results

- **5-fold cross-validation (accuracy)**:
  - scClassify2: 87.93% (Dataset 3), 94.45% (Dataset 1), 80.76% (Dataset 8)
  - scClassify: 67.22% (Dataset 8) — consistent improvement across all 8 datasets
  - sigGCN: 78.55% (Dataset 3)
  - scGCN: 79.31% (Dataset 3)
  - scGPT: 93.04% (Dataset 1)
  - scFoundation: 91.06% (Dataset 1)

- **Ablation (mouse gastrulation)**:
  - Dual-layer (Gene2Vec) vs. single-layer: 0.95 vs. 0.63 accuracy
  - Ordinal regression vs. multi-class: 0.93 vs. 0.82 accuracy
  - Ordinal regression correctly identifies E6.75: ~95% vs. ~30% for multi-class

- **Spatial transcriptomics**: ~0.92 precision on Xenium breast cancer when compared to scClassify; consistent across spatial regions.

---

### Reproducibility Rating: 3/5

**Justification**: The code is released and functional for the demo dataset, but several critical discrepancies between paper and code undermine confident reproduction:

| Issue | Impact |
|---|---|
| Encoder depth mismatch (paper: 3 EncLayers, code: 1 EncLayer) | High — cannot reproduce the exact model |
| Cell filter threshold mismatch (paper: 100 genes, code: 200 genes) | Medium — different preprocessing |
| No early stopping in code | Low — must manually select checkpoint |
| No CV repeats (5-fold only) | Medium — variance estimates may differ |
| Hard-coded CUDA in SinkhornDistance | Low — breaks CPU environments |

**Practical notes**:
- **Environment setup**: `conda env create -f environment.yaml && conda activate scclassify2`. PyTorch 2.0.1 + CUDA 11.8 required; CPU-only not supported due to hardcoded `.cuda()`.
- **Data format**: Input must be H5AD with `obs['cell_type']` column (note: not `CellState`); gene names in `var['feature_id']`.
- **Gene2Vec file**: `gene2vec_dim_200_iter_9.txt` (55MB) must be present in the working directory (hardcoded path in `data.py:13`).
- **Label ordering matters**: The JSON label file must list cell states in sequential biological order — this defines the ordinal structure for the CornLoss.
- **Model selection**: No early stopping; inspect the `log` file to identify the best epoch, then load `models/epoch_X.pth`.
- **HOPACH variant**: The `code_with_HOPACH/` directory provides a hierarchical extension requiring R + HOPACH package; useful for non-sequential cell types.

**Strengths**: Full Python implementation of novel components (CornLoss, SinkhornDistance, Features module); well-organized codebase; web server for zero-infrastructure use.

**Weaknesses**: Several paper claims are inconsistent with code; no unit tests; Sinkhorn loss hardcodes CUDA; no inference script (only training); gene2vec path hardcoded.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
