---
layout: default
permalink: /paper-atlas/hex-ecf6f295/
title: "HEX"
nav: false
wide: true
description: "CODEX 等空间蛋白组技术可以在组织中同时测量很多蛋白，但成本高、流程复杂、需要专用仪器，难以直接进入常规临床流程。HEX 的目标是只用临床常规 H&E 切片，预测空间化的蛋白表达图，而不是只预测一个样本的平均分子值。 论文用同一组织切片的 H&E 与 40 重 CODEX 图像配准，切成约 50 微米的 tile。"
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
      <span>Nature Medicine · 2026</span>
    </div>
    <h1>HEX</h1>
    <p>AI-enabled virtual spatial proteomics from histopathology for interpretable biomarker discovery in lung cancer</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/lilab-stanford/HEX" target="_blank" rel="noopener noreferrer" aria-label="Open code for HEX">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## HEX 方法中文解读

### 它解决什么问题？

CODEX 等空间蛋白组技术可以在组织中同时测量很多蛋白，但成本高、流程复杂、需要专用仪器，难以直接进入常规临床流程。HEX 的目标是只用临床常规 H&E 切片，预测空间化的蛋白表达图，而不是只预测一个样本的平均分子值（原文 `paper.md:13-40`）。

### 核心想法

论文用同一组织切片的 H&E 与 40 重 CODEX 图像配准，切成约 50 微米的 tile。每个 H&E tile 输入病理基础模型 MUSK，再接一个三层回归头，同时输出 40 个蛋白标志物：

```text
H&E tile -> MUSK 特征 -> 256 维 -> 128 维 -> 40 个蛋白预测
                                      -> 按坐标拼成 virtual CODEX
```

训练时，FDS（Feature Distribution Smoothing）把相近表达量 bin 的特征均值/协方差做高斯平滑，减轻稀有或极不平衡标志物的回归偏差；ALF（Adaptive Loss Function）用可学习的形状 `alpha` 与尺度 `c` 调整残差尾部，降低 CODEX 噪声和离群值影响。公开代码在 `HEX_code/hex/utils.py` 和 `train_dist_codex_lung_marker.py` 中实现了这些模块。

推理时以滑动窗口扫描整张 WSI，把每个坐标的 40 维向量写回空间数组。论文还训练了 14 像素窗口/步长的高分辨率版本，用来显示更细的空间结构（`paper.md:371-377`）。

### MICA 如何使用 virtual proteomics？

MICA 同时接受 H&E tile 的 MUSK 特征和每个虚拟蛋白通道的 DINOv2 特征。蛋白特征作为 query，H&E 特征作为 key/value：

$$Q=M_{bag}P_q,\quad K=H_{bag}P_k,\quad V=H_{bag}P_v$$

$$\widetilde H_{coa}=\operatorname{softmax}(QK^T/\sqrt{d_k})V$$

这样蛋白空间信号可以引导模型关注 H&E 中相关的组织区域。随后两个模态分别经过 transformer 和池化，再做 concat 或 bilinear 融合，输出离散生存 hazard；代码还返回 co-attention 与模态注意力分数。该结构对应 `HEX_code/mica/models/model_coattn.py:12-123` 与论文 `paper.md:389-410`。

### 结果与解释

在约 755,000 个训练 tile、372 个独立 TMA 样本和 Bern 泛癌数据上，HEX 的 Pearson、Spearman、SSIM 和 MSE 均优于 CGAN/Virtual Multiplexer；五折验证的平均 Pearson r 为 0.790。MICA 在五个 NSCLC 队列、12 个额外癌种和 ICI 队列上提高预后或疗效预测，并揭示 responder 中 T helper/cytotoxic T-cell 共定位、non-responder 中免疫抑制性巨噬细胞/中性粒细胞聚集等空间 niche。

### 复现边界

GitHub 代码快照包含核心模型和训练控制流，但没有论文队列数据、完整 checkpoint、MUSK/DINOv2 权重环境或可直接运行的配置；`virtual_codex_from_h5.py` 的输入/输出目录仍是空的 TODO。因而架构匹配可以由源码核验，论文数值和临床结果目前只能以论文原始证据为准，不能声称已经端到端复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## HEX: AI-enabled virtual spatial proteomics from histopathology

### Problem

CODEX-scale spatial proteomics is expensive, instrument-intensive and difficult to scale clinically. Earlier H&E-to-molecular methods generally predicted bulk or a small number of markers, leaving intratumor spatial heterogeneity underused (`paper.md:13-40`).

### Method and novelty

HEX uses a pretrained pathology foundation model (MUSK) plus a 256-128-40 regression head to predict 40 immune, structural, lineage and functional protein intensities from each H&E tile. Feature Distribution Smoothing (FDS) addresses imbalanced target values and an Adaptive Loss Function (ALF) reduces sensitivity to noisy/outlier CODEX measurements. Sliding-window predictions are stitched into virtual CODEX maps. MICA then combines MUSK H&E features and DINOv2 virtual-protein features with CODEX-guided co-attention for prognosis and immunotherapy-response prediction.

### Evaluation

Training used about 755,000 matched tiles from ten NSCLC patients; technical validation included 372 independent TMA samples and 206 pan-cancer cores across 34 tissue types (`paper.md:41-57,95-115`). Fivefold cross-validation reported mean Pearson r 0.790, Spearman r 0.787, SSIM 0.949 and MSE 0.076 across 40 markers, with substantial gains over CGAN and Virtual Multiplexer (`paper.md:86-94`). Independent validation reported Pearson r 0.738, Spearman r 0.741, SSIM 0.875 and MSE 0.189 on Stanford-TMA, and Bern validation retained mean Pearson r 0.658 across 24 overlapping markers (`paper.md:95-115`).

For clinical use, the paper reports five NSCLC cohorts (2,150 patients), 12 additional TCGA cancer types (5,019 patients) and an ICI cohort (148 patients). HEX-enabled multimodal integration improved early-stage prognosis and immunotherapy-response prediction, while spatial co-expression patterns provided interpretable tumor-immune niches (`paper.md:116-217`).

### Reproducibility

The paper-linked GitHub snapshot is archived at commit `84ca63db87c78f7af9bf34428efc29f587140546`. It directly supports the regression/FDS/ALF control flow, virtual-map scatter, DINOv2 feature extraction and MICA co-attention/survival path. Reproducibility is **3/5**: core source is present, but CUDA/NCCL, MUSK/DINOv2 weights, robust-loss dependency, cohort data, checkpoints and several path variables are absent; no end-to-end run was verified. Claims about exact paper checkpoints or reported clinical numbers therefore remain paper-grounded rather than code-reproduced.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
