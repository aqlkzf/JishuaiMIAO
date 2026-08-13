---
layout: default
permalink: /paper-atlas/nimbus-11e54d21/
title: "Nimbus"
nav: false
wide: true
description: "Nimbus 不直接猜“这个细胞是什么类型”，而是对每个抗体通道分别回答：“这个细胞是否真的表达该标记？”它利用原始图像中的亚细胞形态和邻域背景，把容易受串色、边界和亮度影响的 integrated expression，转换成更适合聚类的细胞 × 标记阳性分数矩阵。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Nimbus</h1>
    <p>Automated classification of cellular expression in multiplexed imaging data with Nimbus</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/angelolab/Nimbus-Inference" target="_blank" rel="noopener noreferrer" aria-label="Open code for Nimbus">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Nimbus 方法详解：把“细胞类型识别”拆成可迁移的逐标记阳性判断

### 一句话理解

Nimbus 不直接猜“这个细胞是什么类型”，而是对每个抗体通道分别回答：“这个细胞是否真的表达该标记？”它利用原始图像中的亚细胞形态和邻域背景，把容易受串色、边界和亮度影响的 integrated expression，转换成更适合聚类的细胞 × 标记阳性分数矩阵。

### 1. 它在解决什么问题？

多重蛋白成像首先需要把组织图像分割成单个细胞，然后汇总每个细胞内的标记信号。最常见做法是计算细胞掩膜内的平均强度，即 integrated expression。但空间成像没有真正把相邻细胞物理分开，因此这个平均值会遇到几类系统性问题：

- 邻近高亮细胞的信号溢出到当前细胞；
- 细胞膜信号位于分割边界，平均后被稀释；
- 自发荧光、非特异性背景和不同数量级的染色强度；
- 分割误差把别的细胞或背景像素纳入掩膜；
- 同样的“阳性”可能表现为膜、核、胞质或胞外基质等完全不同的空间形态。

人类专家会看原图、亚细胞定位和周围细胞来判断阳性，但这种人工判断不能扩展到数百万细胞。

已有方法也有边界：

- **STELLAR**（*Nature Methods*, 2022）利用 integrated expression 与空间图结构预测细胞类型；
- **MAPS**（*Nature Communications*, 2024）从组织图像/整合表达学习细胞类型；
- **CellSighter**（*Nature Communications*, 2023）直接从多通道图像预测细胞类型；
- **GammaGateR**（*Bioinformatics*, 2024）、Otsu、$k$-means 和 GMM 则按标记或切片做门控/混合建模。

这些方法要么丢掉图像内部结构，要么把输出类别绑定到训练时的抗体面板。换一个 marker panel，监督式细胞类型模型往往需要重新训练（`paper.md:27-36,121-124,166-169`）。

### 2. Nimbus 的关键洞察

Nimbus 把一个困难任务拆成两步：

```text
原始多重图像
  -> 对每个 marker 独立判断每个细胞是否阳性
  -> 得到 cell × marker 的 Nimbus score 矩阵
  -> 再用常规聚类/分型算法确定细胞类型
```

这样做有三个好处：

1. **面板无关。** 模型一次只看一个 marker，不需要固定通道顺序或固定 marker 集合。
2. **保留空间形态。** 模型可以利用膜环、核内信号、胞外结构和邻近串色，而不是只看一个均值。
3. **降低标签偏差的结构化传播。** 模型不知道一个细胞被原研究标成什么细胞类型，只学习单个 marker 的图像模式；错误细胞类型不会以完整组合规则直接灌入模型。

### 3. Pan-M：训练数据如何构造

作者整合五个多重成像数据集，构建 Pan-Multiplex（Pan-M）：超过 1.97 亿个 marker 标注、约 1,500 万个细胞、4 类组织、3 种成像平台、10 个大类谱系和 54 个 marker（`paper.md:91-105,181-187`）。

#### 3.1 银标准标签

对于 MIBI-TOF 和 CODEX，先利用原研究已经得到的细胞类型，再定义数据集特异的映射矩阵：

$$
A_d(t,m)\in\{0,1,\varnothing\},
$$

其中 $t$ 是细胞类型，$m$ 是 marker，0/1/未定义分别表示阴性、阳性或不能由该细胞类型确定。随后把每个细胞实例对应的像素填成 marker 语义掩膜。一个细胞会对多个 marker 贡献训练样本，平均约 13 个（`paper.md:196-205`）。

Vectra 数据没有先做细胞类型聚类，而是由病理专家逐 marker 设阈值，直接生成细胞级阳性/阴性标签（`paper.md:208-214`）。

这些标签称为 silver standard，因为它们继承原始聚类、门控和人工合并中的误差。

#### 3.2 金标准标签

作者从每个研究随机选取图像，在 QuPath 中逐细胞、逐通道校正银标准标签，并经过两轮专家一致性检查。金标准只用于测试，不用于训练（`paper.md:217-220`）。

本地代码中能看到谱系映射与 marker 定位类别（`ct_assignment.py:1-107`），但完整的 cell-type × marker 矩阵生成器和语义掩膜生成脚本仍为 **Not found**。

### 4. 输入、模型和输出

对某个 FoV 的某个 marker，输入是：

- 归一化后的单通道 marker 图像 $\widetilde I_{f,m}$；
- 细胞实例分割 $S_f$ 转换得到的二值细胞内部掩膜 $B_f$。

代码会去掉实例的内边界，再把图像和掩膜堆叠为两通道张量（`code/nimbus-core/src/cell_classification/inference.py:78-89`）：

$$
X_{f,m}(u)=\left[\widetilde I_{f,m}(u), B_f(u)\right].
$$

论文采用 Residual U-Net。网络对每个像素输出 sigmoid 置信度 $P_{f,m}(u)$，然后在细胞实例内取平均：

$$
z_{f,c,m}=\frac{1}{|\Omega_{f,c}|}\sum_{u\in\Omega_{f,c}}P_{f,m}(u).
$$

代码中的 `segment_mean` 正是这一聚合步骤，并丢弃背景实例（`code/nimbus-core/src/cell_classification/inference.py:92-109`）。最终每个 FoV 产生 `fov`、`label` 和多个 `<marker>_pred` 列（`inference.py:165-244`）。

### 5. 预处理

论文描述：

1. 用全数据集的通道级 99.99% 强度分位数归一化；
2. 将空间分辨率降低到原图面积的四分之一；
3. 裁成 $512\times512$ tile，并保留 16 像素重叠；
4. 训练数据写入 TFRecord（`paper.md:190-193`）。

原始代码实现了分位数归一化和通道级 normalization dictionary（`inference.py:15-75`），但默认参数是 `0.999`，即 99.9%，而不是论文写的 99.99%。三个固定代码快照中都没有发现 `0.9999`。因此机制是匹配的，默认数值是 **Partial**。

### 6. 两阶段训练

#### 6.1 噪声朴素预训练

第一阶段使用全部已定义银标准标签做二元交叉熵训练。模型构建代码包含：

- TensorFlow TFRecord 读取、数据集采样和 train/validation/test 拆分；
- Adam 优化器；
- cosine decay 学习率；
- 梯度裁剪；
- 弹性形变、翻转、旋转、亮度/对比度、Gaussian noise 和 blur（`model_builder.py:57-227,276-350`）。

论文报告学习率 $10^{-5}$、weight decay $10^{-4}$、batch size 28，先训练 100,000 step（`paper.md:238-244`）。但本地 `configs/params.toml` 是 `num_steps=20`、batch 4 的测试/示例配置，不能作为正式训练配置的证据。

#### 6.2 噪声鲁棒微调

核心想法是：如果模型对某个银标准标签产生持续高损失，可能是标签错了，不应继续强迫模型拟合。

先把像素损失聚合到细胞：

$$
\ell_c=\frac{1}{|\Omega_c|}\sum_{u\in\Omega_c}\ell(y_c,P(u)).
$$

然后对每个“数据集 × marker × 正负类别”分别维护损失分位数的指数移动平均：

$$
q^{(k)}_{d,m,y}=(1-\alpha)q^{(k-1)}_{d,m,y}
+\alpha Q_{\tau_k}(\{\ell_c\}).
$$

只有低于阈值的细胞进入 loss。实现位于 `promix_naive.py:268-344`。

此外还有 matched-high-confidence selection：

- 银标签为阳性且预测 > 0.9；
- 银标签为阴性且预测 < 0.1。

代码把 `[0.1, 0.9]` 转换成 BCE loss 阈值，并与分位数筛选结果取并集（`promix_naive.py:81-87,346-365`；`configs/params.toml:43-47`）。

论文称按 85th percentile 排除高损失细胞；示例配置却把保留分位数从 0.5 调度到 0.9。正式生产配置缺失，因此这个数值差异不能被强行解释为完全一致。

### 7. 推理过程

```text
marker TIFF + instance segmentation
  -> 通道分位数归一化
  -> 去边界的二值细胞内部 mask
  -> 0°/90°/180°/270°旋转 + 水平/垂直翻转
  -> 每个视图得到像素置信度
  -> 逆变换并平均
  -> 每个实例内求平均
  -> 细胞 × marker 分数表
```

TTA 的旋转、翻转、逆变换和平均在 `inference.py:112-162` 中直接实现。论文还描述大 FoV 的 artifact-free tile-and-stitch；聚焦源码中这一部分由 DeepCell application 层承接，因此代码验证为 **Partial**。

### 8. 结果应该如何解释？

Nimbus score 不是蛋白丰度，也不是完整细胞类型概率。它表示模型认为“该细胞对当前 marker 为阳性”的置信度。

它最有价值的地方，是把空间图像中的复杂模式压缩成更干净的单细胞特征：

- 周边弱膜信号：integrated expression 可能低，但 Nimbus 能识别形态；
- 邻近高亮信号串入：integrated expression 可能高，但 Nimbus 能判断当前细胞不是真阳性；
- 不同平台和 marker 定位：统一映射到 0–1 的阳性空间。

### 9. 评估与主要发现

作者用 held-out 金标准比较 precision、recall、specificity 和 F1，并与银标准、最优强度阈值、STELLAR、MAPS、Otsu、$k$-means、GMM、GammaGateR 等方法比较。

主要结果包括：

- Nimbus 在总体、组织和大多数谱系上的准确率接近银标准；
- 在 MIBI breast 与 CODEX colon 上，其他方法的 F1 通常比 Nimbus 低约 0.1；
- STELLAR/MAPS 跨数据集或缺失 marker 时明显下降，而逐通道 Nimbus 更稳定；
- Nimbus score 的阳性/阴性分布比 integrated expression 更分离；
- 在两个未参与训练的乳腺队列中，Nimbus + SOM/层次合并为 94.66% 的细胞分配了 cluster；
- 对 320 个两种流程不一致的细胞，专家更偏好 Nimbus 分型（65%），integrated expression 为 23%，两者都不对为 12%（`paper.md:115-154`）。

扩展图同时显示：不同 marker 的 F1 差异不小，Nimbus 并非每个通道都接近完美；运行时间也高于只计算 integrated expression。

### 10. 这项工作的真正创新在哪里？

创新不在“使用 U-Net”本身，而在任务分解：

```text
传统：固定 marker panel -> 直接预测 cell type -> 换 panel 需重训

Nimbus：任意单 marker 图像 -> 通用阳性 score -> 下游再聚类
```

它把“成像特有的噪声修正”和“生物学细胞类型发现”分离开。前者用统一预训练模型处理，后者继续使用成熟的单细胞聚类工具。

### 11. 代码和数据复现边界

本地固定了三套权威源码：

- `Nimbus-Inference`：面向用户的推理、viewer 和微调模板；
- `Nimbus`：原始 TensorFlow 训练、ProMix 式鲁棒筛选、推理和评估；
- `publications/...Nimbus`：Fig. 2–5 与扩展图的 6 个 notebook、谱系映射和小型结果表。

同时保留了 2 个补充 PDF、5 个 Source Data xlsx、14 张图和一个训练 checkpoint。完整 Pan-M 位于 Hugging Face，未在 workspace 中整库镜像。

需要明确保留的缺口：

- **Not found：**完整银标准语义掩膜生成器和 cell-type × marker 生产矩阵；
- **Not found：**正式 100k + 100k 训练配置；
- **Partial：**论文 99.99% 与代码默认 99.9% 的归一化差异；
- **Partial：**作图 notebook 依赖外部 Pan-M 大文件和 `gt_pred_ie_consolidated.csv`，本次只做结构与源码检查，未执行；
- **版本边界：**论文原始实现是 TensorFlow，当前 `Nimbus-Inference` 是后续 PyTorch 包装，不能混写成同一实现。

### 12. 使用时的现实限制

- 必须先有可靠的细胞实例分割；
- 只判断阳性/阴性，不适合区分中等与高表达；
- 不适用于训练中未见过的 H&E、IHC 或 spatial transcriptomics；
- 对远离 Pan-M 的组织与染色模式可能失效；
- 不负责决定 cluster 数、稀有亚群或聚类稳定性；
- 最稳妥的实际流程仍应先抽查多个 marker 的图像与 score overlay，再进行大规模聚类。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Nimbus

**Automated classification of cellular expression in multiplexed imaging data with Nimbus** — *Nature Methods* (2025), DOI `10.1038/s41592-025-02826-9`.

### What problem does it solve?

Cell phenotyping in multiplexed tissue images usually starts by averaging each marker's intensity inside every segmented cell. This integrated-expression scalar discards subcellular shape and local context, so it is vulnerable to spillover from neighbors, background staining, segmentation edges and large differences in marker brightness. Direct cell-type models such as STELLAR, MAPS and CellSighter also learn a particular marker panel and generally must be retrained for a new dataset.

Nimbus reframes the task. It predicts whether one marker is positive in one cell from the original marker image and the cell segmentation, processing each marker independently. The output is a continuous cell-by-marker positivity table that can be passed to ordinary clustering or phenotyping workflows.

### Main contribution

The study contributes two linked resources:

- **Pan-Multiplex (Pan-M):** more than 197 million marker annotations across 15 million cells, four tissues, three imaging platforms, ten broad lineages and 54 markers.
- **Nimbus:** a pretrained, noise-robust Residual U-Net that takes a normalized marker channel plus a binary cell-interior mask, predicts pixelwise sigmoid confidence, and averages that confidence within each cell.

The key conceptual advance is panel independence. Because Nimbus predicts one channel at a time rather than a complete cell type, a single model can be applied to different marker combinations without retraining.

### How it works

```text
source-study cell labels
  -> cell-type × marker assignment matrices
  -> silver-standard per-marker masks
  -> diverse Pan-M training set
  -> noise-naive U-Net training
  -> loss-quantile + matched-high-confidence fine-tuning

new marker image + instance segmentation
  -> high-quantile normalization
  -> eroded binary cell-interior mask
  -> flip/rotation test-time augmentation
  -> pixel positivity map
  -> mean score per cell
  -> cell × marker table
  -> clustering / cell phenotyping
```

The noise-robust stage computes loss per cell, maintains dataset-, marker- and class-specific moving loss thresholds, and excludes high-loss cells. Cells that agree with their silver labels at high confidence (>0.9 for positive and <0.1 for negative) are also retained.

### Evaluation and main results

Nimbus is evaluated on expert-corrected gold labels from held-out images across five Pan-M datasets. The paper reports that:

- aggregate precision, recall, specificity and F1 are comparable to the original silver-standard labels across tissues and nearly all lineages;
- Nimbus outperforms the evaluated supervised and unsupervised alternatives on MIBI breast and CODEX colon, with most alternative F1 scores roughly 0.1 lower;
- MAPS and STELLAR degrade strongly when transferred across datasets or when markers are removed, while channel-independent Nimbus remains stable;
- Nimbus scores separate gold-positive and gold-negative cells more cleanly than integrated expression, including dim/peripheral staining and spillover cases;
- Nimbus-score clustering assigns 94.66% of cells in two external breast cohorts, leaving 5.34% unassigned;
- among 320 discordant cells manually reviewed by two experts, the Nimbus-based phenotype was preferred for 65%, integrated expression for 23%, and neither for 12%.

The visual evidence is broad rather than uniform: many channels approach high F1, while Extended Data Fig. 2 exposes several difficult markers with substantially lower accuracy. Nimbus is also computationally slower than integrated expression alone, though the gap narrows when upstream integrated-expression computation is included for comparator methods.

### Why the method matters

Nimbus isolates the image-specific part of cell typing. It learns to correct the noisy spatial measurement before clustering, instead of asking a panel-specific model to learn cell identities and imaging artifacts simultaneously. That makes multiplexed imaging output look more like a conventional single-cell feature matrix while retaining information that a raw per-cell average loses.

### Code and data availability

Three authoritative code sources are retained at fixed revisions:

- `angelolab/Nimbus-Inference` — current user-facing inference, viewer and fine-tuning templates;
- `angelolab/Nimbus` — original TensorFlow data preparation, training, noise-robust selection, inference and evaluation;
- `angelolab/publications/2024-Rumberger_Greenwald_etal_Nimbus` — six paper figure notebooks, lineage mapping and small result tables.

The workspace also retains two supplementary PDFs, extracted supplementary text, five publisher Source Data spreadsheets, 14 figure images and a trained TensorFlow checkpoint. The full Pan-M dataset is externally hosted at `huggingface.co/datasets/JLrumberger/Pan-Multiplex` and is not mirrored locally.

### Reproducibility assessment: 4/5

**Code-paper fidelity: medium-high.** The central training, noise-robust selection, TTA and per-cell aggregation logic are directly inspectable, and inference has user-facing notebooks plus a retained checkpoint. All six declared paper notebooks are present after acquisition repair.

The remaining gaps are material but clearly bounded:

- the full silver-standard semantic-mask generator and assignment matrices are **Not found**;
- the exact production training config (100k + 100k steps, batch 28, published weight decay/backbone selection) is **Not found**; the retained config is an example/test file;
- the paper specifies 99.99th-percentile normalization, while retained code defaults to 99.9%; this is **Partial** agreement;
- paper notebooks require large external Pan-M inputs and a consolidated results table, so they were inspected but not executed;
- the original TensorFlow implementation and newer PyTorch package must not be conflated.

Inference is therefore well supported; exact end-to-end retraining from raw source datasets requires reconstruction of missing labeling and production-configuration details.

### Limitations

- Nimbus depends on a precomputed instance segmentation and inherits segmentation errors.
- It predicts positive versus negative marker status, not calibrated abundance or high-versus-medium expression.
- It is not expected to generalize to unseen modalities such as H&E, immunohistochemistry or spatial transcriptomics.
- Performance may decline for tissues or staining patterns far outside Pan-M.
- Nimbus does not solve downstream clustering choices, rare-population discovery or nondeterministic cluster merging.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
