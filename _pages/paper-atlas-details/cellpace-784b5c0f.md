---
layout: default
permalink: /paper-atlas/cellpace-784b5c0f/
title: "CellPace"
nav: false
wide: true
description: "CellPace 把不同发育阶段的单细胞群体先编码到 scVI/MultiVI 潜空间，再把若干阶段组成有顺序的短序列，用 causal Transformer 同时学习每个位置的扩散去噪。它不追踪同一个真实细胞，而是生成与各时间点群体分布一致的“虚拟细胞序列”，用于已观测阶段模拟、缺失阶段插值和训练范围外短期预测。"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>CellPace</h1>
    <p>CellPace: A temporal diffusion-forcing framework for simulation, interpolation and forecasting of single-cell dynamics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.02.25.707938" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CellPace">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Emad-COMBINE-lab/CellPace-release" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellPace">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellPace 中文方法解读

### 一句话理解

CellPace 把不同发育阶段的单细胞群体先编码到 scVI/MultiVI 潜空间，再把若干阶段组成有顺序的短序列，用 causal Transformer 同时学习每个位置的扩散去噪。它不追踪同一个真实细胞，而是生成与各时间点群体分布一致的“虚拟细胞序列”，用于已观测阶段模拟、缺失阶段插值和训练范围外短期预测。

### 两阶段架构

#### 1. VAE 表示

RNA 数据由 scVI、RNA+ATAC 由 MultiVI 编码为连续 latent。扩散模型在 latent 而不是原始计数上训练，生成后再经 VAE decoder 回到基因/可及性空间。因此最终表达质量同时受 VAE 信息瓶颈与时序模型影响；潜空间距离好不保证每个基因都准确。

#### 2. Temporal Diffusion Forcing

训练样本是一段按阶段排列的 latent sequence。每个位置独立抽取噪声等级，模型看到前面较干净或较嘈杂的上下文，预测各位置的扩散目标。causal mask 保证位置 $t$ 不能读取未来位置，避免预测时信息泄漏。

每个位置还带连续时间信息：归一化 stage position 与相邻阶段 gap。这样 somite 10→11 和 10→15 不再被当成同样的一步。代码在 `model/dif/core.py:140-163` 拼接 position/gap，在 `transformer.py:144-199` 生成 causal mask；Min-SNR 权重位于 `diffusion.py:286-348`。

### Diffusion Forcing 与普通条件扩散的差别

普通条件扩散常把“时间点”当类别，从噪声独立生成一个阶段。CellPace 将多个发育位置放在同一序列，并让每个位置具有独立 diffusion time。早期位置可以先变干净，为后续位置提供 context；模型因而学习跨阶段依赖，而不仅是 stage label 到分布的映射。

这仍是 population-level 生成：序列中相邻 latent 不一定来自同一生物细胞或同一克隆。论文的 trajectory preservation 是分布、伪时间、marker/GRN 等统计一致性，不应改写为实验 lineage reconstruction。

### Pyramid denoising

推断时 pyramid schedule 让较早位置先降低噪声，较晚位置保持更久的不确定性。代码矩阵的高度为

$$H=T_{sample}+\lfloor(horizon-1)\,u\rfloor,$$

其中 $u$ 是 uncertainty scale；每一列按位置错开去噪，并删除相邻重复行（`model/dif/inference.py:607-638`）。滑动窗口把已生成位置作为 context，扩展到更长序列。代码还实现 full-sequence、autoregressive、trapezoid 调度，但论文主体聚焦 pyramid。

### 三种任务怎样区分

- Simulation：在训练见过的阶段从噪声生成群体。
- Interpolation：训练时留出中间阶段，在已见前后阶段之间生成。
- Forecasting：生成晚于训练最后阶段的细胞。它比插值更难，因为没有右侧观测约束。

对 forecasting 的结论应限制在论文测试的短距离外推。Transformer 学到的趋势可能在更远时间累积偏差；模型也不能自动处理新出现、训练中完全没有的生物机制。

### 证据与局限

论文在胚胎多个谱系和 mouse palate RNA+ATAC 上比较分布距离、miLISI、MMD、energy distance、pseudotime/marker、空间映射、GRN 与 PAGA。多指标一致增强可信度，但许多验证仍复用从同一表达数据计算的结构，并非独立 lineage tracing。

本地代码对 VAE→DiF→generation 主链覆盖度高，但完整论文复现仍为 Partial：全量数据链接在论文快照中尚未落实；baseline 训练/统一评估脚本不完整；CLI 强制 GPU 与 fp16；配置/缓存哈希和 stage preprocessing 必须匹配。代码中的非默认 AdamW betas、gradient clipping 和多种调度属于实现细节，不应被误写为论文普遍结论。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellPace — Summary

### Paper Information

- **Title**: CellPace: A temporal diffusion-forcing framework for simulation, interpolation and forecasting of single-cell dynamics
- **Authors**: Chen Su, Amin Emad
- **Affiliation**: McGill University, Mila Quebec AI Institute
- **Journal**: bioRxiv (preprint, 2026)
- **DOI**: 10.64898/2026.02.25.707938
- **Code**: https://github.com/Emad-COMBINE-lab/CellPace-release

---

### Motivation & Novelty

#### Biological Problem

Single-cell sequencing captures snapshots of cellular heterogeneity at single-cell resolution, but each assay destroys the measured cell. In developmental studies, cells are sampled at discrete, often irregularly spaced timepoints, producing disjointed cross-sectional measurements rather than continuous trajectories. Intermediate states may be missing or sparsely sampled, and future states are never directly observed.

#### Limitations of Existing Approaches

- **Trajectory inference** (PAGA, *Genome Biology* 2019; CellRank2, *Nature Methods* 2024): Organizes observed cells but cannot generate profiles for missing states
- **Neural ODE/SDE** (scNODE, *Bioinformatics* 2024; scIMF, *arXiv* 2025): Learns continuous dynamics but requires real cells at the starting timepoint; assumes autonomous cell-level dynamics
- **Generative models** (scDiffusion, *Bioinformatics* 2024; cfDiffusion, *Briefings in Bioinformatics* 2025; ESCFD, *KDD* 2025; CFGen, *arXiv* 2024): Generate cells from noise but treat time as a categorical label — fundamentally unable to interpolate missing intermediates or extrapolate to unobserved future stages

#### Unique Contributions

CellPace is the first diffusion-based framework that simultaneously supports:
1. **Simulation** — generating realistic cells at observed developmental stages from noise
2. **Interpolation** — generating cells at unseen intermediate timepoints
3. **Temporal forecasting** — predicting future cellular states beyond the training range

The key technical innovation is **Temporal Diffusion Forcing (TDiF)**: a transformer-based diffusion backbone with gap-aware continuous temporal encodings that explicitly model irregular sampling intervals. Combined with a causally-masked architecture and pyramid denoising schedule, CellPace learns population-level dynamics across arbitrary temporal intervals.

---

### Method Overview

CellPace uses a two-stage approach:

1. **VAE encoding**: A pretrained scVI (or MultiVI for multiome data) encodes raw counts into a 256-dimensional latent space, handling sparsity and overdispersion via ZINB likelihood
2. **Temporal Diffusion Forcing**: A Transformer with causal attention and AdaLN conditioning learns to denoise latent sequences. The model receives:
   - Per-position noise levels (independent, not shared)
   - Gap-aware temporal features: normalized developmental position $\tau_t \in [0,1]$ and inter-stage time gap $\Delta_t$
   - Min-SNR weighted MSE loss for balanced optimization

At inference, pyramid scheduling denoises earlier positions first, providing clean context for generating future states. A sliding window approach enables arbitrary-length sequence generation. DDIM sampling with 200 steps (from 1000 training steps) provides efficient inference.

See `doc_method.md` for full mathematical details and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Datasets

| Dataset | Cells | Stages | Source |
|---|---|---|---|
| Retinal progenitor cells (RPC) | 35,275 | 31 somite stages | Qiu et al., *Nature* 2024 |
| Epithelial cells | ~54,000 | Multiple somites | Qiu et al., *Nature* 2024 |
| Endothelial progenitor cells | ~9,000 | Multiple somites | Qiu et al., *Nature* 2024 |
| Posterior embryo (multi-lineage) | ~121,000 | Somite 0-34 | Qiu et al., *Nature* 2024 |
| Mouse palate multiome (RNA+ATAC) | 36,154 | 50 pseudotime bins | Yan et al., *Nature Communications* 2024 |

#### Metrics

- **miLISI** (median Local Inverse Simpson Index): mixing quality (higher = better, max 2.0)
- **2-Wasserstein / 1-Wasserstein**: distributional distance in PCA space (lower = better)
- **MMD** (Maximum Mean Discrepancy): multi-scale kernel distance (lower = better)
- **Energy distance**: distributional fidelity for 8 statistical properties
- **KS statistic**: per-stage pseudotime distribution comparison

#### Baselines (6 methods)

| Method | Type | Interpolation | Extrapolation | Requires Starting Cells |
|---|---|---|---|---|
| scDiffusion (*Bioinformatics* 2024) | Latent diffusion | Yes | No | No |
| cfDiffusion (*Brief. Bioinf.* 2025) | Classifier-free diffusion | Post-hoc | Post-hoc | No |
| ESCFD (*KDD* 2025) | Flow + diffusion | Post-hoc | Post-hoc | No |
| CFGen (*arXiv* 2024) | Flow matching | Post-hoc | Post-hoc | No |
| scNODE (*Bioinformatics* 2024) | Neural ODE | Yes | Yes | **Yes** |
| scIMF (*arXiv* 2025) | Neural SDE | Yes | Yes | **Yes** |

#### Key Results

1. **Simulation**: CellPace achieves best overall rank across RPC, epithelial, endothelial, and posterior embryo datasets (Fig. 1f)
2. **Interpolation**: Lowest W2 distance at all difficulty levels (easy/moderate/hard) on RPC data; preserves statistical properties (energy distance; Fig. 3d)
3. **Extrapolation**: Lowest W2 distance for forecasting somite stages 33-34; high miLISI (>1.8)
4. **Trajectory preservation**: Pearson r=0.98 for pseudotime correlation with real data; lowest mean KS statistic
5. **Biological validation**:
   - Marker gene dynamics preserved (Pax2, Pax6, Rax stable; Otx2, Six3 decreasing; Mitf, Trpm1 increasing)
   - Spatial mapping to MOSTA atlas: Pearson r≥0.93 between real and generated cell-type enrichments
   - GRN topology (degree distributions) and regulon dynamics (Etv4 ρ=0.98, Hoxa10 ρ=0.90) preserved
   - PAGA topology: IM distance improved from 0.186 (ablated) to 0.089 (CellPace-augmented) for interpolation
6. **Multimodal**: Joint RNA-ATAC generation outperforms CFGen, especially in extrapolation (miLISI 1.85 vs 1.37; Fig. 5d-e)

---

### Reproducibility

**Rating: 4/5** — High reproducibility with minor caveats.

#### Strengths
- **Complete codebase**: Well-organized Python package with CLI, config files, and demo data
- **Documented pipeline**: Clear two-stage training → generation workflow
- **Demo included**: Subsampled retinal data (50 cells/stage, 100 HVGs) for quick testing (~15 min total)
- **Config-driven**: All hyperparameters in YAML, supporting config overrides from command line
- **Reproducible sequences**: 1M pregenerated training sequences cached to disk with hash validation

#### Weaknesses
- **Full data not yet available**: Zenodo link pending ("will be available"). Only demo data in repo
- **Supplementary Note 1 unavailable**: Full hyperparameters referenced but not in preprint
- **GPU required**: CUDA mandatory; tested on RTX 3090 only
- **Benchmark code not included**: Baseline method training/evaluation scripts not provided
- **scvi-tools version dependency**: Requires scvi-tools 1.4.0+ with specific PyTorch/CUDA versions

#### Practical Notes
- **Environment**: Conda/Mamba with Python 3.12, PyTorch 2.5.1, CUDA 11.8
- **Memory**: Mixed precision (fp16) helps; batch generation with configurable batch_size for OOM prevention
- **Training time**: Demo ~15 min (10K steps, 2 GPUs); full data ~30-60 min (20K steps)
- **Common pitfall**: Must use `layers["raw_counts"]` for input; normalized/log-transformed data will fail

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
