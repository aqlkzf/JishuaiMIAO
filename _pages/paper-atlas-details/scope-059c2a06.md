---
layout: default
permalink: /paper-atlas/scope-059c2a06/
title: "SCOPE"
nav: false
description: "这篇 Nature Biotechnology 2026 论文提出 HySIL（hybrid solid-liquid optics）和两个实现：SCOPE 与 Super-SCOPE。问题背景是大体积光片显微成像里的检测物镜矛盾：油/水浸等 immersion objectives 有高 NA、低像差，但工作距离短、价格高、折射率适配范围窄、腔体集成复杂；"
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
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>SCOPE</h1>
    <p>Hybrid solid-liquid optics enable scalable, high-resolution light-sheet microscopy across diverse immersion media</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SCOPE / HySIL 方法中文解读

### 这篇论文要解决什么问题？

这篇 Nature Biotechnology 2026 论文提出 HySIL（hybrid solid-liquid optics）和两个实现：SCOPE 与 Super-SCOPE。问题背景是大体积光片显微成像里的检测物镜矛盾：油/水浸等 immersion objectives 有高 NA、低像差，但工作距离短、价格高、折射率适配范围窄、腔体集成复杂；空气物镜便宜、工作距离长、容易集成，但在浸没样品里会出现严重球差、光收集能力下降和分辨率退化（`paper.md:18-21`）。

HySIL 的核心目标是：让长工作距离空气物镜在高折射率介质和透明化/膨胀样品中获得更好的波前校正和有效 NA，同时保留低成本、长工作距离、易集成、多介质兼容等优点（`paper.md:24-30`）。

### 现有方法为什么不够？

论文把限制分成两类：

1. **高 NA 浸没物镜**：分辨率好，但工作距离短、成本高、折射率校正范围窄，而且通常需要复杂的密封腔体（`paper.md:21`）。
2. **空气物镜**：成本低、长工作距离、机械集成简单，但在浸没样品里受到球差和低光收集效率限制，通常只能达到细胞级分辨率（`paper.md:21`）。

已有校正路线包括 adaptive optics、SIMlens 这类定制 meniscus 透镜和特殊校正空气物镜，但论文认为它们仍然偏系统特异、工程复杂或成本高（`paper.md:21`, `paper.md:24-27`）。HySIL 的差异在于把固体光学元件和折射率匹配液体做成连续的光学系统，减少内部折射界面，从而降低对多界面折射率匹配的敏感性（`paper.md:27`, `paper.md:189-192`）。

### 方法核心：HySIL、SCOPE 和 Super-SCOPE

HySIL 是一个光学设计框架：把一个固体透镜和与其折射率匹配的液体组合起来，形成连续的 solid-liquid 光学系统。SCOPE 是该框架的稳健版本；Super-SCOPE 使用 Weierstrass super-hemispherical 几何，用更高的几何增益换取更高对准敏感性（`paper.md:30`, `paper.md:53`, `paper.md:204`）。

关键几何和公式如下：

| 概念 | 论文中的定义 | 作用 |
|---|---|---|
| `n` | 固体透镜和液体的折射率，实验实现约为 1.46 | 决定有效 NA 增益 |
| SCOPE NA scaling | 有效检测 NA 按 `n` 缩放 | 稳健、适合常规成像 |
| Super-SCOPE NA scaling | 有效检测 NA 按 `n^2` 缩放 | 分辨率潜力更高，但容差更低 |
| SCOPE 几何距离 | 照明平面到曲面距离为 `r` | `r` 是透镜半径 |
| Super-SCOPE 几何距离 | 距离为 `r(1 + 1 / n)` | Weierstrass 几何 |

这些定义来自论文主文和 Methods（`paper.md:30`, `paper.md:53`, `paper.md:216-219`）。

### 整体流程

```text
选择空气物镜和 HySIL 几何
        |
        v
构建 SCOPE：石英 plano-convex lens + RI 匹配油 + 3D 打印腔体
        |
        v
用 Zemax 模拟 air / air immersion / SCOPE / Super-SCOPE
        |
        v
采集 bead / nanoparticle z-stack 做 PSF 验证
        |
        v
对每个 bead 提取 X/Y/Z profile，拟合 Gaussian，计算 FWHM
        |
        v
把验证后的 SCOPE-pLSM/SLICE 用于膨胀、透明化和组织病理样品
        |
        v
用外部软件完成 stitching、rendering、tracing、registration、可视化
```

### 光学模拟与设备实现

论文的模拟使用 Ansys Zemax OpticStudio 2024，模型包含 paraxial detection lens、Thorlabs TTL200 tube lens、plano-convex fused silica lens 和折射率匹配液体；样品被建模为具有给定厚度和 RI 的平板（`paper.md:213-216`）。比较条件包括 air-air、air immersion、SCOPE 和 Super-SCOPE，固定 aperture stop 对应 0.28 NA 空气物镜，并在各配置中优化物镜位置（`paper.md:216-219`）。输出包括 Huygens PSF、encircled energy、OPD wavefront error 和 RMS wavefront error；RI/厚度容差扫描覆盖 2、4、6 mm 样品，以及 1.38-1.54 的 RI 范围（`paper.md:221-222`）。

设备实现使用 Edmund Optics 48-670 plano-convex 石英透镜，半径 27.5 mm、直径 25 mm；液体使用 Cargille RI-matching oil，`n ~= 1.46`。腔体为黑色树脂 3D 打印，并用光学环氧密封，透镜用 UV 胶固定（`paper.md:255-258`）。检测物镜为 Mitutoyo x10/0.28 NA 和 x5/0.14 NA 长工作距离空气物镜（`paper.md:258-260`）。

**代码证据状态：Not found。

### PSF/FWHM 分析：论文与代码真正重合的部分

论文 Methods 明确写到，PSF 图像栈用于测量单个 PSF 的 lateral `x-y` 和 axial `z` FWHM；beads/nanoparticles 通过自定义 Python GUI 在 maximum-intensity projection 上手动标记；中心坐标用局部最大强度像素进一步精修；随后提取 `x`、`y`、`z` 强度 profile，拟合 Gaussian 并计算 FWHM（`paper.md:270-273`）。代码可用性也只声明释放“detect beads and measure lateral and axial FWHM”的自定义代码（`paper.md:381-384`）。

Zenodo 归档 `bead-analyzer-v1.2.1` 与这部分高度匹配：

- `analysis.py` 的 manual mode 会把 3D stack 转为 MIP，并进入手动点选流程（`analysis.py:567-610`）。
- `detectors.py` 和 `core.py` 提供 right-click 多点收集交互（`detectors.py:90-99`, `core.py:256-281`）。
- `_recenter_point` 会在局部 3D 搜索框中精修 bead 中心；默认 `peak` 模式最接近论文的“局部最大强度”描述（`analysis.py:261-305`, `analysis.py:639-647`）。
- 代码提取 Z profile 和 X/Y line profile，并计算 FWHM（`analysis.py:643-699`）。
- Gaussian 模型为 `A * exp(-0.5 * ((x - mu) / sigma)^2) + C`，FWHM 为 `2 * sqrt(2 * ln(2)) * sigma * scale_factor`（`core.py:330-398`）。
- 单元测试验证 Gaussian FWHM、3D Gaussian、QA 和 robust fitting 行为（`tests/test_core.py:54-70`, `tests/test_core.py:105-168`）。

代码还包含论文未详细描述的扩展能力：blob、trackpy、StarDist、Cellpose 检测模式，prominence-based FWHM，`centroid/radial/edge` 中心模式，3D Gaussian fitting，QA、诊断图、heatmap 和平均 bead 输出（`README.md:79-120`, `analysis.py:1271-1444`）。这些是代码能力，不应反向解释为论文主要方法都由该代码实现。

### 实验验证与应用

Fig. 1 支撑 HySIL/SCOPE 的设计和模拟逻辑：空气物镜与浸没物镜的 NA/WD tradeoff、SCOPE/Super-SCOPE 几何、Huygens PSF 模拟、RMS wavefront error 容差曲线和 pLSM-SCOPE 集成示意（`paper.md:45-68`）。

Fig. 2 是最重要的代码相关图。它展示 SCOPE 相比 air immersion 更紧的 PSF、更高信号、跨 FOV 的 lateral/axial FWHM boxplot、light-sheet PSF 测量和多色 bead 通道对齐（`paper.md:77-97`）。论文报告 x10 SCOPE 约 0.75 um lateral 和 11 um axial FWHM，x10 Super-SCOPE 约 0.56 um lateral 和 5 um axial FWHM，x5 SCOPE 约 1.2 um lateral 和 18 um axial FWHM（`paper.md:91-94`）。

Figs. 3-6 是平台应用证据：expanded mouse brain、whole salamander brain、CUBIC-R mouse brain、iDISCO cavefish brain、iPSC-derived organoids 和 human breast tissue 3D histopathology（`paper.md:100-180`）。这些图支持 SCOPE 的大体积、多介质、生物样品适用性，但相应的样品制备、采集、stitching、tracing、registration、false-coloring 和病理分析流程不在 Zenodo bead-analysis 代码包里。

### 复现性评价

完整论文复现性：**2/5**。原因是完整平台需要真实光学器件、Zemax 模型、设备构建、pLSM/SLICE 或 BrightSLICE 采集/拼接环境、原始大体积数据和外部可视化/追踪/配准软件；这些都没有随代码归档完整提供。论文也说明原始大数据因体积过大，需要向通讯作者合理请求（`paper.md:375-378`）。

PSF/FWHM 分析工具复现性：**4/5**。代码包是可检查的 Python 包，有 CLI/GUI、README、测试和较完整输出流程；但实际复现实验图仍需要原始 bead z-stack、正确的 `scale_xy`/`scale_z` 校准、论文实验配置和跨配置统计整理。

### 关键限制与开放缺口

- SCOPE 的最终分辨率和光收集仍受空气物镜自身 NA 限制（`paper.md:204`）。
- Super-SCOPE 分辨率潜力更高，但对 alignment 和 optical variations 更敏感，spectral bandwidth 更低（`paper.md:204`）。
- 常见 clearing 方法已验证，但极端 RI 样品可能需要替代材料或 immersion formulation（`paper.md:204`）。
- 论文主要验证固定、透明化和膨胀样品；live imaging 只是原则上可适配，尚不是完整验证流程（`paper.md:198`, `paper.md:360`）。
- 代码缺口明确保留为 `Not found`：Zemax/OpticStudio、CAD/device control、pLSM/SLICE acquisition、stitching、Figs. 3-6 downstream biological workflows。

一句话总结：SCOPE/HySIL 是一个以固液折射率匹配来提升空气物镜大体积成像能力的光学平台；本地代码只覆盖论文 PSF 验证中的 bead detection 与 FWHM measurement，不覆盖完整光学平台和生物成像工作流。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SCOPE Summary

### Fast Overview

This Nature Biotechnology 2026 paper introduces HySIL, a hybrid solid-liquid optics framework for making long-working-distance air objectives behave more like high-performance immersion detection optics in light-sheet microscopy. The implemented devices, SCOPE and Super-SCOPE, pair a solid quartz lens with RI-matched immersion oil so the lens and liquid form a continuous optical system for wavefront correction and effective NA enhancement (`paper.md:24-30`, `paper.md:42-53`).

The practical goal is to make high-resolution, large-volume volumetric imaging more scalable. Conventional immersion objectives provide high NA but are costly, short-working-distance, RI-limited, and difficult to integrate in chambers; air objectives are cheaper and long-working-distance but lose resolution and photon collection in immersed samples (`paper.md:18-21`). HySIL/SCOPE targets that tradeoff by retaining air-objective working distance and integration simplicity while correcting aberrations and improving effective NA.

### What The Method Does

SCOPE uses an off-the-shelf plano-convex quartz lens and RI-matching oil, both around `n ~= 1.46`, with the sample imaging plane positioned near the lens-radius geometry (`paper.md:53`, `paper.md:258-260`). The paper states that effective detection NA scales as `n` for SCOPE and `n^2` for the Weierstrass-style Super-SCOPE geometry (`paper.md:30`, `paper.md:53`). Optical simulations in Zemax model air, air-immersion, SCOPE, and Super-SCOPE configurations across sample RI/thickness, wavelengths, and FOV positions (`paper.md:216-222`).

Experimentally, the platform is validated with PSF measurements from beads/nanoparticles, then used in pLSM/SLICE imaging of expanded mouse and salamander brain, CUBIC-R-cleared mouse brain, iDISCO-cleared cavefish brain, iPSC-derived cortical organoids with microglia, and human breast tissue 3D histopathology (`paper.md:33`, `paper.md:100-180`).

### Main Evidence

- **Optics and design:** Fig. 1 shows the air/immersion objective tradeoff, SCOPE/Super-SCOPE geometry, Zemax PSF simulations, RMS wavefront-error tolerance curves, and pLSM-SCOPE integration (`paper.md:45-68`).
- **PSF performance:** Fig. 2 shows visibly tighter PSFs under SCOPE than air immersion, FWHM boxplots across field positions, light-sheet PSF measurements, and multicolor bead co-registration (`paper.md:77-97`). Reported values include approximately 0.75 um lateral and 11 um axial FWHM for x10 SCOPE, 0.56 um lateral and 5 um axial for x10 Super-SCOPE, and 1.2 um lateral and 18 um axial for x5 SCOPE (`paper.md:91-94`).
- **Biological applications:** Figs. 3-6 demonstrate large expanded brain sections, whole salamander brain, cleared mouse/cavefish brains, organoids, and human 3D histopathology (`paper.md:112-180`).
- **Multi-immersion claim:** The paper reports compatibility across sample RI from aqueous to solvent-cleared conditions, with simulations over RI 1.38-1.54 and biological examples spanning RI around 1.33-1.56 (`paper.md:137-143`, `paper.md:195`).

### Reproducibility And Code Availability

The code availability statement is narrow: custom code for bead detection and lateral/axial FWHM measurement is available via Zenodo (`paper.md:381-384`). The local archive `bead-analyzer-v1.2.1` matches that scope. It provides a Python package/CLI/GUI for bead stacks, manual/blob/trackpy/StarDist/Cellpose detection, center refinement, X/Y/Z profile extraction, Gaussian/prominence FWHM, QA, diagnostics, CSV summaries, average bead plots, and heatmaps (`README.md:1-6`, `README.md:79-120`; `analysis.py:567-764`; `core.py:283-398`).

The archive does **not** implement the optical design, Zemax simulations, CAD/device construction, microscope control, BrightSLICE/pLSM acquisition, stitching, biological tracing/registration, or histopathology false-coloring workflows. Raw imaging data are not in the workspace; the paper says the very large raw data are available from the corresponding author on reasonable request (`paper.md:375-378`).

Reproducibility rating: **2/5 for the full paper**, **4/5 for the released PSF/FWHM analysis utility**. The bead-analysis code is inspectable and partially tested, but the full platform depends on physical optics, proprietary/external software, raw data, and paper-described workflows outside the archive.

### Caveats

- Super-SCOPE offers higher NA scaling but is more sensitive to alignment and optical variation and has reduced spectral bandwidth (`paper.md:204`).
- Ultimate resolution and light collection still depend on the air objective (`paper.md:204`).
- Extreme sample RIs may require alternative materials or immersion formulations (`paper.md:204`).
- Live imaging is suggested as possible in principle, while the reported validation uses fixed, cleared, or expanded specimens (`paper.md:198`, `paper.md:360`).
- The released code should be cited as support for Fig. 2-style PSF/FWHM analysis only, not as evidence for the full HySIL/SCOPE optical platform.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
