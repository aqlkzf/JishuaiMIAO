---
layout: default
permalink: /paper-atlas/sc-splash-80906cb2/
title: "sc-SPLASH"
nav: false
description: "sc-SPLASH 不先问“这个 read 比对到哪个基因”，而是先问： > 在同一个固定序列上下文之后，不同细胞是否偏好出现不同的后续序列？ 如果答案是肯定的，这种差异可能来自可变剪接、体细胞突变、等位基因、旁系同源基因、V(D)J 重排、转座/重复序列，甚至参考基因组中根本不存在的基因。sc-SPLASH 先用统计量找到异常序列模式，再用比对、组装、Pfam、BLAST 或实验验证解释其生物学含义。"
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
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>sc-SPLASH</h1>
    <p>Reference-free discovery with barcoded single-cell sequencing</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/refresh-bio/splash" target="_blank" rel="noopener noreferrer" aria-label="Open code for sc-SPLASH">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## sc-SPLASH 方法详解：从带条形码的原始读段中做无参考序列发现

### 一句话理解

sc-SPLASH 不先问“这个 read 比对到哪个基因”，而是先问：

> 在同一个固定序列上下文之后，不同细胞是否偏好出现不同的后续序列？

如果答案是肯定的，这种差异可能来自可变剪接、体细胞突变、等位基因、旁系同源基因、V(D)J 重排、转座/重复序列，甚至参考基因组中根本不存在的基因。sc-SPLASH 先用统计量找到异常序列模式，再用比对、组装、Pfam、BLAST 或实验验证解释其生物学含义。

### 1. 论文要解决什么问题？

常规 10x 单细胞 RNA-seq 分析通常经历“比对到参考基因组 → 按基因计数 → 聚类/差异表达”。这套流程非常适合表达量分析，但有三个盲区：

1. **依赖参考序列。** 非模式生物、复杂重复区或高度多态基因可能缺失或组装错误。
2. **基因级汇总会抹平序列差异。** 两个细胞可以表达同一个基因，却使用不同外显子、突变或等位序列。
3. **已有工具常针对单一事件。** 例如只分析剪接、免疫受体或多聚腺苷酸化，难以统一发现未知事件。

相关前作包括 SPLASH（*Cell*, 2023）和面向大规模 bulk 数据的 SPLASH2（*Nature Biotechnology*, 2025）；UMI-tools（*Genome Research*, 2017）处理条形码/UMI 误差，但不是通用序列变异发现框架；STARsolo（bioRxiv, 2021）和 Cell Ranger（相关技术论文发表于 *Nature Communications*, 2017）以比对和定量为中心。sc-SPLASH 的新意是把 SPLASH 的“anchor–target 条件分布检验”扩展到数千至数十万带条形码的细胞或空间 spot。

### 2. 核心概念：anchor、target 和条件分布

从每条 read 中取两个固定长度的 $k$-mer：

- **anchor**：较稳定的上游序列，记为 $A$；
- **target**：anchor 后面的可变序列；
- **sample**：在 scRNA-seq 中是“实验编号 + 细胞条形码”，在 Visium 中是空间 spot。

对一个 anchor，sc-SPLASH 统计每个细胞中各个 target 的出现次数。真正关心的不是 anchor 总表达量，而是条件分布：

$$
P(\text{target}\mid \text{观察到 anchor},\text{cell}).
$$

这也是论文所说对批次效应较稳健的直觉：如果某个样本整体测序更深，anchor 和 target 计数可能一起增加；方法检验的是“已经看到 anchor 的条件下，各 target 的相对组成是否变化”，而不是只比较总计数。

设 anchor $A$ 有 $T$ 个 target，在样本 $j$ 中第 $i$ 个 target 的计数为 $t_{ij}^{A}$，则其细胞内比例为

$$
p_{ij}^{A}=\frac{t_{ij}^{A}}{\sum_{\kappa=1}^{T}t_{\kappa j}^{A}}.
$$

### 3. 完整计算流程

```text
R1：cell barcode + UMI        R2：cDNA 序列
              \                /
               └── 阶段 1：BKC ──┘
                   可信条形码筛选/可选纠错
                   UMI 去重
                   每个细胞的 anchor-target 计数
                   接头、同聚物和低计数过滤
                              ↓
                 SATC：sample/barcode/anchor/target/count
                              ↓
            阶段 2：按 anchor 合并并建立稀疏列联表
                  行 = targets，列 = cells/spots
                              ↓
                 无监督统计检验 + effect size
                              ↓
            阶段 3：Benjamini–Yekutieli 多重校正
                              ↓
                       显著 anchors
                   ↙          ↓          ↘
             target entropy  监督 GLM   比对/组装/Pfam/JSON
```

#### 阶段 1：BKC 预处理和计数

论文描述的 BKC 输入是成对 FASTQ：R1 包含条形码和 UMI，R2 包含 cDNA。它会：

1. 根据用户白名单或 barcode read-count 曲线的 knee point 选择可信条形码；
2. 可把与可信条形码相差一个碱基的条形码纠正过去；
3. 按“barcode + UMI”去重；
4. 从 R2 枚举 anchor–target 对；
5. 以“实验编号 + barcode”为 sample ID 写入 SATC 文件；
6. 过滤长同聚物、接头/污染序列和低频 $k$-mer。

代码中可直接确认 SPLASH Python 主程序会构造 `bkc --mode pair` 命令，并传入 anchor/target/gap 长度、barcode/UMI 长度、线程数、过滤阈值和 sample ID（`splash/src/splash.py:1140-1189`）。

#### 阶段 2：为每个 anchor 建稀疏列联表

对每个 anchor $A$，构造矩阵 $X_A$：

- 每一行是一个 target；
- 每一列是一个细胞/spot；
- 元素是该细胞中的 target count。

代码确实把 experiment ID 和 barcode 打包成列标识，并用紧凑稀疏矩阵存储非零计数（`splash/src/satc_merge/pvals.cpp:701-750`）。这一步是 sc-SPLASH 能扩展到成千上万个细胞的关键。

低覆盖 anchor 会先被过滤。论文实际分析使用 27 bp anchor、27 bp target、无 gap，并要求 anchor 总计数至少约 50、至少出现在两个细胞中、单细胞内至少约 5 个计数，同时过滤长同聚物和 UniVec 匹配（`paper.md:202-205`）。这些是论文运行设置；软件通用默认长度为 31 bp。

#### 无监督统计检验

论文层面的目标是检验：

$$
H_0:\quad \text{不同细胞具有相同的 target 条件分布}.
$$

若拒绝 $H_0$，说明该 anchor 后的序列组成随细胞变化。effect size 位于 0–1：越接近 0，两组细胞的 target 分布越相似；越接近 1，越容易按 target 分布把细胞分开。

代码还揭示了论文正文没有展开的实现细节：

1. 对每个细胞列，默认抽取约 25% 的**计数**形成训练矩阵，剩余计数形成测试矩阵；这不是把细胞分成训练组和测试组。
2. 在训练矩阵上交替优化 target 侧向量 $f$ 和 sample 侧对比向量 $c$；$c$ 的正负号诱导两组细胞。
3. 在保留的测试计数上计算 `pval_opt` 和 `effect_size_bin`，避免完全在同一批计数上寻找并检验分组。
4. 默认尝试 10 个随机初始化，每次最多 50 次交替迭代。

完整统计推导没有在这篇主论文中重新给出，而是引用 SPLASH/SPLASH2/OASIS；这里能够确认的是代码行为，而不是仅凭本文重建全部理论证明。

#### 阶段 3：多重检验

同时检验大量 anchors 必须控制假发现率。代码对排序后的 P 值使用 Benjamini–Yekutieli 校正：

$$
c_m=\sum_{i=1}^{m}\frac{1}{i},\qquad
p_{(r)}^{\mathrm{raw\ adj}}=p_{(r)}\frac{m c_m}{r},
$$

再从大到小取累积最小值保证单调。校正后 P 值低于阈值（默认 0.05）的 anchor 被保留。这一点与论文方法完全对应（`splash/src/sig_anch/sig_anch.cpp:457-485`）。

### 4. 三个容易混淆的量

#### P 值：是否存在细胞依赖的分布差异？

回答“这个 anchor 是否值得被调用”。

#### Effect size：差异有多强？

回答“target 分布能多清楚地把细胞分成两组”。论文多数下游结果还要求 effect size > 0.2。

#### Target entropy：target 本身有多丰富？

先把所有细胞的同一 target 计数相加：

$$
t_i^{A}=\sum_{j=1}^{N}t_{ij}^{A},\qquad
p_i^{A}=\frac{t_i^{A}}{\sum_{\kappa=1}^{T}t_{\kappa}^{A}},
$$

再计算

$$
H_A=-\sum_{i=1}^{T}p_i^{A}\log_2p_i^{A}.
$$

代码中的 `target_entropy` 与这个公式**完全一致**（`splash/src/satc_merge/extra_stats.cpp:78-92,176-197`）。不要把它和 `anchor_2mer_seq_entropy`、`anchor_3mer_seq_entropy` 混淆；后者衡量单条序列内部 2-mer/3-mer 组成复杂度，不是论文的 target 多样性。

一个 anchor 可以：

- P 值显著但 entropy 不高：只有少数 target，但不同细胞偏好不同；
- entropy 很高但 effect size 不高：target 很多，却在各细胞中分布相近；
- 三者都高：既多样，又强烈随细胞变化，通常最值得深入研究。

### 5. 有 metadata 时的监督分析

若知道细胞类型 $C_j$，论文提出对每个 anchor 做 $L_1$ 正则化多项逻辑回归：

$$
C_j\sim p_{1j}^{A}+p_{2j}^{A}+p_{3j}^{A}+\cdots.
$$

直觉是：如果 target 比例能预测细胞类型，那么这个 anchor 的序列变化具有细胞类型特异性。

但代码与论文公式只有**部分匹配**。实际 R 脚本会：

- 先筛选覆盖广、Hamming 距离较大且无监督 effect size 较高的 anchors；
- 每个 anchor 只保留最丰度的四个 targets；
- 去掉 anchor count ≤ 5 的细胞和样本数 ≤ 5 的类别；
- 用类别样本数的倒数作为权重；
- 运行四折 `cv.glmnet`，`family="multinomial"`、`alpha=1`、无截距；
- 当最大**绝对值**系数 > 1 时报告 anchor。

因此，监督结果应理解为“经过额外筛选和类别平衡后的 top-four-target 分类信号”，而不是对论文中所有 $T$ 个 target 的字面实现。

### 6. 从显著 anchor 到生物学解释

显著性调用本身只说明 target 组成随细胞变化，不会自动告诉你原因。论文的解释层包括：

- 把 anchor 与最常见的四个 target 拼成 extendors；
- 用 STAR/Bowtie2 对参考基因组或转录组比对；
- 判断剪接位点、SNP/突变、旁系同源基因；
- 用 BLAST、Pfam 或局部组装解释无参考序列；
- 比较 target 的 Hamming、Levenshtein 和最长公共子序列距离；
- 用 JSON 的 `name` 和 `command` 定义用户后处理。

代码会替换 `{significant_extendors_tsv}` 等占位符，在独立输出目录中运行命令。一个隐藏行为是：后处理命令失败时只给警告，不会让核心 sc-SPLASH 主流程失败，因此必须检查各后处理目录的日志。

### 7. 论文如何验证方法？

#### 计算效率

- BKC 平均用 165 s、7 GB 完成条形码过滤、UMI 去重和过滤 FASTQ 输出；对比的 UMI-tools 步骤平均用 9,272 s。需要注意，两者计时任务并不完全相同：UMI-tools 计时没有包含后续依赖比对的 UMI 去重。
- 在 Tabula Sapiens muscle 数据上，sc-SPLASH 每样本约 106–128 s、8–18 GB；STARsolo 为 491–668 s、35 GB；Cell Ranger 为 2,540–2,798 s、64–70 GB。

#### 已知事件

- 在超过 40 万个人体细胞中找到 555 个具有细胞类型特异 anchor 的基因，包括已知可变剪接基因 *RPS24* 和 *MYL6*。
- V-set 免疫球蛋白结构域具有最高的报告 entropy（2.16）和 effect size（0.90），结合 IgBLAST 找到 60,697 条 productive、in-frame V(D)J 序列。
- Visium 数据中识别到癌区富集的 *MT-ND4* 双突变、*KRT16/KRT17* 空间差异和 *RPS24* 组织区特异剪接。

#### 参考缺失的新发现

- 在淡水海绵 *Spongilla* 中，“granny” anchor 的 entropy 为 6.2、关联 667 个 targets，但参考基因组和 NCBI 中都找不到。它主要表达于 granulocytes 和 amebocytes，最终通过长读长组装得到五个高度多态的分泌型重复基因 *Granrep1–5*。
- 在 *Ciona* 中，YYD anchor 揭示了另一组重复丰富、等位多态的分泌蛋白基因，并在间充质细胞/血细胞及变态发育阶段呈调控表达。

这些结果说明 sc-SPLASH 能从“统计异常序列模式”走到“新基因家族候选”。但 Granrep/YYD 的免疫功能仍是由表达位置、重复结构和刺激/发育模式支持的假说，并非直接功能实验证明。

### 8. 阅读结果时最重要的判断顺序

拿到一个 sc-SPLASH anchor 后，建议依次问：

1. **覆盖够不够？** 总计数、表达细胞数、单细胞计数是否接近阈值？
2. **统计是否显著？** 看校正 P 值，而不是原始 P 值。
3. **分离是否强？** 看 effect size，避免只追逐微弱但大样本显著的信号。
4. **多样性是否真实？** 看 target entropy 和丰度长尾，排除大量单次测序错误造成的“伪多样”。
5. **能否解释？** 比对、组装、Pfam/BLAST 或 target 距离是否支持剪接、突变、重复等机制？
6. **是否有独立证据？** 空间定位、跨供者重复、长读长、RNA-FISH 或 perturbation 是否支持？

### 9. 代码可复现性与已知缺口

- 已直接验证：稀疏 target-by-cell 矩阵、无监督统计调用路径、Benjamini–Yekutieli 校正、target entropy、JSON 后处理。
- 部分匹配：监督 GLM。
- **MISSING / Not found：** BKC 源码在当前快照中缺失；多个依赖 submodule 目录也是空的。
- 本地没有 supplementary Markdown，无法审核补充表格和补充 PDF 中的全部参数/计数。
- 仓库包含通用示例和 notebook，但没有找到一个能一次性重现 Tabula Sapiens、Visium、海绵和 *Ciona* 全部论文结果的本地流程。
- 本 Author 阶段未编译代码，也未重跑数据。

因此，最稳妥的结论是：sc-SPLASH 的核心统计和熵计算在 SPLASH 主仓库中有清晰实现，论文的主要图像和结果形成了完整的概念验证；但要端到端复现整篇论文，还需要补齐 BKC/依赖 submodules、补充材料、原始数据和论文专用分析脚本。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## sc-SPLASH: Reference-Free Discovery from Barcoded Single-Cell Sequencing

### Problem

Standard droplet scRNA-seq workflows align reads to a reference and emphasize gene-level expression. They can miss sequence variation from alternative splicing, mutations, alleles, paralogs, V(D)J rearrangement, repeats and genes absent from an incomplete reference. Existing tools are often event specific, alignment dependent or expensive at droplet-scale cell counts (`paper.md:21-24`).

Relevant predecessors illustrate the gap: SPLASH (*Cell*, 2023) introduced reference-free anchor–target statistics; SPLASH2 (*Nature Biotechnology*, 2025) made the bulk workflow scalable; UMI-tools (*Genome Research*, 2017) handles barcode/UMI errors but is not an anchor–target discovery engine; STARsolo (bioRxiv, 2021) and Cell Ranger (technology described in *Nature Communications*, 2017) are alignment/quantification pipelines rather than general sequence-variation tests (`paper.md:333-340`).

### Proposed Technology

sc-SPLASH extends SPLASH to 10x-style single-cell RNA-seq and Visium spatial transcriptomics. It searches raw reads for fixed $k$-mers (**anchors**) followed by variable $k$-mers (**targets**), builds a target-by-cell contingency table for each anchor and tests whether target distributions differ across cells or spots. The statistical call is reference free and does not require cell labels; alignment, Pfam/BLAST search, local assembly or custom scripts are optional interpretation steps afterward.

The pipeline has three core stages:

1. **BKC preprocessing and counting:** extract/trust/correct cell barcodes, deduplicate UMIs, count anchor–target pairs per cell and filter artifacts.
2. **Sparse contingency statistics:** merge counts across cells, construct a sparse target-by-cell matrix, estimate a separating contrast, compute a held-out P value and effect size, and calculate target diversity.
3. **Multiple-testing correction:** apply Benjamini–Yekutieli correction and retain anchors below the FDR threshold.

An optional supervised branch fits $L_1$-regularized multinomial regression to identify anchors whose target fractions predict metadata classes. Target entropy is

$$
H_A=-\sum_i p_i^A\log_2 p_i^A,
$$

where $p_i^A$ is the marginal count fraction of target $i$ for anchor $A$ (`paper.md:166-181`).

### What Is New

- A barcoded-read counting layer designed for thousands of cells/spots rather than bulk samples.
- Sparse per-anchor contingency matrices and optimized statistics for droplet-scale data.
- A reference-free core that can detect known events and unknown sequences in poorly assembled organisms.
- One framework spanning unsupervised discovery, optional metadata regression, entropy ranking and user-defined JSON postprocessing.
- A separate BKC tool reported to make barcode filtering/UMI preprocessing practical at scale.

### Evaluation and Results

#### Computational efficiency

On four 10x benchmark datasets, BKC averaged 165 s and 7 GB for barcode filtering, UMI deduplication and filtered FASTQ output. The compared UMI-tools steps averaged 9,272 s and 0.6 GB, about 50 times longer, but performed only whitelist/extract processing and not the later alignment-dependent UMI deduplication, so the runtime comparison is not task-identical (`paper.md:154-163`).

For Tabula Sapiens muscle, sc-SPLASH required 106–128 s and 8–18 GB per sample, versus 491–668 s and 35 GB for STARsolo and 2,540–2,798 s and 64–70 GB for Cell Ranger. Across tested depths, the paper summarizes sc-SPLASH as approximately fivefold faster than STARsolo and twentyfold faster than Cell Ranger through significant-anchor calling (`paper.md:47,133-151`; Fig. 1b–c).

#### Human single-cell and spatial data

- More than 400,000 Tabula Sapiens cells yielded 555 genes with cell-type-specific anchors; *RPS24* and *MYL6* were recovered across many tissues, consistent with known alternative splicing (`paper.md:50`).
- Immunoglobulin V-set calls had the highest reported Pfam-domain entropy (2.16) and effect size (0.90), and integration with local assembly/IgBLAST detected 60,697 productive in-frame V(D)J sequences across 16 tissues (`paper.md:53`).
- Visium analyses recovered a carcinoma-associated *MT-ND4* double mutation, spatially distinct *KRT16/KRT17* paralog usage and tissue-specific *RPS24* isoforms in human intestine and electric eel (`paper.md:56-59`; Fig. 1f–g; Extended Data Fig. 3).

#### Discovery beyond the reference

In freshwater sponge, the highest-entropy “granny” anchor had entropy 6.2 and 667 targets but no match in the reference genome or NCBI. It was enriched in granulocytes and amebocytes and led, with long-read assembly and validation, to five polymorphic secreted repeat genes (*Granrep1–5*) (`paper.md:62-76`; Fig. 2a–e).

In *Ciona*, a high-entropy YYD anchor revealed repeat-rich secreted genes with extensive target and allelic diversity. Expression localized to mesenchymal cells/hemocytes and peaked around metamorphosis (`paper.md:79-88`; Fig. 2f–i). These examples demonstrate the main advantage of statistics-first discovery: a significant sequence pattern can be found before a complete gene model exists.

### Code-Paper Match

Overall fidelity is **medium**: Exact 6, Partial 1, Not found 1.

- **Exact:** orchestration of 10x/Visium BKC jobs, sparse target-by-cell table construction, unsupervised statistic/effect-size path, Benjamini–Yekutieli correction, the published target-entropy formula and JSON postprocessing.
- **Partial:** the supervised GLM uses the paper's $L_1$ multinomial idea but keeps only the top four targets, adds anchor/cell/group filters and inverse-group weights, uses cross-validation, and thresholds the largest absolute coefficient.
- **Not found:** BKC's internal source is absent because `splash/libs/bkc/` is empty in this acquired snapshot. The orchestrator and build metadata are present, but barcode correction, UMI deduplication and counting internals cannot be verified locally.

A subtle verified detail is that the paper's entropy is emitted as `target_entropy` from marginal target counts. The code's separately named 2-mer/3-mer `sequence_entropy` values measure within-sequence composition and are not the published target-diversity equation.

### Reproducibility Assessment: 3/5

Strengths:

- Core sparse statistics, FDR correction, entropy and supervised R code can be inspected directly.
- The repository includes small input manifests, download helpers, analysis examples and postprocessing examples.

Gaps:

- BKC and several dependency submodule directories are empty, so this snapshot is not independently build-complete.
- No supplementary Markdown is local, and the exact paper-wide Tabula Sapiens, Visium, sponge and *Ciona* workflows are not packaged as one rerunnable pipeline.
- The primary paper cites prior SPLASH/OASIS work for the full statistical derivation rather than reproducing it.
- Compilation and dataset reruns were not performed in this Author phase.

### Limitations and Interpretation

- A significant anchor says that target composition varies across cells; it does not by itself identify the causal mechanism. Splicing, mutation, paralog and gene-family assignments depend on downstream alignment/assembly and biological validation.
- Reference freedom helps discover missing sequences, but interpretation becomes harder when no genome or annotation exists.
- Count and prevalence thresholds trade sensitivity for robustness, so lowly covered events can be missed.
- Entropy ranks diversity, not biological importance; repeat artifacts or sequencing errors still require filtering and follow-up.
- The proposed immune roles of Granrep and YYD proteins are hypotheses supported by cell-type localization, repeat architecture and perturbation/developmental expression, not direct functional tests.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
