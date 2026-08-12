---
layout: default
permalink: /paper-atlas/crakvelo-5372efaa/
title: "CRAKVelo"
nav: false
description: "本文分析的论文是 CRAK-Velo: chromatin accessibility kinetics integration improves RNA velocity estimation，发表于 Genome Biology 2026，DOI 为 10.1186/s13059-026-04086-y。"
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
      <span>Genome Biology · 2026</span>
    </div>
    <h1>CRAKVelo</h1>
    <p>CRAK-Velo: chromatin accessibility kinetics integration improves RNA velocity estimation</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-026-04086-y" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CRAK-Velo 方法中文解读

本文分析的论文是 **CRAK-Velo: chromatin accessibility kinetics integration improves RNA velocity estimation**，发表于 *Genome Biology* 2026，DOI 为 `10.1186/s13059-026-04086-y`。CRAK-Velo 的目标是在 RNA velocity 估计中引入同一细胞的染色质可及性信息，让每个基因的转录速率不只由 spliced/unspliced RNA 推断，而是被附近调控区域的开放状态约束和解释（`paper source:31-43`）。

### 1. 论文要解决什么问题？

RNA velocity 用 spliced 和 unspliced RNA 推断细胞未来状态，但核心难点是：每个基因的转录速率如何建模？如果假设转录速率是简单开关，模型会太受限；如果完全从 RNA 数据中学习，又会引入大量参数并容易不稳定。单细胞 multiome 数据同时提供 RNA 和 ATAC，因此 CRAK-Velo 尝试用 chromatin accessibility 解释转录速率，从而得到更生物一致、也更可解释的 velocity（`paper source:39-47`）。

### 2. 现有方法为什么不够？

论文主要对比了三类思路：

- 经典 RNA velocity 和后续模型依赖 spliced/unspliced 关系，需要指定或学习转录速率（`paper source:39-41`）。
- UniTVelo 使用统一时间和参数化曲线来估计 RNA velocity，但它本质上仍主要依赖 RNA 读数（`paper source:47-47`, `paper source:111-119`）。
- MultiVelo 引入 chromatin accessibility，但论文认为 CRAK-Velo 是更简单、更快、同时更容易解释区域-基因调控关系的方案（`paper source:41-43`, `paper source:73-75`）。

CRAK-Velo 的核心改进不是重新发明 RNA 动力学，而是在 UniTVelo 风格的 spliced/unspliced 曲线旁边增加一个由 ATAC 区域可及性推导出的转录速率约束。

### 3. 方法整体流程

```text
scRNA + scATAC paired AnnData
        |
        v
RNA: HVG / PCA / neighbors / moments
ATAC: cisTopic 平滑 -> 区域开放概率 phi
        |
        v
用基因和区域坐标建立 B[region, gene]
        |
        v
筛选 velocity genes，初始化 gamma / scaling
        |
        v
RBF 曲线拟合 spliced RNA: s_hat_g(t)
由 s_hat_g(t) 推导 u_hat_g(t) 和 u_hat'_g(t)
        |
        v
用区域开放概率和权重构造 chromatin rate c^g(t)
得到 ATAC-derived derivative u'_ATAC(t)
        |
        v
交替优化参数和细胞时间:
  更新 theta_g -> 重新分配 cell time -> 按 pseudotime 重排 accessibility
        |
        v
输出 velocity、latent time、拟合参数、region weights、下游图表分析
```

代码中的主流程位于 `CRAK-Velo/crak-velo/main.py:7-37`：读取 RNA/ATAC AnnData，初始化数据，计算 region-gene intersection，构建二值矩阵 `B`，实例化 `Velocity`，拟合模型，并写出 fitted RNA/ATAC AnnData 与 `B.txt`。

### 4. RNA 和 ATAC 预处理

论文说 RNA 部分采用 UniTVelo 类似的流程：选择 highly variable genes，再按 scVelo 风格进行信息基因选择；ATAC 部分保留足够多细胞中出现的区域，并只考虑基因起始位点上下游窗口内的区域（`paper source:81-89`）。

代码中 `init_adata` 读取 `adata` 和 `adata_atac`，对 RNA 运行 `scv.pp.filter_and_normalize`、PCA、neighbors 和 moments（`CRAK-Velo/crak-velo/model/preprocessing.py:23-48`）。HSPC 配置中 `n_top_genes=2000`、`n_pcs=30`、`n_neighbors=30`、`rescale_data=true`（`CRAK-Velo/crak-velo/config/config_main_HSPC.json:15-24`）。

区域-基因关联由 `genes_regions_interesctions` 和 `gene_regions_binary_matrix` 完成：使用 pybedtools 找窗口内的 region-gene pair，根据距离过滤，然后构造 `B`，其中 `B[region, gene]=1` 表示该区域参与该基因参数拟合（`CRAK-Velo/crak-velo/model/preprocessing.py:50-103`）。

需要注意一个不一致：论文方法中写的是 `10^4 bp` 窗口（`paper source:145-145`），mouse brain 配置也是 `10000`，但 HSPC 配置里是 `10e4`（`CRAK-Velo/crak-velo/config/config_main_HSPC.json:23-24`; `CRAK-Velo/crak-velo/config/config_main_10X_mouse_brain.json:17-26`）。除非后续有额外证据解释，否则应视为配置与论文描述之间的差异。

### 5. cisTopic 和开放概率 Eq. 3

论文用 cisTopic 平滑稀疏 ATAC 数据。它为每个细胞定义 topic 向量 $\lambda^n$，为每个 region 定义 topic 向量 $\psi_r$，并用下面公式计算 region 在 cell 中的开放概率：

$$
\phi_r^n = \sum_i^T \lambda_i^n \psi_r^i.
$$

论文还说明采样数为 3000，thinning 为 10，topic 维度 $T=30$（`paper source:91-107`）。

这个公式在主 Python 包中没有直接实现；主包只消费 `adata_atac.obsm["cisTopic"]` 并做 min-max normalize（`CRAK-Velo/crak-velo/velocity/velocity.py:35-37`）。直接实现证据在 `notebooks/preprocessing.ipynb`：notebook 设置 `n_samples=3000`、`n_burnin=10`、`T=30`，运行 `cisTopic.fit`，读取并平均 `theta_ATAC` 和 `phi_ATAC`，再用 `phi = torch.matmul(m,m_psi)` 写入 `adata_atac.obsm["cisTopic"]`（`CRAK-Velo/notebooks/preprocessing.ipynb:94-118`; `CRAK-Velo/notebooks/preprocessing.ipynb:130-147`）。

因此，Eq. 3 是 **notebook-backed preprocessing**，不是主库中的函数。

### 6. RNA 动力学：RBF 曲线

CRAK-Velo 沿用 UniTVelo 的思路，用 RBF 形式拟合 spliced RNA：

$$
\hat{s}_g(t)=h_g e^{-a_g(t_{ng}-\tau_g)^2}+o_g.
$$

再由 spliced 曲线和参数 $\beta_g,\gamma_g,i_g$ 推导 unspliced 曲线和导数（`paper source:111-129`）。

代码中：

- `get_fit_s` 实现 RBF spliced 曲线；
- `get_s_deri` 计算 spliced 曲线导数；
- `get_fit_u` 计算 unspliced 曲线；
- `get_u_deri` 计算 unspliced 导数并对无 region 的基因做 mask（`CRAK-Velo/crak-velo/model/optimize_utils.py:87-102`）。

这里有一个需要谨慎的点：论文 OCR 中 Eq. 5 写成 `(s' - gamma*s)/beta + i`，而代码是 `(s_deri + gamma*s)/beta + intercept`（`CRAK-Velo/crak-velo/model/optimize_utils.py:95-97`）。这可能来自符号约定或 OCR 问题，但从直接代码证据看，不能说它和论文公式逐字一致。

### 7. 用 chromatin accessibility 构造转录速率

CRAK-Velo 的核心新意在这里。论文定义某个基因 $g$ 附近有一组 region $R_g$，每个 region 的开放概率经归一化后乘以该 region 对该基因的权重 $w_r^g$，再由 $\eta_g$ 缩放：

$$
c^g(t)=\eta_g \sum_r^{R_g} c_r^g(t),
$$

$$
c_r^g(t)=w_r^g f(\phi_r^n(t)).
$$

论文强调，accessibility 会周期性地按推断 pseudotime 重排，不同 region 对同一基因有不同权重（`paper source:131-145`）。

代码实现与这个思想高度对应：

- `region_dynamics_matrix` 按 latent time 排序 `M_acc`（`CRAK-Velo/crak-velo/model/optimize_utils.py:187-197`）；
- `compute_alpha` 用 `B * exp(log_region_weights)` 作为 masked region weights，并乘以 `eta` 得到 `alpha`（`CRAK-Velo/crak-velo/model/optimize_utils.py:199-214`）；
- `compute_alpha_atac` 在 supplement helper 中为 figure/evaluation 生成 `adata.layers["ATAC"]`（`CRAK-Velo/crak-velo/supplement/fitting_genes_regions.py:80-103`）。

直观理解：每个基因的转录活性不再是自由参数，而是附近 ATAC region 的开放程度和学习到的 region 权重的加权和。

### 8. RNA 导数与 ATAC 导数的对齐

论文定义 ATAC-derived unspliced derivative：

$$
u_g'^{ATAC}(t)=c^g(t)-\beta_g(t)\hat{u}_g(t).
$$

CRAK-Velo 要让这个 ATAC 推导出的导数与 RBF-RNA 曲线推导出的 $\hat{u}'_g(t)$ 一致（`paper source:147-153`）。

代码中 `compute_u_deri_atac` 计算：

```python
u_deri_atac = alpha - exp(args[1]) * self.Mu
```

也就是 `alpha - beta * observed/preprocessed Mu`（`CRAK-Velo/crak-velo/model/optimize_utils.py:216-219`）。随后 loss 中惩罚 `u_deri_func - u_deri_atac` 的平方差（`CRAK-Velo/crak-velo/model/recover_paras.py:136-151`）。

这属于 **Partial match**：结构上确实是 chromatin-derived derivative 对齐 RNA-derived derivative，但源码用的是 `self.Mu`，而论文公式写的是拟合的 $\hat{u}_g(t)$。

### 9. 参数和时间如何优化？

论文说要同时推断两类未知量：一类是每个基因的动力学和 chromatin 参数 $\theta_g$，另一类是细胞在该基因动力学曲线上的时间 $t_{ng}$，再由 gene-cell time 汇总成 unified pseudotime $t_n$。论文给出的交替过程是：固定 cell time 更新参数，固定参数重新分配 gene-cell time，计算 unified pseudotime，再按 pseudotime 重排 $\phi_r$（`paper source:157-184`）。

代码里可以把这一段理解为两个嵌套的交替：

1. **短周期交替参数子集和 loss 项**：在梯度下降内部，每 400 个 epoch 分成前 200 和后 200 两段，先偏向拟合 spliced/RBF 形状，再偏向拟合 unspliced/kinetic 参数；后半程再把主要参数一起优化。
2. **长周期交替参数和 cell time**：每轮先用当前 `t_cell` 更新参数；每 800 个 epoch，再固定新参数，用 3000 个候选时间点重新匹配每个细胞的时间，并用新的 unified pseudotime 重排 accessibility。

#### 9.1 初始化：先给模型一条时间轴

`Recover_Paras.__init__` 先初始化参数，再计算初始 `t_cell`（`CRAK-Velo/crak-velo/model/recover_paras.py:48-52`）。参数变量来自 `init_vars`：

- `log_gamma`、`log_beta` 对应 $\gamma_g,\beta_g$；
- `offset`、`log_a`、`t`、`log_h` 对应 RBF spliced 曲线的 $o_g,a_g,\tau_g,h_g$；
- `intercept` 对应 unspliced 曲线里的截距项 $i_g$；
- `log_region_weights`、`log_etta` 对应 $w_r^g,\eta_g$，并用 `B` 和 `B_genes_nr` 限制到有 region-gene 关系的位置（`CRAK-Velo/crak-velo/model/optimize_utils.py:43-72`）。

需要区分两个“时间”变量：`self.t` 是每个基因 RBF 曲线中心 $\tau_g$，源码把它初始化为 `0.5`；`self.t_cell` 才是每个 cell-gene 的当前时间矩阵。若配置没有指定 `gcount` 或 diffusion pseudotime，`compute_cell_time(args=None)` 会生成 `[0,1]` 上的初始时间网格；当前 HSPC 和 mouse brain 配置的 `iroot` 都是 `null`（`CRAK-Velo/crak-velo/model/recover_paras.py:112-129`; `CRAK-Velo/crak-velo/config/config_main_HSPC.json:53-55`; `CRAK-Velo/crak-velo/config/config_main_10X_mouse_brain.json:55-57`）。

#### 9.2 一轮参数更新到底算了什么？

`fit_likelihood` 是主循环。每个 epoch 先把当前 TensorFlow 变量打包成 `args`：

```text
args = [
  log_gamma, log_beta, offset, log_a, t, log_h,
  intercept, log_region_weights, log_etta
]
```

然后 `compute_loss(args, self.t_cell, iter, progress_bar)` 在当前 `t_cell` 上计算三类残差（`CRAK-Velo/crak-velo/model/recover_paras.py:247-260`）：

1. 用 `get_s_u` 得到当前参数下的 $\hat{s}_g(t)$ 和 $\hat{u}_g(t)$，再计算 `Ms - s_func` 与 `Mu - u_func`；
2. 用 `get_u_deri` 得到 RBF/RNA 曲线导出的 $\hat{u}'_g(t)$；
3. 用当前 unified pseudotime 重排 ATAC，计算 `u_deri_atac`，再得到 `u_deri_func - u_deri_atac`（`CRAK-Velo/crak-velo/model/recover_paras.py:136-151`）。

第三项是 CRAK-Velo 与纯 RNA velocity 的关键差别。源码先从当前 `t_cell` 取 unified pseudotime，归一化后传给 `compute_u_deri_atac`；后者调用 `compute_alpha`，按 pseudotime 排序 `M_acc`，再用 `B * exp(log_region_weights)` 和 `exp(log_etta)` 计算 chromatin-derived transcription rate `alpha`，最后得到：

```python
u_deri_atac = alpha - exp(args[1]) * self.Mu
```

也就是代码实现里的 $u_g'^{ATAC}$（`CRAK-Velo/crak-velo/model/optimize_utils.py:187-219`）。这里仍要保留前面说过的 caveat：论文 Eq. 11 写的是 $\hat{u}_g(t)$，而源码用的是观测/预处理后的 `self.Mu`。

#### 9.3 loss 不是直接返回论文 Eq. 13

论文把 Eq. 13 写成包含 expression residual 和 ATAC derivative residual 的 negative log-likelihood，并设 $k=0.5$（`paper source:165-175`）。源码确实计算了 `get_log_likelihood`，但训练时 `compute_loss` 返回的是 `finalize_loss`，也就是分阶段 squared-error residual（`CRAK-Velo/crak-velo/model/recover_paras.py:166-207`）：

```text
if iter < epochs / 2:
  if iter % 400 < 200:
    loss = spliced_residual + 0.5 * ATAC_derivative_residual
  else:
    loss = unspliced_residual + 0.5 * ATAC_derivative_residual
else:
  loss = spliced_residual + unspliced_residual + 0.5 * ATAC_derivative_residual
```

所以更准确的实现表述是：前半程让 spliced 曲线和 unspliced 曲线分块稳定下来，但两个分块都带着 ATAC derivative 约束；后半程同时优化 spliced、unspliced 和 ATAC derivative 三项。这里的 `0.5` 是硬编码的 `reg_u_derr_loss`，对应论文里调节 ATAC 噪声影响的 $k$。

#### 9.4 哪些参数在不同阶段被更新？

`get_opt_args` 决定每一小段训练实际对哪些变量求梯度。当前配置 `mode=1`（`CRAK-Velo/crak-velo/config/config_main_HSPC.json:40-45`; `CRAK-Velo/crak-velo/config/config_main_10X_mouse_brain.json:42-47`），因此源码行为是：

- 前半程且 `iter % 400 < 200`：更新 `offset, log_a, t, log_h, log_region_weights, log_etta`。这主要是在调 spliced RBF 曲线的形状、高度、中心和 chromatin 权重。
- 前半程且 `iter % 400 >= 200`：更新 `log_gamma, log_beta, intercept, log_region_weights, log_etta`。这主要是在调 unspliced 曲线相关的 kinetic 参数，同时继续调 chromatin 权重。
- 后半程：更新 `log_gamma, log_beta, offset, log_a, t, log_h, intercept, log_region_weights, log_etta`，也就是把主要 RNA kinetic 参数和 chromatin 参数一起放开（`CRAK-Velo/crak-velo/model/optimize_utils.py:223-245`）。

梯度更新后，代码还做了两个 mask：`processed_grads = g * convert` 只让 velocity genes 参与有效梯度；`args[7].assign(self.B * args[7])` 和 `args[8].assign(self.B_genes_nr * args[8])` 再次把 region weights 与 eta 限制在有 region-gene 连接的位置（`CRAK-Velo/crak-velo/model/recover_paras.py:268-278`）。

#### 9.5 固定参数后怎样重新分配 cell time？

每 800 个 epoch，`fit_likelihood` 会执行：

```python
self.t_cell = self.compute_cell_time(args=args)
```

这一步就是“固定参数，更新细胞时间”（`CRAK-Velo/crak-velo/model/recover_paras.py:280-281`）。具体流程如下：

1. `compute_cell_time(args)` 先生成一个形状为 `3000 x n_genes` 的候选时间网格 `x`，范围是 `[0,1]`（`CRAK-Velo/crak-velo/model/recover_paras.py:112-116`）。
2. `predict_cell_time` 在这 3000 个候选时间点上计算预测曲线 `s_predict/u_predict` 和 RNA-derived `u_deri_func`（`CRAK-Velo/crak-velo/model/recover_paras.py:54-63`）。
3. 同时，它用当前旧的 `self.t_cell` 得到 interim latent time，并据此计算 ATAC-derived `u_deri_atac`（`CRAK-Velo/crak-velo/model/recover_paras.py:65-68`）。
4. `match_time` 对每个 velocity gene、每个 cell，在 3000 个候选时间点上计算距离：

$$
\sqrt{(u_{obs}-\hat{u})^2+(s_{obs}-\hat{s})^2+(u'^{ATAC}-\hat{u}')^2}.
$$

然后取距离最小的候选时间作为新的 gene-cell time（`CRAK-Velo/crak-velo/model/optimize_utils.py:133-155`）。

当前配置使用 `reorder_cell="Soft_Reorder"` 和 `aggregrate_t=true`。因此源码不是直接保留原始 argmin index，而是先对每个基因的分配位置做 rank reorder 和 min-max normalize，再用 `max_density` 聚合成每个 cell 的 unified time，并广播回 `n_cells x n_genes` 的矩阵（`CRAK-Velo/crak-velo/model/optimize_utils.py:156-169`; `CRAK-Velo/crak-velo/model/optimize_utils.py:259-276`）。

直观地说，参数更新让曲线形状更贴近当前细胞位置；time update 则把每个细胞重新投影到更新后的曲线上。因为 distance 里包含 ATAC derivative 项，新的时间不只由 spliced/unspliced phase portrait 决定，也会受到 chromatin-derived dynamics 的影响。

#### 9.6 新时间如何反馈到 chromatin 项？

重新得到 `t_cell` 后，下一轮 loss 会再次调用 `compute_u_deri_atac`。这时 `region_dynamics_matrix` 会按新的 latent time 排序 accessibility 矩阵 `M_acc`，`compute_alpha` 再用新顺序的 accessibility 与 region weights 计算 $c^g(t)$（`CRAK-Velo/crak-velo/model/optimize_utils.py:187-214`）。

因此，CRAK-Velo 的交替优化不是“先单独拟合 RNA，再事后加 ATAC”。更准确的流程是：

```text
当前 t_cell
  -> 计算 RBF RNA 曲线和 ATAC-derived derivative
  -> 按 staged residual loss 更新 RNA 参数与 region weights/eta
  -> 每 800 epoch 用更新后的曲线重新匹配 cell time
  -> 用新 pseudotime 重排 accessibility
  -> 下一轮继续优化
```

最后，训练到最后一个 epoch 或满足 stop condition 后，`update_and_store_results` 会再计算一次 `t_cell`，保存 `velocity`、`fit_t`、`u_derrivative`、`u_atac`、预测的 `Pred_s/Pred_u`、拟合参数和 `fit_region_weights`；主循环末尾还会把聚合后的时间写入 `adata.obs["latent_time"]`（`CRAK-Velo/crak-velo/model/recover_paras.py:224-285`; `CRAK-Velo/crak-velo/model/recover_paras.py:287-322`）。

总结这部分时要特别注意：**论文层面可以说它迭代最小化 negative log-likelihood；源码层面应说它用 Adam 优化 staged squared-error residual，并每 800 个 epoch 通过 3000 点时间网格重新分配 cell time**。

### 10. 下游评估和解释

论文用 HSPC、mouse embryonic brain 和 human cerebral cortex 数据集评估 CRAK-Velo。主要结果包括：

- 在 HSPC 中，CRAK-Velo 更好地区分终末状态并改善 cross-boundary direction（`paper source:47-51`）。
- 在 mouse brain 中，CRAK-Velo 避免了 baseline 方法中的一些 spurious flow，但所有方法仍未正确识别 ependymal cells 为 terminal state（`paper source:65-65`）。
- 用 chromatin-unspliced 表示做 KNN cell-type deconvolution，CRAK-Velo 在图中表现更好（`paper source:51-51`, `paper source:65-65`）。
- 低熵基因、TF-binding enrichment、KLF1/Jag2 region kinetics 用来解释 region weights 的生物意义（`paper source:53-53`, `paper source:67-71`, `paper source:210-244`）。

代码支持情况：

- KNN evaluation 在 `supplement/eval_utils.py:215-273`，Fig1/Fig2 notebooks 调用它（`CRAK-Velo/notebooks/Fig1.ipynb:321-331`; `CRAK-Velo/notebooks/Fig2.ipynb:234-235`）。
- CBDir 在 `supplement/eval_utils.py:54-127`，Fig1 notebook 计算 method-wise CBDir（`CRAK-Velo/notebooks/Fig1.ipynb:461-534`）。
- Fig2 notebook 用 scVelo PAGA 调用生成 graph summary（`CRAK-Velo/notebooks/Fig2.ipynb:299-342`）。
- region kinetics 由 `region_unspliced_kinetics` 和 `region_kinetic_plot` 支持（`CRAK-Velo/crak-velo/supplement/fitting_genes_regions.py:106-132`; `CRAK-Velo/crak-velo/pl/pl.py:188-275`）。

未找到的部分：

- 低熵基因排序的代码实现未在 `crak-velo/` 或 notebooks 中找到。
- ChIP-ATLAS TF-binding enrichment 的代码实现未在 `crak-velo/` 或 notebooks 中找到。

这些分析有论文文字和图像支持，但不能在当前仓库快照中声称有完整源码复现。

### 11. 如何理解 CRAK-Velo 的贡献？

CRAK-Velo 的核心贡献可以概括为：

1. 保留 UniTVelo 风格的简洁 RNA kinetic curve；
2. 用 cisTopic-smoothed chromatin accessibility 构造 gene-specific transcription rate；
3. 学习 region weights，使 velocity 推断和区域调控解释连在一起；
4. 用 ATAC-derived derivative 约束 RNA-derived derivative，让速度估计更符合 chromatin 状态；
5. 输出 region weights 后，可进一步做 gene-region interpretation、region kinetics 和 TF/GO 解释。

从代码证据看，主算法实现是存在且可追踪的，代码-论文一致性为 **medium**。核心 chromatin integration 路径可信，但 Eq. 3 依赖 notebook preprocessing，Eq. 13 的实际优化目标与论文描述不完全一致，低熵和 TF enrichment 的源码复现未找到。整体复现性可评为 **3/5**：核心模型可读可跑，但部分图表和解释性分析依赖 notebook、外部 cisTopic 仓库、局部路径或缺失源码。

### 12. CRAK-Velo 和 MultiVelo 的区别

CRAK-Velo 论文明确把 MultiVelo 当作重要 baseline：两者都想把 chromatin accessibility 加入 RNA velocity，但它们的建模层级完全不同。最短的概括是：

- **MultiVelo**：把 chromatin、unspliced RNA、spliced RNA 都放进一个显式三变量 ODE 系统，拟合一条完整的 $(c,u,s)$ 动力学轨迹。
- **CRAK-Velo**：保留 UniTVelo 风格的 RBF RNA 曲线，用 chromatin accessibility 构造一个 gene-specific transcription rate，再用 ATAC-derived derivative 去约束 RNA-derived derivative，同时学习 region-level weights。

也就是说，MultiVelo 的核心问题是“这个基因的 chromatin-RNA 三维轨迹是什么形状、细胞在这条轨迹的哪一段”；CRAK-Velo 的核心问题是“RNA kinetic curve 已经有了，附近哪些 accessible regions 能解释 transcription rate，并让 RNA derivative 更符合 chromatin 信息”。

#### 12.1 输入对象的差别：gene-level chromatin vs region-level chromatin

MultiVelo 的 chromatin 变量是 gene-level 的 $c(t)$。在论文工作流里，ATAC peaks 会先被聚合到基因：10x mouse brain 数据中，作者把 promoter peaks 和与 promoter accessibility 或 gene expression 相关、且在 10 kb 内的 distal enhancer peaks 聚合成一个 gene-level chromatin modality，再做 TF-IDF normalization 和 WNN smoothing，最终得到 chromatin accessibility、unspliced、spliced 三个矩阵（`MultiVelo/paper source/.../Li et al. - 2023 ... .md:513-517`）。源码入口 `recover_dynamics_chrom` 也要求 RNA 侧有 `Mu/Ms/connectivities`，ATAC 侧有 `Mc` layer（`MultiVelo/src/multivelo/dynamical_chrom_func.py:4384-4435`）。

CRAK-Velo 没有先把所有 nearby peaks 压成一个单独的 gene-level $c(t)$。它保留 region 层级：先用 cisTopic 得到每个 region 在每个 cell 的开放概率 $\phi_r^n$，再用 `B[region,gene]` 表示哪些 region 属于某个基因窗口，最后学习每个 region-gene pair 的权重 $w_r^g$（`paper source:91-107`; `paper source:131-145`; `CRAK-Velo/crak-velo/model/preprocessing.py:50-103`; `CRAK-Velo/crak-velo/model/optimize_utils.py:199-214`）。

这个差别非常关键：

- MultiVelo 的 chromatin input 更像“每个基因一个聚合后的 accessibility time series”；
- CRAK-Velo 的 chromatin input 更像“每个基因周围一组 region 的 accessibility matrix，再学习这些 region 对该基因的贡献”。

所以 MultiVelo 更擅长解释 **chromatin 与 RNA 的时间先后关系**；CRAK-Velo 更强调 **哪个 region 以多大权重影响某个 gene 的 transcription rate**。

#### 12.2 核心数学模型的差别

MultiVelo 直接建立三条 ODE。论文说它用 chromatin accessibility $c$、unspliced pre-mRNA $u$、spliced mRNA $s$ 的三变量系统描述基因表达过程，转录率与 $c(t)$ 成比例，细胞的 state 和 time 通过投影到 ODE 曲线最近点得到（`MultiVelo/paper source/.../Li et al. - 2023 ... .md:45-55`）。对应的核心形式可以写成：

$$
\frac{dc(t)}{dt}=k_c\alpha_c-\alpha_c c(t),
$$

$$
\frac{du(t)}{dt}=\alpha^{(k)}c(t)-\beta u(t),
$$

$$
\frac{ds(t)}{dt}=\beta u(t)-\gamma s(t).
$$

这里 chromatin 自己有动态方程，RNA 的 transcription input 是 $\alpha^{(k)}c(t)$，所以模型是完整的链条：

```text
chromatin accessibility c(t)
        -> unspliced RNA u(t)
        -> spliced RNA s(t)
```

源码里 `predict_exp` 给出单个 phase 的解析解，`generate_exp` 按 model 0/1/2 和 switch times 拼出完整轨迹（`MultiVelo/src/multivelo/dynamical_chrom_func.py:142-191`; `MultiVelo/src/multivelo/dynamical_chrom_func.py:211-330`）。

CRAK-Velo 的数学结构更像“RNA 主模型 + chromatin 约束项”。它先用 RBF 曲线拟合 spliced RNA：

$$
\hat{s}_g(t)=h_g e^{-a_g(t_{ng}-\tau_g)^2}+o_g,
$$

再由 $\hat{s}_g(t)$ 推导 $\hat{u}_g(t)$ 和 $\hat{u}'_g(t)$（`paper source:111-129`; `CRAK-Velo/crak-velo/model/optimize_utils.py:87-102`）。chromatin 不是独立 ODE，而是进入 transcription rate：

$$
c^g(t)=\eta_g\sum_r^{R_g}w_r^g f(\phi_r^n(t)).
$$

然后 CRAK-Velo 用这个 $c^g(t)$ 构造 ATAC-derived unspliced derivative，并要求它和 RBF/RNA-derived derivative 对齐（`paper source:131-153`; `CRAK-Velo/crak-velo/model/optimize_utils.py:187-219`; `CRAK-Velo/crak-velo/model/recover_paras.py:136-151`）。

因此，两者的 chromatin 角色不同：

- MultiVelo：chromatin 是 ODE 状态变量，直接被拟合为 $c(t)$；
- CRAK-Velo：chromatin 是解释 transcription rate 的外部动态输入，用来约束 $\hat{u}'_g(t)$。

#### 12.3 时间和状态解释的差别

MultiVelo 的时间解释更“阶段化”。它有 chromatin state $k_c$ 和 RNA state $k$，并允许 chromatin closing 与 transcription repression 有两种顺序：chromatin 先关是 model 1，transcription 先关是 model 2（`MultiVelo/paper source/.../Li et al. - 2023 ... .md:49-55`）。因此 MultiVelo 可以自然定义四类 gene-cell state：

- primed；
- coupled on；
- decoupled；
- coupled off。

源码里 `compute_velocity` 也按 `t_sw1/t_sw2/t_sw3` 或 `fit_state` 把细胞分成 state 0/1/2/3，再按 model 1 或 model 2 调用不同 phase 的 velocity equation（`MultiVelo/src/multivelo/dynamical_chrom_func.py:603-723`）。

CRAK-Velo 没有 model 1/model 2，也没有 primed/coupled/decoupled/coupled-off 这类离散 state。它学习的是连续 latent time、gene-cell time、RBF 参数、region weights 和 ATAC-derived derivative。下游解释更多是：

- velocity field 是否更符合预期发育方向；
- chromatin-unspliced 表示是否更能分离 cell type；
- 低熵基因和 region weights 是否给出有意义的 gene-region/TF 解释；
- 单个基因如 KLF1 或 Jag2 的 region kinetics 是否和 unspliced RNA 在 pseudotime 上耦合（`paper source:49-71`; `paper source:210-244`）。

所以，如果研究问题是“chromatin closing 和 transcription repression 谁先发生”，MultiVelo 的 M1/M2 和 switch-time 框架更直接；如果研究问题是“哪些 nearby regions 对这个基因的 velocity/transcription rate 贡献最大”，CRAK-Velo 的 $w_r^g$ 和 region kinetics 更直接。

#### 12.4 细胞时间分配方式的差别

MultiVelo 的 cell time 来自三维轨迹投影。给定一组参数后，它先生成理论轨迹的 anchor points，再把每个细胞的观测 $(c,u,s)$ 投影到最近的 anchor。源码中 `anchor_points` 把时间轴分成四段，`calculate_dist_and_time` 调用 `generate_exp` 得到每段理论表达，再用 KDTree 在 $(c,u,s)$ 空间中找最近点，输出 `state_pred` 和 `t_pred`（`MultiVelo/src/multivelo/dynamical_chrom_func.py:747-773`; `MultiVelo/src/multivelo/dynamical_chrom_func.py:789-905`）。

CRAK-Velo 的 cell time reassignment 更接近 UniTVelo 式的时间匹配，但额外加入 ATAC derivative consistency。它用 3000 个候选时间点计算 `s_predict/u_predict` 和 `u_deri_func`，再把每个 cell-gene 匹配到使下面距离最小的时间：

$$
\sqrt{(u_{obs}-\hat{u})^2+(s_{obs}-\hat{s})^2+(u'^{ATAC}-\hat{u}')^2}.
$$

匹配后再把 gene-specific time 聚合成 unified time，并用新 pseudotime 重排 accessibility（`CRAK-Velo/crak-velo/model/recover_paras.py:54-76`; `CRAK-Velo/crak-velo/model/optimize_utils.py:133-169`; `CRAK-Velo/crak-velo/model/optimize_utils.py:259-276`）。

所以两者都在“把细胞放回一条动力学轨迹上”，但距离空间不同：

- MultiVelo：在 $(c,u,s)$ 三维表达/可及性空间投影；
- CRAK-Velo：在 $(s,u,u'^{ATAC}\text{ vs }\hat{u}')$ 这种 RNA fit + derivative consistency 空间中匹配。

#### 12.5 参数优化方式的差别

MultiVelo 是逐基因的轨迹拟合器。主入口 `recover_dynamics_chrom` 默认 `max_iter=5`、`n_anchors=500`，可选择 Nelder-Mead、Adam 或 neural network time prediction；默认如果 `adam=False`，MSE minimization 使用 Nelder-Mead（`MultiVelo/src/multivelo/dynamical_chrom_func.py:4384-4456`）。单基因内部 `fit_dyn` 会分块优化不同参数：先调 switch time 和 chromatin rate，再调 chromatin closing scale/rescale，再调 RNA switch time 和 $\alpha$，再调 $\beta$ 和 unspliced rescale，之后调 $\alpha,\gamma$，最后调 switch times（`MultiVelo/src/multivelo/dynamical_chrom_func.py:2837-2997`）。

CRAK-Velo 的实现是 TensorFlow/Adam 风格的矩阵化优化。`fit_likelihood` 每个 epoch 同时持有所有基因的参数矩阵，默认配置 `epochs=10000`、`learning_rate=1e-2`。前半程按 400 epoch 切换 spliced/RBF 参数子集和 unspliced/kinetic 参数子集，后半程把主要参数一起放开；每 800 epoch 重新分配 `t_cell`（`CRAK-Velo/crak-velo/model/recover_paras.py:241-285`; `CRAK-Velo/crak-velo/model/optimize_utils.py:223-245`; `CRAK-Velo/crak-velo/config/config_main_HSPC.json:27-45`）。

这里的工程取舍也不同：

- MultiVelo 的拟合更像“每个基因各自拟合一个结构化 ODE 状态机”；
- CRAK-Velo 的拟合更像“在所有 velocity genes 上共同优化 RBF/RNA 参数和 region weights，并周期性更新时间”。

#### 12.6 输出结果的差别

MultiVelo 输出的是一个带完整三模态轨迹解释的结果对象。源码文档列出的核心输出包括 `fit_alpha_c/fit_alpha/fit_beta/fit_gamma`、`fit_t_sw1/2/3`、`fit_model`、`fit_likelihood`、anchor curves、`fit_t`、`fit_state`、`velo_s/velo_u/velo_chrom` 等（`MultiVelo/src/multivelo/dynamical_chrom_func.py:4553-4599`; `MultiVelo/src/multivelo/dynamical_chrom_func.py:5061-5114`）。这些输出服务于：

- 每个 gene 的 M1/M2 分类；
- priming/decoupling interval；
- chromatin/RNA/spliced 三个方向的 velocity；
- dynamic plot 中的 state-colored trajectory。

CRAK-Velo 输出更偏 RNA velocity 和 region-weight 解释。源码保存 `velocity`、`fit_t`、`u_derrivative`、`u_atac`、`Pred_s/Pred_u`、各类拟合参数，以及 `varm["fit_region_weights"]`（`CRAK-Velo/crak-velo/model/recover_paras.py:224-322`）。这些输出服务于：

- spliced derivative 形式的 RNA velocity；
- latent time；
- ATAC-derived derivative 与 RNA-derived derivative 的一致性检查；
- 每个 gene 周围 region 权重；
- region kinetics、GO/TF enrichment 等解释分析。

所以 MultiVelo 输出的是“这个基因的三变量轨迹和状态标签”；CRAK-Velo 输出的是“这个基因的 RNA velocity、ATAC derivative 约束项和 region-level regulatory weights”。

#### 12.7 可解释性的重点不同

MultiVelo 的解释性来自 **时间顺序和状态分类**。它回答的问题是：

- chromatin opening 是否早于 RNA induction；
- chromatin closing 是否早于 transcription repression；
- cell-gene 是否处于 primed/coupled/decoupled；
- gene 更像 model 1 还是 model 2；
- priming 或 decoupling interval 有多长。

CRAK-Velo 的解释性来自 **region weights 和 chromatin-derived transcription rate**。它回答的问题是：

- 某个 gene 周围哪些 region 被赋予高权重；
- region accessibility 变化是否领先或伴随 unspliced RNA；
- 低熵 gene 是否集中在特定生物过程；
- high-weighted regions 是否富集 TF binding；
- chromatin 信息是否让 velocity field 更合理。

这也是为什么 CRAK-Velo 论文会强调 KLF1/Jag2 这类 gene-region kinetic plot，而 MultiVelo 论文会强调 M1/M2、priming、decoupling 和 switch-time intervals。

#### 12.8 算法背后的 ATAC 生物学思想差别

从生物学直觉看，两者都接受同一个大前提：ATAC-seq 看到的是 chromatin accessibility，而 chromatin accessibility 影响转录机器能不能接近 promoter/enhancer，因此能补充 RNA-only velocity 看不到的上游调控信息。MultiVelo 论文明确说，RNA velocity 假设 induction phase 里的 transcription rate 比较统一，但真实的 promoter/enhancer chromatin compaction 会改变 transcription rate；从 euchromatin 到 heterochromatin 的转变会降低 transcription，因为转录机器更难接近 DNA（`MultiVelo/paper source/.../Li et al. - 2023 ... .md:37-41`）。CRAK-Velo 的出发点也类似：用 chromatin accessibility 解释 transcription rate，减少只从 RNA 数据学习转录速率带来的自由度和不稳定性（`paper source:39-47`）。

但两者把 ATAC 放进算法时，代表的生物对象不一样。

**MultiVelo 的 ATAC 思想：chromatin 是 upstream state。**

MultiVelo 把 ATAC 聚合成每个 gene 的一个 accessibility 状态 $c(t)$。这个 $c(t)$ 不是一个辅助特征，而是三 ODE 系统的第一个动态变量。它背后的生物假设是：

1. gene locus 的 promoter/enhancer accessibility 可以被压缩成一个有效开放程度 $c(t)$；
2. $c(t)$ 本身会随时间 opening 或 closing；
3. transcription input 与 $c(t)$ 成比例，即染色质越开放，转录输入越强；
4. chromatin state 和 RNA transcription state 可以不同步。

所以 MultiVelo 用 ATAC 主要是为了建模 **epigenome-transcriptome timing**：chromatin 可以先打开但 RNA 还没动，这就是 priming；chromatin closing 和 transcription repression 可以先后错开，这就是 decoupling；chromatin closing 先发生或 transcription repression 先发生，又形成 model 1/model 2（`MultiVelo/paper source/.../Li et al. - 2023 ... .md:47-55`; `MultiVelo/paper source/.../Li et al. - 2023 ... .md:73-79`）。

换句话说，MultiVelo 问的是：

```text
这个基因的 chromatin 状态和 RNA 状态在时间上如何错位？
chromatin opening/closing 与 transcription on/off 谁先发生？
```

它把 ATAC 用成一个“时间结构传感器”。ATAC 的价值在于补上 RNA phase portrait 里看不见的先后顺序。例如论文说，一些细胞在 RNA 的 $(u,s)$ phase portrait 里挤在原点附近，但 chromatin accessibility 已经开始上升，因此可以分辨出 gene expression 之前的逐步变化（`MultiVelo/paper source/.../Li et al. - 2023 ... .md:67-77`）。

**CRAK-Velo 的 ATAC 思想：chromatin regions 是 candidate regulatory elements。**

CRAK-Velo 不把 ATAC 先压成单个 gene-level 状态，而是保留多个 nearby regions。它背后的生物假设是：

1. 一个 gene 的转录不是由一个抽象 $c(t)$ 控制，而可能由多个 nearby cis-regulatory regions 共同影响；
2. 每个 region 的开放概率 $\phi_r^n$ 表示该 region 在当前 cell 中有多可能处于可调控状态；
3. 不同 region 对同一个 gene 的贡献不同，因此需要学习 $w_r^g$；
4. 如果这些 region 真的解释 transcription rate，那么由它们加权得到的 $c^g(t)$ 应该和 RNA kinetic curve 推导出的 unspliced derivative 一致。

因此 CRAK-Velo 用 ATAC 主要是为了建模 **region-to-gene regulatory contribution**。论文明确说，固定 gene $g$ 周围窗口得到 regions 集合 $R_g$，用这些 regions 定义 ATAC-derived transcription rate $c^g(t)$，并且不同 region around gene $g$ 有不同权重 $w_r^g$ 需要推断（`paper source:131-145`）。后面的低熵基因和 TF enrichment 也沿着这个思想展开：如果某个 gene 的权重集中在少数 regions，说明它可能由更特异的调控元件驱动；如果 high-weighted regions 富集 TF binding，说明这些 regions 可能是真正活跃的调控位点（`paper source:212-244`）。

换句话说，CRAK-Velo 问的是：

```text
这个基因附近哪些 ATAC regions 真正在解释 transcription dynamics？
这些 region 的活动能否让 RNA velocity 的导数更符合 chromatin 状态？
```

它把 ATAC 用成一个“调控来源解释器”。ATAC 的价值不只是告诉你 chromatin 早于 RNA，而是告诉你 **哪些具体 regions** 可能推动了某个 gene 的表达变化。论文在 KLF1/Jag2 例子里强调的也正是这一点：不同 regions 的贡献会随 pseudotime 改变，proximal 或高权重 regions 可以在 gene activation 时占主导（`paper source:53-56`; `paper source:67-75`; `paper source:218-224`）。

因此，两者的生物学差别可以更直白地说成：

| 问题 | MultiVelo 的 ATAC 视角 | CRAK-Velo 的 ATAC 视角 |
|---|---|---|
| ATAC 代表什么 | 一个 gene locus 的整体开放状态 $c(t)$ | gene 周围多个 regions 的开放概率 $\phi_r^n$ |
| 生物假设 | chromatin opening/closing 是 transcription dynamics 的上游状态 | 不同 cis-regulatory regions 以不同权重调控 transcription rate |
| 最关心的生物现象 | priming、decoupling、M1/M2 时序差异 | region specificity、low-entropy genes、TF binding enrichment、region kinetics |
| ATAC 如何进入模型 | 作为 ODE 状态变量，直接门控 $du/dt$ 的 transcription input | 作为 weighted regional signal，构造 $c^g(t)$ 并约束 $\hat{u}'_g(t)$ |
| 解释单位 | gene-level timing/state | region-gene contribution |

这也解释了为什么 CRAK-Velo 会说自己比 MultiVelo 更强调 individual chromatin regions 如何 shape transcriptional trajectories。它不是只想判断 chromatin 是否早于 RNA，而是想把 velocity 和 region-level regulatory architecture 接起来（`paper source:75-75`）。

#### 12.9 复现和代码边界的差别

MultiVelo 是更成熟的公开软件包：论文和本地文档都记录了 PyPI/Bioconda/GitHub 可用性，源码包含完整 `recover_dynamics_chrom`、velocity graph、latent time、dynamic plot 等工作流（`MultiVelo/summary.md`; `MultiVelo/src/multivelo/dynamical_chrom_func.py:4384-4599`）。它的代价是预处理链更重：peak-to-gene aggregation、TF-IDF、WNN smoothing、Seurat/Signac/R/Python 之间的协作都比较多（`MultiVelo/paper source/.../Li et al. - 2023 ... .md:513-531`）。

CRAK-Velo 的核心模型代码更紧凑，主要 fitting path 能在 `main.py`、`preprocessing.py`、`velocity.py`、`optimize_utils.py`、`recover_paras.py` 中追踪。但当前仓库快照的 code-paper fidelity 是 **medium**：Eq. 3 主要在 notebook preprocessing，Eq. 11 源码使用 `self.Mu` 而不是论文公式中的 $\hat{u}_g(t)$，Eq. 13 实际优化 staged squared-error residual 而不是直接返回 negative log-likelihood，低熵排序和 TF-binding enrichment 的源码实现未找到。

#### 12.10 一张表总结

| 维度 | MultiVelo | CRAK-Velo |
|---|---|---|
| 论文定位 | *Nature Biotechnology* 2023，multi-omic velocity 三变量 ODE | *Genome Biology* 2026，在 UniTVelo/RBF RNA kinetic curve 上加入 chromatin accessibility 约束 |
| ATAC 背后的生物思想 | ATAC 是 gene-level upstream chromatin state，用来解释 chromatin 与 RNA 的时间错位 | ATAC 是 region-level regulatory evidence，用来解释哪些 cis-regulatory regions 驱动 transcription dynamics |
| chromatin 表示 | gene-level $c(t)$，由 peaks 聚合、TF-IDF、WNN smoothing 得到 | region-level $\phi_r^n$，由 cisTopic smoothing 得到，再通过 `B[region,gene]` 连接 gene |
| 核心方程 | 显式 ODE：$dc/dt,du/dt,ds/dt$ | RBF $\hat{s}_g(t)$ 与 $\hat{u}_g(t)$，加 $c^g(t)=\eta_g\sum_r w_r^g f(\phi_r)$ |
| chromatin 如何影响 RNA | $du/dt=\alpha^{(k)}c(t)-\beta u(t)$，chromatin 直接门控 transcription input | $c^g(t)$ 构造 ATAC-derived derivative，与 RNA-derived $\hat{u}'_g(t)$ 对齐 |
| cell time | 把 $(c,u,s)$ 投影到 ODE anchor trajectory | 用 `(s,u,ATAC derivative consistency)` 在 3000 点时间网格上匹配 |
| 状态解释 | M1/M2、primed、coupled-on、decoupled、coupled-off | 连续 latent time、velocity、region weights；没有 M1/M2 四状态框架 |
| 优化方式 | 逐基因解析轨迹 + 最近点投影 + Nelder-Mead 分块优化，默认也支持 Adam/NN 选项 | TensorFlow Adam，staged residual loss，周期性更新 cell time 和 accessibility ordering |
| 主要输出 | `fit_model`、switch times、`fit_state`、`velo_chrom/velo_u/velo_s`、anchor curves | `velocity`、`fit_t`、`u_atac`、`u_derrivative`、`fit_region_weights`、latent time |
| 最强解释点 | chromatin 与 transcription 的先后顺序、priming/decoupling 时间窗 | 哪些 regulatory regions 影响某 gene，以及 chromatin-derived derivative 如何约束 RNA velocity |

因此，不应该把 CRAK-Velo 理解成“简化版 MultiVelo 三 ODE”。更准确的理解是：CRAK-Velo 接受 MultiVelo 的核心生物动机，即 chromatin accessibility 能改进 RNA velocity，但它选择了另一条工程路径：不显式拟合 chromatin opening/closing ODE，而是在 UniTVelo/RBF RNA 曲线外加一个由 nearby regions 加权得到的 transcription-rate/derivative 约束。这样牺牲了 MultiVelo 的 M1/M2 和 priming/decoupling 状态解释，但换来了更直接的 region-gene weight 解释和更轻量的 chromatin integration 形式。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CRAK-Velo Summary

CRAK-Velo is a semi-mechanistic RNA velocity method for single-cell multiome data. It integrates chromatin accessibility into velocity inference so that gene-level transcription rates are constrained by nearby accessible regions rather than inferred from spliced/unspliced RNA alone. The paper was published in *Genome Biology* in 2026 with DOI `10.1186/s13059-026-04086-y` (`paper source:1-9`, `paper source:31-35`).

### Problem

RNA velocity estimates future transcriptional state from spliced and unspliced RNA. Existing velocity models still need a transcription-rate model for each gene. The paper argues that this is limiting: binary-switch assumptions are restrictive, while fully data-driven transcription-rate estimation can introduce many parameters. Multiome assays provide chromatin accessibility in the same cells, so CRAK-Velo uses accessible regions as mechanistic evidence for transcriptional activity (`paper source:39-43`).

### Proposed Method

CRAK-Velo extends a UniTVelo-style parametric RNA kinetic model with a chromatin-derived transcription-rate term. The method:

- smooths scATAC-seq using cisTopic and computes region open probabilities (`paper source:91-107`);
- links accessible regions to nearby genes through a genomic window (`paper source:85-89`, `paper source:131-145`);
- models spliced RNA with an RBF curve and derives unspliced RNA dynamics (`paper source:111-129`);
- defines a gene transcription rate from normalized accessibility, learned region weights, and a gene-specific scale (`paper source:131-145`);
- reconciles the RBF-derived unspliced derivative with an ATAC-derived derivative (`paper source:147-153`);
- iteratively updates parameters and cell times, then reorders accessibility by inferred pseudotime (`paper source:177-184`).

The code implements the main fitting path in `crak-velo/`: `main.py` runs the pipeline, `preprocessing.py` builds the region-gene matrix, `velocity.py` prepares RNA/ATAC matrices and velocity genes, `optimize_utils.py` implements RBF and chromatin helper functions, and `recover_paras.py` optimizes the model and stores outputs (`CRAK-Velo/crak-velo/main.py:7-37`; `CRAK-Velo/crak-velo/model/preprocessing.py:23-103`; `CRAK-Velo/crak-velo/velocity/velocity.py:31-206`; `CRAK-Velo/crak-velo/model/optimize_utils.py:43-219`; `CRAK-Velo/crak-velo/model/recover_paras.py:224-322`).

### Evaluation

The paper evaluates CRAK-Velo on HSPC differentiation, 10x embryonic mouse brain, and an additional human cerebral cortex dataset. In the HSPC benchmark, the paper reports that CRAK-Velo better identifies expected terminal states and has stronger cross-boundary direction behavior than UniTVelo and MultiVelo (`paper source:47-51`). In the mouse brain benchmark, the paper reports that CRAK-Velo avoids a spurious Upper Layer to Deeper Layer flow recovered by the baselines, while all methods still miss ependymal terminality (`paper source:65-65`).

The figures visually support these claims: Fig. 1 and Fig. 2 show side-by-side velocity fields, CBDir or PAGA summaries, chromatin-unspliced deconvolution panels, accuracy histograms, GO/TF enrichment panels, and KLF1/Jag2 region-kinetic examples (`paper source:55-63`; inspected images `164bfee...jpg` and `d9375d...jpg`). Code support exists for KNN evaluation, CBDir, PAGA notebook calls, and region-kinetic plotting (`CRAK-Velo/crak-velo/supplement/eval_utils.py:54-273`; `CRAK-Velo/notebooks/Fig1.ipynb:461-534`; `CRAK-Velo/notebooks/Fig2.ipynb:299-342`; `CRAK-Velo/crak-velo/supplement/fitting_genes_regions.py:106-132`).

### Reproducibility And Code-Paper Match

The repository contains the core CRAK-Velo model and notebooks for preprocessing and figures. The paper states that code is available on Zenodo/GitHub and that detailed figure workflows are in repository notebooks (`paper source:262-268`). The checked snapshot is GitHub commit `938ba27cba01430a557ee36f86e75c204973c69d`.

Overall code-paper fidelity is **medium**. The main algorithmic idea is implemented: normalized cisTopic accessibility and learned region weights enter an ATAC-derived transcription/derivative term, and optimization stores velocities, latent times, fitted parameters, and region weights. Important caveats remain:

- Eq. 3 open-probability computation is present in `notebooks/preprocessing.ipynb`, not the main Python package (`CRAK-Velo/notebooks/preprocessing.ipynb:94-147`).
- The paper describes Eq. 13 as a negative log-likelihood, but the verified training objective returns a staged squared-error loss with a hard-coded ATAC-derivative penalty of 0.5 (`CRAK-Velo/crak-velo/model/recover_paras.py:166-207`).
- The ATAC-derived derivative source uses observed/preprocessed `self.Mu` where the paper formula uses fitted `\hat{u}_g(t)` (`CRAK-Velo/crak-velo/model/optimize_utils.py:216-219`; `paper source:147-153`).
- The entropy ranking and TF-binding enrichment implementations were not found in `crak-velo/` or notebooks, even though the paper and figures report these analyses (`paper source:210-244`).

Reproducibility rating: **3/5**. The core method code is present and reasonably traceable, but figure-level biological interpretation is only partially reproducible from visible source cells, cisTopic preprocessing depends on a separate repository and local paths, and some paper equations do not match the optimized source objective exactly.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
