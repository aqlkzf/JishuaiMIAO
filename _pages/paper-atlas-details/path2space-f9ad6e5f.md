---
layout: default
permalink: /paper-atlas/path2space-f9ad6e5f/
title: "Path2Space"
nav: false
description: "Path2Space 把乳腺癌 H&E 切片划成与 Visium spot 相当的局部区域，用预训练病理模型 CTransPath 提取每个区域的图像特征，再用一个简单 MLP 一次预测 14,068 个基因的空间表达。作者随后把这些“伪空间转录组”用于细胞比例估计、空间域聚类、预后分型和治疗反应预测。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Cell · 2026</span>
    </div>
    <h1>Path2Space</h1>
    <p>AI-predicted spatial transcriptomics unlocks breast cancer biomarkers from pathology</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2026.04.023" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Path2Space 中文方法解读：从常规 H&E 推断空间表达，再寻找空间生物标志物

### 1. 一句话抓住方法

Path2Space 把乳腺癌 H&E 切片划成与 Visium spot 相当的局部区域，用预训练病理模型 CTransPath 提取每个区域的图像特征，再用一个简单 MLP 一次预测 14,068 个基因的空间表达。作者随后把这些“伪空间转录组”用于细胞比例估计、空间域聚类、预后分型和治疗反应预测。

它真正的新意不仅是 H&E→基因表达回归，而是把可大规模获得的常规切片转成统一的空间表达坐标，使原本只能在少量昂贵 ST 样本上做的空间统计扩展到 TCGA、METABRIC 和多个治疗队列。

### 2. 训练数据和预测目标

核心训练集是 Bassiouni 等人的乳腺癌 10x Visium 队列，共 56,567 个图像—表达配对 spot。作者保留在每张训练切片至少 5% spots 中检测到的 14,068 个基因，并把目标定义为：

$$
y_{s,g}=\log_{10}(\operatorname{count}_{s,g}+1).
$$

这里没有先按 library size 转成 CPM。论文直接比较后发现 raw-count log 模型比 $\log_{10}(CPM+1)$ 模型预测出更多 PCC>0.4 的基因，并在细胞类型推断上更好。但这种目标仍可能携带总 RNA 量和细胞密度信号；作者因此另做 partial-correlation 分析，控制染色强度、癌细胞比例和总 RNA 后，大多数基因仍保持显著正相关。

### 3. 图像预处理：物理尺寸比像素数更重要

对每个真实 Visium spot，作者以其中心截取边长 80 μm 的正方形 tile。对没有 ST 的 WSI，则铺设同样物理大小的 pseudo-spots。不同扫描倍率下像素边长需要调整，不能简单把代码里的 224 pixels 当成永远等于 80 μm。

预处理包括：

1. 用 Sobel 梯度寻找有效组织；若超过 50% 像素的梯度幅度低于 0.15，则丢弃 tile；
2. 用 Macenko 方法做染色归一化；
3. 将保留 tile 送入 CTransPath。

本地 `1main_feature_extraction.py` 和 `func/utils_preprocessing.py` 提供这条入口。CTransPath 权重并未打包在当前精简工作区，且旧脚本含本机硬编码权重路径，复用时必须显式替换。

### 4. CTransPath + MLP：模型本身其实很直接

CTransPath 将每个 tile 编码为 768 维向量 $x_s$。随后 MLP 为：

$$
h_s=\operatorname{Dropout}_{0.2}(\operatorname{ReLU}(W_1x_s+b_1)),
$$

$$
\hat y_s=\operatorname{ReLU}(W_2h_s+b_2),
$$

其中维度为 $768\rightarrow768\rightarrow14{,}068$。训练用 MSE：

$$
L=\frac1{BG}\sum_{s,g}(\hat y_{s,g}-y_{s,g})^2.
$$

`model_MLP.py:46-78` 是这一定义的直接实现；`1main_regression.py` 使用 Adam、学习率 $10^{-4}$、batch size 32，并把输出层 bias 初始化为训练集中每个基因的均值。这一初始化有助于从合理的基因基线开始，但论文方法段未突出它。

输出端 ReLU 强制预测非负，与 $\log_{10}(count+1)\ge0$ 一致。模型并不显式读取相邻 spot，也没有图神经网络；空间关系主要在后处理平滑和下游空间统计中加入。

### 5. 为什么需要 154 个模型

作者采用严格的 leave-one-patient-out：

- 外层 22 次，每次把一个患者的全部切片作为测试集；
- 在其余患者中再做 7 个独立的训练—验证拆分；
- 每个验证拆分训练一个模型，用验证 PCC 早停；
- 对同一测试患者，把 7 个模型的预测平均。

因此共有 $22\times7=154$ 个模型。外部数据或临床队列使用全部 154 个模型平均。`TCGA_Prediction.py:72-135` 已实现对 outer/inner fold checkpoints 的双层循环与平均；训练仍需分别调用 `1main_regression.py` 产生每个 checkpoint。也就是说，发布代码有“加载并集成”的实现，但没有一个从原始数据自动调度 154 次训练的单命令流水线。

### 6. 空间平滑：性能数字必须连同评估协议一起读

预测完成后，每个 spot 与 200 μm 半径内邻居取平均，平均约 8 个邻居：

$$
\tilde y_{s,g}=\frac{1}{|N(s)|+1}\sum_{u\in N(s)\cup\{s\}}\hat y_{u,g}.
$$

空间平滑利用了邻近组织表达往往连续的先验，也会降低局部尖峰。论文 Figure 2 的主要数字对预测和实测表达都做平滑，得到中位 gene-wise PCC 0.38；未平滑预测为 0.20。Figure 3 的公平 benchmark 则用平滑预测对未平滑实测值，并同时报告未平滑 Path2Space。

因此，不能只引用“PCC=0.38”而省略平滑协议。平滑步骤主要出现在教程 notebook，而非核心训练脚本；需要坐标和邻域规则才能复现。

### 7. 从 predicted ST 到细胞类型

作者有两条路线：

1. 把 predicted ST 输入 SpaCET，利用参考 signature 无监督反卷积；
2. 用 PanopTILs 病理核标注作为监督，训练另一个 MLP 直接从 predicted gene expression 回归癌细胞、淋巴细胞和基质细胞比例。

第二条代码在 `2.Cell_type_fraction_model/2.1.main_cell_type_model.py`：先用 MinMaxScaler，在每个训练折内选 1,000 个基因，再训练三输出 `MLPRegressor`。论文写 `SelectKBest(f_classif)`，但当前代码明确用 `f_regression`；因为目标是连续比例，代码选择在统计类型上更自然，但仍是 paper-code discrepancy。

此外，当前脚本活动的超参数网格只有一个小模型 `(32,)`；论文使用的大网格被注释保留在 160–173 行。直接运行默认脚本不会复现论文的完整超参数搜索。

### 8. 从百万 pseudo-spots 到 SpatioTypes

对 1,096 张 TCGA 切片，Path2Space 生成约 670 万 pseudo-spots。作者没有直接跨患者聚类全部 spot，而是两阶段压缩：

1. 每张 slide 内用 SpaGCN 把相邻、表达相似的 pseudo-spots 合成空间 domain，得到 7,295 个 domain；
2. 对 domain 平均表达做 Seurat 联合聚类，得到跨患者一致的 11 个 ST clusters。

每位患者可表示为 11 维 cluster proportion 向量。再对该组成向量做层次聚类，作者得到三类 SpatioTypes：proliferation-enriched、immune-modulated、immune-inactive。Figure 5 显示 immune-inactive 组疾病无进展生存最差，并在 METABRIC 中验证。

这里的 SpaGCN、Seurat、ssGSEA、survival 分析大多不在精简 Python scripts 中；本地发布代码重点覆盖 ST 预测、细胞比例模型和 SPAND，而不是全部 Figure 5–7 的一键重算。

### 9. SPAND：方法概念与代码符号必须分开

论文把空间邻域多样性定义为：

$$
\operatorname{SPAND}(g)=\frac{-I(g)}{\operatorname{mean}(g)},
$$

其中 $I(g)$ 是基于 pseudo-spot 网格 rook 邻接的全局 Moran's I。Moran's I 越高，邻近位置越相似、空间越平滑；加负号后，SPAND 越高才对应越不规则、越异质。

举例：两个基因均值都是 2。若基因 A 的 Moran's I=0.8，则论文 SPAND=-0.4；若基因 B 的 Moran's I=-0.2，则 SPAND=0.1。B 的高低表达更交错，因此 SPAND 更高。

但本地 `scripts/3.SPAND/SPAND.py:81` 实际计算：

$$
\operatorname{score}_{\mathrm{code}}(g)=\frac{+I(g)}{\operatorname{mean}(g)},
$$

少了负号，会把排序方向反过来。复现论文“高 SPAND=高异质性”时必须取代码输出的负值，或修正公式；不能直接把脚本原输出用于论文方向的临床解释。

HER2 SPAND 也不是只对 ERBB2 单基因计算。论文先用 ErbB pathway 做 spot-level ssGSEA NES，再除以预测癌细胞比例，形成“每癌细胞 HER2 pathway activity”，最后计算 SPAND。这个完整变换未由单文件 `SPAND.py` 自动完成。

### 10. 结果应该如何解读

- Figure 2：在 Bassiouni CV 和三个外部 ST 队列中比较基因级 PCC；4,807 个基因在 CV 与外部均超过 PCC 0.4。
- Figure 3：与 16 个当前方法做 Visium benchmark；在 legacy ST benchmark 中 Path2Space 第二，与 EGNv2 无显著差异，因此“所有场景都第一”不成立。
- Figure 4：predicted ST 支持主要细胞类型推断，但 rare populations 的精度随丰度下降；论文承认这是 Visium 分辨率边界。
- Figure 5：SpatioTypes 是 predicted ST 经过空间域与跨患者聚类后的衍生分型，不是 MLP 直接输出。
- Figure 6：论文方向的 HER2 SPAND 在四个 trastuzumab 队列 AUC 为 0.69–0.83；这些是回顾性队列关联，尚不是前瞻性临床决策验证。
- Figure 7：11-cluster proportions 经 L1 logistic regression 预测治疗反应；combined trastuzumab model 只是 cluster score 与标准化 SPAND score 的平均。

### 11. 代码—论文对应

| 机制 | 本地证据 | 对应程度 |
|---|---|---|
| 80 μm tile、组织过滤、Macenko | feature extraction scripts | Partial：权重路径和完整输入不在本地 |
| CTransPath 768维特征 | bundled CTransPath model + preprocessing | Partial：模型定义在，预训练权重另取 |
| 768→768→14,068 MLP | `model_MLP.py:46-78` | Exact |
| Adam/MSE/输出 bias 初始化/早停 | `1main_regression.py`, `model_MLP.py` | Exact |
| 22×7 checkpoints 集成预测 | `TCGA_Prediction.py:72-135` | Exact for inference；训练需外部调度 |
| 200 μm 平滑 | paper Methods + tutorial notebook | Partial：不在核心脚本 |
| 三类细胞比例 MLP | `2.1.main_cell_type_model.py` | Partial：活动网格不是论文完整网格，`f_regression` 与论文不同 |
| SPAND Moran's I | `SPAND.py:27-84` | Partial：空间权重在，但缺论文负号 |
| SpatioType/响应完整分析 | paper Methods | Not found as完整本地流水线 |

### 12. 复现边界

- 源码来自 Zenodo record 14729337 / DOI `10.5281/zenodo.14729336`，不是 Git 仓库，因此没有 Git commit，`code_repo_commit` 保持 `null`。
- 本地 `.repo_source` 明确说明为节省空间排除了 `input_data.zip`（3.8 GB）和 `output_data.zip`（233 MB）；教程引用的样例输入输出因此不完整。
- CTransPath checkpoint 需另行下载，部分脚本有作者机器的绝对路径。
- 环境版本在 README/requirements 中较明确，但论文 key resources 的 PyTorch 2.4.1 与 README 的 2.4.0+cu121 略有差别。
- 工作区没有 154 个模型、全部临床图像、predicted ST 或下游 R/Python 结果，本轮没有重新训练或重算主图。
- 核心发布脚本可解释模型机制，但不足以一键复现全部 TCGA/METABRIC/治疗队列分析。
- SPAND 符号差异会改变结果方向，是实际复现前必须修正的最高优先级问题。

### 13. 左到右读完整流程

$$
\text{H\&E WSI}\rightarrow\text{80 μm tiles}\rightarrow\text{Macenko/QC}
\rightarrow\text{CTransPath}_{768}
$$

$$
\rightarrow\text{MLP}_{768\to768\to14068}
\rightarrow\text{154-model ensemble}
\rightarrow\text{200 μm smoothing}
\rightarrow\text{pseudo-ST}
$$

$$
\rightarrow
\begin{cases}
\text{cell-fraction model}\cr
\text{SpaGCN domains}\to11\text{ clusters}\to\text{SpatioTypes}\cr
\text{HER2 SPAND}\cr
\text{cluster proportions}\to\text{treatment response}
\end{cases}
$$

Path2Space 的价值是把 H&E 变成可做空间统计的代理表达图；其边界是代理信号依赖乳腺癌 Visium 训练、空间平滑显著影响指标，且发布 SPAND 脚本与论文定义存在符号反转。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Path2Space — Summary

### Motivation & Novelty

#### Biological Problem
Tumor spatial architecture — the arrangement of cancer cells, immune infiltrates, stromal components, and vascular niches within the tissue — profoundly shapes breast cancer outcomes and treatment response. Spatial transcriptomics (ST) assays such as 10× Visium reveal these molecular landscapes at 55μm resolution, enabling characterization of the tumor microenvironment (TME), identification of immune niches, and spatially resolved biomarker discovery.

#### Why Existing Methods Fall Short
ST assays cost $500–$2000 per sample, restricting analysis to small cohorts (typically <100 tumors) insufficient for biomarker discovery and validation. Prior computational methods for predicting spatial gene expression from H&E images were limited to tens to hundreds of highly variable genes (HVGs):
- **ST-Net** (*Nature Biomedical Engineering*, 2020): predicts ~250 HVGs with PCC ~0.15–0.20
- **BLEEP** (*NeurIPS*, 2023): contrastive bimodal learning, limited to HVG panel
- **HisToGene** (*bioRxiv*, 2021): transformer-based, HVG-limited
- **EGNv2** (*Pattern Recognition*, 2024): graph neural network approach, state-of-art before Path2Space
- **Benchmarking study** (*Nature Communications*, 2025; Wang et al.): comprehensive comparison of 11 methods on HVG panels, median PCC ≈ 0.2–0.35

None predicted whole-transcriptome spatial expression (14,000+ genes), precluding survival analysis, pathway scoring, deconvolution, or treatment response prediction in large cohorts.

#### Unique Contributions
1. **Whole-transcriptome spatial prediction**: 14,068 genes with median PCC 0.38 (smoothed), outperforming 21 methods
2. **Generalization from fresh-frozen to FFPE**: no significant performance drop despite training exclusively on FF slides
3. **SPAND metric**: novel spatial heterogeneity measure capturing local expression variability at 100×100μm scale, distinct from bulk HER2 measurements
4. **SpatioTypes**: three prognostic spatial breast cancer subgroups derived from cross-patient ST clustering with independent validation in METABRIC
5. **Treatment response prediction from H&E alone**: matches or outperforms costly bulk RNA-seq biomarkers across 7 cohorts

---

### Method Overview

Path2Space is a deep learning method predicting spatial gene expression from H&E histopathology slides through a two-component pipeline:

**Component 1 — ST Predictor**: For each tissue spot, a 224×224px (≈80μm) tile is extracted and color-normalized (Macenko method). The CTransPath foundation model (Swin Transformer, 768-dim output) encodes the tile into a feature vector. A multi-layer perceptron (768→768→14,068 with ReLU, 20% dropout, MSE loss) predicts log₁₀(count+1) normalized expression for all 14,068 genes simultaneously. A 154-model ensemble (22 outer × 7 inner leave-one-patient-out CV) is used; predictions are post-processed with 200μm spatial smoothing.

**Component 2 — Cell Type Inference**: Two approaches: (a) SpaCET unsupervised deconvolution applied to Path2Space-inferred expression using scRNA-seq references; (b) a supervised MLP trained on PanopTILs pathologist cell-type annotations (top-1000 genes by F-test, MinMaxScaler, 5-fold CV).

**Downstream analyses**:
- **SPAND**: spatial heterogeneity score (−Moran's I / mean) quantifying local expression variability
- **SpatioTypes**: SpaGCN within-slide domains → Seurat 11-cluster solution → Ward hierarchical clustering → 3 stable patient subgroups
- **Treatment response**: L1-regularized logistic regression on 11-cluster composition features

**Key biological assumptions**: H&E visual morphology (nuclear architecture, staining patterns, cellular composition) encodes sufficient information to infer spatial transcriptomics at Visium resolution. Spatial smoothing is justified by the diffuse capture physics of Visium spots (55μm diameter, neighboring spots overlap in tissue).

---

### Evaluation

#### Datasets
| Dataset | Role | n | Notes |
|---------|------|---|-------|
| Bassiouni et al. (GSE210616) | Training/CV | 22 patients, 56,567 spots | TNBC-enriched, Visium FF |
| HEST (MahmoodLab) | External validation | 4 patients, 5 slides | Multi-subtype |
| Martinez et al. (GSE213688) | External validation | 4 patients, 4 slides | |
| HTAN | External validation | 7 patients, 9 slides | Lower quality |
| PanopTILs | Cell type model training | 151 patients, 1,709 ROIs | TCGA H&E, pathologist annotations |
| TCGA-BRCA | SpatioType discovery | 976 patients (853 with survival) | 1,096 slides |
| METABRIC | SpatioType validation | 141 patients | Independent cohort |
| TransNEO | Treatment response CV | 61 trastuzumab, 93 chemo | |
| PBCP | Treatment response external | 18 trastuzumab, 19 chemo | |
| IMPRESS | Treatment response external | 62 trastuzumab, 64 chemo | |
| Cedars-Sinai | Treatment response external | 26 trastuzumab | |

#### Key Metrics
**ST prediction accuracy (median PCC, smoothed)**:
- Cross-validation (Bassiouni): 0.38 (0.20 unsmoothed)
- HEST: 0.40; Martinez et al.: 0.36; HTAN: 0.33
- Genes with PCC>0.4 (CV): 6,629; both CV and external: 4,807 "robust" genes

**Benchmarking (988 HVGs, unsmoothed predictions vs unsmoothed labels)**:
- Path2Space highest PCC in cross-validation and external validation (p<0.001 vs all 16 competitors)
- Smooth vs unsmooth: Path2Space achieves top rank in both configurations

**Cell type deconvolution (PanopTILs)**:
- SpaCET on Path2Space-inferred ST: AUC 0.85 (cancer), 0.80 (lymphocytes), 0.85 (stromal)
- Supervised MLP: AUC 0.88, 0.87, 0.85

**SpatioTypes**: Immune-inactive vs immune-modulated: HR=2.04 (p=0.002, Cox PH); METABRIC validation: p=0.01 log-rank, HR=5.45

**Treatment response**:
- Chemotherapy (TransNEO CV → PBCP external): AUC 0.75 → 0.89
- Trastuzumab combined model (TransNEO CV): AUC 0.86; PBCP: 0.90; IMPRESS: 0.74; Cedars-Sinai: 0.72
- HER2 SPAND alone: TransNEO 0.80, PBCP 0.69, IMPRESS 0.72, Cedars-Sinai 0.83
- Comparison: outperforms bulk RNA-seq-based Sammut-ML in PBCP external validation (0.90 vs 0.83 for trastuzumab)

---

### Reproducibility

**Rating: 3/5**

**Justification**: Code is available from Zenodo (non-commercial academic license) with tutorial notebooks and example data. Core MLP architecture is verifiable. However, critical components are absent or incomplete:
- The 154-model ensemble orchestration is not implemented in provided scripts
- Spatial smoothing implementation is not in standalone scripts (tutorial only)
- SpaGCN/Seurat clustering pipeline (R) not provided
- Treatment response logistic regression scripts not provided
- Manuscript hyperparameter grid for cell type model commented out
- CTransPath weights must be separately obtained from the TransPath GitHub
- Pretrained ST models (154 × .pth files) not provided (too large for Zenodo)

**Environment**: Python 3.10.8 with specific library versions (PyTorch 2.4.0+cu121, scikit-learn 1.3.0, SPAMS 2.6.5.4, libpysal 4.11.0). SPAMS may require compilation.

**Data access**: Most training data is publicly available (GEO, HEST Huggingface), but METABRIC requires EGA access, TransNEO/PBCP clinical data requires EGA access, and Cedars-Sinai data requires contacting lead author.

**Practical notes**:
- TCGA slides require GDC authentication and significant download bandwidth (~2TB for 1,096 slides)
- CTransPath inference on TCGA (~6.7M pseudo-spots) requires substantial GPU time
- The paper's reported models (154 trained) are not released; users would need to retrain from scratch

**Strengths**: Well-documented tutorial notebooks; clear module separation; standard PyTorch/scikit-learn stack
**Weaknesses**: Key analysis code (clustering, treatment response) not released; pretrained models not available; sign error in SPAND formula (code ≠ paper)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
