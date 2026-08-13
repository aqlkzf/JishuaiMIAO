---
layout: default
permalink: /paper-atlas/heartfailuremultiomics-ad8d05b8/
title: "HeartFailureMultiomics"
nav: false
wide: true
description: "这项工作的价值不在于给出一个最终的单基因答案，而在于建立了一套从“细胞状态—调控元件—三维结构—转录因子网络—遗传变异”逐层收缩候选机制的框架。它非常适合生成可实验验证的心衰调控假设，但增强子、轨迹、GRN 和变异靶基因仍需要功能实验完成最后的因果闭环。"
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
      <span>Atlases &amp; Resources</span>
      <span>Science · 2026</span>
    </div>
    <h1>HeartFailureMultiomics</h1>
    <p>Single-cell multiomics and chromatin structure reveal gene-regulatory dynamics in heart failure</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Xieeeee/FNIH_Heart" target="_blank" rel="noopener noreferrer" aria-label="Open code for HeartFailureMultiomics">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 人类心衰单细胞多组学与三维基因组图谱：方法详解

### 1. 这项研究到底要解决什么问题？

心力衰竭并不是某一种细胞、某一个基因发生变化这么简单。心肌细胞、成纤维细胞、内皮细胞、免疫细胞等会同时改变；而且同一种细胞内部还可能存在“健康—应激中间态—终末疾病态”的连续变化。

传统方法有两个核心盲区：

1. **组织整体测序会混合不同细胞类型。** 一个基因在组织中升高，可能来自某类细胞数量增加，也可能来自单个细胞内表达增强，bulk 数据难以区分。
2. **仅做单细胞 RNA 测序只能看到转录结果。** 它不能直接回答某个基因为什么被激活：是染色质开放、H3K27ac 增加、H3K27me3 解除、增强子接触改变，还是转录因子网络发生了重排。

此外，心衰相关精细定位变异中超过 85% 位于非编码区。要解释这些变异，必须知道它们位于哪类细胞的调控元件中、可能连接哪个靶基因，以及是否改变转录因子结合或染色质可及性。

论文引用了既往的人类心脏单细胞 RNA 图谱、ABC、SCENIC+、scVelo、ChromHMM、LDSC 等方法，但当前主文 Markdown 只保留了文献编号，没有完整期刊和年份信息，因此本文不臆造参考文献的期刊/年份。

### 2. 研究的核心创新

这不是一个单一模型，而是一套“多层调控图谱拼接框架”。研究者对 36 颗成人心脏的四个心腔进行分析，其中包括 13 个非心衰、13 个缺血性心肌病（ICM）和 10 个非缺血性心肌病（NICM）样本，并组合四类信息：

- 10x Multiome：同一细胞核的 RNA 与 ATAC；
- Droplet Paired-Tag：同一细胞核的 RNA 与 H3K27ac 或 H3K27me3；
- Droplet Hi-C：单细胞三维染色质接触；
- 基因分型、全基因组测序和心血管 GWAS/精细定位结果。

最终产物不是简单的细胞聚类，而是一张可以沿下列路径查询的调控图谱：

```text
疾病/细胞状态
  -> 差异表达与差异开放区域
  -> 染色质状态变化
  -> 候选增强子—基因连接
  -> 转录因子调控网络
  -> 三维染色质结构
  -> 非编码风险变异及候选靶基因
```

### 3. 输入、输出和关键对象

#### 输入

- 每个细胞核的 RNA 计数；
- 每个细胞核的 ATAC 片段；
- H3K27ac/H3K27me3 片段；
- Hi-C contact pairs 与不同分辨率的接触矩阵；
- 供体、性别、疾病状态、实验批次和心腔信息；
- GWAS summary statistics、精细定位后验概率和等位基因信息。

#### 输出

- 759,222 个细胞核、12 个主要心脏细胞类型及其亚群；
- 285,873 个候选顺式调控元件（cCRE）；
- active、open、weak、repressive、unknown 五类染色质状态；
- 66,317 对远端 cCRE—启动子连接；
- 心衰相关差异表达、差异可及性、组蛋白修饰和染色质区室变化；
- 心室心肌细胞和成纤维细胞的状态轨迹与 regulon；
- 心血管风险变异的细胞类型、调控元件和候选靶基因注释。

### 4. 从原始数据到统一细胞图谱

#### 4.1 先把混样细胞核分回供体

30 颗心脏按心腔混样以提高通量并降低处理批次差异。之后利用基因型和 demuxlet 将每个细胞核分配回具体供体。这样既能使用混样实验，又能在统计分析中保留“供体”作为真正的生物重复单位。

#### 4.2 Multiome 质量控制

论文保留满足以下条件的细胞核：

- 表达基因数 >500；
- ATAC fragments >1000；
- 线粒体基因比例 <=5%；
- TSS enrichment >=2。

RNA 使用 SoupX 去除环境 RNA，随后用 Seurat/Signac、Harmony 和 WNN 完成初始整合、聚类和注释。ATAC 峰被统一为以 summit 为中心的 300 bp 区域，再构建不重叠参考峰集合。

#### 4.3 Paired-Tag 与 Multiome 的整合

两种技术都含 RNA，因此 RNA 被用作共同坐标系：

1. SCTransform 标准化；
2. 选择 3000 个共享特征；
3. CCA 寻找 integration anchors；
4. PCA 后取前 30 个主成分进行 UMAP 和 Leiden 聚类；
5. 从 Multiome RNA 向 Paired-Tag RNA 转移标签。

主要细胞类型使用 25 个近邻，亚群使用 5 个近邻；最大预测分数分别要求 >=0.9 和 >=0.8。

#### 4.4 把没有 RNA 的 Hi-C 细胞映射到 RNA 图谱

对基因 $i$ 和 Hi-C 细胞 $j$，论文定义单细胞 gene-associating-domain 分数：

$$
R_{ij}=\sum_{b \in \mathrm{geneBody}(i)} C_{bj},
$$

其中 $C_{bj}$ 表示细胞 $j$ 在基因 $i$ 基因体内第 $b$ 个 bin 的接触数。这样得到“细胞 × 基因”的 scGAD 矩阵，把 Hi-C 转换成近似基因活性的表示。

之后使用 RNA 参考数据的 PCA 模型变换 scGAD 特征，再用 CCA 对齐 RNA 与 Hi-C。每个 Hi-C 细胞在 RNA 参考中寻找 15 个最近邻，通过标准化距离权重投票得到细胞类型。

**代码已直接验证：** `01.Heart_Hi-C_embedding.ipynb` 中确实设置 RNA/3C 模态、使用 `k_anchor=15` 和 30 个 CCA 成分，并通过 PyNNDescent 查询 `k=15` 的 RNA 近邻后输出预测标签。

### 5. 如何建立 cCRE 和染色质状态图谱？

#### 5.1 cCRE 模块

研究对不同细胞类型的聚合 ATAC 信号进行迭代 peak calling，得到 285,873 个 cCRE，占基因组 2.82%。随后用非负矩阵分解（nNMF）将 cCRE 分为 11 个模块：10 个细胞类型富集模块和一个以持续开放启动子为主的 M0 模块。

再通过似然比检验和 specificity score，在经验 FDR <0.05 下识别 20,267 个细胞类型特异 cCRE。

#### 5.2 五状态 ChromHMM

ChromHMM 同时使用 ATAC、H3K27ac 和 H3K27me3。作者比较 2–8 个状态的模型，并用两个标准选择状态数：

1. emission profile 的聚类分离度达到最大值 95% 时，选择最小状态数；
2. 简化模型相对 8 状态模型的中位相关性达到平台。

最终得到五个状态：

| 状态 | 主要信号 | 生物学解释 |
|---|---|---|
| Active | ATAC、H3K27ac 高 | 活跃调控区域 |
| Open | ATAC 高、H3K27ac 较低 | 开放但未必强激活 |
| Repressive | H3K27me3 高 | 抑制状态 |
| Weak | 整体信号弱但更接近基因/启动子 | 弱注释状态 |
| Unknown | 三种信号均较少 | 当前标记组合无法分类 |

这里要注意：状态名称是根据 emission 和基因组重叠人工解释的。因为只用了三类表观标记，它不能与包含更多组蛋白标记的 ENCODE 状态一一等价。

### 6. 如何寻找心衰相关变化？

RNA、ATAC 和组蛋白修饰先按供体聚合成 pseudobulk，再用 DESeq2 比较 HF 与非 HF。论文方法写明模型考虑性别和实验批次，并过滤总计数 <10 的特征。

主要结果包括：

- 10,400 个差异表达基因；
- 52,738 个差异可及 cCRE；
- 37,924 个 H3K27me3 降低区域。

心衰中上调的 cCRE 往往从 open 转为 active，而下调 cCRE 则失去 active/open 状态。这说明疾病变化不只是“峰高变了”，还包括调控元件功能状态转换。

**代码与论文的差异：**直接检查的 RNA 和 ATAC DESeq2 notebook 使用 `~ Sex + HF_status`，没有包含论文所写的实验批次项。因此这些 notebook 是 **Partial** 对应，而不是完全一致的实现。

### 7. ABC 如何连接增强子和基因？

论文给出的 ABC 输入是：

- 10 kb 分辨率的插补 Hi-C 接触矩阵；
- 候选增强子上的 H3K27ac 信号；
- 对应细胞类型的 ATAC consensus peaks。

ABC score >=0.02 的连接被保留。研究报告 66,317 对远端 cCRE—启动子连接，其中 11,938 对具有细胞类型特异性。

但必须保留一个关键缺口：

> **当前代码快照中没有找到 ABC score 的计算代码，也没有找到执行 `>=0.02` 过滤的源代码。**

`GRN_analysis.ipynb` 读取的是已经生成的 `abc` 表，再把其中的 `CellType`、`range`、`TargetGene` 与 RNA/ATAC 的 log2 fold change 合并，用于差异连接、BEDPE 和 APA 分析。因此，下游使用可以验证，ABC 推断本身不能验证。

### 8. 如何推断调控网络和疾病轨迹？

#### SCENIC+

每个主要细胞类型最多取 10,000 个细胞，依次完成：

1. 候选增强子识别；
2. TF motif 富集；
3. TF—增强子—靶基因连接。

regulon 用 RSS 衡量亚群特异性，用 degree centrality 表示网络连接程度。代码中的 GRN notebook 会读取预计算的 `edges_R2G.csv`，构建 TF 靶区域/靶基因集合，并结合差异结果运行 fgsea；但完整 SCENIC+ 训练过程依赖外部结果目录。

#### scVelo

scVelo 使用 spliced/unspliced counts，通过 30 个 PC 和 50 个近邻估计动力学、velocity graph 和 latent time。论文据此提出：

- vCM1–vCM3 偏非心衰；
- vCM4–vCM5 是应激/中间状态；
- vCM6–vCM7 偏终末心衰；
- 成纤维细胞从中间态分叉到 FB6 activated fibroblast 或 FB7 myofibroblast。

这些轨迹是横断面数据上的方向推断，不是同一细胞的纵向追踪，因此应理解为“候选状态进程”。

### 9. 三维基因组分析

scHiCluster 在不同分辨率承担不同任务：

- 100 kb：A/B compartment；
- 25 kb：domain 和 insulation；
- 10 kb：细胞嵌入和 loop/局部接触。

论文识别出 5221 个发生 compartment switching 的 bin。心肌细胞和成纤维细胞出现更多 A->B 转换和更弱的 A-A 相互作用；vCM 在非活跃 B compartment 中增加长距离相互作用，同时在活跃区室中损失短距离相互作用。

代码快照中可以看到 BWA、Pairtools、cooler、scHiCluster compartment/domain 和差异区室统计，但脚本引用实验室绝对路径和外部 helper，无法直接独立运行。

### 10. 如何把 GWAS 变异映射到靶基因？

#### LDSC

77 个心血管性状经过 MAF >=0.01、HapMap3 对齐和标准化后，使用 partitioned LDSC 检验不同细胞类型 cCRE 的遗传力富集。结果以 FDR <0.1 过滤，再用 rank=6 的 nNMF 重复 50 次组织细胞类型—性状模式。

#### 精细定位与功能注释

Wakefield approximate Bayes factor 生成变异后验概率；累计后验概率达到 0.95 的最小集合形成 credible set。之后将变异与以下证据连接：

- 细胞类型 cCRE 与染色质状态；
- ABC、共可及性和 Hi-C loop；
- SCENIC+ GRN；
- 差异 ATAC；
- ChromBPNet 的等位基因可及性预测；
- motifbreakR 的 motif 破坏预测。

论文发现 80 个已知 DCM loci 中有 62 个与心脏 cCRE 重叠，其中 58/62 与心肌细胞特异 cCRE 重叠。vCM5 应激网络的遗传风险最突出。rs13277721—`TRAPPC9` 是一个典型候选：变异位于活跃远端 cCRE，Hi-C 支持远程接触，模型预测风险等位基因破坏 AP-2alpha motif 并降低可及性。

这仍是优先级排序，不是因果证明。真正验证需要等位基因编辑、增强子扰动、CRISPRi/a 或报告基因实验。

### 11. 怎样理解最重要的生物学结论？

1. **心衰是多层调控系统同时失衡。** RNA、ATAC、H3K27ac/H3K27me3、增强子连接和三维结构发生协调变化。
2. **心肌细胞和成纤维细胞是重塑最显著的两类细胞。** 前者表现为身份丢失、应激网络和 NPPA/NPPB 等疾病程序激活；后者出现 activated fibroblast 与 myofibroblast 两条分支。
3. **中间态可能是重要干预窗口。** vCM5 和 FB4 具有高度连接的 FOS/JUN/ATF 等应激调控网络，可能位于稳态向终末疾病态转变的关键位置。
4. **遗传风险主要落在细胞类型特异的活跃调控元件上。** DCM 风险尤其集中于心肌细胞 cCRE，而不是平均分布于整个心脏组织。

### 12. 代码可复现性与已知缺口

代码仓库：`FNIH_Heart`，快照提交为 `48bfde55f2b83b6707339b341e1284a8a70eeb2e`。

总体代码—论文一致性为 **medium**：

- **Exact：**Hi-C/RNA 的 CCA 与 15 近邻标签转移；
- **Partial：**RNA/ATAC DESeq2、Hi-C 预处理与区室分析；
- **Notebook：**ABC 下游、SCENIC+ 结果分析、LDSC/精细定位；
- **Not found：**ABC score 计算与 >=0.02 过滤代码。

主要复现障碍：

- Science 补充材料下载被 403/HTML challenge 阻止，`SUPP_MD` 不存在；
- notebook 依赖机构内部数据路径、参考矩阵、barcode 表、SCENIC+ edges、APA 矩阵和外部脚本；
- CodeGraph 只索引了 3 个 R 文件，不包含 notebook；
- 仓库没有完整锁定的端到端环境和统一运行入口。

因此，这个仓库适合审计论文流程、查看图表生成逻辑和复用局部 notebook，但不能在没有外部数据与路径重构的情况下“一键复现”整张图谱。

### 13. 最后一句话

这项工作的价值不在于给出一个最终的单基因答案，而在于建立了一套从“细胞状态—调控元件—三维结构—转录因子网络—遗传变异”逐层收缩候选机制的框架。它非常适合生成可实验验证的心衰调控假设，但增强子、轨迹、GRN 和变异靶基因仍需要功能实验完成最后的因果闭环。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Single-cell multiomics and chromatin structure in heart failure

### Problem

Heart failure is the endpoint of diverse cardiac diseases, but the regulatory events that move individual cardiac cell types from adaptive stress responses into maladaptive remodeling are incompletely understood. Bulk assays mix cardiomyocytes, fibroblasts, endothelial, immune, and other lineages, while transcriptome-only single-cell studies do not directly identify the regulatory elements, histone states, or 3D contacts that may drive expression changes. This is especially limiting for genetic interpretation because more than 85% of fine-mapped cardiovascular-risk variants are noncoding (`paper.md:50-56`).

### What the study contributes

The paper presents a cell-type-resolved human heart-failure atlas built from 36 hearts and all four cardiac chambers. It combines:

- 10x Multiome RNA + ATAC;
- Droplet Paired-Tag RNA + H3K27ac/H3K27me3;
- Droplet Hi-C chromatin contacts;
- genotype/WGS data and cardiovascular GWAS fine mapping.

RNA or gene-activity representations anchor cross-modality integration, producing a unified map of 759,222 nuclei across 12 major cardiac cell types. The authors then identify cCREs, assign chromatin states, perform subject-level disease contrasts, infer enhancer–gene links and GRNs, analyze chromatin compartments/domains, reconstruct cardiomyocyte and fibroblast state trajectories, and project inherited risk variants onto cell-type regulatory networks.

### High-level method

The computational workflow is a sequence of linked atlases rather than one model:

```text
multi-assay nuclei
  -> QC + genotype demultiplexing
  -> RNA/scGAD-anchored cross-modality integration
  -> cell types and subpopulations
  -> cCRE modules + five ChromHMM states
  -> donor-level HF versus non-HF differential analysis
  -> ABC enhancer-gene links + SCENIC+ regulons
  -> scVelo state trajectories + Hi-C compartments/domains
  -> LDSC/fine mapping/ChromBPNet variant prioritization
```

Important choices include 10-kb Hi-C input and H3K27ac activity for ABC links, retaining ABC scores >=0.02; a five-state ChromHMM model from ATAC, H3K27ac, and H3K27me3; subject-level DESeq2 pseudobulk tests; SCENIC+ GRNs for each major cell type; and 100-, 25-, and 10-kb Hi-C resolutions for compartments, domains, and embedding/loops, respectively.

### Main results

1. **Large integrated atlas.** The study resolves 759,222 nuclei, including 329,255 pooled Multiome, 243,008 unpooled Multiome, 57,379 Droplet Hi-C, 67,453 H3K27ac, and 62,127 H3K27me3 nuclei. Cross-modality maps recover compatible major cardiac lineages.

2. **Expanded regulatory-element catalog.** Iterative peak calling identifies 285,873 cCREs covering 2.82% of the genome, including 49,848 previously uncharacterized elements. nNMF yields 11 accessibility modules, and ChromHMM assigns active, open, weak, repressive, or unknown states. The ABC analysis reports 66,317 distal cCRE-promoter pairs, including 11,938 cell-type-specific pairs.

3. **Widespread HF remodeling.** Subject-level contrasts identify 10,400 differentially expressed genes, 52,738 differentially accessible cCREs, and 37,924 regions with reduced H3K27me3. Cardiomyocytes and fibroblasts show the strongest multi-layer changes. HF-up cCREs tend to move from open to active states, while down-regulated elements lose active/open states.

4. **3D genome disruption.** Droplet Hi-C analysis identifies 5221 bins with compartment switching. Cardiomyocytes and fibroblasts show more A-to-B switching and reduced A-A interactions; vCMs gain long-range interactions in inactive compartments while losing short-range active-compartment interactions.

5. **Disease-state continua.** Seven ventricular cardiomyocyte states span non-HF-enriched, intermediate stress-response, and HF-enriched programs. vCM5 is a highly connected intermediate state enriched for FOS/JUN/ATF-related stress programs and DCM risk. Fibroblast trajectories branch toward FB6 activated fibroblasts and FB7 myofibroblasts, implicating RUNX1/RUNX2 and MEF2/TEAD regulatory programs.

6. **Genetic-risk localization.** Of 80 known DCM loci, 62 overlap a cardiac cCRE; 58 of these 62 overlap cardiomyocyte-specific cCREs. Combining fine mapping, ABC, coaccessibility, Hi-C, ChromBPNet, and motif predictions prioritizes candidate target genes, including a proposed rs13277721-to-`TRAPPC9` long-range link.

### How convincing is the evidence?

The strongest evidence is convergent and descriptive: the main figures visibly align cell identity with RNA, accessibility, histone states, local contacts, and disease-associated changes. Cardiomyocyte/fibroblast remodeling and concentration of DCM risk in cardiomyocyte cCREs are supported across multiple analyses.

The more mechanistic conclusions remain hypotheses. RNA velocity does not longitudinally observe transitions; SCENIC+ edges are inferred; ABC links are predicted enhancer–gene pairs; and fine-mapped variant-to-gene connections require perturbation or allele-specific validation. Method disagreement in the genetic figure is an explicit reminder that target assignment is uncertain.

### Reproducibility and code–paper match

**Rating: 3/5 — substantial analysis code, but not a self-contained reproduction.**

- Paper-linked code: `https://github.com/Xieeeee/FNIH_Heart`, snapshot commit `48bfde55f2b83b6707339b341e1284a8a70eeb2e`.
- Data: raw sequence/genotyping data are reported at dbGaP accession `phs004650`; processed data and tables are reported on Zenodo; processed tracks are available through the HeartEpigenome browser.
- Code fidelity: **medium**. The repository covers modality preprocessing, cross-modality integration, cCRE/DESeq2 analysis, GRNs, Hi-C, LDSC, and fine mapping. The CCA/15-neighbor Hi-C annotation path is directly matched to the paper.
- Verified difference: inspected RNA and ATAC DESeq2 notebooks use `~ Sex + HF_status`, whereas the paper states sex and experimental batch covariates.
- Missing implementation: source that computes ABC scores and applies the >=0.02 filter was not located; the GRN notebook consumes a precomputed `abc` table.
- Execution barrier: many notebooks and scripts use external institutional paths for data, genome references, helper scripts, SCENIC+ edges, APA matrices, and other intermediates. CodeGraph indexes only three R files and not notebooks.
- Supplement gap: the Science supplementary PDF was blocked by an HTML/403 challenge, so supplementary-only parameters and controls could not be independently checked.

The workspace is therefore well suited for auditing the analytical design and reusing individual notebooks after path/data adaptation, but it is not runnable end to end from the snapshot alone.

### Bottom line

This work's main contribution is a multi-layer regulatory atlas that connects cell states, cCRE activity, chromatin organization, and genetic risk in human heart failure. It identifies cardiomyocyte stress states and activated fibroblast branches as major sites of regulatory rewiring and provides a prioritized map of noncoding risk variants to candidate cell types and target genes. The atlas is a strong hypothesis-generation resource; causal enhancer, TF, trajectory, and variant mechanisms still require direct experimental testing.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
