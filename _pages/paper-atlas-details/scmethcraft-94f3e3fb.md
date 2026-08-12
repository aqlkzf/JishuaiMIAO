---
layout: default
permalink: /paper-atlas/scmethcraft-94f3e3fb/
title: "scMethCraft"
nav: false
description: "scMethCraft 面向单细胞 DNA 甲基化矩阵中大量“明确缺失值（NA）”的问题：它先用每个基因组区域的 DNA 序列、k-mer 和位置预测该区域在所有细胞中的甲基化水平，再学习细胞—细胞相似度对这些预测做加权修正。由此同一模型可以输出增强后的甲基化矩阵、细胞相似度和低维嵌入，并支持批次整合、标签转移和 DMR 候选筛选。"
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
      <span>scATAC — Single-Cell Chromatin &amp; DNA Methylation</span>
      <span>Nature Communications · 2026</span>
    </div>
    <h1>scMethCraft</h1>
    <p>Dissecting epigenetic heterogeneity in single-cell DNA methylomes with a unified framework</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-73171-4" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scMethCraft 中文方法解读

### 一句话理解

scMethCraft 面向单细胞 DNA 甲基化矩阵中大量“明确缺失值（NA）”的问题：它先用每个基因组区域的 DNA 序列、k-mer 和位置预测该区域在所有细胞中的甲基化水平，再学习细胞—细胞相似度对这些预测做加权修正。由此同一模型可以输出增强后的甲基化矩阵、细胞相似度和低维嵌入，并支持批次整合、标签转移和 DMR 候选筛选。

### 1. 为什么 NA 不能当作 0

输入为区域乘细胞矩阵 $X\in\mathbb R^{p\times n}$，默认基因组区域宽度为 10 kbp。观测值是 $[0,1]$ 内的平均 CpG 甲基化比例；NA 表示该细胞在该区域没有覆盖到 reads，而 0 表示有覆盖且观测为未甲基化。两者的生物含义完全不同。

例如，某区域在三个细胞中的值为 $(0.8,\mathrm{NA},0.1)$。把 NA 填成 0 会错误地断言第二个细胞高度低甲基化；scMethCraft 在训练损失中跳过该位置，再根据区域序列和其他细胞的关系预测它。

预处理还会去掉缺失比例超过 80% 的区域、低变异区域和高度冗余的相邻区域。论文写相邻区域余弦相似度阈值 0.9，本地 `filter_region()` 默认值是 0.99，二者必须区分。

### 2. 模块一：从三种视角表示一个基因组区域

scMethCraft 逐区域建模；一个 batch 的样本单位是基因组区域，而输出向量覆盖所有 $n$ 个细胞。`MethyDataset` 为每个区域返回四类对象：序列 one-hot、真实甲基化状态、8-mer 特征和位置编码。

#### 2.1 One-hot CNN 分支

10 kbp DNA 序列编码为 4 通道 one-hot 矩阵。`Sequence_extraction` 依次使用卷积 stem、两个卷积 tower block、1×1 卷积和全连接层，得到 25 维表示。这个分支学习局部 motif、碱基组合及更长程的组合模式。

#### 2.2 8-mer Transformer 分支

区域序列还被汇总为 $4^8=65,536$ 维 8-mer 计数。代码先将其压缩到 256 维，把每个位置投影到 16 维并加可学习位置表，再经过 4-head `TransformerEncoderLayer` 和残差连接，最终压缩为 25 维。它提供与卷积视角不同的全局组成信息。

#### 2.3 位置 KAN 分支

区域中点 $p$ 先按所在染色体最大长度 $p_{max}$ 归一化为 $t=p/p_{max}$，再构造包含 $t$ 和多频率正余弦项的 64 维编码。两层 `KANLinear` 将其变换为 50 维位置门控向量。这里的位置不是细胞顺序，而是该 DNA 区域在染色体上的坐标。

#### 2.4 融合与逐细胞预测

CNN 与 k-mer 分支各输出 25 维，拼接为 50 维 $h_{seq}$；位置分支输出 $h_{pos}$。代码执行

$$
h=h_{seq}\odot h_{pos}+h_{seq},
$$

再用 `Linear(50,n_cells)` 得到该区域对所有细胞的 logits。位置向量相当于门控，但残差项保证位置分支不能完全抹掉序列信息。

### 3. 掩码损失：只让真实观测监督模型

训练 notebook 对非 NA 条目建立布尔掩码 $M_{ri}$，并计算

$$
\mathcal L_{seq}
=-\sum_{r,i:M_{ri}=1}
\left[x_{ri}\log\hat x_{ri}+(1-x_{ri})\log(1-\hat x_{ri})\right].
$$

虽然 $x_{ri}$ 可以是连续甲基化比例，BCE 仍可把它视作软标签。关键点是 NA 不进入损失，也不被解释为 0。模块一的 sigmoid 输出随后填入原矩阵的 NA 位置，构成第二模块的输入。

### 4. 模块二：学习细胞之间如何相互修正

完整版本学习 $n\times n$ 参数矩阵 $P$，再对称化并去掉对角线：

$$
S=\frac{|P+P^\top|}{2}\odot(1-I).
$$

相似度层用 $S$ 对每个区域的逐细胞预测向量做线性组合。直观上，如果细胞 $i$ 与多个同类型细胞相似，它的缺失或噪声值会向这些相似细胞的模式靠拢。第二个 masked BCE 仍只在原始有观测的位置评估修正结果，因此模型通过“能否更好预测已知值”学习相似度，而不是直接拿标签监督。

训练时两个模块使用独立优化器，第二模块的输入对第一模块 `.detach()`，使相似度损失不会反向改变序列网络。论文称其为迭代优化；实际 notebook 是在每个 batch/epoch 中依次更新序列模块和相似度模块。

对于大量细胞，`SimilarityLayer_fast` 不显式保存 $n^2$ 参数，而学习 $P\in\mathbb R^{n\times256}$，通过矩阵乘法等价地产生低秩相似传播，并减去对角项。这降低内存，但相似度表达能力受到秩 256 的约束。

### 5. 从相似度得到细胞嵌入

训练后先将相似度做 GCN 风格归一化：

$$
S_{norm}=D^{-1/2}SD^{-1/2}+\alpha I.
$$

代码 `GCN_norm()` 的 $D$ 实际使用 `row_sum + 1`，用于稳定零度节点。序列模型最后一层权重 $L\in\mathbb R^{n\times50}$ 被视为细胞加载矩阵，最终嵌入为

$$
H=S_{norm}L\in\mathbb R^{n\times50}.
$$

从左到右读：每个细胞先沿相似度图收集其他细胞的 50 维加载，再保留由 $\alpha I$ 控制的自身信息。`output_embedding()` 默认 $\alpha=1$。

### 6. 一个模型如何支持多种任务

#### 6.1 数据增强

`output_enhanced_data()` 对区域先运行序列模块并 sigmoid，再运行相似度模块并再次 sigmoid，输出无缺失的细胞乘区域矩阵。它既填补 NA，也会平滑已有值；因此应称“增强矩阵”，而不是只对 NA 做局部填补。

#### 6.2 批次整合

批次校正不是重新训练一个对抗模型，而是对同批次细胞之间的相似度降权。`output_batch_integration()` 支持固定 $\beta$ 或自适应估计，然后使用 $\alpha=0.8$ 的 `GCN_norm` 重新计算嵌入。这样鼓励跨批次边，但若批次与生物学状态混杂，也可能削弱真实结构。

#### 6.3 标签转移

论文对每个目标细胞选取最相似的 10 个已标注来源细胞，并进行相似度加权投票。`cell_annotation()` 实现了这个思路。不过当前函数在第二个循环中复用了前一循环最后一次的 `similarities` 和 `sorted_indices` 变量，而没有逐目标细胞重新索引权重；这是直接源码可见的潜在实现缺陷，批量标签转移前应修复或独立验证。

#### 6.4 DMR 候选

论文在增强矩阵上比较目标细胞类型与其他细胞，采用双侧 Wilcoxon rank-sum、Bonferroni 校正，并以 $\log_2FC<-1$ 且校正 $P<0.01$ 定义 hypo-DMR。论文也明确提醒：增强会在细胞间引入依赖，而 Wilcoxon 假定观测独立，所以显著性更适合用于候选优先级，而非严格独立样本推断。本地 `function/DMR.py` 只有不完整的火山图辅助代码，实际统计流程位于 notebook，且该 Python 文件包含语法错误，不能视为可用 DMR API。

### 7. 主图与补充图支持什么结论

- 图 1 展示序列特征模块、相似度加权模块和多任务输出，是方法结构的直接证据。
- 图 2 在 11 个数据集上比较嵌入与聚类；scMethCraft 在 AMI/ARI 等整体指标上表现稳定，但具体优势依赖数据集。
- 图 3 展示批次混合、生物保留和跨数据集标签转移。结果支持相似度矩阵可复用于整合与注释，不证明任意混杂设计都能被纠正。
- 图 4 用 meta-cell 相关、热图和 STMN2 区域验证增强矩阵；它支持恢复群体一致模式，但 meta-cell 不是逐位点实验真值。
- 图 5 从 ODC 等细胞类型的 hypo-DMR 延伸到组织表达、GO 与疾病遗传力富集。这些是候选机制和关联证据，不是因果调控验证。
- 图 6 的消融表明 one-hot CNN 和相似度模块贡献最大，同时检验 k-mer、位置与相似度矩阵的作用。

补充材料包含 31 张补充图和 4 张表，覆盖数据集构成、更多基准、不同缺失率、低秩快速版、人工遮蔽恢复、bin size、过滤阈值、潜维数以及固定/自适应 $\beta$。这些结果补强了稳健性与参数选择证据，也揭示快速版与标准版并非完全相同的模型容量。

### 8. 论文与本地代码对应

本地克隆来源为 `https://github.com/BioX-NKU/scMethCraft`；该快照未保存可验证的上游 commit，因此不能声明精确版本。

| 论文机制 | 本地实现 | 对应程度 |
|---|---|---|
| 区域矩阵构建与过滤 | `preprocessing/create_count_matrix.py` | Partial：核心过滤存在，余弦阈值默认值不同 |
| FASTA、one-hot 和 8-mer | `preprocessing/retrive_sequence.py` | Exact |
| 区域数据集和位置编码 | `model/scmethcraft_trainning.py::MethyDataset` | Exact |
| CNN + Transformer + KAN 融合 | `Sequence_extraction` | Exact |
| masked BCE 和双优化器训练 | `tutorial_model_training.ipynb` | Notebook：机制匹配，但没有库级 `train()` API |
| 完整/低秩相似度层 | `SimilarityLayer` / `SimilarityLayer_fast` | Exact |
| GCN 归一化与细胞嵌入 | `similarity_norm.py`、`function/embedding.py` | Partial：代码度矩阵使用 `row_sum+1` |
| 数据增强 | `function/enhancement.py` | Exact |
| 固定/自适应批次校正 | `function/batch.py` | Exact；批次嵌入使用 $\alpha=0.8$ |
| top-10 加权标签转移 | `function/annotation.py` | Partial：算法意图匹配，当前权重索引实现疑似错误 |
| DMR 统计与火山图 | notebook、`function/DMR.py` | Partial/Not usable：统计在 notebook，库文件有语法错误 |
| 论文全部下游富集与作图 | 本地仓库 | Not found as one reproducible pipeline |

### 9. 使用边界

1. NA 掩码解决的是“未覆盖不等于零”，不能补救系统性的细胞/区域选择偏差。
2. BCE 将连续甲基化比例视作软概率，是建模近似，不是对 read-level 二项采样过程的完整似然。
3. 相似度传播可能增强共享信号，也可能过度平滑稀有亚型；应检查原始数据、邻居组成和参数敏感性。
4. 增强矩阵中的细胞不再统计独立，后续差异检验的 $P$ 值需要谨慎解释。
5. 代码训练入口主要存在于 notebook，设备、batch size 和若干默认值需要显式核对；不能只安装包就假设完整论文配置会自动复现。
6. 本地代码提交未记录，未来上游更新时应重新固定 commit 并复核源码差异。

### 证据入口

- 主文：`paper source/paper/hybrid_auto/paper.md`
- 主图：`paper source/paper/hybrid_auto/images/`
- 补充文档：`output_paper_supp_md/paper_supp/hybrid_auto/paper_supp.md`
- 补充图：`output_paper_supp_md/paper_supp/hybrid_auto/images/`
- 核心模型：`scMethCraft/scMethCraft/model/scmethcraft_trainning.py`
- 完整训练：`scMethCraft/tutorial/tutorial_model_training.ipynb`
- 下游函数：`scMethCraft/scMethCraft/function/`
- 既有详细材料：`doc_method.md`、`doc_code.md`、`figure_analysis.md`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## summary.md — scMethCraft

**Paper**: Dissecting epigenetic heterogeneity in single-cell DNA methylomes with a unified framework
**Journal**: Nature Communications, 2026
**DOI**: 10.1038/s41467-026-73171-4
**Code**: https://github.com/nmderic/scMethCraft
**Reproducibility**: ★★★☆☆ (3/5) — well-implemented library, but training loop is notebook-only; cosine threshold discrepancy; device hardcoded to cuda:2

---

### Biological Question

Single-cell DNA methylation (scDNAm) sequencing profiles cytosine methylation at CpG dinucleotides genome-wide in individual cells. Methylation at CpG sites represses gene expression and encodes cell identity — each cell type has a characteristic methylation landscape that differs from scRNA-seq or scATAC-seq signals because: (1) values are continuous ratios ∈ [0,1], not read counts; (2) high methylation means *silenced*, not active (inverse semantics); (3) uncovered regions produce explicit NAs (not zeros) representing missing measurements, not zero methylation.

**The central challenge**: at 10 kbp resolution, scDNAm data retains 30–60% NA entries. Prior methods mishandle NAs (treating them as zeros = incorrect), cannot process continuous values directly, and fail to leverage the underlying DNA sequence as a predictor of methylation state.

**scMethCraft's answer**: model DNA sequence as the primary signal, mask NAs during training, and learn iterative cell-to-cell smoothing to enhance predictions.

---

### Why Prior Methods Fall Short

| Method | Journal, Year | Limitation |
|--------|---------------|-----------|
| **EpiScanpy** | Nat. Commun., 2021 | Treats NAs as zeros (confounds absent signal with hypomethylation); cannot learn sequence-level patterns |
| **MethSCAn** | Nat. Methods, 2024 | Imputes NAs with column medians (ignores cell-type specificity); no sequence model |
| **Liu et al.** | Nature, 2021 | Applies genome-wide mean imputation; no cell-type-specific modeling of CpG methylation |
| **SnapATAC2** | Nat. Methods, 2024 | Designed for binary accessibility (scATAC-seq); does not model continuous methylation or explicit NAs |
| **scBasset** | Nat. Methods, 2022 | Models sequence→accessibility (scATAC-seq only); no similarity weighting or methylation-specific loss |
| **DeepCpG** | Genome Biol., 2017 | Single-cell CpG imputation (site-level); cannot scale to thousands of cells at bin resolution |

---

### Method Summary

scMethCraft has two sequentially trained modules plus a post-training embedding step:

**Module 1 — Sequence Extraction**
For each of the ~10,000–30,000 10 kbp genomic bins retained after quality filtering, three parallel branches process the underlying DNA sequence:
- **Branch 1 (One-hot CNN)**: 4-channel one-hot encoding of 10,000 bp → 4 stacked Conv1D blocks (256→362→512→256 filters) → Dense(25-dim)
- **Branch 2 (K-mer Transformer)**: 8-mer frequency vector (65,536-dim) → Dense(256) → learnable positional table → 4-head TransformerEncoderLayer → Dense(25-dim)
- **Branch 3 (Positional KAN)**: Genomic coordinates encoded via multi-frequency sinusoidal PE (64-dim) → 2 KANLinear layers (64→32→50-dim)

The three branches are fused: `cat(branch1, branch2)` × `branch3` (Hadamard gate) + skip → 50-dim → `Linear(50 → n_cells)`. This produces a predicted methylation vector across all cells for each region. Training uses **masked binary cross-entropy** that ignores NA positions.

**Module 2 — Similarity Weighting**
A learnable symmetric n×n similarity matrix S (or n×256 low-rank factorization for large n) smooths the imputed predictions across cells. NAs are filled with Module 1 predictions before this step. A second masked BCE loss (loss2) trains this module with `.detach()` blocking gradient flow to Module 1.

**Cell Embedding**
After training: normalize S via D^{-1/2}SD^{-1/2} + I (GCN-style), then H = S_norm × L where L = `final.weight` ∈ R^{n×50}. Each cell's 50-dim embedding is a similarity-weighted sum of neighboring cells' region loadings — a one-hop graph convolution.

**Downstream tasks**: UMAP + Louvain clustering, batch integration (β=0.2 intra-batch dampening), cell annotation (top-10 KNN), data enhancement (double sigmoid inference), DMR identification (Wilcoxon rank-sum on enhanced matrix, Bonferroni FDR < 0.01, |log2FC| > 1).

---

### Key Results

#### Clustering (Fig 2)
- scMethCraft achieves **average AMI 0.77** vs. MethSCAn 0.75, EpiScanpy 0.73 across 11 diverse datasets (brain cortex, blood, mouse brain)
- Most dramatic gains on individual datasets: MOp AMI 0.85 vs. MethSCAn 0.77 (+10%); ACC AMI 0.97 vs. MethSCAn 0.86 (+13%)
- All differences statistically significant vs. all baselines (Wilcoxon p ≤ 0.0034)
- Improvement holds across all 5 clustering metrics (AMI, ARI, FMI, homogeneity, NMI)

#### Batch Integration (Fig 3)
- Tested on MTG+Pro two-batch combined dataset (6,000+ cells, 2 brain regions)
- Graph iLISI: EpiScanpy 0.18 → scMethCraft 0.40 (+122% improvement in batch mixing)
- AMI biological conservation: 0.82 → 0.85 (modest but consistent improvement)
- Cross-dataset cell annotation (6 datasets, macro-F1): scMethCraft best in all 6, with largest gain on A5-A7 (+10% over KNN)

#### Data Enhancement (Fig 4)
- Pearson correlation with metacell ground truth: Raw ≈ 0.33, EpiScanpy ≈ 0.33, MethSCAn 0.15–0.65, scMethCraft ≈ 0.88–0.92
- Nearly 3× improvement over raw; 5× improvement over EpiScanpy for non-brain datasets (PBMC: 0.15 → 0.81)
- Visual validation: STMN2 locus shows clear class-specific methylation hierarchy (telencephalic excitatory > inhibitory > non-neuronal) after enhancement; indistinguishable in raw data

#### DMR Identification (Fig 5)
- EpiScanpy-ODC: 142 hypo-DMRs; scMethCraft-ODC: substantially more, enriched near ODC marker genes (PTPRZ1, BIN1, MBP)
- OPC DMRs: enrich CNS/brain GO tissue categories; top GO terms = Oligodendrocyte differentiation, Myelination, Gliogenesis
- L5-ET DMRs: enrich Excitatory postsynaptic potential, Chemical synaptic transmission (appropriate for projection neurons)
- Both tissue enrichment and GO enrichment confirm biological specificity of scMethCraft DMRs vs. EpiScanpy's non-specific output

#### Ablation (Fig 6)
- Removing one-hot CNN collapses performance to EpiScanpy baseline (relative gain 0.06/1.00)
- Removing similarity module: 0.76/1.00 — second most critical component
- Removing k-mer: 0.88/1.00; removing position: 0.92/1.00
- MTG exception: removing position occasionally improves performance (relative 1.15), suggesting mild overfitting

---

### Architecture Novelty

1. **KANLinear for positional features**: First scDNAm method to use Kolmogorov-Arnold Networks (B-spline basis, spline_order=3, grid_size=5) to process genomic coordinates. Captures non-linear relationships between position and methylation state (e.g., telomeric vs. centromeric behavior) that a linear layer cannot.

2. **Two-optimizer decoupled training**: Part1 (sequence) and Part2 (similarity) are updated with independent Adam optimizers. `.detach()` prevents loss2 from distorting sequence features. This ensures the sequence module learns purely genomic predictions, and the similarity module learns only cell-cell relationships — critical for preventing feature collapse.

3. **Low-rank similarity factorization**: For n > 5,000 cells, full n×n matrix would require O(n²) memory (3.6 GB for n=15,000). Low-rank P ∈ R^{n×256} reduces to O(nk) memory (60 MB) while achieving equivalent performance. The factorized forward avoids materializing the full matrix.

4. **Masked BCE on continuous values**: Treating continuous [0,1] methylation as "methylation probability" and applying masked BCE is a deliberate approximation consistent with scBasset/DeepCpG. The masking ensures NAs are not treated as zeros during training.

---

### Evaluation Design

**Benchmark datasets** (11 total):
- Human cortex: ACC (anterior cingulate cortex), M1C (primary motor cortex), MTG (middle temporal gyrus), A5-A7 (premotor areas), Pro (premotor cortex), A46 (dorsolateral prefrontal cortex) — from Luo et al. 2022, ~3,000–10,000 cells each
- Immune: PBMC (peripheral blood mononuclear cells)
- Mouse brain: MOs (secondary motor area), MOp (primary motor area), CP1, CP2 (caudate-putamen)

**Clustering metrics**: AMI, ARI, FMI, homogeneity, NMI (5 metrics to avoid single-metric bias)

**Enhancement validation**: Pearson correlation with metacell (50–100 cells aggregated per type per region) as pseudo-ground truth

**Batch integration**: MTG + Pro combined; kBET, Graph iLISI, Batch silhouette (batch mixing) + AMI, ARI, NMI (biological conservation)

**DMR validation**: Tissue enrichment (ENCODE methylation profiles, 30 tissues) + GO enrichment (biological process terms)

**Comparison baselines**: SnapATAC2, EpiScanpy, Liu et al. (latent factor), MethSCAn — covering the state-of-the-art scDNAm methods as of 2026

---

### Reproducibility Assessment

**Code quality** (★★★☆☆):
- All core model classes implemented cleanly in `scMethCraft/model/scmethcraft_trainning.py`
- Preprocessing pipeline complete (`create_count_matrix.py`, `retrive_sequence.py`)
- All downstream functions provided (`embedding.py`, `batch.py`, `annotation.py`, `enhancement.py`)
- 8 tutorial Jupyter notebooks cover the full workflow

**Concerns**:
1. **Training loop is notebook-only**: No `train()` API; users must adapt `tutorial_model_training.ipynb`. Significant barrier for reproducibility.
2. **Device hardcoded**: `device = "cuda:2"` at `scmethcraft_trainning.py:14` — must be manually changed for other GPU setups.
3. **Cosine threshold discrepancy**: Paper states threshold = 0.9 for region deduplication; code default is `threshold_sim=0.99`. Experiments may have used the paper value.
4. **Batch size discrepancy**: Paper Methods says batch_size=64; tutorial uses batch_size=128.
5. **Batch GCN α discrepancy**: Standard embedding uses α=1 (per paper); batch integration uses α=0.8 (undocumented code difference).
6. **DMR scoring incomplete**: `function/DMR.py` contains only a volcano plot helper — the actual Wilcoxon test and fold change computation are in tutorial notebooks.

**What works well**: The masked BCE, similarity matrix construction, low-rank factorization, batch β-dampening, and cell embedding formulas all match the paper exactly.

---

### Related Methods

| Method | Relationship |
|--------|-------------|
| **scBasset** | Predecessor: sequence → scATAC-seq accessibility (binary); inspired Branch 1 architecture and masked BCE idea |
| **DeepCpG** | Related: single-cell CpG site imputation using deep learning; per-site, not bin-level |
| **MethSCAn** | Direct comparison baseline; NMF-based latent factor model for scDNAm |
| **EpiScanpy** | Main baseline; general scATAC-seq toolkit adapted for methylation |
| **SnapATAC2** | scATAC-seq baseline adapted for methylation comparison |
| **MAGIC / SAVER** | scRNA-seq imputation methods; conceptually related to the enhancement task but wrong data type |
| **KAN (Kolmogorov-Arnold)** | General ML framework for spline-based non-linear networks; scMethCraft is first application in scDNAm |
| **GCN (Kipf & Welling 2016)** | Graph convolution normalization formula (D^{-1/2}AD^{-1/2}) directly adopted for similarity-based cell embedding |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
