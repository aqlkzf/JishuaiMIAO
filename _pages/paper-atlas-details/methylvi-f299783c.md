---
layout: default
permalink: /paper-atlas/methylvi-f299783c/
title: "MethylVI"
nav: false
wide: true
description: "单细胞亚硫酸氢盐测序（scBS-seq）同时受到覆盖度稀疏、批次/测序协议差异和真实细胞异质性的影响。直接把“甲基化数/覆盖数”当作无噪声比例会把技术波动误认为生物学信号。MethylVI 用深度生成模型直接建模甲基化计数，目标是得到去噪的甲基化、低维细胞表示、跨协议整合和差异甲基化结果。 对每个细胞和基因组区域，y 是甲基化胞嘧啶数，n 是覆盖数，s 是批次/协议协变量。"
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
    <h1>MethylVI</h1>
    <p>Probabilistic modelling of single-cell bisulfite sequencing data with MethylVI</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-026-01225-9" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for MethylVI">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/suinleelab/methylVI-reproducibility" target="_blank" rel="noopener noreferrer" aria-label="Open code for MethylVI">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MethylVI 方法解读

### 它解决什么问题？

单细胞亚硫酸氢盐测序（scBS-seq）同时受到覆盖度稀疏、批次/测序协议差异和真实细胞异质性的影响。直接把“甲基化数/覆盖数”当作无噪声比例会把技术波动误认为生物学信号。MethylVI 用深度生成模型直接建模甲基化计数，目标是得到去噪的甲基化、低维细胞表示、跨协议整合和差异甲基化结果（论文 `paper.md:9-12`）。

### 概率模型

对每个细胞和基因组区域，`y` 是甲基化胞嘧啶数，`n` 是覆盖数，`s` 是批次/协议协变量。模型先采样 `z ~ N(0,I)`，解码器根据 `z,s` 产生均值 `mu` 和离散程度 `gamma`，然后使用

`y | z,s,n ~ Beta-Binomial(mu, gamma, n)`。

补充材料把 beta 分布改写成均值-离散度参数化：`mu = alpha/(alpha+beta)`、`gamma = 1/(alpha+beta+1)`。因此 `E[y]=n mu`，`Var[y]=n mu(1-mu)(1+(n-1) gamma)`；`gamma=0` 时就是普通二项分布，正的 `gamma` 表示额外过度离散（补充材料 pp.25-26，提取文本 485-533 行）。这使 `mu` 可以解释为区域甲基化比例，同时保留测序覆盖度带来的不确定性。

### 网络和训练流程

编码器：单隐层、128 个节点、ReLU、10% dropout；两个线性头输出变分后验的均值和方差，方差用 softplus 保证为正。解码器结构相同，最后用 sigmoid 约束 `mu` 在 0 到 1，报告的 `z` 维度为 20（补充材料 p.26，535-546 行）。

```text
MuData (mCG/mCH, mc/cov 层)
   -> setup_mudata 注册模态和计数
   -> 编码器 q_phi(z[,u,c])
   -> 解码器输出 mu、gamma
   -> Beta-Binomial 似然 + 变分优化/early stopping
   -> latent 表示、去噪甲基化、DMG 统计和 atlas 查询
```

MethylANVI 增加细胞类型 `c` 和 nuisance 变量 `u`，并令
`q_phi(z,u,c|y,n,s)=q_phi(z|y,n,s)q_phi(u|c,z)q_phi(c|z)`；ELBO 包含重构项、Gaussian KL、分类 KL 和 nuisance KL，有标签时再加入分类损失（补充材料 pp.26-27，548-639 行）。

### 论文实验与代码

五个主图分别展示模型框架、跨协议整合、基因组区域分析、额叶皮层 methylome atlas 迁移和 RNA+甲基化 MultiMethylVI。补充实验还测试随机置零覆盖度的去噪、GC 偏差与 dispersion 的关系、posterior predictive checks 及可扩展性（补充材料 pp.23-29）。复现仓库的 `train_methylvi_model.py:152-204` 明确注册 `mCG/mCH`、构造模型、early-stopping 训练并保存 checkpoint、latent 和 normalized 输出；`calculate_atlas_metrics.py:100-183` 调用 scIB 指标。

Nature HTML 是付费预览，主文 Methods/Results 不在本地。因此学习时应把补充 PDF 作为算法细节来源，并把学习率、batch size、完整预处理和 scvi-tools 版本标为 `Not found`，不要自行补全。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MethylVI

### Problem

Single-cell bisulfite sequencing (scBS-seq) measures methylated and covered cytosines sparsely, so biological methylation heterogeneity is confounded by sampling noise and protocol/batch effects. The paper introduces MethylVI, a deep generative model intended to denoise counts while supporting dimensionality reduction, cross-protocol integration and differential methylation analysis [paper.md:9-12].

### Method and contribution

MethylVI represents each cell with a 20-dimensional latent variable and models methylated counts directly with a beta-binomial likelihood. The beta-binomial mean is the methylation proportion and its region-specific dispersion captures overdispersion; the supplementary derivation gives `E[y]=n mu` and `Var[y]=n mu(1-mu)(1+(n-1) gamma)` [supplementary.pdf pp.25-26, extracted lines 485-533]. A one-hidden-layer encoder and decoder use 128 units, ReLU, 10% dropout, softplus posterior variance and sigmoid decoder means [supplementary.pdf p.26, extracted lines 535-546]. MethylANVI extends the model with cell labels and a classification term in the ELBO [supplementary.pdf pp.26-27, extracted lines 548-639].

### Evaluation

The paper's five main figures cover the generative model, integration benchmarks, genomic-region feature analysis, frontal-cortex atlas transfer learning and joint RNA-plus-methylation MultiMethylVI [paper.md:58-80]. Supplementary experiments report: direct count modeling outperforming PCA/LSI/SnapATAC2-style baselines; robust recovery of randomly zeroed coverage against MAGIC, ALRA and DrImpute; cell-type-specific age-associated methylation and transcriptomic changes; dispersion consistent with GC bias; posterior-predictive checks; and training under ten minutes on the tested large datasets [supplementary.pdf pp.23-29, extracted lines 381-396, 398-408, 410-483, 645-685]. Figures were read locally, not inferred from captions alone.

### Reproducibility and limitations

The reproduction repository is pinned to `main` commit `6360963d53b73ebac5c093a92ff17412e84f2111`. Its scripts exactly expose the paper's key settings and call `MethylVI.setup_mudata`, `MethylVI(...)`, early-stopped training, latent-output/checkpoint saving and scIB metric evaluation [train_methylvi_model.py:14-90, 152-204; calculate_atlas_metrics.py:100-183]. The core model implementation is external in scvi-tools, as stated by the paper [paper.md:96-100], so the clone is an orchestration/reproduction snapshot rather than the authoritative model source. The Nature HTML is a paywalled preview and omits the main Methods/Results; detailed claims therefore retain supplementary-PDF page/line scope. No supplementary Markdown conversion exists (`SUPP_MD=(none)`).

**Reproducibility rating: 3/5.** Data accessions and reproduction scripts are public, but exact main-text numerical results, preprocessing decisions and the installed scvi-tools version are not recoverable from the local preview alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
