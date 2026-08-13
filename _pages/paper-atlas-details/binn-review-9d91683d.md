---
layout: default
permalink: /paper-atlas/binn-review-9d91683d/
title: "BINN_review"
nav: false
description: "这是一篇两页的短篇观点型综述，而不是系统综述或新方法论文。它用一张架构图和十条参考文献说明 biologically informed neural networks（BINNs）的基本思想、代表应用与研究缺口。文章没有新数据、实验、方程、代码或性能基准，因此应把“BINN 往往表现更好”等表述理解为作者对已有文献的选择性综合，而不是本文重新验证的结论。 普通全连接神经网络的隐藏节点没有预先指定的生物含义。"
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
      <span>Nature Reviews Genetics · 2025</span>
    </div>
    <h1>BINN_review</h1>
    <p>Beyond the black box with biologically informed neural networks</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41576-025-00826-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for BINN_review">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 生物学信息神经网络（BINN）中文综述解读

### 这篇文章是什么

这是一篇两页的短篇观点型综述，而不是系统综述或新方法论文。它用一张架构图和十条参考文献说明 biologically informed neural networks（BINNs）的基本思想、代表应用与研究缺口。文章没有新数据、实验、方程、代码或性能基准，因此应把“BINN 往往表现更好”等表述理解为作者对已有文献的选择性综合，而不是本文重新验证的结论。

### 从黑箱到结构可见

普通全连接神经网络的隐藏节点没有预先指定的生物含义。BINN 则把 Reactome、Gene Ontology 或 KEGG 等数据库的层级直接变成网络结构：

$$
\text{omics features}\rightarrow\text{genes}\rightarrow\text{pathways}\rightarrow\text{processes}\rightarrow\text{prediction}.
$$

一个基因只有在数据库声明它属于某通路时，才连接到该通路节点。于是隐藏节点不再是任意编号，而对应实际基因、通路或生物过程。这种解释性发生在训练之前，所以称为 ante-hoc interpretability；它与训练完黑箱后再用 SHAP/LIME 解释输入贡献不同。

不过，“节点有生物学名称”不等于“模型学到了因果机制”。数据库关系可能不完整，节点激活仍受数据、损失和优化影响，通路相关性也可能只是预测关联。

### 多组学如何进入同一网络

文章强调先选择共同实体，通常是 gene：

- mutation 或 copy-number variation 映射到发生异常的基因；
- 多个 transcript 或 protein 可映射到同一基因；
- metabolite 可映射到产生或使用它的酶编码基因；
- 图 1 还明确画出 epigenomics；
- clinical data 等不能直接连到通路本体的变量，可在后部 late fusion，或通过 dummy pathways 接入。

共同基因层使不同模态共享后续通路层级，但文章没有规定聚合、标准化、缺失值或冲突映射的处理方式。这些是具体模型必须另行解决的工程选择。

### 不均匀和不完整的本体怎样处理

现实本体不是整齐的逐层树：有些基因没有中间层通路，有些知识根本未被收录。图 1 展示三种补救：

1. **skip connection**：跨过缺失的中间层；
2. **dummy node/pathway**：人为补齐结构或容纳不可映射输入；
3. **fully connected residual nodes**：增加不受本体约束的分支，学习数据库遗漏的关系。

这里存在关键权衡。纯本体约束让解释路径最清楚，却可能漏掉新生物学；残差容量能提高灵活性，却把黑箱重新带回模型。因此评估时需要报告结构化分支与残差分支各自的贡献。

### 文章覆盖的应用类型

- P-Net：用分子特征对接前列腺癌治疗相关结局。
- DrugCell：联合基因组与药物化学结构预测药物反应和协同作用。
- Hao et al.：整合基因组与临床数据做癌症生存分析。
- VEGA：把生物知识放进变分自编码器，做无监督单细胞网络活动推断。
- PathExpSurv：将生存预测与通路扩展、疾病基因发现联系起来。
- van Hilten et al. 与 Nguyen et al.：分别代表多队列多组学表型预测和多模态融合研究。

本文只用这些工作说明应用版图，没有提供足以复现其架构或比较其性能的细节。具体模型层数、损失、数据集和代码必须回到各自原论文。

### 为什么 BINN 可能适合小样本多组学

作者的逻辑是：本体约束减少可学习连接和参数，缩小假设空间；对“特征多、样本少”的组学数据，这可能降低过拟合，并让预测沿着生物路径解释。但目前有三个因素纠缠在一起：

1. 真实生物知识带来的 inductive bias；
2. 稀疏连接本身带来的正则化；
3. 基因层与 late fusion 带来的多模态融合优势。

如果不做消融，就无法知道性能提升来自哪一项。一个合理但尚未由本文完成的验证，应比较真实本体、保持相同稀疏度的打乱本体、普通稀疏网络、密集网络和不同融合策略。

### 五个研究议程

1. 建立共同 benchmark 和工具，提高可复现性与可比性。
2. 用更全面的评估与消融解释性能来源，并与 GNN 和经典机器学习比较。
3. 设计可接纳多种生物知识和融合方式的灵活架构。
4. 将 BINN 与 neural architecture search 结合，用于提出新的通路关系假设。
5. 围绕具体任务系统比较知识库与本体层级选择。

### 图 1 怎么读

从左到右依次是四类 omics、gene layer、pathway layer、process layer、两层 residual nodes 和 output。虚线表示 skip connection，通路数据库从下方定义黄色和红色层的结构，clinical data 在灰色残差层处 late fusion。图中节点数量和层宽只是示意，不能当作推荐超参数；单一 output 也不表示 BINN 只能做单任务。

### 证据边界

- 本地全文和唯一主图均已核验。
- 未发现补充材料；文章本身也没有补充材料引用。
- 这是 paper-only review，没有本地或公开代码需要分析。
- 工作区旧有 `.codegraph` 和 `CLAUDE.md` 是普通合同回填遗留，不构成代码证据；reviewerpaper 合同不使用它们。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Beyond the black box with biologically informed neural networks

### Review scope

Selby et al. present a two-page perspective-style review of biologically informed neural networks (BINNs) for multi-omics analysis. It is not a systematic review: there is no search strategy, inclusion flow, meta-analysis, benchmark, or supplementary material, and the bibliography contains ten references. Its contribution is a compact architectural argument, a selective application landscape, and a five-part research agenda.

### Field landscape

BINNs replace arbitrary dense hidden layers with nodes and edges derived from biological knowledge. Nodes represent entities such as genes, pathways and higher-order processes; edges encode relationships from Reactome, Gene Ontology or KEGG. This makes the architecture itself interpretable before training (ante hoc), rather than explaining an unconstrained network only after training.

The review positions BINNs between three needs common in omics:

1. high-dimensional features with relatively few samples;
2. integration of heterogeneous genomic, transcriptomic, proteomic, epigenomic or metabolomic inputs;
3. predictions that can be traced back to genes or pathways.

The authors argue that ontology-constrained sparsity reduces parameters and training-data demand, while the biological hierarchy supplies inductive bias. They also explicitly acknowledge that current evidence does not disentangle biological priors from sparsity or data-fusion effects.

### Architectural taxonomy

| Component | Source of structure | Role | Main caveat |
|---|---|---|---|
| Omics-to-gene mapping | Known feature–gene mappings | Harmonizes modalities at a common entity | Some inputs do not map uniquely to genes |
| Gene-to-pathway/process hierarchy | Reactome, GO, KEGG or another ontology | Supplies sparse, interpretable hidden layers | Inherits omissions and biases of the database |
| Skip connections or dummy nodes | Architecture design | Handles uneven ontology depth | Can complicate a clean layerwise interpretation |
| Fully connected residual nodes | Learned without ontology constraints | Captures relationships absent from the prior | Reintroduces opaque capacity |
| Late fusion or dummy pathways | Architecture design | Adds clinical or non-pathway-linkable data | Interpretation differs from the constrained branch |
| Biologically informed VAE | Gene sets/pathways in a generative model | Enables unsupervised single-cell analysis | Evidence is represented by one cited example, VEGA |

### Representative applications cited by the review

| Reference | Task represented in this article | What the review uses it to illustrate |
|---|---|---|
| van Hilten et al. (2024) | Multi-cohort, multi-omics phenotype prediction | Visible/interpretable neural networks across cohorts |
| Kuenzi et al. / DrugCell (2020) | Drug response and synergy | Combining genomic and chemical-structure inputs |
| Elmarakeby et al. / P-Net (2021) | Prostate cancer discovery | Aligning molecular features with therapeutic outcomes |
| Hao et al. (2019) | Cancer survival | Combining genomic and clinical data |
| Seninge et al. / VEGA (2021) | Single-cell network activity | Unsupervised, biologically informed variational autoencoding |
| Hou et al. / PathExpSurv (2023) | Survival and disease-gene discovery | Using BINNs as hypothesis-generating models |
| Nguyen et al. (2024) | Cancer drug response | Exploring multimodal fusion strategies |

The article does not provide enough detail to compare implementations, datasets, effect sizes or code quality. Claims of comparable or better performance than dense networks are narrative synthesis, not a new head-to-head evaluation.

### Main conclusions

- BINNs make biological knowledge an architectural constraint, giving hidden nodes predefined biological meaning.
- A common gene layer can align several omics modalities; clinical or otherwise unmappable data can enter later.
- Constrained connectivity may help in small, high-dimensional settings by reducing the hypothesis space.
- Intrinsic interpretability is attractive for biomarker discovery and target validation, but a biologically named node is not automatically a causal mechanism.
- The field lacks standardized tools, common benchmarks, broad cross-domain tests, and decisive ablations.

### Open problems stated by the authors

1. **Standardization:** common benchmarks and tools for reproducibility and comparison.
2. **Rigorous evaluation:** ablations that separate ontology information, sparsity and fusion, plus comparison with GNNs and classical machine learning.
3. **Flexible architectures:** support for varied biological knowledge and multimodal fusion.
4. **Hypothesis generation:** combining BINNs with neural architecture search to propose new pathway relationships.
5. **Focus on the core:** systematically test database choice and hierarchy depth for each application.

### Evidence boundary

This article is a short expert perspective. It has one conceptual figure, ten references and no supplement, equations, datasets, experiments, code repository or executable workflow of its own. The article reviews implementations but is not evidence that those implementations were locally audited or reproduced.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
