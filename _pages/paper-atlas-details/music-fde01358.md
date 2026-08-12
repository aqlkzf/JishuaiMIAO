---
layout: default
permalink: /paper-atlas/music-fde01358/
title: "MUSIC"
nav: false
description: "论文：Single-cell multiplex chromatin and RNA interactions in ageing human brain（Nature, 2024；DOI: 10.1038/s41586-024-07239-w） 传统单细胞 RNA 测序告诉我们细胞表达什么，单细胞 Hi-C 告诉我们 DNA 哪些位置接近，但多数方法把一次接触压成两个位点，也看不到同一复合物中的 RNA。"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature · 2024</span>
    </div>
    <h1>MUSIC</h1>
    <p>Single-cell multiplex chromatin and RNA interactions in ageing human brain</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-024-07239-w" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MUSIC：在同一个细胞核里同时读取多路染色质接触、RNA 表达和 RNA–染色质结合

论文：*Single-cell multiplex chromatin and RNA interactions in ageing human brain*（Nature, 2024；DOI: 10.1038/s41586-024-07239-w）

### 核心问题

传统单细胞 RNA 测序告诉我们细胞表达什么，单细胞 Hi-C 告诉我们 DNA 哪些位置接近，但多数方法把一次接触压成两个位点，也看不到同一复合物中的 RNA。MUSIC 的目标是保留两层身份：分子来自哪个细胞，以及哪些 DNA/RNA 分子原本处在同一个复合物。

因此它测的不是常规“RNA+ATAC snMultiome”。这里的 multiome 是基因表达、DNA–DNA 多路接触和 RNA–DNA 结合的联合测量。

### 1. 两层条形码怎样保存两种身份

第一层是 cell barcode。RNA 接 RNA 特异 linker，碎片化 DNA 接 DNA 特异 linker；随后做三轮 split-and-pool，使同一细胞核内的 RNA 和 DNA 带上同一组细胞条形码。

第二层是 complex barcode。释放仍保持物理共复合的分子后，同一个复合物获得共同的 10x GEM barcode 与 I7 barcode。这样：

- 相同 cell barcode 表示来自同一细胞；
- 相同 complex barcode 表示曾处于同一分子复合物；
- linker 表示当前 read 来自 RNA 还是 DNA。

Read 1 为 28 bp，包含 16 bp 10x barcode 和 12 bp UMI；I7 为 8 bp；Read 2 为 150 bp，读取细胞条形码、linker 与一个 RNA 或 DNA insert。与 Hi-C 每个 read pair 直接连接两个 insert 不同，MUSIC 每个 read pair 只读一个 insert，接触关系由多个 reads 共享 complex barcode 重建。

### 2. DD、RR、RD 与“多路”的含义

同一 cell+complex barcode 下的 reads 被分成：

- DD：只有 DNA；
- RR：只有 RNA；
- RD：同时有 RNA 和 DNA。

两个 DNA reads 的 DD cluster 是普通 pairwise contact；三个或更多 DNA reads 的 DD cluster 是 multiplex complex。RD cluster 则能表示某个 RNA 同时关联多个染色质位点。

为了画传统 contact map，一个含 $n$ 个 DNA reads 的 complex 可展开为：

$$
\binom{n}{2}=\frac{n(n-1)}{2}
$$

个成对接触。例如 4 个 DNA 分子产生 6 对。这个展开便于与 Micro-C 比较，却不能把 6 对当成 6 个独立实验事件；它们共享一个 complex provenance。

### 3. H1/E14 混样先验证什么

作者先混合人 H1 与小鼠 E14 胚胎干细胞。若 cell barcode 或 complex barcode 严重串扰，一个 cluster 会混入两个物种 reads。低 species-mixing 支持单细胞和单复合物编码可靠。

在 2,546 个 H1 细胞中，每细胞平均约 144,049 个 DNA reads 和 11,384 个 RNA reads，并得到 DNA-only、RNA-only 与 RNA–DNA clusters。约 27.74% 的非单例 DNA-only clusters 含至少三个 DNA reads，说明多路接触不是极少数例外。

### 4. 为什么要和 Micro-C、RNA-seq、iMARGI 比

MUSIC ensemble DNA contact map 能复现 Micro-C 的 A/B compartment 和 TAD 结构。按 cluster 大小拆分后，小 cluster 主要对应 TAD 内接触，大 cluster 更能恢复 nested TAD 和较长程的结构。只保留两个 DNA read 的 cluster 会丢失部分结构，说明 multiplex 信息有独立价值。

RNA 方面，ensemble MUSIC 与 bulk RNA-seq 的基因丰度相关约 $R=0.8$，与 iMARGI RNA reads 相关约 $R=0.9$；还能看到 pre-mRNA、nuclear-speckle-associated RNA 与 XIST 区域的已知模式。

这些是 ensemble 层面的技术验证，不表示每个单细胞都具有 bulk 级覆盖度。

### 5. 人额叶数据怎样定义细胞类型

作者分析 14 个年龄至少 59 岁的 post-mortem frontal cortex 样本。利用同一细胞中的 MUSIC RNA reads 聚类，得到 excitatory neurons、inhibitory neurons、astrocytes、oligodendrocytes、OPCs、microglia 和 vascular cells，并识别亚群。

这是后续分析的必要分层，因为不同细胞类型的 contact probability 曲线本来就不同。若直接混合所有细胞，样本间细胞组成变化会伪装成染色质结构变化。

### 6. $P_c(s)$ 与 LCS erosion

令 $s$ 为两个基因组位点的距离，$P_c(s)$ 表示该距离 bin 内观察到接触的频率：

$$
P_c(s)=\frac{\text{distance bin }s\text{ 中的接触数}}
{\text{该 bin 中可比较的位点对数}}.
$$

整体上距离越远，$P_c(s)$ 越低。单细胞之间的差别在于曲线峰值和近距离接触保持程度：有些细胞丢失更多 local chromatin structure（LCS），却相对保留长程接触。

作者用单细胞曲线的峰值基因组距离构造 LCS-erosion score。分数越高，峰值越向长距离移动，表示局部结构侵蚀越明显。

这不是直接测得的生物年龄，而是染色质构象指标。论文因此谨慎称 chromatin conformational age。

### 7. 构象年龄与转录年龄的关系

转录年龄由 SCALE 模型基于组织特异 ageing genes 计算。各细胞类型中，LCS-eroded cells 的 transcriptomic-age score 更老；若干小核 RNA 也与 LCS erosion 高度相关。

高 Alzheimer pathology 样本中的 excitatory/inhibitory neurons、astrocytes、oligodendrocytes 和 microglia 显示更低 LCS score。回归分析将 transcriptomic age、cell type、AD pathology 与 sex 列为重要相关因素。

但所有供体都在较窄的老年年龄范围，这解释了为什么 chronological age 难以解释单细胞差异。结果是横断面关联，不能说明 LCS erosion 导致阿尔茨海默病，也不能作为经过临床验证的年龄钟。

### 8. eQTL 为什么需要三维接触才能解释细胞类型特异性

同一个人的 eQTL 序列存在于多种细胞，为什么它只在某些细胞类型影响目标基因？作者把已知 brain cis-eQTL–target pairs 与 MUSIC DNA contacts 叠加，问：eQTL 与目标启动子发生接触的细胞类型，是否正是该 eQTL 产生表达效应的细胞类型。

总体和 cell-type-exclusive pairs 都显示显著富集。例如 *NELL1* 的 contact/eQTL effect 出现在 excitatory neurons，*PREX2* 出现在 oligodendrocytes。

这支持“细胞类型特异的三维接近帮助产生细胞类型特异遗传效应”。但 DNA 接触不是增强子功能的充分条件，仍需 perturbation 验证方向与因果。

### 9. XIST–X chromosome association level

女性细胞中，含 XIST RNA 和 chromosome-X DNA 的 RD cluster 被视为 XIST-associated。细胞间这类 cluster 数量差异很大，形成 XIST–X association level（XAL）。作者按 zero/low/medium/high XAL 分组，并用总 RNA read 阈值减少由于测序太浅造成的假阴性。

RNA attachment level（RAL）描述 XIST 在各 genomic bin 的附着强度；cumulative RAL 显示它主要覆盖 X chromosome。比较 XIST-positive 和 XIST-negative chromatin：XAL 越高，两者 $P_c(s)$ 曲线差异越大，尤其在大约 10 Mb 内外出现不同趋势。

不同细胞类型中，excitatory neurons 的差异最大，inhibitory neurons 和 astrocytes 较弱；独立 sequential FISH 结果与这种细胞类型差别一致。

MUSIC 并没有直接标记哪一条 homolog 是 Xa 或 Xi。把 XIST-positive 解释为 inactive-X 相关结构有坚实生物学依据，但单细胞稀疏性和检测阈值仍是边界。

### 10. 四张主图怎样形成证据链

1. 图 1：解释 linker、cell barcode、complex barcode，并报告单细胞产量。
2. 图 2：用 Micro-C、RNA-seq 和 iMARGI 验证 DNA/RNA/RD 信号；证明 multiplex clusters 补充 pairwise contacts。
3. 图 3：从 cortex cell types 到 $P_c(s)$、LCS erosion、transcriptomic age、pathology 和 eQTL contact。
4. 图 4：展示 XIST expression、RAL/XAL、XIST-positive versus negative contact curves 与 cell-type heterogeneity。

技术验证和生物学发现是递进关系；不能只凭图 3/4 而忽略图 1/2 对 barcode 与 cluster 可靠性的支撑。

### 11. 当前工作区代码为什么不能作为 MUSIC 证据

目录中的 `preprocess_merge.R`、`filter_cluster.R`、`pseudotime.R`、`abcmax.R` 等来自另一套 10x RNA+ATAC postnatal brain 项目。它们处理 WNN、Monocle3、ABC-Max、GWAS、Hotspot/SCENIC，不包含：

- MUSIC linker/barcode decoding；
- UMNDBC read filtering；
- DD/RR/RD cluster 构建；
- multiplex contact projection；
- $P_c(s)$ 或 LCS-erosion；
- MUSIC eQTL contact；
- XIST RAL/XAL。

因此 code-paper match 必须标为 **Not matched**。这不是“部分复现”，而是不同论文/项目被放进同一工作区。后续若获取 MUSIC 官方代码，应另行记录来源并重新建立 code map。

### 12. 证据入口与边界

- Primary source: `paper_snMultiome.pdf`
- PDF-derived text used for audit: local temporary extraction, not a durable source file
- Main figure evidence: PDF pages 2–7
- Local scripts: mismatched external project; do not cite for MUSIC claims

最主要限制是缺少 MUSIC 官方代码和本地 raw/processed data。当前工作区能够支持论文解释与图证据审计，不能支持计算复跑。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary — Single-cell multiplex chromatin and RNA interactions in ageing human brain

**Paper**: Wen et al., *Nature* 628, 648–656 (2024)

**DOI**: 10.1038/s41586-024-07239-w

**Method**: MUSIC, multinucleic acid interaction mapping in single cells

### Main contribution

MUSIC jointly measures, from the same nucleus, gene expression, multiplex DNA–DNA contacts, and RNA–chromatin associations. Molecules first receive RNA- or DNA-specific linkers and a split-and-pool cell barcode; molecules remaining in the same physical complex then receive a shared 10x+I7 complex barcode. Reads sharing cell and complex identity can therefore be grouped into DNA-only, RNA-only, or RNA–DNA clusters, including complexes with more than two molecules.

The method was validated in mixed human H1 and mouse E14 embryonic stem cells, then applied to 14 post-mortem human frontal cortices from donors aged 59 years or older. RNA profiles resolved excitatory and inhibitory neurons, astrocytes, oligodendrocytes, oligodendrocyte precursors, microglia, and vascular cells.

### Main findings

- Ensemble MUSIC DNA contacts recapitulate Micro-C A/B compartments and TAD-scale patterns; clusters with three or more DNA reads recover structures missed by pairwise-only clusters.
- Single cells vary in the genomic-distance decay of contact probability $P_c(s)$. The paper summarizes loss of short-range contacts with an LCS-erosion score.
- LCS-eroded cells have older transcriptomic-age signatures across cell types and are enriched in high-Alzheimer-pathology specimens for several cortical cell types.
- Cell types containing a cis-eQTL–promoter DNA contact tend to be the cell types in which the eQTL affects its target gene, supporting contact-based cell-type specificity.
- Female cortical cells vary strongly in XIST–chromosome-X association level. Higher XIST association corresponds to larger structural differences between XIST-associated and unassociated X chromatin, especially in excitatory neurons.

### Evidence boundaries

The ageing and Alzheimer results are cross-sectional correlations in post-mortem samples, not longitudinal clocks or causal tests. The XIST analysis is limited by sparse single-cell RNA–DNA contacts and thresholding. The local R/ATAC/ABC-Max scripts belong to a different postnatal snMultiome project and do not implement MUSIC; code-paper fidelity is therefore **Not matched**.

### Reproducibility

The PDF provides detailed experimental and computational methods plus accession information in online content, but the current workspace lacks the MUSIC processing repository and raw data. The paper can be interpreted and its figures audited locally, but its analysis cannot be rerun with the code currently stored here.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
