---
layout: default
permalink: /paper-atlas/dvd-f68adad7/
title: "DVD"
nav: false
wide: true
description: "常规视觉模型从训练开始就接收清晰、彩色、高对比度图像，容易依赖局部纹理而不是整体形状，因此在形状-纹理冲突、图像退化、抽象形状识别和对抗攻击下与人类表现差异很大。DVD（Developmental Visual Diet）的核心问题是：如果把人类从新生儿到成年期的视觉成熟过程变成训练课程，能否让普通视觉网络学习更偏向全局形状、更稳健的特征？ 过去方法常把低视力简化为一个或几个固定模糊阶段。"
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
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>DVD</h1>
    <p>Adopting a human developmental visual diet yields robust and shape-based AI vision</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/KietzmannLab/DVD" target="_blank" rel="noopener noreferrer" aria-label="Open code for DVD">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DVD 方法详解：用人类视觉发育轨迹训练更稳健的视觉模型

### 1. 研究问题

常规视觉模型从训练开始就接收清晰、彩色、高对比度图像，容易依赖局部纹理而不是整体形状，因此在形状-纹理冲突、图像退化、抽象形状识别和对抗攻击下与人类表现差异很大。DVD（Developmental Visual Diet）的核心问题是：如果把人类从新生儿到成年期的视觉成熟过程变成训练课程，能否让普通视觉网络学习更偏向全局形状、更稳健的特征？

过去方法常把低视力简化为一个或几个固定模糊阶段。本文进一步同时建模连续变化的视敏度、对比敏感度和色彩敏感度，并强调发育顺序，而不只是随机加入退化增强（`paper.md:20-31,181-235`）。

### 2. 输入、输出与整体流程

- 输入：RGB 图像批次 (I\in[0,1]^{B\times3\times H\times W})、当前发育年龄 (t)（月）、分类标签。
- 输出：经过年龄相关视觉变换的 RGB 图像，再送入任意 CNN/ViT 完成分类训练。
- 主要超参数：(alpha) 为每个 epoch 对应的发育月数，(\beta) 为新生期频域阈值强度，(lambda) 控制阈值随年龄衰减的映射。

```text
训练图像
  -> 按 epoch/batch 取得年龄 t
  -> 视敏度：高斯模糊
  -> 对比敏感度：FFT 频谱阈值过滤
  -> 色彩敏感度：灰度与 RGB 插值
  -> 分类网络前向传播
  -> 分类损失、反向传播、参数更新
```

代码中，`generate_age_months_curve` 为每个 batch 生成年龄；`train_one_epoch` 在网络前向传播前调用 `DVDTransformer`（`DVD_code/dvd/dvd/development.py:201-229`; `DVD_code/scripts/main.py:335-435`）。测试阶段统一使用高分辨率图像，不再模拟婴儿视觉（`paper.md:48`）。

### 3. 三个发育变换

#### 3.1 视敏度：高斯模糊

论文根据 Snellen 视力把年龄映射为模糊尺度：

$$\sigma(w,x)=\frac{4\times(20/600)\times w}{100\times x},$$

其中 (w) 是图像宽度，(x) 是 Snellen 视力，(sigma) 越大表示视力越差（`paper.md:187-196`）。代码用双指数函数直接返回年龄对应的 (sigma)，再按 `image_size/224` 缩放，使用反射边界进行高斯模糊（`DVD_code/dvd/dvd/development.py:52-60,123-136`）。

#### 3.2 对比敏感度：频域阈值

论文对每个 RGB 通道做离散傅里叶变换，并用年龄相关阈值去掉低于可见强度的频率成分：

$$T_t=\frac{P_{\max}\beta(1-C_t)}{\left(\left\lfloor\frac{t}{\lambda}\right\rfloor,1\right)},$$

其中 (P_{\max}) 是当前图像的最大频谱功率，(C_t\in[0,1]) 是年龄 (t) 的归一化对比敏感度。低于 (T_t) 的频率被置零，再经逆 FFT 重建图像（`paper.md:199-211`）。

代码确实完成了 FFT、功率谱、硬阈值、逆 FFT 和 `[0,1]` 截断，但分母具体实现为 `max(1, 2*(age_months // lambda))`，因此属于论文公式的 **Partial** 匹配，而不是逐字等价实现（`DVD_code/dvd/dvd/development.py:148-165`）。控制实验表明，对比敏感度是产生形状偏置和稳健性的主要因素；三因素组合的整体表现最稳定（`paper.md:148-160`; Fig. 4）。

#### 3.3 色彩敏感度：灰度到彩色的连续插值

论文定义：

$$I_t=(1-S_t)\times I_{\mathrm{grey}}+S_t\times I_{\mathrm{RGB}},$$

其中 (S_t\in[0,1]) 是年龄相关的色彩敏感度。早期图像接近灰度，随后逐渐恢复完整色彩（`paper.md:214-223`）。代码与该公式直接对应（`DVD_code/dvd/dvd/development.py:138-147,174-180`），并额外提供基于 Lab 色差 ΔE 的阈值模式（`development.py:182-194`）。

### 4. 发育课程如何进入训练

年龄曲线按

`epoch * months_per_epoch + batch * months_per_epoch / batches_per_epoch`

生成，因此每个 batch 都能看到稍有变化的视觉成熟程度（`development.py:201-216`）。代码还支持按时间打乱、`mid_phase` 排序和 `fully_random`。值得注意的是，`fully_random` 模式会在模糊、色彩、对比三个步骤中分别重新抽样年龄，因此三个感觉维度不一定共享同一个 (t)（`development.py:123-151`）；这是代码行为，不是论文主实验的明确设定。

论文在 mini-ecoset 上扫描 (alpha\in\{1,2,4,8\})、(\beta\in\{5\times10^{-5},10^{-4},2\times10^{-4},4\times10^{-4}\})、(lambda\in\{50,100,150\})，选出 DVD-S、DVD-B、DVD-P 后直接迁移到 ecoset、ImageNet-1K 和其他架构（`paper.md:226-235`）。

### 5. 结果应该怎样理解

DVD 不是通过新网络结构获得收益，而是改变训练早期可见的信息。ecoset 上，ResNet-50 基线的形状偏置为 0.34；DVD-P、DVD-B、DVD-S 分别达到 0.70、0.83、0.90，其中 DVD-S 进入人类范围（`paper.md:65`; Fig. 2）。该趋势跨三个数据集和九种 CNN/ViT 架构保持（Fig. 3）。

在 IllusionBench 中，DVD-S 的抽象形状召回率为 36.21%，高于 ResNet-50 基线 8.71%、最佳测试 ViT 17.13% 以及论文列出的多模态基础模型；其场景召回下降到 20.07%，说明表征更偏向整体形状而不是背景（`paper.md:105-119`; Fig. 5）。DVD-B 在 16 类图像退化和六类黑盒/白盒攻击下也普遍优于基线（`paper.md:122-151`; Fig. 6）。

### 6. 论文主张、代码证据与缺口

- **论文主张**：按真实发育顺序逐渐释放高频、低幅度频率和色彩信息，会形成持续的形状优先表征；随机打乱同一组敏感度值效果更差（`paper.md:93,163`）。
- **代码确认**：三阶段变换、年龄曲线、逐 batch 调用、训练更新、验证和 checkpoint 中保存年龄曲线均可直接定位到源代码。
- **缺失证据**：仓库没有论文的形状偏置、IllusionBench、Grad-CAM/LRP、腐蚀和对抗攻击完整分析脚本；没有单元测试、模型权重或本地补充材料 Markdown。
- **外部依赖**：稳健性数据加载器写有 `/home/student/...` 和 `/share/klab/...` 的绝对 HDF5 路径；新图像评估也需要外部 checkpoint 和类别名称文件（`DVD_code/dvd/datasets/dataset_loader.py:47-123`; `DVD_code/scripts/eval_new_images.py:171-211`）。

因此，当前快照足以学习、检查并移植 DVD 核心预处理课程，但不足以从零复现论文全部六张主图和补充实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DVD: a developmental visual curriculum for robust AI vision

### Problem

Standard vision models remain texture-biased, brittle under corruptions and adversarial perturbations, and weak at recognizing global shapes embedded in complex scenes. Earlier curriculum studies mainly used one or a few fixed blur stages; the paper argues that these omit the continuous maturation of human acuity, contrast, and colour (`paper.md:20-31`).

### Method

Developmental Visual Diet (DVD) is an age-conditioned image-preprocessing curriculum spanning birth to 25 years. During training, it progressively reduces Gaussian acuity blur, relaxes a frequency-domain contrast threshold, and increases colour fidelity. The developmental clock (alpha) maps epochs to months; (\beta) and (lambda) control the contrast threshold (`paper.md:181-235`). The method changes the images seen by otherwise standard classifiers rather than introducing a new backbone or loss.

### Main evidence

On ecoset, the ResNet-50 baseline had shape bias 0.34 at 62.99% accuracy; DVD-P reached 0.70 at 65.03%, DVD-B 0.83 with a 4.3-point accuracy reduction, and DVD-S 0.90 in the human range (`paper.md:65`). The upward shape-bias shift appears across mini-ecoset, ecoset, ImageNet-1K, and nine CNN/ViT architectures (`paper.md:71-79`; Fig. 3).

On IllusionBench (6,874 images, 16 shapes, 11 scenes), ImageNet-trained DVD-S achieved 36.21% shape recall versus 8.71% for the ResNet-50 baseline, 17.13% for the best tested ViT, and 12.47–21.24% for named foundation models; DVD-S scene recall fell to 20.07% (`paper.md:105-119`; Fig. 5). Under 16 corruption types, DVD accuracy at high severity was reported as roughly 2× baseline for noise/blur/weather and 3–4× for image-quality deficits (`paper.md:122-139`). At the strongest listed white-box settings, accuracy improved from 17% to 40% for FGSM, 13% to 32% for FGM, and 11% to 39% for PGD (`paper.md:142-145`; Fig. 6). Controlled-rearing results identify contrast-sensitivity development as the dominant contributor, while the full three-factor curriculum is most consistent across categories (`paper.md:148-160`; Fig. 4).

### Interpretation and limits

The evidence supports the paper's central claim that ordering visual information by developmental maturity can change learned feature preference, not merely add random degradation augmentation. Chronological order outperformed shuffled sensitivity values (`paper.md:93,163`). Still, DVD is explicitly an abstraction: psychophysical fits combine retinal and cortical effects, simplified frequency thresholding does not capture the full human contrast-sensitivity function, and each plotted model is not necessarily replicated across many seeds (`paper.md:184,208-211,160`; figure captions).

### Reproducibility: 3/5

The GitHub snapshot at commit `8a4e919812cfa52aa66ecaab121d0bdf5840a257` directly implements the three transformations, curriculum, training integration, validation, and checkpoint persistence. Its code-paper fidelity is **medium**: core preprocessing is exact/partial, but paper-specific shape-bias, IllusionBench, corruption, adversarial, Grad-CAM/LRP, and t-SNE result pipelines are missing. Dataset loaders contain external absolute HDF5 paths, standalone inference needs external checkpoints/class labels, no runtime tests or model weights were found, and supplementary material is linked but not available as local Markdown. The repository therefore supports inspection and adaptation of DVD itself, but not end-to-end reproduction of all reported figures from the checked-in files alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
