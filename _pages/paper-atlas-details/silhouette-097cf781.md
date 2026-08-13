---
layout: default
permalink: /paper-atlas/silhouette-097cf781/
title: "Silhouette"
nav: false
description: "这篇论文的核心不是提出新的单细胞整合模型，而是指出：把 silhouette（轮廓系数）直接改造成单细胞整合评分，会系统性误判整合质量。 作者进一步提出 BRAS（batch-removal-adapted silhouette），通过让每个细胞同时“看见”所有其他批次，而不只看最近的批次，修复批次评测中的 nearest-cluster issue（最近簇盲区）。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>Silhouette</h1>
    <p>Shortcomings of silhouette in single-cell integration benchmarking</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/yoseflab/scib-metrics" target="_blank" rel="noopener noreferrer" aria-label="Open code for Silhouette">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Silhouette 在单细胞整合评测中的问题与 BRAS 方法详解

### 一句话理解

这篇论文的核心不是提出新的单细胞整合模型，而是指出：**把 silhouette（轮廓系数）直接改造成单细胞整合评分，会系统性误判整合质量。** 作者进一步提出 BRAS（batch-removal-adapted silhouette），通过让每个细胞同时“看见”所有其他批次，而不只看最近的批次，修复批次评测中的 nearest-cluster issue（最近簇盲区）。

论文发表于 *Nature Biotechnology*，正式卷期年份为 2026，DOI 为 `10.1038/s41587-025-02743-4`。

### 1. 论文要解决什么问题？

水平单细胞整合（horizontal integration）的输入通常是多个共享基因特征的数据集。整合方法输出低维表示，希望同时做到两件事：

1. 去除技术批次效应；
2. 保留真实的细胞类型和生物状态差异。

因此，评测也必须分成两个互补维度：

- **batch removal（批次去除）**：同类细胞中的不同批次是否充分混合；
- **bio-conservation（生物信号保留）**：不同细胞类型是否仍然可区分。

问题在于，很多基准测试把 silhouette 改写为 cell type ASW 或 batch ASW，并把这些分数用于比较不同整合方法产生的不同 embedding。论文认为，这偏离了 silhouette 的原始适用条件（`paper.md:18-24,66-80`）。

### 2. 为什么现有 silhouette 评测不够可靠？

#### 2.1 原始 silhouette 的任务

Rousseeuw 在 *Journal of Computational and Applied Mathematics*（1987）提出 silhouette，用于在**同一个 embedding** 中评价无监督聚类结果。对属于簇 $C_k$ 的细胞 $i$：

$$
a_i=\text{细胞 }i\text{ 到同簇其他细胞的平均距离},
$$

$$
b_i=\text{细胞 }i\text{ 到最近的其他簇的平均距离},
$$

$$
s_i=\frac{b_i-a_i}{\max(a_i,b_i)}.
$$

$s_i\approx 1$ 表示簇内紧、簇间远；$s_i\approx 0$ 表示簇重叠；$s_i\approx-1$ 表示样本可能被分错簇（`paper.md:27-35`）。

#### 2.2 cell type ASW：把细胞类型当作簇

单细胞整合评测常把外部提供的 cell-type label 当成簇标签，然后计算所有细胞的平均 silhouette，并缩放到 $[0,1]$：

$$
\mathrm{Cell\ type\ ASW}
=\frac{\mathrm{unscaled\ cell\ type\ ASW}+1}{2}.
$$

这里有一个容易误读的细节：显示分数 $0.5$ 对应原始 ASW 为 0，也就是细胞类型发生重叠，而不是“中等程度地保留了生物结构”（`paper.md:38-46`）。

#### 2.3 batch ASW：把批次重叠解释为好结果

Luecken 等人在 *Nature Methods*（2022）的 atlas-level scIB benchmark 中采用了按细胞类型分层的 batch ASW。对细胞类型 $j$：

$$
\mathrm{Batch\ ASW}_{j}
=\frac{1}{|C_j|}\sum_{i\in C_j}\left(1-|s_i|\right),
$$

最后对所有细胞类型取平均（`paper.md:55-63`）。这里用 batch label 作为 silhouette 的簇标签；当不同批次重叠时，$s_i$ 接近 0，因此 $1-|s_i|$ 接近 1。

### 3. 三个关键失效机制

#### 3.1 几何偏好不等于生物学正确

Silhouette 天然偏爱紧凑、凸、近似球形且彼此分离的簇。可是整合后的细胞状态可能形成连续轨迹、分支、环形或其他非凸结构。图 1b 中，生物学上等价的两类细胞仅仅因为形状和间距不同，cell type ASW 就从 0.77 变化到 0.93。

因此，分数变化可能反映 embedding 几何风格，而不是生物信号是否保留。

#### 3.2 外部标签会产生不规则或断裂的“簇”

Silhouette 原本评价聚类算法形成的簇；单细胞 benchmark 却使用预先给定的 cell type 或 batch label。同一个标签可能在 embedding 中分成多个岛或形成非凸区域。图 1c 展示了三种完全不同的结构，却得到同样的 cell type ASW 0.65。

全局 batch ASW 尤其严重：一个批次包含多个细胞类型时，同一 batch label 天然对应多个断裂区域。Extended Data Fig. 2 中，整合与未整合示例分别得到 0.98 和 0.96，几乎无法区分。

#### 3.3 nearest-cluster issue：只混合一个邻近批次也能拿高分

标准 silhouette 的 $b_i$ 只考虑最近的其他簇。假设四个样本分成两个组：样本 1 与 2 混合，样本 3 与 4 混合，但两组之间仍然相距很远。每个细胞都能找到一个重叠的“最近批次”，于是 $s_i\approx0$，batch ASW 接近 1；远处仍未整合的另一组不会进入 $b_i$。

图 1d 的强批次效应与无批次效应示例都得到 0.98，直观展示了这一盲区。

### 4. BRAS 如何修复 nearest-cluster issue？

BRAS 保留“按细胞类型计算 $1-|s_i|$，再跨细胞类型平均”的框架，只改变 $b_i$ 的定义（`paper.md:210-228`）。

#### 输入

- $X\in\mathbb{R}^{n\times d}$：整合后的低维 embedding；
- $y_i$：细胞类型标签；
- $g_i$：batch/sample 标签；
- 距离：默认 cosine，也可使用 Euclidean；
- 变体：`mean_other`（默认）或 `furthest`。

#### 4.1 在每个细胞类型内部计算

先固定一个细胞类型 $j$，仅保留满足 $y_i=j$ 的细胞。在这个子集中，把 batch label 当成簇。

对细胞 $i$，$a_i$ 仍然是它到同一 batch 中其他细胞的平均距离。

#### 4.2 默认 mean-other BRAS

BRAS 不再寻找最近的其他 batch，而是把所有其他 batch 的细胞合并：

$$
b_i^{\mathrm{mean\ other}}
=\frac{1}{N_j-|B_{g_i,j}|}
\sum_{q:\,y_q=j,\,g_q\ne g_i}d(x_i,x_q).
$$

其中 $B_{g_i,j}$ 表示与 $i$ 同细胞类型、同 batch 的细胞集合，$N_j$ 是该细胞类型的总细胞数。

然后计算：

$$
s_i^{\mathrm{BRAS}}
=\frac{b_i^{\mathrm{mean\ other}}-a_i}
{\max(a_i,b_i^{\mathrm{mean\ other}})}.
$$

这样，一个远离当前细胞的 batch 不能再被最近的重叠 batch 完全遮蔽。

#### 4.3 furthest BRAS

更保守的变体先计算每个其他 batch 的平均距离，再选择最远的一个：

$$
b_i^{\mathrm{furthest}}
=\max_{h\ne g_i}
\frac{1}{|B_{h,j}|}\sum_{q\in B_{h,j}}d(x_i,x_q).
$$

它更接近 worst-case 检查：只要仍有一个 batch 明显分离，就会降低混合得分。

#### 4.4 聚合为最终分数

对细胞类型 $j$：

$$
\mathrm{BRAS}_{j}
=\frac{1}{|C_j|}\sum_{i\in C_j}\left(1-|s_i^{\mathrm{BRAS}}|\right).
$$

然后对细胞类型集合 $M$ 做非加权平均：

$$
\mathrm{BRAS}
=\frac{1}{|M|}\sum_{j\in M}\mathrm{BRAS}_{j}.
$$

分数越高，表示在各细胞类型内部，不同 batch 越接近充分混合。

### 5. 从输入到输出的完整计算框架

```text
整合 embedding X + cell-type label y + batch label g
                         |
                         v
              按细胞类型 y=j 切分数据
                         |
                         v
             在每个 j 内把 batch 当成簇
                         |
                         v
             计算 cosine/Euclidean 距离
                         |
                         v
       a_i = 到同 batch 其他细胞的平均距离
                         |
             +-----------+-----------+
             |                       |
             v                       v
 b_i = 到所有其他 batch 细胞均值   b_i = 最远其他 batch 的均值
      （默认 mean_other）             （furthest）
             |                       |
             +-----------+-----------+
                         v
              s_i=(b_i-a_i)/max(a_i,b_i)
                         |
                         v
                    1-|s_i|
                         |
                         v
             在每个细胞类型内取平均
                         |
                         v
               跨细胞类型非加权平均
                         |
                         v
                       BRAS
```

### 6. BRAS 不能单独解决什么？

BRAS 修复的是“只看最近批次”这一具体问题，但它仍然依赖 embedding 中的距离和几何结构。因此它不能单独回答：

- 生物学细胞类型是否被错误合并；
- 稀有细胞群是否消失；
- 连续轨迹是否被扭曲；
- 不同批次大小是否造成距离均值偏置；
- 局部邻域组成是否符合研究目标。

特别是过度校正时，所有 batch 都可能混得很好，但不同 cell type 也被混在一起。论文因此建议把 BRAS 或 cell-type-adjusted local mixing 指标，与 ARI/NMI 等 bio-conservation 指标配对，而不是压缩成一个无法解释的单分数（`paper.md:97-100`）。

### 7. 论文如何评测？

#### 数据

- 2D 人工数据：验证球形偏好、不规则簇和 nearest-cluster issue；
- NeurIPS 2021 scRNA-seq：24,704 个细胞的四样本 minimal example，以及 69,249 个细胞的完整数据；
- HLCA：584,944 个健康肺细胞，覆盖 5 种 assay、14 个数据集和 107 个 donor；
- HBCA：51,367 个健康乳腺细胞，82 个 donor、16 个 pool；
- Splatter 模拟 scRNA-seq：从 strong、intermediate、mild 到 none 的嵌套批次效应，并加入 overcorrected 情形。

#### 整合状态

NeurIPS 数据比较：

- `none`：不整合；
- `suboptimal`：batch-aware HVG 选择后 PCA；
- `effective`：默认 liam；
- `optimized`：liam 的 adversarial scaling 设为 5。

liam 由 Rautenstrauch 和 Ohler发表于 *Nucleic Acids Research*（2024）。HLCA/HBCA 则比较未整合、多个 batch-aware HVG/PCA 基线和作者提供的有效 embedding（`paper.md:151-160`）。

#### 指标

- Batch removal：batch ASW、iLISI、定制 CiLISI、BRAS 及其距离/最远簇变体；
- Bio-conservation：cLISI、cell type ASW、NMI cluster/label、ARI cluster/label。

定制 CiLISI 来自 Andreatta 等发表于 *Nature Communications*（2024）的思路：在每个 cell type 内计算 iLISI，再按细胞数加权汇总（`paper.md:204-208`）。

### 8. 图像证据告诉我们什么？

- Fig. 1：直接构造反例，证明 silhouette 会被几何形状和最近簇机制误导。
- Fig. 2：在 NeurIPS minimal example 中，batch ASW 已经很高且次序不稳定；BRAS 和 CiLISI 更能区分 none、suboptimal、effective、optimized。ARI 比 cell type ASW 更有区分力。
- Extended Data Fig. 3：完整 NeurIPS 数据重复了 minimal example 的趋势。
- Extended Data Fig. 4：HBCA 中，传统 batch ASW 甚至把有效整合排得更差，而 BRAS、iLISI/CiLISI 与 NMI/ARI 的方向更合理。
- Extended Data Fig. 5：在已知真值的模拟严重度序列中，batch ASW 长期接近饱和；过度校正示例说明必须同时观察生物保留。
- Extended Data Fig. 6：mean-other 与 furthest BRAS 都比 nearest-cluster ASW 更有区分力，但 BRAS 与 CiLISI 在 HLCA 中明显分歧，说明全局残余分离和局部组成混合不是同一个目标。

以上结论来自对工作区内八张原始图像的直接检查；图像是结果证据，不是可执行复现证据。

### 9. 代码实现与论文的对应关系

工作区包含 scib-metrics commit `ad2afce6acfc09318f92c516e011e86b851413c3`，其 `pyproject.toml` 声明版本 0.5.10；论文用于 HLCA/HBCA 的版本是 0.5.5。

| 论文概念 | 代码位置 | 直接验证结果 |
|---|---|---|
| 标准 silhouette | `scib-metrics/src/scib_metrics/utils/_silhouette.py:105-157` | 精确实现 $(b_i-a_i)/\max(a_i,b_i)$。 |
| cell type ASW | `scib-metrics/src/scib_metrics/metrics/_silhouette.py:9-40` | 对细胞平均并执行 $(\mathrm{ASW}+1)/2$。 |
| batch ASW / BRAS 聚合 | `metrics/_silhouette.py:43-121` | 按 cell type 分层，计算 $1-|s_i|$，先组内平均，再跨类型非加权平均。 |
| mean-other | `utils/_silhouette.py:73-77` | 汇总到所有其他 batch 细胞的距离，再除以其他细胞总数。 |
| furthest | `utils/_silhouette.py:68-72` | 计算其他 batch 的平均距离并取最大值。 |
| cosine 默认值 | `metrics/_silhouette.py:124-162`; `utils/_dist.py:15-50` | `bras()` 默认 cosine，并实现裁剪到 $[0,2]$ 的 cosine distance。 |
| BRAS 发布版本 | `CHANGELOG.md:69-79` | 明确记录 0.5.5 加入 BRAS 和 cosine 支持。 |

代码还包含主文没有说明的边界行为：

- 某细胞类型只有一个 batch，或每个细胞都有唯一 batch 时，该类型会被跳过（`metrics/_silhouette.py:88-91`）；
- 所有类型都被跳过时，当前实现没有显式空结果保护；
- `bras()` 固定执行 $1-|s_i|$ 缩放，不提供 `rescale=False`；
- 分块计算减少中间内存，但每个细胞类型内仍需进行全对全距离计算；
- 当前 Leiden NMI/ARI helper 搜索 0.2、0.4、…、2.0，并用 NMI 最大值选择 resolution，再返回同一 resolution 的 NMI 和 ARI；它不能单独证明论文图中 ARI 的完整优化流程。

### 10. 复现状态与缺失证据

- **Not found — 定制 CiLISI：**供应的 scib-metrics snapshot 只有通用 `lisi_knn`、`ilisi_knn` 和 `clisi_knn`；没有找到按 cell type 循环并按细胞数加权的定制 CiLISI。
- **MISSING — 补充材料 Markdown：**Supplementary Notes 1–4 和 Supplementary Figs. 1–4 未被本地获取，因此无法核验 ARI/NMI resolution 敏感性、异质样本评测建议和 BRAS 的其他限制。
- **Partial — 版本一致性：**当前代码是 0.5.10，不是论文指定的 0.5.5；它可以验证核心公式与当前行为，但不能替代论文的精确运行环境。
- **未运行：**本次分析没有执行测试、下载原始数据或重建图表。

### 11. 如何在自己的 benchmark 中使用这篇论文？

一个稳妥的实践流程是：

1. 保留明确的 `none`、弱校正、有效校正和过度校正对照；
2. 先检查指标是否按照已知质量顺序变化，是否出现接近 1 的饱和；
3. 用 BRAS 检查所有其他 batch 对当前细胞的影响，而不是只依赖 nearest-cluster ASW；
4. 同时报告 ARI/NMI 或其他任务相关的 bio-conservation 指标；
5. 分 cell type、batch 大小和数据来源检查分数，避免一个总分隐藏失败子群；
6. 配合 embedding 可视化和下游生物分析，而不是把单一指标当作最终结论。

### 12. 待验证假设（不是论文结论）

以下内容是从公式产生的研究问题，不能写成已证实结论：

1. cell type 非加权平均可能让极小群体显著增加 BRAS 方差，可用分层 bootstrap 检验；
2. mean-other 可能弱化“小而远”的异常 batch，furthest 可能过度放大它，联合报告两者可揭示这种权衡；
3. 即使局部生物邻域不变，embedding 尺度和距离归一化仍可能改变 BRAS 排名，需要系统的距离敏感性实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Shortcomings of silhouette in single-cell integration benchmarking

### In brief

Rautenstrauch and Ohler show that silhouette-derived metrics are often unreliable for evaluating horizontal single-cell integration. Silhouette was designed by Rousseeuw (*Journal of Computational and Applied Mathematics*, 1987) to assess data-driven clusters within one embedding, but integration benchmarks instead assign external cell-type or batch labels and compare scores across different embeddings. These changes expose geometry bias, irregular-cluster failures, and a nearest-cluster blind spot.

The paper introduces **batch-removal-adapted silhouette (BRAS)**. BRAS retains the cell-type-adjusted batch-ASW aggregation introduced in the atlas-level scIB benchmark by Luecken et al. (*Nature Methods*, 2022), but replaces the nearest-other-batch distance with the mean distance to all cells in other batches; a furthest-other-batch variant is also evaluated. Cosine distance is the default. The paper recommends pairing BRAS or a cell-type-adjusted local mixing metric with an external bio-conservation metric such as ARI or NMI.

### Problem and limitations of existing metrics

For cell-type ASW, silhouette favors compact, spherical, well-separated label geometries even when alternative shapes are biologically equivalent. For batch ASW, values near zero are inverted into high mixing scores, but a cell only needs to overlap its nearest other batch to appear well integrated. Samples can therefore mix within subgroups while strong separation remains between subgroups.

The paper's 2D examples make the failures concrete: biologically equivalent layouts receive different cell-type ASW values; radically different irregular layouts can receive the same value; and strong versus absent nested batch effects both receive batch ASW of 0.98. Global batch ASW is especially problematic because one batch label spanning several cell types creates disconnected, irregular clusters.

### Proposed evaluation strategy

Given an embedding $X$, cell-type labels, and batch labels, BRAS operates within each cell type:

1. treat batches as clusters;
2. compute the within-batch mean distance $a_i$ for each cell;
3. compute $b_i$ as the mean distance to all cells in other batches (default) or the mean distance to the furthest other batch;
4. form $s_i=(b_i-a_i)/\max(a_i,b_i)$;
5. score mixing as $1-|s_i|$;
6. average within cell types, then take an unweighted mean across cell types.

BRAS addresses the nearest-cluster issue, but it remains a geometry-dependent metric and cannot detect biological overcorrection by itself. The paper therefore evaluates batch removal and bio-conservation separately.

### Evaluation and main findings

The study covers constructed 2D examples, a NeurIPS 2021 nested-batch scRNA-seq dataset (24,704-cell minimal example and 69,249-cell full data), HLCA (584,944 healthy cells), HBCA (51,367 healthy cells), and simulated scRNA-seq datasets with known nested-batch severity. Integration states include no correction, batch-aware HVG/PCA baselines, default liam (*Nucleic Acids Research*, 2024), stronger liam correction, and author-provided atlas embeddings.

Across the displayed experiments, conventional batch ASW is frequently saturated, non-monotonic, or inversely ranked. Cell-type ASW and cLISI often have weak dynamic range. BRAS and the custom CiLISI strategy derived from Andreatta et al. (*Nature Communications*, 2024) more consistently track batch-removal quality, while ARI/NMI better track preservation of cell-type structure. The simulated overcorrection case illustrates why strong batch mixing must be paired with bio-conservation evidence.

The authors also report 66 Nature Portfolio publications using silhouette-based batch-removal metrics through their April 2025 search, indicating that the issue affects a widely adopted evaluation practice rather than a niche implementation.

### Code-verified behavior

The supplied repository is scib-metrics 0.5.10 at commit `ad2afce6acfc09318f92c516e011e86b851413c3`. Direct source inspection verifies the standard silhouette equation, cell-type ASW rescaling, cell-type-stratified batch ASW, mean-other and furthest BRAS definitions, cosine-default BRAS, and unweighted averaging across retained cell types. The changelog confirms that BRAS and cosine support entered scib-metrics in version 0.5.5, as stated by the paper.

The code also skips cell types with only one batch or one unique batch per cell, uses chunked all-pairs distance computation, and has no explicit fallback if every cell type is skipped. These implementation details are not specified in the main paper.

### Reproducibility and gaps

**Workspace reproducibility: 2/5 — metric mechanics are verifiable, but the manuscript workflow is not locally runnable.**

- The paper, eight local figures, and the reusable scib-metrics source are present.
- The paper-specific preprocessing, simulations, integration runs, metric orchestration, raw score tables, and figure notebooks are in Zenodo DOI `10.5281/zenodo.15642298`, which was not acquired.
- The custom CiLISI implementation is **Not found** in the supplied scib-metrics snapshot; only generic iLISI and cLISI are present.
- No supplementary Markdown was acquired, so Supplementary Notes 1–4 and Figs. 1–4 cannot be checked locally.
- The paper used scib-metrics 0.5.5 for HLCA/HBCA and scib 1.1.5 for several other metrics, whereas the acquired package snapshot is 0.5.10.
- The Leiden NMI/ARI helper in this snapshot selects an NMI-optimal resolution; it does not by itself prove the exact paper-specific ARI/NMI optimization procedure.

### Takeaway

Do not treat a high silhouette-derived score as sufficient evidence of successful single-cell integration. First check whether the metric respects the known ordering of control embeddings and has useful dynamic range. For batch removal, BRAS removes the nearest-cluster blind spot; for a defensible benchmark, combine it with an independent bio-conservation metric and inspect the embedding and dataset design.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
