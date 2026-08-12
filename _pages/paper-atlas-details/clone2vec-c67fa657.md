---
layout: default
permalink: /paper-atlas/clone2vec-c67fa657/
title: "clone2vec"
nav: false
description: "这篇工作关注的是带有谱系追踪信息的单细胞转录组数据。难点在于，大多数 clone 只被观测到很少几个细胞，而且 clone 大小分布很不均匀，所以如果直接用细胞类型比例、层次聚类，或者 OT / MMD 这类分布距离去比较 clone，经常会很不稳定。作者想要的是一种不依赖人工细胞类型标签、又能在稀疏采样下稳定描述 clone 行为差异的方法。"
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
      <span>Representation Models</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>clone2vec</h1>
    <p>Clonal embeddings allow exploratory analysis of lineage-resolved single-cell data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2026.04.30.720820" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## clone2vec 方法解读

### 这篇论文想解决什么问题

这篇工作关注的是带有谱系追踪信息的单细胞转录组数据。难点在于，大多数 clone 只被观测到很少几个细胞，而且 clone 大小分布很不均匀，所以如果直接用细胞类型比例、层次聚类，或者 OT / MMD 这类分布距离去比较 clone，经常会很不稳定（`paper.md:39-50`）。作者想要的是一种不依赖人工细胞类型标签、又能在稀疏采样下稳定描述 clone 行为差异的方法。

### clone2vec 的核心想法

clone2vec 的核心不是先把 clone 压成“某几类细胞占比”，而是先在细胞表达空间里看局部邻域，再问：“一个 clone 的细胞，周围通常会和哪些 clone 的细胞出现在一起？”作者把这种“邻域共现”统计成一个 clone-by-clone 矩阵，然后再学习一个低维 clone embedding（`paper.md:42-47`, `paper.md:220-238`）。

可以把它理解成：

```text
细胞表达空间里的局部邻近关系
    -> clone 之间的邻域共现计数
    -> clone 的低维向量表示
```

所以 clone2vec 比较的不是离散标签，而是 clone 在连续表达流形上的“邻域语义”。

### 计算流程

```text
单细胞 AnnData + 每个细胞的 clone 标签 + 已经做好的表达嵌入
    -> 构造 clone-level AnnData
    -> 在细胞表达嵌入上建 kNN 图
    -> 统计每个 clone 在邻域里遇到其他 clone 的次数
    -> 得到 C x C 的 clone 共现矩阵
    -> 用 Skip-Gram 风格的多项式分解学习低维 clone embedding
    -> 再做聚类、原型分析、基因关联、跨数据集对齐
```

### 代码里各步是怎么落地的

#### 1. clone 级输入准备

`clone2vec/preprocessing.py:24-127` 里的 `clones_adata` 会把 cell-level 数据变成 clone-level `AnnData`。它会：

- 过滤太小的 clone；
- 保存每个 clone 的细胞数；
- 在 `.layers['counts']` 和 `.layers['proportions']` 里保存 clone 组成。

这一步对应论文里“需要一个细胞表达嵌入和一组平铺的 clone 标签”的前提（`paper.md:223-226`）。

#### 2. 在表达空间建 kNN 并聚合到 clone

论文方法部分第二步说得很清楚：先在表达嵌入上建 kNN 图，然后对每个细胞统计它的 k 个邻居分别属于哪些 clone，最后把这些计数在同一 clone 内累加（`paper.md:229-232`）。

对应代码是 `clone2vec/tools.py:43-58` 和 `clone2vec/tools.py:216-237` 的 `clonal_nn`：

- 从 `adata.obsm[use_rep]` 读取表达嵌入；
- 用 `pynndescent.NNDescent` 找邻居；
- 把邻居的 clone 标签编码成整数；
- 构造稀疏矩阵并相乘，得到 `gex_adjacency`；
- 最后写入 `clones.obsp['gex_adjacency']`。

这一步就是 clone2vec 的“统计基础设施”。

#### 3. Skip-Gram 风格训练

论文把核心模型描述成一个非常像 word2vec Skip-Gram 的网络：输入和输出维度都是 clone 数 `C`，中间隐藏层维度是 `z`，输出做 softmax，然后最小化邻域共现的负对数似然（`paper.md:235-238`）。

代码对应关系很直接：

- `_create_pairs` 会把共现矩阵里每个非零计数展开成重复的 `(clone_i, clone_j)` 训练样本（`clone2vec/embeddings.py:19-55`）。
- `SkipGram` 定义了 embedding 层、输出线性层、`LogSoftmax`（`clone2vec/embeddings.py:57-119`）。
- `SkipGram.fit` 用 mini-batch、Adam、early stopping 训练（`clone2vec/embeddings.py:156-235`）。
- `clone2vec` 会把训练得到的 embedding 存到 `clones.obsm[obsm_key]`（`clone2vec/embeddings.py:537-673`）。

论文说“收敛后输入到隐藏层的权重矩阵就是 clone 的低维表示”（`paper.md:238-238`），代码里正是通过 `model.U` 实现的（`clone2vec/embeddings.py:533-535`, `clone2vec/embeddings.py:662-673`）。

#### 4. Poisson 版本

作者还提供了一个更快的替代版本：把 multinomial likelihood 换成 Poisson likelihood，这样输出维度间耦合更弱，更适合大数据优化（`paper.md:241-247`）。

代码实现是 `clone2vec_Poi`，位于 `clone2vec/embeddings.py:682-856`。它调用 `fastglmpca.poisson(...)`，并暴露了 `col_size_factor`、`row_intercept` 等参数。也就是说，这篇论文不是只提出概念，代码里确实有两个版本：

- 默认的 multinomial / Skip-Gram 版本；
- 更快的 Poisson GLM-PCA 版本。

#### 5. 跨数据集对齐

论文后半部分一个很重要的贡献是跨 cohort 的 clone embedding 对齐。思路是先用每个 clone 的平均表达找 MNN anchor，再用加权仿射变换把不同数据集映射到同一坐标系（`paper.md:277-295`）。

代码位置：

- `clone2vec/integration.py:237-402` 的 `find_mnn`：找不同 batch / cohort 之间的 MNN anchors；
- `clone2vec/integration.py:142-193` 的 `_affine_transform`：做线性变换加平移。

这和图 5 中间的算法示意图是对得上的。

### 这套方法为什么有用

从图像和正文看，clone2vec 的价值主要有三点：

1. 它能在稀疏 clone 场景下稳定给出 clone 之间的相对关系，而不是依赖脆弱的单个 clone 频率估计。
2. 它保留了连续几何结构，所以既能做聚类，也能做 archetype、梯度、基因关联分析。
3. 它天然适合做跨数据集比较，因为 clone embedding 可以再做对齐（`paper.md:250-295`）。

### 复现上的真实情况

当前 workspace 里的 `kharchenkolab-clone2vec` 仓库很好地覆盖了算法主干：邻域图、Skip-Gram、Poisson 变体、对齐逻辑都能直接找到源码。但论文的 code availability 还提到另一个 `clone2vec_analysis` 仓库用于论文分析复现（`paper.md:196-201`），这个仓库没有在当前工作区里，所以：

- 算法实现：可以直接核对，匹配度高；
- 论文所有图的完整复现实验脚本：当前 workspace 里没有。

### 还缺什么

- 论文正文没有给出清晰的显式公式编号，方法主要靠 prose 描述，所以不能硬造“Eq.1 / Eq.2”式映射。
- 数据集级复现脚本不在当前仓库，需要额外拉取 `clone2vec_analysis` 才能继续做图级复现检查。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## clone2vec Summary

clone2vec is a method for exploratory analysis of lineage-traced single-cell RNA-seq data that avoids hard dependence on discrete cell-type labels. Instead of comparing clones by hand-crafted fate proportions, it builds a cell-level kNN graph in a biologically meaningful expression embedding, aggregates clone co-occurrence counts across neighborhoods, and factorizes the resulting clone-by-clone matrix into a low-dimensional clone embedding (`paper.md:42-47`, `paper.md:220-238`). The paper argues this is more stable than OT, MMD, or cluster-based summaries when clones are small and the clone-size distribution is heavy-tailed (`paper.md:39-50`).

The method is evaluated across embryogenesis, hematopoiesis, and tumor / immune lineage-tracing settings. The figures show that the embedding can separate recurrent clone programs, project those programs back onto gene expression space, and support clone-level gene association analyses and cross-dataset alignment (`paper.md:56-168`). Figure 1 visually grounds the core algorithm: local cell neighborhoods are turned into a clone-neighbor count matrix and then decomposed into latent clonal factors; Figures 2-5 show that this representation recovers developmental territories, Treg subtypes, CD8 archetypes, and cross-cancer recurring lineages.

Reproducibility is relatively strong for the algorithmic core. The public package repo in this workspace implements the clone-neighborhood aggregation in `clone2vec/tools.py:43-58` and `clone2vec/tools.py:216-237`, the Skip-Gram training path in `clone2vec/embeddings.py:19-55`, `clone2vec/embeddings.py:156-235`, and `clone2vec/embeddings.py:537-673`, the fast Poisson alternative in `clone2vec/embeddings.py:682-856`, and the cross-dataset MNN alignment in `clone2vec/integration.py:237-402`. The main limitation is that the manuscript’s full analysis reproducibility is split across a second repository, `clone2vec_analysis`, which is referenced in the paper’s code availability section but not present in this workspace (`paper.md:196-201`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
