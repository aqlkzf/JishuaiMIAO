---
layout: default
permalink: /paper-atlas/compass-80430a6a/
title: "COMPASS"
nav: false
wide: true
description: "COMPASS 要解决的问题是：仅凭肿瘤突变负荷、PD-L1 或单一免疫基因签名，往往难以稳定预测不同癌种、队列和免疫检查点抑制剂中的疗效。论文把治疗前 bulk RNA-seq 转换为可解释的肿瘤免疫微环境（TIME）概念，再预测应答概率。 流程为： 作者以 33 个癌种的 10,184 个 TCGA 肿瘤进行对比学习预训练；同一肿瘤的扰动表达应在概念空间接近，不同肿瘤应分离。随后在临床队列上做监督微调。"
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
      <span>Nature Medicine · 2026</span>
    </div>
    <h1>COMPASS</h1>
    <p>Generalizable AI predicts immunotherapy outcomes across cancers and treatments</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/mims-harvard/COMPASS" target="_blank" rel="noopener noreferrer" aria-label="Open code for COMPASS">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## COMPASS 方法解读

COMPASS 要解决的问题是：仅凭肿瘤突变负荷、PD-L1 或单一免疫基因签名，往往难以稳定预测不同癌种、队列和免疫检查点抑制剂中的疗效。论文把治疗前 bulk RNA-seq 转换为可解释的肿瘤免疫微环境（TIME）概念，再预测应答概率。

流程为：

```text
TPM 表达 + 癌种 token
  -> Transformer 基因上下文表示
  -> 132 个基因集分数
  -> 43 个高层 TIME 概念分数
  -> 应答/非应答分类器与个体化响应图
```

作者以 33 个癌种的 10,184 个 TCGA 肿瘤进行对比学习预训练；同一肿瘤的扰动表达应在概念空间接近，不同肿瘤应分离。随后在临床队列上做监督微调。大队列可 FFT，PFT 冻结编码器而更新投影器和分类器，LFT 仅训练分类器；论文还描述不更新参数的 NFT。官方代码直接实现了 Transformer、分层投影、triplet loss 与 LFT/PFT/FFT（`doc_code.md`）。

评估使用 16 个队列的 1,133 名患者，覆盖七种癌和多种 PD-1/PD-L1、CTLA-4 治疗。图 2 展示留一队列与队列间迁移；图 3 检验跨癌种、跨药物和跨靶点；图 4 检验先泛癌微调、再特定适应证微调的 MSFT。图 6 将基因 TPM、基因分数、基因集分数和高层概念连接到预测概率，因而提供个体层面的解释。

复现边界：本地保留了官方 GitHub 源码，但没有运行受控临床数据或预训练权重；在线响应图服务器的实现未在该快照中核验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## COMPASS

COMPASS is a concept-bottleneck transformer for predicting immune checkpoint inhibitor response from pretreatment bulk RNA-seq. It transfers 132 curated gene signatures into 43 high-level tumor-immune microenvironment concepts, pretrains on 10,184 TCGA tumors, and adapts to clinical cohorts using selective fine-tuning (`paper.md:58-64`).

The paper evaluates 1,133 patients from 16 cohorts across seven cancers. In leave-one-cohort-out testing it reports the best average result among 22 comparators, with 8.5% higher accuracy and 15.7% higher AUPRC; a held-out urothelial trial analysis associates COMPASS response predictions with survival (HR 4.7, P = 1.7 x 10^-7) (`paper.md:43`). Figure 2 makes the cohort imbalance, three cohort-size strata, leave-one-cohort-out design, and 240 transfer tests explicit. Figure 3 tests holdout cancer, drug and target settings; Figure 4 compares multi-stage versus single-stage transfer.

The official public GitHub implementation is present locally at `COMPASS_repo/`, pinned to commit `0e5c87665247e3a300f28282c8bbcc14e26973bd`. Its architecture, projection hierarchy, triplet loss and LFT/PFT/FFT modes match the paper at direct source locations documented in `doc_code.md`. Reproducibility is partial: source code is available, but this analysis did not run protected/public cohort inputs or pretrained checkpoints, and the deployed response-map visualization is not verified in the snapshot.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
