---
layout: default
permalink: /paper-atlas/unifiedmultimodallearning-9ebe567c/
title: "UnifiedMultimodalLearning"
nav: false
wide: true
description: "基因扰动、化学药物、剂量/效能、组合处理以及不同细胞类型的数据通常由不同实验产生。许多已有模型只适用于一种扰动或一种细胞背景，因此难以预测未见过的扰动，也难以复用异质数据。X-Pert 将这些干预抽象成作用于细胞系统的统一外部操作。 X-Pert 有两个核心模块：Perturbation Perceiver 把不同类型和数量的扰动压缩到固定长度的 Perturbverse；"
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
    <h1>UnifiedMultimodalLearning</h1>
    <p>Unified multimodal learning enables generalized cellular response prediction to diverse perturbations</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1101/2025.11.13.688367" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for UnifiedMultimodalLearning">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Chen-Li-17/X-Pert" target="_blank" rel="noopener noreferrer" aria-label="Open code for UnifiedMultimodalLearning">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## X-Pert 方法解读

### 要解决的问题

基因扰动、化学药物、剂量/效能、组合处理以及不同细胞类型的数据通常由不同实验产生。许多已有模型只适用于一种扰动或一种细胞背景，因此难以预测未见过的扰动，也难以复用异质数据（`paper.md:19-29`）。X-Pert 将这些干预抽象成作用于细胞系统的统一外部操作。

### 核心想法

X-Pert 有两个核心模块：Perturbation Perceiver 把不同类型和数量的扰动压缩到固定长度的 Perturbverse；Cell Encoder 将这些扰动 token 注入原始细胞的基因 token 序列，预测完整的扰动后表达谱（`paper.md:33-45`）。

```text
基因文本嵌入 / 分子 Morgan 指纹
          -> 类型专用 MLP（统一到 512 维）
          -> 12 个可学习 latent 的 Perceiver Resampler
          -> 12 x 512 Perturbverse token
          -> 与基因身份、表达值、影响 token 做 gated cross-attention
          -> gene self-attention
          -> 表达值 decoder
          -> 扰动后基因表达预测
```

### 计算步骤

1. 基因扰动由 GPT-4o 生成基因功能描述，再用 `text-embedding-ada-002` 得到 1536 维向量；化合物由 SMILES 计算 1024 维 RDKit Morgan 指纹。两个三层 MLP 将它们投影到 512 维公共空间（`paper.md:288-302`）。
2. 对剂量或基因效能，使用可学习向量逐维缩放扰动嵌入：

$$\widetilde{\mathbf x}_i=\mathbf x_i\odot(s_i\mathbf w).$$

基因效能为 $s_i=(\mu_p-\mu_c)/\mu_c$，化学剂量使用 log10 变换（`paper.md:304-324`）。
3. Perceiver 用 learned latent 作为 query，把扰动输入与 latent 拼成 key/value，并通过注意力和残差 FFN 输出固定的 12 个 token（`paper.md:272-286`）。这些 token 可展平为 6144 维，用于扰动检索和跨模态比较（`paper.md:460-462`）。
4. Cell Encoder 为每个基因构造身份 token、表达值 token 和影响 token。遗传扰动的影响是 one-hot 标记；药物扰动的影响是 GraphDTA 预测的蛋白–分子亲和度（`paper.md:328-370`）。
5. Gated cross-attention 让基因状态读取 Perturbverse，再用 self-attention 建模基因–基因依赖。论文设置 12 层、每层 8 个头（`paper.md:372-412`）。
6. decoder 为每个基因输出标量表达值，基本损失是 MSE。遗传和化学数据联合训练时增加 RBF-kernel MMD，整体目标为 $\mathcal L_{MSE}+0.2\mathcal L_{MMD}$（`paper.md:414-458`）。

### 结果如何验证

论文在 Replogle2022、Norman2019、Sciplex-3、CMAP 和 Tahoe-100M 等数据上评估 PCC、top-DEG $R^2$、Hallmark gene-set PCC、E-distance、cosine similarity 和 KNN accuracy。结果覆盖未见遗传扰动、组合/效能、化学扰动、跨细胞类型扩展、药物筛选和基因–药物对齐（`paper.md:56-80`, `107-246`, `464-550`）。

### 代码核查与限制

`X-Pert/xpert/models/` 中可以直接核对 Perceiver、12 个 latent、gated cross-attention、基因/数值/扰动 token 以及 expression decoder（`perturbation_perceiver.py:158-267,340-408`; `cell_encoder.py:39-264,324-476,549-575`）。但公开快照中没有找到顶层 MMD 训练组装；`examples/basic_usage.py` 创建 analyzer 时没有提供 model，而 analyzer 会直接抛出异常，scGPT 适配层的 `load_model` 和 `predict` 也仍是 `NotImplementedError`。因此架构证据较完整，端到端复现实验仍有明确缺口。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## X-Pert: Unified Multimodal Perturbation Modeling

### Problem

Perturbation-response datasets vary in modality (genetic or chemical), dose/efficacy, combinations, assay scale, and cell type. Existing predictors are usually tied to one perturbation type or cellular context, limiting transfer to unseen interventions and reuse of heterogeneous data (`paper.md:19-29`).

### Proposed Method

X-Pert treats an intervention and a cellular state as interacting modalities. GPT-derived gene perturbation embeddings and RDKit Morgan fingerprints are projected into a common space, resampled by 12 learned Perceiver latents, and used as conditional context for a transformer Cell Encoder. Gene identity, expression value, and impact tokens model the original cell; gated cross-attention captures gene–perturbation effects, and self-attention captures gene–gene dependencies (`paper.md:33-45`, `270-412`). The output is a genome-wide expression prediction. A paper-level MSE objective is augmented with RBF-MMD (α=0.2) for joint genetic/chemical training (`paper.md:426-458`).

### Evidence From Evaluations

Genetic tests use Replogle2022 K562/RPE1 and Norman2019 with 8:2 perturbation splits; X-Pert improves top-DEG R² and Hallmark gene-set PCC over linear, GEARS, CellOracle, scGPT, scFoundation, and other baselines (`paper.md:56-80`). Combination and efficacy experiments show support for unseen combinations and graded response (`paper.md:107-135`). Chemical tests cover Sciplex-3 and CMAP, including unseen molecules/cell types and dose effects (`paper.md:136-165`). With 65,768 Tahoe-100M pseudo-bulk samples, X-Pert supports disease-signature drug screening, although plate effects require regression residual correction (`paper.md:166-196`, `540-550`). Adding diverse cell types improves K562 generalization and Perturbverse KNN structure (`paper.md:198-225`). Joint CMAP training aligns genetic and chemical perturbations and enables drug retrieval against DGIdb and SelleckChem references (`paper.md:227-246`).

### Reproducibility

The linked GitHub snapshot is `Chen-Li-17/X-Pert` commit `623c7f8`. Direct source verification confirms the Perceiver, 12 learned latents, modality encoders, gated cross-attention, gene/value/impact token construction, and expression decoder (`X-Pert/xpert/models/perturbation_perceiver.py:158-267,340-408`; `X-Pert/xpert/models/cell_encoder.py:39-264,324-476,549-575`). The public snapshot does not expose an inspected top-level MMD loss assembly or full experiment training scripts. Its example constructs `PerturbationAnalyzer` without a model and therefore raises at analysis time; the bundled scGPT shim also leaves `load_model` and `predict` unimplemented (`examples/basic_usage.py:93-108`; `xpert/analysis/analyzer.py:73-105`; `xpert/external_model/scgpt/__init__.py:11-15`). Reproducibility is therefore medium: the architectural core is inspectable, but end-to-end reproduction requires missing or external assets/scripts.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
