---
layout: default
permalink: /paper-atlas/scgraphformer-017e5cd5/
title: "scGraphformer"
nav: false
description: "单细胞 RNA 测序的细胞类型注释常先用 kNN 把细胞连成一张固定图，再做图神经网络传播。但 kNN 只保留局部邻居：远距离却生物学相关的细胞可能被遗漏，错误邻居也会成为先验。scGraphformer 的目标是从表达数据中学习所有细胞之间的关联，同时仍允许把 kNN 图作为可选的辅助信息，而不是强制依赖它。 输入是细胞×基因矩阵。论文先做质控、归一化和高变基因选择，得到 \\hat X；每个细胞是一行特征，标签用于监督训练。"
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
      <span>Communications Biology · 2024</span>
    </div>
    <h1>scGraphformer</h1>
    <p>scGraphformer: unveiling cellular heterogeneity and interactions in scRNA-seq data using a scalable graph transformer network</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/xyfan22/scGraphformer" target="_blank" rel="noopener noreferrer" aria-label="Open code for scGraphformer">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scGraphformer：用可扩展图 Transformer 注释单细胞

### 它要解决什么问题？

单细胞 RNA 测序的细胞类型注释常先用 kNN 把细胞连成一张固定图，再做图神经网络传播。但 kNN 只保留局部邻居：远距离却生物学相关的细胞可能被遗漏，错误邻居也会成为先验。scGraphformer 的目标是从表达数据中学习所有细胞之间的关联，同时仍允许把 kNN 图作为可选的辅助信息，而不是强制依赖它（`paper.md:36-56,192-195`）。

### 输入、输出与主流程

输入是细胞×基因矩阵。论文先做质控、归一化和高变基因选择，得到 $\hat X$；每个细胞是一行特征，标签用于监督训练。输出则是每个细胞属于各候选类型的 logits，最后用交叉熵学习。

```text
scRNA-seq 计数矩阵
  -> 归一化、log1p、高变基因
  -> MLP 得到细胞表示
  -> 多层 scGraphformer
       -> 所有细胞的线性化注意力
       -> （可选）kNN 图上的 GCN 聚合
       -> 残差混合
  -> MLP 分类头 -> 细胞类型
```

这里最重要的变化是：模型并不只沿预定义边传消息，而是让每个细胞根据 Query、Key、Value 与全体细胞交换信息。

### 为什么它能处理大规模数据？

普通全注意力会显式计算每对细胞的分数，$N$ 个细胞需要 $O(N^2)$ 的成本。论文先写出标准 Q/K/V：

$$q_u^{(k)}=W_Qz_u^{(k)},\quad k_u^{(k)}=W_Kz_u^{(k)},\quad v_u^{(k)}=W_Vz_u^{(k)}.$$

随后把指数注意力做一阶近似，并归一化 $Q,K$，从而把计算改写成共享的 $\hat K^\top V$、$\sum_jv_j$ 等聚合量：

$$Z^{(k+1)}=\frac{V^{(k)}+(\hat K^{(k)}(V^{(k)})^\top)\hat Q^{(k)}}{N+(\hat Q^{(k)})^\top\hat K^{(k)}}.$$

直观地说，先把“全体细胞提供的信息”压缩为少数统计量，再让每个 query 细胞读取它，因此不必保存完整 $N\times N$ softmax 矩阵。论文据此把主要注意力计算从二次量级降到线性量级（`paper.md:231-255`）。本地实现确实用 `einsum` 计算这些聚合和归一化（`utils/scGraphformer.py:10-46`）。

### kNN 图在这里到底做什么？

如果已有可信图，模型可加入

$$D^{-1/2}\mathcal GD^{-1/2}V$$

形式的 GCN 聚合，再和注意力输出相加。它是补充，而不是主干：代码中只有打开 `--use_knn` 才构图，只有 `--use_graph` 才把 GCN 项加入（`utils/dataset.py:105-134`; `utils/scGraphformer.py:103-108`）。因此，“不需要 kNN”不是说无法使用邻接信息，而是说模型的全局关系学习不以固定 kNN 为前提。

### 训练和结果应怎样理解？

本地 `main.py` 用 Adam 和交叉熵训练，并可导出每层注意力矩阵（`main.py:89-145,167-191`）。论文在 20 个同数据集任务、跨平台 PBMCBench、鼠脑转移和百万细胞级图谱上比较多种方法；例如报告 Zeisel→Rosenberg 的平均准确率为 95.210%，COVID atlas 为 76.05%（`paper.md:105-145`）。

最后要区分两件事：注意力热图可提出“哪些细胞可能相关”的假设，图 6 还以谱系和 marker 表达做了支持；但注意力权重本身不是因果互作证据。当前快照也没有论文使用的处理后数据、完整绘图脚本或 Figshare 存档对照，所以完整复现仍是开放边界。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scGraphformer

scGraphformer addresses supervised cell-type annotation from scRNA-seq data when a fixed kNN graph may miss long-range or subtle cell relationships. It represents cells by normalized/HVG expression features, applies a graph-transformer layer with linearized global Q/K/V attention, optionally adds kNN-based GCN aggregation, and predicts labels with a residual MLP classifier.

The paper compares scGraphformer with CellTypist, scVI, scmap, ACTINN, scBalance, scBERT, TOSICA, and scType across intra-dataset, cross-platform, and large-atlas settings. Its reported examples include 95.210% mean accuracy for Zeisel-to-Rosenberg annotation and a 76.05% COVID atlas accuracy versus 72.5% for CellTypist; Figure 5 also presents runtime comparisons. These are paper-reported results, not rerun results in this workspace.

Reproducibility is **partial**. The paper explicitly links the authors' GitHub repository, and the acquired snapshot at commit `75c76fc6b66195297a764d6e4569b3c01e084538` contains preprocessing, model, training, evaluation, and attention-export code. Direct source evidence confirms the main algorithm at medium paper-code fidelity. However, this snapshot lacks the processed benchmark data, paper-wide run configurations, figure scripts, and a local comparison against the separately mentioned Figshare deposit; therefore full benchmark and figure reproduction is not verified.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
