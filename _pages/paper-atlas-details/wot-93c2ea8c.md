---
layout: default
permalink: /paper-atlas/wot-93c2ea8c/
title: "WOT"
nav: false
description: "这篇 Cell 2019 论文提出 Waddington-OT（WOT），目标是从时间序列单细胞 RNA-seq 数据中重建细胞发育/重编程轨迹。核心困难是：scRNA-seq 会破坏细胞，所以同一个细胞及其后代不能被连续观测；实验只能在不同时间点采样一批不同的细胞。因此，研究者需要把离散的“快照”连接成连续的“电影”。"
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
      <span>Cell · 2019</span>
    </div>
    <h1>WOT</h1>
    <p>Optimal-Transport Analysis of Single-Cell Gene Expression Identifies Developmental Trajectories in Reprogramming</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2019.01.006" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Waddington-OT 方法中文解读

### 1. 这篇论文要解决什么问题？

这篇 *Cell* 2019 论文提出 **Waddington-OT（WOT）**，目标是从时间序列单细胞 RNA-seq 数据中重建细胞发育/重编程轨迹。核心困难是：scRNA-seq 会破坏细胞，所以同一个细胞及其后代不能被连续观测；实验只能在不同时间点采样一批不同的细胞。因此，研究者需要把离散的“快照”连接成连续的“电影”（`paper.md:23-39`）。

论文把问题表述为：给定某个时间点的细胞表达状态，推断它未来可能到哪里（descendant distribution），或者给定某个终末细胞群，推断它过去可能来自哪里（ancestor distribution）（`paper.md:43-57`）。

### 2. 为什么已有方法不够？

论文指出，许多轨迹推断方法有三类问题：

1. **不显式使用采样时间。** 有些方法主要适用于稳态系统，不能很好利用时间课程中的先后顺序（`paper.md:31-39`）。
2. **图/伪时间结构过强。** 一维边和零维分叉点很难描述细胞命运逐渐分离的过程（`paper.md:31-39`）。
3. **不建模细胞增殖和死亡。** 在重编程中，不同细胞类型的增长率不同；忽略这一点会导致错误的流向解释（`paper.md:401-415`）。

WOT 的关键创新是把每个时间点的细胞看成基因表达空间中的概率分布，并用允许质量变化的 **unbalanced optimal transport** 来估计相邻时间点之间的耦合。

### 3. 方法直觉

可以把每个时间点的细胞群想象成基因表达空间里的一堆“质量”。普通 OT 问题问：怎样把一个分布搬到另一个分布，总代价最小？WOT 问的是：在细胞会分裂、死亡、分化的情况下，怎样从时间点 $t_i$ 的细胞分布最合理地“运输”到 $t_{i+1}$ 的细胞分布？

论文的建模假设是：短时间间隔内，真实时间耦合可以用最优运输耦合近似；若过程满足 Markov 假设，则相邻时间点的运输图可以组合成更长时间间隔的耦合（`paper.md:221-233`）。

### 4. 输入、输出和主流程

**输入：**

- 细胞 × 基因表达矩阵；
- 每个细胞的采样时间；
- 可选的增殖/凋亡或 growth-rate 先验；
- 用于解释的基因集、细胞集合或终末命运集合。

代码中，`OTModel` 保存表达矩阵、`day` 字段、可选 `covariate` 和 `cell_growth_rate` 字段（`wot/wot/ot/ot_model.py:19-43`）。命令行初始化会传入 matrix、cell days、growth rates、参数和过滤条件（`wot/wot/commands/util.py:146-176`）。

**输出：**

- 相邻时间点之间的 transport map；
- 更长时间跨度的组合 coupling；
- ancestor / descendant distribution；
- fate probability、trajectory、transition table；
- held-out time point 插值验证结果。

**流程图：**

```text
scRNA-seq UMI matrix
  -> 归一化、过滤、选择变量基因、定义基因签名/细胞集合
  -> 每个时间点得到经验分布 P_t
  -> 对相邻时间点 t0, t1:
       取对应细胞
       做 local PCA（论文用 30 维）
       计算平方欧氏距离 cost matrix
       加入 growth/death 先验
       求解 unbalanced entropic OT
       可迭代更新 learned growth
       得到 transport map
  -> 按时间组合 transport maps
  -> 查询祖先、后代、命运、轨迹
  -> 用 held-out 中间时间点做插值验证
  -> 下游解释：基因签名、TF、旁分泌信号、实验验证
```

### 5. 关键数学与参数

#### 5.1 表达矩阵预处理

论文先从 UMI 矩阵 $U$ 得到表达矩阵：

$E=\frac{U_{ij}}{\sumi=1GU_{ij}}\times10^{4}$

并定义 log-normalized 矩阵 $\tilde E=log(E_{ij}+1)$，以及 99.5% 分位数截断的 $\bar E$（`paper.md:271-275`）。这些预处理步骤在论文 STAR Methods 中描述；当前代码包主要消费已经准备好的表达矩阵。

#### 5.2 增殖/死亡先验

论文使用增殖和凋亡签名估计 birth rate $β(x)$ 和 death rate $δ(x)$，并给出 doubling time：

$τ=\frac{\mathrm{ln}\;2}{β-δ}$

默认范围包括 $β_{MAX}=1.7$、$β_{MIN}=0.3$、$δ_{MIN}=0.3$、$δ_{MAX}=1.7$（`paper.md:319-321`）。代码中的 `compute_growth_scores` 把 proliferation / apoptosis 分数通过 sigmoid 变换成 birth/death，再返回 `exp(birth-death)`（`wot/wot/ot/util.py:11-30`）。

#### 5.3 成本矩阵与 OT 参数

论文使用 30 维 local PCA 空间中的平方欧氏距离，并设置：

$ϵ=0.05,\;λ_1=1,\;λ_2=50,\;growth\_iters=3$

（`paper.md:323-327`）。代码默认匹配 `local_pca=30`、`epsilon=0.05`、`lambda1=1`、`lambda2=50`，但 `growth_iters` 默认是 1（`wot/wot/ot/ot_model.py:85-87`）。因此若要复现实验参数，需要显式设为 3。

代码中成本矩阵先在 PCA 空间计算 pairwise squared Euclidean distance，然后除以 median cost（`wot/wot/ot/ot_model.py:243-253`, `:294-309`）。

#### 5.4 Unbalanced entropic OT

论文说 WOT 需要放松质量守恒，因为细胞会增殖或死亡（`paper.md:49-52`）。代码的 OT solver 接收 `C`、`G`、`lambda1`、`lambda2`、`epsilon` 等参数，并在 primal/dual 里包含类似 KL divergence 的边缘约束惩罚项（`wot/wot/ot/optimal_transport.py:45-63`, `:67-130`）。

学习 growth 的实现是：第一次用输入 `G`，之后用上一轮 transport map 的 row sums 作为新的 growth，再求一次 OT（`wot/wot/ot/optimal_transport.py:10-33`）。`OTModel` 会把每轮 learned growth 存成 `g0`, `g1` 等列（`wot/wot/ot/ot_model.py:318-326`）。

### 6. 轨迹、祖先和后代如何计算？

得到相邻时间点的 transport maps 后，代码可以按时间正向组合它们。`chain_transport_maps` 检查时间路径必须向前，并逐段 glue maps（`wot/wot/tmap/chaining.py:4-40`, `:43-108`）。`TransportMapModel.get_coupling` 对非相邻时间点会自动找路径并组合 maps（`wot/wot/tmap/transport_map_model.py:145-190`）。

然后：

- `push_forward`：把一个时间点的 population 权重乘以前向 transport map，得到后代分布（`wot/wot/tmap/transport_map_model.py:235-299`）。
- `pull_back`：反向乘 map，得到祖先分布（`wot/wot/tmap/transport_map_model.py:301-365`）。
- `fates`：从终末细胞集合往回拉，得到早期细胞属于各命运的概率（`wot/wot/tmap/transport_map_model.py:40-69`）。
- `trajectories`：对目标群体同时向前/向后传播，形成整条轨迹矩阵（`wot/wot/tmap/transport_map_model.py:105-143`）。

### 7. 验证方式

论文使用 **held-out geodesic interpolation**：给定 $t_1<t_2<t_3$，用 $t_1$ 和 $t_3$ 推断中间时间点 $t_2$ 的细胞分布，再与真实 $t_2$ 批次比较 Wasserstein-2 距离，同时比较随机/null models（`paper.md:339-347`）。Figure 2J 中红色 OT 曲线接近绿色 batch-to-batch baseline，并通常优于蓝/青色 null curves（图像 `gr2_lrg.jpg`）。代码实现了 triplet 枚举、local PCA、OT 插值、随机插值、growth/no-growth nulls 和距离记录（`wot/wot/ot/optimal_transport_validation.py:15-196`）。

### 8. 主要生物学结果

论文把 WOT 应用于小鼠 MEF 到 iPSC 的重编程。高质量数据包括 251,203 个细胞（`paper.md:59-63`, `paper.md:281-287`）。Figure 2 展示 FLE landscape、细胞签名、轨迹、祖先分歧和插值验证。Figures 3-5 显示细胞先向 stromal 或 MET 状态分歧，MET 区域再产生 iPSC、trophoblast-like、neural-like 和 epithelial-like 群体。Figure 6 展示旁分泌 ligand-receptor 预测，Figure 7 展示 *Obox6* 和 GDF9 的实验验证（`paper.md:79-164`）。

### 9. 代码复现性与缺口

**已验证代码支持：**

- OTModel 初始化、local PCA、成本矩阵；
- unbalanced entropic OT solver；
- learned-growth iterations；
- transport-map 组合；
- ancestor/descendant/fate/trajectory 查询；
- gene-set scoring；
- interpolation validation。

**重要缺口：**

- `SUPP_MD`/Methods S1 未获取，完整数学推导和完整 paper workflow 不在工作区中；
- global regulatory model 的 live source 未找到；
- paracrine ligand-receptor scoring 实现未找到；
- FLE 生成本身没有在 live package 中验证到，代码主要支持在已有 embedding 上绘图；
- 代码包更像通用 WOT 工具箱，而不是完整论文复现实验仓库。

因此，本工作区对核心算法的复现证据较强，但对全部论文图和下游生物分析的复现证据不完整。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary — Waddington-OT

### Paper

**Optimal-Transport Analysis of Single-Cell Gene Expression Identifies Developmental Trajectories in Reprogramming** introduces **Waddington-OT (WOT)**, a framework for reconstructing probabilistic developmental trajectories from time-course single-cell RNA-seq snapshots. The paper was published in *Cell* in 2019 (DOI `10.1016/j.cell.2019.01.006`; `paper.md:1-5`).

### Problem

Single-cell RNA-seq is destructive: it observes a cell's expression state once and cannot directly follow the same cell or descendants across time. The paper argues that this makes developmental “movies” from discrete time-course snapshots a computational inference problem (`paper.md:23-39`). Existing trajectory methods often do not use collection time, impose graph/pseudotime structures that poorly capture gradual divergence, or ignore growth and death (`paper.md:31-39`, `paper.md:401-415`).

### Proposed method

WOT treats cells at each time point as samples from a probability distribution $P_t$ in gene-expression space. It infers temporal couplings between adjacent time points using **unbalanced optimal transport**, allowing mass to expand or contract with cell growth/death. These adjacent maps are composed under a Markov assumption to estimate longer-range couplings, enabling ancestor distributions, descendant distributions, trajectories, fate probabilities, and shared ancestry (`paper.md:43-57`, `paper.md:221-233`).

Core settings in the paper include squared Euclidean distance in 30-dimensional local PCA space and `$ϵ=0.05, λ_1=1, λ_2=50, growth_iters=3$` (`paper.md:323-327`, `paper.md:393-397`). The code matches the local PCA/cost and most parameter defaults, while `growth_iters` defaults to 1 in the library and must be overridden for the paper setting (`wot/wot/ot/ot_model.py:85-87`, `wot/wot/ot/ot_model.py:294-309`).

### Evaluation and key results

The authors apply WOT to a dense mouse fibroblast-to-iPSC reprogramming time course. After filtering, they analyze 251,203 high-quality cells from an experiment sampled across 18 days (`paper.md:59-63`, `paper.md:281-287`). Figure 2 shows the FLE landscape, cell signatures, inferred trajectories, ancestor divergence, and held-out interpolation validation. The OT interpolation curve in Figure 2J is visually close to the batch-to-batch baseline and better than random null models, supporting the validation described in the text (`paper.md:72-77`, `paper.md:339-347`; image `gr2_lrg.jpg`).

Biologically, the analysis suggests that cells first diverge toward stromal or MET states, then MET gives rise to iPSC, trophoblast-like, neural-like, and epithelial-like populations. Figures 3-5 visualize these fate trajectories and marker/signature trends. Figure 6 presents paracrine ligand-receptor predictions, and Figure 7 shows experimental validation that *Obox6* and GDF9 can enhance reprogramming efficiency (`paper.md:79-164`; images `gr3_lrg.jpg`-`gr7_lrg.jpg`).

### Code-paper match

The public GitHub code at `https://github.com/broadinstitute/wot` is present at commit `ca5e94f05699997b01cf5ae13383f9810f0613f6`. Verified code implements the core reusable WOT algorithm: OT model initialization, local PCA cost matrices, unbalanced entropic OT solvers, learned-growth iterations, map chaining, ancestor/descendant/fate/trajectory queries, gene-set scoring, and interpolation validation (`doc_code.md`).

Overall fidelity is **medium-high for the core algorithm** and **medium for full paper reproduction**. The clone is a software package and example collection, not a complete figure-reproduction repository. Global regulatory model source, paracrine ligand-receptor scoring code, full FLE generation, and exact raw-data-to-figure scripts were not found in the searched live package/notebooks. Methods S1 is referenced by the paper but no supplementary markdown was acquired (`paper.md:223-233`).

### Reproducibility notes

- **Runnable core:** WOT CLI/workflow components exist for computing transport maps, validation summaries, trajectories, fates, and gene-set scores.
- **Important override:** set `growth_iters=3` to match the paper; the package default is 1.
- **Data/scripts gap:** exact paper preprocessing, cell-set construction, regulatory modeling, paracrine scoring, and figure generation require additional materials not present in this workspace.
- **Publish hygiene:** the cloned repo contains large test/notebook data files; publish prep should run large-file checks before staging.
- **Reproducibility rating:** **3/5** — strong reusable method implementation, incomplete paper-specific reproduction evidence.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
