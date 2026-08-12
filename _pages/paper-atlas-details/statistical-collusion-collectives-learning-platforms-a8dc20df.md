---
layout: default
permalink: /paper-atlas/statistical-collusion-collectives-learning-platforms-a8dc20df/
title: "Statistical_Collusion_Collectives_Learning_Platforms"
nav: false
description: "论文研究的不是生物信息学，而是机器学习平台中的集体行动与数据投毒。平台用 N 个用户提交的数据训练分类器，其中 n 个用户形成集体。他们想统一修改自己的特征或标签，让平台在特定输入上给出期望的预测，但行动本身可能有风险，因此需要在行动前回答：凭集体自己汇总的数据，能否计算一个可信的成功率下界？ 集体只知道自身样本和总样本量 N。"
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
      <span>Proceedings of the 42nd International Conference on Machine Learning (PMLR 267) · 2025</span>
    </div>
    <h1>Statistical_Collusion_Collectives_Learning_Platforms</h1>
    <p>Statistical Collusion by Collectives on Learning Platforms</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2502.04879" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法详解：学习平台上的群体统计合谋

### 解决什么问题

论文研究的不是生物信息学，而是机器学习平台中的集体行动与数据投毒。平台用 $N$ 个用户提交的数据训练分类器，其中 $n$ 个用户形成集体。他们想统一修改自己的特征或标签，让平台在特定输入上给出期望的预测，但行动本身可能有风险，因此需要在行动前回答：凭集体自己汇总的数据，能否计算一个可信的成功率下界？

### 核心思想

集体只知道自身样本和总样本量 $N$。它先选目标，再估计变换后特征的频率、目标标签与竞争标签之间的差距，并用

$$R_\delta(k)=\sqrt{\frac{\log(1/\delta)}{2k}}$$

修正有限样本误差。同时用 $\varepsilon/(1-\varepsilon)$ 表示平台分类器偏离经验频率最优分类器的能力。对每个变换后特征 $\tilde x$，若“集体注入的支持”减去“非集体数据的抵抗、统计误差和平台适应项”仍为正，就认为这个特征已被攻破；通过特征的经验比例再减去测试集误差，就是成功率的高概率下界。

```text
集体数据 + N + 置信度 + 平台误差 epsilon
  -> 选择 planting / unplanting / erasing
  -> 固定或从子样本估计共同策略 h
  -> 估计特征频率与标签差距
  -> 加入有限样本误差
  -> 判断每个特征是否跨过阈值
  -> 输出行动前可计算的成功率下界
```

### 三类策略

1. **Signal planting**：把样本改成 $(g(x),y^*)$，强迫信号集合与目标标签绑定；若标签不能改，论文也给出只改特征的版本。
2. **Signal unplanting**：目标是让预测不再等于 $y^*$。先拿出 $n_e$ 个成员，对每个 $\tilde x$ 估计最常见的非目标标签 $\hat y_{\tilde x}$，剩余成员再提交 $(g(x),\hat y_{g(x)})$。$n_e$ 太小会选错标签，太大会削弱后续认证样本量。
3. **Signal erasing**：目标是使 $\hat f(g(x))=\hat f(x)$，即让被 $g$ 消去的特征不再影响预测。该结论需要 $g$ 幂等以及每个变换特征存在有间隔的众数标签；官方代码没有实现这一部分。

### 实验结论

作者使用四分类的合成车辆评价数据。下界始终比真实成功率保守：planting 通常要到约 10% 的集体占比才被显著认证，但实际低于 5% 就可能成功；adaptive unplanting 的认证阈值约 10%，实际约 3%。保持 $n/N$ 不变时，$N$ 越大、绝对集体规模越大，估计越准，说明大型平台未必因规模而更安全。有限离散特征会逐个越过阈值，因此曲线呈阶梯状。

### 适用边界

结论依赖有限特征与标签、用户独立同分布、分类问题、已知 $N$、成员可共享数据并协调策略，以及可解释的 $\varepsilon$。实验只有合成表格数据；真实异质人群、连续特征、回归和真实平台防御均未验证。官方代码与 planting/unplanting 实验匹配较好，但没有锁定依赖、数据需本地生成，signal erasing 实现为 **Not found**。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Statistical Collusion by Collectives on Learning Platforms

### Paper summary

This ICML 2025 paper studies how a coordinated group can change submitted training data to influence a learning platform while using only pooled local observations and the platform's total sample size. Earlier population-level collective-action theory proposed signal-planting/erasing strategies but left important quantities unknown to a real collective and did not give finite-sample, pre-action certificates. The paper turns that theory into a statistical framework that lets a collective both estimate a strategy and compute a high-probability lower bound on its eventual test-time influence.

The framework covers three goals: plant an association between transformed features and a target label; unplant an existing target association by learning the best alternative label per transformed feature; and erase a signal by encouraging predictions to be invariant to the transformation. Empirical feature masses and label gaps are combined with Hoeffding uncertainty and a total-variation $\varepsilon$-suboptimality model of the platform. In finite discrete spaces, features break one by one as the collective grows, yielding interpretable staircase success bounds. In the infinite-data limit, the results recover and tighten the corresponding Hardt et al. (NeurIPS 2023) bounds.

### Evaluation

Synthetic categorical vehicle data test signal planting and adaptive unplanting. Certified bounds stay below observed frequency-classifier success, but are conservative: influential planting is generally certified near a 10% collective share while observed success often occurs below 5%; adaptive unplanting is certified around 10% while observed success occurs near 3%. At fixed $n/N$, increasing $N$ from 500,000 to 2,000,000 improves the bound because the absolute collective supplies better estimates. The adaptive unplanting strategy also beats or matches naive fixed-label alternatives.

### Reproducibility and limitations

The official repository (commit `722bfe4beef1847c6351fba9765b1e24a1c769fe`) implements planting and unplanting bounds and includes experiment/plot notebooks plus saved arrays. Fidelity is medium-high for those experiments, but the synthetic CSV must be generated, dependencies are not pinned, and signal erasing code is **Not found**. The theory assumes finite features/labels, i.i.d. participants, classification, known $N$, coordinated data sharing, and a meaningful $\varepsilon$ bound; one synthetic domain does not establish real-platform effectiveness or safety.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
