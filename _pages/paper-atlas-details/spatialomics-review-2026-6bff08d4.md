---
layout: default
permalink: /paper-atlas/spatialomics-review-2026-6bff08d4/
title: "SpatialOmics_Review_2026"
nav: false
description: "这是一篇综述，不是提出单一算法的原始研究。它试图把空间组学领域拆成一条连续证据链：先选择能回答问题的测量技术，再经过分割、质控、增强和细胞注释，把局部邻域组织成生态位、空间群落与肿瘤生态系统，最后讨论这些结构怎样用于早期演化、转移、微小残留病灶、疗效预测和功能验证。全文的核心不是“哪一个平台最好”，而是不同生物问题需要不同的空间尺度、分子覆盖度、样本兼容性和验证强度。 空间转录组可粗分为成像式和测序式两类。"
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
      <span>Technology Platforms</span>
      <span>Cancer Cell · 2026</span>
    </div>
    <h1>SpatialOmics_Review_2026</h1>
    <p>Spatial omics at the forefront: emerging technologies, analytical innovations, and clinical applications</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.ccell.2025.12.009" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 空间组学综述：如何从技术选择走到可验证的临床结论

### 这篇文章在解决什么问题

这是一篇综述，不是提出单一算法的原始研究。它试图把空间组学领域拆成一条连续证据链：先选择能回答问题的测量技术，再经过分割、质控、增强和细胞注释，把局部邻域组织成生态位、空间群落与肿瘤生态系统，最后讨论这些结构怎样用于早期演化、转移、微小残留病灶、疗效预测和功能验证。全文的核心不是“哪一个平台最好”，而是不同生物问题需要不同的空间尺度、分子覆盖度、样本兼容性和验证强度。

### 第一层：测量技术回答的是不同问题

空间转录组可粗分为成像式和测序式两类。成像式方法在组织中逐轮读取预先设计的探针，单细胞或亚细胞定位较直接，但通常受面板设计、杂交轮数和成像时间限制。测序式方法先在有空间坐标的阵列上捕获 RNA，再回收到测序仪中读取，覆盖面更广，但一个捕获点或一个 bin 并不天然等于一个细胞。论文列出的 5K、6K、18K 等规模和 55 μm、2 μm、500 nm 等尺寸，是综述汇总的平台参数，不应当解释为所有实验条件下都能达到的有效单细胞分辨率。

空间蛋白组的优势是直接靠近功能分子层。荧光循环、寡核苷酸条形码抗体和金属同位素成像各自在通量、空间分辨率、抗体共存与光谱串扰方面取舍不同。这里最容易忽略的限制是抗体本身：抗体的特异性、组织固定后的表位保存和批次校准，会直接限定下游结论的可信度。

空间代谢组以 MALDI、DESI、SIMS 等质谱成像路线为主。它能直接观察代谢物或脂质的空间异质性，但分子鉴定、离子抑制、覆盖范围和空间分辨率之间存在强烈权衡。更高的像素分辨率不等于更完整的代谢物覆盖。

同切片多组学避免了相邻切片之间的错位，但不同检测化学可能彼此干扰；连续切片整合更容易实施，却要承担组织形变和细胞不一一对应的问题。三维重建进一步放大了配准误差。因此，多模态和三维结果必须把“实际共同测得的信号”与“经过模型补全或对齐的信号”明确区分。

### 第二层：计算流程不是中性的搬运步骤

图 2 给出的流程可以从左向右理解为：

1. 从原始图像或阵列信号中分割细胞并完成质控、归一化和扩散校正。
2. 在需要时进行分辨率增强、表达补全或跨模态特征增强。
3. 给细胞或空间单元赋予类型，并分析亚细胞定位和细胞间通信。
4. 把局部邻域归纳为生态位，再向上组织为空间群落和生态系统。
5. 对肿瘤细胞推断拷贝数变异、克隆和状态，或进行跨切片、跨平台和三维整合。

这条链条中，上游误差会向下游传播。例如，两个相邻细胞若被错误合并，其表达谱会混合，细胞类型可能被错注，邻域组成和配体—受体关系也会随之改变。分辨率增强同样需要谨慎：模型把一个点拆成更细的表达单元，是基于图像、邻居或参考数据的推断，并不是重新测量了更多分子。

细胞类型解卷积依赖参考图谱；参考中缺失的状态不可能被可靠恢复。空间配体—受体分析能提出“哪些细胞可能在何处通信”的假设，但空间邻近、配体表达和受体表达本身不能证明信号确实发生。基于表达推断肿瘤 CNV 或克隆结构也需要 DNA、病理或其他正交证据验证。

基础模型可以把病理图像、转录组和空间上下文压缩为可迁移表示，但综述中的这些模型仍主要代表快速发展的研究方向。跨癌种、跨中心、跨平台的域偏移以及可解释性和外部验证，决定它们能否进入临床，而不是模型规模本身。

### 第三层：从细胞到生态系统的四级组织

图 4 给出全文最重要的概念层级：单个细胞形成局部生态位，若干生态位以稳定的邻接方式组成空间群落，多个群落共同构成肿瘤生态系统。图中的多重免疫荧光和组织示意图用于说明这种层级阅读方式，不是对某个通用生态系统分类器的独立临床验证。

图 3 汇总九类常见肿瘤微环境生态位：三级淋巴结构、血管周围、干样 CD8 T 细胞、CAF 相关、侵袭前沿、免疫排斥、缺氧、神经免疫和微生物相关生态位。这是综述根据多项研究整理出的实用分类，不是穷尽列表，也不意味着这些生态位在所有癌种中具有相同边界和功能。

阅读这九类生态位时应区分三层证据：图中画出的结构关系、综述引用的关联、原始研究中的干预或随访证据。例如，CAF 屏障、CXCL12–CXCR4 或 TGF-β 与免疫排斥之间的联系可形成治疗假设；只有当对应研究提供干预和结果证据时，才能进一步谈恢复浸润或改善疗效，不能由示意图本身推出因果结论。

### 第四层：临床转化首先是研究设计问题

图 5 是路线图，而不是已部署临床流程。文章把应用场景组织为早期肿瘤发生、转移、微小残留病灶和治疗反应，并强调横断面多患者队列与纵向治疗前后采样的互补性。空间组学可发现候选结构，但真正可转化的标志物通常需要被压缩为更便宜、更稳定的检测形式，例如少量蛋白面板、病理图像特征或组织/液体联合指标，再经过独立队列和前瞻性验证。

一个可靠的临床证据链应当是：发现队列提出空间结构，独立队列复现，正交检测确认关键分子或克隆，机制实验检验因果，最后在预先定义终点的临床研究中评估增益。样本保存方式、FFPE 兼容性、批次效应、病理区域选择和治疗时间点都可能改变结果。因而“能够画出高维空间图谱”与“能够指导患者决策”之间仍有明显距离。

### 如何按问题选择方案

| 研究问题 | 优先能力 | 主要代价 | 必做验证 |
|---|---|---|---|
| 稀有细胞状态与亚细胞 RNA 定位 | 成像式空间转录组、较高空间分辨率 | 靶向面板与成像时间 | 探针特异性、独立样本复现 |
| 无偏发现新通路 | 测序式空间转录组、较宽基因覆盖 | 捕获单元混合、解卷积依赖 | 单细胞参考、原位验证 |
| 免疫表型和蛋白功能邻域 | 多重空间蛋白组 | 抗体面板与批次校准 | 抗体验证、病理复核 |
| 代谢梯度或药物分布 | 质谱成像 | 分子鉴定与覆盖度权衡 | 标准品或正交质谱 |
| 多模态同细胞关系 | 同切片多组学 | 检测化学干扰、成本 | 模态间质控、原始信号与推断分开 |
| 三维侵袭和克隆结构 | 连续切片或厚组织三维成像 | 配准、形变与计算量 | 标志点检查、DNA/病理验证 |
| 临床预测 | 可扩展面板和多中心队列 | 域偏移与样本流程差异 | 独立、前瞻性、增益验证 |

### 最终阅读边界

这篇综述最可靠的用途是建立技术地图、计算流程和证据层级，并据此设计实验。它汇总了大量代表性方法和疾病实例，但平台参数会更新，文章中的临床示例强度也不一致。图 1–5 是领域综合图：它们支持分类、工作流和研究路线的理解，却不能替代被引用原始研究中的样本量、统计检验、干预和结局证据。使用本文做方法选择时，应回到相应原始论文和最新版平台文档核对参数；使用它提出临床结论时，应明确哪些是观察关联、哪些有机制验证、哪些仍是未来方向。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary: Spatial Omics at the Forefront — Liu et al., Cancer Cell 2026

**Paper**: Liu Y, Dai Y, Wang L. "Spatial omics at the forefront: emerging technologies, analytical innovations, and clinical applications." *Cancer Cell* 44:24-49, 2026.
**DOI**: 10.1016/j.ccell.2025.12.009
**Type**: Comprehensive review
**Scope**: Technologies + analytics + TME biology + clinical translation in cancer spatial omics

---

### Motivation & Novelty

#### Biological Problem

Cancer is profoundly shaped by spatial context. The tumor microenvironment (TME) — composed of immune cells, fibroblasts, endothelial cells, extracellular matrix, and tumor subclones — is organized into functionally coordinated spatial architectures that determine immune evasion, tumor evolution, and therapeutic response. Single-cell RNA sequencing revealed molecular heterogeneity but sacrificed spatial context: we knew *what* cells were in a tumor but not *where* they were, *who* they talked to, or *how* they were organized into functional niches.

#### Limitations of Prior Reviews

Prior spatial omics reviews focused on specific modalities or computational methods in isolation. Earlier reviews (Chen et al., *Nat. Rev. Clin. Oncol.* 2024; Elhanani et al., *Cancer Cell* 2023; Moffitt et al., *Nat. Rev. Genet.* 2022; Tian et al., *Nat. Biotechnol.* 2023) addressed portions of the landscape but did not synthesize:
- The latest commercial platforms (including CosMx WTX ~18,000 genes, Xenium Prime 5K, Visium HD, Trekker)
- The rapidly emerging category of spatial foundation models (UNI, KRONOS, scGPT-spatial, NicheFormer, Novae)
- A systematic 9-niche taxonomy of the TME with mechanistic details
- A structured clinical roadmap connecting study design → assay selection → analysis → translation

#### Unique Contributions of This Review

1. **Up-to-date platform taxonomy** with quantitative capability comparison across transcriptomics (cyclic decoding, cyclic sequencing, barcode-to-cell, tissue-on-array), proteomics (cyclic fluorescence, IMC, label-free), metabolomics (MALDI-IMS, DESI, SIMS), multi-omics, and 3D approaches
2. **Systematic 9-niche framework** for TME organization with clinical correlates for each niche type
3. **Foundation model landscape** in spatial omics (histology-centric, histology-to-omics, omics-centric)
4. **Clinical roadmap** with practical guidance on specimen scale, preservation method, and study design-to-analysis alignment
5. **Emerging translational applications**: pre-cancer atlas, MRD spatial profiling, spatial perturbation genomics (Perturb-map, BaSISS)

---

### Method Overview

#### Spatial Technology Taxonomy

This review organizes the rapidly expanding spatial omics landscape into a structured taxonomy:

**Spatial Transcriptomics** (Figure 1A):
- *Cyclic combinatorial decoding*: Xenium In Situ (5K genes), CosMx (6K–18K genes WTX) — subcellular resolution, FFPE-compatible; differ in probe design (RCA vs. scaffold-based amplification)
- *Cyclic in situ sequencing*: Singular G4X (direct sequencing including TCR/BCR, ~350 genes) — enables variant calling but constrained by short reads
- *Barcode-to-cell*: Slide-tag, Trekker — true single-cell spatial resolution paired with whole-transcriptome scRNA-seq
- *Tissue-on-array capture*: Visium (55 μm), Visium HD (2 μm bins), Stereo-seq (500 nm) — whole transcriptome but bin ≠ cell (critical limitation)

**Key resolution–coverage trade-off**: High gene coverage (whole transcriptome) is currently coupled to lower spatial resolution (capture-based methods), while high resolution imaging methods require targeted panels. CosMx WTX is an emerging exception, offering near-whole transcriptome at subcellular resolution.

**Spatial Proteomics** (Figure 1B):
- PhenoCycler-Fusion 2.0: 60-plex cyclic fluorescence (gold standard multiplexed protein)
- IMC (Standard BioTools): 40+ proteins, metal-conjugated antibodies, mass spectrometry detection — no spectral overlap, ~1 μm resolution
- COMET (Lunaphore): iterative 2-antibody-at-a-time approach — eliminates cross-reactivity issues
- Most platforms capped at 20–60 proteins by antibody availability and spectral constraints

**Spatial Metabolomics** (Figure 1C): MALDI-IMS (10–50 μm, most established), DESI (ambient, clinical-compatible), SIMS (submicron, limited coverage), timsTOF fleX MALDI-2 (ion mobility, enhanced coverage)

**Multi-omics and 3D** (Figures 1D, 1E): Spatial CITE-seq, DBiT-seq/Patho-DBiT (whole transcriptome + >100 proteins, FFPE); 3D via serial sections + co-registration or non-disruptive volumetric methods (light-sheet microscopy, holotomography)

#### Analytical Framework

The review covers a comprehensive computational pipeline (Figure 2):

1. **Cell segmentation**: StarDist (nuclear), Cellpose/DeepCell (dual-channel), Segger (transcript-aware)
2. **Preprocessing**: diffusion correction (SpotClean, BayesTME, SPLIT); normalization (SpaNorm GLM-based, SpatialPCA spatial kernel)
3. **Resolution enhancement**: SpaGCN, TESLA (GCN-based sub-spot splitting), iSTAR (pixel-level transformer-based imputation); Bin2cell/SMURF (cell reconstruction from Visium HD bins)
4. **Cell phenotyping/deconvolution**: BANKSY (neighborhood-aware typing), cell2location/Tangram/Cytospace (reference-based deconvolution)
5. **Cell-cell communication**: COMMOT (optimal transport), NCEMs/NEST (graph-based), NicheNet/SpaTalk (downstream gene expression linking)
6. **Spatial niche identification**: UTAG, CellCharter, scNiche, NicheCompass
7. **Spatial trajectories**: Spateo (2D/3D RNA velocity), TopoVelo, stLearn PSTS
8. **CNV/clonal architecture**: CopyKAT, SpatialInferCNV, stSNV — all require orthogonal validation
9. **Foundation models**: UNI (H&E), KRONOS (fluorescence), scGPT-spatial, NicheFormer, Novae — supporting cross-platform integration, spatial domain ID, gene expression imputation
10. **Multi-modal integration**: PASTE (same-platform + optimal transport), SpaMosaic (cross-platform GNN + contrastive), MISO (multi-omics spatial graph embedding)

#### TME Niche Framework (9 Types, Figure 3)

The paper provides detailed mechanistic descriptions of nine spatially distinct TME niches, each with clinical relevance:

1. **Tertiary Lymphoid Structures (TLS)**: B cell maturation sites; plasma cells migrate along CXCL12+ fibroblastic tracks; IgG deposition on tumor cells → apoptosis in RCC; CXCL13+ CAFs + CXCL13+ CD8+ T cells in nasopharyngeal cancer; suppressed by cancer-educated mesenchymal stem cells in ovarian cancer
2. **Perivascular niches**: DC-T cell interaction hubs for antigen presentation; collagen-rich ECM rim in recurrent GBM; VEGFA+ macrophage–CD34+ endothelial cell interactions in HCC
3. **Stem-like CD8+ T cell niches**: TCF1+CD28+ cells with asymmetric division; cDC crosstalk via CXCL9/IL-15/CCL19/21; absent in immune evasion; FLT3L/CD40 activation expands this niche
4. **CAF-related niches**: Four conserved organizational patterns (s1–s4) defined by neighboring cell composition (Liu et al., *Cancer Cell* 2025); matrix CAFs create immune exclusion barriers; inflammatory CAFs secrete CXCL12/IL-6/TGF-β
5. **Tumor invasive front**: TAM/Treg/neutrophil enrichment; stem-like/hypoxic cancer cell reprogramming; checkpoint upregulation
6. **Immune-excluded niches**: T cells at margins, not parenchyma; CAF barriers, CXCL12-CXCR4 axis, TGF-β, and CD47-THBS1 are reviewed as candidate mechanisms. Evidence for restoring infiltration by pathway blockade comes from the cited studies, not from the schematic itself.
7. **Hypoxic niches**: SPP1+ TAMs co-localize with CAFs → immune exclusion in HCC; quiescent/chemoresistant tumor cells; pro-tumorigenic neutrophil reprogramming
8. **Neuroimmune interface**: Neurotransmitter/neuropeptide signaling shapes immunity; non-invaded nerves with TLS vs. invaded nerves with NLRP3+ TAMs/myCAFs in PDAC
9. **Microbiota-residing niches**: *Fusobacterium* → cancer cell quiescence and chemoresistance; *Akkermansia muciniphila* → antitumor via glutamate metabolism; bacteria-rich niches are immunosuppressive

#### From Niches to Tumor Ecosystems (Figure 4)

A key conceptual contribution is the multi-scale organizational framework: individual cells → cellular niches → spatial communities → tumor ecosystems. Clinically relevant biology emerges at the ecosystem level: how niche-community configurations (e.g., TLS-perivascular community) or spatial contiguity between regions (e.g., FAP+ CAF rim adjacent to CD8+ T cell-excluded zone) predict prognosis.

#### Clinical Translation Framework (Figure 5)

**Roadmap**: Clinical question → clinical endpoints → sampling framework → platform selection → spatial analysis aligned with clinical parameters → mechanistic validation → biomarker/trial development.

**Applications**:
- *Pre-cancer*: HTAN Pre-Cancer Atlas; "molecular clock" progression prediction frameworks positioning lesions along developmental trajectories
- *Metastasis*: Multi-site spatial analyses; TGFβ1+ myCAFs → basal-like cancer cell axis in PDAC; CLDN5-low endothelial niches in brain metastasis
- *MRD*: Second-look laparoscopy (SLL) paired with spatial omics in ovarian cancer; hypoxia programs, ABC transporters, immune exclusion as resistance mechanisms (NCT05739981)
- *Spatial biomarkers*: Composite patterns (cell-cell proximities, niche architectures) outperform single-marker measurements; breast cancer spatial architecture subgroupings predict survival beyond clinical subtypes
- *Target discovery*: Perturb-map/Perturb-FISH (spatial readout of pooled CRISPR screens; *Tgfbr2* loss drives immune exclusion in lung adenocarcinoma); BaSISS (base-specific in situ sequencing; HER2-amplified clones in hypoxic regions in breast cancer)

---

### Evaluation

This is a review paper — no original computational benchmarking. The authors:
- Survey the full landscape of spatial omics platforms with qualitative and quantitative capability comparisons (gene/protein coverage, spatial resolution, tissue compatibility)
- Review biological validation studies across multiple cancer types (RCC, GBM, HCC, PDAC, breast cancer, gastric cancer, ovarian cancer, nasopharyngeal cancer, lung adenocarcinoma)
- Provide a clinical case study: CODEX-based TME profiling of PPP2R1A loss-of-function ovarian cancer revealed B cell-enriched TME → spawned a phase I/II trial (dostarlimab + LB-100; NCT06065462)
- Emphasize composite spatial biomarkers over single-marker metrics throughout

---

### Reproducibility

**Rating: 2/5** — Review paper; individual findings from cited works are reproducing at their own reproducibility levels.

**Justification**: No original computational results are presented. The review synthesizes ~241 published studies. Individual reproducibility varies widely:
- Commercial platforms (Xenium, Visium HD, CosMx): high reproducibility, standardized reagents/protocols
- Computational tools (CellChat, COMMOT, NicheCompass): available as open-source packages with tutorials
- Biological claims: derived from diverse experimental systems; some findings require large cohort validation (noted by authors)

**Practical Notes**:
- No code repository or data repository associated with this review
- Individual tools mentioned are available via their own GitHub repositories
- BioRender-generated figures
- Funded by NCI (U01CA294518, U01CA264583, R01CA266280) and Break Through Cancer

**Strengths**:
- Extremely comprehensive: covers 200+ tools, 5 modalities, 9 TME niches, and clinical translation in a single paper
- Hierarchical framework (cell → niche → community → ecosystem) provides conceptual clarity
- Practical clinical roadmap with specimen scale, preservation, and study design guidance
- Authors include first-hand experience with CODEX on PPP2R1A ovarian cancer → spawned a trial

**Weaknesses**:
- No quantitative comparison of platforms (e.g., no sensitivity/specificity benchmarks)
- Coverage of metabolomics and spatial multi-omics is less detailed than transcriptomics
- Foundation model section covers rapidly evolving literature; some models (KRONOS) are arXiv preprints
- 3D spatial technologies section acknowledges lack of standardized file formats and computational pipelines
- Some biological claims (microbiota, neuroimmune niches) involve fewer studies and smaller cohorts

---

### Key Figures

| Figure | Core Content |
|---|---|
| Figure 1 | Taxonomy of spatial omics platforms (transcriptomics, proteomics, metabolomics, multi-omics, 3D) |
| Figure 2 | Computational analytics pipeline from segmentation to foundation models |
| Figure 3 | Nine TME niche types with cellular composition and spatial context |
| Figure 4 | Multi-scale organizational framework: cells → niches → communities → ecosystems |
| Figure 5 | Clinical/translational roadmap and applications |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
