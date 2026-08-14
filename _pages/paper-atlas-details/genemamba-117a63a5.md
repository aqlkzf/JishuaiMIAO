---
layout: default
permalink: /paper-atlas/genemamba-117a63a5/
title: "GeneMamba"
nav: false
wide: true
description: "单细胞 RNA 测序把每个细胞表示成一个高维、稀疏的基因表达向量。基于 Transformer 的模型在长基因序列上有二次复杂度；单向序列模型又只能看到一个方向的上下文。GeneMamba 的目标是用线性扩展的状态空间模型处理长序列，同时保留基因之间的生物学关系。 论文把“细胞”看作句子，把“基因”看作 token。"
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
      <span>arXiv · 2025</span>
    </div>
    <h1>GeneMamba</h1>
    <p>GeneMamba: An Efficient and Effective Foundation Model on Single Cell Data</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/MineSelf2016/GeneMamba" target="_blank" rel="noopener noreferrer" aria-label="Open code for GeneMamba">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GeneMamba 方法说明

### 解决什么问题

单细胞 RNA 测序把每个细胞表示成一个高维、稀疏的基因表达向量。基于 Transformer 的模型在长基因序列上有二次复杂度；单向序列模型又只能看到一个方向的上下文。GeneMamba 的目标是用线性扩展的状态空间模型处理长序列，同时保留基因之间的生物学关系（论文 `paper.md:11-67`）。

### 方法核心

论文把“细胞”看作句子，把“基因”看作 token。先对表达矩阵做细胞测序深度和基因尺度归一化，再在每个细胞内部按归一化表达量降序排列基因，保留前 2,048 或 4,096 个基因。随后，基因 ID 经过 embedding，进入多层 Bi-Mamba；正向和反向状态通过可学习门控融合，最后输出基因词表上的 logits 和上下文表示。

```text
CELLXGENE 原始矩阵
      |
去重、保留人类基因、过滤低质量细胞、library-size + log1p
      |
每个基因的非零中位数（论文称用 t-digest 估计）
      |
每个细胞内按归一化表达量降序排序，截取 2,048/4,096 基因
      |
Gene embedding -> 正向 Mamba + 反向 Mamba -> gate -> 表示/logits
      |
下一基因预测 NLL + 基因共表达/通路 InfoNCE
      |
整合、细胞类型注释、基因排序重建、基因关系和扰动分析
```

### 关键公式

论文的归一化为

$$M_{ij}^{\mathrm{norm}}=\frac{M_{ij}/\sum_{k=1}^{n}M_{ik}}{\operatorname{t\text{-}digest}\{M_{kj}\mid M_{kj}>0\}}.\tag{1}$$

排序为

$$R_i=\operatorname{argsort}(-M_{ij}^{\mathrm{norm}}).\tag{2}$$

Bi-Mamba 对原序列和有效 token 的反向序列共享层参数，分别得到 $h_t$ 和 $\tilde h_t$，再计算

$$z_t=\sigma(W[h_t,\tilde h_t]),\qquad o_t=z_t h_t+(1-z_t)\tilde h_t.\tag{8-9}$$

预训练损失是

$$\mathcal L=\mathcal L_{\mathrm{lang}}+\gamma\mathcal L_{\mathrm{pathway}},\qquad \gamma=0.1,\tag{15}$$

其中 $\mathcal L_{\mathrm{lang}}$ 是按位置右移后的下一基因交叉熵，$\mathcal L_{\mathrm{pathway}}$ 用温度缩放的余弦相似度拉近同通路基因、区分不同通路基因。

### 论文结果

- **多批次整合：** PBMC12k 的 Avg-batch/Avg-bio 为 0.9604/0.8344，Perirhinal Cortex 为 0.9573/0.9062；UMAP 中批次颜色相互混合，而细胞类型仍形成结构化簇（论文 Figures 3, 12, 13）。
- **细胞类型注释：** hPancreas 的准确率/Macro-F1 为 0.9713/0.7710；MS 为 0.6825/0.5342；平衡后的 Myeloid_b 为 0.9603/0.9235（`paper.md:285-310`）。
- **基因排序重建：** GeneMamba 的 L-Dist=6、BLEU=0.987、Spearman=0.711；Figure 4 中输入输出集合有 6,246 个共享基因，密度图接近对角线。
- **基因表示关系：** Figure 15 中 GeneMamba 与 Gene2Vec 的距离约为 Euclidean 0.14、KL 0.15、JS 0.15，明显低于与随机 embedding 的距离。
- **扰动分析：** 论文声称 Norman/GEARS 任务中 Pearson $r=0.5686$，但 Figure 10 的打印标签和统计量存在冲突，应视为待核查证据。

### 代码核验与复现边界

代码快照为 GitHub `GeneMamba` commit `22f571a8d48256894de05e9d87ea9ec6caa338c0`。`preprocess/h5ad_to_input_ids.py:20-38` 确实会过滤正值、按原始表达量降序排序、映射 token 并截断；但在搜索到的转换器中没有找到论文 Eq. (1) 的 library-size/t-digest 归一化。`genemamba/models/models.py:425-488` 实现了有效 token 的反向、正反向对齐和 gate 融合，但 `models.py:403-406` 计算 `self.mamba(X)+X` 后返回的仍是原始 `X`，因此该快照的实际 Mamba 变换传播与论文设计不一致。

训练器在 `genemamba/utils/utils.py:278-346` 实现右移交叉熵、L2 归一化、温度 0.1 和 `gamma=0.1`；共表达矩阵在 `utils.py:368-391` 被硬编码为 CUDA sparse tensor。`pretrain/train.py:30-44` 在启动时直接初始化 NCCL `env://` 分布式进程组，所以没有证据表明 CPU 或单进程环境可以直接复现预训练。整合、注释和排序重建有脚本，但拓扑分析主要是 notebook，代码库中未找到与论文扰动实验对应的完整入口。

### 如何理解结论

论文结果说明 BiMamba + 排序 token 化在作者设定的数据和 checkpoint 上具有竞争力；它们不等于当前代码快照已经可端到端复现。阅读或复现实验时，应分别记录论文声称、图像直接显示的现象、代码实际执行的行为，以及尚未找到的归一化、数据、checkpoint 和扰动实现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## GeneMamba Summary

### Problem

Single-cell RNA-seq foundation models must represent thousands of sparse gene measurements per cell while retaining biological relationships and scaling to tens of millions of cells. The paper argues that transformer self-attention is costly for these long sequences and that unidirectional sequence models miss downstream context (`paper.md:11-67`).

### Proposed Method

GeneMamba ranks genes within each cell after library-size and per-gene median normalization, embeds the resulting gene-token sequence, and applies stacked bidirectional Mamba/SSM processing. Forward and reverse states are fused by a learnable gate. Pretraining combines causal next-gene prediction with a coexpression/pathway contrastive objective (`paper.md:80-236`).

### Evaluation And Results

The paper constructs a CELLXGENE corpus of 29,849,897 cells after deduplication and quality filtering, then evaluates downstream embeddings on integration, cell annotation, rank reconstruction, gene-pair similarity/topology, and perturbation tasks. Baselines include GeneFormer, scGPT, scFoundation, scBERT, and Harmony (`paper.md:223-284`).

- **Integration:** GeneMamba reports strong Avg-batch/Avg-bio scores, including 0.9604/0.8344 on PBMC12k and 0.9573/0.9062 on perirhinal cortex; the UMAPs show mixed batches with separated cell types (`paper.md:255-284`; Figures 3, 12, 13).
- **Annotation:** reported GeneMamba scores include hPancreas accuracy 0.9713 and Macro-F1 0.7710, MS accuracy 0.6825 and Macro-F1 0.5342, and balanced Myeloid_b accuracy 0.9603 and Macro-F1 0.9235 (`paper.md:285-310`). Figure 11 makes the dataset heterogeneity visible.
- **Rank reconstruction:** GeneMamba achieves L-Dist 6, BLEU 0.987, and Spearman 0.711 on the reported PBMC12k comparison, with a near-diagonal density plot and 6,246 shared input/output genes in Figure 4 (`paper.md:311-336`).
- **Gene representations:** Figure 15 shows GeneMamba closer to Gene2Vec than random embeddings across Euclidean, KL, and JS distances (0.14/0.15/0.15 versus about 0.45/0.42/0.41). Figure 7 shows positive-pair distributions with heavier right tails and shared topology labels.
- **Perturbation:** the paper reports better Norman/GEARS-style prediction and Pearson $r=0.5686$, but Figure 10 prints a conflicting label/statistic assignment; this result needs source clarification before being treated as settled.

### Reproducibility

The GitHub snapshot at commit `22f571a8d48256894de05e9d87ea9ec6caa338c0` contains preprocessing, model, trainer, integration, annotation, and reconstruction code. The converter exactly implements positive-value descending rank tokenization (`preprocess/h5ad_to_input_ids.py:20-53`), and downstream scripts expose concrete metric workflows. However, the searched snapshot does not contain the paper's t-digest normalization implementation, pretraining data/checkpoints, or a perturbation pipeline. `EncoderLayer.forward` computes `self.mamba(X) + X` but returns `X` (`genemamba/models/models.py:389-406`), and pretraining initializes NCCL via `env://` at import time (`pretrain/train.py:30-44`). Overall code-paper fidelity is **medium**, and end-to-end reproduction is not established.

### Limitations

The paper itself notes difficulty with rare cell types and subtle low-expression signals and substantial pretraining resource requirements (`paper.md:337-342`). The code adds practical constraints: external datasets and checkpoints are required, topology analyses are notebook-only, and the exact contrastive denominator differs from the paper's per-anchor notation (`genemamba/utils/utils.py:278-346`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
