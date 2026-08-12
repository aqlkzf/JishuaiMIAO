---
layout: default
permalink: /paper-atlas/hyperst-7bee7ffe/
title: "HyperST"
nav: false
description: "HyperST 用真实 gene expression 在训练期把 spot/niche 图像表示拉入带层级约束的双曲空间，再从两级图像表示预测 200 个基因；双曲几何是结构正则，不是生成模型，也不是生物层级的直接证据。"
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
      <span>arXiv preprint · 2025</span>
    </div>
    <h1>HyperST</h1>
    <p>HyperST: Hierarchical Hyperbolic Learning for Spatial Transcriptomics Prediction</p>
    <a class="paper-detail__doi" href="https://doi.org/arXiv:2511.22107" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## HyperST：在双曲空间对齐 spot/niche 图像与基因表达

### 先说清它预测什么

HyperST 用 H&E 图像预测空间转录组 spot 的 200 个基因表达。训练时同时需要真实 ST 表达，用它约束图像表示；推断时只用目标 spot 图像和周围 niche 图像，不需要基因输入。

方法的核心不是“用双曲空间直接生成 RNA”，而是把双曲对齐作为表示正则：让配对的 image/gene 靠近，并把“图像比基因更一般、spot 比 niche 更一般”编码成父子偏序。最终仍由普通 MLP 从图像表示回归基因表达。

### 为什么同时需要 spot 和 niche

单个 spot patch 提供局部形态，但一个位置的表达也受周围组织微环境影响。HyperST 为每个中心 spot 构造两级输入：

- spot image $X_s$：以测量点为中心的局部 H&E patch；
- niche image $X_n$：覆盖中心点及空间邻居的更大区域；
- spot gene $Y_s$：中心 spot 的真实表达；
- niche gene $Y_n$：中心及邻居表达的均值。

预处理代码默认 `niche_size=7`。它先用 KDTree 估计能覆盖七个邻居的半径，再剔除超出 WSI、组织占比不足或邻居数不等于七的中心点。spot 和 niche 原始裁剪按真实物理尺度计算，最后都 resize 到 $224\times224$。这样不同扫描分辨率下代表的组织尺度更一致。

需要注意：niche gene 是邻居表达均值，不是新的实验观测；均值会平滑局部异质性。被边界过滤的 spot 也可能使训练样本偏向组织内部。

### 多层表示提取器

#### 图像分支

spot 与 niche 图像共用 UNI 病理基础模型。代码通过 PEFT LoRA 修改 UNI 最后若干 Transformer block 的 `attn.qkv`；默认 `last_layer=11`、rank 8、alpha 16、dropout 0.1，其余预训练权重冻结。随后 spot/niche 各有线性 projector。

Fig. 4 的消融显示，在 kidney 数据上适配 11 层时五个指标总体最佳；0、5、7、11 层之间并非所有误差指标严格单调，因此应读作该数据设置下的超参数证据，而非“LoRA 越深永远越好”。

#### 基因分支

代码没有复杂的预训练 gene foundation model参与主训练：`HyperSTDataset` 读取选定 200 个 HMHVG，对 spot 与 niche count 做 $\log_2(x+1)$，再分别通过线性层和对齐模块中的残差 MLP。真实 spot gene 同时是 decoder 的监督标签。

### 为什么选择 Lorentz 双曲空间

双曲空间具有负曲率，其体积随半径指数增长，适合容纳树状层级。HyperST 使用 Lorentz hyperboloid。曲率写为 $-c$，点 $x=[x_{time},x_{space}]$ 满足

$$
\langle x,x\rangle_{\mathbb L}=-\frac1c.
$$

两个点的距离是

$$
d_{\mathbb L}(x,y)=\frac1{\sqrt c}
\cosh^{-1}(-c\langle x,y\rangle_{\mathbb L}).
$$

神经网络先输出欧氏向量，再把它看作原点切空间向量，经 exponential map 投到双曲面。代码让 `curv` 可训练，并把其对数限制在 $[\log0.1,\log10]$，避免曲率失控。

“离原点近=更一般、离原点远=更具体”不是由几何自动保证，而是由后面的 entailment cone loss 施加。

### HCA：让配对 image/gene 靠近

Hierarchical Contrastive Alignment 用负 Lorentz 距离作为 logit。代码包含四个方向：

1. spot image → spot gene；
2. spot gene → spot image；
3. niche image → spot gene；
4. niche gene → spot image。

每个 batch 中正确对应是正样本，其他 spot 是负样本，四项交叉熵取 $1/4$：

$$
L_{HCA}=\frac14(L_{I_s\to G_s}+L_{G_s\to I_s}
+L_{I_n\to G_s}+L_{G_n\to I_s}).
$$

论文 Eq. 8 印成 $\exp(d_{\mathbb L}/\tau)$，正距离会偏好更远的配对，与“对齐”相反。本地实现明确计算 `-Lorentz.pairwise_dist` 再做 cross-entropy，符合 InfoNCE 的吸引语义；因此这里以代码行为为准，并把论文公式视为符号歧义/排版错误。

HCA 只要求匹配，不自动建立父子方向。

### HEA：用 entailment cone 组织层级

对父概念 $y$，双曲 entailment cone 有半开角

$$
\operatorname{aper}(y)=\sin^{-1}
\left(\frac{2K}{\sqrt c\|y_{space}\|}\right),\quad K=0.1.
$$

若候选子概念 $x$ 与父概念方向的外角超过 cone aperture，就产生 hinge penalty：

$$
L_{entail}(y,x)=\max(0,\operatorname{ext}(y,x)-\operatorname{aper}(y)).
$$

HyperST 约束四种父→子：spot image→spot gene、niche image→niche gene、spot image→niche image、spot gene→niche gene。作者把 image 看作较一般的形态描述，把 gene 看作更具体的分子描述；把 spot 看作较少上下文，把 niche 看作信息更丰富的子概念。

一个角度例子：若父 cone aperture 为 $0.5$ rad，子点外角为 $0.3$，损失为 0；外角为 $0.8$，损失为 $0.3$。它只约束几何位置，不证明现实中 niche 是 spot 的本体论“子类”。

代码与论文 Eq. 10 有两个明确差异：代码把四项之和乘 0.5，而论文写 $1/4$；代码还用未在主文公式出现的 aperture thresholds 0.7（image-gene）和 1.2（spot-niche）。

### decoder 和总损失

对齐模块返回 spot/niche 的**欧氏投影表示**（默认 `predict_norm=false`），模型拼接二者：

$$
\hat Y_s=\operatorname{MLP}([I_s\|I_n]).
$$

预测损失为 MSE。代码总损失实际是

$$
L=L_{pred}+0.2\left(L_{HCA}+0.4L_{HEA}\right),
$$

对应论文 Eq. 11 的 $\alpha=0.2$、$\beta=0.4$。这两个值在论文正文未给出，但 CLI 默认值明确存在。模型只从 image feats 解码，所以测试时 gene branch 仅是训练期教师/正则。

### 左到右追踪一次样本

```text
WSI + ST counts + spot coordinates
  → 物理尺度 spot crop
  → KNN=7 niche crop 与邻居表达均值
  → 200 HMHVG，log2(x+1)
  → UNI + LoRA 得到 spot/niche image embeddings
  → 线性/MLP 得到 spot/niche gene embeddings
  → exp map 投入 Lorentz space
  → HCA 配对对齐 + HEA 父子 cone 正则
  → 拼接 spot/niche image representations
  → 两层 ResMLP + 线性层
  → 200 基因预测与 MSE
```

### 论文—代码对应

| 论文机制 | 直接代码 | 匹配 | 边界 |
|---|---|---|---|
| 物理尺度 patch 与 KNN niche | `dataset_preprocess.py:27-278` | Exact | 默认七邻居并过滤边界 spot |
| 200 HMHVG 与 log transform | `dataset_preprocess.py:513-540`、`hySTDataset.py:148-159` | Exact | niche 是邻居 mean |
| UNI 最后层 LoRA | `HyperST/model.py:7-38` | Exact | 默认 11 个 qkv block，可选 FFN |
| Lorentz distance/exp map/cone | `HyperST/lorentz.py:25-188` | Exact | 曲率可学习并截断 |
| HCA 四向对齐 | `modules/alignment.py:126-145` | Partial | 代码负距离合理，论文 Eq. 8 打印正距离 |
| HEA 四层级 | `modules/alignment.py:147-176` | Partial | 代码权重和 aperture threshold 与主文公式不同 |
| decoder 与 MSE | `HyperST/model.py:164-180` | Exact | 只用 spot+niche image 表示输出 |
| 四数据集实验 | split JSON、`main.py`、Table 1 | Partial | split 文件齐全；可见 shell preprocessing/training 主要是 kidney |

### 结果与解释边界

论文在 HEST-1K 的 kidney、colorectum、skin、lung 上做五次 slide-level 80/10/10 split。Table 1 中 HyperST 在 PCC@10/50/200、MSE、MAE 上均优于列出的四个基线。Kidney NCBI704 的 Fig. 3 中，UMOD/PODXL 示例 PCC 分别为 0.724/0.692，优于展示基线。

这些结果支持预测性能，但不能证明双曲坐标对应真实生物谱系。Fig. 1 的 kidney 组织类型解释是概念示意，Fig. 3 是选取的 biomarker 样例。MSI 分类实验使用预测表达做下游分类，说明保留了一些诊断相关信号，不等于可临床替代 ST。

### 版本和复现边界

1. 论文为 arXiv `2511.22107`（2025）。本地代码来自 `https://github.com/liesgame/HyperST`，采集提交 `93ce2379d66ebf0ce186d1ccf2fa9d570f276289`；代码目录没有独立嵌套 `.git`，提交来自采集元数据。
2. `local metadata` 旧值误写成 paper-only/has_code=false，本轮按实际工作区修正为 paper+code，并补齐 repo URL/commit。
3. 无独立 `SUPP_MD`；补充推导和实验设置嵌在主 OCR `paper.md`。另有 arXiv HTML 转换，但因缺引用/图像未作为 canonical source。
4. 完整复现需要申请 HEST 数据与 gated UNI 权重，并在训练脚本填 Hugging Face token。环境文件和 kidney 入口存在，但其他数据集的可见 shell 工作流不完整。
5. 本轮做了 paper-code-figure 静态验证，未下载全部 HEST、训练 200 epochs 或复算五次 splits；ready 状态表示分析合同完成，不是数值复现证明。
6. CodeGraph 数据库当前索引 0 文件，代码证据均来自直接逐行读取。

### 一句话记忆

HyperST 用真实 gene expression 在训练期把 spot/niche 图像表示拉入带层级约束的双曲空间，再从两级图像表示预测 200 个基因；双曲几何是结构正则，不是生成模型，也不是生物层级的直接证据。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## HyperST — Comprehensive Summary

**Title**: HyperST: Hierarchical Hyperbolic Learning for Spatial Transcriptomics Prediction
**arXiv**: 2511.22107 | Submitted November 2025 (preprint, no journal assignment as of April 2026)
**Authors**: Chen Zhang\*, Yilu An\*, Ying Chen\*, Hao Li, Xitong Ling, Lihao Liu, Junjun He, Yuxiang Lin†, Zihui Wang†, Rongshan Yu† (\* equal contribution; † co-corresponding)
**Affiliations**: Xiamen University; Shanghai AI Laboratory; Tsinghua University; Peng Cheng Laboratory
**Code**: Not yet released (as of April 2026)

---

### Motivation & Novelty

#### The Problem

Spatial transcriptomics (ST) technologies measure gene expression at spatially resolved spots on tissue sections, simultaneously capturing molecular profiles and tissue architecture. Despite their power, ST technologies are expensive (~$1,000–$3,000 per slide), require specialized equipment, and remain restricted to research settings. Predicting gene expression directly from routine H&E histology images — which are cheap, abundant, and already collected clinically — would dramatically lower the barrier for molecular tissue profiling.

#### Limitations of Existing Methods

| Method | Type | Limitation |
|---|---|---|
| StNet [He et al., Nature Biomedical Engineering 2020] | Direct regression | Assumes injective image→gene mapping; ignores biological heterogeneity |
| TRIPLEX [Chung et al., CVPR 2024] | Multi-scale image features | Exploits multi-resolution visual features but lacks explicit hierarchical constraints on gene side |
| BLEEP [Xie et al., NeurIPS 2023] | Contrastive (Euclidean) | Aligns image-gene pairs in flat Euclidean space; ignores data hierarchy; spot-level only |
| Stem [ref 50, citation not recovered from OCR] | Generative probabilistic | Models transcriptional uncertainty but neglects hierarchical structure of ST data |

All existing methods share two core limitations:
1. They model ST data in **Euclidean space**, which cannot efficiently represent the tree-like hierarchy of ST data
2. They use only **spot-level** representations and fail to exploit the niche-level genetic context

#### HyperST's Contributions

1. **Hierarchical data formalization**: Explicit definition of parent-child relationships based on *information specificity* — spot entails niche, image entails gene — in both spatial and cross-modal dimensions.

2. **Multi-Level Representation Extractors**: Parallel extraction of spot-level and niche-level features from both H&E images (UNI+LoRA) and gene expression (FC network), providing biological context beyond individual spots.

3. **Hierarchical Hyperbolic Alignment (HHA)**: Two-component module that (a) aligns paired image-gene embeddings in hyperbolic space using InfoNCE with Lorentzian distance (HCA), and (b) enforces entailment cone constraints to structurally regularize the latent space according to ST data's inherent hierarchy (HEA).

4. **State-of-the-art performance** on four diverse tissue datasets, with consistent improvements particularly large on Lung (+16.7% PCC@200 over next-best TRIPLEX) and clinically validated via MSI status prediction.

---

### Method Overview

HyperST predicts spot-level gene expression from H&E images using three components:

#### Component 1: Multi-Level Representation Extractors

For each spot, two spatial scales are extracted:
- **Spot level**: A patch centered on the spot (physical 55 µm diameter, resized to 224×224)
- **Niche level**: A larger patch encompassing the spot and its K-nearest spatial neighbors

Images are encoded by **UNI** (Chen et al., Nature Medicine 2024) — a large pathology foundation model — adapted with **LoRA** fine-tuning on the last 11 attention layers. Gene profiles (top-200 HMHVG, log-transformed) are encoded by a trainable FC network.

#### Component 2: Hierarchical Hyperbolic Alignment

All four embeddings ($I_s, I_n, G_s, G_n$) are projected into the **Lorentz model** of hyperbolic space via the exponential map at the origin. The Lorentz model is preferred for numerical stability. The curvature $c$ is a **trainable parameter**.

Two alignment losses are applied:
- **HCA** (contrastive): InfoNCE with Lorentzian distance; symmetric at spot level, asymmetric (niche→spot only) to avoid false negatives
- **HEA** (entailment): Entailment cone loss penalizes when child embeddings fall outside the parent's angular cone; enforces spot-image→niche-image, spot-gene→niche-gene, image→gene hierarchies

#### Component 3: Gene Decoder

At test time, only the image encoder is needed. Aligned spot and niche image features are concatenated and passed through an MLP to predict the 200-gene expression profile. Training objective: $\mathcal{L} = \mathcal{L}_{pred} + \alpha(\mathcal{L}_{HCA} + \beta\mathcal{L}_{HEA})$.

**Key inductive bias**: Gene embeddings sit at greater hyperbolic depth (farther from origin) than image embeddings, encoding the fact that gene profiles contain more molecular specificity than images. This forces the image encoder to develop gene-predictive features rather than purely visual ones.

---

### Evaluation

#### Datasets (from HEST-1K)

| Dataset | Tissue | WSIs | Spots | Resolution |
|---|---|---|---|---|
| Kidney [Lake et al., Nature 2023] | Kidney | 23 | 25,944 | 0.76 µm/px |
| Colorectum [Valdeolivas et al., NPJ Precision Oncology 2024] | Colon/Rectum | 14 | 20,733 | 0.45 µm/px |
| Skin [Schäbitz et al., Nature Communications 2022] | Skin | 46 | 35,000+ | 0.52 µm/px |
| Lung [Madisonoon et al., Nature Genetics 2023] | Lung | 16 | 31,445 | 0.45 µm/px |

All data sourced from **HEST-1K** [Jaume et al., NeurIPS 2024] — a standardized spatial transcriptomics collection.

#### Evaluation Protocol

- **Metrics**: PCC@k (mean Pearson correlation of top-k most variable genes), MSE, MAE
- **Splits**: 5 independent random WSI splits (80% train / 10% val / 10% test), results reported as mean ± std
- **Comparison**: StNet, BLEEP, TRIPLEX, Stem — all trained under the same fair protocol

#### Main Results (Table 1)

HyperST achieves state-of-the-art across all 4 datasets and all metrics. Key improvements over TRIPLEX (second-best) on PCC@200:

| Dataset | TRIPLEX PCC@200 | HyperST PCC@200 | Relative Improvement |
|---|---|---|---|
| Kidney | 0.351 ± 0.066 | **0.390 ± 0.070** | +10.95% |
| Colorectum | 0.462 ± 0.191 | **0.477 ± 0.184** | +3.24% |
| Skin | 0.740 ± 0.142 | **0.758 ± 0.129** | +2.52% |
| Lung | 0.393 ± 0.272 | **0.459 ± 0.282** | +16.7% |

Note: Lung shows the largest improvement, likely because lung tissue has more complex cellular heterogeneity where niche-level context is especially informative.

#### Biomarker Visualization (Figure 3)

On kidney sample NCBI704, HyperST's spatial expression maps for UMOD (uromodulin, tubular epithelium marker) and PODXL (podocalyxin, glomerular marker) closely match ground truth spatial patterns (PCC 0.724 and 0.692, respectively), while TRIPLEX achieves only 0.691 and 0.465. The visual maps show that HyperST correctly localizes high-expression regions spatially, whereas other methods produce blurred or mislocalized patterns.

#### Clinical Downstream Validation (Table 2)

Pre-trained on Colorectum, HyperST performs **zero-shot inference** on TCGA-COADREAD (colon/rectal cancer) H&E slides. Predicted pseudo-bulk gene profiles are used to train a Random Forest classifier for MSI (microsatellite instability) status — a key biomarker for immunotherapy eligibility:

| Method | AUROC MSI-H | AUROC MSS |
|---|---|---|
| TRIPLEX | 0.630 ± 0.048 | 0.567 ± 0.032 |
| **HyperST** | **0.719 ± 0.060** | **0.601 ± 0.056** |

HyperST achieves ~14% and ~6% higher AUROC, demonstrating that its predicted gene profiles capture clinically relevant molecular signals.

#### Ablation Studies (Table 3 & 4, Kidney)

**Alignment strategy ablation** (most important: Table 3):

| Configuration | PCC@200 | vs. Full |
|---|---|---|
| Full HyperST | 0.390 | — |
| w/o G-I HEA (only remove gene-image entailment) | 0.378 | −3.1% |
| w/o HEA (remove full entailment) | 0.368 | −5.6% |
| w/o HEA + HCA (remove all alignment) | 0.344 | −11.8% |
| MERU variant (hyperbolic, no multi-level) | 0.355 | −9.0% |
| CLIP variant (Euclidean InfoNCE) | 0.321 | −17.7% |

Key finding: Removing all hyperbolic alignment (falling back to the CLIP-style Euclidean baseline) causes the largest drop (−17.7%), confirming that hyperbolic geometry is central. The entailment loss adds a further 5.6% beyond contrastive alignment alone.

**Decoder input ablation** (Table 4): Using both spot+niche image features (0.390) outperforms spot-only (0.353) or niche-only (0.356), confirming the value of multi-level image representations.

**LoRA layer ablation** (Figure 4): Performance increases monotonically from 0 to 11 adapted layers for PCC metrics. MSE and MAE show slight non-monotonicity (5 layers < 7 layers) but 11 layers remains best overall.

---

### Reproducibility

**Rating: 3/5**

*Justification*: The method is well-described with all equations and evaluation protocols explicitly stated. The HEST-1K dataset is publicly available with standardized processing. However:

**Strengths**:
- Full evaluation protocol described (5-fold WSI splits, metrics, preprocessing)
- HEST-1K data source is publicly available (Jaume et al., NeurIPS 2024)
- Physics-aware patch extraction strategy fully described
- Hyperparameters K=0.1 (entailment boundary) documented; split IDs mentioned as available "in code"

**Weaknesses**:
- **No public code** as of April 2026 (arXiv preprint, code not released)
- Key hyperparameters not specified: $\alpha$, $\beta$, $\tau$ (temperature), LoRA rank $r$, FC network depth/width, curvature initialization, batch size, learning rate, number of epochs, optimizer
- $K$ (number of KNN neighbors for niche construction) not stated in the main paper
- UNI model requires separate access (available via HuggingFace under academic license)
- The sign convention in Eq.8 (using $+d_{\mathbb{L}}$ vs $-d_{\mathbb{L}}$ in InfoNCE numerator) is ambiguous without code

**Practical notes**:
- HEST-1K: `pip install hest` provides standardized access to the 4 benchmark datasets
- UNI: Available from `mahmoodlab/UNI` on HuggingFace (requires institutional verification)
- LoRA adaptation: `peft` library (HuggingFace) or `loralib` can implement the LoRA layers
- Hyperbolic operations: `geoopt` library provides numerically stable Lorentz model implementations
- The HMHVG gene selection (top-200 by combined mean + variance ranking) is non-standard; exact formula not given
- MSI downstream validation uses TCGA-COADREAD (available via GDC portal)

---

### Limitations and Open Questions

1. **No validation on non-Visium platforms**: All four datasets use 10x Visium. Generalization to other ST platforms (Slide-seq, MERFISH, Xenium) is unknown.
2. **Only 200 genes predicted**: HMHVG captures biologically active genes, but many clinically relevant genes may be excluded.
3. **Gene encoder is a simple FC**: The gene pathway uses a minimal FC network while the image pathway uses a large foundation model. Whether a more powerful gene encoder (e.g., transformer) would improve the hyperbolic alignment is unexplored.
4. **Niche-level gene profile = simple average**: Spatial averaging loses information about within-niche heterogeneity. Graph-based aggregation could be more informative.
5. **Curvature c is trainable but not analyzed**: The paper does not report learned curvature values or analyze sensitivity.
6. **HCA sign convention**: Eq.8 uses $d_{\mathbb{L}}$ (distance, not negative distance) in the numerator, which is opposite to standard InfoNCE similarity-based formulation. This may be a notation inconsistency — the implementation likely uses $-d_{\mathbb{L}}$ (or equivalently, attraction by minimizing distance for positives).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
