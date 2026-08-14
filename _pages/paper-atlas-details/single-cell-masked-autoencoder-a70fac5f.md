---
layout: default
permalink: /paper-atlas/single-cell-masked-autoencoder-a70fac5f/
title: "Single_cell_Masked_Autoencoder"
nav: false
wide: true
description: "cyMAE（cytometry masked autoencoder）针对固定 30-marker panel 的 CyTOF 单细胞蛋白表达，解决人工 gating 慢、主观且难复现，以及聚类受批次效应影响的问题。它先用大量无标签细胞进行 masked cytometry modeling，再用少量标注数据微调。"
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
      <span>Cell Reports Medicine · 2024</span>
    </div>
    <h1>Single_cell_Masked_Autoencoder</h1>
    <p>Cytometry masked autoencoder: An accurate and interpretable automated immunophenotyper</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/JaesikKim/cyMAE" target="_blank" rel="noopener noreferrer" aria-label="Open code for Single_cell_Masked_Autoencoder">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## cyMAE 方法说明

cyMAE（cytometry masked autoencoder）针对固定 30-marker panel 的 CyTOF 单细胞蛋白表达，解决人工 gating 慢、主观且难复现，以及聚类受批次效应影响的问题。它先用大量无标签细胞进行 masked cytometry modeling，再用少量标注数据微调。

```text
细胞表达向量 -> 随机遮挡 25% marker
             -> marker embedding + 表达值 + 位置编码
             -> 6 层 Transformer encoder
             -> mask token + 2 层 decoder 重建遮挡值
             -> MSE 预训练
             -> 不遮挡运行 encoder
             -> 细胞池化/展平、受试者池化
             -> 注释、插补、临床状态预测
```

论文定义 (H_{i,unmasked}=f_e((E_{unmasked}\parallel V_{i,unmasked})+P_{unmasked}))，并以 (\widehat V_{i,masked}=f_d((H_{i,unmasked}\parallel M)+P)) 重建被遮挡蛋白；损失是遮挡位置上的 MSE。编码器宽度 30、6 层、6 heads，解码器宽度 15、2 层、3 heads。无 mask 时，mean pooling 产生 (C_i^{pool})，flatten 产生 (C_i^{full})；受试者向量再对细胞表示做 mean/sum/max/min pooling。

训练使用 Acute2020（约 650 万细胞），在 Vaccine 与 Acute2021 等同 panel 队列评估细胞注释、蛋白插补、SARS-CoV-2/疫苗/疾病阶段预测。论文报告最高约 15,276 cells/s。局限包括只验证一个 panel、未验证 flow cytometry、终末人工标签作为近似 ground truth，以及代码仓库没有训练权重和完整 subject-pooling 推理脚本。

代码核验：`cyMAE/modeling_pretrain.py` 实现可见 token 选择、mask token、位置编码和 decoder；`engine_for_pretraining.py` 使用 masked MSE；`modeling_finetune.py` 实现无 mask encoder 和分类头。复现时必须显式把脚本默认的 mask ratio 0.75 改为论文设置 0.25。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

cyMAE is a masked-autoencoder transformer for automated immunophenotyping of fixed-panel single-cell CyTOF data. It learns marker co-occurrence from millions of unlabeled cells, then reuses the encoder for labeled cell annotation, marker imputation, and subject-level predictions.

Manual gating is slow, subjective, and difficult to reproduce; clustering is sensitive to batch effects and changing boundaries; supervised marker methods depend heavily on potentially biased labels. cyMAE addresses this with masked cytometry modeling: mask 25% of a cell’s 30 protein channels, encode visible marker/value tokens, and reconstruct the missing values with a small decoder.

The paper evaluates Acute2020, Vaccine, and Acute2021 COVID-19 CyTOF cohorts. It compares against manual/static gating, clustering and supervised baselines across cell-type annotation, imputation, SARS-CoV-2 status, vaccine response, and disease stage. Reported inference reaches 15,276 cells/s, while the same-panel constraint is essential.

Reproducibility is medium: the GitHub snapshot matches the core architecture and losses, but no trained checkpoint or end-to-end fixture is included, subject pooling is not fully implemented, and the entry-point default mask ratio (0.75) must be changed to the paper’s 0.25.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
