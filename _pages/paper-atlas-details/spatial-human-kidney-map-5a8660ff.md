---
layout: default
permalink: /paper-atlas/spatial-human-kidney-map-5a8660ff/
title: "Spatial-Human-Kidney-Map"
nav: false
description: "这项工作不只是在肾组织里“数细胞”，而是要回答三个递进问题：健康与糖尿病肾病（DKD）的组织结构如何改变；哪些局部细胞组合与肾功能下降相连；能否从这些局部结构中找到具有临床风险意义的患者亚群。作者整合 48 份 CosMx 和 16 份 Xenium FFPE 样本，并以 150 位患者的单核 RNA 测序图谱作为参考，最终形成覆盖 200 多位患者、超过 500 万个细胞的统一图谱（论文 Results “Spatial atlas…"
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
      <span>Nature · 2026</span>
    </div>
    <h1>Spatial-Human-Kidney-Map</h1>
    <p>Spatial atlas of diabetic kidney disease reveals a B cell-rich subgroup</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-026-10363-4" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 糖尿病肾病空间图谱：从跨平台整合到 B 细胞富集亚群

### 论文要解决什么问题

这项工作不只是在肾组织里“数细胞”，而是要回答三个递进问题：健康与糖尿病肾病（DKD）的组织结构如何改变；哪些局部细胞组合与肾功能下降相连；能否从这些局部结构中找到具有临床风险意义的患者亚群。作者整合 48 份 CosMx 和 16 份 Xenium FFPE 样本，并以 150 位患者的单核 RNA 测序图谱作为参考，最终形成覆盖 200 多位患者、超过 500 万个细胞的统一图谱（论文 Results “Spatial atlas of DKD”）。

论文的主线可以概括为：跨平台统一细胞状态 → 用多尺度邻域定义组织 niche → 在损伤小管和免疫细胞内部继续细分 microenvironment → 提取空间基因签名 → 在独立 bulk RNA 和血浆蛋白队列中验证疾病进展风险。

### 1. 跨平台整合与细胞类型转移

CosMx、Xenium 和 snRNA-seq 的基因面板、技术噪声和样本组成不同，不能直接拼接。作者先用 scVI 学习负二项观测模型下的低维潜变量，再以 scANVI 利用参考标签做半监督细胞类型转移。主图谱使用 4 个隐藏层和 30 维潜空间；免疫图谱沿用 4 层、30 维，B 细胞图谱则使用 3 层、30 维（论文 Methods “Integration and imputation”“Immune atlas generation”“B cell atlas generation”）。

标签不是一次性硬赋值。免疫和 B 细胞子图谱会在潜空间中找邻居，并按 50%、70%、90% 的置信阈值逐轮纳入更可靠的预测，从而避免低置信细胞立即污染参考集合。这个设计的重要含义是：细胞类型来自“表达状态与参考图谱的一致性”，并不等同于单个 marker 阳性。

空间面板缺失的基因由 snRNA 参考补齐。对空间细胞 $i$ 和参考邻居 $j$，代码使用逆平方距离权重：

$$
\hat{x}_{ig}=\frac{\sum_{j\in N(i)}(d_{ij}+\epsilon)^{-2}x_{jg}}
{\sum_{j\in N(i)}(d_{ij}+\epsilon)^{-2}},\qquad \epsilon=3\times10^{-8}.
$$

直接代码证据位于 `Final_Combined_Integration_Script4_Imputation.py:27-30,53-61,100-102`。这里有两个不能抹平的实现差异：论文写 10 个近邻，本地代码使用 15 个；代码还把小于 0.01 的插补值置零（同文件 `:129`），论文 Methods 未报告这一步。因此，插补表达适合做群体层面的信号发现，不应被解释为单细胞中真实测得的转录本。

### 2. 多尺度邻域如何变成 11 类组织 niche

作者不是只看最近邻，而是分别统计每个细胞周围 20、40、60、80 μm 内各种细胞类型的数量。代码随后用累积圆盘相减得到 20–40、40–60、60–80 μm 的环带：`Niche_Analysis_Script2_Neighbor_Dataframe.py:118-120`；各尺度再按邻居总数归一化（`:147-150`）。因此，一个细胞的特征同时编码“附近是什么细胞”和“这些细胞离中心多远”。

80 μm 邻域总数最低的 5% 被过滤（`:134-136`），多尺度特征经标准化和 25 维 PCA 后进入 MiniBatchKMeans。代码实际以 $k=17$ 生成原始簇（`Niche_Analysis_Script3_Kmeans.py:86-109`），论文报告的 11 个 niche 来自结合组织学位置和标志细胞后的人工合并与命名。这里不能把 11 类说成纯粹由某个自动指标唯一决定；它是计算聚类与生物学注释共同形成的结果。

论文用两条独立路线检查这些 niche 不是任意分组。COVET 比较邻域中的表达协方差结构，Hotspot 再在二维 COVET UMAP 上计算局部基因共变；代码设置 Bernoulli 模型、300 个邻居和 FDR<0.05（`F COVET/COVET_Script3_Hotspot.py:56-70`）。NicheCompass 则把空间邻接图和先验基因程序送入 GATv2 图网络，检验相同空间区室能否由另一种建模假设恢复。两者是交叉验证，不是生成主 niche 标签的必经步骤。

### 3. 从组织 niche 进入疾病相关 microenvironment

11 类 niche 描述肾组织的大尺度区室。作者随后把问题收窄到损伤小管周围，得到五类 injured tubular microenvironment。最关键的 profibrotic microenvironment 在 DKD 中扩张，与 eGFR 呈负相关（论文报告 $r=-0.60$），并富集纤维化、细胞外基质和炎症信号。CellPhoneDB 用插补表达推断配体–受体组合：本地脚本明确设置 1,000 次迭代、表达阈值 0.01、随机种子 42 和 $P<0.05$（`I Immune_Microenvironments/Immune_ME_Script5_cellphoneDB.py:77-98`）。

这些结果应读成“候选通信轴”：配体和受体在空间邻近的细胞群中共同出现，并且部分相互作用强度与 eGFR 相关；它们并不直接证明分子结合、信号方向或因果效应。真正的机制验证仍需扰动实验。

### 4. 免疫图谱与 B 细胞富集亚群

免疫子图谱分出 11 类免疫细胞，并围绕免疫细胞再次计算局部组成，形成成纤维、驻留、T 细胞优势、血管、肾小球、损伤小管和 B 细胞优势等七类免疫 microenvironment。B 细胞优势区域嵌在 profibrotic tubular niche 中，而不是均匀散布在肾脏。

论文用多层证据支持该区域具有 TLS-like 特征：空间上出现 CXCL13–CXCR5；CD4 T 细胞表达 CXCR5、PDCD1，符合 T_FH-like 状态；TNFSF13B–TNFRSF13C 指向 B 细胞存活；IMC 在邻近切片中确认 CD20+ B 细胞和 CD4+ T 细胞；Xenium 检测到 AICDA 和 IRF4。进一步与单细胞参考整合后，B 细胞包含 naive、memory 和 atypical memory 状态，其中 IgD+ naive B 细胞显著富集。

“TLS-like”是恰当边界：这些空间、转录和蛋白证据共同支持局部 B/T 细胞组织化与活化，但并未等同于完整证明了成熟三级淋巴结构的所有组织学构件。

### 5. 从空间发现到患者分层

作者按样本和 niche 汇总原始计数，以 DESeq2 做 pseudobulk 差异分析，并定义

$$
\pi=\operatorname{sign}(\log_2 FC)\times[-\log_{10}(P_{adj})].
$$

本地实现可见 `Niche_Analysis_Script8_spatial_genesignature.py:51-77`。每个 niche 的高排名基因构成空间签名；B 细胞优势签名被投射到 843 个肾组织 bulk RNA 样本，B+ DKD 占 TRIDENT 队列的 8.4%，并显示更快到达肾衰终点。IgA 免疫沉淀质谱还观察到补体与免疫效应蛋白富集。

随后作者在 TRIDENT 血浆蛋白组上用 SMOTE、五折交叉验证和 elastic-net logistic regression 选出 14 个蛋白，并在 3,309 位糖尿病 UK Biobank 参与者中外部验证；论文报告其 AUC 0.70，高于 kidney failure risk equation 的 0.63。需要明确的是，本地仓库没有 TRIDENT 弹性网或 UK Biobank 分析代码；这两段只能由论文文字和图表支持，不能宣称已由本地代码复现。

### 6. 主图的阅读顺序

- Fig. 1：样本、平台与统一细胞图谱，是后续所有空间比较的输入层。
- Fig. 2：20–80 μm 多尺度邻域与 11 类 niche，展示组织结构在 DKD 中如何重排。
- Fig. 3：损伤小管 microenvironment，聚焦 profibrotic 区域及其与 eGFR、纤维化和通信轴的关系。
- Fig. 4：免疫图谱和七类免疫 microenvironment，把 B 细胞优势区域定位到损伤组织背景中。
- Fig. 5：IMC、B 细胞亚型、空间签名、患者结局和血浆蛋白模型，完成从局部空间现象到临床分层的证据链。

### 7. 这项方法能说明什么、不能说明什么

最强结论是：跨平台空间图谱一致地识别到 DKD 中扩张的损伤与免疫区室；其中存在一个嵌于 profibrotic niche 的 B 细胞富集患者亚群，其组织签名与纤维化和较差结局相关，并在独立蛋白队列中显示预测价值。

仍需保留三层不确定性。第一，空间样本与临床结局主要是观察性关联，不能推出 B 细胞聚集导致肾衰。第二，插补基因和 CellPhoneDB 相互作用是模型推断，不是直接分子测量。第三，代码与论文在插补邻居数、17 个原始簇到 11 个最终 niche 的整理，以及外部临床分析可得性上存在明确边界。复现时应把“本地代码可追踪”“论文报告但代码缺失”“生物学解释”分开陈述。

### 源证据入口

- 论文：`paper source/paper/paper.md`
- 主图：`paper source/paper/_page_1_Figure_1.jpeg` 至 `_page_9_Figure_1.jpeg`
- 代码：`Spatial-Human-Kidney-Map-code/`
- 逐项论文—代码对应与缺失边界：`doc_code.md`
- 图证据：`figure_analysis.md`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## summary.md — Spatial-Human-Kidney-Map

### Motivation & Novelty

**Biological problem**: Diabetic kidney disease (DKD) is the leading cause of end-stage renal failure and affects ~40% of diabetic patients. Despite recent therapeutic advances (SGLT2 inhibitors, mineralocorticoid receptor antagonists), many patients still progress rapidly to dialysis. A core obstacle is heterogeneity: DKD ranges from slow decline to rapid deterioration, and the mechanisms driving aggressive progression are poorly understood. Existing risk models using clinical features (eGFR, albuminuria) and genetic scores provide limited stratification power. The cellular and spatial context of renal inflammation — which cell types are present, where, and in what arrangements — remains uncharted at population scale.

**Limitations of existing approaches**:
- **Spot-level spatial transcriptomics** (Visium, SlideSeq): 10–55 µm spots contain multiple cells, preventing single-cell resolution of tissue architecture. (*10x Genomics Visium*; various publications 2019–2022)
- **Prior single-cell spatial kidney studies**: limited to small cohorts (n <30 samples) or restricted gene panels. Lake et al., *Nature*, 2023; Abedini et al., *Nature Genetics*, 2024 profiled injury states but lacked the scale for immune microenvironment characterization or clinical stratification.
- **snRNA-seq atlases**: lose spatial information entirely; cannot directly map immune aggregates or tissue niches.
- **Circulating biomarkers** (TNF receptors 1/2; Niewczas et al., *Nature Medicine*, 2019): predict renal decline but are biologically agnostic — they cannot identify the specific immune pathway driving disease.

**Unique contributions**:
1. **Largest single-cell spatial kidney atlas**: 64 FFPE samples, two platforms (CosMx 1k + Xenium 5k), integrated with 150-sample snRNA-seq reference — >5 million cells from >200 patients.
2. **Computational atlas framework**: multi-scale neighborhood profiling (20–80 µm) enabling niche and microenvironment identification at population scale.
3. **Discovery of B cell-predominant TLS-like microenvironment** in DKD: first characterization of a tertiary lymphoid structure-like niche in diabetic kidney disease, defining a new disease subtype.
4. **Translational pipeline**: spatial tissue signature → plasma proteomics panel → population biobank validation, demonstrating AUC 0.70 vs. 0.63 for the kidney failure risk equation in UK Biobank.

---

### Method Overview

The study implements a sequential computational pipeline:

**1. Multi-platform integration**: CosMx and Xenium spatial transcriptomics data are independently integrated with a 720K-cell snRNA-seq reference using scVI/scANVI (variational autoencoder with semi-supervised cell-type transfer). A 30-dimensional latent space captures transcriptional identity while correcting platform and sample batch effects. This enables unified cell-type annotation across 5M+ cells.

**2. Expression imputation**: The limited spatial gene panels (1,000–5,100 genes) are extended to 3,000 HVGs using inverse-distance weighted averaging from the nearest 15 snRNA-seq reference cells in the scANVI latent space. This enables pathway-level analysis of spatial data.

**3. Niche identification**: Each cell's spatial context is encoded as a multi-scale neighborhood composition vector (20/40/60/80 µm radius, 20 cell types, shell-difference features). PCA + MiniBatchKMeans identifies 11 recurring cellular neighborhoods (niches) validated by two orthogonal approaches: COVET (covariance-based niche distances via approximate optimal transport) and NicheCompass (GATv2Conv-based GNN).

**4. Microenvironment analysis**: The same neighborhood-profiling framework is applied to subsets (injured tubular cells; immune cells) to reveal 5 tubular microenvironments and 7 immune microenvironments, respectively. Differential expression (Wilcoxon, imputed expression) and ligand-receptor analysis (CellPhoneDB v5) characterize each.

**5. Biomarker pipeline**: DESeq2 pseudobulk analysis produces spatial gene signatures (top 10 genes by π-score per niche). The B cell-predominant microenvironment signature is applied to bulk RNA-seq and plasma proteomics to build tissue and circulating biomarkers, validated in UK Biobank.

**Key biological assumptions**: FFPE tissue preserves spatial architecture; scANVI can accurately transfer cell-type labels from nucleus-level to full-cell spatial data despite technical differences; the 20–80 µm scale captures biologically relevant cell-cell communication distances in kidney.

---

### Evaluation

#### Datasets

| Dataset | Type | Size | Purpose |
|---------|------|------|---------|
| TRIDENT cohort (spatial) | CosMx 1k + Xenium 5k | 64 FFPE samples, 58 patients | Main spatial discovery |
| TRIDENT cohort (snRNA-seq) | snRNA-seq reference | 150 patients, 720K cells | Integration reference |
| TRIDENT cohort (bulk RNA-seq) | Bulk RNA-seq | 843 kidney samples | Biomarker validation |
| TRIDENT cohort (proteomics) | Plasma proteomics | 248 patients (B+: n=17, B−: n=231) | Elastic-net model training |
| UK Biobank | Plasma proteomics (Olink) | 3,309 participants with diabetes | External biomarker validation |
| Susztaklab Biobank | Tissue + IgA pull-down MS | 18 samples (9 control, 9 B+) | Immune complex characterization |

#### Key Quantitative Results

**Integration benchmarking**: scANVI outperforms Harmony, Scanorama, Pyliger by SCIB overall score (combination of batch correction and bio-conservation metrics; Extended Data Fig. 1b).

**Niche-GFR correlations** (Pearson, two-sided):
- DCT niche r = 0.61 (P = 7.4×10⁻⁷)
- Immune niche r = −0.59 (P = 1.4×10⁻⁶)
- PT niche r = 0.52 (P = 1.7×10⁻⁵)
- iPT niche r = −0.55 (P = 4.1×10⁻⁶)

**Profibrotic microenvironment**: r = −0.6 with eGFR (P = 3×10⁻⁷); expanded 2–3× in DKD vs. controls; Sirius Red staining validates COL1A1 co-localization.

**B cell enrichment in DKD**: Plasma cells 3.1× higher; B cells 2.4× higher vs. controls. B cell-predominant niche enriched for IgD⁺ naive B cells (P = 2.38×10⁻¹¹).

**B+ DKD subgroup** (TRIDENT, n=248): 8.4% of patients (n=17) classified B+. Kaplan-Meier shows faster progression to dialysis, transplantation, or ≥40% eGFR decline (log-rank P=0.02).

**Plasma biomarker panel**: 14-protein elastic-net model (TRIDENT training); C-statistic improvement over clinical-only model (1,000 bootstraps).

**UK Biobank validation**: time-dependent AUC 0.70 vs. 0.63 (kidney failure risk equation); top quartile B+ protein score = substantially higher progression risk.

**Ligand-receptor findings**:
- HBEGF→EGFR (iPT→fibroblast): r>0 with HAVCR1 (P = 4.7×10⁻¹⁸)
- JAG2→NOTCH2: r>0 with COL1A1 (P = 5.9×10⁻¹¹)
- NRG1-ERBB3 (glomerular): r>0 with eGFR (P = 0.005)
- PLAU-PLAUR (glomerular): r<0 with eGFR (P = 0.014)

---

### Reproducibility: 3/5

**Strengths**:
- Full code deposited on GitHub (11 workflow directories, sequential numbered scripts)
- Docker containers specified for each analysis step (5 containers)
- Spatial data, processed snRNA-seq, and B cell atlas data deposited on Zenodo
- Supplementary tables provide marker genes, DEGs, clinical metadata
- Cross-platform replication (CosMx + Xenium) for key findings
- UK Biobank external validation provides independent clinical confirmation

**Weaknesses**:
- Clinical biomarker analysis (elastic-net, TRIDENT proteomics, UK Biobank tAUC) is NOT in the GitHub repository — missing from reproducibility package
- Hardcoded paths in all scripts (`/home/bcd/revision_nature/...`, `/home/liranmao/katalin/...`) — cannot run as-is without path modification
- k=17 for KMeans (code) vs. 11 niches (paper) requires undocumented manual annotation step
- k=15 for imputation (code) vs. k=10 stated in Methods — inconsistency
- Some scripts depend on Google Colab (DESeq2, SCIB benchmarking) with no standalone alternative
- No environment.yml or requirements.txt — dependency version reconstruction requires reading all Docker container definitions
- Raw spatial data (Zenodo) not yet publicly available at the time of publication (tokenized URL in the paper)

**Practical notes**:
- Requires GPU for scVI/scANVI training (Docker `10jll/scvi_cuda12:version4`)
- Imputation of 3.4M cells requires ~40 GB RAM — implement in chunks as the code does
- Manual niche annotation step (D/Script4) requires biological expertise to map 17 raw clusters to 11 niches; no ground truth labels provided
- Contact: ksusztak@pennmedicine.upenn.edu; TRIDENT data requests via consortium

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
