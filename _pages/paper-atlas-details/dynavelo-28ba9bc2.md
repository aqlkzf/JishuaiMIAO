---
layout: default
permalink: /paper-atlas/dynavelo-28ba9bc2/
title: "DynaVelo"
nav: false
description: "DynaVelo 可以理解为一个面向 single-cell multiome 数据的动态模型：它把同一个细胞里的 RNA 表达和 TF motif accessibility 放进同一个 latent neural ODE 里，学习一个连续的细胞状态变化方向场，然后从这个方向场里导出 RNA velocity、motif velocity、latent time、动态调控网络和扰动预测。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>DynaVelo</h1>
    <p>Deep dynamical models of single-cell multiomic velocities predict loss-of-function and rescue perturbations in B cells</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2025.04.24.650458" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DynaVelo 方法详细解释

本文依据本工作区已有的 `summary.md`、`doc_method.md` 和 `doc_code.md` 编写，目标是把 DynaVelo 的方法逻辑讲清楚：它解决什么问题，输入是什么，模型内部如何从 RNA 和 motif accessibility 学习动态，训练目标如何约束方向性，最后的 trajectory、dynamic GRN 和 perturbation/rescue 结果应该如何解释。

### 1. 一句话理解 DynaVelo

DynaVelo 可以理解为一个面向 single-cell multiome 数据的动态模型：它把同一个细胞里的 RNA 表达和 TF motif accessibility 放进同一个 latent neural ODE 里，学习一个连续的细胞状态变化方向场，然后从这个方向场里导出 RNA velocity、motif velocity、latent time、动态调控网络和扰动预测。

这里最重要的变化是：DynaVelo 不只问“RNA 表达现在像哪个状态、接下来往哪走”，还问“调控层面的 TF motif accessibility 是否也在同步变化，并且这种调控层变化如何帮助解释 RNA 动态”。

### 2. DynaVelo 为什么需要 RNA + motif 两个模态

传统 RNA velocity 主要依赖 spliced/unspliced RNA 的比例来推断基因表达的变化方向。这个思路很有用，但有几个限制：

1. 不是所有基因都有可靠的 velocity 信号。很多基因因为 reads、剪接动力学或技术噪声，无法得到稳定的 scVelo velocity。
2. RNA velocity 主要看到转录结果，不能直接看到更上游的染色质开放性和 TF 活性。
3. 对 germinal center B cell 这类快速转换的系统，命运选择常常由 TF、染色质重塑和表观调控先发生变化，再体现在 RNA 表达上。

DynaVelo 的生物学动机就是补上这一层。它使用 single-cell multiome 数据中的 RNA 表达作为 transcriptional state，同时使用 ATAC 推出的 chromVAR TF motif accessibility 作为 TF activity proxy。这样模型可以把“基因表达状态”和“调控可及性状态”同时放进动态系统里。

在论文应用场景中，这一点尤其重要。GC B cells 会在 dark-zone proliferation、light-zone selection、recycling、apoptosis、memory B cell/plasma cell differentiation 之间快速转换。这些转换不是单纯由当前 RNA 表达决定，也受 Arid1a、Ctcf 等染色质和调控因子影响。DynaVelo 试图让模型同时看到这些状态。

### 3. 输入数据是什么

DynaVelo 的核心输入可以分成四类。

第一类是 RNA 表达矩阵：

$$
x(t) \in R^m
$$

这里 $x(t)$ 表示某个细胞在 latent time $t$ 上的 log-normalized RNA expression，$m$ 是建模基因数。

第二类是 TF motif accessibility 矩阵：

$$
y(t) \in R^k
$$

这里 $y(t)$ 是 chromVAR 计算出来的 cell-wise motif accessibility z-score，$k$ 是 TF motifs 数量。论文和现有文档把它解释为 TF activity 的 proxy。需要注意：motif accessibility 不是 TF 蛋白活性本身，而是染色质可及性层面的近似信号。

第三类是 scVelo 给出的 RNA velocity：

$$
v_x^{scvelo}
$$

它只在一部分 velocity genes 上可靠。DynaVelo 不把 scVelo 当作最终答案，而是把它作为方向监督，帮助神经 ODE 学到合理的 RNA 变化方向。

第四类是 velocity-gene mask 和 cell-type weight。velocity-gene mask 表示哪些基因有可用的 scVelo velocity；cell-type weight 用来平衡不同 cell state 的训练影响，避免稀有状态在 reconstruction loss 中被大量细胞淹没。

### 4. 预处理逻辑：RNA 和 ATAC 如何变成模型输入

RNA 侧的流程大致是：

1. 从 CellRanger 输出开始。
2. 做细胞 QC，包括基因数、UMI 数、线粒体比例等过滤。
3. 做 total-count normalization、log transform 和 highly variable gene selection。
4. 对 spliced/unspliced 矩阵运行 velocyto/scVelo，得到部分基因的 RNA velocity。

ATAC/motif 侧的流程大致是：

1. 使用 ArchR 和 MACS2 处理 scATAC peaks。
2. 使用 chromVAR 计算每个细胞的 motif accessibility z-score。
3. 只保留在足够多细胞中表达的 TF。
4. 当一个 TF 对应多个 motif 时，选择与该 TF RNA 表达 Pearson correlation 最高的 motif。

这一步有一个重要解释：DynaVelo 并不是直接输入 peak-by-cell 矩阵，而是输入 TF motif accessibility。这样模型输出的 motif velocity 更容易被解释为 TF activity program 的动态变化。

### 5. 最核心的数学对象：耦合动态系统

DynaVelo 在观测空间里的出发点是一个耦合 ODE：

$$
\frac{dx(t)}{dt}=f_x(x(t),y(t)), \qquad
\frac{dy(t)}{dt}=f_y(x(t),y(t)).
$$

这个式子表达了一个关键假设：RNA 表达变化不仅由 RNA 表达本身决定，也可能受 motif accessibility 影响；motif accessibility 的变化也可能和 RNA 状态共同相关。

换句话说，DynaVelo 不是分别训练一个 RNA 模型和一个 ATAC 模型，而是把 RNA 和 motif 当作同一个动态系统的两个投影。

但直接在高维 $x(t)$ 和 $y(t)$ 上学习 ODE 很难，因为维度高、噪声大、数据稀疏。所以 DynaVelo 把动态系统放到 latent space 中：

$$
\frac{dz_x(t)}{dt}=f_{z_x}(z_x(t),z_y(t)), \qquad
\frac{dz_y(t)}{dt}=f_{z_y}(z_x(t),z_y(t)).
$$

其中 $z_x(t)$ 是 RNA latent state，$z_y(t)$ 是 motif latent state。实际实现中会把二者拼接：

$$
z(t)=[z_x(t),z_y(t)].
$$

神经网络 ODE function 接收拼接后的 latent state，然后输出两个 velocity block：一个对应 RNA latent dynamics，一个对应 motif latent dynamics。

### 6. 模型结构：encoder + latent time + neural ODE + decoder

DynaVelo 的模型可以按四个模块理解。

#### 6.1 Encoder：从当前观测推断初始 latent state

对每个细胞，模型不是直接假设它从固定初始点演化而来，而是用 encoder 从观测到的 $x$ 和 $y$ 推断初始 latent state：

$$
z_x(0) \sim q(z_x(0)\mid x), \qquad
z_y(0) \sim q(z_y(0)\mid y).
$$

已有文档中对应的先验是：

$$
z(0)\sim N(0,I).
$$

代码中分别产生 $z_x(0)$ 和 $z_y(0)$ 的 Normal posterior 参数。这个设计接近 variational autoencoder 的思路：每个细胞的初始 latent state 有不确定性，而不是一个确定点。

#### 6.2 Latent time：每个细胞有一个 inferred time

DynaVelo 还为每个细胞推断 latent time：

$$
t \sim Beta(2,2).
$$

encoder 会输出 Beta posterior 参数 $\alpha_t,\beta_t$。评估时常用 Beta mean：

$$
E[t]=\frac{\alpha_t}{\alpha_t+\beta_t}.
$$

这里要特别注意：DynaVelo 的 latent time 不是实验采样时间，也不是简单 pseudotime。它是模型为了让 ODE 解释当前细胞状态而推断出的内部时间坐标。公开代码在存储可视化用的 `latent_time` 时还会做 rank normalization 到 $[0,1]$，因此图上看到的 `latent_time` 更像排序后的相对进程，不应直接解释成真实物理时间。

#### 6.3 Neural ODE：在 latent space 里连续演化

有了 $z(0)$ 和 $t$ 后，模型通过 neural ODE 从 $0$ 积分到每个细胞的 latent time：

$$
z(t)=z(0)+\int_0^t f_z(z(s))ds.
$$

这里的 $f_z$ 是神经网络学到的动态函数。它不是手写的生物化学方程，而是从数据、scVelo 方向监督和 RNA/motif consistency 约束中学习出来的 vector field。

实现中有一个细节：训练时会把 batch 内的 latent time 排序后再求解 ODE，因为 ODE solver 需要单调的时间网格。然后模型把求解得到的 latent states 放回原来的细胞顺序。

#### 6.4 Decoder：从 latent state 回到 RNA 和 motif

ODE 求解得到 $z_x(t)$ 和 $z_y(t)$ 后，decoder 把它们映射回观测空间：

$$
x(t)\mid z_x(t)\sim N(g_x(z_x(t)),\sigma_x^2I),
$$

$$
y(t)\mid z_y(t)\sim N(g_y(z_y(t)),\sigma_y^2I).
$$

已有文档中记录的默认设置是 `sigma_x=0.1`、`sigma_y=0.1`，也就是方差 $0.01$。这表示模型用高斯观测模型解释 RNA 和 motif reconstruction。

### 7. DynaVelo 如何得到 RNA velocity 和 motif velocity

这是 DynaVelo 最关键也最容易误解的一步。

模型在 latent space 里学到的是：

$$
\frac{dz_x(t)}{dt}=f_{z_x}, \qquad \frac{dz_y(t)}{dt}=f_{z_y}.
$$

但生物解释通常需要观测空间里的 RNA velocity 和 motif velocity，也就是：

$$
v_x(t)=\frac{d\mu_x(t)}{dt}, \qquad v_y(t)=\frac{d\mu_y(t)}{dt}.
$$

由于 $\mu_x(t)=g_x(z_x(t))$、$\mu_y(t)=g_y(z_y(t))$，DynaVelo 用 chain rule 把 latent velocity 转成 observation-space velocity：

$$
v_x(t)=J_{g_x}f_{z_x},
$$

$$
v_y(t)=J_{g_y}f_{z_y}.
$$

这里 $J_{g_x}$ 和 $J_{g_y}$ 是 decoder 的 Jacobian。也就是说，DynaVelo 不是简单在 reconstructed expression 上做差分，而是用 decoder 对 latent state 的导数，把 latent ODE 的速度投影回 RNA 和 motif 空间。

公开代码中这一点和方法描述匹配得很好：`dynavelo/models.py` 里使用 `vmap(jacrev(...))` 计算 decoder Jacobian，再和 latent velocity 做 batched matrix multiplication，得到 `vx_pred` 和 `vy_pred`。

这也解释了 DynaVelo 的两个主要输出：

1. RNA velocity：模型预测每个基因表达接下来增加还是减少。
2. Motif velocity：模型预测每个 TF motif accessibility 接下来增加还是减少。

motif velocity 是 DynaVelo 区别于 RNA-only velocity 方法的核心输出之一。

### 8. 训练目标如何约束模型

DynaVelo 的总损失可以写成：

$$
{\cal L}={\cal L}_{reconstruction}+\kappa_1{\cal L}_{velocity}+\kappa_2{\cal L}_{velocity consistency}+\kappa_3{\cal L}_{regularization}.
$$

这四部分分别解决不同问题。

#### 8.1 Reconstruction loss：模型要能重建 RNA 和 motif

reconstruction loss 要求 decoder 生成的 $g_x(z_x(t))$ 和 $g_y(z_y(t))$ 能解释观测到的 RNA 表达和 motif accessibility。

如果只有这一项，模型可能只学到一个好看的 autoencoder，而不一定学到真实方向。因此 reconstruction 是必要条件，但不是 velocity 模型的充分条件。

公开实现中还有 cell-type weighting：稀有细胞类型会得到更高权重。这一点在论文高层公式中不突出，但对 GC B cell 这种多状态系统很重要，因为 rare states 可能恰好是命运转换的关键节点。

#### 8.2 RNA velocity supervision：用 scVelo 提供方向锚点

DynaVelo 使用 scVelo velocity 作为 partial supervision。具体来说，它在 velocity genes 上比较模型预测 RNA velocity 和 scVelo velocity 的方向，使用 cosine similarity 作为约束。

直觉上，这一项告诉模型：“在 scVelo 相对可信的基因上，你预测的 RNA 变化方向不要和已有 RNA velocity 完全矛盾。”

但它只是 partial supervision。DynaVelo 仍然可以为所有 modeled genes 预测 RNA velocity，也可以为 motif features 预测 motif velocity。

#### 8.3 Velocity consistency：RNA 和 motif 的动态结构要相互协调

DynaVelo 还加入 RNA velocity 和 motif velocity 之间的 consistency loss。已有文档描述为：比较 RNA velocity 和 motif velocity 的 pairwise cosine-similarity structures。

可以这样理解：如果两个细胞在 RNA velocity 空间里显示出相似的变化方向，那么它们在 motif velocity 空间里也应该有某种一致的动态结构。这个约束把两个模态的方向场耦合起来，避免 RNA 和 motif 各自学成互不相关的动态。

这一步体现了 DynaVelo 的核心假设：调控层和表达层不是两个独立的后处理结果，而是同一个动态过程的两个方面。

#### 8.4 KL regularization：限制 latent state 和 latent time 不要乱跑

最后一类是 regularization，主要是 latent initial state 和 latent time posterior 相对先验的 KL divergence。

它的作用是让 $z(0)$ 和 $t$ 的分布不要过度贴合训练数据噪声，也让 latent space 更稳定。已有文档记录的默认权重包括 `k_z0=1000`、`k_t=1000`、`k_velocity=10000` 和 `k_consistency=10000`，说明 velocity 和 cross-modality consistency 在训练中被赋予很强的约束。

### 9. 从模型输出如何读生物学结果

DynaVelo 训练完成后，主要可以读出六类结果。

#### 9.1 Latent time

latent time 给出细胞在模型内部动态轨迹上的相对位置。它可以帮助判断细胞是否沿着 expected biological progression 排列，例如 GC B cell 从 CB cell-cycle progression 到 CB-to-CC transition，再到 recycling 或 terminal exit。

但 latent time 不是独立测量的时间。它依赖模型假设、训练目标、输入数据和 normalization。尤其公开代码中的 `latent_time` 是 rank-normalized 的相对排序，所以适合用于比较前后顺序，不适合解释绝对时间间隔。

#### 9.2 RNA velocity

RNA velocity 表示模型预测的 gene expression 变化方向。相比 scVelo，DynaVelo 的 RNA velocity 不是只来自 spliced/unspliced 动力学，而是来自 joint latent ODE，并受到 motif dynamics 的间接约束。

因此，当 DynaVelo 与 scVelo 给出不同 latent ordering 或 branch direction 时，需要看两点：一是 DynaVelo 是否更符合已知生物学；二是 motif velocity 是否提供了额外解释，而不是仅仅让模型更复杂。

#### 9.3 Motif velocity

motif velocity 表示 TF motif accessibility 的预测变化方向。例如某些 TF motif 在向 plasma cell 分化方向增强，另一些在 recycling 或 dark-zone 状态中增强。

这类结果的解释应当是：“模型预测该 TF motif accessibility program 正在增强或减弱。”它不能直接等价于 TF 蛋白活性增强，也不能自动证明该 TF causally drives 这个过程。更稳妥的表述是 regulatory hypothesis。

#### 9.4 Generated trajectories

DynaVelo 可以从给定细胞出发，在 latent ODE 中沿时间网格生成 trajectory，然后 decode 回 RNA 和 motif 空间。这用于展示模型认为某个细胞可能如何沿动态路径变化。

生成轨迹的优点是可以同时观察 RNA expression program 和 motif accessibility program 的连续变化。限制是它仍然是模型内插/外推出来的路径，不是实际 lineage tracing 证据。

#### 9.5 Dynamic GRN

DynaVelo 的 dynamic GRN 来自 learned vector field 的局部 Jacobian，而不是传统的静态相关网络。已有文档中的四类 derivative 是：

$$
J_{xx}^{(c)}=\frac{\partial f_x}{\partial x}, \quad
J_{yx}^{(c)}=\frac{\partial f_y}{\partial x}, \quad
J_{xy}^{(c)}=\frac{\partial f_x}{\partial y}, \quad
J_{yy}^{(c)}=\frac{\partial f_y}{\partial y}.
$$

这些量回答的问题是：在某个细胞附近，如果轻微改变某个 gene expression 或 motif accessibility，模型预测 RNA velocity 或 motif velocity 会怎么变。

因此 dynamic GRN 的含义是 local sensitivity of the learned dynamics。它比简单相关性更接近动态系统解释，但仍然不是严格因果实验。它依赖模型学到的 vector field，也依赖 finite-difference 近似和输入特征选择。

公开代码中 dynamic GRN 通过 finite difference 实现，默认扰动量为 $\epsilon=10^{-4}$。为了控制内存，代码只对选定 genes 和全部 TF motifs 计算 Jacobian，而不是对所有基因做完整 dense Jacobian。

#### 9.6 In silico perturbation 和 rescue target

DynaVelo 还做 knockout-like perturbation。规则是：

1. 对非 TF gene，把 RNA expression 设置到 population minimum。
2. 对 TF，同时把该 TF 的 RNA expression 和对应 motif accessibility 设置到 population minimum。
3. 重新计算 velocity，得到 perturbation 前后的差值：

$$
\Delta v_x = v_x^{perturbed} - v_x^{original},
$$

$$
\Delta v_y = v_y^{perturbed} - v_y^{original}.
$$

这些 delta velocities 用来解释“如果模型中压低这个 gene/TF，细胞状态的变化方向会如何改变”。

论文进一步用这些 perturbation deltas 做 rescue analysis：寻找哪些 perturbation 能把 mutant cell state 的 velocity changes 推向 WT-like direction。已有文档指出，公开仓库实现了 perturbation delta 的生成，但 Figure 6 最终 rescue-count scoring 和 plotting 脚本不完整。因此 rescue target ranking 应该看作计算假设，而不是完整可复现实验结论。

### 10. DynaVelo 在 GC B cell 分析中的解释框架

在 WT GC B cells 中，DynaVelo 被用来恢复几个已知过程：

1. CB cell-cycle progression。
2. CB-to-CC transition。
3. CC-to-CB recycling。
4. apoptosis 或 terminal differentiation。

它的关键卖点不是只画出一条更平滑的 latent time，而是能同时给出 RNA 和 motif 层面的动态解释。例如某些分支中 Spi1、Nfkb1、Runx1、Prdm1、Xbp1、Foxo1、Mef2b、Mef2c、Pou2f2 等 TF 的 RNA 和 motif accessibility 变化可以被放在同一个动态系统里比较。

在 Arid1aHet、CtcfHet 等突变背景中，DynaVelo 用同样框架比较动态方向和 regulatory programs 的改变。例如 summary 中提到 Arid1aHet 下 Foxp1、Bach2、Spi1、Stat3 accessibility 有明显变化；dynamic GRN 分析中还关注 Foxo1-to-Cxcr4、Bcl6-to-Bcl2 等边的改变。

这些分析的合理读法是：DynaVelo 提供了一个联合 RNA/motif 的动态解释框架，用来发现哪些 TF activity programs 和 regulatory sensitivities 可能与 mutant phenotype 相关。

### 11. 与 scVelo、Dynamo、scDiffEq 的区别

DynaVelo 和 scVelo 的关系是“利用但不等同”。scVelo 提供 RNA velocity supervision，但 DynaVelo 另外学习 joint RNA/motif latent dynamics，并输出 motif velocity。scVelo 是 RNA velocity 方法，DynaVelo 是 multiome dynamic model。

DynaVelo 和 Dynamo 都关注 vector field 和动态解释，但 DynaVelo 的重点是把 chromVAR-derived motif accessibility 放进动态模型，而不是只在 RNA 空间里建模。

DynaVelo 和 scDiffEq 都使用深度连续动态建模的思想，但 DynaVelo 的区别是显式建模 RNA/motif 两个模态，并用 RNA-motif velocity consistency 把二者耦合。

因此 DynaVelo 的方法学定位可以概括为：RNA velocity supervision + multiome latent neural ODE + motif velocity + dynamic GRN/perturbation hypothesis generation。

### 12. 代码层面哪些部分是可验证的

根据 `doc_code.md`，公开仓库对核心模型机制支持较好，整体 fidelity 是 medium-high。可验证部分包括：

1. `MultiomeDataset` 返回 RNA expression、motif accessibility、scVelo velocity、velocity mask 和 cell-type weight。
2. `dynavelo/models.py` 中实现了 joint latent neural ODE。
3. encoder 推断 Normal initial states 和 Beta latent time。
4. observable velocities 通过 decoder Jacobian 乘 latent velocity 得到。
5. loss 包含 reconstruction、scVelo velocity cosine、velocity consistency 和 KL regularization。
6. evaluation 会把 latent time、velocities 和 uncertainty 写回 AnnData。
7. dynamic GRN 使用 finite-difference Jacobian。
8. perturbation 函数会生成 `delta_vx`、`delta_vy`、`delta_vz` 和 `delta_latent_time`。

不完整或需要谨慎的部分包括：

1. 公开仓库没有完整的 paper figure-generation notebooks/scripts。
2. Figure 6 的最终 rescue target scoring 脚本没有完整提供。
3. preprocessing notebook 使用本地绝对路径，不是可直接复现的 pipeline。
4. perturbation delta 的符号解释需要小心：公开函数存的是 `perturbed - original`，而论文中 knockout GRN interpretation 还涉及 delta negation；缺失的 downstream plotting/scoring code 可能处理了最终符号。

### 13. 这个方法最重要的假设

#### 13.1 Motif accessibility 可以作为 TF activity proxy

DynaVelo 的调控层不是直接测 TF 蛋白活性，而是用 chromVAR motif accessibility 表示 TF motif program。如果一个 TF motif 开放性增强，模型会把它当作 TF activity 相关信号。但 motif accessibility 也可能受 chromatin context、motif family redundancy、peak calling 和 smoothing 影响。

#### 13.2 RNA dynamics 和 motif dynamics 可以被同一个 latent ODE 解释

模型假设 RNA expression 和 motif accessibility 的变化可以被联合 latent vector field 捕捉。这在很多发育/命运转换系统中是合理的，但如果两个模态的时间尺度不同，或者 motif 变化和 RNA 变化不同步，velocity consistency loss 可能会强行对齐本来不同步的过程。

#### 13.3 scVelo velocity 提供了有用方向监督

DynaVelo 依赖 scVelo 作为 partial direction anchor。如果 scVelo velocity 在某个数据集或状态中很噪，DynaVelo 的方向学习也可能被影响。DynaVelo 的优势是不用完全依赖 scVelo，但它并不是完全摆脱 RNA velocity supervision。

#### 13.4 Dynamic GRN 和 perturbation 是模型敏感性，不是实验因果

Jacobian GRN 和 in silico perturbation 比普通相关性更有动态解释，但它们仍然是在已训练模型内部做局部扰动和敏感性分析。没有真实 perturb-seq、lineage tracing 或 functional validation 时，应表述为 hypothesis generation。

### 14. 如何用一句更准确的话描述 DynaVelo 结论

不够准确的说法：

> DynaVelo 证明某些 TF causally control GC B cell fate。

更准确的说法：

> DynaVelo 在 single-cell multiome 数据上学习 RNA expression 和 TF motif accessibility 的联合 latent neural ODE，并通过 RNA/motif velocity、dynamic GRN 和 in silico perturbation 生成关于 GC B cell fate regulation 的动态调控假设；这些假设与已知 GC biology 有一定一致性，但 rescue targets 仍需要实验验证。

### 15. 读 DynaVelo 结果时的检查清单

读一个 DynaVelo 分析结果时，建议依次问：

1. 输入 RNA 和 motif 矩阵是否来自同一批 aligned cells？
2. scVelo velocity 只在哪些 genes 上作为 supervision？
3. motif accessibility 是否经过合理的 TF/motif filtering？
4. latent time 是否只是 rank-normalized visualization，还是 raw Beta mean？
5. 某个 TF 的 motif velocity 是否和它的 RNA trend 一致，还是只在 chromatin 层变化？
6. dynamic GRN edge 是在哪个 cell state 或 latent-time region 中出现的？
7. perturbation delta 的符号定义是 `perturbed - original` 还是已经做过 negation？
8. rescue target 是否来自公开代码可复现脚本，还是论文中缺失的 downstream scoring？
9. 结论是已知生物学支持的动态解释，还是新的待验证假设？

### 16. 总结

DynaVelo 的核心贡献是把 RNA velocity 问题扩展成 multiome dynamic modeling 问题。它不只预测 RNA 表达接下来如何变化，还预测 TF motif accessibility 如何变化，并用一个 joint latent neural ODE 把二者耦合起来。

技术上，它通过 encoder 推断每个细胞的 initial latent state 和 latent time，用 neural ODE 学习连续 vector field，用 decoder Jacobian 把 latent velocity 转成 RNA/motif velocity，再通过 reconstruction、scVelo supervision、RNA-motif velocity consistency 和 KL regularization 共同训练。

解释上，它可以输出 trajectory、latent time、RNA velocity、motif velocity、dynamic GRN 和 perturbation/rescue hypotheses。但这些输出的证据强度不同：latent dynamics 和 velocity 是模型推断，dynamic GRN 是 learned vector field 的局部敏感性，rescue targets 是计算预测。最稳妥的使用方式是把 DynaVelo 看作一个强大的 hypothesis-generation framework，而不是直接因果验证工具。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## DynaVelo Summary

### Motivation and Novelty

DynaVelo addresses a central limitation of single-cell trajectory analysis: RNA-only velocity estimates are noisy, available for only a subset of genes, and miss chromatin-level TF activity that can drive fate decisions before expression changes are obvious. This is especially important in germinal center (GC) B cells, where rapid transitions between dark-zone proliferation, light-zone selection, recycling, apoptosis, and terminal differentiation are regulated by transcription factors and epigenetic regulators.

The method's novelty is a generative neural ODE that jointly models RNA expression and TF motif accessibility from single-cell multiome data. It uses scVelo RNA velocities as partial supervision, but learns a coupled RNA/motif vector field, predicts motif velocities, generates trajectories, computes dynamic GRNs, and simulates loss-of-function or rescue perturbations.

Compared methods include RNA velocity (Nature, 2018), scVelo (Nature Biotechnology, 2020), Dynamo (Cell, 2022), scDiffEq (Nature Methods, 2024), and chromVAR (Nature Methods, 2017). DynaVelo differs by integrating chromVAR-derived TF activity into the dynamical model instead of treating chromatin as a separate downstream annotation.

### Method Overview

DynaVelo takes two aligned matrices: log-normalized RNA expression $x(t)$ and TF motif accessibility $y(t)$. It also uses scVelo velocities for a subset of velocity genes. Encoders infer each cell's initial latent state $z(0)$ and latent time $t$, with Normal and Beta priors. A neural ODE evolves concatenated RNA and motif latent states, and decoders map latent states back to RNA and motif observations.

Observable RNA and motif velocities are computed by multiplying decoder Jacobians by latent velocities. Training combines reconstruction likelihood, cosine similarity to scVelo velocities, a velocity-consistency loss between RNA and motif velocity similarity structures, and KL regularization. After training, DynaVelo can generate trajectories, estimate finite-difference Jacobians for dynamic GRNs, and simulate perturbations by setting gene expression and, for TFs, motif accessibility to minimum observed values.

### Evaluation

The paper applies DynaVelo to murine GC B-cell multiome data across WT, Arid1aHet, CtcfHet, and related Arid1a samples. In WT GC B cells, DynaVelo recovers expected CB cell-cycle progression, CB-to-CC transition, CC recycling, and terminal exits. Its latent time appears more biologically coherent than scVelo's, especially for bifurcating CB/CC dynamics and motif-space ordering.

For TF analysis, DynaVelo identifies branch-specific RNA and motif accessibility dynamics for factors such as Spi1, Nfkb1, Runx1, Prdm1, Xbp1, Foxo1, Mef2b, Mef2c, and Pou2f2. In mutant GC B cells, it detects loss of CC-to-CB recycling and altered TF motif programs, including strong Arid1aHet changes in Foxp1, Bach2, Spi1, and Stat3 accessibility.

Dynamic GRN analyses recover known GC regulatory relationships and highlight edges lost or gained in mutants, such as disrupted Foxo1-to-Cxcr4 and Bcl6-to-Bcl2 behavior. In silico perturbation analyses nominate rescue candidates including Tox and Bcor for Arid1aHet and Pou2f2, Pax5, and Spi1 for CtcfHet.

The key caveat is that many evaluations are biological plausibility checks against known GC literature and model-derived velocity fields. The rescue targets are computational predictions, not experimentally validated interventions in this preprint.

### Reproducibility

Reproducibility rating: **3/5**.

The public repository contains the core DynaVelo implementation, a demo notebook, preprocessing notebook, environment file, selected logs, and selected CSV outputs. The central model mechanics match the paper well: joint latent ODE, latent time inference, decoder-Jacobian velocities, loss terms, Jacobian GRNs, and in silico perturbation are all verifiable in source.

However, the public repo is not a complete paper reproduction package. It lacks full figure-generation notebooks, trained checkpoints, processed AnnData files, and the final rescue-count scoring scripts used for Figure 6. Preprocessing notebooks use local absolute paths. Reproducing the main biological figures therefore requires downloading GEO data and rebuilding missing analysis scripts around the provided package.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
