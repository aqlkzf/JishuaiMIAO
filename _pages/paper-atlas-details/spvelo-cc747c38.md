---
layout: default
permalink: /paper-atlas/spvelo-cc747c38/
title: "spVelo"
nav: false
description: "spVelo 解决的是多批次空间转录组中的 RNA velocity 推断问题：输入 spliced/unspliced 表达、空间坐标和批次信息，输出细胞/spot-by-gene 的 velocity、潜在时间、状态概率和下游生物学解释。核心思想是在 VAE 式 RNA 动力学模型中加入空间 kNN 和跨批次 MNN/OT 图，再用 GAT 和 MMD 让 velocity 场同时利用组织邻域和跨样本对应关系。"
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
      <span>Genome Biology · 2025</span>
    </div>
    <h1>spVelo</h1>
    <p>spVelo: RNA velocity inference for multi-batch spatial transcriptomics data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-025-03701-8" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## spVelo 方法中文解读

### 一句话概览

spVelo 解决的是多批次空间转录组中的 RNA velocity 推断问题：输入 spliced/unspliced 表达、空间坐标和批次信息，输出细胞/spot-by-gene 的 velocity、潜在时间、状态概率和下游生物学解释。核心思想是在 VAE 式 RNA 动力学模型中加入空间 kNN 和跨批次 MNN/OT 图，再用 GAT 和 MMD 让 velocity 场同时利用组织邻域和跨样本对应关系。

### 1. 生物学问题与建模目标

- 研究对象：空间转录组中的细胞或 spot，尤其是多样本、多批次组织数据。
- 关键问题：如何从瞬时的 spliced/unspliced RNA 计数推断未来表达变化，并让不同批次的 velocity 可以放在同一轨迹框架中解释。
- 为什么需要计算方法：真实瞬时 RNA velocity 不可直接观测；空间位置和批次结构如果只做后处理，可能丢失组织内和跨样本的动态关系。
- 方法能支持的解释：velocity 方向、潜在时间、轨迹模式、状态不确定性、候选 driver marker、GRN/CCC 假设。
- 方法不能直接证明：真实分子速度、实验因果调控、蛋白层面的配体-受体通信。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| spliced counts | $S^{N \times G}$ / `spliced` / `"Ms"` | 成熟 mRNA 表达 | `doc_method.md`, `doc_code.md` |
| unspliced counts | $U^{N \times G}$ / `unspliced` / `"Mu"` | 新生 mRNA 表达 | `doc_method.md`, `doc_code.md` |
| spatial coordinates | $X^{N \times 2}$ / `spatial_key` | spot/cell 的组织坐标 | `spVelo/spvelo/_utils.py:140-216` |
| VAE latent | $z_n^{VAE}$ / `qz_m`, `qz_v`, `z` | 表达驱动的细胞状态 | `spVelo/spvelo/_module.py:397-413` |
| GAT latent | $z_n^{GAT}$ / `graph_enc_loc`, `graph_enc_scale` | 空间和跨批次图上下文 | `spVelo/spvelo/_module.py:249-250`, `spVelo/spvelo/_module.py:525-528` |
| state probability | $\pi_{ng}$ / `px_pi` | 每个 cell-gene 属于四种动力学状态的概率 | `doc_code.md` |
| velocity | $V$ / `velos` | 未来表达变化方向和速度 | `spVelo/spvelo/_model.py:523-625` |
| MMD penalty | `calculate_mmd`, `penalty_scale` | 对齐不同批次 latent 分布 | `doc_code.md` |
| LRscore/LRvelo | 论文公式 | 静态/动态细胞通信分数 | 论文与 `figure_analysis.md`；代码中未找到直接实现 |

### 3. 方法主流程

1. 预处理 AnnData：过滤低质量基因，归一化、log transform、计算 moments，选择 HVG，并可用 steady-state scVelo 的 $R^2$ 阈值过滤基因。代码可验证位置见 `spVelo/spvelo/run_methods.py:46-57` 和 `spVelo/spvelo/_utils.py:90-138`。
2. 构建图：批次内用空间坐标建 kNN 图，批次间用表达 MNN/OT 建连接。默认 `spatial_neighbors=15` 和 `mnn_neighbors=15` 可在 `spVelo/spvelo/run_methods.py:20-73` 验证。
3. 表达编码：把 spliced 和 unspliced 拼接后送入 MLP/VAE encoder，得到 $z_n^{VAE}$。
4. 图融合：GATConv 根据空间/MNN 边更新 latent mean 和 variance，再重新采样得到组合 latent $z_n$。这是 spVelo 区别于普通 velocity 模型的关键实现。
5. 动力学解码：decoder 输出四状态概率、latent time 和 kinetic parameters，用四状态 ODE 形式拟合 $\bar{u}$ 与 $\bar{s}$。
6. 训练目标：优化重构项、KL 项、switch penalty 和 MMD batch penalty。注意代码默认 `penalty_scale=0.2`，论文写默认 $\lambda=2$。
7. velocity 推断：代码按 $\beta\bar{u}-\gamma\bar{s}$ 计算 spliced velocity，并可按后验均值或 MAP state 合成最终 velocity。
8. 下游分析：论文展示不确定性、轨迹、driver marker、EGFR perturbation、temporal CCC；其中多个下游流程在公开代码中未找到直接实现。

### 4. 数学目标与直觉

总体目标是：

$$
V^{N \times G}=M(S^{N \times G}, U^{N \times G}, X^{N \times 2})
$$

意思是 velocity 不只由 RNA 计数决定，还由空间位置参与建模。spVelo 先学习表达 latent，再把空间和跨批次图信息加进去：

$$
z_n=z_n^{VAE}+z_n^{GAT}.
$$

四状态概率用 Dirichlet prior 正则化：

$$
\pi_{ng} \sim Dirichlet(0.25,0.25,0.25,0.25).
$$

velocity 的核心输出公式是：

$$
v^{(g)}=\beta_g \bar{u}^{(g)}-\gamma_g \bar{s}^{(g)}.
$$

直觉上，$\beta_g \bar{u}$ 表示 unspliced 转成 spliced 的流入，$\gamma_g \bar{s}$ 表示 spliced 的降解流出，二者差值就是成熟转录本的变化趋势。

论文还给出 latent entropy uncertainty 和 temporal CCC：

$$
h(z)=\frac{1}{2}\log((2\pi e)^d \det(\Sigma))
$$

$$
LRvelo(i,j)=(S_{il}V_{jr}+V_{il}S_{jr})I(d_{ij}<q).
$$

这些公式在论文解释中重要，但公开代码中未找到对应的直接实现。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| HVG、过滤、预处理 | `spVelo/spvelo/run_methods.py:46-57`; `spVelo/spvelo/_utils.py:90-138` | 选择 HVG，min-max scale，按 velocity $R^2$ 过滤 | ~ Partial |
| 空间 kNN 图 | `spVelo/spvelo/_utils.py:140-216` | 批次内按坐标构图 | ✓ Exact |
| MNN/OT 跨批次边 | `spVelo/spvelo/run_methods.py:69-72`; `spVelo/spvelo/_module.py:510-528` | 调用 `get_mnn(..., is_ot=True)` 并合并到 GAT 边 | ✓ Exact |
| MLP expression encoder | `spVelo/spvelo/_module.py:324-399` | 拼接 spliced/unspliced 后编码 | ✓ Exact |
| GAT latent fusion | `spVelo/spvelo/_module.py:249-250`; `spVelo/spvelo/_module.py:525-528` | GAT 更新 mean/variance 后采样 | ✓ Exact |
| MMD penalty | `spVelo/spvelo/_module.py:558-584` | 对 batch pair 的 latent 加 MMD | ~ Partial |
| velocity formula | `spVelo/spvelo/_model.py:523-620` | 计算 $\beta\bar{u}-\gamma\bar{s}$ 并可 clip | ✓ Exact |
| latent entropy uncertainty | NOT FOUND | 代码中找到的是 sampled velocity 的 directional uncertainty | ✗ Not found |
| temporal CCC / EGFR perturbation / GSEA | NOT FOUND | 公开代码未找到直接流程 | ✗ Not found |

### 6. 结果如何解读

`figure_analysis.md` 显示：Figure 2 用 simulated pancreas 和 OSCC 的多种 proxy metric 说明 spVelo 在 confidence、transition、direction、spatial 和 MNN coherence 上优于多个 baseline；Figure 3 展示 OSCC 中 bifurcating/converging trajectory 和 marker 随 latent time 的变化；Figure 4 展示 phase portrait 和 oncogenic pathway enrichment；Figure 5 展示 EGFR in silico perturbation 和 temporal CCC。

这些结果支持 spVelo 能产生更连贯的多批次 velocity 场，也能生成有生物学意义的下游假设。但这些评价依赖 cell-type label、邻域定义和定性图示，不是对真实 instantaneous velocity 的直接测量。

### 7. 局限性与未验证部分

- 公开代码可验证的是核心 velocity 模型；多个下游分析没有找到公开实现。
- 论文默认 $\lambda=2$，代码默认 `penalty_scale=0.2`。
- 论文训练 2000 epochs，代码类默认 500，wrapper 默认 1000。
- time-dependent transcription rate 分支存在，但默认不学习。
- uncertainty 论文写 latent differential entropy，公开代码找到的是 directional uncertainty。
- GRN perturbation 和 temporal CCC 更适合作为假设生成，不应解读为实验因果验证或蛋白通信验证。

### 8. 快速阅读路线

1. 先读 `summary.md`：快速了解论文目标、结论和 reproducibility rating。
2. 再读 `doc_method.md`：理解数学模型、算法流程和变量含义。
3. 内读 `doc_code.md`：查看哪些论文 claims 有代码证据，哪些是 mismatch 或 Not found。
4. 再读 `figure_analysis.md`：理解每张主图支持什么结论。
5. 最后读 `claude_notes.md`：查看完整 evidence ledger、assumption ledger 和开放问题。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## spVelo

### Motivation And Novelty

spVelo addresses RNA velocity inference for multi-batch spatial transcriptomics. Existing RNA velocity methods can model spliced/unspliced dynamics, but they usually do not jointly use spatial coordinates and cross-batch tissue correspondences. This is especially limiting when a biological trajectory spans multiple slices or samples.

The novelty is a deep generative velocity model that combines expression-based VAE kinetics with a graph attention encoder over spatial and cross-batch edges, plus an MMD penalty to align batch latent distributions. The method outputs RNA velocity, latent time, kinetic state, uncertainty, and downstream hypothesis-generation scores for trajectory patterns, driver markers, GRN perturbation, and temporal cell-cell communication.

### Method Overview

Inputs are spliced counts $S$, unspliced counts $U$, spatial coordinates $X$, and batch labels. spVelo preprocesses expression with normalization, smoothing, gene filtering, and HVG selection. It constructs spatial kNN edges within each batch and cross-batch MNN/OT-like edges between comparable cells.

An MLP encoder produces expression-derived latent statistics. A GAT transforms those statistics over the combined graph. The final latent state adds VAE and GAT contributions, then drives state probabilities and gene-specific latent times under a four-state kinetic model. Training optimizes an ELBO with switch regularization and an MMD batch penalty. Velocity is computed as $\beta_g\bar{u}^{(g)}-\gamma_g\bar{s}^{(g)}$.

Code inspection supports the core architecture and velocity output, but public defaults differ from the paper for penalty weight and training epochs. The code also disables time-dependent transcription by default and implements uncertainty differently from the paper entropy formula.

### Evaluation

The paper evaluates spVelo on simulated pancreas data, OSCC spatial transcriptomics, and supplementary spatial velocity comparisons. Main metrics include expression/spatial/MNN confidence, transition, direction, cross-batch velocity coherence, latent-time ordering, and qualitative trajectory/marker analyses. Compared methods include scVelo stochastic/dynamical (Nature Biotechnology, 2020), veloVI (Nature Methods, 2024), LatentVelo (recent neural velocity baseline), scGen-corrected variants (Nature Methods, 2019), and supplementary spatial velocity methods such as STT and SIRV.

Figures show spVelo scoring strongly on pancreas and OSCC proxy metrics, producing ordered latent time, improving cross-batch cosine similarity, identifying high-uncertainty regions, recovering bifurcating/convergent OSCC patterns, fitting MURK and pancreas marker dynamics, and supporting EGFR perturbation plus temporal CCC examples.

The evaluation is useful but not absolute ground truth. Velocity metrics depend on known labels and neighborhood definitions. GRN and CCC analyses are hypothesis-generating and are not experimentally validated causal or protein-signaling assays.

### Reproducibility

Rating: **3 / 5**.

The public GitHub repository (`https://github.com/VivLon/spVelo`, commit `909db4caea261dbe34270ef23b18f6c6751567c1`) contains the core package, model class, module implementation, wrapper path, tutorial, and MIT license. Core VAE/GAT velocity inference can be traced to source lines.

Reproducibility is reduced by several gaps. The public defaults differ from the paper's stated penalty and epoch settings. Some utility code appears experiment-specific or incomplete. The repository does not expose the full benchmark reproduction, Figure 3-5 plotting workflows, EGFR in silico deletion workflow, temporal CCC `LRscore`/`LRvelo` workflow, or MSigDB/GSEA scripts. Reproducing the headline paper figures therefore requires additional unpublished analysis code or substantial reconstruction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
