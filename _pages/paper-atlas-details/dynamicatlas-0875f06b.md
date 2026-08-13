---
layout: default
permalink: /paper-atlas/dynamicatlas-0875f06b/
title: "DynamicAtlas"
nav: false
wide: true
description: "传统发育图谱主要由不同时间点的固定样本组成，能描述细胞命运和基因表达，却难以直接回答组织“怎样运动并形成形状”。DynamicAtlas 把活体电影与固定样本统一到同一空间坐标和同一“形态时间”上，从而让基因表达、组织流动和器官形变可以跨胚胎比较。 关键点是：实验室时钟不是发育时钟。两个胚胎即使采集时间相同，也可能处于不同形态阶段；因此方法用可观察的形态变化来定义时间。"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>DynamicAtlas</h1>
    <p>DynamicAtlas: a morphodynamic atlas for Drosophila development</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02897-8" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for DynamicAtlas">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/npmitchell/dynamicAtlas" target="_blank" rel="noopener noreferrer" aria-label="Open code for DynamicAtlas">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DynamicAtlas 方法详解

### 它解决什么问题？

传统发育图谱主要由不同时间点的固定样本组成，能描述细胞命运和基因表达，却难以直接回答组织“怎样运动并形成形状”。DynamicAtlas 把活体电影与固定样本统一到同一空间坐标和同一“形态时间”上，从而让基因表达、组织流动和器官形变可以跨胚胎比较。

### 核心思路

```text
三维活体/固定成像
 -> 胚胎表面展开为二维图并对齐身体轴
 -> 提取随发育变化的形态特征
      Runt 等条纹形状，或 PIV 积分得到的组织形变
 -> 两两比较所有时间点，得到相似度矩阵
 -> 在高相似度“山脊”上用 fast marching 找对应路径
 -> 把所有两两路径组成弹簧网络并松弛
 -> 得到共识形态时间轴
 -> 给固定样本打时间戳并估计不确定性
 -> 构建集合平均、流场相关矩阵和扰动比较
```

关键点是：实验室时钟不是发育时钟。两个胚胎即使采集时间相同，也可能处于不同形态阶段；因此方法用可观察的形态变化来定义时间。

### 两种时间对齐信号

1. **基因表达形态**：分割 pair-rule gene 条纹边界，比较两个活体序列中所有帧组合的形态相似度。
2. **组织形变**：通过 PIV 得到瞬时速度场，再积分成累积形变轨迹；两个胚胎在相似形变状态时被判为对应时间。

相似度矩阵通常有一条弯曲的高相似度脊线。代码 `shortestPathInImage.m` 把它变成加权表面，并用 fast marching 找单调路径。随后 `relaxPairwiseCorrespondenceNetwork.m` 把多胚胎的两两约束视为弹簧网络：固定一个参考时间点以去掉整体平移自由度，再优化其他时间点，得到比“全部对齐到单个胚胎”更稳健的共识时间轴。

### 固定样本怎样进入图谱？

固定样本只有一个形态快照。方法将该快照与活体共识时间轴逐时刻比较，最佳匹配位置就是时间戳。若匹配曲线平坦或胚胎间差异大，不确定性就高：

$$\sigma_t=\frac{\sigma_\chi}{|\partial_t\chi|}.$$

因此误差条不仅反映拟合好坏，也反映该形态特征是否能精确区分时间。

### 主要发现

- WT 胚胎的全局流动方向在若干时间段保持近似不变，形成 DC、VF、GBE 等“准稳态流模块”；组织仍在运动，稳定的是流动模式。
- DV 轴模式形成突变体丢失多个 WT 模块，AP 轴突变体保留更多模块，说明空间对称性破缺与流动组织有关。
- 温度改变运动速度，但按特征速度重标时间后，17、22、27 °C 的速度与累积形变可以对齐；细胞分裂时间却按不同倍率变化。
- 同样思想可用于三维中肠，以组织坐标系中的面外形变建立器官形态时间。

### 代码与局限

MATLAB 仓库真实实现了查询、PIV、fast marching 对应和共识网络松弛，代码—论文一致性为中等。局限是数据和依赖外置、示例含本机绝对路径、Python 接口在另一 Zenodo 包中，而且本次未运行端到端复现。补充材料只提供 PDF 链接，未转为本地 `SUPP_MD`，其中独有的公式和教程细节保持 `MISSING`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DynamicAtlas

DynamicAtlas is a morphodynamic atlas that places live movies and fixed samples from 500 *Drosophila* embryos, including wild type and 18 mutants, into shared spatial coordinates and a common morphological timeline. It fills a gap left by static expression atlases: tissue shape change must be measured continuously to relate gene-pattern dynamics to mechanics.

The workflow cartographically projects each 3D surface, registers body axes, extracts either pair-rule-gene stripe geometry or PIV-derived cumulative tissue deformation, and builds all pairwise time-similarity matrices. Fast-marching paths provide embryo-to-embryo correspondences; a relaxed correspondence network creates a consensus clock. Fixed samples are then timestamped by comparison with this live sequence, with uncertainty derived from ensemble variability and temporal sensitivity.

Using the aligned atlas, the authors identify reproducible periods in which global tissue-flow patterns are quasi-stationary. Dorsal–ventral patterning mutants lose several WT flow modules, whereas anterior–posterior mutants retain more of their organization. Across 17, 22 and 27 °C, velocity magnitude changes but accumulated-deformation trajectories align after a simple time rescaling; mitotic timing scales differently. A 3D embryonic-midgut analysis shows analogous modules in Lagrangian out-of-plane deformation.

Reproducibility is **3/5**. Paper text, 16 local figures and a real MATLAB implementation are available. The repository contains atlas queries, PIV utilities, fast-marching correspondence and consensus-timeline relaxation, plus a demo workflow. However, atlas data and MATLAB dependencies are external, several master scripts contain machine-specific paths, the separate Python interface was not acquired, and no end-to-end run or main-figure reproduction was performed. Supplementary-only details are explicitly MISSING because the supplementary PDF was not converted.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
