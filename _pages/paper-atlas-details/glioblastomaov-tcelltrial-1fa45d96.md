---
layout: default
permalink: /paper-atlas/glioblastomaov-tcelltrial-1fa45d96/
title: "GlioblastomaOV_TCellTrial"
nav: false
description: "Meylan 等人在 Cell（2026）中研究 CAN-3110（rQNestin34.5v.2）一期临床试验的复发性胶质母细胞瘤样本。论文并不是提出一个新的机器学习模型，而是把 CODEX 空间蛋白组、Xenium 空间转录组、bulk TCRβ 测序和病理学串成一条证据链：一次瘤内注射之后，原先已经存在于肿瘤中的 T 细胞克隆被扩增；其中一部分进入活肿瘤区，保持早期激活、组织驻留和细胞毒程序；病毒残留则主要局限于坏死区。"
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
      <span>Data Sources &amp; Technologies</span>
      <span>Cell · 2026</span>
    </div>
    <h1>GlioblastomaOV_TCellTrial</h1>
    <p>Persistent T cell activation and cytotoxicity against glioblastoma following single oncolytic virus treatment in a clinical trial</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2025.12.055" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 单次溶瘤病毒治疗后，胶质母细胞瘤中的 T 细胞为何能持续工作？

### 一句话结论

Meylan 等人在 *Cell*（2026）中研究 CAN-3110（rQNestin34.5v.2）一期临床试验的复发性胶质母细胞瘤样本。论文并不是提出一个新的机器学习模型，而是把 **CODEX 空间蛋白组、Xenium 空间转录组、bulk TCRβ 测序和病理学**串成一条证据链：一次瘤内注射之后，原先已经存在于肿瘤中的 T 细胞克隆被扩增；其中一部分进入活肿瘤区，保持早期激活、组织驻留和细胞毒程序；病毒残留则主要局限于坏死区。因此，晚期持续的 T 细胞反应更符合抗肿瘤免疫，而不是单纯追逐病毒抗原。

### 论文要解决什么问题？

GBM 对免疫治疗特别困难。论文指出，GBM 恶性细胞具有 NPC-like、OPC-like、AC-like 和 MES-like 等可塑状态，并能降低 MHC-I 或表达 PD-L1、CLEC2D、CD155 等免疫抑制分子。更基础的问题是 T 细胞本来就很少进入肿瘤实质，往往停留在血管周围。此前 CAN-3110 临床研究已经观察到治疗后 TCRβ 推断的 T 细胞比例与生存相关，但仍不能回答三个关键问题：

1. 晚期样本中的 T 细胞是否真的在攻击肿瘤细胞？
2. 它们是在识别残留病毒，还是在识别肿瘤？
3. 哪些空间微环境支持 T 细胞，哪些区域把 T 细胞排斥在外？

这项研究用空间位置把“细胞是谁”“处于什么功能状态”“离谁更近”和“患者结局如何”连接起来。

### 样本与三条测量轴

研究对象来自 NCT03152318 arm A：16 名复发性 GBM 患者接受一次 CAN-3110 瘤内注射，并在复发时切除肿瘤。由于不是固定时间的治疗中活检，样本反映的是不同患者从数周到两年以上的长期状态，而不是严格的纵向动力学。

| 测量 | 样本与规模 | 它回答的问题 |
|---|---|---|
| CODEX，27 个蛋白标记 | 16 例治疗后、28 个大区域、约 380 万细胞；另有 16 例治疗前、21 个区域 | T 细胞是否深入肿瘤，GZMB 高的 T 细胞是否邻近 cl-Casp3 高的凋亡肿瘤细胞 |
| Xenium，480 基因 | 8 名患者配对治疗前后，约 240 万细胞 | T 细胞激活/驻留状态、肿瘤状态、HSV 信号与定制 TCR 克隆的原位位置 |
| bulk TCRβ（immunoSEQ） | 肿瘤和外周血、治疗前后；生存分析覆盖更大的试验队列 | 哪些克隆治疗后扩增，这种扩增是否局限于肿瘤并与结局相关 |

Xenium 面板由 380 基因免疫肿瘤面板加 100 个定制探针组成。定制部分包括早期激活基因（如 *NR4A1*、*CD69*）、GBM 状态基因、5 个 HSV 基因以及患者特异的 TCR CDR3 探针。这个设计是论文最关键的技术桥梁：bulk TCRβ 先告诉研究者“哪个克隆扩增”，CDR3 探针再把这个克隆放回组织切片中。

### 从组织到结论的完整分析流程

```text
治疗前/后 GBM 组织
        |
        +--> CODEX 27 蛋白 --> 分割、标准化、细胞注释
        |                         |
        |                         +--> GZMB T 细胞与 cl-Casp3 肿瘤细胞的距离
        |
        +--> Xenium 480 基因 --> 细胞类型、T 细胞状态、GBM 状态
        |                         |
        |                         +--> 距离梯度、细胞邻域、HSV/TCR 原位定位
        |
        +--> bulk TCRβ ---------> 治疗前后克隆频率与“预存/新出现”分类
                                  |
                                  +--> 与 Xenium CDR3 探针、PFS/OS 联合解释
```

#### 1. 建立细胞地图

CODEX 用 DNA 条形码抗体循环成像。论文将 27 个通道对齐后完成细胞分割、蛋白强度归一化、聚类和人工注释，得到 11 类细胞。发布代码中，蛋白 MFI 先按标记做 z-score，再裁剪到 $[-5,5]$，避免少数极亮细胞主导降维。由于治疗后数据达到 380 万细胞，代码采用子集上拟合 UMAP/Leiden，再把嵌入和标签传播到全体细胞；治疗前样本还使用基于治疗后标注的标签转移。

Xenium 中，细胞经过表达量质控后，用 Seurat/Harmony 建立 11 个一级细胞类型；肿瘤细胞再按 GBM 分子状态细分，T 细胞再聚类为多个 CD8 和 CD4 状态。TCR 与 HSV 探针不用于全局 PCA，避免这些稀疏、患者特异信号决定总体聚类。

#### 2. 用距离而不是仅用丰度描述空间关系

核心距离函数对每个切片分别计算 $k=3$ 个最近邻的平均欧氏距离：

$$
d_i=\frac{1}{3}\sum_{j=1}^{3}\lVert \mathbf{x}_i-\mathbf{x}_{NN_j}\rVert_2.
$$

发布代码的参数名容易读反：`measure_distance_parallel()` 内部使用 `x = coords_source`、`query = coords_target`，并把结果命名为 `to` 细胞。因此，`from = Tumor cells, to = T cells` 得到的是**每个 T 细胞到三个最近肿瘤细胞的平均距离**。Xenium 坐标本身按微米解释；CODEX 脚本先用 0.325 μm/pixel 换算再计算。

距离随后被分成分位数区间，用来回答两类互为镜像的问题：

- 越靠近肿瘤的 T 细胞表达什么？
- 越远离 T 细胞的肿瘤处于什么状态？

这种分析发现，肿瘤近端 T 细胞富集 *NR4A1*、*IFNG*、*GZMB*、*PRF1* 以及组织驻留基因 *ITGAE*、*ZNF683*、*CXCR6*；远端 T 细胞更偏 *TCF7*、*IL7R*、*SELL* 的干样/记忆样程序。

#### 3. 用细胞邻域描述组织结构

对每个细胞，代码统计 $k$ 个最近邻中的细胞类型比例，形成组成向量：

$$
\mathbf{f}_i=(p_{i,\mathrm{T}},p_{i,\mathrm{tumor}},p_{i,\mathrm{B}},\ldots).
$$

随后用 k-means（`nstart=25`, `iter.max=300`）把相似组成聚成 cellular neighborhoods，再合并解释为肿瘤核心、T 细胞-肿瘤界面、淋巴聚集区、血管区和坏死相关区等空间生态位。这里的“邻域”不是预先画出的解剖区域，而是局部细胞组成相似的计算分组。

#### 4. 把 TCR 克隆历史放回空间中

bulk TCRβ 将治疗前后均可检测的克隆定义为 pre-existing，将只在治疗后出现的定义为 emergent，并比较肿瘤与 PBMC 中的频率变化。研究随后为 P28 和 P34 的候选 CDR3 设计 Xenium 探针，最终在组织中验证 43 个克隆。这样可以直接比较扩增克隆和其他 T 细胞到肿瘤的距离，而不只依据总体 T 细胞密度推断。

### 七幅主图如何组成证据链

#### 图 1：一次治疗后，T 细胞浸润可持续很久

CODEX 图像显示淋巴聚集体和深入 GFAP 阳性肿瘤区的 CD4/CD8 T 细胞。Xenium 复现总体 T 细胞增加：中位密度由治疗前 30.4 增至治疗后 138 cells/mm²（$p=0.0078$）。部分样本在 6–25 个月仍有显著浸润，最长超过两年。

#### 图 2：空间共现支持持续细胞毒作用，但不是直接因果证明

GZMB 高 T 细胞与 cl-Casp3 高肿瘤细胞在图像中紧邻；跨样本密度也呈正相关。更短的 GZMB 高/中 T 细胞—肿瘤距离与较长 PFS（175 μm 对 262 μm，$p=0.038$）和较低肿瘤生长率相关。论文谨慎指出，这仍是固定组织切片上的空间和相关性证据；要直接证明杀伤事件，需要体内活细胞成像。

#### 图 3：肿瘤近端与远端 T 细胞承担不同任务

肿瘤近端 T 细胞表现早期 TCR 激活、细胞毒和组织驻留程序；远端 T 细胞表现干样/记忆样程序。可把它理解为“前线效应细胞”和“后方补给库”的空间分工，但后者是机制解释，不是谱系追踪证明。

#### 图 4：T 细胞反应被组织成不同生态位

细胞邻域显示，肿瘤-T 细胞界面富集效应/驻留 T 细胞；淋巴聚集区则富集 B 细胞、树突细胞和干样 T 细胞。主图的组织图像支持这些计算邻域确实对应可见的空间结构。

#### 图 5：晚期 T 细胞并不围绕残留病毒聚集

HSV 蛋白和核酸信号集中在坏死区，附近富集巨噬细胞和中性粒细胞，却缺少 T 细胞。这个空间分离否定了“晚期深部 T 细胞主要被残留 HSV 吸引”的简单解释，但不能逐个确定 TCR 的抗原特异性。

#### 图 6：被治疗放大的主要是预先存在的肿瘤内克隆

治疗后肿瘤 TCR 克隆性升高，而 PBMC 没有同样变化。预存克隆的扩增与更长总体生存相关（中位 445 对 235 天）；Xenium 追踪到的扩增克隆比其他 T 细胞更靠近肿瘤（中位 32.3 对 51.8 μm）。数据库比对未发现 HSV 特异匹配，但“未匹配”不能等同于已经证明肿瘤抗原特异性。

#### 图 7：缺氧 MES-like 2 区域构成空间抗性壁垒

治疗后 MES-like 2（缺氧）状态扩增；距离 T 细胞最远的肿瘤区逐渐由 MES-like 2 占据，并伴随 *CA9*、*VEGFA* 升高。图像显示 VEGFA 高区域与 T 细胞信号互斥。这支持缺氧/VEGF 相关排斥机制，也为联合抗 VEGF 或减少长期地塞米松暴露提供假说，但本研究没有直接检验这些联合治疗。

### 最重要的结果数字

- CD8/Treg 中位比值：治疗前 6.8，治疗后 21.1（$p=0.0042$）。
- CD8 组织驻留 T 细胞治疗后平均 $\log_2FC=3.03$。
- IFNG 阳性和 NR4A1 阳性 T 细胞分别比对应阴性细胞更靠近肿瘤 7.8 μm 和 2.8 μm；IL7R 阳性和 TCF7 阳性细胞分别更远 27.4 μm 和 25.1 μm。
- 肿瘤 TCR 克隆性治疗后升高（$p=0.032$），PBMC 未显著改变（$p=0.62$）。
- 最远 T 细胞距离区间中的肿瘤细胞有 78% 为 MES-like 2。

### 代码与论文能对到哪里？

释放仓库是以图为中心的 R Markdown 工作流，而不是一键运行的软件包。

| 论文分析 | 直接代码位置 | 复现边界 |
|---|---|---|
| 最近邻平均距离 | `scripts/utils/maxime_utils.r:4-46` | 实现明确；依赖已构建的 Seurat 对象和坐标 |
| cellular neighborhood | `scripts/utils/maxime_utils.r:65-149` | kNN 组成和 k-means 明确；最终生物学命名含人工合并 |
| Xenium T 细胞—肿瘤距离分箱 | `scripts/figures/Figure_3_4_Xenium_spatial_distances.Rmd:75-128` | 实现明确；上游对象不在仓库内生成到最终状态 |
| CODEX GZMB/cl-Casp3 阈值与距离 | `scripts/figures/Figure_2_CODEX_spatial_Tcell_tumor.Rmd:109-121,550-569` | 阈值和距离明确；需 CODEX 中间对象及临床表 |
| MES-like 2 与 T 细胞排斥 | `scripts/figures/Figure_7_XENIUM_Tumor_subtype.Rmd:429-469` | 互为方向的距离计算可追踪；成图依赖预处理对象 |

代码的优势是主图分析步骤和参数可读，论文也公开 CODEX（S-BIAD1921）与 Xenium（GSE296577）数据。主要障碍是多个脚本直接读取未随仓库提供的 `.qs` 中间对象和临床 Excel 表，聚类标签还有人工选择；因此复现更接近“从公开原始/处理数据重建分析”，而不是克隆仓库后立即一键重画全部主图。仓库快照没有可验证的 Git commit 元数据，所以这里不虚构提交哈希。

### 应如何解读这篇论文？

最稳健的结论是：单次 CAN-3110 后，GBM 中可以出现长期、深部、功能活跃的 T 细胞浸润；空间蛋白与转录证据、克隆扩增和结局关联彼此支持。更强的机制表述——这些 T 细胞逐个识别哪些肿瘤抗原、病毒如何启动它们、缺氧是否直接造成排斥——仍需要抗原验证、功能实验和前瞻性固定时间采样。

因此，这篇论文的贡献不在于一个单独算法，而在于一套证据组合：**用空间距离建立功能关联，用 TCR 克隆连接治疗前后历史，再用病毒与缺氧区域的空间位置排除替代解释并定位耐药生态位。**

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary — GBM CAN-3110 (Meylan et al., Cell 2026)

### Motivation & Novelty

#### Biological Problem

Glioblastoma (GBM) is refractory to immunotherapy primarily because it is a "cold tumor": T cells infiltrate sparsely, localizing to perivascular spaces rather than tumor parenchyma. Three failed phase III checkpoint blockade trials (CheckMate 143, *JAMA Oncol.* 2020; nivolumab+RT, *Neuro-oncology* 2022, 2023) demonstrated that simply blocking PD-1 is insufficient when T cells are absent. A therapeutic intervention capable of introducing T cells into the tumor bed — and maintaining that infiltration — is a prerequisite for effective combination immunotherapy.

#### Why Existing Approaches Fall Short

Prior spatial analyses of GBM immunotherapy were limited to:
- IHC quantification of T cell density (bulk counts, no functional states)
- Single-cell RNA-seq without spatial context
- The predecessor Ling et al. (*Nature* **623**, 2023) study that showed TCRβ T cell fraction correlates with survival, but lacked in situ mechanistic evidence

No prior study provided in situ evidence of ongoing T cell-mediated cytotoxicity (simultaneous spatial co-localization of effector T cells with apoptotic tumor cells) in human GBM.

#### Unique Contributions

1. **First in situ evidence of T cell cytotoxicity** in human GBM: spatial co-localization of GZMB+ CD8 T cells with cl-Casp3+ tumor cells at late time points post-treatment
2. **Deep spatial profiling using two complementary technologies**: CODEX (27-marker spatial proteomics) + Xenium (480-gene spatial transcriptomics) on the same clinical trial cohort
3. **Novel TCR spatial tracking**: patient-specific CDR3 probes for Xenium enable direct in situ visualization of individually identified expanded clones interacting with tumor cells
4. **Demonstration that oHSV expands pre-existing tumor-infiltrating T cell clones**: not a de novo anti-viral response, but amplification of pre-existing tumor-reactive T cells
5. **Spatial resistance mechanism**: hypoxic mesenchymal (MES-like 2) tumor regions create T cell exclusion zones correlated with VEGFA expression
6. **Viral restriction proof**: HSV remnants restricted to necrotic regions, macrophages/neutrophils (not T cells) near virus — evidence against viral antigen driving late T cell persistence

---

### Method Overview

#### Algorithmic Framework

The study uses three complementary multi-omic spatial technologies analyzed with standard bioinformatics pipelines:

**CODEX (CO-Detection by indEXing):** 27-antibody multiplexed imaging using DNA-barcoded antibodies in 12 iterative hybridization cycles. Processed with: z-score normalization (clipped ±5), UMAP (30% subset → umap_transform for full 3.8M cells), Leiden clustering (resolution=2 → 56 clusters → 11 cell types), XGBoost for label transfer to pre-treatment samples.

**Xenium spatial transcriptomics:** 480-gene in situ RNA detection (380 commercial + 100 custom probes). Processed with: QC (>50 UMI OR >25 genes), Harmony batch correction, Leiden clustering → 11 tier-1 cell types, then separate clustering for tumor subtypes (6 GBM cell states, Neftel et al.) and T cell states (12 clusters → 8 CD8 + 2 CD4 states).

**Bulk TCRβ sequencing (immunoSEQ):** 33 patients, tumor + PBMC, pre + post. Clonotype frequency tracking; database screening against VDJdb and McPAS-TCR; Xenium CDR3 probe design for spatial validation in 2 patients.

**Spatial analysis:**
- *Proximity*: mean distance to k=3 nearest tumor cells per T cell (μm after pixel conversion)
- *Cellular neighborhoods*: kNN composition vectors → k-means (K=14 → 8 zones)
- Distance-based differential expression along decile bins

#### Key Technical Components

- DAPI low → necrotic/low-count cells excluded from analysis
- TCR/HSV probes excluded from PCA (sparse probes distort global embedding)
- Blank antibody channels used to identify autofluorescent cells
- Pixel resolution: CODEX 0.325 μm/pixel; Xenium 0.2125 μm/pixel

---

### Evaluation

#### Datasets

| Dataset | Patients | Technology | Samples |
|---------|---------|-----------|---------|
| CODEX post-treatment | 16 | 27-marker multiplex IF | 28 regions |
| CODEX pre-treatment | 16 | 27-marker multiplex IF | 21 regions |
| Xenium spatial transcriptomics | 8 (paired) | 480 genes | 16 samples |
| Bulk TCRβ sequencing | 33 | immunoSEQ | Tumor + PBMC, pre + post |
| scRNA-seq (Smart-seq2) | 1 (P28) | Full transcriptome | Single cell T cells |

**Data accessions:** CODEX: EBI BioImage Archive S-BIAD1921; Xenium + Seurat: GEO GSE296577; TCRβ-seq: dbGaP phs003378.v2.p1

#### Key Results

**T cell infiltration:**
- CD8 T cells: large post-treatment increase (CODEX, Wilcoxon p<0.05); Xenium: 30.4 → 138 cells/mm² (p=0.0078)
- Deep T cell infiltration sustained up to >2 years post-treatment
- CD8/Treg ratio: 6.8 pre → 21.1 post (p=0.0042)

**In situ cytotoxicity (Figure 2):**
- GZMB^hi CD8 T cells correlate with cl-Casp3^hi tumor cells (r=0.4, p=0.035)
- GZMB^hi CD4 T cells: r=0.5, p=0.007
- GZMB^lo CD8 T cells: inverse correlation (r=−0.5, p=0.007)
- Shorter T cell-tumor distance → longer PFS: 175 vs 262 μm (p=0.038)
- Shorter T cell-tumor distance → lower tumor growth (p=0.028)

**T cell spatial organization (Figure 3):**
- NR4A1+/early activated T cells: closest to tumor (median −2.8 μm vs overall median)
- IFNG+ T cells: −7.8 μm closer than median
- Stem-like (IL7R+, TCF7+): +27.4 and +25.1 μm farther from tumor
- Most pronounced increase post-treatment: tissue-resident CD8 (log2FC=3.03), stem-like CD8 (2.87), CD4 Treg (2.46)

**Cellular neighborhoods (Figure 4):**
- 8 functional zones: tumor, tumor-T interface, lymphoid aggregate, vasculature, peri-necrotic, necrotic
- ~40% of T cells in tumor-T cell interface; ~16% in lymphoid aggregates
- Stem-like T cells: 35% of lymphoid aggregate T cells, interact with B cells (56 μm) and DCs (119 μm)
- IFN-responsive CD8: 5-fold enriched in tumor-proximal zone (p=0.0156)

**Viral localization (Figure 5):**
- HSV protein: 32.1% of post-treatment regions show IHC staining, exclusively in necrotic areas
- T cells: log2FC = −3.47 (depletion) within 50 μm of HSV+ regions
- Macrophages/HLA-DR+: log2FC >1 (enrichment) near HSV+ regions
- 15/1246 expanded TCRs matched known specificities; 0 matched HSV or HSV-related sequences

**TCR clonal dynamics (Figure 6):**
- Tumor clonality: significantly increased post-treatment (p=0.0320); PBMC stable (p=0.62)
- Pre-existing clone expansion → longer OS: 445 vs 235 days median (p=0.033), log-rank p=0.012
- All 43 Xenium-tracked clonotypes enriched in tumor vs PBMC (P28: p=0.00093; P34: p=1.3×10⁻⁸)
- Expanded TCRs: median 32.3 μm from tumor vs 51.8 μm for other T cells (Δ=−19.6 μm, p<10⁻⁴)
- Dexamethasone >100 days: r=−0.414 with T cell clonality (p=0.04)

**Tumor resistance mechanism (Figure 7):**
- MES-like 2 (hypoxia): log2FC=1.38 post-treatment (p=0.0078) — expansion at recurrence
- VEGFA correlates with MES-like 2 signature (r=0.64)
- In T cell exclusion zones (90-100th percentile: 214-3,456 μm from T cells): 78% MES-like 2
- Progressive CA9 and VEGFA gradient with increasing T cell distance

---

### Reproducibility

**Rating: 3/5**

**Strengths:**
- Code fully released (github.com/maximemeylan/GBM_CAN3110), well-documented R Markdown notebooks
- Data deposited in open repositories (GEO, BioImage Archive, dbGaP)
- Constants file with all key parameters (pixel sizes, color palettes, clustering parameters)
- Figure notebooks annotated with corresponding panel labels

**Limitations:**
- **Private clinical data**: clinical_xlsx (`2023_12_1_CAN3110_Trial_Patient_Summary_no_PHI.xlsx`) required but not publicly shared (PHI removed)
- **Intermediate .qs Seurat objects not in GEO**: the analysis requires pre-processed Seurat objects (e.g., `Xenium_tier1-2_T_resivion_20250911.qs`, `02_GBM_seurat_corrected_030924.qs`). GEO contains raw/processed Xenium output; re-running full preprocessing would be needed.
- **Partial XGBoost training code**: the balancing, training loop, and early stopping implementation is described in the paper but not fully replicated in the released code
- **Manual cluster annotations**: cluster-to-cell-type mapping uses hardcoded Leiden cluster IDs that may shift with different random seeds; annotations would need to be redone from scratch
- **Smart-seq2 data for P28**: scRNA-seq data generation described but not obviously available; likely in GEO but not explicitly noted in the code

**Practical notes:**
- R 4.4.2 with Seurat 5.0.2 — newer Seurat versions have API changes
- CODEX processing requires a custom pipeline (DFCI-CODEX-group/CODEX-custom-pipeline, separate repo)
- qs package needed for fast file reading (not CRAN standard)
- 3.8M cell CODEX dataset requires >32GB RAM for full analysis
- dbscan and pbapply needed for spatial analysis utils

**Common pitfalls:**
- Running UMAP on full 3.8M cells without the subset strategy will run out of memory
- TCR/HSV probes must be excluded from PCA — including them creates patient-specific spurious clusters
- Area calculation for Xenium (P51 has manually hardcoded value)
- CODEX pixel size (0.325 μm) vs Xenium (0.2125 μm) must be correctly applied

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
