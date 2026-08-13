---
layout: default
permalink: /paper-atlas/humanimmuneaging-atlas-f67a65e0/
title: "HumanImmuneAging_Atlas"
nav: false
wide: true
description: "这项研究用 CITE-seq 同时测量同一免疫细胞的 RNA 和 127 种表面蛋白，在 24 位器官捐献者、14 个组织部位中建立 128 万细胞的图谱。分析先用多模态标志物精细区分免疫亚群，再用配对供体的跨组织设计把“组织效应”与“年龄效应”分开，最后通过 pseudobulk 混合模型、基因程序分解和 MrVI 反事实预测，定位只在特定组织和细胞状态中出现的衰老变化。"
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
      <span>Nature Immunology · 2025</span>
    </div>
    <h1>HumanImmuneAging_Atlas</h1>
    <p>Multimodal profiling reveals tissue-directed signatures of human immune cells altered with age</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41590-025-02241-4" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for HumanImmuneAging_Atlas">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/YosefLab/CZI-Immuneaging" target="_blank" rel="noopener noreferrer" aria-label="Open code for HumanImmuneAging_Atlas">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Human Immune Aging Atlas 方法解读：组织环境如何重塑免疫衰老

### 一句话理解

这项研究用 CITE-seq 同时测量同一免疫细胞的 RNA 和 127 种表面蛋白，在 24 位器官捐献者、14 个组织部位中建立 128 万细胞的图谱。分析先用多模态标志物精细区分免疫亚群，再用配对供体的跨组织设计把“组织效应”与“年龄效应”分开，最后通过 pseudobulk 混合模型、基因程序分解和 MrVI 反事实预测，定位只在特定组织和细胞状态中出现的衰老变化。

### 1. 为什么不能只研究外周血

免疫系统分布在血液、骨髓、脾、淋巴结、肺和肠道等环境中。同一种 T 细胞或巨噬细胞进入不同组织后，会受到迁移信号、抗原暴露、代谢物和局部细胞互作的影响。如果只采血，观察到的年龄差异可能只是循环细胞组成变化，也会遗漏肺巨噬细胞、肠道驻留 T 细胞等局部状态。

这篇论文最重要的设计优势是 matched donor：同一个捐献者提供多个组织。因此，组织之间的差异不必完全依赖不同人群的横截面对比。24 位供者年龄为 20–75 岁，男女分别为 14 和 10 人，来自美国和英国两个采集队列。主分析覆盖 10 个细胞数超过 75,000 的部位，另有肝、皮肤和结肠等低细胞数参考数据。

### 2. 输入数据：RNA、表面蛋白和受体序列

22 位供者使用 CITE-seq，同时获得基因表达和 127 个抗体标签；另外 2 位只有 scRNA-seq。部分样本还测量 TCR/BCR V(D)J 序列。三种信息承担不同角色：

- RNA 描述转录状态和连续的功能程序；
- ADT 表面蛋白帮助区分转录上相近、免疫表型不同的亚群；
- TCR/BCR 用于克隆型和克隆扩增分析。

图 2 直接展示了蛋白模态的必要性。例如 CD45RA 区分 naive、central memory、effector memory 与 TEMRA，CD69、CD103、CD49a 帮助定义组织驻留记忆 T 细胞，αβ/γδ TCR 蛋白又能避免仅凭 `TRDC` RNA 的误分。

### 3. 预处理和整合：哪些变化应被去除，哪些必须保留

本地仓库的 `data_processing/scripts/` 覆盖 Cell Ranger 后的数据处理、质控、样本合并和整合。核心步骤包括 Scrublet/SOLO 双细胞检测、CellTypist 辅助过滤、decontX 环境 RNA 校正，以及 scVI/TotalVI 潜空间训练。

标准化后的展示值可写为

$$
x_{g i}=\log\left(1+10^4\frac{C_{g i}}{T_{G i}}\right),
$$

其中 $C_{g i}$ 是细胞 $i$ 中基因 $g$ 的计数，$T_{G i}$ 是该细胞的 RNA 总计数。ADT 对应使用 $10^3$ 的缩放因子。实际 scVI/TotalVI 训练以计数生成模型为核心，标准化值主要服务于展示、阈值和部分下游分析，不能把两者混为同一个输入变换。

代码在 `process_sample.py` 中按 batch 调用 R 的 decontX，并将校正矩阵和污染比例写回 AnnData；在 `utils.py` 中根据是否有蛋白选择 SCVI 或 TOTALVI。整合配置明确设置供者 batch key、两层网络、负二项 RNA likelihood 和训练轮数。TotalVI 同时建模 RNA 与 ADT，可吸收抗体背景并保留联合生物信号。

论文用于全图谱展示的是 multi-resolution variational inference（MrVI）。它学习两个互补表示：样本相对不变的 $U$ 空间用于统一细胞状态，样本条件化的 $Z$ 空间保留供者差异。图 1b 中不同供者没有形成孤立大块，而图 1c 仍保持肺、肠和淋巴组织的分离，说明整合目标不是抹去组织生物学。

### 4. 多模态分类：MMoCHi 如何定义亚群

MMoCHi 使用分层分类树。每个节点先依据 RNA 和经 landmark registration 处理的蛋白阈值挑选高置信训练细胞，再训练随机森林把标签扩展到其余细胞。层级结构从主要谱系逐步细分，最终得到 13 个 T 细胞、5 个 NK/ILC、6 个 B 细胞和 7 个髓系亚群。

这种方法的优点是分类规则符合免疫学门控逻辑，同时允许模型综合多个标志物；风险是阈值和人工复核会影响标签。

### 5. 先量化组织效应，再寻找年龄效应

作者用 pseudobulk 避免把同一供者的成千上万个细胞错误当作独立生物重复。对某一谱系或亚群，将同一供者、同一组织的计数聚合，再用 dreamlet 的线性混合模型分析。概念上可写为

$$
y_{gd}=\beta_0+\beta_{\mathrm{tissue}}T_d+\beta_{\mathrm{age}}A_d+
\boldsymbol{\gamma}^{\mathsf T}\mathbf{c}_d+b_d+\varepsilon_{gd},
$$

其中 $y_{gd}$ 是基因 $g$ 在供者单位 $d$ 的 pseudobulk 表达，$\mathbf{c}_d$ 包括性别、CMV、测序化学和处理地点等协变量，$b_d$ 表示供者相关项。不同具体比较使用不同设计式，但共同原则是统计重复单位为供者而不是细胞。

组织分析采用“一个组织对其余组织”的差异表达，并把显著基因聚成 13 个模块，再在具体亚群中做 GSEA。图 3 和图 4 显示：肺巨噬细胞具有 PPARG、FABP4 等脂质代谢程序；肠道 T/NK 细胞具有 ITGA1、ITGAE、CXCR6 等驻留程序；淋巴结 T 细胞富集 TCF7、LEF1、CCR7 和 SELL。图 5a 的方差分解进一步表明，多数谱系中组织解释的表达变异远大于年龄。

### 6. scHPF：把大量差异基因压缩为共表达程序

单基因检验容易得到冗长列表，作者因此用 single-cell hierarchical Poisson factorization（scHPF）将计数矩阵近似分解为细胞因子分数与基因因子分数：

$$
X_{gi}\sim\operatorname{Poisson}\left(\sum_{k=1}^{K}\theta_{gk}\xi_{ki}\right).
$$

$\theta_{gk}$ 表示基因 $g$ 对程序 $k$ 的权重，$\xi_{ki}$ 表示细胞 $i$ 中该程序的活性。作者在多个 $K$ 和重复运行之间构建 consensus，以减少单次初始化造成的不稳定性；另建 tissue-balanced 和 donor-balanced 模型，分别服务于组织与年龄问题。

因子并不天然等于生物通路。论文先看高权重基因，再用 pseudobulk DE、GSEA、蛋白信号和外部队列验证。图 6 中 CD8 T 细胞的 GZMK 程序和 cytokine 程序随年龄增强，而 B 细胞 RAS 程序下降，就是这一证据链的例子。

### 7. MrVI 反事实：年龄变化是否只发生在亚群的一部分细胞

传统 pseudobulk 给出整个亚群的平均年龄效应，但一个注释亚群内部可能包含反应不同的细胞。作者在 CD4 T 细胞中利用 MrVI 的样本条件表示，估计同一细胞状态在“较年轻”和“较年长”条件下的预测差异，并对基因和细胞的效应矩阵做 spectral co-clustering。

可把每个细胞、基因的反事实效应概括为

$$
\Delta_{ig}=f_g(z_i,\text{age}>40)-f_g(z_i,\text{age}<40).
$$

这里 $f_g$ 是模型的条件化表达预测，不是对同一个人真实进行年龄干预。聚类后得到四组共同变化的基因和细胞，再用独立的 dreamlet pseudobulk 比较验证 module-positive 细胞。图 7 显示肺、肠和淋巴结中的 CD4 T 细胞具有不同年龄模块：肠道 Th17 相关程序下降，肺中细胞毒程序下降，淋巴结中调节相关信号下降而炎症相关信号上升。

### 8. 主要衰老结果应如何理解

#### 肺巨噬细胞

图 5 显示肺巨噬细胞的 APOE–TREM2 程序随年龄下降，并在独立肺图谱中得到方向一致的 GSEA。TREM2 与脂质感知和吞噬有关，因此作者提出这可能关联老年肺免疫功能下降；但图谱本身不能证明该程序下降直接导致感染或癌症风险。

#### CD8 T 细胞

GZMK 程序跨多个循环或淋巴组织亚群随年龄增加，cytokine 程序也增强；外部 PBMC 和肺数据提供验证。值得注意的是肺和肠的 TRM 并未表现同样强的 GZMK 年龄趋势，说明“免疫衰老”并非所有组织共享一个统一轨迹。CMV 相关 GNLY 程序与年龄程序有重叠但并不相同，模型中纳入 CMV 协变量就是为了降低混淆。

#### B 细胞

淋巴结 IgM memory B 细胞比例下降，RAS/BCR 相关程序随年龄减弱。论文在骨髓图谱和 PBMC 队列中观察到方向一致证据，但具体组织与亚群的效应大小并不完全相同。

### 9. TCR/BCR 分析

Dandelion 对 Cell Ranger contig 重新进行 IgBLAST 注释、V/J 检查、BCR 等位基因修正和克隆型归并。TCR 要求 CDR3 核苷酸完全一致，BCR 使用 85% 氨基酸相似阈值。克隆性使用 $1-$Pielou evenness：

$$
\mathrm{clonality}=1-\frac{H}{\log_2 C},
$$

其中 $H$ 是克隆频率的 Shannon entropy，$C$ 是克隆型数。值越高表示少数克隆占比越大。作者使用固定细胞数下采样来减少测序深度造成的偏差。本地代码能看到 VDJ 与 GEX 的合并，但完整 Dandelion 重注释流程不在该仓库中。

### 10. 论文与本地代码的对应范围

#### 可直接核对

- Cell Ranger 后的多库合并与质控：`CZI-Immuneaging/data_processing/scripts/`
- decontX 调用及污染矩阵回写：`process_sample.py`
- scVI/TotalVI 建模和潜空间保存：`utils.py`
- 供者 batch、网络层数、likelihood 和训练参数：`generate_integration_config_files_and_script.py`
- VDJ 数据与 AnnData 合并：`process_sample.py`、`vdj_utils.py`

#### 只能部分核对

- MrVI 训练和反事实分析位于 `downstream_mrvi/*.ipynb`，可以检查分析逻辑，但依赖外部数据和模型产物。
- dreamlet 分析位于 `pseudobulk_processing/*.ipynb`，不是统一的可执行流水线。
- popV 标签迁移在 `popv_figure2.ipynb`。

#### 本地仓库未完整提供

- MMoCHi 分层分类训练；
- consensus scHPF 的完整训练流水线；
- scCODA 组成分析；
- Dandelion 的完整重注释运行。

因此，这个代码快照对预处理最具可复现性，对论文主图分析属于 notebook/外部包驱动的部分复现。仓库还依赖 S3 路径、处理后 AnnData 和较大的 GPU 计算资源，不能视为下载后即可从 FASTQ 一键生成全部图表。

### 11. 阅读边界

1. 年龄分组是横截面比较，不是同一供者的纵向衰老轨迹。
2. 组织效应与年龄效应能通过配对设计和协变量降低混淆，但 24 位供者仍限制稀有亚群的统计能力。
3. MrVI 反事实是条件生成模型的预测，不等于真实干预因果效应。
4. scHPF 因子是数据驱动的共表达结构，通路名称来自后续基因和富集解释。
5. 外部队列验证支持方向的一致性，但平台、组织和细胞注释差异意味着效应量不可直接等同。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Human Immune Aging Atlas — summary.md

### Motivation & Novelty

**Biological problem**: The mammalian immune system is distributed across blood and multiple tissue sites (lymphoid organs, mucosal barriers), yet most human immunology studies focus on peripheral blood. This severely limits understanding of how immune cells actually function in tissues, how tissue environment shapes immune identity, and — critically — how aging affects immunity in the places where it matters most.

**Why existing methods fall short**:
- Blood-based studies (*Terekhova et al. Immunity 2023*, *Pereira et al. Nat Immunol 2020*) cannot reveal tissue-resident immune aging
- Previous organ donor T cell studies (*Poon et al. Nat Immunol 2023*, *Kumar et al. Cell Rep 2017*, *Thome et al. Cell 2014*) lacked myeloid and B cell coverage or multi-omics depth
- Cross-tissue transcriptomics (*Dominguez Conde et al. Science 2022*) lacked donor matching across age ranges or the proteome layer

**Unique contributions**:
1. Largest matched blood+tissue immune atlas: 1.28M cells, 14 tissue sites, 24 donors, 10 sites with >75k cells each
2. Multimodal (RNA + 127 proteins) enabling protein-level subset resolution beyond scRNA-seq alone
3. First systematic comparison of tissue vs. age effects across four major immune lineages (T, NK/ILC, B, myeloid)
4. Discovery of tissue-specific immune aging: APOE-TREM2 loss in lung macrophages, GZMK+ CD8+ T aging signature, RAS signaling decline in LN B cells, CD4+ T cell Th17 decline in gut

---

### Method Overview

#### Experimental Design
- 24 organ donors (10F/14M, age 20–75); NY (USA) and Cambridge (UK) cohorts
- CITE-seq with TotalSeq-A/C Universal Cocktail (127 proteins, 22 donors); scRNA-seq only for 2 donors
- 10 main sites: blood, BM, spleen, ILN/LLN/MLN, lung (BAL+parenchyma), jejunum (JEL+JLP)
- Additional: liver, skin, colon (9 donors; not in main analysis)

#### Computational Pipeline

**Integration**: MrVI (Ergen et al. *Nat Genet* 2024) with VampPrior and attention-based Z-space harmonizes donor and batch effects while preserving cell state variation. Outperforms scVI for cross-site/cross-cohort (US/UK) integration.

**Classification**: MMoCHi (Caron et al. *Cell Rep Methods* 2025) classifies 34 immune subsets using a random-forest hierarchy combining RNA and landmark-registered protein expression. Protein is essential for TRM/TN/TEMRA distinction, γδ T cell identification, and NK subset separation.

**Differential expression**: dreamlet (R package) pseudobulk linear mixed models (LMM) with donor as random effect, controlling for sex, CMV, chemistry, processing site. Two analyses: (1) tissue effects (one tissue vs rest), (2) age effects (<40 vs ≥40 years).

**Gene programs**: Consensus scHPF (Levitin et al. *Mol Syst Biol* 2019) factorizes raw counts into gene co-expression modules. Two model types — tissue-balanced (3 sites) and donor-balanced (aging) — run with K=15–30, 5 replicates each, walktrap consensus.

**MrVI counterfactuals**: Per-cell age effects in CD4+ T cells estimated by ridge regression on donor embedding displacement, then spectral co-clustering (4 gene × 4 cell clusters) identifies cell subpopulations with similar age-associated changes.

**VDJ analysis**: Dandelion (Suo et al. *Nat Biotechnol* 2024) reannotates TCR/BCR contigs via IgBLAST; TIgGER allele correction for BCR. Clonality = 1 − Pielou's evenness on 100-cell subsamples.

---

### Evaluation

#### Datasets
- **Primary**: 1.28M cells from 24 organ donors (main 10 sites); presented as .h5ad on CellXGene
- **Validation cohorts**:
  - Human Lung Atlas (Sikkema et al. *Nat Med* 2023, n=29): macrophage and CD8+ T aging
  - BM atlas (Lee et al. *Front Immunol* 2023, n=36–39): B cell aging
  - Human Immune Health Atlas / Sound Life (n=96, age 26–65): CD8+ T cytokine, GZMK+, B RAS signatures in PBMCs

#### Key Results

| Finding | Metric/Significance |
|---|---|
| Tissue explains majority of transcriptional variance | Variance decomp across all lineages: tissue>>age |
| 13 gene clusters spanning myeloid + T + B lineages | FDR<0.05, log2FC>1 |
| CD8+ TN↓ with age in blood+LN; TEM↑ blood; TRM↑ LN | GLM, adj P<0.05 |
| APOE-TREM2 signature ↓ in lung macrophages with age | LMM, validated in independent lung atlas |
| CD8+ GZMK+ signature ↑ with age across subsets/sites | scHPF + GSEA, validated in PBMC cohort |
| CD8+ cytokine signature (CCL3/CCL4/IFNG/TNF) ↑ with age | scHPF LMM, validated in lung atlas |
| IgM+ memory B cells ↓ with age in LN; RAS signaling↓ | LMM + scHPF, validated in BM atlas and PBMC |
| CD4+ T: Th17↓ in gut with age; cytotoxicity↓ in lung | MrVI counterfactuals, pseudobulk DE |
| CD4+ T: regulatory markers↓, inflammation↑ in LN | MrVI, trending across sites |
| CMV: GNLY+ CD8+ signature enriched in CMV+ donors | Distinct from but overlapping with GZMK+ age sig |
| TRM cells (lung+gut) do NOT show GZMK+ age signature | Site-specific protection or differential aging |

#### Biological Interpretations
- **APOE-TREM2 loss in lung macrophages**: TREM2 binds ApoE and promotes phagocytosis; loss with age may explain increased susceptibility to respiratory infections and lung cancer in elderly
- **GZMK+ CD8+ T cells**: matches conserved aging signature from mice (*Mogilenko et al. Immunity 2021*); NK-like functional shift
- **TRM cells spared from GZMK+ aging**: tissue environment may insulate from systemic inflammaging signals; mucosal barrier residency as age-protective niche
- **B cells → innate-like with age**: IL-18 increase, RAS/BCR signaling decrease parallels NK-like B cell phenotypes in disease contexts
- **LN T cells**: high TCF7/LEF1 (stem-like) expression suggests LNs as reservoir for long-lived memory; relevant for CAR-T therapy sourcing

---

### Reproducibility

**Rating: 3/5**

**Justification**: The data processing pipeline (align → QC → integrate) is fully implemented and well-documented in `data_processing/scripts/`. However, the core analytical steps producing paper figures (MMoCHi classification, scHPF training, dreamlet analysis, Dandelion VDJ, scCODA) are either external tools not in this repo or exist only in large (3–63 MB) Jupyter notebooks with data-dependent paths pointing to private AWS S3 buckets. Data is available on CellXGene (h5ad files) and GEO (GSE299043), but starting from raw FASTQ to reproduce figures requires access to proprietary AWS infrastructure and private config files.

**Strengths**:
- Complete raw data availability (SRA accession SRP559768)
- Processed h5ad files on CellXGene with fine-grained annotations
- Pre-trained popV and CellTypist label transfer models provided
- Detailed Methods section covering all analysis choices
- Config versioning system ensures exact parameter reproducibility

**Weaknesses**:
- MMoCHi hierarchy thresholds (Supplementary Table 3) are documented but training requires interactive GUI adjustment (not fully scriptable)
- scHPF, dreamlet analysis, MrVI counterfactuals not in scriptable form — notebook-only
- No `snakemake`/`nextflow` workflow tying steps together
- Requires expensive multi-GPU infrastructure for MrVI and TotalVI on 1.28M cells

**Setup**:
```bash
# Python environment
conda env create -f envs/immune_aging.py_env.v5.yml
conda activate immune_aging

# R environment
conda env create -f envs/immune_aging.r_env.v2.yml
Rscript envs/immune_aging.R_setup.v3.R

# External tools not in repo:
pip install mmochi           # MMoCHi
pip install schpf            # scHPF
pip install dandelion        # Dandelion/IgBLAST
```

**Data access**: h5ad files at https://cellxgene.cziscience.com/collections/cc431242-35ea-41e1-a100-41e0dec2665b

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
