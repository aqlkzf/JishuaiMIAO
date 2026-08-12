---
layout: default
permalink: /paper-atlas/cytotrace2-cace9414/
title: "CytoTRACE2"
nav: false
description: "CytoTRACE 2 从单细胞转录组预测“发育潜能”：一方面给出六类标签（分化、单能、寡能、多能、多潜能、全能），另一方面给出 0–1 连续分数，其中 1 更接近全能、0 更接近终末分化。它学习的是由人工整理的潜能标签所定义的绝对标尺，而不是从一批细胞中无监督重建分支、方向或真实谱系。 与 CytoTRACE 1 的数据集内相对排序不同，CytoTRACE 2 试图让不同组织、平台和物种的分数可比较。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>CytoTRACE2</h1>
    <p>Improved reconstruction of single-cell developmental potential with CytoTRACE 2</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02857-2" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CytoTRACE 2 方法解读：把单细胞映射到跨数据集可比较的发育潜能尺度

### 任务边界

CytoTRACE 2 从单细胞转录组预测“发育潜能”：一方面给出六类标签（分化、单能、寡能、多能、多潜能、全能），另一方面给出 0–1 连续分数，其中 1 更接近全能、0 更接近终末分化。它学习的是由人工整理的潜能标签所定义的绝对标尺，而不是从一批细胞中无监督重建分支、方向或真实谱系。

与 CytoTRACE 1 的数据集内相对排序不同，CytoTRACE 2 试图让不同组织、平台和物种的分数可比较。不过“绝对”仍是相对于训练 atlas 的校准：新物种、严重缺基因、肿瘤异常状态或训练范围外表型都需要额外验证。

### 输入与输出

输入是原始计数或 CPM/TPM 的基因×细胞矩阵和 `mouse`/`human` 物种标识，不能预先做 log 变换。人基因会映射到小鼠同源基因；模型最终按 14,271 个训练特征重排，缺失基因补零。每个细胞同时产生基因表达秩和 $\log_2(\mathrm{CPM}+1)$ 两种表示。

输出包含原始连续分数、后处理后的 `CytoTRACE2_Score`、六类 `CytoTRACE2_Potency`，以及各类别的模型概率。高分表示较高潜能，而不是“更晚”的伪时间。

### GSBN 如何工作

#### 1. 六个可解释的二值基因集模块

模型为六个潜能类别各建一个 Gene Set Binary Network（GSBN）。每个模块含 24 个可学习基因集；连续权重经 straight-through estimator 在前向传播中变为 0/1。`cytotrace2_python/cytotrace2_py/common/models.py:7-14,26-48` 直接实现二值化、初始化和模块结构。这样可从训练后的权重中读取哪些基因被选入，但不意味着入选基因一定因果决定潜能。

#### 2. 同一基因集计算两种富集

秩空间计算 UCell 型富集，强调相对表达并减轻平台尺度影响；log2-CPM 空间计算 AMS，以预计算背景基因集校正表达量富集。两者拼接、BatchNorm、dropout 后进入线性层得到该潜能类别的 logit（`models.py:44-72`）。六个 logit 经 softmax 得到概率 $\mathbf P$。

#### 3. 类别与连续分数

类别取最大概率；原始分数是

$$
\mathrm{RPS}=\mathbf P\cdot[0,0.2,0.4,0.6,0.8,1]^\top.
$$

`common/gen_utils.py:48-68,241-250` 与该定义一致。19 个预训练模型分别来自训练集 leave-one-dataset-out 方案，推断时平均概率和连续分数。

### 三步后处理

1. **Markov diffusion**：在每批细胞的 1,000 个高离散基因上计算相关图，并迭代 $s^{(t+1)}=0.9As^{(t)}+0.1s^{(0)}$（`gen_utils.py:256-320`）。这会借用转录相似邻居的信息，也可能平滑真实稀有状态。
2. **类别内分箱**：将每个预测类别内的细胞按平滑分数排序，重新放进该类别对应的六分之一区间（`gen_utils.py:323-350`），从而保持类别与连续分数一致。
3. **自适应 kNN**：在逐细胞标准化后的 30 PCs 上寻找最多 30 个邻居并做距离加权平均（`gen_utils.py:374-449`）。论文从中心细胞与最近邻开始描述，代码从两组各两个元素开始比较，因此最小保留 4 个（其中排序列表包含中心细胞），属于实现偏差。代码对整个数据集少于 100 个细胞时跳过 kNN；论文另行建议关注少于 5 个细胞的稀有表型时关闭该步骤，这两个阈值针对不同对象。

### 图的证据链

- **主图 1**：定义六级潜能 atlas、GSBN 架构，并以训练、独立测试、leave-clade-out 和多种方法/基因集比较评估绝对与相对排序。
- **主图 2**：从二值基因集提取特征重要性；CRISPR screen 提供独立功能一致性，随后用 qPCR 和肠道原位杂交验证 UFA 合成基因与多潜能细胞的关联。关联与富集证据不等同于对所有标记做了逐基因因果验证。
- **扩展图 1–3**：拆解 GSBN 和后处理贡献，并测试超参数、标签噪声、基因/UMI 下采样和稀有细胞数。
- **扩展图 4–8**：检验未见表型、胚胎时间序列、癌症和 scVelo 比较。CytoTRACE 2 不依赖 spliced/unspliced 矩阵，但也不输出 velocity vector 或谱系转移概率。
- **扩展图 9–10**：检查基因集跨 cohort/物种/平台的一致性，并补充 UFA 标记的组织验证。

### 论文与代码的对应

本地 commit `47ce556037cd849d93f9d61353fd0055b571d1f6` 同时包含 Python 和 R 推断包、19 个 Python 权重、R 参数对象、背景矩阵、映射表和示例结果。核心 GSBN、预处理、集成预测和后处理均可直接定位。

训练循环没有随仓库发布，因此论文中的联合损失、NAdam、WeightedRandomSampler、跨 epoch 梯度累积和早停无法由本地代码核验。评估脚本和全部 atlas 数据也不在工作区，本轮没有重跑论文指标。

### 当前 Python 快照的实现注意点

- `cytotrace2_py.py:144` 写成 `batch_size <- len(expression)`；在 Python 中它是比较表达式而非赋值，所以只影响“用户 batch_size 大于细胞数”时的上限修正，后续通常仍能以单批运行。
- `shortest_consensus()` 的最小邻域与论文文字不同，如上所述。
- `gen_utils.py:442` 对负分数执行自赋值，不能修复负值；不过当前 `shortest_consensus()` 默认至少返回 4，使 `-1` fallback 在正常路径中不可达。它仍提示这段错误处理没有被有效验证。
- Python 源码未发现自动化测试目录；R/Python 示例输出不能替代端到端测试。

### 最重要的解释限制

1. 潜能是模型对训练标签的预测，不是细胞未来命运的直接观测。
2. 后处理利用同一输入数据的邻域结构，局部平滑后的细胞不再完全独立。
3. 跨数据集可比较不代表消除所有批次、物种和疾病域偏移。
4. 特征重要性适合提出候选机制；因果结论仍需专门扰动实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CytoTRACE 2 — Paper Summary

### Motivation & Novelty

#### Biological Problem

All cells in multicellular organisms are hierarchically organized by **developmental potential** (potency) — the capacity to differentiate into other cell types. Potency ranges from totipotent (entire organism) to fully differentiated, and understanding this hierarchy is fundamental to stem cell biology, regenerative medicine, and cancer research. While scRNA-seq has enabled single-cell profiling at unprecedented scale, computationally determining *where* each cell falls on the absolute potency spectrum remains an open challenge.

#### Limitations of Existing Approaches

- **CytoTRACE 1** (Gulati et al., *Science*, 2020): Predicts relative developmental potential using gene counts (transcriptional diversity), but scores are dataset-specific and cannot be compared across experiments.
- **RNA velocity** (scVelo, Bergen et al., *Nat. Biotechnol.*, 2020; CellRank, Lange et al., *Nat. Methods*, 2022): Requires spliced/unspliced data and continuous developmental processes within narrow time windows.
- **Entropy methods** (SCENT/SR, Teschendorff & Enver, *Nat. Commun.*, 2017; SCENT/CCAT, Teschendorff et al., *Bioinformatics*, 2020; SLICE, Guo et al., *NAR*, 2017): Produce dataset-relative scores without absolute calibration.
- **Deep learning for cell type** (scPred, Alquicira-Hernandez et al., *Genome Biol.*, 2019; SingleCellNet, Tan & Cahan, *Cell Syst.*, 2019; scmap, Kiselev et al., *Nat. Methods*, 2018): Lack interpretability and were not designed for potency prediction.
- **Stemness indices** (mRNAsi, Malta et al., *Cell*, 2018; FitDevo, Zhang et al., *Brief. Bioinform.*, 2022; StemID, Herman et al., *Nat. Methods*, 2018): Dataset-specific or require predefined gene weight matrices.
- **Trajectory inference** (scTour, Li, *Genome Biol.*, 2023; Monocle, Qiu et al., *Nat. Methods*, 2017): Focus on ordering within a single dataset rather than absolute potency.

#### Unique Contributions

1. **Absolute potency prediction**: CytoTRACE 2 predicts potency on a universal 0–1 scale calibrated to 6 biological categories (totipotent to differentiated), enabling cross-dataset and cross-species comparison without batch correction.

2. **Interpretable deep learning via GSBNs**: The Gene Set Binary Network architecture constrains gene selection weights to {0, 1}, making learned gene sets directly extractable — a rare property in deep learning.

3. **Curated potency atlas**: 33 human and mouse scRNA-seq datasets (406,058 cells, 125 phenotypes) with experimentally validated potency annotations, organized into 6 broad and 24 granular potency levels.

4. **Biological discovery**: Model interpretability enabled identification of unsaturated fatty acid (UFA) synthesis genes (*Fads1*, *Fads2*, *Scd2*) as cross-tissue multipotency markers — experimentally validated by qPCR and in situ hybridization.

### Method Overview

CytoTRACE 2 is a supervised deep learning framework consisting of:

1. **Preprocessing**: Gene symbol harmonization to a 14,271-gene dictionary; dual encoding into rank space (batch-robust) and log2-CPM (magnitude-preserving).

2. **Core model**: Six GSBN modules (one per potency category), each learning 24 binary gene sets. Two enrichment scores (UCell rank-based + AMS expression-based) per gene set are computed, concatenated, normalized via BatchNorm, and passed through dropout + linear layers to produce potency logits. Softmax yields per-category likelihoods; a weighted sum produces the continuous raw potency score (RPS).

3. **Ensemble**: 19 models trained via leave-one-dataset-out cross-validation, averaged at prediction time.

4. **Postprocessing**: Three-step refinement — (a) Markov diffusion smoothing using transcriptional covariance, (b) binning to reconcile continuous scores with categorical predictions, (c) adaptive k-NN smoothing with consensus-based neighborhood selection.

The pipeline is fully automatic, requires only a gene expression matrix and species label, and runs on CPU. See `doc_method.md` for mathematical details and `doc_code.md` for implementation mapping.

### Evaluation

#### Datasets

- **Training**: 19 datasets, 312,523 cells, 93 phenotypes, 16 tissue types, 6 platforms
- **Test**: 14 held-out datasets, 93,535 cells, 73 phenotypes, 9 tissue types, 7 platforms
- **Extended benchmarks**: Tabula Sapiens (459,320 cells, postmortem), 6 mouse embryogenesis datasets (183,771 cells), AML and oligodendroglioma cancer datasets
- **CRISPR validation**: ~7,000 gene knockouts in mouse HSCs for functional genomics assessment

#### Metrics

- **Absolute order**: Weighted Kendall τ across datasets against 6 broad potency levels
- **Relative order**: Median weighted Kendall τ within individual datasets
- **Multiclass F1**: Mean F1 score across 6 potency categories
- **MAE**: Mean absolute error for categorical potency predictions

#### Key Results

- **Potency classification**: Outperformed 8 supervised ML methods (scPred, SingleCellNet, scmap, logistic regression, XGBoost, linear SVM, radial SVM, multinomial logistic regression) with highest median F1 and lowest MAE across 4-fold cross-validation.
- **Developmental hierarchy inference**: Surpassed 8 methods (CytoTRACE 1, SCENT SR, SCENT CCAT, FitDevo, SLICE, StemID, scTour, mRNAsi) with >60% higher average correlation for relative orderings in 57 developmental systems.
- **Gene set comparison**: Outperformed 18,706 annotated gene sets from MSigDB and ENCODE/ChEA.
- **scVelo comparison**: Higher absolute and relative order correlations than scVelo's dynamical and differential kinetics models in 9 evaluable test datasets.
- **Mouse embryogenesis**: Accurately reconstructed temporal potency decline across 62 embryonic time points spanning E0.5 to P0.
- **Robustness**: Tolerated up to 20% annotation error with minimal performance loss; stable down to 500 genes per cell and 1000 UMIs per cell; reliable for cell populations as small as 5 cells.
- **Cancer applications**: AML potency predictions aligned with known leukemic stem cell signatures; correctly identified multilineage potential in oligodendroglioma.

#### Biological Validation

- UFA synthesis genes (*Fads1*, *Fads2*, *Scd2*) enriched in multipotent cells (train-test AUC 0.87–0.92)
- CRISPR screen validation: top 100 positive multipotency markers enriched for genes whose knockout promotes HSC differentiation (Q = 0.04)
- qPCR confirmed UFA gene enrichment in FACS-purified mouse HSC/MPP vs progenitor/differentiated cells
- In situ hybridization confirmed UFA gene co-expression with multipotency markers in intestinal crypts (jejunum, duodenum, ileum)

### Reproducibility

**Rating: 4/5 (Good)**

**Strengths**:
- Pre-trained model weights and inference code are publicly available (Python via PyPI + R via GitHub) with comprehensive documentation
- 33-dataset potency atlas with detailed annotations in supplementary tables
- Web application at <https://cytotrace2.stanford.edu> provides interactive access including training capability
- Gene dictionary, ortholog mapping, and background matrix are all shipped with the package
- Comprehensive vignettes for both Python and R implementations

**Weaknesses**:
- Training code is not included in the public repository — only available through the web application
- Cross-epoch gradient accumulation (a key training innovation) is not verifiable from shipped code
- Loss function, optimizer configuration, and data sampling code must be taken on faith from the paper
- Some postprocessing details differ between paper and Python code (the consensus grouping starts at two elements; the negative-score fallback is ineffective but normally unreachable)

**Practical Notes**:
- Installation requires Python 3.9+ with PyTorch 2.0.0 and scanpy
- Memory: ~200 MB for model weights + background matrix; runtime scales with cell count (dominated by Markov diffusion and k-NN, both $O(C^2)$ per chunk)
- Input: tab-delimited gene × cell matrix (raw counts or CPM/TPM); do NOT pre-normalize to log-space
- Automatically handles human-mouse ortholog mapping; species parameter required
- Default batch size of 20,000 cells works for most datasets; reduce if memory-limited
- R assignment operator bug on Python line 144 (`batch_size <- len(expression)`) means batch_size cap doesn't work — not critical since the code still functions, just doesn't enforce the documented limit

**Common pitfalls**:
- Input data must NOT be log-transformed — the code applies its own log2(CPM+1) normalization. A warning is issued if max expression ≤ 20.
- Human gene symbols are mapped to mouse orthologs internally; do not pre-convert genes.
- For entire datasets with <100 cells, Python skips k-NN smoothing. Separately, the paper recommends disabling k-NN when rare phenotypes with <5 cells are the target; these thresholds refer to different scopes.
- The Python code has a bug on line 144 (`batch_size <- len(expression)`) where the R-style assignment operator is a no-op in Python, so the batch_size upper limit is not enforced.

**Data availability**: All 33 datasets are publicly available via GEO/SRA/ArrayExpress accession codes provided in Supplementary Table 1. Tabula Muris and Tabula Sapiens data accessible via their respective repositories.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
