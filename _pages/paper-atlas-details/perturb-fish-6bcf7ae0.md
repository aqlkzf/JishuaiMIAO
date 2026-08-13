---
layout: default
permalink: /paper-atlas/perturb-fish-6bcf7ae0/
title: "Perturb-FISH"
nav: false
wide: true
description: "这篇 Cell 2025 论文提出 Perturb-FISH：一种把 pooled CRISPR 扰动、原位 guide RNA 读取、MERFISH 空间转录组和可选功能成像放到同一单细胞体系里的技术平台（PAPERMD:1-5, PAPERMD:13-17）。 传统 Perturb-seq 这类单细胞 CRISPR 筛选可以把“哪个基因被扰动”和“细胞表达谱如何变化”连接起来，但细胞需要被解离，因此失去空间邻近关系。"
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
      <span>Cell · 2025</span>
    </div>
    <h1>Perturb-FISH</h1>
    <p>Simultaneous CRISPR screening and spatial transcriptomics reveal intracellular, intercellular, and functional transcriptional circuits</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/lbinan/Perturb-FISH" target="_blank" rel="noopener noreferrer" aria-label="Open code for Perturb-FISH">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Perturb-FISH 方法中文解释

### 1. 这篇文章要解决什么问题？

这篇 *Cell* 2025 论文提出 Perturb-FISH：一种把 pooled CRISPR 扰动、原位 guide RNA 读取、MERFISH 空间转录组和可选功能成像放到同一单细胞体系里的技术平台（`paper source:1-5`, `paper source:13-17`）。

传统 Perturb-seq 这类单细胞 CRISPR 筛选可以把“哪个基因被扰动”和“细胞表达谱如何变化”连接起来，但细胞需要被解离，因此失去空间邻近关系。光学 pooled screen 保留图像信息，但过去没有很好地接上高通量单细胞转录组 readout。论文在引言中明确指出：如果想研究细胞之间的遗传相互作用，就必须同时知道扰动、表达和空间邻域（`paper source:25-27`）。

Perturb-FISH 的目标就是让每个细胞同时拥有这些信息：

- 它收到的 guide / perturbation 是什么；
- 它的目标基因表达谱是什么；
- 它在空间上在哪里、周围有哪些细胞；
- 如果做了 live imaging，它的功能表型是什么，比如钙活动轨迹。

### 2. 已有方法为什么不够？

论文讨论了几类前置技术：

- **Perturb-seq / 单细胞测序式 pooled CRISPR screen**：可以大规模连接扰动和表达，但细胞被解离，不能分析邻居细胞、局部密度或组织结构（`paper source:25-27`）。论文引用的 Perturb-seq 是 *Cell* 2016，CROP-seq/相关单细胞 CRISPR 读出是 *Nature Methods* 2017 等（`paper source:300-302`）。
- **Optical pooled screen**：可以在显微图像中读出 guide 或表型，但过去没有和高度复用的单细胞转录组 readout 结合（`paper source:27-27`）。
- **Perturb-map**：把 gRNA perturbation 和 10x Visium 空间转录组结合，但用 protein barcode，牺牲了普通 pooled cloning 的一些优势，而且 Visium 空间分辨率限制了非克隆生长细胞的应用（`paper source:27-27`）。
- **MERFISH**：可以高通量读 mRNA，但普通 guide RNA 只有 20 bp，不能像 mRNA 那样被多条 encoding probe 平铺，因此需要新的 guide 放大策略（`paper source:29-29`）。

所以核心缺口不是“没有 CRISPR 筛选”，而是缺少一个可以在同一个细胞上同时读出 **guide identity + transcriptome + spatial context + functional phenotype** 的平台。

### 3. Perturb-FISH 的核心创新

Perturb-FISH 的关键设计是把 guide 本身变成可以原位读取的 barcode。

论文把常用的 `lentiguide-puro` 向量改造为 U6-T7 结构：U6 promoter 在活细胞中表达 guide、驱动 CRISPR 扰动；T7 promoter 在固定后的细胞里启动局部原位转录，产生许多 guide 区域拷贝，便于成像检测（`paper source:37-39`, `paper source:183-187`）。

因为 20 bp guide 太短，作者把探针靶区扩展到 guide 序列加上 scaffold 前 10 bp，使 hybridization 区域达到 30 bp，和 MERFISH probe 的长度尺度匹配（`paper source:207-209`）。guide identity 用 MERFISH 风格的 Hamming weight 4 / Hamming distance 4 codebook 编码：每个 guide 在 15 个 imaging bits 中亮 4 个，任意两个 barcode 至少差 4 bits，因此可以做单 bit 纠错，并丢弃双错误导致的歧义 barcode（`paper source:203-205`）。

可以把创新理解成：

```text
普通 pooled CRISPR guide
        |
        |  加入 T7 promoter，固定后原位放大 guide 区域
        v
可被显微镜读取的 guide barcode
        |
        |  与 MERFISH mRNA readout 兼容
        v
同一细胞中同时得到 perturbation identity 和 transcriptome
```

### 4. 输入、输出和数据结构

#### 输入

实验输入是 pooled guide library、选定的 MERFISH gene panel、细胞或组织样本，以及可选的 live imaging 数据。

论文中的三套主要数据是：

| 数据集 | 扰动对象 | 转录组 readout | 额外信息 |
|---|---|---|---|
| THP1 LPS response | 35 个 target genes、74 条 gRNA | 130 个选定基因 | matched Perturb-seq、局部密度、邻居效应（`paper source:43-49`, `paper source:171-173`） |
| hIPSC astrocyte | 127 个 ASD risk / control targets | 485 个基因 | ATP 刺激后的钙活动 live imaging（`paper source:65-75`, `paper source:175-175`, `paper source:265-271`） |
| A375 tumor xenograft | NF-kB pathway 的 35 个 target genes | 500-gene immune-oncology panel | tumor/T cell 空间邻域（`paper source:89-95`, `paper source:177-177`） |

#### 输出

最终不是一个单一模型文件，而是一组 per-cell 表格和 effect estimates：

- `cell x gene` 表达矩阵；
- `perturbation x cell` 或 `target x cell` 设计矩阵；
- cell segmentation mask；
- neighbor matrix / number of neighbors；
- FR-Perturb 输出的 LFC 表和 q-value 表；
- astrocyte calcium phenotype cluster 和 enrichment；
- tumor/T-cell neighbor design matrix。

论文明确写到，count table 是把每个 cell mask 内 decoded transcripts 加总得到的，perturbation design matrix 也用类似方式组装（`paper source:243-245`）。FR-Perturb 输出两张表：一张是 LFC，一张是 q value（`paper source:277-277`）。

### 5. 从样本到表格：实验和图像处理流程

完整流程可以这样理解：

```text
pooled guide library
        |
        v
U6-T7 guide vector 感染细胞，产生 CRISPR KO / CRISPRi 扰动
        |
        v
固定细胞或组织，T7 原位转录放大 guide 区域
        |
        v
guide + mRNA encoding probes hybridization
        |
        v
多轮 readout probe staining / imaging / cleavage
        |
        v
图像配准、背景校正、spot enhancement、barcode decoding
        |
        v
细胞分割，spot 分配到 cell mask
        |
        v
表达矩阵 + 扰动矩阵 + 空间邻域矩阵
```

论文的 STAR Methods 说明了 guide 图像如何处理：图像配准、背景校正、Gaussian filter 增强 spot、二值化、尺寸/eccentricity 过滤、Z-stack max projection，然后把每个 putative guide 的亮/暗模式和 codebook 比较（`paper source:227-229`）。

代码中，THP1 的图像预处理脚本 `filterthp1.m` 直接实现了这些步骤：读取 `.dax` 图像，配准不同 imaging cycles，除以 background image 校正照明，用小尺度和大尺度 Gaussian filter 的差值增强 spot，并写出 15 个 bit 的 max-projected TIFF（`Perturb-FISH-repo/thp1Preprocessing/filterthp1.m:38-92`）。`decodeThisBinaryImagedontcheckrepeatsbutlookfurther.m` 把二值图像 max-project 后找 spot centroid，只保留 3-5 个 bit 有信号的 spot（`Perturb-FISH-repo/thp1Preprocessing/decodeThisBinaryImagedontcheckrepeatsbutlookfurther.m:1-27`）。`getgeneIDfromBWmanualthresholdsclaedlowestdontcheckrepeats.m` 读取 codebook，计算 spot barcode 到每个 codeword 的距离，并输出 guide ID（`Perturb-FISH-repo/thp1Preprocessing/getgeneIDfromBWmanualthresholdsclaedlowestdontcheckrepeats.m:1-42`）。

细胞分割方面，论文说 THP1 使用 watershed：核 centroid 做 seed，MERFISH transcript density map 做 basin（`paper source:235-237`）。代码 `finishglobalcellmosaic.m` 读取 seed mosaic 和 blurred transcript-density image，运行 watershed，再把 mRNA spot 和 guide spot 分配到每个 cell mask，生成 transcript count table 和 perturbation table（`Perturb-FISH-repo/thp1Preprocessing/finishglobalcellmosaic.m:1-25`, `Perturb-FISH-repo/thp1Preprocessing/finishglobalcellmosaic.m:80-128`）。

### 6. 从表格到扰动效应：FR-Perturb 层

Perturb-FISH 本身生成的是 per-cell multimodal tables。要从这些表格中估计“某个 perturbation 对某个 gene 的影响”，论文使用已有工具 FR-Perturb（`paper source:43-43`, `paper source:275-287`）。

THP1 的 paper 参数是：rank 34、lambda1 = 0、lambda2 = 0、`log_exp_baseline = 2.7`、total transcript count 作为 covariate、10,000 permutations、Benjamini-Hochberg 校正，并且去掉 droplet scRNA-seq 常用的每细胞 10,000 counts normalization（`paper source:275-277`）。

代码里 `cleanrun_FR_PerturbnoNorm.py` 是这个 no-normalization FR-Perturb runner。它读取 h5ad 表达矩阵和 perturbation design matrix（`Perturb-FISH-repo/THP1analysis/cleanrun_FR_PerturbnoNorm.py:245-249`），对表达做 log1p、covariate regression 和 control-centering，其中 `scanpy.pp.normalize_total(dat, target_sum = 10000)` 被注释掉，符合 paper 说的 no-normalization 修改（`Perturb-FISH-repo/THP1analysis/cleanrun_FR_PerturbnoNorm.py:262-278`）。随后代码用 `spams.trainDL` 和 `spams.lasso` 做 factorize-recover，得到扰动效应矩阵 `B`（`Perturb-FISH-repo/THP1analysis/cleanrun_FR_PerturbnoNorm.py:280-296`），再通过 permutation p-values、BH q-values 和 LOWESS scaling 输出 LFC/q-value 表（`Perturb-FISH-repo/THP1analysis/cleanrun_FR_PerturbnoNorm.py:298-363`）。

关键变量可以这样对应：

| 论文概念 | 代码变量 | 位置 |
|---|---|---|
| 细胞 x 基因表达矩阵 | `M`, `adata.X`, `dat.X` | `THP1analysis/analyze_perturb-fish.py:153-169`, `cleanrun_FR_PerturbnoNorm.py:245-249` |
| perturbation design matrix | `P`, `p_mat_pd`, `p_mat` | `THP1analysis/analyze_perturb-fish.py:153-171`, `cleanrun_FR_PerturbnoNorm.py:247-249` |
| covariate | `total_counts`, `cov_mat` | `cleanrun_FR_PerturbnoNorm.py:257-268` |
| FR-Perturb factorization | `W`, `U_tilde`, `U`, `B` | `cleanrun_FR_PerturbnoNorm.py:280-296` |
| 显著性 | `pvals`, `qvals` | `cleanrun_FR_PerturbnoNorm.py:298-363` |

### 7. THP1：先证明方法能复现 Perturb-seq，再利用空间信息

THP1 数据是 Perturb-FISH 的主要验证集。论文先把 THP1-derived macrophages 的 LPS response 做 Perturb-FISH，并和已发表 matched Perturb-seq 数据比较（`paper source:43-45`）。结果包括 replicate 一致性、和 Perturb-seq 的相关性、cluster structure 的一致性，以及 downsampling power analysis（`paper source:45-49`）。本地 Figure 3 图像中可以看到 replicate scatter、Perturb-seq/FISH scatter、FISH/Seq heatmap 和 cell-number power curve。

代码 `analyze_perturb-fish.py` 支持这些分析：它构建 AnnData 和 design matrix，读取 Perturb-seq 的 LFC/q 表，做随机 split consistency check，并绘制 Perturb-seq vs Perturb-FISH scatter / heatmap（`Perturb-FISH-repo/THP1analysis/analyze_perturb-fish.py:49-83`, `Perturb-FISH-repo/THP1analysis/analyze_perturb-fish.py:153-178`, `Perturb-FISH-repo/THP1analysis/analyze_perturb-fish.py:226-257`）。

更重要的是，Perturb-FISH 可以做 Perturb-seq 做不了的空间问题。论文把 THP1 按邻居数分成 low density（2 个或更少邻居）和 high density（3 个或更多邻居），发现一些 perturbation effects 依赖局部密度（`paper source:53-57`, `paper source:247-249`, `paper source:279-279`）。代码中这个阈值直接出现为 `n < 3` 和 `n >= 3`，并且分别写出低/高密度子集后跑 FR-Perturb（`Perturb-FISH-repo/THP1analysis/analyze_perturb-fish.py:103-120`, `Perturb-FISH-repo/THP1analysis/analyze_perturb-fish.py:283-290`）。

论文还研究“一个被扰动细胞是否影响邻居 control cell 的表达”，例如 MYD88 KO 邻居让 control cell 的 TNF/CD14 上调（`paper source:59-61`）。代码里 `Call_neighborEffect_analysis.txt` 保存了对 `extrinsicMerfish.h5ad` 和 `extrinsicDesign.txt` 的 FR-Perturb 调用（`Perturb-FISH-repo/THP1analysis/Call_neighborEffect_analysis.txt:1-1`）。

### 8. Astrocyte：把扰动、表达和 live calcium phenotype 接起来

Astrocyte 数据展示 Perturb-FISH 的“功能表型”扩展。论文对 hIPSC-derived astrocytes 做 ASD risk gene CRISPRi screen，用 ATP 刺激后记录钙活动，再固定并做 Perturb-FISH（`paper source:65-69`, `paper source:265-271`）。每个细胞的 calcium trace 被转成多个特征：peak 数量、prominence、first step、first response time、average peak delay、AUC、是否有 transient，然后 Z-score normalization 和 k-means clustering，得到 6 类 calcium activity phenotypes（`paper source:269-271`）。

代码证据支持这个大框架，但也揭示一个细节：`calciumZscoreParametrization.m` 读取预先计算好的 `calciumsummary`，按 sample 做 Z-score，然后先运行 `kmeans(zscored,8,...)`（`Perturb-FISH-repo/astrocyteanalysis/calciumZscoreParametrization.m:1-24`）。后续 `matchingeffectswithguideenrichment.m` 把 cluster 7、6、8 分别合并/重映射到 5、2、6，最后使用论文中的 6 个标签：`large peak`, `inactive`, `large early transient`, `small peak`, `step`, `delayed`（`Perturb-FISH-repo/astrocyteanalysis/matchingeffectswithguideenrichment.m:4-26`）。因此中文理解上应该说：**论文展示的是 6 类功能表型；代码层面可见的流程是先做 8 类聚类，再压缩成 6 类表型标签。**

之后，代码按 cluster 统计每个 guide 的出现次数，计算相对期望频率的 log enrichment，并用 hypergeometric test 得到 p-value（`Perturb-FISH-repo/astrocyteanalysis/matchingeffectswithguideenrichment.m:33-47`）。表达层面，`matchingeffectswithexpression.m` 对 MERFISH 表达做样本内 Z-score，计算每个 calcium phenotype 的 gene signature，并对 cluster-associated expression 做 ANOVA（`Perturb-FISH-repo/astrocyteanalysis/matchingeffectswithexpression.m:23-64`, `Perturb-FISH-repo/astrocyteanalysis/matchingeffectswithexpression.m:103-110`）。

这一部分的核心思想是：

```text
每个 astrocyte:
    guide identity
    MERFISH expression
    calcium trace features
        |
        v
问题 1: 某个 KD 是否让细胞更容易进入某种 calcium phenotype？
问题 2: 某种 calcium phenotype 有哪些表达 signature？
问题 3: 某个 KD 改变的表达基因是否和 phenotype signature 对得上？
```

本地 Figure 5 图像支持这个结构：上方是六类 calcium traces，中间是 perturbation effect heatmap 和 guide enrichment，底部是 Z-scored expression signature。Figure S3/S4 进一步支持 calcium phenotype 和 astrocyte effect 的一致性。

### 9. Tumor xenograft：在组织里做 tumor-immune spatial perturbation

第三个应用是在 PBMC-humanized NSG 小鼠中的 A375 melanoma xenograft。论文把 35 个 NF-kB pathway target genes 的扰动导入 A375 tumor cells，肿瘤生长后做 Perturb-FISH，读取 500-gene immune-oncology panel（`paper source:87-91`）。分析分两层：

1. tumor cell 内部：某个 KO 如何改变 tumor cell 自己的表达；
2. intercellular：tumor cell 的扰动如何影响邻近 T cell 的表达（`paper source:91-97`）。

论文说 cell typing 用 scanpy，对 log-transformed raw counts 做 Leiden clustering，再按 transcriptome 标注 tumor cells 和 infiltrated T cells，并丢弃低 count 和 doublet clusters（`paper source:253-255`）。

代码层面，`preparetablesforPython.m` 先过滤 tumor count table，去掉 noisy barcode IDs，把两条 guide 合并到同一 target，写出 perturbation 和 expression matrices（`Perturb-FISH-repo/tumorpreprocessing/preparetablesforPython.m:30-58`）。它随后加载 `pythonAllclusters.csv`，注释写明 cell identity 来自 scanpy / notebook（`Perturb-FISH-repo/tumorpreprocessing/preparetablesforPython.m:81-82`）。这说明 tumor cell typing 的代码证据是 **Notebook / external output**，不能当成完全 line-verified exact match。

邻域分析方面，代码先找 immune neighbor tumor cells，再生成有/无 immune neighbor 的 tumor 表达和 perturbation 矩阵（`Perturb-FISH-repo/tumorpreprocessing/preparetablesforPython.m:93-120`）。然后以 T cell 为中心，把邻近 tumor cells 的 perturbation 汇总成 `cancerneighbortoTcell`，作为 T-cell expression analysis 的 design matrix（`Perturb-FISH-repo/tumorpreprocessing/preparetablesforPython.m:122-180`）。`repeatmorecells.txt` 记录了 tumor 全体、immune-neighbor split 和 T-cell-centered FR-Perturb 调用（`Perturb-FISH-repo/tumoranalysis/repeatmorecells.txt:13-77`, `Perturb-FISH-repo/tumoranalysis/repeatmorecells.txt:106-152`）。

本地 Figure 6 图像显示了 intrinsic tumor effect heatmap、cell-type spatial map、CRISPR perturbation spatial map 和 T-cell effect heatmap；Figure S5 支持 tumor split consistency 和 neighborhood-condition comparisons。

### 10. 这篇方法的真正贡献是什么？

Perturb-FISH 的贡献不应理解为“发明了一个新的统计模型”。统计效应估计主要借助已有 FR-Perturb。真正贡献是一个可扩展的 **measurement-and-analysis platform**：

```text
guide barcode 原位读取
    +
MERFISH transcriptome
    +
cell segmentation / spatial neighbor matrix
    +
optional live functional imaging
    |
    v
single-cell perturbation x expression x space x function table
```

这样得到的表格可以回答三类问题：

1. **细胞内效应**：某个 KO/KD 对同一细胞的表达有什么影响？
2. **细胞间/空间效应**：某个被扰动细胞是否影响邻居细胞？某个 perturbation effect 是否依赖局部密度？
3. **功能效应**：某个扰动是否把细胞推向某种 calcium activity phenotype？这种 phenotype 对应哪些表达 signature？

### 11. 代码复现边界

- 强证据：THP1 图像预处理、guide decoding、segmentation/count table、FR-Perturb no-normalization runner、density split、neighbor-effect call 都有直接源码行证据。
- 强证据：astrocyte 的 calcium registration/trace extraction、cluster enrichment、expression signature 也有源码行证据。
- 强证据：tumor 的 table filtering、guide pooling、immune-neighbor split、T-cell neighbor design 和 FR-Perturb calls 有源码行证据。
- Partial / Not found：原始图像、codebook、H5AD/CSV/MAT 中间文件不在 repo snapshot 中；很多脚本使用 Broad 或 Windows 绝对路径；没有 supplementary markdown；astrocyte FR-Perturb 的 paper 参数调用没有在 astrocyte 目录中找到；tumor cell typing 依赖本地获取但未逐行引用的 `clusterCells.ipynb` / 外部 scanpy output，该 notebook 超过 10 MB，因此 publish 时会忽略/排除。

所以，如果研究者想学习方法，当前代码非常有助于理解算法和表格构造；如果想直接一键复现实验结果，则还需要外部数据、路径整理和 notebook/数据资产补齐。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Perturb-FISH Summary

### Paper

**Simultaneous CRISPR screening and spatial transcriptomics reveal intracellular, intercellular, and functional transcriptional circuits**. Binan et al., *Cell* 188:2141-2158.e18, 2025. DOI: `10.1016/j.cell.2025.02.012` (`paper source:1-5`).

### Problem

Perturb-seq and related droplet scRNA-seq CRISPR screens connect perturbations to transcriptomes, but they dissociate cells and lose local spatial context. Optical pooled screens preserve imaging context, but earlier versions were not linked to highly multiplexed single-cell transcriptomic readouts (`paper source:25-27`). Perturb-FISH is designed to combine perturbation identity, targeted transcriptomics, spatial position, and optional live functional phenotypes in the same cells (`paper source:13-17`, `paper source:31-31`).

### Key Idea

Perturb-FISH modifies the guide vector so that a T7 promoter enables local in situ amplification of the guide region after fixation while preserving guide function during live-cell perturbation (`paper source:37-39`). The amplified guide sequence and selected mRNAs are then read with MERFISH-style encoding/readout probes. Computational reconstruction registers images, decodes guide/mRNA barcodes, segments cells, and produces per-cell perturbation and transcript count tables (`paper source:39-39`, `paper source:227-245`).

The main computational analysis then estimates perturbation effects with FR-Perturb and extends the design matrix to spatial or functional settings: low/high local density, perturbations in neighboring cells, calcium phenotype clusters, and tumor/T-cell neighborhoods (`paper source:247-287`, `paper source:289-294`).

### What Was Demonstrated

1. **THP1 LPS response validation**: Perturb-FISH recovers perturbation effects that are consistent across replicates and correlated with matched Perturb-seq, then supports downsampling/power analysis (`paper source:43-49`; Figure 3 local image).
2. **Spatial effects in THP1**: local density changes expression and perturbation effects; neighbor perturbations affect control-cell expression (`paper source:53-61`; Figure 4 and Figure S2 local images).
3. **Astrocyte functional screen**: CRISPRi perturbations of ASD-risk genes are linked to calcium trace phenotypes and expression signatures in iPSC-derived astrocytes (`paper source:65-83`; Figure 5 and Figure S3-S4 local images).
4. **Tumor xenograft screen**: Perturb-FISH is applied to an A375 melanoma xenograft model to study intrinsic tumor-cell effects and tumor-to-T-cell intercellular effects (`paper source:87-97`; Figure 6 and Figure S5 local images).

### Code Match and Reproducibility

The released code snapshot at `Perturb-FISH-repo/` matches the analysis workflow at **medium fidelity**.

Verified code behavior:

- THP1 preprocessing implements image filtering, guide barcode decoding, watershed segmentation, count-table generation, and neighbor detection (`Perturb-FISH-repo/thp1Preprocessing/filterthp1.m:38-92`, `Perturb-FISH-repo/thp1Preprocessing/decodeThisBinaryImagedontcheckrepeatsbutlookfurther.m:1-27`, `Perturb-FISH-repo/thp1Preprocessing/finishglobalcellmosaic.m:80-128`, `Perturb-FISH-repo/thp1Preprocessing/findtouchingcellsparallel.m:37-66`).
- THP1 Python scripts build AnnData/design inputs, run FR-Perturb with no-normalization settings, compare against Perturb-seq, perform random splits, and split low/high density cells (`Perturb-FISH-repo/THP1analysis/analyze_perturb-fish.py:49-83`, `Perturb-FISH-repo/THP1analysis/analyze_perturb-fish.py:153-178`, `Perturb-FISH-repo/THP1analysis/analyze_perturb-fish.py:226-290`, `Perturb-FISH-repo/THP1analysis/cleanrun_FR_PerturbnoNorm.py:262-363`).
- Astrocyte MATLAB scripts support MERFISH/calcium registration, per-cell calcium trace extraction, cluster enrichment, and expression-signature analysis (`Perturb-FISH-repo/astrocyte_preprocessing/getTranslationMtocalcium.m:1-27`, `Perturb-FISH-repo/astrocyte_preprocessing/asd2calciumNew.m:22-52`, `Perturb-FISH-repo/astrocyteanalysis/matchingeffectswithguideenrichment.m:4-47`, `Perturb-FISH-repo/astrocyteanalysis/matchingeffectswithexpression.m:23-64`).
- Tumor MATLAB/Python scripts support filtered tumor tables, guide pooling, immune-neighbor splits, T-cell neighbor design matrices, and FR-Perturb calls (`Perturb-FISH-repo/tumorpreprocessing/preparetablesforPython.m:30-58`, `Perturb-FISH-repo/tumorpreprocessing/preparetablesforPython.m:93-180`, `Perturb-FISH-repo/tumoranalysis/repeatmorecells.txt:13-77`, `Perturb-FISH-repo/tumoranalysis/repeatmorecells.txt:106-152`).

Open reproducibility gaps:

- no supplementary markdown was acquired;
- raw images, codebooks, H5AD/CSV/MAT intermediates are not included in the GitHub snapshot;
- many scripts use absolute Broad or Windows paths;
- astrocyte FR-Perturb command parameters are paper-specified but not directly found in an astrocyte command file;
- tumor cell-type labeling depends on external scanpy output / a local-only `tumoranalysis/clusterCells.ipynb` notebook that was not line-cited and is omitted/ignored for publish because it is over 10 MB.

### Bottom Line

Perturb-FISH is best understood as a spatial/functional perturbation-screening platform. Its novelty is the combination of T7-amplified in situ guide decoding with MERFISH transcript readout, producing cell-level perturbation/transcript/spatial/functional tables. The paper's strongest support is the THP1 validation plus spatial analyses, and the code most strongly supports the preprocessing and FR-Perturb analysis layers. Re-running the full paper workflow from this workspace alone is partial because key data/codebook/notebook surfaces are external or not line-verifiable.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
