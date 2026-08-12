---
layout: default
permalink: /paper-atlas/sdevelo-93f3d269/
title: "SDEvelo"
nav: false
description: "RNA velocity 利用未剪接 RNA（U）到已剪接 RNA（S）的时间滞后推断细胞状态变化。经典模型对每个基因分别拟合 这种确定性逐基因建模有两个问题。第一，不同基因各自估计时间，随后再拼成一个细胞速度，跨基因时序可能不一致。第二，成熟细胞处于近稳态时仍有转录随机波动；强行用确定性场解释这些波动，可能在本应没有净迁移的细胞群中画出整齐而虚假的流线。"
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
      <span>Nature Communications · 2024</span>
    </div>
    <h1>SDEvelo</h1>
    <p>Multivariate stochastic modeling for transcriptional dynamics with cell-specific latent time using SDEvelo</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-024-55146-5" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SDEvelo：用多基因随机转录动力学估计 RNA velocity 与共享潜时间

### 1. 为什么传统逐基因 ODE 会在成熟细胞中“制造方向”

RNA velocity 利用未剪接 RNA（$U$）到已剪接 RNA（$S$）的时间滞后推断细胞状态变化。经典模型对每个基因分别拟合

$$
\frac{du}{dt}=\alpha(t)-\beta u,
\qquad
\frac{ds}{dt}=\beta u-\gamma s.
$$

这种确定性逐基因建模有两个问题。第一，不同基因各自估计时间，随后再拼成一个细胞速度，跨基因时序可能不一致。第二，成熟细胞处于近稳态时仍有转录随机波动；强行用确定性场解释这些波动，可能在本应没有净迁移的细胞群中画出整齐而虚假的流线。

SDEvelo 的目标是同时解决二者：把多个基因放在一个多变量随机微分方程中，并让同一细胞的所有基因共享一个潜时间。输入是 AnnData 中的未剪接/已剪接矩阵；输出包括基因动力学参数、每个细胞的 velocity、预测 $U/S$ 状态和共享 latent time。

### 2. 多变量 SDE：随机性进入转录过程本身

论文的核心模型为

$$
d\mathbf U(t)=
\bigl(\boldsymbol\alpha(t)-\boldsymbol\beta\odot\mathbf U(t)\bigr)dt
+\boldsymbol\sigma_1d\mathbf B_1(t),
$$

$$
d\mathbf S(t)=
\bigl(\boldsymbol\beta\odot\mathbf U(t)-\boldsymbol\gamma\odot\mathbf S(t)\bigr)dt
+\boldsymbol\sigma_2d\mathbf B_2(t).
$$

向量维度等于所选基因数。$\beta$ 和 $\gamma$ 分别是剪接与降解率，$\sigma_1,\sigma_2$ 控制过程噪声。随机项不是简单给观测值加误差，而是让每条生成轨迹在转录与剪接过程中发生随机扰动。

每个基因的转录率采用平滑开关：

$$
\alpha_i(t)=\frac{c_i}{1+\exp[b(t-a_i)]}.
$$

$a_i$ 是切换时间，$c_i$ 是转录幅度，$b$ 控制开关陡峭程度。代码把 `b` 初始化为 100 且 `requires_grad=True`，但没有把它交给任何 optimizer，所以实际训练中它固定为 100。该 sigmoid 因而非常接近阶跃函数，只是在数值上仍可微。

“多变量”在这里主要意味着所有基因的联合 $U/S$ 分布在同一个生成器和同一时间轴上匹配；当前漂移公式仍是逐基因参数化，并没有显式的基因—基因耦合矩阵。它可利用联合分布中的相关结构，但不能直接等同为学到了一个调控网络。

### 3. Euler–Maruyama 如何生成训练样本

本地 `_model.py` 默认以 $h=0.01$ 在 $t\in[0,1)$ 上迭代 100 步：

$$
U_{k+1}=\operatorname{ReLU}\left[
U_k+h(\alpha(t_k)-\beta U_k)
+\sigma_1\sqrt h\,Z_{1k}\right],
$$

$$
S_{k+1}=\operatorname{ReLU}\left[
S_k+h(\beta U_k-\gamma S_k)
+\sigma_2\sqrt h\,Z_{2k}\right].
$$

ReLU 保证生成丰度非负。代码也提供 `torchsde` 路线；若依赖不可用，甚至会尝试运行时安装，再失败回退到原始 Euler 实现。论文结果的复现应固定环境和 `sde_mode`，不能只说“使用 SDEvelo 默认设置”。

初值来自 $U$ 对 $S$ 的线性回归和离原点最近的观测点。若细胞数超过 `n_cell`，代码随机抽取子集用于参数初始化；训练 DataLoader 则基于模型保存的 $U/S$ 张量。预处理可调用 scVelo 的 `filter_and_normalize` 与 moments，默认常见设置为 `min_shared_counts=20`、PCA 30、邻居 30。

### 4. 不写似然，改为匹配真实与生成的联合分布

随机微分方程的精确似然难以计算。SDEvelo 每次生成一条 $K$ 基因轨迹，把所有时间步的 $U$ 和 $S$ 拼成 $2K$ 维样本，再与真实细胞的联合 $U/S$ 向量计算多核 Gaussian Maximum Mean Discrepancy：

$$
\operatorname{MMD}^2(P,Q)=
\mathbb E k(X,X')+
\mathbb E k(Y,Y')-
2\mathbb E k(X,Y).
$$

带宽由当前 pairwise distance 自适应估计，并叠加五个几何尺度的核。训练同时更新 $c,\beta,\gamma,a,\sigma_1,\sigma_2$ 以及 $U/S$ shift，并在每轮后夹紧到预设范围。

论文公式写的是最小化 MMD²；`mmd()` 最后返回 `loss.sqrt()`，即优化 MMD。两者在非负区域具有相同最小点和排序，但梯度尺度不同，因此应标为 Partial，而非逐式 Exact。论文称“adversarial learning”是广义的分布对抗：实现中没有单独判别器。

### 5. 一个共享 latent time 是怎样赋给真实细胞的

训练后模型生成时间网格上的联合状态

$$
\mathbf g_j=[\mathbf U(t_j),\mathbf S(t_j)].
$$

对真实细胞 $\mathbf r_i=[\mathbf U_i,\mathbf S_i]$，论文 Eq. 5 使用 entropic Sinkhorn OT，在真实分布和生成时间轨迹之间求运输计划，再把每个细胞分配到权重最大的生成时间点。这样一个细胞得到单一 $t_i$，所有基因共享它。

代码有两种模式：

- `time_mode=0`：计算平方欧氏距离并选择最近生成状态；这是默认。
- `time_mode=1`：使用 POT 的 `ot.sinkhorn(..., epsilon=0.5)`，再按每行最大权重分配；这才对应论文重点公式。

所以“运行默认 API”与“运行论文 OT latent time”不是同一件事。复现实验必须显式设置 `time_mode=1` 并安装 POT。即使使用 OT，赋值仍是把细胞投影到一条生成轨迹上的统计匹配，不是真实采样时间，也不保证分支系统有唯一全局时钟。

### 6. 最终 velocity 与训练 SDE 要分开理解

训练后 spliced velocity 的确定性部分是

$$
\frac{d\mathbf S}{dt}=\boldsymbol\beta\odot\mathbf U-
\boldsymbol\gamma\odot\mathbf S.
$$

代码输出层按 mode 组合观测或预测 $U/S$，并计算近似 Euler 增量：

$$
\mathbf v_S=
h(\boldsymbol\beta\odot\mathbf U-\boldsymbol\gamma\odot\mathbf S)
+\boldsymbol\sigma_2\sqrt h\,\mathbf Z.
$$

这里包含 $h=0.01$，因此存入 `.layers['sde_velocity']` 的量更接近一步增量，而不是未缩放的连续导数。更重要的是，最终 `velocity_cal()` 的随机数形状为 `(n_genes,)`，同一基因的一个噪声值会广播给所有细胞。训练轨迹生成阶段确实为每一步/基因采样随机噪声，但最终 velocity 层不是每细胞独立噪声。因而成熟 PBMC 图中的随机/弱方向来自整体模型和投影结果，不能把输出层描述为完整实现了每细胞 Wiener 增量。

### 7. 五张主图的证据链

#### 图 1：方法与模拟基准

图 1 展示多变量 SDE、MMD 分布匹配、共享 latent time 与下游输出。模拟中 SDEvelo 的潜时间更贴近真值，并在不同基因数下比较稳态比率误差和相关性。该图证明模型在作者设定的 ODE/SDE生成数据上可辨识参数，不证明真实数据中的真时间已知。

#### 图 2：成熟 PBMC 作为负对照

PBMC 中多数细胞已成熟，理论上不应出现跨细胞类型的大规模定向分化。若干 deterministic velocity 方法画出强流线；SDEvelo 更接近随机局部模式，并给出与成熟状态一致的潜时间结构。这个负对照支持其避免“强行赋方向”的目标，但成熟细胞仍可能有激活或亚群转换，不能先验认定所有局部运动均为零。

#### 图 3：肝癌空间转录组

SDEvelo 将 velocity 与 latent time 投影到空间位置，用于划分肿瘤/正常上皮边界，并把基因表达与潜时间相关联以筛选癌变候选基因。空间 spot 混合多个细胞，且未剪接 reads 的质量受技术影响；论文结果说明方法可以运行在该数据类型，不等于单 spot velocity 具有单细胞分辨率。

#### 图 4：MEF 到 iEP 重编程

方法区分成功重编程轨迹与 dead-end 路径，并将 latent time/velocity 与已知阶段比较。下游 CellRank 提供命运映射。CellRank 使用的是估计 velocity 与邻接图的组合，属于二级推断，不是独立实验谱系证据。

#### 图 5：红系分化与下游生物学

图 5 比较 SDEvelo 与 scVelo 的流线和潜时间，并沿潜时间展示基因表达热图、富集分析以及细胞通讯。它说明共享时钟可组织跨基因程序；GO、PPI 和 LIANA 等环节主要由外部工具完成，当前包内没有完整的 GOATOOLS/PINA 论文脚本，不能由核心源码单独复现。

### 8. 补充材料提供了什么

工作区保存四个补充 PDF。补图包含确定性/随机模拟、分支模拟、PBMC 负对照、空间癌症分析、重编程和红系数据的扩展比较；其他补充文件包含源数据/报告材料。由于没有转换成独立 Markdown，本轮以论文正文对补图的明确引用、图注及本地 PDF存在性作为边界，没有把未直接转录的补充数值扩写成新结论。

### 9. 论文—代码映射

| 论文组件 | 本地代码 | 判断 |
|---|---|---|
| 多基因 SDE 与 sigmoid $\alpha(t)$ | `sdevelo/_model.py:349-428` | **Direct** |
| Euler–Maruyama | `_model.py:349-381` | **Direct** |
| MMD² 目标 | `_model.py:55-107,430-484` | **Partial**：实现返回平方根，无判别器 |
| 参数学习 | `_model.py:181-215,430-465` | **Partial**：另含 shifts；`b` 未进 optimizer |
| Sinkhorn latent time | `_model.py:497-543` | **Partial**：实现存在，但默认走欧氏最近邻 |
| 共享细胞 latent time | `_model.py:538-542` | **Direct**：每细胞一个值 |
| 最终 velocity | `_model.py:555` 之后 | **Partial**：含 $h$；噪声按基因广播 |
| scVelo 预处理 | `_model.py:146-159` | **Direct**：版本分支可见 |
| CellRank/LIANA/GO/PINA 全部论文分析 | tutorial/外部工具 | **Partial / Not found**：核心包不含完整复现脚本 |
| ODE baseline 模拟 Eq. 9–10 | 外部 scVelo 数据模拟 | **Not found** 于核心包 |

核心 SDE、训练和推断 API 是可读且可安装的，论文也提供多个教程 notebook；但默认参数与论文 OT 路线不一致，部分外部下游分析和数据获取不完整，因此 paper–code fidelity 为中高，端到端复现约为 3/5。

### 10. 使用时必须保留的限制

- 所有基因共享一个潜时间简化了跨基因协调，但可能压缩真实分支、循环或异步基因程序。
- MMD 匹配联合分布，不使用真实细胞配对；相似分布可由不同动力学参数产生。
- Sigmoid 斜率实际固定为 100，转录开关比“灵活学习的平滑调控”更受限制。
- latent time 默认最近邻，论文 OT 需显式启用；两者可能给不同排序。
- 输出 velocity 是一步尺度增量，随机项并非每细胞独立采样。
- 空间 spot、scRNA-seq 深度和未剪接 read 质量会影响动力学拟合。
- 成熟群中的随机流线是合理负对照行为，但不能自动证明每条局部箭头的统计校准。
- 与 latent time 相关的癌症基因、GO 或通讯结果是关联性下游分析，不是因果调控证据。

SDEvelo 的核心贡献，是把“每个基因各自拟合一条确定性曲线”改成“在共同时间轴上匹配所有基因的随机联合分布”。它最适合回答细胞群是否呈现一致的转录进程、成熟状态是否缺乏净方向，以及共享潜时间能否组织下游程序；它并没有消除快照数据的不可辨识性，也不能替代真实时间、克隆谱系或扰动实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SDEvelo — Multivariate Stochastic RNA Velocity

**Paper**: Multivariate stochastic modeling for transcriptional dynamics with cell-specific latent time using SDEvelo
**Authors**: Xu Liao, Lican Kang, Yihao Peng, Xiaoran Chai, Peng Xie, Chengqi Lin, Hongkai Ji, Yuling Jiao*, Jin Liu*
**Journal**: *Nature Communications* 15 (2024-12-30)
**DOI**: 10.1038/s41467-024-55146-5
**Code**: https://github.com/Liao-Xu/SDEvelo

---

### Motivation & Novelty

#### Biological Problem

RNA velocity infers cellular dynamics by comparing unspliced (pre-mRNA) and spliced (mature mRNA) abundances. When transcription is active, unspliced RNA accumulates faster than it is processed; when a gene is being silenced, spliced RNA exceeds the steady-state level. These imbalances encode the direction each cell is heading.

However, two fundamental problems limit existing methods:

1. **False trajectories in mature cells**: Deterministic ODE models (Velocyto, La Manno et al., *Nature* 2018; scVelo, Bergen et al., *Nature Biotechnology* 2020) must assign a velocity direction to every cell, even those sampled from fully differentiated steady-state populations (e.g., blood cells). The result is strong but biologically spurious directional flows, a problem documented in Bergen et al. (*Molecular Systems Biology* 2021) and Zheng et al. (*Genome Biology* 2023).

2. **Univariate gene independence**: All major methods (scVelo, VeloVI by Gayoso et al. *Nature Biotechnology* 2023, VeloVAE, UniTVelo — Gao et al., *Nature Communications* 2022, DeepVelo — Cui et al., *Genome Biology* 2024) model each gene with its own independent time parameter, ignoring the fact that gene regulation is a collaborative, multi-gene process governed by a shared cell state.

#### Why Existing Methods Fall Short

| Method | Journal & Year | Issue |
|---|---|---|
| Velocyto | *Nature* 2018 | Steady-state ODE, gene-specific latent time, no noise |
| scVelo (stc/dyn) | *Nat. Biotechnol.* 2020 | Dynamical ODE, higher-order moments for noise, but still univariate |
| VeloVI | *Nat. Biotechnol.* 2023 | Variational Bayes on ODE, uncertainty captured, still per-gene |
| UniTVelo | *Nat. Commun.* 2022 | Unified time model, but deterministic ODE |
| DeepVelo | *Genome Biol.* 2024 | Multi-lineage kinetics, neural ODE, but no intrinsic stochasticity |
| VeloVAE | *Nat. Biotechnol.* 2023 | VAE with ODE, gene-specific latent time |
| VelvetSDE | *Cell Systems* 2024 | Neural SDE, but doesn't explicitly estimate kinetic parameters |
| PhyloVelo | — | Stochastic via phylogenetic tree — requires barcode experiments, not applicable to most human data |

#### SDEvelo's Unique Contributions

1. **Multivariate SDE**: The first RNA velocity method that jointly models all genes under a *single* cell-specific latent time via stochastic differential equations with explicit, interpretable kinetic parameters.
2. **Stochastic framework for mature cells**: Intrinsic noise in the SDE naturally produces random velocity fields in equilibrium populations — no artificial "maturity correction" needed.
3. **Adversarial parameter learning via MMD**: Avoids intractable SDE likelihoods by minimizing Maximum Mean Discrepancy between generated and real data distributions — a kernel-based GAN-like approach.
4. **Sigmoid transcription rate**: Replaces the non-differentiable step-function used in existing methods, enabling smooth gradient-based optimization and better modeling of gradual expression changes.
5. **Spatial transcriptomics compatibility**: Directly applicable to sequencing-based spatial data (10x Visium) with the same pipeline, without spatial-specific modifications.

---

### Method Overview

SDEvelo is a generative model that models RNA transcriptional dynamics as a multivariate stochastic differential equation (SDE):

$$d\mathbf{U}(t) = (\boldsymbol{\alpha}(t) - \boldsymbol{\beta} \odot \mathbf{U}(t))dt + \boldsymbol{\sigma}_1 d\mathbf{B}(t)$$
$$d\mathbf{S}(t) = (\boldsymbol{\beta} \odot \mathbf{U}(t) - \boldsymbol{\gamma} \odot \mathbf{S}(t))dt + \boldsymbol{\sigma}_2 d\mathbf{B}(t)$$

where all p genes share a **single cell-specific latent time t**. The transcription rate uses a differentiable sigmoid: $\alpha_i(t) = c_i / (1 + e^{b(t-a_i)})$.

**Training**: Euler-Maruyama discretization generates synthetic trajectories from current parameters; Maximum Mean Discrepancy (5 Gaussian kernels, adaptive bandwidth) quantifies distributional distance to real data; three Adam optimizers with different learning rates update kinetic parameters.

**Latent time**: Real cells are matched to the nearest point on the trained SDE trajectory (nearest-neighbor by default; optional Sinkhorn optimal transport).

**Downstream**: The estimated velocity and cell-specific latent time feed into CellRank (fate mapping), LIANA (cell-cell communication), GO enrichment, and cancer driver gene detection via latent-time correlation.

---

### Evaluation

#### Simulated Data

- **ODE-simulated data** (scvelo.datasets.simulation): 500 cells, 100–1000 genes. SDEvelo achieved lowest ratio errors (|γ̂/β̂ − γ/β|) and highest Pearson correlation between estimated and true latent time (Fig. 1f).
- **SDE-simulated data**: Same metrics; SDEvelo correctly recovered stochastic trajectories while scVelo produced inconsistent directions (Fig. 1e).
- **Branching data**: SDEvelo correctly identified branching trajectories at all gene numbers (100–1000); Supplementary Fig. S3.

#### Real Datasets

| Dataset | Technology | Cells/Spots | Genes after QC | Key Result |
|---|---|---|---|---|
| Human PBMC | 10x Chromium | 65,877 cells | 601 HVGs | SDEvelo: random velocity (correct for mature cells); others: strong false directions |
| HCC spatial | 10x Visium | 9,812 spots (4 sections) | 1,985 genes | Highest CBDir, AUC, AUPR ratio; correct stroma→TNE transition; 562 cancer driver genes |
| Mouse reprogramming (MEF→iEP) | 10x Genomics + Drop-seq | 85,010 cells | 2,000 HVGs | Highest Pearson r with reprogramming days; correct two-trajectory detection (dead-end vs success) |
| Mouse erythroid | 10x Genomics | 9,815 cells | 2,000 HVGs | Correct BP→Ery transitions; transcriptional boost genes correctly handled |

#### Quantitative Metrics

- **Ratio errors**: SDEvelo = lowest across all gene counts (100–1000)
- **Pearson r (latent time)**: SDEvelo = highest in all simulated settings
- **CBDir score**: SDEvelo = highest in all 4 HCC sections
- **AUC/AUPR**: SDEvelo = best transition probability on HCC
- **Spearman rank correlation (latent time)**: SDEvelo = best on HCC vs scVelo, UniTVelo, VeloVAE, DeepVelo, VeloVI

---

### Reproducibility: 3 / 5

**Justification**: The core mathematical framework is fully implemented in a well-structured Python package (`sdevelo`, available on PyPI). Key evaluation metrics (CBDir, ratio errors) are in notebooks rather than the main package. A critical discrepancy exists between the paper's primary latent time method (Sinkhorn OT, Eq. 5) and the code default (nearest-neighbor, `time_mode=0`), which may affect exact result reproduction.

**Strengths**:
- Clean, documented Python package installable via `pip install sdevelo`
- Standard AnnData/scVelo preprocessing pipeline — no custom data formats
- Jupyter notebooks with step-by-step demos at https://sdevelo.readthedocs.io
- All 4 datasets are public (scVelo's built-in loaders or NCBI SRA)
- Random seeds set (`seed=0` default), deterministic behavior on CPU
- Source data files provided with the paper

**Weaknesses**:
- Default latent time (`time_mode=0`, nearest-neighbor) differs from paper's described method (Sinkhorn OT)
- β and γ are both initialized from `max(unspliced)` — unusual initialization not documented
- Evaluation scripts (CBDir, ratio errors) are in notebooks, not in the main package
- b=100 is fixed but initialized with `requires_grad=True` — confusing to users
- GPU training: requires CUDA; `cuda_device=2` hardcoded in Config (may need manual override)
- `infer_gene_correlations()` assumes dense matrix (`.X.A`) — fails on sparse AnnData

**Environment setup**:
```bash
pip install sdevelo
pip install scvelo==0.2.5  # or >=0.3.0 (both supported)
pip install cellrank liana goatools  # for downstream analyses
pip install POT  # optional: for OT-based latent time (time_mode=1)
```

**Common pitfalls**:
1. Set `args.cuda_device` to your GPU index (default=2 may not be valid)
2. For OT-based latent time (paper's method): set `args.time_mode = 1`
3. Input layers must be named `Mu`/`Ms` (scVelo moments output); or change `args.ukey`/`args.skey`
4. Memory: for >5000 cells, subsampling is automatic but produces different results each run unless `seed` is set
5. `infer_gene_correlations()` requires dense `.X` — call `adata.X = adata.X.toarray()` first if sparse

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
