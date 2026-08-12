---
layout: default
permalink: /paper-atlas/molecular-asynchrony-of-single-cells-c1c23e86/
title: "Molecular_asynchrony_of_single_cells"
nav: false
description: "本文提出的核心不是一个普通的多组学整合流程，而是把 RNA、染色质开放性和组蛋白修饰之间的“不同步”当作动力学信号来使用。论文认为，传统单细胞分析常把多模态特征投射到同一个静态空间，但细胞状态变化本来就包含调控层级之间的时间延迟；这种延迟可以用来估计单细胞的热力学性质和未来状态倾向 。 作者关心的是：在静态采样的单细胞数据里，怎样判断某个细胞只是处在稳定状态，还是正在经历状态转换？伪时间方法能给出轨迹顺序，但不直接解释驱动力；"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>Molecular_asynchrony_of_single_cells</h1>
    <p>The molecular asynchrony of single cells</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2026.06.02.729594" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法中文解读：单细胞分子异步性

本文提出的核心不是一个普通的多组学整合流程，而是把 RNA、染色质开放性和组蛋白修饰之间的“不同步”当作动力学信号来使用。论文认为，传统单细胞分析常把多模态特征投射到同一个静态空间，但细胞状态变化本来就包含调控层级之间的时间延迟；这种延迟可以用来估计单细胞的热力学性质和未来状态倾向 (paper.md:12, paper.md:21)。

### 论文要解决什么问题

作者关心的是：在静态采样的单细胞数据里，怎样判断某个细胞只是处在稳定状态，还是正在经历状态转换？伪时间方法能给出轨迹顺序，但不直接解释驱动力；RNA velocity 依赖较快的 mRNA 动力学；optimal transport 需要密集时间采样；SCENIC 和 Chromatin Potential 等调控框架能提供机制信息，但对混合细胞群中连续热力学状态的刻画仍有限 (paper.md:21)。本文的策略是直接测量同一细胞内的转录组、染色质开放性和组蛋白修饰，再用这些层级之间的错位估计细胞动力学。

### SeqTag 提供什么数据

SeqTag 是本文的实验基础。它在同一单细胞或单核中同时测量三类信息：RNA-seq、ATAC-seq 和 CUT&Tag 组蛋白修饰。流程上先做抗体靶向的 pA-Tn5 tagmentation 捕获组蛋白标记，再做 Tn5 开放染色质 tagmentation，随后进行反转录、组合索引、DNA/cDNA 分离和测序文库扩增 (paper.md:47, paper.md:184)。Figure 1 的本地图像显示了这一湿实验流程、同一批细胞在 RNA/ATAC/H3K27me3 空间中的嵌入，以及由 H3K27ac-ATAC 异步性得到的 priming-energy 地形图 (figure_01.jpg, paper.md:39)。

数据处理上，论文用 Read 2 的位置识别细胞 barcode 和模态标识，barcode 通过 bowtie 比对到参考，reads 经过接头和 poly-dT 修剪、质量过滤后，RNA 用 STAR 比对，DNA 用 bowtie2 比对，并按位置、UMI、细胞 barcode 和子文库索引去重复 (paper.md:235, paper.md:241)。随后用 scanpy 做 RNA 聚类、snapATAC2 做 DNA fragment 嵌入、MACS3 做 peak calling、SnapATAC2 预测 gene-cCRE 关系、HOMER/DAVID 做 motif 和 GO 分析、liftOver 加 LDSC 做 GWAS 富集 (paper.md:247, paper.md:253, paper.md:259, paper.md:271)。

### 分子异步性的计算流程

```text
同一细胞的 RNA + ATAC + CUT&Tag
        |
        v
RNA PCA 作为 reference community space
        |
        v
在各模态中找 kNN，并把表观组邻居投射回 RNA 或 ATAC 坐标
        |
        v
比较 leading layer 与 lagging layer 的局部几何错位
        |
        v
得到三个量：
  Priming Energy
  Epigenetic Remodeling Rate
  Regulatory Entropy
```

作者把 RNA PCA 空间定义为当前已实现的表型状态，因为所有细胞都有同一实验流程测得的 RNA；ATAC 和 CUT&Tag 则代表可能早于转录变化的“张力状态” (paper.md:280)。对每个细胞，方法在不同模态中寻找 k 近邻，把表观组邻居投射到 RNA 空间，计算局部质心和位移向量。直观地说，如果 ATAC 邻域已经指向未来状态，而 CUT&Tag 或 RNA 还没有完全同步，这个几何错位就提供了动力学信息。

### 三个核心量

**Priming Energy。** 这是对“表观遗传预加载能量”的估计。论文用 Hooke 定律类比：ATAC 相对 CUT&Tag 领先的未实现距离形成 potential gap；如果 lagging modality 没有移动，耦合刚度为零；耦合强度随有效 priming distance 的比例缩放 (paper.md:283)。在结果中，OPC 到 ODC 轨迹显示最高 priming energy，提示这些细胞正在经历状态转换 (paper.md:70)。

**Epigenetic Remodeling Rate。** 这是 lagging histone-mark layer 追上 leading ATAC state 的距离估计。方法把 CUT&Tag 空间中的近邻投射到 ATAC spectral embedding 中，计算与 query cell 的欧氏距离，再做 per-cell min-max normalization，并检测距离分布是否双峰；如果双峰成立，两个峰分别代表 lagging 和 leading states，峰间距就是下一单位时间内 CUT&Tag 需要追上的距离 (paper.md:295, paper.md:298)。Figure 3A-B 的本地图像直观展示了这种距离分布和 per-cell distance heatmap (figure_05.jpg, paper.md:107)。

**Regulatory Entropy。** 这是单细胞状态可塑性的度量。方法把表观组邻居投射后的坐标做均值中心化，用 SVD 投射到第一主成分，再用 Gaussian KDE 估计连续概率密度，最后计算 Shannon entropy (paper.md:289)。高熵表示邻域在 RNA 状态空间中分布更宽，细胞可能探索更多替代表型；低熵表示邻域更集中、细胞身份更稳定 (paper.md:129)。

### 生物学应用

在成年小鼠大脑皮层中，作者获得 450,031 个 multiomics cells，并注释为 8 个一级细胞类和 34 个二级 subclass，同时识别 317,517 个候选 cis-regulatory elements 并用 NMF 分成 37 个模块 (paper.md:56, paper.md:59)。

第一个重点案例是少突胶质细胞发生。作者对 OPC-to-ODC 细胞做 diffusion pseudotime 分析，发现细胞从 OPC 走向成熟 ODC 时 priming energy 快速下降，说明活性和抑制性染色质重塑整体耦合但不同步 (paper.md:76)。他们进一步把 immature cells 分为 primed 和 ground-state，发现 primed cells 有更高比例的 bivalent cCREs；成熟过程中一部分 bivalent cCREs 去甲基化而激活，一部分失去 H3K27ac 而变成抑制状态，还有一部分保持双价标记 (paper.md:89)。Figure 2 和 Figure S2 显示了这条轨迹、双价 cCRE 分组和顺序重塑模型 (figure_03.jpg, figure_04.jpg)。

第二个重点是衰老。作者用 remodeling rate 比较 H3K27ac 和 H3K27me3 在 ODC maturation 中的追赶速度，发现 aged early-committed cells 中 H3K27me3 变化异常增强，并且与重塑速率相关的 cCRE 在 COP 高甲基化区域和 astrocyte-specific H3K27ac 区域中富集 (paper.md:104, paper.md:107)。随后，H3K27me3 erosion 与 DNA damage hotspots 和 OPC fate drift 联系起来；强制 OPC-to-astrocyte 方向的模拟显示，年轻 OPC 有较高 barrier，而 aged cells 的 barrier 降低，可能使命运选择偏向 astrocyte-like 方向 (paper.md:118)。

第三个重点是细胞身份丢失和疾病风险。作者用 regulatory entropy 评估不同细胞类型的身份下降速率，报告 inhibitory neurons 和 vascular cells 更易受影响，astrocytes 更抗衰老；高熵细胞比例随年龄增加，主要由 ATAC 和 H3K27me3 drift 驱动，而 H3K27ac 影响较小 (paper.md:129)。他们还把 mouse entropy-driving cCREs liftOver 到 human orthologous regions，并做 GWAS trait enrichment，提出 VLMC-insomnia、L6 IT neuron-Alzheimer's disease 等细胞类型特异的疾病关联例子 (paper.md:145)。Figure 4 和 Figure S4 显示了 regulatory entropy 示意图、高熵细胞比例、H3K27me3/accessibility 变化和 GWAS 富集图 (figure_07.jpg, figure_08.jpg)。

### 如何理解贡献与限制

本文贡献可以拆成两层：SeqTag 提供同一细胞中 RNA、ATAC 和 histone mark 的共同测量；分子异步性分析把这些层级之间的局部几何错位转化为 priming、remodeling 和 entropy 三类动力学摘要。它不是一个需要训练的大模型，而是基于 kNN 投影、局部质心、位移向量、KDE 熵、双峰距离和回归/富集分析的几何统计框架。

需要注意三点限制。第一，论文自己的限制部分承认单细胞表观组数据存在稀疏性和 allelic dropout，kNN centroid projection 只能缓解，不能完全解决；priming energy 依赖区域聚合信号，不是单个位点动力学 (paper.md:157)。第二，推断来自静态 population snapshot，依赖 Waddington landscape 的 ergodic continuity 假设，急性灾难性事件可能超出模型适用范围 (paper.md:157)。第三，本工作区没有可验证代码：论文称 customized code 在 `https://github.com/czhulab/asynchrony`，但 acquisition 时该仓库不可公开获取/返回 404，因此这里不能验证代码实现、默认参数、运行脚本或 paper-code fidelity (paper.md:307)。

另外，`paper.md` 中公式转换有损：`paper.md:277-298` 保留了变量角色和计算步骤叙述，但完整 display equations 没有可靠恢复。因此本中文解释只保守说明可见的操作定义，不重构缺失公式。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## The molecular asynchrony of single cells

### Overview

This bioRxiv 2026 preprint introduces SeqTag, a same-cell tri-modal assay for RNA-seq, ATAC-seq, and CUT&Tag, plus a computational framework called molecular asynchrony for estimating single-cell kinetic properties from temporal lags between molecular layers (paper.md:12, paper.md:27). The key idea is that chromatin accessibility and histone marks can act as leading or lagging coordinates relative to the current RNA state, so their mismatch is treated as informative signal rather than integration noise (paper.md:24, paper.md:151).

### Why Existing Methods Are Not Enough

The paper contrasts molecular asynchrony with pseudotime, RNA velocity, optimal transport, and causal regulatory methods such as SCENIC and Chromatin Potential. Pseudotime orders cells along similarity trajectories but lacks a thermodynamic explanation of driving forces; RNA velocity depends on fast mRNA kinetics; optimal transport needs dense time sampling; and regulatory frameworks are useful but still struggle with mixed populations spanning a continuum of thermodynamic states (paper.md:21). The authors' answer is to exploit the disequilibrium between regulatory layers, especially the fact that chromatin accessibility can precede or coincide with histone-mark changes (paper.md:24).

### Method in One Pass

SeqTag first generates same-cell RNA, ATAC, and histone-mark profiles. The computational analysis maps RNA to a reference community space, projects epigenomic nearest neighbors into that space, and computes cross-modality displacement vectors. From these local neighbor geometries, the paper defines Priming Energy, Epigenetic Remodeling Rate, and Regulatory Entropy (paper.md:36, paper.md:277). Operationally, Priming Energy measures aligned epigenetic tension, Remodeling Rate measures lagging-to-leading catch-up distance in ATAC space, and Regulatory Entropy measures how broadly a cell's epigenomic neighborhood spreads across possible RNA states (paper.md:283, paper.md:289, paper.md:295).

### Main Results

The authors apply SeqTag to aging mouse cerebral cortex and report 450,031 multiomics cells across H3K27ac and H3K27me3 experiments, with 8 primary cell classes, 34 subclasses, 317,517 cCREs, and 37 cCRE modules (paper.md:56, paper.md:59). Figure 1 and Figure S1 visually support the assay, atlas, and priming landscape with same-cell embeddings, validation plots, and cCRE/motif modules (figure_01.jpg, figure_02.jpg).

In oligodendrogenesis, Priming Energy separates OPC-to-ODC transition states and supports a model in which chromatin accessibility leads, H3K27me3 catches up, H3K27ac briefly lags, and bivalent cCREs resolve into activated, repressed, retained, or lost states (paper.md:70, paper.md:76, paper.md:89, paper.md:98). Figures 2 and S2 visibly show the pseudotime trajectory, priming-energy curves, bivalency fractions, gene-linked outcomes, and sequential remodeling model (figure_03.jpg, figure_04.jpg).

For aging, the paper reports that H3K27me3 remodeling becomes decoupled in aged OPCs, H3K27me3 erosion is linked to DNA-damage hotspots, and forced OPC-to-astrocyte analysis suggests that aging lowers the barrier protecting OPC fate (paper.md:104, paper.md:118). Figure 3 and Figure S3 show the remodeling-rate schematic, distance heatmaps, cCRE-rate associations, H3K27me3 changed regions, and forced-transition landscape (figure_05.jpg, figure_06.jpg).

For broader identity erosion, Regulatory Entropy increases in a cell-type-specific way, with inhibitory neurons and vascular cells described as more susceptible and astrocytes as relatively resistant. Entropy-driving cCREs are lifted to human orthologous regions and tested against GWAS traits, yielding examples such as VLMC-insomnia and L6 IT neuron-Alzheimer's disease associations (paper.md:129, paper.md:145). Figures 4 and S4 show the entropy schematic, high-entropy fractions, H3K27me3/accessibility changes, subclass signature heatmaps, and GWAS enrichment plots (figure_07.jpg, figure_08.jpg).

### Reproducibility and Gaps

Raw and processed data are stated to be available from GEO accession `GSE333552` (paper.md:301). The paper states that customized code is available at `https://github.com/czhulab/asynchrony`, but acquisition for this workspace found the repository unavailable/404 and no public clone was retrieved; therefore this analysis is paper-only and does not verify implementation details, runnable scripts, parameter defaults, or code-paper fidelity (paper.md:307).

The converted markdown also degrades the display equations in the Methods derivation. The operational roles of community-space projection, Priming Energy, Regulatory Entropy, and Remodeling Rate are visible in `paper.md:277-298`, but exact algebra is `Not found` in the converted source. The paper itself notes additional limitations: single-cell epigenomic sparsity and allelic dropout, aggregation across regions rather than single-locus kinetics, and reliance on an ergodic-continuity assumption from static population snapshots (paper.md:157).

### Bottom Line

The contribution is a combined measurement-and-analysis framework: SeqTag makes the relevant molecular layers observable in the same cells, and molecular asynchrony converts their local geometric mismatch into thermodynamic summaries of priming, remodeling, and entropy. The biological demonstrations are broad and visually supported by the local figures, but full computational reproducibility remains blocked until the cited custom code repository becomes publicly available or an archived snapshot is supplied.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
