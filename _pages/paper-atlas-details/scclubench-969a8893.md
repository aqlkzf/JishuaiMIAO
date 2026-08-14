---
layout: default
permalink: /paper-atlas/scclubench-969a8893/
title: "scCluBench"
nav: false
wide: true
description: "scRNA-seq 聚类的目标是把表达谱相似的细胞分到同一簇，从而辅助细胞类型识别、marker gene 发现和下游注释。论文指出，已有基准通常只覆盖少数方法或单一评价维度，数据、预处理、输出格式和生物学验证也不统一，因此很难公平比较鲁棒性、可扩展性和实际生物学价值。 scCluBench 是一个基准框架，不是一个新的单一聚类模型。它收集 36 个来自人和小鼠、覆盖 18 种组织的 ."
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
      <span>Domain Clustering</span>
      <span>AAAI · 2026</span>
    </div>
    <h1>scCluBench</h1>
    <p>scCluBench: Comprehensive Benchmarking of Clustering Algorithms for Single-Cell RNA Sequencing</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/XPgogogo/scCluBench" target="_blank" rel="noopener noreferrer" aria-label="Open code for scCluBench">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scCluBench 方法解读

### 1. 它要解决什么问题

scRNA-seq 聚类的目标是把表达谱相似的细胞分到同一簇，从而辅助细胞类型识别、marker gene 发现和下游注释。论文指出，已有基准通常只覆盖少数方法或单一评价维度，数据、预处理、输出格式和生物学验证也不统一，因此很难公平比较鲁棒性、可扩展性和实际生物学价值（`paper.md:14-20,287-293`）。

scCluBench 是一个基准框架，不是一个新的单一聚类模型。它收集 36 个来自人和小鼠、覆盖 18 种组织的 `.h5ad` 数据集，并比较四类方法：传统聚类、深度学习聚类、图聚类和生物学基础模型（`paper.md:51-94,308-360`）。本次分析使用的是 arXiv `2512.02471` 的 HTML 转换稿，因为 AAAI 页面没有得到可用 HTML；代码仓库 README 同时混用了 `scCluBench`、`scBench` 和 `scUnified` 身份，不能把 README 的引文当成唯一来源。

### 2. 输入、输出和整体流程

每个数据集的输入是 AnnData 对象：基因名在 `data.var["feature_name"]`，细胞真值类型在 `data.obs["cell_type"]`，表达矩阵由 `data.to_df()` 得到（`paper.md:362-376`）。方法输出每个细胞的聚类标签；学习 embedding 的方法还输出细胞表示。基准层再计算指标、画 embedding 图、分析 marker gene，并比较两种细胞类型注释策略。

```text
36 个 .h5ad 数据集
        |
        v
统一预处理：检查状态 -> 归一化 -> size factor -> log1p -> scaling
        |
        v
运行传统 / 深度学习 / 图 / 基础模型
        |
        +--> 聚类标签 + 可选 latent embedding
        +--> ACC, NMI, ARI（代码还返回 F1/FMI/V-measure 等）
        +--> t-SNE 与成对 cosine similarity 分布
        +--> 每簇 top-100 DEG -> top-3/top-10 marker 图
        +--> best-mapping 与 marker-overlap -> Sankey
        +--> 5 个随机种子的均值、标准差、效率和稳定性
```

五次重复、均值和标准差是论文实验协议（`paper.md:91-94,451-458`）。本地代码中没有找到能够一次性调度 36 个数据集、所有方法和五次运行的完整入口，因此上图的“基准层”是论文流程，而不是已经在本地端到端验证的执行轨迹。

### 3. 统一预处理

论文的预处理先判断数据是否已经归一化、log1p 变换和标准化；缺少时执行 library-size normalization，计算每个细胞的 size factor，对未变换数据进行 log1p，最后做 z-score scaling（`paper.md:379-383`）。数据本身很异质：整体稀疏率 65.76%-95.42%，有两个数据集超过 20,000 个细胞，五个数据集超过 60,000 个基因（`paper.md:308-360`）。

代码中 `prepare_data_for_model` 读取 h5ad，调用 `normalize_sc`，返回 `(X, Y, sf, data)`（`preprocess.py:203-233`）。`normalize_sc` 在没有 `adata.raw` 时保存原始对象；开启过滤时选择最多 1,000 个 highly variable genes；从 `n_counts` 或 `total_counts` 计算 size factor；再按当前状态执行 per-cell normalization、log1p 和 scaling（`preprocess.py:149-199`）。这些是直接核验的代码行为，但不能据此断言论文中的每一个 baseline 都使用了同一份实现。

### 4. 四类模型

| 类别 | 方法 | 主要思想 |
|---|---|---|
| 传统 | SC3、Louvain、Leiden | 共识聚类或图 modularity/community detection。 |
| 深度学习 | DEC、DESC、scDeepCluster、scMAE、scNAME、scDCC、scziDesk | 通过自编码器、掩码重建、自训练或领域约束学习适合聚类的表示。 |
| 图方法 | scGNN、scDSC、AttentionAE-sc、scCDCG | 将细胞间图结构和自编码器表示结合；scCDCG 进一步使用 cut-informed soft graph 与 optimal-transport 自监督。 |
| 基础模型 | scGPT、GeneFormer、GeneCompass | 提取 Transformer 表示后用 K-means 聚类；另做 8:2 划分的分类微调。 |

论文的 Appendix D 给出具体超参数，例如 scDeepCluster 先用 400 个 epoch 预训练，scMAE 以 0.4 的基因掩码率训练并在第 80 个 epoch 聚类，scGNN 进行图/EM 迭代，scCDCG 使用 16 维表示、$λ=5$、$θ=1$（`paper.md:481-511`）。它们是论文的实验规格；本地快照并不保证所有规格都能从 wrapper 完整复原。

### 5. 代码中可以直接看到的执行路径

#### scDeepCluster

`DeepLearning/scDeepCluster/run.py:37-78` 暴露数据路径、簇数、维度、噪声、预训练和聚类迭代次数、batch size 及 loss 权重。主函数在 `run.py:81-179` 中调用统一预处理，把标签编码成整数，从 `adata.raw` 获取 raw counts，建立 `[输入基因数]+隐藏层` 维度，用 AMSGrad Adam 预训练自编码器，再用 Adadelta 拟合聚类模型，抽取 embedding，最后调用 `save`。这是一个具体深度模型的代码证据，不代表所有方法的内部算法。

#### scGNN

`GNN/scGNN/run.py:143-265` 先设定设备和随机种子，调用相同的预处理 helper，训练 AE/VAE 得到初始表示；然后构建 KNN 图（失败时退回简单 KNN），执行多轮 EM 式聚类、再训练和图更新，最后 K-means 并调用 `save`。这证明仓库有图方法 wrapper，但没有证明论文中的全部 scGNN 实验配置或五次表格汇总流程在本地可重跑。

#### 指标和结果文件

`evaluation.py:79-102` 用 `linear_sum_assignment` 对预测标签做 Hungarian 对齐；`evaluation.py:104-120` 返回 ACC、NMI、ARI、macro-F1、FMI、V-measure、homogeneity、completeness 以及对齐后的标签。`utils.py:9-47` 将这些结果写成 `metrics_<epoch>.json`、`embedding.h5`、`embedding_<epoch>.npy` 和 `types_<epoch>_pred.csv`。README 中的 `metrics.json`、`embedding.npy`、`pred.npy` 是简化描述，文件名并不完全一致。

### 6. 评价指标和表示质量

论文主要使用 ACC、NMI、ARI（`paper.md:103-109,541-577`）。给定真值划分 $U$、预测划分 $V$ 和 $n$ 个细胞：

- **ACC** 在所有一一映射 $m$ 中取最佳值，并用 Hungarian algorithm 求解：
  $$\text{ACC}=\max_{m}\frac{\sum_{i=1}^{n}1{l_{i}=m(u_{i})}}{n}.$$
- **NMI** 衡量 $U$ 和 $V$ 的互信息，并按两者熵的平均值归一化（`paper.md:560-567`）。
- **ARI** 统计成对样本的一致性并进行机会校正，忽略簇标签置换（`paper.md:570-577`）。
- **Macro-F1** 对每个类别独立算 F1 后取平均，避免大类完全主导分数（`paper.md:580-590`）。

定性分析包含 t-SNE 和 embedding 两两 cosine similarity。相似度分布大量集中在高值区域时，论文将其解释为 over-smoothing 或 representation collapse；低相似度的蓝/白区域则代表更可区分的表示（`paper.md:109,215-234`）。图像证据支持这一视觉判断，但不是一个由代码定义的硬阈值。

### 7. 生物学解释

论文用 Scanpy `rank_genes_groups` 为每个真值簇提取 top-100 DEG，作为 gold-standard marker list；对预测簇做同样处理，再用 tracksplot 展示 top-3 或 top-10 marker（`paper.md:112-121,716-720`）。

两种注释方法的区别是：

1. **Best-mapping**：只按标签计数，用 Hungarian 一一匹配预测簇和真值类型，不读取表达量。
2. **Marker-overlap**：对预测簇 $p$ 和真值簇 $g$ 计算
   $$\text{score}(p,g)=|\text{DEG}_{p}\cap\text{DEG}_{g}|/100,$$
   并把 $p$ 赋给得分最高的真值类型。

Sankey 图把预测簇、两种注释结果和 gold-standard 类型串起来，从流的合并、分叉和交叉处观察误注释（`paper.md:121,243-284,728-731`）。仓库的 `analysis/deg_acc.py:4-62` 读取 link JSON 计算聚类/注释准确率和增益，`analysis/sankey.py:7-55` 读取 node/link JSON 渲染 Sankey；这些输入文件和端到端执行命令在本地搜索范围内没有找到。

### 8. 结果与局限

论文 Table 2 的平均 ACC 中 scCDCG 为 81.29%（第 1 名），scMAE 为 78.24%（第 2 名）；论文将前者归因于 cut-informed soft graph，将后者归因于 masked reconstruction 的鲁棒性（`paper.md:124-166,194-197`）。基础模型的 clustering 明显弱于 classification，说明通用预训练表示并不等价于聚类目标优化（`paper.md:169-203`）。在质量、效率和稳定性三部分同时通过的严格标准下，论文只报 scMAE 和 scCDCG 通过；稳定性标准是至少五个 seed 的标准差 <5%，跨环境变化 <2%（`paper.md:734-795`）。

论文还记录 AttentionAE-sc 在两个 retina 数据集 OOM、scziDesk 在 Muris Brain OOM、scDCC 在 QS Limb Muscle 出现 NaN loss（`paper.md:206-209`）。需要保留的实现缺口包括：本地没有发现 SC3/Louvain/Leiden 或 scGPT/GeneFormer/GeneCompass 的等价 runner，没有完整 benchmark scheduler，数据资产和模型权重也不在搜索范围内；因而本地代码适合学习接口和部分模型路径，但不能单凭快照声称可以重建全部论文表格与图。

### 9. 证据边界

- **论文事实：** 数据规模、方法清单、实验超参数、指标定义、图表结果和稳定性结论来自 `paper.md`。
- **代码事实：** h5ad 字段、预处理操作、指标实现、写文件行为，以及 scDeepCluster/scGNN 路径来自上述直接源代码行。
- **解释性结论：** scCDCG 的图表示更清晰、基础模型更偏向分类是论文的 benchmark interpretation，不是本次运行得到的因果验证。
- **未找到：** 完整调度器、传统/基础模型本地 runner、所有数据和五次运行的可复现命令；这些缺口以 `Not found` 保留。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scCluBench Summary

### Problem

scCluBench asks how single-cell RNA-seq clustering methods compare when datasets, preprocessing, outputs, metrics, and biological interpretation are standardized. Earlier benchmarks often covered only one method family or one assessment dimension; this makes robustness, scalability, and downstream biological value hard to compare fairly (paper.md:14-20,287-293).

The analyzed source is the arXiv preprint `2512.02471`, used as a fallback because usable AAAI article HTML was unavailable.

### Prior-method limitations

- Traditional methods such as SC3 (*Nature Methods*, 2017), Louvain/Leiden via Seurat (*Cell*, 2019) are simple and interpretable but the paper reports weaker performance as cell count, dimensionality, sparsity, and noise rise.
- Deep methods such as DESC (*Nature Communications*, 2020), scDeepCluster (*Nature Machine Intelligence*, 2019), and scMAE (*Bioinformatics*, 2024) learn denoised representations, but can be unstable, ignore cell-cell structure, or produce cluster counts that disagree with annotations.
- Graph methods such as scGNN (*Nature Communications*, 2021) model cell relationships but depend on graph construction and may over-smooth embeddings.
- Foundation models such as scGPT (*Nature Methods*, 2024), GeneFormer (*Nature*, 2023), and GeneCompass (*Cell Research*, 2024) transfer broadly, but their general-purpose representations are not explicitly optimized for clustering (paper.md:188-224,285-293,888-940).

### Benchmark design

scCluBench curates 36 human and mouse datasets spanning 18 tissues, with sparsity from 65.76% to 95.42%, two datasets above 20,000 cells, five above 60,000 genes, and multiple sequencing technologies (paper.md:85-90,308-360). It compares 14 conventional clustering methods across traditional, deep-learning, and graph families, and separately evaluates three foundation models for clustering and classification (paper.md:64-94,169-185).

Each `.h5ad` dataset supplies a cell-by-gene matrix and `obs['cell_type']` ground truth. The paper standardizes normalization, size factors, log1p, and scaling; each dataset-method pair is run five times. Outputs are evaluated with ACC, NMI, and ARI, t-SNE views, and pairwise cosine-similarity distributions. A biological layer extracts top-100 DEGs, compares marker overlap, contrasts Hungarian best-mapping with marker-based annotation, and visualizes flows with Sankey diagrams (paper.md:100-121,362-383,451-458).

### Main findings

- scCDCG has the highest average ACC in Table 2 (81.29%, rank 1), followed by scMAE (78.24%, rank 2). The paper attributes scCDCG’s result to cut-informed soft graph embeddings and scMAE’s robustness to masked reconstruction (paper.md:124-166,194-197).
- Embedding plots and similarity histograms show distinct failure modes: DESC can produce the wrong apparent cluster count, while several graph methods concentrate embeddings at high similarity; scCDCG is presented as the graph exception with clearer separation (paper.md:215-234,704-713).
- Foundation-model clustering is substantially weaker than supervised classification on the tested datasets, supporting the interpretation that general-purpose pretraining does not substitute for a clustering-specific objective (paper.md:169-203).
- Marker-overlap annotation improves mean ACC over best-mapping for most method/dataset combinations and exposes biologically meaningful corrections, but very rare pancreatic endothelial/epsilon populations remain difficult (paper.md:240-284).
- Under the paper’s combined quality, efficiency, and stability criteria, only scMAE and scCDCG pass all dimensions. The extended protocol itself has a duplicated ACC threshold and no clearly stated separate NMI threshold, which limits exact reproduction of that gate (paper.md:734-795).

The paper also records concrete failure cases: AttentionAE-sc runs out of memory on two retina datasets, scziDesk runs out of memory on Muris Brain, and scDCC produces a NaN loss on QS Limb Muscle (paper.md:206-209).

### Code and reproducibility

The local snapshot is `https://github.com/XPgogogo/scCluBench` at commit `5a92318416f931397487d8f80c4868e6b8ee912f`. Paper-code fidelity is **medium**. Direct code reads verify a shared h5ad preprocessing helper, Hungarian-aligned ACC plus NMI/ARI and five additional metrics, epoch-specific metric/embedding/prediction outputs, and adoption of these helpers by all 11 inspected deep-learning/GNN runners (`preprocess.py:149-233`, `evaluation.py:79-120`, `utils.py:9-47`; see `doc_code.md`).

Reproduction is incomplete from this snapshot alone:

- `run_template.py` is an interface skeleton whose model section is commented out.
- No equivalent local runners were found for the three traditional methods or three foundation models.
- No verified benchmark-wide command schedules all 36 datasets, five seeds, aggregation, tables, and figures.
- Dataset assets, environment lockfiles for the full benchmark, and generated intermediate analysis inputs are absent from the searched scope.
- The root code README’s scBench/scUnified identity and simplified output filenames do not exactly match the acquired paper or writer implementation.

**Reproducibility rating: 3/5.** The snapshot is valuable for inspecting standardized interfaces and multiple model wrappers, but a faithful end-to-end regeneration requires missing datasets, orchestration, and traditional/foundation-model execution assets.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
