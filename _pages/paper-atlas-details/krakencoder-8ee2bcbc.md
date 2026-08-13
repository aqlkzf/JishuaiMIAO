---
layout: default
permalink: /paper-atlas/krakencoder-8ee2bcbc/
title: "Krakencoder"
nav: false
wide: true
description: "同一个人的脑连接组会因为模态（结构 SC、功能 FC）、脑区模板、纤维追踪算法、去噪方式和相关性估计方法而形成许多不同“口味”。传统方法通常只学习一个方向，例如 SC→FC，或只处理固定模板，难以在研究间转换，也无法把多种观测融合成统一表征。 Krakencoder 的核心假设是：这些连接组是同一潜在脑网络的不同视角。因此，每种口味拥有独立编码器和解码器，但共享一个 128 维潜在空间。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Krakencoder</h1>
    <p>Krakencoder: a unified brain connectome translation and fusion tool</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/kjamison/krakencoder" target="_blank" rel="noopener noreferrer" aria-label="Open code for Krakencoder">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Krakencoder 方法详解

### 它解决什么问题

同一个人的脑连接组会因为模态（结构 SC、功能 FC）、脑区模板、纤维追踪算法、去噪方式和相关性估计方法而形成许多不同“口味”。传统方法通常只学习一个方向，例如 SC→FC，或只处理固定模板，难以在研究间转换，也无法把多种观测融合成统一表征。

Krakencoder 的核心假设是：这些连接组是同一潜在脑网络的不同视角。因此，每种口味拥有独立编码器和解码器，但共享一个 128 维潜在空间。

### 计算流程

```text
连接矩阵
 -> 取上三角边向量 X_i
 -> 仅用训练集拟合的 PCA_i，降到 256 维 X'_i
 -> 第 i 个线性编码器
 -> L2 归一化，得到单位超球面上的 128 维 z_i
 -> 三种用途：
      同一解码器：重建 i -> i
      目标解码器：翻译 i -> j
      多个 z 求平均：融合后解码到任意 j
 -> 逆 PCA_j，恢复目标模板的原始边空间
```

论文包含 15 种口味：3 个脑区模板，每个模板有 3 种 FC 和 2 种 SC，共训练 15×15=225 条路径。PCA 把不同模板统一到 256 维，避免高分辨率模板仅因边数更多而主导损失。

### 为什么潜在空间能对齐

每个 epoch 有两阶段。第一阶段逐路径训练重建，同时使用相关性、欧氏距离和“正确受试者应比其他受试者更相似”的对比项，保留个体差异。第二阶段重新编码全部口味，最小化同一受试者不同口味潜在向量之间的差异。论文给出的主要权重为：重建 MSE 1000、路径潜在分离 10、跨口味潜在一致性 10000。

融合时可平均全部口味，也可只平均 SC（fusionSC）、只平均 FC（fusionFC），或排除目标模板后做跨模板预测（fusion-parc）。这使模型既是翻译器，也是统一表征学习器。

### 如何评价

普通相关性会被“预测群体均值”虚高，因此论文重点使用去均值相关性、Top-1 身份识别率和平均排序百分位 avgrank。avgrank 的随机水平为 0.5；越接近 1，说明真实受试者与自己的预测比与他人的预测更匹配。

在 196 名独立 HCP-YA 测试者上，FC→FC 的平均 avgrank 为 1.00，SC→SC 为 0.99；更困难的 SC→FC 为 0.82，FC→SC 为 0.85。与已有 SC→FC 深度模型相比，身份可识别性提高 42–54%。融合潜在表征还能更好地区分亲缘关系，并保留年龄、性别和认知信息；在 HCP Development 和 Aging 数据上无需重新训练仍保持较高身份识别性。

### 代码与局限

代码仓库与论文高度一致：`model.py` 实现多编码器/解码器和潜在归一化，`train.py` 实现路径训练与潜在一致性阶段，`loss.py` 实现相关性、距离和身份识别损失，`run_model.py` 实现融合及新数据适配。需要注意，当前代码还支持可选的 SC↔FC 潜在变换层，其是否启用取决于 checkpoint 配置。

主要复现缺口不是核心算法，而是外部数据与实验封装：HCP 数据、OSF 资源和预训练变换需另行获取，仓库中未找到把论文最终 2,000-epoch checkpoint 的全部数据、环境和命令锁定在一起的单一不可变清单。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Krakencoder Summary

Krakencoder is a joint translation and fusion model for brain connectomes. It addresses the fact that structural versus functional imaging, atlas choice, tractography, denoising, and connectivity estimator all produce incompatible “flavors,” while most earlier models solve only one direction or one pair of flavors.

The model assigns every flavor its own encoder and decoder but forces all of them through a shared 128-dimensional, L2-normalized latent space. Training covers all 225 paths among 15 flavors, combining reconstruction, correlation/Euclidean contrastive terms that preserve subject identity, and a strong cross-flavor latent-consistency loss. Inference can translate any one flavor to any other or average multiple latent codes to create fusion, fusionSC, fusionFC, and cross-parcellation representations.

The main evaluation used HCP young-adult data split without families crossing train/validation/test boundaries (683/79/196 subjects). Within-modality predictions were nearly perfectly identifiable by average rank; cross-modality avgrank averaged 0.82 for SC→FC and 0.85 for FC→SC. Fusion representations better reflected familial relatedness and retained or enhanced demographic and cognition information. The model also preserved identifiability on HCP Development and Aging cohorts without retraining. Against two prior SC→FC neural approaches, identifiability improved by 42–54%, while one Krakencoder model covered all 225 paths with substantially less total training than many pair-specific baselines.

Code-paper fidelity is high: the repository implements per-flavor encoders/decoders, normalized latent codes, arbitrary translation, the major contrastive/identifiability losses, fusion inference, PCA transforms, and domain adaptation. Exact reproduction is still constrained by external HCP/OSF assets and the absence of one immutable paper experiment manifest.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
