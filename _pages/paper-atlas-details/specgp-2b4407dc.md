---
layout: default
permalink: /paper-atlas/specgp-2b4407dc/
title: "SpecGP"
nav: false
wide: true
description: "完整 N-糖肽的二级质谱同时包含肽段碎片和复杂分支糖链的 B/Y 离子；不同碰撞能量下，这些诊断离子的强度会变化。SpecGP 的目标是根据糖肽结构、前体电荷和碰撞能量预测结构化 MS/MS 谱，并同时预测保留时间，从而帮助糖链异构体区分和 StrucGP 结果重打分。该定位来自论文摘要。 普通谱图预测若只覆盖有限的糖链碎片，就难以保留异构体所需的诊断信息。"
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
      <span>Computational Tools</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>SpecGP</h1>
    <p>SpecGP as a transformer-based model for predicting energy-adaptable structural spectra of glycopeptides</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Sun-GlycoLab/SpecGP" target="_blank" rel="noopener noreferrer" aria-label="Open code for SpecGP">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpecGP 方法解读

### 它要解决什么问题？

完整 N-糖肽的二级质谱同时包含肽段碎片和复杂分支糖链的 B/Y 离子；不同碰撞能量下，这些诊断离子的强度会变化。SpecGP 的目标是根据糖肽结构、前体电荷和碰撞能量预测结构化 MS/MS 谱，并同时预测保留时间，从而帮助糖链异构体区分和 StrucGP 结果重打分。该定位来自论文摘要（`paper.md:12`）。

### 核心想法

普通谱图预测若只覆盖有限的糖链碎片，就难以保留异构体所需的诊断信息。SpecGP 对 B/Y 离子的组成建立表示：补充材料以 HexNAc1Hex1 为例，说明其嵌入由 B 单元离子嵌入线性组合而成，作为 Transformer 解码器 query 与编码后的糖肽特征做 cross-attention，最后预测该离子的强度（`supp.md:261-273`）。

```text
修饰肽序列 + 糖链图 + 候选 B/Y 离子组成 + 电荷/碰撞能量
  -> 图结构 Transformer 编码
  -> 以碎片组成为 query 的解码
  -> 肽段、Y 离子、B 离子强度 + 保留时间
  -> 与实验谱比较，可用于候选结构重打分
```

### 代码中可直接确认的流程

`GPSMDataset` 从序列、糖链、m/z、实验强度、碰撞能量、电荷和保留时间构造样本，并将肽键、肽-糖键和糖-糖键组成一张图（`SpecGP_repo/src/dataloader.py:351-472`）。`collate_fn` 负责对不同数目的肽/Y/B 离子补齐和打包（`src/dataloader.py:140-250`）。

模型由 Encoder、线性/归一化连接和 Decoder 构成，并有 `pep_out`、`y_out`、`b_out`、`rt_out` 四个输出头（`src/model.py:755-795`）。`forward` 返回保留时间与各类离子强度预测（`src/model.py:841-938`）。训练脚本加载 YAML 和 pickle 数据，计算损失、进行梯度裁剪并保存 `last.pt`/`best.pt`（`train.py:274-406`）；预测脚本加载权重并生成含总览和碎片明细的 XLSX（`predict.py:445-519`）。

### 多能量与下游应用

补充图说明低 HCD 倾向产生较大的 Y 离子和较大的 B 离子，而较高 HCD 产生较小的 Y/B 离子；补充图 S4 的示例跨 HCD 6-40%（`supp.md:311-333`）。S5 说明可先预测能量依赖谱图，再求和得到模拟 SCE 谱图（`supp.md:339-348`）。

重打分时，补充说明将 StrucGP 的正常、decoy 和校正候选输入 SpecGP，计算谱图余弦相似度与 RT 分数，再与原始 StrucGP 分数整合，并按 1% target-decoy FDR 筛选（`supp.md:121-144`）。这描述了论文工作流；本次限定代码审阅尚未逐行验证分数公式和 FDR 实现。

### 证据边界

Nature 采集页只有摘要、图和可用性信息，未包含完整 Methods/Results。因此，论文的精确损失公式、超参数、主文数值结果和 SSWT 细节应视为 **Not found in acquired primary text**，不能由图像或代码名称补写。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpecGP

SpecGP is a transformer-based predictor for energy-adaptable structural MS/MS spectra of intact N-glycopeptides. The central challenge is that a glycopeptide combines a peptide with a branched glycan, so standard spectrum predictors can lack the fragment coverage and energy sensitivity needed for structural/isomeric interpretation. The paper presents attention-enhanced B/Y glycan-fragment encoding, collision-energy-aware spectra and a joint retention-time output (abstract `paper.md:12`).

The available evidence supports this high-level pipeline. The supplement explains composition-derived B/Y fragment queries and their decoder cross-attention (`supp.md:261-283`); the checked source builds peptide-glycan graphs and m/z masks (`SpecGP_repo/src/dataloader.py:351-472`), then returns peptide/Y/B intensity predictions and RT from four heads (`src/model.py:781-793,841-938`). Fig. 1 visually matches that arrangement.

Evaluation is represented by the inspected figures: Fig. 2 compares spectrum prediction with DeepGP and DeepGlyco; Fig. 3 evaluates collision-energy behavior; Fig. 4 presents retention-time prediction; Fig. 5 addresses isomer discrimination; and Fig. 6 applies predicted spectra/RT to StrucGP rescoring. Supplementary text adds that energy-specific predictions can be summed for stepped-collision-energy spectra and that rescoring integrates cosine-similarity and RT scores with original StrucGP scores before a 1% target-decoy FDR (`supp.md:121-169,339-348`). The captured publisher page is preview-only, so main-text performance numbers and loss equations were not available for verification.

Reproducibility is **partial**. GitHub code is available and this workspace contains commit `d0492b56decf250b5e1e200bd9bed8df49cc1458`; the paper also lists ProteomeXchange/iProX datasets and Code Ocean (`paper.md:98-107`). Training and prediction scripts are present, but their default pickle datasets and checkpoints were not supplied or executed. The code-paper fidelity is **medium**: the core graph model, training loop and workbook predictor are directly verified, while the exact self-supervised weighting, score-combination/FDR path and a custom-fragment public interface remain partial or not found.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
