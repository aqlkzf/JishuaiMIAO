---
layout: default
permalink: /paper-atlas/smcseq-3a35155b/
title: "SmCseq"
nav: false
wide: true
description: "SmC-seq 用正交微流控条形码把组织坐标写入 DNA，再以温和的酶学胞嘧啶转换读取每个像素的全基因组甲基化，从而揭示胚胎、滋养外胚层和母体蜕膜的空间表观遗传分工；它的实验创新清晰，但复现与解释必须正视 5mC/5hmC 合并信号、相邻切片、像素混合，以及公开代码与论文 Methods 在空间聚类和 DMR 统计上的实质差异。"
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
      <span>Nature Methods · 2026</span>
    </div>
    <h1>SmCseq</h1>
    <p>Spatial 5mC-seq profiling of embryos and decidua after implantation in mammals</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03079-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SmCseq">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/LiuLab888/spatial-5mC-project" target="_blank" rel="noopener noreferrer" aria-label="Open code for SmCseq">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 在组织切片上读取 DNA 甲基化地图：SmC-seq 方法、代码与证据解读

论文：*Spatial 5mC-seq profiling of embryos and decidua after implantation in mammals*（Nature Methods, 2026；DOI: `10.1038/s41592-026-03079-w`）

### 1. 为什么需要“空间 DNA 甲基化”

DNA 甲基化常用来调节基因表达和细胞命运。单细胞甲基化测序可以区分细胞状态，却必须把组织消化成单细胞，因而丢失“这个细胞原来在哪里”。空间转录组能保留位置，但读到的是 RNA，不是 DNA 调控层。

SmC-seq 想把两件事同时保留下来：

$$
\text{每个组织像素}\longrightarrow
(x,y,\text{全基因组 CpG 甲基化读数}).
$$

作者把方法用于着床后 E5.5、E6.5、E7.5 和 E8.5 小鼠胚胎及母体蜕膜，观察胚胎来源、滋养外胚层来源和母体细胞的甲基化空间变化。

“近单细胞分辨率”应谨慎理解：10×10 μm 像素接近许多细胞的尺度，但像素不等同于经过分割验证的单个细胞；20×20 μm 像素更可能混合多个细胞或组织成分。

### 2. 从切片到二维条形码

实验从 7 μm 冷冻切片开始。甲醛固定保持组织形态，随后进行三轮 HCl 处理以去除组蛋白，使被核小体包裹的 DNA 更容易被 Tn5 接近。Tn5 负责切割基因组并加上带连接位点的接头。

空间坐标来自两次互相垂直的微流控连接：

1. 第一块芯片沿一个方向输送 96 种 11 nt barcode A；
2. 移除后把第二块芯片旋转 90°，输送 barcode B；
3. A 通道和 B 通道交点的组合 $(A_i,B_j)$ 定义像素 $(i,j)$。

因此位置不是从测序后图像推测，而是被写入 DNA 片段。通道宽度为 10 μm 或 20 μm，部分 10 μm 芯片之间还有 5 μm 间隔。论文用相邻荧光条形码检查串流和扩散，说明通道之间没有明显污染。

### 3. 为什么普通亚硫酸氢盐路线不理想

传统 bisulfite 测序能把未甲基化 C 转成 U，但处理强烈、容易降解有限的空间像素 DNA。SmC-seq 使用 enzymatic methyl-seq：

- TET2 氧化 5mC；
- β-glucosyltransferase 保护 5hmC；
- APOBEC 把未保护的普通 C 脱氨为 U；
- PCR 后，未甲基化 C 读作 T，受保护的 5mC/5hmC 读作 C。

条形码设计排除 C，以降低转换破坏。扩增前的 gap filling 还用 5-hydroxy-dCTP 代替普通 dCTP，保护延伸产生的接头/条形码插入序列中的胞嘧啶。

最终甲基化水平定义为：

$$
ML=\frac{N_C}{N_C+N_T},
$$

其中 $N_C$ 是该位点被读为 C 的次数，$N_T$ 是被读为 T 的次数。

关键边界是：这套化学不能把 5mC 与 5hmC 分开，论文所谓 5mC 实际是二者的合并信号。在本文胚胎/蜕膜问题中可把它作为以 5mC 为主的指标，但不能在 5hmC 丰富的组织中直接当作纯 5mC。

### 4. 原始 reads 怎样变成每个像素的甲基化矩阵

本地 `spatial-5mC-project/` 对应论文公开代码。主流程为：

1. 从 Read 2 提取 A、B 条形码，只保留白名单组合；
2. 根据两轮条形码之间的特征碱基区分 Watson/Crick 链；
3. Trim Galore 去接头和低质量序列；
4. Bismark 以 `--pbat` 模式比对到 GRCm39；
5. 未比对 reads 从 5′ 端截去 5 bp 后重试，共五轮；
6. 合并各轮 BAM，并按 A×B 组合拆成像素；
7. 去重并运行 Bismark methylation extractor；
8. 输出像素×基因组区间的 coverage、depth 和 methylation matrix。

`--pbat` 不是普通参数细节。文库的链方向符合 PBAT 架构，不使用该选项会改变可比对链和甲基化解释。

反复截短提高召回率，但也带来一个应保留的边界：后续轮次使用更短 reads，唯一比对性可能下降；代码通过合并最佳结果来平衡，而不是所有 reads 都以同一长度进入分析。

### 5. 图 1：SmC-seq 的技术性能是否可信

图 1 展示工作流和 E5.5/E7.5 基准：

- glycosylation protection 为 98.6%；
- deamination efficiency 为 98.0%；
- 单像素基因组覆盖最高 3.46%；
- 平均每像素约检测 230,561 个 CpG，约占全基因组 CpG 的 1.05%；
- 汇总约 200 个像素可覆盖约 80% 小鼠基因组；
- 与 scNMT-seq、sci-Cabernet、snmC-seq2、sciMETv2 比较时，按测序深度标准化后的覆盖率具有竞争力。

两个 E7.5 生物学重复显示相似空间模式，约 80% 的 1 kb bins 与公开单细胞或 bulk 数据落在一致范围。相关性在更大的 10 kb、100 kb、1 Mb bins 中更高是预期现象，因为聚合会降低稀疏噪声；这不能反过来证明单 CpG 或单像素都具有同等精度。

### 6. 如何把空间位置和甲基化一起聚类

这是论文与代码差异最大的部分。

论文 Methods 描述：先构造所有像素间的 $N\times N$ 欧氏距离矩阵，再用 Seurat `FindIntegrationAnchors` 选择关键空间锚点，使降维空间矩阵与 ML 矩阵等权，之后 PCA、$k$-means 和 UMAP。

公开代码 `Spatial_methyl_clustering/spatial_methylation_cluster.R` 实际没有在甲基化聚类中实现这个流程。它对每个样本人工指定 4–10 个坐标锚点，并计算像素到每个锚点的距离：

$$
d_{ia}=\sqrt{(x_i-x_a)^2+(y_i-y_a)^2}.
$$

各距离特征做 z-score，甲基化特征则用：

$$
z^{(ML)}_i=\frac{ML_i-\overline{ML}}{s_{ML}/2}
$$

或在部分蜕膜段落除以 $s_{ML}/4$。这等价于把甲基化变化放大约 2–4 倍，而不是和一个普通标准化空间特征严格等权。

最后拼接

$$
F_i=[z(d_{i1}),\ldots,z(d_{iK}),z^{(ML)}_i]
$$

并运行 `kmeans(..., nstart=25)`；脚本设定随机种子 100，再用 UMAP 可视化。

这不是小实现差异：论文描述的是全像素距离+锚点集成，代码是人工坐标基函数+加权 ML。代码更便宜，从 $O(N^2)$ 降为约 $O(NK)$，但高度依赖组织形状、锚点和阈值的人工调参。

另一个容易混淆的事实是：`FindIntegrationAnchors` 确实出现在 `spatial_RNA_analysis/Seurat_Integration_and_GO_Enrichment.R`，用于多个空间 RNA 数据集的 SCT 集成；它不能证明甲基化聚类脚本也使用了该函数。

### 7. 图 2：相邻切片怎样把甲基化与 RNA 对齐

作者在相邻组织切片上分别做 SmC-seq 与空间 RNA-seq，以组织轮廓配准两种模态。代码 `Data_alignment/alignment_by_outline.py`：

1. 把两个 dot plot 转灰度并降采样到 192×192；
2. 阈值化并做形态学 closing，提取组织边界；
3. 固定 RNA 图、移动 methylation 图；
4. 用 SimpleITK elastix 优化 affine transform；
5. 以 Dice coefficient >0.85 作为质量标准；
6. 去除变换后距离最近 RNA 像素超过 10 μm 的甲基化点。

Dice 可写为：

$$
Dice=\frac{2|A\cap B|}{|A|+|B|}.
$$

高轮廓重叠保证组织大尺度对齐，不保证每个甲基化像素和 RNA 像素来自同一个细胞。相邻切片在胚胎小结构、组织弯曲或局部缺损处仍可能不同，因此本文的甲基化—表达关联主要是空间区域或 cluster 层面的对应。

图 2 显示 ICM 来源、TE 来源和母体子宫组织有不同 ML 动态：胚胎 ICM 来源组织总体逐步获得甲基化，TE 来源组织保持较低或下降，蜕膜则呈显著空间异质性。

### 8. DMR：论文写的统计方法与代码不是同一个

论文 Methods 写的是：在 300 bp bins 中要求覆盖超过 5 个 CpG，用 Fisher's exact test，$P<0.01$，再以 BH FDR<0.1 选择 DMR。

公开 `DMR_analysis/03_DMR_analysis.R` 实际使用 DSS：

```r
DMLtest(..., smoothing=TRUE)
callDMR(delta=0, minlen=50, minCG=3,
        dis.merge=100, p.threshold=1e-5)
```

DSS 建模甲基化计数和生物学变异，并对相邻 CpG 平滑；Fisher test 则是列联表检验。二者不能视为同一实现。代码也没有在 DMR 调用处看到 BH FDR 0.1。

论文图 5h–j 的 GO 富集确实使用 Fisher's exact test，因此“Fisher”很可能混入了不同分析环节。复现仓库结果应按 DSS 脚本；复现论文 Methods 的名义流程则需要另写 Fisher+BH 实现。工作区必须保留这一不一致，而不能替作者选择一个版本后抹平。

### 9. 图 3：ICM 来源组织的甲基化轨迹

SmC-seq 将 ICM 来源像素分成 epiblast、extra-embryonic endoderm（ExEndo）和 extra-embryonic visceral layer（ExVL）等空间簇。E5.5 到 E7.5 期间 epiblast 发生明显 de novo methylation；DMR 与 GO 结果提示前后轴、体节发生和骨骼发育相关调控区域改变。

论文还把部分 SmC-seq DMR 与公开 scNMT-seq 比较，约 28–47% 得到重叠支持。这个比例说明两种实验捕获到一部分共同变化，也说明超过一半 DMR 未被该外部数据确认；差异可能来自空间混合、覆盖稀疏、阶段/样本差异或统计流程。

### 10. 图 4：蜕膜中低甲基化的营养供给谱系

母体蜕膜被分为多个空间甲基化簇。中部的 nutrient-supplier progenitor 簇 M1 具有最低 ML，其低甲基化区域与细胞增殖相关；更成熟的侧方 nutrient-supplier 区域中，低甲基化相关基因富集于胞吐、脂质/营养合成和物质转运。

Psap 等 marker 的空间 RNA 和甲基化图支持该解释。Mki67/5mC 染色用于排除“低 ML 只是所有快速增殖细胞的被动稀释”这一过度简单解释，但不能完全排除复制速率对甲基化的贡献。

### 11. 图 5：滋养外胚层的两层 EPC

E8.5 ectoplacental cone（EPC）形成内外两层：

- inner EPC：更偏增殖，ML 较低；
- outer EPC：更偏血管生成、免疫调节和 NK 细胞保护，ML 相对较高。

只用甲基化值时，EPC 较难充分拆分；加入空间特征后得到四个空间簇，说明“相同平均 ML、不同位置和功能”的细胞可被区分。RNA velocity 给出从内向外的状态方向，但它来自相邻切片的 RNA 数据，不是甲基化本身提供的时间箭头。

inner EPC 与 nutrient-supplier progenitor 的低 ML promoters 有 34,589 个 300 bp bins 重叠，提示胚胎和母体两侧的快速增殖/营养界面可能共享部分低甲基化程序；谱系特异 bins 又分别富集不同功能。

### 12. 代码—论文对应关系

| 论文环节 | 本地代码 | 对应程度 |
|---|---|---|
| 条形码提取、链拆分、PBAT 比对 | `Spatial_methyl_pipeline/` | Exact |
| 五轮 5 bp iterative mapping | 主 template 与 `bins/` | Exact |
| coverage/ML 矩阵 | `bismark_cell_calculate.py` 等 | Exact |
| 甲基化空间聚类 | `spatial_methylation_cluster.R` | Partial；实现与 Methods 不同 |
| $k$-means/UMAP | 同上 | Exact |
| RNA SCT integration | `spatial_RNA_analysis/...R` | Exact |
| 轮廓 affine 配准 | `alignment_by_outline.py` | Exact/Partial；人工调参 |
| DMR 调用 | `DMR_analysis/03_DMR_analysis.R` | Partial；DSS vs Fisher+BH |
| GO 富集 | `GO_analysis.R` | Exact |
| co-clustering | `Co_clustering_analysis.R` | Partial；含 0.5 插补 |
| 自动锚点选择的甲基化聚类 | 未在甲基化脚本找到 | Not found |

总体代码忠实度为 **中等**：原始 SmC-seq 数据处理、空间聚类、DMR、GO、RNA 和配准均有脚本，但核心聚类和 DMR 统计与论文文字存在实质差异。

### 13. 复现时的实际障碍

1. 大量脚本硬编码 `/media/tangym/ETD/...` 路径。
2. coverage 阈值在不同样本间为 1000–5000，ML 下限为 0.2–0.32。
3. 锚点坐标、$k$ 值和部分 ML 权重逐样本手工设定。
4. 边界像素列表 `cell_filtered_EM.txt` 等中间文件未完整提供。
5. 没有容器或锁定环境；Bismark、R、SimpleITK/elastix 等需自行组合。
6. 自定义 PDMS 芯片、HCl 处理和复杂酶学步骤构成实验复现门槛。
7. 原始数据在 GSA `CRA023723` 和 `CRA028148`，完整重跑需要大量存储与计算。

### 14. 解读结果时必须保留的边界

1. SmC-seq 读取合并 5mC/5hmC 信号，不能严格称为纯 5mC。
2. 像素不是经分割确认的单细胞，尤其 20 μm 像素可能混合。
3. 每像素覆盖稀疏，大 bin/pseudobulk 的高相关不代表单点同样可靠。
4. 相邻切片配准不能建立单细胞一一对应。
5. 空间聚类结果依赖人为锚点、过滤阈值、特征权重和 $k$。
6. 论文与代码的聚类、DMR 方法不一致会影响再分析结果。
7. 只有两个生物学重复，且未做预先样本量计算。
8. 研究对象是小鼠着床后发育，不能直接外推为人类胚胎/胎盘机制。

### 15. 一句话总结

SmC-seq 用正交微流控条形码把组织坐标写入 DNA，再以温和的酶学胞嘧啶转换读取每个像素的全基因组甲基化，从而揭示胚胎、滋养外胚层和母体蜕膜的空间表观遗传分工；它的实验创新清晰，但复现与解释必须正视 5mC/5hmC 合并信号、相邻切片、像素混合，以及公开代码与论文 Methods 在空间聚类和 DMR 统计上的实质差异。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SmC-seq Summary

### Motivation & Novelty

**Biological problem**: DNA methylation is a critical epigenetic regulator of embryonic development, yet its spatial organization within tissues was completely unknown. Existing single-cell DNA methylation methods (scNMT-seq, *Nature* 2019; snmC-seq2, *Nat Commun* 2018; sciMETv2, *Nat Commun* 2022; sci-Cabernet, *PNAS* 2023) require cell dissociation, destroying spatial context. Spatial epigenomics technologies existed for chromatin accessibility (Spatial-ATAC, *Nature* 2022; Spatial-CUT&Tag, *Science* 2022) and transcriptomics (DBiT-seq, *Cell* 2020), but no spatial DNA methylation method had been reported.

**Unique contributions**:
1. **First spatial DNA methylation technology** — SmC-seq is the first method to profile genome-wide DNA methylation while preserving spatial coordinates
2. **Near single-cell resolution** — 10×10μm or 20×20μm pixels, comparable to single-cell methods
3. **Enzymatic conversion** — uses EM-seq chemistry (TET2 + β-GT + APOBEC) rather than bisulfite, avoiding DNA degradation
4. **Novel spatial clustering algorithm** — integrates spatial position with methylation level for improved cluster resolution
5. **Biological discoveries** — two-layer EPC organization, nutrient-supplier progenitor hypomethylation, ICM/TE divergent methylation dynamics

---

### Method Overview

SmC-seq is a microfluidic-based spatial DNA methylation profiling technology. The core workflow:

1. **Tissue preparation**: Frozen sections (7μm) are fixed and treated with HCl to remove histones, exposing genomic DNA for efficient Tn5 tagmentation
2. **Spatial barcoding**: Two rounds of microfluidic ligation introduce orthogonal 11-mer barcodes (A and B) through perpendicular channels, encoding 2D spatial position. The unique A×B combination identifies each pixel's location
3. **Enzymatic methylation conversion (EM-seq)**: TET2 oxidizes 5mC→5caC; β-GT glucosylates 5hmC; APOBEC deaminates unmodified C→U. After PCR, methylated C reads as C, unmethylated C reads as T
4. **Sequencing and demultiplexing**: Paired-end 150bp sequencing; barcodes extracted from Read 2; Bismark PBAT alignment with iterative 5bp trimming
5. **Spatial clustering**: Novel algorithm combining Euclidean distances to anchor points with scaled methylation level; k-means clustering
6. **Multi-modal integration**: Adjacent slides used for spatial RNA-seq; image registration (SimpleITK affine, Dice>0.85) aligns methylation and RNA data
7. **Downstream analysis**: DMR identification (DSS), GO enrichment (clusterProfiler), RNA velocity (scVelo)

**Key limitation**: Cannot distinguish 5mC from 5hmC (combined signal). Adjacent-slide assumption introduces uncertainty in single-cell methylation-expression correlation.

---

### Evaluation

#### Datasets
- Mouse embryos at E5.5, E6.5, E7.5, E8.5 (C57BL/6N)
- Embryo-maternal tissue sections (conceptus + decidua)
- Two biological replicates per stage
- Chip resolutions: 10μm (embryo-focused) and 20μm (whole tissue)

#### Benchmarking Metrics
- **Enzymatic conversion**: 98.6% glycosylation protection, 98.0% deamination efficiency
- **Genome coverage**: up to 3.46% per pixel; ~200 pixels needed for 80% genome coverage
- **Standardized coverage**: comparable to scNMT-seq, snmC-seq2, sciMETv2, sci-Cabernet
- **Replicate correlation**: high correlation between biological replicates (Extended Data Fig. 3a,b)
- **Benchmark against published data**: ~80% of 1kb bins show consistent methylation with published bulk and single-cell datasets (Extended Data Fig. 3d)
- **Scatter correlation**: Pearson R > 0.9 at 1Mb, 100kb, 10kb bins vs scNMT-seq and bulk WGBS

#### Biological Validation
- **Immunofluorescence**: 5mC staining confirms spatial ML patterns in decidua and EPC
- **Mki67 co-staining**: Confirms that low-ML cells in decidua are not simply proliferating cells (5mC and Mki67 signals are comparable between Mki67+ and Mki67- cells)
- **Psap staining**: Confirms spatial location of mature nutrient-supplier cells in lateral decidua
- **DMR overlap with scNMT-seq**: 28–47% of SmC-seq DMRs confirmed by published scNMT-seq data

#### Key Biological Findings
- **ICM-derived cells**: ML increases from E5.5 (de novo methylation) to E8.5; three clusters (epiblast, ExEndo, ExVL) with distinct methylation patterns
- **TE-derived cells**: ML decreases from E6.5 to E8.5; two-layer EPC organization (inner EPC: proliferative, low ML; outer EPC: angiogenic/immune, higher ML)
- **Maternal decidua**: Nine methylation clusters; nutrient-supplier progenitor cluster (M1) has lowest ML; hypomethylated regions enriched for proliferation and nutrient metabolism genes
- **Spatial context value**: Spatial information enables 4-cluster resolution in EPC vs only 2 clusters without spatial data (Supp Fig. 2b)

---

### Reproducibility

**Rating: 3/5**

**Justification**: The code is publicly available and covers all major analysis steps. However, several factors limit reproducibility:

**Strengths**:
- Complete code repository with all analysis scripts
- Raw data deposited in Genome Sequence Archive (CRA023723, CRA028148)
- Detailed Methods section with reagent catalog numbers
- Two biological replicates per stage

**Weaknesses**:
- **Sample-specific hardcoded parameters**: Coverage thresholds (1000–5000), ML filters (0.2–0.32), anchor point coordinates, and k values are hardcoded per sample in the clustering script. New users must determine these empirically
- **Absolute paths**: All scripts use absolute paths to a specific machine (`/media/tangym/ETD/...`), requiring path substitution throughout
- **No containerization**: No Docker/Singularity environment provided; dependency versions must be matched manually
- **Microfluidic chip**: Custom PDMS chips from Suzhou Cchip Scientific Instrument — not commercially available as a kit; requires specialized fabrication
- **Adjacent slide assumption**: Methylation-RNA integration relies on adjacent slides having similar cell composition, which cannot be guaranteed
- **Missing intermediate files**: Border pixel exclusion lists (`cell_filtered_EM.txt`) are referenced but not provided in the repository

**Practical notes**:
- Bismark v0.23.0 with PBAT mode is critical; newer versions may have different defaults
- DSS package for DMR analysis requires R 4.x; the paper's "Fisher's exact test" description is misleading — use DSS
- SimpleITK elastix registration requires manual threshold tuning per sample
- The 5-hydroxy-dCTP gap filling step is critical for barcode integrity; standard dCTP will destroy barcodes during APOBEC treatment

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
