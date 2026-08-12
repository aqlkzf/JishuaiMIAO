---
layout: default
permalink: /paper-atlas/spatiotemporalmultiomics-aging-review-62a8aa29/
title: "SpatiotemporalMultiomics_Aging_Review"
nav: false
description: "这是一篇综述，不是一篇提出单一算法或新平台的原始研究。它真正有用的地方，是把转录组、蛋白组、代谢组和表观基因组放进同一个判断框架：一个实验中的“时间”，究竟来自不同时间点的破坏性取样，还是来自对分子进行标记并追踪其命运？ 单细胞测序可以区分细胞类型，却通常要把组织解离，因而丢掉邻域和形态。空间组学保留位置，但一张切片只是一个静态瞬间。连续活细胞成像有真正的时间轴，却难以同时观察大量不同 RNA、蛋白或代谢物。"
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
      <span>Technology Platforms</span>
      <span>Military Medical Research · 2024</span>
    </div>
    <h1>SpatiotemporalMultiomics_Aging_Review</h1>
    <p>Spatiotemporal multi-omics: exploring molecular landscapes in aging and regenerative medicine</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1186/s40779-024-00537-4" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 时空多组学：先分清“时间”从哪里来

这是一篇综述，不是一篇提出单一算法或新平台的原始研究。它真正有用的地方，是把转录组、蛋白组、代谢组和表观基因组放进同一个判断框架：一个实验中的“时间”，究竟来自不同时间点的破坏性取样，还是来自对分子进行标记并追踪其命运？

### 1. 为什么空间和时间不能互相替代

单细胞测序可以区分细胞类型，却通常要把组织解离，因而丢掉邻域和形态。空间组学保留位置，但一张切片只是一个静态瞬间。连续活细胞成像有真正的时间轴，却难以同时观察大量不同 RNA、蛋白或代谢物。

所以“时空多组学”至少要回答三个不同问题：

1. 某个分子或细胞状态在哪里？
2. 不同阶段的空间分布怎样变化？
3. 同一个分子、细胞或谱系是否真的被连续追踪？

前两个问题可以靠连续取样回答；第三个问题需要标记、谱系追踪或实时成像。论文把这一区别概括为 pseudo-temporal 与 authentic spatiotemporal。

### 2. 伪时间：把不同样本排成一条变化轴

设第 $t$ 个阶段得到组学矩阵 $X_t$ 和空间坐标 $S_t$：

$$
D_t=\{X_t,S_t\},\qquad t=t_1,\ldots,t_K.
$$

研究者分别测量年轻/老年、损伤后 0/6/12 小时或 1/3/7 天的切片，再对齐组织区域、聚类细胞状态并比较表达。算法还可以给每个位置一个推断轨迹坐标：

$$
\hat z_i=f(X_i,S_i,t_i).
$$

$\hat z_i$ 是模型推断的顺序，不是摄像机记录的真实历程。即使时间点是真实的，样本通常也来自不同动物或不同切片，不能说“同一个细胞从 A 变成了 B”。

这种设计适合回答“哪个区域先出现炎症”“再生过程中哪些状态依次富集”。它的主要风险是个体差异、切片差异和批次效应被误当成时间变化。因此需要生物学重复、阶段匹配和扰动验证。

### 3. 真正的分子时间：pulse–chase 标记

如果先用一个短脉冲标记新生分子，再在不同追逐时间读取它们的位置，就能更直接地约束动力学。以带标签 RNA 数量 $L$ 为例：

$$
\frac{dL}{dt}=\alpha(t)-\beta L(t),
$$

其中 $\alpha$ 是生成率，$\beta$ 是消失率。多个追逐时间点可帮助区分转录、降解、核输出和胞质移动。不过标记本身可能扰动细胞，探针只能覆盖预先选定的靶标，所以“真实时间”也不等于无偏、无限分辨率。

### 4. 四个组学层分别怎样获得时空信息

#### 4.1 转录组：TEMPOmap 是最清楚的真实时空例子

TEMPOmap 先用 5-ethynyl uridine（5-EU）标记新生 RNA，再通过点击化学连接 splint 探针；primer 和 padlock 探针识别目标转录本，环化后进行原位扩增，并把扩增子固定在水凝胶中。每个扩增子携带五碱基条码，通过六轮 SEDAL 成像解码。

在不同 pulse/chase 间隔比较信号，可以估计转录、降解、核输出和胞质转运。图 3 左半边的 Stereo-seq/Slide-seq 是不同阶段的静态空间测量；右半边 TEMPOmap 才通过代谢标记引入分子年龄。它仍是探针驱动的靶向方法，不能写成“无偏全转录组实时电影”。

#### 4.2 蛋白组：空间成像与 APEX2 邻近标记

循环免疫荧光、IMC/MIBI、CODEX 等方法能在组织中定位蛋白；质谱成像绕开固定抗体面板，但在鉴定、灵敏度和空间分辨率之间另有权衡。

图 4 的 FUCCI 例子用细胞周期荧光指示器把不同细胞排序，是群体伪时间。APEX2 则在活细胞中把邻近蛋白快速生物素化；BP5、BN2 探针用于提高动态复合体标记。这里的证据是“在标记时间窗内靠近 APEX2”，不等于每个蛋白都与诱饵直接结合。

#### 4.3 代谢组：MSI 给出 $m/z$ 的空间场

质谱成像测量：

$$
I(m/z,x,y),
$$

即每个质荷比特征在组织坐标上的强度。MALDI、DESI/AFADESI 和 SIMS 的制样、质量范围和分辨率不同。综述表格中的数值来自不同研究，并非统一条件下的横向基准测试。

图 5a 的 AFADESI-MSI 在给药和同位素示踪后，于多个时点取脑切片，定位代谢物和候选通路。示踪增强了通量解释，但仍是破坏性分时取样，并没有连续拍摄同一脑组织。

#### 4.4 表观基因组：空间位置加调控层

空间 ATAC 用 Tn5 记录开放染色质；空间 CUT&Tag 用抗体引导 protein A–Tn5，在空间条码下记录特定组蛋白修饰或蛋白–DNA 占位。联合 ATAC–RNA 或 CUT&Tag–RNA 能把染色质状态与表达放到相近的组织坐标中。

图 5b 展示小鼠胚胎中的 ATAC、RNA 及联合聚类与解剖结构对应。联合嵌入说明二者协变，但不能单凭相关性断言某个开放位点导致了某个基因表达；需要时间顺序和扰动实验。

### 5. 老化与再生案例应该怎样读

图 6 把 APOE 基因型、年龄、单细胞 RNA、空间转录组和质谱成像放在一起，展示脑区、微胶质细胞状态和脂质分布的关联。不同模态互补，但不必然来自同一个细胞。图 6l 的染色质构象示意又是另一项衰老机制研究，不能把整张图当成一个统一实验。

图 7 的再生案例更像一条证据梯度：

- 涡虫：多个再生时点的三维空间图谱，加上 `plk1` RNAi 扰动；
- 蝾螈脑：连续阶段图谱、RNA velocity 和 pseudotime 支持祖细胞到神经元的候选路线；
- 肝损伤：肝小叶分区揭示不同位置的肝细胞恢复；
- 髓系细胞：`Mmp12` 等信号定位损伤邻域中的免疫状态。

空间共现和轨迹是机制假说；加入基因敲低、功能实验或正交成像后，因果证据才更强。

### 6. 八张图从左到右的阅读路线

1. 图 1：老化十二标志，对照再生的类型、细胞过程和调控因素。
2. 图 2：四个组学层的空间检测技术地图。
3. 图 3：静态多时点 STT 与 5-EU/TEMPOmap 的直接对照。
4. 图 4：蛋白群体排序与活细胞邻近标记的对照。
5. 图 5：代谢物示踪和空间表观转录联合测量。
6. 图 6：脑老化/AD 应用及衰老染色质结构。
7. 图 7：涡虫、蝾螈和肝再生的时空案例。
8. 图 8：中心是挑战，外圈是 3D/单细胞、多组学、AI、功能验证和精准医学前景。

### 7. 选择实验时的最短决策表

| 科学问题 | 合适设计 | 必须保留的边界 |
|---|---|---|
| 哪个区域随年龄或损伤阶段改变？ | 匹配的多时点空间取样 | 不是同一细胞纵向追踪 |
| 新生 RNA 在哪里生成、移动和消失？ | 5-EU pulse/chase + TEMPOmap | 靶向探针与标记偏差 |
| 短暂蛋白复合体何时出现？ | 时间控制的 APEX2 邻近标记 | proximity 不等于直接结合 |
| 代谢物或示踪产物在哪里富集？ | MSI + 同位素示踪 | 分辨率、鉴定与破坏性取样 |
| 染色质和 RNA 如何空间协变？ | 联合空间 ATAC/CUT&Tag–RNA | 相关性不等于调控因果 |

### 8. 这篇综述能证明什么、不能证明什么

它能提供术语、平台和案例的导航图，也能提示“空间快照”和“真实分子时间”的差别。它不能提供系统综述级别的证据等级：论文没有报告检索策略、纳入排除标准或偏倚评估，也没有原创数据、代码或统一 benchmark。精准医学、个体化干预等表述是未来方向，不是已经建立的临床效用。需要复用任何定量结论时，应回到相应原始研究。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary — Spatiotemporal multi-omics in aging and regenerative medicine

**Review:** Chu et al., *Military Medical Research* 11 (2024)
**DOI:** `10.1186/s40779-024-00537-4` · **PMCID:** `PMC11129507`

### Answer first

This narrative review organizes spatially resolved transcriptomics, proteomics, metabolomics and epigenomics around one decisive question: does “time” come from destructive sampling of different specimens at ordered stages, or from labeling molecules and following their fate? The first is the field's common, experimentally accessible form and is called pseudo-temporal in the review. The second supplies direct molecular age or interaction timing, exemplified mainly by TEMPOmap for nascent RNA and APEX2 proximity labeling for proteins. The distinction matters because serial tissue sections can reveal population-level change but cannot by themselves observe the same cell or molecule through time.

The review is broad rather than systematic: it does not report a search strategy, inclusion criteria, evidence grading, original dataset, benchmark or code. Its value is a technology-and-application map; its biological claims should be followed back to the cited primary studies.

### Scope and taxonomy

| Layer | Spatial readout surveyed | Temporal strategy emphasized | Representative example | Main limitation |
|---|---|---|---|---|
| Transcriptome (STT) | capture arrays, beads and imaging-based RNA detection | ordered sections or metabolic RNA labeling | Stereo-seq, Slide-seq, TEMPOmap | static sections are not longitudinal; labeling/probe design can bias coverage |
| Proteome (STP) | cyclic antibody imaging, metal imaging and MS imaging | cell-cycle ordering or live-cell proximity labeling | FUCCI-linked proteomics, APEX2 BP5/BN2 | antibody dependence or spatially restricted labeling radius |
| Metabolome (STM) | MALDI, DESI/AFADESI and SIMS imaging | repeated tissue collection, sometimes with isotope tracers | AFADESI-MSI brain drug study | destructive sampling and resolution–coverage trade-offs |
| Epigenome (STE) | spatial CUT&Tag, spatial ATAC and joint RNA assays | ordered sections/developmental states | spatial ATAC–RNA-seq and CUT&Tag–RNA-seq | sparse data, destructive sampling and difficult cross-modal integration |

The review often uses “pseudo-temporal” broadly for measurements at multiple known time points. That is not always the same as algorithmically inferred pseudotime. A defensible reading separates (1) serial cross-sectional sampling, (2) computational trajectory inference, and (3) true pulse/chase or longitudinal labeling.

### Main findings from the surveyed applications

#### Aging

- Spatial transcriptomic and single-cell combinations localize age-sensitive states that bulk averages obscure, particularly glial and inflammatory states in brain tissue.
- The APOE study reproduced in Fig. 6 links genotype and age to region-specific microglial states, transcriptional programs and lipid distributions. It is an example of coordinated evidence across sections and modalities, not proof that all modalities were measured in the same cell.
- Spatial epigenomic studies connect chromatin organization, accessibility, histone marks or RNA modification with senescence and tissue aging, but most evidence remains cross-sectional.
- Proteomic and metabolomic imaging add molecular layers that RNA cannot substitute for, although their analyte identity, multiplexity and spatial resolution differ sharply by platform.

#### Regeneration

- Fig. 7 uses planarian, axolotl and liver studies to show how ordered spatial atlases can identify early response genes, intermediate cell states and region-specific repair programs.
- Planarian regeneration is represented as a time-resolved 3D atlas with spatial domains and perturbation of `plk1`.
- Axolotl telencephalon regeneration combines serial sections, cell-state maps, RNA velocity and pseudotime to propose transitions from ependymoglial cells through intermediate progenitors toward neurons.
- Liver injury studies reveal zonated hepatocyte responses and spatially restricted immune populations, including `Mmp12`-positive macrophage signals near damaged regions.

These examples generate mechanistic hypotheses. Causality requires perturbation or functional validation, which the review itself names as a future priority.

### Challenges and open problems

1. **Integration:** modalities differ in units, sparsity, resolution and tissue preparation; physical co-registration does not guarantee biological correspondence.
2. **Resolution:** “single-cell” claims depend on capture area, segmentation and molecular sensitivity; higher spatial resolution can reduce coverage or throughput.
3. **Temporal identifiability:** destructive serial sampling confounds biological time with specimen variation and cannot track an individual molecule continuously.
4. **Interpretation:** joint embeddings and predictive models can align modalities without establishing regulatory causality.
5. **Standardization:** inconsistent protocols, preprocessing, metadata and reporting obstruct cross-study comparison.

The review proposes 3D and single-cell profiling, broader multi-omics integration, improved computational methods, functional validation and precision medicine. These are prospects rather than demonstrated clinical outcomes.

### Evidence and reproducibility assessment

**Review reproducibility: 2/5.** The article and figures are openly available and the technology tables provide useful entry points, but the review gives no systematic-review protocol, executable analysis, original data or code. Several numerical and comparative claims are inherited from primary papers and were not independently re-benchmarked here. Eight main figures were directly inspected locally; they are mostly conceptual composites or reproduced panels.

### Practical method-selection guide

| Question | Prefer | Do not overclaim |
|---|---|---|
| Which tissue region changes between ages or repair stages? | matched serial spatial profiling with biological replication | observation of the same cell through time |
| How old is a newly synthesized RNA and where does it move? | pulse/chase labeling plus in situ decoding such as TEMPOmap | transcriptome-wide unbiased coverage |
| Which proteins join a transient local complex? | time-controlled APEX2 proximity labeling | direct physical binding for every labeled protein |
| Where do metabolites or isotope products accumulate? | MSI with region-aware quantification and tracer controls | cell identity without segmentation/orthogonal annotation |
| How do chromatin state and RNA co-vary spatially? | joint or carefully registered spatial epigenome–transcriptome assays | causal regulation from correlation alone |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
