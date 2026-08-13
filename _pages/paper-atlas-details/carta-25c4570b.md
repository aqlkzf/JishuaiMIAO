---
layout: default
permalink: /paper-atlas/carta-25c4570b/
title: "CARTA"
nav: false
wide: true
description: "CARTA 的输入不是表达矩阵或 RNA velocity，而是一组末端细胞带有类型标签的 lineage trees。实验只观测到终点细胞，真正经历过的中间祖细胞往往未采样。CARTA 要反推出一个 cell differentiation map：节点是“能产生哪些终末类型”的 potency set，边表示潜能逐步丢失的分化关系。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>CARTA</h1>
    <p>Inferring cell differentiation maps from lineage tracing data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02903-z" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CARTA">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/raphael-group/CARTA" target="_blank" rel="noopener noreferrer" aria-label="Open code for CARTA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CARTA 中文方法解读

### 它解决什么问题

CARTA 的输入不是表达矩阵或 RNA velocity，而是一组末端细胞带有类型标签的 lineage trees。实验只观测到终点细胞，真正经历过的中间祖细胞往往未采样。CARTA 要反推出一个 cell differentiation map：节点是“能产生哪些终末类型”的 potency set，边表示潜能逐步丢失的分化关系。

例如终末类型为 $S=\{A,B,C\}$，祖细胞可标为 $\{A,B,C\}$，较晚祖细胞可标为 $\{A,B\}$，终末细胞分别标为单元素集合。这样不用事先观测或命名每个瞬时祖细胞。

### 核心评分：浪费的潜能

对 lineage tree 内部节点 $v$ 指派 potency label $\ell(v)$。若其实际采样后代只出现 $A$，但标签仍含 $B,C$，这些未实现类型构成 discrepancy。固定 differentiation map 后，CARTA 用 potency labeling problem 在允许标签与父子兼容约束下寻找最小总 discrepancy。分数越低，候选 map 越能解释多棵 lineage trees。

这里“没有在采样后代出现”不等于生物上绝不可能；分数把有限采样与模型复杂度联系起来。因此 CARTA 不只求最低 discrepancy，而是同时考察祖细胞数 $k$。

### 两种输出结构

- CARTA-Tree 约束 potency sets 构成 laminar family，输出树，可表达二叉或多叉分化。
- CARTA-DAG 允许同一终末类型沿多条路径产生，可表达 convergent differentiation。

对固定 $k$，论文把选择 potency sets 与内部节点标签写成混合整数线性规划；本地 `carta/ilp.py` 分别实现 DAG 和 tree 版本，由 Gurobi 求解。CLI 对用户给出的 $k$ 调用 ILP 时传入 `k-1`，因为根祖细胞单独计数（`carta/carta.py:140-155`）。

### 从一组最优解到最终图

1. 读取 Newick lineage trees 和叶节点 cell-state metadata，并裁掉不在目标状态集合中的叶。
2. 对一系列 $k$ 分别求最优模型，写出 objective、所选 progenitors 和每个 lineage-tree 节点的 potency 标签。
3. 画出 $k$ 与 normalized discrepancy 的 Pareto curve，在拐点选择 $k^*$。
4. 根据被推断标签之间的 cellular flow 支持筛选边，形成最终 map。

第 3、4 步并未完全封装进安装后的 CLI。真实数据的归一化、Kneedle 子区间和 cellular-flow 阈值位于 TLS/LARRY notebooks，因此“运行一次命令即可重现论文最终图”并不成立。

### fastCARTA

完整候选 potency set 随终末类型数指数增长。`--progen_matrix` 路径允许先给定候选祖细胞矩阵，再解较小的 CDMP。它只支持一棵 lineage tree（`carta/carta.py:41-50`），且 `fastCarta.py` 中存在未使用路径引用未定义 `tree` 的问题。该模式是规模扩展近似/受限搜索，不能与枚举所有 potency sets 的精确搜索混为一谈。

### 论文证据怎样读

- Figure 1 用输入 lineage trees、potency-set map 和 discrepancy–complexity Pareto front 定义问题。
- Figure 2 的模拟覆盖二叉树、多叉树和 DAG；与数据生成结构一致时 CARTA-Tree 或 CARTA-DAG表现最佳，说明结构假设必须匹配。
- TLS 分析中 CARTA-DAG 提出 somite 的 convergent route，并恢复 NMP 的 neural bias；这是与 lineage 证据及既有生物学一致的解释，不是直接观测到新的祖细胞。
- LARRY 造血数据中 CARTA-Tree 与经典造血树的 Robinson–Foulds 距离更低，并用未分化细胞表达做正交验证；未恢复 CLP 也显示低采样状态会限制祖细胞推断。

### 代码—论文边界

核心 MILP 与论文公式高度对应，但完整复现是 Partial：依赖商业 Gurobi；`pyproject.toml` 与环境文件的 gurobipy 版本不一致；edge selection、归一化和真实数据 elbow 选择散落在 notebooks；fastCARTA 有边界缺陷。论文所说固定 $k$ 的最优性是在给定候选空间、约束、求解完成和时间限制允许的条件下成立，不应扩展为对真实生物分化图的唯一正确性。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CARTA summary.md

### Motivation & Novelty

#### Biological Problem

During development, cells differentiate from multipotent progenitors into specialized cell types through a series of intermediate states. Characterizing the full **cell differentiation map** — including unobserved transient progenitors — is a fundamental challenge in developmental biology. Recent CRISPR-based lineage tracing technologies (e.g., GESTALT, LARRY, the TLS system) now provide simultaneous readout of lineage trees and cell type annotations for thousands of cells, making it possible to study these maps computationally.

#### Limitations of Existing Methods

Current approaches occupy two extremes, both biologically unrealistic:

1. **Trajectory inference methods** (Monocle, *Nat. Biotechnol.* 2014; PAGA, *Genome Biol.* 2019; Slingshot, *BMC Genomics* 2018): assume all progenitor cell types are observed in the data, and infer pseudotime/branching from scRNA-seq alone. Cannot incorporate lineage tracing data or model unobserved transient progenitors.

2. **Distance-based heuristic methods**:
   - **ICE-FASE** (Fang et al., *Cell* 2022): hierarchical clustering on average cell type separation times. Always infers exactly |S|−1 progenitors (binary tree assumption). Requires timed lineage trees.
   - **EvoC** (Yang et al., *Cell* 2022): UPGMA clustering on pairwise phylogenetic distances. Same binary tree restriction, same limitation.
   - Neither can represent **convergent differentiation** (DAG structure) or polytomies.
   - Both show very high discrepancy scores on real data compared to Carta.

3. **Fitch's algorithm** (*Syst. Biol.* 1971): assigns internal nodes of a phylogeny to observed states by parsimony. Assumes all progenitor types are observed; cannot infer unobserved progenitors.

4. **PhyloVelo** (Wang et al., *Nat. Biotechnol.* 2023): infers transcriptomic velocity using lineage depth. Assumes all progenitors are observed; produces spurious reverse transitions on TLS data.

#### Unique Contributions of Carta

1. **Formal framework**: First method to pose cell differentiation map inference as a multi-objective optimization problem with a principled discrepancy score.

2. **Potency-based representation**: Unobserved progenitors are defined by which observed cell types their descendants can become — enabling inference without requiring all progenitors to be observed.

3. **DAG support**: Unlike all prior methods, Carta-DAG can infer convergent differentiation (multiple developmental paths to the same cell type).

4. **Pareto front**: Carta quantifies the complexity-discrepancy tradeoff, providing a systematic basis for selecting the optimal number of progenitors k*, rather than fixing it a priori.

5. **Optimal by construction**: For any fixed k, Carta's solution has minimum discrepancy — this is provably better than or equal to ICE-FASE/EvoC for the same k.

---

### Method Overview

Carta takes as input **m cell lineage trees** $\mathcal{T} = \{T_1, \ldots, T_m\}$ whose leaves are labeled by observed cell types $S$. It outputs a **cell differentiation map** $F_S$ — a DAG whose internal vertices are progenitor cell types (labeled by potency subsets of $S$) and whose edges represent allowed transitions.

The core algorithm:

1. **Discrepancy score** (Eq. 1-2): Count how often a cell's potency label includes a type not seen among its actual descendants. Minimize this over all compatible labelings (PLP — solved by Sankoff DP).

2. **CDMIP/CDTIP** (NP-hard): Find the progenitor set $\mathcal{P}$ with minimum discrepancy for a fixed number $k$. Solved by MILP using Gurobi. Two modes: Carta-DAG (allows any DAG) and Carta-Tree (enforces laminar family = tree-structured).

3. **Pareto front**: Solve for each k from k_min to k_max; plot normalized discrepancy $\tilde{D}$ vs. k.

4. **Optimal k* selection**: Kneedle algorithm on the flat region of the Pareto curve.

5. **Edge selection**: Cellular flow threshold (>20% of parent's outflow) to determine which edges appear in the final map.

**Key technical assumptions**: no dedifferentiation (DAG structure), maximum parsimony for labeling, sampling limitations addressed through discrepancy score design.

For details, see `doc_method.md`.

---

### Evaluation

#### Simulated Data (Figure 2)

Three simulation scenarios: binary tree maps, trees with polytomies, DAG maps. Each with |S| = 6, 10, 12, 14, 16 cell types; 50–200 cells per type; 5 replicates per parameter set (2,700 total instances).

| Scenario | Carta-Tree | Carta-DAG | ICE-FASE | EvoC |
|----------|-----------|-----------|---------|------|
| Binary tree (|S|=12) | **0.0** median Jaccard | 0.231 | 0.0 | 0.308 |
| Polytomies (|S|=12) | **0.222** | 0.333 | 0.333 | 0.462 |
| DAG (|S|=10) | 0.455 | **0.332** | 0.5 | 0.615 |

Carta-Tree matches ICE-FASE on the scenario most favorable to ICE-FASE (binary trees) but outperforms on all others. Carta-DAG is uniquely capable of recovering DAG-structured maps.

#### TLS Trunk Development (Figure 3)

- 14 cell lineage trees, 6,570 cells, 6 cell types (NMP, Neural Tube, Somite, Endoderm, Endothelial, PGCLC)
- Carta k*=7 (normalized discrepancy 0.458) vs. ICE-FASE (1.936), EvoC (2.580), Fitch (0.915), PhyloVelo (1.930 at k=6)
- **Key biological finding**: Convergent differentiation of somite cells (Figure 3d) — {endothelial, somite} progenitor suggests alternate developmental route for somite origin, consistent with previous in vivo studies of trunk endothelium
- Neural fate bias in NMPs recovered: only {NMP, neural tube} progenitor present, not {NMP, somite}
- Progenitor support: Carta C=1,306 vs. ICE-FASE C=382, EvoC C=41

#### Mouse Hematopoiesis (Figures 4–5)

- 5,864 star-shaped lineage trees (LARRY data), 49,302 cells, 9 cell types
- Carta-Tree k*=7, Robinson-Foulds distance to canonical hematopoiesis = **1** (vs. Weinreb et al. RF=4, ICE-FASE RF=6, EvoC RF=2)
- Correctly identifies: MEP (Meg+Ery progenitor), CMP (common myeloid), myeloblast, early lymphoid separation
- Carta does NOT find CLP (common lymphoid progenitor) — attributed to low sampling of lymphoid (203) and DC (113) cells
- **Orthogonal validation** (Figure 5): Carta's lineage-based progenitor assignments for undifferentiated cells agree with their transcriptional identity in gene expression space

---

### Reproducibility

**Rating: 3/5**

**Rationale**:
- Code is publicly available at https://github.com/raphael-group/CARTA under BSD 3-Clause license
- Both datasets (TLS, LARRY) are publicly available (GSE220949, AllonKleinLab GitHub)
- **Critical dependency**: Gurobi Optimizer required (commercial license; academic licenses available free). No open-source fallback. Version mismatch between `pyproject.toml` (11.0.0) and `environment.yaml` (10.0.2) could cause installation issues.
- Python 3.10.13 specifically required (`requires-python = "==3.10.13"` in pyproject)
- Cassiopeia package required (lineage tracing analysis library)
- Key analysis steps (edge selection, elbow selection, discrepancy normalization, figure generation) are in Jupyter notebooks, not the installed library — making exact reproduction require running notebooks manually
- No Snakemake pipeline for end-to-end reproduction (simulation pipeline exists in `scripts/` but requires manual coordination)

**Practical notes for reproduction**:
1. Install Gurobi (academic license from gurobi.com; must match version 11.0.0)
2. `conda env create -f environment.yaml` (note: specifies gurobipy 10.0.2; may need to update)
3. `pip install -e .` in repo root
4. For TLS analysis: download lineage trees from CARTA GitHub (`data/TLS/`)
5. For LARRY: download from AllonKleinLab paper-data repo; pre-filtering in `notebooks/larry_figures.ipynb`
6. The fastCarta mode (heuristic, used in paper for large instances) requires providing the progenitor matrix separately — use `scripts/fastCARTA.py construct_progenitors()` to generate it from observed potencies

**Simulation reproducibility**: Snakemake pipelines in `scripts/` for generating simulated data; parameters described in Methods.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
