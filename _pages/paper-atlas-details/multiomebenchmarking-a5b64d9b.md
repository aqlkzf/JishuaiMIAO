---
layout: default
permalink: /paper-atlas/multiomebenchmarking-a5b64d9b/
title: "MultiomeBenchmarking"
nav: false
description: "单细胞多组学实验可以在同一个细胞中同时测量 RNA、蛋白丰度或染色质可及性，但成本高、数据稀疏、批次差异明显。因此研究者常用两类计算方法： 缺失模态预测：只有 RNA 时，预测蛋白丰度或 ATAC 峰可及性。 多组学整合：把不同模态、不同批次或模态不完整的数据映射到统一的低维空间。 问题在于，已有算法通常只在各自论文或少量竞赛数据上验证，数据集、预处理、指标和任务定义不一致，难以判断“哪种方法适合我的数据”。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Methods · 2024</span>
    </div>
    <h1>MultiomeBenchmarking</h1>
    <p>Benchmarking algorithms for single-cell multi-omics prediction and integration</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 单细胞多组学预测与整合算法基准：方法详解

### 1. 这篇论文解决什么问题？

单细胞多组学实验可以在同一个细胞中同时测量 RNA、蛋白丰度或染色质可及性，但成本高、数据稀疏、批次差异明显。因此研究者常用两类计算方法：

1. **缺失模态预测**：只有 RNA 时，预测蛋白丰度或 ATAC 峰可及性。
2. **多组学整合**：把不同模态、不同批次或模态不完整的数据映射到统一的低维空间。

问题在于，已有算法通常只在各自论文或少量竞赛数据上验证，数据集、预处理、指标和任务定义不一致，难以判断“哪种方法适合我的数据”。这篇论文的贡献不是提出一个新模型，而是建立一个覆盖面很广的统一基准。

论文比较了 14 个预测算法和 18 个整合算法，共 27 个不同算法，使用 47 个数据集。代表性方法包括 Seurat（*Cell*, 2019）、LIGER（*Cell*, 2019）、totalVI（*Nature Methods*, 2021）、scArches（*Nature Biotechnology*, 2022）、scVAEIT（*PNAS*, 2022）和 MultiVI（*Nature Methods*, 2023）。

### 2. 基准的总体结构

```text
47 个单细胞数据集
    │
    ├── 质量控制、特征对齐、细胞类型标签统一
    │
    ├── 模态预测
    │     ├── RNA → 蛋白
    │     ├── RNA → ATAC
    │     ├── 同数据集：80% 训练 / 20% 测试
    │     └── 跨数据集：同组织或器官的两个数据集分别训练和测试
    │
    └── 多组学整合
          ├── 垂直整合：同一细胞测量多个模态
          ├── 水平整合：相同模态组合的多个批次
          └── 马赛克整合：不同数据集只共享部分模态

预测矩阵或联合嵌入
    ↓
逐数据集计算指标
    ↓
跨数据集平均、标准差、BVC、BER、RI
    ↓
按任务、数据稀疏度和计算资源给出算法建议
```

图 1 直接展示了这个结构，也显示了数据规模和稀疏度差异：RNA 矩阵通常已经很稀疏，而 ATAC 峰矩阵的稀疏度经常达到 0.92–0.99。这一点解释了为什么 RNA→ATAC 比 RNA→蛋白更困难。

### 3. 数据预处理

数据包括 RNA+蛋白、RNA+ATAC、三组学、RNA-only 和 ATAC-only 数据，来自 CITE-seq、REAP-seq、SHARE-seq、SNARE-seq、10x Multiome、TEA-seq、inCITE-seq 和 DOGMA-seq 等技术。

- 质量控制遵循原始数据论文，并使用 Seurat 框架过滤低质量细胞和低频特征。
- scATAC 峰调用依技术而定：SNARE-seq 使用 cisTopic，10x 体系使用 Cell Ranger，SHARE-seq 使用 MACS2。
- 跨数据集 ATAC 预测需要统一峰集合，因此使用 Signac 合并不同数据集独立得到的 peaks。
- 整合评估依赖细胞类型标签；对于不同数据集命名不一致的亚型，作者会合并成共同标签。

### 4. 模态预测任务

#### 4.1 同数据集与跨数据集

**同数据集场景**：随机抽取 80% 细胞训练、20% 细胞测试。

**跨数据集场景**：使用同一组织或器官的一个数据集训练，另一个数据集测试。模型只看到测试集 RNA，蛋白或 ATAC 只作为评估真值。

代码中的 totalVI 示例清楚实现了这一逻辑：合并训练/测试批次，将测试批次的蛋白矩阵置零，选择 4,000 个高变基因，训练 TOTALVI，然后输出测试细胞的蛋白预测。

#### 4.2 PCC

PCC 衡量预测值与真值的线性相关。作者分别计算：

- **cell–cell PCC**：对每个细胞，在所有蛋白或 peaks 上比较预测与真值。
- **protein–protein / peak–peak PCC**：对每个蛋白或 peak，在所有细胞上比较预测与真值。

PCC 越高越好。每个数据集先对细胞或特征取中位数，再跨数据集计算均值和标准差。

#### 4.3 CMD

CMD 比较预测矩阵和真值矩阵所形成的相关矩阵：

$$
d(&#123;&#123;{\boldsymbol{R}}}}_{1},&#123;&#123;{\boldsymbol{R}}}}_{2})=1-\frac{\rm{trace}(&#123;&#123;{\boldsymbol{R}}}}_{1}&#123;&#123;{\boldsymbol{R}}}}_{2})}&#123;&#123;\Vert &#123;&#123;{\boldsymbol{R}}}}_{1}\Vert }_{F}{\Vert &#123;&#123;{\boldsymbol{R}}}}_{2}\Vert }_{F}}
$$

它关注的不是单个数值，而是细胞–细胞或特征–特征关系是否被保留。CMD 越低越好。仓库中的 `Matrics.py` 实现了同样的 trace/Frobenius 形式。

#### 4.4 RMSE 与 AUROC

RMSE 衡量预测矩阵与真值矩阵的数值误差，越低越好。AUROC 用于 ATAC 的二分类可及性判断，1 表示完美，0.5 接近随机。

#### 4.5 排名指数 RI

RI 不是普通名次，而是“在多少个指标上进入前 50%”的计数：

$$
{\rm RI}_i=\sum_j B(v_{ij}).
$$

对于 PCC、AUROC 等越高越好的指标，算法值高于所有算法中位数时记 1；对于 CMD、RMSE 等越低越好的指标，低于中位数时记 1。RI 的优点是能综合多个指标，缺点是忽略领先幅度，并且对参与比较的方法集合敏感。

**代码状态：Not found。** 在 117 个索引代码文件和相关指标脚本中没有找到 RI 的可执行实现。

### 5. 多组学整合任务

#### 5.1 三类整合

- **垂直整合**：同一批细胞同时测量 RNA+蛋白或 RNA+ATAC，重点是保留细胞类型结构。
- **水平整合**：多个批次具有相同模态组合，既要保留生物差异，也要去除批次效应。
- **马赛克整合**：不同数据集只共享部分模态。论文区分四种子场景，例如 RNA-only 与 RNA+蛋白、ATAC-only 与 RNA+ATAC 等。

#### 5.2 BVC：生物学变异保留

BVC 汇总 ARI、NMI、cASW、cLISI 和 ILS。垂直整合只有一个批次，不使用 ILS。

- ARI/NMI：整合后聚类与已知细胞类型的一致性。
- cASW/cLISI：细胞类型是否在嵌入空间中保持清晰结构。
- ILS：只出现在少数批次中的细胞类型是否仍能形成合理结构。

#### 5.3 BER：批次效应去除

BER 是 kBET、KNN connectivity、bASW、iLISI 和 PCR 的平均值，经转换后统一为越高越好。

这两个分数必须一起看：只追求混合批次可能抹掉真实生物差异，只追求细胞类型分离又可能保留批次偏差。图 5 和图 6 的二维散点图正是用 BVC–BER 平面展示这种权衡。

代码中的 `ComputeMetrics.py` 把不同方法的嵌入写入 `AnnData.obsm`，用 batch 和 cell type 初始化 `scib_metrics.Benchmarker`，再补充最优分辨率下的 ARI/NMI，输出 `metrics.csv` 和图表。大部分指标细节由外部 scIB/scib-metrics 库完成。

### 6. 关键实验结果

#### 蛋白预测

totalVI 和 scArches 的综合表现最好，整体 RI 分别为 10 和 7。某些算法会在单个蛋白或单一指标上领先，但 totalVI 的跨指标平衡最好。所有方法对 RNA-uncorrelated 蛋白明显更差，说明 RNA 本身没有足够信息时，模型无法凭空恢复蛋白信号。

#### 染色质可及性预测

LS_Lab 整体最好，MultiVI、scVAEIT 和 LIGER 也较强。但所有算法的原始 peak–peak PCC 都偏低。把 peaks 聚合成 DORCs，或者在测试集上用 30 维 LSI 和 50 邻居进行 KNN 平滑后，结果显著改善。这说明参考 ATAC 矩阵的极端稀疏性是主要瓶颈。

#### 垂直整合

- RNA+蛋白：Seurat、MOJITOO 最强。
- RNA+ATAC：scAI、MOJITOO、MultiVI 在不同指标上领先。

#### 水平整合

- RNA+蛋白：totalVI 最平衡。
- RNA+ATAC：UINMF 是唯一在关键 BVC/BER 比较中同时高于中位数的方法，并获得最高 RI。

#### 马赛克整合

- RNA 与 RNA+蛋白：totalVI、scArches 最强。
- 其他缺失模态组合：UINMF 和 MultiVI 更突出。
- 在能覆盖全部四种子场景的方法中，UINMF 的总 RI 最高。

### 7. 稳健性与计算资源

论文还系统改变训练细胞数、RNA 特征数、训练/测试细胞类型重叠、ATAC 平滑方式和数据规模。

- 增加训练细胞通常同时改善蛋白和 ATAC 预测。
- 增加 RNA 特征有助于蛋白预测，但对 ATAC 预测帮助不稳定。
- 训练集与测试集越接近同组织、同细胞类型，效果越好。
- totalVI、LS_Lab、Seurat、MultiVI 和 UINMF 等优胜方法在测试规模下可在 6 小时内、256 GB 内存以内完成；但 scArches 和 scAI 在超大细胞数时出现内存问题。

### 8. 如何使用这篇基准

不要只看一个总排名。更合理的流程是：

1. 先确定任务是预测、垂直、水平还是哪一种马赛克整合。
2. 匹配数据模态、组织关系、批次结构和稀疏度。
3. 同时查看 cell-level、feature-level、BVC、BER 和资源指标。
4. 在自己的数据上做小规模验证，再决定是否投入完整训练成本。

### 9. 代码与复现性判断

代码–论文一致性为 **medium**。

已验证：

- 目录结构覆盖预测、垂直、水平和马赛克整合。
- totalVI 的关键参数与论文一致。
- RNA→ATAC 的 PCC、CMD、RMSE、AUROC 有直接实现。
- 整合评估使用 scIB/scib-metrics，并明确使用 batch/cell-type 标签。

主要缺口：

- RI 实现 **Not found**。
- 蛋白预测指标主要位于 Notebook。
- 没有统一的顶层命令串联 47 个数据集、27 个算法和全部图表。
- 数据来自多个外部平台，环境高度碎片化，完整复现实验需要大量 CPU/GPU 和内存。
- `SUPP_MD` 为 **MISSING**；本分析使用完整主文、六张主图和直接代码行作为证据。

因此，这个仓库适合理解作者如何调用各算法并复核部分指标，但不是开箱即用的一键基准系统。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Benchmarking Algorithms for Single-Cell Multi-Omics Prediction and Integration

### Problem

Single-cell multi-omics methods can jointly measure RNA with protein abundance or chromatin accessibility, but these assays remain expensive, sparse, and less common than RNA-only profiling. Many algorithms therefore either predict a missing modality from RNA or integrate multiple modalities and batches. Before this study, comparisons were fragmented across individual method papers and the NeurIPS 2021 multimodal challenge (reported in PMLR, 2022), with limited coverage of biological datasets, integration scenarios, robustness, and computational cost.

The paper benchmarks 14 protein/chromatin prediction algorithms and 18 integration algorithms—27 distinct methods in total—using 47 datasets. Representative prior methods include Seurat (*Cell*, 2019), LIGER (*Cell*, 2019), totalVI (*Nature Methods*, 2021), scArches (*Nature Biotechnology*, 2022), scVAEIT (*PNAS*, 2022), and MultiVI (*Nature Methods*, 2023).

### Benchmark contribution

The contribution is a common evaluation framework rather than a new predictive model. It covers:

- RNA→protein and RNA→ATAC prediction under intra-dataset 80/20 splits and inter-dataset transfer between matched tissues/organs.
- Vertical integration of modalities measured in the same cells.
- Horizontal integration across batches.
- Mosaic integration across four incomplete-modality patterns.
- Accuracy, biological conservation, batch removal, stability, training-set composition, sparsity, runtime, and memory.

Prediction is evaluated with cell- and feature-level PCC, correlation matrix distance (CMD), RMSE, and—for ATAC—AUROC. Integration uses ten scIB-style metrics grouped into biological variation conservation (BVC) and batch effect removal (BER). A median-threshold rank index (RI) counts how many metric/scenario comparisons place a method in the top half.

### Main findings

- **Protein prediction:** totalVI and scArches are the strongest balanced choices. Their overall RI values are 10 and 7, respectively. Individual methods can still win specific proteins or metrics.
- **Chromatin prediction:** LS_Lab is strongest overall, followed by MultiVI, scVAEIT, and LIGER. Raw peak-level agreement remains weak for every method; DORC aggregation and KNN smoothing substantially improve peak-level PCC, showing that reference sparsity is a dominant difficulty.
- **Vertical integration:** Seurat and MOJITOO lead RNA+protein; scAI, MOJITOO, and MultiVI lead RNA+ATAC by complementary clustering and geometry-preservation metrics.
- **Horizontal integration:** totalVI leads RNA+protein, while UINMF is the most balanced RNA+ATAC method.
- **Mosaic integration:** totalVI/scArches lead RNA with RNA+protein. UINMF is the most versatile method across all four mosaic subcases and has the largest total RI.
- **Limits of predictability:** all methods struggle on RNA-uncorrelated proteins and on sparse raw ATAC peaks. More training cells and closer cell-type/tissue matching generally help.
- **Compute:** several top methods finish tested tasks within 6 hours and under 256 GB memory, but scArches and scAI encounter memory limits at the largest tested sizes.

### What the code provides

The public `QuKunLab/MultiomeBenchmarking` snapshot contains method-specific wrappers, environment files, saved results, comparison notebooks, and an integration metric script. Direct code reads verify representative totalVI prediction and mosaic-integration workflows, the paper’s totalVI parameter choices, RNA→ATAC PCC/CMD/RMSE/AUROC computations, and scIB-based integration evaluation.

Code-paper fidelity is **medium**:

- Exact or strong matches exist for the benchmark task layout, representative wrappers, totalVI settings, and core metric formulas.
- The repository is example-oriented and fragmented across scripts/notebooks rather than driven by one manifest or top-level runner.
- The paper’s RI implementation was **Not found** in the 117 indexed code files.
- Protein comparison/aggregation is notebook-based, and some normalization/aggregation details are only partially visible in inspected code.
- Raw datasets are external and the full 47-dataset benchmark requires many independent environments plus large CPU/GPU resources.

### Reproducibility assessment

**3/5 — public and substantially inspectable, but not turnkey.**

Strengths:

- Public GitHub and Zenodo code availability.
- Recorded repository commit and branch.
- Broad per-method wrapper coverage and declared package versions.
- Local main figures and complete main article.

Gaps:

- No single end-to-end command for all experiments and figures.
- RI code **Not found**.
- Supplementary Markdown **MISSING**; supplementary PDF/tables remain externally linked.
- Full runtime reproduction was not attempted because of external data, environment fragmentation, and compute demands.

### Practical reading

The benchmark’s recommendations are best treated as scenario-specific priors, not universal rankings. Choose methods using the closest modality pattern, tissue/batch relationship, sparsity regime, and compute budget, then inspect the underlying metric trade-offs rather than relying only on RI.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
