---
layout: default
permalink: /paper-atlas/general-framework-estimating-preferences-response-time-687bc6c3/
title: "General_Framework_Estimating_Preferences_Response_Time"
nav: false
description: "这是一篇关于经济决策、统计学习和机器学习理论的论文，不是生物信息学论文。 传统经济学常把“偏好”直接等同于观察到的选择：面对 \\bm{x} 和 \\bm{y}，选择哪一个就表示偏好哪一个。但同一个选择可能来自不同的证据强度和犹豫程度。论文利用每次选择花费的时间，希望从 恢复共同的偏好参数 \\bm w^。其中 zi\\in\\{-1,1\\} 表示选择，ti\\geq0 表示反应时间。"
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
      <span>ACM Conference on Economics and Computation (EC) · 2026</span>
    </div>
    <h1>General_Framework_Estimating_Preferences_Response_Time</h1>
    <p>A General Framework for Estimating Preferences Using Response Time Data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2507.20403" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 用选择与反应时间估计偏好：方法详解

### 1. 论文究竟在解决什么问题？

这是一篇关于经济决策、统计学习和机器学习理论的论文，不是生物信息学论文。

传统经济学常把“偏好”直接等同于观察到的选择：面对 $\bm{x}$ 和 $\bm{y}$，选择哪一个就表示偏好哪一个。但同一个选择可能来自不同的证据强度和犹豫程度。论文利用每次选择花费的时间，希望从

$$
\mathcal S=\{(\bm x_i,\bm y_i,z_i,t_i)\}_{i=1}^n
$$

恢复共同的偏好参数 $\bm w^*$。其中 $z_i\in\{-1,1\}$ 表示选择，$t_i\geq0$ 表示反应时间。

难点在于：如果直接建立选择和反应时间的完整联合分布，模型会很重，而且稍微扩展决策过程后，似然就可能难以计算。本文的核心想法是只抓住一个条件矩——“平均选择 / 平均反应时间”的比值，而不拟合完整分布。

### 2. 核心方法：把速度—准确率比写成一个二次损失

论文选择一个参数化函数 $g(\bm x,\bm y;\bm w)$，并假设真实参数满足

$$
g(\bm x,\bm y;\bm w^*)=
\frac{\mathbb E[z(\bm x,\bm y)]}{\mathbb E[t(\bm x,\bm y)]}.
\tag{1}
$$

作者把这个量称为与“速度—准确率”有关的比值。随后定义经验损失

$$
\hat{\mathcal L}(\bm w)=\frac1n\sum_{i=1}^n
\left[
\frac{t_i}{2}g(\bm x_i,\bm y_i;\bm w)^2
-z_i g(\bm x_i,\bm y_i;\bm w)
\right].
\tag{4}
$$

这个形式不是经验凑出来的。其总体超额风险恰好是

$$
\mathcal L(\bm w)-\mathcal L(\bm w^*)
=\frac12\mathbb E\left[
\mathbb E[t\mid\bm x,\bm y]
\big(g(\bm x,\bm y;\bm w)-g(\bm x,\bm y;\bm w^*)\big)^2
\right].
\tag{5}
$$

因此，$\bm w^*$ 一定是总体损失的极小点；若任意其他参数都会让 $g$ 在正概率区域发生变化，它还是唯一极小点。这里要注意：可识别的是由数据分布和 $g$ 支持的参数方向，不是无条件恢复所有坐标。

如果函数族写错了，方法仍会寻找在反应时间加权平方距离下最接近真实比值的 $g$。这时结果应理解为“最佳近似”，不能再称为真实结构参数的完全恢复。

### 3. 从输入到输出的计算流程

```text
每次试验：(x_i, y_i, z_i, t_i)
             |
             v
选择决策过程，并推导 g(x,y;w)=E[z]/E[t]
             |
             v
计算单样本损失 (t_i/2)g_i(w)^2-z_i g_i(w)
             |
             v
对全部样本求平均并优化 w
             |
             v
得到偏好参数或可识别的“参数/边界”比例
             |
             +--> 预测选择
             +--> 若恢复尺度/边界，再预测反应时间
             +--> 将参数转成经济含义
```

框架没有规定统一优化器。$g$ 的具体形式决定目标是否凸、参数是否可识别，以及能否获得全局解。

### 4. 漂移扩散模型（DDM）

#### 4.1 为什么 DDM 特别适合这个框架？

DDM 用带漂移的布朗运动描述证据累积：

$$
W_t=B_t+v(\bm x,\bm y;\bm w^*)t.
\tag{11}
$$

轨迹先碰到上边界 $b$ 就选择 $\bm x$，先碰到下边界 $-b$ 就选择 $\bm y$，首次碰界时间就是反应时间。DDM 的关键恒等式是

$$
\frac{\mathbb E[z]}{\mathbb E[t]}=\frac{v(\bm x,\bm y;\bm w^*)}{b}.
$$

所以只需令 $g=v/b$。在标准 DDM 下，这个二次目标与最大似然估计仅差一个 $b^2$ 的比例因子。但这不是通用事实，扩展 DDM 中最大似然会复杂得多。

#### 4.2 线性漂移与 $1/n$ 收敛

线性模型取

$$
v(\bm x,\bm y;\bm w^*)=(\bm x-\bm y)^\top\bm w^*.
\tag{16}
$$

此时目标是二次函数。论文给出逐样本随机梯度更新，并对平均迭代量证明

$$
\mathbb E\left[
\left\|\frac1{n+1}\sum_{i=0}^{n}\hat{\bm w}_i-\bm w^*\right\|_\Sigma^2
\right]=O(1/n),
$$

其中

$$
\Sigma=\mathbb E[(\bm x-\bm y)(\bm x-\bm y)^\top].
$$

$\Sigma$-范数直接衡量预测漂移率的平方误差。该界不依赖 $\Sigma$ 的最小特征值，因此即使某些参数方向没有数据支持，漂移预测仍可有良好保证。但这也意味着定理并没有宣称这些无支持方向上的欧氏参数误差会收敛。

只使用选择时，线性 DDM 会退化为 Logit 回归。反应时间目标主要识别 $\bm w^*/b$，而选择似然识别 $b\bm w^*$；论文指出两者结合可分别恢复 $\bm w^*$ 与边界 $b$。

#### 4.3 非线性漂移

非线性 $v$ 可能让经验目标变为非凸。论文并未证明任意梯度算法都能找到全局最优，而是在“已经得到近似经验解”的条件下，用 Rademacher 复杂度控制泛化误差。对于文中有界的 Lipschitz 示例，量级为 $\log(n)/\sqrt n$，还要加上优化误差。若要把损失差转成参数差，还必须额外满足不同参数产生可分离漂移函数的条件。

#### 4.4 随机起点的扩展 DDM

扩展模型加入均值为零的随机初始偏置：

$$
W_t=B_t+v(\bm x,\bm y;\bm w^*)t+\zeta.
\tag{28}
$$

此时完整似然依赖未知的 $\zeta$ 分布，计算可能不可行；但 Proposition 2 证明 $\mathbb E[z]/\mathbb E[t]=v/b$ 仍成立。因此无需知道初始偏置分布，仍可使用同一个二次目标。这是矩方法相对完整似然最有说服力的鲁棒性优势。

### 5. 对数正态竞速模型与半空间学习

在 lognormal race（LNR）模型中，两个选择各有一个随机到达时间，先到者获胜。论文推导了 $\mathbb E[z]$ 和 $\mathbb E[t]$ 的闭式表达，再把两者之比代入同一损失。目标通常非凸，但可数值优化；竞速思想原则上也能扩展到两个以上的选择。

论文还把线性 DDM 与 Massart 噪声下的半空间学习比较。响应时间方法恢复的是潜在偏好规则，而不仅是预测带噪选择。在 DDM 和边距条件下，Proposition 4 的样本复杂度对误差 $\varepsilon$ 是 $1/\varepsilon$，优于文中引用的选择预测结果的 $1/\varepsilon^2$。代价是必须接受更强的 DDM 过程假设，二者不是无条件公平替代。

### 6. 实证应用

数据来自 Amasino et al.（2019）的跨期选择复现实验：100 名受试者，每人约 141 次选择。每次比较即时金额 $[m_i,0]$ 与延迟获得 10 美元的 $[10,t_d]$。作者对每位受试者单独建模，前 100 条训练，剩余约 40 条测试，比较：

1. 只用选择的线性 DDM；
2. 同时使用选择与反应时间的线性 DDM；
3. 固定 $D_0=\rho=0$ 的 LNR。

三者平均测试选择错误率分别为 0.0754、0.0627 和 0.1215。八个本地图板显示：加入时间的 DDM 整体误差分布更优，LNR 尾部更差；反应时间区间总体覆盖良好但个体间差异明显。

为预测反应时间，作者在得到 $\bm w^*/b$ 后，用平均反应时间矩匹配估计 $b$，再构造预测均值 $\pm1$ 个标准差的区间，平均未覆盖率为 0.051。论文没有给出该矩匹配的完整数值算法。

对于奖励 $R$、延迟 $T$，线性效用

$$
w_rR-w_tT
$$

在论文的 CARA 映射下对应折扣因子 $\exp(-w_t/w_r)$。约 90% 的受试者在“选择+时间”模型中得到更大的折扣因子，说明是否使用反应时间会改变经济解释，而不只是改变预测精度。

### 7. 应怎样理解结论？

- “不需要分布假设”应准确理解为：损失不需要完整的选择/时间联合分布；具体 $g$ 仍包含 DDM、竞速模型等结构假设。
- $1/n$ 是线性 DDM 下、$\Sigma$-范数中的期望平方误差率，不是所有模型、所有范数和所有优化算法的统一结论。
- 非线性定理控制泛化差，并不自动解决非凸优化。
- 实证结果支持该数据集上的改进，不证明反应时间模型在所有任务中都优于只用选择的方法。
- 图中存在主体间异质性和少量离群点，不能把“约 90%”写成“所有人”。

### 8. 复现边界

- 官方代码：在全文、arXiv HTML、采集清单和 GitHub 链接 sidecar 中均 **Not found**。
- 补充材料：在当前采集源中 **Not found**。
- 实证预处理、优化器、初始化、停止条件和随机种子：**Not found**。
- 边界 $b$ 的精确矩匹配步骤：**Not found**，论文只给出文字描述。
- 因此当前分析为 `paper-only`；理论公式和八个图板已核验，但数值结果未独立复现。

论文标题、作者和 arXiv `2507.20403v2` 由原文确认。ACM Conference on Economics and Computation（EC）2026 来自 Michael I. Jordan 官方发表列表；arXiv 文稿本身没有独立写明该会议归属。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## A General Framework for Estimating Preferences Using Response Time Data

### Problem and contribution

The paper asks how to estimate economic preference parameters from paired alternatives, binary choices, and response times without committing to a full distribution for the joint choice-time process. It introduces a conditional-moment framework built around the “speed-accuracy ratio” $\mathbb E[z\mid\bm x,\bm y]/\mathbb E[t\mid\bm x,\bm y]$. Given a parameterized function $g(\bm x,\bm y;\bm w)$ that contains this ratio at the true parameter, it minimizes the response-time-weighted quadratic loss

$$
\hat{\mathcal L}(\bm w)=\frac1n\sum_{i=1}^n
\left[\frac{t_i}{2}g(\bm x_i,\bm y_i;\bm w)^2-z_i g(\bm x_i,\bm y_i;\bm w)\right].
$$

An exact excess-risk identity makes the true parameter a population minimizer and gives uniqueness when other parameters change $g$ on a positive-probability set. Under misspecification, the estimator finds the response-time-weighted closest approximation to the true ratio.

### Relation to existing approaches

Fudenberg et al. (2020) estimate and test scalar-drift DDMs using revealed drift/boundary objects and nonparametric choice probabilities. Sawarni et al. (2025) study preference-dependent DDM drift with a different Neyman-orthogonal loss. Alós-Ferrer et al. (2021) use response times for ordinal preference inference rather than parametric recovery, while Chiong et al. (2024) use setting-specific simulated nonlinear least squares. Choice-only linear DDM estimation reduces to McFadden's 1974 Logit model. The present contribution is broader than a single DDM estimator: once a model supplies the ratio of expected choice to expected time, the same quadratic construction applies.

### Main specializations and theory

For the standard Drift Diffusion Model with boundaries $\pm b$, the ratio simplifies to $v(\bm x,\bm y;\bm w^*)/b$. The loss then coincides with DDM maximum likelihood up to scale. With linear drift $v=(\bm x-\bm y)^\top\bm w^*$, Theorem 1 proves an $O(1/n)$ expected squared-error rate for the averaged stochastic-gradient iterate in the $\Sigma$-norm, where $\Sigma$ is the second moment of alternative differences. This metric measures drift-prediction error and avoids dependence on the minimum eigenvalue of $\Sigma$.

For bounded nonlinear drift classes, Theorem 2 controls generalization through Rademacher complexity, giving order $\log(n)/\sqrt n$ for the paper's bounded Lipschitz example, plus optimization error. Parameter recovery additionally needs a separation condition. For an extended DDM with an unknown mean-zero random starting bias, the same $v/b$ ratio remains valid even though maximum likelihood depends on the bias distribution and can be intractable. The paper also derives the needed moments for a lognormal race model and compares DDM parameter recovery with halfspace learning under Massart noise.

### Empirical evaluation

The application uses the Amasino et al. (2019) intertemporal-choice replication data: 100 subjects, approximately 141 choices each, a separate model per subject, the first 100 records for training, and approximately 40 for testing. It compares choice-only DDM, choice-and-time DDM, and a lognormal race model with $D_0=\rho=0$.

Mean held-out choice errors are 0.0754, 0.0627, and 0.1215, respectively. After estimating the DDM boundary by matching average response time, the choice-and-time model's mean $\pm1\sigma$ time intervals have average miscoverage 0.051. Mapping reward and delay coefficients to an exponential discount factor, the response-time fit produces a larger factor than the choice-only fit for almost 90% of subjects. All eight local panels were inspected and support the reported distributional patterns, including heterogeneity and outliers.

### Limitations and reproducibility

The framework is “distribution-free” only with respect to full outcome distributions; it still requires the chosen $g$ to correctly encode the relevant conditional-moment ratio. Linear-DDM theory is strongest, while nonlinear optimization can be nonconvex. The empirical evidence is one dataset, one train/test ordering, and one fixed LNR specification, so it does not establish universal model dominance.

No official implementation or supplementary material was found in the full paper, retained arXiv HTML, acquisition manifest, or GitHub-link sidecar. Full preprocessing, optimizer settings, initialization, stopping criteria, seeds, and the exact numerical moment-matching procedure for $b$ are Not found. The analysis is therefore paper-only: formulas and figures are inspectable, but the empirical results were not independently reproduced.

The title, authors, and arXiv `2507.20403v2` are verified by the manuscript. ACM Conference on Economics and Computation (EC), 2026 is listed on Michael I. Jordan's official publications page; the arXiv manuscript itself does not independently state that venue.

**Reproducibility assessment: 2/5.** The theoretical method is specified clearly enough to reimplement in simple cases, and data provenance/split and headline model choices are reported. Lack of code and missing empirical fitting details prevent exact reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
