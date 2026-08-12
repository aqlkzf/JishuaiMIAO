---
layout: default
permalink: /paper-atlas/cab-olst-013acc3e/
title: "CAB-OLST"
nav: false
description: "它的核心不是“从脑表面一直看穿到脑底”，而是： > 每次只高质量成像当前的浅表组织，成像后切掉上方 300 μm，再成像新暴露的浅表面；最后用计算方法把所有块拼回完整全脑。 这相当于把困难的“深部光学成像”改写成大量较稳定的“浅层成像 + 全局重建”问题。"
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
    <h1>CAB-OLST</h1>
    <p>Confocal Airy beam oblique light-sheet tomography for brain-wide cell type distribution and morphology</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02888-9" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CAB-OLST 方法详解：用“始终成像浅层 + 计算重建全脑”解决大体积高分辨成像

### 1. 这篇论文解决什么问题？

CAB-OLST（confocal Airy beam oblique light-sheet tomography）不是单独的神经网络，而是一套把光学、机械切片、自动采集和计算分析串起来的全脑成像平台。它希望同时获得三种通常互相制约的能力：

1. **大范围和高通量**：覆盖整个小鼠脑，而不是局部视野；
2. **高空间分辨率**：看清细胞核、树突棘、轴突扣结和长距离轴突；
3. **高信噪比（SNR）**：在脑深部也保持细小结构可辨认。

传统光片显微镜的核心矛盾是：高斯光束的焦区越长，光片通常越厚，轴向分辨率和对比度越差；如果使用紧聚焦光束，薄光片只能覆盖较短的瑞利长度。完整透明脑的深部成像还会受到散射、折射率不匹配和物镜工作距离的限制（`paper.md:21-36`）。

已有代表性路线包括：

- serial two-photon tomography，*Nature Methods*，2012：自动化全脑细胞成像，但点扫描限制速度和信号积分；
- volumetric two-photon tomography，*eLife*，2016：用于 MouseLight 等脑范围神经元重建，但论文认为其速度仍低于 CAB-OLST；
- 传统 LSFM/SPIM（现代应用始于 *Science*，2004）：面照明显著加快采集，但大视野、薄光片和深部成像之间仍有权衡。

### 2. 一句话理解 CAB-OLST

它的核心不是“从脑表面一直看穿到脑底”，而是：

> 每次只高质量成像当前的浅表组织，成像后切掉上方 300 μm，再成像新暴露的浅表面；最后用计算方法把所有块拼回完整全脑。

这相当于把困难的“深部光学成像”改写成大量较稳定的“浅层成像 + 全局重建”问题。

### 3. 输入、输出和两条分析支路

#### 输入

- 荧光标记并透明化的小鼠脑；
- 琼脂糖包埋和折射率匹配油；
- 单通道或多通道激发光；
- 视野、体素采样、激光功率、虚拟狭缝宽度、像素驻留时间、切片厚度和重叠范围等参数。

#### 中间结果

- 大量倾斜光片视野和三维图像块；
- 经过拼接、去倾斜/方向变换、条纹去除后的全脑体数据；
- 配准到 Allen Mouse Brain Common Coordinate Framework 的解剖空间。

#### 最终输出

- **细胞分布支路**：细胞中心坐标和各脑区细胞计数；
- **单神经元支路**：经过人工质控的 SWC 神经元树结构。

### 4. 光学核心：为什么使用 Airy 光束？

空间光调制器（SLM）加载三次相位掩模：

$$
\varnothing(x,y)=\alpha k_0(u^3+v^3),
$$

其中

$$
k_0=\frac{2\pi}{\lambda}, \qquad
(u,v)=\left(\frac{2\pi x}{f_{\mathrm{obj}}},\frac{2\pi y}{f_{\mathrm{obj}}}\right).
$$

$\lambda$ 是波长，$(x,y)$ 是物镜后孔径平面的横向坐标，$f_{\mathrm{obj}}$ 是物镜焦距，$\alpha$ 控制三次相位强度。论文使用 $\alpha=4.32$（640 nm）和 $\alpha=2.66$（488 nm）（`paper.md:196-199`）。

与高斯束相比，Airy 束在传播方向上能维持更长的窄主瓣，因此适合扫描形成大视野薄光片。论文报告其景深超过扫描高斯束的 10 倍。

但标准 Airy 束有两个问题：弯曲轨迹和旁瓣。作者采用：

- 45° 相位旋转，使弯曲 Airy 束在探测平面的投影成为直线；
- 滚动快门虚拟狭缝，只接收主瓣附近的信号，抑制旁瓣和离焦背景；
- 13 μm 样品面狭缝宽度，在光学切片能力和采集速度之间折中。

从实际图像看，Fig. 1 中共焦 Airy 模式的细轴突/神经突背景更暗、线条更清楚；在相同激发条件下的 Extended Data Fig. 6 中，五组 soma 和 neurite 的对比度也全部提高。因此主要收益是**对比度和背景抑制**，不只是峰值亮度变高。

### 5. 多通道为什么不会错位？

不同波长经过 SLM 和光路后会产生色散偏移。作者为不同波长设置不同的 blazed grating（BG）参数，例如 488 nm 使用 −0.8，640 nm 使用 −1.1，通过角度补偿使两个通道重新共定位（`paper.md:94-105,196-199`）。

当前系统按通道顺序采集，不是同时采集。Fig. 3 的合并图同时出现白色重叠细胞和单色细胞：白色部分说明通道能够对齐，单色部分则反映 reporter 与内源蛋白表达本身并非完全一致。论文没有给出基于微球的三维配准误差分布，因此“精确共定位”在本工作区中主要由图像示例支持。

### 6. 从样品到全脑体数据：完整采集流程

```text
荧光标记、透明化、琼脂糖包埋
              |
              v
SLM 生成 Airy 相位 + BG 色散补偿 + 45° 旋转
              |
              v
倾斜 Airy 光片扫描 + 相机滚动快门虚拟狭缝
              |
              v
采集当前浅表层的 xy 马赛克三维图像
              |
              v
振动切片机切除顶部 300 μm
              |
        重复 45–47 个切片周期
              |
              v
拼接 -> 去倾斜/重定向 -> 去条纹 -> 全脑体数据
              |
       +------+------+
       |             |
       v             v
图谱配准与细胞检测   Vaa3D/TeraVR 单神经元追踪
       |             |
       v             v
细胞中心和脑区计数   SWC projectome
```

关键采集参数包括：

| 参数 | 论文值 | 含义 |
|---|---:|---|
| 单视野倾斜平面 | 530 μm × 530 μm | 马赛克基本单元 |
| $x$ 步长 | 1–2.5 μm | 单个体栈内采样 |
| $y$ 步长 | 500 μm | 25× 物镜下相邻视野重叠 |
| 距新切表面起始深度 | 通常 50 μm | 避开切片表面扰动 |
| 每次机械切除厚度 | 300 μm | 暴露新的浅表面 |
| 全脑切片周期 | 45–47 | 覆盖完整小鼠脑 |
| 虚拟狭缝宽度 | 13 μm | 光学切片能力与速度折中 |

### 7. 计算重建：OLSTv2 实际验证了什么？

论文把重建概括为拼接、deskew 和条纹去除（`paper.md:229-235`）。当前工作区提供的 `OLSTv2` 代码只覆盖其中一部分，但这些部分有直接源码证据：

1. `StitchingXML.volume_coords_to_fused_image_coords` 先把局部体坐标转换为 stitching 坐标，再转换到指定的融合图像坐标（`OLSTv2/stitching/StitchingXML.py:1700-1732`）。
2. `stitching_coords_to_fused_image_coords` 显式组合减去包围盒原点、各向异性校正、下采样、重切片、垂直翻转、shear、旋转和裁剪矩阵，最后把坐标四舍五入为整数（`StitchingXML.py:1738-1897`）。
3. `merge_fused_volumes.py` 假设输入为方形网格的 `fused_<n>.tif`，沿两个数组轴拼接，并写出带 ZYX 和 μm 分辨率元数据的 ImageJ TIFF（`merge_fused_volumes.py:42-104`）。
4. `crop_fused_image.py` 根据非零区域裁剪图像，用强度直方图峰值估计背景下限，并可输出最大投影（`crop_fused_image.py:29-152`）。

这些代码说明 OLSTv2 是有实质功能的重建工具，而不是占位仓库；但它不能证明整个 CAB-OLST 系统都可由此仓库复现。

### 8. 三分类 3D U-Net：为什么不是普通前景/背景分割？

细胞密集区域中，相邻细胞核容易接触。如果只预测“细胞/背景”，多个细胞会粘成一个连通区域。论文因此设置三类：

1. background；
2. cell boundary / outer cell；
3. intracellular / cell。

边界类别相当于在相邻细胞之间学习一圈分隔带；内部类别用于提取细胞中心。Extended Data Fig. 9 中可直接看到蓝色外层和红色内部把接触细胞分开。

论文给出的训练设置为：

- 原始 TIFF 体：512 × 512 × 128 voxels；
- 随机 patch：112 × 112 × 32；
- 每次迭代：从一个随机体中抽取 6 个 patch；
- 3D U-Net encoder depth = 3；
- 3D convolution + batch normalization + ReLU + skip connections；
- 输入层不做隐式归一化；
- Adam，初始学习率 $10^{-3}$；
- 每个 epoch 乘以 0.95；
- Dice loss；
- 训练 3 个 epoch，每 25 次迭代验证一次。

五个不同脑区的专家标注体上，论文报告 precision = 0.969、recall = 0.985、$F$ score = 0.976（`paper.md:241-253`）。

**重要代码边界：**上述 U-Net 不在当前 `OLSTv2` 目录中。论文把它链接到另一个仓库 `rmunozca/CAB-OLST_Analysis`。因此这里的网络结构和指标属于论文证据，不是当前代码快照的已验证行为。

### 9. 单神经元 projectome 支路

该支路从稀疏 AAV-GFP 标记开始，经过全脑重建、图谱配准和注释，再由训练人员在 Vaa3D 中进行半自动追踪。另一位经验更丰富的标注者使用 TeraVR 对完整神经元逐段复核，最后执行 auto-refinement，使追踪线靠近荧光中心。最终 SWC 必须是一棵无断裂、无环、无异常多分支点的树（`paper.md:256-259`）。

Fig. 5 展示的六个神经元来自两只脑，可分为偏向 isocortex/STR/TH 的 Type I 和延伸到 HY/MB/HB 的 Type II。它证明了系统能够支持长距离连续重建，但样本量小、人工参与高，因此更接近“能力展示”，不是神经元类型的群体统计结论。

### 10. 主要结果怎样理解？

- 拼接后的光学分辨率：0.77 μm × 0.49 μm × 2.61 μm；
- 全脑细胞分布：0.37 μm × 0.37 μm × 1.77 μm voxel，10 h；
- 单神经元 projectome：0.26 μm × 0.26 μm × 1.06 μm voxel，58 h；
- 标准 Airy 对比共焦 Airy：neurite 对比度提高 4.7×，soma 提高 1.2×；相同激发条件下分别为 4.2× 和 1.5×；
- 机械切片在深部显著提高 soma 和 neurite 对比度；
- 三只 Gad2-H2B-GFP 小鼠的主要脑区分布相符（ANOVA $P=0.996$）。

需要注意，多个全脑图中仍能看到马赛克或切片条带。这不否定细结构可见性，但说明最终定量结果强烈依赖拼接、配准、分割和人工质控。

### 11. 论文、代码和解释性判断要分开

| 证据类型 | 可以说什么 |
|---|---|
| 论文直接报告 | 光学结构、采集参数、速度、分辨率、对比度、U-Net 设置和评估指标 |
| 图像直接观察 | 共焦 Airy 背景更暗、细 neurite 更清楚；机械切片深部图像更锐利；全脑图存在条带/网格 |
| 当前代码直接验证 | 坐标变换、融合 TIFF 拼接、方向变换/裁剪、HDF5 合并等重建工具 |
| 解释性判断 | CAB-OLST 的关键思想是用串行切片维持局部浅层成像质量，再计算恢复全局连续性 |

### 12. 已知缺口与复现难点

- **Not found in OLSTv2**：论文所述显微镜、stage、振动切片机采集控制脚本；
- **Not found in OLSTv2**：3D U-Net 的模型、训练、推理、Dice loss 和细胞中心后处理；
- **Not found in OLSTv2**：完整图谱配准、脑区汇总和 Vaa3D/TeraVR 调度；
- 论文的 Supplementary Tables 1–4 没有本地 Markdown，部分采集设置和平台比较无法在当前工作区逐项核对；
- U-Net 未说明随机种子、数据增强、精确训练/验证体数量、centroid 匹配阈值和推理 patch 重叠；
- OLSTv2 的 shell 子流程包含站点绝对路径和人工参数块，没有锁定环境、测试、示例数据或论文运行清单；
- 原始数据每套约 4–60 TB，完整复现不仅是软件问题，也是硬件、存储和实验操作问题。

综合来看，CAB-OLST 的技术原理和性能证据较完整，OLSTv2 也提供了可核验的重建代码；但当前工作区不能单独复现从显微镜采集到细胞计数或神经元 projectome 的完整生产流程。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## CAB-OLST Summary

### Problem

Brain-wide microscopy must cover centimeter-scale tissue while retaining the resolution and SNR needed to distinguish dense cell bodies, dendritic spines, axonal boutons, and continuous long-range axons. Conventional light-sheet fluorescence microscopy faces a field-of-view versus axial-resolution trade-off, and intact-volume imaging loses quality with depth because of objective working distance, scattering, and refractive-index mismatch (`paper.md:21-36`). Point-scanning approaches such as serial two-photon tomography (*Nature Methods*, 2012) and volumetric two-photon tomography (*eLife*, 2016) offer cellular mapping but have lower throughput and shorter signal integration than the platform reported here (`paper.md:157`).

### Proposed technology

The paper introduces confocal Airy beam oblique light-sheet tomography (CAB-OLST), a single-photon system combining:

- an SLM-shaped, scanned Airy beam for a thin light sheet with more than 10× the depth of field of a Gaussian beam;
- a 45° phase rotation and rolling-shutter virtual slit to suppress Airy side lobes and out-of-focus background without mandatory deconvolution;
- iSPIM geometry for unrestricted lateral scanning;
- wavelength-specific grating compensation for sequential multichannel alignment;
- automated 300-μm mechanical sectioning so each acquisition cycle images a newly exposed superficial slab.

The core systems idea is to preserve optical quality locally through destructive serial sectioning, then reconstruct global brain continuity computationally.

### Workflow

```text
label + clear + embed brain
        -> Airy/confocal oblique mosaic imaging
        -> section top 300 μm and repeat
        -> stitch + deskew + stripe removal
        -> atlas registration + annotation
        -> either 3D U-Net cell detection/counting
           or Vaa3D/TeraVR single-neuron tracing
```

For cell detection, the paper describes a three-class 3D U-Net (background, boundary, intracellular) trained on random 112 × 112 × 32 patches in minibatches of six. It uses an encoder depth of three, Adam at $10^{-3}$, 0.95 learning-rate decay per epoch, Dice loss, and three training epochs (`paper.md:238-253`). This implementation is not in the supplied OLSTv2 snapshot; the paper links it to a separate CAB-OLST analysis repository.

### Evaluation and main results

- Optical resolution after field stitching: 0.77 μm × 0.49 μm × 2.61 μm (`paper.md:12`; Extended Data Fig. 4).
- Whole-brain cell-type distribution imaging: 0.37 μm × 0.37 μm × 1.77 μm voxels in 10 h.
- Whole-brain single-neuron projectome imaging: 0.26 μm × 0.26 μm × 1.06 μm voxels in 58 h.
- Confocal versus standard Airy contrast: 4.7× for neurites and 1.2× for somata in the main comparison; under matched excitation conditions, 4.2× and 1.5×, respectively (`paper.md:59-62`).
- Mechanical sectioning improved soma and neurite contrast at depth, with paired-test $P=0.0060$ and $P=0.0010$ (`paper.md:68-79`).
- The 3D U-Net evaluation across five expert-annotated brain-region volumes reported precision 0.969, recall 0.985, and $F$ score 0.976 (`paper.md:253`).
- Three Gad2-H2B-GFP brains produced consistent major-region cell distributions (ANOVA $P=0.996$), and six neurons from two brains demonstrated distinct long-range projection patterns (`paper.md:111,125-136`).

The strongest figure evidence is paired local comparison: confocal gating makes thin neurites visibly sharper against darker background, and mechanical sectioning maintains clearer structures at 1.8-mm depth. Whole-brain views also show residual mosaic/section banding, so downstream reconstruction and segmentation remain material parts of the method.

### Code-paper match

The paper releases several separate software packages. The supplied `OLSTv2` repository is the package identified for cell-type-distribution analysis, but direct inspection shows that it primarily implements BigStitcher-oriented reconstruction utilities: coordinate transforms, volume fusion, oblique-to-coronal reorientation/cropping, TIFF export, and HDF5 merging. These behaviors are directly verified, but they cover only part of the paper workflow.

Overall full-pipeline fidelity is **low**; fidelity for the narrower reconstruction subpipeline is **medium**. The following were not found in the supplied code scope: microscope/stage/vibratome acquisition control, the custom 3D U-Net, the complete atlas-registration/counting workflow, and Vaa3D/TeraVR tracing orchestration. The repository contains site-specific shell subpipelines rather than a verified end-to-end production runner.

### Reproducibility assessment: 3/5

Positive factors:

- Processed/downsampled data sufficient for paper figures and analyses are deposited on Zenodo; raw 4–60-TB datasets are deposited in the Brain Image Library (`paper.md:268-277`).
- The paper provides quantitative hardware settings, optical equations, acquisition geometry, U-Net hyperparameters, and separate code links for reconstruction, segmentation, stripe removal, stitching, and tracing tools.
- OLSTv2 contains substantive source for reconstruction rather than only figures or pseudocode.

Limiting factors:

- The software is fragmented across several repositories/releases, while this workspace contains only OLSTv2.
- Custom hardware, instrument alignment, acquisition-control scripts, and multi-terabyte inputs are substantial barriers.
- OLSTv2 has hard-coded site paths, manually edited shell parameters, no environment lockfile or tests, and no paper-run configuration/example dataset.
- Supplementary Tables 1–4 are linked but were not available as local Markdown in this workspace.
- The U-Net report omits details such as random seeds, augmentation, exact train/validation counts, centroid matching threshold, and inference tiling.

CAB-OLST is therefore well documented as a technology concept and performance demonstration, but reproducing the complete system requires assembling hardware and multiple external computational components beyond the supplied repository.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
