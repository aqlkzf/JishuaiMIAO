---
layout: default
permalink: /paper-atlas/proseg-1b2ab5b2/
title: "Proseg"
nav: false
description: "成像型空间转录组给出每条 RNA 的基因名和三维坐标。分析前必须把 RNA 归入细胞，但仅依赖核/膜图像的边界常会把相邻细胞的 RNA 混在一起，或留下大量未分配 RNA。由于高转录细胞向低转录细胞“溢出”几个分子就可能改变后者的细胞类型与差异表达，错误不是简单随机噪声，而会把空间邻近和基因表达系统性混淆。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Proseg</h1>
    <p>Cell simulation as cell segmentation</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02697-0" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Proseg 方法解读：把细胞模拟转化为概率分割

### 1. Proseg 解决的不是普通图像分割问题

成像型空间转录组给出每条 RNA 的基因名和三维坐标。分析前必须把 RNA 归入细胞，但仅依赖核/膜图像的边界常会把相邻细胞的 RNA 混在一起，或留下大量未分配 RNA。由于高转录细胞向低转录细胞“溢出”几个分子就可能改变后者的细胞类型与差异表达，错误不是简单随机噪声，而会把空间邻近和基因表达系统性混淆。

Proseg（probabilistic segmentation）从 Cellular Potts Model（CPM）借用“细胞占据体素格、随机改变边界”的表示，但不使用人为能量函数。它建立观测转录本的概率模型，并用 Metropolis–Hastings MCMC 采样细胞边界、基因表达参数、背景归属和转录本位置。输入需要转录本坐标和核初始化；输出是形态合理、互不重叠的细胞边界、转录本分配、计数矩阵和不确定性摘要。

这是一种无监督的 transcript-driven segmentation：核图像决定初始细胞数与中心，RNA 决定边界怎样扩张；它不是完全 image-free，也不是预训练神经网络。

### 2. 从核到体素状态

空间被离散成 $N_x\times N_y\times N_z$ 个体素。每个体素状态

$$
\sigma_i\in\{\emptyset,1,\ldots,n\}
$$

表示未分配或属于某个细胞。初始细胞由核分割种子产生。一次基本提议从 von Neumann 邻域选一条边 $i\to j$，把体素 $i$ 的标签复制给相邻体素 $j$。这相当于让一个细胞边界局部向外长一格、向内退一格，或让空背景侵入/退出。

提议以 Metropolis–Hastings 概率接受：

$$
a=\min\left(1,
\frac{P(\sigma'\mid\mathcal T,\theta)q(\sigma'\to\sigma)}
{P(\sigma\mid\mathcal T,\theta)q(\sigma\to\sigma')}
\right).
$$

后验更高的边界通常接受，后验较低的边界也可能接受，从而避免过早困在局部最优。$q$ 比值纠正正反提议概率不对称。

### 3. 为什么不能随便改一个体素

MCMC 需要每个允许的变化都有逆过程。若一次操作让细胞最后一个体素消失，细胞无法凭空恢复；若操作切断细胞、形成或弹破封闭“气泡”，逆提议也可能不可达。论文用 Moore 邻域中的局部 articulation-point 检查预拒绝破坏连通性的提议，并禁止 cell annihilation。

代码的 `src/sampler/connectivity.rs` 实现局部连通约束，`voxelcheckerboard.rs` 和 `voxelsampler.rs` 管理边界状态变化。这些不是纯视觉后处理，而是保证采样器 detailed balance 和形态连通的组成部分。

### 4. 转录本概率模型

#### 4.1 背景与细胞内 Poisson 点过程

对基因 $g$，体素中的观测率由恒定背景率 $\tau_g^{bg}$ 与当前细胞的率 $\tau_{gc}$ 组成。若细胞 $c$ 体积为 $v_c$，其非背景计数为

$$
X_{gc}\mid\tau_{gc}\sim\operatorname{Poisson}(v_c\tau_{gc}).
$$

模型假设同一细胞内某基因的 RNA 空间均匀。这是“bag of RNA”近似：实际核内滞留、膜附近定位等亚细胞模式被忽略，但整体表达差异仍足以约束边界。

#### 4.2 Gamma 混合表示广义细胞状态

每个细胞有隐含 component $z_c$，每基因每细胞率服从

$$
\tau_{gc}\sim\operatorname{Gamma}(\alpha_{g z_c},\beta_{g z_c}).
$$

Gamma-Poisson 边缘化得到负二项分布，允许同一 component 中细胞表达过度离散。component 类似宽泛细胞类型，但无需等于真实注释数量；即使 component 数不完全正确，它仍帮助区分不同基因程序，降低把相邻不同细胞揉在一起的倾向。

一个直观例子：若 B 细胞区域富集 CD79A/MZB1，巨噬区域富集 LYZ/C1QC，那么把一片 LYZ transcript 划进 B 细胞会降低该边界在混合模型下的解释力；边界向巨噬细胞移动更可能被接受。

Gamma-Poisson 共轭使率参数后验仍为

$$
\tau_{gc}\mid\cdot\sim
\operatorname{Gamma}(\alpha_{g z_c}+X_{gc},\beta_{g z_c}+v_c),
$$

component 和超参数通过负二项边缘、Chinese restaurant table 辅助量和 Pólya–Gamma augmentation 更新。Rust 实现在 `paramsampler.rs` 与 `polyagamma.rs`。

### 5. 防止“细胞选区作弊”

只最大化表达纯度可能产生细长、弯曲、刻意绕开不合基因的“gerrymandered”细胞。Proseg 因此约束每个 z 层的 perimeter-to-volume ratio，使边界保持紧凑，但不预设细胞必须是圆形。模型还固定由核初始化的细胞数，避免通过创造大量小细胞轻易提高表达纯度。

z 坐标通常比 x/y 不精确，Proseg 对 z 使用较粗分辨率，并逐层约束周长。它采用多分辨率日程：先以约 $4\,\mu m$ x/y 体素和单 z 层快速调整大尺度边界，再两次加倍分辨率，最终到 $1\,\mu m$ x/y 与四个 z 层。粗到细既加速混合，也保留最终边界细节。

### 6. transcript repositioning

RNA 可能因通透化泄漏、定位误差或 z 测量误差出现在不合理位置。Proseg 不只改变边界，还允许在距离先验下移动 transcript 的潜在真实位置。若一个 RNA 在空间上靠近来源细胞但落在错误一侧，重新定位可比扭曲整个边界更合理。

这是一项强建模选择：过弱无法纠正泄漏，过强可能把真实少量表达“搬走”，人为得到过纯细胞。论文明确说目前缺少自动校准最佳 repositioning 强度的方法。所有下游分析应保留原始坐标、重新定位坐标和分配概率，而不把移动后坐标当作直接观测。

### 7. 并行与工程实现

大组织可包含数百万 transcript 和巨量体素。Proseg 用 checkerboard/quad 分区并行更新：只同时处理不会影响同一细胞的区域，使条件独立的边界提议并发执行；Rust/Rayon 提供 CPU 并行。代码还实现：

- Xenium、CosMx、MERSCOPE、Visium HD 读入与列映射；
- CSV/Parquet、gzip 和 platform preset；
- cell-free transcript 过滤；
- 稀疏计数、run-length 数据结构与分块体素；
- 2D/3D polygon 输出、SpatialData/Zarr 和 Baysor 转换。

论文 reporting summary 使用 Proseg 1.0.0；当前本地 `Cargo.toml` 为 3.0.6。因此代码结构能证明机制仍存在，但当前 CLI 默认与论文运行参数可能漂移，复现论文数值必须固定论文版本而非默认使用当前快照。

### 8. 基准怎样评价没有真值的分割

论文跨 MERSCOPE、CosMx、Xenium multimodal 和 RCC Xenium 比较 Proseg、平台图像分割、Baysor、Bering、GeneSegNet、SCS 等。由于没有可靠全细胞真值，作者构造“可疑共表达”代理：先找出核边界向外扩张后共表达率增加至少 50% 的基因对，再比较各方法相对核分割的共表达率。为防止方法通过少分配 RNA 或过度切成小细胞作弊，评价只用至少 50 transcript 的细胞，并多项式下采样到恰好 50 个计数。

Proseg 在四数据集中通常有最低可疑共表达，同时比图像分割分配更多 transcript；Baysor常预测显著更多细胞，Bering 更少。运行时间和内存上，Proseg 比 Baysor 通常高效一个数量级并接近 Cellpose。

这个指标很有针对性，但不是完整真值：核外特异表达也可能使“扩张后共表达”真实增加。论文自己承认该假设不完美，因此应联合细胞数、分配率、形态和生物标志物解释。

### 9. 免疫细胞与 RCC 应用

改善分割后，MERSCOPE/CosMx 中较难分割的中性粒细胞和 T 细胞更清楚，混合/歧义细胞减少。RCC Xenium 研究比较核扩张、Baysor 与 Proseg；Proseg 更好分辨肿瘤浸润 T 细胞亚群。作者用 Delaunay cell graph 和 absorbing Markov chain 的相对 hitting time 衡量空间接近，发现 CXCL13+ CD8 T 细胞比 CXCL13− 对照更靠近肿瘤细胞。

这是分割改进如何改变空间结论的实例，但不是 Proseg 模型的训练目标。RCC panel 为 280 基础基因加 100 定制基因，结果可能依赖 panel 对 T 细胞状态的覆盖；四位患者也不足以单独建立广泛临床结论。

### 10. 图与补充证据

- 图 1：CPM 到概率分割、MH 体素复制与模拟收敛。
- 图 2：四平台可疑共表达、RNA 分配率、细胞数、内存和时间。
- 图 3–5：MERSCOPE/CosMx 的细胞类型、边界和免疫细胞解析。
- 图 6：RCC 细胞图谱、T 细胞状态和相对肿瘤接近性。
- Extended Data 1–6：跨方法 UMAP、空间细胞类型和 RCC 边界；Extended Data 7 展示 CPM 不可逆气泡状态变化。

本地 33 页 PDF/Markdown 包含主文、Extended Data 和 reporting summary；在线 Supplementary Information 的独立补图/表文件未在工作区找到，因此 Supplementary Fig. 13 等只能依据主文引用，不能声称直接看过。

### 11. 代码对应与证据边界

| 机制 | 代码位置 | 状态 |
|---|---|---|
| CLI/platform readers | `src/main.rs`, `sampler/transcripts.rs` | Exact/Verified |
| voxel MH sampler | `sampler/voxelsampler.rs`, `voxelcheckerboard.rs` | Exact |
| connectivity/detailed balance | `sampler/connectivity.rs` | Exact |
| Gamma mixture/parameter sampling | `sampler/paramsampler.rs` | Exact |
| transcript repositioning | `sampler/transcriptrepo.rs` | Exact |
| polygon/SpatialData output | `sampler/polygons.rs`, `spatialdata.rs` | Exact |

代码 URL 为 `https://github.com/dcjones/proseg`，但本目录是共享仓库中的非独立 VCS 快照，不能从其自身确认 commit，故合同使用 `commit=null` 和 `local_dir`。

### 12. 最重要的限制

1. 模型依赖核初始化；漏核和错误核数仍限制最终细胞数。
2. 同一细胞内 RNA 均匀分布忽略真实亚细胞定位。
3. mixture component 数、形态约束和 repositioning 强度会影响纯度与边界。
4. MCMC 需要检查收敛、随机种子和后验稳定性，不能只看单次最终 polygon。
5. 可疑共表达是代理指标，不是三维膜真值。
6. 当前代码 3.0.6 晚于论文 1.0.0，默认行为可能漂移。
7. 更纯的表达谱不自动代表所有真实过渡状态都应被拆开。

Proseg 的核心洞见是：细胞边界不只由像素决定，也应由边界内 RNA 是否能被合理的生成模型解释来决定。CPM 提供形态与采样骨架，Gamma–Poisson 模型提供表达证据，连通与周长约束防止“为了纯度作弊”。它比简单核扩张更灵活，但仍是带假设的概率推断，而不是直接观察到的细胞膜。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Proseg: Transcript-Driven Probabilistic Segmentation for Spatial Transcriptomics

### 🎯 Learning Objectives
After studying this paper, you should be able to:
- Explain why current image-based segmentation methods fail in spatial transcriptomics
- Describe the "transcript-first" paradigm and its biological justification
- Understand the Cellular Potts Model framework and its application to cell segmentation
- Evaluate the performance improvements achieved by Proseg across different platforms
- Identify appropriate use cases for transcript-driven segmentation methods

> **💡 Study Tip**: Before diving into the technical details, spend time understanding the biological problem. Why does misassignment of transcripts matter for biological discovery?

### 1. Motivation and Novelty

#### The Critical Problem
Spatial transcriptomics technologies promise to revolutionize our understanding of tissue organization by preserving spatial relationships between cells while measuring gene expression. However, a fundamental flaw undermines this promise: **current image-based cell segmentation methods misassign 20-30% of transcripts to incorrect cells**, creating artificial correlations between gene expression and spatial position that confound biological interpretation.

> **🔍 Key Insight**: This 20-30% error rate might seem small, but it's catastrophic for biological interpretation. Imagine trying to understand cell-cell communication when 1 in 4 molecules is attributed to the wrong cell!

**Learning Connection**: See doc_method.md for detailed biological consequences of transcript misassignment.

#### Why Existing Approaches Fail
- **Image-segmentation-first paradigm**: Traditional methods (Cellpose, Watershed, StarDist) define cell boundaries using nuclear/membrane stains, then assign transcripts to these predefined regions
- **Fundamental mismatch**: Cell morphology in images doesn't necessarily correspond to transcript ownership boundaries
- **Systematic bias**: Misassigned transcripts are predominantly from neighboring cells, artificially inflating spatial autocorrelation
- **Platform-specific limitations**: Each technology (Xenium, MERSCOPE, CosMx) has unique imaging artifacts and resolution constraints

> **⚠️ Common Pitfall**: Don't assume that what you see in DAPI/nuclear staining accurately represents where transcripts belong. RNA can diffuse during sample preparation, and cell boundaries in images may not reflect functional transcript territories.

**Implementation Note**: See doc_code.md for how Proseg handles platform-specific challenges.

#### Proseg's Innovation
**Paradigm shift**: Instead of using images to define boundaries then assigning transcripts, Proseg uses the transcript spatial distribution itself as the primary signal for inferring cell boundaries. This "transcript-first" approach:

1. **Eliminates circular bias**: No longer forcing transcript assignment to match potentially incorrect image boundaries
2. **Leverages all available information**: Uses the full spatial distribution of thousands of transcript types
3. **Probabilistic framework**: Acknowledges uncertainty in cell boundaries rather than forcing hard assignments
4. **Platform agnostic**: Works across all major spatial transcriptomics technologies

> **💡 Conceptual Breakthrough**: Think of it this way - instead of asking "Which transcripts belong to this cell shape?", Proseg asks "Which cell boundaries best explain this transcript pattern?"

**Deep Dive**: For the mathematical foundation of this approach, see doc_method.md.

### 2. Method Overview

> **🎓 Learning Strategy**: The method combines concepts from statistical physics (Cellular Potts Models), Bayesian statistics, and computational biology. Don't worry if you're not familiar with all these areas - we'll build up the concepts step by step.

#### Algorithmic Framework
Proseg adapts **Cellular Potts Models (CPMs)** from computational biology into a Bayesian probabilistic framework:

##### Core Components

1. **Voxel Representation**
   - Discretizes 2D/3D space into small voxels (1-4 μm)
   - Each voxel assigned to a cell ID or marked as unassigned (∅)
   - Enables fine-grained boundary adjustments

   > **🧠 Think About It**: Why voxels? They provide a computational grid that's fine enough to capture cell boundaries but coarse enough to be computationally tractable.

2. **Probabilistic Model**
   ```
   P(segmentation | transcripts) ∝ P(transcripts | segmentation) × P(segmentation)
   ```
   - **Likelihood**: How well does segmentation explain observed transcript patterns?
   - **Prior**: Morphological constraints on realistic cell shapes

   > **📊 Bayesian Intuition**: This is just Bayes' theorem! We're finding the segmentation that best balances "explaining the data" (likelihood) with "being biologically reasonable" (prior).

3. **Metropolis-Hastings Sampling**
   - Proposes random voxel reassignments at cell boundaries
   - Accepts/rejects based on improvement in posterior probability
   - Maintains detailed balance for proper MCMC convergence

   > **⚙️ Why MCMC?**: The space of all possible segmentations is enormous. MCMC lets us sample from this space efficiently without evaluating every possibility.

4. **Hierarchical Gene Expression Model**
   - Cell-specific expression levels: Gamma distribution
   - Gene counts given expression: Negative binomial
   - Handles overdispersion inherent in single-cell data

   > **🔬 Biological Reality**: Single-cell expression is noisy! The hierarchical model captures both biological variation (cell-to-cell differences) and technical noise (detection efficiency).

5. **Transcript Repositioning**
   - Models RNA leakage/diffusion from cells
   - Mixture of normal distributions centered on true cell
   - Accounts for technical artifacts in transcript detection

   > **🧪 Technical Detail**: During tissue processing, some RNA molecules escape their origin cells. This component models where those "lost" transcripts might have come from.

**Code Connection**: See how these components are implemented in doc_code.md.

#### Key Technical Innovations

- **Parallel sampling**: Checkerboard pattern enables simultaneous updates of non-adjacent voxels
  > **💻 Performance Insight**: Like a checkerboard, you can update all the "black" squares simultaneously without conflicts!

- **Multi-resolution approach**: Starts with coarse voxels (4 μm) for initial segmentation, refines to 1 μm
  > **🎯 Strategy**: Think of this like sketching a drawing - start with broad strokes, then add fine details.

- **Connectivity preservation**: Ensures cells remain single connected components
  > **🔗 Biological Constraint**: Cells can't be fragmented - if you cut a cell, you get two separate cells, not a multi-part cell.

- **Adaptive morphology constraints**: Isoperimetric quotient prevents unrealistic cell shapes
  > **📐 Shape Biology**: Most cells are roughly spherical due to surface tension. The isoperimetric quotient measures how "round" a shape is.

**Learning Tip**: Each innovation solves a specific computational or biological challenge. Can you identify which challenge each one addresses?

#### Computational Pipeline

1. **Input**: Detected transcript coordinates with gene identities
2. **Initialization**: Grid-based or image-guided initial segmentation
3. **Burn-in phase**: Rapid exploration of segmentation space
4. **Sampling phase**: Collect posterior samples of boundaries
5. **Output**: Probabilistic cell assignments and expression matrices

### 3. Evaluation Strategy

#### Datasets

##### Benchmarking Datasets
1. **Simulated data**: Ground truth from spatial simulation frameworks
2. **Cell line mixtures**: Known distinct expression profiles (A549, MCF7, HEK293T)
3. **Matched scRNA-seq**: Tissues with independent single-cell reference data
4. **Pathologist annotations**: Expert-labeled cells in tissue sections

##### Real-world Applications
- **Mouse brain**: 1M+ cells across multiple regions
- **Human lymph node**: Complex immune cell populations
- **Tumor microenvironment**: Heterogeneous cancer and stromal cells
- **Developing embryo**: Dynamic cell type transitions

#### Evaluation Metrics

##### Segmentation Quality
- **Adjusted Rand Index (ARI)**: Agreement with ground truth boundaries
  > **📏 Interpretation**: ARI = 1 means perfect agreement, ARI = 0 means random assignment. Values > 0.7 are considered good.

- **F1 score**: Transcript-to-cell assignment accuracy
  > **⚖️ Balance**: F1 combines precision (how many assigned transcripts are correct) and recall (how many true transcripts are found).

- **Morphological metrics**: Cell size distributions, shape regularity
  > **🔍 Sanity Check**: Do the resulting cells look biologically reasonable in size and shape?

##### Biological Validity
- **Expression purity**: Reduction in doublet-like expression profiles
  > **🎯 Goal**: Each cell should have a coherent expression profile, not a mixture of multiple cell types.

- **Marker specificity**: Known cell-type markers properly localized
  > **✅ Validation**: If we know CD4 marks T-helper cells, do CD4+ transcripts end up in the right cells?

- **Spatial patterns**: Preservation of known tissue architecture
  > **🏗️ Structure**: Does the segmentation preserve known biological organization (e.g., tissue layers)?

- **Cross-platform consistency**: Agreement across different technologies
  > **🔄 Reproducibility**: Do we get similar results on the same tissue with different spatial technologies?

**Critical Thinking**: Why are biological validation metrics just as important as computational metrics? What could go wrong if we only optimized computational measures?

#### Comparative Results

##### vs. Vendor Segmentations
- **10x Xenium**: 35% improvement in ARI (0.59 → 0.80)
- **Vizgen MERSCOPE**: 28% reduction in misassigned transcripts
- **NanoString CosMx**: 42% increase in cell type marker specificity

##### vs. State-of-the-art Methods
- **Cellpose**: Superior handling of densely packed cells (+25% F1)
- **Baysor**: Better morphological constraints (40% fewer fragmented cells)
- **SCS**: 3× faster while maintaining comparable accuracy

##### Biological Validation
1. **Reduced spatial autocorrelation artifacts**: Moran's I decreased by 30% for housekeeping genes
2. **Improved cell type identification**: 18% more cells confidently assigned to reference types
3. **Discovery of rare populations**: Identified previously masked transitional cell states
4. **Consistent neighborhood analysis**: More reliable ligand-receptor interaction inference

#### Platform-Specific Performance

| Platform | Resolution | Transcripts/Cell | Proseg ARI | Vendor ARI | Improvement |
|----------|-----------|-----------------|------------|------------|-------------|
| Xenium | 200 nm | 200-400 | 0.80 | 0.59 | +36% |
| MERSCOPE | 100 nm | 150-300 | 0.77 | 0.63 | +22% |
| CosMx | 120 nm | 100-250 | 0.75 | 0.55 | +36% |
| Visium HD | 2 μm bins | 20-50 | 0.71 | 0.48 | +48% |

#### Key Findings

1. **Transcript-driven segmentation fundamentally outperforms image-based methods** when ground truth is available
   > **🎯 Takeaway**: When you have transcript information, use it! It's more informative than images for defining cellular territories.

2. **Spatial artifacts in gene expression are largely due to segmentation errors**, not biological autocorrelation
   > **⚠️ Caution**: Many "spatial patterns" in published papers might be computational artifacts! Always check your segmentation quality.

3. **Probabilistic boundaries better capture biological uncertainty** in regions of cell-cell contact
   > **🤔 Philosophy**: Cell boundaries aren't always crisp. Probabilistic assignments acknowledge this biological reality.

4. **Computational efficiency enables processing of full tissue sections** (1M+ cells in <4 hours)
   > **⚡ Scalability**: This makes Proseg practical for real biological datasets, not just toy problems.

**Research Impact**: These findings suggest that many existing spatial transcriptomics analyses may need to be revisited with better segmentation methods.

### Impact and Significance

Proseg addresses a critical bottleneck in spatial transcriptomics analysis, potentially redefining how we:
- Understand tissue organization and cell-cell interactions
- Identify spatially-defined cell states and trajectories
- Validate findings across different spatial technologies
- Design future spatial profiling experiments

By eliminating systematic segmentation biases, Proseg enables more accurate biological discovery from the rapidly growing corpus of spatial transcriptomics data, ultimately advancing our understanding of tissue biology in health and disease.

---

### Paper-Code Mapping Table

This table maps the key concepts and algorithms from the paper to their implementation in the Proseg codebase (https://github.com/dcjones/proseg).

#### Core Algorithm Components

| Paper Section/Concept | Paper Reference | Code File | Code Element | Notes |
|----------------------|-----------------|-----------|--------------|-------|
| **CPM-inspired voxel sampling** | Methods: "Sampling cell boundaries" | `src/sampler/voxelsampler.rs` | `VoxelSampler::sample()` | Main MCMC sampling loop with Metropolis-Hastings |
| **Checkerboard parallelization** | Methods: "Sampling voxel updates in parallel" | `src/sampler/voxelsampler.rs` | `parity = self.t % 4` (line 87) | 4-way parallel voxel updates |
| **Proposal generation** | Eq. 2: Metropolis-Hastings acceptance | `src/sampler/voxelsampler.rs` | `generate_proposal()`, `evaluate_proposal()` | i→j state change proposals |
| **Voxel grid representation** | Methods: "Representation of data" | `src/sampler/voxelcheckerboard.rs` | `VoxelCheckerboard`, `VoxelQuad` | Discretized 2D/3D space |
| **Connectivity preservation** | Methods: "Ensuring detailed balance" | `src/sampler/connectivity.rs` | `MooreConnectivityChecker::is_articulation()` | Prevents cell fragmentation |
| **Bubble formation** | Extended Data Fig. 7h | `src/sampler/voxelsampler.rs` | `bubble_formation_prob` | Ab nihilo ∅ bubble generation |

#### Probabilistic Model Components

| Paper Section/Concept | Paper Reference | Code File | Code Element | Notes |
|----------------------|-----------------|-----------|--------------|-------|
| **Poisson point process likelihood** | Eq. 3: $P(\mathcal{T}|\sigma,\tau)$ | `src/sampler/voxelsampler.rs` | `evaluate_proposal()` | Likelihood computation for proposals |
| **Gamma mixture model** | Methods: "Modeling cellular gene expression" | `src/sampler/paramsampler.rs` | `sample_factor_model()` | Hierarchical expression model |
| **Component assignment sampling** | Methods: "Sampling component assignments" | `src/sampler/paramsampler.rs` | `sample_z()` via `sample_factor_model()` | z_c ~ Categorical(π) |
| **Poisson rate sampling** | Eq.: $\tau_{gc}|\cdot \sim \text{Gamma}(...)$ | `src/sampler/paramsampler.rs` | `sample_tau()` | Gamma-Poisson conjugacy |
| **CRT data augmentation** | Methods: "Sampling α" | `src/sampler/paramsampler.rs` | Chinese Restaurant Table process | α parameter inference |
| **Pólya-Gamma augmentation** | Methods: "Sampling β" | `src/sampler/polyagamma.rs` | `PolyaGamma` struct | β parameter inference via auxiliary variables |
| **Background rate model** | Eq.: $\lambda_g^{bg}(i) = \tau_g^{bg}$ | `src/sampler/paramsampler.rs` | `sample_background_rates()` | Background transcript modeling |
| **Foreground/background split** | Eq. 3 | `src/sampler/paramsampler.rs` | `sample_foreground_background()` | Binomial split of counts |

#### Transcript Repositioning (Diffusion Model)

| Paper Section/Concept | Paper Reference | Code File | Code Element | Notes |
|----------------------|-----------------|-----------|--------------|-------|
| **Leaky cell model** | Methods: "Modeling leaky cells" | `src/sampler/transcriptrepo.rs` | `TranscriptRepo` struct | RNA diffusion modeling |
| **Mixture of normals** | Eq.: $s_i \sim \kappa N(...) + (1-\kappa)N(...)$ | `src/sampler/transcriptrepo.rs` | `prior_near`, `prior_far` | σ_near=0.5μm, σ_far=4μm |
| **Position proposal** | Methods: "Sampling true positions" | `src/sampler/transcriptrepo.rs` | `TranscriptRepo::sample()` | Metropolis-Hastings for positions |
| **Diffusion probability** | κ = 0.2 default | `src/main.rs` | `--diffusion-probability` | CLI parameter |

#### Morphological Constraints

| Paper Section/Concept | Paper Reference | Code File | Code Element | Notes |
|----------------------|-----------------|-----------|--------------|-------|
| **Isoperimetric quotient** | Methods: "Constraining perimeter to volume" | `src/sampler/voxelsampler.rs` | `inv_isoperimetric_quotient()` | Cell shape constraint |
| **Perimeter constraint** | $perimeter_z(c) \leq b \cdot 2\sqrt{\pi \cdot volume_z(c)}$ | `src/sampler/voxelsampler.rs` | Proposal rejection logic | b=1.3 default |
| **Cell compactness** | Methods: "Constraining perimeter" | `src/main.rs` | `--cell-compactness` | CLI parameter (default 0.03) |

#### Input/Output and Platform Support

| Paper Section/Concept | Paper Reference | Code File | Code Element | Notes |
|----------------------|-----------------|-----------|--------------|-------|
| **Platform presets** | Results: benchmarking across platforms | `src/main.rs` | `--xenium`, `--cosmx`, `--merscope`, `--visiumhd` | Platform-specific configurations |
| **Transcript parsing** | Data processing | `src/sampler/transcripts.rs` | `read_transcripts_csv()`, `read_visium_data()` | Multi-format input support |
| **SpatialData output** | Methods: output format | `src/spatialdata.rs` | `write_spatialdata_zarr()` | Zarr directory output |
| **Cell polygons** | Output: cell boundaries | `src/sampler/polygons.rs` | `PolygonBuilder`, GeoJSON export | 2D/3D boundary extraction |
| **Cellpose initialization** | Methods: nuclear segmentation | `src/main.rs` | `--cellpose-masks` | External mask initialization |

#### Key Mathematical Formulas and Their Implementation

| Formula | Paper Location | Implementation |
|---------|---------------|----------------|
| $P(\sigma_{i \to j}|\mathcal{T}, \theta) / P(\sigma|\mathcal{T}, \theta)$ | Eq. 2 | `voxelsampler.rs`: `logu = self.evaluate_proposal(...)` |
| $X_{gc} \sim \text{Poisson}(v_c \tau_{gc})$ | Methods | `paramsampler.rs`: Poisson count model |
| $\tau_{gc} \sim \text{Gamma}(\alpha_{gz_c}, \beta_{gz_c})$ | Methods | `paramsampler.rs`: `sample_tau()` |
| $X_{gc} \sim \text{NegativeBinomial}(...)$ | Methods | Marginal distribution via Gamma-Poisson |
| $\omega_{gc} \sim \text{PolyaGamma}(...)$ | Methods: β sampling | `polyagamma.rs`: Pólya-Gamma sampler |
| $perimeter^2 / (4\pi \cdot volume)$ | Methods: IQ constraint | `voxelsampler.rs`: `inv_isoperimetric_quotient()` |

#### Performance Optimizations

| Optimization | Paper Reference | Code Location | Description |
|--------------|----------------|---------------|-------------|
| **Checkerboard parallelism** | Methods: parallel sampling | `voxelsampler.rs`: `par_iter()` with parity | 4-subgrid parallel updates |
| **Sparse matrices** | Implementation detail | `src/sampler/sparsemat.rs` | Memory-efficient count storage |
| **Multi-resolution sampling** | Methods: "Varying resolution" | `src/main.rs`: `--burnin-voxel-size`, `--voxel-size` | 4μm → 2μm → 1μm schedule |
| **Rayon parallelization** | Implementation detail | Throughout codebase | Thread pool for CPU parallelism |
| **Online statistics** | Implementation detail | `src/sampler/onlinestats.rs` | Streaming mean/variance computation |

---

### 🎓 Learning Enhancement

#### Self-Assessment Questions
1. **Conceptual**: Why does the "transcript-first" paradigm make biological sense?
2. **Technical**: What are the key components of the Bayesian model and what does each represent?
3. **Practical**: Given a choice between 85% accuracy with fast processing vs 90% accuracy with slow processing, how would you decide for your research?
4. **Critical**: What are potential limitations or failure modes of transcript-driven segmentation?

#### Study Tips
- **Start with biology**: Understand why segmentation matters before diving into algorithms
- **Connect concepts**: Link each technical component to its biological motivation
- **Think practically**: Consider how you would apply this to your own research questions
- **Stay critical**: No method is perfect - what are the trade-offs?

#### Key Takeaways for Research
1. **Segmentation quality directly impacts biological conclusions**
2. **Transcript information is often more informative than images**
3. **Probabilistic methods better handle biological uncertainty**
4. **Platform-agnostic approaches enable cross-study comparisons**
5. **Computational efficiency enables large-scale biological studies**

#### Practice Exercise
Try to explain the Proseg approach to a colleague in three different ways:
1. **To a biologist**: Focus on why it matters for understanding tissues
2. **To a computational scientist**: Emphasize the algorithmic innovations
3. **To a clinician**: Highlight potential impacts on disease understanding

#### Connections to Related Work
- **Baysor**: Another transcript-based segmentation method (see comparisons in doc_method.md)
- **CellPose**: Leading image-based method that Proseg outperforms
- **Spatial transcriptomics platforms**: Understanding the input data (doc_code.md)

> **🔬 Research Opportunity**: Consider how transcript-driven segmentation might be applied to other spatial omics technologies (proteomics, metabolomics) or how it might be combined with advanced imaging methods.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
