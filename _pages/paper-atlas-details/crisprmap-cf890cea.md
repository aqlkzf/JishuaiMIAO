---
layout: default
permalink: /paper-atlas/crisprmap-cf890cea/
title: "CRISPRmap"
nav: false
description: "pooled CRISPR 筛选的核心任务，是把“这个细胞受到了哪个遗传扰动”与“这个细胞呈现了什么表型”对应起来。 Perturb-seq（Cell, 2016）和 CROP-seq（Nature Methods, 2017）把 CRISPR 扰动与单细胞转录组连接起来，能看到大量 RNA 变化，但需要分离并裂解细胞，因此会丢失细胞形态、蛋白质亚细胞定位、邻近细胞关系和组织结构。"
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
      <span>Perturbation Resources</span>
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>CRISPRmap</h1>
    <p>Mapping multimodal phenotypes to perturbations in cells and tissue with CRISPRmap</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CRISPRmap 方法详解

### 1. 它要解决什么问题？

 pooled CRISPR 筛选的核心任务，是把“这个细胞受到了哪个遗传扰动”与“这个细胞呈现了什么表型”对应起来。

Perturb-seq（*Cell*, 2016）和 CROP-seq（*Nature Methods*, 2017）把 CRISPR 扰动与单细胞转录组连接起来，能看到大量 RNA 变化，但需要分离并裂解细胞，因此会丢失细胞形态、蛋白质亚细胞定位、邻近细胞关系和组织结构。经典 optical pooled screening（OPS，*Cell*, 2019；标准化协议发表于 *Nature Protocols*, 2022）保留了图像表型，却依赖原位测序、逆转录和 gap-fill 等循环酶促步骤，在多能干细胞、神经元等难处理细胞中条形码检出率较低，也不易与大规模蛋白和 RNA 成像整合。

CRISPRmap 的目标是：

> 不做原位测序，而是用组合杂交直接读出与 sgRNA 配对的 RNA 条形码，并在同一个细胞中同时测量蛋白、RNA、细胞形态、亚细胞定位和组织空间信息。

### 2. 核心创新：把条形码变成一个“四输入 AND 门”

每个 CRISPRmap 条形码由两个相邻的 30 bp 杂交区组成，分别结合 primer oligo 和 padlock oligo。primer 与 padlock 各携带两个 20 nt readout sequence，总共形成四个 readout 身份。

```text
条形码 RNA
  ├─ primer 与第一个相邻区域结合
  ├─ padlock 与第二个相邻区域结合
  ├─ splint 1 连接一侧 readout 接口
  └─ splint 2 连接另一侧 readout 接口
          ↓ T4 DNA ligase
     形成可扩增的闭环模板
          ↓ rolling-circle amplification, RCA
     产生包含四种 readout 身份的亮点
          ↓ 多轮荧光探针杂交/成像/剥离
     得到跨轮次、跨通道的二进制条形码
```

这个设计的关键不只是“放大信号”，而是“检查组合是否合理”：

- padlock 自连接时会缺少 primer 上的 readout；
- 错误的 primer–padlock 配对会形成不在允许 codebook 中的组合；
- 只有 primer、padlock 和两个 splint 同时正确存在，才能产生完整合法的信号。

因此，CRISPRmap 把化学反应本身变成了一个 AND 逻辑门。它也不需要经典 OPS 中的逆转录和 gap-fill，作者认为这有助于提高检出效率并减少循环酶促步骤。

### 3. 从图像到 guide identity 的计算流程

#### 3.1 输入与输出

输入包括：

- 多轮、多通道、带 z-stack 的显微图像；
- DAPI 与细胞膜/EPCAM 等分割标记；
- 每个 sgRNA 对应的预设计二进制 codebook；
- 可选的抗体、RNAmap 和组织标记通道。

主要输出是一个单细胞表：每行对应一个细胞，包含 guide identity、条形码 QC、蛋白强度、DDR foci 数量、细胞周期、RNA spot 数量和空间特征。

#### 3.2 图像缩放与跨轮次配准

不同成像轮次可能存在两类位移：培养板整体放回显微镜时产生的全局平移，以及细胞在循环处理中的局部移动。CRISPRmap 先对 z 轴做最大投影，并用双三次插值统一像素尺寸，然后在 DAPI 二值核图上计算 TV-$L1$ optical flow，得到每个像素的位移场 $(v,u)$。同一轮次所有通道都使用同一个位移场变换。

这一部分在公开代码中得到直接验证：`Image-rescaling-and-Registration.ipynb` 调用 `optical_flow_tvl1`，对各通道执行 warp，并计算互相关作为配准质量指标。

#### 3.3 双重 Cellpose 分割

作者分别运行两次 Cellpose：

1. 用细胞膜/EPCAM 与 DAPI 得到细胞质/细胞边界；
2. 只用 DAPI 得到细胞核边界。

随后删除没有核的细胞 mask 和没有细胞 mask 覆盖的核，将每个细胞与一个核配对。公开 notebook 将这些信息保存到 `ref_mem`：其中包含细胞像素、核像素、核 ID 等，是后续“spot 属于哪个细胞”的数据接口。

#### 3.4 spot 检测与多轮条形码拼接

对每一张 round–channel 图像，算法先增强对比度，再检测亮点，只保留落在细胞 mask 内的 spot。多个轮次中距离足够近的 spot 被视为同一个 RCA amplicon。

对 amplicon $a$，可以把每个成像轮次 $r$、通道 $c$ 的结果写成：

$$
b_a(r,c)=
\begin{cases}
1,&\text{该 round–channel 在指定半径内检测到 spot},\\
0,&\text{否则。}
\end{cases}
$$

GFP pilot 使用 2 通道 × 4 轮，即 8-bit code；DDR364 使用 3 通道 × 8 轮，即 24-bit code。公开 DDR notebook 使用 2.01 像素的跨轮次关联半径，并通过 `np.array_equal` 将观察到的 24-bit 向量与 codebook 逐行精确匹配。这意味着公开实现没有模糊匹配或纠错：bit pattern 必须完全等于某个 guide 的设计码。

#### 3.5 从 amplicon identity 聚合到 cell identity

一个细胞中可能包含多个属于同一 guide 的 RCA spot，也可能因为分割边界重叠而混入邻近细胞的少量 spot。定义：

- `max_spot`：该细胞中数量最多的 guide-reporting spot 数；
- `second_max_spot`：第二多的 guide-reporting spot 数。

纯度为

$$
\mathrm{Purity}=\frac{\mathrm{max\_spot}}{\mathrm{max\_spot}+\mathrm{second\_max\_spot}}.
$$

标准 QC 要求

$$
\mathrm{max\_spot}\ge 3,
\qquad
\mathrm{Purity}\ge 0.66.
$$

论文写 0.66，公开代码使用 0.67，属于数值取整差异。通过 QC 后，数量最多的 barcode 所对应的 guide 被赋给该细胞。这个“多个 spot 投票 + 纯度”设计，是 CRISPRmap 抵御分割误差的重要技巧。

### 4. 同一个细胞中测量哪些表型？

CRISPRmap 与 IBEX 式循环免疫荧光、RNAmap 结合，主要提取：

- RAD51、BRCA1、RPA2、γH2AX、53BP1、RAD18 等 DDR foci；
- Ki-67、cyclin A2、cyclin B1、p-Histone H3 等细胞周期标记；
- p21、p53、cleaved PARP1 等应激/凋亡相关信号；
- 核、胞质和全细胞平均荧光强度；
- micronuclei 数量；
- 12 个 RNAmap 转录本的 spot 数；
- 组织中的克隆邻域、血管/坏死相关 void 和细胞外基质标记。

RNAmap 复用了 primer–padlock–RCA 框架，但针对内源 RNA：每个基因使用多对检测 oligo，并通过 GC、Tm、局部 BLAST、二级结构和空间重叠等规则选择 probe。论文使用 FISHprobe R 包；工作区中的辅助源码可以验证 FISHprobe 对象和 probe reverse-complement 生成，但完整的 CRISPRmap/RNAmap 特异性设计流程并未以一个可直接运行的脚本发布。

### 5. 如何从单细胞表型得到 guide/variant 结论？

#### 5.1 连续 foci 特征

对每个 guide 和 treatment，作者把该 guide 的 foci count 分布与 AAVS1/NTC control cells 比较：

- 两侧 Kolmogorov–Smirnov test；
- 计算平均 foci 数的 log$_2$ fold change；
- Benjamini–Hochberg 校正；
- 命中条件：$P_{\mathrm{adj}}<0.05$ 且 $|\mathrm{L2FC}|>0.5$。

#### 5.2 用 Wasserstein distance 缓解细胞数不平衡

不同 guide 的细胞数不相等，因此作者从每个 guide 随机抽取 $S=50$ 个细胞，重复 $N=200$ 次，计算与 control 分布之间的平均 1-Wasserstein distance：

$$
W(g_i,j)=\frac{1}{N}\sum_{n=1}^{N}
W_1\!\left(
X_{\{g_i^{(1)},\ldots,g_i^{(S)}\},j},
X_{\{c\},j}
\right).
$$

这一步不是替代 KS/L2FC，而是检查 hit 是否在控制样本量偏差后仍与 control 有明显分布距离。

#### 5.3 二元特征的 beta-binomial test

对于“p21 高表达/低表达”这类阈值化特征，guide $i$ 有 $n_i$ 个细胞，其中 $k_i$ 个为 positive。作者用 control guides 拟合：

$$
p_i\sim\mathrm{Beta}(\alpha,\beta),
$$

$$
k_i\sim\mathrm{Binomial}(n_i,p_i).
$$

Beta 层用于吸收不同 control guide 之间的过度离散。$\alpha,\beta$ 由最大似然估计，test guides 的双侧 $P$ 值再做 BH 校正。

#### 5.4 多变量光学签名聚类

作者把多个 treatment、多个 DDR foci、micronuclei 等特征的 L2FC 组合起来，对 variants 做层次聚类。真正的目标不是只找“某一个 foci 显著”的 guide，而是比较一个变体在多种 DNA damage 条件下的整体反应模式。

因此，一个 missense VUS 如果与已知致病的 splice/nonsense variants 共享相似的多维光学签名，就会被优先标记为可能功能受损。这里的结论是“功能优先级/机制相似性”，不能仅凭该聚类直接完成临床致病性重分类。

### 6. 主要实验结果

- GFP pilot 中，四个 readout 都为阳性的 amplicon 有 98% 属于允许组合；标准 QC 保留 76% 的细胞，中位数为每细胞 11 个 guide-assigned amplicons。
- 在 hESC、iPSC 和 iPSC-derived motor neuron 中，CRISPRmap 的 barcode detection 明显高于 conventional OPS。
- irradiation 数据有 226,369 个通过 QC 的细胞；合并 irradiation 与四种 DNA-damaging drugs 后共有 948,604 个通过 QC 的细胞。
- RNAmap 与 bulk RNA-seq 的总体相关为 $r=0.84$。
- 高 RS2 的 BRCA1/BRCA2/RAD51 相关 nonsense 或 splice guides 产生预期的 RAD51/BRCA1 foci 下降；pooled 与 individual validation 的 L2FC 相关分别为 $r=0.90$ 和 $r=0.95$。
- BRCA1 H1283Y 等 missense VUS 的多变量光学签名与 pathogenic-like variants 聚类在一起。
- OE19 xenograft 可在组织中读出 barcode：56% 的 segmented cells 通过 barcode QC，中位数为 14 个 barcode spots/cell，并能与多轮蛋白染色和空间克隆区域叠加。

### 7. 代码能复现到什么程度？

代码—论文一致性为 **medium**：

- **直接匹配：** TV-$L1$ 配准、Cellpose 双分割、24-bit exact codebook matching、细胞级 spot/purity QC。
- **部分匹配：** 论文写 difference-of-Gaussians，而 canonical amplicon/foci notebooks 实际使用 `blob_log`（Laplacian-of-Gaussian）。
- **Not found：** KS/BH、Wasserstein、beta-binomial、foci co-localization、tissue void 和 10-nearest-neighbor clonality 的实现。
- **工程限制：** 代码以旧版、实验特异的 Jupyter notebooks 为主，包含绝对路径，没有端到端 runner、测试或完整统计脚本。

因此，公开仓库足以理解和重建“图像 → barcode → guide assignment”的核心逻辑，但不足以直接从原始数据一键重现论文全部统计图和组织分析。

### 8. 如何理解 CRISPRmap 的真正价值

CRISPRmap 最重要的不是单独发明了某个图像算法，而是把多个环节组合成一个保留空间信息的筛选系统：

```text
遗传扰动
  + 可光学读取的冗余 RNA barcode
  + 亚细胞分辨率蛋白/RNA表型
  + 单细胞 guide assignment
  + treatment-specific 多变量分析
  = 在细胞和组织空间中绘制“扰动—表型”映射
```

它的优势在于同时观察“发生了什么、发生在哪里、在哪类细胞/细胞周期中发生、周围组织是什么状态”。代价是实验周期、图像处理和 QC 都较复杂，而且完整计算复现仍依赖论文中描述但未公开的统计代码。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## CRISPRmap Summary

### Problem

Pooled CRISPR screens need to connect each cell's perturbation with its phenotype. Perturb-seq (*Cell*, 2016) and CROP-seq (*Nature Methods*, 2017) provide rich single-cell transcriptomic readouts, but cell isolation and lysis remove morphology, subcellular protein localization, cell–cell interactions and tissue organization. Conventional optical pooled screening (*Cell*, 2019; *Nature Protocols*, 2022) preserves images but relies on in situ sequencing chemistry that can perform poorly in difficult cell types and is cumbersome to combine with highly multiplexed protein and RNA phenotyping.

### Proposed Method

CRISPRmap is a sequencing-free optical pooled screening method that couples an sgRNA to an expressed two-part RNA barcode. Adjacent primer and padlock oligos bind the barcode; four readout sequences distributed across those oligos, two splints and T4 ligation form an AND gate before rolling-circle amplification. Cyclic fluorescent probe hybridization converts each amplicon into an 8-bit pilot or 24-bit DDR-library code. Registered images are segmented, spots are associated across cycles, codes are matched to a guide codebook and each cell receives the dominant guide only if it has at least three matched amplicons and sufficient barcode purity.

The same fixed cells are profiled by cyclic immunofluorescence and RNAmap, an adaptation for endogenous transcripts. This yields per-cell guide identity together with protein intensities, subcellular localization, DDR foci, micronuclei, cell-cycle state and transcript counts. Downstream analyses use KS tests with Benjamini–Hochberg correction, L2FC, bootstrapped Wasserstein distance, beta-binomial tests and hierarchical clustering to identify perturbation-specific optical signatures.

### Evaluation and Main Results

- In the GFP pilot, 98% of amplicons positive for four readout probes corresponded to allowed primer–padlock combinations. Standard QC retained 76% of cells, with a median of 11 guide-assigned amplicons per cell, and GFP-targeting guides produced the expected loss of GFP signal.
- CRISPRmap recovered substantially more barcode-positive cells than conventional OPS in hESCs, iPSCs and iPSC-derived motor neurons, while also working in fibroblasts and HT1080 cells.
- The DDR364 screen profiled 226,369 QC-passing cells in the irradiation experiment and 948,604 cells across irradiation plus four DNA-damaging drugs. RNAmap abundance correlated with bulk RNA-seq at $r=0.84$.
- Expected DDR biology was recovered: high-activity nonsense/splice guides in BRCA1, BRCA2 and RAD51-related genes reduced RAD51 or BRCA1 foci. Pooled versus individually transduced effects correlated at $r=0.90$ for RAD51 and $r=0.95$ for BRCA1.
- Multivariate optical signatures separated many damaging splice/nonsense variants from milder missense variants and prioritized selected VUSs, including BRCA1 H1283Y, whose profile clustered with pathogenic-like BRCA1 variants. This is functional prioritization evidence, not by itself clinical reclassification.
- In a Cas9-negative OE19 xenograft pilot, 56% of segmented cells passed barcode QC, the median was 14 detected barcodes per cell and spatially coherent clonal domains could be overlaid with multiplexed tissue markers.

### What Is Novel

The main contribution is the combination of four properties in one workflow: sequencing-free guide identification, redundant AND-gated barcode chemistry, same-cell protein/RNA/spatial phenotyping and applicability to difficult cultured cells and tissue. The approach preserves spatial information that sequencing-based screens discard while avoiding reverse transcription and gap-fill steps used by conventional OPS.

### Limitations

- Barcode readout depends on RNA stability, especially in tissue.
- RNAmap detection efficiency is lower than traditional smFISH, trading molecular sensitivity for amplification, speed and screen scale.
- Cell segmentation and purity thresholds materially affect how many cells pass QC; tissue morphology and small/non-cancer cells are particularly difficult.
- The variant screens use MCF7-BE3 cells and guide effects depend on base-editing efficiency, treatment, cell cycle and RS2 filtering.
- The tissue study is a barcode-readout feasibility experiment rather than an in vivo perturbation-effect screen; the observed guide distribution is strongly skewed.

### Reproducibility

**Rating: 3/5.** The paper provides raw imaging data through BioImage Archive `S-BIAD985`, detailed supplementary tables and a canonical GitHub repository. The acquired commit directly supports TV-$L1$ registration, Cellpose segmentation, binary codebook matching and cell-level guide QC. However, the release is a set of old, path-specific notebooks with no portable end-to-end runner or tests. The notebooks use Laplacian-of-Gaussian spot detection where the paper states difference-of-Gaussians, and implementations of KS/BH hit calling, Wasserstein distance, beta-binomial testing, foci co-localization, tissue void classification and clonality analysis were `Not found`. The optical decoding core is inspectable, but complete figure-level reproduction requires reconstructing missing orchestration and statistics.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
