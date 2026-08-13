---
layout: default
permalink: /paper-atlas/veloae-b14e1527/
title: "VeloAE"
nav: false
description: "VeloAE 的本质是：把 RNA velocity 从嘈杂的高维基因空间，搬到一个由图平滑编码器和注意力解码器学习出的低维空间中，再在该空间估计速度和转移方向。论文和代码都支持核心 autoencoder、AttComb、latent regression 和 velocity projection；但复现论文时必须处理好 GCN/GAT 版本差异、scVelo 委托的 transition graph，以及缺失的本地补充材料。"
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
      <span>PNAS · 2021</span>
    </div>
    <h1>VeloAE</h1>
    <p>Representation learning of RNA velocity reveals robust cell transitions</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/qiaochen/VeloAE" target="_blank" rel="noopener noreferrer" aria-label="Open code for VeloAE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## VeloAE 方法中文解读

### 1. 这篇论文要解决什么问题？

RNA velocity 通过单细胞数据中的 spliced RNA 和 unspliced RNA 推断细胞短期未来状态，是判断发育轨迹方向的重要工具。但论文指出，传统 RNA velocity 在高维基因空间里直接估计细胞转移时容易不稳定：unspliced RNA 含量少、技术噪声高，不同基因给出的方向还可能互相矛盾（`paper.md:15-33`）。

VeloAE 的核心想法是：不要只在原始基因空间里计算 velocity，而是先学习一个低维、去噪、同时保留 spliced/unspliced 动态信息的表示空间，再在这个低维空间里计算速度和细胞转移（`paper.md:31-41`）。

### 2. 为什么已有方法不够？

论文讨论了几类背景方法：传统轨迹推断方法只能看到当前表达状态，缺少过去/未来方向信息；RNA velocity 引入 nascent/unspliced RNA 后能提供方向，但高维速度向量受噪声和投影方式影响很大（`paper.md:23-33`）。一种可能方案是手工挑选动态相关基因，但这依赖人工知识。VeloAE 选择另一条路线：通过表示学习自动把 spliced、unspliced 和邻域结构压缩到低维空间。

### 3. VeloAE 的新颖点

VeloAE 是一个为 RNA velocity 定制的 autoencoder。相比普通 AE，它有两个关键模块：

1. **CohAgg（cohort aggregation）**：编码器侧的图聚合模块。论文版本使用 GCN，把一个细胞的预编码表示和邻居细胞表示加权聚合，使相近细胞在低维空间中更平滑（`paper.md:162-180`）。
2. **AttComb（attentive combination）**：解码器侧的注意力模块。它把基因表示作为 query，把低维 latent dimensions 作为 key，用 Gumbel-Softmax 得到基因到 latent dimension 的注意力权重，再重构原始基因表达（`paper.md:183-204`）。这让模型不仅能重构输入，还能解释哪些 latent dimension 与哪些 marker genes 有关。

### 4. 输入、输出和整体流程

**输入：** 细胞 × 基因矩阵，包括 spliced reads `S`、unspliced reads `U`，以及可选的 transcriptome/aggregated expression `X`。论文把一般输入记为 $X\in\mathbb{R}^{N\times d_x}$（`paper.md:147-160`）。

**输出：** 低维 spliced 表示 $S_z$、低维 unspliced 表示 $U_z$、低维 velocity $V_z$，以及在低维空间上计算的细胞转移图（`paper.md:227-244`）。代码中 `do_projection` 会生成新的低维 `AnnData` 并调用 scVelo 的 `velocity_graph`（`VeloAE_code/veloproj/util.py:337-394`）。

```text
AnnData: S, U, X
  ↓ scVelo 预处理：filter/normalize/moments/velocity
邻接图 + gene PCA 表示
  ↓
共享 VeloAE
  S → Encoder → S_z → Decoder → S_hat
  U → Encoder → U_z → Decoder → U_hat
  ↓
训练损失 = 重构损失 + 低维稳态回归损失
  ↓
V_z = U_z - Γ_z ⊙ S_z
  ↓
低维 velocity graph / stream plot / CBDir 与 ICVCoh 评估
```

### 5. 关键数学公式

#### 5.1 CohAgg：用细胞邻居平滑低维表示

编码器先用 MLP 得到：

$$
Z_o=MLP(X)
$$

然后用带 self-loop 的邻接矩阵做两层图卷积：

$$
\tilde{Z}=\tilde{D}^{-1/2}\tilde{W}\tilde{D}^{-1/2}Z_o\Theta^{(1)}
$$

$$
Z=\tilde{D}^{-1/2}\tilde{W}\tilde{D}^{-1/2}\tilde{Z}\Theta^{(2)}.
$$

直观理解：一个细胞的表示不只来自它自己的表达，还会吸收邻居细胞的信息，因此速度方向更平滑。代码中 `Encoder` 支持 `GCNConv` 两层并带 self-loop（`VeloAE_code/veloproj/model.py:18-82`），邻接图在 `get_veloAE` 中由 scVelo connectivities 转为 PyTorch Geometric 的 edge tensors（`VeloAE_code/veloproj/util.py:774-826`）。但要注意：当前获取的 `main` 分支默认 `--gnn_layer GAT`，而论文写的是 GCN（`VeloAE_code/veloproj/util.py:68-75`）。

#### 5.2 AttComb：用注意力从 latent dimensions 重构基因

对每个基因 $i$，模型根据 gene representation 得到 query $q_i$；对每个 latent dimension $j$，根据 $Z_{:,j}$ 得到 key $k_j$。注意力权重为：

$$
\alpha_{i,j}=\mathrm{Gumbel\text{-}Softmax}\left(\frac{q_i^T k_j}{\sqrt{d_t}}\right).
$$

之后用注意力矩阵重构输入：

$$
\hat{X}=Z\cdot A^T.
$$

代码中 `Decoder.forward` 生成 query/key，`Attention.forward` 计算 scaled dot product、调用 `F.gumbel_softmax`，再矩阵乘法得到重构结果（`VeloAE_code/veloproj/model.py:85-168`）。

#### 5.3 训练目标：重构 + 低维回归

VeloAE 用同一个模型同时编码/重构 spliced 和 unspliced，以保证 latent dimensions 对齐。重构损失为：

$$
L_{rec}=MSE(S,\hat{S})+MSE(U,\hat{U}).
$$

为了模拟 RNA velocity 的稳态模型，论文在低维空间对极端分位细胞拟合：

$$
L_{reg}=\sum_i MSE(\tilde{u}_i,\hat{\gamma}_i\cdot\tilde{s}_i),
$$

$$
\hat{\gamma}_i=\frac{\tilde{u}_i^T\tilde{s}_i}{\tilde{s}_i^T\tilde{s}_i}.
$$

最终目标：

$$
L=L_{rec}+L_{reg}.
$$

代码中 `VeloAutoencoder.forward` 对一个输入矩阵返回 MSE 重构损失；`train_step_AE` 对多个输入（通常是 `S` 和 `U`）求和，然后调用 `leastsq_pt` 加上低维回归损失（`VeloAE_code/veloproj/model.py:307-458`; `VeloAE_code/veloproj/util.py:475-542`）。代码还提供 offset 选项，但论文公式没有 offset；默认参数不使用预测 offset（`VeloAE_code/veloproj/util.py:43-60`）。

#### 5.4 低维速度和细胞转移

训练完成后：

$$
V_z=U_z-\Gamma_z\odot S_z.
$$

代码的 `estimate_ld_velocity` 实现为 `u - gamma * s - offset`，默认可以保持与论文一致的 offset-free 形式（`VeloAE_code/veloproj/util.py:652-660`）。

论文进一步定义从细胞 $i$ 到邻居细胞 $j$ 的低维转移强度：

$$
\pi_{i,j}=\frac{(s_{zj}-s_{zi})^T\cdot v_{zi}}{\|s_{zj}-s_{zi}\|\cdot\|v_{zi}\|}.
$$

然后在邻居上 softmax 得到转移概率（`paper.md:235-244`）。本地代码没有找到这个公式的直接实现；它把低维速度放进 `AnnData` 后调用 `scv.tl.velocity_graph`（`VeloAE_code/veloproj/util.py:370-380`）。

### 6. 实验结果怎么支持方法？

论文用多个数据集验证：scNTseq 刺激时间序列、dentate gyrus OPC→OL、肠道 organoid、鼠/人 erythroid、pancreas 分支等（`paper.md:319-378`）。主要评估指标包括：

- **CBDir**：已知 A→B 时，检查 A 边界细胞 velocity 是否指向邻近 B 细胞（`paper.md:290-306`）。代码实现见 `cross_boundary_correctness`（`VeloAE_code/veloproj/eval_util.py:146-196`）。
- **ICVCoh**：同一 cluster 内邻居细胞 velocity 是否一致（`paper.md:307-318`）。代码实现见 `inner_cluster_coh`（`VeloAE_code/veloproj/eval_util.py:211-236`）。

Table 1 显示 VeloAE 在多个数据集上 ICVCoh 高，并且 CBDir 通常优于 scVelo、PCA、FA、普通 AE 和 ablation（`paper.md:69-76`）。主图中也能看到低维 VeloAE velocity stream 更平滑、更符合预期方向，尤其是 Fig. 2 的时间序列、Fig. 3 的 OPC→OL、Fig. 4 的肠道分支和 Fig. 5 的 erythroid/pancreas 示例。

### 7. 代码复现时需要注意

- 当前代码仓库是 `main` 分支的后续版本，commit 为 `2998bafddcd22de47555ba4fb878ab948a15728a`。README 说明 2022 年有更新，并提到之前数据备份在 `paper-version-backup` 分支（`VeloAE_code/README.md:10-18`）。
- 论文 CohAgg 是 GCN；当前代码默认是 GAT，需要显式设置或切换到论文版本才能更接近原文。
- Eq. 10 的 softmax transition 在 VeloAE 本地代码中没有找到，代码委托 scVelo 构建 velocity graph。
- 本地没有 supplementary markdown/PDF，因此 SI 表格中的完整超参数和补充图没有被验证。
- 数据有些来自外部论文或需要请求，不能仅靠本仓库保证完整一键复现（`paper.md:319-378`）。

### 8. 一句话总结

VeloAE 的本质是：把 RNA velocity 从嘈杂的高维基因空间，搬到一个由图平滑编码器和注意力解码器学习出的低维空间中，再在该空间估计速度和转移方向。论文和代码都支持核心 autoencoder、AttComb、latent regression 和 velocity projection；但复现论文时必须处理好 GCN/GAT 版本差异、scVelo 委托的 transition graph，以及缺失的本地补充材料。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## VeloAE Summary

### What problem does the paper solve?

RNA velocity uses spliced and unspliced RNA to infer short-term cell-state transitions, but transition estimates can be unstable in high-dimensional gene space because unspliced counts are sparse/noisy and different genes may imply contradictory directions (`paper.md:15-33`). VeloAE proposes to learn a denoised low-dimensional representation where both cell states and velocity vectors can be compared more robustly (`paper.md:31-41`).

### Proposed method

**Velocity Autoencoder (VeloAE)** is a tailored autoencoder for RNA velocity. It jointly fits spliced and unspliced matrices with two main additions over a vanilla autoencoder:

1. **CohAgg**: an encoder-side graph module that smooths a cell's latent representation with its neighbors using a GCN in the paper formulation (`paper.md:162-180`).
2. **AttComb**: a decoder-side attention module that uses gene representations as queries and latent dimensions as keys, then reconstructs gene profiles from attention-weighted latent dimensions (`paper.md:183-204`).

After training, VeloAE fits per-latent-dimension degradation coefficients and computes latent velocity $V_z=U_z-\Gamma_z\odot S_z$ (`paper.md:206-230`). It then estimates transitions in latent space using scVelo-style cosine transition scores and softmax over neighbors (`paper.md:235-244`).

### Evaluation and main results

The paper evaluates VeloAE on stimulation time series, dentate gyrus neurogenesis, intestinal organoid differentiation, erythroid mouse/human development, pancreas lineages, and additional challenging datasets (`paper.md:319-378`). It introduces or uses two quantitative metrics:

- **CBDir**: direction correctness for known cross-cluster transitions (`paper.md:290-306`).
- **ICVCoh**: within-cluster velocity coherence (`paper.md:307-318`).

Across Table 1, VeloAE has consistently high ICVCoh and often substantially better CBDir than scVelo, PCA, FA, vanilla AE, and ablation variants (`paper.md:69-76`). Figures 2-5 visually support improvements: low-dimensional panels show smoother or more biologically expected velocity streams than raw scVelo panels, especially in scNTseq, dentate gyrus OPC-to-OL, intestinal organoid branches, erythroid development, and pancreas branches.

### Code-paper match

A GitHub repository was acquired at `[local path omitted]`, commit `2998bafddcd22de47555ba4fb878ab948a15728a`. The match is **medium**:

- Directly implemented: AttComb attention/reconstruction (`VeloAE_code/veloproj/model.py:85-168`), shared VeloAE model (`model.py:307-356`), latent regression helpers (`model.py:358-458`), training loop (`VeloAE_code/veloproj/util.py:247-335`, `util.py:475-542`), latent velocity projection (`util.py:337-394`, `util.py:652-660`), CLI workflow (`VeloAE_code/veloproj/veloproj.py:11-69`), and CBDir/ICVCoh metrics (`VeloAE_code/veloproj/eval_util.py:146-230`).
- Important mismatch: the paper describes GCN CohAgg, but acquired `main` defaults to `GAT` (`VeloAE_code/veloproj/util.py:68-75`); the README says post-paper updates involved GAT and that previous data were backed up in `paper-version-backup` (`VeloAE_code/README.md:10-18`).
- Not found: a local VeloAE implementation of paper Eq. 10 transition softmax. The code delegates latent transition graph computation to `scv.tl.velocity_graph` (`VeloAE_code/veloproj/util.py:370-380`).

### Reproducibility notes

The repository provides installation instructions, a CLI, examples, notebooks/dataset notes, and pretrained-model references (`VeloAE_code/README.md:1-118`). However, full reproduction is not turnkey from the locally acquired evidence:

- Some datasets are previously published or request-only according to the paper (`paper.md:319-378`).
- Local supplementary markdown/PDF is missing, so SI hyperparameter tables and supplementary figures were not verified.
- The acquired `main` branch is post-publication and may not exactly match the PNAS experiments; paper-version pinning or branch selection is needed.
- The default preprocessing in code uses `min_shared_counts=30`, while the paper text states 20 (`paper.md:246-261`; `VeloAE_code/veloproj/util.py:397-407`).

### Bottom line

VeloAE is best understood as a postprocessing/representation-learning layer for RNA velocity: it trains a graph-and-attention autoencoder on spliced/unspliced moments, computes latent velocity, and uses the denoised latent space for more coherent transition inference. The paper's evidence supports improved directionality on several curated datasets, but reproducibility requires careful version control and awareness that the acquired code snapshot differs from the paper in graph-layer defaults and delegates transition graph construction to scVelo.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
