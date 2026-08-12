---
layout: default
permalink: /paper-atlas/scdesign3-931b1b37/
title: "scDesign3"
nav: false
description: "scDesign3 是一个参考数据驱动的单细胞/空间组学模拟器：它把真实数据表示为特征矩阵 Y、细胞状态协变量 X 和可选实验设计协变量 Z，先为每个特征拟合条件边缘分布，再用 copula 建模特征间依赖，最后在给定或新生成的协变量上采样合成数据。论文主张这个统一概率模型可用于真实感模拟、拟合优度评估，以及构造带有已知条件变化的正/负控制数据；本地 R 包实现了这条核心模拟流水线。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Biotechnology · 2024</span>
    </div>
    <h1>scDesign3</h1>
    <p>scDesign3 generates realistic in silico data for multimodal single-cell and spatial omics</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-023-01772-1" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scDesign3 方法解释

### 证据边界

本文档只使用本工作区内可复核的材料：主论文 Markdown、抓取到的图像、克隆的 `scDesign3` R 包源码，以及已生成的代码/方法/图表分析文档。补充材料 Markdown 不存在，记为 `SUPP_MD=none`；本地 `.codegraph/codegraph.db` 存在但索引为空，因此代码结论来自直接读取源码，而不是 CodeGraph。论文还说明完整结果复现源码在 Zenodo，当前本地代码目录不是完整论文复现实验仓库。

下面把“论文方法主张”“本地代码核实行为”和“缺失证据/解释性判断”分开描述。

### 一句话概括

scDesign3 是一个参考数据驱动的单细胞/空间组学模拟器：它把真实数据表示为特征矩阵 **Y**、细胞状态协变量 **X** 和可选实验设计协变量 **Z**，先为每个特征拟合条件边缘分布，再用 copula 建模特征间依赖，最后在给定或新生成的协变量上采样合成数据。论文主张这个统一概率模型可用于真实感模拟、拟合优度评估，以及构造带有已知条件变化的正/负控制数据；本地 R 包实现了这条核心模拟流水线。

### 论文要解决的问题

论文把背景问题定义为：单细胞和空间组学已经覆盖离散细胞类型、连续轨迹、空间位置、多组学特征和实验设计因素，但基准评测需要既有 ground truth 又像真实数据的 in silico 数据。论文指出，以前参考数据驱动的模拟器主要集中在 scRNA-seq、离散细胞类型或较窄设定；对连续轨迹、多组学和空间转录组的支持不足。scDesign3 的目标是用一个统一的概率模型覆盖细胞状态、实验设计、特征模态和空间位置等设定。

这不是从零设定参数的 de novo 模拟器。它依赖一份真实参考数据来学习参数，因此输出的真实性和可解释性都取决于参考数据、输入协变量、选择的边缘分布族、公式和相关性分组。

### 输入表示

论文定义三个输入矩阵：

- **Y**：细胞乘特征矩阵，行是细胞，列是基因、peak、蛋白或其他特征；对测序数据通常是 count matrix。
- **X**：细胞状态协变量，可以是细胞类型、伪时间、空间坐标或其他表示细胞状态的变量。
- **Z**：可选实验设计协变量，例如 batch、condition、sex、age 等。

代码中的入口函数 `scdesign3()` 接收 `SingleCellExperiment` 对象、`celltype`、`pseudotime`、`spatial`、`other_covariates`、`mu_formula`、`sigma_formula`、`family_use`、`corr_formula`、`copula` 等参数，然后依次调用 `construct_data()`、`fit_marginal()`、`fit_copula()`、`extract_para()` 和 `simu_new()`（`scDesign3/R/scdesign3.R:83-280`）。`construct_data()` 从 assay 和 `colData` 中取出 count matrix 与协变量，要求 celltype/pseudotime/spatial 至少提供一种，支持追加 `condition` 和 `batch` 等设计协变量，并根据 `corr_formula` 形成 copula 分组（`scDesign3/R/construct_data.R:48-182`）。

因此，scDesign3 的关键假设是：用户已经有可信的状态协变量或候选状态协变量。它可以评价给定细胞状态结构的拟合优度，但本地核心代码并不把“推断伪时间/聚类/空间坐标”作为主流水线的第一步。

### 核心概率模型

论文的核心模型是两层结构：

1. 对每个特征单独拟合条件边缘分布。
2. 用 copula 在边缘分布之上连接特征间依赖。

#### 特征级边缘分布

论文假设每个特征 \(j\) 在细胞 \(i\) 中的观测 \(Y_{ij}\)，给定状态协变量 \(\mathbf{x}_i\) 和设计协变量 \(\mathbf{z}_i\)，服从特征专属分布：

```text
Y_ij | x_i, z_i ~ F_j(. | x_i, z_i; mu_ij, sigma_ij, p_ij)
```

其中 \(F_j\) 可以随特征而不同，参数 \(\mu_{ij}\)、\(\sigma_{ij}\) 和 \(p_{ij}\) 可以随细胞与特征变化。论文公式 (1) 把均值、尺度/离散度、零膨胀概率分别写成状态协变量、batch 和 condition 的函数。均值参数通过特征特定 link function 建模；尺度参数使用 log link；零膨胀参数使用 logit link。论文还说明，实际参数并不一定同时存在，取决于所选分布族。

本地代码对应 `fit_marginal()`。它把用户给出的 `mu_formula` 和 `sigma_formula` 拼成 `gene ~ ...` 形式，识别 `s()` 或 `te()` 平滑项，并转换为 scDesign3 自定义的 `ga()` 或 `ba()` GAMLSS smoother（`scDesign3/R/fit_marginal.R:52-205`）。对每个基因，代码按 `family_use` 选择高斯、泊松、负二项、零膨胀泊松或零膨胀负二项等模型。若 GAMLSS 拟合失败或返回异常预测值，代码会退回到 `mgcv::gam` 的拟合结果（`scDesign3/R/fit_marginal.R:500-578`）。

这里的“解释性”主要来自每个特征的参数函数：均值趋势可以解释为沿伪时间或空间坐标的表达变化；batch/condition 项可以解释为实验设计效应；尺度和零膨胀参数则提供分布形状层面的信息。论文 Fig. 2b,c 展示了伪时间趋势和空间表达趋势，Fig. 2f,g,h 展示了通过改变模型参数或模型假设构造 synthetic controls 的例子。

#### 特征间依赖

边缘分布拟合后，scDesign3 用 copula 建模特征间相关性。论文描述了 Gaussian copula、vine copula，以及对离散数据使用 distributional transform 来得到适合 copula 拟合的连续化残差/分位数。

本地代码在 `fit_copula()` 中实现这一步。若选择 Gaussian copula，代码先把每个特征的观测通过 fitted marginal 的 CDF 转成标准正态残差矩阵；若选择 vine copula，代码转成 \([0,1]\) 上的 uniform quantile 矩阵（`scDesign3/R/fit_copula.R:181-214`, `scDesign3/R/fit_copula.R:431-861`）。对于离散计数，`DT=TRUE` 时会在 \(F(y-1)\) 与 \(F(y)\) 之间随机插值，避免离散 CDF 的阶梯结构直接进入 copula（`scDesign3/R/fit_copula.R:546-588`, `scDesign3/R/fit_copula.R:765-805`）。

依赖结构按 `corr_group` 分组拟合。Gaussian 分支计算相关矩阵并返回每组的 correlation/copula 对象；vine 分支调用 `rvinecopulib::vinecop()` 拟合 vine copula（`scDesign3/R/fit_copula.R:241-363`）。代码还把边缘 AIC/BIC 与 copula AIC/BIC 组合成 `aic.marginal`、`aic.copula`、`aic.total` 和对应 BIC（`scDesign3/R/fit_copula.R:334-346`, `scDesign3/R/fit_copula.R:865-912`）。

### 生成合成数据的流程

本地包的主流水线可以概括为：

```text
SingleCellExperiment + covariates
  -> construct_data()
  -> fit_marginal()
  -> fit_copula()
  -> extract_para()
  -> simu_new()
  -> synthetic count matrix + new covariates + AIC/BIC + optional fitted models
```

`extract_para()` 对旧协变量或新协变量预测每个细胞-特征组合的均值、尺度/离散度和零膨胀参数，并整理成 `mean_mat`、`sigma_mat`、`zero_mat`（`scDesign3/R/extract_para.R:70-317`）。`simu_new()` 再从 copula 或已有 quantile matrix 采样多变量分位数，并调用不同分布族的 inverse CDF 生成新观测值，例如 `qpois`、`qNBI`、`qZIP`、`qZINBI` 等；最后返回 feature-by-cell 的新矩阵，必要时保持 sparse matrix 格式（`scDesign3/R/simu_new.R:91-365`）。

因此，代码核实的核心行为是“先拟合可解释边缘参数，再拟合特征间依赖，再在协变量上采样”。这和论文方法部分的统计建模描述一致。

### 拟合优度与模型解释

论文把 AIC/BIC 用作无监督拟合优度指标，尝试评价给定细胞结构是否更符合表达数据。例如 Fig. 2e 展示 rBIC 与真实伪时间 \(R^2\) 的负相关；Extended Data Fig. 10 扩展到伪时间、聚类和空间位置，并显示并非所有面板都同样强，空间位置中 rAIC 比 rBIC 更适合一些复杂空间模式。

代码层面，`scdesign3()` 直接返回 `model_aic` 和 `model_bic`（`scDesign3/R/scdesign3.R:271-280`），`fit_copula()` 明确把 marginal 与 copula 的 AIC/BIC 合并返回。包还导出 `perform_lrt()` 用于嵌套模型的似然比检验，`plot_reduceddim()` 用于把模拟数据投影到已有降维空间。这些支持论文中的模型选择、参数解释和可视化分析，但本地仓库没有完整 figure-by-figure 的复现实验脚本；论文指出这些结果复现源码在 Zenodo。

### 图表证据如何支撑方法

Fig. 1 是“模拟能力”证据：它覆盖轨迹、空间转录组、spot-level 空间混合、ATAC/CITE/multiomics 等场景。图中呈现的是论文报告的下游结果，例如 mLISI、Pearson correlation、UMAP/PCA 和 spatial pattern 相似度；当前工作区只验证了图像和图注，不重新运行这些 benchmark。

Fig. 2 是“解释能力”证据：它把参数趋势、相关结构、拟合优度、模型改写和条件/batch 效应放在一起，说明 scDesign3 不只是生成合成矩阵，还能通过可解释参数和 likelihood/AIC/BIC 连接到统计解释。

Extended Data Figs. 1-10 补充了 scRNA 轨迹 benchmark、空间预测、spot deconvolution、ATAC、CITE 和 GOF 的更多案例。它们支持论文的广泛适用性主张，但由于 `SUPP_MD` 和 Zenodo 复现代码不在本地，这些图的数值结论在本工作区属于“论文报告”，不是本地重跑验证。

### 代码匹配结论

本地代码与论文中央方法的匹配度高。已核实的精确匹配包括：

- 输入构造：从 `SingleCellExperiment` 中提取 count matrix、细胞状态协变量和设计协变量。
- 边缘模型：按特征拟合 GAM/GAMLSS，支持平滑函数、不同分布族、尺度参数和零膨胀参数。
- 依赖模型：通过 distributional transform 转换残差/分位数，并支持 Gaussian 或 vine copula。
- 生成步骤：预测参数、采样 copula 分位数、通过 inverse CDF 生成合成 count/feature 矩阵。
- 拟合优度：返回模型 AIC/BIC，和论文的无监督 GOF 思路一致。

部分匹配或缺失包括：

- 论文中的完整 benchmark、全部 figure 脚本和数据处理流程不在本地代码目录中；论文指向 Zenodo。
- 补充材料 Markdown 不存在，因此 Supplementary Methods/Tables 的细节只能从主文线索和源码推断，不能当成本地已读证据。
- 本地 CodeGraph 索引为空，因此没有结构化调用图证据；代码结论来自直接源码阅读。

### 实用理解

把 scDesign3 放进方法图谱时，最准确的定位是：参考数据驱动、协变量条件化、概率模型可解释的 single-cell/spatial omics simulator。它不是单纯复制真实矩阵，也不是只模拟均值趋势；它把每个特征的边缘分布和特征间依赖拆开拟合，再重新组合生成数据。

这种设计带来两个优势。第一，用户可以通过改写 covariate 或参数函数生成有控制变量的 synthetic controls，例如保持或消除 batch effect、设置条件差异、构造 null/alternative。第二，AIC/BIC 和 likelihood 让同一个模型可用于评估候选细胞状态结构的合理性。

主要风险也来自同一设计：如果输入协变量、公式、分布族或相关性分组不合适，模拟结果会继承这些设定偏差；如果真实数据规模或复杂度超出模型假设，局部拟合优度并不保证所有下游 benchmark 都真实。论文图表展示了广泛案例，但本地工作区只能确认核心包实现了论文主方法，不能确认所有论文数值都可从当前仓库独立复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scDesign3 Summary

scDesign3 is a reference-based statistical simulator for single-cell and spatial omics. It learns feature-wise marginal distributions and feature-dependence structure from real data, then generates synthetic data under chosen cell-state and design covariates. The paper also uses the same probabilistic model for interpretation: parameter trends, gene-gene correlations, likelihood-based goodness-of-fit of cell latent structures, and hypothesis-specific synthetic controls (`paper.md:12-12`, `paper.md:27-28`, `paper.md:70-85`).

### Problem

Single-cell and spatial omics benchmarking needs synthetic data with realistic structure and known controls. The paper argues that earlier simulators were limited: reference-based scRNA-seq simulators were generally more realistic than de novo simulators, but few handled continuous trajectories, and realistic simulators were lacking for non-RNA modalities, multiomics, and spatial transcriptomics (`paper.md:21-24`). scDesign3 is intended to fill that gap with one model family that can handle cell types, trajectories, spatial coordinates, feature modalities, and experimental designs (`paper.md:27-28`).

### Method

The input is a cell-by-feature matrix **Y**, a cell-by-state-covariate matrix **X** such as cell type, pseudotime, or spatial coordinates, and optional design covariates **Z** such as batch or condition (`paper.md:97-106`). For each feature, scDesign3 fits a conditional marginal distribution with GAMLSS/GAM parameters for mean, scale/dispersion, and zero inflation when needed (`paper.md:112-149`). Supported families include Gaussian, Bernoulli, Poisson, negative binomial, ZIP, and ZINB (`paper.md:138-138`).

The joint feature distribution is modeled by a copula over fitted marginal CDF values. The paper supports Gaussian copulas and vine copulas, with a distributional transformation for discrete data (`paper.md:155-197`). Synthetic generation samples a copula vector for each synthetic cell, predicts that cell's marginal parameters, and applies inverse marginal CDFs feature by feature (`paper.md:247-280`). Because parameters are explicit, users can alter mean, batch, or condition effects before simulation (`paper.md:283-301`).

### Evaluation

The paper evaluates simulation realism in four settings: scRNA-seq trajectories, spatial transcriptomics, single-cell epigenomics, and multiomics (`paper.md:49-64`). It reports better trajectory simulation than scGAN, muscat, SPARSim, and ZINB-WaVE, spatial expression-map preservation, realistic scATAC/CITE-seq examples, and unmatched RNA+methylation multiomics generation (`paper.md:55-64`). It also evaluates interpretation use cases: gene trend/correlation estimation, AIC/BIC-based goodness-of-fit for clusters/pseudotime/spatial locations, and altered synthetic controls for condition, batch, and null/alternative cell-type hypotheses (`paper.md:70-85`, `paper.md:390-420`).

The figure evidence supports those claims visually. Fig. 1 summarizes broad simulation domains and shows real-vs-synthetic resemblance across modalities; Fig. 2 shows parameter interpretation, model selection, and model alteration; Extended Data Fig. 10 shows negative relationships between marginal AIC/BIC and supervised quality metrics in the tested latent-structure settings (`figure_analysis.md`).

### Code Match and Reproducibility

The local GitHub package snapshot implements the central simulator with high fidelity. The wrapper `scdesign3()` calls `construct_data()`, `fit_marginal()`, `fit_copula()`, `extract_para()`, and `simu_new()` in the same conceptual order as the paper pipeline (`scDesign3/R/scdesign3.R:116-280`). The code verifies feature-wise GAM/GAMLSS marginals, Gaussian/vine copula fitting, distributional transformation, decomposed AIC/BIC, parameter extraction, and inverse-CDF simulation (`doc_code.md`).

Important limits remain. `SUPP_MD` is not present. The paper states that result-reproduction source code and preprocessed datasets are available in Zenodo, but this workspace contains only the GitHub R package snapshot (`paper.md:441-450`). The workspace-local CodeGraph DB exists but was empty, so all code claims were verified by direct R source reads. Figure-level exact reproduction is therefore **Not found** locally, even though the package-level method implementation is strong.

### Bottom Line

scDesign3's main contribution is a unified, interpretable probabilistic simulator: marginal GAM/GAMLSS models capture how each feature depends on biological/design covariates, copulas preserve cross-feature dependence, and inverse-CDF sampling produces synthetic omics matrices under user-specified conditions. The local package strongly supports the core method, while paper-specific benchmark scripts and supplementary materials are external/missing in this workspace.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
