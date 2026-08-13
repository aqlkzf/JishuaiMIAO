---
layout: default
permalink: /paper-atlas/transformerreview-c2bd44af/
title: "TransformerReview"
nav: false
wide: true
description: "这篇 Nature Methods 文章是一篇综述与观点文章，不提出一个可复现的统一算法。它整理的核心问题是：Transformer 在语言中依赖自然序列，而单细胞表达矩阵本质上没有类似词序的天然顺序；因此，决定模型成败的第一步往往不是注意力层本身，而是如何把稀疏、连续、带批次效应的组学测量转换成 token。 全文可沿四条轴阅读： 输入表示：一个 token 代表基因、细胞、通路还是其他分子特征？表达量如何进入 token？"
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
      <span>Nature Methods · 2024</span>
    </div>
    <h1>TransformerReview</h1>
    <p>Transformers in single-cell omics: a review and new perspectives</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-024-02353-z" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for TransformerReview">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/theislab/single-cell-transformer-papers" target="_blank" rel="noopener noreferrer" aria-label="Open code for TransformerReview">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 单细胞组学 Transformer 综述：方法版图、证据边界与选择逻辑

这篇 Nature Methods 文章是一篇综述与观点文章，不提出一个可复现的统一算法。它整理的核心问题是：Transformer 在语言中依赖自然序列，而单细胞表达矩阵本质上没有类似词序的天然顺序；因此，决定模型成败的第一步往往不是注意力层本身，而是如何把稀疏、连续、带批次效应的组学测量转换成 token。

### 1. 综述的组织框架

全文可沿四条轴阅读：

1. **输入表示**：一个 token 代表基因、细胞、通路还是其他分子特征？表达量如何进入 token？
2. **架构与训练**：encoder、decoder 或两者结合；MLM、next-token prediction（NTP）或监督训练。
3. **任务层级**：基因表示、组学特征相互作用、细胞表示、模态生成、细胞注释与空间组学。
4. **证据强度**：某模型展示了可行性，还是在严格外部基准上优于简单方法？是否存在预训练数据泄漏、基线调参不公平或零样本定义含混？

这四条轴不能压缩成一条“标准单细胞 Transformer 流水线”，因为 Geneformer、scGPT、scBERT、TOSICA、tGPT、UCE、CellPLM 等模型在 token 语义、表达编码、预训练目标和输出任务上并不等价。

### 2. 三类输入编码是最关键的分岔

综述把单细胞表达转换为 Transformer 输入的方法分成三类（图 3）：

#### 2.1 按表达量排序

Geneformer、iSEEK、tGPT 等把基因当 token，并按细胞内归一化表达量排序，再加入位置编码。优点是可直接借用 NLP 序列方法，也天然忽略大量零值；代价是表达量被降成秩次，绝对差异和相近表达值之间的距离会丢失。综述认为这种把非序列数据“语言化”的方案仍较初步。

#### 2.2 表达值分箱

scBERT、scGPT 等把每个基因的表达量离散到 bin，再将基因嵌入与 bin 嵌入相加。它保留“哪个基因”和“处于哪个表达区间”，但分箱仍损失分辨率；等宽分箱在某些数据上会让多数值挤入同一 bin。按细胞自适应分箱能改善跨批次语义一致性，却也改变了跨细胞绝对量的解释。

#### 2.3 连续值投影

第三类用线性层或 FFN 直接投影连续表达值，再与基因/位置嵌入结合。它不必离散化，因此理论上保留更多数值信息；但它偏离成熟的离散 token 范式，综述指出其相对性能仍缺少充分比较。TOSICA 还把输出 token 对齐到通路，以换取更直接的生物学解释。

选择时应先问：任务依赖表达秩、绝对量，还是通路级聚合？没有证据表明三类方案中存在跨数据集的统一赢家。

### 3. 注意力能做什么，不能证明什么

若输入 token 对应基因，自注意力令基因 $i$ 的输出成为所有基因 value 投影的加权和：

$$
\mathbf{x}'_i=\sum_{j=1}^{n}a(S)_{ij}W^v\mathbf{x}_j,
$$

其中 $a(S)_{ij}$ 由 query-key 相似度经过 softmax 得到。它使同一基因在不同细胞中获得不同的上下文表示，因而适合描述状态依赖的基因关系。若 token 对应空间中的细胞，则注意力改为建模细胞—细胞关系。

但“注意力矩阵可以画成 GRN”不是“注意力边就是调控边”的证明。多层、多头聚合会进一步削弱可解释性，综述明确援引研究指出 attention score 与特征重要性并不总相关。图 5d 是应用示意，不是 GRN 真实性验证。

计算上，标准注意力对 token 数为 $n$ 时需要 $\mathcal O(n^2)$ 时间与内存。把几千至上万基因作为 token 会成为瓶颈，因此现有模型采用 FlashAttention、Performer、稀疏注意力、迭代注意力或只保留非零基因。效率改进扩大可训练规模，但不会自动解决输入语义、批次效应或评测公平性。

### 4. Encoder、decoder 与训练目标

多数单细胞 Transformer 是 encoder-only，并用 MLM 随机遮盖表达/token 后重建，适合生成上下文化基因或细胞表示，也可将缺失值插补写成类似任务。decoder-only 模型如 tGPT、scMulan 使用 NTP，自回归地生成条件转录组；它适合模拟，但必须赋予表达数据一个序列，并逐 token 生成，成本和顺序假设都更强。scGPT 使用定制 masked attention，处在传统 encoder/decoder 划分之间。

自监督预训练并非必然提升。它在标注有限、未标注细胞多时可能有价值，但综述同时引用独立研究显示，某些任务上 SSL 或大规模 foundation model 没有超过任务专用模型。因此应把“预训练规模大”与“下游生物学泛化已证实”分开。

### 5. 应用版图

- **基因表示与功能**：上下文化基因嵌入用于功能相似性、状态特异作用、染色质状态和网络中心性预测。
- **组学特征交互**：注意力或通路约束用于提出 GRN、增强子—基因或跨模态关系候选，但需要独立实验/统计验证。
- **细胞表示与整合**：CLS 或池化表示支持聚类、批次整合、跨组织/物种映射；过强校正也可能抹去生物信号。
- **扰动预测**：模型尝试预测未见遗传或药物扰动的表达响应；真正困难的是组合扰动、剂量、细胞背景与分布外泛化。
- **模态生成**：从 RNA 预测蛋白/染色质或生成条件细胞状态；生成合理边际分布不等于恢复真实细胞机制。
- **细胞注释**：这是常用基准，但标签本身跨数据集不一致，简单 logistic regression、MLP 或 scTab 等方法有时更强。
- **空间与多模态**：以细胞作为空间 token 或同时编码 RNA、ATAC、蛋白，为组织级建模与多模态 foundation model 提供方向。

### 6. 对 foundation model 主张的批判性结论

综述没有断言 Transformer 已成为单细胞领域的可靠基础模型。它强调：

- 单细胞数据缺少天然序列，输入编码最佳实践尚未收敛。
- 许多工作没有公平调优简单基线，或只在规模有限、任务单一的数据上评估。
- 预训练数据集彼此重叠，测试细胞可能已在训练语料或近邻数据中出现，造成泄漏风险。
- 当前所谓 zero-shot 常受标签映射、数据预处理或任务头训练影响，真正零样本能力仍可疑。
- 参数量、细胞数和任务数不是 foundation capability 的充分证据；跨实验室、组织、物种、疾病和扰动的稳健迁移才更关键。
- attention 可用于提出假设，但不能单独支撑机制解释。

因此，选模型时应优先使用外部数据划分、强而公平的非 Transformer 基线、明确的预训练去重和任务相关生物验证，而不是仅依据模型规模。

### 7. 五幅主图如何串联全文

1. **图 1**：多种单细胞模态经自监督 Transformer 后服务细胞级和基因级任务；它是研究愿景，不是统一实现。
2. **图 2**：对比 autoencoder bottleneck 与 Transformer 的上下文化 token 表示，并拆开多头注意力、Q/K/V 和逐 token FFN。
3. **图 3**：全文最重要的分类图，比较排序、分箱、连续投影，以及 CLS、物种、扰动等 sample/token-level 特殊嵌入。
4. **图 4**：MLM 与 NTP 对应 encoder 插补和 decoder 生成两条训练—应用路径。
5. **图 5**：扰动、整合、细胞/基因任务与 GRN 推断的应用地图；其中 GRN 面板必须结合正文的 attention 解释性警告阅读。

### 8. 研究方向

综述最具建设性的两个方向是：建立覆盖 RNA、表观组、蛋白和空间信息的多模态细胞变异模型；以及用大规模、系统性扰动数据学习可干预的细胞状态空间。二者都需要比“更大 Transformer”更严格的训练数据治理、因果/机制验证和跨域基准。

### 证据边界

- 这是综述型综合，不存在一个统一待复现算法，也没有本地 code evidence。
- companion GitHub 是文献清单，不是论文方法实现，故 metadata 保持 `has_code=false`。
- 论文正文与内嵌补充已通读；五幅主图及其分面均按本地图片目视核对。
- 主要证据：`paper source/paper/vlm/paper.md:15-300`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Transformers in Single-Cell Omics: A Review and New Perspectives

**Authors**: Artur Szalata, Karin Hrovatin, Soren Becker, Alejandro Tejada-Lapuerta, Haotian Cui, Bo Wang, Fabian J. Theis
**Journal**: Nature Methods | **Year**: 2024 | **DOI**: 10.1038/s41592-024-02353-z
**Type**: Perspective/Review
**Companion Resource**: https://github.com/theislab/single-cell-transformer-papers

---

### Review Scope

This perspective article systematically reviews the application of transformer architectures to single-cell omics data, covering ~25 methods from 2022–2024. The review targets researchers at the intersection of machine learning and single-cell biology and critically assesses whether transformers — which have revolutionized NLP, computer vision, and genomics — can similarly transform single-cell analysis. The review covers: (1) transformer architecture adaptations for non-sequential omics data, (2) a survey of existing single-cell transformers by task and architecture, and (3) a candid assessment of current limitations, open problems, and future directions including multimodal foundation models.

---

### Field Landscape

Single-cell omics has enabled granular views of cellular heterogeneity, generating data at unprecedented scale (CZ CELLxGENE: >50M cells). However, existing computational methods — primarily VAE-based autoencoders (scVI, scArches) — cannot fully exploit this data heterogeneity for generalized tasks. Transformers entered the field in 2022 (scBERT, iSEEK), motivated by their success as foundation models in NLP (BERT, GPT), computer vision (ViT), and proteomics (ESM-2, AlphaFold). By mid-2024, >25 transformer models had been proposed for single-cell applications.

**Key turning points**:
- 2022: scBERT, iSEEK — first single-cell transformers with large-scale pretraining
- 2023: Geneformer (Nature) — first therapeutically validated predictions from a single-cell transformer
- 2023: scGPT — multi-task foundation model; tGPT (decoder-only); UCE (650M params)
- 2024: scFoundation (50M cells), GeneCompass (126M cells), CellPLM (spatial), Nicheformer (53M spatial cells)
- 2023–2024: Multiple independent benchmarks show current transformers often outperformed by simpler models

---

### Method Taxonomy

The review organizes single-cell transformers along four dimensions:

#### Dimension 1: Input Encoding (How to Represent Non-Sequential Omics Data)

| Approach | Key Methods | Mechanism | Trade-off |
|---|---|---|---|
| **Ordering** (rank-based) | Geneformer, iSEEK, tGPT | Genes ranked by normalized expression → sequence of tokens | Information loss; reduces to rank |
| **Value categorization** (binning) | scBERT, scGPT | Expression values discretized into bins; each bin has learnable embedding | Reduces resolution; scGPT uses adaptive per-cell binning to mitigate |
| **Value projection** (continuous) | TOSICA, SpaFormer, scFoundation, GeneCompass | Linear projection of expression vector + gene/positional embedding | Continuous embeddings differ from NLP success; resolution preserved |
| **Cells as tokens** | SpaFormer, CellPLM | Input is a tissue; each cell is a token with spatial positional encoding | Captures intercellular relationships; limits gene-level analysis |
| **LLM gene embeddings** | UCE | ESM-2 protein LM generates gene embeddings; expression sampling determines which genes appear | Cross-species without explicit orthology mapping |

#### Dimension 2: Architecture

| Type | Methods | Use Case |
|---|---|---|
| Encoder-only | Geneformer, scBERT, TOSICA, scFoundation, UCE, CellLLM, scCLIP, GeneCompass | MLM pretraining; contextualized gene/cell embeddings |
| Decoder-only | tGPT, scMulan | NTP pretraining; conditional data generation |
| Modified encoder (masked attention) | scGPT | Autoregressive generation within encoder framework |
| Dual encoder | scFoundation, GeneCompass | Separate encoders for different input types/scales |
| Encoder + graph transformer | scMoFormer | Multi-modal integration with graph structure |

#### Dimension 3: Self-Supervised Learning Strategy

| SSL Task | Methods | Mechanism |
|---|---|---|
| **MLM** (masked language modeling) | Geneformer, scBERT, scGPT, scFoundation, SpaFormer, CellPLM, GeneCompass | Mask subset of gene tokens; predict masked values from context |
| **NTP** (next-token prediction) | tGPT, scMulan | Predict next gene in ordered sequence |
| **Contrastive** | CellLLM, scCLIP | Learn similar representations for related cell/modality pairs |
| **No SSL** | TOSICA, scMoFormer | Supervised only; no pretraining |
| **LLM-derived** | GenePT | No training; uses ChatGPT embeddings for gene/cell descriptions |

#### Dimension 4: Application Domain

| Task | Key Methods | Status |
|---|---|---|
| Cell type annotation | scBERT, TOSICA, Geneformer, scGPT, UCE, GeneCompass | Active; but non-transformer scTab outperforms scGPT at cross-organ scale |
| Gene representation | All | Well-established; contextualized embeddings > fixed embeddings |
| Cell representation/batch integration | UCE, GeneCompass, Geneformer | Promising; batch-unaware pretraining shows robustness |
| Perturbation prediction | scGPT, Geneformer, scFoundation, GeneCompass | Early; Geneformer's cardiomyopathy predictions validated experimentally |
| GRN inference | Geneformer, scGPT, tGPT | Via attention scores; but attention ≠ feature importance |
| Spatial omics | SpaFormer, CellPLM, Nicheformer | Rapidly growing; cells-as-tokens models leverage spatial coordinates |
| Multimodal integration | scGPT, scMoFormer, scCLIP, CellPLM | Paired and mosaic integration; scGPT identifies immune subgroups missed by other methods |
| Data generation | tGPT, scMulan, scGPT | Conditional transcriptome simulation; still aspirational at scale |

---

### Key Findings

1. **Architecture adaptations are necessary and diverse**: Single-cell data is non-sequential, requiring special encoding strategies. No consensus on best approach exists as of writing.

2. **Foundation models underperform simple baselines on many tasks**: Independent benchmarks (Boiarsky et al., Kedzierska et al., Liu et al.) consistently show logistic regression and XGBoost often match or outperform current single-cell transformers, even on tasks with minimal labeled data.

3. **Zero-shot generalization is limited**: Despite pretraining on large corpora, zero-shot performance of current models is "questionable" (authors' direct assessment).

4. **Cell type annotation is an unreliable benchmark**: Annotations across datasets are inconsistent; non-transformer scTab outperforms scGPT at large cross-organ scale.

5. **Transformers have unique strengths**: Unlike VAEs, transformers do not require explicit batch covariates to achieve batch robustness in some settings; they produce contextualized gene embeddings; and they enable multi-task use without retraining from scratch.

6. **Benchmarking has systemic flaws**: Comparisons skip hyperparameter tuning of baselines; lack universally recognized metrics for tasks like perturbation prediction; risk dataset leakage due to large pretraining corpora.

---

### Open Problems

1. **Sequentialization**: Non-sequential single-cell data must be artificially ordered for transformers — current solutions are acknowledged as "probably preliminary." The field lacks a principled natural ordering.

2. **Rigorous benchmarking infrastructure**: Need for standardized metrics, public leaderboards, dataset leakage controls, and fair comparison with pretrained baselines.

3. **Multimodal foundation models**: Truly integrating transcriptomics + epigenomics + proteomics + spatial information at scale remains aspirational. Current models use primarily scRNA-seq.

4. **Perturbation landscape modeling**: Future models should pretrain on rich perturbation screens (Perturb-seq) to understand GRNs and enable virtual drug screening.

5. **Attention interpretability**: Attention scores are context-dependent but do not reliably indicate feature importance. Better interpretability methods are needed.

6. **Universal cell simulator**: A generative model conditioned only on cellular characteristics (not requiring input omics data) could revolutionize drug discovery and clinical trial design.

---

### Comprehensive Method Comparison Table

| Method | Year | Journal | Architecture | Input Encoding | SSL Task | Pretraining Scale | Key Application | Limitations |
|---|---|---|---|---|---|---|---|---|
| iSEEK | 2022 | Brief Bioinform | Encoder | Ordering (rank) | MLM | >10M cells, human | Integration | First model; limited task range |
| scBERT | 2022 | Nat Mach Intell | Encoder | Value binning (equal) | MLM | 1M cells, human | Cell annotation | Equal bins → most values in one bin |
| tGPT | 2023 | iScience | Decoder | Ordering (rank) | NTP | 22M cells, cross-species | Generation, clustering | No supervised fine-tuning |
| TOSICA | 2023 | Nat Commun | Encoder | Value projection | None (supervised) | None | Cell annotation, interpretability | No pretraining; pathway-only |
| Geneformer | 2023 | Nature | Encoder | Ordering (rank) | MLM | 30M cells, human | Perturbation, GRN, annotation | Rank ordering loses expression magnitude |
| scGPT | 2024 | Nat Methods | Modified encoder | Value binning (adaptive) | Iterative MLM | 33M cells, human | Multi-task: annotation, perturbation, integration | Outperformed by scTab on cross-organ annotation |
| UCE | 2023 | bioRxiv | Encoder | LLM gene embeddings (ESM-2) | Modified MLM | 36M cells, cross-species | Cross-species integration | Not all genes have protein structures |
| scMoFormer | 2023 | ACM CIKM | Encoder+Graph | SVD-based | None | None | Cross-modality prediction | Limited to supervised setting |
| SpaFormer | 2023 | arXiv | Encoder | Cells-as-tokens, projection | Modified MLM | None | Spatial imputation | No large-scale pretraining |
| scFoundation | 2024 | Nat Methods | Dual encoder | Value projection | Modified MLM | 50M cells, human | Drug response, read depth enhancement | Complex architecture |
| CellLLM | 2023 | arXiv | Encoder | Value binning | Contrastive + MLM | 1.8M cells, human | Disease detection, annotation | Relatively small pretraining |
| scCLIP | 2023 | NeurIPS | Encoder | Value projection | Contrastive | 377K fetal cells | Multimodal RNA+ATAC | Limited pretraining scale |
| GenePT | 2024 | bioRxiv | Closed-source (LLM) | Text description | None | Natural language | Gene function prediction | No molecular data; LLM knowledge limits |
| GeneCompass | 2023 | bioRxiv | Dual encoder | Ordering (rank) | MLM | 126M cells, human+mouse | Cross-species, GRN, annotation | Largest dataset but preprint at writing |
| CellPLM | 2024 | ICLR | Encoder | Cells-as-tokens, projection | Modified MLM+KL | 11M cells, human | Spatial imputation, denoising | Cells-as-tokens limits gene-level analysis |
| scMulan | 2024 | RECOMB | Decoder | Not specified | NTP | Not specified | Multi-task generation | Decoder-only limits bidirectional reasoning |
| Nicheformer | 2024 | bioRxiv | Encoder | Not specified | MLM | 53M spatial cells | Spatial neighborhood prediction | Preprint; no spatial in pretraining claimed |
| Cell2Sentence | 2024 | ICML | LLM (fine-tuned) | Text (gene-ordered) | LLM pretraining | NLP corpus | Text-guided cell analysis | Text-omics gap; evaluation challenges |
| Pathformer | 2024 | Bioinformatics | Encoder | Pathway-grouped | Supervised | None | Disease diagnosis, multi-omics | Pathway-dependent interpretability |
| scHyena | 2023 | arXiv | Hyena (not transformer) | — | SSL | Full-length scRNA-seq | Brain transcriptomics | Non-transformer |
| xTrimoGene | 2024 | NeurIPS | Encoder | — | — | — | Scalable representation | Efficiency focus |
| scTab | 2023 | bioRxiv | Non-transformer | — | — | Large cross-tissue | Cell annotation | Best benchmark on cross-organ annotation |
| SCimilarity | 2023 | bioRxiv | Autoencoder (VAE) | — | Metric learning | Large cross-tissue | Integration, fibrosis macrophages | Non-transformer foundation model |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
