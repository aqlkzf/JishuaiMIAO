---
layout: default
permalink: /paper-atlas/nullstrap-de-29e3b3e7/
title: "Nullstrap-DE"
nav: false
description: "RNA-seq 差异表达分析的目标，是在成千上万个基因里找出不同生物条件之间表达量显著不同的基因。核心难点是同时兼顾两件事： FDR 控制：不能把太多非差异基因误判为差异基因。 统计功效：真正有差异的基因不能被漏掉太多。 论文指出，DESeq2 和 edgeR 这类参数方法通常功效较高，也能处理较复杂的实验设计；"
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
      <span>Computational Tools</span>
      <span>arXiv · 2025</span>
    </div>
    <h1>Nullstrap-DE</h1>
    <p>Nullstrap-DE: A General Framework for Calibrating FDR and Preserving Power in Differential Expression Methods, with Adaptivity to DESeq2 and edgeR</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Nullstrap-DE 方法中文讲解

### 1. 这篇论文要解决什么问题？

RNA-seq 差异表达分析的目标，是在成千上万个基因里找出不同生物条件之间表达量显著不同的基因。核心难点是同时兼顾两件事：

- **FDR 控制**：不能把太多非差异基因误判为差异基因。
- **统计功效**：真正有差异的基因不能被漏掉太多。

论文指出，DESeq2 和 edgeR 这类参数方法通常功效较高，也能处理较复杂的实验设计；但它们的 size-factor normalization 和 dispersion shrinkage 会让参数估计不再是严格的 MLE，而对应的 $p$ 值仍依赖 MLE 的渐近零分布，因此可能出现 FDR 膨胀 (`paper.md:11-35`)。

相对地，Wilcoxon rank-sum test 这类非参数方法更稳健，但在小样本中功效较低，也难以自然加入 batch、sex、age 等协变量 (`paper.md:23-26`)。

### 2. 现有方法为什么不够？

论文讨论的主要背景方法包括：

- **DESeq2**：Love 等，*Genome Biology*, 2014。基于负二项 GLM，使用 size factor 和 dispersion shrinkage；优点是功效高、工作流成熟，问题是 shrinkage/normalization 可能导致理论零分布不准 (`paper.md:20-26`, `paper.md:270-270`)。
- **edgeR**：Robinson 等，*Bioinformatics*, 2010。也基于负二项 GLM，并使用 normalization 和 dispersion 估计；同样可能在部分场景中 FDR 偏高 (`paper.md:20-26`, `paper.md:277-278`)。
- **limma-voom**：Ritchie 等，*Nucleic Acids Research*, 2015。论文将其作为另一类 RNA-seq 参数流程背景提到，但 Nullstrap-DE 的实现重点是 DESeq2 和 edgeR (`paper.md:20-20`, `paper.md:277-278`)。
- **Wilcoxon rank-sum test**：不依赖负二项分布假设，因此更稳健；但小样本时检出能力弱，而且不能方便地调整协变量 (`paper.md:23-26`)。

因此，作者希望构建一种方法：保留 DESeq2/edgeR 的建模和功效优势，同时用数据驱动的方式校准 FDR。

### 3. Nullstrap-DE 的核心想法

Nullstrap-DE 是一个 **add-on framework**：它不是重写一个全新的 DE 方法，而是在一个已有父方法上加一层校准。父方法可以是 DESeq2、edgeR，理论上也可以扩展到其他参数模型 (`paper.md:29-32`)。

核心思想是：

> 用原始数据拟合父方法，得到每个基因的模型参数；然后把“条件效应”强制设为 0，生成一份 synthetic null data；再让同一个父方法在真实数据和 synthetic null data 上各跑一次，用 synthetic null 的统计量估计假阳性数量，从而重新选择阈值。

这相当于为当前数据、当前父方法、当前 normalization/shrinkage 流程构造一个负控分布。这样，FDR 校准不再只依赖理论渐近零分布，而是依赖“如果没有差异表达、但所有估计流程照样运行，会产生多少大统计量”。

### 4. 论文模型

论文使用负二项 GLM 描述 RNA-seq count：

$$Y_{ij}\overset{\mathrm{ind}}{\sim}\mathrm{NB}\left(\mu_{ij},\phi_j\right),$$

其中 $i$ 是样本，$j$ 是基因。均值模型为

$$\log(\mu_{ij})=\log(s_i)+\alpha_j+\mathbf{x}_i^\top\bm{\beta}_j+\mathbf{z}_i^\top\bm{\gamma}_j.$$

各符号含义如下 (`paper.md:44-78`)：

- $s_i$：样本 size factor，用来校正测序深度。
- $\alpha_j$：基因 $j$ 的 baseline intercept。
- $\mathbf{x}_i$：条件设计变量，例如 treatment/control。
- $\bm{\beta}_j$：条件效应，是差异表达检验的目标。
- $\mathbf{z}_i$：协变量，例如 batch、sex、age。
- $\bm{\gamma}_j$：协变量效应。
- $\phi_j$：基因 $j$ 的 dispersion。

差异表达检验可以写成

$$H_{0,j}:\bm{\beta}_j=\mathbf{0}\quad\text{vs.}\quad H_{1,j}:\bm{\beta}_j\neq\mathbf{0}.$$

### 5. Synthetic Null Data 怎么生成？

Nullstrap-DE 的关键是生成一份 synthetic null count matrix $\widetilde{\mathbf{Y}}$。对每个基因和样本，论文定义 (`paper.md:90-107`)：

$$\widetilde{Y}_{ij}\overset{\mathrm{ind}}{\sim}\mathrm{NB}\left(\mu^0_{ij},\hat{\phi}_j\right),$$

其中

$$
\mu^0_{ij}
=\exp\left(\log(\hat{s}_i)+\hat{\alpha}_j+\mathbf{x}_i^\top\bm{\beta}_0+\mathbf{z}_i^\top\hat{\bm{\gamma}}_j\right)
=\exp\left(\log(\hat{s}_i)+\hat{\alpha}_j+\mathbf{z}_i^\top\hat{\bm{\gamma}}_j\right),
$$

因为 $\bm{\beta}_0=\mathbf{0}$。

直观理解：

- 保留测序深度、baseline、协变量效应、dispersion。
- 删除条件效应。
- 这样生成的数据在设计上“不应该有差异表达”，但保留了数据和估计流程中的复杂性。

### 6. 从输入到输出的计算流程

```text
输入：count matrix Y, condition design X, covariates Z, target FDR q
        |
        v
用父方法 DESeq2 / edgeR 拟合真实数据
        |
        |-- 得到 size factors / library offsets
        |-- 得到 intercept, covariate effects, dispersion
        |-- 得到真实数据统计量 T_hat
        |
        v
把条件效应 beta 设为 0，生成 synthetic null counts Y_tilde
        |
        v
在 Y_tilde 上重新运行同一个父方法
        |
        |-- 得到 synthetic-null 统计量 T_tilde
        |
        v
对每个阈值 t 估计 FDP(t)
        |
        v
选择 tau_q，输出 |T_hat_j| >= tau_q 的基因
```

### 7. FDR 阈值怎么校准？

论文定义真实数据统计量和 synthetic null 统计量：

$$
\widehat{\mathbf{T}}=\mathcal{E}(\mathbf{Y},\mathbf{X},\mathbf{Z}),\qquad
\widetilde{\mathbf{T}}=\mathcal{E}(\widetilde{\mathbf{Y}},\mathbf{X},\mathbf{Z}).
$$

然后用 synthetic null exceedance count 估计假发现比例 (`paper.md:130-140`)：

$$
\widehat{\mathrm{FDP}}(t)=
\frac{\#\{j:\|\widetilde{T}_j\|\geq t\}}
{\max\{\#\{j:\|\widehat{T}_j\|\geq t\},1\}}.
$$

给定目标 FDR $q$，选择

$$
\tau_q=\min\left\{t>0:\widehat{\mathrm{FDP}}(t)\leq q\right\}.
$$

最终输出

$$
\widehat{\mathcal{S}}(\tau_q)=\{j:\|\widehat{T}_j\|\geq\tau_q\}.
$$

这个公式的直觉是：

- 分子：在“无差异表达”的 synthetic null 数据里，有多少基因统计量超过阈值。
- 分母：真实数据里，有多少基因统计量超过阈值。
- 比值：如果用这个阈值，预计发现结果里有多少比例是假阳性。

### 8. DESeq2 和 edgeR 中的统计量

论文给出两个主要适配 (`paper.md:117-127`)：

- **Nullstrap-DESeq2**：两条件场景下使用 Wald statistic
  $$\widehat{T}_j=|\hat{\beta}_j|/\mathrm{se}(\hat{\beta}_j).$$
  如果和 DESeq2 用同一统计量，则基因排序保持不变，改变的是显著性阈值。
- **Nullstrap-edgeR**：因为 edgeR 不提供完全对应的标准误统计量，论文使用
  $$\widehat{T}_j=|\hat{\beta}_j|.$$
  因此 Nullstrap-edgeR 可能同时改变排序和阈值。
- R 包还支持
  $$\widehat{T}_j=-\log p_j,$$
  用于保留父方法基因排序但重新校准阈值。

代码核验结果：

- `Nullstrap_edgeR()` 的 `stat="fc"` 确实使用 `abs(logFC)`，`stat="pval"` 使用 `-log(pval)` (`NullstrapDE/R/Nullstrap_edgeR.R:197-203`)。
- 两个 wrapper 都支持 `stat="pval"` (`NullstrapDE/R/Nullstrap_DESeq2.R:144-149`, `NullstrapDE/R/Nullstrap_edgeR.R:197-199`)。
- `Nullstrap_DESeq2()` 的默认统计量是 Wald-like，但代码用 synthetic-null 的 `lfcSE` 作为真实和 null 统计量的分母，并且使用 coefficient column 2 (`NullstrapDE/R/Nullstrap_DESeq2.R:144-153`)。这与论文中直接写的真实数据 $\mathrm{se}(\hat{\beta}_j)$ 并不完全一致，因此属于 **Partial** 匹配。

### 9. 有限样本校正

理论结果给出 FDR 上界 (`paper.md:340-357`)：

$$
\mathrm{FDR}(\tau_q)\leq q\left(1+\frac{c_1\log p}{\sqrt{s}}+c_2\gamma_{n,p}\right).
$$

在小样本 bulk RNA-seq 中，论文建议把阈值条件改得更保守 (`paper.md:372-382`)：

$$
\widehat{\mathrm{FDP}}(t)\leq\frac{q}{1+c_2\gamma_{n,p}},
$$

并说明 $\gamma_{n,p}$ 可按 $\sqrt{\log p/n}$ 的量级处理。

代码实现中没有显式的 $c_2$ 或 $\gamma_{n,p}$ 参数，而是提供 `correct` 选项：

- `correct="none"`：不额外收紧。
- `correct="half"`：把 FDR cutoff 乘以 $1/2$。
- `correct="ratio"`：使用
  $$1/(1+\sqrt{\log_2(p_\text{like})/n})$$
  作为乘子 (`NullstrapDE/R/Nullstrap_DESeq2.R:157-168`, `NullstrapDE/R/Nullstrap_edgeR.R:209-220`)。

所以代码实现的是论文有限样本思想的启发式版本，而不是符号公式的逐字实现。

### 10. 理论保证在说什么？

论文的理论部分是 paper-only，没有对应可执行代码。主要逻辑是 (`paper.md:296-382`)：

1. 如果真实数据和 synthetic null 数据中的参数估计足够准确，估计误差由 $\gamma_{n,p}$ 控制。
2. 如果真正差异表达基因的信号足够强，可以和非差异基因分开。
3. 如果基因统计量之间满足独立性或近似 block-wise 独立性。
4. 那么用 synthetic null exceedance count 构造的 FDP 估计可以控制 FDR，并且功效趋近于 1。

Figure S1 进一步用模拟展示 DESeq2 和 NB-GLM MLE 的 logFC/dispersion MSE 随样本量下降，作为把理论 MLE 假设连接到 DESeq2/edgeR 实际估计器的经验支持 (`paper.md:366-369`, `images/figure_06.jpg`)。

### 11. 实验结果说明了什么？

论文做了四类证据：

- **模拟实验**：50 次重复、1000 个基因，改变样本量、fold change、DE gene proportion、目标 FDR，并加入协变量和模型错设场景。Figure 1 和 S2-S7 显示 Nullstrap-DESeq2 / Nullstrap-edgeR 的 FDR 曲线通常更接近目标线，同时保留较高 power (`paper.md:153-159`, `paper.md:936-997`)。
- **负控置换实验**：在 monocyte 数据中随机置换标签 1000 次；理论上没有真差异基因。Figure 2 显示 DESeq2/edgeR 仍会产生较多假阳性，而 Nullstrap 方法接近 0 (`paper.md:165-168`, `images/figure_02.jpg`)。
- **bulk monocyte 数据**：Nullstrap 方法选择更少基因，但富集到更具体的免疫相关 GO terms (`paper.md:174-180`, `images/figure_03.jpg`, `images/figure_13.jpg`)。
- **airway smooth muscle 与 COVID pseudobulk 数据**：Nullstrap 方法过滤掉部分低相关信号，保留更符合 dexamethasone 或 COVID monocyte biology 的通路/网络 (`paper.md:186-198`, `images/figure_04.jpg`, `images/figure_05.jpg`)。

### 12. 代码与论文的匹配程度

本地代码快照来自 `https://github.com/chexjiang/NullstrapDE`，commit 为 `26b1e347622ed2eb4391157d285167c1cf2a9712`。代码中真正导出的函数只有：

- `Nullstrap_DESeq2`
- `Nullstrap_edgeR`

见 `NullstrapDE/NAMESPACE:1-4`。

匹配较好的部分：

- 两个核心 wrapper 都存在。
- 都实现了父方法拟合、synthetic null counts 生成、重新拟合、阈值选择。
- `binary_search()` 实现了基于真实/合成 null 统计量 exceedance count 的阈值搜索 (`NullstrapDE/R/helper.R:10-65`)。

需要注意的部分：

- DESeq2 默认统计量与论文公式不是完全逐字匹配。
- synthetic null 中 size factor / library size 默认会重采样，这是代码中的额外实现选择。
- 协变量项的代码实现比论文中的一般形式更弱。
- 没找到论文 Simulation Settings 1-4 的专门复现实验脚本。
- airway notebook 调用了 lowercase `nullstrap_deseq2()` / `nullstrap_edger()`，但当前包并不导出这些名字 (`NullstrapDE/analysis/asm/analysis_asm.Rmd:116-152`, `NullstrapDE/NAMESPACE:1-4`)。

因此，本工作区把代码-论文一致性评为 **medium**：核心思想和主要 wrapper 存在，但理论、模拟复现、有限样本公式和部分 notebook API 仍有缺口。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Nullstrap-DE Summary

### Problem

Nullstrap-DE targets false-discovery-rate (FDR) calibration in RNA-seq differential-expression analysis. The paper argues that widely used parametric methods such as DESeq2 and edgeR are powerful but can become anti-conservative because their normalization and shrinkage procedures differ from the maximum-likelihood assumptions behind their asymptotic null tests (`paper.md:11-35`). Nonparametric alternatives such as Wilcoxon tests can be more robust but often lose power and do not naturally support covariate adjustment (`paper.md:23-29`).

### Prior Methods And Limitations

- **DESeq2** (*Genome Biology*, 2014) and **edgeR** (*Bioinformatics*, 2010) use negative-binomial GLMs, size-factor/library normalization, and empirical-Bayes-style dispersion stabilization; the paper's concern is inflated FDR under shrinkage/normalization misspecification (`paper.md:20-26`, references at `paper.md:270-278`).
- **limma-voom** (*Nucleic Acids Research*, 2015) is cited as another parametric RNA-seq workflow based on log-transformed counts and precision weights, but the method development focuses on DESeq2/edgeR (`paper.md:20-20`, reference at `paper.md:277-278`).
- **Wilcoxon rank-sum tests** avoid parametric assumptions but have lower power in small samples and cannot adjust for covariates (`paper.md:23-26`).

### Proposed Method

Nullstrap-DE is an add-on framework for parent DE methods. It fits the parent method, generates synthetic null count data by setting the condition effect $\bm{\beta}_j$ to zero while preserving nuisance estimates, runs the same parent method on the real and synthetic-null data, and chooses a data-driven threshold by comparing real and null statistic exceedances (`paper.md:84-144`).

For DESeq2, the paper uses a Wald-style statistic so the original ranking is meant to be preserved while the significance threshold changes. For edgeR, the paper uses coefficient magnitude by default and also supports a `-log p` statistic (`paper.md:117-127`). The central FDP estimate is

$$
\widehat{\mathrm{FDP}}(t)=
\frac{\#\{j:\|\widetilde{T}_j\|\geq t\}}
{\max\{\#\{j:\|\widehat{T}_j\|\geq t\},1\}},
$$

with $\tau_q$ selected as the minimum threshold satisfying $\widehat{\mathrm{FDP}}(t)\le q$ (`paper.md:130-140`).

### Evaluation

The paper evaluates Nullstrap-DESeq2 and Nullstrap-edgeR in simulations, negative-control permutations, and real RNA-seq analyses:

- Simulations use 50 replicates per scenario, 1,000 genes, varying sample size, fold change, DE proportion, FDR target, and optional confounding covariates; additional Poisson and zero-inflated NB settings test misspecification (`paper.md:153-159`, `paper.md:936-997`).
- Figure 1 and Supplementary Figures S2-S7 visually show Nullstrap methods keeping FDR closer to the target line than DESeq2/edgeR while retaining much of their power.
- In 1,000 permuted monocyte negative-control datasets, Figure 2 shows DESeq2/edgeR producing many false positives while Nullstrap methods are concentrated near zero (`paper.md:165-168`).
- Real monocyte, airway, and COVID pseudobulk examples show fewer selected genes but more biologically focused enrichment patterns, including immune-specific monocyte terms, dexamethasone-relevant airway pathways, and COVID antigen-presentation modules (`paper.md:174-198`).

### Reproducibility And Code Match

The paper reports a public R package and reproduction code at `https://github.com/chexjiang/NullstrapDE` (`paper.md:213-216`). The local snapshot contains exported `Nullstrap_DESeq2()` and `Nullstrap_edgeR()` wrappers, a threshold helper, README examples, smoke tests, and notebooks for monocyte, airway, and COVID analyses.

Code-paper fidelity is **medium**:

- Matched: the two core wrappers implement parent-method fitting, synthetic-null simulation, refitting, and thresholding (`NullstrapDE/R/Nullstrap_DESeq2.R:15-180`, `NullstrapDE/R/Nullstrap_edgeR.R:17-229`, `NullstrapDE/R/helper.R:10-65`).
- Partial: finite-sample correction is exposed through heuristic `correct` modes rather than the paper's literal $q/(1+c_2\gamma_{n,p})$ notation; DESeq2's default code statistic is Wald-like but not a literal use of the real-data standard error; covariate handling in synthetic-null means is less general than the paper notation.
- Missing or unresolved: no dedicated scripts for Simulation Settings 1-4 were found; theorem/proof content is paper-only; the airway notebook calls lowercase wrapper names not exported by the current `NAMESPACE`.

The workspace CodeGraph index exists but indexed zero R files, so final code claims use direct source-line reads rather than CodeGraph navigation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
