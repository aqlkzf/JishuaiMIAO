---
layout: default
permalink: /paper-atlas/mousecortex-multimodal-atlas-192d5834/
title: "MouseCortex-Multimodal-Atlas"
nav: false
description: "E14.5 小鼠皮层正处于神经发生中期：神经干细胞（NSC）产生中间祖细胞（IPC），再分化为不同成熟程度的投射神经元（PN）。论文关心的核心不是“哪些基因随分化变化”，而是调控事件的先后和因果关系：远端增强子何时开放、它连接哪个基因、转录因子结合后是否同时改变 DNA 甲基化与三维接触，以及这些候选元件在活体中能否真正驱动表达。 为此，研究组合了五类证据：scRNA-seq 描述表达轨迹；"
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
      <span>Nature Neuroscience · 2022</span>
    </div>
    <h1>MouseCortex-Multimodal-Atlas</h1>
    <p>Multimodal profiling of the transcriptional regulatory landscape of the developing mouse cortex identifies Neurog2 as a key epigenome remodeler</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41593-021-01002-4" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 发育小鼠皮层多模态调控图谱：从增强子时序到 Neurog2 因果验证

### 1. 论文试图连接的不是两张图，而是五层调控证据

E14.5 小鼠皮层正处于神经发生中期：神经干细胞（NSC）产生中间祖细胞（IPC），再分化为不同成熟程度的投射神经元（PN）。论文关心的核心不是“哪些基因随分化变化”，而是调控事件的先后和因果关系：远端增强子何时开放、它连接哪个基因、转录因子结合后是否同时改变 DNA 甲基化与三维接触，以及这些候选元件在活体中能否真正驱动表达。

为此，研究组合了五类证据：scRNA-seq 描述表达轨迹；scATAC-seq 描述开放染色质和 motif 活性；体内 immunoMPRA 检验候选调控元件；Methyl-HiC 同时读取染色质接触和 CpG 甲基化；Neurog2 体内过表达则检验一个候选转录因子是否足以重塑多层表观基因组。八张主图从“细胞状态”逐步推进到“候选增强子”“三维结构”与“因果扰动”。

### 2. 先独立建立 RNA 与 ATAC 的发育坐标

scRNA-seq 得到 11 个主要群体。RNA velocity 给出局部状态变化方向，Monocle3 把 NSC→IPC→PN 排成连续伪时间。这里的伪时间是转录状态的相对顺序，不是胚胎的真实分钟数。直接代码显示 RNA 数据经过变异基因选择、PCA、Harmony、Louvain 聚类和 UMAP；最终聚类参数为 `resolution=0.3, n.start=100, n.iter=500`，UMAP 为 `min.dist=0.5, spread=1, n.epochs=500`（`seurat2-UMAP.R:129-140`）。

scATAC-seq 独立得到 7 个群体。处理先以 5 kb bins 建立初始结构，再在统一峰集上挑选 25,000 个高变峰，进行 TF-IDF、SVD、Harmony、Louvain 与 UMAP（`signac4-peakNormalization.R:58-59,85-111`）。ChromVAR 用 motif 的实际可及性与 GC 匹配背景比较，得到每个细胞的 motif deviation；因此它回答“含某 motif 的区域是否异常开放”，并不直接等于该 TF 已结合或具备因果作用。

Figure 1–2 的重要信息是：表达与开放染色质都沿 NSC→IPC→PN 连续变化，但远端顺式调控元件比启动子更具细胞类型特异性。这为后面用远端峰寻找增强子提供了依据。

### 3. 怎样把一个 ATAC 峰连接到一个基因

作者先用 Seurat CCA 做 RNA–ATAC 标签转移，再用 Cicero 的近邻分组降低单细胞稀疏性。最终形成 4,892 个 ATAC 聚合组，每组约 50 个相近细胞，并根据跨模态近邻得到匹配的 RNA 聚合表达。代码额外只保留 CCA 相关性至少 0.5 的匹配（`scRNA_scATAC_Integration_02_Create_Aggregate_scATAC_scRNA.R:62-83`）。

对每个距任意 TSS 至少 5 kb、且位于候选基因 500 kb 范围内的峰 $p$ 与基因 $g$，计算：

$$r_{p,g}=\operatorname{cor}(A_{p,1:K},R_{g,1:K}),$$

其中 $K=4,892$，$A$ 是聚合开放度，$R$ 是聚合表达。代码在相关前使用

$$\log_2\left(\frac{\operatorname{CPM}(x)}{100}+1\right),$$

并设置 `associationWindow=±500 kb`、`corCutOff=0.35`、`fdrCutOff=0.1`、`distCutOff=5000`（`scRNA_scATAC_Integration_03_Compute_Peak_to_Gene_links.R:215-224`）。

FDR 的背景不是简单打乱细胞，而是用不同染色体上的峰–基因相关构造 trans-null。这样能保留测序深度和细胞状态造成的背景相关，但它仍假设跨染色体关系可代表无顺式调控的零分布。最终得到 16,978 个正相关增强子–基因对（EGP）。这表示两者沿发育状态共同变化，并非单凭相关就证明增强子直接调控该基因；Hi-C 重叠、MPRA 和后续扰动才逐步增强证据。

### 4. dPD 如何区分“预先开放”与“同步开放”

作者把 RNA 与 ATAC 放入同一伪时间坐标，对每个增强子开放度和基因表达分别拟合 GAM：

$$\hat f(\tau)=\operatorname{GAM}\bigl(x\sim s(\tau,\mathrm{bs}="cs")\bigr),$$

使用 REML 选平滑强度，再把每条曲线缩放到 0–1（`scRNA_scATAC_Integration_05_P2G_monocle.R:223-225`）。对一个 EGP 定义

$$\mathrm{dPD}=\tau^*_{enhancer}-\tau^*_{gene},$$

其中 $\tau^*$ 是平滑曲线达到最大值的伪时间。dPD<0 表示增强子开放峰先于基因表达峰；论文将 dPD≤−2 称为 primed，−2<dPD<2 为 immediate，dPD≥2 为 delayed。

Figure 3 显示 IPC、PN1、PN2 这些短暂状态中，许多增强子先开放、随后基因才达到表达峰；Neurog/Eomes/Neurod 等 motif 富集于 primed 元件。这里“先发生”提高了调控解释的可信度，但仍可能由共同上游因子驱动，不能单独推出峰对基因的因果方向。

代码还有一个复现边界：论文说以 NSC 群体为根，实际 Monocle3 调用选择 NSC 列表中的第 173 个细胞（`scRNA_scATAC_Integration_05_P2G_monocle.R:127-129`）。它仍从 NSC 端起始，但重新过滤或排序细胞可能改变这个固定索引。

### 5. immunoMPRA 给候选增强子加入功能检验

研究把 18,000 条 266 bp 序列在 E13.5 皮层中进行子宫内电转，约 24 小时后按细胞类型进行 intracellular immunoFACS，再比较每条序列的 RNA/DNA 报告信号。普通 pooled MPRA 只能说明序列总体活跃；immunoMPRA 则能判断其在 NSC、IPC 或 PN 中是否选择性活跃。

Figure 4 显示正相关 EGP 的候选增强子比随机序列或非相关对更活跃；VISTA forebrain enhancer 提供外部正对照；突变 Neurog2 motif 几乎消除相关 reporter 活性，说明该 motif 对所测序列的活性是必要的。仓库主要包含下游绘图与整合代码，MPRAflow/MPRAnalyse 的完整执行管线在外部，因此这一层不能仅凭本地仓库端到端复跑。

### 6. 三维基因组与甲基化回答“开放之后发生什么”

Methyl-HiC 在分选的 NSC、IPC、PN 中同时测染色质接触和 CpG 甲基化。论文观察到分化过程中 compartment strength 与 TAD insulation 增强，并有 322 个差异绝缘边界；增强子–启动子的接触通常在增强子最活跃的细胞类型中最强。Hi-C 由 Shaman 以 kNN=100 归一化，个体 E–P 对在锚点周围 10 kb 窗口取分数（论文 Methods `paper.md:344-364`；本地整合脚本 `Integration_03:298-310`）。

这部分的限制很实际：脚本依赖 Bonev lab 的 `misha` mm10 track database、外部 Shaman 和 cworld-dekker。仓库记录了分析逻辑，但没有可携带的 trackdb；因此“代码存在”不等于新环境能直接复现 Hi-C 结果。

Figure 5–7 的总体结论不是所有增强子都按同一种方式成环，而是接触强度构成连续谱：有些位点预先成环，有些随细胞类型增强，还有些呈反相关。转录因子 motif 两端同时出现时，接触和表达改变往往更强，提示 TF 可能参与稳定特异的三维相互作用。

### 7. 为什么 Neurog2 过表达比相关图谱更接近因果证据

作者在 E13.5 皮层中体内过表达 Neurog2，24 小时后比较 GFP 对照与 Neurog2 条件的 ATAC、NOMe/Methyl-HiC 和表达。Figure 8 显示 Neurog2 结合位点开放度上升、局部 DNA 去甲基化，并增强 Neurog2 结合区域之间的 intra-TAD 接触；但全局 compartment、TAD 与距离衰减基本不变。

这使“Neurog2 是多层表观基因组 remodeler”比 motif 相关性更强：时间受控的扰动同时改变多个局部层面。不过它证明的是 Neurog2 在该 24 小时体内过表达条件下具有充分性，不等于每个内源发育变化都仅由 Neurog2 驱动。最强的表达上调出现在增强子和启动子两端都有 Neurog2 结合的基因，支持 dual-anchor 模型，但具体的蛋白复合物和直接物理桥接仍需进一步实验。

### 8. 阅读八张主图的最短路径

- Figure 1：scRNA 细胞类型、velocity 与 NSC→IPC→PN 伪时间。
- Figure 2：scATAC 状态、ChromVAR 与远端 CRE 的动态性。
- Figure 3：EGP、dPD 以及 primed/immediate/delayed 增强子。
- Figure 4：体内 immunoMPRA 和 motif 突变的功能检验。
- Figure 5：Methyl-HiC 显示 TAD、compartment 与甲基化重排。
- Figure 6：EGP 与细胞类型特异的三维接触强度。
- Figure 7：TF motif、局部 looping 与甲基化的联合关系。
- Figure 8：Neurog2 体内过表达对开放度、甲基化和局部接触的因果检验。

最稳妥的总结是：论文通过“单细胞相关→时序先后→三维/功能验证→体内扰动”逐步提高调控结论的强度。它的重要贡献不是声称某一种组学能够解释一切，而是明确展示不同证据层各自能排除什么、仍不能证明什么。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## summary.md — MouseCortex-Multimodal-Atlas

### Motivation & Novelty

**Biological problem:** How do multiple epigenetic layers and transcription factors coordinate to drive neural lineage specification in the mammalian cerebral cortex? During development, neural stem cells (NSCs) give rise to intermediate progenitor cells (IPCs) and ultimately projection neurons (PNs), a process requiring cell-type-specific activation of gene regulatory networks (GRNs). The causal relationships between TF binding, chromatin accessibility, DNA methylation, enhancer activity, and chromatin looping — and their temporal ordering — remained unresolved.

**Limitations of existing methods:** Prior to this work:
- Single-cell studies captured either transcription or chromatin accessibility, but not both simultaneously in the same tissue/age with full integration
- Enhancer–gene linkage methods relied on bulk ChIP-seq or in vitro differentiation systems, lacking single-cell, in-vivo resolution (contrast: Bonev et al., *Cell* 2017 — bulk multiscale 3D genome; Song et al., *Nature* 2020 — human cortex bulk 3D epigenomes)
- The causal role of individual TFs in reorganizing multiple epigenome layers simultaneously in vivo had not been demonstrated at scale
- Existing MPRA approaches were done in cultured cells; in vivo cell-type–specific activity had not been systematically assayed

**Unique contributions:**
1. First systematic multimodal atlas combining scRNA-seq + scATAC-seq + in vivo MPRA + Methyl-HiC + ChIP-seq in developing mouse cortex
2. Novel in vivo immunoMPRA approach combining IUE electroporation with intracellular immunoFACS for cell-type–specific enhancer activity measurement
3. Discovery that Neurog2 simultaneously mediates DNA demethylation, chromatin accessibility, and chromatin looping — acting as a multi-layer epigenome remodeler
4. Demonstration that TF binding at *both* enhancer and promoter anchors (dual-anchor model) produces the strongest transcriptional upregulation

---

### Method Overview

The paper integrates five data modalities collected from E14.5 mouse somatosensory cortex:

**Single-cell layer:** scRNA-seq (10x Genomics v3, 11 clusters) and scATAC-seq (10x, 7 clusters) are independently processed with Seurat/Signac, then integrated via Seurat CCA label transfer + Cicero kNN aggregation. Pearson correlation between 4892 pseudo-bulk groups identifies 16,978 positive enhancer–gene pairs (EGPs): r ≥ 0.35, FDR ≤ 0.1, ≥5 kb from TSS, ≤500 kb window. FDR uses a trans-chromosome null distribution.

**Temporal layer:** Pseudotime (Monocle3, NSC-rooted) + GAM cubic-spline smoothing + rescaling enables calculation of the pseudotime difference (dPD = τ_enhancer – τ_gene) for each EGP. Negative dPD indicates enhancer accessibility precedes gene activation.

**3D epigenome layer:** ImmunoFACS-sorted cell populations (NSC/IPC/PN) undergo Methyl-HiC (simultaneous 3D genome + DNA methylation). Hi-C scored using Shaman kNN=100 normalization.

**Functional validation layer:** In vivo immunoMPRA tests 18,000 sequences (266 bp each) in E13.5 IUE cortex, sorted by cell type, analyzed by MPRAflow + MPRAnalyse.

**Causal layer:** Neurog2-IRES-GFP overexpression (IUE 24h) with paired ATAC-seq, Methyl-HiC, NOMe-seq tests sufficiency of Neurog2 for epigenome remodeling.

---

### Evaluation

#### Datasets
| Modality | Cells/Depth | Replicates |
|----------|-------------|------------|
| scRNA-seq | ~6,000 cells/replicate, 2 replicates | 2 bio reps |
| scATAC-seq | ~6,000 cells/replicate, 2 replicates | 2 bio reps |
| Methyl-HiC | NSC/IPC/PN sorted | 3 bio reps each |
| In situ Hi-C | NSC/IPC/PN sorted | pooled replicates |
| MPRA | 18,000 sequences, ~88 barcodes/CRE | 2–3 bio reps |
| Neurog2 OE | ~24h IUE | 3–4 bio reps |

#### Key Results

**EGP validation:**
- 16,978 positively correlated EGPs (r ≥ 0.35, FDR ≤ 0.1)
- 74% overlap with EGPs from 10x Multiome data (external validation)
- Pearson r = 0.63 correlation between single-ome computational and multiome EGP linkage scores
- Positively correlated EGPs: 42.78% overlap with Hi-C chromatin loops vs. 27.75% for control pairs (Fisher's exact test p ≤ 0.00001)
- MPRA: positively correlated enhancers significantly more active than non-correlated (Wilcoxon rank-sum test)

**Temporal dynamics:**
- Enhancer accessibility generally precedes gene expression at transient cell states (IPC, PN1, PN2) — negative median dPD
- Primed enhancers enriched for bHLH (Neurog2, Neurod) and T-box (Eomes, Tbr1) TF motifs
- Meis1 motif specifically enriched in Neurog2-bound primed enhancers (Fig. 3f)

**3D genome:**
- 322 differentially insulated TAD boundaries (~11% of all TADs)
- Increased compartment strength and insulation upon neuronal differentiation
- E–P loop strength highest in cell type where enhancer is most active (Fig. 6a,b)
- Continuous spectrum of interaction strengths — some pre-looped, some anti-correlated

**MPRA:**
- ~95% of sequences recovered, ~88 unique barcodes per enhancer
- VISTA forebrain enhancers: significantly higher MPRA signal (validation)
- NSC enhancers unexpectedly show low pooled MPRA activity (explained by overrepresentation of neurons in IUE-electroporated cells)
- Motif mutagenesis: Neurog2 motif mutation → near-complete abolition of MPRA reporter activity

**Neurog2 gain-of-function (24h):**
- Neurog2 binding sites become more accessible (ATAC, p < 0.01 paired Wilcoxon)
- DNA demethylation specifically at Neurog2-bound regions (NOMe-seq)
- Increased Hi-C contact strength between Neurog2-bound intraTAD pairs (paired t-test, n=3)
- Global 3D topology (TADs, compartments, contact probability) unchanged
- Highest gene upregulation: Neurog2 bound at **both** enhancer and promoter (dual-anchor model)

#### Comparative Analysis
- Compared enhancer definitions: EGP correlation vs. multiome ATAC+RNA → 74% overlap, r=0.63 concordance
- TF motif accessibility (ChromVAR) vs. ChIP-seq-based deviations: highly consistent (Fig. 2c vs. 2d)
- ImmunoMethyl-HiC quality metrics: bisulfite conversion 99.48%, Hi-C reproducibility r ≥ 0.9, methylation r ≥ 0.93 across replicates
- VISTA enhancer validation: sequences overlapping VISTA forebrain database show significantly higher MPRA activity (ED Fig. 6k)

---

### Reproducibility

**Rating: 3/5** — Well-documented but requires proprietary infrastructure.

**Strengths:**
- All raw and processed data available on GEO (GSE155677)
- Code repository includes all analysis scripts (github.com/BonevLab/Noack_et_al_NatNeuro2021)
- Detailed protocols on protocols.io (MPRA pool preparation, immunoFACS, Methyl-HiC)
- Interactive visualization at shiny.bonevlab.com
- Parameters precisely match Methods section (all verified)

**Weaknesses and pitfalls:**
1. **misha trackdb dependency**: The Hi-C and methylation analyses require a proprietary Tanay-lab `misha` genomic track database at `/home/hpc/bonev/trackdb/mm10`. This is not downloadable from GEO — users would need to rebuild it from processed data
2. **Shaman normalization**: Requires the separate `shaman` R package (bitbucket.org/tanaylab/shaman/) and cworld-dekker for compartment analysis — not in the main repo
3. **Fixed root cell**: `root_cell_list[173]` in Monocle3 is a hardcoded cell index — pseudotime ordering may differ if data is reloaded with different cell ordering
4. **External MPRA pipeline**: MPRAflow + MPRAnalyse processing not included in the repo
5. **HPC file paths**: Many hardcoded paths to `/home/hpc/bonev/annotations/` that need to be updated for any new environment
6. **Intermediate RDS files**: The pipeline assumes pre-computed intermediate files (e.g., `results/scATAC/cicero_KNN_Groupings_cds.RDS`) with no regeneration code for early steps

**Environment setup:**
- R packages: Seurat v3.1.5, Signac, Cicero, Monocle3, ChromVAR, Harmony, ArchR, misha, edgeR, mgcv, ComplexHeatmap
- Python: scVelo (RNA velocity), Velocyto
- External tools: CellRanger v3.1.0, CellRanger-ATAC v1.2.0, MACS2, bismark, MethylDackel, JuiceMe/Juicer
- GEO accession: GSE155677

**Common pitfalls:**
- Ensure all proxy variables are unset when downloading from GEO
- The scATAC pipeline requires running MACS2 externally; the code generates shell scripts for this
- ChromVAR requires JASPAR 2020 with manually added JASPAR 2018 entries (see Methods)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
