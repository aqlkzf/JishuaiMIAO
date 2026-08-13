---
layout: default
permalink: /paper-atlas/cab-olst-edea5647/
title: "CAB-OLST"
nav: false
wide: true
description: "全脑成像既要覆盖厘米尺度，又要看清细胞、细轴突和树突棘。传统高斯光片扩大视野时会变厚，点扫描层析速度和信号积分受限，而物镜工作距离又限制成像深度。CAB-OLST 的核心目标是同时提高视野、分辨率、信噪比和通量。 用扫描 Airy 光束形成长景深薄光片，景深比扫描高斯光束提高十倍以上。 将 Airy 相位旋转 45°，使探测平面上的光片变直，从而可用相机滚动快门形成 13 μm 虚拟狭缝，抑制旁瓣和离焦背景。"
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>CAB-OLST</h1>
    <p>Confocal Airy beam oblique light-sheet tomography for brain-wide cell type distribution and morphology</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/coreyelowsky/OLSTv2" target="_blank" rel="noopener noreferrer" aria-label="Open code for CAB-OLST">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CAB-OLST 方法解读

### 它解决什么问题

全脑成像既要覆盖厘米尺度，又要看清细胞、细轴突和树突棘。传统高斯光片扩大视野时会变厚，点扫描层析速度和信号积分受限，而物镜工作距离又限制成像深度。CAB-OLST 的核心目标是同时提高视野、分辨率、信噪比和通量。

### 核心创新

1. 用扫描 Airy 光束形成长景深薄光片，景深比扫描高斯光束提高十倍以上。
2. 将 Airy 相位旋转 45°，使探测平面上的光片变直，从而可用相机滚动快门形成 13 μm 虚拟狭缝，抑制旁瓣和离焦背景。
3. 使用倒置 SPIM 结构，让样本能在 xy 方向大范围移动。
4. 每完成一层成像就用振动切片机切除 300 μm，使下一轮始终在组织表面附近成像，避免深层散射和像差积累。

SLM 上的立方相位为

$$
\varnothing(x,y)=\alpha k_0(u^3+v^3),\qquad k_0=\frac{2\pi}{\lambda}.
$$

论文在 640 nm 使用 $\alpha=4.32$，在 488 nm 使用 $\alpha=2.66$，并通过不同闪耀光栅参数补偿双色位置偏差。

### 完整流程

```text
透明化并荧光标记的全脑
 -> Airy 光片 + 滚动快门共聚焦探测
 -> x 方向采集单个体栈，y 方向拼成马赛克
 -> 切除 300 μm 组织并重复 45–47 次
 -> 拼接、去斜、去条纹、坐标重排
 -> 全脑配准与脑区注释
 -> 3D U-Net 细胞计数 或 Vaa3D 单神经元追踪
```

单视野为 530 × 530 μm；x 步长为 1–2.5 μm，25× 配置通常使用 25 个 y 位置、间隔 500 μm。OLSTv2 代码能够读取 BigStitcher XML、合并平铺体块，并通过重采样、翻转、剪切和旋转把斜视数据变换到冠状/矢状坐标；但仪器同步控制并未包含在该仓库中。

### 两条分析分支

- **细胞分布**：3D U-Net 从 512 × 512 × 128 体数据中抽取 112 × 112 × 32 patch，每批 6 个；三类输出为背景、细胞边界和细胞内部。Adam 初始学习率为 $10^{-3}$，每轮乘 0.95，使用 Dice loss，训练 3 轮。五个脑区的 precision、recall、F score 分别为 0.969、0.985、0.976。
- **单神经元投射组**：配准后在 Vaa3D 中半自动追踪，再由另一位标注者在 TeraVR 中全程质控，最后输出无断裂、无环的单棵 SWC 树。

### 结果与局限

系统光学分辨率为 0.77 × 0.49 × 2.61 μm；细胞分布全脑成像用时 10 h，单神经元投射组成像用时 58 h。共聚焦 Airy 相比普通 Airy 将神经突对比度提高 4.7 倍。

复现时要注意：论文的软件分散在 OLSTv2、CAB-OLST_Analysis、SmartStitcher、mBrainAligner、Vaa3D 和补充代码中。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CAB-OLST

CAB-OLST is a brain-wide imaging platform designed to escape the usual trade-off among field of view, axial resolution, signal-to-noise ratio and imaging depth. It combines a scanned Airy beam, 45° phase correction, rolling-shutter virtual-slit detection, inverted SPIM geometry and automated vibratome sectioning.

The Airy beam extends depth of field by more than tenfold relative to a Gaussian beam, while the 13-μm virtual slit suppresses side lobes and background without requiring whole-brain deconvolution. Each superficial slab is acquired as overlapping oblique mosaics and then removed, allowing the cycle to continue through the brain. Reconstruction feeds either atlas-registered 3D cell counting or Vaa3D/TeraVR single-neuron tracing.

The system reports 0.77 × 0.49 × 2.61 μm optical resolution. Whole-brain cell-type mapping was completed in 10 h at 0.37 × 0.37 × 1.77 μm voxels, and projectome imaging in 58 h at 0.26 × 0.26 × 1.06 μm voxels. Confocal Airy detection increased neurite contrast 4.7-fold and soma contrast 1.2-fold; the 3D U-Net achieved precision 0.969, recall 0.985 and F score 0.976 on five manually annotated regional volumes.

Reproducibility is fragmented across several packages. The acquired OLSTv2 repository faithfully covers BigStitcher metadata, tiled fusion and oblique-to-anatomical transforms, but not optical acquisition, stage/vibratome synchronization, stripe removal, the 3D U-Net, registration or neuron tracing. Processed data and exact archived code releases are linked by the paper, while raw datasets are 4–60 TB each. Overall reproducibility: **3/5**—substantial public artifacts, but no single runnable end-to-end package and important instrument details remain distributed.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
