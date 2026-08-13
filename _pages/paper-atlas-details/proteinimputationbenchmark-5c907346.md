---
layout: default
permalink: /paper-atlas/proteinimputationbenchmark-5c907346/
title: "ProteinImputationBenchmark"
nav: false
description: "这篇 Genome Biology 2026 论文研究一个实际问题：在单细胞 RNA-seq 数据中，能不能只凭 RNA 表达来推断细胞表面蛋白表达？传统做法常把某个蛋白对应基因的 mRNA 当作蛋白表达的近似值，但论文首先证明这个近似经常不可靠。以 Hao 等人的 PBMC CITE-seq 数据为例，207 个可对齐的蛋白-mRNA 对中，很多只有弱相关或负相关；"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Genome Biology · 2026</span>
    </div>
    <h1>ProteinImputationBenchmark</h1>
    <p>Machine learning predictions surpass individual mRNAs as a proxy of single-cell protein expression</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-026-04083-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ProteinImputationBenchmark">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/fisherj2/imputation-of-protein-from-RNA" target="_blank" rel="noopener noreferrer" aria-label="Open code for ProteinImputationBenchmark">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法解读：ProteinImputationBenchmark

### 这篇论文解决什么问题？

这篇 Genome Biology 2026 论文研究一个实际问题：在单细胞 RNA-seq 数据中，能不能只凭 RNA 表达来推断细胞表面蛋白表达？传统做法常把某个蛋白对应基因的 mRNA 当作蛋白表达的近似值，但论文首先证明这个近似经常不可靠。以 Hao 等人的 PBMC CITE-seq 数据为例，207 个可对齐的蛋白-mRNA 对中，很多只有弱相关或负相关；CD103 是典型例子，表面蛋白只在一小部分 T 细胞中明显，而 ITGAE RNA 分布更广，无法直接代表蛋白水平（`paper source/PMC13235196/paper.md:53-55`）。

因此，论文评估的是另一种思路：不用单个 mRNA，而是用全转录组模式训练机器学习模型，从 RNA 推断蛋白。

### 它不是一个新模型，而是一个基准测试

这项工作不是提出一个新的 imputation 模型，而是对 9 个已有方法做独立 benchmark：

- Seurat reference mapping
- sciPENN
- totalVI
- BABEL
- scMMT
- cTPnet
- scTranslator
- scLinear
- SPECK

论文在 Hao PBMC 数据上做主实验：随机取 20% 作为测试/query 细胞，剩余 80% 作为训练集；scTranslator few-shot 额外用测试集中的 1000 个细胞做微调；主要指标是预测蛋白和真实蛋白之间的 Pearson correlation（`paper source/PMC13235196/paper.md:59-60`）。

### 整体流程

```text
CITE-seq 数据
  RNA 矩阵 + protein/ADT 矩阵 + metadata
        |
        v
统一预处理
  - 读取 Seurat 对象
  - 按实验设置划分训练/测试
  - 输出 RNA/protein 的 raw/normalized 矩阵
        |
        v
9 个方法分别运行
  - 每个方法用自己的 wrapper 和 conda 环境
  - 输出 protein-by-cell 预测矩阵
        |
        v
指标对齐与归一化
  - 不同方法预测值和真实 protein 的尺度不同
  - 按方法作者推荐的格式归一化真实 protein
  - 计算 Pearson、Spearman、RMSE、NRMSE
        |
        v
结果分析
  - 方法性能热图
  - cell type sensitivity
  - 跨数据集泛化
  - scLinear feature importance
```

代码层面，这个流程主要由 Nextflow 组织。`main.nf` 导入 9 类方法模块，先运行 `preprocess_data`，再按开关运行各方法，最后合并预测输出并进入评价步骤（`imputation-of-protein-from-RNA/main.nf:9-18`, `imputation-of-protein-from-RNA/main.nf:119-216`）。

### 训练/测试划分如何实现？

论文说训练前做 80:20 划分，并且随机抽样时保留 cell type 比例（`paper source/PMC13235196/paper.md:134-136`）。代码中这一点是直接可验证的：`prepare_training_data.R` 设置 `set.seed(123)`，读取 `celltype` metadata，然后用 `caret::createDataPartition(..., p = 0.8)` 选训练细胞，剩下的作为测试细胞（`imputation-of-protein-from-RNA/bin/R/prepare_training_data.R:18-18`, `imputation-of-protein-from-RNA/bin/R/prepare_training_data.R:313-397`）。

代码还支持几种 benchmark 变体：

- 不同训练集大小：6.125%、12.5%、25%、50%、100%。
- within-cell-type：只取某一个 cell type，再做 80:20。
- held-out-cell-type：某个 cell type 完全作为测试集，其他细胞训练。
- cross-dataset：一个 CITE-seq 数据集训练，另一个数据集测试。

这些设置在 `nextflow.config` 和 `prepare_training_data.R` 中可以看到，但不是所有论文中使用的完整运行命令都被整理成一个可直接复现的脚本（`imputation-of-protein-from-RNA/nextflow.config:105-138`, `imputation-of-protein-from-RNA/bin/R/prepare_training_data.R:325-397`）。

### 评价指标和归一化

论文主要用 Pearson correlation 衡量预测蛋白和真实蛋白的一致性，并用 NRMSE 辅助评价。NRMSE 是 RMSE 除以真实蛋白表达的标准差（`paper source/PMC13235196/paper.md:138-142`）。

一个重要细节是：不同方法要求的 protein 预处理尺度不同，所以真实 protein 也要按方法分别归一化。论文明确说明：

- Seurat、BABEL、SPECK、scMMT、scLinear：与 CLR normalized counts 比较。
- totalVI：与 scanpy log1p transformed counts 比较。
- sciPENN：先 counts-per-cell，再 log1p，再按 donor 做 gene-wise z-score。
- cTPnet：使用 Stoeckius 等人描述的 abundance transform。
- scTranslator：使用 scaled min-max normalization。

代码中，这个最终对齐主要在 `analyses/adjust_metrics.R` 和 `analyses/method_specific_normalisation.R`，而不是完全在 Nextflow 第一轮 `evaluate_predictions.R` 中完成（`imputation-of-protein-from-RNA/analyses/adjust_metrics.R:45-128`, `imputation-of-protein-from-RNA/analyses/method_specific_normalisation.R:4-190`）。这意味着论文级指标是有代码依据的，但复现时需要跑 pipeline 后再跑分析/调整脚本。

### 主要结果怎么理解？

#### 1. 单个 mRNA 经常不是好 proxy

Fig. 1 显示很多 RNA-protein 对相关性弱，CD103/ITGAE 的例子尤其直观。即使用 percent positivity 或 pseudobulk 这种群体级 RNA 汇总，也不能解决所有单细胞层面的不一致。

#### 2. 全转录组模型通常优于 cognate mRNA

Fig. 2 显示大多数 ML 方法在很多蛋白上给出更高的预测相关性。一个典型例子是 CD110：MPL RNA 在血小板中几乎不可检测，但 CD110 蛋白在血小板表面富集，scLinear 等模型能利用整体血小板转录组特征恢复这个蛋白信号（`paper source/PMC13235196/paper.md:68-70`）。

#### 3. 性能强烈依赖 cell type

Fig. 3 是这篇论文最关键的限制性证据。within-cell-type 的下降相对温和，但 held-out-cell-type 中所有方法都明显下降，论文报告没有任何方法在所有 feature 的 median prediction correlation 上超过 0.3（`paper source/PMC13235196/paper.md:83-85`）。这说明模型学到的很大一部分信息来自训练集中已有的 cell-type transcriptional signatures。

#### 4. 跨数据集泛化不稳定

Fig. 4 进一步说明：同一数据集内训练/测试效果最好，跨 tissue 或跨 disease context 时性能明显下降。论文结论是，可靠 protein imputation 通常需要与目标数据 phenotypic composition 相似的高质量 multimodal reference（`paper source/PMC13235196/paper.md:96-99`, `paper source/PMC13235196/paper.md:112-114`）。

### scLinear feature importance

论文用 scLinear 做可解释性分析，因为它能给出 RNA feature 对 ADT 预测的 importance。论文描述这个 importance 是预测 ADT 对输入 RNA 的 Jacobian，并由 SVD、linear regression、z-score normalization 组件的 Jacobian 乘积得到（`paper source/PMC13235196/paper.md:160-162`）。

代码中这条路径是分散的：

- 主 scLinear wrapper 训练并保存模型，但 feature importance 计算被注释掉，原因是内存消耗大（`imputation-of-protein-from-RNA/modules/local/scLinear/bin/predictADT_scLinear.py:125-138`）。
- `analyses/feature_importance.py` 从绝对路径加载保存的 scLinear 模型，读取测试 RNA，调用 `pipe.feature_importance`，输出 importance matrix（`imputation-of-protein-from-RNA/analyses/feature_importance.py:13-22`）。
- scLinear 的 `prediction.py` 中真正实现了 Jacobian 计算：先转入低维 PCA/SVD 空间，对 z-score 步骤求 Jacobian，再乘上线性模型系数和 SVD components，最后对细胞取平均（`imputation-of-protein-from-RNA/modules/local/scLinear/bin/prediction.py:163-207`）。
- `analyse_predictions.Rmd` 再把这个矩阵整理成 Fig. 3D 对应的 heatmap（`imputation-of-protein-from-RNA/analyses/analyse_predictions.Rmd:1775-1817`, `imputation-of-protein-from-RNA/analyses/analyse_predictions.Rmd:1945-1971`）。

所以 Fig. 3D 的可解释性结论有代码基础，但它不是主 Nextflow wrapper 直接输出的结果。

### 代码复现性评价

代码和论文的匹配度是 **中等**。

已经直接验证的匹配点：

- Nextflow 确实组织了 9 类方法的 benchmark fanout。
- 80:20 随机划分和 cell type proportion preservation 有直接 R 代码实现。
- scTranslator few-shot 的 1000 cells 参数在 Nextflow 模块中明确传入。
- 方法特异的 protein normalization 和 Pearson/NRMSE 指标在后处理脚本中有实现。
- scLinear feature importance 的核心 Jacobian 计算在代码中可见。

主要缺口：

- 克隆仓库中没有完整 `source_data/`。
- `submit_pipe.sh`、`nextflow.config` 和部分分析脚本引用 `/shared-workspace`、`/home/jfisher2` 等绝对路径。
- benchmarking profile 默认 `use_old_inputs="true"`，会从外部旧分析目录读取已保存矩阵。
- scTranslator 预训练 checkpoint 没有随仓库提供。
- 所有最终论文图不能从 fresh clone 一条命令完整再生成。

因此，这个仓库适合用来理解 benchmark 的组织方式、关键实现选择和部分分析路径；如果要完全复现论文所有数值和图，需要额外数据、checkpoint、历史中间文件和本地路径修复。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

Single-cell RNA atlases are widely available, but RNA abundance is often a weak proxy for cell-surface protein abundance. This paper benchmarks whether machine-learning protein imputation from whole-transcriptome scRNA-seq can outperform direct use of a protein's cognate mRNA.

The motivating baseline is strong: among 207 protein-mRNA pairs in the Hao PBMC CITE-seq data, only a small subset shows strong single-cell RNA-protein correlation, while many are weak or negative; CD103 is a highlighted case where RNA and measured surface protein disagree (`paper source/PMC13235196/paper.md:53-55`).

### Benchmark

The study compares nine published methods: Seurat, sciPENN, totalVI, BABEL, scMMT, cTPnet, scTranslator, scLinear, and SPECK. It evaluates them on Hao PBMC train/test splits, cell-type-restricted and held-out-cell-type settings, and pairwise transfer across four CITE-seq datasets. Pearson correlation is the primary prediction metric; NRMSE is also used (`paper source/PMC13235196/paper.md:59-60`, `paper source/PMC13235196/paper.md:144-158`).

This is a benchmark workflow rather than a single new model. The released code uses Nextflow to preprocess CITE-seq matrices, run method-specific wrappers, collect prediction matrices, and evaluate or post-process metrics (`imputation-of-protein-from-RNA/main.nf:119-216`).

### Main Findings

- Whole-transcriptome ML predictions usually match or improve over cognate mRNA. For all features, the maximum ML prediction correlation exceeded the gene mRNA-only correlation, although 22 proteins remained poorly predicted by both approaches (`paper source/PMC13235196/paper.md:68-72`).
- Performance depends strongly on feature properties. Proteins with higher counts and higher between-cell variability are easier to predict, consistent with Fig. 2C.
- Cell-type composition is a major determinant. Held-out-cell-type prediction causes a broad decline, with no method exceeding median prediction correlation 0.3 across all features in that setting (`paper source/PMC13235196/paper.md:83-85`).
- Cross-dataset transfer is volatile. Within-dataset comparisons are strongest; transfer between tissues drops significantly for trained methods (`paper source/PMC13235196/paper.md:96-99`).
- Usability matters because performance is often similar. The paper identifies scLinear and Seurat as prominent fast-running methods with reasonable resource requirements and strong prediction performance (`paper source/PMC13235196/paper.md:100-102`, `paper source/PMC13235196/paper.md:108-108`).

### Reproducibility and Code Match

Overall code-paper fidelity is **medium**. The core benchmark scaffold is present and meaningful:

- The Nextflow workflow imports and conditionally executes the nine method families (`imputation-of-protein-from-RNA/main.nf:9-18`, `imputation-of-protein-from-RNA/main.nf:128-216`).
- The 80:20 split with cell-type preservation is implemented via `caret::createDataPartition` after seeding (`imputation-of-protein-from-RNA/bin/R/prepare_training_data.R:18-18`, `imputation-of-protein-from-RNA/bin/R/prepare_training_data.R:313-397`).
- scTranslator few-shot is run with `--ncells 1000`, matching the paper (`imputation-of-protein-from-RNA/modules/local/scTranslator/main.nf:142-152`).
- Final paper-aligned Pearson/NRMSE values are most clearly represented in the post-pipeline metric adjustment script (`imputation-of-protein-from-RNA/analyses/adjust_metrics.R:81-128`).

The main gaps are also clear:

- Source datasets and saved benchmark matrices are not bundled in the clone.
- Several scripts reference absolute `/shared-workspace` or `/home/jfisher2` paths.
- The benchmarking profile can reuse external precomputed inputs.
- The scTranslator pretrained checkpoint is not present.
- Fig. 3D feature importance is supported by code, but through a separate analysis path rather than the main Nextflow wrapper.

So the repository is useful for understanding how the benchmark was organized and for inspecting high-value implementation choices, but it is not a turnkey reproduction capsule for all paper results.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
