---
layout: default
permalink: /paper-atlas/decalign-07c039e2/
title: "DecAlign"
nav: false
description: "DecAlign 面向文本、语音和视觉的情感/情绪识别。它先把每种模态拆成两部分：模态特有表示 sm 与模态共同表示 cm；再对两种子空间使用不同的对齐原则——对特有表示，在原型层面用多边最优传输缓解分布差异；对共同表示，用统计矩和 MMD 逼近共享语义分布；最后把两条分支融合用于预测。 其核心判断是：“跨模态对齐”不是把所有特征强行压到同一空间。语调、面部微表情和词义有互补信息，过度对齐会抹掉差异；"
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
      <span>Representation Models</span>
      <span>ICLR · 2026</span>
    </div>
    <h1>DecAlign</h1>
    <p>DecAlign: Hierarchical Cross-Modal Alignment for Decoupled Multimodal Representation Learning</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2503.11892" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DecAlign：把多模态“共同语义”和“模态特有信息”分开对齐

### 一句话理解

DecAlign 面向文本、语音和视觉的情感/情绪识别。它先把每种模态拆成两部分：模态特有表示 $s_m$ 与模态共同表示 $c_m$；再对两种子空间使用不同的对齐原则——对特有表示，在原型层面用多边最优传输缓解分布差异；对共同表示，用统计矩和 MMD 逼近共享语义分布；最后把两条分支融合用于预测。

其核心判断是：“跨模态对齐”不是把所有特征强行压到同一空间。语调、面部微表情和词义有互补信息，过度对齐会抹掉差异；但三种模态也表达同一个情绪或情感，需要保留共同语义。DecAlign 因此先解耦，再分别处理异质性与同质性。

### 1. 输入、任务与输出

输入是同步或非同步的三种序列：

- language：BERT/DeBERTa 或预提取文本表示；
- acoustic：语音低层描述或 wav2vec 表示；
- visual：面部/视频特征。

三种序列长度和原始维度不同。模型先用一维卷积把 feature dimension 投影到统一的 $d$，得到 $\tilde X_l,\tilde X_a,\tilde X_v$。MOSI、MOSEI、CH-SIMS 输出连续情感强度并衍生二分类/多分类指标；IEMOCAP 输出六类情绪。

论文在四个公开视频多模态 benchmark 上评估，不涉及生物数据。工作区归入 representation models，但这里的“验证”是 sentiment/emotion benchmark，不应描述成生物学验证。

### 2. 第一步：把每个模态拆成 unique 与 common

对模态 $m$，两个编码器产生

$$
s_m=E^{(m)}_{uni}(\tilde X_m),\qquad
c_m=E_{com}(\tilde X_m).
$$

unique encoder 每个模态独立，common encoder 在三种模态之间共享。为减少两部分重复，论文用余弦相似度作为解耦损失：

$$
\mathcal L_{dec}=\sum_m \operatorname{cos}(s_m,c_m).
$$

训练最小化该项，使 unique 与 common 方向尽量不相似。代码 `compute_decoupling_loss()` 把 `[N,d,T]` 展平后计算每个样本的 cosine similarity，再求均值，和这个机制直接对应。

但要注意，当前 unique/common encoder 都只是 kernel size 1 的 Conv1d。它们是逐时间点线性投影，不在这一步建模时间邻域；真正的时序/跨模态交互发生在后续 Transformer。仅有余弦低相关也不保证统计独立或可识别的因子分解。

### 3. 异质性对齐：原型与多边最优传输

#### 3.1 为什么不逐样本硬对齐

文本、音频、视频并不总有一一对应的局部结构。例如一句正面文本可能带讽刺语气；强迫每个 token/帧完全相同会破坏互补信号。论文选择先把每个模态的 unique 表示归到 $K$ 个原型，再在原型分布层面联合对齐。

对每个模态学习原型均值 $\mu_m^k$ 和协方差 $\Sigma_m^k$，样本对原型有软归属 $w_m^n(k)$；批次平均归属形成边缘分布 $\nu_m(k)$。三个模态原型组合 $(i,j,k)$ 的代价为三对原型距离之和：

$$
C_{ijk}=d(l_i,a_j)+d(l_i,v_k)+d(a_j,v_k).
$$

代码的 pairwise cost 使用对角高斯的二阶 Wasserstein 形式：均值平方距离加对角协方差匹配项。随后建立 $K\times K\times K$ cost tensor，并用三边 Sinkhorn 更新缩放向量，使 transport tensor 的三个边缘接近 $\nu_l,\nu_a,\nu_v$。

这比三个独立 pairwise OT 多一个约束：同一个 joint plan 同时协调文本、音频、视觉原型，不会分别求解后得到互相不一致的配对。

#### 3.2 局部原型项

全局 OT 之外，代码还让每个模态样本靠近其他模态原型，累加六个有方向的 sample-to-prototype 距离。最终

$$
\mathcal L_{hete}=\mathcal L_{OT}+\mathcal L_{local-proto}.
$$

#### 3.3 论文与代码的重要差异

论文把原型建模描述为 GMM，并提到 EM 估计 mixture coefficient、均值和协方差。当前实现并没有 EM：`proto_*` 和 `logvar_*` 是普通 `nn.Parameter`，由反向传播更新；样本归属只是 `softmax(-||x-\mu||^2)`，没有使用 mixture weight 或 covariance 计算高斯 posterior。协方差也被限制为对角。

因此最准确的代码级表述是“GMM-inspired learnable prototypes + distance soft assignment + diagonal-Gaussian OT cost”，不能把当前代码称为完整 EM-GMM 实现。

### 4. 同质性对齐：统计矩与 MMD

common 表示应表达跨模态共享语义。DecAlign 比较三种模态的：

- 均值 $\mu_m$；
- 方差/论文记号中的协方差 $\Sigma_m$；
- 偏度 $\Gamma_m$。

两两差异构成 semantic consistency loss。随后把每个 common 序列沿时间平均，用 RBF kernel 的 maximum mean discrepancy：

$$
\operatorname{MMD}^2(X,Y)=
E[k(x,x')]+E[k(y,y')]-2E[k(x,y)].
$$

总同质性损失为

$$
\mathcal L_{homo}=\mathcal L_{sem}+\mathcal L_{MMD}.
$$

代码确实匹配 mean、per-feature variance 和 skewness，并直接在 mean-pooled common features 上算 RBF MMD。论文描述的 Probabilistic Distribution Encoder（PDE）在当前代码中不存在；代码也没有计算完整 covariance matrix，而是方差向量。因此论文的“高阶分布编码”在本地实现中被简化。

### 5. 融合不是只有一条 Transformer 路径

unique 分支有两条并行路径：

1. 把 $s_l,s_a,s_v$ 在 feature 维拼接，送入 multimodal Transformer，取最后时间步；
2. 使用六个 MulT 风格 cross-attention（A/V→L、L/V→A、L/A→V），各模态再通过 memory Transformer，最后拼接并投影。

代码把两条路径做逐元素相加，得到 $h_{hete}$。common 分支对 $c_l,c_a,c_v$ 分别做时间平均并拼接为 $h_{homo}$。最终：

$$
h=[h_{hete};h_{homo}],\qquad \hat y=W h+b.
$$

当三种模态序列长度不同，代码在拼接 Transformer 路径前截到最短长度。这保证张量可拼接，但可能丢失较长音频或视频尾部信息；cross-attention 的价值之一就是处理非严格对齐序列，而这条直接拼接路径仍采用简单截断。

### 6. 总损失及 paper–code 权重差异

论文写成

$$
\mathcal L_{total}=\mathcal L_{task}+\mathcal L_{dec}
+\alpha\mathcal L_{hete}+\beta\mathcal L_{homo}.
$$

回归任务用 L1，分类任务用 cross entropy。当前 trainer 实际计算：

$$
\mathcal L_{code}=\mathcal L_{task}
+\alpha_1\mathcal L_{dec}
+\alpha_2(\mathcal L_{hete}+\mathcal L_{homo}).
$$

也就是说，代码给 decoupling 一个可调权重，并强制 hete/homo 共用一个权重；这与论文分别设置 $\alpha,\beta$ 的形式不完全相同。论文敏感性图显示 0.05 附近较好，过大的对齐权重明显损害性能，符合“过度对齐会压制任务信息”的直觉。

### 7. 图 1–5 怎样支持方法

#### 图 1：总体性能

气泡/散点比较 Acc-2、F1 等指标，DecAlign 位于较优区域。附录表报告五个随机运行均值：MOSI 的 MAE/Corr/Acc-2/Acc-7/F1 为 0.735/0.811/85.75/45.07/85.82；MOSEI 为 0.543/0.768/86.48/55.02/86.07。论文还报告 IEMOCAP WAF1 73.43、CH-SIMS F1 81.85。

这些结果说明在给定预处理、数据 split 和比较协议下有优势；由于本地默认配置与论文表格差异较大，不能假定直接运行仓库默认值即可复现这些数字。

#### 图 2：架构

图中明确区分上方 heterogeneity alignment 与下方 homogeneity alignment：前者有 prototype space、OT 与 Transformer，后者显示 PDE/统计量/MMD。直接代码核对后应把 PDE 视为论文模块、不是本地已实现模块。

#### 图 3：混淆矩阵

MOSI 七级情感混淆矩阵对比 MulT、MISA、DMD 与 DecAlign。DecAlign 在对角线尤其近中性类别上更集中，但极端类别样本少，混淆矩阵的绝对计数也受类别不平衡影响。

#### 图 4：消融和 modality gap

雷达图与类别结果显示移除 heterogeneity 或 homogeneity alignment 均下降。t-SNE 连接同一样本的 language/vision 点：无对齐时分离，单分支对齐部分收缩，完整模型更紧密。t-SNE 是定性投影，不能独立证明原空间分布完全对齐；真正支持组件作用的是消融指标与多次运行结果。

论文消融还包含 Contrastive Training（CT），并声称对判别边界重要，但本地代码没有 contrastive loss。这是关键可复现缺口，不能用现有代码声称完整复现 Table 2。

#### 图 5：超参数敏感性

$\alpha,\beta$ 热图显示中等对齐强度最好，0.2–0.5 时性能快速下降。这说明 auxiliary alignment loss 需要与 task loss 平衡；方法不是“对齐越强越好”。

### 8. 代码可以确认和不能确认的内容

| 论文机制 | 直接代码证据 | 状态 |
|---|---|---|
| unique/common 编码与 cosine decoupling | `code/models/model.py` | Exact |
| learnable prototypes、对角高斯 cost | 同上 | Exact/Partial |
| 三边 Sinkhorn OT | 同上 | Exact（实现形式） |
| 六方向 local prototype alignment | 同上 | Exact |
| mean/variance/skew + RBF MMD | 同上 | Exact/Partial |
| 两路 unique 融合与 common pooling | 同上 | Exact |
| L1/CE task loss、Adam、scheduler、gradient clip | `code/trains/ATIO.py` | Exact |
| EM-GMM posterior | 未找到 | Not found |
| Probabilistic Distribution Encoder | 未找到 | Not found |
| Contrastive Training | 未找到 | Not found |
| IEMOCAP DeBERTa/MA-Net/wav2vec 专用路径 | 未找到 | Not found |

### 9. 默认配置不是论文配置

论文附录给出 dataset-specific 设置，通常 batch size 32、50 epoch、4 层 Transformer、kernel size 5、学习率 $5\times10^{-5}$ 或 $10^{-4}$、对齐权重约 0.05。当前 `dec_config.json` 是单一通用默认：batch 24、100 epoch、5 层、kernel 1、学习率 $10^{-3}$、`alpha1=alpha2=0.1`、weight decay 0。

随机种子也不同：论文写 1–5，代码入口默认 1111–1115。复现时必须显式构造与每个数据集匹配的配置，不能只执行默认 JSON。

另外，论文说 IEMOCAP 使用 DeBERTa、MA-Net 和 wav2vec 特征，当前仓库文本路径仍是通用 `BertTextEncoder`；特征可能在外部预处理 pickle 中已经编码，但本地代码无法证明论文的完整 IEMOCAP extraction pipeline。

### 10. 最重要的理解边界

第一，unique/common 是由损失诱导的潜在子空间，不是可直接观测的“纯语调”或“纯语义”变量。

第二，原型 OT 对齐的是批次内软原型分布；小 batch、prototype 数和 entropy regularization 都会影响稳定性。

第三，当前代码是论文方法的简化/不完全版本。CT、PDE、EM-GMM 缺失使完整论文消融不可由该快照复现。

第四，四个 benchmark 都属于情感/情绪任务。对其他多模态领域的泛化尚未由本文实验建立。

第五，模型目录嵌在 PaperCode 主仓库中，不是独立上游 Git checkout；旧合同中的 commit 无法由本地元数据复核。

### 源证据入口

- 论文与附录：`paper source/paper/vlm/paper.md`
- 图像：`paper source/paper/vlm/images/`
- 核心模型：`code/models/model.py`
- 训练损失：`code/trains/ATIO.py`
- 当前默认配置：`code/config/dec_config.json`
- 论文—代码逐项映射：`doc_code.md`

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## DecAlign: Hierarchical Cross-Modal Alignment for Decoupled Multimodal Representation Learning

### Motivation & Novelty

#### Problem

Multimodal representation learning must integrate heterogeneous signals (text, audio, visual) while preserving modality-specific characteristics. Conventional fusion methods project all modalities into a shared space via concatenation or linear transformation, which **entangles modality-unique features with shared semantics**, causing:

1. **Semantic interference**: Modality-specific details (facial micro-expressions, vocal prosody) disrupt global cross-modal relationships
2. **Dimensional mismatch**: High-dimensional text (768-d BERT) paired with low-dimensional audio (5-74-d COVAREP) leads to information redundancy or loss during fusion
3. **Token-level inconsistencies**: Global alignment methods ignore local, fine-grained semantic mismatches across modalities

#### Limitations of Existing Approaches

- **Transformer-based methods** (MulT, *ACL 2019*; Self-MM, *AAAI 2021*; PMR, *CVPR 2023*) assume a shared latent space and use cross-attention for global fusion. Dominant modalities overshadow weaker ones, causing information loss.
- **Feature decoupling methods** (MISA, *ACM MM 2020*; FDMER, *ACM MM 2022*; DMD, *CVPR 2023*) separate invariant and specific features but primarily focus on global alignment, overlooking token-level inconsistencies.
- **Knowledge distillation** (DMD, *CVPR 2023*; UMDF, *AAAI 2024*) balances inter-modal contributions but risks over-alignment that collapses modality-unique structure.

#### Unique Contributions

1. **Explicit modality decoupling**: Separate encoders extract modality-unique and modality-common features, with a cosine-similarity-based decoupling loss enforcing orthogonality.
2. **Hierarchical alignment**: A dual-stream mechanism applies **prototype-guided multi-marginal optimal transport** for heterogeneous features (local-to-global alignment) and **statistical moment matching + MMD** for homogeneous features (global distributional consistency).
3. **Multi-marginal OT for cross-modal alignment**: Unlike pairwise OT, the multi-marginal formulation simultaneously aligns prototypes across all $M$ modalities via a joint cost tensor and Sinkhorn algorithm.

---

### Method Overview

DecAlign operates in four stages:

1. **Feature Decoupling**: Conv1d encoders split projected features into modality-unique ($s_m$) and modality-common ($c_m$) components. A cosine similarity loss minimizes their overlap.

2. **Heterogeneity Alignment**: Modality-unique features are aligned through:
   - GMM-inspired learnable prototypes as semantic anchors per modality
   - Multi-marginal optimal transport with entropy regularization (Sinkhorn algorithm) for global prototype matching
   - Local sample-to-prototype alignment via weighted Euclidean distance

3. **Homogeneity Alignment**: Modality-common features achieve distributional consistency via:
   - Statistical moment matching (mean, variance, skewness)
   - Maximum Mean Discrepancy (MMD) with Gaussian kernel in RKHS

4. **Multimodal Fusion**: Two parallel heterogeneity paths (transformer temporal fusion + MulT-style cross-modal attention) are combined with mean-pooled common features, then passed through an FC layer for prediction.

See doc_method.md for full mathematical formulation and code mapping.

---

### Evaluation

#### Datasets

| Dataset | Samples | Classes | Language | Modalities | Task |
|---------|---------|---------|----------|------------|------|
| CMU-MOSI | 2,199 clips | 2 & 7 | English | T+A+V | Sentiment regression |
| CMU-MOSEI | 22,856 clips | 2 & 7 | English | T+A+V | Sentiment regression |
| CH-SIMS | 1,368 / 457 (train/test) | 3 | Chinese | T+A+V | Sentiment analysis |
| IEMOCAP | 10,039 utterances | 6 | English | T+A+V | Emotion classification |

#### Metrics

- **Regression**: MAE (↓), Pearson Correlation (↑), Acc-2, Acc-7, F1
- **Classification**: Weighted Accuracy (WAcc), Weighted F1 (WAF1)

#### Key Results (averaged over 5 seeds)

| Dataset | Best Baseline | DecAlign | Improvement |
|---------|--------------|----------|-------------|
| MOSI (F1↑) | DMD: 83.55 | **85.82** | +2.27 |
| MOSEI (F1↑) | CGGM: 83.94 | **86.07** | +2.13 |
| IEMOCAP (WAF1↑) | CGGM: 72.17 | **73.43** | +1.26 |
| CH-SIMS (F1↑) | ReconBoost: 80.41 | **81.85** | +1.44 |

DecAlign outperforms all 13 compared methods across all 4 datasets and 5 metric types. The improvements are most pronounced on classification metrics (Acc-2, F1), indicating better decision boundary calibration.

#### Compared Methods (with journal/year)

| Method | Venue | Year |
|--------|-------|------|
| MFM | arXiv | 2018 |
| MulT | ACL | 2019 |
| MISA | ACM MM | 2020 |
| Self-MM | AAAI | 2021 |
| CENet | IEEE TMM | 2022 |
| CubeMLP | ACM MM | 2022 |
| FDMER | ACM MM | 2022 |
| PMR | CVPR | 2023 |
| MUTA-Net | Information Sciences | 2023 |
| AOBERT | Information Fusion | 2023 |
| DMD | CVPR | 2023 |
| ReconBoost | arXiv | 2024 |
| CGGM | NeurIPS | 2025 |

#### Ablation Studies

Key findings from component ablation (Table 2):
- Removing both Hete+Homo causes the largest drop (MOSI F1: 85.82 → 81.92)
- Heterogeneity alignment has more impact on regression (MAE) than homogeneity
- Homogeneity alignment primarily stabilizes classification metrics (F1)
- All four sub-strategies (Proto-OT, CT, Sem, MMD) contribute; Proto-OT and CT are most critical

**Note**: The ablation includes a "Contrastive Training (CT)" component that does not appear in the released code. See doc_code.md for details.

#### Biological Validation

The t-SNE visualizations (Figure 4e-h) demonstrate progressive modality gap reduction:
- Without alignment: language-vision features are widely separated
- Homo-only: clusters approach but remain fragmented
- Hete-only: distances shrink further, residual anisotropy persists
- Full DecAlign: tight, co-located clusters with minimal cross-modal gap

---

### Reproducibility

#### Rating: 3/5 (Moderate)

**Strengths**:
- Code released with model, training loop, and evaluation
- Standard publicly available datasets (CMU-MOSI, CMU-MOSEI, CH-SIMS, IEMOCAP)
- Dataset-specific hyperparameters documented in Appendix B.3
- Five-seed averaging protocol specified

**Weaknesses**:
- **Contrastive Training (CT) absent from code** — a component claimed essential in ablations is not in the release
- **PDE encoder not implemented** — paper describes a "Probabilistic Distribution Encoder" for MMD that is absent
- **GMM fitting claim vs implementation** — paper claims EM-based GMM; code uses backprop-learned prototypes
- **Default config mismatches** — shipped `dec_config.json` has different batch size (24 vs 32), epochs (100 vs 50), learning rate (1e-3 vs 5e-5), kernel size (1 vs 5), and seeds ([1111-1115] vs {1-5}) compared to paper
- **No dataset-specific config files** — only a single default config is provided; per-dataset overrides presumably require manual specification
- **IEMOCAP features** — paper says DeBERTa/MA-Net/wav2vec for IEMOCAP, but code uses the same BertTextEncoder for all datasets

#### Practical Notes

- **Hardware**: Single NVIDIA A6000 GPU
- **Dependencies**: PyTorch >= 2.0, transformers >= 4.30, standard scientific Python stack
- **Data format**: Pickle files with MMSA-FET extracted features. The data preparation pipeline (`data_prep.sh`, `setup.sh`) is provided but requires MMSA-FET toolkit.
- **Training time**: ~50 epochs with early stopping; BERT fine-tuning dominates compute cost
- **Common pitfall**: Audio features may contain `-inf` values; code replaces them with 0, but this should be verified for new datasets.

#### Strengths

1. Principled decomposition of the alignment problem into heterogeneous and homogeneous components
2. Multi-marginal OT provides theoretically grounded global alignment
3. Consistent improvements across diverse datasets (English, Chinese, sentiment, emotion)
4. Thorough ablation analysis showing complementary roles of each component

#### Weaknesses

1. Three claimed components (CT, PDE, EM-based GMM) are absent from the released code
2. The simplified soft assignment ignores learned covariance parameters during prototype assignment
3. Hyperparameter sensitivity: performance drops sharply when α, β exceed 0.05
4. Evaluation limited to multimodal sentiment/emotion — generalization to other multimodal tasks remains unestablished
5. Loss weight structure in code differs from paper formulation

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
