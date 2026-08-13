---
layout: default
permalink: /paper-atlas/bayesian-coordinate-differential-privacy-c7280676/
title: "Bayesian_Coordinate_Differential_Privacy"
nav: false
wide: true
description: "局部差分隐私（LDP）通常对一整条高维记录使用同一个隐私预算。如果社会保障号需要很强保护，而普通偏好特征不需要同样强的保护，把最小预算用于所有维度会造成很大效用损失；但直接逐特征加噪又会忽略特征相关性，攻击者可能从弱保护特征反推出敏感特征。 BCDP 为每个坐标定义一个隐私参数 δi：在给定数据先验 π 时，观察机制输出以后，关于第 i 个特征的两种假设，其条件输出概率之比最多变化 e^{δi}。"
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
      <span>PMLR · 2025</span>
    </div>
    <h1>Bayesian_Coordinate_Differential_Privacy</h1>
    <p>Enhancing Feature-Specific Data Protection via Bayesian Coordinate Differential Privacy</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2410.18404" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Bayesian_Coordinate_Differential_Privacy">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/syomantak/BCDP-CodeBase" target="_blank" rel="noopener noreferrer" aria-label="Open code for Bayesian_Coordinate_Differential_Privacy">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Bayesian Coordinate Differential Privacy（BCDP）方法详解

### 解决什么问题

局部差分隐私（LDP）通常对一整条高维记录使用同一个隐私预算。如果社会保障号需要很强保护，而普通偏好特征不需要同样强的保护，把最小预算用于所有维度会造成很大效用损失；但直接逐特征加噪又会忽略特征相关性，攻击者可能从弱保护特征反推出敏感特征。

BCDP 为每个坐标定义一个隐私参数 `δ_i`：在给定数据先验 `π` 时，观察机制输出以后，关于第 `i` 个特征的两种假设，其条件输出概率之比最多变化 `e^{δ_i}`。因此 `δ_i` 越小，输出越难帮助攻击者区分该特征的不同事件。

BCDP 不是 LDP 的替代品。它只控制逐坐标推断，不能自动保护联合属性；普通组合甚至可能失效。论文建议同时要求全局 `ε`-LDP 和逐坐标 `δ`-BCDP。

### 关键桥梁：相关性如何进入隐私保证

论文用条件分布的总变差上界 `q_i` 衡量“知道第 `i` 个坐标后，其余坐标会变化多少”。若机制已经满足坐标 DP 参数 `c_i`，并且同时满足 `ε`-LDP，则可得到

$$
\delta'_i=\min\{c_i+\log(1+q_i e^\varepsilon-q_i),\varepsilon\}.
$$

`q_i=0` 时没有相关性附加代价；`q_i→1` 时，不同特征的隐私预算逐渐被最敏感特征约束。这正是该方法能够在弱相关条件下提升效用、在强相关条件下退化为保守 LDP 的原因。

### 均值估计流程

```text
输入：每个用户 x∈[-1,1]^d、δ、ε、相关性上界 q
  ↓
计算累计预算 c_0=0≤c_1≤…≤c_d≤ε
  ↓
第 k 次查询：只取后缀 (x_k,…,x_d)
              用预算 c_k-c_{k-1} 调用黑盒 LDP 均值机制
  ↓
第 i 个坐标从第 1,…,i 次查询中得到多个无偏估计
  ↓
按逆方差权重合并，再跨用户平均并投影
  → 私有经验均值
```

后面的、较不敏感的坐标参与更多次后缀查询，因此能使用更多有效信息。权重与 `(c_k-c_{k-1})²/(d-k+1)` 成正比。自由参数 `ζ` 用于在“保护最敏感坐标本身”和“支付其与其他坐标的相关性代价”之间分配预算。

### OLS 回归

最小二乘梯度 `zzᵀθ-lz` 对数据是二次的。把一个无偏噪声副本直接代入会产生有偏梯度。论文让每个用户用一半预算生成两个独立的 BCDP/LDP 私有副本，再用不同副本交叉构造乘积，得到无偏的二次目标，最后由服务器运行凸优化器。论文给出隐私与超额风险界，但没有 OLS 实验或代码。

### 实验与局限

合成 Bernoulli 实验表明：当相关性 `q` 较小时，BCDP 均值估计的中位 MSE 明显低于 `min δ`-LDP；`q→1` 时二者汇合。官方代码能对应这一均值实验，但没有 OLS、测试或环境锁文件。方法还依赖设计者知道可靠的 `q` 上界；如何私有估计 `q`、如何应对错误设定、如何安全组合多个 BCDP 发布，论文均未解决。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Enhancing Feature-Specific Data Protection via Bayesian Coordinate Differential Privacy

### Paper summary

This AISTATS 2025 paper introduces Bayesian Coordinate Differential Privacy (BCDP), a prior-aware way to quantify privacy separately for each feature of a locally released high-dimensional record. Uniform LDP must protect every feature at the most stringent requested level, while coordinate-wise mechanisms that ignore correlations can leak sensitive information through other features. BCDP bounds how much the release changes the odds of competing events about coordinate `i`, using a feature-specific parameter `δ_i`, and is intended to complement a simultaneous global `ε`-LDP guarantee.

The paper establishes an operational hypothesis-testing interpretation, relations to LDP/BDP/CDP, post-processing closure, and a counterexample showing that ordinary composition and global privacy do not follow from BCDP alone. A key conversion theorem says that coordinate-DP plus an upper bound on conditional cross-feature dependence (total variation `q_i`) yields explicit BCDP guarantees. This connection powers mechanisms for multivariate mean estimation and ordinary least-squares regression.

### Method

For mean estimation, the method converts desired `δ`, global budget `ε`, and dependence bound `q` into cumulative budgets `c_1≤⋯≤c_d`. It calls any suitable LDP mean channel on nested suffixes `(x_k,…,x_d)` with incremental budgets `c_k-c_{k-1}`, then combines every available estimate of coordinate `i` using inverse-variance weights. Less-sensitive coordinates can exploit larger effective budgets while sensitive coordinates retain their requested BCDP guarantee. For OLS, two independent half-budget private copies are cross-multiplied to form an unbiased estimate of the quadratic gradient/objective before server-side convex optimization.

### Evidence and results

Theorem 2 proves simultaneous `δ`-BCDP and `ε`-LDP and gives a finite-sample MSE bound. In the sensitive/less-sensitive two-block case, weak dependence allows the less-sensitive block to approach an `ε`-LDP rate; as correlation tends to one, the advantage collapses to conservative `min δ`-LDP. A synthetic Bernoulli experiment (`n=10000`, `d=10`, 1,000 trials) confirms this pattern: BCDP has lower median MSE for low/moderate `q` and converges to the baseline near `q=1`. The OLS result is theoretical only.

### Reproducibility and limitations

The official PMLR Software link provides three stand-alone Python scripts at commit `0914cd47902535fce5473f40dfa9424b164aa827`. The code closely implements the mean-estimation simulation and additional parameter sweeps, but contains no OLS implementation, tests, environment lockfile, or command-line packaging; code-paper fidelity is **medium**. The main scientific limitations are reliance on a known valid dependence bound, prior-relative rather than joint privacy, nonstandard composition behavior, bounded-data assumptions, and evaluation limited to one synthetic family. Reproducibility rating: **3/5**.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
