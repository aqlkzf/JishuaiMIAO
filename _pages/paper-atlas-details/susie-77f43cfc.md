---
layout: default
permalink: /paper-atlas/susie-77f43cfc/
title: "SuSiE"
nav: false
description: "SuSiE 的核心是：用若干个“只能选择一个变量、但保留全部选择不确定性”的贝叶斯单效应模型相加，再通过 IBSS 反复对其他效应残差化。这个结构让高度相关变量可以作为一个可信集合被诚实报告；代价是需要给出 L、依赖模型与 LD 质量，并仍可能落入局部最优。"
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
      <span>Journal of the Royal Statistical Society: Series B · 2020</span>
    </div>
    <h1>SuSiE</h1>
    <p>A simple new approach to variable selection in regression, with application to genetic fine mapping</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1111/rssb.12388" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SuSiE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/stephenslab/susieR" target="_blank" rel="noopener noreferrer" aria-label="Open code for SuSiE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SuSiE：把稀疏回归拆成若干个“单效应”问题

### 1. 它真正要解决的困难

SuSiE（Sum of Single Effects）处理的是线性回归中的变量选择：给定响应向量 $\mathbf y$ 和设计矩阵 $\mathbf X=[\mathbf x_1,\ldots,\mathbf x_p]$，希望判断哪些系数 $b_j$ 非零。论文重点应用于遗传精细定位：一段基因组区域中常有许多高度连锁不平衡（LD）的 SNP，多个变量几乎携带同一份信息。此时强行报告一个“被选中的 SNP”会隐藏真实的不确定性；更合理的结论可能是“这 37 个高度相关 SNP 中至少有一个效应变量”。

SuSiE 的关键不是另造一个惩罚项，而是改变稀疏系数的表示方式。它把一个最多含 $L$ 个信号的系数向量写成 $L$ 个单效应向量之和，并让每个单效应都保留“究竟是哪一个变量”的完整后验分布。这样，算法既能给每个变量总体后验包含概率（PIP），也能对每个信号给出可信集（credible set, CS）。论文正文第 2–3 节给出模型与 IBSS 算法，补充材料 A–B 节给出单效应后验、变分目标和推导。

### 2. 基本积木：单效应回归 SER

单效应回归（single-effect regression, SER）假设恰好一个变量产生效应：

$$
\mathbf y=\mathbf X\mathbf b+\mathbf e,\qquad
\mathbf e\sim N(\mathbf 0,\sigma^2\mathbf I),
$$

$$
\mathbf b=b\boldsymbol\gamma,\qquad
\boldsymbol\gamma\sim\operatorname{Mult}(1,\boldsymbol\pi),\qquad
b\sim N(0,\sigma_0^2).
$$

$\boldsymbol\gamma$ 是 one-hot 向量；$\gamma_j=1$ 表示第 $j$ 个变量承担这个效应。因为模型只需比较 $p$ 个一元回归，所以后验可以解析计算。若 $\widehat b_j$ 是第 $j$ 个一元回归的估计、$s_j^2$ 是其方差，则

$$
\alpha_j=P(\gamma_j=1\mid\mathbf X,\mathbf y)
=\frac{\pi_j\operatorname{BF}_j}
{\sum_{k=1}^p\pi_k\operatorname{BF}_k}.
$$

这里 $\alpha_j$ 不是硬选择，而是“该单效应由变量 $j$ 承担”的概率。给定 $\gamma_j=1$ 后，效应大小仍有正态后验，其均值和方差为

$$
\sigma_{1j}^2=\left(s_j^{-2}+\sigma_0^{-2}\right)^{-1},\qquad
\mu_{1j}=\frac{\sigma_{1j}^2}{s_j^2}\widehat b_j.
$$

当前代码在 `R/single_effect_regression.R:17-68` 组织这一步：先生成 SER 统计量，再估计先验方差、计算对数 Bayes factor 和 $\alpha$、计算后验矩，最后计算 KL 项。`R/single_effect_regression.R:89-177` 实现先验方差优化及接近零时的截断。需要注意，当前代码还支持 mixture、EM 和 uniroot 等路径；这些不是 2020 论文中 `susieR 0.4.29` 的原始实现范围。

### 3. 从一个效应到多个效应

SuSiE 把系数向量表示成

$$
\mathbf b=\sum_{l=1}^{L}\mathbf b_l,
\qquad \mathbf b_l=b_l\boldsymbol\gamma_l.
$$

每个 $\mathbf b_l$ 最多只有一个非零元素，所以总系数最多表达 $L$ 个效应。$L$ 是信号数的上界，不要求精确等于真实信号数。经验贝叶斯估计会把多余分量的先验方差压到零或接近零；后处理还会滤掉低纯度可信集。不过，$L$ 过小会让模型没有容量表达全部信号，不能靠后处理补救。

近似后验写成

$$
q(\mathbf b_1,\ldots,\mathbf b_L)=\prod_{l=1}^{L}q_l(\mathbf b_l).
$$

它在不同单效应之间因子化，但每个 $q_l$ 内仍保留 $p$ 个候选变量互斥竞争的结构。因此它不同于把每个 $b_j$ 都独立因子化的普通 mean-field 近似；高度相关变量可以共同分享同一效应的后验质量，而不必被武断地拆成多个独立发现。

### 4. IBSS：逐个拿掉其他效应，再重新做一次 SER

IBSS（iterative Bayesian stepwise selection）可理解为贝叶斯 backfitting。更新第 $l$ 个效应时，先从 $\mathbf y$ 中减去其余 $L-1$ 个效应的当前后验均值：

$$
\overline{\mathbf r}_l
=\mathbf y-\mathbf X\sum_{l'\ne l}E_q(\mathbf b_{l'}).
$$

随后把 $\overline{\mathbf r}_l$ 当作新的响应，调用一次 SER，得到新的 $\boldsymbol\alpha_l$、条件效应均值和二阶矩，再更新拟合值。对 $l=1,\ldots,L$ 完成一轮后重新计算变分下界（ELBO），反复迭代至收敛。

当前源码的对应路径非常直接：

1. `R/susie_workhorse.R:14-55` 初始化模型并执行 IBSS 外循环；每轮调用 `ibss_fit()`，计算目标、检查收敛，再更新方差分量。
2. `R/iterative_bayesian_stepwise_selection.R:171-219` 依次扫过 $L$ 个效应。
3. `R/single_effect_regression.R:196-207` 明确执行“计算残差 → SER → 更新拟合值”。
4. `R/susie_workhorse.R:69-77` 在收敛后裁去近零效应，并可选执行 refinement。

因此，“stepwise”并不表示一次选中后永不回头。图 1 正是在展示这种反复修正：第一次迭代时，最强边际关联 SNP（SMA）进入了一个错误可信集；到第 10 次迭代，其他效应被解释后，SMA 不再必要，算法得到两个分别覆盖真实效应的高纯度可信集。这是普通前向选择与 IBSS 的核心区别。

### 5. ELBO、收敛与局部最优

IBSS 是对变分目标的坐标上升。直观地说，ELBO 同时奖励对数据的拟合，并惩罚近似后验偏离先验。每次 SER 更新都在固定其他分量时优化一个 $q_l$，因此目标不会下降；但“不下降”不等于找到全局最优。

论文图 4(b) 给出故意构造的反例：两个相邻变化点的效应很快互相抵消，从空模型出发，单独加入任意一个变化点都会使拟合变差，于是 IBSS 停在无变化点的差解，目标为 $-181.8$；以真实双变化点初始化则得到 $-148.2$ 的更好解。当前代码 `R/susie_workhorse.R:74-77` 的可选 refinement 会尝试替代初始化以缓解这类局部最优，但它是工程补救，不能转化成全局最优保证。

### 6. PIP 与可信集回答的是两个不同问题

对变量 $j$，总体 PIP 汇总它在任一单效应中出现的概率：

$$
\operatorname{PIP}_j=1-\prod_{l=1}^{L}(1-\alpha_{lj}).
$$

PIP 回答“这个变量是否参与至少一个效应”。可信集则针对某个单效应 $l$：将 $\alpha_{lj}$ 从大到小排序，取累计概率首次达到覆盖水平 $\rho$（通常 0.95）的最小变量集合。它回答“这个集合是否包含承担该效应的变量”。因此，一个含 37 个 SNP 的可信集里，每个 SNP 的 PIP 都可能不高，但“集合中至少一个有作用”的把握仍然很高。

当前 `susie_get_cs()` 在 `R/susie_get_functions.R:277-390` 构造集合、去重、计算声明覆盖度并按相关性纯度过滤。默认 `coverage=0.95`、`min_abs_corr=0.5`；大集合默认抽取至多 100 个变量估计纯度。纯度不是额外的后验概率，而是可信集内部变量相关性的诊断：低纯度集合往往把互不相关的候选混在一起，解释价值较弱。若调用时既不提供 $X$ 也不提供相关矩阵，当前代码会跳过纯度过滤（`R/susie_get_functions.R:283-289,342-349`）。当前版本还可按 `ld_extend_threshold` 扩展集合（`R/susie_get_functions.R:352-365`），这是论文版之后的行为，复现论文结果时不能默认等同。

可信集也不应被反向解读：某变量没有进入报告的可信集，不等于它已被证明为零；论文明确把可信集定义为针对效应的集合不确定性，而不是所有未入集变量的排除检验。

### 7. 四幅主图怎样串起方法证据

- **图 1：算法机制。** 在 1000 个 SNP、两个真实效应且 SMA 为非效应变量的困难样例中，IBSS 从初期错误集合修正为两个真实集合；一个集合仅 3 个 SNP、纯度 0.85，另一个含 37 个强相关 SNP、纯度 0.97。
- **图 2：变量级校准与检测能力。** SuSiE 的 PIP 与 DAP-G、CAVIAR、FINEMAP 比较，并通过改变 PIP 阈值形成 power–FDR 曲线。这里是模拟条件下的比较，不是所有真实数据场景的普遍优越性证明。
- **图 3：集合级表现。** 与 DAP-G 的 95% 可信集比较覆盖、功效、大小和集合内相关性。论文也强调：贝叶斯 95% 可信集不保证频率学覆盖恰为 0.95，实际覆盖依赖模拟场景与信号强度。
- **图 4：推广与失败模式。** (a) 把变化点检测写成特殊设计矩阵上的稀疏回归，并为位置给出可信集；(b) 直接展示局部最优限制。

补充材料进一步给出 SER 后验与 Bayes factor 推导、可信集定义、SuSiE 先验与固定大小稀疏先验的关系、ELBO/方差更新推导，以及图 A1、S3–S5 等模拟补充。它们支持公式和边界解释，但不替代正文对方法目标的定义。

### 8. 在遗传精细定位中的输入与输出

以个体水平数据为例，输入是基因型矩阵 $X$、表型 $y$、效应上界 $L$，以及可选的变量先验权重。输出至少包括：每个效应的 $\alpha$ 矩阵、条件后验均值/二阶矩、每个变量的总体 PIP、经过纯度过滤的可信集、先验与残差方差估计、ELBO 和收敛状态。

高 PIP 或高覆盖可信集仍是模型条件下的统计证据，不自动证明生物因果。LD 错配、群体结构、模型缺失、样本量不足和先验设定都会影响结果。使用汇总统计时还要求 LD 参考与研究样本匹配；当前代码的 `susie_rss` 等接口扩大了可用输入，但这些接口的现代实现细节不能视为原论文所有实验的复现条件。

### 9. 论文版本、当前代码与可复现边界

- 论文正文第 4.2 节明确报告比较实验使用 `susieR 0.4.29`；补充材料 D.2 报告 R 3.5.1 和 OpenBLAS 0.3.5 的计算环境。
- 本地 `susieR/DESCRIPTION` 标记版本 `0.15.58`，实际检出的 Git HEAD 是 `206cc19ca89d985245ca204fbc86772e5c2446d0`。本解读的代码锚点针对这个当前快照。

当前 0.15.58 仍保留“残差化 → SER → 更新拟合 → ELBO/收敛 → PIP/CS”的论文核心，但增加了 summary-statistics/RSS 路径、refinement、mixture 与 NIG 先验、slot prior、LD 扩展等功能。若目标是复现论文数值，应锁定论文版软件、数据、参数和计算环境，而不是直接用当前 HEAD 后期待逐点相同。

工作区有论文与补充材料的 OCR Markdown、主图分析以及当前代码快照，但没有一套已执行并核验的原论文完整 benchmark 输出。论文提及的 manuscript resource、受控或外部数据及竞争方法环境也没有被完整封装在此处。因此这里能够验证方法—公式—代码主干的一致性，不能声称已端到端复现论文全部数值。

### 10. 一句话抓住 SuSiE

SuSiE 的核心是：用若干个“只能选择一个变量、但保留全部选择不确定性”的贝叶斯单效应模型相加，再通过 IBSS 反复对其他效应残差化。这个结构让高度相关变量可以作为一个可信集合被诚实报告；代价是需要给出 $L$、依赖模型与 LD 质量，并仍可能落入局部最优。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SuSiE: Sum of Single Effects Regression

**Paper**: "A simple new approach to variable selection in regression, with application to genetic fine mapping"
**Authors**: Gao Wang, Abhishek Sarkar, Peter Carbonetto, Matthew Stephens
**Journal**: Journal of the Royal Statistical Society: Series B (2020), 82(5), 1273-1300
**DOI**: 10.1111/rssb.12388
**Code**: https://github.com/stephenslab/susieR (v0.15.58)

---

### Motivation & Novelty

#### The Problem

Genetic fine mapping aims to identify which specific genetic variants (SNPs) causally affect a trait of interest (e.g., gene expression, disease risk). This is a variable selection problem in linear regression, but with a critical challenge: SNPs are highly correlated due to linkage disequilibrium (LD). Typical fine mapping datasets contain many SNP pairs with correlation >0.99, making it impossible to confidently select one SNP over another.

The scientifically correct answer in such cases is not "select SNP A" but rather "either SNP A or SNP B is causal, and we cannot determine which." Existing methods fail to provide this kind of uncertainty quantification.

#### Limitations of Existing Approaches

- **Lasso** (Tibshirani 1996, *J. R. Statist. Soc. B*) and **elastic net** (Zou & Hastie 2005, *J. R. Statist. Soc. B*): Select a single combination of variables, ignoring uncertainty. In the correlated case, EN selects all correlated variables with non-zero coefficients, which is qualitatively wrong.
- **Selective inference** (Taylor & Tibshirani 2015, *PNAS*): Assesses uncertainty in coefficients of selected variables, not uncertainty in which variables to select. Can assign highly significant p-values to wrong variables.
- **Stability selection / knockoff filter** (Meinshausen & Bühlmann 2010, *J. R. Statist. Soc. B*; Barber & Candès 2015, *Ann. Statist.*): FDR control results in no discoveries when variables are very highly correlated.
- **Hierarchical testing** (Meinshausen 2008, *Biometrika*; Mandozzi & Bühlmann 2016, *J. Am. Statist. Ass.*): Requires specifying a hierarchy that doesn't naturally exist for SNPs; produces much larger clusters than necessary.
- **BVSR with MCMC** (Guan & Stephens 2011, *Ann. Appl. Statist.*; Wallace et al. 2015, *PLOS Genet.*): Can in principle capture uncertainty, but computationally expensive and difficult to summarize.
- **Fully factorized variational BVSR** (Carbonetto & Stephens 2012, *Bayesian Analysis*; Logsdon et al. 2010, *BMC Bioinformatics*): Fast but fails to capture correlations between variables — often selects at most one of two identical variables without acknowledging uncertainty.
- **CAVIAR** (Hormozdiari et al. 2014, *Genetics*): Exhaustive enumeration, computationally prohibitive for >3 effects.
- **FINEMAP** (Benner et al. 2016, *Bioinformatics*): Heuristic approximation, still slow.
- **DAP-G** (Wen et al. 2016, *Am. J. Hum. Genet.*; Lee et al. 2018, *bioRxiv*): Produces "signal clusters" similar to credible sets but with heuristic rules and lower power.

#### What's New in SuSiE

1. **Sum of Single Effects model**: Writes the sparse coefficient vector as a sum of $L$ "single-effect" vectors, each with exactly one non-zero element. This structure enables a tractable non-factorized variational approximation.

2. **IBSS algorithm**: A Bayesian analogue of stepwise selection — instead of selecting one variable per step, computes a distribution over variables. Formally justified as coordinate ascent on the ELBO (Corollary 1).

3. **Credible sets**: Each of the $L$ single effects yields a credible set — the smallest set of variables with $\geq 95\%$ posterior probability of containing a causal variant. These directly answer the question "which variables might be causal?"

4. **Exchangeability property** (Proposition 3): When two variables are identical, IBSS assigns them identical posteriors — a property not satisfied by lasso, elastic net, or fully factorized variational methods.

5. **Computational efficiency**: $O(npL)$ per iteration, implemented in R but faster than C++ implementations of CAVIAR, FINEMAP, and DAP-G.

---

### Method Overview

SuSiE models the regression coefficient vector as:
$$\mathbf{b} = \sum_{l=1}^{L} \mathbf{b}_l$$
where each $\mathbf{b}_l$ has exactly one non-zero element (a "single effect"). The IBSS algorithm fits this model by iteratively updating each $\mathbf{b}_l$ via a single-effect regression on the residuals from all other effects. This is coordinate ascent on a variational lower bound to the posterior.

**Key technical components**:
- Single Effect Regression (SER): analytically tractable posterior for one-effect model
- Bayes factors computed from $p$ univariate regressions per iteration
- Empirical Bayes estimation of prior variance $\sigma_{0l}^2$ per effect
- Purity filtering of credible sets (min absolute correlation ≥ 0.5)

See `doc_method.md` for full mathematical details and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Datasets

- **Simulation**: Real human genotype data from GTEx project (n=574, chromosomes 1-22), 150 randomly selected genes, p=1000-12000 SNPs per gene. Synthetic outcomes with S=1-5 effect variables, proportion of variance explained φ=0.05-0.4. Total: 6000 data sets (first scenario) + 300 data sets (second scenario, S=10, p=3000-12000).
- **Real data**: Splice QTL fine mapping from Li et al. (2016, *Science*) — 77,345 intron ratios, n=87 Yoruban individuals, ~600 SNPs per intron.

#### Metrics

- **PIP accuracy**: Scatter plots vs. competing methods; power vs. FDR curves
- **Credible set coverage**: Proportion of CSs containing a true effect variable (target: ≥0.95)
- **Credible set power**: Proportion of true effects captured in a CS
- **Credible set size**: Median number of variables per CS (smaller = better)
- **Purity**: Average squared correlation among CS variables (higher = better)
- **Runtime**: Wall-clock time

#### Key Results

**PIPs** (Fig 2): SuSiE PIPs agree closely with DAP-G, CAVIAR, FINEMAP (correlations 0.94-1.0 across data sets). At a given FDR, SuSiE achieves higher power than all competing methods.

**Credible sets** (Fig 3, Table 3): Compared to DAP-G:
- Higher power (e.g., 0.99 vs 0.89 for S=1; 0.37 vs 0.32 for S=5)
- Smaller median size (e.g., 3 vs 3 for S=1; 7 vs 9 for S=5)
- Higher purity (e.g., 0.99 vs 0.99 for S=1; 0.97 vs 0.95 for S=5)
- Coverage near nominal 0.95 for both methods

Compared to hierinf (hierarchical testing): SuSiE CSs are dramatically smaller (median 7 vs 54 for S=5) with much higher purity (0.97 vs 0.56).

**Runtime** (Table 2, S=3): SuSiE mean 0.64s vs DAP-G 2.87s, FINEMAP 23.01s, CAVIAR 2907.51s.

**Real data** (Sec 5): 2652 credible sets across 2496 introns; 457 single-SNP CSs; 156 secondary signals missed by conventional single-signal analyses. CSs enriched in splice sites and regulatory regions.

**Change point detection** (Fig 4): SuSiE correctly identifies 7 change points with credible sets; demonstrates local optima issue for closely spaced change points.

---

### Reproducibility

**Rating: 4/5**

**Justification**: The susieR package is well-maintained, actively developed (v0.15.58 vs paper's v0.4.29), and available on CRAN/GitHub. Core algorithm is fully implemented and matches the paper. Simulation code and data are available at the manuscript resource repository (Zenodo DOI: 10.5281/zenodo.2368676). GTEx genotype data requires dbGaP access (phs000424.v7.p2).

**Strengths**:
- R package with comprehensive documentation and vignettes
- All paper equations implemented and verified
- Extensive test suite
- Multiple interfaces: individual data, sufficient statistics, RSS

**Weaknesses**:
- GTEx genotype data requires dbGaP application (not freely downloadable)
- Paper uses v0.4.29; current code (v0.15.58) has many extensions that may change default behavior
- Simulation scripts not bundled in the R package (separate repository)
- Change point detection requires `susie_trendfilter()` which is not the default entry point

**Environment setup**:
```r
install.packages("susieR")  # CRAN
# or
devtools::install_github("stephenslab/susieR")

# Basic usage
library(susieR)
fit <- susie(X, y, L=10)
susie_get_cs(fit, X=X)  # credible sets with purity filter
susie_get_pip(fit)       # posterior inclusion probabilities
```

**Common pitfalls**:
- Default `L=10` may be too small for traits with many effects; use `L=20` or `susie_auto()`
- `estimate_prior_variance=TRUE` (default) can set V=0 for weak effects; use `estimate_prior_variance=FALSE` with fixed `scaled_prior_variance` if this is undesirable
- For GWAS summary statistics, use `susie_rss()` not `susie()`
- Purity filter (`min_abs_corr=0.5`) may remove valid CSs in low-LD regions; adjust as needed

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
