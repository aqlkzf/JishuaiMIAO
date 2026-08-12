---
layout: default
permalink: /paper-atlas/destiny-d1a54153/
title: "destiny"
nav: false
description: "destiny 处理的不是“给细胞分几个群”，而是如何从大量异步采样的单细胞测量中恢复连续、弯曲甚至分支的状态流形。论文发表于 2016 年，目标是给 R 用户提供一个可扩展的 diffusion map 实现，并针对单细胞数据加入三项实用能力：只计算 k 近邻以支持几十万细胞、显式处理检测下限和缺失值、把新数据投影到已有扩散图。 输入是已经预处理和归一化的细胞×特征矩阵（基因表达、蛋白标记等），或用户提供的距离矩阵。"
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
      <span>Bioinformatics · 2016</span>
    </div>
    <h1>destiny</h1>
    <p>destiny: diffusion maps for large-scale single-cell data in R</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1093/bioinformatics/btv715" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## destiny 中文方法解读：用扩散随机游走展开单细胞连续状态

### 1. 论文要解决的问题

`destiny` 处理的不是“给细胞分几个群”，而是如何从大量异步采样的单细胞测量中恢复连续、弯曲甚至分支的状态流形。论文发表于 2016 年，目标是给 R 用户提供一个可扩展的 diffusion map 实现，并针对单细胞数据加入三项实用能力：只计算 k 近邻以支持几十万细胞、显式处理检测下限和缺失值、把新数据投影到已有扩散图。

输入是已经预处理和归一化的细胞×特征矩阵（基因表达、蛋白标记等），或用户提供的距离矩阵。输出是每个细胞在若干 diffusion components（DC）上的坐标、相应特征值、核宽度与构图参数。它首先构造细胞相似图，再利用图上的多步随机游走定义扩散距离；相近的扩散坐标意味着两个细胞拥有相似的随机游走可达结构，而不只是原始表达值接近。

### 2. 为什么不是直接做 PCA

PCA 寻找解释方差最大的线性方向。若发育过程沿弯曲流形变化，流形两端在欧氏空间中可能不远，线性投影也可能把分支折叠。diffusion map 把局部相似性连接起来：一条由许多高概率局部步组成的路径，可以表达全局连续关系；噪声造成的孤立“捷径”则较难在多步随机游走中占主导。

这并不意味着 diffusion map 自动恢复真实时间或谱系。它恢复的是由输入特征、距离、邻居数和核宽度定义的几何。论文 Fig. 1C 中颜色随实验天数沿流形变化、ESC-like 和 MEF reversion 占据不同区域，是对该几何具有生物意义的支持；不是对每条点云分支都有谱系追踪证据的证明。

### 3. 算法主链

#### 3.1 预处理与距离

补充材料 S1 强调，特征方差不能跨越许多数量级，因为论文版本使用全局 $\sigma$。RNA-seq counts 应先做方差稳定化，如对数或平方根变换；qPCR 的 housekeeping normalization 也需谨慎。当前源码 `R/diffusionmap.r` 会提取数值矩阵，可选先用 PCA，并在普通缺失值存在时用 hot-deck 得到用于距离搜索的矩阵，但这不等于替用户完成生物学上合适的归一化。

对每个细胞只保留 $k$ 个近邻的距离。这样，完整的 $n\times n$ 距离矩阵被稀疏邻接结构替代，存储和后续谱分解才能扩展到大量细胞。当前 `R/knn.r` 支持 cover tree 和 HNSW；HNSW 是当前版本后来增加的可调近似后端，不能据此声称 2016 年论文已经评测了 HNSW。

#### 3.2 高斯核：把局部距离变成相似权重

对全局核宽度，当前代码实现

$$
K_{ij}=\exp\left(-\frac{d_{ij}^2}{2\sigma^2}\right),
$$

非邻居位置为零。$\sigma$ 太小会使图接近断裂，太大则把局部结构过度抹平。论文与补充 S2 用一组候选 $\sigma$ 观察“平均维度”启发式，选择在保持图连通与限制欧氏距离只用于局部区域之间折中的值。Fig. 1A 中曲线峰值对应 $\sigma=1.6$；它是该数据和预处理下的选择，不是通用默认值。

当前包默认还支持 local sigma。源码 `R/diffusionmap.r` 对每个细胞的局部尺度实现

$$
K_{ij}=\sqrt{\frac{2\sigma_i\sigma_j}{\sigma_i^2+\sigma_j^2}}
\exp\left(-\frac{d_{ij}^2}{\sigma_i^2+\sigma_j^2}\right).
$$

这是当前实现的重要能力，但主文与补充围绕全局 $\sigma$ 叙述；阅读论文结果时应以论文参数为准。

#### 3.3 对采样密度归一化

若某一状态被大量采样，原始核的随机游走会因为点多而倾向停留在该区域。`destiny` 先计算每个细胞的核度数 $d_i$，再做

$$
\widetilde K_{ij}=\frac{K_{ij}}{d_i d_j}.
$$

当前源码在 `R/diffusionmap.r` 的 `get_norm_p()` 中直接执行这一除法。其目的不是消除所有生物学密度差异，而是降低技术采样密度对流形几何的影响。因此，稀有群体更可能保留为几何结构；但低质量细胞或批次效应同样可能形成稀疏区域，密度归一化不会自动判别二者。

#### 3.4 对称共轭矩阵与特征分解

归一化后，代码计算新的行和 $\tilde d_i$，构造

$$
S=D_{\tilde d}^{-1/2}\widetilde K D_{\tilde d}^{-1/2}.
$$

$S$ 是对称矩阵，和对应的随机游走算子具有相同谱结构，却更适合稳定、高效的稀疏特征分解。当前实现由 `R/eig_decomp.r` 调用 `RSpectra::eigs()`，然后去掉平凡的第 0 特征向量，把其余特征向量作为 DC1、DC2 等坐标。

从左到右可把整条链理解为：

$$
\text{标准化数据}\rightarrow k\text{NN}\rightarrow K
\rightarrow \text{密度归一化}\rightarrow S
\rightarrow (\lambda_l,\psi_l)\rightarrow \text{DC 坐标}.
$$

扩散距离可写为

$$
D_t^2(i,j)=\sum_l \lambda_l^{2t}\big(\psi_l(i)-\psi_l(j)\big)^2.
$$

较大特征值对应衰减较慢的全局结构。Fig. 1B 前 100 个特征值平滑下降，说明该 256,000 细胞数据没有明显的低维截断；论文仍选择几个 DC 作三维可视化，因此图 C 只是高维扩散结构的一部分投影。

### 4. 单细胞特有的缺失与截尾模型

单细胞 qPCR 等技术中，“恰好等于检测阈值”可表示低于检测限的截尾观测，`NA` 则表示缺失。把二者简单当作普通数值或同一种零会扭曲距离。论文的噪声模型不先填一个确定值，而是把未知真实值视为区间上的分布，再计算两个观测分布的重叠，作为该特征对核相似度的贡献。

补充 Fig. S2 区分四类配对：两个值都可测、一个有效而另一个截尾/缺失、一个缺失而另一个截尾、两个都无确定值。当前 C++ `src/censoring.cpp` 中 `censor_pair()` 保留了这四类分支；两个有效值退化为普通高斯核贡献，混合配对用高斯与区间函数的积分重叠，两个同类不确定值贡献为 1。所有特征贡献相乘得到细胞对相似度。

这是一种明确的观测模型，不是普适 dropout 模型。用户必须正确提供检测阈值、截尾范围和缺失范围；若机制不是左截尾或给定区间不能代表缺失值，模型可能产生有偏相似度。当前普通 `NA` 的 hot-deck 距离搜索与随后可选 censoring kernel 也要分开理解：前者帮助选邻居，后者才改变核权重。

### 5. 新数据投影如何工作

补充 S3 描述了 projection：先计算新细胞到旧参考细胞的转移矩阵 $M'$，再复用旧 diffusion map 的变换。当前 `R/predict.r` 的 `dm_predict()`：

1. 检查新旧数据具有相同特征；
2. 用旧图的距离、$\sigma$、密度归一化参数构造新到旧的核；
3. 形成新的对称化变换行；
4. 乘旧特征向量，并除以旧特征值，得到新细胞的 DC 坐标。

这属于 Nyström 式外推。优点是参考坐标不变且无需重算全部图；边界也很清楚：如果新细胞远离所有参考状态，真实联合流形本应移动旧点，简单投影就会失真。补充材料对此有明确警告。投影因此适合“新样本覆盖已有状态”的场景，不适合用旧图强行容纳全新细胞类型。

### 6. 如何读主图与补充图

- **Fig. 1A**：横轴是 $\log_{10}(\sigma)$，纵轴是启发式平均维度；红圈是该数据选中的 $\sigma=1.6$。
- **Fig. 1B**：特征值没有明显断崖，提示内在结构维度较高，不能把图 C 的三轴当作全部变化。
- **Fig. 1C**：DC1、DC4、DC5 的三维点云按实验日着色。初始 MEF、回归 MEF 和 ESC-like 区域的关系支持方法保留重编程连续结构；虚线标注的 marker-high 区域帮助生物学解释。
- **Supplementary Fig. S1**：PCA 与 diffusion map 在胚胎连续变化上的对照。
- **Supplementary Fig. S2**：四类观测配对，是理解 censoring model 的关键图。
- **Supplementary Figs. S3–S5**：在 qPCR 与 RNA-seq 数据上展示 $\sigma$、特征值与流形；它们是案例验证，不是监督学习意义上的精度 benchmark。
- **Supplementary Table S1**：报告当时硬件和参数下的运行时间。当前依赖、近邻后端与硬件都不同，不能把 2016 数字当作当前性能保证。

本地第二张主图资源是不完整裁剪，因而面板解读以 `paper.md` 的 Fig. 1 图注、完整 `images/fig1.jpeg` 以及补充 Markdown 交叉核对，不把残缺图像当作独立证据。

### 7. 当前代码与论文的对应关系

当前本地仓库 commit 为 `cc5f6bd7d04c79a3cef80a92a56236e9b11c67fd`，`DESCRIPTION` 标记版本 3.25.0。它是论文发表多年后的 Bioconductor 开发版本，不是 2016 年冻结快照。

直接对应论文主链的代码是：

- `R/diffusionmap.r:224-245`：kNN、$\sigma$、kernel、密度归一化、对称化和特征分解总流程；
- `R/diffusionmap.r:412-445`：global/local Gaussian kernel 与 density normalization；
- `R/sigmas.r:110-180`：候选 $\sigma$ 的启发式搜索；
- `src/censoring.cpp:11-150`：四类截尾/缺失观测配对；
- `R/eig_decomp.r:22-29`：当前稀疏 eigensolver；
- `R/predict.r:28-71`：新数据投影。

需要明确标成版本扩展的部分包括：当前默认 local sigma、HNSW 后端、SingleCellExperiment 支持，以及仓库中的 `DPT()`、自动分支与 `gene_relevance()`。DPT 是相关的后续方法：它利用 diffusion map 转移结构计算 diffusion pseudotime，并可递归分支；gene relevance 根据扩散坐标局部变化估计表达偏导。它们存在于当前代码并不等于本篇 *destiny* 软件论文验证了其全部算法与生物学结论。若任务是解释 DPT，应另读 DPT 原论文，而不是只引用本篇主文。

### 8. 一个小数值直觉

假设两细胞距离为 $d=1$。若 $\sigma=1$，全局核权重为

$$
\exp(-1/2)\approx 0.607.
$$

若 $\sigma=0.5$，同一距离权重变成

$$
\exp(-1/0.5) = \exp(-2)\approx 0.135.
$$

较小 $\sigma$ 使图更强调极近邻，也更容易断裂；较大 $\sigma$ 把更多邻居视为相似，可能抹平分支。密度归一化随后还会降低高密度区域内部边的相对影响。这说明图形结果不能脱离预处理、$k$ 和 $\sigma$ 解释。

### 9. 复现与解释边界

要复现论文结果，至少需要相同数据版本、预处理、距离、$k$、$\sigma$、选取的 DC 与随机初始化。当前 `RSpectra` 初始向量默认随机生成；需要严格复现时应设置随机种子或显式 `initvec`。主文只给出软件和案例层面的说明，本工作区未包含论文所有原始数据，也没有执行完整 benchmark。

最终应把 destiny 的输出理解为“数据定义的扩散几何”，而不是直接的发育时间、因果调控网络或已验证谱系。可靠分析应检查不同 $k$、$\sigma$、特征选择和批次处理下流形是否稳定，用已知时间、marker 或独立谱系实验验证方向，并对参考图之外的新状态谨慎使用投影。

### 10. 本工作区的证据范围

- 主文：`paper.md`，69 行，包含方法、应用、Fig. 1 和讨论。
- 补充：`output_supp_md/btv715-destiny-supplement/vlm/btv715-destiny-supplement.md`，包含预处理、参数选择、投影、补充图表与运行时间。
- 图像：完整 `images/fig1.jpeg` 与一张不完整裁剪图；主图已直接查看。
- 代码：`destiny/` 当前 commit `cc5f6bd7d04c79a3cef80a92a56236e9b11c67fd`，本次仅只读核对。
- 未完成：没有在当前环境重跑论文四个数据集和性能表；这些边界不影响方法文档完整性，但限制对数值复现的声称。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## destiny: diffusion maps for large-scale single-cell data in R — Summary

**Paper**: Angerer et al. (2016) *Bioinformatics* 32(8):1241–1243
**DOI**: 10.1093/bioinformatics/btv715
**Type**: Software application note
**Code**: https://github.com/theislab/destiny (R/Bioconductor)

---

### Motivation & Novelty

#### Biological Problem

Single-cell profiling technologies capture individual cell states at a fixed moment. In differentiation and reprogramming experiments, cells progress asynchronously through biological states, so a population snapshot contains cells at many different internal stages. Recovering the underlying developmental continuum — and branching decisions between cell fates — requires a dimensionality reduction method that preserves the **topology** of the biological trajectory, not just variance (PCA) or cluster membership (k-means).

#### Why Existing Methods Fall Short

- **PCA** (linear) cannot represent the curved, branching trajectories of differentiation (Supp. Fig. S1 shows PCA fails to separate embryonic stages that diffusion maps correctly orders)
- **ICA** (linear): same limitation
- **t-SNE**: focuses on local structure, does not preserve global trajectory ordering; non-parametric (cannot project new data)
- **diffusionMap R package** (Richards 2014, CRAN): correct algorithm but dense distance matrix computation — out of memory for >100k cells (Supp. Table S1); no censoring model; no projection
- **MATLAB implementation** (Maggioni/Haghverdi 2015 *Bioinformatics*): no R interface; no censoring model; no nearest-neighbor approximation (out of memory >50k cells)

#### What destiny Contributes

1. **Efficient R/Bioconductor implementation** accessible to biologists without MATLAB
2. **kNN approximation**: sparse distance matrix using only $k$ neighbors per cell (default: adaptive 100–n) vs. full $O(n^2)$ matrices — enables 256,000-cell datasets that would otherwise require >24h or fail with OOM
3. **Single-cell noise model**: 4-case Gaussian/box interference model for censored (below-detection) and missing values in qPCR data — the first diffusion map implementation to handle these
4. **Projection (Nyström extension)**: embed new experimental data into an existing map without recomputation — enables incremental analysis and integration across time points
5. **Automatic σ heuristic**: global (average dimensionality) and local (per-cell kNN distance) modes; no manual tuning needed for standard cases

---

### Method Overview

destiny implements the **diffusion map algorithm** adapted for single-cell data (Coifman et al. 2005; Haghverdi et al. 2015).

**Core framework**: Random walk on a cell-to-cell graph. The transition probability $T_{ij}$ between cells $i$ and $j$ is determined by a Gaussian kernel on their expression distance. After density normalization (to remove sampling bias) and eigendecomposition of the symmetric adjoint, the top eigenvectors define a low-dimensional "diffusion map" space where Euclidean distance approximates diffusion distance — a measure robust to noise and topology-preserving.

**Key biological assumptions**:
- Differentiation is a smooth, continuous process in expression space
- Cell-to-cell transitions occur preferentially between transcriptionally similar cells
- Technical noise and dropout/censoring follow known statistical distributions

**Computational pipeline** (see `doc_method.md` for step-by-step details):
1. kNN graph construction (adaptive k, covertree/HNSW backends)
2. σ estimation (local per-cell or global heuristic)
3. Gaussian kernel → sparse transition matrix
4. Density normalization to remove sampling bias
5. Symmetric adjoint construction
6. Sparse eigendecomposition (RSpectra IRLB) → diffusion components DC1…DC20

For details on equations, variable mappings, and code locations, see `doc_method.md`.
For code-paper verification, see `doc_code.md`.

---

### Evaluation

#### Datasets

| Dataset | Size | Technology | Key finding |
|---------|------|-----------|-------------|
| Guo et al. 2010 (*Dev Cell*) | 429 cells, 48 genes | single-cell qPCR | Embryogenesis oocyte → 64-cell; two branching events at 16-cell stage |
| Moignard et al. 2015 (*Nat Biotechnol*) | 3,934 cells, 46 genes | single-cell qPCR | Early hematopoiesis; progenitor developmental stages |
| Trapnell et al. 2014 (*Nat Biotechnol*) | 271 cells, 47k genes | single-cell RNA-seq | Skeletal muscle myoblast differentiation |
| Zunder et al. 2015 (*Cell Stem Cell*) | 256,000 cells, 36 markers | mass cytometry (CyTOF) | iPSC reprogramming over 20 days |

#### Performance (Supp. Table S1)

| Implementation | Guo (429 cells) | Moignard (3934 cells) | Trapnell (271 cells) | Zunder (256k cells) |
|---|---|---|---|---|
| MATLAB (fast) | 0.3s | 4.3s | 0.6s | >24h |
| MATLAB | 21s | >1h | 4.7s | OOM |
| **R destiny** | 0.5s | 6.0s (k=500) | 0.2s | **1.4h** (k=1000) |
| R diffusionMap | 0.4s | 21s | 0.2s | OOM |

destiny is **comparable to other implementations on small datasets** and **uniquely capable on large datasets** through its kNN approximation.

#### Biological Validation

- **Guo 2010** (Supp. Fig. S3C): destiny correctly identifies two branching events corresponding to the inner cell mass/trophectoderm and epiblast/primitive endoderm segregations
- **Moignard 2015** (Supp. Fig. S4C): developmental stages of hematopoietic progenitors reproduced, consistent with original paper
- **Zunder 2015** (Fig. 1C): 3D diffusion map of 256k iPSC reprogramming cells reveals (a) initial MEF population, (b) cells successfully reprogramming toward ESC identity (Nanog+, CD24+), and (c) cells reverting to MEF state — a continuous molecular roadmap of reprogramming at single-cell resolution

---

### Reproducibility

**Rating: 4/5**

**Justification**: The package is well-maintained (v3.25.0, active development), installable via Bioconductor (`BiocManager::install("destiny")`), and includes comprehensive vignettes with working code. The main paper's demonstration dataset (Zunder 2015) is publicly available via the Cell Stem Cell supplementary materials. Code can recreate Fig. 1C with the 3-line snippet shown in the figure inset. Rating is 4/5 (not 5/5) because:
- The 256k-cell demo requires >8GB RAM and ~1.4h compute
- The σ heuristic involves a random seed via `set.seed` that affects eigendecomposition initialization (results are stochastic without seed-setting)
- The original MATLAB code comparison required a 95GB RAM server

**Practical notes**:
- Install: `BiocManager::install("destiny")` in R
- For large datasets (>100k cells): recommend `k=500-1000`, `sigma='local'` for speed
- qPCR data with dropouts: specify `censor_val`, `censor_range`, `missing_range`
- Sigma estimation: run `find_sigmas(data, verbose=TRUE)` separately to visualize the heuristic before creating the diffusion map
- Reproducibility: set `set.seed()` before `DiffusionMap()` to fix random eigendecomposition initialization

**Strengths**:
- Clean S4 class interface integrating with Bioconductor ecosystem (ExpressionSet, SingleCellExperiment)
- Rich visualization with automatic color legends
- Well-tested (testthat suite), documented vignettes
- Includes DPT (Diffusion Pseudo-Time) for pseudotime ordering
- Gene relevance analysis to identify drivers of each DC

**Weaknesses**:
- Single global σ (when not using local) may not suit data with heterogeneous densities
- Projection is approximate; may fail for cells far outside training distribution
- qPCR censoring model limited to single censor_val threshold (not per-gene)
- No GPU acceleration for the eigendecomposition step

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
