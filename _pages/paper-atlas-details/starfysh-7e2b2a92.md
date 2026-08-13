---
layout: default
permalink: /paper-atlas/starfysh-7e2b2a92/
title: "Starfysh"
nav: false
description: "Starfysh 面向 spot-level 空间转录组：它从原始计数、细胞类型 marker 列表以及可选的配对 H&E 图像中，推断每个 spot 的细胞状态比例、总细胞密度和状态特异表达。它不要求单细胞参考表达矩阵，因此论文称其为 reference-free；但它仍依赖 marker 知识，不能理解为完全无先验的细胞类型发现。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>Nature Biotechnology · 2024</span>
    </div>
    <h1>Starfysh</h1>
    <p>Starfysh integrates spatial transcriptomic and histologic data to reveal heterogeneous tumor-immune hubs</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-024-02173-8" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Starfysh">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/azizilab/starfysh" target="_blank" rel="noopener noreferrer" aria-label="Open code for Starfysh">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Starfysh 方法解读：用 marker 锚点约束空间去卷积，并可融合 H&E

### 一句话定位

Starfysh 面向 spot-level 空间转录组：它从原始计数、细胞类型 marker 列表以及可选的配对 H&E 图像中，推断每个 spot 的细胞状态比例、总细胞密度和状态特异表达。它不要求单细胞参考表达矩阵，因此论文称其为 reference-free；但它仍依赖 marker 知识，不能理解为完全无先验的细胞类型发现。

论文把方法用于乳腺癌空间图谱，并在比例推断之后整合多个切片、定义 tumor–immune hubs、比较 TNBC 与转移性乳腺癌（MBC）的空间生态。这里要分清两层：AVAE/AVAE-PoE 是生成模型主干；hub 聚类、伪时间、通路和细胞互作是下游分析，并不是模型内部的一个隐变量。

### 输入、输出与最短数据流

输入包括：spot-by-gene 原始计数矩阵 $x_i$、spot 坐标、每个候选细胞状态的 marker 集合 $s_k$，以及可选的 H&E 图像。代码先过滤线粒体和核糖体基因，归一化并对数变换用于编码器，保留 2,000 个高变基因与 signature genes；负二项重建仍以原始计数为观测。若有图像，则从每个 spot 周围截取 patch 并做颜色/强度处理。

输出的核心是：每个 spot 的比例 $c_i$、细胞状态潜变量 $u_k$、spot 潜变量 $z_i$、library/density 量 $l_i$ 和由 decoder 给出的基因概率。比例可绘成空间图；状态特异表达由潜变量与 decoder 进一步恢复。跨样本 hub 标签、伪时间和互作网络由这些输出继续计算。

### 第一步：从 marker 分数得到候选锚点

对每个 spot 和细胞状态，Starfysh 用 Scanpy 的 `score_genes` 计算 signature enrichment。实现随后把负值截到一个很小的正数并逐 spot 归一化，得到矩阵 $A$。直观上，$A_{ik}$ 越大，spot $i$ 越像状态 $k$；但它只是 marker 驱动的软证据，不是已知真比例。

仅靠 marker 最高分容易把肿瘤内的新状态压进既有标签。论文因此对表达空间做 principal convex hull analysis（PCHA）：把数据云近似为少量 archetypes，再用 Fisher separability 估计维度、按 resolution 合并相近 archetype，并通过 stable-marriage matching 将 archetype 与 marker 富集状态配对。未被既有 signature 良好解释的 archetype 可提示上下文特异状态；匹配结果也用于修正 anchor spots。

这一步的关键作用不是直接输出最终比例，而是构造可信的比例先验。代码入口集中在 `starfysh/AA.py` 的 PCHA、archetype 合并和稳定匹配，以及 `starfysh/utils.py` 的 gene score 与 anchor refinement。

### 第二步：anchor-informed AVAE

表达模型 `AVAE` 是一个带层次结构的变分自编码器。对细胞状态 $k$，先放置状态潜变量

$$u_k \sim \mathcal{N}(0,10I).$$

每个 spot 的细胞比例使用 Dirichlet 分布。论文与实现都让 signature/anchor 矩阵参与其先验参数：

$$c_i \sim \mathrm{Dirichlet}(\alpha A_i).$$

因此 $A_i$ 给出“更可能含有哪些状态”的方向，浓度 $alpha$ 决定先验强度。编码器另从表达 $x_i$ 产生 Dirichlet 变分后验 $q(c_i\mid x_i)$；最终比例不是简单复制 marker 分数，而是在生成模型重建与先验约束之间学习。

spot 潜变量由状态潜变量按比例混合：

$$z_i\mid c_i,u \sim \mathcal{N}\left(\sum_k c_{ik}u_k,\ \sum_k c_{ik}\sigma_k\right).$$

实现中的变分后验也保留这一结构：编码器为每个候选状态产生均值和方差，再用采样的 $c_i$ 加权。这比把所有 spot 压到一个无结构 latent 更容易将组成差异与状态内异质性分开。

library latent $l_i$ 的先验中心来自空间邻域平滑后的 log library size。decoder 将 $z_i$ 映射为基因概率 $f(z_i)$，观测计数用基因特异离散度的负二项分布建模：

$$x_{ig}\sim\mathrm{NB}\left(\exp(l_i)f_g(z_i),\theta_g\right).$$

这里 $exp(l_i)$ 决定 spot 的总量尺度，softmax decoder 决定基因组成。论文将该量联系到细胞密度，但它仍受测序深度、捕获效率和组织结构影响，不能无条件当成显微镜下绝对细胞数。

训练目标是负 ELBO：负二项重建损失，加上 $u,z,c,l$ 各自后验与先验之间的 KL 项。代码 `AVAE.get_loss()` 明确计算重建项与四类 KL；`c` 的 KL 正是 marker/anchor 先验进入优化的地方。

### 第三步：可选的 H&E product-of-experts

`AVAE_PoE` 增加图像编码器。表达分支给出 $q_x(z)$，图像 patch 给出 $q_y(z)$；两者都近似高斯时，product-of-experts 用精度加权组合均值和方差。某一视图越确定，其方差越小，在联合 posterior 中权重越大。联合 latent 同时重建表达和图像，并保留单视图 marginal 目标，避免模型只依赖一种模态。

H&E 的价值是提供组织形态、边界和局部密度信息，而不是从像素中直接获得可靠的免疫细胞标签。marker 与表达仍然承担细胞状态语义。缺少图像时可运行表达版 AVAE；有图像并不保证每个数据集都改善，收益需要通过留出或外部空间测量验证。

### 训练与推断在代码中的落点

- `starfysh/starfysh/starfysh.py` 的 `AVAE`：比例、library 和状态结构化 encoder，负二项 decoder，以及 ELBO。
- 同文件的 `AVAE_PoE`：图像 encoder/decoder、Gaussian PoE 和联合/边缘损失。
- `starfysh/starfysh/AA.py`：PCHA、内在维度、archetype 合并和稳定匹配。
- `starfysh/starfysh/utils.py`：marker 打分、预处理、空间 window library、anchor refinement 与训练包装。
- `starfysh/starfysh/dataloader.py`：表达数据与 H&E patch 的批处理。
- `starfysh/starfysh/post_analysis.py`：SCI 等空间统计；多样本整合另见 `utils_integrate.py`。

训练包装会做多个随机重启并按比例相关损失选择模型，优化器为 Adam，并使用学习率调度和梯度裁剪。推断后可从比例与 decoder 计算 cell-state-specific expression，也可用联合模型预测图像相关量。

### 图 1 应该怎样读

图 1a 从左到右给出完整链条：转录组、已知 marker 和可选 histology 进入模型；输出比例与 density；多个样本再被整合为空间组成、hub、伪时间和互作。图 1b 的模拟数据把已知真比例与推断比例放在一起，说明 archetype-refined anchors 是模型入口而非最终答案。图 1c 画出 $u_k\rightarrow c_{ik}\rightarrow z_i$、library 和负二项计数的生成关系。图 1d 的相关性热图用于和参考式及其他无参考方法比较。

图 1e–f 用 Xenium/病理证据区分 DCIS 与侵袭性肿瘤区域，并显示两个 DCIS archetype。它支持 Starfysh 可以在同一大类肿瘤状态内保留空间异质性；但这些例子不是所有组织上“自动发现真实亚型”的普遍保证。

### 从比例到 tumor–immune hubs

论文分析 14 个乳腺癌样本，先对各切片推断细胞组成，再把 spot 的比例表征跨样本整合并聚类成空间 hub。hub 表示常共同出现的一组肿瘤、免疫和基质状态，而不是单一细胞类型。随后作者沿组成变化构造伪时间，并做通路富集、距离趋势和配体–受体分析。

图 4比较 TNBC 与 MBC：切片上的 intratumoral、peritumoral 和 stromal hub 分布不同；沿伪时间出现炎症、缺氧、EMT 与代谢程序变化。MBC 富集的 hub 中，Treg、耗竭 T、M2、MDSC 和 CAF 等比例更高，作者据此提出免疫抑制生态。图中 Sankey/互作与距离趋势是基于模型输出的关联分析，不能单独证明细胞间因果通讯。

论文还用 CODEX 抗体面板验证部分空间细胞组成。此类正交验证增强了特定乳腺癌结论的可信度，但面板有限、分辨率与标签体系不同，不能视为所有 latent state 的逐项真值。

### 论文与本地实现的对应和差异

核心生成结构是 Exact：Dirichlet 比例先验、结构化 $z$、windowed library、负二项重建、Gaussian PoE、PCHA 与 stable matching 都能在本地源码中找到。若把 log library 作为变量，代码使用 Normal 先验与论文写作中的 logNormal 是同一尺度约定，不应仅凭类名判为模型缺失。

有几处运行约定需要保留为 Partial，而不能假装完全一致：论文方法段给出的 PoE marginal 权重为 $a=5$，本地实现以 `lambda_poe=0.2` 写成另一种相对加权形式；两者可能只差整体缩放/记号方向，但复现时必须核对具体公式和调用参数。论文记录的部分实验设置（200 epochs、学习率 0.001、Kaiming 初始化、图像 patch 参数）与包装函数默认值（例如 100 epochs、较小学习率、Xavier 初始化、`patch_r=16`）不完全相同。默认值不等于论文最终运行配置，复现应以 notebook/保存参数为准。

此外，hub 的 PhenoGraph 聚类、基准 RMSE/JSD 以及部分论文图分析主要在 notebooks 或外部数据流程中，而非核心 Python API。Shannon entropy、MIC 等描述未在当前核心包的聚焦检索中定位到完整实现，因此应标为 Notebook/Not found，而不是由相近函数补写。

### 使用时最容易误读的边界

1. reference-free 是“不需要 scRNA-seq 参考”，不是“不需要 marker”。marker 错误或跨组织漂移会直接影响 anchor 与比例先验。
2. archetype 是表达几何的极端点，不天然等于生物学细胞类型；匹配与专家命名仍需要证据。
3. spot 比例是模型估计，不是单细胞分割；Visium spot 内仍混合多个细胞。
4. density/library latent 同时包含生物与技术尺度，绝对细胞数需要额外校准。
5. H&E PoE 融合形态信号，但不能替代分子 marker，也不能自动消除批次和染色差异。
6. hub 与伪时间是推断后构造的群体结构；它们适合描述空间生态连续性，不等同于真实时间轨迹或因果演化路径。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Starfysh: Integrating Spatial Transcriptomic and Histologic Data to Reveal Heterogeneous Tumor-Immune Hubs

### Citation
He, S., Jin, Y., Nazaret, A., Shi, L., Chen, X., et al. "Starfysh integrates spatial transcriptomic and histologic data to reveal heterogeneous tumor-immune hubs." *Nature Biotechnology* 43(2), 2024. DOI: [10.1038/s41587-024-02173-8](https://doi.org/10.1038/s41587-024-02173-8)

### Problem Statement

Sequencing-based spatial transcriptomics (ST) technologies such as Visium capture gene expression at multi-cellular resolution, where each spot contains mixtures of multiple cell types. Decomposing these mixtures into constituent cell states is critical for understanding tissue organization, but existing approaches suffer from three key limitations:

1. **Reference dependency**: Most deconvolution methods (Cell2location, DestVI, Tangram, BayesPrism) require paired single-cell RNA-seq data as a reference, which introduces batch effects and may not be available for cost or logistical reasons.
2. **Underutilization of histology**: Paired H&E histology images contain information about tissue architecture, cell density, and spatial dependencies that existing methods fail to leverage for improving deconvolution.
3. **Limited integration**: Methods designed for single samples cannot integrate multiple heterogeneous tissue samples to identify shared or disease-specific spatial neighborhoods, limiting statistical power for studying rare diseases.

### Approach

Starfysh (ST Analysis using Reference-Free auxiliarY deep generative modeling and Shared Histology) is a comprehensive toolbox that addresses all three limitations through:

#### 1. Archetypal Analysis for Reference-Free Anchor Detection

Instead of relying on single-cell references, Starfysh identifies "anchor spots" -- spots most likely dominated by a single cell state -- through two complementary strategies:

- **Gene set scoring**: Spots with highest expression of known cell state marker genes serve as initial anchors, with enrichment scores computed via `sc.tl.score_genes`.
- **Archetypal analysis**: The PCHA algorithm finds prototypical spots (archetypes) at the extrema of the data manifold in PCA space. These archetypes capture the "purest" spots and can discover new or context-dependent cell states. Archetypes are merged hierarchically using a resolution parameter $r$, and their marker genes are identified via Wilcoxon rank-sum tests. Stable marriage matching aligns archetypal communities to known cell types, refining the anchor set.

#### 2. Deep Generative Model with Structured Variational Inference

The core model treats each spot's gene expression as generated from a latent representation $z_i$ that is a mixture of $K$ cell state representations:

$$z_i \mid c_i, u, \sigma \sim \mathcal{N}\left(\sum_k c_{ik} u_k, \sum_k c_{ik} \sigma_k\right)$$

where $c_i \in \Delta^K$ are cell state proportions, $u_k \in \mathbb{R}^D$ are cell state-specific latent variables, and $\sigma_k$ controls cell state heterogeneity. Raw transcript counts follow a negative binomial distribution:

$$x_{ig} \mid z_i, l_i \sim \text{NegBinom}(l_i \cdot f(z_i), \theta_g)$$

where $f$ is a neural network decoder with softmax output and $l_i$ is the library size.

The variational family mirrors this structure with a "structured" posterior where $q(z_i \mid c_i, x_i)$ decomposes into cell state-specific contributions $\zeta(k, x_i)$ weighted by inferred proportions. The proportion prior uses Dirichlet distributions parameterized by the enrichment scores, providing a principled way to incorporate marker gene knowledge with adjustable confidence ($\alpha = 50$ default).

#### 3. Product-of-Experts (PoE) Histology Integration

When histology images are available, Starfysh uses a deep variational information bottleneck approach:

- Image patches $y_i$ around each spot are encoded by a separate neural network $\xi$
- The joint posterior over $z_i$ is computed as a product of Gaussian experts from expression and image branches
- The total loss combines joint and marginal (view-specific) ELBOs

#### 4. Multi-Sample Integration and Hub Identification

Starfysh integrates multiple samples by:
1. Computing sample-specific anchors and markers
2. Aggregating markers across samples
3. Training a joint model on all samples simultaneously
4. Clustering spots by inferred cell state proportions (PhenoGraph) to define "spatial hubs" -- niches with distinct compositions

### Key Results

#### Benchmarking
- On simulated data from breast cancer scRNA-seq, Starfysh matches reference-based methods (DestVI, Cell2location, Tangram, BayesPrism) while significantly outperforming reference-free methods (CARD, BayesTME, STdeconvolve)
- On real TNBC data (CID44971), Starfysh shows significant improvement in disentangling fine-grained cell states (Mann-Whitney U-test, $P = 1.70 \times 10^{-11}$)
- On matched Visium/Xenium breast tumor data, archetypes identified distinct DCIS subtypes without prior knowledge

#### Breast Tumor Analysis (14 samples, 10 patients)
- Characterized 29 diverse cell states in TNBC, including patient-specific tumor states via archetype-guided anchor refinement
- Discovered a continuous tumor state transition from basal to MBC-like states, associated with a compositional shift in immune infiltration along a "pseudospace" axis
- PoE integration improved cell density estimation (MIC = 0.33 vs. 0.18 for shuffled histology)

#### MBC-Specific Findings
- Identified immunosuppressive intratumoral hubs in MBC enriched for T~reg~ cells, M2-like macrophages, MDSCs, and CAFs
- Found hypoxia and EMT as drivers of the immunosuppressive microenvironment
- Predicted T~reg~ crosstalk via FGF2/FGFR1 and CD44 signaling pathways
- Results validated with CODEX profiling (23 antibodies)

#### Integration Results
- Successfully integrated 14 samples across ER+, TNBC, and MBC subtypes (37,517 spots)
- Identified shared and disease-specific spatial hubs
- Quantified MBC as having highest intertumoral heterogeneity

### Implementation Details

- **Framework**: PyTorch
- **Architecture**: Encoder-decoder VAE with 256 hidden dimensions, 10-dimensional latent space
- **Training**: Adam optimizer, exponential LR decay (gamma=0.98), gradient clipping (max norm=5), 3 restarts selecting best $\mathcal{L}_c$
- **Key dependencies**: py_pcha (archetypal analysis), scikit-dimension (intrinsic dimension), histomicsTK (color deconvolution), scanpy (preprocessing)
- **Input**: Raw ST count matrix + cell state marker gene lists + optional H&E image
- **Output**: Cell state proportions per spot, cell state-specific expression, spatial hubs, reconstructed histology

### Data Availability

- Raw ST data: GEO [GSE218951](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE218951)
- CODEX data: figshare (10.6084/m9.figshare.25137320)
- Public datasets: GEO GSE176078 (Wu et al.), ArrayExpress E-MTAB-11114 (Kleshchevnikov et al.)
- Code: [GitHub](https://github.com/azizilab/starfysh), Zenodo (10.5281/zenodo.10460548)

### Limitations and Future Directions

- Archetypal analysis is a preprocessing step rather than integrated into the probabilistic framework
- No explicit multiomic integration (proteomics, chromatin accessibility)
- High-resolution image features (cell morphology) not explicitly modeled
- Hub definition relies on post-hoc clustering rather than being part of the generative model

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
