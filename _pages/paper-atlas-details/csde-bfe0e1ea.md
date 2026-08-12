---
layout: default
permalink: /paper-atlas/csde-bfe0e1ea/
title: "CSDE"
nav: false
description: "CSDE 不试图重新画出“正确”的细胞边界，而是问一个更保守的问题：自动分割、定量和注释造成的错误，会把下游差异表达（DE）推偏多少？它用少量专家复核细胞估计这种偏差，再把大规模自动数据提供的低方差与人工数据提供的可信性结合起来。 论文是 2026 年 bioRxiv 预印本，尚未经同行评审。以下解释以本地论文正文、同文件中的补充材料、图注和 CSDEcode 源码为证据边界。"
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
      <span>Spatially Variable Genes</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>CSDE</h1>
    <p>Mitigating Bias in Spatial Transcriptomic Pipelines via Human Feedback</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2026.01.15.699786" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CSDE：用少量人工证据校正空间转录组差异表达

### 一句话理解

CSDE 不试图重新画出“正确”的细胞边界，而是问一个更保守的问题：自动分割、定量和注释造成的错误，会把下游差异表达（DE）推偏多少？它用少量专家复核细胞估计这种偏差，再把大规模自动数据提供的低方差与人工数据提供的可信性结合起来。

论文是 2026 年 bioRxiv 预印本，尚未经同行评审。以下解释以本地论文正文、同文件中的补充材料、图注和 `CSDE_code` 源码为证据边界。

### 1. 为什么常规空间 DE 会失真

成像型空间转录组先经历细胞分割、转录本归属和细胞类型注释，再比较某类细胞在两个空间区域中的表达。若边界吞入邻近细胞的转录本，或非 T 细胞被错标成 T 细胞，样本量再大也只会让一个有偏估计变得“非常显著”。肺癌案例中，人工复核的自动预测 T 细胞只有 47% 同时通过分割和分类确认；自动方法还报告了 `COL1A1`、`FAP`、`LYZ` 等非 T 细胞标记。

因此三种数据路线各有代价：

- 仅自动数据：数量大、方差小，但系统误差不会因样本量增加而消失。
- 仅人工数据：近似无偏，但每张切片约 600 个复核细胞，置信区间宽、检验功效低。
- CSDE：让自动数据贡献精度，再用同一批人工细胞上的“人工结果减自动结果”抵消偏差。

### 2. 三份数据必须怎样配对

对候选细胞原始局部图像记为 $\mathcal T$。自动流程 $\hat f$ 给出计数和标签 $(\hat X,\hat Y)$，专家流程 $f^*$ 给出 $(X,Y)$。CSDE 使用：

- $D_n=\{(X_i,Y_i)\}_{i=1}^n$：少量人工结果；
- $\hat D_n=\{(\hat X_i,\hat Y_i)\}_{i=1}^n$：同一批细胞的自动结果；
- $\hat D_N=\{(\hat X_j^u,\hat Y_j^u)\}_{j=1}^N$：其余大规模自动结果。

关键不是“有一份人工表和一份自动表”即可，而是 $D_n$ 与 $\hat D_n$ 必须逐细胞对应。只有这样，人工与自动的差值才是在相同对象上测得的处理误差。

人工检查面板把分割边界、膜/核信号、预测标签和关键基因表达叠在一起。专家有三种决定：接受；边界可用但标签错误时纠正；边界不可信时拒绝并归入技术性的 Other 类。这里不是重画边界：边界错的细胞被排除为不可信对象。

### 3. DE 参数：Poisson GLM 中的 LFC

对基因 $g$ 和类别 $k$，论文采用

$$
X_{jg}\mid Y_j=k\sim\operatorname{Poisson}(\mu_k^g),
\qquad
\log\mu_k^g=\beta_0^g+\beta_k^g,
$$

参考类别令 $\beta_0$ 之外的相对系数为 0；$\beta_k^g$ 就是类别 $k$ 相对参考类别的对数倍数变化。源码在 `model.py:182-190` 先给参考类拼接全零系数，再用 `exp` 得到 Poisson rate。输入是原始计数，不在 CSDE 内做归一化。

### 4. 核心校正目标为什么能消偏

对每个基因，CSDE 最大化

$$
\mathcal I_g(b^g)=
\lambda_g\mathcal L_{\hat D_N}^g(b^g)
+\mathcal L_{D_n}^g(b^g)
-\lambda_g\mathcal L_{\hat D_n}^g(b^g).
$$

从左到右读：大规模自动似然提供精度；人工似然提供正确方向；同一人工子集上的自动似然被减掉，用来估计并抵消自动流程的偏差。因为 $\hat D_N$ 与 $\hat D_n$ 来自同一自动机制，后二者的期望相同，所以自动项在期望上相消，只留下人工目标。

一个简化数值直觉：自动数据给出的 LFC 约为 1.0，而人工复核的同批细胞显示自动流程平均多推高 0.4；校正后的中心便接近 0.6。真实算法不是直接做这三个 LFC 的算术，而是在似然/梯度层面完成同一逻辑。

代码用负对数似然最小化同一目标：`optimization.py:72-75` 和 `145-150` 实现 `lambda * loss_unl - lambda * loss_hat + loss_gt`。这与论文基本目标是 Exact 对应。

### 5. $\lambda_g$ 控制什么

$\lambda_g=0$ 时退化为仅人工估计；增大 $\lambda_g$ 会更多利用自动数据，但也会把自动误差带入方差。论文不是凭经验固定它，而是最小化目标 LFC 系数的渐近方差。源码先以 $\lambda_0=0.5$ 拟合，计算三份数据的逐样本 score、人工 Hessian 与协方差，再在 `model.py:281-337` 求闭式比值。

论文声明 $\lambda_g\in[0,1]$；当前代码直接返回比值，没有显式裁剪。因此“始终位于区间内”不能从这个代码快照得到保证。

### 6. 稀有细胞为何需要重要性抽样

结肠样本中的 T 细胞很少，均匀抽 600 个细胞可能得不到足够目标细胞。论文提高自动预测为 T 细胞的候选权重，使每张切片约 600 个复核对象中约 200 个是候选 T 细胞。但只挑自动预测 T 细胞会漏掉假阴性并引入选择偏差，因此论文用自归一化逆权重

$$
\eta_i=\frac{1/w_i}{\sum_l1/w_l}
$$

重新加权人工校正项（论文 Eq. 7）。这一步是统计有效性的组成部分，不是可省略的采样技巧。

重要实现边界：本地核心包没有接收 $w_i$ 或 $\eta_i$ 的 API，也没有 Eq. 7 的加权目标。论文级实验脚本位于另一个 `csde_reproducibility` 仓库；当前工作区只能验证未加权的 Eq. 5 实现。

### 7. 从点估计到显著性

PPI 理论给出 $\hat\beta_k^g$ 的渐近正态性。代码在 `model.py:380-403` 用人工 Hessian、自动 score 方差和人工—自动校正残差组装 sandwich covariance；随后 `model.py:480-531` 逐基因计算 Wald z 检验并用 Benjamini–Hochberg 校正。数值条件不良的基因可由 Hessian condition-number 阈值守卫，但该防御性细节不是论文方法的一部分。

### 8. 实验结果应该怎样读

论文在两张肺癌和两张结肠癌 MERSCOPE 切片上比较肿瘤内外 CD8 T 细胞，每张切片人工复核约 600 个候选对象：

- Figure 1 是方法逻辑：自动低方差但有偏，人工无偏但高方差，CSDE 折中两者。
- Figure 2 展示 CVAT 所用静态诊断面板；它证明人工标签如何产生，不是 CSDE 内置交互界面。
- Figure 3 的肺癌实验显示自动基线产生更多非 T 细胞标记，而 CSDE 的 LFC 在重复切片间更一致，并恢复细胞毒、耗竭和组织驻留相关信号。
- Figure 4 的结肠癌实验复现同一趋势，并突出肿瘤内 T 细胞的缺氧相关程序。
- 补充 Figure S1–S3 展示空间分布与接受/拒绝案例，S4 展示 CVAT 界面；补充方法给出渐近证明、$\lambda$ 选择、标准化复核协议和 benchmark 定义。

肿瘤/邻近区域是在自动数据中预先确定的：距最近肿瘤细胞 20 μm 内记为肿瘤区，并对所有方法固定。CSDE 因此校正的是细胞预处理对 DE 的影响，不会同时校正区域定义错误。

### 9. 论文与本地代码的对应边界

| 机制 | 本地证据 | 结论 |
|---|---|---|
| Poisson GLM 与参考类 LFC | `src/csde/model.py:174-200` | Exact |
| 三份配对数据 | `src/csde/api.py:102-106` | Exact |
| Eq. 5 PPI 目标 | `src/csde/optimization.py:72-75,145-150` | Exact |
| $\lambda$、sandwich covariance、Wald/BH | `src/csde/model.py:281-403,480-531` | Exact/实现扩展 |
| Accept/Reject | `src/csde/api.py:82-91` | Partial |
| 把 A 错标直接纠正为 B（反之亦然） | 高层 API 只有 `is_correct` 布尔量 | Not found |
| 重要性抽样逆权重 Eq. 7 | 核心包无权重输入 | Not found；论文实验在外部复现仓库 |
| 面板生成、CVAT 导入导出、原始 MERSCOPE 流程 | 当前快照仅核心统计包 | Not found；外部复现仓库边界 |

尤其要注意 `run_csde()` 的真实语义：只有“自动预测为 A/B 且 `is_correct=True`”的细胞保留为 A/B，其余都变为 Other。它不能表达论文协议中“边界正确，但把预测 A 改成 B”的人工纠正。因此不能把这个简化 API 等同于完整论文工作流。

### 10. 使用前的检查清单

1. 人工与自动子集是否逐细胞严格对齐？
2. 是否保留所有候选细胞的抽样概率，并在非均匀抽样时使用 Eq. 7 权重？
3. 人工协议能否区分接受、改标签和拒绝，而不是只记录一个正确/错误布尔量？
4. 输入是否为模型所需的计数，参考类与目标类方向是否明确？
5. 是否检查 $\lambda$ 超界、Hessian 条件数、稀有类别样本量和重复切片一致性？
6. 是否把 CSDE 的结论限定为“校正下游 DE”，而不是“修复了分割、注释或空间区域”？

CSDE 最有价值的思想不是用人工替代自动化，而是把人工复核变成一个可量化的误差校准样本。其统计目标在本地核心代码中对应清楚；但重要性抽样和完整人工纠正协议仍需论文的外部复现代码，不能由当前包单独复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CSDE Summary

**Paper:** Mitigating Bias in Spatial Transcriptomic Pipelines via Human Feedback
**Method:** CSDE (Corrected Spatial Differential Expression)
**Authors:** Pierre Boyeau, Stephen Bates, Can Ergen, Michael I. Jordan, Nir Yosef
**Journal:** bioRxiv (preprint)
**Year:** 2026
**DOI:** 10.64898/2026.01.15.699786
**Code:** https://github.com/YosefLab/CSDE

---

### Motivation & Novelty

**Biological problem:** Differential expression (DE) analysis between spatially-resolved cell subsets (e.g., intratumoral vs. extratumoral T cells) is a core analysis in spatial transcriptomics. However, all spatial platforms require automated preprocessing pipelines — segmentation and cell-type annotation — that introduce systematic errors. In crowded tumor microenvironments, only ~47% of automatically predicted T cells may actually be correctly segmented and labeled T cells. Running DE on contaminated labels produces spurious signals: genes from stromal (COL1A1, FAP) and myeloid (LYZ, CSF1) cells appear as "T cell" DE genes.

**Why existing methods fall short:**
- *Segmentation-free methods* (Park et al., *Nature Communications*, 2021; Palla et al., *Nature Biotechnology*, 2022): operate on transcript aggregates, losing single-cell resolution
- *Better segmentation* (Cellpose3, Pachitariu & Stringer, *Nature Methods*, 2025; Proseg, Jones et al., bioRxiv 2024): reduce errors but cannot eliminate them, especially in dense 3D tissue
- *Post-hoc correction tools* (ResolVI, Ergen & Yosef, bioRxiv 2025; Baysor, Petukhov et al., *Nature Biotechnology*, 2022): make assumptions about expression regularity that may not hold
- *Standard MLE on manual data only:* low statistical power due to small n

**CSDE's unique contribution:** Instead of correcting or circumventing preprocessing errors, CSDE *accounts for their uncertainty* in downstream DE testing. It applies Prediction-Powered Inference (PPI; Angelopoulos et al., *Science*, 2023; PPI++, Angelopoulos et al., arXiv 2023) to spatial DE: combining a small expert-validated dataset with a large automated dataset to produce bias-corrected, calibrated LFC estimates with formal statistical guarantees. Key innovations:
1. A streamlined CVAT-based annotation workflow allowing ~600 cells/hour per slide
2. Gene-specific λ optimization (minimizes variance of the specific LFC coefficient of interest, rather than the full parameter vector as in standard PPI++)
3. Importance sampling to focus expert effort on rare cell types

---

### Method Overview

**Framework:** CSDE models gene expression using a Poisson GLM with log-linear mean. The parameter of interest is the log-fold change (LFC) $\beta_k^g$ of gene $g$ between cell subsets. The key idea is a corrected objective function:

$$\mathcal{I}_g(b^g) = \lambda_g \mathcal{L}_{\hat{D}_N}(b^g) + \mathcal{L}_{D_n}(b^g) - \lambda_g \mathcal{L}_{\hat{D}_n}(b^g)$$

The first term uses the large automated dataset for statistical power. The correction term (second - third) removes the bias introduced by automated labels. In expectation, the objective equals the manual log-likelihood regardless of preprocessing errors.

**Pipeline:**
1. Automated pipeline produces counts and labels for all $M$ cells (~300K–800K)
2. Importance sampling selects $n \approx 600$ cells (with ~1/3 being T cells) for expert review
3. Expert reviews cells via CVAT: Accept, Correct label, or Reject as invalid
4. CSDE optimizes the corrected objective using Adam or L-BFGS (JAX/Flax implementation)
5. Gene-specific λ selected to minimize asymptotic variance of the specific LFC coefficient
6. Asymptotic normality provides calibrated confidence intervals; Wald test + BH FDR for significance

**Biological assumptions:**
- Cell expression follows Poisson distribution within each subset
- Gene expressions are conditionally independent given cell-type
- Manual annotations are unbiased (expert can correctly identify cells)
- The ratio $n/N$ remains positive as both grow

See `doc_method.md` for full mathematical derivations and `doc_code.md` for implementation details.

---

### Evaluation

**Datasets:** Two cancer types from the Vizgen MERSCOPE FFPE human immuno-oncology dataset (Vizgen, 2022):
- Lung cancer: 2 slides (Lung 1: 351,309 cells; Lung 2: 825,527 cells)
- Colon cancer: 2 slides (Colon 1: 671,075 cells; Colon 2: 806,291 cells)

**Task:** Identify DE genes between intratumoral and peritumoral CD8 T cells

**Benchmarks:**
- *Automated*: MLE on full automated dataset (standard practice)
- *Manual*: MLE on expert-validated dataset only (n ≈ 600 cells/slide)
- *CSDE*: Proposed method

**Metrics:**
1. **DE gene count:** Number of genes with BH-adjusted p < 0.05
2. **Biological plausibility score:** Spearman correlation between estimated |LFC| and T cell expression from a pancancer scRNA-seq reference (Guimarães et al., *Nature Communications*, 2024). Measures whether the discovered DE genes are actually T-cell genes.
3. **Reproducibility score:** Spearman correlation of LFCs between two replicate slides of the same cancer type

**Key results:**

*Lung cancer:*
- Automated: most DE genes, but low plausibility (includes COL1A1, LYZ, VEGFB, CSF1 — non-T cell markers)
- Manual: fewest DE genes (10), high plausibility
- CSDE: 29 DE genes, all from manual benchmark recovered, higher plausibility than automated
- CSDE uniquely identified: BCL2L1 (survival), NFKB2/STAT3 (transcriptional activation), proliferative signal (CCND1↑, CDKN1B↓), tissue-residency (CCR7↓, CXCR4↓)

*Colon cancer:*
- CSDE: ~2x more DE genes than manual, fewer than automated
- Core shared findings: GZMB, PRF1 (cytotoxicity), HIF1A, PKM (hypoxia adaptation), TGFBR1 (TGF-β immune evasion)
- CSDE unique: CTNNB1, CDK4 (Wnt-driven stem-like proliferation), CCR7↓, GZMK↓ (terminal effector shift)
- Automated false positives: HLA-DRA, HLA-DMA (MHC class II, myeloid contamination), COL1A1, SOD2, JUN/JUNB

**Conclusion:** CSDE achieves higher biological plausibility than automated (by avoiding contamination artifacts) while substantially higher statistical power than manual-only. Similar reproducibility across methods.

---

### Reproducibility

**Rating: 3/5 — Requires significant setup beyond the Python package**

**Strengths:**
- Core statistical library (PyPI `csde`) is clean and well-documented (~600 lines of code)
- Clear AnnData interface with usage example in README
- JAX/Flax implementation handles GPU automatically (install `csde[cuda12]`)
- Test suite with functional test

**Weaknesses / practical challenges:**
- The importance-sampling correction (Eq 7 from the paper) is **not implemented** in the PyPI package — only in the separate `csde_reproducibility` experimental scripts
- The "Correct" annotation action (relabeling) is **not supported** in the current API — only Accept/Reject (`is_correct` boolean)
- Full pipeline (Proseg segmentation → CVAT image generation → manual annotation → CSDE analysis) requires the `csde_reproducibility` repository (https://github.com/PierreBoyeau/csde_reproducibility), which has no documentation beyond code comments
- MERSCOPE data is publicly available (Vizgen, 2022) but requires Vizgen-specific preprocessing scripts
- Hessian computation is slow for large manual sets — O(n × params²) per-observation loop
- No tutorial notebook in the main repository; tutorial logic is spread across the reproducibility repo

**Environment:**
- Python ≥ 3.10
- JAX ≥ 0.4.0 (CPU or GPU via `csde[cuda12]`)
- Standard ML stack: Flax, Optax, Scanpy, AnnData

**Common pitfalls:**
- Must set `jax.config.update("jax_enable_x64", True)` — handled automatically at import
- Rare cell types (<1%) need importance sampling; without it, the manual set may contain too few cells of interest
- The `is_correct` column semantics: True means both segmentation and label are correct; False sends the cell to the "Other" class

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
