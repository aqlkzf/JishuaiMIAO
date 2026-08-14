---
layout: default
permalink: /paper-atlas/braininspiredwarmuprandomnoise-67b42086/
title: "BrainInspiredWarmupRandomNoise"
nav: false
wide: true
description: "论文研究分类网络的置信度校准：模型给出的置信度是否接近预测正确的实际概率。深度网络在随机初始化后可能已经产生过大的 logits 和偏向某些类别的输出，因此出现“准确率不高但置信度很高”的过度自信；网络越深、训练样本越少，这一问题越明显。对未知分布（OOD）样本的过度自信也会导致错误决策。 传统做法常在训练后加入温度缩放、概率变换或额外的 OOD 分数。"
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
      <span>Machine Learning Algorithm</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>BrainInspiredWarmupRandomNoise</h1>
    <p>Brain-inspired warm-up training with random noise for uncertainty calibration</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/cogilab/Random2" target="_blank" rel="noopener noreferrer" aria-label="Open code for BrainInspiredWarmupRandomNoise">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 随机噪声预热训练：方法说明

### 要解决的问题

论文研究分类网络的置信度校准：模型给出的置信度是否接近预测正确的实际概率。深度网络在随机初始化后可能已经产生过大的 logits 和偏向某些类别的输出，因此出现“准确率不高但置信度很高”的过度自信；网络越深、训练样本越少，这一问题越明显（`paper.md:48-57`）。对未知分布（OOD）样本的过度自信也会导致错误决策。

传统做法常在训练后加入温度缩放、概率变换或额外的 OOD 分数。论文引用的代表性工作包括 Guo 等人在 ICML 2017 的现代网络校准研究、Zadrozny 与 Elkan 在 ICML 2001/KDD 2002 的概率变换，以及 Liang 等人在 ICLR 2018 的 ODIN、Hendrycks 等人在 ICLR 2019 的 outlier exposure 和 Liu 等人在 NeurIPS 2020 的 energy-based OOD 检测（`paper.md:36,289,293,302-308`）。这些方法通常把校准作为额外步骤；本论文希望在网络开始学习任务之前直接改变其状态。

### 方法与创新

作者提出受脑发育启发的随机噪声预热（random-noise warm-up）：在网络接触真实任务数据之前，先用无语义的高斯噪声输入和独立、均匀采样的随机类别标签训练若干轮，然后再用普通监督学习训练真实数据（`paper.md:60-77,182-194`）。输入和标签每个 mini-batch 都重新采样，不建立固定配对。其目标不是学习输入特征，而是把初始输出从 SoftMax 的极端饱和区拉回到接近 $1/C$ 的机会水平；之后网络学习任务时，置信度应随准确率同步上升（`paper.md:89-109`）。

### 计算流程

```text
随机初始化的分类网络 f_theta
             |
             v
重复短暂的预热阶段：
  x_noise ~ Normal(0, I)，形状与任务输入相同
  y_noise ~ Uniform({1, ..., C})，且与 x_noise 独立
  每个 batch 重新生成两者
  用普通分类损失做前向、反向和参数更新
             |
预校准参数 theta_warm（未知输入的置信度接近 1/C）
             |
用新的任务优化器在 CIFAR-10 等真实标签数据上训练
             |
测量准确率、置信度、可靠性图、ECE 与 OOD AUROC
```

主模型是多层前馈网络：隐藏层宽度 256，ReLU 与 batch normalization，深度在实验中变化，权重采用 He 风格高斯初始化、偏置为零（`paper.md:176-179`）。论文没有给出单独的预热损失公式，只描述为最小化网络输出与随机标签之间的误差（`paper.md:182-185`）。从实现角度可理解为每个 batch 的交叉熵；这是本分析的形式化解释，不是论文原文公式。

代码验证到的主路径是 `code/scripts/experiment_training.py:363-473`：先使用独立 Adam 优化器调用 `random_train`，再重新创建 Adam 优化器进入 CIFAR-10 训练。`random_input` 在 `code/src/training/random_training.py:8-19` 中生成标准正态张量，`random_train` 在 `:96-105` 的循环中重新生成输入和标签。当前激活的 `random_label` 返回整数类别 ID（`random_training.py:22-29`），不是显式 one-hot；对于 `CrossEntropyLoss`，硬标签目标在优化意义上等价，但张量表示不同。可选的 `uniform_label=True` 会返回长度为 batch 的常数 $1/C$，并非 $B\times C$ 的软标签矩阵，主实验没有启用它。

### 校准与 OOD 评价

论文把置信度按十个区间分箱。第 $m$ 个 bin 的准确率是其中预测正确的比例，置信度是该 bin 内最大 SoftMax 概率的平均值；

$$\mathrm{ECE}=\sum_{m=1}^{M}\frac{B_m}{N}\left|\mathrm{acc}(B_m)-\mathrm{conf}(B_m)\right|,$$

理想校准时 ECE 接近零（`paper.md:200-221`）。仓库的 `reliability_diagram` 使用十个等宽区间，但把 bin 中点当作 `conf_bin`，不是样本置信度均值（`code/src/evaluation/calibration.py:5-62`），所以代码侧 ECE 与论文公式不是完全相同的实现。

OOD 实验用 CIFAR-10 作为 ID、SVHN 作为 OOD，以最大 SoftMax 置信度设阈值：高于阈值判为 ID，低于阈值判为 OOD，扫描阈值得到 ROC 与 AUROC（`paper.md:254-257`）。代码在 `code/scripts/experiment_ood_detection.py:101-114` 和 `code/src/evaluation/ood_detection.py:23-78` 中实现了这一流程，并使用最多 10,000 个有种子的 SVHN 样本（`code/src/data/dataloader.py:132-154`）。

### 主要结果

- 在 CIFAR-10 六层网络、4,000 个训练样本的主实验中，预热后任务训练的测试损失和 ECE 均低于无预热对照；$n=30$ 配对网络的损失和校准比较均报告 Wilcoxon $W=0, P=1.73\times10^{-6}, r=0.873$（`paper.md:74-77`）。
- 在二维玩具网络中，未训练网络的置信度图具有明显空间偏差，logit 和 SoftMax 输出靠近极端值；随机噪声训练后，置信度图更均匀、类别偏差减小并接近二分类机会水平（`paper.md:86-100`；Fig. 3）。
- 在相同准确率或相同训练轮数的比较中，预热网络的置信度更接近准确率（`paper.md:112-126`；Fig. 4）。
- 在 CIFAR-10/SVHN OOD 任务中，预热降低未知样本置信度并提高 AUROC；论文报告 $n=30, W=60, P=3.88\times10^{-4}, r=0.648$（`paper.md:129-146`；Fig. 5）。

### 学习时应保留的限制

仓库提交 `798a76cb1d98bd2dec8da6d3f17c60cea84bcb41` 提供了主流程和图表源数据，但本次分析没有实际运行训练。当前 ResNet scratch CLI 默认学习率 0.01、任务训练 80 轮，而论文 Methods 写的是 0.1、50 轮；fine-tuning wrapper 的 5 轮分类器预热与 20 轮联合微调则与论文描述一致（`code/cli/run_resnet_training.sh:43-52`; `code/cli/run_resnet_finetuning.sh:43-52`; `paper.md:224-233`）。图像分割、语言生成及补充图表的实现未在 `code/scripts/`、`code/src/`、`code/cli/` 中找到，应标记为 **Not found**，不能从主图或论文摘要推断为已复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

Cheon and Paik study uncertainty calibration: whether a classifier's confidence matches its empirical correctness. The paper argues that conventional random initialization can create overconfident, class-biased outputs before task learning, with the problem worsening as model complexity rises or training data shrink (`paper.md:48-57`). This matters for both ordinary predictions and OOD inputs, where high confidence on unknown data can cause unsafe decisions.

### Existing-Method Limitations

Prior calibration approaches commonly add post-processing or auxiliary computation. The paper cites modern neural-network calibration work by Guo et al. (ICML, 2017), classical score-to-probability transforms by Zadrozny and Elkan (ICML, 2001; KDD, 2002), and OOD methods such as ODIN by Liang et al. (ICLR, 2018), outlier exposure by Hendrycks et al. (ICLR, 2019), and energy-based detection by Liu et al. (NeurIPS, 2020) (`paper.md:36,289,293,302-308`). These methods can treat calibration or ID/OOD separation as a separate correction stage; they do not directly change the network's initial state.

### Proposed Method

The paper introduces brain-inspired warm-up training with random noise. Before seeing task data, a network is briefly trained on Gaussian inputs and independently sampled uniform random class labels. Both are regenerated each iteration. The warmed network is then trained normally on labelled data, with no calibration head, hold-out calibration set, or post-hoc score transform (`paper.md:60-77,182-194`). The intended effect is to move logits out of SoftMax saturation and confidence toward the $1/C$ chance level, so later confidence increases track acquired accuracy (`paper.md:89-109`).

### Evaluation and Main Results

- **Calibration failure baseline:** MLPs trained on CIFAR-10 show larger ECE for deeper networks and smaller training subsets (`paper.md:48-57`; Fig. 1).
- **Primary warm-up experiment:** six-layer CIFAR-10 networks trained on 4,000 examples show lower subsequent test loss and ECE with warm-up than paired controls. For $n=30$ networks, the paper reports Wilcoxon $W=0$, $P=1.73\times10^{-6}$, $r=0.873$ for both the loss and calibration comparisons (`paper.md:74-77`; Fig. 2).
- **Robustness:** the paper reports improvement across depth/data-size conditions, ResNet/DenseNet/vision-transformer families, feedback alignment, image segmentation, and language generation. The local workspace directly verifies only the main MLP, BP/FA, ResNet-18, and confidence-based OOD code paths; supplementary claims remain paper-only (`paper.md:77-83`).
- **Input-space mechanism:** in a 2D binary toy model, untrained networks show spatially biased confidence, extreme SoftMax outputs, and class bias; random-noise training makes confidence maps more homogeneous and close to chance (`paper.md:86-100`; Fig. 3).
- **Learning dynamics:** confidence and accuracy stay closer to the identity relation after warm-up under both accuracy-controlled and epoch-controlled comparisons (`paper.md:112-126`; Fig. 4).
- **OOD detection:** CIFAR-10 is ID and SVHN is OOD. Warm-up lowers OOD confidence and improves confidence-threshold AUROC; the paper reports $n=30$, $W=60$, $P=3.88\times10^{-4}$, $r=0.648$ (`paper.md:129-146`; Fig. 5).

### Reproducibility

The Nature HTML paper and five main figures are local. The paper identifies public CIFAR-10/SVHN data and the matching GitHub/Zenodo sources (`paper.md:266-275`). The pinned repository is `https://github.com/cogilab/Random2` at commit `798a76cb1d98bd2dec8da6d3f17c60cea84bcb41`; Python 3.12, PyTorch 2.10, NumPy 2.4.2, and SciPy 1.17.0 are stated by the paper (`paper.md:272-275`). Entry points and source-data regeneration scripts are present in `code/cli/`, `code/scripts/`, and `code/source_data/`.

Reproducibility rating: **3/5**. The core pipeline is runnable in principle and source coverage is good, but this analysis did not execute experiments, no experiment outputs/checkpoints are bundled, and the supplementary PDF/Markdown was not acquired. The code has three material fidelity caveats: active labels are integer class IDs rather than one-hot tensors (objective-equivalent under cross-entropy); ECE uses fixed bin midpoints rather than observed bin means; and the current ResNet scratch wrapper defaults to learning rate 0.01 and 80 task epochs rather than the paper's 0.1 and 50. Image-segmentation and language-generation implementations are **Not found** in the snapshot. CIFAR-10 and SVHN preprocessing also differ in code (`code/src/data/dataloader.py:9-33,106-154`) without a paper-level specification.

### Bottom Line

Random-noise warm-up is a simple initialization-stage intervention: spend a short budget fitting meaningless, balanced targets, then start ordinary task training from the resulting parameter state. The primary figures and code support improved calibration and confidence-based OOD separation for the tested MLP/CIFAR and ResNet settings, while the broader cross-domain claims and exact paper metrics require the unavailable supplement and a metric/schedule audit.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
