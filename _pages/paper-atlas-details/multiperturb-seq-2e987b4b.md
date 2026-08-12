---
layout: default
permalink: /paper-atlas/multiperturb-seq-2e987b4b/
title: "MultiPerturb-seq"
nav: false
description: "单细胞 pooled CRISPR screen 的目标，是给大量细胞施加不同遗传扰动，再观察每个扰动改变了什么。经典 Perturb-seq（Cell, 2016）主要读取 RNA；CRISPR-sciATAC 等方法主要读取染色质开放性。两类读出各有盲点：RNA 能看见细胞状态，但往往是调控变化的下游结果；ATAC 能看见潜在调控元件和表观状态，但不能保证这些变化已经转化成基因表达。"
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
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>MultiPerturb-seq</h1>
    <p>Pooled CRISPR screens with joint single-nucleus chromatin accessibility and transcriptome profiling</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-024-02475-x" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MultiPerturb-seq：把 CRISPR 扰动、染色质开放性和转录组放进同一个细胞里读出

### 论文要解决什么问题？

单细胞 pooled CRISPR screen 的目标，是给大量细胞施加不同遗传扰动，再观察每个扰动改变了什么。经典 Perturb-seq（*Cell*, 2016）主要读取 RNA；CRISPR-sciATAC 等方法主要读取染色质开放性。两类读出各有盲点：RNA 能看见细胞状态，但往往是调控变化的下游结果；ATAC 能看见潜在调控元件和表观状态，但不能保证这些变化已经转化成基因表达。

如果把 RNA 和 ATAC 分开做，还会遇到两个问题：同一个细胞无法一一对应，批次差异也会混入模态差异。MultiPerturb-seq 的目标因此很明确：在同一个细胞核中同时获得

1. CRISPR gRNA 身份；
2. ATAC-seq 开放染色质片段；
3. RNA-seq 转录本。

论文进一步把它用于 AT/RT（非典型畸胎样/横纹肌样瘤）细胞，寻找能够推动肿瘤细胞分化的表观遗传靶点。

### 核心创新：两轮条形码支持超载

MultiPerturb-seq 不是以新机器学习模型为核心，而是以分子实验和组合索引架构为核心。

```text
pooled CRISPRi 文库
        ↓ 低 MOI 感染、筛选、等待 7 天
分离细胞核并分到多个孔
        ↓
第一轮条形码
  - barcoded transposome 标记开放染色质
  - poly(dT) + gRNA 特异引物逆转录
  - 匹配的 barcoded TSO 标记 RNA/gRNA
        ↓ 混池
10x ATAC 液滴中的第二轮条形码
        ↓
分别扩增 ATAC、RNA、gRNA 文库
        ↓
三模态比对、计数、细胞条形码交集
        ↓
gRNA 分配 → 扰动 pseudobulk → RNA/ATAC 分化评分
```

普通液滴实验依赖“一滴一个细胞”。MultiPerturb-seq 则用“孔条形码 × 液滴条形码”的组合来识别细胞，因此可以在一条 10x Chromium ATAC lane 中装载约 100,000 个细胞核，约为论文对照方案的十倍。代价是同一液滴可能含多个细胞核，所以需要足够大的组合条形码空间和物种混合实验来测量碰撞率。

### 从实验到三个计数矩阵

主筛选使用表达第二代 CRISPRi 抑制器的 BT16 AT/RT 细胞，文库靶向 109 个染色质相关基因，每个基因 3 条 gRNA，并包含 17 个 non-targeting 对照。低感染复数使“一细胞一主要扰动”成为主导情形。

第一轮中，barcoded transposome 对开放染色质做 tagmentation；同一孔内，poly(dT) 捕获 mRNA，gRNA 特异引物捕获 guide，带匹配条形码的 TSO 记录第一轮身份。停止 tagmentation 后再做逆转录，是论文强调的实验细节：如果活性转座酶继续存在，可能破坏 RNA–DNA 复合物和三模态一致性。

第二轮把所有细胞核混合后装入 10x ATAC 液滴，由 gel bead 提供第二个条形码。最终材料被拆分、纯化并扩增成 ATAC、RNA 和 gRNA 三套文库。

论文报告的计算处理包括：

- 用 cutadapt 拆出两轮条形码、UMI 和分子读段；
- ATAC 用 Bowtie 2 比对、MACS2 叫峰；
- RNA 用 STAR 比对、featureCounts 注释；
- 按条形码、UMI 和位置去重；
- 构建 `SingleCellExperiment` 计数对象；
- 取三模态都存在的 429,139 个条形码；
- 保留至少 100 个 RNA UMI 或 100 个 ATAC unique fragments 的 121,651 个条形码进入下游分析。

### gRNA 分配为什么需要纠错？

同一细胞内，PCR 或测序错误会把一个真实 UMI 变成多个相近字符串，从而虚增 guide 分子数。论文先按 read count 对 UMI 排序，把高支持 UMI 当作候选原始分子，再递归合并与其 Levenshtein distance 不超过 2 的低支持 UMI。如果同一 UMI 对应多个 guide，只保留 read 支持最高的配对。

这个步骤的意义在于：guide assignment 使用“纠错后的分子”而不是原始 UMI 字符串。但公开代码快照中没有找到这段实现，因此只能确认论文方法，不能做代码级复现。

### RNA 与 ATAC 分化评分

作者把同一扰动下的细胞聚合成 pseudobulk，并分别与人脑发育参考图谱比较：

- RNA 使用跨发育样本变化最大的 1,000 个 HVG；
- ATAC 使用蛋白编码基因 TSS ±2 kb 内变化最大的 1,000 个 HVPP；
- 只使用每细胞至少 200 fragments、且至少捕获 100 个细胞的扰动。

对扰动 $i$ 和阶段 $s$（prenatal 或 postnatal），先对平均 Pearson correlation 做跨扰动 min–max 归一化：

$$
r^{\mathrm{norm}}_{i,s}
=
\frac{r_{i,s}-\min_j r_{j,s}}
{\max_j r_{j,s}-\min_j r_{j,s}}.
$$

分化评分为：

$$
D_i = r^{\mathrm{norm}}_{i,\mathrm{postnatal}}
- r^{\mathrm{norm}}_{i,\mathrm{prenatal}}.
$$

RNA 和 ATAC 分开计算。高正值表示该扰动让细胞更像出生后的脑组织。双评分设计很关键：有些扰动会强烈改变开放染色质，却没有同步推动转录组分化；只有在两个模态都靠前的候选，才更像完整的细胞状态转变。

### 实验结果说明了什么？

平台层面，物种混合实验报告 ATAC、RNA、gRNA 碰撞率分别为 11.6%、6.2% 和 6.6%，78% 的高质量细胞能够分配到 guide。与低通量 CROP-Multiome 相比，MultiPerturb-seq 在 guide 捕获、RNA UMI/基因数、ATAC fragments/peaks 等方面更好，并支持约十倍装载量。

生物学层面，*ZNHIT1* 是 RNA 与 ATAC 联合评分中最突出的候选之一。后续 arrayed CRISPRi 验证显示：

- SOX2 干性信号下降；
- S-phase 表达和 EdU 掺入下降；
- ATOH8、TUJ1、MAP2 等神经分化标志上升；
- H2A.Z CUT&RUN peaks 的数量和强度下降；
- 直接扰动 *H2AZ1* 或 *H2AZ2* 也能降低增殖并提高分化标志。

这些结果支持一条机制链：降低 ZNHIT1 功能 → 减少 H2A.Z 沉积 → 改变染色质状态和细胞周期 → 推动 AT/RT 细胞向更分化的状态移动。它是细胞模型中的机制证据和治疗靶点线索，不等于已经证明动物或患者疗效。

### 代码能复现到什么程度？

论文链接的 GitLab 仓库只包含 5 个 R 源文件。直接代码核对确认了两部分：

- `annotate_species()` 以 0.66 为阈值，根据人/鼠 fragments 把细胞标成 human、mouse 或 collision；
- 脚本生成物种混合和跨技术 RNA/ATAC QC 比较图。

但以下核心实现均 **Not found**：原始 reads 处理、gRNA UMI 合并/分配、SCEPTRE 扰动检验、HVG/HVPP 图谱相关和分化评分。仓库还需要缺失的 RDS/CSV/H5AD 数据、手动修改占位路径，并调用未定义的 `annotate_rna()`。因此代码—论文一致性评为低，公开快照不能端到端复现实验分析。

### 阅读时应保留的边界

- 分化评分是“与参考图谱更相似”，不是直接观察到的发育轨迹。
- 论文的主图支持平台性能和细胞机制，但本地没有补充 protocol、补充图和 primer 表。
- *ZNHIT1* 的治疗意义仍需体内模型、药理工具和临床相关证据。
- MultiPerturb-seq 的最大价值是高通量、同细胞、三模态联合测量；当前公开代码的复现完整度明显弱于论文的方法描述。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## MultiPerturb-seq

### Problem and contribution

Pooled single-cell CRISPR screens had generally measured either gene expression or chromatin accessibility, making it difficult to connect regulatory changes, transcriptional consequences and perturbation identity in the same cell. MultiPerturb-seq is a trimodal screening platform that captures ATAC, RNA and gRNA from the same nucleus. Its main engineering idea is to combine a first well barcode with a second 10x droplet barcode, permitting about 100,000 nuclei to be loaded on one Chromium ATAC lane while retaining usable cell identities.

The study applies the platform to CRISPRi perturbations of 109 chromatin-related genes in AT/RT, a SMARCB1-deficient pediatric brain cancer. Separate RNA and ATAC differentiation scores compare perturbation-specific pseudobulks with prenatal and postnatal brain atlases, allowing the authors to prioritize perturbations that shift both transcription and chromatin toward more mature states.

### Why prior approaches were insufficient

- Perturb-seq (Cell, 2016) and later large-scale transcriptional screens connect guides to RNA phenotypes but do not directly observe chromatin accessibility in the same cell.
- CRISPR-sciATAC and related accessibility screens capture regulatory-state changes without a matched transcriptome.
- CROP-Multiome can collect RNA, ATAC and guide identity, but in this study it uses approximately 10,000 rather than 100,000 cells per lane, requires a specialized guide vector and has lower guide/RNA/ATAC capture.
- Running modalities separately introduces experiment-to-experiment confounding and cannot directly reveal perturbations whose chromatin and RNA differentiation responses disagree.

### Method overview

Cells expressing CRISPRi are transduced at low multiplicity and collected after 7 days. Isolated nuclei are distributed across wells, where barcoded transposomes tag accessible chromatin and matched barcoded TSOs label RNA/gRNA reverse-transcription products. Nuclei are then pooled and superloaded into 10x ATAC droplets for a second barcode. ATAC, RNA and guide libraries are separated and sequenced.

The reported processing workflow demultiplexes and aligns each modality, intersects trimodal barcodes, filters cells, and assigns guides after recursively collapsing UMI sequences within Levenshtein distance 2 of more strongly supported UMIs. Perturbations are pseudobulked, compared with developmental atlases across the top 1,000 HVGs or promoter-adjacent variable peaks, and ranked by separately normalized postnatal-minus-prenatal RNA and ATAC correlations.

### Evaluation and main findings

- Species mixing reports collision rates of 11.6% for ATAC, 6.2% for RNA and 6.6% for gRNA despite roughly tenfold superloading; 78% of high-quality cells receive a guide assignment.
- The trimodal intersection contains 429,139 barcodes; filtering to at least 100 RNA UMIs or 100 ATAC fragments leaves 121,651 barcodes for downstream analysis.
- Compared with CROP-Multiome, MultiPerturb-seq shows better guide capture and higher RNA/ATAC per-cell yield while loading about ten times more cells.
- Joint RNA/ATAC ranking identifies *ZNHIT1* as a leading differentiation perturbation. Arrayed validation shows reduced SOX2 and proliferation, increased neuronal markers, reduced H2A.Z occupancy, and similar differentiation phenotypes after direct *H2AZ1/H2AZ2* perturbation.
- The evidence supports a model in which reducing ZNHIT1-dependent H2A.Z deposition can shift AT/RT cell lines toward a more differentiated state. It does not establish clinical efficacy.

### Code and reproducibility

**Reproducibility rating: 2/5.** The paper provides extensive wet-lab and computational Methods, public sequencing data (BioProject PRJNA1160410) and a public GitLab repository. However, the inspected repository contains only five R files for species-mixing and cross-technology QC visualizations. It lacks the paper's raw-read processing, guide assignment, perturbation testing and differentiation-score implementations. The included scripts require absent local RDS/CSV/H5AD inputs, use a placeholder base path, and call an undefined `annotate_rna()` function.

Direct source inspection verifies the 0.66 species/collision classifier and the RNA/ATAC QC comparison logic, but overall code–paper fidelity is low. See `doc_code.md` for exact line anchors and `doc_method.md` for the paper-reported end-to-end pipeline.

### Limitations

- The detailed supplementary protocol, supplementary figures and primer tables were not acquired locally.
- Differentiation scores measure similarity to reference atlases and are not direct lineage trajectories.
- Core computational implementations are absent from the linked code snapshot, so exact end-to-end reproduction is not possible from the repository alone.
- The therapeutic interpretation is based on cell lines and molecular/phenotypic validation; in vivo efficacy, pharmacology and patient benefit remain untested.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
