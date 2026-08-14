---
layout: default
permalink: /paper-atlas/trajcast-8fa1ae05/
title: "TrajCast"
nav: false
wide: true
description: "传统分子动力学（MD）每一步先计算原子间力，再以约 0.5-1 fs 的小时间步积分牛顿方程。即使机器学习势能面显著降低了力计算成本，积分步数仍然很大。TrajCast 的目标是直接学习“当前完整状态到下一完整状态”的映射，绕过逐步算力和数值积分。 输入是每个原子的元素 Zi、位置 \\mathbf ri(t) 和速度 \\mathbf vi(t)；输出是较大间隔 \\Delta t 后的位置和速度。"
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
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>TrajCast</h1>
    <p>Force-free molecular dynamics through autoregressive equivariant networks</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-026-01227-7" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for TrajCast">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/IBM/trajcast" target="_blank" rel="noopener noreferrer" aria-label="Open code for TrajCast">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TrajCast 方法解读

### 问题

传统分子动力学（MD）每一步先计算原子间力，再以约 0.5-1 fs 的小时间步积分牛顿方程。即使机器学习势能面显著降低了力计算成本，积分步数仍然很大。TrajCast 的目标是直接学习“当前完整状态到下一完整状态”的映射，绕过逐步算力和数值积分。

### 核心创新

输入是每个原子的元素 $Z_i$、位置 $\mathbf r_i(t)$ 和速度 $\mathbf v_i(t)$；输出是较大间隔 $\Delta t$ 后的位置和速度。模型使用 O(3) 等变消息传递网络，因此旋转或反射输入构型时，向量输出会以相同方式变换。它并不假定固定的化学键，这一点对反应性体系尤其重要。

### 计算流程

```text
Z, r(t), v(t)
  -> 截断半径图
  -> 元素 one-hot、边长径向基、速度高斯基、球谐方向编码
  -> 多层速度条件化的等变消息传递
  -> 读出位移与速度更新
  -> 线动量/可选角动量约束
  -> r(t+Delta t), v(t+Delta t)
  -> 自回归地作为下一步输入
```

边 $i\leftarrow j$ 的消息采用 Clebsch-Gordan 张量积，把邻居表征、由边长决定的径向过滤器和边方向球谐函数组合：

$$m_{ij}^{k}=\mathbf h_j^k\otimes_{\rm CG}^{\mathrm{MLP}_e^k(R(r_{ij}))}\mathbf Y(\hat{\mathbf r}_{ij}).$$

速度既通过大小的元素相关高斯基编码，也通过方向的球谐编码进入网络。最后的约束层修正读出的位移和速度，以满足总线动量及配置允许时的角动量约束。

### NVE 训练与 NVT 推理

论文在 NVE 轨迹上训练一步状态预测器。长时间 NVT 推理时，每一次网络前向预测后使用 CSVR 恒温器重缩放速度，使温度围绕目标值采样。温度来自动能：

$$T=\frac{2K}{N_f k_B},\qquad K=\frac12\sum_i m_i|\mathbf v_i|^2.$$

这解释了为什么论文比较的是统计系综性质，而不是带随机恒温器的逐帧轨迹。

### 实验结论

论文在对乙酰氨基酚、alpha-石英和液态水上分别使用 7、30、5 fs 的预测间隔。图 2-4 展示了 VDOS、能量分布、自由能面、MSD 和 RDF 与参考 MD 的接近程度。水的零样本测试从 300 K 冷却到 180 K，图 5 显示扩散、RDF 和结构序参量与 MD 基本一致。图 6 同时指出关键边界：更长的预测间隔会放大速度误差，单步误差小并不保证自回归轨迹稳定。

### 复现与局限

本地 GitHub 快照验证了编码、等变消息传递、位移/速度读出、守恒层及预测循环的主要结构。未在限定代码映射中确认论文训练损失的精确权重、每张图对应的配置或权重文件。由于模型不预测力，压力等力相关性质不可直接计算，论文目前只展示 NVE/NVT，而非 NpT。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TrajCast

### Overview

TrajCast is an autoregressive O(3)-equivariant message-passing neural network for molecular dynamics. Instead of predicting forces and numerically integrating at sub-femtosecond steps, it receives atom types, positions, and velocities and directly forecasts the next positions and velocities. Its local graph construction is intended to support size transfer, while explicit vector equivariance and conservation correction encode physical structure.

### Why It Matters

Machine-learning interatomic potentials make force evaluation cheaper but retain the small integration interval. Previous force-free generators often omit momenta, fix particle count, require much larger data sets, or impose bond/motion assumptions. TrajCast models full phase-space state and uses autoregressive rollout, so it can evaluate dynamical as well as structural observables.

### Evidence from the Paper

The authors benchmark paracetamol, alpha-quartz, and liquid water using 7, 30, and 5 fs forecast horizons, respectively. They report close VDOS and energy distributions for paracetamol/quartz, and near-overlapping water VDOS/RDFs with diffusion coefficients of $2.18\pm0.19$ (TrajCast) and $1.84\pm0.03\times10^{-9}\,{\rm m^2s^{-1}}$ (MD). A water model trained at ambient conditions remained stable during a 300-to-180 K cooling rollout and followed MD structural order and diffusion trends. The reported throughput is over 15 ns/day for a quartz system above 4,300 atoms and over 1 ns/day for water above 5,000 atoms.

### Reproducibility

The linked GitHub snapshot is present locally at commit `c52f107a02176671b21a420b2d4c67e0327b04f7`. Source-backed code matches the main architecture: type/velocity/edge encoding, residual equivariant message passing, displacement/velocity readout, conservation, and forecast-time CSVR thermostat support. The exact training loss mapping, paper-specific checkpoint/configuration, and execution of a figure reproduction are **Not found** in this analysis. The paper points to Hugging Face model/dataset releases and a Zenodo code record; no supplementary Markdown was acquired.

### Limitations

The force-free formulation cannot directly produce pressure or other force-related observables and is demonstrated for NVE/NVT rather than NpT. Forecast horizon is fixed per trained model; Fig. 6 shows that autoregressive stability deteriorates as horizon-related one-step error grows.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
