---
layout: default
permalink: /paper-atlas/systematic-scrnaseq-screens-neural-organoid-morphogens-26a52b0d/
title: "Systematic_scRNAseq_screens_neural_organoid_morphogens"
nav: false
description: "本文解析论文 Systematic scRNA-seq screens profile neural organoid response to morphogens（Nature Methods, 2026；DOI：10.1038/s41592-025-02927-5）。"
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
      <span>Perturbation Resources</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>Systematic_scRNAseq_screens_neural_organoid_morphogens</h1>
    <p>Systematic scRNA-seq screens profile neural organoid response to morphogens</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/quadbio/organoid_patterning_screen" target="_blank" rel="noopener noreferrer" aria-label="Open code for Systematic_scRNAseq_screens_neural_organoid_morphogens">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 系统性单细胞筛选如何解析神经类器官对形态发生因子的响应

本文解析论文 **Systematic scRNA-seq screens profile neural organoid response to morphogens**（*Nature Methods*, 2026；DOI：`10.1038/s41592-025-02927-5`）。它不是提出一个单独的预测模型，而是把“如何给神经类器官做区域化诱导”改写成一个可系统比较的扰动筛选问题：同时改变形态发生因子的种类、加入时间、浓度、组合、细胞系、神经诱导培养基和空间给药方式，再用多重化单细胞 RNA 测序统一读取早期命运结果。

### 1. 论文要解决什么问题

神经类器官区域化依赖 WNT、SHH、FGF、RA 和 BMP 等信号在时间与空间上的组合，但传统方案往往只优化少量条件，数月后再检测少数标志基因。因此，不同实验室即使都声称获得“前脑”“中脑”或“视网膜”类器官，也可能因为细胞系、培养基、给药窗口和组织结构不同而产生不同细胞组成。

已有工作分别解决了局部问题。例如，Cederquist 等在 *Nature Biotechnology*（2019）用可诱导组织者赋予前脑类器官位置身份；Karzbrun 等在 *Nature*（2021）用几何约束重建人神经管形态发生；Jo 等在 *Cell Stem Cell*（2016）等区域特异性方案生成了中脑样类器官；He 等在 *Nature*（2024）建立了人神经类器官整合转录组图谱。这些工作奠定了区域化、组织几何和参考图谱的基础，但并没有在同一实验框架内系统回答以下问题：

- 同一种因子在不同加入时间和浓度下是否产生同一方向的效应？
- 两种因子的组合是相加、由一方主导，还是出现非加性结果？
- 一个条件在不同 hPS 细胞系、不同神经诱导方法和不同批次中能否复现？
- 连续空间梯度与多孔板中的离散剂量，是否会产生相同的背腹轴命运分布？

这篇论文的核心贡献因此是一个“设计—测量—比较”框架，而不是一个万能的区域化配方。

### 2. 三个相互补充的实验层级

#### 2.1 形态发生条件筛选

作者在 96 孔板中培养神经类器官，改变 CHIR99021、XAV939、SHH、purmorphamine、cyclopamine、FGF8、RA、BMP4 和 BMP7 的加入时间、浓度与组合。第 21 天将同条件多个类器官合并、解离、进行 cell hashing，再做 10x 3′ scRNA-seq。主筛选覆盖 3 个 hPS 细胞系、97 个处理条件和 100,538 个细胞。补充图 1 给出了处理矩阵和每个条件实际检测的类器官数量，补充图 2 则保留了全部条件的明场形态，因此单细胞组成变化可以与培养状态共同理解。

#### 2.2 模式化可重复性筛选

作者选择 12 个代表性处理，在 H1、H9、WTC 和 WIBJ2 四个细胞系、MNIM 与 dual SMAD 两种神经诱导方法、两个技术批次中重复。完整设计包含 192 个样本、576 个类器官和 209,902 个细胞。这里的目标不是寻找“平均最优”条件，而是拆分处理、细胞系、培养基和批次各自对结果的贡献。

#### 2.3 连续梯度与离散剂量比较

MiSTR 微流控系统在组织两侧持续输入基础培养基与腹侧化培养基，形成连续梯度；多孔板类器官则接受 A–E 五个离散剂量。两类系统都以多重化 scRNA-seq 读取背腹前脑身份，从而把“信号剂量”与“信号如何穿过组织”分开比较。

### 3. 输入、输出与总体流程

**输入**包括 hPS 细胞系、神经诱导背景、形态发生因子及其时间/浓度/组合、单细胞表达矩阵与 hashtag 计数、发育中人脑和类器官参考图谱，以及 pySCENIC 所需的转录因子列表和 motif 数据库。

**输出**包括每个条件的细胞类型组成、富集/耗竭分数、前后轴（AP）和背腹轴（DV）位置、调控子活性、形态发生因子—调控子关联、组合的非加性分数、跨批次/细胞系/培养基的距离，以及连续和离散梯度的命运分布差异。

```text
形态发生因子设计
（种类 × 时间 × 浓度 × 组合 × 细胞系 × 培养基）
                         │
                         ▼
第 21 天类器官 → 合并/解离 → cell hashing → 多重化 scRNA-seq
                         │
                         ▼
去卷积与质控 → 归一化 → RSS/CSS/PCA/UMAP → 聚类与细胞类型注释
                         │
          ┌──────────────┼──────────────────┐
          ▼              ▼                  ▼
   组成富集/耗竭      参考图谱映射        pySCENIC / AUCell
   Shannon 多样性     AP/DV 轴评分        形态发生因子→调控子
          │              │                  │
          └──────────────┼──────────────────┘
                         ▼
     MMD / E-distance / KLD / NNLS 残差与跨背景比较
                         │
                         ▼
         条件效应、非加性、可重复性和梯度响应结论
```

### 4. 计算分析逐步拆解

#### 4.1 去卷积、质控与共同表示

10x 数据经 Cell Ranger 处理，hashtag 经 CITE-seq-Count 和 `HTODemux` 分配；混合细胞系还使用 demuxlet 或 cellsnp-lite/vireo 做基因型去卷积。主 Seurat 流程去除检测基因少于 1,000 或线粒体比例不低于 10% 的细胞，并进行 log normalization/`ScaleData` 或 SCTransform。可重复性筛选在 Scanpy 中使用 750–20,000 UMI、线粒体比例低于 10%、总计数归一化到 10,000、对数变换和高变基因选择。

随后，作者用早期人脑参考构建 RSS/CSS 表示，并结合 UMAP、聚类、标志基因和参考映射完成注释。这里的关键不是让所有条件在 UMAP 上“混合得越好越好”，而是在保留处理差异的同时，把具有相似发育身份的细胞放到可比较空间中。

#### 4.2 细胞组成富集分数

每个处理条件在同一细胞系内与匹配对照做双侧 Fisher 精确检验，Bonferroni 校正后若 $P_{adj}<0.01$，定义细胞簇 $k$ 在条件 $c$ 下的富集分数为：

$$
E_{c,k}=\log_2\!\left(\mathrm{odds\ ratio}_{c,k}\right).
$$

不显著的结果设为 0，绘图时截断到 $[-5,5]$。因此，$E_{c,k}$ 表示某类细胞相对对照的富集或耗竭，而不是绝对生成速率，也不能直接区分分化、增殖或存活造成的变化。论文提到的 `Morphogen_Screen_Enrichment.R` 在固定代码快照中 `Not found`；仓库只保留了相关的可重复性筛选富集 notebook。

#### 4.3 参考图谱映射与 AP/DV 轴

作者用 scArches 将类器官数据映射到发育中人脑的 scANVI 模型，并用 scPoli/HNOCA 模型映射到人神经类器官图谱。AP 模型以原代放射状胶质细胞的端脑、间脑、中脑和后脑标签为目标，在 scANVI 潜在表示上训练 elastic net；DV 模型先计算背侧与腹侧标志模块，再用高绝对分值细胞训练二项 elastic net。

在前脑内部，还可以把背侧模块分数和腹侧模块分数相减：

$$
\mathrm{DV\_score}_i=S_i^{\mathrm{dorsal}}-S_i^{\mathrm{ventral}}.
$$

这些分数是相对发育身份坐标，不是组织中的物理位置，也不是细胞实际接收到的形态发生因子浓度。

#### 4.4 从表达矩阵到调控子活性

主筛选在 38,504 个 HES3 细胞上运行 pySCENIC v0.12.1：GRNBoost2 先推断 TF—基因邻接，motif pruning 将共表达模块收缩为 regulon，AUCell 再为每个细胞计算 regulon 活性。论文得到 413 个 regulon，平均 141 个基因。

代码中的 `scenic_runs/src/pyscenic_utils.py:127-281` 直接实现了这条链：GRNBoost2 → module discovery → motif enrichment → regulon → AUCell，并保存每次 seed 的中间结果。可重复性筛选则对每个细胞系各运行 100 次、对四条线合并数据再运行 100 次，共汇总 500 次运行，得到 136 个共识 regulon；`consensus_regulons.py:52-246` 实现 TF—基因出现次数、平均权重、阈值筛选和共识 regulon 构建。

#### 4.5 把形态发生因子连接到调控子

作者把 morphogen、时间、培养基及交互变量加入 AUCell 活性矩阵，再让 GRNBoost2 把这些变量当作预测因子、regulon 当作目标。`grnboost_analysis.py:68-242` 直接展示了编码、log/min–max 归一化、按共同细胞对齐、把变量附加到 AUCell 矩阵以及运行 GRNBoost2 的过程。

必须区分两种量：

1. GRNBoost2 的 `importance` 表示预测关联强度；
2. 论文另行计算 timing 和 concentration 与 regulon AUC 的有符号 Pearson 相关。

固定快照中的 `correlation_analysis.py:16-51` 只是把 `importance` 复制到名为 `correlation` 的列，并没有计算 Pearson $r$。因此，论文图 2、图 5 中相关方向和正负号应以论文及其发布分析 notebook 为准，不能由该 helper 复现。这是当前代码—论文对应中最重要的已确认差异。

#### 4.6 组合效应：主导性与非加性不是同一件事

作者先在 RSS 的 20 维 PCA 空间中用 MMD 比较单因子与组合条件。若组合更靠近单因子 A 而远离 B，说明 A 对最终表型更“主导”。

非加性则用另一套几何检验。把对照质心平移到原点，用两个单因子质心的非负线性组合拟合组合条件质心：

$$
R_{A,B}=\left\|\mu_{A+B}-(\alpha\mu_A+\beta\mu_B)\right\|_2,
\qquad \alpha,\beta\ge 0.
$$

残差 $R_{A,B}$ 越大，组合越偏离相加模型。它说明表型空间中的非加性，但不能单独证明分子通路之间存在直接协同。NNLS 分析在仓库中为 notebook-only，未找到独立可复用脚本。

#### 4.7 可重复性距离

论文用三类量衡量样本间差异：Kullback–Leibler divergence 比较细胞类型比例；MMD 和 energy distance 比较 RSS-PCA 空间中的细胞分布。三者都是值越低表示越相似。`05_01_distances_morph.py:8-33` 与 `05_02_distances_reproducib.py:9-35` 直接实现 20 维 RSS-PCA 上的 MMD/E-distance；KLD 计算主要保留在绘图 notebook 中。

这类距离回答“两个样本有多不同”，但不解释差异来自细胞命运转换、选择性死亡、增殖还是技术采样。因此它们适合做条件稳定性比较，不等价于机制模型。

#### 4.8 连续与离散梯度

MiSTR 中的细胞身份沿 A–E 位置逐渐变化；多孔板类器官覆盖相似的 DV 前脑身份，却表现出更强、更阈值化的腹侧化。图 6 的 HCR 和 NKX2.1-GFP 时间序列显示腹侧标志先局部出现、随后在类器官中扩展。这支持组织内部存在传播或正反馈过程，但论文没有识别其具体分子媒介。

### 5. 如何理解主要结果

- **时间与浓度是两个独立控制轴。** 低浓度、晚期 RA 更偏向视网膜；高浓度 RA 更偏向后脑和后部底板。持续提高 SHH 则使前脑身份由端脑逐步移向下丘脑/腹侧命运。
- **组合效应依赖上下文。** XAV939–SHH、RA–SHH/FGF8 等组合在不同细胞系中可能表现为主导、近似相加或明显非加性，不能从单因子结果简单外推。
- **培养背景与细胞系是方法的一部分。** dual SMAD 通常产生更多 CNS/神经元身份，但跨细胞系变异更高；MNIM 产生更广的神经与非神经身份，且不少条件更稳定。
- **剂量模式会改变组织响应。** 连续梯度与离散剂量不是同一刺激的等价实现，组织几何会把相似的外源信号转化成不同的命运分布。
- **网络关联不等于因果。** GRNBoost2 权重、Pearson 相关、MMD 和 NNLS 残差都是统计或几何关联，不能独立证明某个 regulon 是形态发生因子效应的直接因果中介。

### 6. 代码复现边界

官方代码仓库为 `quadbio/organoid_patterning_screen`，本地固定在提交 `971063baf391e5b7b5897c4a3f3a58c02459f489`。总体代码—论文一致性为 **medium**：pySCENIC、共识 regulon、morphogen-GRNBoost2 和 MMD/E-distance 有直接源码支持；大量图形分析依赖 notebook 和外部大数据/参考模型，不能一键重现。

当前明确缺失或不完整的部分包括：`Morphogen_Screen_Enrichment.R` `Not found`；论文 Pearson 相关没有独立可复用实现；KLD 和 NNLS 主要为 notebook-only；主筛选完整预处理、HCR 图像量化与长期 light-sheet 处理脚本 `Not found`。这些缺口不否定论文结果，但决定了哪些结论可以由固定代码快照直接复算。

### 7. 方法的适用范围与局限

该框架最适合回答早期（第 21 天）区域化条件如何改变单细胞组成和调控状态。它不能完整捕捉空间组织、形态、长期成熟与命运稳定性；多个类器官合并后，也无法在所有实验中逐个估计类器官间变异。参考映射依赖参考图谱覆盖范围，日后新增人脑区域或发育阶段可能改变标签解释。

最重要的学习结论是：形态发生因子不是一个可脱离背景解释的“旋钮”。一个条件的结果由 **何时加入、加入多少、与谁组合、用哪条细胞系、采用何种诱导培养基、信号如何穿过组织** 共同决定。论文的价值正是把这些变量放入同一单细胞比较框架，并明确展示哪些规律稳定、哪些规律只在特定实验背景中成立。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Systematic scRNA-seq screens profile neural organoid response to morphogens

### Overview

This Nature Methods study converts neural-organoid protocol optimization into a systematic perturbation screen. Instead of testing a few marker genes after months of culture, it varies morphogen identity, timing, concentration and combinations, then measures day-21 cell composition with multiplexed scRNA-seq. The resource includes a 97-condition screen with 100,538 cells and a separate reproducibility screen spanning four hPS cell lines, two neural induction methods, two batches, 192 samples, 576 organoids and 209,902 cells.

### Why this matters

Regionalized organoid protocols are difficult to compare because studies use different lines, media, schedules and endpoints. Early morphogen competence windows are particularly under-characterized. The paper provides a common single-cell readout for WNT, SHH, FGF8, RA and BMP pathway perturbations, exposes which effects generalize, and shows where line, medium or tissue architecture changes the outcome.

### Approach

Organoids were treated with short pulses, extended concentration series and selected combinations, pooled with cell hashing and profiled at day 21. Cells were QC-filtered, normalized, embedded with RSS/CSS and mapped to developing-brain and organoid reference atlases. Treatment effects were summarized with cell-composition enrichment scores, AP/DV axis scores, MMD/E-distance/KLD reproducibility metrics and NNLS residuals for non-additive combinations.

For gene-regulatory analysis, pySCENIC inferred regulons and AUCell activity. GRNBoost2 then linked morphogen/timing/interaction variables to regulon activities. The reproducibility screen used repeated pySCENIC runs to build consensus regulons before comparing responses across lines and induction methods.

### Main findings

- Timing and concentration are independent control axes. Low and high RA or SHH exposures produce different regional identities rather than a simple increase in one fate.
- Morphogen combinations can be non-additive and cell-line dependent. XAV939–SHH and RA–SHH/FGF8 combinations illustrate synergy or dominance in composition/regulon space.
- Neural induction background strongly shapes response. Dual SMAD inhibition yields more CNS/neuronal identities but generally greater variability; MNIM produces broader neural and non-neural outcomes and often better cross-line reproducibility.
- Cell-line effects are real but not reducible to hES versus hiPS origin or XX versus XY karyotype.
- Continuous MiSTR gradients and discrete organoid doses generate related DV forebrain identities, but MiSTR changes are more gradual and organoids show threshold-like, stronger ventralization with locally spreading NKX2.1 activation.

### Evidence and limitations

The six main figures and ten extended-data figures support the screen coverage, dose/timing effects, interaction analysis, reproducibility design and gradient comparison. HCR and live imaging provide orthogonal validation for selected regional markers. The study remains a day-21 transcriptomic snapshot: it does not fully capture spatial organization, morphology, later maturation or longitudinal fate stability. GRNBoost2 and NNLS identify predictive association/non-additivity, not causal molecular mechanisms.

### Reproducibility and paper–code match

Overall code fidelity is **medium**. The official repository contains reusable pySCENIC, consensus-regulon, morphogen-network and MMD/E-distance code plus many analysis notebooks. It does not provide a one-command reproduction. Large inputs and reference resources are external, several figure analyses are notebook-only, and the specifically named enrichment R script is absent.

A material discrepancy is documented: the paper reports signed Pearson correlations between regulon activity and timing/concentration, while the reusable `correlation_analysis.py` helper substitutes GRNBoost importance for correlation. Paper claims involving Pearson directionality therefore rely on the publication analysis/notebooks, not that helper.

### Code and data availability

- Official code: `https://github.com/quadbio/organoid_patterning_screen`, pinned locally at commit `971063baf391e5b7b5897c4a3f3a58c02459f489`.
- ArrayExpress: `E-MTAB-15622` and `E-MTAB-15667`.
- Zenodo: `10.5281/zenodo.17225179`; metadata and two demultiplexing VCFs are local, while the declared 22.8-GB processed archive remains referenced externally.
- Nature supplementary files MOESM1–MOESM13 are retained locally.

### Bottom line

The paper is best viewed as both a developmental resource and a design-of-experiments lesson: morphogen response is conditional on when, how much, with what partner, in which line, under which induction method and in what tissue geometry the signal is delivered. Its strongest contribution is the joint single-cell measurement of those variables, not a universal deterministic recipe for one regional organoid fate.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
