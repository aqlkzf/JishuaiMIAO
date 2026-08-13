---
layout: default
permalink: /paper-atlas/intervelo-1f1f2849/
title: "InterVelo"
nav: false
description: "InterVelo 用一条潜在 neural-ODE 轨迹给全部基因提供共享的细胞时间，再用可变转录率的剪接动力学和 Euler 重建将 velocity 信息反馈给排序；它的强项是时间—速度共学习，而主要边界是单轨迹/batch ODE 近似、事后方向选择和若干纸—码损失差异。"
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
      <span>Bioinformatics · 2025</span>
    </div>
    <h1>InterVelo</h1>
    <p>InterVelo: a mutually enhancing model for estimating pseudotime and RNA velocity in multi-omic single-cell data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1093/bioinformatics/btaf500" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for InterVelo">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/yurouwang-rosie/InterVelo" target="_blank" rel="noopener noreferrer" aria-label="Open code for InterVelo">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## InterVelo：让全局伪时间与 RNA velocity 相互约束

### 1. 方法要解决的矛盾

传统 RNA velocity 常对每个基因独立拟合剪接动力学，再把基因时间整合为细胞时间。这容易受基因噪声影响，也常假定转录率 $\alpha$ 在发育过程中不变。另一方面，普通伪时间方法能给细胞全局排序，却不直接给出每个基因的变化速度，而且方向可能反转。

InterVelo 将两者放进同一个模型：

- 无监督 VAE + neural ODE 从整个细胞状态学习伪时间 $t$ 和潜在轨迹 $Z_t$；
- 动力学分支用 $Z_t$ 预测细胞特异转录率 $\alpha_{i,g}$，再结合基因特异的 $\beta_g,\gamma_g$ 计算 RNA velocity；
- 预测速度沿伪时间做 Euler 积分并重建表达，反过来约束伪时间。

“相互增强”因而是同一训练目标中的双向约束，不是两个模型交替到数学收敛的明确过程。

### 2. 输入和输出

输入至少包含平滑后的 spliced $S$ 和 unspliced $U$。单组学时 $X=(S,U)$；多组学时可直接拼接其他特征 $O$，即 $X=(S,U,O)$。额外组学只进入潜在时间/状态编码器，RNA 动力学方程仍只作用于 $S,U$。

核心输出是：细胞伪时间、spliced RNA velocity、潜在表示 `X_TNODE`、潜在向量场 `X_VF`、以及基因级 $\beta,\gamma$。只有开启 `pred_unspliced=True` 时才输出 unspliced velocity 和 `pred_alpha` layer（`train.py:176-206`）。

### 3. 无监督分支：伪时间与潜在 ODE

#### 3.1 共享首层的两个编码头

`Encoder` 先用共享全连接层将 $X_i$ 变换为隐藏表示，然后分成：

$$t_i=\sigma(f_t(X_i))\in(0,1),$$

以及潜在变量的 $\mu_i,\log\sigma_i^2$。重参数化为

$$Z_i=\mu_i+\sigma_i\odot\epsilon_i,\qquad \epsilon_i\sim\mathcal N(0,I).$$

实现在 `module.py:114-152,300-304`。Sigmoid 只提供相对 $0$--$1$ 顺序，不是实验时间单位。

#### 3.2 一条潜在 ODE 轨迹

模型按当前 mini-batch 内的 $t_i$ 排序，去掉重复时间，取最早细胞的 $Z$ 作为 $z_0$，再求解

$$\frac{dZ_t}{dt}=f_{\mathrm{ode}}(Z_t).$$

默认用 Euler 法（`module.py:306-325`）。每个 batch 都以该 batch 内当前最早的随机潜在样本作为起点，因此训练目标实际促使细胞贴合一条潜在 ODE 路径。对多分支、不连通或环形拓扑，这个单起点表达是近似，不是显式分支 ODE。

#### 3.3 时间分支损失

编码潜在状态 $Z$、ODE 潜在状态 $Z_t$都经同类解码器重建输入，同时惩罚 $Z$ 与 $Z_t$ 的距离，再加 VAE KL 项。代码中 KL 权重不是固定 0.5：`BaseTrainer.train()` 每轮设为

$$w_{KL}=1-\min(\mathrm{epoch}/\mathrm{epochs},0.6),$$

因而从近 1 递减到 0.4（`basetrainer.py:74-80`）。

### 4. 速度分支：状态依赖的转录率

经典剪接方程是

$$
\frac{dU_{i,g}}{dt}=\alpha_{i,g}-\beta_gU_{i,g},\qquad
\frac{dS_{i,g}}{dt}=\beta_gU_{i,g}-\gamma_gS_{i,g}.
$$

InterVelo 用两层 MLP + Softplus 从 $Z_t$ 解码每个细胞、每个基因的 $\alpha_{i,g}$，而 $\beta_g,\gamma_g$ 是全体细胞共享的可学参数，经 Softplus 后截断到 $[0,50]$（`module.py:359-411,506-524,620-640`）。

论文写 $\alpha=f_\alpha(Z_t,t)$ 或将它记作随时间变化；实现的 `VELODecoder.forward(z,t)` 接收 `t`，却没有使用它，`torch.cat([z,t])` 已被注释。所以 $\alpha$ 通过 $Z_t$ 间接随状态/时间变化，而不是显式依赖 $t$。

默认 `pred_unspliced=False`，模型只输出

$$V^S=\beta U-\gamma S.$$

虽然内部仍计算 $\alpha$，$V^U=\alpha-\beta U$ 和高 unspliced 表达惩罚都只在开启 `pred_unspliced=True` 时进入默认外的分支。

### 5. Euler 重建如何将速度反馈给伪时间

细胞按预测 $t$ 排序后，代码用

$$\hat X_{k+1}=\hat X_k+V_k(t_{k+1}-t_k)$$

逐步重建 RNA 表达。`Velo_Euler_func()` 每 50 个细胞重置一次初值（`module.py:61-86`），限制长序列的累积误差，但也使相邻段落并非一条连续数值轨迹。重建损失促使预测 $t$ 选择一个与 velocity 一致的排序。

### 6. 总损失与论文写法的差异

论文概括为 $L=L_t+\lambda_vL_v$。代码却在每个 batch 内无梯度计算

$$r=\frac{L_t}{L_v},$$

然后优化

$$L=L_t+rL_v$$

（`module.py:666-682`）。由于 $r$ 被 detach，损失数值在 $L_v\ne0$ 时等于 $2L_t$，但梯度仍包含按 $L_t/L_v$ 缩放的 velocity 重建梯度。这是动态梯度平衡，不是论文中一个固定 $\lambda_v$；当 $L_v$ 接近 0 时也没有分母保护。

### 7. 两层方向校正

方向在无根节点时本来可整体反转。代码有两层校正：

1. `Trainer.eval()` 计算 $V^S$ 与 $U$ 的正相关、与 $S$ 的负相关组合分数；若均值为负，当次输出的 velocity 取反、$t\leftarrow1-t$（`loss.py:44-97`; `model.py:267-283`）。
2. 外层 `train()` 又用 scVelo 根据当前 velocity 建图并计算 `velocity_pseudotime`。若其与 InterVelo pseudotime 负相关，就反转 `scale1/scale2` 并从当前权重再训一遍（`train.py:208-297`）。

因此最终方向不只是论文 Pearson 规则的一次直接应用，还依赖 scVelo 的邻居图和 velocity pseudotime 实现。

### 8. 多组学扩展的实际含义

InterVelo 对额外组学的处理是特征级拼接，不是模态特异编码器、交叉注意力或多组学联合生成分布。优点是不需要为 ATAC 等数据另写动力学 ODE；边界是不同模态的尺度、维数和缺失结构不会被模型显式分离。`preprocess_data()` 使用 MaxAbsScaler 分层缩放（`data.py:183-231`），这是复现时不能忽略的代码路径。

### 9. 六张主图如何读

- **图 1** 展示 VAE/neural ODE 时间分支和 RNA 动力学分支如何通过 Euler 重建耦合。
- **图 2** 在钟形、环形模拟和代谢标记神经元数据上比较伪时间与 velocity；模拟结果依赖指定的生成过程和对照方法设置。
- **图 3** 展示齿状回多分支轨迹、基因速度和方向指标。流线是将高维 velocity 投影到嵌入后的可视化，不是观测的单细胞轨迹。
- **图 4** 比较驱动基因和通路富集；重合与富集支持生物一致性，不能单独确定因果调控。
- **图 5** 用不同下采样比例评估稳定性，主要回答细胞数减少后排序和速度是否保持。
- **图 6** 展示 RNA-only 与 RNA+ATAC 的脑皮层发育排序和通路变化；改善反映附加特征对潜在时间的信息增益。

### 10. 实现和复现边界

1. 默认 mini-batch 为 1024，每个 batch 内独立排序并解 ODE；batch 构成会影响数值轨迹。
2. 代码对编码时间的正确方向不可识别，必须依靠事后规则选择方向。
3. `Trainer.eval(return_kinetic_rates=False)` 仍无条件执行 `np.concatenate(alpha_rates)`，而列表为空（`model.py:236-263`）；公开 `train()` 默认传 `True` 避开了该路径。
4. 论文的全套 benchmark 指标多位于 notebook/分析工作流程，不是核心 package 的统一 API。
5. 本次结论来自论文、主图和记录 commit 的源码审计；未重跑全数据 benchmark。

### 11. 一句话总结

InterVelo 用一条潜在 neural-ODE 轨迹给全部基因提供共享的细胞时间，再用可变转录率的剪接动力学和 Euler 重建将 velocity 信息反馈给排序；它的强项是时间—速度共学习，而主要边界是单轨迹/batch ODE 近似、事后方向选择和若干纸—码损失差异。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## InterVelo: Summary

**Paper**: InterVelo: a mutually enhancing model for estimating pseudotime and RNA velocity in multi-omic single-cell data
**Journal**: *Bioinformatics* 41(10), 2025
**DOI**: 10.1093/bioinformatics/btaf500
**GitHub**: https://github.com/yurouwang-rosie/InterVelo

---

### Motivation & Novelty

Single-cell RNA-seq captures static gene expression snapshots. Two families of methods attempt to recover temporal dynamics:

1. **Pseudotime inference** (Monocle [*Nat. Methods* 2017], Slingshot [*BMC Genomics* 2018], scTour [*Genome Biology* 2023]) — ranks cells by similarity but requires prior knowledge of root cells or developmental direction, lacks individual gene-level interpretability, and cannot capture gene-specific dynamics.

2. **RNA velocity** (scVelo [*Nat. Biotechnol.* 2020], veloVI [*Nat. Methods* 2024], DeepVelo [*Genome Biol.* 2024], cellDancer [*Nat. Biotechnol.* 2024]) — mechanistically interpretable via transcription dynamics but assumes constant transcription rates and infers gene-specific times independently, creating biases when integrating into a global developmental timeline.

**Key limitations addressed**:
- Constant transcription rate assumption ignores transcription factor activity, chromatin accessibility, and other regulatory changes along development
- Gene-specific time inference leads to biased pseudotime when aggregated
- No method jointly learns pseudotime and velocity to let them mutually constrain each other
- Most velocity methods cannot incorporate multi-omic information without imposing ODE assumptions on non-RNA modalities

**InterVelo's unique contributions**:
1. **Simultaneous learning** of pseudotime (via VAE + neural ODE) and RNA velocity (via kinetic ODE), with each supervising the other
2. **State-dependent transcription rate**: $\alpha_{i,g} = f_\alpha(Z_t)$ — transcription varies by cell state, not fixed globally
3. **No prior knowledge required**: Velocity direction is used to automatically correct pseudotime direction (no root cell annotation needed)
4. **Multi-omic flexibility**: ATAC-seq or other omics concatenated into input; no modality-specific ODE assumptions
5. **Euler integration**: Variable $\alpha$ makes analytical ODE solutions unavailable; Euler method (segment length 50) approximates expression reconstruction

---

### Method Overview

InterVelo has two tightly coupled components:

**Unsupervised component** (pseudotime): A variational autoencoder (VAE) with a neural ODE backbone (adapted from scTour, *Genome Biology* 2023):
- Shared encoder produces latent state Z (cell identity) and pseudotime t ∈ (0,1)
- Neural ODE models Z_t = ODESolve(Z_t0, f_ode, t) — how cell state evolves through developmental time
- Both Z and Z_t decode to reconstruct input X; alignment between them enforced by MSE penalty

**Supervised component** (velocity): Uses kinetic ODEs with state-dependent transcription:
- $\alpha_{i,g} = f_\alpha(Z_t)$ via 2-layer FC network with Softplus activation
- $V^s = \beta \cdot U - \gamma \cdot S$ with gene-specific β, γ (learned)
- Euler's method reconstructs expression from velocity; reconstruction error drives supervised learning

**Mutual feedback**: pseudotime $t$ defines the integration order for velocity Euler steps; velocity direction is used post-training to detect and correct pseudotime orientation (no reorientation labels needed).

---

### Evaluation

#### Simulated Data
- **Bell-shaped trajectory** (100 simulated datasets): InterVelo achieves highest Pearson correlation for both pseudotime and velocity vs. scVelo, DeepVelo, veloVI + Monocle3/Slingshot/scTour
- **Multi-omic state-switch** (circular trajectory, 100 datasets): InterVelo performs best in circular cross-correlation; multi-omic integration substantially improves pseudotime accuracy

#### Real Datasets

| Dataset | Key Result |
|---|---|
| Metabolic-labeled neurons (scNT-seq, GSE141851) | Highest Pearson corr with true time vs. scVelo/DeepVelo/veloVI/Monocle3/Slingshot/scTour |
| Mouse dentate gyrus P0+P5 (GSE95753) | Correct developmental ordering in all 5 lineages; scVelo fails CA1/CA2/granule |
| Mouse dentate gyrus P12+P35 | Better driver gene alignment with reference markers (astrocyte lineage); CBDir/LenAcc superior |
| Pancreas E15.5 (GSE132188) | Spearman corr=0.98 pseudotime stability when pre-endocrine cells removed; most stable velocity under downsampling |
| Human cortex multi-omic (GSE162170) | ATAC integration corrects subplate-dominated pseudotime; outperforms MultiVelo (*Nat. Biotechnol.* 2023) |

#### Quantitative Metrics (Table 1, 4 real datasets)
InterVelo achieves highest mean score across 4 metrics (CBDir, CBDir2, TransCosine, LenAcc) on all 5 datasets:

| Dataset | InterVelo Mean | Best competitor mean |
|---|---|---|
| Metabolic neurons | 0.42 | DeepVelo: 0.19 |
| Dentate gyrus P0+P5 | 0.45 | DeepVelo: 0.34 |
| Dentate gyrus P12+P35 | 0.46 | veloVI: 0.23 |
| Pancreas | 0.41 | DeepVelo: 0.20 |
| Cortex | 0.37 | scVelo: 0.27 |

#### Downstream Analyses
- **Driver gene identification** (CellRank2): Better alignment with experimental marker genes for astrocyte and granule lineages
- **Pathway enrichment** (GO BP): Biologically correct enrichment (gliogenesis, synaptic plasticity) vs. incorrect pathways from scVelo
- **GSEA (multi-omic cortex)**: Up-regulated synaptic signaling, down-regulated cell cycle — consistent with known ExUp/ExDp biology

---

### Reproducibility

**Rating: 3/5**

**Strengths**:
- Code publicly available on GitHub and archived on Zenodo (DOI: 10.5281/zenodo.16158798)
- Example scripts for single-omic and multi-omic cases provided
- Default configs well-documented in `Constants._default_configs`
- Data accessible via scVelo datasets API and GEO accessions

**Weaknesses**:
- Strict dependency versions: `numpy==1.21.1`, `matplotlib>=3.3,<3.6`, `pandas<2.0.0`, `Python>=3.8,<3.10` — requires an isolated environment with older packages
- No notebooks — only Python scripts; must adapt to own datasets
- Evaluation metrics (CBDir, CBDir2, TransCosine, LenAcc) not included in the package — would need separate implementation from Supplementary Note 3
- Multi-omic preprocessing requires MultiVelo pipeline (smoothing, etc.) as prerequisite
- Direction correction retrains the model if pseudotime direction is wrong — can significantly increase compute time unpredictably
- `seed` sensitivity: examples note that changing seed may be needed if pseudotime is inconsistent with velocity

**Environment setup**:
```bash
conda create -n intervelo python=3.9
conda activate intervelo
git clone https://github.com/yurouwang-rosie/InterVelo && cd InterVelo
pip install .
```

**Common pitfall**: If velocity direction and pseudotime disagree, the model retrains with flipped `scale1`/`scale2`. Users may observe this silently doubling training time. Try `scale1=-1` initially if you know the developmental direction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
