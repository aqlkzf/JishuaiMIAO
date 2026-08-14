---
layout: default
permalink: /paper-atlas/scdrugmap-6cad3584/
title: "scDrugMap"
nav: false
wide: true
description: "scDrugMap 不是一个新的预训练模型，而是一套单细胞药物反应预测基准与应用框架：它把 8 个单细胞基础模型和 2 个通用语言模型放到尽量统一的二分类任务中，比较冻结表征、LoRA 微调和提示预测在“同来源混合数据”与“跨研究数据”上的表现。"
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
      <span>Nature Communications · 2025</span>
    </div>
    <h1>scDrugMap</h1>
    <p>scDrugMap: benchmarking large foundation models for drug response prediction</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/QSong-github/scDrugMap" target="_blank" rel="noopener noreferrer" aria-label="Open code for scDrugMap">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scDrugMap 方法详解：如何公平比较单细胞基础模型的药物反应预测能力

### 一句话定位

scDrugMap 不是一个新的预训练模型，而是一套**单细胞药物反应预测基准与应用框架**：它把 8 个单细胞基础模型和 2 个通用语言模型放到尽量统一的二分类任务中，比较冻结表征、LoRA 微调和提示预测在“同来源混合数据”与“跨研究数据”上的表现。

### 1. 它要解决什么问题？

目标是对每个单细胞转录组预测二元药物反应：

$$
y_i\in\{\text{sensitive},\text{resistant}\}.
$$

论文把响应样本中的细胞标为 sensitive，把不响应样本在治疗前或治疗后采集的细胞标为 resistant（`paper.md:324-327`）。因此，这里的“单细胞标签”实际继承自样本级临床/实验响应，而不是逐细胞直接测得的药敏结果。这是理解任务边界的第一点：模型可能同时学习癌种、研究来源、样本状态和真正的耐药信号。

传统方法已经能做部分工作：

- scDEAL（*Nature Communications*, 2022）把带药物反应标签的 bulk RNA-seq 知识迁移到单细胞；
- DREEP（*BMC Medicine*, 2023）利用药物基因组资源和功能富集估计肿瘤单细胞药物反应；
- DeepDR（*Bioinformatics*, 2024）提供多种编码器、细胞/药物特征和融合模块。

这些方法通常针对特定任务和数据资源设计。scDrugMap 要回答的是另一个问题：已经在数百万细胞上预训练的基础模型，能否用统一的下游头或少量参数微调，获得更强、更可迁移的药物反应表示？论文在 `paper.md:31,173-177` 给出了这一动机。

### 2. 基准包含哪些模型？

| 模型 | 论文中的输入/细胞表示 | 输出维度 | LoRA 目标模块 |
|---|---|---:|---|
| tGPT | 按表达量排序的基因序列；末层序列平均 | 1024 | `c_attn` |
| scBERT | 基因及离散表达；末层序列平均 | 200 | `to_k`, `to_v`, `to_q` |
| Geneformer | 高表达基因排序；Transformer 隐状态 | 256 | `query`, `key`, `value` |
| CellLM | 表达输入；编码器隐状态平均 | 512 | `to_q`, `to_k`, `to_v` |
| scFoundation | `S`、`T`、基因最大池化、基因平均池化拼接 | 3072 | `out_proj` |
| scGPT | 基因、表达和条件信息；`<CLS>` | 512 | `out_proj` |
| CellPLM | 以细胞为 token 的组织级表示；末层输出 | 512 | Q/K/V projection |
| UCE | 统一细胞嵌入；`<CLS>` | 1280 | `out_proj` |
| Llama3-8B | 把高表达基因作为自然语言 token | 4096 | 不微调，只冻结表征 |
| GPT4o-mini | 数据来源 + 每个细胞的高表达基因名 | API 二元回答 | 不微调，提示预测 |

模型细节来自 `paper.md:255-318`。代码快照中的 8 个 scFM 下游 MLP 输入维度和 LoRA 目标与表格一致，但大多数上游模型、权重和嵌入生成脚本不在仓库中。

### 3. 从输入到输出的完整计算框架

```text
带药物响应注释的人类 scRNA-seq 研究
                |
                v
样本响应标签下放到单细胞：sensitive / resistant
                |
                v
论文描述的统一 QC：Seurat、基因数/线粒体比例过滤、PCA、可选 Harmony
                |
                +--------------------------+-------------------------+
                |                          |                         |
                v                          v                         v
         单细胞基础模型                Llama3-8B                GPT4o-mini
       模型特异输入与池化           基因文本化并取隐状态        来源+高表达基因提示
                |                          |                         |
        +-------+-------+                  |                         |
        |               |                  |                         |
        v               v                  v                         v
    冻结模型         LoRA 微调         冻结嵌入+MLP            解析十个二元答案
    预计算嵌入       少量参数更新             |                         |
        |               |                  |                         |
        +-------+-------+------------------+-------------------------+
                |
                v
        sensitive / resistant 预测
                |
                v
   pooled-data 或 cross-data 评估
                |
                v
      F1 / AUROC / Precision / Recall
```

这个框架的关键不是让所有模型内部结构相同，而是让它们面对同一个预测目标，并尽量使用相同的下游分类器和评估维度。模型之间仍然保留不同的词表、序列长度、池化规则、参数规模和预训练数据。

### 4. 数据如何构建？

#### 论文声明

作者检索截至 2024 年的 PubMed 文献，查询式为 `(drug resistance) AND ((single cell) OR (scRNA))`，保留具有药物反应注释的人类数据；外部验证集采用相同策略，重点收集 2024 年 1 月之后的研究（`paper.md:321-324`）。

论文描述的预处理是：

1. Seurat v4.3.0；
2. `nFeature_RNA > 500`；
3. `percent.mt < 10%`；
4. 取前 30 个主成分，以 0.5 分辨率聚类；
5. 对有批次效应的数据使用 Harmony（`paper.md:327`）。

#### 需要保留的矛盾

主数据集一致地报告为 36 个数据集、326,751 个细胞。验证集数字不一致：摘要和方法框架给出 24 个数据集，并由总细胞数 495,237 推出 168,486 个验证细胞；Results 和 Discussion 却写成 17 个数据集、18,856 个细胞（`paper.md:12,34,57,171,324`）。Figure 1d 的横轴和柱长更接近约 168k 的规模，但仅凭图片不能确定精确总数。

#### 代码证据缺口

仓库中没有 Seurat/Harmony 脚本，也没有实现上述 QC 阈值的 R 或 Python 工作流。因此，从 GEO 原始矩阵到各模型 `.npy/.npz` 样本或嵌入文件的过程是 **Not found**，不能根据论文文字反推为“代码已实现”。

### 5. 路线 A：冻结基础模型，只训练 MLP

给定基础模型输出的单细胞表示

$$
\boldsymbol{x}\in\mathbb{R}^{d},
$$

论文使用两层 ReLU 隐层：

$$
\boldsymbol{h}_{1}=\mathrm{ReLU}\left(\boldsymbol{W}_{1}\boldsymbol{x}+\boldsymbol{b}_{1}\right),
$$

$$
\boldsymbol{h}_{2}=\mathrm{ReLU}\left(\boldsymbol{W}_{2}\boldsymbol{h}_{1}+\boldsymbol{b}_{2}\right),
$$

$$
\widehat{\boldsymbol{y}}=\mathrm{Sigmoid}\left(\boldsymbol{W}_{3}\boldsymbol{h}_{2}+\boldsymbol{b}_{3}\right).
$$

其中 $d$ 是模型特异的嵌入维度，$\widehat{\boldsymbol{y}}$ 表示药物敏感概率（`paper.md:207-225`）。

#### 代码确认了什么？

Geneformer 和 scGPT 的 EBD 驱动均实现：

```text
Linear(d,512) -> ReLU -> Linear(512,512) -> ReLU -> Linear(512,2)
```

并使用 AdamW 和 `BCEWithLogitsLoss`（`code/Geneformer/benchmarking_main_EBD.py:11-25,44-68`；`code/scGPT/benchmarking_main_EBD.py:27-59`）。代码返回两个 logits，没有在 `forward` 中显式调用 Sigmoid；Sigmoid 与 BCE 被数值稳定地合并进 `BCEWithLogitsLoss`。

但各 scFM 目录中被导入的 `tool.py` 缺失，所以无法确认计算 F1/AUROC 前，logits 如何被转成最终类别或概率。这一部分只能标为 **Partial**，不能标为端到端 Exact。

### 6. 路线 B：用 LoRA 做参数高效微调

论文把预训练权重分成冻结部分 $\widehat{\boldsymbol{W}}$ 和需要适配的层 $\boldsymbol{W}_{ft}$，并联合训练 MLP 参数 $\Phi_{ft}$：

$$
\boldsymbol{W}^{*}=\arg\min_{\theta_{ft}}
E_{x,y\in D_{ft}}\left[L(\widehat{y},y)\right],
$$

$$
\widehat{y}=scFM_{ft}\left(x;\widehat{\boldsymbol{W}},\Phi_{ft},\boldsymbol{W}_{ft}\right).
$$

LoRA 不直接更新完整矩阵，而是学习低秩增量：

$$
\boldsymbol{W}^{\prime}
=\boldsymbol{W}_{ft}+\Delta\boldsymbol{W}
=\boldsymbol{W}_{ft}+\boldsymbol{A}\boldsymbol{B},
$$

其中 $\boldsymbol{A}\in\mathbb{R}^{d\times r}$、$\boldsymbol{B}\in\mathbb{R}^{r\times k}$，论文设置 $r=8$（`paper.md:228-252`）。

#### 代码确认了什么？

8 个 scFM 的 FT 驱动都设置 `r=8`、`lora_alpha=8`、`lora_dropout=0.05`、`task_type="SEQ_CLS"`，模型特异目标模块也与论文一致。例如：

- Geneformer：`code/Geneformer/benchmarking_main_FT.py:35-73`；
- scGPT：`code/scGPT/benchmarking_main_FT.py:71-104`；
- scFoundation：`code/scFoundation/benchmarking_main_FT.py:47-84`。

scFoundation 代码还明确把最后两个特殊 token 表示、基因最大池化和基因平均池化拼接为 3072 维向量；scGPT 取编码结果的第 0 个 `<CLS>` 表示。

#### 仍未确认什么？

预训练模型代码、权重、词表或加载辅助模块多数缺失，并常指向作者机器上的 `/blue/...` 路径。因此，静态源代码能确认 LoRA 的“设计意图和参数”，但不能确认包装后运行时到底哪些参数保持 `requires_grad=True`，也不能确认每个驱动可成功加载模型。

### 7. 通用语言模型为什么表现较弱？

#### Llama3-8B

论文把高表达基因按表达量排序后作为语言 token，使用冻结的 Llama 表征再训练 MLP（`paper.md:303-306`）。仓库中的 `get_embeds.py` 确实平均最后一层隐状态，但 `dataset_making.py` 会把基因名与表达值拼接，并以最大长度 4096 tokenize（`code/Llama/get_embeds.py:8-16`; `dataset_making.py:29-58`），与论文所述“前 1024 个基因符号”并不完全一致。

#### GPT4o-mini

提示由四段模板、数据来源和基因内容组成：

$$
input=prompt_{pre}+prompt_{source}+source+prompt_{gene}+content+prompt_{post}.
$$

Figure 5 直接展示了任务说明、GEO 来源、基因名和重复三次的输出格式。代码每次发送 10 个细胞，调用 `gpt-4o-mini-2024-07-18`，用正则提取 `{res:...}`，若不是 10 个二元值就丢弃该批次（`code/GPT4/main.py:25-107`）。

这一路线把完整表达谱压缩为少量基因名和研究来源，信息损失很大。论文报告 GPT4o-mini 在大多数类别中的 F1 较低，最好是 liver cancer 的 0.690（`paper.md:117-131`）。代码只找到 top-10 基础提示；论文讨论的 top-100 和 CoT 版本 **Not found**。

### 8. 两种评估场景的本质差别

#### Pooled-data：同一个混合池内划分

多个研究先按 tissue、drug、cancer 或 regimen 合并，再随机划分训练和测试细胞（`paper.md:195-198`）。这种设计回答的是：当训练集已经覆盖相似研究背景时，模型能否区分敏感与耐药细胞？

优点是样本多、训练稳定；风险是同一研究的批次或队列特征可能同时出现在训练和测试中，导致分数偏乐观。Figure 2 中 scFoundation 在绝大多数类别领先，微调结果整体高于冻结表示。

#### Cross-data：按研究隔离

训练来自一个或多个研究，测试来自同类别内完全独立的研究（`paper.md:195-198`）。它更接近真正的跨队列迁移。论文有时把它称为“zero-shot capability”，但要准确理解：下游分类器/LoRA 仍在其他药物反应数据上训练，只是测试研究未参与训练；这不同于完全不训练分类器的纯零样本预测。

Figure 3 显示跨研究性能显著下降，多数 F1 低于 0.8。冻结时 scGPT 在 tumor tissue 最强；微调后 UCE 在多个 tissue、drug 和 regimen 类别更强（`paper.md:86-103`）。所以“最佳模型”会随评估场景变化。

#### 代码能否复现这些划分？

- Llama 路线确实实现 `KFold(n_splits=10, shuffle=True, random_state=42)` 并遍历 10 折（`code/Llama/benchmarking_dataloader.py:57-79`; `benchmarking_main.py:98-123`）。
- 8 个 scFM 的 EBD/FT loader 多数只是 `random_split`，默认 `train_rate=0.8`；Geneformer 代表位置为 `benchmarking_dataloader_EBD.py:38-50` 和 `benchmarking_dataloader_FT.py:40-52`。
- 没有找到所有模型共用的折索引，也没有找到按 study ID 构造 cross-data 训练/测试集的代码。

因此，论文中的共享十折和跨研究协议属于**论文声明，当前快照未验证**。

### 9. 如何读懂结果？

论文以 F1、AUROC、precision 和 recall 为主：

$$
\mathrm{Precision}=\frac{TP}{TP+FP},\qquad
\mathrm{Recall}=\frac{TP}{TP+FN},
$$

$$
F1=\frac{2\times\mathrm{Precision}\times\mathrm{Recall}}
{\mathrm{Precision}+\mathrm{Recall}}.
$$

主要结果应按场景理解：

1. **Pooled-data**：scFoundation 最稳定，微调通常优于冻结；scGPT 在 melanoma 和部分 regimen 上有优势。
2. **Cross-data**：整体分数明显降低；冻结时 scGPT 的部分表示较好，微调时 UCE 更稳。
3. **GPT4o-mini**：仅输入来源和 top genes 的通用语言模型明显落后于单细胞预训练模型。
4. **Validation collection**：在每个数据集内部做 layer-freezing 十折时，scFoundation 再次领先；这不是严格的“新研究零训练”测试。
5. **计算效率**：Figure 7 显示参数量与速度不成简单反比。scFoundation 有 121.2M 参数但图中推理速度最高；UCE 有 849.9M 参数；tGPT 的图示推理时间最长。

### 10. 论文结论、代码事实与分析解释要分开

#### 论文结论

- scFoundation 在 pooled-data 和验证集内部划分上整体最好；
- UCE 在 LoRA cross-data 中整体较强；
- 现有模型的跨研究泛化仍不足，临床转化需要更稳健的方法。

#### 代码直接确认的事实

- 共同的两层 ReLU MLP 形状；
- 8 个 scFM 的嵌入维度、LoRA 超参数和目标模块；
- scFoundation 与 scGPT 的池化实现；
- GPT4o-mini 的 top-10 提示、十细胞分批和输出解析；
- Llama 路线的 10-fold KFold。

#### 分析解释（不是论文原句）

- pooled-data 的高分部分可能来自研究/批次信息同时进入训练和测试；
- Figure 4 中按 cancer type 形成的明显 UMAP 岛提示，药物反应分离可能与癌种/研究来源混杂；
- “最优模型”是数据划分与适配策略的函数，不应只报告单一总排名。

#### 缺失证据

- Seurat/Harmony 预处理和 QC；
- 8 个 scFM 的大多数嵌入生成脚本、上游包和权重；
- 所有模型共用的十折索引；
- study-held-out cross-data 构造；
- top-100/CoT GPT 提示代码；
- Perl/MySQL web server 源码。

### 11. 可复现性判断

当前 GitHub 快照的代码-论文匹配为：Exact 5、Partial 4、Inferred 0、Notebook 0、Not found 5；整体对“分类头和 LoRA 片段”为中等匹配，对“从原始数据到论文结果的端到端复现”为低匹配。启动器还指向不存在的旧目录，并固定调用缺失的 `get_ebd.py`（`launcher.py:5-47`）。

综合评分为 **2/5**：代码足以学习主要实现思路，但不足以独立重建论文报告的十折、跨研究和完整模型结果。本分析没有运行训练或推理。

### 12. 可检验假设（分析者提出，非论文结论）

以下是由证据缺口和图形模式导出的后续实验假设，不应与论文已验证结果混为一谈：

1. 若 pooled-data 使用 group-aware split，按 study 或 patient 隔离，scFoundation 的 F1 可能比随机细胞划分下降更明显。
2. 若将 cancer/study 信息从表示中对抗去除，再评估 Figure 4 的响应分离，部分 UMAP 岛和分类性能可能减弱。
3. 在 cross-data 中加入类别重加权、重采样或以 AUPRC 为优化目标，可能改善论文指出的类别不平衡问题。

验证这些假设需要补齐 study/patient 元数据、原始预处理、共享划分和完整模型资产；当前快照不能直接完成这些实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scDrugMap: Benchmarking Foundation Models For Single-Cell Drug Response

### Problem

Single-cell RNA sequencing can expose heterogeneous treatment response, but its sparsity, dimensionality, batch effects, and study-to-study variation make response prediction difficult. Before scDrugMap, tools such as scDEAL (*Nature Communications*, 2022) transferred bulk drug-response knowledge to single cells, DREEP (*BMC Medicine*, 2023) used pharmacogenomic profiles and functional enrichment, and DeepDR (*Bioinformatics*, 2024) provided many deep-learning configurations. These approaches are task-specific and can require substantial domain-specific training; meanwhile, no broad benchmark had compared recent single-cell foundation models for this task (`paper.md:31,173-177,390-393`).

### Contribution

scDrugMap is a unified **benchmark and access framework**, not a new pretrained model. It compares eight single-cell foundation models (tGPT, scBERT, Geneformer, CellLM, scFoundation, scGPT, CellPLM, UCE) and two general language models (Llama3-8B, GPT4o-mini) for sensitive-versus-resistant classification. It combines curated drug-response datasets, a common downstream MLP, frozen-embedding and LoRA adaptation strategies, prompt-based GPT evaluation, category-stratified results, and command-line/web interfaces (`paper.md:40-57,189-204`).

For frozen scFM representations, a model-specific cell embedding enters a two-hidden-layer ReLU MLP. Fine-tuning injects LoRA adapters with rank 8, alpha 8, dropout 0.05, and model-specific target modules, while jointly training the downstream MLP. GPT4o-mini instead receives the dataset source and top expressed genes for batches of ten cells and returns binary labels (`paper.md:207-252,309-318`).

### Evaluation And Main Findings

The paper evaluates two scenarios:

- **Pooled data:** studies within a tissue/drug/cancer/regimen category are mixed, then cells are split into folds. scFoundation is the most consistently strong model; under fine-tuning it reports mean F1 of 0.947-0.990 across tissue types and leads the three drug classes. scGPT is competitive in melanoma and selected regimens (`paper.md:63-80`).
- **Cross data:** training and test cells come from different studies within the same category. Performance drops substantially, generally below F1 0.8. With frozen embeddings, scGPT is strongest in tumor tissue; after fine-tuning, UCE is strongest across many tissue, drug, and regimen categories (`paper.md:83-103`).

GPT4o-mini is a weak, context-dependent baseline: its best reported mean F1 is 0.690 in liver cancer, but it performs poorly for several other cancers and immunotherapy (`paper.md:117-131`). In the separate validation-collection layer-freezing evaluation, scFoundation again leads most categories (`paper.md:134-148`). Figure 7 adds a practical trade-off view: scFoundation combines a 3072-dimensional embedding with the highest displayed inference speed, UCE is the largest model, and tGPT is the slowest by displayed inference time.

The key conclusion is **scenario-dependent model selection**. Strong pooled performance does not imply transfer to an unseen study; the cross-data experiment is the more relevant test of robustness and changes the preferred fine-tuned model from scFoundation to UCE.

### Important Limitations

1. Pooled cell-level folds can place cells from the same studies in both training and test partitions, making them easier than held-out-study evaluation.
2. Cell labels inherit sample-level sensitive/resistant annotations and may not capture within-sample response heterogeneity.
3. The paper reports that most AUPRC values remain below 0.7 under imbalance, and cross-study F1 is usually below 0.8 (`paper.md:180`).
4. Validation collection sizes are inconsistent: the abstract/method framing implies 24 datasets and 168,486 cells, while Results/Discussion state 17 datasets and 18,856 cells. Figure 1 visually supports the larger scale, but the exact discrepancy is unresolved.
5. UMAP separation is entangled with cancer/study identity and should not be treated as causal evidence of response representation.

### Reproducibility Assessment: 2/5

**What is available.** The GitHub snapshot at commit `72991eb4825dd621dbe9917a266690f37c9f6acc` contains EBD/FT driver and dataloader fragments for the eight scFMs, Llama and GPT4o-mini paths, supplementary metadata spreadsheets, an environment file, and a launcher. Direct source inspection verifies the shared MLP shape, model embedding dimensions, LoRA hyperparameters/targets, scFoundation/scGPT pooling, the GPT prompt path, and Llama's ten-fold KFold implementation.

**What prevents end-to-end reproduction.** Most upstream model packages, checkpoints, metric helpers, and scFM embedding-generation scripts are absent; data/checkpoint paths are author-specific; the launcher points to directories not present in the checkout; and no code was found for Seurat/Harmony preprocessing, common fold indices, held-out-study cross-data construction, or the Perl/MySQL web server. The eight scFM loaders use a single random 80/20 split rather than the paper-described shared ten folds; only Llama contains explicit KFold code. The paper points to a fuller Zenodo archive, but it was not reacquired in this Author phase.

Therefore the snapshot is useful for understanding classifier and adaptation mechanics, but it does not independently reproduce the reported benchmark. No training, inference, or result regeneration was performed in this analysis.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
