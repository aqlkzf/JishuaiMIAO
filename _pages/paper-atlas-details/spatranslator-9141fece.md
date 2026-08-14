---
layout: default
permalink: /paper-atlas/spatranslator-9141fece/
title: "SpaTranslator"
nav: false
wide: true
description: "SpaTranslator 先用空间图和 MNN 三元组把参考与目标切片的已观测模态放到同一个批次校正空间，再用参考切片的配对数据训练一个带自重建、交叉重建、KL 正则和对抗对齐的双向翻译器，最后把目标切片的对齐表示解码成缺失模态。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>SpaTranslator</h1>
    <p>SpaTranslator: A deep generative framework for universal spatial multi-omics cross-modality translation</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/donghongyu2020/SpaTranslator" target="_blank" rel="noopener noreferrer" aria-label="Open code for SpaTranslator">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpaTranslator 方法详解

### 1. 它要解决什么问题

空间多组学能够在同一组织切片、同一空间位置同时测量 RNA、染色质可及性、组蛋白修饰或蛋白质，但配对测量成本高、数据稀疏且存在大量掉零。与此同时，单模态空间数据越来越多。SpaTranslator 的目标是：利用一个具有配对模态的参考切片，给另一个只测到单一模态的目标切片补全缺失模态（论文 `paper.md:18-30`）。

论文以 RNA 到 ATAC 为例：

- $S_1^R$：参考切片 S1 的 RNA 矩阵；
- $S_1^A$：参考切片 S1 的 ATAC 矩阵，与 $S_1^R$ 配对；
- $S_2^R$：目标切片 S2 已测得的 RNA 矩阵；
- $\hat S_2^A$：模型需要生成的 S2 ATAC 矩阵。

关键困难不是简单地学习“RNA 特征到 ATAC 特征”的回归。S1 与 S2 之间还有批次差异，而且空间 spot 的测量比单细胞更稀疏，需要利用邻近 spot 的信息。因此 SpaTranslator 先解决“同一模态跨切片对齐”，再解决“配对模态之间翻译”。

### 2. 为什么已有方法不够

论文比较了 multiDGD（Nature Communications, 2024）、scPair（Nature Communications, 2024）、JAMIE（Nature Machine Intelligence, 2023）和 scButterfly（Nature Communications, 2024）。这些方法主要面向单细胞跨模态生成。论文认为它们在空间场景有三个不足（`paper.md:24,327-330`）：

1. 通常只处理单个细胞或 spot 的特征，没有显式利用空间邻接图；
2. 训练数据与目标切片之间存在批次差异，而已有翻译框架未必显式校正；
3. 一些方法与预定义模态对绑定，难以扩展到新的空间模态。

SpaTranslator 的新意是把空间图编码、MNN 对比式批次校正、变分生成和对抗分布对齐放在同一个两阶段框架中。

### 3. 从输入到输出的完整流程

```text
参考切片: S1_R + S1_A                目标切片: S2_R
          |                                   |
          +---------- 各模态预处理 -----------+
          | RNA: 归一化/log/HVG                |
          | ATAC: 二值化/过滤/TF-IDF           |
          v                                   v
             按空间坐标建立 kNN 图 (k=6)
          |                                   |
          +------ RNA 的 GAT 自编码器 ----------+
          |       重建损失 + MNN 三元组损失      |
          v                                   v
      对齐后的 S1 RNA 表示                对齐后的 S2 RNA 表示
          |
          | 与 S1 ATAC 的图编码表示构成配对训练数据
          v
       对抗式变分跨模态翻译器
       RNA/ATAC 编码 -> 共享随机潜变量 -> 双解码器
          |                                   |
          | 在 S1 上训练                        | 推理时冻结并用均值
          v                                   v
      自重建 + 交叉重建                  ATAC 解码器 -> S2_A_hat
```

#### 3.1 模态预处理

RNA 默认进行总量归一化、`log1p` 和 3,000 个高变基因选择；ATAC 默认二值化，过滤少于 0.5% spot 激活的 peak，做 TF-IDF，再缩放到 $[0,1]$（论文 `paper.md:172-175`；代码 `utils.py:520-650`）。

论文对蛋白质使用按细胞的 CLR 变换（`paper.md:178`），但在检查的代码快照中没有找到明确的 CLR 或 ADT/蛋白质预处理实现。因此，RNA/蛋白质结果属于论文和图像支持的实验结论，不是当前代码中已定位到的实现路径。

#### 3.2 空间图

每个 spot 是节点，按空间坐标的欧氏距离选择 $k=6$ 个邻居。论文把邻接矩阵记为 $A$，并描述为含自环的对称矩阵（`paper.md:181`）。代码使用 KNN 建边并加单位矩阵作为自环，但没有显式把有向 KNN 边对称化（`utils.py:18-102`）。

#### 3.3 RNA 跨切片对齐

S1 RNA 与 S2 RNA 先拼接到一个批次校正任务中。两层 GAT 编码器产生低维表示，图解码器重建输入。不同切片之间表达相似且互为近邻的 spot 构成 MNN 正样本；负样本从 anchor 所在切片随机抽取（论文 `paper.md:193-199`；代码 `aligner_train.py:20-155`）。

由于获取到的论文 Markdown 丢失了原始显示公式，下面是根据论文文字和代码整理的可执行含义，而不是论文公式的逐字恢复：

$$
\mathcal{L}_{\mathrm{align}}=
\operatorname{MSE}(X,\hat X)+
\frac{1}{|\mathcal{T}|}\sum_{(a,p,n)\in\mathcal{T}}
\max\{0,\lVert z_a-z_p\rVert_2-\lVert z_a-z_n\rVert_2+\tau\},
$$

其中 $\tau=1$。第一项保存生物信号，第二项让跨切片 MNN 更接近、同切片随机负样本更远。最终表示写入 `AnnData.obsm['AlignedEmbedding']`。

代码与论文在训练节奏上有差异：论文说前 500 epoch 只做重建，后 500 epoch 每 10 个 epoch 加一次对比损失；代码在 500 epoch 之后的每个 epoch 都计算三元组损失（`paper.md:223`; `aligner_train.py:81-150`）。

#### 3.4 模态编码与 VAE 预训练

RNA 编码器由 MLP 和末层 GCN 组成；ATAC 编码器先按染色体切分 peak，在染色体块内做线性变换，再以 GCN 汇总空间信息。ATAC 解码器也保留染色体分块结构（`translation_train.py:21-257,486-585`）。

编码表示进入模态特异的 VAE 头，得到均值 $\mu_m$ 和 log-variance，训练时使用重参数化采样：

$$
z_m=\mu_m+\epsilon\odot\exp(\tfrac12\log\sigma_m),\qquad
\epsilon\sim\mathcal{N}(0,I).
$$

代码对 RNA 使用 MSE，对 ATAC 使用 BCE，并给两个模态都加 KL 正则（`translation_train.py:698-719`）：

$$
\mathcal{L}_{m}=\mathcal{L}_{\mathrm{rec},m}+
\beta_mD_{\mathrm{KL}}(q_m(z|x)\|\mathcal{N}(0,I)).
$$

`SpaTranslator.train_model` 根据特征数设置 $\beta_R=20/d_R$、$\beta_A=20/d_A$ 并做线性 warm-up（`spatranslator.py:265-300`）。这是代码中确认的细节，论文没有给出这一权重公式。

#### 3.5 双向跨模态翻译

翻译器分别为 RNA 和 ATAC 建立均值/方差编码头，但共享同维度潜空间。任意一侧输入都产生两个输出：RNA 潜表示和 ATAC 潜表示。因此模型内部同时支持 R2A 和 A2R（`translation_train.py:297-418`）。

配对参考 spot 上实际计算四个重建：

- R2R：RNA 自重建；
- R2A：RNA 翻译成 ATAC；
- A2R：ATAC 翻译成 RNA；
- A2A：ATAC 自重建。

代码中生成器的基础目标为（`translation_train.py:723-759`）：

$$
\mathcal{L}_{\mathrm{base}}=
w_R(\mathcal{L}_{R2R}+\mathcal{L}_{A2R})+
w_A(\mathcal{L}_{R2A}+\mathcal{L}_{A2A})+
w_{KL}(D_{KL,R}+D_{KL,A}).
$$

这比“只优化目标方向的交叉重建”更强：同一潜空间需要同时保留两个模态的自重建能力和双向翻译能力。

#### 3.6 对抗分布对齐

RNA 和 ATAC 各有一个判别器，区分真实模态嵌入和从另一模态生成的嵌入。判别器先更新，然后生成器尝试让翻译后的分布更像真实分布（`translation_train.py:765-805,1120-1167`）。

论文描述连续软标签：正样本从 $[0.8,1]$ 采样，负样本从 $[0,0.2]$ 采样；代码实际使用离散的 1、0.5 和 0，并且只有当判别器损失小于 1.35 时才把对抗项减到生成器损失中（论文 `paper.md:208`; 代码 `translation_train.py:789-803,1157-1167`）。这是明确的论文-代码差异。

#### 3.7 推理

R2A 推理时，S2 的 `AlignedEmbedding` 输入翻译器。模型使用潜变量均值而不是随机采样，再经 ATAC 潜解码器和 ATAC 特征解码器产生 $\hat S_2^A$。A2R 分支完全对称。代码调用 `eval()`、`torch.no_grad()` 并返回带目标模态特征名的 `AnnData`（`translation_train.py:1253-1362`）。

### 4. 实验如何证明有效

论文在 MISAR-seq、空间 ATAC-RNA-seq、空间 CUT&Tag-RNA-seq，以及 10x Visium RNA/蛋白质数据上测试。基准指标包括 ARI、AMI、NMI 和 HOM；生物一致性还包括 marker 基因/蛋白 PCC、motif enrichment 以及 ArchR peak-to-gene 关联（`paper.md:59-76,82-147,235-280`）。

- 八个 MISAR-seq 切片平均结果中，相对最佳基线，ATAC-to-RNA 的 ARI 提升 79.6%，RNA-to-ATAC 提升 51.7%。
- H3K27me3-to-RNA 的峰值相对 ARI 提升为 128.1%。
- E15.5 小鼠脑跨切片任务中，两个方向的相对 ARI 提升分别为 53.1% 和 19.9%。
- 图 3 中 marker 和 motif 示例的 PCC 超过 0.8；图 4-5 显示扁桃体和淋巴结 RNA/ADT 任务中的空间结构和 marker 恢复。

把预测 ATAC 与真实 RNA 输入 ArchR 后得到的 `NR2E1`、`SOX2` peak-to-gene 连线应理解为**假设生成结果**：它们是预测数据支持的相关关系，不是实验验证的因果调控边。

### 5. 论文与代码的一致性

总体一致性为 **medium**。

**已直接匹配：**空间图、RNA/ATAC 预处理、GAT/MNN 对齐、染色体分块 ATAC 网络、双向 VAE 翻译、四项重建、判别器以及 R2A/A2R 推理。

**部分匹配：**论文和代码的隐藏维度、预训练 epoch、MNN 损失频率、对抗软标签方案不同。批次对齐和翻译由两个 notebook 串联，不是单个自动化入口。

**Not found：**明确的 ADT/蛋白质 CLR 路径、组蛋白修饰专用预处理、完整五折实验脚本、chromVAR/JASPAR/ArchR 复现代码、自动化测试。

### 6. 使用和解释时最重要的限制

1. 当前代码快照中只有两个 MISAR-seq R2A 教程；A2R、组蛋白和蛋白质任务缺少对应教程。
2. 补充材料不可用，无法核对 Supplementary Tables 1-2、Notes C 和 Figs. S1-S2。
3. 没有执行端到端训练或推理；数据、checkpoint 和论文所用 A100 环境不在工作区。
4. 代码中存在无条件 `.cuda()` 调用，CPU-only 运行路径未得到源码级确认。
5. 图中主要展示聚类和空间相关性优势，没有给出预测不确定性、校准或跨技术外部验证。
6. 论文当前只处理双组学和二维切片；多于两个模态、影像输入和 3D 组织是未来方向（`paper.md:157`）。

### 7. 一句话理解

SpaTranslator 先用空间图和 MNN 三元组把参考与目标切片的已观测模态放到同一个批次校正空间，再用参考切片的配对数据训练一个带自重建、交叉重建、KL 正则和对抗对齐的双向翻译器，最后把目标切片的对齐表示解码成缺失模态。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpaTranslator

**Paper:** *SpaTranslator: A deep generative framework for universal spatial multi-omics cross-modality translation*
**Venue/year:** bioRxiv preprint, 2025
**DOI:** `10.1101/2025.11.15.688644`

### Problem

Paired spatial multi-omics assays are costly and sparse, while single-modality spatial datasets are increasingly abundant. SpaTranslator uses a paired reference slice to generate a missing modality for another slice, aiming to synthesize paired spatial RNA/epigenome or RNA/protein data from a single observed assay.

### Limitations of Prior Methods

The paper compares with four methods developed primarily for single-cell modality translation: multiDGD (Nature Communications, 2024), scPair (Nature Communications, 2024), JAMIE (Nature Machine Intelligence, 2023), and scButterfly (Nature Communications, 2024). According to the paper, these methods operate on individual feature vectors without spatial graphs, do not explicitly handle inter-slice batch effects in this setting, and may be restricted to particular modality pairs. Those limitations are consequential for sparse spatial spots whose neighborhood and slice of origin affect the signal.

### Proposed Method

SpaTranslator combines two stages. First, modality-specific graph autoencoders aggregate information over spatial $k$NN graphs. For the observed modality across reference and target slices, a GAT autoencoder is trained with reconstruction and MNN triplet losses to obtain aligned, batch-invariant embeddings. Second, an adversarial variational translator learns from paired reference embeddings: modality-specific latent distributions feed shared RNA/second-modality decoders, while discriminators encourage translated embeddings to resemble real embeddings. At inference, the frozen translator decodes the target slice's aligned observed-modality embedding into the missing feature matrix.

The checked code confirms spatial graph construction, RNA/ATAC preprocessing, GAT/MNN alignment, chromosome-aware ATAC layers, bidirectional R2A/A2R variational translation, four self/cross-reconstruction terms, adversarial discriminators, and deterministic mean-based inference. It does not expose the full two-stage workflow as one call; two R2A notebooks connect the aligner and translator.

### Evaluation and Main Results

For intra-slice RNA/epigenome translation, the paper evaluates 12 mouse-brain slices from MISAR-seq, spatial ATAC-RNA-seq, and spatial CUT&Tag-RNA-seq. Spots are split 7:1:2, results use five-fold cross-validation, and generated-data clusters are assessed by ARI, AMI, NMI, and homogeneity. Across eight MISAR-seq slices, SpaTranslator reportedly improves ARI over the best baseline by 79.6% for ATAC-to-RNA and 51.7% for RNA-to-ATAC. It also leads on the displayed histone-mark tasks, with a reported peak 128.1% relative ARI improvement for H3K27me3-to-RNA.

In cross-slice E15.5 mouse brain, the paper reports 53.1% and 19.9% relative ARI gains for ATAC-to-RNA and RNA-to-ATAC. Marker-gene and motif predictions reach PCC values above 0.8 in the shown examples, and predicted ATAC is combined with measured RNA for ArchR peak-to-gene analysis around `NR2E1` and `SOX2`. These regulatory links are hypothesis-generating associations, not experimentally validated causal relationships.

Human tonsil and lymph-node experiments extend the reported advantage to RNA/ADT translation. The figures show higher clustering scores, coherent tissue domains, and higher marker gene/protein PCC than all four baselines. The paper concludes that the approach generalizes across epigenomic, histone, and protein targets, although only the RNA/ATAC implementation path was directly verified in this code snapshot.

### Reproducibility and Limitations

**Reproducibility rating: 3/5.** The paper provides public datasets and a public Python repository, and the core R2A/A2R architecture is traceable to direct source lines. Two R2A tutorial notebooks demonstrate batch alignment and translation. However, the repository lacks automated tests, pretrained checkpoints in the inspected snapshot, complete scripts for Figs. 2-5, A2R/histone/protein tutorials, explicit CLR/proteomics code, and the chromVAR/ArchR evaluation pipelines. The notebooks require external `.h5ad` files and user-edited paths, and the implementation contains unconditional CUDA transfers. No end-to-end run was performed here.

The paper-code fidelity is **medium**. Several differences matter: code defaults use 100 RNA and 100 ATAC VAE pre-training epochs rather than the paper's described schedules; the MNN triplet loss is applied every post-warm-up epoch rather than every 10 epochs; adversarial pseudo-labels are discrete rather than sampled from the paper's continuous soft-label intervals; and default graph widths differ from the stated 512/128 configuration. Supplementary material was unavailable, and the acquired Markdown omitted displayed method equations.

Scientific limitations stated by the authors include support for only dual-omics inputs and two-dimensional slices; extensions to imaging, more than two modalities, and 3D tissue are future work. Additional limitations visible from the evidence are the absence of predictive uncertainty/calibration, reliance on predefined cluster counts during evaluation, baselines that do not use spatial graphs, and validation confined to the presented mouse-brain and two human immune-tissue datasets.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
