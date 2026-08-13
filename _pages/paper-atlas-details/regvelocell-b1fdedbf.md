---
layout: default
permalink: /paper-atlas/regvelocell-b1fdedbf/
title: "RegVeloCell"
nav: false
description: "经典 RNA velocity 为每个基因拟合近似独立的转录、剪接和降解动力学；RegVelo 把转录率改成所有上游 spliced regulator 表达的非线性函数。这样 GRN 权重、RNA 动力学、基因级潜在时间和 velocity 可在同一个生成模型中联合估计，并可通过切断某 TF 的出边重新计算 vector field。"
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
      <span>Cell · 2026</span>
    </div>
    <h1>RegVeloCell</h1>
    <p>RegVelo: Gene-regulatory-informed dynamics of single cells</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2026.04.022" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for RegVeloCell">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/theislab/regvelo" target="_blank" rel="noopener noreferrer" aria-label="Open code for RegVeloCell">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## RegVelo：把基因调控网络写进 RNA velocity 动力学

论文：*RegVelo: Gene-regulatory-informed dynamics of single cells*（Cell, 2026；DOI: 10.1016/j.cell.2026.04.022）

### 一句话理解

经典 RNA velocity 为每个基因拟合近似独立的转录、剪接和降解动力学；RegVelo 把转录率改成所有上游 spliced regulator 表达的非线性函数。这样 GRN 权重、RNA 动力学、基因级潜在时间和 velocity 可在同一个生成模型中联合估计，并可通过切断某 TF 的出边重新计算 vector field。

但这种重计算是模型内的 regulon-edge perturbation，不等同于真实基因敲除，也不自动包含蛋白稳定性、反馈重塑、细胞死亡和微环境响应。

### 1. 输入和输出

典型输入包括：

- AnnData 中经过邻域平滑的一阶矩 `Ms`（spliced）与 `Mu`（unspliced）；
- 一张先验 GRN skeleton，行列经代码对齐到 genes；
- regulator/TF 列表；
- 可选的软/硬结构约束和正则强度。

模型主要输出：

- 每个基因的剪接率 $\beta_g$ 和降解率 $\gamma_g$；
- GRN 权重矩阵 $W$ 与基线转录 bias $b$；
- 每个 cell–gene 的潜在时间 $t_{ng}$；
- 预测的 $\bar u_{ng},\bar s_{ng}$ 和 spliced velocity；
- 由 velocity 交给 CellRank 后得到的转移、终末状态和 fate probabilities；
- 修改 GRN 后重新估计的 perturbation vector field 与下游 fate/density change 指标。

### 2. 预处理为何影响“先验网络”本身

论文流程先做常见 scVelo 过滤、归一化、HVG 和 moments，再由 `preprocess_data()` 对 `Ms`、`Mu` 分别按基因做 min–max scaling。随后先跑 scVelo deterministic regression，只保留 `velocity_r2 > 0`、`velocity_gamma > 0` 且被标为 velocity gene 的基因；论文说明 TF 即便不通过 velocity-gene 筛选也应尽量保留，但具体保留逻辑依赖外层数据脚本。

`set_prior_grn()` 并不是原样存入用户网络。默认 `cor_filter=True` 时，它把先验 edge weight 乘以 `Ms` 表达相关系数，再以绝对值 0.01 二值化，删除自环，并在 `keep_dim=False` 时裁掉没有边的基因。于是模型实际看到的 skeleton 可能与 SCENIC+/Pando/Dictys 输出明显不同；运行前应报告输入边数、相关过滤后边数和最终基因集。

### 3. 核心耦合 ODE

对基因 $g$、细胞状态 $n$，RegVelo 使用：

$$
\frac{du_g}{dt}=\alpha_g(\mathbf s)-\beta_g u_g,
$$

$$
\frac{ds_g}{dt}=\beta_g u_g-\gamma_g s_g.
$$

与基因独立模型的关键区别是转录率

$$
\boldsymbol\alpha(\mathbf s)=\operatorname{softplus}(W\mathbf s+\mathbf b),
$$

当前源码还把结果 clamp 到 0–50。`velocity_encoder.fc1.weight` 就是 $W$：行表示 target，列表示 regulator；`fc1.bias` 是 $b$。一个 regulator 的表达变化可通过同一列权重同时改变多个 target 的转录率，因而各基因 ODE 被 GRN 耦合。

小例子：若 target A 只受 TF1 和 TF2 调控，权重分别为 1.2 和 -0.7，表达为 0.8 和 0.5，bias 为 -0.3，则未约束转录输入为 $1.2\times0.8-0.7\times0.5-0.3=0.31$，转录率为 `softplus(0.31)`，而不是一个固定 $\alpha_A$。正负权重分别可表示激活与抑制，但其因果符号仍由模型和先验可识别性限制。

代码另提供 sigmoid/OR 激活路径；论文和默认配置主要对应 softplus，不能把所有实验都解释成布尔逻辑网络。

### 4. VAE 如何为每个 cell–gene 给时间

`VELOVAE.inference()` 把 spliced 和 unspliced 拼接，编码为

$$
q_\phi(\mathbf z_n\mid \mathbf u_n,\mathbf s_n)
=\mathcal N(\boldsymbol\mu_n,\operatorname{diag}\boldsymbol\sigma_n^2).
$$

默认 latent dimension 为 10。decoder 将 $z_n$ 映射为每个 target gene 的 $\rho_{ng}\in[0,1]$，再定义

$$
t_{ng}=t_{max}\rho_{ng},\qquad t_{max}=20.
$$

因此模型首先得到 cell–gene time matrix，而不是每个细胞唯一的时间。下游全局排序可对 gene times 汇总，或在论文评估中用 gene-time correlation graph 再做 DPT。这里的 0–20 是模型尺度，不是小时或发育天数。

### 5. 数值积分和观测分布

给定 $t_{ng}$、$W,b,\beta,\gamma$，模型从默认 $u=s=0,t_0=0$ 积分 ODE，得到 $\bar u_{ng},\bar s_{ng}$。当前实现使用 torchode 的 Dopri5 step method 与 `AutoDiffAdjoint`，但 controller 是 `FixedStepController()`，初始步长 `dt0=1`；源码中的 adaptive `IntegralController(atol, rtol)` 被注释掉。因此“Dopri5”不意味着当前训练具有自适应误差控制，数值精度受固定步长和 $t_{max}$ 影响。

预测读数以 Normal likelihood 建模：

$$
u_{ng}\sim\mathcal N(\bar u_{ng},\sigma_{u,g}),\qquad
s_{ng}\sim\mathcal N(\bar s_{ng},\sigma_{s,g}).
$$

代码 `scale_unconstr_targets` 有三列，但当前 induction likelihood 只使用第 0 列；模型也明确“only consider induction phase”。因此不应把它描述成完整复现 scVelo 的 induction/repression switching 模型。

### 6. 训练目标到底约束了什么

基础目标是 reconstruction negative log likelihood 加 latent KL：

$$
\mathcal L_{local}=\mathcal L_{rec,u}+\mathcal L_{rec,s}
+\lambda_{KL}D_{KL}(q_\phi(z)\|\mathcal N(0,I)).
$$

此外源码叠加多项正则：

1. **转录滞后相关约束**：将按 gene time 排序的预测 $\alpha(t)$ 与稍后位置的 observed unspliced 做 Pearson correlation loss，默认权重 `alpha_constraint=0.1`。
2. **velocity constraint**：若启用，对 $du=\alpha-\beta u$ 加 `100 * norm(du)`；100 倍乘子是源码实现细节，论文公式不足以单独给出它的迁移性。
3. **soft prior penalty**：
   $$\lambda_1\|W\odot(1-G)\|_2,$$
   惩罚先验 skeleton 外的边，但允许学习新边。
4. **Jacobian sparsity**：对状态平均处的 transcription Jacobian 加 $\lambda_2 L_1$。默认 `lam2=0`，只有显式设置才生效。
5. **bias constraint**：`norm(b + 10)` 把基线 bias 推向 -10。

最终损失是这些项之和。它不是纯 ELBO；超参数和 undocumented multipliers 可能明显改变 GRN 与 velocity 的折中。

### 7. 软约束与硬约束不是一回事

先验 skeleton 记为 $G$：

- **hard constraint (`soft_constraint=False`)**：在反向传播 hook 中用 mask 乘梯度，先验外边不能更新。
- **soft constraint（默认）**：regulator 列可学习，先验外边由 $\lambda_1$ 惩罚；若给 regulator list，非 regulator 列仍被梯度 mask。默认还删除自调控自由度。

虽然 $W$ 初始化为全零，但 hard mask 只屏蔽梯度，并没有把先验边初始化成非零；模型仍需从数据学习先验允许边的权重。soft 模式的结果也不是“先验 GRN 权重微调”，因为 skeleton 是二值结构而且 $W$ 从零起步。

### 8. RNA velocity 和 cell-specific GRN

预测 spliced velocity 为

$$
v_{ng}=\beta_g\bar u_{ng}-\gamma_g\bar s_{ng}.
$$

它写入 AnnData 后交给 scVelo/CellRank 建立 cell–cell transitions。RegVelo 本身学习 gene-space vector field；论文中的终末状态、fate probability、TSI/CBC 等很多结果还依赖 CellRank 参数与 connectivity kernel，并非 `REGVELOVI` 单独输出。

因为 softplus 非线性，固定 $W$ 不等于所有细胞共享相同有效调控强度。局部 Jacobian 为

$$
J(\mathbf s)=\operatorname{diag}(\operatorname{sigmoid}(W\mathbf s+b))W,
$$

代码可计算平均或逐细胞 Jacobian，把 $W$ 转成状态依赖的有效 GRN。但这仍是模型导数，不是单细胞直接测得的 TF binding。

### 9. in silico TF perturbation 实际做了什么

`in_silico_block_simulation()` 加载训练模型，定位指定 TF 对应的 $W$ 列，只把绝对权重大于默认 cutoff $10^{-3}$ 的出边改成 `effects`（默认 0），然后重新生成 velocity/latent-time 输出：

$$
W^*_{g,TF}=0\quad\text{for selected active edges}.
$$

它没有把 TF 的表达置零，没有删除 TF 节点，没有清除 target bias，也没有重新训练其余参数。因此最准确的名称是 **regulon-edge block**，不是完整 knockout。之后论文流程把原始与扰动 velocity 分别交给 CellRank，比较 fate probabilities 或 Markov random-walk density；这些差异是模型反事实预测，需要实验验证。

多次随机初始化并平均可评估拟合稳定性，但不覆盖先验 GRN 错误、结构不可识别性或未建模生物机制。

### 10. 论文证据怎样支撑方法主张

- **模拟数据**提供已知 GRN、真实 velocity 和 time，用于区分“能拟合表达”与“能找回网络/方向”。
- **cell cycle/FUCCI 与代谢标记数据**提供近似真实时间和转录率参照，验证 time/velocity，而不只是嵌入图视觉方向。
- **多谱系发育数据**用 CellRank TSI、CBC 和 terminal-state recovery 比较轨迹质量。
- **zebrafish neural crest 与 Perturb-seq**把 TF perturbation 排名同实验扰动效应比较；tfec/elf1 还结合 CRISPR、HCR-FISH、ChIP/CUT&RUN 等证据。

这些结果支持在论文测试体系中的预测价值，但 GRN AUROC、trajectory metrics 与 perturbation correlation 使用不同近似 ground truth，不应合并成一个“机制正确率”。生物验证也只覆盖候选子集，不能证明所有预测边或所有 TF perturbation 都正确。

### 11. 论文机制与源码映射

| 环节 | 直接代码入口 | 对应程度 | 边界 |
|---|---|---|---|
| GRN 调控转录率 | `_module.py:238-267` | Exact | 默认 softplus+clamp |
| coupled splicing ODE | `_module.py:269-315` | Exact | 当前核心仅 induction trajectory |
| VAE 与 gene time | `_module.py:654-775`, `920-968` | Exact | time 是 cell–gene 模型坐标 |
| ODE solver | `_module.py:999-1072` | Partial | Dopri5 + fixed-step controller |
| ELBO/正则 | `_module.py:820-918` | Exact/Partial | 含 100× velocity、alpha correlation、bias 等实现项 |
| soft/hard skeleton | `_module.py:559-582` | Exact | skeleton 经预处理改变，W 从零初始化 |
| prior GRN 过滤 | `preprocessing/_set_prior_grn.py:7-87` | Code-only detail | 默认相关过滤与 0.01 阈值 |
| velocity extraction | `_model.py` / `tools/_set_output.py` | Exact | 下游 fate 仍依赖 CellRank |
| regulon perturbation | `tools/_in_silico_block_simulation.py:6-65` | Exact | 只改已学得 W 出边，不是完整 KO |
| 全论文 benchmark | `regvelo_reproducibility/` | Script-level | 数据、环境和外部工具复杂 |

### 12. 复现与解释边界

- 两个源码快照分别固定在主包 commit `d035e22...` 与复现仓库 commit `5dc3262...`；二者都应记录。
- 先验网络来源、相关过滤、TF/HVG 保留和矩阵转置会直接改变建模基因和边方向。
- 固定步长 ODE 在不同数据尺度、$t_{max}$ 或 stiffness 下需做数值敏感性检查。
- `lam2=0` 时没有 Jacobian L1；不能笼统声称所有默认模型都被 Jacobian 稀疏化。
- velocity、GRN、latent time 可能存在不同参数组合给出相似重构的 identifiability 问题；多次 fit 的一致性是必要诊断。
- fate/driver 结果依赖 CellRank、终末状态定义和 perturbation scoring，不是核心 VAE 的直接读数。
- 仓库的 reproducing scripts 覆盖论文分析，但完整运行还需要外部数据、GRN 工具、GPU/依赖环境；本地存在代码不等于已复算论文结果。

### 建议阅读顺序

先读论文方法示意和核心 ODE，再读模拟 benchmark、cell-cycle time validation、zebrafish perturbation 实验。源码依次看 `preprocessing/_set_prior_grn.py`、`_preprocess_data.py`、`_module.py:velocity_encoder`、`VELOVAE.inference/generative/loss`、`_get_induction_unspliced_spliced()`，最后读 `tools/_in_silico_block_simulation.py` 和复现脚本。

### 证据范围

本文基于本地 Cell 论文 Markdown、主图/图注、直接源码，以及主包 commit `d035e22a4f652ed0f214b95f87ea25d2ee639172` 和复现仓库 commit `5dc3262c3276e2d1cb5a40d6eb8290b8e90d657b` 整理。本次没有重新训练模型、下载全部外部 benchmark 数据或复算论文统计结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## RegVelo Summary

### Paper Metadata

- **Title**: RegVelo: Gene-regulatory-informed dynamics of single cells
- **Authors**: Weixu Wang, Zhiyuan Hu, Philipp Weiler, Sarah Mayes, Marius Lange, Daniel M. Fountain, Julianna O. Haug, Jingye Wang, Zhengyuan Xue, Tatjana Sauka-Spengler, Fabian J. Theis
- **Journal**: Cell, 2026-05-12
- **DOI**: 10.1016/j.cell.2026.04.022
- **Code**: https://github.com/theislab/regvelo | https://github.com/theislab/regvelo_reproducibility

---

### Motivation & Novelty

#### The Problem

Single-cell transcriptomics has produced powerful tools for understanding cell differentiation, but two major methodological traditions have developed independently:

1. **RNA velocity methods** (scVelo, *Nat. Biotechnol.* 2020; veloVI, *Nat. Methods* 2024) model splicing kinetics to reconstruct cell trajectories. But they assume **gene-independent constant transcription rates**, ignoring that transcription is regulated. This makes them mechanistically incomplete — they cannot explain *why* cells move in a given direction.

2. **GRN inference methods** (SCENIC+, *Nat. Methods* 2023; CellOracle, *Nature* 2023; Dictys, *Nat. Methods* 2023) reconstruct regulatory networks from epigenomics and expression data. But they are largely **static**, not modeling how cells move through regulatory states over time.

This disconnect has a practical consequence: neither approach can predict what happens if you knock out a transcription factor. Velocity models have no regulatory structure to perturb; GRN models have no dynamics to propagate the perturbation through.

#### Prior Work Limitations

| Method | RNA Velocity | GRN | Perturbation Simulation | Mechanism |
|---|---|---|---|---|
| scVelo (*Nat. Biotechnol.* 2020) | ✓ | ✗ | ✗ | Constant transcription rates |
| veloVI (*Nat. Methods* 2024) | ✓ | ✗ | ✗ | VAE + constant rates |
| TFvelo (*Nat. Commun.* 2024) | ✓ | ~ | ✗ | TF-regulated velocity, no ODE |
| CellOracle (*Nature* 2023) | ✗ | ✓ | ~ | Shift-based, needs external velocity |
| dynamo (*Cell* 2022) | ✓ | ~ | ~ | Requires metabolic labeling |
| scKINETICS | ✗ | ✓ | ~ | Linear system, no splicing model |

#### RegVelo's Unique Contributions

1. **Coupled ODE system**: First method to simultaneously infer GRN and RNA velocity through a single coupled N_G-dimensional ODE, solved end-to-end with a neural ODE solver.

2. **Actionable in silico perturbation**: Perturbation is implemented by modifying the underlying regulatory circuits (zeroing GRN columns), then propagating through the dynamics — capturing nonlinear long-term consequences rather than first-order immediate shifts.

3. **Prior GRN integration**: Can incorporate prior knowledge from multiomics (SCENIC+, Pando, Dictys) as structural constraints, with soft/hard constraint options.

4. **Early driver detection**: By simulating perturbed dynamics *de novo*, RegVelo identifies TFs expressed at trajectory beginnings that are missed by correlation-based approaches (which require the driver to be expressed in terminal states).

---

### Method Overview

RegVelo is a Bayesian deep generative model that jointly learns:
- A GRN weight matrix W (N_G × N_G) representing TF-target regulatory strengths
- Cell-specific latent time via a variational autoencoder (z → t_ng)
- Kinetic parameters β (splicing rate) and γ (degradation rate) per gene

The core model replaces the independent 1-D ODEs of scVelo with a coupled N_G-dimensional system where transcription rates are non-constant, regulated by upstream TF expression through W.

**Key pipeline**: Raw expression → HVG selection + neighbor smoothing → VAE encoding → gene-specific latent times → ODE integration (torchode dopri5) → RNA velocity → CellRank fate mapping → TF perturbation screening.

See `doc_method.md` for detailed algorithmic description and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets and Metrics

| Dataset | Cells/Genes | Purpose | Key Metric |
|---|---|---|---|
| Simulated 6-gene toggle switch | 1500 time steps | GRN ground truth benchmark | AUROC (GRN), Pearson corr (velocity/time) |
| dyngen simulations (1-9 lineages) | 1000 cells, 800 genes | Scalability + robustness | Velocity corr, latent time corr, AUROC |
| Mouse hematopoietic stem cells (mHSPC) | — | GRN benchmark | AUROC, EPR (early precision rate) |
| Mouse neural crest (Smart-seq2) | — | Robustness to complexity | TSI, CBC |
| FUCCI U2OS + RPE1 cell cycle | — | Ground truth latent time | CBC, velocity consistency, Spearman(latent vs FUCCI) |
| Mouse pancreatic endocrinogenesis | ~3,500 cells | Regulatory perturbation | TSI, driver AUROC |
| Human hematopoiesis | ~5 lineages | Complex dynamics | TSI, CBC (forward + backward), lineage AUROC |
| Human limb myogenesis | — | Model selection demo | CBC, model comparison |
| Human hindbrain development | ~52,914 cells | Large-scale application | TSI, CBC |
| Zebrafish neural crest (Smart-seq3) | 1,180 cells, 8,000 genes | Primary application | TSI, driver AUROC, Spearman vs Perturb-seq |
| Zebrafish Perturb-seq | 7 TF KOs + 11 additional | Experimental validation | Spearman(predicted vs MELD), precision/recall |

#### Key Quantitative Results

- **Cell cycle (U2OS)**: CBC = 0.864, velocity consistency = 0.873, Spearman(latent time vs FUCCI) = 0.683; GRN AUROC = 0.59 (ranks 1st among 6 methods)
- **Hematopoiesis TSI**: 0.95 — only method to recover all 5 terminal states; veloVI gets ~0.7, scVelo ~0.6 (one-sided Welch's t-test vs veloVI: p=1.59×10⁻⁵; vs scVelo: p=2.23×10⁻⁵)
- **Zebrafish driver prediction**: AUROC = 0.91 ± 0.02 (vs. correlation baseline AUROC = 0.65 with fixed weights)
- **Perturb-seq validation**: Mean Spearman = 0.52 for single-TF KOs (competitors < 0.25); precision = recall = 0.6 (competitors ≈ 0.3)
- **Pancreatic endocrinogenesis**: Predicted GATA1/SPI1 toggle switch, known epsilon cell drivers with AUROC = 0.95

#### Biological Discoveries

- **tfec** identified as early pigment lineage driver in zebrafish neural crest, upstream of mitfa; validated by CRISPR-Cas9 knockout showing reduced slc45a2⁺ cells (p=0.001); Sox10 ChIP-seq confirms Sox10 binding in tfec promoter region
- **elf1** discovered as novel pro-pigment ETS-family TF (anti-mesenchymal), validated by Perturb-seq, HCR-FISH, and elf1 CUT&RUN identifying direct binding sites at glulb, cpeb4b, pleca loci

---

### Reproducibility

**Rating: 4/5**

#### Strengths

- **Full code package** available (BSD-3-Clause license) at https://github.com/theislab/regvelo with pip installability
- **Comprehensive reproducibility repo** at https://github.com/theislab/regvelo_reproducibility with numbered pipeline scripts for every dataset
- **Data availability**: Zebrafish SmartSeq3 data at GEO:GSE256009, Perturb-seq at GEO:GSE256008, Sox10 ChIP-seq + Elf1 CUT&RUN at GEO:GSE303928; all other datasets accessible via figshare collection
- **ModelComparison class** enables systematic model selection for new datasets
- **Pre-packaged example datasets** in the regvelo package itself

#### Limitations / Practical Notes

- **Dependency complexity**: Requires scvi-tools, torchode, CellRank 2, and numerous benchmark dependencies. The reproducibility repo requires zarr, dask, torchsde — a complex environment.
- **Computational cost**: ODE integration is expensive. The FixedStepController (dt0=1, t_max=20) makes training tractable but less accurate. Large datasets (8000 genes zebrafish) require significant GPU memory.
- **Prior GRN quality matters**: AUROC drops from 0.91 to 0.65 when prior edge weights are fixed (SCENIC+). The model's strength depends on having a decent prior GRN from multiomics data.
- **GRN uncertainty requires multiple runs**: Bootstrap-based uncertainty (multiple model fits) is computationally expensive; this is noted as a limitation in the paper.
- **Hyperparameter sensitivity**: λ1 < 1 is recommended; λ2 = 0 default; soft_constraint=True default. ModelComparison helps but still requires side information about the system.
- **Common pitfall**: The correlation filter in `set_prior_grn` (threshold 0.01) can discard many prior edges if expression data is noisy. Users should check how many edges survive filtering.

#### Environment Setup

```bash
pip install regvelo  # main package
# For reproducibility:
cd regvelo_reproducibility && pip install -e .
# Dependencies: scvi-tools 1.0-1.2.1, torchode ≥0.1.6, cellrank ≥2.0, torch <2.6.0
```

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
