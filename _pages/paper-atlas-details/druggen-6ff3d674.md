---
layout: default
permalink: /paper-atlas/druggen-6ff3d674/
title: "DrugGEN"
nav: false
wide: true
description: "这篇论文提出 DrugGEN，用于针对指定蛋白质生成新的候选小分子。目标不是只生成语法有效的分子，而是同时保持分子有效性、新颖性、药物样性质和对目标蛋白的结合倾向。论文网页在本地只能得到摘要、图注和可用性信息；详细数值和实验流程来自 41 页的补充材料，代码行为来自随论文发布的 GitHub 快照。 分子被表示成带节点和边的图。生成器和判别器都使用图 Transformer。"
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
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>DrugGEN</h1>
    <p>Target-specific de novo design of drug candidate molecules with graph-transformer-based generative adversarial networks</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-025-01082-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for DrugGEN">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/HUBioDataLab/DrugGEN" target="_blank" rel="noopener noreferrer" aria-label="Open code for DrugGEN">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DrugGEN 方法解释

### 研究问题

这篇论文提出 DrugGEN，用于针对指定蛋白质生成新的候选小分子。目标不是只生成语法有效的分子，而是同时保持分子有效性、新颖性、药物样性质和对目标蛋白的结合倾向。论文网页在本地只能得到摘要、图注和可用性信息；详细数值和实验流程来自 41 页的补充材料，代码行为来自随论文发布的 GitHub 快照。

### 核心想法

分子被表示成带节点和边的图。生成器和判别器都使用图 Transformer。生成器输入一个填充后的起始分子图，判别器在 DrugGEN 模式下看到已知的目标活性分子（AKT1 抑制剂），因此对抗训练会把生成分布推向目标相关分子；NoTarget 模式则用普通 ChEMBL 分子作为真实样本。

关键的边调制注意力是：`Att ⊙ A_e ⊙ (A_e + 1)`（supplementary.md:408-443）。这里 `Att` 是节点 query/key 的注意力矩阵，`A_e` 是边或键特征。代码在 softmax 前实现了等价的逐元素调制（`DrugGEN/src/model/layers.py:122-135`），使键连接参与远距离结构依赖建模。

### 计算流程

```text
SMILES -> RDKit 分子图 -> 原子/键标签和 padding
      -> 节点 X、边 A 的 one-hot 张量
      -> 生成器图 Transformer -> 节点/边 logits
      -> 取最大类别 -> RDKit 分子 -> SMILES 修正
      -> 有效性、新颖性、QED、SA、对接和实验验证
```

代码先从 SMILES 建立原子和键编码器，并过滤超过 `max_atom` 的分子（`src/data/utils.py:26-126`）。生成器分别投影节点和边，先对边特征做对称化，再通过 Transformer，最后读出节点和边类别（`src/model/models.py:48-103`）。判别器使用相同的 Transformer 家族，并把节点特征展平为标量 critic（`src/model/models.py:153-209`）。训练采用 WGAN-GP：critic 损失包括真实/生成分数差和节点、边联合梯度惩罚，generator 试图提高生成样本的 critic 分数（`src/model/loss.py:4-85`）。

### 结果如何支持方法

补充材料的消融实验生成每个变体 10,000 个分子。官方 DrugGEN 的有效性为 0.713，优于 FiLM、edge、edge+1 等注意力变体的 0.110、0.464、0.117；相对起始分子的 novelty-at-inference 为 0.924（supplementary.md:424-447）。在目标模型比较中，AKT1 top-10% 对接中位自由能为 -8.39 kcal/mol；5 个合成分子中，分子 1 的 IC50 为 1.89 uM，分子 2 为 48.55 uM，分子 3-5 高于 100 uM（supplementary.md:251-303, 1217-1233）。注意力图中 22 个蛋白相互作用原子有 20 个被模型高注意力捕获，但这属于事后解释，训练阶段没有使用蛋白-配体接触标签（supplementary.md:771-806）。

### 复现边界

本地代码可以核验图表示、模型、损失、训练循环和推理指标；不能核验论文的 docking、分子动力学、DEEPScreen、合成或酶活实验脚本。训练数据、预训练权重和结果归档由 figshare/Zenodo 链接提供但未下载。网页正文受订阅限制，因此文章正文中未能核验的预处理、数据划分和完整公式保留为 `MISSING`，不应被补充材料或代码之外的推断替代。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DrugGEN

### Problem

Target-specific de novo design must generate valid, novel, drug-like molecular graphs that are biased toward a selected protein. Earlier sequence GANs, graph GANs, reinforcement-learning systems, and 3D generators trade off validity, novelty, diversity, drug-likeness, or target affinity; the paper positions DrugGEN as a 2D graph method for that balance.

### Proposed method

DrugGEN is a conditional graph-generative adversarial system. A generator receives padded node/edge tensors for starting molecules and a discriminator receives target-specific bioactive molecules (AKT1 inhibitors in the main experiment). Both networks use graph-transformer encoders. The distinctive attention modulation is the elementwise form `Att ⊙ A_e ⊙ (A_e + 1)` (supplementary.md:408-443), where bond features modulate node-pair attention. The generator readouts are converted back to molecules and corrected/filtered as SMILES.

### Evaluation

The reported AKT1 and CDK2 experiments use ChEMBL molecules and target bioactivity sets, with validity, novelty, novelty-at-inference, uniqueness, internal diversity, QED, synthetic accessibility, fragment/scaffold similarity, FCD, Lipinski/Veber/PAINS filters, docking, molecular dynamics, attention alignment, synthesis and kinase assays. Supplementary evidence reports targeted DrugGEN validity 0.713, novelty 0.993 (0.924 against inference inputs), uniqueness 0.878 +/- 0.019, QED 0.995 and SA 2.968 +/- 0.862 (supplementary.md:1133-1148). The docking top-10% median for AKT1 is -8.39 kcal/mol, and five synthesized molecules include one 1.89 uM inhibitor, one 48.55 uM inhibitor and three inactive above 100 uM (supplementary.md:251-284, 1217-1233).

### Reproducibility

The authors link code, pretrained models and result archives through GitHub, Zenodo and figshare. The local GitHub snapshot is commit `917d8f507e5e8621704b96a8f83ba807194cff41` (master) and contains the model, WGAN-GP losses, graph encoding, training and inference paths. Docking, MD, synthesis and assay scripts/results are not in the snapshot. The Nature HTML route is access-limited to abstract/captions/metadata; detailed paper claims are therefore grounded in the supplementary text and direct source lines, with missing article-body details marked `MISSING`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
