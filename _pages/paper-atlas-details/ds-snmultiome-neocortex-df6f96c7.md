---
layout: default
permalink: /paper-atlas/ds-snmultiome-neocortex-df6f96c7/
title: "DS-snMultiome-Neocortex"
nav: false
description: "唐氏综合征由 21 号染色体三体（Ts21）引起，但额外基因剂量如何在胎儿期改变神经发生、投射神经元命运和调控网络并不清楚。动物或成年脑数据难以重建人类妊娠中期的起始过程，因此作者对 GW13–23 的 26 名供体（13 Ctrl、13 Ts21）做 10x snMultiome，在同一细胞核中同时测 RNA 与 ATAC，保留 113,801 个高质量 nuclei。"
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
      <span>Science · 2026</span>
    </div>
    <h1>DS-snMultiome-Neocortex</h1>
    <p>A single-cell multiomic analysis identifies molecular and gene-regulatory mechanisms dysregulated in developing Down syndrome neocortex</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1126/science.aea1259" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 唐氏综合征发育期新皮层单核多组学图谱解读

### 研究问题与设计

唐氏综合征由 21 号染色体三体（Ts21）引起，但额外基因剂量如何在胎儿期改变神经发生、投射神经元命运和调控网络并不清楚。动物或成年脑数据难以重建人类妊娠中期的起始过程，因此作者对 GW13–23 的 26 名供体（13 Ctrl、13 Ts21）做 10x snMultiome，在同一细胞核中同时测 RNA 与 ATAC，保留 113,801 个高质量 nuclei。

```text
多供体新皮层 → CellRanger ARC RNA+ATAC
  → SNP demultiplex + ambient RNA 去除 + QC
  → RNA(SCTransform/RPCA) + ATAC(LSI) + WNN 聚类
  → 细胞组成、Monocle3 轨迹、NEBULA DEG、hdWGCNA 模块
  → CellChat/NeuronChat 细胞互作
  → SCENIC+：TF → accessible region → target gene eRegulon
  → NDD rare variants 与 S-LDSC GWAS 收敛分析
```

配套验证包括 SOX2/NEUROD2/BCL11B/SATB2 免疫染色、Ctrl/Ts21 原代人神经祖细胞 4 周分化 snMultiome，以及 isogenic hiPSC 模型和 Seahorse 代谢检测。

### 核心分析逻辑

RNA 用 SCTransform 和 reciprocal PCA 做多供体整合；ATAC 以 MACS2 consensus peaks、TF-IDF/LSI 表示；WNN 联合两个模态得到细胞类型。差异表达采用 NEBULA 的 negative-binomial gamma mixed model，以 donor 随机效应避免把细胞数误当生物重复。细胞组成和染色比例用 binomial generalized mixed model，轨迹与模块/eRegulon 活性用 linear mixed model。

Monocle3 将 excitatory neuron lineage 划为 radial glia、IPC/newborn、immature、maturing 四个 pseudotime bins，并在 CT 与 IT 分支点比较命运比例。轨迹是转录状态排序而非真实谱系追踪；作者用 IHC、参考数据的年龄迁移和体外分化作正交支持。

SCENIC+ 联合 TF motif、ATAC peak 与 RNA 共变构建 enhancer-driven regulons。它把“某 TF 在 Ts21 上调”推进到“其 motif 所在开放区可能连接哪些 target genes”，但仍是计算调控网络，不能替代 TF perturbation。项目未公开分析代码和自定义 cisTarget database，因此本工作区为 paper-only，所有实现对应均为 `Not found`。

### 主要发现

#### 神经发生提前并改变 IT/CT 命运

Ts21 中 SOX2+ progenitors 减少，NEUROD2+ neurons 增加；细胞从 progenitor/newborn 阶段更快进入 immature IT commitment。分支比例显著偏向上层 intratelencephalic neurons（61%），deep-layer corticothalamic neurons 降至 39%。IHC 同时显示 BCL11B+ 深层神经元减少、SATB2+ 上层神经元及 SATB2/BCL11B 双阳性混合身份增加。图 2–3 将组成、组织染色和 pseudotime 三条证据连接起来。

#### 全基因组而非仅 HSA21 的表达失调

HSA21 genes 近似按 3:2 剂量上调，但只构成全部 DEGs 的小部分；共检测 3,464 个 cell-type-specific DEGs。祖细胞维持、自噬和染色质重塑程序下降，OxPhos、神经发生及部分突触程序升高。hdWGCNA 显示 CT identity 模块（TLE4、ZFPM2）下降，而 pro-IT 模块（RORA、LRRC4C、FOXP1）在 CT/IT 中异常增强。

#### BACH1 是候选上游驱动因子

SCENIC+ 得到 358 个 eRegulons，其中 HSA21-encoded TF BACH1 的 activator regulon 在 newborn excitatory neurons 上升，候选 targets 包括 pro-IT TF `CUX2` 与 `BHLHE22`。BACH1 在 pseudotime 中早于 CUX2 达峰，并在 phNPC 数据中复现，因此支持“额外 BACH1 剂量推动 IT 命运”的模型；直接因果仍需 BACH1 剂量校正或扰动实验。

#### 神经血管与小胶质生态位提前改变

CellChat/NeuronChat 提示 VEGFA–VEGFR、collagen、fibronectin 和 laminin-α4 等 radial glia–vasculature signals 增强，CD31+ vessel density 在 VZ 增加。microglia 的 SPP1 phagocytic signal 增强、IGF1 anti-inflammatory signal 减弱，IBA1+/SPP1+ 比例上升，构成 DS prenatal microglial activation 的早期证据。配体受体分析基于表达推断，不能单独证明物理信号传递。

#### 与其他神经发育障碍的收敛

deep-layer EN 的 DEGs 和 12/14 个差异 CT/IT eRegulons 富集 ASD、NDD、developmental delay rare variants，涉及 KMT2C、POGZ、KAT6A、EZH2、GATAD2B 等 chromatin regulators。S-LDSC 还显示 Ts21-altered accessible peaks/eRegulon CREs 富集 intelligence、educational attainment、ASD、ADHD 的遗传力，提示不同疾病在深层投射神经元 specification 上共享脆弱性；富集不是个体风险预测。

### 图像证据与局限

七张主图已直接检查：图 1 建立 paired RNA/ATAC atlas；图 2–3 展示 progenitor 减少、IT/CT 错配和 heterochrony；图 4 汇总 DEG/模块；图 5 展示 neurovascular/microglial niche；图 6 定位 SCENIC+ 与 BACH1；图 7 连接 NDD/GWAS。

复现边界很明确：NeMO 数据为 controlled access；论文没有公开分析仓库、精确脚本、custom cisTarget database、IHC masks 或完整代谢原始数据。工具版本和统计模型描述较清楚，足以理解设计，但不足以逐图复现。该论文说明 Ts21 与加速神经发生相关，并提出 BACH1 等候选机制；它不证明单一 HSA21 gene 足以解释全部表型。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## DS-snMultiome-Neocortex — Summary

### Motivation & Novelty

Down syndrome (DS), caused by trisomy of chromosome 21 (Ts21), is the most common genetic cause of intellectual disability (~1/700 live births). Despite decades of research, the molecular and cellular mechanisms linking HSA21 gene dosage to neurodevelopmental abnormalities in the human brain remained largely unknown, particularly during the critical mid-gestation window when cortical structural changes first appear (Pinter et al. 2001, *Am J Psychiatry*; Tarui et al. 2020, *Cerebral Cortex*).

**Why existing approaches fell short:**
- **Animal models** (Ts65Dn mouse, etc.): conflicting results due to species-specific developmental differences and incomplete construct validity (Shaw et al. 2020, *Dis Model Mech*; Herault et al. 2017, *Dis Model Mech*)
- **Postmortem adult brain transcriptomics** (Palmer et al. 2021, *PNAS*; Olmos-Serrano et al. 2016, *Neuron*; Rastogi et al. 2024, *Neuron*): misses the developmental origin of abnormalities and cannot capture cell-type-specific regulatory dynamics
- **Prior developmental studies**: bulk or single-modality; lacked paired chromatin accessibility for GRN inference

**Unique contributions:**
1. First paired snRNA-seq + snATAC-seq (snMultiome) atlas of **developing human Ts21 neocortex** at mid-gestation (GW13–23)
2. Systematic GRN analysis identifying **HSA21-encoded TF BACH1** as a direct upstream activator of pro-IT specification
3. Identification of **prenatal microglial activation** — earliest evidence of neuroinflammation in DS
4. Linkage of Ts21-altered chromatin to **GWAS heritability** of intelligence, educational attainment, ASD, and ADHD
5. Convergence of DS molecular programs with rare-variant signals from multiple NDDs, pointing to **deep layer neurons as a shared vulnerability**

---

### Method Overview

**Experimental design:**
- 26 donors: 13 Ctrl + 13 Ts21, gestational weeks 13–23
- Tissue: fresh-frozen human mid-gestation neocortex
- Assay: 10X Genomics snMultiome (paired RNA + ATAC per nucleus)
- Pooled multiplexing: 3–4 donors per flowcell; SNP-based demultiplexing (cellsnp-lite + vireoSNP)
- 113,801 high-quality nuclei retained after QC

**Computational pipeline (see doc_method.md for details):**

| Stage | Tool | Output |
|---|---|---|
| Read alignment | CellRanger ARC v2.02 | RNA + ATAC count matrices |
| Ambient RNA removal | CellBender v0.3.0 | Cleaned RNA matrix |
| Normalization + integration | sctransform + RPCA (Seurat v4.4.0) | Batch-corrected embedding |
| Peak calling | MACS2 v2.2.9.1 | Consensus ATAC peaks |
| Joint clustering | WNN (Seurat) + Signac v1.12.0 | 27 cell types |
| Differential expression | NEBULA v1.5.5 | 3464 cell-specific DEGs |
| Composition | sccomp | Cluster-level proportions |
| Coexpression networks | hdWGCNA v0.3.03 | 32 modules |
| Pseudotime | Monocle3 | EN lineage trajectory |
| Cell communication | CellChat v2.1.2 + NeuronChat v1.0.0 | 67 LR pathways |
| GRN inference | SCENIC+ v1.0a1 | 358 eRegulons |
| Heritability | S-LDSC | 7 GWAS trait enrichments |

**Orthogonal validation:**
- IHC (SOX2, NEUROD2, BCL11B, SATB2, CD31, IBA1/SPP1) in 8 age-matched donors; CellPose automated segmentation
- phNPC snMultiome (4 Ctrl + 3 Ts21 lines, 4-week differentiation, 45,282 nuclei)
- hiPSC isogenic di/trisomic pair + Seahorse metabolic flux assays

---

### Evaluation

#### Key Results

**1. Accelerated neurogenic timeline (heterochrony)**
- Progenitor pool (vRG-oRG-PgS) significantly reduced in Ts21
- IT/CT ratio shifted: 61% upper layer vs 39% deep layer (P = 5.9×10⁻¹⁶⁰, binomial GLMM)
- Ts21 cells advance faster through progenitor-to-newborn neuron transition (accumulate in Bin 3, IT commitment stage)
- Predicted developmental age exceeds annotated gestational age in Ts21 (P = 0.03, linear model; driven by EN-L5-L6, EN-L6-CT, EN-ITs)
- Confirmed by IHC: SOX2+ progenitors ↓ (FDR P=0.031); NEUROD2+ neurons ↑ (FDR P=2.86×10⁻⁶)

**2. IT/CT neuron misspecification**
- BCL11B+ (deep layer CT marker) neurons reduced (FDR P=2.41×10⁻⁵); SATB2+ (upper layer IT marker) increased (FDR P=0.022)
- BCL11B+/SATB2+ double-positive cells increased at early time points (GW13–16), indicating mixed identity
- IT TFs (SATB2, CUX2, RORB) misexpressed in CT neurons; CT TFs (BCL11B, TLE4, ZFPM2) misexpressed in IT neurons

**3. Molecular programs: OxPhos, neurogenesis, specification**
- 3464 cell-type-specific DEGs; 18/32 (56%) hdWGCNA modules differentially active
- RGs: ubiquitin pathway (TTC3↑), OxPhos (NDUFV3↑), Arp2/3 complex (NCKIPSD, WASF3↑)
- IPCs: fatty acid OxPhos, axonogenesis (TIAM1↑, HSA21-encoded)
- ENs: synaptogenesis (APP, PDE9A, SYNJ1↑, HSA21-encoded)
- Group 3 modules: CT identity programs ↓ (ZFPM2, TLE4); IT identity module ↑ in CT neurons (RORA, LRRC4C, FOXP1)
- OxPhos ATP production confirmed by Seahorse assays in phNPCs, NPCs, and neurons (P < 0.05)

**4. Proangiogenic/proinflammatory niche**
- 50/67 (82%) CellChat pathways differentially active; vascular + microglia enriched in 32%
- RG-vascular: VEGFA-VEGFR, collagen, fibronectin, laminin-α4 signaling ↑; laminin-α2 (apical RG attachment) ↓
- CD31+ vessel density increased in VZ (FDR P=0.035)
- Microglia: SPP1 phagocytic signaling ↑, IGF1 anti-inflammatory ↓; IBA1+/SPP1+ proportion increased (P=0.011)

**5. BACH1 as HSA21-encoded activator of pro-IT fate**
- SCENIC+ identifies BACH1 eRegulon significantly up-regulated in EN-Newborn-2 (FDR P=1.96×10⁻⁴)
- BACH1 target genes include CUX2 (pro-IT TF) and BHLHE22
- BACH1 peak expression in pseudotime precedes CUX2, consistent with upstream regulatory function
- Validated in phNPC GRNs: BACH1 activates CUX2, increased activity in EN-Upper-IT

**6. NDD convergence**
- EN-L6-CT-2 and EN-L6-IT DEGs enriched in ASD, NDD, DD, syndromic ASD (Fisher's FDR < 0.05)
- Key shared genes: KMT2C, POGZ, KAT6A, EZH2 (chromatin remodelers); GATAD2B (NuRD complex, regulates SATB2/BCL11B)
- 86% (12/14) of differential CT/IT eRegulons enriched in at least one NDD
- S-LDSC: Intelligence, educational attainment, ASD, ADHD heritability enriched in Ts21 DA peaks/eRegulon CREs; AD not enriched (expected)

#### Datasets Used
- **In vivo**: 26 human mid-gestation neocortex samples, GW13–23, UCLA Gene and Cell Therapy Core + NIH NeuroBioBank; 113,801 nuclei
- **In vitro**: Primary human NPC lines (phNPCs) from Ctrl and Ts21 donors; hiPSC isogenic di/trisomic pair (Russell lab)
- **Reference atlas**: Polioudakis et al. 2019 *Neuron*; Wang et al. 2025 *Nature* (for cell type annotation and age estimation)
- **GWAS**: ASD (Matoba et al. 2020), ADHD (Demontis et al. 2023), Intelligence (Savage et al. 2018), Epilepsy (ILAE 2023), EA (Okbay et al. 2022), AD (Bellenguez et al. 2022), Cortical structure (Grasby et al. 2020)

---

### Reproducibility

**Rating: 2 / 5**

**Justification:**
- Raw data under **controlled access** at NeMO Archive (approval required from NIMH Data Archive) — a significant barrier for most researchers
- **No analysis code repository published** — all analyses use established packages, but exact scripts/workflows are unavailable; reproducing from the Methods description would require substantial engineering effort
- SCENIC+ v1.0a1 is an **alpha release** with potential API instability in later versions
- **Custom cistarget database** was generated for this study; not provided as a downloadable resource
- Monocle3 version not specified in Methods
- Analytical pipeline is well-documented (tool versions provided for most packages) but would require significant computational infrastructure (GPU for some tools, high-memory server for SCENIC+)
- IHC raw images and segmentation masks not provided
- Metabolic flux raw data not deposited

**Practical notes:**
- To partially reproduce: request access to NeMO Archive, then run standard Seurat/Signac QC, clustering, and NEBULA DGE
- Full GRN analysis requires building a custom cistarget database — computationally expensive (Cluster-buster on all peaks × motif library)
- The phNPC and hiPSC lines are from specific labs (de la Torre-Ubieta, Lowry, Russell) — obtaining these requires direct collaboration

**Strengths:**
- Clear versions for most tools
- All statistical models explicitly described with model formula components
- Multiple independent validation tiers (IHC + phNPC + hiPSC + Seahorse)
- Companion paper (Risgaard et al. 2026 *Science*) provides postnatal extension

**Weaknesses:**
- Controlled-access data limits broad reproducibility
- No code availability
- Key resource (custom cistarget DB) not shared
- Supplementary materials (tables S1–S16) not accessible in the version reviewed

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
