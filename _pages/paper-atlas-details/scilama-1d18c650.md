---
layout: default
permalink: /paper-atlas/scilama-1d18c650/
title: "sciLaMA"
nav: false
wide: true
description: "单细胞 RNA 测序数据通常是“细胞 × 基因”的表格。VAE 很适合处理这种表格，但传统 scVI（Nature Methods, 2018）主要学习细胞表示，不能自然地产生可用于基因分析的表示；siVAE（Genome Biology, 2023）可以同时学习细胞和基因表示，但基因编码器的输入宽度随细胞数增长。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>sciLaMA</h1>
    <p>sciLaMA: A Single-Cell Representation Learning Framework to Leverage Prior Knowledge from Large Language Models</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/microsoft/sciLaMA" target="_blank" rel="noopener noreferrer" aria-label="Open code for sciLaMA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## sciLaMA 方法详解

### 一、它要解决什么问题？

单细胞 RNA 测序数据通常是“细胞 × 基因”的表格。VAE 很适合处理这种表格，但传统 scVI（*Nature Methods*, 2018）主要学习细胞表示，不能自然地产生可用于基因分析的表示；siVAE（*Genome Biology*, 2023）可以同时学习细胞和基因表示，但基因编码器的输入宽度随细胞数增长。另一方面，scGPT（*Nature Methods*, 2024）等单细胞基础模型能够提供先验知识，却需要较高的训练或微调成本，也不天然适合直接处理表达矩阵（`paper.md:18-24,36-51,496-510`）。

sciLaMA 的思路是：不重新训练外部语言模型，而是把已经计算好的基因向量接到一个“成对 VAE”上，使它们适应当前单细胞表达环境（`paper.md:54-69`）。

### 二、输入、输出与核心直觉

论文定义了两个输入：

1. $N$ 个细胞、$M$ 个基因组成的表达矩阵 $C$，每一行是细胞向量 $\mathbf c_i$；
2. 每个基因的 $D$ 维静态向量 $\mathbf g_j$，来自一个预训练语言/蛋白模型（`paper.md:60-64`）。

模型输出：

- $K$ 维细胞表示 $\mathbf z_i^{\mathrm{cell}}$；
- $K$ 维基因表示 $\mathbf z_j^{\mathrm{gene}}$；
- 用细胞和基因表示重建的表达值 $\hat c_{i,j}$。

```text
表达矩阵 C -----------------> 细胞 VAE ------> z_cell, h_cell
                                                   \
                                                    \---> 成对重建表达
外部基因向量 G -------------> 基因 VAE ------> z_gene, h_gene
                                                        |
                          z_cell 与 z_gene 的同维度对齐惩罚
```

这里的“对齐”是可计算的重建关系，不等于已经证明每一个潜变量维度都是唯一的生物学通路。

### 三、成对 VAE 的结构

转换后的 `paper.md` 没有保留显示公式；下面的公式按保留的原始论文 XML（`pmc_article.xml:10-67`）重写。

#### 1. 细胞编码器

细胞编码器把表达向量映射到一个对角高斯后验：

$$
(\boldsymbol\mu_i^{\mathrm{cell}},\boldsymbol\sigma_i^{\mathrm{cell}})
\leftarrow f_{\phi^{\mathrm{cell}}}^{\mathrm{cell}}(\mathbf c_i),
\quad
\mathbf z_i^{\mathrm{cell}}=\boldsymbol\mu_i^{\mathrm{cell}}+
\boldsymbol\epsilon\odot\exp\!\left(0.5\log[(\boldsymbol\sigma_i^{\mathrm{cell}})^2]\right),
\quad \boldsymbol\epsilon\sim\mathcal N(\mathbf0,I).
$$

代码中的 `RNA_ENCODER` 返回 `mu`、正的 `sigma` 和 Normal 分布的重参数化样本（`sciLaMA_repo/src/sciLaMA/model.py:23-58`）。细胞解码器先产生最后隐藏层 $\mathbf h_i^{\mathrm{cell}}$，并可以额外通过线性层得到普通表达重建（`model.py:61-112`）。

#### 2. 基因编码器

基因编码器对静态先验向量执行同样的变分编码：

$$
(\boldsymbol\mu_j^{\mathrm{gene}},\boldsymbol\sigma_j^{\mathrm{gene}})
\leftarrow f_{\phi^{\mathrm{gene}}}^{\mathrm{gene}}(\mathbf g_j),
\quad
\mathbf z_j^{\mathrm{gene}}=\boldsymbol\mu_j^{\mathrm{gene}}+
\boldsymbol\epsilon\odot\exp\!\left(0.5\log[(\boldsymbol\sigma_j^{\mathrm{gene}})^2]\right).
$$

其解码器输出 $\mathbf h_j^{\mathrm{gene}}$（`paper.md:81-85`; `pmc_article.xml:18-25`）。当前仓库可以为多个外部向量文件分别建立编码器，再用 `average`、`MoE` 或 `PoE` 融合后验；论文的主实验则按不同先验来源分别构造 sciLaMA 变体，因此多源融合属于已验证的代码扩展，不能直接当作论文实验设置（`sciLaMA_repo/src/sciLaMA/model.py:115-156`）。

#### 3. 成对表达重建

论文的关键操作是在解码器隐藏空间做内积：

$$
\hat c_{i,j}= (\mathbf h_i^{\mathrm{cell}})^T\mathbf h_j^{\mathrm{gene}}+b_j.
$$

代码对应 `sample_hidden_batch @ f_dec_h.T + bias`（`sciLaMA_repo/src/sciLaMA/model_lit.py:146-156`）。因此，外部知识不是直接替代表达矩阵，而是先被基因编码器适配，再与当前数据的细胞隐藏表示共同参与重建。

### 四、三阶段训练流程

#### 阶段 1：预训练细胞 VAE

细胞解码器的普通输出重建表达：

$$
\hat{\mathbf c}_i^{\mathrm{cell,recon}}=(\mathbf h_i^{\mathrm{cell}})^T W^{\mathrm{cell}}+\mathbf b.
$$

损失是平方误差和 KL 正则项：

$$
\mathcal L_{\mathrm{cell}}=\sum_i L_i^{\mathrm{cell,recon}}+
\beta D_{\mathrm{KL}}(q_{\mathrm{cell}}\|\mathcal N(0,I)).
$$

原论文的 Eqs. 6-8 位于 `paper.md:99-103` 和 `pmc_article.xml:26-38`。代码在每个细胞上对基因维度求和，再对 batch 求平均（`sciLaMA_repo/src/sciLaMA/loss.py:7-16`）。

#### 阶段 2：冻结细胞分支，适配基因分支

论文冻结 $\phi^{\mathrm{cell}}$、$\psi^{\mathrm{cell}}$ 及细胞解码器的线性参数，然后用成对隐藏表示重建表达并训练基因 VAE（`paper.md:105-111`）。代码在 stepwise phase 2 中复制阶段 1 权重、冻结细胞编码器/解码器，并设置 `gamma=0`（`sciLaMA_repo/src/sciLaMA/trainer.py:238-258`）。

因此这一阶段的代码损失是：

$$
\mathcal L_{\mathrm{gene}}=\text{hidden-space reconstruction}+
\beta D_{\mathrm{KL}}(q_{\mathrm{gene}}\|\mathcal N(0,I)).
$$

代码还保留了一个由潜变量内积产生的重建项，但由于 $\gamma=0$，该项在此阶段不产生贡献（`loss.py:19-39`）。

#### 阶段 3：联合优化

联合阶段使用两种重建：

$$
\hat c_{i,j}^{\mathrm{alignment}}=(\mathbf z_i^{\mathrm{cell}})^T\mathbf z_j^{\mathrm{gene}}+b_j,
$$

并将其平方误差乘以 $\gamma$，与隐藏空间重建和两侧 KL 一起优化：

$$
\mathcal L_{\mathrm{sciLaMA}}=
L_{\mathrm{recon}}+\gamma L_{\mathrm{alignment}}+
\beta KL_{\mathrm{cell}}+\beta KL_{\mathrm{gene}}.
$$

这对应原论文 Eqs. 11-13（`paper.md:114-118`; `pmc_article.xml:47-59`）和 `joint_scilama_loss`（`sciLaMA_repo/src/sciLaMA/loss.py:42-67`）。论文与配置说明 $\gamma=0.05$；论文选择的实验维度是 $K=40$，但仓库模板默认 `latent_dim: 50`，复现实验时必须明确修改（`paper.md:341-345`; `script/template.yaml:16-24`）。

### 五、数据处理与推理

#### 论文规定的数据处理

论文的附录要求对原始计数做 library-size normalization、log 变换、按基因 z-score，并把值截断在 $[-10,10]$（`paper.md:300-310`）。

#### 当前代码的实际行为

代码通过 `scanpy.read_h5ad` 读取 AnnData，按 `adata.var["static_embedding"]` 选择建模基因，并按 `obs[split]` 切分 train/val/test（`sciLaMA_repo/src/sciLaMA/data.py:44-115`）。它只检查整体均值和标准差，不执行论文中的归一化、z-score 或截断（`data.py:53-56`; `utils.py:130-149`）。所以这些预处理必须由用户在进入训练器之前完成。

有外部向量时，代码要求每个 Parquet 包含 `gene_id` 与 `embedding`，然后与 AnnData 的基因名取交集并按排序后的共同基因对齐（`sciLaMA_repo/src/sciLaMA/utils.py:102-127,152-200`）。没有外部向量时，特征编码器使用表达矩阵转置 $X^T$；这对应 self-informed 路线的代码实现，但外部向量的生成过程在仓库中**未找到**（`model_lit.py:82-105`; `trainer.py:149-157`）。

#### 推理输出

推理阶段使用编码器的均值而不是随机样本：

- 细胞均值写入 `adata.obsm[save_key]`，并写入 `sample_embeddings_*.parquet`；
- 基因均值写入 `feature_embeddings_*.parquet`。

这对应论文 Eqs. 14-17（`paper.md:120-123`; `pmc_article.xml:60-67`），代码位置为 `sciLaMA_repo/src/sciLaMA/trainer.py:58-104`。

### 六、论文如何评价它？

| 任务 | 数据与比较 | 论文结论 |
|---|---|---|
| 细胞表示/批次校正 | 五个胰腺数据集；对比 scVI、scGPT、CellPLM、GenePT；ARI、NMI、ASW、cLISI、batchASW、iLISI | 平均 ARI=0.522、NMI=0.745；batchASW=0.865、iLISI=0.238（`paper.md:132-155`）。 |
| 基因表达补全 | 空间数据 30 个基因 leave-one-gene-out；对比 scProjection、gimVI、uniPort、Tangram | 论文报告 PCC、SCC、1-JSD、1/RMSE 的平均提升分别为 27.39%、15.58%、32.86%、3.32%（`paper.md:166-186`）。 |
| marker/module | PBMC 3K 与多来源胰腺数据；静态与 contextual gene embedding | PPBP 邻近模块显示血小板相关 GO 富集（`paper.md:189-203`；Figure 4）。 |
| 发育轨迹 | P0 小鼠皮层；对比 scVI；细胞/基因伪时间图 | 论文报告整体轨迹清晰度提高 20.65%（`paper.md:206-225`；Figures 5/S3）。 |

直接打开的 Figure 4、Figure 5、Figure S1-S4 支持这些方向性的可视化解释；主 Figures 1-3 没有本地栅格文件，因此它们的局部细节只能依据论文 caption，不能声称已完成图像核验（`figure_analysis.md`）。

### 七、复现边界与已知缺口

- **已验证：** paired encoder/decoder、三种损失、三阶段权重冻结与转移、posterior-mean 输出。
- **部分匹配：** 论文规定的表达预处理在代码中没有执行；代码只发出 scaling 警告。
- **未找到：** 六种外部 LLM/PLM 向量的生成脚本、原始数据、完整实验配置、benchmark/GO/trajectory 分析脚本、自动化测试。
- **保留不确定性：** 代码支持多源 embedding 融合，但当前证据不能确认这就是论文报告结果的训练设置；README 中的随机 embedding 示例也不是论文先验的来源证据。

因此，当前仓库足以理解并在准备好输入后运行模型核心，但不足以单独重现论文的全部表格、图和下游结论。以上“未找到”均限定在 acquired commit `f534317e151c49e1239a781b06c4f9b8584a4a30`、完整代码树、论文 Markdown/XML 与六个本地图像的搜索范围内。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## sciLaMA

### Problem

Single-cell VAEs are effective on tabular expression matrices but usually learn cell representations without a compatible route for incorporating text, protein-sequence, or foundation-model knowledge about genes. scVI (*Nature Methods*, 2018) is cell-centric; siVAE (*Genome Biology*, 2023) learns both cells and genes but its gene encoder width grows with the number of cells; GLUE (*Nature Biotechnology*, 2022) accepts graph-structured regulatory priors but not arbitrary sequence/text vectors. Transformer models such as scGPT (*Nature Methods*, 2024) can encode biological knowledge, but fine-tuning is computationally expensive and less natural for dense tabular expression (`paper.md:18-24,36-51,492-510`).

### Proposed Method

sciLaMA is a lightweight paired-VAE adapter for precomputed gene embeddings. A cell encoder maps each scaled expression vector to a latent cell representation; a gene encoder maps each static LLM/PLM vector to a latent gene representation. Their decoder hidden states reconstruct the expression matrix, while an additional inner product between cell and gene latents aligns corresponding dimensions. Training proceeds in three stages: cell VAE pretraining, frozen-cell gene VAE adaptation, then joint refinement with a latent-alignment penalty (`paper.md:54-123`; `pmc_article.xml:10-67`).

```text
cell x gene expression -> cell VAE -----> cell latent/hidden --+
                                                               +-> expression reconstruction
precomputed gene vectors -> gene VAE --> gene latent/hidden --+
                                      latent inner product -> aligned cell/gene coordinates
```

The conceptual novelty is not a new language model. It is an adapter that contextualizes already computed gene vectors with one expression dataset, yielding cell and gene embeddings in coordinated spaces. The paper evaluates natural-language, protein-language, and single-cell foundation-model priors (`paper.md:24,57-69,315-338`).

### Evaluation

- **Cell representation and batch integration:** On five pancreatic studies (14,767 cells; 13,062 intersected genes), the paper reports average ARI 0.522 and NMI 0.745, with batchASW 0.865 and iLISI 0.238. It compares sciLaMA variants with scVI, zero-shot/fine-tuned scGPT, CellPLM, and GenePT and reports a 25-fold runtime reduction relative to fine-tuned scGPT (`paper.md:132-163,355-367`). Figure S2 visually shows sciLaMA variants combining separated cell types with within-cluster batch mixing.
- **Gene imputation:** In a leave-one-gene-out spatial benchmark over 30 measured genes, sciLaMA is compared with scProjection, gimVI, uniPort, and Tangram. The paper reports average improvements of 27.39% PCC, 15.58% SCC, 32.86% 1-JSD, and 3.32% 1/RMSE over the other methods (`paper.md:166-186,370-388`). Main Figure 3 is not available as a local raster.
- **Marker modules:** On PBMC 3K and multi-source pancreas data, contextual gene embeddings group cell-state markers more clearly than static inputs. The displayed PPBP neighborhood is enriched for platelet/coagulation biology (`paper.md:189-203,391-401`; local Figure 4).
- **Developmental trajectory:** On P0 mouse cortex, the paper reports 20.65% clearer trajectory structure than scVI. Figures 5 and S3 show a more continuous pseudotime geometry and temporally localized expression programs; S4 reports moderate agreement with Integrated Gradients (Pearson $r=0.43$, Spearman $\rho=0.46$) (`paper.md:206-225,281-288,409-412`).

These are paper-reported results. The local figures support selected qualitative patterns but do not independently reproduce the metrics.

### Code-Paper Match

**Core implementation fidelity: medium.** Seven mapped core items are Exact, two Partial, one Inferred extension, and three Not found (`doc_code.md`). The current commit directly implements:

- the Gaussian cell and gene encoders and paired hidden-state reconstruction (`src/sciLaMA/model.py:23-156`; `src/sciLaMA/model_lit.py:47-156`);
- cell-only, gene-only, and joint reconstruction/KL objectives matching Eqs. 7-13 (`src/sciLaMA/loss.py:7-67`);
- the three-phase freeze/transfer/joint training schedule (`src/sciLaMA/trainer.py:215-286`);
- posterior-mean cell and gene embedding export (`src/sciLaMA/trainer.py:58-104`).

Important differences are explicit. The paper says expression is normalized, z-scored, and clipped; code only warns when global scaling looks wrong and assumes preprocessing has already occurred (`paper.md:303-310`; `src/sciLaMA/utils.py:130-149`). The paper reports $K=40$, while the supplied template defaults to 50 (`paper.md:341-345`; `script/template.yaml:16-24`). The package also supports multimodal posterior fusion, an implementation extension whose use in the reported experiments is not established (`src/sciLaMA/model.py:115-156`).

### Reproducibility Assessment

**2.5/5: the model core is runnable in principle, but the published study is not reproducible from this snapshot alone.**

Positive evidence:

- installable Python package, typed YAML schema, quick-start training path, checkpoint loading, and output persistence;
- GitHub snapshot fixed at commit `f534317e151c49e1239a781b06c4f9b8584a4a30`;
- direct source correspondence for the central equations and stepwise optimizer.

Missing evidence:

- **Not found:** paper datasets, the six published embedding artifacts or their exact generation pipeline, and per-experiment configs;
- **Not found:** scripts for baselines, imputation, clustering, GO enrichment, Palantir trajectories, metric aggregation, and paper figures/tables;
- **Not found:** automated tests for the data/model/training path;
- **Partial:** preprocessing is described by the paper but not executed by the package;
- **Missing locally:** structured supplementary tables and raster images for main Figures 1-3.

No training or benchmark run was attempted because the required datasets and embedding files are absent. The searched scope was the full acquired source tree plus paper Markdown, primary XML equations, and all six linked images.

### Limitations and Use Considerations

The method can only model genes shared by the expression matrix and every supplied embedding table; the code takes their intersection (`src/sciLaMA/utils.py:163-200`). Its biological conclusions therefore inherit coverage and bias from the selected pretrained embeddings. Contextual organization in UMAP or latent coordinates is evidence of association, not proof of regulatory causality. Finally, the paper demonstrates several datasets and tasks, but the absent experiment pipeline prevents checking seed sensitivity, uncertainty, and generalization beyond the displayed benchmarks.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
