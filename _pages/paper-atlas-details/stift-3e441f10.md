---
layout: default
permalink: /paper-atlas/stift-3e441f10/
title: "STIFT"
nav: false
wide: true
description: "STIFT 不把不同发育时间点只当作需要消除的 batches。它先用 DeST-OT 在每对相邻时间切片之间估计软匹配，把高概率匹配转成跨时间图边，再与每张切片内部的空间 KNN 图合并；最后用 graph attention autoencoder 重构表达，并用跨时点“亲属”构造 triplet loss，让 embedding 同时混合批次、保留空间邻域和时间连续性。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Briefings in Bioinformatics · 2025</span>
    </div>
    <h1>STIFT</h1>
    <p>STIFT: spatiotemporal transcriptomics integration through spatially informed multi-timepoint bridging</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1093/bib/bbaf644" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for STIFT">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/cuhklinlab/STIFT" target="_blank" rel="noopener noreferrer" aria-label="Open code for STIFT">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STIFT：用相邻时间点桥接来整合时空转录组

论文：*STIFT: spatiotemporal transcriptomics integration through spatially informed multi-timepoint bridging*（Briefings in Bioinformatics, 2025；DOI: 10.1093/bib/bbaf644）

### 一句话理解

STIFT 不把不同发育时间点只当作需要消除的 batches。它先用 DeST-OT 在每对相邻时间切片之间估计软匹配，把高概率匹配转成跨时间图边，再与每张切片内部的空间 KNN 图合并；最后用 graph attention autoencoder 重构表达，并用跨时点“亲属”构造 triplet loss，让 embedding 同时混合批次、保留空间邻域和时间连续性。

这里的 parent/child 是最优传输给出的候选对应，不是 lineage tracing 直接观测的细胞亲缘；尤其不同时间切片来自破坏性采样时，同一个 spot 不可能被纵向重复测量。

### 1. 输入、输出和问题设定

输入是按真实时间排序的 AnnData list。每个 slice $\mathcal S_k$ 含：

$$
X_k\in\mathbb R^{n_k\times g},\qquad
S_k\in\mathbb R^{n_k\times d},
$$

其中 $X_k$ 是 spot×gene 表达，$S_k$ 是二维或三维坐标。`section_ids` 的顺序决定哪些 slices 被当作相邻时间；顺序错误会把不合理的样本直接连边。

主要输出是所有 spots 的 30 维 `adata_concat.obsm['STIFT']` embedding，以及由 embedding 进一步得到的 Louvain/Leiden domains、UMAP、metrics 或 trajectory。STIFT 本身没有输出真实 lineage tree，也没有建立显式基因动力学 ODE。

### 2. 预处理：论文合同与 wrapper 的差异

论文描述每个 slice 总 counts normalize 到 10,000、log1p，选择 top 10,000 HVGs 并取所有 slices 的交集，还把 spatial map 按比例归一到 $100\times100$ square。

公开 `STIFT()` wrapper 在每个 slice 上调用 `highly_variable_genes(..., n_top_genes=10000)`、`normalize_total(1e4)`、`log1p()`，再分别 subset；跨 slice 合并时才隐式处理共同特征。辅助 `preprocess_adata_list()` 默认 5,000 HVGs，tutorial 又使用其他数值。最重要的是，代码中没有找到论文所述 $100\times100$ coordinate scaling。

而 DeST-OT 的 `align()` 还会把相邻 slices 合并后再次 normalize/log/PCA（默认 `normalize_counts=True`）。若用户已经预处理过输入，必须检查是否发生重复变换。论文参数、wrapper defaults 与 tutorial 不能混成一套唯一配置。

### 3. DeST-OT 如何建立相邻时间软对应

对 $\mathcal S_k$ 与 $\mathcal S_{k+1}$，源码先取共同 genes，对合并数据做 30-PC PCA，计算：

- $C$：跨 slice expression distances；
- $C_1,C_2$：各 slice 内 expression distances；
- $D_1,D_2$：各 slice 内 spatial distances。

空间距离被按最小/最大非零距离缩放，再匹配到 expression-distance 尺度。优化器构造 fused within-slice geometry：

$$
M_1=D_1\odot C_1,\qquad M_2=D_2\odot C_2,
$$

并把跨 slice expression cost 与保持两侧内部几何的 GW-like cost 组合。当前 wrapper 参数为 `alpha=0.2, gamma=50, epsilon=0.1, max_iter=200, balanced=False`。`epsilon` 提供 entropy regularization，`gamma` 控制 semi-unbalanced mass penalty；log-domain Sinkhorn 迭代得到

$$
\Pi_{k,k+1}\in\mathbb R_+^{n_k\times n_{k+1}}.
$$

$\Pi_{ij}$ 越大，表示在所选表达/空间 cost 和正则下，早期 spot $i$ 向晚期 spot $j$ 分配的 transport mass 越大。它不是统计学意义上经过 calibration 的“$i$ 生出 $j$ 的概率”，也不一定逐行和为 1；semi-unbalanced 模式允许 mass change，以容纳增殖/凋亡和 spot 数变化。

### 4. 从软 coupling 到离散 temporal edges

对每个 $\Pi$，`get_topk_mapping()` 同时取：

- 每一行最大的 $r_t$ 个 columns：早期 spot 的 candidate children；
- 每一列最大的 $r_t$ 个 rows：晚期 spot 的 candidate parents。

论文写为

$$
T_{k,k+1}[i,j]=1
\quad\text{if }j\in\operatorname{Top}_{r_t}(\Pi_{i,:}),
$$

$$
T_{k+1,k}[j,i]=1
\quad\text{if }i\in\operatorname{Top}_{r_t}(\Pi_{:,j}).
$$

例如一行 coupling 为 `(0.05, 0.60, 0.25, 0.10)` 且 $r_t=2$，该 early spot 会连到第 2、3 个 late spots；绝对值 0.60 与 0.25 在离散图中都变成 1。top-k 因而丢弃概率幅度和不确定度，并保证低质量行也产生固定数量候选（只要矩阵尺寸允许）。

`get_family_information()` 把 index 变成 names 并写入 `children_dict`/`parents_dict`。大数据 downsampling helper 可在子样本上算 OT，再用 spatial nearest neighbor 把关系扩展到全数据；但主 `STIFT()` wrapper 没有调用该路径，论文的 $\beta=30\%$–100% 策略需要用户另行编排。

### 5. 空间图与总时空图

每个 slice 用 Euclidean coordinates 建 $r_s$-KNN 图 $A_k$，并加 self-loops。跨时点 matrices 填入 block off-diagonals：

$$
A=
\begin{pmatrix}
A_1&T_{1,2}&0&\cdots\\
T_{2,1}&A_2&T_{2,3}&\cdots\\
0&T_{3,2}&A_3&\cdots\\
\vdots&\vdots&\vdots&\ddots
\end{pmatrix}.
$$

公开 `create_ST2_adj_matrix()` 把 children blocks 及其 transpose 都写入 adjacency，因此交给 GATE 的 message-passing graph 实际上是双向/对称连接；“时间有方向”主要来自 section order 和 parent/child 选择，而 GNN 不执行只能向未来传播的有向动力学。

### 6. GATE 怎样学习 embedding

所有 spots 的 normalized expression 作为 node features，时空 adjacency 决定 neighbor messages。encoder 采用两层 graph attention，hidden dimensions 为 512 和 30。attention 将邻居特征线性变换后加权聚合；decoder 复用 encoder 的转置 weights/attention 重构原始表达 $\hat X$。

预训练只最小化

$$
\mathcal L_{rec}=\frac{1}{ng}\|X-\hat X\|_F^2,
$$

默认 `train_STIFT()` 为 500 epochs。由于 temporal edges 已在 adjacency 中，哪怕预训练没有 triplet loss，跨时点 mapping 也已经影响 embedding。

### 7. temporal triplet fine-tuning

论文公式对中间时点 anchor $i$ 同时使用一个 parent positive 和一个 child positive：

$$
\mathcal L_{tri}=\max\left[
0,\frac12(\|z_i-z^+_{parent}\|_2^2+\|z_i-z^+_{child}\|_2^2)
-\|z_i-z_i^-\|_2^2+m
\right].
$$

negative 从 anchor 同一 slice 随机选，以免简单地把“不同时间”当作负类。总目标是

$$
\mathcal L=\mathcal L_{rec}+\lambda\mathcal L_{tri}.
$$

但公开代码 `create_triplets()` 只取 family list 的第一个 parent **或** child 作为单一 positive，再用 PyTorch `TripletMarginLoss`；没有同时平均两个 positives，也使用 Euclidean norm 而不是论文显式 squared-distance 公式。因此概念一致、目标细节为 Partial match。

triplets 每 100 epochs 刷新一次；negative 是同 batch 随机 spot，可能偶然来自同一 biological domain，代码没有 hard-negative 或 label 过滤。

### 8. 默认参数存在三套口径

- 论文/补充：pretrain 500、fine-tune 通常 1000、$\lambda=0.1$、margin 1。
- `train_STIFT()`：500/1000，但 `weight_triplet=1`。
- 高层 `STIFT()`：500/2000，并未传 `weight_triplet`，所以实际继承 1。

优化器是 Adam，lr 0.001、weight decay 0.0001、gradient clipping 5、seed 666。若要按论文默认复现，必须显式传 $\lambda=0.1$ 并确认使用哪个入口；仅调用 wrapper 并不等价于 Methods 配置。

### 9. embedding 可回答什么，不能回答什么

STIFT embedding 可用于：

- 跨时间 batch mixing 与 domain clustering；
- 看空间 domains 是否随发育/再生连续变化；
- 基于候选 temporal anchors 描述 progenitor-like 到 descendant-like trajectories；
- 在二维或三维 spatial coordinates 上比较组织结构。

它不能单独证明：

- 某个 spot 的真实克隆后代；
- 特定基因调控变化的因果关系；
- transport mass 对应真实细胞数量或增殖率；
- embedding 中相邻必然代表直接时间转移。

任何 trajectory 解释都应回到原始时间 labels、空间 anatomy、marker genes，并在可能时用 lineage tracing 或独立时间数据验证。

### 10. 论文图与验证证据

- **图 1**：三模块概览——DeST-OT、spatiotemporal graph、GATE+triplet。
- **图 2（axolotl brain regeneration）**：比较 batch mixing/domain preservation，并用 EGC subtypes 展示再生时间结构。
- **图 3（mouse embryo）**：五个 Stereo-seq stages、数十万 spots，展示 scalability 和 organ-domain preservation。
- **图 4–5（3D planarian regeneration）**：比较跨时点 anchors 的 anatomy plausibility，并重建三维 domains/trajectories。
- **补充 cardiac infarction、human cortex 与 hyperparameter analyses**：支持跨平台 robustness，但公开 repo 不含完整 figure scripts 和配置，不能从当前快照一键复算。

论文的 batch entropy/iLISI/batch ASW 与 ARI/cLISI/cell-type ASW 衡量的是“混合”和“生物分离”两个方向；单独追求 batch mixing 可能抹去真实时间差，所以应成对解读。

### 11. 论文—代码对应

| 环节 | 直接源码 | 对应程度 | 边界 |
|---|---|---|---|
| 相邻时间 DeST-OT | `DESTOT.py:72-159`, `destot_opt.py:41-164` | Exact/Partial | 独立 DeST-OT 依赖；coupling 非 lineage truth |
| top-k parent/child | `STIFT.py:27-42`, `149-191` | Exact | 概率幅度被二值化 |
| 片内空间 KNN/self-loop | `STIFT.py:503-576` | Exact | 坐标 100×100 scaling 未找到 |
| block spatiotemporal graph | `STIFT.py:193-263` | Exact | message passing graph 被对称化 |
| GATE | `STALIGNER.py`, `gat_conv.py` | Exact/Partial | 本地 attention 实现来自 STAGATE/STAligner 路径 |
| reconstruction training | `train_STIFT.py:47-60` | Exact | MSE-only pretraining |
| triplet training | `train_STIFT.py:62-95`, `121-158` | Partial | 一个 positive；与论文双-positive公式不同 |
| high-level wrapper | `STIFT.py:265-308` | Partial | epochs/$\lambda$/downsampling 与论文口径不一致 |
| benchmark metrics | `metric.py` | Partial | helper 存在，完整论文 pipelines 缺失 |
| 全部主图/补图复现 | public repo | Not found | 仅 generic package 与一个 tutorial |

### 12. 实现与复现风险

- `STIFT.py` 顶部残留作者机器绝对路径；当前相对 import 可工作，但反映环境清理不完整。
- DeST-OT 默认 `use_gpu=True` 并通过 NVML 自动选 free-memory 最大 GPU；无 NVML/GPU 环境应显式 `use_gpu=False`，但高层 wrapper 把它写死为 True。
- 坐标尺度直接进入 OT 和 KNN；论文 scaling 缺失会导致不同平台 pixel/micron 尺度不可比。
- `get_topk_mapping()` 用 `argpartition`，$k$ 必须小于对应维度；极小 slices 需保护。
- main wrapper 对每 slice 分别选 HVGs，并在 OT 内重新 normalize；建议实际运行前检查最终共同 gene matrix。
- public wrapper 的 `n_epochs=2000`、triplet weight 1 与论文 1000/0.1 不同。
- 论文的大规模 benchmark、runtime/memory 与 robustness scripts 未随仓库提供，核心代码可运行不等于论文全结果可复现。

### 建议阅读顺序

先读论文图 1 和 Methods 的 DeST-OT、graph construction、GATE、triplet 四节；再读 `STIFT/STIFT.py:STIFT()` 看 orchestration，随后读 `DESTOT.py`/`destot_opt.py`、`create_ST2_adj_matrix()`、`train_STIFT.py`。最后用 axolotl、mouse embryo、planarian 图验证每种输出的生物学解释，不要从 UMAP 单独判断成功。

### 证据范围

本文基于本地论文 Markdown、主图/图注、补充文本及 GitHub 快照 commit `9d649a018ef0262e1e71f34b9d77439aaf9d0602` 的直接源码整理。本次没有下载全部原始数据、训练 STIFT 或复算论文 benchmark；对缺失脚本和 paper–code defaults 差异保留明确边界。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## STIFT Summary

### Motivation

STIFT addresses integration of spatial transcriptomics data collected across ordered developmental or regenerative time points. Existing spatial integration methods can remove batch effects across slices, but the paper argues that they often treat time as a nuisance batch rather than a biological axis. That can erase developmental structure or create biologically implausible matches, especially in 3D spatiotemporal data.

The central idea is to combine spatial structure and temporal continuity before representation learning. STIFT uses developmental spatial optimal transport to infer adjacent-time relationships, uses those relationships to build a spatiotemporal graph, and trains a graph attention autoencoder with temporal triplet learning.

### Method Overview

STIFT takes ordered AnnData-like slices with gene expression matrices and spatial coordinates. For each adjacent time-point pair, it runs DEST-OT to compute a probabilistic mapping matrix $\Pi_{k,k+1}$. Within each slice, it builds a spatial KNN graph. Between adjacent slices, it keeps top-probability parent and child links from $\Pi$ to create temporal edges.

These spatial and temporal edges are assembled into one block adjacency matrix. A GATE-style autoencoder learns embeddings from expression features on this graph. Training starts with reconstruction loss, then fine-tunes with a triplet loss that pulls likely temporal relatives together and pushes random same-slice negatives away. The final embedding is used for batch correction, spatial-domain clustering, marker interpretation, and downstream trajectory analysis.

### Evaluation

The paper evaluates STIFT on axolotl brain regeneration, mouse embryonic development, and 3D planarian regeneration, with supplementary validation on cardiac infarction and human cortical development. Across figures, STIFT is compared with methods including STAligner, STAGATE, Graspot, and SPIRAL using batch entropy, iLISI, batch ASW, ARI, cLISI, and cell-type ASW.

The strongest evidence is that STIFT often balances batch mixing with biological separation better than baselines. In axolotl, it preserves EGC subtypes and supports a regeneration trajectory. In mouse embryo data, it scales to hundreds of thousands of spots and preserves organ domains. In planarian 3D regeneration, spatiotemporally guided anchors look more anatomically plausible than expression-only anchors.

### Code Match And Reproducibility

The public code implements the core algorithm: DEST-OT, top-k temporal links, spatial KNN graph construction, global spatiotemporal adjacency, GATE training, triplet loss, and metric helpers. The overall code-paper match is medium-high.

Important caveats remain. The repository does not include full scripts for the manuscript's benchmark figures, runtime/memory analysis, hyperparameter grid, or supplementary robustness datasets. The public implementation also differs from the paper in several details: coordinate normalization to a $100 \times 100$ square is not found, the triplet implementation uses one positive rather than the paper's two-positive formulation, and the public triplet-weight default is `1` rather than the supplementary default $\lambda=0.1$.

### Reproducibility Rating

**3/5.** The core method is available and readable, but full figure-level reproduction would require additional data-processing and benchmark scripts not present in the public repository. Users should explicitly set preprocessing, epoch counts, temporal top-k, and triplet weight rather than relying on mixed defaults from the wrapper and tutorial.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
