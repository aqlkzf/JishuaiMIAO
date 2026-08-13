---
layout: default
permalink: /paper-atlas/mrscope-7bcf3a9a/
title: "MRScope"
nav: false
wide: true
description: "fMRI 能覆盖全脑，但 BOLD 是血氧和血容量变化形成的间接信号，无法指出具体是哪类、哪一个神经元在活动。钙成像能分辨遗传标记的单细胞，却通常只能看局部皮层。MRScope 把两者放进同一台 MRI、同一只清醒小鼠和同一组刺激试次中，从而把“局部单细胞活动”放回“全脑血流动力学背景”里解释。 作者构建了 MRI 兼容的单光子显微镜：用丙烯酸镜片降低磁敏感伪影，用光纤从磁体外送入激发光，把 CCD 放到距等中心 7."
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
    <h1>MRScope</h1>
    <p>Simultaneous single-cell calcium imaging of neuronal population activity and brain-wide BOLD fMRI</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/rlemubaghs/camri" target="_blank" rel="noopener noreferrer" aria-label="Open code for MRScope">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MRScope 方法中文解读

### 解决什么问题

fMRI 能覆盖全脑，但 BOLD 是血氧和血容量变化形成的间接信号，无法指出具体是哪类、哪一个神经元在活动。钙成像能分辨遗传标记的单细胞，却通常只能看局部皮层。MRScope 把两者放进同一台 MRI、同一只清醒小鼠和同一组刺激试次中，从而把“局部单细胞活动”放回“全脑血流动力学背景”里解释。

### 核心创新

作者构建了 MRI 兼容的单光子显微镜：用丙烯酸镜片降低磁敏感伪影，用光纤从磁体外送入激发光，把 CCD 放到距等中心 7.1 cm 的位置，并用 D₂O 浸没消除空气界面造成的信号缺失。系统达到约 2.5 µm 光学分辨率、1.45 mm² 视野，同时采集全脑 BOLD。

### 分析流程

```text
同步记录
├─ 荧光电影 → 运动/漂白校正 → CNMF-E → 单细胞、neuropil、群体 ΔF/F
│                                      └→ 手工血管掩膜 → 细胞到最近血管距离
└─ fMRI → 配准/GLM → 显著 BOLD 体素 → 解剖脑区 → PCA

两类线性 SVM 回归：
1. 所有单细胞轨迹 → 预测局部 BOLD
2. 局部或各脑区 BOLD → 预测平均细胞群活动
并用时间打乱数据作为基线，以十折交叉验证 NRMSE 衡量性能。
```

误差定义为

$$
\mathrm{NRMSE}=\frac{\sqrt{\frac{1}{n}\sum_i(x_i-\hat{x}_i)^2}}{\sigma_x}.
$$

### 为什么要做 SVM-RFE

线性 SVM 的 β 权重可以表示每个细胞对预测的贡献。算法反复拟合模型，每轮按“绝对值最小”“最负”或“最正”的权重删除一个细胞，最终得到完整排名。再把排名与细胞到最近血管的欧氏距离比较，就能问：与 BOLD 正相关或负相关的细胞，空间位置是否不同？结果显示，负权重细胞更靠近血管，而强正响应细胞的位置更分散。

### 主要结果

- 五只小鼠共分析 236 个 L2/3 桶状皮层神经元。
- 局部细胞活动预测 BOLD 的误差显著低于时间打乱基线（P≤0.005）。
- 靠近血管的细胞更常表现为负向 BOLD 关系；该空间效应提示局部血管组织会影响 BOLD 的细胞来源解释。
- 反向模型表明，局部以及体感、运动、听觉、丘脑和纹状体等区域的 BOLD 都包含对局部神经群活动的预测信息。

### 应如何理解

这是相关和预测框架，不是因果模型。SVM 能说明两个信号共享信息，却不能证明 BOLD 驱动神经元或神经元直接驱动某个远端脑区。样本量较小、血管需要手工标注、部分检验未做多重比较校正、钙成像仍局限于浅层皮层，而且原始数据未随代码仓库公开，都是重要限制。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

This Nature Methods 2026 technology paper introduces MRScope, an MRI-compatible single-photon microscope that records genetically defined neurons at cellular resolution during whole-brain BOLD fMRI in awake mice. It fills the gap between fiber photometry, which pools cells and neuropil, and fMRI, which offers brain-wide coverage without cellular source specificity.

The system combines acrylic optics, fiber-delivered excitation, an MRI-compatible CCD positioned 7.1 cm from isocenter, D₂O immersion and an awake head-fixed whisker-stimulation setup. It provides a 1.45-mm² field of view, 1.1-µm pixels and about 2.5-µm optical resolution without noticeable BOLD artifacts. During stimulation, the study measured ~4.9% local BOLD, ~2.7% neuropil ΔF/F, ~1.7% cellular-population ΔF/F and ~3.8% vessel dilation, with the optical signals preceding the slower hemodynamic peak.

From 236 layer-2/3 barrel-cortex neurons in five mice, linear SVM regression predicted local BOLD significantly better than temporally shuffled controls (P≤0.005). SVM recursive feature elimination showed that negatively weighted neurons were nearer local vessels, whereas positively weighted neurons were more spatially heterogeneous. Reversing the decoder showed that local and distributed regional BOLD patterns predicted the calcium population signal; regional PCA maps implicated somatosensory, motor, auditory and subcortical networks.

Reproducibility is moderate. The public `camri` repository contains preprocessing, decoder, RFE, connectivity and figure scripts that closely match the paper, but raw data are available only on request, MATLAB dependencies are not pinned, and the entry script contains absolute author-machine paths. Hardware design files are referenced separately in `open_mrscope`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
