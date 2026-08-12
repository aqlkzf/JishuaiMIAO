---
layout: default
permalink: /paper-atlas/oasis-1b1049f0/
title: "OASIS"
nav: false
description: "OASIS 的核心问题是：免疫细胞中的遗传效应、体细胞突变效应、微生物组影响和疾病风险评分，很多并不是固定地作用在“某一种细胞类型”上，而是会随连续的细胞状态改变。传统 bulk mQTL 或离散细胞类型分析容易把这种状态依赖性平均掉。论文因此构建了一个面向日本人群的多组学单细胞免疫图谱，把 PBMC 单细胞转录组、scVDJ、宿主遗传、血浆蛋白组、肠道宏基因组和体细胞事件投射到同一套免疫细胞状态框架中。"
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
      <span>Nature Genetics · 2025</span>
    </div>
    <h1>OASIS</h1>
    <p>Deciphering state-dependent immune features from multi-layer omics data at single-cell resolution</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41588-025-02266-3" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## OASIS 方法中文解读

### 这篇论文要解决什么问题？

OASIS 的核心问题是：免疫细胞中的遗传效应、体细胞突变效应、微生物组影响和疾病风险评分，很多并不是固定地作用在“某一种细胞类型”上，而是会随连续的细胞状态改变。传统 bulk mQTL 或离散细胞类型分析容易把这种状态依赖性平均掉。论文因此构建了一个面向日本人群的多组学单细胞免疫图谱，把 PBMC 单细胞转录组、scVDJ、宿主遗传、血浆蛋白组、肠道宏基因组和体细胞事件投射到同一套免疫细胞状态框架中。

论文数据规模是 235 名参与者，其中 88 名 COVID-19 患者、147 名健康个体；单细胞层面获得 1,506,953 个高质量 PBMC，并定义 7 个 L1 主要细胞类型和 28 个 L2 精细细胞状态。

### 方法整体思路

OASIS 不是一个单一模型，而是一条图谱分析流水线：

```text
PBMC 单细胞图谱
  |
  |-- 按样本/细胞类型聚合表达 -> pseudobulk cis-eQTL
  |-- 按炎症/IFN 模块分箱 -> pseudobulk dynamic eQTL
  |-- Harmony hPC + NBME -> 单细胞分辨率 dynamic eQTL
  |-- KNN 邻域 + Milo -> 微生物组/LOY 相关细胞丰度变化
  |
  |-- WGS / SNP array
  |     |-- eQTL、PRS、HLA、体细胞事件
  |
  |-- scVDJ
  |     |-- TCR/BCR usage、PC、CDR3 长度、SHM 特征
  |
  |-- GWAS / PRS / proteomics
        |-- coloc、PRS-DEG/DEP、疾病相关解释
```

### 1. 单细胞图谱与 pseudobulk cis-eQTL

论文先对每个主要细胞类型分别做单细胞表达归一化，保留在该细胞类型中超过 1% 细胞有非零 UMI 的基因。然后按“样本 × 细胞类型”取 log~2~ 归一化表达的平均值，形成 pseudobulk 表达矩阵，并在样本间做 inverse normal transform。每个细胞类型只保留细胞数大于 10 的样本。

cis-eQTL 使用 tensorQTL：每个基因测试转录起始位点 1 Mb 内、MAF > 0.05 的变异；协变量包括 15 个表达 PC、2 个基因型 PC、年龄、性别、10x chemistry 版本和 COVID-19/健康状态。显著性通过每基因 1,000 次 cis permutation 和 genome-wide q-value 校正确定，阈值 q < 0.05。

代码中 `OASIS_project/scripts/cis-eQTL_mapping/tensorQTL_cis_nominal.py` 和 `tensorQTL_cis_permutation.py` 直接支持这一部分：读取 phenotype BED、covariates、PLINK genotype，运行 `cis.map_nominal` / `cis.map_cis`，并计算 q-values。

### 2. dynamic eQTL：从模块分箱到单细胞 NBME

这是论文最核心的统计部分。作者关注 myeloid cluster 中两个免疫相关模块：

- `HALLMARK_INFLAMMATORY_RESPONSE`
- `GOBP_RESPONSE_TO_ INTERFERON_GAMMA`

每个细胞先用 Seurat `AddModuleScore()` 计算模块分数，然后每个模块按分数分成 10 个等细胞数窗口。每个窗口内对每个样本计算 pseudobulk 表达，用于检测 genotype 与模块状态之间的交互。

#### pseudobulk 线性模型

论文保留的线性模型是：

$$\begin{array}{l}{\rm{Exp}}={\beta }_{0}+{\beta }_{\rm{g}}\times {\rm{genotype}}+&#123;&#123;\beta }_{\rm{a}}\times {\rm{age}}+\beta }_&#123;&#123;\rm{sex}}}\times {\rm{sex}}+{\beta }_{\rm{v}}\times {\rm{version}}\\\qquad\;\;+{\beta }_&#123;&#123;\rm{status}}}\times {\rm{status}}+\mathop{\sum }\limits_{i=1}^{2}{\beta }_{\rm{g&#123;&#123;PC}}}_{\it{i}}}\times {\rm{g&#123;&#123;PC}}}}_{\it{i}}+\mathop{\sum }\limits_{j=1}^{15}{\beta }_{\rm{e&#123;&#123;PC}}}_{\it{j}}}\times {\rm{e&#123;&#123;PC}}}}_{\it{j}}\\\qquad\;\;+{\beta }_{\rm{m}}\times {\rm{module}}+{\beta }_{\rm{g}\times \rm{m}}\times {\rm{genotype}}\times {\rm{module}}+\left(1|{\rm{sample}}\right)\end{array}$$

#### pseudobulk 二次模型

二次模型进一步加入 module^2^ 和 genotype × module^2^：

$$\begin{array}{l}{\rm{Exp}}={\beta }_{0}+{\beta }_{\rm{g}}\times {\rm{genotype}}+{\beta }_{\rm{a}}\times {\rm{age}}+{\beta }_&#123;&#123;\rm{sex}}}\times {\rm{sex}}\\\qquad\;\;+{\beta }_{\rm{v}}\times {\rm{version}}+{\beta }_&#123;&#123;\rm{status}}}\times {\rm{status}}\\\qquad\;\; +\mathop{\sum }\limits_{i=1}^{2}{\beta }_{\rm&#123;&#123;{gPC}}}_{\it{i}}}\times {\rm{gPC}}_{i}+\mathop{\sum }\limits_{j=1}^{15}{\beta }_{\rm&#123;&#123;{ePC}}}_{\it{j}}}\times {\rm{ePC}}_{j}+{\beta }_{\rm{m}}\times {\rm{module}}\\\qquad\;\;+{\beta }_&#123;&#123;\rm{m}}^{2}}\times &#123;&#123;\rm{module}}}^{2}\\\qquad\;\;+{\beta }_{\rm{g}\times m}\times {\rm{genotype}}\times {\rm{module}}\\\qquad\;\;+{\beta }_{\rm{g}\times {m}^{2}}\times {\rm{genotype}}\\\qquad\;\;\times &#123;&#123;\rm{module}}}^{2}+\left(1|{\rm{sample}}\right).\end{array}$$

代码中 `OASIS_project/scripts/dynamic-eQTL/PseudoBulk_dynamic-eQTL.R` 直接实现了这个模型族：`Cate` 对应模块分箱，`Cate2` 对应平方项，`G*Cate` 和 `G*Cate2` 对应交互项；用 `lmer()` 拟合 null/full model，用 LRT 得到 P 值，再用 BH FDR 汇总。需要注意的是脚本 `--num_cate` 默认值是 5，但论文主分析使用 10 个窗口；脚本支持传入 10。

#### 单细胞 NBME 模型

为了把效应定位到更细的连续细胞状态，论文又使用 NBME 模型。细胞状态由 Harmony hPC 表示，模型形式为：

$$\begin{array}{l}{\rm{Exp}}\left({\rm{UMI}}\right)={\beta }_{0}+{\beta }_{\rm{g}}\times {\rm{genotype}}+{\beta }_{\rm{a}}\\\qquad\qquad\quad\;\;\times{\rm{age}}+{\beta }_&#123;&#123;\rm{sex}}}\times {\rm{sex}}+{\beta }_{\rm{v}}\times {\rm{version}}+{\beta }_&#123;&#123;\rm{status}}}\times {\rm{status}}\\\qquad\qquad\quad\;\;+{\beta }_&#123;&#123;\rm{UMI}}}\times \log {\rm{UMI}}+{\beta }_&#123;&#123;\rm{MT}}}\times {\rm{MT}}\\\qquad\qquad\quad\;\;+\mathop{\sum }\limits_{i=1}^{2}{\beta }_{\rm&#123;&#123;{gPC}}}_{\it{i}}}\times {\rm{gPC}}_{i}+\mathop{\sum }\limits_{j=1}^{15}{\beta }_{\rm&#123;&#123;{ePC}}}_{\it{j}}}\times {\rm{ePC}}_{j}+\mathop{\sum }\limits_{k=1}^{15}{\beta }_{\rm&#123;&#123;{hPC}}}_{\it{k}}}\times {\rm{hPC}}_{k}\\\qquad\qquad\quad\;\;+\mathop{\sum }\limits_{k=1}^{15}{\beta }_{\rm{g}\times {\rm{hPC}}_{k}}\times {\rm{genotype}}\times {\rm{hPC}}_{k}+\left(1|{\rm{sample}}\right).\end{array}$$

单细胞 eQTL 强度定义为：

$${\beta }_&#123;&#123;\rm{total}}}={\beta }_{\rm{g}}+\mathop{\sum }\limits_{k=1}^{15}{\beta }_{\rm{g}\times h&#123;&#123;PC}}_{\it{k}}}\times {\rm{h&#123;&#123;PC}}}}_{k}.$$

代码中 `NB_analysis_auto_loop_hg38_update.R` 构造 null/full formula，使用 `glmer.nb()` 拟合，full model 包含 `G*harmony_1` 到 `G*harmony_15`。它导出 full/null 系数和 LRT 结果。缺口是：代码中没有找到显式计算 `${\beta }_&#123;&#123;\rm{total}}}` 或绘制 beta_total UMAP 的后处理脚本；只能看到所需系数被导出。

### 3. HLA/TCR/BCR 关联与 repertoire GWAS

论文用 scVDJ 数据构建 TCR/BCR repertoire 特征，并做两类遗传关联：

1. HLA 氨基酸变异与 TCR V gene usage 的关联，以及 COVID-19 状态下的交互效应。
2. 全基因组变异与 repertoire 综合特征的关联，包括 V(D)J usage PC、CDR3 长度均值/CV、BCR SHM 频率等。

辅助仓库 `OASIS_HLATCR` 是这部分的主要代码来源。`generate_usage.py`、`generate_pc.py`、`generate_cdr3_len.py` 和 `generate_mu_freq.py` 生成 usage、PC、CDR3、SHM 等 phenotype 文件，并做 rank-normalization。`HLA_association_test.R` 用 DESeq2 负二项 Wald test 拟合 `variant` 或 `case:variant` 交互模型。`GWAS.sh` 用 PLINK2 对 usage、PC、CDR3 和 SHM phenotype 做线性 GWAS。这里的限制是 GWAS shell 中 `GENO`、`COVAR` 等配置为空，需要外部环境补齐。

### 4. GWAS colocalization 与 PRS 分析

colocalization 部分把 East Asian GWAS 信号与 OASIS 的 eQTL 信号在 500 kb 窗口内比较，用 coloc 的 PP.H4 > 0.8 作为共享因果变异证据。代码 `colocalization/coloc.R` 实现了区域过滤、等位基因方向协调、`coloc.abf()` 和 H4 汇总输出。

PRS 部分用 PRS-CSx 构建 COVID-19 hospitalized PRS，并把 PRS 分成四分位数，在 COVID-19 与健康样本中分别做 pseudobulk RNA DEG 分析，同时论文还报告蛋白 DEP。代码中 `PRScsx_COVID19.sh` 和 `PRS/DEG_analysis.R`、`DEG_permutation.R` 支持 COVID-19 PRS 与 RNA DEG/置换分析；但未找到 Olink 蛋白组预处理和 DEP 分析代码。

### 5. 体细胞事件的单细胞投射

论文把三类体细胞事件映射到单细胞：

- mCA/LOY：SNP array 中用 MoChA 检测；
- mt-heteroplasmy：WGS 中用 GATK Mutect2 mitochondrial mode 检测；
- 单细胞投射：用 Numbat、Y 染色体表达缺失、cellSNP-lite/vireoSNP 把事件映射到 scRNA-seq 细胞。

代码中可验证的是投射层：

- `mCA_numbat.sh` 和 `mCA_numbat.R` 用 Numbat 结合 scRNA-seq allele/expression 信息和已知 CNV profile；
- `LOY_single-cell.py` 通过 Y chromosome gene 的表达比例为 0 标记 LOY 细胞；
- `mt-heteroplasmy_cellsnp-lite.sh` 和 `mt-heteroplasmy_vireoSNP.py` 用 cellSNP-lite 生成 SNP-by-cell 矩阵，再用 vireoSNP `BinomMixtureVB` 做 clone assignment。

缺口是上游 MoChA 和 GATK Mutect2 调用脚本未在可见仓库中找到；mCA/LOY/mt 后续 DEG/pathway 分析也不是完整可复现。

### 图像证据如何支撑方法？

主图 1 展示 OASIS 的多组学设计和 PBMC UMAP 图谱。主图 2 支持 cis-eQTL 与 metagenome-Milo 分析。主图 3 支持 HLA/TCR/BCR 关联。主图 4 是 dynamic eQTL 的核心示意和结果：模块分数、十个 bin、pseudobulk linear/quadratic model、single-cell NBME 和 beta_total UMAP。主图 5 说明 dynamic eQTL 对 GWAS colocalization 的解释力，并展示 PRS 对 RNA/protein 的上下文特异效应。主图 6-8 分别支持 mCA、LOY、mt-heteroplasmy 的单细胞投射。

### 可复现性评价

代码与论文主要统计流程匹配度较高，尤其是 tensorQTL cis-eQTL、pseudobulk dynamic eQTL、NBME、HLA/repertoire 分析、coloc、PRS RNA DEG、Milo 和 somatic projection。但这些代码更像原始研究分析脚本，而不是便携式 workflow：大量路径是机器本地路径，部分 shell 变量为空，蛋白组和 Eq. (4) beta_total 后处理缺失。因此，读者可以复现方法思想和主要统计模型，但若要完整重跑所有图，需要补充数据访问、环境配置和若干后处理脚本。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## OASIS Summary

### Problem

Most molecular QTL resources are bulk-resolution and underrepresent non-European populations. OASIS addresses this by building a multi-layer immune atlas in Japanese individuals and asking how germline variants, HLA/repertoire variation, PRS, microbiome abundance, and somatic events act across immune cell types and continuous cell states.

### Resource And Workflow

OASIS integrates >1.5 million high-quality PBMCs from 235 participants, including 88 patients with COVID-19 and 147 healthy individuals, with WGS, SNP array genotyping, scVDJ-seq, plasma proteomics, and gut metagenomics. The computational workflow is an atlas-level pipeline:

- pseudobulk cis-eQTL mapping with tensorQTL across L1/L2 immune cell types;
- dynamic eQTL analysis in myeloid cells using module-score windows, linear/quadratic mixed models, and single-cell NBME models over Harmony PCs;
- HLA/TCR/BCR association and repertoire-feature GWAS;
- colocalization of GWAS loci with static and dynamic eQTLs;
- PRS-based RNA/protein differential expression;
- single-cell projection of mCAs, LOY, and mt-heteroplasmy;
- Milo neighborhood analysis for gut metagenome and LOY-associated abundance shifts.

### Main Results

The atlas maps tens of thousands of cis-eQTLs and shows that eQTL power depends strongly on cell counts per sample. Dynamic eQTL analysis identifies myeloid state-dependent regulatory effects, including examples where single-cell NBME and beta_total UMAPs localize effects within inflammatory/interferon-related states. HLA association and repertoire GWAS reveal cell-type-specific TCR/BCR genetic associations. Colocalization examples such as PLD4 and ETS2 show that dynamic eQTLs can sharpen interpretation of immune-disease GWAS loci. PRS analyses find context-specific transcriptomic/proteomic effects in COVID-19. Somatic-event analyses project mCAs, LOY, and mt-heteroplasmy into single-cell resolution and show cell-type-specific enrichments, especially in monocytes/DCs.

### Reproducibility And Code Match

The paper names two code repositories, and both are present locally: `OASIS_project` and `OASIS_HLATCR`. Direct source reads support a medium-high code-paper match for the major statistical workflows: tensorQTL cis-eQTL, pseudobulk dynamic-eQTL lmer models, single-cell NBME, HLA/repertoire association, PLINK repertoire GWAS, coloc, PRS RNA DEG, Milo metagenomics, and somatic-event projection.

The main limitations are portability and missing post-processing. Many scripts contain machine-local paths or shell placeholders. Explicit code for Eq. (4) beta_total post-processing/UMAP rendering was not found, although NBME scripts export the coefficients needed to reconstruct it. Plasma proteomics/Olink analysis code was not found. Upstream MoChA mCA/LOY calling and GATK Mutect2 mt-heteroplasmy calling scripts were also not found in the visible repos.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
