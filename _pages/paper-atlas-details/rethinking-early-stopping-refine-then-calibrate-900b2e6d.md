---
layout: default
permalink: /paper-atlas/rethinking-early-stopping-refine-then-calibrate-900b2e6d/
title: "Rethinking_Early_Stopping_Refine_Then_Calibrate"
nav: false
wide: true
description: "这篇论文讨论的是概率分类器的早停与模型选择，属于机器学习和统计学习，不是生物信息学论文。它指出：验证集交叉熵同时混合了“模型能否区分类别”和“模型置信度是否准确”两件事，而这两件事往往不会在同一个训练轮次达到最好。既然置信度可以在训练后通过温度缩放修正，就不应让暂时性的校准误差过早终止训练。 论文提出的原则是： > 训练时选择区分能力最好的模型，训练后再校准概率。"
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
      <span>SIAM Journal on Mathematics of Data Science (to appear) · 2026</span>
    </div>
    <h1>Rethinking_Early_Stopping_Refine_Then_Calibrate</h1>
    <p>Rethinking Early Stopping: Refine, Then Calibrate</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/dholzmueller/probmetrics" target="_blank" rel="noopener noreferrer" aria-label="Open code for Rethinking_Early_Stopping_Refine_Then_Calibrate">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Rethinking Early Stopping：先提升区分能力，再做概率校准

### 先说结论

这篇论文讨论的是概率分类器的早停与模型选择，属于机器学习和统计学习，不是生物信息学论文。它指出：验证集交叉熵同时混合了“模型能否区分类别”和“模型置信度是否准确”两件事，而这两件事往往不会在同一个训练轮次达到最好。既然置信度可以在训练后通过温度缩放修正，就不应让暂时性的校准误差过早终止训练。

论文提出的原则是：

> 训练时选择区分能力最好的模型，训练后再校准概率。

实际做法几乎不改训练流程：每个 epoch 都在验证集上拟合一次温度缩放，用“温度缩放后的验证损失”作为早停指标；找到最小值对应的 checkpoint 后，再使用该温度输出最终概率。

### 为什么普通早停可能选错

设分类器 $f(x)$ 输出 $k$ 类概率，$Y$ 是 one-hot 标签，$\ell$ 是交叉熵或 Brier score 这样的严格 proper loss。令

$$
C=\mathbb E[Y\mid f(X)]
$$

表示在给定模型输出时真实的条件类别概率。proper loss 的风险可分解为

$$
\operatorname{Risk}(f)
=\underbrace{\mathbb E[d_\ell(f(X),C)]}_{\mathcal K_\ell(f)\text{：校准误差}}
+\underbrace{\mathbb E[e_\ell(C)]}_{\mathcal R_\ell(f)\text{：refinement 误差}}.
$$

这里：

- **校准误差 $\mathcal K_\ell$** 衡量模型报出的概率是否可信。例如所有报 80% 的样本是否真的约有 80% 正确。
- **refinement 误差 $\mathcal R_\ell$** 衡量模型输出包含多少类别信息。误差越小，说明模型越能把不同类别分开；即使它整体过度自信，排序和区分能力仍可能很好。

普通早停选择

$$
t_{\mathrm{risk}}=\arg\min_t\bigl[\mathcal K_\ell(f_t)+\mathcal R_\ell(f_t)\bigr].
$$

但训练后往往还会做温度缩放来降低 $\mathcal K_\ell$。如果 refinement 仍在改善，而校准已经开始恶化，普通验证损失会因为“以后本可修复”的校准问题而过早停止。论文 Figure 1 直接显示了这种轨迹：约 50 epoch 时总验证损失最低，但 refinement 一直到约 280 epoch 仍在下降。

### 核心理论：把 refinement 写成一次最优后处理

论文的关键贡献是 Theorem 3.4。对所有可测的概率重映射 $g:\Delta_k\to\Delta_k$，有

$$
\mathcal R_\ell(f)=\min_g\operatorname{Risk}(g\circ f),
$$

以及

$$
\mathcal K_\ell(f)
=\operatorname{Risk}(f)-\min_g\operatorname{Risk}(g\circ f).
$$

最优映射为

$$
g^*(q)=\mathbb E[Y\mid f(X)=q].
$$

这给出了非常清楚的解释：

- 对模型做最优概率校准之后，剩下的损失就是 refinement；
- 校准前后减少的损失就是校准误差。

因此，不必先用高维分箱去估计 $C$，也不必直接估计多分类校准误差。只要拟合一个后处理器，再计算处理后的 proper loss，就能得到 refinement 的估计。

### 从理论到可执行算法

有限验证集上不能对所有可测函数求最小值，否则会严重过拟合。论文把 $g$ 限制在一个低容量函数类 $\mathcal G$：

$$
\widehat{\mathcal R}_\ell(f)
=\min_{g\in\mathcal G}\frac1n\sum_{i=1}^n
\ell(g(f(x_i)),y_i).
$$

神经网络实验选择温度缩放：

$$
g_\beta(p)=\operatorname{softmax}(\beta\log p),
$$

如果直接使用 logits $z$，就是 $\operatorname{softmax}(\beta z)$。$\beta$ 是逆温度，只有一个标量参数，既能修正全局过度自信/不自信，又不容易在验证集上过拟合。

#### 完整流程

```text
训练集                         验证集
  |                              |
按原损失正常训练                 |
  |                              |
得到 f_1, f_2, ..., f_T --------+
  |                              |
每个 epoch 提取验证 logits z_t
  |
拟合一个 beta_t，使校准后验证损失最小
  |     softmax(beta_t * z_t)
  v
记录 score_t = 校准后的验证 proper loss
  |
选择 t* = argmin_t score_t
  |
恢复 f_t*，使用验证集拟合的温度做最终校准
  v
输出校准后的类别概率
```

要特别注意：模型仍然使用普通交叉熵训练。所谓“refine”不是在反向传播中加入一个新 loss，而是改变 checkpoint 选择规则。

### 温度缩放为什么足够快

对交叉熵而言，关于逆温度 $\beta$ 的目标是凸函数。代码没有沿用许多实现中的 L-BFGS 温度优化，而是对梯度求根。`probmetrics` 中直接计算

$$
\frac{\partial L}{\partial\beta}
=\frac1n\sum_i\left[
\sum_c z_{ic}\operatorname{softmax}(\beta z_i)_c-z_{i,y_i}
\right],
$$

然后在 $u=\log\beta\in[-16,16]$ 上二分 30 次，最后取 $\beta=\exp u$。直接源码见 `code/probmetrics/probmetrics/calibrators/temperature_scaling.py:18-27,57-62,106-122`。Figure 4 显示，这个实现处在速度和 logloss 的较优前沿，因此可以每个 epoch 都拟合一次。

### 代码中真正发生了什么

视觉实验代码的关键路径如下：

1. `Vision/utils.py:58-66` 使用普通交叉熵训练 ResNet-18 或 WideResNet。
2. `utils.py:68-91` 每个 epoch 收集验证集和测试集 logits。
3. `utils.py:93-105` 在全部验证 logits 上拟合 30 步二分温度缩放，并计算校准前后的指标。
4. `Vision/main.py:127-138` 分别按 raw logloss、Brier、分类误差、AUROC 和 `logloss/val_ts` 选择最佳 epoch。
5. `main.py:139-148` 对所选 epoch 报告验证集拟合温度之后的测试 logloss、Brier、ECE 和 smooth ECE。

因此 TS-refinement 对应代码里的 `logloss/val_ts`，而不是 ECE。ECE 是分箱校准指标，不能和理论分解中的 $\mathcal K_\ell$ 混为一谈。

### 高斯模型为什么能把“区分”和“置信度”拆开

论文考虑平衡二分类高斯混合：

$$
Y\in\{-1,1\},\qquad X\mid Y=y\sim\mathcal N(y\mu,\Sigma),
$$

以及逻辑回归预测 $f_w(x)=\sigma(w^\top x)$。定义模型相对 Bayes 方向 $w^*$ 的 expertise：

$$
a_w=\frac{\langle w,w^*\rangle_\Sigma}{\|w\|_\Sigma}.
$$

Proposition 6.1 表明，refinement 只依赖 $a_w$，而校准还依赖权重尺度 $\|w\|_\Sigma$。也就是说：

- 权重方向决定模型掌握了多少类别信息；
- 权重大小决定模型有多自信。

把 $w$ 乘以标量不会改变 expertise，却能改变 confidence。选择

$$
s=\frac{\langle w,w^*\rangle_\Sigma}{\|w\|_\Sigma^2}
$$

后，$w_s=sw$ 的校准误差为零而 refinement 不变。对 logits 乘标量正是温度缩放，所以在该模型假设下，“先选 refinement，再校准”不是经验口号，而是精确分离。

### 高维正则化逻辑回归分析

论文进一步研究

$$
\min_w\frac1n\sum_i\log(1+\exp(-y_iw^\top X_i))
+\frac\lambda2\|w\|^2
$$

在 $n,p\to\infty$ 且 $p/n\to r$ 时的行为。不同 $\lambda$ 可理解为正则化路径上的不同模型选择点。理论给出 $w_\lambda$ 的渐近均值和协方差，再计算 expertise、confidence、校准误差与 refinement 误差。

`RefineThenCalibrate-Theory/utils.py:90-168` 数值求解 $(\eta,\gamma,\tau)$ 非线性系统并积分误差；`LR_expe.py:27-157` 用 $n=2000$、$p/n=0.5$、50 个随机种子对照理论；`LR_heatmap.py:8-92` 扫描谱形状、问题难度和维样本比。它们实现的是理论公式的数值实验，不是定理证明。

### 实验如何支持结论

#### 计算机视觉

论文在 CIFAR-10、CIFAR-100、SVHN 上训练 ResNet-18 和 WideResNet，每种组合 10 次、300 epoch，留 10% 训练集做验证。最清晰的改进出现在 CIFAR-100：

- ResNet-18：raw-logloss 早停后的测试 logloss 为 $1.015$，TS-refinement 为 $0.983$；
- WideResNet：从 $0.798$ 降到 $0.771$。

其他数据集更多是小幅改进或误差范围内相近，因此论文证据支持“更稳定地取得低损失”，不支持“每个任务都大幅提升”。

#### 表格数据

论文比较 RealMLP、普通 MLP 和 XGBoost，在 65 个至少 10,000 样本的数据集上，TS-refinement 与五折版本整体呈现有利的 logloss 分布。小数据集噪声更大，甚至存在显著变差的离群点。这说明验证集容量是方法的重要条件。

所以这部分只能由论文正文和图像支持，不能声称已由本地源码逐行复现。

#### 理论图

Figure 7 中渐近理论曲线和 50 次模拟高度重合，并在该设置预测 refinement 选择带来约 2% 的校准后交叉熵下降。Figure 8 显示，校准可以先达到最优，refinement 也可以先达到最优；当两者相隔较远时，理论收益最高约 25%。这是一类高斯高维模型下的结论，不是任意深度网络的普适保证。

### 什么时候可能失效

- **验证集太小：** 同一验证集既拟合温度又评估损失，会有乐观偏差。论文建议使用交叉验证、集成或正则化 calibrator。
- **TS 表达力不够：** 单一标量只能修正整体置信度，无法处理任意类别依赖或局部校准错误。
- **校准器太复杂：** $\mathcal G$ 越大，越接近理论 $g^*$，但有限样本过拟合越严重。
- **区分信息已经丢失：** 后处理只能重新标定已有概率，无法恢复被模型压缩掉的类别信息。
- **实现边界：** Appendix D 说主实验在验证准确率 100% 时加入 Laplace smoothing，但直接检查的基础 calibrator 和视觉调用点没有显式应用该混合项。这是一个需要复现实验时进一步确认的差异。

### 如何理解这篇论文的贡献

它不是提出新的校准器，而是重新定义校准器在训练流程中的角色：校准器不只用于改善最终概率，也可作为“把校准误差从模型选择指标里消掉”的工具。其核心思想可概括为：

$$
\text{模型选择应该优化校准之后仍无法修复的部分。}
$$

对神经网络，这一原则落成每个 epoch 一次的一维优化；对 boosting、正则化路径或超参数搜索，也可以用相同思路选择迭代次数或配置。它最适合验证数据充足、最终本就需要概率校准、且训练过程中的置信度漂移明显的概率分类任务。

### 证据与缺口

- 已核验：1142 行 arXiv 正文、全部 14 张本地图像、三套官方代码快照的核心源码。
- 代码匹配度：核心 TS estimator、视觉实验和理论数值实现为高匹配。
- **Not found：** 当前 `code source` 中的表格实验 driver、生成 CSV、训练 checkpoint、形式化证明代码。
- **MISSING：** 正式出版社 DOI 和最终卷期信息；当前有依据的状态是 *SIAM Journal on Mathematics of Data Science*（to appear）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Rethinking Early Stopping: Refine, Then Calibrate

### At a glance

This paper revisits early stopping for probabilistic classifiers. Validation cross-entropy is the sum of calibration error and refinement error, yet those terms need not be minimized at the same epoch. Standard early stopping can therefore select a compromise checkpoint even when calibration will later be repaired post hoc. The proposed rule is simple: choose the checkpoint with the smallest validation loss **after** fitting a low-capacity calibrator, then retain that calibration for final prediction—“refine, then calibrate.”

The work is machine learning/statistical learning, not bioinformatics. Its isolated genomics and histopathology example describes one possible spectral regime; it is not the paper's application domain.

### What is new

The theoretical contribution is a variational form of the proper-loss calibration–refinement decomposition. For a probabilistic classifier $f$ and proper loss $\ell$,

$$
\mathcal R_\ell(f)=\min_g\operatorname{Risk}(g\circ f),
\qquad
\mathcal K_\ell(f)=\operatorname{Risk}(f)-\min_g\operatorname{Risk}(g\circ f),
$$

where $g$ ranges over measurable probability remappings. Thus, risk after optimal recalibration equals refinement, while the loss reduction from recalibration equals calibration error.

The practical method restricts $g$ to temperature scaling and evaluates

$$
\widehat{\mathcal R}_{\ell,\mathrm{TS}}(f_t)
=\min_{\beta>0}\frac1n\sum_i
\ell(\operatorname{softmax}(\beta z_t(x_i)),y_i)
$$

at every checkpoint. The epoch minimizing this calibrated validation loss is selected. The classifier still trains with its ordinary loss; only model selection changes.

### Why it can work

Raw validation loss penalizes both loss of discrimination and mis-scaled confidence. If refinement continues improving while calibration worsens, raw loss stops too soon. Temperature scaling changes confidence without changing class ranking, so calibration can be postponed until after a more informative checkpoint has been chosen.

In a balanced Gaussian mixture, the paper formalizes this distinction: refinement depends on a linear model's alignment with the Bayes direction (“expertise”), while calibration also depends on weight magnitude (“confidence”). Rescaling the weights—exactly temperature scaling—can set calibration error to zero while preserving refinement. A high-dimensional ridge-logistic-regression analysis then predicts distinct regularization optima across broad problem regimes.

### Evidence

- **Vision:** ResNet-18 and WideResNet were trained for 300 epochs on CIFAR-10, CIFAR-100, and SVHN, ten runs each. TS-refinement is most visibly helpful on CIFAR-100: ResNet-18 test logloss changes from $1.015$ with raw-logloss stopping to $0.983$, and WideResNet from $0.798$ to $0.771$, with all reported models calibrated by TS. On CIFAR-10 and SVHN, results are mostly smaller gains or ties.
- **Tabular:** RealMLP, MLP, and XGBoost were compared on 65 datasets with at least 10,000 samples. TS-refinement and a five-fold version generally give favorable logloss distributions; performance is noisier on small datasets.
- **Theory:** In the Figure 7 Gaussian example, asymptotic curves closely track 50-seed simulations and predict a 2% post-calibration cross-entropy gain. The parameter scan reports gains up to 25% where calibration and refinement minima are far apart.
- **Figures:** all 14 local PNGs were read directly. They support the separated minima, later stopping under refinement metrics, aggregate benchmark behavior, and validation-size caveat.

### Relation to prior work

Classical decompositions for proper scores go back to Sanders (1963), Murphy (1973), and Bröcker (2009), but the paper argues they lacked this variational interpretation. Guo et al. (ICML 2017) established temperature scaling as a simple neural-network calibrator. Ranjan et al. (2024) observed gains from selecting epochs after post-hoc transformations; this paper supplies the refinement interpretation and extends it across proper losses and a high-dimensional model.

### Reproducibility assessment

**Rating: 4/5 for the covered source surfaces.** Three official fixed-commit repositories are present. `probmetrics` exactly implements the 30-step bisection temperature scaler; the vision repository fits it per epoch and selects `logloss/val_ts`; the theory repository numerically solves the shifted-Beta fixed-point system and reproduces the main theory sweeps. The correspondence is high for the estimator, vision path, and theoretical numerics.

Important boundaries remain:

- the broad `pytabkit` tabular driver is **Not found** in the acquired `code source` snapshot;
- generated CSVs and trained checkpoints are **Not found**;
- proofs are paper mathematics, not code artifacts;
- the paper says Laplace smoothing is used in main experiments at perfect validation accuracy, but it is not visible in the inspected base calibrator/vision call site;
- experiments were source-audited, not rerun;
- the publisher DOI and final issue metadata are **MISSING**; the supported status is *SIAM Journal on Mathematics of Data Science* (to appear).

### Bottom line

The paper's strongest idea is not “calibrate better,” but “do not let a repairable calibration error decide when learning should stop.” TS-refinement turns that principle into a nearly drop-in selection rule. Its low overhead and direct code support make it credible for classifiers with adequate validation data, while the finite-sample bias of same-set calibration and the limited expressiveness of scalar TS define the main practical caution.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
