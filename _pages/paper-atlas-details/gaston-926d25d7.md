---
layout: default
permalink: /paper-atlas/gaston-926d25d7/
title: "GASTON"
nav: false
description: "GASTON 从空间坐标预测低维表达特征，并强制网络中间只有一个标量瓶颈 d(x,y)。这个标量叫 isodepth：它像地形图的海拔，同一等值线上的远距离位置可以共享相似表达状态。随后方法沿 isodepth 用动态规划切出空间域，再为每个基因在每个域内拟合 Poisson 分段线性函数，从而同时描述域边界处的跳变和域内部的连续梯度。 本文依据本地论文 outputpapermd/paper/auto/paper."
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
      <span>Domain Clustering</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>GASTON</h1>
    <p>Mapping the topography of spatial gene expression with interpretable deep learning</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-024-02503-3" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GASTON">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/raphael-group/GASTON" target="_blank" rel="noopener noreferrer" aria-label="Open code for GASTON">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GASTON：把二维组织压成一条可解释的 isodepth 轴

### 一句话理解

GASTON 从空间坐标预测低维表达特征，并强制网络中间只有一个标量瓶颈 $d(x,y)$。这个标量叫 isodepth：它像地形图的海拔，同一等值线上的远距离位置可以共享相似表达状态。随后方法沿 isodepth 用动态规划切出空间域，再为每个基因在每个域内拟合 Poisson 分段线性函数，从而同时描述域边界处的跳变和域内部的连续梯度。

本文依据本地论文 `paper source/paper/auto/paper.md`、主图 1–6，以及仓库提交 `206cc19ca89d985245ca204fbc86772e5c2446d0` 的直接源码。论文常把整个过程称为一个“同时学习”框架，但公开实现实际上是神经网络、动态规划和逐基因回归串联的多阶段流程。

### GASTON 解决的不是普通聚类问题

传统空间域算法通常给每个 spot 一个离散标签，却默认域内平均表达近似恒定；空间变异基因算法则判断某基因是否随二维位置变化，却很难区分：

- 域与域之间的突变；
- 同一域内部的平滑变化；
- 由细胞类型比例变化产生的表观梯度；
- 同一细胞类型内部真正的状态梯度。

GASTON 的核心假设是：组织中大量主导表达变化可由一个共享的一维空间坐标解释。它不是为每个基因各学一条任意二维曲面，而是先学习所有低维表达特征共同依赖的 $d(x,y)$，再让每个基因拥有自己的分段斜率和截距。

### 第一步：准备坐标与表达特征

输入是 $N\times2$ 空间坐标矩阵 $S$ 和 $N\times G'$ 的低维表达特征矩阵 $A$。论文主要使用前 $2Q$ 个 GLM-PC，其中 $Q$ 是候选域数；代码提供的 `get_top_pearson_residuals()` 则使用：

1. Pearson-residual 高变基因；
2. analytic Pearson residual normalization；
3. PCA。

论文明确把 Pearson-residual PCs 作为更快替代方案，并报告在小脑数据上与 GLM-PC isodepth 的相关系数为 0.88，所以这不是完全无依据的改写，但它并非论文多数主分析所述的 GLM-PCA 原路径。

`load_rescale_input_data()` 会分别对 $S$ 和 $A$ 做 `StandardScaler`。因此网络看到的是标准化坐标，原始网络输出的数值和正负方向都没有天然物理单位；论文图中“微米”尺度来自后续独立校准，而不是瓶颈神经元自动输出距离。

### 第二步：用一维瓶颈学习 isodepth

网络写成复合函数

$$
\widehat A(x,y)=f_A\!\left(f_S(x,y)\right),
$$

其中

$$
d(x,y)=f_S(x,y)\in\mathbb R
$$

是唯一的一维瓶颈，$f_A:\mathbb R\to\mathbb R^{G'}$ 从 isodepth 重建低维表达特征。训练目标是均方误差

$$
L=\frac1N\sum_i\left\|A_i-f_A(d(x_i,y_i))\right\|_2^2.
$$

实现位于 `neural_net.py`：`spatial_embedding` 把二维坐标映射到 1，`expression_function` 再映射到表达特征。代码支持 SGD、Adam 和 Adagrad；CLI 默认 Adam、10,000 epochs。默认 `batch_size=None`，所以是全批训练。

这个网络阶段并没有直接输出空间域，也没有直接拟合原始基因计数的 Poisson 似然。它用 MSE 学低维表达主轴，Poisson 回归发生在后续逐基因解释阶段。

#### 30 次初始化怎样实现

论文说训练 30 个随机初始化并选训练误差最小者。主 CLI 一次只训练一个 seed；`run_slurm_scripts.py` 负责生成 30 个独立任务，`process_NN_output.py::process_files()` 再按同一训练集 MSE 选择模型。这里没有 held-out 验证集，因此选择的是“最能拟合当前样本低维特征”的初始化，而不是外部泛化最优模型。

### 第三步：沿 isodepth 用动态规划切空间域

固定学到的 $d_i$ 后，`get_isodepth_labels()`：

1. 把 isodepth 范围离散为默认 50 个 bucket；
2. 对每个 bucket 中的低维表达特征拟合线性段误差；
3. 用 `dp_bucketized()` 寻找给定 $Q$ 下总误差最小的连续分段；
4. 把同一 isodepth 区间的 spot 赋相同域标签。

因此域在 isodepth 轴上必须是连续区间，但它在二维空间中不必连通：两个相隔很远的组织区域只要具有相同 isodepth 范围，就可属于同一域。这正是 GASTON 可利用长距离重复结构、例如小脑褶皱层的原因。

$Q$ 通常通过不同域数的似然曲线和 Kneedle 选肘点；嗅球图 6 是论文明确的例外，作者依据已知七层结构选 $Q=7$，而不是 Kneedle 给出的 8。因而该例并非完全无先验。

### 第四步：逐基因拟合可解释分段函数

对基因 $g$ 和域 $R_p$，论文模型为

$$
f_g(x,y)=\alpha_{p,g}+\beta_{p,g}d(x,y),\qquad (x,y)\in R_p.
$$

代码 `segmented_poisson_regression()` 使用原始计数和每个 spot 的总 UMI exposure，在每个“基因×域”组合上拟合 `sklearn.linear_model.PoissonRegressor`。它比较：

- $H_0$：斜率为 0；
- $H_1$：斜率自由。

`llr_poisson()` 用似然比检验决定是否保留非零斜率。最终矩阵包括：

- `slope_mat`：$\beta_{p,g}$，域内连续变化；
- `intercept_mat`：$\alpha_{p,g}$；
- `discont_mat`：相邻域边界两侧预测值的差；
- `pv_mat`：斜率检验的 P 值。

边界跳变不是另一个神经网络输出，而是从相邻两段的斜率和截距在 breakpoint 处计算出来。

### isodepth 的梯度表示什么

因为所有拟合基因在一个域内都写成 $f_g=\alpha_{p,g}+\beta_{p,g}d$，所以

$$
\nabla f_g(x,y)=\beta_{p,g}\nabla d(x,y).
$$

$\nabla d$ 给出 isodepth 增长最快的方向；不同基因通过 $\beta_{p,g}$ 决定沿同一方向升高、降低或保持平坦。这是一种局部 rank-one 梯度假设：同一域内所有被模型解释的基因梯度必须共线。它换来强可解释性和对稀疏数据的聚合能力，但无法同时表达两个彼此独立的空间变化轴。

图中的 streamlines 来自对训练后 `spatial_embedding` 求空间导数和插值；它们表示模型主轴，不应自动解释为细胞迁移速度、分子通量或因果方向。isodepth 的正负方向可反转，因此“向内/向外”需要结合解剖标注确定。

### 连续变化、跳变和细胞类型归因

GASTON 用 $|\beta|$ 识别域内变化，用边界差 $|\delta|$ 识别不连续变化。这里存在明确论文—代码冲突：

- Methods 文字写阈值为所有绝对斜率/跳变的第 10 百分位；
- `spatial_gene_classification.py` 默认 `q=0.95`，实际取第 95 百分位，只保留每个域或边界最强约 5%。

两者会产生数量级不同的基因集合。论文图 4 报告的 1,572 个空间变化基因究竟对应哪一套调用参数，不能只从函数默认值反推；复现时必须显式记录 `q`。

单细胞分辨率且已有 cell-type 标签时，`pw_linear_fit()` 还能在每个细胞类型子集内拟合斜率。如果某细胞类型的斜率绝对值占总体斜率足够比例，则把梯度归因于该类型。核心函数默认 `ct_perc=0.6`，而旧说明中常见的 0.5 并未在核心库中确认，调用 notebook 可能另行设置。

### 从左到右读真实代码路径

1. `parse_adata.py`：准备 Pearson-residual PCs，必要时加入 RGB 特征。
2. `neural_net.load_rescale_input_data()`：分别标准化坐标和特征。
3. CLI 或 `run_slurm_scripts.py`：训练一个或多个 bottleneck 网络。
4. `process_NN_output.process_files()`：从多 seed 中按训练 MSE 选模型。
5. `dp_related.get_isodepth_labels()`：提取 isodepth，bucketized DP 切域。
6. `model_selection.py`：绘制似然曲线并用 Kneedle 辅助选 $Q$。
7. `segmented_fit.pw_linear_fit()`：原始基因计数的逐域 Poisson 回归。
8. `spatial_gene_classification.py`：按斜率与跳变组合给基因分类。
9. `isodepth_scaling.py`、`binning_and_plotting.py`、`cluster_plotting.py`：物理尺度校准、沿轴分箱和二维可视化。

### 主图证据怎么读

- 图 1 是方法示意：一维瓶颈连接二维坐标和表达，之后才做域、基因函数和细胞类型分析。
- 图 2 的 Slide-seqV2 小脑中，GASTON 与 GraphST 的空间一致性都很高；GASTON 对 RCTD 的 F-measure 为 0.74，并非所有指标绝对领先。优势在于额外提供层内连续坐标。
- 图 3 中稀疏 Sbk1 经 isodepth 分箱后出现清晰分段曲线，marker AUPRC 约 0.31。拟合曲面是模型估计，不应与新增实验测量混淆。
- 图 4 的 CRC 没有域真值；肿瘤/基质命名依据 H&E 与已有注释。代谢、EMT 和免疫结论来自模式富集和已知基因，属于生物学解释而非因果证明。
- 图 5 的 Xenium 乳腺癌展示免疫域和 TCL1A/SELL 梯度；cell-type-attributable 判断依赖输入细胞类型标签。
- 图 6 的嗅球径向层与 isodepth 高度一致，但 $Q=7$ 使用已知层数；“potency/maturation axis”结合了既有神经发生知识，是解释而非网络直接监督出的时间。

### 代码匹配与边界

**总体：Medium-High。** 一维瓶颈、MSE 训练、bucketized DP、Kneedle、逐基因 Poisson 回归、斜率检验、边界差、细胞类型子拟合和可视化均可在本地源码定位。固定提交也已确认。

主要偏差和工程边界包括：论文阈值第 10 百分位与代码默认 0.95 冲突；主分析 GLM-PCA 与库内便捷函数 Pearson residual PCA 不同；30 seeds 需要外部调度；位置编码参数存在但实现未启用；域分割使用 50-bucket 近似；模型选择无 held-out 验证；物理尺度与方向需后处理校准。

最重要的概念限制是：isodepth 只有一维。它适合层状、径向、边界到内部等具有主导空间轴的组织；若同一区域同时存在两个独立梯度，单个 $d(x,y)$ 只能优先解释其中的主变化或折衷表示。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## GASTON 论文总结

本文档基于 `paper source/paper/auto/paper.md` 中的论文正文，以及本地 `GASTON/` 源码整理。论文题目为 *Mapping the topography of spatial gene expression with interpretable deep learning*，发表于 **Nature Methods (2025)**。

### 一句话概括

GASTON 想做的事情，是把一张二维空间转录组切片压缩成一条可解释的一维坐标 `isodepth`，然后把每个基因的表达写成这条坐标上的**分段线性函数**，从而在同一个框架里同时描述：

- 空间域之间的突变边界
- 空间域内部的连续梯度
- 细胞类型组成沿空间轴的连续变化

### 1. 论文试图解决什么问题

空间转录组数据里常常同时存在两类变化：

1. **不连续变化**：例如脑分层、肿瘤和基质的边界，表达会突然跳变。
2. **连续变化**：例如分化、代谢、炎症、迁移等过程，会让表达在一个空间域内部缓慢变化。

已有方法通常只擅长其中一类：

- 空间聚类/分区方法更擅长找离散 domain，但把 domain 内部看得过于平坦。
- SVG 方法能告诉你“这个基因在空间上有变化”，但不能把连续梯度和边界跳变区分开。
- 连续坐标方法又往往难以保证这个坐标在**物理空间**里连续、可解释。

GASTON 的切入点是：如果组织里存在一个主导的空间变化方向，那么也许可以用一条一维轴来概括整张切片的“表达地形”。

### 2. 核心概念：isodepth

论文把 `isodepth` 类比成地形图里的“海拔”：

- `isodepth` 相同的位置，表达状态相似；
- `isodepth` 的等值线构成空间域边界；
- `∇d` 给出表达变化最快的方向；
- 沿 `isodepth` 轴看，可以把稀疏二维数据汇总成更稳定的一维趋势。

这个想法最关键的价值，不是单纯把二维降到一维，而是让模型能：

- 沿整条等深度轮廓汇总信号，缓解稀疏计数问题；
- 允许**空间上相距较远**的区域共享同一个 `isodepth`；
- 用统一坐标同时解释 domain、梯度、细胞类型布局和肿瘤微环境过程。

#### 2.1 最终得到的 `d` 到底是什么

更准确地说，最终得到的 `d` 不是简单的“物理深度”，而是一个从二维组织中学出来的**主空间轴**：

- 数学上，它是一个标量场，等值线定义空间域，梯度给出主变化方向；
- 统计上，它是最能共同解释多基因空间变化的一维 bottleneck 坐标；
- 生物学上，它可能对应层深度、边界到内部的生态位轴，或者成熟度 / potency 轴；
- 实际解读时，最有意义的是 `d` 的相对顺序、边界位置和沿轴的 cell type / gene 变化，而不是原始数值本身。

这也是为什么论文既能用 `d` 解释小脑层结构，也能用它解释肿瘤微环境和嗅球中的连续生物过程。

### 3. 数学模型的核心形式

GASTON 假设每个基因在空间中的表达都可以写成

$$
f_g(x,y) = h_g(d(x,y))
$$

其中：

- `d(x,y)` 是从二维坐标到一维 `isodepth` 的映射；
- `h_g` 是基因 `g` 在 `isodepth` 轴上的一维表达函数。

进一步，论文要求 `h_g` 是**分段线性**的：

$$
f_g(x,y)=\sum_{p=1}^{Q}(\alpha_{g,p}+\beta_{g,p}d(x,y)) \cdot \mathbf{1}_{\{(x,y)\in R_p\}}
$$

这里：

- `R_p` 是第 `p` 个空间域；
- `α_{g,p}` 控制该域内的基线表达；
- `β_{g,p}` 控制该域内沿 `isodepth` 的连续梯度；
- 相邻 domain 之间的函数跳变就是“不连续变化”。

这使得一个模型同时覆盖三件事：

1. domain 边界位置
2. domain 内部连续梯度
3. 不同基因在不同 domain 的空间模式差异

### 4. 论文中的算法流程

GASTON 的实际流程可以概括成三段：

#### Step 0: 低维特征准备

论文写法是先取 top-`2Q` 的 GLM-PCs；本地代码默认实现则是：

- Pearson residual HVG 筛选
- PCA 得到 top-`2Q` 特征
- 对空间坐标和输入特征分别做 `StandardScaler`

这一步的目的不是最终建模，而是给神经网络提供一个更平滑、更易训练的目标。

#### Step 1: 用 bottleneck 神经网络学习 `isodepth`

网络分成两部分：

- `f_S: R^2 -> R`，从 `(x,y)` 到单个 hidden neuron
- `f_A: R -> R^{2Q}`，从这个一维 neuron 回归到低维表达特征

这个单神经元 bottleneck 就是论文中的 `isodepth`。

#### Step 2: 在 `isodepth` 上做分段回归

神经网络给出每个 spot 的 `isodepth` 后，GASTON 不直接把 network 输出当最终结果，而是在这条一维轴上再做一次**分段回归**：

- 用动态规划找 breakpoints
- 把连续的 `isodepth` 划成 `Q` 个 domain

这一步相当于把“连续地形”切成若干个有生物含义的空间层或区域。

#### Step 3: 对每个基因做 Poisson 回归

在每个 domain 里，对每个基因单独拟合

$$
a_{i,g} \sim \text{Pois}(U_i \exp(\alpha_{g,p}+\beta_{g,p} d_i))
$$

其中 `U_i` 是 spot 的总 UMI。随后再用 LLR 检验决定该 domain 内斜率是否保留为非零。

### 5. 论文最重要的结果

### 5.1 小鼠小脑：domain 与梯度可以同时恢复

小脑是一个非常典型的分层组织。GASTON 在这里做到了两层意义上的恢复：

- 宏观上，识别出与已知小脑层一致的空间域；
- 微观上，给出每一层内部沿 `isodepth` 的细胞类型比例和基因表达梯度。

论文强调的一点是：其他方法即使能把层分出来，也通常无法说明“同一层里面从浅到深还发生了什么”。

### 5.2 稀疏 marker gene 也能被恢复

以 `Sbk1` 为例，原始计数非常稀疏，单看二维 raw expression 很难定位 Purkinje-Bergmann layer。GASTON 通过沿 `isodepth` 轮廓聚合表达，把这个信号变成了清晰的一维峰值，并能回投到二维空间。

这说明 GASTON 的优势不是“更复杂的深度学习”，而是它用对了信息共享方式：不是只看邻近 spot，而是沿共享 `isodepth` 的整条轮廓一起汇总。

### 5.3 域内连续变化可以归因到细胞类型

论文把 domain 内连续变化继续拆成两种：

- **cell type-attributable**
- **not attributable to cell type**

例如：

- `Calb1` 的梯度可归因于 granule cells；
- `Secisbp2l` 的梯度可归因于 oligodendrocytes；
- 也有一些基因虽然表现出域内梯度，但不能直接归因到某个主导 cell type，提示它可能来自细胞比例变化、细胞互作或其他过程。

这一步让 GASTON 从“空间表达建模”进一步走向“空间机制解释”。

### 5.4 CRC 肿瘤微环境：把空间模式整理成三类生物过程

在 CRC Visium 数据上，GASTON 识别出 1,572 个空间变化基因，并将它们按组合模式整理为三大类：

- **Type I**：肿瘤内部连续变化，无明显边界跳变
- **Type II**：肿瘤-基质边界处有跳变，且在邻近基质中继续变化
- **Type III**：主要体现基质或边界相关的免疫/增殖信号

作者进一步把这些模式解释为：

- Type I 对应代谢、氧化磷酸化、胆固醇稳态
- Type II 对应 EMT 和侵袭边界
- Type III 更偏免疫反应和增殖

这说明 GASTON 不只是做 clustering，而是在用统一坐标组织肿瘤微环境的空间生物学。

### 5.5 乳腺癌 Xenium：免疫浸润的位置也能投影到 isodepth

在 breast cancer Xenium 数据中，GASTON 学到从 duct 外部到内部的连续 `isodepth`。这条轴能定量描述：

- 不同细胞类型在 duct 周围的位置
- T/B 细胞相关基因的空间梯度
- 免疫浸润与局部组织结构的关系

这说明方法不依赖某一种 SRT 技术，而是适用于 sequencing-based 和 imaging-based 数据。

### 5.6 嗅球：isodepth 可以成为发育/成熟轴

在小鼠 olfactory bulb 的 Stereo-seq 数据中，GASTON 学出的 `isodepth` 与径向层状结构高度一致，并能把它解释为一种“potency / maturation axis”：

- 高 `isodepth` 端更接近 RMS 和未成熟状态
- 低 `isodepth` 端更接近外围成熟层

这说明 `isodepth` 不一定只表示“物理深度”，它也可能对应某种连续生物过程。

### 6. 这篇论文真正的创新点

我认为 GASTON 的创新主要不在“用了神经网络”，而在以下四点：

1. **提出了 isodepth 这个中间表示**
   把空间域和连续梯度统一到一个可解释坐标里。

2. **允许 global pooling**
   沿等 `isodepth` 轮廓汇总表达，从而利用长程空间相关性，而不只依赖局部邻接图。

3. **把离散边界和连续梯度放进同一个分段线性框架**
   这让 domain discovery、gradient discovery、marker gene identification 可以共用一套参数化。

4. **把空间模式和生物过程联系起来**
   尤其在肿瘤例子中，空间表达模式被进一步整理成可以解释的代谢、EMT、免疫程序。

### 7. 方法的关键假设与局限

论文自己也承认 GASTON 依赖两个强假设：

1. **所有空间变化基因共享同一个主导方向**
   即 Jacobian 近似 rank-one。若组织存在两个独立主轴，单一 `isodepth` 可能不够。

2. **空间梯度场是 conservative**
   即 `v = ∇d`，不允许明显“旋转式”的空间流。

因此 GASTON 更适合：

- 层状组织
- 边界到内部这种单主轴结构
- 径向结构
- 某个主导梯度明显的局部组织区域

它不一定适合：

- 同时存在多个强空间轴
- 明显回旋/环流式结构
- 强非单调、多分叉的复杂空间过程

### 8. 从本地代码看，论文和实现有什么差别

本地代码整体忠实于论文主线，但存在几个值得说明的实现差异：

- 论文 Methods 写 GLM-PCA，代码默认是 **Pearson residuals + PCA**
- 30 个随机种子是通过 `run_slurm_scripts.py` 外部并行，不是 CLI 一次完成
- Methods 写第 10 百分位并保留大于阈值者（约上方 90%），代码默认 `q=0.95`（约最强 5%）；两者不是轻微严格度差异，而会产生规模悬殊的基因集合
- 细胞类型归因代码默认 `ct_perc=0.6`，比论文中 `γ=0.5` 更保守
- 代码里对输入做 `StandardScaler`，这是很重要但论文没有重点展开的训练细节

所以更准确的说法是：**论文提出了理论框架，代码给出了可运行、带工程折中的实用版本。**

### 9. 我的整体评价

这篇文章最强的地方，是它提出了一个非常自然、又足够可操作的中间层表示：`isodepth`。一旦这个表示成立，很多原本分散的问题都会变简单：

- 空间域划分变成找 breakpoints
- 梯度分析变成看 slope
- marker gene 识别变成看不同 domain 的函数差异
- 细胞类型变化变成沿一维轴的比例曲线

它的弱点也同样明确：如果组织没有一个主导的一维空间轴，那么 GASTON 的解释力会下降。

总体上，我会把 GASTON 看成一种**“面向单主轴组织几何的可解释空间表达模型”**。它不是最通用的空间转录组方法，但在层状、径向、边界到内部这类几何结构明确的场景里，非常有洞察力。

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
