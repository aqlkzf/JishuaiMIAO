---
layout: default
permalink: /paper-atlas/mmvelo-00ba9437/
title: "mmVelo"
nav: false
description: "mmVelo 解决的问题是：单细胞 multiome 能同时测 RNA 和 ATAC，但这些测量仍然是静态快照；RNA velocity 可以给 RNA 层提供方向，却不能直接给 chromatin accessibility 一个动力学方程。mmVelo 的核心思想是先用多模态 VAE 学到共享细胞状态 zn，再用 RNA splicing kinetics 训练潜在状态转移 dn，最后把 zn+\\rho dn 通过不同 decode…"
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
      <span>bioRxiv · 2024</span>
    </div>
    <h1>mmVelo</h1>
    <p>mmVelo: A deep generative model for estimating cell state-dependent dynamics across multiple modalities</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2024.12.11.628059" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## mmVelo 方法中文解读

### 一句话概览

mmVelo 解决的问题是：单细胞 multiome 能同时测 RNA 和 ATAC，但这些测量仍然是静态快照；RNA velocity 可以给 RNA 层提供方向，却不能直接给 chromatin accessibility 一个动力学方程。mmVelo 的核心思想是先用多模态 VAE 学到共享细胞状态 $z_n$，再用 RNA splicing kinetics 训练潜在状态转移 $d_n$，最后把 $z_n+\rho d_n$ 通过不同 decoder 投影成 RNA velocity 和 peak-level chromatin velocity。

### 1. 生物学问题与建模目标

这个方法关注发育和分化过程中 RNA 表达、chromatin accessibility、TF motif 活性是否同步变化，以及这些变化能否帮助推断调控因子。计算上，mmVelo 把 RNA velocity 当作方向监督信号，把这个方向学到 latent cell-state manifold 上，再映射到 ATAC peak、TF motif、missing modality。它能支持“哪些 peak/motif/TF 可能处在动态调控中”的假设生成，但不能单独证明 TF 真实结合或因果调控。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| ATAC count | $a_n$, `adata_a.X` | 每个细胞的 peak accessibility | `doc_code.md` |
| spliced RNA | $s_n$, `layers["spliced"]` | mature RNA count | `doc_code.md` |
| unspliced RNA | $u_n$, `layers["unspliced"]` | nascent RNA count | `doc_code.md` |
| latent state | $z_n$, `z_moe` | 多模态共享细胞状态 | `mmvelo_multi/models.py:113-118` |
| latent dynamics | $d_n$, `d_moe` | 细胞状态短时间转移方向 | `mmvelo_multi/models.py:417-444` |
| chromatin velocity | $\Delta ATAC$, `dadt` | peak-level accessibility 变化 | `train_mouse_brain.py:323-334` |
| motif velocity | `d_motif_score` | motif activity 沿 $d_n$ 的变化率 | `03_clustering_motif_vjp.py:108-123` |

### 3. 方法主流程

1. 输入 matched multiome 数据：ATAC、spliced RNA、unspliced RNA。
2. RNA encoder 和 ATAC encoder 分别估计 latent state，代码中把两个 posterior mean 平均成 `z_moe`。
3. decoder 从 $z_n$ 重建 ATAC、spliced、unspliced profile，并用 VAE ELBO 训练。
4. 根据 latent neighbor 计算 smoothed profiles，再 fine-tune decoder，减少单细胞稀疏噪声。
5. 用 splicing kinetics 构造 observed RNA velocity target，学习 $\beta,\gamma$ 和 $q(d_n|z_n)$。
6. 预测时计算 $f(z_n+\rho d_n)-f(z_n)$，得到 `dsdt`, `dudt`, `dadt`。
7. 下游用 `dadt` 做 peak clustering、motif velocity、GRNBoost2 TF-peak inference。
8. missing-modality 分支用 modality mask、batch one-hot、MMD/domain adaptation，把 scRNA/scATAC 单模态数据接到 multiome latent space 中。

### 4. 数学目标与直觉

共享状态来自多模态 VAE：

$$
q(z_n|a_n,s_n,u_n)=\frac12(q(z_n|a_n)+q(z_n|s_n,u_n)).
$$

直觉是 RNA 和 ATAC 都描述同一个细胞状态，只是观测层不同。代码可验证的是 mean-level averaging，而不是完整 distribution mixture。

动力学训练的关键是让 latent transition 解码后的 spliced RNA 变化方向接近 RNA velocity：

$$
\frac{ds_n}{dt}_{obs}=
\frac{\tanh(\beta C^u f^u(z_n)-\gamma C^s f^s(z_n))}
{\|\tanh(\beta C^u f^u(z_n)-\gamma C^s f^s(z_n))\|_2}.
$$

代码中这对应 `compute_cossim_loss_dsdt`，用 cosine similarity 做方向匹配。Chromatin velocity 则是：

$$
\Delta ATAC=C^a(f^a(z_n+\rho d_n)-f^a(z_n)).
$$

所以 ATAC 动力学不是直接观测出来的，而是 RNA velocity 训练出的 latent direction 经 ATAC decoder 投影得到。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| multimodal VAE | `mmvelo_multi/models.py:108-170` | RNA/ATAC encoder + decoder likelihood | 部分匹配 |
| smoothed decoder fine-tuning | `models.py:242-282`, `train_mouse_brain.py:129-218` | 用 smoothed profiles fine-tune decoder | 部分匹配 |
| latent dynamics | `models.py:321-532` | 冻结大部分参数，只训练 dynamics encoder 和 kinetics | 精确匹配 |
| velocity output | `train_mouse_brain.py:323-334` | 写出 `dsdt`, `dsdt_obs`, `dadt`, `dudt` | 精确匹配 |
| missing modality | `models_missingmodality_all_adv_modadv.py:207-296` | MMD、domain adaptation、modality mask | 精确匹配 |
| motif velocity | `03_clustering_motif_vjp.py:108-123` | JVP 计算 motif score 的方向导数 | 精确匹配 |
| TF-peak inference | `05_GRN_inference_sep.py:56-160`, `256-295` | GRNBoost2 + permutation + FDR | 精确匹配 |

### 6. 结果如何解读

Fig. 2 支持 mmVelo 在 E18 mouse brain 中产生符合发育轨迹的 chromatin velocity，并展示 Neurod2 promoter/enhancer 的时序差异。Fig. 3 支持 motif velocity 能反映 hair follicle differentiation 中 Hoxc13、Gata3 等 TF motif 的动态。Fig. 4 用 motif enrichment、genomic distance 和 Lef1 区域示例间接支持 TF-peak 关系。Fig. 5 说明在 multiome bridge 存在时，可以从 scRNA 或 scATAC 推断缺失模态的 velocity。

这些结果更适合解读为“动态调控假设生成”，不是直接的因果验证。

### 7. 局限性与未验证部分

- 方法依赖 RNA velocity 方向；如果 splicing kinetics 不可靠，跨模态 velocity 也会受影响。
- smoothed profiles 能降噪，但可能平滑掉稀有状态或快速转变。
- public code 不是完整 paper reproduction CLI；多个 figure scripts 使用 `/home/nomura/Proj/mmvelo/...` 绝对路径。
- human missing-modality 数据在 README 中写为 available upon request，因此 Fig. 5 难以完全自包含复现。
- TF-peak links 是回归和 motif 支持的候选关系，不等于 TF binding 或 perturbation causality。

### 8. 快速阅读路线

1. `summary.md`：先看问题、结论和复现等级。
2. `doc_method.md`：理解数学目标和完整 pipeline。
3. `doc_code.md`：检查论文步骤和代码是否匹配。
4. `figure_analysis.md`：看每个图支持什么、不支持什么。
5. `claude_notes.md`：需要证据表、公式和源码 line range 时再读。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## mmVelo

### Paper

**mmVelo: A deep generative model for estimating cell state-dependent dynamics across multiple modalities**
Satoshi Nomura, Yasuhiro Kojima, Kodai Minoura, Shuto Hayashi, Ko Abe, Haruka Hirose, Teppei Shimamura. bioRxiv, 2024.

### Motivation

RNA velocity infers local transcriptome dynamics from spliced and unspliced RNA, but this kinetic observation does not directly exist for chromatin accessibility. Existing multiomic velocity methods either remain RNA-centric, aggregate chromatin dynamics at gene level, or require specialized assays. mmVelo asks whether RNA-derived directionality can be learned in a shared multiome latent state and then projected to other molecular layers.

### Method Overview

mmVelo uses a multimodal VAE to infer cell states from ATAC, spliced RNA, and unspliced RNA. It fine-tunes decoders on latent-neighborhood-smoothed profiles, then trains a latent dynamics encoder so that decoder-induced spliced RNA change aligns with a splicing-kinetics RNA-velocity target. After training, it computes modality velocities by decoding both $z_n$ and $z_n+\rho d_n$ and taking their difference.

This yields peak-level chromatin velocity, RNA/unspliced velocity, motif velocity, candidate TF-peak regulatory links, and missing-modality velocities when singleome data are bridged by multiome data.

### Evaluation

The paper evaluates mmVelo on 10x Multiome embryonic mouse brain, SHARE-seq mouse hair follicle differentiation, and human cortical development data. Main evidence includes UMAP streamlines, Neurod2 promoter/enhancer dynamics, chromatin-velocity peak clusters, motif velocity examples for TFs such as Hoxc13 and Gata3, GRN-style TF-peak plausibility checks, and missing-modality velocity similarity to multiome neighbors.

Named comparison methods include scVelo (Bergen et al., 2020), MultiVelo (C. Li et al., 2023), Chromatin Velocity (Tedesco et al., 2022), and missing-modality profile models such as scMM (Minoura et al., 2021) and MultiVI (Ashuach et al., 2023), as cited in the paper.

The strongest results support biological plausibility and selected benchmark performance. Regulatory links remain candidate hypotheses rather than causal proof.

### Code Availability And Match

Code was acquired from `https://github.com/nomuhyooon/mmVelo`, branch `tutorial-revision`, commit `32108c9168dbb82691cbb036b3e80374d6c70b0d`.

The core paper method is substantially present: multimodal VAE, smoothed decoder fine-tuning, latent dynamics, decoder-projected velocities, missing-modality model, motif velocity, and GRNBoost2 TF-peak inference. However, the public repository is tutorial/reproduction oriented. Several downstream scripts use hardcoded author paths and precomputed intermediate files, and the human missing-modality tutorial requires data available upon request.

### Strengths

- Clear latent-dynamics formulation that reuses RNA velocity to infer dynamics across modalities.
- Peak-level chromatin velocity enables analyses that gene-level chromatin aggregation would miss.
- Missing-modality branch is implemented with explicit modality masks, batch conditioning, and domain-adaptation losses.
- Motif velocity and TF-peak regression provide useful regulatory hypothesis-generation workflows.

### Limitations

- All dynamics depend on RNA velocity being reliable in the biological system.
- Smoothed profiles reduce sparsity but can blur rare or sharp transitions.
- TF-peak links are regression/motif-based candidates, not perturbational validation.
- Public code does not provide a clean end-to-end paper reproduction path for all figures and datasets.

### Reproducibility Rating

**3/5 (Medium).** The core model implementation is present and line-verifiable, but full paper reproduction is limited by hardcoded local paths, request-only/preprocessed data, and notebook/script-style downstream analyses.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
