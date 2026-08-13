---
layout: default
permalink: /paper-atlas/correlated-cryo-em-msi-chemical-mapping-76e1c3d3/
title: "Correlated_cryo_EM_MSI_chemical_mapping"
nav: false
description: "冷冻电镜（cryo-EM）能看清细胞膜、储存颗粒等超微结构，却通常不能直接判断某个密度由什么化学物质组成。成像质谱能检测元素或分子碎片的空间分布，但结构分辨率和形态信息较弱。本工作把两种模态串联在同一块玻璃化样品、同一区域上，使“结构在哪里”和“化学物质在哪里”能够相互解释。 作者建立了 cryo-EM-FIB-SIMS 流程：先记录不会被保留的高分辨结构信息，再用镓离子束逐像素溅射样品，并在每个像素采集飞行时间质谱。"
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
      <span>Nature Methods · 2026</span>
    </div>
    <h1>Correlated_cryo_EM_MSI_chemical_mapping</h1>
    <p>Subcellular chemical mapping using correlated cryogenic electron and mass spectrometry imaging</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/lmb-mass-spec-compbio/BPAF_uptake_Caulobacter_crescentus_TMT_proteomics" target="_blank" rel="noopener noreferrer" aria-label="Open code for Correlated_cryo_EM_MSI_chemical_mapping">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 冷冻电镜与 FIB-SIMS 关联成像：亚细胞化学定位方法

### 要解决的问题

冷冻电镜（cryo-EM）能看清细胞膜、储存颗粒等超微结构，却通常不能直接判断某个密度由什么化学物质组成。成像质谱能检测元素或分子碎片的空间分布，但结构分辨率和形态信息较弱。本工作把两种模态串联在同一块玻璃化样品、同一区域上，使“结构在哪里”和“化学物质在哪里”能够相互解释。

### 核心创新

作者建立了 cryo-EM-FIB-SIMS 流程：先记录不会被保留的高分辨结构信息，再用镓离子束逐像素溅射样品，并在每个像素采集飞行时间质谱。FIB 同时产生二次电子图像，因此可以先把 cryo-EM 与二次电子图人工配准，再把同视野、同像素尺寸的 SIMS 离子图叠加上去。样品背面增加铂和有机金属涂层，以减少移动并提高质谱信号。

### 方法流程

```text
玻璃化样品
   |
   +--> 可选 cryo-LM：大视野找目标
   |
   +--> cryo-EM / cryo-ET：记录超微结构
   |
冷冻转移 + 样品背面稳定涂层
   |
Ga FIB 逐像素扫描并溅射
   |-------------------------------|
二次电子 FIB 图                 每像素完整 ToF 质谱
   |                               |
   |                         选择目标 m/z 通道
   |                               |
   +----与 cryo-EM 人工配准--------+--> 化学-结构叠加图
                                   |
                             重复扫描得到深度序列
```

标准采集条件包括 30 kV、50 pA、512 × 512 扫描、SIMS 数据 8 × 8 合并、每像素 12.8 μs 驻留时间和约 10–30 nm 的未合并像素。每个像素的强度表示一次提取中的离子计数。连续扫描会逐层去除材料，因此可以形成近似三维的化学深度栈；作者估计每帧去除约 10–50 nm，但不同材料的溅射效率和束损伤会造成不均匀性。

### 如何从图像得到生物学结论

方法不是只依靠一个亮点，而是把离子信号、结构位置和对照共同使用。例如，在未标记的 *C. crescentus* 中，K、Mg、PO~2~ 和 PO~3~ 的局部峰与冷冻电镜中的储存颗粒对应，而 Na 更弥散。BPAF 是含氟污染物，因此用负离子模式下 F 的 19 *m/z* 作为示踪信号。处理细胞中，氟信号与中等对比度的储存颗粒共定位；未处理对照中的氟信号低很多且不呈特异定位，PO~2~ 则仍覆盖整个细胞。

### BPAF 案例与蛋白质组学

BPAF 暴露会延缓细菌生长，并在细胞沉淀中富集。TMT 蛋白质组学显示处理组和对照组在多个时间点分离，acrB2、TipR 等外排相关蛋白上调。公开代码完整覆盖这一辅助分析：过滤 PSM、汇总为蛋白丰度、利用内部桥接样本归一化两个 TMT plex、进行 PCA，并在每个时间点使用 limma `treat`（折叠变化阈值 1.25）检验，再用 BH 方法控制 1% FDR。

关联成像进一步显示 BPAF 暴露后的氟热点位于储存颗粒；颗粒平均直径由 186.4 ± 37.9 nm 增至 206.9 ± 38.5 nm（*P* < 0.0001）。作者据此提出：细胞虽然上调外排系统，但 BPAF 被快速隔离进颗粒，外排泵难以接触并清除它。

### 方法边界

- SIMS 会破坏样品，所以必须先完成 cryo-EM。
- 结构分辨率、SIMS 有效分辨率和 8 × 8 合并后的像素尺度并不相同。
- 配准依赖细胞轮廓、颗粒和碳膜孔等标志物，论文未给出自动优化目标或配准误差。
- 单个 *m/z* 峰不总是分子特异；需要标准品、同位素、碎片信息和阴性对照。
- 公开仓库只包含蛋白质组学 R Markdown。核心的 TofSimsExplorer/Python 处理、峰积分、背景校正、人工叠加和三维重建代码均未找到。

因此，这项工作的价值主要是一种实验技术平台：它把冷冻状态下的高分辨结构与逐像素化学信息连接起来；其主要复现瓶颈则是专用仪器、厂商软件和未脚本化的配准/图像处理。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Subcellular Chemical Mapping with Correlated Cryo-EM and FIB-SIMS

### Overview

This Nature Methods 2026 paper addresses a basic limitation of cryo-electron microscopy: cellular densities can be resolved structurally but are difficult to identify chemically. Conversely, imaging mass spectrometry identifies elemental and molecular signatures but lacks cryo-EM's ultrastructural context. The authors introduce a correlated cryo-EM-FIB-SIMS workflow that images the same vitrified specimen first by cryo-EM and then by gallium focused-ion-beam time-of-flight SIMS, aligning pixel-resolved ion maps to cellular structure.

### What is new

The platform combines cryogenic transfer, backside organometallic coating for stability, simultaneous secondary-electron and SIMS acquisition, and landmark-based correlation to cryo-EM. It works on unlabeled bacteria, metal- and isotope-labeled specimens, cryo-light-microscopy targets, and FIB-milled bacterial or yeast lamellae. Repeated sputtering scans additionally provide depth-resolved chemical information.

### Main evidence

Gold-labeled cells establish that Au 197 *m/z* signal can be correlated with cryo-EM-visible nanoparticles. In unlabeled *Caulobacter crescentus*, K, Mg, and phosphate signals localize to cryo-EM storage granules while Na is more diffuse. A cryo-CLEM experiment separates fluorescently labeled cell classes across light microscopy, EM, and SIMS, and lamella experiments demonstrate compatibility with cryo-ET and eukaryotic specimens.

The biological application tracks bisphenol-AF (BPAF) using its F 19 *m/z* signature. BPAF retards growth, accumulates in cell pellets, alters the proteome, and upregulates efflux-associated proteins. Correlated imaging places fluorine hotspots specifically in medium-contrast storage granules rather than the cytosol or high-contrast stress aggregates. Granules are larger after exposure (206.9 ± 38.5 nm, *n* = 1,464 versus 186.4 ± 37.9 nm, *n* = 252; *P* < 0.0001), supporting rapid, persistent sequestration that may shield BPAF from efflux pumps.

### Reproducibility and limitations

The public GitHub snapshot reproduces the TMT-proteomics adjunct: PSM filtering, protein aggregation, internal-reference normalization across two plexes, PCA, limma/treat testing, BH correction, and efflux-protein heatmaps. Its paper-code fidelity is high for Fig. 4c,d but low for the central imaging technology. No acquired source implements FIB-SIMS acquisition, TofSimsExplorer/Python ion-image processing, peak integration, manual registration, overlay, or 3D reconstruction. Registration is manually landmark-driven and no quantitative alignment uncertainty is reported. SIMS is destructive, chemical resolution differs from structural resolution, sputtering can be nonuniform, and chemical assignments require appropriate standards and controls.

**Reproducibility rating: 3/5.** Instrument and acquisition settings are detailed and the proteomics notebooks/data are public, but the core imaging-analysis and registration steps are vendor-dependent and incompletely scripted.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
