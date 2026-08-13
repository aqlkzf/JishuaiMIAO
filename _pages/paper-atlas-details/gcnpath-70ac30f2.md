---
layout: default
permalink: /paper-atlas/gcnpath-70ac30f2/
title: "GCNPath"
nav: false
description: "GCNPath 预测细胞系对药物的自然对数 IC50。它针对两个泛化难点：基因表达平台与批次变化会使模型跨数据集失效；新药物和新细胞系同时出现的 strict-blind 场景比随机拆分困难。方法不直接把上万个基因送入全连接网络，而是先用 GSVA 把表达压成 292 个 BIOCARTA 通路活性，再把通路之间的生物网络邻近和样本相关性编码成图。"
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
      <span>Machine Learning Algorithm</span>
      <span>Communications Biology · 2026</span>
    </div>
    <h1>GCNPath</h1>
    <p>GCNPath: introspecting drug response prediction with pathway-guided graph convolution networks</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42003-026-09957-5" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GCNPath">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/MinhoLee-DGU/GCNPath2026" target="_blank" rel="noopener noreferrer" aria-label="Open code for GCNPath">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GCNPath：用通路串扰图预测抗癌药物反应

### 问题与核心思路

GCNPath 预测细胞系对药物的自然对数 IC50。它针对两个泛化难点：基因表达平台与批次变化会使模型跨数据集失效；新药物和新细胞系同时出现的 strict-blind 场景比随机拆分困难。方法不直接把上万个基因送入全连接网络，而是先用 GSVA 把表达压成 292 个 BIOCARTA 通路活性，再把通路之间的生物网络邻近和样本相关性编码成图。

```text
细胞表达 ─GSVA─> 292 通路分数 ─PCN/RGCN─> 细胞嵌入 ┐
                                                       ├─拼接─FCN─> ln(IC50)
药物 SMILES ─原子/键图─> Dense GAT ─池化─> 药物嵌入 ┘
```

### 细胞分支：三类 pathway crosstalk network

论文构建三种 PCN：由 STRING PPI 压缩得到的通路关系、由 RegNetwork GRN 压缩得到的关系，以及基于 GSVA 通路分数 Pearson 相关性的关系。每个通路保留 5 个最相关邻居；邻居选择会产生方向性。节点特征是样本特异的通路活性，边类型区分三种关系，因此模型用 relational GCN 传播。通路化减少维度并试图弱化不同 RNA 平台的系统差异，但它也丢失通路内基因差异，且性能依赖基因集和网络版本。

代码入口 `process_cell_gsva.R` 计算 GSVA；`process_cell.py` 用训练数据拟合/复用 `RobustScaler` 并生成图。对外部数据必须通过 `-train` 使用训练阶段 scaler，否则跨数据集比较会泄漏或发生尺度漂移。

### 药物分支与预测头

药物被表示为原子—键图，论文描述 85 维原子特征和 10 维键特征。药物分支使用 GAT/DenseGCN；节点表示经 global max pooling 得到药物向量。细胞和药物嵌入拼接后由 MLP 输出一个 ln(IC50)。`model/GCNPath_Plain.py:16-79,118-189` 直接展示双分支、通路展平、药物池化、拼接与回归头；训练脚本使用 MSE，并以验证 MSE 保存 checkpoint。

论文默认模型强调 RGCN 细胞图和 GAT 药物图。仓库还含 attention 变体与大量 benchmark/case-study 脚本，因此“仓库中存在某模块”不代表它一定用于论文所有主结果；必须以 shell 配置和结果目录对应具体实验。

### 评估怎样支持主张

- 图 2 是消融：PCN 图优于细胞 FCN，扰动 PCN 拓扑会降低 cell-blind 性能；药物原子图 GAT 优于 Morgan fingerprint/SMILESVec FCN。
- 图 3 比较 unblinded、cell-blind、drug-blind、strict-blind。作者的谨慎表述是 GCNPath 多数场景最佳或相当，而非压倒性领先。
- 后续图检验跨 RNA 平台、ChEMBL 未见药物、TCGA 和 SCLC 病例。它们扩大外部验证范围，但 TCGA/病例预测仍是回顾性证据，不等于临床前瞻试验。
- 指标包括 RMSE、PCC、SCC；严格盲拆分比随机 pair 拆分更能检验新细胞/新药泛化。

### 解释性与限制

模型可用 pathway attention/Grad-CAM 排序通路，但重要性表示对预测敏感，不自动证明因果机制。PCN 本身来自已知网络、通路重叠和相关性，所以解释同时继承数据库偏倚。药物响应标签来自 GDSC，跨 ChEMBL/TCGA 时还会受到测定、剂量和终点差异影响。

### 版本与复现边界

本地代码固定在提交 `9496d4c5d2502a9609e67a50b392cc60c9a951b8`；2026-07-19 官方 HEAD 已前移到 `1afd479da11fe5878e1f6da0fddffb1f6e03d13e`。仓库没有 Python package version，环境文件固定 Python 3.8、PyTorch 1.11、PyG 2.1、CUDA 11.3、R 4.2/GSVA 1.46，作者环境为 Ubuntu 20.04 + RTX 3090。工作区包含大量数据、结果和补充源表，但本次只做论文、图和静态源码核读，没有从头重跑预处理、交叉验证、外部验证或病例分析。

旧流程因 Graphify 未产生 `graph.json` 报错；

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## GCNPath summary

GCNPath is a pathway-informed graph neural network for anticancer drug-response regression. It converts expression profiles to 292 BIOCARTA GSVA scores, places them on three pathway-crosstalk graphs derived from STRING, RegNetwork, and pathway-score correlations, and processes the multiplex graph with an RGCN. A parallel GAT encodes drug atom–bond graphs; the two embeddings are concatenated to predict ln(IC50).

The paper evaluates ablations and unblinded, cell-blind, drug-blind, and strict-blind splits, then tests cross-platform expression, ChEMBL compounds, TCGA, and an SCLC case study. The evidence supports competitive and relatively balanced performance rather than universal dominance. Graph topology perturbation and graph-vs-linear comparisons support the value of pathway and drug graphs, while pathway compression also imposes database and gene-set assumptions.

Code fidelity is high for preprocessing, the two graph branches, MSE regression, split logic, and evaluation scripts. Reproducibility is medium: the repository includes data, outputs, supplementary source tables, and scripts, but requires an old CUDA/PyTorch/PyG/R stack and substantial storage. This workspace did not rerun training or reported metrics. Local commit is `9496d4c5…`; upstream HEAD observed 2026-07-19 is `1afd479d…`, so conclusions are snapshot-specific.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
