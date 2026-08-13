---
layout: default
permalink: /paper-atlas/longcallr-0858fd10/
title: "longcallR"
nav: false
wide: true
description: "长读长 RNA 测序能让一条 read 同时跨越多个 SNP 和完整转录本结构，因此天然适合单倍型定相与等位基因特异分析。但 RNA 数据有四个突出难点：基因表达导致覆盖极不均匀；剪接位点附近容易错比对；ASE 会让等位基因比例偏离 0.5；A-to-I RNA 编辑又可能被误判为生殖系 SNP。已有的 Clair3-RNA 能较准确地进行 RNA 变异检测，但不同时完成 SNP 定相和 ASE/ASJ 分析。"
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>longcallR</h1>
    <p>SNP calling, haplotype phasing and allele-specific analysis with long RNA-seq reads</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03045-6" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for longcallR">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/huangnengCSU/longcallR" target="_blank" rel="noopener noreferrer" aria-label="Open code for longcallR">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## longcallR 方法详解

### 它解决什么问题？

长读长 RNA 测序能让一条 read 同时跨越多个 SNP 和完整转录本结构，因此天然适合单倍型定相与等位基因特异分析。但 RNA 数据有四个突出难点：基因表达导致覆盖极不均匀；剪接位点附近容易错比对；ASE 会让等位基因比例偏离 0.5；A-to-I RNA 编辑又可能被误判为生殖系 SNP。已有的 Clair3-RNA 能较准确地进行 RNA 变异检测，但不同时完成 SNP 定相和 ASE/ASJ 分析。

longcallR 把这些任务连成一个流程：

```text
长读长 RNA 比对 BAM + 参考基因组
              |
              v
候选 SNP / 外部候选 VCF
              |
              +--> 7 通道 pileup 图 --> ResNet-50 --> 基因型、合子性
              |                              （论文描述；本仓库未找到实现）
              v
read × SNP 等位基因片段
              |
              v
交替更新 SNP 相位 <--> read 单倍型标签
              |
              +--> phased VCF / haplotagged BAM
              +--> beta-binomial ASE
              +--> H1/H2 × junction present/absent 的 ASJ 检验
```

### 三个核心模块

#### 1. longcallR-nn

候选位点周围 41 bp 被编码成 (41\times d\times7) 张量，七个通道分别是碱基、参考序列、插入、碱基质量、比对质量、read 链方向和转录本链方向。ResNet-50 同时输出五类合子性（包括 RNA editing）与 16 类基因型。训练标签来自 REDIportal 的编辑位点和 DNA 真值集，并为 PacBio MAS-seq、Iso-seq、ONT cDNA、ONT dRNA 分别训练模型。

重要缺口：当前代码快照中**未找到**该神经网络的训练、推理、pileup 图生成代码或权重，因此这一模块只能依据论文理解，不能仅靠本仓库完整复现。

#### 2. longcallR-phase

令 (\delta_i\in\{1,-1\}) 表示 SNP (i) 的相位，(\sigma_k\in\{1,-1\}) 表示片段 (k) 的 haplotag，(q_{ki}(x)) 表示由碱基质量决定的观测概率。目标是最大化

$$P(\delta,\sigma)=\prod_k\prod_{i\in I_k}q_{ki}(\sigma_k\delta_i).$$

算法采用交替优化：固定 SNP 相位，逐条 read 比较正反 haplotag；再固定 read 标签，逐个比较 SNP 相位。只有使概率提高的翻转才保留。随着可信 SNP 增多，更多 read 得到稳定标签；更好的 read 标签又帮助判断剩余候选究竟是真 SNP、测序错误还是 RNA 编辑。

初始化不是完全随机。方法统计两个 SNP 在同一 read 上的四种等位组合，用冲突比例 (mathrm{c}1/mathrm{c}2) 建图；无冲突的 SNP 进入同一连通分量并作为块共同翻转。代码对小块穷举，对大块使用 LD 初始化、交替/分块优化和随机扰动。因为这对应 NP-hard 的加权最小错误修正问题，最终解可能是局部最优。

#### 3. ASE 与 ASJ

ASE 分析把 read 分配给外显子重叠长度最大的基因，只保留 read 数最多的 phase set，然后用 beta-binomial 检验 H1/H2 是否偏离 0.5，并做 Benjamini–Hochberg 校正。

ASJ 分析对每个 junction 统计四类 read：H1-present、H1-absent、H2-present、H2-absent。论文使用 Fisher 精确检验，并定义

$$R=\frac{|R_{a1}|\,|R_{p2}|}{|R_{p1}|\,|R_{a2}|},\qquad \mathrm{SOR}=\ln(R+1/R).$$

代码还加入两个值得注意的细节：计算 SOR 时给四格都加 1 以避免零除；事件 p 值取 Fisher 与 G-test 中较大的一个，再进行 BH 校正，因此比论文文字描述更保守。

### 实验结果如何理解？

在 12 个 PacBio/ONT 人类数据集上，PacBio SNP precision 为 98.5–99.0%，recall 为 91.0–95.3%；相对 Clair3-RNA，longcallR 平均提高约 1.4 个百分点 precision，但牺牲部分 sensitivity。Nanopore 更困难，precision 为 85.8–98.0%，recall 为 73.9–87.3%。在 GIAB 定相真值上，longcallR-phase 比 WhatsHap 得到更长的 phase block 和更低的 switch/Hamming error。

在 202 个 HPRC MAS-seq 样本中，每个样本平均检测到 88 个严格显著 ASJ 事件，其中 46.5% 涉及未注释 junction。图中也显示事件数会随测序覆盖变化，所以“没有检测到”不等价于“没有等位基因特异剪接”。

### 使用与复现边界

- 已直接核对：Rust 候选处理、概率定相、VCF/BAM 输出、ASE 和 ASJ 实现。
- 未找到：`longcallR-nn` 神经网络代码、权重与完整训练流程。
- 代码的 log-space 打分与论文概率结构对应，但不是所有公式的逐字代数实现。
- 论文的补充表和补充说明未作为本地 Markdown 获取。
- 该版本面向 bulk RNA-seq；低覆盖、稀疏杂合位点和高多样性区域仍会限制准确率与统计功效。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## longcallR

longcallR is a unified workflow for SNP calling, haplotype phasing, and allele-specific analysis from bulk long-read RNA-seq. It targets RNA-specific difficulties—uneven expression coverage, splice-alignment errors, skewed allele fractions, and RNA editing—that make genomic-read variant callers or simple RNA pipelines unreliable. Clair3-RNA can call RNA variants accurately but does not provide the joint phasing and downstream ASE/ASJ workflow offered here.

The method has three parts. `longcallR-nn` converts a 41-bp pileup window into seven feature channels and uses ResNet-50 to classify zygosity and genotype. `longcallR-phase` alternates between SNP-phase and read-haplotag updates under a base-quality probability model, progressively admitting compatible variants and separating germline SNPs from errors/editing. Phased VCF/BAM outputs then drive beta-binomial ASE testing and haplotype-by-junction contingency testing for ASJs.

Across 12 PacBio and ONT human datasets, PacBio precision was 98.5–99.0% and recall 91.0–95.3%; longcallR improved precision over Clair3-RNA by 1.4 percentage points on average, with comparable F1 around 95.7%, but generally lower sensitivity. Nanopore precision and recall ranged 85.8–98.0% and 73.9–87.3%. Against GIAB trio phase, longcallR produced longer blocks and lower switch/Hamming error rates than WhatsHap. In 202 HPRC MAS-seq samples it found an average of 88 stringent ASJ events per sample, 46.5% involving unannotated junctions.

Reproducibility is mixed. The repository at commit `0e876f0e` provides substantial Rust source for candidate handling, probabilistic phasing, phased VCF/BAM output, ASE, and ASJ, with runnable CLI documentation and demo inputs. Direct inspection confirms the principal phasing equations' variables and iterative structure, although some code scores use log-space approximations and ASJ testing includes conservative implementation details beyond the paper. The separate `longcallR-nn` ResNet training/inference code and weights were **Not found**, no supplementary Markdown was acquired, and no core automated phasing tests were identified. Overall reproducibility: **3.5/5**—strong for phasing and allele-specific modules, incomplete for the neural caller and full benchmark recreation.

Key limitations are the approximate NP-hard phasing optimization, reduced recall when variants cannot be confidently phased, dependence of allele-specific power on read coverage, bulk-RNA focus, and possible alignment artifacts in highly diverse loci.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
