---
layout: default
permalink: /paper-atlas/latentvelo-06ca20ef/
title: "LatentVelo"
nav: false
wide: true
description: "LatentVelo 解决的是单细胞 RNA-seq 快照数据中的 RNA velocity 和细胞轨迹推断问题。传统 RNA velocity 的目标是利用未剪接 RNA u 和已剪接 RNA s 的关系，估计细胞未来分化方向 ds/dt。经典模型写作： \\frac{dug(t)}{dt}=\\alphag(t)-\\betag ug(t) \\frac{dsg(t)}{dt}=\\betag ug(t)-\\gammag sg(t) 这里 g…"
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
      <span>Cell Reports Methods · 2023</span>
    </div>
    <h1>LatentVelo</h1>
    <p>Inferring single-cell transcriptomic dynamics with structured latent gene expression dynamics</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Spencerfar/LatentVelo" target="_blank" rel="noopener noreferrer" aria-label="Open code for LatentVelo">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## LatentVelo 方法中文解释

### 1. 这篇论文要解决什么问题？

LatentVelo 解决的是单细胞 RNA-seq 快照数据中的 RNA velocity 和细胞轨迹推断问题。传统 RNA velocity 的目标是利用未剪接 RNA `$u$` 和已剪接 RNA `$s$` 的关系，估计细胞未来分化方向 `$ds/dt$`。经典模型写作：

`$\frac{du_g(t)}{dt}=\alpha_g(t)-\beta_g u_g(t)$`

`$\frac{ds_g(t)}{dt}=\beta_g u_g(t)-\gamma_g s_g(t)$`

这里 `$g$` 是基因，`$\alpha,\beta,\gamma$` 分别对应转录、剪接和降解速率（`paper.md:41-50`）。问题在于，Velocyto 和 scVelo 等方法对这些速率和动力学形式有较强假设；当出现多谱系分化、时间变化速率、转录 boost、弱 unspliced 信号或批次效应时，这些假设可能不够灵活（`paper.md:27-39`）。

### 2. LatentVelo 的核心思想

LatentVelo 的关键想法是：不直接在高维基因空间里强行拟合线性动力学，而是先把细胞压缩到低维潜在空间，再在潜在空间里学习带生物结构约束的神经 ODE 动力学（`paper.md:51-76`）。

它把输入的已剪接和未剪接表达分别编码为潜变量：

- `$\hat z_s$`：spliced RNA 的潜在状态；
- `$\hat z_u$`：unspliced RNA 的潜在状态；
- `$\hat t$`：每个细胞的潜在发育时间；
- `$h$`：由当前细胞状态推断出的条件变量，用来控制该细胞走哪条分化分支；
- `$z_r$`：潜在调控状态，用来表示谱系相关的动力学模式。

代码中，`VAE.latent_embedding` 采样 `$z_s,z_u$`，再通过 `encoder_t` 得到 latent time，通过 `encoder_c` 得到 `context/h`（`LatentVelo_code/latentvelo/models/vae_model.py:369-425`）。

### 3. 结构化潜在动力学

论文的非结构化形式是：

`$\frac{dz(t)}{dt}=f(z(t),h)$`

其中 `$f$` 是神经网络，ODE 从学习到的初始状态 `$z_0$` 出发，积分到每个细胞的 `$\hat t$`，得到 `$z(\hat t)$`，并要求它接近编码器直接给出的 `$\hat z$`（`paper.md:53-56`, `paper.md:211-225`）。

为了保留 RNA velocity 的因果结构，LatentVelo 进一步把潜在空间拆成 spliced、unspliced 和 regulatory 三部分：

`$\frac{dz_u(t)}{dt}=f_u(z_u(t),z_r(t))$`

`$\frac{dz_s(t)}{dt}=f_s(z_u(t),z_s(t))$`

`$\frac{dz_r(t)}{dt}=f_r(z_s(t),z_r(t),h)$`

`$h=f_h(\hat z_s,\hat z_u)$`

这表示：unspliced 动力学受调控状态 `$z_r$` 影响；spliced 动力学受 unspliced 和自身状态影响；调控状态又由 spliced、regulatory state 和细胞特异的 `$h$` 决定（`paper.md:57-67`）。代码中的 `VelocityFieldReg.forward` 直接实现了这个结构：它切分 `zs, zu, zr, h`，计算 `spliced_drift`、`unspliced_drift` 和 `reg_drift`，并把 `$h$` 的导数设为 0，因此 `$h$` 是沿轨迹不变的条件变量（`LatentVelo_code/latentvelo/models/velocity_field.py:42-58`）。

### 4. 训练目标

LatentVelo 是 VAE，所以训练目标同时包含重构项、KL 正则项和动力学轨迹匹配项。论文给出的损失为：

`$L=-E_{\hat z,\hat t\sim q}[\text{logNormal}(x|\mu(\hat z),\sigma)]+\text{KL}(q\Vert p)-E_{\hat z,\hat t\sim q}[\text{logNormal}(x|\mu(z(\hat t)),\sigma)-\text{logNormal}(\hat z|z(\hat t),\sigma_z)]$`

第一部分是普通 VAE 的重构和 KL；第二部分要求 ODE 轨迹终点 `$z(\hat t)$` 解码后也能重构输入，并且 `$z(\hat t)$` 接近编码器给出的 `$\hat z$`（`paper.md:219-225`）。代码中的 `VAE.loss` 会计算编码状态和 ODE 状态的解码结果、Gaussian/NB likelihood、latent matching、KL warmup，以及可选的 root/time/correlation regularization（`LatentVelo_code/latentvelo/models/vae_model.py:192-356`）。

### 5. 基因空间速度与生物方向约束

虽然核心模型在潜在空间里估计 velocity，但论文也可以把潜在速度映射回基因空间：

`$\dot s=JD_sf_s(z_s,z_u)$`

也就是用 spliced decoder 的 Jacobian-vector product，把潜在空间速度变成基因表达速度（`paper.md:75`, `paper.md:235-249`）。代码在 `output_results.py` 里用 `torch.autograd.functional.jvp` 实现这个映射，并在 `gene_velocity=True` 时输出 `velo_s`、`velo_u` 和 `velo`（`LatentVelo_code/latentvelo/output_results.py:39-72`, `LatentVelo_code/latentvelo/output_results.py:138-168`）。

论文还用弱正则约束 splicing 方向：

`$\lambda_{su}\mathrm{corr}(\dot s,u)+\lambda_{ss}\mathrm{corr}(\dot s,-s)$`

直觉是：spliced velocity 应该与 unspliced 信号正相关、与当前 spliced 水平负相关，从而保留“未剪接 RNA 变成已剪接 RNA”的方向性（`paper.md:241-249`）。代码中 `corr_reg_func` 用 decoder JVP 得到 gene velocity，再计算这些相关性并加入 loss（`LatentVelo_code/latentvelo/models/vae_model.py:527-694`）。

### 6. 批次校正如何实现？

LatentVelo 的批次校正不是先校正基因矩阵再跑 velocity，而是在模型内部完成：batch ID 输入 encoder 和 decoder，但潜在动力学本身不接收 batch ID，因此学习到的动力学空间被鼓励为 batch-independent（`paper.md:271-278`）。代码中，batch one-hot 会拼接到编码器输入，线性 decoder 可按 batch 使用不同 decoder；但 `VelocityFieldReg` 不含 batch 输入（`LatentVelo_code/latentvelo/models/vae_model.py:135-173`, `LatentVelo_code/latentvelo/models/velocity_field.py:5-75`）。

### 7. 结果和图像证据

- Figure 1 展示了完整模型结构、合成 bifurcation 上的 latent velocity、latent time、`$z_r$` lineage separation、cell-specific trajectories 和 batch correction。
- Figure 2 在胰腺内分泌分化数据上显示 alpha/beta/delta/epsilon 终末状态的轨迹，并用 `$z_r$` 区分不同终末谱系。
- Figure 3 在 MEF reprogramming 中显示 LatentVelo 的 `$z_r$` 能区分 reprogrammed 与 dead-end 状态，并生成分叉轨迹。
- Figure 4 展示合成批次效应和 segmentoid 数据中的 batch correction 与 velocity 指标。
- Figure 5 展示 mouse gastrulation 这种大规模多谱系系统中的轨迹。
- Figure 6 用 synthetic 和 real datasets 比较 LatentVelo 与 scVelo 的 velocity cosine、CBDir、ICCoh 和运行时间。

这些图像已从本地 `images/` 目录直接查看；详细图像证据见 `figure_analysis.md`。

### 8. 代码复现情况

核心代码与论文方法高度匹配。已验证的主要文件包括：

- `latentvelo/models/vae_model.py`：VAE、latent embedding、loss、ODE solve、trajectory、regularization；
- `latentvelo/models/velocity_field.py`：`zs/zu/zr/h` 结构化动力学和 ATAC 速度场；
- `latentvelo/trainer.py`：训练循环、验证集、模型选择；
- `latentvelo/output_results.py`：输出 latent AnnData、latent velocity、gene velocity 和 trajectories；
- `latentvelo/evaluation/metrics.py`：velocity cosine、CBDir、ICCoh、batch velocity cosine；
- `latentvelo/utils.py`：数据预处理和 velocity gene 选择。

需要注意：README 说 `paper_notebooks/` 和 `benchmarks/` 可用于论文结果和 benchmark，但本次分析没有逐个读取 notebook，也没有重跑图，因此“论文全部图可一键复现”不能声称为已验证。

### 9. 局限与未验证项

论文自己指出，LatentVelo 假设所有细胞轨迹从同一个潜在初始状态出发；如果数据中存在稀疏或断开的细胞簇，轨迹起点可能不符合生物预期（`paper.md:183-188`）。此外，不同数据集可能需要调整 latent 维度、使用 cell-type annotated model、限制 gene set 或使用实验时间/root cell 先验（`paper.md:167-188`）。

补充图表不可作为本次 primary evidence。Annotated VAE 内部和 ATAC 完整训练路径只做了部分代码验证，因此这些扩展的代码匹配应视为 Partial，而不是 Exact。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## LatentVelo Summary

### Problem

LatentVelo targets RNA-velocity and trajectory inference from static single-cell RNA-seq snapshots. Traditional velocity methods rely on restrictive gene-space kinetic assumptions: Velocyto assumes steady-state linear relationships, while scVelo relaxes steady state but still fits a strict linear dynamical model with latent time (`paper.md:27-39`, `paper.md:41-50`). These assumptions can fail for transcriptional boosts, lineage-dependent kinetics, time-dependent rates, weak unspliced signal, and batch effects (`paper.md:27-39`, `paper.md:133-152`).

### Proposed Method

LatentVelo is a VAE plus structured neural-ODE model. It encodes spliced and unspliced counts into separate latent states `$\hat z_s,\hat z_u$`, infers latent time `$\hat t$` and a conditioning variable `$h$`, and solves structured dynamics over spliced, unspliced, and regulatory latent variables (`paper.md:51-76`, `paper.md:207-234`). The regulatory state `$z_r$` and conditioning `$h=f_h(\hat z_s,\hat z_u)$` allow branch- or lineage-dependent dynamics (`paper.md:57-67`). Outputs include latent velocity, latent time, batch-corrected latent embeddings, cell-specific trajectories, and optional gene-space velocities via decoder Jacobian-vector products (`paper.md:68-76`, `paper.md:235-249`).

### Key Computational Ideas

- **Dynamics-informed embedding**: the encoded latent state `$\hat z$` is constrained to match the ODE solution `$z(\hat t)$`, so representation learning and dynamics fitting are coupled (`paper.md:53-56`, `paper.md:219-225`).
- **Structured latent dynamics**: code implements `zs/zu/zr/h` dynamics where spliced drift depends on `zs,zu`, unspliced drift depends on `zu,zr`, regulatory drift depends on `zs,zr,h`, and `h` remains constant along a cell trajectory (`LatentVelo_code/latentvelo/models/velocity_field.py:42-58`).
- **Weak biological regularization**: gene-space velocity is computed with decoder Jacobian-vector products and weakly regularized to correlate with unspliced counts and anti-correlate with spliced counts (`paper.md:241-249`; `LatentVelo_code/latentvelo/models/vae_model.py:527-694`).
- **Batch correction by model design**: batch IDs enter the encoder/decoder, while latent dynamics are batch-independent (`paper.md:271-278`; `LatentVelo_code/latentvelo/models/vae_model.py:135-173`).

### Evaluation

The paper evaluates LatentVelo on synthetic dyngen data, pancreatic endocrinogenesis, MEF reprogramming, batch-effect simulations, segmentoid data, mouse gastrulation, and 10 real trajectory datasets (`paper.md:79-181`, `paper.md:311-386`). Metrics include ground-truth velocity cosine for synthetic data, CBDir for expected cell-type transitions, ICCoh for local velocity coherence, kBET/iLISI/cLISI for batch integration, and nearest-neighbor velocity cosine across batches (`paper.md:387-406`). Main figures visually show lineage separation in `$z_r$`, cell-specific trajectories, batch integration, and generally stronger synthetic/real benchmark scores than scVelo (`figure_analysis.md`).

### Code and Reproducibility

Code is available in the workspace at `[local path omitted]`, sourced from `https://github.com/Spencerfar/LatentVelo` at commit `3cdf02946e53411aad68700ea0bba1254c48ec54`. Core implementation fidelity is high: the package implements the VAE, latent ODE, structured velocity field, training loop, trajectory outputs, decoder-JVP gene velocities, batch correction, preprocessing, and metrics (`doc_code.md`). The README documents installation, data setup, model initialization, training, output, and trajectory APIs (`LatentVelo_code/README.md:22-79`).

Important caveats:

- Exact figure reproduction is only partially verified: README points to `paper_notebooks/` and `benchmarks/`, but this analysis did not read notebooks or rerun metrics.
- The annotated scANVI-like and ATAC extensions exist, but only the dispatch/velocity-field anchors were verified in detail.
- No supplementary markdown was available in workspace state.
- Paper-stated limitations remain: a single learned initial state may fail for disconnected trajectories, and some datasets require hyperparameter tuning or root/time priors (`paper.md:183-188`).

### Bottom Line

LatentVelo is a dynamics-aware latent-variable model for RNA velocity that replaces strict gene-space linear kinetics with structured neural ODEs in a learned latent space. The local code strongly matches the core method, especially the VAE/ODE/loss/trajectory machinery. Reproducibility is good for method implementation and package use, but end-to-end paper-figure reproduction remains only partially verified without notebook inspection and reruns.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
