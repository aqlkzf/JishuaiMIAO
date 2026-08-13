---
layout: default
permalink: /paper-atlas/perturb-tracing-0b04f521/
title: "Perturb-tracing"
nav: false
wide: true
description: "Perturb-tracing 把“这个细胞敲掉了哪个基因”和“这个细胞的染色体三维折叠变成了什么样”同时用显微成像读出来，因此能在一个 pooled CRISPR 筛选中并行寻找影响相邻 TAD、A/B 区室、整条染色体压缩程度和细胞核形态的调控因子。 论文发表于 Nature Methods（2025），DOI：10.1038/s41592-025-02652-z。"
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
    <h1>Perturb-tracing</h1>
    <p>Perturb-tracing enables high-content screening of multi-scale 3D genome regulators</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Perturb-tracing 方法详解

### 一句话理解

Perturb-tracing 把“这个细胞敲掉了哪个基因”和“这个细胞的染色体三维折叠变成了什么样”同时用显微成像读出来，因此能在一个 pooled CRISPR 筛选中并行寻找影响相邻 TAD、A/B 区室、整条染色体压缩程度和细胞核形态的调控因子。

论文发表于 *Nature Methods*（2025），DOI：`10.1038/s41592-025-02652-z`。

### 1. 它要解决什么问题？

三维基因组不是单一尺度的结构：局部有 TAD，较长距离有 A/B 区室，整体还有染色体领地与细胞核形态。同一个基因可能只影响某一尺度，也可能同时影响多个尺度。真正困难的是，筛选时必须同时知道：

1. 单个细胞携带哪条 sgRNA；
2. 该细胞中多个基因组位点的三维坐标；
3. 这些坐标对应的局部、长程和全局结构变化；
4. 变化是否在携带同一扰动的多个细胞中稳定出现。

传统的逐基因实验能获得高内容表型，但通量低。高通量 Oligopaint 筛选（*Nature*, 2023）主要聚焦较少的位点对表型；单细胞 CRISPR–染色质可及性筛选（*Nature Biotechnology*, 2021；*Nature Communications*, 2021）能够规模化分析局部开放性，但不是高阶三维折叠。此前的成像 pooled CRISPR 筛选也没有与多尺度 3D 基因组读出整合（`paper.md:18-24,139-151,316-334`）。

### 2. 核心创新：在同一个细胞里配对扰动与三维表型

Perturb-tracing 由三个模块组成：

- **pooled CRISPR knockout**：每个细胞通常只接收一个 sgRNA–barcode 构建体；
- **BARC-FISH**：显微成像读取与 sgRNA 唯一关联的 RNA 条形码；
- **chromatin tracing**：顺序成像 chr22 上 27 个 TAD 的三维位置。

这三个模块的关键不是简单并列，而是通过图像配准和细胞分割，把条形码、染色体轨迹和细胞核表型绑定到同一个细胞。

```text
sgRNA + RNA barcode
        |
        v
同一个细胞
  ├─ BARC-FISH：读出 10 位条形码 -> sgRNA/基因身份
  ├─ chromatin tracing：读出 27 个 TAD 的 3D 坐标
  ├─ Geminin：筛选 G1 期细胞
  └─ DAPI/总蛋白：分割细胞并提取核形态
        |
        v
扰动身份 + 3D 距离矩阵 + 接触矩阵 + 核形态
```

### 3. BARC-FISH 如何编码和解码扰动？

#### 3.1 十位三进制条形码

每个 barcode 有十位，每一位取值为 0、1 或 2：

$$
\mathbf b=(b_1,\ldots,b_{10}),\qquad b_k\in\{0,1,2\}.
$$

理论编码空间为

$$
3^{10}=59{,}049.
$$

但实验在克隆时只保留约 4,000–5,000 个菌落，使一个 barcode 大概率只与一个 sgRNA 配对，因此当前设计的实用容量约为 5,000 条 sgRNA，而不是完整使用 59,049 个码（`paper.md:47,193-196`）。

#### 3.2 原位信号放大

每一位 barcode RNA 同时杂交 linear probe 和 padlock probe。padlock 连接成环后，以 linear probe 为引物进行 phi29 rolling-circle amplification（RCA），在原位生成高拷贝扩增产物。随后使用三种荧光二级探针分别识别 0、1、2（Fig. 1）。十轮成像依次读取十位数字。

#### 3.3 图像解码与纠错

MATLAB archive 中的流程是：

1. `runM2_decodeAndBleedthroughCorrection.m` 对 30 个“位×取值”通道做配准、二值化和串色清理；
2. `runM3_findThreshold_kraken.m` 使用 30 个硬编码强度阈值筛选信号，这些阈值明确针对一个名为“211117 kraken”的数据集；
3. `runM4_segment3.m` 对细胞做 watershed 分割，每一位选择像素数最多且严格胜出的颜色作为 0/1/2；
4. `runM7plus...m` 或 `runT6...m` 用 Hamming 距离匹配 codebook，仅当最近的 good code 唯一且错误少于两位时接受，也就是最多允许一位 mismatch。

Extended Data Fig. 1 显示：完全匹配时解码率为 33%，纠错后提高到 51%；NGS 检出的 4,469 个 barcode 中，76% 是只对应一条 sgRNA 的 good code。

**缺口：** archive 只读取 `GoodCodes.mat`、`BadCodes.mat`、`Decode.mat` 等文件，没有从 NGS reads 生成 codebook 的代码；这一段在发布代码中为 **Not found**。

### 4. 如何得到一条染色体的 3D 轨迹？

论文选择 chr22，是因为它较短，而且 A549 中没有已知 chr22 结构变异。实验对覆盖 chr22 的 27 个 TAD 分别选取中央 100-kb 区域做顺序 DNA FISH（`paper.md:53`）。

#### 4.1 连接相邻轮次的焦点

`runT4_LargeScale_linkTraces_210922.m` 先过滤拟合宽度和 adjusted-$R^2$ 不合格的焦点，然后计算连续 TAD 轮次之间的三维距离。只有两个焦点互为最近邻且距离小于 2 µm 时才连接。新轨迹只能从一组预先指定的“较好 TAD”启动，最后删除少于五个位点的短轨迹。

因此，它是一个带有强先验阈值的启发式 tracking 算法，不是全局最优匹配或概率模型。

#### 4.2 补拟合缺失位点

`runT5_LargeScale_refineTraces_largeScaleTracing.m` 根据已有轨迹定义一个染色体 territory，在缺失 TAD 对应的图像中重新拟合焦点，并再次使用拟合优度和宽度阈值决定是否加入轨迹。

#### 4.3 把轨迹分配给细胞

`runT6_matchTraceswithBarcode_update220713.m` 将 chromatin tracing 与 BARC-FISH/DAPI 图像配准，按轨迹质心找到所属 cell/nucleus，并计算轨迹的回转半径：

$$
R_g=\sqrt{\frac{1}{n}\sum_{i=1}^{n}\lVert \mathbf r_i-\bar{\mathbf r}\rVert^2}.
$$

只有质心位于细胞核中、$R_g\ge0.5$ µm 且细胞属于 G1 期时，轨迹才保留并绑定 barcode/GeneName。

### 5. 为什么只分析 G1 期？

S/G2 期发生 DNA 复制，同一个 TAD 会出现成对拷贝，直接混入会改变焦点数量和距离分布。论文用 Geminin 抗体区分细胞周期，只分析 G1 细胞（Extended Data Fig. 2）。

archive 中 `runM5_extractGeminin.m` 使用固定的 normalized Geminin cutoff = 800，并在后续要求 `intensityG1 == 1`。这是代码中真实使用的规则，但它是数据集校准值，不是跨实验自动学习的阈值。

### 6. 多尺度表型怎么计算？

设 TAD $i$ 和 $j$ 的坐标分别为 $\mathbf r_i=(x_i,y_i,z_i)$ 和 $\mathbf r_j=(x_j,y_j,z_j)$：

$$
d_{ij}=\lVert \mathbf r_i-\mathbf r_j\rVert_2.
$$

#### 6.1 相邻 TAD 距离

对 $i$ 与 $i+1$ 同时被观测的轨迹，计算 $d_{i,i+1}$。`r2_adjTADdis.m` 只让至少有 40 条轨迹的扰动进入比较，并输出 log2 fold change、Wilcoxon signed-rank test、z score 和 FDR。

NIPBL knockout 增大相邻 TAD 距离，而 CTCF knockout 减小该距离，方向符合 loop extrusion 的已知作用，因此构成正对照。

#### 6.2 长程 A–A、A–B、B–B 接触

archive 对非相邻 TAD 定义：

$$
C_{ij}=\mathbf 1[d_{ij}<0.5\ \mu\mathrm m],\qquad |i-j|>1.
$$

再根据 TAD 的 compartment score 符号，把接触分成 A–A、B–B 和 A–B，并对每条轨迹统计接触数。

#### 6.3 整条染色体的压缩程度

27 个 TAD 共有

$$
\binom{27}{2}=351
$$

个不同的 TAD pair。`r4_interTADdis_comparewithAll.m` 汇总这 351 个距离的变化：整体距离升高表示 chromosome territory decompaction，下降表示 compaction。

#### 6.4 A/B compartment score

代码先用 power law 拟合空间距离随基因组距离的期望变化：

$$
\widehat d(g)=b g^s.
$$

随后用 $d_{ij}/\widehat d(g_{ij})$ 归一化距离，计算 TAD 距离 profile 之间的 Pearson 相关矩阵，再对该矩阵做 PCA。第一主成分作为 compartment score；如果它与 gene density 负相关，就整体翻转符号，使正值对应基因更密集的 A compartment。

### 7. 核形态读出

`runM7_3dDAPIfeature.m` 对 DAPI z-stack 做三维阈值化，并用 `regionprops3` 提取体积、凸包体积、表面积、主轴、extent、solidity 和 voxel intensity。核内强度不均匀度定义为：

$$
\mathrm{COV}=\frac{\mathrm{SD}(I)}{\mathrm{mean}(I)}.
$$

论文发现 RB1/MYBPH knockout 使 DAPI 强度更均匀，TRIM36/EEPD1 knockout 使细胞核更不球形。跨扰动相关分析还显示：染色质越压缩，细胞核通常越球形。

**缺口：** `r6_analyzeDAPI.m` 会读取 `sphericity` 字段，但 archive 中没有任何脚本计算这个字段；Fig. 5l 的聚合物模拟代码也没有发布。这两部分均为 **Not found**。

### 8. 筛选结果与验证

研究共分析 17,304 个 G1 细胞、57,286 条 chr22 轨迹和 1,407,797 个三维位置，并从 137 个候选基因中报告 21 个 top hits。

主要结果包括：

- RB1、PCBP1、CHD7 knockout 导致 chr22 去压缩；GLDC、HOXB9、BRME1 knockout 导致压缩；
- 18 个染色质折叠 top hits 中有 9 个的距离变化与 A/B compartment pattern 显著相关；
- DDX24、MRVI1、ZNF114 的短程效应与 NIPBL 相关，提示可能部分涉及 loop extrusion；
- CHD7 knockdown 导致长程去压缩，而 CHD7 overexpression 产生相反的压缩效应；这一方向在 RPE-1/chr21、神经嵴祖细胞和 chromosome paint 中得到验证；
- PCBP1 和 ZNF114 的独立 CRISPR 验证分别支持去压缩和压缩方向。

这些相关性用于提出机制假说，但不能证明某个新因子直接参与 loop extrusion 或 compartment formation。论文也明确承认，CRISPR loss-of-function 经过多个细胞周期才显现，因而难以区分直接与间接调控。

### 9. 代码与论文究竟匹配到什么程度？

**总体：medium fidelity；端到端可复现性约 2/5。**

匹配较好的部分：

- BARC-FISH 图像处理、三色 digit 解码和一位错误纠正；
- Geminin/G1 筛选；
- 27-TAD 轨迹连接、补拟合和 cell/barcode 配对；
- 相邻距离、长程接触、全局距离、compartment PCA 与 DAPI COV。

必须保留的边界：

- Zenodo 内容是 MATLAB archive，不是带 commit 的 Git 软件仓库；
- 没有 lockfile、MATLAB/toolbox 版本、driver、tests、example raw data 或一条端到端运行命令；
- 大量脚本包含 `C:\...`、`G:\...` Windows 路径、固定 FOV 数、固定 TAD 数、特定 protospacer ID 和数据集阈值；
- codebook、annotation 和中间 MAT/DAX 文件缺失；
- 多个统计脚本虽然构造了 combined non-targeting control，却实际用 pooled all-trace/all-cell quantity 作为部分 fold change/test baseline，与论文图上的“sgRNA/control”表述并不完全一致；
- 本地没有 supplementary Markdown/PDF，Supplementary Methods 独有参数无法核验。

因此，这个 archive 很适合研究算法逻辑和做 paper–code 对照，但不能被描述为开箱即用、可独立复现全部图表的软件包。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Perturb-tracing

**Paper:** “Perturb-tracing enables high-content screening of multi-scale 3D genome regulators,” *Nature Methods* (2025), DOI `10.1038/s41592-025-02652-z`.

### Problem

The regulators of higher-order 3D genome organization are difficult to discover systematically because the phenotype is not one number: a perturbation may alter adjacent TADs, A/B compartment contacts, whole-chromosome compaction and nuclear shape in different ways. Earlier work either perturbed one candidate at a time, used plate-based imaging with relatively low-content locus-pair phenotypes—for example the high-throughput Oligopaint screen in *Nature* (2023)—or used scalable single-cell CRISPR readouts for local chromatin accessibility in *Nature Biotechnology* (2021) and *Nature Communications* (2021). None provided a pooled, same-cell perturbation screen with multi-scale 3D chromosome conformations (`paper.md:18-24,139-151,316-323`).

### What the paper introduces

Perturb-tracing combines:

- pooled CRISPR–Cas9 knockout screening;
- BARC-FISH, a ten-digit ternary RNA-barcode readout amplified by padlock-probe ligation and rolling-circle amplification;
- chromatin tracing of 27 TADs across chromosome 22;
- Geminin, DAPI and total-protein imaging for cell-cycle restriction and nuclear phenotypes.

The key innovation is that the sgRNA-linked barcode and the 3D chromatin phenotype are decoded in the **same individual cell**. The screen used 420 sgRNAs targeting 137 genes plus controls and generated 30 imaging readouts per perturbation, or 12,600 perturbation–target combinations (`paper.md:24,33-47`; Fig. 1; Extended Data Fig. 7).

### Method in brief

```text
sgRNA–barcode cell library
    -> BARC-FISH ten-round decoding + one-mismatch correction
    -> 27-TAD sequential DNA FISH and 3D focus fitting
    -> reciprocal-nearest-neighbor trace linking + missing-focus refinement
    -> cell registration and G1 filtering
    -> perturbation-specific distance/contact/compartment matrices
    -> hit calling, correlation fingerprints and nuclear morphology analysis
```

The archive directly implements much of this workflow in MATLAB. It uses a 2 µm reciprocal-nearest-neighbor cutoff and five-locus minimum for initial traces, refits missing foci within chromosome territories, removes assigned traces with radius of gyration below 0.5 µm, accepts uniquely nearest good barcodes with at most one mismatch, and defines long-range contact as a nonadjacent TAD pair separated by less than 0.5 µm. A/B compartments are obtained by genomic-distance normalization, a Pearson matrix and PCA with sign oriented to gene density.

### Evaluation and main findings

The screen analyzed 17,304 G1 cells, 57,286 chr22 traces and 1,407,797 3D positions (`paper.md:53`). NIPBL and CTCF produced the expected opposing adjacent-TAD phenotypes, providing an internal positive-control check.

The authors report 21 top candidate regulators across multiple scales. Examples include:

- RB1, PCBP1 and CHD7 knockout decompact chr22, whereas GLDC, HOXB9 and BRME1 knockout compact it;
- nine of 18 chromatin-folding hits have distance-change patterns correlated with A/B compartment structure;
- DDX24, MRVI1 and ZNF114 have short-range patterns correlated with NIPBL, suggesting partial association with loop extrusion;
- RB1 and MYBPH reduce DAPI intensity unevenness, while TRIM36 and EEPD1 reduce nuclear sphericity;
- across hits, greater chromatin compaction is associated with a more spherical nucleus.

CHD7 received the strongest orthogonal validation: knockdown decompacted chromatin, overexpression compacted it, and the long-range effect replicated in another chromosome/cell line, neural crest progenitors and whole-chromosome-paint measurements. PCBP1 and ZNF114 were also individually validated with opposing decompaction/compaction directions (Figs. 2–5; Extended Data Figs. 3–6).

### Interpretation and limitations

The high-content matrices allow perturbations to be grouped by phenotypic similarity and related to known mechanisms, but correlation with NIPBL or A/B scores does not establish direct molecular action. The authors also note that CRISPR loss-of-function effects accumulate over multiple cell cycles, so direct and indirect 3D-genome regulators cannot be cleanly separated (`paper.md:145-151`). The screen covers selected mostly nuclear/senescence-associated genes rather than a genome-wide library, knockout efficiency is incomplete, and high-stringency hit calling may create false negatives.

### Reproducibility assessment

**Code-paper fidelity: medium. End-to-end reproducibility: 2/5.**

What is available:

- a Zenodo archive of 78 MATLAB-oriented files covering BARC-FISH image processing, cell segmentation, G1 gating, chromosome-trace construction/refinement, perturbation grouping, distance/contact/compartment analyses, DAPI features and validation analyses;
- direct code matches for the central computational ideas and many thresholds;
- local paper Markdown and all 12 main/extended figure images.

What prevents a clean rerun:

- no MATLAB/toolbox specification, lockfile, top-level driver, tests, example raw `.dax`/`.mat` data or end-to-end command;
- numerous hard-coded Windows paths, protospacer IDs, dataset names and fixed thresholds;
- required codebook/annotation/intermediate files are absent;
- NGS sgRNA–barcode codebook generation, the nuclear-sphericity calculation and the Fig. 5 polymer simulation are **Not found**;
- several phenotype scripts compare perturbations with pooled all-trace/all-cell baselines even though paper plots are described relative to control, leaving exact figure reconstruction ambiguous;
- no local supplementary Markdown/PDF was acquired, so Supplementary Methods-only details remain unverified.

The release is therefore useful as a study-logic archive and for tracing paper-to-code correspondence, but it is not a portable or independently executable software package.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
