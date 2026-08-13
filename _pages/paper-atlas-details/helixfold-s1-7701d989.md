---
layout: default
permalink: /paper-atlas/helixfold-s1-7701d989/
title: "HelixFold-S1"
nav: false
wide: true
description: "复合物结构预测常通过生成大量候选构象来提高命中正确构象的机会，但盲目增加采样会带来高成本和大量冗余。HelixFold-S1 的摘要提出：先预测链间接触概率，再把计算资源投入到更可能、且较少重复的接触区域，从而指导复合物构象探索。 它不是把所有随机构象一视同仁地生成和筛选，而是把链间 token 对的概率图当作探索蓝图。每轮从候选界面中选择一个界面约束，运行结构模型；之后用已经采过的界面和预测置信度更新下一轮的选择。"
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
      <span>Protein &amp; Sequence Models</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>HelixFold-S1</h1>
    <p>Reshaping biomolecular structure prediction through strategic conformational exploration with HelixFold-S1</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/PaddlePaddle/PaddleHelix" target="_blank" rel="noopener noreferrer" aria-label="Open code for HelixFold-S1">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## HelixFold-S1 方法解读

### 要解决的问题

复合物结构预测常通过生成大量候选构象来提高命中正确构象的机会，但盲目增加采样会带来高成本和大量冗余。HelixFold-S1 的摘要提出：先预测链间接触概率，再把计算资源投入到更可能、且较少重复的接触区域，从而指导复合物构象探索（`paper.md:9-12`）。

### 核心思路

它不是把所有随机构象一视同仁地生成和筛选，而是把链间 token 对的概率图当作探索蓝图。每轮从候选界面中选择一个界面约束，运行结构模型；之后用已经采过的界面和预测置信度更新下一轮的选择。直觉上，这会避免反复把预算花在同一类界面上。

```text
输入复合物 JSON
  -> MSA/模板特征
  -> 模块 1：预测界面概率
  -> 模块 2：读取概率图和已有历史
  -> 选择新的界面约束
  -> 结构预测
  -> 保存结构、置信度和界面采样历史
```

### 从代码可验证的流程

公开脚本依次运行 MSA 模块、模块 1 和模块 2（`run_inference.sh:28-69`）。模块 2 对 HelixFold-S1 要求模块 1 已生成界面概率文件；随后把 `interface_prob` 加入特征批次（`run_inference_S1_module2.py:1125-1186,1348-1352`）。每一轮会用约束掩码过滤候选，并记录直接采样历史。普通采样分支将原始概率、置信度项和历史鼓励项组合；`topn_cluster` 分支则使用经过掩码的概率直接选择（`213-384`）。选中的界面图写入 `batch['feat']['interface_info']`，再送入结构模型。

代码中的一种评分形式可写为：

$$
S_{ij}=\left(P_{ij}+bC_{ij}+c\frac{\log(t+1)}{I_{ij}+D_{ij}+1}\right)M_{ij}.
$$

其中 $P_{ij}$ 是模块 1 的界面概率，$C_{ij}$ 是由既往预测得到的置信度图，$I_{ij}$、$D_{ij}$ 分别是间接和直接历史计数，$M_{ij}$ 是可采样掩码。这是根据代码整理的解释，不应当误称为论文公式。

### 输入、输出与复现条件

README 说明输入 JSON 至少含两条链，可设置 `recycle`、`ensemble` 和分子实体；输出包括 MSA、模块 1 中间结果、模块 2 的结构/指标，以及 `interface_infos` 中的概率图和采样记录（`README.md:54-103,229-280`）。完整运行还需要预训练权重、遗传数据库、Paddle/CUDA 环境和 GPU。README 给出的 reduced 数据库下载量约 190 GB、解压后约 530 GB（`README.md:39-52`）。

### 证据强度与不足

四张主图支持框架、性能/消融、概率诊断和引导探索这四类叙事，但当前 Nature HTML 只有摘要、图题和可用性信息，没有完整 Methods、补充材料或结果表。因此，本文档不确认论文的具体指标、训练目标、概率定义或“数量级”采样节省。公开代码能验证推理阶段的引导采样路径，但模块 1 训练、权重与基准流程仍是未验证范围。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## HelixFold-S1 Summary

HelixFold-S1 is a guided conformational-exploration approach for biomolecular complex structure prediction. Rather than using an unguided large ensemble, the paper abstract says that predicted interchain contact probabilities direct computation to informative, high-probability and low-redundancy contacts, with claimed gains in accuracy and sampling efficiency (`paper source/nature_html/paper.md:9-12`).

The linked public implementation is available in PaddleHelix on the `dev` branch at commit `8e3991ab1209134b148b05d44e784a43eaa4484d`. Its inference script runs feature/MSA construction, an interface-generation module, and S1 module 2 (`PaddleHelix/apps/protein_folding/HelixFold-S1/run_inference.sh:28-69`). Module 2 imports module-1 interface probabilities, reweights eligible interface pairs using sampling history and configured confidence signals, selects an interface map, and repeats structure prediction for the requested ensemble (`run_inference_S1_module2.py:213-384,1178-1186,1429-1473`).

The downloaded figures show the proposed framework, benchmark/ablation layouts, contact-probability diagnostics, and guided-exploration comparisons. However, this Nature HTML capture is a subscription preview: it has the abstract, figures/captions, availability statements, and references, but not Methods or result tables. The analysis therefore does not restate numerical benchmark results, formulas, training details, or an Exact paper-code mapping. The paper makes code, trained weights, and inference scripts available through the linked GitHub path and a Zenodo record (`paper.md:92-95`), but reproducing inference still requires downloaded checkpoints, genetic databases, CUDA/Paddle dependencies, and suitable GPU resources.

Reproducibility status: **3/5**. Public source, setup notes, example inputs, and an explicit two-module inference path are present; full reproduction and the paper's quantitative claims remain unverified in this workspace because the retained primary text lacks Methods/supplement and no GPU run was performed.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
