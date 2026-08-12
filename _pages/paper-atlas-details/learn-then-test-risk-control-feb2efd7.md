---
layout: default
permalink: /paper-atlas/learn-then-test-risk-control-feb2efd7/
title: "Learn_Then_Test_Risk_Control"
nav: false
description: "一个已经训练好的模型通常还需要设置阈值：分类器何时拒答、预测集合放多少标签、分割掩膜从什么概率开始保留。直接在验证集上选表现最好的阈值，只能说明样本内效果好，不能保证部署后的总体错误率一定低于用户指定的上限。 Learn Then Test（LTT）在不重新训练基础模型的情况下，用一份独立同分布的校准数据，为这些后处理参数提供显式的有限样本风险保证。"
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
      <span>The Annals of Applied Statistics · 2025</span>
    </div>
    <h1>Learn_Then_Test_Risk_Control</h1>
    <p>Learn then test: Calibrating predictive algorithms to achieve risk control</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1214/24-AOAS1998" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Learn Then Test 方法详解

### 它解决什么问题

一个已经训练好的模型通常还需要设置阈值：分类器何时拒答、预测集合放多少标签、分割掩膜从什么概率开始保留。直接在验证集上选表现最好的阈值，只能说明样本内效果好，不能保证部署后的总体错误率一定低于用户指定的上限。

Learn Then Test（LTT）在不重新训练基础模型的情况下，用一份独立同分布的校准数据，为这些后处理参数提供显式的有限样本风险保证。它不仅能处理覆盖率，还能处理 FDR、选择性分类错误、条件 MSE、OOD 误拒绝率、IoU 和召回率等风险；参数可以是多维的，风险也不必关于参数单调。

### 核心思想：把“选阈值”改写成“拒绝不安全假设”

给定候选网格 $\Lambda=\{\lambda_1,\ldots,\lambda_N\}$，每个 $\lambda_j$ 定义一个后处理规则 $T_{\lambda_j}$。对风险

$$
R(\lambda)=\mathbb E[L(T_\lambda(X),Y)]
$$

构造原假设

$$
H_j:R(\lambda_j)>\alpha.
$$

这里原假设表示“这个参数不安全”。如果有足够证据拒绝 $H_j$，就把 $\lambda_j$ 放入认证集合 $\widehat\Lambda$。

```text
预训练模型 + 候选后处理参数 + 独立校准集
                    |
                    v
       计算每个样本、每个参数的损失表
                    |
                    v
       对每个“不安全”原假设计算有效 p 值
                    |
                    v
 Bonferroni/Holm、固定序列或图式多重检验控制 FWER
                    |
                    v
   得到认证集合，再从中按效用选最终参数
```

如果多重检验把族错误率控制在 $\delta$，就有

$$
\Pr\left(\sup_{\lambda\in\widehat\Lambda}R(\lambda)\leq\alpha\right)\geq1-\delta.
$$

这个“集合内同时成立”的结论非常重要：认证以后，可以继续用同一份校准数据在 $\widehat\Lambda$ 内挑预测集合最小、拒答率最低或其他效用最好的参数，而不产生二次使用数据的问题。

### 第一步：从经验风险得到有效 p 值

当损失位于 $[0,1]$ 时，先计算

$$
\widehat R_j=\frac1n\sum_{i=1}^nL(T_{\lambda_j}(X_i),Y_i),
$$

再使用 Hoeffding--Bentkus（HB）组合界：

$$
p_j^{\mathrm{HB}}=\min\left(
e^{-nh_1(\widehat R_j\wedge\alpha,\alpha)},
e\Pr\{\operatorname{Bin}(n,\alpha)\leq\lceil n\widehat R_j\rceil\}
\right).
$$

$p_j$ 越小，越不支持“风险大于 $\alpha$”。官方代码在 `core/bounds.py:29-35` 逐项实现该公式。对无界损失，论文还比较了投注型 p 值和 CLT p 值；其中 CLT 版本只有渐近有效性，不能与 HB 的有限样本结论混为一谈。

### 第二步：怎样控制多重检验

#### Bonferroni/Holm

最直接的方法是仅保留 $p_j\leq\delta/|\Lambda|$ 的点。它允许 p 值之间任意相关，但网格大时很保守。代码实际调用 Holm step-down 方法，它仍控制 FWER，通常比普通 Bonferroni 更有力。

#### 固定序列检验

如果事先知道哪些参数更可能安全，就按顺序逐个检验，并在第一次无法拒绝时停止。单起点时不必对整个网格支付 Bonferroni 代价；多起点时把显著性预算分给各起点。关键限制是：顺序不能偷看同一批测试 p 值后再决定。

#### 顺序图式检验（SGT）

把每个假设作为图节点，把总错误预算 $\delta$ 分配到节点。某节点被拒绝后，它的预算沿有向边传给邻居。这样可以利用参数网格的单调性、邻近关系或 Pareto 前沿，同时维持 FWER 保证。官方 OOD 代码实现了 fallback 和 Hamming 图及其预算传播。

### 多风险和 Pareto 前沿

若要同时控制 $m$ 个风险，候选点不安全的含义是至少有一个风险超标：

$$
H_j:\exists \ell,\;R_\ell(\lambda_j)>\alpha_\ell.
$$

分别计算各风险的 $p_{j,\ell}$ 后，取

$$
p_j=\max_\ell p_{j,\ell}.
$$

只有所有分量都提供足够证据时，这个联合原假设才会被拒绝。因此，被认证的每个参数都同时满足全部风险目标。

OOD 示例同时控制“把分布内样本误判为 OOD”的概率和“决定预测时的条件未覆盖率”。两个阈值形成二维网格，风险的坐标单调性产生 Pareto 前沿。2D 固定序列、fallback SGT 和 Hamming-equalized SGT 把检验资源集中到该前沿，而不是对 $1001^2$ 个点平均付出多重性代价。

### “Learn then Test” 中的 learn/test 拆分

基础 LTT 的基础模型早已用独立训练集拟合；校准阶段测试一个预先规定的网格和顺序。只有当“检验路径本身也要从数据学习”时，才必须再拆一次校准集：

```text
校准集 T_cal
   ├── T_graph：学习多风险参数空间中的候选路径
   └── T_testing：用全新 p 值执行固定序列检验
```

在 $T_{\mathrm{graph}}$ 上，方法寻找各风险 p 值都接近同一个 $\beta$ 的点：

$$
\widetilde\lambda(\beta)=\lambda_j,
\quad j=\arg\min_{j'}\|[p_{j',1},\ldots,p_{j',m}]-(\beta,\ldots,\beta)\|_\infty.
$$

将不同 $\beta$ 得到的点去重并排序后，只在 $T_{\mathrm{testing}}$ 上执行固定序列检验。前一半负责 learn，后一半负责 test，因而数据驱动地学路径却不破坏 FWER。实例分割代码采用 50/50 拆分和 200 个对数间隔的 $\beta$。

### 实验说明了什么

- COCO 多标签分类：控制 FDR；固定序列比 Bonferroni 和统一浓缩界更接近目标，输出集合更有用。
- ImageNet 选择性分类：错误率低于 $0.15$，阈值越严格，拒答越多。
- MEPS 回归：控制只在选择预测的样本上的 MSE，展示了非分类风险。
- CIFAR-10 OOD：同时控制两个风险，并识别超过 99% 的测试 ImageNet OOD 图像。
- COCO 实例分割：在三维阈值网格上同时控制未覆盖、$1-\mathrm{mIoU}$ 和 $1-\mathrm{recall}$；后续效用排序使覆盖率较紧，而 recall/IoU 更保守。

### 必须记住的边界

1. 校准数据必须与部署分布同分布，并且独立于模型训练和使用同一测试 p 值的数据自适应设计。
2. 保证是总体边际保证，不保证不同类别、性别、种族、照明条件等子群体都具有相同错误率。
3. LTT 只能认证候选网格中的点；目标不可达时允许返回空集。
4. 数学保证不等于代码开箱即用。官方仓库核心方法完整，但依赖旧版 Python/PyTorch、外部数据和权重、缓存文件，并要求手工修改 Detectron2。

### 代码状态

官方仓库为 `https://github.com/aangelopoulos/ltt`，本地固定提交 `3ad7a64adad9f356e29f40e73935a6114f896396`。论文--代码忠实度为 **medium-high**：核心 p 值、多重检验、风险表、SGT、split fixed sequence 和五类实验均能定位；但没有找到一个面向任意损失/参数网格的统一 LTT 软件 API，也没有自动化测试套件，完整实验复现仍需人工准备外部依赖与数据。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Learn Then Test: summary

### Problem

Modern predictors often expose post-processing choices—classification thresholds, abstention rules, prediction-set sizes, mask thresholds—but ordinary validation does not certify that the chosen setting obeys an explicit population risk limit. Existing distribution-free methods such as conformal prediction and earlier risk-controlling prediction sets focused mainly on coverage or required a one-dimensional parameter and monotone risk. Learn Then Test (LTT) instead handles arbitrary bounded risks, non-monotone behavior, multidimensional tuning parameters, and several risks at once without retraining the base model.

### Paper summary

LTT reframes calibration as multiple hypothesis testing. For each candidate $\lambda_j$, it tests the unsafe null $H_j:R(\lambda_j)>\alpha$ using a valid calibration-set p-value. Any family-wise error rate (FWER) procedure then returns a certified set $\widehat\Lambda$ for which, with probability at least $1-\delta$, every retained candidate has risk at most $\alpha$. Because validity holds simultaneously over the returned set, the user may choose the most useful certified candidate afterward using the same calibration data.

The default finite-sample construction uses a Hoeffding--Bentkus p-value for losses in $[0,1]$. Bonferroni/Holm gives a generic baseline; fixed-sequence testing exploits an externally specified ordering; sequential graphical testing (SGT) propagates the error budget across a structured parameter grid. For multiple risks, each candidate's p-value is the maximum of the component p-values. For difficult high-dimensional grids, split fixed-sequence testing uses one calibration split to learn a promising path and fresh data to test it, preserving FWER validity. In the two-risk OOD example, graph structure targets the Pareto frontier between abstention/type-I error and conditional coverage.

### Evaluation

The paper instantiates LTT on five settings: multi-label FDR control on MS COCO; selective ImageNet classification; selective MEPS regression; simultaneous OOD type-I-error and prediction-set coverage control on CIFAR-10 with ImageNet as OOD data; and simultaneous coverage, mean-IoU, and recall control for Detectron2 instance segmentation on COCO. Across repeated random calibration/validation splits, the risks remain at or below their targets. Structured fixed-sequence and SGT procedures are consistently less conservative than Bonferroni and especially uniform concentration. In the OOD experiment, the calibrated procedure detects more than 99% of the tested ImageNet inputs while satisfying both in-distribution risk targets. The instance-segmentation study controls three coupled risks over a three-dimensional grid; its chosen utility ordering makes coverage tight and recall/IoU conservative.

### Assumptions and limitations

The guarantee requires i.i.d. target-distribution calibration data independent of model training, valid p-values, and testing structures fixed without using the same p-values; data-adaptive structures require an extra split. Finite-sample HB validity assumes bounded loss, while the CLT regression option is asymptotic. Guarantees are marginal rather than conditional across subgroups, and LTT may return an empty certified set when a target is infeasible. A coarse or poorly ordered grid can also sacrifice utility even while validity holds.

### Reproducibility

The official repository `aangelopoulos/ltt` was pinned at commit `3ad7a64adad9f356e29f40e73935a6114f896396`. Code-paper fidelity is **medium-high**: the core p-values, FWER corrections, risk-table construction, SGT graphs, split fixed-sequence method, and every experiment family are present. Full reproduction is not turnkey. The environment pins Python 3.7/PyTorch 1.4-era dependencies; COCO and ImageNet require external datasets/checkpoints; several experiments depend on caches; and Detectron2 requires a manual source modification. No generic packaged LTT API or automated test suite was found.

### Source note

The analysis uses the author-matched arXiv `2110.01052v5` 35-page manuscript because the Project Euclid version-of-record page/PDF was blocked by Incapsula. The 2025 publication metadata—*The Annals of Applied Statistics* 19(2), DOI `10.1214/24-AOAS1998`—was verified independently through Crossref.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
