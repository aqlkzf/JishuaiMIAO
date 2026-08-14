---
layout: default
permalink: /paper-atlas/largescalecellniches-f8eb4f6c/
title: "LargeScaleCellNiches"
nav: false
wide: true
description: "空间组学可以告诉我们哪些细胞彼此相邻，但传统方法通常只按形态或表达相似性聚类，无法定量说明“哪些细胞互作或调控过程塑造了这个 niche”。NicheCompass 的目标是把 niche 定义为一组共享的空间基因程序（gene programs, GPs）活动模式：这些程序可以代表配体-受体、代谢物-传感器、转录调控，或串联的组合互作。 输入可以是单模态 RNA 空间数据，也可以是 RNA 加染色质可及性（ATAC）的多模态数据。"
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
      <span>Cell-Cell Communication</span>
      <span>bioRxiv · 2024</span>
    </div>
    <h1>LargeScaleCellNiches</h1>
    <p>Quantitative characterization of cell niches in spatial atlases</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Lotfollahi-lab/nichecompass-reproducibility" target="_blank" rel="noopener noreferrer" aria-label="Open code for LargeScaleCellNiches">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## NicheCompass 方法详解

### 1. 要解决的问题

空间组学可以告诉我们哪些细胞彼此相邻，但传统方法通常只按形态或表达相似性聚类，无法定量说明“哪些细胞互作或调控过程塑造了这个 niche”。NicheCompass 的目标是把 niche 定义为一组共享的空间基因程序（gene programs, GPs）活动模式：这些程序可以代表配体-受体、代谢物-传感器、转录调控，或串联的组合互作（论文 `paper.md:18-27,33-53`）。

### 2. 输入与输出

输入可以是单模态 RNA 空间数据，也可以是 RNA 加染色质可及性（ATAC）的多模态数据。每个观测（cell 或 spot）包含：

- 原始 omics 计数；
- 二维空间坐标；
- sample、field of view、donor 等分类协变量；
- 可选的细胞类型或区域标签。

输出包括每个细胞/spot 的 GP 对齐潜变量、空间邻居图和 UMAP、niche 聚类、每个 GP 的空间活动，以及可用于细胞-细胞通信解释的基因和细胞对分数。

### 3. 核心思想

```text
空间 omics + 坐标 + 协变量
          |
          v
每个样本内部的对称 kNN 空间图
          |
          +--> 细胞自身特征 X
          +--> 邻域聚合特征 X'
          +--> 先验/ de novo GP 掩码
          |
          v
图神经网络编码器 + 协变量嵌入
          |
          v
GP 可解释的变分潜空间 Z
          |
          +--> 重建空间邻接矩阵 A
          +--> 重建自身 RNA/ATAC
          +--> 预测邻域 RNA/ATAC
          |
          v
联合损失训练、GP 筛选和正则化
          |
          v
niche 聚类、GP 解释、参考图谱映射和基准评估
```

#### 3.1 空间图和邻域标签

论文把细胞/spot 作为图节点，把空间近邻作为边。实验中使用每个样本独立的对称 kNN 子图，再组成一个断开的大图；这样不同切片不需要先做坐标配准。节点标签把自身表达和包含自环的邻域聚合表达拼接起来，分别表达自分泌/细胞内信号以及邻居的旁分泌、接触信号（`paper.md:412-430`）。

代码中，鼠脑 atlas 流程用 Squidpy 计算每个 batch 的 4-neighbor 图，并用稀疏矩阵 `A.maximum(A.T)` 强制对称，再用零填充块矩阵阻止跨样本边（`05_compute_neighbourhood.py:23-81`）。

#### 3.2 基因程序（GP）

先验 GP 用 self-component 和 neighborhood-component 两套二值掩码表示。配体通常位于 neighborhood，受体和下游靶基因位于 self；转录调控 GP 的 TF 和靶基因位于 self；组合 GP 将配体-受体与下游调控连接起来。多模态数据还可以根据基因体或启动子附近位置把 ATAC peaks 关联到相应 GP（`paper.md:433-445`）。论文的默认 GP 来自 OmniPath、MEBO-COST、CollecTRI 和 NicheNet V2，并在大量重叠时过滤/合并。

本地复现仓库直接实现了 OmniPath、MEBO-COST 和 NicheNet 的 GP 读取、NicheNet 每个 GP 最多 250 个靶基因，以及 0.9 重叠阈值过滤（`04_construct_gene_programs.py:11-75`）。随后把 source/target/category 掩码写入 AnnData（`06_package_gene_programs.py:9-33`）。

#### 3.3 编码器、解码器和损失

论文描述的编码器先将 omics 向量映射到 GP 数量对应的隐藏维度，再用动态注意力图层生成变分后验的均值和标准差；低内存的 NicheCompass Light 使用图卷积层。解码器包括：

1. 用潜变量相似度重建邻接矩阵；
2. 用 GP 掩码的线性解码器重建细胞自身 RNA/ATAC；
3. 用另一套掩码解码器预测邻域聚合 RNA/ATAC。

训练损失由边重建二元交叉熵、自身与邻域的负二项损失、KL 散度以及选择性/de novo L1 正则化组成；邻居采样把每个节点的消息传递限制为 4 个采样邻居，以降低大图内存需求（`paper.md:466-571`）。

重要的证据边界是：当前代码仓库只调用外部 `nichecompass` 包中的 `NicheCompass(...)` 和 `.train(...)`，没有包含编码器、解码器、损失或 GP pruning 的实现。因此上述结构是论文主张；本地可以验证的是参数如何传入，而不是这些内部张量运算。

#### 3.4 GP 筛选和参考映射

论文提出 warm-up 之后根据 GP 的解码器权重和潜变量活动估计其贡献，低于阈值的 GP 会被永久关闭；先验和 de novo GP 分开筛选。选择性 L1 正则化还可以偏向靶基因等指定类别（`paper.md:511-527`）。代码暴露 `active_gp_thresh_ratio`、`n_epochs_all_gps` 和 L1 权重，但筛选公式实现仍在外部包中。

参考图谱映射采用受限微调：加载参考模型后冻结全部网络权重，只解冻分类协变量嵌入，在 query 数据上训练；最后把 reference/query AnnData 作为断开的图组件拼接（`map_query_on_nichecompass_reference_model.py:393-460`）。这样可以去除 query 的技术差异，同时保留新的生物学 variation。

### 4. 代码复现流程

本地仓库的可验证流程是：

1. 预处理各个空间数据集；
2. 读取并过滤 GP，生成 source/target 掩码；
3. 构建每个样本的对称空间图并合并为断开图；
4. 初始化外部 `NicheCompass` 模型并传入 covariate、GP、latent 和损失参数；
5. 训练后用 Scanpy 计算 latent neighbor graph 和 UMAP；
6. 在 benchmark 中保存多个 latent run，调用外部 metrics 工具并写出 CSV；
7. 在 reference mapping 中仅微调 covariate embedder。

鼠脑 atlas 示例使用 GCN、400 epochs、25 个 all-GP epochs、学习率 0.001、edge reconstruction 权重 500000、gene-expression reconstruction 权重 300，以及 4 个采样邻居（`mouse_brain_atlas/07_train_model.py:9-123`）。

### 5. 论文中的主要结果

论文在胚胎发育、鼠海马、乳腺癌、NSCLC、鼠脑多模态数据以及百万级全脑 atlas 上评估 NicheCompass。报告的结论包括：

- 胚胎数据中识别出 Forebrain、Midbrain、Hindbrain、Floor Plate 等细粒度 niche，并得到与解剖结构一致的层级；
- SlideSeqV2 基准中整体表现优于 GraphST、CellCharter、STACI、DeepLinc 等比较方法；
- CosMx NSCLC 中通过 sample/field-of-view 协变量改善批次整合，并识别肿瘤-基质边界等结构；
- 乳腺癌中 de novo GP 可以对应 basal/luminal 角蛋白表达；
- reference mapping 发现与 SPP1+ 浸润巨噬细胞相关的 query 肿瘤 niche；
- RNA+ATAC 比单独 RNA 能更好分离鼠脑的 Major Island of Calleja、Corpus Callosum 和 Anterior Commissure 等结构；
- 全脑 atlas 展示了百万级细胞规模的可扩展性。

### 6. 复现限制

当前证据等级为中等（3/5）：分析仓库、环境文件、参数和数据链接比较完整，但核心 `nichecompass` 包不在快照中；完整 `.h5ad` 数据、训练模型和 GPU 运行环境未下载或执行；HTML 转 Markdown 丢失了多个显示公式；没有 supplementary Markdown、article XML，以及 Fig. 5/Fig. 6 等后续主图的本地图像。上述缺口在 `doc_code.md`、`doc_method.md` 和 `figure_analysis.md` 中保留为 `MISSING`/`Not found`，没有用推测补齐。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Quantitative Characterization of Cell Niches in Spatial Atlases

### Problem

Spatial omics can reveal communities of neighboring cells, but many existing approaches define niches from morphology or expression similarity without quantifying the cellular interaction events that create them. NicheCompass addresses this by learning spatial representations whose dimensions correspond to interpretable interaction and regulatory gene programs (GPs), while integrating samples, supporting multimodal data, and scaling to large atlases (`paper.md:18-27,33-53`).

### Proposed Method

NicheCompass is a conditional graph variational autoencoder for spatial omics. It builds sample-specific spatial neighbor graphs, encodes self and neighborhood omics features with a graph neural network, embeds categorical covariates for batch-effect control, and decodes graph adjacency plus self/neighborhood RNA and ATAC counts. Binary GP masks constrain decoder connectivity so latent dimensions can be interpreted as prior or de novo GP activity. Neighbor sampling and sparse graph processing are used to reduce memory use (`paper.md:403-577`).

The reproducibility repository directly implements the surrounding workflow: it assembles OmniPath, MEBO-COST, and NicheNet programs; constructs symmetric disconnected graphs; packages GP masks in AnnData; invokes the external `NicheCompass` package; exports latent graphs/UMAPs; computes benchmark metrics; and performs covariate-only query fine-tuning. The core model package itself is a separate dependency (`doc_code.md`).

### Evaluation and Main Results

The paper evaluates seqFISH mouse organogenesis, SlideSeqV2 mouse hippocampus, CosMx human NSCLC, Xenium human breast cancer, Spatial ATAC-RNA-seq mouse brain, and a whole mouse-brain atlas. Metrics cover spatial conservation (CAS, CLISIS, GCS), niche coherence (NASW, CNMI), batch correction (BLISI, PCR), and a category-balanced overall score (`paper.md:123-156,580-634`).

Reported results include: biologically coherent embryo niches and a GP-supported tissue hierarchy; first-place benchmark performance on the full SlideSeqV2 task; stronger CosMx NSCLC integration and niche resolution than the compared methods; de novo programs separating basal and luminal breast-cancer niches; reference mapping that retains donor/query variation and identifies an SPP1 macrophage-associated tumor niche; multimodal ATAC/RNA resolution of brain niches that RNA alone misses; and an atlas workflow reaching millions of cells (`paper.md:56-120,123-156,161-207,208-300,301-321`). These are paper claims; no benchmark or training run was executed here.

### Reproducibility

**Rating: 3/5 (medium).** The acquired code snapshot is a useful, pinned analysis layer with explicit scripts, environments, parameter recipes, and external data/model links. Direct source evidence verifies graph construction, GP preparation, model invocation, query fine-tuning, and metric aggregation. Reproduction is incomplete without the separately maintained `nichecompass` package, downloaded preprocessed `.h5ad` data and trained models, and the computational environment. The converted Markdown omits displayed equation bodies; supplementary Markdown/XML and later main-figure image files are unavailable; notebooks and training were not run. These gaps are labeled `MISSING`/`Not found` in the detailed documents rather than filled by inference.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
