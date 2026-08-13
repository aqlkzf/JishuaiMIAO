---
layout: default
permalink: /paper-atlas/contextflow-72f8fd11/
title: "ContextFlow"
nav: false
description: "ContextFlow 从多个时间点的空间转录组快照学习连续速度场。它的关键不是把空间坐标直接作为速度网络输入，而是在相邻时间点的 minibatch optimal transport（OT）配对中加入两类上下文：局部组织表达环境和 ligand–receptor（LR）通讯模式。由这些先验偏置出的跨时点细胞对，再监督 conditional flow matching。"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>ContextFlow</h1>
    <p>ContextFlow: Context-Aware Flow Matching for Trajectory Inference from Spatial Omics Data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2510.02952" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ContextFlow">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/santanurathod/ContextFlow" target="_blank" rel="noopener noreferrer" aria-label="Open code for ContextFlow">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ContextFlow：用空间微环境和细胞通讯约束流匹配

### 一句话理解

ContextFlow 从多个时间点的空间转录组快照学习连续速度场。它的关键不是把空间坐标直接作为速度网络输入，而是在相邻时间点的 minibatch optimal transport（OT）配对中加入两类上下文：局部组织表达环境和 ligand–receptor（LR）通讯模式。由这些先验偏置出的跨时点细胞对，再监督 conditional flow matching。

因此，ContextFlow 学到的是“在这些空间先验下更可信”的群体流。它不能直接追踪同一个真实细胞，也不能把某条推断轨迹当作已实验验证的谱系关系或配体受体因果作用。

### 1. 输入和输出

输入是按时间分组的空间转录组数据。公开训练路径实际需要预处理 `.h5ad` 中至少包含：

- `X_pca`：主要动力学状态，通常 50 个主成分；
- `spatial`：空间坐标；
- `local_mean_X_pca`：空间邻域的平均表达表示；
- `LR_pattern`：由 LIANA+ 等资源导出的通讯特征；
- `day` 和 `celltype`：时间与评价标签。

输出是定义在 PCA 表达空间上的统一时间依赖速度场 $u_\theta(t,x)$。通过 ODE 积分，可从初始时间点生成后续分布（IVP），或从每个观测时点预测下一步（next-step）。OT coupling 是训练监督的一部分，并不是最终唯一的细胞配对真值。

### 2. 基础：minibatch OT flow matching

对相邻快照 $X_i$ 和 $X_{i+1}$，普通 MOTFM 先用表达距离构造 minibatch OT coupling $\pi$。按 $\pi$ 抽取源—目标对 $(x_0,x_1)$ 后，在随机时间 $t\sim U[0,1]$ 上构造高斯条件路径：

$$
x_t=(1-t)x_0+t x_1+\sigma\epsilon,
$$

其目标速度在代码采用的线性路径下为

$$
u_t=x_1-x_0.
$$

神经网络最小化

$$
\mathcal L_{CFM}=\mathbb E\|u_\theta(t,x_t)-u_t\|^2.
$$

本地实现分别位于 `torchcfm/conditional_flow_matching.py:41-235` 和 `main.py:36-83`。对于不等时间间隔，代码把目标速度除以 $\Delta t$（`conditional_flow_matching.py:130-169`）。训练 MLP 将时间与 PCA state 拼接，使用三层 SELU hidden transformation 和输出层（`torchcfm/models/models.py:4-21`）。

### 3. 两种空间上下文

#### 3.1 Spatial smoothness（SS）

对每个细胞，在组织切片的半径邻域内平均邻居表达，得到局部微环境向量。若两个不同时点的细胞局部环境相似，它们的跨时点连接更可信。

训练代码不现场搜索邻居，而从 `.h5ad` 读取 `local_mean_X_pca`（`src/data_loading.py:102-140`）。半径 $r$、邻域构造和表达预处理位于数据脚本中。因此“主模型使用 SS 特征”是 Exact，“从任意原始数据自动算好 SS”则是 Partial。

#### 3.2 Ligand–receptor（LR）通讯

每个位置的 LR pattern 表示其局部通讯活动。跨时点 LR 特征相似，被解释为功能上下文更连续。代码读取 `LR_pattern`，计算跨时点平方欧氏距离（`torchcfm/optimal_transport.py:129-142`）。

LR 特征的生成依赖 LIANA+、配体受体资源和空间聚合流程；仓库有相关脚本，但主训练入口假设特征已经写入 `.h5ad`。因此 LR 对训练 coupling 的使用是 Exact，端到端预处理是 Partial。

### 4. Transitional Plausibility Matrix

对相邻时间点的两个 minibatch，先得到

$$
D_{SS}(k,l)=\|m_k-m_l\|^2,
\qquad
D_{LR}(k,l)=\|r_k-r_l\|^2.
$$

组合距离为

$$
B_{kl}=\lambda D_{SS}(k,l)+(1-\lambda)D_{LR}(k,l).
$$

$\lambda=1$ 只用 SS，$\lambda=0$ 只用 LR。论文把由此形成的 prior 称为 transitional plausibility matrix。注意它表达的是启发式可行性偏好：SS 或 LR 相似并不证明两细胞具有真实祖先—后代关系。

### 5. 两种 prior integration

#### 5.1 CTF-C / PACM：修改运输 cost

cost-aware 方案直接混合表达距离和 context distance。例如：

$$
C'_{kl}=\alpha C^{gene}_{kl}+(1-\alpha)B_{kl}.
$$

随后对 $C'$ 做标准 entropic Sinkhorn。代码中 `OT_cost_variation` 的 `g+mc`、`g+lr`、`g+mc+lr` 分支实现这些组合（`torchcfm/optimal_transport.py:218-255`）。

这里不同 cost 的量纲和归一化很重要；配置提供 `g_normalize`、`mc_normalize`、`lr_normalize`。不固定这些开关，$\alpha$ 的数值不能跨数据集直接解释。

#### 5.2 CTF-H / PAER：修改熵参考

entropy-aware 方案先对 $-B$ 逐行 softmax：

$$
\widehat M_{kl}=\frac{e^{-B_{kl}}}{\sum_l e^{-B_{kl}}},
$$

再求

$$
\min_{\pi\in\Pi(a,b)}
\langle C,\pi\rangle+
\epsilon\,KL(\pi\|\widehat M).
$$

它把 prior 当作相对熵参考，而不是与表达 cost 手工相加。Theorem 3.1 给出 Sinkhorn kernel

$$
K=\widehat M\odot\exp(-C/\epsilon).
$$

代码在 `optimal_transport.py:100-161` 生成 prior，在修改版 POT 的 `ot_modified/bregman/_sinkhorn.py` 中构造该 kernel。这是核心 **Exact** 匹配。

“软过滤”不等于硬禁止：只要 prior 元素非零，表达 cost 与边缘约束仍可能分配质量。较大的 $\epsilon$ 强化 prior 参考，较小的 $\epsilon$ 更接近只看运输 cost。

### 6. 从 coupling 到速度场

`get_batch()` 对每个相邻时间点：

1. 抽取源、目标 minibatch；
2. 同步取出 PCA、空间、microenvironment 和 LR 特征；
3. 用 CTF-C 或 CTF-H 求 OT plan；
4. 按 plan 重采样 $(x_0,x_1)$；
5. 生成 $x_t$ 和 $u_t$；
6. 拼接所有时间区间，以 MSE 更新统一 MLP。

核心路径是 `src/data_loading.py:142-224` → `conditional_flow_matching.py:256-334` → `optimal_transport.py:165-278` → `main.py:36-83`。

一个重要实现问题是 `get_batch()` 每次调用都执行 `np.random.seed(42)`（`data_loading.py:149`）；因此各 epoch 的原始 minibatch indices 会重复。随机 $t$、高斯噪声及按 OT plan 采样仍可能变化，但模型没有获得预期的 numpy minibatch 覆盖。这应视为复现和泛化边界，而不是论文算法特性。

### 7. 推断和评价

训练完成后用 `torchdyn.NeuralODE` 的 `dopri5` 积分速度场。两种协议是：

- **IVP**：只从最早快照出发，连续积分到全部后续时间；误差会累积。
- **Next-step**：每次从真实观测快照重新出发，只预测下一个时点；更容易但诊断局部转移更直接。

评价包括 multi-kernel MMD、energy distance、sliced Wasserstein（200 projections）和按细胞类型加权的 sliced Wasserstein。论文表中写 $W_2$，公开评价实际是 sliced approximation，故 `doc_code.md` 标为 Partial。

weighted metric 还需要 XGBoost cell-type classifier；`main.py` 中加载路径指向作者本机 `/Users/...`，仓库没有可直接复用的对应 classifier。主评价块部分使用宽泛 `try/except`，失败时可能静默跳过 next-step 输出。这使完整数表不能由原始 checkout 无修改重现。

### 8. 论文图和结果应怎样读

Figure 1 是概念图：SS/LR 先验抑制不合理的跨切片连接。Figure 2 比较预测和真实 cell-type proportion 的 KL divergence；Figure 3 表明 context-aware minibatch OT 仍保持近似线性 epoch runtime，但 CTF 明显比 random CFM 慢。Figure 4 以 excitatory↔inhibitory switches 定义不合理 coupling，CTF-H 从 MOTFM 的 54 条降到 24 条。Figure 5 及附录展示预测细胞类型的空间进程。

这些结果说明先验减少了**按作者规则定义**的不合理配对，并改善 held-out distribution metrics。它们不证明每条 coupling 是真实细胞轨迹；“excitatory-inhibitory switch 不合理”本身是特定生物学评判规则。LR 图的稳定空间模式支持先验的可解释性，但不是 LR 对转变的因果验证。

### 9. 论文—代码匹配结论

| 环节 | 匹配 | 边界 |
|---|---|---|
| 多时间点 conditional flow matching | Exact | 线性高斯条件路径与 MSE 目标存在 |
| SS/LR 距离进入 OT | Exact | 训练读取预计算特征 |
| 原始数据到 SS/LR 特征 | Partial | 依赖多步外部预处理与 LIANA+ |
| CTF-C / PACM | Exact | cost 混合与标准 Sinkhorn |
| CTF-H / PAER | Exact | row-softmax prior 与相对熵 Sinkhorn kernel |
| $O(N^2)$ | Qualified | 指 minibatch OT；整体靠 minibatching 扩展，不构造全数据 coupling |
| 统一 ODE velocity field | Exact | PCA 表达空间，非空间坐标空间 |
| 论文 $W_2$ metric | Partial | 代码用 200 projection sliced Wasserstein |
| Weighted $W_2$ | Partial / Not portable | classifier 路径硬编码且模型未提供 |
| 完整端到端复现 | Not found | 无 checkpoints，processed h5ad 和 classifier 路径不完整 |

### 10. 最重要的解释边界

ContextFlow 的 context 是**配对先验**，并非直接写进速度网络的额外状态变量。训练后同一个 $u_\theta(t,x)$ 只看到时间和表达表示；空间信息通过“哪些源目标对被选中”间接塑造速度场。这种设计使推断可生成、可积分，却也意味着 prior 的偏差会被学习并传播。

实际使用时必须记录：PCA 与归一化、空间邻域半径、LR 资源和聚合方法、$\lambda$、CTF-C 的 $\alpha$、CTF-H 的 $\epsilon$、batch seed、训练/holdout 时间点和评价 classifier。缺少这些信息时，不能把相似的 loss 或图形称为论文级复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ContextFlow — Paper Summary

### Motivation & Novelty

#### Problem

Inferring cellular trajectories from longitudinal spatial transcriptomics data is essential for understanding tissue dynamics in development, regeneration, and disease. Because spatial profiling is destructive, only unpaired population snapshots at discrete time points are available. The challenge is to reconstruct continuous trajectories — how individual cells' transcriptional states evolve over time — from these snapshots.

#### Limitations of Existing Approaches

Flow matching methods like MOTFM (Tong et al., TMLR 2024) learn velocity fields using optimal transport couplings, but compute these couplings based solely on transcriptomic distance. They ignore the spatial context unique to spatial transcriptomics data:

- **DeST-OT** (Halmos et al., Cell Systems 2025): Spatiotemporal alignment with growth modeling, but $O(N^3)$ complexity and no generative capability.
- **TOAST** (Ceccarelli et al., bioRxiv 2025): Topography-aware OT for spatial alignment, but pairwise-only without trajectory learning.
- **PASTE** (Zeira et al., Nature Methods 2022): Spatial alignment of adjacent slices, no temporal dynamics.
- **CFM** (Lipman et al., ICLR 2023): Flow matching with random or independent couplings — no spatial or biological priors.

None of these methods incorporate cell-cell communication patterns or local tissue organization into the trajectory inference process.

#### Unique Contributions

1. **Transitional Plausibility Matrix (TPM)**: Encodes two spatial priors — neighborhood expression smoothness (SS) and ligand-receptor communication patterns (LR) — into a biologically informed matrix that quantifies how plausibly each pair of cells across time points are related.

2. **Two prior integration schemes**:
   - **PACM (CTF-C)**: Directly modifies the OT cost matrix with biological priors
   - **PAER (CTF-H)**: Replaces the uniform entropy reference with the prior distribution — eliminates the need for the $\alpha$ hyperparameter and normalization

3. **Theoretical guarantee**: Theorem 3.1 proves that PAER can be solved by the Sinkhorn algorithm with a modified Gibbs kernel $\mathbf{K} = \widehat{\mathbf{M}} \odot \exp(-\mathbf{C}/\epsilon)$, maintaining $O(N^2)$ computational complexity.

---

### Method Overview

ContextFlow is a flow matching framework that incorporates spatial priors into minibatch OT couplings for learning biologically meaningful velocity fields from longitudinal spatial transcriptomics data.

**Pipeline**:
1. **Preprocessing**: Log-normalize gene expression → PCA (50 components); compute local neighborhood means (spatial smoothness) and ligand-receptor interaction features (via LIANA+)
2. **Prior construction**: Build transitional plausibility matrix $\mathbf{M} = \lambda \cdot \text{SS} + (1-\lambda) \cdot \text{LR}$ for each consecutive time pair
3. **Context-aware OT**: Solve modified entropic OT using Sinkhorn with prior-aware kernel to obtain couplings
4. **Flow matching**: Train a neural velocity field (4-layer MLP) using conditional flow matching with OT-derived sample pairs
5. **Trajectory generation**: Integrate the learned velocity field using a neural ODE solver (dopri5)

**Key assumption**: Cells in similar microenvironments with similar communication patterns are more likely to undergo similar state transitions across short time intervals. This is encoded as a soft constraint — the prior biases OT couplings toward biologically plausible pairings without forcing them.

See `doc_method.md` for detailed mathematical formulations and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Datasets

| Dataset | Technology | Time Points | Cells | Resolution |
|---|---|---|---|---|
| Axolotl Brain Regeneration (Wei et al., Science 2022) | Stereo-seq | 5 stages | ~28,780 | Single-cell |
| Mouse Embryo Organogenesis (Chen et al., Cell 2022) | Stereo-seq | 8 stages | ~399,248 | Single-cell |
| Liver Regeneration (Ben-Moshe et al., bioRxiv 2021) | Visium | 3 stages | N/A | Spot-level (55μm) |

#### Metrics

- **2-Wasserstein distance** ($\mathcal{W}_2$): OT-based distributional distance (implemented as sliced Wasserstein with 200 projections)
- **Weighted $\mathcal{W}_2$**: Per-cell-type Wasserstein weighted by cell type frequency, using XGBoost classifier for predicted cell type assignment
- **MMD**: Multi-kernel maximum mean discrepancy with RBF kernels ($\gamma \in \{2, 1, 0.5, 0.1, 0.01, 0.005\}$)
- **Energy Distance**: Multivariate energy distance via `dcor` library

#### Sampling Protocols

- **IVP (Initial Value Problem)**: Integrate from first time point through all subsequent — most challenging, accumulates errors
- **Next-Step**: Integrate from each observed time point to the next — less stringent, limits error propagation

#### Key Results

**Brain Regeneration (Interpolation, Table 2)**:
- CTF-H ($\lambda=1$) achieves best performance across all metrics under both IVP and Next-Step sampling
- IVP: Weighted $\mathcal{W}_2$ = 3.905 ± 0.395 (CTF-H) vs 4.198 ± 0.319 (MOTFM) — 7% improvement
- MMD: 0.074 ± 0.014 (CTF-H) vs 0.173 ± 0.017 (MOTFM) — 57% improvement

**Brain Regeneration (Extrapolation, Table 3)**:
- CTF-H ($\lambda=1$, IVP): Weighted $\mathcal{W}_2$ = 5.277 ± 0.936 vs 6.503 ± 0.720 (MOTFM) — 19% improvement
- Energy: 27.777 ± 8.621 vs 56.452 ± 15.932 — 51% improvement

**Mouse Organogenesis (Interpolation, Table 4)**:
- CTF-H ($\lambda=0.5$, IVP): Weighted $\mathcal{W}_2$ = 2.814 ± 0.414 vs 3.251 ± 0.676 (MOTFM)
- CTF-H ($\lambda=0$, Next-Step Extrapolation): Weighted $\mathcal{W}_2$ = 1.505 ± 0.057 vs 1.626 ± 0.066 (MOTFM)

**Liver Regeneration (Table 5)**:
- CTF-H ($\lambda=0$): $\mathcal{W}_2$ = 32.682 ± 1.472 vs 34.303 ± 1.448 (MOTFM)

#### Biological Validation

- **Implausible coupling reduction**: CTF-H produces 24 excitatory-inhibitory lineage switches vs 54 for MOTFM (Figure 4) — 56% reduction
- **Cell type preservation**: Lower KL divergence between predicted and true cell type distributions (Figure 2)
- **Temporal coherence**: Smooth cell type progression over developmental stages matching known biology (Figure 10)

---

### Reproducibility

**Rating: 2.5/5**

#### Strengths
- Code is publicly available at https://github.com/santanurathod/ContextFlow
- Core algorithm (PACM/PAER OT, Sinkhorn with prior kernel) is cleanly implemented
- 85 JSON config files document hyperparameter settings for all experiments
- Preprocessing pipeline and dataset download scripts are included

#### Weaknesses
- **Hardcoded local paths**: XGBoost classifier loaded from `/Users/rssantanu/Desktop/...` (author's local machine); biological prior matrices similarly hardcoded
- **External preprocessing dependency**: LR features require LIANA+ and specific preprocessing pipeline; not fully end-to-end reproducible from the repository alone
- **Missing trained models/checkpoints**: No pre-trained models provided
- **Missing processed h5ad files**: Raw data download scripts exist, but the exact preprocessing pipeline to generate the final h5ad files (with `local_mean_X_pca`, `LR_pattern`, etc.) requires running multiple scripts in sequence
- **Fixed random seed issue**: `np.random.seed(42)` called in `get_batch()` causes identical batches across epochs (likely unintentional)
- **Small model specification not in paper**: The MLP hidden width of 10 is a critical hyperparameter not mentioned in the paper

#### Practical Notes
- Requires: PyTorch, torchdyn, anndata, scanpy, squidpy, LIANA+, POT, XGBoost, dcor
- The `ot_modified/` directory bundles a modified POT library (~15K LOC) — not a pip-installable dependency
- Training time is comparable to MOTFM (~minutes on GPU for Brain Regeneration dataset, see Figure 3)
- Preprocessing (LIANA+ LR computation) takes 23s for Brain Regeneration, 200s for Organogenesis (Table 6)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
