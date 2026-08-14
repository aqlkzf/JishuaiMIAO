---
layout: default
permalink: /paper-atlas/efficient-protein-structure-generation-with-sparse-denoising-mod-03d767b0/
title: "Efficient_protein_structure_generation_with_sparse_denoising_models"
nav: false
wide: true
description: "蛋白质扩散生成器在长度超过约 400 个残基时速度和可设计性下降，而且遇到训练时没有见过的新任务通常需要重新训练。salad（sparse all-atom denoising）用稀疏、全原子去噪模型处理长蛋白，并用采样时的结构编辑支持新约束。 每个残基只与 K 个空间/序列邻居做不变点注意力（IPA），复杂度从 O(N^2) 降为 O(NK)，并避免 O(N^3) 的持久 pair 特征和 triangle multiplicatio…"
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
      <span>Protein &amp; Sequence Models</span>
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>Efficient_protein_structure_generation_with_sparse_denoising_models</h1>
    <p>Efficient protein structure generation with sparse denoising models</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/mjendrusch/salad" target="_blank" rel="noopener noreferrer" aria-label="Open code for Efficient_protein_structure_generation_with_sparse_denoising_models">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法中文解释

### 要解决的问题
蛋白质扩散生成器在长度超过约 400 个残基时速度和可设计性下降，而且遇到训练时没有见过的新任务通常需要重新训练。salad（sparse all-atom denoising）用稀疏、全原子去噪模型处理长蛋白，并用采样时的结构编辑支持新约束（`paper.md:28-48`）。

### 核心方法
每个残基只与 K 个空间/序列邻居做不变点注意力（IPA），复杂度从 O(N^2) 降为 O(NK)，并避免 O(N^3) 的持久 pair 特征和 triangle multiplication。模型同时预测坐标、氨基酸和 DSSP 等辅助量；VP、长度缩放 VP、VE 三种噪声方案覆盖不同长度。

### 推理流程
```text
结构/条件 -> 在时间 t 加序列和坐标噪声
         -> 稀疏 IPA 去噪（回收上一状态）
         -> 逐步反向采样得到 backbone
         -> 每一步可编辑输入噪声或输出结构
         -> ProteinMPNN 设计序列，ESMFold/AF2 过滤
```
VE 模型的 shaped noise 先采样具有 10 A 平均段长的中心链，再把每个中心分配给 200 个残基；中心也可以来自 SVG 字母路径，因此可以生成指定形状。编辑输出可做循环/螺旋对称、固定 motif 或把 parent/child 多状态轨迹对齐平均。

### 训练目标与证据
主要目标是轨迹坐标去噪、全原子误差、FAPE、旋转、局部 FAPE、氨基酸/DSSP/distogram 和结构违规损失的加权和（Eq. 13，`paper.md:359-421`）。模型在过滤后的 PDB 上训练 200,000 次迭代。200 个 backbone、每个 8 个 ProteinMPNN 序列、ESMFold/AF2 预测构成基准；成功标准通常为 scRMSD < 2 A 且 pLDDT > 70。

### 结果、限制与代码
shaped VE noise 在 1,000 残基达到最高 36.7% 设计性，约 8M 参数；随机二级结构条件提高多样性但牺牲设计性；多状态任务完整成功率 2.9%，高于既有 0.05%。论文没有新的湿实验验证，并且训练数据去掉配体、离子和核酸。`salad` 代码快照直接验证了稀疏特征、损失聚合和通用采样循环，但论文主模型的精确配置、编辑工具和 checkpoint 在限定源码范围内仍为 Partial/Not found。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem
Protein structure diffusion models lose designability and runtime efficiency as residue count grows, while task-specific conditioning often requires retraining. The paper introduces salad (sparse all-atom denoising), targeting long proteins and training-free structure editing (paper.md:28-48).

### Method and novelty
Salad denoises amino-acid identities and all-atom/backbone coordinates with a sparse SE(3)-equivariant transformer. Each residue attends to K neighbours, reducing attention from O(N^2) to O(NK), and avoids persistent pair features/triangle multiplication (paper.md:53-69). VP, length-scaled VP and VE schedules are compared; shaped VE noise supplies domain-like or user-defined initial geometry. Structure editing modifies input noise and/or each denoising output, enabling motifs, symmetry, repeats and coupled multi-state generation without retraining (paper.md:70-97).

### Evidence and evaluation
The models are trained on filtered PDB chains (30% mmseqs2 clusters), 1,024-residue batches, for 200,000 iterations (paper.md:441-452). Benchmarks generate 200 backbones per length, design eight ProteinMPNN sequences, and use ESMFold/AlphaFold metrics; designability is pLDDT > 70 and scRMSD < 2 A (paper.md:98-134, 525-530). VP is competitive through 400 residues; VP-scaled/VE retain quality longer, and shaped noise reaches 36.7% designability at 1,000 residues with about 8M parameters. Random secondary-structure conditioning increases diversity but lowers designability; a 50,000-backbone synthetic set yields 81.4% designable structures and 11,973 PDB-novel structures. Multi-state editing achieves 2.9% per-backbone success versus 0.05% reported for ProteinGenerator (paper.md:119-122).

### Reproducibility and limitations
The linked `salad` snapshot is available at commit `8348117`; direct source reads verify sparse feature preparation, loss aggregation and a generic sampler, but not an exact manuscript-variant configuration (`doc_code.md`). Training/checkpoint and editing utilities are incomplete in the bounded source scope. The paper has no new experimental validation, excludes ligands/ions/nucleic acids, and trails Genie 2 in diversity without conditioning (paper.md:134-140).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
