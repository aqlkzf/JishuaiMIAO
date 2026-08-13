---
layout: default
permalink: /paper-atlas/stflow-71aea22e/
title: "STFlow"
nav: false
wide: true
description: "STFlow 将“由 H&E 图像预测空间转录组”从逐 spot 回归改写成整张切片表达矩阵的生成问题：先从符合计数稀疏性的先验采样一份表达猜测，再让一个局部空间 Transformer 反复根据图像、坐标和邻居当前表达修正它。这样某个 spot 的预测可以显式依赖邻近 spot 的表达状态，而不是把整张切片的联合分布拆成互不相关的单点预测。"
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
      <span>Representation Models</span>
      <span>PMLR · 2025</span>
    </div>
    <h1>STFlow</h1>
    <p>Scalable Generation of Spatial Transcriptomics from Histology Images via Whole-Slide Flow Matching</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/2506.05361" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for STFlow">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Graph-and-Geometric-Learning/STFlow" target="_blank" rel="noopener noreferrer" aria-label="Open code for STFlow">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STFlow 方法解读：用整张切片上的流匹配生成空间基因表达

### 一句话抓住核心

STFlow 将“由 H&E 图像预测空间转录组”从逐 spot 回归改写成整张切片表达矩阵的生成问题：先从符合计数稀疏性的先验采样一份表达猜测，再让一个局部空间 Transformer 反复根据图像、坐标和邻居当前表达修正它。这样某个 spot 的预测可以显式依赖邻近 spot 的表达状态，而不是把整张切片的联合分布拆成互不相关的单点预测。

### 1. 输入与输出是什么

一张切片有 $N$ 个 spot。对第 $i$ 个 spot：

- $I_i$ 是 H&E 图像 patch；
- $C_i\in\mathbb R^2$ 是平面坐标；
- $Y_i\in\mathbb R^G$ 是要预测的 $G$ 个基因表达。

冻结的 pathology foundation model 先把图像变成特征 $Z_i=f_{PFM}(I_i)$。本地训练代码通常不在主循环里运行 UNI、GigaPath 或 Ciga，而是从 HDF5 载入预提取特征；因此“PFM 冻结”在实现上表现为训练数据已经是 embedding。

论文实验预测 top 50 highly variable genes，并用逐基因 Pearson correlation 评价。它生成的是选定基因面板的表达，不是从 H&E 恢复完整转录组，也不等价于真实实验测量。

### 2. 为什么要从回归改成生成

单点模型近似

$$
p(Y\mid I,C)\approx\prod_i p(Y_i\mid I_i,C_i),
$$

这忽略邻近细胞状态之间的统计依赖。STFlow 让去噪器在每一步都读取整片当前表达 $Y_t$，并在局部图上计算邻居表达差 $Y_{t,j}-Y_{t,i}$。所以后一次修正可以利用前一次产生的空间表达格局。

这里“建模 cell-cell interaction”应理解为模型允许邻域表达共同影响预测；它并没有从数据中识别配体—受体关系，也不能仅凭预测证明细胞间的因果调控。

### 3. 训练：在先验与真实表达之间随机插值

训练时先从先验采样 $Y_0$，再采样

$$
t\sim\operatorname{Uniform}(0,1),
$$

并构造线性插值：

$$
Y_t=(1-t)Y_0+tY.
$$

去噪器接收坐标、图像特征、当前表达和时间：

$$
\hat Y=f_\theta(C,Z,Y_t,t),
$$

训练目标是有效（非 padding）spot 上的均方误差：

$$
\mathcal L=\operatorname{MSE}(Y,\hat Y).
$$

`Interpolant.corrupt_exp()` 对应线性插值（`STFlow/stflow/flow/interpolant.py:24-30`）；`Denoiser.forward()` 过滤 padding 后计算 MSE（`model/denoiser.py:93-97`）；训练循环依次采样、插值、预测、反传和梯度裁剪（`app/flow/train.py:61-98`）。

这份实现训练的是“给定 $Y_t,t$ 预测终点 $Y$”的 denoiser，并在采样时由终点预测构造速度；它不是直接让网络输出常见 flow-matching 写法中的向量场 $v_\theta$。理解论文算法时应以仓库的终点预测参数化为准。

### 4. 为什么先验用 ZINB

空间转录组计数通常有大量零并且方差大于均值。论文比较三类先验：全零、标准 Gaussian、zero-inflated negative binomial（ZINB）。ZINB 用负二项部分描述过度离散，用额外的零膨胀概率描述超额零：

$$
p(y)=
\begin{cases}
\pi+(1-\pi)\operatorname{NB}(0;\mu,\phi),&y=0,\\
(1-\pi)\operatorname{NB}(y;\mu,\phi),&y>0.
\end{cases}
$$

代码通过 `scvi.distributions.ZeroInflatedNegativeBinomial` 采样，也提供 Gaussian 和全零先验（`flow/noise.py:4-34`）。非 Gaussian 样本随后做 `log(x+1)`，与表达归一化空间对齐（`flow/interpolant.py:15-19`）。默认 `zi_logits=0` 对应 $\pi=0.5$；论文在 $\mu\in\{0.1,0.2,0.4\}$、$\phi\in\{1,2,4\}$ 上搜索，而不是从训练集自动估计先验参数（附录 A、C；paper.md 第 365、436–438 行）。

附录 Table 10 报告 ZINB 平均表现最好，但逐数据集并非每一项都严格胜出。因此更准确的结论是“ZINB 提供有效总体归纳偏置”，不是它在所有组织和 encoder 上必然最佳。

### 5. 去噪器如何组合图像和时间

`Denoiser` 先把图像 embedding 线性映射到隐藏维度；时间 $t$ 经过正弦/余弦频率编码和两层 MLP。二者相加形成每个 spot 的 token feature：

$$
H_i=W_I Z_i+\operatorname{MLP}(\operatorname{Fourier}(t)).
$$

对应代码是 `image_transform`、`TimestepEmbedder` 和 `features = img_features + time_emb`（`model/denoiser.py:10-49,73-90`）。当前 noisy expression $Y_t$ 不直接加到 token，而是在空间注意力中以邻居表达差参与权重计算，并在每层后由 token 重新预测表达。

### 6. 局部图与空间注意力

对每个 spot，模型在同一切片内选择 $k$ 个最近邻。默认 $k=8$。在目标 $i$ 与邻居 $j$ 之间，注意力消息拼接：

1. 目标 token 的 query；
2. 邻居 token 的 key；
3. 由相对坐标得到的空间边特征；
4. 当前表达差 $Y_{t,j}-Y_{t,i}$。

之后用 MLP 输出每个 head 的标量分数，在邻居维做 softmax，并对邻居 value 和边特征分别加权求和（`model/transformer.py:90-127`）。这正是表达状态进入空间通信的地方。

每个 Transformer block 执行：空间 attention 残差、token MLP 残差、由 token 预测新表达（`transformer.py:130-169`）。四层产生四份表达预测，代码最终取层平均（`transformer.py:219-228`）。

### 7. Frame Averaging 如何实现 E(2) 不变性

直接使用 $(x,y)$ 坐标会对平移、旋转、镜像敏感。STFlow 对中心化后的局部方向向量计算 $2\times2$ 协方差矩阵和特征向量，利用每个主轴的正负号组合构造 $2^2=4$ 个 frame：

$$
C'_{i\to j,o}=F_o^\top(C_j-C_i),\qquad o=1,\ldots,4.
$$

每个 frame 经同一个 edge MLP 后再平均，从而消除特征向量符号不确定性，并使空间表示对二维平移、旋转和反射保持不变。`FrameAveraging.create_frame()` 明确创建四组操作、中心化、求 `torch.linalg.eigh` 并投影（`model/fa.py:7-50`）；空间 attention 在四个 frame 上变换后取均值（`transformer.py:99-107`）。

代码注释中出现过 `N*8`，但实际 `dim=2`，`n_frames=2**dim`，因此运行张量应是四个 frame。解释应服从实际表达式而不是陈旧注释。

图像 patch 本身并没有通过这段 FA 变换。论文认为 PFM 的大规模图像增强使视觉特征对 E(2) 变化较鲁棒；这属于经验假设，不是由 STFlow 代码严格证明的像素级不变性。

### 8. 推断：五步把先验推向表达预测

推断从 $Y_{t_1}\sim p_0$ 开始，在默认五个线性时间点上重复预测。若当前状态为 $Y_t$，网络预测终点 $\hat Y$，代码构造

$$
v_t=\frac{\hat Y-Y_t}{1-t},
$$

并用 Euler 步更新：

$$
Y_{t+\Delta t}=Y_t+\Delta t\,v_t.
$$

`Interpolant.denoise()` 实现这个公式（`flow/interpolant.py:32-38`）；`test()` 从 0.01 到 1.0 建时间网格，逐步调用模型并在最后返回预测（`app/flow/test.py:48-80`）。从 0.01 而非恰好 0 开始并不是为了避免上述分母在 0 处发散；真正的奇点在 $t=1$，而循环在最终更新时间前停止。

论文 Table 5 显示从一步到两步通常改善，五步附近趋于平台，因此默认 $S=5$ 是精度和成本折中，而非数学上保证收敛的步数。

### 9. 复杂度：论文结论与当前实现要分开

若每个 spot 只对固定 $k$ 个邻居做 attention，核心 attention 成本为论文所写的

$$
O(Nkd+Nkd^2),
$$

远小于全局 attention 的二次连接数；推断成本再乘 refinement step 数 $S$。这解释了图 5 中相对 HisToGene、TRIPLEX 的时间/显存优势。

但当前 `_build_graph()` 先广播坐标形成完整 $N\times N$ 相对距离矩阵，再用 `topk` 取近邻（`transformer.py:187-201`）。所以注意力本身是局部的，当前近邻搜索仍有 $O(N^2)$ 的中间内存/计算。训练用随机连续区域 patch 缓解这一问题；把“局部注意力线性扩展”直接等同为“仓库端到端严格线性”是不准确的。真正超大 whole-slide 推断需要分块、稀疏 kNN 或近似邻居实现。

### 10. 图和实验如何支撑结论

- **图 1**：问题和方法总览，显示 spot、邻域表达交互和从先验开始的迭代生成。
- **图 2**：四个 ST 数据集的表达频率分布，支持稀疏、过度离散先验设计。
- **图 3**：去噪器与 E(2)-invariant spatial attention；可与代码的图像+时间 token、FA 边特征、表达差 attention 对照。
- **图 4**：TENX141/TENX115 上 UBE2C（图内标注；正文个别位置写成 UB2EC）与 VWF 的空间预测，并比较去掉 flow matching 的版本。
- **图 5**：不同 spot 数下 slide 模型的推断时间和 GPU memory；视觉 encoder 时间被排除。
- **图 6**：五个 refinement step 的空间表达变化，展示预测逐步接近真值的案例。
- **附录图 7 与 Tables 6–13**：模型参数、数据集统计、先验/架构/消融和 ZINB 超参数补充实验。附录就在同一 `paper.pdf`，已纳入本地证据范围。

论文在 HEST-1k 与 STImage-1K4M 上报告 STFlow 优于八个基线，并称相对 pathology foundation model 平均提升超过 18%。这些是选定数据、基因面板、划分和三随机种子的实验结果，不应解释成对所有组织或临床场景的保证。

### 11. 论文—代码对应与可复现边界

| 机制 | 对应程度 | 直接证据或限制 |
|---|---|---|
| 线性插值、终点预测 MSE、Euler refinement | Exact | `interpolant.py`, `denoiser.py`, `train.py`, `test.py` |
| Gaussian/zero/ZINB 先验 | Exact | `flow/noise.py:4-34`，ZINB 依赖 `scvi-tools` |
| 图像+时间 conditioning | Exact | `model/denoiser.py:73-90` |
| 表达差参与局部注意力 | Exact | `model/transformer.py:90-127` |
| 四-frame E(2) 空间编码 | Exact | `model/fa.py:7-50`; `transformer.py:99-107` |
| 固定 $k$ 局部 attention | Exact | `transformer.py:187-228` |
| 端到端线性 whole-slide scaling | Partial | attention 为局部，但当前 kNN 构图显式生成 $N^2$ 距离矩阵 |
| 发表 checkpoint/完整环境直接运行 | Partial | 依赖外部数据、PFM 权重及若干未锁定依赖 |
| 当前 `Denoiser` 构造 | Code issue | `TransformerBlock` 向 `GeneUpdate` 传 `non_negative`，而当前构造函数不接收该参数（`transformer.py:19-35,160`） |
| 论文 benchmark 重现 | Not rerun | 本次恢复未训练模型或重跑基准 |

这个构造参数不一致会在实例化默认模型时触发 `TypeError`，除非使用的实际运行版本与当前快照不同或补丁另有来源。因此本地代码与论文思想高度对应，但当前快照不能在未经修正/版本核对时标为开箱即用。

### 12. 使用时最容易误解的四点

第一，STFlow 预测的是表达分布的条件样本/估计，并不替代空间转录组实验。第二，“cell-cell interaction”指模型中的邻域依赖，不是已识别的生物因果网络。第三，E(2) 保证针对坐标分支，图像 encoder 的旋转/镜像鲁棒性主要来自预训练增强。第四，ZINB 是人工网格选择的先验，不是从每张新切片自动拟合的真实计数生成机制。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## STFlow — Scalable Generation of Spatial Transcriptomics from Histology Images via Whole-Slide Flow Matching

### Paper Information

- **Authors**: Tinglin Huang, Tianyu Liu, Mehrtash Babadi, Wengong Jin, Rex Ying
- **Affiliations**: Yale University, Broad Institute of MIT and Harvard
- **Venue**: ICML 2025
- **arXiv**: 2506.05361
- **Code**: [github.com/Graph-and-Geometric-Learning/STFlow](https://github.com/Graph-and-Geometric-Learning/STFlow)

---

### Motivation & Novelty

Predicting spatially-resolved gene expression from routine H&E histology images could democratize spatial transcriptomics by removing the need for expensive ST experiments. Existing approaches have two fundamental limitations:

1. **Independent spot prediction**: Methods like STNet (*Nature Biomedical Engineering*, 2020), BLEEP (*NeurIPS*, 2023), and pathology foundation models (UNI, *Nature Medicine*, 2024; GigaPath, *Nature*, 2024) predict each spot's expression independently, ignoring cell-cell communication — a key biological mechanism where neighboring cells influence each other's gene expression.

2. **Scalability**: Slide-level methods like HisToGene (*bioRxiv*, 2021) and TRIPLEX (*CVPR*, 2024) use global attention across all spots, requiring $O(N^2)$ computation that fails on typical WSIs with >10,000 spots.

**STFlow's key contributions**:

- **Joint distribution modeling**: Reformulates gene expression prediction as a generative task using flow matching, where the iterative refinement process allows the model to condition on neighboring cells' (noisy) expressions, explicitly incorporating cell-cell interaction
- **E(2)-invariant local attention**: A frame averaging (FA)-based transformer that achieves spatial invariance (rotation/translation/reflection) while using local k-nearest-neighbor attention ($O(Nkd)$), making it orders of magnitude more efficient than global attention
- **Gene expression-aware prior**: Explores zero-inflated negative binomial (ZINB) prior distribution that matches the sparse, overdispersed nature of gene expression data

---

### Method Overview

STFlow takes pre-extracted pathology foundation model features (from frozen UNI/GigaPath/Ciga encoders) and spot coordinates as input, then predicts gene expression through iterative flow matching refinement.

**Core pipeline**:
1. Extract visual features using a frozen pathology foundation model
2. Sample initial gene expression from ZINB prior distribution
3. Iteratively refine through $S=5$ denoising steps using a spatial transformer
4. The spatial transformer uses local k-NN attention with frame averaging for E(2)-invariance and incorporates gene expression differences between neighboring spots in the attention calculation

The training objective is MSE between predicted and ground-truth expression at random timesteps (flow matching). The denoiser architecture is lightweight (1.15M parameters) compared to alternatives like TRIPLEX (13.8M) or HisToGene (149M).

See `doc_method.md` for detailed mathematical framework and `doc_code.md` for implementation mapping.

---

### Evaluation

#### Datasets

- **HEST-1k** (Jaume et al., *arXiv*, 2024): 10 benchmark datasets across organs (breast, prostate, pancreas, skin, colon, rectum, kidney, liver, lung, lymph nodes), with patient-stratified k-fold cross-validation. Technologies: Visium + Xenium.
- **STImage-1K4M** (Chen et al., *arXiv*, 2024): 7 cancer organ datasets with random 8:1:1 train/val/test splits. Technology: Visium.

#### Metrics

- Pearson correlation between predicted and measured expression for top 50 highly variable genes (after log1p normalization)
- Reported as mean ± std across 3 random seeds

#### Comparative Results

**HEST-1k (10 datasets, average PCC)**:

| Method | Type | PCC |
|---|---|---|
| STNet | Spot-based | 0.286 |
| UNI | Spot-based (foundation) | 0.344 |
| GigaPath | Spot-based (foundation) | 0.344 |
| BLEEP | Spot-based (contrastive) | 0.368 |
| HisToGene | Slide-based | 0.237 |
| TRIPLEX | Slide-based | 0.395 |
| **STFlow** | **Slide-based (generative)** | **0.415** |

STFlow achieves **18% relative improvement** over the best pathology foundation model (BLEEP/GigaPath at 0.368) and **5% absolute improvement** over the best baseline (TRIPLEX at 0.395).

**Biomarker prediction** (4 clinically relevant genes):

| Gene | Best Baseline (TRIPLEX) | STFlow |
|---|---|---|
| GATA3 | 0.853 | **0.860** |
| ERBB2 | 0.832 | **0.844** |
| UBE2C | 0.749 | **0.772** |
| VWF | 0.612 | **0.666** |

#### Ablation Studies

- **Flow matching (w/o FM)**: Removing iterative refinement reduces average PCC from 0.415 to 0.405 (UNI backbone)
- **Frame averaging (w/o FA)**: Removing E(2)-invariant spatial encoding reduces average PCC from 0.415 to 0.406
- **Prior distribution**: ZINB > Zero > Gaussian (consistent across all foundation models)
- **Refinement steps**: Performance improves from $S=1$ (0.405) to $S=2$ (0.417) and plateaus at $S=5$ (0.415)

#### Efficiency

STFlow is significantly more efficient than alternative slide-level architectures:
- **2-3 orders of magnitude faster** inference time than TRIPLEX and HisToGene at scale
- **Lower GPU memory** usage due to local attention (k=8) vs global attention
- GigaPath-slide hits OOM on several datasets; STFlow does not

---

### Reproducibility

**Rating: 4/5** (Good)

**Strengths**:
- Code publicly available with clear structure and README
- Uses established benchmarks (HEST-1k, STImage-1K4M) with public splits
- Pre-trained pathology foundation model weights are downloadable
- Hyperparameters fully documented (Appendix A)
- Dependencies are standard (PyTorch, scanpy, scvi-tools)

**Weaknesses**:
- setup.py is minimal — no requirements.txt or comprehensive dependency specification
- ZINB hyperparameters require grid search (not learned)
- Data download and feature extraction pipeline requires significant setup
- Gene expression dimension (50) is hardcoded in the attention mechanism

**Practical notes**:
- Requires pre-extracted foundation model features (UNI needs access request)
- Training: ~100 epochs with early stopping on single GPU (RTX A6000)
- The code defaults to SwiGLU activation which paper doesn't mention — this may affect reproduction if using GELU
- Potential bug: `non_negative` kwarg passed to `GeneUpdate` but not accepted — may need code modification

**Data availability**: HEST-1k and STImage-1K4M are publicly available. Foundation model weights: UNI (request access), GigaPath (public), Ciga (public).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
