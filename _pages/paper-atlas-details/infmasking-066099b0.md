---
layout: default
permalink: /paper-atlas/infmasking-066099b0/
title: "InfMasking"
nav: false
description: "InfMasking 是一种面向多模态“协同信息”的对比学习方法：它不只要求图像、文本、音频等单模态表示彼此一致，而是反复遮住融合 token 的大部分内容，让完整融合表示与许多不同残缺视图保持可辨认的对应关系。有限数量的 masked views 用来估计均值与协方差，再通过 Gaussian 矩母函数得到可训练的近似损失。"
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
      <span>NeurIPS · 2025</span>
    </div>
    <h1>InfMasking</h1>
    <p>InfMasking: Unleashing Synergistic Information by Contrastive Multimodal Interactions</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2509.25270" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## InfMasking 方法中文解读

### 一句话理解

InfMasking 是一种面向多模态“协同信息”的对比学习方法：它不只要求图像、文本、音频等单模态表示彼此一致，而是反复遮住融合 token 的大部分内容，让完整融合表示与许多不同残缺视图保持可辨认的对应关系。有限数量的 masked views 用来估计均值与协方差，再通过 Gaussian 矩母函数得到可训练的近似损失。

### 协同信息为何不同于冗余信息

冗余信息指每个模态单独就能提供的共同语义；唯一信息只存在于一个模态；协同信息则只有组合模态后才出现。例如一张本身无害的图片与一句本身中性的文字，组合后可能成为 hateful meme。CLIP 式跨模态对齐擅长学习冗余，却可能忽略“组合方式”本身。

InfMasking 以 CoMM 为基础：完整融合表示与另一增强视图对齐，同时每个单模态表示也和完整融合表示对齐，以覆盖冗余、唯一性与部分协同。新增 masking 分支专门强化不同部分信息组合仍指向同一完整多模态语义的能力。

### 三类表示其实共享同一个融合网络

每个样本生成两种随机增强 $X',X''$。模态专属 encoder 和 adapter 把输入变成同维 token。代码枚举每个单模态子集以及“全部模态”子集：二模态时是 `[10]、[01]、[11]`，三模态时是三个单模态加 `[111]`（`pl_modules/infmasking.py:58-94`）。

论文 Fig. 1 画成三条 Transformer 路径，容易被读成三套独立参数；实现中所有子集都调用同一个 `InfFusion/FusionTransformer`。因此得到：每个单模态表示 $Z_i$、完整融合表示 $Z$，以及每个子集内部的多次 token-masked 表示。损失实际只取 `prototype=-1`，即全模态分支的 masked views；单模态分支也计算 masked views，但随后没有进入 mask loss，带来额外计算。

### token masking 怎么做

对每个模态的 latent token 独立随机排序，保留比例 $1-\rho$，其余位置替换成可学习 mask token。所有模态 token 拼接，前置 `[CLS]`，经共享自注意力和 LayerNorm 后取 CLS 表示。`models/inffusion.py:148-207` 实现完整与 masked 前向，`223-248` 实现 mask 替换。

遮蔽发生在编码后的 token 空间，不是原始像素或文本字符，因此可以在不同模态 encoder 上复用。高遮蔽率让每个 view 只保留不同的局部组合；太低时任务接近复制完整表示，太高时又可能丢失可识别信息。论文消融显示约 60–80% 更有效，但最优值依赖数据配置。

### “Infinite” 是理论极限，代码仍使用有限 K

概念目标是让完整表示与随机遮蔽分布中的无穷多 views 最大化互信息：

$$
\lim_{K\to\infty}\frac1K\sum_{k=1}^K \widehat I_{NCE}(Z,Z_{mask}^{(k)}).
$$

实际不可能运行无限次。代码由 `num_mask` 生成有限 $K$ 次前向（`inffusion.py:179-182`），再把同一个样本的 $K$ 个 projected masked embeddings 视为来自某一分布的样本。名称“无限 masking”指被解析近似的目标，不代表训练时真的创建无限 views。

### Gaussian 近似与协方差项

对每个样本的 $K$ 个 masked 表示估计

$$
\mu=\frac1K\sum_k z_k,\qquad
\Sigma=\frac1K\sum_k(z_k-\mu)(z_k-\mu)^\top.
$$

若 masked 表示近似 Gaussian，指数内积的期望可用矩母函数解析化。查询 $q$ 的正 logit 包含

$$
q^\top\mu+\frac12q^\top\Sigma q,
$$

而其他样本的 masked views 及 batch 内完整表示成为负例。`losses/infmasking_loss.py:39-92` 直接计算全协方差、正负 logits、交叉熵与额外二次项。

这个近似有三条边界。第一，$K$ 有限且常较小，协方差估计噪声不低；代码除以 $K$ 而非 $K-1$。第二，Gaussian 是工作假设，t-SNE 云团只能提供定性支持，不能证明高维分布严格正态。第三，全 $E\times E$ 协方差成本为 $O(BE^2)$，当前小 embedding 可行，但直接扩到数百或上千维会显著增加显存。

### 总损失如何组合

`InfMaskingLoss.forward` 先对全部表示做 L2 normalize 和带梯度的跨设备 gather。mask loss 分别作用于两种增强的完整融合表示与其 masked views。随后每个单模态及全模态表示都与另一增强的完整融合表示做对称 InfoNCE。可概括为

$$
\mathcal L=\mathcal L_{mask}(Z',\widetilde Z')+
\mathcal L_{mask}(Z'',\widetilde Z'')+
\sum_i\mathcal L_{NCE}(Z_i',Z'')+
\sum_i\mathcal L_{NCE}(Z_i'',Z').
$$

配置可对各项加权，还可启用 entropy penalty。训练后通常冻结 encoder，以完整多模态表示做线性 probe；论文主要衡量表征质量，而不是端到端监督微调效果。

### 代码中最重要的未明示课程学习

代码不是从第一轮就使用固定强度协方差项，而是

$$
ratio=\lambda_{mask}\frac{epoch+1}{max\_epochs}
$$

线性从近零增长到 `mask_lambda`（`infmasking_loss.py:131-138`）。均值对齐与离散负例从开始就存在，协方差贡献逐渐增强。这可能减少早期表示未稳定时的高方差梯度，但论文公式没有清楚呈现该退火；复现时若使用静态权重并不等同于当前代码。

另外，`labels` 和 `CrossEntropyLoss` 直接调用 `.cuda()`，而不是跟随输入 device；CPU 或非 CUDA 后端会失败。投影头使用 SyncBatchNorm，单卡/小 batch 和多 GPU 行为也可能不同。

### 图与实验如何支撑主张

Fig. 1 给出单模态、完整融合和 masked 三类对比关系。Fig. 2 在可控 Trifeature 协同任务上改变 $K$ 与 mask ratio：增加 views 到约 6–8 后收益趋缓，高遮蔽率优于低遮蔽率。附录可视化显示同一样本的 masked embeddings 在完整表示周围形成云团，为 Gaussian 近似提供定性动机。

真实数据覆盖 MultiBench、MM-IMDb 与三模态设置，使用线性 probe 比较 CoMM、FactorCL、CLIP/CMC 等。结果说明新增 loss 在这些任务和配置下有益，但不能从下游准确率反推 PID 意义上的 synergy 被无偏、精确测量；Trifeature 才提供可控的 interaction 标签。详细图解见 `figure_analysis.md`。

### 版本与复现边界

- `.repo_source` 记录克隆提交 `6773ed7e3deea81baae30b4779edca4f9569421f`，当前嵌套仓库 HEAD 为 `206cc19ca89d985245ca204fbc86772e5c2446d0`；本分析以当前可读源码为准并记录漂移。
- 环境依赖 PyTorch、Lightning、Hydra、Transformers、timm 等；数据下载和预处理并非所有 benchmark 都是一键完成。
- 没有预训练 checkpoint；完整重现需要数据、配置、随机种子、多次运行和相同硬件/分布式设置。
- 有限 $K$ 带来额外 Transformer 前向，并且当前共享网络为每个单模态分支也生成最终未使用的 masked views，实际开销高于只计算全模态 mask loss 的最小实现。
- Gaussian 协方差、退火权重、自相似负例和额外二次项都应按当前代码复现，不能只照论文概念式实现。

### 最终理解

InfMasking 的核心不是“遮住输入再重建”，而是把多种残缺融合表示当作同一完整多模态语义的随机观测，用对比学习的均值与协方差信息强化组合依赖。它确实针对协同任务提供了额外训练信号，但“无限”是数学极限，“synergy”是方法动机而非直接可观测量；当前性能还依赖有限采样、Gaussian 假设、退火和共享融合网络的具体实现。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## InfMasking: Unleashing Synergistic Information by Contrastive Multimodal Interactions

**Paper**: arXiv 2509.25270 | NeurIPS 2025
**Authors**: Liangjian Wen, Qun Dai, et al. (Southwestern University of Finance and Economics)
**Code**: https://github.com/brightest66/InfMasking

---

### Motivation & Novelty

#### The Problem

Multimodal learning methods like CLIP [ICML 2021] and ALIGN [ICML 2021] rely on the **multi-view redundancy assumption**: each modality independently contains all task-relevant information, so maximizing their agreement suffices. This assumption holds for image-caption pairs (both describe the same scene) but fails for tasks requiring *synergistic* integration.

Synergy (from Partial Information Decomposition theory) refers to information that emerges **only** when modalities are combined — no single modality carries it. A canonical example: hateful meme detection, where a benign image + neutral caption combine to convey hate that neither modality signals alone.

#### Limitations of Existing Methods

| Method | Journal/Year | Limitation |
|---|---|---|
| CLIP / ALIGN | ICML 2021 | Optimizes for redundancy; ignores synergy and uniqueness |
| FactorCL [Liang et al.] | NeurIPS 2023 | Explicit redundancy/uniqueness decomposition, but cumulative factorization errors; fails synergy |
| CoMM [Dufumier et al.] | ICLR 2025 | Captures all three types but synergy enhancement is indirect, mixed with other terms |
| MAE [He et al.] | CVPR 2022 | Single-modal; generative (reconstruction), not contrastive multimodal |
| CMC [Tian et al.] | ECCV 2020 | Multi-view coding, limited to redundancy-based alignment |

#### InfMasking's Unique Contribution

1. **Dedicated synergy loss term**: $\mathcal{L}_\text{InfMasking}$ directly maximizes the mutual information between partially-masked multimodal representations and their unmasked counterpart — forcing the model to encode information that consistently appears across diverse partial modality combinations.

2. **Infinite masking strategy**: Takes the mathematical limit $K \to \infty$ of random masked views, then derives a tractable closed-form lower bound via Jensen's inequality + Gaussian moment generating function.

3. **Practical efficiency**: No reconstruction decoder, no additional parameters beyond K forward passes through the shared FusionTransformer.

---

### Method Overview

InfMasking augments the CoMM objective with a synergy-specific term. The training pipeline has three parallel branches:

1. **Full fusion branch**: Both augmented views $X'$, $X''$ are fully encoded → $Z'$, $Z''$ (captures R+S+U)
2. **Unimodal branch**: Each modality encoded alone → $Z_i$ (captures R+U_i)
3. **Masked branch**: Feature tokens are randomly masked at ratio ρ (50-80%), K times → $Z_\text{mask}^{1\ldots K}$ (captures synergy through diverse partial views)

The **InfMasking loss** aligns $Z'$ with its K masked counterparts by maximizing mutual information, approximated via a Gaussian lower bound:
- Estimate $\boldsymbol{\mu}, \boldsymbol{\Sigma}$ of masked representations from K samples
- Compute positive logit as $z'^T(\boldsymbol{\mu} + \frac{1}{2}\boldsymbol{\Sigma}z'/\tau)$ (incorporating variance)
- Optimize via cross-entropy against K masked negatives + quadratic variance term

**Key architectural choices**:
- Transformer fusion (1 layer, 8 heads for bimodal; 2 layers for trimodal)
- Learnable [CLS] token for global representation
- 3-layer MLP projection head (embed_dim=40 → 512 → 256)
- Token masking in latent space, not raw input — modality-agnostic

---

### Evaluation

#### Synthetic Validation (Trifeature)

Controlled benchmark with ground-truth interaction types. InfMasking outperforms all baselines:

| Model | Redundancy↑ | Uniqueness↑ | Synergy↑ |
|---|---|---|---|
| CLIP/Cross [ICML 2021] | 100.0 | 11.6 | 50.0 |
| FactorCL [NeurIPS 2023] | 99.8 | 62.5 | 46.5 |
| CoMM [ICLR 2025] | 99.9 | 86.8 | 71.4 |
| **InfMasking** | **99.9** | **90.6** | **77.0** |

CoMM→InfMasking: +5.6% synergy, +3.8% uniqueness.

#### MultiBench 2-Modality (7 datasets)

All results are linear probing on frozen representations:

| Method | V&T EE (MSE↓) | MIMIC (acc↑) | MOSI (acc↑) | UR-FUNNY (acc↑) | MUSTARD (acc↑) | Avg (cls)↑ |
|---|---|---|---|---|---|---|
| FactorCL | 10.82 | 67.3 | 51.2 | 60.5 | 55.8 | 58.7 |
| CoMM | 7.96 | 66.4 | 63.7 | 63.3 | 64.4 | 64.45 |
| **InfMasking** | **4.23** | **68.1** | **69.0** | **64.3** | **66.8** | **67.05** |

InfMasking outperforms CoMM on all 5 datasets; MOSI improvement (+5.3%) is most dramatic.

#### MM-IMDb (Multi-label Movie Genre, Image+Text)

| Method | Weighted F1↑ | Macro F1↑ |
|---|---|---|
| CoMM (CLIP backbone) | 61.29 | 53.79 |
| **InfMasking (CLIP backbone)** | **62.60** | **55.93** |

#### 3-Modality Extension

| Dataset | CoMM | InfMasking |
|---|---|---|
| V&T Contact Pred. | 94.1 | 94.1 |
| UR-FUNNY (V+T+A) | 64.8 | **65.6** |

#### Ablation: Loss Components

The full loss (all three terms, $\lambda_1=\lambda_2=\lambda_3=1$) achieves the best average performance. Removing $\mathcal{L}_\text{InfMasking}$ drops synergy from 77.0% to 71.4%. Removing the cross-modal term further drops to 58.7%.

---

### Reproducibility

**Rating: 3/5**

**Strengths**:
- Code is publicly released with full configs for all 7 benchmarks
- Hyperparameters fully specified in Appendix A (Table 6) and configs/
- 5-run statistics (seeds 42-46) reported throughout
- MultiBench preprocessing and encoders follow published CoMM settings (reproducible baseline)

**Weaknesses**:
- The key annealing schedule (`ratio = mask_lambda × epoch/max_epochs`) is not mentioned anywhere in the paper — a user following the paper alone would implement a static weight
- MM-IMDb trains on raw data (not pre-extracted features); requires custom preprocessing
- No pre-trained checkpoints provided
- `environment.yml` specifies PyTorch 2.1 + CUDA 11.8; compatibility with newer CUDA may require adjustment
- Proof of Appendix G (Lemma 3) involves Jensen + MGF steps not explicitly verified in code

**Practical setup**:
```bash
conda env create -f environment.yml
conda activate multimodal
# Download MultiBench data per dataset/multibench.py instructions
bash run_scripts/trifeatures_run.sh  # Synthetic validation
bash run_scripts/multibench_run.sh   # Real-world 2-modality
bash run_scripts/all-mod_run.sh      # 3-modality
```

**Common pitfalls**:
- embed_dim=40 is small; the quadratic covariance [B, E, E] requires E≤~64 to stay memory-efficient on a 24GB GPU
- mask_lambda schedules differ per dataset (implicit in epoch count × mask_lambda product)
- `mask_lambda` in config (=1 by default) is the *maximum* value; actual weight is 0 at epoch 0

---

### Key Limitations

1. **No formal theoretical characterization of synergy coverage**: The paper acknowledges it cannot formally prove that $\mathcal{L}_\text{InfMasking}$ captures all synergistic information.

2. **Scalability to high-dimensional embeddings**: Full covariance matrix is O(E²) per sample; large embed_dim (e.g., E=512 for CLIP-scale) would require diagonal approximation.

3. **Primarily validated on MultiBench pre-processed features**: Most datasets use pre-extracted features (not end-to-end training), limiting conclusions about representation transfer at scale.

4. **No pre-training then fine-tuning evaluation**: All experiments are self-supervised representation learning + linear probing. Applicability to large-scale pre-training (e.g., CLIP-scale) is not demonstrated.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
