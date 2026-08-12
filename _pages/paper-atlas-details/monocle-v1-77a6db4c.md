---
layout: default
permalink: /paper-atlas/monocle-v1-77a6db4c/
title: "Monocle v1"
nav: false
description: "Monocle 1 的出发点是一个实验事实：即使细胞在同一时刻被收集，它们也可能处在完全不同的分化阶段。若只按 0、24、48、72 小时分组取平均，早开始和晚开始分化的细胞会混在一起，关键调控开关被平滑掉。Monocle 因此不把采样时刻当作细胞内部时间，而是根据表达相似性将单细胞重新排列，定义“pseudotime”。 论文的输入是已经定量的单细胞表达矩阵；该研究使用人骨骼肌成肌细胞的 FPKM。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Biotechnology · 2014</span>
    </div>
    <h1>Monocle v1</h1>
    <p>The dynamics and regulators of cell fate decisions are revealed by pseudotemporal ordering of single cells</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/nbt.2859" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Monocle 1 中文方法解读：从异步单细胞快照重建伪时间

### 1. 论文真正提出了什么

Monocle 1 的出发点是一个实验事实：即使细胞在同一时刻被收集，它们也可能处在完全不同的分化阶段。若只按 0、24、48、72 小时分组取平均，早开始和晚开始分化的细胞会混在一起，关键调控开关被平滑掉。Monocle 因此不把采样时刻当作细胞内部时间，而是根据表达相似性将单细胞重新排列，定义“pseudotime”。

论文的输入是已经定量的单细胞表达矩阵；该研究使用人骨骼肌成肌细胞的 FPKM。核心输出包括细胞在低维空间中的最小生成树、每个细胞所属的轨迹/分支与伪时间，以及沿伪时间显著变化的基因及其表达趋势。下游再对趋势聚类、做调控元件富集，并用 shRNA 实验验证候选因子。

这里的伪时间不是钟表时间，也不是细胞真实年龄。它是沿算法选定轨迹累计的转录变化距离。只有在“相邻表达状态代表相邻生物阶段”且采样覆盖连续过程时，伪时间才可被解释为分化进程。

### 2. 为什么采样时间不够

Fig. 1a 给出实验设计：血清切换后按 24 小时间隔捕获细胞。Fig. 1c 显示 ENO3 和 MYH3 在相同时间点的单细胞之间高度异质；Fig. 1d 的免疫荧光也表明同一培养皿中细胞进展不同。因此，采样时刻只给出弱先验，不能作为细胞状态的精细顺序。

Monocle 的关键假设是，异步性反而提供了许多过程“中间帧”。如果不同细胞覆盖了从增殖到分化的连续表达状态，就能从快照拼出一条状态路径。这一逻辑类似把打乱的电影帧重新排序，但帧之间的相似性来自高维表达而非图像。

### 3. 细胞排序的算法主链

#### 3.1 选择用于排序的基因

论文分析先过滤低质量细胞与低检测基因，并选择随采样日显著变化的基因用于排序。这个步骤很重要：若把大量纯噪声或与过程无关的基因放入距离，细胞几何会被技术变化主导；但使用采样日筛基因也意味着方法并非在所有层面都完全不使用时间标签。算法的轨迹构建是无监督的，但本研究的 ordering gene 选择利用了实验设计。

论文对 FPKM 的检测下限使用 Tobit 模型。可把观测表达写为

$$
Y=\begin{cases}
Y^*, & Y^*>\lambda,\\
\lambda, & Y^*\leq\lambda,
\end{cases}
$$

其中 $Y^*$ 是潜在连续表达，$\lambda$ 是检测下限。这样，位于下限的观测被视作左截尾，而不是等同于真实表达恰好为零。它针对的是该时期 FPKM 数据及检测机制；不能直接当作现代 UMI counts 的通用分布模型。

#### 3.2 ICA 降到二维

每个细胞最初是 $d$ 维表达向量。Monocle 1 对 ordering genes 的表达做变换和标准化，再用 Independent Component Analysis（ICA）得到二维坐标：

$$
x_i\in\mathbb{R}^d \longrightarrow z_i\in\mathbb{R}^2.
$$

ICA 试图寻找统计独立的潜在成分，不是按最大方差排序的 PCA。论文选择二维是为了构图和可视化，也隐含了一个强约束：真实过程必须能在这两个成分中保持主要连接关系。若不同状态在二维中重叠，后续 MST 无法恢复被压缩掉的信息。

#### 3.3 在细胞上构造最小生成树

在 ICA 坐标中计算细胞间欧氏距离，并连接一棵 minimum spanning tree（MST）。MST 在连接所有细胞的前提下，使边长总和最小：

$$
T^*=\arg\min_{T\in\mathcal{T}}\sum_{(i,j)\in E(T)}\lVert z_i-z_j\rVert_2.
$$

树没有环，因此天然提供一条或多条可遍历路径。Fig. 2b 中每个点是细胞，细线是 MST 边；增殖细胞、分化肌母细胞与间质细胞形成主干和侧支。

MST 是一种几何摘要，不是实验观察到的细胞谱系。它必须连接所有点，因此离群细胞也会被接到某处；两条生物学上分离的过程若在 ICA 空间靠近，可能被错误连接。

#### 3.4 主路径、PQ tree 与分支

Monocle 先寻找 MST 的直径路径，即树中距离最长的端点间路径，把它作为主要轨迹骨架。论文随后用 PQ tree 表示与 MST 拓扑相容的细胞顺序，并在允许的排列中选择使相邻细胞转录距离较小的顺序。对不在主路径上的细胞，再寻找替代子轨迹并接回主轨迹，使一个前体能够通向多个 fate。

“最长路径”并不自动告诉算法哪个端点是起点。方向需要结合实验先验或已知 marker 确定。在肌生成案例中，增殖标记 CDK1 高的群体被解释为早期，肌分化标记 MYOG/MYH2 高的群体被解释为晚期。若没有这样的外部依据，树的方向可整体翻转。

#### 3.5 从树距离定义伪时间

设选定起始细胞为 $s_0$，从根到细胞 $s_i$ 的有序路径为 $s_0,s_1,\ldots,s_i$，伪时间是路径上相邻细胞距离的累积：

$$
\psi(s_i)=\sum_{j=1}^{i}\lVert z_{s_j}-z_{s_{j-1}}\rVert_2.
$$

因此两个相邻细胞的伪时间差反映 ICA 空间的转录变化量，而不是固定分钟数。树上分支共享分叉前的累计距离，分叉后各自继续增加。最终每个细胞同时拥有 pseudotime 和 trajectory/branch 标签。

一个数值直觉：若从根到某细胞依次经过三条长度 0.4、0.7、0.2 的边，则其伪时间是 1.3；另一个细胞即使在 48 小时采集，只要离根路径总长为 0.8，就会被排在前者之前。

### 4. 如何检测沿伪时间变化的基因

得到 $\psi_i$ 后，论文对每个基因拟合表达随伪时间的非线性曲线。概念上比较：

$$
\text{full}:\quad g\big(E[Y_i]\big)=s(\psi_i),
$$

与不含伪时间的 null model。这里 $s(\cdot)$ 是低自由度平滑函数，表达观测仍用 Tobit 截尾分布。似然比检验产生 p 值，再做 Benjamini–Hochberg FDR 校正。论文报告 1,061 个动态基因（FDR < 5%）。

这一检验回答“表达是否随当前推断的伪时间系统变化”，并不证明基因驱动了时间变化。伪时间和表达来自同一数据，ordering genes 的选择还可能带来选择性偏差；独立验证和对非 ordering genes 的检查尤其重要。

随后，论文用拟合曲线之间的相关性定义距离，并将基因聚成六类动力学模式：立即、短暂、渐进的上调或下调。Fig. 3 左侧直接展示这六种模式；中间是 GO 富集，右侧是调控元件中的转录因子 motif 富集。

### 5. 从动态相关到候选调控因子

Monocle 的轨迹本身只产生顺序。论文的调控推断还包含额外步骤：

1. 对动态基因按伪时间曲线聚类；
2. 在各类基因的 promoter/enhancer 中检测保守 TF motif 富集；
3. 根据 motif 与已知肌生成因子的共占据关系提出候选；
4. 通过 shRNA knockdown 测量 MYH2 阳性比例与面积。

Fig. 4a 显示多种候选敲低后的分化表型，Fig. 4b 展示 enhancer/promoter motif co-occupancy，Fig. 4c 给出竞争结合或直接抑制两种机制模型。实验支持候选因子影响肌生成，但 motif 共富集不能单独区分两种机制，论文也明确把机制写成待进一步验证的模型。

### 6. 四张主图应怎样连起来读

- **Fig. 1** 建立问题：同一采样时刻的细胞不同步，按 clock time 平均会模糊状态。
- **Fig. 2a–b** 展示 ICA → MST → 主路径 → pseudotime；Fig. 2c–f 展示重新排序后出现连续表达波和 ID1/MYOG 开关。
- **Fig. 3** 把 1,061 个动态基因压缩成六类时间模式，并连接到 GO 和 motif 候选。
- **Fig. 4** 从计算候选走向 perturbation 验证，防止把相关性直接当成调控因果。

本次直接查看了四张本地主图。Fig. 2b 的绿色间质细胞支路说明分支也可能代表污染/不同细胞类型，而不是共同前体真正分化出的第二命运；论文结合 PDGFRA、SPHK1 和免疫荧光把它解释为间质污染群。这是“树分支不等于谱系分叉”的重要例子。

### 7. 补充材料提供的关键验证

本地补充 PDF 共 17 页。Supplementary Fig. S4–S6 用 marker 与已知肌生成调控程序检查排序；Fig. S7 对随机抽取的细胞子集重新排序，报告小至 50 个细胞时与全数据顺序仍有较高 Spearman 相关，并评估动态基因检测的 precision/recall；Fig. S9 比较 bulk、按采样日排列的单细胞与按伪时间排列的单细胞，说明异步混合压缩了动态范围。

这些验证支持该数据集上的稳定性，但不能转化为任意数据规模或拓扑的保证。特别是当中间状态未采到、批次与进程混杂、存在环状过程或多条轨迹在二维重叠时，MST 仍会给出一棵树，却可能没有正确生物学解释。

### 8. 常见误读与边界

#### 8.1 “无监督”不等于没有分析选择

轨迹构建不需要预先给每个细胞 fate 标签，但本研究用采样日筛 ordering genes，并用已知 marker 决定方向和解释群体。基因过滤、变换、ICA 维度、距离、分支数与起点都会影响结果。

#### 8.2 伪时间不是绝对时间

$\psi$ 的单位是嵌入空间路径距离。不能把伪时间 10 解释为 10 小时，也不能直接比较两个独立运行的数值尺度。伪时间压缩或扩展的区域还受采样密度影响。

#### 8.3 MST 强制树结构

树无法表示环和汇合；每个点必须被连接。细胞周期等环状过程、两个谱系汇入同一状态或真正离散的群体都可能被误表达。应检查邻域、离群点和替代降维结果，而不能只接受一条好看的线。

#### 8.4 动态基因不等于因果 driver

沿伪时间变化可能是过程结果、共同上游调控或细胞组成变化。本文之所以能提出更强结论，是因为随后做了 motif 分析和 loss-of-function 实验；没有这些证据时只能称 pseudotime-associated genes。

### 9. 代码与版本证据边界

该工作区没有 Monocle 1 源码快照，也没有可验证的 Monocle 1 Git commit。论文当时指向 `monocle-bio.sourceforge.net` 并提到 supplementary source code，但本地搜索范围内未获得该源代码。因此，本工作区必须保持 `paper-only`，`doc_code.md` 只能把论文 Online Methods 转成候选实现映射，所有条目均为 **Inferred / Not verified**，不能标为 Exact。

相邻 `[local path omitted]` 是 Monocle 3 源码。Monocle 3 使用不同的数据结构、降维和 principal graph 学习流程；它不能作为 Monocle 1 的直接代码证据。本次没有读取它来证明任何 Monocle 1 实现，也没有修改该邻居目录。

因此，实现层面当前能确认的是论文明确声明的依赖与公式边界，例如 fastICA、MST/PQ tree、VGAM Tobit/GAM 与似然比检验；具体函数名、包内文件布局和默认参数若只来自推断，均不应冒充源码事实。

### 10. 一个可靠的复现检查单

若要重新实现或复现 Monocle 1，应至少记录：

1. 原始 reads 到 FPKM 的软件版本与过滤规则；
2. ordering genes 如何选取，是否使用采样时刻；
3. log/标准化细节、ICA 随机种子与保留成分；
4. MST 距离、起点、主路径、分支数与 PQ tree 排列规则；
5. pseudotime 的方向与 marker 外部证据；
6. Tobit 检测下限、平滑自由度、null/full model 与 FDR；
7. 对细胞抽样、ordering gene 集合和离群点的敏感性分析。

本工作区没有重跑原始数据或源码，因而不声称数值级复现。它完成的是论文、主图、图注和补充材料的源证据解释，并把缺失的代码证据明确保留为 `Not found`。

### 11. 本工作区证据入口

- 主文：`paper source/PMC4122333/paper.md`
- 论文 PDF：`paper source/PMC4122333/nihms-570726.pdf`
- 补充 PDF：`paper source/PMC4122333/NIHMS570726-supplement-1.pdf`
- 主图：`paper source/PMC4122333/images/nihms-570726-f0001.jpg` 至 `f0004.jpg`
- 代码：`MISSING / Not found`（Monocle 1 本地直接源码不存在）

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Monocle v1 — Paper Summary

### Motivation & Novelty

#### Biological Problem

Understanding cell differentiation requires knowing the precise sequence and timing of transcriptional changes. Skeletal muscle differentiation — one of the most studied systems in cell biology — had been characterized at the transcriptomic level using bulk RNA-Seq, identifying key master regulators (MYOD, MYOG, MRF4, MYF5) and broad kinetic trends. However, individual myoblasts differentiate at different rates: at any given time point, the same culture contains proliferating progenitors, intermediate myocytes, and terminally differentiated myotubes side by side.

Bulk measurements average over this mixture, creating **Simpson's paradox artifacts**: trends in individual cells are obscured by averaging, positively correlated regulators can appear uncorrelated, and fine-grained sequential gene programs collapse into a small number of coarse temporal clusters. Experimental synchronization by serum starvation or cell sorting disrupts the physiological differentiation niche and significantly alters kinetics.

#### Why Existing Methods Fell Short

| Method | Limitation |
|---|---|
| Bulk RNA-Seq time series (Cuffdiff, DESeq2) | Averages over asynchronous cells; masks Simpson's paradox |
| SPD algorithm — Qiu et al., *PLOS Comput. Biol.* 7, 2011 | Bulk expression input; sensitive to mixing effects; requires prior knowledge of trajectory endpoints |
| Magwene et al. microarray ordering algorithm (ref. 10 in paper) | Bulk microarray samples; assumes single trajectory; no branching; no single-cell variation modeled; original source of the PQ tree–based ordering approach Monocle extends |
| SPADE — Qiu et al., *Nat. Biotechnol.* 29, 2011 | Mass cytometry only; limited to ~32 protein markers; requires predefined marker panel |

Single-cell RNA-Seq captures complete transcriptomes per cell, but existing algorithms in 2014 either required prior knowledge of marker genes (flow cytometry-based) or operated on averages (bulk ordering).

#### Unique Contributions of Monocle v1

1. **First unsupervised whole-transcriptome single-cell ordering algorithm**: No marker knowledge required; works from any scRNA-Seq experiment
2. **Branched trajectory reconstruction**: Handles multiple cell fates arising from a single progenitor — a topological extension of prior single-trajectory bulk ordering
3. **Pseudotime concept formalized**: Defines pseudotime as cumulative transcriptional distance along the trajectory, providing a continuous measure of biological progress independent of clock time
4. **Integration with differential expression**: Directly links ordering to statistical identification of dynamically regulated genes using censored regression (Tobit) to handle RNA-Seq detection limits
5. **Biological discovery pipeline**: Pseudotime ordering → gene clustering → cis-regulatory analysis → experimental validation — a complete discovery-to-validation workflow

---

### Method Overview

Monocle treats a single-cell RNA-Seq experiment as a time series in disguise. Each cell represents a distinct point along the differentiation trajectory, and the algorithm's task is to recover the order of these points.

**Algorithmic framework**:

1. **Gene selection**: Filter for reliably detected, dynamically varying genes (Tobit-family differential expression test between timepoints; FDR < 0.01)
2. **Dimensionality reduction**: Project selected genes into 2D space via Independent Component Analysis (ICA), which finds statistically independent axes of variation
3. **Graph construction**: Build a Minimum Spanning Tree (MST) on cells in 2D ICA space, using Euclidean distance as edge weights
4. **Trajectory ordering**: Find the MST's diameter path (longest path); handle noise-driven branches with a PQ tree; assign pseudotime as cumulative Euclidean distance along the ordering
5. **Branching**: User specifies number of lineages k; algorithm identifies k longest backbone branches and constructs a tree-structured ordering
6. **Differential analysis**: Fit a GAM-Tobit model per gene (cubic spline function of pseudotime, 3 effective df); identify dynamically regulated genes by likelihood ratio test
7. **Gene clustering**: K-medioid clustering on GAM-predicted expression curves using correlation-based distance

**Key biological assumptions**:
- Differentiation is a continuous, smooth process in transcriptome space
- Cells from the same biological process are captured at various stages of progress
- Noise in individual cells is smaller than the systematic variation due to differentiation progress
- Gene expression varies smoothly along the differentiation trajectory (justifying the spline model)

**Computational pipeline**: See `doc_method.md` for detailed mathematical derivations and `doc_code.md` for implementation details.

---

### Evaluation

#### Dataset

- **Organism/system**: Primary human skeletal muscle myoblasts (HSMM), quadriceps biopsy, female age 17
- **Cell capture**: Fluidigm C1 microfluidic system; one chip per timepoint (49–77 cells/timepoint)
- **Timepoints**: 0h (growth medium), 24h, 48h, 72h post-serum switch (differentiation medium); 4 timepoints × ~60 cells = **~250 single cells total**
- **Sequencing**: ~4M 100bp paired-end reads per cell (HiSeq 2500); bulk RNA-Seq at 10-20M reads/library for comparison
- **Expression quantification**: TopHat 2.0.9 → Cuffdiff 2.2 → FPKM; GENCODE v17; hg19
- **GEO accession**: GSE52529

#### Main Results

| Metric | Value | Context |
|---|---|---|
| Dynamically regulated genes | 1,061 | FDR < 5% by GAM-Tobit LRT |
| Gene clusters identified | 6 | Distinct pseudo-temporal kinetic trends |
| TFs enriched near upregulated genes | 175 | cis-regulatory analysis via ENCODE DNase-I HS + ChromHMM |
| Novel TF regulators validated | 4 | MZF1, ZIC1, XBP1, USF1 (FDR < 5% by shRNA screen) |
| Marginal regulators | 4 | CUX1, ARID5B, POU2F1, AHR (trend toward significance) |
| Robustness (50 cells subset) | Spearman ≥ 0.8 | vs. full-dataset ordering |
| Precision of dynamic gene detection | ≥95% | Maintained across all subset sizes tested |

#### Biological Validation

- **Ordering accuracy**: Pseudotime correctly recovers MEF2C preceding MYH2+ cells (confirmed by parallel immunofluorescence; Fig 2d)
- **Gene kinetics**: Cell-cycle regulators (CDK1) active early; sarcomere components active late — consistent with expected myogenesis biology
- **ID1 switch**: Switch-like inactivation of ID1 (prerequisite for MYOG activation) is clearly visible in pseudotime but masked in real-time ordering (Fig 2e,f) — a textbook demonstration of why pseudotime ordering is needed
- **Contaminating cell type**: Pseudotime identifies a branch of interstitial mesenchymal cells (PDGFRA+, SPHK1+) without requiring prior immunopurification
- **Cross-species validation**: Pseudotemporal kinetics of MYOD/MYOG/MEF2 targets are highly consistent with those in C2C12 mouse myoblast differentiation
- **RNAi screen**: 44 shRNAs against 11 predicted TF candidates; knockdown of XBP1, USF1, ZIC1, MZF1 significantly enhanced myotube formation; MYH2+ fraction and total myotube area increased; nuclei counts unchanged (ruling out proliferation artifact)

#### Comparison to Bulk RNA-Seq

Bulk RNA-Seq analysis of the same differentiation time course:
- Identified up- and downregulated genes but did **not** distinguish early from late regulation
- Did **not** detect the 6 distinct kinetic clusters (only coarser trends visible)
- Dynamic range of expression was compressed for most genes (Simpson's paradox effect)
- Missed the switch-like ID1 inactivation event
- Identified fewer enriched TF motifs than pseudotime analysis (subset of the 175 found by Monocle)

---

### Reproducibility Rating: 3/5

**Justification**: The algorithm is described with mathematical rigor in the Online Methods, and most implementation choices are specified (ICA k=2, VGAM FPKM 0.1, FDR thresholds, PAM k=6). However:

**Strengths**:
- Full mathematical formalism for pseudotime, branching, and differential expression
- R packages named explicitly (fastICA, VGAM, PAM)
- Expression pipeline specified (TopHat 2.0.9 + Bowtie 2.0.6 + Cuffdiff 2.2)
- Data deposited at GEO: GSE52529
- Supplementary Source Code provided with the paper

**Weaknesses / Reproducibility Challenges**:
- K for ICA (k=2) is not automatic — requires user judgment for new datasets
- K for gene clustering (K=6) is not automatic — paper notes "largest K that produced qualitatively distinct clusters"
- Gene selection depends on availability of time point labels — algorithm differs for cross-sectional data
- Cuffdiff 2.2 is now deprecated; modern scRNA-Seq workflows use count-based tools (STAR, featureCounts, UMI counts), not FPKM. Reproducing the exact pipeline requires the legacy Tuxedo suite.
- Monocle v1 sourceforge repository may have limited maintenance; users should use Monocle 2 or 3 (available on Bioconductor)
- The "15-gene manual QC" step is semi-manual and cannot be automated

**Environment setup**: R 3.x with CRAN packages (fastICA, VGAM, cluster/PAM, CummeRbund). Primary scRNA-Seq data from Fluidigm C1 platform. Bulk alignment requires the legacy Tuxedo pipeline.

**Common pitfalls**:
- ICA is non-deterministic (random initialization); results can vary between runs — fix random seed
- Tobit model convergence can fail for very lowly expressed genes
- PQ tree exhaustive search can be slow if data is very noisy (many indecisive vertices)
- The number of branches k must be specified correctly — wrong k produces artifactual trajectory structure

**Successor algorithms**: Monocle v1's core limitations (2D ICA only; manual k for branches; bulk FPKM input) motivated two major revisions: **Monocle 2** (Qiu et al., *Nature Methods* 2017) replaced ICA with DDRTree for higher-dimensional trajectories; **Monocle 3** (Cao et al., *Nature Methods* 2019) replaced DDRTree with UMAP + principal graphs for large-scale atlas data. Both are available on Bioconductor as `monocle` and `monocle3` packages.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
