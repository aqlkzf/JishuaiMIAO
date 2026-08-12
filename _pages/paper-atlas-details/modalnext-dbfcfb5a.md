---
layout: default
permalink: /paper-atlas/modalnext-dbfcfb5a/
title: "modalnext"
nav: false
description: "Modal-NexT 的出发点是：RNA 基因、ATAC 峰、蛋白、细胞和空间邻居虽然类型不同，但都可以表示为图中的实体与关系。只要把观测矩阵转换成“某个细胞以某种强度连接某个特征”的关系边，就能用同一套图嵌入框架处理配对多组学、未配对多组学、空间多组学和同模态多来源数据。 本解读以本地原始 PDF/OCR Markdown、Figure 1–6，以及官方 GitHub 仓库代码为证据。"
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
      <span>Information Fusion · 2025</span>
    </div>
    <h1>modalnext</h1>
    <p>Modal-NexT: Towards unified heterogeneous cellular data integration</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.inffus.2025.103479" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Modal-NexT：用统一“细胞—特征图”处理四类异质数据整合

Modal-NexT 的出发点是：RNA 基因、ATAC 峰、蛋白、细胞和空间邻居虽然类型不同，但都可以表示为图中的实体与关系。只要把观测矩阵转换成“某个细胞以某种强度连接某个特征”的关系边，就能用同一套图嵌入框架处理配对多组学、未配对多组学、空间多组学和同模态多来源数据。

本解读以本地原始 PDF/OCR Markdown、Figure 1–6，以及官方 GitHub 仓库代码为证据。正文为 Information Fusion 论文，DOI `10.1016/j.inffus.2025.103479`，正式在线年份 2025，卷期元数据对应 2026。工作区 `src/` 和 `tutorial/` 与官方仓库当前固定提交 `94940e26608ab374926f87303e06260ab63b729d` 比较后内容一致；仓库没有 Python 包版本文件，因此 package version 为 `Not found`。论文链接指向在线补充材料，但本地 acquisition 中没有补充文件，当前也未取得可核验的独立补充正文；涉及 Supplementary Figure/Text 的结论仅按正文引用记录为 `Not found locally`，不能冒充已经读过补充图。

### 1. 统一表示：数值矩阵变成多关系二部图

给定某个模态矩阵 $A\in\mathbb N^{n\times m}$，行是细胞、列是特征。论文先做文库大小归一化，再除以每个特征的非零中位数，以降低测序深度和 housekeeping feature 量级的影响。随后只对非零值进行一维 K-means 辅助分箱：表达值所在 bin 不再只是边权，而成为不同 relation type。

图中于是有两类实体：cell node 与 feature node；一个非零观测对应

$$
(\text{cell}_i,\;\text{relation-bin}_b,\;\text{feature}_j).
$$

Figure 2a 从矩阵排序、分箱一直画到多颜色边，表达的正是这个变化。代码 `src/graph_src/tools/_general.py::discretize()` 默认 `n_bins=5`，而论文 Methods 写 10 个区间；教程实际使用值应以具体脚本为准。零表达不生成 cell-feature 边，因此“所有矩阵元素”并不等于“所有元素都有边”。

论文还强调不需要 ZINB、NB 或预先给定的峰—基因调控网络。这是说图构建不依赖这些 modality-specific priors，并不等于没有任何预处理或归一化假设。

### 2. 第一阶段：OT-NMF 给图节点一个有生物结构的起点

对于模态 $p$，把矩阵转置为 $X^{(pt)}\in\mathbb R_+^{m_p\times n}$，分解为 feature factor $H^{(p)}\in\mathbb R^{m_p\times k}$ 和 cell factor $W\in\mathbb R^{k\times n}$：

$$
L_{init}=\sum_j OT(H^{(p)}W_j,X_j^{(pt)})-\rho E(H^{(p)})-\mu E(W).
$$

普通 NMF 用逐元素误差；这里用特征之间的 optimal transport 距离。ground cost 默认由两个特征跨细胞表达轮廓的 cosine distance 决定。`src/nmf/models.py::nmfModel` 对每个模态保存 $H^{(p)}$，共享或分别建立 $W$，使用 OT dual variables 与 entropy regularization 交替更新。默认 latent dimension 50，RNA/ADT 的 $H$ regularization 为 $10^{-2}$、ATAC 为 $10^{-1}$、$W$ regularization 为 $10^{-3}$、OT entropy `eps=0.05`；默认 LBFGS，外层最多 100 次、内层最多 1000 次。

配对多模态中，同一个细胞实体跨模态共享 $W$，所以 RNA 与 ATAC/蛋白特征通过共同 cell node 间接联通。NMF 输出写入 `mdata.obsm['W_OT']` 与各模态 `uns['H_OT']`，作为第二阶段的预初始化；未被初始化的节点在教程中可用 Gaussian vectors 补齐。

### 3. 第二阶段：固定快照实际训练的是 PBG 关系图嵌入

论文 Eq. 4–7 把第二阶段描述为 GAT：邻居注意力聚合后用 edge classifier 重建 relation type。但固定仓库的可运行路径是修改过的 PyTorch-BigGraph：`gen_graph()` 写实体、relation 和 edge list，`pbg_train()` 调用 `MultiRelationEmbedder`，使用 relation-aware score、negative samples 与 Softmax/Ranking 等 loss 更新实体 embedding。

这两种描述不能直接画等号：在直接代码中没有找到论文公式那种显式 $a_{ij}$ 邻居 softmax 聚合层，也没有找到 $W_{cls}(f_i+f_j)$ 的多类 edge classifier。PBG 的核心是正边相对负采样边的打分/损失。准确边界是 cell-feature 多关系图和 edge reconstruction 的总体思想有实现，但论文具体 GAT 方程对当前公开训练路径是 `Partial / Not found`。

代码还有运行时细节：relation type 由每个表达 bin 分别生成；空间 cell-cell relation 独立加入；weight decay 会根据 edge count 经验缩放。旧文档曾把 bin relation 权重写成 1–5，但当前直接代码的 active relation config 对这些 cell-feature bin 设置 `weight: 1.0`，`expr_weight` 虽计算却没有用于该字段，这也是必须以当前快照为准的地方。

### 4. 四种任务如何落到同一张图

#### 4.1 配对多模态

RNA 与 ATAC/蛋白测的是同一批细胞时，跨模态对应细胞合并为一个 cell entity。该节点同时连向多种 feature entity；共享 OT-NMF cell factor 提供初始化，PBG 再重建多种关系。Figure 2b 展示了“共用 cell node”如何成为模态桥。

#### 4.2 未配对多模态

没有相同细胞时，每个模态先建立自己的 cell-feature graph 和 embedding。论文 Eq. 9–12 给出类似 DEC 的 fuzzy clustering、目标分布 $Q$、锐化辅助分布 $P$ 与 $L_{align}=KL(P\|Q)$ 迭代对齐，同时正文也明确给出 BBKNN 作为加速替代。固定仓库中没有找到 DEC loss/centroid gradient 的实现；`tutorial/unpaired_2_post_train.py` 读取两套 cell embedding、拼接后做 PCA/neighbors/UMAP，配套 notebook/说明走 BBKNN 快速后处理。因此论文 DEC 属于描述方法但公开快照实现 `Not found`，可复现路径是 PBG embedding 加后处理对齐。

#### 4.3 空间多模态

空间数据仍是配对多模态，但再按坐标给每个 spot 加 $r$ 个近邻 cell-cell edge。`construct_graph_by_coordinate()` 使用 `NearestNeighbors(n_neighbors=r+1)`，去掉自身后默认取 3 个邻居；教程把这些边交给 `gen_graph(list_CC=...)`。这里不是在表达矩阵上运行一个单独 spatial GCN，而是把空间邻接作为另一种 PBG relation 加进统一图。论文与 Figure 5 的敏感性讨论表明 $r$ 会影响组织域识别，作者选择 $r=3$，不能视为跨数据集的理论最优值。

#### 4.4 多来源同模态

多个 scRNA-seq 数据集拥有部分共享基因、部分特异基因。Modal-NexT 将同名共享 feature entity 合并，而来源特异 feature 保持独立；各数据集的 cell node 都连到自己的全部可用特征。Figure 2e 展示了通过 shared feature nodes 让不同来源图连通，而不是先取所有数据集的基因交集。

### 5. “使用全部特征”在代码中并非无条件成立

论文把保留非交集/非精选特征作为优势，但 `gen_graph()` 默认参数是 `use_highly_variable=True`、`use_top_pcs=True`：RNA 默认取 `.var['highly_variable']`，ATAC 默认取 top-PC-associated peaks。调用者可以关闭筛选，且多来源图能保留来源特异特征；然而不能把默认运行路径描述为必然包含每个原始 feature。复现报告必须列出这两个开关和实际节点数。

同样，`nmfModel` 构造器虽然保存 `highly_variable` 参数，却断言它必须为 `True`，随后直接读取 `.var['highly_variable']`。这说明 OT-NMF 初始化本身也依赖预先标记的特征集合，而非天然“全特征初始化”。

### 6. 图怎样支持论文的生物结论

Figure 1 先把四类任务分开定义。Figure 2 给出统一图构造方案。Figure 3 在 paired RNA+ATAC 上显示细胞 embedding 与聚类指标，并把 cell、gene、peak 放进同一空间；Hoxc13 附近的基因/峰与 TF-target network 是 embedding proximity 的解释性应用，相近表示不等于因果调控已被证明。

Figure 4 检验 unpaired integration：按模态着色看混合，按 cell type 着色看生物结构，并把 batch removal 与 biology conservation 分开。由于公开教程的后处理路径与论文 DEC 方程不同，论文数值不能只靠现有 `.py` 脚本就声称可逐点复现。

Figure 5 把 spatial cell-cell edge 用于 Lymph 与 Thymus。图中 Modal-NexT 识别 capsule、vessel 或 subcapsular zone，并用 CD169、Aire、Themis 空间表达作支持；其中 Thymus 没有 ground truth，DB score 是无监督紧致/分离指标，不能替代组织学真值。

Figure 6 展示 104 个癌症 scRNA 数据集的 multi-source integration：整合后 cell type 更集中，同时 epithelial cells 仍按 cancer type 分化；cell-gene joint embedding 还显示肿瘤 CD8 T 相关基因邻近。它支持“共享+特异 feature node 可保留来源表型”，但二维 UMAP 邻近不等于统计显著或临床预测。

### 7. 论文—代码映射的关键结论

| 论文机制 | 固定快照入口 | 判断 |
|---|---|---|
| 归一化、非零值一维 K-means 分箱 | `preprocessing/_general.py`, `tools/_general.py::discretize` | Exact；默认 5 bins，论文写 10 |
| OT-NMF 与共享 paired cell factor | `nmf/models.py`, `nmf/utils.py` | Exact |
| 多关系 cell-feature graph | `graph_src/tools/_pbg.py::gen_graph` | Exact |
| GAT attention Eq. 4–5 | active PBG model path | Not found；公开实现是 PBG relation scoring |
| classifier Eq. 6 与交叉熵 Eq. 7 | `torchbiggraph/model.py`, `losses.py` | Partial；loss/edge reconstruction 存在，打分结构不同 |
| DEC unpaired alignment Eq. 9–12 | `src/`, `tutorial/` | Not found；教程采用 post-hoc/BBKNN 路径 |
| spatial 3-NN cell-cell edges | `spatialknn/preprocess.py`, spatial tutorial | Exact |
| shared/specific feature nodes | `gen_graph()` entity union logic | Exact |
| “无特征选择”默认路径 | `gen_graph()` and `nmfModel` defaults | Partial/contradicted；默认使用 HVG/top-PC flags |

### 8. 版本与复现边界

1. 本地代码没有 `.repo_source`，但已将 `src/`、`tutorial/` 与官方仓库 HEAD `94940e26608ab374926f87303e06260ab63b729d` 做递归比较，除缓存目录外一致；合同固定这个提交。package version `Not found`。
2. `src/graph_src/tools/_pbg.py` 带有作者机器的硬编码 `sys.path.append(...)`，部署前必须确认本地 import 实际解析到工作区代码。
3. README 指定 Python 3.8、Torch 1.11/CUDA 11.3 时代依赖；未提供 lockfile，较新 PyTorch/Scanpy/MuData/PBG 组合可能不兼容。
4. benchmark 数据需另行从 Google Drive 下载，工作区没有 `dataset_repo` 大数据与预计算 `.h5mu/.h5ad`；教程不是可在当前目录直接端到端执行的完整快照。
5. 独立 supplementary 文件本地 `Not found`；因此 Supplementary Figures 1–15、Text 1 的细节没有被当前工作区直接核验。
6. 本次完成正文、六张主结果/方法图和直接代码的静态映射，但没有重跑 OT-NMF、PBG、BBKNN、百万细胞整合或论文 benchmark。端到端数值复现为 `Not run`。

一句话总结：Modal-NexT 真正统一的是“怎样把异质矩阵变成实体关系图”；OT-NMF 给节点一个结构化起点，PBG 用边重建更新 embedding，不同场景只改变 cell/feature 实体如何合并和增加哪些边。论文的 GAT 与 DEC 方程比当前公开快照更完整，理解方法时可以读，复现时必须以 PBG 和教程实际路径为准。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Modal-NexT: Towards Unified Heterogeneous Cellular Data Integration

### Paper Overview

**Citation**: Tang, Z., Chen, G., Chen, S., He, H., Huang, J., Dong, T., Zhou, J., Zhao, L., You, L., & Chen, C.Y.-C. (2025). Modal-NexT: Towards unified heterogeneous cellular data integration. *Information Fusion*, 103479.

**Code Repository**: https://github.com/shapsider/modalnext

---

### Motivation & Novelty

#### Biological Problem
Current AI integration techniques for heterogeneous cellular data are isolated in different scenarios - each method is designed for specific modality combinations (RNA+ATAC vs RNA+Protein vs spatial) without a unified paradigm. This fragmentation hinders progress toward artificial intelligence virtual cells (AIVCs).

#### Key Limitations of Existing Methods
1. **Graph-based methods** (SIMBA, Monae): Rely on prior biological regulatory data; complex training
2. **Autoencoder-based methods** (MultiVI, totalVI): Loss of interpretability; restricted to specific modalities
3. **Linear-based methods** (Mowgli, NMF): Good interpretability but struggle to preserve complex biological heterogeneity

#### Core Contributions
1. **Unified integration paradigm** that treats cells and features as entities in a joint graph
2. **Four integration scenarios** unified under one framework:
   - Paired multi-modal integration
   - Unpaired multi-modal integration
   - Spatial multi-modal integration
   - Multi-source integration
3. **No modality-specific likelihood or regulatory-network prior** is required, although normalization, discretization, graph topology, optional OT-NMF initialization and feature-selection flags remain important assumptions.
4. **Comprehensive benchmarks** covering multiple integration scenarios

---

### Method Overview

#### Algorithmic Framework

Modal-NexT operates in two stages:

**Stage 1: Integrative Non-negative Matrix Factorization (iNMF) Initialization**
- Uses optimal transport-based NMF to obtain initial embeddings
- Decomposes expression matrix $\mathbf{X}^{(pt)} \in \mathbb{R}^{m_p \times n}_+$ into:
  - $\mathbf{H}^{(p)} \in \mathbb{R}^{m_p \times k}$ (feature embeddings)
  - $\mathbf{W} \in \mathbb{R}^{k \times n}$ (shared cell embeddings)
- Loss function with entropy regularization:

$$L_{init} = \sum_{j=1}^{n} OT(\mathbf{H}^{(p)}\mathbf{W}_{j}, \mathbf{X}_{j}^{(pt)}) - \rho E(\mathbf{H}^{(p)}) - \mu E(\mathbf{W})$$

**Stage 2: Graph-based Transductive Learning (PyTorch-BigGraph)**
- Constructs cell-feature joint graph with binned edge types
- Edge construction: Sort and bin normalized feature expressions into 5-10 discrete levels
- Uses Graph Attention Network (GAT) for embedding updates:

$$f_i = sigmoid(\sum_{j \in N(i)} a_{ij}[W_{gat}f_i])$$

- Edge reconstruction loss:

$$L_{transductive} = -ylog(c_{edge})$$

#### Four Integration Scenarios

| Scenario | Cell Pairing | Edge Types | Special Handling |
|----------|-------------|------------|------------------|
| Paired | Same cell across modalities | Cell-Feature (multi-modal) | Merge paired cell entities |
| Unpaired | Different cells | Cell-Feature (per modality) | DEC-based alignment |
| Spatial | Same cell + coordinates | Cell-Feature + Cell-Cell | KNN spatial graph |
| Multi-source | Multiple datasets | Shared + Specific features | Feature entity merging |

---

### Evaluation

#### Datasets
| Dataset | Cells/Spots | Modalities | Scenario |
|---------|-------------|------------|----------|
| MouseSkin | 6,436 | RNA+ATAC | Paired |
| Liu | 206 | RNA+ATAC | Paired |
| 10xPBMC | 9,320 | RNA+ATAC | Paired |
| OP-CITE | 4,249 | RNA+Protein | Paired |
| 10xMultiome | 9,631 | RNA+ATAC | Unpaired |
| Ma2020 | 32,231 | RNA+ATAC | Unpaired |
| Muto2021 | 44,190 | RNA+ATAC | Unpaired |
| Lymph | 3,484 | RNA+Protein | Spatial |
| Thymus | 4,697 | RNA+Protein | Spatial |
| Pancancer | ~1M | scRNA-seq | Multi-source |

#### Metrics
- **Paired integration**: AMI, ARI, HOM, NMI (clustering quality)
- **Unpaired integration**: Batch remove + Biology conservation → Overall score
- **Spatial integration**: DB score, multi-resolution tissue region identification

#### Key Results
1. **Paired**: Modal-NexT achieves competitive AMI/ARI/NMI across RNA+ATAC and RNA+Protein datasets
2. **Unpaired**: Balances batch removal and biology conservation; automatic batch integration without explicit design
3. **Spatial**: Captures fine structures (capsule, vessels) missed by other methods; best DB score
4. **Multi-source**: Integrates 104 cancer studies (~1M cells); recovers clinical phenotypes (tumor vs normal)

---

### Biological Insights

#### TF-Target Network Inference
- Feature embedding similarity enables cross-modal regulatory inference
- Example: Hoxc13 (TF) and chr15 peaks validated for hair follicle differentiation

#### Cell Type Marker Discovery
- Cell type-specific factors from NMF initialization
- Top features per factor correspond to known markers (Hoxc13, Krt71, Foxq1)

#### Tumor-Normal System
- Accurately localizes tumor-related genes near specific cell types
- Identifies genes (CD27, CXCL13, PDCD1, TIGIT, CTLA4, LAG3, TNFRSF9) for tumor CD8+ T cells
- Provides complementary insights beyond differential expression analysis

---

### Reproducibility Assessment

#### Rating: 4/5 (Good)

#### Strengths
1. **Code availability**: Complete pipeline provided with tutorials for all scenarios
2. **Dependencies clear**: Standard packages (muon, scanpy, PyTorch-BigGraph)
3. **Dataset links**: Google Drive links for all benchmark datasets
4. **Step-by-step tutorials**: Numbered Python scripts for each scenario

#### Potential Blockers
1. **PyTorch-BigGraph path**: Hard-coded path in `_pbg.py:11` requires modification
2. **Data preprocessing**: Relies on pre-computed `.h5mu.gz` files not fully documented
3. **GPU memory**: Large datasets may require significant VRAM
4. **Dependency versions**: torch-1.11.0+cu113 is specified; compatibility with newer versions is not documented or verified here.

#### Environment Requirements
```
Python 3.8
muon
torchbiggraph
scanpy
pytorch-ignite
tensorboardX
torch-1.11.0+cu113
```

---

### Critical Assessment

#### Advantages
1. **Truly unified**: One paradigm for all heterogeneous cellular data scenarios
2. **No modality-specific prior required**: It avoids modality-specific likelihoods and regulatory networks, but still depends on preprocessing and graph-design choices.
3. **Can retain heterogeneous/source-specific features**: the graph is not restricted to the cross-dataset feature intersection, but released defaults still enable HVG/top-PC feature selection.
4. **Interpretable**: NMF-based initialization provides factor analysis capabilities

#### Limitations
1. **Two-stage pipeline**: Separate NMF and GNN training steps
2. **Hyperparameter sensitivity**: Spatial integration sensitive to neighbor count (r=3 optimal)
3. **Alignment method**: Unpaired scenario relies on DEC clustering quality
4. **Computational cost**: PBG training for large graphs can be expensive

#### Comparison with Related Work
| Method | Paired | Unpaired | Spatial | Multi-source | No Priors |
|--------|--------|----------|---------|--------------|-----------|
| Modal-NexT | ✓ | ✓ | ✓ | ✓ | ✓ |
| SIMBA | ✓ | ✗ | ✗ | ✗ | ✓ |
| Monae | ✓ | ✓ | ✗ | ✗ | ✗ |
| MultiVI | ✓ | ✓ | ✗ | ✗ | ✗ |
| SpatialGLUE | ✗ | ✗ | ✓ | ✗ | ✗ |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
