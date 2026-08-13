---
layout: default
permalink: /paper-atlas/craniofacialspatiotemporalatlas-37c0da4f/
title: "CraniofacialSpatiotemporalAtlas"
nav: false
description: "颅神经嵴细胞（CNCC）迁移到上颌突后形成骨、牙、肌周支持组织、腭中线及其他结缔组织。关键争议是：这些细胞在进入腭原基前是否已经带有谱系偏向，还是到 E12.5 之后才被局部环境诱导分化。 本文把三种证据串在一起：五个胚胎阶段的 scRNA-seq 提供细胞类型和时间分布；三个阶段的 94 基因 seqFISH 将这些状态放回组织空间；"
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
      <span>Data Sources &amp; Technologies</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>CraniofacialSpatiotemporalAtlas</h1>
    <p>High-resolution spatial transcriptomics and cell lineage analysis reveal spatiotemporal cell fate determination during craniofacial development</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-59206-2" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CraniofacialSpatiotemporalAtlas">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ChaiLabUSC/code" target="_blank" rel="noopener noreferrer" aria-label="Open code for CraniofacialSpatiotemporalAtlas">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 颅面发育时空图谱：腭部间充质命运何时被决定

### 核心生物学问题

颅神经嵴细胞（CNCC）迁移到上颌突后形成骨、牙、肌周支持组织、腭中线及其他结缔组织。关键争议是：这些细胞在进入腭原基前是否已经带有谱系偏向，还是到 E12.5 之后才被局部环境诱导分化。

本文把三种证据串在一起：五个胚胎阶段的 scRNA-seq 提供细胞类型和时间分布；三个阶段的 94 基因 seqFISH 将这些状态放回组织空间；Sox9、Tfap2b 和 Hic1 的诱导型 CreER 谱系追踪直接检验早期标记细胞后来形成何种结构。计算分析提出候选命运路线，原位杂交和小鼠 lineage tracing 决定这些路线是否具有体内支持。

### 1. scRNA-seq 先建立跨阶段细胞词典

作者在 E12.5、E13.5、E14.5、E15.5 和 E18.5 各取 3 个重复，共分析 79,151 个细胞。每个样本保留 200–7,500 个检测基因且线粒体比例 <5% 的细胞，LogNormalize 到每细胞 10,000 counts，选 2,000 个高变基因，并在 ScaleData 时回归 S.Score 和 G2M.Score。直接代码位于 `code/Seurat.rmd:38-56`。

15 个 Seurat 对象合并后重新标准化、PCA，再用 Seurat v5 CCAIntegration 得到共享低维空间：

$$
\max_{u,v}\operatorname{corr}(X_1u,X_2v).
$$

实现使用 `IntegrateLayers(method=CCAIntegration)`，随后在前 20 个 integrated CCA 维度构图，resolution=0.5 聚类并运行 UMAP（`code/Seurat Integration.R:58-94`）。CCA 的作用是寻找跨样本相关结构并减少批次差异；它不能保证所有真实阶段差异都被保留，因此最终解释还依赖 marker、阶段比例和空间验证。

作者先将 26 个大簇归为 mesenchymal、epithelial、endothelial、immune、myogenic 等，再提取间充质簇细分（代码 `:137-178`）。marker 分析使用 `FindAllMarkers(min.pct=0.25, logfc.threshold=0.25)`（`:119-126`）。最终识别 13 类间充质状态，包括 osteogenic、odontogenic、perimysial、midline 和 Sox9+ progenitor。注释是 marker 引导的人工生物学解释，并非聚类算法自动输出的发育命运。

### 2. seqFISH 提供单细胞空间坐标

scRNA-seq 告诉我们“有哪些状态”，但组织解离后不知道它们位于腭板上方、内侧、鼻侧还是牙胚周围。作者因此设计 94 基因 seqFISH panel，在 E12.5、E13.5 和 E15.5 头部切片中逐分子成像。panel 包含 pan-mesenchymal、骨/牙/肌周/中线谱系 marker，以及 epithelial、myogenic 和 anterior–posterior landmark。

每张切片要求细胞至少检测 7 个基因、20 个 transcripts，面积至少 347 pixels；随后 CPM 归一化到 $10^6$、log1p、PCA、20 邻居图和 Leiden resolution=1.0。论文 Methods 和 `doc_code.md` 对这些参数一致，但实际 `Scanpy.ipynb` 未保存在当前代码目录；代码映射来自此前仓库快照/分析记录，当前可直接读取的本地代码主要是两份 Seurat 文件。

单独切片聚类确认 scRNA 定义的主要细胞类型处于预期解剖位置，并发现 Cxcl5/Ntrk2 medial fibroblast 和 Tbx18/Foxf1 nasal fibroblast 等空间亚群。空间 marker 又由 RNAscope 检查，避免把 94 基因 panel 上的聚类标签当作完整转录组事实。

### 3. scVI 如何整合多个 seqFISH 阶段

作者把 E12.5、E13.5、E15.5 的 anterior 与 posterior 切片分别整合。scVI 用负二项观测模型和 VAE 学习潜变量 $z_n$：

$$
x_{ng}\sim \mathrm{NB}(\mu_{ng}(z_n,s_n),\theta_g),
$$

其中 $s_n$ 是 sample batch。论文与旧代码映射均显示 `batch_key="sample"`、2 个隐藏层、hidden width=30；latent 再用于 20-neighbor graph、UMAP 和 Leiden。较小网络适合仅 94 基因的 panel。

这里存在不可抹平的版本差异：论文 Methods 报告 integrated seqFISH 使用 Leiden resolution=4.0，而代码映射记录的 notebook 使用 0.5。当前仓库也没有该 notebook，无法确认论文最终运行是否显式改为 4.0。因此 cluster 数量和细粒度亚群必须标为 paper-reported，而不是由当前本地代码完全重现。

scVI 对齐的意义是比较不同阶段相似表达状态的位置变化，不是自动推断祖先—后代关系。把 E12.5 cluster 和 E15.5 cluster 放在同一 latent space 只能说明分子相似，真正 lineage 需要 CreER 实验。

### 4. 从静态切片读出动态空间变化

作者按阶段绘制相同谱系的空间位置：osteogenic 细胞从腭板上方逐渐转向下方/内侧；midline 细胞从鼻侧向融合中心集中；perimysial 细胞随软腭形成向内外侧扩展。所有主要谱系在 E12.5 已可辨认，说明命运分化至少开始于腭板抬升和融合之前。

这种“动态地图”来自不同胚胎的横断面拼接，不是同一细胞的活体录像。空间连续性、marker 递进和独立重复使解释合理，但只有后续 lineage tracing 才能证明早期细胞的后代去向。

### 5. Sox9+ progenitor 并非均一池

scRNA cluster 0 的 Sox9+ progenitor 在 E12.5 占比最高（约 16.4%），到 E14.5 降至约 7.2%。seqFISH 进一步发现 Sox9+ 细胞内部已出现互斥或偏向性的组合：Sox6+/Sox9+ 偏 osteogenic，Tfap2b+/Sox9+ 偏 odontogenic，Hic1+/Sox9+ 偏 perimysial。

Sox9-CreER;tdTomato 在 E11.5 诱导，E13.5/E16.5 检查后代，显示 Sox9+ 早期细胞确实贡献多个间充质谱系。这证明 Sox9 池具有广泛贡献，但不表示每个单独 Sox9+ 细胞都是全能；群体层面的多谱系输出也可能来自多个已带偏向的 Sox9 亚群。seqFISH 的异质性结果正支持后一种更谨慎解释。

### 6. Tfap2b 与 Hic1 将命运窗口推到腭发生之前

论文向更早的 E9.5–E11.5 检查 marker。Tfap2b 在牙源性区域逐渐受限，Hic1 在未来肌周/软腭区域形成特定空间域。RNAscope 确认这些表达不是 seqFISH 聚类伪影。

Tfap2b-CreER 和 Hic1-CreER 分别在不同早期时间给予 tamoxifen，再于 E16.5 观察 tdTomato 后代。E11.5 诱导能有效标记预期 odontogenic 或 perimysial territory，而更早诱导的效率/特异性模式不同。结合表达域形成，作者将关键 fate determination window 定位在 E10.5–E11.5，即 palatogenesis 开始前。

CreER 结论仍受驱动基因表达阈值、tamoxifen 动力学和 recombination efficiency 影响。它证明“在该时间表达该 marker 的群体后来主要贡献这些组织”，不等于测得一个瞬时、不可逆的分子承诺点。

### 7. 主图的证据链

- Fig. 1：五阶段 scRNA atlas 和主要 mesenchymal clusters，建立 lineage marker 词典。
- Fig. 2：E15.5 seqFISH 空间图，验证细胞状态的解剖位置并显示新增 fibroblast 亚群。
- Fig. 3：跨 E12.5、E13.5、E15.5 的 integrated seqFISH，展示 osteogenic、midline、perimysial 等谱系的空间迁移/扩张。
- Fig. 4：Sox9+ progenitor 的阶段变化、空间位置和 Sox9-CreER 多谱系贡献。
- Fig. 5：Sox6/Tfap2b/Hic1 与 Sox9 的组合，揭示 E12.5 progenitor 内部预先存在的谱系偏向。
- Fig. 6：更早期 RNAscope 与 Tfap2b/Hic1 lineage tracing，将 fate window 定位至 E10.5–E11.5。

`figure_analysis.md` 已逐图记录面板、marker、空间结构和证据边界；图像来自 paper Markdown 的内嵌/引用上下文，最终定量读数仍应回到原图和图注。

### 8. 代码可复现性和明确边界

当前本地代码可直接验证 scRNA 的 QC、normalization、cell-cycle regression、CCA integration、20 维构图、resolution=0.5 clustering、marker 和 mesenchymal subset。路径仍含 `.../` 与 `~/`，没有统一环境或一键 pipeline。seqFISH 的 `Scanpy.ipynb` 和 `scvi_tool.ipynb` 在 `doc_code.md` 中有此前证据映射，但不在当前 `code/` 快照；94 基因 panel、SGNlite/TissUUmaps 处理和最终手工 cluster annotation 也不完整。

因此，最强结论来自多种证据汇合：scRNA 发现状态，seqFISH 定位，RNAscope 检查 marker，CreER 检查后代。算法本身没有“证明命运”；它缩小候选群体和时间窗口。最稳妥的生物学表述是：腭部 CNCC-derived mesenchyme 在 E12.5 已呈谱系偏向异质性，而 Tfap2b/Hic1 标记群体的体内后代支持部分命运模式在 E10.5–E11.5、腭发生之前已经建立。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary: High-Resolution Spatial Transcriptomics and Cell Lineage Analysis Reveal Spatiotemporal Cell Fate Determination During Craniofacial Development

**Journal**: Nature Communications 16 (2025-05-12)
**DOI**: 10.1038/s41467-025-59206-2
**Lab**: Chai Lab, University of Southern California
**Type**: Technology application / multi-omics atlas paper

---

### Motivation & Novelty

**Biological problem**: Cranial neural crest cells (CNCCs) migrate into the pharyngeal arches and differentiate into at least 5 mesenchymal lineages that build the face — osteogenic (bone), odontogenic (teeth), perimysial (muscle support), midline (shelf fusion), and connective tissue. A fundamental developmental question is: when and where is cell fate determined? Are CNCCs already programmed before arriving at the palate primordium, or do local signals after E12.5 drive differentiation?

**Why existing methods fall short**: Prior studies used either:
- scRNA-seq (Ozekin et al., *Dev Dyn*, 2023; Jing et al., *Nat Commun*, 2022) — excellent resolution but no spatial context
- 10x Visium spatial RNA-seq (Piña et al., *Nat Commun*, 2023) — spatial but low resolution (~55 µm spots, multiple cells per spot)
- In silico perturbation (Yan et al., *Nat Commun*, 2024) — single-cell + ATAC but limited spatiotemporal dynamics
- Histological sections — static, no molecular identity

None could simultaneously provide (a) single-cell resolution, (b) spatial position within tissue, and (c) longitudinal tracking across developmental stages.

**Key novelties**:
1. First comprehensive spatiotemporal atlas of CNCC-derived mesenchyme using **seqFISH** (subcellular, single-molecule resolution) at E12.5, E13.5, E15.5
2. Multi-stage integration of spatial transcriptomics revealing **lineage-specific spatial dynamics** as palatogenesis unfolds
3. Discovery that **Sox9+ progenitors are already heterogeneous at E12.5**, with distinct subpopulations expressing lineage markers
4. Definitive in vivo proof that mesenchymal fate is determined **at E10.5-E11.5 — before palatogenesis begins**
5. Public data resource on FaceBase (DOI: 10.25550/62-Y0VT) with interactive TissUUmaps visualization

---

### Method Overview

The study combines three complementary approaches:

**1. scRNA-seq Atlas (79,151 cells, 5 stages)**
Palatal tissue from E12.5 to E18.5 (3 replicates/stage) was profiled using 10x Chromium 3' v3. After per-sample QC (200-7500 genes, <5% MT reads), multi-stage integration used Seurat v5 CCA (Hao et al., *Nat Biotechnol*, 2024) across 15 samples. Cell cycle effects were regressed out before clustering (Leiden, resolution=0.5 on CCA embedding). 13 mesenchymal cell types and 8 non-mesenchymal types were annotated by differential marker expression.

**2. seqFISH Spatial Atlas (E12.5, E13.5, E15.5)**
A custom 94-gene panel targeting all palatal cell types was applied to embryonic head cryosections by Spatial Genomics Inc. Individual sections were processed in Scanpy (Wolf et al., *Genome Biol*, 2018) with CPM normalization and Leiden clustering (resolution=1.0). Multi-stage integration used scvi-tools (Gayoso et al., *Nat Biotechnol*, 2022) with a variational autoencoder (n_layers=2, n_hidden=30, batch_key=sample) at high Leiden resolution (4.0) to distinguish fine-grained spatial clusters. Results were visualized in TissUUmaps 3 (Pielawski et al., *Heliyon*, 2023).

**3. In vivo Lineage Tracing**
Inducible Cre-ER drivers (Sox9-CreER, Tfap2b-CreER, Hic1-CreER) × tdTomato reporter were used to trace progenitor contributions. Tamoxifen induction at E9.5, E10.5, or E11.5; analysis at E13.5 or E16.5. Validated predictions from the computational spatial analysis.

---

### Evaluation

#### Dataset scale
| Data type | Cells/Sections | Stages | Replicates |
|-----------|---------------|--------|-----------|
| scRNA-seq | 79,151 cells | E12.5, E13.5, E14.5, E15.5, E18.5 | 3/stage |
| seqFISH (individual) | Anterior + posterior sections | E12.5, E13.5, E15.5 | N/A (tissue sections) |
| seqFISH (integrated) | ~200,000+ cells | E12.5, E13.5, E15.5 | Anterior + posterior separately |
| Lineage tracing | 3 CreER drivers | E9.5-E11.5 induction | 3 independent repeats/experiment |

#### Key results

**scRNA-seq**: 13 mesenchymal subtypes characterized with marker gene panels:
- Osteogenic (clusters 5, 11): *Runx2*, *Sp7*, *Ibsp*, *Sox6*, *Smpd3*
- Odontogenic (clusters 7, 8): *Lhx6*, *Msx1*, *Tfap2b*, *Grik1*
- Perimysial (clusters 3, 12): *Hic1*, *Tbx15*, *Aldh1a2*, *Fgf18*, *Ebf2/3*
- Midline (clusters 1, 4, 10): *Tbx22*, *Alx1*, *Meis2*, *Pax3*
- Sox9+ progenitors (cluster 0): enriched at E12.5 (16.4%) → declining to 7.2% by E14.5

**seqFISH spatial validation**: All scRNA-seq-defined cell types confirmed at their expected anatomical locations at E15.5. Two novel populations identified: medial fibroblasts (*Cxcl5*, *Ntrk2*) adjacent to dental epithelium, and nasal fibroblasts (*Tbx18*, *Foxf1*) on the nasal side of soft palate.

**Dynamic lineage tracking**: Osteogenic cells shift from superior palatal shelf → inferior/medial location (most dramatic). Midline cells shift from nasal region → center of palatal shelf. Perimysial cells expand mediolaterally. All lineages identifiable at E12.5.

**Sox9+ progenitor heterogeneity**: At E12.5, Sox6+/Sox9+ (osteogenic progenitors), Tfap2b+/Sox9+ (odontogenic), and Hic1+/Sox9+ (perimysial) subpopulations are already distinct. Sox9-CreER;tdTomato lineage tracing confirms multi-lineage contribution.

**Pre-palatogenesis fate commitment**: *Tfap2b* (odontogenic) and *Hic1* (perimysial) expression becomes spatially restricted in the maxillary process at E10.5-E11.5, confirmed by RNAscope ISH (E9.5, E10.5, E11.5). Lineage tracing from E11.5 (not E10.5) labels respective territories efficiently, pinpointing E10.5-E11.5 as the fate commitment window.

#### Validation strategy
- **Technical**: seqFISH gene expression validated against RNAscope ISH for *Tfap2b*, *Sox6*, *Pax3*, *Hic1*, *Myod1* — all consistent
- **Computational**: Spatial cluster markers cross-referenced against scRNA-seq markers (Supplementary Figs S4a, b)
- **Biological**: Lineage tracing for Sox9-CreER, Tfap2b-CreER, Hic1-CreER validates spatial predictions in vivo
- **Functional**: Temporal progression from broad markers (Runx2, Lhx6) → lineage-specific (Sox6, Tfap2b) → differentiation markers (Sp7, Ibsp, Lef1) establishes molecular hierarchy

---

### Reproducibility

**Rating: 3/5** — The analysis is conceptually reproducible but requires significant effort due to data access barriers and code incompleteness.

**Strengths**:
- scRNA-seq data deposited at GEO (GSE293181) and FaceBase (DOI: 10.25550/62-QZ1A)
- seqFISH data on FaceBase (DOI: 10.25550/62-Y0VT) with interactive TissUUmaps viewer
- Code for main analysis steps is available (GitHub: https://github.com/ChaiLabUSC/code, Zenodo: DOI 10.5281/zenodo.15085996)
- Key parameters documented in Methods section
- All transgenic mouse strains specified with Jackson Laboratory catalog numbers

**Practical reproduction path**:
1. Download scRNA-seq data from GEO GSE293181
2. Run per-sample processing with `Seurat.rmd` (update `.../` paths)
3. Run multi-stage integration with `Seurat Integration.R`
4. For spatial analysis: access FaceBase for H5AD files, use `Scanpy.ipynb` + `scvi_tool.ipynb`
5. Change Leiden resolution to 4.0 in `scvi_tool.ipynb:cell 19` to match paper

**Environment**: R (Seurat v5), Python (scanpy 1.10.0, scvi-tools 1.1, numpy 1.24.4, scipy 1.9.1, pandas 2.2.2, sklearn 1.5.1, matplotlib 3.9.1, torch). GPU required for scVI training.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
