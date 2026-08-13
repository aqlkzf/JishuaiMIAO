---
layout: default
permalink: /paper-atlas/groupsparseae-c31ff932/
title: "GroupSparseAE"
nav: false
description: "CLIP、CLAP 已经把图像—文本或音频—文本对齐到同一稠密空间，但普通 TopK 稀疏自编码器常把两个模态拆成两套互不重叠的特征。论文的 GSAE 在配对样本的稀疏码上加入组稀疏约束，MGSAE 再让两个模态共享同一个随机候选 mask，迫使对应样本更多地激活同一批概念神经元。"
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
      <span>ICLR · 2026</span>
    </div>
    <h1>GroupSparseAE</h1>
    <p>Decomposing multimodal embedding spaces with group-sparse autoencoders</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2601.20028" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GroupSparseAE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/saprmarks/dictionary_learning" target="_blank" rel="noopener noreferrer" aria-label="Open code for GroupSparseAE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Group-Sparse Autoencoders：让多模态稀疏字典共享概念

### 一句话理解

CLIP、CLAP 已经把图像—文本或音频—文本对齐到同一稠密空间，但普通 TopK 稀疏自编码器常把两个模态拆成两套互不重叠的特征。论文的 GSAE 在配对样本的稀疏码上加入组稀疏约束，MGSAE 再让两个模态共享同一个随机候选 mask，迫使对应样本更多地激活同一批概念神经元。

### 1. “split dictionary”是什么

设 $x$ 是图像或音频 embedding，$y$ 是与之配对的文本 embedding。原始多模态编码器已经使 $x$ 和 $y$ 语义对齐。但若分别经过同一个普通 SAE，可能得到

$$
z_x=(0,1.2,0,\ldots),\qquad
z_y=(0,0,0.9,\ldots).
$$

两者都能良好重构输入，却使用不同字典坐标表达同一个概念。这就是 split dictionary：字典的大量特征只对一个模态激活。它不一定破坏单模态重构，却会破坏跨模态检索、概念命名和统一干预。

图 1 用两组紫色箭头表示 split dictionary 与共享多模态字典的差别。论文 Theorem 1 进一步说明，在有限、已对齐的配对数据上，若存在 split 字典，总能构造一个非 split 的可行替代；因此分裂不是表示空间强制的结果，而是训练目标和优化偏置造成的。这个构造可能增加字典元素，不能理解为“固定容量下非 split 解一定同样容易学到”。

### 2. 普通 TopK SAE 基座

对 $d$ 维 embedding $x$，编码和解码为

$$
z=\Pi_K\!\left(W_{enc}(x-b_0)+b\right),
$$

$$
\hat x=W_{dec}z+b_0.
$$

$\Pi_K$ 通常先 ReLU，再只保留最大的 $K$ 个正激活。字典大小 $p>d$，所以每个输入只用少数列重构。论文主实验中 $d=512$、扩展倍数 16，即 $p=8192$，并取 $K=32$。

本地 `dictionary_learning` 固定提交实现了这套基座：`AutoEncoderTopK.encode` 做 centering、linear、ReLU、TopK，`decode` 做线性重构；`TopKTrainer` 处理重构损失、死特征辅助损失、单位范数 decoder、梯度投影和阈值跟踪。

但这只是论文所引用的基础库，不是 GSAE/MGSAE 论文实验代码。

### 3. GSAE：用 $L_{2,1}$ 把配对特征绑成组

对配对输入 $(x,y)$，共享 encoder、decoder 和 encoder bias，但允许两个模态有不同的 centering bias $b_0,b_1$：

$$
z_x=\Pi_K(W_{enc}(x-b_0)+b),
$$

$$
z_y=\Pi_K(W_{enc}(y-b_1)+b).
$$

组稀疏项为

$$
\mathcal L_{gs}(z_x,z_y)
=\sum_{i=1}^{p}\sqrt{z_{x,i}^2+z_{y,i}^2}.
$$

总损失为

$$
\mathcal L=
\lVert x-\hat x\rVert_2^2+
\lVert y-\hat y\rVert_2^2+
\lambda\mathcal L_{gs}.
$$

为什么这会鼓励共享支持？对第 $i$ 个字典特征，两个模态的激活被当作一个二维组。若只让一个模态单独激活，会新增一个组范数代价；若配对语义可以由同一坐标共同承担，两个激活共享一个组，代价更有利。

需要精确表述：$L_{2,1}$ 鼓励整个组同时为零或共同保留，但它不直接要求 $z_{x,i}=z_{y,i}$，也不保证每一对样本拥有完全相同的 TopK 支持。重构项、$\lambda$ 和容量共同决定平衡。

主实验对 GSAE 选择 $\lambda=0.05$；附录的扩展倍数/$K$ sweep 使用 $\lambda=0.01$。这些数值是实验选择，不是理论唯一值。

### 4. MGSAE：共享随机 mask 再做 TopK

MGSAE 在 encoder 输出和 TopK 之间，对两个模态应用同一个随机二值 mask：

1. 计算配对样本的 dense pre-activations；
2. 采样一个共享 mask；
3. 两个模态都只能从 mask 保留的相同坐标集合中选 TopK；
4. 分别解码并计算重构 + group-sparse loss。

图 2 直接画出 paired encoders、共享 mask、TopK 和线性 decoder。共享 mask 不保证最后选出的 $K$ 个坐标完全一致，但缩小了两者的共同候选池，也能让长期未被选中的神经元获得机会。

论文在 CLIP/CLAP 主实验中从多个概率中选择 $p=0.2$，以让 explained variance 接近 GSAE。附录其他编码器实验采用不同 mask 参数，所以不能把 0.2 当作跨模型默认。

### 5. MMS：怎样判断特征既语义一致又跨模态

仅统计“这个神经元是否在两个模态出现”还不够，因为它可能对一堆不相关样本激活。论文定义 Multimodal Monosemanticity Score (MMS)，考察一个特征高激活样本之间的语义相似度，并分别计算同模态和跨模态组合，例如：

- MMS(image, image)
- MMS(text, text)
- MMS(image, text)

高跨模态 MMS 表示该神经元在图像和文本中都对应相近语义。图 4 把每个模型的特征按 MMS 降序排列；曲线能显示高质量特征有多少，以及后段何时落到零。MMS 依赖另一个相似度编码器，因此它测量的是参照模型定义下的语义一致性，不是绝对的人类可解释性。

本地基础库只有一般 SAE reconstruction、L0、fraction alive 等评估，没有论文的 MMS 实现。

### 6. 从数据到训练的完整论文流程

#### 图像—文本

- 用 CLIP ViT-B/16 提取 CC3M 配对图像/标题 embeddings；
- 每个 embedding 先做单位 L2 归一化；
- 用配对 batch 训练 SAE、GSAE、MGSAE 25,000 steps；
- 主设置 batch 128、$K=32$、16 倍字典。

#### 音频—文本

- 用音乐微调的 LAION-CLAP 提取 JamendoMaxCaps 音乐/标题 embeddings；
- 音频预处理为 30 秒片段；
- 训练 10,000 steps；
- 在 MusicBench、GTZAN、NSynth、FMACaps 等任务检查语义和跨模态性能。

随后用稀疏码替代原始 dense embeddings 做 zero-shot 分类/检索，统计每个神经元属于 image/audio only、text only、both 或 neither，并做概念命名和线性 probe 分解。

### 7. 图与结果应该怎样读

- 图 3：GSAE/MGSAE 增加两个模态都激活的神经元，减少 dead/neither。CLIP 设置下，MGSAE 相对 SAE 增加约 35% multimodal neurons、减少约 69% dead neurons。
- 图 4：group-sparse 曲线在跨模态 MMS 上覆盖更长，说明不只是“激活了”，而是更多特征在参照语义空间里保持一致。
- 表中的 zero-shot 结果：CLIP 上 MGSAE 的 CIFAR-10 从 SAE 0.657 提高到 0.842，但仍低于 dense CLIP 0.916；ImageNet 0.373 也明显低于 dense 0.686。稀疏可解释性改进没有完全消除信息损失。
- CLAP 任务中，GSAE 在 GTZAN 为 0.705，接近 dense CLAP 0.710；但不同任务上 GSAE/MGSAE 排名并非完全一致，mask 不是无条件提升。
- 图 5 的 CelebA “blonde” probe：MGSAE 的高贡献概念含 blonde、girl、woman，既找出目标属性，也暴露性别伪相关；这是解释案例，不是对偏差因果来源的完整审计。
- 附录图 6 用 MS COCO 重复 MMS 趋势；图 7 对 “violin” 神经元加值后，文本到音乐的 top retrieval 从无小提琴转向背景/主奏小提琴。这是少量定性 steering 示例，不等于普遍可控性保证。

主图 1–5 和附录图 6–7 均已直接目检；附录 A.1–A.5 与正文位于同一个 `paper.md`，没有独立补充 Markdown。

### 8. 当前代码真正提供什么

固定提交 `60ec6bf5264944d64a4ca271f45a29ebfb9d4946` 的 `saprmarks/dictionary_learning` 提供：

- TopK、BatchTopK、Matryoshka、JumpReLU 等一般 SAE；
- activation buffer 和 `trainSAE` 训练循环；
- TopK reconstruction/auxiliary dead-feature loss；
- decoder 列单位范数约束和相切梯度投影；
- geometric median bias 初始化；
- reconstruction、L0、fraction alive 等通用评估；
- 基础端到端测试。

它没有论文的：

- paired multimodal dataloader；
- $L_{2,1}$ group-sparse loss；
- modality-specific biases；
- shared cross-modal random mask；
- MMS；
- CC3M/JamendoMaxCaps embedding pipeline；
- zero-shot、concept naming、CelebA 和 steering 脚本；
- 论文 checkpoints。

CHANGELOG 中出现的 “GSAE” 是库历史中的 gated SAE 命名语境，不能据此认定存在本论文的 Group-Sparse Autoencoder。对论文核心方法，代码匹配必须标为 **Not found**；只对 TopK 基座和通用训练技巧可标 **Exact/Partial**。

### 9. 适用范围与边界

- 方法要求语义配对数据；没有可靠 pairs 时 group loss 的监督信号不成立。
- 它分解的是已训练多模态 encoder 的 embedding，无法修复 encoder 原本不存在的对齐或概念。
- shared support 提高跨模态一致性，但可能合并模态特有细节；$\lambda$、mask probability 和 $K$ 需要按 reconstruction 与 alignment 权衡。
- Theorem 1 是存在性/构造性结果，不保证 SGD 会找到好解，也不保证固定字典容量下无代价。
- 论文实验使用 CLIP、CLAP、SigLIP2、AIMv2 等通用多模态模型，不是生物信息学研究。
- 本次没有重新训练论文模型；因为核心代码和 checkpoint 未发布，论文数值仅作为论文报告保留。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Decomposing Multimodal Embedding Spaces with Group-Sparse Autoencoders

**Authors**: Chiraag Kaushik (Georgia Tech), Davis Barch (Dolby Labs), Andrea Fanelli (Dolby Labs)
**Venue**: ICLR 2026 (arXiv:2601.20028)
**Code**: https://github.com/saprmarks/dictionary_learning (base SAE toolkit; paper-specific GSAE/MGSAE code not publicly released)

---

### Motivation & Novelty

#### Problem

Sparse autoencoders (SAEs) have emerged as a powerful tool for decomposing neural network embeddings into interpretable concept directions, building on the Linear Representation Hypothesis. When applied to multimodal embedding spaces like CLIP (image/text) or CLAP (audio/text), standard SAEs learn **split dictionaries** — most dictionary vectors activate only for inputs of a single modality. An image of a dog and the caption "a dog" are decomposed into disjoint feature sets, even though CLIP explicitly aligns their embeddings. This split destroys modality alignment in the sparse code space, preventing cross-modal interpretability and control.

#### Limitations of Existing Approaches

- **Standard TopK SAEs** (Gao et al., 2024, arXiv): learn semantic features but most are unimodal, yielding ~65% accuracy on zero-shot CIFAR-10 from sparse codes vs 91.6% from dense CLIP
- **BatchTopK SAEs** (Bussmann et al., 2024, arXiv): batch-level sparsity doesn't solve the split-dictionary problem; 65.7% on CIFAR-10
- **Matryoshka SAEs** (Zaigrajew et al., 2025, arXiv): hierarchical structure helps but 58.7% on CIFAR-10 — worse than standard TopK
- **Post-hoc alignment** (Papadimitriou et al., 2025, arXiv): learn transformations between modality-specific features or identify co-activating pairs, but don't address the root cause
- **Matched pursuit** (Costa et al., 2025, arXiv): increases multimodal concepts but focuses on hierarchical structure, not explicitly mitigating the split phenomenon

#### Unique Contributions

1. **Formal analysis**: Definition of modality-split dictionaries and proof (Theorem 1) that split dictionaries on aligned spaces always admit non-split alternatives — the split is a training bias, not an inherent limitation
2. **Multimodal monoseismicity score (MMS)**: A metric quantifying both semanticity and multimodality of individual dictionary features across modality pairs
3. **Group-sparse autoencoder (GSAE/MGSAE)**: $L_{2,1}$ regularization on paired sparse codes + cross-modal random masking — a principled approach from classical group sparsity theory
4. **First SAE analysis on audio/text** (CLAP embeddings) — prior work focused exclusively on vision-language models

---

### Method Overview

The method modifies standard TopK SAE training to learn multimodal dictionaries from paired data:

1. **Shared architecture**: Single encoder/decoder with modality-specific bias terms ($\boldsymbol{b}_0$, $\boldsymbol{b}_1$) — forces a common concept dictionary
2. **Group-sparse loss**: $\mathcal{L}_{gs}(\boldsymbol{z}_x, \boldsymbol{z}_y) = \sum_i \sqrt{z_{x,i}^2 + z_{y,i}^2}$ — the $L_{2,1}$ mixed norm encourages paired codes to have overlapping support (shared active features)
3. **Cross-modal random masking** (MGSAE): Shared binary mask applied before TopK forces both modalities to select from the same feature subset
4. **Total loss**: $\mathcal{L} = \|\boldsymbol{x} - \hat{\boldsymbol{x}}\|_2^2 + \|\boldsymbol{y} - \hat{\boldsymbol{y}}\|_2^2 + \lambda \cdot \mathcal{L}_{gs}(\boldsymbol{z}_x, \boldsymbol{z}_y)$

Three variants compared: SAE (baseline), GSAE (group-sparse loss only), MGSAE (group-sparse + masking). See doc_method.md for full mathematical details and algorithm walkthrough.

---

### Evaluation

#### Datasets

| Setting | Encoder | Training Data | Validation | Embedding Dim |
|---|---|---|---|---|
| Image/Text | CLIP ViT-B/16 | CC3M (3M pairs) | CC3M val (10K) | 512 |
| Music/Text | LAION CLAP | JamendoMaxCaps | MusicBench (10K) | 512 |

All models: K=32 sparsity, 16× expansion (8192 features), 128 batch size.

#### Dead Neurons (CC3M validation, Figure 3)

| Model | Image only | Text only | Both | Neither (dead) |
|---|---|---|---|---|
| SAE | 1817 | 1316 | 4618 | 441 |
| GSAE | 1025 | 1156 | 5823 | 188 |
| MGSAE | 853 | 973 | 6230 | 136 |

MGSAE achieves **35% more multimodal neurons** and **69% fewer dead neurons** than SAE.

#### Zero-Shot Classification (Sparse Code → Class Label)

| Model | CIFAR-10 | CIFAR-100 | ImageNet |
|---|---|---|---|
| SAE (TopK) | 0.657 | 0.418 | 0.303 |
| BatchTopK | 0.657 | 0.277 | 0.178 |
| Matryoshka | 0.587 | 0.166 | 0.185 |
| **GSAE** | **0.808** | **0.526** | **0.354** |
| **MGSAE** | **0.842** | **0.554** | **0.373** |
| CLIP (dense) | 0.916 | 0.687 | 0.686 |

MGSAE improves over standard SAE by **+18.5pp** on CIFAR-10, **+13.6pp** on CIFAR-100, **+7.0pp** on ImageNet.

#### Audio/Text Zero-Shot (CLAP embeddings)

| Model | GTZAN Genres | NSynth Instruments | FMACaps Retrieval (MRR) |
|---|---|---|---|
| SAE | 0.376 | 0.265 | 0.023 |
| GSAE | 0.705 | 0.303 | 0.050 |
| MGSAE | 0.672 | 0.354 | 0.061 |
| CLAP (dense) | 0.710 | 0.339 | 0.075 |

Remarkably, GSAE nearly matches dense CLAP on GTZAN genres (0.705 vs 0.710) despite being 16× sparser.

#### Cross-Encoder Generalization (Appendix)

Results on SigLIP2 and AIMv2 encoders confirm the method generalizes: MGSAE consistently has the most multimodal neurons and fewest dead neurons across all encoders.

#### Case Study: CelebA Linear Probe Interpretation

When decomposing a "blonde hair" classifier in the MGSAE dictionary, the top contributing concepts are: "blonde", "girl", "woman", "bright" — correctly identifying the true feature and known gender spurious correlation. Standard SAE's top concepts are uninformative due to poor concept naming from unimodal features.

---

### Reproducibility

**Rating: 2/5** (Partial)

#### What's Available
- Base SAE toolkit: `saprmarks/dictionary_learning` — well-maintained, pip-installable, supports TopK/BatchTopK/JumpReLU/Gated/Matryoshka variants
- Paper is detailed on hyperparameters ($\lambda$, mask probability, training steps, batch size, expansion factor)
- Mathematical formulation is complete and self-contained

#### What's Missing
- **GSAE/MGSAE training code not released**: The paper's core contributions (group-sparse loss, cross-modal masking, paired data pipeline) are not in the public repository. The authors used the base library and added custom modifications.
- **No evaluation scripts**: MMS metric computation, zero-shot classification, concept naming, CelebA analysis — none available
- **No pre-trained models**: No checkpoints released
- **No data preprocessing scripts**: CC3M embedding extraction, JamendoMaxCaps preprocessing not provided

#### Reproduction Effort

A researcher would need to:
1. Implement the $L_{2,1}$ loss, cross-modal masking, and modality-specific biases (~200 lines of PyTorch)
2. Write paired embedding data loaders for CC3M and JamendoMaxCaps
3. Implement the MMS evaluation metric
4. Write zero-shot classification evaluation code
5. Obtain CLIP ViT-B/16 and LAION CLAP models + datasets

Estimated effort: **2-3 days** for an experienced PyTorch developer familiar with SAEs. The base library handles ~40% of the infrastructure.

#### Strengths
- Clear mathematical framework grounded in well-studied $L_{2,1}$ group sparsity theory
- Comprehensive evaluation across 2 multimodal settings (image/text, audio/text) and 4 encoders
- Strong experimental gains with minimal architectural changes
- First application of SAEs to audio/text joint embeddings

#### Weaknesses
- Requires paired data at training time — limits applicability to settings with abundant paired samples
- Hyperparameter selection ($\lambda$, mask probability) requires sweep with heuristic stopping criteria
- Zero-shot performance still significantly below dense embeddings (37.3% vs 68.6% on ImageNet)
- No analysis of scaling behavior (only 16× expansion tested in main paper; Table 3 shows 4×/8×/16× with fixed $\lambda$=0.01)
- Theoretical result (Theorem 1) is constructive but non-tight — the added dictionary element per pair leads to $O(n)$ dictionary growth

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
