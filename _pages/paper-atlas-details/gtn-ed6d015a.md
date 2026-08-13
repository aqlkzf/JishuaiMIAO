---
layout: default
permalink: /paper-atlas/gtn-ed6d015a/
title: "GTN"
nav: false
description: "GTN 的“Transformer”不是今天常说的 self-attention Transformer。它学习的是图结构变换：对异构图的多种边类型做可微的软选择，再通过邻接矩阵相乘把若干关系组合成 meta-path 图，最后在这些自动生成的图上做 GCN 节点分类。核心贡献是把“专家手工选 meta-path → 再训练 GNN”的两阶段流程改成端到端学习。"
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
      <span>Representation Models</span>
      <span>NeurIPS · 2019</span>
    </div>
    <h1>GTN</h1>
    <p>Graph Transformer Networks</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.1911.06455" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GTN">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/seongjunyun/Graph_Transformer_Networks" target="_blank" rel="noopener noreferrer" aria-label="Open code for GTN">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Graph Transformer Networks（GTN）中文方法解读

### 一句话抓住方法

GTN 的“Transformer”不是今天常说的 self-attention Transformer。它学习的是图结构变换：对异构图的多种边类型做可微的软选择，再通过邻接矩阵相乘把若干关系组合成 meta-path 图，最后在这些自动生成的图上做 GCN 节点分类。核心贡献是把“专家手工选 meta-path → 再训练 GNN”的两阶段流程改成端到端学习。

### 1. 输入为什么是一叠邻接矩阵

异构图有多种节点与边关系。论文将每种有向边类型 $t$ 写成一个邻接矩阵

$$
A_t\in\mathbb R^{N\times N},
$$

并堆叠成 $\bar A\in\mathbb R^{N\times N\times K}$。例如 DBLP 中有 Paper→Author、Author→Paper、Paper→Conference、Conference→Paper。节点还有特征矩阵 $X\in\mathbb R^{N\times D}$。

一条 meta-path 是边类型的序列。例如 Author→Paper→Author（APA）连接发表过同一论文的作者，Author→Paper→Conference→Paper→Author（APCPA）连接在同一会议体系发表的作者。若采用“列是起点、行是终点”的约定，一条路径的邻接关系可以由对应邻接矩阵依次相乘得到。

传统 HAN、metapath2vec 等方法通常需要专家先指定 APA、APCPA 等路径。GTN 的问题是：能否让模型根据当前分类任务自己决定应组合哪些边类型以及路径应有多长？

### 2. GTConv：软选择一种关系

对第 $c$ 个通道，GTConv 学习边类型权重 $w_{c,t}$，经 softmax 得到

$$
\alpha_{c,t}=\frac{e^{w_{c,t}}}{\sum_{t'}e^{w_{c,t'}}},
\qquad
Q_c=\sum_{t=1}^{K}\alpha_{c,t}A_t.
$$

$Q_c$ 是候选邻接矩阵的凸组合。若某个 $\alpha$ 接近 1，它近似选择单一边类型；若多个权重较大，它代表多种关系的软混合。

直接代码 `model_gtn.py:125-158` 对 `weight` 的边类型维做 softmax，然后把每种稀疏边的 value 乘相应权重并 `coalesce`。论文把这个操作称为对邻接张量做 $1\times1$ convolution，因为它只在“边类型通道”维混合，不在节点空间卷积。

### 3. GTLayer：用矩阵乘法组合关系

第一层包含两个独立 GTConv，得到 $Q_1$ 与 $Q_2$，随后计算

$$
A^{(1)}=Q_1Q_2.
$$

矩阵乘法把两跳关系合成为新的直接连接。一个小例子：若 $A_{AP}[p,a]=1$ 表示作者 $a$ 写论文 $p$，$A_{PA}[a',p]=1$ 表示论文 $p$ 属于作者 $a'$，则相乘后的非零项表示作者间存在 APA 关系。软选择意味着 $A^{(1)}$ 实际是所有两步边类型组合的加权和，某条 meta-path 的系数是沿途选择权重的乘积。

代码 `model_gtn.py:104-123` 将两个稀疏 COO 张量交给 `torch.sparse.mm`。后续 GTLayer 不再重新生成两个分支：它把上一层已生成的 $H$ 当作第一项，再从原始边集合软选一个新关系作为第二项，因而每层向已有路径追加一步。

### 4. Identity 为什么控制路径长度

如果每层都必须追加一种真实边关系，堆叠层数就会强制路径越来越长。GTN 把单位矩阵 $I$ 也加入候选边集合：

$$
A_0=I.
$$

选择 $I$ 相当于该步停留在原节点，不增加有效关系长度。于是 $l$ 个 GT layers 可以表示不超过相应最大长度的路径，而不必所有通道都使用同样长度。`main.py:68-84` 在真实边类型之后明确追加 identity edge list。

这也解释图 3：IMDB 的一些权重对 $I$ 较高，模型偏好较短的 MDM/MAM 关系；DBLP 对真实关系的组合更强，适合更长的会议/论文/作者路径。注意力权重提供的是模型内重要性线索，不是因果解释。

### 5. 多通道不是多头自注意力

GTN 同时学习 $C$ 个 meta-path 通道。每个通道有自己的边类型权重，因此最终得到 $C$ 张不同的软 meta-path 图。对每张图使用同一个 GCN 权重：

$$
Z_c=\sigma\!\left(\widetilde D_c^{-1}\widetilde A_c XW\right),
\qquad
Z=Z_1\|Z_2\|\cdots\|Z_C.
$$

拼接后的表示送入分类器。`model_gtn.py:60-88` 正是 GT layers → 每通道 GCN → ReLU → concat → Linear → 交叉熵。这里的“channel”是不同学习图结构，不是 query/key/value attention head。

代码的 GCN 使用有向的行度归一化 $D^{-1}A$，不是常见的对称 $D^{-1/2}AD^{-1/2}$；`gcn.py:75-104` 还在传播前加入自环。GT layer 自身也在每次关系相乘后做度归一化，避免多次矩阵乘法使数值随路径数快速增长。

### 6. 完整张量与稀疏数据流

1. `main.py` 读取节点特征、各边类型稀疏矩阵与 train/validation/test 标签。
2. 每种关系转为 `(edge_index, edge_value)`，并追加 identity。
3. 第一 GTLayer 对原始关系集合做两次软选择，逐通道稀疏相乘。
4. 每个后续 GTLayer 将当前 meta-path 图与一个新的软关系相乘，并做度归一化。
5. 同一个 GCN 分别在每个通道传播节点特征。
6. 拼接通道表示，用线性分类器预测带标签节点；训练采用 Adam 与交叉熵。
7. 验证 micro-F1 最佳时保存对应测试指标，最后汇总多次运行。

这条路径中，GT 层既改变“谁与谁相连”，GCN 又在新邻接上改变节点表示；两者通过分类损失联合优化。

### 7. 图 1–3 从左到右怎么读

#### 图 1：单个 GT layer

左边是一叠边类型邻接矩阵；上下两个 $1\times1$ conv 分别产生 $Q_1$ 和 $Q_2$；中间矩阵乘法生成新邻接 $A^{(1)}$；红色新边表示原图无直接边、但存在被选中两跳组合的节点对。该图解释软选择和关系合成。

#### 图 2：完整 GTN

多个 GT layers 递归增长 meta-path，且同时保留多个通道；最终 GCN 在每张学习图上产生节点表示并拼接。弯曲回路表示上一层输出成为下一层相乘的一侧，与代码 `H_` 的传递一致。

#### 图 3：边类型权重

图中条形是各层 GTConv softmax 后的关系权重。作者用 DBLP 与 IMDB 的差异说明模型可通过 identity 调节有效路径长度，并可将高权重组合展开成 meta-path。图 3与表 3一起支持“自动发现的高权重路径与专家路径有重合，也会发现新组合”的解释性主张。

### 8. 论文实验说明了什么

论文在 DBLP、ACM 和 IMDB 三个异构节点分类数据集上比较 DeepWalk、metapath2vec、GCN、GAT、HAN、GTN-I 与 GTN。表 2报告 GTN 的 F1 分别为 94.18、92.68、60.92，在三组中均最高；GTN-I 移除 identity 后尤其在 IMDB 降至 52.33，支持短路径选择对该数据重要。

这些结果的边界很明确：

- 任务是三个转导式节点分类 benchmark，不是图级任务或开放世界归纳泛化。
- 节点特征和图模式都由既定预处理提供；“不需领域 meta-path”不等于不需数据模式知识。
- 三个数据集规模较小，稀疏矩阵乘法生成的 meta-path 图可能迅速变稠，扩展到大图会遇到时间/显存问题。

### 9. 论文与代码的关键差异

1. 论文说 GTConv 参数以常数初始化；当前 `model_gtn.py:135-141` 使用 `Normal(std=0.01)`。两者都使初始 softmax 接近均匀，但不是字面相同。
2. 论文描述“两层 dense + softmax”；当前实现 `model_gtn.py:35,80` 只有一个 `Linear`，损失函数内部处理 logits。
3. 后续层在代码中复用归一化后的上一层 $H$ 作为第一乘数，而不是对原始 $A$ 再做一次独立软选择；归一化夹在关系合成之间。
4. GCN 会再加自环，和把 $I$ 作为可选关系是两种不同机制：前者保证信息保留，后者让模型学习有效 meta-path 长度。
5. 仓库还包含 `model_fastgtn.py`，这是主论文之后/之外的扩展，不应反向当作 NeurIPS 2019 论文核心证据。

### 10. 可解释性应怎样谨慎使用

一条离散 meta-path 的重要性可近似由沿层权重乘积得到。若一个通道近似 one-hot，展开很直观；若多种关系都有明显权重，通道代表大量 meta-path 的混合，不能只挑最大项就宣称模型仅使用那一条路径。权重揭示模型如何组合输入关系，但还需消融、稳定性和预测层面的分析才能说明该路径是否真正必要。

### 11. 代码版本与复现边界

因此元数据保留仓库 URL但提交为 null。仓库含 `ACM.mat` 示例和预处理 notebook，但 `main.py` 默认从 `../data/<dataset>/` 读取 pickle，完整 DBLP/IMDB 预处理数据并不都在当前目录。本次只核对静态源代码与论文，不执行旧版 PyTorch Geometric 环境训练。

### 推荐阅读路线

先看图 1理解“软选关系 + 矩阵相乘”，再用一个 APA 数值例子理解邻接乘法；接着看图 2和 `model_gtn.py:60-123` 串起递归通道，最后看图 3、表 2/3与论文—代码差异。这样不会把 GTN 误读成标准 Transformer，也能明确自动 meta-path 学习的实际边界。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Graph Transformer Networks (GTN) — Summary

**Paper**: Graph Transformer Networks
**Authors**: Seongjun Yun, Minbyul Jeong, Raehyun Kim, Jaewoo Kang, Hyunwoo J. Kim
**Venue**: NeurIPS 2019
**arXiv**: 1911.06455
**Code**: https://github.com/seongjunyun/Graph_Transformer_Networks

---

### Motivation & Novelty

#### Problem

Graph neural networks have achieved strong results on homogeneous graphs, but real-world graphs are **heterogeneous** — they contain multiple types of nodes and edges. For example, in a citation network, nodes can be authors, papers, or conferences, connected by writes, cites, and publishes-at edges.

The standard solution requires hand-crafted **meta-paths**: composite edge-type sequences that encode meaningful multi-hop relations (e.g., Author→Paper→Author for co-authorship). Selecting useful meta-paths requires domain expertise and significantly affects model performance.

#### Limitations of Prior Methods

- **GCN** (Kipf & Welling, ICLR 2017): homogeneous graphs only; ignores edge-type information
- **GAT** (Veličković et al., ICLR 2018): attention on homogeneous graphs; same limitation
- **HAN** (Wang et al., arXiv 2019): uses manually defined meta-paths; two-stage pipeline; sensitive to meta-path choice
- **metapath2vec** (Dong et al., KDD 2017): random-walk on manually defined meta-paths; representations not task-optimized
- **DeepWalk** (Perozzi et al., KDD 2014): homogeneous graph embedding; no edge-type awareness

#### Key Contributions

1. **Automatic meta-path discovery**: GT layers learn soft edge-type combinations via 1×1 convolution + softmax, discovering useful meta-paths without domain knowledge
2. **End-to-end learning**: graph structure transformation and node representation learning are jointly optimized
3. **Interpretability**: attention weights $\alpha_{t_l}^{(l)}$ provide meta-path importance scores
4. **State-of-the-art**: best performance on all 3 benchmark node classification tasks without pre-defined meta-paths

---

### Method Overview

GTN learns to transform a heterogeneous graph into multiple new meta-path graphs, then performs GCN on the learned graphs for node classification.

#### Architecture Components

**1. Input Representation**
The heterogeneous graph is represented as K edge-type adjacency matrices $\{A_k\}_{k=1}^K$ in sparse COO format. An identity matrix is appended as an additional "edge type" to enable learning meta-paths of any length up to $l+1$.

**2. GT Layer (Graph Transformer Layer)**
The core innovation. Each GT layer:
- Applies **1×1 convolution with softmax weights** to compute a convex combination of edge-type adjacency matrices: $Q = \sum_k \alpha_k A_k$
- Learns **two** such combinations Q₁ and Q₂ (first layer) or reuses previous output as Q₁ (deeper layers)
- **Matrix-multiplies** Q₁ × Q₂ to produce a new meta-path adjacency: this discovers 2-hop connections through the heterogeneous graph
- Normalizes by row-degree: $A^{(l)} = D^{-1}(Q_1 Q_2)$

**3. Multi-Channel Meta-Paths**
Output channels C > 1 allows learning multiple different meta-paths simultaneously, each represented by an independent adjacency matrix.

**4. GCN on Meta-Path Graphs**
A single shared GCN applies to each of the C meta-path adjacency matrices, producing C node representations that are concatenated and passed to a linear classifier.

#### Key Design Choices

- **Identity matrix in A**: critical for learning variable-length meta-paths (GTN-I ablation without it performs worse, especially on IMDB where short paths are more informative)
- **Shared GCN weights across channels**: reduces parameters while allowing different graph structures per channel
- **Sparse matrix multiplication**: memory-efficient computation of meta-path adjacencies via `torch.sparse.mm()`

---

### Evaluation

#### Datasets

| Dataset | Nodes | Edge types | Task | Training/Val/Test |
|---|---|---|---|---|
| DBLP | 18,405 | 4 (PA, AP, PC, CP) | Author research area classification | 800/400/2857 |
| ACM | 8,994 | 4 (PA, AP, PS, SP) | Paper category classification | 600/300/2125 |
| IMDB | 12,772 | 4 (MD, DM, MA, AM) | Movie genre classification | 300/300/2339 |

All datasets are directed heterogeneous graphs. Node features are bag-of-words (334/1902/1256 dimensions).

#### Results (F1 Score, macro)

| Method | DBLP | ACM | IMDB |
|---|---|---|---|
| DeepWalk (KDD 2014) | 63.18 | 67.42 | 32.08 |
| metapath2vec (KDD 2017) | 85.53 | 87.61 | 35.21 |
| GCN (ICLR 2017) | 87.30 | 91.60 | 56.89 |
| GAT (ICLR 2018) | 93.71 | 92.33 | 58.14 |
| HAN (arXiv 2019) | 92.83 | 90.96 | 56.77 |
| **GTN-I** (ablation) | 91.13 | 91.13 | 52.33 |
| **GTN** (proposed) | **94.18** | **92.68** | **60.92** |

GTN outperforms all baselines on all datasets. Notably:
- GTN outperforms HAN (which uses pre-defined meta-paths) despite learning meta-paths automatically
- GTN uses only 1 GCN layer whereas GCN/GAT/HAN use at least 2 layers
- GAT performs better than HAN, suggesting pre-defined meta-paths can hurt performance
- GTN-I (without identity matrix) performs consistently worse, especially on IMDB (8.5% gap vs GTN)

#### Interpretability Analysis

GTN discovers meta-paths consistent with domain knowledge:
- **DBLP**: Top-ranked APA, APCPA (matches domain-defined meta-paths); also discovers CPCPA (conference→paper→conference→paper→author, novel)
- **ACM**: Discovers PAP, PSP (matches pre-defined)
- **IMDB**: Higher identity matrix attention → shorter paths preferred (MDM, not MDMDM)

---

### Reproducibility

**Rating: 3/5**

**Strengths**:
- Code is publicly available at GitHub
- Training protocol clearly specified (Adam, 200 epochs, 10 runs)
- Hyperparameters stated: embedding dim=64, lr=0.01, weight_decay=0.001
- Dataset statistics provided in Table 1

**Weaknesses**:
- Data preprocessing notebook provided, but raw data format (MATLAB .mat) requires specific loading
- Single fixed seed=777 for all 10 runs (not independent runs — deterministic)
- Weight initialization in paper (constant) differs from code (Normal std=0.01)
- Classifier description in paper ("two dense layers + softmax") differs from code (single linear)
- FastGTN variant is in the repo but not described in this paper
- No data download instructions; ACM.mat provided as sample but DBLP/IMDB require separate acquisition

**Practical notes**:
- Dependencies: PyTorch, torch_geometric, torch_sparse, torch_scatter (older API, may require specific versions)
- CUDA required: all tensors are explicitly moved to GPU
- Run command: `python main.py --model GTN --dataset ACM --num_layers 2 --num_channels 2 --epoch 200`
- Data expected at `../data/<DATASET>/` relative to script location

---

### Strengths and Weaknesses

**Strengths**:
- Elegant formulation: meta-path discovery as differentiable 1×1 convolution
- Interpretable: attention scores provide meta-path importance
- No domain knowledge required
- Strong empirical results across all benchmarks

**Weaknesses**:
- Computational cost: sparse matrix multiplication for meta-path construction is $O(E^2/N)$, expensive on large or dense graphs (motivates FastGTN extension)
- All runs use same seed (not truly independent); variance estimates may be misleading
- Assumes all nodes have features; no explicit handling of feature-less node types
- Limited to node classification; link prediction and graph classification require extension

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
