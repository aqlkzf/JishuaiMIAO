---
layout: default
permalink: /paper-atlas/simvi-35534bbc/
title: "SIMVI"
nav: false
description: "空间组学数据里，一个细胞的表达模式通常同时受两类因素影响： 细胞内在状态：例如细胞类型、细胞周期、分化阶段等。 空间诱导状态：例如空间梯度、邻近细胞互作、局部微环境信号等。 难点在于，这两类因素经常纠缠在一起。比如同一种细胞类型本来就可能聚集在组织的某个区域；如果一个模型直接使用空间邻域信息学习嵌入，就可能把“细胞类型本身的空间分布”误当成“空间微环境造成的表达改变”。"
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
      <span>Cell-Cell Communication</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>SIMVI</h1>
    <p>SIMVI disentangles intrinsic and spatial-induced cellular states in spatial omics data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-58089-7" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SIMVI 方法中文解释

### 1. 这篇论文要解决什么问题？

空间组学数据里，一个细胞的表达模式通常同时受两类因素影响：

1. **细胞内在状态**：例如细胞类型、细胞周期、分化阶段等。
2. **空间诱导状态**：例如空间梯度、邻近细胞互作、局部微环境信号等。

难点在于，这两类因素经常纠缠在一起。比如同一种细胞类型本来就可能聚集在组织的某个区域；如果一个模型直接使用空间邻域信息学习嵌入，就可能把“细胞类型本身的空间分布”误当成“空间微环境造成的表达改变”。论文指出，许多空间组学方法主要学习空间可变基因、空间感知嵌入或细胞互作相关表达变化，但没有明确解决“内在变异”和“空间诱导变异”的可辨识拆分问题（`paper.md:21-35`）。

SIMVI 的目标就是把这两部分拆开：

- \(z\)：细胞内在变异，尽量表示细胞自身属性。
- \(s\)：空间诱导变异，尽量表示邻域和微环境带来的状态。

学到这两个表示之后，SIMVI 不只做聚类或整合，还进一步用 \(s\) 来估计每个细胞、每个基因的空间效应（`paper.md:47-59`, `paper.md:329-373`）。

### 2. 输入、输出和总体流程

论文把输入定义为：

- \(X\in &#123;&#123;\mathbb{R}}}^{n\times p}\)：空间组学计数矩阵，\(n\) 个细胞/点，\(p\) 个基因。
- \(C\in &#123;&#123;\mathbb{R}}}^{n\times 2}\)：每个细胞的二维空间坐标。
- \(G=(V,E)\)：基于坐标构建的空间图。论文中全程使用 \(k=10\) 的 kNN 图，并定义 \(N(i)=\{j|(i,j)\in E\}\) 为细胞 \(i\) 的邻居（`paper.md:201-204`）。

代码中，`SimVIModel.extract_edge_index` 默认 `method='knn'`、`n_neighbors=10`，用 `kneighbors_graph` 从 `adata.obsm[spatial_key]` 构图；也提供 Delaunay 分支，但不是默认路径（`SIMVI/simvi/model/simvi.py:234-312`）。

整体计算流程可以概括为：

```text
计数矩阵 X + 空间坐标 C
        |
        v
构建空间图 G，默认 kNN, k=10
        |
        v
变分推断
  - MLP 编码器：学习内在后验 q_Phi(z | x, b)
  - GAT 编码器：利用空间图学习空间后验 q_Psi(s | neighborhood)
  - 可选 library size 后验 q_Phi_l(l | x, b)
        |
        v
解码器 f(z, s, b)：重构计数矩阵，默认 ZINB 似然
        |
        v
训练目标
  - 重构损失
  - z 的 KL 项
  - s 的小权重 KL 项
  - library size KL 项，如果不使用观测 library size
  - z 和 s 的非对称独立性正则
        |
        v
得到 intrinsic embedding 和 spatial embedding
        |
        v
空间效应估计
  - 对 s 做 archetypal analysis 得到 archetype 权重 s'
  - 用 z 对表达 Y 和 s' 做残差化
  - 线性回归估计细胞/基因级空间效应
```

代码中，`get_latent_representation(..., representation_kind="intrinsic")` 返回 `q_m`，`representation_kind="interaction"` 返回 `qgat_m`，`representation_kind="all"` 返回拼接表示 `qall_m`（`SIMVI/simvi/model/simvi.py:318-380`）。

### 3. 生成模型：论文提出的概率故事

论文的生成过程是：

$$
z \sim \,&#123;&#123;\rm{Normal}}}\,(0,I)\\
\pi : \,&#123;&#123;\rm{permutation}}}\,,\,p(\pi | z,G)=\frac{1}{Z}{U}_{G}({z}^{\pi })\\
{s}^{i}| z \sim \,&#123;&#123;\rm{Normal}}}\,(A{z}^{\pi (N(i))},{\Sigma }_{s})\\
{l}^{i} \sim \,&#123;&#123;\rm{LogNormal}}}\,\left({l}_{\mu }^&#123;&#123;b}^{i}},{l}_{\sigma }^&#123;&#123;b}^{i}}\right)\\
{\rho }^{i}=\,f({z}^{\pi (i)},{s}^{i},{b}^{i})\\
{w}_{g}^{i} \sim \,&#123;&#123;\rm{Gamma}}}\,({\rho }_{g}^{i},{\theta }_{g})\\
{y}_{g}^{i} \sim \,&#123;&#123;\rm{Poisson}}}\,({l}^{i}{w}_{g}^{i})\\
{h}_{g}^{i} \sim \,&#123;&#123;\rm{Bernoulli}}}\,\left({f}_{h}^{g}({z}^{\pi (i)},{s}^{i},{b}^{i})\right)\\
{x}_{g}^{i}=\,{h}_{g}^{i}{y}_{g}^{i}
$$

这个生成模型的关键想法是：

- \(z^i\) 是细胞内在状态，先验为标准正态，并且本身不依赖空间图。
- \(\pi\) 是一个把内在状态分配到空间位置的排列，概率由图相关的 \(U_G(z^\pi)\) 控制，用来表达“细胞类型/状态可能有空间组织”。
- \(s^i\) 依赖邻域内在状态 \(z^{\pi(N(i))}\)，表示空间诱导变异。
- \(l^i\)、\(f\)、\(\theta\)、\(f_h\) 继承 scVI 风格的 ZINB 计数建模（`paper.md:213-221`）。

代码验证结果：

- 包内确实实现了 scVI 风格的解码器和 ZINB/NB 重构损失。`DecoderSCVI` 接收拼接潜变量、library size 和 batch 信息，`reconstruction_loss` 默认调用 `ZeroInflatedNegativeBinomial`（`SIMVI/simvi/module/simvi.py:132-141`, `SIMVI/simvi/module/simvi.py:274-346`）。
- 没有在本地 Python 源码中找到可执行的 \(U_G(z^\pi)\) 概率排列先验项。论文后面也明确说这个项实践中不可处理，因此在损失函数中只使用可行的部分（`paper.md:270-278`；搜索范围：`SIMVI/simvi/module/simvi.py`、`SIMVI/simvi/model/simvi.py`、workspace CodeGraph Python 索引）。

### 4. 变分后验：如何从数据推断 \(z\)、\(s\)、\(l\)

论文写出的后验分解为：

$$
{q}_{\Phi }({z}^{\pi i},{s}^{i},{l}^{i}| {x}^{i},{x}^{N(i)},{b}^{i})=
{q}_{\Phi }({z}^{\pi i}| {x}^{i},{b}^{i})
{q}_{\Psi }({s}^{i}| {x}^{N(i)},{b}^{N(i)})
{q}_&#123;&#123;\Phi }_{l}}({l}^{i}| {x}^{i},{b}^{i})
$$

也就是说：

- \(q_\Phi(z)\)：只看细胞自己的表达和 batch，学习内在变异。
- \(q_\Psi(s)\)：看邻域表达相关信息，学习空间诱导变异。
- \(q_{\Phi_l}(l)\)：学习 library size，或者在实践中使用观测 library size。

论文说 \(q_\Psi(s)\) 使用一层 dynamic GAT 来建模（`paper.md:227-235`）。代码中对应关系如下：

| 论文符号 | 代码变量 | 位置 | 说明 |
|---|---|---|---|
| \(q_\Phi(z)\) 均值/方差 | `q_m`, `q_v` | `SIMVI/simvi/module/simvi.py:202-203` | `base_encoder` 从 `log(1+x)` 产生。 |
| 内在潜变量样本 | `z` | `SIMVI/simvi/module/simvi.py:202-203` | encoder sample。 |
| \(q_\Psi(s)\) 均值/方差 | `qgat_m`, `qgat_v` | `SIMVI/simvi/module/simvi.py:206-212` | `GATv2Conv` 在 `edge_index` 上处理 `q_m[:, -self.n_spatial:]`。 |
| 空间潜变量样本 | `z_gat` | `SIMVI/simvi/module/simvi.py:211-214` | 从 `Normal(qgat_m, qgat_v.sqrt())` 采样。 |
| 解码器输入 | `z_all` | `SIMVI/simvi/module/simvi.py:214-215` | 代码顺序是 `[z_gat, z]`。 |
| library size | `library`, `ql_m`, `ql_v` | `SIMVI/simvi/module/simvi.py:198-199`, `SIMVI/simvi/module/simvi.py:223-226` | 默认使用观测 library size；可切换到学习分支。 |

需要注意：论文写法是 \(q_\Psi(s^i|x^{N(i)},b^{N(i)})\)，代码实现是先用 MLP 得到 intrinsic encoder mean，再把其中最后 `n_spatial` 个维度送入 GAT。这和论文的架构思想一致，但不是逐字逐符号地实现完整后验表达式。

### 5. 训练目标：有效 ELBO 和非对称正则

论文从完整 ELBO 出发，推导出 \(z^\pi\) 的 KL 项包含两部分：

$$
{\sum}_{i}{D}_&#123;&#123;&#123;&#123;\rm{KL}}}}}(q({z}^{\pi i}| {x}^{i},{b}^{i},G)| | &#123;&#123;{\mathcal{N}}}}(0,I))+
&#123;&#123;\mathbb{E}}}_{q({z}^{\pi }| x,b,G)}\log \frac{1/n!}&#123;&#123;U}_{G}({z}^{\pi })/Z}
$$

实践中只保留第一部分，因为 \(U\) 不可处理，且作者认为如果后验能很好刻画观测，它会自动捕捉共定位模式（`paper.md:246-278`）。

空间潜变量的 KL 项也被替换成小权重的标准正态正则：

$$
\alpha {\sum}_{i}{D}_&#123;&#123;&#123;&#123;\rm{KL}}}}}(
q({s}^{i}| {x}^{N(i)},{b}^{N(i)},G)
| | &#123;&#123;{\mathcal{N}}}}(0,I))
$$

论文随后强调，仅优化 ELBO 不足以保证拆分，因为 \(z\) 可能吸收所有信息。因此 SIMVI 加入 \(z\) 和 \(s\) 的独立性正则，且只正则 \(z\) 分支。两种正则形式是：

$$
I(z,s)=\frac{1}{2}\log \frac{\det {\hat{\Sigma }}_{s}\det {\hat{\Sigma }}_{z}}{\det {\hat{\Sigma }}_{[z,s]}}
$$

以及

$$
I(z,s)=\,&#123;&#123;\rm{MMD}}}\,(p([z,s]),\,&#123;&#123;{\mathcal{N}}}}(0,I)).
$$

最终 Eq. (14) 写成：

$$
&#123;&#123;{\rm{Loss}}}}\, &#123;&#123;{\rm{for}}}}\,({\phi }_{1},{\phi }_{2})=-\,&#123;&#123;\rm{ELBO}}}\,+\beta I(z,s),
$$

$$
&#123;&#123;{\rm{Loss}}}}\, &#123;&#123;{\rm{for}}}}\, ({\psi }_{1},{\psi }_{2})\, &#123;&#123;{\rm{and}}}} \, &#123;&#123;{\rm{for}}}}\, &#123;&#123;{\rm{other}}}} \, &#123;&#123;{\rm{parameters}}}}\,=-\,&#123;&#123;\rm{ELBO}}}.
$$

代码验证结果：

- `recon_loss`、`kl_z`、`kl_zgat`、`kl_library` 在 `_generic_loss` 中计算（`SIMVI/simvi/module/simvi.py:415-455`）。
- 实际标量损失是 `mean(reconst_loss + weight * weighted_kl_local) + weight * lam_mi * mi_loss`（`SIMVI/simvi/module/simvi.py:481-486`）。
- 默认 `reg_to_use='mmd'`、`kl_gatweight=0.01`、`lam_mi=1000`（`SIMVI/simvi/model/simvi.py:85-124`）。
- 代码没有暴露两个优化器或两个独立 branch loss。它通过在正则里对空间潜变量 `z_gat` 做 `.detach()` 来让独立性正则主要影响 \(z\) 路径：MI 路径在 `SIMVI/simvi/module/simvi.py:503-521`，MMD 路径在 `SIMVI/simvi/module/simvi.py:523-536`。

因此，Eq. (14) 在代码中更像是“单一总损失 + detach 实现的非对称梯度”，而不是显式分支优化。

### 6. permutation-based pretraining 是什么？

论文提出可选的去噪自编码预训练：在训练 batch 中随机选一部分基因，把这些基因的值在细胞之间打乱，同时保留每个基因的边际分布，然后让模型从加噪版本重构原始数据（`paper.md:323-326`）。

代码中：

- `_get_inference_input_from_concat_tensors` 复制输入 `x_mask`，用 `torch.rand(x.shape[1]) < permutation_rate` 选择基因，然后默认把这些基因在细胞之间随机重排（`SIMVI/simvi/module/simvi.py:143-164`）。
- `train` 在 `epoch < mae_epochs` 时设置 `eval_mode=False`，从而启用输入扰动；之后切换到 `eval_mode=True`（`SIMVI/simvi/model/simvi.py:677-711`, `SIMVI/simvi/model/simvi.py:800-806`）。

所以这不是一个单独脚本中的预训练阶段，而是普通训练循环早期的输入扰动模式。

### 7. 为什么训练时要全图推断、mask loss？

论文指出，一般连通图不容易自然切分成独立 mini-batch，所以采用类似半监督节点分类的训练方式：先把全数据和全图送入模型计算每个细胞的中间输出，再只在训练/验证细胞子集上计算 loss（`paper.md:320-321`）。

代码中：

- `train` 随机划分 `train_mask`、`val_mask`、`test_mask`（`SIMVI/simvi/model/simvi.py:736-741`）。
- `_train` 每次先对完整 `data` 和 `edge_index` 运行 `model.inference`，再按 mask 或 batch index 截取 latent output，送入 decoder 和 loss（`SIMVI/simvi/model/simvi.py:817-860`）。
- `_eval` 也先全图推断，再截取验证细胞（`SIMVI/simvi/model/simvi.py:863-895`）。

这和论文的训练描述匹配。

### 8. 空间效应估计：从 \(s\) 到每个基因/细胞的 SE

SIMVI 的下游空间效应估计把空间变异 \(s\) 当作连续 treatment，把内在变异 \(z\) 当作 covariate。流程是：

1. 用 PCHA/archetypal analysis 把 \(s\) 转成 archetype 权重 \(s'\)。论文使用 py_PCHA，`delta=0.1`、`conv_crit=1E-5`、`maxiter=200`（`paper.md:329-335`）。
2. 用线性回归残差化：

$$
Y \sim \hat{Y}(z),\,{s}^&#123;&#123;\prime} } \sim {\hat{s}}^&#123;&#123;\prime} }(z);\quad
\bar{Y}=Y-\hat{Y}(z),\,{\bar{s}}^&#123;&#123;\prime} }={s}^&#123;&#123;\prime} }-{\hat{s}}^&#123;&#123;\prime} }(z).
$$

3. 拟合空间效应模型：

$$
\bar{Y} \sim {\sum}_{j}{\bar{s}}_{j}^&#123;&#123;\prime} }z{\beta }_{j}+{c}_{j}{\bar{s}}_{j}^&#123;&#123;\prime} }.
$$

4. 得到空间效应：

$$
{\sum}_{j}{\bar{s}}_{j}^&#123;&#123;\prime} }z{\beta }_{j}+{c}_{j}{\bar{s}}_{j}^&#123;&#123;\prime} }.
$$

论文还提出 individual mode：

$$
\bar{Y} \sim {\bar{s}}_{j}^&#123;&#123;\prime} }z{\beta }_{j}+{c}_{j}{\bar{s}}_{j}^&#123;&#123;\prime} }.
$$

并说明研究中使用 individual mode（`paper.md:365-373`）。

代码中，`get_se` 完成这个流程：

- 如果没有外部 `adata`，先从模型推断 `latent_z` 和 `latent_s`；否则从 `adata.obsm` 读取（`SIMVI/simvi/model/simvi.py:541-559`）。
- 对表达矩阵做 `normalize_total` 和 `log1p`，并可把 batch、cell type 或额外 obsm 作为 covariate 拼到 `latent_z`（`SIMVI/simvi/model/simvi.py:560-579`）。
- `get_archetypes` 调用 `py_pcha.PCHA`（`SIMVI/simvi/model/simvi.py:433-472`, `SIMVI/simvi/model/simvi.py:581-584`）。
- 默认 `mode='individual'`，逐 archetype 拟合残差化和加权线性回归，返回空间效应、\(R^2\)、p 值和 archetype 权重（`SIMVI/simvi/model/simvi.py:608-649`）。
- joint mode 也存在，会构造 \(z\) 和所有 residual archetype weight 的交互项（`SIMVI/simvi/model/simvi.py:650-671`）。

### 9. 实验结果怎么支持方法？

论文在五类数据上评估：

- MERFISH human cortex：用细胞类型、batch、layer、MYH11 niche 评估拆分效果（`paper.md:68-88`, `paper.md:379-394`）。
- Slide-seqV2 mouse hippocampus：评估空间 niche 是否对应解剖结构（`paper.md:88-108`, `paper.md:397-406`）。
- Slide-tags human tonsil：分析 germinal center B cell 的空间 niche 和循环状态（`paper.md:111-128`, `paper.md:409-415`）。
- Spatial multiome melanoma：发现肿瘤微环境 niche 和 ATAC spatial-effect state（`paper.md:131-157`, `paper.md:418-424`）。
- CosMx melanoma cohort：分析 macrophage 空间状态和 ligand-receptor / spatial effect 相关结构（`paper.md:160-183`, `paper.md:430-448`）。

本地检查过六张主图：

- Fig. 1-2 支持“内在表示”和“空间表示”分工不同。
- Fig. 3 支持从空间表示估计 gene/cell-level spatial effect 的下游流程。
- Fig. 4-6 展示 tonsil、multiome melanoma、cohort melanoma 中的生物学应用。

但图像本身不能替代 Source Data 重新计算，也不能证明补充材料中的理论推导。

### 10. 代码和论文的一致性

总体代码-论文一致性评估为 **medium**。

匹配较好的部分：

- kNN 空间图构建。
- intrinsic encoder + GAT spatial encoder。
- scVI 风格 decoder 和 ZINB/NB 重构损失。
- 有效 ELBO 中的重构、KL、library、空间 KL surrogate。
- MI/MMD 独立性正则。
- permutation-based denoising pretraining。
- 全图推断、mask loss 的训练方式。
- `get_se` 中的 archetype + residual regression 空间效应估计。

重要差异和缺口：

- 本地代码中没有找到可执行的 \(U_G(z^\pi)\) 排列先验 utility 项；论文也说明实践中会丢弃这个不可处理项。
- Eq. (14) 论文写成分支特异目标，代码中是单一总损失，并通过 `z_gat.detach()` 近似实现非对称正则。
- `SUPP_MD=none`，所以 Supplementary Note 1/2 的 identifiability 和 positivity 数学推导在本地证据中缺失。
- 论文代码可用性中还提到 `https://github.com/MingzeDong/SIMVI_reproducibility`，但本 workspace 只克隆了官方 package repo `https://github.com/KlugerLab/SIMVI`。因此本地代码足以审计核心方法实现，不足以复现所有 figure 和 benchmark。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SIMVI Summary

SIMVI (Spatial Interaction Modeling using Variational Inference) is a deep variational framework for spatial omics that separates cell-intrinsic variation from spatial-induced variation. The paper is motivated by a common ambiguity in spatial data: cell types and intrinsic states are often spatially organized, so an embedding that uses spatial neighborhoods can mistakenly treat cell identity as a spatial effect (`paper.md:21-35`). SIMVI addresses this by learning two coupled latent variables, \(z\) for intrinsic variation and \(s\) for spatial-induced variation, then using \(s\) for spatial niche analysis and single-cell spatial-effect estimation (`paper.md:47-59`, `paper.md:329-373`).

### Method In Brief

The input is a spatial omics count matrix \(X\), cell coordinates \(C\), and a k-nearest-neighbor graph \(G\) built with \(k=10\) (`paper.md:201-204`). The model uses a graph-unaware encoder for \(z\), a graph-aware GAT posterior for \(s\), and a scVI-like decoder for ZINB/NB count reconstruction (`paper.md:227-235`; `SIMVI/simvi/module/simvi.py:87-141`, `SIMVI/simvi/module/simvi.py:197-214`, `SIMVI/simvi/module/simvi.py:274-346`).

The paper derives an ELBO containing a graph-dependent permutation-prior utility \(U_G(z^\pi)\), but explicitly drops the intractable \(U_G\) term in the practical effective ELBO (`paper.md:246-300`). The package implements the practical loss as reconstruction loss plus weighted Gaussian KL terms plus MI/MMD independence regularization (`SIMVI/simvi/module/simvi.py:415-500`). SIMVI's Eq. (14) describes branch-specific asymmetric regularization; the package approximates this with a combined scalar loss where the spatial latent is detached inside the independence regularizer (`SIMVI/simvi/module/simvi.py:503-536`).

For downstream spatial effects, SIMVI transforms the learned spatial latent into archetype weights, residualizes both expression and archetype weights against intrinsic covariates, and fits linear models to estimate cell/gene-level spatial effects (`paper.md:329-373`; `SIMVI/simvi/model/simvi.py:433-671`).

### Evaluation And Results

The paper evaluates SIMVI on MERFISH human cortex, Slide-seqV2 mouse hippocampus, Slide-tags human tonsil, spatial multiome melanoma, and a newly generated cohort-level CosMx melanoma dataset (`paper.md:38-38`, `paper.md:189-189`). Figures 1-2 visually support the representation split: intrinsic embeddings group cell types while spatial embeddings emphasize layers, MYH11-localized niches, and hippocampal anatomical regions. Figure 3 supports the spatial-effect workflow and shows cleaner spatial patterns than raw normalized counts for representative genes. Figures 4-6 show downstream biological analyses in tonsil, spatial multiome melanoma, and cohort melanoma.

Reported results include stronger spatially relevant benchmark scores in cortex and hippocampus, germinal-center B-cell dynamics in tonsil, tumor niche and ATAC spatial-effect states in melanoma, and macrophage spatial states plus ligand-receptor/spatial-effect association patterns in cohort melanoma (`paper.md:82-108`, `paper.md:111-183`).

### Code-Paper Match

Overall code-paper fidelity is **medium**. The official package implements the central algorithmic path: kNN graph construction, intrinsic encoder, GAT spatial encoder, decoder likelihood, practical ELBO-like loss, denoising/permutation pretraining, full-graph masked training, latent extraction, archetypes, and spatial-effect estimation (`doc_code.md`). The main implementation is concentrated in `SIMVI/simvi/module/simvi.py` and `SIMVI/simvi/model/simvi.py`.

Important caveats:

- No executable `U_G(z^\pi)` permutation-prior utility term was found in the local package source; the paper says this term is dropped in practice.
- Eq. (14)'s branch-specific objective is implemented as a combined scalar loss with spatial latent detach in the regularizer, not as visibly separate branch optimizers.
- `SUPP_MD=none`, so Supplementary Note 1 identifiability derivations and Supplementary Note 2 positivity derivations are missing from local primary evidence.

### Reproducibility

The paper makes data and code available: CosMx melanoma data are on Zenodo, other analyzed datasets are public, the package repo is `https://github.com/KlugerLab/SIMVI`, and result-generation code is stated to be at `https://github.com/MingzeDong/SIMVI_reproducibility` (`paper.md:457-466`). This workspace acquired only the official package repo as canonical `code source`, recorded at commit `945afd210b92657a5127ba726bab5364a137736d`; the result-reproduction repo was not cloned.

The local package source is sufficient to audit the core method implementation, but not enough to reproduce every paper figure or benchmark. Missing local evidence includes supplementary markdown, source-data spreadsheets, exact preprocessing scripts, and the separate reproduction repository.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
