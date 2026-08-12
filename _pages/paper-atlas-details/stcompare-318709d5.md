---
layout: default
permalink: /paper-atlas/stcompare-318709d5/
title: "STcompare"
nav: false
description: "STcompare 用于比较两张结构对应的组织切片。它先要求两张切片在同一像素网格上对齐，然后为每个基因提供两个互补量：空间相关检验判断图案方向是否保持或反转；空间 fold-change 相似度判断对应位置的表达量是否仍在给定倍数范围内。 论文是 2025 年 bioRxiv 预印本，尚未经同行评审。以下解读以本地 51 页论文 PDF/OCR、主图与补充内容、以及 commit 6b27d1d... 的 R 源码为边界。"
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
      <span>Spatially Variable Genes</span>
      <span>bioRxiv · 2025</span>
    </div>
    <h1>STcompare</h1>
    <p>STcompare: comparative spatial transcriptomics data analysis of structurally matched tissues to characterize differentially spatially patterned genes</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2025.11.21.689847" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STcompare：比较“空间图案是否改变”，而不只是平均表达是否改变

### 一句话理解

STcompare 用于比较两张结构对应的组织切片。它先要求两张切片在同一像素网格上对齐，然后为每个基因提供两个互补量：空间相关检验判断图案方向是否保持或反转；空间 fold-change 相似度判断对应位置的表达量是否仍在给定倍数范围内。

论文是 2025 年 bioRxiv 预印本，尚未经同行评审。以下解读以本地 51 页论文 PDF/OCR、主图与补充内容、以及 commit `6b27d1d...` 的 R 源码为边界。

### 1. 为什么普通差异表达回答不了这个问题

非空间 DGE 把每张组织压缩成表达值分布或均值。于是会出现两种错位：

- 两个样本平均表达相同，但高表达区域从组织中心移到边缘；DGE 可能说“无差异”，空间图案却已改变。
- 两个样本图案位置完全一致，但一个整体高两倍；DGE 会说“差异”，空间组织关系却保持。

STcompare 不替代 DGE，而是补充两个空间问题：对应位置的涨跌是否一致？即使形状一致，幅度又是否一致？

### 2. 前提比统计检验本身更重要

输入不是任意两张空间数据。两份 `SpatialExperiment` 必须经过：

1. 结构配准，例如 STalign，使共同解剖结构落到同一坐标系；
2. 栅格化，例如 SEraster，使相同 pixel ID 真正表示匹配空间位置；
3. 合理的分辨率和归一化，使两个像素值可比较。

这些步骤都在 STcompare 包外。若像素 $i$ 在样本 X 表示皮质、在 Y 却表示髓质，负相关可能只是配准错误。像素大小也控制信号与噪声的平衡：过细会稀疏，过粗会抹平局部变化。

源码 `getGenePixelDF()` 只取两个对象共同的列名，并按这些 pixel IDs 抽取表达；它不会检查组织学对应是否正确。

### 3. 空间相关检验

对某基因在 $N$ 个匹配位置的表达向量 $X=(x_1,\ldots,x_N)$ 与 $Y=(y_1,\ldots,y_N)$，先计算 Pearson 相关

$$
r=\frac{\sum_i(x_i-\bar x)(y_i-\bar y)}
{\sqrt{\sum_i(x_i-\bar x)^2}\sqrt{\sum_i(y_i-\bar y)^2}}.
$$

论文的分类是：

- $r<0$ 且经验 $p_E<0.05$：differentially spatially patterned gene（DSPG），两张图在匹配位置呈反向关系；
- $r>0$ 且 $p_E<0.05$：显著相似空间图案；
- 不显著：证据不足，不能直接解释为“图案完全不同”。

注意，DSPG 的定义很严格：只把显著负相关归为差异空间图案。零相关、局部位移、旋转残差或非线性改变即使生物学重要，也可能只落在“不显著”。

### 4. 为什么普通 Pearson p 值会严重失真

相邻像素往往相似，样本不是独立同分布。普通相关检验把 $N$ 个像素当作 $N$ 个独立观测，会高估有效样本量。论文模拟 100 个彼此独立但各自具有空间自相关的随机场，9900 个有向非自身配对中，解析 p 值的假阳性率达到 0.50；考虑空间自相关的经验检验将其降到 0.04。

这说明关键创新不是 Pearson $r$，而是怎样构造“保持 X 自相关程度、但与 Y 独立”的零分布。

### 5. 变异函数匹配的经验零分布

对 X 重复 $B$ 次，默认 $B=100$：

1. 随机打乱 X 在空间位置上的取值，切断原有图案；
2. 对打乱值使用 Gaussian `locfit` 平滑；候选 $\delta$ 表示局部核覆盖的邻居比例；
3. 计算每个平滑结果的 variogram，并选择使其最接近原始 X variogram 的 $\delta^*$；
4. 得到保留近似空间自相关尺度、但不再与 Y 配对的 $X_j$；
5. 计算 $r_j=cor(X_j,Y)$。

经验双侧 p 值为

$$
p_E^X=\frac1B\sum_{j=1}^B\mathbf1(|r_j|>|r|).
$$

源码再交换 X、Y，重复整套过程得到 $p_E^Y$。论文报告更保守的

$$
p_E=\max(p_E^X,p_E^Y).
$$

当前公开函数只返回 `pValuePermuteX` 与 `pValuePermuteY` 两列，没有自动计算最大值；用户必须显式 `pmax()`。若直接任选一列，分类会比论文规则更宽松。

#### 一个数值直觉

假设观察到 $r=-0.45$，100 个空间保持置换中有 3 个满足 $|r_j|>0.45$，则 $p_E^X=0.03$。交换后有 7 个更极端，$p_E^Y=0.07$。论文规则取 0.07，所以该基因不应在 0.05 阈值下叫 DSPG。

默认 $B=100$ 时 p 值分辨率是 0.01；`p=0` 只表示 100 次中没有更极端值，不表示真实概率严格为零。大量基因检验时还应考虑多重检验，但论文示例主要使用未校正的经验阈值，不能自动解释为严格控制 FDR。

### 6. 源码中比论文文字更详细的变异函数匹配

`matchingVariograms()` 不只是“打乱后平滑”。对每个候选 $\delta$，代码还在线性回归中用目标 variogram 对置换 variogram 做尺度拟合，再以斜率缩放平滑场并按截距注入噪声，最后比较 variogram 残差平方和。这一 rescaling 是实现的一部分，但论文主叙述较简化。

当位置数超过 1000 时，源码随机抽 1000 个位置估计 variogram，以限制两两距离计算；平滑和最终相关仍使用完整位置。默认只比较距离分布 25% 分位以内的 variogram，因为远距离 pair 少、估计不稳定。

$\delta$ 不是物理距离，而是 locfit 的最近邻比例。小 $\delta$ 保留细尺度结构，大 $\delta$ 产生更平滑的场。若最优值频繁卡在搜索边界，应扩展搜索范围。

### 7. 空间 fold-change 相似度

相关性不受整体尺度影响。若 $Y=4X$，相关可能接近 1，但幅度已改变。因此第二个检验逐像素计算

$$
z_i=\log_2\frac{y_i}{x_i}.
$$

默认阈值 $b=1$：

$$
f(x_i,y_i)=\mathbf1(|z_i|\le b),\qquad
S=\frac1{N_q}\sum_{i=1}^{N_q}f(x_i,y_i).
$$

$S$ 是有效像素中落在两倍范围内的比例。代码也分别给出 $z_i<-1$（X 更高）和 $z_i>1$（Y 更高）的比例与 pixel IDs，便于在组织图上标色。

为防低表达噪声主导：每个样本默认以该基因 5% quantile 为阈值，只保留 $x_i>t_1$ 或 $y_i>t_2$ 的位置；若不足全部共同位置的 10%，返回 NA；精确零被替换为 0.0001 以避免无穷 log fold-change。

源码存在一个报告细节：用户显式提供 `t1/t2` 时，过滤使用提供值，但输出表随后又把阈值重算为默认 quantile，因此输出记录可能与实际使用阈值不一致。

### 8. 两个量必须联合解释

| 相关结果 | 相似度 S | 合理解释 |
|---|---:|---|
| 显著正相关 | 高 | 图案与幅度都较稳定 |
| 显著正相关 | 低 | 图案位置相同，但总体或局部幅度改变 |
| 显著负相关 | 任意 | 匹配位置呈反向变化，符合论文 DSPG 定义 |
| 不显著 | 高/低 | 相关证据不足；可能低表达、非线性变化或配准噪声 |

Figure 1 的模拟中，A 与 B 平均值近似相同却图案相反，得到显著负相关，但仍有约 54% 位置在两倍范围内；A 与 C 图案一致却整体幅度不同，得到显著正相关，但相似度为 0。这正是两个指标不能互相替代的原因。

### 9. 论文图和真实数据结果

#### Figure 1：方法与假阳性控制

A–D 对比 DGE、结构配准、空间相关和 fold-change 相似度；E–H 展示自相关随机场、解析/经验 p 值差异、variogram-matched permutations 和经验零分布。图中 FPR 0.50→0.04 是模拟校准结果，不等于所有真实数据都保证 4% 假阳性。

#### Figure 2A–E：MERFISH 脑生物重复

作者用 STalign 对齐同一 bregma 位置的两张成年小鼠冠状脑切片，并用 SEraster 聚合到 200 μm 像素。483 个测量基因中，MERINGUE 找到两重复共有的 415 个 SVG；其中 388/415（93%）显著正相关，0 个显著负相关。`Gabbr1` 与 `Adgrl1` 的 $r$ 相近，但相似度分别 0.91 与 0.55，说明重复间幅度偏差可独立出现。

#### Figure 2F–K：AKI 与正常肾

10x Visium 肾切片具有皮质、外髓质和内髓质对应结构。作者在两条件都为空间变异的 2278 个基因中，找到 25 个（1%）显著负相关 DSPGs，527 个（23%）显著正相关。`Cbr1` 等基因从正常髓质高表达转为 AKI 皮质高表达，提示组织区室特异的代谢重编程。这里是一张 AKI 与一张对照切片，条件效应与个体/切片差异不能完全分离。

补充部分位于同一 51 页 PDF 中，包含低表达与重复差异示例、非 SVG 的组织图案、肾区室配准、DSPG 补充空间图以及表格。它支持主文案例解释，但不扩展为独立大队列验证。

### 10. 论文与代码的对应边界

| 机制 | 本地代码 | 状态 |
|---|---|---|
| Pearson $r$ | `R/spatialCorrelation.R:534-553` | Exact |
| shuffle、locfit、variogram matching | `R/spatialCorrelation.R:85-136,234-327` | Exact/代码更详细 |
| 双侧经验 $p_E$ | `R/spatialCorrelation.R:318-327` | Exact |
| X/Y 双向置换 | `R/spatialCorrelation.R:512-548` | Exact |
| 最终取两 p 值最大值 | 函数仅返回两列 | Partial：调用者负责 |
| fold-change pixel 分类 | `R/packageFunction.R:229-246` | Exact |
| 相似度与低覆盖 NA | `R/packageFunction.R:208-260` | Exact |
| 配准、栅格化、SVG 筛选 | STalign/SEraster/MERINGUE | External |
| 脑与 AKI 分析 | vignette/脚本 | 包含分析示例，不是核心函数 |

现有 `doc_code.md` 曾将“全部七个公式完全匹配”概括为 HIGH fidelity；更精确的说法是核心数值公式高度一致，但最终保守 p 值聚合仍是用户侧操作，而且实现包含论文主文字未展开的 rescaling、抽样与阈值记录行为。

### 11. 使用前检查清单

1. 两张切片是否真的结构同源，配准残差是否可视化检查？
2. pixel resolution、聚合函数、归一化和共同像素范围是否固定？
3. 是否先限定有组织图案且表达足够的基因，避免对噪声解释“不相关”？
4. 是否用 `pmax(pValuePermuteX,pValuePermuteY)` 实现论文保守规则？
5. $B$ 是否足以支撑目标显著性和多重检验精度？
6. 最优 $\delta$ 是否常卡边界，variogram 是否确实匹配？
7. fold-change 阈值与低表达阈值是否符合平台动态范围？
8. 是否分别报告 $r$、经验 p、$S$ 和差异像素方向，而非压成单一“空间差异”标签？
9. 条件是否有生物重复，能否区分疾病效应与个体/批次效应？
10. 是否在解剖区室内复核，避免 whole-tissue correlation 的 Simpson 悖论？

STcompare 最有价值之处，是把“形状是否保持”和“幅度是否保持”拆开，并让相关显著性尊重空间自相关。其统计实现与论文高度对应，但所有结论都建立在正确配准、合理像素尺度和保守 p 值聚合之上。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## STcompare: Comparative Spatial Transcriptomics Analysis for Differentially Spatially Patterned Genes

**Paper**: Clifton K, Jiang V, dos Santos Peixoto R, Singh S, Matsuura R, Rabb H, Fan J. "STcompare: comparative spatial transcriptomics data analysis of structurally matched tissues to characterize differentially spatially patterned genes." *bioRxiv* 2025.11.21.689847. doi: 10.1101/2025.11.21.689847

**Code**: https://github.com/JEFworks-Lab/STcompare (R package, GPL-3)

**Category**: svg_patterning

---

### Motivation & Novelty

Standard differential gene expression (DGE) analysis — the workhorse of transcriptomics — asks only whether the *mean* expression of a gene differs between conditions. For spatially resolved data, this is insufficient in two ways:

1. **False negative**: A gene that expresses centrally in healthy tissue but peripherally in disease has the same mean expression but entirely different spatial patterns. Wilcoxon-based DGE calls it "not differentially expressed" ($\log_2\text{FC} = -0.03$, $p = 0.39$).
2. **False positive**: A gene with identical spatial patterns but uniformly scaled-up expression is called "differentially expressed" ($\log_2\text{FC} = 1.61$, $p < 2.2\text{e-}16$) even though its tissue organization is the same.

Existing spatial analysis methods also fall short:
- **SVG detection** (SpatialDE, *Nat Methods* 2018; SPARK-X, *Genome Biol* 2021; nnSVG, *Nat Commun* 2023): identifies genes with organized spatial patterns *within* a single sample, but cannot compare patterns *across* samples.
- **Differential SVG testing** (spEDT, *Nucleic Acids Res* 2024): detects whether a gene gains or loses spatial variability between conditions, but not whether a gene that *remains* spatially variable has changed its specific pattern.
- **Spatial mixed models** (Ospina et al., *Scientific Reports* 2024): models cell-type-specific DGE for spatial data but does not test for pattern shifts.

STcompare fills this gap by providing two complementary tests for **structurally matched** tissue pairs:
1. **Spatial correlation test**: Does the spatial pattern itself shift between conditions? (Are locations of high expression different?)
2. **Spatial fold-change test**: Among genes with similar patterns, does the expression *magnitude* change locally?

A critical innovation is the use of **empirical p-values via variogram-matched permutations** (adapted from Viladomat et al., *Biometrics* 2014) to control the false positive rate inflated by spatial autocorrelation. Without this correction, 50% of random uncorrelated spatially autocorrelated gene pairs are falsely called significant (FPR=0.50 vs. 0.04 with correction).

---

### Method Overview

STcompare is an R package implementing two statistical tests on paired, structurally matched ST datasets. It requires as prerequisites: (1) spatial structural alignment (e.g., STalign, *Nat Commun* 2023) and (2) rasterization onto a shared pixel grid (SEraster, *Bioinformatics* 2024).

#### Test 1: Spatial Correlation

For each gene, compute Pearson's correlation $r$ between expression vectors at matched locations across two datasets. Because spatially variable genes violate the independence assumption of analytical p-values, STcompare generates an empirical null distribution:

- Randomly shuffle X across locations; apply Gaussian kernel smoothing (locfit) with bandwidth $\delta$ chosen to match the variogram (spatial autocorrelation structure) of the original X.
- Compute null correlations $r_1,\ldots,r_B$ ($B=100$ permutations by default).
- Empirical p-value $p_E$ = fraction of null $r_j$ more extreme than observed $r$.
- Run once permuting X, once permuting Y; report the more conservative $p_E$.

**Classification**: $r < 0$, $p_E < 0.05$ → differently spatially patterned gene (DSPG); $r > 0$, $p_E < 0.05$ → similarly spatially patterned.

#### Test 2: Spatial Fold-Change Similarity

For each valid location $i$ (expression above 5th percentile in either dataset), compute $\log_2(y_i/x_i)$. A location is "similar" if $|\log_2(y/x)| < 1$ (default 2-fold threshold). The similarity score $S$ = fraction of similar locations. Dissimilar locations are labeled by direction (more in X = yellow; more in Y = red), enabling spatial visualization of where changes occur.

#### Joint Interpretation

| Spatial correlation | Similarity score | Interpretation |
|---------------------|-----------------|----------------|
| $r < 0$, $p_E < 0.05$ | Any | DSPG: pattern shifted or inverted |
| $r > 0$, $p_E < 0.05$ | $S$ high | Pattern AND magnitude conserved |
| $r > 0$, $p_E < 0.05$ | $S$ low | Pattern conserved, magnitude changed locally |
| $p_E > 0.05$ | — | No spatial pattern evidence |

---

### Evaluation

#### Simulated Data

**Correlated patterns** (3 kidney-shaped datasets): Dataset A (radial center-hot pattern), B (radial center-cold, same mean as A), C (same pattern as A, 2× magnitude).
- Bulk DGE: A vs B = not significant ($p=0.39$); A vs C = significant ($p < 2.2\text{e-}16$)
- STcompare: A vs B = significantly negatively correlated ($r < 0$, $p_E < 0.05$), S=0.54; A vs C = significantly positively correlated ($r > 0$, $p_E < 0.05$), S=0
- **Key result**: STcompare correctly captures both failure modes of DGE.

**FPR control** (100 independent autocorrelated genes, 9900 pairs):
- Analytical p-values: FPR = 0.50 (4928/9900 pairs falsely significant at $\alpha=0.05$)
- Empirical p-values: FPR = 0.04 (400/9900 pairs, near expected 0.05)
- **Key result**: ~12.3× reduction in false positives.

#### Mouse Brain MERFISH Biological Replicates

- **Data**: Two MERFISH coronal brain sections from different animals at matched bregma location (S2R2, S2R3); 483 genes, rasterized to 200μm pixels
- **SVG overlap**: 415 genes identified as SVG in both replicates
- **Result**: 93% (388/415) SVGs significantly positively correlated ($p_E < 0.05$); 0 negatively correlated. 7% not significant (mostly low-expression genes).
- **Non-SVGs**: 21% (14/68) were nonetheless significantly positively correlated (small hotspot patterns, high-dispersion patterns, low-expression genes).
- **Validation**: High SVG correspondence across replicates confirms STcompare's sensitivity for biologically real positive cases.

#### Mouse Kidney Acute Kidney Injury (AKI) vs. Control (10x Visium)

- **Data**: 10x Visium at 55μm spots; IRI AKI sample (24hr, "IL3") vs normal ("NL3") from Gharaie et al., *Scientific Reports* 2023. Spots annotated via Harmony-integrated Louvain clustering into cortex, outer medulla, inner medulla.
- **SVG set**: 2278 genes spatially variable in both conditions (MERINGUE)
- **Results**:
  - 1% (25/2278 SVGs) significantly differently spatially patterned ($r < 0$, $p_E < 0.05$) — **DSPGs**
  - 23% (527/2278) significantly positively correlated ($r > 0$, $p_E < 0.05$)
- **Biological findings (DSPGs)**:
  - Metabolic reprogramming: Pgam1, Fh1, Cbr1, Oplah — decreased in medulla, increased in cortex in AKI (compartment-specific shift; TCA cycle, glycolysis, glutathione pathway)
  - Gstm1 (glutathione pathway): decreased outer medulla, increased inner medulla + cortex
  - OXPHOS genes (Iscu, Atp5f1, Ndufa4, Cox7b, Cox8a): decreased in medulla but maintained in cortex
- **Biological findings (positively correlated, S low)**:
  - Acsm2, Slc34a1 (proximal tubule markers): remain spatially cortex-localized but expression greatly reduced — consistent with proximal tubule-specific AKI consequence
  - Nox4, Gpx1 (oxidative stress protection): decreased in cortex
  - Vnn1, Nbl1 (fibrosis markers): increased in cortex in AKI

---

### Reproducibility

**Rating: 3/5**

**Justification**: The R package is clean and well-documented with two worked vignettes (simulated data and AKI analysis). Core methods are fully reproducible from the package. However:

**Strengths**:
- Open-source R package on GitHub (GPL-3)
- Bioconductor-compatible (SpatialExperiment, BiocParallel)
- Well-documented functions with full Roxygen documentation and examples
- Simulated datasets (`speKidney`, `simRanPatternRasts`) bundled in package
- FPR simulation script in `inst/scripts/`

**Weaknesses/Practical Notes**:
- Kidney AKI Visium data now available at Zenodo (https://zenodo.org/records/17676992), but requires contacting original authors of Gharaie et al. 2023 — not directly deposited by STcompare authors.
- Brain MERFISH data at Zenodo (https://zenodo.org/records/10724029) — publicly available.
- The biological replicates vignette (`biological-replicates-example.Rmd.bnk`) is archived (`.bnk` extension) and not rendered in documentation.
- Computational cost is significant for large gene sets: each gene requires B×|δ| locfit smoothing calls + variogram computations. For 2278 SVGs at default settings (B=100, 11 δ values), runtime can be hours on a single core. Parallelization (`nThreads`) helps within each gene but outer gene loop is sequential.
- No formal benchmark against other methods for detecting spatial pattern changes (comparison is against bulk DGE only, not against spatial domain-aware DGE).
- Package requires R ≥ 4.3.0 and Bioconductor infrastructure (SpatialExperiment, SEraster).

**Environment setup**:
```r
# Install prerequisites
BiocManager::install("SpatialExperiment")
BiocManager::install("SEraster")

# Install STcompare
remotes::install_github("JEFworks-Lab/STcompare")
```

**Common pitfalls**:
1. `spatialCorrelationGeneExp` requires matched pixel **names** (row names of spatialCoords) across both SpatialExperiment objects — ensure consistent naming after rasterization.
2. The conservative p-value is NOT automatically reported as `max(pValuePermuteX, pValuePermuteY)` — users must do this manually: `pmax(results$pValuePermuteX, results$pValuePermuteY)`.
3. For large N (>1000 pixels), only 1000 are subsampled for variogram computation — results may vary slightly across runs unless seed is set.
4. Zero expression values are silently replaced with 0.0001 in the similarity score calculation — be aware when interpreting similarity scores for lowly-expressed genes.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
