---
layout: default
permalink: /paper-atlas/protrans-ab025f3d/
title: "ProTrans"
nav: false
description: "scProTrans 的本质是：用基因/蛋白/peak 的序列 embedding 提供跨数据集可迁移的生物先验，用 cell embedding 表示每个细胞状态，再用 cross-attention 学习“当前细胞中哪些输入分子信息对目标分子预测有用”。核心模型和主要 translation 模式在代码中能够找到；论文中若干下游分析和作图步骤没有在发布代码快照中找到，应在复现时单独标记为缺失或需要作者补充。"
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
      <span>Genome Biology · 2026</span>
    </div>
    <h1>ProTrans</h1>
    <p>A sequence knowledge-guided deep learning method for single-cell multi-omics translation</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-026-04070-6" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scProTrans 方法中文解读

### 1. 论文要解决什么问题

单细胞 RNA 测序数据已经非常丰富，但单细胞蛋白组测量仍然昂贵、覆盖有限，并且很多蛋白难以通过抗体或多组学实验直接捕获。论文的目标是：利用已有的配对 CITE-seq 等多组学数据，学习从转录组到蛋白组的映射，从而在只有 scRNA-seq 或 ATAC 数据时预测蛋白表达 (`paper source/springer_html/paper.md:48-57`)。

现有方法的主要限制是：很多模型依赖配对训练数据，只能预测训练集中已经测到的蛋白；对于没有出现在训练 panel 中的蛋白，通常缺少预测能力。论文把这个问题称为需要更强的跨组学翻译和 zero-shot translation 能力 (`paper source/springer_html/paper.md:54-57`, `paper source/springer_html/paper.md:161-164`)。

### 2. scProTrans 的核心想法

scProTrans 的关键不是只从表达矩阵学习映射，而是把三类信息合在一起：

- **基因序列知识**：从 NCBI 基因序列出发，用 dna2vec 得到 gene embedding。
- **蛋白序列知识**：从 UniProt 蛋白序列出发，用 ProtT5 得到 protein embedding。
- **细胞状态信息**：从单细胞表达矩阵出发，用 scVI 得到 cell embedding。

然后，模型把“蛋白 + 细胞”作为 Query，把“基因 + 细胞”作为 Key，把标准化 RNA 表达作为 Value，用多头 cross-attention 预测蛋白表达 (`paper source/springer_html/paper.md:69-80`, `paper source/springer_html/paper.md:281-337`)。

直观地说，一个细胞里的每个目标蛋白都会带着自己的蛋白序列表示和该细胞的状态去“询问”哪些基因表达更相关。注意力矩阵因此可以被解释为某个细胞状态下的基因-蛋白关联强度。

### 3. 计算流程

```text
RNA counts
  -> filter genes / normalize total / log1p / highly variable genes
  -> normalized RNA X ----------------------+
                                            |
                                            v
                                     Value V for attention

RNA profile -> scVI -> cell embedding C ----+
                                            |
Gene sequence -> dna2vec -> gene embedding G
Protein sequence -> ProtT5 -> protein embedding P

concat(G, C) -> Key K
concat(P, C) -> Query Q
Q, K, V -> multi-head cross-attention
       -> two-layer predictor
       -> predicted protein profile Y_hat
Y_hat vs normalized protein Y -> MSE loss
```

#### 3.1 Gene encoder

论文描述从 NCBI 收集人类基因序列，裁剪到 10,000 bp，再分成 100 bp 片段，用 k=8 的 dna2vec k-mer 表示生成 gene embedding，并缓存以避免重复计算 (`paper source/springer_html/paper.md:260-264`)。代码中，`encode_gene` 从预计算的 `dna2vec_1w.npz` 中筛出当前表达矩阵包含的基因 embedding，并保存到 `gene_embedding.npz` (`ProTrans/code/encode.py:14-38`)。

#### 3.2 Protein encoder

论文描述用 UniProt 的人类蛋白序列和 ProtT5 生成 1024 维 protein embedding (`paper source/springer_html/paper.md:266-269`)。代码中，`encode_protein` 先清理抗原名，再通过 antigen-UniProt 映射找到 ProtT5 HDF5 中的 embedding (`ProTrans/code/encode.py:42-79`)。

#### 3.3 Cell encoder

论文使用 scVI 生成 100 维 cell embedding，目标是降噪和处理批次效应 (`paper source/springer_html/paper.md:272-278`)。代码里 `encode_cell_all` 构建 AnnData，训练 `scvi.model.SCVI(adata, n_latent = 100)`，并保存 latent representation 和 normalized expression (`ProTrans/code/ProTrans.py:22-44`)。

#### 3.4 Cross-omics translation module

论文定义：

- `G in R^{n_g x d_g}`：基因 embedding；
- `P in R^{n_p x d_p}`：蛋白 embedding；
- `C in R^{n_c x d_c}`：细胞 embedding；
- `X in R^{n_c x n_g}`：标准化 RNA 表达。

模型先把 `G`、`P` 复制到每个细胞，再与该细胞的 embedding 拼接，得到 `M^{gc}` 和 `M^{pc}`。其中 `M^{gc}` 是 Key，`M^{pc}` 是 Query，`X` 是 Value (`paper source/springer_html/paper.md:287-319`)。

注意力计算是标准 scaled dot-product attention：

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d)) V
```

代码实现位于 `ProTrans/code/ProTrans.py:46-126`。其中 `query_linear` 和 `key_linear` 把输入映射到 500 维，再切成 10 个 head；`protein_rna_attention` 计算 `torch.bmm(query, key.transpose(1, 2))`、缩放、softmax、再乘以 value (`ProTrans/code/ProTrans.py:56-82`, `ProTrans/code/ProTrans.py:121-126`)。

### 4. 损失函数和训练

论文把标准化蛋白表达 `Y` 和预测值 `Y_hat` 做均方误差损失，并说明默认训练 200 epochs，若 50 个 epoch 没有改进则 early stopping (`paper source/springer_html/paper.md:340-351`)。代码中使用 Adam 和 `nn.MSELoss()`，保存最优模型 `best_model.pth`，并用 `patience` 控制 early stopping (`ProTrans/code/ProTrans.py:130-166`, `ProTrans/code/ProTrans.py:330-371`)。

需要注意一个实现差异：论文写 batch size 为 32，而当前代码默认 `--batch_size 48`；论文方法部分写主 RNA profile 选 top 5000 highly variable genes，但主脚本从 raw data 预处理时使用 3000 (`paper source/springer_html/paper.md:275-278`, `paper source/springer_html/paper.md:503-503`; `ProTrans/code/ProTrans.py:130-143`, `ProTrans/code/ProTrans.py:187-191`)。

### 5. Zero-shot translation 是什么

Zero-shot 的目标是预测训练集中没有测到的蛋白。论文的解释是：蛋白 encoder 对所有目标蛋白都可以生成序列 embedding，因此模型训练时学到的是“基因序列、蛋白序列、细胞状态、表达模式”之间的关系；推理时可以把未见过蛋白的 embedding 放进 Query，预测它的表达 (`paper source/springer_html/paper.md:404-429`)。

代码中，`mode == 'zeroshot'` 时随机把 40% 的蛋白作为测试蛋白，剩下 60% 用于训练；测试时把 held-out protein embedding 作为 query，调用 `forward_zero_shot` 生成预测，并输出 `prediction.csv`、`truthvalue.csv`、`evaluate.csv` (`ProTrans/code/ProTrans.py:235-251`, `ProTrans/code/ProTrans.py:310-321`, `ProTrans/code/ProTrans.py:378-426`)。

这里要区分两层证据：

- **代码支持**：通用的随机蛋白 holdout zero-shot 机制。
- **论文图示支持**：CD324/CD325 最近邻、序列比对、embedding 相似度、训练蛋白比例 sweep 等图示分析在本代码快照中没有找到对应脚本 (`paper source/springer_html/images/figure_05.png`)。

### 6. Gene-protein association 如何解释

论文把 attention matrix 当作单细胞层面的 gene-protein association。不同 cell 有不同 cell embedding，所以 Query 和 Key 都含有细胞状态；把不同 head 的 attention matrix 求和，可以得到 cell-specific gene-protein association matrix；再对同一 cell type 的细胞求和，可得到 cell-type-specific matrix (`paper source/springer_html/paper.md:387-390`)。

代码支持到第一部分：模型返回 headwise attention 和 `attn_sum`，在测试阶段如果设置 `--attention`，会把 batch 中的 `attn_sum` 累加并保存为 numpy 文件 (`ProTrans/code/ProTrans.py:70-82`, `ProTrans/code/ProTrans.py:432-463`)。

但代码没有找到以下下游分析：

- 按 cell type 聚合 attention；
- 用 CellMarker2.0 作为 gold standard；
- 用 fold change 和 attention score 联合计算 marker-gene precision；
- 生成 Fig. 4C-D 的 precision bar chart。

因此，注意力导出是代码验证的；marker precision 结果是论文和图像支持的，但不是本代码快照中可复现的步骤 (`paper source/springer_html/paper.md:393-401`, `paper source/springer_html/images/figure_04.png`)。

### 7. 扩展到 ATAC 和多组学

论文把 scProTrans 扩展到 epigenome：用 peak encoder 代替 gene/protein 的一部分输入，ATAC profile 经 TF-IDF 变换后作为 Value。TF-IDF 公式是 Eq. 15，用于校正测序深度并提高稀有 peak 的权重 (`paper source/springer_html/paper.md:432-446`)。

代码中有两个扩展脚本：

- `ProTrans-ATAC-RNA.py`：ATAC-to-RNA，Query 是 gene embedding + cell embedding，Key 是 peak embedding + cell embedding，Value 是 normalized ATAC (`ProTrans/code/ProTrans-ATAC-RNA.py:49-390`)。
- `ProTrans-ATAC-ADT.py`：ATAC-to-protein，Query 是 protein embedding + cell embedding，Key 是 peak embedding + cell embedding，Value 是 normalized ATAC (`ProTrans/code/ProTrans-ATAC-ADT.py:49-384`)。

ATAC 相关 notebooks 支持 peak preprocessing：`gen_atac.ipynb` 从 h5 提取 peak count，`atac2seq.ipynb` 根据 peak interval 提取基因组序列，`seq2emb.ipynb` 用 dna2vec 生成 peak embedding。

### 8. 评价结果怎么理解

论文在多个层面评价 scProTrans：常规 RNA-to-protein translation、跨 cell type、跨 batch、跨 sequencing technology、zero-shot protein prediction、下游 clustering/subtype、扰动响应、ATAC/空间组学扩展。Fig. 2 的本地图像显示 scProTrans 在 MSE/MAE/correlation 和 rank table 中表现较强，论文报告 96 个模拟实验中平均 MAE 为 0.88、平均 correlation 为 91.4% (`paper source/springer_html/paper.md:86-124`, `paper source/springer_html/images/figure_02.png`)。

但从复现角度看，发布代码更像“核心方法实现 + 若干主要模式脚本”，不是完整论文复现包。缺失的部分包括：

- 全部数据集和所有 baseline 的 benchmark orchestrator；
- Fig. 3 clustering/subtype 分析脚本；
- Fig. 4 marker precision 脚本；
- Fig. 5 CD324/CD325 case study 和 ratio sweep；
- Fig. 6 perturbation response 的 EdgeR/GO/pathway 分析；
- Fig. 7 spatial proteomics 的脚本。

### 9. 一句话总结

scProTrans 的本质是：用基因/蛋白/peak 的序列 embedding 提供跨数据集可迁移的生物先验，用 cell embedding 表示每个细胞状态，再用 cross-attention 学习“当前细胞中哪些输入分子信息对目标分子预测有用”。核心模型和主要 translation 模式在代码中能够找到；论文中若干下游分析和作图步骤没有在发布代码快照中找到，应在复现时单独标记为缺失或需要作者补充。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## ProTrans Summary

### Problem

scRNA-seq data are widely available, but protein profiling at single-cell scale remains comparatively costly and limited. The paper argues that CITE-seq and other paired multi-omics datasets can be used as references for translating transcriptome profiles into proteome profiles, but existing methods often depend heavily on paired training data and usually cannot predict proteins absent from the training panel (`paper source/springer_html/paper.md:48-57`, `paper source/springer_html/paper.md:161-164`).

### Proposed Method

The paper introduces **scProTrans**, released as the `ProTrans` code repository, as a sequence knowledge-guided deep learning framework for cross-omics translation. The method combines gene sequence embeddings, protein sequence embeddings, and cell embeddings in a multi-head cross-attention model. For each cell, gene-cell embeddings serve as keys, protein-cell embeddings serve as queries, and normalized transcriptome values serve as values; the attention output is mapped into predicted protein abundance (`paper source/springer_html/paper.md:63-80`, `paper source/springer_html/paper.md:281-337`).

The design gives scProTrans two distinctive capabilities. First, attention matrices can be interpreted as gene-protein association scores at cell or cell-type level (`paper source/springer_html/paper.md:387-390`). Second, because target proteins are represented by sequence-derived embeddings, the same model can predict held-out or unavailable proteins in a zero-shot setting (`paper source/springer_html/paper.md:404-429`).

### Evaluation

The paper evaluates scProTrans on paired single-cell transcriptome-proteome datasets, cross-cell-type splits, cross-batch splits, cross-technology transfer, downstream clustering/subtype discovery, perturbation response, zero-shot protein prediction, and ATAC/spatial extensions. In the main benchmark, it compares against moETM, scVAEIT, totalVI, sciPENN, Seurat, and scButterfly, and reports strong performance across 96 simulated experiments with a mean MAE of 0.88 and mean correlation of 91.4% (`paper source/springer_html/paper.md:86-124`). The local Fig. 2 image visually supports this result through boxplots, diagonal comparison scatterplots, and a rank table (`paper source/springer_html/images/figure_02.png`).

The result figures support a broader biological narrative: predicted protein profiles improve clustering and subtype discovery (Fig. 3), attention highlights marker-associated gene/protein structure (Fig. 4), held-out proteins can be reconstructed in zero-shot examples (Fig. 5), translated proteomes support perturbation-response analysis (Fig. 6), and the attention core can be adapted to epigenome-to-proteome/RNA and spatial scenarios (Fig. 7) (`paper source/springer_html/images/figure_03.png`, `figure_04.png`, `figure_05.png`, `figure_06.png`, `figure_07.png`).

### Code and Reproducibility

The released GitHub snapshot is useful but incomplete relative to the full paper analysis. It contains a main RNA-to-protein script, sequence embedding lookup helpers, a cross-technology script, ATAC-to-RNA and ATAC-to-protein scripts, and ATAC preprocessing notebooks. Core code-paper fidelity is **medium**: the principal architecture, loss, zero-shot holdout, evaluation metrics, cross-technology transfer, and ATAC extensions are implemented (`ProTrans/code/ProTrans.py:22-483`, `ProTrans/code/encode.py:14-79`, `ProTrans/code/ProTrans-technology.py:47-295`, `ProTrans/code/ProTrans-ATAC-RNA.py:49-390`, `ProTrans/code/ProTrans-ATAC-ADT.py:49-384`).

Important gaps remain. The repository does not include the CellMarker2.0 marker-gene precision implementation, cell-type attention aggregation, full benchmark orchestration, clustering/subtype plotting, perturbation-response EdgeR/enrichment scripts, train-protein-ratio zero-shot sweeps, or spatial proteomics scripts. The code also differs from Methods text in some defaults: the paper states batch size 32 and top 5000 highly variable genes, while the main script defaults to batch size 48 and selects 3000 highly variable genes in the raw preprocessing path (`paper source/springer_html/paper.md:275-278`, `paper source/springer_html/paper.md:503-503`; `ProTrans/code/ProTrans.py:130-143`, `ProTrans/code/ProTrans.py:187-191`).

### Bottom Line

scProTrans is a sequence-aware attention model for translating single-cell RNA or ATAC profiles into protein or RNA profiles. The core released code supports the central computational idea and several major experimental modes, but the repository should be treated as a method implementation plus example workflows rather than a complete reproduction package for every figure in the paper.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
