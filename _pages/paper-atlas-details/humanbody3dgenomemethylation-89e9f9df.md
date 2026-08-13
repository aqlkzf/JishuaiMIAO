---
layout: default
permalink: /paper-atlas/humanbody3dgenomemethylation-89e9f9df/
title: "HumanBody3DGenomeMethylation"
nav: false
description: "这项工作先在同一细胞核里配对测量甲基化和 3D 接触，再为每个模态构建适合稀疏单细胞数据的低维表示，用 WNN 联合定义人体细胞图谱，最后在基因组区室、loop/DMR 和细胞 cluster 三个尺度上比较两种表观遗传层何时一致、何时提供互补甚至矛盾的信息。"
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
      <span>Science · 2026</span>
    </div>
    <h1>HumanBody3DGenomeMethylation</h1>
    <p>Human body single-cell atlas of three-dimensional genome organization and DNA methylation</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/zhoujt1994/HumanCellEpigenomeAtlas" target="_blank" rel="noopener noreferrer" aria-label="Open code for HumanBody3DGenomeMethylation">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 人体单细胞三维基因组与 DNA 甲基化图谱：方法详解

### 1. 这篇论文要解决什么问题？

不同细胞类型依靠不同的基因调控程序维持身份。DNA 甲基化反映基因组不同区域的表观遗传状态，三维染色质接触反映染色体在细胞核中的折叠方式；二者都与基因表达有关，但不一定携带相同的信息。

此前工作的主要局限有三类：

1. **bulk 组织测序会平均掉细胞类型差异**，无法区分复杂组织中的亚群。
2. **已有单细胞研究覆盖的组织和细胞类型有限**，很难比较全身不同谱系。
3. **甲基化与三维基因组通常分开测量**，因此无法在同一个细胞核内直接比较两种模态。

论文主文没有完整保留这些既有工作的题名、期刊和年份，参考文献在当前 HTML 转换中也只剩编号，所以本文不补造具体文献信息。可验证的主文结论是：作者用 snm3C-seq 在同一细胞核中同时测量 DNA 甲基化和染色质接触，并把范围扩展到 16 种成人组织（`paper.md:15-27,45-54`）。

### 2. 核心贡献不是一个预测模型，而是一张配对图谱

这项工作不是“输入一个样本，训练一个带损失函数的神经网络，再输出标签”。它更像一个多阶段计算图谱工程：

- 输入：16 种组织、至少两位供体的单细胞核；
- 同核测量：mCG/mCH 甲基化与 3D 染色质接触；
- 细胞级输出：各模态的低维表示、35 个 major type、206 个 subtype；
- 基因组级输出：甲基化 compartment、DMR、A/B compartment、domain、loop；
- 联合输出：两种模态在 compartment、loop、细胞聚类上的一致与不一致。

质控后共有 86,689 个细胞核、1950 亿条非克隆甲基化 reads 和 180 亿条长程染色质接触（`paper.md:27,54-60`）。

### 3. 从实验输入到计算输出

```text
16 种组织，至少 2 位供体
        |
        v
分离细胞核
        |
        v
交联 DNA -> 限制性酶切 -> 连接
        |
        v
细胞核分选 -> 亚硫酸氢盐转换 -> 双端测序
        |
        +------------------------------+
        |                              |
        v                              v
每个细胞的 mCG / mCH              每个细胞的染色质接触
        |                              |
        v                              v
5-kb mCG LSI                    100-kb 3C PCA
        |                              |
        +---------- WNN 联合 ----------+
                       |
                       v
              donor integration / t-SNE
                       |
                       v
             35 个大类 -> 206 个亚型
                       |
        +--------------+----------------+
        |              |                |
        v              v                v
 mCG compartment      mCH           3D genome
 DMR / motif       context / scale   compartment/domain/loop
        |              |                |
        +--------------+----------------+
                       |
                       v
          跨模态相关、ARI 与不一致细胞状态
```

图形摘要 `figure_01.jpg` 和 Fig. 1B `figure_02.jpg` 直接显示了从交联、酶切连接、亚硫酸氢盐转换到双端测序的流程。实验试剂、限制性内切酶、比对步骤、artifact 定义和 QC 阈值位于补充 Methods；官方补充文件下载返回 HTTP 403，因此本地 `SUPP_MD` 为 **MISSING**，这些细节必须标为 **Not found**。

### 4. 三条模态表示支路

#### 4.1 mCG：5-kb 特征与 LSI

代码直接读取 `5kCG_lsi`，选择显著成分，固定取前 100 维并逐细胞归一化，然后以欧氏距离和 perplexity 50 运行 t-SNE（`fig1/03.method_clustering.ipynb:570-620`）。可以把这一支路理解为：

```text
细胞 x 5-kb 甲基化特征
        -> 稀疏高维矩阵
        -> LSI 降维
        -> 归一化低维向量
        -> 邻域与可视化
```

这里的 5-kb 是基因组分箱尺度，不表示每个 bin 都有完整覆盖。准确的覆盖过滤标准在本地证据中找不到。

#### 4.2 3C：100-kb 接触特征与 PCA

联合 notebook 消费名为 `100k3C_pc14_seuratL2` 的接触表示，同时消费 `5kCG_u21_seuratL2` 的甲基化表示（`fig1/04.method_anchor.ipynb:441-444`）。这说明发布代码的联合阶段实际使用：

- mCG 支路的 21 个成分；
- 3C 支路的 14 个成分；
- 两者都已经经过 Seurat 风格的 L2/donor integration 处理。

但是，这个代码片段只验证了联合阶段的输入，并没有完整给出 anchor 如何筛选、供体如何配对、最终标签如何人工审核。

#### 4.3 mCH：100-kb 特征与 PCA

mCH notebook 对特征矩阵运行 `PCA(n_components=100, svd_solver='arpack', random_state=0)`，保留 `100kCH_pca` 的 100 维，再用 perplexity 50 的 t-SNE 可视化（`fig3/07.mCH_clustering.ipynb:363-387`）。

这条支路的重要意义是：即使多数非神经细胞的全局 mCH 很低，基因组空间分布仍可能具有细胞类型结构。它是一种描述性表示，不等于 mCH 对表达有因果作用。

### 5. 两种主模态怎样联合？

代码使用 WNN（weighted nearest neighbors）联合 mCG 和 3C 的低维表示：

1. 取 `5kCG_u21_seuratL2` 与 `100k3C_pc14_seuratL2`；
2. 调用 `wnn(pc_list)` 得到权重和距离表示；
3. 对联合距离表示再做 50 维 PCA；
4. 以 `p_cutoff=0.05` 选择显著 PC；
5. 归一化后运行 t-SNE（`fig1/04.method_anchor.ipynb:441-545`）。

直观上，WNN 不是简单拼接两张矩阵，而是让每个细胞的邻域同时参考甲基化和接触信息。论文据此得到 35 个大类，并结合 scRNA-seq 与 snATAC-seq 进一步标注 206 个亚型（`paper.md:60`）。

需要谨慎的是：本地快照没有验证出一条从原始矩阵、供体整合、外部 RNA/ATAC 映射、cluster merge 到最终 35/206 标签的完整可执行路径。若把发布 notebook 当成一个端到端软件包，会高估其可复现性。

### 6. mCG compartment 为什么不是“按平均值切三段”？

论文把 10-kb 基因组 bin 内各 CpG 位点的甲基化分布作为特征，再进行聚类（`paper.md:72-75`）。直接代码显示：

```python
KMeans(n_clusters=nc, random_state=0, n_init=10)
```

聚类后，状态还会按照平均甲基化重新排序（`fig2/02.PMD_hetero.ipynb:865-921`）。因此，它关注的是一个 bin 内 CpG 的**分布形状**，而不只是单个均值。两个平均 mCG 相似的 bin，可能分别由“高低混合”与“整体中等”组成，分布式表示有机会将它们区分开。

论文最终用三个生物学状态解释结果：

- **hypomethylated**：富集于 TSS 和 cCRE；
- **partially methylated**：与 PMD-like、抑制性区域和 B compartment 相关；
- **hypermethylated**：更接近活跃 A compartment 的大范围背景状态。

论文报告 1,364,566 个 DMR，平均长度 377 bp，覆盖 17.9% 基因组，并找回既往 bulk 图谱中 95.4% 的 DMR，新增 587,648 个区域（`paper.md:81`）。注意：Fig. 2M 图像似乎印成 `1,363,566`，与主文相差 1000；本文采用主文数值并保留差异。

### 7. 3D 基因组如何比较？

论文从三类尺度描述接触图谱：

1. **contact decay**：接触随基因组距离的分布；
2. **A/B compartment 与 domain**：长程区室和局部结构域；
3. **chromatin loop**：特定位点之间的局部增强接触。

作者用短程/长程接触比构造一个连续轴：局部 100 kb-1 Mb 信号主要对应 loop/TAD，比较时用 200 kb-2 Mb；长程 >10 Mb 信号主要对应 compartment，比较时用 10-100 Mb（`paper.md:123-129`）。神经细胞偏 domain-dominant，多个造血谱系偏 compartment-dominant。论文还报告 283,606 个 major-type differential loop，并发现亚型特异 loop 与差异表达相关（`paper.md:132-135`）。

这不是一个优化目标或 loss，而是多个统计汇总和差异分析组成的图谱。loop caller、imputation、domain 阈值、compartment 定向及 FDR 参数在主文中没有给出，本地 supplement 又缺失，因此不能声称已完整复现。

### 8. 两种模态怎样互相验证，又怎样暴露差异？

#### 8.1 基因组尺度的一致性

大多数细胞类型中，A/B compartment score 与 mCG 负相关，即活跃 A compartment 通常较低甲基化；但七个 PMD 强的细胞类型呈正相关。甲基化的 partially methylated compartment 通常对应 B compartment，而 fully methylated compartment 通常对应 A compartment（`paper.md:141-150`）。

这说明二者常常对齐，但不是同一种信号。Fig. 5 还显示甲基化 compartment 在高分辨率下比接触定义的 A/B compartment 更细。

#### 8.2 loop、DMR 与表达

论文把 DMR 与 loop anchor 对齐，比较 motif enrichment，并计算不同亚型中 loop strength 与 anchor mCG 的关系（`paper.md:153-159`）。CTCF 在多数谱系的 loop-associated DMR 中富集，同时出现谱系特异 TF motif。

这些 motif 是**候选调控因子**，不是结合实验。loop 与表达或 DMR 的相关也不能直接推出调控方向。

#### 8.3 细胞聚类的一致与不一致

论文用 ARI 比较 mCG 与 3C 两套 subtype partition（`paper.md:165-168`）：

- ARI 高：两种模态给出的细胞划分更一致；
- ARI 低：两种模态看到的状态结构不同。

骨骼肌 notebook 直接读取 5-kb mCG 与 100-kb 3C 的独立 embedding，分别聚类，再把两套标签放入联合对象比较（`fig6/01.MusSkl_clustering.ipynb:180-202,323-410`）。主文发现一些细胞在接触层面像成熟肌纤维，在甲基化层面仍像 stem cell，因此提出“3D 结构变化可能早于甲基化变化”的解释（`paper.md:171-177`）。

这应被理解为**假设生成**：数据是横断面的，没有 lineage tracing 或时间序列，不能直接证明先后顺序。Schwann cell 等其他谱系也应采用同样的谨慎标准。

### 9. 结果如何验证？

论文没有一个统一的“模型准确率”，而是使用多种一致性证据：

- 同一细胞类型跨供体高度相关；
- 与既往 sorted-cell/bulk methylome 一致；
- loop 特异性与 ENCODE bulk Hi-C 一致；
- DMR 大量覆盖 ATAC peak，同时也保留非 ATAC-peak 的谱系信息；
- 已知谱系 TF motif 被恢复；
- subtype-specific loop 与差异表达对应；
- ARI 定量比较两模态 cluster agreement。

这些结果支持图谱的生物学一致性，但不等于所有统计量都能由本地代码和数据重新计算。

### 10. 研究者使用时最需要记住的边界

1. **补充 Methods 缺失。** 官方下载返回 403，`SUPP_MD` 为 MISSING；QC、calling 和统计阈值不能猜。
2. **代码匹配度为 medium。** 61 个科学 notebook 覆盖很多图和分析，但没有完整 raw-to-atlas 命令。
3. **依赖外部大数据树。** notebook 假定存在 `ENTEX_ROOT` 及大量 ALLC、cooler、h5ad/HDF 中间文件。
4. **部分 panel producer 缺失或未定位。** 包括 Fig. 2O/S13E、Fig. 3I/S23B 和部分 S32 分析。
5. **三份超大 notebook 被保留。** 53 MB、12 MB 和 11 MB 文件没有删除，但 CodeGraph 不索引 notebook；最终代码结论来自直接的局部读取。
6. **bisulfite 的固有限制。** 不能区分 5mC 与 5hmC（`paper.md:207`）。
7. **相关不等于因果。** compartment、loop、DMR、表达与细胞转变之间的联系主要用于描述和提出机制假设。

### 11. 一句话理解这套方法

这项工作先在同一细胞核里配对测量甲基化和 3D 接触，再为每个模态构建适合稀疏单细胞数据的低维表示，用 WNN 联合定义人体细胞图谱，最后在基因组区室、loop/DMR 和细胞 cluster 三个尺度上比较两种表观遗传层何时一致、何时提供互补甚至矛盾的信息。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Human Body Single-Cell Atlas of 3D Genome Organization and DNA Methylation

### Overview

This 2026 *Science* atlas addresses a basic coverage problem in human epigenomics: bulk assays average signals across cell types, while earlier single-cell methylation and 3D-genome studies covered limited tissues or measured the two regulatory layers separately. The authors apply single-nucleus methyl-3C sequencing (snm3C-seq) to measure DNA methylation and chromatin contacts in the same nuclei across 16 adult human tissues (`paper.md:15-27,45-54`).

After quality control, the resource contains 86,689 nuclei, 195 billion nonclonal methylation reads, and 18 billion long-range contacts. Joint analysis of the two modalities identifies 35 major cell types and 206 subtypes, supported by donor concordance and comparison with prior sorted/bulk methylomes, ENCODE Hi-C, scRNA-seq, and snATAC-seq (`paper.md:27,54-60`). The atlas is available through downloadable data, GEO accession GSE326618, an interactive browser, and the paper-linked code repository (`paper.md:237-240`).

### What the Atlas Adds

The main contribution is not one predictive model but a matched, body-wide reference and a set of analyses that expose complementary methylation and 3D-genome structure.

- **CG methylation:** Global mCG spans roughly 59% in trophoblast to 81% in inhibitory neurons. Distribution-based clustering of 10-kb bins yields hypomethylated, partially methylated, and hypermethylated compartments, generalizing PMD-like organization across cell types. The study reports 1,364,566 DMRs covering 17.9% of the genome and recovers 95.4% of DMRs from earlier bulk profiling while adding 587,648 regions (`paper.md:66-87`).
- **Non-CG methylation:** Neurons have the strongest mCH, but low-level mCH in many nonneuronal lineages is spatially organized, depleted at active regulatory elements, and sufficient to separate multiple cell types and subtypes (`paper.md:96-117`).
- **3D genome:** Contact-decay, compartment, domain, and loop analyses distinguish domain-dominant lineages, including neurons, from compartment-dominant lineages enriched among hematopoietic cells. The atlas contains 283,606 loops that differ across major cell types; subtype-specific loops are associated with differential expression (`paper.md:123-135`).
- **Cross-modality structure:** Methylation compartments generally align with A/B compartments, but the relationship changes by lineage and genomic scale. Loop-DMR coupling is similarly heterogeneous (`paper.md:141-159`).
- **Discordant cell states:** Adjusted Rand index and lineage case studies show that mCG- and contact-derived subtype partitions can disagree. Skeletal muscle, Schwann cells, trophoblast, and other epithelial populations illustrate cases where one layer looks discrete while the other follows a gradient or defines additional clusters (`paper.md:165-183`).

### Computational Strategy

The released notebooks support a feature-level workflow rather than an end-to-end package. Direct code reads verify 5-kb mCG LSI features, 100-kb contact PCA features, weighted nearest-neighbor integration, and t-SNE for the joint atlas (`fig1/03.method_clustering.ipynb:570-620`; `fig1/04.method_anchor.ipynb:441-545`). A focused methylation notebook represents each 10-kb bin by its distribution over CpG methylation and uses deterministic k-means settings before ordering states by methylation (`fig2/02.PMD_hetero.ipynb:865-921`). The mCH branch uses 100-kb features, 100-component PCA, and t-SNE (`fig3/07.mCH_clustering.ipynb:363-387`).

These choices explain how sparse modalities are reduced and combined, but the local evidence does not reconstruct all raw-read processing, donor integration, external RNA/ATAC label transfer, or final cluster curation.

### Evaluation and Interpretation

Validation is based on cross-donor reproducibility, agreement with external methylome and Hi-C references, overlap with ATAC peaks, recovery of known lineage motifs, and association of differential loops with expression. The figures show strong biological coherence across these checks, but there is no single held-out benchmark score for the atlas.

The most interesting result is also the one that needs the most restraint: asymmetric methylation/contact assignments in muscle and Schwann cells could reflect different rates of epigenomic change during differentiation. The data are cross-sectional, so this is a hypothesis rather than direct temporal or lineage-tracing evidence (`paper.md:171-180,204`). Motif enrichment likewise prioritizes candidate regulators but does not verify binding.

### Limitations

- Bisulfite sequencing cannot distinguish 5mC from 5hmC (`paper.md:207`).
- Materials and Methods are only in the official supplement, whose direct download returned HTTP 403; no reliable local `SUPP_MD` exists. Exact assay/QC thresholds and several statistical settings are therefore **Not found**.
- The code snapshot is a figure-oriented Jupyter Book with 61 scientific notebooks and large external-data dependencies, not a self-contained raw-data pipeline.
- Several published-panel producers or plotting cells are absent or unpinned in the release, including parts of the motif, mCH-expression, and supplementary discordance analyses.
- CodeGraph covers only 3 files/17 nodes, so notebook claims required focused direct reads. Three notebooks larger than 10 MB are retained, including one 53-MB notebook.
- Fig. 2 panel M appears to print `1,363,566 DMRs`, whereas the article text reports `1,364,566`; the text value is used here and the mismatch remains documented.

### Reproducibility Assessment: 3/5

**Strengths:** the paper links a fixed code snapshot, downloadable processed data, raw GEO data, an interactive browser, explicit methylation/contact software environments, and notebook-level figure workflows. Direct code reads match several central representations and analyses, yielding **medium** code-paper fidelity.

**Constraints:** full reruns require a large external `ENTEX_ROOT` data hierarchy and two computational environments. The missing Methods supplement blocks verification of primary processing and statistical thresholds, no one-command workflow covers raw reads through the final atlas, and some published-panel code is missing. Targeted figure reproduction is plausible with the external inputs; complete reconstruction from raw sequencing is not demonstrated by the local workspace.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
