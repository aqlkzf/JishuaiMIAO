---
layout: default
permalink: /paper-atlas/scagde-ff46fee6/
title: "scAGDE"
nav: false
description: "scAGDE 不是只对稀疏的 scATAC 峰矩阵做一次降维。它先用普通变分自编码器找出能区分细胞的峰并建立细胞近邻图，再用图卷积变分自编码器同时重建“哪些细胞彼此相邻”和“每个峰是否开放”，最后用软聚类和高置信伪标签继续收紧潜空间。输出因此兼顾细胞嵌入、聚类、峰筛选和开放概率插补。"
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
      <span>scATAC — Single-Cell Chromatin &amp; DNA Methylation</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>scAGDE</h1>
    <p>Topological identification and interpretation for single-cell epigenetic regulation elucidation in multi-tasks using scAGDE</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-57027-x" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scAGDE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Hgy1014/scAGDE" target="_blank" rel="noopener noreferrer" aria-label="Open code for scAGDE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scAGDE 中文方法解读

### 一句话理解

scAGDE 不是只对稀疏的 scATAC 峰矩阵做一次降维。它先用普通变分自编码器找出能区分细胞的峰并建立细胞近邻图，再用图卷积变分自编码器同时重建“哪些细胞彼此相邻”和“每个峰是否开放”，最后用软聚类和高置信伪标签继续收紧潜空间。输出因此兼顾细胞嵌入、聚类、峰筛选和开放概率插补。

### 1. 输入与最终输出

输入为细胞乘峰矩阵 $X\in\mathbb R^{N\times M}$。代码的 `prepare_data(binary=True)` 将大于 1 的值截为 1，因此核心模型使用的是峰是否被观察到开放的二值表示，而不是原始片段数的计数分布。

标准 `Trainer.fit()` 的持久输出包括：

- `adata.obsm["latent_init"]`：第一阶段自编码器的初始嵌入；
- `adata.var["is_selected"]`：入选峰标记，默认取重要性最高的 10,000 个峰；
- `adata.obsm["latent"]`：图模型学习到的最终细胞嵌入；
- `adata.obsm["impute"]`：可选的逐细胞逐峰开放概率；
- `adata.obs["cluster"]`：可选的最终聚类标签。

### 2. 第一阶段：先学习细胞表征，再用权重筛峰

第一阶段是一个 Bernoulli 变分自编码器。编码器把二值峰向量映射为高斯后验参数：

$$
(\mu_i,\log\sigma_i^2)=f_e(x_i),\qquad
z_i=\mu_i+\sigma_i\odot\epsilon,quad \epsilon\sim\mathcal N(0,I),
$$

解码器给出重建概率 $\hat x_i=f_d(z_i)$。目标由二元交叉熵与到标准正态先验的 KL 散度组成。

训练完后，scAGDE 不直接丢弃这个模型，而是读取编码器第一层权重。论文令某个峰连接到各隐藏节点的权重离散程度代表峰重要性：如果一个峰对不同隐藏特征的作用差异很大，它更可能承载细胞间异质性。默认保留得分最高的 10,000 个峰；若峰数不足则全部保留。

本地代码的实际路径是 `Trainer.CountModel()` → `ChromatinAccessibilityAutoEncoder.fit()`，随后对 `model.encoder.hidden[0].weight` 沿隐藏节点方向计算 `torch.std` 并做 min-max 缩放。论文公式写的是方差，而代码使用标准差；排序通常单调一致，但数值定义并不相同。

### 3. 从初始嵌入构建细胞图

第一阶段嵌入还用于定义细胞间拓扑。`get_adj()` 默认以欧氏距离寻找包括自身在内的 15 个近邻，得到邻接矩阵 $A$，再计算

$$
\bar A=D^{-1/2}AD^{-1/2}.
$$

这一步很关键：图不是直接从极高维、极稀疏的原始峰矩阵构建，而是从已经压缩过的 `latent_init` 构建。直观上，第一阶段负责提出“哪些细胞可能相似”，第二阶段再让图模型同时检验拓扑与峰信号是否相容。

### 4. 第二阶段：图卷积变分编码器与两个解码器

图编码器同时接收筛选后的峰矩阵和归一化邻接矩阵。GCN 在每层聚合邻居信息，产生 $Z_\mu$ 和 $Z_\sigma$，再通过重参数化得到最终潜变量 $Z$。

随后有两个不同任务的解码器：

1. 图解码器使用内积

$$
\hat A=\operatorname{sigmoid}(ZZ^\top)
$$

重建细胞之间的连接；相近细胞的潜向量应具有较大内积。

2. 峰解码器使用全连接层和 sigmoid

$$
B=\operatorname{sigmoid}(ZW_d),
$$

得到 $b_{ij}\in[0,1]$，解释为细胞 $i$ 的峰 $j$ 开放概率。它对二值输入使用 Bernoulli 负对数似然。代码直接返回浮点概率作为插补矩阵，不再随机采样一个新的 0/1 矩阵。

例如某个原始零值被解码为 $b_{ij}=0.82$，表示在模型学习的细胞状态与邻域下，该峰很可能开放；它是模型估计而不是新增实验观测。

### 5. 自监督聚类如何反过来塑造嵌入

图模型先在不含聚类损失的条件下预训练，然后对潜变量执行 K-means 初始化聚类中心。对每个细胞与中心，Student-t 核产生软分配 $q_{ij}$。随后构造更尖锐的目标分布

$$
p_{ij}=\frac{q_{ij}^2/f_j}{\sum_{j'}q_{ij'}^2/f_{j'}},
\qquad f_j=\sum_iq_{ij},
$$

并最小化 $D_{KL}(P\|Q)$。平方会放大已经较高的分配概率，而除以簇频率可减轻大簇支配。

此外，模型取 $\arg\max_j p_{ij}$ 作为伪标签，只让超过动态置信阈值的条目参与加权交叉熵。这样聚类不只是训练后的读出，而会反向更新图嵌入。当前代码的阈值从 0.55 线性提高到 0.8；论文文字写 0.60 到 0.80，这是明确的实现差异。

还要区分“训练聚类层”和“最终公开标签”：代码中的 DEC/伪标签损失指导潜空间，但 `Trainer.GraphModel()` 最终调用 R `mclust` 对嵌入重新聚类并写入 `adata.obs["cluster"]`。

### 6. 总训练目标与两阶段流程

论文把图模型目标概括为

$$
\mathcal L=
\gamma_1\mathcal L_{graph}
+\gamma_2\mathcal L_{KL}
+\gamma_3\mathcal L_{Bernoulli}
+\gamma_4\mathcal L_{cluster}.
$$

代码实际执行顺序是：

1. 训练初始峰自编码器；
2. 计算峰重要性并筛峰；
3. 用初始嵌入建立 KNN 图；
4. 预训练图模型，只含图重建、峰重建和 KL；
5. K-means 初始化中心；
6. 联合训练图重建、峰重建、KL、DEC 和伪标签损失；
7. 导出嵌入与插补概率，再用 `mclust` 生成最终标签。

`GraphEmbeddingModel.loss_function()` 的默认权重是 `wADJ=10, wX=5, wKL=1, wDEC=1`。其中图重建在代码中使用 BCE，而论文公式描述为平方误差；峰重建还额外乘以 0.5。论文列出的 $10,5,1,1$ 与代码数字相同，但论文符号所对应的损失顺序不能无条件等同于代码变量。

### 7. 图和补充材料提供了什么证据

- 图 1 给出完整流程：初始 AE、峰选择、KNN 图、图 VAE、Bernoulli 插补与聚类优化。
- 图 2 在模拟数据中改变深度、噪声和 dropout，以 ARI、NMI、F1 检验鲁棒性。
- 图 3–4 在 11 个真实 scATAC 数据集上比较聚类和可视化；主结论是 scAGDE 的整体生物保留与分群表现领先或接近领先。
- 图 5 的消融分别检验 AE 表征构图、Bernoulli 解码器和图学习机制，支持三个部件各自贡献性能。
- 图 6 显示选中峰更偏向远端/内含子、与增强子特征重叠，并用基因组轨迹展示候选调控区域。
- 图 7 检验插补：插补后细胞与 meta-cell 的相关提高，Forebrain 的分群、DAR、motif 和 chromVAR 信号更清晰。
- 图 8–9 将最终嵌入接入 ArchR、motif、GO 和 scRNA 参考整合，提出人脑细胞类型及谷氨酸能神经元亚群的候选 CRE—TF—基因关系。

`MOESM1_ESM.pdf` 的 69 页补充信息进一步覆盖模拟设计、11 个真实数据集、约 80 万细胞的人胎儿图谱、构图/解码器/GNN 消融、超参数以及增强子和插补分析。`MOESM2_ESM.pdf` 是 reporting summary；`MOESM3_ESM.pdf` 是审稿与作者回复，审稿人也明确指出公开仓库缺少完整论文分析脚本。这些补充证据强化了基准覆盖，但并未把相关性和富集结果提升为实验因果验证。

### 8. 论文与本地代码对应

本地代码快照：`5da06f51dca7df2c59cc4a7ba270efc6f7356ad8`。

| 论文机制 | 本地代码 | 对应程度 |
|---|---|---|
| 二值化输入 | `scAGDE/utils.py::prepare_data` | Exact |
| 初始变分 AE | `ChromatinAccessibilityAutoEncoder` | Partial：结构匹配，但代码未实现论文陈述的 $\beta=0.5$ |
| 权重驱动峰选择 | `Trainer.CountModel`、`peakSelect` | Partial：代码用标准差，论文写方差 |
| 初始嵌入 KNN 图 | `utils.get_adj`、`Trainer.GraphModel` | Exact |
| GCN 高斯编码器 | `GCNEncoder` / `GCNGaussianSample` | Exact |
| 内积图解码器 | `sigmoid(z @ z.T)` | Partial：解码器匹配，代码损失为 BCE 而非论文平方误差 |
| Bernoulli 峰解码/插补 | `Decoder`、`encodeBatch(impute=True)` | Exact |
| DEC 目标分布与伪标签 | `ClusterAssignment`、`target_distribution`、`BCE` | Partial：初始阈值不同 |
| K-means 初始化 | `GraphEmbeddingModel.init_center` | Exact |
| 最终标签 | `trainer.py` → `mclust_R` | Partial：不是直接取训练期聚类层输出 |
| 大规模批训练 | `Trainer_scale` / `GraphEmbeddingModel_scale` | Partial：每批图与网络结构不同于标准路径 |
| Harmony 后处理 | 本地包与 notebooks | Not found |
| 全部主图/补充图复现脚本 | 本地包 | Not found；教程只覆盖使用范例和部分下游分析 |

### 9. 结果解释边界

1. 峰重要性来自模型权重离散度，不是峰对某个表型的因果效应。
2. KNN 图由第一阶段表征决定；若初始表征受批次或低质量细胞支配，错误邻接会被第二阶段传播。
3. 插补概率是模型平滑后的估计，可能强化真实弱信号，也可能强化模型偏差；应同时保留原始矩阵并做独立验证。
4. DEC 目标和伪标签会使簇更紧，但也可能过早固化错误分群。阈值、簇数和随机种子需要敏感性检查。
5. 图 8–9 的 CRE、motif、共可及性和表达一致性适合生成调控假设，不能替代扰动实验。
6. 公开代码足以运行核心方法，却不是论文所有基准和生物图的冻结复现包；论文公式与当前代码之间的差异必须保留。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scAGDE Summary

### Motivation and Novelty

Single-cell ATAC-seq measures chromatin accessibility at single-cell resolution, but the resulting cell-by-peak matrix is sparse, high-dimensional, and nearly binary. This makes cell-type identification, peak selection, imputation, and regulatory interpretation difficult, especially for low-depth or high-dropout datasets.

scAGDE addresses this by combining three ideas:

1. A chromatin accessibility autoencoder learns a preliminary representation and ranks peaks by encoder-weight variation.
2. A KNN cell graph built from the preliminary representation is used as topology for graph learning.
3. A graph autoencoder learns final cell embeddings while reconstructing both the cell graph and Bernoulli accessibility probabilities, with self-supervised clustering losses added during training.

The novelty is the explicit coupling of peak selection, cell topology, Bernoulli accessibility modeling, and cluster refinement in one scATAC-focused framework. The paper argues that this lets scAGDE outperform autoencoder-only and non-graph scATAC methods while producing biologically interpretable peaks and imputed accessibility signals.

### Method Overview

scAGDE takes a preprocessed scATAC-seq count matrix $\mathcal{X}\in R^{N\times M}$, filters peaks, and binarizes counts. It first trains a chromatin accessibility autoencoder on the binary matrix. The autoencoder output serves two purposes: its latent representation defines nearest-neighbor cell topology, and its first-layer encoder weights define peak importance scores. The default workflow selects the top 10,000 peaks.

The selected peak matrix and KNN graph are passed to a GCN-based graph autoencoder. The encoder produces a topological latent embedding $\mathbf{Z}$. One decoder reconstructs the cell graph through latent inner products, while a Bernoulli decoder estimates each peak's probability of being accessible. The Bernoulli probabilities are used as imputed accessibility values.

The model also includes self-supervised clustering. Cluster centers are initialized from K-means; soft assignments are sharpened into a target distribution; high-confidence assignments become pseudo-labels. The final objective combines graph reconstruction, variational KL regularization, Bernoulli accessibility likelihood, and clustering loss.

In the released code, most of this pipeline is implemented in `scAGDE/trainer.py`, `scAGDE/model.py`, `scAGDE/layer.py`, and `scAGDE/loss.py`. Important code-paper differences remain: the first autoencoder loss does not implement the paper's stated $\beta=0.5$ KL weight, peak importance uses standard deviation rather than variance, graph reconstruction uses BCE rather than squared error, and final public-API cluster labels are assigned by R `mclust` on learned embeddings.

### Evaluation

The paper evaluates scAGDE across simulation, real scATAC benchmarks, architecture ablations, peak interpretation, imputation, and human brain regulatory analysis.

On simulated bone marrow ATAC datasets, scAGDE is robust to reduced fragment depth, increasing noise, and increasing dropout, measured by ARI, NMI, and F1. On 11 real scATAC datasets, it reports the best aggregate bio-conservation score and high ARI on most datasets compared with scABC (*Nature Communications*, 2018), cisTopic (*Nature Methods*, 2019), SnapATAC (*Nature Communications*, 2021), Signac (*Nature Methods*, 2021), ArchR (*Nature Genetics*, 2021), SnapATAC2 (*Nature Methods*, 2024), SIMBA (*Nature Methods*, 2024), SCALE (*Nature Communications*, 2019), SAILER (*Bioinformatics*, 2021), PeakVI (*Nature Methods*, 2022), and BAVARIA (*Nature Machine Intelligence*, 2022).

For visualization and downstream scATAC analysis, the paper also compares against EpiScanpy (*Nature Communications*, 2021), which is used mainly as a package-level baseline for dimensionality reduction and peak-selection behavior.

Ablations support the AE-derived graph, Bernoulli decoder, and GNN structure. Peak-selection analyses show scAGDE-selected peaks are more often distal/intronic and more enhancer-like than EpiScanpy-selected peaks. Imputation analyses show improved cell-to-meta-cell correlation, more Forebrain DARs, stronger motif enrichment, and sharper chromVAR TF deviation patterns. Human brain analysis uses scAGDE embeddings with ArchR, marker databases, motif enrichment, GO analysis, and scRNA integration to annotate cell types and propose regulatory differences among glutamatergic neuron subclusters.

The strongest validated claims are clustering/embedding performance and model-component contribution. The regulatory claims are plausible and well supported by enrichment and co-accessibility evidence, but they remain candidate mechanisms rather than causal enhancer validation.

### Reproducibility

**Rating: 3/5.**

Strengths:

- The paper provides open code at `https://github.com/Hgy1014/scAGDE`.
- The acquired repository includes a Python package, MIT license, requirements, example data, and tutorials for end-to-end use, stepwise use, imputation, peak-selection analysis, and large-scale batch training.
- Core architecture pieces are present in code: autoencoder, peak scoring, KNN graph, GCN encoder, graph decoder, Bernoulli decoder, DEC-style target distribution, pseudo-label loss, and mclust final clustering.

Limitations:

- Full scripts to reproduce all benchmark, ablation, and biological figure panels are not present in the released repository.
- Some paper equations differ from the released implementation: AE KL weighting, peak-score statistic, graph reconstruction loss, pseudo-label threshold, and loss-weight interpretation.
- Harmony batch-correction post-processing discussed in the paper was not found in the package or tutorials.
- The workflow depends on R `mclust`, and the wrapper has a silent degenerate fallback on one error path.
- Large-scale support exists through `Trainer_scale`, but it changes the graph construction and architecture relative to the standard method.

Overall, the code is sufficient to run the method and inspect core implementation choices, but not sufficient by itself to fully reproduce the paper's full benchmark suite and all biological analyses without additional data-processing scripts and parameter details.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
