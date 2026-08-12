---
layout: default
permalink: /paper-atlas/jointggmspatialtemporal-27ea9596/
title: "JointGGMSpatialTemporal"
nav: false
description: "JointGGMSpatialTemporal 的核心思想是：把 GGM 边是否存在表示成贝叶斯潜变量 γ，并用空间/时间 MRF 先验让相关图中的同一条边共享信息，从而在多组、空间或时间结构数据中获得更稳定的网络估计。"
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
      <span>Machine Learning Algorithm</span>
      <span>Biometrics · 2017</span>
    </div>
    <h1>JointGGMSpatialTemporal</h1>
    <p>On Joint Estimation of Gaussian Graphical Models for Spatial and Temporal Data</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## JointGGMSpatialTemporal 方法中文解读

### 1. 这篇论文要解决什么问题？

论文关注 **Gaussian graphical model (GGM)** 的图结构估计：在高斯变量 $X$ 中，如果精度矩阵 $\Theta=\Sigma^{-1}$ 的非对角元素 $\Theta_{ij}$ 不为 0，就表示变量 $i$ 与变量 $j$ 在给定其他变量后仍然条件相关。论文首先把单个 GGM 的邻居选择转化为节点逐个回归问题 (`paper.md:263-272`)。

真正的应用场景往往不是只有一个图。例如同一批基因可能在不同脑区、不同发育时间点都有网络。若每个图独立估计，会浪费图之间的相似性；若强迫所有图一样，又会抹掉真实差异。因此作者提出：用贝叶斯邻居选择估计每条边的后验概率，再用 MRF 先验把空间相邻、时间相邻的图连接起来，共同估计多个相关网络 (`paper.md:300-304`)。

### 2. 单图：贝叶斯邻居选择

对节点 $i$，GGM 的条件分布可写成回归形式：

$$
\mathbf{X}_{i}|\mathbf{X}_{\Gamma_i} \sim \mathcal{N}\left(-\mathbf{X}_{\Gamma_i}\Theta_{i\Gamma_i}^{T}\Theta_{ii}^{-1}, \Theta_{ii}^{-1}\mathbf{I}\right).
$$

因此，寻找 $i$ 的邻居等价于判断回归系数中哪些不为 0 (`paper.md:263-272`)。论文定义

$$
\beta_{i\Gamma_i} = -\Theta_{ii}^{-1}\Theta_{i\Gamma_i},
$$

并引入二元潜变量 $\gamma_{ij}$ 表示边是否存在。若 $\gamma_{ij}=0$，$\beta_{ij}$ 来自窄的 spike 正态分布；若 $\gamma_{ij}=1$，$\beta_{ij}$ 来自宽的 slab 正态分布 (`paper.md:272-281`)。直观理解是：

```text
γ_ij = 0  -> β_ij 接近 0 -> 无边
γ_ij = 1  -> β_ij 可明显偏离 0 -> 有边
```

代码中的 `getBNS.m` 对应这个过程：默认迭代 20,000 次、burn-in 10,000 次 (`getBNS.m:3-9`)；每轮更新 β (`getBNS.m:38-46`)、σ (`getBNS.m:47-49`) 和 γ (`getBNS.m:51-55`)；最后把 burn-in 后采样到的 γ 平均成边的后验概率 `obj.postprob` (`getBNS.m:105-107`)。

### 3. 多图：用 MRF 先验共享空间/时间结构

多图扩展的核心是：不要独立地估计每个图的每条边，而是让相关图中的同一条边倾向于状态一致。论文把潜变量写成 $|B|\times |T|\times p\times p$ 的数组 γ，其中 $B$ 是空间位置集合，$T$ 是时间点集合 (`paper.md:300-304`)。

MRF 先验有三个关键参数 (`paper.md:306-336`)：

- $\eta_1$：控制整体稀疏度，类似单图中的边先验概率；
- $\eta_s$：控制空间相似性，越大表示同一时间不同空间位置的边越倾向一致；
- $\eta_t$：控制时间相似性，越大表示同一空间位置相邻时间点的边越倾向一致。

可以把模型理解成下面的流程：

```text
每个图的观测数据
        |
        v
逐节点回归：Xi ~ X_Gamma_i
        |
        v
采样 β、σ、γ
        |
        +-- 空间相邻图：η_s 奖励边状态一致
        +-- 时间相邻图：η_t 奖励边状态一致
        |
        v
后验边概率 postprob
```

论文给出了 $\gamma_{btij}$ 的 logistic 形式条件分布，其中线性项由 $\eta_1$、空间邻居状态和时间邻居状态组成 (`paper.md:339-353`)。由于 MRF 的归一化常数不可直接计算，作者用伪似然近似来做 $\eta_s$ 和 $\eta_t$ 的 MH 更新 (`paper.md:355-358`)。

### 4. 代码如何对应论文方法？

| 论文组件 | 代码位置 | 说明 |
|---|---|---|
| 单图 BNS | `getBNS.m:1-109` | β/σ/γ 的 MCMC 更新，输出 `postprob`。 |
| 空间多图 | `getBNSspatial.m:1-170` | 使用 `etaS` 和 `updategAS.m` 共享空间图的边状态。 |
| 时间多图 | `getBNStemporal.m:1-170` | 使用 `etaT` 和 `updategAT.m` 共享相邻时间图的边状态。 |
| 空间+时间多图 | `getBNSst.m:1-231` | 同时更新 ηS/ηT，并处理观测不足或缺失的时空单元。 |
| γ 条件更新 | `updategAS.m`, `updategAT.m`, `updategASTmiss.m` | 实现 Eq. 4 形式的 logistic 条件概率。 |
| η 的 MH 更新 | `getetaSmh.m`, `getetaTmh.m`, `getetaSmhst.m`, `getetaTmhst.m` | 用伪似然比较新旧 η。 |

特别值得注意的是，`getBNSst.m` 会统计每个时间/空间单元的样本数，并跳过样本数太少的单元 (`getBNSst.m:19-31`)；这对应论文所说模型可以自然处理缺失的 locus/time 组合 (`paper.md:300-302`)。

### 5. 实验结果说明了什么？

论文用三类模拟和一个真实数据分析验证方法：

1. **多个相关图模拟。** Figure 1 比较 MRF、Guo、glasso、JGL-Fused 和 JGL-Group；多数面板中 MRF 的 TP-FP 曲线更高 (`paper.md:501-519`; `figure_analysis.md`)。
2. **时间相关图模拟。** Figure 2 显示时间 MRF 在不同样本数和时间点数下优于基线 (`paper.md:520-536`)。
3. **空间+时间相关图模拟。** Figure 3 显示在扰动比例 0.1、0.2、0.5 下 MRF 曲线都位于基线之上 (`paper.md:537-553`)。
4. **计算时间。** Figure 4 展示节点数、图数量和并行核数对运行时间的影响；论文报告算法复杂度为 $O(p^3)$ (`paper.md:555-578`)。
5. **果蝇脑发育数据。** Figures 5–6 展示 NCX/non-NCX 脑区、发育时期和 ASD 相关基因/通路的网络及 η 后验分布 (`paper.md:579-645`)。

### 6. 复现性和局限

论文明确给出 MATLAB 代码链接 (`paper.md:651-653`)，仓库中的核心函数与论文方法高度对应。`examples.m` 提供单图、空间、时间、空间+时间四种用法 (`examples.m:16-175`)。

但这个仓库更像核心算法发布，而不是完整论文复现包：没有找到每个论文图的完整绘图脚本、随机种子和独立 supplementary markdown；论文中提到的两步法精度矩阵重估 (`paper.md:290-294`) 也没有在顶层 MATLAB 文件中找到清晰对应实现。CodeGraph 对 MATLAB 文件索引为 0，因此所有代码结论都应以直接读取 `.m` 文件行号为准。

### 7. 一句话总结

JointGGMSpatialTemporal 的核心思想是：把 GGM 边是否存在表示成贝叶斯潜变量 γ，并用空间/时间 MRF 先验让相关图中的同一条边共享信息，从而在多组、空间或时间结构数据中获得更稳定的网络估计。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## JointGGMSpatialTemporal — Summary

### Paper

- **Title:** On Joint Estimation of Gaussian Graphical Models for Spatial and Temporal Data
- **Journal/year:** *Biometrics*, 2017
- **DOI:** `10.1111/biom.12650`
- **Code:** `https://github.com/linzx06/Spatial-and-Temporal-GGM`, acquired at commit `8dbddd424484b9cb3dd172c6380057a6e763ef50` (`paper.md:651-653`).

### Problem

The paper addresses estimation of Gaussian graphical models (GGMs), where graph edges encode conditional dependence between variables. Standard approaches estimate one graph at a time, but many biological studies collect related data across groups, locations, or time points. Estimating each graph independently can waste shared information, while overly rigid joint methods can force inappropriate equality of precision-matrix entries. The authors propose a Bayesian neighborhood-selection method that infers edge-inclusion probabilities and then extends it with a Markov random field (MRF) prior so related graphs can borrow strength across spatial and temporal structure (`paper.md:261-304`).

### Method in one paragraph

For each node, the method rewrites GGM neighborhood estimation as a Gaussian regression and puts a spike-slab prior on the regression coefficients through a binary latent edge-state matrix γ (`paper.md:263-281`). For multiple graphs, γ becomes a spatial/time-indexed array, and a pairwise MRF prior rewards matching edge states across spatially related loci and adjacent time points via parameters ηS and ηT (`paper.md:300-336`). The sampler alternates β, σ, γ, and η updates; the final output is the marginal posterior edge probability matrix/array (`getBNS.m:38-60`, `getBNSst.m:84-229`).

### What is novel

- **Bayesian neighborhood selection for GGMs:** A node-wise regression view with spike-slab coefficient priors yields posterior edge probabilities rather than only penalized point estimates (`paper.md:263-294`).
- **Flexible multi-graph sharing:** The MRF prior encodes whether edge states should agree across spatial loci, adjacent time points, or both (`paper.md:300-353`).
- **Estimated sharing strength:** ηS and ηT are estimated by Metropolis-Hastings using a pseudolikelihood approximation because the MRF normalizing constant is generally intractable (`paper.md:355-358`; `getetaSmhst.m:21-28`; `getetaTmhst.m:21-28`).
- **Missing spatial/time cells:** The paper says the model can naturally handle missing locus/time combinations (`paper.md:300-302`), and the code explicitly skips cells with too few replicates in the spatiotemporal wrapper (`getBNSst.m:19-31`).

### Evaluation

The paper evaluates the method on simulations and Drosophila brain development data:

1. **Multiple related graphs:** Three-graph simulations compare MRF to Guo's method, JGL variants, and graphical lasso; Figure 1 visually shows the MRF curve at or near the top in most settings (`paper.md:501-519`; `figure_analysis.md`).
2. **Temporal graphs:** Time-evolving graph simulations show MRF outperforming Guo, glasso, and JGL-Group in TP-vs-FP curves (Figure 2; `paper.md:520-536`).
3. **Spatial+temporal graphs:** Simulations with three spatial loci and ten time periods show MRF above baselines across perturbation levels (Figure 3; `paper.md:537-553`).
4. **Runtime:** The paper reports $O(p^3)$ computational cost and compares serial/parallel strategies (Figure 4; `paper.md:555-578`).
5. **Application:** The Drosophila brain analysis estimates ASD-gene networks across NCX/non-NCX regions and developmental periods, with posterior distributions for edge inclusion and η parameters (Figures 5–6; `paper.md:579-645`).

### Code-paper match

The code match is **high** for the core method. `getBNS.m` implements the single-graph Bayesian neighborhood sampler, including β, σ, and γ updates and posterior edge-probability output (`getBNS.m:1-109`). `getBNSspatial.m`, `getBNStemporal.m`, and `getBNSst.m` implement spatial, temporal, and spatiotemporal versions (`doc_code.md`). The helper files `updategAS.m`, `updategAT.m`, and `updategASTmiss.m` implement γ full-conditionals, while `geteta*.m` files implement η MH updates (`doc_code.md`).

### Reproducibility notes

- The repository includes MATLAB demos for single, spatial, temporal, and spatiotemporal workflows (`examples.m:16-175`).
- Main functions default to 20,000 MCMC iterations and 10,000 burn-in iterations when options are omitted (`getBNS.m:3-9`, `getBNSst.m:3-17`).
- The code exposes posterior edge probabilities (`obj.postprob`) and η traces (`obj.etaSA`, `obj.etaTA`) in the relevant wrappers (`getBNSspatial.m:166-169`, `getBNSst.m:225-229`).
- Gaps: no separate supplementary markdown was acquired; exact plotting scripts and random seeds for every published figure were not found; a clearly named implementation of the optional two-step precision-matrix refit described in the paper was not found (`doc_code.md`).

### Practical takeaway

Use this method when the target output is a set of related conditional-dependence graphs and it is scientifically reasonable that edges should be similar across spatial locations, adjacent time points, or both. The main benefit is not a new optimizer for one GGM; it is a Bayesian edge-state sharing model that converts spatial/temporal relatedness into improved posterior edge estimates.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
