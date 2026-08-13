---
layout: default
permalink: /paper-atlas/lymphnodesenescenceatlas-2074f00e/
title: "LymphNodeSenescenceAtlas"
nav: false
description: "免疫衰老常从外周血研究，但淋巴结是 B 细胞进行生发中心反应、亲和力成熟和抗体产生的核心组织。只看血液或解离后的单细胞数据，会丢失“衰老细胞位于组织何处、与哪类细胞邻近、是否形成局部生态位”这些信息。本研究因此不是提出单一算法，而是构建一个跨年龄、跨模态的人淋巴结细胞衰老 atlas，重点回答三件事：哪些细胞进入衰老样状态；它们如何随年龄改变空间位置；这些位置变化对应怎样的转录、蛋白、染色质和代谢重编程。"
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
      <span>Data Sources &amp; Technologies</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>LymphNodeSenescenceAtlas</h1>
    <p>Human Lymph Node Cellular Senescence Atlas Reveals Age-Dependent Alteration in Germinal Center B Cell Function and Niches</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.04.02.716161" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for LymphNodeSenescenceAtlas">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/MingyuYang-Yale/DBiT-seq" target="_blank" rel="noopener noreferrer" aria-label="Open code for LymphNodeSenescenceAtlas">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 人淋巴结细胞衰老空间图谱：方法与证据解读

### 1. 这篇论文在解决什么问题

免疫衰老常从外周血研究，但淋巴结是 B 细胞进行生发中心反应、亲和力成熟和抗体产生的核心组织。只看血液或解离后的单细胞数据，会丢失“衰老细胞位于组织何处、与哪类细胞邻近、是否形成局部生态位”这些信息。本研究因此不是提出单一算法，而是构建一个跨年龄、跨模态的人淋巴结细胞衰老 atlas，重点回答三件事：哪些细胞进入衰老样状态；它们如何随年龄改变空间位置；这些位置变化对应怎样的转录、蛋白、染色质和代谢重编程。

研究收集 65 名供体、108 份样本，按 `<50`、`50–69`、`≥70` 岁分组。最终整合的空间数据覆盖 56 名个体、超过 2,000 万个细胞，包括 18 个完整淋巴结和 81 个 CODEX tissue cores、11 个 DBiT 空间转录组样本、9 个 spatial ATAC-seq 样本，并对少数重点样本增加 CosMx、单细胞蛋白质组和 SRS 代谢成像。

### 2. 六种模态各自回答什么

```text
人淋巴结 FF / FFPE 连续切片
  ├─ CODEX 53-plex 蛋白成像 → 细胞类型、p16/p21/HMGB1/γ-H2AX、空间 SenSpots
  ├─ DBiT-seq 空间 RNA → 20 μm 网格表达、衰老通路和 B 细胞功能
  ├─ spatial ATAC-seq → 衰老基因位点可及性、TF motif
  ├─ CosMx 6000-gene → 单细胞 SenMayo 分数及与 CODEX 共注册
  ├─ nanoPOTS LC-MS/MS → 单个 p16+ 与 p16- 滤泡细胞蛋白差异
  └─ SRS + TPF → 脂质/蛋白比及 FAD/NADPH 氧化还原状态
                  ↓
          统一解释年龄相关的细胞状态与空间生态位
```

CODEX 提供全队列的大规模空间定位；DBiT-seq 和 CosMx补充 RNA 机制；ATAC-seq寻找调控层变化；nanoPOTS 与 SRS 分别验证蛋白和代谢后果。它们来自连续而非同一张切片，因此跨模态共注册能保留大体组织结构，但不是逐细胞的完全同位测量。

### 3. 参照图谱与细胞注释

作者整合 Tabula Sapiens 和 Secondary Lymphoid Organ Atlas 构建单细胞 RNA 参照，经 Harmony 校正后得到 95,389 个细胞、34 种免疫和基质细胞类型；另分析约 51 万个 PBMC 作为外周衰老参照。CODEX 的蛋白空间数据通过 MaxFuse 与 scRNA-seq 对齐：先从共享特征建立跨模态 pivots，再把细胞类型标签传播到蛋白成像细胞。论文报告超过 98% 的 CODEX 细胞获得注释。

这个步骤的意义是把高覆盖但标记数有限的 53-plex 蛋白图像，连接到更丰富的转录细胞类型体系。边界是：MaxFuse 和后续非 pivot 细胞分类的项目脚本没有出现在本地两个公开仓库中，因此只能从论文方法验证设计，不能从代码复现具体标签。

### 4. 如何定义“衰老样细胞”

#### 4.1 CODEX 蛋白 senotype

CODEX 使用 p16、p21、HMGB1 和 $\gamma$-H2AX 四个标记。每个样本内对每个标记取强度最高的 10% 作为阳性，再组合成不同 senotype。样本内阈值能缓解不同切片染色强度的批次差异，但“top 10%”是相对定义：即使样本整体衰老负担很低，仍会有固定比例被标阳，因此结论应结合多标记共阳性和年龄趋势，而不是把单一阳性等同于不可逆细胞衰老。

#### 4.2 RNA 的 SenMayo 分数

CosMx 的表达较稀疏，论文先按基因在所有细胞中的最大值归一化：

$$
\widetilde{T_i(j)}=\frac{T_i(j)}{\max_k T_i(k)},
$$

再对 SenMayo 基因集 $G$ 求和：

$$
S(j;G)=\sum_{i=1}^{|G|}\widetilde{T_i(j)},
$$

最后在数据内标准化：

$$
z(S)=\frac{S-\mu(S)}{\sigma(S)}.
$$

最大值归一化使每个基因对总分的贡献有相近上限，避免少数高表达基因完全支配分数。单细胞参照分析还用 SenMayo、SASP、DNA damage 和 cell-cycle arrest module scores；不同图中使用 top 10% 或 top 20% 阈值，阅读时不能把这些百分位混为同一绝对标准。

### 5. 如何量化衰老细胞向滤泡中心聚集

作者依据 CD20/CD21 高表达细胞拟合滤泡的二维高斯椭圆，以中心 $\mu$ 和协方差 $\Sigma$ 描述其位置和形状。滤泡内部使用 Mahalanobis 距离：

$$
d_M(x)=\sqrt{(x-\mu)^T\Sigma^{-1}(x-\mu)},
$$

它会按椭圆长短轴缩放，使不同形状滤泡的“相对半径”可以比较。滤泡外部改用到边界的 Euclidean distance，并把内外空间离散为同心 annuli，统计不同 senotype 的径向分布。

由此得到论文的核心空间发现：年轻供体的衰老样细胞较分散、偏滤泡外；50–69 岁逐渐进入 mantle zone；70 岁以上 p16+/p21+ B 细胞在生发中心形成局灶的 **SenSpots**。这是年龄相关的空间重排，而不只是总阳性细胞比例上升。该几何分析的项目代码在两个公开仓库中 `Not found`。

### 6. 多组学如何连接到生物机制

#### 6.1 空间转录组与 CosMx

DBiT-seq 将两轮正交微流控 barcode 组合成 50×50 空间网格；表达矩阵经 SCTransform、PCA、邻居图和聚类，再通过 Harmony/KNN 与单细胞参照连接。重点样本还用 iStar 融合 H&E 与低分辨率表达得到超分辨率图，并用 MaxFuse/STalign 与 CODEX 配准。

结果显示老年样本激活更多衰老相关通路；在衰老 GC B 细胞中，FOS/AP-1、NF-$\kappa$B 等应激炎症程序增强，而免疫球蛋白转录下降，提示形成 SenSpots 的 B 细胞可能伴随抗体产生功能衰减。该关联支持“GC niche 功能受损”，但论文没有直接测量抗体亲和力或疫苗反应。

#### 6.2 单细胞蛋白质组和代谢成像

对一名 78 岁供体，作者用激光显微切割获取 p16+ 与 p16- 滤泡细胞，再以 nanoPOTS/FAIMS LC-MS/MS 分析；每细胞中位数约识别 740 个蛋白，150 个蛋白显著差异。DKC1 是 p16+ 细胞中最强下降者之一（约 $\log_2FC=-3.2$），把衰老热点与端粒酶复合体/端粒维护受损联系起来。

同一重点组织的 SRS/TPF 显示 p16+ 或 p21+ GC B 细胞脂质/蛋白比升高，部分衰老标记阳性细胞的 optical redox ratio 降低，提示脂质积累和更氧化的代谢状态。由于 nanoPOTS、SRS 和 CosMx 深度分析各主要来自单一供体，这些机制线索需要更大队列和功能扰动验证。

#### 6.3 空间表观基因组

9 个 spatial ATAC-seq 样本用于基因活性、peak 和 motif 分析。70 岁以上样本在 CDKN2A/CDKN2B、CDKN1A 和 H2AFX 等位点出现更高、更宽的可及性；KLF1/3/5/6、NFY、SP1/SP2、HOXA9 等 motifs 偏向老年样本，而 MEF2A、EAR2/NR2F2 等偏向年轻样本。这与 RNA 层的炎症、DNA damage 和 cell-cycle arrest 程序相互支持，但 motif 富集只表示潜在调控因子结合偏好，不证明这些 TF 实际驱动了衰老。

### 7. 主要证据链

1. **全队列 CODEX**：p16/p21 及多标记共阳性细胞随年龄增加，并从滤泡外向 GC 内集中。
2. **空间几何模型**：用椭圆归一化距离证明位置变化不是简单由滤泡形状造成。
3. **DBiT/CosMx RNA**：SenMayo 和炎症程序增强，GC B 细胞免疫球蛋白程序下降。
4. **nanoPOTS/SRS**：DKC1/端粒维护、脂质积累和氧化还原改变提供蛋白与代谢层支持。
5. **spatial ATAC**：衰老位点开放和 KLF/AP-1/NF-$\kappa$B 相关调控景观支持年龄相关重编程。

这些证据共同指向 GC B-cell niche 是晚年淋巴结衰老的重要储库，但“SenSpot 为克隆性扩增”“DKC1 缺失导致衰老”仍是需要谱系或扰动实验检验的机制假设。

### 8. 公开代码能复现到什么程度

`spatial_epigenome_FFPE/` 提供通用 ATAC/Signac/ArchR 处理和 iStar 脚本。它们能验证部分技术底层流程，但整体 paper-code fidelity 为 **low**：

- `Exact/Partial`：DBiT barcode 设计、部分预处理/图像对齐、通用 spatial ATAC 流程、iStar 准备—运行—可视化链条；
- `Not found`：本图谱的 CODEX/MaxFuse 标注、SenMayo 评分、滤泡 Mahalanobis 分析、nanoPOTS/SRS 处理和完整年龄组统计脚本；
- 两个仓库主要来自既往 DBiT-seq 和 FFPE lymphoma 项目，不是本论文的一键复现包。

因此该工作区适合学习实验设计、核对通用预处理代码和追踪论文证据，但不能据此声称完整复现所有主图。数据虽已指向 SenNet Portal，实际复现还需要受控数据访问、缺失的项目脚本、商业成像平台和精确样本配准信息。

### 9. 结论与边界

这项工作的真正贡献是把“细胞衰老是否增加”推进到“衰老样状态在淋巴结的哪个结构中积累、由哪些 B 细胞承担、伴随哪些跨层分子变化”。SenSpots 和向生发中心的迁移为老年体液免疫减弱提供了空间解释框架。与此同时，研究是 bioRxiv 预印本，部分深度模态为单供体，41–59 岁的 LN 单细胞参照不足，跨切片配准和固定百分位阈值也会引入不确定性；论文自己也要求用选择性诱导/清除 B、T 细胞衰老的功能实验验证因果关系。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Human Lymph Node Cellular Senescence Atlas

**Paper**: Human Lymph Node Cellular Senescence Atlas Reveals Age-Dependent Alteration in Germinal Center B Cell Function and Niches
**DOI**: 10.64898/2026.04.02.716161
**Journal**: bioRxiv (preprint, April 6, 2026)
**Type**: Atlas / Data resource paper
**Key PIs**: Rong Fan, Yuval Kluger, Mina L. Xu (Yale University)
**Data**: SenNet Data Portal (data.sennetconsortium.org), TMC-Yale

---

### Motivation & Novelty

**Biological problem**: Human immune function declines progressively with age (*immunosenescence*), causing reduced vaccine efficacy, increased infection susceptibility, and chronic "inflammaging." The germinal center (GC) — where B cells undergo affinity maturation to produce high-quality antibodies — is a central site of adaptive immunity. Yet the identities, spatial organization, and molecular mechanisms of senescent-like cells in human lymph nodes across the lifespan were almost entirely unknown.

**Why existing approaches fell short**:
- PBMC studies (circulating immune cells) miss tissue-resident dynamics and spatial context
- Prior spatial proteomics studies (e.g., mapping exhausted T cells in tumors) had not been applied to normal aging LN at this scale
- scRNA-seq atlases like Tabula Sapiens (Science, 2022) and the SLO Atlas (Nature Methods, 2023) lacked age-stratified donors spanning the full lifespan, particularly >70 years
- Single-modality spatial approaches cannot distinguish senescence mechanisms from surface protein markers alone

**Unique contributions**:
1. **First comprehensive spatial atlas of cellular senescence in human lymph nodes** spanning ages 18-100 years (65 donors, 20+ million cells)
2. **Discovery of age-dependent "SenSpots"**: Focal clonal-like accumulation of p16+/p21+ GC B cells in follicles of >70 yo donors — a previously undescribed spatial remodeling pattern
3. **Centripetal shift**: Young donors show diffuse extrafollicular senescence; older donors show GC-concentrated senescent cells — direct evidence for follicular niche remodeling
4. **DKC1 depletion in p16+ follicular cells**: The telomerase co-factor Dyskeratosis Congenita 1 (DKC1) is one of the most strongly depleted proteins (log₂FC ≈ -3.2), suggesting compromised telomere maintenance as a driver of B cell senescence
5. **Multi-modal validation**: Same senescence signatures confirmed at protein (CODEX), transcript (DBiT-seq, CosMx), chromatin (ATAC-seq), and metabolic (SRS) levels across six independent platforms
6. **AP-1 and KLF transcription factor programs** enriched at senescence loci in older donor chromatin — implicating inflammation-senescence coupling as a targetable regulatory axis

---

### Method Overview

The atlas integrates six spatial and single-cell modalities:

| Modality | Technology | Samples | Scale | Key Output |
|---|---|---|---|---|
| High-plex protein imaging | CODEX (PhenoCycler-Fusion) 53-plex | 18 whole LNs + 81 TMA cores | ~20M cells | Cell type + senotype map |
| Spatial transcriptomics | DBiT-seq (20 μm barcodes) | 11 LN samples | 2500 pixels/sample | Gene expression landscape |
| Spatial epigenomics | Spatial ATAC-seq (DBiT device) | 9 FF LN samples | Per-spot chromatin | Accessibility at CDKN loci |
| Single-molecule ST | CosMx (6000 genes) | 1 sample (86 yo) | Single-cell | SenMayo spatial map |
| Single-cell proteomics | nanoPOTS LC-MS/MS (LCM) | 1 sample (78 yo) | ~740 proteins/cell | p16+ cell protein profile |
| Metabolic imaging | SRS + TPF | 1 sample (78 yo) | ~100 nm resolution | Lipid/redox metabolic state |

**scRNA-seq reference**: 95,389 cells from Tabula Sapiens + SLO Atlas integrated via Harmony → 34 annotated cell types; 510,000 PBMCs from 25 donors for peripheral aging reference.

**Cell type annotation**: MaxFuse cross-modal integration of scRNA-seq labels to CODEX protein profiles (>98% CODEX cells annotated).

**Senescence scoring**: Four canonical protein markers (p16, p21, HMGB1, γ-H2AX) in CODEX; SenMayo gene set scored in scRNA-seq and CosMx using max-normalized OES + z-score; top-10% per-sample threshold for CODEX positivity.

**Follicle geometry**: Gaussian ellipse model (centroid µ, covariance Σ) from CD20+/CD21+ cells; Mahalanobis distance (inside follicle) and Euclidean distance (outside) to quantify senescence radial distribution.

---

### Evaluation

#### Cohort
- 65 donors (41M/24F, ages 1-86 years), 108 samples total
- Group 1: <50 yo (n=26, median 32y), Group 2: 50-69 yo (n=15, median 56y), Group 3: ≥70 yo (n=10, median 75y)
- Yale Pathology Tissue Services, IRB-approved, histologically confirmed non-malignant

#### Key Quantitative Results

**scRNA-seq aging signatures (PBMCs)**:
- SenMayo score significantly higher in Group 3 vs Groups 1+2 (p=0.04)
- SASP score: p=0.001; Cell Cycle Arrest score: p=0.0016
- CDKN1A (p21) elevated in Group 3 vs younger (p=0.0058); CDKN2A (p16): p=0.000521

**CODEX spatial senescence**:
- p16+ and p21+ cells increase with age, pronounced rise in >70 yo donors
- Quadruple-positive (p16+p21+γ-H2AX+HMGB1+) cells almost exclusively in >70 yo
- Centripetal shift: young → diffuse extrafollicular; 50-70 yo → mantle zone; >70 yo → GC core

**Spatial transcriptomics (age stratification)**:
- Older samples (>53 yo) have mean 3.33 active senescence pathways/sample vs 1.67 in younger (Mann-Whitney U=30.0, p=0.029)
- Most upregulated genes in >70 yo vs <50 yo: HLA-A, HLA-B, HLA-C, HLA-DRA, HLA-DMB, FCGR2A

**nanoPOTS proteomics**:
- 150 proteins significantly different between p16+ vs p16- follicular cells (ANOVA FDR<0.05)
- DKC1: log₂FC ≈ -3.2 (most depleted)
- Top pathway: "Telomere extension by telomerase" (most significantly altered)

**Metabolic imaging**:
- Lipid/protein ratio significantly elevated in p16+ and p21+ GC B cells
- Optical Redox Ratio (ORR) decreased in p16+ and γ-H2AX+ cells (oxidized senescent state)
- B_memory cells: ~75% of p16+ cells, ~60% of γ-H2AX+ cells

**Epigenomics**:
- CDKN2A, CDKN1A, H2AFX loci show higher and broader ATAC peaks in >70 yo samples
- KLF family motifs (KLF1, KLF3, KLF5, KLF6), SP1/SP2, HOXA9 enriched in >70 yo
- MEF2A, NR2F2 enriched in <50 yo (growth/anti-inflammatory programs)

#### Cell-Type–Specific Findings

- **GC B cells (DZ + LZ)**: Highest SenMayo enrichment; cycling-like B cells show elevated H2AFX and HMGB1; plasma B cells show increased CDKN1A and CDKN2A
- **T cells**: Largely resist classical senescence programs; develop stress-adapted pro-inflammatory phenotype instead
- **VSMCs**: Adopt stromal-inflammatory senescent profile
- **Memory B cells**: Primary reservoir of advanced senescence (~75% p16+ cells in >70 yo follicles)

---

### Reproducibility

**Rating: 2/5 — Data deposited but most analysis code not publicly available**

**Strengths**:
- Raw data deposited to SenNet Data Portal (data.sennetconsortium.org) with upload IDs provided
- Two GitHub repos available (DBiT-seq preprocessing infrastructure, spatial ATAC general pipeline)
- CODEX antibody panel with catalog numbers and dilutions fully specified (Table S2)
- DBiT-seq barcode sequences provided (Tables S3-S6)
- Standard tools used: STAR v2.7.8a, Seurat 4.2, ArchR, FragPipe v21.1
- Python/R versions specified for CosMx analysis

**Weaknesses**:
- **No code for core analyses**: CODEX preprocessing (MaxFuse integration, cell type annotation, senotype mapping), SenMayo spatial scoring scripts, follicle radial distribution analysis, nanoPOTS data processing, SRS image analysis — all absent
- **Public repos are from prior papers**: DBiT-seq repo = original 2021 DBiT-seq paper (Yang et al., Nature, 2020); spatial_epigenome_FFPE repo primarily contains lymphoma-specific analyses
- **Single-donor depth analyses**: nanoPOTS (78 yo), SRS (78 yo), CosMx (86 yo) — each from one donor; biological replication lacking
- **Age gap**: scRNA-seq LN reference lacks donors aged 41-59 years — middle-age senescence transitions undercharacterized
- **Preprint**: Not yet peer-reviewed; methods may change

**Practical notes**:
- Primary data access: SenNet Data Portal requires registration
- Yale HPC cluster (YCGA) used for CosMx; PALM MicroBeam LCM system for nanoPOTS
- CODEX imaging: AKOYA PhenoCycler-Fusion system (commercial, ~$500K instrument)
- Custom antibody conjugation with AKOYA DNA reporters required for in-house antibodies
- iStar, MaxFuse, STalign are published tools available from respective authors

---

### Chinese Interpretation

**核心发现**：本研究首次系统绘制了人类淋巴结中细胞衰老的空间多组学图谱，横跨18至100岁共65名供体。研究发现，随年龄增长，衰老细胞在组织中经历"向心性迁移"：年轻供体中衰老细胞广泛分布于滤泡外区域，50-70岁时集中于套区，70岁以上时高度集中于生发中心（GC），形成"衰老热点"（SenSpots）。

**关键机制**：衰老GC B细胞中端粒酶辅因子DKC1显著缺失（log₂FC≈-3.2），提示端粒维护受损是B细胞衰老的驱动力。表观基因组分析揭示AP-1（FOS/JUN）和KLF转录因子家族在衰老相关位点的染色质可及性显著增加，可能协调炎症与衰老的耦合。代谢成像显示衰老GC B细胞中脂质/蛋白质比升高、细胞处于更氧化状态。

**意义**：该图谱重新定义了淋巴结作为动态免疫老化器官的角色，揭示以GC B细胞为核心的滤泡区域是老年人体内衰老免疫细胞的主要储库，为理解疫苗效果下降和增龄相关体液免疫减退提供了空间机制。

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
