---
layout: default
permalink: /paper-atlas/clades-d16a7353/
title: "CLADES"
nav: false
description: "CLADES 用带时间点和克隆条形码的单细胞数据估计“每个 meta-clone 中，各细胞群以多快速度增殖、死亡或转向其他群体”，再把这些连续时间速率交给 Gillespie 随机模拟，生成单细胞分裂树与终末命运概率。"
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
      <span>Nature Communications · 2025</span>
    </div>
    <h1>CLADES</h1>
    <p>CLADES: a hybrid NeuralODE-Gillespie approach for unveiling clonal cell fate and differentiation dynamics</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-63150-6" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CLADES 中文方法解读

### 一句话理解

CLADES 用带时间点和克隆条形码的单细胞数据估计“每个 meta-clone 中，各细胞群以多快速度增殖、死亡或转向其他群体”，再把这些连续时间速率交给 Gillespie 随机模拟，生成单细胞分裂树与终末命运概率。

### 输入和输出

输入不是单个细胞的轨迹，而是张量 $N(t,c,p)$：时间点 $t$、meta-clone $c$、细胞群 $p$ 的绝对/缩放计数；另有 PAGA 等得到的允许转移图 $L$、观测时间、总细胞数缩放和生物约束。输出包括 clone-specific 转移矩阵 $K_c(t)$、bootstrap 置信区间，以及随机模拟得到的分裂次数和 fate probability。

meta-clone 是对条形码克隆的聚合。它提高计数稳定性，但意味着输出描述的是聚合克隆组，而非每个原始 barcode 的精确动力学。

### NeuralODE 动力学

每个 clone 的群体向量满足

$$\frac{dN_c(t)}{dt}=N_c(t)K_c(t).$$

矩阵的非对角元素表示群体间分化速率；对角元素合并净增殖/凋亡项。拓扑掩码 $L$ 禁止没有先验边的转移。`const` 模式直接学习时间不变矩阵；`dynamic` 模式用神经网络根据状态/时间产生变化速率。`torchdiffeq` 的 ODE solver 从 Day 0 积分到观测时间点（`model/ode_block.py:34-175`）。

训练器以 Poisson NLL 比较预测和观测计数，并添加六类正则：过大分化/增殖率、零计数群体速率、禁止增殖或凋亡的群体、不同 clone 的背景结构相似性、负向/凋亡约束等（`trainer/clonaltrans.py:100-299`）。这些项体现强先验；估计速率并非由数据无约束唯一识别。

### 为什么需要 bootstrap

单个最优速率不能表达采样不确定性。CLADES 对数据重采样并重复拟合，通过模型集合计算速率分布和置信区间。代码的当前实现位于 `main_bootstrap.py` 与 `utils/utility.py`；旧分析若只引用 `deprecated_version/clonaltrans_bootstrap.py` 会错过活跃路径。

### Gillespie 部分

NeuralODE 给出群体级平均反应速率，Gillespie SSA 则把它转成离散随机事件：某个细胞增殖、死亡或分化。每一步根据当前细胞数与 $K(t)$ 计算 propensity，随机采样下一事件及等待时间，并随动态模型选择最近时间的速率矩阵（`model/gillespie.py:9-163`）。多次模拟后统计从起始群体到终末群体的概率和分裂次数。

因此 NeuralODE 与 Gillespie 回答不同问题：前者拟合平均计数随时间变化，后者展示在这些估计速率下可能出现的随机单细胞谱系。模拟树是模型生成结果，不是实验直接测得的真实 lineage tree。

### 图和结果应怎样读

- 方法图展示 clone×population 计数进入 NeuralODE，估计 clone-specific kinetics，再进入随机模拟。
- 合成实验比较 constant/dynamic 模式在时间点数量与噪声改变下的恢复能力；模式选择依赖真实速率是否随时间变化。
- 人脐带血和小鼠造血数据展示不同 meta-clone 的 DC、单核、红系等输出差异，并用起始细胞表达差异支持 lineage priming。
- 相关性、marker 和模拟 fate 是相互补充的证据，但仍不能证明某条分化边为直接因果路径；拓扑 $L$ 已预先限制可学习边。

### 代码—论文边界

本地 commit `f990efe061826cb705fdd1ae4f2950b7902fe0e0` 的活跃代码覆盖 ODE、损失、bootstrap、Gillespie 和绘图，核心对应度较高。复现仍为 Partial：配置含绝对路径/GPU 假设；meta-clone、PAGA 拓扑和缩放因子需预先生成；完整论文图依赖 notebooks 和外部数据；动态速率的解释受正则权重、时间采样与可辨识性限制。旧 `deprecated_version/` 不应作为当前入口。

### 证据入口

- 论文：`paper source/PMC12402506/paper.md`
- 主图：`paper source/PMC12402506/images/`
- ODE：`clonaltrans/clonaltrans/model/ode_block.py`
- 活跃训练器：`clonaltrans/clonaltrans/trainer/clonaltrans.py`
- bootstrap：`clonaltrans/clonaltrans/main_bootstrap.py`
- Gillespie：`clonaltrans/clonaltrans/model/gillespie.py`、`main_gillespie.py`
- 配置：`clonaltrans/clonaltrans/config/`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CLADES: Clonal Lineage Analysis with Differential Equations and Stochastic Simulations

**Paper**: CLADES: a hybrid NeuralODE-Gillespie approach for unveiling clonal cell fate and differentiation dynamics
**Journal**: Nature Communications, Vol. 16, 2025
**DOI**: 10.1038/s41467-025-63150-6
**Authors**: Mingze Gao, Melania Barile, et al. (Yuanhua Huang, Elisa Laurenti, Berthold Göttgens groups — HKU + Cambridge)
**Code**: https://github.com/StatBiomed/clonaltrans (v1.2.0)

---

### Motivation & Novelty

#### Biological Problem

Hematopoietic stem cells (HSCs) are heterogeneous: individual clones from the same stem cell pool can produce vastly different proportions of downstream blood cell types (erythroid, myeloid, DC, mast cell lineages) at different rates. This clone-specific kinetic heterogeneity is the biological basis of clonal dominance in aging and leukemia progression, yet it has remained largely unquantified.

The LARRY static barcoding system (*Weinreb et al., Science 2020*) enables tracking of thousands of individual clones across time — but existing computational methods cannot extract quantitative per-clone kinetics from this data.

#### Why Existing Methods Fall Short

| Method | Limitation |
|--------|-----------|
| **Pseudodynamics** (*Fischer et al., Nat. Biotechnol. 2019*) | Models population distribution shifts, not per-clone rates; continuous space only |
| **LineageOT** (*Forrow & Schiebinger, Nat. Commun. 2021*) | Optimal transport coupling between time points; no kinetic rate estimation |
| **CoSpar** (*Wang et al., Nat. Biotechnol. 2022*) | Captures fate bias and early clonal lineage topology, but tracks relative proportions rather than absolute kinetics |
| **RNA velocity** (scVelo, unitvelo) | Transcriptomic dynamics without lineage information |
| **Pseudotime methods** (Palantir, Monocle) | No temporal or clonal resolution |

#### Unique Contributions

1. **Clone-specific kinetic rates**: First method to jointly estimate proliferation and differentiation rates for individual meta-clones rather than population averages
2. **Absolute cell count modeling**: Uses FACS-measured total cell counts with scaling factors, not relative proportions — enabling true rate estimation
3. **Confidence intervals via bootstrapping**: Provides 95% CI for each estimated rate, enabling statistical testing between meta-clones
4. **Gillespie simulation**: Generates lineage trees and fate probabilities from estimated rates, giving a quantitative picture of differentiation topology
5. **Meta-clone framework**: Pools low-barcode-count clones into meta-clones for statistical stability, with interpretable cluster-level biology

---

### Method Overview

CLADES has two core components:

#### 1. NeuralODE Estimator

Models clone dynamics as independent ODEs with two modes:
- **Constant mode**: Time-invariant rates ($K_1, K_2$ are direct parameters) → suitable for steady-state-like systems
- **Dynamic mode**: Time-variant rates from a 2-layer MLP (input: current cell counts → output: rate matrices) → suitable for complex temporal dynamics

The ODE is constrained by a PAGA-derived topology graph $L$ that enforces biologically plausible transition directions. Six penalty terms enforce biological constraints (rate magnitude, terminal fate proliferation, zero-count populations, background resemblance, apoptosis, progenitor growth). PoissonNLL reconstruction loss handles sparse barcoding data robustly.

#### 2. Gillespie Stochastic Simulation Algorithm (SSA)

After estimating rates, CLADES uses a modified Gillespie algorithm to simulate 1000 independent differentiation trajectories from each progenitor type. This produces:
- Number of cell divisions between progenitor and first progeny production
- Probability of each terminal fate being produced from each starting state

See `doc_method.md` for full mathematical details.

---

### Evaluation

#### Synthetic Benchmarks

Validated on synthetic datasets with both time-invariant and time-variant ground-truth rates:
- **Constant mode**: Recovery rate >80% with ≥3 training time points (time-invariant data); outperforms dynamic mode on simple patterns
- **Dynamic mode**: Better for complex time-variant systems; generalizes better even to time-invariant data
- **Noise robustness**: Constant mode stable for noise level <10; dynamic mode stable for noise level <15
- **Recommendation**: Minimum 3 time points (including Day 0) for satisfactory performance

#### Biological Validation

**Human cord blood (GSE276896)**:
- 68,856 cells, 12 populations, 3940 clones → 12 meta-clones
- 12 meta-clones identified with distinct terminal fate outputs (mast cell, erythroid, monocyte, DC)
- Maximum inferred proliferation rate 2.5/day (consistent with >10h cell cycle)
- Example: meta-clone 2 vs 7 both originate in HSC/MPP1 but produce strikingly different DC vs monocyte ratios — CLADES correctly infers significantly higher HSC/MPP2→DC transition rate in meta-clone 2

**Mouse hematopoiesis (Weinreb 2020, Science)**:
- ~130,000 cells, 22 populations, 5859 clones → 13 meta-clones
- Weighted average of meta-clone rates correlates with whole-system rates at Pearson r=0.819
- Meta-clones 5 and 8 identified as non-differentiating clones (retained in progenitor space); confirmed by DEG analysis showing stem cell marker upregulation

**Gene expression validation**:
- DEGs within meta-clone-specific progenitor cells show early lineage priming (e.g., neutrophil-associated Cd48, Chek1, Gfi1 upregulated in mono/neutrophil meta-clones)
- Meta-clone behaviors attributable to distinct transcriptional states at Day 0 progenitors

---

### Reproducibility

**Rating: 3/5** — Data and code available, but full reproduction requires significant GPU compute and manual configuration.

**What is available**:
- Full Python package at https://github.com/StatBiomed/clonaltrans
- Demo datasets (mouse + cord blood) with pre-formatted input files
- 13 figure-reproduction notebooks in `notebooks/` directory
- Raw data: GEO accession GSE276896 (cord blood scRNA-seq)
- Processed data and model inputs: Figshare DOI 10.6084/m9.figshare.27908142

**Environment setup**:
```bash
git clone https://github.com/StatBiomed/clonaltrans
cd clonaltrans
conda env create -f environments.yml
conda activate clonaltrans
# Edit config JSON to set absolute paths and GPU IDs
python ./clonaltrans/main.py --config ./clonaltrans/config/main_dynamic_cordblood.json
```

**Common pitfalls**:
1. **All paths must be absolute** in config files (relative paths not supported)
2. **Bootstrapping takes ~10 hours on 4 GPUs** (800 trials); do not run with fewer resources
3. **Scaling factors must be pre-computed** from FACS data — not automated in the package
4. **Meta-clone formation** is in preprocessing notebooks, not the main package
5. **Config alpha values differ from paper defaults**: cord blood uses [1.0, 0.5, 0.5, 0.25, 0.05, 0.5], not [1.0, 0.5, 0.5, 0.5, 0.1, 1.0]

**Strengths**:
- Clean modular codebase; well-separated config/data/model/trainer/analysis
- Comprehensive notebooks covering all paper figures
- Demo datasets for testing without re-generating raw data

**Weaknesses**:
- No install/pip setup; must run from repo root with sys.path manipulation
- Absolute-only paths make container deployment difficult
- No unit tests; most validation is notebook-based
- Preprocessing (meta-clone formation, scaling factors) requires expert input and custom FACS data

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
