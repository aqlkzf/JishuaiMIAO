---
layout: default
permalink: /paper-atlas/cellwhisperer-iclr-2024-61881414/
title: "CellWhisperer_ICLR_2024"
nav: false
wide: true
description: "单细胞 RNA 测序数据通常包含数千到数百万个细胞，每个细胞约有 2 万个基因维度。传统分析既需要编程能力，也需要对具体组织、细胞类型和疾病背景有较强的生物学知识。CellWhisperer 希望把自然语言变成一个额外的分析接口，使研究者可以直接提出“显示肠道中的组织驻留 T 细胞”或“这些细胞是什么”等问题，并让答案与当前转录组数据相关联。"
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
      <span>bioRxiv · 2024</span>
    </div>
    <h1>CellWhisperer_ICLR_2024</h1>
    <p>Multimodal learning of transcriptomes and text enables interactive single-cell RNA-seq data exploration with natural-language chats</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/epigen/cellwhisperer" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellWhisperer_ICLR_2024">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellWhisperer 方法详解

### 1. 这篇工作要解决什么问题？

单细胞 RNA 测序数据通常包含数千到数百万个细胞，每个细胞约有 2 万个基因维度。传统分析既需要编程能力，也需要对具体组织、细胞类型和疾病背景有较强的生物学知识。CellWhisperer 希望把自然语言变成一个额外的分析接口，使研究者可以直接提出“显示肠道中的组织驻留 T 细胞”或“这些细胞是什么”等问题，并让答案与当前转录组数据相关联。

它实际解决的是两个相关但不同的任务：

1. **检索与零样本标注**：把转录组和文本映射到同一个向量空间，计算任意文本与任意细胞/样本的匹配分数。
2. **转录组条件对话**：把转录组向量转换成大语言模型可接收的 token 表示，让 Mistral 7B 在回答问题时参考当前样本的表达状态。

本文档基于本地获取的 bioRxiv 作者版本（DOI `10.1101/2024.10.15.618501`，2024，v1）。最初请求的 OpenReview 页面受到 challenge 阻拦，因此不能把当前文本称为已获取的 OpenReview 稿件。代码行为仅指本地 GitHub 快照 commit `29843cf308704e019048424b0c3b98179628358a`。

### 2. 为什么已有方法还不够？

- Geneformer（*Nature*, 2023）能够把按表达量排序的基因序列编码成转录组表示，但本身不能理解自由文本。论文还指出它最多处理 2048 个基因，而且排序表示缺少定量分辨率。
- BioBERT（*Bioinformatics*, 2020）能编码生物医学文本，却不包含当前样本的表达信息。
- CLIP（ICML, 2021）和 LiT（论文参考文献列为 CVPR, 2021）证明了对比学习可以连接两个模态，但原任务是图像和文本。
- LLaVA（arXiv, 2023）提供了把非文本模态接入 LLM 的设计范式，但原始输入同样是图像而不是转录组。
- CELLxGENE（bioRxiv, 2021）擅长可视化和交互选择，却没有原生的转录组-自然语言共同表示。

CellWhisperer 的关键不是简单地“给单细胞软件加一个聊天框”，而是先学习一个可检索的转录组-文本语义空间，再让对话模型消费该空间中的转录组表示。

### 3. 方法总览

```text
GEO 表达矩阵 + 元数据 -----------------------+
  -> 清洗 -> LLM 生成简洁文本注释            |
CELLxGENE 单细胞矩阵                          +-> 1,082,413 个 (转录组, 文本) 配对
  -> 按元数据分组 -> pseudo-bulk              |
  -> LLM 生成简洁文本注释 --------------------+

转录组 -> 基因排序/tokenize -> Geneformer -> 2048 维投影 --+
                                                          +-> 对比损失 -> 共同嵌入空间
文本 ----> WordPiece <= 128 -> BioBERT -----> 2048 维投影 --+

自由文本查询 -> 文本嵌入 -> 与细胞嵌入计算缩放余弦相似度
                           -> 检索、零样本标注、UMAP 着色

转录组嵌入 -> token adapter -> Mistral 7B + 用户问题 -> 自然语言回答
             （论文描述；本地缺少内部 trainer）
```

### 4. 训练数据如何构造？

论文从两个大规模公共资源得到训练对（`paper.md:162-177`）：

- **GEO/ARCHS4**：从 722,425 个统一处理的人类 RNA-seq 样本出发，去除表达基因不足 250 的样本和与独立验证集重叠的样本，保留 705,430 个转录组。
- **CELLxGENE Census**：从 257 个研究、19,663,838 个细胞出发，在每个样本内按元数据分组并对表达量取均值，得到 376,983 个 pseudo-bulk 转录组。
- **文本标准化**：使用 Mixtral 8x7B 把异构元数据压缩为简洁的生物学描述。论文给出的采样参数为 temperature 0.2、`top_p=0.9`、`top_k=50`。

最终共得到 1,082,413 个匹配的转录组-文本对。这里的 LLM 是数据整理工具；它产生监督文本，但不等同于最终的 CellWhisperer 对话模型。

### 5. 共同嵌入模型

#### 5.1 符号

论文没有给该模型定义公式符号，下面的符号是为了说明而引入：

| 符号 | 含义 | 代码对应 |
|---|---|---|
| `x_i` | 第 `i` 个转录组 | `expression_tokens` 等输入 |
| `t_i` | 与 `x_i` 匹配的文本 | `input_ids`, `attention_mask` |
| `f_x`, `f_t` | Geneformer、BioBERT 编码器 | `transcriptome_model`, `text_model` |
| `p_x`, `p_t` | 两个模态投影器 | `img_block`, `text_block` |
| `z_i^x`, `z_i^t` | L2 归一化后的 2048 维嵌入 | `feat1`, `feat2` |
| `alpha` | 可学习的 logit 温度 | `temperature` |
| `S_ij` | 转录组 `i` 与文本 `j` 的匹配 logit | `o` |

#### 5.2 转录组预处理

论文做法是把基因按表达量排序，取前 2048 个基因，并通过人类基因符号字典 token 化（`paper.md:192-198`）。这与 Geneformer 的“gene sentence”表示一致。

代码中的 `JointEmbedDataModule` 从 AnnData 读取自然语言注释和表达矩阵，调用联合 processor，并过滤表达基因过少的样本（`jointemb/dataset/jointemb.py:133-240`）。Geneformer 路径最终产生 `expression_tokens` 和 `expression_token_lengths`（`jointemb/processing.py:92-180`）。

#### 5.3 文本预处理

文本由 BioBERT 的 WordPiece tokenizer 处理，最大长度为 128。代码配置 `model_max_length: 128`，并固定 padding 长度（`cellwhisperer_clip_v1.yaml:95-103`; `jointemb/dataset/jointemb.py:147-170`）。

#### 5.4 两个编码器

```text
h_i^x = f_x(x_i)   # Geneformer 特征
h_i^t = f_t(t_i)   # BioBERT 特征
```

最终配置的 `locking_mode: LU` 很重要：`L` 表示转录组 tower 始终锁定，`U` 表示文本 tower 在前期 warm-up 后解锁。因此，CellWhisperer 采用的是 LiT 风格训练：保留 Geneformer，微调 BioBERT 和投影层（`cellwhisperer_clip_v1.yaml:73-94`; `jointemb/model.py:120-188`）。

#### 5.5 投影到 2048 维共同空间

论文将每个模态的特征通过两层线性网络、ReLU 和归一化映射到 2048 维（`paper.md:180-189`）。直接读代码后可以写成：

```text
u_i^m = Linear2(ReLU(BatchNorm(Linear1(h_i^m))))
r_i^m = ShortcutLinear(h_i^m)
z_i^m = L2Normalize(LayerNorm(u_i^m + r_i^m))
```

其中 `m` 是转录组或文本模态。论文的高层描述与“2048 维双投影器”一致，但代码还包含一个可学习 shortcut 和最终 LayerNorm（`jointemb/loss/discriminator.py:16-45`）。因此这一项是 **Partial** 而非完全逐字对应。

#### 5.6 相似度

代码计算一个 batch 内所有转录组与所有文本的相似度矩阵：

```text
S_ij = exp(alpha) * (z_i^x)^T z_j^t
```

因为两个向量都经过 L2 归一化，点积等价于余弦相似度。`exp(alpha)` 是可学习缩放项，初始化对应温度 0.07（`jointemb/loss/discriminator.py:48-80`）。

#### 5.7 对称 InfoNCE 损失

对于 batch 大小 `B`，正确匹配位于相似度矩阵对角线。代码分别从两个方向做交叉熵：

```text
L_x->t = CE(S,   [0,1,...,B-1], transcriptome_weights)
L_t->x = CE(S^T, [0,1,...,B-1], annotation_weights)
L_clip = (L_x->t + L_t->x) / 2
```

这会提高匹配对的相似度并压低同一 batch 内其他不匹配对的相似度。`losses.py:45-86` 直接实现了该目标。最终配置启用了 sample weighting；密度较低区域的样本可以得到更大的贡献，从而缓解公共数据库覆盖不均衡的问题。

#### 5.8 训练日程

论文与 v1 YAML 对应的关键参数如下：

| 参数 | 值 |
|---|---:|
| batch size | 512 |
| epoch | 16 |
| 最大学习率 | `1e-5` |
| 第一阶段 | 前 3% step 冻结 Geneformer 和 BioBERT，只训练投影器 |
| 第二阶段 | 解锁 BioBERT，再进行 3% 线性 warm-up |
| 后续 | cosine decay |
| Geneformer | 全程冻结，输出可缓存 |

Lightning 代码实现冻结/解锁、第二次 warm-up 和 cosine scheduler（`cellwhisperer_lightning.py:264-285,318-351,359-444`）。缓存会在第一个 epoch 后及训练结束时落盘。这些是**代码验证行为**；本地没有不可变的历史训练 manifest，因此不能仅凭 YAML 证明论文模型当时一定由该文件运行完成。

### 6. 推理：CellWhisperer score

对于查询文本 `q` 和细胞/样本 `x_j`：

```text
score(q, x_j) = exp(alpha) * (z_q^t)^T z_j^x
```

分数越大，查询与该转录组越匹配。若输入是一组候选标签，可以对同一个转录组的标签分数做 softmax，得到零样本分类概率。

代码中的 `score_transcriptomes_vs_texts` 支持：

- 原始 AnnData 或已经算好的二维转录组嵌入；
- 文本字符串或已经算好的文本嵌入；
- 先平均表达再编码，或先编码再平均嵌入；
- raw、softmax、z-score 和 0-1 归一化输出。

默认是先得到每个细胞的归一化嵌入，再按组平均嵌入（`utils/inference.py:20-161`）。这与先平均表达矩阵再经过非线性编码器并不等价，使用时需要明确选择。

### 7. 转录组条件对话模型

#### 7.1 训练对话

论文构造 106,610 个对话（`paper.md:240-250`）：

- 10,000 个 simple chats；
- 10,000 个 detailed chats；
- 5,000 个 complex chats；
- 81,610 个 multi-turn conversational chats。

生成这些对话时使用每个转录组的 top 50 高表达基因、top 50 GSVA gene sets 和文本注释。

#### 7.2 论文描述的适配方式

论文声称使用两层 adapter，把一个 2048 维 CellWhisperer 转录组嵌入映射为 **8 个 4096 维**、与 Mistral 7B 兼容的 token embedding（`paper.md:252-255`）。随后：

1. 冻结 Mistral，用 1,082,213 个 simple pair 训练 adapter 一个 epoch；
2. 解冻 Mistral，在 106,610 个生成对话上共同微调 Mistral 和 adapter 一个 epoch；
3. 使用原始自回归目标，但对问题部分做 loss mask，只监督回答 token。

#### 7.3 本地代码能验证到哪里？

`src/llava/rules/training.smk:1-164` 能验证两阶段工作流：第一阶段打开 `tune_mm_mlp_adapter`，第二阶段加载 `mm_projector.bin` 并微调 LLM。规则也给出 `1e-4` 和 `2e-5` 两个学习率。

但是 `modules/LLaVA/` 在当前快照中是空目录，被调用的 `modules/LLaVA/llava/train/train_mem.py` 不存在。因此下面内容必须保留为 **MISSING / Not found**：

- adapter 的真实层定义；
- 2048 维如何精确变成 8 个 4096 维 token；
- token 插入位置；
- answer-only loss mask；
- generation 与 perplexity 的实现。

此外，Snakemake 注释写的是“转换成 4 个 token”，论文写的是 8 个 token。没有 trainer 和实际运行配置时，不能替作者消除这个矛盾。

### 8. 评估结果应如何理解？

#### 共同嵌入

- 跨模态检索平均 ROC-AUC：0.927。
- Tabula Sapiens 20 类细胞类型零样本 ROC-AUC：0.94；177 类为 0.91。
- ImmGen：0.99；胰腺数据：0.83；229 个疾病亚型：0.82。
- 相比 Geneformer，Extended Data Figure 2 显示 batch integration 从 0.78 提升到 0.84，cell-type clustering 从 0.49 提升到 0.56。
- 8,812 个 gene-set 名称与 GSVA 的对应关系总体偏正，但不同概念之间差异很大，也存在弱相关和负相关。

这些结果支持“文本监督能把转录组按生物学概念组织起来”，但高 ROC-AUC 不表示相近细胞亚型都能被准确区分。

#### 对话模型

在 200 个留出问答上，论文将匹配转录组与 30 个错误转录组进行 perplexity 比较，并报告 90% 的 matched preference。它说明模型通常会使用转录组条件，但**不等于**回答事实正确，也不等于没有幻觉。Extended Data Figure 3 还显示不同细胞类型之间表现不均匀。

### 9. 探索性假设与已验证结论要分开

Figure 4 中，模型用“stem cells”查询定位结肠上皮中的一群细胞，聊天回答提到 `LGR5`，表达图也显示空间对应；非炎症样本的 CellWhisperer score 高于炎症样本，图中给出 `p < 1e-37`。

这可以产生一个值得继续检验的假设：慢性炎症环境可能与 `LGR5` 阳性肠上皮干细胞状态减弱有关。但当前图是细胞层面的探索性比较，不能单独证明病人层面独立性，更不能证明炎症导致干细胞减少。合理后续包括按病人聚合、控制批次/组织区域、预注册统计模型，以及实验验证。

### 10. 代码-论文一致性与复现边界

**总体一致性：medium；复现评分：3/5。**

#### 已直接验证

- Geneformer/BioBERT 双编码器和 `LU` 冻结策略；
- 2048 维 residual projection；
- learned-temperature 全配对相似度；
- 加权、对称 InfoNCE；
- batch 512、16 epoch、两段 warm-up 和 cosine schedule；
- 文本-转录组打分函数；
- embedding model Flask API。

#### 缺失或不完整

- LLaVA trainer、内部 adapter、生成与 perplexity 代码；
- 模型权重、完整运行日志和不可变训练 manifest；
- 独立 Supplementary Markdown；
- Figure 1 本地图片（只有 caption）；
- 当前工作没有执行训练或复现实验。

因此，从当前快照可以较完整地学习和检查 embedding/search 方法，但不能独立重建论文中的完整聊天模型。最稳妥的使用方式是把 CellWhisperer 当作探索工具：用自然语言提出候选模式，再回到表达矩阵、统计检验和独立实验进行确认。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellWhisperer

### Problem

Single-cell RNA-seq datasets contain thousands to millions of cells and roughly 20,000 gene measurements per cell, so interpretation normally requires both programming skill and domain expertise. Existing analysis tools are task-specific, while transcriptome foundation models do not by themselves provide an interface for arbitrary biological questions. Geneformer (*Nature*, 2023) embeds ranked gene-expression sequences but is transcriptome-only and, as the paper notes, is limited to 2048 genes with little quantitative resolution. BioBERT (*Bioinformatics*, 2020) understands biomedical text but not sample-specific expression. General multimodal methods such as CLIP (ICML, 2021), LiT (CVPR, 2021 in the paper's bibliography), and LLaVA (arXiv, 2023) provide the architectural precedent but were designed around images and language.

### Proposed Method

CellWhisperer makes natural language a query and interaction layer for transcriptomes. Its first component is a dual encoder trained on 1,082,413 matched transcriptome-text pairs curated from GEO (705,430 profiles) and CELLxGENE Census (376,983 pseudo-bulk profiles). A frozen Geneformer transcriptome tower and a fine-tuned BioBERT text tower feed separate 2048-dimensional projection modules. Symmetric InfoNCE training brings matched pairs together and separates all unmatched in-batch pairs; the resulting scaled cosine similarity is the `CellWhisperer score` used for free-text retrieval and zero-shot annotation.

The second component follows a LLaVA-style design. The paper maps each 2048-D transcriptome embedding through an adapter into eight Mistral-compatible token embeddings, then fine-tunes Mistral 7B on 106,610 transcriptome-centric conversations. This supports questions about selected cells, genes, and biological state. Both components are exposed through an augmented CELLxGENE Explorer interface, where users can search, visually select cells, chat about them, and check generated claims against expression maps.

### Computational Flow

```text
repository count matrices + metadata
  -> filtering, pseudo-bulk aggregation, LLM-curated descriptions
  -> paired transcriptome/text dataset
  -> Geneformer(x) and BioBERT(t)
  -> residual 2048-D projections + L2 normalization
  -> learned-temperature all-pairs similarity
  -> weighted symmetric InfoNCE
  -> free-text search / zero-shot labels / transcriptome embedding
  -> transcriptome-token adapter + Mistral 7B
  -> natural-language answer in CELLxGENE
```

The code adds details not explicit in the paper's compact architecture description: each projection has a nonlinear branch plus a learned linear shortcut and final LayerNorm; modality-specific density weights can enter the two contrastive directions; frozen encoder outputs are cached by input hash; and inference can average expression before embedding or normalized embeddings afterward.

### Evaluation

The embedding model is evaluated through cross-modal retrieval, zero-shot classification, gene-set correspondence, and embedding geometry. The paper reports mean cross-modal retrieval ROC-AUC of 0.927. Zero-shot ROC-AUC is 0.94 for 20 common Tabula Sapiens cell types, 0.91 for all 177 types, 0.99 for ImmGen immune profiles, 0.83 for the pancreas benchmark, and 0.82 across 229 disease subtypes. Extended Data Figure 2 shows improved batch integration (0.84 versus 0.78) and cell-type clustering (0.56 versus 0.49) relative to Geneformer, while 8,812 gene-set-name queries show broadly positive but heterogeneous correspondence with GSVA.

For the conversational branch, 200 held-out question-answer pairs are scored against 30 mismatched transcriptomes each. The paper reports that matched transcriptomes are preferred in 90% of cases by perplexity quantile. This shows that generation generally depends on the transcriptome input, but it is not a factuality test. Main Figures 3-4 are worked interactive examples; they demonstrate workflow and hypothesis generation rather than controlled accuracy.

### Limitations

- CellWhisperer inherits Geneformer's gene limit/rank representation and Mistral's generation failures. The paper reports occasional over-specific hallucinations and recommends independent validation.
- Training coverage reflects public repositories; poorly represented biology is unlikely to transfer well.
- High macro ROC-AUC coexists with confusion among closely related cell types and weaker accuracy for large label sets.
- Gene-set correspondence is not uniform, and the embedding-geometry comparison is against Geneformer rather than a broad method panel.
- The colonic inflammation example is exploratory. Its cell-level distribution test does not by itself establish patient-level independence or causality.

### Reproducibility

**Rating: 3/5; code-paper fidelity: medium.** The acquired GitHub snapshot (commit `29843cf308704e019048424b0c3b98179628358a`) directly supports the dual encoder, residual projectors, symmetric contrastive loss, v1 training configuration, scoring utility, validation modules, and embedding-model Flask service. The v1 YAML matches the paper's batch size 512, 16 epochs, `1e-5` learning rate, 3% frozen warm-up, BioBERT unlock, second warm-up, and cosine schedule. The paper states that data, checkpoints, and start-to-finish pipelines are available through the project, but they were not executed in this analysis.

The snapshot's `modules/LLaVA/` directory is empty, although Snakemake rules invoke `modules/LLaVA/llava/train/train_mem.py`. Therefore the internal transcriptome-token adapter, exact eight-token construction, answer loss masking, generation, and perplexity implementation are **MISSING / Not found**. The workflow comment also says four tokens while the paper says eight. No supplementary Markdown, run logs, model weights, or immutable historical training manifest were acquired, and Figure 1 has no retained local image. These gaps prevent full conversational-model reproduction from this workspace without additional assets.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
