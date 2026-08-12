---
layout: default
permalink: /paper-atlas/instability-computational-efficiency-statistical-accuracy-18b58cdb/
title: "Instability_Computational_Efficiency_Statistical_Accuracy"
nav: false
description: "许多统计估计量不是一次算出来的，而是反复应用样本算子 Fn： 总体算子 F 表示无限样本时的理想更新，\\theta^\\star 是其不动点。有限样本使 Fn 偏离 F。论文关心两个问题：迭代多少次才能到达统计误差下限？一个对样本扰动“不稳定”的算法，是否仍可能比稳定算法更值得使用？ 第一轴是总体算法的收敛速度：FAST(\\kappa) 表示几何收敛，误差近似按 \\kappa^t 下降；"
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
      <span>Journal of Machine Learning Research · 2025</span>
    </div>
    <h1>Instability_Computational_Efficiency_Statistical_Accuracy</h1>
    <p>Instability, Computational Efficiency and Statistical Accuracy</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2005.11411" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法详解：不稳定性、计算效率与统计精度

### 核心问题

许多统计估计量不是一次算出来的，而是反复应用样本算子 $F_n$：

$$
\theta_n^{t+1}=F_n(\theta_n^t).
$$

总体算子 $F$ 表示无限样本时的理想更新，$\theta^\star$ 是其不动点。有限样本使 $F_n$ 偏离 $F$。论文关心两个问题：迭代多少次才能到达统计误差下限？一个对样本扰动“不稳定”的算法，是否仍可能比稳定算法更值得使用？

### 方法的两个坐标轴

第一轴是总体算法的收敛速度：**FAST($\kappa$)** 表示几何收敛，误差近似按 $\kappa^t$ 下降；**SLOW($\beta$)** 表示误差近似按 $t^{-\beta}$ 下降。

第二轴是经验算子相对总体算子的扰动：

$$
\|F_n(\theta)-F(\theta)\|\lesssim r^\gamma\varepsilon(n,\delta),
$$

其中 $r=\|\theta-\theta^\star\|$。若 $\gamma\ge0$，靠近目标时扰动不增大，称为稳定；若 $\gamma<0$，靠近目标时扰动反而放大，称为不稳定。这里的“不稳定”是局部、定量的定义，并不等于算法必然失败。

### 推导流程

```text
构造样本算子 F_n 与总体算子 F
          |
确定 F 是 FAST(kappa) 还是 SLOW(beta)
          |
确定 F_n-F 是 STA(gamma) 还是 UNS(gamma)
          |
用分 epoch 的局部化论证平衡：
总体优化误差  vs.  累积样本扰动
          |
得到最终统计半径、所需迭代次数和有效初始化区域
```

关键不是单独追求最快收敛或最强稳定性，而是平衡两者。典型地，当 $\varepsilon\asymp n^{-1/2}$ 时，慢但稳定的更新可以在 $n^{1/2}$ 次迭代后达到 $n^{-1/4}$；快但不稳定的 Newton 更新也能达到 $n^{-1/4}$，却只需 $O(\log n)$ 次。

### 三类实例

- **过指定高斯混合**：EM 是慢收敛且稳定的，约需 $\sqrt n$ 次迭代；Newton 是快收敛但不稳定的，约需 $\log n$ 次。二者统计误差都是 $n^{-1/4}$（多维时为 $(d/n)^{1/4}$）。
- **非线性回归/弱信号相位恢复**：当 $g(x)=x^{2p}$、$\theta^\star=0$ 时，梯度下降、Newton 和三次正则 Newton 都达到 $n^{-1/(4p)}$，但迭代数分别为 $n^{(2p-1)/(2p)}$、$\log n$ 和 $n^{(4p-3)/(2(4p-1))}$。$p=1$ 时即 $n^{1/2}$、$\log n$、$n^{1/6}$。
- **信息性无响应**：同样展示稳定梯度法与不稳定 Newton 法在统计精度接近时的计算差异。

### 如何理解结论

论文不是说 Newton 永远优于梯度下降。保证是局部的：需要足够样本、统一扰动界、正确的初始化球或环带，并确保后续迭代不离开受控区域。图 5 明确展示了初始化太靠近奇异点时 Newton 可能跳到另一个吸引域。此外，Newton 每步需要 Hessian 和矩阵求逆；高维下实际总成本可能抵消迭代数优势。

### 实验与复现边界

六幅图支持理论缩放：相同统计误差斜率下，Newton 的迭代数增长远慢于 GD/EM。未在 JMLR 页面、全文、arXiv、GitHub 精确检索或 Papers with Code 找到作者官方代码，因此当前工作区为 paper-only；精确实验脚本、随机种子和实现细节标记为 `Not found`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Paper Summary

### What problem does it solve?

This JMLR 2025 theory paper studies iterative statistical estimators as empirical fixed-point maps $F_n$. Standard population-to-sample analyses mainly cover stable algorithms. That leaves a puzzle in singular models: Newton-type algorithms may be locally unstable to sampling perturbations yet reach the same statistically optimal radius as stable first-order methods in far fewer iterations.

### Main contribution

The authors classify the population operator by geometric **FAST($\kappa$)** or inverse-polynomial **SLOW($\beta$)** convergence and classify its empirical perturbation by **STA($\gamma$)** or **UNS($\gamma$)** scaling. An epoch-based localization argument balances population optimization error against sample perturbation, yielding explicit statistical-radius and iteration-complexity bounds. The framework covers slowly converging stable operators and both fast and slow unstable operators, complementing earlier fast/stable theory.

The central insight is that stability and computational speed are distinct axes. Instability worsens how close empirical iterates can safely approach a singular fixed point, but sufficiently fast population contraction can compensate. In canonical cases with sampling noise $\varepsilon\asymp n^{-1/2}$, stable gradient/EM updates and unstable Newton updates both reach $n^{-1/4}$ error, while the former require a polynomial number of iterations and Newton requires $O(\log n)$.

### Evidence and applications

The theory is specialized to informative non-response, over-specified symmetric Gaussian mixtures, and non-linear regression with $g(x)=x^{2p}$ in the weak-signal regime. For $p=1$, gradient descent, cubic-regularized Newton, and Newton all attain $n^{-1/4}$ statistical error, but require respectively $n^{1/2}$, $n^{1/6}$, and $\log n$ iterations up to constants/log factors. Mixture-model experiments similarly show EM taking roughly $\sqrt n$ iterations while Newton grows much more slowly, with both showing the predicted $n^{-1/4}$ error slope. The paper also proves general sharpness results and demonstrates that uncontrolled instability can send Newton iterates to another fixed point.

### Assumptions and limitations

The guarantees are local and depend on population Lipschitz/convergence assumptions, uniform high-probability perturbation bounds, adequate sample size, and suitable initialization. Unstable methods often require an annulus that excludes a neighborhood of the singular fixed point and an invariance condition for later iterates. Theoretical iteration counts do not alone determine wall-clock cost: Newton steps require Hessians/inverses, and dimension-dependent costs matter. Simulations illustrate scaling rather than serving as an extensive benchmark.

### Reproducibility

The official JMLR PDF was converted with MinerU hybrid high effort after the older arXiv version lacked structured HTML. All six numbered figures (10 linked panel images) were visually inspected. No official code or experiment repository was found across the JMLR page/full text, arXiv, exact-title and arXiv-ID GitHub searches, and Papers with Code. The workspace is therefore **paper-only**: theorem statements and plots are reproducible from the source, but the authors' exact simulation scripts and random seeds are `Not found`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
