---
layout: default
permalink: /paper-atlas/response-time-alignment-heterogeneous-preferences-9ecc2e98/
title: "Response_Time_Alignment_Heterogeneous_Preferences"
nav: false
description: "这篇论文不是用“反应更快就权重更大”这种经验规则，而是在 DDM 下推导出一个严格的反应时间权重，先从匿名选择恢复个体效用差的无偏代理，再平均或回归，从而识别人群的平均偏好。"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>Response_Time_Alignment_Heterogeneous_Preferences</h1>
    <p>Response Time Enhances Alignment with Heterogeneous Preferences</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2605.06987" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 用反应时间恢复异质人群的平均偏好

### 1. 这篇论文究竟在解决什么问题？

RLHF、DPO 等偏好学习方法通常把很多标注者的二选一结果混在一起，再拟合一个统一奖励函数。这个做法隐含了一个很强的假设：所有标注者拥有同一个偏好，只是选择存在随机性。

现实中，标注者的价值观、知识和口味各不相同，而且数据经常是匿名的，每个人可能只贡献一次比较。此时，选择比例描述的是“有多少人选了 A”，却不直接告诉我们“不同人偏好 A 的强度平均是多少”。因此，选择数据能够收敛到 Borda 式聚合，却不一定等于论文关心的功利主义目标——人群平均效用。

论文的关键想法很朴素：除了记录选了哪一个，还记录用了多久。反应时间不要求用户身份，也不要求重复询问，却能提供偏好强度的信息。

### 2. 反应时间为什么有用？

作者采用漂移扩散模型（Drift-Diffusion Model, DDM）。面对两个选项时，决策证据按带漂移的布朗运动积累：

$$
W_\tau=B_\tau+v\tau.
$$

证据第一次碰到 $+b$ 或 $-b$ 时做出决定：

$$
T=\inf\{\tau>0:|W_\tau|=b\},\qquad
Z=2\mathbf 1(W_T=b)-1.
$$

这里，$Z$ 是选择，$T$ 是反应时间，$v$ 是两个选项的效用差，$b$ 是作决定所需的证据阈值。$|v|$ 越大，通常越快碰到边界；所以 $T$ 含有偏好强度信息。忽略 $T$ 后，DDM 的选择概率正好退化为 Bradley–Terry 形式 $\sigma(2bzv)$，这也解释了为什么只看选择时，$b$ 与 $v$ 的尺度纠缠在一起。

论文允许每个人有不同的 $v_i$，但假设所有人共享同一个未知边界 $b$。这不是无关紧要的技术条件，而是把不同匿名个体的反应时间放到同一尺度上的核心假设。

### 3. 第一步：把每次“选择 + 时间”变成漂移的无偏代理

如果 $b$ 已知，作者构造权重

$$
w_b(t)=
\frac{\sum_{k=0}^{\infty}\left(c_k(b)^2/t-1\right)e^{-c_k(b)^2/(2t)}}
{\sum_{k=0}^{\infty}(-1)^kc_k(b)e^{-c_k(b)^2/(2t)}},
\qquad c_k(b)=(2k+1)b.
$$

最重要的恒等式是

$$
\mathbb E[Zw_b(T)\mid V=v]=v.
$$

因此，$Zw_b(T)$ 可以理解为一次匿名比较产生的“漂移伪标签”。把这些伪标签平均起来，

$$
\widehat\mu_n=\frac1n\sum_{i=1}^nZ_iw_b(T_i),
$$

就能无偏估计 $\mu=\mathbb E[V]$。这一步不需要知道第 $i$ 个标注者是谁，也不需要同一人出现第二次。

### 4. 第二步：从反应时间本身估计未知边界

实际中 $b$ 不知道。作者先计算反应时间的经验 Laplace 变换：

$$
\widehat L_n(\lambda)=\frac1n\sum_{i=1}^ne^{-\lambda T_i}.
$$

当 $\lambda$ 很大时，$-\log L_b(\lambda)/\sqrt{2\lambda}$ 接近 $b$。直接使用这一关系得到的单尺度估计虽然一致，但其总体偏差下降较慢。论文进一步用两个尺度做 Richardson 外推：

$$
\widetilde B_n=
\frac{\log\widehat L_n(\lambda_n)-\log\widehat L_n(4\lambda_n)}
{\sqrt{2\lambda_n}}.
$$

这个差分消掉展开式中的主导常数项，把总体偏差从 $O(\lambda^{-1/2})$ 改善为 $O(\lambda^{-1})$。在实验中，$\lambda_n=(\log n)^{3/2}$。

### 5. 完整算法流程

```text
输入：匿名的 (选择 Z_i, 反应时间 T_i, 可选比较特征 psi_i)
                         |
                         v
         计算 lambda_n 与 4 lambda_n 的经验 Laplace 变换
                         |
                         v
            得到 Richardson 边界估计 B_tilde_n
                         |
                         v
           构造伪标签 v_hat_i = Z_i w_{B_tilde_n}(T_i)
                    /                         \
                   v                           v
            对伪标签取平均                 用 psi_i 回归伪标签
                   |                           |
                   v                           v
         平均效用差 mu                    平均偏好向量 theta*
```

如果所有比较针对同一对选项，输出

$$
\widehat\mu_n^{\mathrm{PI}}=\frac1n\sum_iZ_iw_{\widetilde B_n}(T_i).
$$

如果效用是线性的，令 $\psi_i=\phi(x_i)-\phi(y_i)$，并计算

$$
\widehat v_i=Z_iw_{\widetilde B_n}(T_i),\quad
\widehat Q_n=\frac1n\sum_i\psi_i\psi_i^\top,\quad
\widehat m_n=\frac1n\sum_i\psi_i\widehat v_i,
$$

最终输出

$$
\widehat\theta_n=\widehat Q_n^{-1}\widehat m_n.
$$

直观上，这是先用反应时间把被 logistic 非线性扭曲的选择还原成效用差代理，再做普通线性回归。定理证明，在论文的 DDM、共同边界、独立性和矩条件下，$\widehat\theta_n$ 收敛到人群平均偏好 $\theta^\star$。

### 6. 与已有方法的区别

- **经典 RLHF（Christiano 等，NeurIPS 2017；Ouyang 等，NeurIPS 2022）**：用二元偏好拟合单一奖励，不处理匿名异质偏好的平均效用识别。
- **DPO（Rafailov 等，NeurIPS 2023）及其变体**：改变策略优化损失，但仍依赖单一奖励的选择统计骨架。
- **异质偏好与社会选择研究（2024–2025）**：指出 Bradley–Terry 聚合会出现 Borda 偏移或最坏情形失真；本文不是再设计一种投票规则，而是增加反应时间这个正交观测信号。
- **已有反应时间推断工作**：已知边界时可以推断偏好；本文的新增重点是在同一批匿名异质数据中同时估计未知共同边界与平均偏好。

### 7. 实验说明了什么？

合成实验包含固定两选项的标量情形和四维线性情形。Bradley–Terry 的 MSE 随样本增加后停在非零平台，而 DDM 估计继续下降，并逐渐接近知道真实边界的 oracle。边界消融图也显示 Richardson 估计比单尺度估计更接近真实 $b=1.25$。

真实实验使用 Amasino 等（2019）的跨期选择数据。清洗后有 98 名参与者的 13,793 次试验。最大子样本 $n=5000$ 时，DDM 估计与个体级目标方向的余弦相似度约为 0.998，而 pooled Bradley–Terry 约停在 0.993–0.994。

这个结果不能被解读为“真实人类严格服从 DDM”。论文自己明确说明：真实数据实验是在模型可能错设时展示反应时间仍有信息，而不是额外的识别定理。

### 8. 使用边界与尚未解决的问题

1. **共同边界是核心假设。** 如果不同人的谨慎程度不同，反应时间差异可能同时来自偏好强度和阈值差异。
2. **非决策时间。** 对固定的加性非决策时间，附录给出三尺度修正；随机或个体异质的非决策时间尚未解决。
3. **有限样本代价。** 边界依赖大 $\lambda$ 的 Laplace 尾部，实际收敛可能慢，因此作者专门加入 Richardson 修正。
4. **不是完整的 LLM 对齐系统。** 论文解决奖励目标的统计估计，没有给出端到端 RLHF/DPO 训练实现。
5. **代码缺失。** 在 arXiv 页面、全文、采集 sidecar 和 GitHub 晚期发现流程中均未找到官方代码。公式和实验设置较详细，但数值实现无法用作者代码独立核验。

### 9. 一句话理解

这篇论文不是用“反应更快就权重更大”这种经验规则，而是在 DDM 下推导出一个严格的反应时间权重，先从匿名选择恢复个体效用差的无偏代理，再平均或回归，从而识别人群的平均偏好。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Response Time Enhances Alignment with Heterogeneous Preferences

### Problem

Modern RLHF and direct preference-learning pipelines pool binary labels and fit one Bradley–Terry-style reward. That statistical model treats labelers as if they shared one preference. With anonymous, heterogeneous labelers, pooled choices can converge to a Borda-like aggregate rather than the cardinal population-average utility, and the mean preference scale is not identifiable when the choice temperature is unknown.

The paper asks whether one inexpensive extra measurement—the time taken to choose—can identify the utilitarian average even when every observation may come from a fresh, anonymous labeler.

### Proposed method

Each decision follows a drift-diffusion model (DDM): evidence is Brownian motion with individual-specific drift $V_i$ and a shared but unknown absorbing boundary $b$. The sign of the first boundary hit is the choice $Z_i$; the hitting time is the response time $T_i$. The authors derive a response-time weight $w_b(t)$ for which $Z_iw_b(T_i)$ is an unbiased pseudo-outcome for $V_i$ when $b$ is known.

For unknown $b$, they estimate the large-$\lambda$ tail of the empirical response-time Laplace transform. A two-scale Richardson extrapolation,

$$
\widetilde B_n=
\frac{\log\widehat L_n(\lambda_n)-\log\widehat L_n(4\lambda_n)}
{\sqrt{2\lambda_n}},
$$

cancels the dominant population-bias term and is consistent. Plugging $\widetilde B_n$ into the response-time weight gives a consistent estimate of the mean drift. In a linear contextual model, ordinary least squares of these pseudo-outcomes on comparison features consistently recovers $\theta^\star=\mathbb E[\theta_i]$. This implies asymptotic utilitarian distortion one under the paper's assumptions, unlike the choice-only barrier.

### Evidence

Synthetic experiments compare pooled Bradley–Terry, the plug-in DDM estimator, and an oracle DDM estimator that knows $b$. In both scalar and four-dimensional contextual settings, Bradley–Terry MSE plateaus, while DDM error continues to decline over increasing sample sizes. Boundary ablations visually show that Richardson extrapolation remains closer to the true $b=1.25$ than the one-scale estimator.

The real-data study uses 13,793 intertemporal-choice trials from 98 participants after filtering. Across 50 subsamples, the DDM estimator reaches cosine similarity of about 0.998 to a subject-level target at $n=5000$, versus roughly 0.993–0.994 for pooled Bradley–Terry. The paper correctly treats this as empirical evidence under possible DDM misspecification, not as a new real-data identification proof.

### Assumptions and limitations

- Identification depends on a common DDM boundary and response times that meaningfully reflect first-passage decisions.
- The main theory assumes bounded drifts/preferences, with appendix extensions to suitable exponential moments.
- Deterministic additive non-decision time receives a three-scale correction; random or heterogeneous non-decision time remains unresolved.
- The method estimates an aggregate reward/preference target but does not implement an end-to-end RLHF or DPO training system.
- Large-$\lambda$ boundary estimation can converge slowly in finite samples.

### Reproducibility

The arXiv HTML provides detailed equations, proofs, five figures, and Appendix C settings: $\lambda_n=(\log n)^{3/2}$, $K=100$ series terms, 50 main replications, sampling grids, preprocessing, and reported compute. However, no official code repository or runnable scripts were found in the paper, arXiv sidecars, or late-code search. The workspace is therefore `paper-only`; mathematical and figure claims are well documented, but computational reproduction cannot be independently verified from supplied code.

**Reproducibility rating: 3/5.** Strong mathematical specification and unusually detailed experimental settings, reduced by missing implementation and local data artifacts.

### Classification

This is a primary machine-learning/statistical-method paper with foundations in behavioral decision theory, game theory, and theoretical economics. It is not a bioinformatics paper.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
