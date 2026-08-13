---
layout: default
permalink: /paper-atlas/meningiomaatlas-2b040cf0/
title: "MeningiomaAtlas"
nav: false
description: "脑膜瘤已经有比较成熟的分子分型和染色体臂级别标志物，例如分子组 MG、1p/22q 缺失等；这些信息能解释一部分临床异质性，但仍然不能回答一个更细的问题：同一个肿瘤内部、肿瘤和硬脑膜交界处、以及肿瘤微环境中的不同细胞状态，到底如何影响脑膜瘤进展？论文明确提出，需要用单细胞和空间分辨的组学来解析这种肿瘤级别异质性 。"
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
      <span>Nature Genetics · 2026</span>
    </div>
    <h1>MeningiomaAtlas</h1>
    <p>Spatially resolved single-cell analyses of human meningioma identify novel cell states influencing tumor microenvironment and progression</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/patilvikas/Meningioma_spatial_transcriptomics" target="_blank" rel="noopener noreferrer" aria-label="Open code for MeningiomaAtlas">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法中文解读

### 这篇论文要解决什么问题？

脑膜瘤已经有比较成熟的分子分型和染色体臂级别标志物，例如分子组 MG、1p/22q 缺失等；这些信息能解释一部分临床异质性，但仍然不能回答一个更细的问题：同一个肿瘤内部、肿瘤和硬脑膜交界处、以及肿瘤微环境中的不同细胞状态，到底如何影响脑膜瘤进展？论文明确提出，需要用单细胞和空间分辨的组学来解析这种肿瘤级别异质性 (`paper.md:18-21`)。

因此，这篇论文不是提出一个单一算法，而是构建一个多模态脑膜瘤图谱：snRNA-seq、Visium HD 空间转录组、bulk DNA methylation/RNA-seq、蛋白质组和血浆甲基化共同支持同一个问题 (`paper.md:30-30`, `paper.md:190-190`)。

### 数据和输出是什么？

主要输入包括：

- 102 个 snRNA-seq 样本，580,185 个高质量细胞核；其中 68 个样本、392,818 个细胞核作为 atlas 队列用于细胞状态发现 (`paper.md:30-30`, `paper.md:44-44`)。
- 43 个 Visium HD 空间转录组样本，7,146,538 个分割后的细胞 (`paper.md:30-30`)。
- 712 个 bulk DNA methylation/RNA-seq 样本，用于分子组、bulk 去卷积和预后建模 (`paper.md:30-30`)。
- 88 个 bulk 蛋白质组样本和 59 个血浆甲基化样本，用于外部/转化层面的验证 (`paper.md:30-30`, `paper.md:190-190`)。

主要输出是细胞类型、细胞状态和空间关系的图谱，尤其是围绕髓系细胞状态展开：它们在不同分子组中不同，从硬脑膜到肿瘤发生转变，与肿瘤性细胞有状态特异性的相互作用，并且和患者进展风险相关 (`paper.md:44-62`, `paper.md:126-184`)。

### 总体计算流程

```text
snRNA-seq / Visium HD / bulk RNA 和甲基化数据
        |
        v
单细胞质控与注释
  - Seurat + scDblFinder
  - inferCNV + scATOMIC + 标志基因人工检查
        |
        v
按细胞类型发现 metaprogram, MP
  - 每个样本、每个细胞类型单独做 NMF
  - rank k = 6..9
  - 每个 program 取 top 50 genes
  - 过滤跨 rank 重复出现的稳健 program
  - 按基因重叠/Jaccard 聚类
  - 基因出现在 >=25% 组成 program 中则进入 MP
  - 用 AUCell 给每个细胞打 MP 分数
        |
        +-----------------------------+
        |                             |
        v                             v
bulk 和预后分析                 空间转录组分析
  - BayesPrism 去卷积            - bin2cell/StarDist 分割细胞
  - ssGSEA 打 MP 分数             - RCTD 注释细胞类型
  - Cox / Brier / ICS 风险模型     - 硬脑膜距离、邻域分析
                                  - CellNEST / Ripley / density
        |                             |
        +-------------+---------------+
                      v
         解释髓系细胞状态如何塑造微环境并影响预后
```

### 1. 单细胞质控和细胞类型注释

论文的 snRNA-seq 质控规则很直接：保留至少 1,000 UMIs 的细胞，去除线粒体转录本比例超过 3% 的细胞，用 scDblFinder 去除 doublet，并用 DecontX/DIEM 估计 ambient RNA (`paper.md:228-234`)。

代码中 `seurat_preprocessing.R` 对应这些步骤：创建 Seurat 对象时设置 `min.features = 1000`，计算 `percent_mito` 并筛选 `<3`，再用 `scDblFinder` 找 doublet，随后执行 NormalizeData、FindVariableFeatures、ScaleData、PCA、邻居图、聚类和 UMAP (`seurat_preprocessing.R:31-62`)。

细胞类型注释更复杂。论文说先用 inferCNV 判断有大尺度拷贝数改变的 cluster 为 neoplastic；拷贝数中性的 cluster 再结合 canonical marker 和 scATOMIC；如果某些拷贝数中性 cluster 是患者特异的、且不表达髓系/内皮/淋巴标志，也会被归为 neoplastic；这个过程会迭代重复，并移除不确定细胞 (`paper.md:237-240`)。代码里能看到 inferCNV 和 scATOMIC 的主要步骤：`inferCNV_duracontrol.R` 用 dura 作为 reference (`inferCNV_duracontrol.R:6-18`, `inferCNV_duracontrol.R:34-58`)，`scATOMIC_run.R` 对每个患者运行 scATOMIC 并合并结果 (`scATOMIC_run.R:20-28`, `scATOMIC_run.R:32-48`)。但完整的人工迭代注释过程没有完全脚本化，所以这里是部分复现。

### 2. 用 NMF 找 recurrent metaprograms

论文的核心对象是 metaprogram, 简写 MP。可以把 MP 理解为“在多个样本中重复出现的一组共同表达基因程序”。它不是单个 marker gene，而是一组能描述细胞状态的基因集合。

论文的方法是：对每个细胞类型分别做 sample-wise NMF；某个样本中该细胞类型至少有 50 个细胞才纳入；NMF rank 从 6 到 9；每个 NMF program 用 top 50 genes 表示；只保留跨 rank 稳健出现、非冗余的 program；用 Jaccard/基因重叠聚类；如果某个基因出现在该 MP 的至少 25% 组成 program 里，就进入这个 MP；最后用 AUCell 给每个细胞计算 MP 活性 (`paper.md:249-252`)。

代码对应关系如下：

- `PreProcess_scRNA_RawCounts_to_CPM.R` 把每个细胞类型、每个样本的原始 counts 转成 CPM (`PreProcess_scRNA_RawCounts_to_CPM.R:8-21`)。
- `run_nmf.R` 定义 NMF 函数，并对 rank `6:9` 循环运行，保存 W/H 矩阵 (`run_nmf.R:18-29`, `run_nmf.R:40-49`)。
- `robust_nmf_programs.R` 和 `NMF_downstream_analysis.R` 负责选 top 50 genes、过滤稳健 program、计算基因重叠、聚类 (`robust_nmf_programs.R:13-46`, `NMF_downstream_analysis.R:40-58`)。
- `make.genesets` 用比例阈值选择 MP genes；主脚本里对四类细胞都用了 `0.25` (`NMF_downstream_analysis.R:112-129`, `NMF_downstream_analysis.R:180-183`)。
- AUCell 分数被写入 Seurat metadata，髓系细胞根据最高 MP 分数分配到 cycling、IFN、EMT、TNF、JAK/tissue repair、MYC/metabolic 等状态 (`NMF_downstream_analysis.R:200-201`, `NMF_downstream_analysis.R:351-399`)。

需要注意一个细节：代码里 MP 的边界标签来自人工检查 NMF heatmap 后的 label vectors (`NMF_downstream_analysis.R:173-183`)。所以这个流程不是完全无人工干预的自动算法。

### 3. 髓系细胞状态和分子组的关系

论文发现非肿瘤细胞中髓系细胞占主要部分，并识别出多个髓系 MP：cycling、IFN/surveillance、EMT、TNF/inflammatory、tissue repair、metabolic 等 (`paper.md:47-47`)。随后作者把每个肿瘤内的髓系表达做 pseudobulk，再用 ssGSEA 量化 MP 活性，比较不同 MG 和 WHO grade (`paper.md:59-62`)。

代码里对应的是 `NMF_downstream_analysis.R`：先对髓系细胞用 AUCell 打分，再按患者聚合成 pseudobulk，使用 edgeR 做 TMM/log2CPM，最后用 `ssgseaParam` 和 `gsva` 得到 MP 分数 (`NMF_downstream_analysis.R:255-284`)。后续代码把 MG 和 WHO grade 加到表里并画箱线图 (`NMF_downstream_analysis.R:289-320`)。

生物学解释上，论文强调髓系状态不是随机噪声，而是和脑膜瘤分子组、WHO grade、肿瘤微环境功能相关。例如 tissue repair 在 MG2 更常见，EMT-like 髓系状态在 MG1 更突出，cycling 髓系状态随更高级别或更差预后相关 (`paper.md:59-62`)。

### 4. 空间分析：从硬脑膜到肿瘤

论文有一个关键观察：脑膜瘤几乎都与硬脑膜相连，因此硬脑膜-肿瘤边界可能包含复发和微环境演化的信息 (`paper.md:115-115`)。

在 spatial dura cohort 中，论文显示肿瘤样本中髓系细胞比例远高于周围 dura；髓系状态也发生变化，TNF-like 程序在 dura 中更高，而 EMT 和 metabolic 程序在 tumor 中更高 (`paper.md:115-132`)。代码里 `seurat_spatial_dura_downstream.R` 对空间 dura 相关样本按细胞类型做 Seurat 分析和按患者 batch integration (`seurat_spatial_dura_downstream.R:16-43`)；`NMF_downstream_analysis.R` 把发现的 MP genesets 应用到空间 dura 和内部区域队列上，并计算状态比例和表达差异 (`NMF_downstream_analysis.R:433-510`, `NMF_downstream_analysis.R:517-602`)。

对 Visium HD，论文使用 bin2cell 从 H&E 图像和 2 um bin 中分割出细胞，再用 RCTD 注释细胞类型，只保留 singlet 细胞 (`paper.md:273-279`)。代码 `bin2cell_run.py` 读取 Visium 输出，运行 StarDist，设置 `prob_thresh=0.01`，扩展 labels，并把 bins 汇总成 cell-level 对象 (`bin2cell_run.py:34-75`)。`bin2cell_output_analysis.R` 构建 RCTD reference/query 并把 RCTD 结果加回 Seurat 对象 (`bin2cell_output_analysis.R:31-57`)。

对于硬脑膜边界，代码计算每个非 dura 细胞到 dura 的最近距离，筛出髓系 singlet，给它们计算 MP 分数，然后以 100 um 为 bin 统计 MP 表达并在前 2 mm 拟合趋势 (`bin2cell_distance_to_dura.R:23-43`, `bin2cell_distance_to_dura.R:61-115`)。论文中 BANKSY 加人工 fine-tuning 的 dura 分割步骤在代码里没有完整展开，所以这个步骤只能部分追踪。

### 5. 髓系-肿瘤性细胞相互作用

论文从三条线索分析相互作用。

第一条是 CellChat。论文用 CellChat 在 snRNA-seq atlas 上推断髓系和 neoplastic 细胞之间的 receptor-ligand interaction，只保留 `P < 0.01` 的高可信相互作用 (`paper.md:255-258`, `paper.md:138-146`)。代码 `cellchat.R` 创建 CellChat 对象，使用 human database，识别 overexpressed genes/interactions，计算通信概率，按 `min.cells = 50` 过滤，并用 `thresh = 0.01` 可视化 (`cellchat.R:10-24`, `cellchat.R:36-37`)。

第二条是空间邻域。论文对每个髓系细胞建立 50 um 邻域，取邻域内 neoplastic 细胞的平均基因表达，再和该髓系细胞的 MP 表达相关；Pearson correlation >0.1 的 neoplastic genes 被定义为 MP-correlated genes (`paper.md:282-282`, `paper.md:149-152`)。代码 `bin2cell_myeloid_neighborhood_neoplastic_expression.R` 通过命令行传入距离，并对每个样本调用 `full_monty_optimized` (`bin2cell_myeloid_neighborhood_neoplastic_expression.R:27-41`)；后者用 RANN radius search 找邻居，计算 neoplastic 平均表达并返回髓系 MP metadata (`utilities_bin2cell_receptorligand_distances.R:7-63`)。下游脚本用 `corr > 0.1` 得到二值基因集合并计算 overlap (`myeloid_neighborhood_downstream.R:28-31`, `myeloid_neighborhood_downstream.R:36-90`)。不过 `corr` 本身的计算在已检查代码里不是完整可见的。

第三条是 CellNEST。论文说对 Visium HD 用 CellNEST，保留每个样本 top 20% interactions，再要求髓系-肿瘤性 interaction 在队列中每个方向至少出现 50 次，然后用 Wilcoxon test 和 Benjamini-Hochberg 校正找与特定 MP 显著相关的 interaction (`paper.md:285-288`)。代码从 CellNEST top20percent CSV 输出开始，把 AUCell MP 分数映射到 from/to cells (`cellnest_postprocessing.R:15-30`, `cellnest_postprocessing.R:49-83`)，再用 `>50` 次过滤、z-score 标准化、Wilcoxon test、BH 校正和 top interaction 排名 (`cellnest_downstream.R:8-23`, `cellnest_downstream.R:29-101`)。但 CellNEST 训练本身不在这个 GitHub 快照里。

### 6. 空间组织和共定位

论文使用 Moran's I 衡量 neoplastic MPs 的空间自相关，并观察 1p/22q loss 与更高的空间异质性相关 (`paper.md:109-109`)。代码 `morans_by_MP.R` 对 singlet、非 dura/brain 细胞按类型拆分，计算 AUCell MP 分数，构建 kNN 空间邻接，并运行 `moran.test` (`morans_by_MP.R:29-60`, `morans_by_MP.R:68-120`)。

论文还分析局部细胞密度与 MP 表达的关系 (`paper.md:158-164`)。代码 `MP_by_density.R` 用二维 kernel density 估计髓系和 neoplastic 细胞密度，并计算 Pearson correlation (`MP_by_density.R:28-57`)。

共定位部分有一个重要缺口。论文描述 CRAWDAD 在 50 到 1,000 um 多个尺度上计算 z-score，并用三个 permuted null backgrounds 比较随机性；同时计算 Ripley's inhomogeneous L-cross (`paper.md:291-294`)。代码中找到了 Ripley's L-cross：`ripley's_function.R` 对 myeloid reference 和 neoplastic target，在 0 到 1,000 um、每 10 um 一个 r 值上运行 `Lcross.inhom` (`ripley's_function.R:37-43`, `ripley's_function.R:47-75`)。但没有找到 CRAWDAD z-score/permuted-null 的直接实现。

### 7. bulk 去卷积和预后建模

论文用 BayesPrism 把 bulk RNA-seq 分解到主要细胞类型和状态上，然后在 inferred cell-type-specific expression 上用 ssGSEA 计算 MP 分数 (`paper.md:261-264`)。代码 `Bayesprism_run.R` 构建 single-cell reference、bulk mixture、cell type labels 和 cell state labels，并运行 `run.prism` (`Bayesprism_run.R:8-39`)；`Bayesprism_analysis.R` 提取 fraction 和 expression，再对各细胞类型做 log2CPM 和 GSVA/ssGSEA (`Bayesprism_analysis.R:11-18`, `Bayesprism_analysis.R:47-76`)。

预后部分，论文对每个 MP 做 Cox model：一个模型调整 MG，另一个模型调整该细胞类型丰度；并用 median MP expression 画 Kaplan-Meier 曲线 (`paper.md:267-270`)。最终，论文提出 integrated cell state, ICS score，把七个预后相关 MP 和 MG 结合，提升相对 WHO grade 或 MG 的 outcome prediction (`paper.md:170-184`)。代码里能看到 survival object、feature selection、Cox models、Brier curve、risk score、cutoff、forest plot 和 Kaplan-Meier plot (`Bayesprism_analysis.R:107-162`, `Bayesprism_analysis.R:188-220`)。但这个部分依赖外部 helper/model 和硬编码 cutoff，因此不是完全端到端可复现。

### 图像证据如何支持结论？

Fig. 1 显示 atlas 的细胞类型结构、NMF MP heatmaps、myeloid/neoplastic MP 相似性和 MG 相关的髓系状态差异 (`paper.md:33-38`)。Fig. 2 显示区域性 neoplastic transcriptomic heterogeneity 和相对稳定的 1p/22q CNV (`paper.md:83-88`)。Fig. 3 显示从 dura 到 tumor 的髓系状态转变，以及 TNF MP 在 dura border 附近随距离下降 (`paper.md:118-123`)。Fig. 4 汇集 CellChat、50 um 邻域、CellNEST、density、CRAWDAD/Ripley 等证据，支持髓系-肿瘤性细胞相互作用的状态特异性和空间尺度依赖性 (`paper.md:141-146`)。Fig. 5 显示多个 MP 与 PFS 相关，且 MG + ICS 的 Brier curve 优于 WHO grade 或 MG alone (`paper.md:173-178`)。

扩展图则主要用于验证：Extended Data Fig. 1 支持细胞类型注释，Extended Data Fig. 2 支持公共队列中的 MP 复现，Extended Data Fig. 3 支持髓系 MP marker 的 RNA/蛋白相关性，Extended Data Fig. 4-5 支持 CNV 稳定性，Extended Data Fig. 6 支持血浆甲基化对部分髓系 MP 的近似读出 (`paper.md:514-559`)。

### 复现性评价

代码和论文的一致性是 **medium**。许多关键计算都有直接脚本证据：QC、inferCNV、NMF、MP genesets、AUCell/ssGSEA、CellChat、BayesPrism、bin2cell、RCTD、dura distance、50 um neighborhood、CellNEST downstream、Moran's I、density correlation、Ripley's L-cross。

主要限制是：

- GitHub 仓库是脚本集合，不是一个封装好的 workflow。
- 许多脚本依赖本地 RDS/RDA 中间对象和受控访问数据。
- 细胞注释、MP 边界、dura segmentation 等步骤包含人工判断。
- CellNEST upstream training 和 CRAWDAD z-score pipeline 不在已获取代码中。
- ICS 预后模型的完整端到端重建需要外部 helper、模型文件和 cutoff。

因此，这个仓库适合用来理解论文分析逻辑、核对关键图的生成方式、复用部分脚本；但如果要完全复现整篇论文，需要额外获取 EGA/GEO/Zenodo/MassIVE/dbGaP/SRA 等数据，并重建多个中间对象 (`paper.md:330-333`)。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Paper

**Spatially resolved single-cell analyses of human meningioma identify novel cell states influencing tumor microenvironment and progression**. Nature Genetics, 2026. DOI: `10.1038/s41588-026-02615-w` (`paper.md:1-6`).

### Problem

Meningioma molecular groups and chromosome-arm biomarkers already help predict clinical behavior, but they do not fully explain tumor-level heterogeneity or the role of the tumor microenvironment. The paper targets that gap by profiling meningiomas at single-cell and spatial resolution, including tumor and dura-associated regions (`paper.md:18-21`).

### What The Study Builds

This is an atlas and analysis pipeline rather than a single software method. The authors generate and integrate:

- snRNA-seq: 102 samples and 580,185 high-quality nuclei; an atlas subset of 68 samples and 392,818 high-quality nuclei (`paper.md:30-30`, `paper.md:44-44`).
- Visium HD spatial transcriptomics: 43 samples and 7,146,538 segmented cells (`paper.md:30-30`).
- Bulk validation: 712 DNA methylation/RNA-seq cases, 88 proteomics cases, and 59 plasma methylation cases (`paper.md:30-30`, `paper.md:190-190`).

The central computational output is a set of recurrent cell-type-specific metaprograms (MPs), especially myeloid states that vary across molecular groups, shift from dura to tumor, interact with neoplastic cells, and predict progression (`paper.md:44-62`, `paper.md:126-132`, `paper.md:138-184`).

### Method In One Pass

The paper first performs snRNA-seq QC and cell typing. It filters low-quality nuclei, removes doublets, uses inferCNV and scATOMIC/canonical markers for annotation, and removes ambiguous cells (`paper.md:228-240`). It then identifies cell-type-specific MPs by sample-wise NMF: include cell-type/sample groups with at least 50 cells, sweep ranks `k = 6..9`, define programs by top 50 genes, cluster robust programs by gene overlap, define MPs from genes present in at least 25% of constituent programs, and score MP activity by AUCell (`paper.md:249-252`).

Spatially, Visium HD data are segmented into cells with bin2cell/StarDist and annotated with RCTD (`paper.md:273-279`). The authors analyze dura distance, 50 um myeloid-neoplastic neighborhoods, CellNEST spatial receptor-ligand interactions, local density correlations, CRAWDAD z-scores, and Ripley's L-cross co-localization (`paper.md:279-294`). Bulk RNA deconvolution with BayesPrism maps these cell states into 712 bulk cases, and ssGSEA/Cox models test their prognostic value (`paper.md:261-270`).

### Main Findings

The atlas identifies 11 neoplastic MPs and seven myeloid MPs; among non-neoplastic cells, myeloid cells dominate and show biologically interpretable states such as cycling, IFN/surveillance, EMT, TNF/inflammatory, tissue repair, and metabolic (`paper.md:44-47`). Myeloid states vary by meningioma molecular group and WHO grade, including tissue repair enrichment in MG2 and EMT enrichment in MG1 (`paper.md:59-62`).

Regional sampling shows that neoplastic transcriptional heterogeneity can vary across regions within a tumor, while 1p and 22q copy-number loss proportions remain comparatively stable across sampled regions in the studied internal regional cohort (`paper.md:91-103`). Spatial transcriptomics then links chromosome 1p/22q loss to higher spatial heterogeneity in several neoplastic MPs (`paper.md:109-109`).

The dura-to-tumor analysis shows strong myeloid reprogramming. Tumor samples contain far more myeloid cells than dura samples, and myeloid states shift: EMT and metabolic programs increase in tumor, while the TNF program is suppressed and decreases over short distances from the dural border (`paper.md:115-132`).

Myeloid-neoplastic interactions are state-specific. CellChat, 50 um spatial neighborhoods, CellNEST, density correlations, and global co-localization analyses all support the idea that myeloid states are associated with distinct nearby neoplastic expression programs and spatial organization (`paper.md:138-164`).

Finally, cell states add prognostic information. Cycling and metabolic myeloid MPs are associated with shorter progression-free survival after MG adjustment, while EMT and tissue repair are protective in analogous models; an integrated cell state score improves outcome prediction beyond WHO grade or MG alone (`paper.md:170-184`).

### Code And Reproducibility

The paper states that generated code is available via Zenodo and GitHub (`paper.md:336-339`). The acquired GitHub snapshot is `patilvikas/Meningioma_spatial_transcriptomics` at commit `f2d18aaf62e8d37c8777af3fb4c3828a1fbf6787`.

Code-paper fidelity is **medium**. Strong direct matches exist for snRNA-seq QC, inferCNV with dura controls, NMF/MP construction, AUCell/ssGSEA scoring, CellChat, BayesPrism, bin2cell, RCTD setup, dura-distance analysis, 50 um neighborhoods, CellNEST downstream ranking, density correlations, Moran's I, and Ripley's L-cross. The released code is mostly scripts over precomputed objects rather than a one-command workflow.

Major reproducibility gaps:

- Full iterative cell annotation is only partially represented; scATOMIC and inferCNV code are present, but manual/iterative curation is not fully scripted.
- MP boundary selection includes manual labels derived from inspected NMF heatmaps.
- BANKSY plus manual dura segmentation is described by the paper but not fully implemented in the released scripts.
- Upstream CellNEST training is not included; the code starts from top-20% CellNEST CSV outputs.
- CRAWDAD z-score/permuted-null co-localization code was not found in the GitHub snapshot, although Ripley's L-cross is implemented.
- End-to-end ICS reproduction depends on external data objects, helper functions/models, and hard-coded cutoffs.

Data access is also nontrivial. Newly generated raw sequencing and clinical metadata are deposited in EGA, while public single-cell cohorts, proteomics, and prior bulk datasets are spread across GEO, Zenodo, MassIVE, SRA, dbGaP, and EGA (`paper.md:330-333`). Reproducing the complete atlas therefore requires controlled-access data retrieval and reconstruction of intermediate R objects expected by the scripts.

### Bottom Line

The paper is best read as a multimodal meningioma atlas showing that myeloid states are not passive background cell types: they vary with molecular group, evolve across the dura-tumor interface, align with neoplastic interaction programs, and add prognostic signal. The code release is valuable for tracing the analysis logic and many figure-generation steps, but it is not a fully self-contained reproducibility package.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
