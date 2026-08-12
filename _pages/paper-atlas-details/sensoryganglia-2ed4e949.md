---
layout: default
permalink: /paper-atlas/sensoryganglia-2ed4e949/
title: "SensoryGanglia"
nav: false
description: "这项研究把体细胞嵌合变异当作人体内自然形成、终生保留的“谱系条形码”，比较背根神经节（DRG，感觉）与交感神经节（SG）的克隆组成。人类、两套小鼠 CRISPR 谱系记录、单核测序和鹌鹑活体成像共同支持：多数躯干神经嵴细胞在离开神经管之前已偏向 DRG 或 SG 命运；它们还会在神经管内沿头尾轴迁移，这一过程依赖 FGF 信号。"
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
      <span>Data Sources &amp; Technologies</span>
      <span>Nature · 2026</span>
    </div>
    <h1>SensoryGanglia</h1>
    <p>Developmental organization of sensory and sympathetic ganglia</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-026-10313-0" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 感觉神经节与交感神经节的发育组织：方法解读

### 一句话结论

这项研究把体细胞嵌合变异当作人体内自然形成、终生保留的“谱系条形码”，比较背根神经节（DRG，感觉）与交感神经节（SG）的克隆组成。人类、两套小鼠 CRISPR 谱系记录、单核测序和鹌鹑活体成像共同支持：多数躯干神经嵴细胞在离开神经管之前已偏向 DRG 或 SG 命运；它们还会在神经管内沿头尾轴迁移，这一过程依赖 FGF 信号。

### 问题为什么难

DRG 和 SG 都来自躯干神经嵴（neural crest, NC），但分别形成感觉与自主神经系统。长期争论是：NC 细胞离开神经管时仍然多能，之后由迁移环境决定命运；还是它们在 delamination 之前已经分化为不同祖细胞谱系。

传统染料、病毒或荧光 reporter 往往一次标记空间上相邻的一群细胞。若后代同时出现在 DRG 与 SG，不能确定它们来自同一祖细胞，还是起初就混合了多个祖细胞。它们也较难在整条颈—胸—腰轴上追踪人体克隆。因此论文引入 mosaic variant barcode analysis（MVBA）：细胞分裂中自然产生的体细胞嵌合变异会传给所有后代，变异的组织分布与等位基因频率（AF）就成为内源谱系记录。

### 整体证据链

```text
3 名供体：94 个 DRG + 93 个 SG + 外周器官
        ↓
高深度 WGS 发现候选体细胞嵌合变异
        ↓
MPAS >500× 验证并测量每个神经节中的 AF
        ↓
MV × 神经节矩阵
  ├─ 解剖地图（geocline）
  ├─ Manhattan 距离聚类 + 10,000 次 bootstrap
  ├─ 头尾轴与背腹轴 AF 方差比较
  └─ 超几何模拟估计 DRG/SG 与左/右分离时的祖细胞数
        ↓
人类结论：DRG 与 SG 克隆上分离，且 DRG/SG 命运分离早于左右分离
        ↓
小鼠 Homing CRISPR + DARLIN、单核 MVBA、RNA velocity 复核
        ↓
鹌鹑活体成像 + FGFR 抑制解释头尾迁移机制
```

### 第一步：用自然变异做人体谱系追踪

作者从 3 名供体获得颈、胸、腰段双侧神经节以及脑、心、肝、肾、皮肤等外周组织。外周器官的约 300× WGS 用于发现较早发生、分布较广的候选变异，神经节约 30× WGS 补充局部候选；随后用定制扩增子面板对所有候选位点做大于 500× 的 MPAS。最终识别超过 1,200 个可靠 MVs（论文第 68–74 行；Methods 第 341–368 行）。

对一个二倍体中的单等位基因变异，若携带该变异的后代占组织细胞比例 $f$，理想情况下：

$$
\mathrm{AF}\approx \frac{f}{2}.
$$

所以 AF 不只是“有没有这个克隆”，还近似表示克隆贡献大小。不过实际 ganglion 中包含非 NC 衍生细胞、测序误差和取样波动；论文用 snRNA-seq 估计 DRG/SG 中约 80% 细胞是躯干 NC 衍生，并用阳性/阴性位点和置信区间校准 MPAS，而不是把原始 AF 直接等同于细胞比例。

本地 `compute_maf_binom.py` 解析 pileup 碱基及质量，计算 MAF 和 95% 区间，并另提供 Clopper–Pearson 与 Wilson 区间函数（`code/Pipelines/MuTect2_Strelka2/helper_scripts/compute_maf_binom.py:9-73,92-171`）。但从 MPAS 原始输出生成论文最终 AF 矩阵的全部上游脚本并未完整存入仓库，这是复现边界。

### 第二步：判断 DRG 与 SG 是否属于不同克隆谱系

作者把每个 MV 在各神经节的 $\sqrt{\mathrm{AF}}$ 组成矩阵，用 Manhattan 距离和 complete linkage 聚类。平方根变换压缩高 AF 克隆的视觉支配，Manhattan 距离也适合大量零值的稀疏向量。`bootstrap.R` 固定随机种子 123，并为每名供体运行 `pvclust(..., method.dist="manhattan", method.hclust="complete", nboot=10000)`（`code/Analysis/bootstrap/bootstrap.R:3-22,25-61`）。

Fig. 2 把 MV 的空间分布直接画到左右、颈胸腰 DRG/SG 上；Fig. 3 的树状图显示，显著支持的近邻通常属于相同 ganglion 类型，而不是简单按左右或相同脊柱节段聚类。作者还比较：

- **头尾轴（rostrocaudal）**：同一种 ganglion 沿不同胸段的变异程度；
- **背腹轴（dorsoventral）**：相近节段 DRG 与 SG 之间的变异程度。

由于每条胸段链有 12 个 ganglia，而单节段只有 4 个，背腹比较采用 3 个相邻节段的 rolling window 来平衡样本数。三名供体的背腹差异均显著大于头尾差异（论文第 76–83 行）。仓库保存了已计算好的 rolling-SD CSV，`Analysis.R` 对 horizontal 与 vertical 值做 Wilcoxon 检验（`code/Analysis/Stdev_vertical_horizontal/Analysis.R:1-30`）；rolling-SD 的上游生成步骤不在该脚本中，所以该行应视为部分而非完整实现。

### 第三步：用“分离时祖细胞数”排序发育事件

关键逻辑是比较两个事件：

1. DRG 与 SG 命运分离；
2. 左侧与右侧谱系分离（与 delamination 相关）。

如果 DRG/SG 分离发生得更早，当时共同祖细胞池应更小；稍后的左右分离发生时，细胞池已经扩增。对仅出现于某一组的 MV，论文用

$$
N_{\min}=\frac{1}{2\overline{\mathrm{AF}}}
$$

估计最小祖细胞数。这个公式在论文 Methods 中明确给出，但仓库没有独立实现，不能把 `input$temp` 误认作该公式。

对两组共享的 MV，作者扫描候选祖细胞数，用超几何分布构造在该细胞池大小下可产生的 AF 区间，并找到仍可解释两组 AF 差异的最大规模。核心 R 代码扫描 `seq(5,5000,by=5)`，调用 `hyperCI`，对单等位基因状态做乘 2 校正，并把 `idd*2` 写为估计值（`Start_population_simulation.R:18-48`）。

这里存在值得保留的论文—代码差异：论文描述 1,000 个从 0 到 10,000、步长 10 的候选值，而代码使用 5 到 5,000、步长 5，最后再乘 2；两者输出尺度可对应，但搜索参数的表述并不字面一致。

Fig. 4 从二维 AF 差异图、模拟分布和祖细胞数估计连续展示这一推理。结果中 DRG/SG 分离对应的最大祖细胞数低于左/右分离，支持命运指定先于 delamination；这是群体统计推断，不是对单个历史细胞状态的直接观测。

### 第四步：三种正交验证

#### 小鼠 CRISPR 谱系记录

研究使用 Sox10-Cre 驱动的 Homing CRISPR 和可诱导 DARLIN 两套系统。若 DRG 与 SG 来自独立的已指定克隆，同一编辑条形码的强连接应更常出现在相同 ganglion 类型。Fig. 4 的克隆树与 coupling 分析支持这一预测。DARLIN 分析以 notebooks 形式存在，但依赖外部 DARLIN 工具；本地代码不足以独立重建完整条形码计数流程。

#### 人体单核 MVBA

作者从供体 ID07 的 T2/T3 DRG 和 SG 获得 224 个单核，同时扩增基因组和转录组；其中 75 个核获得细胞类型注释。184 个 MVs 构建的系统树显示，末端近邻更常来自相同 ganglion。仓库的 shell 脚本把标签随机打乱 10,000 次，并统计末端配对类别（`code/Analysis/Permutation_single_cell/Permutation.sh:1-21`）。需要注意，224-cell 分支仍把结果追加到文件名含 `75_Cells` 的输出，属于实现中的命名/覆盖风险。

#### RNA velocity 与鹌鹑活体成像

小鼠 E8.5–E9.5 的 NC 单细胞 RNA 数据用 scVelo dynamical model 寻找早期感觉/交感偏向转录因子，支持 delamination 前已有不同转录动力学（论文第 58–67、439–448 行；Extended Data Fig. 3）。该分析主要存在于一个大型 notebook，适合标为 Notebook 证据而非逐函数 Exact。

鹌鹑 Pax7 enhancer reporter 的时间序列直接显示部分 NC 细胞在神经管内沿头尾方向移动，约 20% 可跨中线；FGFR 抑制剂 inf﻿igratinib 将头尾迁移显著降低，并增加侧向离开神经管的倾向（论文第 192–203、449–468 行）。Fig. 5 把单核树和活体轨迹并列：前者验证克隆组织，后者给出这种跨节段克隆扩散的细胞行为机制。

### 如何读五张主图

- **Fig. 1**：研究设计和每名供体的 MV 分类；先确认样本覆盖与 barcode 来源。
- **Fig. 2**：MV 的解剖空间图；同类 ganglion 可跨节段共享克隆。
- **Fig. 3**：三名供体的 bootstrap 树；DRG/SG 身份比左右位置更能解释克隆相似性。
- **Fig. 4**：事件顺序的核心定量证据；比较 DRG/SG 与左/右 AF 差异及祖细胞规模。
- **Fig. 5**：单核系统树、置换检验、鹌鹑活体迁移和 FGF 干预。

这些描述来自对 `paper.pdf` 主图页面的直接检查，而不是只复述图注；逐 panel 证据见 `figure_analysis.md`。

### 能复现到什么程度

代码快照很好地覆盖了超几何祖细胞模拟、bootstrap 聚类、单核置换、若干 QC 与 MV caller 工作流；核心 R/Python/shell 行可以直接核对。它不能一键从原始数据复现整篇论文：WGS 的 BWA/SAMBAMBA/GATK 预处理、最终 MPAS AF 矩阵生成、DARLIN 外部工具、ResolveOME 平台和部分 notebook 环境仍需额外资源。

因此最稳妥的结论是：**多物种、多记录系统的证据一致支持早期命运偏置/指定；MVBA 给出事件顺序的定量谱系推断，但其祖细胞数依赖二倍体、单起源变异和抽样模型等假设。**

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## summary.md — Developmental organization of sensory and sympathetic ganglia

**Paper**: Developmental organization of sensory and sympathetic ganglia
**Authors**: Keng Ioi Vong, Yanina D. Álvarez, Qingquan Zhang, et al. (Xiaoxu Yang & Joseph G. Gleeson)
**Journal**: Nature (2026)
**DOI**: 10.1038/s41586-026-10313-0
**Code**: https://github.com/shishenyxx/Human_DRG_SG

---

### Motivation & Novelty

**Biological problem**: The neural crest (NC) generates both sensory (dorsal root ganglia, DRG) and sympathetic ganglia (SG) from a common progenitor pool. A decades-long debate in developmental biology has centred on whether delaminating NC cells are multipotent — capable of generating both DRG and SG depending on local signals — or are already fate-specified before they leave the neural tube. Resolving this determines the conceptual framework for understanding neurocristopathies (including neuroblastoma) and how the peripheral nervous system is patterned.

**Why existing methods fall short**: Conventional lineage tracing relied on dye labelling (*Dev. Biol.*, 1963; *Development*, 1989), viral tracing, or fluorescent reporters (Confetti). These methods inject or label spatially mixed cell populations, making it impossible to distinguish clonal origins from proximity effects. Moreover, they typically analyze a single axial level and cannot detect rostrocaudal clonal spread across multiple spinal segments. Chick-quail chimera experiments have produced contradictory conclusions (*Cell Stem Cell* 2015; *Neuron* 1989; *Nature* 1988 vs. *Development* 1997, 2010) depending on whether cells were assessed in ovo vs. transplant contexts.

**Unique contributions**:
1. **MVBA applied to the peripheral nervous system**: Naturally occurring somatic mosaic variants (MVs) in human post-mortem donors are used as permanent, universal lineage barcodes — no transgenic manipulation, applicable to humans, stable across a lifetime.
2. **Pan-axial sampling**: The study covers all 94 DRG and 93 SG from cervical to lumbar levels in three donors — far broader than any prior single-animal fate-mapping experiment.
3. **Pre-delamination fate specification demonstrated quantitatively**: By comparing population size estimates at DRG/SG fate split vs. left/right split (via hypergeometric simulation), the authors show that NC fate is specified when the progenitor pool is significantly smaller — i.e., before the left-right commitment that occurs at delamination.
4. **FGF-dependent rostrocaudal migration discovered**: Live imaging in quail embryos identifies that NC cells migrate along the rostrocaudal axis within the neural tube before delamination, and this migration requires FGF signalling. Blocking FGF receptors redirects NC cells to delaminate laterally instead.

---

### Method Overview

The paper applies **Mosaic Variant Barcode Analysis (MVBA)** — a lineage tracing method first validated in the brain (Breuss et al., *Nature* 2022; Chung et al., *Nature* 2024) — to peripheral ganglia.

**Human MVBA workflow**:
1. Post-mortem dissection of DRG and SG (cervical to lumbar, bilateral) + peripheral organs from 3 neurotypical donors
2. 300× WGS of organ biopsies → somatic MV discovery (4-caller ensemble: MosaicHunter, Mutect2+DeepMosaic, Mutect2+MosaicForecast, Mutect2+Strelka2)
3. 30× WGS of individual ganglia for local clone confirmation
4. Custom AmpliSeq panels per donor → >500× MPAS validation in all tissues
5. √(AF) matrix → Manhattan distance hierarchical clustering + 10,000-replicate bootstrap
6. Population size modelling: hypergeometric simulation to estimate maximum progenitor pool at DRG/SG vs. left/right split

**Mouse validation**: Two CRISPR barcoding systems used orthogonally:
- Homing CRISPR (Sox10-Cre × ROSA26-Cas9 × MARC1-PB7), assayed at 1 month
- DARLIN (doxycycline-inducible Cas9 at E8.5), assayed at E14.5

**Single-cell resolution**: ResolveOME single-nucleus simultaneous genomic + transcriptomic amplification in 224 nuclei from T2/T3 DRG/SG of donor ID07; phylogenetic tree + permutation test.

**Mouse NC scRNA-seq**: Wnt1-Cre;TdTomato sorted cells at E8.5, E9.0, E9.5; scVelo RNA velocity to identify fate-biased transcription factor kinetics.

**Live imaging**: Quail embryos electroporated with Pax7enh-H2B-Citrine; 6-hour time-lapse at HH9; FGF receptor inhibition (infigratinib) to test rostrocaudal migration mechanism.

---

### Evaluation

#### Datasets
- 3 human post-mortem donors: ID06 (70M), ID07 (85M), ID08 (74F)
- 94 DRG + 93 SG total; 827 / 252 / 511 validated MVs per donor
- Mouse: Sox10-Cre Homing CRISPR (n=2 experiments, 1-month mice); DARLIN (E8.5 injection, E14.5 dissection)
- scRNA-seq: 16,115 mouse NC cells from E8.5–E9.5 (Wnt1-Cre;TdTomato)
- Quail: n=6 embryos (imaging), n=4+4 (FGFi vs DMSO)
- SRA accession: PRJNA799597

#### Key quantitative results
| Experiment | Result |
|---|---|
| Human: MVs enriched in DRG or SG | 30.8% (ID06), 37.4% (ID07), lower in ID08 |
| Hierarchical clustering stability | 16 of 18 bootstrap-significant pairs = same ganglion type |
| DV variance > RC variance | All 3 donors significant: p=0.015 (ID06), p<2.2×10⁻¹⁶ (ID07), p=0.0075 (ID08) |
| Population at DRG/SG < population at L/R split | Significant for ID07 and ID08 (Mann-Whitney U p<0.001); modest for ID06 |
| Mouse CRISPR: DRG/SG independent clades | Largest clade = 27 SG, zero DRG |
| Single-cell: T3-DRG:T3-SG pairs | Significantly less frequent than chance (p=0.0427) |
| Single-cell: T3-SG:T3-SG pairs | Significantly more frequent than chance (p=0.0011) |
| Quail FGF inhibition | Rostrocaudal migration: 19.35% (DMSO) → 1.35% (FGFi), p=0.0129 |
| Quail midline crossing | ~20% of NC cells cross the midline before delamination (n=5 embryos) |
| scRNA-seq: fate-biased TFs | Sensory: Oncut1 (p=3.6×10⁻³ at E8.5, p=5.9×10⁻⁴ at E9.5); Sympathetic: Rfx4 (p=7.7×10⁻⁶⁴ at E8.5) |

---

### Reproducibility

**Rating: 3.5/5**

**Strengths**:
- All analysis code deposited on GitHub (https://github.com/shishenyxx/Human_DRG_SG) with clear module structure
- Raw sequencing data available through SRA (PRJNA799597)
- Bootstrap seed hardcoded (set.seed(123)) — fully reproducible
- Snakemake pipeline for somatic variant calling is well-structured with YAML config
- Sample sizes, statistical tests, and p-values clearly reported throughout

**Limitations / practical notes**:
- The code requires pre-processed input CSV files (variant × sample AF matrices) as input; the upstream scripts that generate these from MPAS output are not provided — a significant reproducibility gap for the primary data
- WGS pre-processing (BWA → SAMBAMBA → GATK BQSR) is documented in Methods but not scripted in the repository
- DARLIN barcode counting depends on external tools from the Li et al. 2023 paper (not included in repo)
- Mouse scRNA-seq analysis is in a single large Jupyter notebook (`NC_scRNAseq_analysis.ipynb`) without modular functions
- snMPAS analysis requires the ResolveOME commercial platform (BioSkryb Genomics)
- Population simulation code has undocumented discrepancy: paper says "step 10, range 0-10,000" but code uses `seq(5, 5000, by=5)`

**To reproduce the main findings**:
1. Download PRJNA799597 from SRA
2. Run BWA + SAMBAMBA + GATK BQSR (from Methods) to generate processed BAMs
3. Run `Pipelines/MuTect2_Strelka2/Snakefile` for somatic variant calling
4. Generate AF matrix from MPAS data (upstream scripts not provided — key gap)
5. Run `Analysis/bootstrap/bootstrap.R` and `Analysis/Simulate_starting_population/Start_population_simulation.R`
6. Mouse data: obtain DARLIN barcoding tools from Westlake (Li et al. 2023 protocol)

---

### Clinical Relevance

The revised developmental model has implications for **neuroblastoma** — a tumour arising from the sympathoadrenal NC lineage. If NC fate specification occurs in the neural tube before delamination, tumorigenic driver mutations could be acquired during early neural tube stages, suggesting that neuroblastoma's developmental origin is earlier than the classical sympathoadrenal progenitor stage. This may explain why neuroblastoma driver mutations are sometimes found bilaterally and at multiple axial levels.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
