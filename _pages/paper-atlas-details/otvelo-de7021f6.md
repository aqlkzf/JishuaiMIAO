---
layout: default
permalink: /paper-atlas/otvelo-de7021f6/
title: "OTVelo"
nav: false
wide: true
description: "OTVelo 解决的是动态基因调控网络（dynamic gene regulatory network, dynamic GRN）推断问题。输入是多个时间点采集的单细胞 RNA-seq 表达矩阵，输出是基因之间的有向、带符号、可随时间变化的调控关系。 难点在于：单细胞测序是破坏性测量，同一个细胞不能在多个时间点重复观测。因此，虽然我们有不同时间点的细胞群体，却没有真实的单细胞轨迹。"
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
      <span>PLOS Computational Biology · 2025</span>
    </div>
    <h1>OTVelo</h1>
    <p>Optimal transport reveals dynamic gene regulatory networks via gene velocity estimation</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1371/journal.pcbi.1012476" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for OTVelo">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/sandstede-lab/OT-Velocity" target="_blank" rel="noopener noreferrer" aria-label="Open code for OTVelo">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## OTVelo 方法中文解读

### 1. 这篇论文要解决什么问题？

OTVelo 解决的是**动态基因调控网络**（dynamic gene regulatory network, dynamic GRN）推断问题。输入是多个时间点采集的单细胞 RNA-seq 表达矩阵，输出是基因之间的有向、带符号、可随时间变化的调控关系。

难点在于：单细胞测序是破坏性测量，同一个细胞不能在多个时间点重复观测。因此，虽然我们有不同时间点的细胞群体，却没有真实的单细胞轨迹。论文指出，如果能知道每个细胞中每个基因表达的变化率，即 gene velocity，就能更好判断调控方向和激活/抑制关系；但 RNA velocity 依赖足够的 spliced/unspliced reads，很多数据并不满足这个条件（`paper.md:59-81`）。

OTVelo 的核心思想是：

> 用最优传输在相邻时间点之间推断“祖先-后代”概率，再用这个概率重构每个细胞的过去/未来状态，从而用有限差分估计基因速度，最后用速度之间的时滞相关或 Granger 因果回归推断 GRN。

### 2. 为什么已有方法不够？

论文对比了多类已有 GRN 方法（`paper.md:65-74`, `paper.md:275-289`）：

- **GENIE3 / GRNBoost2**：基于树模型预测目标基因表达，能给出有向关系，但通常不利用时间戳，也不给出调控符号。
- **SINCERITIES / SCRIBE**：使用时间信息或 Granger 思想，但常需要伪时间排序或聚合统计量，不能自然给出每个时间区间的动态图。
- **SCODE / GRIT / HARISSA / CARDAMOM / scEGOT**：引入线性 ODE、反应模型、Gaussian mixture 或其他显式动态模型；这些模型在某些任务有效，但会引入模型假设。
- **RNA velocity 相关方法**：能提供表达变化方向，但需要测到足够的 spliced/unspliced RNA。

OTVelo 的定位是：利用时间戳 scRNA-seq，但不假设具体的基因表达动力学模型；它通过 OT 估计速度，并能输出时间分解的 GRN（`paper.md:75-81`, `paper.md:236-242`）。

### 3. OTVelo 的整体流程

```text
多个时间点的单细胞表达矩阵
        |
        | log(x+1) 预处理；按真实时间或伪时间分箱
        v
相邻时间点之间求 fused Gromov-Wasserstein OT 耦合 T
        |
        | 用 T 做 barycentric projection，预测细胞过去/未来表达
        v
每个细胞、每个基因的速度 v_g(x_{t,c}, t)
        |
        +--> OTVelo-Corr：OT 加权的时滞速度相关
        |
        +--> OTVelo-Granger：用 elastic-net 回归做 Granger 风格因果推断
        v
每个时间区间的有向带符号 GRN；也可汇总为全局 GRN
```

本地阅读的 Fig 1 图像正是这个流程：A 是时间序列单细胞表达矩阵，B 是 FGW OT 对齐，C 是速度，D 是相关/Granger 推断，E 是各时间区间的权重矩阵和图，F 是跨时间汇总后的调控边表。

### 4. 输入、输出和符号

论文在 `paper.md:83-102` 定义了基本符号：

- 有 *N* 个时间点 *t*<sub>1</sub>, …, *t*<sub>*N*</sub>。
- 每个时间点 *t* 有 *n*(*t*) 个细胞，测量 *m* 个基因。
- *x*<sub>*t*</sub> ∈ ℝ<sup>*m*×*n*(*t*)</sup> 是时间 *t* 的表达矩阵。
- *x*<sub>*t,c*</sub> ∈ ℝ<sup>*m*</sup> 是时间 *t* 第 *c* 个细胞的表达向量。
- *v*<sub>*g*</sub>(*x*<sub>*t,c*</sub>, *t*) 是基因 *g* 在该细胞该时间点的速度。

输出是一个 *m*×*m* 的权重矩阵：行/列表示调控源基因和目标基因，权重大小表示调控强度，符号表示激活或抑制。也可以保留每个相邻时间区间的矩阵，形成动态 GRN（`paper.md:236-242`）。

### 5. 第一步：FGW 最优传输推断细胞转移概率

对两个相邻时间点 *t* 和 *t̃*，OTVelo 要估计一个耦合矩阵 *T*<sub>*t,t̃*</sub>。矩阵中的元素表示：时间 *t̃* 的某个细胞是时间 *t* 某个细胞后代的概率或权重。

论文使用 fused Gromov-Wasserstein（FGW）OT。Eq. (1) 的目标函数包含两部分（`paper.md:107-123`）：

1. **Wasserstein 项**：比较两个时间点细胞在表达空间中的距离 *D*<sub>*t,t̃*</sub>。
2. **Gromov-Wasserstein 项**：比较两个时间点内部的几何结构，即细胞-细胞之间的距离矩阵 *S*<sup>*t*</sup> 和 *S*<sup>*t̃*</sup>。

实际计算时使用带熵正则的 Eq. (2)：

$$
\text{objective} = (1-\alpha)\langle T,D\rangle_F + \alpha\,\text{GW mismatch} - \epsilon H(T).
$$

其中 *α* 控制表达空间距离和结构距离的权衡，*ε* 控制耦合矩阵的平滑程度（`paper.md:124-126`）。

代码实现位于 `Utils/utils_Velo.py`：

- `compute_graph_distances` 用 kNN 图和 Dijkstra 最短路计算时间点内部的 geodesic distance（`Utils/utils_Velo.py:15-24`）。
- `solve_prior` 构造 cross-time cost `M`、两个内部距离 `D1/D2`，按最大值归一化，并调用 POT 的 `entropic_fused_gromov_wasserstein`（`Utils/utils_Velo.py:273-313`）。
- kNN 邻居数使用 `min(0.2*n1, 0.2*n2, 50)` 的规则，和论文实现细节一致（`paper.md:249-255`; `Utils/utils_Velo.py:297-305`）。

### 6. 第二步：barycentric projection 预测细胞状态

有了耦合矩阵 *T* 后，论文用 Eq. (3) 做 barycentric projection：

$$
\mathcal{T}_{t,\tilde{t}}(x_{t,c}) =
\frac{\sum_{\tilde{c}}T^{t,\tilde{t}}_{c,\tilde{c}}x_{\tilde{t},\tilde{c}}}{\sum_{\tilde{d}}T^{t,\tilde{t}}_{c,\tilde{d}}}.
$$

直观理解：一个当前细胞的未来表达状态，是下一时间点所有细胞表达向量的加权平均，权重来自 OT 耦合（`paper.md:128-134`）。

代码中这一点体现在 `solve_velocities` 里的矩阵乘法：例如 forward projection 使用 `counts_all[i+1] @ (T.T / sum(T.T, axis=0))`（`Utils/utils_Velo.py:337-342`）。中间时间点和最后时间点也用类似的正向/反向归一化矩阵乘法（`Utils/utils_Velo.py:363-381`）。

### 7. 第三步：有限差分估计 gene velocity

论文定义了三种速度（`paper.md:136-164`）：

- 第一个时间点只能看未来，所以用 forward velocity；
- 最后一个时间点只能看过去，所以用 backward velocity；
- 中间时间点同时利用过去和未来，所以用 centered finite difference。

如果时间点等间隔，centered velocity 就是 forward 和 backward 的平均；如果不等间隔，则按相邻时间间隔加权。

代码中的 `solve_velocities` 正好对应这三种情况：

- 第一个时间点：`(mapped_future - current) / dt[0]`（`Utils/utils_Velo.py:337-342`）；
- 中间时间点：forward 项和 backward 项按 `dt` 加权求和（`Utils/utils_Velo.py:362-368`）；
- 最后时间点：`(current - mapped_past) / dt[-1]`（`Utils/utils_Velo.py:378-381`）。

代码同时保存 signed velocity 和 absolute velocity（`Utils/utils_Velo.py:352-392`）。这很重要，因为调控符号依赖 signed velocity。

### 8. 第四步 A：OTVelo-Corr

OTVelo-Corr 用 Eq. (6) 计算两个基因之间的 OT 加权时滞相关：

$$
C_{g_1,g_2}=\frac{1}{N-1}\sum_k\sum_c\sum_{\tilde{c}}
v_{g_1}(x_{t_k,c},t_k)v_{g_2}(x_{t_{k+1},\tilde{c}},t_{k+1})
T^{t_k,t_{k+1}}_{c,\tilde{c}}.
$$

如果 *g*<sub>1</sub> 的速度变化先于 *g*<sub>2</sub>，且二者同向，则可能表示激活；如果相关为负，则可能表示抑制（`paper.md:186-206`）。论文还强调，速度会按基因归一化到单位标准差，使相关矩阵无量纲。

代码实现：

- `OT_lagged_correlation` 对 signed velocity 做方差归一化（`Utils/utils_Velo.py:400-440`）。
- `correlation_varied_lags` 计算 `v_t @ T @ v_{t+lag}.T / (Nt-lag)`（`Utils/utils_Velo.py:509-528`）。
- 代码也支持把多个相邻耦合矩阵相乘来处理更大 lag，但实现中最多比较 3 个 lag，而论文公式是一般的 lag>0（`Utils/utils_Velo.py:447-466`）。

### 9. 第四步 B：OTVelo-Granger

OTVelo-Granger 的思想是：如果基因 *g*<sub>1</sub> 的过去速度能帮助预测基因 *g*<sub>2</sub> 的未来速度，那么 *g*<sub>1</sub> 可能调控 *g*<sub>2</sub>。论文 Eq. (7) 使用 elastic-net 回归：

$$
A_{t_k,t_{k+1}}=\arg\min_A
\|v(x_{t_{k+1}},t_{k+1})-A\hat{v}(x_{t_{k+1}},t_k)\|
+\lambda(r\|A\|_1+(1-r)\|A\|_2).
$$

这里 $\hat{v}$ 是把前一时间点速度通过 OT 投影到后一时间点细胞上得到的“配对”速度；λ 控制正则强度，*r* 控制 L1/L2 比例（`paper.md:208-224`）。每个相邻时间段会得到一个矩阵，Eq. (8) 再把它们求和得到全局 GRN（`paper.md:226-229`）。

代码中，当 `elastic_Net=True` 时，`OT_lagged_correlation` 会使用 `ElasticNet` 或 `Ridge`，用投影后的上一时刻速度预测下一时刻速度，保存系数矩阵并跨时间求和（`Utils/utils_Velo.py:484-506`）。默认参数 `alpha_opt=1.0`, `l1_opt=0.5` 对应论文 λ=1、r=0.5（`paper.md:301-305`; `Utils/utils_Velo.py:400`）。

### 10. 结果如何？

论文在 13 个模拟数据集和 9 个实验数据集上验证（`paper.md:59-65`）。本地阅读主图后，可概括为：

- **HARISSA 模拟网络（Fig 3）**：OTVelo-Granger 在多个较复杂网络上表现较强，OTVelo-Corr 在 BN8 等场景表现好；signed AUPRC 与 unsigned AUPRC 趋势大体一致（`paper.md:315-342`）。
- **采样参数（Fig 4）**：时间跨度和相邻时间间隔比每个时间点细胞数更影响性能，说明速度/时滞相关依赖合适的采样时间尺度。
- **BoolODE curated networks（Fig 5）**：OTVelo-Corr 在 mCAD、VSC、HSC、GSD 上整体表现稳定，AUPRC ratio 经常高于随机基线（`paper.md:343-355`）。
- **dropout 和分支（Fig 6-7）**：dropout 会伤害多数方法；分支拆开处理对 Corr 更重要，Granger 对 split/combined 更稳健（`paper.md:356-383`）。
- **不平衡分支（Fig 8）**：reweighted marginals 能更好保留分支结构并提升多分支数据集表现（`paper.md:384-389`），但这个重加权实现在已搜索的 Python 工具代码中没有找到。
- **真实数据（Fig 9-15）**：OTVelo 在实验数据上不是每个指标都第一，但在 scGEM、THP-1、mouse ERS 和大规模 drosophila 场景中表现出竞争力；特别是 OTVelo-Corr 对大基因数更可扩展（`paper.md:390-499`）。

### 11. 代码与论文匹配程度

核心算法代码与论文匹配度较高：

- FGW OT coupling：`Utils/utils_Velo.py:273-313`；
- kNN geodesic distance：`Utils/utils_Velo.py:15-24`；
- finite-difference velocity：`Utils/utils_Velo.py:318-395`；
- Corr / Granger：`Utils/utils_Velo.py:400-551`；
- HARISSA 批处理：`Utils/test_batch_HARISSA.py:33-208`；
- BEELINE/curated 数据处理：`Utils/test_batch_BEELINE.py:70-280`；
- 评估指标：`Utils/evaluation_metrics.py:5-213`。

但复现完整论文还有几个限制：

1. 许多实验结果依赖 notebooks 和外部数据，CodeGraph 只索引了 Python 文件。
2. Fig 8 的非均匀/重加权 marginal 实现在已搜索 `Utils/*.py` 和 notebook 文本中没有找到。
3. 每个真实数据集的完整 preprocessing 和绘图流程没有全部逐 cell 级别验证。

### 12. 方法的直观理解

可以把 OTVelo 理解成三层近似：

1. **用 OT 近似细胞轨迹**：不是追踪真实同一个细胞，而是在相邻时间点的群体之间找概率对应关系。
2. **用轨迹近似速度**：用 projected future/past expression 做有限差分，得到每个基因的变化率。
3. **用速度近似调控**：如果一个基因速度的变化领先并预测另一个基因速度变化，就把它看作潜在调控边。

这种设计的优点是：不需要 spliced/unspliced RNA，不需要指定具体 ODE 模型，还能输出动态 GRN。代价是：结果依赖 OT coupling 的质量、时间采样尺度、分支/细胞比例处理，以及回归/相关的线性或二阶统计假设。

### 13. 主要局限和未来方向

论文讨论了几个未来方向（`paper.md:501-512`）：

- 更长 time lag；
- partial correlation 以控制混杂；
- 非线性 Granger；
- 融合 scATAC-seq；
- unbalanced OT 处理细胞类型比例变化；
- 给 GRN 边权提供统计置信区间或假设检验。

从代码角度看，最值得补齐的是：把非均匀 marginal / unbalanced OT 做成 `solve_prior` 的显式参数，并把 Fig 8 这类实验流程从 notebook 迁移成可测试脚本。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## OTVelo Summary

### Problem

OTVelo targets dynamic gene regulatory network (GRN) inference from time-stamped single-cell gene expression data. The central difficulty is that scRNA-seq destroys cells during measurement, so expression cannot be tracked in the same cell across time. Existing GRN methods often use static expression associations, require pseudotime-ordered cells, assume explicit ODE/reaction models, or need RNA velocity from sufficient spliced/unspliced reads. The paper argues that gene velocity—the rate of change of each gene's expression—would improve GRN inference, but it is often unavailable from sequencing depth alone (`paper.md:59-81`).

### Proposed Method

OTVelo estimates gene velocities from time-stamped scRNA-seq using optimal transport, then infers directed signed GRNs from those velocities. The pipeline is:

1. Log-transform counts and build consecutive time-point cell populations.
2. Solve an entropic fused Gromov-Wasserstein (FGW) OT problem between adjacent time points to estimate transition probabilities between ancestor and descendant cells.
3. Use barycentric projections through the coupling matrix to predict each cell's past/future expression state.
4. Compute forward, backward, or centered finite-difference gene velocities.
5. Infer GRNs by either:
   - **OTVelo-Corr:** OT-weighted time-lagged velocity correlation;
   - **OTVelo-Granger:** elastic-net Granger-style regression of next-time velocities on projected prior-time velocities.
6. Aggregate interval-specific matrices into a global network or keep them as dynamic GRNs (`paper.md:103-242`).

Fig 1 visually confirms this workflow: time-stamped matrices → FGW alignment → cell/gene velocity → Corr/Granger inference → temporal graphs → global aggregation.

### Key Equations

- **FGW OT coupling:** Eq. (1)/(2) combines feature-space cell cost, within-time geometry mismatch, and entropic regularization (`paper.md:107-126`).
- **Barycentric projection:** Eq. (3) predicts a cell's future/past expression state as a coupling-weighted average of cells at another time point (`paper.md:128-134`).
- **Gene velocity:** Eq. (4) uses forward/centered/backward finite differences from projected states (`paper.md:138-164`).
- **Velocity projection:** Eq. (5) pairs unobserved prior velocities with later cells for regression (`paper.md:166-174`).
- **OTVelo-Corr:** Eq. (6) computes OT-weighted time-lagged products of normalized gene velocities (`paper.md:186-206`).
- **OTVelo-Granger:** Eq. (7)/(8) fits interval-specific elastic-net matrices and sums them globally (`paper.md:208-229`).

### Evaluation and Main Results

The paper evaluates OTVelo on 13 simulated datasets and 9 experimental datasets (`paper.md:59-65`). Major result patterns:

- **HARISSA synthetic networks:** OTVelo-Granger performs best on several larger or more complex synthetic networks, while OTVelo-Corr is strong on BN8; signed AUPRC trends generally follow unsigned AUPRC (`paper.md:315-342`; Fig 3 inspected).
- **Sampling sensitivity:** Time lag and measurement period affect accuracy more than moderate changes in cells per time point (Fig 4 inspected; `paper.md:333-342`).
- **Curated BoolODE/BEELINE networks:** OTVelo-Corr performs consistently well for unsigned and signed AUPRC ratios across mCAD, VSC, HSC, and GSD (`paper.md:343-355`; Fig 5 inspected).
- **Dropout and branching:** Dropout degrades most methods, but OTVelo remains competitive in several settings; splitting branches benefits Corr more than Granger (`paper.md:356-383`; Figs 6-7 inspected).
- **Imbalanced branches:** Reweighted marginals improve branch preservation and AUPRC ratios in Fig 8 (`paper.md:384-389`; Fig 8 inspected), but this implementation was not found in the searched package source.
- **Experimental benchmarks:** Results are heterogeneous but competitive: OTVelo-Granger has strong early precision in several BEELINE/STREAMLINE panels, OTVelo-Corr is best or near-best on scGEM Table 3 metrics, OTVelo-Granger has best AUPRC on mouse ERS, and OTVelo-Corr scales to a large *Drosophila* 5000-gene analysis (`paper.md:390-499`; Figs 9-15 inspected).

### Code-Paper Match

The GitHub snapshot at commit `8b8df25183c071d4dd439aaf9d3405d32d3ef0e9` matches the core algorithmic claims well:

- `Utils/utils_Velo.py` implements kNN geodesic distances, entropic FGW couplings, barycentric finite-difference velocities, OTVelo-Corr, lag composition, Granger/ElasticNet, and interval slices.
- `Utils/test_batch_HARISSA.py` and `Utils/test_batch_BEELINE.py` implement representative simulation/curated benchmark pipelines.
- `Utils/evaluation_metrics.py` implements the stated AUPRC/AUROC/signed/early-precision metrics.

The match is not complete for full paper reproduction: major experimental workflows are notebook-based, notebooks were not indexed by CodeGraph, external datasets are required, and the Fig 8 reweighted marginal implementation was not found in searched Python utilities. See `doc_code.md` for source-line labels.

### Reproducibility Notes

- **Code availability:** Public GitHub repository cloned locally as `OT-Velocity/`; README points to tutorial and reproduction notebooks.
- **Dependencies:** The repo includes `requirements.txt`; result notebooks may require downloading external datasets as described in the README.
- **Default parameters:** Paper and code align on α=0.5, ε=0.01, λ=1, and elastic-net ratio r=0.5 for core defaults (`paper.md:301-305`; `Utils/utils_Velo.py:400`).
- **Reproducibility rating:** **3.5/5.** The algorithmic core is readable and line-matched to the paper, but full benchmark reproduction depends on notebooks/external data, and the reweighted marginal experiment is not clearly packaged in searched source.

### Limitations

The paper itself identifies extensions such as longer lags, partial correlation, nonlinear Granger causality, scATAC integration, unbalanced OT, and statistical uncertainty/error quantification (`paper.md:501-512`). From code inspection, the most important practical gap is explicit support for nonuniform/reweighted marginals in the reusable Python function.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
