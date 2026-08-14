---
layout: default
permalink: /paper-atlas/chromfound-4c221f2b/
title: "ChromFound"
nav: false
wide: true
description: "ChromFound 是面向单细胞染色质可及性数据的基础模型。它不把固定的 peak 集合当作词表，而是把每个开放染色质区域（OCR）作为一个带有连续可及性数值、染色体编号、起点和终点坐标的 token。这使不同组织或新出现的 OCR 仍可被表示，避免固定 peak 词表造成的对齐缺失。 每个 OCR 的表示由四部分相加：染色体可学习 embedding、起点位置的正弦位置编码、终点位置的正弦位置编码，以及可及性数值的线性投影。"
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
      <span>2025</span>
    </div>
    <h1>ChromFound</h1>
    <p>ChromFound: Towards A Universal Foundation Model for Single-Cell Chromatin Accessibility Data</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/JohnsonKlose/ChromFound" target="_blank" rel="noopener noreferrer" aria-label="Open code for ChromFound">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ChromFound 方法说明

ChromFound 是面向单细胞染色质可及性数据的基础模型。它不把固定的 peak 集合当作词表，而是把每个开放染色质区域（OCR）作为一个带有连续可及性数值、染色体编号、起点和终点坐标的 token。这使不同组织或新出现的 OCR 仍可被表示，避免固定 peak 词表造成的对齐缺失（paper.md）。

每个 OCR 的表示由四部分相加：染色体可学习 embedding、起点位置的正弦位置编码、终点位置的正弦位置编码，以及可及性数值的线性投影。随后模型先在长度 256 的局部窗口内做 WPSA 注意力，再经降维后的 Mamba 模块处理长程依赖，并将结果残差加回原 OCR 表示（paper.md）。图 1 清楚展示了这一结构，以及四层编码器、池化和下游投影分支（figure_01.png）。

预训练时，作者在 197 万细胞上掩蔽零值和非零值 OCR，并只在掩蔽位置用 MSE 重建归一化后的可及性信号。论文报告了在聚类、细胞类型注释、ATAC-to-RNA 预测及增强子扰动分析上的结果（paper.md）。

代码仓库包含基因组坐标/染色体/value embedding、Mamba 主干、细胞 embedding 提取和细胞类型微调路径；例如 `cell_embedding.py` 读取 `.h5ad`、提取并平均池化 embedding，写入 `X_embedding`。但仓库未提供可检索到的预训练启动脚本、掩蔽 MSE 损失调用、预训练权重或数据。因此可把下游代码视为部分可用，而不能据此复现论文的完整预训练流程（cell_embedding.py）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ChromFound Summary

ChromFound is a scATAC-seq foundation model that treats each open chromatin region as a continuous, genome-aware token rather than selecting a fixed peak vocabulary. Its encoder combines local windowed attention with Mamba-based long-context mixing, then transfers representations to clustering, cell annotation, cross-omics prediction, and perturbation-oriented regulatory analyses (paper.md).

The paper pretrains on 1.97 million cells from a 2.64-million-cell collection across more than 30 tissues. It uses masked reconstruction of log-normalized accessibility values with MSE, explicitly masking both zero and non-zero values (paper.md). In reported clustering experiments, it gives average gains of 17.02% ARI, 10.39% FMI, 6.72% NMI, and 6.69% AMI over the evaluated baselines (paper.md).

The available GitHub code is a meaningful but incomplete match. It provides the input embedding/backbone model and scripts for embedding extraction and cell-type fine-tuning. It does not provide the pretraining launcher/loss loop, checkpoint, datasets, or enough preprocessing assets to reproduce the central pretraining result. The correct reproducibility assessment is therefore **partial**, not fully runnable.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
