---
layout: default
permalink: /paper-atlas/astral-single-cell-proteomics-d0f23cb6/
title: "Astral_single_cell_proteomics"
nav: false
wide: true
description: "这套方法通过 50-SPD 纳流 LC、FAIMS 降噪、Orbitrap/Astral 并行 DIA、严格 FDR 验证和 MS1 单细胞矩阵分析，把单细胞蛋白覆盖与定量精度推到更高水平；公开 notebook 对后分析和图形有较强支撑，但完整复现仍依赖外部原始数据、Spectronaut 配置和实验室路径修复。"
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Astral_single_cell_proteomics</h1>
    <p>Challenging the Astral mass analyzer to quantify up to 5,300 proteins per single cell at unseen accuracy to uncover cellular heterogeneity</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-024-02559-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Astral_single_cell_proteomics">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/SimpleNumber/SCP_on_AstralMS" target="_blank" rel="noopener noreferrer" aria-label="Open code for Astral_single_cell_proteomics">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Astral 单细胞蛋白质组学方法详解

### 先给结论：这篇论文的方法是什么？

这不是一篇提出新神经网络或新聚类算法的论文，而是一套端到端的单细胞质谱蛋白质组学技术平台。它把样品制备、纳流 LC、FAIMS、Orbitrap Astral 的并行 MS1/MS2 采集、Spectronaut DIA 分析和单细胞统计分析联合优化，目标是在较高通量下同时提高蛋白覆盖深度与定量可靠性。

论文最终展示了三类能力：

1. 在 250 pg 的单细胞量级肽段输入上获得很深的蛋白覆盖；
2. 在已知人–酵母混合比例中恢复预期倍数变化，并优于 Orbitrap Exploris 480；
3. 在真实单细胞中区分 A549/H460、不同大小的 A549，以及 TE-like/hPS 两类细胞。

主要论文证据位于 `paper source/nature_html/paper.md:9-27,33-211`。

### 1. 它要解决什么问题？

单细胞蛋白质组学的输入极低，常常只有几十到几百 pg 蛋白。由此产生四个相互制约的问题：

- 信号弱，低丰度肽段容易被背景淹没；
- 梯度过短时，肽段分离不充分、谱图更复杂；
- 梯度过长时，覆盖可能提高，但每天可分析的细胞数下降；
- 即使“鉴定到”蛋白，也不代表定量足够准确，尤其是低丰度蛋白。

早期方法已经解决了部分环节。例如 SCoPE-MS（*Genome Biology*, 2018）用同位素标记和 carrier 思路提高灵敏度；nPOP（*Genome Biology*, 2022）提高了自动化制备能力；One-Pot（*Analytical Chemistry*, 2023）提供了稳健的无标记单细胞制备流程；超快 LC–MS 的无标记路线也在 *Proteomics* 2023 中被系统讨论。本文的重点不是否定这些方法，而是说明：样品制备、色谱、仪器速度、离子过滤、DIA 搜索和 FDR 控制必须一起优化，才能同时获得深度、速度和定量质量（`paper.md:18-24,349-362`）。

### 2. 方法的输入与输出

#### 输入

- 250 pg HeLa/K562 商业肽段，用于覆盖深度和梯度优化；
- 总量 250 pg、比例已知的人–酵母肽段混合物，用于定量准确性验证；
- A549、H460 单细胞；
- naive hPS 与 TE-like 单细胞；
- 20、40 或 100 个细胞的较高输入样品，用于构建 tailored DIA library；
- cellenONE 给出的 A549 细胞直径信息。

#### 输出

- 每次运行的 protein group（PG）与 precursor 数量；
- MS1 蛋白定量矩阵；
- CV、数据点/峰、峰宽和已知倍数变化的恢复情况；
- PCA、UMAP、热图和标志蛋白分布；
- 对细胞系、细胞大小/细胞周期相关异质性、TE/hPS 谱系差异的解释。

### 3. 整体流程

```text
单细胞或低输入肽段
        │
        ▼
384 孔板微量制备
  cellenONE / FACS 分选
  DDM + TEAB + trypsin 一锅裂解消化
        │
        ▼
25 cm 纳流 LC，选择 50 SPD
  快速上样 + 较低流速洗脱
        │
        ▼
FAIMS Pro 去除部分背景离子
        │
        ▼
Orbitrap Astral DIA
  Orbitrap：MS1
  Astral：MS2
  两个分析器并行工作
        │
        ▼
Spectronaut 18.6
  method evaluation / DirectDIA+ / library search
  MS1 定量 + FDR 控制
        │
        ├── 技术验证：覆盖、CV、FDR、人–酵母倍数变化
        │
        └── 单细胞分析：过滤 → log2 → 标准化 → 缺失值填补
                                      │
                                      ▼
                               PCA / UMAP / 热图
                                      │
                                      ▼
                              细胞异质性与标志蛋白
```

一个重要边界是：GitHub 仓库只覆盖 Spectronaut 输出之后的数据整理和画图，不能把 notebook 中的文件夹名误当作质谱采集实现。

### 4. 为什么选择 50 SPD？

作者比较了 30–80 samples per day。缩短梯度会让峰更尖、信号更强，但过快时分离能力下降、谱图复杂度上升，而且每个洗脱峰上的数据点减少。

Fig. 1 直接显示：HeLa 和 K562 的 PG/precursor 数在 50 SPD 附近达到高点，80 SPD 明显下降；同时 50 SPD 仍保留约 5 个 MS1 数据点/峰。作者因此把 50 SPD 作为后续单细胞实验的统一条件（`paper.md:36-50`; `figure_analysis.md` Fig. 1）。

可以把这个选择理解为一个工程折中：

$$
\text{有效信息量}\approx
\text{信号强度}\times\text{分离质量}\times\text{峰上采样充分度}.
$$

这不是论文给出的优化目标函数，而是对实验权衡的解释。

### 5. FAIMS 起什么作用？

低输入条件下，单电荷背景离子的相对影响更大。FAIMS 通过补偿电压筛选离子，提高信噪比。

论文扫描了 −38 到 −88 V。图中 −48 至 −68 V 区间表现较好：相较无 FAIMS，蛋白和 precursor 覆盖增加，MS1/MS2 CV 降低，而每个峰的数据点数没有明显减少。不同电压得到的 peptide 集合并不完全相同，但蛋白层面的共同集合更稳定（`paper.md:80-97`; Fig. 2）。

作者后续大多数 Astral 实验使用 −48 V。需要注意，notebook 只读取不同电压实验的 Spectronaut 结果，并不控制 FAIMS 硬件（`SCP_on_AstralMS/Figure_2.ipynb:224-333,405-494`）。

### 6. Orbitrap Astral 采集设计

Astral 平台的关键优势是并行采集：Orbitrap 记录 MS1，Astral 记录快速、高灵敏度的 MS2。论文给出的主要设置包括（`paper.md:268-286`）：

- Orbitrap MS1：分辨率 240,000，$m/z$ 400–900，最大注入时间 100 ms；
- Astral DIA MS2：$m/z$ 400–800；
- 对高输入 library 使用较窄窗口和较短注入时间；
- 对 1–40 个细胞和 50–500 pg 输入使用约 20 $m/z$ 窗口；
- 单细胞通常使用 60 ms precursor accumulation time；
- 输入越低，通常需要更长的积累时间。

这里的核心思想是按输入量调整 acquisition capacity。较高输入不需要长时间积累，而且可以使用较窄窗口；单细胞信号弱，需要在速度、灵敏度和窗口复杂度之间重新平衡。

这些采集设置只在论文中得到验证。代码仓库没有质谱控制方法，也没有 Spectronaut search project。

### 7. Spectronaut 的三种分析模式

论文区分三个常用模式（`paper.md:289-292`）：

#### Method evaluation

每个 raw file 被当作独立 condition，不做跨运行匹配，适合观察单次运行自身能鉴定多少蛋白。

#### DirectDIA+

把 replicate 定义为同一 condition，允许匹配，提高数据完整度和 ID 数量。

#### Library search

先用较高输入的 DIA 数据构建 tailored library，再搜索单细胞/低输入数据。它可以显著增加 ID，但 library 大小与采集方法必须匹配，并且需要特别检查 FDR。

所有主要定量使用 MS1。因为单细胞制备没有烷基化，搜索时移除了 cysteine carbamidomethylation 静态修饰。

### 8. 为什么必须单独验证 FDR？

论文发现 Spectronaut 18 默认设置在 PG 层面可能比标称的 1% 更宽松，因此使用两种 entrapment：

1. 保持胰酶切位点位置的 shuffled human database；
2. *C. elegans* database。

FDR 估计式为

$$
\widehat{\rm{FDR}}=\frac{d(1+1/r)}{t+d},
$$

其中：

- $d$：decoy/entrapment 蛋白数；
- $t$：target 蛋白数；
- $r$：decoy 与 target database 的大小比例。

Fig. 1k 中 shuffled 与 *C. elegans* 检查得到约 1.8%–2.7%，说明默认阈值没有严格达到 1%。作者进一步采用 Baker 等人建议的全部 0.01 cutoff。论文还指出，把三个重复的 unique IDs 简单相加会累积错误鉴定，FDR 可升至 5.5%，所以更建议报告平均 ID 数（`paper.md:65-77,295-301`）。

代码中 `get_FP` 统计 `JB_FAKE` 蛋白，`get_FP_celegants` 统计 *C. elegans* 命中，并根据数据库大小乘以修正因子（`Figure_1.ipynb:200-234,880-940`）。这是对图中结果的部分实现，不是完整的数据库构建与搜索流程。

### 9. 如何验证“定量准确”，而不只看 CV？

作者使用总量相同但人–酵母比例不同的 250 pg 混合物：150:100、200:50、240:10 pg。因为真实比例已知，可以直接检查测得 fold change 是否接近期望值。

notebook 对两个条件的平均定量 $Q_1,Q_2$ 计算

$$
\log_2(FC)=\log_2\left(\frac{Q_1}{Q_2}\right),
$$

并以

$$
x=\log_2\left(\frac{Q_1+Q_2}{2}\right)
$$

表示平均丰度（`Figure_3.ipynb:312-352`）。

重复间 CV 为标准差除以均值。为了展示 CV 如何随丰度变化，代码使用 100 个蛋白的滚动窗口，并拟合

$$
f(x)=a e^{-b x}+c
$$

（`Figure_3.ipynb:44-50,349-368`）。

结果表明：Astral 定量蛋白数超过 Exploris 480 的两倍；在两台仪器共同定量的低丰度蛋白中，局部 CV 从 Exploris 的约 20% 降到 Astral 的约 12%。但越接近定量极限，CV 仍然快速升高（`paper.md:100-126`; Fig. 3）。

### 10. 单细胞矩阵怎样进入 PCA/UMAP？

#### A549 大小分析

`Figure_4.ipynb` 的直接行为是（`Figure_4.ipynb:494-615`）：

1. 读取 Spectronaut protein report；
2. 去掉 blank 列；
3. 保留至少在 20 个细胞中有值的蛋白；
4. 对定量值做 log2；
5. 对每个蛋白跨细胞标准化；
6. 用整个数据集的最小值填补剩余缺失值；
7. 执行三维 PCA 和 `UMAP(random_state=0)`；
8. 从 cellenONE 文件附加 diameter/elongation。

#### A549/H460 与 TE/hPS

A549/H460 和 TE/hPS 分析使用相似流程，但缺失值阈值是至少 5 个样品有值（`Figure_4.ipynb:730-894`; `Figure_5.ipynb:160-192,455-515`）。

需要特别理解：这里的标准化是“按蛋白跨细胞”进行，目的是比较某个蛋白在不同细胞中的相对高低，而不是保留原始绝对丰度尺度。

### 11. 生物学结果怎样理解？

#### A549 与 H460

PCA 和热图把 A549、H460、blank 清楚分开。A549 平均覆盖约 4,879 PG，H460 约 3,166 PG，说明相同直径范围并不保证相同蛋白含量或覆盖（`paper.md:132-146`; Fig. 4a–c）。

#### A549 大小与细胞周期

PG 数随直径增加，单细胞最大达到 5,300 个蛋白。PCA/UMAP 也随直径呈现结构，histone、actin、NUCKS1、MKI67 等蛋白沿流形出现不同梯度（`paper.md:149-172`; Fig. 4d–f；Extended Data Fig. 1）。

但是，论文没有做细胞周期同步或独立 phase label。因此 G1/S/G2/M 注释应视为基于大小和 marker 的假设生成结果，不能当作已经验证的细胞周期分类器。

#### TE-like 与 naive hPS

两类细胞在 PCA 和 UMAP 中强烈分开。TE-associated 的 KRT18、KRT19、RAB25、DAB2、YAP1 等在一侧更高，而 hPS-associated 的 DPPA4、DPPA2、SUSD2、DNMT3L 在另一侧更高（`paper.md:175-190`; Fig. 5；Extended Data Fig. 2）。

这说明单细胞蛋白质组能够恢复已知谱系差异，但仓库中没有找到论文所述 t-test、Benjamini–Hochberg 校正和 STRING GO 分析代码，所以这些统计/富集结果不能从当前 notebook 完整重现。

### 12. 代码到底能复现到哪一步？

#### 已直接验证

- Spectronaut run-summary TSV 解析；
- PG、precursor、FWHM、数据点/峰和 CV 汇总；
- shuffled/*C. elegans* entrapment 命中统计；
- FAIMS 条件比较和 overlap 数据；
- 人–酵母 log2 fold change、CV 和滚动拟合；
- A549/H460/TE/hPS 过滤、log2、标准化、最小值填补；
- PCA、UMAP、热图和 figure table 序列化。

#### MISSING / Not found

- 原始 MS 文件和本地 Spectronaut report 目录；
- cellenONE 原始大小文件；
- notebook 引用的 FASTA 文件；
- LC、FAIMS 和质谱采集控制实现；
- Spectronaut 搜索与 library 生成配置；
- TE/hPS t-test、BH 校正和 STRING GO 脚本；
- `requirements.txt`、环境锁文件或完整运行说明；

notebook 中大量 `/groups/protechhub/...` 与 `/users/iuliia.bubis/...` 是作者/实验室绝对路径。它们表达静态数据依赖，不代表当前环境已经执行过这些单元，也不是 runtime trace。

### 13. 最值得学习的三个方法学要点

1. **不要把鉴定深度与定量质量混为一谈。** 本文既比较 ID 数，也用已知混合比例检查 fold change，并画出丰度依赖的 CV。
2. **高 ID 数必须配套独立 FDR 检查。** matching 和 library 能增加覆盖，但 entrapment 显示默认阈值可能偏松，重复间简单求并集还会累积错误。
3. **单细胞结构解释必须保留验证边界。** PCA/UMAP 与 marker 梯度可以生成生物学假设，但缺少独立标签时，不能把可视化注释升级为确定的细胞状态。

### 14. 一句话总结

这套方法通过 50-SPD 纳流 LC、FAIMS 降噪、Orbitrap/Astral 并行 DIA、严格 FDR 验证和 MS1 单细胞矩阵分析，把单细胞蛋白覆盖与定量精度推到更高水平；公开 notebook 对后分析和图形有较强支撑，但完整复现仍依赖外部原始数据、Spectronaut 配置和实验室路径修复。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Astral single-cell proteomics: summary

### Problem

Single-cell mass-spectrometry proteomics must recover weak peptide signals while retaining enough chromatographic sampling for accurate quantification and enough throughput for biological studies. The field had already developed multiplexed SCoPE-MS (*Genome Biology*, 2018), automated nPOP (*Genome Biology*, 2022), One-Pot label-free preparation (*Analytical Chemistry*, 2023), and other miniaturized workflows, but the paper argues that proteome depth and quantitative performance remained limiting (`paper source/nature_html/paper.md:18-24,349-361`).

### Proposed technology

The study combines:

- One-Pot-style miniaturized preparation in 384-well plates;
- a 25-cm Aurora Ultimate TS nanoflow LC column with an integrated emitter;
- 50 samples per day (SPD) as the selected speed/coverage compromise;
- FAIMS Pro signal filtering;
- parallel Orbitrap MS1 and Astral MS2 DIA acquisition;
- Spectronaut 18.6 analysis with method-evaluation, DirectDIA+ matching, tailored-library and stringent-FDR variants;
- MS1 quantification followed by protein-matrix filtering, log2 transformation, normalization, imputation and dimensionality reduction.

The novelty is primarily an optimized integrated technology platform, not a new computational model. The key design idea is to preserve approximately five MS1 measurements per elution peak at 50 SPD while exploiting the Astral analyzer's fast, sensitive MS2 acquisition (`paper.md:36-62,202-211,268-301`).

### Main evaluation

#### Coverage and FDR

With 250 pg HeLa/K562 digests, Fig. 1 shows maximal identification near 50 SPD. Tailored 10-ng libraries raise low-input coverage to more than 7,500 PGs for HeLa and more than 6,800 for K562 under default settings. Independent shuffled-target and *C. elegans* entrapment checks show that default Spectronaut settings can exceed the nominal 1% protein-level FDR, motivating the fully stringent 0.01 cutoff set (`paper.md:36-77`).

#### FAIMS

The favorable FAIMS region improves low-abundance signal and median CV without visibly reducing points per peak. The paper reports up to 55.3% more PGs and 42.6% more precursors than no FAIMS, while also showing that different compensation voltages recover partly different peptide sets (`paper.md:83-94`; Fig. 2).

#### Quantitative benchmark

Defined human–yeast mixtures test 2:1, 5:1 and 10:1 yeast fold changes at 250-pg total input. Astral quantifies more than twice as many proteins as the Exploris 480 and gives tighter fold-change distributions for shared proteins. At the low-abundance end, the reported local CV is about 12% on Astral versus 20% on Exploris; precision worsens as abundance falls (`paper.md:100-126`; Fig. 3).

#### Biological applications

- A549 and H460 lung-cancer cells separate clearly by PCA and heat-map structure. Average A549 coverage is about 4,879 PGs versus 3,166 for H460 in the first comparison (`paper.md:132-146`).
- Across 66 A549 cells, IDs increase with diameter; the maximum is 5,300 proteins in one cell. PCA/UMAP structure tracks cell size and marker abundance, suggesting cell-cycle-related heterogeneity, but no cell-cycle control was performed (`paper.md:149-172`; Fig. 4 and Extended Data Fig. 1).
- TE-like and naive hPS cells separate strongly by PCA/UMAP. Library searches yield about 2,339 PGs in TE-like cells and 2,544 in hPS cells, and lineage-marker abundance patterns agree with known transcriptomic markers (`paper.md:175-190`; Fig. 5 and Extended Data Fig. 2).

### Code–paper match

**Overall fidelity: medium.** The GitHub snapshot at commit `5acb54c4f5e6748ac622f5d8dd2e06aae8ddf081` contains five notebooks and serialized figure tables. Direct inspection verifies downstream Spectronaut-export parsing, CV and fold-change calculations, entrapment-hit counting, filtering/imputation, PCA/UMAP, and plotting for Figs. 1–5 (`SCP_on_AstralMS/Figure_1.ipynb:81-265`; `Figure_2.ipynb:224-494`; `Figure_3.ipynb:173-368`; `Figure_4.ipynb:494-894`; `Figure_5.ipynb:57-515`).

The code is not the acquisition workflow. It does not operate the LC, FAIMS or mass spectrometer and does not run Spectronaut. Notebook path labels must not be treated as an acquisition implementation or runtime trace.

### Reproducibility

**Rating: 3/5 for figure-level auditability; lower for end-to-end reproduction.**

Strengths:

- public paper, PRIDE accession `PXD049412`, source-data links and public GitHub/figshare code statement (`paper.md:334-343`);
- all five figure notebooks are present;
- many derived CSV/Parquet/text tables needed by later plotting cells are bundled;
- key downstream calculations closely correspond to paper figures.

Gaps:

- raw MS files, Spectronaut report directories, cellenONE exports and referenced FASTA files are not bundled in the code snapshot;
- preprocessing cells retain `/groups/protechhub/...` and `/users/iuliia.bubis/...` absolute paths;
- no dependency lockfile or environment specification is provided;
- acquisition control and Spectronaut search/library configuration are absent;
- the TE/hPS t-test, Benjamini–Hochberg correction and STRING GO workflow are not found in the notebooks;
- supplementary Markdown is unavailable in this workspace; only the supplementary-PDF link was acquired (`paper.md:495-503`).

Thus, the snapshot can audit and likely reconstruct much of the plotting layer from bundled serialized tables, but it cannot reproduce the technology from raw cells or spectra without external data, proprietary software configuration and path repair.

### Limitations and interpretation boundaries

- The 250-pg digest benchmark approximates a single-cell input but does not represent the full variation in real cellular protein content.
- Accuracy and precision degrade toward low abundance, limiting biological clustering to proteins measured with adequate signal.
- Matching and libraries can increase IDs but also interact with global/run-specific FDR behavior.
- Cell-cycle labels in A549 UMAP are hypothesis-generating, because the study did not experimentally control or independently label cell-cycle phase.
- The TE/hPS marker maps support lineage separation, but the missing statistical/GO code prevents full computational reproduction of the reported enrichment analysis.

### Bottom line

The paper demonstrates a high-depth, quantitatively strong label-free SCP platform by jointly optimizing preparation, LC throughput, FAIMS, Orbitrap Astral DIA acquisition and downstream analysis. Its strongest evidence is the convergence of coverage/FDR tuning, an explicit two-proteome accuracy benchmark, and two biological applications. The released notebooks provide solid support for figure construction and postanalysis, but not for the upstream acquisition or Spectronaut workflow.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
