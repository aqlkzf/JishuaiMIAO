---
layout: default
permalink: /paper-atlas/encode4-cb14f9a7/
title: "ENCODE4"
nav: false
description: "ENCODE 4 试图回答的不是一个狭窄的预测问题，而是一个资源构建问题：如何在大量人和小鼠生物学背景中，系统地标注调控元件、基因与转录本，以及它们之间的物理和功能联系？ 单一实验无法同时回答这些问题。例如： DNase-seq/ATAC-seq 能提示染色质开放位置，但不能单独证明该序列会调控某个基因； ChIP-seq 和组蛋白修饰能提供蛋白占据与染色质状态，但相同标记组合未必产生相同的表达效应；"
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
      <span>Atlases &amp; Resources</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>ENCODE4</h1>
    <p>The Encyclopedia of DNA Elements</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ENCODE 4 方法详解：从多组学实验到可查询的基因调控百科全书

### 1. 这篇论文到底在解决什么问题？

ENCODE 4 试图回答的不是一个狭窄的预测问题，而是一个资源构建问题：**如何在大量人和小鼠生物学背景中，系统地标注调控元件、基因与转录本，以及它们之间的物理和功能联系？**

单一实验无法同时回答这些问题。例如：

- DNase-seq/ATAC-seq 能提示染色质开放位置，但不能单独证明该序列会调控某个基因；
- ChIP-seq 和组蛋白修饰能提供蛋白占据与染色质状态，但相同标记组合未必产生相同的表达效应；
- 报告基因实验能测试序列的潜在活性，却脱离了部分内源染色质约束；
- CRISPR 扰动更接近内源功能，但覆盖范围有限；
- Hi-C 能测物理接触，但接触不自动等于调控因果关系。

因此，ENCODE 4 把超过 16,000 个全基因组实验、超过 5,000 个生物样本组织成三个互相连接的层次：**调控元件、基因/转录本、元件—基因相互作用**，并加入小鼠发育和跨物种比较（`paper.md:12`, `paper.md:24-35`）。

> 重要定位：这是一篇旗舰资源/图谱论文，不是一篇完整定义单一算法的论文。下面的“方法”是多个实验—计算模块的集成框架。

### 2. 相比既有工作，ENCODE 4 补了什么缺口？

ENCODE 的演进本身说明了覆盖缺口：

- 试点阶段只研究人类基因组的 1%，发表于 *Nature* 2007；
- 第二阶段扩展到全基因组，发表于 *Nature* 2012；
- 第三阶段进一步增加人和小鼠原代细胞/组织及 cCRE 图谱，发表于 *Nature* 2020（`paper.md:21`, `paper.md:985-990`）。

ENCODE 4 继续补足四类不足：

1. **生物背景不够广。** 人类染色质开放图谱扩展至 4,159 个细胞、组织或状态，约为前次报告的 5.5 倍（`paper.md:47-50`）。
2. **同一细胞类型采样不够深。** 单个样本只能观察到约一半的该细胞类型核心 DHS；通常需要 20 个以上独立样本才可较好识别核心集合（`paper.md:67-70`）。
3. **分辨率不足。** 深度 intact Hi-C 在特定背景中把长程相互作用端点解析到 10 bp 量级，而以往接触图通常无法稳定达到元件或 motif 级别（`paper.md:207-216`；`images/figure_07.jpg`）。
4. **功能证据和预测仍分散。** ENCODE 4 将序列模型、motif 解释、变异效应、CRISPR、物理接触和增强子—基因预测放入同一资源体系，但仍保留不同证据类型的边界。

小鼠部分仍未“完成”：论文估计 2.6 million DHS 的小鼠索引约为 61% 完整（`paper.md:257-260`）。

### 3. 总体输入—计算—输出框架

```text
人/小鼠组织、原代细胞、细胞系、发育过程和扰动样本
                         |
                         v
                 标准化全基因组实验
  可及性 | 组蛋白状态 | TF/RBP 占据 | RNA | 报告基因/CRISPR | Hi-C
                         |
                         v
                 实验级原始与处理数据
      reads | signal profiles | peaks | expression | transcripts | contacts
                         |
                         v
               各模块的计算分析与质量控制
  DHS/cCRE | 序列模型/motif | 变异效应 | 转录本/稳定性 | loops/rE2G
                         |
                         v
                跨实验、跨细胞、跨物种整合
                         |
                         v
       ENCODE Portal + genome tracks + SCREEN/Factorbook/各类查看器
```

论文说明，每个实验都有唯一 accession；样本制备、实验与分析协议、质量控制、原始测序数据、表达量/peak/browser track 等初级处理结果应从 accession 获取（`paper.md:342-345`）。因此，旗舰论文给出的是资源结构和主要结论，真正复现必须回到具体 accession 和配套论文。

### 4. 模块一：构建人类调控元件参考索引

#### 4.1 从样本级 peak 到 DHS 共识索引

**输入：** 4,159 个 DNase I 样本，并在部分样本中加入 bulk 或 single-cell ATAC-seq（`paper.md:47-50`）。

**论文给出的计算流程：**

1. 在每个样本中识别开放染色质 peak；
2. 合并约 705 million 个样本级 peak；
3. 得到 5.33 million 个共识区域；
4. 用 non-negative matrix factorization（NMF）描述每个 DHS 的细胞选择性活动模式，形成 activity barcode；
5. 随着新样本加入，绘制新 DHS 发现曲线并评估饱和度；
6. 对深度采样的细胞类型区分“核心”与偶发 DHS（`paper.md:53-70`; `images/figure_02.jpg`）。

**输出：** 位于人类基因组唯一可比对区域中的约 5.3 million 个高置信 DHS（`paper.md:53`）。论文还估计，未来一次新的开放染色质实验平均只会增加约 50 个新元件（`paper.md:61`）。

**没有给出的关键细节：** peak caller、共识区域合并阈值、NMF 的秩、目标函数、求解器与初始化均 **Not found**。这些不能从图 2 反推。

#### 4.2 给 DHS 增加状态、占据和转录证据

ENCODE 4 在 DHS 骨架上叠加多类证据：

- 六种组蛋白修饰：H3K27ac、H3K4me1、H3K4me3、H3K36me3、H3K27me3、H3K9me3；
- CTCF 与 TF ChIP-seq；
- PRO-seq、PRO-cap 和 BruUV-seq 检测新生转录；
- ChromHMM 与 Segway 半监督隐马尔可夫模型进行染色质状态注释（`paper.md:73-97`）。

TF 覆盖从约 500 个蛋白增加到 1,100 个。对缺少合适抗体的 TF，项目把 epitope tag 引入内源编码序列，再进行 ChIP-seq；但大规模实验主要集中在 HepG2 和 K562（`paper.md:82-88`）。这意味着 TF 图谱很大，但细胞背景并不均匀。

#### 4.3 cCRE 分类：候选不等于已证明功能

ENCODE 把包含 DHS 的 DNA 片段按以下信息规则化分为七种调控状态：

- 与 transcription start site 的距离；
- 组蛋白修饰模式；
- TF 占据；
- ENCODE 4 更新标准中加入的新生转录信息。

最终约 2.4 million 个元件、1,679 个样本被纳入 cCRE 分类（`paper.md:100-103`）。

这里要严格区分三种概念：

- **cCRE：** 根据多种观测规则得到的候选注释；
- **reporter activity：** 序列在报告系统中驱动转录的潜力；
- **CRISPR perturbation effect：** 元件在内源染色质和目标基因背景中的功能影响。

论文发现 reporter assay 更“宽松”；CRISPRi 显著区域几乎都同时具备开放染色质、TF binding 和 reporter activity。作者据此解释：报告基因主要测序列潜能，而 CRISPR 还受到染色质开放以及能否接触目标启动子的约束（`paper.md:106-112`）。

七类的完整名称、阈值和优先规则在本旗舰文本中 **Not found**。

### 5. 模块二：从 DNA 序列预测实验信号，再解释 motif

#### 5.1 模型的输入和输出

针对每一种 assay × tissue/cell context，论文分别训练卷积神经网络，并采用 five-fold cross-validation（`paper.md:115-121`）：

| 模型 | 对应数据 |
|---|---|
| BPNet | TF ChIP-seq |
| ChromBPNet | DNase-seq / ATAC-seq |
| ReporterNet | reporter assay |
| ProCapNet | PRO-cap |

**输入：** 局部 DNA 序列。
**输出：** 总信号 count 和碱基分辨率的 profile shape，同时显式建模 assay-specific bias（`paper.md:121`; `images/figure_03.jpg`）。

模型规模包括 2,339 个 TF ChIP-seq、1,143 个 DNase-seq、369 个 ATAC-seq、6 个 PRO-cap 和 8 个高通量 reporter 实验（`paper.md:118`）。

#### 5.2 可解释性流水线

```text
DNA sequence
   |
   v
实验/细胞背景特异的 profile CNN + bias correction
   |
   +--> predicted count + base-resolution profile
   |
   v
DeepLIFT：每个碱基的 contribution score
   |
   v
TF-MoDISco：聚类高贡献子序列，得到 CWM motif
   |
   v
FiNeMo：用 CWM 库竞争扫描 contribution map
   |
   v
motif instances
   |
   v
MotifCompendium：跨模型合并为统一 motif 索引
```

每个实验输出三类可查看轨道：bias-corrected prediction、nucleotide-resolution contribution、以及 motif 相关结果（`paper.md:121-126`）。超过 280,000 个模型 motif 被压缩为 3,384 个非冗余 motif（`paper.md:129-132`）。图 3 还显示，在其比较标准下，外部数据库 17,867 个 motif 中有 16,835 个可匹配到 ENCODE catalog（`images/figure_03.jpg`）。

#### 5.3 哪些训练细节不能从本文得到？

以下均 **Not found**：

- count loss 与 profile loss 的具体形式和权重；
- CNN 的层数、卷积核、激活和参数量；
- optimizer、learning rate、batch size、epoch、early stopping；
- sequence window、负样本、signal transformation；
- DeepLIFT background、TF-MoDISco 聚类参数、FiNeMo 调用阈值。

因此不能把上面的流程图当成可执行训练配方。本地也没有代码快照。

### 6. 模块三：非编码变异效应与 cV2F

#### 6.1 多来源变异证据

ENCODE 使用两类直接证据：

1. 在供体杂合位点测量 allele-specific assay signal；
2. 用合成 reporter assay 测大量选定变异。

论文报告实验测试约 1.5 million 个常见和低频变异，其中 149,679 个在 FDR < 0.05 时具有显著 allele effect；eQTL 与深度学习又把预测扩展到约 10 million 个变异（`paper.md:138-144`）。

图 4 可见五类来源：MPRA、STARR-seq、DNase-seq、fine-mapped eQTL 和 deep learning，并比较 ChromBPNet hits 与 MPRA/DNase allele imbalance 的富集（`images/figure_04.jpg`）。

#### 6.2 cV2F 的概念表达

图 4c 给出的示意关系是：

$$
y \sim f(x^{c}, x^{e}, x^{b})
$$

其中：

- $y$：GWAS fine-mapping posterior inclusion probabilities；
- $x^{c}$：variant-to-function features；
- $x^{e}$：element-to-function features；
- $x^{b}$：baseline LD 和 conservation features；
- $f(\cdot)$：学习这些特征组合并产生 0–1 cV2F score 的映射。

这是从图中转写的**概念符号**，不是正文给出的正式目标函数（`paper.md:147-152`; `images/figure_04.jpg`）。

#### 6.3 评估

论文报告：

- held-out UK Biobank fine-mapped associations 上 AUPRC = 0.82；
- 加入 ENCODE 4 数据后，在 UK Biobank、MVP European ancestry、MVP African ancestry 上分别提高 14%、28%、14%；
- tissue-matched cV2F 用于 African-ancestry polygenic prediction 时，相对 non-functional baseline 提高 13%（`paper.md:152`）。

图 4d 将 cV2F 与 baseline LD、pre-ENCODE baseline LD、variant-function-only 和 element-function-only 模型并列比较（`images/figure_04.jpg`）。

模型类型、likelihood/loss、正则化、特征归一化、训练切分和 calibration 均 **Not found**，所以无法仅凭本文复训 cV2F。

### 7. 模块四：基因、转录本结构和 RNA 稳定性

#### 7.1 长读长扩展基因与转录本目录

Capture-long-read sequencing 新增 17,931 个 human lncRNA genes（140,268 transcripts）以及 22,784 个 mouse genes（136,169 transcripts）（`paper.md:161-164`）。超过 400 个 full-length transcriptomes 进一步得到超过 200,000 个 polyA+ transcripts，其中 35% 相比 GENCODE v40 具有新剪接结构（`paper.md:167-170`）。

#### 7.2 用 TSS–EC–TES 三元组拆分异构体差异

每个转录本被表示为：

$$
(TSS,\ EC,\ TES)
$$

- `TSS`：transcript start site 身份；
- `EC`：exon junction chain 身份；
- `TES`：transcript end site 身份。

同一基因的不同转录本可形成 `[1,1,1]`、`[1,2,2]`、`[1,2,3]` 等类别，再放到 simplex 中判断多样性主要来自起始、剪接还是终止位置（`paper.md:173-178`; `images/figure_05.jpg`）。论文报告 44% 的 protein-coding genes 偏向其中某一类变化（`paper.md:178`）。

这是结构编码，不是需要优化的损失函数。转录本组装、collapse、novelty tolerance、TPM 计算和 simplex 坐标公式均 **Not found**。

#### 7.3 两个时间区间的 RNA turnover

Bru-seq/BruChase-seq 在 16 个协调培养的 cell lines 中测量 RNA 降解。图 6 显示：先 Bru labeling 30 分钟，再在 0、2、6 小时采样，从而比较 0–2 h 和 2–6 h 的 scaled stability（`paper.md:181-192`; `images/figure_06.jpg`）。

典型模式包括：

- *KLF6*：两个区间都低稳定；
- *ALKBH5*：两个区间都高稳定；
- *RPL31*：早期低、后期高；
- *SYPL1*：细胞类型差异明显。

稳定性评分公式、动力学模型、归一化和重复样本误差模型均 **Not found**。

### 8. 模块五：物理接触和增强子—基因关系

#### 8.1 intact Hi-C 接触图

ENCODE 对 DNA:DNA proximity-ligation libraries 进行深度测序，并使用 intact Hi-C 构建 100 种人类细胞/组织的接触图（`paper.md:207-213`）。在深度图中，论文报告：

- 长程相互作用端点可达 10 bp；
- 可检测大多数短于 250 kb 的 loops；
- combined LCL map 含约 1 million point-to-point loops，连接 138,049 个 anchors（`paper.md:213`）。

图 7 从整条染色体逐级放大到 10-bp bin，并展示 cell line、CTCF sequence、蛋白降解和 tissue-specific loops（`images/figure_07.jpg`）。

alignment、contact normalization、loop caller、阈值、phasing 和 replicate merging 均 **Not found**。

#### 8.2 物理联系不直接等于功能联系

作者把 Hi-C loops 与 CRISPR 扰动得到的 element-to-gene links 比较：

- 一个 K562 tiling CRISPRi 实验中，最多 92% 的调控扰动对应物理 loop；
- 一个 HCT-116 实验中，30/30 个映射到的调控联系对应物理 loop，而未显示调控作用的位点对只有 30% 存在物理接触（`paper.md:233-236`）。

这些结果支持物理联系的重要性，但不意味着“看到 loop 就已证明功能”。

#### 8.3 ENCODE-rE2G

**训练数据：** 10,356 个 element–gene pairs，其中 471 个为 CRISPR 实验验证的调控连接。
**模型：** 一系列 supervised classifiers。
**输入概念：** 图 7f 显示 CRISPR、DNase-seq 和 intact Hi-C。
**输出：** cell-type-specific enhancer–gene maps（`paper.md:239-242`; `images/figure_07.jpg`）。

论文报告：75% 的预测联系距目标启动子 100 kb 以内，平均每个基因 5.9 个联系、每个 distal element 1.6 个联系；在没有物理接触数据时，利用 1,458 个 DNase-seq 实验扩展到超过 92 million 个预测（`paper.md:242`）。

分类器类型、负样本构造、特征定义、loss、split、calibration 和 cutoff 均 **Not found**。

### 9. 模块六：小鼠发育与跨物种功能保守性

#### 9.1 小鼠出生后图谱

ENCODE 以 C57BL6/J × CAST/EiJ F1 小鼠进行 allele-specific 和 parent-of-origin 分析，跨组织和年龄采集 RNA、chromatin accessibility、ChIP 和 Hi-C 等数据（`paper.md:263-266`）。

图 8 最重要的视觉信息不是“每个格子都有实验”，而是一个**稀疏的 assay × tissue × age 覆盖矩阵**。短读长 RNA-seq 和 DNase-seq 覆盖较广，其余实验只覆盖子集（`images/figure_08.jpg`）。图中 28,251 个基因被分成 prenatal-only 4,972、两阶段均检测 20,957、postnatal-only 2,322（`paper.md:269-274`）。

注意：正文概括七个主要时间点，而图中还可见一个中间成年年龄类别。精确到 assay 的时间安排应查 accession，不能强行把二者合并。

#### 9.2 功能保守性不是只看序列

ENCODE 构造两类 human–mouse 元件对：

- 按 sequence homology：2.2 million pairs；
- 按 orthologous genes 周围区域：约 180 million pairs。

然后把 human/mouse DNase-seq、ATAC-seq 和 histone ChIP-seq 样本共嵌入共享低维空间，进行 in silico sample matching，再比较元件对在匹配背景中的活动模式（`paper.md:280-286`; `images/figure_09.jpg`）。

```text
sequence-matched / gene-homology element pairs
                     |
                     v
  matched human/mouse assay contexts in shared space
                     |
                     v
        compare regulatory activity patterns
                     |
                     v
 functional-conservation calls / annotation transfer
                     |
                     v
 loop prioritization + noncoding-variant interpretation
```

论文报告 core set 有 300,000 对达到 FDR ≤ 10%，extended set 有 3.1 million 对达到 FDR ≤ 25%（`paper.md:283`）。共嵌入算法、latent dimension、相似度统计量、null model 和具体多重检验流程均 **Not found**。

### 10. 如何评价这个资源？

ENCODE 4 没有一个统一 benchmark，因为各模块任务不同。代表性证据包括：

| 模块 | 评价方式 | 论文报告 |
|---|---|---|
| DHS index | 发现曲线和 >20,000 个外部 accessibility datasets | 几乎全部外部元件被索引覆盖；新实验平均约增加 50 个元件（`paper.md:61`） |
| motif catalog | JASPAR/HOCOMOCO/CIS-BP 合并集 | 图中 16,835/17,867 个外部 motif 可匹配（`images/figure_03.jpg`） |
| variant prediction | ChromBPNet vs MPRA/DNase allele evidence | 分别报告 13-fold 和 10-fold enrichment（`paper.md:144`） |
| cV2F | held-out UKBB/MVP fine-mapping；AUPRC | UKBB AUPRC 0.82；加入 ENCODE 4 后各队列提高 14%/28%/14%（`paper.md:152`） |
| physical vs regulatory | Hi-C vs CRISPR links | K562 最多 92%；HCT-116 示例为 30/30（`paper.md:233-236`） |
| conservation | activity matching + FDR | core 300,000 对（≤10%）；extended 3.1 million 对（≤25%）（`paper.md:283`） |

这些结果表明资源具有覆盖度、跨证据一致性和应用价值，但不能解读成所有组织、assay 或模型都具有同样精度。

### 11. 复现性与证据边界

#### 当前 workspace 可以做到

- 理解三层资源设计和各模块输入/输出；
- 核对论文报告的规模、主要指标和主图证据；
- 理解 CNN → contribution → motif、cV2F 特征整合、TSS–EC–TES、Hi-C → rE2G、跨物种 matching 等概念流水线。

#### 当前 workspace 做不到

1. **SUPP_MD：MISSING。** 论文引用的 supplementary figures/tables 无法在本地直接核验。
2. **code source：MISSING。** `MODE=paper-only`, `HAS_CODE=false`；没有代码行为可以验证，也不应创建 `doc_code.md`。
3. **实验级方法：Not found locally。** 旗舰 Methods 明确把样本制备、协议、QC、原始和处理数据交给 portal accession 与 companion papers（`paper.md:342-345`）。
4. **正式目标函数和优化：Not found。** `paper.md:1-1109` 未发现方法优先的正式 displayed objective；本文中的 cV2F 与转录本三元组公式只是图示/表示法。
5. **关键实现参数：Not found。** 包括 peak/loop/transcript calling、模型架构和超参数、稳定性评分、保守性共嵌入与统计检验。

### 12. 研究者应该怎样真正复现？

1. 先确定目标模块和精确 ENCODE accession/series；
2. 下载对应样本元数据、实验协议、QC、raw reads 和 released processed tracks；
3. 阅读该模块引用的 companion paper；
4. 固定 genome build、biosample ontology、pipeline/version、对照和 accession 版本；
5. 先复核 released peaks/tracks/catalog，再进行跨 assay 集成；
6. 将本文件作为模块导航图，而不是可执行 protocol。

### 结论

ENCODE 4 的创新不在一个“万能模型”，而在把开放染色质、染色质状态、TF/RNA、功能扰动、序列模型、变异效应、长读长转录本、RNA turnover、3D contact 和跨物种证据连接成可访问的调控百科全书。它非常适合回答“某个元件在什么背景下有什么证据、可能联系哪个基因、是否跨物种保守”这类问题；但若要逐实验或逐模型复现，必须继续进入 ENCODE Portal accession 和配套论文，因为旗舰文本本身没有提供完整目标函数、优化与实现细节。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ENCODE 4 — Summary

### What problem does the paper address?

ENCODE 4 asks how to build a usable reference map of genome regulation across human and mouse biology. A single assay cannot jointly identify regulatory DNA, transcript structures and lifetimes, and the physical or functional links between elements and genes. The consortium therefore integrates more than 16,000 genome-wide experiments across more than 5,000 biological samples into three connected layers: **regulatory elements**, **genes and transcripts**, and **interactions among them** (`paper.md:12`, `paper.md:24-35`).

This is an atlas/resource paper, not one fully specified algorithm. Its key contribution is the coordinated scale and integration of many experimental and computational modules.

### What was limited before ENCODE 4?

Earlier ENCODE phases progressed from 1% of the human genome (pilot phase, *Nature*, 2007), to genome-wide human studies (*Nature*, 2012), and then broader primary human/mouse tissues and cCRE annotations (*Nature*, 2020) (`paper.md:21`, `paper.md:985-990`). ENCODE 4 targets remaining coverage and resolution gaps:

- the human accessibility map expands to 4,159 samples, about 5.5-fold over the previous report (`paper.md:47-50`);
- TF occupancy expands from about 500 proteins to 1,100, although difficult antibody targets required endogenous epitope tagging and were concentrated in HepG2 and K562 (`paper.md:82-88`);
- mouse DHS sampling expands about 15-fold over MouseENCODE, yet the resulting mouse index is still estimated to be only about 61% complete (`paper.md:257-260`);
- earlier contact maps lacked the depth to routinely resolve individual elements or motifs, whereas the reported high-density intact Hi-C maps reach endpoints within 10 bp in selected contexts (`paper.md:207-216`).

The paper also emphasizes a conceptual limitation: biochemical annotations alone do not uniquely determine regulatory effect. Reporter assays and endogenous CRISPR perturbations test different constraints, and physical contact does not automatically equal regulation (`paper.md:100-112`, `paper.md:233-236`).

### What does ENCODE 4 contribute?

#### 1. Regulatory-element reference and functional evidence

ENCODE combines approximately 705 million DNase peaks from 4,159 samples into a 5.33-million-region DHS index, then models cell-selective activity patterns and evaluates saturation (`paper.md:50-61`; visually confirmed in `images/figure_02.jpg`). Histone marks, CTCF and TF occupancy, and nascent transcription add regulatory-state evidence; a rule-based cCRE system categorizes about 2.4 million elements from 1,679 samples (`paper.md:73-103`). Reporter and CRISPR assays provide functional evidence while preserving the distinction between sequence potential and endogenous context (`paper.md:106-112`).

#### 2. Sequence models and motif interpretation

Per-experiment convolutional models predict total signal and base-resolution profile shape from local DNA sequence for TF binding, accessibility, nascent transcription, and reporter activity. The stated workflow is:

```text
DNA -> assay/context-specific profile model
    -> base-wise contribution scores (DeepLIFT)
    -> de novo CWM motifs (TF-MoDISco)
    -> motif instances (FiNeMo)
    -> cross-model motif catalog
```

The project consolidates more than 280,000 model-derived motifs into 3,384 motifs (`paper.md:115-135`; visually confirmed in `images/figure_03.jpg`).

#### 3. Variant-effect integration

Experimental assays test about 1.5 million common and low-frequency variants, with 149,679 significant allelic effects at FDR < 0.05; eQTL and deep-learning analyses extend predictions to about 10 million variants (`paper.md:138-144`). The cV2F framework combines variant-level evidence, element-level evidence, baseline linkage disequilibrium, and conservation into consensus variant scores (`paper.md:147-152`; `images/figure_04.jpg`).

#### 4. Genes, isoforms, and RNA turnover

Capture-long-read sequencing adds 17,931 novel human lncRNA genes and 140,268 associated transcripts. More than 400 long-read transcriptomes support over 200,000 polyA+ transcripts, 35% with novel splicing relative to GENCODE v40 (`paper.md:161-170`). A TSS–exon-chain–TES triplet decomposes isoform diversity, while Bru-seq/BruChase-seq maps early and late RNA stability across 16 coordinated cell lines (`paper.md:173-192`; `images/figure_05.jpg`, `images/figure_06.jpg`).

#### 5. Physical and predicted enhancer–gene links

Intact Hi-C produces high-resolution maps across 100 human cell/tissue types, including deeply sequenced reference cell lines and lymphoblastoid donors (`paper.md:207-218`). Perturbation comparisons test which loops depend on specific proteins and how physical loops correspond to CRISPR-derived regulatory links (`paper.md:221-236`). ENCODE-rE2G trains supervised classifiers on 10,356 element–gene pairs, including 471 experimentally verified links, and extends prediction to more than 92 million interactions using 1,458 DNase-seq experiments where physical maps are unavailable (`paper.md:239-242`).

#### 6. Mouse development and cross-species conservation

The mouse arm builds a 2.6-million-DHS index and profiles postnatal tissues over time (`paper.md:257-274`). Functional conservation is assessed not only through sequence homology but also by comparing matched human/mouse accessibility and histone activity patterns for 2.2 million sequence-matched and roughly 180 million gene-homology-based element pairs (`paper.md:277-291`; `images/figure_08.jpg`, `images/figure_09.jpg`).

### Evaluation and headline evidence

Because ENCODE 4 is a collection of modules, there is no single benchmark or metric. Representative evaluations include:

| Module | Comparison / metric | Reported result |
|---|---|---|
| DHS completeness | discovery curve plus >20,000 non-ENCODE accessibility datasets | nearly all external elements overlap the index; a future experiment is estimated to add about 50 elements on average (`paper.md:61`) |
| Sequence motifs | combined JASPAR/HOCOMOCO/CIS-BP collection | Figure 3 shows 16,835 of 17,867 external motifs matched to the ENCODE catalog under the displayed comparison (`paper.md:121`; `images/figure_03.jpg`) |
| Variant prediction | ChromBPNet hits vs MPRA and DNase allelic imbalance | reported 13-fold and 10-fold enrichment, respectively (`paper.md:144`) |
| cV2F | held-out UK Biobank and MVP fine-mapped associations; AUPRC | reported UK Biobank AUPRC 0.82 and improvements of 14%, 28%, and 14% after adding ENCODE 4 data across the stated cohorts (`paper.md:152`) |
| Physical versus regulatory links | Hi-C loops vs CRISPR tiling interactions | up to 92% correspondence in K562; 30/30 mapped regulatory links correspond to loops in one HCT-116 study (`paper.md:233-236`) |
| Cross-species conservation | activity-pattern testing with FDR control | 300,000 core pairs at FDR ≤ 10% and 3.1 million extended pairs at FDR ≤ 25% (`paper.md:283`) |

These results support breadth, internal concordance, and utility. They do not establish uniform accuracy for every assay, tissue, model, or catalog entry.

### Strengths

- **Coordinated breadth:** diverse assays, biosamples, perturbations, developmental stages, and species are connected through common resource surfaces (`paper.md:24-35`).
- **Multiple evidence types:** candidate annotations, model predictions, physical contacts, reporter assays, and endogenous perturbations are not collapsed into one undifferentiated label.
- **Resolution and scale:** selected intact Hi-C maps reach individual-element or motif-scale resolution, and long-read/RNA-turnover work expands beyond conventional steady-state short-read measurements.
- **Public access:** experimental results, processed outputs, predictions, viewers, track hubs, and MCP servers are exposed through the ENCODE portal and specialized interfaces (`paper.md:306-318`).

### Limitations and reproducibility

**Interpretive limitation.** This flagship paper is a high-level synthesis. Similar assay annotations can have different effects on target expression, the mouse DHS index remains incomplete, and high-resolution physical maps are saturated only in a few deeply studied contexts (`paper.md:327-336`).

**Workspace reproducibility assessment: low for exact reruns, strong for conceptual navigation.**

- Detailed protocols and primary analyses are delegated to unique ENCODE portal accessions and companion papers; the flagship Methods section says accessions contain sample preparation, protocols, QC, raw data, and processed data (`paper.md:342-345`).
- A separate supplementary Markdown file is **MISSING**, so locally cited supplementary tables and figures cannot be checked.
- A code snapshot is **MISSING** (`MODE=paper-only`, `HAS_CODE=false`); `doc_code.md` is intentionally skipped.
- Formal losses, model architectures, optimizers, hyperparameters, peak/loop/transcript calling rules, stability equations, and conservation-testing implementations are **Not found** in `paper.md:1-1109`.
- Figure 8 visibly includes an intermediate adult age category not enumerated in the prose’s seven-principal-time-point summary; exact assay schedules should be resolved from portal accessions (`paper.md:266-269`; `images/figure_08.jpg`).

Thus, this workspace can reproduce the **conceptual pipeline, reported scales, and main visual/result claims**, but not accession-level experiments or computational models without external source retrieval.

### Bottom line

ENCODE 4 is a capstone regulatory-genomics atlas that connects accessible and chromatin-state annotations, interpretable sequence models, variant effects, long-read transcript structure, RNA turnover, high-resolution 3D contacts, enhancer–gene predictions, and mouse conservation. Its scientific value lies in the linked evidence layers and public resource scale. Its principal reproducibility caveat is equally clear: exact experiment- and model-level reproduction lives in portal accessions and companion papers, not in this flagship manuscript alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
