---
layout: default
permalink: /paper-atlas/tracer-ae610f3b/
title: "TRACER"
nav: false
description: "Xenium、MERFISH 等成像型空间转录组直接给出每条 RNA 的基因名和三维坐标。常规流程先从核染色或膜染色得到二维细胞边界，再把落在边界内的转录本归给该细胞。但组织切片有厚度：一个核可能在当前焦平面内，邻近细胞的核却在平面外；两者的胞质和 RNA 在三维空间仍可能重叠。二维边界于是会把不同细胞的 RNA 混到一起，也会留下没有任何检测核可归属的 RNA。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>TRACER</h1>
    <p>Reconstructing biologically coherent cellular profiles from imaging-based spatial transcriptomics</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2026.03.08.710395" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TRACER 方法解读：用转录一致性修正空间转录组的细胞边界

### 1. 问题不是“找出细胞核”，而是“把每条转录本归给谁”

Xenium、MERFISH 等成像型空间转录组直接给出每条 RNA 的基因名和三维坐标。常规流程先从核染色或膜染色得到二维细胞边界，再把落在边界内的转录本归给该细胞。但组织切片有厚度：一个核可能在当前焦平面内，邻近细胞的核却在平面外；两者的胞质和 RNA 在三维空间仍可能重叠。二维边界于是会把不同细胞的 RNA 混到一起，也会留下没有任何检测核可归属的 RNA。

TRACER（Tissue Reconstruction via Associative Clique Extraction and Relation-mapping）不重新训练图像分割模型，而是在已有分割之后修正“转录本—细胞”关系。它利用数据内部学到的基因—基因共现一致性和转录本空间邻近性：先把不符合当前细胞主表达程序的 RNA 分离出来，再从未分配 RNA 中寻找可能的细胞片段，最后只合并空间靠近且转录程序兼容的片段。

因此 TRACER 的输入是转录本级表格，不是原始显微图像；输出仍是每条转录本的细胞 ID，以及 whole cell、partial cell、reconstructed partial cell 等实体标签。它是 reference-free、training-free 的后处理框架，不需要细胞类型注释或参考图谱。

### 2. 核心类比：细胞像文档，基因像词

TRACER 从自然语言处理中借用 normalized pointwise mutual information（NPMI）。在文本中，一篇文档定义上下文，一个词是否出现是二元事件；在 TRACER 中，一个可信细胞核定义上下文，一个基因是否达到最低检测数是二元事件。

设共有 $C$ 个可信核，$M_{cg}=1$ 表示基因 $g$ 在核 $c$ 中至少出现 $N_{\min}$ 次，否则为 0。代码默认 $N_{\min}=2$，用 presence/absence 而不是原始计数：

$$
P(i)=\frac{1}{C}\sum_c M_{ci},\qquad
P(i,j)=\frac{1}{C}\sum_c M_{ci}M_{cj}.
$$

点互信息与归一化形式为

$$
PMI(i,j)=\log\frac{P(i,j)}{P(i)P(j)},
$$

$$
NPMI(i,j)=\frac{PMI(i,j)}{-\log P(i,j)}\in[-1,1].
$$

正值表示两个基因在核内共同出现得比独立假设更频繁；负值表示共同出现被抑制，可能代表互斥谱系程序；接近 0 表示近似独立。代码对没有观察到共同出现的组合默认保留为 NaN，也可在两个边缘概率都足够大时设为 $-1$。NaN 是“证据未知”，不应等同于 0 的“观察上独立”。

一个小例子：100 个可信核中，基因 A 出现在 40 个，B 出现在 30 个，两者共同出现在 24 个。则 $P(A)=0.4$、$P(B)=0.3$、$P(A,B)=0.24$；独立预期只有 0.12，因此 $PMI=\log 2>0$，A 与 B 对同一细胞程序提供相互支持。

### 3. 为什么只用“可信核”估计 NPMI

如果用已经混杂的整细胞作为上下文，错误边界会反过来污染基因关联。论文和代码先保留 Xenium `qv>=30` 的转录本，再选择 `overlaps_nucleus==1` 的核内转录本；对 Xenium 还排除转录数最低和最高 20% 的核，用中间 20–80% 分位减少低信号与异常大核的影响。MERFISH 使用原研究提供的高核概率转录本。

这不是说核内表达等同于全细胞表达，而是把核作为相对可靠的“上下文窗口”，先学习数据集内部的共现结构，再将该结构用于全体转录本。不同 panel、组织和检测技术需要各自估计 NPMI，不能把某个乳腺癌矩阵无条件移植到另一个平台。

### 4. 五阶段修正流程

#### 4.1 阶段 1：两遍保守剪枝

对初始分割中的每个细胞，TRACER 收集其基因集合，查看每个基因与其他基因之间低于阈值的 NPMI 边。代码默认阈值为 $-0.1$，迭代删除负边最多的基因，直到剩余基因内部不再有超阈值冲突。

第一遍被分离的转录本不直接丢弃，而是赋予 `cellID-1`，形成该 whole cell 的候选 partial cell。第二遍再次检查这些 partial 集合；仍不一致的基因才转成 unassigned。两遍设计体现“保守”：先从原细胞剥离可疑成分，再要求剥离成分自身形成一致程序。

注意剪枝单位是基因：若某个基因被判为不一致，该细胞内该基因的所有对应转录本都会一起移动。它不是逐 RNA 估计来源概率。

#### 4.2 阶段 2：重建未分配片段

TRACER 对 unassigned 转录本在 $(x,y,z)$ 空间构建 kNN 图，并按距离阈值切断过远边。图的连通分量是候选片段；小分量被过滤，其余分量再接受同样的 NPMI 一致性剪枝。保留下来的 coherent component 被标记为 reconstructed partial cell 候选。

这一步解决“核不在切片平面但 RNA 仍在”的情况。它只能说某个空间 RNA 簇像一个一致的细胞片段，不能证明完整细胞边界或真实核位置。

#### 4.3 阶段 3：按 $\Delta C$ 分层拼接

每个 whole、partial 或 component 都用中心坐标和基因集合表示。Delaunay 三角化给出空间邻居候选；算法只评估这些局部边，避免任意远距离合并。

对基因集合 $G$，论文定义 purity 为正 NPMI 支持，conflict 为负 NPMI 惩罚，并令

$$
C(G)=\operatorname{purity}(G)-\operatorname{conflict}(G).
$$

若要合并两个实体 $U,V$，计算

$$
\Delta C=C(G_U\cup G_V)-\max\{C(G_U),C(G_V)\},
$$

或加入偏好更简单解释的 $1/n$ 惩罚。$\Delta C\ge0$ 才进入候选。代码以最大堆优先处理最高增益，用 Union-Find 维护动态簇，并在每次弹出候选时重新计算，防止旧边状态失效。另有硬约束：两个已经包含真实 whole cell 的簇不能互相合并；partial/component 可以附着到 whole cell。最终标签优先级为 cell > partial > component。

#### 4.4 阶段 4：空间连通性细化

转录一致不代表空间上合理。拼接后，代码在全部转录本上构建空间图，检查同一实体内是否出现互不连通的分量；最大分量保留原标签，其余分量加 `-2`、`-3` 等后缀分开。这会去掉仅靠相似表达程序跨空间“遥接”的片段。

#### 4.5 阶段 5：再次拼接

空间拆分后的实体再次进入 $\Delta C$ 拼接，使被拆出的片段有机会与更近、更一致的实体重新组合。论文把阶段 3 输出称为 TRACER-stitched，把经过空间约束和再次拼接的最终输出称为 TRACER-fine-tuned。

### 5. purity、conflict 和 signal strength 怎样读

论文的原始 purity 可理解为超过正阈值 $\theta$ 的基因对比例；conflict 是负 NPMI 绝对值相对所有可能基因对数 $K=\binom{k}{2}$ 的归一化和。对弱关联更稳健的版本使用对称 ReLU dead zone：

$$
R_\tau(w)=
\begin{cases}
w-\tau,&w>\tau,\\
0,&|w|\le\tau,\\
w+\tau,&w<-\tau.
\end{cases}
$$

代码默认 $\tau=0.05$。正信号和与负信号和分别给出 ReLU purity/conflict；两者绝对值之和是 signal strength；相对比例给出 relative purity/conflict。高 purity、低 conflict 表示基因集合内部更相容，但小 panel 或低信号细胞可能在“没有足够证据”时也显得冲突低，因此必须联合 signal strength 和转录本数解释。

这里存在一个直接代码差异：`metrics.py` 的评估 conflict 按总可能基因对 $K$ 归一化，与论文一致；`core.py` 中非 ReLU 的拼接 coherence 对负项使用负对数目的均值。也就是说展示指标与某条非 ReLU 拼接路径并非完全相同参数化。ReLU 路径在两处都按 $K$ 归一化，复现时必须记录 `use_relu`、$\theta$、$\tau$ 和阈值。

### 6. 三类输出实体的生物含义

- whole cell：包含当前平面中可信核的主要细胞实体；
- partial cell：从某个 whole cell 中剥离出的转录一致片段，可能来自平面外邻近细胞；
- reconstructed partial cell：由原本 unassigned 的空间一致 RNA 分量重建的候选片段。

“partial”是算法和几何解释，不是由真实三维膜边界直接证实的细胞类型。TRACER 允许不同实体的凸包局部重叠，意在表达切片厚度下的三维交叠；它不输出一个互斥覆盖整张二维图像的传统语义分割掩膜。

### 7. 论文图的证据链

- 图 1：用切片几何说明 whole/partial/missed cell，并给出从 NPMI、剪枝、component 到拼接的完整流程。
- 图 2：乳腺癌 Xenium 的 NPMI 块结构，以及 purity/conflict 在 UMAP 和分布上的表现。
- 图 3：肺癌 Xenium 中 multimodal、核扩张、TRACER-stitched 与 fine-tuned 的凸包、UMAP 和 marker 对比。
- 图 4：partial cell 的 3D 几何、基因频率与 whole cell 的谱系分离。
- 图 5：混合谱系/双细胞样 profile 的拆解，以及 ligand–receptor 假阳性减少。
- 图 6：与 3D membrane-guided Baysor 分割的定量比较和跨平台评估。

嵌入在同一 48 页 PDF/Markdown 后半部的补充材料包含 3D 仿真、额外 Xenium/MERFISH 结果、Scrublet 稳健性、coherence 指标、凸包和运行时表。主文报告在 17 CPU、96 GB 申请内存的作业中，约 2800 万条乳腺癌 Xenium 转录本耗时约 5.2 小时、峰值约 27 GiB；140 万和 80 万转录本数据低于 7 分钟和 2 分钟。这里的速度来自特定硬件、参数和 Cython/并行路径，不是所有环境的保证。

### 8. 下游改善能说明什么

论文在乳腺癌、肺癌 Xenium 和小鼠回肠 MERFISH 上展示：TRACER 后的 UMAP 簇更分离，marker 跨谱系污染减少，purity 上升、conflict 下降，Scrublet doublet score 更低；混合 tumor–T cell profile 可拆成更明确的成分；去除混杂后，一些 segmentation-derived ligand–receptor interaction 消失。

这些结果支持“转录本归属会改变下游结论”，但也存在循环验证风险：TRACER本身以基因一致性优化，再用基因一致性指标评价必然有一定优势。因此论文还用原研究标签、3D 几何、Scrublet、marker 特异性和 3D membrane-guided 分割作旁证。即便如此，没有普适真实三维细胞边界，partial cell 的真实性仍主要由多种间接证据共同支持。

### 9. 代码证据与复现边界

本地 `tracer_code` 是无独立 Git 元数据的源码快照；项目元数据指向 `https://github.com/imlong4real/TRACER`，但无法从该目录确认精确提交。因此代码出处记为 `local_dir`，不能伪造 commit。

| 机制 | 本地证据 | 状态 |
|---|---|---|
| 核内二元 NPMI | `metrics.py:45-230` | Exact |
| 两遍基因剪枝 | `core.py:151-558` | Exact |
| unassigned 空间 component | `core.py:628-693,898-1100` | Exact |
| Delaunay + DSU + heap 的 $\Delta C$ 拼接 | `core.py:1187-1603` | Exact |
| 空间连通性拆分 | `core.py:2025-2163` | Exact |
| conflict 归一化 | `metrics.py` 与 `core.py` | Discrepancy，路径依赖 |

教程脚本给出乳腺癌、肺癌、黑色素瘤和小鼠回肠流程，但运行依赖另行下载的大型数据。当前恢复验证了源码映射，没有重跑 2800 万条转录本的完整分析。

### 10. 使用时最重要的边界

1. NPMI 受 panel、样本量和核选择影响；稀有基因对尤其不稳定。
2. 基因 presence 阈值、负 NPMI 阈值、空间 kNN/距离和最小 component 大小都会改变输出。
3. NaN、0 和负 NPMI 含义不同，不能统一填零后不记录。
4. 不能用 TRACER 结果反过来当作独立真值证明 TRACER 正确。
5. partial cell 是具有空间和转录一致性的候选三维片段，不是直接成像的完整细胞。
6. 强真实过渡状态可能同时表达多个谱系程序，过强 coherence 剪枝有抹平生物连续性的风险。
7. 应同时保留上游 cell ID、每阶段 ID、实体类型、purity/conflict/signal strength 与参数，便于审计。

简而言之，TRACER 把细胞分割后的修正问题转化为“局部空间中哪些基因集合彼此支持”。NPMI 提供数据内生的生物一致性，空间图限制几何可能性，$\Delta C$ 决定是否拼接。它最有价值的地方是保守地保留、拆分和重组转录本，而不是强迫每条 RNA 进入一个互斥二维细胞；它最大的解释边界也正来自这里：一致的候选三维片段仍需要独立形态或实验依据验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TRACER: Reconstructing Biologically Coherent Cellular Profiles from Imaging-Based Spatial Transcriptomics

### Paper Information

| Field | Details |
|-------|---------|
| **Title** | Reconstructing biologically coherent cellular profiles from imaging-based spatial transcriptomics |
| **Authors** | Long Yuan, Youyun (Peter) Zheng, Shuming Zhang, Rameen Beroukhim, Atul Deshpande |
| **Affiliations** | Johns Hopkins University (Immunology, Computer Science, Bloomberg-Kimmel Institute, ECE, Data Science & AI Institute); Dana-Farber Cancer Institute; Harvard Medical School; Broad Institute of MIT and Harvard |
| **Journal** | bioRxiv preprint (2026) |
| **DOI** | 10.64898/2026.03.08.710395 |
| **GitHub** | https://github.com/imlong4real/TRACER |
| **License** | Apache License 2.0 |

---

### 1. Motivation and Problem Statement

#### The Segmentation Problem in Imaging-Based Spatial Transcriptomics

Imaging-based spatial transcriptomics platforms (Xenium, MERFISH) acquire transcripts from tissue sections with non-negligible thickness (typically 5--10 $\mu$m). Standard 2D segmentation methods apply nuclear staining or membrane markers to assign transcripts to cells, but this creates two systematic errors:

1. **Mixed cellular profiles from boundary overlap**: Cells located above or below the imaging plane partially intersect the section, causing transcripts from different cells to project into the same 2D footprint. The resulting "hybrid" profiles contain markers from multiple lineages (e.g., T cell + tumor markers in a single cell).

2. **Missed partial cells with out-of-plane nuclei**: Cells whose nuclei are not captured in-plane leave their cytoplasmic transcripts either unassigned or incorrectly attributed to neighboring cells. These transcripts are typically discarded as noise.

These segmentation errors propagate directly into downstream analyses: cell typing produces spurious hybrid clusters (e.g., "stromal-T cell hybrids"), ligand-receptor inference yields biologically implausible interactions (e.g., DCIS tumor cells falsely expressing CD80, CD8A, CD8B), and spatial niche characterization becomes unreliable. Recent work by Mitchel et al. (*Nat Genet* **58**(2), 434--444, 2026; ref [18]) demonstrated that segmentation-induced transcript admixture dominates downstream analyses in imaging-based spatial transcriptomics.

#### Limitations of Existing Approaches

Existing computational methods for addressing segmentation errors include:

- **Baysor** (Petukhov et al., *Nat Biotechnol*, 2022): Bayesian segmentation using prior distributions over cell shapes, optionally guided by 3D membrane priors
- **SCS** (Littman et al., *Nat Methods*, 2023): Joint optimization of segmentation and cell typing
- **BIDCell** (Fu et al., *Nat Comm*, 2024): Deep learning-based cell instance segmentation
- **fastreseg** (Wu et al., *Sci Rep*, 2025): Fast transcript reassignment heuristic
- **Bering** (Jin et al., *Nat Comm*, 2025): Graph neural network approach
- **Segger** (Heidari et al., *bioRxiv*, 2025): Contrastive learning framework

These approaches require training, external references, or substantial computational resources (GPUs). Furthermore, no gold standard exists for evaluating segmentation quality in imaging-based spatial transcriptomics (Plummer et al., *Nat Biotechnol*, 2025), and geometric overlap metrics from natural image segmentation do not translate to the fuzzy, functionally defined boundaries of biological cells.

#### TRACER's Unique Contributions

1. **Reference-free, deterministic, training-free approach** using NPMI (from NLP) for gene-gene coherence scoring
2. **Coherence-based evaluation metrics** (purity, conflict) for platform-agnostic segmentation quality assessment
3. **Recovery of partial cells** from unassigned transcripts, treating them as biologically meaningful rather than noise
4. **3D-aware cellular reconstruction** via hierarchical stitching with $\Delta C$ optimization

---

### 2. Method Overview

TRACER (Tissue Reconstruction via Associative Clique Extraction and Relation-mapping) is a 5-stage pipeline that refines cellular representations using gene-gene coherence and spatial co-localization, without requiring external annotations, supervised training, or GPU acceleration.

#### 2.1 Core Innovation: NLP-to-Spatial-Transcriptomics Analogy

TRACER draws an analogy between natural language processing and spatial transcriptomics:

| NLP Concept | Spatial Transcriptomics Analog |
|-------------|-------------------------------|
| Document (context) | Segmented nucleus |
| Word (token) | Gene |
| Event $i$ | Gene $i$ is present in the nucleus |
| Event $(i,j)$ | Both genes $i$ and $j$ are present in the same nucleus |

This formulation uses binary presence/absence (not transcript counts), making it robust to technical noise and count-level artifacts.

#### 2.2 NPMI Computation

Each segmented nucleus is treated as a context window. A gene is considered present if at least $N_{\min} = 2$ transcripts are detected inside the nuclear boundary, yielding a binary matrix:

$$M \in \{0, 1\}^{C \times G}$$

where $C$ is the number of nuclei and $G$ is the number of genes.

For each gene pair $(i, j)$, marginal and joint probabilities are estimated as:

$$P(i) = \frac{1}{C} \sum_{c=1}^{C} \mathbb{I}(M_{c,i} = 1)$$

$$P(i,j) = \frac{1}{C} \sum_{c=1}^{C} \mathbb{I}(M_{c,i} = 1 \wedge M_{c,j} = 1)$$

Pointwise mutual information is computed as:

$$PMI(i,j) = \log_2 \left( \frac{P(i,j)}{P(i)P(j)} \right)$$

Normalized PMI corrects for bias toward rare events:

$$NPMI(i,j) = \frac{PMI(i,j)}{-\log_2 P(i,j)} \in [-1, 1]$$

- $NPMI = 0$: statistical independence
- $NPMI > 0$: enriched co-expression (same lineage)
- $NPMI < 0$: depletion / mutual exclusivity (cross-lineage)

Nuclei (rather than whole-cell segments) are used as contexts because nuclear segmentation is more reliable across platforms. For Xenium datasets, nuclei in the central distribution of transcript counts (excluding lowest and highest 20th percentiles) are used; for MERFISH, all nuclei are used.

#### 2.3 Pipeline Stages

##### Stage 1: Conservative NPMI Pruning (Two-Pass Greedy Pruning)

For each segmented cell, genes are evaluated against the precomputed NPMI matrix:

- **Pass 1**: Iteratively remove the gene with the largest number of NPMI < $\theta$ edges (default $\theta = -0.1$) until no incoherent gene pairs remain. Removed genes are reassigned to a "partial cell" identifier (e.g., `cellID-1`). This separates the core coherent gene program from potentially contaminating transcripts.

- **Pass 2**: Apply the same greedy pruning to the partial cell gene sets. Genes failing coherence a second time are marked as unassigned (not forced into any entity).

Implementation detail: The greedy pruning algorithm (`prune_genes_by_npmi_greedy`) builds a sub-matrix of NPMI values for genes within a cell, identifies pairs below the threshold, and iteratively removes the gene with the most incoherent edges. A Cython-accelerated version (`_cy_prune`) is used when available for performance.

##### Stage 2: Unassigned Component Annotation

Transcripts remaining unassigned after Stage 1 (plus originally unassigned transcripts) are processed:

1. **3D kNN graph construction**: Transcripts are embedded in 3D physical space as nodes. Edges connect mutual nearest neighbors within a Euclidean distance threshold (default $k=8$, distance $\leq 1.5\;\mu$m).
2. **Connected component detection**: Extract connected components from the graph.
3. **Size filtering**: Components with fewer than `min_comp_size` transcripts (default 25--50) are discarded.
4. **NPMI pruning per component**: For retained components, apply the same greedy NPMI pruning. Components with internally consistent gene programs are labeled as "reconstructed partial cells."

##### Stage 3: Hierarchical Stitching ($\Delta C$-Based Merging)

Fragmented cellular entities (whole cells, partial cells, reconstructed partial cells) are selectively merged:

1. **Delaunay triangulation** of entity centroids in 3D defines candidate merge pairs (spatial neighbors).
2. **Coherence score** for entity with gene set $G = \{g_1, \ldots, g_k\}$:

$$C(G) = \text{purity}(G) - \text{conflict}(G)$$

where:

$$\text{purity}(G) = \frac{1}{|P|} \sum_{(i,j) \in P} \mathbb{I}(w_{ij} > \theta)$$

$$\text{conflict}(G) = \frac{1}{K} \sum_{(i,j) \in N} (-w_{ij})$$

with $P$ = observed gene pairs with finite NPMI, $N \subseteq P$ = pairs with negative NPMI, $\theta = 0.05$ (noise floor), and $K = \binom{k}{2}$.

3. **Merge criterion** with simplicity penalty:

$$\Delta C = \left(C(G_U \cup G_V) - \frac{1}{|G_U| + |G_V|}\right) - \max\left(C(G_U) - \frac{1}{|G_U|},\; C(G_V) - \frac{1}{|G_V|}\right)$$

Merges are accepted only when $\Delta C \geq 0$. The simplicity penalty $\frac{1}{|G|}$ discourages trivial merges driven by small gene sets.

4. **Constraint**: Two clusters that both contain a whole cell are never merged (prevents merging two distinct cells).
5. **Union-Find (DSU)** data structure with rank-based union and path compression drives greedy merging via a max-heap prioritized by $\Delta C$.
6. **Label assignment priority**: cell > partial > component (deterministic via lexicographic sorting).

The output of this stage is called **TRACER-stitched**.

##### Stage 4: Spatial Coherence Enforcement

After stitching, each entity's transcripts may be spatially disconnected. This stage:

1. Builds a kNN graph on all transcripts within each entity.
2. Detects connected components constrained by entity labels.
3. Splits entities whose transcripts form multiple disconnected spatial components, retaining only the largest connected component under the original label.

This eliminates spatially inconsistent outliers while preserving the dominant transcriptional program.

##### Stage 5: Final Stitching

Repeats the Stage 3 hierarchical stitching on the spatially coherent entities from Stage 4. This fine-tuning pass captures merges that become possible after spatial cleanup.

The output of this stage is called **TRACER-fine-tuned**.

#### 2.4 ReLU-Based Coherence Formulation

For benchmarking (not for the pruning/stitching pipeline itself), TRACER provides a symmetric ReLU-based coherence formulation that reduces sensitivity to weak associations:

$$\text{ReLU}_{\tau}(w) = \begin{cases} w - \tau, & w > \tau \\ w + \tau, & w < -\tau \\ 0, & |w| \leq \tau \end{cases}$$

with $\tau = 0.05$. This defines:

$$\text{purity}_{\text{ReLU}}(G) = \frac{1}{K} \sum_{i < j} \max(\text{ReLU}_\tau(w_{ij}), 0)$$

$$\text{conflict}_{\text{ReLU}}(G) = \frac{1}{K} \sum_{i < j} \max(-\text{ReLU}_\tau(w_{ij}), 0)$$

#### 2.5 Entity Classification

TRACER produces three categories of cellular entities:

| Entity Type | Definition |
|------------|-----------|
| **Whole cell** | Contains a well-focused nucleus in-plane; represents the majority of the cellular volume |
| **Partial cell** | Fragment separated by TRACER from a whole-cell profile (contamination from overlapping cells) |
| **Reconstructed partial cell** | Coherent transcript cluster assembled from previously unassigned transcripts (cells missed entirely by segmentation) |

#### 2.6 Coherence-Derived Evaluation Metrics

TRACER introduces the following segmentation-agnostic metrics:

| Metric | Definition |
|--------|-----------|
| **Purity** | Fraction of gene pairs with NPMI above threshold $\theta$ (coherence) |
| **Conflict** | Weighted sum of negative NPMI values normalized by total possible pairs (incompatibility) |
| **Signal strength** | $S(G) = \sum_{(i,j) \in P} \lvert w_{ij} \rvert$ (total magnitude of gene-gene associations) |
| **Relative purity** | $\frac{\sum \max(w_{ij}, 0)}{S(G)}$ |
| **Relative conflict** | $\frac{\sum \max(-w_{ij}, 0)}{S(G)}$ |

Relative purity and relative conflict sum to 1 when $S(G) > 0$.

---

### 3. Mathematical Properties

The paper establishes several formal properties (with proofs in Supplementary Note 1):

- **Remark 1 (Boundedness)** (Eqs. 14--15): $0 \leq \text{purity}(G) \leq 1$ and $0 \leq \text{conflict}(G) \leq 1$
- **Remark 2 (Well-posedness)**: $-1 \leq C(G) \leq 1$
- **Remark 3 (Noise robustness)** (Eq. 16): Under gene independence ($w_{ij} \approx 0$ with $\mathcal{O}(n^{-1/2})$ fluctuations), $\mathbb{E}[\mathbb{I}(w_{ij} > \theta)] \to 0$ for any fixed $\theta > 0$, so $\mathbb{E}[\text{purity}(G)] \approx 0$ for independent gene pairs
- **Remark 4 (Monotonicity)**: Increasing $w_{ab}$ past $\theta$ weakly increases $C(G)$; decreasing $w_{ab}$ into negative territory strictly decreases $C(G)$
- **Remark 5 ($\Delta C$ biological coherence)**: $\Delta C \geq 0$ only when the union does not introduce disproportionately many negative NPMI pairs; cross-lineage merges yield $\Delta C < 0$ and are rejected
- **Remark R1 (ReLU preservation)**: ReLU transformation preserves boundedness and monotonicity; weak associations in the dead zone $|w_{ij}| \leq \tau$ contribute zero

Note: Eqs. 5--8 define the four-part partition of the event space for each gene pair ($P(i,j)$, $P(i,\neg j)$, $P(\neg i,j)$, $P(\neg i,\neg j)$), which sum to 1 by construction (standard 2$\times$2 contingency table). These are omitted from this summary as they are definitional.

---

### 4. Evaluation

#### 4.1 Datasets

| Dataset | Platform | Transcripts | Segmentation | Source |
|---------|----------|-------------|-------------|--------|
| Breast cancer | Xenium (standard) | 28,059,774 | Nucleus expansion | Janesick et al., *Nat Comm*, 2023 |
| Lung cancer | Xenium (multimodal) | 1,436,900 | Multimodal + nucleus expansion | Takano et al., *Nat Comm*, 2024 |
| Mouse ileum | MERFISH | 819,665 | Baysor + Cellpose 3D membrane | Petukhov et al., *Nat Biotechnol*, 2022 |

#### 4.2 Key Results

##### Coherence Improvement (Breast Cancer Xenium)

Values below are mean cell-level metrics computed from the tutorial output (`metrics_summary.csv`); the paper itself reports these trends via violin plot distributions (Supplementary Fig. 4D) rather than exact scalar values.

| Metric | Before TRACER (NE) | TRACER-Stitched | TRACER-Fine-Tuned |
|--------|--------------------|-----------------|--------------------|
| Purity (mean) | 0.457 | 0.780 | 0.793 |
| Conflict (mean) | 0.055 | 0.001 | 0.002 |
| Relative purity (mean) | 0.625 | 0.998 | 0.994 |
| Relative conflict (mean) | 0.375 | 0.002 | 0.006 |

##### Hybrid Population Resolution

- **Stromal-T cell hybrids**: Resolved into distinct stromal and T cell clusters with lineage-appropriate markers
- **T cell-tumor hybrids**: Separated into distinct T cell and tumor populations (e.g., a single hybrid cell with HER2+ tumor + CD8+ T cell markers splits into two coherent entities)
- **"Unlabeled" cells**: Mixed profiles resolved into coherent T cell-like and tumor-like programs

##### Ligand-Receptor Artifact Removal

Standard segmentation caused DCIS-1 tumor cells (characterized as low-invasive) to spuriously express immune-restricted markers (CD80, CD8A, CD8B), producing biologically implausible DCIS-to-immune cell interactions. TRACER refinement eliminated these artifacts, yielding interaction patterns consistent with lineage-restricted ligand-receptor expression.

##### MERFISH Mouse Ileum: Outperforms 3D Membrane-Guided Segmentation

Compared to Baysor with Cellpose-derived 3D membrane priors:
- TRACER-stitched whole cells exhibited marked increase in purity with further improvement after fine-tuning
- Conflict decreased substantially
- Transcript counts decreased modestly (pruned transcripts were disproportionately associated with incoherent gene-gene relationships)
- TRACER identified 3,275 partial cells forming distinct clusters with coherent marker programs

##### Scrublet Doublet Detection

Scrublet (Wolock et al., *Cell Syst*, 2019) was used as an orthogonal expression-only benchmark:
- **Baysor segmentation**: Elevated Scrublet scores concentrated in cluster-bridge regions, consistent with mixed-lineage contamination
- **TRACER outputs**: Near-zero predicted doublets across all expected doublet-rate settings (0.02, 0.20, 0.25, 0.30), with uniformly low Scrublet scores. Note: the paper Methods text says "three expected doublet rates" but lists four values; the summary lists all four as they appear in the text.

##### Partial Cell Biology

Partial and reconstructed partial cells:
- Form well-defined UMAP clusters with distinct marker programs (LYZ/macrophages, LUM/stromal, CD3E/T cells, SLAMF7/B cells, ERBB2/DCIS tumor, PECAM1/endothelial, ACTA2/perivascular, KIT/mast cells)
- Spatial distribution mirrors whole cells, consistent with vertical continuity of tissue architecture
- Reconstructed partial cell convex hulls fill gaps between segmented cells, supporting biological relevance

##### Deterministic Reproducibility

Across independent runs with different random seeds:
- Exact-match fraction = 1.0
- Adjusted Rand Index (ARI) = 1.0
- Normalized Mutual Information (NMI) = 1.0

Determinism is achieved through: reproducibility seed setting, distance rounding to stabilize near-ties in kNN, lexicographic tie-breaking, and sorted deterministic application order.

#### 4.3 Transcript Accounting (Supplementary Table 2)

**Supplementary Table 2** reports the number of transcripts assigned to whole cells, partial cells, reconstructed partial cells, or remaining unassigned at each TRACER stage. Total transcripts are conserved at every stage.

##### Breast Cancer Xenium (`min_comp_size=25`)

| Stage | Unassigned | Whole Cell | Partial Cell | Reconstructed Partial | Total |
|----|----|----|----|----|-----|
| Original | 1,988,154 | 26,071,620 | 0 | 0 | 28,059,774 |
| Stage 1 (Prune) | 5,921,403 | 18,313,439 | 3,824,932 | 0 | 28,059,774 |
| Stage 2 (Components) | 5,299,316 | 18,313,439 | 3,824,932 | 622,087 | 28,059,774 |
| Stage 3 (Stitched) | 5,299,316 | 18,326,600 | 3,816,187 | 617,671 | 28,059,774 |
| Stage 4 (Spatial) | 5,299,316 | 16,119,790 | 6,022,997 | 617,671 | 28,059,774 |
| Stage 5 (Fine-tuned) | 5,299,316 | 16,307,533 | 5,921,089 | 531,836 | 28,059,774 |

##### Lung Cancer Xenium (`min_comp_size=10`)

| Stage | Unassigned | Whole Cell | Partial Cell | Reconstructed Partial | Total |
|----|----|----|----|----|-----|
| Original | 1,822 | 1,435,078 | 0 | 0 | 1,436,900 |
| Stage 1 (Prune) | 99,128 | 1,113,094 | 224,678 | 0 | 1,436,900 |
| Stage 2 (Components) | 98,949 | 1,113,094 | 224,678 | 179 | 1,436,900 |
| Stage 3 (Stitched) | 98,949 | 1,200,105 | 137,678 | 168 | 1,436,900 |
| Stage 4 (Spatial) | 98,949 | 1,088,743 | 249,040 | 168 | 1,436,900 |
| Stage 5 (Fine-tuned) | 98,949 | 1,225,256 | 112,673 | 22 | 1,436,900 |

##### Mouse Ileum MERFISH (`min_comp_size=10`)

| Stage | Unassigned | Whole Cell | Partial Cell | Reconstructed Partial | Total |
|----|----|----|----|----|-----|
| Original | 0 | 819,665 | 0 | 0 | 819,665 |
| Stage 1 (Prune) | 129,604 | 509,098 | 180,963 | 0 | 819,665 |
| Stage 2 (Components) | 129,604 | 509,098 | 180,963 | 0 | 819,665 |
| Stage 3 (Stitched) | 129,604 | 537,832 | 152,229 | 0 | 819,665 |
| Stage 4 (Spatial) | 129,604 | 436,311 | 253,750 | 0 | 819,665 |
| Stage 5 (Fine-tuned) | 129,604 | 445,028 | 215,033 | 0 | 819,665 |

Key observations: Stage 1 prunes ~8M transcripts from whole cells into partial cells in the breast cancer dataset. Stage 4 spatial refinement redistributes transcripts from whole cells to partial cells (enforcing spatial connectivity), and Stage 5 stitching partially re-merges them. MERFISH produces zero reconstructed partial cells because the original Baysor segmentation had no unassigned transcripts. Note: The mouse ileum MERFISH dataset was preprocessed and filtered by the original study prior to TRACER analysis; both Xenium datasets (breast cancer and lung cancer) correspond to raw, unprocessed transcript-level data.

---

### 5. Computational Performance (Supplementary Table 1)

##### Overall Runtime

| Dataset | Platform | Transcripts | CPUs | MaxRSS (GiB) | Total Runtime | GPU Required |
|---------|----------|-------------|------|---------------|---------------|-------------|
| Breast cancer Xenium | Xenium | 28,059,774 | 17 | 26.9 | 311.1 min (~5.2 h) | No |
| Lung cancer Xenium | Xenium | 1,436,900 | 17 | 2.45 | 6.3 min | No |
| Mouse ileum MERFISH | MERFISH | 819,665 | 17 | 4.57 | 1.75 min | No |

##### Per-Stage Breakdown (minutes)

| Dataset | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 |
|---------|---------|---------|---------|---------|---------|
| Breast cancer Xenium | -- | 8.2 | 72.8 | 144.1 | 31.0 |
| Lung cancer Xenium | 0.30 | 0.40 | 1.00 | 0.50 | 4.10 |
| Mouse ileum MERFISH | 0.06 | 0.01 | 0.13 | 0.09 | 1.12 |

Note: Breast cancer Stage 1 runtime was not clearly resolved in the OCR of the supplementary table. For the smaller datasets, Stage 5 (final stitching) dominates runtime; for the large breast cancer dataset, Stage 4 (spatial coherence enforcement) is the bottleneck. Wall-clock time was measured via SLURM (`sacct`); per-stage runtimes were obtained from internal logs.

Hardware: Dual-socket Intel Xeon Platinum 8580 (120 cores, 503 GiB RAM). All jobs used 17 allocated CPU cores and 96 GB requested memory.

---

### 6. Implementation Details

#### Software Architecture

The codebase is organized as a pip-installable Python package (`tracer`):

```
src/tracer/
  __init__.py
  core.py          # Main pipeline: pruning, graph construction, stitching, spatial coherence
  metrics.py       # NPMI computation, purity/conflict scoring, quality filtering
  plot.py          # Visualization utilities
  tiling.py        # Spatial tiling for large datasets
  _cy_prune.pyx    # Cython-accelerated greedy pruning
  _cy_spatial.pyx  # Cython-accelerated spatial label-constrained components
```

#### Key Dependencies

- **PyTorch Geometric**: Graph construction and manipulation (`torch_geometric.data.Data`)
- **SciPy**: Delaunay triangulation (`scipy.spatial.Delaunay`), connected components (`scipy.sparse.csgraph`)
- **scikit-learn**: k-nearest neighbors (`sklearn.neighbors.NearestNeighbors`)
- **NetworkX**: Graph algorithms for connected component detection
- **Scanpy**: Downstream single-cell analysis (normalization, PCA, Leiden clustering, UMAP)
- **Squidpy**: Ligand-receptor interaction analysis (permutation-based testing with OmniPath database)
- **Cython** (optional): Performance acceleration for pruning and spatial operations

#### Default Parameters

| Parameter | Value | Stage |
|-----------|-------|-------|
| NPMI pruning threshold | $-0.1$ | Stages 1, 2 |
| Minimum transcript count for gene presence ($N_{\min}$) | 2 | NPMI computation |
| kNN neighbors for unassigned graph | $k = 8$ | Stage 2 |
| Distance threshold for kNN | 1.5 $\mu$m | Stage 2 |
| Minimum component size | 25--50 transcripts | Stage 2 |
| Purity threshold $\theta$ | 0.05 | Stage 3 coherence |
| ReLU dead-zone $\tau$ | 0.05 | ReLU metrics |
| $\Delta C$ minimum for merging | 0.0 | Stage 3 |
| Simplicity penalty | Enabled | Stage 3 |

#### Reproducibility Infrastructure

The code implements several mechanisms for deterministic outputs:
- `set_reproducibility_seed(42)`: Sets `PYTHONHASHSEED`, `np.random.seed`, `random.seed`
- Distance rounding to 6 decimal places (`np.round(distances, decimals=6)`) to stabilize near-ties in kNN
- Lexicographic ordering of neighbors: `np.lexsort((indices, dist_key))`
- Deterministic component ordering: `sorted(components, key=lambda comp: min(comp))`
- Sorted application order for pass 1/2 results: `results.sort(key=lambda x: str(x[0]))`
- Deterministic label assignment: `sorted(cell_ids[r])[0]`
- `reproducibility_smoke_test()` function for verification

---

### 7. Limitations

1. **Parameter sensitivity**: Maximum spatial distance threshold for fine-tuning requires tuning; relaxed thresholds (e.g., 15 $\mu$m) can merge spatially distant transcripts into overly large partial cells
2. **Noisy input NPMI**: Computing NPMI from noisy segmentation may yield misleading gene associations; mitigated by using nuclear segmentations (less susceptible to boundary errors)
3. **Rare gene undersampling**: Infrequent genes may show spurious mutual exclusion; handled by conservative pruning (ignoring evidence from rare gene pairs)
4. **Transitional cell states**: Population-level NPMI statistics may not capture rare transitional states (e.g., EMT, macrophage repolarization) that legitimately express cross-lineage markers, potentially leading to incorrect pruning
5. **Not adaptive**: Fixed distance thresholds across tissue regions; future work could incorporate data-driven distance estimation

---

### 8. Data and Code Availability

| Resource | URL |
|----------|-----|
| TRACER code | https://github.com/imlong4real/TRACER |
| Xenium breast cancer | https://www.10xgenomics.com/products/xenium-in-situ/preview-dataset-human-breast |
| Xenium lung cancer (multimodal) | https://kero.hgc.jp/Ad-SpatialAnalysis_2024.html |
| MERFISH mouse ileum | https://datadryad.org/dataset/doi:10.5061/dryad.jm63xsjb2 |
| Curated benchmarking data | Zenodo DOI: 10.5281/zenodo.18892839 |

Docker support is available via the included `Dockerfile`. Multiple tutorials with real datasets are provided for breast cancer, lung cancer, melanoma, and mouse ileum.

---

### 9. Reproducibility Rating: 5/5

- Code fully available under Apache 2.0 with pip-installable package
- All datasets publicly available with clear download links and documented preprocessing
- Deterministic outputs by design (identical results across runs: ARI = 1.0, NMI = 1.0)
- Multiple tutorials covering Xenium and MERFISH workflows
- Docker support for environment reproducibility
- Supplementary tables document runtime, memory, and transcript accounting across all stages
- Built-in `reproducibility_smoke_test()` for verification
- No GPU required; runs on standard multi-core CPU hardware

---

### 10. Compared Methods

| Method | Year | Journal | Role in Paper |
|--------|------|---------|---------------|
| Baysor | 2022 | *Nat Biotechnol* | Baseline segmentation (3D membrane-guided); TRACER outperforms on purity/conflict |
| SCS | 2023 | *Nat Methods* | Referenced as prior segmentation correction approach |
| BIDCell | 2024 | *Nat Comm* | Referenced as deep learning segmentation method |
| fastreseg | 2025 | *Sci Rep* | Referenced as transcript reassignment heuristic |
| Bering | 2025 | *Nat Comm* | Referenced as GNN-based approach (requires training) |
| Segger | 2025 | *bioRxiv* | Referenced as contrastive learning framework (requires training) |
| Scrublet | 2019 | *Cell Syst* | Used as orthogonal doublet-detection benchmark |
| Squidpy | 2022 | *Nat Methods* | Used for ligand-receptor interaction analysis |
| Scanpy | 2018 | *Genome Biol* | Used for single-cell preprocessing and clustering |
| Cellpose | 2020 | *Nat Methods* | Used for 3D membrane segmentation (input to Baysor) |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
