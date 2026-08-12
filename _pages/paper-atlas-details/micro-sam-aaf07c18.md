---
layout: default
permalink: /paper-atlas/micro-sam-aaf07c18/
title: "micro-sam"
nav: false
description: "显微图像分割的困难不只是“把细胞圈出来”，而是成像模态、目标形态和数据维度差异很大：光学显微镜（LM）与电子显微镜（EM）不同，二维图像、三维体数据和时间序列也需要不同操作。CellPose、StarDist 等专用方法在接近训练分布的数据上很强，但遇到新条件时性能会下降；重新训练又需要大量人工标注。原始 SAM 虽然能用点或框交互分割，但它主要在自然图像上训练，对显微镜中的密集、相邻或细小目标并不稳定。"
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
    <h1>micro-sam</h1>
    <p>Segment Anything for Microscopy</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## μSAM：面向显微图像的 Segment Anything

### 它要解决什么问题？

显微图像分割的困难不只是“把细胞圈出来”，而是成像模态、目标形态和数据维度差异很大：光学显微镜（LM）与电子显微镜（EM）不同，二维图像、三维体数据和时间序列也需要不同操作。CellPose、StarDist 等专用方法在接近训练分布的数据上很强，但遇到新条件时性能会下降；重新训练又需要大量人工标注。原始 SAM 虽然能用点或框交互分割，但它主要在自然图像上训练，对显微镜中的密集、相邻或细小目标并不稳定。

μSAM 的目标是把“自动产生初始结果—人工快速纠错—用新标注继续训练”连成一个统一工作流，并尽量让同一套模型接口覆盖 LM、EM、2D、3D 和跟踪任务。

### 核心创新

1. **按交互过程微调 SAM。** 训练时不只使用固定框提示，而是模拟用户逐步纠错：先给一个点或框，再从当前预测的漏分区域采正点、从误分区域采负点，连续迭代。
2. **随机使用上一轮掩膜。** 上一轮低分辨率掩膜以 50% 概率作为下一轮提示，避免模型过度依赖 mask prompt，从而兼容“有掩膜”和“只有多个点”两种交互方式。
3. **增加自动实例分割（AIS）解码器。** 在 SAM 图像编码器后接一个 UNETR 风格解码器，输出前景、中心距离和边界距离三张图，再用种子分水岭得到实例。
4. **联合训练交互与自动分割。** 两个任务共享图像编码器，使自动建议和交互纠错同时受益。
5. **统一工具链。** Python 库和 napari 插件支持二维、三维、高通量标注、跟踪和用户微调。

### 整体流程

```text
显微图像
   │
   ├─ 灰度复制为 3 通道 / 归一化 / 缩放
   ▼
SAM 图像编码器 ───────────── 缓存 embedding
   │                              │
   │                              ├─ 点/框/mask 提示
   │                              │      ▼
   │                              │   交互目标掩膜
   │                              │      │
   │                              │   从错误区域采纠错点并迭代
   │                              │
   └─ UNETR 风格 AIS 解码器
          ├─ 前景概率
          ├─ 中心距离
          └─ 边界距离
                    ▼
             阈值 + 种子分水岭
                    ▼
              自动实例分割
                    ▼
             napari 中人工纠错
                    ▼
             可选：用新标注再训练
```

### 交互微调如何工作？

每次训练先从实例标注中抽取有限数量的对象，以控制显存。初始提示是对象内部的正点或对象框。SAM 预测掩膜和预测 IoU，损失为掩膜 Dice 损失与 IoU 回归的 L2 损失之和：

$$
\mathcal{L}_{\mathrm{interactive}}
=\mathcal{L}_{\mathrm{Dice}}(\hat{Y},Y)
+\mathcal{L}_{2}(\widehat{\mathrm{IoU}},\mathrm{IoU}(\hat{Y},Y)).
$$

然后从假阴性区域采一个正点，从假阳性区域采一个负点，把它们追加到已有提示中。论文默认重复八个子迭代，并对各轮损失取平均。代码中图像 embedding 只计算一次，各轮只重新运行提示编码器和掩膜解码器，因此符合交互应用的计算模式。

单点提示可能对应整个对象或对象的一部分，所以 SAM 会给出三个候选掩膜。实现根据预测 IoU 选择候选，并计算 Dice 与 IoU 回归损失。上一轮低分辨率 mask 默认以 0.5 概率输入下一轮，这是 μSAM 相比简单 SAM 微调方案的重要细节。

### AIS 为什么需要三张图？

只预测前景无法可靠拆开接触对象。μSAM 同时预测：

- $F(x)$：像素属于目标的概率；
- $D_c(x)$：到对象中心的归一化距离；
- $D_b(x)$：到对象边界的归一化距离。

中心距离与边界距离共同产生 watershed 种子，前景阈值形成分水岭掩膜。边界信息能减少相邻细长对象被合并，中心信息能减少非凸对象被错误切成多块。当前代码的通道顺序是“前景、中心距离、边界距离”，随后调用基于中心/边界距离的 seeded watershed。

AIS 与交互分割使用同一批图像和同一编码器。联合训练器先反向传播交互损失，再反向传播三通道距离/前景损失。论文比较了顺序训练方案，发现如果后续 AIS 更新编码器会损害交互能力，而冻结编码器又会限制 AIS，因此联合训练效果最好。

### 推理与实际标注

自动模式先缓存图像 embedding，再运行 AIS、AMG 或其他生成器。二维输入直接生成实例；三维数据按多维逻辑处理。若启用 `annotate`，自动结果会直接载入 napari 的 2D 或 3D 标注器，用户用点、框等提示修正，最终从 `committed_objects` 图层保存结果。这样自动分割不是终点，而是降低人工操作量的起点。

### 如何评价？

论文使用对象级分割准确率：

$$
\mathrm{SA}(t)=\frac{\mathrm{TP}(t)}{\mathrm{TP}(t)+\mathrm{FP}(t)+\mathrm{FN}(t)}.
$$

平均分割准确率把 IoU 阈值 $t=0.50$ 到 $0.95$（步长 0.05）的 $\mathrm{SA}(t)$ 取平均。交互评估模拟连续纠错；自动评估在验证集上搜索 AIS/AMG 阈值，再用于测试集。

LIVECell、多个 LM/EM 数据集以及未直接出现在训练集的条件都显示：微调后的 specialist/generalist 模型明显优于默认 SAM。AIS 在不少任务上可与 CellPose 等自动方法竞争，但在小目标、密集目标和陌生域上仍可能失败。三项用户研究展示了 2D 类器官、3D EM 细胞核和荧光跟踪中的实际标注效率。

### 怎样理解论文结论？

μSAM 最有价值的地方不是“一个模型完全自动解决所有显微分割”，而是把强大的通用表示、自动初始结果和低成本交互纠错结合起来。自动结果不够好时，用户可以用提示快速修正；修正结果又能成为新训练数据。它更像一个可迭代的标注与建模平台。

### 局限与复现边界

- 当前架构仍需分别训练 LM 和 EM generalist，尚未得到统一跨模态模型。
- SAM 固定三通道输入不适合任意多通道显微数据；论文对双通道数据采用平均后复制，会损失信息。
- 自动分割的质量依赖数据域、目标大小和阈值；交互模式是重要兜底。
- 本地代码与论文方法高度一致，但获取的是当前 commit `a731082…`，未确认是所有论文实验的精确历史版本。
- 模型权重、完整数据和部分实验配置需要外部下载；Supplementary Information 未转换为本地 Markdown，因此补充材料独有细节仍是已知缺口。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Segment Anything for Microscopy (μSAM)

### Overview

μSAM adapts the Segment Anything Model to microscopy and packages interactive segmentation, automatic instance segmentation, multidimensional annotation, tracking and user fine-tuning into one napari-centered system. The paper addresses a persistent bioimage-analysis problem: strong specialist tools exist, but their accuracy drops outside their training distribution, annotation for retraining is slow, and separate workflows are often needed for LM, EM, 2D, 3D and time series.

The core idea is to retain SAM’s promptable image encoder/prompt encoder/mask decoder while fine-tuning it with simulated iterative corrections. μSAM also attaches a UNETR-style decoder to the shared image encoder. That decoder predicts foreground, distance to object centers and distance to object boundaries; thresholding and seeded watershed convert these maps into automatic instances. Automatic masks can then be corrected interactively and reused as training data.

### What Is New

- An open implementation of iterative SAM fine-tuning that trains point, box and repeated correction behavior instead of specializing to one prompt type.
- Probabilistic reuse of the previous mask prompt, preventing the model from becoming dependent on mask inputs during multi-point correction.
- Joint training of promptable segmentation and a three-channel automatic instance-segmentation decoder.
- Separate LM and EM generalist models that improve over default SAM across diverse datasets.
- A unified napari/Python workflow for 2D, volumetric, high-throughput and tracking annotation, plus model retraining.

### Evidence and Results

Experiments use LIVECell and diverse LM and EM datasets, including both represented and unseen imaging conditions. Evaluation covers simulated point/box correction, automatic mask generation (AMG), the proposed AIS, comparisons with tools such as CellPose, and three user studies. The principal metric is mean segmentation accuracy, averaging object-level segmentation accuracy across IoU thresholds from 0.50 to 0.95.

Figures 2–4 show that fine-tuned specialist and generalist models consistently improve promptable segmentation over default SAM; AIS is often comparable to established automatic methods, though difficult datasets still have low automatic scores. Figure 5 shows practical resource trade-offs and the value of cached embeddings. Figure 6 demonstrates shorter or competitive annotation workflows for organoid segmentation, 3D EM nuclei and fluorescence tracking. The evidence supports a versatile annotation platform, not a claim that one checkpoint solves every modality: the authors train separate LM and EM generalists, and multichannel inputs remain awkward.

### Code–Paper Match

Overall fidelity is **high**. The acquired `micro-sam` code directly implements the paper’s key mechanisms:

- eight-sub-iteration-capable prompt correction with error-derived points;
- Dice mask loss plus IoU-regression loss;
- previous-mask prompting sampled with probability 0.5 by default;
- interleaved interactive and AIS optimization using a shared encoder;
- three decoder maps and seeded-watershed instance construction;
- cached embeddings and automatic-to-napari correction.

The main caveat is versioning: the local code is current commit `a7310821ffd5b17f6dcbadb1e5a1a8e0e5f2a5aa`, not a confirmed frozen paper revision. Reproducing every figure also requires external datasets, checkpoints and experiment-specific configurations.

### Reproducibility Assessment: 4/5

The paper supplies an open, substantial library and clear method descriptions; core algorithms are traceable to source lines, and the code supports training and inference. One point is withheld because the exact historical experiment snapshot is not established locally, large assets are external, and supplementary information was not converted into the workspace. These are documented gaps rather than evidence that the implementation is absent.

### Main Limitations

- Separate LM and EM generalist models are needed; a single cross-modality model was not successful with the current architecture.
- SAM’s three-channel input causes information loss or awkward mappings for multichannel microscopy.
- Fully automatic results remain task-dependent, especially for small, dense or unfamiliar objects; interaction is often the robust fallback.
- User studies are practical demonstrations with limited annotator/task scope, not a comprehensive usability benchmark.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
