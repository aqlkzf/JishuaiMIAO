---
layout: default
permalink: /paper-atlas/dexterous-soft-hand-exoskeleton-b105fb13/
title: "Dexterous soft hand exoskeleton"
nav: false
wide: true
description: "严重手功能障碍患者往往不仅握力不足，而且无法主动完成抓握前的手型预塑和拇指定位。传统软手套多只提供手指屈伸，因此难以稳定抓取形状差异很大的日常物体。本文面向接近完全手瘫痪的 ALS 患者，并在脑卒中患者中验证其适用边界。 系统是可个体化的纺织气动手外骨骼，加入拇指对掌、拇指外展、腕背屈和手指协调驱动。它通过共同设计过程确定舒适、安全、独立性和可靠性等需求，再将这些需求变为机械结构与控制策略。"
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
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>Dexterous soft hand exoskeleton</h1>
    <p>A dexterous soft hand exoskeleton restores intentional grasping in individuals with severe hand impairment</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 灵巧软体手外骨骼：方法解读

### 要解决的问题

严重手功能障碍患者往往不仅握力不足，而且无法主动完成抓握前的手型预塑和拇指定位。传统软手套多只提供手指屈伸，因此难以稳定抓取形状差异很大的日常物体。本文面向接近完全手瘫痪的 ALS 患者，并在脑卒中患者中验证其适用边界。

### 核心方案

系统是可个体化的纺织气动手外骨骼，加入拇指对掌、拇指外展、腕背屈和手指协调驱动。它通过共同设计过程确定舒适、安全、独立性和可靠性等需求，再将这些需求变为机械结构与控制策略。

```text
sEMG 残余肌肉信号
  -> 滤波与 RMS 特征
  -> 自适应阈值检测抓握意图
  -> IMU 判断动作状态并抑制易误触发阶段
  -> 错误监测 CNN 复核
  -> 气动外骨骼执行预塑、闭合、保持和打开
```

### 意图检测

对活动窗口均值与参考窗口均值加标准差倍数比较：当 $\overline{x}_{act}>\overline{x}_{ref}+\tau\sigma_{ref}$ 时触发抓握。论文使用 162 ms 活动窗口和 1 s 动态参考窗口。为了尽早响应，阈值设得较灵敏；随后用 CNN 检查触发后 200-500 ms 的信号，若多数窗口为静息则将该触发视为错误并快速停止动作。

CNN 的训练窗口为 200 ms；峰值前 200 ms 到峰值后 800 ms 之间为“抓握意图”，其余为静息。网络包含三层一维卷积（32、64、128 个滤波器）、全局平均池化和全连接分类头。

### 结果与边界

ALS 共同设计参与者在最终系统辅助下可在 BBT 中转移最多五个积木，并实现独立进食。六位脑卒中参与者中，重度组在 ARAT 的 grasp 和 grip 子项获益明显；中度组并未普遍获益，部分 pinch 表现下降。这说明该方案更适合恢复缺失的基础抓握，而非增强仍保留精细控制的人群。

Zenodo 发布包提供 EMG 数据、CNN 训练和离线阈值评估代码。它没有提供 IMU 状态机、气动阀/Arduino 固件、实时采集或 Unity 训练游戏，因此可以复现部分 EMG 分析，不能端到端复现临床运行的外骨骼系统。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Dexterous Soft Hand Exoskeleton

### Overview

This Nature Machine Intelligence technology paper develops a high-dexterity textile pneumatic hand exoskeleton for severe to near-complete hand paralysis. Instead of assuming that a user can preshape the hand, the co-created design adds thumb opposition, thumb abduction, wrist dorsiflexion, coordinated finger actuation, and hands-free EMG control.

### Evidence and Results

The eight-session, nine-month co-creation process was centered on one participant with ALS. The paper reports that the final design enabled a Box-and-Blocks Test score of five and independent feeding, whereas the early flexion-extension prototype did not improve BBT. In six stroke participants, severe impairment subgroup performance improved by an average 10 ARAT grasp points and 4.67 grip points; moderate impairment did not show broadly positive benefit and showed reduced pinch performance. Mean SUS was 65.4/100.

For intentional control, an adaptive EMG threshold detects rises in residual flexor pollicis longus activity, with IMU context intended to inhibit triggers during reach/place states. A secondary CNN checks whether a high-sensitivity trigger was a false positive. The paper reports 97.1% start-grasp detection in the game-based ALS evaluation and an increase in rest-phase specificity from 94.6% to 99.6% with error correction.

### Reproducibility

Code and data are publicly released through Zenodo record 20037934. The snapshot includes EMG-RMS data, onset/error CNN training, and offline threshold evaluation, producing a **medium** paper-code fidelity assessment. It does not include the real-time IMU state machine, firmware, valve/Arduino control, Unity game, or complete deployed-system calibration; the archive supports EMG analysis replication but not end-to-end device replication.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
