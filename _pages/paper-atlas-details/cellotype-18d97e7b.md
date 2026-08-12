---
layout: default
permalink: /paper-atlas/cellotype-18d97e7b/
title: "CelloType"
nav: false
description: "CelloType 的真正创新点是把多通道组织图像中的“找对象、画边界、判类别、给置信度”变成一个共享查询和共享特征的联合学习问题；实验显示这种统一建模明显优于两阶段流水线，但分类迁移能力、训练数据需求和严格的全流程复现仍然是主要限制。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>CelloType</h1>
    <p>CelloType: a unified model for segmentation and classification of tissue images</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CelloType 方法详解

### 1. 它要解决什么问题？

空间组学图像分析通常把两个任务串起来做：

1. 先找出每个细胞的边界；
2. 再根据分割结果判断细胞类型。

这个两阶段流程有一个根本问题：第二步只能看到第一步裁出的细胞或汇总特征，一旦分割漏掉细胞、合并相邻细胞或画错边界，分类误差就会被放大。与此同时，分类信息本来可以反过来帮助分割——不同细胞和组织结构具有不同的形态、纹理和标志物组合，但传统流程没有让两个任务共同学习。

已有方法大多只覆盖其中一部分。例如 Mesmer（*Nature Biotechnology*, 2022）和 Cellpose2（*Nature Methods*, 2022）主要解决细胞/细胞核分割；CellSighter（*Nature Communications*, 2023）和 CELESTA（*Nature Methods*, 2022）依赖已有分割结果进行细胞类型注释。它们很难用一个统一模型同时处理多通道图像、紧密相邻细胞、转录本信号以及尺寸远大于细胞的非细胞结构。

CelloType 的目标是：对一张组织图像一次性输出每个实例的边界框、像素级掩膜、类别和置信度。

### 2. 核心思想

CelloType 把 Swin Transformer、DINO 和 MaskDINO 组合成一个端到端实例模型：

```text
组织图像（1、2 或几十个通道）
          │
          ▼
Swin-L 多尺度特征提取
          │
          ▼
DINO / MaskDINO 编码器
  展平多尺度特征并加入空间位置
          │
          ▼
选择最可能包含对象的 top-K 查询
  查询内容 + 初始锚框
          │
          ▼
可变形注意力解码器
  逐层修正边界框
  训练时加入带噪声的真值查询
          │
          ├── 分类头 → 细胞/结构类别
          ├── 边界框头 → 对象位置
          └── 掩膜头 → 像素级实例边界
          │
          ▼
置信度过滤后的 boxes + masks + classes + scores
```

统一训练的价值在于共享表征：分割提供精细的像素结构，帮助检测器初始化更好的框；检测和分类让掩膜分支聚焦于真正的对象区域，并利用类别相关的形态和通道模式。

### 3. 输入与输出

输入图像记为 $I\in\mathbb{R}^{H\times W\times C}$。通道数 $C$ 取决于任务：

- 细胞/细胞核分割：核或膜的一到两个通道；
- 多重蛋白成像：几十个抗体通道；
- Xenium/MERFISH：DAPI、转录本位置或转录本密度图；
- 多尺度组织注释：同时包含小细胞、脂肪细胞和骨小梁等结构。

模型输出实例集合

$$
\mathcal{Y}=\{(b_i,m_i,c_i,s_i)\}_{i=1}^{N},
$$

其中 $b_i$ 是边界框，$m_i$ 是二值掩膜，$c_i$ 是类别，$s_i$ 是置信度。

### 4. 多尺度特征：为什么用 Swin-L？

Swin Transformer 用移位窗口注意力建立层级特征。浅层保留边缘和局部纹理，深层编码更大范围的组织上下文，因此适合同时处理小细胞和大结构。论文使用在 COCO 实例分割上预训练的 Swin-L。

代码配置确实选择了 `D2SwinTransformer`，大模型参数为 embedding 192、深度 `[2,2,18,2]`、注意力头 `[6,12,24,48]`。虽然配置文件名含有 `R50`，实际启用的是 Swin-L。代码还通过 `MODEL.IN_CHANS` 改变输入通道数；CODEX 训练入口把它设置为 92，这就是模型适配高维多重成像的机制。

### 5. 查询初始化：从哪里开始找细胞？

论文把混合查询写成

$$
{Q}_{\text{pos}}={f}_{\text{encoder}}(X\,),\qquad
{Q}_{\text{content}}=\text{learnable}.
$$

$Q_{\text{pos}}$ 表示初始框的位置，$Q_{\text{content}}$ 表示对象内容。直观地说，模型先在所有空间位置上判断“哪里可能有对象”，选择得分最高的 top-$K$ 位置，再让解码器围绕这些候选位置提取对象特征。

代码中的两阶段解码器确实会：

1. 对编码后的所有空间位置预测类别和框；
2. 选择 top-$K$ 候选；
3. 把候选框作为 reference boxes；
4. 把相应的编码特征作为初始内容查询。

这里存在一个细节差异：论文文字强调内容查询保持为可学习向量，而当前默认代码 `LEARN_TGT=False`，内容主要来自选中的编码特征。因此总体策略吻合，但默认实现不是论文公式最字面的版本。

### 6. 逐层修正边界框

DINO 使用可变形注意力，只在参考框附近和少量多尺度采样点上聚合信息，而不是让每个查询看整张图像。第 $\ell$ 层的更新可以概括为

$$
b_{\ell+1}=\sigma\!\left(\delta_\ell+\sigma^{-1}(b_\ell)\right),
$$

其中 $b_\ell$ 是当前参考框，$\delta_\ell$ 是本层预测的修正量。代码逐层执行这一更新，并允许早期掩膜先转换成框，再作为解码器初始框。后者使像素级分割信息能够在训练早期反过来帮助检测。

### 7. 去噪训练

论文给真值框加入受控噪声：

$$
|\Delta x| < \lambda \frac{w}{2},\quad
|\Delta y| < \lambda \frac{h}{2},\quad
|\Delta w| < \lambda w,\quad
|\Delta h| < \lambda h.
$$

这样模型不仅学习“从一个好框继续修正”，还学习从错误标签和偏移框中恢复。代码会复制真值对象、随机替换部分标签、按框尺寸扰动中心和宽高，并用注意力掩膜隔离不同去噪组。

论文还描述正负样本的两个噪声尺度 $\lambda_1=0.4$ 和 $\lambda_2=1$。当前代码只暴露一个命名参数 `DN_NOISE_SCALE=0.4`，没有找到第二个独立尺度，所以去噪机制存在，但两尺度叙述不是完全一一对应。

### 8. 分类、掩膜与置信度

#### 分类

论文写的是 $K+1$ 类 logits（含“无对象”类）并使用 SoftMax：

$$
{\rm SoftMax}(z_i)=\frac&#123;&#123;\mathrm e}^{z_i}}
{\sum_{j=1}^{K+1}{\mathrm e}^{z_j}}.
$$

论文把最大的非背景类别概率定义为置信度。

代码中确实有线性分类头，但默认实例推理使用每类 sigmoid 分数，而不是上述 SoftMax。更重要的是，最终实例分数还会乘上掩膜前景区域的平均概率，因此代码中的置信度同时反映“类别确信度”和“掩膜质量”。这可能解释了置信度排序很有效，但它与论文 Methods 中的公式并不完全相同。

#### 掩膜

论文的掩膜公式为

$$
m={q}_{\mathrm c}\otimes M\!\left(T(C_{\mathrm b})+F(C_{\mathrm e})\right).
$$

含义是：把每个对象查询 $q_c$ 映射为一个掩膜向量，再与高分辨率像素特征逐点做内积。代码直接用

```python
torch.einsum("bqc,bchw->bqhw", mask_embed, mask_features)
```

实现这一过程，是论文与代码最清晰的精确对应之一。

### 9. 联合损失

论文把目标函数概括为

$$
\text{Loss}={\lambda}_{\text{cls}}L_{\text{cls}}
+{\lambda}_{\text{box}}L_{\text{box}}
+{\lambda}_{\text{mask}}L_{\text{mask}}.
$$

代码展开后包含：

- 分类损失；
- 掩膜像素损失和 Dice 损失；
- 边界框 L1 损失和 GIoU 损失；
- 中间候选、去噪查询和每个解码层的辅助损失。

因此论文的三项公式是概念分组，真实训练目标更细。当前配置的主要权重为分类 4、mask 5、Dice 5、box 5、GIoU 2。

### 10. 训练与推理中的关键差异

论文和代码在训练设置上不是完全统一：

- 论文通用描述为 Adam、学习率 $10^{-6}$、batch 8，并在验证 AP 连续 15 个 epoch 不改善时停止；
- 代码默认是 AdamW、学习率 $10^{-4}$、固定迭代次数和每 500 次迭代评估；
- Xenium/MERFISH 的论文设置本身也使用 $10^{-4}$ 和固定 20,000/5,000 次迭代。

另一个重要差异是查询数。论文说测试时使用 1,000 个 queries，但当前模型配置 `NUM_OBJECT_QUERIES=300`；`DETECTIONS_PER_IMAGE=1000` 只是保留候选“查询×类别”分数的上限，不等价于 1,000 个独立实例查询。

### 11. 实验结果应该怎样理解？

- **TissueNet：** CelloType_C 的细胞/细胞核 mean AP 为 0.56/0.66，高于 Cellpose2 的 0.35/0.52 和 Mesmer 的 0.31/0.24。
- **Cellpose Cyto：** CelloType_C mean AP 0.47，覆盖荧光、明场、其他显微和非显微对象。
- **Xenium：** DAPI+转录本 mean AP 0.47；只有转录本时约 0.02，说明形态通道仍然关键。
- **MERFISH：** DAPI+转录本从 0.40 提升到 0.44，转录本提供的是增量信息。
- **结直肠 CODEX 联合任务：** CelloType mean AP 0.55，高于 Mask R-CNN 0.43 和 Cellpose2+CellSighter 0.13。
- **骨髓 CODEX：** 一个模型同时处理小细胞、脂肪细胞和骨小梁，但不同结构的精度并不均一。

置信度越高、准确率越高的趋势在结直肠和骨髓数据上都很明显。不过要注意：图中证明的是“这个分数具有排序价值”，并不能证明论文给出的 SoftMax 公式就是代码实际使用的分数。

### 12. 复现性与局限

代码与论文总体匹配度为 **中等**。核心 Swin/MaskDINO 架构、框迭代、掩膜内积、多通道接口、训练/测试入口和预训练权重下载都存在；但完整复现仍有明显障碍：

- 依赖 Python 3.8、PyTorch 1.9、CUDA 11.1、Detectron2 和需要编译的可变形注意力算子；
- 仓库没有包含论文使用的全部数据、交叉验证划分、处理后的标注和一键 benchmark/绘图流程；
- README 和 `setup.py` 仍含有指向另一个 GitHub owner 的旧链接；
- 没有找到论文所述的 AP early stopping、两个独立去噪尺度或 1,000-query 配置。

### 13. 一句话总结

CelloType 的真正创新点是把多通道组织图像中的“找对象、画边界、判类别、给置信度”变成一个共享查询和共享特征的联合学习问题；实验显示这种统一建模明显优于两阶段流水线，但分类迁移能力、训练数据需求和严格的全流程复现仍然是主要限制。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## CelloType

### Problem

Spatial-omics image analysis usually treats cell segmentation and cell-type annotation as two separate tasks. Errors from the first stage propagate into the second, classification cannot use the full image context, and two independent models must be trained. Existing tools illustrate this split: Mesmer (*Nature Biotechnology*, 2022) and Cellpose2 (*Nature Methods*, 2022) focus on segmentation, while CellSighter (*Nature Communications*, 2023) and CELESTA (*Nature Methods*, 2022) annotate cells after segmentation. These methods also struggle to provide one model for tightly packed cells, multiplexed images, transcript-derived signals and much larger noncellular tissue structures.

### Proposed method

CelloType is an end-to-end transformer model that jointly performs object detection, instance segmentation and classification. A Swin-L backbone extracts multiscale features; DINO/MaskDINO selects object queries, refines anchor boxes with deformable attention and denoising, and produces class logits and boxes; a mask head combines decoded query embeddings with high-resolution pixel features to produce instance masks. Training jointly optimizes class, box and mask objectives, allowing segmentation and classification to share representations.

Inputs can range from one- or two-channel cell/nuclear images to multiplexed protein images and DAPI/transcript composites. Outputs are instance masks, boxes, predicted cell/structure types and confidence scores. The same architecture is applied to cells, nuclei, adipocytes, trabecular bone and other microanatomical structures.

### Evaluation and main results

The paper evaluates CelloType with AP over IoU thresholds 0.50–0.90 using cross-validation and compares it with Mesmer, Cellpose2, SCS, Baysor, Cellpose2+CellSighter and Mask R-CNN.

- **TissueNet:** confidence-aware CelloType_C reaches mean AP 0.56 for cell segmentation and 0.66 for nuclear segmentation, versus 0.35/0.52 for Cellpose2 and 0.31/0.24 for Mesmer.
- **Cellpose Cyto:** CelloType_C reaches mean AP 0.47, compared with 0.37 for unscored CelloType and 0.32 for Cellpose2 across diverse microscopy and nonmicroscopy subsets.
- **Xenium:** DAPI+transcript CelloType reaches mean AP 0.47; transcript-only CelloType, SCS and Baysor are near 0.01–0.02, showing that transcript signal alone is insufficient in this setting.
- **MERFISH:** DAPI+transcript input improves nuclear segmentation from mean AP 0.40 to 0.44 relative to DAPI alone.
- **Colorectal CODEX joint task:** CelloType achieves mean AP 0.55 across 11 cell types, versus 0.43 for Mask R-CNN and 0.13 for Cellpose2+CellSighter. Its confidence threshold has a substantially stronger relationship with accuracy.
- **Bone-marrow CODEX:** one model segments/classifies small cells, adipocytes and trabecular bone, with mean AP 0.39, 0.31 and 0.42 for adipocytes, trabecular bone and remaining cell types, respectively.

The figures also show important qualifications: performance varies by image/platform and object class; CelloType requires more memory and training time than the simpler baselines; accuracy declines gradually as the number of classes increases; and classification transfer is limited when new tissues contain unseen cell types.

### Paper–code fidelity

Overall fidelity is **medium**. The paper-linked repository at commit `eb7dc8417a5c130c31b66eba71c3c3f112c22c7d` contains the Swin-L MaskDINO architecture, query selection, iterative box refinement, denoising queries, mask dot product, joint losses, multichannel entry points, pretrained-weight downloader and inference examples. Core architectural claims are directly visible in source.

Several manuscript details do not match the checked defaults exactly:

- the paper defines confidence as maximum SoftMax class probability, while code uses sigmoid class scores multiplied by mean mask probability;
- the paper states 1,000 evaluation queries, while the model config has 300 queries and a separate 1,000-detection cap;
- the paper gives two denoising scales (0.4 and 1), while code exposes one named scale of 0.4;
- the general Methods section describes Adam at $10^{-6}$ and AP-based early stopping, while code defaults to AdamW at $10^{-4}$ with a fixed iteration schedule.

### Reproducibility

**Rating: 3/5.** Public code, model weights, package metadata, preprocessing scripts, dataset-specific train/test entry points and small example images are available. However, the snapshot requires an old GPU-specific stack (Python 3.8, PyTorch 1.9, CUDA 11.1, Detectron2 and compiled deformable-attention operators), and the full study datasets, fold assignments, processed annotations, benchmark driver and plotting pipeline are not included. The README also contains stale clone/package URLs pointing to a different GitHub owner.

The repository is sufficient to inspect and likely run model inference after environment setup and weight download, but it is not a turnkey reproduction of every reported cross-validation result or figure.

### Bottom line

CelloType’s main contribution is not a new segmentation head in isolation, but the adaptation of a unified DINO/MaskDINO transformer to multichannel tissue images so that boxes, masks, classes and confidence are learned together. The experimental evidence supports broad segmentation gains and a clear advantage over a two-stage segmentation-plus-classification baseline, while transfer to new classifications and exact benchmark reproducibility remain the principal limitations.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
