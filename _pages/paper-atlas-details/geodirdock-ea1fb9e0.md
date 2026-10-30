---
layout: default
permalink: /paper-atlas/geodirdock-ea1fb9e0/
title: "GeoDirDock"
nav: false
wide: true
description: "蛋白质-配体对接要同时决定配体放在哪里、朝向哪里，以及可旋转键取什么角度。DiffDock 一类盲扩散方法可以从噪声生成姿态，但在复杂体系中可能定位到错误的口袋，或得到化学上不合理的内部构象。GeoDirDock（GDD）把专家提供的口袋、方向和扭转角先验加入反向扩散过程，让每一步更新沿着目标区域的测地线前进。Nature 页面给出的摘要称，GDD 在 RMSD 和物理姿态合理性上优于盲对接；"
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
      <span>Computational Tools</span>
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>GeoDirDock</h1>
    <p>Informed protein-ligand docking via geodesic guidance in translational, rotational and torsional spaces</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-025-01091-x" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GeoDirDock">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/NBDsoftware/GDD" target="_blank" rel="noopener noreferrer" aria-label="Open code for GeoDirDock">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GeoDirDock 方法说明

### 1. 这篇工作解决什么问题？

蛋白质-配体对接要同时决定配体放在哪里、朝向哪里，以及可旋转键取什么角度。DiffDock 一类盲扩散方法可以从噪声生成姿态，但在复杂体系中可能定位到错误的口袋，或得到化学上不合理的内部构象。GeoDirDock（GDD）把专家提供的口袋、方向和扭转角先验加入反向扩散过程，让每一步更新沿着目标区域的测地线前进。Nature 页面给出的摘要称，GDD 在 RMSD 和物理姿态合理性上优于盲对接；详细公式和表格来自作者的 Supplementary information。

### 2. 输入、输出和先验

输入包括蛋白结构、配体 SMILES/文件、可选蛋白序列，以及一个 CSV 和预处理目录。仓库 README 规定了三类区域文件：

- `sph<ligand>.csv`：平移球的中心 `(x,y,z)` 和半径 `R`；
- `rot<ligand>.json`：两个取向轴的极角/方位角区间；
- `tor<ligand>.json`：每个可旋转键的一个或多个圆周角区间。

输出是一组配体三维坐标，可选地保存反向扩散的 PDB 轨迹，并用 confidence model 对候选姿态排序。代码接口见 `GDD/README.md:23-78` 和 `GDD/utils/parsing.py:384-748`。

### 3. 三个空间中的测地线引导

#### 平移：T3

令配体质心为 $p_t$，目标球为 $B(\epsilon;r)$。若质心已经在球内，就关闭平移引导；否则

$$v^{tr}_{dir}=\frac{\epsilon-p_t}{\|\epsilon-p_t\|_2},\qquad
\alpha_{tr}=\|\epsilon-p_t\|_2.$$

因此模型的平移 score 仍然保留，但更新方向会向球心移动。实现位于 `GDD/utils/guidance.py:183-215`。

#### 旋转：SO(3) 和 S2

直接在 SO(3) 中描述“正确朝向”比较困难。GDD 先把配体质心到第一个原子的向量作为第一根轴，再用质心到第二个原子向量的叉积构造第二根轴，以避免镜像歧义。两个轴都归一化后成为 $S^2$ 上的点。

球面点用球坐标映射为

$$v(\phi,\theta)=(\cos\phi\sin\theta,\sin\phi\sin\theta,\cos\theta).$$

当前点 $v_\alpha$ 到目标点 $v_\beta$ 的大圆路径使用

$$u=\frac{v_\beta-(v_\beta^Tv_\alpha)v_\alpha}
{\|v_\beta-(v_\beta^Tv_\alpha)v_\alpha\|_2},
\quad g(t)=\cos(t)v_\alpha+\sin(t)u,$$

以及 $t^*=\arccos(v_\beta^Tv_\alpha)$。代码在 `guidance.py:219-331` 中计算轴、目标区域中心、切向旋转轴，并顺序乘上两个 axis-angle 旋转矩阵。当前实现的 docstring 明确说明它使用区域中心，而不是每个边界的最近点，这是理解论文公式与代码差异的关键。

#### 扭转：SO(2)m 和 hypertorus

每个可旋转键是一个圆周角，因此 $SO(2)^m\simeq T^m=\mathbb{R}^m/2\pi\mathbb{Z}^m$。对每个维度，代码检查角度是否落在任一允许 sector 中；若不在，就比较直接距离和跨越 $2\pi$ 的距离，选择最近边界，得到最短路径的单位切向量和长度。实现见 `GDD/utils/torus_geodesics.py:8-92` 和 `guidance.py:356-389`。

### 4. 反向扩散流程

```text
蛋白 + 配体 + sph/rot/tor 区域
          |
          v
构建分子图，复制 N 个候选并随机化扭转角/刚体旋转
          |
          v
每个 denoising step:
  score model 预测平移、旋转、扭转 score
  按 schedule 生成 score 漂移和随机噪声（或 ODE 漂移）
  提取当前状态并检查是否在目标区域
  若不在：计算测地线方向/距离并混合更新
  应用刚体变换、扭转键旋转和 Kabsch 对齐
          |
          v
候选姿态 + 可选 confidence 排序和 PDB 输出
```

`randomize_position` 在 $[-\pi,\pi]$ 随机化每根可旋转键并施加随机刚体旋转（`utils/sampling.py:16-45`）。`sampling` 在每个时间点调用模型（`sampling.py:87-126`），再计算三个空间的 score/noise 扰动（`sampling.py:143-186`）。`modify_conformer` 只有在状态离开区域时才调用对应 guider；扭转更新随后应用到 `mask_rotate` 选出的子图，并以 Kabsch 变换重新对齐（`utils/diffusion_utils.py:58-195`）。

平移和扭转默认使用 `m0`：

$$u_{guided}=(1-\gamma)u_{model}+\gamma v_{dir}\alpha.$$

代码还提供 `m1`-`m4`，分别改变是否使用测地线距离、模型更新幅度，以及方向/距离是否独立混合（`guidance.py:430-471`）。

### 5. 评估结果如何理解？

作者比较 DiffDock、只使用平移引导的 GDD-TR 和三种空间都引导的 GDD-Full，数据包括 PDBBind 衍生测试集、DockGen、PoseBusters 和 D3R 相关设置。指标包括 RMSD、低于 2 Å 的比例、中位 RMSD、旋转/扭转 MSE 和运行时间。

在 DockGen 的 20-step/40-sample 设置，GDD-Full 的 top-1/top-5 `<2 Å` 比例为 17.98%/24.16%，DiffDock 为 3.93%/8.99%；中位 RMSD 为 4.75/6.08 Å。PoseBusters 中对应比例为 59.01%/65.34% 与 33.26%/43.79%，中位 RMSD 为 1.55/3.89 Å。Supplementary Table 2 还显示，GDD-Full 的旋转和扭转 MSE 远低于 DiffDock，说明改进不只是把配体移进正确口袋，也改善了内部姿态。

运行时间有小幅开销：Supplementary Table 1 的 20-step/40-sample 平均时间为 DiffDock 92 s、GDD-TR 94 s、GDD-Full 101 s。半径扰动实验显示平移先验较稳健；旋转区域过宽（$\eta=1.5$）会损害效果；扭转区域对模糊更稳健。增大 $\gamma$ 通常主要加快收敛，而中等值已经带来主要精度收益。

### 6. 复现边界

代码仓库和 Zenodo 记录公开，快照包含环境文件、运行示例和训练 checkpoint。Nature 主文是订阅预览，完整训练架构、损失、数据切分和 confidence 训练细节在现有主文 Markdown 中没有出现；补充材料以 PDF 保留并用于核对公式和结果。因此这些内容在分析中标记为 `Not found`，不能从代码或摘要中臆测补全。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## GeoDirDock Summary

### Problem

Blind diffusion docking can place a ligand in the wrong pocket or produce inaccurate internal orientations, especially for difficult protein-ligand systems. GeoDirDock (GDD) adds expert spatial information to DiffDock's denoising process instead of relying only on a learned score and an unconstrained search.

### Method

GDD describes desired regions in translation, orientation and rotatable-bond torsion spaces. Translation uses a binding sphere in $T^3$; orientation uses two ligand axes represented as points on $S^2$ and shortest great-circle directions; torsions use shortest paths on the hypertorus $T^m=SO(2)^m$. At each reverse-diffusion step, a geodesic direction and distance are blended with the model's update by a guidance strength $\gamma$. The resulting rigid transform and torsion rotations are applied to each sampled ligand pose, with Kabsch alignment after flexible updates. The detailed equations are in Supplementary Sections A.1-A.3 and the corresponding implementation is in `GDD/utils/guidance.py` and `GDD/utils/diffusion_utils.py`.

### Evaluation

The authors compare DiffDock, translation-only GDD (GDD-TR) and full GDD on PDBBind-derived tests, DockGen and PoseBusters, using RMSD, below-2-Å success, median RMSD, rotation/torsion MSE and runtime. In the supplementary DockGen table, GDD-Full with 20 steps and 40 samples reaches 17.98% top-1 and 24.16% top-5 poses below 2 Å, versus 3.93% and 8.99% for DiffDock. On PoseBusters the corresponding values are 59.01% and 65.34%, versus 33.26% and 43.79%, with median RMSD 1.55 Å versus 3.89 Å. Full guidance also reduces rotation and torsion MSE by roughly two orders of magnitude in the reported Holo/Apo comparisons. Runtime overhead is modest in the supplementary study (+9.78% for the 20-40 protocol).

The ablations show that translation-radius fuzzing is robust, rotation becomes worse for very broad angular regions, torsion is more robust to broad regions, and moderate guidance strengths improve accuracy while larger values mainly accelerate convergence. The main figures visually show narrower low-error distributions for guided poses and reduced top-hit RMSD/torsion MSE.

### Reproducibility (3/5)

The Nature page links the public GitHub repository `NBDsoftware/GDD` and Zenodo record, and the snapshot includes an environment file, command-line example and trained score/confidence checkpoints. The code-paper match is medium: core guidance equations and inference paths are implemented, but the acquired article is a subscription preview and the full training, preprocessing, split and confidence-model details are not present in the available primary markdown. The supplementary information is retained as a PDF and was text-extracted for source verification; no environment, checkpoint or benchmark execution was performed in this workspace.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
