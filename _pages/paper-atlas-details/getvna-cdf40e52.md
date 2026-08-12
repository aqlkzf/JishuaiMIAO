---
layout: default
permalink: /paper-atlas/getvna-cdf40e52/
title: "GETvNA"
nav: false
description: "研究 DNA 弯曲、修复酶结合和蛋白沿 DNA 移动，需要同时具备高空间分辨率和亚秒级时间分辨率。smFRET 很适合动态测距，但通常只给出两个染料之间的一条距离；常规超分辨定位能给出空间坐标，却往往要求结构在较长采集时间内保持静止。GETvNA 的目标，是在普通单分子荧光/FLIM 平台上直接读取核酸复合物的轴向结构变化。"
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
    <h1>GETvNA</h1>
    <p>Single-molecule dynamic structural biology with vertically arranged DNA on a fluorescence microscope</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GETvNA：把荧光寿命变成 DNA 的动态“高度尺”

### 要解决的问题

研究 DNA 弯曲、修复酶结合和蛋白沿 DNA 移动，需要同时具备高空间分辨率和亚秒级时间分辨率。smFRET 很适合动态测距，但通常只给出两个染料之间的一条距离；常规超分辨定位能给出空间坐标，却往往要求结构在较长采集时间内保持静止。GETvNA 的目标，是在普通单分子荧光/FLIM 平台上直接读取核酸复合物的轴向结构变化。

### 核心创新

GETvNA 是 “graphene energy transfer with vertical nucleic acids”。DNA 构建体由双链区和单链悬垂端组成。单链碱基吸附到石墨烯表面，双链区因碱基堆叠而大致垂直于表面。这样，染料到石墨烯的距离就对应 DNA 轴向位置。石墨烯能量转移随距离近似按 $d^{-4}$ 变化，因此荧光寿命对纳米尺度高度非常敏感，而且只需要一个供体染料。

### 从光子到结构的流程

```text
设计带 ssDNA 悬垂端的荧光标记 dsDNA
  -> 转移并清洁单层石墨烯
  -> DNA 自吸附并形成近似竖直取向
  -> TCSPC/FLIM 采集 PTU 光子事件和仪器响应函数 IRF
  -> 读取时间戳、探测通道和微时间
  -> 按通道、微时间、宏时间和强度筛选光子
  -> 对衰减曲线做 IRF 卷积的单指数最大似然拟合
  -> 得到寿命 tau 或寿命时间轨迹
  -> 用 GET 标定式转换为高度 z(t)
  -> 根据几何模型得到弯曲角，或直接跟踪蛋白轴向位置
```

寿命到高度的关系为：

$$z=&#123;&#123;d}_{0}\left(\frac{1}{1-\frac{\tau }&#123;&#123;\tau }_{0}}}-1\right)}^{\frac{1}{4}}$$

其中 $\tau$ 和 $\tau_0$ 分别是有、无石墨烯时的寿命，$d_0$ 是 50% 能量转移对应的标定高度。局部弯曲角通过

$$\theta =\arccos \left(\frac{z-{z}_&#123;&#123;{\mathrm{bulge}}}}}{L-{z}_&#123;&#123;{\mathrm{bulge}}}}}\right)$$

得到；$L$ 是无弯曲对照的高度，$z_{\mathrm{bulge}}$ 是弯曲点高度。

### 主要实验结果

- 36–66 bp DNA 的高度测量和分子动力学模拟共同支持双链区近似竖直。
- 单条轨迹在每个时间箱约 1,000 个光子时达到低于 4 Å 的轴向精度，并能区分相差一个碱基对的 DNA。
- 3A、5A、7A bulge 和 A-tract 产生可分辨的高度/角度变化。
- AP 位点与 Endonuclease IV 体系出现多个动态构象状态。
- 对 AGT 进行染料标记后，可观察其沿 DNA 的快速和慢速运动；稳定状态的步长分布与整数碱基对位移相容，A-tract 区域表现出明显的限制或优先结合。

### 代码能复现什么

补充软件中的 Python 脚本能够读取 PicoQuant PTU、筛选光子、处理 IRF，并用最大似然或最小二乘方法拟合荧光寿命。它没有包含寿命到高度、弯曲角、AGT 稳态识别和完整作图流水线；论文说明后续作图脚本位于 Zenodo。因此当前代码与论文的“寿命拟合层”匹配较好，但不是一键式的完整复现包。

### 使用边界

有效范围主要约为 7–30 nm；过近时荧光几乎完全淬灭，过远时 GET 灵敏度下降。DNA 长度、染料连接臂、石墨烯缺陷/双层区域、光子数和信噪比都会影响精度。跨分子汇总的高度分布宽度为 8.5–10.5 Å，明显差于单条轨迹内的 Å 级精度，因此“单分子动态精度”和“跨样本绝对准确度”必须区分。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## GETvNA summary

GETvNA is an experimental/computational platform for dynamic structural biology of nucleic-acid complexes on a fluorescence microscope. It addresses a gap between smFRET, which mainly yields pairwise distances, and super-resolution localization methods that often require static or specially oriented structures. A single-stranded DNA overhang adsorbs to graphene and makes the attached duplex stand approximately vertical; graphene energy transfer then converts a fluorophore lifetime into its height above the surface with a steep $d^{-4}$ dependence.

The workflow combines graphene sample preparation, vertically oriented labeled DNA, TCSPC/FLIM acquisition, IRF-reconvolved maximum-likelihood lifetime fitting, and geometric conversion of lifetime to axial height and bending angle. The authors validate orientation using DNA lengths from 36 to 66 bp and MD simulations, then measure bulge-, A-tract-, abasic-site-, and Endonuclease-IV-induced bending. Labeling AGT instead of the DNA end enables direct tracking along the duplex.

Key results include within-trace axial precision below 4 Å at roughly 1,000 photons per bin, discrimination of constructs differing by one base pair, dynamic enzyme-induced structural states, and AGT slow-mode steps compatible with integer base-pair displacements. The paper also reports that A-tract DNA confines or preferentially binds AGT. Precision across pooled molecules is lower—height-distribution widths are 8.5–10.5 Å—highlighting surface/sample heterogeneity.

Reproducibility is **3/5**. The paper provides detailed wet-lab methods, raw/processed data and plotting scripts on Zenodo, and Supplementary Software with example PTU data. The acquired code exactly covers PTU decoding, photon filtering, IRF processing, and lifetime fitting. It does not contain lifetime-to-height conversion, angle calculation, AGT stable-state analysis, or a packaged end-to-end runner. The method also depends strongly on graphene quality, fluorophore calibration, photon budget, and a restricted axial range (practically about 7–30 nm).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
