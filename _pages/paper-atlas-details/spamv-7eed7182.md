---
layout: default
permalink: /paper-atlas/spamv-7eed7182/
title: "SpaMV"
nav: false
description: "同一个空间位置可以同时测到转录组、表观组、蛋白组或代谢组。传统整合常把所有模态压到一个统一表示里，这适合找共同组织结构，却可能把只在某个模态中清楚的生物信号当成噪声。SpaMV 的核心假设是：每个 spot 的观测由一部分跨模态共享状态和每个模态自己的私有状态共同产生。 因此，对第 i 个模态 xi，模型学习一个共享变量 zs 和一个私有变量 z{pi}。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>SpaMV</h1>
    <p>Interpretable spatial multi-omics data integration and dimension reduction with SpaMV</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2025.08.02.668264" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpaMV：把空间多组学拆成共享信息与模态私有信息

### 它解决的不是普通“对齐”问题

同一个空间位置可以同时测到转录组、表观组、蛋白组或代谢组。传统整合常把所有模态压到一个统一表示里，这适合找共同组织结构，却可能把只在某个模态中清楚的生物信号当成噪声。SpaMV 的核心假设是：每个 spot 的观测由一部分跨模态共享状态和每个模态自己的私有状态共同产生。

因此，对第 $i$ 个模态 $x_i$，模型学习一个共享变量 $z_s$ 和一个私有变量 $z_{p_i}$。它提供两种用途：domain clustering 模式把共享与全部私有嵌入拼在一起做空间域划分；topic modeling 模式让每个潜在维度对应可读的空间主题，并用特征—主题权重解释哪些基因、peak、蛋白或代谢物支持该主题。论文的模型概览和两种模式见 `paper source/paper/auto/paper.md:198-218`，Fig. 1 给出整套结构图。

### 输入、图和编码器

输入要求各模态观察相同且已对齐的 spot。每个模态保留自己的 spot×feature 矩阵，并建立自己的邻接图。论文描述的图同时连接空间邻近位置和数据空间中的近邻；代码入口 `SpaMV/spamv.py:200-205` 调用 `adjacent_matrix_preprocessing`，默认 `neighborhood_depth=2`、`neighborhood_embedding=10`。这意味着表示既受到局部组织连续性的平滑，也会吸收分子特征相似的远端 spot。

每个模态有两条独立编码支路：共享编码器输出 $q_{\phi_{s_i}}(z_s\mid x_i)$，私有编码器输出 $q_{\phi_{p_i}}(z_{p_i}\mid x_i)$。topic 模式的编码器是两层 GATv2，输出均值与正尺度（`SpaMV/layers.py:6-18`）；clustering 模式使用 PyG `GAT`。源码在 `SpaMV/model.py:47-69` 为每个模态分别创建 shared/private encoder，故这里不是一个编码器简单切分向量。

代码导出最终共享嵌入时，实际对各模态共享编码器的后验均值做算术平均：

$$
\hat z_s=\frac{1}{M}\sum_{i=1}^{M}\mu_{s_i}.
$$

见 `SpaMV/model.py:261-266`。论文把共享整合称作 mixture of experts，但当前实现的输出聚合可具体理解为“均值专家”，不是一个额外学习的门控网络。

### 两种重构如何把信息推到正确的位置

若只让 $[z_s,z_{p_i}]$ 重构自己的模态，共享变量可能吞掉全部信息，私有变量也可能复制公共信号。SpaMV 同时使用 self reconstruction 和 cross reconstruction。

自重构第 $i$ 个模态时，代码使用

$$
[\operatorname{sg}(z_{s_i}),z_{p_i}]\rightarrow \hat x_i,
$$

其中 `sg` 是 stop-gradient。`SpaMV/model.py:155-160` 对 `zss[i]` 调用 `detach()`，使自重构误差不能继续优化共享编码器，只能迫使私有变量保留本模态剩余信息。

跨模态重构 $x_j$ 时，则使用从模态 $i$ 推断的 $z_{s_i}$，再配一个不携带 $x_j$ 信息的辅助私有变量：

$$
[z_{s_i},r_j]\rightarrow \hat x_j,\quad i\ne j.
$$

非解释模式的 $r_j$ 从零均值高斯抽样；topic 模式当前代码直接使用全零向量（`model.py:143-162`）。因此跨重构只能主要依赖共享表示。这个“topic 模式辅助私有向量为零”是实现细节，不能泛化成论文所有理论推导都固定为零。

### 怎样阻止共享信息泄漏到私有变量

对每一对 $i\ne j$，SpaMV 训练一个两层 measurement MLP $M_i^j(z_{p_i})$，尝试从模态 $i$ 的私有变量预测模态 $j$。测量模型自己最小化预测误差；主模型则最小化其输出在 spot 间的变化。直觉是：如果 $z_{p_i}$ 不含另一个模态的信息，最优预测器只能反复输出近似总体均值，其输出方差应很小。

`SpaMV/layers.py:52-90` 实现所有跨模态 MLP；`SpaMV/spamv.py:242-259` 周期性重新初始化和训练它们，`spamv.py:344-359` 把输出标准差作为主模型惩罚。这里的实际目标不是严格计算互信息，而是用一个有限容量预测器的可预测性作为代理。因此“私有”表示相对于当前数据、网络和训练达到较低跨模态可预测性，并不构成数学上的可识别性证明。

论文 Methods 写 domain clustering 在第 200 次迭代、topic modeling 在第 10 次开始训练 measurement model（`paper.md:319-323`）。当前提交的代码恰好相反：`self.pretrain_epoch = 200 if interpretable else 10`（`spamv.py:188-194`），也就是 topic 模式 200、clustering 模式 10。无法仅凭本地证据判断这是论文排版/OCR错误还是版本差异，复现时必须以代码参数为准并报告该不一致。

### topic 模式为何还需要第二阶段 HSIC

第一阶段主要防止共享信号进入私有变量；反方向的泄漏——私有信号进入共享变量——在 topic 解释中同样会误导。topic 模式因此增加第二个 400-epoch 上限阶段：冻结私有侧参数，只更新共享侧和解码相关参数，并惩罚共享与私有样本之间的 Hilbert–Schmidt independence criterion：

$$
\operatorname{HSIC}(Z_s,Z_p)=\frac{\operatorname{tr}(LHKH)}{(n-1)^2}.
$$

代码以 Gaussian kernel 构造 $K,L$，以 $H=I-\frac1n\mathbf 1\mathbf 1^T$ 居中（`SpaMV/spamv.py:320-326`）；第二阶段训练分支见 `spamv.py:273-301`。论文明确该阶段只用于 topic modeling，因为 clustering 的目标是分区准确度，而不是每个共享维度的纯净语义（`paper.md:271-283`）。HSIC 越小表示在所选核尺度下依赖越弱，但不等于生物学机制独立。

### 两种解码器对应两个任务

domain clustering 模式先做模态相应的降维/标准化，再用两层 MLP 重构，默认 Gaussian likelihood；代码默认共享和每个私有空间各 32 维、隐藏层 256、学习率 $10^{-3}$（`spamv.py:127-172`）。最终 `get_embedding` 把平均共享均值和每个私有均值拼接（`model.py:222-236`），下游聚类由教程/工具函数完成，而非 VAE 内部直接输出离散标签。

topic modeling 模式默认共享与每个私有空间各 10 维，使用 count-like NB（也允许 ZINB）似然。对模态 $i$，代码按

$$
\mu_i=l_i\,\operatorname{softmax}([z_s,z_{p_i}])\operatorname{softmax}(\beta_i)
$$

构建期望计数，其中 $l_i$ 是 spot library size，$\beta_i$ 是 topic×feature 权重（`model.py:116-137,163-185`）。全局—局部 horseshoe 型层级先验收缩大多数 $\beta$，让少数高权重特征更易解释。论文相应推导见 `paper.md:287-319`。需要注意，softmax 使权重适合相对贡献解释，不应把它读成因果调控系数。

训练后还会删除不够“有意义”的主题。代码先以空间坐标建立邻居，计算每个维度的 Moran's I；若存在低值，用二类 KMeans 保留高空间自相关簇，再要求 `exp(z)` 的标准差超过阈值 1（`spamv.py:281-318`）。默认噪声阈值参数 0.3 只触发是否聚类的判断，代码不是逐维简单执行 `Moran's I > 0.3`。这是阅读论文简述时容易忽略的实现边界。

### 怎样读六幅主图

- Fig. 1 是方法合同：双 GAT 编码器、共享/私有潜变量、两种重构、measurement model、HSIC，以及 clustering/topic 两种输出。它是结构示意，不证明分解唯一。
- Fig. 2 用已知共享和私有空间块的模拟数据检验能否找回真值。SpaMV 在六类监督聚类指标和 Jaccard 保留度上表现强，并让主题/高权重特征对应预设因子。它证明的是作者模拟生成机制下的恢复能力。
- Fig. 3 在 E13 小鼠胚胎转录组—表观组数据上比较解剖区域、Jaccard 和模态偏向主题，展示私有主题可补充统一嵌入遗漏的结构。
- Fig. 4 处理 H3K27ac—H3K27me3，利用 feature-topic 权重提出与发育区域相关的基因。候选基因是计算假说，不是扰动验证。
- Fig. 5 在透明细胞肾癌转录组—代谢组中展示恶性、免疫、基质和内皮相关的共享/私有主题；细胞类型标签仍依赖作者注释和参考知识。
- Fig. 6 的小鼠胸腺案例最直接展示私有模态价值：转录 DEG 可能提示 T 细胞，而仅 19 个 marker 的蛋白面板在特定区域支持 B 细胞、浆细胞样树突细胞和巨噬细胞解释。该结果很有启发性，但受小蛋白面板限制。

逐面板图像证据在 `figure_analysis.md`，图像位于 `paper source/paper/auto/images/`。论文 Markdown 末尾包含 Extended Data Fig. 1–3 的图注与图像；工作区未发现独立 supplementary PDF/Markdown。正文声称更完整推导见 Supplementary Note B（`paper.md:218`），因此本地证据不能宣称已逐页核验该补充推导。

### 基准结果能说明什么、不能说明什么

模拟和四个真实数据案例显示，SpaMV 报告的空间域、Jaccard、主题相关性及生物标志解释总体优于或补充 SpatialGlue、CellCharter、COSMOS、SMOPCA、MISO、spaMultiVAE 等基线。Jaccard 主要衡量邻域结构保留，不直接等价于更真实的生物机制；监督指标依赖已有区域标签；主题案例依赖文献和 marker 解释。

更关键的复现边界是：当前 GitHub 快照提供 SpaMV 包、两个教程以及部分示例数据入口，却没有论文所有数据预处理、竞争方法运行、全部绘图和统计汇总脚本。因此可以审计核心模型，并能按教程运行作者方法，但不能仅靠该目录一键重建 Figs. 2–6 的完整 benchmark。论文列出的预处理数据位于 Zenodo 16436314，真实数据另来自 GEO、Figshare 和 BGI（`paper.md:390-394`）；本次没有重新下载或重跑这些大数据。

### 版本与适用边界

本地代码快照来自 `https://github.com/ericcombiolab/SpaMV`，提交为 `d7105ef70e9276350e8a12bddfbd3d396d1c33d2`。论文是 2025 年 bioRxiv 预印本 DOI `10.1101/2025.08.02.668264`，尚不能把结论表述为同行评审期刊定论。当前设计和代码按两个模态组织；论文也明确指出，三个以上模态会出现“只在某个模态子集共享”的因素，单一共享空间不足以表达这一层级（`paper.md:198-204`）。

最后，shared/private 是由训练目标操作化的统计分解，不是唯一真值。空间图会平滑边界，低 Moran's I 的非空间程序可能被剪掉，强度差异与批次效应也可能进入私有空间。最稳妥的使用方式是：用 clustering 模式做综合空间分区，用 topic 模式生成可追溯的特征假说，再回到原始模态空间、组织学和独立实验验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpaMV

### Paper

**Title:** Interpretable spatial multi-omics data integration and dimension reduction with SpaMV
**Authors:** Yang Liu, Kexin Ma, Haoran Xu, Ke Xu, Yunfei Hu, Zhenhan Lin, Jiangli Lin, Bo Han, Shuaicheng Li, Zhixiang Lin, Xin Maizie Zhou, Lu Zhang
**Venue:** bioRxiv preprint, 2025
**DOI:** `10.1101/2025.08.02.668264`

### Motivation

Spatial multi-omics data measure multiple molecular layers at the same tissue locations, but many integration methods compress all modalities into a single shared latent space. That can improve alignment while losing signals that are specific to one modality, such as chromatin potential without matching RNA expression or protein markers with weak transcript correspondence. SpaMV addresses this by explicitly modeling each modality as a view of the same tissue slice with both shared and private latent factors.

### Method Overview

SpaMV is a variational multi-view representation model with two graph-attention encoders per modality: one shared encoder and one private encoder. The encoders use graphs built from spatial proximity and data-space k-nearest-neighbor similarity. Decoders reconstruct each modality from shared and private latents.

The method uses three main constraints to encourage disentanglement. Cross-modality reconstruction pushes shared latents to carry information useful across modalities. Stop-gradient self reconstruction preserves the need for private latents. Auxiliary measurement models try to predict other modalities from private latents, and SpaMV penalizes variability in those predictions to remove shared information from the private space. In topic modeling mode, a second training stage adds HSIC regularization between shared and private latents.

SpaMV has two output modes:

- **Domain clustering:** returns combined shared/private embeddings for spatial segmentation.
- **Interpretable dimension reduction:** returns spatial topics plus feature-topic weights, allowing users to identify shared and modality-private biological programs.

### Evaluation

The paper evaluates SpaMV on three simulated datasets and four real spatial multi-omics datasets: mouse embryo transcriptome-epigenome, mouse embryo H3K27ac-H3K27me3, ccRCC transcriptome-metabolome, and mouse thymus transcriptome-proteome. Reported baselines include SpatialGlue (Nature Methods, 2024), CellCharter (Nature Genetics, 2024), COSMOS (Nature Communications, 2025), SMOPCA (Genome Biology, 2025), MISO (Nature Methods, 2025), and spaMultiVAE (Nature Methods, 2024).

Across figures, SpaMV is reported to improve supervised clustering metrics, neighborhood Jaccard preservation, and visual recovery of anatomical or simulated domains. The most biologically compelling examples are the private-topic analyses: SpaMV highlights epigenome- or transcriptome-private embryo regions, histone-modification-associated developmental genes, tumor-region transcriptome/metabolome topics, and a proteome-private thymus topic that supports more accurate cell-type annotation than transcript-only DEGs.

### Code Match

The public repository `https://github.com/ericcombiolab/SpaMV` was cloned at commit `d7105ef70e9276350e8a12bddfbd3d396d1c33d2`. Overall code-paper fidelity is **medium-high**. The core model is implemented: shared/private GAT encoders, graph construction, reconstruction terms, measurement models, HSIC stage, topic pruning, and evaluation utilities are present.

Important caveats:

- The measurement-model warm-up schedule appears reversed relative to the OCR paper text: code uses 200 epochs for interpretable mode and 10 for non-interpretable clustering mode.
- Interpretable cross reconstruction uses zero auxiliary private variables, while the paper describes a standard Gaussian auxiliary variable.
- Some preprocessing defaults differ from the method prose.
- The public repo does not include full competitor benchmark pipelines for all figures; it provides SpaMV tutorials and points to Zenodo for full data.

### Reproducibility

**Rating:** 3/5.

The package is compact and the core implementation is readable, with tutorial scripts for simulated and real datasets. However, complete reproduction requires external Zenodo data, R `mclust`, PyTorch/Pyro/PyG dependencies, and missing competitor pipelines. The repository is sufficient to understand and run SpaMV, but not by itself sufficient to reproduce every comparative benchmark in the paper.

### Main Limitations

- SpaMV is designed for two-modality settings; more than two modalities may require subset-shared latent variables.
- Topic interpretation depends on preprocessing, graph construction, pruning thresholds, and marker-feature interpretation.
- Private-topic biological claims are computationally supported but generally not experimentally validated.
- OCR quality for the preprint is usable but noisy for Eq. 1, so the analysis relies on readable paper prose and source verification for objective details.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
