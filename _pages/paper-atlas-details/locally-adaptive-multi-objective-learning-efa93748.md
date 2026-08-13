---
layout: default
permalink: /paper-atlas/locally-adaptive-multi-objective-learning-efa93748/
title: "Locally_Adaptive_Multi_Objective_Learning"
nav: false
description: "这篇论文不是通过增加更多“时间区间目标”来适应漂移，而是让同一组目标的权重持续保有恢复能力：minimax 负责每一步同时兼顾当前最难目标，Fixed Share 负责在分布变化后快速重新发现变坏的目标。"
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
      <span>Machine Learning Algorithm</span>
      <span>arXiv · 2026</span>
    </div>
    <h1>Locally_Adaptive_Multi_Objective_Learning</h1>
    <p>Locally Adaptive Multi-Objective Learning</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2602.14952" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Locally_Adaptive_Multi_Objective_Learning">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/jivatneet/adaptive-multiobjective" target="_blank" rel="noopener noreferrer" aria-label="Open code for Locally_Adaptive_Multi_Objective_Learning">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 局部自适应多目标学习：方法解读

### 这篇论文解决什么问题？

这不是生物信息学文章，而是一篇在线学习、分布漂移与算法公平性方向的方法论文。系统每次先看到特征 $x_t$、给出预测 $p_t(x_t)$，随后才看到真实结果 $y_t$。它希望同一个预测器同时满足多项目标，例如：

- 不同亚群上的平均残差接近零（multiaccuracy）；
- 相比已有基准预测 $\tilde p_t$ 不损失预测精度；
- 还可以把覆盖率、校准、群组遗憾等写成目标。

难点在于数据分布会改变。若只检查整个时间段，前半段的正偏差和后半段的负偏差可能相互抵消，看起来“总体无偏”，但当前预测已经严重失效。论文因此要求目标在局部连续时间窗内也保持较小（正文 `paper.md:183-196`）。

### 现有方法为什么不够？

Lee 等人在 NeurIPS 2022 的在线 minimax 多目标框架中，用 Hedge 学习各目标的权重。它优化的是整个时间范围的最坏目标，不能快速响应突变。其局部扩展方式是为“每个目标 × 每个时间区间”额外建立目标：理论覆盖范围强，但目标数、内存和计算量膨胀，而且此前缺少系统实验（`paper.md:202-212`）。

本文的关键选择是：**目标集合保持不变，只把目标权重学习器从 Hedge 换成局部自适应的 Fixed Share。**

### 方法主线

```text
固定目标集合 L，选择目标窗口宽度 τ
             ↓
根据当前权重 q^(t) 找到“最需要纠正”的目标混合
             ↓
求解 min_P max_y 的单步稳健预测，得到 p_t
             ↓
观察 y_t，计算每个目标的当前损失
             ↓
指数加权：提高当前被违反目标的权重
             ↓
Fixed Share：给所有目标重新注入少量均匀权重
             ↓
用最近 τ 步的平方损失更新 η_t，进入下一轮
```

#### 第一步：把需求写成目标

以 multiaccuracy 为例，对每个亚群函数 $f\in\mathcal F_{\mathrm{MA}}$ 同时放入正负两个目标：

$$
\ell_{\mathrm{MA}_{f,\sigma}}^{(t)}
=\sigma f(x_t)(y_t-p_t(x_t)),\qquad \sigma\in\{\pm1\}.
$$

正负成对后，取所有目标的最大值就等价于约束残差的绝对偏差。为了不把“公平纠偏”做成完全不准确的预测，再加入

$$
\ell_{\mathrm{pred}}^{(t)}
=c(p_t(x_t),y_t)-c(\tilde p_t(x_t),y_t),
$$

即校正预测相对基准预测的额外损失（`paper.md:289-314`）。

#### 第二步：每轮做 minimax 预测

目标权重 $q^{(t)}$ 表示当前各目标的重要程度。预测器求解

$$
P_t(x_t)=\arg\min_{P\in\Delta(\mathcal Y)}\max_{y\in\mathcal Y}
\mathbb E_{p\sim P}\left[\sum_{\ell}q_\ell^{(t)}\ell(p,x_t,y)\right].
$$

直观上，先假设结果 $y$ 会以最不利方式出现，再选能让加权目标最小的预测。均值预测的目标是凸的，因此通常可用确定性解。代码在 `core/algorithms.py:53-119` 用 CVXPY 同时约束二元结果 $y=0,1$ 的损失上界。

#### 第三步：Fixed Share 让旧目标重新“活过来”

普通 Hedge 的指数更新为

$$
\widehat q_{\ell}^{(t+1)}\propto q_\ell^{(t)}e^{\eta_t\ell^{(t)}}.
$$

如果某个目标长期没有问题，它的权重可能接近零；分布突然改变后，即便它重新恶化，也很难快速恢复。Fixed Share 在更新后增加均匀混合：

$$
q_{\ell}^{(t+1)}=(1-\gamma)\widehat q_{\ell}^{(t+1)}+\frac{\gamma}{|\mathcal L|}.
$$

这相当于始终保留一小部分“重新关注任何目标”的能力。代码在 `core/algorithms.py:391-394` 直接实现了该操作。

#### 第四步：窗口宽度与学习率

给定目标窗口宽度 $\tau$，论文取 $\gamma=1/(2\tau)$，并根据最近 $\tau$ 步的加权平方损失更新

$$
\eta_t=\sqrt{
\frac{\log(|\mathcal L|\,2\tau)+1}
{\sum_{s=t-\tau+1}^{t}q^{(s)\top}(\ell_{\mathcal L}^{(s)})^2}}.
$$

较小的 $\tau$ 响应更快，但理论误差界更松；较大的 $\tau$ 更稳定，但可能更慢地发现突变。实现用固定长度队列维护分母（`core/algorithms.py:403-416`）。

### 理论结论

对长度为 $\tau$ 的区间，最坏目标的平均误差可达到

$$
O\!\left(\sqrt{\frac{\log(|\mathcal L|\tau)}{\tau}}\right).
$$

这个结论来自两部分：Fixed Share 把任一区间上的最坏目标与加权目标联系起来；minimax 响应保证加权目标和不为正（`paper.md:218-269`）。它保证的是用户明确写入 $\mathcal L$ 的目标，不会自动保证没有写入的公平性或效用概念。

### 为什么预测精度目标很重要？

如果只保留 multiaccuracy 目标，最优 minimax 解可能只输出区间端点 $a$ 或 $b$。这虽能迅速纠正残差，却可能破坏概率解释和预测质量。论文推导了这一退化，代码中的 MA-only 类也确实按加权压力符号选择 0/1（`core/algorithms.py:209-212`）。加入基准相对损失后，`OnlineMAPred` 联合求解偏差与预测精度的折中，能够得到内部概率值。

### 实验如何验证？

- **GEFCom2014-L**：预测电力负荷是否超过 150MW，以温度/时间组检查局部 multiaccuracy，$\tau=336$ 小时。
- **COMPAS**：按时间排序的再犯预测，以种族、年龄、性别亚群检查局部偏差，$\tau=50$ 天。
- **合成漂移**：在线性模型系数中加入不同幅度的跳变。

图 3–8 显示：局部自适应 MA+prediction 在所测窗口中通常取得最低的局部或总 MA 误差，同时保持相对基准预测的精度；只做 MA 虽可能略降偏差，却明显增加预测损失。图 11–14 的消融说明 Fixed Share、局部学习率以及窗口选择都影响结果；图 16 显示漂移越剧烈，本方法相对优势越明显。这些是特定数据和设置上的经验结果，不应外推为对所有漂移的普遍优越性。

### 代码对应关系与复现边界

- `core/algorithms.py`：minimax、MA/MA+prediction、Fixed Share 和 MC 对照算法；
- `core/utils.py`：滑动窗口局部误差；
- `load/load_utils.py`：把分位数预测线性插值成 CDF；
- `load/`、`compas/`、`synthetic/` 的 notebook：三组实验和消融。

官方仓库快照与论文实验算法的匹配度高，但没有独立测试套件或一键命令行复现实验。分位数预测、omniprediction、multi-group learning 等扩展主要停留在理论框架或表格层面，不能把它们描述成已被完整代码验证。

### 一句话理解

这篇论文不是通过增加更多“时间区间目标”来适应漂移，而是让同一组目标的权重持续保有恢复能力：**minimax 负责每一步同时兼顾当前最难目标，Fixed Share 负责在分布变化后快速重新发现变坏的目标。**

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Locally Adaptive Multi-Objective Learning

### Paper at a glance

This 2026 arXiv method paper by Jivat Neet Kaur, Isaac Gibbs, and Michael I. Jordan studies online prediction under arbitrary distribution shift. It asks how one predictor can keep several criteria—such as subgroup unbiasedness and predictive accuracy—small not merely over the complete history, but on recent or otherwise local contiguous intervals. The work belongs to online machine learning, adaptive forecasting, and calibration/fairness; it is not bioinformatics.

### Why previous approaches are insufficient

The online minimax multi-objective framework of Lee et al. (NeurIPS 2022) uses Hedge to weight objectives and provides a whole-horizon bound. Large positive and negative errors can cancel across regimes, so a globally acceptable predictor may be badly biased after a shift. The earlier adaptive construction copies every objective onto every interval, which expands the objective set, raises memory/runtime, and had little empirical validation (`paper.md:183-212`).

### Proposed method

The paper keeps the objectives fixed and replaces Hedge with a locally adaptive weight learner—concretely, Fixed Share. Each round:

1. objective weights identify the currently difficult criteria;
2. the predictor solves a worst-case-label minimax problem for their weighted mixture;
3. after observing the label, exponential weights emphasize violated objectives;
4. a uniform share prevents any objective's weight from vanishing;
5. a trailing-window estimate adapts the learning rate to recent squared losses.

For target window width $\tau$, $\gamma=1/(2\tau)$ and the local average worst-objective error scales as $O(\big(\log(|\mathcal L|\tau)/\tau\big)^{1/2})$ (`paper.md:256-280`). In the main mean-estimation instance, signed subgroup residual objectives enforce multiaccuracy while an excess-loss objective protects accuracy relative to a baseline forecast. That second objective is essential: without it, the minimax correction can produce only extreme predictions (`paper.md:289-314`).

### Evaluation and findings

The experiments cover GEFCom2014-L electricity-demand forecasting, temporally ordered COMPAS recidivism prediction, and controlled linear-model jump shifts. Comparisons include raw forecasts, multiaccuracy, multiaccuracy plus predictive loss, and online multicalibration, using non-adaptive, locally adaptive, and interval-expanded adaptive-objective variants (`paper.md:341-389`).

On GEFCom, the locally adaptive MA variants show near-zero plotted local multiaccuracy error while non-adaptive curves fluctuate; MA+prediction preserves or improves baseline-relative predictive loss. On COMPAS, local MA+prediction has substantially smaller subgroup-local error than non-adaptive and multicalibration variants, whereas removing the prediction objective improves MA slightly but markedly worsens predictive error. Across window widths and increasingly abrupt simulated shifts, locally adaptive MA+prediction consistently has the lowest plotted MA error among the evaluated methods (`paper.md:392-428`, `658-693`). These results are empirical for the studied objectives and datasets, not a universal dominance theorem.

### Code and reproducibility

The paper explicitly releases `https://github.com/jivatneet/adaptive-multiobjective`; this workspace preserves commit `ed815f1ad8a2e081bc80346179a34fd8a52560b1`. Direct inspection finds high fidelity for the empirical core: CVXPY minimax prediction, signed MA and baseline-loss objectives, Fixed-Share mixing, adaptive $\eta_t$, local metrics, and comparison algorithms are implemented in `core/algorithms.py` and `core/utils.py`. The GEFCom, COMPAS, and synthetic workflows are supplied as notebooks.

**Reproducibility rating: 4/5.** Strengths are an official MIT-licensed repository, environment file, readable reusable core, and notebooks for all experiment families. Limits are the lack of automated tests and a one-command runner, notebook-centric orchestration, and no dedicated implementation found for the paper's generic quantile/omniprediction extensions. The theorem proofs remain paper evidence rather than executable verification.

### Key limitations

- One run is tuned to a chosen local width $\tau$; responsiveness and statistical rate trade off.
- Objectives must form a finite, mutually compatible collection under the paper's assumption.
- Real-data evidence covers two applications, with no uncertainty intervals or formal significance testing in the plots.
- Broader applications in Table 1 are framework extensions, not all experimentally demonstrated or fully implemented.
- Canonical metadata differs from the task's provisional author string: the primary arXiv source lists Kaur, Gibbs, and Jordan, not A. Alaa.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
