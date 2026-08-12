---
layout: default
permalink: /paper-atlas/moscot-7f3ebb08/
title: "moscot"
nav: false
description: "moscot 解决的不是“把所有细胞排成一条确定轨迹”，而是：给定两个无法逐细胞配对的群体，寻找一个概率耦合矩阵，说明每个源细胞的概率质量应如何分配给目标细胞。时间、空间映射、空间切片对齐和时空发育都可写成这个核心问题的不同几何版本，再通过同一套 prepare → solve → push/pull API 求解和解释。"
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
      <span>Nature · 2025</span>
    </div>
    <h1>moscot</h1>
    <p>Mapping cells through time and space with moscot</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-024-08453-2" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## moscot 方法详解：用最优传输连接时间、空间与多组学快照

### 一句话理解

moscot 解决的不是“把所有细胞排成一条确定轨迹”，而是：给定两个无法逐细胞配对的群体，寻找一个概率耦合矩阵，说明每个源细胞的概率质量应如何分配给目标细胞。时间、空间映射、空间切片对齐和时空发育都可写成这个核心问题的不同几何版本，再通过同一套 `prepare → solve → push/pull` API 求解和解释。

论文题为 “Mapping cells through time and space with moscot”，发表于 *Nature* 2025，DOI `10.1038/s41586-024-08453-2`。论文中的 MOSCOT 是 “multi-omics single-cell optimal transport” 的缩写；软件包名使用小写 `moscot`。

### 为什么需要概率耦合

单细胞 RNA、ATAC 或空间测量通常会破坏细胞，因此早、晚两个时间点不是同一批细胞；解离后的单细胞参考与空间切片也没有已知的一对一对应。若源数据有 $N$ 个细胞，目标数据有 $M$ 个细胞，moscot 输出

$$
P\in\mathbb{R}_+^{N\times M}.
$$

$P_{ij}$ 不是“细胞 $i$ 必然变成细胞 $j$”，而是由模型、代价、边缘分布和正则化共同决定的匹配质量。行和列满足给定或软约束的边缘分布 $a,b$：

$$
U(a,b)=\{P\ge 0\mid P\mathbf 1_M=a,\;P^\top\mathbf 1_N=b\}.
$$

一个小例子：若早期有两个细胞，晚期有三个细胞，某一行是 $(0.05,0.35,0.10)$，它的和为 0.5，表示该源细胞持有总质量的一半，其中最多质量流向第二个晚期细胞。它仍保留多个可能后代，而不是强行给出唯一标签。

### 三种最优传输几何

#### W-type：两边共享可比特征

时间序列中的早晚细胞若都在同一个 PCA、LSI 或联合潜空间中，可直接计算跨数据集代价 $C_{ij}=c(x_i,y_j)$，求

$$
P^*=\arg\min_{P\in U(a,b)}\langle C,P\rangle-\varepsilon H(P),
$$

其中

$$
H(P)=-\sum_{ij}P_{ij}(\log P_{ij}-1).
$$

$\varepsilon$ 越大，耦合越平滑、越不确定；越小则更集中，但优化更难、也更容易受噪声影响。代码中的 `TemporalProblem.solve()` 默认 `epsilon=1e-3`、`tau_a=tau_b=1`、`rank=-1`，但这些是当前软件快照的 API 默认值，不等于论文每个实验都使用默认值。

#### GW-type：两边没有直接可比特征

若两边的特征空间不同，直接比较 $x_i$ 和 $y_j$ 没有意义。Gromov–Wasserstein（GW）转而比较各自内部结构：源侧细胞间距离 $C^X_{ii'}$ 与目标侧距离 $C^Y_{jj'}$ 是否在匹配后保持一致。概念上它最小化

$$
\sum_{ii'jj'}L(C^X_{ii'},C^Y_{jj'})P_{ij}P_{i'j'}.
$$

空间映射可用这一假设：在单细胞表达空间中相近的细胞，映到组织后也应具有相似的空间邻域关系。

#### FGW-type：共享特征与内部结构同时存在

Fused GW 把跨数据集的 W 项和数据集内部的 GW 项合并：

$$
(1-\alpha)\langle C,P\rangle+\alpha\operatorname{GW}(C^X,C^Y,P).
$$

$\alpha=1$ 是纯 GW；$\alpha\to0$ 趋近 W 项。代码后端 OTT-JAX 的参数化写成 `GW + fused_penalty × W`，所以 `alpha_to_fused_penalty()` 实际转换为

$$
\text{fused\_penalty}=\frac{1-\alpha}{\alpha}.
$$

例如 $\alpha=0.8$ 时，传给后端的 fused penalty 是 0.25，不是 0.8。这是理解论文公式与代码参数对应关系的关键。

### 时间映射：moscot.time

`TemporalProblem.prepare()` 读取 `AnnData.obs` 中的时间键，并按策略拆成子问题。默认 sequential 策略求 $(t_0,t_1),(t_1,t_2),\ldots$；也支持上三角、下三角或显式时间对。共享表示可来自 `AnnData.obsm`，未提供时可局部计算 PCA。

#### 生长和死亡如何进入边缘分布

发育过程中细胞会增殖或凋亡。如果所有源细胞都只有相同质量，模型可能把数量变化错误解释为分化。论文沿用 WOT 思路，以增殖率 $\beta(x_i)$、死亡率 $\delta(x_i)$ 和时间间隔 $\Delta t$ 调整源边缘：

$$
g_i=\exp[(\beta_i-\delta_i)\Delta t],\qquad
a_i=\frac{g_i}{\sum_jg_j}.
$$

当前源码 `birth_death.py:196-234` 正是先从 `adata.obs` 取分数，再计算 `exp((birth-death)*delta/scaling)` 并归一化。没有分数时可使用均匀边缘。

估计的生长/死亡率和样本细胞比例都可能有噪声，因此可用不平衡 OT，把硬边缘约束换成 KL 惩罚。`tau_a,tau_b` 越接近 1，边缘约束越严格；越接近 0，允许的质量偏离越多。这里“不平衡”不是数据预处理中的类别不平衡，而是允许传输质量不严格守恒。

#### 从耦合得到后代、祖先和驱动基因

给定源细胞群的归一化指示向量 $p$，前推为

$$
q=P^\top p,
$$

得到晚期每个细胞承接该群质量的程度；反向拉回则用 $Pq$ 得到祖先概率。当前源码 `BaseDiscreteSolverOutput.push()` 和 `pull()` 不必显式物化整个矩阵，也能应用传输算子。跨多个时间点时，软件按选定的时间子问题路径连续应用这些算子。

驱动基因分析是“概率分布与特征相关”：把目标群的祖先概率与早期细胞基因表达作 Pearson 或 Spearman 相关。相关高表示该基因在模型认为更可能成为目标群的祖先中富集，但仍是候选关联，不是因果证明。

### 空间映射与切片对齐

#### moscot.space.mapping

空间映射把解离的单细胞参考投到空间数据。`MappingProblem.prepare()` 同时接收单细胞表达表示、空间坐标和两边共享基因。纯 GW 只用两侧内部结构；FGW 还加入共享表达的线性项。求得耦合后，可以：

- 把单细胞细胞类型标签映到空间位置；
- 把空间平台未测量的基因或蛋白从参考数据投影到组织；
- 通过真实与预测表达的相关性评估映射。

论文把约 91,000 个小鼠肝 CITE-seq 细胞映到约 367,000 个 MERSCOPE 空间细胞，联合利用 RNA、蛋白与空间信息。图 3 中实测 `Vwf/Axin2` 定位血管结构，映射的 `Adgrg6/Gja5` 帮助识别门静脉区域，并转移 Kupffer 细胞与蛋白信息。这个案例证明的是多模态信息补全的实用性，不代表未测特征已经变成直接测量。

#### moscot.space.alignment

切片对齐比较两张空间切片的表达结构与空间结构。求得 $P$ 后，把查询切片坐标 $Z^{(r+1)}$ 投到参考坐标：

$$
\widetilde Z^{(r+1)}=P^{(r)}Z^{(r+1)}.
$$

源码提供非线性 warp 和 affine 两种模式。warp 直接使用传输加权坐标；affine 进一步拟合线性变换。序列策略可把相邻切片逐步接到参考切片，star 策略则把多个查询都对齐到一个公共坐标框架。图 3g–i 显示三张高分辨率小鼠脑冠状切片对齐前后的批次混合与 `Slc17a7` 结构一致性。

### 时空映射：moscot.spatiotemporal

`SpatioTemporalProblem` 复用时间问题的生长/死亡边缘，又复用空间对齐的 FGW 几何。每个时间对同时考虑：

- 跨时间的共享转录组距离（W 项）；
- 每个时间点内部的空间关系（GW 项）。

其 `prepare()` 把 `time_key` 作为批次策略键、`spatial_key` 作为空间结构；`solve()` 暴露 $\alpha,\varepsilon,\tau_a,\tau_b,\text{rank}$。在约 500,000 个 MOSTA 空间 bins、E9.5–E16.5 八个时间点上，论文报告时空模型的注释转移准确率平均比仅时间 moscot 高 5%，比 TOME 高 13%。这支持“加入空间结构有增益”，但增益依赖论文的注释指标、参数搜索和数据集。

论文还把心脏区域沿时间传播，并找出 `Tbx20`、`Myh7` 等心脏命运驱动候选；图 4 的驱动基因空间图显示它们与相应发育区域一致。这里仍是耦合后的相关筛选，不应把每个候选都称为已验证调控因子。

### 多组学胰腺案例与实验验证

论文新生成 E14.5、E15.5、E16.5 小鼠胰腺 paired RNA+ATAC 数据，用联合表示构建时间代价。耦合汇总为细胞类型转移矩阵并显示为 Sankey 图，再分别沿 delta 和 epsilon 谱系计算祖先概率、候选 TF 表达和 motif 活性。

计算结果把 `Neurod2` 指向 epsilon 祖细胞。作者随后在人诱导多能干细胞胰岛分化模型中用 CRISPR 干扰做实验验证：图 5h、i 显示两个 sgRNA 条件下 GHRL 阳性面积和 `GHRL` mRNA 均下降。这一层提供了 NEUROD2 影响 epsilon 形成的因果支持；而 moscot 本身负责的是候选谱系与调控因子的概率推断。

### 可扩展性来自哪里

普通 Sinkhorn 若显式保存 $N\times M$ 代价矩阵，内存是二次复杂度。moscot 调用 OTT-JAX：

1. 按批次在线计算所需的代价行，避免物化完整矩阵，使内存接近线性；
2. 用 JAX JIT 和 GPU 加速仍然近似二次时间的全秩算法；
3. 用秩 $r$ 的低秩耦合近似，把时间与内存进一步降到关于细胞数的线性量级。

源码在 `rank>-1` 时选择 `LRSinkhorn` 或 `LRGromovWasserstein`；当前快照的线性低秩 solver 设 `gamma=500`，二次低秩 solver 设 `gamma=10`。这些是软件实现默认值，不应反推为论文每项分析参数。论文胚胎图 2 使用 rank 2,000 的低秩模型：moscot 能处理每边 275,000 个细胞，而 WOT 超过 75,000 个细胞就内存不足。这里“线性可扩展”特指在线/低秩算法的复杂度性质，不表示任意配置都线性时间。

### 代码如何对应论文

| 论文概念 | 当前源码位置 | 证据边界 |
|---|---|---|
| 时间对拆分、边缘与求解参数 | `src/moscot/problems/time/_lineage.py:42-270` | Exact API；实验参数在论文复现仓 |
| 生长/死亡边缘 | `src/moscot/base/problems/birth_death.py:196-255` | Exact |
| push/pull | `src/moscot/base/output.py:114-160` | Exact |
| 空间映射 | `src/moscot/problems/space/_mapping.py:75-342` | Exact high-level wiring |
| 时空 FGW | `src/moscot/problems/spatiotemporal/_spatio_temporal.py:45-276` | Exact |
| $\alpha$ 参数转换 | `src/moscot/backends/ott/_utils.py:180-184` | Exact |
| Sinkhorn、GW 与低秩选择 | `src/moscot/backends/ott/solver.py:275-485` | Exact wrapper；数值核心来自 OTT-JAX |

本地代码快照是 `theislab/moscot` 软件仓内容，包含源码、测试和文档，但没有可验证的上游 Git 提交元数据；它是 2026 年导入 PaperCode 的本地目录，依赖声明已是 Python ≥3.10、JAX ≥0.6.1、OTT-JAX ≥0.5.0，明显可能晚于论文冻结版本。论文明确把分析复现代码放在 `theislab/moscot-framework_reproducibility`，benchmark 另在 `theislab/moscot_benchmarks`；这两个复现仓没有包含在本工作区。因此：核心方法/API 可以直接核对，论文全部图和精确预处理不能仅凭本地软件仓重跑。

### 主图阅读顺序

- 图 1：先读“实验场景/先验 → 样本 → OT 耦合 → 下游”的横向流程，再读多模态、可扩展和统一 API 三个设计目标。
- 图 2：把性能拆成三层：可运行规模、转移准确率、祖先概率与驱动基因相关；不要只看运行时间。
- 图 3：区分“参考到空间的映射”和“切片间对齐”；映射值是预测，原平台测量值才是观测。
- 图 4：对比时空、仅时间和 TOME，并看候选驱动基因在真实空间中的定位。
- 图 5：计算部分给出 delta/epsilon 分支与候选，CRISPRi 才是 NEUROD2 的实验验证。

### 假设与限制

1. 时间映射采用马尔可夫假设，只依赖当前状态；跨时间的长程记忆和真实克隆关系未被直接观测。
2. 代价空间决定“相似”的含义。PCA、LSI、联合潜空间、特征缩放和批次校正发生变化，耦合也会变化。
3. 增殖/凋亡先验来自表达分数，可能有噪声；不平衡 OT 缓解但不消除这个问题。
4. $\varepsilon$、$\tau$、$\alpha$、rank 与 cost scaling 有明确统计含义，也会改变平滑度、质量守恒、结构权重和近似误差。
5. GW/FGW 依赖结构对应假设。若表达邻域与空间邻域本来不对应，结构项会引入错误匹配。
6. 映射的基因、蛋白和标签是模型预测，不是新增实验测量；应以留出特征、已知标记和独立验证评估。
7. 低秩模型提升规模，但可能丢失罕见细胞状态。论文的 metacell 分析也显示聚合会漏掉罕见原始生殖细胞。
8. 当前工作区未保存论文分析复现仓与 benchmark 仓，也未端到端执行论文数据，因此不能声称独立复现论文数值。

### 最短实用路径

使用者可把 moscot 理解为四步：选择合适的 W/GW/FGW 几何；在 `prepare()` 中声明时间、空间、共享表示和边缘；在 `solve()` 中控制正则化、不平衡度与 rank；最后用 `push()`、`pull()`、转移矩阵、标签映射或特征相关把耦合转成生物问题。最重要的解释纪律是：耦合是依赖模型假设的概率关系，候选驱动基因是相关证据，只有独立实验才能把其中一部分推进到因果结论。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## MOSCOT: Multi-Omics Single-Cell Optimal Transport

**Publication**: Nature | January 22, 2025 | DOI: 10.1038/s41586-024-08453-2

**Authors**: Dominik Klein, Giovanni Palla, Marius Lange, Michal Klein, Zoe Piran, et al.

---

### Executive Summary

MOSCOT is a scalable optimal transport framework for mapping single cells across temporal, spatial, and multimodal dimensions. The method addresses three critical limitations of prior OT tools: (1) lack of multimodal support, (2) quadratic/cubic computational complexity preventing atlas-scale analysis, and (3) fragmented implementations across different applications.

#### Reproducibility Rating: 3.5/5 for this local workspace

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Code Availability | 4/5 | Core software source is local; paper reproduction and benchmark repositories are not local |
| Data Availability | 5/5 | All datasets publicly accessible (GEO, CNGB, Vizgen) |
| Documentation | 5/5 | Extensive tutorials, API docs, 119 test files |
| Equation-Code Mapping | 4/5 | High-level equations are wired locally; numerical solvers are delegated to OTT-JAX |
| Parameter Guidance | 4/5 | Defaults provided; some require biological intuition |

---

### Motivation and Novelty

#### Biological Problem
Single-cell genomic technologies enable multimodal profiling but destroy cells during measurement, creating disconnected snapshots across:
- **Time**: Developmental trajectories cannot be directly observed
- **Space**: Dissociation loses native tissue context
- **Modalities**: Technologies capture different molecular layers separately

> "Single-cell genomic technologies have increased our understanding of the dynamics of cellular differentiation and tissue organization. However, these experiments involve destruction of the cell and capture only a subset of molecular information." (Paper, Page 1)

#### Key Innovations

| Innovation | Description | Code Location |
|------------|-------------|---------------|
| **Multimodal Support** | Unified handling of RNA, ATAC, proteins, spatial data via shared latent spaces | `src/moscot/problems/*/` |
| **Linear Scalability** | Low-rank approximations achieve O(n) complexity | `src/moscot/backends/ott/solver.py:285-297` |
| **Unified API** | Consistent interface across temporal, spatial, spatiotemporal applications | `src/moscot/problems/` |
| **Spatiotemporal Analysis** | Novel FGW-type combining temporal trajectories with spatial organization | `src/moscot/problems/spatiotemporal/` |

---

### Method Overview

#### Core OT Framework

MOSCOT decomposes biological mapping problems into three optimal transport formulations:

| OT Type | Feature Space | Application | Mathematical Form |
|---------|---------------|-------------|-------------------|
| **W-type** (Wasserstein) | Identical features | Temporal trajectories | $\min_{P \in U(a,b)} \langle C, P \rangle - \varepsilon H(P)$ |
| **GW-type** (Gromov-Wasserstein) | Different features | Spatial alignment | $\min \sum_{ijkl} L(C^X_{ij}, C^Y_{kl}) P_{ik} P_{jl}$ |
| **FGW-type** (Fused GW) | Mixed features | Spatiotemporal | $(1-\alpha)\langle C, P \rangle + \alpha \cdot \text{GW}(P)$ |

#### Computational Pipeline

```
AnnData Input -> Problem Setup -> Cost Matrix -> OT Solver -> Transport Matrix -> Biological Analysis
     |               |               |              |               |                |
 Multimodal    TemporalProblem   Custom       Sinkhorn       Push/Pull         Growth Rates
 scRNA/spatial MappingProblem    Costs       Low-rank       Operations        Trajectories
               FGWProblem                    GPU/JAX                          Driver Genes
```

---

### Benchmark Results

#### Scale Achievements

| Application | Dataset | Scale | Comparison |
|-------------|---------|-------|------------|
| Temporal | Mouse embryogenesis | 1.7M cells, 20 timepoints | WOT: 75K cell limit |
| Spatial Mapping | Liver CITE-seq + MERSCOPE | 91K + 367K locations | Tangram/gimVI infeasible |
| Spatiotemporal | MOSTA atlas | 500K locations, 8 timepoints | 13% improvement over TOME |

#### Performance Metrics

**Temporal Analysis (vs. WOT, TOME)**:
- **20x scalability improvement**: 1.7M cells vs. 75K limit
- **Better biological realism**: <10% vs. 19% predicted apoptosis
- **Superior driver gene correlations**: Higher Spearman's correlations with known markers

**Spatial Mapping (vs. Tangram, gimVI)**:
- Outperformed across 14 benchmark datasets using held-out gene correlation
- Positive correlation with spatial correspondence

#### Experimental Validation

**NEUROD2 as Epsilon Cell Regulator**:
> "The differentiation of NEUROD2 knockout (KO) iPS cells to stem-cell-derived islets resulted in a significant decrease in the number of ghrelin-expressing cells and reduced levels of GHRL mRNA." (Paper, Page 7)

- Computational prediction experimentally validated in human iPSCs
- n=4 independent experiments with ANOVA statistical testing

---

### Code-Paper Equation Mapping

| Paper Equation | Description | Code Implementation |
|----------------|-------------|---------------------|
| Eq. 1 | Feasible coupling set $U(a,b)$ | `src/moscot/backends/ott/solver.py:341` (LinearProblem) |
| Eq. 2 | Kantorovich problem | `src/moscot/backends/ott/solver.py:299-342` |
| Eq. 3 | Entropic regularization | OTT-JAX `sinkhorn.Sinkhorn` |
| Eq. 6 | Sinkhorn iterations | OTT-JAX `ott.solvers.linear.sinkhorn` |
| Eq. 7 | Growth rate marginals | `src/moscot/base/problems/birth_death.py:222-228` |
| Eq. 9 | Unbalanced KL relaxation | `tau_a`, `tau_b` parameters in solver |
| Eq. 14 | GW quadratic objective | `src/moscot/backends/ott/solver.py:483-485` |
| Eq. 15 | FGW combined objective | `alpha_to_fused_penalty()` at `_utils.py:180-184` |
| Eq. 16 | Gene imputation $\tilde{Y} = P^T X$ | `src/moscot/base/output.py:114-136` (push) |

---

### Critical Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Python | >=3.10 | Runtime |
| JAX | >=0.6.1 | GPU acceleration, JIT compilation |
| OTT-JAX | >=0.5.0 | Core OT algorithms |
| anndata | >=0.9.1 | Single-cell data structures |
| scanpy | >=1.9.3 | Preprocessing workflows |
| mudata | >=0.2.2 | Multimodal data handling |

---

### Limitations and Considerations

#### Technical Limitations
1. **Memory requirements**: Atlas-scale datasets require high-memory GPUs or significant CPU RAM
2. **OTT-JAX dependency**: Core algorithms in external package (version sensitivity)
3. **Parameter sensitivity**: Epsilon, tau, alpha require biological intuition

#### Hidden Implementation Details
1. **Alpha conversion**: Paper's $\alpha$ converts to `fused_penalty = (1-alpha)/alpha` for OTT-JAX
2. **Geodesic costs**: Graph-based costs use heat kernel diffusion with `t = epsilon/4.0`
3. **Low-rank defaults**: `gamma=500` for linear, `gamma=10` for quadratic problems
4. **Marginal scaling**: Growth rates normalized by population size for biological interpretation

---

### Key Takeaways

1. **Scale Breakthrough**: First OT method enabling atlas-scale analysis (>1M cells)
2. **Biological Validation**: Computational predictions experimentally confirmed
3. **Unified Framework**: Consistent API across temporal, spatial, multimodal applications
4. **Foundation Technology**: Establishes OT as core methodology for single-cell analysis

> "Given the widespread need to align cellular measurements in single-cell genomics, we anticipate that moscot will accelerate and simplify the analyses of large-scale multimodal datasets." (Paper, Page 10)

---

### Quick Start

```python
import moscot as mt

# Temporal trajectory inference
tp = mt.problems.time.TemporalProblem(adata)
tp.prepare(time_key="day")
tp.solve(epsilon=1e-2, tau_a=0.9, tau_b=0.99)
trajectories = tp.push(source=0, target=1)

# Spatial mapping
mp = mt.problems.space.MappingProblem(adata_sc, adata_spatial)
mp.prepare(spatial_key="spatial", alpha=0.5)
mp.solve()
protein_map = mp.push(data="protein")
```

---

### Resources

- **Documentation**: https://moscot-tools.org
- **Source Code**: https://github.com/theislab/moscot
- **Reproducibility**: https://github.com/theislab/moscot-framework_reproducibility
- **scverse Integration**: Native AnnData/MuData support

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
