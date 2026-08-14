---
layout: default
permalink: /paper-atlas/scimilarity-6fb7bc4c/
title: "SCimilarity"
nav: false
wide: true
description: "SCimilarity 用重构保持表达细节，用 Cell Ontology 约束的 triplet learning 学习可迁移的细胞距离，再用近邻索引把这个距离扩展成数千万细胞的搜索、注释与解释系统；公开代码实现了核心算法，但完整 atlas、模型资产和论文实验仍属于外部复现边界。"
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
      <span>Nature · 2025</span>
    </div>
    <h1>SCimilarity</h1>
    <p>A cell atlas foundation model for scalable search of similar human cells</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Genentech/scimilarity" target="_blank" rel="noopener noreferrer" aria-label="Open code for SCimilarity">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SCimilarity 方法详解（基于论文与代码）

### 1. 这篇论文要解决什么问题？

单细胞图谱已经包含来自大量组织、疾病和实验条件的细胞，但传统流程通常只在一个数据集内做降维、整合或分类。这样很难回答一个更直接的问题：给定一个新细胞（或一组代表性细胞），在数千万个细胞中哪些细胞的完整表达状态最相似？论文提出 SCimilarity，把单细胞表达映射到一个可搜索、可解释的共同空间，并允许查询训练期间没有见过的新数据，而不需要为查询数据重新训练或微调模型。

论文指出，PCA 和自编码器可以保留输入信息，却不会主动学习“哪些细胞应该相似”；而专门的批次整合方法（例如 Harmony、Scanorama、scVI 和 scArches）主要优化数据集整合，通常需要把待整合数据放入拟合流程。SCimilarity 的目标是学习一个可以冻结、复用和索引的细胞状态距离。

### 2. 核心想法

SCimilarity 同时使用两种学习信号：

1. **监督式度量学习**：使用 Cell Ontology 标签构造 anchor-positive-negative 三元组，把同一细胞类型、但来自不同研究的细胞拉近，把明确不同的细胞推远；具有祖先-后代关系的标签被视为含糊比较，不用于负样本。
2. **无监督重构**：从低维表示重构输入表达，保留同一细胞类型内部的细微状态差异，避免纯 triplet loss 把连续状态过度压缩。

论文选择的模型使用 margin $\alpha=0.05$ 和 triplet 权重 $\beta=0.001$：

$$
L=(1-\beta)L_{\rm MSE}+\beta L_{\rm triplet}.
$$

因此，SCimilarity 不是一个只输出离散细胞标签的分类器，也不是只追求批次混合的整合器，而是一个可以继续用于检索、注释、异常检测和解释的细胞状态度量。

### 3. 从表达矩阵到搜索结果

```text
原始 UMI count 矩阵 + 基因名
        |
        +--> 质量控制、固定基因顺序、每细胞归一化到 10,000、log1p
        |
        v
全连接 Encoder f(x) --> 128 维、L2 归一化的细胞向量
        |                         |
        |                         +--> 参考索引的近邻搜索
        |                                      |
        |                                      +--> 相似细胞 + 研究/组织/疾病元数据
        |                                      +--> kNN 标签共识 --> 细胞类型预测
        |                                      +--> 距离 Integrated Gradients --> 重要基因
        v
Decoder g(f(x)) --> 重构表达 --> MSE

训练时：ontology-aware triplet loss + reconstruction loss --> 参数更新
```

#### 3.1 输入预处理

论文使用固定的 28,231 个基因空间，并将 UMI counts 按每个细胞归一化到 10,000 后执行自然对数 `log1p`（论文 Methods，lines 286-289）。代码中的 `scimilarity/src/scimilarity/utils.py:12-53` 要求 `adata.layers["counts"]`，把它复制到 `adata.X`，执行同样的总量归一化和 `log1p`。`utils.py:56-137` 再检查目标基因重叠（默认至少 5,000 个）、处理稀疏矩阵，并按保存的 `gene_order` 对齐列。

这一步很重要：模型并不接受任意基因顺序或任意缩放的矩阵。查询数据如果缺少大量目标基因，或仍然是未经归一化的 counts，距离就不再对应论文中的模型输入条件。

#### 3.2 Encoder 和 Decoder

论文的 Encoder 宽度为 $28,231\rightarrow1,024\rightarrow1,024\rightarrow1,024\rightarrow128$。代码 `scimilarity/src/scimilarity/nn_models.py:18-66` 使用输入 dropout 0.4、隐藏层 dropout 0.5、Linear + BatchNorm1d + PReLU，最后用 `F.normalize(x, p=2, dim=1)` 把每个细胞向量归一化到单位球面。

Decoder 在 `nn_models.py:69-127` 中反向使用隐藏宽度，把 128 维表示映射回基因空间。它只在训练时需要；`CellEmbedding` 推理时只加载 `encoder.ckpt`，然后把输入分批送入 Encoder（`cell_embedding.py:23-160`）。

单位范数有两个作用：第一，所有细胞都在同一个固定尺度上，triplet margin 的意义不会因为向量范数任意增大而失效；第二，在单位向量上，cosine distance 与平方欧氏距离具有相同的近邻排序，虽然数值尺度不同。

### 4. 三元组和损失函数

#### 4.1 Triplet loss

对于 anchor $&#123;&#123;\bf{x}}}_{i}^{a}$、positive $&#123;&#123;\bf{x}}}_{i}^{p}$ 和 negative $&#123;&#123;\bf{x}}}_{i}^{n}$，论文定义：

$$
{\rm{d}}({\bf{x}},{\bf{y}})=||f({\bf{x}})-f({\bf{y}})||_2^2
$$

$$
L_{\rm triplet}=\frac{1}{N}\sum_i\max\big(d({\bf{x}}_i^a,{\bf{x}}_i^p)-d({\bf{x}}_i^a,{\bf{x}}_i^n)+\alpha,0\big).
$$

代码 `scimilarity/src/scimilarity/triplet_selector.py:130-183` 的逻辑是：

- 找到同一标签的细胞对作为 anchor-positive；
- 如果传入 study ID，则只保留来自不同 study 的正样本对；
- 通过 Cell Ontology 得到 anchor 标签的祖先和后代，把这些关系从 negative 候选中排除；
- 对所有候选负样本计算 $d(a,p)-d(a,n)+\alpha$；
- 默认使用 `semihard`，即 loss 大于 0 且小于 margin 的候选（`triplet_selector.py:257-278`）。

如果启用 `perturb_labels`，代码会在存在合适父标签时把一部分细胞标签粗粒化一个层级（`triplet_selector.py:98-128`）。若一个 batch 没有有效的三元组，代码插入 `[0, 0, 0]` 作为保护性 fallback（`triplet_selector.py:185-199`）；这保证训练步骤不会因空索引崩溃，但不是论文重点描述的算法步骤。

#### 4.2 Reconstruction loss

论文只对 anchor 重构：

$$
L_{\rm MSE}=\frac{1}{N}\sum_i||{\bf{x}}_i^a-g(f({\bf{x}}_i^a))||_2^2.
$$

论文中 batch 的 $N=1,000$。代码 `training_models.py:231-245` 先对整个 batch 执行 `embedding, reconstruction = self(cells)`，再用 `nn.MSELoss()` 比较原 batch 和重构 batch。这里的实现与“每个 batch cell 都可作为 anchor 候选”的训练组织一致，但代码并没有单独建立一个只含 anchor 的张量，阅读实现时应区分论文符号和 batch-level 代码路径。

#### 4.3 混合目标与优化

`training_models.py:293-315` 精确实现：

```python
(triplet_loss_weight * triplet_loss) + ((1.0 - triplet_loss_weight) * mse)
```

训练脚本 `scripts/train.py:241-262` 的默认值包括 margin 0.05、triplet weight 0.001、batch size 1,000、latent dimension 128、学习率 0.005、hidden dimensions `[1024, 1024, 1024]`、input dropout 0.4、hidden dropout 0.5、semi-hard mining 和跨 study 正样本。`training_models.py:177-193` 使用 AdamW 与 cosine annealing；`training_models.py:341-352` 还会对第一层 Encoder Linear 参数加一个按当前学习率缩放的 L1 penalty。

### 5. 训练和推理的边界

#### 5.1 训练阶段

论文使用 56 个训练 study、203 个跨 study 可用的 Cell Ontology term，并采样 50,000,000 个信息量较高的 triplet；15 个完整 study 被留作测试，而不是从每个 study 随机划分细胞。训练集和测试集均经过质量控制，去除 doublet、线粒体比例过高或检测基因过少的细胞。

代码层面，`scripts/train.py:98-176` 从外部 TileDB/CellArr 元数据中排除癌症相关样本、设置 `total_counts>1000`、`n_genes_by_counts>500`、线粒体比例小于 20%、排除 doublet，并创建 `CellMultisetDataModule`。这里存在一个边界细节：论文文字说删除“小于 500 个基因”的细胞，而脚本使用严格的 `>500`，因此恰好 500 个基因的细胞在两种描述下处理不同。

#### 5.2 推理和检索

`CellEmbedding` 初始化时读取：

- `encoder.ckpt`：Encoder 参数；
- `gene_order.tsv`：基因顺序；
- `layer_sizes.json`：从 checkpoint 推断网络宽度；
- `label_ints.csv`：标签映射。

`get_embeddings` 可以接收 NumPy、PyTorch 或 CSR/CSC 稀疏矩阵，按 `buffer_size=10000` 分批推理，并返回 `[num_cells, latent_dim]` 的 NumPy 数组。代码使用 `torch.inference_mode()`，并在结果含 NaN 时抛出异常（`cell_embedding.py:129-160`）。

`CellSearchKNN` 支持 HNSWlib 和 TileDB vector search（`cell_search_knn.py:43-106`）。`CellQuery.search_nearest` 默认请求 $k=10,000$，并把 `embedding_idx` 和 `query_nn_dist` 与研究、样本等元数据拼接（`cell_query.py:209-278`）。如果指定 `max_dist`，代码把 $k$ 扩大到 1,000,000 后按距离过滤。

#### 5.3 kNN 注释

`CellAnnotation.get_predictions_knn` 调用同一个近邻索引（`cell_annotation.py:209-212`），对每个 query 的邻居按标签计数；默认使用多数投票，也可以使用 $1/\max(d,10^{-6})$ 的距离加权投票（`cell_annotation.py:235-251`）。输出还包括最小/最大距离、最佳标签相对第二标签和全部命中的比例。也就是说，注释是共享 embedding 的一个下游应用，不是训练时直接优化的 softmax 分类头。

### 6. 可解释性：距离而不是类别的解释

论文把 Integrated Gradients 应用于两个细胞在 latent space 中的距离，而不是对分类 logits 做解释。对于 foreground $\mathbf{x}$ 和 background $\mathbf{y}$：

$$
&#123;&#123;\rm{Importance}}}_{i}({\bf{x}},{\bf{y}})=\left|\max(x_i-y_i,0)\times\int_0^1\frac{\partial d({\bf{y}}+a({\bf{x}}-&#123;&#123;\bf{y}}}),{\bf{y}})}{\partial x_i}\,da\right|.
$$

代码 `scimilarity/src/scimilarity/interpreter.py:67-129` 以 background 为 baseline，使用 Captum 的 Integrated Gradients，通过 `attr *= anc > neg` 只保留 foreground 表达更高的基因，随后取绝对值。`get_ranked_genes` 按跨细胞平均 attribution 排序并返回标准差（`interpreter.py:131-161`）。

因此，高 attribution 表示该基因的表达差异会显著影响这对细胞的**学习距离**。它可以帮助生成细胞状态 signature，但不能单独证明基因是该状态的因果驱动因素；background 的选择也会影响结果。

### 7. 论文结果如何理解？

- 在 15 个 held-out study 上，SCimilarity 的表示用于整合、注释和检索；论文报告其 cell-type ASW 较高，但 study ARI/NMI/batch ASW 显示它没有强行抹掉所有 study 结构。
- 在纤维化相关 macrophage 查询中，SCimilarity 与 gene-signature 分数的 Spearman $\rho=0.77$，高于 scGPT 的 0.59 和 scFoundation 的 0.54。
- 在健康肾脏标签受限任务中，SCimilarity 与作者标签的匹配率为 86.5%；在 held-out CITE-seq 免疫数据上报告准确率 75.3%。相关细胞类型之间仍有明显不一致，且作者标签本身存在 marker 混合。
- 跨组织查询发现 fibrosis-associated macrophage 与 myofibroblast 状态，并通过 attribution 找到已知与候选标志基因。论文随后在 3D hydrogel 系统中复现了 FM-like 细胞状态；这是“由检索生成假设，再进行实验验证”的案例，不是代码单独能保证的结果。

### 8. 代码与论文的一致性、缺口和使用边界

#### 已直接验证

`doc_code.md` 中逐行核对了 Encoder/Decoder、四个核心损失/距离公式、ontology-aware mining、预处理、embedding、HNSW/TileDB 搜索、kNN 注释和 Integrated Gradients。整体代码-论文一致性评估为 **高**。

#### 仍需外部资源

- 论文的完整 CellArr/TileDB 训练数据；
- 预训练模型目录和 checkpoint；
- 23.4-million-cell reference embeddings、kNN 图和元数据；
- 论文 figure、benchmark、ILD/FMs 查询和实验验证的端到端工作流。

这些资源由论文的数据/代码可用性声明提供：模型权重、embedding、元数据和 kNN 图存放在 Zenodo，代码和 tutorials 在 GitHub；但它们没有作为本地 Author 阶段的可运行输入被执行。

#### 研究者使用时应注意

1. query 的基因顺序和 log-normalization 必须与模型约定一致；
2. kNN 距离不是自动等于论文图中的 inverse-distance SCimilarity score；
3. atlas 中不同组织、疾病、study 的细胞量差异很大，命中数量不能直接当作生物学 prevalence；
4. 低置信度可能表示新生物状态，也可能表示技术不兼容或 reference 覆盖不足；
5. attribution、跨组织共现和相似性都是候选机制线索，需要独立实验或统计设计验证。

### 9. 一句话总结

SCimilarity 用重构保持表达细节，用 Cell Ontology 约束的 triplet learning 学习可迁移的细胞距离，再用近邻索引把这个距离扩展成数千万细胞的搜索、注释与解释系统；公开代码实现了核心算法，但完整 atlas、模型资产和论文实验仍属于外部复现边界。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SCimilarity

### Why This Paper Matters

Single-cell atlases contain tens of millions of profiles, but conventional workflows were not designed to search the full expression state of a new cell across studies, tissues, diseases, and experimental systems. PCA and autoencoders preserve input variation but do not explicitly learn a transferable notion of cell similarity. Integration methods such as Harmony (*Nature Methods*, 2019), Scanorama (*Nature Biotechnology*, 2019), scVI, and scArches optimize dataset alignment, often by fitting or adapting to the datasets being integrated, rather than exposing a frozen search metric over a massive reference.

SCimilarity is a deep metric-learning foundation model that turns a cell profile into a unit-normalized 128-dimensional embedding. It combines Cell Ontology-aware triplet loss, which places same-type cells from different studies near one another, with reconstruction loss, which preserves within-type expression-state variation. A frozen encoder and approximate-nearest-neighbor index then support cell search, annotation, outlier detection, and gene attribution without query-dataset retraining.

### Method in Brief

```text
log-normalized expression in a fixed gene space
        |
        v
fully connected encoder --> unit 128-D cell embedding
        |                         |
        |                         +--> ontology-aware cross-study triplet loss
        v
decoder reconstruction ---------> combined loss

frozen query embedding --> reference kNN --> similar cells + metadata
                         --> labeled kNN   --> cell-type prediction
                         --> Integrated Gradients --> important genes
```

The paper's selected model uses a triplet margin of 0.05 and triplet coefficient $\beta=0.001$ in

$$
L=(1-\beta)L_{\rm MSE}+\beta L_{\rm triplet}.
$$

Lower $\beta$ improves sensitive state retrieval by preserving more expression detail; higher $\beta$ mixes same-type cells across studies more strongly. Ambiguous ancestor-descendant Cell Ontology relationships are excluded from negative sampling, and positives are sampled across studies. The model was trained on 7,886,247 profiles from 56 studies with 203 ontology terms; 15 complete studies (1,415,962 cells) were held out for evaluation. The searchable corpus contained 23,381,150 cells from 412 studies.

### Main Results

- **Retrieval:** On the reported fibrotic-macrophage benchmark, similarity to the query agreed with a gene-signature score at Spearman $\rho=0.77$, compared with $0.59$ for scGPT and $0.54$ for scFoundation.
- **Integration/generalization:** The pretrained representation yielded higher cell-type silhouette coherence and comparable graph connectivity to dedicated integration methods, but retained more study structure. This is a documented tradeoff, not complete batch correction.
- **Annotation:** A single frozen model annotated held-out kidney profiles at 86.5% agreement with author labels when constrained to the study label set, comparable with kidney-specific scANVI (85.2%), CellTypist (90.4%), and TOSICA (87.2%). On the held-out CITE-seq immune dataset, reported accuracy was 75.3%, versus 52.2%, 59.1%, and 44.4%, respectively.
- **Biological search:** Querying fibrosis-associated macrophage and myofibroblast states found related profiles across fibrotic diseases and tissues. Distance-based Integrated Gradients recovered established signatures and highlighted lipid scavenging, matrix remodeling, complement, and genes including `TREM2`, `HLA-DQA1`, and `RGS1`.
- **Experimental validation:** The top in vitro macrophage match was a 3D hydrogel culture. In the authors' independent day-8 replication, 41.5% of myeloid cells were reported as FM-like across three donors and expressed hallmark genes such as `CCL18`, `GPNMB`, `SPP1`, and `TREM2`.

These numerical and biological results are paper-reported; this workspace did not rerun training or reproduce the experiments.

### What the Code Confirms

The analyzed GitHub snapshot at commit `3ce3ec81e122a115eb3e667706725120f7ee252d` has **high paper-code fidelity** for the core method. Direct source reads confirm:

- the encoder/decoder architecture and L2-normalized latent output;
- squared Euclidean distance, triplet-margin loss, MSE reconstruction, and the combined objective;
- Cell Ontology ancestor/descendant exclusion, cross-study positives, and semi-hard mining;
- fixed-gene alignment, per-10,000 log normalization, and buffered embedding;
- HNSW/TileDB nearest-neighbor search, metadata return, and kNN annotation;
- the modified Integrated Gradients procedure used to rank genes.

Material implementation details not emphasized by the central equations include AdamW with cosine annealing, an LR-scaled L1 penalty on the first encoder linear layer, and a zero-loss fallback triplet when no valid mined triplet exists. The search API returns raw neighbor distances; the paper's displayed inverse-distance SCimilarity score convention is not centralized in the core query API.

### Limitations

- Reference coverage is uneven, and the paper reports poor performance for fetal samples, granulocytes, hematopoietic stem/progenitor cells, and intermediate precursors. Cancer cells and cell lines were withheld from training.
- A query profile or centroid, metadata filters, and score thresholds require user choices that can change results. Retrieved similarity and attribution are associative, not causal.
- Cross-platform generalization was demonstrated, but the authors explicitly advise care when interpreting cross-technology integrations.
- Closely related cell identities remain difficult, and author annotations are themselves an imperfect benchmark.

### Reproducibility: 4/5

Code and tutorials are public under Apache 2.0, and the paper provides Zenodo deposits for the publication snapshot, model weights, embeddings, metadata, and kNN graphs. The local source snapshot implements the central method closely and includes training/inference scripts. Reproduction is not turnkey in this workspace because the large CellArr/TileDB corpus, model files, reference indexes, and paper-analysis workflows were not locally materialized or executed; no single script reproduces every benchmark, figure, biological query, and wet-lab result. The supplementary PDF exists locally, but no supplementary Markdown or reconstructed supplemental tables were available for this authoring phase.

### Bottom Line

SCimilarity's central contribution is a reusable cell-state metric rather than a one-task predictor: reconstruction retains subtle transcriptomic state, ontology-aware metric learning makes distance transferable across studies, and a large indexed atlas turns that distance into search. The code strongly supports this mechanism. The paper's biological examples show how retrieval can generate experimentally testable hypotheses, while the coverage, thresholding, and reference-composition limits determine how cautiously those hypotheses should be interpreted.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
