---
layout: default
permalink: /paper-atlas/scellst-bda03236/
title: "sCellST"
nav: false
description: "sCellST 想解决的是：只有常规 H&E 病理切片时，能不能预测到接近单细胞分辨率的基因表达？H&E 图像便宜且常见，而空间转录组和 Xenium 等分子技术成本高、样本少。Visium 能给出每个 spot 的表达，但一个 spot 通常混合 10--20 个细胞，因此训练时没有真实的单细胞表达标签。 sCellST 把一个 Visium spot 看作一个 bag，把这个 spot 内的细胞图像看作多个 instances。"
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
      <span>Nature Communications · 2026</span>
    </div>
    <h1>sCellST</h1>
    <p>sCellST predicts single-cell gene expression from H&amp;E images</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-67965-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for sCellST">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/loicchadoutaud/sCellST" target="_blank" rel="noopener noreferrer" aria-label="Open code for sCellST">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## sCellST 方法中文解读

### 这篇文章解决什么问题？

sCellST 想解决的是：只有常规 H&E 病理切片时，能不能预测到接近单细胞分辨率的基因表达？H&E 图像便宜且常见，而空间转录组和 Xenium 等分子技术成本高、样本少。Visium 能给出每个 spot 的表达，但一个 spot 通常混合 10--20 个细胞，因此训练时没有真实的单细胞表达标签（`paper.md:39-64`, `paper.md:242-248`）。

### 核心思想

sCellST 把一个 Visium spot 看作一个 **bag**，把这个 spot 内的细胞图像看作多个 **instances**。模型先给每个细胞预测一个基因表达分数，再把同一个 spot 中所有细胞的预测求平均，得到 spot 级预测；训练时只比较这个 spot 级预测和 Visium 实测表达（`paper.md:272-296`）。这样即使没有单细胞表达标签，也能弱监督地训练出细胞级预测器。

```text
H&E + Visium spot 表达
   -> CellViT 分割细胞，裁剪 12 µm × 12 µm 小图并 resize 到 48×48
   -> MoCo v3 / ResNet-50 自监督编码，得到每个细胞的 embedding
   -> MLP 基因表达预测器 f_theta，输出非负表达分数
   -> 对同一 Visium spot 内的细胞预测求平均
   -> 与 spot 实测表达做损失，反向训练 f_theta
```

### 关键模块

1. **细胞分割与裁剪**：论文使用 CellViT 做核/细胞检测和分类，按细胞中心裁剪 12 µm × 12 µm 图像，并根据空间坐标把细胞关联到 Visium spot（`paper.md:260-264`）。代码里 `MilVisiumHandler.create_spot_cell_map` 读取 cell embedding 文件中的 spot-cell 对应关系，并过滤没有细胞的 spot（`sCellST/scellst/dataset/data_handler.py:134-152`）。
2. **自监督图像表示**：用 ResNet-50 作为编码器，主要采用 MoCo v3 对 H&E 细胞小图做对比学习；训练 SSL 时不使用任何基因表达标签（`paper.md:266-270`）。
3. **MIL 基因预测器**：`GenePredictor` 是多层感知机，默认隐藏层为 `[256, 256, 256]`，最后用 `Softplus(beta=20)` 保证预测非负（`sCellST/scellst/module/gene_predictor.py:11-91`, `sCellST/config/predictor/gene_predictor.yaml:1-6`）。
4. **spot 聚合**：`InstanceMilModel` 对每个细胞 embedding 预测表达，再用 `torch_scatter.scatter(... reduce="mean")` 按 spot 聚合（`sCellST/scellst/model/instance_mil_model.py:13-61`, `sCellST/scellst/lightning_model/gene_lightning_model.py:27-51`）。

### 损失函数

论文主要保留 MSE 损失。先做 library-size normalization 和 log transform：

$$
y_j^p=\ln\left(1+s\frac{y_j}{\sum_j y_j}
ight),\quad s=10000.
$$

然后最小化预测 spot 表达和真实 spot 表达之间的均方误差（`paper.md:299-318`）。代码中 `BaseMilModel.loss_dict` 把 `"mse"` 映射到 PyTorch 的 `mse_loss`，`InstanceMilModel.loss` 在 bag 级预测上计算损失（`sCellST/scellst/model/base_mil_model.py:58-61`, `sCellST/scellst/model/instance_mil_model.py:53-61`）。论文也尝试了负二项分布 NLL，用 library-size factor 和基因特异的离散参数，但模拟中没有明显优势，所以后续使用 MSE（`paper.md:320-328`）；代码对应 `InstanceDistributionMilModel`（`sCellST/scellst/model/instance_mil_distribution.py:11-88`）。

### 实验结果怎么理解？

- **模拟实验**：随机匹配形态和表达时相关性约为 0；按 cluster centroid 构造强关系时 mean correlation 到 0.93；更难的 cell scenario 仍有正相关，marker genes 的 spot-level mean correlation 从 0.20 提高到 0.68（`paper.md:65-102`）。这说明 MIL 框架本身能从 spot 标签中学到细胞级信号。
- **spot 级 benchmark**：在 kidney 8 张 Visium 和 prostate 5 张 Visium 上，sCellST 与 HisToGene、THItoGene、MclSTExp、Istar 比较。top-50 HVG/SVG 的 8 个比较里 sCellST 都最好；top-500 时仍然有竞争力，但部分设置 MclSTExp 更高（`paper.md:103-131`）。
- **细胞级验证**：sCellST 预测按 CellViT 标签分组后，免疫、基质、上皮相关 marker 的表达模式符合生物预期（`paper.md:132-162`）。
- **Xenium 验证**：用 Visium 训练的 breast 模型迁移到 Xenium H&E，虽然整体 median PCC 不高（0.06--0.15），但 KRT8、EPCAM、PTPRC、CD3E 等 marker 的空间模式和 Xenium 有较好对应（`paper.md:163-182`）。
- **细分细胞类型**：用 marker gene list 训练后，可以区分 fibroblast/endothelial、lymphocyte/plasma cell 等比 CellViT 粗标签更细的形态类型（`paper.md:183-205`）。

### 局限与复现

sCellST 依赖细胞分割质量、染色/扫描域差异、FFPE Visium 训练数据规模和图像分辨率；这些都会影响泛化（`paper.md:211-217`）。因此本地代码与核心方法高度匹配，但完整复现实验图还需要外部数据、embedding/checkpoints 和复现实验仓库。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## sCellST Summary

### Problem

sCellST addresses a practical gap between routine histology and molecular profiling: H&E whole-slide images are abundant, but spatial transcriptomics (ST) and single-cell gene-expression assays are expensive and less accessible. The paper asks whether single-cell gene-expression (GE) scores can be inferred from cellular morphology when the only paired molecular supervision is Visium spot-level expression, where each spot mixes roughly 10--20 cells (`paper.md:39-64`, `paper.md:242-248`).

### What sCellST introduces

sCellST is a weakly supervised, multiple-instance-learning (MIL) method for predicting single-cell GE from H&E-derived cell crops. The pipeline is: detect nuclei/cells on H&E, crop 12 µm × 12 µm cell images resized to 48 × 48 pixels, embed cells with a ResNet-50 encoder trained by MoCo v3 self-supervised contrastive learning, score each cell with a feed-forward GE predictor, and mean-aggregate cell predictions inside each Visium spot to train against measured spot GE (`paper.md:39-64`, `paper.md:260-296`). After training, the model can be applied to H&E slides alone to produce single-cell, spatially resolved GE predictions (`paper.md:61-64`).

### Why existing methods are insufficient

The paper compares against spot-level H&E-to-ST methods: HisToGene, THItoGene, MclSTExp, and Istar. These methods use spot images, transformers/graph attention, contrastive image-expression alignment, or patch-level weak supervision, but they do not natively solve the paper's main target: cell-level GE prediction from Visium-like spot supervision (`paper.md:103-112`, `paper.md:386-407`). sCellST is designed around cells as instances and Visium spots as bags.

### Evaluation and key results

- **Simulation:** artificial assignments between ovarian cancer cell images and scRNA-seq profiles showed that random morphology-expression matching gives mean correlation near 0, a centroid scenario reaches mean correlation 0.93, and the harder cell scenario remains positive; marker genes increase spot-level mean correlation from 0.20 to 0.68 (`paper.md:65-102`).
- **Spot-level benchmarks:** on kidney (8 Visium slides) and prostate (5 Visium slides) datasets from HEST, sCellST was best in all 8 comparisons for top-50 HVG/SVG sets and remained among the best for top-500 gene sets, though MclSTExp was sometimes higher (`paper.md:103-131`).
- **Cell-level biology:** predicted GE grouped by CellViT labels recovered plausible stromal, immune, and epithelial markers, and spatial maps highlighted immune aggregates and connective-cell patterns invisible at Visium resolution (`paper.md:132-162`).
- **Xenium comparison:** a Visium-trained breast model transferred to 9 Xenium breast H&E slides, with median PCC values around 0.06--0.15 across genes and higher gene-specific examples such as KRT8 0.41, EPCAM 0.47, PTPRC 0.45, and CD3E 0.33 (`paper.md:163-182`).
- **Fine cell-type scoring:** marker-gene training on ovarian cancer separated fibroblast/endothelial, lymphocyte/plasma, and epithelial-like morphologies without manual fine labels (`paper.md:183-205`).

### Code and reproducibility

The primary method code is available at `https://github.com/loicchadoutaud/sCellST` and is cloned in `sCellST/`; the paper also lists a separate `sCellST_reproducibility` repository for figure analyses (`paper.md:410-417`). The local code matches the central MIL predictor well: `GenePredictor` implements the MLP with Softplus output (`sCellST/scellst/module/gene_predictor.py:11-91`), `InstanceMilModel` maps cell embeddings to instance predictions and scatter-aggregates them by spot (`sCellST/scellst/model/instance_mil_model.py:13-61`), and the Lightning wrapper selects mean-aggregation MIL models plus PCC/SCC metrics (`sCellST/scellst/lightning_model/gene_lightning_model.py:14-128`). Reproducibility is **3/5**: the model implementation and tutorial are present, but large HEST/Xenium data, SSL pretrained embeddings/checkpoints, and the separate reproducibility repository are needed to recreate all paper figures.

### Main limitations

The paper emphasizes that segmentation errors, staining/scanner domain shifts, scarcity of FFPE ST training data, and the low spatial resolution of spot-based ST can limit performance (`paper.md:211-217`). The code analysis also found that `GeneLightningModel` references `BagMilModel` and `AttentionMilModel` branches without imports in the inspected file; the default regression/NB paths are matched, but those optional task modes are not verified runnable (`sCellST/scellst/lightning_model/gene_lightning_model.py:27-51`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
