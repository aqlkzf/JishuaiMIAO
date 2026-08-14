---
layout: default
permalink: /paper-atlas/multi-joint-soft-exosuit-62cdaef2/
title: "Multi_joint_soft_exosuit"
nav: false
wide: true
description: "颈段脊髓损伤（SCI）会破坏上肢的神经肌肉控制，影响伸手、举臂和日常 生活的独立性。论文指出，已有上肢可穿戴机器人在 SCI 人群中的验证很少， 而且大多只针对手指张开/闭合 。相关背景包括 软体外骨骼综述和肩部织物 exomuscle。本工作的区别是 同时覆盖肩外展以及肘屈曲/伸展，并在颈段 SCI 参与者中进行功能测试。 作者提出轻量、模块化的软体外骨骼服。织物气动执行器由两片 TPU 涂层 尼龙布热封而成；"
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
    <h1>Multi_joint_soft_exosuit</h1>
    <p>A multi-joint soft exosuit improves shoulder and elbow motor functions in individuals with spinal cord injury</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-025-01105-8" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Multi_joint_soft_exosuit">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 多关节软体外骨骼服：方法详解

### 1. 要解决的问题

颈段脊髓损伤（SCI）会破坏上肢的神经肌肉控制，影响伸手、举臂和日常
生活的独立性。论文指出，已有上肢可穿戴机器人在 SCI 人群中的验证很少，
而且大多只针对手指张开/闭合
（paper.md:L12）。相关背景包括
软体外骨骼综述（Xiloyannis 等，*IEEE Transactions on Robotics*，2021；
paper.md:L125）和肩部织物
exomuscle（Georgarakis 等，*Nature Machine Intelligence*，2022；
paper.md:L134）。本工作的区别是
同时覆盖肩外展以及肘屈曲/伸展，并在颈段 SCI 参与者中进行功能测试。

### 2. 系统与创新点

作者提出轻量、模块化的软体外骨骼服。织物气动执行器由两片 TPU 涂层
尼龙布热封而成；在热封前放入耐热纸形成内部气腔，再热封聚氨酯管作为
进气口。伸肌执行器的纵向切口用于前臂固定，屈肌执行器则通过切口穿过
Velcro 带，把执行器两端固定在肘关节近端和远端
（paper.md:L232-L237）。惯性传感器
用于自动识别/支持肩外展及肘屈曲或伸展；摘要明确了这一控制方式，但未
给出控制器的状态机或参数
（paper.md:L12）。

机械表征给出了执行器的边界性能：

- 伸肌的扭矩随压力近似线性，在 69 kPa、约 135° 时平均最大
  `22.1 +/- 0.8 Nm`；扭矩随角度呈非线性，并在约 135° 达峰
  （paper.md:L240-L245）。
- 屈肌的力随压力近似线性，在 69 kPa、0% 收缩率时平均最大
  `40.4 +/- 3.5 N`；力随收缩率非线性，在 0% 附近有主峰、约 60% 处有
  局部峰（paper.md:L248-L253）。

因此，核心创新不是一个复杂的学习模型，而是把柔性气动执行器、惯性
传感和多关节协调穿戴结构组合起来，并直接面向 SCI 的功能动作。

### 3. 计算/物理流水线

```text
织物裁剪与热封
      |
      v
肩部模块 + 肘伸肌模块 + 肘屈肌模块
      |
      v
压力源 -> 气腔膨胀 -> 产生执行器力/扭矩
  ^                         |
  |                         v
惯性传感器 -> 运动阶段判断 -> 自动施加肩/肘辅助
                                  |
                                  v
             同一任务下 Robot OFF 与 ON 的比较
       活动范围/耐力 | 肌电 EMG | ADL | BBT | SUS/QUEST
                                  |
                                  v
             计算 ON-OFF 差异并观察损伤程度相关趋势
```

实验分两级：先用 11 名健康志愿者验证独立肘部模块，再在 15 名颈段 SCI
参与者（C4–C7，AIS A–D）上测试肩部与肘部一体化系统
（paper.md:L12）。主图 2–3 展示肩/肘
静态与动态动作，图 4 展示模拟日常生活活动（ADL），图 5 给出 SCI 参与者
的代表性轨迹，图 6 汇总盒子与积木测试（BBT）、系统可用性量表（SUS）
和 QUEST（paper.md:L63-L85）。

为了读懂扩展数据图 4，可以把横轴记为无辅助时的基线 ROM，把纵轴记为
`ROM_on - ROM_off`（单位：度）；正值表示开启机器人后活动范围增加。点的
颜色编码 `Delta EMG`（相对于基线 EMG 的 ON-OFF 百分比），蓝色表示肌肉
活动降低。屈曲和伸展趋势的指数拟合分别给出 `R²=0.85` 与 `R²=0.62`
（paper.md:L256-L261）。这些是
图中定义/解释的量，不是从代码复现出的公式。

### 4. 结果如何支持方法

摘要报告 SCI 参与者的静态耐力时间增加超过 250%，动态任务主要肌肉活动
最高降低 50%；仍保留抓握能力的两名参与者在 BBT 中获得更高分
（paper.md:L12）。扩展数据图 4 进一步
显示“双重效果”：基线 ROM 较低、损伤较重者主要获得 ROM 增益；基线 ROM
较高者 ROM 大致保持，但肌肉用力下降
（paper.md:L256-L261）。图 6 的 SUS/QUEST
条形图还把功能效果与舒适性、易用性和安全性评价联系起来。

### 5. 证据边界与复现缺口

当前本地 `paper.md` 是 Nature HTML 预览，只包含摘要、图注、元数据和链接，
没有正文 Methods/Results，也没有方程（转换统计中 `equations=0`）。因此下列
关键实现无法据此重建：IMU 校准和滤波、运动阶段判定阈值、压力轨迹与上限、
执行器到关节的力矩映射、采样率/延迟补偿、EMG 预处理、试次数、随机化和
统计检验。

论文链接了 reporting-summary PDF、四个视频以及 Figs. 1–6 的 XLSX 源数据，
但这些文件未在工作区取得（paper.md:L276-L313）。
所以本文档应作为“有证据边界的概念和物理流程说明”，而不是声称已具备
可运行的控制器或完整临床统计复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

The paper addresses loss of shoulder and elbow motor function after cervical spinal cord injury (SCI). The authors identify a gap in upper-limb wearable robotics: prior systems were tested only minimally in people with SCI and focused mainly on hand opening/closing (source: `paper source/nature_html/paper.md:9-12`).

### Proposed technology

The technology is a lightweight, modular soft exosuit that supports shoulder abduction and elbow flexion or extension. Fabric-based pneumatic actuators are placed on the torso/shoulder and forearm, while inertial sensors trigger assistance automatically. The abstract reports staged validation: elbow modules in 11 healthy volunteers, followed by the integrated shoulder/elbow system in 15 people with cervical SCI (levels C4-C7, AIS A-D).

### Evidence

The reported SCI outcomes are increased static endurance (more than 250%), reduced activity of muscles used in dynamic tasks (up to 50%), and improved Box and Block Test (BBT) scores in the two participants retaining prehensile ability. Figure inspection supports the experimental structure: Fig. 2 shows static/dynamic elbow tests in healthy participants; Fig. 3 shows analogous SCI tests; Fig. 4 covers simulated activities of daily living (ADLs); Fig. 5 shows assisted ADL traces; and Fig. 6 reports BBT, System Usability Scale (SUS), and QUEST usability results (`paper.md:58-85`). Extended data report actuator construction, mechanical characterization, and an impairment-dependent ROM/EMG trade-off (`paper.md:232-261`).

### Reproducibility and limitations

This is a `paper-only` analysis. The structured Nature acquisition searched the code-availability block, article HTML, and converted paper and found no paper-linked GitHub repository (`github_links.json`, `acquisition_manifest.json`). The publisher page is explicitly a subscription preview (`paper.md:15`), so the converted source does not contain the Introduction, Methods, Results, Discussion, participant tables, statistical tests, controller timing, sensor thresholds, or manufacturing protocol. These are marked `Not found` rather than reconstructed. Supplementary videos, a reporting PDF, and an XLSX source-data workbook are linked but were not converted (`paper.md:276-312`). Reproduction therefore requires institutional access to the full article and supplementary assets.

**Overall reproducibility rating: 2/5.** The device concept, cohort sizes, headline effects, figure-level outputs, actuator peak values, and source-data location are recoverable; the protocol and computational/control details needed to repeat the study are not available in the acquired source.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
