---
layout: default
permalink: /paper-atlas/scamvib-9bb16e6b/
title: "scAMVIB"
nav: false
description: "同一细胞的 RNA、ATAC 或 ADT 既含共同的 cell-type 信号，也含模态特异信息与技术噪声。简单拼接会让高维模态支配距离，等权融合又假设每个模态同样可靠。scAMVIB 把每个组学视为一个 view，用 information bottleneck 将细胞压缩成离散 cluster T，同时尽量保存各 view 对 cluster 有用的信息；view 权重在迭代中自适应更新。 算法不是深度生成模型。"
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
      <span>Briefings in Bioinformatics · 2026</span>
    </div>
    <h1>scAMVIB</h1>
    <p>Adaptive multi-view information bottleneck for multi-omics data clustering</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1093/bib/bbaf717" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scAMVIB：用多视图信息瓶颈做单细胞多组学聚类

### 它解决的核心问题

同一细胞的 RNA、ATAC 或 ADT 既含共同的 cell-type 信号，也含模态特异信息与技术噪声。简单拼接会让高维模态支配距离，等权融合又假设每个模态同样可靠。scAMVIB 把每个组学视为一个 view，用 information bottleneck 将细胞压缩成离散 cluster $T$，同时尽量保存各 view 对 cluster 有用的信息；view 权重在迭代中自适应更新。

算法不是深度生成模型。它由 Python 预处理和 MATLAB sequential IB 两段组成：先用 similarity network fusion 生成跨组学增强矩阵 $S'$，再把原始两个组学和 $S'$ 当作三个 views，运行硬聚类 draw–merge 优化。论文题为 “Adaptive multi-view information bottleneck for multi-omics data clustering”，DOI `10.1093/bib/bbaf717`，Fig. 1 是流程总览。

### 第一段：为什么先构造信息增强 view

对每个组学，IE-MOIF Python 脚本先 MinMax 或 z-score 标准化，再用 SNF 建立 cell–cell affinity。论文把相似度、transition matrix 和局部 KNN kernel 写成 Eqs. 1–4；当前代码直接调用 `snfpy`：

- `snf.make_affinity(..., metric='euclidean', K=20, mu=0.5)`；
- `snf.snf(..., K=20)`；
- 最后计算 $S'=P^{(c)}S$。

直接位置是 `scAMVIB/IE_matrix/main_IE-MOIF.py:39-95`。K=20 和 $\mu=0.5$ 在代码中硬编码，论文主要参数分析没有充分讨论它们。

$S$ 是选定的局部 feature matrix。若 `--drm fs`，脚本使用 `SelectKBest(chi2)`，但 `fit()` 的第二个输入来自真实 label（`:73-85`）。因此该 feature-selection 路径是监督的，与“整个 clustering 无监督”存在实质边界。若现实数据没有标签，应关闭它或用不依赖标签的方案；论文 benchmark 的性能不能无条件代表无标签部署。

SNF view 把跨模态邻域结构传播回 feature space，能补充原始 RNA/ATAC/ADT；它也可能把错误邻居扩散到 $S'$。把 $S'$ 当第三个 view 并不意味着得到独立的新实验模态，它与前两个 view 高度派生相关。

### 信息瓶颈到底在优化什么

经典 IB 对输入细胞 $X$、cluster 表示 $T$ 和 relevant variable $Y$ 使用

$$
\mathcal L=I(T;X)-\beta I(T;Y).
$$

第一项鼓励压缩，第二项鼓励 cluster 保留 feature 信息。scAMVIB 对 $m$ 个 view 扩展为

$$
\mathcal L=\sum_{i=1}^m w_i\{I(T;X)-\beta I(T;Y^i)\},\qquad \sum_iw_i=1.
$$

这里 $X$ 不是原始矩阵本身，而是“细胞身份”；$Y^i$ 是某 view 的 feature 变量；$T$ 是硬 cluster assignment。`ProcessInput.m` 将每个非负矩阵行归一成 $p(y^i\mid x)$，并构造 joint/marginal probabilities。因为算法使用概率和对数，负 z-score 输入不天然合适；默认 MinMax 更符合实现假设。

核心实现沿用 Slonim、Friedman、Tishby 2003 sequential IB 代码思想，`BasicFunction` 保留相关版权。scAMVIB 的新增重点是多 view、增强 view 与自适应权重，而非从零发明 hard IB。

### draw–merge：一个细胞怎样换 cluster

初始时随机把细胞分到 $k$ 个 clusters，并复制同一 partition 给所有 views。每次 sweep 对细胞 $x$：

1. 从当前 cluster 暂时 draw 出 $x$；
2. 对每个候选 cluster $t$ 和每个 view，计算 merge cost；
3. 将 view costs 按当前 $w_i$ 加权；
4. 选择总 cost 最小的 cluster 并更新所有 views 的同一 assignment。

若把 $x$ 合入 $t$，$p(\tilde t)=p(x)+p(t)$，新 centroid 是二者按 mixing proportions 的加权平均。feature preservation cost 使用 Jensen–Shannon divergence：

$$
\Delta L_i=p(\tilde t)\left[JS_\Pi\{p(y^i\mid x),p(y^i\mid t)\}-\beta^{-1}H(\pi_1,\pi_2)\right].
$$

hard assignment 下 compression 项可化为二元 mixing entropy，所以代码 `MergeCosts.m` 用 `Ent([pi1 pi2])` 是等价简化。`OptimizeT.m:12-30` 是逐细胞循环，`MinSumCosts.m` 计算加权 argmin，`UpdateAssignment.m` 同步所有 view。

这不是 k-means：距离不是 Euclidean centroid distance，而是 cluster 前后 mutual information 变化。代价是计算随 cells×features×iterations 增长，大数据运行可达小时级。

### 自适应权重：论文与代码最重要的不一致

论文 Eq. 14 以 maximum-entropy 推导写出一种基于

$$
|I(T;X)-\beta I(T;Y^i)|
$$

的平方根权重。当前代码没有实现该公式。每轮 assignment 后，`OptimizeT.m:33-64` 计算

$$
o_i=H(T)-\beta I(T;Y^i),
$$

再用 Boltzmann softmax：

$$
w_i=\frac{\exp(-o_i/\theta)}{\sum_j\exp(-o_j/\theta)}.
$$

这里 `prm.inv_beta=1/beta`，所以代码 `(1/prm.inv_beta)*ITY` 确实是 $\beta I(T;Y)$。$H(T)$ 在 uniform cell prior 和 deterministic clustering 下作为 $I(T;X)$。这套 softmax 与论文 Eq. 14 不是代数等价形式，是明确的 paper-code discrepancy。

更关键的是温度 $\theta$ 完全没有出现在论文公式：小 $\theta$ 使一个 view 更占优势，大 $\theta$ 使权重趋于均匀。`Runing.m:47-50` 设 `Select_theta=50`，而 `T_search.m` 还搜索其他值。旧 `CLAUDE.md` 所称“最大熵公式已实现”必须加上这一代码事实边界。

论文 Algorithm 1 也没有显示权重更新步骤，但代码在每个 sweep 后确实交替更新，因此伪代码不完整。

### 收敛、重启和“最佳结果”

`CheckConvergence.m` 在一个 sweep 没有 assignment 改变或达到 100 loops 时停止。`MainIB.m:30-47` 默认做 10 次随机重启，并按最终信息目标选择内部 best $T$。

但 `Runing.m:84-132` 从真实 labels 读取 $k$，也就是 cluster 数不是无监督估计；随后对每次 restart 计算 ARI/NMI，并在写结果时选择最大 ARI 的 restart。虽然 `MainIB` 自身按目标选 best，外层 benchmark 输出还使用 ground truth 做 model selection。现实无标签任务无法复制这一选择，应只用内部 objective、稳定性或另行估计 $k$。

论文报告 AMI，但 `Runing.m` 仅调用 `func_nmi` 和 `func_ari`（`:97-106`）；AMI 未在当前主执行脚本计算。统计显著性、九次/多次实验和论文所有表格也不在一个可运行 orchestration 中。

### 图表证据怎样串联

- Fig. 1 给出 raw views→IE-MOIF增强→多 view IB→cluster 的总体流程。
- Fig. 2 在 SLN111D1 等数据上用二维可视化对比 cluster 与真实 labels；可视化分离不是独立于标签的证明。
- Fig. 3 检查 $\beta$ 敏感性。较大 $\beta$ 更强调保存 view 信息，论文推荐值与当前 `Runing.m` 示例值并不完全一致，实际应按数据验证。
- Fig. 4 检查 RNA feature 数 $K$，论文推荐 1000；ATAC 常固定 5000，ADT 保留全部。该选择同时影响 SNF 和 IB computation。
- Fig. 5 与一般 multi-view clustering 方法比较 ARI/NMI/AMI；监督 feature selection、已知 $k$ 和 restart 选择会影响公平性。
- Figs. 6–8 用 CellLine Sankey、cluster DEGs 与真实 label DEGs 验证 biological coherence。marker overlap 支持 cluster 可解释性，但真实标签也参与 $k$ 与评估，不是盲验证。

主图及图注嵌在 PMC paper Markdown 和本地 PDF，逐图解释见 `figure_analysis.md`。本地有 `supp_bbaf717.pdf`，但无独立 supplement Markdown；补充参数、general MVC 方法、runtime 和 feature analysis 的结论主要依赖论文引用，未在本机重跑。

### 输入、输出与实际运行

Python 脚本输出标准化矩阵、SNF similarity、可选 FS 矩阵和增强 $S'$。MATLAB `Runing.m` 读入三个 sparse views，读取 labels 得到 $k$，选择 $\theta,\beta$，运行 `MainIB` 并保存 cluster assignments。

当前脚本含大量硬编码 Windows 路径，例如 `D:/Dataset/...` 和 `D:/Experiment/...`；`main_IE-MOIF.py:34-37,61` 甚至固定 `Dataset='BMNC'` 与 label path，命令行参数不能完全控制路径。运行前必须重构路径和输出目录。环境跨 Python snfpy/scikit-learn 与 MATLAB，仓库没有容器或 lockfile。

### 版本与复现边界

本地 `.repo_source` 记录 `https://github.com/ZZUzy/scAMVIB` 提交 `ed8ebab928786ee40ad11ffb802337c4bc08c3fd`。代码目录无嵌套 `.git`，该值来自采集 manifest。

代码足以审计 SNF、IB assignment、softmax weight 和 ARI/NMI 主链，但数据未打包，路径需手工改，supervised FS 与已知 cluster 数依赖 ground truth，AMI/显著性和完整图表流程缺失。论文发表年份为 2026，但 DOI 后缀 `bbaf717` 和 PMC 页面应作为元数据来源；不能把仓库当前示例参数自动当作每个论文数据集最终设置。

### 最稳妥的使用建议

在真正无标签数据上关闭 chi-square FS，独立选择 cluster 数，按内部 objective/stability 而非 ARI 选 restart；同时报告 $\beta$ 与未公开公式中的 $\theta$。检查各 view 最终权重，避免增强 view 因与原 views 派生相关而重复计权。将 cluster 当作候选 cell states，并用 marker、独立标签和批次稳定性验证，而不是把高 benchmark 分数视为无偏的细胞类型发现。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## scAMVIB — Adaptive Multi-View Information Bottleneck for Multi-Omics Data Clustering

### Paper Information

| Field | Value |
|-------|-------|
| **Title** | Adaptive multi-view information bottleneck for multi-omics data clustering |
| **Authors** | Zhen Tian, Xiaojiao Wei, Zhengzheng Lou, Zhixia Teng, Shouli Fu |
| **Journal** | *Briefings in Bioinformatics*, 27(1):bbaf717 |
| **Year** | 2026 |
| **DOI** | [10.1093/bib/bbaf717](https://doi.org/10.1093/bib/bbaf717) |
| **Code** | [https://github.com/ZZUzy/scAMVIB](https://github.com/ZZUzy/scAMVIB) |
| **Language** | MATLAB (core) + Python (preprocessing) |

---

### Motivation & Novelty

#### Problem

Single-cell multi-omics technologies (e.g., 10x Multiome, CITE-seq) profile multiple molecular layers — transcriptome, epigenome, proteome — from the same cells. Integrating these modalities for cell clustering faces two challenges: (1) the duality between redundant and complementary information across modalities, and (2) view heterogeneity — different omics have different dimensionality, noise levels, and discriminative power, requiring differential weighting rather than equal treatment.

#### Limitations of Existing Approaches

- **Cobolt** (*Genome Biol*, 2021): Hierarchical multimodal VAE for joint RNA+ATAC representation, but applies uniform weighting across modalities.
- **scGDCC** (*IEEE BIBM*, 2024): Graph-based dual contrastive calibration for multi-omics; aligns pseudo-labels but doesn't adaptively weight views.
- **scAHVC** (*ISBRA*, 2024): Multi-view subspace clustering with tensor nuclear norm; captures consensus but uniform weighting.
- **scMIC** (*IEEE JBHI*, 2023): Deep multi-level information fusion; strong on CITE-seq but no explicit view weighting mechanism.
- **scEMC** (*Brief Bioinform*, 2024): Skip aggregation network for multi-modal clustering; effective but treats views equally.
- **DCCA** (*Nat Commun*, 2022): Multimodal deep learning for clustering; learns modality-specific representations but uniform fusion.

All above methods apply equal or fixed weighting to omics modalities, ignoring intrinsic differences in information content.

#### Unique Contributions

1. **Multi-view IB framework for multi-omics**: Reformulates single-cell multi-omics clustering as a multi-view information bottleneck problem, naturally handling the compression-preservation trade-off between redundancy and complementarity.
2. **Adaptive weighting via maximum entropy**: Dynamically assigns view weights proportional to information content, addressing view heterogeneity.
3. **SNF-based cross-omics feature enhancement**: Constructs a fused similarity network that propagates inter-omics associations into the feature space, creating an additional view that captures cross-omics relationships.

---

### Method Overview

scAMVIB operates in two stages:

**Stage 1: Preprocessing (Python)**
- Multi-omics data are MinMax-normalized per modality
- Similarity Network Fusion (SNF) constructs a fused cell-cell similarity network from all omics
- Optional chi-square feature selection reduces dimensionality
- The fused network multiplied by selected features produces an enhanced matrix $\mathbf{S}'$

**Stage 2: Multi-view IB Clustering (MATLAB)**
- Three views constructed: RNA, ATAC/ADT, and enhanced $\mathbf{S}'$
- Count matrices converted to probability distributions $p(y|x)$, $p(x)$
- Sequential IB optimization: each cell is drawn from its cluster and reassigned to the cluster minimizing the weighted multi-view merge cost (JS-divergence based)
- View weights are updated after each sweep using a softmax formula with a temperature parameter
- Process iterates until convergence; 10 random restarts, best selected by information preservation

See `doc_method.md` for detailed equations and algorithm walkthrough.

---

### Evaluation

#### Datasets

| Dataset | Platform | Modalities | Cells | Cell Types |
|---------|----------|-----------|-------|------------|
| CellLine | 10x | RNA + ATAC | 200 | 4 |
| CBMN | CITE-seq | RNA + ADT | 1,181 | 4+ |
| SLN111D1/D2 | CITE-seq | RNA + ADT | ~5,000 | 15+ |
| SLN208D1/D2 | CITE-seq | RNA + ADT | ~5,000 | 15+ |
| PBMC3k | 10x | RNA + ATAC | 3,000 | 7+ |
| Ma-2020 | SHARE-seq | RNA + ATAC | ~1,000 | 5+ |

#### Metrics

- **ARI** (Adjusted Rand Index): Measures agreement between predicted and true clustering, corrected for chance
- **NMI** (Normalized Mutual Information): Information-theoretic overlap measure
- **AMI** (Adjusted Mutual Information): Chance-corrected variant of NMI

#### Results Summary

scAMVIB achieves the best ARI on all 7 datasets in the multi-omics comparison (Table 1). Key results:

| Dataset | scAMVIB ARI | Best Baseline ARI | Baseline Method |
|---------|------------|-------------------|----------------|
| CellLine | **0.959** | 0.953 | DCCA |
| CBMN | **0.993** | 0.988 | scMIC |
| SLN111D1 | **0.559** | 0.462 | scDMSC |
| SLN208D2 | **0.631** | 0.618 | scDMSC |
| PBMC3k | **0.583** | 0.569 | scDMSC |

Improvements are most significant on complex datasets (SLN, PBMC) with many cell types. On simpler datasets (CellLine, CBMN), margins are smaller.

The learned view weights (Table 3) show biologically meaningful patterns: on CellLine, RNA receives weight ~1.0 (dominant modality); on CBMN, ADT receives weight ~0.96. The fused $\mathbf{S}'$ view consistently receives the lowest weight.

#### Ablation Study

Full 3-view integration outperforms all single-view and 2-view ablations across all datasets (Table 4), confirming the value of multi-view integration.

#### Biological Validation

On CellLine data: Sankey diagram shows near-perfect cluster-to-cell-type correspondence. Wilcoxon rank-sum DEG analysis identifies cluster-specific markers (e.g., MS4A1 for GM, PRAME for K562) consistent with known cell-type biology.

#### Computational Cost

scAMVIB is **significantly slower** than deep learning baselines on larger datasets:
- CellLine (200 cells): 22.9s (competitive)
- SLN datasets (5000+ cells): ~10,000s (2.8 hours) — roughly 10-100x slower than DCCA, scMIC, scEMC

This is the main practical limitation: the per-cell sequential sweep scales poorly with cell count.

---

### Reproducibility

**Rating: 3/5** (Moderate)

#### Strengths
- Code is publicly available on GitHub
- MATLAB code is self-contained with no external toolboxes
- Fixed random seed (=0) ensures deterministic results
- Example dataset (GSE100866) included in repo

#### Weaknesses
- **Two-language pipeline** (Python preprocessing → MATLAB clustering) creates a fragmented workflow
- **Supervised feature selection**: Chi-square FS requires ground truth labels, which is problematic for truly unsupervised use cases
- **Undocumented θ parameter**: A critical hyperparameter (softmax temperature for view weights) is not mentioned in the paper, making it impossible to reproduce exact results from the paper alone
- **Weight formula discrepancy**: Paper Eq.14 describes a different formula than what the code implements (see doc_code.md for details)
- **Hardcoded paths**: `Runing.m` uses Windows paths (`D:/Dataset/...`); users must modify
- **SNF parameters** (K=20, mu=0.5) are hardcoded and not discussed as tunable
- **Missing AMI**: Code only computes ARI and NMI; AMI reported in paper must be computed separately
- **No environment specification**: MATLAB version not specified; Python dependencies pinned to old versions (numpy 1.17, sklearn 0.23)

#### Practical Notes
1. Run Python `main_IE-MOIF.py` first to generate the enhanced matrix CSV
2. Edit `Runing.m` paths to match your data location
3. Requires tuning both β (IB trade-off) AND θ (weight temperature) — paper only discusses β
4. For datasets >5000 cells, expect multi-hour runtimes

---

### Strengths and Weaknesses

#### Strengths
- Clean theoretical framework combining IB principle with multi-view learning
- Adaptive weighting produces biologically interpretable results (Table 3)
- Strong clustering performance across diverse datasets and platforms
- Simple algorithm with no neural network training required
- Information-theoretic foundation provides principled compression-preservation trade-off

#### Weaknesses
- Poor scalability: O(L·N·k·ΣD_i) per restart, ~10,000s for 5000 cells
- Paper-code discrepancy in the weight formula undermines reproducibility
- Supervised feature selection step contradicts the unsupervised clustering framing
- Undocumented θ hyperparameter requires tuning but is absent from the paper
- Limited to paired multi-omics (same cells profiled across all modalities)
- No handling of missing modalities, batch effects, or variable cell numbers across modalities
- MATLAB implementation limits adoption in the predominantly Python single-cell ecosystem

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
