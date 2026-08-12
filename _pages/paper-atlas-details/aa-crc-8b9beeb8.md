---
layout: default
permalink: /paper-atlas/aa-crc-8b9beeb8/
title: "AA-CRC"
nav: false
description: "普通 conformal risk control（CRC）可以控制总体平均风险，但所有样本共用一个阈值。这样容易出现一种低效现象：简单样本的集合过大、假阳性过多，而困难样本又可能不够稳健。已有条件 conformal 方法通常要求研究者预先给出人群或条件函数；图像难度等连续因素很难靠人工分组表达。"
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
      <span>Machine Learning Algorithm</span>
      <span>AISTATS (PMLR 258) · 2025</span>
    </div>
    <h1>AA-CRC</h1>
    <p>Automatically Adaptive Conformal Risk Control</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2406.17819" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## AA-CRC 方法详解

### 它解决什么问题

普通 conformal risk control（CRC）可以控制总体平均风险，但所有样本共用一个阈值。这样容易出现一种低效现象：简单样本的集合过大、假阳性过多，而困难样本又可能不够稳健。已有条件 conformal 方法通常要求研究者预先给出人群或条件函数；图像难度等连续因素很难靠人工分组表达。

AA-CRC 的目标是：在维持目标风险 $\alpha$ 的同时，让阈值随样本难度自动变化，并对由学习到的函数类所描述的群组、标签条件和协变量漂移给出风险保证。

### 核心思想：把 CRC 写成优化问题

论文先定义风险残差的原函数：

$$
I(x,y,u)=\int(\ell(x,y,u')-\alpha)\,du'\big|_u.
$$

然后在函数类 $\Lambda$ 中优化阈值函数 $\lambda$。最优解的一阶条件要求：对 $\Lambda$ 中任意非负加权函数，损失相对目标 $\alpha$ 的加权平均不能为正。这就把 conformal 的边际校准转化为一种 multiaccuracy 风险校准。

当 $\Lambda$ 只包含常数时，方法退化为普通 CRC；当它包含重叠群组指示变量时，得到群组条件风险控制；当函数依赖 $(x,y)$ 时，可表达标签条件控制；当 $\lambda(x)=\Phi(x)^\top\theta$ 时，可控制嵌入空间线性可表达的协变量漂移。

### 自动学习条件函数

```text
基础预测器
   ↓
独立 residual 数据：学习“样本有多难”
   ↓
构造 Phi(x) 和函数类 Lambda
   ↓
校准数据 + 测试样本特征：优化 AA-CRC 目标
   ↓
样本特异阈值 lambda(x)
   ↓
区间或分割掩膜
```

对于表格回归，随机森林学习绝对残差，每棵树的叶节点成为一个重叠群组，叶节点成员向量就是 $\Phi(x)$。对于图像分割，先找出每张 residual 图像在目标召回率下允许的最大像素阈值，再训练 ResNet/CNN 预测这个阈值；去掉最后预测层后得到难度嵌入 $\Phi(x)$，校准阶段只优化其上线性阈值头。

结构化标签空间不能逐个枚举，因此论文给出不依赖测试标签的高效目标（Eq. 24）。它在校准风险积分之外加入测试样本阈值项 $(1-\alpha)\lambda(X_{n+1})/(n+1)$。理论只要求局部一阶最优，因此落入局部极小点仍能维持风险论证；找到更好的极小点主要改善精度。

### 实验结果

- 模拟回归：目标覆盖率 0.9，边际覆盖率 0.897；自动群组覆盖率范围 0.886-0.913。
- 息肉分割：100 次划分的召回率为 $0.906\pm0.021$；平均精度从 CRC 的 0.395 提升到 0.457。
- 火焰分割：召回率为 $0.898\pm0.003$；平均精度从 0.363 提升到 0.403。

这里的提升不是降低召回要求，而是按样本难度更有效地分配同一个风险预算。六张主图的直接检查也显示：困难样本获得较低阈值，简单样本获得较高阈值，从而减少假阳性。

### 假设与边界

AA-CRC 需要交换性、嵌套预测集、关于阈值单调且左连续的损失，以及适当的函数空间和正则项。它不能在完全无假设的条件下保证每一个 $x$ 的点态条件风险；保证只覆盖 $\Lambda$ 能表达的群组或漂移。学到的嵌入如果遗漏关键难度因素，相应的条件保证也不会自动扩展到这些方向。

官方代码对分割主线的忠实度为 **medium-high**：风险积分、目标梯度、可微阈值学习、CRC 对照和 precision/recall 评估均能定位到直接源码。但数据、权重和中间预测未随仓库提供，实验脚本包含作者机器绝对路径，也没有锁定的运行环境；回归部分的随机森林 Algorithm 1 未找到清晰的直接实现。因此代码适合学习方法和重建分割实验，但不能一键复现全部结果。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Automatically Adaptive Conformal Risk Control

### Paper summary

Classical conformal prediction and conformal risk control (CRC) give distribution-free marginal guarantees, but can spend the error budget unevenly: easy samples may receive overly conservative sets while difficult regions remain poorly controlled. Prior relaxed-conditional methods can enforce validity over a user-chosen class of groups or covariate shifts, but choosing that class is itself difficult.

AA-CRC turns CRC into an implicit optimization problem. The objective integrates the difference between observed loss and target risk, and its first-order conditions yield multiaccuracy-style weighted-risk guarantees. This construction extends conditional conformal reasoning from coverage to general monotone risks and permits conditioning functions of both covariates and labels. The “automatic” component learns a function class that predicts sample difficulty: random-forest leaf indicators for tabular regression, or learned neural embeddings for images. A test-dependent but label-independent surrogate avoids enumerating structured labels.

The guarantees interpolate between ordinary marginal CRC, overlapping-group risk control, label-conditional control, and robustness to covariate shifts representable in the chosen embedding span. They require exchangeability, nested prediction sets, monotone left-continuous loss, and suitable optimization/regularization; they are not arbitrary pointwise conditional guarantees.

### Evaluation

In simulated regression, target coverage 0.9 yields 0.897 marginal coverage and 0.886-0.913 coverage over adaptive RF groups. On polyp segmentation, across 100 splits AA-CRC controls recall at $0.906\pm0.021$ while increasing average precision from 0.395 to 0.457 versus CRC. On fire segmentation, recall is $0.898\pm0.003$ and precision rises from 0.363 to 0.403. Direct figure inspection corroborates input-dependent thresholds and precision gains at approximately the same recall target.

### Reproducibility and limitations

The official repository `vincentblot28/multiaccurate-cp` was pinned at commit `64504c011ac2db910e258037e48170a63381b5e6`. Code fidelity is **medium-high**: numerical risk integration, objective gradients, differentiable threshold optimization, adaptive inference, CRC comparison, and repeated-split metrics are present. However, crucial experiment orchestration lives in notebooks/scripts with absolute local paths; datasets, trained weights, and derived predictions are external; no pinned environment is supplied; and a direct implementation of the paper's random-forest Algorithm 1 was **Not found**. The repository therefore explains and substantially supports the segmentation method but is not a turnkey reproduction.

Formal publication: *Proceedings of the 28th International Conference on Artificial Intelligence and Statistics* (AISTATS 2025), PMLR 258:19-27.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
