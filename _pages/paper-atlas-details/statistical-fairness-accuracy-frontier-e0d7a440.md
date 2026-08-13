---
layout: default
permalink: /paper-atlas/statistical-fairness-accuracy-frontier-e0d7a440/
title: "Statistical_Fairness_Accuracy_Frontier"
nav: false
description: "假设政策制定者必须给两个群体使用同一个预测模型。两个群体的数据规律不同，因此一个模型不可能同时对两者都达到各自的最优误差。制定者不仅关心总体预测是否准确，也关心误差如何分配给两个群体。 已有的公平—准确性（fairness–accuracy, FA）前沿主要研究一个理想问题：如果完整的人群分布已知，哪些群体误差组合是不可被同时改进的？这篇论文研究更现实的有限样本版本： 从两组有限数据估计目标前沿点会损失多少福利？"
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
      <span>arXiv · 2025</span>
    </div>
    <h1>Statistical_Fairness_Accuracy_Frontier</h1>
    <p>The Statistical Fairness–Accuracy Frontier</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2508.17622" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Statistical_Fairness_Accuracy_Frontier">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 《The Statistical Fairness–Accuracy Frontier》方法详解

### 1. 论文究竟在解决什么问题？

假设政策制定者必须给两个群体使用**同一个预测模型**。两个群体的数据规律不同，因此一个模型不可能同时对两者都达到各自的最优误差。制定者不仅关心总体预测是否准确，也关心误差如何分配给两个群体。

已有的公平—准确性（fairness–accuracy, FA）前沿主要研究一个理想问题：如果完整的人群分布已知，哪些群体误差组合是不可被同时改进的？这篇论文研究更现实的有限样本版本：

1. 从两组有限数据估计目标前沿点会损失多少福利？
2. 已知或未知两组协变量分布时，最优估计器分别是什么？
3. 固定采样预算应该怎样分给两个群体？
4. 估计误差是否会不对称地伤害某一群体？
5. 能否一次性控制整条经验 FA 前沿，而不只是固定的一个点？

这不是生物信息学论文，而是统计学习、算法公平与福利分析的理论工作。

### 2. 先澄清“公平”的定义

对群体 $g\in\{r,b\}$，预测器 $f$ 的风险为

$$
\mathcal R_g(f)=\mathbb E[\ell(f(X),Y)\mid G=g].
$$

论文把公平度量定义为

$$
|\mathcal R_r(f)-\mathcal R_b(f)|,
$$

即两个群体的预测损失之差；在文中讨论的回归场景中，这对应 Equalized Loss。它**不是**人口统计均等（demographic parity）、机会均等或 equalized odds。后续所有保证只适用于这一风险/福利定义，不能直接替换成其他公平准则。

预测器 $f'$ 对 $f$ 构成 FA 支配，需要同时满足：

- 两个群体的风险都不更高；
- 两组风险差不更大；
- 三项中至少一项严格改善。

所有不被其他预测器 FA 支配的风险对组成 FA 前沿。

### 3. 用福利权重参数化前沿

在“群体平衡”的几何情形中，前沿从红组最优模型出发，经过风险相等点，到达蓝组最优模型。论文用 $\lambda\in[0,1]$ 参数化它：

$$
f_\lambda=\arg\min_f\mathcal R_\lambda(f),
\qquad
\mathcal R_\lambda(f)=\lambda\mathcal R_r(f)+(1-\lambda)\mathcal R_b(f).
$$

$\lambda$ 表示制定者对红组误差的相对福利权重，$1-\lambda$ 是蓝组权重。改变 $\lambda$，等价于用不同斜率的支持线接触可达风险集合，从而扫过前沿。

需要注意：$\lambda=1/2$ 只是给两组误差同等边际权重，并不保证两组风险相等；真正的“最公平点”是前沿与两组风险相等线的交点。

### 4. 共享线性模型

理论部分假设每个群体有自己的真实线性机制：

$$
Y=X^\top\beta_g+\varepsilon_g,
\qquad
\mathbb E[\varepsilon_g\mid X]=0,
\qquad
\mathbb E[\varepsilon_g^2\mid X]=\sigma^2,
$$

但部署时只能使用一个共享系数 $\beta$。损失为平方损失。定义

$$
\Sigma_g=\mathbb E_g[XX^\top],
\qquad
\nu_g=\mathbb E_g[XY]=\Sigma_g\beta_g.
$$

给定 $\lambda$，总体分布下的 oracle 系数是

$$
\beta_\lambda
=\Sigma_\lambda^{-1}\nu_\lambda,
$$

其中

$$
\Sigma_\lambda=\lambda\Sigma_r+(1-\lambda)\Sigma_b,
\qquad
\nu_\lambda=\lambda\nu_r+(1-\lambda)\nu_b.
$$

所以 $\beta_\lambda$ 不是 $\beta_r$ 与 $\beta_b$ 的普通线性插值，而是由两组协方差共同决定的加权组合。

### 5. 方法流程

```text
输入：红组样本 S_r、蓝组样本 S_b、福利权重 lambda
  |
  +-- 每组计算：样本协方差 Sigma_hat_g
  |              交叉矩 nu_hat_g
  |              组内 OLS 系数 beta_hat_g
  |
  +-- 如果真实 Sigma_r、Sigma_b 已知
  |      用真实协方差把两组 OLS 系数组合成 beta_tilde_lambda
  |
  +-- 如果真实协方差未知
  |      用经验协方差和经验交叉矩直接做加权 OLS，得到 beta_hat_lambda
  |
  +-- 计算共享模型对两组的风险对 (R_r, R_b)
  |
  +-- 遍历 lambda，得到经验 FA 前沿
输出：每个 lambda 对应的共享预测器及其两组风险
```

### 6. 情形一：协方差已知

先分别拟合两组 OLS：

$$
\widehat\beta_g=\widehat\Sigma_g^{-1}\widehat\nu_g.
$$

然后构造

$$
\widetilde\beta_\lambda
=\Sigma_\lambda^{-1}
\left[\lambda\Sigma_r\widehat\beta_r
+(1-\lambda)\Sigma_b\widehat\beta_b\right].
$$

它保持了 oracle 的协方差加权结构，只把未知的群体系数替换为 OLS 估计。定理 1 证明它在已知协变量分布的线性模型族中，对相应的最坏情形误差是精确 minimax 最优的；实际上只需要知道协方差，不需要完整协变量分布。

在球形协方差 $\Sigma_g=\rho_g^2I_d$ 下，误差主阶包含

$$
\frac{\lambda^2\rho_r^2}{n_r}
+\frac{(1-\lambda)^2\rho_b^2}{n_b}.
$$

固定总样本数时，相应的采样比例为

$$
\frac{n_r}{n_b}=\frac{\lambda\rho_r}{(1-\lambda)\rho_b}.
$$

因此，福利权重越高或协变量尺度越大的群体应得到更多样本。这类似分层抽样中的 Neyman allocation。

### 7. 情形二：协方差未知

此时直接最小化加权经验风险：

$$
\widehat\beta_\lambda
=(\lambda\widehat\Sigma_r+(1-\lambda)\widehat\Sigma_b)^{-1}
[\lambda\widehat\nu_r+(1-\lambda)\widehat\nu_b].
$$

误差分成两部分：

$$
\mathbb E\|\widehat\beta_\lambda-\beta_\lambda\|_{\Sigma_g}^2
=\mathcal V_g(\lambda)+\mathcal B_g(\lambda).
$$

- **方差项 $\mathcal V_g$**：来自不知道 $\beta_r,\beta_b$，与已知协方差情形的误差同阶。
- **偏差项 $\mathcal B_g$**：来自用经验协方差替代真实协方差。即使 $\beta_r,\beta_b$ 已知，它仍会存在。

偏差项与 $\|\beta_r-\beta_b\|^2$ 成比例。当两个群体的真实回归机制相同时，它消失；群体越异质，它越重要。论文在指定的 Gaussian/subgaussian、谱界、参数有界和样本量条件下给出同阶上界与 minimax 下界，因此加权 OLS 在此情形是**常数因子意义下**的 minimax 最优，而不是无条件的精确最优。

采样设计由两个目标拉扯：

- 降低方差项，倾向于采用 $\lambda$ 和 $\rho_g$ 加权的非均衡分配；
- 降低协方差偏差项，在两组尾部常数相同时倾向于 $n_r=n_b$。

因此群体差异越大，越应该向平衡采样移动。论文没有给出对所有参数都适用的单一全局最优比例。

### 8. 为什么有限样本会对两组产生不对称影响？

单组风险差满足

$$
\mathcal R_g(\widehat\beta_\lambda)-\mathcal R_g(\beta_\lambda)
=\|\widehat\beta_\lambda-\beta_\lambda\|_{\Sigma_g}^2
+2(\widehat\beta_\lambda-\beta_\lambda)^\top
\Sigma_g(\beta_\lambda-\beta_g).
$$

第二项带符号。按 $\lambda$ 和 $1-\lambda$ 对两组求和时它抵消，所以它对两组的贡献方向相反。其红组界含 $\lambda(1-\lambda)^2$，蓝组界含 $\lambda^2(1-\lambda)$。靠近一个端点时，没有被优先考虑的群体可能承担更大的绝对偏差效应。

这说明：制定者在总体目标中写下的福利权重，不一定等于有限数据实际实现的群体误差分配。

### 9. 整条前沿的统一保证

此前结果针对固定 $\lambda$ 的期望误差。为了允许制定者查看整条经验曲线后再选择 $\lambda$，论文定义

$$
\Delta_\lambda
=\widehat{\mathcal R}_\lambda-\mathcal R_\lambda\in\mathbb R^2.
$$

定理 4 对未知协方差估计器证明：在概率至少为 $1-\delta-\eta$ 时，

$$
\sup_{\lambda\in[0,1]}\|\Delta_\lambda\|_2
\le C_u\log(1/\delta)
\left[
\frac{\log^5(n_r)}{\sqrt{n_r}}
+\frac{\log^5(n_b)}{\sqrt{n_b}}
\right].
$$

它同时覆盖连续区间中的所有 $\lambda$，比在有限网格上简单做 union bound 更强。证明使用截断与良态协方差事件、估计器关于 $\lambda$ 的 Lipschitz 性、Doob 鞅有界差分、chaining 和 $\varepsilon$-net。

作者把它解释为总体前沿周围的置信带。但要准确理解：这是非渐近的高概率统一偏差界，不是论文已经实现的点态标准误程序、假设检验，也没有给出如何从数据精确估计常数 $C_u$。不能把它和前面“固定 $\lambda$ 的期望 minimax 风险”混为一谈。

### 10. 实验与证据边界

论文只做了合成实验：两组 Gaussian 线性模型、$d=15$、50 个 $\lambda$ 网格点，每个点 100 次 Monte Carlo。比较总体前沿、已知协方差经验前沿和未知协方差经验前沿。

- 等样本、不同协方差时，较大协方差尺度的蓝组风险膨胀更明显，未知协方差曲线离总体前沿更远。
- 同协方差、不同样本数时，两组风险膨胀近似对称。
- 在 $\lambda=0,1$ 端点，已知与未知协方差估计器重合，符合偏差中的 $\lambda^2(1-\lambda)^2$ 因子。

这些图验证的是定性机制，不是 minimax 下界或统一置信带覆盖率的实证检验。

### 11. 局限与复现状态

- 仅覆盖两个群体、平方损失、正确设定的线性模型、相同噪声方差以及较强的可逆性与尾部条件。
- 没有真实数据、非线性模型、多群体、群体标签不确定性或动态反馈实验。
- 未找到官方代码或补充材料。检索范围包括论文与 arXiv source、ar5iv HTML、以及 GitHub 精确标题仓库查询。
- 数学公式足以自行重写估计器，但论文未提供实验脚本、随机种子和完整生成配置，不能逐点复现 Figure 5。

最重要的阅读结论是：这篇论文并没有提出一个普适的“公平算法”。它给出的是一个特定风险公平定义下，有限样本如何收缩 FA 前沿、怎样设计 minimax 估计器与采样分配，以及这种统计误差如何改变群体福利分布的精确理论框架。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## The Statistical Fairness–Accuracy Frontier

### Problem

A policymaker often has to deploy one predictor across heterogeneous groups while caring both about total predictive error and how that error is distributed. A population fairness–accuracy (FA) frontier describes the non-dominated risk tradeoffs when the full data distribution is known, but real designers estimate a point—or the whole curve—from finite and potentially imbalanced group samples. This paper asks how much welfare is lost through that estimation, which estimator is minimax optimal under different covariance information, how samples should be allocated, and which group bears the error.

The fairness notion is specific: for group risks $\mathcal R_r(f)$ and $\mathcal R_b(f)$, fairness is the risk disparity $|\mathcal R_r(f)-\mathcal R_b(f)|$ (Equalized Loss). FA dominance requires weakly lower risk for both groups and weakly lower disparity, with at least one strict improvement. This is not demographic parity or equalized odds.

### Method

For group-balanced problems, a welfare weight $\lambda\in[0,1]$ traces the frontier through

$$
f_\lambda=\arg\min_f\{\lambda\mathcal R_r(f)+(1-\lambda)\mathcal R_b(f)\}.
$$

The technical results use two group-specific homoskedastic linear outcome models, $Y=X^\top\beta_g+\varepsilon_g$, but require one shared linear coefficient at deployment. The oracle coefficient is a covariance-weighted combination,

$$
\beta_\lambda=[\lambda\Sigma_r+(1-\lambda)\Sigma_b]^{-1}
[\lambda\Sigma_r\beta_r+(1-\lambda)\Sigma_b\beta_b].
$$

With known covariances, the proposed estimator substitutes group OLS estimates for $\beta_r,\beta_b$ in this oracle expression. It is exactly minimax optimal for the relevant worst-case parameter errors and weighted excess risk; knowledge of the full covariate distributions beyond $\Sigma_r,\Sigma_b$ does not improve it. Under spherical covariances, its finite-sample bound implies the allocation rule

$$
n_r/n_b=\lambda\rho_r/[(1-\lambda)\rho_b].
$$

With unknown covariances, weighted empirical OLS uses empirical covariance and cross-moment mixtures. Its error separates into coefficient-estimation variance and covariance-estimation bias. The bias scales with $\|\beta_r-\beta_b\|^2$, vanishes for identical group mechanisms, and leads heterogeneous problems toward more balanced sampling. Matching-order upper and lower bounds establish minimax optimality up to constants under the paper's Gaussian/subgaussian, spectrum, bounded-parameter, and sample-size conditions.

### Main findings

- Finite-sample error can be asymmetric by group even though the same estimator serves everyone. In the known-covariance setting, expected per-group inflation differs through covariance scale; unequal sample counts do not map mechanically to unequal group harm because both samples estimate one shared coefficient.
- With estimated covariances, an additional signed cross term affects the two groups in opposite directions. Its red- and blue-group bounds have different $\lambda$ factors, so the non-prioritized group can bear the larger bias effect near an endpoint.
- The variance term favors welfare- and covariance-weighted sample allocation, whereas the covariance-bias term favors balanced group samples. The tradeoff depends on group heterogeneity; the paper does not reduce it to one universal allocation formula.
- Beyond fixed-$\lambda$ expected-error bounds, Theorem 4 controls the entire unknown-covariance empirical frontier simultaneously. Up to logarithmic factors, the high-probability Euclidean deviation scales as $n_r^{-1/2}+n_b^{-1/2}$, allowing $\lambda$ to be selected after inspecting the curve.

The last result is a nonasymptotic uniform deviation bound interpreted as a confidence band. It is not a reported pointwise standard-error method, calibrated hypothesis test, or operational procedure for estimating its unknown constant.

### Evaluation

The evaluation is a synthetic mechanism check rather than a broad benchmark. A two-group Gaussian linear model with isotropic covariances is simulated in $d=15$. For 50 $\lambda$ values and 100 Monte Carlo repetitions per value, the paper compares the population frontier with known- and unknown-covariance empirical frontiers.

With equal sample counts but unequal covariance scales, Figure 5a shows a larger inflation of blue-group risk and a visibly larger gap for the unknown-covariance estimator. With equal covariances but unequal sample counts, Figure 5b shows roughly symmetric group-risk inflation. The empirical estimators meet at $\lambda=0,1$, consistent with covariance bias vanishing at the endpoints. These plots illustrate the theory qualitatively; they do not validate minimax lower bounds or the uniform band's coverage.

### Relation to prior work

Liang et al. (*Journal of Political Economy*, 2025) characterize the FA frontier under full distributional knowledge. Liu and Molinari (arXiv, 2024) derive asymptotic frontier inference, and Auerbach et al. (arXiv, 2024) test fairness improvability. This paper instead gives finite-sample, nonasymptotic minimax estimation and full-frontier deviation results for a shared linear regression model. It also differs from work targeting explicit Wasserstein fairness constraints, demographic parity, or equalized odds because its normative primitive is the vector of group prediction risks.

### Limitations and reproducibility

- Scope is two groups, squared loss, a correctly specified shared linear predictor, equal noise variance, and strong invertibility/tail conditions; extensions to nonlinear models, multiple or uncertain group labels, and feedback are left open.
- Evidence is synthetic only; there is no real-data case study, baseline algorithm benchmark, or sensitivity analysis beyond the two plotted regimes.
- **Official code: Not found.** Acquisition checked the arXiv source, ar5iv HTML, paper text, and an exact-title GitHub repository search. No supplementary material was found either.
- The paper gives estimator formulas and simulation parameters but not a released script, random seed, or full generation details sufficient for exact plot reproduction.

**Reproducibility rating: 2/5.** The core estimators and stylized experiment can be reimplemented from the mathematics, but the absence of official code and exact experiment artifacts prevents direct reproduction. This limitation does not weaken the source-grounded theoretical analysis, but it constrains empirical verification.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
