---
layout: default
permalink: /paper-atlas/zman-seq-90ea14c4/
title: "Zman-seq"
nav: false
description: "普通单细胞转录组只拍到细胞状态的静态快照。伪时间或 RNA velocity 可以从表达数据推测先后关系，却无法直接回答“这个免疫细胞进入肿瘤多久了”。Zman-seq 的关键创新是把时间信息在测序前写进细胞：用连续的荧光抗 CD45 抗体脉冲标记血液中的白细胞，随后用单细胞 FACS index sorting 同时记录每个细胞的荧光印记和孔位，再把孔位与 MARS-seq 表达谱连接起来。"
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
      <span>Cell · 2024</span>
    </div>
    <h1>Zman-seq</h1>
    <p>Time-resolved single-cell transcriptomics defines immune trajectories in glioblastoma</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2023.11.032" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Zman-seq 方法解释：先在体内给细胞盖时间戳，再读取它如何被肿瘤改写

### 方法真正解决的问题

普通单细胞转录组只拍到细胞状态的静态快照。伪时间或 RNA velocity 可以从表达数据推测先后关系，却无法直接回答“这个免疫细胞进入肿瘤多久了”。Zman-seq 的关键创新是把时间信息在测序前写进细胞：用连续的荧光抗 CD45 抗体脉冲标记血液中的白细胞，随后用单细胞 FACS index sorting 同时记录每个细胞的荧光印记和孔位，再把孔位与 MARS-seq 表达谱连接起来。

因此它不是单纯的轨迹算法，而是一个“体内脉冲追踪 + 流式时间判定 + 单细胞转录组 + 时间约束轨迹”的组合技术。其核心输出有两层：单细胞的离散肿瘤暴露时间箱，以及 metacell 层面的连续肿瘤暴露时间 cTET（continuous tumor exposure time）。

### 1. 血液—组织屏障如何变成时钟

实验在取材前每隔 12 小时注射一种不同荧光偶联的抗 CD45 抗体。抗体能迅速标记仍在血管内的 CD45 阳性白细胞；细胞一旦进入组织或肿瘤，便不再暴露于之后的血中抗体脉冲。于是细胞保留的荧光组合记录了它最后一次仍在循环系统中的时间。

举例说，若取材前 48、36、24、12 小时依次注射四种标签，一个细胞带有 48 h 和 36 h 标签，却没有 24 h、12 h 标签，说明它在 36 h 注射时仍在血中、在 24 h 注射前已经进入肿瘤，故被分到 36 h 暴露时间箱。这里的“36 h”是离散区间标签，不是精确到某一时刻的连续测量。

论文对这一物理前提做了多重验证（图 1、图 S1）：外周血白细胞染色率约 99.8%；游离抗体在 60 分钟内降到检测下限；15 分钟标记主要位于血管内，而 24 小时后标记细胞主要转移到血管外；脑内常驻、卵黄囊来源的小胶质细胞基本不带标签；转移的已标记白细胞在 96 小时及更久仍可检测。这些结果共同支持“短脉冲、长期保留、只标循环细胞”的解释。

这个设计也决定了适用边界：必须存在能把标记区室与目标组织分开的物理屏障，目标细胞必须在循环中表达可标记表面分子，标签需要足够稳定且不能明显改变细胞行为。长期组织驻留细胞没有血液暴露，所以无标签并不等于“刚进入组织”。

### 2. 从 FACS 强度到离散时间箱

不同细胞的大小、形状和背景荧光不同，不能对每个通道使用一个未经校正的固定强度阈值。论文对未染色细胞拟合含二阶交互项的高斯广义线性模型，再判断观测荧光是否显著偏离预期背景。

本地 `ZmanR/R/time_assignment.R` 中的 `FACS_model()` 对每个荧光通道拟合

$$
Y_c \sim (\mathrm{FSC.A}+\mathrm{FSC.W}+\mathrm{FSC.H}
+\mathrm{SSC.A}+\mathrm{SSC.W}+\mathrm{SSC.H}+\log\mathrm{APC.A})^2,
$$

其中 $Y_c$ 是通道 $c$ 的荧光值。模型只用 `Stain == "nonstained"` 的细胞拟合；再对“预测值减观测值”的残差拟合正态分布，以

$$
b_c=\mu_c-s_c\sigma_c
$$

为边界。默认 $s_c=3$，约对应单侧三倍标准差，但并不严格等同于论文文字中的 $p<0.001$。代码的预测变量是 `log_APC.A`，论文方法文字写的是 DAPI；这是明确的论文—代码差异，不能把两者说成完全一致。

`FACS_model()` 再按通道顺序覆盖 `group`，把多重阳性细胞分配给它最后暴露的时间箱。调用者必须保证 `fluorophores` 与 `timebins` 顺序一一对应，否则生物学时间会被系统性错标。图 S2A 正是这一“先逐通道判阳性、再按荧光组合定时间箱”的示意。

### 3. 为什么先聚合成 metacell

离散时间戳并非每个细胞都有同样稳定的信号，单细胞表达也高度稀疏。论文先用 MetaCell 在 KNN 图上聚合表达相似的细胞：去除特定线粒体、免疫球蛋白、核糖体和低可信基因，丢弃少于 300 UMI 的细胞，以 $T_{vm}>0.1$ 且总 UMI 大于 100 选择高离散基因，然后采用 $K=100$、750 次 bootstrap、每次重采样 75% 的细胞构造 metacell。每个 metacell 最后根据标记基因人工注释。

主 GBM 数据包含 10,583 个高质量白细胞、139 个 metacell，每个约 55–170 个细胞；NK/淋巴细胞细分分析使用 2,431 个细胞、37 个 metacell；aTREM2 实验的髓系图包含 7,421 个细胞、94 个 metacell。MetaCell 构造本身来自外部包，不在 `ZmanR` 中实现，因此本地代码不能独立从原始计数重现论文全部聚类。

### 4. 离散时间箱如何变成连续 cTET

对一个 metacell，先统计其中细胞落入各时间箱的比例 $p_i$，再形成累积分布

$$
F(t_i)=P(T\le t_i)=\sum_{j\le i}p_j.
$$

若 metacell 主要由早期细胞构成，CDF 会很早升高，曲线下面积 AUC 较大；若主要由晚期细胞构成，CDF 到后段才升高，AUC 较小。论文因此定义

$$
\mathrm{cTET}=1-\frac{\mathrm{AUC}-\min(\mathrm{AUC})}
{\max(\mathrm{AUC})-\min(\mathrm{AUC})},
$$

使 cTET 接近 0 表示刚进入肿瘤，接近 1 表示驻留较久。

一个简单例子：时间箱为 12、24、36 h。metacell A 的比例是 $(0.8,0.15,0.05)$，CDF 很快达到 0.8；metacell B 是 $(0.05,0.15,0.8)$，CDF 早段只有 0.05。A 的原始 AUC 更大，但经过 $1-$ 归一化后 cTET 更小，因此 A 被放在轨迹早端、B 在晚端。

`compute_mc_cdf()` 还有论文正文容易忽略的稳定化步骤：先给小鼠×metacell 计数加 0.01 伪计数，按不同时间箱的总体采样量校正，再在 MetaCell 图上做三轮邻域平滑；每轮使用 0.6 自身、0.3 一阶邻居、0.1 二阶邻居。随后代码以 `sum(CDF * (T_max - t))` 计算离散 AUC，并存成 `norm_auc`。要特别注意：这个中间量仍是“越早越大”；最终轨迹通过倒序排列和归一化才实现“0 早、1 晚”。图 3B/图 S3B–C 展示各 metacell 的 CDF，图 3C 把 cTET 映射回 NK metacell 图。

### 5. 时间约束轨迹如何构造

Zman-seq 不直接把 cTET 排序当成最终轨迹，而是结合人工细胞类型注释与表达聚类：

1. 以注释的细胞类型为 `ref_k` 个簇，按每簇平均 cTET 排序，得到参考路径 $T_r$。
2. 对高离散、GO 相关的 metacell 表达做层次聚类，令簇数从 `ref_k+1` 一直增加到 metacell 数；每种聚类都按簇平均 cTET产生一条候选路径 $T_k$。
3. 只保留与参考路径 Spearman 相关系数大于 0.75 的候选路径。
4. 将参考路径和所有保留路径的平均结果等权平均，得到 `smoothed_auc`，即最终时间轨迹坐标。

代码核心可写成

$$
T_c=\frac{1}{2}\left[T_r+operatorname{normalize}
\left(\operatorname{mean}_{k:\rho(T_k,T_r)>0.75}T_k\right)\right].
$$

这不是完全无监督的轨迹推断：参考路径依赖人工细胞类型注释，候选路径又以与参考路径的一致性过滤。它更准确的定位是“用实测时间约束并平滑已注释的状态转换”。若参考注释错误、分支结构复杂或某一时间段采样不足，最终路径也会继承这些限制。

### 6. 沿时间寻找基因、TF 和外源信号

`calculate_corr_genes()` 对每个基因计算表达与 `smoothed_auc` 的 Spearman 相关；`predict_expression_along_time()` 再用一次 loess（默认 degree 1、span 0.9）把基因表达投到均匀时间网格，用于热图。图 3E 因而能区分不同变化速度：NK 细胞的归巢受体 *S1pr5*、*Cx3cr1* 很早下降，细胞毒分子 *Gzmb*、*Gzma*、*Prf1* 较慢下降，而 *Itga1*、*Xcl1*、*Gzmc* 等 TGF-β 相关状态逐渐上升。

论文随后用 DoRothEA A/B 置信度靶基因估计 TF 活性，并用 NicheNet 按“能否解释时间相关靶基因”优先排序配体。它据此提出 TGF-β1/SMAD3 是 NK 功能障碍的重要驱动，并在髓系轨迹中看到单核细胞经 *Arg1* TAM 到 *Gpnmb* TAM 的变化，以及 NF-κB 活性下降、STAT3/HIF1A/NFE2L2 上升。aTREM2 处理则把共同的早期单核细胞状态重定向到 *Acp5*/*Cd72* 炎症型 TAM 分支，并增强 CCL3/4/5 等趋化因子回路（图 4–5）。

这些 TF、配体和差异表达分析不是 `ZmanR` 的内部实现。DoRothEA、NicheNet、DESeq2、scVelo 和多种伪时间基准均由外部流程完成；本地包只提供时间箱、cTET、轨迹平滑、相关基因和可视化的主要构件。

### 7. 怎样读论文的图

- 图 1 与图 S1：验证时钟是否真的只标循环细胞，以及脉冲和标签能维持多久。
- 图 2 与图 S2：先不做连续轨迹，只看 12/24/36 h 离散箱是否随免疫状态产生合理富集。
- 图 3 与图 S3：完整展示 CDF→cTET→NK 轨迹→时间相关基因→TF/配体解释。
- 图 4 与图 S4–S5：把相同框架用于单核细胞到免疫抑制 TAM 的 36–48 h 转变。
- 图 5 与图 S7：比较对照和 aTREM2，说明干预不是简单改变终点丰度，而是重定向分化路径。
- 图 S6：以实测 AUC 为参照比较 scVelo、DPT、Palantir、Monocle2、redPATH、SCORPIUS；结果同时显示推断方法对基因选择高度敏感，而不是证明 cTET 本身没有误差。

补充图 S1–S7 的图注已包含在本地 `paper.md` 中；独立的补充表/原始分析脚本没有作为本工作区证据文件完整保存。

### 8. 论文—代码对应与版本边界

| 机制 | 本地实现 | 判断 |
|---|---|---|
| 二阶高斯 GLM 与逐通道时间箱判定 | `ZmanR/R/time_assignment.R:133-176` | **Partial**：总体结构一致；代码用 3σ 默认阈值和 `log_APC.A`，论文写 $p<0.001$ 与 DAPI |
| CDF、离散 AUC 与时间箱校正 | `ZmanR/R/zman_trajectory_analysis.R:129-249` | **Exact / extended**：核心公式存在，并额外实现伪计数和三轮图平滑 |
| cTET 方向反转和参考路径 | `zman_trajectory_analysis.R:53-60,326-351` | **Exact**：高原始 AUC对应早期，最终轨迹为 0 早、1 晚 |
| metacell 表达归一化 | `zman_trajectory_analysis.R:275-299` | **Exact**：局部快照实现了 metacell 表达聚合与 `log2(1+x*5000)` |
| 时间约束轨迹平滑 | `zman_trajectory_analysis.R:326-351` | **Exact / extended**：等权合并参考路径和相关性大于 0.75 的候选路径 |
| 时间相关基因与 loess | `zman_trajectory_analysis.R:379-450` | **Exact**：Spearman 检验和 loess 预测均可定位 |
| MetaCell 构造、DoRothEA、NicheNet、DESeq2 和基准 | 外部依赖/论文分析流程 | **Not found**：不在本地 ZmanR 源码中 |

本地 `DESCRIPTION` 标记 ZmanR 版本为 1.0.0，上游地址记录为 `https://github.com/kenxie7/ZmanR`。但 `ZmanR/` 内没有独立 `.git` 或 `.repo_source`，因此**上游提交哈希 Not recorded**；运行 `git -C ZmanR rev-parse HEAD` 得到的是 PaperCode 外层仓库提交，不能当作 ZmanR 来源版本。当前快照也没有端到端论文作图脚本、锁定环境、容器或自动测试，所以可核对函数机制，但不能仅靠该目录复现所有主图。

工作区 CodeGraph 已尝试用于核心函数定位，但索引没有返回相关符号；以上实现判断均回退到直接阅读 R 源码，并以论文 STAR Methods、主图及补充图注作为最终证据。

### 9. 最容易误读的边界

1. cTET 是 metacell 层面的相对连续分数，不是每个细胞的精确入瘤时刻；其 0–1 缩放依赖当前分析集合的最小和最大 AUC。
2. 无荧光标签可能表示长期驻留、技术漏检或不满足标记前提，不能自动解释为一个正常时间箱。
3. 时间箱宽度为 12 小时，尽管抗体脉冲本身约有 30 分钟分辨率；生物时间分辨率仍受注射间隔、迁移与采样影响。
4. 图邻域平滑会提高稳定性，也会把邻近 metacell 的时间组成混合；小群体或真实快速转变可能被平滑。
5. 轨迹由人工注释提供参考，不天然识别任意分叉、汇聚或循环；aTREM2 的“分叉”来自条件比较和图结构共同解释。
6. 配体—靶基因和 TF 活性是数据库驱动的计算优先级，不等同于因果证明。论文用部分体外实验增强 TGF-β/TREM2 解释，但并未逐一验证全部候选边。

### 推荐阅读顺序

先看图 1/S1，确认时间标签的实验逻辑；再看图 S2A 和 `FACS_model()`，理解荧光组合怎样变成离散箱；接着看图 3B–D 与 `compute_mc_cdf()`、`smooth_zman_trajectory()`，抓住 AUC 方向和参考路径；最后读图 3E–G、图 4–5，把“观察到随时间变化”与“推测其调控驱动”分开。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Zman-seq summary.md

### Motivation & Novelty

#### Biological Problem

Immune cells circulating in the bloodstream continuously infiltrate solid tumors, where they encounter an immunosuppressive microenvironment and transition from functional effector states to dysfunctional, tumor-tolerant states. The molecular circuits, timescales, and causal sequence of these transitions are largely unknown because all existing scRNA-seq methods produce static snapshots: they reveal which cell states exist in a tumor but cannot determine when a cell acquired that state, how fast the transition occurred, or which upstream signals drove it.

#### Limitations of Existing Approaches

- **RNA velocity** (La Manno et al., *Nature* 2018; Bergen et al., *Nat. Biotechnol.* 2020): Infers temporal direction from the ratio of unspliced to spliced mRNA. Requires many genes with good splicing models, is sensitive to gene selection, and performs poorly when multiple trajectories coexist — as in the immunosuppressive TME.
- **Pseudotime algorithms** — Monocle2 (Trapnell et al., *Nat. Biotechnol.* 2014), DPT (Haghverdi et al., *Nat. Methods* 2016), Palantir (Setty et al., *Nat. Biotechnol.* 2019), SCORPIUS (Cannoodt et al., *bioRxiv* 2016), redPATH (Xie et al., *Genomics Proteomics Bioinformatics* 2021): Order cells along a manifold by gene expression similarity. Highly parameter-dependent; no empirical ground truth; fail to distinguish concurrent trajectories (e.g., monocyte-to-TAM vs. monocyte-to-DC).
- **Metabolic RNA labeling** (SLAM-seq, scSLAM-seq): Measures newly synthesized RNA over hours. Requires chemical reagents not applicable in vivo; limited to rapid processes (<12h) and cell culture settings.
- **Multi-timepoint static profiling**: Samples tumors at different days post-implantation, but cannot distinguish recently infiltrated cells from cells that have been in the tumor since the beginning.

#### Unique Contribution

Zman-seq (Hebrew "זְמַן" for "time") introduces **empirical temporal information directly into scRNA-seq data** by exploiting the blood-tissue barrier as a physical separator:
1. Sequential intravenous injections of fluorophore-conjugated anti-CD45 antibodies at 12h intervals label circulating leukocytes with time-stamps.
2. Once a cell crosses into the tumor, it is shielded from subsequent injections and retains only the stamps acquired while in circulation.
3. FACS index sorting captures the fluorescent profile of each sorted cell, enabling a **continuous tumor exposure time (cTET)** to be computed for every single cell via a GLM classification + CDF-AUC method.

This produces a hybrid of scRNA-seq and live-cell tracking: a transcriptome-wide, single-cell measurement with empirically determined residence time. The result is a ground-truth temporal axis for trajectory analysis — not inferred, but measured.

---

### Method Overview

#### Algorithmic Framework

Zman-seq combines a **wet-lab pulse-chase labeling protocol** with a **statistical computational pipeline** (ZmanR R package):

1. **GLM time-bin classification** (`FACS_model()`): A second-order Gaussian GLM trained on unstained cells predicts each cell's expected fluorescence from its physical properties (FSC/SSC/CD45-APC). Cells with fluorescence residuals below μ − 3σ are classified as carrying that stamp.

2. **MetaCell aggregation** (external MetaCell package): 10,000+ cells are partitioned into stable metacells of ~55–170 cells using K-NN graph bootstrapping. This converts noisy single-cell timestamps into robust CDF-based estimates.

3. **cTET computation** (`compute_mc_cdf()`): For each metacell, the cumulative distribution of time-bin frequencies is computed. The AUC of this CDF, normalized to [0,1], defines the continuous tumor exposure time (cTET), with 0 = recently arrived and 1 = long-term resident.

4. **Trajectory refinement** (`smooth_zman_trajectory()`): A reference path from cell-type label ordering is combined with gene-expression-based cluster orderings (filtered by Spearman r > 0.75) to produce a refined combined trajectory.

5. **Downstream analysis**: Spearman correlation + loess smoothing identifies time-correlated genes; Dorothea (A+B confidence) for TF activity; NicheNet for upstream ligand prioritization; DESeq2 pseudo-bulk for treatment effects.

#### Biological Assumptions

- The blood-brain barrier (or equivalent tissue barrier) effectively blocks the passage of antibody between injections
- Microglia (tissue-resident, yolk-sac origin) are not labeled — validated experimentally
- Labeled cells retain their fluorescent stamps for the duration of the experiment (validated: signal detectable ≥96h)
- The most-recent stamp each cell carries reflects when it entered the tissue

#### Key Technical Components

- **ZmanR R package**: GLM classification, cTET, trajectory refinement, Spearman/loess analysis, visualization
- **MARS-seq**: Plate-based scRNA-seq (384-well) with UMI deduplication, HISAT alignment to mm10
- **MetaCell**: External R package for noise-robust transcriptome aggregation
- **DoRothEA + NicheNet**: External tools for TF activity and ligand-receptor inference

---

### Evaluation

#### Datasets

| Dataset | Cells | MCs | Condition |
|---------|-------|-----|-----------|
| GBM myeloid + lymphoid (main) | 10,583 | 139 | GL261 syngeneic, 12/24/36h stamps |
| GBM aTREM2 experiment | ~15,000 | 94 myeloid + 107 lymphoid | 3 aTREM2 + 3 control mice, 12/24/36/48h |
| Colon + lung + blood (validation) | 8,976 | 91 | Steady-state, 12/24/36/48h stamps |

#### Biological Validation Results

**NK cell trajectory** (Figure 3):
- Chemotactic NK cells (S1pr5+, Cx3cr1+) dominate 12h; dysfunctional NK cells (Itga1+, Xcl1+, Gzmc+) dominate 36h
- TGF-β1 identified as the primary upstream driver (Figure 3F-G), explaining the transition from Itga1-low/cytotoxic to Itga1-high/dysfunctional
- SMAD3 activity spikes at the terminal dysfunctional state; SMAD4 (counterbalancing) drops simultaneously
- **Human validation**: TGF-β blockade (anti-TGF-β 1D11) rescued human NK cell degranulation (CD107a), TNF-α and IFN-γ production in co-culture with human glioma stem cells (Figure S3H)

**Myeloid trajectory** (Figure 4):
- Infiltrating monocytes (Chil3+, Plac8+, Ear2+) at 12h → monocyte-derived macrophages → Arg1+ TAMs → Gpnmb+ regulatory TAMs at 36-48h
- TGF-β1 and ANXA1 are primary upstream ligands (Figure 4F-G)
- TF circuit: NF-κB/RELA (early, anti-inflammatory) → STAT2/IRF9 (antiviral, lost) → STAT3 → HIF1A/CREB1 → NFE2L2 (terminal immunosuppressive)
- **Human translation**: Murine early-trajectory genes align with human monocyte/inflammatory TAM states; late-trajectory genes align with human regulatory lipid TAMs (Figure S5E)

**aTREM2 therapeutic intervention** (Figure 5):
- TREM2 blockade produces a bifurcation of the monocyte-to-TAM trajectory: control → Arg1+ TAMs; aTREM2 → Acp5+/Cd72+ pro-inflammatory TAMs
- A small set of ligands (CCL3, CCL4, CCL5, CCL7, CCL8, CXCL9, C3) explains the majority of downstream effects (p = 3.9×10⁻¹⁰²)
- CCL5 and CCL7 expression are associated with improved GBM patient survival (p = 0.016 and p = 0.029, TCGA GEPIA)

**Computational benchmarking** (Figure S6):
- scVelo showed reversed differentiation directions with default HVG selection
- DPT, Palantir, Monocle2, redPATH, SCORPIUS all showed moderate Spearman correlation with cTET when using GO-selected or Zman-seq-derived genes; performance varied substantially with gene selection
- Zman-seq-derived genes improved correlation for all algorithms, confirming that empirical time labels improve gene selection for pseudotime

#### Applicability Beyond GBM

- Colon and lung leukocytes show robust stamp signals and organ-specific cell-state adaptation
- Tissue-resident cells (alveolar macrophages, intestinal ILC, IgA plasma cells) correctly show zero labeling
- Applicable to any tissue with a physical blood-tissue barrier (including BBB, gut epithelium, lung alveolus)

---

### Reproducibility Rating: 3/5

#### Justification

**What is available**:
- ZmanR R package (GitHub: https://github.com/kenxie7/ZmanR) with documented functions for the full computational pipeline
- Raw scRNA-seq data deposited at GEO (GSE232040), publicly available
- Example datasets (GBM T cell example, FACS example data) provided with the package
- Human GBM data from Pombo-Antunes et al. (GEO: GSE163120) used for cross-species validation

**What limits reproducibility**:
1. **No formal analysis scripts**: ZmanR provides the computational building blocks but no end-to-end analysis script that reproduces the figures. The NicheNet, DoRothEA, DESeq2, and scVelo benchmarking analyses exist only as described in STAR Methods — no code deposited at GitHub or GEO (as of analysis date).
2. **External dependencies not fixed**: MetaCell version, DoRothEA database version, and NicheNet prior network version can significantly affect results. No containerized environment provided.
3. **Manual annotation step**: Cell-type labels for metacells were manually assigned by expert biologists. Reproducibility depends on subjective cluster boundaries.
4. **Wet-lab protocol complexity**: Intravenous antibody injections with precise timing, multiple fluorophores, and intravascular specificity validation require specialized FACS infrastructure.
5. **Incomplete vignettes**: ZmanR's README illustrates the workflow but does not provide working end-to-end code with the GBM dataset.

#### Practical Notes

- **Environment**: R 4.1.0, Python 3.8.16 required. MetaCell (Bioconductor), DoRothEA, NicheNet must be installed separately.
- **Data access**: GEO:GSE232040 requires no access restrictions.
- **Common pitfall**: MetaCell's bootstrap-based construction is stochastic — set a random seed and check that metacell assignments are stable across runs before proceeding to cTET.
- **FACS data format**: `FACS_model()` expects a dataframe with specific column names (`FSC.A`, `FSC.W`, `FSC.H`, `SSC.A`, `SSC.W`, `SSC.H`, `log_APC.A`, `Stain`) — preprocessing raw FCS files requires FlowJo or custom scripts not provided.
- **Strengths**: Clean statistical framework, well-documented ZmanR functions, clear biological validation with human data.
- **Weaknesses**: High experimental burden, no containerized analysis, critical downstream analyses (NicheNet, DoRothEA) not wrapped in ZmanR.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
