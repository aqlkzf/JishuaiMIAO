---
layout: default
permalink: /paper-atlas/magic-afe98eb1/
title: "MAGIC"
nav: false
description: "单细胞 RNA 测序通常只捕获每个细胞真实转录本的一小部分。低表达基因即使真实存在，也常被观测为零，进而破坏基因–基因关系。MAGIC（Markov affinity-based graph imputation of cells）的基本假设是：细胞状态受调控网络约束，位于一个低维流形上；相似状态的细胞应共享表达信息。 因此 MAGIC 不为每个零单独拟合一个概率模型。"
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
      <span>Cell · 2018</span>
    </div>
    <h1>MAGIC</h1>
    <p>Recovering Gene Interactions from Single-Cell Data Using Data Diffusion</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2018.05.061" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MAGIC 中文方法解读：沿单细胞状态流形扩散，而不是逐基因猜零值

### 1. MAGIC 要修复的不是“所有零”，而是采样不足

单细胞 RNA 测序通常只捕获每个细胞真实转录本的一小部分。低表达基因即使真实存在，也常被观测为零，进而破坏基因–基因关系。MAGIC（Markov affinity-based graph imputation of cells）的基本假设是：细胞状态受调控网络约束，位于一个低维流形上；相似状态的细胞应共享表达信息。

因此 MAGIC 不为每个零单独拟合一个概率模型。它先在“细胞 × 基因”矩阵上建立细胞图，再让表达沿图进行有限步随机游走扩散。输出是平滑后的每细胞表达向量，适合恢复低频、结构化的生物趋势；不保证恢复随机的细胞内波动。

### 2. Figure 1：六步读懂主算法

Figure 1（`paper source/images/gr1_lrg.jpg`）从上到下是完整数据流：

1. 输入原始细胞–基因矩阵 $D$；
2. 在 PCA 空间计算细胞间距离；
3. 用自适应核把距离转成 affinity $A$；
4. 行归一化得到 Markov 转移矩阵 $M$；
5. 计算 $M^t$，得到长度为 $t$ 的随机游走概率；
6. 用

$$
D_{\mathrm{imputed}}=M^tD
$$

把每个细胞的表达替换为其扩散邻域的加权组合。

关键点是 PCA 只用于构图；论文明确写明最终乘法使用 PCA 前、已做库大小归一化的基因矩阵，所以输出仍保持单基因分辨率。

### 3. 预处理：先消除测序深度，再用 PCA 稳定距离

原论文算法先将每个细胞的总计数归一到所有细胞库大小的中位数：

$$
D_{norm}(i,j)=\frac{D(i,j)}{\sum_kD(i,k)}\operatorname{median}(\mathrm{Libsize}).
$$

随后在基因维做 PCA，以减少稀疏噪声对邻居搜索的影响。当前 Python `magic.py:358-449` 把数据直接交给 `graphtools.Graph`，只在基因列全零时警告，并不执行库大小归一化；Python 用户必须预先处理。MATLAB `compute_operator.m:55-65` 则包含库大小归一化和可选 log transform。

这意味着同样写 `MAGIC().fit_transform(X)`，输入 raw counts 与输入已标准化矩阵不是同一算法条件。复现时必须记录传入矩阵的尺度与变换。

### 4. 自适应核为什么比固定宽度重要

细胞流形不同区域密度不均。固定核宽度会让高密度区域过度连通、低密度区域断裂。MAGIC 对每个细胞 $i$ 用其第 $k_a$ 个邻居距离作为局部尺度 $\sigma_i$，再把距离映射为 affinity。经加法对称化和行归一化：

$$
A\leftarrow A+A^T,\qquad
M(i,j)=\frac{A(i,j)}{\sum_kA(i,k)}.
$$

$M(i,j)$ 是一步从细胞 $i$ 转到 $j$ 的概率。细胞到自身距离为零，因此自环在归一化前具有最高权重，保留自身观测的贡献。

Supplementary Figure S1（`figs1_lrg.jpg`）直接比较固定与自适应核：固定核随扩散把数据压向高密度区域，自适应核更好保存分支形状；合成三臂流形也只有自适应版本恢复正确几何。这是 MAGIC 能沿密度方向平滑、而非简单全局平均的关键。

当前 Python 代码把构图委托给 `graphtools.Graph`（`magic.py:385-447`），默认 `knn=5`、`knn_max=3*knn=15`、`decay=1`。MATLAB 源码显式展示 adaptive distance、对称化和 Markov 归一化（`compute_operator.m:80-110`）。因此 Python 的核心 operator 可从调用与 `diff_op` 验证，但具体 kernel 细节还受安装的 graphtools 版本影响。

### 5. 扩散时间 $t$：去噪与过度平滑的旋钮

$M^t(i,j)$ 表示从细胞 $i$ 出发走 $t$ 步到达 $j$ 的概率。小 $t$ 只共享局部邻居；适中 $t$ 会削弱偶然边并连接沿流形相通的细胞；过大 $t$ 则会把真实的低频生物差异也磨平。

Figure S1C–D 显示两阶段行为：早期相邻扩散结果快速变化，对应去除高频噪声；随后变化趋稳，再继续扩散进入 smoothing regime。噪声越大，最佳 $t$ 越大；合成树数据中，由变化拐点选出的 $t$ 与对 ground truth 的最佳恢复基本对应。

论文 Methods 用相邻 $D_t,D_{t-1}$ 的 $R^2$ 变化，低于 0.05 后取第二个 $t$。当前代码已经不同：Python `magic.py:655-689,691-803` 和 MATLAB `compute_optimal_t.m:22-59` 都计算 Procrustes disparity，以 0.001 为阈值。Python 在首次低于阈值时设 `t_opt=i+1`，并在超过 500 个基因时随机抽 500 个基因估计 $t$。这是后续软件版本的实现边界，不应写成原论文公式的逐字实现。

### 6. Python 代码如何真正执行 $M^tD$

`MAGIC.fit()` 创建并缓存 graph/diffusion operator；`transform()` 选择基因和 exact/approximate solver；`_impute()` 执行扩散。

`magic.py:748-770` 有两条等价目标但不同内存行为的路径：

- 当 $t$ 已给定且 operator 维度较小，先用 `np.linalg.matrix_power(M,t)` 再乘数据；
- 其他情况逐步执行 `data_imputed = M.dot(data_imputed)`，特别适合 `t='auto'`，因为每一步都能检查收敛。

exact solver 在原基因空间扩散；approximate solver 在 PCA 空间扩散后 inverse transform（`magic.py:576-601`），速度更快，但逆变换可能产生负值。默认构造器是 `t=3`，并非自动选 $t$；只有显式传 `t='auto'` 才执行收敛选择。

### 7. 原论文最后的 99 分位重标定与当前 Python 差异

论文在扩散后把每个基因的最大插补值缩放到原始数据该基因的第 99 百分位：

$$
D_{rescaled}(i,j)=D_{imputed}(i,j)
\frac{P_{99}(D_{\cdot j})}{\max_i D_{imputed}(i,j)}.
$$

这一操作补偿扩散把分子质量摊到更多非零位置后造成的幅度下降。当前 Python `magic.py` 的主类没有这一步，MATLAB当前主入口也没有看到同一重标定路径。因此应该把它视为论文算法描述，而不是当前 Python API 输出的保证。

### 8. Figure 2 说明恢复了什么

Figure 2（`gr2_lrg.jpg`）用骨髓细胞展示三个层次：

- 热图中稀疏的经典标记在 MAGIC 后形成与细胞簇一致的连续表达块；
- 二维/三维散点随 $t=0,1,3,7$ 逐步显出造血分化轨迹；
- 与独立 FACS 蛋白测量的相关性提高：CD34 从 0.39 到 0.73，FCGR3 从 0.55 到 0.88。

这类外部蛋白对应支持 MAGIC 恢复了部分真实结构，而不只是让图变得更光滑。但标记阳性比例大幅提高不等同于逐细胞“测到了原本缺失的真实分子”；输出是邻域条件下的推断值。

### 9. 从插补到基因关系：kNN-DREMI 是下游分析

论文用 MAGIC 后的表达计算 kNN-DREMI，以捕捉非线性、条件化的基因关系。它先在细网格做 kNN 密度估计，再聚合到 20×20 粗网格并列归一化成条件密度（DREVI），最后计算条件互信息。论文默认 $k=10$、细网格 60×60、粗网格 20×20。

当前 Python MAGIC 将该计算委托给 `scprep.stats.knnDREMI`，不是 `magic.py` 自己实现；archetype/PCHA、伪时间基因排序、ZEB1 靶点和 ATAC-seq 验证也都是下游分析，不属于核心插补器。不能把这些结果理解成 `fit_transform()` 自动输出的调控网络。

### 10. 代码与论文对应边界

| 证据项 | 直接实现 | 判断 |
|---|---|---|
| PCA/图构建入口 | `magic.py:358-449` | Exact/委托 graphtools |
| $k_{max}=3k$ | `magic.py:163-172` | Exact |
| $M^tD$ | `magic.py:748-770` | Exact |
| 自动 $t$ | `magic.py:655-803` | Partial；Procrustes 替代论文 $R^2$ |
| 库大小归一化 | MATLAB `compute_operator.m:55-65` | Python Not found |
| 99 分位重标定 | 论文 Methods | 当前 Python Not found |
| kNN-DREMI | 委托 scprep | Partial/external dependency |
| PCHA/ATAC 等下游分析 | 仓库未包含完整实现 | Not found |

### 11. 使用与解释限制

- MAGIC 依赖大量细胞共同定义流形；样本过少或关键状态缺失时无法创造可靠邻域。
- 过大的 $k$ 或 $t$ 会过度平滑、合并真实差异，Figure S3 也显示极端参数下相关性下降。
- 它更擅长恢复与主要流形相关的结构化基因；随机、瞬时或罕见状态信号可能被削弱。
- 插补值不是原始测量值，不适合在不保留 raw counts 的情况下直接当作测序证据。
- 下游差异表达、相关网络或因果结论必须评估插补诱导的依赖；MAGIC 展示的是数据支持的关系，不等同于调控因果。
- Python、MATLAB和论文算法在归一化、$t$ 选择与重标定上有版本差异，复现必须记录语言、包版本、预处理和参数。

一句话概括：MAGIC 通过细胞图上的有限步 Markov 扩散，让每个细胞从沿同一生物状态流形的邻居借信息；它恢复的是结构化表达趋势，而不是对每个零值给出确定的分子真相。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MAGIC Summary

**Paper**: Recovering Gene Interactions from Single-Cell Data Using Data Diffusion
**Authors**: van Dijk et al.
**Journal**: Cell 174, 716–729 (2018)
**DOI**: 10.1016/j.cell.2018.05.061
**Code**: https://github.com/KrishnaswamyLab/MAGIC

---

### Motivation & Novelty

**Biological problem**: scRNA-seq captures only 5–15% of each cell's transcriptome. This stochastic under-sampling ("dropout") makes gene-gene relationships invisible — even known regulatory interactions (e.g., ZEB1 activating VIM during EMT) are undetectable in raw data. Most cells appear to express zero for any given gene, even when the gene is actually expressed.

**Limitations of existing approaches**:
- **Cluster-based aggregation** (e.g., Seurat, Phenograph): collapses thousands of cells into a few clusters, losing single-cell resolution
- **PCA / meta-genes**: aggregates genes, losing single-gene resolution
- **kNN-imputation**: bluntly averages over k nearest neighbors in raw data — unreliable because raw nearest neighbors are distorted by dropout
- **Diffusion maps** (Haghverdi et al., *Bioinformatics* 2015; *Nat. Methods* 2016): find diffusion components for pseudotime, but cannot restore the original gene expression matrix or reveal gene-gene relationships
- **LRA** (Achlioptas & McSherry, *J. ACM* 2007): linear low-rank approximation, cannot capture non-linear manifold structure
- **NNMC** (Candes & Recht, *Commun. ACM* 2012): trusts non-zero values and only imputes zeros — wrong for scRNA-seq where even non-zero values are under-counted

**What's new**:
1. **Diffusion-based imputation**: uses the diffusion operator (Markov affinity matrix raised to power $t$) to share information between cells along the data manifold, not just direct neighbors
2. **Adaptive kernel**: equalizes effective neighborhood size across density variations, preserving fine structure in rare cell populations
3. **kNN-DREMI**: adapts DREMI (Krishnaswamy et al., *Science* 2014) to scRNA-seq using kNN density estimation, enabling quantification of non-linear gene-gene dependencies
4. **Manifold restoration**: unlike dimensionality reduction methods, MAGIC restores the original high-dimensional gene expression matrix to its underlying manifold

---

### Method Overview

MAGIC takes a cells × genes count matrix and returns an imputed matrix where dropout and noise are corrected via data diffusion.

**Pipeline**:
1. **Library size normalization**: equalize total counts per cell
2. **PCA**: reduce to ~20–100 robust dimensions (retaining ~70% variance)
3. **Adaptive affinity graph**: compute cell-cell affinities using a Gaussian kernel with locally adaptive bandwidth ($\sigma(i)$ = distance to $k_a$-th neighbor); symmetrize; Markov-normalize to get transition matrix $M$
4. **Diffusion**: compute $D_{imputed} = M^t \cdot D$; optimal $t$ selected by Procrustes convergence
5. **Rescaling**: restore expression scale to 99th percentile of original data

**Key biological assumption**: cell phenotypes lie on a low-dimensional manifold in gene expression space. Dropout is high-frequency noise; biological signals are low-frequency. Diffusion acts as a low-pass filter on the graph spectrum.

**Downstream**: kNN-DREMI quantifies non-linear gene-gene dependencies post-imputation; archetype analysis (PCHA) identifies extreme phenotypic states.

---

### Evaluation

#### Datasets
| Dataset | Technology | Cells | Biological System |
|---|---|---|---|
| Mouse bone marrow | MARS-seq2 | ~10,000 | Hematopoiesis |
| Mouse retina | Drop-seq | ~27,000 | Retinal bipolar neurons |
| Mouse cortex | Smart-seq2 | 3,005 | Cortex/hippocampus neurons |
| HMLE EMT | inDrops | 7,523 | Epithelial-to-mesenchymal transition |
| HMLE ZEB1 induction | inDrops | 3,500 | ZEB1-driven EMT validation |

#### Key Results
- **Bone marrow**: CD14 detection in monocytes: 1.6% → 94% after MAGIC; FACS-mRNA correlation: CD34 0.39 → 0.73, FCGR3 0.55 → 0.88
- **Cluster preservation**: Rand index 0.93 (retina); 0.89–0.94 at 90% dropout (cortex)
- **Synthetic validation**: R² from 7% → 43% (90% dropout); gene-gene correlation R² from 0.12 → 0.65
- **EMT**: 79% of cells in intermediate states revealed; 10 archetypes identified
- **TF target prediction**: 268/292 TFs (92%) have significant overlap with ATAC-seq targets (FDR-corrected hypergeometric test); 372/418 TFs (89%) have significantly higher DREMI with ATAC-seq targets (KS test, p<0.05)
- **ZEB1 targets**: 1,085 predicted targets validated with p=3.1×10⁻⁷³ against background

#### Comparison to Other Methods
| Method | Bone Marrow | EMT | Notes |
|---|---|---|---|
| MAGIC | Recovers all known relationships | Reveals continuum + archetypes | Best overall |
| kNN-imputation | Fails to recover relationships | Fails | Blunt averaging |
| Diffusion maps smoothing | Correct for DC1-aligned genes only | Fails for complex structure | One gene at a time |
| LRA | Partial recovery | Fails for non-linear structure | Linear only |
| NNMC | Incorrect correlations | Fails | Trusts non-zeros |

---

### Reproducibility

**Rating: 4/5**

**Justification**: Python, MATLAB, and R implementations are publicly available and actively maintained. The Python package (`magic-impute`) is pip-installable. Tutorial notebooks for both EMT and bone marrow datasets are provided. The EMT scRNA-seq and ATAC-seq data are deposited at GEO (GSE114397). Main results are reproducible with provided code and data.

**Strengths**:
- Three language implementations (Python, MATLAB, R)
- sklearn-compatible API (`fit`, `transform`, `fit_transform`)
- Tutorial notebooks with real data
- Data deposited at GEO

**Weaknesses**:
- Python MAGIC does NOT perform library size normalization — users must normalize beforehand (not clearly documented)
- Archetype analysis (key EMT result) is not in the MAGIC repo; requires separate PCHA implementation
- Default parameters differ between Python (knn=5) and MATLAB (ka=4, k=12) — may give different results
- Optimal t criterion differs from paper (Procrustes vs R-sq)
- The "approximate" solver can return negative values

**Environment setup**:
```bash
pip install magic-impute scprep
# or
pip install git+https://github.com/KrishnaswamyLab/MAGIC.git#subdirectory=python
```

**Common pitfalls**:
1. Forgetting to library-normalize before calling MAGIC (Python)
2. Using MAGIC output for differential expression with tools that assume sparsity (will over-estimate DEGs)
3. Running diffusion map analysis on MAGIC output (leads to over-smoothing; run DM on raw data)
4. Treating very low post-MAGIC values as expressed (recommend treating near-zero as zero)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
