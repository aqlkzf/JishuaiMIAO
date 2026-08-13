---
layout: default
permalink: /paper-atlas/marsgt-1f0af0a3/
title: "MarsGT"
nav: false
wide: true
description: "MarsGT 要解决的问题是：配对 scRNA-seq 和 scATAC-seq 中，稀有细胞往往只有很小比例，且 dropout 会让它们的 RNA 或染色质信号不稳定。若分别处理两种矩阵，细胞、基因和调控峰之间的信息难以互相补足。 它把细胞、基因、峰当作三类节点；RNA 非零值形成 cell--gene 边，ATAC 非零值形成 cell--peak 边。"
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
      <span>Nature Communications · 2024</span>
    </div>
    <h1>MarsGT</h1>
    <p>MarsGT: Multi-omics analysis for rare population inference using single-cell graph transformer</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/mtduan/marsgt" target="_blank" rel="noopener noreferrer" aria-label="Open code for MarsGT">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MarsGT：用单细胞图 Transformer 找稀有群体

MarsGT 要解决的问题是：配对 scRNA-seq 和 scATAC-seq 中，稀有细胞往往只有很小比例，且 dropout 会让它们的 RNA 或染色质信号不稳定。若分别处理两种矩阵，细胞、基因和调控峰之间的信息难以互相补足。

它把细胞、基因、峰当作三类节点；RNA 非零值形成 cell--gene 边，ATAC 非零值形成 cell--peak 边。随后按某细胞中更有特异性的高表达/高可及特征优先抽取子图，令稀有群体相关信号更常进入训练。图 1 的图像直接展示了这条流程。

```text
RNA + ATAC -> 异质图 -> 稀有信号偏好的子图
           -> 多头关系注意力 -> cell/gene/peak 联合嵌入
           -> 细胞伪簇 + peak-gene 概率 -> 全图推断
           -> 主群/稀有群 + 每簇 eGRN
```

训练时，基因嵌入与细胞嵌入的内积、峰嵌入与细胞嵌入的内积需要重构原始 RNA/ATAC 信号；同时使用聚类损失。第二阶段把基因和峰嵌入拼接后预测 peak--gene 关系，并与表达、可及性和先验关系共同聚合为簇特异分数。论文进一步用 JASPAR TF 结合位点把 peak--gene link 组织为 eGRN。

代码层面，`marsgt_model.py` 的 `GNN_from_raw` 与 `MarsGT` 实现了编码与两阶段损失，`conv.py` 实现关系特异的 HGT 注意力，`egrn.py` 实现每簇 peak--gene 分数聚合。需要注意：公开仓库有教程 notebook，但完整数据、TF 外部资源和全部基准绘图并未被整合成一个可一键复现实验。

论文在模拟和真实数据上比较稀有细胞识别，稀有比例最低到 0.5%，采用 F1、precision、recall、purity、entropy、NMI 等指标，并在淋巴瘤和黑色素瘤例子中报告稀有群及调控网络解释。它的贡献不是只做聚类，而是在同一模型中把稀有细胞发现和调控关系推断连接起来。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MarsGT

MarsGT is a multi-omics rare-cell discovery method that jointly models cells, genes and ATAC peaks as a heterogeneous graph transformer. It trains on rare-feature-biased subgraphs, assigns cells from learned embeddings, and estimates cluster-specific peak--gene relations for eGRN interpretation.

The Nature Communications paper evaluates simulated and real paired RNA--ATAC datasets, including rare fractions from 0.5% to 3%, and reports clustering and rare-cell metrics plus repeated-run stability. Its biological examples include B-lymphoma and melanoma MAIT-like populations (paper.md:401-464; 93-146).

**Reproducibility: 3/5.** The cited GitHub snapshot at commit `e3ce668` implements the core HGT, losses and eGRN score calculations, and includes a tutorial notebook. Full reproduction remains dependent on external data, TF-binding resources and non-unified benchmark/figure workflows.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
