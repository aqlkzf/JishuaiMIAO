---
layout: default
permalink: /paper-atlas/fundamental-limitations-of-foundation-models-in-single-cell-tran-a9f0e7bf/
title: "Fundamental_Limitations_of_Foundation_Models_in_Single_Cell_Transcriptomics"
nav: false
wide: true
description: "这是一项比较性基准研究，不是提出一个新的基础模型。作者比较 scGPT、SCMAMBA-2 和 Geneformer 在细胞类型分类中的表现，并把 Seurat v5 作为统计学基线。核心问题有三个：预训练模型的嵌入是否比传统方法更好；输入受到噪声时模型是否稳健；微调数据的类别不平衡是否会让预测偏向多数类（论文第 1 节和第 2 节，行 24-50）。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>Fundamental_Limitations_of_Foundation_Models_in_Single_Cell_Transcriptomics</h1>
    <p>Fundamental Limitations of Foundation Models in Single-Cell Transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 单细胞转录组基础模型的局限：方法解读

### 这篇论文要回答什么问题？

这是一项比较性基准研究，不是提出一个新的基础模型。作者比较 scGPT、SCMAMBA-2 和 Geneformer 在细胞类型分类中的表现，并把 Seurat v5 作为统计学基线。核心问题有三个：预训练模型的嵌入是否比传统方法更好；输入受到噪声时模型是否稳健；微调数据的类别不平衡是否会让预测偏向多数类（论文第 1 节和第 2 节，行 24-50）。

### 被比较的模型与编码方式

- **scGPT**：Transformer，在约 3300 万个非癌单细胞转录组上以 masked-gene prediction 预训练；使用 bin-based tokenization。
- **SCMAMBA-2**：结构化状态空间模型，前向和反向两个 SSM 头的输出取平均；使用与 scGPT 相同的 bin-based tokenization。
- **Geneformer**：Transformer，在约 3000 万个非恶性细胞上预训练；使用 rank-value encoding，把基因按归一化表达排序。

论文报告 scGPT 约 5100 万个可训练参数、SCMAMBA-2 约 6000 万个，Geneformer 比前两者分别少约 40% 和 50%（行 41-50）。这些规模和架构来自论文；

#### Bin-based tokenization

scGPT 和 SCMAMBA-2 对每个细胞中的基因位置组合三种信息：基因身份 token、表达量 bin、condition token。论文描述的流程是：先对原始计数做对数变换，在细胞内排序，再离散为 50 个等宽 bin。三个 embedding 按位置逐元素相加，形成输入序列，再送入模型编码器（行 59-77）。

#### Rank-value encoding

Geneformer 的流程是：

1. 在 Genecorpus-30M 中为每个基因计算非零表达的全局中位数；
2. 对新细胞按总转录本数做归一化，再用全局因子调整每个基因的表达；
3. 按调整后的表达值排序，把基因 token 按从高到低排列成序列（行 80-83）。

直观地说，bin-based 方法把表达值压进有限的离散区间，rank-value 方法保留细胞内相对次序，同时引入训练语料的全局表达背景。作者据此推测，后者更容易保留上调/下调等生物学关系（行 168-171）。

**公式状态：Not found。** 转换后的 `paper.md` 没有保留三种 embedding 相加的完整公式、Geneformer 的全局中位数与排序公式，也没有宏平均公式。搜索范围包括完整 195 行 `paper.md` 的 Methods 行 27-112、Results 行 115-171，以及对应的文章 HTML；这里只保留论文中仍可读的变量名和文字步骤，不自行补写公式。

### 实验计算流程

```text
单细胞表达矩阵 + 细胞类型标签
              |
              v
log 归一化、混杂因素校正、高变基因选择
              |
              +-----------------------------+
              |                             |
              v                             v
       无噪声数据上微调                 测试数据
              |                       在比例 n 的数据上
              |                       加入 Gaussian noise
              |                             |
              +----------> 模型专属 tokenization
                                           |
                                           v
                                  foundation-model embedding
                                           |
                                           v
                                  相同功能的分类头
                                           |
                                           v
                            分类指标 + 噪声曲线 + 类别计数
```

#### 数据与预处理

作者使用 hPancreas 和肿瘤浸润 Myeloid 数据集；结果段落给出的规模约为 14.8k 和 13.2k 个细胞（行 86-99、121）。预处理包括 log normalization、混杂因素校正和高变基因选择，然后才进行 tokenization。数据划分、过滤阈值、协变量、软件版本和保留的基因数没有报告。

#### 微调与基线

预训练模型先产生 embedding，再送入功能上相同的分类头；与 Seurat v5 比较 accuracy、macro precision、macro recall 和 macro F1（行 112、118-124）。模型在 RTX6000 上微调相同步数，但论文同时说步数取决于训练集；学习率、batch size、优化器、随机种子和分类头结构均为 **Not found**。

#### 测试时噪声

在推理时固定已经微调的权重，把标准差设为数据集中非零计数的中位数，并在测试数据的不同百分比上加入 Gaussian noise，再重新 tokenization（行 100-109）。论文正文写到 10%-100%，而 Figure 2/3 的横轴只显示 0-80%；这一差异应保留，不能假定缺失的 90%-100% 曲线。

30% 被作者称为关键阈值，因为 PCA 中的簇完整性据称在此处破坏，统计基线也在此处失败。但本地四张图没有 PCA 图，也没有簇完整性的定量结果。

#### 采样偏差分析

作者把每个类别的真实细胞数与预测细胞数并列。Figure 4 中 Pancreas 的分布总体较稳定；Myeloid 中 SCMAMBA-2 明显过预测 Mono_CD14，Geneformer 明显过预测 Macro_SPP1。图像能直接证明预测分布发生偏移，但“过拟合”或“训练不确定性”仍是作者的解释，不能仅凭柱状图确定因果关系（行 156-165）。

### 主要结果怎样理解？

Figure 1 显示 Seurat v5 在两个展示的数据集和四类指标上都领先。Geneformer 通常是三个基础模型中最强者，尽管参数更少。Figure 2（Pancreas 的 accuracy、precision、recall）和 Figure 3（Myeloid 的 accuracy）显示，Geneformer 在中等噪声区间通常下降更慢；SCMAMBA-2 在 Myeloid 上尤其快地降到低平台。Figure 4 则显示类别不平衡与多数类偏置同时出现。

作者把这些现象归因于 rank-value encoding 的全局基因归一化，认为 50-bin 离散化可能丢失细粒度表达信息。但三种模型的架构、预训练语料、参数量、训练目标和实现同时不同，所以实验支持的是“编码方式值得进一步做受控消融”的假设，而不是已经证明 tokenization 单独造成性能差异。

### 可复现性与已知缺口

精确公式、第三个数据集（论文有时声称使用三个数据集但只列出两个）、数据划分、超参数、随机性、噪声实现细节、Seurat 设置、误差条和显著性检验均为 **Not found**。因此可以复述和学习这套实验设计及其图像证据，但不能从当前材料运行完全相同的实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Fundamental Limitations of Foundation Models in Single-Cell Transcriptomics

### Problem

Single-cell foundation models are pretrained on millions of transcriptomes with the expectation that their embeddings will transfer well to downstream biological tasks, including in low-data or noisy settings. This 2025 bioRxiv benchmark asks whether that expectation holds for cell-type annotation and whether common tokenization strategies preserve enough biological context.

The compared models span scGPT (*Nature Methods*, 2024), SCMAMBA-2 (bioRxiv preprint, 2024), and Geneformer (*Nature*, 2023). Their scale does not guarantee a fair or informative representation: scGPT and SCMAMBA-2 discretize expression into 50 bins, whereas Geneformer ranks genes after normalization by corpus-wide expression. The paper argues that compression during tokenization and class imbalance during fine-tuning can erase or distort biologically meaningful signals.

### Benchmark design

This is a comparative study, not a new model. The authors preprocess hPancreas and tumor-infiltrating Myeloid expression data, fine-tune the three pretrained models for cell-type classification with functionally identical heads, and compare them with Seurat v5. They evaluate accuracy and macro precision, recall, and F1. To stress tokenization, they add Gaussian noise before tokenization to an increasing fraction of test data while keeping model weights fixed. They also compare true and predicted class counts to examine sampling bias.

The core pipeline is:

```text
scRNA-seq counts -> preprocessing -> model-specific tokenization
                -> pretrained embedding -> classification head
                -> metrics, noise curves, and class-count distributions
```

### Main findings

- Figure 1 shows Seurat v5 leading every model on both displayed datasets and all four metrics. Geneformer is generally the strongest foundation model despite having about 40% fewer trainable parameters than scGPT.
- Figures 2 and 3 show that all models deteriorate under pre-tokenization Gaussian noise. Geneformer retains higher performance through most of the moderate-noise range, while scGPT and especially SCMAMBA-2 often decline more sharply.
- Figure 4 shows relatively stable Pancreas class distributions but pronounced Myeloid skew. SCMAMBA-2 heavily overpredicts the abundant Mono_CD14 class; Geneformer overpredicts Macro_SPP1 and cDC2_CD1C.
- The authors attribute Geneformer's relative robustness to rank-value encoding with a global gene normalization factor, and argue that 50-bin encodings can obscure subtle expression relationships.

The final attribution should be read as a hypothesis supported by the benchmark, not a clean causal ablation. Architecture, pretraining corpus, parameter count, and implementation vary together with tokenization. The images establish comparative point-estimate patterns but contain no error bars or replicate distributions.

### Source inconsistencies and limitations

The abstract says Seurat exceeds Geneformer by 9% in accuracy, while Results says approximately 15%; the aggregation behind either figure is not specified. Methods and Discussion refer to three datasets but identify only hPancreas and Myeloid. The perturbation prose describes testing through 100%, whereas Figures 2 and 3 stop at 80%.

Exact equations are **Not found** in the converted paper: the bin-embedding sum, Geneformer normalization/ranking formulas, and macro-averaging formula are introduced but their rendered expressions are missing. Exact dataset splits, classifier-head architecture, hyperparameters, random seeds, replicate counts, uncertainty estimates, perturbation pseudocode, negative-value handling, Seurat settings, and PCA evidence for the 30% threshold are also not reported in the available local evidence.

### Reproducibility

**Reproducibility rating: 1/5.** The conceptual benchmark is understandable, and four main figures are available locally, but no official paper-linked code repository, runnable scripts, environment, processed dataset bundle, or supplementary methods were found. The acquisition manifest and GitHub-link sidecar contain no repository URL. Consequently, there is no code-paper match to assess and no implementation behavior can be verified.

The strongest supported conclusion is descriptive: in these two displayed datasets, larger pretrained single-cell models did not outperform Seurat v5, Geneformer was relatively more robust to moderate input noise, and class imbalance coincided with prediction skew. Stronger claims that rank-value tokenization itself causes the advantage require controlled ablations and reproducible implementations.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
