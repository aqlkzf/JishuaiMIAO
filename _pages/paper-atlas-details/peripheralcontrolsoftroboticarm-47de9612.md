---
layout: default
permalink: /paper-atlas/peripheralcontrolsoftroboticarm-47de9612/
title: "PeripheralControlSoftRoboticArm"
nav: false
wide: true
description: "水下非结构化环境中的软体机械臂需要柔顺、灵活，同时还要知道哪里接触了物体、接触力有多大以及接触方向。集中式视觉或把所有原始传感器信号拉回控制器会增加线缆、刚度和延迟。本文把感知和部分反射控制分布到吸盘附近，并用较高层的外围控制器协调抓取。 机械臂长 410 mm，锥形本体上有十个不同尺寸的传感吸盘。每个吸盘有三个 LED/光电晶体管方向，硅胶反射层把受力变形转换为光强变化。"
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
      <span>Machine Learning Algorithm</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>PeripheralControlSoftRoboticArm</h1>
    <p>Peripheral control enabled by distributed sensing in an octopus-inspired soft robotic arm for autonomous underwater grasping</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-026-01230-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for PeripheralControlSoftRoboticArm">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法解读：分布式感知驱动的章鱼式软体机械臂

### 要解决的问题

水下非结构化环境中的软体机械臂需要柔顺、灵活，同时还要知道哪里接触了物体、接触力有多大以及接触方向。集中式视觉或把所有原始传感器信号拉回控制器会增加线缆、刚度和延迟。本文把感知和部分反射控制分布到吸盘附近，并用较高层的外围控制器协调抓取。

### 系统结构

机械臂长 410 mm，锥形本体上有十个不同尺寸的传感吸盘。每个吸盘有三个 LED/光电晶体管方向，硅胶反射层把受力变形转换为光强变化。两个吸盘连接到一块 connection board，五块板通过 I2C 与基座 master board 通信。吸盘级 LNC 负责阈值检测和局部吸附，master 上的 PNS 根据多个吸盘的方向和位置选择三根腱的动作。

```text
受力/变形 -> LED/光电晶体管差分采样
          -> 三方向归一化与向量合成
          -> 局部阈值触发吸附
          -> 五块板经 I2C 汇总到 master
          -> 估计物体倾角 beta（观察窗口内平均）
          -> 吸附、背侧弯、腹侧弯、顺/逆时针扭转
```

论文定义吸盘方向向量和角度：

$$\mathbf{s}_j=\sum_{i=1}^{3}\mathbf{v}_{ij},\qquad
\alpha_j=\tan^{-1}\frac{s_{j\_y}}{s_{j\_x}}.$$

对所有接触吸盘的方向向量求和后，论文先把下半平面的向量反射到上方，再用

$$\mathbf{r}=\sum_{j=1}^{10}\mathbf{s}_j,\qquad
\beta=\left(\tan^{-1}\frac{r_y}{r_x}+\frac{\pi}{2}\right)\bmod\pi$$

得到物体相对机械臂轴线的倾角。$\beta$ 与接触吸盘数量、吸盘是否位于末端 SC8-10 一起决定抓取策略。局部吸附先保证黏附，约 4 s 的观察窗口后外围控制器再改变腱动作。

### 实现证据与差异

Zenodo 固件中，connection-board 源码确实对三个差分通道做归一化、阈值判断，并把局部结果通过 I2C 返回；master 源码会聚合 active 吸盘、滤波角度并构造三腱模式。固件发送的是 $(v_x^2-v_y^2,2v_xv_y)$ 双角坐标，而不是直接发送论文符号 $\mathbf{s}_j$；master 中也未在检查范围内明确呈现论文所说的下半平面反射。因此代码对应关系是 Partial，而不是 Exact。`SendMotorCmd` 写入 `bufferTX` 与传输函数读取 `space1.all` 之间的赋值也未找到，不能据此声称已经验证了端到端电机执行。

### 评价

传感器平均灵敏度约 394.9 +/- 21 mV N^-1，方向误差在有利压入深度下小于 18 度。实验覆盖干湿环境、拉脱、嵌入机械臂后的接触识别、运动中接触和静态淡水池抓取。系统不使用外部视觉或遥操作，但测试对象和抓取规则仍是证明概念性质；没有固件构建或硬件复现实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem and contribution

Soft arms can be compliant and dexterous, but distributed tactile sensing usually costs wiring, space, and centralized processing. This technology paper presents a 410-mm tendon-driven octopus-inspired arm with ten optoelectronic mechanoreceptive suction cups, pair-level local processing, and a master peripheral controller for autonomous underwater grasping. The novelty is the integration of compact force/direction sensing with a hierarchical local-reflex/PNS control architecture rather than a learned policy.

### Method in brief

Each cup uses three LEDs and phototransistors in a reflective silicone stalk. Differential optical signals are normalized and combined into a local direction; a threshold crossing triggers that cup's suction group. Five connection boards preprocess two cups each and expose active/directional records over I2C. The master aggregates active cups, estimates object inclination $\beta$ over an observation window, and selects dorsal/ventral bending, clockwise/counterclockwise twisting, or suction-only behavior. The paper's equations and the released firmware are compared in `doc_method.md` and `doc_code.md`; the firmware's doubled-angle encoding is mathematically related but not source-proven equivalent to every paper coordinate-transform step.

### Evidence

Cup characterization reports an average sensitivity of 394.9 +/- 21 mV N^-1, noise below 5 mV, approximately 0.1-N accuracy, and directional error below 18 degrees at favorable indentation. Tests include dry/wet indentation, pull-off, embedded-arm sensing, moving-contact correction, and underwater grasping of cylindrical, small, and irregular objects. The experiments used static freshwater tanks, no vision, no teleoperation, objects about 3-6 cm and 0.1-5 N, and a reported load capability near 500 g (`paper.md:318-324`). Figures 1-9 were locally inspected.

### Reproducibility and limitations

The paper-linked Zenodo archive (`10.5281/zenodo.18969202`) contains embedded firmware and design/data artifacts. Direct source inspection verifies local optical processing, I2C exchange, posture filtering, and tendon-mode construction. It does not verify a `bufferTX` to `space1.all` motor-transport handoff, a firmware build, or a hardware run; those are explicitly marked `Not found`/unverified in `doc_code.md`. No supplementary Markdown was acquired, and the prototype's grasp policy is intentionally simplified and non-optimal.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
