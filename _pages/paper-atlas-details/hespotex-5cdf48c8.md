---
layout: default
permalink: /paper-atlas/hespotex-5cdf48c8/
title: "HESpotEx"
nav: false
description: "HESpotEx 是一个两阶段监督学习框架：第一阶段只看真实空间转录组（ST）表达与 spot 坐标，用 GATE/STAGATE 学习“分子—空间”嵌入；第二阶段把每个 spot 对应的 H&E patch 编码成图像嵌入，要求它与第一阶段的 ST 嵌入相关，同时通过空间图解码器预测 spot 级基因表达。 它的输出是根据形态估计的表达，不是新的 RNA 测量。"
robots: noindex, nofollow
sitemap: false
---

<!-- Generated locally by bin/export_paper_atlas.py. -->
<section class="paper-detail" id="paper-detail">
  <a class="paper-detail__back" href="{{ '/paper-atlas/' | relative_url }}">
    <i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Back to Paper Atlas
  </a>
  <header class="paper-detail__hero">
    <div class="paper-detail__chips">
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Computational Science · 2026</span>
    </div>
    <h1>HESpotEx</h1>
    <p>HESpotEx: a dual-stream deep learning framework for spot-level gene expression prediction from histological images</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s43588-026-00992-0" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## HESpotEx：用分子图嵌入监督病理图像预测空间基因表达

### 核心结论

HESpotEx 是一个两阶段监督学习框架：第一阶段只看真实空间转录组（ST）表达与 spot 坐标，用 GATE/STAGATE 学习“分子—空间”嵌入；第二阶段把每个 spot 对应的 H&E patch 编码成图像嵌入，要求它与第一阶段的 ST 嵌入相关，同时通过空间图解码器预测 spot 级基因表达。

它的输出是**根据形态估计的表达**，不是新的 RNA 测量。模型适合生成候选空间表达图和下游假设，但不能替代 ST 实验，也不能因为预测图符合组织结构就推断基因调控或临床诊断。

### 为什么不直接做 image → genes

单个 H&E patch 能显示细胞密度、核形态、组织分区和肿瘤结构，但许多基因的表达并无可见形态特征。HESpotEx 加入两个中间约束：

1. STAGATE 把真实表达与空间邻域压缩成 graph-aware latent，给图像分支一个较稳定的分子目标；
2. 图像解码器聚合相邻 spot，让预测利用组织上下文，而不是逐 patch 独立回归。

Fig. 1 的上半部分是分子教师：表达矩阵与 $X,Y$ 坐标进入 GATE 编码器—解码器。下半部分才是实际预测器：H&E patch → QuiltNet → latent → 图解码器 → 表达。两个阶段通过 spot 顺序一一对应。

### 阶段一：从真实 ST 建立分子嵌入

设一张切片有 $N$ 个 spot、$G$ 个目标基因，表达矩阵为 $X\in\mathbb R^{N\times G}$，空间坐标为 $C\in\mathbb R^{N\times2}$。代码先做基因对齐、HVG 选择、总量归一化和 `log1p`，再按坐标建立 kNN 或半径图 $A$。

STAGATE 可概括为

$$
Z=E_{\mathrm{GATE}}(X,A),\qquad
\hat X=D_{\mathrm{GATE}}(Z,A),
$$

其中 $Z$ 是每个 spot 的低维分子嵌入。训练自编码器重构表达，使 $Z$ 同时保存表达结构和局部空间关系。本地实现位于 `model/expression_embedding.py` 与 `model/exp_module.py`。

这里的 $Z$ 并不是无偏“生物学真值”。若训练数据带有切片批次、测序深度或空间平滑伪影，它们也可能进入嵌入，并在第二阶段成为图像模型的监督目标。

### 阶段二输入：spot patch、空间图和核数量

`CLIPDataset` 按 `adata.obsm['spatial']` 中每个 spot 的像素坐标截取 H&E 区域，并统一缩放至 $224\times224$。同一切片全部 spot 作为一个样本，因此邻接矩阵覆盖整张切片。标准训练路径的 `calcADJ` 默认连接 4 个欧氏最近邻。

若提供 nuclei mask 就直接读取，否则代码用 Cellpose nuclei 模型在整张图上分割。每个 patch 中唯一标签数被截到 $[1,20]$，除以本切片最大值后再加 1，得到范围约为 $(1,2]$ 的核数量因子：

$$
s_i=1+\frac{\operatorname{clip}(n_i,1,20)}{\max_j\operatorname{clip}(n_j,1,20)}.
$$

注意代码的 `len(unique_values)` 可能把背景标签也计入，因此它是经验性 cellularity 修正，不是精确细胞计数。

### QuiltNet 图像编码与 latent 对齐

每个 patch 由冻结的 QuiltNet/OpenCLIP ViT-B-32 编码为 512 维特征：

$$
h_i=f_{\mathrm{QuiltNet}}(I_i).
$$

一个 MLP 将其映射到与 ST embedding 相同维度：

$$
\hat z_i=g_\theta(h_i).
$$

QuiltNet 在训练时被冻结，只有 latent head、图解码器和 gene head 更新。对齐损失直接使用平均 Pearson 相关：

$$
L_{\mathrm{latent}}=1-\operatorname{meanPCC}(Z,\hat Z).
$$

直观上，若真实 ST latent 的两个维度随 spot 同升同降，图像 latent 也应复现这个变化趋势。PCC 强调形状一致性而非绝对尺度，所以还需要表达 MSE 约束最终输出。

### 图上下文解码器到底怎样工作

论文示意图称它为 GCN decoder，但代码不是标准 `GCNConv`。`ImageDecoder` 先对邻居表示做均值聚合；默认 `gcn=False` 时把自身表示和邻居均值拼接，线性变换、ReLU 后做 L2 归一化：

$$
u_i^{(l)}=\operatorname{norm}\left(
\operatorname{ReLU}left(W_l[z_i\,\|\,\operatorname{mean}_{j\in\mathcal N(i)}z_j]\right)
\right).
$$

模型并行地用同一初始 image embedding 通过 4 个 decoder layer，收集四层输出后用两层 LSTM 聚合，并加上直接 gene head：

$$
\tilde y_i=operatorname{LSTM}(u_i^{(1)},\ldots,u_i^{(4)})
+q_\theta(\hat z_i).
$$

最终标准 HESpotEx 乘以核数量因子：

$$
\hat y_i=s_i\tilde y_i.
$$

图分支提供空间平滑和邻域上下文，直接 MLP 分支保留 patch 自身信息，核因子再按估计 cellularity 整体缩放该 spot 的所有基因。这个乘法很强：核分割偏差会同时放大或缩小全部预测基因。

### 训练目标与一个数值例子

本地训练目标是等权相加：

$$
L=L_{\mathrm{latent}}+L_{\mathrm{MSE}}
=\left(1-\overline{\mathrm{PCC}}(Z,\hat Z)\right)
+\operatorname{MSE}(Y,\hat Y).
$$

例如某 batch 的 latent 平均 PCC 为 0.75，表达 MSE 为 0.18，则总 loss 为 $(1-0.75)+0.18=0.43$。代码另计算 gene-wise PCC loss 供测试报告，但训练循环只优化 latent PCC loss 与 MSE。

训练器默认 AdamW、学习率 $10^{-3}$、weight decay $10^{-3}$、batch size 1、最多 50 epochs。一个重要实现风险是：`train.py` 用 **test PCC loss** 选择最佳 epoch，而非验证集指标。如果论文数值直接沿用这一路径，会产生测试集参与模型选择的潜在乐观偏差；工作区代码不能证明论文每个 benchmark 都严格按这段入口执行，因此应标为实现风险而非已确认的论文违规。

推断结束后，代码还将每个预测数组减去其全局最小值，使输出非负。这是 post-hoc 平移，会改变绝对尺度，但不改变相关系数。

### 结果证据怎么读

- HER2+ 数据上，补充材料报告平均 PCC 0.322，第二名 THItoGene 为 0.251；低表达基因比较中 HESpotEx 的 KL divergence 最低。Fig. 2 的消融支持 GATE、QuiltNet、postprocessing 与图解码器组件。
- ncISD 数据的展示基因 OVOL1、IL16、OAS1 在 Fig. 3 中与真实空间模式较一致；这些是预测一致性示例，不是疾病机制验证。
- TCGA-BRCA 中，Fig. 4 将 WSI 切块预测后聚合，与 bulk expression 比较；补充材料报告 1042 个样本平均 PCC 0.498。两组预测表达的生存曲线 HR=2.399、$P=0.037$，说明有关联，但并不能证明模型具有独立临床预后效用。
- cSCC 的预测 cluster 与病理区域、淋巴细胞浸润和 NOTCH1 图有空间对应。这里应解释为病理一致性和假设生成，而非自动诊断。
- Xenium 与 Visium HD 结果展示更高分辨率迁移和分块拼接；本地仓库未提供完整重建脚本，不能从核心 Python 文件独立复现这些图。

### 论文—代码映射

| 机制 | 直接证据 | 匹配 | 边界 |
|---|---|---|---|
| GATE/STAGATE spot embedding | `model/expression_embedding.py:115-162`、`model/exp_module.py:20-46` | Exact | 预处理与嵌入可追踪 |
| QuiltNet encoder | `model/models.py:26`、`model/image_modules.py:56-71` | Exact | 权重需手动放到固定路径 |
| image latent 与 PCC 对齐 | `model/models.py:92,120` | Exact | PCC 对齐而非对比学习 |
| 四个 graph decoder + LSTM | `model/models.py:33-37,96-105` | Partial | 与“GCN decoder”概念一致，层实现不是标准 GCN |
| 直接 gene head | `model/models.py:45-50,94-105` | Exact | 与图输出残差相加 |
| nuclei postprocessing | `common/dataset.py:61-83`、`model/models.py:107` | Exact | 经验性乘法修正，依赖 Cellpose |
| latent PCC + expression MSE | `model/models.py:120-126`、`train.py:45-46` | Exact | 两项等权 |
| checkpoint 与输出平移 | `train.py:159-178` | Exact | 测试集选 epoch、预测减最小值 |
| 全 benchmark、TCGA survival、HoVer-Net 验证 | 本地代码树直接搜索 | Not found | 主结果有论文/补充证据，但缺少对应执行脚本 |

### 版本与可复现性边界

1. 论文是 *Nature Computational Science* 2026，DOI `10.1038/s43588-026-00992-0`。工作区主文来源仍是订阅 HTML preview；名为 `paper.pdf`、`paper.accept.pdf` 和 `try.pdf` 的文件实际是 HTML，不是有效 PDF。可验证的完整补充材料来自 `paper_supp1.pdf`/`supplementary_information.md`，另有 peer-review 文档。
2. 本地代码来自 `https://github.com/wwYinYin/HESpotEx`，采集提交 `c3964aac60de9332c5cb2c7582829f2ba983fae5`。代码目录没有独立嵌套 `.git`，提交值来自工作区采集元数据。
3. 代码硬编码 `cuda:1`，STAGATE 还有独立设备设置；QuiltNet 权重必须手动放在 `./model/QuiltNet-B-32/open_clip_pytorch_model.bin`。这些都会阻止开箱即跑。
4. 核心模型与教程存在，但论文全 benchmark、TCGA 聚合/UMAP/生存、HoVer-Net 淋巴细胞验证和高分辨率拼接工作流未在所读代码中找到。
5. 本轮验证的是源文档—代码对应，没有下载全部外部数据、运行约 15 小时 A100 教程或重做论文统计。因此 `ready_to_publish` 表示分析合同完整，不表示数值复现完成。

### 一句话记忆

HESpotEx 先用真实 ST 图学出“分子坐标系”，再让冻结 QuiltNet 的 H&E patch 表示进入这个坐标系，并用邻域解码器和核数量因子预测表达；它增强了形态到表达的空间约束，但输出始终是模型估计，且当前仓库的完整论文结果复现链仍不齐全。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## HESpotEx Summary

### Motivation and Novelty

HESpotEx tackles spot-level gene expression prediction from routine H&E histology. The biological motivation is practical: spatial transcriptomics reveals tissue molecular organization but is costly, while H&E WSIs are abundant and clinically routine. HESpotEx tries to infer spatial molecular patterns from morphology alone.

The novelty is a dual-stream, two-stage design. First, ST expression and spot coordinates are embedded with a graph attention autoencoder. Second, H&E patches are encoded with a pretrained QuiltNet image model, aligned to the ST latent space with a PCC-based loss, decoded through a graph-context module, and postprocessed with nuclei-count information. This differs from simpler image-only regressors by explicitly using an ST graph latent target and neighborhood-aware decoding.

### Method Overview

HESpotEx starts from paired ST data and H&E images. It preprocesses gene expression, constructs a spatial graph, and trains STAGATE/GATE to produce expression-derived spot embeddings. It then crops 224 x 224 H&E patches around spots, extracts image features with a frozen QuiltNet encoder, maps those features into the ST latent space, and predicts expression through a graph decoder plus direct gene head. The implementation trains with equal-weight latent PCC loss and expression MSE.

Predictions are evaluated as gene-expression matrices over spots or WSI tiles. Downstream analyses include spatial gene maps, unsupervised clustering of predicted expression, TCGA-BRCA aggregation and survival association, and high-resolution ST consistency analysis.

### Evaluation

Accessible supplementary notes and figures report broad evaluations:

- HER2+ breast cancer: mean PCC 0.322 for HESpotEx versus 0.251 for THItoGene, and KL 1.321 versus 1.497 for OmiCLIP.
- cSCC: mean PCC 0.239 versus 0.188 for IGI-DL, and KL 1.617 versus 1.696 for OmiCLIP.
- Low-expression HER2+ genes: HESpotEx has the lowest KL divergence among compared methods.
- ncISD datasets: HESpotEx leads on AD, LP, and psoriasis in reported PCC/KL/MSE comparisons.
- TCGA-BRCA: Supplementary Note 7 reports mean PCC 0.498 across 1042 samples and 0.526 across 169 HER2+ samples, far above the second-ranked OmiCLIP; predicted-expression clusters show survival association with HR = 2.399 and P = 0.037.
- In-house cSCC WSIs: predicted clusters and NOTCH1 maps align with differentiation, lymphocyte infiltration, and tumor regions.
- High-resolution ST: HESpotEx is reported to preserve cross-sectional continuity better than baselines.

Baselines include THItoGene (Briefings in Bioinformatics, 2023), Hist2ST (Briefings in Bioinformatics, 2022), TCGN (Medical Image Analysis, 2024), OmiCLIP (Nature Methods, 2025), mclSTExp (Briefings in Bioinformatics, 2024), BLEEP (NeurIPS, 2023), and related methods such as iStar (Nature Biotechnology, 2024).

### Reproducibility

**Rating: 2.5 / 5.**

The core model is available under MIT license, and the repository exposes the main architecture, data loaders, STAGATE embedding, training loop, and tutorial. Processed datasets are linked through Zenodo, and the README explains required inputs.

The rating is limited because the main article full text/PDF was not accessible in this environment, exact paper equations could not be checked, and the repository read here does not expose a complete benchmark-reproduction pipeline for every figure. Several practical barriers also appear in code: hardcoded CUDA devices, manually required QuiltNet weights, notebook-centered tutorials, and missing plain scripts for TCGA survival analysis, HoVer-Net validation, and all baseline comparisons. Therefore the core method is understandable and partially runnable, but full paper-figure reproduction is not demonstrated from the packaged Python files alone.

### Key Caveats

- This workspace is a partial analysis because the main full text/PDF was inaccessible through the current Nature route.
- Main claims are supported by accessible abstract, supplementary notes, figures, README, and code, but exact main-paper method wording remains unresolved.
- Evaluation claims not backed by visible code are marked as not found or notebook/external-script dependent in `doc_code.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
