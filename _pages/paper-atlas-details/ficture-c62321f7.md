---
layout: default
permalink: /paper-atlas/ficture-c62321f7/
title: "FICTURE"
nav: false
description: "FICTURE 不先把空间转录组切成“一个个细胞”，而是让每个亚微米像素从附近多个锚点中概率性地选择信息来源，再推断该像素属于哪些转录因子，从而得到连续、像素级的组织表达地图。"
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
      <span>Nature Methods · 2024</span>
    </div>
    <h1>FICTURE</h1>
    <p>FICTURE: scalable segmentation-free analysis of submicron-resolution spatial transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## FICTURE 方法详解

### 一句话理解

FICTURE 不先把空间转录组切成“一个个细胞”，而是让每个亚微米像素从附近多个锚点中概率性地选择信息来源，再推断该像素属于哪些转录因子，从而得到连续、像素级的组织表达地图。

### 1. 它要解决什么问题？

亚微米空间转录组可以记录数百万到数十亿个带坐标的 RNA 分子，但每平方微米通常只有很少的转录本。分析时存在一个根本矛盾：

- 把分子聚合到较大的固定网格，计数更稳定，但会损失实验原本提供的高分辨率；
- 先做细胞分割，再在细胞内汇总表达，依赖核或细胞边界图像；当细胞形状不规则、切片没有切到细胞核、细胞多核/无核、染色质量不佳或 RNA 位于胞外时，会漏掉或错分转录本。

论文在多个已分割数据集中观察到 12–55% 的转录本没有被分配到细胞。这个问题在肌肉、血管、肿瘤基质、脂肪组织和高密度组织中特别明显。

已有方法各有局限：Baysor（*Nature Biotechnology*, 2022）能直接处理分子坐标，但在大面积、全转录组数据上计算代价高；JSTA（*Molecular Systems Biology*, 2021）结合深度网络和 watershed，需要细胞核位置及匹配的单细胞参考；GraphST（*Nature Communications*, 2023）以分割后的细胞为单位，容易把稀有或分散细胞类型过度平滑；SSAM（*Nature Communications*, 2021）和 STtools（*Bioinformatics Advances*, 2022）的滑窗策略能缓解固定网格问题，但会重复使用重叠窗口中的分子。

### 2. FICTURE 的核心创新

FICTURE 将任务拆成两个阶段：

1. **先学习稳定的表达因子。** 把稀疏像素聚合到六边形网格，在较粗尺度上运行 LDA；也可以直接使用其他工具或单细胞参考提供的因子表达谱。
2. **再做像素级空间解码。** 在组织上放置比细胞更密的锚点。每个像素不被硬分配给某个网格或细胞，而是在附近锚点之间进行概率选择；锚点则保存多个表达因子的混合比例。

因此，局部像素可以共享统计信息，但最后的因子边界不受六边形或预定义细胞边界限制。

```text
带坐标的转录本
      |
      +--> 六边形聚合 --> LDA / 外部参考 --> 因子表达谱 beta
      |
      +--> 密集锚点格 --> 初始化锚点因子比例 theta
      |
      +--> 重叠空间 minibatch
                |
                +--> 计算像素到邻近锚点的距离先验 w_ij
                +--> 更新像素因子概率 phi
                +--> 更新像素到锚点概率 psi
                +--> 更新锚点因子参数 gamma
                |
                +--> 像素因子图 + 锚点图 + 因子基因计数
```

### 3. 模型中的变量

设有 $N$ 个像素、$M$ 个基因，稀疏计数矩阵为

$$
X\in\mathbb{Z}^{N\times M}.
$$

FICTURE 在组织上放置 $n$ 个锚点。主要变量是：

- $\beta_k$：第 $k$ 个因子的基因表达分布；
- $\theta_j$：锚点 $j$ 的因子混合比例；
- $c_i$：像素 $i$ 选择的锚点；
- $z_i$：像素 $i$ 的潜在因子；
- $w_{ij}$：像素 $i$ 在先验上选择锚点 $j$ 的权重。

距离先验为

$$
w_{ij}\propto 1-\left(\frac{\lVert y_i-y'_j\rVert}{d_{\max}}\right)^\nu,
$$

其中 $d_{\max}$ 是锚点邻域半径。离像素近的锚点权重更大，但在细胞边界附近仍然保留不确定性。代码中的 `PixelMinibatch._prepare_batch` 使用 BallTree 找到半径内锚点，并构建同样的稀疏距离权重矩阵。

生成过程可以理解为：先为每个因子抽取基因表达分布 $\beta_k$，为每个锚点抽取因子混合 $\theta_j$；然后每个像素先选择锚点 $c_i$，再从该锚点的混合中选择因子 $z_i$，最后由相应因子的基因分布生成像素计数。

### 4. 推断过程

论文使用随机变分推断。全局因子表达谱由 $\lambda$ 参数化；局部后验包括：

- $\psi_i$：像素对候选锚点的概率；
- $\phi_i$：像素对各因子的概率；
- $\gamma_j$：锚点因子比例的 Dirichlet 参数。

在每个空间 minibatch 中，代码反复执行：

1. 根据像素基因计数和当前锚点混合更新 $\phi$；
2. 根据因子兼容性、表达证据和距离先验更新 $\psi$；
3. 用

   $$
   \gamma\leftarrow\alpha+\psi^\top\phi
   $$

   汇总邻域像素信息，更新锚点混合；
4. 直到 $\gamma$ 的变化小于阈值，或达到最大迭代次数。

这对应代码 `online_slda.py` 中 `OnlineLDA.do_e_step` 的核心循环。`slda_minibatch.py` 明确保存稀疏计数、$\psi$、$\phi$ 和 $\gamma$。

### 5. 为什么它能扩展到大数据？

空间耦合只发生在局部邻域。FICTURE 把组织分成有重叠的空间窗口，论文和代码默认窗口边长为 500 µm。每个窗口只输出内部像素和锚点，边缘由相邻窗口负责，减少边界依赖。

输入数据按块读取；不同 minibatch 可以并行处理。这样不需要把整张切片的全部分子同时放入内存，内存消耗主要由固定大小的局部窗口决定。论文因此报告了近似固定的内存预算和随像素数线性增长的运行时间。

### 6. 从输入到输出的完整流程

#### 6.1 数据过滤

不同平台使用不同质量控制：Seq-Scope 去除低密度区和人工标记的组织外区域；Xenium 保留质量分数大于 15 的转录本；Stereo-seq 和 MERSCOPE 使用发布的全部转录本。

#### 6.2 粗尺度因子学习

论文分别使用 24 µm（Seq-Scope）、15 µm（Stereo-seq）和 12 µm（原位平台）的六边形宽度训练 LDA。代码的高层 `run_together` 工作流先生成六边形 DGE，再调用在线 LDA 保存因子×基因模型。

#### 6.3 锚点初始化

论文实验中相邻锚点距离为 4 µm。粗尺度 LDA 被投影到锚点，作为 $\theta_j$ 的初值；随后将初始概率压平，避免粗网格先验过强。

这里存在一个值得注意的版本差异：论文写的是将最小概率下限设为 $0.5/K$，而当前检查的解码代码使用 `0.2/K`。复现论文时应核对历史配置，而不能直接把当前默认值当成论文参数。

#### 6.4 像素解码与输出

解码器流式读取转录本，构建局部像素×基因矩阵，运行上述变分更新，并输出：

- `.pixel.tsv.gz`：每个像素的因子概率；
- `.anchor.tsv.gz`：每个锚点的因子混合；
- `.posterior.count.tsv.gz`：因子×基因的后验计数。

高层工作流还会生成差异表达、因子报告和空间图像。

### 7. 实验结果说明了什么？

论文在模拟数据以及 Seq-Scope、Stereo-seq、Xenium、MERSCOPE 的五个真实数据集上评估。

- 十类细胞模拟中，论文报告 FICTURE 像素准确率为 97.3%，Baysor 为 93.6%，GraphST 为 86.8%。
- 当指定因子数从 10 增加到 20 时，FICTURE 分配给多余因子的像素比例低于 0.1%，表现出较强的模型复杂度鲁棒性。
- 在 1 mm²、每 µm² 四个转录本、500 个基因的示例中，论文报告 FICTURE 使用 1.2 GB、0.23 CPU 小时；Baysor 使用 37 GB、7.3 CPU 小时。
- 图像中，FICTURE 比固定六边形更清楚地恢复结肠壁层次；在胚胎中发现分割遗漏的红细胞/血管结构；在乳腺癌中呈现不规则成纤维细胞和脂肪细胞形态；在肝脏中解析门管区、中央静脉和非实质细胞结构。

这些数值是论文报告结果，本工作区没有重新运行完整 benchmark。

### 8. 如何正确解释 FICTURE 的输出？

FICTURE 的“因子”不一定等于一个细胞类型，也不一定对应一个细胞实例。它可以表示：

- 细胞类型；
- 细胞状态；
- 炎症、纤维化等生物过程；
- 亚细胞转录模式；
- 胞外 RNA 或跨细胞的局部微环境信号。

因此，FICTURE 更像一张高分辨率转录因子地图，而不是传统意义上的细胞轮廓图。在需要细胞计数、膜边界或细胞实例追踪时，仍可能需要分割；在分割不可靠或研究对象是跨细胞空间程序时，FICTURE 更有优势。

### 9. 局限性

- 基础 LDA 假设因子相互独立，没有建模因子相关性和层级结构。
- 因子学习与像素解码分开进行，没有联合优化。
- 因子数 $K$、锚点密度和邻域半径需要用户指定；参数不合适会降低分辨率或导致过度平滑。
- 均值场变分推断可能低估后验方差，使边界像素过度自信。
- 核心模型不使用组织学图像，也不直接生成细胞膜或单细胞实例。

### 10. 代码与复现性

官方 GitHub 仓库的核心代码与论文高度一致：六边形 LDA、锚点投影、距离先验、$\psi/\phi/\gamma$ 更新、空间 minibatch 和像素输出都能在源码中直接对应。当前快照固定在提交 `cb7cb86da22f37adc7e576d41d66e5574c37fc2a`。

复现限制包括：大型真实数据需要外部下载；没有识别出与论文发表版本严格对应的代码标签；论文链接的 Supplementary Text 未转换为本地 Markdown；本工作区没有执行完整 benchmark。综合而言，核心算法可检查、可运行，但精确重现论文全部数值仍需要恢复论文时期的配置和数据环境。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## FICTURE

**Paper:** *FICTURE: scalable segmentation-free analysis of submicron-resolution spatial transcriptomics*
**Venue:** *Nature Methods* 21, 1843–1854 (2024)
**DOI:** `10.1038/s41592-024-02415-2`

### What problem does it solve?

Submicron spatial-transcriptomics assays can place millions to billions of molecules at near-microscopic coordinates, but only a few transcripts are observed per square micrometer. Coarse grids increase counts at the cost of resolution. Cell segmentation can discard or misassign RNA when nuclei are absent, cell shapes are irregular, cells are multinucleated, boundary stains are weak, or transcripts lie outside conventional cell boundaries. The paper reports that 12–55% of transcripts were unassigned in examined segmented datasets.

Prior alternatives had complementary limitations. Baysor (*Nature Biotechnology*, 2022) performs transcript-level clustering/segmentation but becomes expensive for large tissue areas and whole-transcriptome panels. JSTA (*Molecular Systems Biology*, 2021) combines deep learning and watershed segmentation but needs nuclei and a matching single-cell reference. GraphST (*Nature Communications*, 2023) operates after cell segmentation and can oversmooth small or dispersed populations. Sliding-window approaches such as SSAM (*Nature Communications*, 2021) and STtools (*Bioinformatics Advances*, 2022) reduce grid artifacts but repeatedly count overlapping transcripts and constrain downstream analysis choices.

### The proposed method

FICTURE—Factor Inference of Cartographic Transcriptome at Ultra-high REsolution—is a segmentation-free spatial factorization method. It first learns factor-by-gene profiles from transcript counts aggregated into hexagons with ordinary LDA, or accepts factors from another tool or external reference. It then places a dense lattice of overlapping anchors over the tissue. Each pixel probabilistically chooses a nearby anchor according to a distance prior, while each anchor carries a mixture of expression factors. Stochastic variational inference alternates pixel-factor probabilities, pixel-to-anchor probabilities and anchor factor mixtures inside overlapping spatial minibatches.

The important conceptual move is to share sparse information **locally and probabilistically** without committing to a cell boundary. The output is a pixel-resolution factor map that can represent cell types, cell states, biological processes, subcellular programs or extracellular signals.

### Evaluation and findings

The study uses simulations plus five real datasets across Seq-Scope, Stereo-seq, Xenium and MERSCOPE. Visual comparisons show that FICTURE preserves layered colon structure where 24-µm grids are coarse and 12-µm grids are noisy; recovers erythrocyte, vascular, stromal and adipocyte-associated signals missed by segmentation; and maps fine liver zonation and non-parenchymal structures.

In the ten-cell-type simulation, the paper reports pixel-level accuracy of 97.3% for FICTURE, 93.6% for Baysor and 86.8% for GraphST. FICTURE remained stable when the requested number of factors increased from 10 to 20, with less than 0.1% of pixels assigned to excess factors. For a 1-mm² example with four transcripts per µm² and 500 genes, the reported resource use was 1.2 GB and 0.23 CPU hours for FICTURE versus 37 GB and 7.3 CPU hours for Baysor. The figures also show approximately linear runtime with pixels/anchors and a nearly fixed memory envelope over the tested ranges. These numerical results are paper-reported and were not rerun in this workspace.

### Code–paper fidelity

The official GitHub repository is captured at commit `cb7cb86da22f37adc7e576d41d66e5574c37fc2a`. Direct source inspection found a high-fidelity match to the core method:

- the high-level workflow builds hexagonal DGE, trains online LDA, projects factor profiles to anchors and invokes pixel decoding;
- the decoder constructs the paper's distance-decaying pixel-to-anchor support;
- the model explicitly stores and updates the variational parameters $\psi$, $\phi$ and $\gamma$;
- spatial input is streamed through overlapping minibatches, and only patch interiors are retained;
- learned or external factor profiles produce pixel, anchor and posterior-count outputs.

One notable version/configuration difference is that the paper describes flattening initial anchor probabilities to at least $0.5/K$, while the inspected decoder currently uses `0.2/K`. The repository is official but has no manuscript-era tag identified in this analysis.

### Reproducibility

**Rating: 4/5.** The paper, all 16 figures, official source code, generic end-to-end workflow, examples and public data links are available. Core algorithmic behavior is directly traceable from paper equations to source lines. Exact paper reproduction is limited by external large datasets, the absence of a validated manuscript-era code release, the unavailable local Supplementary Text derivation, and the lack of a verified single command reproducing every benchmark panel. The full benchmark was not executed here.

### Limitations

- LDA treats factors as independent and does not model factor hierarchies or correlations.
- Factor learning and pixel decoding are separated rather than jointly optimized.
- Users must choose $K$, anchor density and neighborhood radius; poor choices can reduce accuracy or oversmooth boundaries.
- Mean-field variational inference can be overconfident and underestimate posterior ambiguity.
- The core model does not use histological images and does not produce explicit cell instances or membranes.

Overall, FICTURE is best viewed as a scalable high-resolution **factor map**, not a replacement for every use of cell segmentation. It is especially valuable where segmentation is unreliable or where tissue-scale programs extend across conventional cell boundaries.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
