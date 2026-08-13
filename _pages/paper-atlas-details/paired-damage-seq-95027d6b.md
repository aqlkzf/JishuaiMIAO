---
layout: default
permalink: /paper-atlas/paired-damage-seq-95027d6b/
title: "Paired-Damage-seq"
nav: false
wide: true
description: "Paired-Damage-seq 先把细胞核里的氧化 DNA 损伤“修复式标记”为生物素信号，再用抗体引导的 pA-Tn5 把损伤附近的 DNA 切下并加上条形码；与此同时，它在同一个细胞核中做带相同条形码的逆转录。这样，研究者既能看到“这个细胞是什么类型、处于什么状态”，又能看到“这类细胞的哪些基因组区域更容易出现损伤”。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Paired-Damage-seq</h1>
    <p>Single-cell parallel analysis of DNA damage and transcriptome reveals selective genome vulnerability</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/czhulab/Paired-Damage-seq" target="_blank" rel="noopener noreferrer" aria-label="Open code for Paired-Damage-seq">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Paired-Damage-seq 方法详解

### 一句话理解

Paired-Damage-seq 先把细胞核里的氧化 DNA 损伤“修复式标记”为生物素信号，再用抗体引导的 pA-Tn5 把损伤附近的 DNA 切下并加上条形码；与此同时，它在同一个细胞核中做带相同条形码的逆转录。这样，研究者既能看到“这个细胞是什么类型、处于什么状态”，又能看到“这类细胞的哪些基因组区域更容易出现损伤”。

### 1. 它要解决什么问题？

DNA 损伤并不是均匀落在基因组上的。序列组成、染色质开放程度、转录活动、异染色质结构和修复效率都会影响一个区域最终积累多少损伤。但是传统方法有两个关键盲区：

1. **群体平均掩盖细胞类型差异。** Click-Code-seq（*Journal of the American Chemical Society*, 2018）、AP-site sequencing（*Nature Chemistry*, 2019）、Nick-seq（*Nucleic Acids Research*, 2020）和 CLAPS-seq（*Nucleic Acids Research*, 2021）等方法可以绘制群体水平的损伤图谱，却无法判断复杂组织中信号来自哪一种细胞。
2. **已有单细胞多组学通常没有直接测 DNA 损伤。** Paired-seq（*Nature Structural & Molecular Biology*, 2019）测 RNA 与开放染色质；Paired-Tag（*Nature Methods*, 2021）和 CoTECH（*Nature Methods*, 2021）测 RNA 与染色质占据/组蛋白修饰；Droplet Paired-Tag（*Nature Structural & Molecular Biology*, 2023）进一步提升了通量。它们能给细胞身份，却没有把氧化损伤本身作为配对模态。

还有一个更根本的困难：DNA 损伤事件稀疏、随机，而且不能像普通 DNA 模板那样直接“把损伤信号扩增”。因此单个细胞的损伤轨迹往往像椒盐噪声，单独用它聚类很不稳定。

### 2. 核心创新：把损伤转成可捕获的生物素标签

Paired-Damage-seq 的第一个关键设计叫 **labeling-by-repair（修复式标记）**。它借用碱基切除修复反应，把不同损伤汇聚到一个可标记的单链缺口状态：

```text
8-oxoG / AP 位点 / 已有单链断裂
        │
        ├─ Fpg：去除 8-oxoG，并处理部分断端
        ├─ Endo IV：切开 AP 位点、整理断端
        ▼
可供聚合酶延伸的单链缺口
        │
        ├─ Bst polymerase：缺口平移，掺入 biotin-dUTP
        └─ Taq ligase：封口
        ▼
带生物素的损伤邻近 DNA
```

随后，抗生物素抗体识别这些标记，抗体结合的 protein A-Tn5 在损伤附近进行靶向 tagmentation，同时加上第一轮条形码 BC1。这个设计的要点是：它不是试图直接扩增“损伤”本身，而是把损伤转换成一个抗体可识别、Tn5 可捕获的 DNA 片段。

实验在甲醛固定的完整细胞核中完成，并在标记前进行核小体去除，以降低不同染色质状态带来的酶可及性偏差。论文用预修复、无靶向 tagmentation、人工 nickase 位点和 H$_2$O$_2$ 剂量梯度等实验验证了信号特异性。

### 3. 第二个关键创新：DNA 和 RNA 共用同一个细胞身份

同一批 BC1 同时通过两条路线进入同一个细胞核：

- 损伤 DNA 通过带 BC1 的 pA-Tn5 获得条形码；
- RNA 通过带相同 BC1 的逆转录引物生成 cDNA。

之后，完整细胞核经历两轮 split-and-pool 连接，依次获得 BC2 和 BC3。于是来自同一个细胞的损伤 DNA 与 cDNA 共享 BC1+BC2+BC3：

```text
固定细胞核
  ├─ 损伤标记 + BC1 靶向 tagmentation
  └─ BC1 逆转录
        ↓
第一轮混合/分孔：连接 BC2
        ↓
第二轮混合/分孔：连接 BC3
        ↓
裂解、共同预扩增
        ↓
分成 DNA 库和 RNA 库
        ↓
测序后按 BC1+BC2+BC3 配对
```

这使 RNA 成为“计算分选器”：先根据转录组判断细胞类型或处理状态，再把同一类细胞的损伤 reads 汇总。论文真正可靠的损伤图谱多数是这种 RNA 定义群体后的 pseudobulk，而不是把每个细胞的损伤轨迹当作高置信度地图。

### 4. 从 FASTQ 到细胞类型损伤图谱

#### 4.1 条形码和模态拆分

Read 2 中包含 UMI、三个条形码块以及 linker。论文先根据 linker 确定 BC1、BC2、BC3 的精确位置，再把 192×192×12 种允许组合建成参考序列，用 Bowtie 做近似匹配。

代码仓库中的 `preproc combine_384plex` 是这一环节最完整的实现：它读取成对 FASTQ，提取 8+8+4 bp 条形码和 UMI，并根据 DNA/RNA 接头特征把 reads 分到不同模态。随后 `preproc convert` 把通过白名单匹配的条形码和 UMI 写回 read name。

#### 4.2 DNA/RNA 比对与去重复

仓库中的实际静态流程是：

```text
barcode FASTQ
  → Trim Galore
  → Bowtie2（DNA）/ STAR（RNA）
  → 排序
  → reachtools rmdup2
  → reachtools bam2Mtx2（RNA 10X 风格矩阵）
```

论文还规定了 Q30、DNA MAPQ >10 和细胞覆盖度阈值，但这些过滤没有在一个可移植脚本中完整重现。`per_run.sh` 还保留了原实验室的 `/gpfs` 参考基因组路径，这些路径是来源记录，不应被文档“美化”为可直接运行的本地路径。

#### 4.3 用 RNA 确定细胞身份

RNA 计数矩阵进入 Seurat：SCTransform → PCA → 邻居图 → 聚类 → UMAP。

- HeLa 数据按 BC1 对应的 Ctrl、0 h、2 h、6 h、24 h、48 h 处理组标注。
- 小鼠脑数据根据 marker genes 注释为 ExN、InN、OPC、ODC、AST、MiG、Endo、VLMC 等亚类，并用参考 snRNA-seq 做映射验证。

#### 4.4 汇总损伤信号和找 peaks

单细胞损伤数据噪声大，所以先按 RNA 类别汇总，再做窗口矩阵、peak calling、染色质状态比较和细胞类型特异 peak 分析。

仓库提供了 SnapATAC2 导入 fragment、计算 TSSe 和构建 50-kb tile matrix 的脚本，也提供了 HeLa MACS3 peak calling 脚本。但它们不是完整端到端实现：

- HeLa 脚本使用 `--shift -200 --extsize 400`，与论文 Methods 中报告的 shift 200、extension 500 不一致；
- 小鼠脑完整的 SnapATAC2 marker-region/peak 流程没有在固定提交中找到；
- 脚本依赖外部 BAM、fragment、矩阵和中间结果。

### 5. 怎样把损伤和表达联系起来？

论文认为逐细胞损伤过于随机，因此先用 SEACell 按转录组相似性把细胞聚合成 300 个 metacells。随后，对每个基因，统计其 500 kb 范围内损伤 peaks 的 reads，并用 SnapATAC2 `add_cor_scores` 计算与基因原始表达计数的秩相关；再打乱 metacell 身份建立背景分布。

这一步得到的不是“某个损伤一定调控某个基因”，而是跨 metacell 的统计关联。论文报告 11,814 个正相关和 4,362 个负相关 gene-peak pairs，并比较它们在 H3K4me1、H3K4me3、H3K27ac、H3K9me3、H3K27me3、H3K36me3 区域中的富集。

必须保留一个重要代码边界：固定提交中没有找到完整的 300-SEACell 构建、500-kb 关联、`add_cor_scores` 调用和置换背景实现。仓库只提到 SEACell，并提供了后续 Fisher overlap/odds-ratio 的参考脚本。

### 6. 两个论文公式

#### 物种混合估计条形码碰撞率

设 $N_1$、$N_2$、$N_{12}$ 分别为含至少一个人细胞、至少一个鼠细胞、同时含人鼠细胞的条形码数：

$$
N=\frac{N_1N_2}{N_{12}},
$$

$$
\mu_1=-\ln\left(\frac{N-N_1}{N}\right),\qquad
\mu_2=-\ln\left(\frac{N-N_2}{N}\right),
$$

$$
M=1-\frac{(\mu_1+\mu_2)e^{-\mu_1-\mu_2}}{1-e^{-\mu_1-\mu_2}}.
$$

论文估计碰撞率为 11.4%，但仓库中没有找到显式实现。

#### RNA 注释与参考映射的 overlap coefficient

若 $A_i$ 是 Paired-Damage-seq 标签，$B_j$ 是公开 snRNA-seq 标签，$R_x$ 是参考映射标签：

$$
O_{i,j}=\min\left(
\max\left(\frac{A_i\cap R_x}{A_i}\right),
\max\left(\frac{B_j\cap R_x}{B_j}\right)
\right).
$$

这个公式用于检查两套注释是否通过同一参考类别对齐。固定代码中同样没有找到显式实现。

### 7. 论文得到什么结论？

#### 技术性能

- nickase 切点密度与损伤 reads 的 Spearman $\rho=0.67$；背景为 $\rho=-0.27$；
- 预修复降低损伤峰信号，H$_2$O$_2$ 剂量升高带来更强信号；
- 64,794 个 HeLa 细胞中，每细胞中位数为 5,320 个损伤位点和 4,453 个转录本；
- 聚合 RNA 与 bulk RNA-seq 的 PCC 为 0.87，聚合损伤与 CLAPS-seq 的 PCC 为 0.72；
- 约 1,000 个细胞聚合后，损伤图谱可达到 PCC ≥0.9。

#### 生物学发现

- 损伤在 compartment B、转录区、增强子、STR、Z-DNA 和潜在 G-quadruplex 序列中呈非随机分布；
- H$_2$O$_2$ 后损伤变化与 ATAC、H3K9me3 变化负相关，提示损伤与表观遗传记忆损失相关；
- 小鼠脑中，不同细胞类型有不同的损伤 hotspots；脑特异细胞的 active enhancer 与损伤重叠更强；
- 细胞类型特异 peaks 与功能 GO、转录因子 motif、部分疾病 GWAS 信号和年龄相关染色质衰减区域相关。

### 8. 应该怎样正确解读？

1. **测到的是混合损伤类别。** 8-oxoG、AP site 和 SSB 被合并为一个信号，不能逐 read 区分。
2. **热点是“形成−修复”的净结果。** 高信号可能来自更多损伤，也可能来自更慢修复。
3. **多数结果依赖群体汇总。** RNA 提供细胞身份，损伤图谱通常是该类细胞的聚合结果。
4. **相关不是因果。** 损伤、表达、ATAC、H3K9me3、衰老和疾病风险之间的统计联系不能单独证明方向。
5. **疾病分析统计功效有限。** 小鼠到人类坐标映射、高背景和跨数据集整合都会增加不确定性。
6. **代码可复现性为中等。** 预处理实现较具体；下游分析保留 `/gpfs` 路径、缺少完整 SEACell/SnapATAC2 correlation 实现、缺少锁包环境，并依赖未随仓库提供的中间数据。

### 9. 最值得记住的设计思想

Paired-Damage-seq 的真正价值在于把两个互补信息源拼在一起：RNA 很适合回答“这是什么细胞”，损伤 reads 更适合在同类细胞汇总后回答“这类细胞的基因组哪里经常受伤”。它没有消除损伤的随机性，而是利用配对转录组先建立生物学分组，再把随机单细胞信号变成可解释的群体级选择性脆弱图谱。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Paired-Damage-seq

**Paper:** *Single-cell parallel analysis of DNA damage and transcriptome reveals selective genome vulnerability* — *Nature Methods* (2025), DOI `10.1038/s41592-025-02632-3`.

### Problem

Oxidative DNA lesions are nonrandomly distributed, but bulk sequencing averages across heterogeneous cell types and damage-only single-cell measurements are dominated by sparse, stochastic signal. Existing bulk damage maps cannot connect vulnerable loci to a cell's identity or transcriptional program, while prior single-cell multiomics assays generally measure RNA with chromatin modalities rather than DNA damage itself.

### Proposed Technology

Paired-Damage-seq jointly profiles oxidative base damage, AP sites and single-strand breaks with RNA in the same cell. It uses an in situ “labeling-by-repair” reaction: Fpg and Endo IV expose/process lesions, *Bst* polymerase incorporates biotin-dUTP by nick translation, and *Taq* ligase seals the nick. Anti-biotin-directed protein A-Tn5 then tags damage-proximal DNA. The DNA fragments and reverse-transcribed RNA receive a shared BC1 barcode followed by two ligation-based combinatorial barcodes, BC2 and BC3, so both modalities can be assigned to the same nucleus.

After sequencing, RNA is used to infer treatment state or cell type. Sparse damage reads are then aggregated within those RNA-defined groups to obtain condition- and cell-type-resolved damage maps. Peak calling, chromatin-state comparisons, metacell-level damage-expression correlations and regulatory/disease enrichment analyses characterize selective genome vulnerability.

### Evaluation and Main Results

- **Specificity controls:** damage signal increased with Nt.BbvCI cutting-site density (Spearman $\rho=0.67$), decreased after prerepair, and increased with H$_2$O$_2$ dose. Nontargeting tagmentation and ATAC-seq controls did not reproduce the same patterns.
- **Single-cell scale:** 64,794 filtered HeLa cells yielded median values of 5,320 damage loci and 4,453 transcripts per cell. Species mixing estimated an 11.4% barcode collision rate.
- **Cross-assay agreement:** aggregated RNA agreed with bulk RNA-seq (PCC 0.87), and aggregated damage agreed with CLAPS-seq (PCC 0.72). Aggregating approximately 1,000 cells gave a damage profile with PCC at least 0.9 to the larger aggregate.
- **HeLa stress response:** damage was structured by chromatin and sequence context. Heterochromatic compartment B carried higher average damage, while transcribed regions, enhancers, short tandem repeats, Z-DNA and putative G-quadruplex sequences showed selective susceptibility. Damage changes were negatively associated with accessibility and H3K9me3 changes, and metacell analysis reported 11,814 positive versus 4,362 negative linked gene-peak pairs.
- **Mouse cortex:** 73,813 cells were assigned to major neuronal and non-neuronal subclasses using RNA. Damage maps showed conserved repeat/compartment effects plus cell-type-specific enhancer and motif patterns. Brain-specific cell types had stronger damage enrichment at active enhancers than Endo/VLMC populations.
- **Functional associations:** cell-type-specific peaks aligned with relevant GO terms, transcription-factor motifs, selected GWAS traits and regions that lose chromatin accessibility or H3K9me3 with age. These analyses are predictive/associative, not causal.

### What Is Novel

The central advance is not merely another single-cell barcoding system: it converts DNA lesions into an enrichable signal and links that signal to a transcriptome-derived cell identity. This makes it possible to ask which genomic regions are repeatedly vulnerable in a particular cell class even when individual-cell damage profiles are too noisy for direct clustering.

### Code-Paper Match and Reproducibility

**Reproducibility rating: 3/5 (moderate).** Repository: `czhulab/Paired-Damage-seq`, fixed at commit `2efce21e45045810a7e4473d1094a51089785781`.

The strongest code-paper match is the preprocessing path: barcode/modality extraction, whitelist mapping, DNA/RNA alignment, duplicate removal and RNA matrix generation are concretely implemented. HeLa Seurat clustering, MACS3 peak calling, Fisher overlap tests, mouse-brain Seurat annotation and SnapATAC2 fragment/tile-matrix creation are also represented.

Important limits remain:

- downstream scripts preserve external `/gpfs` paths and depend on unbundled matrices, BAMs, fragments and intermediate tables;
- the deposited HeLa MACS3 script uses peak parameters that differ from the Methods text;
- the complete 300-SEACell plus SnapATAC2 `add_cor_scores` damage-expression correlation workflow was not found;
- explicit implementations of the collision formula and RNA-reference overlap coefficient were not found;
- downstream R/Python/system package versions are not locked, and the repository describes those analyses as reference code;
- two publisher supplement PDFs are retained (Reporting Summary and Peer Review), but no supplementary Markdown exists (`SUPP_MD=none`).

The public code is therefore useful for understanding preprocessing and reconstructing many figure analyses, but it does not constitute a verified one-command end-to-end reproduction of all reported results.

### Major Scientific Limitations

- The assay pools 8-oxoG, AP sites and SSBs under one damage signal rather than resolving lesion types per read.
- Observed hotspots combine damage formation and repair kinetics.
- Reliable biological conclusions usually require aggregation by RNA-defined groups, limiting per-cell damage interpretation.
- Damage-expression, epigenetic-aging and GWAS results are associations across modalities/datasets and should not be read as direct causal proof.
- Mouse-to-human peak mapping and high background reduce statistical power for disease-trait enrichment.

### Bottom Line

Paired-Damage-seq provides a persuasive biochemical and computational strategy for revealing nonrandom, cell-type-specific genome vulnerability. Its validation and main biological patterns are well supported by the paper's 12 figures, while the released repository offers medium-fidelity computational support with a clear boundary between a concrete preprocessing implementation and incomplete, environment-dependent downstream reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
