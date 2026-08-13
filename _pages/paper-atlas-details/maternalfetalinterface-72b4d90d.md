---
layout: default
permalink: /paper-atlas/maternalfetalinterface-72b4d90d/
title: "MaternalFetalInterface"
nav: false
description: "这项研究用同一细胞核的 RNA 与染色质可及性建立孕 5–39 周的母胎界面时间图谱，再用亚微米级 Stereo-seq 把第二孕期约 110 万个细胞放回组织空间。作者据此重建滋养层分化、螺旋动脉内皮重塑和蜕膜基质细胞状态，并发展 iScore 预测 EVT 侵袭深度，最后把妊娠并发症 GWAS 信号通过 SCAVENGE 投射到具体母源或胎源细胞。"
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
      <span>Nature · 2026</span>
    </div>
    <h1>MaternalFetalInterface</h1>
    <p>Single-cell spatiotemporal dissection of the human maternal-fetal interface</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-026-10316-x" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for MaternalFetalInterface">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/complexdisease/mf.interface" target="_blank" rel="noopener noreferrer" aria-label="Open code for MaternalFetalInterface">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 母胎界面图谱方法解读：把时间、空间、调控和遗传风险放到同一坐标系

### 一句话理解

这项研究用同一细胞核的 RNA 与染色质可及性建立孕 5–39 周的母胎界面时间图谱，再用亚微米级 Stereo-seq 把第二孕期约 110 万个细胞放回组织空间。作者据此重建滋养层分化、螺旋动脉内皮重塑和蜕膜基质细胞状态，并发展 iScore 预测 EVT 侵袭深度，最后把妊娠并发症 GWAS 信号通过 SCAVENGE 投射到具体母源或胎源细胞。

### 1. 为什么母胎界面必须同时看时间、来源和空间

母胎界面不是固定器官，而是随孕周快速变化的混合组织。胎儿来源的滋养层细胞进入母体蜕膜，重塑螺旋动脉；母体免疫和基质细胞既要允许有限侵袭，又要维持组织完整性。只做单一孕周的 scRNA-seq 会丢失时间变化，只做转录组难以看到调控元件，只做 dissociated cell 又会丢失“离界面或血管多远”这一关键变量。

研究因此建立四个相互补充的坐标：

- gestational age：孕 5–39 周的发育时间；
- maternal/fetal origin：每个细胞的遗传来源；
- RNA/ATAC state：表达状态和可及性调控状态；
- tissue coordinates：第二孕期切片中的真实位置、母胎界面和血管边界。

### 2. paired snRNA–snATAC 图谱

10x Multiome 同时测量一个细胞核的 RNA 和 ATAC。最终图谱包含 191,735 个核、19 类主要细胞，覆盖孕 5–39 周。图 1a 显示细胞组成随孕期显著变化：早孕期 VCT、EVT 和蜕膜相关细胞占比较高，后期 SCT 比例明显增加。

#### RNA 整合

`01_snRNA_integration.r` 使用 Seurat SCTransform 和 reciprocal PCA：每个样本先做方差稳定化，再以 `FindIntegrationAnchors(reduction="rpca")` 找跨样本对应状态，最后 `IntegrateData`。RPCA 的目标是对齐共享细胞状态，同时减少把罕见或孕周特异状态强行混合的风险。

RNA 质控包括约 1,000–50,000 UMI、检测基因数大于 400、线粒体比例低于 20%。notebook 还用 Scrublet 检测 doublet，其期望双细胞率随观测细胞数自适应调整。阈值是操作性质量门槛，不意味着界外细胞必然是技术伪影。

#### ATAC 整合

`02_snATAC_integrate.r` 使用 Signac：按样本调用 peaks，去除 blacklist，构建 TF-IDF/LSI 表示，再用 reciprocal LSI 把样本投射到共享空间。ATAC 质控包括片段数、TSS enrichment 和 nucleosome signal。RNA 与 ATAC 来自同一核，使细胞标签不必通过独立实验间接匹配，也能把某个基因表达变化连接到 promoter/enhancer accessibility。

### 3. 如何区分母体与胎儿细胞

母胎混合是本研究最容易产生系统性错误的环节。作者并行使用两类证据：

1. Souporcell 从单细胞测序 reads 聚类基因型，并与已知的滋养层胎源、DSC/淋巴内皮母源参考对应；
2. CopySCAT 从 ATAC 推断较大的拷贝数变化，帮助识别或过滤可能的异常细胞。

最终 182,773/191,735 个细胞获得来源标签。男性胎儿样本中，`UTY` 阳性细胞的 94.3% 被判为胎源，提供了独立验证。这个验证只适用于有 Y 染色体的妊娠；对女性胎儿，来源仍主要依赖基因型推断。

### 4. 从 ATAC 和 RNA 构建滋养层调控网络

滋养层从 villous cytotrophoblast（VCT）分叉形成 extravillous trophoblast（EVT）和 syncytiotrophoblast（SCT）。作者用 CellOracle 将开放染色质与表达结合：

1. 从 ATAC peaks 和 Cicero co-accessibility 建立候选 enhancer–promoter 联系；
2. 用 JASPAR2020 motif 扫描候选区域，生成 TF–target 先验边；
3. 在特定细胞群中用 Ridge regression 估计调控系数。

对目标基因 $g$，可写为

$$
y_g=\beta_{0g}+\sum_t X_t\beta_{tg}+\lambda\sum_t\beta_{tg}^2,
$$

其中 $X_t$ 表示候选 TF 的表达或调控特征，$\lambda$ 抑制共线 TF 造成的不稳定。本地 notebook 后续保留较强的边，例如 $|\beta|>0.1$。

结果识别 71 个 EVT 上调 TF 和 30 个 SCT 上调 TF。网络显示 EVT 程序中的 TF 倾向抑制 SCT 偏好基因，SCT 程序反向抑制 EVT 偏好基因，作者将其概括为 bistable toggle switch。这里“toggle”是由表达、开放染色质和回归网络支持的调控模型，并非逐条边都经过 perturbation 实验验证。

### 5. Stereo-seq：把细胞放回组织

16 个孕 20–24 周 basal plate 切片使用 Stereo-seq。原始 barcode 的物理间距约 0.5 μm，但分析单位不是单个 0.5 μm 点：SAW 和 Cellpose 先分割细胞，再把细胞边界内的分子聚合成 CellBin。最终获得约 110 万个空间细胞。

空间数据用 Stereopy/Scanpy 处理，以 Harmony 对批次、化学版本和染色策略进行校正。这里 Harmony 只用于空间数据；snMultiome 使用 RPCA/rLSI。混淆两条整合路线会误解代码。

作者用 cell community detection（CCD）识别组织 niche：以 300-pixel 滑动窗口计算局部细胞类型组成，再对窗口特征做 Leiden 聚类，最后由覆盖窗口投票给细胞赋予 community。得到 floating villi、villous core vessel、junction、maternal artery、D1 和 D2 六类空间社区。

### 6. 空间距离不是 UMAP 距离

母胎界面和螺旋动脉壁在 QuPath 中人工标注。对细胞坐标 $x_i$，到边界 $B$ 的最短欧氏距离为

$$
d_i=\operatorname{sign}(x_i,B)\min_{b\in B}\|x_i-b\|_2.
$$

到 maternal–fetal interface 的距离规定母侧为正、胎侧为负；到 vessel wall 的距离规定血管外为正、血管内为负。这个 signed distance 把不同形状切片转换为可比较的一维解剖轴。

图 2 的空间图显示 EVT 聚集于界面和螺旋动脉周围，免疫细胞也呈 niche 特异分布。空间共现统计使用 300 pixels 范围内的细胞对频率；它说明邻近，不直接等于配体–受体通讯。

### 7. 螺旋动脉内皮的四个重塑状态

经典 arterial endothelial cell（caEC）表达 PDE3A 和 VIM。随着 EVT 进入血管并替换内皮，作者在空间数据中识别 R0、R1 和 R2 状态，形成 caEC→R0→R1→R2 的顺序：R0 先丢失部分黏附/屏障程序，R1 更靠近侵入 EVT，R2 显示更强 apoptosis 相关表达和更完整的重塑表型。

`13_STOMICs_EC_Fig2.ipynb` 用 PDE3A 与 VIM 两个特征训练 multinomial logistic regression：

$$
P(y_i=k\mid x_i)=\frac{\exp(\alpha_k+\mathbf{w}_k^\top x_i)}{\sum_j\exp(\alpha_j+\mathbf{w}_j^\top x_i)},
\qquad x_i=(\mathrm{PDE3A}_i,\mathrm{VIM}_i).
$$

10 次 bootstrap AUROC 评估分类稳定性。CODEX 和免疫荧光进一步在独立样本的蛋白层验证 PDE3A/VIM 状态与 EVT 替换位置。四状态是转录/空间分类，不是对同一内皮细胞纵向追踪得到的真实时间序列。

### 8. EVT 轨迹与 iScore

作者用 CellRank 辅助确定初始状态，再用 Palantir 重建 VCT 向 EVT/SCT 的分叉。EVT 分支包括 proEVT、interstitial EVT、endovascular EVT 和其他成熟状态。伪时间表示细胞沿表达流形的相对位置，不等于真实孕周或单细胞被观测到的迁移路径。

#### iScore 的训练目标

空间中的 signed MFI distance 提供了 EVT 侵袭深度标签。为减轻单细胞稀疏性，作者把距离相近的 10 个 EVT 聚成 pseudobulk，在 3,192 个 EVT-enriched genes 上训练 LASSO：

$$
\hat{\boldsymbol\beta}
=\arg\min_{\boldsymbol\beta}
\left[\frac{1}{2n}\|\mathbf y-\mathbf X\boldsymbol\beta\|_2^2
+\alpha\|\boldsymbol\beta\|_1\right].
$$

notebook 使用 `Lasso(alpha=50)`，最终 54 个基因系数非零。预测值再标准化为 iScore：

$$
\mathrm{iScore}_i=\frac{\hat y_i-\overline{\hat y}}{s_{\hat y}}.
$$

高 iScore 表示转录状态更像深入母体侧的 EVT。训练和测试表达分别标准化，以降低信息泄露。模型在 held-out spatial EVT 上检验，并投射到 snRNA-seq；placenta accreta EVT 分数更高、smooth chorion EVT 更低，符合已知侵袭差异。

iScore 不是直接测量迁移速度，也不是普适病理诊断分数。它依赖本研究空间距离标签、基因 panel 和标准化方式，跨数据集比较必须复现相同预处理。

### 9. SCT 亚型和同步化结节

图 4 还把 SCT 分为不同状态。GPC5 高表达的 SCT-B preferentially 位于 syncytial aggregates/knots，并随孕周增加；RNAscope 和免疫染色支持其空间定位。因为 syncytium 是多核连续结构，snRNA 中的“细胞比例”实际是核状态比例，不能直接解释为独立细胞数。

### 10. DSC 路径与 DSC4 的内源性大麻素调节

蜕膜基质细胞从 ACTA2+ 未蜕膜化状态走向多个 DSC 状态。空间与单核数据共同识别靠近血管的 DSC3 和靠近 MFI/D1 niche 的 DSC4；DSC4 富集 `CNR1`、`SEMA3A`、`WNT5A` 等。

`15_DSC_analysis.ipynb` 以 Louvain resolution 0.1 细分 DSC3，并用 Squidpy `n_neighs=5` 寻找 DSC 邻近 EVT。控制侵袭深度后，靠近 DSC4 的 EVT iScore 仍显著较低，支持局部抑制假说，但仍属于空间关联。

功能实验将原代基质细胞体外 decidualize，并在第 5 天加入 0.5 μM methanandamide（mAEA，CB1 agonist）；单细胞分析显示 DSC4 样状态增加、apoptosis 程序下降。第 7 天条件培养基用于 trophoblast Transwell，mAEA 处理组显著降低侵袭。空间、体外状态和功能读出共同支持 CB1-dependent paracrine regulation，但未证明孕期大麻暴露与该实验剂量可直接等同。

### 11. CellChat：候选通讯网络

`16_cellchat.r` 按细胞类型聚合配体与受体表达，估计相互作用概率，并比较孕期或空间状态。该分析帮助提出 EVT、DSC、endothelium 与 immune cells 的通讯候选。CellChat 的概率来自表达数据库和群体统计，不是受体占有率或信号通量。论文/报告中 CellChat v2 与 reporting summary v1.6.1 的版本描述不完全一致，复现时应以实际代码环境为准。

### 12. SCAVENGE：从 GWAS 变异到细胞风险

GWAS 通常给出位点层面的关联，snATAC 则给出每个细胞的开放 peaks。SCAVENGE 的流程是：

1. 用 fine-mapped variant 权重和 peak accessibility 计算 gchromVAR z-score；
2. 取高分细胞作为 seeds；
3. 在 snATAC LSI 的 mutual kNN graph（$k=30$）上做 random walk with restart；
4. 得到每个细胞的 trait relevance score（TRS），再检验细胞类型富集。

传播可概括为

$$
\mathbf r^{(t+1)}=(1-\gamma)\mathbf W\mathbf r^{(t)}+\gamma\mathbf r^{(0)},
$$

代码设置 $\gamma=0.05$，并进行 1,000 次 permutation。网络传播让接近 seed 的染色质状态获得风险信号，同时也意味着结果依赖 LSI 图结构和 peak–variant 映射。

论文发现 fetal pre-eclampsia risk 最集中于 EVT，maternal pre-eclampsia risk 还涉及 DSC3、arterial endothelium 和 POU5F1+LGR5+ endometrial epithelium；后者也富集 preterm birth 和 miscarriage risk。这里的“风险细胞”表示遗传关联变异更可能作用于该细胞开放染色质，不等于这些细胞是疾病的唯一病因。

### 13. 本地代码覆盖与缺口

#### 直接或 notebook 可核对

- snRNA SCTransform/RPCA：`Analysis/01_snRNA_integration.r`
- snATAC Signac/rLSI：`Analysis/02_snATAC_integrate.r`
- Souporcell/CopySCAT：`Analysis/04–06`
- chromVAR、enhancer 和 coverage：`Analysis/07–09`
- CellOracle GRN：`Analysis/11_GRN_analysis_Fig1.ipynb`
- Stereo-seq、CCD、距离：`Analysis/12_STOMICs_preprocessing_Fig2.ipynb`
- endothelial classifier：`Analysis/13_STOMICs_EC_Fig2.ipynb`
- trophoblast trajectory/iScore：`Analysis/14_Trop_analysis_Fig4.ipynb`
- DSC4 邻域：`Analysis/15_DSC_analysis.ipynb`
- CellChat、SCAVENGE：`Analysis/16_cellchat.r`、`18_SCAVENGE_analysis.r`

#### 复现限制

- 多个核心步骤是带输出的 notebook，依赖未随仓库保存的大型对象和硬编码路径；
- SAW 是商业/受限工具，`17_SAW.sh` 只是简化入口；
- 缺少统一 environment lock 和完整随机种子记录；
- dbGaP 原始数据需要受控访问；
- CODEX、RNAscope、Transwell 等实验读出不能由计算仓库重建。

### 14. 阅读边界

1. 伪时间、endothelial state 和 iScore 是横截面细胞的推断顺序，不是同一细胞的连续录像。
2. CellOracle 边和 CellChat 交互是模型候选，不等于直接 perturbation 或蛋白结合证据。
3. signed distance 依赖人工边界标注；切片方向和组织形变会影响绝对距离。
4. DSC4 邻近与 EVT 低 iScore 的空间关联得到体外实验支持，但仍不能直接外推具体人群暴露风险。
5. SCAVENGE 定位的是遗传调控作用最可能发生的细胞状态，不是临床诊断或个体风险预测器。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary — MaternalFetalInterface

**Paper**: Single-cell spatiotemporal dissection of the human maternal-fetal interface
**DOI**: 10.1038/s41586-026-10316-x
**Journal**: Nature (2026)
**Type**: Atlas / datasource
**Code**: https://github.com/complexdisease/mf.interface

---

### Motivation & Novelty

The human maternal-fetal interface (MFI) is a transient mosaic of intermingled fetal and maternal cells that must simultaneously support placental invasion and maintain immune tolerance. Dysregulation at the MFI underlies major pregnancy complications (pre-eclampsia, preterm birth, miscarriage) that collectively affect millions of pregnancies worldwide and have poorly understood molecular etiologies.

**Limitations of existing approaches**:
- Prior single-cell studies (Vento-Tormo et al. *Nature* 563:347, 2018; Arutyunyan et al. *Nature* 616:143, 2023; Pique-Regi et al. *eLife* 8:e52004, 2019) were limited to narrow gestational windows (first trimester or term only), lacked paired ATAC-seq data, and used lower-resolution spatial methods
- No prior study generated a full-gestation (GW5–39) paired transcriptomic-epigenomic reference
- Submicrometre spatial transcriptomics was not previously applied to the human MFI; prior spatially resolved studies (Greenbaum et al. *Nature* 619:595, 2023) used lower-resolution technologies
- Genetic risk GWAS variants had not been systematically linked to specific MFI cell types at single-cell resolution

**Unique contributions**:
1. **Comprehensive gestational atlas**: 191,735 paired snRNA+ATAC nuclei from GW5 to GW39 — the most complete temporal coverage of the human MFI
2. **Submicrometre spatial transcriptomics**: 16 second-trimester basal plate sections with Stereo-seq at 0.5-μm resolution (~1.1M cells), enabling single-cell resolution across entire 1 cm² tissue sections
3. **Novel cell state discoveries**: Four arterial endothelial states (caEC→R0→R1→R2), novel SCT-B syncytial knot subtype, and novel DSC4 CB1+ decidual stromal subtype
4. **Quantitative EVT invasiveness model**: LASSO-based iScore from spatial transcriptome (54 genes) predicts single-cell invasion depth with Spearman correlation validated on independent datasets
5. **Endocannabinoid regulation of invasion**: First demonstration that DSC4 cells mediate CB1-dependent paracrine suppression of EVT invasion — with direct public health implications for cannabis use in pregnancy
6. **GWAS-to-cell-type mapping**: SCAVENGE integration identifies EVTs (fetal) and POU5F1+LGR5+ endometrial epithelium (maternal) as convergent vulnerable populations across three pregnancy complications

---

### Method Overview

The study integrates four complementary technologies across matched tissue samples:

**snRNA-seq + snATAC-seq** (paired 10x Chromium Multiome): Seurat v4 SCTransform + rpca integration for transcriptomics; Signac reciprocal LSI for chromatin accessibility. CellOracle reconstructs GRNs by integrating ATAC open chromatin with RNA expression via Ridge regression over FANTOM5 enhancer-linked TF binding sites. CellRank + Palantir reconstruct developmental trajectories.

**Stereo-seq spatial transcriptomics**: SAW v8.1 pipeline processes raw FASTQ at 0.5-μm bin resolution → deep learning cell segmentation → CellBin aggregation. Harmony corrects batch effects across 16 samples. CCD algorithm (sliding 300-pixel windows + Leiden clustering) identifies 6 recurrent spatial niches. Spatial distances to MFI and vessel walls computed in QuPath-annotated coordinate systems.

**Machine learning innovations**:
- *Endothelial state classifier*: Multinomial logistic regression on PDE3A and VIM achieves high AUROC for classifying caEC/R0/R1/R2 states
- *iScore*: LASSO regression trained on pseudobulked EVTs (10 cells/depth bin), using MFI distance as target, selects 54 of 3,192 EVT-enriched genes

**SCAVENGE GWAS integration**: gchromVAR z-scores (GWAS posterior probabilities × ATAC peak accessibility) → random walk propagation (γ=0.05) on mutual kNN graph from LSI embedding → per-cell TRS → Fisher's exact test for cell-type enrichment.

---

### Evaluation

#### Datasets
- **snMultiome**: 28 samples (191,735 nuclei), GW5–39, Stanford + UCSF biobanks
- **Stereo-seq**: 16 samples (GW20–24), ~1.1M cells, 62 vessels annotated
- **CODEX**: 3 samples (GW15.2, 19.0, 22.1), 9-antibody panel
- **In vitro**: 33,088 HuF-derived DSCs (13,493 control, 19,595 mAEA)
- **External validation** (iScore): GSE198373 (smooth chorion EVTs), GSE212505 (placenta accreta EVTs)
- **GWAS**: 4 datasets — pre-eclampsia (maternal n=10,255, fetal n=7,259), PTB (n=3,331 + replication n=233,290), miscarriage (n=49,996)

#### Key results
- **Atlas coverage**: 19 cell types with concordant RNA/ATAC annotations; 182,773/191,735 cells (>95%) maternal/fetal assigned
- **Toggle switch**: 71 EVT-upregulated TFs and 30 SCT-upregulated TFs; reciprocal suppression pattern confirmed genome-wide
- **Endothelial states**: caEC→R0→R1→R2 progression with increasing vessel-wall detachment distance (Wilcoxon p<0.001); apoptosis genes enriched in R2; CODEX protein validation in 3 independent samples
- **iScore performance**: Spearman correlation significant in held-out test set (n=63,916 EVTs, 16 samples); reduced iScore in smooth chorion EVTs; elevated in placenta accreta EVTs
- **DSC4 regulation**: EVTs within 5 grid tiles of DSC4 have significantly lower iScores than depth-matched EVTs (P=3.8×10⁻¹⁴²); mAEA conditioned medium reduces CTB invasion (P=3.7×10⁻⁵, n=6 placentas)
- **GWAS risk**: iEVTs show strongest fetal pre-eclampsia enrichment (FDR≤2.2×10⁻⁹⁶); DSC3 + arterial endothelium + POU5F1+LGR5+ epithelium enriched for maternal pre-eclampsia risk; shared POU5F1+LGR5+ endometrial epithelium enrichment for PTB and miscarriage replicated in independent cohort (n=233,290)
- **Biological validation**: CODEX independently confirms protein-level cell state identities; RNAscope confirms GPC5+ SCT-B in syncytial knots; immunofluorescence confirms DSC3/DSC4 spatial localization

---

### Reproducibility

**Rating: 3/5**

**Justification**: The code repository is well-structured (18 scripts/notebooks covering all major analyses) and the methods are described in detail in both the main paper and supplementary. However, several barriers to full reproduction exist:
- Raw data access is controlled (dbGaP accession phs004305.v1 requires Data Access Committee approval)
- Many core analyses are in Jupyter notebooks (⚠ Notebook) rather than standalone reproducible scripts; exact computational environments are not captured in a reproducibility manifest (no `environment.yml`, `requirements.txt`, or `renv.lock`)
- STOmics SAW pipeline is commercial software with restricted distribution
- Code paths are hardcoded to private servers (`/path/to/...`, `/tank/data2/cw/...`) and must be adapted for reuse
- iScore training notebook would need to be run from scratch to reproduce exact 54-gene selection (reproducible with seed-setting, but no explicit seeds documented)

**Strengths**: All major analysis scripts are present; supplementary notes describe Stereo-seq protocol in extensive detail; GWAS datasets are publicly downloadable; external validation datasets (GSE198373, GSE212505) are open access; COSMOS data explorer at https://cell.ucsf.edu/snPlacenta/ provides interactive access to processed data.

**Practical environment setup**:
```
R packages: Seurat v4, Signac, chromVAR, SCAVENGE, CellChat v2, BuenColors
Python: stereopy v1.6.1, scanpy, palantir v1.1.0, cellrank v1.5.1, squidpy, scikit-learn v1.4.2, harmony-pytorch
External tools: STOmics SAW v8.1, Cell Ranger ARC v2.0.0, MACS2 v2.2.7
```

**Common pitfalls**:
- Souporcell requires pre-specification of expected number of genotypes per sample (may need tuning per sample batch)
- Stereo-seq CellBin resolution depends on deep learning segmentation quality — samples with poor DAPI staining or high cell density may undersegment
- SCAVENGE is sensitive to the GWAS reference genome version; all GWAS bed files must be lifted to hg38 before running
- CellOracle GRN quality depends on Cicero co-accessibility, which needs sufficient cells per lineage (recommend >1,000 per major cell type)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
