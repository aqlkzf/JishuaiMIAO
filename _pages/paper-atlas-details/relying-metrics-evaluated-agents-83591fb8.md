---
layout: default
permalink: /paper-atlas/relying-metrics-evaluated-agents-83591fb8/
title: "Relying_Metrics_Evaluated_Agents"
nav: false
description: "平台或监管者可能有很强的数据收集能力，却不知道“应该收集哪个变量”。真正执行任务的被评估者反而知道一个与成本相关的指标 X。论文研究的不是“看到 X 的取值后是否报告”，而是被评估者在取值实现之前，是否告诉委托人这个变量存在且可观测。 代理人付出二元努力，成本为 C；完成任务后委托人获得价值 b。如果隐藏 X，委托人只能给统一报酬 p： 如果公开 X，委托人可按 x 设置报酬 \\rho(x)，并使用条件成本分布 Fx 优化每一类的价格。"
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
      <span>Proceedings of the ACM on Web Conference 2025 · 2025</span>
    </div>
    <h1>Relying_Metrics_Evaluated_Agents</h1>
    <p>Relying on the Metrics of Evaluated Agents</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1145/3696410.3714864" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法详解：被评估者为什么愿意公开、隐藏或模糊一个指标？

### 核心问题

平台或监管者可能有很强的数据收集能力，却不知道“应该收集哪个变量”。真正执行任务的被评估者反而知道一个与成本相关的指标 $X$。论文研究的不是“看到 $X$ 的取值后是否报告”，而是被评估者在取值实现之前，是否告诉委托人这个变量存在且可观测。

### 基本委托代理博弈

代理人付出二元努力，成本为 $C$；完成任务后委托人获得价值 $b$。如果隐藏 $X$，委托人只能给统一报酬 $p$：

$$
\Pi_{\mathrm{con}}(p)=F(p)(b-p),\qquad
V_{\mathrm{con}}(p)=\mathbb E[(p-C)\mathbf 1\{C<p\}].
$$

如果公开 $X$，委托人可按 $x$ 设置报酬 $\rho(x)$，并使用条件成本分布 $F_x$ 优化每一类的价格。代理人比较公开后的效用 $V_{\mathrm{rev}}(\rho^*)$ 与隐藏后的效用 $V_{\mathrm{con}}(p^*)$。

公开信息同时产生两股相反力量：

- **租金抽取**：识别低成本、容易完成的任务后，委托人会降低这部分报酬；
- **项目扩张**：识别高成本、困难任务后，委托人可能提高报酬，让更多任务得以完成。

因此，能区分最低成本群体的阈值特征通常被隐藏；能区分最高成本群体的特征在一定 $b$ 区间内会被公开。这与三级价格歧视相似：隐藏时只有一个统一价格，公开后可以分组定价；不同的是，是否提供分组信息由“被定价者”决定。

### 部分公开：garbling

对二元指标，代理人可以先通过随机响应通道：

$$
Y=\begin{cases}
X,&\text{概率 }\varepsilon,\\
\xi,&\text{概率 }1-\varepsilon,
\end{cases}
$$

其中 $\xi$ 是与 $X$ 同边际分布但独立的随机变量。$\varepsilon=0$ 等于完全隐藏，$\varepsilon=1$ 等于完全公开。委托人看到 $Y$ 后重新优化报酬，代理人选择使自身效用最大的 $\varepsilon^*$。

中间的 $\varepsilon^*$ 可能优于两个端点：它保留足够的成本相关性，使困难状态得到较高报酬，同时加入足够噪声，避免委托人对容易状态过度压价。指数混合分布的例子同时展示了

$$V_{\mathrm{garb}}>V_{\mathrm{rev}}>V_{\mathrm{con}}$$

和

$$V_{\mathrm{garb}}>V_{\mathrm{con}}>V_{\mathrm{rev}}.$$

第二种情况尤其重要：若不允许模糊，代理人会完全隐藏；允许部分公开后，代理人与委托人都改善，形成严格 Pareto 改善。该通道也满足局部差分隐私量级的保证，但论文没有把“隐私偏好”直接写入效用；隐私的经济价值来自合同本身。

### 福利结论

转移支付在总福利中相互抵消，公开信息影响福利的关键是完成任务数量。委托人不会因拥有更多可用信息而变差；代理人最优的 garbling 相比完全隐藏弱提高总福利。不过社会福利最优通常希望公开的信息不少于代理人自己选择的程度，所以三方偏好并不完全一致。

### 实证示例

论文使用 2018 年波士顿一周的公开 Uber/Lyft 抓取数据。第一种情景把 Lyft 价格当作代理人的成本替代变量，把距离当作新指标；通过 KDE 估计条件成本分布，然后比较连续距离、阈值化距离及其最优 garbling 的效用。图中低阈值偏向隐藏，高阈值偏向公开，中间部分阈值偏向模糊。第二种情景用 OLS 近似已有 Uber 定价模型，再研究 Lyft surge multiplier。

### 适用边界

- 努力是二元且成功是确定的；不包含多级努力与随机成功。
- 双方风险中性，委托人可承诺最优合同。
- 指标公开后可验证，代理人不能撒谎或按实现值选择性隐瞒。
- 多个定理依赖可微分、单调逆危险率、价格弹性、严格凹性或 MLRP 等条件。
- 出行平台实验是机制示例，不是对真实 Uber/Lyft 定价的因果或结构估计。
- 未找到官方代码、固定数据快照、随机种子或完整预处理脚本，因此只能依据论文公式重建。

### 标题说明

当前 arXiv v3 与 ACM 正式发表标题均为 *Relying on the Metrics of Evaluated Agents*。*Information Elicitation in Agency Games* 是 arXiv 源码中保留的 EC/FORC 2024 旧稿标题。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Relying on the Metrics of Evaluated Agents

### Paper summary

Online platforms and regulators often evaluate agents with metrics, yet the evaluated agents may know relevant variables that the evaluator does not even know exist. This paper models that asymmetry as an agency game: a cost-bearing agent decides, before a metric is realized, whether to reveal its observability to a principal that can then verify the metric and condition payments on it.

The central finding is that an agent’s disclosure incentive is governed by a tradeoff between **rent extraction** and **project expansion**. A metric that separates low-cost/easy tasks lets the principal reduce payments and tends to be concealed; a metric that separates high-cost/difficult tasks can induce higher payments and more completed tasks and can be revealed. The analysis makes the connection to third-degree price discrimination explicit: revelation replaces one pooled transfer with group-specific transfers, but the information holder here is the party being priced.

The paper then expands the agent’s action from reveal/conceal to a binary randomized-response channel. An interior garbling level can preserve enough information to expand trade while limiting the principal’s ability to extract rents. For some cost distributions, partial revelation gives the agent more utility than either endpoint; when the agent otherwise prefers concealment, this creates a strict Pareto improvement because the principal also benefits from useful information. Agent-optimal garbling weakly improves total welfare over concealment, although the welfare optimum generally favors at least as much information as the agent does.

The theory is illustrated with a public Uber/Lyft dataset. Distance is used as a cost-correlated feature in a hypothetical platform-switching contract. The estimated utility curves reproduce the qualitative theory: low thresholds are hidden, high thresholds are revealed, and some intermediate thresholds are optimally garbled. These are illustrative calculations, not a causal or structural description of the companies.

### Publication and title history

- Archival title: *Relying on the Metrics of Evaluated Agents*.
- Venue: *Proceedings of the ACM on Web Conference 2025*, pages 1468–1487.
- DOI: `10.1145/3696410.3714864`.
- arXiv: `2402.14005v3`, which also uses the archival title.
- *Information Elicitation in Agency Games* is the earlier EC/FORC 2024 draft title retained in the arXiv source archive, not the current arXiv title.

### Reproducibility and limitations

No official code repository was found in the paper, title/arXiv GitHub searches, or searched author-publication surfaces, so this workspace is `paper-only`. The full arXiv paper and appendices specify the objectives, distributional assumptions, KDE/OLS illustration, and sensitivity plots, but exact scripts, seeds, preprocessing pipeline, and a frozen dataset snapshot are Not found. Other limitations include binary effort, deterministic task completion, risk neutrality, verifiable nonselective disclosure, strong distributional regularity for several results, and a short 2018 rideshare scrape with proxy costs.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
