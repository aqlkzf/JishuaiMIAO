---
layout: default
permalink: /paper-atlas/simba-ca5fca8b/
title: "SIMBA"
nav: false
description: "SIMBA 要解决的是单细胞分析里的一个结构性问题：很多方法只学习细胞的低维表示，然后依赖聚类结果去找 marker 或做解释。这样会带来两个后果。第一，marker 发现会受聚类分辨率和聚类算法影响；第二，scRNA-seq、scATAC-seq、多模态分析、批次校正、多组学整合往往被写成不同任务，需要不同方法和不同解释流程。 SIMBA 的核心想法是：不要只把细胞嵌入到低维空间，而是把细胞和生物学特征一起嵌入。"
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
      <span>Representation Models</span>
      <span>Nature Methods · 2024</span>
    </div>
    <h1>SIMBA</h1>
    <p>SIMBA: single-cell embedding along with features</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-023-01899-8" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SIMBA 方法中文解释

### 这篇论文要解决什么问题？

SIMBA 要解决的是单细胞分析里的一个结构性问题：很多方法只学习细胞的低维表示，然后依赖聚类结果去找 marker 或做解释。这样会带来两个后果。第一，marker 发现会受聚类分辨率和聚类算法影响；第二，scRNA-seq、scATAC-seq、多模态分析、批次校正、多组学整合往往被写成不同任务，需要不同方法和不同解释流程（`paper.md:21-30`）。

SIMBA 的核心想法是：不要只把细胞嵌入到低维空间，而是把细胞和生物学特征一起嵌入。这里的特征可以是基因、开放染色质区域 peak、TF motif、k-mer 等。论文把这些对象都看成图节点，把表达、可及性、序列匹配、跨批次/跨模态相似性看成边，然后用图嵌入方法学习所有节点的共同表示（`paper.md:27-33`, `paper.md:42-59`）。

### 方法总览

```text
单细胞矩阵
  |
  v
预处理和特征选择
  |
  v
构图：cell / gene / peak / motif / k-mer / cell-cell
  |
  v
PyTorch-BigGraph 训练多关系图嵌入
  |
  v
得到细胞和特征的初始 embedding
  |
  v
Softmax transformation 让不同类型节点可比较
  |
  v
查询邻居、计算特征特异性指标、找 marker、推断调控因子和靶基因
```

这个设计的关键是“任务差异体现在图怎么建，而不是每个任务重新设计一套模型”。同一个 `gen_graph` 入口可以接收 RNA、ATAC、motif、k-mer、跨数据集 cell-cell 边等输入（`simba/simba/tools/_pbg.py:28-45`），再输出 PyTorch-BigGraph 需要的图文件和实体别名（`simba/simba/tools/_pbg.py:523-546`）。

### 第一步：把数据变成图边

#### scRNA-seq

论文先过滤低表达基因，做 library-size normalization 和 log transform，然后可以选择 variable genes（`paper.md:237-240`）。构图时，如果某个细胞表达某个基因，就在 cell 和 gene 之间连边。为了把表达强度变成图关系，SIMBA 把非零表达值离散成多个等级，默认 5 个 bin，并把不同等级编码成不同关系，权重从 1.0 到 5.0（`paper.md:258-261`）。

代码里，`discretize` 默认 `n_bins=5`，对非零表达值做直方图近似和一维 KMeans，再把离散结果写入 `adata.layers['disc']`（`simba/simba/tools/_general.py:7-71`）。`gen_graph` 会读取这些离散等级，为每个等级创建一个 cell-gene relation，并把权重线性映射到 1 到 5（`simba/simba/tools/_pbg.py:377-423`）。

#### scATAC-seq

ATAC 任务中，peak-by-cell 矩阵被二值化；如果有序列信息，还可以把 peak-by-motif 和 peak-by-k-mer 矩阵加入图中（`paper.md:264-268`）。代码中 cell-peak 边权重为 1.0，peak-motif 边权重为 0.2，peak-k-mer 边权重为 0.02（`simba/simba/tools/_pbg.py:256-375`）。

论文提到的 `scan_for_kmers_motifs.R` 在当前代码快照中确实存在。它从 BED 区域生成 FASTA，用 `Biostrings` 统计 k-mer，用 `JASPAR2020` 和 `motifmatchr` 扫描 motif，并把结果写成 HDF5 矩阵（`R_scripts/scan_for_kmers_motifs.R:1-142`）。

### 第二步：批次校正和跨模态整合的 cell-cell 边

批次校正时，SIMBA 先按 scRNA-seq 的方式为每个 batch 建 cell-gene 图，然后用计算推断的 cell-cell 边把不同 batch 的图连接起来。论文定义两个数据矩阵 \(X1\) 和 \(X2\)，先算：

$$X=X1\times {X2}^{T}$$

再做截断 randomized SVD：

$$X\approx U\times \Sigma {\times V}^{T}$$

随后对 \(U\) 和 \(V\) 做 L2 归一化，保留 mutual nearest neighbors 作为跨 batch 的 cell-cell 边（`paper.md:279-297`）。

代码中的 `infer_edges` 与这个描述匹配：它找 shared features，计算 `X_ref * X_query.T`，调用 `randomized_svd`，归一化两个低维矩阵，做双向 KNN，并只保留互为近邻的 cell 对（`simba/simba/tools/_integration.py:12-152`）。这些边会放在 `layers['conn']`，然后 `gen_graph` 把它们变成 cell-cell relation（`simba/simba/tools/_pbg.py:425-521`）。

跨 scRNA-seq 和 scATAC-seq 的整合需要先把 ATAC peak 转成 gene activity score。论文用 TSS 上下游 100 kb 的 peak，gene body 或 gene body 上游 5 kb 内的 peak 权重为 1，其他 peak 用指数衰减：

$$e^{\frac{-distance}{5000}}$$

然后对 peak 做加权求和并按 gene size 缩放（`paper.md:303-303`）。代码中的 `GeneScores` 默认参数正是 100 kb 和 5 kb，并实现了注释读取、TSS/gene body 扩展、距离权重、gene size 缩放和 cells-by-genes 输出（`simba/simba/tools/_gene_scores.py:27-272`）。

### 第三步：图嵌入训练

论文把图写成 \(G=(V,E)\)。每个实体 \(v\) 有一个向量 \(\theta_v\)。对于边 \(e=(u,v)\)，得分是点积：

$$s_e=\theta_u\cdot\theta_v$$

论文的边损失是：

$$&#123;&#123;\mathscr{L}}}_{e}=-\log \frac&#123;&#123;\rm{exp }}\left({s}_{e}\right)}{\sum _&#123;&#123;e}^&#123;&#123;\prime} }&#123;&#123;\in }}{\mathscr{N}}}{\rm{exp }}\left(&#123;&#123;s}}_{e^&#123;&#123;\prime} }}\right)}{w}_{e}$$

其中 \(\mathscr{N}\) 是负采样候选边集合，\(w_e\) 是边权重（`paper.md:321-327`）。论文强调负采样要满足类型约束，例如 cell-peak 的负样本也应该是 cell-peak 类型，而不是无意义的 peak-peak 边（`paper.md:330-333`）。为了减少过拟合，论文还加入 L2 正则：

$$&#123;&#123;\mathscr{L}}}_{\rm{reg}}{\mathscr{=}}{\mathscr{L}}{\mathscr{+}}\lambda \sum _{u\in N}\mathop{\sum }\limits_{d=1}^{D}{\theta }_&#123;&#123;ud}}^{2}.$$

这里 \(\lambda=wd\times wd_{interval}\)，论文默认 `wd_interval=50`（`paper.md:336-342`）。

代码证据需要谨慎表述。SIMBA 本地代码确实设置了 PyTorch-BigGraph 参数，例如 `dimension=50`、`loss_fn='softmax'`、`eval_fraction=0.05`、`wd_interval=50`，并通过 `pbg_train` 自动估计 weight decay、转换图文件、调用 `torchbiggraph.train`（`simba/simba/_settings.py:115-153`, `simba/simba/tools/_pbg.py:549-646`）。但是具体 loss 和负采样执行在 PyTorch-BigGraph 内部，不是 SIMBA 本地源码里的一个函数体。因此，代码匹配应标为 Partial，而不是说 SIMBA 仓库自己完整实现了论文里的 sampler。

还有一个细节：论文说每条边产生 100 个 uniform negatives 和 100 个 degree-proportional negatives（`paper.md:333-333`），但当前代码默认是 `num_batch_negs=50` 和 `num_uniform_negs=50`（`simba/simba/_settings.py:133-148`）。如果论文实验使用了额外配置覆盖，当前 `code source` 没有直接证明。

### 第四步：Softmax transformation

PBG 训练得到的是初始 embedding。论文认为不同实体类型的 embedding 可能在不同 manifold 上，所以需要用细胞作为 reference，对 feature 或 query 进行 Softmax transformation（`paper.md:361-365`）。

论文先定义 cell \(c_i\) 和 feature \(f_j\) 之间的边概率正比于点积指数：

$$P\left({e}_&#123;&#123;c}_{i},\,{f}_{j}}\right)\propto {\rm{exp}}\left(\bf&#123;&#123;v}_&#123;&#123;c}_{i}}}\cdot \bf&#123;&#123;v}_&#123;&#123;f}_{j}}}\right)$$

对某个 feature \(f_j\)，所有 cell 上的概率分布是：

$${p}_&#123;&#123;c}_{i},\,{f}_{j}}=\frac{\exp (\mathbf&#123;&#123;v}_&#123;&#123;c}_{i}}}\cdot \mathbf&#123;&#123;v}_&#123;&#123;f}_{j}}})}&#123;&#123;\sum }_{k=1}^{n}\exp (\mathbf&#123;&#123;v}_&#123;&#123;c}_{k}}}\cdot \mathbf&#123;&#123;v}_&#123;&#123;f}_{j}}})}$$

然后用这些概率加权 cell embedding，得到新的 feature embedding：

$$&#123;&#123;\hat{\mathbf{v}}}_&#123;&#123;f}_{j}}}=\frac{\mathop{\sum }\nolimits_{i=1}^{n}{p}_&#123;&#123;c}_{i},\,{f}_{j}}^&#123;&#123;T}^{-1}}\mathbf&#123;&#123;v}_&#123;&#123;c}_{i}}}}{\mathop{\sum }\nolimits_{i=1}^{n}{p}_&#123;&#123;c}_{i},\,{f}_{j}}^&#123;&#123;T}^{-1}}}$$

论文所有分析中 \(T=0.5\)（`paper.md:367-388`）。

代码中的 `softmax` 计算 reference-query 点积、做温度缩放 Softmax、阈值过滤低概率项、重新归一化，并把加权后的 query embedding 写入 `adata_query.layers['softmax']`（`simba/simba/tools/_post_training.py:14-59`）。`embed` 再把 reference 和转换后的 query 拼成一个共同 AnnData（`simba/simba/tools/_post_training.py:62-241`）。

### 第五步：解释 embedding

SIMBA 的解释方式有两类。

第一类是 feature specificity metrics。论文为每个 feature 计算相对于所有 cell 的概率分布或点积分布，然后定义 max、Gini、standard deviation、entropy 等指标（`paper.md:391-430`）。代码中 `compare_entities` 计算 dot product、normalized dot product、softmax probability、top-50 max、std、Gini 和 entropy（`simba/simba/tools/_post_training.py:244-306`）。

第二类是把 SIMBA embedding 当成实体数据库做邻居查询。论文用 k-d tree 查找某个 cell 或 feature 的近邻，并可以限制查询实体类型（`paper.md:439-442`）。代码中 `query` 用 `KDTree` 实现 KNN 或 radius search，并支持 `anno_filter`/`filters` 做类型过滤（`simba/simba/tools/_post_training.py:309-467`）。

### 调控因子和靶基因推断

论文把 master regulator 定义为 TF gene 和 TF motif 都有细胞类型特异性，并且两者在 SIMBA 空间中接近。实现上，先计算 TF motif 到所有 gene 的距离，再看对应 TF gene 在所有 gene 中的 rank（`paper.md:445-449`）。代码 `find_master_regulators` 实现了 motif/gene 列表检查、可选 metrics 合并、motif-gene 距离、rank 计算和阈值过滤（`simba/simba/tools/_post_training.py:470-614`）。

靶基因推断的假设是：候选 target gene 要同时靠近 TF motif 和 TF gene；同时候选基因附近的 peak 也要靠近 TF motif 和 target gene（`paper.md:451-463`）。代码 `find_target_genes` 先从 TF motif 和 TF gene 的近邻 gene 取候选集合，再要求候选 gene 附近 peak 包含该 motif，最后按 gene-to-motif、gene-to-TF-gene、peak-to-motif、peak-to-gene 的 rank 过滤和排序（`simba/simba/tools/_post_training.py:617-846`）。

### 结果怎么理解？

主要图像证据支持这样一个故事：

- Fig. 1 是框架图：同一个图嵌入流程适配 RNA、ATAC、多模态、批次校正和多组学整合。
- Fig. 2 显示 RNA PBMC 数据中，SIMBA 能把细胞和 marker genes 放在同一个空间里，并用 barcode plot 和 max/Gini 指标支持 marker 排名。
- Fig. 3 显示 ATAC 数据中，peak、motif、k-mer 可以和 cell 一起嵌入；GATA1/GATAAG/KLF1 例子展示了序列特征和细胞类型的联系。
- Fig. 4 显示 SHARE-seq 多模态数据中，SIMBA 可同时放置细胞、gene、motif、peak，并进一步做 master regulator 和 target gene 分析。
- Fig. 5 显示 batch correction：raw embedding 受 batch 影响，SIMBA 后不同 batch 混合而 cell type 结构保留。
- Fig. 6 显示 RNA/ATAC 跨模态整合：raw RNA 和 ATAC 按模态分开，SIMBA 后模态混合并保留 cluster 结构。

### 复现时要注意什么？

代码-论文匹配总体较高，但要分清三层：

1. **SIMBA 包本身**：当前 `code source` 对构图、PBG 调用、edge inference、gene scores、Softmax、metrics、query、regulator/target gene 工具支持充分。
2. **PBG 内部训练行为**：loss、sampler、held-out metric 生成由 PyTorch-BigGraph 执行，SIMBA 本地源码主要负责配置和调用。
3. **论文 benchmark**：比较实验脚本在外部 `simba_comparison` 仓库，论文和 README 都这样说明（`paper.md:511-511`, `README.md:12-14`）。

此外，论文 Methods 描述的 null-node significance 和 `fix` operator 流程，在当前 `master` 代码快照中没有找到本地实现（`paper.md:433-436`）。这不影响主包的图嵌入流程，但会影响完整复现论文中特征显著性分析的能力。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SIMBA Summary

SIMBA (single-cell embedding along with features) is a graph-embedding method for representing cells and biological features in the same latent space. Instead of learning only a cell embedding and then clustering cells to interpret markers, SIMBA makes cells, genes, peaks, TF motifs, k-mers, and optional cross-dataset cell links into typed graph nodes and edges, then embeds all entities together (`paper.md:27-33`, `paper.md:42-59`).

### Problem

The paper targets two linked problems in single-cell analysis. First, many pipelines are cluster-centric: marker discovery depends on the chosen clustering resolution and algorithm (`paper.md:21-24`). Second, different tasks such as scRNA-seq analysis, scATAC-seq analysis, multimodal analysis, batch correction, and multi-omics integration are usually formulated with different tools and assumptions, even though they all involve relationships between cells and measured features (`paper.md:24-30`).

SIMBA's answer is a unified graph representation: change the graph inputs for each task, but reuse the graph embedding, Softmax transformation, metric calculation, and neighbor-query machinery.

### Method in One Pass

1. Preprocess single-cell matrices. RNA expression is normalized/log-transformed and discretized into expression levels; ATAC peaks are binarized; motif/k-mer matrices can be generated from peak sequences (`paper.md:237-249`, `paper.md:258-268`).
2. Build a heterogeneous graph. Cells, genes, peaks, motifs, k-mers, and inferred cell-cell links become nodes/edges with relation-specific weights (`paper.md:252-306`).
3. Train graph embeddings with PyTorch-BigGraph. The paper uses a dot-product link-prediction objective with type-constrained negatives and L2 regularization (`paper.md:312-345`).
4. Apply Softmax transformation so entities of different types are comparable in a reference-cell space (`paper.md:361-388`).
5. Use the shared embedding for feature metrics, nearest-neighbor queries, marker discovery, batch-corrected interpretation, multimodal feature interpretation, master-regulator ranking, and target-gene inference (`paper.md:391-463`).

Code evidence matches the package-level workflow well: `discretize`, `gen_graph`, `infer_edges`, `gene_scores`, `softmax`/`embed`, `compare_entities`, `query`, `find_master_regulators`, and `find_target_genes` are all present in the checked `simba` source (`doc_code.md`).

### Main Results

- **Framework overview:** Fig. 1 shows the common graph-to-embedding template across scRNA-seq, scATAC-seq, multimodal analysis, batch correction, and multi-omics integration (`paper.md:48-59`; `figure_analysis.md`).
- **scRNA-seq PBMCs:** SIMBA separates PBMC cell types, places marker genes near expected cell groups, and ranks genes by max/Gini metrics without requiring clustering as the first interpretive step (`paper.md:65-88`).
- **scATAC-seq hematopoiesis:** SIMBA embeds cells together with peaks, TF motifs, and k-mers; the examples highlight GATA-related sequence features and KLF1-region peaks near MEP cells (`paper.md:94-123`).
- **SHARE-seq multimodal analysis:** SIMBA combines RNA, ATAC, motif, k-mer, and peak information, recovers hair-follicle differentiation features, and supports master-regulator/target-gene analyses such as Lef1 and Hoxc13 (`paper.md:129-149`).
- **Batch correction:** SIMBA uses inferred cross-batch cell-cell links to mix batches while preserving cell-type structure and marker-gene interpretation (`paper.md:161-181`).
- **Multi-omics integration:** SIMBA integrates separately profiled RNA and ATAC cells using gene scores and inferred cross-modality links, while keeping cells and features available in one embedding (`paper.md:190-210`).

### Code-Paper Match

Overall code-paper fidelity is **high** for the package workflow. The checked repo implements graph construction, RNA discretization, motif/k-mer scanning helper, edge inference, ATAC gene scores, Softmax embedding, metrics, queries, master-regulator ranking, and target-gene ranking (`doc_code.md`).

Important caveats:

- The exact PBG loss and sampler are not implemented as SIMBA-local Python functions; SIMBA configures PyTorch-BigGraph and delegates training to upstream PBG (`simba/simba/tools/_pbg.py:622-646`).
- The paper says 100 uniform and 100 degree-proportional negatives; the checked default config sets 50 and 50 (`simba/simba/_settings.py:133-148`). Experiment-specific overrides were not verified in this `code source`.
- The null-node/fix-operator significance workflow described in Methods was not found in the checked `master` source tree (`paper.md:433-436`; `doc_code.md`).
- Benchmark scripts are intentionally external: the paper and repo point to `pinellolab/simba_comparison` for comparison analyses (`paper.md:511-511`, `README.md:12-14`).

### Reproducibility Notes

The paper reports that datasets are curated in the SIMBA package and deposited at Zenodo, with source-data spreadsheets for main figures (`paper.md:499-505`, `paper.md:654-678`). The code availability section gives the Bioconda/GitHub package, documentation/tutorial site, external comparison scripts, and Zenodo snapshot for the analyzed version (`paper.md:508-511`).

Practical reproduction should separate three layers:

- **Package workflow reproduction:** use the checked `simba` package for preprocessing, graph building, PBG training, embedding, metrics, and queries.
- **Paper figure/result reproduction:** use the paper's datasets/source data and tutorials; figures depend on dataset curation and plotting choices not fully represented by the package functions alone.
- **Benchmark reproduction:** fetch `simba_comparison`; it is outside this workspace's `code source`.

The main unresolved implementation evidence is PBG-internal training behavior and the null-node significance procedure, not the core SIMBA graph/embedding/post-training package workflow.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
