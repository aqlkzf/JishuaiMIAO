---
layout: default
permalink: /paper-atlas/scllm-dsc-02e546c1/
title: "scLLM-DSC"
nav: false
wide: true
description: "scLLM-DSC 解决的是单细胞 RNA 测序数据的无监督细胞聚类问题。输入是表达矩阵 \\mathbf{X}\\in\\mathbb{R}^{N\\times D}，其中 N 是细胞数、D 是基因数；输出是每个细胞的聚类标签 \\mathbf{C}=\\{c1,c2,\\dots,cN\\}。"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>scLLM-DSC</h1>
    <p>scLLM-DSC: LLM-Knowledge Enhanced Cross-Modal Deep Structural Clustering for Single-Cell RNA Sequencing</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2606.13007" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scLLM-DSC">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/XPgogogo/scLLM-DSC" target="_blank" rel="noopener noreferrer" aria-label="Open code for scLLM-DSC">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scLLM-DSC 方法中文解读

### 1. 这篇论文要解决什么问题？

scLLM-DSC 解决的是单细胞 RNA 测序数据的无监督细胞聚类问题。输入是表达矩阵 $\mathbf{X}\in\mathbb{R}^{N\times D}$，其中 $N$ 是细胞数、$D$ 是基因数；输出是每个细胞的聚类标签 $\mathbf{C}=\{c_1,c_2,\dots,c_N\}$。论文把任务定义为学习 $f:(\mathbf{X},\mathbf{G})\to\mathbf{Z}$，其中 $\mathbf{G}$ 是由 LLM 从 NCBI 基因知识中得到的语义知识库，$\mathbf{Z}$ 是融合转录组结构和生物语义后的潜空间 (`paper source/arxiv_html/paper.md:62`)。

作者认为，传统聚类方法擅长挖掘表达矩阵的数值分布或拓扑结构，但往往把基因当成抽象编号，忽略基因功能、调控含义等生物语义；而单细胞 foundation model 虽然强大，但常以生成式或掩码重建为预训练目标，并不天然适合区分局部细胞亚群边界 (`paper source/arxiv_html/paper.md:20`, `paper source/arxiv_html/paper.md:25`)。

### 2. 核心思想

scLLM-DSC 的核心不是让 LLM 直接生成细胞标签，而是让 LLM 作为“生物语义编码器”：先把 NCBI 中的基因描述编码成基因向量，再构造细胞级语义向量；同时用结构聚类网络从表达矩阵中学习细胞拓扑结构；最后用对比学习把“语义视图”和“结构视图”对齐到同一个潜空间中，再做聚类 (`paper source/arxiv_html/paper.md:29`, `paper source/arxiv_html/paper.md:68`)。

```text
表达矩阵 X + NCBI 基因文本知识
        │
        ├─ 基因语义编码：基因文本 → LLM embedding → G
        │
        ├─ 双路径细胞语义编码
        │      ├─ 表达量加权的基因语义聚合
        │      └─ top-K 基因排序序列的 Cell2Sentence 编码
        │
        ├─ 结构视图编码：scCDCG 风格结构编码器 → Z^feat
        │
        └─ 跨模态对齐：InfoNCE + 方差正则 → Z^cluster → KMeans/Leiden
```

图 2 直观展示了这个三模块结构：上半部分是语义路径，中下部分是结构路径，右侧是对比学习融合和下游聚类 (`paper source/arxiv_html/images/figure_02.png`)。

### 3. 基因语义编码

对第 $j$ 个基因，作者把 NCBI 中的基因符号、功能摘要等信息序列化为文本 $\mathcal{T}_j$，并用冻结的 LLM 编码：

$$\mathbf{g}_{j}=f_{\mathrm{LLM}}(\mathcal{T}_{j}).$$

所有基因向量堆叠成：

$$\mathbf{G}=[\,\mathbf{g}_{1},\mathbf{g}_{2},\dots,\mathbf{g}_{M}\,]^{\top}\in\mathbb{R}^{M\times d_{1}}.$$

这一步把离散基因 ID 转换为连续的、含功能知识的语义向量。图 1 用 AKT1 展示了从 NCBI 知识字段到 GPT embedding 的流程 (`paper source/arxiv_html/paper.md:74`, `paper source/arxiv_html/images/figure_01.png`)。

### 4. 双路径细胞语义编码

每个细胞先按表达量选取 top-$K$ 基因，实验中 $K=2048$ (`paper source/arxiv_html/paper.md:94`, `paper source/arxiv_html/paper.md:285`)。然后构造两条语义路径：

#### 4.1 表达量加权语义聚合

令 $\widetilde{\mathbf{X}}\in\mathbb{R}^{N\times K}$ 表示筛选后的表达矩阵，$\widetilde{\mathbf{G}}\in\mathbb{R}^{K\times d_1}$ 表示对应基因的语义向量，则：

$$\mathbf{Z}^{(1)}=\widetilde{\mathbf{X}}\,\widetilde{\mathbf{G}}\in\mathbb{R}^{N\times d_{1}}.$$

这相当于用表达量作为权重，把一个细胞中高表达基因的语义向量加权求和 (`paper source/arxiv_html/paper.md:99`)。

#### 4.2 基因序列上下文建模

第二条路径把每个细胞的 top-$K$ 基因名按表达排序后看成一个“句子” $\mathcal{S}_i$，再用 LLM 编码：

$$\mathbf{Z}^{(2)}_{i}=f_{\mathrm{LLM}}(\mathcal{S}_{i}),\quad\mathbf{Z}^{(2)}\in\mathbb{R}^{N\times d_{1}}.$$

这个路径借鉴 Cell2Sentence，用排序后的基因列表捕捉基因共现和上下文关系 (`paper source/arxiv_html/paper.md:110`)。

#### 4.3 双路径融合

两个细胞语义向量按比例融合：

$$\mathbf{Z}^{\mathrm{text}}=\omega\mathbf{Z}^{(1)}+(1-\omega)\mathbf{Z}^{(2)}.$$

图 6 和 4.6 节显示，$\omega=0.5$ 时 ACC/NMI/ARI 最优，说明表达量语义和序列上下文语义互补 (`paper source/arxiv_html/paper.md:367`, `paper source/arxiv_html/images/figure_06.png`)。

### 5. 结构视图编码

结构视图使用 scCDCG 风格的深度结构聚类骨干网络，把表达矩阵映射为：

$$\mathbf{Z}^{\mathrm{feat}}=f_{\mathrm{struc}}(\mathbf{X})\in\mathbb{R}^{N\times d_{2}}.$$

该分支包含三类无监督目标 (`paper source/arxiv_html/paper.md:130`)：

- $\mathcal{L}_{NCut}$：Normalized Cut 损失，用于保持高阶拓扑结构。
- $\mathcal{L}_{MSE}$：自编码器重构损失，确保潜表示保留表达信息。
- $\mathcal{L}_{KL}$：软聚类分配和目标分布之间的 KL 损失，目标分布通过最优传输机制优化，用于缓解聚类坍塌。

需要注意：本文没有完整展开 $\mathcal{L}_{NCut}$、$\mathcal{L}_{MSE}$、$\mathcal{L}_{KL}$ 的公式，而是引用 scCDCG 作为结构骨干；

### 6. 跨模态对齐和融合

语义表示 $\mathbf{Z}^{\mathrm{text}}$ 和结构表示 $\mathbf{Z}^{\mathrm{feat}}$ 先分别经过两层 MLP 投影到同一维度：

$$\mathbf{\hat{Z}}^{\mathrm{text}}=f_{\phi}(\mathbf{Z}^{\mathrm{text}}),\quad\mathbf{\hat{Z}}^{\mathrm{feat}}=g_{\psi}(\mathbf{Z}^{\mathrm{feat}}).$$

相似度矩阵为：

$$\mathbf{S}=(\mathbf{\hat{Z}}^{\mathrm{text}}(\mathbf{\hat{Z}}^{\mathrm{feat}})^{\top})/\tau.$$

然后用双向 InfoNCE 让同一个细胞的文本视图和结构视图互相靠近、不同细胞互相区分：

$$\small\mathcal{L}_{CL}=-\frac{1}{2N}\sum_{i=1}^{N}\left(\underbrace{\log\frac{\exp(S_{ii})}{\sum_{k=1}^{N}\exp(S_{ik})}}_{\text{Text }\to\text{ Feature}}+\underbrace{\log\frac{\exp(S_{ii})}{\sum_{k=1}^{N}\exp(S_{ki})}}_{\text{Feature }\to\text{ Text}}\right).$$

为了避免所有样本被投影到同一点，方法加入方差正则：

$$\mathcal{L}_{align}=\mathcal{L}_{CL}+\lambda\mathcal{L}_{var}.$$

论文实验中投影头为 128 维，$\tau=0.1$，$\lambda=10^{-2}$ (`paper source/arxiv_html/paper.md:151`, `paper source/arxiv_html/paper.md:285`)。

### 7. 训练和推断

总损失为：

$$\mathcal{L}=\alpha\mathcal{L}_{align}+\beta\mathcal{L}_{NCut}+\gamma\mathcal{L}_{MSE}+\delta\mathcal{L}_{KL}.$$

训练收敛后，语义和结构投影向量取平均：

$$\mathbf{Z}^{\mathrm{cluster}}=\frac{1}{2}\left(\mathbf{\hat{Z}}^{\mathrm{text}}+\mathbf{\hat{Z}}^{\mathrm{feat}}\right).$$

最后在 $\mathbf{Z}^{\mathrm{cluster}}$ 上用 KMeans 或 Leiden 得到聚类标签 (`paper source/arxiv_html/paper.md:204`)。论文还说明训练采用两阶段流程：先做 autoencoder 预训练（NCut/MSE），再做对比聚类；聚类由 KMeans 初始化，并用 Sinkhorn 细化 (`paper source/arxiv_html/paper.md:285`)。

### 8. 实验结果怎么看？

实验使用 scCluBench 的 6 个真实 scRNA-seq 数据集，包括 Mauro Pancreas、Sonya Liver、Sapiens Liver、Muris Brain、Muris Liver、Muris Limb Muscle (`paper source/arxiv_html/paper.md:227`, `paper source/arxiv_html/paper.md:276`)。指标为 ACC、NMI、ARI (`paper source/arxiv_html/paper.md:288`)。

主要结论：

- 与深度嵌入/结构聚类方法相比，scLLM-DSC 平均 ACC 88.80%、NMI 85.35%、ARI 83.04%，整体排名第一 (`paper source/arxiv_html/paper.md:239`, `paper source/arxiv_html/paper.md:318`)。
- 与 scGPT、Geneformer、GeneCompass 等 foundation model 相比，scLLM-DSC 在多数数据集上更好；但 Sonya Liver 上 Geneformer/GeneCompass 达到 100%，作者认为可能与预训练数据重叠有关 (`paper source/arxiv_html/paper.md:291`, `paper source/arxiv_html/paper.md:318`)。
- 图 5 的消融实验显示，去掉 $\mathcal{L}_{align}$ 或 $\mathcal{L}_{NCut}$ 会明显降低性能，说明语义对齐和结构拓扑都很关键 (`paper source/arxiv_html/paper.md:355`, `paper source/arxiv_html/images/figure_05.png`)。
- 图 4 展示了 Mauro Pancreas 上从 marker gene 到 marker-overlap 再到注释比较的生物解释流程 (`paper source/arxiv_html/paper.md:329`, `paper source/arxiv_html/images/figure_04.png`)。

### 9. 复现风险

论文声称代码和数据位于 `https://github.com/XPgogogo/scLLM-DSC`，但本次获取时该 GitHub 仓库返回 `Repository not found`，无法克隆。

此外，论文没有在正文中给出完整的 scCDCG 损失实现、OT/Sinkhorn 细节、Optuna 搜索空间、数据下载版本或预处理脚本。这些不是结论错误，而是复现时需要补充的关键缺口。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scLLM-DSC Summary

### What Problem It Solves

scLLM-DSC targets unsupervised clustering of single-cell RNA-seq data. The paper argues that cell clustering is central to resolving tissue heterogeneity, but many clustering methods reduce genes to numerical indices and therefore miss explicit biological functions encoded in gene metadata (`paper source/arxiv_html/paper.md:14`, `paper source/arxiv_html/paper.md:20`).

### Why Existing Methods Are Limited

The paper groups prior work into conventional scRNA-seq clustering, deep structural clustering, and biological foundation models. Conventional and deep clustering methods such as scDeepCluster, scGNN, scDSC, and scCDCG model expression distributions or topology but are described as semantically agnostic (`paper source/arxiv_html/paper.md:40`). Foundation models such as scBERT, Geneformer, scGPT, and scFoundation learn broad cell/gene representations, but the authors argue they have an objective mismatch for clustering because generative or masked-model pretraining does not directly enforce local subpopulation boundaries (`paper source/arxiv_html/paper.md:25`, `paper source/arxiv_html/paper.md:45`).

### Proposed Method

scLLM-DSC is an LLM-knowledge enhanced cross-modal deep structural clustering framework. It combines:

1. **Knowledge-driven semantic view**: NCBI gene descriptions are encoded by a frozen LLM into gene embeddings; top-$K$ genes per cell are transformed into two semantic cell views via abundance-weighted aggregation and Cell2Sentence-style ranked gene serialization (`paper source/arxiv_html/paper.md:74`, `paper source/arxiv_html/paper.md:94`).
2. **Structure-aware topological view**: a scCDCG-style structural encoder extracts expression-derived features under NCut, MSE, and KL objectives (`paper source/arxiv_html/paper.md:130`).
3. **Cross-modal fusion**: projected semantic and structural embeddings are aligned with bidirectional InfoNCE plus variance regularization, then averaged for KMeans or Leiden clustering (`paper source/arxiv_html/paper.md:151`, `paper source/arxiv_html/paper.md:204`).

The key computational idea is to use LLMs as semantic mappers for gene/cell representations, not as generators, and then force the semantic and expression-structural views to agree in a shared latent space (`paper source/arxiv_html/paper.md:29`).

### Evaluation

The paper evaluates six scRNA-seq datasets from scCluBench: Mauro Pancreas, Sonya Liver, Sapiens Liver, Muris Brain, Muris Liver, and Muris Limb Muscle (`paper source/arxiv_html/paper.md:227`, `paper source/arxiv_html/paper.md:276`). Metrics are ACC, NMI, and ARI (`paper source/arxiv_html/paper.md:288`).

Against deep embedding and structural clustering baselines, scLLM-DSC reports the best average rank with mean ACC 88.80%, NMI 85.35%, and ARI 83.04% (`paper source/arxiv_html/paper.md:239`, `paper source/arxiv_html/paper.md:318`). Against foundation models, it outperforms scGPT, Geneformer, and GeneCompass on most datasets, although Geneformer and GeneCompass reach perfect scores on Sonya Liver in Table 3 (`paper source/arxiv_html/paper.md:291`). Ablations show performance drops when removing semantic alignment, NCut, MSE, KL, or either semantic path, supporting the importance of both topology and semantic knowledge (`paper source/arxiv_html/paper.md:355`, `paper source/arxiv_html/paper.md:358`).

### Reproducibility Notes

- **Code availability**: The paper advertises `https://github.com/XPgogogo/scLLM-DSC`, but acquisition could not clone it because GitHub returned `Repository not found`; therefore this workspace is `paper-only` and no code-paper match was verified (`paper source/arxiv_html/paper.md:285`, `logs/delegation_and_code_availability.md:1`).
- **Data and protocol**: The paper says all datasets are from scCluBench and used without further preprocessing, but the acquired manuscript does not include dataset hashes, scripts, or download manifests (`paper source/arxiv_html/paper.md:276`).
- **Model dependencies**: The method uses OpenAI `text-embedding-3-small`, PyTorch >=2.9.1, CUDA 13.0, Optuna tuning, and A800-80GB GPU experiments (`paper source/arxiv_html/paper.md:285`).
- **Missing details**: Full scCDCG loss definitions, OT/Sinkhorn implementation details, hyperparameter search space, and exact preprocessing are **Not found** in local paper-only evidence.

### Bottom Line

scLLM-DSC is a method paper proposing that single-cell clustering can benefit from aligning expression-derived structural embeddings with LLM-derived biological semantics. The paper provides a clear mathematical pipeline and strong reported benchmark/ablation results, but local reproducibility is currently limited by an inaccessible advertised GitHub repository and missing implementation/data artifacts.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
