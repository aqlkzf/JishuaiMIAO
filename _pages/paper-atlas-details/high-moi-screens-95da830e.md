---
layout: default
permalink: /paper-atlas/high-moi-screens-95da830e/
title: "High_MOI_screens"
nav: false
description: "这篇 Nature Methods 论文研究的是：在 pooled CRISPRi 筛选中，不再坚持“每个细胞只进一个 sgRNA”的低 MOI 设计，而是用中等偏高 MOI 让一个细胞携带多个 sgRNA，从而用更少细胞完成筛选。论文声称 MOI 2.5–10 在许多条件下可以保持筛选性能，并能显著减少细胞数需求；其中 MOI 2.5–5 是更稳妥的压缩区间。"
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
      <span>Perturbation Resources</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>High_MOI_screens</h1>
    <p>Multiplexed perturbation enables scalable pooled screens</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03095-w" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 高 MOI 多重扰动筛选方法中文解释

### 一句话概括

这篇 Nature Methods 论文研究的是：在 pooled CRISPRi 筛选中，不再坚持“每个细胞只进一个 sgRNA”的低 MOI 设计，而是用中等偏高 MOI 让一个细胞携带多个 sgRNA，从而用更少细胞完成筛选。论文声称 MOI 2.5–10 在许多条件下可以保持筛选性能，并能显著减少细胞数需求；其中 MOI 2.5–5 是更稳妥的压缩区间（`paper.md:20-36`, `paper.md:291-333`）。

### 为什么需要这个方法？

传统 pooled CRISPR 筛选需要较高 guide representation，常见目标是 200–500× coverage。做 genome-wide screen 时，这会需要数千万甚至上亿细胞，成本和操作压力都很高（`paper.md:66-80`）。如果研究对象是 primary tissue、FACS sorting、药物处理或其他难扩增体系，细胞数会成为瓶颈。

### 方法核心

论文把“提高 MOI”作为筛选压缩手段：

1. 低 MOI 通常约 0.3–0.5，使每个细胞大多只有一个 sgRNA（`paper.md:45-49`）。
2. 高 MOI 让一个细胞表达多个 sgRNA，即 sgRNA multiplexing（`paper.md:87-96`）。
3. 作者使用 CRISPRi，也就是 dCas9-Zim3-KRAB 抑制系统，而不是 Cas9 nuclease，以降低多重切割带来的基因组重排风险（`paper.md:113-118`）。
4. 感染水平通过 dPCR 标定，并用荧光 reporter 的 MFI 作为更方便的 MOI 估计代理（`paper.md:78-108`, `paper.md:1359-1363`）。

### 实验设计

论文先用一个 compact 2,000-sgRNA epigenetic-regulator library 做系统评估。这个 library 每个基因 3 条 sgRNA，并含有 5% nontargeting controls（`paper.md:263-273`）。筛选比较三类条件：

- **Low-MOI control**：MOI 固定 0.3，同时减少细胞数。
- **Constant sgRNA number**：MOI 越高，细胞数越少，使总 sgRNA 数大致恒定。
- **Constant cell number**：细胞数固定，MOI 越高，总 sgRNA 观察数越多。

论文使用 DESeq2 估计 guide-level effect size，用 MAGeCK 估计 gene-level effect size，并用 AUC / ROC-AUC 评价 essential gene recovery（`paper.md:263-288`, `paper.md:1541-1545`）。论文还写出一个用于评估 MOI effect 的回归式：

$$\hat{\beta}_{mg} \sim \alpha_g + \gamma_m + 0$$

其中 $m$ 是 MOI，$g$ 是 guide，$\gamma_m$ 表示 MOI 增加对 effect size 的影响（`paper.md:1493-1507`）。

### 主要结论

代码和论文证据都支持的结论需要分开看：

#### 论文声称

- 中等 MOI（特别是 2.5–5）可以部分补偿细胞数降低造成的筛选性能损失（`paper.md:291-333`）。
- 太高的 MOI（20–30）在细胞数也降低时会明显变差，可能因为 cell number 太低、gRNA collision 或 knockdown 下降（`paper.md:346-352`）。
- 在 genome-wide CD54/ICAM-1 筛选中，MOI 5 可以在较低 coverage 下保持有用的筛选性能，并用 MAGeCK + FDR < 0.01 找基因层面的 hits（`paper.md:615-640`）。

#### 代码可验证的是

公开 GitHub 只包含 mapping/counting 代码，而不是完整统计分析代码。README 明确说仓库包含两个用于带 barcode 的 CRISPR screen sequencing data mapping/counting 脚本（`README.md:1-8`）。

- `mapping_single_sgRNA.Rmd`：读取 single-guide FASTQ，BBDuk 剪切，按 sgRNA perfect match 过滤，统计 sgRNA 和 barcode counts，输出 `counts_all.csv`（`mapping_single_sgRNA.Rmd:25-88`）。
- `mapping_dual_sgRNA.Rmd`：用 Cutadapt 处理 dual-guide reads，分别统计 gRNA1-barcode 和 gRNA2-barcode 组合，再相加输出 `tables/sgrna_count_BC.txt`，可作为 MAGeCK 输入（`mapping_dual_sgRNA.Rmd:23-135`）。

#### 代码中未找到直接实现

公开仓库中未找到 starcode 调用、DESeq2/MAGeCK 运行脚本、ROC/AUC 计算脚本、绘图脚本、ICAM-1 network analysis 脚本。也缺少 FASTQ、annotation、UMI table 和本地路径所需的数据文件，因此不能从公开仓库直接复现论文全部图表和统计结果。

### 如何理解这个方法的适用边界？

这篇论文不是建议“MOI 越高越好”。更准确的理解是：在细胞数受限时，可以用中等高 MOI 把多个 sgRNA 放进同一细胞，提高有效扰动覆盖度；但 MOI 太高会带来 off-target、toxicity、组合效应、gRNA collision 和解释困难（`paper.md:1238-1296`）。因此实际使用时需要先做 pilot test，确认细胞可感染、可 super-infect，并且没有明显毒性。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Multiplexed perturbation enables scalable pooled screens — Summary

### What problem does the paper solve?

Pooled CRISPR screens need high guide representation, often requiring very large cell numbers. This is expensive and sometimes infeasible for primary cells, FACS sorting, drug treatment, or other resource-limited screens. The paper tests whether high-MOI delivery of multiple sgRNAs per cell can compress CRISPRi screens while preserving performance (`paper.md:66-96`).

### Main idea

Instead of enforcing one sgRNA per cell at low MOI (~0.3–0.5), the method deliberately uses moderate high MOI so each cell carries multiple sgRNAs. The study benchmarks how this affects knockdown efficiency, guide representation, essential-gene recovery, drug-tolerance hit discovery, and a genome-wide CD54/ICAM-1 FACS screen (`paper.md:20-36`, `paper.md:109-125`).

### Key findings

- MFI can act as a practical proxy for lentiviral copy number after calibration against low-MOI/dPCR measurements (`paper.md:78-108`, `paper.md:1359-1363`).
- A compact 2,000-sgRNA epigenetic-regulator screen shows that moderate MOI, especially roughly 2.5–5, can partially compensate for reduced cell numbers (`paper.md:256-333`).
- Excessive MOI, especially 20–30 under reduced cell numbers, can degrade performance and complicate interpretation (`paper.md:346-352`, `paper.md:1238-1253`).
- A genome-wide dual-sgRNA CD54/ICAM-1 screen at MOI 5 identifies regulators with useful performance even at reduced coverage; significant hits use MAGeCK with FDR < 0.01 (`paper.md:615-640`).

### Code availability and reproducibility

The public GitHub repository contains mapping/counting scripts, not the full downstream statistical analysis. This matches the paper's Code availability statement (`paper.md:1522-1525`). Direct source reads verify:

- single-guide BBDuk trimming, perfect-match counting, barcode diversity summaries, and `counts_all.csv` output (`mapping_single_sgRNA.Rmd:25-88`);
- dual-guide Cutadapt trimming, UMI/barcode counting for gRNA1/gRNA2, merged counts, and `tables/sgrna_count_BC.txt` output (`mapping_dual_sgRNA.Rmd:23-135`).

Missing from the public repo: starcode calls, DESeq2/MAGeCK execution, ROC/AUC analysis, plotting, and ICAM-1 network analysis. The scripts also require external FASTQs, annotation files, UMI tables, and local absolute paths, so local execution is not reproducible from the repository alone.

### Practical interpretation

The paper is best understood as a screening-design and experimental-technology study. The core message is not “use the highest possible MOI,” but rather “moderate MOI can trade viral multiplicity for fewer cells if infection, toxicity, collision effects, and downstream interpretation are carefully controlled.”

### Reproducibility rating

**Medium-low for full paper reproduction; medium for mapping/counting code transparency.** The wet-lab protocol and analysis logic are well described, and public code covers read mapping/counting. However, the released repository omits data, local execution environment, and downstream statistical/figure scripts.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
