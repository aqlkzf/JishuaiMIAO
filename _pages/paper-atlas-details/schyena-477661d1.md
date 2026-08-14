---
layout: default
permalink: /paper-atlas/schyena-477661d1/
title: "scHyena"
nav: false
wide: true
description: "单细胞 RNA 测序（scRNA-seq）同时存在两个困难：测序 dropout 产生大量零值，以及每个细胞包含约两万基因，直接使用全基因序列会带来很高的计算成本。常见流程会选取高度可变基因（HVG），但 HVG 对参数、批次和数据集敏感，可能丢失细胞信息。论文提出 scHyena，用 Hyena 的长卷积替代二次复杂度的 self-attention，以处理完整基因向量（论文第 1 节，行 20-40）。 连续表达值的线性适配器。"
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
      <span>arXiv · 2023</span>
    </div>
    <h1>scHyena</h1>
    <p>scHyena: Foundation Model for Full-Length Single-Cell RNA-Seq Analysis in Brain</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/scHyena2023/scHyena" target="_blank" rel="noopener noreferrer" aria-label="Open code for scHyena">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scHyena 方法说明（基于论文证据）

### 1. 解决什么问题

单细胞 RNA 测序（scRNA-seq）同时存在两个困难：测序 dropout 产生大量零值，以及每个细胞包含约两万基因，直接使用全基因序列会带来很高的计算成本。常见流程会选取高度可变基因（HVG），但 HVG 对参数、批次和数据集敏感，可能丢失细胞信息。论文提出 scHyena，用 Hyena 的长卷积替代二次复杂度的 self-attention，以处理完整基因向量（论文第 1 节，行 20-40）。

### 2. 核心创新

1. **连续表达值的线性适配器。** 每个基因表达值 (C_i) 是连续数值，线性层将其映射为表达嵌入 (E_i)，避免把数值分箱后再 token 化造成的信息损失（行 118-126）。
2. **基因嵌入而非位置编码。** 基因在序列中的排列没有时间含义；模型为每个基因学习 (G_i)，并将 (G_i+E_i) 输入 Hyena，使位置携带明确的基因身份（行 129-133）。
3. **双向 Hyena。** 原始 Hyena 的因果卷积只看当前位置及过去。scRNA-seq 中任意基因都可能相关，因此 scHyena 将滤波器定义在 (t=-L+1,ldots,L-1)，长度为 (2L-1)，让输出使用全体基因（行 102-116）。

### 3. 计算流程

```text
每个细胞的归一化表达 C1...CL（L=19,306）
        |
        | MEM 阶段随机掩码非零值
        v
线性适配器：Ci -> Ei       基因表：Gi
        \________ 逐位置相加 ________/
                       |
             M 个双向 Hyena block（实验中 M=4）
                       |
       +---------------+----------------+
       |                                |
 [CLS] 向量 -> 线性分类头          掩码位置预测
       |                                |
  细胞类型/Doublet                 表达值补全
```

Hyena 的基本卷积为

$$y_t=(h*u)_t=\sum_{\tau=0}^{L-1}h_{t-\tau}u_\tau,$$

其中滤波器写成 (h_t=\gamma_\theta(t))，从而可以构造长滤波器。递归形式为

$$y=x^N\cdot(h^N*(x^{N-1}\cdot(h^{N-1}*(\cdots x^1\cdot(h^1*v))))),$$

其中 (v,x^1,ldots,x^N) 是输入投影，(cdot) 是逐元素门控；实验设置 (N=3)。论文称使用 FFT 后每次长卷积为 (mathcal{O}(L\log_2L))（行 62-90）。

### 4. 预训练：Masked Expression Modeling

预处理把不同数据集的基因 ID 对齐到 Ensembl stable ID，保留 19,306 个基因；过滤总表达量低于 200 的细胞，将每个细胞总计数缩放到 10,000，再做 (log(x+1))（行 171-175）。预训练数据为 Kamath 与 Wang 两个脑组织数据集，共 575,482 个细胞。

MEM 随机选择掩码集合 (M)，把对应的非零表达替换为 `[MASK]` 嵌入，掩码概率在 ([0.05,0.4]) 范围内选择；零值不在预训练阶段掩码，因为无法判断是真零还是 dropout。模型在双向上下文中预测原表达，损失为

$$\ell_{MEM}=\sum_{i\in M}(C_i-C_i')^2,$$

其中 (C_i') 是预测值（行 135-145）。论文报告使用 AdamW、学习率 (10^{-4})、batch size 8、2 个 epoch 和两张 RTX 3090，训练约 3.5 天（行 177-180）。

### 5. 下游任务

#### 细胞类型分类与 Doublet 检测

在输入嵌入前加入可学习的 `[CLS]` 向量；经过双向 Hyena 后，将 `[CLS]` 表示送入线性分类头。交叉熵为

$$\ell_{cls}=-\sum_{i=1}^{N_c}y_i\log p_i,$$

其中 (p_i) 是第 (i) 类的 softmax 概率。Doublet 在含 Doublet 的实验中作为类别之一。下游微调为 5 个 epoch、AdamW、学习率 (10^{-5})，保留训练集 10% 做验证并选择验证集最优模型（附录 B，行 383-392）。

#### scRNA-seq 表达补全

直接沿用 MEM 会让模型倾向输出零，因为零值占多数。因此补全微调时对非零值使用 0.4 的掩码概率，对零值使用 0.04；损失仍为上式的平方误差（行 157-160）。非零值定量评估把待掩码位置分成五组，用 MSE 与 Pearson 相关系数比较真实值和预测值；零值实验把零位置分成十组，逐组补全后合并，再用 UMAP 检查细胞类型聚类和批次结构（行 243-249，附录 B 行 394-395）。

### 6. 数据与结果

下游数据集为 Lau、Leng、Smajic 和 Zhu，均统一到相同的 19,306 个基因。分类基线包括 Seurat、SciBet 和 scBERT；补全基线为 MAGIC 和 DCA。表 1 中，含 Doublet 时 scHyena 在四个数据集的 weighted F1 分别为 0.982、0.983、0.983、0.987，并在多数类别/平均指标上达到最佳或并列最佳。去除 Doublet 后，scHyena 与 Seurat、SciBet 相当或更好（行 189-232）。

图 4 和图 9 的预训练嵌入 UMAP 显示多数细胞类型形成相对连贯的群。图 6、图 13 的真实值-补全值联合图中，scHyena 点云通常更接近 (y=x)，论文据此报告较低 MSE 和较高 Pearson 相关。图 7、图 14-16 的 UMAP 用细胞类型和患者/批次着色；论文将 scHyena 补全后的更紧密同类型群解释为减少批次影响。UMAP 是定性证据，不能替代独立的批次校正指标。

### 7. 可复现性与已知缺口

本文档只使用论文 Markdown 和本地图像。论文链接的 scHyena GitHub 仓库 `https://github.com/scHyena2023/scHyena` 在采集时返回 404/不可用，因此没有可验证的代码实现。模型宽度 (D)、归一化与残差顺序、随机种子、学习率 schedule、基因排序、checkpoint、数据下载和推理脚本均为 **Not found**。论文报告的指标和图形没有被本地重新计算；它们应视为论文结果，而非独立复现结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scHyena: Foundation Model for Full-Length Single-Cell RNA-Seq Analysis in Brain

### Overview

scHyena is a 2023 arXiv method for learning representations from full-length brain scRNA-seq profiles. It targets two practical problems: dropout-related noise and the difficulty of processing tens of thousands of genes without selecting a small, dataset-sensitive highly variable gene subset. The paper's key idea is to adapt the Hyena long-convolution operator to continuous, non-causal gene-expression sequences, enabling 19,306-gene inputs with paper-reported (mathcal{O}(L\log L)) convolution cost rather than quadratic self-attention.

The model combines three changes: a linear adapter maps each continuous expression value to an embedding without binning; a learned gene embedding supplies gene identity instead of positional order; and a bidirectional Hyena filter of length (2L-1) lets every gene position depend on the entire cell profile. Four bidirectional blocks are pretrained with masked expression modeling (MEM), minimizing squared error on masked nonzero expression values. A learned `[CLS]` embedding and linear head support cell-type/doublet classification, while MEM-style prediction with different zero/nonzero masking rates supports imputation.

### Existing-method limitations

The paper argues that conventional attention is quadratic in gene-sequence length and that HVG selection may vary across batches or omit informative genes. scBERT (Nature Machine Intelligence, 2022) processes full expression profiles with Performer but bins continuous values; scHyena is designed to avoid that discretization. For classification it compares with Seurat (Cell, 2021), SciBet (Nature Communications, 2020), and scBERT. For imputation it compares with MAGIC (Cell, 2018) and DCA (Nature Communications, 2019), motivated partly by runtime and denoising limitations of prior workflows.

### Evaluation

Pretraining uses 575,482 brain cells from Kamath and Wang datasets. Downstream evaluation uses Lau, Leng, Smajic, and Zhu datasets, all mapped to the same 19,306 Ensembl IDs. Table 1 reports macro/micro/weighted and class-specific F1 scores with and without doublets. In the with-doublet setting, scHyena has the best or tied-best weighted F1 on all four datasets (0.982 Lau, 0.983 Leng, 0.983 Smajic, 0.987 Zhu) and strong doublet F1, while the without-doublet results are broadly comparable to or better than Seurat and SciBet. The paper uses marker-gene co-expression as an indirect doublet-likeness check because ground-truth doublets are unavailable.

For imputation, nonzero entries are masked in five groups and evaluated by MSE and Pearson correlation against normalized expression. The joint plots report scHyena predictions closer to (y=x) and better metrics than MAGIC and DCA. Zero-imputation UMAPs across four datasets show denser same-cell-type clusters and, in the authors' interpretation, reduced patient/batch structure. These UMAP findings are qualitative and were not accompanied by a dedicated batch-correction metric.

### Reproducibility and limitations

**Reproducibility: 2/5 (paper-only).** The paper provides datasets, major preprocessing, objectives, optimizer settings, block/recurrence counts, and evaluation protocols. However, its linked implementation, `https://github.com/scHyena2023/scHyena`, was unavailable/404 during acquisition, so no paper-code match or runnable example could be verified. Exact model width, residual/normalization layout, seeds, schedules, checkpoint/data scripts, gene ordering, and raw predictions are Not found in the available paper source.

The study is restricted to selected human brain datasets, with pretraining biased toward substantia nigra and Parkinson's disease sources. Reported generalization to other tissues and broader disease tasks is prospective. Doublet validation lacks ground truth, and imputation UMAP improvements do not by themselves prove faithful recovery of missing biological signal. All performance statements above are paper-reported rather than independently reproduced.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
