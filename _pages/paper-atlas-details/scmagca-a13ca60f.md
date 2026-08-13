---
layout: default
permalink: /paper-atlas/scmagca-a13ca60f/
title: "scMAGCA"
nav: false
wide: true
description: "scMAGCA 输入配对或多模态单细胞矩阵，先做 feature selection 和 normalization，拼接成 \\mathbf{X}^{con}，再构建 cell-cell KNN 图 \\mathbf{A}；GCN encoder 学出 latent embedding \\mathbf{Z}；"
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
      <span>Nature Communications · 2026</span>
    </div>
    <h1>scMAGCA</h1>
    <p>Interpretable modality-aware mapping of gene regulation in single-cell multiomics with scMAGCA</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-73055-7" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scMAGCA">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/zemingzhou30/scMAGCA" target="_blank" rel="noopener noreferrer" aria-label="Open code for scMAGCA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scMAGCA 方法中文解读

### 证据边界

这份文档把四类内容分开：

- **论文主张**：来自主论文和补充材料，例如论文把 scMAGCA 定义为整合 adversarial learning、graph convolution 和 zero-inflated modeling 的单细胞多组学框架，目标是学习可解释共享嵌入并用于聚类、批次校正和疾病解析（`paper source/paper/auto/paper.md:29-45`）。
- **代码验证行为**：来自发布代码 `scMAGCA/`。代码确认了核心 GCN autoencoder、ZINB heads、Gaussian-prior discriminator、KMeans/KL refinement 等模块，也暴露了若干实现细节，例如 PCA 后再做 cosine KNN（`scMAGCA/scMAGCA/scMAGCA.py:25-37`）。
- **解释性理解**：本文件中的直觉解释用于帮助学习方法，不等同于论文或代码的新证据。
- **缺口和限制**：保留 `Not found` 语言。完整覆盖所有论文 benchmark、十次独立重复和所有图表生成的单一端到端 runner 在代码中 **Not found**；现有证据是包代码、教程、figure notebooks/R scripts、precomputed results 和 dataset-specific shell commands（`doc_code.md:31-32`）。

### 1. scMAGCA 要解决什么问题

单细胞多组学的输入通常是同一批细胞的多个矩阵，例如 RNA 表达、ADT 蛋白、ATAC chromatin accessibility，有时还有三模态 TEA-seq。难点不是简单把矩阵拼起来，而是要同时处理：

1. 不同模态的特征空间不同，RNA/ATAC 稀疏且高维，ADT 维度较低但噪声结构不同。
2. 细胞身份既受单个特征影响，也受邻近细胞的局部拓扑影响。
3. 下游任务通常需要聚类、解释 latent factors、找 marker/regulator，而不是只输出一个黑箱 embedding。

论文认为已有方法各有短板：VAE 类方法能学习 latent space，但不一定显式保存 cell-cell topology；图方法能保留邻域，但不一定建模 dropout/count dispersion；部分 multi-omics 方法只适合特定模态组合或缺少 adversarial alignment（`paper source/paper/auto/paper.md:37-45`）。scMAGCA 的核心回答是：把 KNN cell graph、GCN autoencoder、ZINB count likelihood、Gaussian-prior adversarial regularization 和 DEC-style clustering 放到同一个聚类导向框架里。

### 2. 一句话框架

scMAGCA 输入配对或多模态单细胞矩阵，先做 feature selection 和 normalization，拼接成 $\mathbf{X}^{con}$，再构建 cell-cell KNN 图 $\mathbf{A}$；GCN encoder 学出 latent embedding $\mathbf{Z}$；linear decoder 重构预处理特征，ZINB decoder 拟合 raw selected counts，discriminator 把 latent distribution 约束到 Gaussian prior；最后用 KMeans 初始化并通过 target distribution + KL loss 精炼 cluster。

```text
raw RNA / ADT / ATAC
        |
        v
feature selection
        |
        +--> raw selected counts X_raw_con -------------+
        |                                                |
        v                                                v
normalization / log / scale -> X_con -> KNN graph A -> GCN encoder -> Z
                                                             |
                   +----------------------+------------------+----------------+
                   |                      |                                   |
             linear decoder          ZINB heads                         discriminator
                   |                      |                                   |
                 MSE                  ZINB loss                         adversarial loss
                   |
                   +----------- pretraining objective ------------------------+
                                                             |
                                                             v
                                                   KMeans + Student-t Q
                                                             |
                                                   target distribution P
                                                             |
                                                       KL refinement
                                                             |
                                                             v
                                             embedding, clusters, factors
```

论文 Figure 1 的 legend 也按这个顺序描述：每个模态独立预处理，拼接成 joint matrix，构建 KNN cell-cell graph，GCN encoder 输出 embedding，linear/ZINB decoders 重构输入，pretraining 后用 cluster centroids 和 KL objective 精炼 assignment，并通过 GCN weight tracing 做特征解释（`paper source/paper/auto/paper.md:735-735`）。

### 3. 关键变量

| 变量 | 形状 | 含义 | 主要去向 |
|---|---:|---|---|
| $\mathbf{X}^{r}$ | $n \times d_{rna}$ | RNA matrix | 拼接进 $\mathbf{X}^{con}$ |
| $\mathbf{X}^{d}$ | $n \times d_{adt}$ | ADT/protein matrix | 拼接进 $\mathbf{X}^{con}$ |
| $\mathbf{X}^{t}$ | $n \times d_{atac}$ | ATAC peak matrix | 拼接进 $\mathbf{X}^{con}$ |
| $\mathbf{X}^{con}$ | $n \times m$ | 预处理后拼接矩阵 | KNN graph、GCN encoder、linear reconstruction |
| $\mathbf{X}^{con}_{raw}$ | $n \times m$ | feature-selected raw counts | ZINB loss target |
| $\mathbf{A}$ | $n \times n$ | cell-cell adjacency | GCN message passing |
| $\mathbf{Z}$ | $n \times 32$ | integrated latent embedding | discriminator、KMeans、cluster refinement、interpretation |
| $\mu,\theta,\pi$ | $n \times m$ | ZINB mean、dispersion、dropout probability | ZINB likelihood |
| $\mathbf{Q},\mathbf{P}$ | $n \times k$ | soft assignment 和 sharpened target distribution | KL clustering loss |

论文在方法中明确区分 $\mathbf{X}^{con}$ 和 $\mathbf{X}^{con}_{raw}$：前者是归一化和 log-transform 后拼接，用于 graph construction 与 linear reconstruction；后者是 feature selection 后未转换的 raw matrix，只用于 ZINB loss（`paper source/paper/auto/paper.md:175-183`）。代码中对应的是 `self.X = torch.cat([X1, X2], dim=-1)` 和 `self.X_raw = torch.cat([X1_raw, X2_raw], dim=-1)`（`scMAGCA/scMAGCA/scMAGCA.py:62-72`）。

### 4. 逐步计算流程

#### Step 1: feature selection 和预处理

论文说 RNA+ADT 保留 top 2000 highly variable genes 和所有 ADTs，RNA+ATAC/TEA-seq 类似保留 genes/peaks，并把处理后的模态横向拼接（`paper source/paper/auto/paper.md:175-181`）。

代码验证更具体：`run_scMAGCA.py` 的参数包括 `--filter1`、`--filter2`、`--f1=2000`、`--f2=2000`，然后把两个模态转成 `AnnData`，调用 `read_dataset()` 和 `preprocess_dataset()`，最后把 `adata.X` 与 `adata.raw.X` 分别送进模型（`scMAGCA/scMAGCA/run_scMAGCA.py:27-33`, `scMAGCA/scMAGCA/run_scMAGCA.py:86-119`）。`preprocess_dataset()` 会先保存 `adata.raw`，再 `normalize_total`，做 row-wise Seurat CLR，随后 `log1p` 和 `scale`（`scMAGCA/scMAGCA/preprocess.py:45-70`）。

学习时可以这样理解：scMAGCA 同时保留两个版本的数据。标准化后的 $\mathbf{X}^{con}$ 适合建邻接图和做 MSE reconstruction；raw selected matrix 适合让 ZINB 去解释零膨胀和 over-dispersion。

#### Step 2: 构建 cell-cell graph

论文定义在 $\mathbf{X}^{con}$ 上用 KNN 构造 adjacency $\mathbf{A}$，cell 是 node，edge 表示跨模态相似性，cosine similarity 用于衡量细胞间距离（`paper source/paper/auto/paper.md:183-183`）。论文实现设置中还说全局固定 $k=30$（`paper source/paper/auto/paper.md:359-359`）。

代码验证为 **Partial match**：`get_adj(count, k=30, pca=100)` 默认先做 PCA 到 100 维，再调用 `kneighbors_graph(..., metric="cosine")`（`scMAGCA/scMAGCA/scMAGCA.py:25-37`）。所以代码实际图是 “PCA-smoothed cosine KNN graph”，不是直接在完整 $\mathbf{X}^{con}$ 上做 KNN。这一差异对复现很重要，因为 PCA 会改变邻居关系。

#### Step 3: GCN encoder 和 decoder

论文 AGC-AE 部分用 Eq. 4-5 描述 GCN layer update：输入层是 $\mathbf{Z}^{0}=\mathbf{X}^{con}$，每层通过 normalized adjacency、learnable weight 和 PReLU activation 更新，输出 latent representation $\mathbf{Z}$（`paper source/paper/auto/paper.md:203-219`）。

代码匹配较好。两模态类 `scMultiCluster` 使用 `Encoder(layer_config=[input_dim1+input_dim2,1024,256,64,self.z_dim])`，其中 `self.z_dim = 32`；linear decoder 是 `32 -> 512 -> 1024 -> input_dim1+input_dim2`（`scMAGCA/scMAGCA/scMAGCA.py:39-60`）。`Encoder` 由多层 PyG `GCNConv`、`BatchNorm1d`、`PReLU` 组成（`scMAGCA/scMAGCA/layers.py:20-35`）。

直觉上，GCN 的作用是让一个细胞的 embedding 不只看自身特征，还看 KNN 图上的邻居。如果 KNN 图合理，这会增强局部细胞状态信号；如果 KNN 图被 batch 或某个模态主导，GCN 也会传播错误邻域。

#### Step 4: ZINB count modeling

论文用 Eq. 8-13 定义 NB/ZINB likelihood，并说明 decoder 从 latent $\mathbf{Z}$ 预测 $\mu$、$\theta$、$\pi$，分别表示 mean、dispersion 和 dropout probability，用于拟合 $\mathbf{X}^{con}_{raw}$（`paper source/paper/auto/paper.md:231-263`）。

代码中 `dec_mean`、`dec_disp`、`dec_pi` 是三个 head，`MeanAct` 是 exp + clamp，`DispAct` 是 softplus + clamp，`pi` 用 sigmoid（`scMAGCA/scMAGCA/scMAGCA.py:57-60`, `scMAGCA/scMAGCA/layers.py:6-18`）。ZINB loss 通过 `torch.where(x <= 1e-8, zero_case, nb_case)` 区分零和非零项（`scMAGCA/scMAGCA/loss.py:26-50`）。

实现注意点：两模态代码中 `zinb_loss = self.zinb_loss(x=self.X_raw, mean=mean, disp=disp, pi=pi)`，其中 `self.X_raw` 是全数据 raw target，而 `mean/disp/pi` 来自当前 PyG batch（`scMAGCA/scMAGCA/scMAGCA.py:99-118`）。现有文档把这列为复现风险，因为它似乎依赖 graph batch 实际包含全图或形状刚好匹配；改写 data loader 时应重新检查。

#### Step 5: adversarial latent regularization

论文把 adversarial alignment 写成 $\min_G \max_D$，其中 G 是 graph encoder，D 区分 Gaussian prior sample 和 encoder 生成的 latent code；prior 设为 $p(\mathbf{z})=\mathcal{N}(0,I)$（`paper source/paper/auto/paper.md:265-281`）。

代码验证为 **Partial match**：`Discriminator` 是两层 MLP + sigmoid，`self.real_distribution = torch.randn(self.num, self.z_dim)` 作为 prior sample，`adversarial_loss()` 用 BCE 让 prior 为 1、encoded embedding 为 0（`scMAGCA/scMAGCA/scMAGCA.py:96-118`, `scMAGCA/scMAGCA/layers.py:52-61`, `scMAGCA/scMAGCA/loss.py:69-74`）。但代码没有清晰的 alternating minimax loop，而是把 `discriminator_loss` 与 MSE/ZINB 一起放进同一个 optimizer step（`scMAGCA/scMAGCA/scMAGCA.py:118-122`）。

因此，写论文理解时可以说“论文主张 adversarial minimax alignment”；写代码行为时应说“发布代码实现了 Gaussian-prior discriminator BCE regularization，但不是显式交替训练的 minimax loop”。

#### Step 6: KMeans 初始化和 KL refinement

论文 Eq. 16-18 用 Student-t soft assignment $q_{ij}$、target distribution $p_{ij}$ 和 $\mathrm{KL}(P\|Q)$ 精炼聚类；训练是先 pretraining，再 clustering refinement（`paper source/paper/auto/paper.md:283-303`）。

代码中 `fit()` 先用 `KMeans(n_clusters=...)` 在 latent space 初始化 `self.mu`，然后每轮计算 `q = soft_assign(z, self.mu)`、`p = target_distribution(q).data`、`cluste_loss = cluster_loss(p,q)`，总 loss 是 `alpha*MSE + beta*ZINB + cluster_loss`，optimizer 是 Adadelta `lr=1, rho=.95`（`scMAGCA/scMAGCA/scMAGCA.py:129-180`, `scMAGCA/scMAGCA/loss.py:52-67`）。停止条件是 label 变化比例低于 `tol=0.001`，即少于 0.1% labels 变化（`scMAGCA/scMAGCA/run_scMAGCA.py:19-25`, `scMAGCA/scMAGCA/scMAGCA.py:191-197`）。

这个阶段把连续的 integrated embedding 变成离散细胞亚群。它适合 benchmark 指标和后续 marker 分析，但也可能把连续状态过度离散化，所以疾病 progression 或 communication 结论需要下游证据支持。

#### Step 7: 解释 latent factors 和生物学输出

论文 Supplementary Note 13 描述从 32 维 latent space 沿 GCN weights 反向追踪到输入特征，选出 top 200 genes/peaks/ADTs 做解释（`paper source/paper/auto/paper.md:351-357`）。主图 5-8 则把 embedding/clusters 接到 eRegulon、marker、gene activity、motif enrichment、peak-gene links、communication 和 qPCR 等分析（`paper source/paper/auto/paper.md:743-749`）。

这里必须区分：scMAGCA 代码能验证 embedding、clustering、部分 figure notebooks/R scripts 和预计算结果；qPCR 是论文/source-data/wet-lab 证据，不能从 scMAGCA Python package 直接复现。Figure 8 对 LACTB2/NCOA2 的支持是“计算发现 + 实验验证”，不是 neural model 本身证明临床因果作用（`figure_analysis.md:53-57`）。

### 5. 两阶段目标函数怎么读

预训练阶段：

$$
\mathcal{L}_{pretrain} = \alpha\mathcal{L}_{MSE} + \beta\mathcal{L}_{ZINB} + \gamma\mathcal{L}_{d}
$$

精炼阶段：

$$
\mathcal{L}_{train} = \alpha\mathcal{L}_{MSE} + \beta\mathcal{L}_{ZINB} + \mathcal{L}_{c}
$$

论文方法实现段写明默认 encoder widths `{m,1024,256,64,32}`、decoder `{32,512,1024,m}`、$k=30$、pretraining 400 epochs、Adam AMSGrad、learning rate $10^{-3}$，默认 $\alpha=0.2,\beta=0.8,\gamma=0.01$（`paper source/paper/auto/paper.md:359-361`）。代码默认参数与这些值一致（`scMAGCA/scMAGCA/run_scMAGCA.py:17-33`）。

但发布脚本并不总用默认权重。`scripts/run_scMAGCA_script.sh` 对不同 dataset 设置了不同的 `--alpha`、`--beta`、`--gama`，例如 10x1kpbmc 用 `0.5/1/0.1`，human_brain_3k 用 `1/1/0.2`（`scMAGCA/scripts/run_scMAGCA_script.sh:1-42`）。因此，复现实验结果时不能只引用默认命令，还要找到对应 dataset script 或 figure notebook 的参数。

### 6. 评估证据怎么读

论文主要评估层次如下：

| 场景 | 论文证据 | 应该支持的结论 | 谨慎点 |
|---|---|---|---|
| RNA+ADT benchmark | 14 个 RNA+ADT datasets，IDs 1-5 development，IDs 6-14 held-out aggregate，指标 AMI/NMI/ARI/ACC（`paper source/paper/auto/paper.md:55-55`） | held-out RNA+ADT 聚类性能强 | aggregate 不是 14 个全体直接平均 |
| RNA+ATAC benchmark | 14 个 RNA+ATAC datasets，IDs 19-23 development，IDs 24-32 held-out aggregate（`paper source/paper/auto/paper.md:57-57`） | RNA+ATAC 上竞争力强，ARI/ACC 排名突出 | 部分 baseline 在子指标上仍有竞争力 |
| unlabeled RNA+ATAC | 3 个 unlabeled datasets，用 ASW/DB/CH（`paper source/paper/auto/paper.md:63-63`） | 无标签场景中 embedding/clustering geometry 有用 | 内部指标不能替代真实生物标签 |
| batch integration | Figure 3 使用 bio-conservation、batch-correction、aggregate metrics（`paper source/paper/auto/paper.md:739-739`） | 批次混合和生物结构保留 | batch model 代码是独立 variant |
| tri-modal TEA-seq | Figure 4 比较 RNA/ADT/ATAC 组合并做 marker concordance（`paper source/paper/auto/paper.md:741-741`） | 三模态输入可提升表示和解释 | 单个 TEA-seq case 不能代表所有三模态组合 |
| disease applications | Alzheimer brain、kidney cancer、qPCR validation（`paper source/paper/auto/paper.md:745-749`） | embedding/clusters 能支持下游生物发现 | 调控、通信、疾病进展多为下游解释，不是模型直接因果输出 |

补充表说明 RNA+ADT 和 RNA+ATAC 表格值是 `n=10 independent experiments` 的均值与标准差（`output_supp_md/41467_2026_73055_MOESM1_ESM/auto/41467_2026_73055_MOESM1_ESM.md:178-184`）。但是发布代码中单一全 benchmark 十次重复 orchestrator **Not found**；这不否定论文表格，但限制了从代码仓库直接复现整篇 benchmark 的便利性。

### 7. 代码和论文最重要的差异

1. **KNN 输入不同**：论文说在 $\mathbf{X}^{con}$ 上构图；代码默认先 PCA 到 100 维再 cosine KNN（`scMAGCA/scMAGCA/scMAGCA.py:25-37`）。
2. **adversarial loop 更简单**：论文写 minimax；代码是一个 BCE loss 加到同一个 optimizer step（`scMAGCA/scMAGCA/scMAGCA.py:113-122`）。
3. **benchmark 参数是 dataset-specific**：默认 $\alpha,\beta,\gamma$ 存在，但 shell scripts 对多个 dataset 覆盖权重（`scMAGCA/scripts/run_scMAGCA_script.sh:1-42`）。
4. **batch 模型不是 base model 原封不动套用**：`scMAGCA_batch.py` 使用 `z_dim=8`，并把 batch one-hot 拼进 encoder/decoder/ZINB heads（`scMAGCA/scMAGCA/scMAGCA_batch.py:38-60`）。
5. **完整 benchmark runner Not found**：仓库有核心包、教程、figure notebooks/R scripts、precomputed CSVs 和部分脚本，但没有一个统一 CLI 覆盖所有论文 dataset、十次重复和所有 figure。

### 8. 复现和学习建议

如果目标是理解方法，先按这个顺序读：

1. `claude_notes.md`：看变量、equation、claim 和 open gaps。
2. `doc_method.md`：看数学和流程。
3. 本文件：用中文串起计算直觉。
4. `doc_code.md`：看代码和论文的 exact/partial/Not found 对照。
5. 代码：从 `scMAGCA/scMAGCA/run_scMAGCA.py` 进入，再读 `scMAGCA/scMAGCA/scMAGCA.py`、`layers.py`、`loss.py`、`preprocess.py`。

如果目标是实际复现，建议先跑一个教程或单一 dataset，而不是直接复现整篇论文：

1. 固定对应 dataset 的 `--alpha/--beta/--gama`、feature filters 和 `ad_out`。
2. 检查工作目录，因为模型会写 `../datasets/<file>/raw/raw.pt` 和 `../results/`。
3. 对比 `results/` 中已有 embedding/prediction CSV。
4. 如果改 data loader，优先检查 ZINB target 与 batch output 的 shape。
5. 对 Figure 5-8 的生物解释只把 scMAGCA embedding/clusters 当作起点，后续 enrichment、communication、qPCR 分别需要各自证据。

### 9. 底线结论

scMAGCA 是一个代码基本可对应论文核心结构的多组学 integration/clustering 方法。最可靠的代码级理解是：它在选中特征上构建 PCA-smoothed cosine KNN cell graph，用四层 GCN 得到 32 维 latent embedding，通过 linear reconstruction、ZINB likelihood 和 Gaussian-prior discriminator 做预训练，再用 KMeans + Student-t target distribution + KL loss 精炼 cluster。论文展示了广泛 RNA+ADT、RNA+ATAC、batch、tri-modal 和疾病应用证据；但完整 paper-scale benchmark 复现不是一个单脚本流程，疾病机制和 biomarker 结论也应作为 embedding 后的下游解释与实验支持来读。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scMAGCA: Interpretable Modality-Aware Mapping of Gene Regulation in Single-Cell Multiomics

**Authors**: Wang et al.
**Journal**: Nature Communications, 2026
**DOI**: [10.1038/s41467-026-73055-7](https://doi.org/10.1038/s41467-026-73055-7)
**Code**: [github.com/zemingzhou30/scMAGCA](https://github.com/zemingzhou30/scMAGCA)
**Workspace**: `integration_multimodal/scMAGCA`

---

### Executive Summary

scMAGCA is a graph-adversarial autoencoder for paired or multimodal single-cell data. It integrates RNA, ADT, ATAC, and related modalities by building a cell-cell graph from concatenated features, encoding the graph with GCN layers, modeling sparse raw counts with ZINB decoder heads, regularizing the latent space against a Gaussian prior, and refining clusters with KMeans plus KL divergence.

The main contribution is the combination of five components in one clustering-oriented framework: graph topology, nonlinear GCN embedding, dropout-aware count likelihood, adversarial latent regularization, and interpretable latent/feature analysis. The paper reports broad performance across RNA+ADT, RNA+ATAC, batch, tri-modal TEA-seq, Alzheimer's mouse brain, and kidney cancer multiome settings.

**Reproducibility rating: 3/5.** The core package, tutorials, figure notebooks/R scripts, precomputed results, and source links are available. Core architecture matches the paper well. Full paper-scale reproduction is harder because benchmark orchestration is distributed, dataset-specific loss weights are used, figure analyses rely on notebooks and precomputed CSVs, and some implementation details are not foregrounded in the paper.

---

### Method Overview

scMAGCA starts with paired single-cell modality matrices. It selects informative features, normalizes/log-transforms them, and concatenates them into `X_con`; raw selected counts are retained as `X_con_raw` for ZINB. A KNN cell graph is built using cosine similarity. The implementation uses PCA to 100 components before the KNN step, which is a meaningful code-level detail not emphasized in the paper.

The model has two training phases:

1. **Pretraining** learns an integrated embedding with a GCN encoder and optimizes MSE reconstruction, ZINB count likelihood, and Gaussian-prior adversarial loss.
2. **Clustering refinement** initializes centroids with KMeans and optimizes MSE, ZINB, and KL divergence between Student-t soft assignments and a sharpened target distribution.

Outputs are cell embeddings, cluster labels, and latent factors/features used for downstream biological interpretation. See `doc_method.md` for the mathematical walkthrough and `doc_code.md` for code-paper mapping.

**Prior-method context.** The paper positions scMAGCA against Seurat v4/WNN (*Cell*, 2021), totalVI (*Nature Methods*, 2021), Cobolt (*Genome Biology*, 2021), scMM (*Cell Reports Methods*, 2021), GLUE (*Nature Biotechnology*, 2022), MOFA+ (*Genome Biology*, 2020), DeepMAPS (*Nature Communications*, 2023), scMDC (*Nature Communications*, 2022), MIDAS (*Nature Biotechnology*, 2024), and MultiVI (*Nature Methods*, 2023). Its novelty claim is not that each component is individually new, but that graph convolution, adversarial latent regularization, ZINB count modeling, and DEC-style clustering are combined into a modality-aware single-cell multi-omics framework.

---

### Evaluation and Claims

The paper evaluates scMAGCA across several use cases:

| Setting | Main Evidence | What It Supports |
|---|---|---|
| RNA+ADT benchmarks | 14 datasets, held-out aggregate over 9 after 5 development datasets | Strong clustering performance against multimodal baselines |
| RNA+ATAC benchmarks | 14 labeled datasets, held-out aggregate over 9 after 5 development datasets | Competitive/top clustering, especially ARI/ACC |
| Unlabeled RNA+ATAC | ASW, DB, CH on 3 datasets | Useful unsupervised structure when labels are absent |
| Multi-batch integration | GSE164378 plus supplementary datasets | Batch mixing while preserving cell-type structure |
| Tri-modal TEA-seq | RNA, ADT, ATAC combinations | Added modalities improve clustering and biological concordance |
| Functional genomics | PBMC, Alzheimer's mouse brain, kidney cancer | Embeddings can feed marker, factor, enrichment, motif, and communication analyses |
| Biomarker validation | Kidney cancer qPCR for LACTB2/NCOA2 | Orthogonal support for selected downstream biomarkers |

The strongest methodological evidence is clustering and embedding performance. The strongest biological evidence comes when computational findings are supported by marker concordance, gene activity, motif enrichment, and qPCR. Disease mechanism and communication claims should be read as downstream interpretation rather than direct causal inference by the model.

---

### Code-Paper Validation

Overall fidelity is **medium-high**. Verified matches include:

- cosine KNN graph with default `k=30`
- four-layer GCN encoder with widths `{m, 1024, 256, 64, 32}`
- BatchNorm1d and PReLU in the encoder
- linear decoder from 32 dimensions back to feature space
- ZINB mean, dispersion, and dropout heads
- Gaussian-prior discriminator
- Adam AMSGrad pretraining and Adadelta refinement
- KMeans initialization, Student-t assignment, target distribution, and KL clustering loss
- separate tri-modal and batch-aware model variants

Important differences:

- KNN graph construction uses PCA to 100 components before cosine KNN.
- Adversarial training is implemented as a simpler BCE regularization path, not a clearly alternating minimax loop.
- Benchmark scripts use dataset-specific `alpha`, `beta`, and `gama` values rather than only the paper defaults.
- The batch model uses `z_dim=8` and appends batch one-hot indicators, so it differs from the base 32-dimensional architecture.
- A single script for all reported benchmark datasets and ten independent runs was not found.

---

### Practical Reproducibility

**Available artifacts**

- GitHub source code and PyPI package.
- Tutorials for RNA+ADT, RNA+ATAC, tri-modal, and batch examples.
- Figure notebooks/R scripts and precomputed result files.
- Nature article PDF, supplementary information, rendered figure pages, and converted markdown in this workspace.

**Barriers**

- Some dataset paths and run scripts are example-style rather than a portable end-to-end benchmark pipeline.
- Published-style results depend on dataset-specific shell commands and precomputed outputs.
- Several downstream figure analyses are notebook/R based, not clean CLI pipelines.
- Large `.h5ad`, result, PDF, and figure files need careful git hygiene.
- The ZINB loss path should be audited if adapting the PyG batching behavior to new datasets.

**Recommended reproduction path**

1. Start with a tutorial dataset and verify package installation.
2. Use the relevant model class: two-modality, three-modality, or batch.
3. Reproduce one benchmark dataset with the provided script settings, including dataset-specific loss weights.
4. Compare embeddings/labels against the provided `results/` outputs.
5. Treat full paper-scale reproduction as a separate workflow requiring dataset acquisition, notebook execution, and figure-specific scripts.

---

### Bottom Line

scMAGCA is a credible multimodal single-cell integration method with a released implementation that largely matches the core paper architecture. The most useful code-grounded understanding is that the method is a GCN autoencoder over a PCA-smoothed cosine KNN cell graph, trained with reconstruction, ZINB, Gaussian-prior regularization, and DEC-style clustering. Its biological applications are broad and often plausible, but downstream regulatory and disease claims should be interpreted as analyses built on top of the embedding rather than causal outputs of the neural model itself.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
