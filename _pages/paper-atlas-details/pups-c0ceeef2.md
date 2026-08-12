---
layout: default
permalink: /paper-atlas/pups-c0ceeef2/
title: "PUPS"
nav: false
description: "PUPS 把蛋白亚细胞定位从“给蛋白打一个细胞器标签”改写成“给定某条蛋白序列和某个具体细胞的地标染色图，生成该蛋白在这个细胞中的荧光图像”。蛋白序列回答“要预测的是谁”，细胞图像回答“它要被放进怎样的细胞环境”，因此模型可以同时处理未见蛋白、未见细胞系和同一细胞系内的单细胞差异。 论文发表于 Nature Methods（2025），DOI：10.1038/s41592-025-02696-1。"
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
      <span>Protein &amp; Sequence Models</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>PUPS</h1>
    <p>Prediction of protein subcellular localization in single cells</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PUPS 方法详解：在单细胞中预测未见蛋白的亚细胞定位

### 一句话理解

PUPS 把蛋白亚细胞定位从“给蛋白打一个细胞器标签”改写成“给定某条蛋白序列和某个具体细胞的地标染色图，生成该蛋白在这个细胞中的荧光图像”。蛋白序列回答“要预测的是谁”，细胞图像回答“它要被放进怎样的细胞环境”，因此模型可以同时处理未见蛋白、未见细胞系和同一细胞系内的单细胞差异。

论文发表于 *Nature Methods*（2025），DOI：`10.1038/s41592-025-02696-1`。

### 1. 论文要解决什么问题？

蛋白的位置会影响其功能、相互作用和疾病表型，但实验图谱不可能覆盖所有“蛋白 × 细胞类型 × 单细胞状态”组合。论文指出，HPA 虽然包含 13,147 个基因编码蛋白的定位信息，但每个蛋白最多只在三个细胞系中测量，整个数据集也只有 37 个细胞系。更重要的是，同一蛋白在不同细胞系、甚至同一细胞系的不同单细胞中都可能改变核内/胞质等空间分布。

所以真正困难的问题不是普通分类，而是：

> 能否在没有测过目标蛋白、甚至没有用过目标细胞系训练的情况下，预测它在某个具体单细胞里的空间定位图像？

### 2. 为什么已有方法不够？

#### 2.1 只看序列的方法缺少细胞环境

- WoLF PSORT（*Nucleic Acids Research*, 2007）和 light attention（*Bioinformatics Advances*, 2021）等方法可从序列预测细胞器标签。
- 优点是能推广到未见蛋白。
- 局限是输出通常是粗粒度标签，无法表示同一蛋白在不同细胞系或不同单细胞中的相对空间分布，也无法直接生成蛋白图像。

#### 2.2 只看图像的方法需要目标蛋白已经被拍到

- HPA 图像分类工作（*Nature Methods*, 2019）可以从已有蛋白图像标注定位。
- paired-cell inpainting（*PLoS Computational Biology*, 2019）利用参考细胞的目标蛋白图像和查询细胞的地标图像进行补全。
- 这类方法能利用细胞形态，却不能在完全没有目标蛋白图像的条件下预测未见蛋白。

PUPS 的关键判断是：序列和细胞图像不是互相替代的输入，而是分别承担“蛋白泛化”和“细胞状态泛化”。

### 3. 输入与输出

对一个蛋白–单细胞样本，模型使用：

| 对象 | 形式 | 作用 |
|---|---|---|
| 蛋白序列 | 从 N 端开始最多 2,000 个氨基酸 | 定义目标 proteoform，并提供定位相关序列模式。 |
| ESM-2 表征 | 每个残基 1,280 维 | 预训练蛋白语言模型提供的残基级特征。 |
| 蛋白长度 | 一个标量 | 在注意力池化时屏蔽补零位置。 |
| 三通道地标图 | $3 \times 128 \times 128$ | 论文描述为细胞核、微管和 ER；提供具体细胞的结构与状态。 |
| 29 维定位标签 | 多标签向量 | 辅助任务的监督信号。 |
| 真实抗体染色图 | $1 \times 128 \times 128$ | 主任务的训练目标。 |

模型输出一张 $128 \times 128$ 的目标蛋白预测图，同时输出 29 个亚细胞定位标签的概率。

### 4. 完整计算流程

```text
蛋白氨基酸序列
    |
    | ESM-2：前 2,000 个残基，每个残基 1,280 维
    v
残基特征矩阵 + 有效序列长度
    |
    | Light Attention
    | 特征卷积 + 注意力卷积
    | 注意力加权池化 + 最大池化
    v
300 维蛋白表征 z
    |                                  \
    |                                   \ 单层线性分类器
    |                                    v
    |                              29 个定位 logits
    |                              辅助 BCE 损失
    |
    | 将 z 平铺到 16 x 16 空间网格
    v
三通道单细胞地标图 -> 卷积编码器 -> 16 x 16 x 512 图像表征
                                      |
                               与平铺后的 z 拼接
                                      |
                         U-Net 风格解码器 + 跳跃连接
                                      v
                         目标蛋白的单通道预测图
                         与真实图像计算 MSE

总损失 = 图像 MSE + 加权辅助 BCE
```

### 5. 序列分支如何工作？

#### 5.1 ESM-2 负责提供通用蛋白知识

论文使用预训练 ESM-2，把每个氨基酸变成 1,280 维向量。代码加载 `esm2_t33_650M_UR50D` 并抽取第 33 层表征（`PUPS/src/utils/esm2_utils.py:10-19,47-66`）。序列只保留从 N 端开始的前 2,000 个残基，较短序列补零。

这个截断保留 N 端有明确生物学意义：许多定位信号位于 N 端，例如线粒体转运肽。但对超长蛋白而言，2,000 位之后的信息会被舍弃，这是模型设计的明确限制。

#### 5.2 Light Attention 把变长序列压缩成 300 维

令残基特征为 $E$。模型用两条可分离一维卷积分支分别生成特征 $F$ 和注意力分数 $A$：

$$
F=f_{\mathrm{feat}}(E), \qquad A=f_{\mathrm{attn}}(E).
$$

注意力分支会屏蔽补零位置，然后计算加权和；同时再计算一个最大池化：

$$
p_{\mathrm{attn}}=\sum_i F_i\operatorname{softmax}(A)_i,
\qquad
p_{\max}=\max_i F_i.
$$

二者拼接后，经线性层、dropout、ReLU 和 batch normalization 得到 300 维蛋白表征 $z$（`PUPS/src/model/nn_light_attention.py:44-64,90-110`）。

一个论文正文没有展开的源码细节是：padding mask 明确作用在注意力分数上，而最大池化分支直接对卷积输出取最大值。

#### 5.3 辅助任务为什么重要？

如果只用图像重建损失，序列表征未必会主动学习“哪些序列模式决定定位”。PUPS 因此把 $z$ 输入一个单层线性分类器，预测 29 个 HPA 定位标签：

$$
\hat{a}=W_cz+b_c.
$$

训练使用多标签 BCE-with-logits。这个辅助任务把定位知识直接压入 $z$，而 $z$ 又同时进入图像生成器，所以辅助监督能改善未见蛋白的图像预测。Extended Data Fig. 3 的消融显示，移除辅助分类器会明显恶化性能。

### 6. 图像分支如何工作？

#### 6.1 细胞地标图不是目标蛋白图

输入是描述细胞结构的三张地标图，而不是目标蛋白本身。它们提供细胞大小、形态、核结构和细胞状态等上下文，让同一条蛋白序列在不同细胞中得到不同预测。

论文描述的预处理包括：图像下采样四倍、Otsu 阈值、$\sigma=5$ 的高斯平滑、去除小孔洞和小/边界细胞核、以核质心裁剪 $128 \times 128$ 单细胞图、各通道缩放到 $[0,1]$，并把地标通道中低于 0.19 的像素置零（`paper.md:189-195`）。Extended Data Fig. 5 说明这个阈值对抑制目标抗体荧光串色非常关键。

#### 6.2 编码器学习具体细胞的表征

源码中的主要形状变化是：

```text
3 x 128 x 128
 -> 64 x 128 x 128
 -> 128 x 64 x 64
 -> 256 x 32 x 32
 -> 512 x 16 x 16
 -> 512 x 16 x 16 bottleneck
```

卷积使用 Xception 风格的 depthwise separable convolution，并配合激活、batch normalization 和池化（`PUPS/src/model/nn_unet.py:59-167`）。

#### 6.3 蛋白和细胞在哪里融合？

300 维蛋白向量 $z$ 被复制到 $16 \times 16$ 的每个空间位置：

$$
Z_{\mathrm{tile}}\in\mathbb{R}^{300\times16\times16}.
$$

然后与图像 bottleneck $H$ 按通道拼接：

$$
J=[H;Z_{\mathrm{tile}}].
$$

源码对应 `PUPS/src/model/nn_unet.py:223-229`。这一步的直觉是：蛋白向量提供“要生成什么蛋白”，图像 bottleneck 提供“当前空间位置属于怎样的细胞环境”。

#### 6.4 U-Net 解码器生成蛋白图像

融合后的表征通过上采样解码器恢复到 $128 \times 128$。编码器各尺度的特征通过拼接式跳跃连接送入对应解码层（`nn_unet.py:231-243`），保留细胞边界和局部结构。最终得到一张单通道图像 $\hat{Y}$。

图像损失是：

$$
\mathcal{L}_{\mathrm{img}}
=\frac{1}{128^2}\sum_{u,v}(\hat{Y}_{uv}-Y_{uv})^2.
$$

### 7. 联合训练目标

代码中的默认目标为：

$$
\mathcal{L}_{\mathrm{total}}
=\mathcal{L}_{\mathrm{img}}+\lambda\mathcal{L}_{\mathrm{aux}},
\qquad \lambda=1.
$$

这意味着图像任务和标签任务共同更新 ESM-2 后的 light-attention 模块、辅助分类器和图像网络。

这里存在一个必须保留的论文–代码差异：

- 论文 Methods 写 Adam 学习率为 $10^{-4}$（`paper.md:159`）。
- 当前源码 `configure_optimizers()` 使用 `1e-3`，并配置 `ReduceLROnPlateau(patience=2)`（`PUPS/src/model/full_model.py:164-170`）。

本地证据不能判断发布 checkpoint 实际使用哪一个值，因此不能把二者擅自统一。

### 8. 如何从预测图像得到生物学结论？

#### 8.1 核内比例

模型先用 StarDist 从核通道得到核掩膜 $M$，然后计算：

$$
r(\hat{Y},M)=
\frac{\sum_{u,v}M_{uv}\hat{Y}_{uv}}
{\sum_{u,v}\hat{Y}_{uv}}.
$$

这个核内比例把一张复杂图像压缩成可比较的定位量。

#### 8.2 跨细胞系变异

论文把每个细胞的 $r$ 离散为：$r>2/3$ 记为 1，$r<1/3$ 记为 −1，其余记为 0；先在每个细胞系内求平均，再比较同一蛋白跨细胞系的变化。高变异蛋白富集于转录、细胞分化和染色质调控。

#### 8.3 同一细胞系内的单细胞变异

对固定蛋白–细胞系组合，直接计算单细胞 $r$ 的方差。预测排名与真实 HPA 排名具有较高一致性，说明部分单细胞定位差异可由地标图中的形态/状态解释，而不是完全随机。

### 9. 关键实验结果

- **held-out 图像误差：** holdout 1 和 holdout 2 的中位 MSE 分别为 0.00705 和 0.00960；均匀分布基线为 0.408 和 0.412。
- **跨细胞系核内比例：** 预测与真实值相关系数分别为 0.794 和 0.878。
- **新实验验证：** 在五个细胞系、九个蛋白的新成像实验中，预测与真实核内比例的 Pearson 相关为 0.767，95% CI 为 0.757–0.777。
- **消融：** 替换 ESM-2 为 one-hot、移除辅助分类器、移除/削弱 inpainting 网络或跳跃连接都会降低性能。
- **基准：** 序列辅助头与 light attention 相当并优于 WoLF PSORT；图像生成优于 Lu 等人的 paired-cell inpainting 基线。
- **可解释性：** AARS2 的 N 端线粒体转运肽、DDIT3 的 basic leucine zipper/NLS 区域与模型的残基重要性峰值对应。

### 10. 代码到底能复现到什么程度？

代码–论文整体匹配度评为 **medium**，复现性评为 **3/5**。

#### 已具备

- 固定 Git commit：`e0354b9e6374c1f6676fcbc9d9c15ca6c7fccd6d`。
- 核心模型、数据构建、预处理和 Shapley 支持源码。
- 299 行 conda 依赖清单。
- 22 个 epoch checkpoint 和 `nothreshold.ckpt`。
- README 指定论文结果使用 epoch-01、`val_combined_loss=0.18` 的 checkpoint，该文件确实存在。
- 论文图 2–6 对应的分析 notebook。

#### 仍然阻止一键复现的因素

1. **外部 HPA 数据依赖。** `SubCellDatset` 连接本地 MongoDB 的 `hpa_old`/`hpa` 数据库，并从记录中读取 ESM-2 binary 和图像路径；数据库与图像资产不在工作区内。
2. **本地图像路径仍是占位配置。** `src/utils/utils.py` 中是 `/path/to/folder1` 和 `/path/to/folder2`，用户必须配置真实路径。
3. **第三地标通道语义不一致。** 论文写 ER，运行时字段名为 `mitochondria_channel`；下载代码把 yellow 图像存到该键，而可视化函数又把 yellow 描述为 ER。没有真实存储数据时不得推断其含义。
4. **学习率冲突。** 论文 `1e−4`，源码 `1e-3`。
5. **默认训练入口有参数名错误。** `train.py:main()` 传入 `if_alphabetical=True`，但 `run_train()` 接受的是 `use_old_hpa_client`（`PUPS/train.py:21-31,112-122`）。
6. **本地没有 supplementary。** Supplementary Figures/Tables 未被本分析使用。

### 11. 如何正确理解 PUPS 的创新？

PUPS 不是简单地把两个神经网络并排放在一起。它建立了一个很清楚的条件生成分解：

$$
\text{protein image}
=f(\text{protein sequence identity},\ \text{single-cell context}).
$$

- 序列决定哪些定位模式对该蛋白是可能的。
- 地标图决定这些模式在当前细胞里如何实现。
- 辅助分类任务迫使序列表征保留定位知识。
- 图像生成任务保留空间分布、相对丰度和单细胞异质性。

这种分解解释了为什么模型能同时推广到未见蛋白和未见细胞系，也是论文相对于纯序列分类或纯图像补全方法最重要的贡献。

### 12. 使用与解读时的注意事项

- 预测图像可以准确复现统计定位模式，但不等于发现了因果机制。
- SDHD、ETHE1 致病突变的定位变化是模型预测，需要实验验证。
- 模型主要在细胞系上训练和验证，不能直接等同于组织环境。
- 必须验证第三地标通道的真实语义，并保留 bleed-through 阈值控制。
- 若复现实验，应明确记录采用论文学习率还是源码学习率，以及是否修正训练入口参数。
- 本地没有 supplementary，任何依赖补充表格、抗体清单或额外图的结论都应继续标记为 `MISSING`。

### 结论

PUPS 的价值在于把蛋白序列的可泛化性和单细胞图像的上下文信息合并到一个空间生成模型中。论文的 held-out 测试、消融、串色控制和新实验验证共同支持其主要结论；源码也清楚实现了核心结构。但如果目标是完全复现论文，还需要重建外部 HPA MongoDB/图像环境，并对第三通道、学习率和训练入口的差异作出有记录的处理。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PUPS: Prediction of Protein Subcellular Localization in Single Cells

### At a Glance

PUPS predicts the fluorescence image of an unseen target protein in an individual cell from two inputs: the protein's amino-acid sequence and three landmark-stain images describing that cell. The sequence branch enables generalization beyond proteins observed in training; the image branch supplies cell-line and single-cell context. Their fused representation produces a spatial protein image rather than only a compartment label.

Published in *Nature Methods* (2025). DOI: `10.1038/s41592-025-02696-1`.

### Problem

Protein localization is functionally important and disease-associated, but existing atlases cover only a small fraction of possible protein–cell-line pairs. The Human Protein Atlas measures proteins encoded by 13,147 genes, with each protein observed in at most three of 37 cell lines in the aggregated data considered by the paper. Localization can also vary across individual cells within the same cell line, so a single atlas annotation is not enough to describe a new experimental context.

Previous approaches divide into two incomplete families:

- Sequence-based localization models can generalize to unseen proteins, but they predict coarse compartment labels and lack cell-specific morphology. Examples include WoLF PSORT (*Nucleic Acids Research*, 2007) and light attention (*Bioinformatics Advances*, 2021).
- Image-based classifiers or representation models capture cellular context but require an observed target-protein image. Examples include the Human Protein Atlas image-classification work (*Nature Methods*, 2019) and paired-cell inpainting (*PLoS Computational Biology*, 2019). They cannot directly generate localization for a protein never measured in the query cell.

PUPS is designed to bridge these two capabilities.

### Method

```text
protein sequence
  -> ESM-2 residue embeddings (first 2,000 residues, 1,280-D each)
  -> light attention
  -> 300-D protein representation
       |                      \
       |                       -> 29-label auxiliary localization classifier
       v
three 128 x 128 landmark images -> convolutional encoder
  -> 16 x 16 x 512 cell representation
  -> concatenate a spatially repeated protein representation
  -> U-Net-style decoder with skip connections
  -> one 128 x 128 predicted target-protein image
```

The main image loss is mean-squared error against the antibody-stain image. A binary cross-entropy auxiliary loss trains the sequence representation to predict 29 HPA localization labels. Ablations show that ESM-2 features, the auxiliary task, the image-inpainting branch, network depth and skip connections all contribute to held-out performance.

### Data and Evaluation

The model uses HPA Cell Atlas releases 16–22 and proteoform sequences from Ensembl. The paper reports:

- 340,553 training cells;
- 36,552 examples in holdout 1, divided into 11,050 evaluation and 25,502 test cells;
- 24,007 examples in holdout 2 from 556 proteoforms / 515 genes, designed to include more dissimilar and unseen protein families;
- held-out cell lines as well as held-out proteins, testing joint protein/cell-line generalization.

Core evaluation signals include:

- **Image prediction:** median MSE 0.00705 on holdout 1 and 0.00960 on holdout 2, compared with 0.408 and 0.412 for homogeneous-protein baselines.
- **Cross-cell-line localization:** predicted versus real intranuclear proportions correlate at 0.794 and 0.878 in the two held-out analyses.
- **Single-cell variability:** rankings based on the variance of intranuclear proportion show substantial consensus between predicted and real images.
- **Independent experiments:** nine proteins were imaged in five cell lines; predicted and measured intranuclear proportions correlate at 0.767 (95% CI 0.757–0.777), including cell lines outside model training.
- **Benchmarks:** the auxiliary sequence classifier is comparable to light attention and better than WoLF PSORT in the displayed comparisons; image prediction outperforms the paired-cell inpainting comparator in MSE and IoU.

### Main Scientific Findings

PUPS enables analysis that the incomplete atlas cannot support directly:

- Proteins with high localization variability across cell lines are enriched for transcription, cell differentiation and chromatin-regulation processes.
- Proteins with high variability across single cells are associated with cell division, transcription, double-strand break repair and apoptosis.
- Learned sequence representations recover localization-relevant regions such as the AARS2 mitochondrial transit peptide and the DDIT3 basic leucine zipper/NLS region.
- Cellular landmark embeddings cluster by cell line without cell-line labels as model inputs.
- Sequence changes in pathogenic SDHD and ETHE1 variants produce predicted localization shifts, although these mutation results are computational hypotheses rather than direct experimental validation.

### Figure-Grounded Evidence

The six main and eight extended-data figures were all inspected locally. Together they provide a coherent evidence chain:

1. architecture and coverage gap (Fig. 1; Extended Data Figs. 1–2);
2. held-out accuracy, ablation, benchmarks and spectral bleed-through control (Fig. 2; Extended Data Figs. 3–5);
3. cross-cell-line and single-cell variability (Figs. 3–4; Extended Data Figs. 6–7);
4. new experimental validation (Fig. 5);
5. learned representations and mutation-conditioned predictions (Fig. 6; Extended Data Fig. 8).

The 0.19 intensity threshold is particularly important: Extended Data Fig. 5 shows that without leakage suppression, the model can reproduce target-stain bleed-through from landmark channels rather than respond correctly to the requested protein sequence.

### Code–Paper Match

Overall code–paper fidelity is **medium**.

The checked commit contains the central architecture, preprocessing/data-building code, 22 epoch checkpoints, a 299-line conda package list and the notebooks mapped to the paper figures. The README identifies `splice_isoform_dataset_cell_line_and_gene_split_full-epoch=01-val_combined_loss=0.18.ckpt` as the model used for paper results, and that checkpoint is local.

Four boundaries prevent a turnkey reproduction:

1. **External runtime data:** training/evaluation require local HPA MongoDB collections and referenced image assets; these are not bundled.
2. **Landmark-channel ambiguity:** the paper says the third landmark is ER, while the runtime data field is named `mitochondria_channel`. Acquisition and visualization code use inconsistent biological naming around the yellow channel. Without the stored assets, this cannot be safely resolved.
3. **Learning-rate mismatch:** paper Methods state Adam `1e−4`; source code uses `1e-3`.
4. **Training entry-point mismatch:** `train.py:main()` passes `if_alphabetical`, but `run_train()` accepts `use_old_hpa_client`, so the advertised `python train.py` path is not directly runnable as checked.

### Reproducibility Assessment: 3/5

**Strengths:** fixed Git commit; readable core model and data-building source; pinned package inventory; released checkpoints; figure-analysis notebooks; clear paper-level dataset and preprocessing descriptions.

**Weaknesses:** large external MongoDB/image dependency; local path placeholders; inconsistent landmark naming; paper/code learning-rate conflict; broken default training entry; notebooks were not rerun; no local supplementary material.

The repository is sufficient to understand and audit the principal architecture, and potentially to evaluate the released checkpoint after reconstructing the data environment. It is not a self-contained, one-command reproduction package.

### Limitations

- The method is trained and validated primarily on cell lines; tissue-context prediction remains future work.
- Prediction quality depends on landmark stains and image preprocessing, including robust control of spectral bleed-through.
- The generated image may reproduce statistical localization patterns without revealing the causal cellular mechanism.
- Mutant-sequence localization examples are predictions and need direct biological validation.
- HPA aggregation, antibody/proteoform associations and the paper's held-out collections cannot be independently audited without the external database contents.
- Supplementary tables and figures are `MISSING` locally and were not used in this analysis.

### Bottom Line

PUPS's key contribution is to treat protein localization as a conditional image-generation problem: sequence tells the model *which protein* to place, while landmark images tell it *which individual cell* it is placing the protein into. The held-out tests, ablations, leakage controls and new experiments collectively support useful generalization to unseen proteins and cellular contexts. The released code strongly supports the architectural claim, but exact computational reproduction still requires reconstructing the HPA data infrastructure and resolving documented paper–code discrepancies.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
