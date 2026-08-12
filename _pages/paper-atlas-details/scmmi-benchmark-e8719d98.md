---
layout: default
permalink: /paper-atlas/scmmi-benchmark-e8719d98/
title: "SCMMI Benchmark"
nav: false
description: "SCMMI Benchmark 不是一个新的整合模型，而是一个用于选择单细胞多模态整合方法的基准框架：它把不同数据设定拆成多个任务，统一运行或汇总方法输出，再用共享指标做任务条件下的推荐。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>SCMMI Benchmark</h1>
    <p>Benchmarking single-cell multi-modal data integrations</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02737-9" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SCMMI Benchmark 方法中文解读

### 一句话概览

SCMMI Benchmark 不是一个新的整合模型，而是一个用于选择单细胞多模态整合方法的基准框架：它把不同数据设定拆成多个任务，统一运行或汇总方法输出，再用共享指标做任务条件下的推荐。

### 1. 生物学问题与建模目标

单细胞多模态数据可能同时或分别测量 RNA、ATAC、ADT/protein 和空间位置。真实问题不是“哪个方法全局最好”，而是在 paired、unpaired、mosaic 或 spatial 场景下，哪个工具能保留细胞类型结构、消除批次效应、对齐跨模态细胞、补全缺失模态，并且能在可接受资源下运行。

### 2. 输入、输出与关键状态变量

| 元素 | 含义 | 代码/文档锚点 |
|---|---|---|
| RNA 矩阵 | 细胞 x 基因表达 | `doc_method.md` |
| ATAC 矩阵 | 细胞 x peak 开放性 | `doc_method.md` |
| ADT/protein | 表面蛋白丰度 | `doc_method.md` |
| GAM | ATAC peak 到 gene-level proxy | `Get_GAM.R` |
| Joint embedding | paired 数据的共同低维表示 | `doc_code.md` |
| Imputation matrix | 缺失模态预测矩阵 | `metrics.py:743-1234` |
| Rank / score | min-max 后的指标汇总排名 | stage2 RMarkdown scripts |

### 3. 方法主流程

1. 定义六类任务：paired RNA+ATAC、paired RNA+ADT、spatial RNA+ADT、diagonal RNA+ATAC、mosaic RNA+ATAC、mosaic RNA+ADT。
2. 从公开数据构造 paired、pseudo-unpaired、mosaic 和 spatial benchmark。
3. 对需要共享特征空间的 RNA+ATAC 方法生成 GAM。
4. 用 `SCMMIB_pipeline/wdl_workflow/main.wdl` 分发不同方法 wrapper。
5. 收集 joint embedding、graph、modality-specific latent 或 imputation matrix。
6. 计算 biological conservation、batch removal、alignment、imputation、robustness、usability/scalability 指标。
7. 用 min-max score 和 rank aggregation 得到任务条件推荐。

### 4. 数学目标与直觉

Batch ASW 衡量同一细胞类型内部批次是否混合：

$$
batchASW_i = 1 - |silhouette_{batch}(i)|
$$

Graph connectivity 检查同一细胞类型在整合图中是否保持连通：

$$
GC = \frac{1}{|C|}\sum_{c \in C}\frac{LCC(subgraph_c)}{N_c}
$$

LISI 衡量局部邻域混合：

$$
LISI = \frac{1}{\sum_i p_i^2}
$$

最终 ranking 用 min-max score：

$$
score_i = \frac{metric_i - metric_{min}}{metric_{max} - metric_{min}}
$$

这些公式让不同量纲指标可以合并，但排名会依赖参与比较的方法集合和指标权重。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 匹配程度 |
|---|---|---|
| paired embedding metrics | `SCMMI_Benchmark/scmmib/metrics.py:241-338` | ✓ Exact |
| graph metrics | `SCMMI_Benchmark/scmmib/metrics.py:341-416` | ✓ Exact |
| unpaired/mosaic alignment | `metrics.py:30-92`, `419-740` | ✓ Exact |
| imputation metrics | `metrics.py:743-1234`; `knn_smooth.py:132-236` | ✓ Exact |
| WDL dispatcher | `SCMMIB_pipeline/wdl_workflow/main.wdl`; `taskit.wdl` | ✓ Exact |
| GAM preprocessing | `Get_GAM.R`; `Get_GAM_GeneActivity.R` | ✓ Exact |
| 全部 65 个 task-method manifest | 未找到单一完整 manifest | ✗ Not found |

### 6. 结果如何解读

图 1 说明 benchmark 的核心结构。图 2-6 分别展示 paired RNA+ATAC、paired/spatial RNA+ADT、diagonal RNA+ATAC、mosaic RNA+ATAC 和 mosaic RNA+ADT 的任务条件推荐。GLUE、MIDAS、totalVI、StabMap、Seurat v4/v5、SpatialGlue 等工具在不同任务和指标下各有优势。

这些排名应理解为论文 benchmark claim，而不是本工作区重新运行所有方法得到的结果。代码可验证的是指标、pipeline 和代表性 wrapper；完整排名依赖预计算 stage2 结果表和 RMarkdown 汇总脚本。

### 7. 局限性与未验证部分

- 未找到单一 manifest 直接证明全部 65 个 task-method 应用。
- 不是所有 wrapper 都逐行审计；已验证共享 WDL、metric package 和代表性 wrapper。
- raw data 到每个 final ranking table 的完整 provenance 分散在 preprocessing、WDL、precomputed result tables、metric code 和 RMarkdown 脚本中。
- pseudo-unpaired 任务依赖隐藏 true match，真实 unpaired cohort 可能更难。
- runtime/GPU 结论依赖硬件、`nvitop` 采样和具体 wrapper 行为。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SCMMI Benchmark

### Motivation and Novelty

Single-cell multimodal integration methods are used across RNA+ATAC, RNA+protein, spatial multiomics, unpaired, and mosaic data designs, but method papers usually evaluate different datasets and metrics. SCMMI Benchmark treats tool choice as a task-specific benchmarking problem rather than proposing another integration model.

The novelty is scope and structure: six integration settings, public multimodal datasets, 40 algorithms mapped to 65 integration method applications, and a unified evaluation framework spanning usability, accuracy, robustness, scalability, alignment, and imputation. The paper's practical contribution is a decision framework for method selection under modality, pairing, resource, and output constraints.

### Method Overview

The method is a benchmark framework:

1. Define task families: paired RNA+ATAC, paired RNA+ADT, spatial RNA+ADT, unpaired diagonal RNA+ATAC, mosaic RNA+ATAC, and mosaic RNA+ADT.
2. Curate public multimodal datasets and construct pseudo-unpaired or mosaic tasks when needed.
3. Preprocess inputs, including gene activity matrix generation for many diagonal RNA+ATAC methods.
4. Run method wrappers through a WDL-based execution pipeline.
5. Collect method outputs: joint embeddings, graph outputs, modality-specific aligned embeddings, and imputation matrices.
6. Score outputs using biological-conservation, batch-removal, cell-alignment, imputation, robustness, and usability/scalability metrics.
7. Normalize metric groups and rank methods by task.

Core equations include batch ASW, graph connectivity, LISI/iLISI/cLISI, ARI, AMI, min-max score normalization, and robustness rank aggregation. The local code verifies metric implementations in `SCMMI_Benchmark/scmmib/metrics.py` and `knn_smooth.py`, WDL dispatch in `SCMMIB_pipeline/wdl_workflow/`, and representative wrappers for MultiVI, GLUE, MIDAS, totalVI, and SpatialGlue.

### Compared Methods

Named comparison methods with journal/year metadata recorded in `claude_notes.md` include:

| Method | Role in Benchmark | Journal | Year |
|---|---|---|---|
| Seurat v4 WNN | Paired multimodal weighted-nearest-neighbor integration | Cell | 2021 |
| GLUE | Graph-linked unpaired RNA+ATAC embedding | Nature Biotechnology | 2022 |
| MIDAS | Mosaic integration and imputation | Nature Biotechnology | 2024 |
| MultiVI | Generative RNA+ATAC integration from scvi-tools | Nature Methods | 2023 |
| totalVI | RNA+protein generative model | Nature Methods | 2021 |
| StabMap | Stabilized mosaic integration | Nature Biotechnology | 2024 |
| MaxFuse | Weakly linked feature/spatial-multimodal alignment | Nature Biotechnology | 2023 |
| scIB | Benchmark metric framework reused for integration metrics | Nature Methods | 2022 |

The paper and pipeline include many additional task-specific methods; they are treated as benchmark scope rather than individually cited comparison rows here because this summary only expands methods whose journal/year metadata was audited.

### Evaluation

The benchmark evaluates four main performance dimensions:

- **Usability and scalability**: software/document/paper quality, executability, tutorial and function documentation, system restrictions, and time/memory/GPU behavior across dataset sizes.
- **Paired embedding accuracy**: biological conservation and batch removal using ARI, AMI, cLISI, graph connectivity, batch ASW, iLISI, and related scIB-style metrics.
- **Cell alignment**: FOSCTTM, true cell match, and cell-type match for unpaired diagonal and mosaic tasks.
- **Imputation and robustness**: Pearson correlation for RNA/ADT, AUROC/AUPR for ATAC, raw and kNN-smoothed ground truths, sequencing-depth downsampling, repeated runs, and paired-guide-size robustness for mosaic data.

Main figure claims are task-specific. Seurat v4 WNN is strong in paired RNA+ATAC; GLUE is the main diagonal RNA+ATAC recommendation; MIDAS is strong for mosaic integration and imputation; totalVI, bindSC, MaxFuse, StabMap, MultiVI, SpatialGlue, and Seurat v5 bridge are recommended under specific data/resource regimes. These rankings are paper/figure claims, not rerun results from this workspace.

### Reproducibility

Reproducibility rating: **3.5/5**. The reusable framework components are moderately strong to strong, but full benchmark rerun provenance is only moderate because some raw-to-final ranking paths remain distributed across precomputed result tables and scripts.

Strong local support:

- Metric code directly implements the central paired, unpaired, mosaic, graph, and imputation metric families.
- WDL files and task-specific wrappers show how benchmark methods are dispatched.
- Representative wrappers verify execution patterns for paired RNA+ATAC, diagonal RNA+ATAC, mosaic RNA+ATAC, paired/mosaic RNA+ADT, and spatial RNA+ADT.
- Figure summary scripts implement min-max scoring, AUC summaries, grouped averages, and plot-ready rankings.

Remaining gaps:

- No single verified manifest was found that proves every one of the 65 advertised task-method applications.
- Full raw-to-final-table provenance is distributed across preprocessing scripts, WDL runs, precomputed result tables, metric code, and RMarkdown figure scripts.
- Robustness downsampling generation was only partially traced across all datasets.
- Some resource measurements depend on live hardware, `nvitop` polling, WDL runtime logs, and method-specific environments.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
