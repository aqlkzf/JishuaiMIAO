---
layout: default
permalink: /paper-atlas/ringdeconvolutionmicroscopy-645bf2c0/
title: "RingDeconvolutionMicroscopy"
nav: false
wide: true
description: "普通反卷积默认整幅视野使用同一个点扩散函数（PSF）。但真实显微镜的像差通常随视野位置变化：中心处测得的 PSF 用到边缘时会失配，造成低对比度、噪声放大或错误结构。若在每个位置都标定 PSF，标定量和计算量又会迅速失控。 RDM 的关键观察是：多数显微镜和相机围绕光轴具有旋转对称性。位于相同半径、不同角度的点源，其 PSF 形状相同，只是绕中心旋转。"
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
    <h1>RingDeconvolutionMicroscopy</h1>
    <p>Ring deconvolution microscopy: exploiting symmetry for efficient spatially varying aberration correction</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/apsk14/rdmpy" target="_blank" rel="noopener noreferrer" aria-label="Open code for RingDeconvolutionMicroscopy">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 环形反卷积显微镜（RDM）方法详解

### 解决什么问题

普通反卷积默认整幅视野使用同一个点扩散函数（PSF）。但真实显微镜的像差通常随视野位置变化：中心处测得的 PSF 用到边缘时会失配，造成低对比度、噪声放大或错误结构。若在每个位置都标定 PSF，标定量和计算量又会迅速失控。

RDM 的关键观察是：多数显微镜和相机围绕光轴具有旋转对称性。位于相同半径、不同角度的点源，其 PSF 形状相同，只是绕中心旋转。论文把这一性质称为线性旋转不变性（LRI）：

$$
\tilde{h}(\rho,\phi;r,\theta)=\tilde{h}(\rho,\phi-\theta;r,0).
$$

因此不必为二维视野中的每个位置分别测量 PSF，只需知道 PSF 随半径如何变化。

### 为什么已有方法不够好

- 标准反卷积只用中心 PSF，无法处理边缘的空间变化像差。
- 分块反卷积、PSF 插值和模态分解需要越来越密的 PSF 标定才能接近精确模型；极端情况下，百万像素图像可能需要百万个 PSF。
- 通用 U-Net 等深度去模糊方法速度快，但容易继承训练数据或仿真模型偏差，在新样本上不稳定。
- RDM 用明确的光学对称性压缩系统自由度：核心环形卷积在假设成立时是精确前向模型，而不是经验分块近似。

### 从标定到重建

```text
随机分布的荧光微珠图像
        │ 定位各个 PSF
        ▼
拟合 5 个主要 Seidel 像差系数
        │
        ▼
沿一条半径合成整组 PSF
        │ 转换到旋转傅里叶域
        ▼
模糊样本图像 ── 环形卷积前向模型 ── 迭代反演 ── 清晰图像

快速替代：模糊图像 + Seidel 系数 ── DeepRD ── 近似清晰图像
```

#### 1. 单次标定

拍摄一张随机散布点源的图像，检测每个点源的位置与 PSF。RDM 用同一组 Seidel 系数描述球差、彗差、像散、场曲和畸变随视场位置造成的变化。相比每个位置独立拟合 Zernike 系数，这种全局参数化更适合旋转对称系统。拟合问题是非凸的；仿真显示多数运行能接近真实系数，即使没有到达全局最优，生成的 PSF 往往仍足以获得较好的重建。

#### 2. 生成径向 PSF

拟合后的 Seidel 系数通过光学 PSF 模型生成从中心到边缘的一条径向 PSF 序列。代码中的 `get_rdm_psfs` 可生成逐半径的精确模式，也可用 `patch_size` 把多个半径合并成环带以节省资源。前者对应论文的精确环形模型，后者是工程近似。

#### 3. 环形卷积

一般空间变化成像模型要对所有物点和 PSF 进行二维积分，代价约为 $O(N^4)$。LRI 使角度方向变成卷积方向：

1. 把物体图像转换到极坐标；
2. 沿角度维做傅里叶变换；
3. 每个半径的物体频谱乘以该半径 PSF 的旋转傅里叶变换；
4. 乘上极坐标积分权重 $r\,dr\,d\theta$ 并沿半径求和；
5. 逆变换并返回笛卡尔坐标。

这样将复杂度降到 $O(N^3\log N)$。论文仿真表明，像差增强时普通卷积误差随之增加，而环形卷积仍与暴力精确模型一致；在百万像素规模上速度接近提升四个数量级。

#### 4. 环形反卷积

重建把待估图像像素作为优化变量，最小化

$$
\|\mathcal{R}_h(f)-g\|_2^2+\lambda_{TV}TV(f)+\lambda_2\|f\|_2+\lambda_1\|f\|_1,
$$

其中 $g$ 是测量图像，$\mathcal{R}_h$ 是环形卷积。代码用 Adam 或 SGD 通过可微前向模型迭代更新，并把负值投影为零。默认从测量图像初始化，使用 150 次 Adam 迭代。TV、L1 和 L2 项可抑制噪声与环状伪影。

### DeepRD

DeepRD 输入模糊图像和五个 Seidel 系数，用环形卷积生成的合成空间变化模糊数据训练。它适合大图和视频：论文报告其速度比迭代 RDM 快近三个数量级，质量接近但略低、跨样本一致性也较差。它是物理条件化的学习近似，而不是精确求解器。

### 实验结果

- 微型显微镜：RDM 在视野边缘解析出标准反卷积和 U-Net 难以恢复的分辨率靶、组织与活体缓步动物细节。
- 高 NA 多色荧光：每个颜色通道分别标定，可同时纠正空间像差和色差，并恢复边缘的肌动蛋白与线粒体亚细胞结构。
- 多模光纤微内窥镜：RDM 只需 1 张标定图像，SVRL 需要 441 张；RDM 在边缘更好地恢复圆形微珠和神经元细突起。
- 仿真：28 张测试图像上，环形反卷积平均 PSNR 最高但约需 60 秒；DeepRD 更快。
- 光片显微镜：把旋转对称推广为单轴横向对称，轴向 PSF FWHM 从标准反卷积的 $1.10\pm0.48\,\mu m$ 改善到 $0.76\pm0.25\,\mu m$。

### 使用时必须注意

- 图像必须与光轴中心正确对齐，且系统确实近似旋转对称；否则“精确性”不成立。
- Seidel 拟合和反卷积都是非凸/迭代过程，结果依赖初始化、正则化、迭代次数和预处理。
- 强噪声或大 PSF 会产生环状伪影；需要适当正则化。
- 仓库核心函数与论文高度匹配，但完整论文复现依赖外部数据和多个 notebook，没有统一的一键脚本。
- 补充材料 Markdown 未获得，因此补充材料独有参数记为 `MISSING`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Ring Deconvolution Microscopy

### Overview

Ring deconvolution microscopy (RDM) corrects spatially varying microscope aberrations without calibrating a PSF at every image location. It exploits rotational symmetry: PSFs at the same field radius share a shape and differ only by rotation. A single image of randomly distributed point sources is used to fit primary Seidel aberration coefficients, from which a radial PSF stack is synthesized. The main reconstruction then solves an inverse problem using an exact ring-convolution forward model; DeepRD provides a much faster learned alternative conditioned on the same coefficients.

### Why existing methods are insufficient

Standard deconvolution is fast but assumes one space-invariant PSF and therefore degrades off axis. Patch-wise or modal spatially varying methods become more accurate as calibration density increases, but can require hundreds to millions of PSFs and large compute. Generic learned deblurring can be fast, yet may inherit simulation/training bias and extrapolate poorly. RDM occupies a useful middle ground: it is exact under a physically common symmetry assumption and needs only one calibration exposure.

### Method in brief

The LRI relation

$$
\tilde{h}(\rho,\phi;r,\theta)=\tilde{h}(\rho,\phi-\theta;r,0)
$$

turns general space-variant image formation into a radial integral of angular convolutions. In polar coordinates, RDM Fourier-transforms the angular dimension, multiplies each object ring by the corresponding PSF rotational Fourier transform, integrates over radius, and maps the result back to Cartesian coordinates. This reduces exact forward modeling from $O(N^4)$ to $O(N^3\log N)$ for an $N\times N$ image. Deconvolution optimizes image pixels through this differentiable operator with optional TV/L1/L2 regularization and nonnegativity projection.

### Evidence and results

The paper demonstrates miniature microscopy, ×100/1.4-NA multicolor fluorescence microscopy, multimode-fiber micro-endoscopy, and light-sheet microscopy. RDM improves edge/corner structure where center-PSF deconvolution fails. On multimode-fiber data it uses one calibration image versus 441 for SVRL, although it represents the field with 120 rather than 30 PSFs. Simulations show ring convolution remains accurate as aberration magnitude increases and is nearly four orders of magnitude faster than brute-force exact blur at megapixel scale. Across 28 simulated test images, ring deconvolution gives the best average PSNR but takes about 60 s; DeepRD is almost three orders faster with slightly lower and less consistent quality. The sheet extension improves mean axial bead FWHM to 0.76 ± 0.25 μm versus 1.10 ± 0.48 μm after standard deconvolution.

### Reproducibility

The authors provide `rdmpy` with direct APIs for Seidel calibration, PSF rendering, ring/sheet convolution, and iterative deconvolution. Direct source inspection shows a strong paper-code match. Modality examples and pretrained DeepRD models are included, but experiments are notebook-led, external data must be downloaded, dependency versions are not completely locked, and no single command regenerates all figures. Reproducibility rating: **4/5 for the core method, 3/5 for the full paper**.

### Limitations

Exactness depends on real rotational or lateral symmetry and accurate centering. Calibration and reconstruction are nonconvex iterative procedures, so preprocessing and optimization choices matter. Ring deconvolution may introduce ringing/noise and is slower than learned inference. DeepRD exchanges theoretical guarantees for speed and training-distribution dependence. Supplementary-only details are `MISSING` because no supplementary Markdown was acquired.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
