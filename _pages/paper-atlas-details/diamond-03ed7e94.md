---
layout: default
permalink: /paper-atlas/diamond-03ed7e94/
title: "Diamond"
nav: false
wide: true
description: "机器学习模型可以拟合复杂的特征关系，但常见解释方法往往只给出单个特征的重要性，或者把两个边际上都重要的特征误认为存在相互作用。这样的排序结果还缺少一个可解释的截断规则：用户很难知道选出的相互作用中有多少可能是假的。Diamond 的目标是在已经训练（或准备训练）的预测任务上，发现真正的非加性特征相互作用，并将交互层面的假发现率（FDR）控制在用户指定的 q 水平。"
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
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>Diamond</h1>
    <p>Error-controlled non-additive interaction discovery in machine learning models</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/batmen-lab/diamond" target="_blank" rel="noopener noreferrer" aria-label="Open code for Diamond">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Diamond 方法详解：带错误率控制的非加性相互作用发现

### 1. 要解决的问题

机器学习模型可以拟合复杂的特征关系，但常见解释方法往往只给出单个特征的重要性，或者把两个边际上都重要的特征误认为存在相互作用。这样的排序结果还缺少一个可解释的截断规则：用户很难知道选出的相互作用中有多少可能是假的。Diamond 的目标是在已经训练（或准备训练）的预测任务上，发现真正的**非加性**特征相互作用，并将交互层面的假发现率（FDR）控制在用户指定的 $q$ 水平（论文 `paper.md:25-37,54-71`）。

这里的非加性是函数层面的概念：如果模型函数不能写成分别排除某个特征的子函数之和，就称该特征集合产生非加性相互作用。例如 $x_i x_j$ 不能拆成两个单变量函数之和；而 $\log(x_i x_j)=\log(x_i)+\log(x_j)$ 在对数空间中是可加的（`paper.md:54-57`）。

论文讨论的相关解释方法包括 Neural Interaction Detection（ICLR 2018）、Neural Interaction Transparency（NeurIPS 2018）、TreeSHAP（*Nature Machine Intelligence*, 2020）、Shapley-Taylor interaction（ICML 2020）和 Integrated Hessians（*JMLR*, 2021）。它们可以提供相互作用分数，但论文认为原始分数不一定去除了边际效应，也没有直接提供交互层面的 FDR 控制（`paper.md:31,350-364`）。

### 2. Diamond 的核心想法

Diamond 将三个组件串起来：

1. **Model-X knockoff 控制变量。** 为每个原始特征生成一个 knockoff 特征，使其模仿原始特征的依赖结构，同时在给定原始特征后与响应独立。
2. **在增强输入上训练并解释模型。** 把 $X$ 和 $\widetilde X$ 沿特征轴拼接，使用 MLP、Transformer、KAN、树模型或因子分解模型等，再计算边际分数 $e_i$ 与成对分数 $e_{ij}$。
3. **非加性蒸馏和 FDR 过滤。** 从 $e_{ij}$ 中回归掉两个边际效应和特征对偏差，用残差作为非加性分数；随后比较原始-原始、原始-knockoff 和 knockoff-knockoff 对的数量，选择满足目标 $q$ 的阈值。

```text
X, Y
  -> 生成 X_tilde
  -> 拼接 [X, X_tilde]
  -> 训练预测模型
  -> 计算 e_i 与 e_ij
  -> 倾向得分 + GAM 去除边际/偏差
  -> 获得 |残差| 作为非加性分数
  -> knockoff 计数估计 FDR，筛选原始-原始相互作用
```

图 1 的实际图像也显示了这条路径：knockoff 生成、增强模型输入、后验解释、残差校准和按 FDR 排序（`figure_analysis.md`；原图 `images/figure_01.png`）。

### 3. 数学定义和计算步骤

#### 3.1 Knockoff 条件

论文要求 knockoff 满足交换性和条件独立性：对任意特征子集交换 $X_j$ 与 $\widetilde X_j$ 后联合分布不变，并且

$$
\widetilde{\bf X}\perp\!\!\!\perp {\bf Y}\mid {\bf X}.
$$

高斯情形的条件分布见论文 Eq. 2-3（`paper.md:219-248`）。实际实验还比较 KnockoffsDiagnostics、KnockoffGAN、Deep knockoffs、VAE knockoffs，并故意测试逐特征置乱得到的无效 knockoff（`paper.md:103-120,314-317`）。

代码中的 `sim.py` 和 `real.py` 都先生成 `X_knockoff`，再执行 `np.concatenate((X, X_knockoff), axis=1)`（`diamond/src/sim.py:75-103`; `diamond/src/real.py:53-68`）。

#### 3.2 模型与解释器

论文使用 MLP、CNN、FT-Transformer、KAN、XGBoost、LightGBM 和 factorization machine。DNN/KAN 可以用 Expected Hessian 或 Integrated Hessian；树模型使用 TreeSHAP；FM 直接使用学习到的二阶系数（`paper.md:296-317`）。

代码的 DeepPINK 输入层为每个原始-knockoff 对学习权重，再计算

$$
z_j=Z_jX_j+Z_{j+p}\widetilde X_j,
$$

然后让 $z$ 进入 MLP、CNN 或 Transformer（`diamond/src/models/DeepPink.py:268-331`）。对于 `ig`，PathExplainer 使用零 baseline；对于 `eg`，使用经验数据作为 baseline 并启用 expectation（`diamond/src/sim.py:123-155`; `diamond/src/real.py:123-199`）。

一个重要的代码-论文差异是配置：论文主文写的是依赖 $p$ 的 MLP 宽度和六层 Transformer，而当前代码使用固定 MLP `[140,100,60,20]`，Transformer 深度为 2。补充材料在本地缺失，因此无法判断是否存在实验特定配置（`paper.md:302`; `diamond/src/models/DeepPink.py:288-307`）。

#### 3.3 非加性蒸馏

论文将成对解释分数分解为

$$
e_{ij}=s_{ij}+g_i(e_i)+g_j(e_j)+b(I_{ij})+\varepsilon_{ij},
$$

其中 $s_{ij}$ 是希望保留的非加性效应，$g_i,g_j$ 是边际效应，$b(I_{ij})$ 是不依赖标签的特征对偏差，$\varepsilon_{ij}$ 是噪声（Eq. 4）。通过加权回归估计 nuisance 项：

$$
\min_{b,g_1,g_2,\ldots}\sum_{i<j}w_{ij}
\left\|e_{ij}-g_i(e_i)-g_j(e_j)-b(I_{ij})\right\|^2.
$$

论文用 logistic regression 估计倾向概率，并用 pyGAM 的广义加性模型拟合（Eq. 5；`paper.md:254-276`）。

当前代码的 `fdr_control.py` 具体构造边际 attribution 编码、pair identity 编码和随机高斯投影；随后拟合 `LogisticRegression`，把稳定化 IPTW 的倒数作为 `LinearGAM` 权重，最后以 `abs(obs - pred)` 作为 calibrated interaction（`diamond/src/fdr_control.py:160-199`）。因此，代码确实实现“残差蒸馏”的计算表面，但 Eq. 5 的权重和 $b(I_{ij})$ 参数化只能标记为 **Partial**，不能声称逐项等同。

#### 3.4 交互 FDR 阈值

将残差分数按阈值 $t$ 排序。论文定义 $\mathcal K$ 为至少含一个 knockoff 的相互作用集合，$\mathcal{KK}$ 为含两个 knockoff 的集合，并使用

$$
T=\min\left\{t\in\mathcal T:
\frac{|\{j:\Gamma_j\ge t,j\in\mathcal K\}|-2|\{j:\Gamma_j\ge t,j\in\mathcal{KK}\}|}
{|\{j:\Gamma_j\ge t,j\notin\mathcal K, j\notin\mathcal{KK}\}|}\le q\right\}.
$$

代码把 pair 分成 `TT`（原始-原始）、`TD`（恰好一个 knockoff）和 `DD`（两个 knockoff），所以分子中的 $|K|-2|KK|$ 可化为 `TD_count-DD_count`（`paper.md:279-293`; `diamond/src/models/model_utils.py:250-275`）。

但 `get_selected_interactions` 不是 Eq. 6 的逐字实现：它额外使用绝对值、把估计裁剪到 $[0,1]$、维护递增的 running maximum、在估计超过 $q$ 时提前停止，并在只有一个原始选择且没有 knockoff 选择时清空结果（`diamond/src/models/model_utils.py:263-302`）。这部分必须保留为 **Partial**，而不是 Exact。

### 4. 输出和如何运行

`sim.py` 或 `real.py` 每个 seed 先写 JSON，其中包含 attributions、interactions、true/false pairs 以及 pair 类型。随后独立运行 `fdr_control.py`，生成 `fdr_control/attributions.csv`、`interactions.csv` 和 `fdr_power.csv`。两个示例 notebook 会顺序调用训练、FDR 控制和可视化，但训练脚本本身不会自动调用 FDR 控制。

仓库提供 `environment.yml`、`data.zip`、`example/simulation.ipynb` 和 `example/real.ipynb`，但需要从源码安装 xLearn。当前分析没有创建环境、解压数据或运行实验，因此依赖兼容性和图表复现尚未验证。

### 5. 论文结果与图像证据

- **模拟数据：** 十个函数，$n=20{,}000$、$p=30$、20 个随机种子，目标 $q=0.2$。图 2 中校准后的 FDR 柱形大多位于 0.2 目标线下方，而未校准和三个 baseline 显著超出目标；MLP、FT-Transformer 通常具有更高 power。
- **Knockoff/解释器稳健性：** 图 3 显示多个 knockoff 和重要性测量组合仍保持低 FDR；逐特征置乱的无效 knockoff 虽然 FDR 低，但 power 几乎为零，说明保守性伴随发现能力损失。
- **糖尿病进展：** 图 4 的 BMI-STL 在 MLP、LightGBM、XGBoost 中重复出现；FT-Transformer 给出血压-HDL 和年龄-性别等其他候选。
- ***Drosophila* enhancer：** 图 5 中 Diamond 的前五候选与作者提供的物理相互作用清单有明显重叠，Snail-Twist 的局部图形呈抑制模式。
- **死亡率：** 图 6 中 Diamond+MLP 的候选较稀疏，而 baseline 产生密集低阈值云；前十候选中三项有直接文献支持。

真实数据中的星标和 PubMed 标注是作者提供的文献/ curated reference 证据，不是本地分析独立验证的因果真值。论文也提醒，直接相互作用和 transitive interaction 无法区分（`paper.md:192-204`）。

### 6. 学习时应记住的边界

1. Diamond 控制的是选中集合的交互 FDR，不是因果效应或生物机制的证明。
2. 关键假设依赖 knockoff 质量、预测模型质量和交互重要性测量；模型越弱，power 可能越低。
3. 非加性蒸馏是必要的，但当前代码对 Eq. 5/6 增加了主文未写出的工程细节。
4. 补充材料、完整 baseline 脚本、五折模型选择流程和自动化测试在本地没有找到，属于明确的 `MISSING` / `Not found` 证据缺口。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Diamond: Error-Controlled Non-Additive Interaction Discovery

### Problem

Machine-learning interpretation methods can rank feature pairs, but a high pair score does not necessarily represent a true non-additive interaction. Two individually important features can receive a large interaction score even when their effects are additive. Existing methods also generally leave the selection cutoff to the user and can be unstable under small perturbations, so a ranked list alone does not quantify how many selected interactions are likely to be false (`paper.md:25-34`).

Representative prior methods include Neural Interaction Detection (ICLR 2018), Neural Interaction Transparency (NeurIPS 2018), TreeSHAP (*Nature Machine Intelligence*, 2020), Integrated Hessians (*Journal of Machine Learning Research*, 2021), and Shapley-Taylor interactions (ICML 2020). These methods provide useful interaction scores, but Diamond's premise is that their raw scores neither isolate non-additivity reliably nor supply interaction-level FDR control (`paper.md:31,350-364`).

### Proposed Method

Diamond combines three ideas:

1. Generate model-X knockoff features that mimic the dependence structure of the original features while acting as response-independent controls.
2. Train a selected ML model on the augmented matrix $[X,\widetilde X]$ and obtain marginal and pairwise importance scores using a compatible interpretation method.
3. Distil non-additive effects by regressing pair scores on marginal effects and pair-specific bias, then use original/knockoff pair counts to choose an interaction-score threshold at a target FDR.

The key innovation is the distillation step. The paper models a reported pair score as a mixture of the desired non-additive effect, two marginal effects, feature-pair bias, and noise. A propensity-weighted generalized additive model estimates the nuisance terms; the residual becomes the interaction score used for FDR estimation (`paper.md:251-293`).

```text
X, Y -> knockoffs X_tilde -> train on [X, X_tilde]
     -> marginal and pair importance
     -> residual non-additivity calibration
     -> knockoff-count FDR threshold
     -> selected original-original interactions
```

Diamond is designed to wrap multiple model families and explainers rather than replace them. The paper studies MLP, CNN, FT-Transformer, KAN, XGBoost, LightGBM, random forest, and factorization machines with Expected Hessian, Integrated Hessian, TreeSHAP, or model-specific scores (`paper.md:296-317`).

### Evaluation

#### Simulations

The main benchmark contains ten nonlinear simulation functions with $n=20{,}000$, $p=30$, 20 random seeds, and target FDR $q=0.2$. The paper compares Diamond across seven model families and against permutation $P$ values with Benjamini-Hochberg or Benjamini-Yekutieli correction and a maximum feature-wise FDR heuristic.

Figure 2 shows the central result: without calibration, FDR is far above 0.2 for most model/function combinations; with calibration, the plotted mean FDR remains at or below the target while retaining useful AUROC and power. The three baselines also fail to control interaction FDR in the displayed experiments. MLP and FT-Transformer generally have greater power than CNN and factorization machines, demonstrating that error control does not remove dependence on model quality.

Figure 3 shows similar empirical FDR control across KnockoffsDiagnostics, KnockoffGAN, Deep Knockoffs, VAE knockoffs, Expected Hessian, Integrated Hessian, and a model-specific measure. Independently permuted invalid knockoffs also yield low plotted FDR but nearly zero power, so this result is best read as conservatism under severe misspecification, not validation of arbitrary knockoff generators.

#### Real Data

- **Diabetes progression:** 442 patients and ten standardized baseline variables. BMI-serum triglyceride level is selected across MLP, LightGBM, and XGBoost; FT-Transformer reports blood-pressure/high-density-lipoprotein and age/sex pairs (`paper.md:123-143`).
- ***Drosophila* enhancers:** 7,809 sequences with 23 transcription factors and 13 histone modifications. Among the top five interactions, the paper reports overlap with the curated physical-interaction list for three MLP/tree pairs, four FM pairs, and all five FT-Transformer pairs. Snail-Twist is interpreted as a repressive interaction (`paper.md:146-169`).
- **Mortality:** 14,407 NHANES/NHEFS participants with 35 clinical/laboratory variables before one-hot expansion. Three of the top ten MLP interactions have direct literature support, including sex-sedimentation rate and creatinine-blood urea nitrogen (`paper.md:172-189`).

These real-data findings are scientific hypotheses and plausibility checks, not causal or complete ground-truth validation. The paper explicitly states that Diamond cannot distinguish direct interactions from transitive ones (`paper.md:201`).

### Limitations

- Diamond tends to overestimate FDR and lose power.
- Interaction recovery depends on the predictive model and importance measure.
- The method cannot distinguish direct, mediated, transitive, or causal relationships.
- The study primarily treats pairwise interactions; higher-order search grows combinatorially.
- Main-paper evidence is empirical. The locally available source does not include the referenced supplementary derivations and experiments.

### Reproducibility and Code-Paper Match

**Reproducibility rating: 3/5 (medium).** The paper provides public code, a pinned repository commit in this workspace, an environment file, two runnable-style notebooks, and a bundled data archive. The core source implements augmented original/knockoff training, several model/explainer branches, residual GAM calibration, interaction-type counting, and CSV result generation.

The overall code-paper fidelity is **medium**:

- **Matched:** original/knockoff augmentation, DeepPINK-style pair coupling, Path-Explain/TreeSHAP/FM scoring, residual calibration, and original-vs-knockoff selection surfaces.
- **Partial:** Eq. 5 weighting and pair-bias representation; Eq. 6 thresholding; model architectures; real-data repeat aggregation.
- **Not found:** fivefold model-selection workflow, full permutation/BH/BY baseline pipeline, and automated tests for the primary workflow.
- **Code concern:** the real-data DNN branch computes task-specific losses but passes MSE to its training wrapper; this was source-verified but not executed.
- **MISSING:** local supplementary Markdown/PDF and supplementary figures.

The example notebooks connect training, FDR control, and visualization, but they are short demos rather than complete scripts for reproducing every figure. No environment setup or experiment was run during this analysis, so runtime reproducibility remains unverified.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
