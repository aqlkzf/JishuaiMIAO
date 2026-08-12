---
layout: default
permalink: /paper-atlas/tcat-2f3ccbdd/
title: "TCAT"
nav: false
description: "TCAT 的实质是把大规模、多数据集共同出现的 T 细胞程序固化成一个参考基底，再用简单、可审计的非负固定参考拟合，把新细胞表示为多个谱系、功能和技术程序的相对混合；它牺牲了发现未知程序的能力，换取跨研究的一致性、稳定性和可解释性。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>TCAT</h1>
    <p>Reproducible single-cell annotation of programs underlying T cell subsets, activation states and functions</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TCAT / starCAT 方法详解

### 1. 这项工作解决什么问题

单细胞转录组中的一个 T 细胞通常不只具有一个“身份”。同一个细胞可以同时表现出谱系、分化阶段、细胞毒性、抗原刺激、干扰素反应、增殖、应激和低质量等信号。传统聚类把细胞压缩成一个离散标签，因此容易出现两类问题：

1. 不同谱系的细胞因为共享一个强功能程序而被聚到一起，例如多个亚群的增殖细胞形成统一的 cell-cycle 簇；
2. 同一亚群内部同时存在的多个功能状态被单一标签遮蔽。

论文将问题改写为“程序分解”：每个细胞不是只属于一个类别，而是由多个非负基因表达程序（gene expression program, GEP）以不同权重叠加而成。`starCAT` 是通用的固定参考推断框架，`TCAT` 是用七个大型 T 细胞数据集构建的专用参考图谱（`paper.md:24,56-71`）。

### 2. 相比已有方法，核心变化在哪里

ProjecTILs（*Nature Communications*, 2021）、Symphony（*Nature Communications*, 2021）和 Azimuth/Seurat 多模态参考（*Cell*, 2021）主要把查询细胞映射到离散参考标签。它们适合回答“这是什么细胞”，但不能直接表示“这个细胞同时有多少 naive、cytotoxic、interferon 和 proliferation 信号”。

cNMF（*eLife*, 2019）能够从单个数据集发现重叠程序，但每次在查询数据上重新分解会带来三个困难：小样本不稳定、不同研究所得因子不在同一坐标系、因子需要重新人工命名。TCAT 的关键贡献不是更复杂的模型，而是先从多数据集提炼可复现的共识程序，再把这些程序固定下来用于新数据。

### 3. 名词和口径

- **GEP**：在单个数据集中由 cNMF 发现的基因表达程序。
- **cGEP**：多个数据集中相似 GEP 合并后形成的 consensus GEP。
- **starCAT**：给定固定程序矩阵后，只估计查询细胞程序用量的算法与软件包。
- **TCAT**：starCAT 的 T 细胞参考实现与其派生注释。
- **52 与 46**：最终参考矩阵有 52 个程序，其中包括 6 个非 T 细胞/双细胞提示程序；论文标题式表述所说的 T 细胞核心目录为 46 个 cGEP。两者是不同统计口径，并不矛盾（`paper.md:62-71,353-367`）。

### 4. 整体流程

```text
七个参考数据集，约 170 万 T 细胞、38 种组织
        |
        v
各数据集独立质控和高变基因选择
        |
        v
适配后的 Harmony：在基因空间进行非负批次校正
        |
        v
各数据集独立运行 cNMF，得到 267 个数据集级 GEP
        |
        v
跨数据集相关图 + 互为前七邻居 + >2/3 连通规则
        |
        v
平均合并谱，得到 52 个固定参考程序
        |
        +----------------------------------+
                                           |
新查询原始计数                            固定参考 G*
        |                                  |
        v                                  v
检查非负 -> 基因取交集 -> 按基因标准差缩放 -> 只拟合 U
        |
        v
每个细胞的相对 cGEP 用量
        |
        +--> 谱系/亚群标签
        +--> 增殖分数
        +--> 抗原特异性激活 ASA 分数
        +--> 直接查看功能、应激和双细胞程序
```

### 5. 第一步：在各参考数据集中发现程序

#### 5.1 预处理

作者过滤低检测基因和低 UMI 细胞，选择 2,000 个过度离散基因，并按基因方差缩放。用于初始分解的矩阵不包含 ADT；ADT 在后续全特征谱重拟合时用于帮助程序解释（`paper.md:335-350`）。

普通 Harmony 通常校正 PCA 坐标，但 cNMF 需要非负的基因表达矩阵。论文先在常规归一化矩阵上用 PCA/Harmony 学习批次与聚类结构，再把 mixture-of-experts 校正应用到原始基因空间，并把校正后少量负值截为零。这样得到既批次校正又保持非负的矩阵 $X^c$（`paper.md:341`）。

#### 5.2 cNMF 目标

设：

- $X\in\mathbb{R}_{\ge0}^{N\times H}$：$N$ 个细胞、$H$ 个基因；
- $U\in\mathbb{R}_{\ge0}^{N\times K}$：每个细胞对 $K$ 个程序的用量；
- $G\in\mathbb{R}_{\ge0}^{K\times H}$：每个程序的基因权重。

cNMF 求解：

$$
\operatorname*{ArgMin}_{U,G}\lVert X-UG\rVert_F,
\qquad U\ge0,\;G\ge0.
$$

作者对候选 $K=15\ldots55$ 各运行 20 次，以重构误差和稳定性选择 $K^*$，再对选定的 $K^*$ 运行 200 次获得共识谱（`paper.md:301-318,344-350`）。

### 6. 第二步：把 267 个 GEP 合并为跨数据集共识

每个数据集独立分解后，作者在所有数据集级 GEP 之间建立相关图：

1. 将各程序谱重新归一化，并除以对应数据集的基因 TP10K 标准差；
2. 只比较来自不同数据集的程序；
3. 要求 Pearson 相关 $R>0.5$；
4. 两个程序还必须互为对方跨数据集相关度前七名；
5. 按相关度从高到低处理候选边；
6. 合并簇时要求跨簇可能配对中超过三分之二存在连接，并禁止同一数据集在一个共识簇中出现两次；
7. 对一个共识簇内的谱取平均。

代码中的默认相关阈值为 0.5、连通比例为 0.666；论文时代 notebook 还明确记录 `order_thresh=7`。这些规则分别可在 `build_consensus_reference.py:47-49,140-216,219-380` 和 `Define_cGEPs_Latest.ipynb:132664-132678,132820,133234-133312` 中核对。

267 个 GEP 最初形成 49 个多数据集合并组和 52 个单例。作者保留 3 个有生物学依据的单例，过滤其余单例，最终得到 52 个参考程序。保留的程序不仅有谱系和状态，也有 mitochondrial、poor-quality、immediate-early-gene 以及 6 个非 T 细胞双细胞提示程序；这些信号被显式表示，而不是被误吸收到生物学亚群中。

### 7. 第三步：用固定参考注释新查询

#### 7.1 输入和对齐

查询输入应是非负原始计数。实现会：

1. 将 DataFrame 转换为 AnnData（如需要）；
2. 拒绝负值，对非整数值给出警告；
3. 取查询与参考基因交集并排序；
4. 对每个基因按标准差缩放但不减均值，从而保持非负；
5. 将查询转换成与参考相同的数据类型。

这些行为直接位于 `code/starCAT/src/starcat/starcat.py:227-261`；README 说明计数应放在 `adata.X`（`code/starCAT/README.md:42-49`）。

#### 7.2 固定参考 NMF

设 $G^*$ 为已构建好的参考程序矩阵，starCAT 不再更新程序，只拟合查询用量：

$$
\operatorname*{ArgMin}_{U}\lVert X^{query}-UG^*\rVert_F,
\qquad U\ge0.
$$

论文使用 Frobenius 损失、multiplicative-update (`mu`) 求解器、容差 $10^{-4}$ 和最多 1,000 次迭代。发布代码把 `H=reference`、`update_H=False` 传给 scikit-learn 的 `non_negative_factorization`，与论文目标一致（`paper.md:321-332`; `starcat.py:19-26,264-290`）。

#### 7.3 行归一化

默认输出为：

$$
\widetilde U_{ik}=\frac{U_{ik}}{\sum_j U_{ij}}.
$$

因此数值表示一个细胞中各参考程序的相对组成，不是绝对通路活性。某个程序占比上升会机械地压低其他程序的占比。未归一化用量仍保留在对象中（`starcat.py:199-223`）。

### 8. 从 cGEP 用量得到高级注释

#### 8.1 谱系与亚群

论文把所有归一化 cGEP 用量标准化后，在 COMBAT 的人工 ADT 门控标签上训练 class-balanced multinomial logistic regression，并在独立流感疫苗数据中测试。TCAT 多标签预测的 balanced accuracy 为 0.72，高于 clustering 0.61、Symphony 0.58、Azimuth 0.52 和 ProjecTILs 0.13（`paper.md:74-94,397-415`）。

#### 8.2 增殖

增殖分数定义为三个细胞周期程序之和：

$$
S_{proliferation}=U_{CellCycle-S}+U_{CellCycle-Late-S}+U_{CellCycle-G2M}.
$$

下游分析以 0.1 区分高低细胞周期用量（`paper.md:448`）。

#### 8.3 抗原特异性激活 ASA

AIM-seq 的逐步前向选择得到四个程序：

$$
S_{ASA}=U_{TIMD4/TIM3}+U_{ICOS/CD38}+U_{CTLA4/CD38}+U_{OX40/EBI3}.
$$

每一步选择能在 COMBAT 和流感疫苗数据中最大化 CD71$^+$CD95$^+$ 预测平均 AUC 的程序；当两个数据集的 AUC 都不再提高时停止。作者主动排除了广泛的细胞周期、细胞骨架和亚群关联程序，使 ASA 更聚焦于激活而不是谱系（`paper.md:457-463`）。

方法正文给出的二值阈值是 0.0625，而 Fig. 5 与 Extended Data Fig. 6 图注写作 `ASA > 0.065`（`paper.md:170,178,694`）。这很可能是图示取整，但工作区缺少 `TCAT.V1.scores.yaml`，不能核验发布包的精确阈值；方法复现应保留 0.0625，复述图示时注明 0.065。

### 9. 证据链如何验证方法有效

- **模拟数据**：参考和查询故意包含不完全相同的程序，并随机丢失部分基因。starCAT 对共有程序的 Pearson 相关通常超过 0.7，小查询下比重新运行 cNMF 更稳定。
- **独立亚群基准**：在 336,739 个流感疫苗 T 细胞上，用独立人工 CITE-seq 门控检验多标签注释，而不是只在训练数据上报告拟合。
- **混合程序解释**：COMBAT 示例表明，一个聚类可以同时混有亚群、细胞周期、细胞毒、干扰素和低质量信号，TCAT 能将其拆开。
- **实验激活验证**：五位供体的 peptide AIM-seq 产生 AIM-positive、AIM-negative 和 mock 群体。ASA 在 COMBAT、流感疫苗和 AIM 数据中的 AUC 分别为 0.920、0.818 和 0.828。
- **疾病与临床关联**：样本级分析在 COVID-19、类风湿关节炎、肿瘤及 ICI 队列中发现可重复关联。ICI 结果属于回顾性关联，不能当作前瞻性疗效预测器。

图像层面的完整证据链见 `figure_analysis.md`：本工作区直接检查了 6 张主图、8 张 Extended Data 图和 M1 中 10 张 Supplementary Figure。

### 10. 如何实际使用和解释

最适合的使用场景是：研究者希望把多个 T 细胞研究放进同一可解释坐标系，并允许每个细胞同时携带多个程序。基本步骤是准备 `adata.X` 中的非负计数，加载 `TCAT.V1` 或自定义参考，运行 `fit_transform`，再分析 `usage_norm` 与附加分数。

解释时应遵守以下边界：

- 高 cGEP 用量表示查询表达与该参考程序相似，不等于证明一种离散细胞身份；
- 固定参考不能发现参考中没有的新程序，异常残差也不会自动被命名；
- 行归一化后的值是组成比例，跨条件比较应注意组成效应；
- ASA 是经 AIM、蛋白和克隆扩增关联验证的转录代理指标，不是抗原特异性的直接实验测量；
- poor-quality、IEG 和双细胞程序应作为诊断维度，而不应自动解释成疾病机制。

### 11. 代码与论文的对应程度

核心查询算法的对应程度高：输入检查、基因交集、非中心化标准差缩放、固定 `H` 拟合、求解器参数和行归一化均可在发布包中直接定位。共识参考构建的主要阈值和图合并逻辑也能在源码与 notebook 中互证。

整体论文复现程度为中等，原因不是核心公式缺失，而是运行资产和分析环境不完整：

- 当前工作区没有下载后的 `TCAT.V1.reference.tsv`、`TCAT.V1.scores.yaml` 和其中的分类器资产；
- `TCAT_analysis` 中大量 notebook 依赖 `/data/srlab1/TCAT/...` 作者集群路径及未打包中间文件；
- figure map 有两个失效 notebook 路径，Extended Data 1 和 6A 仍是未解析的问号占位；
- 没有发现软件包测试套件或完整环境锁文件；
- 论文使用 scikit-learn 1.1.3，README 报告 1.3.2 测试，`setup.py` 只限定 `>=1.0`；
- 网页列出的 M5–M8 补充/源数据表未进入本工作区。

因此，本工作区足以审计算法、主要参数、图表逻辑和论文论证，但若要逐数值重现全部结果，仍需外部 TCAT.V1 资产、公开原始数据以及作者集群上的中间产物。

### 12. 一句话总结

TCAT 的实质是把大规模、多数据集共同出现的 T 细胞程序固化成一个参考基底，再用简单、可审计的非负固定参考拟合，把新细胞表示为多个谱系、功能和技术程序的相对混合；它牺牲了发现未知程序的能力，换取跨研究的一致性、稳定性和可解释性。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## TCAT / starCAT Summary

### Paper

**Reproducible single-cell annotation of programs underlying T cell subsets, activation states and functions** — *Nature Methods* 22, 1964–1980 (2025). DOI: `10.1038/s41592-025-02793-1`.

### Problem

T-cell transcriptomes combine lineage, differentiation, activation, proliferation, stress and technical signals. Clustering assigns one discrete label and can therefore hide coexpressed programs—for example, proliferating cells from several subsets may cluster together. De novo factorization can recover programs but is slower, unstable in small queries and does not automatically place different datasets in the same coordinate system.

Existing reference mappers such as ProjecTILs (*Nature Communications*, 2021), Symphony (*Nature Communications*, 2021) and the Azimuth/Seurat multimodal framework (*Cell*, 2021) transfer discrete labels but do not directly quantify several concurrent functional programs. Earlier T-cell component catalogs—cNMF (*eLife*, 2019), NMFproject-based autoimmune T-cell programs (*Cell Genomics*, 2024) and pan-cancer programs (*Nature*, 2023)—covered fewer contexts or fewer programs.

### Proposed Method

The paper introduces **starCAT**, a general fixed-reference annotator, and **TCAT**, its T-cell reference.

1. Run adapted Harmony batch correction and cNMF independently on seven reference datasets containing 1.7 million T cells from 38 tissues.
2. Correlate 267 dataset-specific GEPs across datasets and merge mutually similar programs using $R>0.5$, mutual top-seven matching and a greater-than-two-thirds connectivity rule.
3. Average merged spectra to form 52 reference programs, including six non-T-cell doublet programs; the curated T-cell catalog therefore contains 46 cGEPs.
4. For a new query, standard-deviation-scale overlapping genes and estimate only the nonnegative usage matrix $U$ while holding the reference $G^{*}$ fixed:

$$
{\rm ArgMin}_{U}|X^{\rm query}-UG^{*}|_{F}, \qquad U\ge 0.
$$

5. Row-normalize usages and derive lineage, proliferation and antigen-specific activation (ASA) annotations.

The practical novelty is not a new deep model; it is a reusable multi-dataset program coordinate system that lets one cell simultaneously carry subset, functional and artifact annotations.

### Main Results

- **Simulation:** starCAT recovered overlapping programs with Pearson $R>0.7$, suppressed reference-only programs and remained accurate as query size decreased, while de novo cNMF degraded.
- **Independent subset benchmark:** in 336,739 flu-vaccine T cells with manual CITE-seq gates, TCAT multi-label prediction achieved balanced accuracy 0.72 versus 0.61 for clustering, 0.58 for Symphony, 0.52 for Azimuth and 0.13 for ProjecTILs.
- **Multi-program interpretation:** TCAT separated subset identity from cell cycle, cytotoxic, interferon and poor-quality programs in COMBAT cells, revealing heterogeneity obscured by published clustering.
- **AIM-seq:** peptide stimulation of five donors identified 24 AIM-associated cGEPs. Four programs—TIMD4/TIM3, ICOS/CD38, CTLA4/CD38 and OX40/EBI3—formed the ASA score.
- **ASA validation:** AUC was 0.920 for CD71/CD95 activation in COMBAT, 0.818 in flu-vaccine and 0.828 for AIM positivity. ASA also associated with activation proteins, proliferation and TCR clone expansion.
- **Disease use cases:** sample-level analyses identified reproducible COVID-19, rheumatoid arthritis and tumor-associated programs.
- **ICI associations:** activation/cell-cycle programs were higher in nonresponders, while naive cGEPs were higher in responders across melanoma, non-melanoma skin cancer and colorectal cancer. These are retrospective associations, not prospective clinical validation.

### What the Figures Show

The main and extended figures visually support a coherent chain: cross-dataset cGEP blocks → independent query annotation → decomposition of mixed cluster signals → experimental activation programs → ASA validation → disease/ICI associations. Supplementary figures reinforce simulation robustness, $K$ selection, cGEP marker specificity, clustering errors, activation gene-set comparisons and cohort-quality effects.

### Reproducibility

**Rating: 3/5 — algorithmically reproducible, full analysis only partially portable.**

Strengths:

- Both author-declared repositories are preserved with commits.
- The released `starCAT` package directly matches the fixed-reference objective, solver settings, gene overlap/scaling and row normalization.
- The paper analysis repository maps most figure panels to notebooks.
- Public data accessions and code URLs are reported.

Gaps:

- The exact downloaded `TCAT.V1.reference.tsv` and score YAML are absent from this workspace; they are runtime Zenodo assets.
- Many analysis notebooks require unbundled `/data/srlab1/TCAT/...` files and intermediates; there is no single end-to-end workflow.
- The figure map has two broken paths and two panels with unresolved question-mark placeholders; no package test suite was found.
- The paper uses scikit-learn 1.1.3, the README reports testing with 1.3.2 and packaging allows `>=1.0`.
- ASA is reported as 0.0625 in Methods and rounded to 0.065 in figure captions; the packaged threshold cannot be checked without the missing score bundle.

### Limitations

- Requiring cross-dataset reproducibility may filter genuine disease- or tissue-specific programs.
- Fixed-reference inference cannot discover a novel query program; it can only express the query in the supplied basis.
- Row-normalized usages are relative and compositional, not absolute pathway activity.
- AIM-seq used five donors, one peptide pool and one co-stimulation design.
- Sample processing and quality affect IEG, poor-quality and sometimes ASA-related signals.
- Several clinical cohorts are small, and the ICI analysis combines pre/post-treatment samples in CRC.

### Bottom Line

TCAT is most useful when researchers want a consistent, interpretable T-cell program representation across studies without rerunning and annotating de novo factorization. Its core inference code is simple and faithful to the paper; the scientific value comes from the breadth and validation of the reference catalog. Exact paper-wide reproduction still requires the external `TCAT.V1` bundle, public datasets and author-cluster intermediates not preserved here.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
