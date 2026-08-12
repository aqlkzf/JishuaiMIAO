---
layout: default
permalink: /paper-atlas/how-sampling-shapes-llm-alignment-8043bb47/
title: "How_Sampling_Shapes_LLM_Alignment"
nav: false
description: "这是一篇理论机器学习与 LLM 对齐论文，不是生物信息学文章。它关心一个常被当成工程细节的问题：做偏好学习时，我们究竟让人比较哪些候选回答？ 通常的直觉是，只要数据足够多，采样策略至多影响方差和训练速度，不该改变最终答案。本文指出：这个直觉只有在非常理想化的 Bradley--Terry（BT）偏好模型下才可能成立。真实偏好如果包含上下文依赖、循环偏好或无法用单一标量奖励表达的矛盾，采样分布本身会参与定义“最优策略”。"
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
    <h1>How_Sampling_Shapes_LLM_Alignment</h1>
    <p>How Sampling Shapes LLM Alignment: From One-Shot Optima to Iterative Dynamics</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2602.12180" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 采样如何塑造 LLM 对齐：从单轮最优解到迭代动力学

### 这篇论文究竟在问什么？

这是一篇理论机器学习与 LLM 对齐论文，不是生物信息学文章。它关心一个常被当成工程细节的问题：做偏好学习时，我们究竟让人比较哪些候选回答？

通常的直觉是，只要数据足够多，采样策略至多影响方差和训练速度，不该改变最终答案。本文指出：这个直觉只有在非常理想化的 Bradley--Terry（BT）偏好模型下才可能成立。真实偏好如果包含上下文依赖、循环偏好或无法用单一标量奖励表达的矛盾，采样分布本身会参与定义“最优策略”。如果新模型又被用于生成下一轮候选回答和更新参考模型，采样效应还会被逐轮放大。

### 1. 基本对象

对一个固定 prompt，设有 $K$ 个候选回答：

- $P_{ij}=\Pr(i\succ j)$：回答 $i$ 胜过 $j$ 的概率；$P$ 不必服从 BT 模型。
- $\bm\mu$：生成比较对时的采样分布。
- $\bm\pi_{\mathrm{ref}}$：用于正则化的参考策略。
- $\bm\pi$：训练后策略。
- $\beta$：偏好信号相对于 KL 锚定的强度。

论文选择 IPO 作为主要分析对象，因为它的总体最优解可以显式写成

$$
\boxed{
\bm\pi^\star\propto
\bm\pi_{\mathrm{ref}}\odot
\mathrm{softmax}(\beta P\bm\mu)
}
$$

这里 $(P\bm\mu)_i$ 是回答 $i$ 对采样对手的加权胜率。因此，改变 $\bm\mu$ 不只是重新加权同一个估计量，而是直接改变 softmax 里的分数，进而改变总体最优策略。

### 2. 第一层：单轮最优解

#### 2.1 固定采样不能保证合理排名

论文把 IPO 看作将偏好矩阵聚合成概率分布的规则，并检查三个性质：

1. Condorcet-top：如果某回答两两击败所有其他回答，它应排第一。
2. Smith-top：最小支配集合中的回答都应高于集合外回答。
3. Order-preserving：若偏好本身有传递顺序，输出概率应保持该顺序。

结论是：无论事先固定哪一个采样分布，都存在使 IPO 违反这三个性质的偏好矩阵。若允许采样根据具体 $P$ 调整，则可以恢复 Condorcet-top 和 Smith-top 的存在性保证；但论文没有给出在未知 $P$ 下可直接运行的自适应采样算法，这一点被明确留作未来工作。

对于一般传递矩阵，甚至可能没有任何全支撑采样能保持完整顺序；对于更强的“强传递”结构，IPO 才能对任意采样保持顺序。

#### 2.2 更偏向强者的采样会放大策略尖锐度

当偏好强传递且满足论文的行优势/majorization 条件时，如果采样相对于基线进一步向高排名回答倾斜，相应的策略 logit 差会严格变大。这可能提升头部回答间的区分度，但也让输出分布更集中、降低多样性。

这个结论有严格前提，不能简化成“所有 on-policy 采样必然导致所有回答对的差距增大”。

### 3. 第二层：迭代动力学

单轮分析回答“给定采样后，最优解是谁”；迭代分析回答“这个最优解如果反过来决定下一轮数据和参考模型，长期会发生什么”。

论文引入两个反馈通道：

$$
\bm\pi_{\rm ref}^{(t)}
\propto
\bm\pi_t^\alpha\bm\pi_{\rm ref}^{1-\alpha},
$$

$$
\bm\mu_t=\lambda\bm\pi_t+(1-\lambda)\bm\pi_0.
$$

- $\alpha$ 控制参考模型有多大程度追随当前模型；$\alpha=1$ 表示完全自指。
- $\lambda$ 控制采样有多大程度来自当前模型；$\lambda=1$ 表示完全 on-policy。
- $\beta$ 控制每轮偏好更新的激进程度。

代入 IPO 显式最优解，得到 MRS-IPO 更新：

$$
\boxed{
\bm\pi_{t+1}
=\mathrm{softmax}\!\left(
\log\bm\pi_{\rm ref}^{(t)}+\beta P\bm\mu_t
\right)
}
$$

算法流程非常直接：

```text
当前策略 pi_t
   ├─几何混合固定参考（alpha）──> 本轮参考 pi_ref^(t)
   └─线性混合离线采样（lambda）─> 本轮采样 mu_t
                 │
                 └─计算 P mu_t，并按 beta 放大
                               │
                               v
                      softmax 得到 pi_(t+1)
                               │
                               └──进入下一轮
```

### 4. 两种长期失败模式

#### 4.1 循环偏好：策略持续振荡

若三个回答形成石头--剪刀--布式循环，当前策略改变采样后，“最有利的方向”会随策略一起旋转。论文给出的三动作构造中，均匀固定点在

$$
\alpha^2+\frac{a^2\beta^2\lambda^2}{3}>1
$$

时线性不稳定，邻近轨迹会持续绕行而不收敛。$\alpha$、$\beta$、$\lambda$ 和循环优势 $a$ 越大，越容易进入振荡区。

另一方面，对任意偏好矩阵，若

$$
\alpha+\frac{\beta\lambda}{2}
\left\|P-\frac12\mathbf1\mathbf1^\top\right\|_2<1,
$$

更新映射是压缩映射，因而有唯一内部固定点并从任意内部初始化收敛。这是保守的充分条件，不是必要条件。

#### 4.2 强传递偏好：熵坍缩

若偏好具有稳定的强弱顺序，问题不再是转圈，而是优势被反复累积。控制坍缩强度的关键比例是

$$
\frac{\beta\lambda}{1-\alpha}.
$$

$\alpha<1$ 时，固定参考仍能阻止数学上精确到顶点的坍缩，但该比例变大时，极限策略可以无限接近把全部概率放在第一名。$\alpha=1$ 时，论文证明熵最终单调下降，策略收敛到只选择第一名的确定性分布。

因此，多样的固定参考或离线数据可以减缓自强化，却未必能抵消长期累积的反馈。

### 5. DPO 为什么需要单独说明？

DPO 没有 IPO 那样的显式最优解，其最优策略通过一阶条件隐式定义。论文证明：DPO 的总体最优解对采样不敏感，当且仅当真实偏好恰好能由 BT 模型表示。否则，即使数据无限多，采样偏差也不会自动消失。

DPO 的 logit 集中结论只描述小扰动下的加权总体方向，不等同于 IPO 的逐回答、全局保证。MRS-DPO 的模拟也出现振荡和集中，但 IPO 与 DPO 的稳定阈值、以及 $\alpha,\beta,\lambda$ 的相对作用并不完全相同。

### 6. 实验如何验证？

作者使用 NVIDIA HelpSteer 的 35,331 条带多维评分的回答记录。对每个 prompt 取四个回答；对每一对回答随机选一个评价维度，将评分差通过 sigmoid 转成 $P_{ij}$。过滤后得到：

- 118 个循环偏好矩阵；
- 4,924 个强传递偏好矩阵。

每个 MRS-IPO 轨迹运行 3,000 轮。循环强度用策略坐标的时间平均方差度量，坍缩用末轮 Shannon 熵度量。28 张图均已在本地逐一视觉核验：循环矩阵在强反馈时出现持续旋转，强传递矩阵在强反馈时向单一回答集中；有限样本扰动会造成轨迹相位不同，使平均曲线错误地显得更平稳。

### 7. 应该怎样理解结论边界？

- 论文分析的是固定 prompt、有限候选集和总体偏好矩阵，不是完整 LLM 参数训练。
- 实验从 HelpSteer 评分构造偏好矩阵，并非真实部署中逐轮重新向人类收集反馈。
- 稳定性条件是充分条件；循环与坍缩定理各自依赖明确的偏好结构。
- 论文说明了风险机制，但没有证明所有在线 DPO/IPO 系统都会坍缩或振荡。
- 截至 2026-07-22，正文、arXiv 元数据、GitHub 精确题名/编号检索和公开网页检索均未找到官方代码仓库，因此当前工作区为 `paper-only`。

最值得带走的观点是：在非理想偏好下，采样不是被动的数据管道，而是目标函数的一部分；在迭代对齐中，它又成为动力系统的反馈增益。稳定训练需要同时控制参考刷新、on-policy 数据比例和更新强度，而不能只盯住单轮训练损失。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## How Sampling Shapes LLM Alignment: Summary

### Problem

Preference-optimization methods learn from sampled response pairs and usually regularize toward a reference policy. Prior analyses often treat the pair sampler and reference as fixed external choices. That abstraction misses two effects: outside an exact Bradley--Terry model, changing which pairs are sampled can change the population optimum; in iterative alignment, the current model may generate the next round's data and become the next reference, creating a self-reinforcing feedback loop.

### Contribution

The paper studies both effects through Identity Preference Optimization (IPO), with a complementary Direct Preference Optimization (DPO) analysis.

In the **one-shot** setting, IPO has the closed form

$$
\bm{\pi}^{\star}\propto
\bm{\pi}_{\mathrm{ref}}\odot\mathrm{softmax}(\beta P\bm{\mu}),
$$

which exposes exactly how sampling $\bm\mu$ changes the solution. No single fixed sampler makes IPO satisfy all three examined ranking desiderata (Condorcet-top, Smith-top, and order preservation), while a sampler adapted to the preference matrix can recover the first two. Under strong transitivity the ranking is sampler-robust, but moving sampling mass toward higher-ranked responses can enlarge logit gaps and reduce diversity under the paper's structural conditions.

In the **iterative** setting, the authors define MRS-IPO. The incumbent policy $\bm\pi_t$ is mixed geometrically into the next reference with strength $\alpha$ and affinely into the next sampler with strength $\lambda$; the next policy is the corresponding IPO optimum. This converts alignment into a discrete dynamical system rather than a sequence of unrelated static optimizations.

### Main findings

- With cyclic preferences, self-reinforcement can produce persistent policy oscillations. For a three-action cycle, the uniform fixed point is unstable when $\alpha^2+a^2\beta^2\lambda^2/3>1$.
- A conservative global contraction condition, $\alpha+(\beta\lambda/2)\lVert P-\tfrac12\mathbf1\mathbf1^\top\rVert_2<1$, guarantees convergence for arbitrary preference matrices.
- With strictly strongly transitive preferences, large $\beta\lambda/(1-\alpha)$ yields near-collapse; at $\alpha=1$, entropy eventually decreases to zero and the policy converges to the top response.
- DPO has the same central sampling dependence outside exact BT preferences, but its optimizer is implicit and several concentration/stability results are weaker than IPO's. The paper does not claim identical IPO and DPO thresholds.

### Evidence

Experiments construct $K=4$ matrices from NVIDIA HelpSteer's 35,331 scored responses, yielding 118 cyclic and 4,924 strongly transitive instances. Over 3,000-step simulated dynamics, cycle strength rises in stronger feedback/update regimes and terminal entropy falls in concentration regimes. All 28 figures were visually inspected. Finite-sample perturbation figures show that random phase differences can hide oscillations in averages and that collapse paths vary substantially across realizations.

### Interpretation and limits

The important distinction is:

- **One-shot optimum:** sampling selects which population policy is optimal for a fixed training round.
- **Iterative dynamics:** that selected policy changes future sampling and references, so small design choices accumulate into convergence, cycling, or collapse.

This is a theoretical mechanism study, not an end-to-end LLM fine-tuning benchmark. It fixes a prompt and finite candidate set, works primarily with population preference matrices and exact per-round optima, and constructs experimental matrices from HelpSteer scores rather than running a live human/model feedback system. The contraction condition is sufficient, not necessary, and the structural theorems should not be generalized beyond their assumptions.

### Reproducibility

**Paper-only.** No official implementation was linked in the paper or found through arXiv metadata, exact-title/arXiv-ID GitHub searches, or general web search as of 2026-07-22. The data source and matrix construction are described, but no runnable scripts, exact random seeds, or complete computational environment are available in this workspace. Reproducibility rating: **2/5**—the population equations and simulation protocol are unusually explicit, but the released executable implementation is `Not found`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
