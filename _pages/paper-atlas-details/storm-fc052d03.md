---
layout: default
permalink: /paper-atlas/storm-fc052d03/
title: "STORM"
nav: false
wide: true
description: "STORM 是一个把 H&E 病理形态、空间转录组表达和组织空间邻域放进同一表示空间的多模态基础模型。它先在配对的 H&E-ST 数据上做空间掩码预训练，再把学到的表示用于空间域发现、从 H&E 预测虚拟 ST，以及患者预后和免疫治疗反应建模。"
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
      <span>—</span>
    </div>
    <h1>STORM</h1>
    <p>A Multimodal Foundation Model of Spatial Transcriptomics and Histology for Biological Discovery and Clinical Prediction</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STORM 方法详解

### 一句话理解

STORM 是一个把 H&E 病理形态、空间转录组表达和组织空间邻域放进同一表示空间的多模态基础模型。它先在配对的 H&E-ST 数据上做空间掩码预训练，再把学到的表示用于空间域发现、从 H&E 预测虚拟 ST，以及患者预后和免疫治疗反应建模（`paper.md:61-70`, `paper.md:202-272`）。

### 证据边界

本文直接依据论文正文和 Online Methods，重点覆盖 `paper.md:40-70`, `paper.md:79-193`, `paper.md:196-305`。论文只说明代码和模型在同行评审阶段作为补充软件提供，并计划在正式发表后公开（`paper.md:302-305`）。因此本文严格区分：

- **论文陈述**：论文明确写出的模型、训练或结果；
- **方法解释**：为帮助理解而对论文结构作出的解释，不等同于作者明确结论；
- **代码验证**：**Not found**，因为 `code source=none`；

### 1. 论文要解决什么问题？

空间转录组能够在组织坐标中测量基因表达，但成本高、流程复杂、通量有限。H&E 切片便宜、常规且包含丰富形态信息，却不能直接给出分子表达。此前的 H&E-to-ST 方法通常面向单一癌种或小数据集，并依赖任务特定训练，因此跨组织和跨平台泛化受限（`paper.md:40`, `paper.md:46-52`）。

论文比较的相关方法包括：

- BLEEP，NeurIPS 2023，用双模态对比学习预测空间表达（`paper.md:379`）；
- DeepPT，Nature Cancer 2024，通过插补转录组支持病理治疗反应预测（`paper.md:337`）；
- OmiCLIP，Nature Methods 2025，是已有的视觉-组学基础模型（`paper.md:321`）；
- Virchow 和 GigaPath 等病理基础模型，主要从大规模形态数据学习视觉表示（`paper.md:373`, `paper.md:380`）；
- SpaGCN，Nature Methods 2021，以及 GraphST，Nature Communications 2023，主要利用表达、空间图或平滑约束发现空间域（`paper.md:338`, `paper.md:344`）。

STORM 的核心目标不是只做一次 H&E-to-ST 回归，而是先学习一种同时理解“局部形态、局部分子状态、邻域组织结构”的通用表示。

### 2. 输入、输出和两级层次结构

STORM 的结构分为两个层级（`paper.md:202`）：

1. **spot 层**：分别编码单个位置的 H&E patch 和 ST 表达；
2. **空间层**：联合处理一个局部邻域中的多模态 token，使中心位置的表示包含周围组织上下文。

| 阶段 | 输入 | 输出 | 论文位置 |
|---|---|---|---|
| ST spot 编码 | $\bm{X}\in\mathbb{R}^{1\times M}$ | $\bm{H}_G\in\mathbb{R}^{1\times64}$ | `paper.md:205` |
| H&E patch 编码 | $\bm{V}\in\mathbb{R}^{1\times C}$ | $\bm{H}_P\in\mathbb{R}^{1\times768}$ | `paper.md:205` |
| 空间编码 | 邻域 token、模态标识、空间位置 | 空间上下文化的 H&E/ST 表示 | `paper.md:202-221` |
| 掩码预训练 | 部分可见的 H&E-ST 邻域 | 对被遮挡位置的重建分布 | `paper.md:225-232` |
| 下游任务 | H&E，或配对 H&E-ST | 空间域、虚拟 ST、患者风险分数 | `paper.md:241-272` |

论文预训练数据包含 632 张配对 H&E-ST 组织切片、约 120 万个空间位置、18 个器官和四类空间转录组平台（`paper.md:61`, `paper.md:70`）。

### 3. 第一级：单位置模态编码

对每个空间位置，NOVAE 编码基因表达：

$$
\bm{H}_{G}=f_{\mathrm{ST}}(\bm{X})\in\mathbb{R}^{1\times h},\qquad h=64.
$$

H0-mini 编码对应的 H&E patch：

$$
\bm{H}_{P}=f_{\mathrm{HE}}(\bm{V})\in\mathbb{R}^{1\times d},\qquad d=768.
$$

这里的直观含义是：NOVAE 提供分子状态摘要，H0-mini 提供形态摘要，空间编码器再决定一个位置应如何结合自身和邻居的信息（`paper.md:202-208`）。

**缺失信息：**论文没有说明 64 维 ST token 和 768 维 H&E token 如何投影到同一空间编码维度，也没有给出对应投影层的参数。没有代码，因此无法验证这一接口。

### 4. 第二级：空间多模态编码

对于 Visium，模型联合处理 $5\times5$ 的 spot 邻域（`paper.md:202`）。每个空间 block 包含：

- 共享的多头自注意力 MSA，用于不同位置和不同模态之间的信息交互；
- 两个模态专属的前馈网络，即 modality experts；
- LayerNorm、残差连接、模态嵌入和 ALiBi 位置偏置（`paper.md:208-221`）。

输入 token 写为：

$$
\bm{H}_{0,i}=\bm{H}_{i}+\bm{M}_{i}+\bm{P}_{i}. \tag{1}
$$

其中，$\bm{H}_{i}\in\{\bm{H}_{P,i},\bm{H}_{G,i}\}$ 是形态或表达特征，$\bm{M}_{i}\in\{\bm{M}_{H},\bm{M}_{G}\}$ 表示 token 属于哪种模态，$\bm{P}_{i}$ 表示通过 ALiBi 注入的位置关系（`paper.md:211-218`）。

一个空间 block 的更新为：

$$
\bm{H}_{l}^{\prime}=\operatorname{MSA}(\operatorname{LN}(\bm{H}_{l-1}))+\bm{H}_{l-1},
\qquad
\bm{H}_{l}=\operatorname{MoME\text{-}FFN}(\operatorname{LN}(\bm{H}_{l}^{\prime}))+\bm{H}_{l}^{\prime}. \tag{2}
$$

**方法解释：**共享 MSA 负责跨位置和跨模态融合，模态专属 FFN 则允许 H&E 与 ST 保留不同的非线性变换。论文明确支持 H&E+ST 联合输入，也支持 H&E-only；当 ST token 缺失时，注意力退化为普通 H&E 自注意力（`paper.md:208`）。

**缺失信息：**空间 block 数量、attention head 数量、隐藏维度、FFN 宽度、dropout 和二维坐标如何具体转换为 ALiBi 偏置均未给出。

### 5. 多模态空间掩码预训练

论文把 H&E-ST spot 类比为“词”，把空间邻域类比为“句子”。模型随机遮挡位置，只保留每个模态 5 个可见 spot，然后用模态专属 decoder 重建被遮挡的信息。每个 decoder 由一个 MLP 和两个 Transformer block 构成，预训练结束后丢弃（`paper.md:225`）。

预训练目标为：

$$
\mathcal{L}_{\text{pretrain}}=-\frac{1}{\|\mathcal{M}_{\mathrm{HE}}\|}\sum_{i\in\mathcal{M}_{\mathrm{HE}}}\log p_{\mathrm{HE}}\!\left(z_{\mathrm{HE},i}\mid\mathbf{X}^{\mathcal{M}}\right)-\frac{1}{\|\mathcal{M}_{\mathrm{ST}}\|}\sum_{i\in\mathcal{M}_{\mathrm{ST}}}\log p_{\mathrm{ST}}\!\left(z_{\mathrm{ST},i}\mid\mathbf{X}^{\mathcal{M}}\right). \tag{3}
$$

$\mathcal{M}_{\mathrm{HE}}$ 和 $\mathcal{M}_{\mathrm{ST}}$ 分别是两种模态的被遮挡位置，$\mathbf{X}^{\mathcal{M}}$ 是掩码后的输入（`paper.md:225-228`）。

**方法解释：**如果模型要从少量可见位置恢复缺失形态和表达，它就必须学习三类关系：同一位置的形态-分子关系、相邻位置的组织结构关系，以及跨平台基因面板差异下仍可复用的特征。

**缺失信息：**论文没有定义 $z_{\mathrm{HE},i}$ 和 $z_{\mathrm{ST},i}$ 的具体形式、离散化方式、概率分布、decoder 输出参数化或精确采样策略。因此 Eq. 3 不能仅凭正文完整复现。

### 6. 预训练配置

论文报告的配置如下（`paper.md:232`）：

| 配置 | 数值 |
|---|---|
| 训练轮数 | 1000 epochs |
| 优化器 | AdamW |
| 学习率 | $10^{-4}$ |
| weight decay | $0.05$ |
| 学习率调度 | 40 epoch warmup 后 cosine decay |
| batch size | 1024 |
| 硬件 | 8 张 NVIDIA H100 |
| 精度 | automatic mixed precision |
| ST 编码器 | NOVAE，冻结 |
| 可训练部分 | H0-mini 和空间编码器 |
| layer-wise LR decay | $\lambda=0.7$ |
| H&E 增强 | random resized crop 和翻转 |
| ST 增强 | 无 |

为兼容不同平台的基因面板，decoder 预测所有面板基因的并集，但对当前输入中不存在的基因进行 mask。论文以 Xenium 少于 500 个基因、Visium 多于 10,000 个基因为例说明这种异质性（`paper.md:232`）。

### 7. 从输入到输出的完整计算流程

```text
配对 H&E + ST + 空间坐标
          |
          v
切出局部邻域（Visium 为 5 x 5 spot）
          |
     +----+----+
     |         |
     v         v
 H0-mini     NOVAE
 H&E 768维   ST 64维
     |         |
     +----+----+
          |
加入模态嵌入和 ALiBi 位置关系
          |
          v
共享 MSA + 模态专属 FFN
          |
          v
对被遮挡 H&E/ST 位置做联合重建
          |
   丢弃预训练 decoder
          |
          v
得到可迁移的 STORM 编码器
     +---------+----------------+
     |         |                |
     v         v                v
H&E+ST 聚类  H&E -> 虚拟 ST   WSI 临床预测
K-means      轻量 MLP head    跨模态融合+池化
```

### 8. 三类下游任务

#### 8.1 空间域发现

模型直接编码配准后的 $5\times5$ H&E-ST 邻域，不做额外任务训练，然后用 K-means 聚类。评价包括 NMI、ARI、FMI、HOM、COM、CHAOS、PAS 和 ASW。差异表达采用 Wilcoxon rank-sum test 和 Benjamini-Hochberg 校正，通路富集采用 Fisher's exact test，阈值为 FDR $<0.05$（`paper.md:241-244`）。

论文报告：肾癌平均 NMI/ARI 为 0.53/0.40，肺癌为 0.62/0.60，高于 OmiCLIP 和其他基线；模型还分离出具有代谢、炎症和免疫差异的细粒度区域（`paper.md:79-94`）。

#### 8.2 从 H&E 预测虚拟 ST

在 STORM 后接一个轻量 MLP，只训练该 prediction head。Visium 实验使用 80/20 slide-level split，训练 10 epochs，AdamW 学习率为 $5\times10^{-4}$，以 500 个 HVG 的 gene-wise PCC 评价（`paper.md:247-250`）。

微调损失为：

$$
\mathcal{L}(\bm{Y},\hat{\bm{Y}})=\frac{1}{NG}\sum_{i=1}^{N}\sum_{j=1}^{G}\left(\lambda_{1}\left\|y_{ij}-\hat{y}_{ij}\right\|+\lambda_{2}(y_{ij}-\hat{y}_{ij})^{2}\right). \tag{4}
$$

**方法解释：**该式看起来是加权的 L1/范数项与 L2 平方项组合，但论文没有明确第一项范数的定义，也没有给出 $\lambda_1$ 和 $\lambda_2$。

论文报告八个肿瘤数据集中 STORM 的中位 PCC 均为最高，例如结直肠癌为 0.633，而 DeepPT 为 0.304、Virchow 为 0.266（`paper.md:103-106`）。在 Xenium、Visium HD 和 CosMx 上，模型也报告了高于对比方法的结果（`paper.md:133-136`）。这些结果未在本地复现。

#### 8.3 患者级临床预测

全切片被切成 $55\,\mu$m patch：$20\times$ 下为 $110\times110$ px，$40\times$ 下为 $220\times220$ px，再缩放到 $224\times224$。STORM 从 H&E 生成虚拟 ST；H&E 与虚拟 ST 特征经过 Perceiver 压缩、cross-attention 融合和模态专属 attention pooling，得到 slide-level 风险分数（`paper.md:263-269`）。

论文报告结直肠癌和肺癌预后 C-index 为 0.701-0.741，并在 SURGEN 和 NLST 外部测试集上评估；Integrated Gradients 用于定位风险贡献，细胞组成和通路分析用于解释预测（`paper.md:145-178`, `paper.md:272`）。

### 9. 消融实验在检验什么？

论文分别替换或移除四类组件（`paper.md:235-238`）：

1. 用随机初始化模型或直接 H0-mini 替代 STORM 中的 H&E 编码方案；
2. 用原始 HVG 向量替代 NOVAE；
3. 把 grid size 设为 1，移除空间上下文；
4. 不做预训练，只从随机初始化训练下游任务。

这四组消融分别检验形态预训练、ST 表示、空间邻域和多模态预训练的作用。当前转换后的正文没有给出完整数值消融表，且本地没有图像或代码，无法进一步核对。

### 10. 如何理解 STORM 的核心创新？

**论文直接支持的部分：**

- 使用独立的 H&E 和 ST foundation encoder 获取 spot 表示；
- 在局部空间邻域内用共享注意力融合两种模态；
- 用模态专属 FFN 保留不同模态的处理路径；
- 通过空间掩码重建学习可迁移表示；
- 同一编码器同时支持 H&E+ST 和 H&E-only 输入（`paper.md:202-232`）。

**解释性总结：**STORM 的关键不是把 H&E 特征和表达向量简单拼接，而是让“模态对齐”和“空间上下文”在预训练阶段同时发生。这样，H&E-only 推理仍可利用训练时学到的形态-分子对应关系。

这段是方法解释，不是代码验证；没有公开实现时，不能确认 token 排列、projection、attention mask 或 decoder 的具体行为。

### 11. 可复现性缺口

- STORM 公开代码、checkpoint、环境文件和 runnable example；
- 64 维与 768 维 token 的投影方式；
- spatial encoder 的层数、head 数、隐藏维度、FFN 结构和 dropout；
- 二维组织坐标对应的 ALiBi 细节；
- 掩码采样、重建 target $z$ 和概率分布；
- Eq. 4 中 $\lambda_1$、$\lambda_2$ 的值及表达归一化流程；
- Perceiver、cross-attention、pooling、response/prognosis head 的完整配置；
- 完整数据清单、随机种子和可执行划分脚本；
- 本地补充材料和 Figure 1-5 图像。

此外，论文摘要报告 23 个独立队列、7245 名患者（`paper.md:40`, `paper.md:70`），Discussion 又写 11 个队列、超过 2500 名患者（`paper.md:184`）。在把临床范围作为固定事实引用前，需要作者澄清统计口径。

### 12. 阅读结论

从方法层面看，STORM 提供了一个清晰的三段式框架：单位置模态编码、空间多模态融合、掩码重建预训练。论文报告的空间域、虚拟 ST 和预后结果支持该框架的潜力，但这些仍是论文陈述。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## STORM Summary

### Problem

Spatial transcriptomics (ST) maps gene expression in tissue context but is costly and low-throughput; H&E is routine and morphologically rich but lacks molecular resolution (`paper.md:46-52`). Existing task-specific H&E-to-ST models, pathology foundation models, and ST-domain methods are described as narrower or less generalizable than a pretrained multimodal model (`paper.md:49`, `paper.md:67`, `paper.md:85`). The comparison set includes BLEEP (NeurIPS 2023; `paper.md:379`), DeepPT (Nature Cancer 2024; `paper.md:337`), pathology models such as Virchow (Nature 2024; `paper.md:373`) and GigaPath (Nature 2024; `paper.md:380`), and OmiCLIP (Nature Methods 2025; `paper.md:321`).

### Proposed method

STORM (Spatial Transcriptomics and histOlogy Representation Model) is a hierarchical H&E-ST foundation model. It pretrains on 1.2 million spots from 632 paired sections across 18 organs. NOVAE encodes each ST gene vector to 64 dimensions and H0-mini encodes each H&E patch to 768 dimensions. A spatial encoder then processes a $5\times5$ neighborhood with shared multi-head self-attention, modality-specific feed-forward experts, modality embeddings, and ALiBi positional biases (`paper.md:61-64`, `paper.md:202-221`). Masked H&E/ST spots are reconstructed with modality-specific decoders; the reported pretraining objective is a sum of masked negative log-likelihoods (`paper.md:225-232`).

The resulting representation is used in three modes: K-means clustering for multimodal spatial domains, a lightweight MLP head for H&E-to-ST prediction, and slide-level clinical prediction after H&E-derived virtual ST is fused with morphology by cross-attention and attention-based pooling (`paper.md:241-272`).

### Evaluation

- **Spatial domains:** On eight kidney/lung samples, the manuscript reports mean NMI/ARI of 0.53/0.40 in kidney and 0.62/0.60 in lung, above OmiCLIP and other baselines; it also reports high spatial homogeneity and low abnormal-spot scores (`paper.md:79-85`).
- **Visium virtual ST:** Across eight tumor types (142 sections, 85,236 spots), STORM reports the highest median gene-wise PCC in every dataset. Colorectal PCC is 0.633 versus 0.304 for DeepPT and 0.266 for Virchow (`paper.md:103-106`).
- **Unseen histologies/platforms:** Reported median PCCs are 0.586 for ovarian cancer, 0.447 for mesothelioma, and 0.557 for DLBCL; high-resolution results include 0.209 on Xenium, 0.298 on Visium HD, and 0.295/0.280 on CosMx ovarian/colorectal cohorts (`paper.md:127-136`).
- **Prognosis:** H&E plus virtual ST is reported to achieve C-indices from 0.701 to 0.741 in colorectal and lung cohorts, with external SURGEN/NLST testing, 1,000-bootstrap comparisons, and significant risk stratification (`paper.md:145-154`).
- **Interpretation:** Integrated Gradients, cell composition, and gene/pathway analyses associate high-risk regions with tumor/stromal features and low-risk regions with immune infiltration (`paper.md:163-178`).

These are reported manuscript results, not locally reproduced measurements. Figure assets are absent, so no plotted result was independently inspected (`figure_analysis.md`).

### Reproducibility and limitations

**Reproducibility rating: 1/5 (paper-only).** The paper provides the main architecture, equations, training settings, benchmark cohorts, and data links. However, the workspace has no public code, checkpoint, environment, runnable example, or supplementary implementation. The paper says code/model are peer-review supplementary software and will be released for non-commercial academic research upon publication (`paper.md:302-305`). Exact projection layers between the 64-D and 768-D encoders, spatial-block widths/heads, ALiBi construction, masking targets, decoder likelihoods, Eq. (4) weights, normalization, split seeds, and clinical-head details are not specified (`doc_method.md`).

Data access is mixed: many ST and H&E cohorts are linked publicly, but all immunotherapy cohorts are held at Stanford and are not publicly available because of privacy (`paper.md:281-293`). The manuscript also reports different aggregate cohort totals in the abstract (23 cohorts, 7,245 patients; `paper.md:40`, `paper.md:70`) and discussion (11 cohorts, more than 2,500 patients; `paper.md:184`); this count discrepancy should be resolved before treating the clinical scope as a fixed inventory.

### Bottom line

The paper's central contribution is a spatially contextual multimodal pretraining scheme that lets H&E morphology and ST expression inform one another while supporting H&E-only virtual ST inference. The reported benchmarks support strong cross-tissue and cross-platform performance, but exact implementation and independent verification remain unavailable in this workspace.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
