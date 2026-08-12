---
layout: default
permalink: /paper-atlas/ptsdsndlpfc-3a5ca6ed/
title: "PTSDsnDLPFC"
nav: false
description: "这篇工作研究创伤后应激障碍（PTSD）背外侧前额叶皮层（DLPFC）中，哪些细胞类型、表达程序、染色质调控关系和细胞间信号发生了变化，以及这些变化能否与 PTSD 遗传风险位点连接起来。它不是单一的“差异表达研究”，而是把四类测量放在同一框架中：单核 RNA 测序描述转录状态，单核 ATAC 测序描述染色质可及性，单核 multiome 在同一细胞核中连接 RNA 与 ATAC，Xenium 空间转录组验证候选信号在组织中的位置。"
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
      <span>Nature · 2025</span>
    </div>
    <h1>PTSDsnDLPFC</h1>
    <p>Single-cell transcriptomic and chromatin dynamics of the human brain in PTSD</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-025-09083-y" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PTSDsnDLPFC：从人脑单核图谱到调控元件和风险位点的多模态证据链

### 1. 这项研究真正要回答什么

这篇工作研究创伤后应激障碍（PTSD）背外侧前额叶皮层（DLPFC）中，哪些细胞类型、表达程序、染色质调控关系和细胞间信号发生了变化，以及这些变化能否与 PTSD 遗传风险位点连接起来。它不是单一的“差异表达研究”，而是把四类测量放在同一框架中：单核 RNA 测序描述转录状态，单核 ATAC 测序描述染色质可及性，单核 multiome 在同一细胞核中连接 RNA 与 ATAC，Xenium 空间转录组验证候选信号在组织中的位置。

研究共纳入 111 名供体：36 名 PTSD、36 名重度抑郁障碍（MDD）和 39 名对照。四种数据合计超过 200 万个细胞核或空间细胞，包括 935,371 个 snRNA-seq 细胞核、473,033 个 snATAC-seq 细胞核、119,431 个 multiome 细胞核和 523,314 个 Xenium 细胞。不同模态并非都来自全部 111 名供体，因此每项分析的有效样本数应以对应模态为准，而不能把“细胞数”当作独立受试者数。

### 2. 整体分析路线

可以把方法读成六层递进证据：

1. 用 snRNA-seq 建立 DLPFC 细胞类型图谱，并在细胞类型内比较 PTSD、MDD 与对照。
2. 用供体层面的组成模型和伪 bulk 模型，避免把大量细胞误当作大量独立生物学重复。
3. 用 Xenium 检验重点基因和细胞状态是否能在组织切片中复现。
4. 用配体—受体模型提出细胞间通信假设，并对 SST/GABA 轴追加小鼠应激模型和电生理实验。
5. 用 snATAC-seq 与 multiome 把开放染色质峰连接到基因，构建 TF–CRE–gene 调控链。
6. 用 LDSC 和带功能先验的 SuSiE 精细定位，把细胞类型特异调控元件与 PTSD GWAS 风险位点相连。

这是一条逐层缩小候选范围的路线，不是从表达变化直接证明疾病因果机制。

### 3. snRNA-seq：先确定“在哪类细胞中变化”

作者对 snRNA-seq 数据进行质量控制、归一化、批次整合、降维和聚类，再依据经典标记基因标注兴奋性神经元（EXN）、抑制性神经元（IN，包括 SST、PVALB、VIP 等亚型）、少突胶质细胞（OLG）、少突前体细胞（OPC）、星形胶质细胞（AST）、小胶质细胞（MG）和内皮细胞（END）等主要群体。图 1 的 UMAP 展示的是这些转录状态在低维空间的分离，不等于皮层中的真实空间位置。

差异表达并非只依赖一种检验。论文并行使用细胞层面的 MAST、Wilcoxon 检验，以及供体伪 bulk 层面的 edgeR、DESeq2。公开脚本中的 MAST 模型可写成：

$$
Y_{gic} \sim \beta_0 + \beta_1\,\mathrm{condition}_i +
\beta_2\,\mathrm{CDR}_{ic} + \beta_3\,\mathrm{age}_i +
\beta_4\,\mathrm{PMI}_i + \beta_5\,\mathrm{RIN}_i +
\beta_6\,\mathrm{sex}_i + \beta_7\,\mathrm{race}_i,
$$

其中 $Y_{gic}$ 是供体 $i$ 的细胞 $c$ 中基因 $g$ 的表达，CDR 是单细胞检测率，PMI 是死后间隔，RIN 是 RNA 完整性。脚本仅分析至少在 5% 细胞中检测到的基因，并采用 FDR < 0.01、效应量绝对值大于 $\log_2(1.2)$ 的阈值。MAST 和 Wilcoxon 的“共识差异基因”用于获得更稳健的细胞层候选；伪 bulk 方法则先在供体和细胞类型内汇总计数，把供体作为生物学重复。

研究报告 1,184 个 PTSD 相关 snDEGs。突出的结果包括 OLG 比例降低、SST 相关信号减弱，以及内皮细胞中 **FKBP5** 强烈上调（论文报告 log2FC = 1.42，FDR = $3.42\times10^{-128}$）。这些数字说明关联强且可重复，但死后横断面数据仍不能确定变化发生在疾病之前还是之后。

### 4. PTSD 与 MDD：共同压力表型和诊断特异性

MDD 组的作用不是简单增加样本量，而是帮助区分 PTSD 特异变化与更一般的抑郁、慢性应激或治疗相关变化。作者比较 PTSD–对照、MDD–对照及 PTSD–MDD 的表达方向与富集通路，并在供体层面分析细胞组成。

细胞组成采用 scCODA 一类的贝叶斯组成模型。由于所有细胞类型比例之和固定为 1，一个群体增加必然使其他群体的相对比例发生变化，因此不能对每类细胞独立做普通检验。组成分析回答的是“相对于参考组成，某类细胞的份额是否改变”，不直接回答绝对细胞数是否减少。代码证据中该分析主要保存在 notebook，而非完整的独立脚本，因此复现时需要额外核对 notebook 的运行顺序和输入对象。

### 5. Xenium：把候选信号放回组织，但不是全转录组重复

Xenium 使用定向的 366 基因面板，在 DLPFC 组织切片上定位 RNA 分子并进行细胞分割和类型映射。它可检查候选信号是否出现在预期细胞类型和皮层区域。例如主图显示 **FKBP5** 阳性信号在组织中的分布，并支持其在血管/内皮相关区域的增强。

这里必须保留一个边界：Xenium 是针对预选基因的空间验证，不是对 snRNA-seq 全转录组结果的无偏重复。面板之外的基因没有被检验；分割误差和细胞类型映射误差也会影响空间计数。

### 6. 细胞间通信：从表达共现到可检验假设

作者使用 CellChat 和 NeuronChat，根据发送细胞中的配体表达、接收细胞中的受体表达及数据库中的已知相互作用，计算细胞类型间潜在通信强度。概念上可写为：

$$
S_{A\rightarrow B}^{(l,r)} = f\bigl(\bar{x}_{A,l},\bar{x}_{B,r},\text{辅因子},\text{数据库规则}\bigr),
$$

其中 $\bar{x}_{A,l}$ 是细胞类型 $A$ 的配体 $l$ 平均表达，$\bar{x}_{B,r}$ 是细胞类型 $B$ 的受体 $r$ 平均表达。$S$ 是模型分数，不是实测的分子流量，也不证明两个细胞在空间上直接接触。

两个工具共同指向 SST 抑制性神经元相关通信下降。作者随后在单一延长应激（SPS）小鼠模型中测量 GABA 能突触电流；图中 SPS 组的 GABA tonic current 低于对照，为“抑制性功能受损”提供独立功能支持。该实验增强了生物学可信度，但小鼠应激模型不能等同于人类 PTSD，且电生理结果不能逐一验证计算模型中的每一条配体—受体边。

### 7. snATAC-seq 与 multiome：从开放峰连接到靶基因

snATAC-seq 通过 Tn5 插入事件测量可及染色质。ArchR 流程使用迭代 LSI 降维、聚类、基因活性评分、伪 bulk peak calling 和细胞类型注释。multiome 在同一细胞核中同时得到 RNA 与 ATAC，使峰可及性与基因表达的相关性不必完全依赖跨样本映射。

对候选峰 $p$ 和附近基因 $g$，peak-to-gene link 的基本量是跨细胞或聚合状态的相关：

$$
r_{pg}=\mathrm{cor}(A_p,E_g),
$$

其中 $A_p$ 为峰可及性，$E_g$ 为基因表达。高相关弧线表示峰可能是该基因的顺式调控元件（CRE），但相关不能单独证明物理接触或调控方向。主图中的基因组轨迹和弧线展示了不同细胞类型的开放峰及其候选靶基因连接。

论文方法写到在约 2 Mb 搜索范围内建立 peak-to-gene 连接；但公开 `ATAC/peak2genelinks.R` 调用 `addPeak2GeneLinks` 时没有显式设置 `maxDist`。因此，“论文中的 2 Mb 参数是否由上游配置或默认值实现”属于代码—论文的部分匹配，不能从该脚本单独确认。

### 8. 条件相关 CRE 和 TF–CRE–gene 网络

作者进一步比较 PTSD 与对照的峰可及性，识别条件相关 CRE，并把三类证据组合起来：

1. 差异或细胞类型特异的开放峰；
2. 峰与基因表达的 peak-to-gene 相关；
3. 峰内转录因子 motif 及 TF 活性证据，如 chromVAR 偏差和 footprinting。

公开 `ATAC/TF_CRE_Gene.R` 先将 motif 匹配与 peak-to-gene 表相交，再保留相关系数大于 0.4、FDR 小于 0.05 的连接，形成 TF–CRE–gene 三元关系。它表达的是“该 TF 可能通过这一开放元件影响该基因”的优先级。motif 相似性、TF 家族共享结合序列以及相关性都可能产生多解，因此这些网络是候选调控图，而不是经过扰动实验确认的有向因果网络。

### 9. 从细胞类型调控元件连接到 PTSD 遗传风险

作者首先用分层 LD score regression（LDSC）检验 PTSD GWAS 遗传力是否富集于特定细胞类型的开放染色质注释。若某类细胞的 CRE 中 SNP 所解释的遗传力高于其覆盖 SNP 数所预期的比例，则提示该细胞类型的调控区域与疾病遗传风险有关。富集不意味着所有该类细胞都异常，也不能定位单个因果变异。

随后在 8 个 GWAS 位点进行 SuSiE 精细定位。SuSiE 将区域效应表示为少量“单效应”之和，并为每个变异计算后验纳入概率（PIP）：

$$
\mathrm{PIP}_j=P(\beta_j\neq 0\mid \hat{\beta},LD,\pi_j),
$$

其中 $LD$ 是连锁不平衡矩阵，$\pi_j$ 是变异先验。代码 `GWAS/Finemap/finemap_susie.R` 同时运行均匀先验和基于 ATAC 注释的功能先验模型，处理等位基因方向、LD 矩阵和数值正则化，并调用 `susie_rss`（代码中 $n=186{,}689$、$L=5$）。主图以 LRFN5 区域为例展示 PIP 与开放染色质/peak-to-gene 证据的叠加。

功能先验会把与相关细胞类型开放染色质重叠的变异排在更前面，但它不会凭空创造信息。PIP 仍依赖 GWAS 统计量、LD 参考、先验构造和模型假设；高 PIP 变异是实验验证优先对象，而非自动成为已证实的因果变异。

### 10. 如何正确串起主要发现

这项研究最强的地方是同一候选可以被不同层级反复观察。例如 FKBP5 先在内皮细胞差异表达中出现，再由空间数据定位；SST/GABA 轴先由人脑表达和通信模型提出，再由小鼠电生理提供功能支持；遗传位点则由 GWAS、细胞类型开放染色质、peak-to-gene 和精细定位共同缩小范围。

正确表述应是：多种独立或互补数据使某些细胞类型和调控通路成为更可信的 PTSD 相关候选。不能表述成：多组学已经证明某个差异基因、通信边或 CRE 导致 PTSD。主要限制包括死后横断面设计、诊断和药物等残余混杂、模态间供体不完全重叠、组成数据的相对性、空间面板的预选择、通信模型缺少直接分子流量测量，以及跨物种功能验证的外推边界。

### 11. 论文与代码复现边界

- **直接对应**：`RNA/MAST_DEG.R` 明确给出 MAST 协变量、基因过滤和显著性阈值；`ATAC/TF_CRE_Gene.R` 明确给出 motif–CRE–gene 拼接及相关/FDR 阈值；`GWAS/Finemap/finemap_susie.R` 明确实现带/不带 ATAC 先验的 SuSiE。
- **部分对应**：peak-to-gene 主流程存在，但公开脚本没有显式实现论文所述的 2 Mb `maxDist`；需要检查保存对象或原始运行环境。
- **notebook 依赖**：细胞组成和细胞通信的重要步骤主要位于 notebook，运行状态、隐藏对象和交互式筛选增加了复现成本。
- **环境依赖**：若干脚本包含硬编码路径或依赖预先生成的 Seurat/ArchR 对象，代码快照不是从原始 FASTQ 一键重建全文结果的封闭流水线。

### 12. 源证据导航

- 论文正文与方法：`paper source/paper/vlm/paper.md`
- 补充材料：`output_paper_supp_md/paper_supp/vlm/paper_supp.md`
- RNA 差异表达：`PTSDsnDLPFC/RNA/MAST_DEG.R`
- peak-to-gene：`PTSDsnDLPFC/ATAC/peak2genelinks.R`
- TF–CRE–gene：`PTSDsnDLPFC/ATAC/TF_CRE_Gene.R`
- GWAS 精细定位：`PTSDsnDLPFC/GWAS/Finemap/finemap_susie.R`
- 图证据逐图说明：`figure_analysis.md`
- 代码—论文匹配和复现说明：`doc_code.md`

阅读这些文件时，应以论文和直接源码为最终证据；本文件负责解释证据链和方法边界，不替代原始结果表、图注或可执行环境。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Single-Cell Transcriptomic and Chromatin Dynamics of the Human Brain in PTSD

### Paper Information

- **Authors**: Ahyeon Hwang, Mario Skarica, Siwei Xu, ... , Jing Zhang, Matthew J. Girgenti
- **Journal**: Nature (2025)
- **DOI**: 10.1038/s41586-025-09083-y
- **Code**: https://github.com/mjgirgenti/PTSDsnDLPFC

---

### Motivation & Novelty

Post-traumatic stress disorder (PTSD) is a polygenic psychiatric disorder (heritability 24-40%) that occurs in 6-8% of the general population after severe trauma. Previous molecular studies of PTSD used bulk tissue or limited single-cell datasets that could not resolve which specific cell types drive disease pathology. Bulk RNA-seq studies (Girgenti et al., *Nat. Neurosci.*, 2020; Logue et al., *Neurobiol. Stress*, 2021) identified altered GABAergic, immune, and glucocorticoid pathways but could not attribute these changes to specific cell types. A smaller single-cell study (Chatzinakos et al., *Am. J. Psychiatry*, 2023; n=10-11 per group) provided initial cell-type-specific data but lacked statistical power. Critically, no study had examined the single-cell chromatin landscape of the PTSD brain, leaving the regulatory mechanisms connecting GWAS risk variants to cell-type-specific gene expression unexplored.

**Unique contributions**:

1. **Scale**: Largest single-cell multi-omic analysis of a human brain subregion in a psychiatric disorder — over 2 million nuclei from 111 post-mortem DLPFC samples (36 PTSD, 36 MDD, 39 control), spanning snRNA-seq (935K), snATAC-seq (473K), snMultiome (119K), and Xenium spatial transcriptomics (523K).

2. **Multi-omic integration**: First study to combine single-cell transcriptomics with single-cell chromatin accessibility in PTSD, enabling identification of cell-type-specific cis-regulatory elements (CREs) and their target genes. This integration links GWAS risk variants to regulatory mechanisms within specific cell types.

3. **SST interneuron vulnerability**: Demonstrates reduced SST interneuron output signaling in PTSD through neurotransmitter-receptor communication analysis, validated by slice electrophysiology in a mouse PTSD model (single prolonged stress).

4. **Endothelial FKBP5 finding**: Unexpectedly shows that the strongest FKBP5 upregulation occurs in endothelial cells rather than neurons, suggesting a neurovascular glucocorticoid mechanism.

5. **GWAS fine-mapping with ATAC priors**: Develops a framework for fine-mapping PTSD GWAS variants using cell-type-specific ATAC peak enrichment scores as informative priors for SuSiE, identifying 8 risk loci with putative causal variants in EXN and IN CREs.

---

### Method Overview

The study employs a multi-modal computational pipeline (see doc_method.md for full details):

**Data generation**: Paired snRNA-seq and snATAC-seq from 111 DLPFC samples, plus 25 snMultiome and 18 Xenium samples from overlapping donors.

**snRNA-seq analysis**: CellRanger → CellBender ambient RNA removal → Scrublet/DoubletDetection → Pegasus clustering with Harmony batch correction → three-level cell-type annotation (7 major types, 14 subtypes, 61 fine subtypes). DEG analysis uses four complementary methods (MAST, Wilcoxon, Nebula, DESeq2 pseudobulk) with consensus snDEGs defined as the MAST-Wilcoxon intersection at |FC|>1.2 and FDR<0.01.

**snATAC-seq analysis**: ArchR pipeline with iterative LSI for dimensionality reduction, MACS2 for peak calling (913,717 union peaks), and peak-to-gene linkage to identify 395,932 CREs (correlation > 0.4, FDR < 0.05).

**Integration and regulatory analysis**: Constrained RNA-ATAC integration identifies regulatory links; chromVAR and TF footprinting reveal TF binding dynamics; TF-CRE-Gene networks map transcriptional regulation.

**CCC analysis**: CellChat for ligand-receptor networks and NeuronChat for neurotransmitter-receptor interactions, with differential analysis via 3D matrix normalization and subtraction.

**GWAS integration**: LDSC heritability partitioning across cell-type-specific ATAC peaks and SuSiE fine-mapping with ATAC enrichment scores as informative priors.

---

### Evaluation

#### Datasets

| Modality | Samples | Nuclei | Genes/Peaks | Conditions |
|----------|---------|--------|------------|------------|
| snRNA-seq | 105 (of 111) | 935,371 | 27,982 genes | CON/MDD/PTSD |
| snATAC-seq | 94 | 473,033 | 913,717 peaks | CON/MDD/PTSD |
| snMultiome | 25 | 119,431 | RNA + ATAC | CON/MDD/PTSD |
| Xenium | 18 | 523,314 | 366 genes | CON/MDD/PTSD |

#### Key Results

- **1,184 PTSD snDEGs** across 7 cell types (MAST ∩ Wilcoxon); 1,918 MDD snDEGs; 57.6% overlap between conditions
- **OLG significant decrease** in PTSD (scCODA, FDR < 0.05)
- **SST IN sender output reduced** (log differential = -0.518), confirmed by electrophysiology
- **FKBP5 log₂FC = 1.42** in endothelial cells (FDR = 3.42×10⁻¹²⁸), validated by Xenium spatial data showing enrichment near blood vessels
- **395,932 CREs** identified; 88.6% of snATAC peaks overlap with bulk brain CREs
- **8 GWAS risk loci** fine-mapped to cell-type-specific CREs; MAD1L1 locus reveals ELFN1 as the putative target gene in INs
- **snRNA-seq vs bulk correlation**: r = 0.69 (PTSD), r = 0.72 (MDD)
- **snRNA-seq vs Xenium correlation**: r = 0.62 (snXenium), r = 0.61 (scXenium)

#### Biological Validations

- *In vivo*: SST IN-to-EXN eIPSC reduction (GABRA5-mediated) confirmed in SPS mice (P = 0.01)
- *In vivo*: GABA tonic current reduction in SPS mice via GABA_B receptors (P = 0.02)
- *In vitro*: EGR2 and SMARCC1 knockdown in iPS cell-derived neurons confirms 27 downstream DEGs
- *Spatial*: FKBP5 spatial enrichment in endothelial cells near blood vessels confirmed by Xenium
- *Cross-study*: 61.4% directional consistency with Chatzinakos et al. PTSD DEGs

---

### Reproducibility

**Rating: 4/5**

**Strengths**:
- All code publicly available on GitHub (https://github.com/mjgirgenti/PTSDsnDLPFC) and Zenodo
- Comprehensive environment.yml specifying all R and Python package versions
- 23 Jupyter notebooks for reproducing all main and supplementary figures
- Detailed Methods section with specific thresholds and parameters for every analysis step
- Count matrices available on Zenodo (https://doi.org/10.5281/zenodo.15186498)

**Weaknesses**:
- Raw sequencing data requires a data use agreement with the National PTSD Brain Bank (restricted access)
- Some analyses (CCC, scCODA) only in notebooks, not in standalone scripts
- Hardcoded file paths throughout scripts reference the Yale HPC cluster
- Six "high-quality" snRNA-seq samples used for RNA-ATAC integration are not identified by sample ID
- Code lacks a unified snakemake/nextflow workflow — scripts are run independently
- No Docker container provided; complex mixed R/Python environment required

**Practical notes**:
- Environment requires both Python 3.9 and R 4.2 in the same conda environment
- ATAC analysis requires ArchR, which has non-trivial installation on some systems
- GWAS fine-mapping requires 1KG reference panel (~8M SNPs) and GWAS summary statistics from MVP (requires dbGaP access)
- GPU required for CellBender (CUDA); total computation is substantial (~weeks on a cluster)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
