---
layout: default
permalink: /paper-atlas/biollm-21c7d68a/
title: "BioLLM"
nav: false
wide: true
description: "单细胞基础模型（scFM）在模型结构、基因词表、输入长度、预处理和代码接口上差异很大，因此同一份 scRNA-seq 数据很难用统一方式切换模型和做公平比较。BioLLM 的贡献是一个标准化的软件框架和评测协议，而不是重新提出一种预训练目标。 论文把框架分成三部分：配置/任务管理、模型加载接口、数据处理与评测。配置文件指定 modelused、设备、词表、检查点、任务类型和预处理参数。"
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
      <span>Representation Models</span>
      <span>Patterns · 2025</span>
    </div>
    <h1>BioLLM</h1>
    <p>BioLLM: A standardized framework for integrating and benchmarking single-cell foundation models</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.patter.2025.101326" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for BioLLM">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/BGIResearch/BioLLM" target="_blank" rel="noopener noreferrer" aria-label="Open code for BioLLM">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## BioLLM 方法讲解

### 它解决什么问题

单细胞基础模型（scFM）在模型结构、基因词表、输入长度、预处理和代码接口上差异很大，因此同一份 scRNA-seq 数据很难用统一方式切换模型和做公平比较。BioLLM 的贡献是一个标准化的软件框架和评测协议，而不是重新提出一种预训练目标。

### 核心架构

论文把框架分成三部分：配置/任务管理、模型加载接口、数据处理与评测（`paper.md:99-155`）。配置文件指定 `model_used`、设备、词表、检查点、任务类型和预处理参数。`BioTask` 读取配置并选择 scGPT、Geneformer、scFoundation、scBERT、CellPLM 等 loader；`LoaderBase` 规定加载预训练权重和提取 embedding 的接口；`DataHandler` 负责 AnnData 检查、基因词表过滤、归一化、log1p、HVG 选择以及 PyTorch Dataset/DataLoader。

```text
AnnData + 配置 + checkpoint
          |
          v
BioTask: 解析配置 -> 选择模型 loader -> 加载模型/词表
          |
          v
DataHandler: raw X -> 基因 ID/词表过滤 -> 归一化/log1p -> HVG
          |
          v
零样本 embedding 或监督微调
          |
          v
ASW/批次混合 | GRN/GO | accuracy/precision/recall/macro-F1 | PCC/SRCC
```

### 具体任务

- **细胞 embedding**：按模型预训练条件处理输入。论文中 Geneformer/scGPT 使用 3,000 个 HVG，scBERT/scFoundation 通常使用全基因；scGPT、scBERT、scFoundation 使用 log1p，Geneformer 使用 raw counts（`paper.md:159-162`）。评测细胞类型分离和批次效应的 ASW。
- **GRN**：从基因 embedding 计算余弦相似度邻接矩阵，再做 Leiden 社区发现和 BP/MF/CC 的 GO 富集；分辨率为 0.1-1.0，校正后 *p* < 0.01（`paper.md:163-165,183-185`）。
- **细胞类型注释**：8:2 train/test，再将训练集 8:2 划分 train/validation；统一 20 epochs，学习率按模型设定，报告 accuracy、precision、recall、macro-F1（`paper.md:167-169,187-189`）。
- **药物反应**：用 scFM embedding 替换 DeepCDR 的表达特征，与药物图、突变和甲基化特征联合预测 IC50，使用 PCC 和 SRCC（`paper.md:171-173,191-195`）。

### 结果与理解

scGPT 在细胞分离、注释和稀有细胞类型识别方面总体最好，但批次校正并不总是理想；Geneformer 和 scFoundation 在基因层面任务有优势；scBERT 整体较弱。Geneformer 在运行时间和 GPU 使用上较高效，scFoundation 更占显存。微调通常改善 embedding 和注释结果（`paper.md:45-89`；图 2-6）。

### 代码核查与限制

直接检查 GitHub 快照后，`BioTask` 的模型分派、`DataHandler` 的过滤/归一化、细胞 embedding、GRN 和 DeepCDR 任务均有对应代码。可是 `CellPLM.get_gene_expression_embedding()` 仍是 `pass`，其 `get_embedding('gene-expression', ...)` 分支最终抛出 `ValueError`（`biollm/loader/cellplm.py:175-217`）。因此论文中“支持 CellPLM/基因表达 embedding”的表述不能对这条路径标为完全可运行。数据集、模型 checkpoint 和 GPU/CUDA 环境也不在快照中，完整复现实验需要按论文资源链接补齐。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## BioLLM Summary

### Problem

Single-cell foundation models (scFMs) differ in architecture, tokenization, preprocessing, APIs and evaluation conventions. Those differences make model switching, fair benchmarking and reproducibility difficult (`paper.md:29-35`).

### Contribution

BioLLM is a standardized Python framework for scRNA-seq that separates configuration/task execution, model adapters and data handling. It supports zero-shot embeddings and fine-tuning for cell annotation, GRN analysis and drug-response workflows, with common metrics and documentation (`paper.md:39-43,99-155`).

### Method in Brief

An AnnData object and configuration enter `BioTask`, which selects a concrete loader, loads vocabulary/checkpoint, and delegates preprocessing to a model-specific `DataHandler`. The processed data are converted to model inputs and passed through a zero-shot embedding or fine-tuning task. Outputs are evaluated with ASW/batch metrics, GO-enriched GRNs, classification metrics, or PCC/SRCC drug-response correlations. The central design is an adapter contract, not a new pretraining loss.

### Evaluation and Findings

The paper evaluates four main models (scBERT, Geneformer, scGPT and scFoundation) across individual/joint cell-embedding datasets, 13 annotation datasets, GRN resolutions and DeepCDR GDSC/CCLE drug-response tasks (`paper.md:45-79`). scGPT is the strongest overall, especially for cell separation, annotation and rare cell types; Geneformer and scFoundation are strong for gene-level tasks; scBERT generally underperforms. Fine-tuning improves annotation and embedding quality. Geneformer is consistently efficient for annotation/drug response, while scFoundation is memory-heavy. Figure 6 summarizes these trade-offs.

### Reproducibility

The paper links public GitHub code, Zenodo archives and model checkpoints (`paper.md:197-209`). The cloned repository contains task docs and configuration examples, but benchmark datasets/checkpoints and a single end-to-end command are external. Installation warns that `flash-attn` and CUDA versions are sensitive (`BioLLM/README.md:16-27`). Direct source verification confirms the core orchestration, preprocessing, embedding, GRN and drug-response paths. It also finds a concrete gap: the CellPLM adapter accepts `gene-expression` as an API value but raises `ValueError` instead of dispatching it (`biollm/loader/cellplm.py:175-217`).

### Limitations

The paper restricts the framework to scRNA-seq and notes heterogeneity in loaders and fine-tuning strategies (`paper.md:93-95`). Cross-model comparability therefore remains partly dependent on each adapter's preprocessing and checkpoint behavior. No GPU benchmark was run in this analysis environment.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
