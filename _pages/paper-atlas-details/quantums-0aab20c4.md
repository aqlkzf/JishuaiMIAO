---
layout: default
permalink: /paper-atlas/quantums-0aab20c4/
title: "QuantUMS"
nav: false
description: "QuantUMS 解决的是 DIA 蛋白质组学里的“定量值是否可信”问题：同一个 peptide precursor 会有 MS1 母离子信号和多个 MS/MS fragment 信号，但这些信号会受噪声、共洗脱、共碎裂等干扰影响。论文声称 QuantUMS 用信号强度和质量分数来估计每个定量通道的偏差和方差，再做反方差加权聚合，从而同时输出 precursor/protein quantity 和 quantity quality。"
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
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>QuantUMS</h1>
    <p>Accurate quantification in proteomics with QuantUMS</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-026-03131-2" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for QuantUMS">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## QuantUMS 方法中文解读

### 一句话概览

QuantUMS 解决的是 DIA 蛋白质组学里的“定量值是否可信”问题：同一个 peptide precursor 会有 MS1 母离子信号和多个 MS/MS fragment 信号，但这些信号会受噪声、共洗脱、共碎裂等干扰影响。论文声称 QuantUMS 用信号强度和质量分数来估计每个定量通道的偏差和方差，再做反方差加权聚合，从而同时输出 precursor/protein quantity 和 quantity quality。

### 1. 生物学问题与建模目标

在 LC-MS/MS bottom-up proteomics 中，鉴定到某个 precursor/protein 不等于它的定量值准确。legacy DIA-NN 主要聚合少数高质量 fragment，可能丢弃 MS1 信息，也可能无法处理某次 acquisition 中出现的局部干扰。QuantUMS 的目标不是发现新的生物机制，而是减少技术定量误差，尤其是 ratio compression，并给每个数量值一个质量分数，帮助后续 differential expression 分析过滤低可信定量。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| 输入信号 | MS1, MS/MS fragments | 同一 precursor 的多个定量通道 | `doc_method.md`, `doc_code.md` |
| 质量分数 | $C$, `corr`, `Ms1.Profile.Corr`, `Fr.*.Score` | 特征信号的 elution-profile 质量/相关性 | `QuantUMS_standalone/diann-output-config-16-threads.txt:7-13` |
| 识别置信度 | `Q.Value`, `PEP` | 控制哪些 precursor 可用于训练/定量 | `doc_code.md` |
| 输出 | `QuantUMS.Feature.Quantity/Quality` | precursor 数量与质量 | `QuantUMS_standalone/quantums.cpp:3024-3027` |
| 输出 | `QuantUMS.Protein.Quantity/Quality` | protein 数量与质量 | `QuantUMS_standalone/quantums.cpp:3166-3169` |

### 3. 方法主流程

QuantUMS 先读取 DIA-NN 导出的 `.parquet` report，把 run、precursor、protein、Q.Value、PEP、MS1 和 fragment 列索引起来。对每个信号 $S$ 和质量分数 $C$，它构造 $T_S=S^{-1}$、$T_C=1-\sqrt C$、$T_{S,C}=\sqrt{T_ST_C}$，用这些量估计 log-bias 和 log-variance。随后先校正信号偏差，再把不同 run 和不同 feature 的估计用反方差权重合并。超参数不是人工固定，而是通过比较同一 precursor 不同 feature 给出的数量估计来学习：一部分 loss 追求 feature 之间一致，另一部分 loss 追求去除 ratio compression。最后，protein 层面使用 variance-aware MaxLFQ 思路，把 precursor ratio 做加权聚合。

### 4. 数学目标与直觉

核心误差模型是：

$$
Z=\log S=Z_{true}+\varepsilon
$$

如果能估计 $\mathbb{E}[\varepsilon]$，就可以减去 bias；如果能估计 $\operatorname{Var}(\varepsilon)$，就可以让低方差信号权重大、高方差信号权重小。加权平均使用：

$$
\mathrm{WA}\{Z_i\}=\frac{\sum_i \operatorname{var}_i^{-1}Z_i}{\sum_i \operatorname{var}_i^{-1}}
$$

统计直觉很直接：多个通道都在测同一个 precursor，它们彼此不一致时就暴露了定量误差；QuantUMS 用这种“内部一致性”来调参，而不是依赖实验设计标签。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| 读取 DIA-NN report | `QuantUMS_standalone/quantums.cpp:2895-2999` | 读取 `.parquet`，填充 run/precursor/MS1/fragment 数据 | Exact |
| bias/variance transform | `QuantUMS_standalone/quantums.cpp:1584-1594`, `1711-1749` | 根据 signal 和 corr 构建误差项并校正 log signal | Partial |
| 反方差聚合 | `QuantUMS_standalone/quantums.cpp:1760-1803`, `2113-2127` | `weight = 1 / var` 后聚合 MS1/MS2/fragment | Exact |
| loss 与梯度下降 | `QuantUMS_standalone/quantums.cpp:2308-2708` | precision/accuracy loss，加 Armijo backtracking | Exact |
| protein 量化 | `QuantUMS_standalone/quantums.cpp:2735-2880` | 加权 median ratio + 线性求解 + protein quality | Exact |

重要差异：论文/补充材料说 MS1 和 MS/MS 的超参数分别优化，并提到 13 个参数；OSF standalone 源码中可见的是 7 个 coefficient slot，而且 `MSLevel` 没有明显驱动独立参数分支。因此这里应写作 Partial，而不是把论文描述和源码完全等同。

### 6. 结果如何解读

Fig. 1 显示了算法流程和 mixed-species ratio benchmark：legacy 模式下 *E. coli* ratio compression 更明显，QuantUMS high-accuracy 更接近期望比例；质量过滤后保留下来的 protein ratio 更集中。Fig. 2 显示 QuantUMS 在 fibroblast 和 CLL 数据中能在相同 BH FDR 下发现更多 DE proteins，但这不等于所有新增 DE 都被独立验证。论文也承认 QuantUMS 主要降低 LC-MS 技术误差；当生物差异或样本制备差异更强时，收益会变小。

### 7. 局限性与未验证部分

代码可验证的是 OSF standalone QuantUMS 核心算法，不是完整 DIA-NN 产品源码。figshare 上的 figure scripts 和分析 reports 在本环境中被 AWS WAF challenge 阻挡，未能下载检查，所以图形复现脚本是 `Not found`。PRIDE 原始数据也没有下载。补充材料 OCR 中有少数公式符号失真，严谨复述公式时需要回看 PDF。

### 8. 快速阅读路线

先读 `summary.md` 把握论文贡献和复现评分；再读 `doc_method.md` 理解数学链条；需要源码对应时读 `doc_code.md`，尤其注意 7 vs 13 参数差异；看结果时读 `figure_analysis.md`；需要追踪原始证据和缺口时读 `claude_notes.md`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## QuantUMS

**Paper:** Accurate quantification in proteomics with QuantUMS
**Journal / year:** Nature Biotechnology, 2026
**DOI:** 10.1038/s41587-026-03131-2
**Category:** machine_learning_algorithm
**Code:** OSF standalone/source archive, extracted into `QuantUMS_standalone/`

### Motivation And Novelty

Mass-spectrometry-based DIA proteomics can identify many peptides and proteins, but quantification quality is harder to control than identification error. Legacy DIA-NN quantification aggregates selected fragment signals, which can discard useful MS1 evidence and can be biased by run-specific interferences. The result is ratio compression, weaker quantitative accuracy, and lower confidence in downstream differential abundance analysis.

QuantUMS introduces uncertainty-aware DIA quantification. It models each quantitative feature's log-bias and log-variance from signal intensity and a quality score, corrects bias, aggregates MS1 and MS/MS features with inverse-variance weighting, and propagates uncertainty into precursor and protein quality metrics. The novelty is not a new biological model; it is a machine-learning-tuned measurement model for more accurate and quality-controlled protein quantities.

### Method Overview

QuantUMS takes DIA-NN-exported quantitative evidence: run IDs, precursor IDs, protein groups, q-values, PEP, MS1 intensity/correlation and fragment intensity/correlation columns. For each feature signal $S$ and quality score $C$, it constructs transformed predictors such as $T_S=S^{-1}$ and $T_C=1-\sqrt C$, then estimates log-bias and log-variance. Bias-corrected feature signals are aggregated across acquisitions and features using inverse-variance weights.

The hyperparameters are learned from the data. QuantUMS compares quantities inferred from parallel quantitative channels of the same precursor, using a precision term for cross-feature concordance and an accuracy term designed to reduce ratio compression. It offers high-precision and high-accuracy modes. After precursor quantification, it performs a variance-aware MaxLFQ-like protein aggregation and emits `QuantUMS.Feature.Quantity`, `QuantUMS.Feature.Quality`, `QuantUMS.Protein.Quantity` and `QuantUMS.Protein.Quality`.

The public OSF standalone code closely implements the core algorithm, but with a notable caveat: the paper describes MS1/MS2-separated hyperparameters and 13 total parameters, while the released standalone source exposes seven coefficient slots and does not visibly branch the signal-scale transform by `MSLevel`. This is a concrete paper-code partial match rather than a full exact match.

### Evaluation

The paper evaluates QuantUMS on several DIA proteomics settings:

- Mixed-species benchmarks with known ratios, including K562 / *E. coli*, LFQbench-style mixtures, and Orbitrap Astral data.
- Varying sample loading amounts and experiment sizes, including a 144-run dia-PASEF benchmark.
- Differential expression analyses on fibroblast perturbation and chronic lymphocytic leukemia datasets.

Baselines include legacy DIA-NN quantification from DIA-NN (Nature Methods, 2020), previous-generation DIA-NN 1.8 output in the fibroblast comparison, and MaxLFQ-derived ideas from earlier label-free quantification literature. The key reported effects are reduced ratio compression, improved mean absolute deviation in mixed-species ratios, quality filtering that enriches accurate quantities, and more detected DE proteins at matched estimated FDR in selected biological datasets.

Figure 1 supports the uncertainty-aware aggregation story and the mixed-species ratio improvement. Figure 2 supports downstream DE sensitivity gains, especially in fibroblasts and selected CLL comparisons. The figures do not prove universal improvement across all proteomics experiments; the paper itself notes that biological/sample variation can dominate measurement error.

### Reproducibility

**Rating: 3 / 5**

Positive evidence:

- The paper provides source code through OSF.
- The extracted standalone code verifies the main computational path: Parquet input, precursor feature quantification, automatic differentiation, precision/accuracy loss, Armijo backtracking, quality scoring and protein-level aggregation.
- The paper lists PRIDE datasets and figshare reports/logs.

Limitations:

- The source is an OSF archive, not a git repository with commit history.
- The public standalone source partially diverges from the paper's stated MS1/MS2-separated hyperparameter description.
- Figshare figure scripts could not be acquired in this environment because the share URL returned an AWS WAF challenge under `curl`.
- Full reproduction requires large external PRIDE datasets and deposited DIA-NN reports/logs.

The method is therefore reproducible at the core-algorithm/source-inspection level, but full paper figure reproduction is not yet verified.

### Key Gaps To Preserve

- `Not found`: figshare figure-generation scripts were not inspected; searched Nature Code availability and attempted the figshare share URL, which returned an AWS WAF challenge.
- `Partial`: OSF standalone code supports the main algorithm but not the full DIA-NN production integration.
- `Partial`: paper claims MS1/MS2-separated hyperparameters; standalone source exposes seven coefficient slots.
- `MISSING`: exact benchmark orchestration and full statistical scripts are not in the extracted OSF source snapshot.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
