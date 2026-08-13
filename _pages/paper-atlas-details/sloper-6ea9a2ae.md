---
layout: default
permalink: /paper-atlas/sloper-6ea9a2ae/
title: "SLOPER"
nav: false
description: "SLOPER（Score-based Learning Of Poisson-modeled Expression Rates）处理的不是普通的空间聚类问题。它先为每个基因学习一个二维向量场：在组织内任一点，这个向量指出该基因的相对表达强度朝哪个方向上升、上升有多快。这个向量场随后既可作为空间模式本身，也可驱动 Langevin 采样，把稀疏、扩散的观测计数重排成空间上更集中的“增强表达”。"
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
      <span>Spatially Variable Genes</span>
      <span>bioRxiv · 2025</span>
    </div>
    <h1>SLOPER</h1>
    <p>Mapping spatial gradients in spatial transcriptomics data with score matching</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1101/2025.11.24.690257" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SLOPER">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/chitra-lab/SLOPER" target="_blank" rel="noopener noreferrer" aria-label="Open code for SLOPER">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SLOPER 方法解读：不先平滑表达量，而是直接学习“往哪里升高”

SLOPER（Score-based Learning Of Poisson-modeled Expression Rates）处理的不是普通的空间聚类问题。它先为每个基因学习一个二维向量场：在组织内任一点，这个向量指出该基因的相对表达强度朝哪个方向上升、上升有多快。这个向量场随后既可作为空间模式本身，也可驱动 Langevin 采样，把稀疏、扩散的观测计数重排成空间上更集中的“增强表达”。

本文还是 2025 年 bioRxiv 预印本；因此下面把论文提出的完整分析框架与该代码快照实际提供的函数分开说明。

### 1. 输入、输出与真正学习的对象

输入可以是单分子分辨率的转录本坐标，也可以是细胞/spot 级的计数矩阵和二维坐标。对基因 $g$，论文把组织区域记为 $T$，把生物学上的归一化空间强度记为 $\phi_g(\mathbf{s})$。SLOPER 的核心输出不是 $\phi_g$ 本身，而是

$$
\mathbf{f}_{\theta_g}(\mathbf{s})\approx \nabla_{\mathbf{s}}\log\phi_g(\mathbf{s}).
$$

从左到右读：先对空间强度取对数，再对二维位置求梯度。向量方向表示表达相对增高最快的方向，长度表示局部对数强度变化率。例如某点的梯度是 $(0.6,0.8)$，沿该单位方向移动 $0.1$ 个归一化坐标单位时，$\log\phi_g$ 的一阶变化约为 $0.1$，强度约乘以 $e^{0.1}\approx1.105$。它描述的是局部相对变化，不等同于该点的原始计数。

### 2. 为什么从 Poisson 点过程开始

对一个基因，SLOPER 用非齐次 Poisson 点过程描述转录本位置。任一区域 $R\subseteq T$ 的转录本数满足

$$
N(R)\sim\operatorname{Poisson}\left(\int_R\lambda(\mathbf{s})\,d\mathbf{s}\right).
$$

观测强度被分解为

$$
\lambda(\mathbf{s})=u(\mathbf{s})\phi(\mathbf{s}),
$$

其中 $u$ 表示文库大小、捕获效率或细胞体积等技术因素，$\phi$ 表示希望保留的生物空间变化。给定某基因的转录本总数后，位置服从与 $\lambda$ 成比例的密度；目标则是去除 $u$ 后学习 $\nabla\log\phi$。

这种建模比“先拟合一张平滑表达曲面再求导”更直接。score matching 只需要学习密度对数的梯度，归一化常数会在求导时消失，因此无需计算 $\int_T\phi$。

### 3. 从 score matching 到有边界的截断目标

经典 score matching 的隐式目标包含向量场范数和散度：

$$
\|\mathbf f_\theta(\mathbf{s})\|^2+2\,\operatorname{div}\mathbf f_\theta(\mathbf{s}).
$$

组织不是无限平面，而是有不规则边界的有限区域。直接套用经典分部积分会留下边界项。论文采用 truncated score matching，引入到组织边界的距离

$$
g_0(\mathbf{s})=\min_{\mathbf z\in\partial T}\operatorname{dist}(\mathbf{s},\mathbf z),
$$

并对每个位置使用

$$
h_\theta(\mathbf{s})=
g_0\|\mathbf f_\theta\|^2
+2g_0\operatorname{div}\mathbf f_\theta
+2\langle\nabla g_0,\mathbf f_\theta\rangle.
$$

第一项约束向量大小，第二项通过散度连接到未知真实 score，第三项校正边界距离的空间变化。靠近边界时 $g_0$ 变小，避免把组织外没有观测的区域错误解释成强烈的生物梯度。

代码中的 `boundary_distances_and_gradients_torch()` 先用坐标的 concave hull 近似组织边界，再计算每个 spot 到最近边界点的距离和指向组织内部的单位向量。`_divergence()` 用 PyTorch 自动微分逐维求散度；`riemann_truncsm_loss()` 逐项实现上式。

### 4. 聚合计数中的重要性加权：论文与当前代码的关键差异

论文指出训练位置来自观测分布 $p_\lambda$，而目标期望属于 $p_\phi$。由于 $\lambda=u\phi$，importance reweighting 给每个转录本赋予与 $1/u(\mathbf{s})$ 成比例的权重。对区域 $C_k$ 中计数 $a_k$ 的聚合数据，论文的经验目标权重因此为 $a_k/u_k$：高计数增加该 spot 的贡献，较大技术因子降低贡献。

但当前核心代码 `prepare_weights()` 只读取基因的 `adata.X`，把每个值下限裁剪到 `1e-3`，再除以总和；它既不接收也不计算 $u_k$。所以：

- 若调用者预先把 `adata.X` 变成了与 $a_k/u_k$ 成比例的数值，代码归一化后可实现论文权重；
- 若直接传入原始计数，实际权重只是裁剪后的 $a_k/\sum_j a_j$，技术因子校正没有在该函数内发生；
- 零计数也会因 `a_min=1e-3` 获得极小正权重，这是实现选择，不是论文公式本身。

这是复现时最需要显式检查的数据合同，不能只凭函数名假定已做文库归一化。

### 5. 网络与训练

论文为每个基因单独训练带两个残差块和 Fourier 位置编码的神经网络。当前 `ScoreNet` 输出二维 score；默认 `hidden_dim=128`、`depth=3`，即输入层后有两个 `ResBlock`，但 `use_fourier=False`，复现论文设置时必须显式开启 Fourier features。代码还提供论文未重点描述的 `LogLambdaNet`：它输出标量势函数，loss 再对输入求梯度，天然得到保守场。

`train()` 默认用 Adam、学习率 $10^{-3}$、500 个 epoch，并用 StepLR 在每 200 个 epoch 将学习率乘 0.1。训练可全批量或小批量。当前 loss 还含可选的 KNN gate、curl penalty 和额外正则查询点；这些是代码扩展，不能反向当作论文主方法的必要组成。

每基因一个模型让不同基因能拥有完全不同的梯度方向，这是相对一维共同轴模型的核心优势；代价是训练成本随基因数近似线性增长，且随机初始化与超参数会影响结果。

### 6. 用梯度生成增强表达

学到 score 后，论文从多个随机初始位置运行退火 Langevin 动力学：

$$
\mathbf{s}^{(t+1)}=
\mathbf{s}^{(t)}+
\frac{\epsilon^2}{2}\mathbf f_\theta(\mathbf{s}^{(t)})+
\epsilon\sigma_t\mathbf z_t,
\qquad \sigma_t=\alpha^t.
$$

漂移项沿表达概率升高方向移动粒子；噪声项早期帮助探索，随后随 $\alpha^t$ 衰减。直观例子：若 $\epsilon=0.1$、score 为 $(2,0)$，无噪声的一步漂移是 $0.5\times0.1^2\times(2,0)=(0.01,0)$。

`sample_ld_in_polygon_sdf()` 直接实现这一步进。代码先把组织多边形栅格化为 signed distance field；`SDFProjector.project()` 把越界粒子用近似 Newton 步推回边界内。采样结束后，`counts_from_samples_nearest()` 把粒子分配给最近 spot，得到增强计数。这里代码采用“最近 spot”而不是论文文字中的一般区域包含关系，是针对 spot 数据的具体实现。

增强表达不是去噪后的连续强度估计，而是由学习到的 score 驱动、重新采样并分箱得到的随机计数表示。粒子数、步数、$\epsilon$、$\alpha$ 和边界离散精度都会影响结果。

### 7. 三类下游任务

#### 7.1 空间域

论文对增强计数矩阵做每细胞 UMI 归一化、对数变换和 k-means。DLPFC 中，作者报告 SLOPER 的域划分优于所比较方法，并用人工皮层层次验证；增强表达在层特异基因 AUROC 上优于原表达，PCP4 的空间模式也更集中。核心库提供增强计数生成，但完整域分析主要出现在 `demo.ipynb`，不是一个封装好的库函数。

#### 7.2 基因模块

论文在各 spot 上比较两个基因梯度的余弦相似度，再取空间平均形成基因—基因相似矩阵，最后谱聚类。鼠睾丸 Slide-seq 数据包含 39,206 个细胞、23,705 个基因，作者用 geneCover 选 500 个基因；SLOPER 模块与已知精子发生阶段 marker 的 ARI 为 0.32，比较方法低于 0.26。当前核心 `SLOPER.py` 没有谱聚类与模块分数的完整实现。

#### 7.3 isodepth

论文用模块内梯度的 outer product 构建 GOP 矩阵，再由方向导数和 forward Euler 恢复一维 isodepth。DLPFC 中报告的 SLOPER isodepth 与 GASTON 参考的 Spearman 相关为 0.92，而 GraphST 各嵌入分量平均为 0.09。当前核心库没有 GOP 到 isodepth 的完整实现；这部分应视为论文算法，而不是已验证的公开 API。

### 8. 如何读主图证据

- 图 1 从左到右展示输入、每基因 IPPP/score 网络、再到增强表达、空间域、模块和 isodepth；它是方法结构图，不是性能证据。
- 图 2 的模拟比较直接学习梯度与先估强度再求导的 KIE。表中最不稀疏条件 KIE 略高（0.72 对 0.67），其余稀疏条件 SLOPER 更高；因此合理结论是稀疏条件下优势更明显，而不是所有设置都胜出。
- 图 3 展示 DLPFC 域、人工层次、增强表达 AUROC 和 PCP4；它支持增强后空间特异性，但仍是单一组织类型中的结果。
- 图 4 的 0.92 相关是与 GASTON isodepth 的一致性，不是独立实验真值。
- 图 5 展示鼠睾丸重复小管结构和发育阶段模块。IRIS 使用外部单细胞参考，且该数据没有真实域标签，所以与 IRIS 的视觉相似不能写成“域准确率”。

### 9. 论文—代码对应与复现边界

| 组件 | 状态 | 直接证据与解释 |
|---|---|---|
| 不规则组织边界、$g_0$ 与 $\nabla g_0$ | Exact | `SLOPER/SLOPER.py:67-143` 构造 concave hull 并求最近边界 |
| 截断 score-matching 三项损失 | Exact | `SLOPER/SLOPER.py:391-520` 与论文目标逐项对应 |
| 每基因二维 ScoreNet | Exact/Config | `SLOPER/SLOPER.py:225-254`；残差深度匹配，但 Fourier 默认关闭 |
| 聚合计数的 $a_k/u_k$ | Partial | `SLOPER/SLOPER.py:39-64` 只归一化传入表达，未显式使用 $u_k$ |
| Adam 与学习率调度 | Exact | `SLOPER/SLOPER.py:526-632` |
| 退火 Langevin 更新与边界投影 | Exact/Implementation | `SLOPER/SLOPER.py:781-1066`；SDF 投影是具体工程实现 |
| 粒子转增强 spot 计数 | Partial | `SLOPER/SLOPER.py:1068-1118` 用最近 spot 分箱 |
| 空间域完整流程 | Notebook | 核心库只提供前置表示，演示 notebook 承担分析编排 |
| 梯度余弦模块与模块分数 | Not found | 核心库未见完整谱聚类流水线 |
| GOP/forward Euler isodepth | Not found | 核心库未见完整实现 |

复现时建议先固定坐标标准化、`adata.X` 是否已除以文库因子、Fourier 开关和随机种子，再分别检查训练 loss、边界内采样率与增强计数总数。结果解释应区分“学到局部相对梯度”“由梯度产生增强计数”和“对增强表示进行下游聚类”这三个层级。

### 10. 最简心智模型

把每个基因的观测想成组织上的稀疏雨点。SLOPER 不先画一张平滑的雨量地图，而是直接学习每个位置“雨点密度往哪边增加”。边界距离让模型知道组织到哪里结束，importance weight 负责区分技术曝光量与生物强度。学到的箭头场再推动一群带噪声的粒子，最终把粒子落点数回 spot，形成更集中的增强表达。论文进一步用箭头之间的方向关系找基因模块、用箭头的共同几何方向恢复 isodepth；但这两条下游路线在当前核心代码快照中没有完整封装。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SLOPER: Score-based Learning Of Poisson-modeled Expression Rates

**Paper**: Mapping spatial gradients in spatial transcriptomics data with score matching
**Authors**: An Wang, Donald Geman, Uthsav Chitra*, Laurent Younes* (Johns Hopkins University)
**Journal**: bioRxiv preprint (2025)
**DOI**: 10.1101/2025.11.24.690257
**Code**: https://github.com/chitra-lab/SLOPER

---

### Motivation & Novelty

#### Biological Problem

Spatial transcriptomics (ST) technologies measure gene expression at thousands of locations in a 2D tissue slice. A central challenge is characterizing *spatial variation* in gene expression — not just which genes are expressed where, but in which direction and at what rate expression changes. This is captured by **spatial gradients**: vector fields where each vector indicates the direction and magnitude of increasing expression for a given gene.

Spatial gradients are biologically important because:
- Tissue domains are marked by genes with large gradients at domain boundaries
- Continuous variation (e.g., along the crypt-villus axis of intestinal glands) is captured by smoothly varying gradients
- Gene modules — co-regulated gene groups — share similar gradient directions

#### Limitations of Existing Methods

| Method | Limitation | Journal/Year |
|--------|-----------|--------------|
| GASTON (Chitra et al.) | Assumes all genes share the same gradient direction (1-D isodepth) | Nature Methods 2025 |
| GASTON-Mix (Chitra et al.) | Same 1-D assumption, extended to mixture model | Bioinformatics 2025 |
| BELayer (Ma et al.) | Requires prior knowledge of tissue geometry | Cell Systems 2022 |
| StarTrail (Chen et al.) | Gaussian process — computationally expensive; doesn't model discrete counts | bioRxiv 2024 |
| KIE (Diggle 1985) | Computes gradient analytically from smoothed intensity — loses spatial precision | JRSS-C 1985 |
| GraphST (Long et al.) | Domain identification only; no gradient learning | Nature Communications 2023 |
| Hotspot (DeTomaso & Yosef) | Gene module identification from expression, not gradients — spatially diffuse | Cell Systems 2021 |

#### Unique Contributions

1. **Per-gene gradient learning**: SLOPER learns a separate spatial gradient vector field $\nabla \log \phi_g$ for each gene, without assuming all genes share the same direction
2. **IPPP model**: Principled probabilistic model of discrete transcript locations/counts via inhomogeneous Poisson point process
3. **Truncated score matching**: Correctly handles bounded tissue domains (standard score matching fails on bounded domains)
4. **Annealed Langevin enhancement**: Novel use of diffusion-based sampling to "denoise" sparse gene expression, producing sharper and more spatially coherent expression profiles
5. **Gradient-based gene modules**: Gene similarity defined by gradient direction alignment (cosine similarity), not expression correlation — more spatially precise

---

### Method Overview

SLOPER is a deep learning framework with two main components:

#### 1. Score Matching for Gradient Estimation

For each gene $g$, SLOPER trains a neural network $f_{\theta_g}: \mathbb{R}^2 \to \mathbb{R}^2$ to approximate the spatial gradient $\nabla \log \phi_g$ using **truncated score matching** (TSM). The TSM loss is:

$$\mathcal{L}_{\mathrm{TSM}}(\theta) = \sum_{k=1}^K \frac{a_k}{u_k}\left[g_0(\mathbf{c}_k)\|f_\theta(\mathbf{c}_k)\|^2 + 2g_0(\mathbf{c}_k)\,\mathrm{div}(f_\theta(\mathbf{c}_k)) + 2\langle \nabla g_0(\mathbf{c}_k), f_\theta(\mathbf{c}_k)\rangle\right]$$

where $g_0(\mathbf{c}_k)$ is the distance from spot $k$ to the tissue boundary, $a_k$ is the transcript count, and $u_k$ is the library size.

**Architecture**: ScoreNet with 2 residual blocks, Fourier feature positional encoding, hidden dim 128. Trained with Adam + StepLR for 500 epochs per gene.

#### 2. Annealed Langevin Dynamics for Expression Enhancement

Given the learned score, SLOPER generates enhanced transcript locations by running annealed Langevin dynamics:

$$\mathbf{s}^{(t+1)} = \mathbf{s}^{(t)} + \frac{\varepsilon^2}{2} f_{\theta^*}(\mathbf{s}^{(t)}) + \varepsilon \sigma_t z^{(t)}, \quad \sigma_t = \alpha^t$$

Particles start from random positions and are pushed toward high-expression regions. The annealing ($\alpha < 1$) concentrates particles in high-probability regions, producing sharper expression profiles. Enhanced counts are obtained by binning final particle positions to nearest spots.

#### Downstream Applications

- **Spatial domains**: k-means on Langevin-enhanced expression matrix (after scanpy normalization)
- **Gene modules**: Spectral clustering on gradient cosine similarity matrix $\rho(g,g')$
- **Isodepth**: 1-D spatial axis from gradient outer product (GOP) matrix + forward Euler integration

See `doc_method.md` for full mathematical details and `doc_code.md` for implementation specifics.

---

### Evaluation

#### Datasets

| Dataset | Technology | Genes | Spots/Cells | Ground Truth |
|---------|-----------|-------|-------------|--------------|
| Human DLPFC (Maynard et al., Nature Neuroscience 2021) | 10x Genomics Visium | 33,538 (500 selected) | 3,639 | 6 cortical layers + WM (manual annotation) |
| Mouse testis (Chen et al., Cell Reports 2021) | Slide-SeqV2 | 23,705 (500 selected) | 39,206 | Spermatogenesis stage markers (Johnston et al., PNAS 2008) |
| Simulated IPPP | — | 1 | 10,000 | Ground-truth intensity function (3 Gaussian ridges) |

Gene selection: geneCover (Wang et al., RECOMB 2025) — label-free marker selection.

#### Metrics

- **Spatial domain accuracy**: Normalized Mutual Information (NMI) vs. manual annotations
- **Gene expression enhancement**: AUROC for domain-specific gene identification
- **Gradient estimation**: Average cosine similarity with ground-truth gradient (simulation)
- **Gene module accuracy**: Adjusted Rand Index (ARI) vs. spermatogenesis stage markers
- **Isodepth accuracy**: Spearman correlation with GASTON isodepth

#### Key Results

**Simulation (Fig 2)**:
- SLOPER achieves higher cosine similarity with ground-truth gradient than KIE across all sparsity levels
- SLOPER gradient field is more spatially coherent than KIE-estimated gradient

**DLPFC (Fig 3)**:
- SLOPER NMI > GraphST, KIE, Leiden, k-means for spatial domain identification
- SLOPER uniquely identifies Layer 2 (other methods fail to resolve it)
- Langevin-enhanced expression achieves higher AUROC than original expression for Layers 1-6
- PCP4 (Layer 5 marker): enhanced expression sharply localizes to Layer 5 vs. diffuse original

**DLPFC Isodepth (Fig 4)**:
- SLOPER isodepth: Spearman ρ = 0.92 with GASTON isodepth
- GraphST embeddings: mean Spearman ρ = 0.09 (not spatially coherent)

**Mouse testis (Fig 5)**:
- SLOPER gene modules: ARI = 0.32 vs. spermatogenesis markers; all other methods ARI < 0.26
- SLOPER identifies two elongated spermatid populations (domains 2 and 4) not found by IRIS (which uses an external reference)
- SLOPER modules 3, 9, 10 → pachytene spermatocytes (Stage XIII-XIV); module 5 → round spermatids (Stage VI); module 1 → round-to-elongated transition (Stage VIII); module 4 → early elongated spermatids
- Zoom-in of single tubule: modules 6→1→2 show outward-to-inward maturation progression

---

### Reproducibility

**Rating: 3/5**

**Justification**: The core score matching and Langevin dynamics are fully implemented and well-documented. However, three key analyses from the paper (isodepth inference, gene module spectral clustering, domain identification pipeline) are not in the library — only the demo notebook covers part of the pipeline. The paper's main quantitative results (NMI, ARI, Spearman ρ) cannot be fully reproduced from the released code alone.

#### Environment Setup

```bash
# Dependencies (no requirements.txt — install manually)
pip install torch==2.5.1+cu124 --index-url https://download.pytorch.org/whl/cu124
pip install scanpy==1.11.1 shapely==2.1.1 scikit-learn==1.5.2 scipy==1.15.2 numpy==2.1.0 matplotlib==3.10.1

# Data: DLPFC sample 151673 included in repo (data/151673/)
# Run demo: jupyter notebook demo.ipynb
```

#### Strengths

- Clean, modular PyTorch implementation
- GPU-accelerated Langevin sampling with SDF boundary projection
- Dual model modes (score network vs. potential network) for flexibility
- Optional regularizers (KNNGate, curl penalty) for sparse genes
- DLPFC data included in repo for immediate testing

#### Weaknesses

- **Missing implementations**: Isodepth (Section 2.4.3), gene module clustering (Section 2.4.2), and domain identification pipeline (Section 2.4.1) are not in the library
- **Per-gene training**: Training a separate model per gene is computationally expensive for large gene sets (G=500 genes × 500 epochs each)
- **No requirements.txt**: Dependency versions documented only in README
- **Hyperparameter sensitivity**: Key parameters (ε, α, H, network architecture) are not systematically documented; supplement referenced but not included in repo
- **Boundary computation**: O(N²) concave hull computation may be slow for large datasets (Slide-seq: 39,206 cells)

#### Common Pitfalls

1. Forgetting to enable `use_fourier=True` in ScoreNet (paper uses Fourier features; default is False)
2. Not normalizing coordinates before training (critical for stable gradients)
3. Using `LogLambdaNet` (potential mode) vs. `ScoreNet` (score mode) — paper describes score mode only
4. Boundary computation with `visualize=True` (default) will display plots during preprocessing — set `visualize=False` for batch processing
5. Langevin sampling requires the tissue polygon (hull) from boundary computation — must be passed to `build_sdf_projector`

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
