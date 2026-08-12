---
layout: default
permalink: /paper-atlas/spacetracer-74cc153b/
title: "SpaceTracer"
nav: false
description: "SpaceTracer 的目标是利用自然积累的体细胞单核苷酸变异（SNV）作为克隆条形码，在不进行遗传工程标记的情况下重建组织谱系。它的输入是空间转录组比对 BAM、spot 坐标/聚类、参考基因组和群体变异资源；输出首先是高置信 somatic SNV 及其 spot-level genotype。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>SpaceTracer</h1>
    <p>Detection of Somatic Point Mutations Directly from Spatial Transcriptomics Enables in vivo Spatiotemporal Lineage Tracing</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2026.02.04.703493" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpaceTracer：从空间转录组中的体细胞 SNV 到组织原位谱系推断

### 1. 方法真正解决的第一问题是可靠变异检测

SpaceTracer 的目标是利用自然积累的体细胞单核苷酸变异（SNV）作为克隆条形码，在不进行遗传工程标记的情况下重建组织谱系。它的输入是空间转录组比对 BAM、spot 坐标/聚类、参考基因组和群体变异资源；输出首先是高置信 somatic SNV 及其 spot-level genotype。只有在这些变异足够可靠时，才能进一步建立克隆矩阵、系统树、空间扩散和 lineage-aware expression/interaction。

因此要区分三层结论：

1. **SNV calling**：某个位点是否为真实体细胞突变。
2. **克隆/谱系重建**：共享突变是否支持共同祖先与分支次序。
3. **时空历史解释**：不同分支在切片上的位置是否支持扩张或迁移。

第三层不是直接观测细胞运动，而是把突变层级、空间位置和额外转录证据组合后的历史推断。

### 2. 为什么空间转录组既困难又有优势

RNA 数据只覆盖表达区域，存在 RNA editing、等位基因特异表达、mapping bias、PCR/测序错误和表达量差异。Visium spot 又混合多个细胞，低克隆比例突变的 VAF 很小。另一方面，空间转录组在有限表达区域内往往“deep and sparse”：同一位点可有较深 reads/UMIs，且同一克隆的 mutant spots 可能空间聚集。SpaceTracer 的设计就是把这些 RNA 与空间特征都纳入，而不是直接套用 DNA variant caller。

### 3. 五阶段核心流水线

#### 3.1 候选位点预扫描

`1_run_data_process.py` 从 BAM 统计 pileup，排除明显 germline/population variants 与低质量位点，并准备空间 spot/cluster 信息。仓库支持 Visium、Stereo-seq 和传统 ST 的 barcode/UMI tag 差异。候选扫描追求较高敏感性，后续 Bayesian calling、特征和分类器再提高 precision。

空间 cluster 可来自 SpaGCN/GraphST 等外部流程，再以 DBSCAN 等步骤整理。聚类不是最终 clone label；它只为估计局部 allele fraction、空间聚集和 spot 细胞数量提供上下文。

#### 3.2 UMI 级共识与 haplotype phasing

RNA reads 先按 spot barcode 和 UMI 聚合。多个 reads 支持同一 UMI 时，方法用混合模型区分真实分子、测序错误与 PCR chimera；旧证据记录混合参数 $\alpha=0.5$。随后利用邻近 heterozygous germline sites 对候选 SNV 做 phasing。若 mutant allele 与某一 germline haplotype稳定共现，可信度提高；过多不一致 haplotypes 可提示 mapping/PCR artifact。

这一阶段的关键不是“多数投票”这么简单。一个 UMI 只对应一个原始分子，必须避免把同一分子的重复 reads 当成独立证据。代码在 `module/UMI_combine.py`、`phase_combine.py` 与相关工具中实现，但精确概率公式依赖输入格式与配置。

#### 3.3 层级 Bayesian genotyping

`2_run_genotyper.py` 先在样本层面比较四类状态：reference homozygous、heterozygous germline、alternative homozygous 和 somatic mosaic，再把样本先验传递到 spot 层面。直观上，对位点 $l$ 和数据 $D$：

$$
P(G_l\mid D_l)\propto P(D_l\mid G_l)P(G_l).
$$

样本层 mosaic prior 使用很低的体细胞突变率量级；spot 层则结合 cluster VAF 和估计细胞数。spot 的 cell count 不是直接测量：辅助脚本按 UMI 数相对最高 UMI cluster 的 median 估算，乘以 20 并向上取整，最后 capped at 25。这是工程近似，会影响低 VAF genotype posterior。

层级模型的意义是共享全样本证据，同时保留突变只存在于部分空间 spot 的可能性。它产生候选 posterior/likelihood 和 VAF 特征，但最终高置信 somatic label 还要经过机器学习与 artifact filtering。

#### 3.4 近百个特征

`3_run_get_features.py` 汇总约 98 个候选位点特征：

- read/UMI quality：base quality、mapping quality、read position、soft clipping、mismatch、strand bias、indel proximity；
- allele/genotype：depth、alt UMI、VAF、Bayesian mosaic likelihood、haplotype consistency；
- spatial：mutant spots 聚集、KS test、Moran's I、rank-biserial correlation、cluster outliers；
- RNA-specific：RNA editing、ASE、gene strand、polymer/repeat、expression/mappability；
- sample-size-normalized statistics，避免深度本身成为伪标签。

代码会把非常深的位点下采样/限制在约 2000×，并大量删除与样本量强相关或区分度低的列。feature schema 与 pretrained model 必须一致；仓库当前版本包含列名迁移和旧/新 schema 兼容逻辑，混用旧 feature table 与新模型可能失败或 silently 丢列。

#### 3.5 随机森林与后过滤

`4_run_model_predict.py`/`mutation_prediction.py` 对候选位点进行 hard filters、缺失填充、编码、特征选择和分类。训练时可用 SMOTE 处理类别不平衡，并以 leave-one-donor-out 评估泛化。仓库提供两类模型：

- spatial-feature-preserved：适合克隆仍有组织化空间结构；
- spatial-feature-free：避免迁移细胞或弥散克隆因不聚集而被漏掉。

预测后还要过滤 dbSNP、RNA-editing、panel of normals、重复/低 mappability、异常 haplotype 与 artifact mutational signatures。NMF 分解 RNA artifact signatures，再按 hFDR 等规则去除可能的裂解/化学修饰噪声。最后 `5_remove_recurrent_mutations.sh` 删除跨样本反复出现的可疑位点。

随机森林概率不是 mutation posterior 的同义词；它是在 curated labels 和特征分布下学到的分类分数，跨平台/组织应用需要重新检查 calibration。

### 4. 为什么需要两个分类模型

空间聚集是有力证据：一个真实 clone 的突变通常集中在相邻区域，而随机错误较分散。但迁移、免疫细胞流动、肿瘤浸润或组织切片几何会破坏聚集。如果所有样本强制使用空间特征，真实弥散 clone 可能被判假；若完全不使用空间，又浪费空间转录组的主要优势。

SpaceTracer 因此训练 preserved 与 free 两套模型。它们不是“高质量/低质量”版本，而对应不同的生物空间假设。选模应由预期克隆组织、平台分辨率和验证结果决定，不能在看到结果后任意选择最有利模型。

### 5. 从 SNV 矩阵到谱系树

对通过过滤的 mutation，构建 clone/spot × mutation 的 presence/absence 或概率矩阵。共享 founder mutation 支持共同祖先，子克隆新增 mutation 支持更晚分支。论文使用 PhyloSOLID 重建树，并以两类 ground truth 验证：CRISPR barcode lineage 数据被映射到空间布局，比较 SNV 树与 barcode tree 的一致性。

需要保留三个边界：

- SNV absence 可能是未表达/未覆盖，而不是真实野生型。
- 同一突变可能 recurrent，必须用 context/signature/PON 与树一致性过滤。
- 系统树的 branch order 来自 mutation accumulation 假设；空间距离本身不决定祖先方向。

PhyloSOLID 和部分下游树分析不属于 SpaceTracer 核心五步 SNV caller，因此“核心 pipeline 可运行”不代表从 BAM 到论文所有 phylogeny/figure 一键完成。

### 6. 主要验证与应用证据

#### 图 1：方法框架

图 1 对比空间 RNA 的深覆盖局部区域与 WGS 的广覆盖，并展示空间聚集帮助区分真实 clone 与噪声。层级 Bayesian network、特征抽取、RF 和 artifact signature 构成 SNV calling 主链。

#### 图 2：SNV benchmark

作者用相邻切片 200× WGS 和六个公开样本构建 benchmark，并与 Monopogen、SComatic、SpatialSNV 比较。leave-one-donor-out 结果支持 precision/sensitivity；论文报告总体准确率至少约 80%。相邻切片 WGS 不是完全相同细胞，表达区域覆盖也不同，因此 validation negative 中会包含空间取样不一致。

#### 图 3：谱系 benchmark

将已知 CRISPR barcode 树映射到空间后，SpaceTracer SNV calls + PhyloSOLID 可恢复相近层级。这里验证的是整条“检测→矩阵→树”链在构造/参考数据上的表现，不等于每个人体组织树都有 ground truth。

#### 图 4：cSCC 起源与迁移

论文在皮肤鳞癌中识别 normal epithelial、tumor 和迁移性非肿瘤 clone，结合 founder/subclonal mutations 推断起源和空间传播，并做 lineage-coupled expression。迁移方向来自树的先后关系与切片位置：它是历史推断，不是 time-lapse imaging。

#### 后续图：肿瘤生态与正常组织发育

作者将 clone fitness、免疫互作、BCR mutation、不同组织发育 lineage 与表达程序联系起来。基因表达/配体受体差异是在 clone assignment 后做的下游统计，不能反过来当作 SNV 真实性的独立验证，除非分析明确分离训练与验证证据。

### 7. 论文—代码对应

| 论文环节 | 本地代码 | 判断 |
|---|---|---|
| BAM/候选预扫 | `1_run_data_process.py` + Snakemake modules | **Direct/Partial**：主链可见，依赖 samtools、reference 和外部资源 |
| UMI 共识/phasing | `module/UMI_combine.py`, `phase_combine.py` | **Direct**：实现存在 |
| 层级 genotyping | `2_run_genotyper.py`, `individual_genotyper.py`, `spot_genotyper.py` | **Direct/Partial**：公式与代码可对齐，结果依赖 priors/cell-count approximation |
| 约 98 特征 | `3_run_get_features.py`, `extract_features.py`, `spatial_features.py` | **Direct** |
| RF/SMOTE | `4_run_model_predict.py`, `mutation_prediction.py` | **Direct**：预训练模型与 feature schema 必须匹配 |
| artifact/PON/recurrent filters | model code、Resources、step 5 shell | **Direct/Partial**：资源文件与版本影响结果 |
| PhyloSOLID 树 | 外部/下游工具 | **Partial / Not found** 于核心 caller |
| 论文完整 cSCC/多组织下游图 | 当前仓库未提供统一 notebooks | **Not found** |

工作区同时有 `code/` 与 `SpaceTracer/` 两份近似重复仓库。合同应指定一个 canonical `code source`；本轮采用 `code/`，避免把重复文件误当不同实现或重复统计更改。

### 8. 复现所需输入与现实边界

完整运行至少需要 coordinate-sorted BAM、参考 FASTA、gene annotation、gnomAD/dbSNP/RNA-editing/mappability/PON 等资源、spot cluster 与平台 tag 配置。仓库提供 conda/pip 环境、配置示例、Snakemake wrappers 和部分模型资源，因此核心复现条件比 notebook-only 项目更好。

仍有边界：

- repo commit 未记录，预训练模型与代码 schema 的精确版本关系不透明；
- 大型参考资源和全部论文输入/验证数据不随工作区完整提供；
- 部分 shell/perl/R/外部工具不由 Python environment 单独覆盖；
- 论文写作时曾称代码“准备发布”，当前快照虽存在，仍需把它视为特定时间点版本；
- demo 能验证文件流，不等于复现论文全部 benchmark 和生物学结论。

### 9. 最重要的解释限制

- RNA 中检测到的等位基因不等于 DNA 中必然存在；RNA editing、ASE 和 mapping artifact 必须持续过滤。
- 未检测到 mutation 常由无表达/低覆盖导致，不能直接作为系统树中的可靠 0。
- Visium spot 混合多细胞，VAF 到 clone fraction 的换算依赖估计 cell number。
- 空间聚集既是特征也可能来自组织表达/测序深度结构；应防止 information leakage。
- leave-one-donor-out 比随机 site split 更严格，但新平台/组织仍可能 distribution shift。
- 两模型选择体现不同空间假设，不能事后挑选最符合故事的输出。
- SNV 树支持共同祖先与相对分支，绝对时间需 mutation-rate 或外部时间信息。
- “迁移”是 phylogeny + spatial pattern 的解释，不是直接运动测量。
- lineage-coupled gene expression 和 cell-cell communication 是关联性下游分析。

SpaceTracer 的主要贡献，是把空间信息用在 RNA somatic SNV 的去噪和判别上，再把自然突变转成原位 clone labels。它使人类组织中无需预先工程化标记的谱系分析成为可能，但结论强度始终受限于 RNA 变异检测、spot 混合、缺失数据和系统树假设；空间图本身不能替代真正的时间追踪。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpaceTracer — Paper Analysis Summary

**Paper**: Detection of Somatic Point Mutations Directly from Spatial Transcriptomics Enables in vivo Spatiotemporal Lineage Tracing
**DOI**: 10.64898/2026.02.04.703493
**Journal**: bioRxiv preprint (under consideration at *Nature*)
**Year**: 2026 (posted February 6, 2026)
**Authors**: Zhirui Yang, Mengdie Yao, Qing Yang, Yiheng Du, Jinhong Lu, … Yanmei Dou
**Institution**: Westlake University, Fudan University (Huashan Hospital)
**GitHub**: https://github.com/douymLab/SpaceTracer

---

### Motivation & Novelty

#### Biological Problem

Lineage tracing — the reconstruction of which cells gave rise to which — is fundamental to understanding development, cancer progression, and aging. In model organisms, this is accomplished by introducing genetic barcodes (CRISPR, Brainbow, Mosaic). In humans, these manipulations are not permitted, so only naturally occurring somatic mutations can serve as barcodes.

Somatic mutations accumulate as a byproduct of normal cell division and DNA damage over time. They are heritable from parent to daughter cell, making them ideal lineage markers: two cells sharing a rare somatic mutation must have shared a common ancestor. The challenge is reading these natural barcodes in native tissue.

#### Limitations of Existing Approaches

**CNV-based spatial methods**:
- inferCNV (Trinity CTAT Project): Gene expression-based CNV caller; assumes non-cancer cells are diploid; limited resolution; influenced by expression levels.
- CalicoST (*Nat. Methods*, 2024): Reference-free, allele-aware spatial CNV caller; limited by the coarse resolution of large chromosomal blocks — cannot distinguish fine-grained subclones sharing the same CNV profile.

**scRNA-seq SNV callers adapted to spatial data**:
- Monopogen (*Nat. Biotechnol.*, 2023): Designed for scRNA-seq; lacks spatial proximity for noise filtering; lower accuracy on spatially resolved data.
- SComatic (*Nat. Biotechnol.*, 2023): Same limitation — not optimized for spatial transcriptomics.

**Spatial-specific callers**:
- SpatialSNV (*GigaScience*, 2025): Wraps Mutect2 (a DNA-seq tool); generates tens of thousands of likely-artifact calls per sample, requiring extensive post-filtering.

#### SpaceTracer's Unique Contributions

1. **First high-accuracy somatic SNV caller for spatial transcriptomics**: Achieves ≥80% accuracy on independent benchmarks, significantly outperforming all competitors (p=3.9×10⁻⁹, one-tailed t-test).

2. **Spatial proximity as a noise filter**: Adjacent spots sharing clonal mutations provide a new avenue for local signal enhancement — a signal boosting mechanism impossible with WGS or scRNA-seq alone.

3. **Two-model design for different biological contexts**: A spatial-preserved model and a spatial-feature-free model allow application to both organized clonal structures and extensively migrating populations.

4. **End-to-end lineage tracing platform**: Integrates SNV detection, phylogeny reconstruction (via companion tool PhyloSOLID), deconvolution, and cell-cell communication in a single workflow.

5. **Perturbation-free human applicability**: Uses naturally occurring somatic mutations — applicable to any human tissue without genetic manipulation.

---

### Method Overview

SpaceTracer is a Python/R bioinformatics pipeline with five core algorithmic stages:

1. **Prescan**: `samtools mpileup` → candidate loci; gnomAD frequency lookup for germline exclusion; spatial domain clustering (SpaGCN/GraphST + DBSCAN).

2. **UMI-level Bayesian consensus**: Collapse sequencing reads to UMI-level allele calls using a Bayesian model that separates sequencing error from PCR chimera artifacts (α-mixing parameter = 0.5).

3. **Hierarchical Bayesian genotyping**: Infer individual-level and spot-level genotypes using a four-state model (refhom, het, althom, mosaic). Individual-level prior is derived from gnomAD population allele frequencies (μ = 1e-7/bp for mosaic mutations). Spot-level prior incorporates cluster VAF and cell count per spot.

4. **Comprehensive feature extraction**: ~98 features per candidate across four categories — spatial (KS test, Moran's I), read-level (quality, bias), RNA-specific (strand bias, RNA editing), and site-level (expression, mappability). Depth capped at 2000× to prevent high-expression loci from dominating.

5. **Random Forest classification + artifact filtering**: Two pre-trained RF models (spatial/non-spatial) with SMOTE class balancing and leave-one-donor-out cross-validation. Post-prediction filtering uses NMF-derived artifact signatures (hFDR ≥0.8 threshold) plus hard filters (dbSNP, RNA editing databases, panel of normals from 33 non-neoplastic samples).

**Key biological assumption**: Spatial proximity implies clonal relatedness. Adjacent cells are more likely to share somatic mutations; the cluster VAF therefore provides a meaningful prior for spot-level genotype inference.

**Computational pipeline**: A Snakemake workflow (conda or Docker) orchestrates 8 automated rules. Pre-trained models allow new samples to skip training entirely.

---

### Evaluation

#### Benchmark Datasets

**In-house BCC benchmark** (primary):
- 1 basal cell carcinoma (BCC) sample
- Spatial Visium slide + adjacent section sequenced at 200× WGS
- Tumor (RT) and normal (RN) regions microdissected separately for matched validation

**6 public benchmark datasets** (independent validation):
| Dataset | Tissue | GEO Accession | Cross-validation method |
|---------|--------|----------------|------------------------|
| cSCC P4, P6 | Cutaneous squamous cell carcinoma | GSE144240 | Adjacent slice scRNA-seq |
| Brain Br5292, Br5595, Br8100 | Normal dorsolateral prefrontal cortex | Globus (jhpce#) | Adjacent Visium slices |
| Breast P10 | Normal breast | GSE176078 | Adjacent slice scRNA-seq |

**Phylogeny benchmark**:
- 2 simulated spatial datasets from CRISPR-barcoded LUAD scRNA-seq (GSE195665 [Science 2021])
- CytoSPACE projection onto Visium HD lung cancer layout
- Ground truth: CRISPR barcode phylogeny

#### Performance Metrics

**Mutation detection accuracy**:
- BCC benchmark (200× WGS ground truth): SpaceTracer significantly outperforms competitors (p=0.00049, two-tailed t-test; Fig. 2b)
- 6 public datasets: SpaceTracer accuracy ≥80% on all (p=3.9×10⁻⁹, one-tailed t-test; Extended Data Fig. 4e)
- Sensitivity comparison: p=1.45×10⁻⁴ (one-tailed t-test; Extended Data Fig. 3f-h)

**SNVs detected per sample**: Several to dozens per tissue slice; ~10-20% in exonic regions

**Mutation rate validation**: Per-cell mutation rates estimated from spatial data fall within published DNA-sequencing-derived ranges:
- Normal skin: 0.4–12 mut/Mb (literature); matches SpaceTracer estimates
- Tumor skin: 0.1–380 mut/Mb
- Normal brain: 0.167–1.3 mut/Mb
- Normal breast: 0.1–0.4 mut/Mb

**Phylogeny reconstruction** (LUAD CRISPR benchmark):
- High concordance with ground-truth CRISPR barcode trees in both LUAD-1 and LUAD-2 benchmarks (Fig. 3)
- PhyloSOLID algorithm used; tolerates inherent sparsity and noise of single-cell data

**Mutational signatures**: Signatures extracted from spatial data match known COSMIC DNA signatures (SBS7a/b/c/d for skin UV damage; SBS1, SBS5 for aging; validated against deconstructSigs)

#### Key Biological Findings

**cSCC tumor initiation and progression** (cSCC-1, cSCC-2 from GSE144240):
- Phylogenetically distinct clones: normal (Cn), tumor (Ct), and migrating non-tumor (Cp)
- Ct cells migrated from epithelium to dermis, expanded as tumor bulk
- Cp cells (non-tumor-forming) migrate even more extensively than tumor cells; per-cell mutation rate significantly higher than tumor cells (p=2.85×10⁻¹⁵); undergo significant downregulation of cornification/differentiation
- This widespread non-tumor epithelial migration is recurrent across independent donors → suggests systematic dedifferentiation event enabling early tumor invasion
- **Crucially undetectable by gene expression alone** — only revealed by somatic SNV barcoding

**Tumor heterogeneity and immune ecosystem**:
- Phylogenetic fitness score (Local Branching Index) correlates with EMT score (p=0.026) and expression-based fitness signature (p=0.012)
- Rapidly expanding subclones upregulate MT-ND5 (energy metabolism) and downregulate CD151 (metastasis suppressor)
- ANXA1 ligand upregulated in high-fitness tumor keratinocytes → promotes M2 macrophage polarization, suppresses cytotoxic T cells

**Mutant B cells in cSCC**:
- 7 somatic SNVs in BCR loci; 4/7 in variable regions (somatic hypermutation signature)
- Mutant B cells are plasma cell-like (upregulated IGLC2, IGHG1, IGHG)
- Mutant B cells migrate from tertiary lymphoid structures (TLS) into tumor boundary (KS test p=5.7×10⁻²⁰)
- Tumor cells upregulate JAG1 → binds CD46 on mutant B cells → potential tumor immune evasion via reverse Notch signaling

**Normal tissue-resident B cells**:
- Breast tissue has significantly higher BCR somatic mutation frequency than brain or colon (p=0.0012)
- 44/45 BCR mutations in B cell receptor genes; only 36% in canonical hypervariable regions
- BCR variable-region mutations show significant spatial clustering → compartmentalized immune activity

**Glioblastoma** (Extended Data Fig. 10): Clear tumor initiation and progression patterns across 3 independent GBM samples.

---

### Reproducibility

**Rating: 3/5** — Core method is reproducible but with notable gaps.

**Strengths**:
- Public GitHub repository with versioned code (v1.1.0, updated February 25, 2026)
- Pre-trained models included (`models_trained/`) — new users can skip training
- Docker image available (`xiayh17/spacetracer`)
- Demo input data provided with Snakemake workflow
- All benchmark GEO accessions listed (GSE144240, GSE158328, GSE220978, etc.)
- Wet-lab BCC data deposited in SRA (PRJNA1396783)

**Limitations**:
- Downstream analyses (per-cell mutation rate estimation, fitness-associated DEG, Fig. 4 biological analyses) are not in the public repo — likely in separate scripts
- Companion tool PhyloSOLID is referenced (ref. 25, 30) as "(2025)" — preprint not yet published at time of writing
- WGS + Spatial transcriptomics from same sample required for highest-confidence benchmarking; not all users will have paired samples
- Cell type deconvolution (Spotiphy) and reference atlas construction require matched scRNA-seq — adds complexity for new users
- The NMF-derived artifact signatures (lysis_errors.SigProfile.txt) are pre-computed and provided, but regeneration from scratch would require the full 101-slide training dataset

**Environment setup**:
```bash
# Docker (recommended)
docker pull xiayh17/spacetracer

# Conda alternative
conda env create -f environment.yml
pip install -r requirements_pip.txt

# Required external tools
# samtools, bedtools, bcftools, Java
```

**Common pitfalls**:
- MapQ ≥255 filter is SpaceRanger-specific (unique mapping gets MapQ=255 in STAR)
- gnomAD population frequency files must match the reference genome (GRCh38)
- SpaGCN requires histology image for spatial clustering (H&E image from Visium)
- Cell number estimation (get_umiCount_cellNum.py) assumes linear UMI-count scaling; may need calibration for very dense or sparse tissues
- hFDR signature filtration is implemented in R, requiring a separate R environment

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
