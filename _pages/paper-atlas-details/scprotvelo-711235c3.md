---
layout: default
permalink: /paper-atlas/scprotvelo-711235c3/
title: "scProtVelo"
nav: false
wide: true
description: "scProtVelo 的关键不是把 RNA velocity 的标签换成“蛋白”，而是用共同潜在空间连接非同细胞的 RNA 与蛋白测量，以 mRNA 驱动蛋白的解析动力学和四状态概率混合解释翻译延迟，再把 \\kappa r-\\delta p 投影为局部细胞转移方向；它提供了蛋白层面的动态视角，但结论强度受跨模态配对、轨迹分段、尺度变换和恒速率假设共同限制。"
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
      <span>Science · 2025</span>
    </div>
    <h1>scProtVelo</h1>
    <p>Mapping early human blood cell differentiation using single-cell proteomics and transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1126/science.adr8785" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scProtVelo">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/theislab/scProtVelo" target="_blank" rel="noopener noreferrer" aria-label="Open code for scProtVelo">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scProtVelo：从单细胞 mRNA–蛋白动力学推断蛋白速度

### 先把论文和方法放在正确的位置

这篇 Science 论文首先是一项人造血干/祖细胞（HSPC）的单细胞蛋白质组资源研究：作者测量了 2500 余个 CD34+ 细胞、2900 余种蛋白，并与单细胞转录组和 CITE-seq 参考数据整合，用蛋白层面的差异揭示转录数据不易看到的早期分化信号。scProtVelo 是论文后段、主要对应图 7 的动力学方法贡献，不应把整篇论文缩写成“一个速度模型”。图 1–6 建立数据质量、跨模态图谱、分化生物学和功能验证；图 7 才回答：能否利用 mRNA 与蛋白之间的翻译延迟，给蛋白状态加上方向和速度？

这里的“配对”需要谨慎理解。蛋白质组细胞和转录组细胞并非同一细胞上的同步双测量；作者先用 GLUE 把不同模态投到共同潜在空间，再通过邻域插值构造计算上的成对 mRNA–蛋白表示。它是跨数据集匹配，不是实验上的同细胞配对。

### 为什么蛋白速度需要新的动力学方程

传统 RNA velocity 利用未剪接和已剪接 RNA 的时间差。scProtVelo 把上下游量改成 mRNA $r(t)$ 和蛋白 $p(t)$：

$$
\frac{dr}{dt}=\alpha-\beta r,
$$

$$
\frac{dp}{dt}=\kappa r-\delta p.
$$

$\alpha$ 是转录产生率，$\beta$ 是 mRNA 降解率，$\kappa$ 是翻译率，$\delta$ 是蛋白降解率。第二式中的蛋白变化取决于当前 mRNA 提供的合成通量 $\kappa r$ 与蛋白降解通量 $\delta p$ 的差。这使“mRNA 已经变化、蛋白尚未跟上”的时间延迟成为方向信息。

给定初始表达 $(r_0,p_0)$ 和一段内恒定的速率，mRNA 的解析解是

$$
r(t)=r_0e^{-\beta t}+\frac{\alpha}{\beta}(1-e^{-\beta t}).
$$

蛋白解还包含由 mRNA 驱动的耦合项：

$$
p(t)=p_0e^{-\delta t}+\frac{\alpha\kappa}{\beta\delta}(1-e^{-\delta t})
+\frac{\kappa(r_0\beta-\alpha)}{\beta(\delta-\beta)}(e^{-\beta t}-e^{-\delta t}).
$$

最后一项正是两种衰减时间尺度叠加产生的延迟。源码在 `scprotvelo/_module_scprotvelo.py:581-612` 直接实现这两个解析解；代码沿用 veloVI 命名，把论文的蛋白降解率 $\delta$ 写成 `gamma`，不是另一种生物学参数。分母加入 `1e-6` 并对 `gamma == beta` 单独处理，这是数值保护；它也提示完全相等速率的极限并未以解析极限公式实现，解释个别基因拟合时应保留这一实现边界。

### 一个细胞为什么有四种候选状态

单个表达点不足以唯一决定它处于上升还是下降阶段。模型因此将每个基因的观测表示成四个成分的混合：低表达稳态、诱导动态、高表达稳态和抑制动态。诱导分支从低表达初值出发，抑制分支先计算到切换时间 $t_s$ 的高表达状态，再沿抑制动力学前进。源码中四个均值的固定顺序是 `[rep_ss, ind, ind_ss, rep]`（`_module_scprotvelo.py:457-579`）。

这不是先用阈值给每个细胞贴上四分类标签。模型同时学习：

- 基因更偏向诱导还是抑制分支的全局混合权重；
- 每个细胞–基因在动态态和稳态之间的局部权重；
- 细胞潜在时间、各基因速率与观测噪声。

这些权重用 Dirichlet 分布参数化，四个解析轨迹作为高斯混合分布的均值。因而“状态”是后验概率，而非直接观测事实。代码还有三个 `alpha` 分量：诱导段、用于生成抑制初值的上升段、实际抑制段；这比把论文文字简单理解为两个 $\alpha$ 更具体，应以源码行为为复现依据。

### 从 GLUE 表示到时间、状态和动力学参数

预处理首先在轨迹相关细胞中筛选两模态共有基因，分别归一化和邻域平滑，再在 GLUE 空间做跨模态邻居插值，最后按基因 IQR 缩放并筛选差异基因（`scprotvelo/_data_processing.py:8-252`）。IQR 缩放会让不同量级基因在高斯似然中更接近等权；因此模型中的数值速率依赖这套尺度，不能直接当作未经缩放的绝对生化速率。

VAE 编码器只接收 GLUE embedding，而不是直接把原始 mRNA 和蛋白表达送入编码器（`_module_scprotvelo.py:615-652`）。编码器得到细胞潜变量 $z_i$，解码器再产生潜在时间和局部状态混合参数；基因级动力学参数则作为可学习参数存在。解码后，解析 ODE 给出四个候选 mRNA/蛋白均值，混合似然判断哪个分支和状态更能解释观测。

训练目标可读成四组约束的合计：mRNA 与蛋白重建负对数似然；$z$ 和 Dirichlet 状态权重的 KL 正则；保证初末状态与动力学关系合理的参数/端点惩罚；可选的扩散伪时间先验。源码的实际加权和始终是最终复现合同（`_module_scprotvelo.py:654-768`），不能仅凭论文概念图推断损失权重或训练阶段。

模型支持两种重要用法。基因特异时间允许每个基因有自己的动力学进度，适合拟合相位图；共享时间则让一个细胞的基因共用时间，并可加入 DPT 先验，适合比较预测蛋白表达的解释度。二者回答的问题不同，不应把某一模式的结果泛化为另一模式的严格验证。

### 速度如何变成细胞方向

拟合后，蛋白速度就是方程右端：

$$
v_p=\frac{dp}{dt}=\kappa r-\delta p.
$$

正值意味着按当前拟合参数蛋白趋向增加，负值意味着趋向减少。用户接口在 `scprotvelo/_model_scprotvelo.py:211-362` 计算速度，且可根据后验状态处理诱导/抑制分支。论文按拟合似然选择高可信基因用于速度图；这一步减少差拟合基因的干扰，但“似然高”只表示模型较好解释数据，并不自动证明方向在生物学上正确。

速度图沿用 scVelo 风格：在邻居图中比较当前细胞速度向量 $v_i$ 与候选状态差 $x_j-x_i$ 的余弦相似度（`scprotvelo/_velocity_graph.py:192-269,276-305`）。因此箭头是“在选定表示、基因和邻居图下，与模型速度最一致的局部转移”，不是被直接追踪到的真实谱系，也会受邻域构建和基因筛选影响。

### 从图 1 到图 7 应怎样读

- 图 1 建立 scp-MS 数据规模、覆盖率和质量控制。单细胞蛋白质组高度稀疏，论文报告每细胞约 68% 缺失；后续整合和插值是必要步骤，同时也是不确定性来源。
- 图 2 展示跨模态整合与主要 HSPC 群体，说明蛋白和 RNA 数据可在共同结构中对齐，但不等于逐细胞真实配对。
- 图 3–5 比较 RNA 与蛋白层面的分化信号，突出仅看转录本会漏掉或低估的蛋白调控。
- 图 6 用 CRISPR/Cas9 实验检验 SOD1、SOD2、TALDO1、H1F0 等候选因子的功能影响，把图谱关联推进到功能证据。
- 图 7 才是 scProtVelo 的核心证据链：先展示 mRNA–蛋白延迟和代表性基因相位拟合，再比较模型的基因状态与翻译速度方向，最后以预测蛋白表达的解释方差同线性基线比较。

图 7 的结果支持“显式动力学优于静态线性 mRNA–蛋白关系”这一论文内比较，但并不等于在所有组织、所有分支或所有蛋白上都优于其他速度方法。论文也指出完整 HSPC 层级含多分支，恒定基因速率假设难以同时覆盖，因此在红系等聚焦轨迹上拟合更合理。

### 复现与解释边界

2. `setup.py` 没有声明发布版本和依赖；`scprotvelo/__init__.py` 从已安装包元数据读取版本。因此不能从当前源码文本断言包版本。根目录 `environment.yml` 才是较完整的环境快照，包含 Python 3.9.15、scanpy 1.9.1、scvelo 0.3.2 等固定依赖。
4. 模型假设每个聚焦轨迹片段内基因速率恒定、解析 ODE 足以描述 mRNA–蛋白关系。分支、细胞类型特异速率、翻译后调控和测量缺失都可能违反假设。
5. GLUE 对齐、邻域插值、IQR 缩放、差异基因/似然基因筛选和速度图邻域都会影响最终箭头；速度是整条计算链的结果，不能只归因于 ODE。

### 一句话总结

scProtVelo 的关键不是把 RNA velocity 的标签换成“蛋白”，而是用共同潜在空间连接非同细胞的 RNA 与蛋白测量，以 mRNA 驱动蛋白的解析动力学和四状态概率混合解释翻译延迟，再把 $\kappa r-\delta p$ 投影为局部细胞转移方向；它提供了蛋白层面的动态视角，但结论强度受跨模态配对、轨迹分段、尺度变换和恒速率假设共同限制。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scProtVelo: Single-cell Protein Velocity for Mapping Blood Cell Differentiation

### Executive Summary

**Title**: Mapping early human blood cell differentiation using single-cell proteomics and transcriptomics
**Journal**: Science, 2025
**DOI**: 10.1126/science.adr8785
**Authors**: Furtwängler, Üresin, Richter, Schuster, Barmpouri, Holze, Wenzel, Grønbæk, Theilgaard-Mönch, Theis, Schoof, Porse

**Data availability**: Raw scp-MS + scRNA-seq in EGA under accession EGAS00001007930; processed data and scProtVelo on Zenodo (doi: 10.5281/zenodo.15554000)
**Code**: https://github.com/theislab/scProtVelo (Python package)

---

### Motivation & Novelty

#### The Core Problem

Single-cell transcriptomics has revolutionized understanding of hematopoiesis, revealing gradual transitions and differentiation trajectories in the human HSPC compartment. However, mRNA is a proxy for protein abundance — the actual functional molecule — and this proxy is imperfect. Bulk multi-omics studies had already shown that mRNA-protein correlations are typically low (r < 0.4 for many genes), and that the proteome reveals phenotypical information inaccessible to transcriptomics. But two major gaps remained:

1. **No single-cell proteomics atlas of in vivo human HSPC differentiation** existed at the scale needed to study cell state heterogeneity
2. **No method existed to model translation dynamics** from unpaired single-cell mRNA and protein data, analogous to how RNA velocity models splicing kinetics

#### Why Existing Methods Fall Short

- **scRNA-seq / RNA velocity** (La Manno et al., *Nature* 2018; Bergen et al., *Nat. Biotechnol.* 2020; Gayoso et al., *Nat. Methods* 2024): Purely transcriptomic; misses protein-level regulation. RNA velocity on erythroid differentiation is known to produce erroneous backflow vectors (Bergen et al., *Mol. Syst. Biol.* 2021).
- **CITE-seq** (Stoeckius et al., *Nat. Methods* 2017): Antibody-based surface markers only; targeted, not untargeted; no temporal modeling of translation dynamics.
- **Bulk proteomics** (Amon et al., *Mol. Cell Proteomics* 2019; van den Berg et al., *PLOS Genet.* 2023): Population-level averages lose single-cell heterogeneity; temporal modeling has been done at bulk level but not translated to single-cell resolution.
- **veloVI** (Gayoso et al., *Nat. Methods* 2024): RNA velocity VAE that scProtVelo directly extends — but handles only the mRNA-mRNA (unspliced-spliced) dynamics, not mRNA-protein translation dynamics.

#### Unique Contributions

1. **Largest scp-MS dataset of human HSPCs**: 2,934 proteins × 2,506 cells recapitulating the HSPC hierarchy — substantially larger than prior scp-MS studies
2. **Multi-omics single-cell integration**: Unpaired scp-MS + CITE-seq integrated via GLUE → joint trajectory analysis outperforms either modality alone (lineage assignment accuracy: 65%→95% for protein cells)
3. **scProtVelo algorithm**: Translation kinetics VAE that models mRNA-protein temporal dynamics at single-cell resolution; 40% improvement in explained protein variance vs linear correlation
4. **Protein-level HSC biology**: Proteins not apparent from mRNA (SOD1, SOD2, TALDO1, H1F0) validated as functionally important for HSC activity by CRISPR/Cas9 knockout
5. **Framework for multi-omics velocity studies** across biological systems beyond hematopoiesis

---

### Method Overview

#### Two-Level Architecture

The paper contributes at two levels: (1) an experimental and integrative pipeline to generate and analyze a human HSPC multi-omics atlas, and (2) scProtVelo, a computational method for modeling translation dynamics.

**Experimental pipeline:**
1. scp-MS of CD34+ bone marrow cells (6 donors, FACS-sorted, 384-well plate, SCoPE-MS with RETICLE acquisition)
2. SCeptre processing: batch correction, median-ratio normalization, UMAP/Leiden clustering
3. CITE-seq of CD34+ cells (4 donors, 10x Genomics 3' v3, totalVI integration)
4. GLUE integration (Cao & Gao, *Nat. Biotechnol.* 2022): VAE-based unpaired multi-omics integration creating a joint latent space
5. CellRank trajectory analysis (Lange et al., *Nat. Methods* 2022; Weiler et al., *Nat. Methods* 2024) on the joint latent space

**scProtVelo computational method:**
- Extension of veloVI (Gayoso et al., *Nat. Methods* 2024) to model mRNA-protein dynamics instead of unspliced-spliced dynamics
- 4-state generative model: induction steady/dynamic × repression steady/dynamic
- Coupled ODE system with closed-form analytical solutions
- VAE inference using GLUE joint embedding as encoder input
- Two configurations: individual gene times (trajectory inference) vs shared time with DPT prior (variance explanation)

See `doc_method.md` for the full mathematical framework.

#### Key Biological Assumption

Constant (time-independent) kinetic rates per gene within a trajectory segment. This is reasonable for short differentiation windows (erythroid, pre-mDC), but not for the full HSPC hierarchy (where rate changes are known, especially during HSC exit from quiescence). The paper acknowledges this limits simultaneous multi-trajectory modeling.

---

### Evaluation

#### Datasets

| Dataset | Cells | Features | Use |
|---------|-------|----------|-----|
| scp-MS primary | 2,506 | 2,934 proteins | Main HSPC atlas |
| scp-MS secondary | 922 | 2,174 proteins | MEP refinement (CD71/BAH-1) |
| CITE-seq | 9,086 | 5,820 genes + 44 ADTs | mRNA reference |
| External bulk | HSC, MEP, CMP, GMP | — | Benchmark scp-MS accuracy |
| Erythroid scProtVelo | 472 (prot) + 1,677 (RNA) | 146 genes | Translation dynamics |
| Pre-mDC scProtVelo | 262 (prot) + 897 (RNA) | 46 genes | Translation dynamics |

#### Key Results

**1. scp-MS data quality:**
- Batch effects removed (PC regression: MS run, TMT label, donor, age each explain <5% variance)
- Protein log2 fold-changes correlate strongly with bulk proteomics reference (Pearson > 0.7 for matched populations)
- UMAP embedding recapitulates HSPC hierarchy

**2. Multi-omics integration quality:**
- GLUE silhouette score = 0.03 (well-mixed protein and mRNA cells)
- Cell type separation (NMI, ARI) preserved before and after integration in both modalities
- CellRank on joint space: 6 terminal states correctly identified; lineage assignment improved from 86%→91% (mRNA cells) and 65%→95% (protein cells) vs individual modalities

**3. Biology: protein-level insights:**
- mRNA-protein correlation in early HSC differentiation: r ≈ 0.06-0.25 (very low)
- Concordance is higher in lineage specification (r ≈ 0.7 for erythroid)
- Proteins unique to scp-MS analysis: SOD1, SOD2, SOD2, TALDO1, H1F0 (not well-captured by mRNA)
- CRISPR functional validation:
  - TALDO1 KO: LTC-IC frequency 1/42 (vs 1/14 control)
  - H1F0 KO: LTC-IC frequency 1/80
  - SOD1 KO: LTC-IC frequency 1/153; near-complete colony formation failure
  - SOD2 KO: similar to SOD1 KO phenotype, without proliferative block

**4. scProtVelo performance:**
- Gene state inference (activation vs repression): accuracy ~0.8 for top-25 likelihood genes vs ~0.4 random baseline
- Velocity-based trajectory: correctly recapitulates erythroid HSC → EMP → Early/Late Eryth progression
- RNA velocity (veloVI) comparison: erroneous backflow from Late to Early Eryth; scProtVelo avoids this
- Explained protein variance: median R² 36% (linear model) → 50% (scProtVelo), p < 0.001, ~40% relative improvement

---

### Reproducibility Rating: 4/5

| Category | Score | Notes |
|----------|-------|-------|
| Data availability | 5/5 | Raw data in EGA (EGAS00001007930); processed data on Zenodo |
| Code completeness | 4/5 | Core VAE package complete; downstream CellRank/GLUE steps require separate setup |
| Documentation | 3/5 | README minimal; notebooks are the main guide; no step-by-step tutorial |
| Environment | 4/5 | `environment.yml` provided; pinned dependencies (torch 2.3.1, scvi-tools 1.1.5) |
| Accessibility | 3/5 | Requires custom data pairing step; scProtVelo input format not trivially constructed |

**Practical notes for reproduction:**
- Requires access to the Zenodo data (processed scp-MS h5ad, CITE-seq h5ad, GLUE combined object)
- The `pair_data()` function in `_data_processing.py` requires specific AnnData attributes: `batchcorr_norm_log2_nan` layer (protein), leiden clusters aligned to combined GLUE object
- Two notebook configurations: `1_*` (individual gene times, trajectory inference) and `3_*` (shared time with DPT prior, variance analysis)
- scvi-tools 1.1.5 API: uses `LossOutput` dataclass; incompatible with scvi-tools >= 2.0

**Strengths:**
- All raw data deposited in controlled-access repository (EGA)
- Processed data and model weights on Zenodo
- Core model is a clean Python package with standard scvi-tools API

**Weaknesses:**
- 68% missing values in scp-MS require careful handling; not all downstream analyses handle NaN consistently
- The 15-NN imputation creates artificial cell pairs that may not truly represent single-cell biology
- The variance analysis (Fig 7E-G) requires the DPT-constrained model configuration, which uses a different training regime from the trajectory inference configuration — this is not clearly distinguished in the paper

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
