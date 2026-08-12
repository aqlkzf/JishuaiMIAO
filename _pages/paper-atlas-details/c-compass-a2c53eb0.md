---
layout: default
permalink: /paper-atlas/c-compass-a2c53eb0/
title: "C-COMPASS"
nav: false
description: "细胞器分级实验会把蛋白质在多个离心组分中的丰度记录成一条“曲线”。传统分类器通常给每个蛋白一个细胞器标签，但约一半蛋白可能多定位，而且不同条件下还会重新定位。C-COMPASS 的目标是输出一个和为 1 的细胞器贡献向量，例如“线粒体 0.7、胞质 0.3”，并比较不同条件之间的变化。相同思路还能用于与蛋白质共同分级的脂质。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>C-COMPASS</h1>
    <p>C-COMPASS: a user-friendly neural network tool profiles cell compartments at protein and lipid levels</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## C-COMPASS 方法解读

### 它解决什么问题？

细胞器分级实验会把蛋白质在多个离心组分中的丰度记录成一条“曲线”。传统分类器通常给每个蛋白一个细胞器标签，但约一半蛋白可能多定位，而且不同条件下还会重新定位。C-COMPASS 的目标是输出一个和为 1 的细胞器贡献向量，例如“线粒体 0.7、胞质 0.3”，并比较不同条件之间的变化。相同思路还能用于与蛋白质共同分级的脂质。

### 为什么已有方法不够？

SubCellBarCode 和 DOM-ABC 使用 SVM，MetaMass 使用聚类，TRANSPIRE 使用高斯过程，BANDLE 与 TAGM-MCMC 使用概率模型。它们各自能完成分类、差异定位或不确定性分析，但论文强调：此前工具没有同时覆盖定量多定位、细胞器丰度校正、蛋白质—脂质联合分析和面向非编程用户的图形界面。

### 核心流程

```text
分级丰度表 + 单定位标记蛋白
        ↓
缺失值置零、每条曲线按总和归一化
        ↓
少数标记类别上采样
        ↓
两类曲线按比例混合，制造“多定位”训练样本
        ↓
调参并训练前馈神经网络
        ↓
多轮训练与预测取平均
        ↓
按细胞器阈值去除假阳性，再归一化为 CC
        ↓
条件比较（RL、RLS、DS、P 值）/ 总蛋白校正 / 脂质定位
```

每个物种的分级曲线记为 $p^{(s,r)}\in\mathbb{R}_+^F$。模型假设它由 $C$ 个细胞器分布混合而成：

$$
p^{(s,r)}=\sum_{c=1}^{C}w_c^{(s,r)}p^{(c)},\qquad w_c\ge 0,\quad\sum_cw_c=1.
$$

网络输入维度是组分数 $F$，经过可调宽度的全连接层和 $C$ 维输出层，再用 ReLU 保证非负，最后除以总和，因此输出天然落在概率单纯形上。代码中的 `classification_model.py:59-163` 与该描述一致。

训练数据不平衡时，程序从同一细胞器随机抽取三条标记曲线并取中位数，必要时加入噪声，直到各类别数量相同。随后把两个细胞器的曲线按多个比例混合，同时把比例作为软标签。这使网络能学习多定位，而不是只学习硬分类。

预测后，程序为每个细胞器建立独立阈值：观察“其他细胞器标记蛋白”被误分到该类的分数，以指定可靠性百分位作为阈值；低于阈值的值归零，剩余贡献重新归一化。不同条件间有

$$
RL_c=CC_{c,2}-CC_{c,1},\qquad RLS=\sum_c|RL_c|.
$$

RLS 为 0 表示无变化，最大 2 表示两个分布完全转移。DS 则汇总各细胞器的 Cohen's $d$ 效应量。

### 论文验证了什么？

作者在脂肪细胞 PCP、hyperLOPIT、不同组分分辨率模拟、人源化小鼠肝脏和蛋白质—脂质共同分级数据上测试方法。图 2 显示类别平衡改善了少数类预测；图 4 显示在模拟双定位和三定位时，C-COMPASS 的误差低于 BANDLE 与 DOM-ABC；图 5 展示代谢条件相关的蛋白重新定位；图 6 显示心磷脂、三酰甘油等脂质得到符合已知生物学的细胞器分配。

### 使用时要注意

- 实验分级必须真正分开目标细胞器；高度重叠的曲线无法靠神经网络凭空分辨。
- 阈值依赖标记蛋白的纯度与覆盖范围。
- 脂质定位借用了蛋白标记建立的空间坐标，因此是共同分级证据，不等同于成像定位。
- 本地代码与核心算法高度一致，但论文补充示例会话、完整补充参数和 BANDLE 脚本在本工作区中为 **MISSING**。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## C-COMPASS

C-COMPASS is a graphical, open-source spatial-omics tool that converts biochemical fractionation profiles into quantitative distributions over cellular compartments. Its central advance is neural regression on balanced single-compartment markers plus synthetic mixed profiles, allowing proteins—and co-fractionated lipids—to receive multilocalization vectors instead of a single class.

Earlier workflows such as SubCellBarCode/DOM-ABC (SVM), MetaMass (clustering), TRANSPIRE (Gaussian-process classification), BANDLE (Bayesian inference), and TAGM-MCMC can classify or quantify uncertainty, but the paper argues they do not jointly provide quantitative compartment mixtures, organelle-composition correction, lipid/protein integration, and a nonprogrammer GUI.

The pipeline unit-normalizes fraction profiles, balances marker classes, simulates mixed localizations, tunes a feed-forward network, ensembles repeated predictions, removes compartment-specific false positives, and renormalizes surviving class contributions. Between conditions it reports compartment deltas, an $RLS=\sum_c|\Delta CC_c|$ score, effect-size-based DS, and significance. Optional total-proteome data support organelle-centric abundance estimates.

Evaluation spans adipocyte PCP, hyperLOPIT, reduced-fraction simulations, comparison with BANDLE and DOM-ABC, humanized mouse liver across metabolic states, and matched liver proteomics/lipidomics. Reported results include improved marker-class performance after upsampling, robust multilocalization at adequate fraction resolution, lower error than BANDLE/DOM-ABC for simulated dual/triple localizations, biologically plausible fasting-associated protein relocalizations, and organelle-consistent lipid assignments such as cardiolipins to mitochondria and triacylglycerols to lipid droplets.

Reproducibility is strong but not complete. The authors provide GitHub code, releases, documentation, PRIDE data, and Zenodo example sessions. The local snapshot matches the paper's core algorithms at high fidelity and contains an end-to-end synthetic test. However, the supplementary example assets and BANDLE scripts are **MISSING** from this workspace, and reproducing paper figures requires large experimental datasets and version-sensitive desktop/TensorFlow dependencies.

**Reproducibility rating: 4/5.** Core implementation is public and closely matches the paper; full paper-result reproduction additionally depends on external data and supplementary/example assets.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
