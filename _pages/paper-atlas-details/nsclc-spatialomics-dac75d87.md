---
layout: default
permalink: /paper-atlas/nsclc-spatialomics-dac75d87/
title: "NSCLC_SpatialOmics"
nav: false
wide: true
description: "NSCLCSpatialOmics 研究的是：在 PD-1/PD-L1 免疫治疗前，非小细胞肺癌组织里的空间免疫微环境能否预测患者的无进展生存期。论文把 PCF/CODEX 空间蛋白组用于发现与耐药或响应相关的细胞状态，再把这些细胞状态转译成 DSP-GeoMx 空间转录组中的紧凑基因签名。最终输出不是一张空间图，而是患者级别的 resistance score 和 response score。"
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
      <span>Nature Genetics · 2025</span>
    </div>
    <h1>NSCLC_SpatialOmics</h1>
    <p>Spatial signatures for predicting immunotherapy outcomes using multi-omics in non-small cell lung cancer</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41588-025-02351-7" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for NSCLC_SpatialOmics">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/tznaung/NSCLC_SpatialOmics" target="_blank" rel="noopener noreferrer" aria-label="Open code for NSCLC_SpatialOmics">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## NSCLC_SpatialOmics 方法中文解读

### 一句话概览

NSCLC_SpatialOmics 研究的是：在 PD-1/PD-L1 免疫治疗前，非小细胞肺癌组织里的空间免疫微环境能否预测患者的无进展生存期。论文把 PCF/CODEX 空间蛋白组用于发现与耐药或响应相关的细胞状态，再把这些细胞状态转译成 DSP-GeoMx 空间转录组中的紧凑基因签名。最终输出不是一张空间图，而是患者级别的 resistance score 和 response score。

### 1. 生物学问题与建模目标

PD-L1 染色不能充分解释 NSCLC 患者对免疫治疗的差异反应：有些 PD-L1 高表达患者仍然进展，有些患者可能承受毒性但没有持久获益。因此论文把问题转化为一个空间多组学生存建模任务：先从治疗前组织中识别与 PFS 相关的肿瘤区和基质区细胞组成，再训练可跨队列验证的基因签名。

方法能支持的解释是“哪些空间细胞状态和基因表达组合与免疫治疗结局相关”。它不能单独证明某个细胞类型或基因导致耐药或响应；这些结果更适合作为生物标志物和机制假设生成。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| PCF/CODEX 图像 | PCF spatial proteomics | 29-plex 蛋白标记、细胞位置和表型 | `doc_method.md`, `figure_analysis.md` |
| DSP-GeoMx 表达 | DSP-GeoMx WTA/CTA | 肿瘤/基质 compartment 的转录组表达 | `doc_method.md` |
| 细胞比例矩阵 | ${M}_{ij}^{\mathrm{tumor}}$, ${M}_{ij}^{\mathrm{stroma}}$ | 患者 $i$ 在 compartment 内的细胞类型 $j$ 比例 | `doc_code.md` |
| Cox/LASSO 系数 | ${\beta}_{m,j}$, ${\beta}_{j}^{\mathrm{final}}$ | 重复模型和最终模型的生存风险权重 | `claude_notes.md` |
| 患者签名分数 | ${S}_{i}^{\mathrm{final}}$ | 用于 PFS/OS 分层的风险或响应分数 | `doc_method.md` |
| 最终输出 | resistance / response gene signature | 两组 8 基因签名和患者级别分数 | `summary.md` |

### 3. 方法主流程

1. 收集 Yale 发现队列、UQ 验证队列和 Greek 转录组验证队列的治疗前 NSCLC 样本。
2. 用 PCF/CODEX 做空间蛋白组测量，用 DSP-GeoMx 做 compartment-level 空间转录组测量。
3. 对 PCF 图像做细胞分割、arcsinh 归一化、Harmony 批次校正、Phenograph/Leiden 聚类和人工细胞类型标注。代码中可验证的入口主要是 `NSCLC_SpatialOmics/scripts/PCF_Celltyping.ipynb`。
4. 分别在 tumor 和 stroma compartment 中汇总患者级细胞类型比例，形成 Cox/LASSO 的输入矩阵。
5. 在 Yale 队列中训练方向约束的 Cox/LASSO：resistance 模型用非负系数，response 模型用非正系数。
6. 根据稳定选择到的细胞类型生成 cell-type signature，并在 Yale/UQ 中评估 PFS。
7. 用空间邻域、PD-L1 上下文和 CIBERSORTx deconvolution 做生物学解释；这些部分在本地代码中没有完整可运行脚本。
8. 把细胞类型映射到候选基因池，在 DSP-GeoMx 表达矩阵上训练 gene signature，并在 Yale/UQ/Greek 中验证 PFS 分层。

### 4. 数学目标与直觉

细胞比例矩阵是核心输入：

$$
{M}_{ij}^{\mathrm{tumor}}, \quad {M}_{ij}^{\mathrm{stroma}}
$$

其中 $i$ 是患者，$j$ 是细胞类型。它把空间单细胞信息压缩成适合小样本生存模型的患者级特征。

重复 Cox/LASSO 产生特征系数：

$$
{\beta}_{m,j}
$$

resistance 模型限制 ${\beta}_{m,j}\ge 0$，只允许特征提高 hazard；response 模型限制 ${\beta}_{m,j}\le 0$，只允许特征降低 hazard。这个约束把生物学方向先验写进统计模型。

最终分数是加权和：

$$
{S}_{i}^{\mathrm{final}}=\sum_j {\beta}_{j}^{\mathrm{final}} {M}_{ij}
$$

对 cell-type signature，$M_{ij}$ 是细胞比例；对 gene signature，$M_{ij}$ 是 compartment 表达量。这个分数再按 median 或 tertile 分组，用 Cox/Kaplan-Meier 评估 PFS 或 OS。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| 肿瘤区 resistance cell-type LASSO | `NSCLC_SpatialOmics/scripts/lasso_cox_cellFract_tumor_resistanceLASSO_model_PFS.R:13-66` | `glmnet(family="cox", lower.limits=0)`，100 个 seed | ~ Partial |
| 基质区 response cell-type LASSO | `NSCLC_SpatialOmics/scripts/lasso_cox_cellFract_stroma_responseLASSO_model_PFS.R:13-72` | `upper.limits=0`，50 个 seed | ~ Partial |
| cell-type 分数计算 | `NSCLC_SpatialOmics/scripts/lasso_cox_cellFract_tumor_resistanceLASSO_model_PFS.R:76-81` | 用细胞比例和系数的加权和打分 | ~ Partial |
| resistance gene 训练 | `NSCLC_SpatialOmics/scripts/lasso_TrainTest_CK_RNA_multipleSplits_PFS_2Yrs_3celltypes_PGV_resistance_PFS.R:57-207` | 50 个 split，每个 split 内 100 次 Cox/LASSO | ~ Partial |
| response gene 训练 | `NSCLC_SpatialOmics/scripts/lasso_TrainTest_pStroma_RNA_multipleSplits_PFS_2Yrs_3celltypes_M1_2_CD4_response.R:56-206` | 同样的方向约束基因模型 | ~ Partial |
| 最终 gene coefficient CSV | 本地未找到 | 论文最终 8+8 基因模型无法从公开仓库精确重跑 | ✗ Not found |

代码可验证的是 Cox/LASSO 的主要建模框架、方向约束、部分 processed matrices 和 UQ scoring 逻辑。代码中未找到直接实现的是 CIBERSORTx、Scimap/NeighborhoodCoordination、multivariable Cox 表、Greek validation 的完整脚本，以及最终 gene coefficient CSV。

### 6. 结果如何解读

Figure 3 支持 cell-type signature 的核心结论：肿瘤区 proliferating tumor cells、granulocytes 和 vessels 与较差 PFS 相关；基质区 M1/M2 macrophages 和 CD4 T cells 与较好 PFS 相关。Figure 4 和 Figure 5 是解释层，说明这些细胞状态有空间邻域和转录组 deconvolution 支持，但不构成因果证明。Figure 6 是临床导向输出，显示 resistance 和 response gene signatures 在 Yale、UQ、Greek 队列中对 PFS 有方向一致的分层能力。

### 7. 局限性与未验证部分

- 这是观察性生存建模，不能证明细胞类型或基因导致免疫治疗响应。
- 公开代码不是端到端 workflow；缺少 `Yale_firstLine_pre_patients.csv`、最终 coefficient CSV、若干 split summary 和 multivariable Cox 脚本。
- 空间邻域和 CIBERSORTx 分析在论文中重要，但本地仓库没有对应可验证脚本。
- 代码里有一些实现细节与论文描述不完全一致，例如 resistance gene final selection 阈值在脚本中从 `>0.05` 覆盖为 `>0.2`。
- 验证队列临床组成不同，OS 结果比 PFS 更不稳定，因此还需要前瞻性验证。

### 8. 快速阅读路线

1. `summary.md`：先看问题、贡献、验证结果和复现评分。
2. `doc_method.md`：理解从空间多组学到 Cox/LASSO 签名的完整方法。
3. `doc_code.md`：查看论文步骤和公开代码的逐项匹配、缺失文件和实现差异。
4. `figure_analysis.md`：按主图理解每个结果支持什么结论。
5. `claude_notes.md`：需要证据 ledger、假设、缺失代码和 reanalysis 记录时再读。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spatial Signatures For Predicting Immunotherapy Outcomes Using Multi-Omics In NSCLC

### Motivation And Novelty

PD-1-based immunotherapy has changed advanced NSCLC treatment, but patient selection remains imperfect. Tumor PD-L1 staining alone misses important cases: some patients resist treatment despite high PD-L1, and others may experience toxicity without durable benefit. This paper asks whether pretreatment spatial organization of the tumor immune microenvironment (TIME) can provide stronger biomarkers for progression-free survival (PFS).

The novelty is a staged spatial multi-omics biomarker workflow. The authors first use PCF/CODEX spatial proteomics to identify cell-type states associated with resistance or response, then translate those cell states into compact gene signatures using DSP-GeoMx compartment transcriptomics. The clinically oriented output is not a spatial map itself, but a patient-level signature score that can stratify PFS and, for some analyses, OS.

Compared methods and tools:

| Method / Tool | Journal | Year | Role In This Paper | Limitation Addressed |
|---|---|---|---|---|
| CODEX multiplex tissue imaging | Nature Protocols | 2021 | Spatial proteomic cell phenotyping | Provides cell states and tissue context but not transcriptome-scale biomarkers by itself. |
| DSP-GeoMx spatial transcriptomics | Nature Biotechnology | 2023 | Compartment-level gene expression | Captures gene expression but needs biological anchoring to cell states. |
| Spatially informed melanoma immunotherapy signatures | Clinical Cancer Research | 2024 | Prior robust signature-training framework | Needed adaptation and validation in NSCLC. |
| NeighborhoodCoordination | Cell | 2020 | Cellular neighborhood interpretation | Supports spatial biology but is not a survival-score model. |
| CIBERSORTx / LM22 | Nature Methods | 2015 | Deconvolution validation | Lower-resolution orthogonal support rather than direct spatial proteomic measurement. |

### Method Overview

The workflow begins with three advanced NSCLC cohorts treated with PD-1-based immunotherapy: Yale as discovery/training, UQ as validation, and Greek as an additional transcriptomic validation cohort. PCF/CODEX images are segmented and normalized, tumor/stroma compartments are annotated, and final cell types are assigned. Patient-level cell fractions are then computed separately for tumor and stroma.

For cell-type signatures, the method fits repeated LASSO-penalized Cox models with sign constraints. Resistance models use nonnegative coefficients, so selected features increase hazard. Response models use nonpositive coefficients, so selected features reduce hazard. The tumor resistance signature centers on proliferating tumor cells, granulocytes, and vessels. The stromal response signature centers on M1 macrophages, M2 macrophages, and CD4 T cells.

For cell-to-gene signatures, candidate genes are drawn from the cell types discovered in the proteomics stage. Repeated train/test splits and direction-constrained Cox/LASSO models select compact gene sets. The resistance gene signature contains *KRT7*, *KRT18*, *EFNA1*, *SERINC2*, *FZD6*, *CD24*, *CCND3*, and *S100A9*. The response gene signature contains *SIGLEC1*, *TLR2*, *CXCL9*, *CD81*, *MRC1*, *CCL8*, *CCL13*, and *FCGR1A*.

### Evaluation

The first evaluation layer tests cell-type signatures. In the Yale training cohort, the tumor resistance signature is associated with worse PFS, and UQ validation preserves the same direction. The stromal response signature is associated with better PFS in Yale and validates directionally in UQ. These results support the compartment-specific design: resistant biology is strongest in tumor regions, whereas response-associated biology is strongest in stroma.

The second evaluation layer asks whether spatial and transcriptomic analyses support the same biology. Neighborhood analysis shows resistant regions enriched for proliferating tumor, granulocyte, vessel, and PD-L1-positive tumor patterns, while response-associated tissue contains macrophage and T-cell interaction patterns. CIBERSORTx deconvolution of stromal DSP data supports increased M2 macrophage fractions in nonprogressors.

The final evaluation layer tests gene signatures across cohorts. The resistance gene score stratifies PFS in Yale, UQ, and Greek cohorts, with high scores linked to worse outcomes. The response gene score also validates across cohorts, with high scores linked to better PFS. OS analyses are more mixed: the resistance signature appears more robust for OS than the response signature.

Important limitation: the evidence is associative. The models identify biomarkers and plausible immune mechanisms, but they do not prove causal resistance or response pathways. The validation cohorts also differ in treatment line and clinical composition, so prospective validation is still needed before clinical use.

### Reproducibility

Reproducibility rating: **3 / 5**

The public repository contains useful processed data and analysis scripts. It partially verifies the core statistical workflow: direction-constrained `glmnet` Cox models, repeated seed/split logic, processed tumor/stromal cell-fraction matrices, gene candidate lists, and UQ validation scoring scripts.

The release is not a complete end-to-end reproduction package. Several critical files are referenced but absent, including `Yale_firstLine_pre_patients.csv`, split HR summaries, good-model counts, and final gene coefficient CSVs. The repository also lacks local scripts for CIBERSORTx deconvolution, Scimap/NeighborhoodCoordination spatial interaction analysis, multivariable Cox tables, and exact Greek validation. Some plot labels are manually annotated, and several thresholds in code are more specific or slightly different from the paper text.

Practical takeaway: the code is strong enough to understand and partially rerun the modeling strategy, especially the cell-type Cox/LASSO analyses, but exact reproduction of all published gene-signature and spatial-interpretation claims requires missing intermediate assets or external reconstruction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
