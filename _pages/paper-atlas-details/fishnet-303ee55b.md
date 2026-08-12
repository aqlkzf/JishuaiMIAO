---
layout: default
permalink: /paper-atlas/fishnet-303ee55b/
title: "FISHnet"
nav: false
description: "FISHnet 不是在单一阈值上寻找一条“最佳边界”，而是在多个物理距离尺度上反复做图社区发现，并用随机重复共识 + 相邻阈值平台稳定性筛出可信的多尺度结构域区间。"
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
      <span>Domain Clustering</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>FISHnet</h1>
    <p>FISHnet: detecting chromatin domains in single-cell sequential Oligopaints imaging data</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## FISHnet 方法详解：从单等位基因距离矩阵到多尺度染色质结构域

### 1. 它要解决什么问题？

Sequential Oligopaints DNA FISH 可以在单等位基因、单细胞层面追踪一串按基因组顺序排列的位点。每个等位基因最终可表示为一个 $N\times N$ 的成对距离矩阵 $D$：$D_{ij}$ 是位点 $i$ 与 $j$ 在三维空间中的物理距离，单位通常为 nm（`paper.md:21,41`）。

研究者希望从这个矩阵中找出沿基因组连续的染色质结构域及其边界，但这类数据有三个难点：

1. **信噪比较低。** 单个等位基因只有一次瞬时构象，矩阵中的块状结构远弱于群体 Hi-C。
2. **位点掉失常见。** 探针不可及、重复序列或覆盖不足会形成整行整列的缺失，容易被误判为边界。
3. **结构具有尺度层级。** 小的 subTAD-like 结构可能嵌套在更大的 TAD-like 结构中，单一窗口或单一阈值难以同时识别。

此前用于 Oligopaints 数据的 insulation-score boundary caller（Bintu 等，*Science*, 2018）以滑动窗口寻找边界，但边界线本身不表示哪些边界共同组成一个结构域，也不直接表达嵌套关系；本文模拟中其 AUC 为 0.76，而 FISHnet 为 0.95（`paper.md:62-65,145`；Extended Data Fig. 4）。

FISHnet 的核心思路是：**把不同物理距离阈值下的“近邻关系”变成图，在每张图上做模块度社区发现，再只保留跨相邻阈值稳定存在的结构。**

### 2. 输入和输出

#### 输入

- `input_matrix`：一个等位基因的方形成对距离矩阵，形状为 $N\times N$；
- `distance`：按顺序给出的 nm 阈值列表；
- `plateau_size`：至少连续多少个阈值具有相同结构域数，才视为稳定平台；
- `window_size`：平滑窗口参数；
- `size_exclusion`：需要被重新并入邻居的小社区最大长度；
- `merge`：相距不超过多少个 bin 的边界需要合并。

论文分析的常用设置是 `plateau_size=4`、`window_size=2`、`size_exclusion=3`、`merge=3`，阈值步长为 10 nm（`paper.md:226-238,277-280`）。公开函数本身不自动生成 10-nm 阈值序列，调用者必须显式传入 `distance`。

#### 输出

`FISHnet_main` 返回两个共享键的字典：

- `Domains[group] = [(start, end), ...]`：某个稳定阈值平台对应的结构域区间；
- `Distance_scale[group] = [t_1,t_2,...]`：形成该平台的阈值列表。

区间坐标是矩阵 bin 编号，不会自动转换为基因组坐标（`FISHnet_code/README.md:30-39`; `FISHnet/FISHnet_main.py:215-221`）。

### 3. 整体计算流程

```text
单等位基因三维坐标
  -> 成对距离矩阵 D                         [教程提供]
  -> 可选缺失值线性插值                     [论文使用；仓库实现 Not found]
  -> 对每个距离阈值 t：
       1. 二值化为近邻图
       2. 局部平均平滑
       3. 构造 Newman–Girvan 期望矩阵
       4. Louvain-like 模块度最大化，随机运行 20 次
       5. 记录初步社区数
  -> 寻找社区数在相邻阈值上的稳定平台
  -> 对平台内每个阈值重新运行 20 次并做 adjusted-Rand 共识
  -> 再对同一平台的阈值级共识做一次 adjusted-Rand 共识
  -> 修正过小社区
  -> 提取标签切换位置作为边界
  -> 合并相近边界
  -> 将边界序列转换为结构域区间
```

### 4. 第一步：用距离阈值建立邻接图

对于距离阈值 $t$，论文定义二值邻接关系：若两个位点距离不大于 $t$，则认为它们在这一尺度上相互接近（`paper.md:41`）。

距离阈值本质上是**物理尺度参数**：

- 小阈值只保留非常近的位点对，更容易显出小而嵌套的结构；
- 大阈值保留更多边，社区会合并成更大的结构域。

Figure 1 和 Extended Data Fig. 1 直接显示，阈值增大时平均社区大小上升并最终趋于平台；Figure 5 和 Extended Data Fig. 10 显示 `<150 nm` 的调用主要是小、嵌套结构，而 `>500 nm` 主要是大、非嵌套结构。

**论文/代码差异：**

- 论文写的是 `distance <= threshold`；
- 代码实际为 `input_matrix < thresh`（`FISHnet/FISHnet_main.py:49-54`）。

因此恰好等于阈值的元素在公开实现中不会被置为 1。

### 5. 第二步：平滑二值矩阵

论文将二值矩阵用 2×2 信号平均窗口平滑，得到 0–1 之间的连续邻接权重（`paper.md:44`）。平滑的目的不是制造新结构，而是降低单像素噪声，使对角线附近的块状近邻关系更连续。

代码对位置 $(i,j)$ 计算以下切片的 `nanmean`：

```text
[i-window : i+window, j-window : j+window]
```

并在矩阵边缘截断越界范围（`FISHnet/FISHnet_support_functions.py:29-57`）。

**需要特别注意：**当 `window_size=2` 时，内部位置通常取 4×4 切片，而不是字面上的 2×2。这是复现公开代码行为时必须保留的实现细节。Extended Data Fig. 2 显示，较小的平滑窗口性能最好，窗口过大会模糊并移动边界。

### 6. 第三步：把结构域问题写成模块度最大化

令平滑后的邻接矩阵为 $A$，节点 $i$ 的加权度为

$$
k_i=\sum_j A_{ij}.
$$

论文给出的模块度为（`paper.md:47-50`）：

$$
Q=\frac{1}{m}\mathop{\sum }\limits_{i,j}\left[A_{i,j}-\frac{k_i k_j}{m}\right]\delta(g_i,g_j),
$$

其中 $g_i$ 是节点 $i$ 的社区，$\delta(g_i,g_j)$ 只在两个节点属于同一社区时为 1。直观上：

- $A_{ij}$ 是观察到的接近程度；
- $k_i k_j/m$ 是在保留节点总连接强度时的期望值；
- 观察值高于期望值的节点更适合放进同一结构域。

代码先构造 Newman–Girvan 期望矩阵（`FISHnet/construct_nulls.py:5-12`）：

$$
P_{ij}=\frac{k_i k_j}{\sum_{u,v} A_{uv}},
$$

再构造传给 Louvain 的矩阵（`FISHnet/calculate_modularity.py:16-21`）：

$$
B=\frac{A-\gamma P}{\sum A},\qquad \gamma=1.
$$

**论文/代码差异：**论文将 $m$ 描述为不含对角线的权重和；代码直接使用 `sum(A)`。原始距离矩阵对角线为 0，阈值化后对角线会成为 `True`，平滑还会传播其影响，因此代码目标与论文公式结构接近但并非逐字等价。

### 7. 第四步：随机 Louvain-like 优化

`genlouvain` 从“每个节点各自是一个社区”开始，随机打乱节点顺序，尝试把节点移动到能带来正模块度增益的社区，然后把已形成的社区聚合成更小的矩阵继续优化（`FISHnet/genlouvain.py:31-105`）。停止条件对应：

$$
\Delta Q=Q_{\mathrm{itr}}-Q_{\mathrm{itr}-1}<10^{-10}.
$$

由于节点访问顺序和相同增益下的选择可能不同，同一矩阵可能落入不同局部最优。FISHnet 因此在每个阈值运行 20 次。

代码调用时使用 `seed=None`，NumPy 从系统熵初始化随机状态，而不是保存论文所说的 20 个不同种子。结论是：**默认情况下完全相同的输入也可能得到略有差异的调用，公开接口不支持精确随机复现。**

### 8. 第五步：用 adjusted Rand index 选择共识

FISHnet 不选择模块度 $Q$ 最高的那一次，而是计算所有分区两两之间的 adjusted Rand index（ARI）。ARI 衡量两个社区标签划分是否一致，并校正随机一致性：完全相同为 1，无优于随机时接近 0，也可能略为负数。

对于 20 个分区，代码计算 $20\times20$ 的 ARI 矩阵，求每个分区与其他分区的平均相似度，选择平均值最高的分区（`FISHnet/get_similarity_consensus.py:16-39`）。它可以理解为：

> 在 ARI 相似度下，挑选最接近“这一组分区中心”的真实分区。

这比逐 bin 投票更能保持一个合法的整体社区划分，也避免只追逐某一次随机运行的最高模块度。

### 9. 第六步：寻找跨阈值稳定的平台

FISHnet 将“相邻多个阈值得到相同结构域数”视为稳定证据。`plateau_size=4` 表示至少四个连续阈值满足稳定条件。

公开实现的初步扫描有一个容易忽略的细节（`FISHnet/FISHnet_main.py:59-92`）：

1. 每个阈值先随机运行 20 次；
2. 统计每次的社区数；
3. 对社区数取平均再四舍五入；
4. `find_plateau_points` 按这个四舍五入的数寻找连续平台。

论文叙述更像是“每个阈值先得到共识分区，再统计共识分区的结构域数”（`paper.md:56`）。因此这里的 Match 为 **Partial**。

代码还有一个论文没有描述的连续性保护：如果分区只有两个数值标签，但沿基因组顺序切换超过两次，该次运行不会进入初步社区数统计（`FISHnet_main.py:65-73`）。这是在避免把空间上不连续的重复标签误当成两个连续结构域。

### 10. 第七步：平台内再做两层共识

确定平台后，代码会对平台内每个阈值**重新**运行 20 次 Louvain，并得到阈值级 ARI 共识；然后把同一平台内的多个阈值级共识再做一次 ARI 共识（`FISHnet_main.py:98-121`; `FISHnet_support_functions.py:61-90`）。

于是稳定性来自两个方向：

- **同一阈值内**抵抗随机局部最优；
- **相邻阈值之间**抵抗阈值微小变化。

代价是初步平台扫描和最终调用是两批独立随机运行，平台选择与最终分区都可能随运行变化。

### 11. 第八步：小社区修正、边界合并和区间输出

#### 小社区修正

`Size_exclude_communities` 找出长度 `<= size_exclusion` 的连续社区片段，并把这些 bin 重新分配给左右相邻社区（`FISHnet_support_functions.py:94-205`）。所谓“remove”不是删除 bin，而是重标记。

#### 边界提取

沿着最终社区标签从左到右扫描，标签发生变化的位置即为边界（`FISHnet_main.py:152-172`）。

#### 边界合并

相距不超过 `merge` 个 bin 的边界被归为一组，并由该组的均值替代（`FISHnet_main.py:178-209`）。因此 README 示例中会出现 `48.5` 这类半 bin 边界。

#### 区间输出

排序后的相邻边界被转成 `(start,end)` 区间（`FISHnet_support_functions.py:316-332`）。不同平台键表示不同物理尺度下的结构域集合，而不是强制构建出的严格树结构。

### 12. 论文如何用 FISHnet 做群体和细胞类型分析？

核心仓库实现的是单矩阵结构域调用器。论文还将调用结果用于多个下游流程：

| 下游分析 | 论文方法 | 本地代码状态 |
|---|---|---|
| Ensemble count/frequency/average matrices | 对多等位基因矩阵阈值化、求和，并按非 NaN 观测数或等位基因数归一化（`paper.md:196-211`） | **Not found** |
| 神经元/小胶质细胞亚群 | 将每个等位基因编码成边界向量，计算等位基因相关矩阵，再用 NetworkX greedy modularity 聚类（`paper.md:241-244`） | **Not found** |
| 细胞类型边界统计 | 每个 bin 的卡方检验；10,000 次单尾置换检验（`paper.md:247-256`） | **Not found** |
| 原始距离 PCA 与 FISHnet 边界 PCA | 标准化、协方差/特征分解；边界 PCA 还包含卷积（`paper.md:259-268`） | **Not found** |
| Ensemble domain mask | 每个像素编码被多少层嵌套结构域覆盖，再跨等位基因求和（`paper.md:271-274`） | **Not found** |

这些分析在论文 Methods 中有文字说明，Figures 3–5 和 Extended Data Figures 7–10 也提供了结果证据，但不能声称它们由本地仓库中的脚本实现。

### 13. 评估结果该怎样理解？

- 模拟数据 ROC AUC 为 0.95，优于 boundary caller 的 0.76。
- 40% 模拟 dropout 时 AUC 为 0.91；插值后 80% dropout 仍为 0.88（Extended Data Fig. 3）。
- 在真实 HCT116 的人工 dropout 实验中，插值把高 dropout 下的 FPR 控制在约 5.5%，无插值约升至 9%（Extended Data Fig. 5）。
- 论文覆盖九个数据集、2–30 kb 分辨率、130 kb–2.5 Mb 区域和三个模型系统（`paper.md:142`）。
- RAD21 降解后，HCT116 最强边界的等位基因频率从约 10% 降至 4%（Figure 2）。
- 基于 FISHnet 边界的 PCA 能明显区分 IMR90、K562 和 A549，而原始距离矩阵 PCA 大量重叠（Figure 4）。
- Ensemble domain mask 与 Hi-C 的 Pearson 相关为 0.90、0.88、0.91（HCT116、IMR90、K562；Extended Data Fig. 9）。

这些结果说明 FISHnet 提取的边界/结构域特征具有生物学信息，但不意味着每个单等位基因结构域都等同于群体 Hi-C 的 TAD。

### 14. 代码可复现性与明确边界

记录的代码版本为 commit `e05418d95ac12b2d8f29fa13c9e124fcbbbd0242`。核心调用器、依赖列表和 HCT116 教程 notebook 存在；16 个 Python 文件均可通过语法解析。整体代码—论文保真度为 **medium**，可复现性评估为 **3/5**。

主要限制：

- **MISSING：本地 supplementary Markdown。** 本次未获取、未转换、也未使用 supplementary；不得把论文页面上的 PDF 链接当作已读补充材料。
- **Not found：线性插值实现。** 论文多次使用插值，但核心仓库要求用户自己提供预处理矩阵。
- **Not found：ensemble matrices、cell-type statistics、PCA、domain-mask analyses 实现。**
- **Not found：模拟生成、ROC、参数扫描的完整脚本。**
- 没有自动测试、固定版本环境或随机种子记录。
- 论文说明当前版本主要面向小到中等的对称矩阵（约 `<150` bins）；更大、更噪的数据会显著增加计算成本（`paper.md:148`）。

### 15. 一句话抓住 FISHnet

FISHnet 不是在单一阈值上寻找一条“最佳边界”，而是在多个物理距离尺度上反复做图社区发现，并用**随机重复共识 + 相邻阈值平台稳定性**筛出可信的多尺度结构域区间。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## FISHnet Summary

### Problem

Sequential Oligopaints imaging measures genome folding at single-allele resolution and produces pairwise physical-distance matrices between ordered genomic loci. These matrices are noisy, frequently contain locus dropouts, and can exhibit nested structures across several physical scales. At the time of the study, there were few methods tailored to domain calling in this data type. A prior insulation-score boundary caller applied to Oligopaints data (Bintu et al., *Science*, 2018) identifies change points with a sliding window, but does not directly encode nested domain intervals and performs less well under the paper’s simulations (`paper.md:21-32,62-65,145`; Extended Data Fig. 4).

### Proposed method

FISHnet is a graph-theory method for calling chromatin domains and boundaries from one single-allele pairwise-distance matrix. It:

1. thresholds physical distances at multiple nanometer scales;
2. smooths each binary proximity matrix;
3. partitions the resulting weighted graph by Louvain-like modularity maximization;
4. repeats optimization 20 times and selects an adjusted-Rand consensus;
5. retains domain structures whose domain count is stable across adjacent thresholds;
6. consensus-calls each stable plateau, corrects small communities, merges nearby boundaries, and returns domain intervals.

The threshold sweep is also the hierarchy mechanism: low thresholds preferentially expose small and nested subTAD-like structures, while high thresholds expose larger encompassing domains. Plateau stability and two levels of adjusted-Rand consensus reduce sensitivity to noisy matrices and stochastic local modularity maxima (`paper.md:41-56,163-193`; Figures 1 and 5).

### Main results

- On 606 strings-and-binders simulations, FISHnet achieved ROC AUC 0.95; the compared Bintu boundary caller achieved 0.76 (Figure 1; Extended Data Fig. 4).
- With simulated dropout, performance remained AUC 0.91 at 40% dropout. Linear interpolation markedly improved high-dropout behavior, including AUC 0.88 at 80% simulated dropout (Extended Data Fig. 3).
- On artificially degraded real HCT116 maps, interpolation limited high-dropout false-positive rates to roughly 5.5%, versus about 9% without interpolation (Extended Data Fig. 5).
- FISHnet was applied to nine datasets spanning 2–30-kb resolution, genomic regions of 130 kb–2.5 Mb, and three model systems (`paper.md:142`; Extended Data Fig. 6).
- Frequent single-allele boundary calls aligned with ensemble Hi-C TAD/subTAD boundaries. After RAD21 depletion, the strongest HCT116 boundary decreased from approximately 10% to 4% of alleles (Figure 2; `paper.md:74-85`).
- Boundary profiles revealed folding heterogeneity, including 49 excitatory-neuron and 8 microglia subclusters. FISHnet-boundary PCA separated IMR90, K562, and A549 more clearly than PCA of raw pairwise-distance matrices (Figures 3–4).
- Ensemble FISHnet domain masks correlated with Hi-C at Pearson $r=0.90$, $0.88$, and $0.91$ in HCT116, IMR90, and K562, respectively (Figure 5; Extended Data Fig. 9).

### Code-paper match

The recorded repository snapshot is `FISHnet_code` at commit `e05418d95ac12b2d8f29fa13c9e124fcbbbd0242`. Overall fidelity is **medium**.

The core single-matrix caller is present and directly implements randomized Louvain-like optimization, 20-run adjusted-Rand consensus, plateau grouping, size exclusion, boundary merging, and interval output. A tutorial notebook converts Bintu 2018 HCT116 coordinates to 83×83 distance maps, calls `FISHnet_main`, and plots the result. All 16 Python files parse successfully, and the repository includes a requirements file.

Important paper/code differences remain:

- the paper describes automatic min-to-max thresholds in 10-nm steps, but code requires an explicit threshold list;
- the paper says distance `<= threshold`, while code uses strict `< threshold`;
- `window_size=2` normally averages a 4×4 code slice, not a literal 2×2 window;
- the paper excludes diagonal weights from $m$, while code normalizes by the full adjacency sum;
- plateau discovery uses a rounded mean community count across raw randomized runs before later consensus calls;
- random seeds are not recorded (`seed=None`), so exact calls can vary between runs.

### Reproducibility assessment: 3/5

The core algorithm can be inspected and invoked from the public snapshot, and the tutorial supplies a concrete input and example path. However, the repository does not contain automated tests, a pinned environment, recorded seeds, or a full manuscript reproduction workflow. The following paper-described implementations were **not found** after searching all 16 Python files, the notebook, and both READMEs:

- linear interpolation for dropouts;
- ensemble count, frequency, and average matrices;
- cell-type boundary clustering, chi-square tests, and permutation tests;
- pairwise-distance and FISHnet-boundary PCA;
- ensemble FISHnet domain-mask construction and Hi-C correlation;
- simulation generation, ROC analysis, and parameter-sweep scripts.

The paper further states that the current implementation is intended for symmetric matrices smaller than about 150 bins and that larger or noisier maps increase computational cost (`paper.md:148`). No local supplementary Markdown exists, and none was used in this analysis.

### Bottom line

FISHnet’s key contribution is to transform noisy single-allele distance maps into **stable, multiscale domain intervals** by combining modularity-based community detection with repeated consensus and cross-threshold plateau selection. The article and figures provide strong simulation and cross-dataset evidence, but the public code snapshot supports the core caller rather than the complete population-level analysis used for the manuscript’s ensemble, statistical, PCA, and domain-mask conclusions.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
