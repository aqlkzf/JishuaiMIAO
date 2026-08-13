---
layout: default
permalink: /paper-atlas/virtues-000db3ae/
title: "VirTues"
nav: false
description: "空间蛋白组数据的难点不是只有图像分辨率：不同队列使用不同的 marker panel、成像技术和噪声范围。固定通道数的模型难以迁移到新 panel，也难把蛋白的生物学关系带入 token。VirTues 希望学习一个可复用的“虚拟组织”表示，让同一个 backbone 支持 marker 重建、细胞分割与分型、niche/组织表征、检索和临床预测。"
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
      <span>Nature · 2026</span>
    </div>
    <h1>VirTues</h1>
    <p>The Virtual Tissues foundation model resolves spatial proteomics across scales</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/bunnelab/virtues" target="_blank" rel="noopener noreferrer" aria-label="Open code for VirTues">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## VirTues 方法中文讲解

### 它要解决什么问题？

空间蛋白组数据的难点不是只有图像分辨率：不同队列使用不同的 marker panel、成像技术和噪声范围。固定通道数的模型难以迁移到新 panel，也难把蛋白的生物学关系带入 token。VirTues 希望学习一个可复用的“虚拟组织”表示，让同一个 backbone 支持 marker 重建、细胞分割与分型、niche/组织表征、检索和临床预测。

### 核心想法

模型把每个 marker 的图像 patch 和该蛋白的 ESM-2 序列 embedding 融合，再用两种稀疏注意力分别学习“同一空间位置上的 marker 关系”和“同一 marker 在组织中的空间关系”。训练时随机遮挡 token，让解码器恢复原图；编码器中的 patch summary token 被保留下来，供后续细胞、niche 和组织级任务使用。

```text
多通道图像 + marker 身份
        │ 8×8 patch；ESM-2 marker embedding；线性投影后相加
        ▼
图像 token 网格 + 可学习 patch summary token
        │ 独立遮挡 / 整个 marker 遮挡 / 整个 niche 遮挡
        ▼
VirTues 编码器
  marker attention：同一位置跨通道
  spatial attention：同一通道跨位置
        ▼
patch summaries ──► cell / niche / tissue 表征
        │
        └─ 每个通道独立解码 ──► 重建已测或新 marker
                         └─ 冻结 backbone 的 U-Net ──► 实例和细胞类型 mask
```

### 计算流程

1. **Token 化。** 每个通道切成 (8\times8) patch。图像 patch 向量和 ESM-2 marker 向量分别投影到 (d_{model})，再相加；每个空间位置另放一个 patch summary token。这样既保留通道身份，也把蛋白序列层面的先验带进模型。
2. **Mask。** 训练时每个通道随机遮挡 60–100% 的 patch token；论文还测试整条 marker 全遮挡以及一个空间 niche 的所有 marker 全遮挡。被遮挡 token 用可学习 mask token 替换，但仍带有 marker 信息。
3. **编码器。** 16 个 transformer block 交替使用 marker attention 和 spatial attention，每个 block 8 个 head，并使用二维 rotary position embedding 和 pre-layer normalization。前者只在同一位置交流，后者只在同一通道交流，从而避免对全部 (MHW) token 做昂贵的全注意力。
4. **解码器。** 对每个目标通道，把可见编码 token、遮挡位置和一份 patch summary token 副本组成一组，逐通道解码并用线性层恢复像素。新 marker 可以作为全遮挡通道输入，直接做 zero-shot 重建。
5. **多尺度表示。** 细胞表示来自多个重叠 (128\times128) crop（stride 42）中、按细胞像素交叠数加权的 patch summary 平均。niche/组织表示使用不重叠 crop，少于 30% 组织覆盖的 crop 被排除；无监督检索使用简单平均，有监督任务使用 ABMIL 的动态权重平均。
6. **下游任务。** 冻结 VirTues 后，U-Net 风格的头从多个深度的 patch summary 预测实例特征和细胞类型 logits；实例分支用 InstanSeg 后处理，分型分支用 focal Tversky 与 cross-entropy 的等权组合。细胞 token 可接线性 probe，组织 token 可接 ABMIL 分类器，niche token 可用于 Wasserstein 检索和治疗反应分析。

预训练目标是所有像素（遮挡和未遮挡）上的均方误差：

$$\mathcal L_{MAE}=\|{\bf x}^{rec}-{\bf x}\|_2^2.$$

论文报告 15 个 IMC 队列（3,102 名患者、146 个 marker），并扩展到 32 个队列、4 种技术和 239 个 marker。代码中 `VirTuesPretrainingDataset` 返回图像、marker 索引和 patch mask，`VirTuesTrainer.compute_loss` 对拼接后的重建和目标直接求 MSE；`VirtuesSegmentationHead` 在 `torch.no_grad()` 下调用冻结的 encoder，再输出实例和语义 logits。

### 结果如何理解？

Fig. 2 的图像和相关系数显示，模型能在独立、整 marker 和整 niche 遮挡下恢复形态；对训练中未见的 marker，性能低于专门训练但仍高于简单均值/最高相关 marker 基线。Fig. 3 及 Extended Data Figs. 2–5 显示跨肺癌、乳腺癌、黑色素瘤和多技术队列的细胞分型与实例分割。Fig. 4 展示组织级诊断、相似组织检索和风险分层；Fig. 5 展示从细胞 summary 聚类得到的治疗反应 signatures，并在独立 Meyer 队列中进行 zero-shot 生存分层。Extended Data Fig. 1 进一步展示 IMC-only 模型向 CODEX、Orion 等技术的迁移。

比较对象包括 CA-MAE、KRONOS、Cellpose、InstanSeg、StarDist、MAPS、Astir 以及 Wang 等人的空间 predictor。图像支持“总体竞争力/优势”的方向，但并不意味着 VirTues 对每个细胞类别或每个 cohort 都最好；Extended Data Fig. 6 和 Fig. 10 也提醒，单靠生存标签或细胞比例基线可能产生看似显著的分层。

### 复现边界

仓库（commit `0e2c068c838d6132b1dd6e319b92bf14aa039f63`）包含模型、数据集、训练脚本、配置和三个 demo notebook，并链接预训练权重。直接代码证据支持可变通道输入、marker prior 相加、masked MSE 和冻结 U-Net 分割。仍需外部 spora 数据、预计算 ESM-2 embedding 和 checkpoint；论文中细胞/niche/组织聚合的实现未在本代码快照中找到，低层 attention 与部分 decoder 细节也只有 Partial 证据。不要把这些缺口从图示或 README 推断为已实现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## VirTues summary

### Problem

Spatial-proteomics studies vary in marker panels, imaging technology and noise, so fixed-panel encoders and cohort-specific pipelines transfer poorly. VirTues targets a shared, marker-aware representation that can be reused from cell to tissue and across cohorts.

### Proposed method

VirTues is a masked-autoencoder foundation model for multiplex imaging. It patches each channel at 8×8 resolution, adds an ESM-2 protein embedding to every channel's image tokens, and inserts learnable patch-summary tokens. A factorized transformer alternates marker attention (cross-channel interactions at one position) and spatial attention (within-channel interactions across positions). A per-channel decoder reconstructs masked images; patch summaries are then pooled into cell, niche and tissue representations for reconstruction, segmentation/typing, retrieval, diagnosis and biomarker discovery.

### Why prior workflows are insufficient

The paper identifies three limitations of conventional ViTs and existing spatial-imaging models: quadratic cost in both spatial and channel dimensions, tokenization that ignores marker-specific biological meaning, and fixed marker panels that prevent transfer to unseen combinations. CA-MAE and other baselines are used in the paper's scaling/benchmark comparisons; KRONOS, Cellpose, InstanSeg, StarDist, MAPS and Astir are task-specific comparators. The paper does not provide enough local bibliographic detail in the analyzed Methods passages to assign every comparator a venue/year, so no such metadata is inferred here.

### Evaluation and main findings

The core corpus contains 15 IMC datasets (3,102 patients, 146 markers); the extended corpus contains 32 cohorts across IMC, CODEX, Orion and MIBI (more than 5,100 patients and 239 markers). Figures show strong masked reconstruction under independent, marker and niche masking, useful zero-shot reconstruction of unseen markers, competitive or leading cell-type and instance segmentation across cohorts, tissue-level diagnostic performance, visually coherent retrieval, and attention patterns aligned with tissue regions and marker biology. In TNBC, four foundation-model-derived cell-cluster signatures predict immunotherapy response; transfer to an independent Meyer cohort stratifies disease-free survival. The paper reports comparisons against Wang et al. spatial signatures and simple tumour/T-cell/B-cell ratios, with VirTues generally stronger in the shown pre-treatment AUROC and transferred-risk analyses.

### Reproducibility

The GitHub snapshot (commit `0e2c068c838d6132b1dd6e319b92bf14aa039f63`) includes model/data/training modules, configuration examples, pretrained-weight links and three demo notebooks. Direct code checks confirm variable-channel inputs, additive marker-prior fusion, masked MSE training and a frozen U-Net segmentation head. Reproduction still depends on external spora datasets, ESM-2 marker embeddings and released checkpoints. The paper's cell/niche/tissue aggregation implementation was not located; encoder attention internals and exact decoder defaults are only partially linked. Overall code-paper fidelity: **medium (3/5)**.

### Scope note

Paper claims, image observations and code-verified behavior are kept separate in `doc_method.md`, `doc_code.md` and `figure_analysis.md`. Missing implementation details remain explicitly **Not found** or **Partial** rather than being inferred from the figures or README.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
