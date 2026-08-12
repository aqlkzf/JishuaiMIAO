---
layout: default
permalink: /paper-atlas/droplet-hi-c-20de05df/
title: "Droplet-Hi-C"
nav: false
description: "Droplet Hi-C 把传统的原位 Hi-C 近邻连接化学，接到成熟的 10x Genomics 液滴微流控平台上，从而一次测量数万细胞的染色质三维接触；在此基础上，论文又构建了面向正常组织的细胞类型/染色质结构分析，以及面向肿瘤的 CNV、SV、ecDNA 和同细胞 RNA 联合分析。"
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
    <h1>Droplet-Hi-C</h1>
    <p>Droplet Hi-C enables scalable, single-cell profiling of chromatin architecture in heterogeneous tissues</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Droplet Hi-C 方法详解

### 一句话理解

Droplet Hi-C 把传统的原位 Hi-C 近邻连接化学，接到成熟的 10x Genomics 液滴微流控平台上，从而一次测量数万细胞的染色质三维接触；在此基础上，论文又构建了面向正常组织的细胞类型/染色质结构分析，以及面向肿瘤的 CNV、SV、ecDNA 和同细胞 RNA 联合分析。

### 1. 它解决什么问题？

染色质接触图描述基因组不同位置在细胞核中是否彼此靠近。它能揭示 A/B compartment、结构域、环、结构变异和环外 DNA，但异质组织有三个难点：

1. **bulk Hi-C 会平均掉细胞差异。** 脑组织中的不同神经元、胶质细胞，或肿瘤中的恶性、免疫和基质细胞会混在一起。
2. **早期单细胞 Hi-C 难以扩展。** single-cell Hi-C（*Nature*, 2013/2017）、single-nucleus Hi-C（*Nature*, 2017）和 Dip-C（*Science*, 2018）能获得单细胞结构，但微孔流程规模有限、耗时且成本高。
3. **高通量或多组学方法仍然复杂。** sci-Hi-C（*Nature Methods*, 2017）使用组合索引提高通量，却有覆盖稀疏和手工流程长的问题；HiRES（*Science*, 2023）与 GAGE-seq（*Nature Genetics*, 2024）能同时测 RNA，但实验实施仍较复杂（`paper.md:21-30,528-538`）。

肿瘤还增加了 CNV、SV 和 ecDNA 异质性。仅看扩增倍数，常常分不清圆形的 ecDNA 与整合在染色体上的 HSR；bulk 测量也看不到不同克隆在治疗前后的变化（`paper.md:27,85-111`）。

### 2. 核心创新

#### 2.1 把 in situ Hi-C 接到商业液滴平台

Droplet Hi-C 不重新发明微流控芯片，而是使用普及度较高的 10x Genomics Single Cell ATAC 系统：

- 先在完整细胞核内完成限制性酶切和近邻连接；
- 再用 Tn5 打断连接后的 DNA；
- 将单个细胞核与带条形码的 gel bead 包进液滴；
- 让来自同一细胞的片段获得同一细胞身份。

论文报告从固定细胞到测序文库约 10 小时，可并行处理 8 个样本，一批达到 40,000 个以上细胞（`paper.md:36-47`；Figure 1）。

#### 2.2 同一平台覆盖正常组织与肿瘤

正常组织的主要困难是稀疏，因此可以先插补，再研究细胞类型、compartment、domain、loop 和 multi-way hub。肿瘤的主要困难是基因组不稳定，所以作者明确不对癌细胞接触矩阵做插补，避免把 CNV/SV 结构平滑掉（`paper.md:315-318`）。

#### 2.3 用三维接触模式识别 ecDNA

ecDNA 与 HSR 都可能有高拷贝数，但空间行为不同：ecDNA 倾向于更均匀地接触多个染色体，而 HSR 位于染色体上，接触分布更集中。论文把拷贝数、跨染色体接触均匀性和 trans/cis 倾向组合成 logistic 与 CNN caller。

#### 2.4 Paired Hi-C 同时测 RNA

Paired Hi-C 改用 10x Multiome 试剂并保护 RNA，使同一细胞核同时产生 Hi-C 和转录组数据。这样可以直接问：某个 compartment 转换、ecDNA 边界或拷贝数变化，是否对应同一细胞中的表达变化。

### 3. 实验流程

```text
细胞/细胞核
  → 1% 甲醛固定（Paired Hi-C 通常为 0.6%）
  → 裂解与 SDS 处理
  → DpnII + MboI + NlaIII 三酶切割
  → T4 DNA ligase 原位连接
  → FANS 纯化细胞核
  → 10x 液滴内 Tn5 tagmentation 和细胞条形码
  → 建库与双端测序
```

Droplet Hi-C 的固定、酶切和连接参数见 `paper.md:237-255`。三种限制性内切酶增加可形成连接片段的位点密度。作者延长 index PCR 的延伸时间，并调整 SPRI 比例，以保留较长的 Hi-C 连接片段。

Paired Hi-C 加入 RNaseOUT/SUPERaseIn，采用较温和的 SDS 条件，并修改 cDNA 纯化以保留短转录本（`paper.md:258-276`）。RNA 与 Hi-C 在同一 gel bead 上使用不同条形码，需要根据 Multiome whitelist 做人工映射（`paper.md:465-468`）。

### 4. 从 FASTQ 到单细胞 contact map

```text
FASTQ
  → 提取并校正 10x barcode
  → Trim Galore 去接头
  → BWA-MEM (-SP5M) 比对 hg38/mm10
  → Pairtools parse / sort
  → 把 barcode 写入 pairs 列
  → barcode-aware deduplication
  → 每细胞 contact 统计和质控
  → Cooler 生成多分辨率矩阵
```

这条主路径在 `04.proc_paired_hic_v2.1.sh:39-96` 中有直接实现。`phc.pairsam_add_bc.v2.pl:15-56` 从 read name 恢复两个 barcode 列，`phc.count_pairs_sc.py:28-65` 统计 cis/trans contacts，`PHCrankPair` 用 rank–count 曲线的 elbow 选择细胞（`phc_help.R:56-99`）。

一个需要特别注意的源码问题是：统计脚本初始化键名 `duplicate`，但遇到重复 read 时增加的是 `duplicates`（`phc.count_pairs_sc.py:43-49`）。因此复现前应修复或确认输入已经完全去重。

### 5. 正常组织分析：从稀疏矩阵到细胞类型

#### 5.1 scHiCluster 插补

成年小鼠皮层的单细胞矩阵很稀疏。作者在去除 blacklist 后，使用线性卷积和 random walk with restart：

- 100 kb：整条染色体表示和可视化；
- 25 kb：结构域边界；
- 10 kb：基因分数和 loop（`paper.md:315-318`）。

代码给出 `rp=0.5`、`tol=0.01` 和不同分辨率的窗口（`schic_impute_v2.sh:34-70`）。但当前脚本循环只启用 10 kb，复现论文时需要恢复 25/100 kb 运行。

#### 5.2 scGAD：把接触图变成 cell × gene 矩阵

对基因 $i$ 和细胞 $j$，scGAD 分数 $R_{ij}$ 是 10-kb 插补矩阵中落在基因体区域的原始接触数。这样，每个细胞不再由一个巨大的二维接触矩阵表示，而是由“每个基因附近有多少接触”的向量表示（`paper.md:321-324`）。

随后：

1. 在参考 snRNA-seq 中选择 2,000 个变异基因；
2. 用 RNA 拟合 30 个 PC；
3. 用同一 PCA 变换 scGAD；
4. 通过 CCA/Seurat 风格整合；
5. 对每个 Hi-C 细胞寻找 15 个最近的 RNA 邻居；
6. 按距离加权转移细胞类型标签（`paper.md:327-330`）。

论文在小鼠皮层识别出 20 个群体，包括 5 个非神经元、9 个谷氨酸能和 6 个 GABA 能细胞类型（`paper.md:62`）。

#### 5.3 compartment、domain、loop 与 hub

- **Compartment：** 100 kb balanced matrix 做特征分解，并用 CpG 密度确定 A/B 符号；样本间用 Spearman 相关比较。
- **Domain：** 25 kb 计算 insulation；某 bin 在一种细胞类型中被多少比例的细胞判为边界，即 boundary probability。FDR <0.001 且概率差 >0.05 时定义为可变边界。
- **Loop：** sample level 使用 `cooltools dots`，细胞类型层面使用修改后的 SnapHiC/scHiCluster 流程。
- **Multi-way hub：** 一个 paired-end 分子若连接至少 3 个不同的 10-kb bin，就支持多路接触；在一个细胞类型中，参与多路接触的细胞频率转为 $Z$ 分数，$Z>1.96$ 定义为 hub（`paper.md:336-381`）。

Figure 2 显示这些结构与匹配细胞类型的 H3K27ac、super-enhancer 和 marker gene 富集相关，但这是关联证据，不等于结构变化直接导致表达变化。

### 6. 肿瘤分析：CNV、SV 与 ecDNA

#### 6.1 CNV 与 SV

NeoLoopFinder 的 `calculate-cnv` 用广义加性模型残差估计 copy-number ratio。假设样本为二倍体：

$$
\widehat{\mathrm{CN}}=2\times\text{copy-number ratio}.
$$

CNV 校正后的 contact matrix 再交给 EagleC `predictSV`，组合多分辨率结果并注释融合基因（`paper.md:384-393`）。对应 wrapper 在 `neoloop_cnv.sh:52-71`，但其 `--hic-50k` 实际指向 25-kb matrix，需要复现者核对。

#### 6.2 ecDNA 的三个直观特征

对 1-Mb bin $i$：

1. **Copy number：** 是否存在扩增。
2. **Hub index：** 该 bin 与各染色体 trans contacts 的 Gini 系数。分布越均匀，Gini 越低。
3. **Trans-to-cis contacting-bin ratio：**

$$
R_i=\frac{N_T}{N_C}.
$$

$N_T$ 是其他染色体上发生接触的 bin 数，$N_C$ 是同一染色体上的接触 bin 数（`paper.md:396-399`）。

代码中的 logistic 路径使用的却是

$$
\log_2(N_{\mathrm{inter}}+1)-\log_2(N_{\mathrm{intra}}+1),
$$

而不是论文写的原始比值（`external_code/ecDNAcaller/_process.py:74-107`）。这意味着论文公式、已拟合系数和重新训练的数据定义不能随意互换。

#### 6.3 Logistic caller

论文用 COLO320DM 的 ecMYC 和 GBM39 的 ecEGFR 为正例，以 COLO320HSR 和 GBM39-ER 的相同区域为负例。模型形式为：

$$
\eta_i=\beta_0+\beta_1\mathrm{CN}_i+\beta_2\mathrm{ratio}_i+\beta_3\mathrm{Gini}_i,
$$

$$
p_i=\frac{1}{1+e^{-\eta_i}}.
$$

推理代码与上式一致（`_process.py:99-109`），但 `glm` 拟合过程没有包含在源码中。

#### 6.4 CNN caller

每个细胞先形成 1-Mb 分辨率的 $3044\times3044$ 矩阵。对中心 bin 取 $5\times3044$ 邻域，模型并联使用：

- 局部 $5\times5$ 接触块；
- 两层卷积提取的空间模式；
- 五行的 L1-normalized row mean；
- 中心 bin 跨染色体接触的 Gini。

拼接维数为

$$
25+192+5+1=223.
$$

源码将 223 维输入映射到 64 维隐藏层，再输出 none/ecDNA/HSR 三类 softmax（`ecDNAcaller_deep.py:175-234`）。论文把 223 描述为 hidden size，源码说明它实际上是拼接输入宽度。

论文报告 40 epochs、batch size 32、AdamW、$\beta=0.99$ hard bootstrapped cross-entropy，但当前仓库只包含预训练权重和推理代码，**没有找到训练循环、loss 或 optimizer 实现**（`paper.md:432-435`）。

### 7. Paired Hi-C 如何连接结构与表达

Paired Hi-C 的 RNA 侧由 Cell Ranger 处理，Hi-C 侧沿用 Droplet Hi-C。两种模态配对后，Seurat/CCA 用共同的 2,000 个变异基因整合参考数据（`paper.md:465-471`）。

在 GBM 中，作者为四种细胞状态计算相对基因集分数：

$$
\mathrm{SC}_{j(i)}=
\frac{\sum_g\mathrm{Exp}_{g(i)}}{N_j}
-
\frac{\sum_g\mathrm{Exp}^{\mathrm{cont}}_{g(i)}}{N_{j\mathrm{cont}}}.
$$

然后比较 OPC/NPC 与 AC/MES 两组最大分数，并用 15 个最近 RNA 邻居把状态分数转移到只有 Hi-C 的细胞（`paper.md:456-462`）。

这一设计让作者看到：ecMYC 某些区域的 copy number 与表达高度相关，另一些区域即使拷贝数较低仍保持高表达；说明 ecDNA 的表达效应不只是“拷贝越多、RNA 越多”。

### 8. 关键实验结果

- **通量与质量：** 三种人细胞系混合实验获得 3,709 个高质量细胞，每细胞中位数 108,439 对 unique contacts；小鼠皮层获得 6,235 个细胞，每细胞中位数 175,021 对（`paper.md:53,59`）。
- **皮层细胞类型：** 20 个群体的 compartment、domain、loop 和 multi-way hub 与对应调控特征一致（Figures 1–2）。
- **ecDNA/HSR：** CNN 在论文报告的 MYC 任务上达到 sensitivity 0.80、specificity 0.99、accuracy 0.93、precision 0.99（`paper.md:111`）。
- **药物演化：** 9,204 个 GBM39/GBM39-ER 细胞显示 erlotinib 后 ecEGFR 消失、ecMDM2 出现、ecMYC 结构更异质，并由 FISH 验证（Figure 4）。
- **原发肿瘤：** 在 GBM 患者样本中分离恶性/非恶性细胞，并同时观察 chr7 扩增、chr10 缺失、ecEGFR、SV 和细胞状态差异（Figure 5）。
- **Paired Hi-C：** 小鼠皮层获得 12,361 个 joint profiles，中位数 42,210 个 Hi-C read pairs、3,914 个 RNA UMI 和 1,746 个基因（`paper.md:189`）。

### 9. 如何正确理解这些结论

1. **这首先是一项平台技术。** 最大贡献不是某一个单独算法，而是把高通量实验、结构分析、肿瘤变异和多组学连接起来。
2. **单细胞 Hi-C 的稀疏性没有消失。** 正常组织依赖插补和细胞类型聚合；Paired Hi-C 的 Hi-C complexity 还低于 Droplet Hi-C（`paper.md:213-219`）。
3. **ecDNA caller 的价值来自空间信息。** 它不是只看 copy number，而是利用 ecDNA 与 HSR 的 trans-contact 分布差异。
4. **训练集规模与泛化仍是限制。** 经典细胞系既用于建立模型，也用于核心性能展示；需要更多独立肿瘤验证。
5. **治疗前后变化不是 lineage tracing。** 数据支持克隆构成和 ecDNA 结构发生变化，但不能独自证明每个新结构是新生成还是稀有克隆被选择。

### 10. 代码复现状态

整体 code–paper fidelity 为 **medium**，复现评分 **3/5**。

已经找到并核验：

- barcode-aware FASTQ-to-pairs/cooler 预处理；
- scHiCluster 插补、gene-score、domain 和 loop wrappers；
- 细胞过滤、UMAP/Leiden 和 scGAD/RNA integration notebooks；
- NeoLoopFinder/EagleC CNV/SV wrapper；
- logistic 与 CNN ecDNA 推理；
- Multiway.hub 的多路接触提取和 hub calling。

主要缺口：

- 大量实验室绝对路径，缺少冻结环境和顶层 runner；
- notebook 依赖未打包的中间对象，没有验证完整执行顺序；
- CNN 训练代码缺失；
- 未建立 ecDNA boundary refinement 和显著 trans-interaction 检验的直接实现；
- Multiway.hub 的示例/输入和部分注释资产不完整；
- pair QC、EagleC resolution 和 logistic ratio 存在源码问题或论文差异。

因此，这个发布版本足以学习方法、核对核心实现并重建部分流程，但不等于可直接一键复现整篇论文。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Droplet Hi-C

**Paper:** *Droplet Hi-C enables scalable, single-cell profiling of chromatin architecture in heterogeneous tissues*
**Journal/year:** *Nature Biotechnology*, 2025
**DOI:** `10.1038/s41587-024-02447-1`

### Problem

Chromatin conformation is difficult to measure in heterogeneous tissues at both high throughput and useful per-cell coverage. Bulk Hi-C averages across cell types and tumor clones. Early microwell methods—including single-cell Hi-C (*Nature*, 2013/2017), single-nucleus Hi-C (*Nature*, 2017) and Dip-C (*Science*, 2018)—provide single-cell structure but are limited in scale, time and cost. Combinatorial-indexing sci-Hi-C (*Nature Methods*, 2017) scales to more cells but has sparse coverage and a lengthy manual workflow; multimodal methods such as HiRES (*Science*, 2023) and GAGE-seq (*Nature Genetics*, 2024) add RNA but remain experimentally complex (`paper.md:21-30,528-538`).

Tumors add a second challenge: CNVs, SVs and ecDNA vary across clones and treatment. Bulk sequencing and aggregate Hi-C can detect amplification but often cannot distinguish circular ecDNA from chromosomal homogeneously staining regions (HSRs) or resolve their cell-to-cell evolution (`paper.md:27,85-111`).

### What the paper introduces

**Droplet Hi-C** couples in situ Hi-C chemistry to the commercial 10x Genomics single-cell ATAC droplet platform. Cross-linked nuclei are restriction-digested and ligated in situ, then Tn5-fragmented and cell-barcoded in droplets. The authors report an approximately 10-hour workflow, eight samples in parallel and at least 40,000 cells per batch (`paper.md:36-47`; Figure 1).

The paper also introduces:

- a normal-tissue analysis stack for imputation, cell annotation, compartments, domains, loops and multi-way chromatin hubs;
- logistic and convolutional-neural-network ecDNA callers that use single-cell contact architecture to distinguish ecDNA from HSR;
- **Paired Hi-C**, a Multiome-compatible extension that jointly measures Hi-C and RNA in the same nucleus.

### Method at a glance

```text
fixed cells/nuclei
  → in situ digestion + ligation
  → 10x droplet tagmentation/barcoding
  → sequencing
  → barcode recovery + BWA-MEM + Pairtools + Cooler
  → per-cell contacts and QC
  ├── normal tissue: scHiCluster imputation → scGAD/RNA integration
  │                  → compartments, domains, loops, multi-way hubs
  ├── cancer: observed contacts → CNV/SV → ecDNA/HSR caller
  └── Paired Hi-C: matched RNA + Hi-C → structure–expression analysis
```

For mouse cortex, scGAD counts gene-body contacts and co-embeds them with reference snRNA-seq for cell labeling. Compartments are called at 100 kb, domains at 25 kb, loops at 10 kb and multi-way hubs from molecules contacting at least three 10-kb bins (`paper.md:315-381`). Cancer matrices are not imputed; CNVs are inferred with NeoLoopFinder and SVs with EagleC (`paper.md:384-393`).

The ecDNA caller uses copy number, a chromosome-wise Gini “hub index” and trans-to-cis contact tendency. The CNN consumes a 5 × 3,044 neighborhood around each 1-Mb bin, combines local contacts, convolutional features, row summaries and Gini, and predicts none/ecDNA/HSR (`paper.md:396-441`).

### Evaluation and main findings

#### Assay performance and cortex

- A human–mouse mixture yielded 5,262 single-species high-quality cells plus 284 potential doublets after shallow sequencing. A three-human-cell-line mixture produced 3,709 high-quality cells with a median 108,439 unique pairs per cell and separated HeLa S3, GM12878, K562 and mitotic populations (`paper.md:53`; Extended Data Figure 1).
- Adult mouse cortex yielded 6,235 high-quality profiles with a median 175,021 unique pairs per cell. Distance decay, compartments and TAD boundaries agreed with Dip-C and sn-m3C-seq references (`paper.md:59`; Extended Data Figure 2).
- scGAD/RNA integration resolved 20 cortical groups: 5 non-neuronal, 9 glutamatergic and 6 GABAergic. Aggregated profiles revealed cell-type-specific compartments, boundaries, loops and multi-way hubs enriched at matched super-enhancers and marker genes (`paper.md:62-82`; Figures 1–2).

#### Cancer structure and ecDNA

- COLO320DM and COLO320HSR both amplify *MYC*, but single-cell contact architecture separates circular ecMYC from chromosomal HSR. The logistic model achieved 0.89 accuracy and 0.71 sensitivity; the CNN achieved 0.93 accuracy, 0.80 sensitivity, 0.99 specificity and 0.99 precision on the reported MYC task (`paper.md:102-111`; Figure 3 and Extended Data Figure 5).
- In 9,204 GBM39/GBM39-ER cells, erlotinib treatment was associated with ecEGFR loss, ecMDM2 emergence and extensive ecMYC structural heterogeneity. FISH provided orthogonal validation (`paper.md:117-137`; Figure 4).
- In a primary GBM sample, Droplet Hi-C separated malignant from nonmalignant cells and recovered chr7 amplification, chr10 deletion, ecEGFR, malignant-specific SVs and chromatin-state differences across GBM cellular states (`paper.md:140-163`; Figure 5).
- In an AML/MDS sample, a roughly 5-Mb ecMYC and associated long-range contacts disappeared after treatment, alongside clinical remission (`paper.md:166`).

#### Paired Hi-C

- Species mixing produced concordant human/mouse assignments in RNA and Hi-C.
- Mouse cortex yielded 12,361 joint profiles with a median 42,210 Hi-C read pairs, 3,914 RNA UMIs and 1,746 genes per cell; 20 cell types were resolved (`paper.md:189-192`; Figure 6 and Extended Data Figure 9).
- Same-cell data linked compartments and ecDNA copy-number structure to gene expression, while also showing that Paired Hi-C has lower Hi-C complexity than Droplet Hi-C (`paper.md:198-219`).

### Strengths

- Uses a widely available commercial microfluidic platform rather than custom microwells or a long combinatorial-indexing protocol.
- Demonstrates utility across cell mixtures, brain tissue, cancer cell lines, patient GBM, AML/MDS and PBMCs.
- Integrates multiple structural scales: compartments, domains, loops, CNVs, SVs, ecDNA and multi-way hubs.
- ecDNA calls are supported by cell-line controls and FISH, not contact maps alone.
- Raw/processed data are deposited at GEO `GSE253407`, and three code repositories are named (`paper.md:495-504`).

### Limitations

- Paired Hi-C has lower contact complexity than Droplet Hi-C, and Droplet Hi-C has fewer cis-long contacts than some biotin-enriched in situ Hi-C methods (`paper.md:213-219`).
- Normal-tissue analyses rely on imputation and external references; cell-type regulatory associations are not causal evidence.
- ecDNA classifier training centers on a small set of canonical loci/cell lines; broader generalization needs independent validation.
- The treatment studies are observational comparisons rather than lineage tracing.
- Several algorithms and intermediate datasets are not packaged into a portable, end-to-end workflow.

### Reproducibility and code–paper match

**Reproducibility rating: 3/5.** Data and substantial source code are public, and the snapshot contains the main preprocessing logic, scHiCluster wrappers, notebook analyses, CNV/SV wrappers, multi-way hub scripts, pretrained ecDNA weights and both inference paths. Overall code–paper fidelity is **medium** (`doc_code.md`).

Main reproducibility gaps:

- laboratory-specific absolute paths and no frozen environment/top-level runner;
- notebooks consume missing intermediate/reference objects and have no verified complete execution order;
- deep ecDNA training/validation code is not present, only pretrained inference;
- ecDNA boundary refinement and significant trans-interaction implementations were not established;
- a duplicate-key bug exists in per-cell QC, and the EagleC wrapper maps its nominal 50-kb input to a 25-kb matrix;
- the logistic code uses a log2 inter/intra count ratio, not the paper's stated raw $N_T/N_C$ ratio.

The release is strong enough for method inspection and partial reconstruction, but a full rerun requires environment rebuilding, external data recovery, path replacement and additional missing training/analysis code.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
