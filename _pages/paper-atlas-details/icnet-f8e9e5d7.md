---
layout: default
permalink: /paper-atlas/icnet-f8e9e5d7/
title: "ICNet"
nav: false
wide: true
description: "耳蜗模型已经可以高精度工作，但听觉中脑，特别是下丘（inferior colliculus, IC）的神经编码模型，难以同时保持毫秒级时间分辨率、神经反应的完整统计结构，并处理数小时记录中的非平稳性。ICNet 用九只麻醉沙鼠、每只 512 个电极通道的多单位活动（MUA）来学习声音到 IC 神经活动的映射。 模型是卷积编码器-解码器。编码器把声音波形 s 压缩成共享瓶颈表示 r-hatb；九个动物专属解码器把它变成每个单位在每个约 1."
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
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>ICNet</h1>
    <p>Modelling neural coding in the auditory midbrain with high resolution and accuracy</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/fotisdr/ICNet" target="_blank" rel="noopener noreferrer" aria-label="Open code for ICNet">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ICNet 方法中文解释

### 要解决的问题

耳蜗模型已经可以高精度工作，但听觉中脑，特别是下丘（inferior colliculus, IC）的神经编码模型，难以同时保持毫秒级时间分辨率、神经反应的完整统计结构，并处理数小时记录中的非平稳性。ICNet 用九只麻醉沙鼠、每只 512 个电极通道的多单位活动（MUA）来学习声音到 IC 神经活动的映射。

### 核心想法

模型是卷积编码器-解码器。编码器把声音波形 `s` 压缩成共享瓶颈表示 `r-hat_b`；九个动物专属解码器把它变成每个单位在每个约 1.3 ms 时间 bin 中的概率分布。Poisson 只有一个 rate 参数，无法表达 IC 中常见的低于 Poisson 的方差；ICNet 使用五类 categorical 分布表示 0、1、2、3、4 个 spike，再从分布采样得到离散 MUA。

```text
声音波形
  -> 24,414 Hz 重采样、声压校准、左侧 2,048 样本上下文
  -> 卷积编码器（共享）
  -> 64 通道瓶颈
  -> 9 个动物分支 + 记录时间输入
  -> 每分支 512 单位的 5 类概率
  -> categorical 采样
  -> 762.94 Hz 的 MUA；也可输出瓶颈或按特征频率选单位
```

### 训练与评估

完整训练声音共 7.83 小时，包括 TIMIT 安静/噪声语音、环境噪声、处理语音、音乐和 moving ripples；多分支模型使用 7.05 小时。训练使用 Adam、batch size 50、起始学习率 0.0004，并按验证集停滞减半学习率、早停。评估声音完全与训练集分开，使用 RMSE、log-likelihood、解释方差/相关性和 coherence。

### 结果与边界

图像证据显示 categorical 模型比 Poisson 更准确地复现 Fano factor 和跨试次分布；时间输入保持了晚期记录的准确度；共享编码器在动物间提取共同潜在动力学。ICNet 还能复现频率调谐、时间动力学、动态范围适应、调幅调谐、前向掩蔽和上下文增强。公开仓库提供预训练权重和可执行推理示例，但没有训练脚本、完整评估脚本或原始数据，因此重新训练和重新计算论文全部指标仍是 `Not found`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ICNet Summary

### Problem

Auditory-brain models lag behind cochlear models in accuracy, statistical fidelity and robustness to recording drift. The paper targets millisecond-resolution simulation of inferior-colliculus neural activity for arbitrary sounds.

### Method

ICNet is a convolutional encoder-decoder trained on 512-channel IC recordings from nine gerbils. A shared encoder produces a 64-channel bottleneck; nine animal-specific decoders emit 512-unit distributions conditioned on sound and recording time. Five-way categorical outputs (0-4 spikes per 1.3-ms bin) model underdispersed responses better than a Poisson baseline. The released implementation loads pretrained weights, samples categorical responses, and optionally returns CF-sorted units or bottleneck features.

### Evidence

Training uses 7.83 h of speech, noise, processed speech, music and moving ripples; evaluation uses held-out complex sounds and dedicated neurophysiology stimuli. Figures show improved Fano-factor/distribution matching over Poisson, preserved late-recording accuracy with time input, shared-encoder gains across animals, near-veridical speech/ripple/music activity, and reproduction of frequency tuning, temporal dynamics, dynamic-range adaptation, amplitude-modulation tuning, forward masking and context enhancement. Metrics include RMSE, log-likelihood, explained variance/correlation and coherence.

### Reproducibility

The official GitHub snapshot (main, `7a631f1`) contains pretrained `model_weights.hdf5`, custom layers, configuration, characteristic frequencies, an example WAV and executable notebook/script. Inference is directly traceable to `src/ICNet_functions.py`. Training scripts, evaluation-metric code, complete data files, and supplementary Markdown are `Not found`; reported benchmark numbers remain paper-grounded. Reproducibility rating: 4/5 for pretrained inference, 2/5 for retraining/evaluation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
