---
layout: default
permalink: /paper-atlas/rna-velocity-review-bbaf339-858c4c7b/
title: "RNA_velocity_review_bbaf339"
nav: false
description: "这篇综述把 RNA velocity 理解为“从 unspliced/spliced RNA 计数推断细胞转录动态向量场”的问题，并用三类范式组织现有方法：稳态方法简单可解释但假设强，轨迹方法更灵活但优化复杂，状态外推方法能捕捉局部异质动力学但依赖邻域选择。研究者应把 velocity 结果当作模型假设驱动的动态证据，并结合数据质量、模型假设、可视化检查和生物学验证来解释。"
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
      <span>Briefings in Bioinformatics · 2025</span>
    </div>
    <h1>RNA_velocity_review_bbaf339</h1>
    <p>Paradigms, innovations, and biological applications of RNA velocity: a comprehensive review</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1093/bib/bbaf339" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## RNA velocity 综述方法解读

### 这篇论文在解决什么问题？

单细胞 RNA 测序通常只能看到细胞在某一时刻的转录组快照。传统轨迹推断方法可以按照转录相似性把细胞排序成伪时间，但“方向”往往不够直接：一个细胞到底是在向哪个命运移动？某条分化分支是否真的发生？哪些基因或调控过程推动了转变？

RNA velocity 的核心思想是利用 **未剪接 RNA** 和 **已剪接 RNA** 的相对丰度来推断短期转录动态。直观地说，如果某个基因的未剪接 RNA 相对较多，可能表示这个基因正在被诱导；如果未剪接 RNA 不足，则可能表示该基因正在被抑制或降解。论文把 RNA velocity 描述为通过普通微分方程建模转录动态，并从相对 mRNA 丰度推断瞬时变化率 $ds/dt$。

需要注意：这篇文章是综述，不是一个新算法的软件论文；本工作空间也没有作者发布的代码或数据。

### 基本输入、输出和计算目标

#### 输入

一个典型 RNA velocity 分析需要：

- scRNA-seq 原始读段或计数；
- 每个细胞、每个基因的未剪接矩阵 $U$；
- 每个细胞、每个基因的已剪接矩阵 $S$；
- 可选的其他模态，例如 ATAC-seq 染色质可及性、代谢标记、空间位置、蛋白水平或转录因子调控网络；
- 细胞邻接图或低维嵌入，用于平滑、投影和解释。

#### 输出

常见输出包括：

- 每个细胞的高维 velocity 向量；
- 转录、剪接、降解等动力学参数；
- 潜在时间、转录状态、调控模块、不确定性等潜变量；
- 细胞间转移概率；
- UMAP/t-SNE/PCA 等低维空间中的 velocity 可视化；
- 下游解释，例如分化方向、命运概率、驱动基因和调控机制。

### 核心动力学方程

图 1D 展示了 RNA velocity 的经典转录/剪接/降解方程：

$$
\frac{du(t)}{dt} = \alpha - \beta u(t),
$$

$$
\frac{ds(t)}{dt} = \beta u(t) - \gamma s(t),
$$

其中：

| 符号 | 含义 |
|---|---|
| $u(t)$ | 未剪接 pre-mRNA 丰度 |
| $s(t)$ | 已剪接 mature mRNA 丰度 |
| $\alpha$ | 转录速率 |
| $\beta$ | 剪接速率 |
| $\gamma$ | 降解速率 |

不同 RNA velocity 方法的关键差别在于：这些速率是全局常数、基因特异、细胞特异、谱系特异、过程特异，还是由神经网络或贝叶斯模型推断；潜在时间是直接测量、由模型推断，还是完全不显式建模。

**证据缺口：** 论文多处引用 Supplementary Material 1 来说明更详细的速率方程，但本工作空间没有补充材料 Markdown（`SUPP_MD=none`），因此补充材料中的精确推导在本地属于 **Not found / MISSING**。

### 典型计算流程

论文的图 1 可以概括为以下流程：

```text
原始 scRNA-seq 数据
  ↓
区分并定量 unspliced / spliced 转录本
  ↓
得到 U 和 S 两个细胞×基因矩阵
  ↓
过滤、归一化、log 转换、KNN moment 平滑；或直接使用 raw counts
  ↓
选择 RNA velocity 模型进行动力学推断
  ↓
得到 velocity 向量、动力学参数、潜变量或不确定性
  ↓
计算细胞转移概率
  ↓
投影到 UMAP/t-SNE/PCA 并绘制 stream/grid velocity
  ↓
下游分析：伪时间、驱动基因、命运映射、调控解释、不确定性评估
```

这条流程说明 RNA velocity 不是单纯画箭头，而是一个从计数矩阵、动力学模型、优化目标到生物解释的完整推断链条。

### 三类 RNA velocity 方法

论文的主线是把现有方法分为三大类：稳态方法、轨迹方法和状态外推方法。图 2 用相图和优化目标直观展示了这三类范式。

#### 1. 稳态方法（steady-state methods）

稳态方法假设某些细胞或基因接近转录平衡，可以在相图中用未剪接和已剪接 RNA 的关系估计动力学参数。

代表方法包括：

- **Velocyto**：最早的 RNA velocity 框架，基于稳态假设，识别稳态细胞，用最小二乘线性回归估计稳态比率或降解相关参数，再计算 velocity。
- **scVelo deterministic/stochastic**：继承稳态思想，并在 stochastic 模型中加入未剪接/已剪接计数的二阶矩，考虑方差和协方差。
- **MultiVelo 稳态版本**：加入 ATAC-seq 染色质可及性，把上游调控信息纳入转录速率建模。
- **VeloAE**：用 autoencoder 在低维潜空间中学习 RNA velocity，缓解高维稀疏和噪声问题。
- **TopicVelo**：用 Bayesian nonnegative matrix factorization 分解多个生物过程或 topic，再用 chemical master equation 和 Gillespie 模拟建模转录爆发，并最小化预测分布与观测分布之间的 KL divergence。

稳态方法优点是简单、快速、可解释；缺点是依赖较强假设。如果系统中存在多速率动力学、复杂分支、异质亚群、转录爆发或缺少稳态细胞，稳态方法容易失效。

#### 2. 轨迹方法（trajectory methods）

轨迹方法不只拟合一条稳态直线，而是构建未剪接和已剪接 RNA 随时间变化的相图轨迹。模型把观测细胞匹配到轨迹上的某个位置，并优化动力学参数。

代表方法包括：

- **scVelo dynamical model**：使用 ODE 和 expectation maximization。E-step 给细胞分配 latent time 和转录状态；M-step 优化动力学参数，使轨迹更好解释观测细胞位移。
- **MultiVelo dynamical model**：把染色质可及性作为第三个相图维度，用于推断上游调控对转录速率的影响。
- **UniTVelo**：使用 radial basis function 描述平滑的时间函数，并用 gene-shared latent time 统一不同基因的方向性。
- **Dynamo**：利用 metabolic labeling 直接获得真实时间信息，因此能在绝对时间尺度上估计 velocity 和参数。
- **veloVI / VeloVAE / LatentVelo**：使用 VAE、神经 ODE 或潜空间动力学来重构未剪接和已剪接矩阵，支持更复杂的非线性或谱系特异动力学。
- **Pyro-Velocity / cell2fate**：使用贝叶斯或随机变分推断，直接处理 raw counts，并提供参数、latent time 或 velocity 的不确定性。

轨迹方法比稳态方法更灵活，能输出 latent time、状态和不确定性等有解释价值的变量。但它们也更依赖优化过程和 ODE 形式；当轨迹观测不完整、分支复杂或动力学不是简单 stepwise induction/repression 时，仍可能出错。

#### 3. 状态外推方法（state extrapolation methods）

状态外推方法的核心问题是：如果从当前细胞根据局部动力学向未来走一步，外推状态是否接近真实观测到的邻近细胞？它们通常不拟合全局轨迹，而是用局部邻域监督 cell-specific velocity。

代表方法包括：

- **cellDancer**：每个基因训练独立神经网络，估计 cell-specific kinetic rates；通过最大化外推状态与邻居的 cosine similarity 来学习 velocity。
- **DeepVelo**：构建 KNN 图，用 graph convolutional network 编码局部邻域，再用解码器预测基因和细胞特异参数；目标是最小化预测状态与期望邻居之间的位移。
- **SymVelo**：双分支框架，高维分支用 neural ODE，低维分支借鉴 VeloAE；两个分支分别计算 Markov transition matrix，并通过最小化两者差异进行 mutual learning。

状态外推方法适合捕捉局部、细胞特异、多速率动力学，尤其适合高度异质的系统。但它们依赖邻居选择质量，计算开销较高，生物应用验证也比 scVelo 等经典流程少。

### 与 GRN 和多组学的关系

这篇综述不是专门的 GRN 推断论文，但它指出了 RNA velocity 与调控网络、多组学整合的连接：

- MultiVelo 用 ATAC-seq 可及性解释转录速率变化；
- Dynamo 用 metabolic labeling 估计绝对时间尺度动力学；
- Protaccel 把速度思想扩展到蛋白水平；
- SIRV 结合空间转录组；
- TFvelo 用 TF-target 关系推断基因特异动态；
- scKINETICS 用调控网络驱动的微分方程建模 phenotype transitions；
- cell2fate 用调控模块分解时间依赖的转录动态。

因此，RNA velocity 的未来方向不只是“细胞往哪里走”，还包括“是什么调控机制推动细胞往那里走”。

### 生物应用总结

论文把应用分成三类。

#### 分化和发育

RNA velocity 被用于小鼠胚胎、人类前脑、斑马鱼神经系统、人类视网膜、胸腺上皮、骨髓基质细胞、NK 细胞发育、肠道、子宫内膜、胎肺、精子发生、视觉皮层和植物再生等场景。主要用途是重建谱系方向、发现过渡状态、识别驱动基因和验证分化路径。

#### 疾病和损伤微环境

在炎症、系统性红斑狼疮、子痫前期、肺修复、阿尔茨海默病、心肌梗死、糖尿病足溃疡、病毒感染和伤口愈合中，RNA velocity 用于分析异常转变、修复过程、发育停滞和病理重塑。

#### 肿瘤微环境

在肿瘤中，RNA velocity 用于研究 T 细胞分化和耗竭、非小细胞肺癌、前列腺癌可塑性、结直肠息肉、慢性淋巴细胞白血病、胰腺癌免疫效应、CNS 淋巴瘤、胶质瘤干细胞和骨转移生态系统。论文也提醒，肿瘤样本常缺少祖先细胞，而且突变可能导致异常剪接，因此需要结合染色体异常、标志基因和其他证据谨慎解释。

### 实践建议

论文给出的核心建议可以总结为：

1. **先看生物系统复杂度。** 简单、方向明确的分化系统可以从 Velocyto 或 scVelo 开始；复杂分支、肿瘤和高异质系统可能需要高级轨迹模型或状态外推模型。
2. **重视数据质量。** UMI 数、稀疏度、unspliced/spliced 分离质量都会影响结果。
3. **谨慎处理预处理。** 归一化和 KNN 平滑可以降噪，但也可能扭曲真实的随机性和 velocity。
4. **不要只看二维流线图。** 低维可视化可能产生拓扑伪影，应结合 latent time、driver genes、uncertainty、marker genes、已知细胞命运和不同嵌入方法。
5. **需要标准化 benchmark。** 目前缺少跨数据集、跨生物场景、公平比较多种 RNA velocity 方法的统一基准。

### 可复现性和本地缺口

- 论文的 Data availability：Not applicable。
- 论文的 Code availability：Not applicable。
- 本地没有代码仓库，`doc_code.md` 已跳过。
- 本地没有 Supplementary Material 1，因此详细速率方程不可验证。
- 这篇综述适合复现其概念框架、方法分类和文献路线图；不适合作为可运行软件分析复现。

### 一句话总结

这篇综述把 RNA velocity 理解为“从 unspliced/spliced RNA 计数推断细胞转录动态向量场”的问题，并用三类范式组织现有方法：稳态方法简单可解释但假设强，轨迹方法更灵活但优化复杂，状态外推方法能捕捉局部异质动力学但依赖邻域选择。研究者应把 velocity 结果当作模型假设驱动的动态证据，并结合数据质量、模型假设、可视化检查和生物学验证来解释。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Paper

**Paradigms, innovations, and biological applications of RNA velocity: a comprehensive review** — Wang et al., *Briefings in Bioinformatics* 26(4), 2025. DOI: `10.1093/bib/bbaf339`.

### Problem

Single-cell RNA-seq captures static snapshots of cells, while many biological questions require direction: which state is a cell moving toward, which lineage branch is likely, and which genes or regulatory processes drive that transition? RNA velocity addresses this by comparing unspliced and spliced mRNA abundance to infer short-term transcriptional change and future cellular states.

### What this review contributes

This is a synthesis/review paper, not a new software release. It organizes RNA velocity methods into three computational paradigms:

1. **Steady-state methods** — e.g. Velocyto, scVelo deterministic/stochastic variants, MultiVelo steady-state variants, VeloAE, TopicVelo. These use steady-state assumptions, least-squares ratios, latent-space denoising, or distributional objectives such as KL divergence.
2. **Trajectory methods** — e.g. scVelo dynamical, MultiVelo dynamical, UniTVelo, Dynamo, veloVI, VeloVAE, LatentVelo, Pyro-Velocity, cell2fate. These fit ODE-based or neural/Bayesian trajectories over latent or measured time.
3. **State extrapolation methods** — e.g. cellDancer, DeepVelo, SymVelo. These learn local, cell-specific velocities by predicting future states and matching them to neighboring observed cells.

The review also summarizes applications across differentiation and development, diseased or injured microenvironments, and tumor microenvironments, then discusses preprocessing pitfalls, complex transcriptional dynamics, visualization artifacts, and best-practice method selection.

### High-level computational workflow

The reviewed RNA velocity workflow is:

```text
raw scRNA-seq data
  → unspliced/spliced transcript quantification
  → count filtering, normalization, optional k-NN moment smoothing or raw-count modeling
  → kinetic inference with steady-state, trajectory, or state-extrapolation model
  → per-cell velocity vectors, kinetic rates, latent variables, uncertainty when available
  → transition probabilities and low-dimensional projection
  → downstream interpretation: pseudotime, driver genes, fate mapping, regulatory hypotheses
```

Fig. 1 directly depicts this pipeline, including spliced/unspliced matrices, preprocessing, the ODE system for transcription/splicing/degradation, velocity projection, and downstream analyses. Fig. 2 directly depicts the three method paradigms as steady-state regression/distribution matching, latent-time trajectory fitting, and future-state extrapolation.

### Key equations and model ideas

The paper frames RNA velocity with ordinary differential equations and names velocity as an instantaneous change rate $ds/dt$. Fig. 1 shows the canonical system:

$$
\frac{du(t)}{dt} = \alpha - \beta u(t),
$$

$$
\frac{ds(t)}{dt} = \beta u(t) - \gamma s(t),
$$

where $u(t)$ is unspliced RNA, $s(t)$ is spliced RNA, and $\alpha$, $\beta$, and $\gamma$ correspond to transcription, splicing, and degradation. Different methods vary in whether these rates are constant, gene-specific, cell-specific, lineage-specific, process-specific, inferred with EM, estimated by regression, learned by neural networks, or treated probabilistically.

### Evaluation and applications covered

Because this is a review, it does not introduce a new benchmark experiment. Instead, it compiles representative applications in Table 3. The main application areas are:

- **Differentiation and development:** embryonic development, forebrain oligodendrocyte precursor specification, zebrafish neural and enteric systems, retina, thymic epithelial cells, bone marrow stromal cells, NK development, intestine, endometrium, fetal lung, spermatogenesis, visual cortex, and plant shoot regeneration.
- **Diseased and injured microenvironments:** inflammation, systemic lupus erythematosus, preeclampsia, lung repair, Alzheimer’s disease, myocardial infarction, diabetic foot ulcers, viral infection, and wound healing.
- **Tumor microenvironments:** T cell differentiation/exhaustion, non-small cell lung cancer, prostate cancer plasticity, colorectal polyps, chronic lymphocytic leukemia, pancreatic ductal adenocarcinoma immune effects, CNS lymphoma, glioma stem cells, and bone metastasis ecosystems.

The review argues that scVelo remains widely used because of availability and versatility, while newer methods address known limitations in complex, heterogeneous, multi-omic, or stochastic settings.

### Strengths

- Clear taxonomy of RNA velocity methods by computational paradigm.
- Useful comparison of assumptions, kinetic parameters, latent time, raw-count use, multi-omic support, and estimation frameworks in Tables 1-2.
- Broad application survey across normal development, disease, injury, and cancer.
- Strong practical cautions about preprocessing, KNN smoothing, low-dimensional streamlines, incomplete dynamics, and model-assumption mismatch.
- Highlights extensions beyond classical splicing kinetics, including protein, spatial, metabolic-labeling, TF-target, and regulatory-network approaches.

### Limitations and caveats

- The paper is a review and provides no new runnable method, benchmark dataset, or implementation.
- Supplementary Material 1 is referenced for detailed rate equations, but no supplementary markdown is available in this workspace; those equations remain **Not found** locally.
- Reported method comparisons are conceptual and literature-based rather than a standardized head-to-head benchmark.
- Figure schematics support the workflow and taxonomy but do not provide numerical performance evidence.
- The review itself emphasizes that RNA velocity results can be distorted by preprocessing, KNN graph construction, incomplete trajectories, and 2D visualization artifacts.

### Reproducibility notes

- **Mode:** paper-only.
- **Code availability:** the paper states “Not applicable.”
- **Data availability:** the paper states “Not applicable.”
- **Local code repository:** none found; acquisition manifest and GitHub link extraction report no repository URLs.
- **doc_code.md:** skipped by design because `HAS_CODE=false`.
- **Reproducibility rating:** **1/5** for runnable reproduction of this paper as an analysis artifact, because it is a review with no released code/data; **4/5** for conceptual reproducibility of the taxonomy and workflow from the paper text and figures.

### Recommended use by researchers

Use this review as a decision map. Start by checking whether the biological system likely satisfies steady-state or simple trajectory assumptions. If not, consider models that support lineage-specific rates, raw counts, uncertainty, multi-omics, metabolic labeling, or local state extrapolation. Treat velocity streamlines as hypotheses, not conclusions: validate them with marker genes, known fates, latent variables, driver genes, uncertainty estimates, alternative embeddings, and, where possible, orthogonal experiments.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
