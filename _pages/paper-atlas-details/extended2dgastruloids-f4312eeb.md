---
layout: default
permalink: /paper-atlas/extended2dgastruloids-f4312eeb/
title: "Extended2DGastruloids"
nav: false
description: "经典 BMP4 微图案二维 gastruloid 的优点是简单、重复性高，适合活细胞成像和定量扰动；缺点是以往通常只观察到约 42–48 小时，之后组织结构容易失序。因此，我们很难在同一可控体系中研究原条样区域之后的中胚层迁移、分化和空间组织。 本文把培养延长到 10 天，并把实验平台与三类计算分析结合：三维单细胞图像定量、活细胞轨迹分析、单细胞转录组及胚胎参考映射。"
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
    <h1>Extended2DGastruloids</h1>
    <p>Extended culture of 2D gastruloids to model human mesoderm development</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02669-4" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Extended2DGastruloids">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/idse/extendedgastruloid" target="_blank" rel="noopener noreferrer" aria-label="Open code for Extended2DGastruloids">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 延长培养的二维 gastruloid：如何观察人类中胚层发育

### 这项工作解决什么问题？

经典 BMP4 微图案二维 gastruloid 的优点是简单、重复性高，适合活细胞成像和定量扰动；缺点是以往通常只观察到约 42–48 小时，之后组织结构容易失序。因此，我们很难在同一可控体系中研究原条样区域之后的中胚层迁移、分化和空间组织。

本文把培养延长到 10 天，并把实验平台与三类计算分析结合：三维单细胞图像定量、活细胞轨迹分析、单细胞转录组及胚胎参考映射。

### 核心创新

细胞先在直径 700 µm 的圆形微图案上生长 24 小时，再加入 50 ng ml$^{-1}$ BMP4；培养基采用定义明确的 mTeSR1，并每天完全换液。这些改动使 colony 到第 4 天仍保持高度可重复的结构，并在中心形成“上层假复层上胚层样组织、下层间充质”的分层结构。

### 完整流程

```text
人多能干细胞单细胞悬液
  -> 700 µm 圆形微图案，mTeSR1 中预培养 24 h
  -> BMP4 诱导并每日换液
  -> 第 2–4 天：原条样细胞迁移与中胚层空间化
  -> 第 6–10 天：进一步出现心肌/内皮/体节相关状态

并行测量：
  固定样本 z-stack -> Ilastik + Cellpose -> 单核三维强度 -> r 与 (r,z) 分布
  TBXT 活细胞成像 -> CellPose + TrackMate -> MATLAB 轨迹、位移和方向角
  10x scRNA-seq -> SCVI/UMAP/Leiden -> 伪时间 -> 人/猴胚胎参考映射
```

### 图像分析如何工作？

显微图像先拼接，再按 z 切片分割细胞核。每个细胞核获得空间位置和各荧光通道的平均强度。为了比较不同 colony，作者把半径方向分成“每个 bin 含相同细胞数”的区间。若标记物 $m$ 的阈值为 $\tau_m$，bin $b$ 中的阳性比例可写为：

$$
P_{m,b}=\frac{1}{|b|}\sum_{i\in b}\mathbf{1}(I_{m,i}>\tau_m).
$$

同一思想扩展到 $(r,z)$ 二维网格，就能把“中心/边缘”和“上层/下层”同时表示出来。图 1 和图 3 中的定量图与原始截面图相互支持。

### 迁移分析揭示了什么？

TBXT-neon 时间序列表明，许多最终到达 colony 中心的细胞最初位于原条样环。对位置 $x_t$、中心 $c$ 和速度 $v_t$，作者比较 $v_t$ 与指向中心的向量 $c-x_t$，得到相对径向内移方向的偏角。偏角分布集中在 0° 附近，支持“定向内迁移”；同时也观察到向外迁移，在边缘形成 FOXF1 阳性的侧板中胚层样群体。

### 单细胞转录组如何定义细胞状态？

48、72、96 小时的六个样本过滤后包含 51,884 个细胞和 16,380 个基因。分析使用 SCVI 建立整合潜空间，再进行 UMAP 和 Leiden 聚类。中胚层被细分为早期/晚期新生中胚层、前部旁轴中胚层样、侧板中胚层样和连接柄样状态。差异基因使用 Earth Mover's Distance 排序；扩散伪时间从人工选择的多能性根细胞出发；scANVI/scArches 把 gastruloid 映射到 CS7 人胚和 CS8 猴胚参考。

这些映射不是一一对应，因此文中使用 `-like` 很重要：它表示转录和标记物相似性，而不是证明这些体外细胞已经拥有完整的体内身份。

### 信号通路结论

- 第 2 天后撤除 BMP 或加入 BMP 受体抑制剂，会显著削弱外周 FOXF1 阳性的侧向中胚层样群体。
- 抑制 Wnt 分泌主要削弱 TBX6 阳性的前体节/旁轴中胚层样群体。
- 加入 Activin、提高 Nodal 样信号，会抑制多类中胚层形成。

因此，不同空间群体不是同一种“泛中胚层”的随机波动，而是具有不同信号依赖的状态。

### 结果与局限

第 6–10 天可见 FOXC2/MEOX1、NKX2.5、ACTN2/MEF2C 和 PECAM 等体节、心肌和平滑肌/内皮相关标记。该体系适合研究模式形成与迁移，但不能等同于完整胚胎，也没有形成成熟器官。

代码与论文的概念匹配度为中等：图像分析、SCVI/Scanpy 和轨迹后处理均有实现；但原始图像仅可申请获取，部分计数矩阵和中间 AnnData/MAT 文件不在仓库，定制 CellPose 权重及完整 TrackMate 导出步骤缺失，也没有完整锁定的软件环境。因此它更像“研究分析快照 + 模板集合”，而不是一键复现实验包。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Extended Culture of 2D Gastruloids

### Problem

Human 2D gastruloids are simple, reproducible, and compatible with quantitative live imaging, but earlier protocols were generally studied only through about two days because organization deteriorated later. This work develops an extended culture system to observe human mesoderm morphogenesis and differentiation for up to ten days.

### What is introduced

The platform grows human pluripotent stem cells on 700-µm micropatterns for 24 hours before BMP4 induction, uses defined mTeSR1 medium, and performs daily medium changes. Colonies remain organized through day 4 and form a pseudostratified epiblast-like layer above mesenchyme. By combining 3D immunofluorescence, live TBXT-neon tracking, scRNA-seq, pseudotime, embryo-reference mapping, and signaling perturbations, the study resolves spatially distinct anterior paraxial-, lateral plate-, and connecting-stalk-like mesoderm.

### Main findings

- TBXT-positive cells migrate directionally from a primitive-streak-like ring both inward and outward, producing reproducible radial and vertical mesoderm organization.
- scRNA-seq at 48, 72, and 96 hours identifies early/late nascent, anterior paraxial, lateral plate, and connecting-stalk-like states that map to related human and monkey embryonic populations.
- Continued high BMP signaling is required for FOXF1-positive lateral-like mesoderm; high Wnt supports TBX6-positive presomitic/paraxial-like mesoderm; excess Activin/Nodal signaling antagonizes mesoderm formation.
- By days 6–10, colonies contain cells with cardiac/smooth-muscle, endothelial, and somite-related markers, although these remain heterogeneous `-like` derivatives rather than mature tissues.

### Computational workflow

The imaging pipeline stitches confocal tiles, segments nuclei slice by slice with Ilastik and Cellpose, consolidates masks, extracts per-nucleus 3D fluorescence, and computes equal-cell-count radial and $(r,z)$ distributions. Live-cell objects are linked with Fiji TrackMate and quantified in MATLAB. Transcriptomic notebooks use Scanpy/scvi-tools for SCVI integration, UMAP/Leiden clustering, Earth Mover's Distance marker analysis, diffusion pseudotime, MAGIC visualization, and scANVI/scArches reference transfer.

### Reproducibility

Code is available at `idse/extendedgastruloid` and the local snapshot matches the major analysis concepts with **medium fidelity**. The repository includes reusable MATLAB image-analysis code, experiment templates, tracking post-processing, and large scRNA-seq notebooks. It is not a turnkey package: raw microscopy is available only on request, large count/intermediate files are external, custom CellPose weights and the full TrackMate export workflow are missing, paths are dataset-specific, and software environments are not pinned. Reproducibility rating: **3/5**.

### Limitations

The system models selected aspects of gastrulation and mesoderm development, not a complete embryo. Cell identities rely on marker programs and reference similarity; some mappings are mixed. The radially constrained geometry is a major advantage for quantification but does not reproduce full embryonic axes, extraembryonic context, or organ-level maturation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
