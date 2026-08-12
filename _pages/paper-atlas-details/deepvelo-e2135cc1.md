---
layout: default
permalink: /paper-atlas/deepvelo-e2135cc1/
title: "DeepVelo"
nav: false
description: "DeepVelo 解决的是单细胞转录组动态建模问题。普通 scRNA-seq 只能观察到很多细胞在某一时刻的表达快照，不能连续追踪同一个细胞随时间变化。RNA velocity 能估计短时间的瞬时变化，但论文认为它不足以描述更长时间尺度的发育轨迹；线性 ODE 或稀疏向量场方法又可能低估非线性调控关系。"
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
      <span>Science Advances · 2022</span>
    </div>
    <h1>DeepVelo</h1>
    <p>DeepVelo: Single-cell transcriptomic deep velocity field learning with neural ordinary differential equations</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1126/sciadv.abq3745" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DeepVelo 方法中文解读

### 这篇文章解决什么问题

DeepVelo 解决的是单细胞转录组动态建模问题。普通 scRNA-seq 只能观察到很多细胞在某一时刻的表达快照，不能连续追踪同一个细胞随时间变化。RNA velocity 能估计短时间的瞬时变化，但论文认为它不足以描述更长时间尺度的发育轨迹；线性 ODE 或稀疏向量场方法又可能低估非线性调控关系（`paper source/science_html/paper.md:18-24`）。

DeepVelo 的核心想法是：学习一个从细胞表达状态到 RNA velocity 的神经网络函数，然后把这个函数当作微分方程的右端项，用 ODE 求解器连续模拟细胞状态变化（`paper source/science_html/paper.md:24-36`）。

### 输入、输出和基本假设

输入是单细胞表达矩阵，以及通过 spliced/unspliced reads 推断出来的 RNA velocity。论文使用 Cellranger 和 velocyto 处理原始数据，再按 scVelo 推荐流程筛选高变基因、归一化、计算 30 个 PC 和 30 个近邻的 moments，并用 dynamical mode 得到 velocity；只有 velocity genes 被用于 neural ODE 特征（`paper source/science_html/paper.md:154-157`）。

输出不是一个离散的伪时间排序，而是一个可以对任意细胞状态预测速度的连续向量场。这个向量场可以用于：

- 向前模拟细胞未来状态；
- 反向模拟 terminal cell 的历史轨迹；
- 计算 CCI 来衡量细胞状态不稳定性；
- 做 in silico perturbation 来找发育 driver genes；
- 评估 velocity prediction MSE。

### 模型结构

论文把模型描述为 VAE。VAE 接收基因表达状态 `x`，输出 RNA velocity。编码器把高维表达压缩到低维 latent representation，解码器从 latent representation 预测 velocity。论文说明使用 TensorFlow/Keras、64 维隐藏层、16 维 latent layer、ReLU、MSE reconstruction loss、Adam、L1 activity regularization `lambda = 1e-6`、小学习率和 early stopping（`paper source/science_html/paper.md:166-175`）。

代码中 `deepvelo/code/vae.py` 实现了这个核心组件：`create_encoder` 生成 encoder 和采样层（`deepvelo/code/vae.py:31-40`），`create_decoder` 生成 decoder（`deepvelo/code/vae.py:46-54`），`VAE.train_step` 计算 MSE reconstruction loss、KL loss、total loss 并更新参数（`deepvelo/code/vae.py:80-100`）。

一个重要差异是：公开 notebooks 为了加速 integration，很多地方把 VAE 暂时替换成普通 autoencoder。notebook 明确说 VAE 反复调用计算量大，因此教程中临时使用 normal AE，结果相似（`scratch/notebook_code/Figure2.py.txt:67-78`；`scratch/notebook_code/Figure3.py.txt:59-70`）。所以这份代码能解释方法核心，但不是完整打包的软件实现。

### 计算流程

```text
单细胞表达矩阵 + spliced/unspliced counts
  -> scVelo 预处理并估计 RNA velocity
  -> X = velocity genes 的表达状态
  -> Y = velocity genes 的 RNA velocity
  -> 训练 AE/VAE: f_A(x) -> dx/dt
  -> 用 dx/dt = scaled f_A(x) 定义 ODE
  -> solve_ivp 前向或后向积分
  -> 每隔若干步投影到 PCA 空间，用 KNN reference cell 校正漂移
  -> 得到模拟轨迹、CCI、terminal fate、扰动结果、动态共表达网络
```

论文强调预测 velocity 要先做线性缩放，并用 SciPy 的 ODE solvers 积分；DOP853 更准确但慢，RK23 更快（`paper source/science_html/paper.md:190-193`）。notebook 中也实现了 scaling factor、`raw_ae`、`solve_ivp` 和 KNN reference correction（`scratch/notebook_code/Figure2.py.txt:135-176`）。

### CCI：细胞状态不稳定性

CCI 是 cell criticality index，用来衡量一个细胞状态未来会发生多大变化。论文把它定义为沿模拟轨迹相邻时间点表达分布之间的累计 KL divergence；变化大的细胞 CCI 高，变化小的细胞 CCI 低（`paper source/science_html/paper.md:67-70`; `paper source/science_html/paper.md:217-220`）。

代码中 CCI 的实现很直接：把每个模拟路径中相邻两个状态归一化成分布，用 `scipy.special.kl_div(a, b)` 计算 KL divergence，处理 infinity 后求和（`scratch/notebook_code/Figure2.py.txt:445-452`）。

### 扰动实验

DeepVelo 的 in silico perturbation 分三步：先选上游祖细胞作为初始状态并自然演化，得到 baseline terminal fate；再找与不同 terminal fate 相关的初始状态 DE genes；最后逐个扰动 trajectory-specific DE gene，如果目标 terminal fate 的比例显著升高，就把这个基因归为 developmental driver gene（`paper source/science_html/paper.md:232-241`）。

终末状态分类使用 KNN：把模拟出的细胞状态投影到前 30 个 PC，用 `K = 30` 的 KNN classifier 预测 cell type（`paper source/science_html/paper.md:208-211`）。代码对应 `KNeighborsClassifier(n_neighbors=30)`（`scratch/notebook_code/Figure2.py.txt:663-667`）。

### 主要结果怎么理解

在胰腺发育数据中，Fig. 2 显示 DeepVelo 可以从一个 out-of-sample 初始状态模拟到 beta cell 方向；CCI 在 endocrine progenitor/pre-endocrine 区域较高；扰动后 alpha cell 终末比例从图中 baseline 的 47% 升到 61%。在 dentate gyrus 中，Fig. 3 显示 Nbl2 相关轨迹、Nbl1/Nbl2 转换附近的高 CCI，以及扰动后 CA fate 比例升高。在 neocortex 中，Fig. 4 显示 biphasic fate-commitment dynamic。Fig. 5 显示 retrograde trajectories 能得到更清晰的 gene coexpression modules，并且 VAE 的 validation MSE 低于 linear 和 SparseVFC。

### 复现性与局限

论文提供了数据 accession 和 GitHub/Zenodo 源码链接（`paper source/science_html/paper.md:271-271`）。当前 GitHub snapshot 包含 `vae.py` 和 Figure 2/Figure 3 notebooks，但 README 明确说这是 raw notebooks，软件包仍在整理中（`deepvelo/README.md:5-7`）。因此可以复现和检查核心分析逻辑，但不是开箱即用的完整工具。

另一个限制是 Science HTML 转换把很多公式变成了 `No alternative text available`，包括 VAE、loss、CCI 和 retrograde trajectory 的显示公式位置。因此本分析只引用论文 prose 和代码行为，不重建缺失公式。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DeepVelo Summary

DeepVelo addresses the problem that most single-cell RNA-seq experiments provide static snapshots, while RNA velocity gives only short-horizon instantaneous changes. The paper argues that pseudotime and discrete-transition methods such as Monocle and Palantir do not model continuous-time transcriptome dynamics, and that linear ODE or sparse vector-field methods can miss nonlinear gene-regulatory relationships (`paper source/science_html/paper.md:18-24`).

The proposed method trains a neural velocity predictor, described as a VAE, to map a cell's gene-expression state to RNA velocity and then uses that predictor as the right-hand side of an ODE for forward or backward simulation (`paper source/science_html/paper.md:24-36`). The main downstream analyses are trajectory extrapolation, cell criticality index (CCI) scoring, in silico perturbation of initial gene-expression states, retrograde trajectory simulation for coexpression networks, and velocity-field benchmarking (`paper source/science_html/paper.md:44-79`; `paper source/science_html/paper.md:119-130`).

The technical pipeline starts from scRNA-seq counts, computes spliced/unspliced RNA velocity using scVelo dynamical mode, keeps velocity genes as neural-ODE features, trains an autoencoder/VAE velocity model, and integrates predicted velocities with SciPy ODE solvers. To reduce drift, DeepVelo adds noise during denoising training and periodically snaps simulated states back toward the empirical manifold using KNN reference cells in PCA space (`paper source/science_html/paper.md:154-157`; `paper source/science_html/paper.md:190-205`).

The paper evaluates the method on mouse pancreatic endocrinogenesis, mouse dentate gyrus, developing mouse neocortex, mouse gastrulation, human forebrain, and a bone-marrow benchmark. It reports that DeepVelo can simulate out-of-sample trajectories, identify high-criticality fate-commitment regions, shift terminal fate proportions under driver-gene perturbations, improve dynamic coexpression module enrichment, and reduce out-of-sample velocity-prediction MSE by at least 50% versus linear and SparseVFC baselines (`paper source/science_html/paper.md:27-27`; `paper source/science_html/paper.md:119-130`).

Reproducibility is mixed. The paper provides dataset accessions and points to Zenodo/GitHub source code (`paper source/science_html/paper.md:271-271`), and the GitHub snapshot contains `vae.py` plus Figure 2/Figure 3 notebooks. However, the repository itself says the publication code is temporarily deposited raw notebooks rather than a packaged tool (`deepvelo/README.md:5-7`). The public notebooks verify many core mechanics, including scVelo preprocessing, ODE integration, CCI calculation, and perturbation classification, but they often substitute a normal autoencoder for the VAE described in the paper (`scratch/notebook_code/Figure2.py.txt:67-78`). Code-paper fidelity is therefore **medium**.

Major caveats: the Science HTML conversion lost many mathematical formulas as `No alternative text available`, so exact equations 1-20 are not recoverable from the acquired markdown. The implementation analysis preserves those as `MISSING` rather than reconstructing them from prose.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
