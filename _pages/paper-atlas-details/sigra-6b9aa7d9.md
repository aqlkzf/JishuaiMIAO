---
layout: default
permalink: /paper-atlas/sigra-6b9aa7d9/
title: "SiGra"
nav: false
description: "若一个细胞自身的表达很稀疏，周围细胞的表达、它的位置关系、以及该处的细胞形态/染色信号可以提供互补证据。SiGra 不是简单地把邻居平均，而是让图 Transformer 学习“哪个邻居、哪一种模态更有用”。"
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
      <span>Domain Clustering</span>
      <span>Nature Communications · 2023</span>
    </div>
    <h1>SiGra</h1>
    <p>SiGra: single-cell spatial elucidation through an image-augmented graph transformer</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SiGra：用图 Transformer 联合图像与表达来理解空间组织

### 它要解决什么问题？

空间转录组同时有“位置”和“表达”，但表达矩阵常常稀疏、带噪声；这会让细胞/空间域边界模糊，也会漏掉本应出现的标记基因。Seurat v4 和 Scanpy 的常规聚类主要从表达出发；stLearn 使用邻域和组织图像，BayesSpace 将表达与空间邻域作贝叶斯建模，SpaGCN 则用图卷积处理空间图（论文 `paper.md:20-27,238-244`）。SiGra（*Nature Communications*, 2023）进一步把每个细胞或 spot 周围的多通道图像也作为输入，目标是同时得到更好的空间聚类表示和增强后的表达。

### 一句话直觉

若一个细胞自身的表达很稀疏，周围细胞的表达、它的位置关系、以及该处的细胞形态/染色信号可以提供互补证据。SiGra 不是简单地把邻居平均，而是让图 Transformer 学习“哪个邻居、哪一种模态更有用”。

### 输入、输出与数据表示

把样本写成空间图 $G=(V,E)$：节点 $v_i$ 是一个细胞或 spot，边 $e_{ij}$ 连接空间上相近的两个节点。每个节点还携带：

- 基因表达向量 $\boldsymbol g_i$；
- 多通道图像块 $\boldsymbol M_i$，展平后成为图像向量 $\boldsymbol x_i$；
- 邻居集合 $\mathcal N(v_i)$。

论文把这些定义在 `paper.md:171-177`。输出有两类：混合分支的重建表达 $\hat{\boldsymbol g}_{h,i}$（增强表达），以及混合隐变量 $\boldsymbol z_{h,i}$（用于聚类）。

```text
原始 counts + 坐标 + 组织图像
          │
          ├─ 归一化/对数变换、按中心坐标裁剪图像块
          ├─ 以距离建图，得到空间邻接 G
          ▼
图像 M_i ── 图 Transformer ── z_M,i ── 解码 ── ĝ_M,i
表达 g_i ── 图 Transformer ── z_g,i ── 解码 ── ĝ_g,i
                         │
                  拼接 [z_M,i, z_g,i]
                         ▼
                  混合图 Transformer
                         │
                   z_h,i 与 ĝ_h,i
                         │
             三个重建误差联合训练；z_h,i 用于聚类
```

代码中的对应关系很直接：`Cal_Spatial_Net` 从 `adata.obsm['spatial']` 构造 radius 或 kNN 图并保存到 `adata.uns['Spatial_Net']`（`SiGra_model/utils.py:204-240`）；`Transfer_img_Data` 用同一套边生成 PyG 的表达图和图像图（`:138-177`）。CosMx 流程会将 counts 归一化到 10,000、取对数、裁剪 120×120 图像块并用半径 80 建图（`train_nanostring.py:24-63`），与论文的具体预处理相符。

### 三条分支到底在学什么？

1. **图像分支**：从 $\boldsymbol x_i$ 和邻域图像学得 $\boldsymbol z_{M,i}$，再预测该节点的基因表达 $\hat{\boldsymbol g}_{M,i}$。这要求模型从形态/染色中恢复转录信息。
2. **表达分支**：从 $\boldsymbol g_i$ 与邻域表达得到 $\boldsymbol z_{g,i}$，再得到 $\hat{\boldsymbol g}_{g,i}$。这是带空间上下文的表达自编码器。
3. **混合分支**：把前两条隐变量拼接，得到 $\boldsymbol z_{h,i}$ 和最终的 $\hat{\boldsymbol g}_{h,i}$。它是作者用于聚类和“增强表达”的主要输出（`paper.md:183-188,229`）。

源码 `TransImg` 的 `conv*` 是表达支路，`imgconv*` 是图像支路，`neck/neck2/c3/c4` 是拼接后的混合支路；前向传播依次返回 `h2, img2, c2, h4, img4, c4`（`SiGra_model/transModel.py:210-258`）。因此可对应为 $z_g,z_M,z_h$ 与三种重建。默认情况下 `c4` 的输出维度是 `in_dim`，所以 `cout` 是对基因向量的混合重建，而不是图像重建。

### 图注意力如何使用邻居？

论文将第 $l$ 层的更新写成：

$$
\boldsymbol h_i^{(l+1)}=\operatorname{ReLU}\!\left(W_1^{(l)}\boldsymbol h_i^{(l)}+\sum_{v_j\in\mathcal N(v_i)}\alpha_{i,j}V_j^{(l)}\right).
$$

其中 query/key/value 为

$$
Q_i^{(l)}=W_Q^{(l)}\boldsymbol h_i^{(l)}+b_Q^{(l)},\quad
K_j^{(l)}=W_K^{(l)}\boldsymbol h_j^{(l)}+b_K^{(l)},\quad
V_j^{(l)}=W_V^{(l)}\boldsymbol h_j^{(l)}+b_V^{(l)}.
$$

$\alpha_{i,j}$ 是节点 $i$ 对邻居 $j$ 的注意力权重：相似、信息量大的邻居可获得更大权重（论文 `paper.md:194-212`）。不过要区分“论文公式”与“源码细节”：源码调用 PyG 的 `TransformerConv` 来实现注意力，并在可见层使用 ELU（`transModel.py:216-255`），没有手写上述 Q/K/V 和 ReLU。因此这是概念上高度一致、实现细节上 **Partial** 的匹配。

### 为什么无需标签也能训练？

监督信号就是输入表达本身。论文的损失是：

$$
L=\sum_{i=1}^{N}\lambda_1L_{M,i}+\lambda_2L_{g,i}+L_{h,i},
$$

三项分别约束图像、表达和混合分支去重建同一个基因表达目标（`paper.md:215-226`）。对单细胞空间数据，论文给出 $\lambda_1=\lambda_2=0.1$；Visium 为 1 和 1。

`train_nano_fov` 将 `bgene`、`bimg` 输入模型，计算 `mse(bgene,gout)`、`mse(bgene,iout)`、`mse(bgene,cout)`，用默认权重 0.1、0.1、1.0 合成 loss（`train_transformer.py:909-977`）。一个易混点是变量名：`gloss` 对应表达支路 `gout`，`iloss` 对应图像支路 `iout`；不要仅凭变量名前缀反过来改写论文中的 $L_M/L_g$ 含义。

### 从隐变量到空间域

推理时，代码把混合隐变量 `cz` 写到 `adata.obsm['pred']`（`train_transformer.py:219-231`）。NanoString 流程在 `pred` 上建立邻居图、搜索合适分辨率，然后运行 Scanpy Leiden（`train_nanostring.py:100-170`）。

- **spot 级数据**：论文直接对 $z_h$ 作 Leiden 聚类。
- **单细胞数据**：先得到 Leiden 细胞类别；再用滑动窗口统计每个窗口内各类别比例 $\boldsymbol c_{i,j}=[q_1,\ldots,q_t]$；最后层次聚类窗口得到更大尺度的空间域（`paper.md:232-235`）。

源码确有这一步：`sliding_window` 统计每个窗口的各类别计数，`cell2domain` 做 L1 归一化后以 Ward 方法聚类（`functions/cell2domain/sigra_domain.py:56-96`）。但该函数默认 `kernel_size=500, stride=100`，不能仅凭本地源码确认论文补充材料中 100 µm/10 µm 的特定设置；补充 Markdown 未获取，因此这部分精确调参仍是 **MISSING**。

### 作者报告的验证与应有的谨慎

论文在 CosMx 肺癌、MERSCOPE 小鼠肝脏、以及 12 张 DLPFC Visium 切片上比较 Seurat、Scanpy、stLearn、SpaGCN、BayesSpace。报告的 DLPFC 中位 ARI 为 SiGra 0.57，其他方法为 0.28--0.44（`paper.md:125-136`）；CosMx 也报告更高的 ARI（`paper.md:68-85`）。这些是论文结果，当前工作区没有数据、预训练权重与一键实验清单，故没有在此复跑。

六张本地图像确实展示了预期的现象：图 2/5 的域图与基线比较，图 3/4/6 的原始与增强表达比较。但“图上更平滑/更集中”不等于已逐点证明表达一定真实；应结合人工标注、bulk 对照、独立实验和可能的过度平滑风险解释。当前仓库对核心算法是很好的源码证据，但对补充调参和完整可复现实验仍有明确边界。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SiGra: image-augmented graph transformer for spatial domains and expression enhancement

### Problem

Spatial transcriptomics can be noisy, sparse, and low coverage, obscuring domain boundaries and marker genes. Common single-cell workflows such as Seurat v4 and Scanpy use expression but not the full spatial-image modality; stLearn uses histology and neighbourhood information, BayesSpace models expression plus neighbourhoods statistically, and SpaGCN uses a graph constructed from expression/histology (`paper.md:20-27,238-244`). SiGra (Nature Communications, 2023) is designed to use per-cell/spot images, expression, and spatial adjacency together.

### Method in brief

SiGra builds a coordinate-neighbour graph, attaches cropped multichannel image features and expression to every node, then uses image, gene, and hybrid graph-transformer encoder-decoders. The three branches reconstruct expression under a weighted MSE objective; the hybrid latent is used for clustering and the hybrid reconstruction is the enhanced profile (`paper.md:33-59,171-229`). In the checked source, this core is represented by `Cal_Spatial_Net`, `Transfer_img_Data`, `TransImg`, and the three-MSE training loop (`SiGra_model/utils.py:138-240`; `SiGra_model/transModel.py:210-258`; `SiGra_model/train_transformer.py:909-977`).

### Evaluation reported by the paper

The study evaluates NanoString CosMx lung cancer (20 FOVs; 83,621 cells), Vizgen MERSCOPE mouse liver (395,215 cells), and 12 human DLPFC 10x Visium slices (`paper.md:65-85,105-136`). Against Seurat, Scanpy, stLearn, SpaGCN, and BayesSpace, it reports:

- CosMx: overall ARI 0.55, with median SiGra ARI 0.59 across FOVs; the paper reports a multimodal-image ablation ARI of 0.59 versus gene-only median 0.40 (`paper.md:68-85`).
- DLPFC: median ARI 0.57, compared with 0.28 (Scanpy), 0.29 (Seurat), 0.39 (stLearn), 0.40 (SpaGCN), and 0.44 (BayesSpace) (`paper.md:125-136`).
- Enhancement analyses: more concentrated marker patterns, additional DEGs, and altered candidate ligand-receptor results in lung and liver examples (`paper.md:88-119,139-150`). Main figures were read directly; they visually show the intended raw-versus-enhanced and baseline-versus-SiGra contrasts.

### Reproducibility and code-paper match

**Code-paper fidelity: high for the central method.** The repository directly implements radius graphs, flattened image features, the three `TransImg` branches, weighted reconstruction losses, Leiden on the hybrid embedding, and a sliding-window/hierarchical cell-to-domain function. The paper's generic Q/K/V ReLU equations are only a **Partial** match: source delegates attention to PyG `TransformerConv` and uses ELU in the live model. The live `cell2domain` defaults also do not establish the paper's supplementary physical-unit window settings.

The paper links a Python package and tutorials (`paper.md:279-282`), and the workspace has a GitHub snapshot with recorded source commit `4786b2e4e33cb2b2436145e0ca23c9255ad2611e`. It does **not** contain the primary datasets, pretrained results, acquired supplementary markdown, or one reproducible end-to-end experiment manifest. Consequently, published results are documented rather than rerun here, and supplementary-only architecture/tuning details remain **MISSING**.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
