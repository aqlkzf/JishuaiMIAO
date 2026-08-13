---
layout: default
permalink: /paper-atlas/globalcellstategeneprogram-b16af0b4/
title: "GlobalCellStateGeneProgram"
nav: false
description: "论文的核心问题是：如何把大量来源不同、物种不同、测序平台不同的单细胞转录组数据放到同一个“细胞状态空间”里，并进一步理解基因扰动如何驱动细胞状态变化。传统整合模型或单细胞大模型可以产生嵌入，但作者认为它们对扰动响应预测仍不够好，尤其难以区分“基因功能本身的保守效应”和“不同起始细胞状态下的上下文特异效应”。 因此，论文提出的框架分两层：第一层学习全局细胞状态流形；"
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
      <span>Representation Models</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>GlobalCellStateGeneProgram</h1>
    <p>Global cell-state and gene-program representations reveal conserved and context-specific perturbation responses of cells</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.05.16.725005" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GlobalCellStateGeneProgram">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/xingjiepan/SCMG" target="_blank" rel="noopener noreferrer" aria-label="Open code for GlobalCellStateGeneProgram">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SCMG 方法中文解读

### 这篇论文解决什么问题？

论文的核心问题是：如何把大量来源不同、物种不同、测序平台不同的单细胞转录组数据放到同一个“细胞状态空间”里，并进一步理解基因扰动如何驱动细胞状态变化。传统整合模型或单细胞大模型可以产生嵌入，但作者认为它们对扰动响应预测仍不够好，尤其难以区分“基因功能本身的保守效应”和“不同起始细胞状态下的上下文特异效应”。

因此，论文提出的框架分两层：第一层学习全局细胞状态流形；第二层把这个流形和 Perturb-seq 扰动数据结合起来，得到基因表达程序、扰动类别和少样本扰动预测模型。

### SCMG：全局细胞状态流形

SCMG（Single-cell Manifold Generator）是一个带对比学习的自编码器。输入是单细胞表达向量 $x_{in}$，编码器输出 512 维细胞状态嵌入：

$$z = encoder(x_{in})$$

解码器不是只接收 $z$，还接收数据集身份 $A$，输出重构表达：

$$x_{decode} = decoder(z, A)$$

这个设计的含义是：编码器尽量不依赖数据集标签，只学习“生物学细胞状态”；解码器再根据数据集身份恢复对应实验条件下的表达分布。论文 Methods 在 `paper.md:347-356` 描述了这一点；代码中的 `CellEmbedder` 直接实现了 512 维 encoder、64 维 dataset embedding 和 dataset-conditioned decoder（`SCMG/scmg/model/contrastive_embedding.py:48-71`）。

### 对比学习如何去批次效应？

作者先对相似或重叠的 scRNA-seq 数据集做两两整合，找跨数据集的 mutual K nearest neighbors（mKNN，K=10），把这些细胞对当作“相同或相近生物状态”的正样本。对于正样本细胞 $i,j$，再随机采样一个细胞 $k$ 作为负样本。目标是让正样本距离 $d_{i,j}$ 小于到负样本的距离。论文给出的对比损失是：

$$L_{contrastive}(i,j,k) = softplus(d_{i,j} - d_{i,k}) + softplus(d_{i,j} - d_{j,k})$$

总损失还包括嵌入向量 L2 正则和表达重构 MSE。注意：当前转换得到的 `paper.md` 中总损失公式和 program score 公式有部分符号丢失，因此这里不凭空补全，只保留已经能从正文和代码确认的部分。代码中对应的损失函数位于 `SCMG/scmg/model/contrastive_embedding.py:73-115`。

### 训练数据和标准基因集

论文用 36 个训练 scRNA-seq 数据集，另外 3 个数据集用于 zero-shot benchmark。人和鼠的数据先映射到共同标准基因集，最终包含 18,108 个基因（`paper.md:362-386`）。缺失的标准基因在表达矩阵中置 0，并记录缺失基因以避免重构损失受到未测量基因影响。代码中 `get_Xs_from_anndata` 和 `standardize_adata` 都实现了按标准基因集重排、零填充和归一化的逻辑（`SCMG/scmg/model/manifold_generation.py:14-44`；`SCMG/scmg/preprocessing/data_standardization.py:130-162`）。

### 整体计算流程

```text
多来源 scRNA-seq
  └─ 标准基因集对齐 + 1e4 归一化 + log1p
      └─ 两两数据集整合，找 mKNN 正样本细胞对
          └─ SCMG 对比自编码器
              ├─ encoder：表达 -> 512 维细胞状态 z
              ├─ contrastive loss：相似细胞拉近，负样本推远
              └─ decoder：[z, dataset identity] -> 重构表达
                  └─ 全局细胞状态流形、query cell 投影、解码表达

SCMG 流形 + Perturb-seq
  ├─ human/10x-equivalent 解码
  ├─ 生理表达模式 PCA
  ├─ 扰动响应 pseudobulk shift PCA
  ├─ 联合空间聚类 -> gene-expression programs
  └─ MoE 功能嵌入 -> perturbation classes + few-shot prediction
```

### 基因表达程序如何得到？

作者希望定义主要的细胞状态转变轴。由于原始数据混有物种和平台差异，他们先把每个细胞编码到 SCMG 空间，再找最近的 human/10x 参考细胞，用该参考细胞的数据集 ID 作为 decoder 条件，得到“human/10x-equivalent”表达（`paper.md:425`）。Figure 3A 直观展示了这个流程。

之后作者把两类信号融合：

1. 全局细胞图谱中的生理表达模式；
2. 11,406 个扰动条件下的 pseudobulk 表达变化。

每类信号分别做 PCA 到 50 维，扰动 PCA 缩放到与生理 PCA 相同的标准差尺度，然后拼接成 100 维联合空间。作者用 correlation distance 建 5NN 图，再用 Leiden 聚类（resolution=10）故意过分裂，初始得到 187 个 cluster，随后人工合并和注释，去掉没有明确表达模式或富集结果的 mixed cell types（`paper.md:437-443`）。Figure 3E/F 显示了这些程序，包括 neuronal、epithelial、muscle、cell cycle、ribosome biogenesis、DNA replication/repair 等。

### 扰动功能嵌入和 MoE 模型

扰动部分的关键假设是：每个被扰动基因 $g$ 都有一个低维功能嵌入 $v_g \in \mathbb{R}^M$；在给定起始细胞状态 $z$ 时，扰动导致的表达变化 $\Delta y$ 可以通过一个依赖细胞状态的线性映射从 $v_g$ 得到。论文用 mixture-of-experts（MoE）实现这个想法：多个 expert 是线性映射，gating network 接收 SCMG 细胞状态嵌入并输出 expert 权重。论文设置为 $M=16$、$K=8$ experts、$N=18108$ readout genes（`paper.md:452-455`）。

代码中的 `CatRealRegressor` 与这个设计相符：它用 categorical embedding 表示被扰动基因，用多个 linear expert 输出表达变化，用 gate MLP 根据真实值上下文输入生成 softmax 权重，最后加权求和（`SCMG/scmg/model/perturbation_prediction.py:64-143`）。训练使用 masked MSE，并计算 Pearson correlation（`SCMG/scmg/model/perturbation_prediction.py:147-302`）。

### 少样本扰动预测

作者把 MoE 学到的基因功能嵌入用于 few-shot prediction。对于一个要预测的新细胞环境（例如 K562、RPE1 或 hESC），先从功能嵌入空间中用 K-means 选出 K 个代表性扰动基因，实验测量这些基因在目标环境中的扰动响应，然后训练 ridge regression 从功能嵌入预测 pseudobulk 表达变化。其余基因的响应由这个小样本模型预测（`paper.md:467`）。Figure 4D/E 和 Figure 6G/H 显示，few-shot 模型优于 zero-shot 和 train-set-mean baseline，且扰动效应越强预测越准确。

### 代码复现度

它覆盖了核心可复用模型：SCMG encoder/decoder、对比损失、标准基因输入构造、query embedding/projection，以及通用 MoE 扰动预测器。

但论文图表和完整分析脚本不在这个仓库中。`SCMG/README.md:46` 明确指出 manuscript figures 的脚本位于另一个仓库 `SCMG_scripts`。

### 主要局限

- 转换后的论文 Markdown 丢失了部分公式符号，尤其是总损失和 program score 的完整显示公式。
- gene-expression program 和 perturbation class 的最终标签依赖人工合并与注释，自动复现难度较高。
- few-shot 预测准确率仍受扰动效应大小和细胞状态覆盖度限制；弱扰动信噪比较低。
- 当前流形强调人/鼠保守变化，可能弱化物种特异差异，论文讨论中也承认这一点（`paper.md:236`）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

The paper studies how to represent cell states and genetic perturbation responses in a shared coordinate system across heterogeneous single-cell datasets. Existing large single-cell foundation or integration models can embed cells, but the paper argues that they still struggle to predict perturbation responses and to separate conserved gene-function effects from cell-state-specific rewiring (`paper.md:9-15`, `paper.md:230-254`).

### Proposed Method

The authors introduce **SCMG** (Single-cell Manifold Generator), a contrastive autoencoder that learns a global 512-dimensional cell-state manifold. The encoder maps a transcriptome to a dataset-agnostic latent vector, while the decoder reconstructs expression using both the latent vector and dataset identity (`paper.md:347-356`). Pairwise mKNN links between biologically matched cells across datasets supply positive pairs, and random cells supply negatives for a softplus contrastive loss (`paper.md:353-356`).

The framework then uses SCMG to build downstream perturbation representations:

- decode cells into human/10x-equivalent expression profiles to suppress species/assay effects (`paper.md:425`);
- combine physiological expression patterns and perturbation pseudobulk shifts to define gene-expression programs (`paper.md:437-443`);
- train a mixture-of-experts model that learns perturbed-gene functional embeddings and cell-state-conditioned expression-shift maps (`paper.md:452-455`);
- use those embeddings for perturbation classes and few-shot prediction (`paper.md:461-467`).

### Main Results

SCMG is trained on 36 scRNA-seq datasets and evaluated on zero-shot integration, decoding, and projection tasks. The paper reports better dataset intermixing than scVI, Geneformer, scGPT, SCimilarity, and UCE while preserving cell-type structure (`paper.md:59-73`, `paper.md:395-407`). The global manifold supports query-cell projection and annotation without retraining (`paper.md:410`).

For perturbation analysis, the method derives gene-expression programs from a joint physiological/perturbation space, starting from 187 overclustered Leiden clusters before manual curation (`paper.md:443`). The MoE functional embedding is trained with `M=16`, `K=8` experts, and `N=18108` readout genes (`paper.md:455`), then clusters 608 reproducible perturbed genes into perturbation classes (`paper.md:461`). Few-shot perturbation prediction improves over zero-shot and train-set-mean baselines in RPE1, K562, and hESC contexts, with higher accuracy for larger perturbation effects (`paper.md:137-140`, `paper.md:195`).

### Reproducibility Notes

Data are available through a Hugging Face dataset, a global-pattern browser, and GEO accession `GSE295214` for hESC Perturb-seq (`paper.md:257-260`). The code availability section links the `SCMG` package and a separate `SCMG_scripts` repository for manuscript figure-generation scripts (`paper.md:263-266`).

The acquired code snapshot is the `SCMG` package at commit `29f44c98c5621d575a058b549e0fdde0ba31a730`. It directly implements the SCMG encoder/decoder, contrastive/reconstruction loss components, standard-gene matrix construction, query embedding/projection helpers, and a generic MoE perturbation-response regressor (`doc_code.md`). However, the cloned package does **not** include the manuscript `SCMG_scripts` workflows for gene-program curation, perturbation-class clustering, few-shot K-means/ridge evaluation, or figure generation. Overall code-paper fidelity is **medium**: core reusable model components match, but end-to-end paper reproduction is incomplete without the separate scripts and external data.

### Limitations

- Exact displayed total-loss and program-score formulas were not fully recoverable from the converted Markdown; missing glyphs are kept as gaps rather than reconstructed.
- Gene-expression program labels and perturbation-class merges involve manual curation, limiting fully automated reproducibility from the paper text alone.
- Predictive accuracy remains imperfect and depends strongly on perturbation effect size and cell-state coverage (`paper.md:140`, `paper.md:254`).
- Current global representations prioritize conserved human/mouse variation and may attenuate species-specific biology (`paper.md:236`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
