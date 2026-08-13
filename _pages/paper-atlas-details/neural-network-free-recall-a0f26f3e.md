---
layout: default
permalink: /paper-atlas/neural-network-free-recall-a0f26f3e/
title: "Neural_network_free_recall"
nav: false
wide: true
description: "这篇论文研究自由回忆时，人是否一定依赖经典的“时间情境”机制。经典观点认为，记忆会整合近期刺激历史，因此回忆会表现出近因效应和时间邻近性。论文的核心结论是：优化自由回忆表现的循环神经网络可以学习到多种类人的策略，其中表现最好的模型会形成对刺激身份不敏感、但编码项目学习位置的索引表征；作者把这种稳定的顺序支架类比为记忆宫殿。 默认代码配置使用长度为 8 的项目列表。研究阶段依次输入项目，回忆阶段输出动作；"
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
    <h1>Neural_network_free_recall</h1>
    <p>A neural network model of free recall learns multiple memory strategies</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Veritaria/rnn-free-recall" target="_blank" rel="noopener noreferrer" aria-label="Open code for Neural_network_free_recall">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 自由回忆神经网络模型：多种记忆策略的学习机制

### 问题

这篇论文研究自由回忆时，人是否一定依赖经典的“时间情境”机制。经典观点认为，记忆会整合近期刺激历史，因此回忆会表现出近因效应和时间邻近性。论文的核心结论是：优化自由回忆表现的循环神经网络可以学习到多种类人的策略，其中表现最好的模型会形成对刺激身份不敏感、但编码项目学习位置的索引表征；作者把这种稳定的顺序支架类比为记忆宫殿（`paper.md:9-12`）。

### 模型输入、输出与任务

默认代码配置使用长度为 8 的项目列表。研究阶段依次输入项目，回忆阶段输出动作；若动作对应列表中尚未回忆过的项目，得到正奖励，否则得到错误或“不知道”的惩罚（`tasks/FreeRecall.py:27-58`；`experiments/Basic/setups/setup.json:67-83`）。因此模型学习的不是单步分类，而是一个连续的“学习列表 -> 多步回忆”策略。

```text
项目序列
  -> GRU 在学习阶段更新隐状态并存入记忆槽
  -> 进入回忆阶段，按当前状态检索记忆
  -> 检索结果注入 GRU 的候选状态
  -> 输出项目概率与价值估计
  -> 获得奖励，使用 A2C 更新参数
```

### 核心计算

代码中的 `ValueMemoryGRU` 有 128 维隐状态，并配有容量为 8 的 `ValueMemory`（`setup.json:3-33`）。学习阶段打开 `encoding` 标志，将当前状态写入循环缓冲区；回忆阶段打开 `retrieving` 标志，以当前状态为查询，根据相似度对记忆值加权，再送入 GRU（`value_gru.py:200-230`）。

实现的候选状态可写成：

$$\tilde{h}=\tanh(i_n+r\odot h_n+g\odot m)$$

其中 $m$ 是检索到的记忆，$g$ 是记忆门控；随后由输入门将 $\tilde{h}$ 与旧状态组合成新状态（`value_gru.py:254-275`）。这是从代码直接抽取的形式，不是因为预览版论文提供了同样的公式。

### 为什么会出现不同策略

论文将策略差异和两个因素联系起来：回忆目标是否鼓励尽量找回全部项目，以及模型是否还能利用近因信息。补充图的说明文字记录了折扣因子和学习/回忆阶段工作记忆冲刷比例的扫描，每个条件训练 20 个随机种子模型（`supplementary/supp.md` 中 Supplementary Fig. 1-2）。当模型需要稳定地遍历整个列表、且不能方便地依赖刚刚出现的项目时，位置索引更有吸引力；这就是论文的记忆宫殿类策略。

### 如何评估

基础分析脚本计算条件回忆概率、前向不对称、时间组织分数、隐状态余弦相似度，以及记忆检索曲线（`experiments/Basic/experiment.py:79-179`）。主图还比较策略的表现和噪声鲁棒性；扩展数据将部分 PEERS 人类受试者的行为模式与模型策略相对照（`paper.md:256-277`）。

### 可复现性与边界

代码仓库提供默认运行命令和主任务、模型、训练、分析文件，因而核心流程可运行。当前获取到的 Nature 页面是预览文本，缺少正文 Methods；本文没有执行完整训练、聚类笔记本或 PEERS 数据分析，也没有逐图复现数值。此外，空记忆时 `ValueMemory.retrieve` 的返回形状与调用处的解包方式需要实际运行验证（`value.py:73-75`，`value_gru.py:200-214`）。这些应被视为明确的待验证项，而不是已证实的复现结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## A Neural Network Model Of Free Recall Learns Multiple Memory Strategies

### Overview

This 2026 *Nature Machine Intelligence* paper studies whether free recall must be explained by a temporal-context mechanism. Its central claim is that recurrent networks trained for free recall discover several human-like retrieval strategies; high-performing models can instead use a stimulus-invariant code for studied position, forming an index scaffold likened to a memory palace (`paper source/nature_html/paper.md:9-12`).

The public repository supplies a configuration-driven PyTorch implementation. Its default runnable experiment uses an eight-item free-recall task, a 128-dimensional GRU, an eight-slot episodic value memory, A2C optimization, and recorded behavioral/representation analyses (`rnn-free-recall_repo/experiments/Basic/setups/setup.json:3-118`). During study it stores recurrent states; during recall it retrieves a similarity-weighted memory value and inserts it into the GRU candidate update (`models/model/value_gru.py:200-275`).

### Evaluation Evidence

The main figures compare strategy classes, representation measures, performance, and noise robustness; later figures vary external context and content-based search. Extended data compares selected human PEERS profiles with the strategy classes and reports correlations between recall performance and strategy metrics (`paper.md:240-285`). The supplementary PDF describes discount-factor and working-memory-flush sweeps with 20 seeds per setting (Supplementary Fig. 1-2 captions).

### Reproducibility Assessment

**3/5: executable core implementation, partial paper-method visibility.** The paper explicitly links the GitHub repository (`paper.md:102-105`), and its README gives a default command: `python -u main.py --exp Basic --setup setup.json`. Core task, model, trainer, and Basic analysis source are present. The exact main Methods text is unavailable in the acquired Nature preview, the precise configuration behind each published panel was not dynamically traced, notebooks/PEERS analyses were not run, and an empty-memory return-shape branch needs execution verification. These are documented limitations rather than evidence of a missing code release.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
