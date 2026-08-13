---
layout: default
permalink: /paper-atlas/pseudotimede-7329a08f/
title: "PseudotimeDE"
nav: false
wide: true
description: "PseudotimeDE 解决的是单细胞 RNA-seq 里一个很常见但容易被低估的问题：已经推断出细胞伪时间之后，怎样判断某个基因是否沿伪时间发生差异表达。论文的核心判断是，伪时间不是一个没有误差的真实协变量，而是从同一批表达数据里估计出来的随机量；如果后续 DE 检验把每个细胞的伪时间当成固定值，就可能得到不校准的 p 值，从而影响 FDR 控制或损失检出能力。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Genome Biology · 2021</span>
    </div>
    <h1>PseudotimeDE</h1>
    <p>PseudotimeDE: inference of differential gene expression along cell pseudotime with well-calibrated p-values from single-cell RNA sequencing data</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/SONGDONGYUAN1994/PseudotimeDE" target="_blank" rel="noopener noreferrer" aria-label="Open code for PseudotimeDE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PseudotimeDE 方法中文解释

### 这篇论文要解决什么问题

PseudotimeDE 解决的是单细胞 RNA-seq 里一个很常见但容易被低估的问题：已经推断出细胞伪时间之后，怎样判断某个基因是否沿伪时间发生差异表达。论文的核心判断是，伪时间不是一个没有误差的真实协变量，而是从同一批表达数据里估计出来的随机量；如果后续 DE 检验把每个细胞的伪时间当成固定值，就可能得到不校准的 p 值，从而影响 FDR 控制或损失检出能力（`paper source/springer_html/paper.md:12-12`, `paper source/springer_html/paper.md:45-48`）。

因此，PseudotimeDE 的目标不是发明新的轨迹推断算法，而是在任意用户指定的伪时间推断方法之后，给每个基因输出更可靠的 p 值。论文把这个方法描述为四步：subsampling、pseudotime inference、model fitting、hypothesis testing（`paper source/springer_html/paper.md:57-63`）。

### 为什么已有方法不够

论文讨论了几类已有方法的限制。

第一类是 TSCAN、Slingshot、Monocle、Monocle2 等轨迹推断软件自带的 DE 功能。它们通常只能作为同一个软件包内部的下游步骤使用，不能自然接收外部用户给定的伪时间（`paper source/springer_html/paper.md:36-36`）。

第二类是 tradeSeq。tradeSeq 使用 NB-GAM，模型形式灵活，但论文指出它的 p 值依赖不够准确的零假设近似，原 tradeSeq 论文也更倾向于把 p 值当作排序分数，而不是严格的概率解释。因此，如果用户要做 FDR 或 type I error 控制，这会成为问题（`paper source/springer_html/paper.md:39-39`）。

第三类是 Monocle3-DE。它可以使用用户给定的协变量，但使用 GLM，假设表达均值的对数和伪时间是线性关系。对很多沿伪时间有非线性变化的基因，这个模型会太受限（`paper source/springer_html/paper.md:39-39`）。

NBAMSeq 和 ImpulseDE2 原本面向 bulk RNA-seq time-course，理论上可以改用于连续伪时间，但论文认为它们在 scRNA-seq 伪时间场景中的表现缺少系统 benchmark（`paper source/springer_html/paper.md:42-42`）。

### 方法直觉

PseudotimeDE 的关键想法是：不要只在原始数据上推断一次伪时间，而是通过反复抽取 80% 细胞、重新推断伪时间，得到许多伪时间实现 $\mathbf{T}^1,\ldots,\mathbf{T}^B$。这些实现反映了伪时间推断的不确定性。然后，在每个 subsample 中随机打乱伪时间，重新拟合模型，得到零假设下的检验统计量分布。这样，p 值不再只依赖“伪时间固定时”的渐近分布，而是把伪时间推断不确定性也传播进零分布里。

论文默认 $B=1000$，并说明每次抽取 80% 细胞；如果细胞有预定义 group，就在每个 group 内做 stratified sampling（`paper source/springer_html/paper.md:263-266`）。

### 数学设定

论文把表达矩阵记为 $\mathbf{Y}=(Y_{ij})$，大小是 $n \times m$，其中 $n$ 是细胞数，$m$ 是基因数，$Y_{ij}$ 是细胞 $i$ 中基因 $j$ 的 read count。伪时间向量记为 $\mathbf{T}=(T_1,\ldots,T_i,\ldots,T_n)^T$，其中 $T_i \in [0,1]$（`paper source/springer_html/paper.md:257-260`）。

对每个基因 $j$，基础模型是 NB-GAM：

$$\left\{\begin{array}{ll} Y_{ij} \sim \operatorname{NB}(\mu_{ij}, \phi_{j}),\\ \log(\mu_{ij}) = \beta_{j0} + f_{j}(T_{i}), \end{array}\right. $$

这里 $f_j(T_i)=\sum_{k=1}^{K} b_k(T_i)\beta_{jk}$ 是 cubic spline。论文默认 knot 数为 6，并使用 mgcv 拟合（`paper source/springer_html/paper.md:272-278`）。

为了处理 scRNA-seq 中可能存在的 excess zeros，论文还给出 ZINB-GAM：

$$\left\{\begin{array}{ll} Z_{ij} \sim \operatorname{Ber}(p_{ij}),\\ Y_{ij}|Z_{ij} \sim Z_{ij} \cdot \operatorname{NB}(\mu_{ij}, \phi_{j}) + (1-Z_{ij}) \cdot 0,\\ \log(\mu_{ij}) = \beta_{j0} + f_{j}(T_{i}),\\ \operatorname{logit}(p_{ij}) = \alpha_{j0} + \alpha_{j1}\log(\mu_{ij}). \end{array}\right. $$

用户可以指定 NB-GAM 或 ZINB-GAM；如果不指定，PseudotimeDE 会用 AIC 自动选择，默认倾向 NB-GAM，只有 ZINB-GAM 的 AIC 至少好 10 才切换过去（`paper source/springer_html/paper.md:281-287`）。

### 检验统计量和 p 值

PseudotimeDE 检验：

$$H_{0}: f_{j}(\cdot) = 0 \quad\mathrm{vs.}\quad H_{1}: f_{j}(\cdot) \neq 0$$

如果 $f_j(\cdot)=0$，说明基因 $j$ 的表达均值不随伪时间变化。论文定义拟合出的 smooth vector 为 $\boldsymbol{\hat{f}}_j$，协方差矩阵为 $\mathbf{\widehat V}_{f_j}$，检验统计量为：

$$S_{j}=\boldsymbol{\hat{f}}_{j}^{\mkern-1.5mu\mathsf{T}} \mathbf{\widehat V}_{f_{j}}^{r-} \boldsymbol{\hat{f}}_{j},$$

其中 $\mathbf{\widehat V}_{f_j}^{r-}$ 是 rank-$r$ pseudoinverse（`paper source/springer_html/paper.md:293-305`）。

当伪时间被视作固定值时，可以使用 mgcv 的 smooth component 渐近 p 值；但 PseudotimeDE 的重点是随机伪时间，所以它改用 subsample-permutation 零分布（`paper source/springer_html/paper.md:305-311`）。

经验 p 值为：

$$p_{j}^{\text{emp}} = \frac{\sum_{b = 1}^{B}\mathbb{I}(s_{j}^{b} \geq s_{j}) + 1}{B + 1},$$

其中 $s_j$ 是原始数据上的统计量，$s_j^b$ 是第 $b$ 个打乱伪时间 subsample 的零假设统计量（`paper source/springer_html/paper.md:314-314`）。

为了提高 p 值分辨率，PseudotimeDE 还拟合参数零分布：先拟合 gamma 分布，再尝试两成分 gamma mixture；如果 LRT p 值 $\leq 0.01$，就用 mixture，否则用单 gamma。参数 p 值写成：

$$p_{j}^{\text{param}} = 1 - \hat{F}_{j}(s_{j}), $$

论文报告的结果使用 $p_j^{\text{param}}$，因为它比经验 p 值分辨率更高（`paper source/springer_html/paper.md:315-318`）。

### 代码里实际怎么做

代码层面最重要的边界是：`runPseudotimeDE()` 和 `pseudotimeDE()` 不负责推断伪时间。它们需要用户已经准备好：

- `ori.tbl`：原始数据中每个细胞的伪时间；
- `sub.tbl`：一个 list，每个元素是某个 subsample 中细胞和伪时间的表；
- `mat`：表达矩阵或 `SingleCellExperiment`/`Seurat` 对象。

`runPseudotimeDE()` 会检查 `sub.tbl` 中的 cell 是否都属于 `ori.tbl`，然后用 `BiocParallel::bplapply()` 对每个基因调用 `pseudotimeDE()`（`PseudotimeDE/R/runPseudotimeDE.R:40-118`）。真正的单基因检验在 `PseudotimeDE/R/PseudotimeDE.R:47-299`。

具体对应关系如下：

| 论文步骤 | 代码证据 | 说明 |
|---|---|---|
| 构建 NB-GAM spline | `PseudotimeDE/R/PseudotimeDE.R:81-82`, `PseudotimeDE/R/PseudotimeDE.R:319-339` | 使用 `expv ~ s(pseudotime, k = ..., bs = 'cr')` 和 `mgcv::gam`/`bam`。 |
| ZINB-GAM + EM | `PseudotimeDE/R/PseudotimeDE.R:151-179`, `PseudotimeDE/R/PseudotimeDE.R:391-470` | 支持强制 ZINB 或 AIC 自动选择。 |
| 观测统计量 $S_j$ | `PseudotimeDE/R/PseudotimeDE.R:190-203`, `PseudotimeDE/R/PseudotimeDE.R:479-567` | 复用/改写 mgcv 的 smooth-term test statistic。 |
| subsample 打乱伪时间 | `PseudotimeDE/R/PseudotimeDE.R:257-278` | 对每个 `sub.tbl` 元素执行 `sample(x$pseudotime)` 后重拟合。 |
| 经验 p 值 | `PseudotimeDE/R/PseudotimeDE.R:280-281` | 代码中的 `(sum(Tr <= boot_models$stat)+1)/(n.boot+1)` 等价于右尾计数。 |
| 参数 p 值 | `PseudotimeDE/R/PseudotimeDE.R:283-289`, `PseudotimeDE/R/PseudotimeDE.R:688-720` | 拟合 gamma 或两成分 gamma mixture。 |
| 可视化伪时间不确定性 | `PseudotimeDE/R/plotUncertainty.R:21-71` | 画每个细胞在 subsamples 中的伪时间分布。 |

上游工作流在 vignette 里展示：先用 Slingshot 对原始 LPS 数据推断伪时间，再抽取 80% 细胞、对每个 subsample 重跑 Slingshot，并用相关性检查方向是否需要翻转（`PseudotimeDE/vignettes/quickstart.Rmd:49-113`）。所以，从代码角度看，完整方法是“用户负责生成 `ori.tbl/sub.tbl`，包负责统计检验”。

### 图像证据怎么支持论文

本地图片只包含 Figs. 2-8，没有 Fig. 1 的本地图片。Fig. 2 直接显示了两类伪时间不确定性：单谱系内部的 pseudotime spread，以及 bifurcation topology 在 subsample 中可能失败或改变。Fig. 3 是 simulation benchmark，显示 PseudotimeDE 在 null p 值校准、FDP、AUROC、power 上的优势。Figs. 4-8 则是 LPS、胰岛 beta cell、bone marrow、NKT、cell-cycle 的真实数据/benchmark 支持（见 `figure_analysis.md`）。

### 结果和结论

论文报告，在 simulations 中，PseudotimeDE 的 null p 值最接近 Uniform [0,1]，FDP/FDR 控制更好，并且在多数设置下 AUROC 和 power 更好（`paper source/springer_html/paper.md:86-103`）。真实数据中，PseudotimeDE 找到的基因更容易富集到与对应生物过程相关的 GO/GSEA terms，例如 LPS 免疫反应、胰岛 beta cell 发育、骨髓分化和 NKT lineage-specific bulk gene sets（`paper source/springer_html/paper.md:109-180`）。

### 重要限制和代码边界

- **不是一键端到端轨迹工具。** 代码包不自动完成任意数据的伪时间推断；用户要自己用 Slingshot、Monocle3-PI 或其他方法构造 `ori.tbl/sub.tbl`。
- **适用场景偏向稳定谱系。** 论文认为 PseudotimeDE 更适合单谱系、循环数据，或少数清晰分离的谱系；如果 subsampling 后 topology 经常变化且无法对应，方法会变难用（`paper source/springer_html/paper.md:239-239`）。
- **本地 GitHub 快照缺少论文结果复现脚本。** 包里有 R 函数、vignettes、tests、示例数据和图形 helper，但没有找到生成论文 simulation/real-data panels 的完整脚本。论文把复现 source code/data 指向 Zenodo（`paper source/springer_html/paper.md:363-366`）。
- **wrapper 参数转发有代码 caveat。** `runPseudotimeDE()` 暴露了 `k`, `knots`, `fix.weight`, `aicdiff`, `seed`, `quant`, `usebam` 等参数，但内部调用 `pseudotimeDE()` 时没有把这些参数转发进去（`PseudotimeDE/R/runPseudotimeDE.R:40-56`, `PseudotimeDE/R/runPseudotimeDE.R:74-81`, `PseudotimeDE/R/runPseudotimeDE.R:98-105`）。单基因 `pseudotimeDE()` 本身支持这些参数（`PseudotimeDE/R/PseudotimeDE.R:47-60`）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PseudotimeDE Summary

### What Problem The Paper Solves

PseudotimeDE tests for genes whose expression changes along inferred pseudotime in scRNA-seq data. The paper argues that this downstream DE task is statistically fragile because most pseudotime methods return point estimates without uncertainty, while downstream tests then treat those estimates as fixed. That can produce invalid p-values, failed FDR control, or unnecessary power loss (`paper source/springer_html/paper.md:12-12`, `paper source/springer_html/paper.md:45-48`).

### Why Existing Methods Were Insufficient

The paper separates three limitations in prior approaches:

- Built-in DE functions in trajectory packages such as TSCAN, Slingshot, Monocle, and Monocle2 are tied to their own pseudotime engines and cannot generally consume arbitrary user-provided pseudotime (`paper source/springer_html/paper.md:36-36`).
- tradeSeq uses NB-GAM but its paper does not attach strong probabilistic interpretation to the p-values, making p-value-based FDR procedures problematic for this use case (`paper source/springer_html/paper.md:39-39`).
- Monocle3-DE accepts user-provided covariates but uses a GLM, which is less flexible than GAM for nonlinear expression-pseudotime relationships (`paper source/springer_html/paper.md:39-39`).

NBAMSeq and ImpulseDE2 are continuous-time bulk RNA-seq methods that can be adapted in principle, but the paper says their scRNA-seq pseudotime performance lacked benchmarking (`paper source/springer_html/paper.md:42-42`).

### Proposed Method

PseudotimeDE's core idea is to propagate pseudotime uncertainty into the null distribution of a gene-level smooth-effect statistic. The paper describes four steps: subsampling, pseudotime inference, model fitting, and hypothesis testing (`paper source/springer_html/paper.md:57-63`).

At the statistical core, PseudotimeDE fits NB-GAM, or optionally ZINB-GAM, for each gene. It tests $H_0: f_j(\cdot)=0$ against $H_1: f_j(\cdot)\neq 0$, computes a quadratic smooth-effect statistic $S_j$, then estimates the null distribution by permuting pseudotime vectors inferred from subsamples (`paper source/springer_html/paper.md:272-318`). It returns both empirical and high-resolution parametric p-values; the paper's results use the parametric p-values (`paper source/springer_html/paper.md:314-318`).

### Evaluation

The simulation benchmark uses dyntoy datasets and compares PseudotimeDE against tradeSeq, Monocle3-DE, NBAMSeq, and ImpulseDE2. In the highlighted simulations, PseudotimeDE shows the best null p-value calibration, better FDP behavior at target FDR 0.05, highest AUROC, and high power in most settings (`paper source/springer_html/paper.md:72-103`; `figure_analysis.md` Fig. 3).

Real-data applications cover LPS-stimulated dendritic cells, pancreatic beta-cell maturation, mouse bone marrow differentiation, natural killer T-cell subtypes, and a cell-cycle phase benchmark (`paper source/springer_html/paper.md:106-200`, `paper source/springer_html/paper.md:348-360`). The figures support the paper's claim that PseudotimeDE p-values lead to more biologically meaningful GO/GSEA results and better agreement with known cyclic or lineage-specific gene sets (`figure_analysis.md` Figs. 4-8).

### Code-Paper Match And Reproducibility

The cloned GitHub repository is an R package at commit `c278a487e11159b8c7f046f3943699e7ec232067`. Its core R code implements the gene-level NB/ZINB-GAM fit, smooth-term statistic, permutation null, empirical p-value, and gamma/gamma-mixture parametric p-value (`doc_code.md`).

The main paper-code boundary is that exported DE functions consume precomputed `ori.tbl` and `sub.tbl` rather than running pseudotime inference internally. The vignette demonstrates Slingshot-based original/subsample pseudotime construction, so the paper workflow is runnable as a user-level example, not as a single end-to-end package function (`PseudotimeDE/vignettes/quickstart.Rmd:49-134`; `PseudotimeDE/R/runPseudotimeDE.R:40-118`).

Reproducibility status: **method implementation is available, but paper-result reproduction is incomplete in this cloned snapshot**. The package includes examples, tests, package data, and helper plots, but no scripts were found for regenerating the published simulation and real-data figures. The paper states that source code and data for reproducing results are available from Zenodo (`paper source/springer_html/paper.md:363-366`), which was not part of the local code snapshot.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
