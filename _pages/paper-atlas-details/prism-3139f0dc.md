---
layout: default
permalink: /paper-atlas/prism-3139f0dc/
title: "PRISM"
nav: false
description: "最关键的工程思想是：RCA 纳米球大小不同，会让所有通道一起变亮或变暗；这种变化主要沿着颜色空间中的“半径”方向。PRISM 不把绝对亮度当作身份，而是用归一化后的方向和第四通道层级来识别条形码。"
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
      <span>Technology Platforms</span>
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>PRISM</h1>
    <p>High-plex spatial RNA imaging in one round with conventional microscopes using color-intensity barcodes</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/HuangLab-PKU/PRISM-Code" target="_blank" rel="noopener noreferrer" aria-label="Open code for PRISM">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PRISM 方法中文解读：单轮颜色强度条形码空间 RNA 成像

### 1. 论文要解决什么问题？

PRISM（profiling of RNA in situ through single-round imaging）针对的是一个很实际的瓶颈：普通荧光显微镜可以可靠区分的光谱通道有限，而传统空间 RNA 成像往往要通过多轮杂交、成像、剥离和重新配准来提高 multiplex。多轮流程需要流体、温控和精确图像配准，也会增加样本形变、耗时和厚组织成像的难度。

论文的核心主张是：不增加显微镜的物理通道数，也可以把“每个通道只有一个 bit 的有/无信号”扩展为“每个通道具有多个可校准的强度等级”。PRISM 用一次成像中的四通道相对强度来编码 RNA 身份；论文展示了 30-plex，并进一步验证最高 64-plex 的设计（`paper.md:36-67,177-189`）。

### 2. 一句话理解

```text
RNA → padlock 探针连接 → RCA 纳米球 → 单轮混合探针竞争染色
   → 四通道强度向量 → 去除亮度尺度 → 颜色空间高斯解码
   → RNA 坐标 → 细胞表达矩阵 → 空间细胞分析
```

最关键的工程思想是：RCA 纳米球大小不同，会让所有通道一起变亮或变暗；这种变化主要沿着颜色空间中的“半径”方向。PRISM 不把绝对亮度当作身份，而是用归一化后的方向和第四通道层级来识别条形码。

### 3. 分子层：怎样把一个基因变成四通道条形码？

#### 3.1 Padlock 探针和 RCA

每个目标基因选择一个 40 nt 的 RNA 靶序列，并把它拆成两个 20 nt 的结合臂。设计时考虑熔解温度、连续 G、转录本覆盖、BLAST 脱靶和二级结构。探针还携带四个 20 nt 的 barcode segment，分别对应四个荧光通道（`paper.md:216-225`）。

探针两端在目标 RNA 上邻接后被连接；Phi29 聚合酶进行 rolling-circle amplification（RCA），在原位产生包含大量重复 barcode 的局部纳米球。这样一次目标 RNA 事件被放大为一个可检测 punctum，同时四个 barcode segment 被重复，便于测量四通道强度。

#### 3.2 选择性扩增

高度表达的基因可能产生过密信号。论文让部分高表达基因的 padlock 与不可复制的对应探针混合，稀释克隆扩增的数量；在生成表达矩阵时再按已知稀释比例校正计数（`paper.md:220-223`）。这是针对动态范围的实验校准，不是从图像中自动学习的去偏模型。

#### 3.3 用荧光/非荧光探针比例制造强度等级

每个 barcode segment 都有一对相同序列的成像探针：一个带荧光标签，一个不带标签。两者按预设比例混合，并一次性把所有探针池化。竞争性结合到 RCA 产物后，带标签探针占比决定该 segment 的预期荧光强度（`paper.md:43-49,225-227`）。

因此，一个 barcode 可以写成四维强度码：

\[
\mathbf b=(b_1,b_2,b_3,b_4),
\]

其中每个 (b_i) 是由探针混合比例实现的离散强度等级，而不只是“有/无”信号。30/31-plex 设计中，前三个通道使用 0–4 级；由于自发荧光，Cy3 这个第四通道在该设计中只使用两个等级。论文指出，实际比例仍需根据光学系统校准。

### 4. 条形码几何：为什么要用 radius vector？

#### 4.1 名义容量

对于 (m) 个通道、每个通道 (n) 个强度等级，论文给出的名义容量是：

\[
n^m-1,
\]

减去全零码。例如三个通道分别取 0、1/4、2/4、3/4、4/4，共有 (5^3-1=124) 个名义组合（`paper.md:50-54`）。

#### 4.2 RCA 尺寸变化造成的混淆

真实 RCA 纳米球大小不完全一致。若一个纳米球只是另一个的两倍，那么 ((0,1,0)) 与 ((0,2,0)) 可能变成相同的颜色方向；绝对强度不同，却难以区分身份。因此，PRISM 把条形码看成颜色空间中的 radius vector，只保留方向角分离足够大的码。

#### 4.3 固定和切平面

30-plex 设计限制前三个整数等级满足：

\[
b_1+b_2+b_3=4.
\]

非负整数三元组的数量是

\[
\binom{4+3-1}{3-1}=15,
\]

正好对应论文所说的 15 个平面交点条形码。第四通道取二值状态后，得到 (15\times2=30) 个码；如果加入第四通道独立端点，则可得到论文所述的 31-plex。这里的组合数是对论文设计的数学解释；代码仓库保存了最终 30-code CSV，但没有找到自动执行 radius-vector 筛选和角度优化的实现。

64-plex 使用更细的前三通道五等分和第四通道三层（0、1、2），不是简单地给 30 个标签追加名字。该设计在论文讨论和 Extended Data Fig. 7–10 中有证据，但当前取得的 `PRISM-Code` 没有对应的 64-code 资产。

### 5. 成像和计算解码

#### 5.1 输入与输出

对每个候选 RNA punctum，输入是四通道强度：

\[
(I_1,I_2,I_3,I_4).
\]

输出包括候选坐标、每通道强度、最可能的基因标签、第二候选标签及其概率/置信度；随后再把 RNA 坐标映射到核或细胞，形成 cell-by-gene 矩阵。

#### 5.2 spot 提取

薄组织：论文使用 top-hat 过滤后的局部极大值；厚组织：使用 3D 局部极大值和 Airlocalize 高斯拟合。四个通道的候选坐标被合并，每个坐标读取四维强度。之后进行光谱串扰校正、通道均值归一化，并过滤总强度过低的点（`paper.md:261-266`）。

代码对应关系：

- `PRISM-Code/scripts/readout.py:99-220,227-352` 合并通道候选坐标、读取强度，并输出位置/强度表；
- `PRISM-Code/prism/readout/intensity_readout.py:15-66` 对 top-hat 结果取局部最大强度；
- `PRISM-Code/prism/readout/spot_detection.py:404-511` 同时保留传统 top-hat/高斯检测和 Spotiflow 路径；但 `configs/readout.yaml:10-35` 的默认 detector 是 Spotiflow，所以与论文薄片默认描述属于 **Partial**，不是无条件 Exact。

#### 5.3 L1 投影：去掉 RCA 亮度尺度

定义前三通道之和：

\[
S=I_1+I_2+I_3.
\]

把前三通道投影到固定和的平面：

\[
p_1=I_1/S,\quad p_2=I_2/S,\quad p_3=I_3/S.
\]

论文使用的颜色空间坐标是：

\[
x=(I_1-I_2)/S,\qquad
y=2I_3/S-1,\qquad
z=I_4/S.
\]

如果 RCA 尺寸把所有通道同时乘以 (a>0)，上述比例基本不变；因此，投影抛弃了主要的径向亮度变化，保留了条形码方向。前三通道给出 15 个平面簇，第四通道把它们分成不同层。

代码中，`prism/gene_calling/codebook_gmm_method.py:98-127` 计算 color-sum ratio 和第四通道层特征；`prism/gene_calling/gmm_method.py:344-418` 也构建归一化投影和层相关特征。这是当前仓库中最明确的 **Exact** 方法对应，但代码内部的通道列名与论文的 Ch1–Ch4 记号并不完全相同。

#### 5.4 高斯分类和置信度

论文把投影后的点看成 15 个高斯样式的分布，再与第四通道层组合成约 30 个簇。端点码本来接近颜色空间边界上的点，论文会加入小方差，使端点也可以用相同的高斯框架评估。初始 gene calling 按属于某簇的置信度阈值过滤；进一步可以手动划定 3D 边界，再直接赋码或在边界内重新拟合高斯（`paper.md:267-272`）。

代码中有两个相关实现：

1. `CodebookGMMMethod` 用 codebook 初始化高斯中心，再拟合和输出标签概率；
2. `GMMMethod` 先处理第四通道层，再在投影空间内拟合分层高斯模型。

对应代码为 `prism/gene_calling/codebook_gmm_method.py:129-218,221-256`、`prism/gene_calling/gmm_method.py:420-602` 和 `prism/gene_calling/base.py:12-64`。手动颜色空间边界则只在 `notebooks/gene_calling_manual_2d.ipynb` 中看到，因此标记为 **Notebook**。

### 6. 从 RNA 坐标到细胞和空间生物学

薄组织中，DAPI 图像先做自适应阈值，随后进行欧氏距离变换和 watershed，得到核区域和核质心。每个解码 RNA 通过 k-d tree 分配给最近核质心，生成 cell index 与 cell-by-gene 矩阵。厚组织使用 StarDist 进行 3D 核分割（`paper.md:305-310`）。

当前代码的对应关系需要谨慎描述：

- `unified_segmentation.py:102-143,307-393` 和 `scripts/segment_dapi.py:15-68` 直接覆盖自适应阈值、距离变换、watershed 和 StarDist 调度；
- 最近质心和表达矩阵构建只在 `scripts/legacy/segment_cell_2D.py:11-36`、`segment_cell_3D.py:48-135` 中找到；它们读取的 `mapped_genes.csv` 与维护 gene-calling 输出的 `mapping.csv` 接口不一致，因此是 **Partial/legacy**；
- `cell_typing_and_analysis.ipynb` 的 Harmony、Leiden、Squidpy 单元格属于 **Notebook**，而且从预计算 expression matrix 开始，并使用外部模块和本地 Windows 路径；
- GASTON 与 STAGATE 在当前取得的 `PRISM-Code` 中 **Not found**。论文代码可用性说明把 post-gene-calling 分析指向另一个 `PRISM-Analysis` 仓库（`paper.md:395-404`）。

所以，Figure 2–6 的生物学图表不能简单等同于当前公开 snapshot 的一键输出。它们还依赖下游分析仓库、实验数据、配置和人工注释。

### 7. 论文验证了什么？

论文把错误拆成两个阶段：RNA → RCA 纳米球的扩增准确性，以及纳米球颜色 → 基因标签的解码准确性。

- smFISH 共定位实验报告 RCA 信号与 smFISH 的共定位超过 90% 或 95%；
- 独立并行实验估计单个 RCA 探针的灵敏度约 21%；
- 与 RNAscope 比较时，PRISM/RNAscope 计数比例按不同分母为 9.4%、15.8% 和 11.5%；
- 30-plex 脑组织 false decoding 约 4.33%；64-plex 脑和胚胎分别为 4.20% 和 2.40%（`paper.md:273-302`）；
- 30-plex 例子报告超过 80% spot retention 和 95.7% decoding accuracy；64-plex 脑/胚胎报告 95.8%/97.6% 准确率（`paper.md:61-67,177-189`）。

这些数字不能混成一个“总体准确率”：高特异性是在保留下来的点和特定阈值下测得的，而 RCA 捕获灵敏度仍明显低于 smFISH。论文讨论把 PRISM 灵敏度概括为约 10%，而不是宣称完整捕获所有转录本。

### 8. 图像证据如何支持方法？

- **Fig. 1 / Extended Data Figs. 1–3：** 直接展示条形码分子设计、radius-vector 筛选、固定和投影、Gaussian cluster 与置信度/保留率权衡。
- **Fig. 2–3：** 展示全胚胎、细胞类型、共表达和跨切片 atlas 的规模；这些图支持空间应用，但不单独证明因果调控。
- **Fig. 4–5：** 展示 HCC 的 UMAP、肿瘤—基质—免疫空间结构、CAF 屏障和准 3D 组织；GASTON/STAGATE 属于下游分析，当前代码 snapshot 中没有对应实现。
- **Fig. 6 / Extended Data Fig. 6：** 用 100 µm 脑组织和深度剖面检验强度比例对轴向衰减的容忍度；它支持可行性，不代表任意厚度都能保持同等信号质量。
- **Extended Data Figs. 5, 7, 9, 10：** 用 strip–rehybridization 和 64-plex 数据验证错误率、容量扩展与保留率。

### 9. 可复现性结论

本 workspace 的 code–paper match 是 **Medium**，可复现性评分为 **3/5**。

#### 已验证（Exact）

多通道 spot/intensity 读取、L1/ratio 特征、30-code CSV、高斯解码、标签概率输出和 2D watershed 都有直接源代码证据。

#### 部分验证（Partial）

传统 top-hat 并非默认检测器；通道校正矩阵和 channel rename/classifier 接口存在静态不一致；StarDist 训练模型资产未随 snapshot 提供；最近质心 RNA 分配仍是 legacy 路径。

#### 仅 Notebook / 缺失

手动颜色边界、Harmony/Leiden、Squidpy 只在 notebook 中出现。上游 focal-stack、CIDRE、FFT 配准、MIST/手动拼接由仓库 README 说明为未公开 companion；GASTON、STAGATE、64-code 配置在当前 `PRISM-Code` 中没有找到。没有执行 pipeline，因此配置问题是静态审计发现，不是运行时失败报告。

### 10. 解读边界与可检验假设

**论文结论：** PRISM 证明了在一次成像中使用颜色强度条形码，可以在常规显微镜上完成几十种目标 RNA 的空间识别，并能应用于薄组织、连续切片和 100 µm 厚脑组织。

**代码支持的解读：** 公共代码最完整地体现了“强度向量 → 比例/层特征 → 概率高斯分类”这一核心计算抽象，而不是完整的原始图像到生物学结论流程。

**可检验假设（不是论文结果）：** 如果用真实通道协方差、深度依赖噪声和串扰矩阵联合优化码本，而不是只按几何角度均匀增加等级，可能在相同 false-decoding 率下提高 spot retention。另一个工程假设是统一 correction、classifier 和 RNA assignment 的配置接口，会显著改善当前公开 snapshot 的可复现性。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PRISM: High-plex spatial RNA imaging in one round

**Paper:** *High-plex spatial RNA imaging in one round with conventional microscopes using color-intensity barcodes*, *Nature Biotechnology* (2025), DOI `10.1038/s41587-025-02883-7`.

### Problem

Conventional fluorescence microscopes distinguish only a few spectral channels. Imaging-based spatial transcriptomics therefore commonly increases multiplexity through repeated labeling, imaging, and stripping cycles or through specialized optical modalities. Those approaches add fluidics, temperature control, registration burden, experiment time, and difficulty in thick tissue.

### Proposed technology

PRISM—profiling of RNA in situ through single-round imaging—encodes RNA identity in the **relative intensities** of four fluorescence channels. Target-bound padlock probes are ligated and amplified by rolling-circle amplification (RCA). Each repeated barcode segment is stained by a preset mixture of labeled and unlabeled imaging probes, so competitive binding produces a designed channel intensity. All imaging probes are pooled and read in one staining/imaging round on a conventional microscope.

The key coding insight is to represent the first three channel levels as radius-vector directions. Absolute brightness changes with RCA nanoball size, but proportional channel scaling preserves direction. PRISM selects well-separated codes on the plane

\[
Ch1+Ch2+Ch3=4,
\]

yielding 15 integer codes, then uses a binary fourth-channel level to obtain 30 codes. Measured spots are L1-normalized by the first-three-channel sum and decoded as Gaussian-like clusters in a ratio/layer color space. A finer first-three-channel grid plus three fourth-channel levels supports the demonstrated 64-plex design.

### Workflow at a glance

```text
RNA target
  -> padlock hybridization and ligation
  -> localized RCA nanoball
  -> pooled competitive intensity staining
  -> four-channel image and spot extraction
  -> crosstalk/scale correction
  -> ratio-space projection
  -> Gaussian/confidence gene calling
  -> nucleus segmentation and RNA-to-cell assignment
  -> cell typing and spatial analysis
```

### Main evidence reported by the paper

- The 30-plex demonstration forms 30 color-space clusters, retains more than 80% of spots at the selected confidence threshold, and reports 95.7% decoding accuracy.
- Orthogonal strip–rehybridization validation reports false-decoding rates of 4.33% for 30-plex mouse brain, 4.20% for 64-plex brain, and 2.40% for 64-plex embryo data—equivalent to 95.8% and 97.6% accuracy for the two 64-plex experiments.
- A sampled E12.5–E14.5 mouse embryo atlas comprises 26 sections, 4,257,418 cells, and 107,655,795 transcripts.
- Twenty consecutive HCC sections yield a quasi-3D tumor–normal landscape with 1,218,279 cells and 32 clusters, highlighting CAF-associated barriers and immune heterogeneity.
- A 100-µm mouse brain slice demonstrates intact-tissue 3D decoding, cell typing, and subcellular RNA localization.

The paper separates specificity from sensitivity. RCA–smFISH colocalization exceeds 90% or 95% in two validation protocols, but standalone single-padlock RCA sensitivity is reported near 21%. PRISM/RNAscope count ratios are 9.4–15.8% depending on the denominator, and the Discussion characterizes PRISM sensitivity as about 10%, notably lower than smFISH. High decoding accuracy therefore does not imply complete transcript capture.

### What is novel and useful

PRISM spends fluorescence dynamic range as an encoding dimension. Its normalization makes codes relatively insensitive to multiplicative brightness variation, while the fourth channel provides a coarse layer index. This enables dozens of identities in one image without cyclic fluidics and makes whole-section, consecutive-section, and thick-tissue experiments accessible to laboratories with conventional fluorescence equipment.

The most promising use cases are targeted spatial atlases, tumor microenvironment mapping, validation of known marker panels, and experiments where cycle-to-cycle registration or reagent exchange is especially undesirable. PRISM is targeted rather than transcriptome-wide: panel design and probe calibration remain central experimental decisions.

### Limitations

- Multiplexity is bounded by angular code separation, spectral crosstalk, optical registration, tissue autofluorescence, and spot crowding rather than by nominal combinatorics alone.
- Single-color endpoint codes have elevated false-call risk under color aberration or spot splitting.
- Manual color-space boundaries can improve purity but introduce analyst dependence.
- RCA-based capture sensitivity is substantially below direct single-molecule methods in the reported comparisons.
- Serial-section “3D” HCC reconstruction depends on manual anchors and affine alignment and is not equivalent to intact isotropic volume imaging.
- Exact probe-mixing ratios, selective-amplification dilutions, and other supplementary-only calibration details were not available in the acquired Markdown evidence.

### Code and reproducibility assessment

**Workspace reproducibility rating: 3/5; code–paper fidelity: Medium.** The paper provides Zenodo raw/analysis data and public repositories. The acquired `PRISM-Code` snapshot directly implements meaningful post-stitching components: multichannel spot/intensity readout, ratio-feature construction, Gaussian gene calling, the 30-code codebook, probabilities, watershed segmentation, and StarDist dispatch.

It is not an end-to-end reproduction. The repository states that upstream stacking, illumination correction, registration, and stitching code is not public. RNA-to-cell assignment is only in legacy scripts; downstream post-calling analysis is assigned by the paper to a separate `PRISM-Analysis` repository that was not acquired; and the shipped configuration/channel interfaces contain static inconsistencies. The analysis notebooks use precomputed inputs and hard-coded external/local paths. No pipeline execution was performed during this Author phase.

### Bottom line

The paper provides strong experimental evidence that intensity-ratio barcodes can deliver 30–64 targeted RNA identities in one imaging round with low false-decoding rates across thin and 100-µm tissues. The central decoding idea is visible and substantially implemented in public code. Reproduction from raw images to every biological figure still requires additional upstream, downstream, model, calibration, and configuration work.

**Interpretive hypothesis, not a paper result:** empirically optimizing code positions against channel covariance and depth-dependent noise may improve spot retention at a fixed false-decoding rate more effectively than increasing intensity divisions uniformly.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
