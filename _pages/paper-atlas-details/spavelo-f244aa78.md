---
layout: default
permalink: /paper-atlas/spavelo-f244aa78/
title: "spaVelo"
nav: false
description: "RNA velocity 需要利用未剪接 RNA（unspliced）和已剪接 RNA（spliced）的相对关系来推断表达变化方向。传统 scVelo、VeloVI、VeloVAE 和 Dynamo 主要面向解离的单细胞数据，把 spot/cell 当成相互独立的样本；TopoVelo 和 spVelo 虽然加入空间信息，但空间图的构建与动力学拟合是解耦的。spaVelo 的目标是让空间依赖和 RNA 动力学在同一个生成模型中联合学习。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Bioinformatics · 2026</span>
    </div>
    <h1>spaVelo</h1>
    <p>A dependency-aware deep generative model for inferring RNA velocity from spatial transcriptomics</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1093/bioinformatics/btag270" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## spaVelo：从空间转录组推断 RNA velocity

### 1. 它要解决什么问题？

RNA velocity 需要利用未剪接 RNA（unspliced）和已剪接 RNA（spliced）的相对关系来推断表达变化方向。传统 scVelo、VeloVI、VeloVAE 和 Dynamo 主要面向解离的单细胞数据，把 spot/cell 当成相互独立的样本；TopoVelo 和 spVelo 虽然加入空间信息，但空间图的构建与动力学拟合是解耦的。spaVelo 的目标是让空间依赖和 RNA 动力学在同一个生成模型中联合学习（paper.md:25-35）。

### 2. 核心直觉

对每个 spot、每个基因，spaVelo 同时估计：

- 一个空间相关的潜变量表示；
- 基因处于诱导、诱导稳态、抑制或抑制稳态中的概率；
- 基因特异的潜在时间；
- 空间调制因子 $\rho$，用来改变局部转录速率。

动力学方程是

$$\frac{du}{dt}=\rho\alpha-\beta u,\qquad \frac{ds}{dt}=\beta u-\gamma s.$$

因此空间位置不是事后画图或预处理得到的附加信息，而是通过 GP 先验影响 latent representation，再影响 $\rho$、状态概率和时间，最后影响 velocity（paper.md:44-52, 100-132）。

### 3. 从输入到输出

```text
spliced + unspliced + spatial coordinates
        │
        ├─ 预处理、缩放、速度基因筛选、Dynamo 状态先验
        │
        ├─ Encoder([spliced, unspliced]) -> 高斯后验参数
        │       ├─ 前 L 维：坐标条件下的 sparse GP posterior
        │       └─ 其余维：标准 Gaussian posterior
        │
        ├─ sample z
        ├─ Decoder(z) -> state probabilities π, rho, tau
        ├─ 四个动力学状态的闭式解 -> u/s mixture likelihood
        ├─ reconstruction + GP KL + Gaussian KL + state KL + switch penalty
        └─ posterior decoding -> pred_velocity, pred_t, state, rho, pred_s, pred_u
```

代码中的 `SPAVELO.__init__` 创建 sparse GP、encoder、全局动力学速率和每基因 switch time（spaVelo/spaVelo.py:104-180）。`encoder_inference` 把 GP latent 与普通 Gaussian latent 拼起来（spaVelo/spaVelo.py:287-364）。`get_px` 用 `alpha * alpha_rho` 形成 spot-specific transcription rate，并组合诱导/抑制状态（spaVelo/spaVelo.py:493-520）。

### 4. 为什么需要四个状态？

诱导阶段表达从低值上升；诱导稳态接近 $u=\rho\alpha/\beta$、$s=\rho\alpha/\gamma$；抑制阶段停止转录，未剪接和已剪接 RNA 按 $\beta$、$\gamma$ 衰减；抑制稳态趋近于零。每个状态都有闭式解，代码对应 `spaVelo.py:_get_induction_unspliced_spliced` 和 `_get_repression_unspliced_spliced`（spaVelo/spaVelo.py:582-620）。

### 5. 训练目标

论文将目标写成

$$L_{total}=-ELBO+\beta KL(q(\pi)||p(\pi))+\lambda L_{switch}.$$

其中 ELBO 包括 spliced/unspliced 重构项、空间 GP latent 的 KL 和普通 Gaussian latent 的 KL；$p(\pi)$ 可以来自 Dynamo 的 U-S phase portrait，也可以退化为均匀 Dirichlet 先验；switch penalty 约束推断的 switch point 与表达分位数估计一致（paper.md:143-239）。

代码还实现了一个论文没有单独强调的 denoising latent consistency KL：把拟合表达再次送入 encoder，并约束其 latent distribution 接近原始 posterior（spaVelo/spaVeloDenoise.py:95-108）。另一个必须注意的差异是：代码先计算 warm-up penalty weight，随后在 `spaVeloDenoise.py:125-128` 将其覆盖为常数 1，所以不能直接把论文的动态 penalty 调度当成当前代码行为。

### 6. 输出和评估

真实数据 runner 将结果写入 AnnData：`pred_velocity`、`pred_t`、`state_prob`、`state`、`rho`、`pred_s`、`pred_u` 和 `likelihood`，并保存 `spavelo_adata.h5ad`（spaVelo/experiments/run_spaVelo_real_deno.py:172-216）。论文用模拟数据、axolotl 脑、OSCC 和 thymus 数据评估，并用 $k$-CBDir 衡量跨边界方向正确性（paper.md:251-261）。

### 7. 阅读时的边界

论文声称的 CellRank2 reverse-diffusion latent-time 流程在 runner 中以 `get_cell_latent_time` 被调用，但本次代码核查没有把该函数的完整实现和论文描述逐行对应起来；应标为 Partial。补充 PDF 已获取，但尚未转换为 markdown，因此 supplement-only 的表格和图仍属于未完整审计证据。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## spaVelo: summary

### Problem and contribution

Spatial transcriptomics provides expression together with tissue coordinates, but most RNA-velocity models treat observations as independent. spaVelo is a spatial variational autoencoder that couples RNA kinetics with spatially structured latent variation and a spot-specific transcription-rate multiplier $\rho$.

### Method in one paragraph

The model encodes concatenated unspliced/spliced expression into a hybrid latent vector: GP dimensions receive a sparse variational GP prior over coordinates, while the remaining dimensions use a standard Gaussian prior. A decoder predicts transcription-state probabilities, state-specific latent times, and $\rho$. These quantities parameterize closed-form induction, induction-steady, repression, and repression-steady solutions of the unspliced/spliced kinetic ODEs. A mixture likelihood reconstructs both modalities; training combines reconstruction, GP/normal KL terms, a state-prior KL term, and a switch-point penalty.

### Evaluation

The paper evaluates one 3,000-spot/1,000-gene simulation, axolotl Stereo-seq brain sections, OSCC Visium slices, and a thymus dataset. Baselines include scVelo, veloVI, STT, TopoVelo, and Dynamo. The main direction metric is $k$-CBDir. On the reported simulation, spaVelo obtains 0.4350 versus 0.4238 for TopoVelo; on axolotl stage 57 it obtains 0.5855 versus 0.3456 for STT; on OSCC slice s5 it obtains 0.1849 versus 0.2841 for STT (paper.md:265-297). The ablation supports both GP and $\rho$, although the double ablation is not uniformly worst on every OSCC $k$ setting (paper.md:330-348).

### Reproducibility

The paper and code are available locally. The cloned repository at commit `0d695ea0fb23a01909361f9f372034febed18532` contains the core model and real-data runner. The runner writes velocity, latent time, state probabilities, $\rho$, fitted expression, likelihood, and an `.h5ad` artifact (spaVelo/experiments/run_spaVelo_real_deno.py:172-216). Fidelity is medium-high for the core model, but the paper's prose and implementation differ in training defaults and penalty scheduling; see `doc_code.md`. The supplementary PDF is present but not converted to markdown; supplement-only numeric details remain only partially audited.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
