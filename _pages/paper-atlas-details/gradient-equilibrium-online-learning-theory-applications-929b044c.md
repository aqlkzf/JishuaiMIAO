---
layout: default
permalink: /paper-atlas/gradient-equilibrium-online-learning-theory-applications-929b044c/
title: "Gradient_Equilibrium_Online_Learning_Theory_Applications"
nav: false
description: "传统在线学习通常问“累计损失相对最佳固定决策是否具有次线性遗憾”。这篇论文提出另一条轴线：沿实际更新轨迹观察到的梯度，长期平均后能否相互抵消？作者称之为梯度均衡（gradient equilibrium, GEQ）： GEQ 与无遗憾并不互相蕴含。它关注的是一阶平衡条件，而不是累计损失最优性，因此特别适合把“无偏”“覆盖率正确”“分组残差为零”等统计目标写成在线算法的直接保证。"
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
      <span>Journal of Machine Learning Research 26(305):1-68 · 2025</span>
    </div>
    <h1>Gradient_Equilibrium_Online_Learning_Theory_Applications</h1>
    <p>Gradient Equilibrium in Online Learning: Theory and Applications</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 梯度均衡：把在线更新变成可解释的长期统计保证

### 论文解决什么问题？

传统在线学习通常问“累计损失相对最佳固定决策是否具有次线性遗憾”。这篇论文提出另一条轴线：沿实际更新轨迹观察到的梯度，长期平均后能否相互抵消？作者称之为**梯度均衡（gradient equilibrium, GEQ）**：

$$
\left\|\frac1T\sum_{t=1}^T g_t(\theta_t)\right\|_2\to0.
$$

GEQ 与无遗憾并不互相蕴含。它关注的是一阶平衡条件，而不是累计损失最优性，因此特别适合把“无偏”“覆盖率正确”“分组残差为零”等统计目标写成在线算法的直接保证。

### 为什么普通梯度下降就能做到？

使用固定步长的在线梯度下降：

$$
\theta_{t+1}=\theta_t-\eta g_t(\theta_t).
$$

把前 `T` 次更新相加，所有中间项会望远镜消去：

$$
\frac1T\sum_{t=1}^Tg_t(\theta_t)=\frac{\theta_1-\theta_{T+1}}{\eta T}.
$$

所以关键不是每一步梯度都趋近于零，而是参数增长慢于线性，即 `||theta_t||=o(t)`。若参数始终有界，平均梯度甚至按 `O(1/T)` 消失。论文进一步用“恢复性梯度场”描述一种向内拉回的更新结构，并把理论扩展到正则化、变步长、投影梯度与镜像下降。

### 实际使用流程

```text
黑箱预测 f_t、当前特征/组别 z_t
              ↓
观察真实结果 y_t
              ↓
选择梯度恰好等于目标误差的损失
              ↓
更新低维修正量 theta_{t+1}=theta_t-eta_t g_t
              ↓
输出下一步修正预测/分位数/组合权重/Elo 分数
              ↓
累计平均梯度对应长期偏差或覆盖缺口
```

这是一种后处理方案：不必重训黑箱模型，只在线更新一个截距、分组系数、分位数偏移或评分向量。

### 四类代表性应用

1. **回归去偏**：输出 `f_t+theta_t`，平方损失梯度就是预测残差，因此 GEQ 意味着长期平均预测等于长期平均观测。
2. **多组去偏**：用组指示向量 `z_t` 和修正 `z_t^T theta_t`，使出现频率足够高的每个群体都获得组内残差平衡。
3. **分位数追踪与集成**：分位数损失的次梯度是覆盖指示误差；多个不同学习率的追踪器再用指数梯度学习单纯形权重，以兼顾适应速度和分位数损失。
4. **Elo/两两偏好**：把参赛者编码成 `-1/+1` 特征，逻辑损失的在线 GD 就得到 Elo 风格更新；GEQ 转化为每个高频模型的预测胜率与实际胜率长期一致。

### 实验说明了什么？

论文使用合成序列、COMPAS、MIMIC 住院时长、HelpSteer2 奖励与 Chatbot Arena。图像证据显示：固定大步长通常更快消除偏差，但轨迹更抖；衰减步长更平滑但均衡更慢。分位数组合能较快缩小覆盖缺口并保持接近最佳单个追踪器的损失。Elo 实验也呈现相同的速度—损失权衡；L1 正则使评分更平滑，却留下小的非零偏差。

### 如何理解边界？

GEQ 只保证“梯度平均后为零”，不保证每一步梯度小、参数收敛或累计损失最优。大步长可能以剧烈振荡的方式取得均衡。正则化会改变均衡方程，而分位数组合的严格集成覆盖定理仍是开放问题。

官方代码实现了 GD、指数梯度、去偏模型、分位数追踪及各应用 notebook；但没有自动测试或统一复现入口。MIMIC 需要受限数据，HelpSteer 部分步骤需要外部模型与算力，本次未做完整数值复现。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### What the paper contributes

This JMLR 2025 method paper introduces **gradient equilibrium (GEQ)** as an online-learning target: the average gradient evaluated along the learner's actual iterates converges to zero. It is not a reformulation of no regret—neither property implies the other in general. Its main theoretical insight is that constant-step online GD telescopes, making GEQ equivalent to sublinear iterate growth; restorative gradient fields, regularization, and mirror/projected variants provide conditions that control that growth.

GEQ turns an optimization statement into useful sequential statistical guarantees. Squared loss gives long-run unbiased predictions, quantile loss gives one-sided coverage, GLM losses give residual–feature balance, and logistic pairwise updates give unbiased Elo win-rate predictions per frequently observed player. These guarantees require no distributional or stationarity assumption.

### Evidence and applications

Experiments cover synthetic regret/GEQ examples, COMPAS, MIMIC length of stay, HelpSteer2 rewards, and Chatbot Arena. Figures show that larger constant steps usually erase bias faster, while decaying steps smooth predictions at the cost of slower equilibrium. Quantile ensembling combines several trackers and approaches target coverage while retaining near-best quantile loss. Elo updates reduce global and per-model bias, with an observable loss/speed trade-off.

### Reproducibility

The JMLR page links the official `aangelopoulos/gradient-equilibrium` repository, pinned here at `be4d434b09bb1d199f85f8db10ebcbbf4b179838`. The code closely matches the algorithms: reusable GD/ExpGD and correction models sit in `core/algorithms.py`, while application notebooks implement the reported studies. Reproducibility is **3.5/5**: code and notebooks are public and method-aligned, but there is no test suite or unified runner; MIMIC requires external access, some HelpSteer steps need substantial model assets/compute, and this analysis did not execute the full experiments.

### Scope and limitations

GEQ controls the norm of the average gradient, not average loss, individual gradient norms, or iterate volatility. Large constant steps can satisfy GEQ while producing unstable paths. Regularization can stabilize updates but changes the equilibrium target and can leave residual bias. The quantile ensemble's empirical success is shown, but its ensemble-level coverage guarantee is left for future work.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
