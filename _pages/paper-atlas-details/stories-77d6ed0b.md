---
layout: default
permalink: /paper-atlas/stories-77d6ed0b/
title: "STORIES"
nav: false
description: "STORIES 接收多个时间点的空间转录组切片，在基因表达空间里学习一个标量势能函数 J\\theta(x)。细胞沿势能下降方向 -\\nabla J\\theta(x) 演化；模型用 Fused Gromov–Wasserstein（FGW）距离比较预测群体与下一时点实测群体，使预测既接近下一时点的基因表达，又尽量保存组织内部的相对空间结构。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>STORIES</h1>
    <p>STORIES: learning cell fate landscapes from spatial transcriptomics using optimal transport</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02855-4" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for STORIES">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/cantinilab/stories" target="_blank" rel="noopener noreferrer" aria-label="Open code for STORIES">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STORIES 方法解读：用空间结构约束可外推的细胞命运势能

### 一句话理解

STORIES 接收多个时间点的空间转录组切片，在基因表达空间里学习一个标量势能函数 $J_\theta(x)$。细胞沿势能下降方向 $-\nabla J_\theta(x)$ 演化；模型用 Fused Gromov–Wasserstein（FGW）距离比较预测群体与下一时点实测群体，使预测既接近下一时点的基因表达，又尽量保存组织内部的相对空间结构。训练后的势能可用于排序细胞，梯度可转成 CellRank 的转移核，再做命运概率、基因趋势和转录因子富集。

它的核心不是把二维坐标直接塞入神经网络。神经网络只看表达特征，空间坐标只进入训练损失。这让不同时间切片无需先做刚性对齐，同时也意味着模型学到的是“被空间结构监督的表达动力学”，而不是显式预测细胞在组织中的物理移动。

### 1. 要解决的困难

多时点单细胞数据没有真实的一一谱系配对：$t_k$ 的某个细胞通常不能在 $t_{k+1}$ 再被测一次。OT 方法因此把每个时点看成细胞群体分布，寻找群体之间的软匹配。空间转录组又多出一个困难：不同切片可能平移、旋转、缩放，发育过程还会改变形态，原始坐标不能直接逐点相减。

STORIES 的折中是：

- 基因表达用普通跨群体代价比较；
- 空间部分不比较绝对坐标，而比较切片内部的成对距离；
- 用 FGW 同时优化两部分；
- 用一个跨所有时点共享的表达势能产生未来表达预测。

因此空间信息约束了“哪些表达状态之间的匹配在组织结构上合理”，但推断时的势能和速度仍只依赖表达状态。

### 2. 输入、输出和前提

公开包的 `SpaceTime.fit()` 要求 AnnData 中包含：

- `obs[time_key]`：离散时点；
- `obsm[omics_key]`：表达表示，论文基准使用 Harmony 对齐后的 PCA；
- `obsm[space_key]`：每张切片的二维空间坐标；
- 可选 `obs[weight_key]`：非均匀细胞质量，用于表示增殖或死亡。

论文基准通常取 50 个主成分；两个较小案例使用 20 个。复现实验脚本还会对表达主成分做尺度归一化，并对每张切片的空间坐标居中和缩放。这些关键预处理不由核心包自动完成。

主要输出是：

1. 每个表达状态的势能 $J_\theta(x)$；
2. 表达空间向量场 $v(x)=-\nabla_xJ_\theta(x)$；
3. 给定步长 $\tau$ 后的未来表达 $x-\tau\nabla J_\theta(x)$；
4. 通过 CellRank、样条回归和 TRRUST 富集得到的命运概率、表达趋势与候选调控因子。

这里的 $v(x)$ 是模型从跨时点分布学到的“基因表达空间速度”，不是由 unspliced/spliced 计数估计的经典 RNA velocity。势能值也可作为发育排序坐标，但不是带真实时间单位的测量。

### 3. 势能怎样产生动力学

STORIES 用两层、每层 128 单元的 MLP 表示 $J_\theta$，激活函数为 GeLU，最后输出单个标量。论文采用 Wasserstein 梯度流观点：群体分布沿势能下降方向演化。公开代码的默认显式步为

$$
x_{t+\tau}=x_t-\tau\nabla J_\theta(x_t).
$$

`steps/explicit.py` 直接以 `jax.grad` 计算梯度；`ProximalStep.chained_*` 可把一个时间间隔拆成多步。扩展数据图 1 比较了多步、无 teacher forcing 与隐式离散，论文发现它们没有优于单步显式、带 teacher forcing 的组合，因此正式实验使用成本较低的默认路径。

teacher forcing 的含义是：训练每一对相邻时点时，都从实测的 $\mu_{t_k}$ 出发预测 $t_{k+1}$，而不是把更早的模型预测连续滚动到后面。这通常使训练稳定，但也减少了训练时对长期误差累积的直接暴露；对未见晚时点的外推仍需单独测试。

### 4. FGW 损失如何利用空间

设实测细胞分布为

$$
\mu_t=\sum_i a_i\delta_{(x_i,r_i)},
$$

其中 $x_i$ 是表达表示，$r_i$ 是空间坐标；模型预测分布记为 $\rho_t=\sum_j b_j\delta_{(y_j,s_j)}$。FGW 在所有满足边缘质量约束的运输矩阵 $P$ 中求解

$$
\mathrm{FGW}_{\alpha}^{\varepsilon}(\mu,\rho)
=\min_P(1-\alpha)L(P)+\alpha Q(P)-\varepsilon E(P).
$$

- $L(P)$ 比较 $x_i$ 与 $y_j$，要求预测表达接近实测表达；
- $Q(P)$ 比较切片内部距离 $d(r_i,r_{i'})$ 与 $d(s_j,s_{j'})$，要求被匹配细胞的相对组织几何相容；
- $E(P)$ 是熵正则，使 OT 求解更平滑、更易计算；
- $\alpha$ 控制空间项权重，论文基准最终用 $5\times10^{-3}$。

成对距离在整体平移、旋转以及论文采用的尺度处理下不变，所以模型无需知道两张切片的共同坐标系。但“对等距变换不敏感”不等于对任意形变完全不敏感；强烈的局部拓扑变化、切片缺失和空间采样偏差仍会影响匹配。

熵正则 OT 自身有自距离偏置。`loss.py` 实现去偏版本：

$$
\overline{\mathrm{FGW}}(\mu,\rho)=
\mathrm{FGW}(\mu,\rho)-\tfrac12\mathrm{FGW}(\mu,\mu)-\tfrac12\mathrm{FGW}(\rho,\rho).
$$

总损失对所有相邻时点求和，并乘时距：

$$
\mathcal L(\theta)=\sum_{k=1}^{K-1}(t_{k+1}-t_k)
\overline{\mathrm{FGW}}(\mu_{t_{k+1}},\rho_{t_{k+1}}(\theta)).
$$

当 $\alpha=0$ 时退化为只看表达的线性 Sinkhorn 损失。公开 `SpaceTime` 默认启用 quadratic，并断言 `0 < quadratic_weight < 1`；若要运行线性对照，需要设置 `quadratic=False`，而不是在启用 quadratic 时直接传 0。

### 5. 一轮训练在代码里发生什么

`stories/stories/spacetime.py` 的路径可以按下面顺序阅读：

1. `DataLoader` 按时点划分细胞，并在每个时点分别做 train/validation split；
2. 每轮从所有时点各抽一个同样大小的 mini-batch；不足时点会补采样，但补入样本质量设为 0；
3. `loss_fn()` 对每个相邻时点调用显式势能步，得到预测表达；
4. `quadratic_loss()` 用预测表达、实测表达和两张切片的内部空间距离计算去偏 FGW；
5. JAX 对损失反向传播，Optax AdamW 更新势能网络；
6. 验证损失触发 early stopping，并通过 Orbax 保存最佳参数。

`transform()` 只对表达表示应用训练好的梯度步，不输入空间坐标。这再次说明空间是训练监督，不是推断时的输入变量。

### 6. 增殖和死亡怎样进入模型

标准平衡 OT 要求相邻群体的总质量守恒，但真实发育中不同细胞群会增殖或凋亡。论文用增殖、凋亡基因集计算每个细胞的增长得分，再经过 sigmoid 和 softmax 形成运输边缘权重。`DataLoader` 可通过 `weight_key` 使用这些质量。

这不是从数据中无监督识别真实分裂谱系，而是把基因集先验转换为群体质量。$\Delta t$ 控制权重尖锐程度；论文选择 1，并用已知细胞周期给出的最大可能后代数作合理性核对。增长率具体构造主要存在复现笔记本中，不是 `stories-jax` 核心包的一站式 API。

### 7. 势能之后如何得到命运与候选调控因子

#### 7.1 CellRank 转移和命运概率

`tools.compute_velocity()` 计算 $-\nabla J_\theta$，再交给 CellRank `VelocityKernel` 建立细胞转移矩阵。案例分析用 GPCCA，并人为指定终末状态：轴突再生案例是 `dpEX/nptxEX/mpEX`，小鼠中脑案例是 `NeuB/GlioB`。因此命运概率不是 STORIES 势能单独、无监督地产生的；它还依赖邻接图、CellRank 参数和指定终末状态。

#### 7.2 基因趋势

论文仅为趋势分析使用 MAGIC 插补。`regress_genes()` 把每个基因表达对势能做样条回归，以拟合优度和峰值位置排序，得到沿势能的表达级联。高回归得分表示表达与该一维势能排序一致，不证明该基因驱动了动力学。

#### 7.3 TF 富集

`tf_enrich()` 使用 TRRUST 的 TF–靶基因集合，对某 TF 靶基因与非靶基因的趋势回归分数做单侧 rank-sum 检验。它输出的是数据库靶标在趋势基因中的富集候选。数据库覆盖、物种同源映射、基因相关性和多重检验都会影响解释；“candidate regulator”不能写成因果验证。

### 8. 论文图像证据讲了什么

#### 图 1：从切片到势能

图 1 明确显示三层关系：多时点空间切片作为输入；FGW 训练表达势能；势能梯度支持轨迹、势能排序支持基因趋势和 TF 富集。图中空间只出现在损失侧，与正文“potential is not a function of space”一致。

#### 图 2：三套大图谱基准

作者在小鼠、斑马鱼、蝾螈 Stereo-seq 图谱上设置训练、时间范围内早期测试和包含未见晚时点的晚期测试。10 个随机种子下，STORIES 在六个测试组合的 Wasserstein 表达误差上优于 PRESCIENT；小鼠细胞类型转移准确率也更高。空间匹配图显示斑马鱼 adaxial 细胞被定位在脊索附近，somite 匹配覆盖正确组织区域。

这些结果支持“空间正则改善所选数据和指标上的群体预测”，但不是单细胞谱系真值。比较对象受限：论文说明 stVCR 无公开实现，其他方法也多因代码不可用而未进入基准；PRESCIENT 的噪声参数 `train_sd` 由作者调为 0.01。

#### 图 3：蝾螈神经再生

势能从 wnt/reaEGC 的高值，经 rIPC/IMN 中值，下降到三个成熟兴奋性神经元状态。CellRank 转移恢复三条已报道路线；15 dpi 的 reaEGC 命运概率随损伤两侧空间位置不同。趋势分析复现 Vim 下降、Nptx1 上升，并提出 Hes5、Cdc25b、Map1a、L1cam、Nsg2 等阶段性候选；TRRUST 富集得到 CTNNB1、SP1、MYC、SOX6、MYCN、REST。

#### 图 4：小鼠中脑胶质发生

势能将 RGC 放在高处，将 NeuB 和 GlioB 放在低处；转移场恢复 RGC 向神经与胶质两支分化。空间命运概率显示吻侧更偏 NeuB、极尾侧更偏 GlioB。Mki67 随分化降低，Aldh1l1 升高；趋势还提出 Gmnn、Rrm2、Hmgb2、Tuba1b、Glul、Glis3，TF 富集包括 SOX4、NOTCH2、MYC/MYCN/MAX。

#### 扩展数据

扩展图 1 支持单步、teacher forcing、显式 Euler 的工程选择；扩展图 2 展示 $\alpha$ 在表达误差和空间一致性之间的权衡，最佳区间约 $10^{-3}$ 到 $5\times10^{-3}$；扩展图 3–6 给出跨物种匹配细节；扩展图 7–8 展示命运概率和额外重复切片；扩展图 9 检查 PCA 维数与运行时间；扩展图 10 检查增长率对 $\Delta t$ 的敏感性。正式 PDF 的主图和全部扩展图均已在本次刷新中直接核对。

### 9. 复现性到底到哪里

本地包含两套代码：

- `stories/`：可安装的 `stories-jax` 包，提交 `b9d235add529b025ca5caa951cc908447ea895c9`；
- `stories_reproducibility/`：论文训练配置、评估脚本和绘图/预处理笔记本。

核心包精确覆盖势能网络、显式/隐式步、线性与 FGW 损失、训练循环、势能/速度、趋势和 TF 富集。测试文件用合成 AnnData 覆盖显式、线性、多步和两类隐式路径，但只是短 smoke tests，不验证论文数值。

复现实验仍有边界：原始三套大型图谱需外部下载；预处理与增长率分散在大型笔记本；配置依赖 Hydra、Weights & Biases、SLURM/GPU 环境；核心包默认 `max_iter=10000` 和恒定 AdamW 学习率，而论文复现脚本使用 15000 次上限及 cosine schedule；图 3/4 的部分结果依赖 CellRank 终末状态、MAGIC、TRRUST、RBF 插值与 Blender。因而“代码公开”成立，但从空环境复现全部图不是单条命令即可完成。

### 10. 最稳妥的结论

STORIES 的真正创新，是把 FGW 当作神经势能模型的训练损失：绝对空间坐标不必跨切片对齐，空间内部关系却能约束跨时点表达动力学。它在三套 Stereo-seq 图谱和两个案例中给出一致的预测与可解释下游结果。

最重要的解释边界是：势能是统计模型，不是直接测量的生物能量；梯度是表达空间动力方向，不是经典 RNA velocity；空间影响来自训练损失，不代表模型显式学习物理迁移；命运概率还依赖 CellRank 和指定终末状态；趋势基因与 TF 富集是候选证据，不是因果驱动验证；群体 OT 匹配也不是单细胞真实谱系追踪。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## STORIES: Learning Cell Fate Landscapes from Spatial Transcriptomics Using Optimal Transport

**Citation:** Huizing G.-J., Samaran J., Capocefalo D., Audit A., Peyré G., Cantini L. *Nature Methods*, 23(3), 2025. DOI: [10.1038/s41592-025-02855-4](https://doi.org/10.1038/s41592-025-02855-4)

**Code:** [github.com/cantinilab/stories](https://github.com/cantinilab/stories) | `pip install stories-jax`

### Motivation & Novelty

Spatiotemporal atlases from technologies like Stereo-seq profile gene expression at single-cell resolution within tissues across multiple developmental time points. Inferring cell fate trajectories from such data requires methods that leverage both transcriptomic and spatial information — but spatial coordinates across time points cannot be directly compared because tissue slices may be rotated, translated, or morphologically transformed.

**Existing limitations:**
- **Monocle** (*Nat. Biotechnol.*, 2014): orders cells along pseudotime but cannot predict future expression states
- **RNA velocity** (*Nature*, 2018): predicts expression changes but relies on simplified splicing kinetics
- **Waddington OT** (*Cell*, 2019): infers cell-cell transitions via OT but provides neither pseudotime nor velocity
- **PRESCIENT** (*Nat. Commun.*, 2021): learns a gene expression potential via OT gradient flows, but ignores spatial information entirely
- **Moscot** (*Nature*, 2025): uses FGW for cell-cell transitions between adjacent time points, but cannot extrapolate to unseen future time points
- **SpaTrack**: learns spatial + expression velocities via linear OT but cannot predict beyond observed time points
- **stVCR**: uses rigid spatial alignment (insufficient for morphological transformations), no code available

**STORIES' contribution:** STORIES is the first method to use **Fused Gromov-Wasserstein (FGW) optimal transport** as a training loss for learning a continuous model of differentiation. FGW compares gene expression directly while comparing spatial coordinates through isometry-invariant pairwise distance matrices. This allows STORIES to:

1. Learn a **spatially informed potential** $J_\theta$ that formalizes Waddington's landscape — without requiring slice alignment
2. Provide both a differentiation ordering ($J_\theta$ values) and learned gene-expression-space velocity vectors ($-\nabla J_\theta$); these are not clock time or splicing-derived RNA velocity
3. Predict gene expression at future time points not seen during training
4. Identify cell fate decisions influenced by spatial context

### Method Overview

STORIES trains a neural network $J_\theta$ (2-layer MLP, 128 units, GeLU) to represent a differentiation potential. Given spatial transcriptomics at $K$ time points:

1. **Forward Euler prediction**: cells at $t_k$ are evolved as $\hat{\mathbf{x}} = \mathbf{x} - \tau \nabla J_\theta(\mathbf{x})$
2. **FGW loss**: predicted distributions are compared to observations via debiased FGW, which matches cells based on gene expression similarity while encouraging spatially coherent matchings
3. **Teacher-forcing**: predictions always start from ground-truth observations (not chained predictions)
4. **Downstream**: the trained potential provides pseudotime, velocity (for CellRank integration), gene expression trends (spline regression), and TF enrichment (TRRUST + Wilcoxon)

Key hyperparameters: $\alpha = 5 \times 10^{-3}$ (FGW spatial weight), $\varepsilon = 0.01$ (Sinkhorn regularization), batch size = 1000 cells/timepoint, AdamW optimizer with cosine LR schedule. See `doc_method.md` for full mathematical derivation and `doc_code.md` for code-paper mapping.

### Evaluation

#### Datasets

| Dataset | Organism | Process | Time Points | Cells | Resolution |
|---|---|---|---|---|---|
| MOSTA | Mouse | Embryonic development | E9.5–E16.5 (7 train + 2 test pairs) | 794,063 | Stereo-seq bin50 |
| ZESTA | Zebrafish | Embryonic development | 3.3–24 hpf (5 train + 2 test pairs) | 17,920 | Stereo-seq |
| ARTISTA | Axolotl | Brain regeneration | 2–30 dpi (5 train + 2 test pairs) | 22,083 | Stereo-seq |
| Dorsal midbrain | Mouse | Gliogenesis (RGC→NeuB/GlioB) | E12.5–E16.5 (3 time points) | 4,581 | Image-based segmentation |

Each atlas is split into training, early test (within time range), and late test (extends to unseen future time points).

#### Benchmark Results

**Wasserstein distance** (lower = better): STORIES outperforms PRESCIENT on all 6 test cases (3 datasets × 2 test sets), with the largest improvement on late test sets where the model must generalize to unseen time points.

**Cell-type transition accuracy** (mouse development): STORIES achieves higher accuracy than PRESCIENT in both early and late test sets.

**Spatial benefit** ($\alpha > 0$ vs $\alpha = 0$): Adding spatial information improves Wasserstein distance in all test cases. Qualitative examples show:
- STORIES correctly maps adaxial cells near the notochord (zebrafish); PRESCIENT scatters them across the embryo
- STORIES matches somite cells to their anatomical location; PRESCIENT misses most somites
- STORIES correctly localizes liver and lung predictions to respective organs (mouse); PRESCIENT broadly distributes lung predictions

#### Biological Case Studies

**Axolotl neuron regeneration**: STORIES recovers the three major trajectories (wntEGC→mpEX, reaEGC→rIPC2→dpEX, reaEGC→rIPC1→IMN→nptxEX) without manually specifying starting points or isolating spatial regions. Spatial analysis reveals that reaEGC fate depends on location: right-of-injury → mpEX, left-of-injury → nptxEX. Gene trends recover known markers (Vim decreasing, Nptx1 increasing) and identify CTNNB1 as the top enriched TF.

**Mouse gliogenesis**: STORIES recovers the RGC→NeuB/GlioB branching trajectory. RGC fate depends on spatial position: rostral → NeuB, caudal extreme → GlioB. Gene trends recover Mki67 (decreasing, proliferation) and Aldh1l1 (increasing, astrocyte marker). TF enrichment identifies SOX4 and NOTCH2, both known in gliogenesis.

### Reproducibility

**Rating: 4/5** — Well-documented code with clear reproducibility infrastructure, but some critical preprocessing is not in the main package.

**Strengths:**
- Open-source package (`pip install stories-jax`) integrated into Scverse ecosystem
- Separate reproducibility repository with Hydra configs, all 10 random seeds documented, SLURM scripts
- Clean code architecture: small codebase (~500 lines for core), well-documented
- Tests for all 3 step types (explicit, Monge implicit, ICNN implicit)

**Weaknesses:**
- **Normalization not in package**: PCA truncation, max-normalization, and spatial centering/scaling are only in `scripts/train.py`, not in the installable package. Users must discover and replicate these manually.
- **Growth rate computation not in package**: Only accessible through reproducibility notebooks
- **Cosine LR scheduler not in package defaults**: Package uses constant LR; reproducing paper results requires manually setting up the scheduler
- **Max iterations mismatch**: Package defaults to 10,000; paper uses 15,000
- **Data availability**: All datasets are publicly available (MOSTA, ZESTA, ARTISTA on cngb.org), but preprocessed `.h5ad` files are from the authors' server

**Environment:** JAX 0.4.26 + CUDA, Flax 0.8.2, OTT-JAX 0.4.6, CellRank 2.0.4. The paper reports under 20 min on an A40 GPU for approximately 396,000 cells across seven time points; this is not a verified runtime for the full 794,063-cell MOSTA table entry.

**Interpretation boundaries:** spatial coordinates supervise the FGW loss but are not direct inputs to the potential or `transform()`; CellRank fate probabilities additionally require its graph/model and specified terminal states; OT plans are population couplings rather than observed lineages; trend genes and TF enrichments nominate candidates, not causal drivers.

**Common pitfalls:**
- Forgetting to normalize gene expression and spatial coordinates before training
- Using the package's default max_iter=10000 instead of the paper's 15000
- Not applying the cosine learning rate schedule (significant for convergence)
- Using α too high (e.g., 0.1) makes training much slower due to GW computational cost

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
