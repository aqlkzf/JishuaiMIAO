---
layout: default
permalink: /paper-atlas/masld-macrophageatlas-46e73b82/
title: "MASLD_MacrophageAtlas"
nav: false
description: "这项研究先用单核 RNA 测序比较 lean、obese、MASL 和 MASH 肝脏中的巨噬细胞组成，再用四种空间技术确认新发现的 GPNMB 高表达代谢型巨噬细胞（MetMac）位于何处、表达哪些蛋白，随后用肝组织切片和细胞实验检验 hepatocyte-derived IL32 是否能改变其吞噬与炎症状态，最后把 MetMac 标志物带到 206 例 bulk RNA、247 例血清蛋白组和 53,030 人 PheWAS 中评估…"
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
      <span>Nature Genetics · 2026</span>
    </div>
    <h1>MASLD_MacrophageAtlas</h1>
    <p>Integrated multi-omics identifies distinct macrophage alterations during progression of metabolic dysfunction-associated steatohepatitis</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41588-026-02600-3" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MASLD Macrophage Atlas 方法解读：从肝巨噬细胞图谱到 MetMac–IL32 轴

### 一句话理解

这项研究先用单核 RNA 测序比较 lean、obese、MASL 和 MASH 肝脏中的巨噬细胞组成，再用四种空间技术确认新发现的 GPNMB 高表达代谢型巨噬细胞（MetMac）位于何处、表达哪些蛋白，随后用肝组织切片和细胞实验检验 hepatocyte-derived IL32 是否能改变其吞噬与炎症状态，最后把 MetMac 标志物带到 206 例 bulk RNA、247 例血清蛋白组和 53,030 人 PheWAS 中评估临床相关性。

### 1. 研究问题：MASH 中增加的到底是哪类巨噬细胞

MASLD 从单纯脂肪变性的 MASL 进展到伴随炎症和肝细胞气球样变的 MASH。经典框架认为，驻留 Kupffer cell（KC）受损后，循环单核细胞进入肝脏并形成 monocyte-derived macrophage。小鼠研究进一步提出以 `Trem2` 为特征的 lipid-associated macrophage（LAM），而终末期人肝纤维化中又有 `TREM2+ CD9+` scar-associated macrophage。

这篇论文询问的是更窄、也更临床相关的问题：在人类 MASL 到 MASH 的转变期，KC 是否真的被某一类巨噬细胞替代；这类细胞是否就是小鼠 LAM；它在肝小叶、门管区和炎症灶中的位置是否不同；哪些局部信号维持其表型。

### 2. 多层证据设计

研究分为三层：

1. 发现层：18 份冷冻肝组织进行 snRNA-seq，包括 4 例 lean、5 例 obese、4 例 MASL 和 5 例 MASH，共保留 176,150 个细胞核。
2. 空间与功能验证层：GeoMx WTA、CosMx、COMET Hyperplex、MILAN、免疫组化、precision-cut liver slice（PCLS）和体外巨噬细胞实验。
3. 临床转化层：206 例 MASLD bulk RNA 加 10 例对照、247 例 SomaLogic 血清蛋白组，以及 53,030 名 UK Biobank 参与者的 OLINK/PheWAS。

这种设计不是把所有数据拼成一个统一模型，而是让不同平台回答不同问题：snRNA-seq 负责“细胞是谁”，空间平台负责“细胞在哪里”，功能实验负责“候选信号能做什么”，临床队列负责“标志物是否随病程和表型变化”。

### 3. snRNA-seq：从原始核到髓系亚群

本地 `01_QC_and_Clustering.R` 直接实现主流程。每个样本先用 SoupX 估计并去除 ambient RNA；创建 Seurat 对象后保留 700–9,000 个检测基因、线粒体比例低于 30% 的细胞核，再用 `scDblFinder(dims=50)` 去除 doublet。

RNA 展示值使用 Seurat LogNormalize：

$$
x_{gi}=\log\left(1+10^4\frac{C_{gi}}{\sum_h C_{hi}}\right),
$$

其中 $C_{gi}$ 是基因 $g$ 在细胞核 $i$ 中的 UMI。随后以 50 个维度寻找跨样本 integration anchors，`IntegrateData` 生成批次校正的 integrated assay；scale 时回归总 UMI 和线粒体比例。PCA/UMAP 后以 Louvain resolution 1.5 得到初始簇，再人工归并为 8 类肝细胞。

髓系细胞被单独取出，使用 30 个 PCA 维度和 resolution 2 再聚类，得到 KC、MetMac、TransMac、preMac、Monocyte、cDC1、cDC2 和 migDC。代码里的名称仍是 `GPNMB Mac`，论文发表时改称 MetMac。这一命名差异很重要：代码中看到 `GPNMB Mac` 时不应误以为是另一个群体。

### 4. 组成变化：miloR 不只比较簇百分比

简单比较每个簇的百分比高度依赖聚类边界。miloR 改为在连续的 PCA/KNN 空间中建立重叠 neighborhood，测试每个局部区域在疾病组间是否增减。代码使用

- `buildGraph(k=30, d=30)`；
- `makeNhoods(prop=0.2, refined=TRUE)`；
- `testNhoods(design=~disease)`；
- graph-overlap 加权的 FDR。

对 neighborhood $j$，其样本计数可概括为负二项模型：

$$
N_{js}\sim\operatorname{NB}(\mu_{js},\phi_j),\qquad
\log\mu_{js}=\alpha_j+\beta_j\,\mathrm{disease}_s+\log L_s,
$$

其中 $L_s$ 是样本的细胞数 offset，$\beta_j$ 表示疾病相关的局部丰度变化。图 1e 显示 MASH 中 KC neighborhood 减少、MetMac neighborhood 增加；按患者计算的簇比例和分疾病 UMAP提供方向一致证据。因为发现队列只有 18 个样本，结果仍应由空间和独立队列验证，而不能只依赖局部图检验。

### 5. 状态变化：ssGSEA 与差异表达

作者在 KC、MetMac、TransMac、preMac 和 monocyte 中计算 16 组预先挑选的炎症、代谢、吞噬和应激通路。代码通过 `GSVA::gsva(method="ssgsea")` 得到每个样本/群体的排序富集分数，再用 limma 比较疾病阶段。

ssGSEA 的核心不是单个 marker，而是看某个基因集是否整体集中在排序列表顶部。因而“MetMac 在 MASH 中 inflammasome 或 cytokine score 升高”表示相关基因集合协同偏高，并不等于每个细胞都启动同一条完整信号通路。

图 1g 的总体模式是：KC 保持较稳定的吞噬、自噬和 IL10 相关特征，MASH MetMac 更突出抗原呈递、糖酵解、先天免疫和促炎程序。代码还为 CellPhoneDB 导出每个疾病阶段的 count 和 metadata，再导入配体–受体结果；这能提出细胞通讯候选，但表达共现不是实际分泌和受体激活的直接证明。

### 6. MetMac 是如何定义的

群体层面，MetMac 是人工注释的髓系簇，主要表达 `GPNMB`、`HS3ST2`、`LPL`、`FABP5` 等代谢/脂质处理基因。对 GPNMB 阳性细胞的专门分析则使用明确阈值：

$$
\mathrm{GPNMB}^+(i)=\mathbf{1}\{C_{\mathrm{GPNMB},i}\ge 2\}.
$$

本地 `04_Figure_3.R` 第 429 行按原始 RNA assay 的 GPNMB UMI 至少为 2 选择 944 个细胞，再以 5 个 PCA 维度、resolution 0.3 子聚类。这个阈值减少单 UMI 噪声，但仍是操作性定义，不等价于蛋白阳性。

作者还用 `AddModuleScore` 计算 LAM signature，基因集合为

$$
G=\{TREM2,LIPA,LPL,CTSB,FABP4,FABP5,LGALS1,LGALS3,CD9,CD36\}.
$$

模块分数近似为目标基因平均表达减去表达水平匹配的对照基因平均表达。结果显示 GPNMB+ 细胞中只有部分具有高 LAM score，且人 MASH 髓系细胞中 `TREM2` 阳性比例极低。图 4g 的组合统计进一步显示 MASH 中 GPNMB 阳性约 12%，非 MASH 约 5.7%，而 TREM2 阳性约 0.5%。因此论文把 MetMac 描述为与 LAM 有部分重叠、但并非等同的群体。

这个结论需要谨慎：GPNMB 也可在 KC 或其他巨噬细胞状态中表达，MetMac 与 TransMac/LAM 更可能是连续状态上的富集区域，而非绝对离散的谱系。

### 7. 空间证据：这些细胞在哪里

#### GeoMx

GeoMx 在 8 例 F3 at-risk MASH 活检中选择门管区、steatohepatitis 区和低脂肪区，以 CD68、CD45 和 panCK 分割细胞区域。80 个 segment 中 77 个通过质控。论文用患者作为随机效应比较区域表达，并以 snRNA-seq reference 做 SpatialDecon。

结果显示 steatohepatitis 区的 CD68 segment 富集 GPNMB、LPL、FABP5、LYZ 等，而低脂肪区更接近 KC。GeoMx 的差异表达模型不在 GitHub 中，本地 `03_Figure_2.R` 主要覆盖 SpatialDecon 和图形，因此区域 DEG 数量应以论文为最终证据。

#### CosMx

CosMx 在单细胞空间层面测量约 1,000 个 RNA 靶标。代码用 Seurat v5 加载、合并、SCTransform、PCA/UMAP 和人工注释，并展示 GPNMB、LPL、FABP5、HLA-DRA 与 IL32 的空间位置。它支持 GPNMB+ macrophage 在炎症/门管相关区域出现，但 panel 限定意味着没有测到的基因不能解释为不表达。

#### COMET 与 MILAN

COMET 进行循环多重蛋白成像，并可组合 IL32 RNA 与 GPNMB 蛋白；MILAN 在整张活检上迭代抗体染色，将 CD68、CD14 或 CD163 z-score 大于 1 的细胞定义为髓系，再按 GPNMB、LYZ、HLA-DR、SPP1 等门控。蛋白层结果支持 MASH 中 GPNMB+、HLA-DR+、lysozyme+ 巨噬细胞增加及门管附近定位。

COMET/MILAN 的完整分析代码未在仓库提供，所以这些结论可由论文图和方法核对，但不能从当前代码快照完全复现。

### 8. IL32–MetMac 轴：从共定位到功能实验

CosMx/COMET 显示 `IL32` 主要来自受损或 ballooning hepatocyte，并与 GPNMB+ macrophage 空间邻近。作者据此提出肝细胞 IL32 是局部信号，而不是仅凭 CellPhoneDB 的无空间配体–受体预测。

功能验证分两类：PCLS 中脂质负荷和 IL32 处理增加 GPNMB+ macrophage 的吞噬/溶酶体相关读出；THP-1 来源 macrophage 中，IL32 与棕榈酸组合改变 Oil Red O、内吞–溶酶体降解及 `IL1B`/`IL10` 等表达。论文还包含 LPL CRISPR 操作以评估脂质处理表型。

这些实验支持“IL32 可调节巨噬细胞代谢和炎症状态”，但不能仅凭空间相关宣称 IL32 是患者体内 MetMac 产生的唯一原因。PCLS、THP-1 和 CRISPR 的原始分析代码不在本仓库，属于论文证据而非代码复现证据。

### 9. 从图谱到临床队列

#### CIBERSORTx

本地 `Cibersort_MASLD.R` 从 snRNA-seq 中提取 KC、`GPNMB Mac` 和 monocyte 生成 signature，使用 batch correction s-mode、关闭 quantile normalization、100 permutations，对 bulk RNA 队列估计三类细胞比例。概念上求解

$$
Y_{g s}\approx\sum_k S_{gk}p_{ks},\qquad p_{ks}\ge0,
$$

其中 $Y$ 是 bulk 表达，$S$ 是单核 reference signature，$p$ 是样本中推断的细胞比例。结果显示随 MASH/纤维化或较高 NAS，MetMac fraction 增加、KC fraction 下降。

这是一种 reference-dependent deconvolution：如果真实患者细胞状态不在 signature 中，其信号可能被分配给最相近的三类，因此比例是模型估计而不是组织计数。

#### 血清蛋白与 PheWAS

247 例 SomaLogic 数据检验 GPNMB、MSR1 等可溶蛋白与 MASH/纤维化的关联。UK Biobank 的 53,030 人 PheWAS 再把 OLINK GPNMB/CD163 与 ICD-10 映射的 phecode 关联，并调整年龄、性别和 BMI。它说明标志物与代谢和肝病表型共享人群关联，但 PheWAS 不能判断 GPNMB 是致病因子、疾病结果还是共同代谢状态的标志。

### 10. 本地代码的可复现边界

#### 直接覆盖

- SoupX、QC、scDblFinder、Seurat integration 和细胞类型子聚类：`01_QC_and_Clustering.R`
- myeloid marker、ssGSEA、miloR、CellPhoneDB 输入输出：`02_Figure_1.R`
- GPNMB+ 阈值、子聚类、LAM score、CosMx 展示：`04_Figure_3.R`
- GeoMx SpatialDecon 和 Figure 2 绘图：`03_Figure_2.R`
- bulk signature 与 CIBERSORTx 结果分析：`Cibersort_MASLD.R`
- CosMx 专门流程：`CosMx_Nanostring.R`

#### 缺失或部分覆盖

- GeoMx 的完整质控和差异表达流水线；
- COMET 与 MILAN 的完整图像处理/统计；
- PCLS、THP-1、LPL CRISPR 功能实验分析；
- SomaLogic 血清蛋白组和 UKB PheWAS 分析；
- Figures 4–6 的多数统计生成代码。

因此代码—论文匹配度是中等：Figures 1–3 和 CIBERSORTx 有较好覆盖，后半篇功能与临床验证主要只能从论文和图中核验。

### 11. 阅读时必须保留的边界

1. MetMac 是表达状态与聚类标签，不等于已证明的独立发育谱系。
2. GPNMB UMI≥2、蛋白 z>1 等阈值属于不同平台的操作定义，不能直接互换阳性率。
3. MetMac 与 LAM 部分重叠；低 TREM2 支持“不是经典 LAM”，但不排除共享来源或连续过渡。
4. 空间邻近支持局部通讯假说，不等于配体受体因果；功能实验增强了证据但使用离体/细胞模型。
5. bulk deconvolution、血清标志物和 PheWAS扩大了临床相关性，却不能单独证明细胞群驱动疾病进展。

### 证据入口

- 论文：`paper source/paper/auto/paper.md`
- 图像：`paper source/paper/auto/images/`
- 图解：`figure_analysis.md`
- 方法：`doc_method.md`
- 代码映射：`doc_code.md`
- 本地代码：`OG_MB-MASLD-LIVER-2025/`，commit `1bad05447c93281e104fa465896954398a9f25bf`

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary — MASLD MacrophageAtlas

**Paper**: Boesch M et al., "Integrated multi-omics identifies distinct macrophage alterations during progression of metabolic dysfunction-associated steatohepatitis." *Nature Genetics* (2026).
**DOI**: 10.1038/s41588-026-02600-3
**Category**: datasource/atlases_resources
**Paper type**: atlas (multi-omics resource with biological discovery)

---

### Motivation & Novelty

#### Biological Problem
Metabolic dysfunction-associated steatotic liver disease (MASLD) affects >30% of the global population and is the leading indication for liver transplantation. Progression from simple steatosis (MASL) to active steatohepatitis (MASH) is driven by chronic inflammatory activation, with hepatic macrophages playing a central role. However, **which macrophage populations emerge specifically during MASL→MASH transition, and how they interact with the liver microenvironment, was poorly characterized in humans**.

#### Limitations of Existing Approaches
Prior work falls into two categories:

1. **Mouse models**: Identified lipid-associated macrophages (LAMs; *Trem2*+) and scar-associated macrophages (SAMs; *TREM2*+ *CD9*+) in murine MASH and cirrhosis. Key limitation: LAMs defined in adipose tissue (Jaitin et al., *Cell* 2019) and SAMs in cirrhotic liver (Ramachandran et al., *Nature* 2019) — translation to human progressive MASLD (MASL→MASH) was incomplete.

2. **Human snRNA-seq**: MacParland et al. (*Nat Commun* 2018) mapped healthy liver; Gribben et al. (*Nature* 2024) focused on epithelial plasticity in cirrhosis. No spatially resolved atlas across the pre-cirrhotic MASLD spectrum existed.

3. **Bulk RNA-seq and prior atlases**: Govaere et al. (*Sci. Transl. Med.* 2020) characterized transcriptomic signatures in bulk RNA-seq but lacked single-cell resolution. De Ponti et al. (*JHEP Rep.* 2024) reviewed macrophage diversity without spatial resolution.

#### Novel Contributions
1. **MetMac discovery**: Identifies a novel *GPNMB*⁺ *HS3ST2*⁺ metabolically active macrophage (MetMac) population that expands from MASL to MASH and is **distinct from classical LAMs** (lacks *TREM2*; only partial overlap with LAM signature)
2. **Spatial localization**: Demonstrates MetMac accumulation specifically in portal tracts and steatohepatitis regions (not parenchyma) using 4 spatial platforms (GeoMx, CosMx, COMET, MILAN)
3. **IL32-macrophage axis**: Discovers hepatocyte-derived IL32 as a paracrine signal driving GPNMB⁺ macrophage phagocytic activity and pro-inflammatory reprogramming
4. **Clinical biomarker translation**: Validates GPNMB, MSR1, LPL, HS3ST2 as disease activity markers in n=206 bulk RNA-seq and serum GPNMB as biomarker in n=247 patients; PheWAS (n=53,030) links GPNMB to metabolic syndrome

---

### Method Overview

#### Multi-Modal Design
The study integrates 8 assay modalities in a three-tier framework:
- **Discovery**: snRNA-seq (18 samples, 176,150 nuclei): 4 lean, 5 obese, 4 MASL, 5 MASH
- **Spatial validation**: GeoMx WTA (n=8 at-risk MASH F3), CosMx 1000-plex (n=10+2), COMET Hyperplex (n=6), MILAN (n=8)
- **Clinical translation**: Bulk RNA-seq (n=206+10), SomaLogic serum proteomics (n=247), PheWAS (n=53,030 UKB)

#### Computational Pipeline (snRNA-seq)
1. **Preprocessing**: SoupX ambient correction → scDblFinder doublet removal → Seurat v4 integration (dims=50, regressing nCount_RNA + %mito)
2. **Clustering**: UMAP + Louvain (res=1.5) → 8 broad cell types → type-specific subclustering → 8 myeloid subtypes
3. **Differential abundance**: miloR KNN (k=30, d=30) testing by disease group
4. **Pathway analysis**: ssGSEA (GSVA v1.42) on 16 curated MSigDB pathways; statistics via limma
5. **Cell-cell communication**: CellPhoneDB v3.1 per disease stage
6. **GPNMB⁺ subanalysis**: UMI≥2 threshold; 5-dim subclustering; LAM signature scoring (AddModuleScore)

#### Spatial Analysis
- GeoMx: Q3-normalized WTA profiling, linear mixed-effects model by region (GeoMxTools)
- CosMx: SCTransform → PCA(30) → UMAP → Louvain(0.3) → manual annotation; ImageDimPlot/ImageFeaturePlot
- COMET: Sequential immunofluorescence + RNA-FISH; HORIZON software
- SpatialDecon: snRNA-seq myeloid profile matrix as deconvolution reference

#### Clinical Translation
- **CIBERSORTx**: Bulk RNA-seq deconvolution using KC/MetMac/Monocyte signatures; 100 permutations, relative mode
- **Logistic regression**: SPSS, backward stepwise; ACP5/CD163/LPL/MSR1 → high disease activity
- **SomaScan**: 2,941 aptamer-based protein measurements; Mann-Whitney U test by disease category
- **PheWAS**: UKB n=53,030, 1,253 Phecodes; case-control OLINK protein associations

---

### Evaluation

#### snRNA-seq Findings (Figures 1, 3)
- **KC depletion**: Statistically significant decrease in MASH (miloR FDR<5%, Fig 1e; proportion boxplot p=0.03, Fig 1f)
- **MetMac expansion**: Significant increase in MASH (p=0.004), from ~10% to >25% of myeloid cells
- **GPNMB⁺ fraction**: 5.7% (non-MASH) → **12%** in MASH (Fig 3g)
- **LPL⁺ MetMac subset**: 2.8% MASH vs 0.2% no-MASH (+14-fold)
- **TREM2⁺**: Only 0.5% MASH — not a dominant human MASH macrophage marker

#### Spatial Validation (Figures 2-4)
- **GeoMx**: 207 DEGs between SH and low-steatosis regions; GPNMB highest fold-change gene (Fig 2c)
- **COMET**: GPNMB⁺ macrophages comprise 18.1% of CD68⁺/CD163⁺/CD14⁺ myeloid cells in end-stage MASH (Fig 4b)
- **MILAN**: GPNMB⁺ macrophages significantly increased MASL→MASH at protein level (p=0.022); HLA-DR⁺ also increased (p=0.006) (Fig 4e)
- **IHC**: GPNMB⁺ cells increase across MASLD spectrum (ANOVA linear trend p=0.002, n=20 biopsies; Fig 4a)
- **CosMx**: 9% of GPNMB⁺ macrophages within 10μm of cholangiocytes → portal infiltration confirmed

#### IL32 Axis (Figure 5)
- PCLS: Lipid loading induces GPNMB⁺ macrophage aggregation and ceroid formation in ex vivo human tissue
- CATD co-staining: Confirms active phagolysis in GPNMB⁺/CATD⁺ cells
- THP-1 in vitro: IL32 + PA (palmitate) → IL1B upregulation ~6× (p<0.0001) + IL10 reduction (p=0.0068)
- THP-1: 100 ng/mL IL32 → ~2× greater endo-lysosomal degradation (Fig 5i)
- THP-1: Oil Red O lipid uptake ~3× higher with IL32 (Fig 5h)

#### Clinical Validation (Figure 6)
- **Bulk RNA-seq (n=206)**: GPNMB NAS≥4 vs <4: p=2.36×10⁻⁸; LPL p=1.25×10⁻¹²; HS3ST2 p=3.02×10⁻⁹
- **CIBERSORTx**: KC fraction drops from ~50% (Normal) to ~30% (MASH F4); MetMac increases progressively (multiple p<0.05 comparisons)
- **Serum proteomics (n=247)**: GPNMB significant in all 4 clinical categories (at-risk MASH, F3-F4, MASH, high NAS); MSR1 in 3 of 4
- **PheWAS (n=53,030)**: GPNMB → diabetes mellitus + hypoglycemia; CD163 → chronic liver diseases

---

### Reproducibility: 2/5

**Justification**: The study is a high-quality multi-omics atlas but has substantial reproducibility limitations:

**Positive factors**:
- Code for Figures 1-3 is publicly available on GitHub (R scripts for snRNA-seq, GSVA, miloR, CellPhoneDB, CosMx)
- Raw snRNA-seq data available via EGA (EGAS50000000768)
- GeoMx and CosMx datasets on GEO (GSE312698, GSE312379)
- MILAN and COMET data on Zenodo/Figshare
- Methods section is detailed for snRNA-seq pipeline

**Negative factors**:
- **~50% of results lack code**: GeoMx DEG pipeline (Fig 2c/d), COMET/MILAN analysis (Fig 4), PCLS/in vitro experiments (Fig 5), serum proteomics/PheWAS (Fig 6) have no code in the repository
- **Raw snRNA-seq data access restricted**: EGA requires managed access application; data cannot be immediately used
- **Small discovery cohort**: n=18 samples (4+5+4+5) is underpowered for definitive subcluster identification; spatial validation modalities also small (n=6-10)
- **Mixed Seurat versions**: v4 for snRNA-seq, v5 for CosMx — creates software environment complexity
- **GeoMx pipeline uses proprietary GeoMxTools** not included in GitHub
- **No environment/dependency file**: No renv lockfile or conda environment YAML provided

**Practical notes**: A skilled bioinformatician can reproduce Figures 1-3 from the GitHub code given snRNA-seq data access through EGA. Figures 4-6 require proprietary platforms (HORIZON, COMET, MILAN) or tools not provided (GeoMx DEG pipeline, serum proteomics scripts). The in vitro experiments in Figure 5 require specialized cell biology expertise and equipment.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
