---
layout: default
permalink: /paper-atlas/tosica-ad5f4a06/
title: "TOSICA"
nav: false
description: "单细胞参考图谱建好后，常见任务是把已有的细胞类型标签稳定地迁移到新批次或新研究的 query 数据。传统流程往往是降维、聚类、找 marker、人工命名；不同研究会因 marker 和命名标准不同而得到不一致的注释。已有深度模型虽然可自动化，但其隐藏层通常难以回溯到具体的生物过程。TOSICA（Nature Communications, 2023）希望同时给出标签和“为什么是这个标签”的路径/调控子层解释。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>Nature Communications · 2023</span>
    </div>
    <h1>TOSICA</h1>
    <p>Transformer for one stop interpretable cell type annotation</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/JackieHanLab/TOSICA" target="_blank" rel="noopener noreferrer" aria-label="Open code for TOSICA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TOSICA：把细胞类型注释和可解释性放进同一个 Transformer

### 它要解决什么问题？

单细胞参考图谱建好后，常见任务是把已有的细胞类型标签稳定地迁移到新批次或新研究的 query 数据。传统流程往往是降维、聚类、找 marker、人工命名；不同研究会因 marker 和命名标准不同而得到不一致的注释。已有深度模型虽然可自动化，但其隐藏层通常难以回溯到具体的生物过程。TOSICA（Nature Communications, 2023）希望同时给出标签和“为什么是这个标签”的路径/调控子层解释。

### 核心想法

它不把所有基因自由地连接到所有隐藏单元，而是先用通路或 regulon 的先验知识做一个二元掩码 $\mathbf M$。对每个细胞的表达向量 $\boldsymbol e$，只有属于某基因集的基因才可以连接到对应 token：

$$\mathbf W'=\mathbf W*\mathbf M,\qquad \mathbf t=\mathbf W'\boldsymbol e.$$

因此每个 token 可被命名为一个通路或 regulon；重复 $m$ 次后形成 token 矩阵，再加一个可学习 CLS token。CLS 通过多头自注意力收集不同基因集的信息，最后得到细胞类型概率：

$$\mathbf A=\operatorname{softmax}\left(\frac{\mathbf Q\mathbf K^\mathsf T}{\sqrt{d_k}}\right),\qquad
\mathbf p=\operatorname{softmax}(\mathbf W_p\cdot\mathbf{CLS}).$$

论文还把 CLS 指向各 token 的注意力当作细胞的 attention embedding：它既可用于 UMAP/整合，也可排序哪些通路或 regulon 对一个细胞的判别更重要。

```text
带标签参考表达矩阵 + GMT 基因集
        │
        ├─ 构建 gene × gene-set 掩码 M
        ├─ 掩码线性层：基因 -> 可命名 token
        ├─ CLS + 多层多头自注意力
        └─ 输出：细胞类型概率 + CLS-to-token attention embedding

新 query 表达矩阵 + 相同 mask/权重
        └─ 预测标签、置信度、通路/调控子 attention
```

### 代码实际怎样做？

`train.py` 从 GMT 文件生成 mask，过滤连接太少的基因集，并最多保留 `max_gs` 个集合；`customized_linear.py` 在前向和反向都强制 `weight * mask`，所以不允许训练“违背先验”的边。`TOSICA_model.py` 实现 token 嵌入、Q/K/V、自注意力、残差 MLP 和 CLS 分类；它还把各层 attention 做 residual-aware roll-out，提取最终 CLS 到非 CLS token 的权重。`pre.py` 将 query 的预测、概率和 attention 写进 AnnData；若最高 softmax 概率低于默认 0.1，就标作 `Unknown`。

这里有两个容易混淆的解释量：CLS-to-pathway attention 是模型对 token 的注意力嵌入；导出的 `gene2token_weights.csv` 则是掩码嵌入层权重在 embedding 维度上的绝对值最大值。两者回答的问题不同，不能互换。

### 论文评估说明了什么？

图 2 报告六个数据集上 19 种方法的比较，TOSICA 的平均准确率为 86.69%；图中 mAtlas 的 reference/query attention-UMAP 让同类细胞聚集，并显示相对稳定的运行时间。图 3 用 regulon attention 区分胰腺细胞状态、构建软骨细胞伪时序；图 4 和图 5 将这种解释扩展到泛癌髓系细胞及 COVID-19/SLE 免疫细胞，展示通路或 TF attention 与亚群、疾病过程的关联。

这些结果支持“注释 + 可解释 embedding”的工作流，但注意力或相关性本身不是因果调控证据。

### 可复现边界

代码与论文的主模型、损失、SGD/余弦调度和 query 阈值高度对应；但发布快照的 `splitDataSet()` 在类别平衡后随机做 70:30 训练/验证划分，而论文的评估叙述强调按研究或生物状态分割。公开快照有 tutorial 和 Fig. 4 notebook，却没有打包的全量 benchmark 数据、下载步骤和所有作图脚本；因此，完整复现论文数字和补图仍需要外部数据与额外流程。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TOSICA

TOSICA (Transformer for One-Stop Interpretable Cell-type Annotation) addresses supervised reference-to-query annotation when standard marker/manual workflows are slow and deep latent models lose a direct biological interpretation. It replaces an unconstrained first projection with a fixed gene-to-pathway/regulon mask, uses a Transformer CLS token to classify cells, and exposes CLS-to-token attention as an embedding for integration, subtype, and trajectory analyses.

The paper evaluated six labelled datasets—human artery, bone, pancreas, mouse brain, pancreas, and atlas—against 18 other annotators. It reports the highest mean accuracy (86.69% across 19 methods), mAtlas query accuracy of 81.06%, and attention-embedding analyses of pancreas, osteoarthritis, pan-cancer myeloid cells, and COVID-19/SLE immune cells (paper lines 44–99, 102–169; Figs. 2–5).

The released repository at commit `0aa2b32f7a413105165298baeb414db332390776` has a high-fidelity match for the masked linear embedding, Transformer attention, CLS classification, attention roll-out, cross-entropy training, SGD/cosine optimization, and thresholded query prediction. Important differences/gaps are documented: the released training code makes a balanced random 70:30 split rather than the paper's study/state-oriented split, defaults to 10 epochs, and does not package all paper datasets or a full end-to-end benchmark/figure reproduction pipeline. Five main figures and the complete Nature HTML paper are locally available; supplementary material was not acquired separately.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
