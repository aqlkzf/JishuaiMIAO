---
layout: default
permalink: /paper-atlas/spatio-darlin-44ca59e3/
title: "Spatio-DARLIN"
nav: false
description: "Spatio-DARLIN 的目标是在同一张完整组织切片中同时读出三类信息： 细胞状态：空间单细胞转录组； 空间位置：细胞在组织中的二维坐标； 克隆谱系：DARLIN 条形码记录的共同祖先关系。 论文指出，传统荧光谱系追踪保留空间结构，但条形码容量低且不能直接给出细胞状态；高多样性遗传条形码结合单细胞 RNA-seq 可以获得分子状态和谱系，但需要组织解离，破坏原位空间结构；"
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>Spatio-DARLIN</h1>
    <p>Spatio-DARLIN enables robust and efficient in situ lineage tracing in mice at single-cell resolution</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Spatio-DARLIN 方法中文解读

### 1. 这篇论文要解决什么问题？

Spatio-DARLIN 的目标是在**同一张完整组织切片**中同时读出三类信息：

1. **细胞状态**：空间单细胞转录组；
2. **空间位置**：细胞在组织中的二维坐标；
3. **克隆谱系**：DARLIN 条形码记录的共同祖先关系。

论文指出，传统荧光谱系追踪保留空间结构，但条形码容量低且不能直接给出细胞状态；高多样性遗传条形码结合单细胞 RNA-seq 可以获得分子状态和谱系，但需要组织解离，破坏原位空间结构；直接把空间转录组和谱系追踪拼在一起也不够，因为空间平台的谱系条形码捕获率低、单张切片细胞数很大导致同源条形码（homoplasy）风险升高，且测序错误、PCR/扩散、分割错误都可能制造假克隆（`paper.md:24-30`）。

因此，Spatio-DARLIN 的核心不是单一算法，而是一个**实验平台 + 条形码去噪/克隆调用计算流程**：先让 DARLIN 小鼠在 CA/TA/RA 三个基因组位点产生可表达的谱系条形码，再用 BMKMANU S3000 空间转录组芯片保留位置和转录组，最后用定制计算流程把低丰度、含噪的 DARLIN amplicon reads 转成可靠的单细胞克隆标签（`paper.md:47-59`）。

### 2. 为什么已有方法不够？

论文强调三类瓶颈：

- **空间 vs 信息深度的取舍**：经典荧光 reporter 有空间上下文，但条形码容量低，也缺乏转录组状态；单细胞高多样性条形码方法有信息深度，但解离后丢失原位空间（`paper.md:24`）。
- **空间转录组捕获率问题**：谱系条形码通常比普通基因表达更稀疏，空间平台低捕获率会使克隆图变得不完整（`paper.md:27`）。
- **错误会直接变成假克隆**：谱系条形码错误会把一个真实克隆拆碎；空间条形码或细胞分割错误会把细胞放到错误位置，形成空间上弥散的假克隆信号。Fig. 1f/g 直观展示了这种错误模式，预处理后 clone signal 变得更局部（`images/figure_01.png`; `paper.md:56`）。

论文还把 Spatio-DARLIN 与 iTracer、Space-TREX、KP-Tracer、PEtracer、SpaceBar 等空间谱系技术作文献比较；但作者明确提示这不是同一生物系统下的直接 side-by-side benchmark（`paper.md:116`; `images/figure_16.jpg`）。

### 3. Spatio-DARLIN 的新意是什么？

Spatio-DARLIN 把两个系统耦合起来：

- **DARLIN 小鼠**：在 Col1a1/CA、TIGRE/TA、Rosa26/RA 三个位点各有 10 个 CRISPR target array，Dox 诱导编辑后产生高多样性、可表达的谱系条形码（`paper.md:47-50`）。
- **BMKMANU S3000 空间转录组**：使用 2.5 µm poly(dT) microbeads，bead 间距 3.5 µm；论文认为该密度足以支持单细胞分辨率，因为小鼠细胞直径约 10 µm（`paper.md:47`）。
- **DARLIN amplicon 富集 + 去噪**：对空间 barcoded cDNA 做 targeted seminested PCR，提高 DARLIN 条形码捕获，再用专门计算流程去除测序/PCR/空间 carryover 等噪声（`paper.md:50-56`）。

Fig. 1a 把这条路线画成 CA/TA/RA、GEX 和 H&E 多层数据的整合图；Extended Data Fig. 2 则把 read 结构和计算预处理流程拆开显示（`images/figure_01.png`; `images/figure_08.jpg`）。

### 4. 计算流程总览

可以把计算部分理解成下面这条链：

```text
空间转录组 + DARLIN amplicon FASTQ
  → R1 解出 spot barcode / UMI，R2 解出 lineage barcode
  → 三步 QC：纠错、去 PCR artifact、去 capture-oligo carryover
  → allele calling：把校正后的 barcode 映射成 CA/TA/RA mutation pattern
  → spot-to-cell 聚合：按细胞分割 mask 汇总 UMI
  → 罕见 barcode 过滤：保留低生成概率 barcode
  → clone graph：共享罕见 barcode 的细胞连边，连通分量为 clone
  → 下游空间分析：肠道 unrolling、clone width、brain clone2vec、BANKSY、Wasserstein 等
```

需要特别区分：**论文描述了完整下游分析**，但主克隆代码仓库 `spatio_DARLIN` 主要是**预处理仓库**。代码可验证部分覆盖 R2 cutadapt、BSTMatrix 空间 barcode 解析、QC notebook、allele annotation、spot-to-cell 聚合；罕见 barcode 概率模型、clone graph、Wasserstein 验证、肠道/脑部下游图分析代码在主克隆仓库中 `Not found`（见 `doc_code.md` 的 searched scope）。

### 5. 输入、输出和主要假设

#### 输入

- **paired-end DARLIN amplicon reads**：R1 为 85 bp，包含 spot barcode 和 UMI；R2 为 350 bp，包含 lineage barcode 和 flanking sequence（`paper.md:267`; `images/figure_08.jpg`）。
- **空间图像和坐标**：BMKMANU S3000 的 H&E/ssDNA 图像、spot 坐标、细胞分割结果；论文的 mRNA 流程使用 BSTMatrix、STAR 和 Cellpose 生成 segmented cell count matrix（`paper.md:228-231`）。
- **CA/TA/RA locus 配置**：代码通过 `template` 判断 CA/TA/RA，并映射到 Col1a1/Rosa/Tigre（`spatio_DARLIN/snakefiles/BMKS3000.smk:7-16`; `spatio_DARLIN/bin/annotate_allele.py:11-20`）。

#### 输出

- **代码仓库可生成的输出**：多分辨率 spot-level 矩阵、cellbin 矩阵、allele 注释后的 features、clone-by-spots / clone-by-cells 类矩阵（`spatio_DARLIN/README.md:1-10`, `177-206`; `spatio_DARLIN/snakefiles/BMKS3000.smk:156-187`）。
- **论文级输出**：可靠 clone、空间克隆图、肠道克隆宽度/耦合、脑区 clone2vec/BANKSY/Wasserstein 分析等（`paper.md:279-336`）。这些后半段分析代码未在主仓库中找到。

#### 主要假设

- DARLIN 三个位点能提供足够多样、可表达的 barcode，并且低生成概率 barcode 可降低 homoplasy（`paper.md:279-285`）。
- 2.5 µm bead 与准确细胞分割可把 spot 信号聚合到单细胞尺度（`paper.md:47`, `276`）。
- 可靠条形码恢复率目前约 25–50%，且随组织和 replicate 变化；二维切片会对子克隆进行 subsampling，可能带来解释偏差（`paper.md:171-174`）。

### 6. 预处理细节：从 FASTQ 到 cell-by-barcode 矩阵

#### 6.1 R2 lineage barcode 提取

论文说 lineage barcode 从 R2 用 cutadapt v5.0 提取（`paper.md:267`）。代码中 `run_cutadapt.py` 做得更严格：

- 先根据 template 选择 Col1a1/Rosa/Tigre 的 locus-specific primer；
- 只取 15 bp primer；
- 对 R2 的 3′ 和 5′ primer 都要求 full-length overlap，并设置 `--error-rate 0` 和 `--discard-untrimmed`（`spatio_DARLIN/bin/run_cutadapt.py:14-28`, `47-67`）。

这是一个**代码可见但论文没有展开的实现细节**：实际 repo 默认比论文文字描述的“用 cutadapt 提取”更严格。

#### 6.2 R1 spot barcode / UMI 解析

论文说 spot barcode 和 UMI 从 R1 提取并由 BSTMatrix 校正（`paper.md:267`）。代码路径是：

- `write_BMK_config.py` 写 BSTMatrix 配置，指向 trimmed FASTQ、H&E 图像、输出目录和 barcode type（`spatio_DARLIN/bin/write_BMK_config.py:10-47`）；
- Snakemake 调用 `BSTMatrix -c ... -s 1` 做 spatial barcode / UMI parsing（`spatio_DARLIN/snakefiles/BMKS3000.smk:69-86`）。

#### 6.3 三步 QC

论文的关键计算创新之一是三步 QC（`paper.md:267-270`），repo 中由 Snakemake 通过 papermill 调用 `QC/BMKS3000.ipynb` 实现（`spatio_DARLIN/snakefiles/BMKS3000.smk:88-109`; `spatio_DARLIN/darlin/settings.py:1-7`）。

##### 第 1 步：lineage barcode 纠错

Notebook 按 `(SR, UR, LB_len)` 分组，其中 `SR` 是 corrected spot barcode，`UR` 是 corrected UMI，`LB_len` 是 lineage barcode 长度。每组用 `umi_tools` directional clustering 纠错；距离阈值为

$$
\text{threshold}=\left\lceil \text{LB\_len}\times\text{LB\_error\_rate}\right\rceil,
$$

并且至少为 1。默认 `LB_error_rate=0.02`（`spatio_DARLIN/QC/BMKS3000.ipynb:20-43`, `252-295`）。这对应论文的“length-aware Hamming distance threshold, error rate 0.02”（`paper.md:270`）。

##### 第 2 步：去除 PCR amplification artifact

同一个 `(SR, UR)` 分子如果支持多个 lineage barcode，说明可能有 chimera 或 amplification artifact。Notebook 计算每个 corrected lineage barcode 在该 molecule 内的 read fraction：

$$
\text{reads\_fraction}_{i}=\frac{\text{reads}_{i}}{\sum_j \text{reads}_{j}}.
$$

只保留

$$
\text{reads\_fraction}_{i}\ge 0.8.
$$

代码证据见 `spatio_DARLIN/QC/BMKS3000.ipynb:341-374`；论文用同样的“≥80% reads within a molecule”描述该过滤（`paper.md:270`）。

##### 第 3 步：去除 capture-oligo carryover artifact

对于每个 spot barcode `SR`，Notebook 计算

$$
k=\frac{n_{\mathrm{reads}}}{n_{\mathrm{UMIs}}}.
$$

论文保留 $k\ge10$ 的 spot（`paper.md:270`）。代码中还额外要求单条 molecule 的 supporting reads `reads >= reads_cutoff`，默认 10；最终过滤为 `k >= slope_cutoff` 且 `reads >= reads_cutoff`（`spatio_DARLIN/QC/BMKS3000.ipynb:425-524`）。README 示例配置也把 `slope_cutoff: 10` 与 `reads_cutoff: 10` 作为默认说明（`spatio_DARLIN/README.md:151-174`）。

### 7. Allele calling 与 spot-to-cell 聚合

QC 后，论文把 DARLIN barcode 映射到参考序列以决定 mutation pattern，并说明 MATLAB-based CARLIN 很耗时，所以放到去噪之后再做以提高可扩展性（`paper.md:273`）。代码有两条路径：

- **Python/darlinpy 路径**：`BMKS3000.smk` 调用 `annotate_allele.py`，把 `CA/TA/RA` 映射到 `Col1a1/Tigre/Rosa`，再调用 `darlinpy.analyze_sequences` 生成 allele 注释（`spatio_DARLIN/snakefiles/BMKS3000.smk:111-120`; `spatio_DARLIN/bin/annotate_allele.py:11-33`）。
- **MATLAB/CARLIN 路径**：`BMKS3000_matlab.smk` 在 QC 后准备 slim FASTQ，再调用 Custom_CARLIN / MATLAB 路线（`spatio_DARLIN/snakefiles/BMKS3000_matlab.smk:116-156`）。

随后，论文把同一细胞 mask 中所有 spot 的 barcode UMI 汇总成 cell-by-barcode UMI matrix（`paper.md:276`）。代码的 `group_spots_to_cells` rule 使用 segmentation 输出 `all_barcode_num.txt` 和 `barcodes_pos.tsv.gz`，调用 BSTMatrix 的 `cell_split/get_mtx.py` 生成 cell-level matrix（`spatio_DARLIN/snakefiles/BMKS3000.smk:136-154`）。

### 8. 罕见 barcode 与 clone graph：论文算法 vs 代码状态

论文定义了 clone calling 的下游算法（`paper.md:279-285`）：

1. 对每个 locus 的 barcode 估计生成概率 $\rho$；
2. 当

$$
\rho\le \rho_*,\quad \rho_*=1\times10^{-5}
$$

时，把该 barcode 视为 rare barcode；论文说这个 cutoff 可在 FDR 0.05 下可靠标记约 10,000 个 clones（`paper.md:282`）。

3. 建立 cell graph：如果两个细胞共享至少一个 rare barcode，就连一条边；
4. graph 的 connected components 被视为 clones；
5. 保留每个 CA/TA/RA locus 不超过 3 个 distinct alleles 的 clones，并排除 >100 cells 的异常大 clones（`paper.md:285`）。

**代码状态：`Not found`。** 主克隆仓库中未找到生成概率 $\rho$、allele bank lookup、rare/common barcode 过滤或 connected-component clone graph 的实现。已搜索范围包括 `README.md`、`snakefiles/*.smk`、`bin/*.py`、`QC/BMKS3000.ipynb`、`darlin/*.py`、`doc/`、`test/`，以及 `rho/prob/rare/connected/component` 等关键词（详见 `doc_code.md`）。因此，文档中必须把这些步骤写成**论文描述/图像支持**，不能写成主仓库可复现代码。

### 9. 验证和下游分析

#### 9.1 相邻切片验证

论文用 PSI、DSI 与三个相邻 MSI 切片验证 homoplasy 与 clone reproducibility。不同肠段共享 rare barcode 约 1%，相邻 MSI 切片共享约 50%；真实 clone 的 Wasserstein distance 明显小于 shuffled barcode control（`paper.md:68-76`, `288-296`）。Fig. 2 的图像显示 MSI 相邻切片之间的共享比例和 heatmap 对角结构，以及 observed vs shuffled 的 Wasserstein violin plot（`images/figure_02.png`）。

**代码状态：`Not found`。** 主仓库没有找到 Wasserstein validation 脚本。

#### 9.2 小肠 Swiss-roll unrolling 与 clone width

论文手动在 QuPath 画绿色 serosa reference line，用 RGB threshold 提取参考线，构建 $k=10$ kNN graph，再用 Dijkstra 得到沿 serosa 的累计距离作为 proximal–distal $x$ 坐标；细胞通过 40 pixel 邻域迭代投影得到 crypt–villus $y$ 坐标（`paper.md:246-260`）。Extended Data Fig. 4 直接画出了这 4 步流程（`images/figure_10.jpg`）。

Clone width 的估计为：沿 proximal–distal 轴做 KDE，按 half-max density 拟合 step function，再取 autocorrelation 降到 0.1 的 lag 作为 clone width（`paper.md:299-300`; `images/figure_10.jpg`）。

**代码状态：`Not found`。** 主仓库未找到 QuPath/Dijkstra/unrolling 或 clone-width KDE/autocorrelation 脚本。

#### 9.3 脑部 clone embedding、空间域和 hypothalamus 距离

论文对脑样本使用 clone2vec：把 clone 当作 token、cells 当作 context，训练 10 维 embedding，再 UMAP 投影，SNN graph ($k=15$) + Leiden resolution 1.0 得到 clone clusters（`paper.md:327-330`）。Fig. 4 显示 64,948 个 mRNA-QC cells、49.5% reliable lineage barcode recovery、12,211 clones、5,072 multi-cell clones，以及 2,827 clones 的 17 个 clonal clusters（`images/figure_04.png`; `paper.md:109-120`）。

对 hypothalamus，论文用 BANKSY 定义 spatial domains，并用对称 Wasserstein 距离衡量 clone 空间相似性：

$$
d_{A,B}=\frac{W(A\to B)+W(B\to A)}{2}.
$$

再用 Ward 层次聚类分析空间 clone groups（`paper.md:333-336`）。Fig. 6 显示 hypothalamus 空间域、within-clone distance 更短、Wasserstein heatmap 和局部 clone subclusters（`images/figure_06.png`; `paper.md:146-159`）。

**代码状态：`Not found`。** clone2vec、BANKSY、principal curve、hypothalamus symmetric Wasserstein/hclust 等下游分析脚本未在主仓库中找到。

### 10. 主要结果怎样支撑方法？

- **小肠捕获效率与 QC**：Y007 proximal small intestine 中，论文报告 146,584 个 mRNA-QC cells，51,459 个细胞检测到至少一个 DARLIN barcode（35.1%），约 25% 的所有细胞通过 stringent reliable clone QC（`paper.md:53-59`; `images/figure_01.png`）。
- **同源条形码风险较低**：非相邻 PSI/DSI 控制与 MSI 的 rare barcode overlap 约 1%，相邻 MSI 切片约 50%，支持低 homoplasy 与空间可重复 clone detection（`paper.md:73-76`; `images/figure_02.png`）。
- **肠道动态**：unrolling 后，epithelial clones 沿 proximal–distal 轴局部化，clone width 约 176 µm；1–3 周 chase 中 crypt–villus zones 的 clonal coupling 增强，符合 stem-cell neutral drift 解释（`paper.md:81-97`; `images/figure_03.png`）。
- **脑部应用**：E10 标记后成年脑中，论文报告 64,948 个 QC cells、49.5% reliable barcode recovery、12,211 clones；clone2vec clusters 与 cortex、hippocampus、interbrain、ventricular/meningeal 区域相关（`paper.md:109-120`; `images/figure_04.png`）。
- **发育解释**：cortex 显示 radial/cone-like clones，hippocampus CA clone 有局部和对称模式，hypothalamus 中 53.6% 的 233 个 clone 被限制在单一 spatial domain，提示 E10 时已有空间预模式（`paper.md:126-159`; `images/figure_05.png`, `images/figure_06.png`）。
- **bulk 验证**：bulk gDNA 分析用 $\alpha\times\beta$ 采样效率归一化 clone size，支持 cortex/hippocampus clone expansion 大于 thalamus/hypothalamus（`paper.md:121-123`, `338-342`; `images/figure_15.jpg`）。主仓库未包含该 bulk pipeline；论文指向外部 `darlinpy` pipeline（`paper.md:338-342`）。

### 11. 可复现性：应该怎样读这个代码仓库？

主仓库 `spatio_DARLIN` 的 README 明确说它是 Spatio-DARLIN 空间谱系追踪数据的 Snakemake **preprocessing pipeline**，包括 lineage barcode identification/QC、spatial barcode parsing、allele annotation、spots-to-cells grouping 和最终矩阵生成（`spatio_DARLIN/README.md:1-10`）。论文 Code availability 也只承诺“scripts for data preprocessing”（`paper.md:365-366`）。因此，合理的复现边界是：

- **可复现/代码支持较强**：amplicon FASTQ 到 spot/cell barcode matrices 的预处理流程；R2 cutadapt；R1/BSTMatrix；三步 QC notebook；allele annotation；spot-to-cell aggregation。
- **需要外部数据和环境**：GEO 数据、BMKMANU/BSTMatrix、Snakemake/Conda、MATLAB/CARLIN 或 darlinpy、segmentation inputs（`spatio_DARLIN/README.md:12-21`, `104-132`, `208-224`）。
- **主仓库未找到**：罕见 barcode 生成概率模型、clone graph、Wasserstein validation、肠道 unrolling/clone width/CoSpar coupling、脑部 clone2vec/BANKSY/空间距离聚类、bulk regional clone-size validation。

所以，本 workspace 的代码-论文匹配结论是：**预处理 fidelity 为中高，完整论文复现 fidelity 为中低**。这不是简单矛盾，因为论文和 README 都把公开代码限定在 preprocessing；但如果要复现所有 figures，需要 GEO 数据、Supplementary Table 2 参数和未在主仓库中发现的下游分析脚本。

### 12. 阅读本文时最容易混淆的点

1. **“barcode recovery” 与 “clone calling” 不是同一步。** 前者是从 noisy reads 中得到可靠 cell-by-barcode matrix；后者还要根据 barcode rarity 和 graph connected components 合并细胞成 clones。
2. **“rare barcode” 是为了控制 homoplasy。** 阈值 $\rho_* = 10^{-5}$ 不是表达量阈值，而是生成概率 cutoff。
3. **代码仓库主要覆盖 preprocessing。** Fig. 3–6 的许多 biological analyses 有纸面方法和图像证据，但主 repo 没有对应实现。
4. **QC notebook 已经被源码验证。** 早期 evidence map 中对 `darlin.settings.QC_dir` 的不确定性已由 `spatio_DARLIN/QC/BMKS3000.ipynb` 直接读证据解决；剩余 `Not found` gaps 是下游 rare-barcode/clone graph/validation/biological analysis 代码，而不是 QC notebook。
5. **2D 切片是生物解释限制。** 论文自己指出二维切片会 subsample clones 并可能引入偏差，需要结合切片方向或 3D reconstruction 解释（`paper.md:171-174`）。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spatio-DARLIN Summary

### What problem does this solve?

Spatio-DARLIN is designed to recover **cell state, spatial position and clonal ancestry in the same intact mouse tissue section**. The paper argues that classical fluorescent lineage tracing keeps spatial context but has low barcode capacity and lacks cell-state information, whereas high-diversity single-cell lineage tracing destroys native spatial architecture through dissociation (`paper.md:24`). A direct combination of spatial transcriptomics and lineage tracing is also insufficient because spatial platforms have low lineage-barcode capture, large cell counts increase homoplasy risk, and errors in barcode sequence / diffusion / library prep / cell segmentation can create false clone assignments (`paper.md:27`).

### What does Spatio-DARLIN introduce?

The method combines the high-diversity DARLIN mouse with BMKMANU S3000 spatial transcriptomics. DARLIN contributes three edited target arrays — Col1a1/CA, TIGRE/TA and Rosa26/RA — while the S3000 chip contributes dense 2.5-µm poly(dT) beads spaced 3.5 µm apart; the paper argues that this density supports single-cell-resolution spatial lineage tracing because mouse cells are ~10 µm in diameter (`paper.md:47`). Targeted seminested PCR enriches DARLIN barcodes from spatially barcoded cDNA, and a dedicated computational pipeline denoises barcode calls before clone analysis (`paper.md:47-56`). Fig. 1 (`images/figure_01.png`) visually shows the full assay flow from mouse/tissue/chip through CA/TA/RA/GEX/H&E layers.

### High-level computational method

The central computation is a **barcode recovery and denoising pipeline**:

1. Read 1 contains spot barcode and UMI; read 2 contains the lineage barcode and flanking sequence (`paper.md:267`; Extended Data Fig. 2 image `images/figure_08.jpg`).
2. Extract lineage barcodes from R2 using cutadapt and extract/correct spot barcodes and UMIs from R1 using BSTMatrix (`paper.md:267`). The cloned code matches this preprocessing: `run_cutadapt.py` trims R2 with locus-specific primers (`spatio_DARLIN/bin/run_cutadapt.py:14-67`), and Snakemake calls BSTMatrix for barcode parsing (`spatio_DARLIN/snakefiles/BMKS3000.smk:69-86`).
3. Apply three-step QC: lineage-barcode correction using umi_tools directional clustering with error rate 0.02; retain molecule-level lineage calls supported by at least 80% of reads; retain spots with read/UMI ratio $k\ge10$ (`paper.md:270`). The repo-local `QC/BMKS3000.ipynb` implements these thresholds and filters (`spatio_DARLIN/QC/BMKS3000.ipynb:20-43`, `252-295`, `341-374`, `425-524`).
4. Map corrected barcodes to alleles after denoising, either with MATLAB/CARLIN as described in the paper or the repo's Python `darlinpy` alternative (`paper.md:273`; `spatio_DARLIN/snakefiles/BMKS3000_matlab.smk:116-156`; `spatio_DARLIN/bin/annotate_allele.py:11-33`).
5. Aggregate barcode UMIs across spots belonging to the same cell mask to make a cell-by-barcode matrix (`paper.md:276`; `spatio_DARLIN/snakefiles/BMKS3000.smk:136-154`).
6. Paper-only downstream steps then filter rare barcodes with $\rho\le\rho_*$, $\rho_*=1\times10^{-5}$, connect cells sharing rare barcodes, and call connected components as clones (`paper.md:279-285`). Code for this rare-barcode probability model and clone graph was **not found** in the primary cloned repo.

### Main results and evaluation

- **Intestine performance:** In Y007 proximal small intestine, the paper reports 146,584 high-quality cells, 51,459 cells with at least one detectable DARLIN barcode (35.1%), and approximately 25% of all profiled cells passing stringent reliable-clone QC (`paper.md:53-59`). Fig. 1 and Extended Data Fig. 3 (`images/figure_01.png`, `images/figure_09.jpg`) visually show barcode QC, rare/common barcode behavior and clone counts.
- **Clone detection accuracy:** Adjacent MSI sections share roughly half of rare barcodes, whereas non-adjacent PSI/DSI controls show ~1% overlap. Observed same-clone Wasserstein distances are lower than shuffled controls (`paper.md:73-76`; Fig. 2 image `images/figure_02.png`).
- **Intestinal dynamics:** Computational unrolling maps the Swiss roll to proximal-distal and crypt-villus axes; epithelial clones are localized along the proximal-distal axis with clone width around 176–178 µm, and zonal clonal coupling increases over 1–3 weeks in a pattern consistent with neutral drift (`paper.md:81-97`; Fig. 3 and Extended Data Fig. 4/5 images).
- **Brain performance and structure:** In adult brain after E10 labeling, the paper reports 64,948 QC cells, 49.5% reliable lineage barcode recovery, 12,211 clones, and 5,072 multi-cell clones (`paper.md:113-116`). Clone2vec embedding separates 17 clonal clusters enriched in cortex, hippocampus, interbrain or ventricular/meningeal regions (`paper.md:119`; Fig. 4 image `images/figure_04.png`).
- **Developmental interpretations:** The paper identifies radial/cone-like cortical clones, localized and symmetric hippocampal CA clones, and hypothalamic clone clusters aligned with spatial domains/nuclei (`paper.md:126-159`; Fig. 5/6 images). Bulk gDNA validation supports larger cortex/hippocampus clone sizes than thalamus/hypothalamus (`paper.md:121-123`; Extended Data Fig. 9 image `images/figure_15.jpg`).

### Reproducibility and code-paper match

**Reproducibility rating: 3/5 for preprocessing, 1–2/5 for full paper reproduction from this repo alone.**

What is reproducible from the primary repo:

- Snakemake preprocessing for properly formatted BMKMANU S3000 amplicon data (`spatio_DARLIN/README.md:1-10`, `208-224`).
- Locus-specific cutadapt trimming, BSTMatrix spatial barcode parsing, QC notebook, allele annotation and spot-to-cell aggregation (`doc_code.md`).
- Test configs/scripts exist, but they use reduced thresholds (`slope_cutoff`/`reads_cutoff` 4) for test data while the README/paper defaults use 10 (`spatio_DARLIN/test/test_BMKS3000/config-CA.yaml:12-20`; `spatio_DARLIN/README.md:151-174`).

What is missing from the primary repo:

- Rare-barcode probability model / allele-bank lookup and connected-component clone graph.
- Adjacent-section Wasserstein validation scripts.
- Intestine unrolling, clone-width estimation and CoSpar clonal-coupling scripts.
- Brain clone2vec, BANKSY, tangential-coordinate, hypothalamus Wasserstein clustering and bulk clone-size analysis code.

The paper's code-availability section only promises **scripts for data preprocessing** (`paper.md:365-366`), so these missing downstream items are consistent with a preprocessing-only repo rather than necessarily a contradiction. Full figure reproduction would require GEO datasets (`paper.md:360`), supplementary analysis parameters and downstream analysis scripts not found in the primary snapshot.

### Key limitations to keep in mind

The paper itself notes that reliable lineage barcode recovery is currently ~25–50% and varies across tissues/replicates, and that 2D tissue sectioning subsamples clones and may introduce interpretation bias (`paper.md:171`). The main documentation gap is not the experimental concept but the separation between **published preprocessing code** and **unpublished/not-cloned downstream analysis code**.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
