---
layout: default
permalink: /paper-atlas/stt-cfd9302c/
title: "STT"
nav: false
wide: true
description: "STT 可以理解为“多吸引子版本的 RNA velocity + 空间约束随机游走 + Markov coarse-graining”：它用 unspliced/spliced 数据为每个 attractor 学一个局部动力学 tensor，再通过 membership、GPCCA 和空间 kernel 把局部基因表达/剪接动力学连接到全局细胞命运转移。"
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
      <span>Nature Methods · 2024</span>
    </div>
    <h1>STT</h1>
    <p>Spatial transition tensor of single cells</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/cliffzhou92/STT" target="_blank" rel="noopener noreferrer" aria-label="Open code for STT">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STT（Spatial transition tensor）方法中文讲解

### 1. 这篇论文要解决什么问题？

STT 试图解决单细胞和空间转录组数据中的“多稳态细胞命运转变”问题。传统轨迹推断和 RNA velocity 方法可以给细胞状态变化提供方向信息，但论文指出它们有几个局限：许多模型倾向于一个全局平衡态，难以同时表示多个稳定细胞状态；很多方法不能直接加入空间转录组中的物理邻近关系；标准 RNA velocity 主要关注 spliced mRNA 的速度，而 unspliced mRNA 中也包含调控和“吸引到某个状态盆地”的信息（`paper.md:21-37`）。

STT 的核心想法是：不要把所有细胞都看成朝同一个平衡态运动，而是假设数据中存在多个 attractor（吸引子/稳定细胞状态）。每个细胞可以以不同概率属于多个 attractor，过渡细胞则位于这些 attractor 之间的 saddle（鞍点）附近（`paper.md:39-59`）。

### 2. 输入和输出

**输入**包括：

- 每个细胞、每个基因的 unspliced 计数矩阵 `U`；
- spliced 计数矩阵 `S`；
- 初始细胞类型、聚类或 attractor 标注，用于初始化细胞-attractor 归属；
- 如果是空间转录组，还需要空间坐标或空间邻接图；
- 若干超参数，例如 velocity kernel、表达相似性 kernel、空间 kernel 的权重，邻居数、GPCCA 分解组件数、基因筛选阈值、迭代停止阈值等（`paper.md:44-52`, `paper.md:263-268`）。

**输出**包括：

- attractor 特异的 transition tensor；
- 每个细胞属于每个 attractor 的 membership `rho`；
- 细胞转变熵 entropy 和 attractor 层面的转移矩阵；
- 局部 tensor streamline 和全局 transition path；
- multistability genes 和 pathway tensor similarity 分析结果（`paper.md:203-284`）。

### 3. 从 RNA velocity 到多稳态 tensor

论文从一个含 unspliced 和 spliced 计数的随机动力系统开始：

$$\left\{\begin{array}{c}{\mathrm{d}}{U}_{i}=(\;{f}_{i}\left(t,{S}_{1},{\ldots},{S}_&#123;&#123;N}_{\mathrm{G}}}\right)-{\beta }_{i}{U}_{i})&#123;&#123;\mathrm{d}}t}+{\sigma }_{i}{\mathrm{d}}{W}_{i,t},\\ {\mathrm{d}}{S}_{i}=(\,{\beta }_{i}{U}_{i}-{\gamma }_{i}{S}_{i})&#123;&#123;\mathrm{d}}t}+{\sigma }_{i}{\mathrm{d}}{Z}_{i,t},\end{array}\right.$$

这里 `f_i` 表示其他基因对第 `i` 个基因 transcription production rate 的非线性调控，`beta_i` 是 splicing rate，`gamma_i` 是 degradation rate，噪声项表示表达随机性（`paper.md:53-59`）。

STT 的关键近似是：在每个 attractor `c` 附近，可以把复杂的非线性调控局部近似为 attractor 特异的 transcription rate `alpha_{c,i}`，于是得到：

$$\left\{\begin{array}{c}\frac&#123;&#123;\mathrm{d}}{U}_{i}}&#123;&#123;{\mathrm{d}}t}}={\alpha }_{c,i}-{\beta }_{i}{U}_{i},\\ \frac&#123;&#123;\mathrm{d}}{S}_{i}}&#123;&#123;{\mathrm{d}}t}}={\beta }_{i}{U}_{i}-{\gamma }_{i}{S}_{i}.\end{array}\right.$$

论文令 `${\gamma_i}=1`，并用最大似然/最小二乘估计 `alpha_c` 和 `beta`（`paper.md:173-188`）。

### 4. 参数估计和 transition tensor

在硬分配初始化下，单个基因的目标函数是：

$$\mathop{\min }\limits_&#123;&#123;&#123;&#123;\alpha }}}_&#123;&#123;\it{c}}},\beta }\mathop{\sum}\limits_{c=1}^{K}\mathop{\sum}\limits_{k=1}^&#123;&#123;N}_{\mathrm{C}}}{\left({\alpha }_&#123;&#123;c}}-\beta {U}_{k}\right)}^{2}{1}_{k\in {\Omega }_&#123;&#123;c}}}+\mathop{\sum}\limits_{k=1}^&#123;&#123;N}_{\mathrm{C}}}{\left(\beta {U}_{k}-{S}_{k}\right)}^{2}.$$

它有闭式解（`paper.md:184-198`）：

$${\alpha }_&#123;&#123;c}}^{(* )}={m}_&#123;&#123;c}}{\beta }^{\left(* \right)},{\beta }^{(* )}=\frac{\mathop{\sum }\nolimits_{k=1}^&#123;&#123;N}_{\mathrm{C}}}{U}_{k}{S}_{k}}{\mathop{\sum }\nolimits_{k=1}^&#123;&#123;N}_{\mathrm{C}}}\left({U}_{k}^{\,2}+\mathop{\sum }\nolimits_{c=1}^{K}({U}_{k}-{m}_&#123;&#123;c}})^{2}{1}_{k\in {\Omega }_&#123;&#123;c}}}\right)}.$$

然后对每个细胞 `k`、每个 attractor `c` 定义 unspliced 和 spliced 两个速度分量：

$${v}_{k,u,c}={\alpha }_{c}^{(* )}-{\beta }^{\left(* \right)}{U}_{k},\quad {v}_{k,s,c}={\beta }^{\left(* \right)}{U}_{k}-{S}_{k}.$$

对所有基因重复，就得到 transition tensor：

$${v}_{k,l,c,g}\in &#123;&#123;\mathbb{R}}}^&#123;&#123;N}_{\mathrm{C}}\times 2\times K\times {N}_{\mathrm{G}}}.$$

**代码对应关系。** 本地代码中 `construct_tenstor` 实现了这个核心步骤：`par[i,K]` 是 `beta`，`par[i,:K]` 是 `alpha`，`tensor_v[:,:,0,i] = alpha - U * beta`，`tensor_v[:,:,1,i] = U * beta - S`（`STT/example_notebooks/stt/tl/_dynamical_analysis.py:85-195`）。注意代码里的 tensor 存储顺序是 cells × genes × mRNA state × attractor，和论文记号的轴顺序不同，但数学含义一致。

### 5. 从 tensor 到随机游走

STT 不是只估计局部速度，还要把细胞之间的 transition probability 建成 Markov chain。论文把总转移概率写成三部分（`paper.md:203-208`）：

$$P={w}_{1}{P}^&#123;&#123;\mathrm{v}}}+{w}_{2}{P}^&#123;&#123;\mathrm{c}}}+\left(1-{w}_{1}-{w}_{2}\right){P}^&#123;&#123;\mathrm{s}}}.$$

- `P^v`：由 tensor velocity 诱导；
- `P^c`：由基因表达相似性诱导；
- `P^s`：由空间坐标相似性诱导。

因为每个细胞可能属于多个 attractor，STT 先用 membership `rho_{k,c}` 对 attractor-specific tensor 做加权平均：

$${V}_{k,u,g}=\sum _{c}{\rho }_{k,c}{v}_{k,u,c,g},{V}_{k,s,g}=\sum _{c}{\rho }_{k,c}{v}_{k,s,c,g}.$$

再用 inner-product kernel 构建速度诱导的转移倾向：

$${w}_&#123;&#123;kl}}=\exp ({V}_{k,u}^{T}\Delta {U}_&#123;&#123;kl}}+{V}_{k,s}^{T}\Delta {S}_&#123;&#123;kl}}).$$

**代码对应关系。** `aver_velo` 用 `tensor_v` 与 membership 做点积来得到平均速度（`STT/example_notebooks/stt/tl/_dynamical_analysis.py:197-206`）。`dynamical_analysis` 使用 CellRank 的 `VelocityKernel(..., scheme='dot_product')`，再和 expression connectivity kernel 混合；如果 `use_spatial=True`，再和 spatial kernel 混合（`STT/example_notebooks/stt/tl/_dynamical_analysis.py:42-51`）。

### 6. GPCCA、membership 和 entropy

有了随机游走矩阵以后，STT 用 GPCCA 对非平衡 Markov chain 做 coarse-graining，得到每个细胞属于各个 attractor 的 membership `rho_{k,c}`，以及 attractor 层面的 coarse-grained transition matrix（`paper.md:219-223`）。

细胞的 transition entropy 定义为：

$${\varepsilon }_{i}=-\mathop{\sum }\nolimits_{c=1}^{K}{\rho }_{i,c}\mathrm{ln}{\rho }_{i,c}.$$

直观上，如果一个细胞几乎只属于一个 attractor，entropy 低；如果它对多个 attractor 都有较高 membership，说明它更像过渡细胞，entropy 高。

**代码对应关系。** `dynamical_analysis` 中 `GPCCA(kernel)` 计算 Schur decomposition 和 macrostates，然后把 `g_fwd.macrostates_memberships.X` 存成 membership/rho，把 `coarse_T` 归一化成 `P_hat`（`STT/example_notebooks/stt/tl/_dynamical_analysis.py:53-76`）。`dynamical_iteration` 用 `-np.sum(rho*np.log(rho+1e-8), axis=1)` 计算 entropy（`STT/example_notebooks/stt/tl/_dynamical_analysis.py:294-296`, `STT/example_notebooks/stt/tl/_dynamical_analysis.py:322-325`）。

### 7. 迭代更新：tensor 和 membership 互相改进

STT 的算法中心是一个交替迭代：

1. 给定当前 membership `rho`，重新估计 `alpha_c`、`beta` 和 transition tensor；
2. 给定新的 tensor，重新构建随机游走并用 GPCCA 更新 membership；
3. 直到 membership 改变量低于阈值，或达到最大迭代次数（`paper.md:242-251`）。

论文把 membership 加权后的目标函数写成：

$${\mathcal{J}}\left({\alpha }_{c},\beta,{\rho }_{k,c}\right)=\mathop{\sum }\limits_{c=1}^{K}\mathop{\sum }\limits_{k=1}^&#123;&#123;N}_{\mathrm{C}}}{\left({\alpha }_{c}-\beta {U}_{k}\right)}^{2}{\rho }_{k,c}+\mathop{\sum }\limits_{k=1}^&#123;&#123;N}_{\mathrm{C}}}{\left(\beta {U}_{k}-{S}_{k}\right)}^{2}+\,\lambda \mathop{\sum }\limits_{c=1}^&#123;&#123;N}_{\mathrm{C}}}{a}_{c}^{2}+\lambda {\beta }^{2}.$$

STT 还定义 multistability score，用来筛选最符合多稳态模型的基因（`paper.md:253-256`）：

$$1-\frac{J\left({\alpha }_{c},\beta,{\rho }_{k,c}\right)}&#123;&#123;&#123;&#123;N}}}_&#123;&#123;\rm{C}}}({\rm{Var}}\left(U\right)+{\rm{Var}}\left(S\right))}.$$

**代码对应关系。** `dynamical_iteration` 从 `adata.obs['attractor']` 的 one-hot 编码初始化 `rho`，然后循环执行 PCA、neighbors、`dynamical_analysis`、tensor 重估、平均速度更新和 entropy 差异检查（`STT/example_notebooks/stt/tl/_dynamical_analysis.py:260-376`）。基因筛选通过 `r2_test > thresh_ms_gene` 实现（`STT/example_notebooks/stt/tl/_dynamical_analysis.py:35-38`）。

### 8. 空间信息如何进入 STT？

对于空间转录组，STT 把空间邻近性作为第三个 kernel：空间上靠近的细胞更容易互相转移，也更可能被分到相同或相近的 attractor basin（`paper.md:203-223`）。图 1g 直观展示了 spatial transcriptomics 输入如何与 tensor 模型结合，最终得到 spatial-constrained random walk（`figure_analysis.md`）。

代码中 `use_spatial=True` 时，会基于 `spa_conn_key+'_connectivities'` 构建 spatial connectivity kernel，并用 `spa_weight` 和前面的 tensor/expression kernel 混合（`STT/example_notebooks/stt/tl/_dynamical_analysis.py:268-276`）。

### 9. Dynamical manifold、transition path 和 pathway analysis

为了可视化全局命运结构，STT 定义 dynamical manifold 坐标：

$${y}_{k}=\mathop{\sum} \nolimits_{c=1}^{K}{\rho }_{k,c}{\mu }_{c},$$

其中 `mu_c` 是每个 attractor 在 PCA/UMAP 空间中的中心。然后用 Gaussian mixture density `P(y)` 构建 landscape：

$$\phi \left(y\right)=-{\mathrm{ln}}{\mathcal{P}}(y).$$

代码 `construct_landscape` 正是这样做的：先计算 `rho @ centers`，再用 `GaussianMixture` 拟合并把负 log likelihood 存成 landscape 值（`STT/example_notebooks/stt/tl/_construct_landscape.py:20-75`）。

transition path 在代码中存在于 plotting utility `infer_lineage`：它用 `P_hat` 构建 PyEMMA Markov model，支持最大概率流树 `MPFT`，也支持用 `msm.tpt` 计算指定初末状态之间的 major flux（`STT/example_notebooks/stt/pl/_plot_utils.py:287-370`）。这部分是 notebook/plotting 工具，不在 `stt.tl` 核心命名空间中。

Pathway analysis 的思路是：下载 KEGG 等 pathway 数据库，找出与 multistability genes 有足够重叠的 pathway，用这些基因的 averaged tensor 构建 velocity graph，计算 pathway graph 之间的相关性，然后 PCA、UMAP、K-means 聚类（`paper.md:281-284`）。代码 `compute_pathway` 实现了这些步骤（`STT/example_notebooks/stt/tl/_pathway_analysis.py:29-103`）。

### 10. 论文结果怎么支持这个方法？

- **模拟数据**：图 2 显示，在 toggle switch 和 EMT circuit 中，STT 的 streamline 更接近 ground truth 多稳态结构，并且 cosine similarity boxplot 支持其速度估计优于或竞争于对照方法（`paper.md:67-83`；`figure_analysis.md`）。
- **A549 EMT 数据**：图 3 显示 STT 识别出 E、ICS、M 三个 attractor，transition path 经过 ICS，entropy 和 absorption probability 支持 ICS 是过渡 hub（`paper.md:84-103`）。
- **空间 mouse brain、chicken heart、hemibrain**：图 4–6 显示 STT attractor 与空间区域/细胞类型有对应关系，并能在空间坐标上展示 tensor streamlines 和 pathway dynamics（`paper.md:104-151`）。

### 11. 代码可复现性和缺口

本地代码与论文核心算法的对应度为 **medium**。`_dynamical_analysis.py` 直接实现了 transition tensor、平均速度、CellRank/GPCCA 随机游走、迭代更新、entropy stopping 和空间 kernel 混合；`_construct_landscape.py`、`_pathway_analysis.py`、`_plot_utils.py` 分别实现 landscape、pathway analysis 和 PyEMMA transition path plotting（`doc_code.md`）。

主要缺口：

1. 本 workspace 没有 `SUPP_MD`，但论文多处引用 Supplementary Notes/Tables；数据预处理、超参数表、补充推导和鲁棒性细节不能在本地验证。
2. 仓库偏 notebook/tutorial 风格，README 使用 `import sctt as st`，同时也有 `example_notebooks/stt/` 包结构；完整 notebook 复现实验没有在本分析中运行。
3. Transition path theory/PyEMMA 实现在 plotting utility 里，不是核心 `tl` 分析模块的一部分。
4. 论文也承认 STT 的 attractor 假设不能处理强振荡动力学，例如强 cell-cycle effect 的数据可能需要方法扩展（`paper.md:157-171`）。

### 一句话总结

STT 可以理解为“多吸引子版本的 RNA velocity + 空间约束随机游走 + Markov coarse-graining”：它用 unspliced/spliced 数据为每个 attractor 学一个局部动力学 tensor，再通过 membership、GPCCA 和空间 kernel 把局部基因表达/剪接动力学连接到全局细胞命运转移。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spatial transition tensor of single cells — summary

### What problem does the paper solve?

STT targets cell-state transition inference from single-cell and spatial transcriptomics when multiple stable cell states coexist. The paper argues that common RNA velocity and trajectory tools can miss such multistability because they often model dynamics around one global equilibrium, lack explicit spatial transition constraints, or focus mainly on spliced velocity while ignoring unspliced dynamics that may reveal attraction into cell-state basins (`paper.md:21-37`).

### Proposed method

Spatial transition tensor (STT) models cells in joint unspliced (`U`) and spliced (`S`) count space as belonging probabilistically to multiple attractor basins. For each gene and attractor, it estimates local transcription/splicing parameters and constructs an attractor-specific velocity tensor. It then averages these tensor components by cell-attractor membership, builds a velocity/expression/spatial cellular random walk, and coarse-grains the walk with GPCCA to update memberships and attractor-level transition probabilities (`paper.md:44-66`, `paper.md:173-260`).

The main computational outputs are:

- attractor-specific transition tensor over cells, U/S state, attractors, and genes;
- membership matrix `rho`, entropy, and coarse-grained attractor transition matrix;
- local tensor streamlines and global transition paths on a dynamical manifold;
- multistability genes and pathway-level tensor similarity embeddings (`paper.md:203-284`).

### Evaluation and main results

The paper benchmarks STT on toggle-switch and EMT simulations, where the figures show STT streamlines closer to the ground-truth multistable structure than displayed scVelo/UniTVelo/cellDancer alternatives and higher/competitive cosine-similarity boxplots for velocity recovery (`paper.md:67-83`; `figure_analysis.md`). In A549 EMT data, STT identifies epithelial, intermediate, and mesenchymal attractors and supports the intermediate cell state as a high-entropy transition hub (`paper.md:84-103`). In spatial datasets, STT detects attractors aligned with mouse brain, chicken heart, and adult mouse hemibrain tissue regions and maps pathway-specific tensor dynamics in spatial coordinates (`paper.md:104-151`).

### Code-paper match

The code snapshot is a GitHub release branch clone at commit `1a1e61e4848002bf127670a198844cb11fd067a5`. Core functions in `example_notebooks/stt/tl/_dynamical_analysis.py` implement tensor construction, averaged velocity, CellRank/GPCCA dynamics analysis, iterative membership updates, entropy stopping, spatial kernel mixing, monitor-mode parameter updates, and multistability gene filtering. Landscape construction, pathway analysis, tensor plotting, and PyEMMA-based transition path plotting are also present in the notebook package (`doc_code.md`).

Overall fidelity is **medium**: core STT mechanics are directly implemented, but the repository is notebook-oriented, some functions are in plotting utilities rather than the core `tl` namespace, and supplementary-only hyperparameter/preprocessing details are unavailable locally.

### Reproducibility notes

- Code availability in the paper points to the GitHub release branch and example notebooks; the local repo includes those notebook-oriented scripts and a basic usage block (`paper.md:301-304`; `STT/README.md:20-38`).
- Exact notebook reproduction was not run in this analysis. Claims about code behavior are based on direct source reads.
- `SUPP_MD` is none, although the paper refers to Supplementary Notes/Tables for preprocessing, derivations, hyperparameters, and robustness. Those details remain `MISSING` unless supplied later.
- The code uses CellRank, GPCCA/PyEMMA, scVelo, scanpy, GSEApy, UMAP, and scikit-learn; environment installation may be nontrivial, especially around GPCCA/PyEMMA dependencies (`STT/README.md:20-24`).

### Bottom line

STT is a mechanistic, multistable extension of RNA-velocity-style analysis that uses both unspliced and spliced counts, optional spatial constraints, and Markov-chain coarse graining to infer local tensor dynamics and global attractor transitions. It is best viewed as a research notebook package with clear core algorithm code but incomplete local supplementary evidence for full paper-level reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
