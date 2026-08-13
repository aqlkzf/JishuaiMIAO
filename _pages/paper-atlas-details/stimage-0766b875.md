---
layout: default
permalink: /paper-atlas/stimage-0766b875/
title: "STimage"
nav: false
description: "空间转录组能够在组织坐标上测量 RNA，但成本高、样本数量有限；常规 H&E 切片便宜且广泛存在，却只能直接观察形态。STimage 用配对的 H&E 图像与空间转录组计数训练模型，学习“一个空间 spot 周围的形态”与“该 spot 的基因表达”之间的统计关联。训练后，只需 H&E 图像即可预测每个位置的基因表达、表达区间或细胞类型。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>Nature Communications · 2026</span>
    </div>
    <h1>STimage</h1>
    <p>Robust and interpretable prediction of gene markers and cell types from spatial transcriptomics data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-68487-0" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for STimage">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/BiomedicalMachineLearning/STimage" target="_blank" rel="noopener noreferrer" aria-label="Open code for STimage">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STimage 方法解读：从 H&E 形态预测空间基因表达分布

### 1. 方法解决什么问题

空间转录组能够在组织坐标上测量 RNA，但成本高、样本数量有限；常规 H&E 切片便宜且广泛存在，却只能直接观察形态。STimage 用配对的 H&E 图像与空间转录组计数训练模型，学习“一个空间 spot 周围的形态”与“该 spot 的基因表达”之间的统计关联。训练后，只需 H&E 图像即可预测每个位置的基因表达、表达区间或细胞类型。

STimage 的关键不是声称图像等同于测序，而是把预测结果建模为负二项分布，并通过模型集成分开描述数据噪声与模型知识不足。论文还加入 LIME 解释、空间 IoU 指标、Xenium 单细胞分类和下游生存/药物反应分析。需要把这些分支区分开：核心 `stimage/` 包直接实现经典 CNN-NB 回归和分类；基础模型集成、完整不确定性流程、Hover-Net 和临床分析更多位于 `development/`、图脚本或外部分析层。

### 2. 输入、输出与预处理

训练输入包括 H&E 图像、空间 spot 坐标和对应基因计数。代码支持旧版 ST 与 Visium，把数据整理为 AnnData，再围绕每个 spot 裁剪瓦片。论文默认瓦片为 $299\times299$ 像素；这个像素范围并不天然等于固定微米尺度，必须结合扫描分辨率和平台 spot 大小解释。论文在跨平台实验中甚至用 Visium 的 55 微米范围去评价原始 100 微米 legacy-ST spot，这是一种显式尺度选择，不应被误读为所有 299 像素都表示同一生物区域。

预处理依次包含：

1. 读取图像、计数矩阵与坐标；
2. 可选对表达矩阵做 `log1p`；
3. 用 Vahadane 方法把染色风格匹配到模板；
4. 通过 OpenCV 计算组织覆盖率，默认删除组织不足 70% 的瓦片；
5. 将保留瓦片裁剪并可做旋转、翻转等增强；
6. 按 `library_id` 做样本级训练、验证和测试拆分。

最后一点可防止同一张切片的相邻瓦片同时进入训练集和测试集造成明显泄漏。不过当前 `02_Training.py:114-119` 对验证生成器也设置了 `aug=True`；这与通常固定验证数据的实践不一致，是本地快照中应保留的复现警告。

### 3. CNN-NB 回归模型

#### 3.1 从形态到潜在向量

默认特征提取器是带 ImageNet 权重的 ResNet50。输入瓦片 $\mathbf{s}$ 经卷积网络 $f_\theta$ 和全局平均池化得到向量

$$
\widehat{\mathbf{z}}=f_\theta(\mathbf{s}).
$$

默认可冻结骨干，也可选择微调。代码还允许 VGG16、InceptionV3、MobileNetV2、DenseNet121 和 Xception。论文进一步以 Virchow2 等病理基础模型替换骨干，但完整基础模型注册与 FSTimage 集成不是主包中的同等成熟路径。

#### 3.2 每个基因预测两个参数

对于每个基因 $g$，模型建立独立的 `Dense(2)` 输出头，并把两个原始数变成负二项分布参数：

$$
\widehat r_g=\operatorname{softplus}(a_g)>0,
\qquad
\widehat p_g=\operatorname{sigmoid}(b_g)\in(0,1).
$$

于是条件表达计数为

$$
X_g\mid\mathbf{s}\sim\operatorname{NB}(\widehat r_g,\widehat p_g),
$$

其均值和方差为

$$
\mu_g(\mathbf{s})=\frac{\widehat r_g(1-\widehat p_g)}{\widehat p_g},
\qquad
\operatorname{Var}[X_g\mid\mathbf{s}]
=\frac{\widehat r_g(1-\widehat p_g)}{\widehat p_g^2}.
$$

例如模型输出 $r=5,p=0.25$，预测均值为 $5\times0.75/0.25=15$，方差为 $60$。与只输出 15 的点预测相比，负二项分布同时表示“期望是多少”和“围绕期望有多分散”。

论文公式把标量 $p$ 的变换写作 Softmax，但本地代码 `stimage/_model.py:71-72` 使用 sigmoid。对一个标量概率，sigmoid 才能把值压到 $(0,1)$；单元素 Softmax 恒为 1。因此这是重要的论文—代码差异，复现应以代码行为为准。

#### 3.3 训练目标

模型对所有基因和 batch 中所有 spot 最小化负对数似然。代码中的单观测损失为

$$
\log\Gamma(r)+\log\Gamma(x+1)-\log\Gamma(r+x)
-r\log p-x\log(1-p).
$$

它与代码采用的负二项参数化一致，使用 Adam，学习率为 $10^{-5}$，可设置 patience 10 的早停。虽然论文说多基因可共同训练并“学习基因关系”，代码实现实际是共享图像骨干、每个基因使用独立输出头；共享表示能传递形态信息，但没有显式的基因—基因图或协方差层。

### 4. 不确定性如何分解

一个模型给出 NB 分布，因此其预测方差描述在固定模型下的随机性，即 aleatoric uncertainty。多个随机种子或不同骨干模型产生多个均值；这些均值之间的变化反映 epistemic uncertainty。全方差公式写作

$$
\operatorname{Var}(X_g\mid\mathbf{s})=
\operatorname{Var}_{\Theta}\!\left[
\mathbb{E}(X_g\mid\mathbf{s},\Theta)\right]
+
\mathbb{E}_{\Theta}\!\left[
\operatorname{Var}(X_g\mid\mathbf{s},\Theta)\right].
$$

第一项是模型均值跨成员的方差，第二项是成员内部 NB 方差的平均。直觉上：更多、更匹配的训练数据可能降低 epistemic uncertainty，但不会消除测量和生物固有噪声。

论文训练 30 个模型，并从中构造五个集成；FSTimage 还平均多种病理基础模型的结果。本地 `development/ensemble_training.py` 有研究脚本，但主包没有一个与论文所有集成步骤完全对应的稳定命令。因此“不确定性公式有直接论文证据、核心 NB 有直接包代码、完整集成属于 Notebook/开发层”三者必须分别陈述。

### 5. 为什么还需要空间指标

PCC 衡量预测值与观测值的线性相关，但不直接检查高表达区域是否落在相同位置。论文提出几何 IoU：

1. 分别把预测与真值标准化为 z-score；
2. 以 0 为阈值二值化高/低表达；
3. 按 spot 坐标还原为空间矩阵；
4. 用 $\sigma=1$ 的 Gaussian filter 降噪；
5. 计算两个高表达区域的交并比

$$
\operatorname{IoU}=\frac{|A\cap B|}{|A\cup B|}.
$$

本地 `_utils.py` 只直接导入 Jaccard/IoU 计算，未在核心包中完整实现论文所述 Gaussian-filtered 空间构造，因此代码匹配为 Partial。PCC、Moran's I 和 IoU 回答不同问题，不能相互替代。

### 6. LIME 解释的是局部敏感性，不是因果机制

LIME 先把一个瓦片分成核/区域，再反复遮蔽这些区域，观察目标基因预测怎样变化，最后用稀疏局部线性模型近似神经网络。正权重表示在该局部扰动实验中，保留该区域倾向于提高预测。

论文写明使用 Cellpose-3 分割细胞核；当前 `stimage/04_Interpretation.py:53-72` 却将图像转为 HED，经过阈值、距离变换和 watershed 产生分区，再交给 LIME。因此本地可复现的是 watershed 版本，不是论文所称 Cellpose-3 版本。LIME 热图也只说明模型对扰动的响应，不能证明某类细胞因果性地驱动基因表达。透明评审文件曾要求扩大解释评估并检验 faithfulness，这提醒读者不要只凭少量漂亮热图作强生物学结论。

### 7. 分类分支与 Xenium 单细胞分支

主包的表达分类分支先提取 ResNet50 2048 维特征，再用 elastic-net logistic regression 做多输出分类。论文描述按 z-score 将表达分为 high/low；当前训练脚本却用 `pd.qcut(x, 3)` 创建三个分位数组，因此标签定义是 Partial，而不是精确复现论文二分类。

图 4 的 Xenium 单细胞任务是另一条路线：作者用 Seurat 参考映射生成四类细胞标签，经 SIFT 把 Xenium DAPI 与 H&E 配准，再修改 Hover-Net 同时做核实例分割与细胞分类。五张乳腺癌切片用四训一测的 LOOCV。该实现位于 `Figure_scripts/Figure4/train_hovernet_rep1.py`，不是主 `stimage` CNN-NB 入口；图中癌上皮最易识别，而基质、免疫、内皮特征重叠更多，熵高的区域也更易误分类。

### 8. 主图怎样串起证据

- 图 1：预处理、CNN/基础模型—NB 架构、COX6C/KRT5 spot 预测、FFPE 外部测试及 TCGA 相邻切片应用。
- 图 2：CD63/ATP1A1 的 aleatoric 与 epistemic 不确定性、单模型对集成、空间 IoU，以及 33 张 HER2ST 切片上的 LOOCV 基准。
- 图 3：跨技术与癌种外推，包括 legacy ST、皮肤 Visium、Xenium 聚合真值和 PhenoCycler 蛋白信号。
- 图 4：Xenium-Hover-Net 单细胞分割/分类、混淆矩阵、潜在空间与预测熵。
- 图 5：TCGA 1034 张乳腺癌图像的 pseudo-bulk 预测、Cox 生存分层及下游临床关联。

主文报告：九个 Visium 训练样本预测两个外部 FFPE 样本时，1522 个功能基因中 1136 个为正相关，顶级基因 PCC 约 0.4；在 33 张 HER2ST 切片基准中多数样本优于比较方法；额外测试覆盖皮肤、肾、肝、Xenium 与 PhenoCycler。跨域结果有启发性，但表现随患者、平台和基因明显变化，不能把“某些标记的空间图一致”推广为任意基因、任意癌种的可靠替代测序。

### 9. 补充材料与评审材料的作用

21 页补充信息包含数据集表和 S1–S18 等扩展实验：OOD 基准、染色归一化、瓦片尺寸、皮肤/肝/肾 LOOCV、分类、LIME、Xenium 与临床分析。58 页透明评审文件记录了早期审稿人对样本量、跨平台偏差、解释 faithfulness、展示基因选择和统计检验的质疑，以及作者的修改回复。4 页 reporting summary 给出研究设计与复现声明。

补充图强化了覆盖范围，却也揭示了边界：不同样本性能离散；299 像素是经验优化结果；模型对染色归一化敏感；解释结论仍依赖分割与局部扰动选择。评审回复是理解修改历史的材料，不等同于独立验证。

### 10. 论文与当前代码快照的证据等级

代码仓库固定在提交 `206cc19ca89d985245ca204fbc86772e5c2446d0`。证据可分为：

| 组件 | 状态 | 直接边界 |
|---|---|---|
| CNN-NB、NLL、预处理、样本拆分、预测均值 | Exact | 主 `stimage/` 源码可定位 |
| Gaussian-IoU、二分类标签、完整集成 | Partial / Notebook | 核心包缺部分步骤或实现与论文不同 |
| Cellpose-3 LIME 分割 | Mismatch | 本地解释脚本实际使用 watershed |
| FSTimage、Hover-Net、TCGA 生存/药物反应 | Development / Figure scripts | 不是统一主包流水线 |

### 11. 最值得保留的使用边界

1. 输出是由训练数据支持的形态—表达统计预测，不是测得 RNA。
2. NB 参数化允许表达离散度，但分布校准仍需独立检查。
3. 小样本与跨平台场景尤其应同时报告 epistemic uncertainty、性能分布和失败病例。
4. 必须按患者/切片拆分，不能按相邻瓦片随机拆分。
5. 扫描分辨率、spot 尺度、染色模板和瓦片大小共同决定形态上下文。
6. LIME 区域是局部解释，不是细胞功能或因果证据。
7. TCGA 生存和药物反应属于下游关联分析，不能单独建立临床效用。

STimage 最重要的思想是：不只预测一个表达数，而是预测一个条件分布，并把空间一致性、模型集成和局部解释加入评估。但真正复现时必须沿着代码边界区分核心包、开发脚本和论文级分析，尤其不能忽略 sigmoid/Softmax、二类/三类标签、Cellpose/watershed 这三处明确差异。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## STimage: Robust and Interpretable Spatial Gene Expression Prediction from H&E Images

**Paper:** Tan X, Mulay O, Xie J, et al. "Robust and interpretable prediction of gene markers and cell types from spatial transcriptomics data." *Nature Communications* 17, 2026.
**DOI:** 10.1038/s41467-026-68487-0
**Code:** https://github.com/BiomedicalMachineLearning/STimage
**Category:** segmentation_annotation

---

### Motivation & Novelty

#### Biological Problem

Spatial transcriptomics (ST) — platforms like 10x Visium — produces matched H&E histology images and genome-wide gene expression for each spatial spot. This creates a powerful training opportunity: a deep learning model can learn to predict molecular expression from morphological appearance alone. Once trained, the model can be applied to routine H&E slides (far cheaper and more available than ST), enabling molecular-resolution analysis of millions of archived pathology specimens.

The clinical stakes are high: predicting gene expression from histology enables survival stratification, drug response prediction, and identification of tissue regions with cancer-relevant molecular states — all without additional sequencing.

#### Limitations of Existing Approaches

| Method | Limitation |
|--------|-----------|
| HE2RNA (*Nat. Commun.* 2020) | Whole-slide level prediction only; no per-spot spatial resolution; no uncertainty |
| STnet (*Nat. Biomed. Eng.* 2020) | Fixed point estimates; no distribution modeling; no uncertainty |
| Hist2Gene (*Sci. Rep.* 2022) | Limited performance on small datasets |
| Hist2ST (*Bioinformatics* 2022) | Zero-inflated NB but no epistemic uncertainty; ViT requires all spots in memory (not scalable to Visium's 3,000+ spots); fails on 32GB GPU |
| HisToGene (*Nat. Commun.* 2023) | ViT memory bottleneck; no distribution output; no uncertainty |
| Xfuse (*Nat. Biotechnol.* 2022) | Fixed point estimates; no uncertainty quantification |

#### Unique Contributions

1. **Distributional prediction:** Models gene expression as a Negative Binomial distribution (not a point estimate), providing calibrated uncertainty estimates per spot per gene.
2. **Dual uncertainty decomposition:** Uses an ensemble of 30 models to separate epistemic uncertainty (model ignorance) from aleatoric uncertainty (data noise) via the law of total variance.
3. **Nucleus-level LIME interpretability:** Identifies which nuclei in a tile drive predictions for specific genes, integrated with pathological annotations at single-cell resolution.
4. **Foundation model integration (FSTimage_ens):** Extends the NB output head to any image backbone including GigaPath, Virchow2, H-Optimus, UNI, CONCH, Phikon, CTransPath for further performance gains.
5. **IoU spatial metric:** A novel geometric evaluation metric that measures how well predicted spatial patterns match observed patterns (vs. PCC which ignores spatial structure).
6. **Scalability:** Tile-independent CNN architecture processes spots independently, enabling datasets from hundreds of thousands of Xenium single-cell spots without memory constraints.
7. **Clinical translation:** Demonstrated patient survival stratification (Cox regression, c-index >0.6) and drug response prediction (AUC=0.70) from H&E images using STimage-predicted gene expression.

---

### Method Overview

STimage is a six-step pipeline combining deep learning with probabilistic modeling:

1. **Preprocessing:** Tile 299×299 pixel windows from H&E WSIs at ST spot coordinates. Filter tiles with <70% tissue coverage. Apply Vahadane stain normalization to reduce technical batch effects between slides.

2. **Feature extraction:** Frozen ResNet50 (ImageNet-pretrained) processes each tile independently through convolutional layers + GlobalAveragePooling2D to produce a 2048-dimensional feature vector per spot. Alternatively, foundation models (Virchow2 has 632M parameters, trained on 3.2M WSIs) can replace ResNet50.

3. **NB distribution heads:** For each of $G$ genes, a separate Dense(2) layer maps the feature vector to (r̂, p̂) — parameters of the Negative Binomial distribution. Softplus ensures r̂>0; sigmoid ensures p̂∈(0,1). The model is trained by minimizing the NB negative log-likelihood (NLL) jointly over all genes.

4. **Prediction:** Predicted gene expression = NB mean = $\hat{r}(1-\hat{p})/\hat{p}$ per spot.

5. **Uncertainty:** Ensemble of 30 models trained with different random seeds. Epistemic uncertainty = variance of predicted means across ensemble members; aleatoric = mean of NB variances. Both are visualized as spatial heatmaps.

6. **Interpretability:** LIME with nucleus-level segmentation identifies histologically meaningful cellular features that explain predictions for individual genes.

**Key assumptions:**
- Spots are spatially independent (no inter-spot context in standard model)
- Training and test samples come from matched tissue types (though OOD testing shows good cross-cancer generalizability)
- Gene expression is count-distributed (NB)

See `doc_method.md` for full mathematical derivations and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Datasets

| Dataset | Type | Size | Used For |
|---------|------|------|---------|
| 10x Visium breast cancer (in-house) | Fresh frozen, Visium | 2 samples | Initial development |
| Swarbrick HER2+ (Wu et al., *Nat. Genet.* 2021) | Fresh frozen, Visium | 6 samples | Training |
| 10x Genomics public Visium | Fresh frozen, Visium | 3 samples | Training |
| 10x FFPE Visium | FFPE, Visium | 1 sample (OOD test) | OOD evaluation |
| HER2ST (Andersson et al., *Nat. Commun.* 2021) | Legacy ST | 33 samples (36-3 low quality) | LOOCV benchmarking |
| Xenium breast cancer (in-house) | Single-cell, Xenium | 5 samples | Cell classification |
| Skin melanoma (in-house) | FFPE, Visium | 13 samples (10 patients) | Cancer-type generalization |
| Kidney cancer (Raghubar et al., 2023) | Fresh frozen, Visium | 6 samples | Cancer-type generalization |
| Liver immune disease (GSE240429) | FFPE, Visium | 4 samples | Non-cancer generalization |
| PhenoCycler Fusion skin cancer (in-house) | Spatial proteomics | — | Gene-protein correlation |
| TCGA-BRCA | Non-spatial WSI + bulk RNA | 1034 images, 670 patients | Clinical validation |
| Drug response cohort (Sammut et al., *Nature* 2022) | Non-spatial | 168 patients | Drug response prediction |

**Total:** 87,166 ST spots + 2.1 million cells (Xenium) + 670 TCGA patients

#### Primary Metrics

- **PCC:** Pearson correlation between predicted and observed gene expression per gene per sample
- **Moran's I:** Spatial autocorrelation metric — rewards spatially coherent predictions
- **IoU:** Intersection over Union of binarized spatial expression maps (novel metric)
- **AUC:** Area under ROC curve for classification tasks
- **C-index:** Concordance index for survival models

#### Key Results

**Gene expression prediction (HER2ST LOOCV, 33 samples):**
- STimage outperforms STnet, HisToGene, THItoGene, IGI-DL, and Hist2ST in the majority of 33 test samples
- Virchow2_STimage (foundation model backbone) consistently outperforms vanilla STimage
- FSTimage_ens (ensemble of 8 foundation models) achieves the highest performance

**Top functional genes (breast cancer):**
- 1136/1522 functional genes show positive PCC
- Top 10 genes: PCC ≈ 0.4 for FFPE test samples
- Top predicted gene ATP1A1: PCC = 0.51-0.52 on FFPE out-of-distribution data

**OOD performance:**
- Model trained on fresh-frozen Visium generalizes to FFPE (different technology, cohort)
- Cross-cancer generalization: breast→skin (SOX10, S100B, CD34 predicted from breast-trained model)
- Cross-platform: Visium-trained model applied to legacy ST, Xenium, PhenoCycler Fusion, and TCGA

**Cell type classification (Xenium, 5 samples LOOCV):**
- Cancer epithelial cells: highest F1 scores
- Overall: outperforms CellViT (*Med. Image Anal.* 2024) in IoU scores
- Uncertainty (entropy) enriched in misclassified regions

**TCGA validation:**
- Average gene-wise PCC = 0.48 across 1034 images from 670 patients
- Survival: c-index >0.6 for multivariate Cox models using predicted expression
- Drug response: AUC = 0.70 (vs. 0.78 using true bulk RNA-seq)

#### Ablations

- Stain normalization improves performance (Fig. S3)
- 299×299 tile size optimal (Fig. S4, different resolutions tested)
- Ensemble of 10 models outperforms individual models and reduces variance

---

### Reproducibility

**Rating: 3/5**

**Strengths:**
- Full code available at https://github.com/BiomedicalMachineLearning/STimage under BSD-3 license
- 6-step pipeline with config-file interface is reasonably user-friendly
- All public datasets are linked; private in-house data available upon request through UQ eSpace
- Pre-trained models for 4 cancer types available through Streamlit web app
- Tutorials and example config files provided

**Weaknesses:**
- **Foundation model ensembling (FSTimage_ens)** — the paper's best-performing model — exists only in `development/` scripts, not in the installable package. Requires proprietary foundation model access (Virchow2, GigaPath require gated access)
- **Uncertainty quantification** (30 models, 5 ensemble groups) is in `development/ensemble_training.py`, not main package
- **Environment requires Python 3.8** with TF 2.15.0 + Keras 2.15.0 — specific version constraints may cause conflicts on modern systems
- **Validation augmentation bug:** validation generator uses aug=True (same as training) — this would affect reported performance metrics
- **Missing ResNet preprocessing:** standard ResNet50 preprocessing (`preprocess_resnet`) is commented out in DataGenerator — inconsistent with ImageNet pretraining
- Large TCGA dataset (1034 images, 1034 patients) and Xenium data require substantial storage and compute

**Common pitfalls:**
- Install with Python 3.8 specifically: `conda create -n stimage python=3.8 python-spams`
- Stain normalization requires a template sample — specify `template_sample` in config
- Sample-level split is mandatory for honest evaluation; do not set both `training_ratio=1.0`
- For FFPE test on fresh-frozen model (OOD): expect lower PCC but reasonable IoU
- Foundation model use requires separate authentication/download for each model

---

### Strengths and Weaknesses

**Strengths:**
- Principled probabilistic framework (NB distribution) for count data
- Uncertainty decomposition is theoretically grounded and clinically meaningful
- Single-cell resolution interpretability via LIME + nucleus segmentation
- Comprehensive evaluation across 4 cancer types, 5 spatial platforms, non-spatial TCGA
- Strong clinical translation results (survival + drug response)
- Scalable: processes 100K+ Xenium cells without memory issues

**Weaknesses:**
- Backbone is frozen by default — misses fine-grained tissue-specific features learnable from ST data
- No spatial context between spots (each tile is independent) — ignores neighborhood gene expression patterns
- LIME is computationally expensive (1000 perturbations per tile); not practical for whole-slide analysis
- Foundation model results require gated access to commercial model weights
- Paper-code discrepancies (Cellpose-3 vs. watershed; binary vs. 3-class; Softmax vs. sigmoid) reduce exact reproducibility confidence
- PCC values remain modest (0.4 for top genes) — the biological signal is real but partial

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
