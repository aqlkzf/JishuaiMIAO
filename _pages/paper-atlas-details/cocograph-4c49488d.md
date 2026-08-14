---
layout: default
permalink: /paper-atlas/cocograph-4c49488d/
title: "CoCoGraph"
nav: false
wide: true
description: "分子生成必须同时满足化学价态、连通性、新颖性和真实分子性质分布。早期 VAE、GAN、图生成器及离散扩散模型通常把化学规则交给网络学习，可能产生无效分子，或需要生成后过滤。CoCoGraph 的关键取舍是：把价态和连通性写进扩散转移，网络只学习真实分子的结构模式。 给定分子式，先建立含显式氢的价态有效图。一次双边交换（DES）选择两条边 (i,j)、(k,l)，删除它们并添加 (i,k)、(j,l)。"
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
    <h1>CoCoGraph</h1>
    <p>A collaborative constrained graph diffusion model for the generation of realistic synthetic molecules</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-026-01229-5" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CoCoGraph">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/manurubo/CoCoGraph" target="_blank" rel="noopener noreferrer" aria-label="Open code for CoCoGraph">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CoCoGraph 方法说明

### 要解决的问题

分子生成必须同时满足化学价态、连通性、新颖性和真实分子性质分布。早期 VAE、GAN、图生成器及离散扩散模型通常把化学规则交给网络学习，可能产生无效分子，或需要生成后过滤。CoCoGraph 的关键取舍是：把价态和连通性写进扩散转移，网络只学习真实分子的结构模式（paper.md:25-55, 151-169）。

### 方法核心

给定分子式，先建立含显式氢的价态有效图。一次双边交换（DES）选择两条边 $(i,j)$、$(k,l)$，删除它们并添加 $(i,k)$、$(j,l)$。四个端点各失去一条边又得到一条边，所以度数/价态、原子数和分子式保持不变；同时拒绝产生非连通图、重复键超过三重键或重复分子。不断交换后，图趋向固定度序列上的 Molloy--Reed 最大熵分布（paper.md:196-223）。

扩散模型输入节点、边、图特征和时间，经过三层 EnhancedGINE，为每个原子对预测成键/断键概率，再组合成四维 DES 概率张量。时间模型使用相似 GNN 和均值池化，预测当前图在扩散轨迹中的归一化位置 $t_{pred}$。三项加权 BCE 训练扩散模型，MSE 训练时间模型（paper.md:225-315）。FPS 版本额外输入 2048 位 Morgan 指纹，增加子结构信息（paper.md:318-329, 388-397）。

```text
分子式 -> 随机价态有效图 G_T
      -> 特征化 -> 扩散模型预测 DES
      -> 采样交换，拒绝断开图/重复 SMILES
      -> 时间模型预测 t_pred 并反馈给扩散模型
      -> 选整条轨迹中 t_pred 最小的图 -> SMILES
```

训练使用约 225 万分子（筛选后约 167 万）、5--70 个原子、batch 12；BASE 三个 epoch，FPS 从 BASE 预训练后再微调两个 epoch。采样时 DES 候选初始阈值为 0.95，必要时每次降低 0.05；最终不取最后一步，而取时间模型认为最接近原始分布的状态（paper.md:400-448）。

### 结果与局限

BASE/FPS 在 GuacaMol 上均达到 100% validity、99.9% uniqueness，novelty 为 98.6%/98.5%；报告 KL 分数为 96.0%/96.7%，优于 DiGress 的 92.6% 和 JTVAE 的 47.3%（paper.md:58-77）。FPS 在十项性质中优于 JTVAE 九项、优于 DiGress 七项。8.2M 分子数据库的专家测试约 62% 能识别真实分子，非博士/硕士训练者约 59%，无环和以脂肪族键为主的分子接近随机猜测（paper.md:130-148）。

局限是分子式被固定，不能直接在公式空间搜索；DES 候选的最坏复杂度为 $O(n^4)$，目前约限制到 70 个原子。代码快照直接验证了公式建图、邻接张量、FPS 特征和连通/去重采样（`code/lib_functions/formula_utils.py:160-180`; `data_preparation_utils.py:318-337`; `sample_utils.py:106-156,169-293`），但完整训练入口、权重和损失调用关系仍是 Partial/Not found。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CoCoGraph Summary

CoCoGraph is a constrained, collaborative discrete graph-diffusion generator for realistic synthetic molecules. It diffuses a formula-specific molecular graph with double-edge swaps that conserve every atom's degree/valence, then uses a diffusion model plus a learned time model to reverse the swaps and choose the trajectory state predicted closest to the original distribution.

The central limitation of earlier VAEs, GANs, graph generators and diffusion models is the need to learn chemical validity, with invalid samples, expensive filtering, non-uniform diffusion progress and limited property realism. CoCoGraph moves valence and connectivity constraints into the transition operator, leaving neural capacity for structural statistics (paper.md:25-55, 151-169).

The BASE model has about 534K parameters (471K diffusion + 63K time), versus 4.6M for DiGress and 5.3M for JTVAE. On GuacaMol, BASE and FPS both report 100% validity and 99.9% uniqueness; novelty is 98.6%/98.5% and the reported KL scores are 96.0%/96.7%, compared with DiGress 85.2% validity and 92.6% KL and JTVAE 100% validity and 47.3% KL (paper.md:58-77). FPS beats JTVAE on 9/10 and DiGress on 7/10 GuacaMol property distributions (paper.md:83-99). Across 36 RDKit descriptors, the generated distributions generally track PubChem more closely, while aromatic-ring and H-bond-donor cases remain weaker.

The authors generated 8.2M molecules (7.1% redundancy; 98.5% novelty) and ran a 20-round expert Turing-like test. Overall experts reached about 62% real-molecule identification, 59% without postgraduate organic-chemistry training; acyclic and predominantly aliphatic molecules were near chance (paper.md:130-148). The method is formula-conditioned, has $O(n^4)$ candidate-swap complexity, and therefore does not explore formulas and is practically limited to about 70 atoms (paper.md:163-169).

Reproducibility is medium: the full arXiv manuscript, figures, linked GitHub snapshot and model-weight references are local, but the snapshot includes large data bundles, has no supplementary Markdown, and does not expose a single clean end-to-end reproduction command. Direct code evidence confirms the graph construction, feature preparation and constrained sampler; exact loss wiring and checkpoint semantics remain partially unverified.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
