---
layout: default
permalink: /paper-atlas/vetra-1e4fb980/
title: "VeTra"
nav: false
description: "VeTra 面向单细胞 RNA-seq 的轨迹推断问题。传统轨迹推断常根据细胞之间的转录组相似性来排序，但相似性本身通常不能决定轨迹方向，因此很多方法需要用户提供起点、终点、marker 基因或实验先验 。当细胞过程存在复杂分支时，如果方法预设线性、分叉或环形等固定拓扑，也可能限制新结构的发现 。 RNA velocity 的优势是给每个细胞一个局部运动方向和速度，能在不依赖先验的情况下提示细胞状态转移方向 。"
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
      <span>Bioinformatics · 2021</span>
    </div>
    <h1>VeTra</h1>
    <p>VeTra: a tool for trajectory inference based on RNA velocity</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1093/bioinformatics/btab364" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## VeTra 方法中文解读

### 这篇论文要解决什么问题？

VeTra 面向单细胞 RNA-seq 的轨迹推断问题。传统轨迹推断常根据细胞之间的转录组相似性来排序，但相似性本身通常不能决定轨迹方向，因此很多方法需要用户提供起点、终点、marker 基因或实验先验 (`paper.md:39-39`)。当细胞过程存在复杂分支时，如果方法预设线性、分叉或环形等固定拓扑，也可能限制新结构的发现 (`paper.md:41-41`)。

RNA velocity 的优势是给每个细胞一个局部运动方向和速度，能在不依赖先验的情况下提示细胞状态转移方向 (`paper.md:43-45`)。VeTra 的核心思想就是：不要只看细胞相似不相似，而是沿着 RNA velocity 指向的方向，把方向一致、空间上相邻的细胞连接成有向图，再从图中得到不同发育流的细胞集合和伪时间 (`paper.md:51-53`)。

### 输入、输出和总体思路

论文说 VeTra 需要两个输入：低维空间中的二维坐标，以及每个细胞的 RNA velocity 向量 (`paper.md:124-124`)。代码中 `VeTra.__init__()` 直接从两个文本文件读取 `embedding` 和 `delta_embedding` (`VeTra/VeTra.py:60-64`)。运行 `vetra()` 后，代码会为每条轨迹输出：

- `cell_select_k.txt`：第 k 条轨迹选择了哪些细胞；
- `trajectory_k.txt`：这些细胞的伪时间值；
- `trajectory_k.pdf`：二维图上的轨迹/伪时间可视化；
- `TI_results/`：保存上述结果 (`VeTra/VeTra.py:332-379`)。

README 中的最小运行方式是先构造 `VeTra("embedding.txt", "delta_embedding.txt")`，再调用 `vetra(deltaThreshold=12, WCCsizeCutoff=5, clusternumber=3, cosine_thres=0.7, expand=2)` (`VeTra/README.md:22-35`)。

### 核心算法流程

```text
二维细胞坐标 + 二维 RNA velocity 向量
        |
        v
对每个细胞计算向量头部位置：embedding_i + velocity_i
        |
        v
在向量头部附近找候选邻居
        |
        v
用 cos1 过滤速度方向相似的邻居
        |
        v
用 cos2 选择最符合当前细胞运动方向的目标细胞
        |
        v
构建细胞有向图
        |
        v
提取弱连通分量 WCC
        |
        v
在“四维空间”中层次聚类 WCC
        |
        v
扩展邻近且速度方向相似的细胞
        |
        v
用 principal curve 得到每条轨迹的伪时间
```

#### 1. 在 velocity 空间中找候选转移

论文的算法段说，对细胞 $i$，先从它的向量头部附近收集 $k$ 个最近邻，然后用速度向量之间的余弦相似性筛选方向相似的邻居 (`paper.md:110-110`)。代码对应地计算 `embedding_toward = embedding + delta_embedding`，再用投影头部到所有细胞坐标的距离排序候选细胞 (`VeTra/VeTra.py:160-172`)。

论文给出第一个余弦：

$$
cos1_{ij} = \frac{v_i \cdot v_j}{\|v_i\|\|v_j\|}
$$

其中 $v_i$ 和 $v_j$ 是细胞 $i$ 和候选细胞 $j$ 的 velocity 向量 (`paper.md:110-110`)。代码中用 `1 - spatial.distance.cosine(pair_vector, arrow_vector)` 计算同类余弦，并把负值截断成 0 (`VeTra/VeTra.py:174-183`)。

#### 2. 用第二个余弦确定有向边

筛出方向相似的候选细胞后，论文说再选择位于当前细胞上游、且 $cos2$ 最高的细胞作为转移目标 (`paper.md:110-110`)。代码中第二个向量是“当前细胞到候选细胞的位移”：

```python
pair_vector = embedding[sortIndex[k[1]], :] - embedding[i, :]
arrow_vector = delta_embedding[i, :]
cosine_n = 1 - spatial.distance.cosine(pair_vector, arrow_vector)
```

见 `VeTra/VeTra.py:187-210`。代码选择 `cosine_n` 最大的候选点，并向 `graphSource` / `graphTarget` 添加一条从当前细胞到该候选细胞的有向边 (`VeTra/VeTra.py:200-214`)。

这里有一个重要差异：论文公式文字写的是 $cos1_{ij} > 0.5$ (`paper.md:110-110`)，但发布代码的 `vetra()` 默认参数是 `cosine_thres=0.7`，README 示例也是 0.7，并且代码把这个阈值同时用于第一轮方向筛选和第二轮目标选择 (`VeTra/VeTra.py:147-210`, `VeTra/README.md:29-35`)。

#### 3. 从有向图中得到粗粒度轨迹流

论文说，所有细胞的转移关系确定后会得到多个有向图；为了找粗粒度结构，VeTra 提取弱连通分量 WCC (`paper.md:53-53`)。代码用 `networkx.DiGraph()` 建图，再调用 `nx.weakly_connected_components()` 提取 WCC，并按 `WCCsizeCutoff` 过滤太小的分量 (`VeTra/VeTra.py:215-233`)。

然后论文说，WCC 之间还要继续合并：两个子图之间的距离定义为“所有最近细胞对距离的最大值”，细胞距离在四维空间中计算，两维来自表达低维嵌入，两维来自 reduced space 中的 velocity 向量 (`paper.md:112-112`)。代码对应地把 `embedding` 和 `delta_embedding` 拼成 `merge_embed_delta`，用欧氏距离比较两个 WCC 中的细胞集合，再做 complete-linkage 层次聚类，并用 `clusternumber` 切成指定数量的轨迹组 (`VeTra/VeTra.py:157-159`, `VeTra/VeTra.py:252-282`)。

#### 4. 扩展轨迹成员

论文说，为了得到从 root 到 branch 的完整轨迹，VeTra 会把附近且方向相似的细胞也扩展进来，条件是 $cos1_{ij} > 0.7$ (`paper.md:112-112`)。代码将邻居搜索范围乘以 `expand`，对当前轨迹组内细胞附近的细胞计算 velocity 余弦，如果 `cosine_ > 0.7` 且不在原组中，就追加到该轨迹组 (`VeTra/VeTra.py:284-309`)。

#### 5. 用 principal curve 计算伪时间

论文最后说，把每组成员细胞投影到 principal curve 上得到伪时间 (`paper.md:112-112`)。代码在 `find_sink_aera()` 中调用 R 包 `princurve`，取出 principal curve 的 `lambda` 作为沿曲线的位置 (`VeTra/VeTra.py:76-92`)。之后代码还会根据两端点方向和中段平均 velocity 的一致性决定是否反转 lambda 顺序 (`VeTra/VeTra.py:91-143`)。这个方向校正是代码中可见的实现细节，论文没有展开描述。

### 调控因子分析：VeTra + TENET

VeTra 不只输出轨迹，还把轨迹用于调控网络分析。论文说它集成了 TENET 的引擎，用每条推断轨迹识别有影响力的转录因子 (`paper.md:97-99`, `paper.md:122-124`)。

代码中的流程是：

```text
轨迹文件 trajectory_k.txt + 细胞选择 cell_select_k.txt + 表达矩阵
        |
        v
按轨迹伪时间排序选中细胞
        |
        v
运行 TENET_TF / TENET 计算 transfer entropy
        |
        v
根据 FDR 或 top-N links 构建 GRN
        |
        v
统计每个 TF 的 outdegree 并画条形图
```

`run_tenet_tf()` 会对每条轨迹调用 `./TENET_TF`，传入表达文件、线程数、轨迹文件、细胞选择文件、history length 和物种信息，并把输出文件按轨迹编号重命名 (`VeTra/VeTra.py:392-440`)。`PreProcessScriptTF.py` 会转置表达矩阵，并根据物种对应的 GO 转录因子列表生成 TF-target 候选对 (`VeTra/PreProcessScriptTF.py:11-45`)。`runTE_TF.py` 展示了 Python/Java transfer entropy 计算包装：它按伪时间排序细胞表达，调用 `infodynamics.jar` 的 kernel transfer entropy calculator，并写出每对基因的 TE 结果 (`VeTra/runTE_TF.py:18-79`)。最后 `makeGRN_tf()` 过滤链接，`countOutdegree()` 根据作为源基因的次数给 TF 排名并画出轨迹加 regulator bar plot (`VeTra/VeTra.py:659-809`)。

需要注意的是，仓库中的 `TENET` 和 `TENET_TF` 是可执行文件；Python 包装逻辑可以审查，但二进制内部实现不能从当前源码中直接验证。

### 论文结果如何支持方法？

论文在四类真实数据上展示了定性比较：胰腺发育、chromaffin/sympathoblast 发育、细胞周期、海马发育，并与 Slingshot、FateID、PAGA、CellRank、CellPath 等方法比较 (`paper.md:60-88`)。主图 2 的本地图像显示了这些数据集上的多方法 pseudotime/trajectory 面板。论文称 VeTra 在胰腺数据中识别出 ductal、alpha、beta/epsilon 相关三条主要轨迹 (`paper.md:66-73`)，在 chromaffin 数据中捕捉到两条分支 (`paper.md:77-77`)，在细胞周期数据中得到环形轨迹 (`paper.md:81-81`)，在海马数据中区分出五条发育线路 (`paper.md:85-87`)。

主图 1 是最直接的方法图：可以看到 velocity arrows、两个 cosine 条件、有向图、WCC、WCC 聚类和每条轨迹的伪时间。主图 3 展示的是 downstream regulator 分析：每条轨迹旁边都有按 target 数量排序的 regulator 条形图，与代码中的 `countOutdegree()` 绘图逻辑一致 (`VeTra/VeTra.py:740-809`)。

### 可复现性和缺口

当前代码可以复现核心轨迹推断路径和 regulator wrapper 的主要操作：输入读取、cosine 选边、WCC、WCC 聚类、成员扩展、principal-curve 伪时间、TENET wrapper、GRN 过滤和 outdegree 排名都有对应源码 (`VeTra/VeTra.py:60-880`)。README 也给出依赖和最小运行示例 (`VeTra/README.md:7-50`)。

但不是所有论文结果都能从当前仓库完整复现：

- 论文的模拟数据评价使用平均 normalized Hamming distance $D$，得分为 $(1-D)*100$ (`paper.md:91-93`)；在已检查的 8 个 Python 文件、README、`*.sh`、`*.R`、`*.ipynb` 中没有找到该评分实现。
- 论文提到不同数据集可能选择 Velocyto 或 scVelo 产生的 RNA velocity (`paper.md:120-120`)；当前代码主要暴露下游的 `embedding.txt` 和 `delta_embedding.txt` 接口，没有完整的数据预处理/velocity 生成脚本。
- TENET/TENET_TF 的 Python 调用和周边处理可见，但二进制内部不可审查。

因此，可以把 VeTra 的公开代码理解为“核心方法和示例运行代码较完整，论文 benchmark 复现层不完整”。在本工作区的 `doc_code.md` 中，整体 paper-code fidelity 评为 medium。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## VeTra Summary

VeTra is a trajectory-inference method for single-cell RNA-seq that uses RNA velocity direction rather than only transcriptomic similarity. The paper's goal is to infer lineage trajectories and pseudotime without requiring predefined topology, roots, terminals, or marker-gene priors, then use the inferred trajectories for downstream regulator analysis (`paper.md:39-45`, `paper.md:51-53`).

### Why Existing Methods Are Limited

The paper argues that many TI methods order cells by transcriptomic similarity and therefore need external information to orient pseudotime or choose roots and terminals (`paper.md:39-39`). It also argues that fixed topological templates such as linear, bifurcation, or cycle can make complex branching harder to discover (`paper.md:41-41`). RNA velocity gives each cell a direction and speed of movement, which the authors use as the signal for directed trajectory grouping (`paper.md:43-45`).

### Proposed Method

VeTra takes a 2D embedding and an RNA velocity vector for each cell (`paper.md:124-124`; `VeTra/VeTra.py:60-64`). For each cell, it searches candidates near the projected vector head, filters candidates by velocity-vector cosine similarity, selects a transition target using a second cosine criterion, and builds a directed graph (`paper.md:53-53`, `paper.md:110-110`; `VeTra/VeTra.py:160-214`). It extracts weakly connected components, clusters them in a four-dimensional embedding-plus-velocity space, expands memberships using a velocity-cosine threshold, and computes pseudotime by projecting selected cells onto a principal curve (`paper.md:53-53`, `paper.md:112-112`; `VeTra/VeTra.py:215-379`).

For regulator analysis, VeTra wraps TENET/TENET_TF to run transfer-entropy-based GRN inference per inferred trajectory, then ranks regulators by outdegree (`paper.md:97-103`, `paper.md:122-124`; `VeTra/VeTra.py:392-440`, `VeTra/VeTra.py:659-809`). The three local figures support the workflow visually: Figure 1 shows the algorithmic stages, Figure 2 shows real-data method comparisons, and Figure 3 shows trajectory-specific regulator rankings.

### Evaluation

The paper evaluates VeTra on pancreas, chromaffin/sympathoblast, cell-cycle, and hippocampus datasets, comparing against Slingshot, FateID, PAGA, CellRank, and CellPath (`paper.md:60-88`). The reported qualitative results are that VeTra identifies three major pancreas trajectories including ductal, alpha, and beta/epsilon-related branches (`paper.md:66-73`), captures chromaffin and sympathoblast branches (`paper.md:77-77`), identifies a circular cell-cycle trajectory (`paper.md:81-81`), and separates five hippocampal lineages (`paper.md:85-87`). The paper also reports simulated-data evaluation using Dyngen/VeloSim structures and a normalized Hamming-distance score `(1-D)*100` (`paper.md:89-93`).

### Code and Reproducibility

Reproducibility rating: **3/5**. The public repository contains a runnable trajectory implementation, example input files, an example script, dependency notes, TENET/TENET_TF binaries, Python wrappers, and regulator-ranking code (`VeTra/example_run.py:13-22`, `VeTra/README.md:7-50`). The core trajectory algorithm has medium paper-code fidelity: the main graph/WCC/clustering/extension/principal-curve steps are implemented, but the paper/code cosine threshold description differs and TENET executable internals are not source-inspectable (`doc_code.md`).

The main missing reproducibility item is the benchmark/evaluation layer. Direct source verification did not find code for the simulated-data normalized Hamming score, Dyngen/VeloSim benchmark generation, or `(1-D)*100` scoring in the source-like files searched. The repository therefore supports running VeTra and the regulator workflow, but it does not fully reproduce all paper benchmark tables/figures from scripts alone.

### Paper-Code Coverage Notes

- **Exact coverage:** input loading, directed graph construction, WCC extraction, WCC grouping, membership expansion, pseudotime export, and per-trajectory output files.
- **Partial coverage:** cosine threshold details differ between paper prose/formula and released defaults; TENET integration is wrapped but partly opaque because the executable binaries are not source.
- **Not found:** simulated normalized Hamming-distance benchmark scoring implementation.
- **Evidence base:** `paper.md`, the three local figure images, and direct source reads from `VeTra.py`, `runTE.py`, `runTE_TF.py`, preprocessing helpers, `makeTEasMatrix.py`, `countOutdegree.py`, `example_run.py`, and `README.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
