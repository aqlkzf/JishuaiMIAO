---
layout: default
permalink: /paper-atlas/celldancer-ba49c10b/
title: "cellDancer"
nav: false
wide: true
description: "cellDancer 是一个“relay velocity model”：对每个基因单独训练一个 DNN，输入某个细胞的未剪接/已剪接表达量，输出该细胞的 \\alpha,\\beta,\\gamma；再用 RNA 动力学方程预测下一时刻的表达状态；最后让这个预测位移尽可能指向局部邻居中最像“未来状态”的细胞。 可以理解为："
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
      <span>Nature Biotechnology · 2024</span>
    </div>
    <h1>cellDancer</h1>
    <p>A relay velocity model infers cell-dependent RNA velocity</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/GuangyuWangLab2021/cellDancer" target="_blank" rel="noopener noreferrer" aria-label="Open code for cellDancer">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## cellDancer 方法中文解读

### 1. 这篇论文要解决什么问题？

RNA velocity 的目标是从单细胞 RNA 测序里同时观测到的未剪接 mRNA（unspliced）和已剪接 mRNA（spliced），推断细胞状态接下来会往哪里走。经典模型通常假设同一个实验中的细胞共享相似的转录、剪接、降解动力学参数。但在真实发育过程中，细胞可能同时经历多阶段、多分支命运转变，不同细胞群或不同分支的动力学参数并不相同。论文指出，这会导致已有方法在“转录增强”基因和“分支基因”上出现方向错误（`paper.md:12`, `21-24`）。

cellDancer 的核心想法是：不要为全体细胞拟合一套全局速率，而是为每个基因、每个细胞估计自己的转录速率 $\alpha$、剪接速率 $\beta$、降解速率 $\gamma$，并利用局部邻居来训练这些速率（`paper.md:24-35`, `41-50`）。

### 2. cellDancer 的一句话概括

cellDancer 是一个“relay velocity model”：对每个基因单独训练一个 DNN，输入某个细胞的未剪接/已剪接表达量，输出该细胞的 $\alpha,\beta,\gamma$；再用 RNA 动力学方程预测下一时刻的表达状态；最后让这个预测位移尽可能指向局部邻居中最像“未来状态”的细胞（`paper.md:204-256`）。

可以理解为：

```text
每个基因单独训练
        |
输入：每个细胞的 unspliced u 和 spliced s
        |
DNN 输出：该细胞的 alpha/beta/gamma
        |
离散化 ODE 预测下一步 u(t+Δt), s(t+Δt)
        |
和邻居细胞的真实位移比较
        |
最小化 1 - 最大余弦相似度
        |
得到单细胞分辨率 RNA velocity 和 kinetic rates
```

### 3. 基础动力学方程

论文从单个基因的一阶动力学方程开始（`paper.md:188-201`）：

$$
\frac&#123;&#123;{\mathrm{d}}u\left( t \right)}}&#123;&#123;\mathrm{d}t}} = \alpha \left( t \right) - \beta \left( t \right)u\left( t \right)
$$

(1)

$$
\frac&#123;&#123;{\mathrm{d}}s\left( t \right)}}&#123;&#123;\mathrm{d}t}} = \beta \left( t \right)u\left( t \right) - \gamma \left( t \right)s\left( t \right)
$$

(2)

这里：

- $u(t)$：未成熟/未剪接 mRNA；
- $s(t)$：成熟/已剪接 mRNA；
- $\alpha(t)$：转录速率；
- $\beta(t)$：剪接速率；
- $\gamma(t)$：降解速率。

传统模型常把这些速率设成常数、二值或全局共享参数；cellDancer 则把它们建模成依赖细胞状态的函数。

### 4. DNN 如何学习 cell-specific rates？

对基因 $i$，论文定义 DNN 映射（`paper.md:204-212`）：

$$
\left( {\alpha ^i(t),\beta ^i(t),\gamma ^i(t)} \right)^&#123;&#123;{\mathrm{T}}}} = &#123;&#123;\Phi }}_{\theta ^i}\left( {u^i\left( t \right),s^i\left( t \right)} \right)
$$

(3)

含义是：给定某个细胞中该基因的未剪接表达 $u^i(t)$ 和已剪接表达 $s^i(t)$，DNN $\Phi_{\theta^i}$ 输出该细胞的三个速率。

代码中核心实现是 `src/celldancer/velocity_estimation.py`：

- `DNN_layer` 定义网络结构，实际代码为 `Linear(2,h1) -> Linear(h1,h2) -> Linear(h2,3)`，训练时 `h1=h2=100`（`velocity_estimation.py:37-41`, `535-557`）。
- `forward()` 把 `unsplice` 和 `splice` 合成二维输入，并经 sigmoid 输出三个通道（`velocity_estimation.py:43-51`）。
- 代码随后把 sigmoid 输出乘以 `alpha0`, `beta0`, `gamma0`，得到最终报告的 $\alpha,\beta,\gamma$（`velocity_estimation.py:51-57`）。

**需要注意的差异：**论文文字说输入层有 $2n$ 个节点、输出层有 $3n$ 个节点（`paper.md:254`），但代码是对细胞行应用 `2 -> 100 -> 100 -> 3` 的映射。核心功能是一致的：都为每个细胞输出 $\alpha,\beta,\gamma$；但张量结构和论文表述并不完全相同。因此这属于 `Partial` 的纸码匹配。

### 5. 如何从 rates 预测未来状态？

论文把 ODE 离散化（`paper.md:215-228`）：

$$
\frac&#123;&#123;u\left( {t + \Delta t} \right) - u\left( t \right)}}&#123;&#123;\Delta t}} = \alpha \left( {u\left( t \right),s\left( t \right)} \right) - \beta \left( {u\left( t \right),s\left( t \right)} \right)u\left( t \right),
$$

(4)

$$
\frac&#123;&#123;s\left( {t + \Delta t} \right) - s\left( t \right)}}&#123;&#123;\Delta t}} = \beta \left( {u\left( t \right),s\left( t \right)} \right)u\left( t \right) - \gamma \left( {u\left( t \right),s\left( t \right)} \right)s\left( t \right),
$$

(5)

代码中对应为（`velocity_estimation.py:58-62`）：

- `unsplice_predict = unsplice + (alphas - beta*unsplice)*dt`
- `splice_predict = splice + (beta*unsplice - gamma*splice)*dt`

论文在模型参数中给出 $\Delta t=0.5$（`paper.md:333`），代码公开 API `velocity()` 的默认值也是 `dt=0.5`（`velocity_estimation.py:690-703`）。

### 6. 损失函数：为什么叫“relay velocity”？

cellDancer 不要求知道真实时间点，而是假设细胞的未来状态能在局部邻居中找到近似对应。对每个细胞 $j$，DNN 预测一个未来位移向量 $v_j$；同时，从该细胞指向邻居细胞 $j'$ 的实际表达差异构成观测位移 $v_j^\prime$。训练目标是让预测位移与某个邻居位移的方向尽可能一致（`paper.md:228-251`）。

总损失为：

$$
&#123;&#123;{\mathcal{L}}}} = \mathop {\sum}\limits_{j = 1}^n &#123;&#123;&#123;&#123;\mathcal{L}}}}_j}
$$

(6)

单细胞损失为：

$$
&#123;&#123;{\mathcal{L}}}}_j = 1 - \mathop &#123;&#123;\max }}\limits_{\{\, j^\prime \} } \frac&#123;&#123;v_j \cdot v_j^\prime }}&#123;&#123;\left| {v_j} \right| \ast \left| {v_j^\prime } \right|}}
$$

(7)

其中：

$$
v_j = \left( {u\left( {t_j + \Delta t} \right) - u\left( {t_j} \right),s\left( {t_j + \Delta t} \right) - s\left( {t_j} \right)} \right)
$$

(8)

$$
v_j^\prime = \left( {u\left( {t_{j^\prime }} \right) - u\left( {t_j} \right),s\left( {t_{j\prime }} \right) - s\left( {t_j} \right)} \right)
$$

(9)

代码中 `velocity_calculate()` 先用 `NearestNeighbors` 找邻居，再计算预测位移和邻居位移，最后返回 `1 - cosine_max`（`velocity_estimation.py:88-145`）。默认公开 API 使用 `loss_func='cosine'`，并把每个细胞的损失取平均（`velocity_estimation.py:235-239`, `690-703`）。

直观理解：

- 如果预测箭头正好指向某个合理的邻居，余弦相似度高，损失低；
- 如果预测方向和局部邻居方向相反，损失高；
- 每个细胞只需要找到“最像未来状态”的邻居，不需要全局统一时间轴。

这就是 relay：局部速度一个接一个“接力”，形成整体细胞状态转移方向。

### 7. 训练、优化和默认参数

论文说明 DNN 使用 Adam，学习率 0.001，weight decay 0.004，patience 为 3，若 3 个 checkpoint 内损失不下降则停止；所有案例中 $\Delta t=0.5$（`paper.md:254`, `333`）。

代码验证如下：

- Adam + weight decay 0.004：`velocity_estimation.py:335-340`；
- early stopping：`EarlyStopping(monitor="loss", patience=patience)`，并用 `check_val_every_n_epoch` 控制 checkpoint 间隔（`velocity_estimation.py:588-608`）；
- `velocity()` 默认参数：`max_epoches=200`, `check_val_every_n_epoch=10`, `patience=3`, `learning_rate=0.001`, `dt=0.5`, `n_neighbors=30`, `permutation_ratio=0.125`, `loss_func='cosine'`（`velocity_estimation.py:690-703`）。

代码还实现了每个 epoch 对细胞进行随机抽样：当 `0 < permutation_ratio < 1` 时，使用 `data_fitting.sample(frac=self.permutation_ratio)`（`velocity_estimation.py:481-485`）。

### 8. 从基因速度到细胞嵌入空间 velocity

每个基因都能得到一个速度，但实际可视化和 pseudotime 通常需要把多基因速度投影到 UMAP/t-SNE/PCA 等低维空间。论文采用类似 velocyto/scVelo 的思想：如果细胞 $j$ 的 velocity 与从 $j$ 到 $j'$ 的表达差异方向相关性越高，则 $j$ 越可能转移到 $j'$（`paper.md:269-296`）。

论文定义转移概率：

$$
P_{jj^\prime } \propto e^{\frac&#123;&#123;corr\left( {v_j,\delta _{jj^\prime }} \right)}}{\sigma }}
$$

(10)

并归一化：

$$
\mathop {\sum}\nolimits_{j^\prime \in N} {P_{jj^{\prime} }} = 1
$$

(11)

低维 velocity：

$$
\tilde v_j = \mathop {\sum}\nolimits_{j^\prime \in N} {\left( {P_{jj^{\prime} } - 1} \right)} {\hat{\theta}}_{jj^{\prime} }
$$

(12)

代码 `compute_cell_velocity.py` 中实现了这一部分：

- `sigma_corr = 0.05`；
- `probability_matrix = np.exp(corrcoef / sigma_corr)*knn_embedding.A`；
- 对每行归一化；
- 计算低维空间单位位移向量；
- 写入 `velocity1` 和 `velocity2`（`compute_cell_velocity.py:54-154`）。

### 9. pseudotime 如何估计？

论文的 pseudotime 不是先验给定，而是根据低维 velocity field 生成轨迹（`paper.md:299-316`）：

1. 把低维嵌入空间划分成网格；
2. 每个网格/meta-cell 取内部细胞 velocity 的均值；
3. 从细胞出发沿 velocity field 扩散生成多条轨迹；
4. 选择长度局部最大的 long trajectories；
5. 根据轨迹终点决定 fate，根据离 long trajectory 最近的位置赋 pseudotime；
6. 对不同 time zones 做时间平移对齐。

运动方程为：

$$
\xi _j\left( {t + \Delta t} \right) = \xi _j\left( t \right) + {\tilde{v}}_I\Delta t
$$

(13)

论文还说每一步加入 $\theta\in N(0,\pi/6)$ 的随机摆动角（`paper.md:307`）。代码中 `diffusion.py` 验证了这个实现：`velocity_add_random()` 从 `np.random.normal(0, theta, 1)` 抽样并旋转 velocity，`diffusion_off_grid_wallbound()` 设定 `THETA = np.pi/6`（`diffusion.py:223-255`, `335-389`）。

`pseudo_time.py` 中还包含 long trajectory 的长度、相似度、选择、fate assignment 和 pseudotime 写入逻辑（`pseudo_time.py:31-145`, `972-1111`, `1115-1340`）。不过该模块很大，时间区间对齐有许多辅助分支；本分析只验证了主路径和关键函数，未逐行重构所有边界情况。

### 10. 论文的主要实验结果

#### 10.1 模拟数据

论文模拟 transcriptional boost、multi-forward branching、multi-backward branching 三种多速率动力学，并与 scVelo、velocyto、DeepVelo、VeloVAE 比较。论文报告 cellDancer 在三种情形下的平均错误率约为 13%、3%、9%，低于对照方法（`paper.md:56-61`; Supplementary Table 1 `supp.md:292-331`）。Extended Data Fig. 1 的图像中也能看到 cellDancer 的 error-rate boxplot 低于多数基线。

代码中 `simulation.py` 确认了 ODE 模拟核心：使用 SciPy `solve_ivp`/RK45，并提供 forward/backward/two-alpha/boost 等生成器（`simulation.py:1-220`）。但完整 benchmark 驱动脚本和竞争方法比较脚本在当前代码快照中 `Not found`。

#### 10.2 小鼠胚胎红系成熟

Fig. 2 显示 cellDancer 在 UMAP 上恢复 progenitor 到 erythroid 的方向，并在 *Hba-x* 和 *Smim1* 等 MURK 转录增强基因上给出更合理的速度方向。论文称 scVelo、DeepVelo、VeloVAE 在这些基因/细胞类型中出现方向错误（`paper.md:62-81`）。

#### 10.3 小鼠海马发育

Fig. 3 显示五个分支的 hippocampus development velocity；*Ntrk2*、*Gnao1* 等分支基因的 phase portrait 表明 cellDancer 能在不同分支上给出方向。论文还用低 loss gene 做 GO enrichment，并用 pseudotime 推断 root/terminal states（`paper.md:82-107`）。

#### 10.4 胰腺内分泌发育与 dynamo

Fig. 4 展示 $\alpha,\beta,\gamma$ 的 UMAP embedding 能把 alpha、beta、delta、epsilon 等细胞类型区分开；论文还把 cellDancer velocity 输入 dynamo 做 vector field 和 Jacobian 分析（`paper.md:108-124`）。代码中 `embedding_kinetic_para.py` 验证了 kinetic-parameter UMAP，`utilities.py` 验证了 dynamo 数据导出工具（`embedding_kinetic_para.py:7-59`, `utilities.py:233-360,394-436`）。但 Fig. 2 的 Gata2 perturbation 和 Fig. 4 的 Arx/Pax4 Jacobian 具体脚本在当前 repo 中 `Not found`。

#### 10.5 其他鲁棒性

论文还展示了 cell-cycle scEU-seq 对照、人类前脑神经发生、dropout/sparsity、stopping criteria、并行速度等结果（`paper.md:125-157`）。其中并行训练在代码中可见：`velocity()` 使用 `joblib.Parallel` 按基因批量训练（`velocity_estimation.py:767-835`）。但 Extended Data Fig. 8 的 Poisson/dropout 模拟源代码在 `src/celldancer/*.py` 中搜索 `dropout`、`Poisson`、`poisson` 后仍 `Not found`。

### 11. 代码复现性评价

**能复现/理解的核心部分：**

- 每基因 DNN；
- $\alpha,\beta,\gamma$ 预测；
- 离散化 ODE 预测未来状态；
- 邻居余弦损失；
- Adam/early stopping/default parameters；
- embedding velocity projection；
- pseudotime 主流程；
- kinetic-parameter embedding；
- dynamo export；
- 基础 ODE simulation helpers。

**当前代码快照缺失的部分：**

- 未找到 `.ipynb` notebooks；
- 未找到完整 paper-figure reproduction scripts；
- 未找到 scVelo/velocyto/DeepVelo/VeloVAE benchmark driver；
- 未找到 Gata2 perturbation、Arx/Pax4 Jacobian 的具体分析脚本；
- 未找到 Extended Data Fig. 8 的 Poisson/dropout 模拟实现。

因此，纸码总体匹配度是 **medium**：核心算法在代码中实现得比较清楚，但论文全套结果复现还需要额外的数据处理和应用分析脚本。

### 12. 学习这个方法时最应该抓住的点

1. **cellDancer 的创新不是单纯使用 DNN，而是用 DNN 学 cell-specific kinetic rates。**
2. **训练信号来自局部邻居，而不是已知真实时间。** 预测速度只要指向局部邻域中最合理的未来状态即可。
3. **每个基因单独训练。** 这让不同基因能有不同动力学模式，也便于并行。
4. **$\alpha,\beta,\gamma$ 本身也是分析对象。** 论文不仅用它们算 velocity，还用它们做细胞身份、细胞周期和转录调控解释。
5. **不要把代码里的输出简单理解成 raw sigmoid probability。** 代码会对 sigmoid 输出进行尺度变换，所以最终 $\alpha,\beta,\gamma$ 是缩放后的 kinetic estimates。
6. **论文结果和库代码要分开看。** 库代码足以说明核心方法；完整复现实验图还需要当前快照之外的脚本/数据流程。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## cellDancer summary

### What problem does the paper solve?

cellDancer addresses a core RNA-velocity limitation: conventional models infer one set of kinetic assumptions across all cells, but real scRNA-seq experiments often contain multi-stage or multi-lineage transitions with different transcription, splicing, and degradation kinetics. The paper frames this as a failure mode for branching genes and transcriptional-boost genes, where global kinetics can reverse or distort inferred velocity directions (`paper.md:12`, `21-24`).

### Proposed method

cellDancer is a relay velocity model implemented as a model-based DNN. For each gene, it uses unspliced and spliced abundance in each cell to infer cell-specific transcription, splicing, and degradation rates $\alpha$, $\beta$, and $\gamma$. It then uses discretized RNA-kinetic ODEs to predict the cell's future unspliced/spliced abundance and trains the DNN by aligning that predicted velocity vector with the best observed displacement among local neighbor cells (`paper.md:41-50`, `185-256`).

In short:

```text
one gene at a time
(unspliced, spliced) per cell
        -> DNN -> cell-specific alpha/beta/gamma
        -> discretized ODE -> predicted future state
        -> neighbor cosine loss -> trained RNA velocity
```

The method also projects gene-wise velocities into low-dimensional embeddings and derives gene-shared pseudotime from velocity-guided trajectories (`paper.md:269-316`).

### Why existing methods are insufficient

The paper compares against velocyto/static RNA velocity, scVelo/dynamical RNA velocity, and deep-learning methods DeepVelo and VeloVAE. The key limitation emphasized is that methods with global/shared kinetics struggle when a gene has multiple kinetic regimes across stages or branches. The paper highlights transcriptional boost during erythroid maturation and branching dynamics during hippocampus development as concrete failure cases (`paper.md:21-24`, `56-81`, `82-107`).

### Main evaluation and results

- **Simulations:** For transcriptional boost, multi-forward branching, and multi-backward branching simulations, the paper reports lower error rates for cellDancer than scVelo, velocyto, DeepVelo, and VeloVAE. Reported mean error rates for cellDancer are about 13%, 3%, and 9% in the three regimes (`paper.md:56-61`; Supplementary Table 1 in `supp.md:292-331`). Extended Data Fig. 1 visually shows lower cellDancer error boxes and convergence curves.
- **Mouse gastrulation erythroid maturation:** Fig. 2 and Extended Data Fig. 2 show cellDancer recovering erythroid differentiation flow and MURK transcriptional-boost gene directions, while other methods show inverted or incorrect directions in several panels (`paper.md:62-81`).
- **Mouse hippocampus development:** Fig. 3 and Extended Data Figs. 3-4 show multi-branch velocity inference, branch-specific genes, low-loss gene ranking, GO enrichment, and pseudotime over five lineages (`paper.md:82-107`).
- **Mouse pancreas:** Fig. 4 and Supplementary Fig. 3 show that cell-specific $\alpha$, $\beta$, and $\gamma$ embeddings separate cell identities and can be passed to dynamo for vector-field/Jacobian analyses (`paper.md:108-124`).
- **Additional robustness:** Extended Data Figs. 5-10 cover scEU-seq cell-cycle comparison, rate-based turnover strategies, human forebrain neurogenesis, dropout/sparsity robustness, stopping-criteria stability, and parallel runtime (`paper.md:125-157`).

### Code-paper match

The cloned GitHub repo at `[local path omitted]` implements the reusable core algorithm:

- DNN layer, sigmoid outputs, scaled $\alpha/\beta/\gamma$, and discretized updates are in `src/celldancer/velocity_estimation.py:32-62`.
- Neighbor cosine loss is in `velocity_estimation.py:88-145` and used by default in `velocity()` (`velocity_estimation.py:690-703`).
- Adam, weight decay, early stopping, checkpoint, patience, and default $\Delta t=0.5$ match paper parameters (`velocity_estimation.py:335-340`, `535-633`, `690-703`).
- Embedding velocity projection implements the transition-probability kernel with `sigma_corr=0.05` (`compute_cell_velocity.py:20-154`).
- Pseudotime and trajectory generation are implemented in `pseudo_time.py` and `diffusion.py`; the key random swaying angle $N(0,\pi/6)$ is verified in `diffusion.py:223-255,335-389`.
- Kinetic-parameter UMAP and dynamo export utilities are implemented in `embedding_kinetic_para.py:7-59` and `utilities.py:233-360,394-436`.

Overall fidelity is **medium**: the core library matches the main relay-velocity method, but the repo snapshot does not contain full paper-specific notebooks/scripts for all benchmark and application figures. The code also uses a per-cell `Linear(2,100)->Linear(100,100)->Linear(100,3)` implementation rather than the paper's literal `2*n`/`3*n` layer wording, and it scales sigmoid outputs before reporting rates.

### Reproducibility notes

**Strong points**

- Paper provides public data sources and dataset-specific preprocessing summaries (`paper.md:320-333`, `338-348`).
- Code availability points to the same GitHub repo cloned here (`paper.md:351`).
- Package exposes high-level functions for velocity estimation, cell-velocity projection, pseudotime, kinetic-parameter embeddings, simulation helpers, and dynamo export.
- Parallelism is implemented with `joblib.Parallel`, supporting the runtime/speedup claim at the library level (`velocity_estimation.py:767-835`).

**Gaps / `Not found`**

- No `.ipynb` notebooks were found in the cloned repository snapshot.
- Paper-specific scripts for reproducing all figures, benchmark comparisons against scVelo/velocyto/DeepVelo/VeloVAE, Gata2 perturbation, Arx/Pax4 Jacobian analysis, and dataset-specific preprocessing were not found in `code source`.
- Source implementation of the Extended Data Fig. 8 Poisson/dropout simulation was not found by searches for `dropout`, `Poisson`, or `poisson` in `src/celldancer/*.py`.

### Bottom line

cellDancer's methodological contribution is local, cell-specific kinetic inference: it replaces one-size-fits-all RNA-velocity kinetics with per-gene DNNs that infer per-cell reaction rates and optimize a neighbor-local velocity alignment loss. The paper's figures support the idea across simulated multi-rate regimes and several developmental systems. The available code is sufficient to understand and use the core algorithm, but not sufficient by itself to reproduce every paper figure without additional data-processing and analysis scripts.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
