---
layout: default
permalink: /paper-atlas/deepmaps-655cdcb8/
title: "DeepMAPS"
nav: false
description: "论文：Single-cell biological network inference using a heterogeneous graph transformer（Nature Communications, 2023；DOI: 10.1038/s41467-023-36559-0）。DeepMAPS 把“整合细胞”和“推断细胞类型特异网络”放进同一条路径：先把特征和细胞组成二部异质图，再以 HGT 同时学习基因（或蛋白）和细胞表示；"
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
      <span>Nature Communications · 2023</span>
    </div>
    <h1>DeepMAPS</h1>
    <p>Single-cell biological network inference using a heterogeneous graph transformer</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-023-36559-0" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for DeepMAPS">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/OSU-BMBL/deepmaps" target="_blank" rel="noopener noreferrer" aria-label="Open code for DeepMAPS">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DeepMAPS：用异质图 Transformer 从单细胞多组学推断生物网络

论文：*Single-cell biological network inference using a heterogeneous graph transformer*（Nature Communications, 2023；DOI: `10.1038/s41467-023-36559-0`）。DeepMAPS 把“整合细胞”和“推断细胞类型特异网络”放进同一条路径：先把特征和细胞组成二部异质图，再以 HGT 同时学习基因（或蛋白）和细胞表示；模型的基因—细胞注意力接着服务于基因模块、调控子和 GRN 推断。

### 1. 问题与总流程

常见整合工具可给出细胞嵌入或聚类，但不把“哪个特征对哪个细胞重要”作为模型内部的可解释边。DeepMAPS 的输出既包括 cell/gene embedding 与注意力，也包括细胞聚类、簇活跃基因模块，及 scRNA-ATAC 情形下的 GRN：

```text
原始多组学计数 → 按模态整合为特征×细胞矩阵 X
→ 基因/特征节点 + 细胞节点的二部图 → AE 初始表示 → HGT
→ cell/gene embedding 与 attention → 聚类、SFP 模块、GRN
```

边的存在由 $X$ 的非零项决定，而非先计算全局基因相关性（`paper.md:176-196`）。

### 2. 三种输入如何统一为 $X$

论文约定行是特征、列是细胞；低于 0.1% 非零的行或列会移除（`paper.md:134-136`）。

- **多个 scRNA-seq**：log-normalize、每个矩阵选前 2,000 HVG、用 Seurat CCA 对齐，得到 $I$ 个基因、$J$ 个细胞的 $X$（`paper.md:138-140`）。
- **CITE-seq**：RNA 与表面蛋白分别 log-normalize、纵向拼接，并做 CLR：

$$\mathrm{CLR}(x_{ij})=\log\left(1+\frac{x_{ij}}{\exp\left(\frac{\sum_{i\in\mathscr Z_j}\log(1+x_{ij})}{|\mathscr Z_j|}\right)}\right).$$

$\mathscr Z_j$ 是 cell $j$ 的非零特征索引集合（`paper.md:142-147`）。
- **scRNA-ATAC-seq**：由 peak 到基因的调控潜能得到 $X^{A'}$，结合表达 $X^R$ 与 RNA velocity 得到 GAS：

$$x_{ij}^{G}=\begin{cases}x_{ij}^{R}+(1+\beta^+)x_{ij}^{A'},&x_{ij}^{V}>0\\x_{ij}^{R}+(1-\beta^-)x_{ij}^{A'},&x_{ij}^{V}<0\\x_{ij}^{R}+x_{ij}^{A'},&x_{ij}^{V}=0.\end{cases}$$

正速度提高可及性贡献，负速度降低它（`paper.md:149-175`）。本地 `calculate_GAS_v1` 读取外部 velocity CSV、按行/列 rank 构造带符号权重并计算 `GAS`（`deepmaps/scRNA_scATAC1.r:403-505`）。**Not found（已检索 Python/R/Docker 路径）**：该快照没有 RNA-velocity 计算和论文所述 LTMG 离散化；它消费的是已给定 velocity 文件。

### 3. 图与 autoencoder 初始表示

给定 $X=\{x_{ij}\}$，DeepMAPS 建立 $G=(V,E,A,R)$：基因/特征节点 $V^G$、细胞节点 $V^C$，$x_{ij}>0$ 时有 gene--cell 边，论文把该边权置为 1（`paper.md:176-192`）。驱动以 `np.nonzero(gene_cell)` 取边，以基因数偏移 cell ID，并写入正向 `g_c` 与反向 `rev_g_c` 邻接表（`deepmaps/arg.py:507-549`）。

两个独立 AE 分别压缩“每个基因跨细胞的向量”和“每个细胞跨基因的向量”，论文目标为

$$loss=\mathrm{MSE}(X,\hat X),\qquad loss=\mathrm{MSE}(X^T,\widehat{X^T}).$$

（`paper.md:178-184`）。源码的 `AE` 为 `dim→512→256→512→dim`、ReLU（`deepmaps/reduction.py:8-27`），`train_AE` 用 Adam、MSE、2,000 epoch（`reduction.py:57-80`）；`arg.py` 分别实例化 gene 与转置 cell 的模型（`arg.py:435-496`）。

### 4. HGT：Q/K/V、关系注意力和输出

对目标节点 $v_t$ 与相邻源节点 $v_s$，每个 head 使用节点类型专属线性层：

$$Q^h(v_t)=Q^h_{\mathrm{linear},\tau(v_t)}(\mathcal H^{(l-1)}[v_t]),$$
$$K^h(v_s)=K^h_{\mathrm{linear},\tau(v_s)}(\mathcal H^{(l-1)}[v_s]),\qquad V^h(v_s)=V^h_{\mathrm{linear},\tau(v_s)}(\mathcal H^{(l-1)}[v_s]).$$

这是论文 Eq. 9--11（`paper.md:204-220`）。每个 meta-relation 还有独立 attention/message 矩阵：

$$ATT_{head}^{h}(v_s,e_{s,t},v_t)=\left(K^h(v_s)W_{\phi(e_{s,t})}^{ATT}Q^h(v_t)^T\right)\cdot\frac{\mu\langle\tau(v_s),\phi(e_{s,t}),\tau(v_t)\rangle}{\sqrt d},$$

并在 $v_t$ 邻域上对多头结果 softmax（`paper.md:227-236`）。`HGTConv.message` 创建 `q_linears/k_linears/v_linears`、按 relation 取 `relation_att/relation_msg/relation_pri` 并产生 raw score（`deepmaps/pyHGT/conv.py:30-115`）；第 124 行才以目标节点为单位 softmax 加权消息。

论文的消息/更新为

$$MSG_{head}^{h}(v_s,e_{s,t},v_t)=V^h(v_s)W_{\phi(e_{s,t})}^{MSG},$$
$$\widetilde{\mathcal H}^{l}[v_t]=\operatorname{Aggregate}_{v_s\in\mathscr N(v_t)}(Attention\cdot Message).$$

（`paper.md:238-263`）。源码使用 GELU、类型专属输出层、sigmoid 限制的 skip mixing 和 LayerNorm（`conv.py:130-151`），是论文抽象更新的具体实现。

论文把最后一层各 head 的 L2 norm 定义为 gene-to-cell importance：

$$a_{ij}=\sqrt{\sum_h ATT_{head}^{h}(i,j)^2}.$$

（`paper.md:268-274`）。关键代码边界是：`model.py` 虽收集各层 `gc.res_att`，却固定 `self.att=self.att[0]`（`deepmaps/model.py:128-143`），`arg.py` 导出该 `gnn.att`（`arg.py:830-897`）。所以快照输出的是**第一层 raw、多头 score**，不能直接当作论文的“最后层、softmax 后再作 L2 norm”的 $a_{ij}$。

### 5. 子图训练与损失

为避免巨图训练，论文以 50 个子图覆盖 30% 节点；对一个 cell，邻居 gene 按 $x_{ij}$（表达或 GAS）抽样：

$$\mathrm{Prob}(e_{s,t})=\frac{x(v_s,v_t)}{\sum_{v\in\mathscr N(v_t)}x(v,v_t)}.$$

HGT 是 GAE encoder，embedding 内积重建 $\hat X$，损失为

$$loss=\mathrm{KL}(\mathrm{softmax}(\hat X),\mathrm{softmax}(X)).$$

（`paper.md:276-284`）。Python 驱动的 KL 分支为 `F.kl_div(decoder.softmax(...).log(), adj.softmax(...))` 并反传更新（`deepmaps/arg.py:730-780`）。具体运行参数和分支依入口而变，不能把论文的 50/30%/100 epoch 当作所有本地运行的硬编码。

### 6. SFP 模块和 scRNA-ATAC GRN

论文先用 final cell embedding 做 Louvain 聚类（默认 resolution 0.4；`paper.md:286-290`）。在每簇内，以 gene embedding Pearson 相关（>0.5）形成 gene--gene 边，以 $a_{ij}>\mu(a)+sd(a)$ 形成 gene--cell 边，再解连接簇内细胞且总边权最小的 SFP（`paper.md:292-300`）。代码 `get_gene_module` 调 `global_matching_graph` 和 `set_cover_mst`（`scRNA_scATAC1.r:625-649`）；后者在 terminal/邻域诱导图上做 Prim MST、删除非 terminal 叶节点、合并并再裁剪（`scRNA_scATAC1.r:1365-1429`）。它使用驱动输出的 attention，故继承上一节 attention 定义差异。

仅对 scRNA-ATAC，论文用 TF--peak binding 与 peak--gene potential 构造 regulatory intensity：

$$s_{ij|q}=\sum_k b_{qk}^{A}\,r_{ik|j},$$

随后以簇内表达与 RI 得 regulon activity，再将 regulon 合并为 GRN、以 eigenvector centrality 排主 TF（`paper.md:301-316`）。Docker 示例展示完整调用链：GAS → `run_HGT` → `get_gene_module` → 外部 LISA → `Calregulon`/`uni` → `RI_cell` → `calRAS`/`CalRAS2` → `masterFac`（`deepmaps/docker/test.R:135-237`）。`RI_cell` 实作 peak/gene/TF 矩阵乘积（`scRNA_scATAC1.r:980-1036`），`masterFac` 建簇特异邻接矩阵并调 `igraph::evcent`（`scRNA_scATAC1.r:1144-1188`）。外部 JASPAR/LISA 资产、LISA 运行和 peak 注释仍是运行依赖；

### 7. 评价与边界

论文在多个 scRNA、CITE-seq、scRNA-ATAC 基准上比较 Seurat、MOFA+、Harmony、TotalVI、GLUE 等；带标签任务用 ARI、无标签 ATAC 用 AWS 选参数（`paper.md:320-328`）。网络比较 IRIS3 和普通共表达网络；GRN 相对 Reactome、DoRothEA、TRRUST v2 以 precision/recall/F1 评价（`paper.md:361-381`）。这是论文的评估设计，不能由未运行的快照替代。

- 已直接核查：AE、非零边建图、HGT Q/K/V/关系变换/softmax/残差、KL 分支、GAS、SFP/MST、RI/RAS/GRN centrality。
- **Not found（检索范围：`deepmaps/` Python/R 及 Docker 示例）**：RNA-velocity 计算和 LTMG 离散化实现；GAS 只读取外部 CSV velocity。
- **图像边界**：本次未读取 raw figure image，不作任何基于图像视觉内容的判断。

复核时先读本文件，再读 `doc_code.md` 的 Match Assessment，最后回到 `paper source/PMC9944243/paper.md` 与上述精确源码行。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DeepMAPS: Single-cell Biological Network Inference Using a Heterogeneous Graph Transformer

**Paper**: Ma A, Wang X, Li J, et al. *Nature Communications* 14, 964 (2023)
**DOI**: [10.1038/s41467-023-36559-0](https://doi.org/10.1038/s41467-023-36559-0)
**Code**: [https://github.com/OSU-BMBL/deepmaps](https://github.com/OSU-BMBL/deepmaps)
**Webserver**: [https://bmblx.bmi.osumc.edu/](https://bmblx.bmi.osumc.edu/)

---

### Motivation & Novelty

#### Biological Problem
Single-cell multi-omics technologies (scRNA-seq + scATAC-seq, CITE-seq) capture multiple regulatory layers simultaneously, but existing integration tools — Seurat v3/v4 (*Cell*, 2021), MOFA+ (*Genome Biology*, 2020), Harmony (*Nature Methods*, 2019), TotalVI (*Nature Methods*, 2021) — focus on cell clustering and batch correction. They do not explicitly model the topological relationships between genes and cells, and thus cannot infer cell-type-specific biological networks (gene regulatory networks, gene association networks) as a direct output of the integration process.

#### Limitations of Existing Approaches
1. **No gene-level topology**: Existing methods learn cell embeddings but do not jointly learn gene representations in the same latent space, losing gene-gene relational information.
2. **Post-hoc network inference**: GRN tools like SCENIC (*Nature Methods*, 2017) and IRIS3 (*Nucleic Acids Research*, 2020) infer networks after clustering, using gene co-expression correlation. This is hypothesis-driven (co-expression ≈ regulation) and cannot capture non-co-expressed regulatory relationships.
3. **No attention-based interpretability**: Existing GNN methods for single-cell data (scGNN, *Nature Communications*, 2021) use homogeneous graphs (cells only), missing the gene dimension.

#### Unique Contributions
1. **Heterogeneous graph formulation**: Models scMulti-omics as a bipartite graph with cells and genes as distinct node types, enabling joint embedding learning.
2. **HGT for scMulti-omics**: Adapts the heterogeneous graph transformer (Hu et al., 2020) with multi-head attention and relation-specific transformations to learn gene-to-cell importance scores.
3. **End-to-end network inference**: Cell clustering and biological network construction happen within one framework, where attention scores directly indicate gene importance to cell types.
4. **Velocity-weighted integration**: A novel RNA velocity-based method to balance gene expression and chromatin accessibility contributions in scRNA-ATAC-seq data.
5. **Steiner Forest Problem (SFP)**: Uses combinatorial optimization to extract minimal gene modules connecting cells within clusters, yielding biologically compact networks.

---

### Method Overview

DeepMAPS operates in five major stages:

1. **Data preprocessing and integration**: Modality-specific normalization (log-norm for RNA, CLR for CITE-seq protein, MAESTRO peak-to-gene mapping + velocity-weighted GAS for scRNA-ATAC-seq) produces an integrated gene-cell matrix.

2. **Initial embedding**: Two separate autoencoders (dim→512→256) learn initial representations for genes and cells independently, trained with MSE reconstruction loss (2000 epochs).

3. **HGT training**: A bipartite heterogeneous graph (genes + cells as nodes, edges where expression > 0) is trained with a graph autoencoder using:
   - Multi-head attention with type-specific Q/K/V projections and relation-specific transformation matrices
   - Subgraph sampling (50-80 mini-batches) for scalability
   - KL divergence loss on reconstructed adjacency vs. original

4. **Cell clustering**: Louvain clustering on HGT-learned cell embeddings (resolution=0.4).

5. **Network inference**: SFP-based gene module extraction using embedding correlations and attention scores, followed by GRN construction (for scRNA-ATAC-seq) using JASPAR TF binding data and regulon activity scoring.

See `doc_method.md` for detailed equations and `doc_code.md` for implementation mapping.

---

### Evaluation

#### Datasets
- **Benchmarking**: 10 datasets (3 multiple scRNA-seq, 3 CITE-seq, 4 scRNA-ATAC-seq) with cell counts ranging from 3,009 to 32,029
- **Independent testing**: 5 additional datasets (R-test, C-test, A-test-1/2/3)
- **Case studies**: (1) Mixed PBMC + lung tumor leukocyte CITE-seq (3,485 cells); (2) DSLL lymph node scRNA-ATAC-seq (14,566 cells)

#### Compared Methods
| Method | Task | Version |
|---|---|---|
| Seurat v3/v4 (*Cell*, 2021; *Nature Biotechnology*, 2018) | Cell clustering | v3.2.3, v4.0 |
| MOFA+ (*Genome Biology*, 2020) | Cell clustering | v1.0.0 |
| Harmony (*Nature Methods*, 2019) | Cell clustering | v0.1 |
| TotalVI (*Nature Methods*, 2021) | Cell clustering | v0.10.0 |
| GLUE (*Nature Biotechnology*, 2022) | Cell clustering | v0.3.2 |
| SCENIC (*Nature Methods*, 2017) | GRN inference | — |
| IRIS3 (*Nucleic Acids Research*, 2020) | Gene association network | — |
| MAESTRO (*Genome Biology*, 2020) | GRN inference (ATAC) | — |

#### Key Results
- **Cell clustering**: DeepMAPS achieved best ARI (for labeled datasets) and ASW (for unlabeled datasets) across all 10 benchmark datasets under grid-search parameter optimization (36 parameter combos)
- **Independent testing**: Best ARI on 3 labeled test datasets with default parameters; comparable performance on unlabeled datasets
- **Robustness**: Best performance in cell cluster leave-one-out tests
- **Gene association networks**: Significantly higher closeness centrality (CC) and eigenvector centrality (EC) compared to IRIS3 and background co-expression networks
- **GRN quality**: More unique TF regulations, higher number of cell-type-specific regulons enriching to single pathways, competitive F1 scores on Reactome, DoRothEA, and TRRUST v2 databases
- **Biological validation**: Identified BAFF→TACI→AP-1(JUN)→CDK6 signaling axis in DSLL, connecting cell-cell communication to downstream GRN regulation

#### Metrics
- Cell clustering: ARI, ASW, CH index, DBI
- Network evaluation: Closeness centrality, eigenvector centrality
- GRN evaluation: Precision, recall, F1 score against Reactome/DoRothEA/TRRUST v2
- Statistical tests: Two-tailed t-test, Wilcoxon rank-sum test (BH-adjusted)

---

### Reproducibility

**Rating: 3/5** (Moderate)

#### Strengths
- **Code available**: GitHub repository with Python + R code, Docker container, and web portal
- **Data available**: All benchmark datasets publicly available (GEO, figshare, 10× Genomics)
- **Grid-search parameters documented**: Default parameters per data type specified in code
- **Webserver**: Code-free interface at bmblx.bmi.osumc.edu (may not be maintained long-term)

#### Weaknesses
- **R-Python split**: Core pipeline requires R (reticulate) to call Python. The Python code is not standalone — `arg.py` reads from an R variable (`r.list_in`). This creates a complex cross-language dependency.
- **Missing velocity integration code**: The novel velocity-weighted GAS integration (a key contribution) is not fully implemented in the released code. The rank-based $\beta$ computation is absent from the repository.
- **Outdated dependencies**: PyTorch 1.9.1, torch-geometric 2.0.1, Python 3.8.5 — all significantly outdated. The CUDA 11.0 requirement may cause compatibility issues on modern systems.
- **JASPAR data not included**: The TF binding site data directory (`jaspar/`) contains only a README; users must download the actual data separately.
- **Attention score discrepancy**: Code stores first-layer pre-softmax attention rather than the L2-normed final attention described in Eq. 18, which may affect downstream network inference quality.
- **No training configuration files**: Grid-search requires manual parameter specification; no automated benchmarking scripts included.
- **GPU reproducibility caveat**: Authors acknowledge in the Discussion that different GPU models may produce slightly different results due to floating-point precision differences. The precision truncation trick in code (`trunc(x*1e10)/1e10`) partially addresses this but is not documented.

#### Practical Notes
- **Environment**: Requires both R (Seurat, Signac, igraph) and Python (PyTorch, torch-geometric) environments. Docker image recommended.
- **GPU**: NVIDIA A100 recommended; the subgraph sampling approach makes memory requirements moderate (~8GB for typical datasets).
- **Runtime**: Deep learning models (DeepMAPS, TotalVI) are slower than Seurat and MOFA+. AE pre-training (2000 epochs × 2) adds significant overhead.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
