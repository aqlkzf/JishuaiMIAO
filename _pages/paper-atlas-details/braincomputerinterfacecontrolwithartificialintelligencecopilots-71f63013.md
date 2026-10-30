---
layout: default
permalink: /paper-atlas/braincomputerinterfacecontrolwithartificialintelligencecopilots-71f63013/
title: "BrainComputerInterfaceControlWithArtificialIntelligenceCopilots"
nav: false
wide: true
description: "运动脑机接口需要把 EEG 信号转换为光标或机械臂指令，但单独依赖神经信号会受噪声、解码错误和任务复杂度限制。本文把用户看作主控者，把 AI 看作能利用目标、场景和任务规则的副驾驶（copilot），以提高实际任务表现。 论文摘要明确提出 CNN 与 ReFIT-like Kalman filter 的组合，并将共享自主用于光标和机械臂任务。图 1-2 直接展示了这一数据流和 copilot 的任务信息输入。"
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
      <span>Technology Platforms</span>
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>BrainComputerInterfaceControlWithArtificialIntelligenceCopilots</h1>
    <p>Brain-computer interface control with artificial intelligence copilots</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-025-01090-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for BrainComputerInterfaceControlWithArtificialIntelligenceCopilots">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/kaolab-research/bci_raspy" target="_blank" rel="noopener noreferrer" aria-label="Open code for BrainComputerInterfaceControlWithArtificialIntelligenceCopilots">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## AI-BCI 共享自主控制方法说明

### 要解决的问题

运动脑机接口需要把 EEG 信号转换为光标或机械臂指令，但单独依赖神经信号会受噪声、解码错误和任务复杂度限制。本文把用户看作主控者，把 AI 看作能利用目标、场景和任务规则的副驾驶（copilot），以提高实际任务表现。

### 核心思路

```text
EEG 多通道时间窗
  -> CNN/EEGNet 提取意图特征
  -> 自适应 Kalman 滤波器得到二维控制状态
  -> 结合目标/场景信息的 PPO copilot
  -> 光标到靶或机械臂抓取放置
```

论文摘要明确提出 CNN 与 ReFIT-like Kalman filter 的组合，并将共享自主用于光标和机械臂任务（`paper.md:12`）。图 1-2 直接展示了这一数据流和 copilot 的任务信息输入。

### 解码器

本地代码的 EEGNet 为 64 电极输入构建时域卷积、深度卷积和可分离卷积，并输出概率、logit 和隐藏状态（`code/bci_raspy/decoders/EEGNet.py:62-171`）。其 Kalman 递推为 $x_{t+1}=M_1x_t+M_2y_t$；在线环路将四方向输出变成二维速度，更新状态，并在允许时用推断状态自适应更新滤波统计量（`Offline_EEGNet/kalman_filter.py:211-226`; `modules/kf_clda.py:2-80`）。

补充材料说明 CNN 采用按 trial 划分的五折交叉验证，初始学习率为 $10^{-3}$，验证指标持续 10 个 epoch 未改善时降学习率/早停（`supp.md:176-182`）。

### 光标 copilot

中心外 8 靶任务中，8 个目标相隔 45 度；成功要求在目标上连续停留 500 ms，超时为 24 s（`supp.md:63-72`）。论文所述 PPO copilot 使用两层各 64 单元 MLP 和 256 维 LSTM，学习率 $3\times10^{-4}$、rollout 2048、batch 64、训练 120 万步（`supp.md:185-190`）。本地训练脚本也使用 RecurrentPPO/MlpLstmPolicy、2048 和 64 的默认设置，但没有验证到论文实际使用的完整配置或 checkpoint，因此不能把两者称为精确一致。

### 机械臂 copilot

补充材料给出 Franka Panda、RealSense D455、GroundingDINO 目标定位、XY 安全边界、自动抓取/放置半径和冷却时间（`supp.md:193-223`）。然而在已获取的代码中没有验证到 Franka 控制器、GroundingDINO 调用或完整机器人 copilot，因此这部分只能按论文/补充材料理解，不能作为本地可复现实现。

### 结果和边界

摘要报告瘫痪参与者的光标 target hit rate 提高 3.9 倍，并能在 copilot 帮助下完成原本不能完成的连续方块搬运（`paper.md:12`）。这些是文章结论，不应扩展为对所有用户或所有任务的泛化保证：补充材料还记录了未达到所选动作 EEG 调制阈值的 SCI 参与者（`supp.md:139-173`）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Brain-computer interface control with artificial intelligence copilots

### Overview

This technology paper asks whether shared autonomy can lift non-invasive BCI performance enough to matter clinically. It combines EEG decoding with a CNN and ReFIT-like adaptive Kalman filter, then adds AI copilots that use task information for cursor control and robotic pick-and-place (`paper source/nature_html/paper.md:9-12`).

### What Is New

The contribution is not only an EEG decoder: the system explicitly gives a copilot task context that a human BCI signal alone cannot reliably carry. The article reports that a participant with paralysis achieved a 3.9-fold higher cursor target hit rate and completed a sequential robotic block task that could not be completed without the copilot (`paper.md:12`).

### Evidence and Evaluation

Main figures visibly cover the architecture (Figs. 1-2), multi-session CNN-KF control (Fig. 3), assisted cursor control (Fig. 4), and vision-guided robotic pick-and-place (Fig. 5). The local supplement documents decorrelated and centre-out-8 tasks, trial-level CNN cross-validation, PPO cursor-copilot hyperparameters, and robotic hardware/safety details (`supp.md:27-72,176-223`). It also reports selection/attrition limits: two additional SCI participants did not exhibit strong modulation for the selected behaviors, and two pilot participants did not complete experiments (`supp.md:139-173`).

### Reproducibility

The paper links experimental/training code, plotting code and Zenodo data (`paper.md:90-99`). The acquired primary repository at commit `43a635540f113a7d6e29538b6a9ba8555f5fce9f` directly supports a CNN decoder, adaptive Kalman loop and simulated cursor/RecurrentPPO training surfaces. Overall paper-code fidelity is **medium**: the exact CNN-to-KF experiment wiring, reported policy/checkpoint and Franka/GroundingDINO robot stack are not verified in the snapshot. The main publisher HTML is a subscription preview, so unexposed main-text protocol/statistical details remain **Not found** rather than inferred.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
