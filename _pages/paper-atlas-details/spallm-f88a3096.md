---
layout: default
permalink: /paper-atlas/spallm-f88a3096/
title: "spaLLM"
nav: false
wide: true
description: "spaLLM 把空间多组学的两个数值模态与 scGPT 生成的 RNA spot embedding 放进多张图中传播，再通过三级注意力汇合为 64 维表示，最后用 mclust 等聚类器划分空间域。这里的“LLM”是冻结 scGPT 的预计算表示，不是训练或提示一个聊天模型。"
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
      <span>Briefings in Bioinformatics · 2025</span>
    </div>
    <h1>spaLLM</h1>
    <p>spaLLM: enhancing spatial domain analysis in multi-omics data through large language model integration</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1093/bib/bbaf304" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for spaLLM">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/liiilongyi/spaLLM" target="_blank" rel="noopener noreferrer" aria-label="Open code for spaLLM">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## spaLLM 中文方法解读

### 一句话理解

spaLLM 把空间多组学的两个数值模态与 scGPT 生成的 RNA spot embedding 放进多张图中传播，再通过三级注意力汇合为 64 维表示，最后用 mclust 等聚类器划分空间域。这里的“LLM”是冻结 scGPT 的预计算表示，不是训练或提示一个聊天模型。

### 输入与输出

输入包括同一批 $N$ 个 spot 的两种组学矩阵 $X_1\in\mathbb R^{N\times D_1}$、$X_2\in\mathbb R^{N\times D_2}$，空间坐标 $P\in\mathbb R^{N\times2}$，以及从 RNA 生成的 512 维 scGPT embedding。第二模态可以是蛋白或染色质可及性。输出是每个 spot 的 64 维联合表示；空间域标签来自后续 mclust/Leiden/Louvain，并非网络直接监督分类。

### 方法从左到右

#### 1. scGPT 表示

作者先把 RNA AnnData 的基因名匹配到 scGPT 词表，再调用 `scgpt.tasks.cell_emb.embed_data`，最长输入 1200、batch size 64，将 `X_scGPT` 保存为 NumPy 文件。该步骤依赖外部 scGPT 模型目录；仓库只提供带占位路径的脚本 `embedding.py`，不包含模型权重或一键数据管线。

#### 2. 三类邻接关系

- 空间图：默认每个 spot 连 3 个坐标最近邻；空间表观组—转录组数据改为 6 个。
- 两个组学特征图：各自在预处理特征上以 correlation metric 建 20-NN 图。
- LLM embedding 图：示例脚本从 scGPT embedding 构建相似性邻接矩阵。

代码先把单向 kNN 邻接与转置相加并二值化，再加自环并做归一化，因此送入 GNN 的邻接是显式对称化的（`preprocess.py:70-119`）。

#### 3. 六条表示分支

第一和第二组学分别在空间图、特征图上经过三层 `DeepEncoder`，得到四个 64 维表示。scGPT embedding 还分别沿 RNA 空间图与 LLM 相似图传播，得到另外两个 64 维表示：

$$R_{os1},R_{oe1},R_{os2},R_{oe2},R_{fs},R_{fe}.$$

“多视图”指的正是同一 spot 在空间邻接、数值特征邻接与 scGPT 相似邻接下的不同视角。

#### 4. 三级注意力融合

对输入表示 $h_k$，注意力层计算

$$a_k=\operatorname{softmax}\big(u^\top\tanh(W h_k)\big),\qquad h=\sum_k a_kh_k.$$

第一级分别合并 `LLM-spatial + omics1-spatial` 与 `LLM-feature + omics1-feature`；第二级合并这两个 RNA/LLM视角，同时合并第二组学的空间与特征视角；第三级再合并两个组学，得到最终 `emb_combined`。注意力权重是模型内部加权系数，可用于描述分支贡献，但不能直接解释为生物因果重要性。

#### 5. 重建与一致性目标

论文给出的目标由六个 MSE 项组成：两个原始组学重建、两个跨组学一致性、两个 scGPT embedding 重建，并按数据集类型赋权。训练不使用空间域标签；标签只用于选择聚类数和计算 ARI、NMI、AMI、homogeneity、v-measure 等评估指标。

### 论文结果怎样读

论文在四类数据上展示结果：MISAR-seq 胚胎小鼠脑（RNA+ATAC）、10x 人淋巴结、SPOTS 小鼠脾（RNA+蛋白）和 Spatial-CITE-seq 人扁桃体。MISAR 与淋巴结有人工区域标签，可计算监督指标；脾与扁桃体更多依赖组织形态和 marker 解释。`spaLLM zero` 把 LLM embedding 置零，用于区分“新 GNN/注意力架构”与“scGPT 信息”的增益。

这些实验支持 scGPT 分支在所测数据上提供补充信息，但不证明对所有组织或平台泛化。论文也明确指出不支持图像模态。性能比较使用已知/指定聚类数和人工标签，不能等同于完全无先验发现未知域数。

### 代码核对后的关键边界

本地快照表达了论文架构，但当前主训练路径存在阻断性不一致，不能直接视为可运行复现：

1. `DeepEncoder.weights` 是普通 Python list，而不是 `ParameterList`；这些权重不会出现在 `model.parameters()` 中，也不会随 `.to(device)` 自动迁移（`modelTriatt_Flow1.py:19-24`）。因此优化器不能更新主要 GNN 编解码器参数，GPU 运行还可能设备不一致。
2. 模型返回 `emb_combined`、`emb_cross1`、`emb_cross2`（`modelTriatt_Flow1.py:105-111`），训练器却读取 `emb_latent_combined` 与 `emb_latent_omics*_across_recon`（`spaLLM_util.py:59-66,108-116`），会触发 `KeyError`。
3. 论文/构造函数保存了数据类型 epoch 默认值，但 `train(epochs=...)` 可显式覆盖；示例脚本实际参数必须作为复现证据读取。
4. 仓库没有依赖锁文件、自动测试、打包配置或已保存模型；示例含硬编码本地路径，完整复现需要人工准备数据、R `mclust`、rpy2 与 scGPT 环境。

因此最准确的代码—论文结论是：算法组件和公式映射为 Partial，当前提交的端到端可执行性为 Not runnable as-is。旧文档中“完整可复现”“训练能直接完成”等表述已撤回。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## spaLLM Summary

spaLLM is a spatial multi-omics domain-identification method that supplements RNA and a second omics modality with a frozen scGPT spot embedding. It constructs spatial, omics-feature and scGPT-similarity graphs, produces six graph-conditioned representations, fuses them with three stages of attention, and clusters the resulting 64-dimensional spot embedding.

### Main contribution

The conceptual contribution is not a new language-model training objective. scGPT is used once to produce a 512-dimensional RNA-derived representation. The novelty lies in treating that representation as two additional graph views—propagated over spatial and embedding-similarity graphs—and combining them with RNA/ATAC or RNA/protein graph views.

The loss uses six MSE components: reconstruction of two omics inputs, reconstruction of the scGPT embedding from its spatial and feature branches, and cross-modal consistency for the two omics representations. Spatial-domain labels are not used for network fitting; mclust or graph clustering is applied afterward.

### Evidence

The paper evaluates MISAR-seq mouse embryonic brain, 10x human lymph node, SPOTS mouse spleen and Spatial-CITE-seq human tonsil data. It reports stronger supervised clustering metrics than compared methods on annotated datasets and uses morphology, attention weights and marker profiles for the other applications. The zero-embedding ablation indicates that both the new architecture and nonzero scGPT features contribute.

The conclusions should remain bounded: cluster count/annotations inform evaluation, only four datasets are shown, native images are unsupported, and attention weights are not causal biological explanations.

### Code fidelity

The snapshot is **Partial and not runnable as-is**. Its graph and attention structure match the paper, but `DeepEncoder` stores trainable matrices in a plain list, so PyTorch does not register or optimize them. The model also returns result keys that differ from those expected by the loss and evaluation functions, causing `KeyError`. No tests, environment lock, model checkpoint or fully parameterized CLI are included.

See `Chinese method notes` for the learning-oriented explanation and `doc_code.md` for direct code anchors.

### Metadata

- Journal: *Briefings in Bioinformatics* 26(4), 2025, bbaf304
- DOI: `10.1093/bib/bbaf304`
- Code: `https://github.com/liiilongyi/spaLLM`
- Local paper source: `spaLLM_paper/spaLLM_paper.md`
- Local code source: `spaLLM/`

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
