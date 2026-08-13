---
layout: default
permalink: /paper-atlas/cellfluxrl-55a550f1/
title: "CellFluxRL"
nav: false
description: "CellFluxRL 不是从零训练新的虚拟细胞模型，而是在已训练的 CellFlux 流匹配模型上做奖励驱动的 RL 后训练：同一 control image 与药物条件生成多个候选，用七个生物/结构/形态评分挑出相对好的与差的样本，再让速度场提高高奖励样本、压低低奖励样本的生成倾向。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>arXiv · 2026</span>
    </div>
    <h1>CellFluxRL</h1>
    <p>CellFluxRL: Biologically-Constrained Virtual Cell Modeling via Reinforcement Learning</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2603.21743" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CellFluxRL">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/yuhui-zh15/CellFlux" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellFluxRL">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellFluxRL 中文方法解读

### 一句话理解

CellFluxRL 不是从零训练新的虚拟细胞模型，而是在已训练的 CellFlux 流匹配模型上做奖励驱动的 RL 后训练：同一 control image 与药物条件生成多个候选，用七个生物/结构/形态评分挑出相对好的与差的样本，再让速度场提高高奖励样本、压低低奖励样本的生成倾向。

### 基础 CellFlux

输入是未处理细胞图像 $x_0$ 和药物条件 $c$，目标是生成处理后图像 $x_1$。CellFlux 学习条件速度场 $v_\theta(x_t,t,c)$，沿 ODE 把 control 分布运输到 perturbed 分布。流匹配损失主要约束像素分布，并不直接知道“细胞核必须位于细胞质内”或药物的 MoA 应产生何种形态。

本地 `code/` 只包含这一基础 CellFlux：`training/train_loop.py` 用 conditional OT path 构造中间态/目标速度，UNet 预测速度；`training/eval_loop.py` 以 Heun2、50 NFE 积分并计算 FID。数据加载器从同实验 batch 配对 control/treated 图像并加载药物 embedding。

### 七个奖励

奖励分三组：

- 生物功能：预训练分类器给正确 mechanism-of-action 的概率。
- 结构：Cellpose 分割后，细胞核是否被细胞质包围；核 roundness 是否符合该 MoA 的真实分布。
- 形态统计：核/细胞质最大面积以及核/细胞质数量，相对 MoA 条件真实均值和标准差的负平方标准化偏差。

总奖励是加权和：MoA 权重 5、nucleus-in-cytoplasm 权重 2，其余为 1。奖励既是训练信号、评价指标，也是 test-time best-of-$N$ 的选择器。这种复用带来“按自己的标尺优化再按同一标尺评价”的偏倚，因此 FID/KID、未参与训练的外部生物测量和专家检查仍重要。

### DiffusionNFT 风格后训练

对固定 $(x_0,c)$ 生成一组候选 $\hat x_1^{(i)}$，组内归一化奖励形成相对优势。由于 flow matching 的精确样本似然难算，方法不直接做常规 policy-gradient，而是在 forward interpolation 上构造正/负速度目标，以对比损失推动当前策略靠近高奖励分布并远离低奖励分布。滞后策略 $v^{old}$ 提供数据收集基准，KL 正则限制模型偏离预训练 CellFlux，降低 reward hacking 与图像退化。

“RL”在这里指奖励驱动的在线策略更新，而不是细胞环境中的长时序决策 MDP。候选差异主要来自给 $x_0$ 注入的高斯噪声和数值积分差异。

### Test-time scaling

推断时对同一条件生成 $N$ 个样本，按同一总奖励返回最高者。$N$ 增加会提高找到高分样本的概率，但不改变基础生成分布，也不能证明选择结果更接近真实未测细胞。它以线性增加计算量换取 verifier 分数。

### 结果边界

论文只在 BBBC021 的 MCF-7 三通道、$96\times96$ 图像上测试。CellFluxRL 在七个奖励上优于基础模型，MoA 与结构分数提升，但 FID 从 20.36 变差到 24.01，显示奖励对齐和传统视觉分布质量存在权衡。正文“overall -4.44→-1.54”与 Table 1 “-2.44→0.46”不一致，文档保留该内部矛盾，不替作者推断版本来源。

Cellpose 分割误差会直接污染六个结构/形态奖励；MoA 分类器也可能被对抗性形态利用。单数据集、手工权重、无湿实验验证意味着“biologically meaningful”应理解为更符合这些 evaluator，而不是已证明更准确预测药物生物学。

### 最关键的代码边界

本地仓库是 `https://github.com/yuhui-zh15/CellFlux` 的基础模型快照，而非 CellFluxRL 实现。以下核心贡献均为 **Not found locally**：DiffusionNFT RL loop、七个 reward、Cellpose 评分封装、KL/正负速度损失、best-of-$N$、CellFluxRL checkpoint。旧文档中任何把基础代码当成 RL 实现的表述都应撤回。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellFluxRL: Biologically-Constrained Virtual Cell Modeling via Reinforcement Learning

### Paper Information

- **Authors**: Dongxia Wu\*, Shiye Su\*, Yuhui Zhang\*, Elaine Sui, Emma Lundberg, Emily B. Fox†, Serena Yeung-Levy† (Stanford University)
- **Preprint**: arXiv:2603.21743 (March 2026)
- **Code**: Base CellFlux model at [github.com/yuhui-zh15/CellFlux](https://github.com/yuhui-zh15/CellFlux) (ICML 2025); CellFluxRL RL code not yet released
- **Dataset**: BBBC021 (Broad Bioimage Benchmark Collection)

---

### Motivation & Novelty

#### Problem

Image-based virtual cell models use generative models (flow matching, diffusion) to predict how cell morphology changes under chemical perturbations — aiming to replace expensive wet-lab drug screening. However, existing models produce images that are **visually realistic but biologically implausible**: nuclei appearing outside the cytoplasm, incorrect cell counts, or nuclear shapes inconsistent with the drug's mechanism of action. These failures arise because pixel-level training objectives (flow matching loss) do not enforce higher-level physical and biological constraints.

#### Limitations of Prior Work

- **CellFlux** (Zhang et al., arXiv 2025): State-of-the-art flow matching model for distribution-to-distribution perturbation prediction. Strong FID/KID scores but produces physically impossible structures (Fig. 1 in paper).
- **PhenDiff** (Bourou et al., MICCAI 2024): Diffusion-based phenotype generation. Lower MoA prediction accuracy (0.18 vs CellFlux's 0.26).
- **IMPA** (Palma et al., *Nature Communications* 2025): Perturbation prediction via generative modeling. Lowest structural and morphological scores among baselines.

All prior methods optimize pixel-level objectives without biological constraints.

#### Unique Contributions

1. **RL post-training for virtual cells**: First application of reinforcement learning to align image-based generative cell models with biological constraints, using DiffusionNFT (Zheng et al., arXiv 2025) adapted for source-to-target flow matching.

2. **Seven biologically meaningful rewards** across three categories:
   - Biological function: MoA classification accuracy
   - Structural validity: nucleus-in-cytoplasm containment, nuclear roundness
   - Morphological correctness: nucleus/cytoplasm size and count statistics

These serve triple duty: evaluation metrics, RL training signals, and test-time selection criteria.

3. **Test-time scaling for virtual cells**: Best-of-$N$ selection using the same reward functions, showing monotonic improvements complementary to RL training.

4. **New evaluation framework**: Shifts the field's evaluation paradigm from pixel-level metrics (FID/KID) toward biologically meaningful criteria.

---

### Method Overview

CellFluxRL is a two-stage approach: (1) pretrain a flow matching model (CellFlux) that learns distribution-to-distribution transformations from control to perturbed cells, then (2) post-train with RL using biologically meaningful reward functions.

The base CellFlux model learns a velocity field $v_\theta$ that transports control cell distributions to perturbed cell distributions via flow matching, conditioned on drug fingerprint embeddings. At inference, an ODE is integrated from the control image to produce a predicted treated image.

CellFluxRL applies DiffusionNFT-based RL post-training: at each iteration, multiple candidate images are generated, scored by 7 reward functions, and used to define a contrastive loss that increases the likelihood of high-reward generations while decreasing that of low-reward ones. A KL divergence penalty prevents the model from deviating too far from the pretrained policy.

At inference, test-time scaling further improves quality via best-of-$N$ selection: generate multiple candidates and select the one with the highest combined reward.

See doc_method.md for detailed equations, algorithm walkthrough, and the connection between mathematical formulation and code implementation.

---

### Evaluation

#### Datasets

- **BBBC021**: High-content microscopy perturbation dataset. 98K three-channel fluorescence images (DNA, F-actin, β-tubulin) at 96×96 resolution. 26 chemical perturbations across 12 modes of action (MoA) in MCF-7 breast cancer cells. Train/test split follows CellFlux.

#### Metrics

**Biological rewards** (higher is better):
- MoA: predicted probability of correct mode of action (MoA classification accuracy also reported: 0.61 → 0.66)
- Nuc-in-Cyto: fraction of nuclear area contained within cytoplasm (0.88 → 0.96)
- Roundness: negative z² deviation from MoA-specific roundness distribution
- NucSize, CytoSize: negative z² deviation of max nucleus/cytoplasm area
- NucCount, CytoCount: negative z² deviation of cell density

**Generative quality** (lower is better):
- FID: Fréchet Inception Distance (CellFlux 20.36, CellFluxRL 24.01 — slight trade-off)
- KID: Kernel Inception Distance (CellFlux 0.015, CellFluxRL 0.014 — slight improvement)

#### Key Results (Table 1)

| Metric | PhenDiff | IMPA | CellFlux | CellFluxRL | +TTS (N=4) |
|--------|----------|------|----------|------------|------------|
| MoA | 0.18 | 0.12 | 0.26 | **0.34** | **0.56** |
| Nuc-in-Cyto | 0.91 | 0.79 | 0.88 | **0.96** | **0.97** |
| Roundness | -0.24 | -0.32 | -0.34 | **-0.26** | **-0.19** |
| Overall | -5.20 | -3.19 | -2.44 | **0.46** | **3.15** |
| FID ↓ | 41.94 | 35.70 | **20.36** | 24.01 | 23.19 |
| KID ↓ | 0.028 | 0.029 | 0.015 | **0.014** | 0.016 |

CellFluxRL improves over CellFlux on ALL biological metrics. The overall reward jumps from -2.44 to 0.46 (+TTS: 3.15). The FID trade-off is modest (20.36 → 24.01) while KID slightly improves.

> **Note**: The paper text in §5.2 states "the overall reward improves from -4.44 to -1.54," which does not match Table 1 values (-2.44 → 0.46). The text figures may reflect a different reward weighting scheme or an earlier experimental configuration. We report the Table 1 values here.

#### Ablation Studies

- **Single-reward optimization** (Table 2): Optimizing one reward at a time gives the best score on that metric but limited improvement elsewhere. The combined weighted strategy (CellFluxRL) achieves 2nd or 3rd best on every individual metric.
- **KL weight sensitivity** (Figure 6): Smaller $\beta$ favors structural/morphological metrics; larger $\beta$ slightly benefits biological function. $\beta=1$ provides a reasonable trade-off.
- **Test-time scaling** (Figure 5): Monotonic improvement as $N$ increases from 1 to 16. RL-trained model consistently outperforms the base model at every $N$, with the gap most pronounced at small $N$.

---

### Reproducibility

#### Rating: 2/5 (Low)

**Justification**: The core contribution — CellFluxRL RL training code — is not publicly available. Only the base CellFlux model is released. Without the RL training loop, reward function implementations (especially Cellpose integration), and DiffusionNFT adaptation, the CellFluxRL results cannot be independently reproduced.

#### What IS Available

- Base CellFlux model code ([github.com/yuhui-zh15/CellFlux](https://github.com/yuhui-zh15/CellFlux)): UNet architecture, flow matching training, evaluation pipeline
- BBBC021 dataset: publicly available via Broad Bioimage Benchmark Collection
- Pretrained CellFlux checkpoints on HuggingFace
- MoA classifier training script

#### What IS NOT Available

- CellFluxRL RL training code (DiffusionNFT adaptation)
- 7 reward function implementations (Cellpose integration, MoA reward wrapper, morphological statistics computation)
- Test-time scaling implementation
- CellFluxRL pretrained checkpoints
- Ground truth per-MoA statistics (mean/std for roundness, sizes, counts)

#### Practical Notes

- **Environment**: `environment.yml` provided, requires `flow_matching` (Meta's library), `torchdiffeq`, `pytorch_lightning`
- **Hardware**: Base CellFlux trains on standard GPUs; CellFluxRL RL training used 1 H100 GPU for 32 hours (1200 steps)
- **Data**: BBBC021 pre-processed data available from Zenodo (via IMPA repo)
- **Common pitfall**: The dataset is pre-split; the OOD set (8 compounds) must be excluded from training

#### Strengths

- Clear algorithmic description with pseudocode (Algorithm 1)
- Well-designed reward functions with biological motivation
- Comprehensive ablations (single-reward, KL weight, test-time scaling curves)
- The modular reward framework is easy to extend

#### Weaknesses

- No code release for the core contribution (RL training + rewards)
- Only evaluated on a single, relatively small dataset (BBBC021, 98K images)
- FID slightly degrades after RL training (20.36 → 24.01), suggesting a visual quality trade-off
- All rewards require Cellpose segmentation as a preprocessing step — segmentation errors could propagate
- The reward weights (MoA=5.0, Nuc-in-Cyto=2.0, rest=1.0) appear manually tuned without sensitivity analysis on the weight ratios

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
