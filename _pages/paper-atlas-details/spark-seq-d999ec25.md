---
layout: default
permalink: /paper-atlas/spark-seq-d999ec25/
title: "SPARK-seq"
nav: false
description: "SPARK-seq（Science, 2025）把 CRISPR 靶基因、细胞转录组和细胞表面结合的适配体同时读到同一个单细胞条形码下：如果敲除某个膜蛋白后，一组适配体在这些细胞上的结合量系统性下降，这组适配体就可能直接结合该蛋白。配套的 SPARTA 分析把序列聚成家族、比较敲除组与对照组的结合差异、筛选靶标，再用深度学习预测结合序列并生成新变体。"
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
      <span>Data Sources &amp; Technologies</span>
      <span>Science · 2025</span>
    </div>
    <h1>SPARK-seq</h1>
    <p>SPARK-seq: A high-throughput platform for aptamer discovery and kinetic profiling</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1126/science.adv6127" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SPARK-seq：把“适配体结合了谁”变成单细胞可测的扰动信号

### 一句话理解

SPARK-seq（*Science*, 2025）把 CRISPR 靶基因、细胞转录组和细胞表面结合的适配体同时读到同一个单细胞条形码下：如果敲除某个膜蛋白后，一组适配体在这些细胞上的结合量系统性下降，这组适配体就可能直接结合该蛋白。配套的 SPARTA 分析把序列聚成家族、比较敲除组与对照组的结合差异、筛选靶标，再用深度学习预测结合序列并生成新变体。

这里必须区分两个名字：

- **SPARK-seq** 是实验平台：Cell-SELEX、池化 CRISPR 扰动、10X 单细胞多模态捕获和测序。
- **SPARTA** 是计算框架：适配体家族聚类、结合差异与靶标打分，以及 CNN/VAE 模块。

### 为什么传统 Cell-SELEX 还不够？

适配体是通常 20–100 nt 的单链 DNA/RNA，可以在天然细胞膜环境中识别蛋白。Cell-SELEX 能绕过纯化膜蛋白的困难，但筛选后的“靶标是谁”仍是瓶颈。传统 Apt IP-MS 往往需要十轮以上富集，倾向选择高拷贝序列和高丰度、易被质谱检测的蛋白，一次实验通常只确认一两个适配体。PCR 扩增偏差还可能让高丰度序列并不是结合性质最好的序列。

SPARK-seq 的关键转化是：不再先挑一个高丰度适配体去拉下蛋白，而是在混合的基因敲除细胞群中同时测量许多适配体。靶蛋白的缺失成为一个因果方向明确的内部对照。

### 输入、输出与实验规模

#### 输入

1. 经过 4 轮 Cell-SELEX 的 R4 ssDNA 适配体库；每条序列含 46 nt 随机区、5' PCR handle 和 3' 单细胞捕获序列。
2. SUM159PT 细胞的池化 CRISPR 扰动库：46 条 gRNA，覆盖 13 个候选膜蛋白（每蛋白 3 条）和 7 条阴性对照。
3. 同一细胞上的三种读出：mRNA、gRNA 和适配体 UMI。

#### 输出

- 单细胞 × 适配体家族结合矩阵；
- 适配体家族—膜蛋白候选关系；
- 单条适配体在敲除组相对对照组的 $\log_2FC$；
- 用于结合分类和新序列生成的模型与候选变体。

论文最终在一次实验中把 5535 条适配体映射到 8 个直接表面蛋白靶标：PTK7、ITGA3、CDCP1、NRP1、NRP2、PTPRD、PTPRF 和 PTPRS。

### 从细胞到靶标的完整流程

```text
4 轮 Cell-SELEX 的适配体库
             +
13 个膜蛋白的池化 CRISPR 敲除细胞
             |
             v
10X 5' 单细胞捕获：mRNA + gRNA + aptamer UMI
             |
             v
细胞质控与单 gRNA 身份判定
             |
             v
top 10,000 适配体序列 --BLAST-short + MCL--> 1,906 个家族
             |
             v
每个家族在各 gRNA 细胞群相对 NC 的 binding difference
             |
             v
噪声过滤 + 2 成分 GMM 阈值 + 多 gRNA 蛋白打分
             |
             +--> 适配体—蛋白映射与实验验证
             |
             +--> CNN 结合预测 / VAE 变体生成
```

#### 1. 三种信息如何落到同一个细胞？

10X 5' 流程分别用 poly(T)、CRISPR capture primer 和定制适配体 capture sequence 捕获 mRNA、gRNA 和适配体。原始适配体 reads 经四个 Perl 脚本完成接头匹配、细胞 barcode 校正、barcode 提取和 UMI 去重，形成适配体计数矩阵。共同的细胞 barcode 让每个细胞同时具有“敲了什么”和“哪些适配体仍在表面”的信息。

论文先保留 14,275 个高质量细胞，再得到 8466 个 gRNA 身份清楚的单细胞，其中包括 473 个阴性对照细胞。公开 R 代码的质控条件是 aptamer UMI >100、检测基因数 >200、线粒体比例 <10%。

#### 2. 如何确定一个细胞主要携带哪条 gRNA？

代码定义主 gRNA 比例：

$$
r_c=\frac{\max_j n_{cj}}{\sum_j n_{cj}}.
$$

当总 gRNA UMI 至少 200 且 $r_c\ge 0.7$ 时，细胞被分给最高计数的 gRNA；否则标为 negative 或 multiple。随后删除少于 50 个细胞的 gRNA 组，以及只剩一条 gRNA 支持的蛋白。

论文方法描述用三成分 GMM 推导 0.70 阈值，但发布函数 `cell_gRNA_identity()` 直接使用固定的 `min_ratio=0.7`，没有包含拟合过程。这是论文与代码的重要边界。

#### 3. 为什么先把序列聚成“适配体家族”？

测序得到 $4.027\times10^7$ 条不同序列和 $1.72\times10^8$ reads。top 10,000 序列已经覆盖 68.84% reads，扩大到 50,000 或 100,000 只增加不足 1% 覆盖，却显著增加噪声和计算成本。

SPARTA 对 top 10,000 序列做 all-vs-all `blastn-short`，将 BLAST bit score 除以全局最大分数形成加权图，再用 Markov clustering（MCL）得到 1906 个家族。其假设是相似序列更可能共享结构和靶标；它降低单条稀疏序列造成的统计不稳定，但也可能把真正不同的结合模式合并，所以家族预测仍需要单条序列验证。

代码存在一个参数不一致：`smart_cluster.py` 的 inflation 默认值是 1.5，而仓库 README 示例用 0.7。论文没有在主方法中给出足以唯一恢复最终 1906 家族的完整命令，因此复现时必须显式记录该参数。

#### 4. Binding Difference 如何把敲除转成靶标信号？

对适配体家族 $f$，先求阴性对照细胞计数的中位数。每个 gRNA 细胞的差值为：

$$
BD_{f,c}=x_{f,c}-\operatorname{median}_{c'\in NC}(x_{f,c'}),
$$

再对同一 gRNA 组取中位数：

$$
BD_{f,g}=\operatorname{median}_{c\in g}(BD_{f,c}).
$$

若敲除蛋白 $p$ 后家族 $f$ 的结合下降，$BD_{f,g}$ 会更负。代码还过滤两类噪声：对许多家族都造成大幅下降的“混乱 gRNA”，以及在各组几乎没有变化的家族。

代码对 BD 做保留符号的伪 $\log_2$ 变换：绝对值小于 1 的值保持不变，其余变为 $\operatorname{sign}(x)\log_2(|x|+1)$。随后为每个家族拟合二成分高斯混合：

$$
p(BD)=\pi_1\mathcal N(\mu_1,\sigma_1^2)+\pi_2\mathcal N(\mu_2,\sigma_2^2),\quad \mu_1<\mu_2.
$$

下均值成分的 $\mu_1$ 被用作阈值，只保留 $BD\le\mu_1$ 的强下降关系。一个蛋白至少要有两条 gRNA 支持。候选蛋白得分本质上是其支持 gRNA 的负 BD 之和：

$$
Score_{f,p}=\sum_{g\rightarrow p}-BD_{f,g}.
$$

当候选超过一个时，代码再按两倍比值或归一化比例规则保留一个或多个靶标。

#### 5. 为什么 $-\log_2FC$ 能提供动力学线索？

单条适配体的敲除/对照丰度差异为：

$$
\log_2FC=\log_2\frac{\text{KO 细胞中的适配体丰度}}{\text{NC 细胞中的适配体丰度}}.
$$

特异适配体在靶标敲除后减少，因此 $\log_2FC<0$，$-\log_2FC$ 越大表示靶标依赖的保留越强。论文用流式、SPR 和 RT-IC 发现 $-\log_2FC$ 与解离速率 $k_{off}$ 强相关：PTK7 的 SPR 结果 $R^2=0.88$，RT-IC 为 $R^2\approx0.87$；与 $K_D$ 或 $k_{on}$ 的关系较弱或不一致。

这不是直接从测序精确估计 $k_{off}$ 的物理模型，而是实验洗涤过程产生的经验代理：慢解离适配体更能在处理后留在细胞表面。最终排序仍需 SPR/RT-IC 标定。

### 六幅主图如何支撑结论？

#### 图 1：平台设计

展示 Cell-SELEX 库、mRNA/gRNA/aptamer 三路捕获以及通过共同 barcode 联结三种信息。它定义了实验可观测量，但本身不证明靶标识别准确。

#### 图 2：PTK7/sgc8c 单靶标概念验证

在人和鼠细胞中敲除 PTK7 后，sgc8c-S 结合信号下降；单细胞 UMAP 同时区分物种、gRNA 和适配体信号。这证明敲除导致的结合损失可以被 SPARK-seq 捕获。

#### 图 3：从 top 10,000 序列到家族—蛋白图谱

展示 BLAST-MCL 聚类、三层单细胞矩阵、BD/GMM/打分流程和 12 个家族对 9 个扰动蛋白群的关系。PTPR 家族的恢复依赖论文所述 Mixscape 精炼，但该步骤未出现在公开仓库中。

#### 图 4：多靶标实验验证

敲除/对照火山图、流式和 SPR/MST 共同验证 PTK7、CDCP1、NRP1、NRP2、ITGA3/ITGB1 与 PTPR 家族候选。论文最后报告 5535 条适配体对应 8 个直接靶标；ITGB1 被解释为复合体共受体而不是最终直接靶标。

#### 图 5：特异性、旁系同源蛋白与低丰度覆盖

竞争和交叉 SPR 实验支持靶标特异性；NRP1 与 NRP2 可被不同适配体区分。校准流式显示靶标丰度跨越两个数量级，从每细胞超过 $10^5$ 的 ITGA3 到不足 1000 的 PTPRD/PTPRF。

#### 图 6：动力学排序与模型扩展

$-\log_2FC$ 与 $k_{off}$ 的相关性说明 SPARK-seq 偏好慢解离序列。CNN 以 2395 条 PTK7 binder 和 2395 条 nonbinder 训练，在 7 条已知 PTK7 适配体与 24 个无关对照上约 97% 准确。VAE 生成 15 个 PTK7 变体，其中 12 个体外结合，SPARK-Apt-18 的解离最慢。

### SPARTA 的两个深度学习模块

#### FCNA 结合分类器

公开 Python 代码把最长 48 nt 的序列 one-hot 编码，经过两个实际执行的 1D 卷积、池化、全局池化和带 skip connection 的上采样解码，再由线性层输出类别。训练使用交叉熵、Adam、80/20 随机拆分和 100 epochs。`conv3/pool3` 虽在构造函数中定义，却没有在 `forward()` 调用；不能把它们算作实际模型层。

#### Raptgen VAE 生成器

编码器把 46 nt 序列映射到二维潜空间，profile-HMM 解码器建模匹配、插入和删除状态。损失包含重构项和 KL 散度：

$$
\mathcal L=\mathcal L_{recon}-\frac{1}{2N}\sum_i(1+\log\sigma_i^2-\mu_i^2-\sigma_i^2).
$$

发布脚本训练 1000 epochs、batch size 512。它把 `RAPGEN_MODELS_PATH` 和默认 GPU 写成作者机器路径/`cuda:3`，需要人工修改才能在其他环境运行。

### 代码—论文对应与复现边界

| 论文步骤 | 直接代码证据 | 对应状态 |
|---|---|---|
| 单细胞质控 | `code/R/cell_quality.R:19-32` | Exact：三个阈值明确 |
| gRNA 身份与组过滤 | `code/R/cell_gRNA_identity.R:11-42` | Partial：固定 0.7；论文的三成分 GMM 拟合未发布 |
| BLAST-short + MCL | `code/aptamer_family_analysis/smart_cluster.py:19-24,38-102` | Partial：实现明确，但 inflation 默认与 README 示例不一致 |
| BD、噪声过滤、二成分 GMM、蛋白打分 | `code/R/predict_apt_pro.R:14-145` | Exact/Partial：核心计算可追踪，启发式分支比论文正文更复杂 |
| Mixscape 恢复 PTPRS | 本地代码中 `Not found` | MISSING：论文使用，仓库没有实现 |
| FCNA 分类 | `code/aptamer_family_analysis/fcna_trainer.py:42-98,140-249` | Exact：结构和训练循环可追踪 |
| VAE 生成 | `code/aptamer_family_analysis/raptgen_models.py:60-88,221-230`; `ratgen_aptamer.py:20-85` | Partial：模型存在，但有硬编码路径且缺统一依赖环境 |

仓库提供 R 包函数、Python 模型、Perl 原始处理脚本、示例输入/输出和 commit `7bdd8e8`，原始测序数据位于 SRA `PRJNA1202227`。但它没有一键复现实验到全部主图的 workflow，也没有 Mixscape 步骤、完整环境文件和所有上游中间对象。因此，最合理的复现评价是中等：核心计算逻辑公开且可审计，完整端到端结果仍需补步骤和环境整理。

### 应该如何理解论文结论？

最强证据来自三层闭环：靶标敲除造成适配体结合下降；候选再经流式、SPR、MST、竞争和交叉结合验证；动力学测量进一步解释为何某些序列在单细胞测序中富集。由此可以可靠支持 SPARK-seq 在这个细胞系和靶标面板上实现高通量映射并覆盖低丰度蛋白。

仍需谨慎外推的部分包括：新细胞类型和新靶标上的 gRNA 效率、top 10,000 与 MCL 参数的可迁移性、$-\log_2FC$ 到 $k_{off}$ 的跨实验标定，以及深度学习模型在 PTK7 之外的泛化。SPARK-seq 的真正创新不是“测序直接给出靶标”，而是把遗传扰动变成可扩展的靶标依赖性对照，再用正交实验把统计候选变成可信的分子配对。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SPARK-seq: A high-throughput platform for aptamer discovery and kinetic profiling

**DOI:** 10.1126/science.adv6127
**Journal:** Science (2025), Vol. 391, eadv6127
**Authors:** G. Luo, Y. Jiang, L. Liu, T. Fu, Q. Wu\*, W. Tan\*
**Code:** https://github.com/fuyboo/sparta
**Data:** SRA: PRJNA1202227

---

### Motivation & Novelty

Cell surface proteins constitute the targets of >60% of therapeutic drugs, yet high-throughput aptamer discovery against these proteins in native cellular environments has been impossible. The central bottleneck is target identification: conventional Cell-SELEX followed by mass spectrometry pulldown (Apt IP-MS) is slow, low-throughput, requires >10 enrichment rounds, and produces only 1–2 aptamers per experiment. It biases toward high-abundance proteins and abundant aptamer sequences, missing low-copy targets and rare slow-dissociating aptamers.

**What's new:** SPARK-seq repurposes the Perturb-seq framework (*Nat. Methods* 2019; *Nat. Genet.* 2021) for aptamer discovery. By embedding aptamer binding readout directly into single-cell CRISPR screens, it converts aptamer-protein interactions into sequencing data that can be analyzed at scale. Three specific innovations:
1. **Simultaneous target identification for 13 proteins in a single experiment** — compared to 1–2 by Apt IP-MS
2. **Kinetic profiling at the aptamer family level** — SPARK-seq preferentially enriches slow-off-rate (small koff) aptamers by design, providing a koff proxy (-log2FC) that replaces SPR for preliminary ranking
3. **Paired deep learning** — SPARTA's CNN classifier and Raptgen VAE translate the interaction atlas into predictive and generative tools

Prior multi-target aptamer approaches include microfluidics-based selection (*Nat. Chem.* 2023) and SELEX combined with deep sequencing (*Nat. Biotechnol.* 2024). SPARK-seq differs by directly linking aptamer identity to genetic knockout readout at single-cell resolution, removing the need for pull-down experiments.

---

### Method Overview

SPARK-seq integrates four components in a single experiment:

1. **Aptamer library** (R4, enriched by 4-round Cell-SELEX): 46-nt random region flanked by PCR handles and a 3' capture sequence for 10X compatibility
2. **CRISPR perturbation**: 46 gRNAs targeting 13 surface proteins (3 gRNAs/protein + 7 negative controls), transduced into SUM159PT breast cancer cells
3. **Single-cell multiomics** (10X Genomics 5' v2): mRNA, gRNA, and aptamer binding captured simultaneously per cell via dedicated barcodes
4. **SPARTA analysis pipeline** (R package + Python): BLAST-MCL aptamer family clustering → differential binding analysis → 2-component GMM thresholding → protein scoring → CNN prediction → VAE-based sequence generation

Key technical assumptions: (i) aptamers with slow koff are selectively retained after washing steps, encoding kinetic information in sequencing counts; (ii) target-specific aptamers will show reduced binding when their target protein is knocked out; (iii) related aptamers binding the same target can be grouped by sequence similarity.

---

### Evaluation

#### Experimental Validation
- **Flow cytometry**: All predicted aptamers bind target-expressing cells but not KO cells; validated at 4°C and 37°C
- **SPR**: Nanomolar affinities confirmed for PTK7, CDCP1, NRP1, NRP2, ITGA3/ITGB1, PTPRD, PTPRF, PTPRS
- **MST**: Orthogonal affinity confirmation for selected targets
- **Competition assay**: 10× excess non-cognate aptamer does not reduce binding; homologous competition shows dose-dependent displacement
- **SPR cross-binding**: 12 aptamer families vs 8 proteins — high-affinity interactions only with intended targets

#### Quantitative Results
| Metric | Value |
|---|---|
| Total aptamer sequences identified | 4.027 × 10⁷ |
| Top 10,000 sequences coverage | 68.84% of reads |
| Aptamer families (MCL) | 1906 |
| High-quality single cells | 8466 |
| Validated aptamer-protein pairs | 5535 aptamers × 8 proteins |
| koff–log2FC correlation (PTK7, SPR) | R² = 0.88, p < 0.0001 |
| koff–log2FC correlation (PTK7, RT-IC) | R² = 0.87, p = 0.0007 |
| SPARK-seq vs. conventional koff advantage | ~10× slower dissociation rate for PTK7, NRP1, NRP2 |
| FCNA CNN accuracy (PTK7, external) | ~97% |
| Raptgen generation success | 12/15 variants bind PTK7; SPARK-Apt-18 has slowest koff |

#### Coverage
- Target protein abundance spans >100-fold: >10⁵ copies/cell (ITGA3) to <1000 copies/cell (PTPRD, PTPRF)
- 3 proteins initially undetectable by standard proteomics (NRP2, PTPRD, PTPRS)
- Paralog discrimination: NRP1 vs NRP2 (~49.9% sequence identity PTPR family) with no cross-reactivity
- Multi-target aptamers detected: Apt-3-3 (ITGA3/ITGB1 complex); Apt-4-5 (PTPRD, PTPRF, PTPRS paralogs)

---

### Reproducibility

**Rating: 3/5**

**Justification:** Code is publicly available and covers the main SPARTA analysis pipeline. Raw sequencing data deposited at NCBI (PRJNA1202227). The core prediction logic (R package) and deep learning modules (Python) can be run with provided example data. However, several reproducibility barriers exist:

**Strengths:**
- R package installable via `devtools::install_github("fuyboo/SPARTA")`
- Python code for FCNA and Raptgen included with example data
- Pre-trained model weights in `data/output/aptamer_prediction/best_model.pkl`
- Perl scripts for raw read processing included

**Weaknesses / Common Pitfalls:**
1. **Hardcoded path** in `ratgen_aptamer.py:20` (`/home/disk/fuyongbo/lgy/...`) — must be manually edited before running Raptgen
2. **Mixscape step missing from public code**: Recovering PTPRS (aptamer Family 4) requires Mixscape filtering, described in paper but not in SPARTA code
3. **MCL inflation discrepancy**: argparse default is 1.5 but README example uses 0.7; final paper used 1906 families (consistent with 0.7)
4. **No conda/requirements file**: Python dependencies (pysam, raptgen, pytorch, etc.) not specified in a single requirements.txt
5. **gRNA GMM not in code**: Paper describes 3-component GMM for gRNA threshold derivation; code uses fixed 0.7 cutoff. Threshold is empirically the same but reproducibility across datasets not guaranteed
6. **SELEX data not deposited**: R4 aptamer library sequences must be extracted from raw sequencing data (PRJNA1202227); no pre-processed FASTA provided

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
