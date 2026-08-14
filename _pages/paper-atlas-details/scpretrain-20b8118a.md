---
layout: default
permalink: /paper-atlas/scpretrain-20b8118a/
title: "scPretrain"
nav: false
wide: true
description: "单细胞 RNA 测序的细胞类型标注通常依赖少量人工标注细胞，但未标注细胞更多，并且包含有用的基因表达模式。仅用标注数据训练容易过拟合，也容易把平台、器官、物种和批次效应当成细胞类型信号。scPretrain 的目标是先利用多个未标注数据集学习可迁移的细胞表示，再用少量新数据集标注进行微调。 把每个未标注数据集的 K-means 聚类结果当作“伪标签”。"
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
      <span>Bioinformatics · 2022</span>
    </div>
    <h1>scPretrain</h1>
    <p>scPretrain: Multi-task self-supervised learning for cell type classification</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/ruiyi-zhang/scPretrain" target="_blank" rel="noopener noreferrer" aria-label="Open code for scPretrain">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scPretrain 方法详解

### 要解决的问题

单细胞 RNA 测序的细胞类型标注通常依赖少量人工标注细胞，但未标注细胞更多，并且包含有用的基因表达模式。仅用标注数据训练容易过拟合，也容易把平台、器官、物种和批次效应当成细胞类型信号。scPretrain 的目标是先利用多个未标注数据集学习可迁移的细胞表示，再用少量新数据集标注进行微调（论文 `scPretrain.md:1-9,35-46`）。

### 核心想法

把每个未标注数据集的 K-means 聚类结果当作“伪标签”。伪标签不是声称等于真实细胞类型，而是提供一个自监督分类任务：如果表示能够预测不同表达簇，就可能保留有助于后续细胞类型分类的结构。所有数据集共享一个 encoder，但每个数据集/聚类划分拥有独立分类头，以减轻批次效应。

### 输入、输出与流程

```text
多个未标注表达矩阵 X1...Xg
        |
        | 人/鼠基因映射、统一基因集合、缺失基因补零
        v
每个数据集按约 50/100/200 个细胞每簇生成三组 K-means 伪标签
        |
        v
共享 encoder + 数据集/划分专属分类头，多任务交叉熵训练
        |
        v
200 维细胞表示；在表示空间重新聚类并重复训练
        |
        v
带真实标签的新数据集：迁移匹配基因权重并微调
        |
        +--> 细胞类型预测
        +--> K-means/UMAP 聚类与可视化
        +--> RF、逻辑回归、SVM 等下游分类器
```

### 数学形式

给定表达矩阵 $X\in\mathbb{R}^{n\times s}$，第一阶段 K-means 近似求解

$$
\min_{C,\tilde Y}\|X-\tilde YC\|^2,
\quad \text{s.t. }\tilde Y\mathbf 1_{\tilde k}=\mathbf 1_n. \tag{3}
$$

得到的 $\tilde Y$ 是细胞到簇的分配矩阵。encoder $E_\theta$ 将一个 $s$ 维基因向量映射到低维表示 $h$。分类器输出 softmax 概率

$$
\nu_i=\frac{e^{t_i}}{\sum_j e^{t_j}}, \tag{1}
$$

并以交叉熵训练。多任务目标是

$$
\min_{\theta,\omega}\sum_{i=1}^{g}L(F_i(E_\theta(X_i)),\tilde Y_i). \tag{6}
$$

在第一轮训练后，用表示重新聚类：

$$
\min_{C',\tilde Y}\|E_\theta(X)-\tilde YC'\|^2,
\quad \text{s.t. }\tilde Y\mathbf 1_{\tilde k}=\mathbf 1_n. \tag{5}
$$

然后交替更新伪标签和 encoder。对有真实标签的目标数据 $(Z,Y)$，微调目标为

$$
\min_{\theta,\Phi}L(F_\Phi(E_\theta(Z)),Y). \tag{11}
$$

### 代码中可以直接核实的实现

- `data.py:140-166` 使用 FAISS K-means；默认 `avg_cluster_num=100`，生成三种簇数。
- `model.py:7-15,35-67` 共享一个 encoder，并为三个聚类粒度建立三组数据集专属线性头；所有任务的 `CrossEntropyLoss` 相加。
- `data.py:179-196` 在非 PCA 模式对输入执行 `log1p`。
- `finetune.py:12-38,40-96` 按基因名迁移预训练权重，在验证集准确率上早停，并计算 accuracy、Kappa、AUPRC、AUROC。
- `rf_svm_lr.py` 和 `clus.py` 将 encoder 表示用于随机森林/逻辑回归/SVM 或 UMAP。

需要注意，源码中的 encoder 实际是一个 `Linear(num_g,200)` 层；论文中描述的更深分类器和完整十轮实验调度没有在当前快照中完全重现。

### 论文报告的结果

论文在 60 个来自 29 个器官、10 个平台的人/鼠数据集上进行留一数据集交叉验证：59 个数据集用于预训练，剩余一个用于微调，循环 60 次。平均 accuracy、Cohen's Kappa、AUPRC、AUROC 分别为 0.939、0.882、0.841、0.975；无预训练对照为 0.888、0.747、0.784、0.926。表示直接聚类的 Rand index 为 0.18，对照为 0.15（`scPretrain.md:136-165`）。

图像证据显示，Figure 2 的多数点位于无预训练对角线之上，Figure 3 的 scPretrain UMAP 簇更紧凑，Figure 4 中使用随机森林等传统分类器的表示也大多高于对照。

### 复现边界与开放问题

当前代码目录缺少 `dataset/*.h5`、缓存伪标签、正交基因表和预训练权重；因此无法在此工作区复现论文的精确数值。随机划分没有固定随机种子，且论文所述十轮“重新聚类-训练”在 README 中被拆成手动 CLI 阶段。上述内容是代码/数据范围内的缺口，不应被表述成已经验证的运行结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scPretrain: Multi-task self-supervised learning for cell type classification

### Problem

Single-cell type annotation is commonly trained only on labelled cells, although unlabelled cells are more abundant and carry information about gene activity. The paper argues that this supervised-only setup can overfit and amplify platform, organ, species, and other batch effects (`scPretrain.md:1-9`).

### Proposed Method

scPretrain pretrains one gene-expression encoder on many unlabelled datasets. K-means partitions each dataset into pseudo-labels at three cluster granularities; dataset/partition-specific classifiers train the shared encoder with summed cross-entropy. The encoder is then repeatedly re-embedded and reclustered, and finally fine-tuned with a small labelled target set. The resulting representation can also feed K-means/UMAP, random forest, logistic regression, or SVM (`scPretrain.md:35-42`, `62-132`).

### Evaluation

The study uses 60 human and mouse datasets spanning 29 organs and 10 platforms, with a shared 17,298-gene vocabulary. Leave-one-dataset-out evaluation pretrains on 59 datasets and fine-tunes on the remaining dataset, repeated 60 times (`scPretrain.md:136-144`). Relative to the same neural classifier without pretraining, scPretrain reports mean accuracy 0.939 vs 0.888, Cohen's Kappa 0.882 vs 0.747, AUPRC 0.841 vs 0.784, and AUROC 0.975 vs 0.926; significantly better results occur on 39, 38, 47, and 55 datasets for those metrics respectively (`scPretrain.md:146-148`). Representation-only clustering reaches Rand index 0.18 vs 0.15 (p<0.05), and RF/SVM feature comparisons show most points above the identity line (`scPretrain.md:159-165`).

### Reproducibility

The GitHub snapshot at commit `b63008d57dfc057bda27c92a1a45e5754bf16b09` contains the principal PyTorch modules and CLI commands. Direct source verification confirms K-means label generation, shared encoder plus three task-head banks, gene alignment, fine-tuning, UMAP, and conventional-classifier evaluation. However, the checked-in workspace lacks the required `dataset/*.h5` files, cached labels/gene lists, orthology table, and pretrained weight file; exact numerical reproduction is therefore not demonstrated. The source encoder is a single linear 200-D layer and the two representation-clustering phases are exposed as separate commands, so code-paper fidelity is medium rather than exact.

**Reproducibility rating: 3/5.** Core algorithms and interfaces are inspectable, but external data/model assets and experiment orchestration are required for a faithful rerun.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
