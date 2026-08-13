---
layout: default
permalink: /paper-atlas/periscope-89fcdc9b/
title: "PERISCOPE"
nav: false
wide: true
description: "PERISCOPE 的核心是：在同一个细胞里，一边用 Cell Painting 拍到丰富的细胞形态，一边用原位测序读出这个细胞携带的 CRISPR guide；随后把同一基因的许多细胞聚合成“形态指纹”，用于筛选命中基因、比较通路关系并提出新的功能假设。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>PERISCOPE</h1>
    <p>A genome-wide atlas of human cell morphology</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/broadinstitute/2022_PERISCOPE" target="_blank" rel="noopener noreferrer" aria-label="Open code for PERISCOPE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PERISCOPE 方法详解：把全基因组 CRISPR 扰动与单细胞形态连接起来

### 一句话理解

PERISCOPE 的核心是：在同一个细胞里，一边用 Cell Painting 拍到丰富的细胞形态，一边用原位测序读出这个细胞携带的 CRISPR guide；随后把同一基因的许多细胞聚合成“形态指纹”，用于筛选命中基因、比较通路关系并提出新的功能假设。

### 为什么需要这种方法

传统 pooled CRISPR 筛选的规模很大，但读出通常只有存活、增殖或少量标记。阵列式显微筛选能看到细胞核、线粒体、高尔基体、细胞骨架等丰富表型，却需要把每个扰动放在独立孔中，成本和规模受限。

PERISCOPE 试图同时保留两者的优势：

- 扰动仍然是 pooled 的，因此可以覆盖约两万个蛋白编码基因；
- 表型是多通道显微图像，因此每个细胞可获得数千个形态特征；
- guide 身份通过原位测序在图像坐标中读出，因此可以把“谁被敲除”和“细胞变成什么样”直接连接起来。

这项工作在 HeLa-DMEM、HeLa-HPLM 和 A549-DMEM 三个条件中建立了全基因组形态图谱。HPLM 是更接近人血浆成分的培养基，因此两套 HeLa 数据还能用于研究营养环境如何改变基因扰动表型。

### 从细胞到基因形态指纹

#### 1. pooled CRISPR 扰动

文库为每个基因设计四条 guide，并加入 1,000 条 nontargeting control。低感染复数使大多数细胞只携带一个扰动。经过筛选和表型形成期后，细胞进入成像流程。

#### 2. Cell Painting

Cell Painting 用多种染料标记细胞核、核仁/RNA、线粒体、肌动蛋白、高尔基体、质膜等结构。CellProfiler 从图像中提取 3,973 个特征，包括强度、纹理、形状、颗粒度、共定位和邻域信息。

这些特征不是抽象的黑盒向量。许多特征保留了通道和细胞区室名称，因此后续可以追问：一个基因主要改变整细胞，还是只改变线粒体、WGA 标记区室或细胞核？

#### 3. 原位测序读取 guide

细胞固定后进行多轮 ISS。每一轮产生碱基特异信号，连续循环组成 guide 对应的 barcode。图像配准后，每个细胞同时拥有：

\[
(\text{guide identity},\; \text{morphology feature vector}).
\]

如果一个细胞出现多个不一致 barcode，分析会把它视为歧义样本而过滤。Extended Data Figure 1 直观展示了 12 个测序循环以及单一/多重 barcode 的差别。

#### 4. 聚合为 guide 和 gene profile

单细胞噪声很大，因此主要推断单位是聚合后的 profile。论文描述的流程是：先按板标准化，再过滤缺失严重、低方差、高相关或已知技术性特征，然后按中位数从细胞聚合到 guide，再从 guide 聚合到基因。

校正后的代码仓库 `2022_PERISCOPE` 直接实现了这一部分：

- `Profile_Aggregation/profile_aggregation.ipynb:61-139` 合并板级 profile、清理 guide，并按缺失、方差、相关性和 blocklist 过滤特征；
- `Profile_Aggregation/profile_aggregation.ipynb:218-267` 继续按中位数生成 gene profile。

这里的中位数聚合可以降低离群细胞和单条 guide 偏差，但也会牺牲信息：如果只有少数细胞出现强表型，聚合值可能把它稀释掉。

### 如何定义一个“形态命中基因”

#### 单特征统计检验

对每个基因、每个形态特征，作者把该基因扰动细胞与 nontargeting control 做 Mann–Whitney U 检验。若某特征满足 `P < 0.001`，就记为该基因的显著特征。

代码中的直接证据位于：

- `Hit_Calling/per_feature_hit_calling.ipynb:63-107`：加载细胞系表达数据，建立 expressed gene 与 zero-TPM gene 集合；
- `Hit_Calling/per_feature_hit_calling.ipynb:109-145`：逐基因、逐特征与 nontargeting control 比较并保存 P 值和 U 统计量。

#### 为什么需要 zero-TPM 对照

仅有 `P < 0.001` 还不能决定一个基因是否真正“命中”，因为 3,973 个特征会带来大量机会。作者把在相应细胞系中转录量为零的基因当作经验阴性对照：理论上，敲除一个没有表达的基因不应稳定地产生表型。

作者统计每个基因有多少显著特征，再取 zero-TPM 基因分布的第 99 百分位作为阈值，相当于经验 1% FDR。全特征分数和通道/区室分数分别计算，这一点很重要：一个只影响线粒体的强表型，放进全部 3,973 个特征后可能被稀释。

Figure 2 notebook 中 `:115-187,217-254` 可看到这套阈值逻辑。代码里有一条注释写成 “FDR 5%”，但实际函数、变量、文件名和上 1% 阈值都对应 1%，应视为遗留注释，而不是算法真的用了 5%。

论文报告的命中数为：

- HeLa-DMEM：1,930 个；
- HeLa-HPLM：1,553 个；
- A549：1,089 个。

这些数字来自论文和已保存 notebook 输出，本次分析没有重新运行计算，因此不能称为独立复现。

### 如何判断形态 profile 是否包含真实生物学

#### 已知复合物与网络关系

如果 profile 有意义，那么同一蛋白复合物或高可信互作网络中的基因，形态应该比随机基因更相似。作者用 Pearson correlation 比较 CORUM 复合物、不同 STRING 置信度的基因对以及随机对照。三个 screen 都显示已知相关基因整体更相似，HeLa 的信号比 A549 更强。

这是一种“表征有效性”验证：它说明形态空间捕捉到了生物组织结构，但不表示任意两个最近邻基因都直接相互作用。

#### PCA 与 UMAP

PCA 用来减少冗余特征，UMAP 用来把基因 profile 映射到二维。Figure 2 notebook 明确使用 cosine 距离、`n_neighbors=4`、`min_dist=0.04` 和固定随机种子 43。UMAP 上的功能标签是人工解释，适合导航和提出问题，不是监督学习得到的真值分类。

#### morphological signal score

为了给“表型强度”排序，作者把显著特征的 P 值转换后求和：

\[
S_g = \sum_{i} -\log(P_{g,i}), \quad P_{g,i}<0.001.
\]

实际 notebook 使用 `-log10(P)`，并用 `P <= 0.001` 掩码（`2_HeLa_Screens_Summary/Figure_2.ipynb:1311-1327`）。这与论文思想一致，但精确复现时应以代码中的底数和边界为准。

### 培养环境比较揭示了什么

HeLa-DMEM 与 HeLa-HPLM 共享许多生物过程，但也出现条件特异的富集和相关结构。论文报告 DMEM 有 391 个富集过程、HPLM 有 321 个，其中 275 个共享，116 个仅在 DMEM，46 个仅在 HPLM。

Figure 3 把两个培养基的 gene–gene correlation 放在同一热图的上下三角中：先在一个矩阵上聚类，再把顺序应用到另一个矩阵。这样能够直接看到哪些模块保持稳定，哪些模块因培养环境而增强、减弱或重组。

值得注意的是，论文 Methods 对一般 PCA 流程描述为接近 90% 解释方差，但 Figure 3 notebook 在这个面板中用了 70%（`3_HeLa_Comparison/Figure_3.ipynb:368-386`）。这属于图特异实现差异，不应在复现时被忽略。

### guide 一致性与 mAP

同一基因的四条 guide 应当比无关 guide 更相似。作者用 cosine similarity 排序，再用 mean average precision 衡量同基因 guide 是否排在前面。

论文给出了通用 AP/mAP 公式；Extended Data 9 notebook 的具体实现更窄：假设每个基因有四条 guide，去掉 query 自身后只看前十名，以剩余三条同基因 guide 为分母，并平均四个 query（`Extended_Data_9/mAP_calculations.ipynb:705-801`）。因此它实现了论文指标的目标，但不是通用公式的逐字版本。

Extended Data Figure 9 显示：每条 guide 的细胞数越多，mAP 越高；论文数据大约处于每条 guide 100–125 个细胞的区间，尚未完全饱和。这解释了为什么提高覆盖度是未来改进的重点。

### 从单特征走向可解释机制

作者没有只依赖 UMAP，而是回到原始 Cell Painting 特征。对于每个特征，选 P 值最小的 20 个基因并保留并列项，再做 GO 富集。Figure 5 notebook 中的 `nsmallest(..., keep='all')` 和 GOATOOLS 流程直接支持这一描述（`5_Single_Features/Figure_5.ipynb:383-445`）。

WGA granularity 是代表性例子：与该特征强相关的基因富集于 vacuolar ATPase/溶酶体相关功能。由于特征名称、通道和实际细胞图像可以对应起来，研究者能从“某基因在二维图上靠近某簇”进一步走向“哪个细胞区室、哪种纹理发生改变”。

仓库还实现了单细胞回取：可以随机取样，或聚类后从最接近平均 profile 的簇中选择代表细胞（`Extended_Data_10/utils/extract_single_cell_samples.py:14-83`）。这些图片有助于解释，但代表细胞是算法选择的例子，不能替代完整分布。

### TMEM251：从形态近邻到实验验证

TMEM251 是这篇论文最完整的发现案例。计算上，作者先计算所有基因与 TMEM251 的 cosine similarity，再对排序结果做 GO Cellular Component preranked GSEA。对应代码位于 `6_TMEM251/Figure_6.ipynb:288-312`。结果指向高尔基体、溶酶体和 V-ATPase 相关生物学。

但相似性和 GSEA 只能产生假设。论文随后加入独立实验：

- TMEM251 定位于高尔基体；
- 敲除后出现溶酶体 WGA 积累；
- mannose-6-phosphate 依赖的溶酶体酶运输受损；
- 溶酶体 pH 没有明显改变；
- 溶酶体水解酶活性下降。

这些结果共同支持 TMEM251/LYSET 参与溶酶体酶运输。正确的证据链是：形态相似性提出方向，富集缩小候选机制，独立实验验证并排除“只是整体 pH 改变”等替代解释。不能把 nearest neighbor 或 GSEA 本身写成机制证明。

### 代码仓库能复现到什么程度

正确的最终分析仓库是 `broadinstitute/2022_PERISCOPE`，本地检查 commit 为 `17d345046beee46c8fa8601f970b66651232e7ed`。`cellpainting-gallery` 是 `cpg0021-periscope` 数据和目录结构的来源，不是最终分析主仓库。

静态检查确认仓库覆盖：profile 聚合、Mann–Whitney 检验、1% FDR 命中、PCA/相关性/UMAP、媒体比较、mAP、单特征 GO、TMEM251 相似性/GSEA，以及单细胞图像读取与展示。环境文件也固定了 Python 和主要依赖版本。

未被完整覆盖的部分包括：

- 从原始显微图像开始的校正、分割、barcode calling 和 3,973 特征提取；
- 一条命令串起全部数据和图的工作流；
- 每个 TMEM251 后续实验的完整定量代码；
- 本地 supplementary Markdown。

本次 Author 阶段只做了源码和 notebook 静态核对，没有运行科学流程。因此最合适的结论是：最终分析与论文的对应度较高，但端到端复现仍依赖外部上游仓库、大体量公开数据和人工组织 notebook。

### 使用这套图谱时应遵守的推理边界

1. **hit 是统计异常，不等于已知机制。** 它表示形态显著偏离阴性对照。
2. **相似度是候选关系，不等于直接互作。** 不同通路可能汇聚到相同细胞状态。
3. **UMAP 和聚类是导航工具。** 布局、参数和人工标签会影响视觉解释。
4. **GO/GSEA 是富集证据。** 重叠基因集和注释偏差会影响网络外观。
5. **代表细胞不是总体。** 聚合与选择都会隐藏异质性。
6. **机制需要正交实验。** TMEM251 案例之所以有说服力，是因为计算线索后还有定位、运输、pH 和酶活实验。

### 最值得复用的研究范式

PERISCOPE 最重要的贡献不只是一个数据集，而是一条可复用的发现链：

\[
\text{全基因组 pooled 扰动}
\rightarrow \text{多区室形态 profile}
\rightarrow \text{统计 hit}
\rightarrow \text{相似性/富集/特征解释}
\rightarrow \text{回看单细胞}
\rightarrow \text{正交实验验证}.
\]

对于未知基因，最稳妥的用法不是只看一个 nearest neighbor，而是同时整合命中类型、区室特征、已知复合物/网络支持、跨条件稳定性、单细胞图像和实验可检验性。这样，形态图谱才能从“大规模描述”转化为可信的机制发现入口。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## A genome-wide atlas of human cell morphology

### Citation

**Ramezani et al.** “A genome-wide atlas of human cell morphology.” *Nature Methods* (2025). DOI: [10.1038/s41592-024-02537-7](https://doi.org/10.1038/s41592-024-02537-7).

### One-sentence summary

PERISCOPE combines pooled CRISPR knockout, Cell Painting, and in situ guide-barcode sequencing to build genome-wide, compartment-resolved morphology profiles that recover known biological organization, reveal environmental dependence, and generate experimentally testable hypotheses such as the lysosomal-trafficking role of TMEM251/LYSET.

### Why this paper matters

Genome-wide CRISPR screens usually trade phenotypic richness for scale: pooled assays can test many perturbations but often read out only survival or a small number of markers, while image-based arrayed screens provide rich phenotypes at much greater cost. PERISCOPE narrows this gap by optically linking a guide barcode to a multichannel Cell Painting phenotype in the same cell (`paper.md:18-47`).

The resulting atlas is valuable in two ways. First, it identifies genes whose perturbation changes morphology at whole-cell or compartment level. Second, it provides continuous profiles that can be compared across genes, conditions, and cell lines to recover complexes, pathway organization, and candidate functions for poorly characterized genes.

### What the authors did

The authors used a four-guide-per-gene pooled CRISPR library with 1,000 nontargeting controls. They screened HeLa cells in DMEM and HPLM and A549 cells in DMEM, stained cells with Cell Painting, decoded perturbations through repeated ISS cycles, and extracted 3,973 image features. After quality control, features were standardized, filtered, median-aggregated to guide and gene profiles, and tested against nontargeting controls (`paper.md:33-47,189-306`).

For hit calling, every gene-feature pair was compared with nontargeting controls using a Mann–Whitney U test. The number of features with `P < 0.001` formed a morphology score, and zero-TPM genes provided empirical negative controls for a 1% FDR threshold. Whole-cell and compartment-specific signals were considered separately (`paper.md:309-312`).

The authors then assessed biological coherence with CORUM and STRING relationships, visualized gene profiles with UMAP, compared media through enrichment and paired correlation heat maps, interpreted individual features through GO enrichment and cell retrieval, and used profile similarity to prioritize TMEM251 for mechanistic follow-up.

### Main results

- **Large genome-wide atlases:** 20,421 HeLa DMEM profiles, 20,420 HeLa HPLM profiles, and 20,393 A549 profiles were reported.
- **Thousands of morphology hits:** the paper reports 1,930 HeLa DMEM hits, 1,553 HeLa HPLM hits, and 1,089 A549 hits at the chosen empirical threshold (`paper.md:50-76,99-116`).
- **Biological coherence:** genes in the same CORUM complexes or higher-confidence STRING relationships tend to have more similar morphology than random pairs.
- **Environmental dependence:** HeLa DMEM and HPLM share a large functional core but also show media-specific enriched processes and rewired correlation blocks. The paper reports 275 shared, 116 DMEM-only, and 46 HPLM-only enriched terms (`paper.md:79-96`).
- **Interpretable features:** individual Cell Painting measurements can concentrate coherent gene functions; a WGA granularity example highlights vacuolar ATPase/lysosomal phenotypes (`paper.md:119-136`).
- **Productive hypothesis generation:** TMEM251 morphology similarity pointed toward Golgi/lysosomal biology. Follow-up experiments supported a role in mannose-6-phosphate-dependent lysosomal enzyme trafficking without a detectable change in lysosomal pH (`paper.md:139-156`).

These are paper results. They were not numerically rerun in this analysis.

### Code and reproducibility assessment

The correct final-analysis repository is [`broadinstitute/2022_PERISCOPE`](https://github.com/broadinstitute/2022_PERISCOPE), inspected locally at commit `17d345046beee46c8fa8601f970b66651232e7ed`.

Static inspection found direct notebook or Python support for:

- profile feature selection and median aggregation;
- per-feature Mann–Whitney tests and zero-TPM controls;
- whole-cell and compartment 1% FDR hit thresholds;
- morphology signal scoring;
- PCA, Pearson correlation, CORUM/STRING comparisons, UMAP, and paired heat maps;
- guide-level mAP;
- per-feature GO enrichment;
- TMEM251 cosine-similarity/GSEA prioritization;
- Gallery-backed single-cell sampling and image rendering.

The repository pins its environment and includes public-data instructions, intermediate outputs, and figure notebooks. However, it is not a self-contained raw-data-to-paper workflow. Raw image correction, segmentation, barcode calling, and feature extraction are externalized; many analyses depend on notebook state and large remote files; and complete code for every TMEM251 validation assay was not located.

**Reproducibility rating: 3.5/5.** The final computational analysis is unusually transparent and closely connected to the paper, but full end-to-end reproduction requires upstream repositories, substantial resources, and manual notebook orchestration. No runtime reproduction was attempted here.

### Important implementation nuances

- The paper writes the morphology signal as a sum of `-log(P)`, while the Figure 2 notebook uses `-log10(P)` and an inclusive `P <= 0.001` mask.
- The paper provides a general mAP equation over a ranked list; the Extended Data 9 notebook assumes four guides, evaluates the top ten after self-removal, and divides by the three possible matching guides.
- The general Methods section describes PCA features near 90% explained variance, while the Figure 3 media-comparison notebook uses a panel-specific 70% cutoff before paired heat-map construction.
- A notebook comment mentions “FDR 5%,” but the implemented upper-1% control threshold, variable names, filenames, and paper all indicate 1%; the comment appears stale.

These differences do not invalidate the overall analyses, but they matter for exact reproduction and should be reported rather than silently harmonized.

### Strengths

- Combines true genome-scale perturbation coverage with rich, multichannel morphology.
- Uses compartment-aware hit calling to preserve localized phenotypes.
- Tests representation quality against established complexes and networks.
- Includes multiple cell contexts and a physiologic-like medium comparison.
- Connects aggregate profiles back to interpretable features and single-cell images.
- Demonstrates a complete discovery arc from computational nomination to experimental validation.

### Limitations

- The workflow is experimentally and computationally intensive: the paper estimates about four weeks of wet-lab work and two weeks of computing (`paper.md:171-186`).
- Sensitivity depends strongly on guide representation, knockout efficiency, and the number of cells per perturbation.
- Zero-TPM empirical controls require appropriate expression data and encode a particular FDR design choice.
- Aggregation can obscure heterogeneous or rare single-cell responses.
- Similarity, clustering, and enrichment are hypothesis-generating and do not uniquely identify mechanism.
- A549 signal is weaker, plausibly because of lower Cas9 efficiency, illustrating that screen quality is cell-line dependent.
- The corrected repository does not contain a one-command end-to-end pipeline or complete executable evidence for all upstream and validation steps.

### Practical takeaways

PERISCOPE is best treated as a phenotypic discovery atlas rather than a definitive interaction map. A strong use pattern is to combine several layers—hit status, profile similarity, compartment-specific features, known-network support, and retrieved cells—before choosing candidates for orthogonal experiments. The TMEM251 case study shows why: morphology similarity was useful because it produced a specific organelle/trafficking hypothesis that was then tested independently.

For computational reuse, begin with the public `cpg0021-periscope` data and the `2022_PERISCOPE` aggregation/hit-calling notebooks, preserve the exact notebook-specific parameters, and avoid assuming that publisher equations fully specify implementation details.

### Evidence status

- **Primary paper:** reopened and used throughout; Nature HTML Markdown, 761 lines.
- **Corrected code:** reopened directly; `2022_PERISCOPE` at the fixed commit above.
- **Figures:** all six main and ten Extended Data images visually inspected.
- **Supplementary source:** no local supplementary Markdown was available; it was not reacquired or OCR-processed.
- **Runtime:** no scientific workflow or notebook was executed.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
