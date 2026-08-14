---
layout: default
permalink: /paper-atlas/tcr-translate-a7b0bcd1/
title: "TCR-TRANSLATE"
nav: false
wide: true
description: "论文要根据给定的抗原肽和呈递它的 MHC，生成可能具有抗原特异性的 TCR β 链 CDR3 序列。难点在于 TCR–pMHC 关系是多对多且存在交叉反应，而公开的配对数据十分稀疏、偏向少数病毒抗原；分类器可以打分，却不能直接提出新的受体序列。 把 pMHC→TCR 看成低资源机器翻译。输入由抗原肽和 MHC pseudo-sequence 组成，输出是 CDR3β。"
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
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>TCR-TRANSLATE</h1>
    <p>Conditional generation of real antigen-specific T cell receptor sequences</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-025-01096-6" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for TCR-TRANSLATE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/pirl-unc/tcr_translate" target="_blank" rel="noopener noreferrer" aria-label="Open code for TCR-TRANSLATE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TCR-TRANSLATE 方法中文解读

### 要解决的问题

论文要根据给定的抗原肽和呈递它的 MHC，生成可能具有抗原特异性的 TCR β 链 CDR3 序列。难点在于 TCR–pMHC 关系是多对多且存在交叉反应，而公开的配对数据十分稀疏、偏向少数病毒抗原；分类器可以打分，却不能直接提出新的受体序列（`paper.md:22-44`）。

### 核心想法

把 pMHC→TCR 看成低资源机器翻译。输入由抗原肽和 MHC pseudo-sequence 组成，输出是 CDR3β。作者比较 BART 和 T5 两类 encoder–decoder，并组合三种监督方式：单向基线、双向 pMHC↔TCR，以及再加入遮盖重建的 multitask。预训练使用 IEDB 的配体数据和 TCRdb 序列，最终选择在准确率、多样性和较低 polyspecificity 之间更均衡的 TCRT5-FT（论文简称 TCRT5）。

```text
公开 TCR-pMHC + MIRA
        │ 标准化、HLA 推断、去重
        ├── 训练集 (~330k pairs)
        └── 留出 top-20 pMHC 验证集 (~68k pairs)
                │
     [PMHC] 肽 [SEP] pseudo → TCRT5 encoder-decoder
                │ beam search
                ▼
          排名的 CDR3β 序列
                │
   BLEU / F1 / recovery / OLGA / diversity / GIANA
                │
      WT1 CDR3β graft → NFAT-luciferase assay
```

### 目标函数

基线使用 token-level categorical cross-entropy：

$$\mathcal{L}=\mathrm{CE}({\bf y},\hat{\bf y})=-\sum_i\sum_j y_{ij}\log p_\theta(y_{ij}|{\bf x}).$$

双向训练将 pMHC→TCR 与 TCR→pMHC 两个损失相加；multitask 再加入 pMHC 和 TCR 的 masked reconstruction（`paper.md:255-279`）。每个 batch 随机决定是否交换方向、是否使用损坏输入，从而在同一 epoch 内混合任务并减少遗忘（`paper.md:282-318`）。

### 数据和评估

数据来自 McPAS、VDJdb、IEDB 和 allele-imputed MIRA；作者只保留人类 MHC-I 配对并标准化氨基酸、TCR 基因和 HLA。top-20 pMHC 被留作验证，另外构造 14 个与训练表位编辑距离至少 5 的稀疏 benchmark。评估同时看“像不像已知 binder”和“是否只重复少数序列”：Char-BLEU、native recovery、mAP、OLGA generation probability、unique count、Jaccard、位置熵变化、k-mer JS，以及 Precision/Recall/F1@K（`paper.md:208-240,321-350`）。

### 结果与局限

条件生成优于无条件生成；multitask 虽提高部分准确率，却更容易生成 polyspecific、重复的序列。TCRT5 在 2,000 次验证生成中有 1,996 个具有非零 OLGA 概率、181 个已知 binder，并产生 7 个未出现在 fine-tuning 中的序列。稀疏 benchmark 上 TCRT5 的高排名功能相似序列最多。WT1 实验中 F8（`CASSVGLYNEQFF`）能激活 T 细胞，但对 CEFX 病毒/细菌肽混合物也有反应，说明特异性仍不足（`paper.md:111-157`）。仓库能核对 tokenizer、dataset、generation 和 metric 接口，但没有完整实验脚本、checkpoint、OLGA/GIANA 分析和湿实验代码；训练脚本还存在 `args.config_file` 配置变量疑点。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TCR-TRANSLATE Summary

### Problem

Functional TCR design against arbitrary antigens is difficult because TCR–pMHC recognition is many-to-many, cross-reactive, and represented by sparse, biased paired data. Existing classifiers score specificity but do not directly propose receptor sequences; earlier generators either redesign known repertoires or generate unconditional natural-like TCRs (`paper.md:22-44`).

### Method

TCR-TRANSLATE casts pMHC-to-CDR3β design as low-resource sequence translation. TCRBART and TCRT5 encoder–decoders use character-level peptide plus MHC pseudo-sequence inputs and autoregressively generate CDR3β sequences. Twelve variants compare random/pretrained initialization with baseline, bidirectional, and masked-reconstruction multitask objectives. The flagship TCRT5 is selected using both accuracy and diversity, then decoded with beam search (`paper.md:45-93,187-318`).

### Evaluation and Findings

The top-20 pMHC validation split contains about 68k pairs and is intentionally excluded from training. Metrics include Char-BLEU, F1@K, native sequence recovery, mAP, OLGA biological likelihood, unique-sequence count, Jaccard diversity, Δentropy, and k-mer JS shift (`paper.md:225-229,321-350`). TCRT5 improves conditional generation over unconditional baselines, gives 1,996/2,000 valid generations and 181 known binders on validation, and outperforms ER-TRANSFORMER and GRATCR on a 13-epitope sparse benchmark. A generated CDR3β (F8, `CASSVGLYNEQFF`) activates a WT1 NFAT-luciferase assay, but also responds to a broad CEFX peptide pool (`paper.md:111-157`).

### Reproducibility

The paper is source-complete and the linked GitHub snapshot directly verifies token formatting, many-to-many dataset objects, Hugging Face decoding, and several metric helpers. It does not expose the complete experiment orchestration, pretrained checkpoints, all data-building/OLGA/GIANA scripts, or wet-lab code; `scripts/train.py:37` also appears to reference an undefined `args.config_file`. Reproducibility rating: **3/5** for computational interfaces, lower for end-to-end result reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
