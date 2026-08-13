---
layout: default
permalink: /paper-atlas/spatialex-43739a01/
title: "SpatialEx"
nav: false
description: "高参数空间多组学常遇到一个实验限制：相邻组织切片可以来自同一组织块，却只测了不同分子面板或不同模态。例如切片 1 测 panel A，切片 2 测 panel B；若把细胞×分子矩阵排成表格，已测值只落在对角块，其余两块缺失。直接用坐标配准仍不能得到同一个细胞的完整分子谱，因为连续切片不是完全相同的细胞集合。 SpatialEx 的入口是一个更稳定的共同视图：两张切片都有 H&E 形态图像。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>SpatialEx</h1>
    <p>High-parameter spatial multi-omics through histology-anchored integration</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02926-6" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SpatialEx">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/KEAML-JLU/SpatialEx" target="_blank" rel="noopener noreferrer" aria-label="Open code for SpatialEx">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpatialEx / SpatialEx+：用组织学作为连续切片的共同锚点

### 先理解“对角整合”是什么

高参数空间多组学常遇到一个实验限制：相邻组织切片可以来自同一组织块，却只测了不同分子面板或不同模态。例如切片 1 测 panel A，切片 2 测 panel B；若把细胞×分子矩阵排成表格，已测值只落在对角块，其余两块缺失。直接用坐标配准仍不能得到同一个细胞的完整分子谱，因为连续切片不是完全相同的细胞集合。

SpatialEx 的入口是一个更稳定的共同视图：两张切片都有 H&E 形态图像。基础 SpatialEx 学习“形态+空间邻域 → 一个 omics 面板”；SpatialEx+ 再把两个这样的预测器与双向 omics-cycle 映射器联合训练，补齐缺失块。最终每张切片都同时拥有实测面板和预测面板，可用于扩大基因 panel，或形成转录—蛋白、转录—代谢的空间多组学矩阵。论文概览与 Fig. 1 见 `paper source/paper/auto/paper.md` 的 SpatialEx/SpatialEx+ 结果段和 Methods `paper.md:242-296`。

### 从 H&E 到每个细胞的图像特征

流程先做细胞核分割并以每个细胞为中心裁剪图像 patch。预训练病理基础模型 UNI 把 patch 编码成固定长度 H&E embedding；论文明确训练 SpatialEx 时冻结该图像模型（`paper.md:308-310`）。本地 `SpatialEx/utils.py:create_ImageEncoder` 也设置 `frozen=True`，但模型权重路径硬编码为作者机器目录，因此仓库不能开箱即用地重建图像特征，用户需要自行取得合法权重并修改路径。

这里的关键假设是：连续切片中的相似细胞形态与微环境包含可迁移的分子线索。它不是说 H&E 唯一决定表达；炎症状态、低丰度转录本和代谢物可能没有足够形态信号，所以预测仍是条件期望而非实测替代品。

### 为什么使用超图而不是普通邻接图

普通图的一条边只连接两个细胞；SpatialEx 以一个中心细胞和其 $k=7$ 个空间近邻组成一个 hyperedge，表示局部微环境。论文把传播写成 node→hyperedge→node 两步。代码在预处理阶段把它合成归一化传播矩阵：

$$
\widetilde H=D_V^{-1/2}HWD_E^{-1}H^TD_V^{-1/2},
$$

其中 $H$ 是细胞—超边关联矩阵，$W$ 的边权均为 1。`SpatialEx/preprocess.py:512-521` 预先计算该矩阵；HGNN 层随后执行

$$
X^{(l+1)}=\widetilde H X^{(l)}\Theta^{(l)},
$$

当前实现见 `SpatialEx/model.py:8-51`。所以论文的两阶段信息传递与代码的一次稀疏矩阵乘法是数学折叠关系，而不是代码漏掉了其中一步。默认两层 HGNN、隐藏维度 512、Adam、学习率 0.001；基础 `SpatialEx` 默认 500 epochs（`SpatialEx/SpatialEx.py:85-135`）。

### 基础 SpatialEx 的两类训练信号

第一类是预测损失。给定 H&E embedding 与超图，网络输出面板表达 $\hat Y$，以均方误差约束：

$$
\mathcal L_{mse}=\|Y-\hat Y\|_2^2.
$$

基础 trainer 为每个切片/面板各建一个模型 `module_HA`、`module_HB`，在配对 mini-batch 上分别计算损失并相加（`SpatialEx/SpatialEx.py:168-189`）。批量版本并非在随机单细胞上直接监督：预处理把邻近细胞聚成 pseudo-spots，并通过 `agg_mtx` 聚合预测和实测表达后算损失。这会提高稳定性和可扩展性，也会平滑真正的单细胞异质性。

第二类是 Deep Graph Infomax 风格的对比损失。模型把真实 H&E 序列编码为 $h_1$，把打乱/破坏后的序列编码为 $h_2$，并以真实表示的均值

$$
c=\frac1N\sum_i h_{1i}
$$

作为全局组织摘要（`SpatialEx/model.py:54-81`）。当前 `Predictor_dgi` 使用 PyTorch `CosineEmbeddingLoss`，令真实表示靠近 $c$、破坏表示远离 $c$；主 `Model` 将预测 MSE 与该损失相加。它与论文显式 cosine 公式功能相近但不是逐字符相同的实现，尤其内置 loss 带 margin 语义。

这项对比约束只要求局部表示与全局上下文相容，不能保证预测到某个基因的具体因果形态特征。

### SpatialEx+ 怎样补齐对角矩阵

设切片 1 实测 $Y_A^1$，切片 2 实测 $Y_B^2$。两个 H&E→omics 主干分别学习 panel A 和 panel B：

$$
f_A(H_1)\approx Y_A^1,\qquad f_B(H_2)\approx Y_B^2.
$$

交叉应用得到缺失面板初估：

$$
\hat Y_A^2=f_A(H_2),\qquad \hat Y_B^1=f_B(H_1).
$$

SpatialEx+ 再建立双向回归模块 $g_{A\to B}$ 与 $g_{B\to A}$。它们既学习“预测 A → 实测 B”“预测 B → 实测 A”，也学习“实测 A → 预测 B”“实测 B → 预测 A”。当前训练总损失是两个主干重构损失加四个 cycle 映射 MSE：

$$
\mathcal L=\mathcal L_A+\mathcal L_B+
\mathcal L_{A\to B}^{cross}+\mathcal L_{B\to A}^{cross}+
\mathcal L_{A\to B}^{cycle}+\mathcal L_{B\to A}^{cycle}.
$$

直接代码为 `SpatialEx/SpatialEx.py:404-441`。非常重要的实现细节是交叉主干预测在 `:430-431` 使用 `grad=False`，cycle 模块的梯度不会穿回 H&E 主干；每轮中先产生 detached prediction，再优化回归头。这比“所有模块完全端到端互相回传”更准确。

代码中的 omics-cycle `Regression` 使用 Linear→LeakyReLU→BatchNorm→Linear→LeakyReLU；论文描述为 Linear→ReLU→BN→Linear，因此激活函数和组件排列存在 Partial match。`Model_Plus` 也包含 MLP、HGNN 和单线性 predictor，而不是纯粹的两层 decoder。

### 直接预测与间接预测

基础 `SpatialEx.inference` 选择 panel A 或 B 的 H&E 主干直接输出；`auto_inference` 把 panel-B 主干应用到切片 1，把 panel-A 主干应用到切片 2（`SpatialEx.py:194-292`）。SpatialEx+ 还有两条路线：direct 是 H&E→目标面板，indirect 是先用 H&E 得到本切片另一面板，再经 omics-cycle 翻译。两条路线的一致程度可以作为内部检查，但它们共享训练假设，不是独立实验验证。

### 百万细胞版本为什么不只是“大 batch”

对于近百万细胞切片，代码使用 `SpatialExP_Big`、HyperSAGE 和空间 tile/pseudo-spot 策略，而不是普通 HGNN 全图训练。空间窗口带重叠，保留局部邻域；细胞先分配到类似 Visium 的六边形 pseudo-spots，损失在聚合后表达上计算。它降低内存并平滑噪声，却改变了监督分辨率。论文 Fig. 4 展示可扩展性，补充表列出约 90 万细胞案例；这不等于所有步骤仍严格在逐细胞损失上运行。

### 六幅主图的证据链

- Fig. 1 定义 H&E 锚定、超图预测与双 omics-cycle 的结构。Extended Data Fig. 1 进一步画出六项损失的数据流。
- Fig. 2 测试单细胞 H&E→omics，在乳腺癌 Xenium 及其他组织上以 PCC、SSIM、CMD、细胞分类和空间域恢复与 CNN_Reg、DeepPT、Hist2ST、THItoGene 等比较。
- Fig. 3 把同一 313-gene 数据拆成互斥 panel，检验 SpatialEx+ 能否补齐并恢复 DCIS/IDC 等空间域。补充消融图显示各模块共同贡献，但作者数据拆分仍比真正跨平台更受控。
- Fig. 4 展示 Human Breast IDC 大切片的百万细胞扩展，以及补齐 panel 后的联合空间域和差异基因模式。
- Fig. 5 处理真正跨模态案例：乳腺癌转录—蛋白和小鼠脑转录—代谢。预测矩阵可以联合分析，但预测模态不能冒充同一细胞上的实验共测。
- Fig. 6 用逐步减少切片重叠的 sliding-window 实验测试稳健性。性能在非重叠时仍有信号，支持 H&E 锚的迁移作用；它并未覆盖严重组织形变、病灶只出现在一张切片或跨批次染色漂移的所有情况。

图像证据在 `paper source/paper/vlm/images/`，逐面板解释见 `figure_analysis.md`。补充材料 `output_paper_supp_md/paper_supp/auto/paper_supp.md` 包含 Supplementary Text 1、Table 1 和 Figs. 1–11。补充文本提出多切片 divide-and-conquer（两两组合数随切片数增长）和 iterative（步骤少但误差累积）策略；它们是建议性扩展，不等于当前主类已实现任意多模态联合模型。

### 指标怎样解释

PCC 衡量每个分子的预测与实测细胞间变化是否线性一致；SSIM 衡量超图上的空间结构相似；CMD 比较分子间相关矩阵；NMI/ACC/AUC 测试预测表达能否支持下游空间域或细胞类型。Supplementary SPCC 比较实测与预测 Moran's I 的相关性，但本地库只实现 Moran's I，没有找到完整 SPCC 汇总代码，可能位于未发布绘图脚本。

高 PCC 不能保证绝对表达校准，高 SSIM 可能受空间平滑抬高，下游标签指标又依赖注释质量。最稳妥的验证应同时检查逐分子误差、空间图、负对照和独立切片。

### 版本与复现边界

核心模型、预处理、教程和五个 notebook 均在本地，但完整论文 benchmark、所有基线运行与绘图汇总并未形成一键流水线。UNI 权重路径硬编码，requirements 也不足以锁定完整 GPU/病理模型环境。论文实现细节报告 Python 3.8、PyTorch 2.3.1、RTX 3090（`paper.md:308-310`）；数据入口与处理后 source data 在 `paper.md:368-374`。

### 最终应怎样使用结果

SpatialEx+ 最适合把相邻切片的互补测量扩展成“可检验的完整候选矩阵”。对关键 marker、罕见细胞群、病灶边界或跨模态机制结论，应回到原始图像和实测数据，并尽可能用独立实验验证，不能把形态推断值当作真正共测值。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpatialEx / SpatialEx+: High-Parameter Spatial Multi-Omics through Histology-Anchored Integration

### Paper Information

- **Title**: High-parameter spatial multi-omics through histology-anchored integration
- **Authors**: Yonghao Liu, Chuyao Wang, Zhikang Wang, Liang Chen, Zhi Li, Jiangning Song, Qi Zou, Rui Gao, Bin-Zhi Qian, Xiaoyue Feng, Renchu Guan, Zhiyuan Yuan
- **Journal**: Nature Methods (2025)
- **DOI**: 10.1038/s41592-025-02926-6
- **Code**: https://github.com/KEAML-JLU/SpatialEx

---

### Motivation & Novelty

#### The Problem

Spatial omics technologies face fundamental trade-offs between resolution, throughput, and the number of measurable features. High-resolution platforms like 10x Xenium can profile ~300 genes per section, but biological understanding demands thousands of genes and multiple omics layers (transcriptomics, proteomics, metabolomics). Simultaneous multi-omics co-profiling on a single section remains technically challenging, and serial-section approaches introduce cellular misalignment.

This creates the **spatial diagonal integration problem**: how to computationally reconstruct comprehensive multi-omics profiles from serial tissue sections, each profiled with different molecular measurements?

#### Limitations of Existing Approaches

- **Single-cell diagonal integration** methods (GLUE, *Nature Biotechnology* 2022; scConfluence, *Nature Communications* 2024) rely on weak biological links (e.g., gene-protein coding relationships) and ignore spatial context
- **H&E-to-omics prediction** methods (DeepPT, *Nature Cancer* 2024; Hist2ST, *Briefings in Bioinformatics* 2022; THItoGene, *Briefings in Bioinformatics* 2024) operate at spot resolution, not single-cell, and don't address cross-omics integration
- **Spatial integration** methods (SpatialGLUE, *Nature Methods* 2024; CellCharter, *Nature Genetics* 2024; MISO, *Nature Methods* 2025) handle vertical/horizontal/mosaic integration but not diagonal integration

#### Unique Contributions

1. **Histology as universal anchor**: Uses H&E images (routinely acquired with any spatial assay) to bridge different tissue sections — a practical anchor that doesn't require co-measured features
2. **Hypergraph learning**: Models multi-cell microenvironment interactions through hyperedges (groups of spatially proximal cells), capturing higher-order spatial dependencies beyond pairwise cell-cell graphs
3. **Omics cycle module**: Enforces cross-omics mapping consistency between serial sections through bidirectional transformation functions (A→B and B→A), ensuring slice-invariant omics relationships
4. **Technology-agnostic design**: Works at both spot-level (Visium) and single-cell resolution (Xenium) without modification, and handles transcriptomics, proteomics, and metabolomics

---

### Method Overview

#### SpatialEx (Base Model)

SpatialEx predicts omics profiles from H&E histology images at single-cell resolution:

1. **Feature extraction**: Cell patches cropped from H&E images → frozen UNI pathology foundation model → 1024-dim embeddings
2. **Hypergraph encoding**: Spatial KNN (k=7) → hypergraph neural network (2 layers) with pre-computed spectral normalization → 512-dim context-aware cell representations
3. **Contrastive learning**: Deep Graph Infomax objective — original vs. feature-shuffled hypergraph — captures global tissue context
4. **Prediction**: MLP decoder maps representations to gene expression space

#### SpatialEx+ (Diagonal Integration)

SpatialEx+ extends SpatialEx for cross-section integration:

1. **Dual backbones**: Two SpatialEx models, one per slice (each with its own omics)
2. **Omics cycle modules**: Two MLP regressors map between omics types (OC₁: A→B, OC₂: B→A)
3. **Cycle-consistent training**: 6 loss terms enforce both per-slice reconstruction and cross-omics mapping consistency. Notably, cross-slice SpatialEx predictions are gradient-detached, meaning OC modules train on fixed predictions each step — a form of alternating optimization not described in the paper (see doc_code.md)
4. **Inference**: Direct prediction + indirect mapping through OC modules produces complete multi-omics profiles for each cell on each slice

See `doc_method.md` for detailed mathematical formulation and `doc_code.md` for implementation mapping.

---

### Evaluation

#### Datasets

| Dataset | Platform | Cells | Features | Task |
|---------|----------|-------|----------|------|
| Human Breast Cancer | Xenium | 167K + 118K | 313 genes | H&E-to-omics, panel integration, omics integration |
| Human Breast IDC Big | Xenium | 893K + 885K | 280 genes | Million-cell scalability |
| Human Colon | Xenium | 134K + 129K | 325 genes | H&E-to-omics |
| Mouse Colon | Xenium | 108K + 111K | 379 genes | H&E-to-omics |
| Human Skin Melanoma | Xenium | 44K + 61K | 282 genes | H&E-to-omics |
| Mouse Brain SMA | Visium + MALDI-MSI | 2.9K + 3.1K | 1000 genes + 50 metabolites | Omics integration |

#### Metrics

- **PCC** (Pearson correlation coefficient): per-gene prediction accuracy
- **SSIM** (structural similarity): spatial pattern preservation
- **CMD** (correlation matrix distance): gene-gene / cell-cell relationship preservation
- **NMI** (normalized mutual information): spatial domain identification accuracy
- **ACC** (accuracy): cell-type transfer accuracy
- **Moran's I / SPCC**: spatial autocorrelation preservation

#### Key Results

**H&E-to-omics prediction** (Fig. 2):
- SpatialEx outperforms DeepPT and CNN_Reg across all metrics on Breast Cancer (PCC: substantially higher per-gene correlations)
- CMD: 0.206 (SpatialEx) vs. 0.302 (DeepPT) — 32% improvement in gene correlation structure preservation
- Successful cell-type annotation (myoepithelial subtypes KRT15+ and ACTA2+) from predicted expression

**Panel diagonal integration** (Fig. 3):
- SpatialEx+ with 150+163 gene panels achieves 28-66% improvement in NMI over DeepPT across spatial resolutions
- Expanded gene panels enable distinction of immune vs. stromal regions invisible with single panels

**Million-cell scalability** (Fig. 4):
- Successfully processes ~900K cells per section
- GO enrichment on newly revealed domains confirms immune response pathways (GO:0002253, adj. P = 4.69×10⁻⁹)

**Omics diagonal integration** (Fig. 5):
- Transcriptomics-proteomics: HER2 and CD20 protein patterns accurately predicted across slices
- Transcriptomics-metabolomics: Multi-omics integration reveals both anatomic and pathological (Parkinson's lesion vs. intact) domains that single omics alone misses

**Robustness** (Fig. 6):
- Minimal performance decline from fully overlapping to completely non-overlapping sequencing areas (flat performance curves across sliding window strides)

#### Compared Methods

| Method | Journal | Year | Task |
|--------|---------|------|------|
| DeepPT | *Nature Cancer* | 2024 | H&E-to-omics baseline (modified for single-cell) |
| CNN_Reg | This paper | 2025 | ResNet50 + MLP baseline |
| Hist2ST | *Briefings in Bioinformatics* | 2022 | H&E-to-omics (adapted with mini-batch) |
| THItoGene | *Briefings in Bioinformatics* | 2024 | H&E-to-omics (adapted with mini-batch) |
| CellCharter | *Nature Genetics* | 2024 | Spatial domain identification (used for evaluation) |
| SpatialGLUE | *Nature Methods* | 2024 | Multi-omics spatial integration (used for downstream) |
| SOView/Pysodb | *Nature Protocols* | 2024 | Visualization tool |

---

### Reproducibility

**Rating: 3.5/5**

#### Strengths
- Code is publicly available on GitHub with 5 tutorial notebooks covering all experimental scenarios
- Pre-computed UNI embeddings are provided on Google Drive for the main breast cancer dataset
- All spatial omics datasets are publicly available from 10x Genomics and Mendeley
- Clear API: `se.SpatialEx(adata1, adata2, graph1, graph2).train()` with sensible defaults

#### Weaknesses
- **UNI model path hardcoded** (`utils.py:208`): Points to authors' local filesystem; users must modify this and obtain UNI model weights (requires Hugging Face access to MahmoodLab/UNI)
- **Missing intermediate preprocessing**: Some data preprocessing steps (protein quantification via NicheTrans, metabolomics alignment) are referenced but not included in the library. Preprocessed immunofluorescence data from the NicheTrans pipeline is available at https://zenodo.org/records/15706278 (cite NicheTrans when using)
- **Cell segmentation outside sequencing area**: Requires pre-computed cell coordinates (provided as CSV) for whole-slide inference; Cellpose segmentation code is included but requires significant compute for large WSIs
- **No configuration file**: Hyperparameters scattered across class defaults; no centralized config for reproduction
- **H&E image registration**: Requires alignment matrices from Xenium Explorer; code for computing these from scratch is not provided

#### Practical Notes
- **Environment**: Python 3.8, PyTorch 2.3.1, CUDA; 24GB VRAM (RTX 3090) sufficient for all experiments
- **Dependencies**: `timm`, `cellpose`, `transformers` (for Phikon), `scanpy`, `tifffile`
- **Training time**: ~6 min for 164K cells (SpatialEx, 500 epochs, RTX 3090); ~73.4 sec for million-cell (SpatialExP_Big, 200 epochs, from Supp Table 1); H&E embedding (UNI inference) ~0.76-0.84s for 167K-119K cells (Supp Table 1)
- **Source data**: All processed experiment data available at Zenodo https://doi.org/10.5281/zenodo.17191222
- **Common pitfall**: UNI model loading fails silently with wrong path; check `create_ImageEncoder` in `utils.py`

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
