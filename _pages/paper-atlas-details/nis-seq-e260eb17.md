---
layout: default
permalink: /paper-atlas/nis-seq-e260eb17/
title: "NIS-Seq"
nav: false
description: "池化 CRISPR 筛选的目标，是建立“基因扰动 → 细胞表型”的对应关系。传统富集式筛选通常先按生长、FACS 等方式挑出一群细胞，再对群体中的 sgRNA 做测序；这种方案规模大，但会丢失单细胞的空间结构、亚细胞定位和快速动态过程。 光学池化筛选则先用显微镜记录每个活细胞的表型，再在原位读出该细胞携带的 sgRNA。Feldman 等人在 Cell 2019 年发表的方法通过细胞质中的条形码 mRNA 来识别扰动。"
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
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>NIS-Seq</h1>
    <p>NIS-Seq enables cell-type-agnostic optical perturbation screening</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/schmid-burgk/NIS-Seq" target="_blank" rel="noopener noreferrer" aria-label="Open code for NIS-Seq">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## NIS-Seq 方法详解

### 1. 这篇论文要解决什么问题？

池化 CRISPR 筛选的目标，是建立“基因扰动 → 细胞表型”的对应关系。传统富集式筛选通常先按生长、FACS 等方式挑出一群细胞，再对群体中的 sgRNA 做测序；这种方案规模大，但会丢失单细胞的空间结构、亚细胞定位和快速动态过程。

光学池化筛选则先用显微镜记录每个活细胞的表型，再在原位读出该细胞携带的 sgRNA。Feldman 等人在 *Cell* 2019 年发表的方法通过细胞质中的条形码 mRNA 来识别扰动。论文指出，这一设计有两个关键限制：

1. 小细胞、低转录活性细胞或细胞质体积很小的细胞，条形码 RNA 信号不足；
2. 原位测序需要通透细胞，高密度条件下细胞边界会变得不可靠，细胞质测序点难以准确归属到某个细胞核。

NIS-Seq（Nuclear In-Situ Sequencing）的核心思路是：**不要依赖细胞自身持续表达条形码 mRNA，而是在固定后，直接从细胞核内整合的基因组 DNA 上按需扩增 sgRNA 序列信号。**

### 2. 核心创新

作者在 sgRNA 表达盒的 RNA polymerase III 终止子之后加入一个反向 T7 启动子，构建 CROPseq-iT7 载体。活细胞表型成像完成后：

1. 固定并通透细胞；
2. 用 T7 polymerase 对整合在基因组中的 sgRNA 反向互补序列进行体外转录（IVT）；
3. 在细胞核内形成许多局部 RNA 拷贝；
4. 进行逆转录、padlock 延伸与连接；
5. 通过滚环扩增（RCA）形成亮的核内扩增点；
6. 用三色 sequencing-by-synthesis 读取最多 14 个碱基周期。

因此，NIS-Seq 把“细胞质散点归属到细胞”的问题，转换成“核内亮点归属到细胞核”的问题。这个空间转换是方法最重要的创新。

### 3. 输入和输出

#### 输入

- CROPseq-iT7 池化 sgRNA 文库；
- 可进行 CRISPR 编辑的细胞，或后续瞬时递送的 Cas9；
- 活细胞表型图像；
- 多轮 NIS-Seq 三通道图像及核染色图像；
- Cellpose 生成的细胞核/细胞分割掩膜；
- 已知 sgRNA 参考文库；
- 对于零知识分析：单细胞 p65–mNeonGreen 图像及样本表。

#### 输出

- 每个测序点的位置、序列和强度；
- 每个细胞核的主导 sgRNA 序列及置信过滤结果；
- 活细胞表型图像与 NIS-Seq 图像之间的细胞核对应关系；
- 每个细胞的表型数值；
- 每个基因的细胞数、效应量、显著性和 FDR；
- 可选的 768 维图像嵌入、聚类标签和 UMAP 坐标。

### 4. 从输入到输出的完整计算流程

```text
CROPseq-iT7 池化文库
        │
        ▼
细胞转导 + CRISPR 扰动
        │
        ▼
活细胞表型成像 ───────────────────┐
        │                         │
固定 / 通透                       │
        │                         │
核内 T7 IVT                       │
        │                         │
逆转录 → padlock → RCA            │
        │                         │
三色循环测序                      │
        │                         │
周期配准 → 测序点检测 → 碱基识别  │
        │                         │
参考文库匹配 → 核内条形码共识      │
        │                         │
        └──── 图像配准与核匹配 ◄───┘
                       │
                       ▼
             单细胞 = 表型 + sgRNA
                       │
                       ▼
           基因层面效应与 FDR 检验
                       │
             可选零知识图像嵌入
```

#### 4.1 活细胞表型成像

实验先记录动态表型，再破坏性地进行原位测序：

- HeLa 筛选使用 p65–mNeonGreen，检测 IL-1β 或 TNF 刺激后的 NF-κB 核转位；
- THP1 巨噬细胞使用 ASC–GFP，检测 nigericin 或 PrgI+PA 诱导的炎症小体 speck；
- 原代人巨噬细胞使用 C1C–EGFP 报告系统。

这一顺序保留了池化测序通常无法获取的亚细胞位置和动态信息。

#### 4.2 多轮图像配准与测序点检测

不同 NIS-Seq 周期的核染色图像通过 FFT 加速的互相关进行平移配准。随后把前三个测序周期的三个荧光通道相加，进行高通滤波、局部极大值检测和亮度阈值过滤。

仓库中的 `image_analysis/AnalyzeInSituCombined_v2.htm` 直接实现了这套流程。它接收排序好的 2,048 × 2,048 TIFF 图像、Cellpose 核掩膜、补偿矩阵和参考文库；`SpotDetection()` 在 `493-516` 行检查八邻域局部最大值。

#### 4.3 通道解混和三色碱基识别

设测序点 $s$ 在周期 $c$ 的三通道观测为 $y_{s,c}$，平均碱基强度矩阵的逆为 $M^{-1}$，则解混信号可写为：

$$
u_{s,c}=M^{-1}y_{s,c}.
$$

这是对论文文字算法的形式化表达，不是论文中的编号公式。

- C、A、T：取解混后三个通道中的最大值；
- G：作为“暗碱基”，当三个通道都低于该测序点跨周期最大信号的 20% 时调用。

代码在 `AnalyzeInSituCombined_v2.htm:647-690` 中实现了这个规则。

#### 4.4 参考文库匹配和核内共识

论文称，测得序列与反向互补的 Brunello sgRNA 文库匹配时允许 0 或 1 个错配，并排除歧义匹配。匹配后的测序点按核掩膜聚合。

设核 $n$ 中属于序列 $q$ 的测序点总强度为 $I_{n,q}$。主导序列只有在

$$
\frac{\max_q I_{n,q}}{\sum_q I_{n,q}}>\frac{2}{3}
$$

且核内最大信号超过阈值时才被接受。论文给出的阈值是：多数细胞类型为 $7\times10^5$，iMac 为 $2\times10^5$。

这里有一个重要的纸面—代码差异：

- 核内 66.7% 主导比例和强度阈值在 `AnalyzeInSituCombined_v2.htm:841-964` 中有直接实现；
- 但已检查的 HTML 源码只建立精确序列查找表，**没有找到（Not found）允许一个错配的校正实现**（`737-783` 行）。

因此，不能仅凭论文文字把“一错配校正”当作当前仓库已经验证的行为。

#### 4.5 表型图像与 NIS-Seq 图像配准

HeLa 数据先按显微镜 stage 位置配对，再用 FFT 互相关精配准。表型核与 NIS 核之间采用最近中心匹配，要求：

- 最大移动距离 11.1 µm；
- 核面积差不超过两倍；
- 歧义匹配被排除。

`image_analysis/NuclearMatching_v8.htm:411-546` 会计算核质心和面积，使用距离与 0.5–2 倍面积门限，并删除“多个表型核映射到同一个 NIS 核”的情况。

THP1 在刺激后核图像更不稳定，因此论文采用 z-stack 聚合的膜染色轮廓，向内缩 5 个像素估计核位置；先做 8 × 8 降采样的粗配准，再做 2 × 2 降采样的精配准。

#### 4.6 单细胞表型计算

##### p65 核转位

对一个细胞掩膜内的核染色像素 $x_i$ 和 p65–mNeonGreen 像素 $y_i$，表型是 Pearson 相关系数：

$$
r=\frac{n\sum_i x_i y_i-(\sum_i x_i)(\sum_i y_i)}
{\sqrt{n\sum_i x_i^2-(\sum_i x_i)^2}\sqrt{n\sum_i y_i^2-(\sum_i y_i)^2}}.
$$

`QuantCorrelation_v2.htm:217-268` 直接根据逐细胞像素矩计算这个值。

##### 炎症小体 speck

先进行局部背景扣除和高通滤波，把负值设为 0，再比较高频 GFP 信号与总 GFP 信号。`QuantPhenotype_v3.htm:242-292` 输出每个细胞的总强度和高频强度，Figure 3 的 notebook 再形成 specking ratio。

#### 4.7 基因层面的统计检验

发布的 Figure 2/3 notebook 使用同一类分析：

1. 按目标基因聚合细胞；
2. 至少需要 10 个细胞；
3. 计算该基因平均表型与 non-targeting control 平均表型之比；
4. 使用 `mannwhitneyu` 比较两组单细胞分布；
5. 使用 `fdrcorrection` 进行多重检验校正。

这些步骤可在 `figure2/NIS_Figure2A.ipynb:145-182`、`NIS_Figure2D.ipynb:140-171`、`figure3/NIS_Figure3A.ipynb:124-155` 和 `NIS_Figure3E.ipynb:130-161` 中直接核实。

#### 4.8 零知识图像分析

传统分析需要研究者先定义表型，例如 p65 与 DNA 染色的相关系数。论文进一步探索：能否不预先规定“什么是异常”，直接让通用视觉模型组织单细胞图像。

流程为：

```text
712,146 张单细胞 p65 图像
        │
ImageNet-1K 预训练 SwinV2-T
去掉分类头，改为单通道输入
        │
每细胞 768 维向量
        │
200 类 k-means
        │
聚类中心 Ward 层次聚类 → 12 大类
        │
UMAP 二维展示
        │
比较各基因在 12 类中的占比偏移
```

仓库验证了前四个计算模块：

- `figure6/nisseq/model/model.py:4-9`：`num_classes=0, in_chans=1`；
- `embedding/embeddings.py:13-48`：生成并保存 embedding；
- `clustering/__init__.py:15-43`：`KMeans(n_clusters=200, random_state=0)` 和 Ward linkage；
- `umap_fit.py`/`umap_transform.py`：拟合和转换 UMAP。

代码还揭示两个论文正文未强调的细节：UMAP 默认最多用 100,000 个细胞拟合，且 `random_seed: null`，因此默认结果不完全确定。另一方面，基因—聚类过度代表分数、基因排名和 Figure 6 最终绘图代码 **没有找到（Not found）**。

### 5. 结果如何支持方法？

- Figure 1：八种细胞类型都能看到核内亮点；THP1 来源和原代巨噬细胞中，传统细胞质方法没有可见信号。69,525 条 sgRNA 与 NGS 计数相关，$R=0.863$。
- Figure 2：两个 HeLa 全基因组筛选分别连接约 169 万和 131 万个细胞，找回 IL-1β/TNF 特异受体和共享 NF-κB 通路成员。
- Figure 3：两个 THP1 全基因组筛选分别连接约 146 万和 86 万个细胞，找回 *NLRP3*、*NAIP*、*NLRC4*、*ANTXR2* 等炎症小体相关基因。
- Figure 4：在原代人巨噬细胞中完成 28 条 sgRNA 的小规模端到端筛选，共有 2,663 个细胞同时映射到表型和 sgRNA；结果提示该体系中的 PrgI+PA 激活依赖 *ANTXR2*，但未显示对 *NLRC4* 的依赖。
- Figure 5：在人表皮组织片中实现文库特异的条形码识别，但这不是带表型读出的组织扰动筛选。
- Figure 6：零知识嵌入找到了理性定义的 p65/DNA 相关指标遗漏的 *RELA* 表型。

### 6. 如何理解这项方法的价值？

NIS-Seq 的价值不在于提出新的统计检验，而在于重新设计了条形码信号产生的位置和时机：

- **位置：**从细胞质移到细胞核；
- **时机：**从依赖活细胞内源转录，改为固定后由 T7 polymerase 按需扩增；
- **对象：**从不稳定的细胞边界归属，改为更稳定的核掩膜归属；
- **表型：**仍然可以在固定前用任意显微成像方式记录。

这使光学池化筛选可以进入小细胞、低转录细胞、高密度细胞、原代巨噬细胞和组织样本等此前困难的场景。

### 7. 局限与复现边界

- 典型情况下只有 40–60% 的细胞核能映射到参考文库；原因可能包括病毒基因组截短、序列错误、多重整合和碱基识别错误。
- 全基因组筛选需要约 5 天人工操作和大量循环成像。
- 原代巨噬细胞筛选规模较小，组织实验只验证条形码识别。
- 论文正文称原代巨噬细胞筛选使用六轮 NIS-Seq，但 Figure 4g 和图注显示四轮；该不一致需要保留。
- 代码整体匹配度为 **medium**：核心图像处理、六个主要 notebook 和 Figure 6 主干存在，但 Figure 4/5 专用分析、combine-screen 工具、一个错配校正以及 Figure 6 基因排名/绘图均为 **Not found**。
- 论文原始图像总量超过 1 TB；Figure 6 约 250 GB 的图像链接仍是占位符，预计算 embedding 和 UMAP 模型也不在当前快照中。
- 本次分析没有实际运行代码或 notebook，因此只能确认静态实现，不能宣称已经完成端到端复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## NIS-Seq Summary

### Problem

Optical pooled CRISPR screening links a microscopy phenotype to the perturbation carried by each cell. The established Feldman et al. method (*Cell*, 2019) sequences barcoded mRNA in the cytosol, which works best in large, transcriptionally active cells with clear boundaries. The NIS-Seq paper identifies two practical failure modes: weak signal in small or low-transcription cells, and ambiguous assignment of cytosolic spots after permeabilization at high cell density.

### Proposed technology

Nuclear In-Situ Sequencing (NIS-Seq) moves perturbation readout into the nucleus. Its CROPseq-iT7 vector places an inverted T7 promoter downstream of the sgRNA cassette. After live-cell phenotyping and fixation, T7 polymerase generates many local reverse-complement sgRNA transcripts from integrated genomic DNA. Reverse transcription, padlock ligation, rolling-circle amplification and up to 14 cycles of three-color sequencing-by-synthesis yield bright nuclear barcode spots.

The computational workflow then:

1. aligns sequencing cycles by FFT cross-correlation;
2. detects and spectrally unmixes spots;
3. calls bases and maps sequences to the guide library;
4. collapses spots to a dominant nuclear barcode;
5. registers phenotype and NIS-Seq images and matches nuclei;
6. quantifies a cell phenotype; and
7. compares gene-wise single-cell distributions with non-targeting controls using Mann–Whitney tests and FDR correction.

The core novelty is molecular and spatial rather than algorithmic: nuclear, on-demand barcode amplification converts a difficult cytosolic cell-boundary problem into a nucleus-object assignment problem.

### Evaluation and main findings

- Across eight cell types from two species, NIS-Seq produced visible nuclear signals in all tested types, including THP1-derived and primary human macrophages where cytosolic in situ sequencing did not produce visible signal.
- Typical reference-library mapping was 40–60%. A mixed-population experiment showed high specificity with more moderate sensitivity, and NIS-Seq guide counts correlated with PCR-based NGS across 69,525 detected sgRNAs ($R=0.863$).
- Two genome-scale HeLa screens linked 1.69 million IL-1β-stimulated cells and 1.31 million TNF-stimulated cells to perturbations. They recovered stimulus-specific receptors/adaptors (*IL1R1*, *MYD88*, *TNFRSF1A*, *TRADD*) and shared NF-κB regulators (*NFKBIA*, *MAP3K7*, *CHUK*, *IKBKG*), followed by orthogonal-sgRNA validation.
- Two genome-scale THP1 screens linked 1.46 million nigericin-stimulated and 0.86 million PrgI+PA-stimulated macrophages. They recovered expected inflammasome components including *NLRP3*, *NAIP*, *NLRC4* and *ANTXR2*, with orthogonal and clonal validation.
- A targeted 28-sgRNA screen in primary human macrophages mapped 2,663 cells to both phenotype and guide and supported *ANTXR2*-dependent but *NLRC4*-independent PrgI+PA activation in this primary-cell assay.
- Human epidermal sheets showed library-specific nuclear barcode detection, demonstrating tissue compatibility, although this was not a phenotype-linked tissue perturbation screen.
- A SwinV2-T-based “zero-knowledge” analysis embedded 712,146 single-cell images into 768 dimensions, then used k-means, hierarchical clustering and UMAP to reveal visually coherent phenotypes. It surfaced *RELA*, whose reporter-expression phenotype was missed by the hand-designed p65/DNA correlation metric.

### Limitations

- NIS-Seq still leaves 40–60% of nuclei unmapped; proposed causes include truncated viral integrations, sequence errors, multiple integrations and base-calling errors.
- A genome-scale screen requires about 5 days of hands-on processing and substantial cyclic imaging, although the authors automated repetitive liquid-handling steps.
- The primary-macrophage experiment is small and donor-dependent; the tissue experiment establishes barcode detection, not screening performance.
- Figure 6 is exploratory and is not benchmarked against alternative self-supervised or domain-specific representation models.
- The main text says six cycles were used for the primary-macrophage screen, whereas Fig. 4g and its caption show four cycles.

### Reproducibility

**Reproducibility rating: 3/5.** The repository is a credible but incomplete analysis release.

- Overall paper–code fidelity is **medium**. The browser applications source-verify the major image-processing steps, six notebooks implement Figs. 1e,f, 2a,d and 3a,e, and the Figure 6 package implements embeddings, k-means/hierarchy and UMAP.
- The checked-in base caller performs exact reference lookup; the paper’s stated one-mismatch correction was **Not found**.
- Dedicated analysis code for Figs. 4 and 5, the linked combine-screen application, and Figure 6 gene over-representation/ranking and panel assembly were **Not found**.
- Paper-wide raw imaging data exceed 1 TB and are available only on request; Figure 6 references ~250 GB of raw images through placeholder download links, and the corresponding embeddings/model artifacts are absent from this snapshot.
- No code or notebook was executed during this analysis, so runnable end-to-end reproduction is not established.

For technical details, read `doc_method.md`; for source-level fidelity and exact gaps, read `doc_code.md`; for visual evidence, read `figure_analysis.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
