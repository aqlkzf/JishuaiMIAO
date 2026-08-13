---
layout: default
permalink: /paper-atlas/sckinetics-68948010/
title: "scKINETICS"
nav: false
wide: true
description: "scKINETICS 把细胞速度写成 x'=Ax，用 ATAC/motif 证据限制 A 的可学边，用 cluster-specific covariance 给 A 一个协表达先验，用 local manifold 给不可观测 velocity 加 truncated-normal bounds，再用 target-wise EM 学出 cluster-specific Ac。"
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
      <span>Bioinformatics · 2023</span>
    </div>
    <h1>scKINETICS</h1>
    <p>scKINETICS: inference of regulatory velocity with single-cell transcriptomics data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1093/bioinformatics/btad267" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scKINETICS">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/dpeerlab/scKINETICS" target="_blank" rel="noopener noreferrer" aria-label="Open code for scKINETICS">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scKINETICS 方法中文解读

### 0. 这篇方法到底在解决什么问题

scKINETICS 的目标不是单独画一张 RNA velocity stream，也不是单独推一个静态 GRN。它想把两个问题合在同一个模型里：

1. 每个细胞现在往表达空间的哪个方向移动？
2. 这个移动方向由哪些 TF-target 调控边驱动？

传统 RNA velocity 方法通常把每个基因的动态分开建模，例如用 unspliced/spliced RNA 估计未来方向；GRN 方法通常给出静态调控结构，却不直接给每个细胞一个 velocity。scKINETICS 的核心想法是把速度写成一个稀疏线性调控动力系统：

$$
\vec{x}'(t)=A\vec{x}(t).
$$

这里 $\vec{x}(t)$ 是一个细胞当前的表达向量，$\vec{x}'(t)$ 是该细胞的表达速度，$A$ 是要学习的带符号调控矩阵。这个矩阵有双重身份：

- **velocity operator**：用 $A\vec{x}$ 计算细胞速度。
- **signed GRN**：用 $A_{ij}$ 表示 regulator/TF $j$ 对 target gene $i$ 的表达变化率影响；正值可解释为 activation-like effect，负值可解释为 repression-like effect。

所以 scKINETICS 的一句话版本是：用 epigenetic evidence 限定哪些 TF-target 边可以存在，用 coexpression 给边权一个先验，用 local manifold 给不可观测的速度加约束，然后用 EM 同时学习 cluster-specific $A_c$ 和 per-cell velocities。

### 1. 一张图看完整计算框架

```text
scRNA-seq AnnData + ATAC/multiome/bulk peak evidence
  -> peak-to-gene annotation + motif scan
  -> TF-target mask G, TargetRecord dictionary
  -> PCA + optional MAGIC + positive expression transform
  -> cluster-specific transformed expression X_c
  -> masked covariance prior A_hat_c = Cov(X_c) * G_c
  -> kNN/Jaccard/DBSCAN local manifold bounds alpha_n, beta_n
  -> target-wise EM update for each cluster-specific A_c
  -> per-cell velocity v_n = A_c x_n
  -> velocity graph / embedding stream
  -> TF-column knockout activity score
```

这条链路里最关键的点是：velocity 不是先由别的方法算好再拿来解释；scKINETICS 在 EM 过程中把 velocity 当成 latent variable，并通过 $A$、coexpression prior 和 manifold bounds 联合约束它。

### 2. 输入、输出和证据边界

#### 2.1 输入

| 输入 | 代码对象/位置 | 作用 | 证据边界 |
|---|---|---|---|
| scRNA-seq AnnData | `adata` | 提供细胞表达矩阵、基因名、细胞/cluster 元数据 | Exact: `ExpectationMaximization.fit(adata, G, celltype_basis=...)` |
| cluster/cell-type labels | `adata.obs[celltype_basis]` | 决定每个 cluster 单独拟合一个 $A_c$ | Exact: `EM.py:149-190` |
| ATAC peaks / multiome peaks / bulk ATAC peaks | peak BED / selected peaks | 定义开放 chromatin 区域，用于候选调控边 | Exact for peak/motif pipeline; pancreas exact constants are `MISSING in source` |
| genome annotation | `TxDb.*`, ChIPseeker-style annotation | peak-to-gene mapping | Exact: `tf_targets.py:109-139`, `tf_targets.py:331-390` |
| motif resources | CisBP motif files, MOODS scan | 判断 peak 中可能有哪些 TF binding motifs | Exact: `tf_targets.py:50-76`, `tf_targets.py:261-329` |
| hyperparameters | `maxiter`, `tol`, `knn`, `sigma`, `sigma_prior`, `threads` | 控制 EM、manifold constraint 和 prior strength | Exact: `EM.py:25-48` |

论文的 pancreas regeneration 应用报告了 5501 cells、15497 genes、6575 peaks、1876 mask genes、1291 target-only genes、585 TFs、21.6% nonzero mask values。这些是 paper evidence；当前代码快照没有从源码或已打开数据 sidecar 直接验证这些常数，所以应保留 `MISSING in source`。

#### 2.2 输出

| 输出 | 代码对象 | 形状/含义 | 解释边界 |
|---|---|---|---|
| cluster-specific matrices | `model.A_`, `As[celltype]` | 每个 cluster 一个 genes x genes 的稀疏带符号矩阵 | 模型推断的调控 velocity operator，不是实验验证 GRN |
| per-cell velocities | `model.velocities_` | cells x velocity genes | 由 $A_cx_n$ 计算；regulator-only TFs 可能被过滤 |
| fitting curves | `model.curves` | target-wise marginal likelihood traces | 用于检查 EM 迭代行为 |
| velocity graph / embedding velocity | `VelocityGraph.velocity_graph`, `V_emb` | cell-neighbor transition / 2D arrows or stream | 可视化投影，不是 velocity 原始学习位置 |
| TF activity score | `percell_ablate(...)` output | cells x TFs cosine distance | in silico sensitivity score，不等同真实 knockout |

### 3. 变量、维度和代码名

| 论文符号 | 代码变量 | 维度 | 含义 |
|---|---|---|---|
| $\vec{x}_n(t)$ | `X_.values[n, :]` | genes | cell $n$ 的 transformed expression。代码使用 `adata.uns['X_<celltype>']`。 |
| $x_i'(t)$ | velocity for target gene `i` | scalar per cell/gene | target gene $i$ 的表达变化率。 |
| $A$, $A_c$ | `A`, `As[celltype]`, `self.A_` | genes x genes | 行是 target gene，列是 regulator/TF gene。 |
| $A_{ij}$ | `A[target_ix, TForder_ix]` | scalar | TF $j$ 对 target $i$ 的 velocity weight。 |
| $G_c$ | `G[celltype]`, `TargetRecord` | dictionary | target -> candidate TFs and indices。 |
| $\hat{A}_c$ | `celltype_priors[celltype]`, `ahat` | genes x genes 或 target-specific vector | cluster covariance 乘以 GRN mask 后的先验。 |
| $\sigma$ | `sigma` | scalar, default `5.0` | truncated-normal velocity likelihood 的尺度。 |
| $\hat{\sigma}$ | `sigma_prior` | scalar, default `1.0` | coexpression prior 的尺度；越小 prior 越强。 |
| $\alpha_n,\beta_n$ | `alpha`, `beta`, `alpha_all`, `beta_all` | cells x genes | 每个细胞、每个基因的 latent velocity lower/upper bounds。 |
| $\vec{a}_i$ | `a_s` | regulators of target $i$ | target $i$ 对应的 regulator weight vector。 |
| $E_1$ | `A_min` | regulators x regulators | M-step 二次项。 |
| $E_2$ | `B_min` | regulators | M-step 一次项。 |
| $A^*$ | `Amut` | genes x genes | 某个 TF column 被置零后的 perturbation matrix。 |

最容易混淆的是 `A` 的方向。论文写 $x_i'(t)=\sum_j x_j(t)A_{ij}$，所以 `A` 的**行**是 target，**列**是 regulator。代码计算速度时使用：

```python
velocity = np.dot(A, X_.values.T).T
```

它等价于对 cell-by-gene 表达矩阵右乘 $A^T$，最终输出还是 cell-by-gene 的 velocity。

### 4. 数学链条：从 ODE 到 EM

#### 4.1 target gene ODE

对 target gene $i$：

$$
x_i'(t)=\sum_{j=1}^{d_i}x_j(t)A_{ij}.
$$

$d_i$ 不是全基因数，而是 target $i$ 被 TF-target mask 允许的 regulator 数量。没有 motif/peak-to-gene evidence 的边固定为 0，EM 不会学习这些边。

#### 4.2 full-system ODE

所有 target 的方程合并为：

$$
\vec{x}'(t)=A\vec{x}(t).
$$

这个式子是 scKINETICS 的核心桥梁：$A$ 同时解释速度和调控网络。它不是普通 expression correlation network，因为 $A_{ij}$ 作用在 target expression derivative 上。

#### 4.3 analytic solution

论文指出线性系统有解析解：

$$
\vec{x}(t)=e^{At}\vec{x}(0).
$$

这个式子用于说明 fitted $A$ 可以外推 future expression，也用于论文 simulation 叙述。当前代码快照没有找到 matrix-exponential simulation script，因此这部分应写作 paper-only / `Not found` in code。

#### 4.4 coexpression prior

论文把每条候选边的权重建成：

$$
A_{ij}\sim N(\hat{A}_{ij},\hat{\sigma}).
$$

代码里 $\hat{A}_c$ 是 cluster-specific covariance 乘以 binary GRN mask：

$$
\hat{A}_c=\mathrm{Cov}(X_c)\odot G_c.
$$

这个 prior 有两个作用：初始化 EM，以及在更新时把边权拉向协表达给出的方向和大小。但协表达不是因果证据；它可能来自 batch、shared upstream regulator、cell-state gradient 或 compositional effect。

#### 4.5 truncated-normal latent velocity

真实 velocity 不可观测，所以 scKINETICS 用 local manifold 给它加上下界：

$$
\vec{x}'_n(t)\sim TruncN(A\vec{x}_n,\vec{\alpha}_n,\vec{\beta}_n,\sigma).
$$

直觉是：一个细胞的 immediate future state 应该落在局部 phenotype manifold 的某些 dense neighbor directions 附近。$\alpha_n,\beta_n$ 是每个 cell/gene 的 bounds，$\sigma$ 控制 likelihood 的宽度。

#### 4.6 EM 为什么需要存在

如果真实速度 $\vec{x}'$ 已经观测到，那么学习 $A$ 就近似是一个 masked linear regression：

$$
\vec{x}'=A\vec{x}.
$$

但单细胞快照数据只有 $\vec{x}$，没有真实 $\vec{x}'$。因此 scKINETICS 把速度当作 latent variable，用 EM 反复做两件事：

1. **E-step intuition**：在当前 $A_k$ 下，估计每个 cell/gene 的 latent velocity 应该落在什么范围内，并计算 truncated-normal correction。
2. **M-step intuition**：在这些 latent-velocity correction 和 coexpression prior 的约束下，更新 $A$ 的边权。

论文目标写作：

$$
Q(A|A_k)=E_{\vec{x}'|\vec{x},A_k}[\log L(A|\vec{x}',\vec{x})],
\quad
A_{k+1}=\arg\max_A Q(A|A_k).
$$

这句话可以翻译成更直白的版本：给定当前矩阵 $A_k$，先对未知速度 $\vec{x}'$ 的可能值做条件期望；然后找一个新的 $A_{k+1}$，让这个期望 log-likelihood 最大。

#### 4.7 从一个 target gene 看 EM 的实际计算

源码不是一次性更新整个矩阵 $A$。它把每个 cluster 的每个 target gene 拆开，只更新这个 target 的 regulator vector：

$$
\vec{a}_i = (A_{i,j_1}, A_{i,j_2}, \ldots, A_{i,j_{d_i}}).
$$

这里 $i$ 是 target gene，$j_1,\ldots,j_{d_i}$ 是 TF-target mask 允许调控它的 TF。对一个 target 来说，变量形状如下：

| 对象 | 代码变量 | 形状 | 含义 |
|---|---|---|---|
| regulator expression | `X_latent = X_[TForder].values.T` | regulators x cells | 每列是一个 cell 的候选 TF 表达向量 |
| target velocity bounds lower | `alpha = alpha_[:, target_ix]` | cells | target $i$ 在每个 cell 的 velocity 下界 |
| target velocity bounds upper | `beta = beta_[:, target_ix]` | cells | target $i$ 在每个 cell 的 velocity 上界 |
| prior vector | `ahat = A_[target_ix, TForder_ix]` | regulators | masked covariance 给 target $i$ 的先验边权 |
| current weights | `a_s` | regulators | 当前迭代中的 $\vec{a}_i$ |
| predicted target velocity | `mean_s = np.dot(a_s, X_latent)` | cells | 当前 $\vec{a}_i$ 预测的每个 cell 的 target velocity |

初始化很简单：

$$
\vec{a}_i^{(0)}=\hat{\vec{a}}_i.
$$

也就是代码里的：

```python
ahat = A_[target_ix, TForder_ix]
a_s = np.copy(ahat)
```

这说明 coexpression prior 不只是正则项，还是 EM 的起点。

#### 4.8 E-step 在代码里具体算什么

对 target $i$ 的某个 cell $n$，当前参数给出的 mean velocity 是：

$$
\mu_n = \vec{a}_i^T\vec{x}_n^{TF}.
$$

但 velocity 不是普通 Gaussian，而是被 manifold bounds 截断：

$$
x'_{n,i}\sim TruncN(\mu_n,\alpha_{n,i},\beta_{n,i},\sigma).
$$

代码先计算截断正态的归一化分母：

```python
den = norm.cdf(beta, loc=mean, scale=sigma) - norm.cdf(alpha, loc=mean, scale=sigma)
```

对应：

$$
Z_n = \Phi\left(\frac{\beta_{n,i}-\mu_n}{\sigma}\right)
- \Phi\left(\frac{\alpha_{n,i}-\mu_n}{\sigma}\right).
$$

如果 $Z_n$ 很小，说明当前 mean velocity $\mu_n$ 和 manifold bounds 很不协调；如果 $Z_n$ 较大，说明当前预测速度在 bounds 内更合理。

然后 `preq` 计算 PDF 差值带来的 correction：

```python
norm_beta = norm_pdf(beta, loc=mean_s, scale=sigma)
norm_alpha = norm_pdf(alpha, loc=mean_s, scale=sigma)
L1 = (norm_beta - norm_alpha) / den
```

直觉上，`L1` 告诉 M-step：当前预测速度 $\mu_n$ 相对于截断区间 $[\alpha,\beta]$ 应该往哪个方向修正。它不是一个新的观测速度，而是来自 truncated normal 条件分布的修正项。

代码中的 likelihood trace 是：

```python
marginal_l = np.sum(np.log(den)) + prior(a, ahat, sigma_prior)
```

它保留了截断分母和 Gaussian prior 这些会影响迭代比较的项；常数项不影响更新方向。源码用这个值记录 `curves[target]`，并在 15 次迭代后判断是否提前停止。

#### 4.9 M-step 如何闭式更新边权

M-step 的目标是更新当前 target 的 regulator weights。论文给出的形式是：

$$
\vec{a}_i^{(k+1)}=-(E_1^T+E_1)^{-1}E_2.
$$

源码中 $E_1$ 对应 `A_min`：

```python
A_min = -.5 / sigma_prior**2 * np.eye(X_latent.shape[0]) \
        - (.5 * outerprod_ / sigma**2)
```

数学上可以理解为：

$$
E_1
=-\frac{1}{2\hat{\sigma}^2}I
-\frac{1}{2\sigma^2}\sum_n \vec{x}_n^{TF}(\vec{x}_n^{TF})^T.
$$

它是二次项，形状是 regulators x regulators。第一项来自 prior precision，第二项来自 regulator expression 的二次结构。这个项只依赖 `X_latent`、$\sigma$、$\hat{\sigma}$，所以对一个 target 来说可以预先算好。

源码中 $E_2$ 对应 `B_min`：

```python
B_min = ahat / (sigma_prior**2) \
        + np.sum(mean_s * X_latent, axis=1) / sigma**2 \
        - np.sum(L1 * X_latent, axis=1) / sigma
```

它是一次项，形状是 regulators。三部分含义分别是：

| 项 | 直觉 |
|---|---|
| `ahat / sigma_prior**2` | 把边权拉回 coexpression prior |
| `sum(mean_s * X_latent) / sigma**2` | 当前 predicted velocity 对更新的贡献 |
| `- sum(L1 * X_latent) / sigma` | truncated-normal bounds 对 velocity 的修正 |

最后源码更新：

```python
a_s = -1.0 * np.linalg.pinv(A_min + A_min.T).dot(B_min)
```

论文写 matrix inverse，源码用 `np.linalg.pinv`，也就是 pseudoinverse。这样在 regulator 表达矩阵相关性强、矩阵接近奇异时更稳定。

#### 4.10 一轮 target-wise EM 可以这样读

对一个 cluster 里的一个 target gene，循环是：

```text
输入:
  X_latent: regulators x cells
  ahat: regulators
  alpha, beta: cells

初始化:
  a_s = ahat

重复:
  1. mean_s = a_s dot X_latent
  2. den = CDF(beta; mean_s, sigma) - CDF(alpha; mean_s, sigma)
  3. L1 = PDF(beta; mean_s, sigma) - PDF(alpha; mean_s, sigma) over den
  4. B_min = prior term + current-mean term - truncation-correction term
  5. a_s = - pinv(A_min + A_min.T) dot B_min
  6. 记录 marginal likelihood

输出:
  A[target_ix, TForder_ix] = a_s
```

这个流程解释了为什么 scKINETICS 的 EM 是 **masked、target-wise、cluster-specific** 的：

- **masked**：每个 target 只更新 motif/peak mask 允许的 TF columns。
- **target-wise**：每个 target 的 regulator vector 独立求解，可以并行。
- **cluster-specific**：每个 cluster 使用自己的 `X_`、$\hat{A}_c$、$\alpha,\beta$，最后得到自己的 $A_c$。

#### 4.11 学习 EM 时最该抓住的直觉

把 scKINETICS 的 EM 看成三股力量的平衡：

1. **表达数据**：TF 表达 `X_latent` 决定哪些 regulator weight 组合能产生某个 velocity。
2. **coexpression prior**：`ahat` 让边权不要脱离 cluster 内 TF-target covariance 太远。
3. **manifold bounds**：`alpha,beta` 要求 latent velocity 落在局部 future-like neighbor directions 附近。

如果只看表达数据，速度不可观测，问题欠定；如果只看 coexpression，得到的是静态相关网络；如果只看 manifold，得到的是平滑方向但没有调控解释。EM 的作用就是在这三者之间找一个局部最优的 $A_c$。

### 5. 逐步解释：每一步输入、计算、输出、失败模式

#### Step 1: 用 epigenetic evidence 决定哪些边可以非零

**输入**：ATAC peaks、genome annotation、motif database、表达矩阵中的 gene names。

**计算**：

1. `PeakAnnotation.call_motifs` 串起 peak annotation、sequence extraction、background estimation、motif scan 和 pair formatting。
2. `annotate_peaks` 使用 ChIPseeker 风格的 `annotatePeak`，按 TSS 距离过滤；默认 `max_upstream_distance=500`、`max_downstream_distance=3000`。
3. `scan_peaks` 用 MOODS 扫描 motif，并可把 TF 限制在表达矩阵中存在的 genes。
4. `prepare_target_annotations` 去重 TF-target pairs，生成 `TargetRecord` 字典 `G`，并把 target/TF 都映射到同一个 model gene index space。

**输出**：`G[celltype][target] -> TargetRecord`，其中每个 target 记录 `transcription_factors` 和 `transcription_factors_indices`。

**意义**：这一步决定 $A$ 的 zero pattern。它是可识别性的来源，也是风险来源：motif false positive、距离型 peak-to-gene 错误、distal enhancer missing，都会决定哪些调控边能被学到或永远学不到。

#### Step 2: 把表达矩阵变成 EM 使用的正值表达空间

**输入**：AnnData expression matrix。

**计算**：

1. `scanpy.pp.pca(self.adata, n_comps=50)`。
2. 如果没有 `adata.obsm['X_magic']`，调用 `run_MAGIC`。
3. `scaling='softplus'` 时用 `log(1+exp(x))`。
4. `scaling='linear'` 时把矩阵整体平移到正数。
5. 写入 `adata.obsm['X_transformed']`，并按 cluster 写入 `adata.uns['X_<cluster>']`。

**输出**：cluster-specific transformed expression `X_c`。

**意义**：论文强调 count matrix input，但代码显示 EM 实际使用的是 imputed/positive transformed expression。这是 reproducibility 中很重要的 hidden preprocessing detail。

#### Step 3: 计算 cluster-specific coexpression prior

**输入**：`X_c` 和 `G_c`。

**计算**：`get_prior` 对每个 cluster 计算 `np.cov(X_.T)`，再乘以 binary mask `g`：

$$
\hat{A}_c=\mathrm{Cov}(X_c)\odot G_c.
$$

**输出**：`celltype_priors[celltype]`。

**意义**：这个 prior 决定初始边权的符号和大小，也在 M-step 中作为 Gaussian prior 约束 $A_{ij}$。如果 cluster label 不准或 covariance 被 confounder 主导，先验会把 EM 拉向错误方向。

#### Step 4: 用 local manifold 构造 latent velocity bounds

**输入**：`adata.obsm['X_pca']`、`adata.obsm['X_transformed']`、`celltype_priors`。

**计算**：

1. 在 PCA 空间建 Euclidean kNN graph。
2. 对 kNN connectivity 再建 Jaccard-distance kNN graph。
3. 对每个 cell 计算 neighbor expression difference：`slopedist = X_neighbor - X_cell`。
4. 用 `np.std(slopedist, axis=0) / 10.0` 得到 per-gene offset，并 clip 到至少 `1e-10`。
5. 用 DBSCAN 对 neighbor slope vectors 聚类，metric 是 cosine。
6. 自适应调整 `eps`，让 component 数量保持在经验范围。
7. 用 prior-predicted direction `prior.dot(data.iloc[cellrand][list(prior)])` 选择 cosine agreement 最高的 component。
8. 用选中的 `med +/- offset` 生成 $\alpha_n,\beta_n$。

**输出**：`alpha_all`, `beta_all`, `kNN_graph`。

**意义**：manifold 约束不是后处理 smoothing，而是直接进入 EM likelihood 的 latent velocity constraint。它解释了 scKINETICS velocity 的局部一致性，也带来风险：如果 manifold 受 batch、branch ambiguity 或错误 cluster 影响，bounds 会把速度引向错误方向。

#### Step 5: 对每个 cluster、每个 target 做 EM

**输入**：`G_`、`X_`、`A_ = celltype_priors[celltype].values`、`alpha_`、`beta_`。

**计算**：

1. 外层按 cluster/celltype 循环，得到 cluster-specific $A_c$。
2. 内层按 target gene 循环，只取该 target 的 candidate TF columns。
3. `X_latent = X_[TForder].values.T`，形状是 regulators x cells。
4. `ahat = A_[target_ix, TForder_ix]`，作为 target-specific prior vector。
5. 用 `marginal_L_faster` 计算 truncated-normal denominator 和 prior likelihood。
6. 用 `preq` 计算 truncated-normal correction。
7. 用 `calculate_A_min` 和 `calculate_a_s` 得到新的 `a_s`。
8. 迭代到 `maxiter`，或 15 次后 relative likelihood improvement 小于 `tol`。
9. 写回 `A[target_ix, TForder_ix] = a_s.copy()`。

**输出**：每个 cluster 的 fitted matrix `A`。

**意义**：scKINETICS 并不是拟合一个全局统一网络；它在同一个 epigenetic mask 框架下学习 cluster-specific dynamics。这样能表达不同 cell state 的调控差异，但也让结果依赖 cluster definition。

#### Step 6: 计算 per-cell velocities，并过滤输出基因

**输入**：fitted $A_c$ 和 cluster expression `X_`。

**计算**：

```python
velocity = np.dot(A, X_.values.T).T
```

然后代码找出列非零 TFs 和行非零 targets，把“作为 regulator 但不是 dynamical target”的 TF 从 velocity columns 中去掉：

```python
TFs, targets = np.where(np.sum(A,0)!=0)[0], np.where(np.sum(A,1)!=0)[0]
invalid_TFs = list(set(TFs)-set(TFs[np.isin(TFs, targets)]))
this_velocity = this_velocity.drop(columns=X_.columns[invalid_TFs])
```

**输出**：`model.velocities_`。

**意义**：最终 velocity gene columns 不一定等于最初所有 TF/target union。读下游结果时要注意：有些 TF 是 regulator-only，在速度输出中会被移除。

#### Step 7: 把高维 velocity 投影成 embedding stream

**输入**：`model.velocities_`、`adata.obsm['X_pca']`、2D embedding。

**计算**：

1. `VelocityGraph.create_velocity_graph` 建 PCA kNN 和 Jaccard graph。
2. 对每个 cell，计算 neighbor displacement `dX = X_neighbor - X_cell`。
3. 计算 `dX` 和模型 velocity 的 cosine correlation。
4. `compute_transitions` 把 velocity graph 变成 transition matrix。
5. `embed_graph` 把 transition directions 投影到 2D embedding。
6. `plot_velocities_stream` / `plot_velocities_scatter` 画 stream 或 arrows。

**输出**：2D velocity arrows/streamplot。

**意义**：Fig. 2 里的 stream 是高维 $A_cx$ velocity 的可视化投影；不是在 2D 图上重新学习出来的速度。

#### Step 8: TF-wide in silico perturbation

**输入**：fitted `A`、cluster expression `X_`。

**计算**：

1. 计算原始速度：

$$
v = Ax.
$$

2. 对每个 TF，把对应 column 置零：

$$
A^*_{:,j}=0.
$$

3. 重新计算：

$$
v^* = A^*x.
$$

4. 对每个 cell 计算 `original_velocity` 和 `velocities_mut` 的 cosine distance。

**输出**：cells x TFs 的 TF activity score。

**意义**：如果置零某个 TF column 后 velocity 改变很大，该 TF 在当前 fitted linear velocity operator 中影响大。它是 model-based sensitivity，不是实验 knockout，也不模拟 TF expression change、cofactor、chromatin 或 network rewiring。

### 6. 图和结果应该怎么读

| 图/结果 | 支持什么 | 不支持什么 |
|---|---|---|
| Fig. 1 | 方法结构：TF-target ODE、signed $A$、epigenetic/coexpression constraints、manifold truncated-normal bounds | 不是 performance validation |
| Fig. 2 | pancreas ADM embedding 上，scKINETICS velocity stream 和 pseudotime reference direction 更一致 | 当前源码中 `Not found` Palantir benchmark / baseline scripts，所以不能写成已源码复现 |
| Fig. 3 | local velocity consistency 和 count downsampling / $\sigma$ / prior noise robustness 的论文结果 | robustness scripts `Not found`; 代码只直接支持 `sigma` 参数存在 |
| simulation | 用 $e^{At}x(0)$ 生成数据并报告 nonzero $A$ correlation `r=.665` | matrix-exponential simulation source `Not found` |
| Fig. 4 | TF column zeroing + cosine distance 的 activity score，代码强支持 | activity score 不是实验 perturbation validation |

论文中的 Ptf1a、Sox9、Fosl2/AP1、Xbp1、Dnajc21 结果应读作 biological interpretation / hypothesis generation。尤其 Ptf1a 的例子说明：TF expression 低并不一定意味着 model activity 低，因为 score 同时利用 TF-target prior、target expression 和 fitted velocity operator。

### 7. 代码-论文忠实度

| 组件 | 忠实度 | 说明 |
|---|---|---|
| $x_i'(t)=\sum_j x_j(t)A_{ij}$ | Exact | target-wise sparse regulator update 有源码证据。 |
| $\vec{x}'(t)=A\vec{x}(t)$ | Exact | `np.dot(A, X_.values.T).T` 直接实现。 |
| TF-target mask | Exact | peak annotation、motif scan、target merge 在 `tf_targets.py` 中实现。 |
| covariance prior $\hat{A}_c$ | Exact | `np.cov(X_.T)` 乘以 binary GRN mask。 |
| manifold truncated-normal bounds | Exact | kNN/Jaccard/DBSCAN、$\alpha,\beta$ bounds 和 CDF/PDF likelihood terms 有源码证据。 |
| target-wise EM update | Exact | `A_min`, `B_min`, `preq`, `pinv` 对应论文更新式。 |
| cluster-specific fitting | Exact | 每个 `celltype` 单独拟合 `A_c`。 |
| velocity graph / visualization | Exact | `graph_embedding.py` 实现 velocity graph、transition 和 stream/quiver plot。 |
| TF activity score | Exact | `tf_perturbation.py` 实现 TF column zeroing + cosine distance。 |
| MAGIC/positive transform | Partial hidden detail | 代码明确实现，论文没有重点展开。 |
| scATAC differential peak utility | Partial | 有工具函数，但 pancreas 应用主要使用 bulk ATAC peaks。 |
| pancreas demo notebook | Notebook | notebook 有 end-to-end flow anchors，但不是完整 benchmark/reproduction scripts。 |
| Palantir / baseline benchmark | Not found | 当前 package/demo snapshot 没有找到对应脚本。 |
| robustness/downsampling/prior-noise experiments | Not found / Partial | `sigma` 参数存在；实验脚本未找到。 |
| matrix-exponential simulation | Not found | 论文 simulation source 未找到。 |
| exact pancreas constants | MISSING in source | 论文报告常数未从源码或已打开 sidecars 验证。 |

### 8. 实现中最容易忽略的细节

1. **输入不是直接裸 count 进入 EM**：代码会 PCA、可选 MAGIC，并做 softplus/linear positive transform。
2. **`A` 的 orientation 很重要**：行是 target，列是 regulator；速度计算写作 `A.dot(X.T).T`。
3. **mask 决定可学边**：unsupported edges 固定为 0，不会被 EM 救回来。
4. **coexpression 是 prior，不是 causal proof**：它提供 sign/magnitude bias，但也可能被 confounder 误导。
5. **manifold 是推断约束，不是后处理**：$\alpha,\beta$ 进入 truncated-normal likelihood。
6. **DBSCAN component selection 有 prior bias**：代码用 prior-predicted direction 选最一致的 neighbor component。
7. **输出 gene space 会被过滤**：regulator-only TFs 不一定出现在 final `velocities_` columns。
8. **TF activity 是 sensitivity score**：zero column 只测试 fitted operator 里的 TF downstream contribution。

### 9. 适合怎么用，不适合怎么用

适合的使用场景：

- 有 scRNA-seq，并且有 bulk ATAC、scATAC 或 multiome peaks 可作为 regulatory prior。
- 问题关心 trajectory direction，也关心候选 TF regulators。
- 可以接受结果是 model-based hypotheses，需要后续实验或独立证据验证。
- cluster labels、motif database、peak-to-gene mapping 的质量相对可靠。

需要谨慎的场景：

- epigenetic prior 质量差，导致 TF-target mask 大量 false positive 或 false negative。
- manifold 主要由 batch effect、sample composition 或错误 branch 混合驱动。
- 需要严格复现论文所有 benchmark、robustness、simulation 数值；当前源码快照缺少对应脚本。
- 需要真实 causal perturbation 结论；scKINETICS 只能给优先级排序和假设生成。

### 10. 推荐阅读路线

1. 先读 `summary.md`，抓住论文问题、核心创新和 reproducibility rating。
2. 再读 `doc_method.md`，看完整数学推导和 pipeline。
3. 查 `doc_code.md` 的 `Match Assessment`，区分 `Exact`、`Partial`、`Notebook`、`Not found`、`MISSING in source`。
4. 读本文件，按输入、变量、每一步计算和输出理解方法。
5. 最后查 `claude_notes.md`，需要精确 paper line、code line 或 missing evidence 时再回到 ledger。

### 11. 一句话总结

scKINETICS 把细胞速度写成 $x'=Ax$，用 ATAC/motif 证据限制 $A$ 的可学边，用 cluster-specific covariance 给 $A$ 一个协表达先验，用 local manifold 给不可观测 velocity 加 truncated-normal bounds，再用 target-wise EM 学出 cluster-specific $A_c$。学到的 $A_c$ 既能计算 per-cell velocity，也能通过 TF-column knockout 生成 TF activity score。当前源码强支持这条核心链路；论文中的 benchmark、robustness、simulation 和精确数据常数必须保留 paper-only / `Not found` / `MISSING in source` 边界。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scKINETICS Summary

### Paper Identity

- **Method:** scKINETICS
- **Title:** *scKINETICS: inference of regulatory velocity with single-cell transcriptomics data*
- **Venue:** *Bioinformatics* 39(Suppl 1), 2023
- **DOI:** `10.1093/bioinformatics/btad267`
- **Code snapshot:** `https://github.com/dpeerlab/scKINETICS`, branch `main`, commit `40588aca0fea25a1c4c397e3579f355556dc7fd6`

### Motivation

scKINETICS targets a gap between RNA velocity and gene-regulatory-network inference. Standard velocity methods can estimate where cells move in expression space, but they usually do not identify the transcription factors driving those movements. Many GRN methods infer static regulatory structure, but they do not directly estimate de novo per-cell velocity.

The paper asks whether a single model can infer both:

1. per-cell transcriptional velocities, and
2. a signed sparse regulatory matrix whose entries describe TF effects on target-gene expression-rate dynamics.

The main biological demonstration is pancreatic regeneration and acinar-to-ductal metaplasia (ADM), where the desired output is not only a trajectory from acinar-like toward duct-like states, but also regulator hypotheses for branches of that trajectory.

### Core Method

The method models expression velocity as a sparse linear regulatory system:

$$
\vec{x}'(t)=A\vec{x}(t).
$$

For each target gene $i$,

$$
x_i'(t)=\sum_{j=1}^{d_i}x_j(t)A_{ij},
$$

where only TFs allowed by the regulatory mask can contribute. Candidate nonzero entries in `A` are constrained by ATAC peaks, TF motif calls, and peak-to-gene association. Edge signs and magnitudes are initialized and regularized by cluster-specific coexpression covariance. Because true velocities are unobserved, scKINETICS uses EM with a truncated-normal latent-velocity constraint derived from local manifold neighborhoods.

The computational framework is:

```text
scRNA-seq AnnData + epigenetic peaks
  -> motif/peak-to-gene TF-target mask
  -> transformed expression and cluster-specific covariance prior
  -> kNN/Jaccard/DBSCAN manifold bounds alpha,beta
  -> target-wise EM updates for cluster-specific A_c
  -> per-cell velocity A_c x
  -> velocity graph / embedding visualization
  -> TF-column knockout activity score
```

### Verified Implementation

The acquired source strongly supports the core algorithm:

- `sckinetics/tf_targets.py` builds TF-target records from peak annotation, sequence extraction, motif scanning, and target merging.
- `sckinetics/EM.py` implements the EM class with defaults `maxiter=20`, `sigma=5.0`, and `sigma_prior=1.0`.
- `get_prior` computes cluster-specific covariance priors and masks them by GRN support.
- `get_constraints` constructs manifold-derived bounds using PCA kNN, Jaccard-distance neighbor graph, neighbor slopes, DBSCAN components, prior-direction agreement, and clipped offsets.
- The target-wise M-step updates regulator vectors and stores fitted matrices `A_c`.
- Velocities are computed as `np.dot(A, X_.values.T).T`, matching $x'=Ax$.
- `graph_embedding.py` creates velocity graphs and 2D scatter/stream visualizations.
- `tf_perturbation.py` zeroes TF columns, recomputes velocities, and reports cosine-distance activity scores.

The code also exposes details that are less prominent in the paper: optional MAGIC imputation, softplus/linear positive expression transformation, adaptive DBSCAN `eps`, numerical clipping of manifold windows, and filtering of regulator-only TFs from final velocity outputs.

### Evaluation Claims

The paper reports that scKINETICS captures ADM progression in a pancreas regeneration dataset. It shows velocity streams pointing from acinar-like toward duct-like states, better high-dimensional alignment to pseudotime reference directions than scVelo, VeloVAE, and UniTVelo, and lower local velocity inconsistency. It also reports robustness to count downsampling, varying $\sigma$, and prior noise. A simulation study generated expression from $e^{At}x(0)$ plus Gaussian noise and reported average correlation `r=.665` on nonzero `A` entries.

TF perturbation analysis uses the fitted regulatory matrix for TF-wide in silico knockout. The paper highlights Ptf1a, Sox9, Fosl2/AP1, Xbp1, and Dnajc21-related regulatory programs as plausible drivers of ADM state or branch differences.

### Evidence Boundaries

Important paper-vs-code boundaries:

- The high-dimensional Palantir/pseudotime benchmark and baseline comparison scripts were **Not found** in the acquired package source or demo notebook.
- Robustness experiment scripts for downsampling, prior noise, and parameter sweeps were **Not found**; only the configurable `sigma` parameter is directly present.
- The matrix-exponential simulation source using $e^{At}x(0)$ was **Not found**.
- Exact pancreas constants reported in the paper, including 5501 cells, 15497 genes, 6575 peaks, and 585 TFs, are **MISSING in source** because they were not verified from source code or opened sidecar data.

These gaps do not invalidate the core implementation, but they mean the manuscript's quantitative benchmark, robustness, and simulation results should be treated as paper evidence rather than verified reproducible code behavior in this snapshot.

### Reproducibility Rating

**Rating: 3 / 5.**

Strengths:

- Public source code and an end-to-end pancreas demo notebook are present.
- The core ODE, GRN mask, covariance prior, manifold constraint, EM update, velocity computation, visualization, and TF perturbation have direct source support.
- The code-paper match is high for the central inference engine.

Limitations:

- Full reproduction of the paper's benchmark, robustness, and simulation figures would require scripts not found in the acquired snapshot.
- Some important preprocessing and numerical heuristics are clearer in code than in the paper.
- Exact data constants were not verified from source or sidecar data.
- TF activity is model-based perturbation scoring, not experimental causal validation.

Overall, scKINETICS is reproducible at the package/core-method level, but not fully reproducible for all manuscript-level quantitative claims from the current repository snapshot alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
