---
layout: default
permalink: /paper-atlas/euclideanfastattention-77ae3c7a/
title: "EuclideanFastAttention"
nav: false
wide: true
description: "分子机器学习力场需要根据原子种类与三维坐标预测能量和力。局部消息传递网络为了达到近似线性复杂度，通常只让 rcut 内的原子交换信息；层数增加只能沿已有邻接路径传递，远距离或断开的原子仍可能不可见。标准自注意力能全局建模，却需要二次的原子对计算。EFA 的目标是在保持三维几何对称性的前提下，让每个原子获得全局信息，同时对原子数保持线性标度。"
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
      <span>Representation Models</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>EuclideanFastAttention</h1>
    <p>Machine learning global atomic representations with Euclidean fast attention</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/thorben-frank/euclidean_fast_attention" target="_blank" rel="noopener noreferrer" aria-label="Open code for EuclideanFastAttention">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Euclidean Fast Attention (EFA) 方法解读

### 它解决什么问题

分子机器学习力场需要根据原子种类与三维坐标预测能量和力。局部消息传递网络为了达到近似线性复杂度，通常只让 `r_cut` 内的原子交换信息；层数增加只能沿已有邻接路径传递，远距离或断开的原子仍可能不可见。标准自注意力能全局建模，却需要二次的原子对计算。EFA 的目标是在保持三维几何对称性的前提下，让每个原子获得全局信息，同时对原子数保持线性标度（arXiv `paper.md:20-41`）。

### 核心想法

对一个单位方向 `u`，EFA 用 ERoPE 将特征按位置投影旋转：

$$
\mathrm{ERoPE}_{\vec u}(\bm x,\vec r)=\bm x e^{i\omega\vec u\cdot\vec r}.
$$

这样查询原子 `m` 与键原子 `n` 的乘积中出现相对位移 `r_m-r_n`。单个方向会依赖坐标系，因此 EFA 对单位球面上的方向做积分；该积分给出 `sinc(omega r_mn)`，只依赖距离。若输入含有等变特征，EFA 再与球谐函数耦合，使输出保留方向信息（arXiv `paper.md:55-120`）。

### 计算流程

```text
原子类型、坐标、局部邻接图
        -> 局部等变消息传递
        -> 生成 q/k/v
        -> 对每个 Lebedev 方向做 ERoPE(q,k)
        -> 先汇总 sum_n(k_tilde outer v)
        -> 每个原子用 q_tilde 查询该全局汇总
        -> 对方向按权重求和，必要时与球谐函数做张量积
        -> 残差连接与原子级 MLP
        -> 总能量与其坐标梯度（力）
```

关键是 `K^T V` 型统计量只需对全部原子累加一次，再被每个查询原子使用，因此不必显式构造 `N x N` 注意力矩阵。代码中这一过程位于 `rope.py:172-263`，批次内使用 `segment_sum` 防止不同分子混合；`fast_attention.py:256-380` 选择 Lebedev 网格或周期性边界下的晶格方向。

### 为什么不仅是“更远的消息传递”

局部 MPNN 可通过增加层数扩大有效截止半径，但信息被多次压缩且依赖中继路径。EFA 直接汇总全系统的键-值统计量，因而可以在一次更新中访问远距离原子。图 2 的链图显示局部 MP 所需层数随链长增加，EFA 维持一次更新；图 3 显示 MP+EFA 在 NaCl 型系统的误差更低，并给出近线性的推理时间。

当相互作用依赖方向，仅用距离不够。累烯例子中，`ell=0` 的不变 EFA 仍不能正确恢复二面角势垒；加入 `ell>0` 的等变特征后，EFA 才接近参考曲线，并给出较合理的分子动力学分布（arXiv `paper.md:217-230`）。

### 实验与可复现性

论文测试非局域电荷转移、S_N2 反应和累烯等体系。文中报告 MP+EFA 在非局域电荷转移表的 8 项指标中有 7 项领先，并在给定 S_N2 比较中降低能量与力误差；图 4 还显示没有 EFA 的局部模型会产生错误的反应轨迹。公开仓库包含 EFA 实现、配置、测试和 notebooks，核心实现与论文高度匹配。

补充 PDF 没有转为 Markdown，也没有在本次分析中运行全部训练任务。因此补充材料专属超参数和逐表复现应视为 `Not found`，而非已验证结论。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Euclidean Fast Attention: Summary

EFA is a global representation module for Euclidean data, designed for atomistic machine-learning force fields where conventional local message passing misses long-range distance- and orientation-dependent effects. It replaces quadratic pairwise attention with a factorized linear update: Euclidean rotary positional encoding (ERoPE) embeds positions along integration directions, and a Lebedev-sphere average restores the relevant symmetry. The result can consume equivariant features and be inserted into local MPNNs with residual/refinement blocks (arXiv `paper.md:52-120`; `fast_attention.py:142-381`).

The paper evaluates idealized interactions, NaCl-like systems, non-local charge transfer, S_N2 reactions, dimers, and cumulenes. Its direct visual evidence shows EFA retaining global-potential structure past a local cutoff, tracking linear inference-time fits, producing the reaction trajectory that local MP misses, and preserving the cumulene torsional dynamics. It reports best performance in 7 of 8 non-local-charge-transfer metrics and 34x/8x energy/force MAE reductions for the stated S_N2 comparison (arXiv `paper.md:188-215`).

Reproducibility is good but not complete: the exact public implementation, configs, tests, and notebooks are present at commit `a7f28ca`, and paper-to-code fidelity is high for ERoPE and factorized attention. The DOI HTML is subscription-preview-only, so detailed support comes from the locally retained arXiv preprint `2412.08541`; the supplementary PDF and full expensive training runs were not independently reproduced.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
