---
layout: default
permalink: /paper-atlas/scpn-cee56a1f/
title: "scPN"
nav: false
wide: true
description: "scPN 把细胞看成一个 gene interaction network 在未知时间点的静态快照，用分段线性 ODE 同时推断 pseudotime、velocity-like dynamics 和 gene-gene interaction matrix。它的核心不是先排时间再算速度，也不是先算速度再排时间，而是在“给定矩阵排细胞”和“给定细胞顺序拟合矩阵”之间交替更新。"
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
      <span>NAR Genomics and Bioinformatics · 2025</span>
    </div>
    <h1>scPN</h1>
    <p>Simultaneously infer cell pseudotime, velocity field, and gene interaction from multi-branch scRNA-seq data with scPN</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1093/nargab/lqaf144" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scPN">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ZHOUZHEN2002/scPN" target="_blank" rel="noopener noreferrer" aria-label="Open code for scPN">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scPN 方法中文解读

### 一句话概览

scPN 把细胞看成一个 gene interaction network 在未知时间点的静态快照，用分段线性 ODE 同时推断 pseudotime、velocity-like dynamics 和 gene-gene interaction matrix。它的核心不是先排时间再算速度，也不是先算速度再排时间，而是在“给定矩阵排细胞”和“给定细胞顺序拟合矩阵”之间交替更新。

### 1. 它到底想解决什么问题

scRNA-seq 给的是很多细胞的表达快照，没有真实发育时间。传统 trajectory 方法用表达相似性推 pseudotime，但不直接学习动态方程；RNA velocity 方法先从 spliced/unspliced kinetics 得到方向，再推时间，可能出现 pseudotime 和 velocity field 不一致；GRN 方法常常给静态网络，不能自然表示多分支发育中不同 cell types 的不同调控关系。

scPN 的切入点是：如果每个基因是网络里的一个 node，表达值是 node state，那么每个细胞就是这个动态网络在某个未知时间点的观测。要还原发育过程，就要同时恢复：

1. 细胞的时间顺序；
2. 表达沿时间的变化方向；
3. 哪些基因影响哪些基因的 interaction matrix。

### 2. 关键变量

| 名称 | 论文符号 | 代码名 | 含义 |
|---|---|---|---|
| 表达矩阵 | $x$ | `adata.X`, `x` | cell by gene 状态矩阵 |
| 细胞顺序 | $t_i$ | `route`, `latent_time` | inferred pseudotime |
| 基因相互作用矩阵 | $A$, $A^{(k)}$ | `A`, `A_gpu` | gene $j$ 对 gene $i$ 的影响 |
| 分段区域 | $R_k$ | `leiden` cluster | 多分支中的局部动态区域 |
| TF-target prior | $W$ | `target_idx`, `mask` | ChEA 先验 mask |
| 导数 / 速度目标 | $\dot{x}$ | `dy(route, x)` | 沿 pseudotime 的表达变化率 |

### 3. 核心模型直觉

如果所有细胞来自一个简单线性系统，可以写成：

$$
\dot{x}=Ax.
$$

但多分支发育通常不是一个全局矩阵能解释的，所以 scPN 使用 piecewise linear ODE：

$$
\frac{d x_i(t)}{d t}
=\sum_{k=1}^m\sum_{j=1}^N
a_{ij}^{(k)}x_j(t)\mathbf{1}_{\{x_t\in R_k\}}.
$$

直观地说：每个 branch / cluster 有自己的 $A^{(k)}$。同一个 TF 在不同细胞状态下可以有不同 target pattern，这就是 Fig. 4 里 Olig2 在 RadialGlia 和 ImmAstro 网络不同的理论来源。

### 4. 为什么 TSP 会出现

scPN 不知道每个细胞的真实时间，所以需要把细胞重新排序。排序的目标是让相邻时间点的表达和速度都平滑。论文定义两个细胞的距离为：

$$
\operatorname{dist}[i,j]
=\Vert x(t_i)-x(t_j)\Vert
+\Vert Ax(t_i)-Ax(t_j)\Vert.
$$

这就变成一个 TSP-like 问题：找到一条经过所有细胞的 route，让相邻细胞的总距离尽量小。表达项保证状态连续，$Ax$ 项保证动态方向也连续。

代码中这一点是部分支持的：real-data scripts 确实用 `python_tsp` 的 simulated annealing 和 local search 求 route，但脚本里的 transformed-expression distance 是一个 scalar term，不完全等于 paper 的 pairwise $\Vert Ax_i-Ax_j\Vert$。显式 Two-Opt 出现在 `Test&Contrast.ipynb`，不是主要 real-data scripts。

### 5. 怎样拟合 gene interaction matrix

给定 route 后，细胞就有了顺序。代码用 5-point finite-difference stencil 估计 $\dot{x}$：

```text
dy(route, x) -> route-ordered finite difference derivative
```

然后优化：

$$
l_{regre}=\Vert\dot{x}-Ax\Vert^2.
$$

也就是让 $A$ 解释表达沿 pseudotime 的变化。为了让 $A$ 更像 TF-target network，scPN 使用 ChEA prior。论文写作 $l_{prior}=\Vert W\odot A\Vert$；代码实现中，`target_idx` 先变成 mask，`A` 初始化和每轮更新后都会被 mask 限制，同时 loss 里用 reciprocal weights 惩罚非优先位置。因此结论应写成：代码验证了 prior-constrained matrix fitting 的思想，但不是逐字实现论文公式。

### 6. 多分支怎么处理

论文的方法是：

1. Leiden clustering 得到区域 $R_k$；
2. 每个区域内部学习 local route 和 local $A^{(k)}$；
3. 用 cluster centroid distance 建 MST；
4. 按 MST traversal 把 regional pseudotime 拼成 global pseudotime。

代码证据更保守：

- `scPN_Dentate_Gyrus.py` 里确实对 8 个 cluster 分别生成 route 和 connection matrix；
- 后续 global pseudotime 是按 cluster ID 手工读 CSV、反转方向、归一化并赋值；
- 没有在源码中找到通用 centroid MST connector。

所以“piecewise local matrix”有代码支持，“general MST stitching”是 paper claim，公开代码中 `Not found`。

### 7. 输出应该怎么理解

scPN 输出三类东西：

| 输出 | 可以怎么用 | 需要避免的过度解释 |
|---|---|---|
| pseudotime | 看细胞发育顺序是否与已知 cell types / UMAP 结构一致 | 不能当真实实验时间 |
| velocity field | 看 inferred direction 是否与 pseudotime gradient 一致 | 不是传统 spliced/unspliced RNA velocity 的同一建模来源 |
| gene interaction matrix | 提名 TF 和 target hypotheses | 不能直接等同于 causal GRN 或实验证实调控 |

Fig. 4 的 Sox9、Olig2、Stat3、Klf4 等结果适合写成候选 regulator。代码没有找到 85% threshold 和 degree ranking 后处理，因此不要写成“公开代码可完整复现 Fig. 4”。

### 8. 与代码的主要对应关系

| 论文步骤 | 代码证据 | 状态 |
|---|---|---|
| Dentate preprocessing, 2000 HVGs, Leiden 0.1 | `scPN/realdata/scPN_Dentate_Gyrus.py:20-25` | Exact |
| OligoLite/Gastrulation preprocessing | `scPN/realdata/scPN_Oligolite.py:18-23`, `scPN/realdata/scPN_gastrulation.py:18-23` | Partial, 1000 HVGs |
| ChEA mask | three real-data scripts around ChEA parsing | Exact |
| finite-difference derivative | `dy(route, x)` in three scripts | Exact |
| TSP route search | `python_tsp` heuristics in three scripts | Partial |
| masked Adam optimization of $A$ | `optimize_matrix_A` | Partial |
| Dentate branch stitching | `scPN_Dentate_Gyrus.py:171-305` | Partial, manual |
| velocity matrix | `realdata/Test&Contrast.ipynb` | Notebook |
| AutoClass implementation | source search | MISSING |
| MST connector and Fig. 4 threshold | source search | Not found |

### 9. 复现时最容易踩坑的地方

- 路径写死为 `/data1/zzhou/...`，需要系统性改路径。
- 代码大量使用 CUDA tensor，CPU 环境不能直接跑。
- OligoLite/Gastrulation 脚本中可见 `torch`、`optim`、`os`、`pd`、`x`、`cluster`、`adata_file` 等变量/导入缺失，可能依赖 notebook 全局状态。
- README 写了 `import scPN` 的 package-like API，但源码没有找到对应模块。
- paper 的 AutoClass、MST stitching、Fig. 4 后处理不在已读公开源码中。

### 10. 最简学习路线

1. 先记住一个核心循环：`A -> TSP route -> finite difference -> optimize A -> repeat`。
2. 再理解 piecewise：每个 Leiden cluster 可以有自己的 $A^{(k)}$。
3. 最后区分证据层级：paper 给出完整方法图，代码验证主要部件，但不验证每个工程步骤。

一句话总结：scPN 是一个把 pseudotime、velocity-like derivative 和 regulatory matrix 放在同一个动态系统里联合推断的方法；它的思想清晰，公开代码能看到核心部件，但复现完整论文工作流需要补齐不少工程和后处理细节。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scPN

### 基本信息

### 核心问题

scPN 解决的是一个耦合推断问题：在只有静态 scRNA-seq 表达矩阵、没有真实采样时间的情况下，同时恢复细胞 pseudotime、速度场和基因相互作用矩阵。论文认为，传统 trajectory 方法通常先根据表达相似性排序，RNA velocity 方法通常先估计速度再推 pseudotime，GRN 方法又多偏静态，因此三者之间容易出现不一致。scPN 的建模入口是把每个细胞看成基因网络动态系统中的无序快照，再通过分段 ODE 将多分支轨迹分到不同局部线性系统中。

### 方法概览

scPN 的模型主体是 piecewise linear ODE：

$$
\frac{d x_i(t)}{d t}=
\sum_{k=1}^m\sum_{j=1}^N a_{ij}^{(k)}x_j(t)
\mathbf{1}_{\{x_t\in R_k\}}.
$$

这里 $x$ 是 cell by gene 表达矩阵，$R_k$ 是由 Leiden cluster 定义的局部区域，$A^{(k)}$ 是区域特异的 gene-gene interaction matrix。算法采用类似 EM 的交替优化：给定当前 $A$，用表达差异和 $Ax$ 差异构造 TSP 距离并更新细胞顺序；给定当前顺序，用有限差分估计 $\dot{x}$，再优化 $A$ 使 $Ax$ 接近 $\dot{x}$。ChEA TF-target prior 被用于构造先验 mask $W$，使学习到的矩阵更容易解释为候选调控关系。

### 论文结果

论文用两类证据支持方法：

1. 模拟动态系统：Fig. 2 展示 SIS、MP、LV、WC、modified MP、MD 和 piecewise linear system 的真实曲线与预测曲线大体重合，并在图例中报告残差。这个结果说明优化框架能在作者设计的 synthetic dynamics 上恢复时间序列形状，但不等价于真实 scRNA-seq 噪声环境下的稳定性证明。
2. 真实 scRNA-seq 数据：Fig. 3 在 Gastrulation、OligoLite 和 Dentate Gyrus 上展示 scPN pseudotime 和 velocity field，并与 Monocle3、Slingshot、Palantir、scVelo、cellDancer、veloVI 做视觉对比。主文证据主要是 UMAP 上 pseudotime gradient 和 arrow field 的一致性，而不是一个统一数值 benchmark。
3. TF 解释：Fig. 4 基于学到的 cluster-specific matrices 做 TF degree ranking，突出 Sox9、Olig2、Stat3、Klf4 等神经发育相关 TF。该结果应理解为模型生成的候选调控假设，并非实验证实的 causal GRN。

### 代码匹配结论

公开代码能证明 scPN 的核心部件确实存在：预处理、ChEA mask、有限差分导数、TSP/local-search 排序、Adam 优化 $A$、KNN pseudotime smoothing 和部分 velocity notebook。最强证据在 `scPN/realdata/scPN_Dentate_Gyrus.py`，其中包含 8 个 Leiden cluster 的 route/matrix 生成和后续 pseudotime 拼接。

但代码与论文不是完全一致：

- paper 说预处理选择 top 2000 HVGs；Dentate 脚本使用 2000，OligoLite/Gastrulation 脚本使用 1000。
- paper 写 $l_{prior}=\Vert W\odot A\Vert$ 且使 $A$ 只保留 prior 位置；代码实际使用 reciprocal weights、binary mask 和每步 projection，属于同一意图但不是同一公式。
- paper 描述用 cluster centroid distance 和 MST 连接 regional pseudotime；公开 Dentate 脚本可见的是手工 cluster 拼接，没有找到通用 MST 实现。
- paper 的完整 velocity matrix workflow 和 Fig. 4 的 85% threshold / degree ranking 后处理，在已读脚本中没有完整复现；velocity 构造主要是 notebook 证据。
- repo 是脚本和 notebook 集合，不是可安装 package；README 的 `import scPN` 示例没有在源码中找到对应模块 API。

### 复现评分

**Rating: 2 / 5.**

理由：论文和公开 GitHub snapshot 提供了足够理解核心思想的脚本、notebook 和数据文件，且几个关键算法部件能用源码行号定位。但复现门槛高：路径写死为 `/data1/zzhou/...`，代码默认 CUDA，部分脚本缺少可独立运行所需 imports/variables，README API 与源码结构不一致，AutoClass imputation、MST stitching、Fig. 4 postprocessing 和完整 velocity workflow 缺少可直接验证的公开实现。若只想理解方法，材料充足；若要无改动复现实验，公开代码还不够。

### 阅读建议

1. 先读 `Chinese method notes`，建立直觉。
2. 再读 `doc_method.md`，看公式、算法步骤和假设。
3. 读 `doc_code.md`，确认哪些 paper claim 有源码支持，哪些是 `Partial` 或 `Not found`。
4. 读 `figure_analysis.md`，理解每张主图支持什么、不能支持什么。
5. 查 `claude_notes.md`，获取 paper line anchors、code anchors 和未验证清单。

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
