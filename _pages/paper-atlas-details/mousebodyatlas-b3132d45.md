---
layout: default
permalink: /paper-atlas/mousebodyatlas-b3132d45/
title: "MouseBodyAtlas"
nav: false
description: "这项研究把成年小鼠整身切成 10 μm 纵切片，铺到约 2×6 cm、含 974,016 个空间条码的 Array-seq 芯片上，同时获得 H&E 与全转录组。作者用 5,900 万单细胞构成的 CellKb 参考给每个 spot 注释细胞类型，再训练 LABEL 从 H&E 图像直接预测器官、组织亚区和细胞类型，最后用 LPS 内毒素血症展示 STAT1/IRF1 驱动的全身炎症响应。"
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
      <span>Cell · 2026</span>
    </div>
    <h1>MouseBodyAtlas</h1>
    <p>Whole-body molecular and cellular mapping of the laboratory mouse</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2026.03.006" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MouseBodyAtlas 方法解读：整只小鼠的空间转录组与虚拟染色

### 一句话理解

这项研究把成年小鼠整身切成 10 μm 纵切片，铺到约 2×6 cm、含 974,016 个空间条码的 Array-seq 芯片上，同时获得 H&E 与全转录组。作者用 5,900 万单细胞构成的 CellKb 参考给每个 spot 注释细胞类型，再训练 LABEL 从 H&E 图像直接预测器官、组织亚区和细胞类型，最后用 LPS 内毒素血症展示 STAT1/IRF1 驱动的全身炎症响应。

### 1. 技术障碍

普通空间转录组载玻片容不下成年小鼠纵切面；整身切片又容易碎裂并损伤 RNA。研究使用 cryomacrotome 和 Kawamoto film method 保持结构，把切片转移到定制 Agilent 1M Array-seq slide。每个 spot 带 18 nt 空间条码、UMI 和 poly-dT，因此测序 reads 可还原“哪个转录本来自身体哪个位置”。

两张对照切片分别覆盖 588,299 和 610,689 个有效 spots，平均每 spot 约 662 个基因和 1,241 个 UMI。图 1 中脑层、小肠绒毛轴和肝小叶分区 marker 与解剖位置一致，说明坐标注册保留了真实组织结构。

### 2. 从 reads 到空间表达矩阵

`Preprocessing/STARSolo_n18.sh` 用 STARsolo 对齐。代码刻意按 `R2 R1` 传入 reads：Array-seq 的 R1 保存 barcode+UMI，R2 保存 cDNA，与常见 10x 命令直觉相反。barcode 使用精确匹配，UMI 用 1MM_CR 校正。

预处理把 spot count matrix 与空间坐标、H&E 图像合并。组织 mask 由灰度/模糊阈值得到，但 Array-seq 与 H&E 的初始配准点在 Adobe Illustrator 中人工确定，`Scale_coordinates()` 只负责之后的比例变换。这是重要可复现边界：代码不能从原始图像自动恢复所有人工 landmark。

代码多处使用 `sc.pp.filter_genes(..., min_counts=25)`，而论文写至少 20 UMI/gene；这是实际实现与方法文字的阈值差异。标准的 total-count normalization、log1p、HVG/PCA/Leiden 随后用于器官与亚区聚类。

### 3. CellKb 如何给 spot 赋细胞类型

每个 Array-seq spot 通常混合多个细胞。CellKb 汇集 466 项研究、约 5,900 万单细胞，构建 9,692 个签名并归并为 495 个 granular types。对每个 spot，先取相对其他 spots 正 log-fold-change 最高的 500 个基因，再与参考签名做秩匹配。

论文的比例分数为

$$
P_i=(M_i-\bar M)+0.1\bar M(n_i-1),
$$

其中 $M_i$ 是类型 $i$ 的匹配分数，$\bar M$ 是 top-20 平均分，$n_i$ 是 top-20 中该类型重复命中的签名数。top-3 再归一化用于可视化。

这个 $P_i$ 是启发式相对分数，不是严格的细胞比例后验概率。CellKb 服务和完整 5,900 万细胞参考不在本地仓库，因此核心赋值无法仅靠当前代码快照从头复现。作者用 RCTD、CARD 和 cell2location 比较，spot-level concordance 分别约 93.7%、91.4% 和 87.8%，说明主导类型较稳定，但并不验证所有稀有类型。

### 4. LABEL：从 H&E 预测空间标签

LABEL 的训练标签来自相邻 Array-seq/H&E spot。流程是：

1. Vahadane stain normalization；
2. 每个 spot 周围截取 128×128 px patch；
3. UNI2-h ViT-Giant 提取 1,536 维形态特征；
4. 将二维坐标放在图像特征之前拼接；
5. StandardScaler 后 PCA 到 200 维；
6. KNN（$k=5$）分层预测 organ、subregion 和 cell type。

记图像 embedding 为 $h_i$、坐标为 $(x_i,y_i)$：

$$
z_i=\operatorname{PCA}_{200}\left(\operatorname{Scale}[x_i,y_i,h_i]\right),
\qquad
\hat y_i=\operatorname{mode}\{y_j:j\in N_5(z_i)\}.
$$

坐标在 PCA 前注入意味着 LABEL 不只是看形态，还利用器官在身体中的位置。这提高整身切片准确率，但也可能削弱对器官位置异常、移植或严重病理结构的泛化。

图 3 显示 organ accuracy 约 0.91，leave-one-section-out 为 0.71；subregion 为 0.73/0.47。肝细胞等形态明确、丰富的类型预测较好，免疫和稀有类型明显较弱。代码还训练五层标签，而论文主要报告三层。

#### 一个实现问题

验证 notebook 对训练集 `fit_transform` 后，又在 evaluation data 上重新 `scaler.fit_transform`，而不是使用训练 scaler 的 `transform`。这使 train/eval 的尺度基准不完全一致。PCA 仍由训练集拟合，但该处理不是标准无泄漏部署流程，报告性能应按现有代码理解，不能视为理想外部泛化估计。

### 5. 全身 LPS 炎症图谱

小鼠腹腔注射 LPS，12 小时后进行整身 Array-seq。作者在 37 个组织亚区做 control–LPS 差异表达，使用 Wilcoxon 和 BH 校正，报告 5,143 个 DEGs。空间图显示炎症并非均匀：同一基因或通路在不同器官、不同 broad cell type 中效应不同。

CellKb 比例还用于比较细胞组成，并用独立 IHC 验证肺/脾 neutrophil、多个器官 macrophage、fibroblast 以及胸腺/脾细胞凋亡。spot 的推断比例变化可能同时受细胞数、RNA 含量和状态改变影响，因此 IHC 是必要的正交证据。

CellChat 用 ligand/receptor 表达和空间约束推断通讯变化。这些结果代表候选信号网络，不是实际蛋白结合或分泌通量。

### 6. IRF1/STAT1 调控网络

pySCENIC 先用 GRNBoost2 从表达共变异推断 TF–target 候选，再用 motif enrichment 修剪直接调控候选，AUCell 计算每个 spot/cell-type 中 regulon 活性：

$$
\mathrm{AUC}_{R,i}=\operatorname{AUC}\bigl(\text{样本 }i\text{ 的基因排序中 regulon }R\text{ 的累积命中曲线}\bigr).
$$

论文筛选 motif NES≥3.2、Q≤0.001 的 STAT1/IRF1 regulons，并比较 LPS 与 control 的 ΔAUCell。图 7 显示两者在造血和非造血细胞中广泛激活，但 target 组合具有器官特异性。

Irf1−/− 与 Stat1−/− 小鼠提供功能验证：两种 KO 均减弱 LPS 后体温下降，并逆转部分器官 ISG 表达。KO 结果支持 STAT1/IRF1 是系统炎症的重要调控节点，但不表示它们解释全部 LPS 反应。

### 7. 代码覆盖范围

#### 可直接核对

- STARsolo 与 read layout：`code/analysis/spatial transcriptomics/Preprocessing/`
- AnnData、组织 mask、坐标缩放：同目录 preprocessing scripts
- organ/subregion clustering 与 DE：`Spatial_annotation/`、`DE/`
- RCTD/CARD/cell2location benchmark：`CellType_Deconvolution_Benchmarking/`
- LABEL patch、UNI2-h、PCA/KNN 与评估：`code/LABEL/`
- pySCENIC/AUCell：`pySCENIC_workflow/`

#### 不完整或外部

- CellKb 数据库、signature 生成和在线匹配服务；
- 定制条码设计文件和芯片制造；
- Adobe Illustrator 人工配准 landmark；
- 论文的 patch-size ablation（仓库主要硬编码 128 px）；
- 完整实验流程和 IHC/KO 原始量化。

### 8. 阅读边界

1. Array-seq spot 不是单细胞；CellKb 的“比例”是参考驱动的启发式估计。
2. LABEL 同时利用形态和绝对空间位置，不能视为纯组织病理 foundation-model 分类器。
3. 只有两张主要对照、两张主要 LPS 空间切片，spot 数巨大但生物学重复数有限。
4. DEG 与 regulon 活性是关联证据；KO 和 IHC 提供更强验证，但仍存在剂量、时间点和器官采样边界。
5. 代码使用 UNI2-h/1536D，而论文对 UNI 的引用较宽泛；复现应以本地 checkpoint 与 notebook 为准。

### 证据入口

- 论文：`paper.md`
- 图像：`images/`
- 图解：`figure_analysis.md`
- 方法：`doc_method.md`
- 代码映射：`doc_code.md`
- 本地代码：`code/`（GitHub `chevrierlab/WMST-paper`；本地合同未记录 commit）

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## summary.md — MouseBodyAtlas

**Paper**: Whole-body molecular and cellular mapping of the laboratory mouse
**Authors**: Clevenger MH, Cipurko D, Patil A, Li B, Takahama M, Mei L, Plaster M, Richey G, Kawamoto T, Bao F, Chevrier N
**Journal**: *Cell* (2026-03-27) | DOI: 10.1016/j.cell.2026.03.006
**Type**: Atlas / Technology paper

---

### Motivation & Novelty

The laboratory mouse is the dominant model system in biomedical research, yet no technology existed for simultaneous, genome-wide measurement of gene expression across all tissues and cell types of the intact adult mouse body. Two complementary approaches existed but were incompatible with each other:

- **Whole-body imaging**: optical clearing (e.g., CUBIC, *Cell* 2014; iDISCO, *Nat Biotechnol* 2024) enables body-wide visualization of specific fluorescent markers, but is restricted to pre-selected proteins and cannot measure genome-wide expression.
- **Spatial transcriptomics**: platforms like Visium/10x (Ståhl et al., *Science* 2016; Moses & Pachter, *Nat Methods* 2022 review) measure thousands of genes per tissue section but are restricted to small tissue areas (typically 6.5 × 6.5 mm) that cannot accommodate adult mouse cross-sections (~2 × 6 cm).

The fundamental gap was threefold: (1) no histological sectioning method preserved RNA integrity across adult mouse whole-body sections; (2) spatial transcriptomics capture arrays were too small; and (3) no computational framework existed to handle the scale and complexity of body-wide cell-type annotation.

**What's new**:
1. **Array-seq whole-mouse platform**: Adaptation of the Array-seq technology (*Nat Methods* 2024) to whole-mouse sections using the Kawamoto film method for cryomacrotome sectioning. Custom Agilent 1M microarray with 974,016 spatial barcodes covering ~2×6 cm.
2. **Scalable cell-type assignment**: A rank-based CellKb framework using a curated reference of 59M single cells from 466 studies, mapping 495 granular cell types without requiring batch correction between reference datasets.
3. **LABEL virtual staining model**: A spatially aware KNN classifier combining UNI2-h (ViT-Giant pathology foundation model) features with spatial coordinates, enabling automated annotation of H&E images at organ/tissue/cell-type level without sequencing.
4. **Body-wide disease mapping**: First whole-organism spatial transcriptomics profiling of a disease model (endotoxemia/LPS), revealing tissue-specific and cell-type-specific transcriptional responses at the whole-body scale.

---

### Method Overview

The paper has four interconnected components:

#### 1. Experimental Platform (Array-seq for Whole-Mouse Sections)
Whole adult mice are embedded in SCEM medium, flash-frozen, and sectioned at 10μm using a cryomacrotome (Leica CM3600XP). Sections are mounted on custom Array-seq slides (Agilent SureSelect 1M, repurposed for spatial transcriptomics capture) carrying 974,016 spot-barcoded poly-dT probes. H&E staining is performed on the slides, followed by tissue permeabilization and reverse transcription. Sequencing is performed on Illumina NovaSeq 6000 (44bp R1 + 70bp R2).

#### 2. Spatial Cell-Type Assignment (CellKb)
Each Array-seq spot's top 500 differentially expressed genes (ranked by positive log FC vs all spots) are compared against 9,692 cell-type-specific gene signatures from CellKb using a rank-based scoring method. Spots are assigned the top-scoring cell types, with proportions computed via: $P_i = (M_i - \bar{M}) + 0.1 \cdot \bar{M} \cdot (n_i - 1)$.

#### 3. LABEL (Learning Annotations By Embedding with Landmarks)
LABEL transfers spatiotranscriptomics-derived annotations to histology images. It uses: (1) Vahadane stain normalization, (2) UNI2-h ViT-Giant (1536D) feature extraction from 128×128 pixel patches, (3) spatial coordinate injection before PCA(200), and (4) hierarchical KNN(k=5) classification at three levels (organ → tissue subregion → broad cell type).

#### 4. Endotoxemia Disease Mapping
LPS (3-5 mg/kg i.p.) is used to induce systemic inflammation. Whole-mouse Array-seq profiles from LPS and control mice are compared: DE analysis (Wilcoxon, FDR<0.05), ligand-receptor inference (CellChat with spatial constraints), cell-type composition changes (Propeller test), and GRN inference (pySCENIC with IRF1/STAT1 as candidate TFs).

---

### Evaluation

#### Datasets
- **Array-seq**: 2 control + 2 LPS whole-mouse sections from 6-week-old female C57BL/6J mice; ~600k spots per section; ~1.2M total spots
- **KO validation**: Irf1−/− and Stat1−/− mice (LPS + control, bulk RNA-seq, 8 organs)
- **IHC validation**: Ly6G (neutrophils), F4/80 (macrophages), Vimentin (fibroblasts), TUNEL (apoptosis), 3-5 independent mice per group
- **LABEL external test**: 4 additional H&E-only whole-mouse sections from same mice (different depths)

#### Key Results
| Metric | Value |
|---|---|
| Spots per whole-mouse section | 588,299 – 610,689 |
| Genes detected per spot (average) | 662.3 ± 2.9 |
| UMIs per spot (average) | 1,241.4 ± 19.2 |
| Organ-level inter-replicate correlation (Pearson) | 0.968 ± 0.013 |
| Array-seq vs bulk RNA-seq correlation | 0.790 ± 0.041 |
| Granular cell types detected (of 495) | 67–69% per section |
| CellKb vs RCTD concordance | 93.7% |
| CellKb vs CARD concordance | 91.4% |
| CellKb vs cell2location concordance | 87.8% |
| LABEL organ accuracy (in-distribution) | 0.91 |
| LABEL organ accuracy (leave-one-out) | 0.71 |
| LABEL tissue subregion accuracy (in-dist) | 0.73 |
| LABEL cell type accuracy (hepatocytes) | 0.98 |
| LPS vs control DEGs across 37 tissue subregions | 5,143 |
| IRF1/STAT1 upregulated in ≥1.5× (broad cell types) | 57.3% (43/75) |

#### Biological Validation
- Macrophage accumulation in lung/liver/spleen/kidney after LPS: validated by F4/80 IHC
- Neutrophil increase in lung/spleen after LPS: validated by Ly6G IHC
- Thymocyte apoptosis in endotoxemia: validated by TUNEL
- STAT1/IRF1 KO mice: both abrogated body temperature drop after LPS; reversed ISG response in bulk RNA-seq

---

### Reproducibility

**Rating: 3.5/5**

**Strengths**:
- Code and data are publicly available: GitHub (chevrierlab/WMST-paper), Zenodo (preprocessed datasets), Code Ocean (LABEL capsule), GEO (GSE266246, GSE248904)
- Scripts are well-organized with clear naming conventions and step-by-step notebooks
- STARsolo + Scanpy pipeline is standard and reproducible
- LABEL pipeline is self-contained in notebooks with comments

**Limitations / Practical Notes**:
- **Cryomacrotome required**: Whole-mouse sectioning requires a Leica CM3600XP cryomacrotome, not standard equipment; limits broad replication
- **Manual H&E alignment**: Coordinate registration between Array-seq spots and H&E images was done manually in Adobe Illustrator — a subjective step that cannot be automated from the repository
- **CellKb is external**: The cell-type assignment is via the CellKb web service (not a Python package installable locally); the reference of 59M cells is not downloadable
- **UNI2-h checkpoint**: The UNI2-h model checkpoint (`vit_giant_patch14_224.dinov2.uni_mass100k`) requires a license from Hugging Face (gated access); not publicly downloadable without application
- **Hardcoded paths**: All Jupyter notebooks contain absolute paths (`/home/lbh/projects_dir/BigSlice/...`) that must be changed for any local reproduction
- **LABEL patch size ablation missing**: Paper claims comparison of 5 patch sizes (32/64/128/256/512px); only 128px code in repository
- **Environment not specified**: No conda/pip requirements file provided; users must infer dependencies from import statements

**To reproduce LABEL from scratch**:
1. Apply for UNI2-h access on HuggingFace
2. Extract H&E patches (128×128) centered on Array-seq spot coordinates
3. Run Vahadane normalization (torch-staintools library)
4. Run ViT-Giant feature extraction
5. Concatenate [spatial coords, features] → PCA(200) → KNN(k=5)

---

### Key Limitations (from paper)

1. Cryomacrotome not universally available; smaller (younger/smaller) animals can use standard cryomicrotomes
2. Array-seq does not achieve single-cell resolution; subcellular expansion techniques would improve this
3. LABEL trained only on female C57BL/6J mice in one sagittal plane; generalization to other strains/conditions is limited
4. ~600 genes/spot is relatively shallow compared to other spatial platforms; targeted approaches or higher sequencing depth would improve sensitivity

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
