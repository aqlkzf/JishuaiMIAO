---
layout: default
permalink: /paper-atlas/sctour-d2051c92/
title: "scTour"
nav: false
wide: true
description: "单细胞 RNA-seq、snRNA-seq、scATAC-seq 等数据通常只给出细胞在某一时刻的静态测量，但发育和分化研究关心的是“细胞沿什么顺序变化、往哪个方向走、未观测到的状态会是什么样”。论文认为已有方法有几个限制：很多 pseudotime 方法需要用户指定起始细胞；RNA velocity 依赖 spliced/unspliced mRNA 或代谢标记信息；批次效应会影响轨迹和速度可视化；"
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
      <span>Genome Biology · 2023</span>
    </div>
    <h1>scTour</h1>
    <p>scTour: a deep learning architecture for robust inference and accurate prediction of cellular dynamics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-023-02988-9" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scTour">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/LiQian-XC/sctour" target="_blank" rel="noopener noreferrer" aria-label="Open code for scTour">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scTour 方法中文解读

### 这篇论文要解决什么问题

单细胞 RNA-seq、snRNA-seq、scATAC-seq 等数据通常只给出细胞在某一时刻的静态测量，但发育和分化研究关心的是“细胞沿什么顺序变化、往哪个方向走、未观测到的状态会是什么样”。论文认为已有方法有几个限制：很多 pseudotime 方法需要用户指定起始细胞；RNA velocity 依赖 spliced/unspliced mRNA 或代谢标记信息；批次效应会影响轨迹和速度可视化；对新细胞、新数据集或未观测时间段的预测能力有限（`paper.md:23-33`）。

scTour 的目标是用一个统一模型同时完成：

- 推断每个细胞的发育 pseudotime；
- 推断 transcriptomic vector field；
- 学习低维 latent space；
- 对未见过的细胞、数据集或时间区间做动态预测。

### 方法总览

scTour 把 VAE 和 neural ODE 结合起来。输入是细胞乘基因/特征的 abundance matrix $x \in R^{n \times g}$。模型先用 encoder 为每个细胞预测两类信息：一类是 VAE latent posterior 的参数 $\mu, \log \sigma^2$，另一类是 0 到 1 之间的标量时间 $t$。然后模型按 $t$ 对细胞排序，把最早时间点对应的 latent state 当作 ODE 初值，用 neural ODE 沿时间轴积分得到另一组 latent state $z_t$。最后 decoder 同时从 encoder latent $z$ 和 ODE latent $z_t$ 重构表达矩阵，并用重构误差、KL divergence 和 $z$ 与 $z_t$ 的差异共同训练模型（`paper.md:523-583`）。

可以把流程理解成：

```text
表达/峰值矩阵 X
    |
    v
共享 encoder 隐层
    |                         |
    v                         v
mu, log sigma^2            time t
    |                         |
    v                         v
采样 z                  按 t 排序
     \                    /
      \                  v
       \          z(t0), t0..tn
        \                |
         \               v
          \       neural ODE -> z_t
           \             /
            v           v
          decoder 重构 X
              |
              v
加权重构损失 + KL + ||z - z_t||^2
```

代码层面，这个流程由 `sctour/module.py` 中的 `Encoder`、`LatentODEfunc`、`Decoder` 和 `sctour/model.py` 中的 `TNODE.forward` 实现（`module.py:6-151`, `model.py:87-170`）。

### 关键数学模块

#### 1. VAE posterior

论文假设单个细胞的 latent state 来自对角协方差高斯分布：

$$
q(z|x)=\mathcal{N}(z;\mu,\sigma^2 I)
$$

$$
\mu,\log\sigma^2=f_z(x)
$$

并用 reparameterization trick 采样：

$$
z=\mu+\sigma\odot\epsilon,\quad \epsilon\sim\mathcal{N}(0,I)
$$

这些公式在论文方法部分给出（`paper.md:523-541`）。代码中 `Encoder.forward` 输出 `qz_mean` 和 `qz_logvar`，`TNODE.forward` 用 `epsilon * exp(.5*qz_logvar) + qz_mean` 采样 `z`（`module.py:88-93`, `model.py:109-114`）。

#### 2. 时间网络和 neural ODE

scTour 的另一个 encoder head 输出 pseudotime：

$$
t=f_t(x)
$$

论文强调这个 head 和 posterior head 共享第一层 hidden representation，并用 Sigmoid 把时间映射到 0-1（`paper.md:543-547`）。代码中 `self.fc` 是共享层，`fc2` 输出 posterior 参数，`fc3(...).sigmoid()` 输出时间（`module.py:80-93`）。

之后，模型定义 latent dynamics：

$$
\frac{dz(t)}{dt}=f_{ode}(z(t))
$$

并从最早的 latent state $z_{t_0}$ 积分得到 $z_{t_1},...,z_{t_n}$（`paper.md:543-567`）。代码先按 `T` 排序，去掉重复时间点，再用 `torchdiffeq.odeint` 从 `z[0]` 积分，默认 `ode_method='euler'`（`model.py:115-135`）。`LatentODEfunc` 是一个两层线性网络，中间用 ELU（`module.py:6-49`）。

#### 2.1 Neural ODE 在 scTour 里是如何结合进来的

这里最容易误解成“先训练一个 VAE，再额外跑一个 ODE”。scTour 实际上是把 Neural ODE 放进同一个端到端训练图里：encoder 产生的 latent sample $z$ 和时间 $t$ 决定 ODE 的初值与积分网格；ODE 产生的 $z_t$ 又必须通过同一个 decoder 重构原始输入，并且被 $z$ 到 $z_t$ 的差异项约束。因此 ODE 不是独立后处理，而是训练目标的一部分（`paper.md:543-583`, `model.py:109-168`）。

更具体地说，一个 mini-batch 进入 `TNODE.forward` 后会发生下面几步：

```text
X
  -> Encoder
      -> T: 每个细胞的 learned pseudotime
      -> qz_mean, qz_logvar
  -> reparameterization 得到 z
  -> 按 T 排序并去掉重复时间点
  -> 取最早时间点的 z[0] 作为 z0
  -> odeint(lode_func, z0, T) 得到 pred_z，也就是论文里的 z_t
  -> Decoder(z) 和 Decoder(pred_z) 分别重构 X
  -> reconstruction(z) + reconstruction(z_t) + KL + ||z - z_t||^2
```

这条链条说明了 scTour 的几个关键设计。

第一，$t$ 不是外部给定的真实时间，而是 encoder 从同一个输入 $x$ 学出来的标量。这个时间 head 和 VAE posterior head 共享第一层 hidden representation：代码里 `Encoder.forward` 先经过 `self.fc`，再由 `fc2` 输出 `qz_mean/qz_logvar`，由 `fc3(...).sigmoid()` 输出 $t \in [0,1]$（`module.py:80-93`）。所以 pseudotime、latent posterior 和后面的 ODE 路径是在同一个表示空间里共同学习的。

第二，Neural ODE 学的是 latent space 里的速度场，而不是直接在基因表达空间里积分。`LatentODEfunc.forward(t, x)` 的函数签名接收时间 `t` 和状态 `x`，这是 `torchdiffeq.odeint` 的接口要求；但当前实现实际只把 latent state `x` 送入两层 MLP，得到 $\frac{dz}{dt}$（`module.py:30-49`）。因此这个 ODE 是 autonomous latent dynamics：时间 $t$ 主要决定积分顺序和步长，导数方向由当前位置的 latent state 决定。

第三，排序后的最早 latent state 是 ODE 初值。代码中先 `torch.argsort(T)`，再去掉重复时间点，因为 `odeint` 要求时间点严格递增/递减；随后 `z0 = z[0]`，并调用 `odeint(self.lode_func, z0, T, ...)` 生成 `pred_z`（`model.py:115-135`）。这意味着 ODE 轨迹不是从一个固定可学习参数出发，而是从当前 batch 中 learned pseudotime 最早的细胞 latent state 出发。

第四，decoder 把 ODE 路径和表达重构绑在一起。同一个 decoder 同时接收 encoder latent `z` 和 ODE latent `pred_z`，分别得到 `pred_x1` 和 `pred_x2`。如果 `pred_z` 沿 ODE 积分后偏离真实 transcriptomic manifold，它的重构误差会变大；如果 `pred_z` 虽能重构但和 encoder latent `z` 不一致，`z_div = ||z - pred_z||^2` 会惩罚它（`model.py:137-168`）。所以 ODE 学到的不是任意平滑曲线，而是“沿 learned pseudotime 能解释表达矩阵的 latent 动力学”。

第五，训练后的多个输出都复用同一个 ODE 函数：

- vector field：`get_vector_field` / `_get_vector_field` 直接计算 `model.lode_func(T, Z)`，如果 pseudotime 被反转则把方向乘以 `-1`（`train.py:370-397`, `train.py:518-560`）。所以论文里的 transcriptomic vector field 本质上就是训练好的 $f_{ode}$ 在 cell latent position 上的导数。
- latent representation：`get_latentsp` 重新用 encoder 得到 $z$，再按 learned time 调用 `odeint` 得到 `pred_zs`，最后返回 `alpha_z * zs + alpha_predz * pred_zs`（`train.py:400-444`, `train.py:563-670`）。这对应论文公式 $z_{latent}=\omega z+(1-\omega)z_t$。
- 未观测时间预测：`predict_ltsp_from_time` 先从训练数据得到参考时间和 latent representation，对目标时间 $t$ 找时间上最近的 $k$ 个参考点，再从每个邻居的 latent state 积分到目标时间，最后求平均；新预测点还会被加入参考池，用来预测后续时间点（`paper.md:651-657`, `predict.py:254-367`）。

因此，scTour 中 Neural ODE 的结合方式可以概括为：encoder 学出“在哪里”和“按什么时间顺序走”，Neural ODE 学出 latent space 里“往哪个方向变化”，decoder 和 loss 负责检查这条变化路径是否仍能解释原始表达矩阵，训练后同一个 $f_{ode}$ 又被用于 vector field、latent mixing 和 unobserved-time prediction。

#### 3. 训练目标

论文写出的目标是 modified lower bound：

$$
\mathcal{L}=\alpha\log p(x|z)+(1-\alpha)\log p(x|z_t)-D_{\mathrm{KL}}(q(z|x)||p(z))-\|z-z_t\|_2^2
$$

其中 $p(z)=\mathcal{N}(z;0,I)$（`paper.md:569-583`）。

代码中实现的是最小化形式：

```text
loss =
  alpha_recon_lec  * recon_loss_ec
+ alpha_recon_lode * recon_loss_ode
+ z_div
+ alpha_kl * kl_div
```

也就是说，论文用最大化 log-probability 的写法，代码用正的 loss term 做最小化；二者思想一致，但代码把 $\alpha$ 拆成 `alpha_recon_lec`、`alpha_recon_lode` 和 `alpha_kl`（`model.py:162-168`, `_utils.py:7-19`）。

#### 4. 三种重构模式

论文给出三种 reconstruction mode（`paper.md:585-619`）：

- MSE：直接最小化重构表达与观测表达的平方误差；
- NB：用 negative binomial likelihood，decoder 输出每个基因的 abundance proportion，再乘 library size 得到均值；
- ZINB：在 NB 基础上增加 dropout probability。

代码对应实现为：

- `loss_mode == 'mse'` 时使用 `F.mse_loss`（`model.py:137-142`）；
- `loss_mode == 'nb'` 时 decoder 用 Softmax 输出比例，模型乘 library size，并调用 `log_nb`（`module.py:128-141`, `model.py:143-151`, `_utils.py:60-76`）；
- `loss_mode == 'zinb'` 时 decoder 额外输出 dropout logits，并调用 `log_zinb`（`module.py:141-149`, `model.py:152-160`, `_utils.py:32-57`）。

### 训练流程

1. 准备 AnnData。
   MSE 模式需要 log-normalized expression；NB/ZINB 模式需要 raw count。代码在训练和预测时都会检查这一点（`train.py:155-170`, `predict.py:38-58`）。

2. 抽样训练细胞。
   论文说明 scTour 支持 subsampling-based training（`paper.md:629-631`）。代码默认当细胞数超过 10,000 时使用 20% 细胞，否则使用 90%；也可以由用户设置 `percent`（`train.py:172-186`）。

3. 设置默认超参数。
   论文写明 batch size 为 1024，默认 ODE solver 为 Euler，默认 $\alpha=0.5$，优化器为 Adam，learning rate 为 0.001，weight decay 为 `1e-6`，epoch 数与细胞数相关（`paper.md:627-627`）。代码默认值与这些描述一致（`train.py:112-134`, `train.py:192-235`, `train.py:254-262`）。

4. mini-batch 训练。
   `Trainer.train` 构建 DataLoader，创建 Adam optimizer，然后每个 epoch 执行训练和验证。每个 batch 调用 `TNODE.forward`，反向传播并更新参数（`train.py:239-334`）。

### 推断流程

#### pseudotime

训练后，`get_time` 用 encoder 的 time head 为每个细胞预测 pseudotime。论文说由于 ODE 方向可能相反，所以用基因数和 pseudotime 的关系决定是否反转（`paper.md:633-635`）。代码没有显式拟合 sklearn 线性回归，而是计算 pseudotime 和 log1p gene count 的中心化乘积符号；如果为正，就返回 `1 - ts`（`train.py:337-367`）。

#### vector field

论文把 transcriptomic vector field 定义为 learned differential equation $f_{ode}$（`paper.md:637-637`）。代码中 `_get_vector_field` 直接计算 `model.lode_func(T, Z)`，如果 pseudotime 曾被反转，则把方向乘以 `-1`（`train.py:518-560`）。

#### latent representation

论文定义最终 latent representation：

$$
z_{latent}=\omega z+(1-\omega)z_t
$$

更大的 $\omega$ 偏向 transcriptomic structure，更小的 $\omega$ 偏向 pseudotime ordering（`paper.md:639-645`）。代码用 `alpha_z` 和 `alpha_predz` 表达同一含义，并强制二者和为 1，最后返回 `alpha_z * zs + alpha_predz * pred_zs`（`train.py:563-670`）。

### 预测功能

scTour 的预测分两类。

第一类是给定 query cell 的表达矩阵，预测其 pseudotime、vector field 和 latent representation。代码分别提供 `predict_time`、`predict_vector_field` 和 `predict_latentsp`（`predict.py:105-251`）。`predict_latentsp` 有 `coarse` 和 `fine` 两种模式：`fine` 会把 query data 和训练数据合并后一起推断 latent，再取 query 部分（`predict.py:219-251`）。

第二类是给定未观测时间点，预测该时间点的 latent space。论文公式是：

$$
z_t=\frac{1}{k}\sum_j \mathrm{ODESolve}(z_j,f_{ode},t_j,t)
$$

也就是在训练集参考 pseudotime 中找与目标时间最接近的 $k$ 个邻居，从每个邻居的 latent state 积分到目标时间，再求平均（`paper.md:651-657`）。代码在 `predict_ltsp_from_time` 中按绝对时间差找最近邻，调用 `odeint`，平均后把新预测点加入参考池，用于后续时间点预测（`predict.py:254-367`）。

### vector field 可视化

论文把 latent-level vector field 投影到 UMAP 等低维 embedding。核心是计算 velocity 和邻居 latent 差异之间的 cosine similarity：

$$
P_{ij}=\exp\left(\frac{\cos(\nu_i,l_{ij})}{\sigma}\right),\quad
\nu_i=f_{ode}(z_i),\quad l_{ij}=z_j-z_i
$$

再行归一化，得到 embedding 上的 displacement vector：

$$
\Delta u=\sum_{j\neq i}(P_{ij}-\frac{1}{n})\frac{u_j-u_i}{\|u_j-u_i\|}
$$

（`paper.md:659-681`）。代码中 `cosine_similarity` 计算 latent 差异和 vector field 的相似度，`vector_field_embedding` 计算 embedding displacement，`vector_field_embedding_grid` 和 `plot_vector_field` 负责箭头/streamline 可视化（`vector_field.py:15-117`, `vector_field.py:158-215`, `vector_field.py:218-518`）。

### 论文中的评估

论文用多类数据展示 scTour：

- 小鼠 dentate gyrus neurogenesis：展示 pseudotime、vector field、latent space，并测试 batch/subsampling robustness（Fig. 2；`paper.md:80-93`, `paper.md:683-689`）。
- 小鼠 pancreatic endocrinogenesis：通过排除 Fev 细胞和 Ngn3-high EP 细胞测试未见状态和未见时间区间预测（Fig. 3；`paper.md:97-110`, `paper.md:691-695`）。
- cortical excitatory neuron development：测试跨平台、跨系统、跨物种预测（Fig. 4；`paper.md:112-173`, `paper.md:697-703`）。
- benchmark：与 scVelo、Palantir、Monocle 3、Slingshot、scVI 比较 pseudotime、vector field 和 latent space（Fig. 5；`paper.md:175-240`, `paper.md:749-781`）。
- human skeletal muscle development：用于发育时间对齐、基因动态分析和体外分化细胞的发育阶段预测（Fig. 6；`paper.md:242-501`, `paper.md:783-787`）。

### 代码与论文的对应程度

代码对核心方法的支持很完整：VAE posterior、time head、neural ODE、MSE/NB/ZINB loss、训练默认值、latent mixing、query prediction、vector field 可视化都能在源码中找到直接实现。

但代码仓库不是完整的论文复现实验仓库。直接搜索 package source、docs、README/setup/YAML、文件名和 notebook cell source 后，没有找到 Fig. 5 / Fig. S17 benchmark runner，也没有找到所有数据集和图面板的完整生成脚本。因此应该把仓库理解为 scTour 方法软件包，而不是 paper figure reproduction bundle。

### 方法局限

论文自己指出，scTour 的 vector field 本质上沿 pseudotime 方向，因此不能完整描述循环过程；只有 terminal state 的数据可能被强行排序，从而产生不合理方向；连续 ODE 积分理论上更适合非分支轨迹，复杂分支结构中可能把分支顺序连接起来（`paper.md:509-513`）。这些限制与代码结构一致，因为当前实现使用一个标量时间轴和全局 ODE dynamics，而不是显式的分支特异模型。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scTour Summary

scTour is a deep-learning method for inferring and predicting cellular dynamics from single-cell abundance matrices. The paper targets four limitations of prior trajectory and RNA-velocity methods: many pseudotime methods require a known start cell, RNA velocity depends on spliced/unspliced or metabolic-labeling information, batch effects can distort dynamics, and prediction for unseen cells or datasets is limited (`paper.md:23-33`).

### Proposed Method

The method combines a variational autoencoder with a neural ODE. A shared encoder maps each cell's expression vector to both posterior parameters for latent state $z$ and a scalar pseudotime $t$. Cells are sorted by $t$, the earliest latent state seeds a neural ODE, and the ODE produces a time-evolved latent series $z_t$. A decoder reconstructs expression from both $z$ and $z_t$, with an objective combining weighted reconstruction terms, KL divergence to a standard normal prior, and a penalty that keeps $z_t$ close to $z$ (`paper.md:523-583`).

The released code implements this core pipeline directly. `Encoder`, `LatentODEfunc`, and `Decoder` define the modules; `TNODE.forward` performs time sorting, ODE solving, reconstruction losses, KL, and z-divergence; `Trainer` provides training and inference; `predict.py` provides query prediction; and `vector_field.py` maps latent vector fields to embeddings (`module.py:6-151`, `model.py:87-170`, `train.py:41-670`, `predict.py:15-367`, `vector_field.py:15-518`).

### What scTour Outputs

- Pseudotime: a sigmoid time head predicts a value in `[0, 1]`; code can reverse direction using gene-count information (`paper.md:633-635`, `train.py:337-367`).
- Vector field: the learned ODE derivative network is evaluated at latent coordinates (`paper.md:637-637`, `train.py:518-560`).
- Latent representation: a weighted mixture $\omega z + (1-\omega)z_t$ combines intrinsic transcriptomic structure and ODE-time structure (`paper.md:639-645`, `train.py:563-670`).
- Prediction: trained models can predict pseudotime/vector field/latent representations for query cells and can integrate ODE trajectories for requested unobserved time intervals using nearest reference times (`paper.md:647-657`, `predict.py:105-367`).

### Evaluation

The paper demonstrates inference on dentate gyrus neurogenesis, showing pseudotime, vector-field, and latent-space views that follow expected developmental structure and remain visually coherent under batch/subsampling settings (Fig. 2; `paper.md:80-93`). It tests unseen-state and time-interval prediction in pancreatic endocrinogenesis, including held-out Fev endocrine cells and Ngn3-high endocrine progenitor reconstruction (Fig. 3; `paper.md:97-110`). It also tests cross-platform, cross-system, and cross-species prediction in excitatory neuron development (Fig. 4; `paper.md:112-173`).

For benchmarking, scTour is compared with scVelo, Palantir, Monocle 3, Slingshot, and scVI over pseudotime, vector-field, and latent-space criteria (Fig. 5; `paper.md:175-240`, `paper.md:749-781`). The paper further applies scTour to human skeletal muscle development and in vitro/in vivo progenitor alignment (Fig. 6; `paper.md:242-501`, `paper.md:783-787`).

### Reproducibility and Code-Paper Match

Code-paper fidelity is **high** for the reusable scTour method implementation: the VAE posterior, time head, neural ODE, MSE/NB/ZINB losses, training defaults, latent mixing, prediction APIs, and vector-field visualization utilities are all present in the cloned repository. The main implementation difference is notation: the paper writes a maximized lower-bound objective, while code minimizes positive reconstruction/KL/divergence losses with separate alpha weights (`model.py:137-168`).

Reproducibility is **partial** for the paper's full experimental suite. The package contains method code and tutorial notebooks, but no benchmark runner or complete figure-generation scripts were found for Fig. 5 / Fig. S17 comparisons. The source paper was acquired through MinerU hybrid OCR and is usable with caveats; no supplementary markdown is available, so supplementary table details were not independently read. The paper reports code availability on GitHub and Zenodo (`paper.md:837-837`), and this workspace uses the GitHub snapshot at commit `4d26abb936b7872706e6540f38bab6251159a475`.

### Main Limitations

The paper states that scTour's vector field follows inferred time and therefore cannot fully describe cyclic processes; terminal-state-only datasets can force artificial pseudotime directions; and continuous ODE integration is theoretically strongest for non-branching trajectories and may sequentially connect branches in complex topology (`paper.md:509-513`). These caveats are consistent with the code design, where the vector field is a derivative along a scalar time-ordered latent path.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
