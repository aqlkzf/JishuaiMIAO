---
layout: default
permalink: /paper-atlas/ols-1c535dad/
title: "OLS"
nav: false
description: "传统单分子追踪常在“视野与通量”和“背景抑制、定位精度、时间分辨率”之间取舍。OLS（oblique line scan，倾斜线扫描）把单物镜倾斜光片、线扫描和相机滚动快门同步起来，在约 250 × 190 µm² 的大视野内实现最高 1,250 Hz 采集，从而同时观察许多细胞及快速扩散蛋白。 检测在 11 × 11 像素窗口中进行；细胞 SMT 与溶液 isSMT 的阈值分别为 14 和 16。轨迹连接限制为细胞中 1."
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>OLS</h1>
    <p>Oblique line scan illumination enables expansive, accurate and sensitive single-protein measurements in solution and in living cells</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## OLS 方法中文解读

### 它解决什么问题

传统单分子追踪常在“视野与通量”和“背景抑制、定位精度、时间分辨率”之间取舍。OLS（oblique line scan，倾斜线扫描）把单物镜倾斜光片、线扫描和相机滚动快门同步起来，在约 250 × 190 µm² 的大视野内实现最高 1,250 Hz 采集，从而同时观察许多细胞及快速扩散蛋白。

### 核心流程

```text
HaloTag 标记样品
  -> 倾斜光片逐线扫描 + 滚动快门同步探测
  -> 高速荧光时间序列
  -> 似然比检测亮点
  -> 径向对称初定位 + 二维积分高斯精定位
  -> 限制搜索半径和断帧数的轨迹连接
  -> 核/胞质语义分割与轨迹归属
  -> MSD 与变分贝叶斯 state arrays
  -> 扩散状态分布、细胞/孔/剂量统计
```

检测在 11 × 11 像素窗口中进行；细胞 SMT 与溶液 isSMT 的阈值分别为 14 和 16。轨迹连接限制为细胞中 1.25 µm、溶液中 2.5 µm，最多跨两帧。单一状态可用 $D_{est}=MSD_{2D}/(4\Delta t)$，多状态则在扩散系数与定位误差网格上用 Dirichlet 过程混合的 state arrays 估计后验占比。

### 为什么有效

OLS 用薄而倾斜的扫描光片抑制离焦背景，并让相机只读出与光线位置匹配的滚动狭缝；因此既提高 SNR，又减少持续照明造成的运动模糊。大视野一次可覆盖大量细胞，论文进一步表明细胞间差异比 FOV 或孔间差异更大，因此高通量不是附属优点，而是可靠刻画异质性的关键。

### 主要结果

- 四台显微镜得到相近的 KEAP1 剂量响应，说明系统具有跨仪器一致性。
- 约 400 Hz 才能充分看到 KI-696 诱导的快速 KEAP1 状态，说明低帧率会系统性低估快扩散成分。
- OLS 区分 VCP 的核、核周和胞质运动，并将 PCNA 动力学与细胞周期分类结合。
- isSMT 的校正扩散系数与 Stokes–Einstein 理论一致，并检测 TCF4–β-catenin 结合及竞争性破坏。
- 同一平台还演示了双色 SMT、约 15 nm 定位精度的 STORM，以及 SMT/FRAP 联合实验。

### 代码与复现边界

Zenodo 包提供测试影片、Hoechst 分割模型、二进制 `mindlt` wheels 和端到端 Python 示例。示例明确调用分割、检测-定位-连接、掩膜归属与 state arrays，关键参数与论文基本对应。但核心算法没有源码，显微镜控制脚本和研究规模原始数据也未公开。因此可以做“小样例 API 级复现”，不能完成源码审计或完整研究复现。

### 局限

提高帧率会压缩可用视野高度；Brownian 混合模型未处理限制扩散、环境各向异性和定向运输；大视野高速时间序列带来显著存储与计算压力；此外，软件不能替代专用光学硬件、标记与校准条件。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## OLS paper summary

### What problem it solves

Single-molecule tracking usually trades field of view and throughput against background rejection, localization quality and temporal resolution. OLS combines an inclined, scanned single-objective light sheet with synchronized rolling-shutter detection to image a 250 × 190 µm² field at up to 1,250 Hz, enabling high-throughput measurements of fast protein motion in cells and in solution.

### Method and evidence

The computational workflow detects emitters with a likelihood-ratio test, refines positions with integrated-Gaussian fitting, links positions into trajectories, assigns them to learned nuclear/cytoplasmic masks and resolves diffusion subpopulations with variational Bayesian state arrays. The experiments show reproducible measurements across four microscopes; drug-induced KEAP1 dynamics require roughly 400 Hz sampling; OLS resolves compartment-dependent VCP and cell-cycle-dependent PCNA motion; and in-solution SMT tracks TCF4–β-catenin association and competitive disruption. It also supports two-color SMT, STORM with about 15 nm lateral localization precision, and SMT/FRAP.

### Reproducibility

Reproducibility is **3/5**. Nature HTML, all 13 main/extended figures, a 373 MB Zenodo package, a TensorFlow segmentation model, example TIFFs and an end-to-end script are available. The example closely mirrors the paper’s analysis interfaces and key parameters. However, `mindlt` is supplied only as compiled wheels, the optical-control/MicroManager code is absent, the study-scale raw data require an agreement, and no repository commit exists. Thus API-level rerunning is supported on the example dataset, while independent inspection or full-study reproduction is not.

### Main caveats

OLS speed reduces usable field height; its state model assumes Brownian mixtures and does not model confinement, anisotropy or directed motion; and the data volume can be prohibitive. Reported biological sensitivity also depends on specialized microscope hardware, labeling and calibration that are not captured by the software archive alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
