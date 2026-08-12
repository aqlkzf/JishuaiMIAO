---
layout: default
permalink: /paper-atlas/genes2genes-61a0514a/
title: "Genes2Genes"
nav: false
description: "Genes2Genes 把每个基因在两条单细胞轨迹上的动态看成两条带不确定性的序列：先用局部高斯分布表达不确定性，再用 MML 决定哪些时间点值得匹配，最后用五状态动态规划把“一致、快慢不同和真正失配”编码成可解释的字符串。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Genes2Genes</h1>
    <p>Gene-level alignment of single-cell trajectories</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Genes2Genes 方法详解：从单细胞轨迹到基因级时序对齐

### 1. 方法要解决什么问题

单细胞轨迹分析通常先给每个细胞一个伪时间 (t\in[0,1])，再观察基因表达如何随伪时间变化。真正困难的是比较两条轨迹：它们的细胞数、采样密度和发育速度可能不同，同一个基因也可能出现提前、延后、局部一致或局部完全不同的动态。

Genes2Genes（G2G）不强求细胞一一对应，也不只比较轨迹起点和终点。它对每个共有基因回答三个更细的问题：

1. 哪些伪时间区间的表达分布相容？
2. 相同表达程序是否在一条轨迹中更快或更慢？
3. 哪些区间只存在于其中一条轨迹，构成真正的局部失配？

其最终输出不是单一相似度，而是一条由 `M/V/W/I/D` 组成的对齐字符串。因此，研究者既能得到整体相似程度，也能定位差异发生的时段。

### 2. 输入、输出与基本假设

#### 输入

- 两个经过归一化和 `log1p` 变换的单细胞表达数据集；
- 每个细胞的一维伪时间；
- 两个数据集共有的待分析基因列表；
- 插值时间点数量、核窗口、状态转移参数等超参数。

代码支持 AnnData 或矩阵接口。AnnData 路径从 `.X` 读取表达矩阵，从 `.var_names` 读取基因名，并固定从 `.obs['time']` 读取伪时间（`Genes2Genes/genes2genes/Main.py:201-256`）。

#### 输出

对每个基因 (g)，G2G 输出：

- 参考轨迹和查询轨迹的插值表达分布；
- 最优对齐总代价；
- `M/V/W/I/D` 状态字符串；
- 对齐路径和局部匹配位置；
- 可用于可视化、聚类和聚合的 alignment landscape。

多个基因的状态字符串还能进一步生成编辑距离矩阵、基因簇、共识对齐路径和跨基因匹配计数矩阵。

#### 核心假设

- 上游伪时间能大致反映真实进程顺序；
- 每条轨迹可用一维、近似线性的进程表示；
- 局部基因表达分布可由高斯分布近似；
- 两个数据集的预处理尺度具有可比性；
- 时序关系可由五种状态及其转移先验表达。

### 3. 整体计算框架

```text
两个表达矩阵 + 两组伪时间 + 共有基因
                    │
                    ▼
        构造人工伪时间点 / 最优分箱
                    │
                    ▼
     对每个基因做高斯核“分布式插值”
                    │
                    ▼
 比较共享高斯模型与独立高斯模型的 MML 码长
                    │
                    ▼
      构造每对时间点的局部匹配代价矩阵
                    │
                    ▼
    五状态动态规划：M、V、W、I、D
                    │
                    ▼
       回溯得到最优路径与状态字符串
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   局部差异解释   基因字符串聚类   多基因共识对齐
```

代码中的主调用链与此一致：

```text
Main.RefQueryAligner
  -> run_interpolation
  -> TimeSeriesPreprocessor.prepare_interpolated_gene_expression_series
  -> OrgAlign.DP5.run_optimal_alignment
  -> OrgAlign.DP5.compute_cell
  -> OrgAlign.DP5.backtrack
  -> ClusterUtils.run_clustering / get_cluster_average_alignments
```

### 4. 第一步：把不规则细胞采样变成局部表达分布

#### 4.1 为什么不能只插值均值

两条轨迹在同一伪时间附近可能具有相近均值，却有完全不同的细胞间异质性。只拟合一条平均曲线会丢掉这部分信息。G2G 因而在每个人工时间点估计一个局部高斯分布，同时保留均值和标准差。

设细胞 (c) 的伪时间为 (p_c)，表达量为 (x_c)，人工时间点为 (\tau)。高斯核权重为

\[
w_c(\tau)=\exp\left[-\frac{(p_c-\tau)^2}{h^2}\right],
\]

其中论文使用的默认窗口为 (h=0.1)。局部加权均值为

\[
\mu(\tau)=\frac{\sum_c w_c(\tau)x_c}{\sum_c w_c(\tau)}.
\]

代码同时估计加权标准差 (\sigma(\tau))，然后在每个人工时间点采样 50 个表达值：

\[
x^{(k)}(\tau)\sim\mathcal N\!\left(\mu(\tau),\sigma^2(\tau)\right),
\qquad k=1,\ldots,50.
\]

论文在 `paper.md:265-283` 描述了核函数、局部均值/标准差、50 次采样和插值复杂度；实现位于 `TimeSeriesPreprocessor.py:109-169,180-214`。代码固定 `torch.manual_seed(1)`，有利于复现人工采样。

#### 4.2 人工时间点与最优分箱

默认模式在观测伪时间范围内生成等间隔点。可选的最优分箱模式调用 `ContinuousOptimalBinning` 决定切分点（`TimeSeriesPreprocessor.py:172-177`）。论文分析 notebook 会显式开启该模式并把分割点写入 aligner。

#### 4.3 极低表达基因

若局部方差为 0 或不可计算，高斯编码会不稳定。论文说明了极端零表达情况下的方差替代策略（`paper.md:285-290`）。v0.1.0 代码实现得更具体：它根据非零计数进入不同分支，并对退化分布使用 `0.01` 的标准差下限（`Main.py:315-511`; `TimeSeriesPreprocessor.py:144-150`）。

因此，这部分属于 **Partial**：论文与代码目标一致，但代码含有更细的经验阈值，精确复现时必须保留。

### 5. 第二步：用最小消息长度判断两个局部分布是否匹配

#### 5.1 MML 的直觉

最小消息长度（minimum message length, MML）把模型选择写成“传输模型和数据需要多少信息”。

\[
I(H,D)=I(H)+I(D\mid H).
\]

如果两个局部表达样本可以由同一个高斯模型解释，那么“共享模型”的总码长应当相对较短；如果它们差异很大，分别编码会更经济。

#### 5.2 两个假设

对参考轨迹时间点 (j) 的样本 (D^S_j) 和查询轨迹时间点 (i) 的样本 (D^T_i)，比较：

- **共享假设**：两组样本使用同一个局部高斯模型编码；
- **独立假设**：每组样本使用自己的高斯模型编码。

为了避免固定以某一轨迹为共享模型，代码计算两个方向并取平均：先用参考模型编码两组数据，再用查询模型编码两组数据。

独立模型码长可写为

\[
I_{\mathrm{ind}}(i,j)=
I(\theta^S_j)+I(D^S_j\mid\theta^S_j)
+I(\theta^T_i)+I(D^T_i\mid\theta^T_i).
\]

局部匹配代价定义为

\[
C(i,j)=I_{\mathrm{shared}}(i,j)-I_{\mathrm{ind}}(i,j).
\]

两组分布越相容，共享编码相对越有利，(C(i,j)) 越低；分布差异越明显，代价越高。

论文在 `paper.md:323-449` 给出共享/独立假设以及 Wallace–Freeman 高斯编码；代码 `OrgAlign.py:537-568` 直接计算两个方向的共享码长、独立 null 码长及其差值。这一核心模块属于 **Exact**。

### 6. 第三步：五状态序列对齐

#### 6.1 五种状态的含义

| 状态 | 网格移动 | 生物学/时序解释 |
|---|---|---|
| `M` | 对角移动 | 两条轨迹各前进一步，局部一对一匹配。 |
| `V` | 查询方向前进、参考位置保持 | 查询轨迹在该局部被拉伸，可表示相对速度或滞后。 |
| `W` | 参考方向前进、查询位置保持 | 参考轨迹在该局部被拉伸。 |
| `I` | 查询方向前进 | 查询轨迹存在参考轨迹无法匹配的区间。 |
| `D` | 参考方向前进 | 参考轨迹存在查询轨迹无法匹配的区间。 |

`V/W` 与 `I/D` 虽然都可能使用水平或垂直移动，但意义不同：前者仍属于连续的时序对应，只是局部进度不同；后者表示真正的未匹配区间。

#### 6.2 状态转移代价

状态机把转移概率转换为信息代价：

\[
T_{X\rightarrow Y}=-\log_2 P(Y\mid X).
\]

论文使用的自由参数为

\[
[P(M\mid M),P(I\mid I),P(M\mid I)]
=[0.99,0.1,0.7],
\]

并通过对称关系补全相关转移（`paper.md:452-455`）。`OrgAlign.py:26-133` 实现了完整五状态机，论文 notebook 也设置相同的 `aligner.state_params`，因此属于 **Exact**。

### 7. 第四步：五矩阵动态规划

G2G 为每个状态维护一个动态规划矩阵：

\[
F_M,F_V,F_W,F_I,F_D.
\]

以匹配状态为例：

\[
F_M(i,j)=C(i,j)+
\min_{X\in\{M,V,W,I,D\}}
\left[F_X(i-1,j-1)+T_{X\rightarrow M}\right].
\]

其余状态采用相应的水平或垂直前驱坐标，并加上状态转移信息代价。实现中 `I/D` 的局部 emission cost 为 0，其惩罚主要来自状态转移码长（`OrgAlign.py:537-568`）。

总体目标可以概括为

\[
\pi_g^*=\arg\min_{\pi}
\left[
\sum_{(i,j)\in\pi}C_{x_{ij}}(i,j)
+\sum_k T_{x_{k-1}\rightarrow x_k}
\right].
\]

终点处在五个矩阵中选择最小总代价，再沿保存的前驱指针回溯，生成状态字符串。论文递推式位于 `paper.md:461-518`；代码矩阵、递推和回溯分别位于 `OrgAlign.py:242-280,381-532,652-723`，属于 **Exact**。

若两条插值轨迹长度为 (n,m)，单基因动态规划的时间和空间复杂度均为 (O(nm))，常数因子包括五个状态矩阵。不同基因彼此独立，`Main.align_all_pairs` 使用多进程并行（`Main.py:566-575`）。

### 8. 如何从状态字符串得到下游结论

#### 8.1 局部解释

状态字符串保留了差异发生的位置。例如：

- 大段 `M`：两条轨迹局部高度一致；
- 连续 `V/W`：共同程序存在，但进度不同；
- 连续 `I/D`：某一轨迹出现另一条轨迹无法解释的动态。

这比一个全局相关系数更有信息，因为同一基因可以前期匹配、后期失配。

#### 8.2 基因聚类

两个基因的对齐模式通过标准化 Levenshtein 距离比较：

\[
d(g_a,g_b)=
\frac{\operatorname{Lev}(a_a,a_b)}{\max(|a_a|,|a_b|)}.
\]

随后对预计算距离矩阵进行凝聚层次聚类，并可用 silhouette score 辅助选择阈值（`ClusterUtils.py:19-64,96-156`）。该模块与论文 `paper.md:524-555` 一致，属于 **Exact**。

#### 8.3 多基因共识对齐

对于一个基因集合，代码在 alignment landscape 的当前位置统计五种状态频率，选择出现最多的状态继续回溯，得到共识路径；同时统计每对参考/查询时间点被多少基因判定为匹配（`ClusterUtils.py:461-541`）。低相似度基因或基因簇可继续做通路富集分析。

### 9. 论文实验说明了什么

#### 模拟数据

论文构造 3,500 对基因轨迹，覆盖七种动态模式和 15 个时间点。G2G 报告的分类准确率为 98.2%–100%；在阈值 0.22 下得到 15 个簇，误聚类率 0.1%。无共享过程的负对照被全部判为失配（`paper.md:94-119`）。

这部分说明五状态字符串能够在已知真值下区分“速度不同”和“过程不同”。

#### PAM 与 LPS 巨噬细胞反应

G2G 找到共同核心反应、峰值反应以及刺激特异的早期/晚期差异。TNF 的端点 log fold change 很小、Wilcoxon (P=0.2)，但轨迹对齐相似度较低（`paper.md:126-145`），说明端点统计可能遗漏时序差异。

#### 健康肺与 IPF

健康 AT2→AT1 与 IPF AT2→异常 basal-like 进程比较包含 994 个高变基因和 13 个时间点，平均相似度约 62%，失配主要集中于后期；低相似度基因富集上皮–间质转化（`paper.md:151-166`）。

#### 体内与 ATO T 细胞发育

1,371 个转录因子、14 个时间点的比较得到约 66% 平均相似度，早期差异涉及多能性，晚期差异涉及 TNF 通路。TNF 处理使 ATO 细胞与体内状态的潜空间距离下降约 5%（`paper.md:169-213`）。论文把它定位为概念验证，而不是完整的功能救援证明。

### 10. 论文与代码的一致性

| 模块 | 结论 | 主要证据 |
|---|---|---|
| 分布式插值 | **Exact** | `TimeSeriesPreprocessor.py:109-214` |
| MML 共享/独立模型代价 | **Exact** | `OrgAlign.py:537-568` |
| 五状态机 | **Exact** | `OrgAlign.py:26-133` |
| 五矩阵动态规划与回溯 | **Exact** | `OrgAlign.py:242-280,381-532,652-723` |
| 字符串距离与聚类 | **Exact** | `ClusterUtils.py:19-156` |
| 多基因聚合 | **Exact** | `ClusterUtils.py:461-541` |
| 低表达极端情况 | **Partial** | 代码比论文描述包含更多阈值与方差下限。 |
| 公共 API 参数设置 | **Partial** | 多个关键属性依赖 notebook 动态赋值。 |
| 四组论文分析 | **Notebook** | `G2G_notebooks/` 提供模拟、PAM/LPS、IPF、T-cell/ATO 工作流。 |
| 自动化测试 | **Not found** | v0.1.0 快照没有测试文件。 |

总体判断为：**核心方法实现忠实度高，工程接口完整度中等。**

### 11. 复现时最容易踩的坑

1. **不能只初始化对象就直接运行。** 论文 notebook 会显式设置：

   ```python
   aligner.WEIGHT_BY_CELL_DENSITY = True
   aligner.WINDOW_SIZE = 0.1
   aligner.state_params = [0.99, 0.1, 0.7]
   aligner.optimal_binning = True
   ```

2. **`align_single_pair` 的形参具有误导性。** 方法签名包含 `state_params=...`，但内部实际传给 `DP5` 的是 `self.state_params`（`Main.py:522-538`）。因此必须设置对象属性。
3. **输入不会自动完成论文全部预处理。** 表达归一化、`log1p`、共有基因选择和伪时间推断应在上游完成。
4. **低表达规则会影响数值。** 不能在复现时随意删除 `0.01` 方差下限或非零计数分支。
5. **版本必须区分。** 论文分析使用 v0.1.0；论文提到的 v0.2.0 加速结果不应直接归于本工作区检查的代码。
6. **缺少测试。** 建议先以少量基因运行串行版本，再检查插值分布、状态字符串和路径，最后启用多进程。

### 12. 方法的边界

- 伪时间错误会直接传递到局部匹配结果；
- 细胞密度不足会降低局部分布估计质量；
- 高斯平滑假设可能模糊突变式表达变化；
- 当前算法只比较两条近似线性轨迹，不能直接处理分支、环或多条件联合对齐；
- `I/D` 失配说明动态无法对齐，但不等于已经找到因果调控机制；
- 窗口、时间点数、状态概率和聚类阈值都会改变结果分辨率。

论文在 `paper.md:219-231` 明确讨论了伪时间质量、细胞密度、平滑轨迹和“两条线性轨迹”限制。

### 13. 一句话理解

Genes2Genes 把每个基因在两条单细胞轨迹上的动态看成两条带不确定性的序列：先用局部高斯分布表达不确定性，再用 MML 决定哪些时间点值得匹配，最后用五状态动态规划把“一致、快慢不同和真正失配”编码成可解释的字符串。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Gene-level alignment of single-cell trajectories

### Paper

- **Method:** Genes2Genes (G2G)
- **DOI:** `10.1038/s41592-024-02378-4`
- **Venue/year:** *Nature Methods*, 2025
- **Task:** align gene-expression dynamics between two single-cell pseudotime trajectories and localize matched, stretched and trajectory-specific regions.

### Core idea

Genes2Genes treats trajectory comparison as sequence alignment at gene level. For each shared gene, it first interpolates a Gaussian expression distribution at artificial pseudotime points. It then uses minimum message length (MML) to score whether a reference/query pair of local distributions is better explained by a shared Gaussian model or by independent models. A five-state dynamic program finds the lowest-message-length path:

- `M`: one-to-one match;
- `V` and `W`: local temporal stretching in either trajectory; and
- `I` and `D`: unmatched query or reference regions.

Backtracking produces an interpretable state string per gene. Normalized Levenshtein distance between these strings supports gene clustering, and gene-level paths can be aggregated into a consensus trajectory alignment.

### Method in one view

```text
expression + pseudotime
  → distributional Gaussian-kernel interpolation
  → shared-vs-independent MML cost matrix
  → five-state dynamic programming
  → per-gene alignment string and local similarity
  → gene modules, aggregate paths and pathway analysis
```

The local match cost is the difference between shared-model and independent-model coding lengths:

\[
C(i,j)=I_{\mathrm{shared}}(D^S_j,D^T_i)-I_{\mathrm{independent}}(D^S_j,D^T_i).
\]

Lower cost indicates that the two local distributions can be compressed economically under a shared explanation.

### Main findings

- In 3,500 simulated pairs spanning seven temporal patterns, G2G reports 98.2–100% pattern-classification accuracy. Alignment-string clustering yields 15 clusters with 0.1% misclustering at the reported threshold.
- In PAM versus LPS macrophage responses, G2G recovers shared response modules and localized stimulus-specific dynamics. TNF shows low temporal alignment similarity despite weak endpoint differential-expression evidence.
- In healthy versus idiopathic pulmonary fibrosis epithelial progression, 994 highly variable genes have about 62% mean similarity, with divergence concentrated late and low-similarity genes enriched for epithelial–mesenchymal transition.
- In vivo versus artificial-thymic-organoid T-cell development shows about 66% mean similarity across 1,371 transcription factors, with early pluripotency and late TNF-pathway mismatch. TNF treatment shifts ATO cells modestly toward the in vivo state, presented as proof of concept.

### Relation to prior methods

CellAlign (*Nature Methods*, 2018) aligns mean expression trends but does not explicitly retain local expression distributions or distinguish the full five-state vocabulary. TrAGEDy (bioRxiv preprint, 2024, as cited by the paper) compares trajectory gene expression but performs less consistently on several simulated timing/mismatch patterns in the reported benchmark. Genes2Genes' main contribution is the combination of distributional interpolation, information-theoretic scoring and biologically interpretable state strings.

### Paper–code assessment

**Core fidelity: high.** The paper-used `Teichlab/Genes2Genes` v0.1.0 tag contains the distributional interpolation, symmetric MML cost, five-state transition model, five-matrix DP, backtracking, alignment-string clustering and aggregate alignment. The separate `G2G_notebooks` repository contains the manuscript analyses and paper parameter settings.

Important caveats:

- several attributes must be assigned directly by notebooks before execution;
- `align_single_pair` declares a `state_params` argument but uses `self.state_params` internally;
- low-expression handling contains implementation-specific thresholds and a variance floor;
- the package snapshot has no automated tests; and
- the package README references a tutorial notebook absent from the acquired v0.1.0 tag.

The paper also mentions faster v0.2.0 runtime, but this workspace evaluates the v0.1.0 code identified by the manuscript notebooks.

### Reproducibility

**Rating: 4/5.** The paper, figures, supplementary information, paper-used package version, manuscript notebooks, code commit identifiers and parameters are available. Reproduction remains sensitive to an older scientific-Python environment, notebook-side object configuration, pseudotime preprocessing and numerical edge-case behavior.

### Limitations

- Alignment quality depends on upstream pseudotime and cell-density coverage.
- Gaussian interpolation favors smooth local dynamics and may obscure abrupt changes.
- The current formulation aligns two one-dimensional, approximately linear trajectories; it does not directly solve branching, cyclic or multi-condition alignment.
- State strings describe temporal correspondence but do not prove regulatory causality.
- Window size, grid/binning, transition probabilities and clustering thresholds affect resolution.

### Bottom line

Genes2Genes is a well-matched paper-and-code method for turning two single-cell trajectories into gene-specific temporal alignments. Its chief value is interpretability: it separates timing changes from genuine unmatched regions and carries that structure into clustering, pathway analysis and hypothesis generation. The implementation is substantively faithful to the paper, but reliable reuse requires following the manuscript notebooks' configuration rather than relying on constructor defaults alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
