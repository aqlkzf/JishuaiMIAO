---
layout: default
permalink: /paper-atlas/lymphomaspatial-2999e2bd/
title: "LymphomaSpatial"
nav: false
description: "这篇 Nature Genetics 2025 论文研究弥漫性大 B 细胞淋巴瘤（DLBCL）的肿瘤免疫微环境如何在组织空间中组织起来，以及这种空间组织如何影响 T 细胞、肿瘤 B 细胞和细胞间通讯。论文分析了 78 个大 B 细胞淋巴瘤样本和 5 个正常对照，结合 CosMx 单细胞空间转录组、CODEX 空间蛋白组、全外显子测序和 bulk RNA-seq [paper.md:1-12], [paper.md:33-44]。"
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
      <span>Cell-Cell Communication</span>
      <span>Nature Genetics · 2025</span>
    </div>
    <h1>LymphomaSpatial</h1>
    <p>Multi-modal spatial characterization of tumor immune microenvironments identifies targetable inflammatory niches in diffuse large B cell lymphoma</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41588-025-02353-5" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法中文解读

### 这篇论文要解决什么问题

这篇 Nature Genetics 2025 论文研究弥漫性大 B 细胞淋巴瘤（DLBCL）的肿瘤免疫微环境如何在组织空间中组织起来，以及这种空间组织如何影响 T 细胞、肿瘤 B 细胞和细胞间通讯。论文分析了 78 个大 B 细胞淋巴瘤样本和 5 个正常对照，结合 CosMx 单细胞空间转录组、CODEX 空间蛋白组、全外显子测序和 bulk RNA-seq [paper.md:1-12], [paper.md:33-44]。

核心思想是：不要只看“样本里有哪些细胞”，还要看“这些细胞在组织二维空间里如何相邻、成团、互相发送信号”。论文最终定义了 7 类 cellular niches（CNs，细胞生态位/细胞邻域结构），并把这些 CN 与 T 细胞功能状态、肿瘤 B 细胞状态、配体-受体通讯和临床/病理分组联系起来 [paper.md:12-12], [paper.md:61-61]。

### 为什么已有方法不够

论文指出，bulk RNA-seq deconvolution 可以估计细胞组成，但没有单细胞分辨率；scRNA-seq 能看到单细胞状态，但组织解离会丢失二维空间结构；空间蛋白组虽然保留组织结构，但抗体 panel 数量有限，限制了机制发现 [paper.md:21-24]。因此，作者使用 CosMx 空间转录组作为主数据层，用 CODEX 做蛋白层面的正交验证。

### 输入、输出和整体流程

输入包括：

- CosMx SMI 的基因计数矩阵、细胞 metadata、FOV 位置、细胞边界坐标和转录本坐标 [paper.md:167-167]。
- CODEX 31 抗体 panel 的空间蛋白成像结果 [paper.md:33-33], [paper.md:236-281]。
- WES 和 bulk RNA-seq 等分子数据，用于临床/分子背景比较 [paper.md:305-308]。

整体流程可以概括为：

```text
FFPE TMA 组织切片
  -> CosMx 单细胞空间转录组
  -> QC / SCTransform / PCA / Harmony / clustering / UMAP
  -> 主要细胞类型和 19 个细胞状态
  -> 以每个细胞为中心构建 200-pixel 邻域
  -> 根据邻域组成做 k-means，得到 7 个空间 CN
  -> 计算富集、共定位网络、DEG/功能签名、配体-受体通讯
  -> 比较不同 CN、EBV 状态和解剖部位
```

输出不是一个预测模型，而是一套空间免疫图谱和分析框架：它把细胞状态、邻域组成、空间 niche、通讯信号和疾病亚型联系起来。

### 第一步：CosMx 细胞质控、降维、聚类和注释

论文使用 Seurat 处理 CosMx 计数矩阵。细胞过滤规则包括 UMI 数少于 20、基因数少于 10 的细胞，以及缺少明确 canonical marker 表达的细胞；最后保留 1,322,740 个高质量细胞 [paper.md:167-167]。随后使用 SCTransform 标准化，PCA 降维，Harmony 去除 TMA slide batch effect，FindNeighbors/FindClusters 做图聚类，并用 UMAP 可视化 [paper.md:167-167]。

细胞类型注释依赖两类证据：一是 `FindAllMarkers` 找到的差异表达基因，二是人工检查 canonical lineage markers，例如 T 细胞、B/浆细胞、髓系、基质、上皮、红细胞等 marker [paper.md:170-173]。作者还用内部构建的 B 细胞淋巴瘤 snRNA-seq atlas 的大类细胞 signature，通过 `AddModuleScore` 和 joint embedding 进行验证 [paper.md:176-176]。

本地代码中，`Preprocessing.r` 与这一步高度一致：它构建 Seurat 对象，按 `nCount_RNA >= 20 & nFeature_RNA >= 10` 过滤，运行 `SCTransform`、`RunPCA`、`RunHarmony`、`FindNeighbors`、`FindClusters` 和 `RunUMAP` [Preprocessing.r:43-56]；随后列出 lineage marker，使用 DotPlot 和 `FindAllMarkers`，并说明会多轮过滤和重聚类直到得到清晰的细胞状态 [Preprocessing.r:61-83]。

CODEX 的处理在论文中很详细，包括染色、成像、UNet++ 分割、marker-based cell typing、kNN/Leiden 聚类和病理专家复核 [paper.md:236-281]。但本地代码仓库没有 CODEX 图像处理流程，只包含基于缓存表格的 CosMx/CODEX 组成比较绘图 [Figure 1.r:52-72]。

### 第二步：以 200 pixel 半径构建 cellular neighborhood

论文把每个高质量细胞都当作一个中心细胞，定义其 cellular neighborhood 为中心细胞质心 200 pixels（24 微米）以内的所有细胞 [paper.md:179-182]。作者测试了 100 到 2,000 pixels 的不同半径，并用 Spearman 相关评估不同半径得到的邻域结构；补充材料说明不同 cutoff 的邻域结果高度相关 [paper.md:182-182], [supp.md:126-128]。

对每个中心细胞，作者建立一个 cell-by-cell state composition matrix：每一列是一个中心细胞，每一行是一个细胞状态，矩阵元素是该中心细胞邻域内对应状态的细胞数量 [paper.md:182-182]。

本地 `Figure 2.r` 对这一步有直接实现：代码按中心细胞状态和 FOV 循环，读取 `CenterX_local_px` 和 `CenterY_local_px`，设定 `cutoff = 200`，先用正方形窗口筛选候选细胞，再用欧氏距离 `sqrt(...)` 过滤半径内细胞，最后统计 cell_state 频数并保存为 `my_neighbor_list.rds` [Figure 2.r:37-82]。

### 第三步：从 neighborhood 到 7 个空间 CN

论文用 200-pixel neighborhood composition matrix 做 *k*-means 聚类，测试多个 resolution，合并结构相似的 cluster，最终定义 7 个空间 cellular niches [paper.md:185-185]。这 7 类 CN 是：

- CN1_T：T 细胞富集。
- CN2_PC：浆细胞富集。
- CN3_Myeloid：髓系细胞富集。
- CN4_Stromal：基质细胞富集。
- CN5_Tumor-B：致密肿瘤 B 细胞 niche。
- CN6_Diffuse：肿瘤 B 细胞与多种免疫细胞混合的 diffuse niche。
- CN7_Mixed：混合型非肿瘤/少量肿瘤结构 [paper.md:61-61]。

本地代码对这一步是部分支持：`Figure 2.r` 注释说明 CN 来自基于 neighborhood matrix 的 k-means，但实际脚本直接读取缓存的 `spatial_niche.rds`，没有本地实现 `kmeans()` 或 resolution 搜索 [Figure 2.r:137-145]。代码确实重新对 neighborhood matrix 做 PCA，并把缓存 CN 标签投影到 PCA 空间 [Figure 2.r:141-150]。

### 第四步：细胞状态富集的 observed/expected 比值

论文用 observed/expected ratio 判断某类细胞在某个 group 或 niche 中是否富集。方法是先建立 cell state by group 的 contingency table，再用 chi-squared test 计算 expected distribution，然后计算：

$$ &#123;&#123;R}}_&#123;&#123;\rm{o}}/{\rm{e}}}=\frac&#123;&#123;\rm{Observed}}}&#123;&#123;\rm{Expected}}} $$

其中 $&#123;&#123;R}}_&#123;&#123;\rm{o}}/{\rm{e}}}>1$ 表示富集，$&#123;&#123;R}}_&#123;&#123;\rm{o}}/{\rm{e}}}<1$ 表示低于随机期望 [paper.md:188-197]。Extended Data Fig. 3a 展示了这个 $R_{o/e}$ heatmap，并显示 T 细胞、IgG 浆细胞、APOE/C1Q TAM、FRC 分别富集于 CN1-CN4，肿瘤 B 细胞富集于 CN5 和 CN6 [paper.md:487-492]。

代码证据边界：本地 R 脚本中没有找到显式的 chi-squared expected-count 计算或 `pheatmap` 富集热图实现。因此这一步是论文和图像证据支持的方法步骤，不是本地代码已验证的实现。

### 第五步：CellTrek 共定位网络

论文用 CellTrek v0.0.94 的 `scoloc` 构建每个空间 niche 内的细胞共定位网络。简化理解是：对同一个 niche 内的细胞建立 Delaunay triangulation，再基于 minimum spanning tree 得到共定位图；图中节点代表细胞状态，边宽代表两种细胞状态在该 niche 内的接近程度 [paper.md:200-203]。

Extended Data Fig. 4 显示了 7 个 CN 的网络：CN1 以 C5_T 为中心，CN5/CN6 以 C0_Tumor-B 为中心，CN7 没有明显单一中心 [paper.md:495-500]。本地代码没有找到 CellTrek、`scoloc`、`scoloc_vis`、Delaunay 或 MST 的实现。

### 第六步：niche-specific 功能状态分析

论文用 Seurat `FindAllMarkers` 比较不同空间 niche 之间的 DEGs，以及同一种细胞在不同 niche 中的 DEGs [paper.md:206-209]。功能 signature 包括细胞周期、T 细胞 cytotoxicity、T 细胞 exhaustion 等；signature genes 来自 pan-cancer 研究并与 CosMx panel 求交集，然后用 Seurat `AddModuleScore` 计算分数 [paper.md:209-209]。

本地代码支持下游 signature 和统计比较。例如：

- `Figure 4.r` 为肿瘤 B 细胞定义 G1/S 和 G2/M signature，并运行 `AddModuleScore` [Figure 4.r:23-28]。
- `Figure 5.r` 为 EBV 比较定义 T 细胞 cytotoxicity 和 exhaustion signature，计算 score，使用 t-test，并用 `FindAllMarkers` 比较 EBV 组间 T 细胞基因表达 [Figure 5.r:121-199]。
- `Figure 6-7.r` 为不同解剖部位的 T 细胞计算 cytotoxicity、exhaustion 和 cell-cycle signature，并使用 pairwise t-test [Figure 6-7.r:123-160]。

### 第七步：邻域限制的配体-受体通讯

论文只在局部邻域内推断 cell-cell communication。配体-受体数据库来自 CellChat、CellPhoneDB v2.0 和 iTALK，共 4,028 个 ligand-receptor pairs [paper.md:212-215]。通讯活性定义为：

$$ {\rm{Activity}}\left({L},{R},{s},{r}\right)=\sqrt&#123;&#123;{\rm{Exp}}}_&#123;&#123;L},{s}}\times &#123;&#123;\rm{Exp}}}_&#123;&#123;R},{r}}} $$

其中 $L$ 是 ligand，$R$ 是 receptor，$s$ 是表达 ligand 的 sender cell，$r$ 是表达 receptor 的 receiver cell，${\rm{Exp}}_&#123;&#123;L},{s}}$ 和 ${\rm{Exp}}_&#123;&#123;R},{r}}$ 分别是 ligand 和 receptor 的表达值 [paper.md:218-221]。论文明确说这个计算由 Spyrrow v0.1 的 Python 函数 `commu.cn.call` 实现 [paper.md:221-221]。

本地代码从 Spyrrow 计算之后开始：`Figure 3.r` 说明 Python Spyrrow 已经生成了一个矩阵，每行是 cell pair，每列是 ligand-receptor pair；R 脚本读取 `cell_cell_communication_res.rds`，为两个细胞加上 cell_state、CN_cluster 和 sample_ID metadata [Figure 3.r:35-50]。之后 R 代码负责筛选 sender/receiver 状态，统计正 interaction 数量、平均/总强度和比例，并作图 [Figure 3.r:52-88]。

所以，本地 R 脚本能验证“通讯结果如何被汇总和展示”，但不能验证 Spyrrow 公式本身的实现。

### 第八步：normalized PD-L1-PD-1 count 和 intensity

论文定义了两个归一化指标 [paper.md:224-227]：

- normalized PD-L1-PD-1 interaction count：具有正 PD-L1-PD-1 activity 的 myeloid-T 或 tumor-T cell pair 数量，除以对应 niche 中 receiver cells（C5_T 加 NK）的总数。
- normalized PD-L1-PD-1 interaction intensity：这些 cell pair 的 PD-L1-PD-1 activity 总和，除以同样的 receiver-cell 总数。

本地 `Figure 3.r` 对 C6_TAM_APOE_C1Q 到 C5_T 的 PD-L1/PD-1 分析有直接代码：调用 `aggretrate_sum_sample_CN("C6_TAM_APOE_C1Q","C5_T","CD274","PDCD1")`，统计每个 sample/CN 的 T cell 数，计算 `interac_prop = group_count / Total_T_count` 和 `group_sum_by_cell_count = group_sum / Total_T_count`，并对 `interac_prop` 做 Kruskal-Wallis test [Figure 3.r:90-120]。需要注意的是，论文写 receiver cells 是 C5_T 加 NK；本地引用代码中可见的是 C5_T 计数，NK 是否并入 C5_T 在这段代码中没有单独显示。

### 主要生物学发现

1. 不同空间 niche 中 T 细胞状态不同。CN1 中 T 细胞更偏 naive/memory、cytotoxic 且 dysfunction marker 低；CN3 中 T 细胞 cytotoxic 但伴随 dysfunction/exhaustion marker；CN5 中 T 细胞更高表达 *ENTPD1*、*TIGIT*、*PDCD1* 等抑制/耗竭相关 marker [paper.md:67-70]。

2. CN5 是致密肿瘤 B 细胞 niche，肿瘤 B 细胞表现出更高细胞周期和 *BCL2* 特征；CXCL12-CXCR4 通讯在 CN5 中突出，FRC 是 CXCL12 来源之一 [paper.md:81-92]。

3. EBV-positive nodal DLBCL 中，肿瘤 B 细胞比例更低、T 细胞比例更高，CN1 和 CN7 更富集；但 CN1 T 细胞同时有更高 cytotoxicity 和 exhaustion marker，提示慢性刺激和功能障碍 [paper.md:95-106]。

4. Immune-privileged sites（CNS、睾丸、眼）来源 DLBCL 虽然处于免疫特权部位，仍有明显 T 细胞浸润，T 细胞有 cytotoxicity 和 proliferation 信号，但也有 PD-L1-PD-1、Galectin-9-TIM3 等 coinhibitory communication [paper.md:109-128]。

### 图像证据如何支持方法

Fig. 1 展示 cohort、TMA、CosMx/CODEX 和数据分析流程，以及 major lineage UMAP、marker dot plot 和 CosMx/CODEX 组成对照。Fig. 2 是方法核心：它把 200-pixel neighborhood、邻域组成、PCA 空间中的 7 个 CN、CN 组成和代表性 FOV 串起来。Fig. 3-4 展示 niche-specific T cell/tumor-B 功能状态和通讯。Fig. 5-7 把同一框架用于 EBV 状态和解剖部位比较。Extended Data Fig. 3 展示 $R_{o/e}$ heatmap，Extended Data Fig. 4 展示共定位网络，Extended Data Fig. 6 展示通讯拆解 [figure_analysis.md]。

### 代码复现边界

本地代码快照的代码-论文一致性为中等。它对以下部分有较强直接支持：Seurat/Harmony 预处理、200-pixel neighborhood 计算、邻域组成矩阵、PCA 可视化、基于缓存 CN 标签的图形生成、Spyrrow 输出的 R 端聚合、PD-L1-PD-1 归一化汇总和主要统计检验 [doc_code.md]。

但它不是完整端到端复现。重要缺口包括：

- 没有找到 observed/expected enrichment 的显式实现。
- 没有找到 CellTrek `scoloc` 共定位网络代码。
- 没有找到 Spyrrow `commu.cn.call` 的本地 Python 实现。
- 没有找到 CODEX 图像处理、分割和 cell typing 脚本。
- CN 标签从 `spatial_niche.rds` 读取，未本地重跑完整 *k*-means/resolution-selection。
- README 说明 demo data 约 80k cells，基于 demo data 得到的结果可能与论文不同 [README.md:16-17]。

此外，本 workspace 的 CodeGraph 索引存在但为空（0 files / 0 nodes / 0 edges），因此本分析中的代码结论来自直接读取 R 源码，而不是 CodeGraph。

### 局限性

论文自身也强调了限制：TMA 和有限 FOV 可能带来 sampling bias；CosMx 和 CODEX 不是 serial sections，沿 Z 轴分离，不能直接细胞对细胞映射；队列异质性较高，因此无法充分分析 CN 特征和患者结局的关联 [paper.md:143-143]。对本地复现来说，还要额外注意：很多关键上游结果是以 figure 或缓存 RDS 形式出现，而不是完整可重跑源码。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Fast Overview

This Nature Genetics 2025 study uses multimodal spatial profiling to map diffuse large B cell lymphoma (DLBCL) tumor immune microenvironments. The authors profile 78 large B cell lymphomas and five controls with CosMx single-cell spatial transcriptomics, CODEX spatial proteomics, genomics and bulk RNA-seq [paper.md:1-12], [paper.md:33-44]. The core output is a seven-niche spatial framework that links local tissue architecture to T-cell state, tumor-B-cell state and ligand-receptor communication [paper.md:12-12], [paper.md:61-61].

### Problem And Prior Limitations

DLBCL microenvironments are heterogeneous and clinically relevant, but bulk deconvolution loses single-cell resolution, scRNA-seq loses 2D tissue organization, and spatial proteomics is constrained by antibody-panel size [paper.md:21-24]. The paper positions single-cell spatial transcriptomics as a way to retain both cell-state and spatial information.

### Method Contributions

The pipeline starts from CosMx cell-level transcript counts, metadata, FOV positions, cell-boundary coordinates and transcript coordinates [paper.md:167-167]. Cells are filtered, normalized with SCTransform, integrated with Harmony, clustered, annotated by marker genes and DEGs, and validated against an in-house lymphoma snRNA-seq atlas plus CODEX major-lineage comparisons [paper.md:164-176].

The key spatial abstraction is a 200-pixel cellular neighborhood around every retained cell. Each center cell gets a neighborhood composition vector, and *k*-means clustering of these vectors defines seven cellular niches (CN1-CN7) [paper.md:179-185]. The paper then computes observed/expected enrichment, CellTrek co-localization networks, niche-specific DEGs/signatures, Spyrrow ligand-receptor communication scores, and normalized PD-L1-PD-1 count/intensity metrics [paper.md:188-227].

### Key Findings

The seven CNs capture stereotyped lymphoma architectures: T-cell, plasma-cell, myeloid, stromal, dense tumor-B, diffuse tumor/immune and mixed niches [paper.md:61-61]. T cells differ strongly by niche: CN1 T cells show more naive/memory and lower dysfunction markers, while myeloid-rich and tumor-rich niches show stronger exhaustion or checkpoint-associated patterns [paper.md:67-70].

Tumor-B cells are especially enriched in CN5 and CN6. CN5 tumor-B cells show stronger proliferation/BCL2 features and CXCL12-CXCR4 communication, interpreted as germinal-center dark-zone-like biology [paper.md:81-92]. EBV-positive nodal DLBCLs show more T-cell and mixed niches but also cytotoxic/exhaustion programs, suggesting chronic stimulation [paper.md:95-106]. Immune-privileged-site DLBCLs show robust T-cell infiltration into diffuse/mixed niches with cytotoxicity, proliferation and coinhibitory PD-L1-PD-1 or Galectin-9-TIM3 signals [paper.md:109-128].

### Figure Support

Fig. 1 shows the multimodal cohort workflow and major cell-type validation; Fig. 2 shows the neighborhood-to-CN abstraction; Fig. 3 links CNs to T-cell function and PD-L1-PD-1 communication; Fig. 4 focuses on CN5 tumor-B/CXCL12-CXCR4 biology; Fig. 5 compares EBV-positive and EBV-negative nodal cases; Fig. 6-7 compare anatomical sites and IPS immune activation/exhaustion. Extended Data Figs. 1, 3, 4 and 6 support CODEX concordance, $R_{o/e}$ enrichment, co-localization networks and communication decompositions [figure_analysis.md].

### Code And Data Availability

The paper provides CosMx SMI data through GEO accession GSE289194, group assignments in Supplementary Table 1, and WES/RNA-seq data through EGA accession EGAS50000001146 [paper.md:305-308]. The code is available at the Coolgenome/Lymphoma-spatial GitHub repository and Zenodo [paper.md:311-314].

The local code snapshot is an R figure-script repository with cached demo/intermediate RDS files. The README states the demo data include around 80k cells and that results generated from demo data can differ from the paper [README.md:16-17]. Direct source reads confirm exact or partial support for Seurat/Harmony preprocessing, 200-pixel neighborhood construction, neighborhood composition, PCA visualization with cached CN labels, downstream communication aggregation, normalized PD-L1-PD-1 summaries, and statistical comparisons [doc_code.md].

### Reproducibility Notes

Code-paper fidelity is **medium**. The local release is useful for understanding and partially rerunning figure-level workflows, especially the CosMx R analysis and downstream aggregation/plotting logic. It is not a full end-to-end reproduction of the entire paper cohort.

Major missing or external pieces are explicit observed/expected enrichment code, local CellTrek `scoloc` co-localization code, local Spyrrow `commu.cn.call` formula implementation, CODEX processing scripts, and the full *k*-means/resolution-selection path from neighborhood matrix to final CN labels. CodeGraph could not be used for source evidence because the workspace-local index reports `0 files / 0 nodes / 0 edges`; code claims in this analysis use direct R source line reads.

### Limitations

The paper itself notes limitations from TMAs and restricted CosMx FOVs, possible sampling bias, non-serial CosMx/CODEX sections that prevent direct cell-to-cell mapping, heterogeneous cohort design, and lack of outcome association testing for CN features [paper.md:143-143]. For this workspace, the additional practical limitation is that several primary method outputs are available as figures or cached RDS inputs, not as fully reproducible local source code.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
