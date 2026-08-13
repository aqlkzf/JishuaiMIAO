---
layout: default
permalink: /paper-atlas/topomics-e271ec1f/
title: "TopOmics"
nav: false
wide: true
description: "TopOmics 解决的是单细胞和空间多组学中的一个常见矛盾：研究者需要能处理大规模、多模态、空间信息的数据模型，但又希望潜变量可解释。论文指出，主题模型本来很适合解释复杂数据，因为每个 latent direction 可以解释为一个“topic”；但已有单细胞/空间组学主题模型往往绑定在特定数据类型、特定噪声模型或特定估计算法上，互操作性和通用性不足。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>TopOmics</h1>
    <p>TopOmics: Topic Modelling for All Omics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.05.26.727810" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for TopOmics">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/fcaretti/TopOmics" target="_blank" rel="noopener noreferrer" aria-label="Open code for TopOmics">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TopOmics 方法中文解读

### 这篇文章要解决什么问题

TopOmics 解决的是单细胞和空间多组学中的一个常见矛盾：研究者需要能处理大规模、多模态、空间信息的数据模型，但又希望潜变量可解释。论文指出，主题模型本来很适合解释复杂数据，因为每个 latent direction 可以解释为一个“topic”；但已有单细胞/空间组学主题模型往往绑定在特定数据类型、特定噪声模型或特定估计算法上，互操作性和通用性不足（`paper.md:24-27`）。

TopOmics 的基本类比是：细胞或 spot 相当于文本中的 document；基因、蛋白、染色质区域等 feature 相当于 word；不同组学模态相当于同一个 document 的不同 section；空间邻域可以看成 document 之间的图结构（`paper.md:36-39`）。因此，模型的目标不是学习一个黑盒 embedding，而是学习每个细胞由哪些 topic 组成，以及每个 topic 在每个模态上对应哪些 feature。

### 方法的核心思想

TopOmics 是一个多模态、可选空间图的 amortized LDA 框架。论文中的生成模型包括：

- 每个细胞/spot `n` 有一个 topic proportion `theta_n`；
- 每个模态 `m`、每个 topic `k` 有一个 topic-feature distribution `phi_{k,m}`；
- 每个观测 feature 可以通过 latent topic assignment `z_{n,m,f}` 解释；
- 不同数据类型使用不同 likelihood，例如 RNA/蛋白计数用 Gamma-Poisson 或 Negative Binomial，ATAC peak 或甲基化位点用 Bernoulli，连续值可用 Gaussian，经典主题模型还可用 Multinomial（`paper.md:134-177`）。

代码中，`MultimodalAmortizedLDA` 是主入口。它暴露 `n_topics`、`likelihoods`、`cell_topic_prior`、`topic_feature_prior_type`、`weight_mode`、空间 GCN/GAT 参数等接口（`TopOmics_repo/src/topomics/models/amortizedLDA.py:88-127`），并把这些参数传给底层 Pyro module（`TopOmics_repo/src/topomics/models/amortizedLDA.py:470-513`）。

### 输入和输出

输入可以是 `AnnData`、`MuData`、`SpatialData` 或多个 `AnnData` 的字典。对于多模态数据，代码会按指定顺序抽取每个 modality 的矩阵、layer 和空间图，再把 feature 横向拼接成一个统一矩阵，同时保留每个 modality 的 feature 数量（`TopOmics_repo/src/topomics/data/data_extraction.py:11-156`）。这对应论文中每个细胞有 `M` 个观测向量、每个模态长度为 `F_m` 的设定（`paper.md:144-145`）。

输出主要包括：

- `theta`：细胞 × topic 的矩阵，可以用于聚类、空间 domain 识别、UMAP 可视化；
- `phi`：topic × feature 的矩阵，可以解释每个 topic 对应哪些基因、蛋白或 ATAC peak；
- modality weights：多模态聚合时每个细胞/模态的贡献；
- feature-feature 或 cross-modality interaction score，用于生成 marker heatmap 或调控假设（`paper.md:237-240`）。

代码中，`get_latent_representation` 返回细胞 topic 分布（`TopOmics_repo/src/topomics/models/amortizedLDA.py:1315-1399`），`get_feature_topic_dist` 返回 topic-feature 分布（`TopOmics_repo/src/topomics/models/amortizedLDA.py:1221-1270`），`cross_modality_score` 用 `Theta` 和两个模态的 `Phi` 计算 feature-feature 交互矩阵（`TopOmics_repo/src/topomics/models/base_model.py:179-260`）。

### 计算流程

可以把 TopOmics 的流程理解为：

```text
多模态矩阵 + 可选空间图
        |
        v
按 modality 抽取、拼接 feature，并记录每个 modality 的长度
        |
        v
对非 Gaussian 输入做 library-size 归一化和 log1p
        |
        v
每个 modality 单独编码：
  普通数据 -> 全连接 encoder
  空间数据 -> GATv2/GCN/SGC 空间 encoder
        |
        v
每个 modality 产生 topic-logit 空间里的 Gaussian 参数
        |
        v
用 MoE 聚合多个 modality 的 Gaussian
        |
        v
采样 log_theta，再 SoftMax 得到 theta
        |
        v
theta 乘以 phi，得到每个 modality 的 feature 均值/概率
        |
        v
用相应 likelihood 重构数据，并通过 ELBO 训练
```

论文 Figure 6 正是这个流程：输入矩阵先归一化；如果有空间信息，先经过 graph attention；每个 modality 使用 encoder 输出 `mu` 和 `sigma`；然后通过 weighted Mixture-of-Experts 聚合；SoftMax 后得到和为 1 的 topic representation；最后用 topic-feature 参数解码并支持下游分析（`paper.md:139-141`）。代码中对应的核心位置是 guide 的输入归一化、encoder、MoE 聚合与 `log_cell_topic_dist` 采样（`TopOmics_repo/src/topomics/module/_amortizedLDA.py:1156-1280`），以及 model 的 topic-feature 解码和 likelihood 观测（`TopOmics_repo/src/topomics/module/_amortizedLDA.py:423-540`）。

### Dirichlet 的 logistic-normal 近似

论文说 `theta_n` 服从 Dirichlet prior，但实际训练使用 amortized variational inference。为了可重参数化，TopOmics 使用 logistic-normal 近似 Dirichlet：先在 logit 空间采样 Gaussian，再通过 SoftMax 得到 simplex 上的 topic proportion（`paper.md:153-159`）。

代码实现很直接：`logistic_normal_approximation(alpha)` 根据 Dirichlet concentration `alpha` 计算 Gaussian 的 `mu` 和 `sigma`（`TopOmics_repo/src/topomics/utils/_amortized_utils.py:26-31`）。cell-topic prior 在 module 初始化时被展开到长度 `K`，再转为 logistic-normal 参数（`TopOmics_repo/src/topomics/module/_amortizedLDA.py:143-155`）。训练时，model 采样 `log_cell_topic_dist` 并 SoftMax 成 `theta`（`TopOmics_repo/src/topomics/module/_amortizedLDA.py:423-430`）。

topic-feature 的 Dirichlet prior 也是类似处理。若 `topic_feature_prior_type="logistic_normal"`，代码会为每个 modality 的 feature prior 预先计算 logistic-normal 参数，然后采样 `log_topic_feature_dist_m`（`TopOmics_repo/src/topomics/module/_amortizedLDA.py:178-189`, `TopOmics_repo/src/topomics/module/_amortizedLDA.py:267-280`）。

### Horseshoe prior 的作用

论文提供另一个 topic-feature prior：Horseshoe prior。它通过 topic-level、feature-level、topic-feature-level 三层 shrinkage 参数，让多数不重要的 feature-topic 关联被压小，同时允许强信号逃过 shrinkage。这有助于得到更稀疏、更容易解释的 topic-feature 结构（`paper.md:192-207`）。

代码中，Horseshoe 路径会采样 `caux`、`tau`、`delta`、`lambda` 和 `beta`，用 `horseshoe_shrinkage` 计算有效 shrinkage multiplier，再把它乘到 `beta` 上得到 topic-feature logits（`TopOmics_repo/src/topomics/module/_amortizedLDA.py:282-357`）。shrinkage 公式封装在 `TopOmics_repo/src/topomics/utils/_amortized_utils.py:34-81`。guide 里有对应的 LogNormal/Normal 变分参数（`TopOmics_repo/src/topomics/module/_amortizedLDA.py:728-775`, `TopOmics_repo/src/topomics/module/_amortizedLDA.py:1045-1090`）。

### 多模态如何合并

论文的多模态部分说，每个 modality 都有一个 encoder，输出 topic-logit 空间中的 Gaussian 分布；多个 Gaussian 通过 weighted mixture 合并。论文文字和 Figure 6 都说默认权重是 cell-dependent，并与 encoder 给出的 variance 成反比（`paper.md:139-139`, `paper.md:213-219`）。

代码支持三种权重模式：

- `equal`：每个可用 modality 权重相同；
- `universal`：每个 modality 一个全局可学习权重；
- `cell`：每个细胞一个可学习 modality 权重向量。

这些权重在 `_mix_gaussians` 中经过 mask 和 SoftMax 归一化，然后用于加权 modality mean；variance 则按 total variance 公式合并，包括 modality 内部方差和 modality mean 之间的方差（`TopOmics_repo/src/topomics/module/_amortizedLDA.py:839-906`）。需要注意：这是一个 **Partial match**。代码确实支持 cell-dependent weights，也使用 encoder variance 进入合并后的 variance，但当前代码没有把权重直接设为 `1/sigma_m^2`；`cell` 模式使用的是可学习 raw weights（`TopOmics_repo/src/topomics/module/_amortizedLDA.py:843-847`, `TopOmics_repo/src/topomics/module/_amortizedLDA.py:893-897`）。

### 空间信息如何进入模型

对空间组学数据，论文说 TopOmics 从空间坐标构建邻域图；低分辨率 mouse brain 使用 4/5 个邻居的图，VisiumHD 使用 10 近邻；默认空间 encoder 是 GATv2，并提供 GCN、SGC 和 skip connection 选项（`paper.md:222-234`, `paper.md:321-336`, `paper.md:427-430`, `paper.md:442-442`）。

代码中，空间图由 wrapper 解析并传入 module；若有空间图，模型会把完整 feature matrix 和 adjacency 初始化到 guide 中（`TopOmics_repo/src/topomics/models/amortizedLDA.py:456-532`）。`GCNEncoder` 支持 `GATv2Conv` 和 `GCNConv`，并用 `alpha * h_self + (1-alpha) * h_nei` 混合自身信号和邻居聚合信号（`TopOmics_repo/src/topomics/utils/_encoders.py:26-38`, `TopOmics_repo/src/topomics/utils/_encoders.py:107-127`, `TopOmics_repo/src/topomics/utils/_encoders.py:275-282`）。为了支持大图，代码把完整图存放在 CPU，并在每个 minibatch 只抽取 k-hop 子图到计算设备上（`TopOmics_repo/src/topomics/utils/_encoders.py:187-194`, `TopOmics_repo/src/topomics/utils/_encoders.py:327-343`）。

### 论文实验和代码对应关系

Figure 1 的 scaling 实验用合成 RNA+ATAC 数据比较 TopOmics、SHARE-Topic、MultiVI 和 MOFA+（`paper.md:39-47`, `paper.md:409-415`）。代码中 cell-count scaling 脚本确实会训练 TopOmics 并使用 validation ELBO early stopping（`TopOmics_repo/paper/workflow/scripts/scaling_multimodal_cells.py:121-142`）。但 feature-scaling 脚本里定义的是 `train_omics_topic`，后面调用的是 `train_topomics`，这个快照中看起来存在命名不一致（`TopOmics_repo/paper/workflow/scripts/scaling_multimodal_features.py:80-100`, `TopOmics_repo/paper/workflow/scripts/scaling_multimodal_features.py:180-190`）。

Figure 2 的 mouse brain spatial RNA+ATAC 实验在代码中有较明确脚本：加载 RNA/ATAC，二值化 ATAC，构建 spatial graph，用 Gamma-Poisson 和 Bernoulli likelihood 训练 TopOmics（`TopOmics_repo/paper/scripts/train_mouse_brain_spatial.py:104-182`）。但脚本默认值和论文描述并非完全一致：论文写的是 per-cell weights 和 2-layer GATv2；脚本默认 `weight_mode="universal"` 且默认 `gcn_n_layers=1`，除非通过命令行或 workflow 覆盖（`TopOmics_repo/paper/scripts/train_mouse_brain_spatial.py:40-79`, `paper.md:427-430`）。

Figure 3 的 VisiumHD colorectal cancer 实验把 nucleus RNA 和 cytoplasm RNA 当作两个 modality（`paper.md:433-448`）。核心库可以表达这种多模态空间模型，但在已检查的 `paper/scripts/`、`paper/workflow/`、`src/topomics/` 和 `paper/config.yaml` 中没有找到直接复现该 Figure 3 的 QuPath/GeoJSON/VisiumHD nucleus-cytoplasm 训练脚本；`train_visium.py` 只是一个通用的 unimodal Squidpy Visium 示例（`TopOmics_repo/paper/scripts/train_visium.py:80-123`）。

Figure 4 的 TEA-seq 实验使用 RNA、ATAC、protein 三个 modality（`paper.md:451-466`）。代码脚本匹配大部分设置：加载 `h5mu`，准备 count layer，二值化 ATAC，筛选 RNA/ATAC HVG，设置 K=10、MoE、cell weights、Gamma-Poisson/Bernoulli likelihood、batch size 128、80/20 split、最多 500 epoch（`TopOmics_repo/paper/scripts/train_teaseq.py:99-153`）。但论文说 per-gene learnable dispersion；脚本里这是命令行选项，默认关闭（`TopOmics_repo/paper/scripts/train_teaseq.py:59-64`, `TopOmics_repo/paper/scripts/train_teaseq.py:122-141`）。

### 如何理解这篇工作的贡献

TopOmics 的贡献不是提出一个完全黑盒的 embedding 模型，而是把 topic model 扩展成一个可用于现代组学数据的统一框架：

1. 用不同 likelihood 适配 RNA、ATAC、protein、连续值等数据；
2. 用 amortized inference 和 minibatch 训练提高可扩展性；
3. 用 logistic-normal 近似让 Dirichlet-like topic proportion 可以通过神经网络训练；
4. 用 Horseshoe prior 增强 topic-feature 稀疏性和解释性；
5. 用 GAT/GCN/SGC 把空间邻域信息放入 encoder；
6. 用 MoE 把多个 modality 聚合到同一个 `theta` 表示；
7. 保留 `theta` 和 `phi`，从而能做 marker、空间 domain、cluster 和 cross-modality interaction 分析。

### 需要保留的不确定性

- `paper.md` 转换后有若干 display equation 缺失，因此完整代数公式不能只靠本地 Markdown 逐项复核。
- Figure 6 的 inverse-variance default weighting 与当前代码实现不是完全相同的机制。
- Figure 3 的直接复现实验脚本没有找到。
- Figure 2 和 Figure 4 的脚本需要命令行或配置覆盖才能完全贴近论文文字中的所有设置。
- Appendix KL 推导在代码里是通过 Pyro 的同名 latent sample 和 KL scaling 间接对应，不是一个显式闭式 KL 函数。

因此，最准确的结论是：TopOmics 的核心模型实现有较强代码支撑；论文级复现实验代码覆盖不均，需要对每个 figure 的脚本和参数单独核查。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TopOmics Summary

### Problem

TopOmics targets interpretable modeling of modern single-cell and spatial omics datasets that may contain multiple modalities per cell or spot. The paper argues that topic models are attractive because topics are interpretable latent directions, but existing topic-model implementations are often tied to specific data types, likelihoods, or inference algorithms (`paper.md:24-27`). TopOmics reframes cells/spots as documents, genes/proteins/chromatin features as words, modalities as document sections, and spatial neighborhoods as graph links between documents (`paper.md:36-39`).

### Proposed Method

TopOmics is a modular amortized LDA-style framework for single-cell and spatial multiomics. Each cell has a topic distribution `theta`; each modality has topic-feature distributions `phi`; and observations are generated through modality-appropriate likelihoods such as Gamma-Poisson/Negative Binomial, Bernoulli, Gaussian, or Multinomial (`paper.md:134-177`). The implementation exposes these choices in `MultimodalAmortizedLDA`, validates modality/likelihood settings, and builds a Pyro module with logistic-normal Dirichlet approximations, optional Horseshoe topic-feature priors, optional spatial GAT/GCN encoders, and multimodal MoE aggregation (`TopOmics_repo/src/topomics/models/amortizedLDA.py:88-127`, `TopOmics_repo/src/topomics/models/amortizedLDA.py:470-532`).

The computational pipeline is: extract and concatenate modality matrices; normalize non-Gaussian encoder inputs by library size; optionally run spatial graph encoders; encode each modality to Gaussian topic-logit parameters; aggregate modalities; SoftMax the sampled logits into cell-topic proportions; decode through topic-feature matrices; and optimize the Pyro ELBO plus optional regularizers (`paper.md:139-162`; `TopOmics_repo/src/topomics/module/_amortizedLDA.py:1156-1280`, `TopOmics_repo/src/topomics/module/_amortizedLDA.py:423-540`).

### Evaluation

The paper evaluates TopOmics on several settings:

- Scaling experiments on synthetic RNA+ATAC data compare TopOmics with SHARE-Topic, MultiVI, and MOFA+; Figure 1 visually shows TopOmics scaling to larger cell counts with lower runtime curves than some baselines (`paper.md:39-47`, `paper.md:409-415`).
- A mouse brain spatial RNA+ATAC benchmark compares TopOmics to SpatialGlue, COSMOS, MultiVI, and MOFA+ using clustering accuracy, NMI, and Moran's I; Figure 2 visually supports strong anatomical reconstruction and interpretable topics (`paper.md:53-70`, `paper.md:418-430`).
- A VisiumHD colorectal cancer analysis treats nucleus and cytoplasm RNA as separate modalities and reports TopOmics among the best methods for NMI, KMeans accuracy, and spatial coherence in the figure panels (`paper.md:76-87`, `paper.md:433-448`).
- A TEA-seq PBMC analysis uses RNA, ATAC, and protein, showing competitive multimodal metrics plus topic-abundance maps, marker heatmaps, and cross-modality interaction heatmaps (`paper.md:93-110`, `paper.md:451-469`).

### Reproducibility Notes

The repository is available at `https://github.com/fcaretti/TopOmics`, and the paper states that reproduction code is under the repository's `paper` folder (`paper.md:269-272`, `paper.md:403-407`). The acquired snapshot includes the core package and paper scripts at commit `35fdaa54fa7cb92df2824dd3d9c2a661a8ae3216`.

Code-paper fidelity is **medium-high** for the reusable model implementation and **medium** for exact paper figures. The core method is well represented in source: logistic-normal priors, Horseshoe priors, likelihoods, spatial encoders, topic/feature APIs, and cross-modality interaction scoring are directly implemented. Important caveats remain: the paper's inverse-variance default MoE wording is only partially matched by the inspected code; the direct Figure 3 colorectal VisiumHD nucleus/cytoplasm training script was not found; Figure 2 and Figure 4 scripts have defaults/configurability that do not fully match every paper statement without overrides; and the Appendix KL derivation is conceptually aligned to Pyro KL-scaled latent sampling but is not a named closed-form implementation.

Overall, TopOmics is best viewed as a credible, source-backed method paper with a usable public implementation and partial paper-workflow reproduction coverage, rather than a fully turnkey exact reproduction for every main figure.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
