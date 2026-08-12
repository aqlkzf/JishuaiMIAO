---
layout: default
permalink: /paper-atlas/totalx-c52279df/
title: "TotalX"
nav: false
description: "常规液滴式单细胞 RNA 测序主要捕获带 poly(A) 尾的 mRNA，因此 miRNA、tRNA、snoRNA/scaRNA、部分 lncRNA 以及不带 poly(A) 尾的病毒 RNA 会被系统性漏掉。TotalX 在 10x Chromium 3′ v3.1 上加入少量酶学和计算步骤，使长、短、编码和非编码 RNA 可以在同一单细胞框架中测量。 细胞/细胞核在同一反应中进行 3′ poly(A) 化、5′ 加帽和逆转录；"
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
      <span>Technology Platforms</span>
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>TotalX</h1>
    <p>Scalable single-cell total RNA sequencing unifies coding and noncoding transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TotalX 方法说明

### 它解决什么问题？

常规液滴式单细胞 RNA 测序主要捕获带 poly(A) 尾的 mRNA，因此 miRNA、tRNA、snoRNA/scaRNA、部分 lncRNA 以及不带 poly(A) 尾的病毒 RNA 会被系统性漏掉。TotalX 在 10x Chromium 3′ v3.1 上加入少量酶学和计算步骤，使长、短、编码和非编码 RNA 可以在同一单细胞框架中测量（`paper.md:18-30,36-40`）。

### 实验流程

细胞/细胞核在同一反应中进行 3′ poly(A) 化、5′ 加帽和逆转录；自定义含尿嘧啶模板转换寡核苷酸完成模板转换，UDG 随后去除它。预扩增 5 个循环后，用 Cas9/DASH 切除线粒体和胞质 rRNA，再扩增 7–10 个循环。磁珠把 cDNA 分成 >400 bp 长片段和 <400 bp 短片段，分别建库；短片段还可富集约 18–30 bp miRNA，最后按比例混池测序（`paper.md:247-265`）。

### 计算流程

```text
FASTQ → Cutadapt 去接头/去前 6 bp → 长 RNA 与短 RNA 两套参考
      → Cell Ranger 双重比对 → 以长参考确定细胞条形码
      → 用相同条形码取短参考结果 → 合并短 RNA 计数
      → Scrublet / scVI / Scanpy / WGCNA / PAGA 下游分析
```

长参考包括 protein-coding、lncRNA、miRNA、sn/sno/scaRNA、tRNA 等 biotype，并可加入 DENV2；短参考只保留 miRNA、snoRNA 和 scaRNA。论文指定 Cutadapt 参数 `-u 6 -a 'AAAAAAAAAA;min_overlap=10' -m 18`，并在 Cell Ranger 中使用短 RNA 友好的 STAR 参数。条形码先由长 RNA 运行筛选，再将短参考中带 `xf:Z:25` 的 UMI 计数替换/补入长参考矩阵（`paper.md:268-292`）。

### 结果与可复现性

TotalX 在 PBMC 中揭示非编码 RNA 的细胞类型特异性及共表达模块，在 DENV2 感染细胞中捕获非 poly(A) 病毒转录本，在发育脑中解析非编码 RNA 的区域、细胞类型和时间动态，包括 MIR137 及其靶基因反相关（`paper.md:62-183`）。仓库含 Cutadapt、参考构建脚本和 Figure2–5 分析 notebook；但完整 Cell Ranger 双通路、STAR 参数补丁、BAM 过滤和计数替换脚本未找到，补充材料 markdown 也缺失，应明确标记为 `Not found` 而不是推断。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## TotalX summary

TotalX is a scalable total-RNA single-cell protocol that extends a commercial 10x Chromium 3′ workflow to capture both polyadenylated and non-polyadenylated coding and noncoding transcripts. It combines co-incubated polyadenylation/capping/reverse transcription, UDG cleanup, Cas9/DASH rRNA depletion, separate long/short library handling and dual-reference quantification (`paper.md:36-40,247-292`).

The paper reports application to over 500,000 cells spanning PBMCs, DENV2-infected hepatocytes and developing human brain. TotalX detects cell-type-specific miRNAs, tRNAs and lncRNAs, coding/noncoding co-expression modules, non-polyadenylated viral RNA and developmental noncoding programs including MIR137 dynamics (`paper.md:9-30,62-183`). Comparisons against VASA-seq and standard 10x use UMI-normalized gene detection and pseudo-bulk correlations (`paper.md:295-307`).

Reproducibility is medium: the GitHub snapshot contains trimming/reference scripts and analysis notebooks, but the production Cell Ranger dual-pass workflow, STAR parameter patch, `xf:Z:25` filtering and deterministic short-count substitution were not located. No supplementary markdown was acquired. Figures 1–15 are present locally and were used as visual navigation; final claims remain grounded in `paper.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
