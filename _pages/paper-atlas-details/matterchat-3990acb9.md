---
layout: default
permalink: /paper-atlas/matterchat-3990acb9/
title: "MatterChat"
nav: false
wide: true
description: "材料图网络可以利用原子间的三维几何来预测性质，但不能像语言模型一样接受专家提问；纯文本 LLM 又很难从 CIF 字符串中可靠地恢复空间关系。MatterChat 将晶体结构图和自然语言提示放进同一个生成模型。 材料编码器产生保留元素、键角和局部环境的原子级表示。桥接器用 32 个 query 对这些表示做 cross-attention，并以 self-attention 进一步整合，再投影到 Mistral 的隐藏维度。"
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
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>MatterChat</h1>
    <p>A multimodal large language model for materials science</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-026-01214-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for MatterChat">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MatterChat 方法讲解

### 要解决的问题

材料图网络可以利用原子间的三维几何来预测性质，但不能像语言模型一样接受专家提问；纯文本 LLM 又很难从 CIF 字符串中可靠地恢复空间关系。MatterChat 将晶体结构图和自然语言提示放进同一个生成模型（`paper.md:22-37`）。

### 模型结构

```
晶体结构 -> 原子图 -> 冻结的 CHGNet/MACE -> 原子嵌入
                                  |
                       32 个可学习 query -> Q-Former bridge -> 线性投影
用户问题 -> Mistral tokenizer -------------------------------> 拼接
                                  |
                       冻结的 Mistral 7B -> 文本答案
```

材料编码器产生保留元素、键角和局部环境的原子级表示。桥接器用 32 个 query 对这些表示做 cross-attention，并以 self-attention 进一步整合，再投影到 Mistral 的隐藏维度（`paper.md:60-75`）。代码中材料编码器和 LLM 的参数确实被冻结，Q-Former/投影层承担训练（`Model/material_Q_Former_LLM_complete.py:25-57`）。

### 数据、训练和推理

作者从 MPtrj 中选取 142,899 个 relaxed 结构，随机按 9:1 划分。每个结构生成 12 类问答：化学式、空间群、晶系，以及金属性、直接带隙、稳定性、实验观测、磁性、磁序、形成能、凸包以上能量和带隙（`paper.md:202-230`）。

训练分两阶段。第一阶段用图文相关性、条件文本预测和图文匹配 BCE 三个损失对齐结构与描述；论文给出的总损失是三者相加（`paper.md:234-248`）。第二阶段将桥接器接到 LLM，用监督交叉熵学习描述和性质任务（`paper.md:253-256`）。推理时可以使用多模态 RAG：从训练池按嵌入距离找两个近邻，与原始输出一起对分类多数投票、对回归取平均（`paper.md:123-124,279-281`）。

### 结果和局限

在 14,290 个测试样本上，MatterChat 在六个分类任务和三个数值任务中优于所比较的 LLM/物理模型；MACE 版本在 GNoME 分布外数据上迁移较强（`paper.md:126-155`）。Fig. 6 的相似度矩阵和注意力图显示 query 槽位与结构/语言特征存在规律对应，但这仍不能证明真正的语义因果 grounding。连续体积和密度预测存在 resolution gap，训练是单轮问答，冻结 LLM 仍可能产生幻觉（`paper.md:181-193`）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MatterChat Summary

MatterChat is a structure-aware multimodal large language model for inorganic materials. It addresses the gap between graph/MLIP models that predict properties well but cannot converse, and text-only LLMs that miss explicit three-dimensional geometry (`paper.md:22-37`).

The model freezes a pretrained CHGNet or MACE material encoder and a Mistral 7B LLM, training a BLIP-2-style bridge with 32 learned queries (`paper.md:60-75`). The bridge converts atom embeddings into LLM-width prefix embeddings, which are fused with a user prompt to generate descriptions or property answers. Training uses a two-stage alignment/instruction scheme over 142,899 relaxed Materials Project structures and 12 text tasks (`paper.md:202-266`).

On 14,290 held-out structures, MatterChat is compared with Vicuna, Mistral, SchNet, CHGNet, MACE and adapter baselines. Fig. 5 reports the strongest classification accuracies and lowest RMSEs for bandgap, formation energy and energy above hull; an optional embedding-retrieval RAG improves regression RMSE by about 12% and classification by about 0.6% with about 0.7% latency overhead (`paper.md:126-155,279-281`). GNoME out-of-distribution tests favor the MACE variant without additional fine-tuning.

Reproducibility is medium. The Zenodo archive contains model/source code, inference scripts, sample CIFs, logs and outputs, but the training launcher references unavailable `/pscratch` datasets, checkpoints and a Mistral path (`code_repo/MatterChat_code/training_code/train_matterchat.py:20-23,107-127`). The code directly verifies the Q-Former/LLM bridge and causal decoder path, but the paper's explicit correlation/association pretraining losses and exact alternating-layer schedule are not found in the inspected archive. The paper also reports a resolution gap for continuous density/volume, single-turn training, and hallucination/grounding risks (`paper.md:181-193`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
