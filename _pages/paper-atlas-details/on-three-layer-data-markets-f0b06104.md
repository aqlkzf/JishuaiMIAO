---
layout: default
permalink: /paper-atlas/on-three-layer-data-markets-f0b06104/
title: "On_Three_Layer_Data_Markets"
nav: false
wide: true
description: "这是一篇数据市场、信息经济学和博弈论论文。它研究三层市场：用户拥有数据并需要平台服务；多个平台获得用户信号，选择是否进入市场、以多大噪声向外出售；第三方数据买家支付价格购买信号。核心问题是：竞争是否真的保护用户，以及禁止数据共享、统一隐私门槛和差异化监管中哪一种更有利于用户。 用户特征为 \\bm\\theta\\sim\\mathcal N(0,Id)。"
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
      <span>Quantitative Economics (to appear) · 2026</span>
    </div>
    <h1>On_Three_Layer_Data_Markets</h1>
    <p>On Three-Layer Data Markets</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2402.09697" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for On_Three_Layer_Data_Markets">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 《On Three-Layer Data Markets》方法详解

### 这篇论文研究什么？

这是一篇数据市场、信息经济学和博弈论论文。它研究三层市场：用户拥有数据并需要平台服务；多个平台获得用户信号，选择是否进入市场、以多大噪声向外出售；第三方数据买家支付价格购买信号。核心问题是：竞争是否真的保护用户，以及禁止数据共享、统一隐私门槛和差异化监管中哪一种更有利于用户。

### 模型中的三类参与者

用户特征为 $\bm\theta\sim\mathcal N(0,I_d)$。平台 $i$ 在用户加入后观察

$$
s_i=\bm x_i^\top\bm\theta+\mathcal N(0,1),
$$

并可向买家出售进一步加噪的信号

$$
\tilde s_i=s_i+\mathcal N(0,\sigma_i^2).
$$

$\sigma_i$ 越大，买家得到的信息越少，隐私越强。买家希望估计 $\bm y^\top\bm\theta$。论文用后验均方误差相对先验均方误差的下降量定义“揭示信息” $\mathcal I$。在平台信号互为替代品的假设下，

$$
\mathcal I(\bm\sigma_S)=\mathbf m^\top M^{-1}\mathbf m,
$$

其中 $m_i=\gamma_i=\bm x_i^\top\bm y$，$M_{ii}=2+\sigma_i^2$，$M_{ij}=\gamma_i\gamma_j$。它对卖出数据的平台集合单调增加，对噪声单调下降，并具有次模性：买家已有的数据越多，新增一家平台数据的边际价值越小。

### 效用函数

用户得到服务收益，但承担向买家泄露信息的隐私损失：

$$
\mathcal U_{\rm user}=\sum_i a_i e_i\mathcal I_i-\alpha\mathcal I.
$$

平台在进入后得到服务收益和售数收入，并支付成本：

$$
\mathcal U_i=a_i\mathcal I_i+b_ip_i-c_i.
$$

买家的收益是信息价值减去总支付：

$$
\mathcal U_{\rm buyer}=\beta\mathcal I-\sum_i b_ip_i.
$$

$\alpha$ 表示用户对隐私的重视程度，$\beta$ 表示买家对数据的估值，$c_i$ 是平台服务成本。

### 如何求解四阶段博弈

```text
平台选择进入 e 和噪声 sigma
          ↓
用户选择加入哪些平台 a
          ↓
平台向数据买家报价 p
          ↓
买家选择购买哪些信号 b
          ↓
逆向归纳得到子博弈精炼均衡
```

从最后一阶段倒推，平台 $i$ 的均衡价格恰好等于它对买家信息量的边际贡献：

$$
p_i^*=\beta[\mathcal I(\text{全部数据})-\mathcal I(\text{去掉平台 }i)].
$$

买家在均衡中购买全部可用信号。由于次模性，其他平台越多，单个平台的边际信息价值和价格越低。用户的最优加入集合构成子格；论文采用对平台有利的并列破除规则。平台若已经进入，就会把噪声调到足以让用户加入、又尽可能提高售数收益的位置。

### 两个平台时的关键几何结构

在 $(\sigma_1^2,\sigma_2^2)$ 平面中，用户可能加入两个平台、只加入一个或一个也不加入。均衡候选点位于“加入全部”和“一个也不加入”的边界，否则某个平台可以略微降低噪声、维持用户加入并提高售价。对于足够大的 $\alpha$，关键边界点满足

$$
\frac{2+\sigma_1^2}{\gamma_1^2}=\frac{2+\sigma_2^2}{\gamma_2^2}=2\alpha-1.
$$

买家估值 $\beta$ 很低时可能没有平台进入；中间区域仅低成本平台进入；足够高时两个平台都进入。

### 一般 $K$ 个平台的结论

平台直接服务价值被归一化为 $1/2$，所以 $c_i<1/2$ 称为低成本平台，$c_i>1/2$ 称为高成本平台。

- 当 $\beta$ 足够高时，所有平台进入，用户与全部平台共享，买家购买全部数据；用户效用为零，而买家效用为正。
- 当 $\beta$ 足够低时，只有低成本平台进入；用户效用仍为零。
- 竞争降低单个平台的数据边际价格，因此主要改善买家而非用户的处境。
- 在论文刻画的区间内，进入平台越多，总功利福利越高。

“用户效用为零”的机制是平台将噪声压到用户参与约束边界：只要用户还有严格正剩余，平台就可能降低一点噪声来提高售数收入。

### 为什么简单禁止售数不一定最好？

如果所有平台都是低成本平台，禁止售数后它们仍愿意提供服务，用户既保留服务收益又没有泄露，因此禁令最优。但在高、低成本平台并存时，禁令会使依赖数据收入的高成本平台退出，用户同时失去其服务。

当买家估值足够高时，有限的最低噪声门槛可以让高成本平台继续进入，并把隐私损失控制在较低水平，从而优于完全禁止。进一步，论文提出差异化方案：禁止低成本平台售数，同时允许高成本平台在满足最低噪声标准后售数。这利用了两类平台不同的进入约束。

### 需要谨慎理解的边界

这些结论来自理论模型，不是市场数据的因果估计。它们依赖高斯信号、信息替代性、加性服务收益、平台偏好的并列破除和纯策略均衡。部分中间参数区间可能没有纯策略均衡。“大型平台通常低成本”只是经济解释，不是论文实证识别的结果。

论文没有公开代码、模拟脚本或数据集；在 arXiv HTML、全文及代码可用性检索范围内均 **Not found**。因此可复现对象是定理推导、偏离条件和比较静态，而不是软件运行结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## On Three-Layer Data Markets — Summary

### Problem

The paper asks how privacy, platform entry, data pricing, and buyer purchasing interact when personal data moves through three economic layers: a user, competing service platforms, and a third-party data buyer. It is a theoretical information-economics and game-theory paper, not a bioinformatics study.

### Framework

The user exchanges noisy signals for platform services; platforms choose whether to enter and how much Gaussian noise to add before resale; the buyer pays for signals that improve estimation of a latent user attribute. Information value is measured by posterior MSE reduction. Under a substitution assumption, revealed information is monotone and submodular, which makes a platform's equilibrium price equal to its marginal contribution to the buyer's information.

The four-stage game is solved backward: platforms choose entry/noise, the user chooses memberships, platforms price, and the buyer purchases. For the main high-privacy-concern regimes, platforms push noise to the user's participation boundary, leaving zero user surplus. With high buyer valuation all platforms enter; with low valuation only platforms whose service value covers their cost enter.

### Main results

- Platform competition lowers marginal data prices and benefits the buyer, but does not necessarily improve user utility.
- Utilitarian welfare increases with the number of participating platforms in the characterized outer regimes.
- A complete data-sharing ban is user-optimal when all platforms are low-cost, but can drive high-cost platforms out in a mixed market.
- With sufficiently valuable data, a finite minimum-noise mandate preserves high-cost platform services and can beat a ban for users.
- A discriminatory mandate—ban low-cost platforms from resale while imposing a finite noise floor on high-cost ones—can further improve user utility.

### Evidence and limitations

The evidence consists of formal propositions, theorems, proofs, and geometric two-platform illustrations; there are no empirical datasets or benchmark comparisons. Conclusions rely on Gaussian signals, informational substitutability, additive service values, platform-favoring tie-breaking, and pure-strategy equilibria; intermediate parameter ranges may lack such equilibria. Firm cost is a model primitive, so the interpretation “large equals low-cost” is illustrative rather than identified from data.

### Reproducibility

Mode is `paper-only`. No official code, dataset, simulation scripts, or code-availability section was found in the arXiv HTML/Markdown search. All five paper figure panels were recovered and visually inspected. The latest verified archival identity is arXiv `2402.09697v4` (revised 18 November 2025), while Michael I. Jordan's publication page lists *Quantitative Economics*, “to appear”; a final journal DOI/issue was **Not found** in the checked Crossref/OpenAlex metadata.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
