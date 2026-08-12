---
layout: default
permalink: /paper-atlas/neurovelo-e652881a/
title: "NeuroVelo"
nav: false
description: "NeuroVelo 把 spliced 与 unspliced RNA 用同一个线性编码器压到低维空间，同时学习每个细胞的伪时间和一个潜空间神经 ODE。训练既要求能重构观测表达、ODE 轨迹能穿过编码后的细胞，也要求 ODE 导数接近 splicing kinetics 给出的 velocity。训练后，ODE 导数可解码为基因空间 velocity；"
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
      <span>Cell Reports Methods · 2026</span>
    </div>
    <h1>NeuroVelo</h1>
    <p>Interpretable learning of temporal cellular dynamics from single-cell data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.crmeth.2026.101342" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## NeuroVelo：用线性潜空间连接 RNA velocity、神经 ODE 与局部基因网络

### 一句话理解

NeuroVelo 把 spliced 与 unspliced RNA 用同一个线性编码器压到低维空间，同时学习每个细胞的伪时间和一个潜空间神经 ODE。训练既要求能重构观测表达、ODE 轨迹能穿过编码后的细胞，也要求 ODE 导数接近 splicing kinetics 给出的 velocity。训练后，ODE 导数可解码为基因空间 velocity；在某个潜空间点计算 ODE Jacobian，再用线性编码/解码矩阵映射回基因坐标，得到一个局部、状态依赖的交互分数矩阵。

这里的“GRN”是模型局部线性化产生的有向权重，不是实验干预确认的因果网络。

### 1. 输入和两个互相耦合的坐标

输入是同一批细胞的 spliced 矩阵 $X_s$ 与 unspliced 矩阵 $X_u$。同一个两层线性编码器 $E$ 分别产生

$$z_s=E(X_s),\qquad z_u=E(X_u).$$

编码器的第一层还接出一个 sigmoid 头，使用 spliced 输入预测

$$t=\sigma(W_t h_s+b_t)\in(0,1).$$

代码中的 `Encoder` 没有在线性层之间加入激活（`module.py:70-92`），所以两层组合仍是一张线性映射。spliced 与 unspliced 共享全部编码权重，但权重由两个重构项和动力学项共同训练，不能说潜空间只由 spliced geometry 决定。

sigmoid 只给出相对伪时间。若没有外部方向信息，同时把 $t$ 反转并把向量场变号仍可描述同一几何轨迹；论文也明确承认这一方向不可辨识性。

### 2. 每个 sample 有一个潜空间 ODE

对 sample/treatment $d$，模型使用

$$\frac{dz_s^{(d)}}{dt}=f^{(d)}(z_s),$$

其中 `LatentODE` 是 Linear–ELU–Linear 网络（`module.py:5-48`）。虽然 `forward(t,x)` 接受时间，函数体不使用 `t`，所以实际是 autonomous ODE。`TNODE.lode_func` 为每个 sample 建一个独立网络（`model.py:67`）。

训练时，一个 minibatch 先按预测伪时间排序；每个 sample 取最早细胞的 $z_s$ 为初值，再用 `torchdiffeq.odeint` 沿该批次的伪时间积分（`model.py:120-155`）。重复时间点会被删除，因为求解器要求严格单调的时间序列。

这一实现对每个 sample/batch 形成一条确定性积分曲线，并没有显式的分叉 ODE 或 lineage-specific initial conditions。低维嵌入图上的分支表现来自整体表示与后续投影，不能理解为求解器真的从一个初值产生了多条随机分支。

### 3. 四个基础损失如何互相约束

默认 `pre_ptime=False`、`reconstruct_xt=False` 时，总损失为：

$$
\mathcal L=\mathrm{MSE}(X_s,D(z_s))+\mathrm{MSE}(X_u,D(z_u))+
\sum_d\mathrm{MSE}\!\left(f^{(d)}(\hat z_s),e^\beta z_u-e^\lambda z_s\right)+
\mathrm{MSE}(z_s,\hat z_s).
$$

- 前两项让共享线性 autoencoder 保留 spliced/unspliced 信息。
- 第三项是 physics-informed constraint。$e^\beta$ 与 $e^\lambda$ 保证速率为正；代码中二者是长度为 `n_latent` 的向量，不是逐基因 kinetic rates。
- 第四项要求从批次最早状态积分出的 $\hat z_s(t)$ 靠近编码得到的 $z_s$。

velocity constraint 在 `model.py:155` 比较的是 $f(\hat z_s)$，即 ODE 预测轨迹上的导数，而右侧用观测编码 $z_u,z_s$。当 `reconstruct_xt=True` 时最后一项改为 gene-space 重构；当 `pre_ptime=True` 时还加入外部 `adata.obs['latent_time']` 对预测时间的 MSE，因此不再是完全无监督的伪时间学习。

### 4. velocity 怎样回到基因空间

训练后先编码细胞，在其潜状态计算 $f^{(d)}(z_s)$，再通过线性 decoder 得到 gene-space 向量。对纯线性映射 $D(z)=W_dz+b_d$，速度变换是 $W_df(z)$，bias 对导数没有贡献。

`latent_data()` 正确构造潜空间 AnnData，把 $z_s$ 放入 `spliced`，把 $f(z_s)$ 放入 `spliced_velocity`（`utils.py:211-236`）。然而当前 `decode_gene_velocity()` 在 `utils.py:208` 把 Torch tensor 的 `.values` 属性传给 ODE 网络，而不是传 tensor 本身；该 helper 在此代码快照存在运行缺陷。旧 README 推荐的 gene-space velocity 路径不能未经修正就视为已验证可运行。

### 5. Jacobian 为什么能提供局部交互分数

在潜状态 $z^*$ 附近，神经 ODE 可一阶展开：

$$f(z^*+\delta z)\approx f(z^*)+J(z^*)\delta z,\qquad J_{ij}=\frac{\partial f_i}{\partial z_j}.$$

若组合编码矩阵为 $W_e$，组合解码矩阵为 $W_d$，代码构造

$$A=W_dJ(z^*)W_e$$

并因图的 source/target 约定再转置（`grn.py:41-49,85-105`）。$A$ 表示：在模型学到的线性投影下，小的基因表达扰动如何改变解码后的局部速度。

这个映射在代数上是精确计算的，但它不是对真实生化调控的“精确恢复”：encoder/decoder 未被约束为严格互逆，潜空间丢弃信息，网络也可能通过相关结构拟合。阈值化 $A$ 得到的边应称为候选局部调控关系；论文用 ChIP-seq proxy 做 benchmark，也不能覆盖所有功能性调控。

### 6. 静态与随时间变化的网络

`GraphMaker` 可在全部细胞、指定 cell types 或伪时间窗口的平均潜状态上计算 Jacobian。移动窗口便得到随伪时间变化的 $A(t)$，`GraphMakerAnimation` 用它制作动态图。

但当前 `GraphMaker.assign_samples()` 会把所有细胞的 `sample` 强制设为 0，`graph_maker()` 也固定使用 `node_0`（`grn.py:20-49`）。因此训练虽支持 sample-specific ODE，现有 GRN helper 不会自动为多个 sample 选择各自的 ODE；多条件分析需要分开输入或修改后处理代码。

### 7. leading eigenvectors 与基因排序

Jacobian 的大模特征值对应局部变化最强的方向。`ModelAnalyzer` 在各模型中计算 latent Jacobian eigenvectors，经 decoder 映射到 gene weights，再用跨随机种子 cosine similarity 对齐方向并汇总排名。这更像“哪些基因参与主导动态 mode”，不等同于每个基因的直接调控出度。

论文用 Velocity Alignment 比较不同随机初始化产生的同一细胞 velocity。当前 `vector_fields_similarity()` 对 model pair 的 cell-wise cosine 取绝对均值，因此方向完全反转也会得到高绝对相似度；使用时必须结合伪时间方向检查。

### 8. 论文主图该怎样读

Figure 1 是结构图：线性 phase space、非线性一维伪时间、神经 ODE 与 RNA-velocity constraint 共同训练。图中 gene-space velocity 是 latent derivative 的线性解码，GRN 则来自局部 Jacobian，不是同一个输出。

Figures 2–4 分别在 mouse gastrulation、human bone marrow 与 pancreas 上比较 CBDir、ICCoh、GSEA 与 ChIP-seq proxy AUPRC。论文称 NeuroVelo 在部分 cell types 的 GRN AUPRC ratio 最优；这些 benchmark 是数据集和选择流程的结果，并不表示每个预测 edge 都被验证。

Figure 5 用 lineage-barcoded lung cancer 数据，把仅从 RNA 学到的伪时间与 barcode-derived fitness signature 做 Spearman correlation。相关性支持排序一致，但 fitness signature 本身也是推导量，不是细胞的真实采样时间。

本地 `paper.md` 只保留正文与 captions，没有论文面板图片；`NeuroVelo/figures/model_final.png` 是代码仓库的模型示意，可验证训练结构，但不能替代论文 Figures 2–5 的视觉证据。

### 9. 当前代码的复现边界

- 论文写 latent dimension 50、ODE hidden 100；`Trainer` 默认分别为 5、25，底层模块默认又是 20、128。
- 三个附带 notebook 的 `Trainer(...)` 调用未覆盖这两个维度，因此实际跟随代码默认 5、25，而不是旧分析所猜测的论文值。
- `Trainer` 的 `percent=None`、`nepoch=None` 并未实现 docstring 所述自动默认；notebook 明确传入 `percent=0.8` 和 160/300/400 epochs。直接使用默认值会在数据切分或训练循环失败。
- README 示例使用不存在的 `sample_obs` 参数名，实际参数是 `odesample_obs`；示例还漏传 `percent` 与 `nepoch`。
- `odesample_obs=None` 会创建名为 `None` 的临时列并可运行单 sample，但显式提供列名更清楚；多 sample 时必须保证标签是从 0 到 `n_sample-1` 的整数，因为代码直接用 `g == i`。
- 当前 `decode_gene_velocity()` 和 multi-sample `GraphMaker` 有上述后处理缺陷。
- 源码 provenance 由 `NeuroVelo/.repo_source` 记录为提交 `0f069baf23e64b1184af70b9983060d28d9fb6a3`，包版本为 1.2.0。

### 10. 一个小例子

假设潜空间只有两维，某点的 Jacobian 为

$$J=\begin{pmatrix}0.8&-0.2\\0.1&-0.5\end{pmatrix}.$$

第一维的小扰动会增强第一维速度并轻微增强第二维速度；第二维扰动会抑制两维速度。乘上 $W_d$ 与 $W_e$ 后，这些潜维关系被展开为 gene-by-gene 权重。某条正边意味着“在当前状态和当前模型投影下，gene $j$ 增加与 gene $i$ 的预测速度增加相关”，而不是单凭该矩阵就证明 $j$ 直接结合并激活 $i$。

### 证据入口

- 论文正文与 captions：`paper.md`。
- 模型示意：`NeuroVelo/figures/model_final.png`。
- 线性编码器、decoder 与 ODE：`NeuroVelo/neurovelo/module.py`。
- 训练前向与损失：`NeuroVelo/neurovelo/model.py`。
- Trainer 与 notebook 参数：`NeuroVelo/neurovelo/train.py`、`NeuroVelo/notebooks/*.ipynb`。
- velocity 与 ensemble：`NeuroVelo/neurovelo/utils.py`。
- Jacobian 网络：`NeuroVelo/neurovelo/grn.py`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## NeuroVelo — Summary

**Paper**: Interpretable learning of temporal cellular dynamics from single-cell data
**Authors**: Idris Kouadri Boudjelthia, Salvatore Milite, Nour El Kazwini, Yuanhua Huang, Andrea Sottoriva, Guido Sanguinetti
**Journal**: Cell Reports Methods, 6, 101342 (2026)
**DOI**: 10.1016/j.crmeth.2026.101342
**Code**: https://github.com/idriskb/NeuroVelo

---

### Motivation & Novelty

**Biological problem**: Reconstructing temporal cellular dynamics from static scRNA-seq snapshots. While RNA velocity methods provide cell-level velocity vectors showing where cells are heading, they cannot explain *why* — they do not directly reveal the gene regulatory networks (GRNs) that drive the observed dynamics.

**Limitations of existing methods**:
- **scVelo** (*Nat. Biotechnol.* 2020): Gold-standard RNA velocity, but uses strong parametric assumptions (first-order kinetics) and cannot extract GRNs directly.
- **DeepVelo** (*Sci. Adv.* 2022): Couples RNA velocity with neural ODEs but uses non-linear projections that obscure interpretability.
- **latentVelo** (*Cell Rep. Methods* 2023): Non-linear dimensionality reduction with velocity; less interpretable.
- **UniTVelo** (*Nat. Commun.* 2022): Focuses on improved pseudotime; no GRN component.
- **scTour** (*Genome Biol.* 2023): Neural ODE for trajectories but does not use splicing information.
- **Dynamo** (*Cell* 2022): Uses dynamical systems theory similar to NeuroVelo, but requires metabolically labeled data (not standard scRNA-seq).
- **GENIE3** (*PLoS One* 2010), **GRNBoost2** (*Bioinformatics* 2018): Dedicated GRN methods, but require TF gene lists and are run separately from trajectory inference.

**NeuroVelo's unique contributions**:
1. **Joint trajectory + GRN inference**: A single model simultaneously produces RNA velocity fields and interpretable gene regulatory networks — no post-hoc GRN step needed.
2. **Linear phase space**: By constraining the latent encoding to be linear, the neural ODE Jacobian can be mapped algebraically to gene space ($\hat{J}=W_dJW_e$), yielding a projected local interaction-score matrix.
3. **Physics-informed training**: The RNA velocity splicing constraint ($f(z_s) \approx e^\beta z_u - e^\gamma z_s$) is imposed as a soft loss penalty, not a hard parametric assumption, removing global kinetic constraints.
4. **Robustness via ensemble**: A Velocity Alignment metric selects the best hyperparameters across multiple random seeds; gene rankings are averaged across aligned eigenvectors from multiple models.

---

### Method Overview

NeuroVelo is a physics-informed neural ODE model with a linear autoencoder backbone.

**Architecture**:
- **Linear encoder** ($g \to l$ dims, paper default $l = 50$): maps spliced and unspliced reads into a shared linear latent space. Linearity enables an algebraic projection of the latent Jacobian into gene coordinates.
- **Non-linear 1D pseudotime encoder**: a sigmoid layer producing $t \in (0,1)$ per cell; shares the first encoder layer with the latent encoder.
- **Sample-specific Neural ODE**: one 2-layer ELU network $f^{(d)}$ per sample/treatment group, solving $dz_s/dt = f^{(d)}(z_s, t)$ in latent space.
- **Linear decoder** ($l \to g$): reconstructs gene expression from latent coordinates.

**Training objective** (4 terms):
1. MSE reconstruction of spliced reads
2. MSE reconstruction of unspliced reads
3. RNA velocity constraint in latent space: $\text{MSE}(f(z_s), e^\beta z_u - e^\gamma z_s)$
4. Trajectory alignment: $\text{MSE}(z_s(t), z_s)$ (ODE solution should match observed latent positions)

**GRN extraction** (post-training):
- Compute Jacobian $J = \partial f / \partial z$ at the mean latent position of a cell type
- Decode to gene space: $\hat{J} = W_d J W_e \in \mathbb{R}^{g \times g}$
- $\hat{J}_{ij}$ gives the influence of gene $j$ on gene $i$'s transcription rate

**Gene ranking**: leading eigenvectors of $J$, decoded to gene space and averaged across multiple trained models using cosine-similarity alignment.

---

### Evaluation

**Datasets** (5 total):
| Dataset | Cells | Genes | Type |
|---|---|---|---|
| Mouse gastrulation (erythroid) | 9,815 | median 2,791 | Standard scRNA-seq |
| Human bone marrow | 5,780 | median 1,190 | Standard scRNA-seq |
| Pancreatic endocrinogenesis | 3,696 | median 2,447 | Standard scRNA-seq |
| Mouse cancer (KP-Tracer, 3726_NT_T1) | 754 | median 3,490 | Lineage-barcoded |
| Mouse cancer (KP-Tracer, 3435_NT_T1) | 1,082 | median 2,352 | Lineage-barcoded |

**Competing methods**: scVelo (*Nat. Biotechnol.* 2020), UniTVelo (*Nat. Commun.* 2022), latentVelo (*Cell Rep. Methods* 2023), DeepVelo (*Sci. Adv.* 2022), scTour (*Genome Biol.* 2023), Dynamo (*Cell* 2022), PhyloVelo (*Nat. Biotechnol.* 2023, for barcoded data)

**Velocity metrics**:
- **CBDir** (cross-boundary direction correctness): cosine similarity between velocity vectors and expected transition directions across cluster boundaries. NeuroVelo achieves state-of-the-art or competitive on all 3 standard datasets.
- **ICCoh** (in-cluster coherence): velocity consistency within clusters. Similarly strong performance.

**GRN metrics**:
- **AUPRC ratio** (vs. random baseline): normalized area under precision-recall curve against ChIP-seq gold standard from ChIP-Atlas (±10kb from TSS, MACS2 score)
- NeuroVelo outperforms GENIE3 and GRNBoost2 in 4/8 cell types (human bone marrow) and 4/8 (mouse gastrulation), without requiring TF gene lists as input

**Pseudotime validation on barcoded data**: Spearman correlation between inferred pseudotime and barcode-derived fitness signature. NeuroVelo performs comparably to PhyloVelo (which uses barcode information directly) on both cancer datasets; significantly outperforms scVelo and DeepVelo.

**GSEA validation**: Pathways identified from NeuroVelo eigenvector gene rankings match known biology — erythroid differentiation, immune cell proliferation, insulin secretion — with higher or comparable enrichment scores compared to scVelo driver genes.

---

### Reproducibility

**Rating: 3/5**

**Justification**:
- Code is available on GitHub and PyPI (`pip install neurovelo`)
- Three main datasets (mouse gastrulation, bone marrow, pancreas) are embedded in scVelo package — easily accessible
- Pre-trained models (5-6 seeds per dataset) are provided in `notebooks/trained_models/` — saves significant training time
- Jupyter notebooks for all three main datasets provided with full workflows

**Issues**:
- **Hyperparameter discrepancy**: Paper states default latent dim = 50, ODE hidden = 100, but `Trainer` defaults are 5 and 25 respectively. Researchers following the paper's stated defaults will get different results than following the code defaults. Notebooks likely use non-default values.
- **Lineage-barcoded data** (KP-Tracer): Raw data must be requested directly from Wang et al. — not publicly available in standard repositories.
- **Python version constraint**: Requires Python ≥ 3.8, ≤ 3.9.10 — tight constraint that may conflict with modern environments.
- **Multiple random seeds required**: Paper trains 5-6 models per dataset for robust results; training time multiplied accordingly.
- **No CLAUDE.md or docs site**: Navigation between notebooks is not guided; no reproducibility instructions in `README.md` specify which hyperparameters were actually used for each dataset.

**Environment setup**:
```bash
# Preferred: use environment.yml
conda env create -f environment.yml
# Or pip
pip install neurovelo  # PyPI version
pip install git+https://github.com/idriskb/NeuroVelo  # Latest
```

**Common pitfalls**:
- Do not silently mix paper values (`n_latent=50`, `n_ode_hidden=100`) with the bundled notebooks, which leave the `Trainer` defaults at 5 and 25
- Input AnnData must already have HVG selection and normalization done (scVelo preprocessing)
- Explicitly set `percent` and `nepoch`; both default to `None` without a working automatic fallback
- Prefer an explicit `odesample_obs` column; for multiple samples its values must be integer labels `0..n_sample-1`
- The current `decode_gene_velocity()` has a tensor `.values` bug, and `GraphMaker` forces GRN extraction through `node_0`
- Use `latent_data()` for the verified latent-space velocity path; gene-space projection requires correcting `decode_gene_velocity()` first
- Multiple seeds (≥5) are necessary for reliable gene rankings — single-seed results may vary

**Strengths**: Clean, modular PyTorch code; pre-trained models reduce barrier; Zenodo archive for reproducibility.
**Weaknesses**: Hyperparameter documentation inconsistency; no automated pipeline; barcoded data not fully accessible.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
