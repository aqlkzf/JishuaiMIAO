---
layout: default
permalink: /paper-atlas/improved-bayes-risk-reduced-social-welfare-cd8749bd/
title: "Improved_Bayes_Risk_Reduced_Social_Welfare"
nav: false
wide: true
description: "这篇论文研究的不是生物信息学，而是算法经济学与博弈论机器学习。它指出：当多个预测服务商为了争夺用户而调整模型时，更好的数据表示虽然能降低单个模型的 Bayes 风险，却可能让所有服务商的预测变得更相似，破坏原有的“分工覆盖”，从而提高用户在均衡中的总体预测损失。"
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
      <span>NeurIPS · 2026</span>
    </div>
    <h1>Improved_Bayes_Risk_Reduced_Social_Welfare</h1>
    <p>Improved Bayes Risk Can Yield Reduced Social Welfare Under Competition</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2306.14670" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Improved_Bayes_Risk_Reduced_Social_Welfare">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/mjagadeesan/competition-nonmonotonicity" target="_blank" rel="noopener noreferrer" aria-label="Open code for Improved_Bayes_Risk_Reduced_Social_Welfare">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 为什么模型单体更准，竞争市场中的用户反而可能受损？

### 一句话结论

这篇论文研究的不是生物信息学，而是**算法经济学与博弈论机器学习**。它指出：当多个预测服务商为了争夺用户而调整模型时，更好的数据表示虽然能降低单个模型的 Bayes 风险，却可能让所有服务商的预测变得更相似，破坏原有的“分工覆盖”，从而提高用户在均衡中的总体预测损失。

### 问题从哪里来？

通常我们只评估一个模型：表示越好，最优分类器越准。但真实数字市场中常有多个服务商。用户会选择对自己更准确的平台，平台则追求市场份额，而不是直接最小化全体用户的平均损失。

这会产生一个容易忽略的差别：

- 单体指标：如果市场里只有一个模型，最低能做到多少损失？
- 市场指标：多个模型相互响应并达到均衡后，用户实际收到的预测损失是多少？

论文证明，这两个指标不必同向变化。

### 竞争模型

用户 $(x,y)$ 面对 $m$ 个服务商，每个服务商选择分类器 $f_j$。用户以 logit 规则选择平台：

$$
\Pr[j^*(x,y)=j]
=\frac{\exp(-\ell(f_j(x),y)/c)}{\sum_{j'=1}^m\exp(-\ell(f_{j'}(x),y)/c)}.
$$

$c$ 越小，用户越倾向于选择损失最低的平台。服务商 $j$ 的收益是它获得的平均市场份额：

$$
u(f_j;\mathbf f_{-j})
=\mathbb E[\Pr(j^*(x,y)=j)].
$$

所有服务商都不能单方面通过换分类器增加市场份额时，就达到 Nash 均衡。用户侧的社会损失是：

$$
\mathrm{SL}(f_1,\ldots,f_m)
=\mathbb E[\ell(f_{j^*(x,y)}(x),y)].
$$

而表示质量用单个服务商能达到的最低风险衡量：

$$
\mathsf{OPT}_{\mathrm{single}}
=\min_{f\in\mathcal F}\mathbb E[\ell(f(x),y)].
$$

关键点是：服务商优化的是市场份额，论文评价的是用户损失，这两个目标并不一致。

### 非单调性的核心机制

对二分类，定义每种表示 $x$ 上的 Bayes 风险：

$$
\alpha(x)=\min\{\Pr(Y=1\mid x),\Pr(Y=0\mid x)\}.
$$

在有限输入、无噪声用户选择、允许所有确定性分类器的设定下，论文给出：

$$
\mathrm{SL}(f_1^*,\ldots,f_m^*)
=\mathbb E[\alpha(x)\mathbf 1\{\alpha(x)<1/m\}].
$$

可以把 $1/m$ 理解为“少数群体是否值得某个平台专门服务”的门槛：

- 当 $\alpha(x)>1/m$ 时，少数标签对应的用户足够多。某个平台预测少数标签可以获得市场份额，所以平台形成差异化；两种标签都有人提供，用户能够找到正确预测，局部社会损失为 0。
- 当 $\alpha(x)<1/m$ 时，少数群体太小。所有平台都选择多数标签，预测趋同；少数用户无人覆盖，局部社会损失变成 $\alpha(x)$。

因此，表示变好可能让 $\alpha(x)$ 穿过门槛，从“多样化均衡”进入“同质化均衡”。论文中的最简单例子里，Bayes 风险从 0.4 降到 0.3，但均衡社会损失从 0 升到 0.1。

### 从理论到数值计算

线性分类器没有闭式均衡，论文采用近似最佳响应：

```text
合成数据或 CIFAR-10
        ↓
得到表示 x
        ├─训练单个线性模型 → 单体最低风险
        ↓
初始化 m 个服务商模型
        ↓
依次选择服务商 j：
  冻结其他模型
  必要时重初始化 j
  用梯度下降最大化 j 的市场份额
  更新市场份额与社会损失
        ↓
所有服务商收益变化都小于 epsilon 时停止
        ↓
比较均衡社会损失与单体风险
```

代码中的用户选择采用带声誉权重的 log-sum-exp 计算，社会损失则按每个用户选择各平台的概率，对平台预测损失加权。这个流程是数值启发式算法：停止条件是收益稳定，并不提供全局最佳响应或均衡误差的严格证书。

### 实验如何构造“表示变好”

论文沿三个方向改变表示：

1. 改变单个表示下的类别比例，即直接改变 $\alpha$；
2. 改变两类高斯分布的噪声，噪声越小表示越容易分离；
3. 逐步增加可见维度，使表示包含更多信息。

在允许所有分类器的理论设定和限制为线性分类器的模拟中，都能看到社会损失先升后降或出现跳变。它还把 AlexNet、VGG16、ResNet18/34/50 的 ImageNet 预训练特征用于 CIFAR-10：单体风险更低的表示并不总能产生更低的竞争均衡损失，而且排序会随服务商数量变化。

### 应该怎样理解结论？

论文并没有说“规模扩大一定伤害社会福利”，而是证明单体性能改善**不足以保证**市场福利改善。竞争可能带来有价值的模型差异化；当技术进步让竞争者都收敛到相似方案时，这种覆盖优势会消失。

因此，评估平台型学习系统时，不能只看单模型 accuracy 或 Bayes risk，还应考察：竞争者如何响应、模型之间是否仍有差异、不同用户群体是否至少能找到一个有效服务商，以及市场份额目标是否与用户福利一致。

### 适用边界与复现情况

- 所有平台共享同一表示，只调整下游分类器。
- 用户被假设能感知与自身标签相关的预测损失。
- 平台不选择价格、数据收集或进入退出策略。
- CIFAR-10 的 50,000 张训练图像同时构成优化与评价人口，因此不是泛化实验。
- 官方代码与论文数值流程对应度高，但缺少依赖锁定、随机种子、预生成 CIFAR 特征和结果文件；本次没有声称完成端到端复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Improved Bayes Risk Can Yield Reduced Social Welfare Under Competition

### Problem

Better predictive representations usually lower the risk of a model considered in isolation. This paper asks whether that improvement necessarily benefits users when several model providers strategically compete for market share. It shows that the answer can be negative: equilibrium user loss can rise even as isolated-provider Bayes risk falls.

### Main Idea

The paper models each provider as choosing a classifier and each user as selecting a provider through a logit response to prediction loss. Providers maximize expected market share; social welfare is the accuracy users receive after making that choice. These are different objectives.

In a finite-input binary setting with noiseless user choice and all deterministic classifiers, the equilibrium social loss has the closed form

$$
\mathbb E[\alpha(x)\mathbf 1\{\alpha(x)<1/m\}],
$$

where $\alpha(x)$ is the per-representation Bayes risk and $m$ is the number of providers. When $\alpha(x)$ is large enough, a provider can profitably serve the minority label, so equilibrium predictions diversify and users collectively obtain full coverage. When $\alpha(x)$ becomes small, all providers choose the modal label; their predictions homogenize and minority users lose coverage. This threshold effect can make better representations reduce welfare.

The analysis extends to multiclass classification and unequal market reputations. The latter changes the threshold and can require mixed equilibria.

### Evidence

The paper demonstrates non-monotonicity along three synthetic axes—per-input Bayes risk, representation noise, and representation dimension—first with exact theory and then with linear-predictor simulations. It also evaluates five ImageNet-pretrained representations on the 50,000-image CIFAR-10 population for binary and 10-class tasks with 3, 4, 5, 6, or 8 providers.

The CIFAR figures contain concrete ordering reversals. In the binary task, VGG16 can yield lower equilibrium social loss than AlexNet despite higher isolated risk. In the 10-class task, ResNet18 yields lower equilibrium social loss than VGG16 for every tested provider count despite substantially higher isolated risk. These results show possibility and dependence on market structure; they do not claim that scale always harms welfare.

### Domain and Contribution Type

This is an algorithmic economics / game-theoretic machine-learning **method and theory** paper. Its main contribution is an equilibrium model and characterization of welfare under competition, supplemented by a numerical best-response procedure and experiments. It is not a bioinformatics paper.

### Reproducibility

The official repository, `mjagadeesan/competition-nonmonotonicity`, matches the numerical pipeline at commit `edba0529320d0018f5ac0d25e8973131526adab4`. It implements weighted logit choice, provider best responses, social loss, synthetic generators, pretrained CIFAR feature extraction, and binary/multiclass experiment drivers.

Reproducibility is **3/5**. Static code-paper fidelity is high, but the snapshot lacks dependency pins, random seeds, saved CIFAR feature arrays, and output data; `cifar_data.py` also omits ResNet18 from its extraction list while downstream code expects it. No end-to-end experiment was rerun. The theorem proofs have no executable counterpart, as expected.

### Limitations

The exact theory assumes shared global representations, classifier-only provider actions, finite inputs, and noiseless user choice. The simulations use one finite population for optimization and evaluation and rely on approximate rather than certified best responses. Prices, entry, data collection, provider-specific representations, and generalization to new users are outside the model.

### Publication Identity

The acquired source is arXiv `2306.14670v3`, which identifies the conference version as NeurIPS 2023. Michael Jordan's 2026 publication list and the first author's current publication page additionally identify the full version as accepted/forthcoming in *Quantitative Economics*. No journal DOI was found in the verified archival metadata, so the arXiv DOI `10.48550/arXiv.2306.14670` is retained.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
