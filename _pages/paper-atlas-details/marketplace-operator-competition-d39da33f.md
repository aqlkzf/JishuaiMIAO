---
layout: default
permalink: /paper-atlas/marketplace-operator-competition-d39da33f/
title: "Marketplace Operator Competition"
nav: false
description: "电商平台既可以向第三方卖家收取佣金，也可以用自营商品进入同一市场。论文研究一个反直觉问题：平台是否可以不靠限价或行政管制，而是通过自己报出低价并准备一定库存，迫使原本具有垄断地位的第三方卖家降价？这里的平台不仅关心当期利润，还关心顾客能否买到商品，因为一次满意交易可能提高复购和平台长期价值。"
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
      <span>arXiv preprint · 2025</span>
    </div>
    <h1>Marketplace Operator Competition</h1>
    <p>Marketplace Operators Can Induce Competitive Pricing</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2503.06582" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 市场平台如何通过库存承诺诱导竞争性定价

### 论文要解决什么问题？

电商平台既可以向第三方卖家收取佣金，也可以用自营商品进入同一市场。论文研究一个反直觉问题：平台是否可以不靠限价或行政管制，而是通过自己报出低价并准备一定库存，迫使原本具有垄断地位的第三方卖家降价？这里的平台不仅关心当期利润，还关心顾客能否买到商品，因为一次满意交易可能提高复购和平台长期价值。

Jordan 主页使用的题名 **The Role of the Marketplace Operator in Inducing Competition** 是 arXiv v1 题名；当前 v2 题名是 **Marketplace Operators Can Induce Competitive Pricing**。截至本次分析，它仍是 arXiv 预印本。

### 模型的核心结构

这是一个两阶段、同时选择价格和数量的 Stackelberg 博弈：

```text
平台 M 先承诺价格 p_M 和库存 q_M
              |
              v
第三方卖家 I 观察后选择价格 p_I 和库存 q_I
              |
              v
消费者先购买低价商品；剩余需求由配给规则决定
              |
              v
计算双方收益、消费者剩余和均衡
```

线性需求为 $Q(p)=\theta-p$。卖家每销售一件商品只能保留 $(1-\alpha)p$，所以盈亏平衡价是

$$p_0=\frac{c_{\mathtt{I}}}{1-\alpha},$$

其单独垄断市场时的最优价格是

$$p_{\mathtt{I}}^\star=\frac{p_0+\theta}{2}.$$

论文把 $p_{\mathtt{I}}<p_{\mathtt{I}}^\star$ 定义为“竞争性定价”。平台每促成一件商品销售还获得 $k$ 的顾客体验价值；它既可能从自营销售获利，也可能通过第三方销售获得 $\alpha p_{\mathtt{I}}$ 的佣金。

### 方法：先求卖家响应，再反推平台决策

#### 1. 卖家的库存可以消去

只要价格有正利润，卖家最优库存就等于该价格下的需求。少订会丢掉有利可图的订单，多订会为卖不出去的库存付成本。因此，卖家的二维价格—库存问题可化成一维定价问题：

$$u_{\mathtt{I}}=[(1-\alpha)p_{\mathtt{I}}-c_{\mathtt{I}}]D_{\mathtt{I}}.$$

#### 2. 库存使平台的低价威胁变得可信

在基准的强度配给（高估值顾客先买低价商品）下，高价卖家的剩余需求是

$$R(p_i)=Q(p_i)-q_j.$$

当平台价格位于 $[p_0,p_{\mathtt{I}}^\star)$ 时，平台必须至少准备阈值库存

$$q^\dagger(p_{\mathtt{M}})=\theta-p_0-2\sqrt{(p_{\mathtt{M}}-p_0)(\theta-p_{\mathtt{M}})}$$

才能让卖家觉得“等待高价卖剩余需求”不如直接匹配平台低价。于是卖家有三种响应：

- **竞争（compete）**：匹配/压低平台价格并拿走低价需求；
- **等待（wait）**：设置更高价格，销售平台库存满足后留下的需求；
- **退出（abstain）**：剩余需求不足以覆盖盈亏平衡价。

最重要的机制是：平台准备的 $q_{\mathtt{M}}$ 可能一件也卖不掉。相同价格时需求优先给第三方卖家，但库存承诺改变了卖家偏离到高价的收益，因此“未售库存”仍具有战略价值。

#### 3. 平台只需比较少数边界策略

给定 $p_{\mathtt{M}}$，平台不必在所有库存值上搜索。证明表明，只需比较 $0$、恰好诱导竞争的 $q^\dagger$、略低于阈值的 $q^\dagger-\epsilon$，或覆盖自身全部需求的 $Q(p_{\mathtt{M}})$ 等边界点。然后对每类策略做一维价格优化并比较收益，就得到平台的最优行动；卖家再采用前面的最优响应，二者组成子博弈精炼纳什均衡。

### 主要结论

- 平台成本相对较高、第三方成本较低时，平台往往不想亲自承担销售，却愿意用少量库存承诺诱导卖家以更低价格竞争。
- 平台成本很低或卖家成本很高时，平台更可能自己供货并迫使卖家退出。
- 佣金率 $\alpha$ 并非越高越好。提高佣金增加每笔第三方交易收入，同时提高卖家的盈亏平衡价和垄断价，甚至让卖家退出；最优佣金通常位于内部。
- 顾客体验权重 $k$ 越大，平台通常愿意准备更多库存，即使这些库存只用于压低第三方卖家的价格。
- 在强度配给、完全替代和卖家最优响应条件下，平台进入不会降低消费者剩余；当 $p_{\mathtt{M}}<p_{\mathtt{I}}^\star$ 时会严格提高。总福利非负提升来自论文图 12 的参数网格计算，不能扩展成所有模型下的普遍定理。

### 稳健性与边界

比例配给把剩余需求改为

$$R(p_i)=Q(p_i)\left(1-\frac{q_j}{Q(p_j)}\right).$$

总体的竞争/等待/退出结构仍存在，但等待的卖家会保持垄断价，不再因为平台库存而降价。对不完全替代商品，论文用 $\gamma q_j$ 替换 $q_j$；$\gamma$ 越小，竞争压力越弱、等待区域越大，但在一般正替代条件下仍可实现去垄断化。

这些结论依赖较强假设：只有一个第三方卖家、线性需求、连续库存、剩余库存价值为零、平台先行动、$k$ 是每笔交易的固定常数。多卖家竞争、非线性需求、正的库存残值、整数库存、内生行动顺序及其他配给规则下的福利仍未解决。

### 代码与复现状态

这是 `paper-only` 分析。论文和官方 LaTeX source 没有提供实现；作者主页及以新旧题名和 arXiv ID 进行的 GitHub 检索也未找到官方仓库。source 中只有 TikZ 与已经生成好的数值图，没有求解均衡或生成 $200\times200$ 网格的脚本。因此解析推导可以核查，但数值图无法从公开代码重新生成。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Marketplace Operators Can Induce Competitive Pricing

### Paper summary

This paper studies a hybrid marketplace in which the platform operator both collects a referral fee from an independent seller and may enter as a seller itself. The central question is not simply whether entry displaces the seller, but whether a credible low-price, positive-inventory commitment can discipline the seller's monopoly price. The authors model this as a two-stage price-quantity Stackelberg game: the marketplace operator commits first to price and inventory; after observing that commitment, the independent seller chooses its own price and inventory.

The key result is that operator inventory can be strategically valuable even when it remains unsold. Under the baseline intensity-rationing model, the independent seller has a closed-form, piecewise best response: it either matches/undercuts the operator and competes, prices above the operator and serves residual demand, or abstains. By carrying at least a threshold inventory while pricing between the seller's break-even and sole-seller prices, the operator can make low-price competition credible and induce a price below the seller's monopoly benchmark. Backward induction then reduces the operator's equilibrium problem to comparing a small set of boundary inventory strategies and at most three one-dimensional price optimizations.

The equilibrium need not always induce competition. When the operator's unit cost is high relative to the independent seller's, it may optimally carry a small strategic stock that pushes the seller to match a lower price; when the operator is cheaper, it may serve demand itself and induce seller abstention; a narrower intermediate region induces the seller to wait and serve residual demand. The referral fee also has an interior trade-off: a larger fee raises revenue per third-party sale but raises the seller's break-even and monopoly prices and can drive the seller from the market. A larger customer-experience weight generally makes the operator willing to carry more inventory, including inventory used only as a competitive threat.

### Consumer and welfare results

Under linear demand, perfect substitutes, intensity rationing, and seller best response, operator entry weakly increases consumer surplus relative to an independent-seller monopoly; the increase is strict when the operator prices below the seller's sole-seller price. Any lost independent-seller surplus is more than offset by increased consumer surplus. The paper's total-welfare comparison is weaker evidence: Figure 12 reports nonnegative welfare differences over a $200\times200$ parameter grid for each plotted $(\alpha,k)$ combination, but the paper does not state this grid observation as a general theorem for all rationing or substitution models.

The qualitative competition mechanism survives two extensions. Under proportional rationing, regime boundaries shift and a seller that waits retains its monopoly price rather than being de-monopolized. Under a one-directional imperfect-substitutes model, replacing rival inventory by $\gamma q$ weakens competitive pressure but still leaves parameter regions in which the operator de-monopolizes the seller.

### Evidence and limitations

The current record is arXiv `2503.06582v2` (revised 22 October 2025), titled **Marketplace Operators Can Induce Competitive Pricing**. Michael I. Jordan's 2025 publication list uses the original v1 title, **The Role of the Marketplace Operator in Inducing Competition**. Current arXiv metadata and author pages still classify it as a preprint; no archival venue was found.

The model is deliberately stylized: two sellers, sequential commitment, linear demand, continuous divisible inventory, zero salvage value, a fixed per-sale customer-experience benefit, and exogenous referral fee in the core game. The strongest consumer-surplus theorem depends on intensity rationing and perfect substitutes. Multiple independent sellers, nonlinear demand, inventory carryover/salvage, integer capacity, endogenous timing, and welfare under other rationing rules remain open. The submitted LaTeX source also retains editing/checklist machinery, so the clean compiled v2 PDF was used as the visual authority.

### Reproducibility

**Paper-only.** No official computational repository was found in the paper/source, on author publication pages, or through GitHub searches using both titles and the arXiv ID. The source archive contains TikZ and pre-rendered numerical plots but no scripts for computing best responses, solving equilibria, or regenerating the $200\times200$ grids. The analytic derivations are inspectable, but the numerical figures cannot be independently regenerated from released code.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
