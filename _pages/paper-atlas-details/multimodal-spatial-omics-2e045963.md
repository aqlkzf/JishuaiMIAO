---
layout: default
permalink: /paper-atlas/multimodal-spatial-omics-2e045963/
title: "Multimodal_spatial_omics"
nav: false
wide: true
description: "转录组、蛋白组、表观基因组、代谢组和组织学图像各自只观察到细胞状态的一部分，而且分辨率、噪声、稀疏性和坐标体系不同。本文不是提出一个新算法，而是把实验采集策略、整合/融合概念、算法家族、任务和验证难点放在同一张地图上。 连续切片允许每种技术使用最优协议，但必须进行非刚性配准并处理组织形变。共分析在同一切片同时测量多种分子层，空间对应最可靠，却会受到固定、染色和连续反应的兼容性限制。测序型 ST 覆盖广但通常分辨率较低；"
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
      <span>Patterns · 2026</span>
    </div>
    <h1>Multimodal_spatial_omics</h1>
    <p>Multimodal spatial omics: From data acquisition to computational integration</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.patter.2026.101592" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Multimodal_spatial_omics">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 多模态空间组学：从数据采集到计算整合

### 这篇综述解决什么问题？

转录组、蛋白组、表观基因组、代谢组和组织学图像各自只观察到细胞状态的一部分，而且分辨率、噪声、稀疏性和坐标体系不同。本文不是提出一个新算法，而是把实验采集策略、整合/融合概念、算法家族、任务和验证难点放在同一张地图上。

### 实验采集

连续切片允许每种技术使用最优协议，但必须进行非刚性配准并处理组织形变。共分析在同一切片同时测量多种分子层，空间对应最可靠，却会受到固定、染色和连续反应的兼容性限制。测序型 ST 覆盖广但通常分辨率较低；成像型 ST 可达细胞/亚细胞分辨率但常用靶向 panel。ATAC/CUT&Tag、抗体成像、MALDI/DESI 等分别补充染色质、蛋白和代谢物信息。

### 整合与融合

横向整合比较不同样本的同一模态；纵向整合把不同模态通过 spot/cell 坐标连接；对角整合没有直接 anchor，需要学习共同潜空间。早期融合拼接原始特征，中间融合先分别编码再合并表示，晚期融合独立预测后聚合结果。中间融合能表达跨模态非线性，但要防止某一模态支配表示。

### 算法主线

1. 概率模型：令每个位置有共享状态 (z_n)，每个模态有自己的似然 (p(X_n^{(m)}|z_n,\Theta^{(m)}))，通过后验推断得到细胞比例或状态及不确定性。Stereoscope、Cell2location、DestVI 是代表。
2. 矩阵分解：(X^{(m)}\approx ZW^{(m)})，共享因子表示空间程序，模态载荷表示基因/蛋白特征。CellPie、LIGER、SIMO、SPOTlight 具有可解释、低计算成本的优点。
3. 最优传输：Wasserstein OT 在共同特征空间学习细胞-spot 运输计划；GW/FGW 比较两数据集的成对距离，适合不同特征空间。PASTE/PASTE2、Moscot 和 SIMO 用于配准或映射。
4. 深度学习：CNN 编码 H&E，AE/VAE 学习可重建潜表示，GNN 用空间邻接消息传递，Transformer 用注意力学习长程关系。OmiCLIP、Nicheformer 和 GigaTIME 展示了基础模型方向。

### 任务选择

有匹配 scRNA-seq 参考时，优先考虑 Cell2location/Stereoscope；多模态空间域可考虑 SpatialGlue/MISO；小数据或需要可解释性时保留 CellPie/LIGER 基线；连续切片配准可考虑 PASTE/Moscot；H&E 预测需要足够的匹配训练样本。严重 dropout 时使用 NB/ZINB 似然或过滤低信息特征。

### 验证与局限

综述列出 RMSE、MAE、相关系数、ARI/NMI、TRE、Dice、AUC/F1、余弦相似度等任务指标，但强调没有普适 ground truth。理想基准应结合模拟、spike-in、正交技术和扰动实验。主要瓶颈包括分辨率不匹配、MSI 代谢物鉴定、批次效应、TB 级数据、缺少统一格式、伪重复以及将相关关系误读为因果关系。未来需要标准化协议、带元数据的公共数据、可扩展管线和动态/因果模型。

### 证据边界

文章没有随附统一 GitHub 实现；文中列出的工具属于被综述的方法，不能当作本文代码。超参数、运行时间和可复现实验脚本在文章中 `Not found`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Multimodal Spatial Omics: From Data Acquisition to Computational Integration

### Review Scope

Isik et al. (*Patterns* 7, 101592, 2026; DOI 10.1016/j.patter.2026.101592) review the experimental and computational landscape for integrating spatial transcriptomics (ST), proteomics, epigenomics, metabolomics and histology. This is a review, not a new algorithm or benchmark; it supplies a taxonomy, method-selection guidance and a research agenda.

### Central Argument

No spatial modality captures a complete cellular state. Transcriptomics measures active gene programs, proteomics measures effectors, epigenomics measures regulatory potential, and metabolomics measures biochemical output. Integration is difficult because modalities differ in resolution, feature space, noise, sparsity and acquisition geometry. The review's practical message is to choose a method from the acquisition design and biological task, then report uncertainty and validation rather than treating an integrated embedding as ground truth.

### Acquisition Landscape

Two experimental designs are contrasted (paper lines 37-44; Figure 1):

| Design | Strength | Cost / risk |
|---|---|---|
| Serial sections | Each assay can use its best protocol; broad modality choice | Sections must be co-registered; tissue deformation and resolution mismatch create uncertainty |
| Co-profiling | Exact spatial correspondence on one section; no cross-section registration | Assay compatibility, fixation and sequential-processing constraints can reduce quality |

Sequencing ST (ST, Visium/Visium HD, Slide-seq/V2, HDST, Curio) trades coverage for resolution and often has matched H&E. Imaging ST (seqFISH, MERFISH, Xenium/ISS) reaches cellular or subcellular resolution but usually uses targeted panels. Spatial ATAC-seq/CUT&Tag and MISAR-seq add chromatin state, while antibody imaging, CODEX/MIBI/IMC, DSP and MSI provide complementary protein coverage. MALDI/DESI MSI is especially relevant to metabolite mapping but suffers matrix interference and identification ambiguity.

### Integration Taxonomy

The paper separates integration from fusion (lines 117-132; Figure 2). Horizontal integration aligns the same modality across donors or conditions; vertical integration aligns different modalities with a shared spot/cell anchor; diagonal integration has no direct anchor and must infer a shared latent space. Early fusion concatenates features, intermediate fusion combines modality-specific embeddings, and late fusion aggregates independent model predictions. Intermediate fusion best exposes nonlinear cross-modal structure but can suffer modality imbalance; late fusion tolerates missing modalities but can miss interactions.

### Computational Families

| Family | Core idea | Representative methods / tasks | Main trade-off |
|---|---|---|---|
| Probabilistic inference | Modality-specific likelihoods share a latent biological state; posterior inference gives uncertainty | Stereoscope, Cell2location, DestVI; deconvolution and prediction | Principled uncertainty and noise models, but inference/reference assumptions matter |
| Matrix factorization | Approximate each matrix as shared factors plus modality-specific loadings | CellPie, LIGER, SIMO, SEPAR, SPOTlight; domains and deconvolution | Interpretable and lightweight, but low-rank assumptions can miss nonlinear structure |
| OT / geometry | Optimize a transport plan using feature, spatial or relational costs | PASTE/PASTE2, Moscot, SpaOTsc, novoSpaRc, SIMO; alignment and mapping | Handles different feature spaces and geometry, but cost design and scaling are critical |
| CNN / GAN | Encode histology patches and predict molecular maps or profiles | ST-Net, STASCAN, DeepSpaCE, Ouroboros | Strong image-to-omics prediction, data hungry and vulnerable to domain shift |
| AE / VAE / contrastive | Learn shared latent embeddings with reconstruction, KL or positive/negative-pair losses | MUSE, SpaOmicsVAE, stPlus, gimVI, stAI, mclSTExp, BLEEP, SpaMI | Flexible integration and imputation, but latent representations can be hard to validate |
| Graph models | Nodes are spots/cells; edges encode adjacency or learned neighborhood relations | SpaGCN, GraphST, GraphCellNet, KanCell, SpatialGlue, MISO, PRAGA, COSMOS, SpaTranslator | Natural spatial inductive bias; graph construction and oversmoothing can dominate results |
| Transformers / foundation models | Self-attention models long-range gene, image-patch and cross-modal dependencies | spaLLM, TransformerST, THItoGene, Hist2ST, SPATIA, Nicheformer, OmiCLIP, GigaTIME | Global context and transfer; large data, compute and calibration requirements |

### Method Selection

For reference-based deconvolution, Cell2location or Stereoscope are recommended when a matched, annotated scRNA-seq reference is available. For multimodal domains, SpatialGlue or MISO encode neighborhoods and heterogeneous features. CellPie/LIGER are sensible when data are small or interpretability and speed dominate. PASTE/Moscot suit serial-section alignment. CNN/GCN/ViT models suit exploratory H&E prediction when enough matched training data exist. NB/ZINB likelihoods or careful feature filtering are preferable under severe dropout. These are recommendations from the review, not comparative benchmark results.

### Validation and Limitations

The review emphasizes that there is no universal ground truth: mRNA/protein disagreement can be biological or technical, and diagonal integration lacks a shared anchor. Suggested proxies include RMSE/MAE/correlation and JSD/KL/SSIM for deconvolution; ARI/NMI/Silhouette plus spatial coherence for domains; TRE, MSE, LTARI and Dice for registration; correlation, MAE/MSE/RMSE and AUC/F1 for prediction; and cosine/Pearson/Spearman for imputation (lines 253-264). Ideal benchmarks combine simulations, spike-ins, orthogonal assays and perturbations.

Open barriers are assay compatibility, resolution mismatch, sparsity and MSI identification, costs above roughly £5,000-£10,000 per specimen, terabyte-scale storage, fragmented pipelines, batch effects, weak standardization, and limited causal/mechanistic interpretation. The review calls for common protocols and metadata, cloud-accessible reference datasets, ground-truth benchmarks, end-to-end tools (for example SpatialData/Squidpy), donor-aware statistics, and dynamic/causal models for perturbation and digital-twin use cases.

### Reproducibility

This workspace is `paper-only`: acquisition found no paper-specific GitHub implementation or supplementary code. The review cites many independent tools, but comparison repositories are not evidence of an implementation of this review. Claims above are grounded in the local paper text and inspected figures; tool versions, exact hyperparameters and runtime comparisons are generally `Not found` because the source is a survey rather than an executable method paper.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
