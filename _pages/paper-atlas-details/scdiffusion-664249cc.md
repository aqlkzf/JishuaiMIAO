---
layout: default
permalink: /paper-atlas/scdiffusion-664249cc/
title: "scDiffusion"
nav: false
description: "scDiffusion 不是直接在高维基因表达向量上做扩散，而是先把细胞表达压缩成 128 维潜在表示，再在潜在空间训练扩散模型；生成时用分类器梯度把采样过程“推向”指定细胞类型、器官/细胞类型组合或两个发育状态之间的中间状态。"
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
      <span>arXiv · 2024</span>
    </div>
    <h1>scDiffusion</h1>
    <p>scDiffusion: conditional generation of high-quality single-cell data using diffusion model</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scDiffusion 方法中文解释

### 核心问题

scDiffusion 解决的是“如何生成高质量、可控条件的单细胞 RNA-seq 数据”。论文指出，真实 scRNA-seq 数据获取成本高，某些细胞类型或发育状态很稀有；已有统计模拟方法容易过度简化，GAN 类方法训练不稳定且通常只能生成已知分布内的数据（`paper.md:11-17`, `paper.md:20-35`）。

### 一句话理解

scDiffusion 不是直接在高维基因表达向量上做扩散，而是先把细胞表达压缩成 128 维潜在表示，再在潜在空间训练扩散模型；生成时用分类器梯度把采样过程“推向”指定细胞类型、器官/细胞类型组合或两个发育状态之间的中间状态（`paper.md:41-56`, `paper.md:62-132`）。

### 模型由三部分组成

1. **自编码器（autoencoder）**
   论文使用预训练的 SCimilarity 作为基础，自编码器把原始细胞表达 $S_{ori}$ 编码成潜在向量 $x_0$，再由 decoder 还原为表达谱。输入会先做 total count 1e4 归一化和 log 转换，潜在空间维度为 128（`paper.md:50-56`）。代码中也能看到 `normalize_total(..., target_sum=1e4)`、`log1p` 和 VAE encoder（`scDiffusion/guided_diffusion/cell_datasets_loader.py:61-88`; `scDiffusion/VAE/VAE_model.py:11-75`）。

2. **潜在扩散模型（latent diffusion）**
   得到 $x_0$ 后，模型逐步加噪得到 $x_i$，训练 denoising network 从噪声潜在向量中预测噪声并反向去噪。论文给出前向扩散：

   $$q\left(x_i\middle\|x_{i-1}\right)=\mathcal{N}\left(x_i\middle\|\sqrt{1-\beta_i}x_{i-1},\beta_i I\right)$$

   以及线性 $\beta_i$ schedule（`paper.md:65-75`）。代码实现了线性 beta schedule 和从 $x_0$ 直接采样 $x_t$ 的闭式形式（`scDiffusion/guided_diffusion/gaussian_diffusion.py:18-35`, `scDiffusion/guided_diffusion/gaussian_diffusion.py:188-206`）。

3. **条件控制器（classifier guidance）**
   分类器单独训练，用带噪潜在向量和时间步预测细胞标签。采样时，分类器对目标标签的 log probability 求梯度，再把这个梯度加到扩散反向均值上，引导生成结果朝目标条件移动（`paper.md:102-112`）。代码里 `classifier_sample.py` 计算目标类别梯度，`gaussian_diffusion.py` 在 reverse step 中应用条件均值修正（`scDiffusion/classifier_sample.py:134-142`; `scDiffusion/guided_diffusion/gaussian_diffusion.py:397-442`）。

### Gradient Interpolation 是什么？

普通条件生成只指定一个目标，例如“生成某种细胞类型”。Gradient Interpolation 指定两个条件，例如“起始状态”和“终点状态”，然后按权重混合两个梯度：

$$\beta_i(\gamma_1\nabla_{x_i}\log p_\phi(y_1|x_i)+\gamma_2\nabla_{x_i}\log p_\phi(y_2|x_i))$$

同时，采样初始点不是纯高斯噪声，而是从真实初始细胞的潜在向量 $x_0$ 加噪得到：

$$x_{init}=\sqrt{\alpha_t}x_0+\sqrt{1-\alpha_t}\epsilon$$

这样模型可以从一个真实状态出发，被两个条件梯度牵引，生成连续中间状态（`paper.md:118-132`）。代码中 `cond_fn_inter` 分别计算两个条件梯度，并读取初始细胞、归一化、编码、加噪后作为采样起点（`scDiffusion/classifier_sample.py:88-106`, `scDiffusion/classifier_sample.py:151-225`）。

### 实验如何验证？

论文做了四类实验：

- **真实感生成：** 与 scGAN、scDesign3 比较 SCC、MMD、LISI、random-forest AUC 和 UMAP（`paper.md:162-168`）。
- **指定细胞类型生成：** 在 Tabula Muris 和 PBMC68k 上用 CellTypist 与 KNN 检查生成细胞是否像目标细胞类型（`paper.md:174-189`, `paper.md:308-339`）。
- **多条件 OOD 生成：** 组合“器官”和“细胞类型”两个分类器，生成训练集中没有的器官-细胞类型组合，并用 marker gene 表达比较（`paper.md:195-207`）。
- **发育中间态生成：** 在 Waddington-OT 数据上生成缺失时间点或连续中间状态，用 MMD、LISI、UMAP 和 pseudotime 评价（`paper.md:213-225`）。

### 代码复现要点

代码库提供了核心实现，但不是开箱即复现实验图表：README 要求下载论文数据、准备外部 SCimilarity 权重、修改本地路径、训练 autoencoder/diffusion/classifier，再用脚本采样 latent embedding，并通过 notebooks 解码和画图（`scDiffusion/README.md:27-78`）。因此，本 workspace 对代码匹配的判断是 **medium fidelity**：核心算法在代码中存在，但论文 checkpoint、完整图表流水线和部分评估流程需要外部资源与手工配置。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## scDiffusion Summary

### Overview

scDiffusion is a latent-diffusion framework for conditional generation of single-cell RNA-seq data. It embeds normalized gene-expression profiles with a finetuned SCimilarity-like autoencoder, trains a skip-connected MLP denoiser over 128-dimensional latent embeddings, and uses classifier gradients to guide generation toward requested cell types, organ/cell-type combinations, or interpolated developmental states (`paper.md:41-56`, `paper.md:62-132`).

### Why it matters

The paper addresses a practical single-cell bottleneck: high-quality scRNA-seq data are costly and rare cell states may be under-sampled (`paper.md:11-17`). scDiffusion is designed to augment data in silico while controlling generated conditions. The reported experiments cover unconditional realism, conditional cell-type synthesis, out-of-distribution multi-condition synthesis, and Waddington-OT developmental interpolation (`paper.md:150-156`).

### Method highlights

- **Latent autoencoder front-end:** input expression is normalized to total count 1e4, log-transformed, and encoded into a 128-dimensional latent vector (`paper.md:50-56`; `scDiffusion/guided_diffusion/cell_datasets_loader.py:61-88`).
- **Denoising network:** a fully connected skip-connected model predicts diffusion noise on latent embeddings (`paper.md:62-96`; `scDiffusion/guided_diffusion/cell_model.py:45-92`).
- **Classifier guidance:** separate classifiers are trained on noised embeddings and provide gradients during sampling (`paper.md:102-112`; `scDiffusion/classifier_train.py:109-117`; `scDiffusion/classifier_sample.py:134-142`).
- **Multiple conditions:** two classifiers can be combined by summing gradients with different weights (`paper.md:115-115`; `scDiffusion/classifier_sample.py:60-74`).
- **Gradient Interpolation:** two target-state gradients are weighted and applied from a noised real latent state to synthesize continuous intermediate states (`paper.md:118-132`; `scDiffusion/classifier_sample.py:88-106`, `scDiffusion/classifier_sample.py:151-225`).

### Results reported by the paper

The paper reports that scDiffusion generated realistic scRNA-seq data compared with scGAN and scDesign3 under SCC, MMD, LISI, random-forest AUC, and UMAP inspections (`paper.md:162-168`). For conditional generation, CellTypist and KNN evaluations are reported on Tabula Muris and PBMC68k (`paper.md:174-189`, `paper.md:308-339`). For OOD generation, marker-gene boxplots compare generated organ/cell-type combinations with real target cells and other cells (`paper.md:195-207`). For interpolation, MMD/LISI/UMAP and pseudotime analyses evaluate missing or intermediate Waddington-OT states (`paper.md:213-225`).

### Code availability and reproducibility

The repository `https://github.com/EperLuo/scDiffusion` was cloned at commit `e20ee19090739a874fd8ae001d8337e4d480e52b`. Code-paper fidelity is **medium**: the core autoencoder, diffusion, classifier guidance, multi-condition guidance, and interpolation mechanisms are present (`doc_code.md`). However, trained checkpoints are not included, sample scripts save latent `.npz` embeddings by default, and the README expects users to download external h5ad datasets and SCimilarity weights and to edit local paths before running (`scDiffusion/README.md:27-78`). Figure/table reproduction is mainly through notebooks in `exp_script/`, not a single end-to-end script.

### Main limitations / open gaps

- The paper's exact variance notation with `$w$` maps only partially to code: the code uses an `nw` exponent over diffusion `log_variance`, not a one-to-one `exp(w beta_i)` implementation (`doc_code.md`).
- Local figure files were recovered from arXiv HTML and visually matched to captions, but the converted markdown did not contain original inline image links (`figure_analysis.md`).
- No separate supplementary markdown exists; supplementary tables and captions are embedded at the end of `paper.md` (`paper.md:305-357`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
