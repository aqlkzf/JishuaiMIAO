---
layout: default
permalink: /paper-atlas/sctel-93f2bd9b/
title: "scTEL"
nav: false
description: "scTEL 面向 CITE-seq 和 scRNA-seq 的联合分析。CITE-seq 可以在同一个细胞内同时测 RNA 和表面蛋白，但论文指出它成本高、抗体面板有限，而且 RNA 与蛋白表达之间常常不是简单强相关关系，因此只靠 RNA 或只靠已有蛋白面板都不够 。 论文的核心目标是：用已有 CITE-seq 数据学习从 RNA 表达到蛋白表达的映射，这样在只有 scRNA-seq 或蛋白面板不完整的场景中，也能预测或补全蛋白表达 。"
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
      <span>npj Systems Biology and Applications · 2025</span>
    </div>
    <h1>scTEL</h1>
    <p>A joint analysis of single cell transcriptomics and proteomics using transformer</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41540-024-00484-9" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scTEL 方法解释

### 这篇论文要解决什么问题

scTEL 面向 CITE-seq 和 scRNA-seq 的联合分析。CITE-seq 可以在同一个细胞内同时测 RNA 和表面蛋白，但论文指出它成本高、抗体面板有限，而且 RNA 与蛋白表达之间常常不是简单强相关关系，因此只靠 RNA 或只靠已有蛋白面板都不够 (`paper source/nature_html/paper.md:21-30`)。

论文的核心目标是：用已有 CITE-seq 数据学习从 RNA 表达到蛋白表达的映射，这样在只有 scRNA-seq 或蛋白面板不完整的场景中，也能预测或补全蛋白表达 (`paper source/nature_html/paper.md:12-12`, `paper source/nature_html/paper.md:83-86`)。

### 方法输入和输出

**论文设定。** 输入是多个已归一化的 CITE-seq 数据集。不同数据集可能有不同基因集合和不同蛋白面板。scTEL 先取所有数据集的共同基因集合 \(G_{com}\)，再从中选取 1000 个高变基因作为输入特征；蛋白输出空间则取所有数据集蛋白集合的并集 \(P_{ref}\) (`paper source/nature_html/paper.md:89-104`)。

**代码验证。** 代码中训练基因矩阵通过 `concatenate(... join='inner')` 做共同基因合并，测试集也与训练集取交集；HVG 选择使用 `highly_variable_genes(... n_top_genes=1000)` (`scTEL_repo/scTEL/Preprocessing.py:120-160`)。蛋白矩阵用 `join='outer', fill_value=0.` 合并，并生成数据集-蛋白可用性布尔矩阵，供后续 masked loss 使用 (`scTEL_repo/scTEL/Preprocessing.py:205-220`)。

模型输出有三类：蛋白表达预测/补全、细胞类型预测、用于数据整合和 UMAP 等下游分析的 embedding (`paper source/nature_html/paper.md:107-113`)。代码 API 对应暴露 `impute()`, `predict()`, `embed()` (`scTEL_repo/scTEL/scTEL_API.py:97-121`)。

### 整体流程

```text
多个 CITE-seq 数据集
  -> RNA / protein 归一化
  -> 共同基因交集 + 1000 HVGs
  -> 蛋白面板并集 + 缺失蛋白 mask
  -> embedding layer
  -> TE layer + LSTM cell 堆叠
  -> 蛋白预测 / 分位数预测 / 细胞类型预测 / embedding
```

图 1 也以这个流程组织：先合并 UMI 归一化后的 RNA 矩阵并筛选 HVG，再输入 scTEL，最后完成蛋白预测、细胞类型识别和数据整合 (`paper source/nature_html/images/figure_01.png`, `paper source/nature_html/paper.md:48-53`)。

### 预处理在做什么

论文描述的预处理包括 UMI 归一化、log 转换和 z-score 标准化，目标是降低测序深度和技术噪声带来的影响 (`paper source/nature_html/paper.md:59-77`)。

代码中对应使用 Scanpy 的 `normalize_total` 和 `log1p`，之后按 batch 对训练/测试 RNA 以及训练蛋白数据做 `scale` (`scTEL_repo/scTEL/Preprocessing.py:100-118`, `scTEL_repo/scTEL/Preprocessing.py:167-203`)。这里和论文是 **Partial** 匹配：操作类型一致，但论文里的 median-scaling 公式没有在代码中手写实现，而是依赖 Scanpy 默认行为。

### TE layer 和 LSTM cell 为什么组合在一起

**论文主张。** TE layer 用 Transformer attention 从基因表达矩阵中提取特征，捕获基因之间的相互关系；LSTM cell 接收 TE layer 产生的中间表示 \(Z_t\)，通过 cell state 和 hidden state 在多个阶段传递信息 (`paper source/nature_html/paper.md:113-154`)。

**图像证据。** 图 2a 展示 TE layer 中的全连接、multi-head attention、Add&Norm 等模块；图 2b 展示 LSTM 的 input/forget/output gate 和 cell state 流程 (`paper source/nature_html/images/figure_02.png`, `paper source/nature_html/paper.md:116-121`)。

**代码验证。** `TE_Layer.py` 中 `Input_TE` 和 `FF_TE` 使用 PyTorch `TransformerEncoderLayer`，并接线全连接、BatchNorm、PReLU、Dropout 等模块 (`scTEL_repo/scTEL/Network/TE_Layer.py:29-90`)。`scTEL_Model` 中有三个 TE 阶段和三个 `LSTMCell`，`forward_transfer` 返回细胞类型概率、蛋白输出和 embedding (`scTEL_repo/scTEL/Network/scTEL.py:19-67`)。

### 多任务损失如何实现

论文把训练目标写成：

\[
L_{total}=L_{MSE}+L_{quantile}+L_{CE}
\]

其中 MSE 用于蛋白表达回归，quantile loss 用于预测区间/不确定性，CE 用于细胞类型分类 (`paper source/nature_html/paper.md:157-193`)。由于不同 CITE-seq 数据集的蛋白面板不完全重叠，真实目标矩阵里的空缺蛋白不应该参与蛋白 loss (`paper source/nature_html/paper.md:163-169`)。

代码中 `sse_quantile` 把 squared error 和 quantile loss 合在一个蛋白 loss 内，再乘以蛋白可用性 mask；细胞类型则用手写 cross entropy (`scTEL_repo/scTEL/Network/Losses.py:13-76`)。训练循环中总 loss 是 `mod1_loss + mod2_loss`，其中 `mod1_loss` 是分类项，`mod2_loss` 是 masked protein loss (`scTEL_repo/scTEL/Network/scTEL.py:95-155`)。

### impute、predict、embed 的区别

代码里三个推理入口含义不同：

- `impute()`：对训练/参考 CITE-seq 数据中未测到的蛋白位置补预测值，已有蛋白值保留；实现上用 `(1 - bools) * predicted + array` 只填缺失位置 (`scTEL_repo/scTEL/Network/scTEL.py:157-186`, `scTEL_repo/scTEL/Network/scTEL.py:218-220`)。
- `predict()`：对测试 scRNA-seq 细胞输出完整参考蛋白矩阵；如果训练时有细胞类型类别，还会输出预测标签 (`scTEL_repo/scTEL/Network/scTEL.py:222-263`)。
- `embed()`：导出 512 维 embedding，供整合和可视化使用 (`scTEL_repo/scTEL/Network/scTEL.py:188-216`)。

### 论文结果怎么读

论文在 PBMC、MALT、H1N1 和 Monocytes 四个公开数据集上评估 scTEL，并与 Seurat、totalVI、sciPENN 等方法比较 (`paper source/nature_html/paper.md:42-45`, `paper source/nature_html/paper.md:205-205`)。

**数据整合。** 图 3 的 UMAP 显示 scTEL 在 PBMC-H1N1 和 PBMC-MALT 场景中有更好的批次混合，同时保留细胞类型结构；论文也报告 scTEL 在各场景中有最高 silhouette score (`paper source/nature_html/images/figure_03.png`, `paper source/nature_html/paper.md:217-240`)。

**蛋白预测。** 图 4 用 RMSE 比较蛋白预测误差，图 5 用 Pearson correlation 和预测区间 coverage 比较预测质量；论文称 scTEL 在三个场景中平均 RMSE 最低、平均相关性最高，并且 coverage 优于 sciPENN 和 totalVI (`paper source/nature_html/paper.md:249-286`, `paper source/nature_html/images/figure_04.png`, `paper source/nature_html/images/figure_05.png`)。

**细胞类型识别。** 图 6 报告 PBMC 57 类分类结果：scTEL accuracy 0.866、F1 0.896、ARI 0.909，高于 sciPENN 和 Seurat (`paper source/nature_html/images/figure_06.png`, `paper source/nature_html/paper.md:292-309`)。

### 代码复现边界

代码仓库确实实现了 scTEL 的核心模型、预处理、masked protein loss、quantile 输出、细胞类型头、embedding/impute/predict API (`scTEL_repo/scTEL/scTEL_API.py:16-121`, `scTEL_repo/scTEL/Network/scTEL.py:19-263`)。

但复现边界需要明确：

- 仓库 README 要求用户下载数据并手动逐个运行 notebooks，没有提供一个覆盖所有论文图表和指标的统一 benchmark/evaluation runner (`scTEL_repo/README.md:23-56`)。
- 论文把训练过程和模型参数的更多细节指向 Supplementary Information，但当前 workspace 没有 `SUPP_MD`，因此补充材料中的细节无法在本地用 markdown 行号验证 (`paper source/nature_html/paper.md:199-199`)。
- 因此，核心方法实现是可验证的；完整论文结果的一键复现链条在当前源码中是 **Not found**。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Paper

**A joint analysis of single cell transcriptomics and proteomics using transformer** introduces **scTEL**, a deep-learning framework for CITE-seq/scRNA-seq analysis. The paper appeared in *npj Systems Biology and Applications* in 2025 with DOI `10.1038/s41540-024-00484-9` (`paper source/nature_html/paper.md:1-6`, `paper source/nature_html/paper.md:466-476`).

### Problem

CITE-seq measures RNA and surface proteins in the same cells, but the paper argues that cost, antibody availability, antibody artifacts, and weak RNA-protein correlation limit direct proteomic measurement at scale (`paper source/nature_html/paper.md:21-30`). The proposed goal is to learn a mapping from RNA expression to protein expression so that protein abundance can be predicted or imputed from cheaper scRNA-seq-style inputs (`paper source/nature_html/paper.md:12-12`, `paper source/nature_html/paper.md:83-86`).

### Method

scTEL integrates multiple normalized CITE-seq datasets by intersecting common genes, selecting top highly variable genes, and taking the union of protein panels as reference proteins (`paper source/nature_html/paper.md:89-104`). It is presented as a multi-task model for protein prediction, cell-type identification, and data integration (`paper source/nature_html/paper.md:107-113`).

Architecturally, scTEL combines Transformer Encoder layers for gene-expression feature extraction with LSTM cells for sequential hidden/cell-state propagation (`paper source/nature_html/paper.md:113-154`). The objective combines masked protein MSE, quantile loss, and cell-type cross-entropy (`paper source/nature_html/paper.md:157-193`).

### Main Results

The paper evaluates PBMC, MALT, H1N1, and Monocytes datasets and compares scTEL with Seurat, totalVI, and sciPENN (`paper source/nature_html/paper.md:42-45`, `paper source/nature_html/paper.md:205-205`). Reported results include:

- **Data integration:** UMAP and silhouette analyses show stronger dataset mixing by scTEL, especially for PBMC-H1N1 and PBMC-MALT (`paper source/nature_html/paper.md:217-240`; `paper source/nature_html/images/figure_03.png`).
- **Protein prediction:** scTEL is reported to have the lowest average RMSE and highest average Pearson correlation across the three evaluated settings (`paper source/nature_html/paper.md:249-286`; `paper source/nature_html/images/figure_04.png`; `paper source/nature_html/images/figure_05.png`).
- **Uncertainty:** scTEL outputs quantile-based prediction intervals and is reported to maintain stronger coverage than sciPENN and totalVI; Seurat is excluded from this uncertainty comparison (`paper source/nature_html/paper.md:286-289`; `paper source/nature_html/images/figure_05.png`).
- **Cell typing:** For PBMC 57-category classification, the paper reports 86.6% scTEL accuracy versus 77.0% sciPENN and 76.1% Seurat, with higher F1 and ARI shown in Fig. 6 (`paper source/nature_html/paper.md:292-309`; `paper source/nature_html/images/figure_06.png`).

### Code Verification

The paper points to the GitHub repository `https://github.com/142857cyy/scTEL`, and the acquired code snapshot is from that source (`paper source/nature_html/paper.md:333-336`). Direct source inspection found the core method implemented:

- `scTEL_API` wires preprocessing, dataloaders, training, imputation, prediction, and embeddings (`scTEL_repo/scTEL/scTEL_API.py:16-121`).
- Preprocessing performs inner gene concatenation/intersection, HVG selection, batch-wise scaling, outer protein union, and dataset-by-protein masks (`scTEL_repo/scTEL/Preprocessing.py:120-160`, `scTEL_repo/scTEL/Preprocessing.py:167-220`).
- The model has three TE/LSTM stages, protein regression and quantile heads, an optional cell-type head, and exported embeddings (`scTEL_repo/scTEL/Network/scTEL.py:19-67`, `scTEL_repo/scTEL/Network/scTEL.py:157-263`).
- The protein loss masks unavailable protein entries and combines squared-error and quantile terms; cell labels use cross-entropy (`scTEL_repo/scTEL/Network/Losses.py:13-76`).

### Reproducibility Boundary

The released repository supports the main implementation and includes scenario notebooks, readers, baseline scripts, and plotting notebooks. However, the README instructs users to run notebooks manually and no single clear full benchmark/evaluation runner was found for regenerating all reported figures and metrics from raw data (`scTEL_repo/README.md:49-56`). No supplementary markdown exists in this workspace, so supplement-only model-parameter/training details referenced by the paper remain a local source gap (`paper source/nature_html/paper.md:199-199`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
