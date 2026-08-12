---
layout: default
permalink: /paper-atlas/deepspatial-5882bdcf/
title: "DeepSpatial"
nav: false
description: "DeepSpatial 不是把相邻切片逐像素“补帧”，也不是把二维切片简单堆成 2.5D。它先用非平衡最优传输（UOT）在相邻切片之间建立软细胞对应，再训练一个 Gene Diffusion Transformer（GiT）学习细胞状态随深度连续变化的速度场，最后从上下两张真实切片出发求解 ODE，在任意中间深度生成带三维坐标、表达向量和细胞类型的虚拟细胞。 本工作区核对的是 bioRxiv 论文 10.1101/2026.04.28."
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
      <span>Integration &amp; Multi-modal</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>DeepSpatial</h1>
    <p>Reconstructing True 3D Spatial Omics at Single-Cell Resolution</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2026.04.28.721395" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DeepSpatial：怎样把稀疏二维切片生成连续三维空间组学体积

### 一句话理解

DeepSpatial 不是把相邻切片逐像素“补帧”，也不是把二维切片简单堆成 2.5D。它先用非平衡最优传输（UOT）在相邻切片之间建立软细胞对应，再训练一个 Gene Diffusion Transformer（GiT）学习细胞状态随深度连续变化的速度场，最后从上下两张真实切片出发求解 ODE，在任意中间深度生成带三维坐标、表达向量和细胞类型的虚拟细胞。

本工作区核对的是 bioRxiv 论文 `10.1101/2026.04.28.721395` 与官方仓库 `yyh030806/DeepSpatial` 的固定源码快照 `fdb98657fca95679cc45adf3510a161de05bca08`。论文 Methods 位于 `paper.md:855-950`；核心代码位于 `deepspatial/data_utils/uot_solver.py`、`deepspatial/models/git.py`、`deepspatial/module.py` 和 `deepspatial/core.py`。

### 1. 它解决的任务是什么

输入是一组已经配准、具有真实 z 坐标的二维空间组学切片。每个细胞有三部分状态：

$$
s_i=(\mathbf{x}_i,\mathbf{g}_i,c_i),
$$

其中 $\mathbf{x}_i\in\mathbb{R}^2$ 是平面坐标，$\mathbf{g}_i\in\mathbb{R}^D$ 是基因或蛋白表达，$c_i$ 是细胞类型。输出不是一张固定中间切片，而是相邻物理切片 $S_0,S_1$ 之间的连续体积；每个新细胞都应得到 $(x,y,z)$、表达向量和类别。

代码 API 体现了这一路径：`DeepSpatial.setup_data()` 读取 AnnData 切片并归一化坐标；`build_model()` 构造 GiT 和流匹配模块；`fit()` 训练；重建函数把相邻切片间生成的细胞组合为新的 AnnData。这里的“true 3D”指连续深度上的细胞级生成，而不是实验直接测得完整三维体积；生成区域仍由输入切片、配准质量和模型假设约束。

### 2. 第一步：统一坐标尺度

论文要求先把切片配准到公共坐标系，再对全体切片的 x、y、z 分别做全局 min-max 归一化。代码 `core.py:48-87` 直接实现这一过程，并保存最小值与范围，生成后再逆变换回物理尺度。这一步很重要：流匹配在无量纲的 $[0,1]$ 区间学习，避免微米尺度、切片间距和表达量尺度混在同一个数值问题里。

DeepSpatial 本身并不替用户完成所有生物配准。论文对无公共坐标的样本建议先用 PASTE 等方法；因此切片错位会直接进入后续 UOT 和速度场，而不会被神经网络自动证明为正确。

### 3. 第二步：用 UOT 建立相邻切片的软细胞对应

流匹配需要知道哪些起点与终点应组成训练对，但相邻切片没有天然的一一细胞对应。DeepSpatial 为每对细胞定义联合代价：

$$
C_{ij}=\alpha_{\mathrm{spatial}}D^{\mathrm{spat}}_{ij}
+(1-\alpha_{\mathrm{spatial}})D^{\mathrm{gene}}_{ij}
+\lambda_{\mathrm{penalty}}P^{\mathrm{cell}}_{ij}.
$$

空间项是归一化欧氏距离，表达项是归一化余弦距离；若细胞类型不同，$P^{\mathrm{cell}}_{ij}=1$。`uot_solver.py:35-57` 与该式直接对应，但代码把类别惩罚固定为 `10.0`，没有暴露为公共 API 参数。由于前两项都被归一到大致 $[0,1]$，这个惩罚近似把跨类型匹配变成强约束。

接着求熵正则的非平衡 Sinkhorn 耦合 $\pi^*$。与平衡 OT 不同，UOT 允许两侧边缘质量不完全守恒，因此更适合细胞密度变化、组织边界差异以及论文所述的增殖或凋亡情景。代码 `uot_solver.py:101-118` 使用 POT 的 `sinkhorn_unbalanced`，默认熵正则 `0.8`、边缘松弛 `0.05`、最多 100 次迭代、停止阈值 `1e-3`。

需要准确理解 $\pi^*$：它是由坐标、表达和已有标签共同定义的软训练配对，不是实验追踪得到的真实细胞谱系，也不能单独解释为因果迁移路径。

### 4. 第三步：把细胞状态变成 GiT token

GiT 同时处理维度很不对称的坐标和表达：

- 二维坐标经线性层变成 1 个空间 token；
- 长度为 $D$ 的表达向量按默认每 8 个特征分块，每块经两层 MLP 变成一个 gene token；
- 两类 token 拼接后加固定的一维正弦位置编码。

源码 `models/git.py:99-127` 给出的默认结构由高层 API 控制：hidden size 256、6 个 GiTBlock、8 个注意力头。表达维度不能被 patch size 整除时，`git.py:32-42` 先补零；输出头在 `git.py:193-195` 再切回原始基因数。

Transformer 的全局条件不是额外序列 token，而是四个嵌入之和：

$$
\mathbf{w}_t=E_t(t)+E_z(z_t)+E_z(\Delta z)+E_c(c_t).
$$

代码 `git.py:183-190` 使用同一个 z embedder 编码当前位置 $z_t$ 与切片间距 $\Delta z$。每个 GiTBlock 由这个条件生成注意力和 MLP 两支的 shift、scale、gate，通过 adaLN-Zero 调制 token。调制层和坐标/表达输出层被零初始化（`git.py:131-157`），使训练初期的速度预测从接近零开始，降低 ODE 向量场突然发散的风险。

### 5. 第四步：流匹配学的是“速度”，不是中间图像

对 UOT 抽到的起终点 $(s_0,s_1)$，训练随机采样 $t$，沿线性概率路径得到中间状态：

$$
s_t=(1-t)s_0+t s_1,
$$

其连续坐标与表达的目标速度分别是 $\mathbf{x}_1-\mathbf{x}_0$ 和 $\mathbf{g}_1-\mathbf{g}_0$。GiT 输入当前的 $(\mathbf{x}_t,\mathbf{g}_t,c_t,t,z_t,\Delta z)$，输出空间、表达、类别三组速度。

当前代码 `module.py:63-105` 的真实损失是：

$$
\mathcal{L}=\operatorname{MSE}(v_x,u_x)
+0.1\operatorname{MSE}(v_g,u_g)
+10\operatorname{MSE}(v_c,u_c).
$$

这里存在第一处关键论文—代码差异：论文 Eq. 5 把类别项写成 cross-entropy，但代码把 one-hot 类别也沿连续路径插值，并用与坐标、表达相同的速度 MSE；源码中没有该训练路径的交叉熵。因而实现更准确地说是“三个连续状态通道的联合流匹配”，最终才对类别轨迹取 argmax。

优化器是 AdamW，默认学习率 `2e-4`、weight decay `1e-5`。训练还维护 decay 0.999 的 EMA 模型，并只用 EMA 模型采样（`module.py:32-44,118-126,162-207`）。EMA 没有在论文 Methods 中明确展开，却会影响实际生成结果。

### 6. 第五步：按细胞密度在深度上放置虚拟细胞

如果相邻切片分别有 $N_0,N_1$ 个细胞，DeepSpatial 假设细胞密度随相对深度 $t$ 线性变化。其归一化 CDF 为：

$$
F(t)=\frac{2N_0t+(N_1-N_0)t^2}{N_0+N_1}.
$$

令 $u\sim U(0,1)$ 并解二次方程，可得：

$$
t=\frac{-N_0+\sqrt{N_0^2(1-u)+N_1^2u}}{N_1-N_0}.
$$

`core.py:462-469` 直接实现这个逆 CDF；当 $N_0\approx N_1$ 时退化为 $t=u$。因此虚拟细胞的 z 分布不是机械等间距，而是跟随两端细胞数量的线性密度假设。目标细胞总数由平均切片细胞数乘以“物理间距/指定厚度”估算（`core.py:436-444`），所以 `thickness` 同时影响重建分辨率和内存成本。

### 7. 第六步：双向 ODE 生成

对每个目标深度，模型可从下层切片正向积分，也可从上层切片反向积分。论文 Eq. 6 写的是 $b\sim\mathrm{Bernoulli}(0.5)$，即固定 50/50 选方向；代码 `core.py:471-476` 则使用：

```python
is_fwd = torch.rand(total_cells, device=dev) > t_vals
```

所以靠近 $S_0$ 的点更大概率从 $S_0$ 出发，靠近 $S_1$ 的点更大概率从 $S_1$ 出发。它缩短了平均积分距离，但不是论文写的独立 50/50 Bernoulli。这是第二处关键复现边界。

采样以默认 `dopri5` 求解概率流 ODE，并按 chunk 处理父细胞以控制显存。代码先求离散轨迹，再在相邻 ODE 步之间线性插值得到每个 $t$ 的状态（`core.py:482-521`）。因此“任意深度”在接口上连续，但数值精度仍受 ODE 容差、采样步数、速度场质量和轨迹插值共同限制。

### 8. 论文所称空间剪枝，代码实际做了什么

论文 Eq. 9 描述：先过采样，再保留与源端空间锚点运输代价最小的 $N(t)$ 个细胞。这暗示会计算空间距离并删除几何离群点。

当前源码 `core.py:528-543` 没有实现该空间子集优化。它计算每个父细胞表达向量的非零基因数 $k$，然后只保留生成表达中最大的 $k$ 个值，其余置零。也就是说，代码做的是“按父细胞匹配表达稀疏度”，不是论文 Eq. 9 的空间剪枝。这是第三处、也是输出解释中最重要的差异：公开实现会改变所有生成表达矩阵的稀疏性，但没有按论文公式筛除空间离群细胞。

### 9. 图应该怎样读

图 1 是方法主线：离散多层二维切片 → UOT 对齐 → Transformer 流匹配 → 密度引导的 ODE 生成 → 连续三维体积。它同时展示任意深度虚拟切片、复杂三维空间域、器官级重建和多平面切片四种用途。

图 2 使用真实三维 Deep-STARmap/Deep-RIBOmap 数据先人为稀疏取层，再比较重建与 ground truth；这是比只看切片平滑度更强的评估设计。图 3 和图 4 分别展示 BRCA IMC 与 HNSCC openST 的应用，支持蛋白/转录组和肿瘤微环境场景。图 5 报告从 129 张、约 416 万真实细胞扩展到约 3917 万细胞的全脑结果，并给出 41.6 小时运行时间。图 6 用另一只动物的水平切片做跨方向参照，说明生成体可支持冠状、水平和矢状虚拟切片。

这些图支持“生成结果在多种结构和标记统计上与参照一致”，但不能单独证明每个虚拟细胞的真实对应关系。尤其真实应用中的中间深度没有逐细胞 ground truth，图形连续性也可能受到输入配准、密度先验和表达稀疏化的共同影响。

### 10. 输入、输出与复现边界

最小输入合同是：相同特征空间的 AnnData 列表、`.obsm` 中的二维坐标、`.obs` 中的物理 z 与细胞类型。输出 AnnData 的 `.X` 是稀疏生成表达，`.obsm` 保存恢复到物理尺度的坐标，`.obs` 继承父细胞元数据并加入生成 z 和预测类别。

公开仓库提供 Python 包、训练/推断核心和部分教程，足以审计主算法；但本工作区没有找到论文补充材料的独立 Markdown，也没有验证论文全部处理后数据、模型权重和端到端表格复现。因此当前能确认的是“固定源码实现了哪些机制”，不是“本地已经重现论文所有数值”。

最后应把 DeepSpatial 理解为一个受配准、UOT 配对、线性密度先验和神经 ODE 共同约束的条件生成器。它提供了从 2D 切片构造连续 3D 假设组织的实用途径；生成细胞是模型推断，不是新增实验观测。复现时必须显式记录论文版本、代码提交、坐标预处理、细胞标签、`thickness`、UOT 参数、ODE 参数以及上述三处论文—代码差异。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## DeepSpatial Summary

**Paper**: Reconstructing True 3D Spatial Omics at Single-Cell Resolution
**DOI**: 10.1101/2026.04.28.721395
**Authors**: Yuhang Yang*, Yiming Luo*, Kai Zhang, Yonggan Bu, Zheng Xia, Haoxin Peng, Rui Yan, Qi Liu, Defu Lian, Yang Chen, Lin Shen, Enhong Chen
**Institution**: University of Science and Technology of China; Peking University Cancer Hospital; Oregon Health & Science University
**Category**: integration_multimodal
**Date analyzed**: 2026-05-19

---

### Motivation & Novelty

#### Biological problem
The 3D organization of cells is fundamental to tissue function — neurons fire in laminar circuits, tumor cells form hierarchical niches, and immune cells infiltrate along vascular gradients. Deciphering these spatial relationships requires capturing the full 3D molecular landscape of tissue. Yet spatial omics is inherently 2D: physical sectioning produces thin slices separated by gaps of 10–100+ µm, each profiled independently.

#### Why existing methods fall short

**Experimental 3D platforms** (Deep-STARmap/RIBOmap, Nat. Methods 2025; Yapp et al. 3D-CyCIF, Nat. Methods 2025) can profile intact 3D tissue volumes without sectioning, but are limited to ~150–200 µm depth — insufficient for organ-scale 3D mapping — and require prohibitively expensive and complex protocols.

**Computational alignment-only methods** (PASTE, Nat. Methods 2022; GPSA, Nat. Methods 2023) register discrete 2D slices into a common coordinate system but produce no content between measured sections. They still leave the fundamental gaps unfilled.

**2.5D generative methods** — the current state of the art — address the gap problem by interpolating virtual slices between real ones:
- SpatialZ (Nat. Methods 2025): generative imputation between adjacent sections; defines the primary benchmark
- MiMYR (bioRxiv 2025): diffusion model for 2.5D tissue synthesis
- MorpHE (bioRxiv 2026): image-guided spatial omics generation

Even with dense virtual interpolation, these remain fundamentally **discrete**: the representation is a stack of 2D planes. This inherent discreteness causes: (1) z-axis discontinuities that obscure depth-dependent molecular gradients; (2) inability to resolve 3D cellular neighborhoods spanning multiple layers; (3) artifacts from excessive interpolation steps; (4) computational cost that scales with the number of virtual planes generated.

#### What DEEPSPATIAL contributes
DEEPSPATIAL makes a fundamental shift from **2.5D stacking to true 3D continuous modeling** by reformulating 3D reconstruction as learning a continuous probability density evolution via **flow matching**. The key contributions:

1. **Continuous vector field representation**: Instead of generating discrete intermediate planes, learns a velocity field $\mathbf{v}_\theta(t, s_t)$ that can yield tissue states at ANY arbitrary z-depth via ODE integration — infinitely resolvable.

2. **Unbalanced Optimal Transport coupling**: Establishes biologically rigorous cell correspondences that accommodate different cell counts between slices (proliferation/apoptosis), constrained by spatial proximity, transcriptomic similarity, and cell-type identity simultaneously.

3. **Gene Diffusion Transformer (GiT)**: A DiT-based multimodal architecture with a unified tokenization strategy — one spatial token + M gene patch tokens — conditioned on physical depth and cell type via adaLN-Zero, enabling heterogeneous modality co-evolution in a shared vector field.

4. **Density-preserving generation**: Inverse CDF sampling ensures generated cells respect the macroscopic density gradient between source and target slices, preventing over-representation at either endpoint.

5. **Scalability**: Chunked ODE integration enables organ-scale reconstruction (39M cells, mouse whole brain) in 41.6 hours — versus an estimated 801 hours for SpatialZ at the same scale.

---

### Method Overview

DEEPSPATIAL processes an ordered list of 2D spatial omics slices through a three-stage pipeline:

**Stage 1 — Unbalanced Optimal Transport (UOT) coupling**: For each adjacent slice pair $(S_0, S_1)$, compute a cost matrix combining normalized Euclidean spatial distance, cosine gene expression distance, and a cell-type penalty (λ=10.0 to disfavor cross-type matching). Solve the entropy-regularized UOT objective (ε=0.8, τ=0.05) via the Sinkhorn algorithm to obtain a soft coupling matrix $\pi^*$. Sample training pairs $(s_0^{(i)}, s_1^{(j)})$ proportionally to $\pi^*_{ij}$.

**Stage 2 — Flow matching training**: For each sampled cell pair and random time $t \in [0,1]$, interpolate the cell state linearly ($s_t = (1-t)s_0 + ts_1$). Train the GiT model to predict the constant target velocities $(x_1-x_0, g_1-g_0)$ for continuous modalities and cell-type evolution for the discrete modality, via a joint MSE loss with weights $\lambda_g=0.1$ (gene) and $\lambda_c=10.0$ (cell type). An EMA model (decay=0.999) is maintained for inference.

**Stage 3 — 3D volume generation**: Sample uniform random variables $u$; invert the density CDF to obtain target t-values reflecting the physical cell density gradient. Assign each virtual cell to a direction (forward from $S_0$ or backward from $S_1$) based on t-value proximity. Integrate the EMA model via dopri5 ODE solver in chunks of 2048 cells. Apply post-hoc gene sparsity enforcement matching parent cell density. Restore physical coordinates via inverse min-max transform.

The architecture is a clean Python library (no training scripts) with a `DeepSpatial().setup_data().build_model().fit().reconstruct_full_volume()` API. Default model: hidden_size=256, depth=6, num_heads=8, patch_size=8.

See `doc_method.md` for full mathematical derivation and `doc_code.md` for implementation details including discovered paper/code divergences.

---

### Evaluation

#### Benchmark against real 3D ground truth (Figure 2)
Using Deep-STARmap and Deep-RIBOmap 3D datasets (150 µm continuous), real data was downsampled to sparse pseudo-2D sections and then reconstructed. Compared to SpatialZ (current 2.5D state-of-the-art):

| Dataset | Metric | DEEPSPATIAL | SpatialZ |
|---------|--------|-------------|----------|
| cSCC Deep-STARmap | Cosine similarity | **0.37** | 0.19 |
| cSCC Deep-STARmap | Moran's I R | **0.897** | 0.766 |
| Mouse brain STARmap | Cosine similarity | **0.48** | 0.27 |
| Mouse brain STARmap | Moran's I R | **0.902** | 0.884 |
| Mouse brain RIBOmap | Cosine similarity | **0.43** | 0.26 |
| Mouse brain RIBOmap | Moran's I R | **0.875** | 0.816 |

Cosine similarity (3D voxel cell-type composition) shows ~2× improvement; Moran's I correlation (transcriptomic spatial structure) shows smaller but consistent improvement.

#### Real-world applications
- **BRCA IMC** (Figure 3): 15-slice imaging mass cytometry dataset, 40 protein markers, 2 µm thickness, 20 µm interval. Reconstructed 280 µm continuous 3D tumor microenvironment. Revealed continuous vascular networks from fragmented sections; immune-vascular niche analysis showed T/B cells preferentially localized to distal vascular ends (150–250 µm), endothelial cells enriched near 50 µm.
- **HNSCC openST** (Figure 4): Irregular inter-slice spacing metastatic lymph node whole-transcriptome data, split into 4 subgroups. Smooth cellular z-axis transitions; preserved canonical marker genes (S100A7 in tumor, SPP1 in CAMs). 3D neighborhood analysis revealed T cell clustering at depths not detectable from any single 2D section.
- **Mouse whole brain** (Figure 5): 129-slice MERFISH atlas (4.17M cells) → 39.17M cell 3D atlas in 41.6 hours. Spearman R=1.00 (P<0.001) for cell-type proportions across all 14 brain regions. Equivalent UMAP structure between 3D atlas and original slices.
- **Multi-planar slicing** (Figure 6): Virtual coronal, horizontal, and sagittal cross-sections all matched real anatomical sections from an independent validation animal. Continuous 3D striatum and olfactory bulb architecture visualized.

---

### Reproducibility: 3/5

**Positive factors**:
- Clean public library at https://github.com/yyh030806/DeepSpatial with pip installation
- Three tutorial notebooks (BRCA IMC, Deep-STARmap mouse brain, MERFISH hypothalamus)
- Interactive documentation at https://yyh030806.github.io/DeepSpatial
- All datasets used are public (BRAIN Initiative, openST, IMC from cited papers)
- Code is concise (~1,500 lines) and well-documented with docstrings
- Default hyperparameters in code match paper's Table S1 description

**Concerns**:
- **No benchmark evaluation code**: The primary quantitative comparisons (cosine similarity, Moran's I vs SpatialZ) are not in the repository. SpatialZ is not included for direct comparison.
- **Key paper/code discrepancies**: Cell-type loss (paper claims cross-entropy, code uses MSE); bidirectional sampling (paper claims Bernoulli(0.5), code uses t-biased); spatial pruning (paper claims Eq 9 minimum transport cost, code uses gene sparsity enforcement). These are material differences that affect reproducibility of claimed results.
- **Gene sparsity enforcement undocumented**: A key post-processing step affecting all gene expression outputs is absent from the paper — reproducing results without the code would produce unrealistically dense expression profiles.
- **No pre-trained models provided**: Users must train from scratch on their own data; no reference checkpoints for validation.
- **Table S1 referenced for hyperparameters** but supplementary not available (no supp_md). Default hyperparameters in code are consistent with what can be inferred, but some details (UOT iterations, ODE tolerance) are only in code.
- The 39M-cell brain reconstruction requires a "mid-range server" (vague) and 41.6 hours — resource requirements not formally specified. chunk_size=2048 may need tuning for different GPU VRAM.

**Overall**: The core methodology is reproducible given the public code and documentation. The primary barrier is the lack of evaluation benchmarking code and the paper/code discrepancies that would prevent exact replication from the paper alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
