---
layout: default
permalink: /paper-atlas/training-data-composition-generalization-475206cc/
title: "Training_data_composition_generalization"
nav: false
wide: true
description: "监督式抗体-抗原结合预测必须同时提供正例和负例，但“负例”如何定义会改变模型到底学到了什么。本文比较不同负类组成对同分布（ID）准确率、跨任务/跨抗原分布外（OOD）泛化，以及生物学规则发现的影响。论文摘要明确指出：更接近正例的负例可能降低 ID 表现，却提高 OOD 表现，并改变正类相关规则。 研究使用 Absolut! 结构模拟数据，并用 Porebski 实验数据验证。"
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
      <span>Computational Tools</span>
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>Training_data_composition_generalization</h1>
    <p>Training data composition determines machine learning generalization and biological rule discovery</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-025-01089-5" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Training_data_composition_generalization">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/csi-greifflab/negative-class-optimization" target="_blank" rel="noopener noreferrer" aria-label="Open code for Training_data_composition_generalization">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法中文解读

### 要解决的问题

监督式抗体-抗原结合预测必须同时提供正例和负例，但“负例”如何定义会改变模型到底学到了什么。本文比较不同负类组成对同分布（ID）准确率、跨任务/跨抗原分布外（OOD）泛化，以及生物学规则发现的影响。论文摘要明确指出：更接近正例的负例可能降低 ID 表现，却提高 OOD 表现，并改变正类相关规则（`paper source/nature_html/paper.md:1-15`）。

### 数据与任务

研究使用 `Absolut!` 结构模拟数据，并用 Porebski 实验数据验证。负类包括 `vs Non-binder`、`vs Weak`、`vs 9` 和 `vs 1`；Extended Data Fig. 1 将负例按亲和力分成 0-10 的 weak partitions 与 11-25 的 non-binder partitions（`paper.md:256-263`）。训练集为 30,000 条、测试集为 10,000 条；11-mer CDRH3 中 90% identity 表示只有一个位置不同（`supplementary_information.md:792-800`）。正负分布差异主要用 Jensen-Shannon distance（JSD）描述（`supplementary_information.md:15-22`）。Nature 预览没有给出完整 Methods，因此 JSD 的精确特征化和采样公式记为 **Not found**。

### 计算流程

```text
结合数据/抗体 CDRH3
        ↓
选择正抗原和负类定义，构造平衡二分类任务
        ↓
训练 SN10/SNN（并比较 Logistic/CNN/Transformer/PLM）
        ↓
同任务 ID 测试 + 换任务/抗原 OOD 测试
        ↓
计算 JSD、序列相似性，以及 logits/attribution 与结合能的相关性
```

代码中 `BinaryDataset` 将每行特征整理为 `(1, features)` 的 float tensor，并把标签整理为标量 float（`negative-class-optimization/src/NegativeClassOptimization/NegativeClassOptimization/datasets.py:138-152`）。抗原集合配对时排除正负集合重叠，并排除总支持集超过可用抗原数的组合（`:172-206`）。默认 SNN 为 220 个输入特征、10 个隐藏单元；标准训练使用 Adam、学习率 0.001、50 epochs、batch size 64（`pipelines.py:376-412`; `scripts/script_02a_train_1v1.py:79-110`）。

每个 epoch 用 BCE loss 做前向、反向传播和参数更新，然后计算测试 loss/accuracy；可选的 SWA 从第 3 个 epoch 开始（`ml.py:689-750`, `:862-929`）。OOD 结果由改变训练和测试任务得到，补充图 4 给出了完整的任务矩阵（`supplementary_information.md:65-69`）。

### 规则发现与结论

规则发现只在正类样本上做：将 logits 与总结合能相关，将每个氨基酸 attribution 与该位置能量贡献相关（`supplementary_information.md:90-99`, `:143-152`）。代码使用 DeepLIFT、shuffle baseline、10 次 shuffle、logits 目标和 `multiply_by_inputs=True`（`scripts/script_04b_attributions.py:78-96`），能量贡献通过外部 Absolut! `getFeatures` 命令生成（`scripts/script_04a_energy_per_residue.py:82-102`）。

Supplementary Text 1 说明，单纯增加训练/测试的相似序列并不能解释 ID 准确率；多数相关性不显著，且作者认为相同标签造成的数据泄漏不太可能（`supplementary_information.md:800-814`）。单表位分析保持了主要 ID/OOD 趋势，并提高了一些任务的 logit 规则发现，但 attribution 规则没有一致提升（`:820-840`）。因此，负类选择既是泛化控制变量，也是模型解释结果的生物学先验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

Binary sequence classifiers depend on what is called a negative example. In antibody-antigen binding, this choice can make a benchmark look accurate while teaching the model a task-specific shortcut. Ursu, Minnegalieva and colleagues therefore vary negative-class composition and measure both predictive generalization and recovery of biological binding rules.

### Contribution

The study uses synthetic structure-derived `Absolut!` data plus experimental Porebski data to compare `vs Non-binder`, `vs Weak`, `vs 9`, and `vs 1` negative definitions. Its central result is that negatives closer to positives in affinity space can reduce ID accuracy but improve OOD behavior, while changing the relationship between model outputs/attributions and ground-truth binding energy (`paper.md:1-15`; `supplementary_information.md:15-22`).

### Method and Evaluation

Tasks are balanced binary CDRH3 classification problems. SN10/SNN is compared with logistic regression, CNNs, Transformers and pretrained protein-language-model variants (Supplementary Tables 4-5, `supplementary_information.md:509-787`). Performance is evaluated on the same task (ID) and after changing the task/antigen (OOD), with replicate aggregation and JSD/sequence-overlap analyses. Rule discovery is assessed by Pearson correlations between positive-class logits and total binding energy, and between per-residue attributions and per-residue energy (`supplementary_information.md:90-126`).

### Reproducibility

The paper links processed data/results through Zenodo and code through GitHub (`paper.md:72-95`). This workspace contains the pinned repository snapshot at commit `6ba07d7`, supplementary markdown/PDF, four article figures, and frozen result tables. Core training is directly traceable to package source, but the Nature preview omits the full Methods and the exact JSD/affinity-space implementation is not located in the inspected source. Attribution depends on Captum and energy features depend on an external Absolut! executable. The code also has an SWA-disabled artifact-save defect (`pipelines.py:435-474`). Overall reproducibility: **3/5**.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
