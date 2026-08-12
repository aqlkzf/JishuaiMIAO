---
layout: default
permalink: /paper-atlas/hetosgebench-57faa887/
title: "HEtoSGEBench"
nav: false
description: "HEtoSGEBench 的重要信息是：H&E 图像确实包含可用于预测部分空间基因表达的信息，但复杂模型并不天然更好；论文指出包含更多组件的复杂 deep-learning 架构并未在整体上优于简单方法，并且存在过拟合到染色/非生物图像模式的风险。因此，未来方法不仅要提高 spot-level accuracy，还要证明跨数据泛化、临床效用、可复现性和可用性。"
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
      <span>Nature Communications · 2025</span>
    </div>
    <h1>HEtoSGEBench</h1>
    <p>Benchmarking the translational potential of spatial gene expression prediction from histology</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-56618-y" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## HEtoSGEBench 方法中文解读

### 这篇论文解决什么问题？

空间转录组可以在组织切片坐标上测量基因表达，但实验成本和可及性限制了它在大规模临床病理图像中的应用。已有方法尝试从 H&E 病理图像预测 spatial gene expression (SGE)，即把图像 patch 映射到对应空间点位的基因表达向量。论文摘要说明，本研究系统复现并评估 11 个从组织学图像预测 SGE 的方法，使用 5 个空间转录组数据集，并用 TCGA 数据做外部验证；评价维度包括预测性能、泛化能力、转化潜力、可用性和计算效率（`paper source/nature_html/paper.md:9-12`）。

### 为什么需要这个 benchmark？

论文指出，现有 SGE-from-H&E 方法的评估往往由方法开发者自己完成，数据集、指标和实验框架不统一，因此缺少独立、全面、可比较的认识（`paper.md:21-35`）。HEtoSGEBench 的核心贡献不是提出一个新的预测模型，而是建立一个统一评估框架，回答：这些模型能否稳定预测空间表达？能否跨研究/跨平台泛化？能否用于 TCGA 这类只有 H&E 与 bulk RNA-seq 的临床数据？代码是否容易复现和迁移？

### 输入、输出和总体流程

图 1a 把任务画得很清楚：输入是 H&E 图像 patch，形状为 `w x h x 3`；机器学习模型输出 `1 x p` 的基因表达向量（`figure_01.png`；`paper.md:24-29`）。图 1b 给出五类评价：

1. Gene Expression Prediction：预测表达是否接近 ground truth SRT。
2. Model Generalisability：模型训练于一个空间转录组数据集后，能否用于新数据/TCGA 图像。
3. Clinical Translational Impact：预测出来的表达是否能辅助病人生存/风险分析。
4. User Accessibility：代码、文档、接口、复现难度。
5. Computational Efficiency：运行时间、资源消耗和可扩展性。

可以把 benchmark 理解为如下管线：

```text
H&E slide + SRT matrix
    -> spot-centered image patches + gene filtering/normalization
    -> train/validation/test 或 cross-study split
    -> 11 个 SGE 预测方法分别产生 predicted SGE
    -> 表达预测指标：PCC、MI、SSIM、AUC、NRMSE、JS divergence 等
    -> TCGA 图像：tile 预测后平均成 pseudobulk GE
    -> 与 TCGA bulk RNA-seq 相关性比较
    -> 用 pseudobulk GE 建 Cox 生存模型
    -> 加入 usability 和 efficiency 分数
    -> metric rank -> category rank -> final rank
```

### 数据集与方法选择

方法选择标准是：截至 2024 年 1 月，能够从 histology image 预测 SRT 的公开论文/预印本；没有代码、说明不清、难以在新数据执行、多模态输入、或预测 scRNA/bulk RNA-seq 而不是 ST 的方法被排除（`paper.md:166-171`）。最终评估 11 个方法：GeneCodeR、ST-Net、DeepPT、Hist2ST、HisToGene、DeepSpaCE、EGNv1、EGNv2、TCGN、THItoGene、iStar。

数据包括 HER2+ ST、cSCC ST、TCGA-BRCA、10x Visium breast cancer 和 Visium kidney。论文详细说明了 patch 大小、HVG/表达过滤、TCGA 图像筛选和 bulk RNA-seq 下载方式（`paper.md:174-238`）。

### 关键评价指标

论文强调使用 scale-independent metrics，因为不同模型可能对表达值做不同归一化/变换，直接反变换会引入偏差（`paper.md:356-359`）。代码中 `benchmarkUtils.R` 实现 normalized mutual information、NRMSE、JS divergence、SSIM、AUC 等函数（`HEtoSGEBench/benchmark pipeline/benchmarkUtils.R:28-109`）；`00-CombineDat.Rmd` 把预测表达和 ground truth 合并后计算 Pearson/Spearman correlation、RMSE、MI、JS、NRMSE、SSIM、多个阈值 AUC（`HEtoSGEBench/benchmark pipeline/00-CombineDat.Rmd:66-109`）。

对于 TCGA 泛化，模型先在 H&E tile 上预测表达，然后对一张图像内的 tile 求平均得到 pseudobulk GE，并做变换：

$${x^{\prime}}=\log (\max (0,x)+1)$$

其中 `x` 是某个基因在某张 TCGA 图像上的 predicted pseudobulk 值（`paper.md:383-386`）。之后与真实 TCGA bulk RNA-seq 做 patient-level correlation（`paper.md:386-389`）。

临床转化部分把 TCGA 样本分为 HER2+、TNBC、luminal 三类乳腺癌；每类中用 predicted pseudobulk GE 和 RNA-seq GE 分别构建 Cox 生存模型，用 C-index 和 log-rank p-value 评价，并使用 3-fold CV 重复 100 次（`paper.md:390-400`）。

### 图的含义

- **Fig. 1**：定义任务和五大评价维度。
- **Fig. 2**：展示 11 个方法的实现特征、参数量、类别排名以及 PCC/MI/SSIM/AUC 分布。
- **Fig. 3**：比较 all genes、HVGs、SVGs 以及 Visium 外部数据上的性能差异。
- **Fig. 4**：把 TCGA 图像质量、pseudobulk 相关性、生存 C-index、KM 曲线联系起来，展示转化潜力。
- **Fig. 5**：从 availability、code quality、documentation、reproducibility、generalisability 等角度评分，说明“能不能用、好不好复现”本身也是 benchmark 的一部分。

### 代码仓库与论文的匹配程度

公开仓库 `SydneyBioX/HEtoSGEBench` 与 benchmark 评价逻辑匹配度为 **medium**。仓库 README 明确列出五类评价和 Rmd 运行顺序，并要求从 Zenodo DOI `10.5281/zenodo.14602489` 下载 processed datasets（`HEtoSGEBench/README.md:14-26`）。仓库主要包含评价和画图脚本：

- `00-CombineDat.Rmd`：计算预测表达与 ground truth 的指标。
- `01-BenchmarkUsability.Rmd`：生成 usability plot 和 score。
- `02-BenchmarkPredictedExprs.Rmd`：生成 ST/Visium SGE metrics。
- `03-BenchmarkTCGA.Rmd`：TCGA pseudobulk 相关性和生存分析。
- `04-BenchmarkRanks.Rmd`：整合六类排名并画 heatmap。

缺口是：仓库不是从 raw H&E/SRT 到 11 个模型训练预测的完整一键复现系统；它依赖 Zenodo processed data，也没有包含所有外部方法的训练实现。因此它更像“benchmark evaluation/figure reproduction pipeline”，而不是每个模型的完整训练库。

### 核心结论

HEtoSGEBench 的重要信息是：H&E 图像确实包含可用于预测部分空间基因表达的信息，但复杂模型并不天然更好；论文指出包含更多组件的复杂 deep-learning 架构并未在整体上优于简单方法，并且存在过拟合到染色/非生物图像模式的风险（`paper.md:148-151`）。因此，未来方法不仅要提高 spot-level accuracy，还要证明跨数据泛化、临床效用、可复现性和可用性。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## HEtoSGEBench Summary

### Problem

This Nature Communications paper benchmarks whether spatial gene expression (SGE) can be predicted from routine H&E histology with enough reliability to be useful beyond the original spatial-transcriptomics experiments. The abstract frames the task as using paired histology images to predict spatial expression and evaluates eleven methods on five SRT datasets plus external TCGA validation (`paper source/nature_html/paper.md:9-12`).

### Why this benchmark was needed

Prior SGE-from-H&E methods were usually evaluated by their own developers, on different datasets and with different criteria. The paper states that there was no consistent detailed framework for comparing performance, stability and broader applicability (`paper.md:21-35`). The benchmark therefore focuses not only on spot-level prediction accuracy but also on cross-study generalisation, clinical translational impact, usability and computational efficiency.

### What HEtoSGEBench does

HEtoSGEBench is an evaluation framework for eleven histology-to-SGE methods: GeneCodeR, ST-Net, DeepPT, Hist2ST, HisToGene, DeepSpaCE, EGNv1, EGNv2, TCGN, THItoGene and iStar. Fig. 1 shows the canonical machine-learning task: an RGB histology patch is mapped to a `1 x p` gene-expression vector; the same figure lists five benchmark categories (`figure_01.png`; `paper.md:24-29`).

The evaluation uses HER2+ ST, cSCC ST, TCGA-BRCA, Visium breast cancer and Visium kidney datasets, with consistent patch extraction/gene filtering and cross-validation or cross-study splits (`paper.md:174-238`). Category ranks are computed by ranking methods on each metric, averaging within categories, then averaging over categories (`paper.md:340-353`).

### Main evaluation logic

- **SGE prediction**: scale-independent metrics compare predicted and ground-truth expression because models use different transformations (`paper.md:356-359`). Code computes Pearson/Spearman correlation, RMSE, normalized MI, JS divergence, NRMSE, SSIM and thresholded AUC (`HEtoSGEBench/benchmark pipeline/00-CombineDat.Rmd:66-109`; `benchmarkUtils.R:28-109`).
- **Generalisability**: TCGA H&E tiles are predicted, averaged into pseudobulk expression, transformed with `x'=log(max(0,x)+1)`, and compared to matched bulk RNA-seq (`paper.md:383-389`).
- **Clinical translational impact**: predicted pseudobulk expression is used for breast-cancer subtype survival models, comparing C-index and log-rank p-values against RNA-seq models (`paper.md:390-400`).
- **Usability/efficiency**: usability scoring covers availability, code quality, documentation, reproducibility and generalisability; the code computes weighted scores from a spreadsheet (`HEtoSGEBench/benchmark pipeline/01-BenchmarkUsability.Rmd:55-89`).

### Key findings

The benchmark supports that H&E-derived models can recover some biologically relevant SGE patterns and show positive TCGA pseudobulk correlations, but it does not show that more complex architectures always win. The paper explicitly observes that more complex deep-learning architectures were not superior across the benchmark and highlights overfitting/stain-artifact concerns (`paper.md:148-151`). Fig. 2 summarizes method characteristics and overall ranks; Fig. 3 shows gene-set and Visium performance variation; Fig. 4 connects TCGA predictions to pseudobulk correlation and survival; Fig. 5 exposes major usability/reproducibility differences.

### Reproducibility

The public code repository (`https://github.com/SydneyBioX/HEtoSGEBench`, commit `4706dc8e8e8b7cb2387eb32929d8b79d289deac3`) provides R/Rmd scripts for benchmark evaluation and figure reproduction. Its README states that processed datasets are required from Zenodo DOI `10.5281/zenodo.14602489` and lists the execution order: `00-CombineDat.Rmd`, `01-BenchmarkUsability.Rmd`, `02-BenchmarkPredictedExprs.Rmd`, `03-BenchmarkTCGA.Rmd`, `04-BenchmarkRanks.Rmd` (`HEtoSGEBench/README.md:14-26`).

Code-paper fidelity is **medium**: the public repository matches the benchmark evaluation/ranking pipeline, but does not include all raw training implementations for the eleven external SGE predictors. CodeGraph was initialized but indexed zero files for the R/Rmd repository, so final code claims are based on direct source-line reads.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
