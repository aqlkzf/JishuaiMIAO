---
layout: default
permalink: /paper-atlas/cytotemporalcortex-5f08222c/
title: "CytoTemporalCortex"
nav: false
wide: true
description: "人和小鼠的大脑皮层发育具有相同的基本谱系：放射状胶质细胞（RG）产生中间祖细胞（IP），再产生神经元（N）。但两者的发育速度、祖细胞扩增和神经元成熟时间不同。若直接按胚胎天数或孕周对齐，比较的常常不是相同发育状态。 HuMous 因此不把“物种差异”简化为某个时间点的差异表达，而是为每个基因构造一张二维表达景观：横轴表示从早到晚的发育年龄，纵轴表示从 RG 经 IP 到神经元的分化状态。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature · 2026</span>
    </div>
    <h1>CytoTemporalCortex</h1>
    <p>Developmental gene expression patterns driving species-specific cortical features</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-026-10491-x" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CytoTemporalCortex">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/gomez-L/humous" target="_blank" rel="noopener noreferrer" aria-label="Open code for CytoTemporalCortex">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## HuMous 中文方法解读：把物种、年龄和细胞类型放到同一张表达地形图上

### 1. 论文真正要比较什么

人和小鼠的大脑皮层发育具有相同的基本谱系：放射状胶质细胞（RG）产生中间祖细胞（IP），再产生神经元（N）。但两者的发育速度、祖细胞扩增和神经元成熟时间不同。若直接按胚胎天数或孕周对齐，比较的常常不是相同发育状态。

HuMous 因此不把“物种差异”简化为某个时间点的差异表达，而是为每个基因构造一张二维表达景观：横轴表示从早到晚的发育年龄，纵轴表示从 RG 经 IP 到神经元的分化状态。相同基因在人、小鼠和人皮层类器官中的三张景观可以直接比较，从而区分保守、物种特异、培养环境特异和反向调控的模式。

### 2. 输入和最终输出

输入是多个公开 scRNA-seq 数据集：

- 小鼠 E12–E17，约 30,000 个细胞；
- 人 PCW12–24，28,867 个细胞；
- 人皮层类器官 2–7 个月，28,045 个细胞。

原始注释被整理为 RG、IP、N 三类。每个条件内部先整合不同数据集，再平衡抽样。主要计算输出包括：

1. 每个细胞的归一化年龄分数和分化分数；
2. 每个基因的 $250\times250$ 表达景观；
3. 景观的 SD、entropy 和 VGG16 图像特征；
4. 22 个 patterned landscape clusters；
5. 跨物种或跨培养环境的景观相关系数；
6. 可供实验验证的候选调控因子，如 JUNB 和 IRF1。

### 3. 第一步：为什么要训练两个 ordinal regression

每个条件分别训练两个有序回归模型：一个预测年龄等级，一个预测分化等级。这里的监督标签不是连续真值，而是有顺序的类别，例如早期到晚期、RG 到 IP 到 N。

代码 `lib/lib_ordi.R` 使用 `bmrm::nrbm` 拟合 ordinal SVM。代价矩阵经类别频数平衡：

$$
C\leftarrow \frac{\operatorname{costMatrix}(y)}
{\operatorname{tabulate}(y)_{\mathrm{col}(C)}\operatorname{tabulate}(y)},
\qquad C\leftarrow\frac{C}{\sum C}.
$$

这样数量较多的年龄或细胞类型不会自动主导损失。流程先在全部基因上训练模型，再按权重两端选择最有影响的特征，训练缩减模型并交叉验证。人数据脚本中，年龄模型用 20 折，分化模型用 2 折；这两个设置并不相同。

论文把最终分析称为 systematic and unsupervised identification，主要指景观模式的聚类和跨条件发现；二维坐标本身并非完全无监督，因为 ordinal models 明确使用了年龄和 RG/IP/N 顺序标签。

### 4. 连续坐标是怎样从 ordinal score 得到的

离散等级预测容易形成堆积或不均匀分布。`ordi_activate()` 先用 dip test 和 KS test判断分布形状，再对分数作自适应双曲正切变换：

$$
z'=\tanh\left(s\,[z-\operatorname{median}(z)]\right),
$$

其中强度 $s$ 随标准差选为 5、2.5 或 2；随后缩放到 $[0,1]$，并在 1% 与 99% 分位点 Winsorize。分化轴还可把 RG、IP、N 分别限制到部分重叠的区间。例如人数据用 RG $[0,0.24]$、IP $[0.21,0.47]$、N $[0.4,1]$。

因此二维流形不是从数据中自由旋转出来的嵌入，而是带有明确生物学方向的坐标系：横向必须解释为年龄，纵向必须解释为分化。

### 5. 第二步：如何把散点细胞变成一张基因景观

对二维坐标建立 $250\times250$ 的规则网格。每个网格点寻找最近的 $k=100$ 个细胞，然后对某个基因在这些细胞中的表达取平均：

$$
L_g(u,v)=\frac{1}{k}\sum_{i\in \mathcal N_k(u,v)}x_{ig}.
$$

左到右阅读一张景观，就是从早期到晚期；下到上阅读，则是从 RG 经过 IP 到 N。颜色越强，表示该邻域内该基因的平均表达越高。

一个小例子：若某网格点最近的 100 个细胞中，基因 $g$ 的总归一化表达为 240，则该像素值为 2.4。相邻网格点共享许多近邻，因此图像会平滑。这种平滑有利于比较宏观模式，但会弱化稀有亚群和尖锐边界。

live code 在生成景观前会把 `ScaleData` 的整个矩阵整体上移，使最小值为零；论文只说使用 non-negative scaled arrays，并未单独描述这一步。`knn_rowMeans()` 还按约 100 个基因一批处理，以避免一次物化所有基因、所有像素和近邻造成过高内存占用。

### 6. 第三步：SD、entropy 和 VGG16 分别在看什么

SD 衡量景观的强弱对比；全局 Cauchy–Schwarz entropy 衡量像素强度分布的复杂度。论文用确定性阈值把景观划分为 low、non-patterned、patterned 和 ubiquitous，正文再合并展示三类。29.5% 的景观属于 patterned。

必须区分“代码中算出了指标”和“代码中包含完整分类”：当前 partial mirror 的 `LandsH.R` 计算 SD 与 entropy，但最终阈值分类脚本没有收录。因此阈值来自论文 Methods，不能宣称在本地代码中完整复现。

对 patterned landscapes，论文把 PNG 输入 ImageNet 预训练的 VGG16，截取第五个 max-pooling 层：

$$
7\times7\times512=25{,}088
$$

个图像特征。随后在这些特征中选择 2,000 个高变特征，做 PCA、邻居图、UMAP 和三轮 Seurat 聚类，最终得到 22 个景观簇。VGG16 在这里不是预测细胞类型，而是把边缘、纹理和空间结构编码成可聚类的数值向量。

论文 Methods 写 PNG 为 $244\times244$，而本地 `LandsH.R` 实际导出 $224\times224$。`application_vgg16(include_top=FALSE)` 仍输出 $7\times7\times512$，所以核心特征维度一致；这是需要保留的 paper–code 尺寸差异。三轮聚类和 22 簇的完整脚本也不在该 partial mirror 中。

### 7. 第四步：如何比较两张景观

两张景观先各自缩放到 $[0,1]$。只保留任一景观像素强度超过 0.3 的位置，以减少共同背景对相关性的影响。随后固定抽取 2,000 个像素、有放回 bootstrap 10 次，取十次 Pearson correlation 的中位数：

$$
\rho_{g}^{A,B}=\operatorname{median}_{b=1}^{10}
\operatorname{cor}\left(L_{g,b}^{A},L_{g,b}^{B}\right).
$$

高于 0.5 被标为高度相关，低于 −0.5 被标为反相关。这个相关系数比较的是二维表达形状，不等同于基因总表达量或调控因果关系。

### 8. 图 1–3 应怎样串起来读

- **图 1** 建立坐标系：数据整合、两个 ordinal axes、景观和 Humous.org 资源。
- **图 2** 组织景观空间：29.5% patterned，VGG16/UMAP 得到 22 个簇；RG 和神经元程序更保守，IP 相关程序差异最大。
- **图 3** 比较同源基因在不同条件的形状。JUNB 是人—小鼠间最反相关的转录因子，$\rho=-0.64$：在人 RG 中高，在小鼠神经元中高。

这里的 JUNB 是计算筛选出的候选，不是仅凭相关性就已证明的因果因子。因果证据来自后续实验。

### 9. 图 4–5 如何把计算候选变成机制

图 4 用双向实验验证 JUNB：在人类器官中 CRISPRi knockdown 加快神经元生成，而在小鼠 RG 中过表达延长增殖/神经发生窗口、改变克隆大小和细胞周期。CellOracle 给出候选靶基因，CUT&Tag 和表达数据提供部分直接调控证据。

图 5 继续问“为何相似的 JUNB locus 在两物种 RG 中状态不同”。论文定位到在人 RG 表达而在小鼠 RG 缺失的上游因子 IRF1；CUT&RUN 支持 IRF1 在人类器官中结合 JUNB promoter，在小鼠 RG 人工表达 IRF1 能激活 reporter 和内源 Junb，并把转录状态推向人 RG。由此作者提出“poised developmental programme”：小鼠位点保留可响应结构，但缺少恰当的上游调控环境。

### 10. 代码覆盖范围和复现边界

当前 `humous/` 是脚本的 partial mirror，最适合验证以下计算链：

1. `scr/dataset_integration/IntH.R`：调用条件内整合；
2. `lib/lib_ordi.R` 与 `scr/ordinals_age_diff/`：ordinal axes；
3. `lib/lib_lands.R` 与 `scr/landscapes_generation/`：kNN 景观与相关性；
4. `scr/computer_vision/Lands_vgg16_featextr.R`：VGG16 特征；
5. `scr/correlations/corrL.R`：跨条件 bootstrap correlations。

以下部分在本地不能独立端到端复现：`pairwise_integration()` 的定义、DTW 对齐、最终 profile thresholding、三轮景观聚类，以及大部分 CellOracle、CUT&Tag/CUT&RUN、Tracker-seq 和湿实验分析。完整数据和脚本指向 OSF `10.17605/OSF.IO/E8GMA`，另一个下游仓库是 `awaisj14/Humous`。

代码还在 `IntH.R` 中向 `pairwise_integration()` 传入 `nfeats=10000`，而论文 Methods 写每次整合选择 2,000 个高变特征。由于函数定义和中间对象缺失，当前只能记录这个参数差异，不能据此重建最终实际特征集合。

### 11. 最重要的理解边界

HuMous 不是单细胞轨迹模拟器，也不追踪同一个细胞的命运。它把不同细胞的横截面数据按已知年龄和分化顺序压到一个可比较坐标系，再对局部邻域做平滑，形成“基因表达地形”。景观相似性适合发现候选的保守或重排程序，但会受到数据整合、标签整理、平滑尺度、阈值和培养体系差异影响。论文最强的地方，是把这种发现框架与 JUNB/IRF1 的双向功能实验连接起来，而不是把图像相关性本身当成机制证明。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CytoTemporalCortex (HuMous) — Summary

### Motivation & Novelty

#### Biological Problem
The cerebral cortex shows dramatic species-specific differences in size, progenitor diversity, and neuronal output — differences ultimately underlying human cognitive capacity. The source of these differences is poorly understood. Two explanations exist: (1) species-specific genes (e.g., NOTCH2NL, ARHGAP11B, SRGAP2), which account for only a small fraction of divergence; and (2) temporal shifts in the expression of shared, conserved genes. The second mechanism is biologically plausible and supported by isolated examples (e.g., SATB2 timing controlling corpus callosum formation), but has never been systematically mapped across the corticogenesis transcriptome.

#### Limitations of Existing Approaches
- **No systematic cross-species comparison framework**: Prior comparisons aligned datasets by raw developmental age, ignoring that different cell types evolve at different rates (mosaic evolution — Bizzotto & Walsh, *Nat Rev Neurosci.* 2022). Direct age alignment (E15 mouse ≈ PCW18 human) is poorly justified and misses cell-type-specific dynamics.
- **Conventional transcriptomics**: Standard differential expression between species identifies bulk changes but not cyto-temporal patterning within a shared framework.
- **In vivo experiments**: Prior gain/loss-of-function studies focused on individual candidate genes (NOTCH2NL — Suzuki et al., *Cell* 2018; ARHGAP11B — Florio et al., *Science* 2015) without a data-driven approach to nominate targets.

#### Key Contributions (Novelty)
1. **HuMous cyto-temporal framework**: First systematic, unsupervised comparison of cell-type-specific gene expression dynamics across mouse, human, and cortical organoids using ordinal regression and kNN smoothing.
2. **Interactive resource (humous.org)**: 12,700–13,500 gene landscapes per species, searchable and correlatable, enabling community-level discovery.
3. **JUNB identification and characterization**: First demonstration that a shared AP-1 TF has opposite cell-type expression between mouse neurons and human RG, bidirectionally controlling human cortical features.
4. **IRF1 upstream mechanism**: First identification of a human-specific upstream regulator (IRF1) that activates a mouse-primed locus (Junb) to recapitulate human phenotypes — demonstrating "poised developmental programs."

---

### Method Overview

The HuMous pipeline builds a 2D cyto-temporal manifold and populates it with ~12,700–13,500 gene expression landscapes per condition.

**Key steps**:
1. Integrate multiple scRNA-seq datasets per condition (Mouse: E12–E17; Human: PCW12–24; OrgH: 2–7 months) using Seurat v3 pairwise integration with temporal alignment (DTW on corticogenic milestones and RG:IP:N proportions).
2. Fit ordinal SVM regression models (bmrm v4.1) separately per condition to assign each cell a normalized age score (x, 0–1) and differentiation score (y, 0–1).
3. Generate gene expression "landscapes": kNN smoothing (k=100) on a 250×250 grid produces a 2D image per gene per condition.
4. Classify landscapes by SD/entropy → patterned (SD>0.15), non-patterned, ubiquitous.
5. Apply VGG16 (ImageNet, include_top=False) to extract 25,088 features per landscape → UMAP clustering → 22 landscape clusters.
6. Compute bootstrapped pairwise correlations (threshold=0.3, n=10 bootstraps, 2000 pixels) across species/context → classify genes into 4 classes.
7. Experimental validation of top candidate (JUNB) via IUE in mouse, CRISPRi in human organoids, CUT&Tag, CUT&RUN, Tracker-seq, and scRNA-seq.

See `doc_method.md` for mathematical details.

---

### Evaluation

#### Datasets
- **Mouse**: GSE118953, GSE107122, GSE153164, PRJNA637987 (~30,000 cells, E12–E17)
- **Human**: phs000989, GSE162170, NeMo nemo:dat-9jd8xw6 (~28,867 cells, PCW12–24)
- **OrgH**: Pollen 2019 (Cell), Velasco 2019 (Nature), Tanaka 2020 (Cell Rep), Kanton 2019 (Nature) (~28,045 cells, 2–7 months)
- **New scRNA-seq (generated)**: E16 electroporated mouse cortex (JUNB, IRF1/EGR1 OE conditions), P0 Tracker-seq; GEO: GSE324846

#### Key Quantitative Results

| Claim | Result |
|---|---|
| % patterned landscapes (human vs. mouse) | P=1.29×10⁻¹²⁶ (fewer in human) |
| JUNB landscape correlation (H vs. M) | ρ = -0.64 (most anti-correlated TF) |
| JUNB KD → neuron:progenitor ratio (OrgH) | P=0.0466 (two-tailed t-test) |
| JUNB OE → IP-N/RG ratio (mouse E16) | P=0.0055 (decreased) |
| JUNB OE → clone size (Tracker-seq) | χ²=51.43, P=5.8×10⁻⁸ |
| JUNB OE → G1/S fraction increase | P=0.0093 |
| IRF1 activates human JUNB promoter in mouse | P=0.0027 |
| IRF1 OE → extended neurogenesis (BrdU birthdating) | P=0.0077 |

#### Biological Findings

**Cell-type conservation patterns** (Figure 2): RG and neurons show highly conserved expression programs; IPs show the most divergence. IP-only landscapes are more frequent in human, reflecting expanded SVZ. ~50% of mouse RG-only genes shift to RG-IP or IP-only in human — genes co-opted into human IPs for enhanced self-renewal capacity.

**Disease gene insights** (Figure 2f): Cortical malformation genes (microcephaly, lissencephaly) concentrated in IPs; neuropsychiatric genes enriched in neurons; some Alzheimer's disease genes expressed in progenitors.

**JUNB mechanism** (Figures 3–4): The AP-1 complex member JUNB has mutually exclusive expression: mouse neurons vs. human RG. It controls ~769 target genes in human RG, predominantly cell-cycle regulators. Direct CUT&Tag binding confirmed for 17/32 RG-enriched activated targets. JUNB remodels chromatin via H3K27 acetylation in mouse RG after overexpression.

**IRF1 upstream regulation** (Figure 5): IRF1 is expressed in human but not mouse RG. It directly binds the JUNB promoter (CUT&RUN in OrgH). The JUNB/Junb locus is "primed" in mouse (accessible IRF1 binding motifs) but inactive without IRF1. Artificial IRF1 expression in mouse RG: (1) activates Junb; (2) shifts mouse RG transcriptome toward human RG; (3) phenocopies JUNB OE (extended neurogenesis, G1/S increase). EGR1 acts synergistically.

#### Reference Points for Evaluation
- The UMAP-based batch mixing metric (iLISI) was used to validate integration quality
- Ordinal model performance: Spearman ρ and Kendall τ both significantly correlated with actual age/diff labels (P<0.0001 in all conditions/cell types)
- Landscape robustness: 5 permutations show high correlation with reference landscapes (mean 0.80–0.86 depending on k choice)

---

### Reproducibility Rating: 3.5/5

#### Justification
**Strengths**:
- All scRNA-seq datasets deposited publicly (GEO accession GSE324846 for new data; previously published datasets accessible through dbGaP, GEO, NeMo, EGA)
- Code deposited at github.com/gomez-L/humous (core pipeline) and github.com/awaisj14/Humous (downstream analyses)
- Interactive landscape viewer at humous.org
- Methods describe exact hyperparameters (λ=0.05, nfolds=20, k=100, threshold=0.3, etc.)
- All statistical tests and sample sizes reported with exact P-values

**Limitations reducing score**:
- GitHub repository (gomez-L/humous) is **a partial mirror** — `pairwise_integration()` function and several intermediate objects only available at OSF (https://doi.org/10.17605/OSF.IO/E8GMA); not all preprocessing scripts are in the public GitHub
- CellOracle, CUT&Tag/CUT&RUN, and lineage barcode analyses are in a **separate repository** (awaisj14/Humous) that also links to OSF for data
- The VGG16 pipeline requires a specific **Python 3.7 miniconda environment** that may be difficult to reproduce in 2026+
- PNG size discrepancy (code: 224×224, paper: 244×244) suggests a minor documentation issue
- Wet-lab experiments require specialized access: human fetal tissue (ethics protocol from Liège), iPSC lines, IUE expertise

#### Practical Notes
- To reproduce landscape computation: clone gomez-L/humous, download integrated data objects from OSF, run `scr/ordinals_age_diff/OrdisH.R` → `scr/landscapes_generation/LandsH.R`
- VGG16 step requires R package `keras` with `use_miniconda(condaenv="minic_py37")`
- Intermediate RDS objects are large (>10 GB total); allocate adequate storage
- The `pairwise_integration()` function in `IntH.R` (line 101) is not in the GitHub `lib_misc.R` — must retrieve from OSF

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
