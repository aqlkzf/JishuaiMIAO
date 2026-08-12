---
layout: default
permalink: /paper-atlas/archvelo-9b0ce848/
title: "ArchVelo"
nav: false
description: "ArchVelo = ATAC archetypal analysis + MultiVelo-style chromatin/RNA kinetics + archetype-wise velocity decomposition。 它先把 scATAC peak-summit 矩阵分解成少数 archetypes，然后对每个基因，把与该基因相关的 peaks 汇总成每个 archetype 的 gene weight，再用这些 ar…"
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
      <span>Nature Communications · 2026</span>
    </div>
    <h1>ArchVelo</h1>
    <p>ArchVelo: archetypal velocity modeling for single-cell multi-omic trajectories</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-74000-4" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ArchVelo 方法中文精读

### 这篇文章想解决什么问题？

ArchVelo 面向的是 paired scATAC+RNA-seq 数据：同一个细胞同时测到 RNA 表达和染色质可及性。作者要解决的问题是：只有静态单细胞快照时，怎样推断细胞沿什么方向运动，以及这些方向背后可能由哪些调控程序驱动。

传统轨迹推断常在 kNN 图上做无向的伪时间或轨迹排序，需要额外假设起点、终点或分支点；RNA velocity 利用 unspliced/spliced RNA 的比例来给轨迹加方向，但主要建模的是转录产物的动态 (`paper.md:34-38`)。MultiVelo 把 scATAC 也放进 velocity 模型里，但它把一个基因附近所有峰的可及性汇总成一个 chromatin signal，这会掩盖不同 enhancer/promoter 或不同上游调控程序对同一个基因的不同影响 (`paper.md:40-42`, `paper.md:58-60`)。

ArchVelo 的核心想法是：不要直接把所有 ATAC peaks 平均掉，而是先从 ATAC 矩阵中学习少数几个共享的 chromatin archetypes，把这些 archetypes 当作可解释的调控程序，再把它们放进 RNA velocity 的 ODE 模型里。

### 一句话概括

ArchVelo = **ATAC archetypal analysis** + **MultiVelo-style chromatin/RNA kinetics** + **archetype-wise velocity decomposition**。

它先把 scATAC peak-summit 矩阵分解成少数 archetypes，然后对每个基因，把与该基因相关的 peaks 汇总成每个 archetype 的 gene weight，再用这些 archetype signals 驱动 unspliced/spliced RNA 的动力学拟合。因为模型对 archetype contributions 是线性的，最后总 velocity 可以拆成多个 archetype-specific velocity components。

### 输入和输出

| 名称 | 论文符号 | 代码对象 | 含义 |
|---|---|---|---|
| 细胞数 | $N$ | AnnData observations | 每个细胞同时有 RNA 和 ATAC。 |
| ATAC peak-summit 矩阵 | $Y \in \mathbb{R}^{S \times N}$ | `XC_raw`, ATAC AnnData | $S$ 个 peak summits 在 $N$ 个细胞中的可及性。 |
| RNA 矩阵 | $X$ | `adata_rna.layers['Mu']`, `adata_rna.layers['Ms']` | unspliced 和 spliced RNA 层。 |
| archetype profiles | $A \in \mathbb{R}^{K \times N}$ | `XC`, `smooth_arch.layers['Mc']` | $K$ 个 archetype 在细胞上的活性曲线。 |
| peak loadings | $Z \in \mathbb{R}^{S \times K}$ | `S` | 每个 peak 如何由 $K$ 个 archetypes 表示。 |
| gene-level archetype weight | $z_k^g$ | `gene_weights.loc[:, g]` | 基因 $g$ 附近 peaks 对 archetype $k$ 的汇总权重。 |
| latent time | $t$ | `fit_t`, `new_times` | 细胞在某个基因动力学曲线上的时间位置。 |
| 输出 velocity | $v^g$, $v_k^g$ | `velo_s`, `velo_s_comp_k` | 总 spliced velocity 和第 $k$ 个 archetype 的 component velocity。 |

最终代码输出是一个 AnnData-like 对象，里面有总的 `u/s/a/velo_s` layers，也有 `u_comp_k`, `s_comp_k`, `a_comp_k`, `velo_s_comp_k` 等 component layers (`ArchVelo/src/ArchVelo/modeling.py:190-287`)。

### 第一步：用 archetypal analysis 表示 ATAC

论文把 ATAC peak-summit matrix 写作 $Y$，并做如下分解：

$$
\min_{Z,B}\|Y-ZA\|_F^2,\qquad A=BY
$$

约束是 $B \geq 0$, $Z \geq 0$, $B1=1$, $Z1=1$ (`paper.md:154-163`)。直观地说：

- $A$：$K$ 个 archetypes，每一行是一个 chromatin accessibility program 在所有细胞中的 profile。
- $Z$：每个 peak 对这些 archetypes 的 loading。
- $B$：让每个 archetype 本身由原始 peaks 的凸组合表示。

Fig. 1D 的本地图像也直接显示了 $Y \approx Z \times A$ 和这些非负/凸约束 (`images/46e6ea...jpg`)。

代码验证：`apply_AA_no_test` 调用 `create_archetypes_no_test`，后者调用 vendored `PCHA`，默认 `delta=0.1`, `init='furthest_sum'`，并输出 `XC` 和 `S` (`ArchVelo/src/ArchVelo/archetypal_regression/archetypes.py:9-28`, `ArchVelo/src/ArchVelo/archetypal_regression/archetypes.py:66-108`)。所以 AA-delta/PCHA 这一步在当前包里是核心实现。

### 第二步：从 peak loading 到 gene weight

论文对每个基因 $g$ 定义：

$$
z_k^g=\sum_{p\in P(g)} z_{pk}
$$

这里 $P(g)$ 是映射到基因 $g$ 的 peaks 集合 (`paper.md:60`, `paper.md:214`)。含义是：如果一个基因附近很多 peaks 都偏向 archetype $k$，那么该基因对 archetype $k$ 的调控权重就大。

代码里对应的是 `annotate_and_summarize`：它把 peak annotation 中的 `gene` 贴到 peak-loading 矩阵上，然后按 gene 聚合得到 `gene_weights` (`ArchVelo/src/ArchVelo/preprocessing.py:27-36`)。随后 `create_denoised_atac` 用 `XC_smooth @ gene_weights` 得到 gene-level 的 AA-denoised chromatin profile，并写入 `layers['Mc']` (`ArchVelo/src/ArchVelo/modeling.py:80-106`)。

注意一个实现细节：论文符号写的是 sum；当前代码中聚合使用的是 `groupby('gene').mean()`，之后在 `extract_ArchVelo_pars` 里又乘以 archetype 的动态范围 `(max_c - min_c)` (`ArchVelo/src/ArchVelo/modeling.py:172-177`)。因此读论文公式时要理解为方法思想；具体数值尺度由代码的 normalization 决定。

### 第三步：WNN 平滑 archetypes

论文说 MultiVelo-AA 和 ArchVelo 都先对 archetypes 做 weighted nearest neighbor smoothing (`paper.md:238-240`)。代码对应两层：

1. `gen_wnn` 对 RNA 做 PCA，对 ATAC/archetype matrix 做 LSI，然后通过 MultiVelo 的 `pyWNN` 计算 neighbor index 和 distance (`ArchVelo/src/ArchVelo/preprocessing.py:91-171`)。
2. `smooth_archetypes` 调用 `mv.knn_smooth_chrom`，把 archetypes 在 WNN 邻域里平滑，并写出 `arches.h5ad` (`ArchVelo/src/ArchVelo/preprocessing.py:38-52`)。

这一步的作用是降低 scATAC 的稀疏噪声，让每个 archetype profile 更适合作为动力学输入。

### 第四步：先跑 MultiVelo-AA 初始化

ArchVelo 不是完全从零拟合所有动力学参数。论文明确说先构造 MultiVelo-AA：

$$
\overline{c^g}=\sum_k z_k^g a_k
$$

然后用 MultiVelo-AA 初始化 latent time、transcription、splicing、degradation 参数 (`paper.md:238-240`)。

代码也这样做：

- `apply_MultiVelo_AA` 先生成 `gene_weights` 和 AA-denoised ATAC，然后调用 `mv.recover_dynamics_chrom(...)` (`ArchVelo/src/ArchVelo/modeling.py:108-120`)。
- `apply_ArchVelo_full` 也先调用 `mv.recover_dynamics_chrom(...)`，写出 `multivelo_result_denoised_chrom.h5ad`，再调用 `apply_ArchVelo` (`ArchVelo/src/ArchVelo/modeling.py:122-150`)。

所以当前包的实现可以理解为：**MultiVelo 提供初始时钟和动力学起点，ArchVelo 在此基础上把 chromatin/transcription 拆成多个 archetype components 重新拟合。**

#### 4.1 为什么必须先做初始化？

这一点对理解 ArchVelo 很重要：第四步不是一个可有可无的预处理，而是在给后面的高维 ODE 拟合提供“初始坐标系”。

如果只看 MultiVelo，一个基因 $g$ 主要面对一组三元动态：

```text
chromatin c^g(t) -> unspliced u^g(t) -> spliced s^g(t)
```

但 ArchVelo 把 chromatin/transcription 拆成 $K$ 个 archetype components。对同一个基因，它不再只拟合一个 chromatin 输入，而是拟合：

```text
a_1(t), a_2(t), ..., a_K(t)
       |
       v
u_1^g(t), ..., u_K^g(t)
       |
       v
s_1^g(t), ..., s_K^g(t)
```

这会让参数量明显增加。论文也明确说，因为 ArchVelo 比 MultiVelo 参数更多，所以需要先找一个合适初始化 (`paper.md:238-240`)。代码里能看到这种设计：`apply_ArchVelo_full` 先跑 `mv.recover_dynamics_chrom(...)`，再把结果交给 `apply_ArchVelo` (`ArchVelo/src/ArchVelo/modeling.py:122-127`)。

直观地说，MultiVelo-AA 给 ArchVelo 三类初始信息：

1. **时间轴**：每个细胞在每个基因上的初始 latent time，即 `full_res_denoised[:, gene_list].layers['fit_t']` (`ArchVelo/src/ArchVelo/modeling.py:161`)。
2. **RNA 动力学起点**：`fit_alpha`, `fit_beta`, `fit_gamma`, `fit_rescale_u`, `fit_t_sw1/2/3` 等参数，来自 `full_res_denoised.var[...]` (`ArchVelo/src/ArchVelo/modeling.py:169-170`)。
3. **可用于 velocity smoothing 的 RNA 邻接图**：后面 `_velocity_worker` 会用 `full_res_denoised.obsp['_RNA_conn']` 对 velocity 做平滑 (`ArchVelo/src/ArchVelo/modeling.py:204`)。

所以第四步可以记成一句话：**先用一个简化的 gene-level chromatin profile 把每个基因的时间和 RNA 参数粗略定出来，避免第五/六步在完全没有起点的情况下搜索。**

#### 4.2 MultiVelo-AA 到底把什么东西合并了？

前三步得到的是 $K$ 条 archetype 曲线 $a_k$ 和每个基因的 archetype 权重 $z_k^g$。MultiVelo-AA 先把这些 component 合成一个 gene-level chromatin profile：

$$
\overline{c^g}=\sum_k z_k^g a_k
$$

学习时可以把它想成：

```text
第 1 个 archetype 活性 a_1 乘基因权重 z_1^g
+ 第 2 个 archetype 活性 a_2 乘基因权重 z_2^g
+ ...
+ 第 K 个 archetype 活性 a_K 乘基因权重 z_K^g
= 基因 g 的一个合成 chromatin profile
```

代码中这件事发生在 `create_denoised_atac`：

```text
XC_smooth @ gene_weights -> atac_AA_denoised.layers['Mc']
```

这里 `XC_smooth` 是细胞 $\times$ archetype 的 smoothed archetype activity，`gene_weights` 是 archetype $\times$ gene 的 gene-level loading。矩阵乘法以后得到细胞 $\times$ gene 的 AA-denoised chromatin profile (`ArchVelo/src/ArchVelo/modeling.py:95-105`)。

这个合成 profile 是给 MultiVelo-AA 用的，不是 ArchVelo 最终的 component model。也就是说：

- 第四步的 `atac_AA_denoised.layers['Mc']`：每个基因只有一个合成 chromatin signal。
- 第五步的 `smooth_arch.layers['Mc']`：保留 $K$ 个 archetype signal，后面逐 component 建 ODE (`ArchVelo/src/ArchVelo/modeling.py:167`)。

这两个对象很容易混淆。记住区别以后，第四步和第五步的关系就清楚了：**第四步先把 components 合起来跑一次 MultiVelo；第五步再把 components 拆开做 ArchVelo。**

#### 4.3 第四步的输入、输出和后续合同

第四步输入：

| 输入 | 代码对象 | 作用 |
|---|---|---|
| RNA unspliced/spliced | `adata_rna.layers['Mu']`, `adata_rna.layers['Ms']` | MultiVelo-AA 要拟合的 RNA 观测。 |
| smoothed archetype activity | `XC_smooth` / `smooth_arch` | 构造 gene-level chromatin profile 的原料。 |
| gene weights | `gene_weights` | 告诉模型每个基因更受哪些 archetype 影响。 |
| WNN/RNA neighborhood | `nn_idx`, `nn_dist`, 后续 `_RNA_conn` | 降噪和平滑 velocity。 |

第四步输出的核心是 `full_res_denoised`。后面第五/六步主要从它取：

| 输出 | 代码读取位置 | 后面怎么用 |
|---|---|---|
| `fit_t` | `fit_t_arr = full_res_denoised[:, gene_list].layers['fit_t']` | 作为每个细胞的初始 latent time。 |
| `fit_alpha` | `var_df['fit_alpha']` | 初始化每个 component 的 transcription rate。 |
| `fit_beta` | `var_df['fit_beta']` | 初始化该基因共享的 splicing rate。 |
| `fit_gamma` | `var_df['fit_gamma']` | 初始化该基因共享的 degradation rate。 |
| `fit_t_sw1/2/3` | `var_df[...]` | 初始化 transcription activation/repression switch。 |
| `fit_rescale_u` | `var_df['fit_rescale_u']` | 让 predicted unspliced 和 observed unspliced 的尺度对齐。 |

这些字段在 `extract_ArchVelo_pars` 里被一次性取出来 (`ArchVelo/src/ArchVelo/modeling.py:159-177`)。因此第四步不是最终答案，而是给第五/六步规定了一个“起跑线”：

```text
MultiVelo-AA 输出 fit_t 和 gene-level 参数
        |
        v
ArchVelo 用这些值初始化每个 archetype component 的参数
        |
        v
再通过 joint optimization 调整参数和 latent time
```

#### 4.4 学习时最容易误解的地方

**误解 1：MultiVelo-AA 已经是 ArchVelo 的最终模型。**

不是。MultiVelo-AA 仍然只有一个 $\overline{c^g}$。它的主要作用是初始化；最终可解释的 `velo_s_comp_k`, `u_comp_k`, `s_comp_k`, `a_comp_k` 来自后面的 ArchVelo component fitting。

**误解 2：第四步的 $z_k^g$ 和第五步的 $\delta_k^g$ 是同一个数。**

不完全相同。$z_k^g$ 是 gene weight；第五步实际使用的强度还乘了 archetype dynamic range $n_k=\max(a_k)-\min(a_k)$。代码里是：

```text
gw_vals_scaled = gw_vals * (max_c - min_c)[:, None]
```

也就是论文里的 $\delta_k^g=z_k^g n_k$ (`paper.md:214`; `ArchVelo/src/ArchVelo/modeling.py:172-177`)。

**误解 3：第四步只给一个全局 latent time。**

代码读的是 `full_res_denoised[:, gene_list].layers['fit_t']`，形状可以理解为细胞 $\times$ 基因。也就是说，初始化阶段保留的是 gene-wise time assignments；第六步再根据 ArchVelo 的 component phase space 更新这些 times。

#### 4.5 第四步怎么接到第五步？

可以把第四步和第五步之间的接口写成下面这张表：

| 第四步产物 | 第五步/第六步消费方式 |
|---|---|
| `fit_t_arr[:, g]` | 给基因 $g$ 的每个细胞一个初始 `times`。 |
| `fit_alpha` | 复制成 $K$ 个 component 的初始 $\alpha_k^g$。 |
| `fit_beta`, `fit_gamma` | 作为所有 components 共享的 $\beta^g,\gamma^g$ 初值。 |
| `fit_t_sw1`, `fit_t_sw2/3` | 初始化 transcription switch 的开始和结束。 |
| `fit_rescale_u` | 补偿 unspliced 和 spliced 的尺度差异。 |
| `_RNA_conn` | 最后平滑 `velo_s` 和 `velo_s_comp_k`。 |

这也是为什么第四步必须先讲清楚：如果不知道这些变量从哪里来，第五步 ODE 里的 `times`, `pars`, `beta`, `gamma`, `t_sw1s` 会显得像凭空出现。

### 第五步：ArchVelo 的 ODE 模型

这一节最容易卡住，因为它突然从前面的矩阵分解跳到 ODE。先把衔接关系说清楚：

前四步已经准备好了三个东西：

1. **每个细胞在每个 archetype 上的 chromatin 活性**：$a_k(t)$，来自 AA 后的 smoothed archetype profile。代码里是 `smooth_arch.layers['Mc']`，再经过 `minmax` 变成 `c_all` (`ArchVelo/src/ArchVelo/modeling.py:167`)。
2. **每个基因对每个 archetype 的权重**：$z_k^g$，来自 gene-linked peaks 的聚合。代码里是 `gene_weights`，再乘以 archetype 动态范围 `(max_c - min_c)` 得到 `gw_vals_scaled` (`ArchVelo/src/ArchVelo/modeling.py:172-177`)。
3. **每个细胞、每个基因的初始时间和动力学参数**：来自第四步 MultiVelo-AA 的 `fit_t`, `fit_alpha`, `fit_beta`, `fit_gamma`, `fit_t_sw1/2/3` 等 (`ArchVelo/src/ArchVelo/modeling.py:159-170`)。

所以第五步不是重新从原始 ATAC/RNA 开始。它是在问：**如果第 $k$ 个 archetype 的 chromatin 活性随时间开关，那么它对基因 $g$ 的 transcription 贡献是多少；多个 archetype 的贡献加起来，能不能解释这个基因的 unspliced/spliced RNA？**

换成一条计算链就是：

```text
smoothed archetype a_k(t)
        +
gene weight z_k^g 和 dynamic range n_k
        |
        v
第 k 个 component 对基因 g 的 transcription input
        |
        v
unspliced u_k^g(t)
        |
        v
spliced s_k^g(t)
        |
        v
velocity v_k^g(t) = d s_k^g(t) / dt
```

#### 5.1 chromatin archetype 自己先按时间打开/关闭

论文把每个 archetype 的 chromatin dynamics 写成：

$$
\dot{a}_k(t)=\tau_k^{(c)}(t)\alpha_k^{(c)}-\alpha_k^{(c)}a_k(t)
$$

这里 $\tau_k^{(c)}(t)$ 表示 opening/closing 状态 (`paper.md:190-198`)。直观理解：

- 如果 $\tau_k^{(c)}(t)=1$，chromatin archetype 正在 opening，$a_k(t)$ 会朝 1 靠近。
- 如果 $\tau_k^{(c)}(t)=0$，chromatin archetype 正在 closing，$a_k(t)$ 会朝 0 衰减。
- $\alpha_k^{(c)}$ 控制靠近 1 或 0 的速度。

这一步只描述 archetype 的 chromatin 曲线本身，还没有进入 RNA。它对应代码里每个 component 的 chromatin switch：`calculate_exact_gene_layers` 里对每个 component `j` 取 `t2 = chrom_switches[j]`，并按 `t_sw` 把 latent time 分成不同状态 (`ArchVelo/src/ArchVelo/optimization.py:32-53`)。

#### 5.2 chromatin 怎么变成 unspliced RNA？

然后 unspliced RNA：

$$
\dot{u}^g(t)=\sum_{k=1}^{K}\tau_k^g(t)\alpha_k^g\delta_k^g a_k(t)-\beta^g u^g(t)
$$

这个式子是理解 ArchVelo 的关键。它不是说“ATAC 直接等于 RNA velocity”，而是说：chromatin archetype 先影响 transcription input，transcription input 再改变 unspliced RNA。

对某一个基因 $g$，第 $k$ 个 archetype 的输入项是：

$$
\tau_k^g(t)\alpha_k^g\delta_k^g a_k(t)
$$

逐项看：

- $a_k(t)$：第 $k$ 个 archetype 在时间 $t$ 的 chromatin 活性，也就是前面 AA/WNN 得到的动态程序。
- $\delta_k^g=z_k^g n_k$：这个 archetype 对基因 $g$ 有多重要。$z_k^g$ 来自第二步 gene weight，$n_k=\max(a_k)-\min(a_k)$ 是 archetype 动态范围 (`paper.md:214`)。代码里 `gw_vals_scaled = gw_vals * (max_c - min_c)[:, None]` 正是在做这件事 (`ArchVelo/src/ArchVelo/modeling.py:172-177`)。
- $\alpha_k^g$：如果该 archetype 对该基因处于激活期，它产生 transcription 的速率。
- $\tau_k^g(t)$：第 $k$ 个 archetype 对基因 $g$ 的 transcription 开关。它和 chromatin 开关不同：chromatin 可以先打开，RNA transcription 可以稍后开始或关闭。

后面的 $-\beta^g u^g(t)$ 是 unspliced RNA 被 splicing 消耗掉。也就是说，unspliced RNA 的变化由两股力量决定：前面 chromatin-driven transcription 在增加它，splicing 在减少它。

代码里这个 ODE 的速度项非常直接：`velocity_equations_njit` 计算 `vu = alpha * c - beta * u` (`ArchVelo/src/ArchVelo/optimization.py:274-276`)。这里的 `c` 就是某个 component 的 chromatin 状态，`alpha` 对应 $\alpha_k^g$，`beta` 对应 $\beta^g$。gene weight 没有塞进这个函数里，而是在外层乘上：`_velocity_worker` 对 `c/u/s/vs` 乘 `norm_const = gw_vals_scaled[:, i]`，再加总各 component (`ArchVelo/src/ArchVelo/modeling.py:31-62`)。

#### 5.3 unspliced 怎么变成 spliced velocity？

spliced RNA：

$$
\dot{s}^g(t)=\beta^g u^g(t)-\gamma^g s^g(t)
$$

这就是 RNA velocity 最熟悉的部分：spliced RNA 被 unspliced RNA 的 splicing 增加，被 degradation 减少。代码中对应 `vs = beta * u - gamma * s` (`ArchVelo/src/ArchVelo/optimization.py:274-276`)。

最终我们关心的 velocity 是：

$$
v^g(t)=\dot{s}^g(t)
$$

因此第五步的 ODE 输出不只是拟合曲线，而是直接产生后面用于 velocity graph 的 `velo_s`。

#### 5.4 为什么它和 MultiVelo 不一样？

MultiVelo-AA 在第四步只构造一个 gene-level chromatin profile：

$$
\overline{c^g}=\sum_k z_k^g a_k
$$

然后用这个单一 chromatin signal 初始化时间和参数 (`paper.md:238-240`)。ArchVelo 第五步进一步把这个和式拆开：不是只拟合一个 $\overline{c^g}$，而是让每个 archetype 都有自己的 component：

$$
\dot{u}_k^g(t)=\tau_k^g(t)\alpha_k^g\delta_k^g a_k(t)-\beta^g u_k^g(t)
$$

$$
\dot{s}_k^g(t)=\beta^g u_k^g(t)-\gamma^g s_k^g(t)
$$

然后再加和：

$$
u^g(t)=\sum_k u_k^g(t),\qquad s^g(t)=\sum_k s_k^g(t)
$$

论文特别强调：不能简单对每个 archetype 独立跑一次 MultiVelo，因为所有 components 共享同一个基因的 $\beta^g,\gamma^g$，而且 likelihood 是联合定义的 (`paper.md:230-234`)。代码中也能看到这一点：`err_all` 先用 `func_to_optimize` 得到每个 component 的 `u, s`，再用 `gn` 乘权重并 `np.sum(..., 1)` 加成总 `u_sum, s_sum`，最后用同一组 `beta/gamma` 拟合观测 `u/s` (`ArchVelo/src/ArchVelo/optimization.py:319-330`)。

#### 5.5 公式里的变量和代码里的变量怎么对应？

| 论文变量 | 直观含义 | 代码位置 |
|---|---|---|
| $a_k(t)$ | 第 $k$ 个 archetype 的 chromatin 活性曲线 | `smooth_arch.layers['Mc']`, `c_all` (`modeling.py:167`) |
| $z_k^g$ | 基因 $g$ 对 archetype $k$ 的 peak-loading 权重 | `gene_weights` (`modeling.py:172`) |
| $n_k$ | archetype 动态范围 | `max_c - min_c` (`modeling.py:172-177`) |
| $\delta_k^g$ | 加权后的 component 强度 | `gw_vals_scaled`, `gn` (`modeling.py:176`, `optimization.py:360-367`) |
| $\alpha_k^{(c)}$ | chromatin opening/closing rate | `alpha_cs`, `a_cs` (`optimization.py:335-340`) |
| $\alpha_k^g$ | component transcription rate | `alphas = pars[:num_comps]` (`optimization.py:15`, `optimization.py:291`) |
| $\beta^g$ | splicing rate，所有 components 共享 | `beta = pars[3*num_comps + 1]` (`optimization.py:18`) |
| $\gamma^g$ | degradation rate，所有 components 共享 | `gamma = pars[3*num_comps + 2]` (`optimization.py:19`) |
| $t$ | gene-specific latent time | `fit_t_arr`, `new_times`, `times` (`modeling.py:161`, `optimization.py:360-371`) |

#### 5.6 代码到底是在数值积分吗？

不是普通的逐步数值积分。论文说每个连续时间区间有 analytic solution (`paper.md:230-234`)；代码也用分段指数解：

- `calculate_exact_gene_layers` 对每个 component 计算 chromatin switch、transcription switch、每个细胞落在哪个时间段，然后返回 component-level 的 `c/u/s` 和 `vc/vu/vs` (`ArchVelo/src/ArchVelo/optimization.py:13-127`)。
- `predict_exp_mine` 写出分段指数解，里面有 `exp(-alpha_c*tau)`, `exp(-beta*tau)`, `exp(-gamma*tau)` (`ArchVelo/src/ArchVelo/optimization.py:146-195`)。
- `func_to_optimize` 在优化时用 anchor points 近似取出每个时间点的 `c/u/s`，供误差函数和 latent time 更新使用 (`ArchVelo/src/ArchVelo/optimization.py:289-317`)。

所以学习时可以把它理解为：**ODE 给出动力学方程；实现时不靠小步长积分，而是按开关区间使用解析指数解。**

#### 5.7 和第六、第七步的连接

第五步给出“给定时间和参数时，模型会预测什么”：

```text
给定 t, alpha_k^g, beta^g, gamma^g, chromatin switches
        |
        v
预测每个 component 的 c_k(t), u_k^g(t), s_k^g(t)
        |
        v
得到 component velocity v_k^g(t)
        |
        v
按 gene weight 加权并求和，得到总 u^g(t), s^g(t), v^g(t)
```

第六步就是反过来做拟合：调整参数和 latent time，让预测的总 `u/s` 和观测的 `Mu/Ms` 更接近，并让预测的 weighted archetype phase space 和观测接近。`optimize_all` 每轮先 `optimize_pars`，再用 KDTree 在 `[c_1,...,c_K,u,s]` 空间里把细胞重新分配到最近的 latent time (`ArchVelo/src/ArchVelo/optimization.py:360-397`)。

第七步则利用第五步天然保留下来的 component 结构：因为代码没有只保存总 `u/s/vs`，而是保存每个 component 的 `u_comp_k`, `s_comp_k`, `a_comp_k`, `velo_s_comp_k`，所以后面才能说“总 velocity 是哪些 archetype velocity 加出来的” (`ArchVelo/src/ArchVelo/modeling.py:210-287`)。

#### 5.8 一句话再压缩

第五步的本质是：**前四步把 ATAC 变成了少数 archetype 程序、gene weights 和初始 latent time；第五步把每个 archetype 程序当作一个 transcription driver，放进 chromatin -> unspliced -> spliced 的 ODE 级联里；第六步拟合这些参数和时间；第七步利用线性加和得到可解释的 component velocity。**

为了复习方便，核心变量再列一次：

- $a_k(t)$：第 $k$ 个 chromatin archetype 在 latent time 上的可及性。
- $\alpha_k^{(c)}$：第 $k$ 个 archetype 的 chromatin opening/closing rate。
- $\alpha_k^g$：基因 $g$ 上第 $k$ 个 archetype 的 transcription rate。
- $\tau_k^g(t)$：第 $k$ 个 archetype 对基因 $g$ 的 transcription 是否激活。
- $\delta_k^g=z_k^g n_k$：gene-level loading 乘以 archetype dynamic range。
- $\beta^g$：splicing rate。
- $\gamma^g$：degradation rate。

这些公式来自 `paper.md:190-231`。Fig. 2A 的图像也显示 chromatin archetypes 通过 $\sum_k \alpha_k^g z_k^g a_k$ 进入 transcription，然后经过 splicing 和 degradation (`images/af1922...jpg`)。

代码验证补充：

- `calculate_exact_gene_layers` 对每个 component 计算 switch times，调用解析解，返回每个 component 的 `c/u/s` 和 `vc/vu/vs` (`ArchVelo/src/ArchVelo/optimization.py:13-127`)。
- `predict_exp_mine` 实现分段指数解 (`ArchVelo/src/ArchVelo/optimization.py:146-195`)。
- `velocity_equations_njit` 直接计算 $\dot{u}=\alpha c-\beta u$ 和 $\dot{s}=\beta u-\gamma s$ (`ArchVelo/src/ArchVelo/optimization.py:260-278`)。

#### 5.9 从“一个基因、一个细胞、一个 component”开始理解

不要一开始就看全矩阵。先固定：

- 一个基因 $g$；
- 一个细胞 $i$；
- 一个 archetype component $k$。

这时第五步真正要回答的问题是：

```text
在细胞 i 的 latent time t_i 上，
第 k 个 archetype 的 chromatin 状态是多少？
它给基因 g 贡献多少 unspliced RNA？
这些 unspliced RNA 又会产生多少 spliced RNA velocity？
```

对应到代码变量：

| 数学对象 | 单点含义 | 代码对象 |
|---|---|---|
| $t_i$ | 细胞 $i$ 对基因 $g$ 的 latent time | `_extract_worker` 先按 `gene_idx` 取 `times = fit_t_arr_full[:, gene_idx]`，某个细胞的时间是 `times[cell_idx]` (`ArchVelo/src/ArchVelo/modeling.py:17-24`) |
| $a_k(t_i)$ | 第 $k$ 个 archetype 在该时间点的状态 | `c_all[:, k]` 或 `calculate_exact_gene_layers` 输出的 `c_out[:, k]` |
| $\delta_k^g$ | 该 archetype 对基因 $g$ 的强度 | `gn[k]` / `gw_vals_scaled[k, gene_idx]` |
| $u_k^g(t_i)$ | 第 $k$ 个 component 贡献的 unspliced | `u_out[cell_idx, k]`，后续写入 `u_comp_k` |
| $s_k^g(t_i)$ | 第 $k$ 个 component 贡献的 spliced | `s_out[cell_idx, k]`，后续写入 `s_comp_k` |
| $v_k^g(t_i)$ | 第 $k$ 个 component 的 spliced velocity | `vs_out[cell_idx, k]`，后续写入 `velo_s_comp_k` |

理解这个单点以后，再把 $i$ 扩展到所有细胞，把 $k$ 扩展到所有 archetypes，把 $g$ 扩展到所有基因，就是完整 ArchVelo。

#### 5.10 代码里的参数向量 `pars` 怎么读？

`calculate_exact_gene_layers(times, pars, chrom_switches, alpha_c, scale_cc, c0)` 一开始就把 `pars` 拆开 (`ArchVelo/src/ArchVelo/optimization.py:13-19`)：

```text
pars =
[
  alpha_0, ..., alpha_{K-1},
  t_sw1_0, ..., t_sw1_{K-1},
  diff_sw_rna_0, ..., diff_sw_rna_{K-1},
  rescale_u,
  beta,
  gamma
]
```

逐项解释：

- `alphas = pars[:num_comps]`：每个 component 的 transcription rate，对应 $\alpha_k^g$。
- `t_sw1s = pars[num_comps:2*num_comps]`：RNA transcription activation 的开始时间，对应 $t_k^{g,(i)}$。
- `diff_sw_rnas = pars[2*num_comps:3*num_comps]`：activation 到 repression 的时间差，所以代码里 `t3 = t1 + diff_sw_rnas[j]`。
- `pars[3*num_comps]`：`rescale_u`，用于把 predicted unspliced 的尺度调回观测尺度。
- `beta = pars[3*num_comps + 1]`：该基因共享的 splicing rate $\beta^g$。
- `gamma = pars[3*num_comps + 2]`：该基因共享的 degradation rate $\gamma^g$。

注意，chromatin 自己的参数没有放在 `pars` 的主体里，而是通过另一组参数传入：

```text
chrom_switches, alpha_cs, scale_ccs, c0s
```

这些来自 `optimize_chromatin` 对每个 archetype chromatin curve 的拟合 (`ArchVelo/src/ArchVelo/optimization.py:280-284`, `ArchVelo/src/ArchVelo/optimization.py:335-345`)。

所以一个基因 $g$ 的第五步参数可以分成两层：

```text
chromatin 层：每个 archetype 什么时候开/关、打开/关闭速度、初始状态
RNA 层：每个 archetype 什么时候启动 transcription、transcription 多快、共同 beta/gamma 是多少
```

#### 5.11 chromatin switch 和 transcription switch 是两套开关

论文里的 $\tau_k^{(c)}(t)$ 控制 chromatin opening/closing；$\tau_k^g(t)$ 控制该 archetype 对基因 $g$ 的 transcription 是否 active。这两套开关不一定同时发生。

代码里每个 component `j` 有三个关键时间：

```text
t1 = t_sw1s[j]             # RNA transcription activation
t2 = chrom_switches[j]     # chromatin opening -> closing switch
t3 = t1 + diff_sw_rnas[j]  # RNA transcription repression
```

然后代码比较 `t2` 和 `t3`：

- 如果 `t2 <= t3`，chromatin 先进入 closing，RNA repression 后发生，`m_type = 1`。
- 如果 `t2 > t3`，RNA 先 repression，chromatin 后 closing，`m_type = 2`。

这就是 `calculate_exact_gene_layers` 中 `t_sw = np.array([t1, t2, t3])` 或 `np.array([t1, t3, t2])` 的原因 (`ArchVelo/src/ArchVelo/optimization.py:32-47`)。

从学习角度看，这一步是在处理一种真实生物可能性：chromatin 的可及性变化和 RNA transcription 的启动/关闭可以有时间差。ArchVelo 不强行要求“chromatin 一开 RNA 马上开、chromatin 一关 RNA 马上关”，而是允许 component-specific delay。

#### 5.12 四个时间区间里分别在算什么？

代码用 `state_indices = np.searchsorted(...)` 给每个细胞的 `times` 分配状态 (`ArchVelo/src/ArchVelo/optimization.py:48-53`)。可以把每个 component 的时间轴粗略分成四段：

| 代码状态 | 直观阶段 | ODE 行为 |
|---|---|---|
| `s_idx == 0` | transcription 尚未启动 | 只计算 chromatin 前期变化，`cur_pred_r = False`，RNA 输出为 0。 |
| `s_idx == 1` | transcription active | chromatin 和 RNA 都按 active transcription 动态推进。 |
| `s_idx == 2` | 中间状态 | 如果 chromatin 已关闭，则 `chrom_open=False`；如果 RNA 已 repression，则 `alpha=0`。 |
| `s_idx == 3` | 后期关闭 | `vel_alpha=0`, `vel_open=False`，RNA 不再由该 component 新增，只剩 splicing/degradation 延续。 |

这解释了为什么代码里有很多看起来琐碎的 `if s_idx == ...`。它们不是任意分支，而是在把 piecewise ODE 的不同开关区间翻译成程序。

#### 5.13 `predict_exp_mine` 不是黑箱积分器

第五步的 ODE 容易让人以为代码在做小步长数值积分，例如 Euler 或 Runge-Kutta。这里不是。`predict_exp_mine` 直接写出每个连续时间区间的解析指数解 (`ArchVelo/src/ArchVelo/optimization.py:146-195`)。

学习时可以这样理解：

1. 在一个区间内，开关状态固定，比如 chromatin 正在 open、transcription 正在 active。
2. 开关固定以后，ODE 系数也固定。
3. 固定系数的一阶线性 ODE 可以写出指数解。
4. 到下一个 switch time，把上一段末尾的 `c,u,s` 当作下一段初始值继续算。

因此代码先计算 `c1,u1,s1`, `c2,u2,s2`, `c3,u3,s3` 这些 switch 边界值 (`ArchVelo/src/ArchVelo/optimization.py:55-75`)，再对每个细胞所在区间调用 `predict_exp_mine` (`ArchVelo/src/ArchVelo/optimization.py:76-107`)。

这也是为什么文档前面说“ODE 给出动力学方程，实现时用解析解”：第五步的数学和实现没有矛盾，只是实现没有用逐步积分。

#### 5.14 公式里的 $\delta_k^g$ 在代码里在哪里？

论文 Eq. 3 把 $\delta_k^g$ 写在 transcription 输入项里：

$$
\dot{u}^g(t)=\sum_k \tau_k^g(t)\alpha_k^g\delta_k^g a_k(t)-\beta^g u^g(t)
$$

但 `velocity_equations_njit` 里只看到：

```text
vu = alpha * c - beta * u
vs = beta * u - gamma * s
```

这不是缺失，而是实现位置不同。代码先计算“未按 gene weight 缩放”的 component curve，然后在外层乘以 `gn` / `norm_const`：

- 优化误差里：`u_sum = np.sum(u * gn, 1)`, `s_sum = np.sum(s * gn, 1)` (`ArchVelo/src/ArchVelo/optimization.py:319-330`)。
- 生成最终 velocity layer 时：`c *= norm_const`, `u *= norm_const`, `s *= norm_const`, `vs *= norm_const` (`ArchVelo/src/ArchVelo/modeling.py:47-50`)。

所以纸面公式是：

```text
component ODE 里面带 delta_k^g
```

代码实现是：

```text
先算标准 component curve
再把 component curve 乘以 delta_k^g
最后对 k 求和
```

两者在线性模型下等价。这个点很关键，因为它解释了为什么代码中的 `velocity_equations_njit` 看起来比论文公式少了一项。

#### 5.15 第五步和第六步的边界：模型预测 vs 参数学习

严格说，第五步定义“给定参数时如何预测”，第六步定义“怎样找到这些参数”。它们在代码里交织得比较紧：

```text
func_to_optimize / calculate_exact_gene_layers
        |
        v
给定 times 和 pars，预测 c/u/s

err_all / optimize_pars / optimize_all
        |
        v
调整 pars 和 times，让预测接近观测
```

第五步的核心输出是 predicted component states：

```text
c_out[:, k], u_out[:, k], s_out[:, k], vc_out[:, k], vu_out[:, k], vs_out[:, k]
```

第六步才用这些 predicted states 和观测值比较。这里要分清两件事：

```text
observed:  u_all_orig, s_all_orig, c_all
predicted: u_sum, s_sum, c
```

`err_all` 里的显式误差主要是 RNA 部分：

```text
(u_sum - observed u)^2 + (s_sum - observed s)^2
```

而 chromatin components 主要进入 `optimize_all` 的 latent-time reassignment：代码把预测的 `[c_1, ..., c_K, u_sum, s_sum]` 和观测的 `[weighted c_1, ..., weighted c_K, u, s]` 放在同一个 phase space 里，用 KDTree 重新给细胞分配最近的时间 (`ArchVelo/src/ArchVelo/optimization.py:386-394`)。所以当前包里这更像“RNA 参数误差 + chromatin/RNA phase-space 时间更新”的组合，而不是一个单独显式写出的完整 Eq. 6 likelihood。

所以学习时不要把两个问题混在一起：

- **第五步问**：如果参数已知，曲线和 velocity 怎么算？
- **第六步问**：参数和 latent time 应该怎么更新，才能让曲线贴近数据？

#### 5.16 最终为什么能得到 `velo_s_comp_k`？

第五步保留了每个 component 的 $v_k^g(t)=\dot{s}_k^g(t)$。后面 `_velocity_worker` 返回：

```text
'vs_comps': 每个 component 的 smoothed spliced velocity
'vs_no_sm_comps': 每个 component 的 unsmoothed spliced velocity
'vs': 所有 components 求和后的 smoothed total velocity
'vs_no_sm': 所有 components 求和后的 raw total velocity
```

然后 `velocity_result` 把它们写成 AnnData layers (`ArchVelo/src/ArchVelo/modeling.py:222-282`)：

| 输出 layer | 含义 |
|---|---|
| `velo_s` | 所有 components 加和并 RNA-neighbor 平滑后的总 spliced velocity。 |
| `velo_s_no_sm` | 未平滑的总 spliced velocity。 |
| `velo_s_comp_k` | 第 $k$ 个 archetype component 的 spliced velocity。 |
| `velo_s_no_sm_comp_k` | 第 $k$ 个 component 未平滑 velocity。 |
| `u_comp_k` | 第 $k$ 个 component 贡献的 unspliced profile。 |
| `s_comp_k` | 第 $k$ 个 component 贡献的 spliced profile。 |
| `a_comp_k` | 第 $k$ 个 component 贡献的 chromatin profile。 |
| `velo_s_comp_k_norm` | 用总 velocity 的平均绝对值归一化后的 component velocity。 |

这就是 ArchVelo 相比 MultiVelo 更可解释的关键：模型不是只输出一个总方向，而是把总方向拆成了多个 archetype program 的方向贡献。

#### 5.17 建议的源码阅读顺序

如果你要自己跟代码学习第五步，按这个顺序读最省力：

1. `modeling.py:122-150`：看 `apply_ArchVelo_full`，确认先 MultiVelo-AA 再 ArchVelo。
2. `modeling.py:154-188`：看 `extract_ArchVelo_pars`，确认 `fit_t`, `fit_alpha/beta/gamma`, `gene_weights`, `c_all` 怎么进入优化。
3. `optimization.py:360-397`：看 `optimize_all`，确认参数优化和 latent time 更新的大循环。
4. `optimization.py:335-358`：看 `optimize_pars`，确认 MultiVelo-AA 的参数如何变成 ArchVelo 的初值。
5. `optimization.py:13-127`：看 `calculate_exact_gene_layers`，逐段理解 component ODE 的 switch logic。
6. `optimization.py:260-278`：看 `velocity_equations_njit`，确认最终 velocity 公式。
7. `modeling.py:190-287`：看 `velocity_result`，确认 total layers 和 component layers 怎么写回 AnnData。

读完这条链，第五步就可以总结为：**给定每个细胞的时间、每个 component 的 chromatin/RNA 开关和速率，ArchVelo 用解析 ODE 计算每个 component 的 $c/u/s/v$，再按 gene weight 缩放并加和，得到总 RNA velocity，同时保留 component velocity。**

### 第六步：参数优化和 latent time 更新

论文说 ArchVelo 使用 adapted EM：M-step 更新参数，E-step 给细胞重新分配 latent time；chromatin 参数用 scipy dual annealing，RNA 参数用 Nelder-Mead，E-step 在 $(K+2)$ 维 phase space 里做最近邻分配 (`paper.md:266-270`)。

#### 6.1 为什么这里叫 EM？

ArchVelo 里有两类未知量：

1. **模型参数 $\theta$**：chromatin opening/closing 参数、transcription switch 和 rate、splicing rate $\beta^g$、degradation rate $\gamma^g$。
2. **latent time $t_i$**：每个细胞应该落在该基因动力学曲线的哪个时间点。

这两个东西互相依赖：

- 如果知道每个细胞的 $t_i$，就可以拟合最能解释这些细胞 $u/s/a$ 观测的 ODE 参数。
- 如果知道 ODE 参数，就可以沿着模型曲线找每个细胞最像哪个时间点，从而更新 $t_i$。

所以论文采用一种 adapted expectation-maximization：

```text
固定 latent time -> 更新 ODE 参数        # M-step
固定 ODE 参数   -> 重新分配 latent time # E-step
重复几轮
```

这里的 EM 不是教科书里有隐变量后验分布闭式更新的那种 EM，而是更工程化的 alternating optimization：参数更新用数值优化，time 更新用最近邻搜索。

#### 6.2 论文里的目标函数在比较什么？

论文先定义每个细胞的观测向量：

$$
\mathbf{x_i}=(u_i, s_i, \widetilde{a}_{1,i}, \ldots, \widetilde{a}_{K,i})
$$

其中：

$$
\widetilde{a}_{g}^{k}=w_c\delta_k^g a_g^k
$$

也就是把第 $k$ 个 archetype 的 chromatin signal 乘上两个权重：

- $\delta_k^g$：这个 archetype 对基因 $g$ 的强度。
- $w_c$：chromatin 项在拟合中的权重。

模型预测向量是：

$$
\mathbf{f}(t_i,\theta)=(\widehat{u}_i, \widehat{s}_i, \widehat{\widetilde{a}}_{1,i}, \ldots, \widehat{\widetilde{a}}_{K,i})
$$

论文 Eq. 6 的本质就是最小化观测和预测的平方距离 (`paper.md:252-264`)：

$$
\sum_i\left[
(u_i-\widehat{u}_i)^2
+(s_i-\widehat{s}_i)^2
+w_c^2\sum_{k=1}^{K}\left(\delta_k^g(a_{k,i}-\widehat{a}_{k,i})\right)^2
\right]
$$

所以 EM step 的目标可以直观理解为：

```text
让模型曲线同时贴近三类东西：
1. observed unspliced u
2. observed spliced s
3. weighted archetype chromatin states a_1 ... a_K
```

这也是为什么 E-step 不是在普通 $(u,s)$ 平面里找最近点，而是在 $(K+2)$ 维空间里找：

```text
[a_1, a_2, ..., a_K, u, s]
```

#### 6.3 第六步的输入从哪里来？

对每个基因 $g$，`extract_ArchVelo_pars` 会准备好 `optimize_all` 需要的输入 (`ArchVelo/src/ArchVelo/modeling.py:154-188`)：

| 输入 | 形状直觉 | 来源 | 用途 |
|---|---|---|---|
| `u_all_orig` | 细胞数 | `adata_rna[:, gene].layers['Mu']` | 观测 unspliced。 |
| `s_all_orig` | 细胞数 | `adata_rna[:, gene].layers['Ms']` | 观测 spliced。 |
| `c_all` | 细胞数 $\times K$ | `smooth_arch.layers['Mc']` min-max 后结果 | 观测 archetype chromatin curves。 |
| `new_times` | 细胞数 | `full_res_denoised[:, gene].layers['fit_t']` | MultiVelo-AA 给的初始 latent time。 |
| `gn` | $K$ | `gw_vals_scaled[:, gene]` | $\delta_k^g=z_k^g n_k$，component 强度。 |
| `var_row` | 一个 gene 的参数行 | `fit_t_sw1/2/3`, `fit_alpha`, `fit_beta`, `fit_gamma` 等 | MultiVelo-AA 参数初值。 |
| `weight_c` | 标量 | `apply_ArchVelo(..., weight_c=0.3)` | Eq. 6 中 chromatin 项权重。 |

`_extract_worker` 对每个 gene 取出这些向量，然后调用 `optimize_all(...)` (`ArchVelo/src/ArchVelo/modeling.py:17-24`)。因此 EM 是 **gene-wise** 做的：每个基因有自己的 `u/s/times/pars`，但共享同一套 archetype curves `c_all`。

#### 6.4 外层循环：`optimize_all`

代码里的 EM-like 外层循环在 `optimize_all` (`ArchVelo/src/ArchVelo/optimization.py:360-397`)：

```text
x0 = None
for i in range(max_outer_iter):
    times = new_times.copy()
    pars, ... = optimize_pars(..., times, ...)

    if i < max_outer_iter - 1:
        用当前 pars 预测 c/u/s
        在 [c_1,...,c_K,u,s] 空间里建 KDTree
        给每个细胞找最近的模型点
        new_times = target_times[idx]
        x0 = pars
```

默认上层参数是 `max_outer_iter=3`, `method='Nelder-Mead'`, `update_mode='cells'` (`ArchVelo/src/ArchVelo/modeling.py:122-130`)。也就是说，代码通常只做少数几轮 alternating update，而不是一直迭代到严格收敛。

#### 6.5 M-step 第一部分：先拟合 chromatin dynamics

论文说 M-step 先拟合 Eq. 2 的 chromatin 参数，用 scipy dual annealing (`paper.md:266-270`)。代码对应：

```python
for j in range(num_comps):
    c_sw[j], a_cs[j], s_ccs[j], c0s[j] = optimize_chromatin(t_np, c_all[:, j])
```

这里 `j` 是 archetype component (`ArchVelo/src/ArchVelo/optimization.py:335-345`)。

`optimize_chromatin` 里优化的是：

```text
switch, alpha_c, scale_cc, c0
```

对应含义：

| 代码变量 | 直观含义 |
|---|---|
| `switch` / `c_sw[j]` | chromatin 从 opening 转到 closing 的时间 $t_k^{(c)}$。 |
| `alpha_c` / `a_cs[j]` | chromatin opening rate。 |
| `scale_cc` / `s_ccs[j]` | closing rate 相对 opening rate 的缩放。论文为简化写 opening/closing mirror，代码实际允许 closing scale。 |
| `c0` / `c0s[j]` | 初始 chromatin 状态。 |

它最小化的是 `err_chrom`：

```text
sum((observed c - predicted c)^2)
```

其中 predicted chromatin 由 `solve_for_chromatin` 的指数形式给出 (`ArchVelo/src/ArchVelo/optimization.py:129-143`, `ArchVelo/src/ArchVelo/optimization.py:280-284`)。

学习时可以把这一小步理解成：**在当前 latent time 排列下，先给每个 archetype 单独拟合一条 opening/closing chromatin 曲线。**

#### 6.6 M-step 第二部分：再拟合 RNA kinetics

chromatin 参数确定后，`optimize_pars` 继续拟合 RNA 相关参数：

```text
alpha_0 ... alpha_{K-1}
t_sw1_0 ... t_sw1_{K-1}
diff_sw_rna_0 ... diff_sw_rna_{K-1}
rescale_u
beta
gamma
```

初值来自第四步 MultiVelo-AA：

```python
x0 = np.array(
    [var_row['fit_alpha']]*num_comps
    + starts
    + fins
    + [var_row['fit_rescale_u'], var_row['fit_beta'], var_row['fit_gamma']]
)
```

也就是说：

- MultiVelo-AA 的 `fit_alpha` 被复制成 $K$ 个 component 的初始 transcription rate。
- MultiVelo-AA 的 `fit_beta`, `fit_gamma` 作为该基因共享的 splicing/degradation 初值。
- `fit_t_sw1/2/3` 给 transcription activation/repression switch 提供初始范围 (`ArchVelo/src/ArchVelo/optimization.py:347-354`)。

然后代码调用：

```python
scipy.optimize.minimize(..., method=method)
```

默认 `method='Nelder-Mead'` (`ArchVelo/src/ArchVelo/optimization.py:356-358`)。

这里被最小化的是 `err_all`：

```text
u_sum = sum_k u_k * gn_k
s_sum = sum_k s_k * gn_k
loss = sum((u_sum * rescale_u - observed_u_scaled)^2)
     + sum((s_sum - observed_s)^2)
```

代码位置是 `ArchVelo/src/ArchVelo/optimization.py:319-330`。注意这里的 `beta` 和 `gamma` 是所有 components 共享的；这就是论文说不能对每个 archetype 独立跑 MultiVelo 的原因。

#### 6.7 M-step 里的 bounds 怎么理解？

`optimize_pars` 构造了一个 bounds 列表 (`ArchVelo/src/ArchVelo/optimization.py:347-348`)：

```text
[(0, 300)] * K
+ [(switch_neg[j], c_sw[j])] * K
+ [(0, 20 - switch_neg[j])] * K
+ [(1e-12, 2), (1e-12, 5), (1e-12, 20)]
```

按 `pars` 的顺序解释：

| 参数块 | bounds | 含义 |
|---|---|---|
| `alpha_k^g` | `0..300` | component transcription rate 非负，允许较大值。 |
| `t_sw1_k` | `switch_neg[j]..c_sw[j]` | transcription activation 不应晚于 chromatin switch。 |
| `diff_sw_rna_k` | `0..20-switch_neg[j]` | repression time = activation time + duration，duration 非负。 |
| `rescale_u` | `1e-12..2` | unspliced 尺度校正。 |
| `beta` | `1e-12..5` | splicing rate 正数。 |
| `gamma` | `1e-12..20` | degradation rate 正数。 |

`switch_neg` 是根据 chromatin 初始状态和 opening rate 算出的一个允许的早期下界 (`ArchVelo/src/ArchVelo/optimization.py:339-344`)。这不是论文里单独展开的概念，而是代码为了让 switch time 搜索范围合理而加的实现细节。

#### 6.8 E-step：用 KDTree 更新 latent time

M-step 得到当前参数后，E-step 固定这些参数，重新给每个细胞分配 time。

代码先用当前参数预测模型曲线：

```python
c, u, s = func_to_optimize(c_sw, a_cs, s_ccs, c0_s, pars, times)
```

如果 `update_mode == 'grid'`，代码会用 `np.linspace(0, 20.0, n_anchors)` 构造均匀 anchor times；否则默认 `update_mode='cells'`，使用当前细胞的 `times` 作为 candidate time (`ArchVelo/src/ArchVelo/optimization.py:376-384`)。

然后把预测值缩放到和观测空间一致：

```text
c = c * gn * weight_c / scale_c
u = u * gn * resc_u
s = s * gn
u_sum = sum_k u_k
s_sum = sum_k s_k
```

这里的 `c` 保留 $K$ 个 component 维度；`u` 和 `s` 会先按 component 加权，再对 $K$ 个 component 求和 (`ArchVelo/src/ArchVelo/optimization.py:386-390`)。

接着建立 KDTree：

```python
tree = KDTree(concat([c_1, ..., c_K, u_sum, s_sum]))
```

再用观测向量查询最近点：

```python
query = concat([weighted observed c_1, ..., weighted observed c_K, observed u, observed s])
_, idx = tree.query(query)
new_times = target_times[idx]
```

这就是论文说的 $(K+2)$ 维 phase space：$K$ 个 archetype chromatin dimensions，加上 summed unspliced 和 summed spliced 两个 RNA dimensions (`paper.md:270`; `ArchVelo/src/ArchVelo/optimization.py:390-394`)。

学习时可以想象成：模型曲线在 $(K+2)$ 维空间里画出一条轨迹；每个真实细胞也在这个空间里有一个点；E-step 把细胞投到离它最近的模型轨迹点上，那个轨迹点的 time 就成为新的 latent time。

#### 6.9 `weight_c` 和尺度归一化在 E-step 里做什么？

因为 chromatin 和 RNA 的数值尺度不同，直接拼接 `[c_1,...,c_K,u,s]` 会让尺度大的变量主导最近邻距离。代码做了两件事：

1. `scale_c = std(sum(c_all * gn)) / std(s_all_orig)`：把 chromatin 总尺度和 spliced RNA 尺度拉到相近范围。
2. `weight_c`：额外控制 chromatin 在 time assignment 里的影响强度。

对应代码：

```text
c_all_scaled = (c_all * gn / scale_c) * weight_c
c_pred_scaled = c_pred * gn * weight_c / scale_c
```

(`ArchVelo/src/ArchVelo/optimization.py:361-367`, `ArchVelo/src/ArchVelo/optimization.py:386-392`)。

论文说 ArchVelo 选择 $w_c=0.3$ 作为默认参数 (`paper.md:264`)；代码 `apply_ArchVelo` 默认也是 `weight_c=0.3` (`ArchVelo/src/ArchVelo/modeling.py:130`)。

#### 6.10 anchor points：论文和代码的细节差异

论文写 E-step 可以维护 uniformly spaced anchor points，默认 500 个 (`paper.md:270`)。

当前代码里有两个相关但不同的概念：

1. `func_to_optimize` 内部调用 `anchor_points(t_sw, 20, 500, return_time=True)`，用于在 switch intervals 上生成解析解采样点，再把给定 `times` 映射到最近 anchor (`ArchVelo/src/ArchVelo/optimization.py:309-315`)。
2. `optimize_all` 的 E-step 如果 `update_mode == 'grid'`，会使用 `np.linspace(0, 20.0, n_anchors)`；但 `_extract_worker` 传入的是 `n_anchors=1000`，而默认 `update_mode='cells'` 时并不走这个 uniform grid (`ArchVelo/src/ArchVelo/modeling.py:17-24`, `ArchVelo/src/ArchVelo/optimization.py:360-384`)。

所以更准确的代码边界是：**论文描述的是概念上的 anchor-point E-step；当前包默认更像在已有 cell times 上做最近邻 reassignment，另有 grid 模式可用，但默认数量和论文 500 的叙述不完全一致。**

#### 6.11 一轮 EM-like 更新的完整计算链

把一轮写成学习版伪代码：

```text
输入：
  observed u, observed s
  observed archetype chromatin c_1...c_K
  current latent time t
  gene weights gn = delta_1^g...delta_K^g
  MultiVelo-AA 初始参数

M-step:
  1. 对每个 archetype k:
       用 current t 拟合 chromatin curve
       得到 c_sw[k], alpha_c[k], scale_cc[k], c0[k]
  2. 固定 chromatin 参数:
       用 Nelder-Mead 拟合 alpha_k^g, RNA switches, rescale_u, beta, gamma
       loss 主要比较 predicted summed u/s 和 observed u/s

E-step:
  3. 用更新后的参数生成模型轨迹点:
       predicted c_1...c_K, u_sum, s_sum
  4. 构造观测点:
       weighted observed c_1...c_K, observed u, observed s
  5. 在 K+2 维 phase space 里用 KDTree 找最近模型点
  6. 把每个细胞的 time 更新为最近模型点的 time

下一轮：
  用新的 t 继续 M-step
```

#### 6.12 最后返回了什么？

`optimize_all` 最终返回：

```python
return pars, times, (c_sw, a_cs, s_ccs, c_on, c0_s)
```

这些返回值后面会被 `_velocity_worker` 消费：

- `pars`：RNA/transcription 参数，包括 $\alpha_k^g$, switch differences, `rescale_u`, $\beta^g$, $\gamma^g$。
- `times`：最后一轮使用的 latent time。
- `(c_sw, a_cs, s_ccs, c_on, c0_s)`：chromatin switch/rate/initial-state 参数。

然后 `_velocity_worker` 调用 `calculate_exact_gene_layers` 生成最终的 `c/u/s/vs` component layers (`ArchVelo/src/ArchVelo/modeling.py:26-74`)。

#### 6.13 证据边界：论文 EM vs 当前代码

这里要保留 `Partial` 判断，不要把代码说得比证据更完整：

- 论文 Eq. 6 写的是包含 chromatin、unspliced、spliced 的 Gaussian likelihood (`paper.md:252-264`)。
- 当前代码的 `err_all` 显式优化的是 summed `u/s` 的平方误差；chromatin 项主要通过单独的 `optimize_chromatin` 和 KDTree phase-space reassignment 进入 (`ArchVelo/src/ArchVelo/optimization.py:319-330`, `ArchVelo/src/ArchVelo/optimization.py:335-397`)。
- 论文描述 E-step 默认 500 anchor points；当前代码默认 `update_mode='cells'`，另有 `grid` 模式和内部 500-point curve sampling。
- 因此可以说：**代码实现了与论文 EM 思路一致的 bounded EM-like alternating loop，但没有找到一个单独完整实现 Eq. 6 的 objective。**

### 第七步：为什么 velocity 可以分解？

ArchVelo 最重要的新功能来自线性结构。论文写：

$$
u^g(t)=\sum_k u_k^g(t),\qquad s^g(t)=\sum_k s_k^g(t)
$$

因此：

$$
v^g(t)=\dot{s}^g(t)=\sum_k \dot{s}_k^g(t)=\sum_k v_k^g(t)
$$

(`paper.md:90-108`, `paper.md:242-250`)。

直观理解：一个细胞的总 velocity 是很多调控程序同时施加的合力。ArchVelo 把这个合力拆开，得到每个 archetype 单独贡献的方向。Fig. 5 的本地图像显示 dashed component curves 可以加和成 total spliced curve 和 total velocity curve (`images/6ffe68...jpg`, `images/e58d34...jpg`)。

代码验证：

- `_velocity_worker` 得到每个 component 的状态和 velocity，再算 total sum (`ArchVelo/src/ArchVelo/modeling.py:26-74`)。
- `velocity_result` 写入总 layers 和每个 component 的 layers，例如 `velo_s_comp_0`, `u_comp_0`, `s_comp_0`, `a_comp_0` (`ArchVelo/src/ArchVelo/modeling.py:190-287`)。
- `generate_decomposition` 把单个基因的 component traces 整理成适合画图的长表 (`ArchVelo/src/ArchVelo/modeling.py:289-358`)。

这部分是论文创新点与代码实现匹配最强的地方。

### 论文如何评估？

论文主要用三类证据：

1. **u-s phase-space likelihood**：看模型对 unspliced/spliced 关系拟合得好不好。`evaluation.py` 有 ArchVelo、MultiVelo、scVelo 的 likelihood helper (`ArchVelo/src/ArchVelo/evaluation.py:10-59`, `ArchVelo/src/ArchVelo/evaluation.py:129-163`)。
2. **latent time consistency**：看不同基因推断出的 latent time 是否更一致。论文方法里用 Spearman correlation profile 和 silhouette score (`paper.md:272-274`)。
3. **CBDir**：看 velocity 方向是否指向人工整理的正确 cell-type transition。`metrics.py` 实现了 cross-boundary correctness：比较 embedding 上 velocity 向量与 source-to-target neighbor displacement 的 cosine similarity (`ArchVelo/src/ArchVelo/metrics.py:69-132`)。

图像证据：

- Fig. 3 mouse brain 里，ArchVelo 的 likelihood、latent-time silhouette 和 mean CBDir 都优于多数或全部 baseline（本地图像 `27653f...jpg`；论文 `paper.md:62-70`）。
- Fig. 4 HSC 里也显示类似趋势（本地图像 `729d3b...jpg`；论文 `paper.md:72-80`）。
- Fig. 5 显示 mouse brain 中 A5 更像 cell-cycle component，A8 更像 astrocyte differentiation component (`paper.md:110-116`)。
- Fig. 7-8 显示 CD8 T cell 中 cell cycle、functional differentiation 和 Ccr6- 到 Ccr6+ progenitor 轨迹 (`paper.md:118-134`)。

### 代码验证、论文主张和缺失证据要分开看

#### 代码已经验证的部分

- AA/PCHA archetype learning：`archetypes.py`。
- gene weights 和 WNN smoothing：`preprocessing.py` / `modeling.py`。
- MultiVelo-AA bootstrap：`modeling.py`。
- ArchVelo ODE exact solution 和 velocity equations：`optimization.py`。
- component velocity layers 和 decomposition：`modeling.py`。
- u-s likelihood helper 和 CBDir metric：`evaluation.py`, `metrics.py`。

#### 论文和图支持，但当前 repo 没有完整复现代码的部分

- HSC 和 CD8 的完整 figure-generation notebooks。论文和 README 都指向外部 `ArchVelo_notebooks` (`paper.md:376-380`, `ArchVelo/README.md:26-31`)。
- TF motif analysis / TF nomination。论文 Methods 写了 motifmatchr、$Y^T M$、$Z^T M$ 和 motif correlation scores (`paper.md:316-320`)，Fig. 6/Fig. 8 的图像也显示 motif heatmaps；但是当前 `ArchVelo/README.md` 和 `ArchVelo/src/**` 中没有找到一等的 motif/TF-ranking 实现。

#### 部分匹配

- RNA-from-ATAC regression：代码有 3-fold CV 和 50 个 ridge alpha grid 的实现 (`ArchVelo/src/ArchVelo/archetypal_regression/archetypes_regression.py:139-350`)，但当前可见的 `apply_AA` helper 使用 75/25 split，而论文写 66.7%/33.3% split (`paper.md:178-186`, `ArchVelo/src/ArchVelo/archetypal_regression/archetypes.py:43-51`)。
- Eq. 6 full likelihood：代码有 u-s likelihood 和 chromatin/RNA fitting 逻辑，但没有找到一个单独完整实现 paper Eq. 6 chromatin-weighted Gaussian likelihood 的 objective。

### 学习时最应该抓住的主线

如果只记一条主线，可以这样理解：

```text
ATAC peaks 太稀疏、太高维
        |
        v
用 AA 学 K 个共享 chromatin archetypes
        |
        v
把每个基因附近 peaks 汇总成 archetype weights
        |
        v
用 MultiVelo-AA 初始化时间和动力学参数
        |
        v
每个基因拟合 K 个 archetype transcription components
        |
        v
总 velocity = 所有 component velocities 的和
        |
        v
单独看 component velocity，可解释不同调控程序驱动的轨迹
```

ArchVelo 的贡献不是简单“加了 ATAC”，而是把 ATAC 变成一组可共享、可分解、可解释的动态调控程序。它的强点是核心 kinetic/decomposition 逻辑清楚，代码中也能看到 component layers 的落地；它的弱点是线性假设、基因逐个拟合，以及当前包内缺少完整 manuscript notebooks 和 motif workflow。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## ArchVelo Summary

### Paper

**ArchVelo: archetypal velocity modeling for single-cell multi-omic trajectories** by Avdeeva, Walker, van der Veeken, Rudensky, and Pritykin. The OCR header records receipt on 30 September 2025, acceptance on 26 May 2026, and DOI `10.1038/s41467-026-74000-4` (`paper.md:1-11`). The acquisition used the unedited Nature reference PDF, so small copy-editing differences may remain in the OCR text.

### Problem

ArchVelo addresses trajectory inference from paired scATAC+RNA-seq data. Standard trajectory methods often rely on undirected similarity graphs and extra assumptions about roots or endpoints, while RNA velocity methods add direction through unspliced/spliced RNA kinetics (`paper.md:34-38`). MultiVelo brought chromatin accessibility into RNA velocity, but it summarizes all peaks linked to a gene into a single chromatin profile, which can hide distinct regulatory elements and upstream programs (`paper.md:40-42`, `paper.md:58-60`).

### Proposed Method

ArchVelo represents the scATAC modality with archetypal analysis. It decomposes peak-summit accessibility profiles into a small number of shared chromatin archetypes and peak loadings, then uses those archetypes as regulatory programs inside a MultiVelo-style chromatin/transcription/splicing ODE model (`paper.md:56-60`, `paper.md:154-163`, `paper.md:190-231`). For each gene, transcription is modeled as a linear sum of archetype-specific contributions weighted by gene-linked peak loadings; splicing and degradation remain governed by shared gene-level rates.

High-level pipeline:

1. Normalize ATAC peak-summit counts and learn AA-delta archetypes $Y \approx Z A$.
2. Aggregate peak loadings into gene-level archetype weights $z_k^g$.
3. Smooth archetypes over WNN neighborhoods.
4. Run MultiVelo-AA to initialize latent time and kinetic parameters.
5. Refit an ArchVelo per-gene ODE with archetype-specific transcription components and shared $\beta^g,\gamma^g$.
6. Sum component velocities into a global velocity field and optionally inspect each archetypal component separately.

The local code supports this core pipeline: PCHA-based archetypes in `archetypes.py`, gene weights/WNN smoothing in `preprocessing.py`, MultiVelo bootstrap plus ArchVelo fitting in `modeling.py`, exact ODE/velocity computations in `optimization.py`, and component layers such as `velo_s_comp_k`, `u_comp_k`, `s_comp_k`, and `a_comp_k` in `velocity_result`.

### Evaluation

The paper evaluates ArchVelo on mouse embryonic brain and human HSC multi-omic datasets, then applies it to CD8 T cells responding to acute and chronic LCMV infection. In mouse brain, the figure evidence shows better Satb2 u-s fits, higher per-gene likelihood versus MultiVelo, stronger latent-time silhouette, and the highest mean CBDir bar among evaluated baselines (`paper.md:62-70`; local image `27653f...jpg`). In HSC, the composite figure similarly shows improved likelihood/silhouette patterns and high mean CBDir on a curated hematopoietic transition graph (`paper.md:72-80`; local image `729d3b...jpg`).

ArchVelo's distinctive output is velocity decomposition. The paper and figures show A5/A8 components separating cell-cycle and astrocyte differentiation programs in mouse brain, HSC components associated with megakaryocyte/BEM/erythroid branches, and CD8 progenitor components associated with a Ccr6- to Ccr6+ trajectory (`paper.md:82-117`, `paper.md:118-134`; local figure reads in `figure_analysis.md`).

### Reproducibility And Code Match

Reproducibility is **moderate** for the core method and **incomplete** for the full manuscript analysis from this repo alone.

- Code availability: the paper names the ArchVelo package repo and a separate `ArchVelo_notebooks` repository for manuscript analyses, plus a Zenodo archive (`paper.md:376-380`).
- Data availability: PBMC, mouse brain, HSC, and CD8 datasets are public through 10x/GEO/Figshare links (`paper.md:362-374`).
- Current repo match: the cloned package implements the core AA, MultiVelo-AA, ODE fitting, component velocity layers, u-s likelihood helper, and CBDir metric.
- Missing in current repo: motif/TF-ranking implementation is `Not found` in `ArchVelo/README.md` and `ArchVelo/src/**`; full HSC/CD8 notebooks are external; Graphify semantic extraction failed with provider 503 and was not used as evidence.

Important partial matches: the package has 3-fold ridge/CV machinery for RNA-from-ATAC regression, but the visible helper split does not exactly match the paper's 66.7/33.3 split; the package implements u-s likelihood benchmarking directly, while a single standalone full Eq. 6 likelihood objective with chromatin terms was not found.

### Limitations

The paper itself names the linear mapping between chromatin archetypes and transcriptional activation rates as a current limitation: it is interpretable and tractable, but real gene regulation can be nonlinear and condition-dependent (`paper.md:146`). The method also remains gene-wise after archetype learning, with joint modeling across genes suggested as a future extension (`paper.md:148`). For this workspace, the largest evidence limitation is not the core package but the missing external analysis notebooks and motif workflow, which prevents repo-local verification of all biological figure-generation steps.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
