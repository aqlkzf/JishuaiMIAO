---
layout: default
permalink: /paper-atlas/bamboomixer-extension-892650d8/
title: "Bamboomixer_extension"
nav: false
wide: true
description: "本地可得的 Nature Machine Intelligence 文章是“可复用性报告”，HTML 正文主要包含摘要、图注和数据/代码可用性信息；没有完整方法章节、数据规模或编号公式。因此，下面把“论文明确说法”和“Zenodo 19048302 代码验证行为”分开。代码细节不能被误写成论文原文结论。 液态电解液设计需要同时处理分子结构、配方组成、温度和盐浓度。传统模型在数据分布改变、化学体系改变或目标属性扩展时，稳健性和迁移性不足。"
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
    <h1>Bamboomixer_extension</h1>
    <p>Reusability report: Exploring the utility and extensibility of an integrated modelling framework for liquid electrolyte design</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Bamboomixer extension 方法说明

### 证据范围

本地可得的 Nature Machine Intelligence 文章是“可复用性报告”，HTML 正文主要包含摘要、图注和数据/代码可用性信息；没有完整方法章节、数据规模或编号公式（全文 `paper.md` 共 265 行）。因此，下面把“论文明确说法”和“Zenodo 19048302 代码验证行为”分开。代码细节不能被误写成论文原文结论。

### 要解决的问题

液态电解液设计需要同时处理分子结构、配方组成、温度和盐浓度。传统模型在数据分布改变、化学体系改变或目标属性扩展时，稳健性和迁移性不足。报告的摘要明确提出四个关注点：复现实验、数据量/分布敏感性、零样本与少样本跨体系迁移，以及从分子描述符扩展到电子能量边界（ESW/EEB）和电池库仑效率（CE）[paper.md:9-12]。参考文献列出 *PRX Energy* 2024 的分子混合物图网络、*Nature Machine Intelligence* 2025-2026 的电解液模型等，但本地HTML没有逐方法定量比较表 [paper.md:102-130]。

### 方法总览

```text
单分子 SMILES/分子图 + 分子性质
             │
             ▼
      Mono 图编码器（多任务预训练）
             │ 分别得到溶剂/盐的节点和边表示
             ▼
配方图 + 摩尔比 + 温度 + 浓度 ──► MolMix 注意力聚合
             │                      │
             │                      └─► conductivity / anion ratio / ESW / CE
             │
目标性质 ──► 条件扩散（384维配方嵌入）
             │
             ▼
Set Transformer + 字典距离匹配 ──► 溶剂/盐 BoW 配方
             │
             └─► 再送入 MolMix，输出生成配方的性质预测
```

这个结构与论文摘要及 Fig. 1 的“预测 + 条件扩散 + 解码/匹配”框架一致 [paper.md:12,58-60]。三阶段预测训练和双阶段生成训练也写在代码仓库 README 中 [code/bamboomixer_extension/README.md:16-24]。

### 关键模块（代码依据）

#### 1. 单分子预训练

`Mono` 使用 `Graph2DBlock` 编码分子图，对节点和边分别做全局均值池化后拼接，并建立多个属性头 [formula_design/predictor/mono.py:70-112,143-180]。输出包括熔点、沸点、pKa、LUMO/HOMO、折射率、密度、介电常数、黏度、表面张力和蒸气压等 [mono.py:180-236]。有些属性输入温度：折射率/密度/介电常数通过温度嵌入，黏度使用 VFT 模块，表面张力使用线性关系，蒸气压使用无平移 VFT 模块 [mono.py:188-220]。

#### 2. 配方预测

`MolMix` 在 `torch.no_grad()` 中复用单分子编码器，对溶剂集合和盐集合使用不同的注意力聚合器，然后拼接：

$$h_{inv}=[h_{solv,node},h_{solv,edge},h_{salt,node},h_{salt,edge}]。$$

再把温度、浓度各重复为 8 个通道，送入 anion ratio、ESW/ESWC 和 CE 的有界输出头 [formula_design/predictor/molmix.py:146-228]。电导率由 `sigma、n1、n2、T0、A、B` 六个头交给经验温度依赖模块计算，而不是单一线性头 [molmix.py:82-113,171-210]。`train_mode=pretrain` 输出 NE/Mistry 两类电导率和 ESWC；`fine_tune` 输出实验电导率、ESW 和 CE [molmix.py:99-115,182-228]。

#### 3. 数据预处理

配方预处理会补全 SMILES、分别把溶剂和盐的摩尔比归一化、检查盐摩尔比小于 1，并将摄氏温度变为

$$T_{norm}=(T_C+273.15)/373.15。$$

电导率（mS/cm）变为

$$c_{norm}=(\log c+4.6002)/8.3344。$$

这些转换及逆变换均由 `scripts/prepare_data/prepare_data.py` 和生成脚本直接实现 [prepare_data.py:163-225; scripts/test_results/generate.py:249-253]。论文正文没有给出这些常数。

#### 4. 条件扩散

训练时条件向量为

$$p=[c_{conductivity},r_{anion},e_{ESW},q_{CE}]。$$

对 384 维配方嵌入 $e_0$ 加噪：

$$e_t=\sqrt{\bar\alpha_t}e_0+\sqrt{1-\bar\alpha_t}\epsilon,\quad \epsilon\sim N(0,I)。$$

1-D U-Net 根据时间步和四个条件预测噪声 [formula_design/generator/diffusion.py:81-110]。默认配置使用 1000 步余弦 beta 调度和 `diff_MSE` [config/train/generator_diffusion_config.yaml:9-49]。采样从形状 `[batch,1,384]` 的高斯噪声开始，按时间从 1000 反向去噪 [diffusion.py:112-149]。

#### 5. 配方解码

`FormulaDecoder` 将 384 维嵌入按 2:1 切成溶剂 256 维和盐 128 维。Set Transformer 产生最多 `max_num_mol` 个分子槽位及 softmax 摩尔比；槽位和固定分子字典都做 L2 归一化，用欧氏距离匹配，再以 `softmax(-1000d)` 形成 BoW，最后按 L1 归一化 [formula_design/generator/decoder.py:197-273]。生成脚本依次保存嵌入、BoW 和 JSON 性质预测，并把小于 0.02 的 BoW 分量截断 [scripts/test_results/generate.py:146-284]。

### 评估与图像证据

- Fig. 2 展示复现/稳健性比较、温度曲线、分布重叠和按属性的柱状比较。
- Fig. 3 展示数据量和分布变化下的曲线、柱状图、散点密度图及热图。
- Fig. 4 展示零样本/少样本迁移、元素分布、预测-真实电导率散点和候选溶剂结构。
- Fig. 5 展示分子属性排名、多个目标的预测-真实散点、误差/多样性热图以及与公开基线的比较。

这些观察来自五张本地图片，而不仅是图注；图注位置见 `paper.md:58-80`。补充材料表 1-3 给出复现参数差异（例如最大 epoch 1999、fine-tune batch size 512、early-stop patience 20），表 4 是缺失分子属性消融，表 5 是 fine-tune 后的电导率/阴离子比指标 [supplementary/supp.md:41-96]。具体指标定义、数据规模、切分和基线数值在本地来源中仍是 `Not found`。

### 可复现性结论

数据链接指向 Hugging Face，原始代码、扩展代码和推荐配置分别指向 Zenodo 17694573、19048302、19876420 [paper.md:90-99]。要得到论文级数值结论，还需取得外部数据/checkpoint 并实际运行训练和测试。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

Machine-learning electrolyte design needs models that remain useful when molecular composition, operating regime and target property change. The Nature Machine Intelligence reusability report evaluates and extends the integrated Bamboomixer framework, whose stated design combines molecular structure with formulation composition, preserves permutation invariance, and couples forward prediction to inverse formulation generation [paper.md:9-12].

### Existing-method limitations

The report frames robustness, transferability and applicability as insufficiently explored in existing ML electrolyte models [paper.md:9-12]. It cites prior electrolyte design, molecular-mixture and force-field approaches (including *PRX Energy* 2024, *Nature Machine Intelligence* 2025-2026 and related venues) but the accessible HTML does not provide a detailed method-by-method comparison or quantitative baseline table [paper.md:102-130].

### Proposed framework

Bamboomixer extension is a multiscale predictive-generative workflow. Molecular graphs are encoded with a multi-task `Mono` model; solvent and salt representations are aggregated separately in `MolMix`, which predicts conductivity, anion ratio, electronic energy boundaries (ESW/ESWC) and Coulombic efficiency. A conditional diffusion model samples a 384-dimensional formulation embedding from requested properties, and a set-transformer/distance decoder maps it to a solvent/salt BoW formulation. The archive README exposes the three predictive stages and dual generative stages [code/bamboomixer_extension/README.md:16-24]; source verification is detailed in doc_method.md.

### Evaluation evidence

Fig. 2 is a visual reproducibility/robustness benchmark; Fig. 3 varies data volume and distribution; Fig. 4 shows zero-shot/few-shot transfer; and Fig. 5 connects molecular descriptors to conductivity, anion ratio, electronic boundaries and battery metrics [paper.md:58-80]. The abstract claims substantial gains over standard baselines for the multiscale extension [paper.md:12]. Supplementary Tables 1-3 list reproduction parameter changes, Table 4 reports missing-molecular-property ablations, and Table 5 reports post-fine-tuning conductivity/anion-ratio scores [supplementary/supp.md:41-96]. Exact metric definitions, dataset sizes, baseline identities and split protocols are not exposed in the accessible article text; no training or inference run was performed in this analysis.

### Reproducibility and limitations

Data are linked to Hugging Face datasets and code/checkpoints to Zenodo records 17694573 (original), 19048302 (extension) and 19876420 (recommended parameters) [paper.md:90-99]. The local code snapshot is the Zenodo 19048302 archive (commit marker `19048302`) and includes preprocessing, configs and CLI scripts. Reproduction also depends on CUDA/PyTorch/Torch Geometric versions and external datasets/checkpoints; the archive README lists tested versions but does not bundle them [code/bamboomixer_extension/README.md:3-7].

### Bottom line

The workspace provides a source-grounded implementation map and figure-supported understanding of an extensible predictive-plus-generative electrolyte design framework. It is suitable for code inspection and a guided reproduction attempt, but not for claiming independently verified numerical performance until the linked datasets/checkpoints and full evaluation protocol are retrieved and executed.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
