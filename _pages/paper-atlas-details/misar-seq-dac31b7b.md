---
layout: default
permalink: /paper-atlas/misar-seq-dac31b7b/
title: "MISAR-seq"
nav: false
description: "MISAR-seq 把组织切片划成 50×50 µm 的二维网格，在每个网格中同时测量 ATAC 可及性和 RNA 表达。它的价值不只是把两张独立空间图叠在一起，而是让同一个位置的调控元件开放程度与转录输出可以直接配对，从而观察小鼠胚胎脑发育过程中“染色质先准备、基因后表达”的时空调控关系。 整套方法包含两部分：实验端用 Tn5、逆转录和两轮正交微流控条形码在同一切片上生成配对 ATAC/RNA 文库；"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature Methods · 2023</span>
    </div>
    <h1>MISAR-seq</h1>
    <p>Simultaneous profiling of spatial gene expression and chromatin accessibility during mouse brain development</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-023-01884-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for MISAR-seq">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/gpenglab/MISAR-seq" target="_blank" rel="noopener noreferrer" aria-label="Open code for MISAR-seq">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MISAR-seq：在同一空间网格中同时读取染色质开放性与基因表达

### 一句话理解

MISAR-seq 把组织切片划成 50×50 µm 的二维网格，在每个网格中同时测量 ATAC 可及性和 RNA 表达。它的价值不只是把两张独立空间图叠在一起，而是让同一个位置的调控元件开放程度与转录输出可以直接配对，从而观察小鼠胚胎脑发育过程中“染色质先准备、基因后表达”的时空调控关系。

整套方法包含两部分：实验端用 Tn5、逆转录和两轮正交微流控条形码在同一切片上生成配对 ATAC/RNA 文库；计算端分别处理两种稀疏程度不同的模态，再用空间邻域约束聚类，并沿皮层发育轨迹连接开放峰与潜在靶基因。

### 1. 这项技术要解决什么问题

单细胞 RNA 测序能告诉我们基因已经表达，单细胞 ATAC 测序能告诉我们哪些调控区域可能可用，但组织解离会丢失位置。传统空间转录组保留位置，却没有同步的开放染色质层。若 ATAC 和 RNA 来自不同切片或不同细胞，峰—基因关系只能通过跨样本整合推断，技术差异和组织错位会混入相关性。

MISAR-seq 让两种模态共享同一个空间 barcode。对一个网格而言：

- ATAC 记录该区域内哪些基因组片段可被 Tn5 插入；
- RNA 记录该区域内哪些转录本被捕获；
- 网格坐标把两者放回 H&E 解剖图中。

这里的分辨率不是单细胞。每个 50×50 µm 网格约含 5—20 个细胞，所以“某峰与某基因在同一网格相关”仍可能来自不同细胞类型的共定位，而不是同一个细胞内的直接调控。

### 2. 实验流程：怎样让 ATAC 和 RNA 共用空间地址

#### 2.1 在切片上分别标记两种分子

组织先用 1% 甲醛固定。装载 read1/read2 接头的 Tn5 在原位插入开放染色质。随后对 mRNA 逆转录，poly(T) 引物同时携带 10 bp UMI、read2 anchor 和生物素标签。这样 ATAC 片段与 cDNA 具有不同化学把手，但仍留在同一组织位置。

#### 2.2 两轮正交微流控条形码

第一块微流控芯片用 50 条平行通道输送 BC1；第二块旋转 90°，再用 50 条通道输送 BC2。两组通道交叉产生 $50\times50=2,500$ 个地址。每个交叉点的空间地址由 BC2+BC1 确定。

两轮条形码需要严格控制泄漏和扩散。作者修改了 DBiT-seq 的通道和密封结构，并用 Cy3/FAM 染料观察二维棋盘图案，确认条形码边界。相邻切片做 H&E，用于把条形码网格映射到解剖区域。

#### 2.3 分离两类文库

组织消化后，带生物素的 RNA cDNA 被链霉亲和素磁珠捕获；上清中的 ATAC 片段进入 ATAC 文库。两种文库分开扩增和测序，但保留相同空间 barcode，因此计算端可以按网格重新配对。

### 3. 原始 reads 如何恢复成空间网格

公开 Python 脚本显示了条形码的精确位置。

#### RNA

`MISAR_Split_BC_RNA.py` 从一条 read 中提取：

- UMI：位置 0—10；
- BC2：10—18；
- BC1：50—58。

新 barcode read 按 `BC2 + BC1 + UMI` 排列，共 26 bp。顺序不能交换，否则 barcode whitelist 与空间坐标会错位。

#### ATAC

`MISAR_Split_BC_ATAC.py` 保留前 75 bp 基因组序列，再提取 BC2（75—83）和 BC1（115—123），生成 16 bp 的 `BC2 + BC1` barcode read。

重排后的 FASTQ 进入 Cell Ranger ARC 2.0.1，使用定制的 737K barcode whitelist 对齐到 mm10，输出 ATAC fragments、RNA feature-barcode matrix 和网格级质控指标。仓库中的 shell 脚本还生成 CPM 归一化 bigWig 与 TSS enrichment 图。

### 4. 组织区域过滤：网格存在不等于网格有组织

芯片有 2,500 个理论地址，其中一部分位于组织外。`Grid_filter.py` 对 H&E 图像做 Gaussian blur 和 Otsu 二值化，再按 50×50 网格判断哪些格子覆盖组织。得到的位置文件同时过滤 RNA 对象和 ATAC fragments。

部分样本还需要先在 Photoshop 中制作黑白 mask，所以这不是完全自动的组织分割。切片旋转、形变或相邻 H&E 与测序切片不完全一致，都可能造成边界网格误配。

### 5. 为什么 ATAC 和 RNA 要分别降维

RNA 是计数数据，一个网格常有许多基因非零；ATAC peak 或 5 kb tile 更稀疏，接近二值数据。若直接把原始矩阵拼接，高丰度 RNA 或极稀疏 ATAC 会主导距离。因此代码先为两种模态分别构造低维表示。

#### 5.1 ATAC 的 iterative LSI

ATAC 使用 5 kb TileMatrix，选择 25,000 个变异特征，在 1—30 维中迭代两次。LSI 可概括为：

1. 用 TF–IDF 降低普遍开放 tile 和测序深度的影响；
2. 对加权矩阵做 SVD；
3. 在低维空间聚类；
4. 根据聚类重新选择有区分力的特征并重复。

#### 5.2 RNA 的实际实现

主脚本先对 RNA 做 SCTransform，并回归线粒体比例；随后也调用三轮 iterative LSI、选 3,000 个特征和 1—20 维。但代码在后面把 `LSI_RNA` 的 SVD embedding 替换成 Seurat PCA 的前 30 个主成分：

```r
matSVD <- dat@reductions$pca@cell.embeddings[,1:30]
proj@reducedDims$LSI_RNA$matSVD <- matSVD
```

因此最终联合分析中的 RNA 表示实际是 SCTransform+PCA，不是论文文字容易让人理解的纯 RNA LSI。这一实现差异会影响距离、聚类和跨模态权重。

### 6. 空间 refinement：代码中的真正空间约束

普通聚类只看分子相似度，可能在连续脑区中产生孤立网格。代码通过 R 的 `refine()` 调用 Python `utils.py`，用网格坐标计算欧氏距离：

$$
d_{ij}=\sqrt{(x_i-x_j)^2+(y_i-y_j)^2}.
$$

对方形网格，每个位置取四个最近邻，加上自身共五个标签。若自身标签在这五个标签中出现不超过 2 次，且某个邻居标签出现至少 3 次，就把该网格改为多数标签。默认 V2 模式会连续运行两次。

这个过程本质上是局部多数投票平滑：

```text
中心标签 A，四邻居为 B、B、B、A → 改为 B
中心标签 A，四邻居为 B、B、A、C → 保留 A
```

它能消除空间孤点，但也可能抹去真实的小区域或锐利边界。它不是学习卷积核的图神经网络。

论文方法提到“graph convolution layer”和“deep embedding clustering”，但公开仓库中没有 GCN、图卷积参数或 DEC 损失函数。可直接核验的空间机制是上述 KNN 多数投票加 Seurat SNN 聚类。因此图卷积/深度聚类应标为 `Not found`，不能用这段 refinement 代码冒充完整实现。

### 7. 两种模态如何合并

代码调用 `addCombinedDims()`，把 ATAC 与 RNA 低维表示按列拼接：

$$
E_{\mathrm{combined}}=[E_{\mathrm{ATAC}}\;\Vert\;E_{\mathrm{RNA}}].
$$

论文说明多切片分析再用 Harmony 去除批次效应，然后在联合表示上构建 UMAP 与聚类。公开单样本脚本展示了拼接和 UMAP，但没有完整复现 8 张切片联合 Harmony 的入口。

主脚本分别对 RNA、ATAC 和 Combined 表示以 0.3、0.5、0.8 的分辨率运行 Seurat SNN 聚类，再调用空间 refinement。小于 20 个网格的离群小簇会通过 KNN 重新分配到大簇。

图 2 应从三层读：ATAC 聚类表示开放染色质域，RNA 聚类表示表达域，Combined 聚类综合两者。16 个联合空间簇与 H&E/脑图谱解剖区域相符，并显示从 E11.0 到 E18.5 组织复杂度增加。聚类一致并不表示 ATAC 与 RNA 一一对应；图 3 的 Sankey/重叠图反而显示一个较粗的 ATAC 状态可对应多个更细的 RNA 状态。

### 8. 质量与空间真实性如何验证

论文在 8 张矢状脑切片、4 个胚胎时期（E11.0、E13.5、E15.5、E18.5，各 2 张）上得到 7,118 个双模态网格。

主要验证包括：

- 每网格 16,472—34,730 个 ATAC unique fragments；
- FRiP 15.0%—45.6%，线粒体 fragments 2.52%—2.95%；
- TSS enrichment 与单模态空间 ATAC/10x scATAC 比较；
- 聚合 ATAC 与 ENCODE E15.5 brain bulk ATAC 共享主要峰；
- 相邻切片重复的空间模式一致；
- RNA 标志基因与 Allen Brain Atlas 原位杂交图相符；
- 论文使用 RCTD/scRNA-seq 参考检查细胞类型分布。

其中 RCTD 和作者所述自定义 RMSE 图像相似度脚本未包含在仓库，属于论文结果而非当前代码可重跑模块。

### 9. 从峰到基因：为什么需要发育轨迹

单个网格中 peak accessibility 与 RNA 同时测量，但发育调控常有时间滞后：增强子先开放，基因稍后表达。作者选择皮层相关空间簇，在联合 ATAC+RNA latent space 中用 ArchR 构造监督式 pseudotime，然后把网格沿 0—100 轨迹分箱。

`GetTrajectory()` 对每个 pseudotime bin 求均值，再以窗口做 rolling mean，减少空间网格的稀疏噪声。代码调用中使用的平滑窗口需要从实际参数追踪；函数默认值与已有文档中描述的窗口并非在所有位置一致，因此应以运行调用为准。

对基因 $g$，只考虑其 TSS 两侧 250 kb 内的 peak $p$，在平滑后的轨迹上计算 Pearson 相关：

$$
r_{pg}=\mathrm{corr}(A_p(t),R_g(t)).
$$

这里 $A_p(t)$ 是 peak 随 pseudotime 的开放曲线，$R_g(t)$ 是基因表达曲线。高正相关说明两者沿轨迹共同升降，是潜在 cis 连接，不是物理染色质接触证据。

### 10. DER 分数在表达什么

DER（domain of enhancer regulation）把与同一基因连接的多个远端 peak 聚合成基因级可及性活动：

$$
\mathrm{DER}_g(s)=\sum_{p\in L(g)}A_p(s),
$$

其中 $L(g)$ 是通过距离和相关性筛选后连接到基因 $g$ 的 peak 集合，$s$ 是网格。`getScores()` 正是对这些 peak 计数求列和。

它让“多个增强子共同调控一个基因”的开放性信号可以与 RNA 表达并排画轨迹。作者据此观察到 Neurod6、Thra、Mef2c 等基因的 DER/peak 开放先于表达上升，解释为 epigenetic priming。

但 DER 依赖前面的候选连接；错误 peak—gene 配对也会被聚合。公开代码还会去除 `*Rik`、`Gm*`、线粒体和核糖体基因，并对一个 peak 只保留最高相关基因，这些隐含筛选会改变网络规模。

### 11. 论文与 DER 代码存在的阈值差异

论文描述皮层轨迹峰—基因链接使用 FDR $<10^{-4}$、$P<0.05$、PCC $>0.6$，并称采用单尾 t 检验。`PeakToGene()` 中实际写的是：

```r
o$Pval <- 2 * pt(-abs(o$TStat), ncol(seATAC) - 2)
```

这是双尾检验。仓库后续可见筛选还使用 `pvalZ <= 0.05`，没有在同一代码路径明确执行 PCC > 0.6；函数签名中的相关阈值默认也不能还原论文最终筛选。可能存在未公开的最终脚本或版本差异，因此 76,072 条增强子—基因链接不能仅靠当前 `DER.R` 原样复现。

### 12. 转录因子网络和皮层级联

论文把 TF motif accessibility、peak—gene links 和 RNA 表达组合成有向网络，并区分：

- promoter 路径：TF motif 位于目标基因可及启动子；
- enhancer 路径：TF motif 位于与目标基因连接的远端 peak。

在皮层发生过程中，作者重点提出 Pax6→Eomes→Tbr1 的级联，并显示部分调控元件开放早于下游表达。图 4 展示空间 TF motif deviation 与表达，图 5 展示沿皮层轨迹的动态和网络。

仓库加载了 `networkD3` 并保留峰—基因/DER 函数，但没有完整的 TF-target 建网、启动子/增强子分类和最终网络生成脚本。因此生物学网络可由论文图与结果支持，代码映射是 `Partial/Not found`，不应声称端到端复现。

### 13. 代码—论文对应总表

#### Exact

- RNA/ATAC barcode 固定位置提取；
- Cell Ranger ARC 与定制 whitelist 的预处理框架；
- H&E 网格过滤；
- ATAC iterative LSI 与 RNA SCTransform/PCA；
- 四邻域空间多数投票；
- ATAC/RNA embedding 拼接；
- 250 kb 范围内 Pearson peak—gene 相关；
- DER 的 linked-peak 聚合。

#### Partial

- 8 切片 Harmony 联合分析未完整脚本化；
- peak—gene 阈值和尾部检验与论文不一致；
- MAGIC 可见于扩展代码，但后续 window smoothing 不完整；
- TF motif 到目标网络只发布了部分前置模块；
- 单样本示例不能直接生成全文所有跨时期图。

#### Not found

- 论文所述 graph convolution layer；
- deep embedding clustering 实现；
- RCTD deconvolution 脚本；
- 重复切片 RMSE 相似度脚本；
- 完整 GRN 构建与 promoter/enhancer 边分类流程。

所以公开代码能解释 MISAR-seq 的核心预处理、表示学习、空间平滑和 DER 思路，但不能端到端重建论文全部图和所有定量链接。

### 14. 阅读结论时最重要的边界

1. **网格不是单细胞。** 5—20 个细胞的混合会让跨细胞共定位看起来像同一细胞的调控。
2. **空间平滑会牺牲小区域。** 多数投票强化连续域，同时可能吞掉真实罕见结构。
3. **相关峰不是确认增强子。** 250 kb 距离和轨迹相关不能替代 3D 接触或扰动实验。
4. **pseudotime 不是实际时间追踪。** 四个胚胎时期的横截面网格被排列成连续轨迹。
5. **论文与代码有关键差异。** 图卷积、深度聚类、GRN、RCTD 及最终阈值不能由当前仓库完整核验。

在这些边界内，MISAR-seq 最可靠的贡献是证明同一空间网格中联合 ATAC+RNA 测量可行，并用配对信号描绘发育脑区。更复杂的调控级联是由该图谱提出的优先验证假说。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MISAR-seq: Simultaneous Profiling of Spatial Gene Expression and Chromatin Accessibility

### Motivation & Novelty

#### Biological Problem

Brain development requires coordinated gene regulation across multiple molecular layers — chromatin accessibility determines which genes *can* be expressed, while transcription determines which genes *are* expressed. Understanding the regulatory logic that drives spatial tissue organization requires measuring both layers simultaneously in their native spatial context. Previous approaches measured these modalities separately or without spatial information, making it impossible to directly link spatial chromatin states to spatial gene expression patterns in the same cells.

#### Limitations of Existing Approaches

- **Single-cell multi-omics** (SHARE-seq, Ma et al., *Cell*, 2020; Zhu et al., *Nat. Methods*, 2021): Joint ATAC+RNA profiling but without spatial information — dissociation destroys tissue architecture
- **Spatial transcriptomics** (DBiT-seq, Liu et al., *Cell*, 2020; Slide-seq, Rodriques et al., *Science*, 2019): Spatial RNA only — no epigenetic layer
- **Spatial epigenomics** (Spatial-ATAC-seq, Deng et al., *Nature*, 2022; Spatial-CUT&Tag, Deng et al., *Science*, 2022; Epigenomic MERFISH, Lu et al., *Cell*, 2022): Spatial chromatin/histone marks only — no gene expression

#### Unique Contributions

1. **First spatial co-profiling of ATAC + RNA**: MISAR-seq simultaneously measures chromatin accessibility and gene expression on the same tissue section at 50×50 μm resolution, enabling direct correlation of regulatory elements with their transcriptional output in spatial context
2. **Microfluidic design improvements**: Modified DBiT-seq channel flow and sealing slabs minimize leakage and diffusion, validated by Cy3/Fam dye imaging
3. **Spatially-aware computational integration**: Custom iterative LSI with spatial neighbor refinement improves domain detection compared to non-spatial clustering
4. **Regulatory cascade discovery**: Joint spatial ATAC+RNA data enables prediction of the Pax6→Eomes→Tbr1 feedforward cascade in corticogenesis, distinguishing promoter from enhancer regulation

### Method Overview

MISAR-seq (Microfluidic Indexing-based Spatial ATAC and RNA-seq) combines:

- **Experimental protocol**: Tissue fixation → Tn5 transposition (ATAC) → reverse transcription (RNA) → two rounds of microfluidic barcode ligation (50×50 = 2,500 grids) → library separation by biotin pull-down → sequencing
- **Computational pipeline**: Cell Ranger ARC alignment → tissue filtering (image-based) → iterative LSI with spatial refinement (separate ATAC and RNA) → concatenation of embeddings → Harmony batch correction → Seurat SNN clustering + spatial smoothing
- **Downstream analysis**: Peak-gene linkage by correlation along pseudotime trajectories → DER (Domain of Enhancer Regulatory) activity scores → TF motif enrichment → gene regulatory network construction

See `doc_method.md` for detailed algorithm walkthrough and `doc_code.md` for code-paper mapping.

### Evaluation

#### Datasets

- **Primary data**: Eight sagittal brain sections from C57BL/6 mouse embryos at E11.0, E13.5, E15.5, E18.5 (two sections per stage, 7,118 total grids)
- **Benchmarks**: 10x scATAC-seq (E18.0 brain), spatial-ATAC-seq (Deng et al., *Nature*, 2022), DBiT-seq (Liu et al., *Cell*, 2020), ENCODE bulk ATAC-seq (E15.5 forebrain)
- **Validation**: Allen Mouse Brain Atlas in situ hybridization, scRNA-seq reference (La Manno et al., *Nature*, 2021)

#### Quality Metrics

| Metric | MISAR-seq | Benchmark |
|--------|-----------|-----------|
| ATAC unique fragments/grid | 16,472–34,730 | 10x scATAC: comparable |
| FRiP (fraction reads in peaks) | 15.0–45.6% | Comparable to individual omics |
| Mitochondrial fragments | 2.52–2.95% | Low contamination |
| TSS enrichment | Higher than 10x scATAC and spatial-ATAC | Good signal quality |
| RNA UMIs/grid | Comparable to DBiT-seq | At same 50μm resolution |
| Replicate correlation (ATAC) | High Spearman r | Reproducible across sections |

#### Key Results

1. **16 combined spatial clusters** recapitulating major brain anatomical domains across all four developmental stages
2. **19,025 peak-gene linkages** (FDR < 1e-4, P < 0.05, PCC > 0.45) linking chromatin accessibility to gene expression
3. **37 enriched TF motifs** with tissue-specific distribution, including Neurod1 (DPallm), Rfx2 (diencephalon/hindbrain), and muscle-specific TFs (Myod1/Myog/Myf5)
4. **76,072 putative enhancer-gene linkages** in the corticogenesis trajectory
5. **Pax6→Eomes→Tbr1 feedforward cascade**: Direct regulatory evidence distinguishing promoter vs enhancer mechanisms during corticogenesis
6. **Epigenetic priming**: Chromatin accessibility precedes gene expression along pseudotime (e.g., Neurod6, Thra, Mef2c gain accessibility before expression increases)

#### Biological Validation

- Spatial cluster patterns consistent between biological replicates (RMSE similarity)
- ATAC peaks overlap with ENCODE bulk data from E15.5 brain
- Cell-type deconvolution (RCTD) agrees with anatomical annotation
- Marker gene spatial patterns validated by Allen Brain Atlas ISH data
- Integration with scRNA-seq reference shows concordant cell-type mapping

### Reproducibility

**Rating: 3/5** (Moderate)

#### Strengths
- Raw data publicly available (NGDC: OEP003285)
- Code repository on GitHub with core analysis scripts
- Software versions documented (R 4.1.2, ArchR 1.0.1, Seurat 4.1.0, etc.)
- Example sample data provided (E15.5-S1)
- Shell pipeline for end-to-end preprocessing

#### Weaknesses
- **Major code gaps**: Graph convolution + deep embedding clustering described in Methods are absent from the repository — the actual clustering uses different methods (standard Seurat SNN + spatial refinement)
- **Incomplete pipeline**: GRN construction code, RCTD deconvolution code, and RMSE similarity scripts are not provided
- **Single-sample scripts**: Provided code processes one sample (E15_5-S1); multi-sample integration with Harmony and the full 7,118-grid analysis across all stages is not scripted
- **Data processing dependency**: Raw fastq → Cell Ranger ARC requires a custom barcode whitelist and specific Cell Ranger ARC version (v2.0.1), which may be difficult to reproduce with newer versions
- **Chinese data repository**: Raw data on NGDC (biosino.org) may have slower access for international researchers

#### Practical Notes
- DER.R hardcodes a data path (`data/seurat_rna_atac_all.rds`) — users need to adapt to their file locations
- The Python `utils.py` requires `numba` and is called from R via `reticulate` — this cross-language bridge can cause version compatibility issues
- H&E image processing requires manual annotation step in Adobe Photoshop (creating white/black mask) before automated grid filtering
- Memory requirement: moderate (~16 GB RAM sufficient for single section); Cell Ranger ARC requires 64 GB

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
