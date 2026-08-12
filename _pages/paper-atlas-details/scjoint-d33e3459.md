---
layout: default
permalink: /paper-atlas/scjoint-d33e3459/
title: "scJoint"
nav: false
description: "scJoint 不是把 RNA 计数和 ATAC 峰矩阵直接拼在一起，也不是要求同一细胞有成对测量。它先把 ATAC 峰转换为按基因汇总的活性分数，使 RNA 与 ATAC 拥有同一组基因特征；随后让两种模态共用一个线性编码器，在 RNA 标签监督、低维表示约束和跨模态余弦对齐的共同作用下学习 64 维空间。第一轮训练后，用 RNA 邻居给 ATAC 传标签；第二轮再用这些伪标签和中心损失收紧同类细胞，最后重新做一次 KNN 标签迁移。"
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
      <span>Nature Biotechnology · 2022</span>
    </div>
    <h1>scJoint</h1>
    <p>scJoint integrates atlas-scale single-cell RNA-seq and ATAC-seq data with transfer learning</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-021-01161-6" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scJoint：用带标签 RNA 参考图谱迁移注释到 ATAC

### 一句话先讲清楚

scJoint 不是把 RNA 计数和 ATAC 峰矩阵直接拼在一起，也不是要求同一细胞有成对测量。它先把 ATAC 峰转换为按基因汇总的活性分数，使 RNA 与 ATAC 拥有同一组基因特征；随后让两种模态共用一个线性编码器，在 RNA 标签监督、低维表示约束和跨模态余弦对齐的共同作用下学习 64 维空间。第一轮训练后，用 RNA 邻居给 ATAC 传标签；第二轮再用这些伪标签和中心损失收紧同类细胞，最后重新做一次 KNN 标签迁移。

这里的“迁移学习”因此有明确方向：**带标签的 scRNA-seq 是源域，未标注的 scATAC-seq 是目标域**。输出既包括 ATAC 细胞类型及置信分数，也包括可用于 tSNE/UMAP 的联合嵌入。

### 证据范围

- 论文：`paper source/paper/vlm/paper.md`，DOI `10.1038/s41587-021-01161-6`。
- 主图：`paper source/paper/vlm/images/`；图 1 是方法与规模基准，图 2–5 分别覆盖小鼠图谱、全图谱重注释、PBMC 多模态和配对 SNARE-seq。
- 补充材料：`output_paper_supp_md/paper_supp1/vlm/paper_supp1.md` 与本地 `paper_supp1.pdf`、`paper_supp2.pdf`。
- 代码：`scJoint_code/`，来源 `https://github.com/SydneyBioX/scJoint`，本地记录提交 `cbbfa5d7e7faa35f3d725bd5257507a01a22810f`。

下面的实现结论以这个本地提交为边界，不假定当前 GitHub 默认分支仍与它相同。

### 输入为什么能进入同一个网络

RNA 的列是基因表达，原始 ATAC 的列却是开放峰；二者不能直接共享权重。论文先用 Signac 等流程把 ATAC 峰汇总成 gene activity score，再取两种数据共有的基因。代码的数据加载器对表达/活性矩阵逐元素二值化：

$$
x_{ig}^{\mathrm{bin}} = \mathbf{1}(x_{ig}>0).
$$

对应实现是 `util/dataloader_stage1.py:57-68` 和 `105-117`。这一步把“表达了多少”改成“是否检测到”，缓解两种模态量纲差异；代价是丰度信息被丢弃。CITE-seq/ASAP-seq 场景中的蛋白特征是例外：代码先二值化基因部分，再把连续蛋白矩阵原样拼接，因此不能笼统说 scJoint 的所有输入都二值化。

### 网络本身比示意图更简单

图 1a 看起来像一般神经网络，但本地实现只有两个线性层：

$$
z=f_\theta(x)=W_e x+b_e,\qquad o=W_c z+b_c,
$$

其中 $z\in\mathbb{R}^{64}$，$o\in\mathbb{R}^{K}$。`util/model_regress.py:5-20` 是共享的 `Linear(input_size, 64)` 编码器，`23-32` 是 `Linear(64, K)` 分类头；中间没有 ReLU、批归一化或多层隐藏网络。RNA 与 ATAC 复用同一组 $W_e,b_e$，这才是跨模态共同坐标系的结构来源。

### 第一步：同时保留结构、对齐模态、利用 RNA 标签

#### 1. NNDR：让 64 个坐标有变化、少冗余、中心稳定

论文的 neural-network dimension reduction（NNDR）由三部分构成：放大每个维度的批内变化、压低不同维度的相关性、把均值拉回零附近。直观上，如果所有细胞都映到同一点，逆离差项会变大；如果多个维度复制同一信号，非对角相关项会变大。

代码 `util/closs.py:29-42` 的实际形式可读为

$$
L_{\mathrm{red}}
= \operatorname{mean}|\operatorname{triu}(C,1)|
+ \frac{1}{\operatorname{mean}|z-\bar z|}
+ \operatorname{mean}|z|.
$$

需要注意，函数名 `cor()` 实际计算的是中心化后的样本**协方差** $C=(Z-\bar Z)^\top(Z-\bar Z)/(B-1)$，没有再除以各维标准差。因此论文称“correlation matrix”，代码并非严格的相关矩阵实现。这不会否定它抑制维度共变的意图，但会改变尺度敏感性。

#### 2. 余弦对齐：只要求最容易匹配的 ATAC 细胞靠近 RNA

对每个 ATAC 细胞，先在当前批次 RNA 嵌入中找最大余弦相似度；再只取这些最大值里最高的 $p$ 比例：

$$
L_{\cos}=-\frac{1}{|I_p|}\sum_{i\in I_p}
\max_j \frac{z_i^{A\top}z_j^R}{\|z_i^A\|_2\|z_j^R\|_2}.
$$

论文与默认配置均用 $p=0.8$。这不是建立一一对应，而是允许约 20% 目标细胞暂时没有可靠源域伙伴，适用于 RNA 与 ATAC 细胞类型不完全重合的情况。代码在 `util/closs.py:45-50,81-96` 用 `topk(max(cosine_sim(...)))` 实现这一逻辑。

#### 3. RNA 分类：让联合空间仍然表达细胞类型

RNA 细胞的已知标签通过交叉熵监督分类头：

$$
L_{\mathrm{CE}}=-\frac1B\sum_b\log \operatorname{softmax}(o_b)_{y_b}.
$$

`util/closs.py:134-140` 直接调用 PyTorch `cross_entropy`。第一阶段实际训练中，RNA 贡献分类与 NNDR，RNA/ATAC 都贡献 NNDR，ATAC–RNA 对贡献余弦对齐；`util/trainingprocess_stage1.py:94-148` 展示了共享编码器同时收到这些梯度。

此外，代码还对编码器和分类器显式加入系数 0.1 的参数绝对值均值，即 L1 正则（`util/closs.py:16-26`），论文方法公式没有列出这一项。它是复现时不能忽略的代码级训练约束。

### 第二步：KNN 把 RNA 标签传给 ATAC

阶段一完成后，代码把嵌入做 $L_2$ 归一化，再以 RNA 嵌入和真实 RNA 标签训练 30 邻居分类器；每个 ATAC 细胞取多数票标签。`util/knn.py:48-123` 是完整路径。

这里存在一个重要论文—代码差异。论文把置信度写成多数类 RNA 邻居的 softmax 概率均值：

$$
\hat p_i=\frac1{30}\sum_{j\in M(i)}g_j(k^*).
$$

本地代码却调用 `compute_hit_conf()`：同类邻居加 $1/h_j$，异类邻居减 $1/h_j$，其中 $h_j$ 是该 RNA 细胞被所有 ATAC 查询命中的次数（`util/knn.py:11-17,33-44,114-117`）。因此保存的 `_knn_probs.txt` 是命中频率校正后的有符号分数，不是论文公式中的 softmax 概率；将它解释为严格的 $[0,1]$ 概率会出错。

为控制图谱规模，RNA 超过 20,000 个细胞时，代码按固定间隔均匀抽样到约 20,000 个作为 KNN 参考（`util/knn.py:62-85`）。这是可扩展性的实际组成部分，但论文主方法描述没有突出这一上限。

### 第三步：用伪标签把同类细胞进一步拉紧

阶段二产生的 ATAC 标签被当作伪标签加入训练。中心损失希望每个嵌入接近其类别中心：

$$
L_{\mathrm{center}}=\frac1B\sum_b\|z_b-c_{y_b}\|.
$$

论文公式写的是平方欧氏距离，并描述按批次样本平均来修订中心；本地 `util/closs.py:100-131` 则把中心定义成可训练 `nn.Parameter`，由 SGD 反向传播更新，而且在平方距离矩阵后调用 `sqrt`，最终惩罚的是欧氏距离而非平方欧氏距离。阶段三代码还同时对 RNA 和 ATAC 应用中心损失，而不是只约束目标域。

论文总目标概括为

$$
L_{\mathrm{scJoint}}=L_1+\lambda L_{\mathrm{center}},
$$

常规数据默认 $\lambda=1$；多技术小鼠图谱为加强批次混合使用 10。对发育连续轨迹，论文提出 Step 3'：关闭阶段三交叉熵，避免强制离散分类破坏连续结构；代码配置 `with_crossentorpy` 对应此开关。

阶段三之后再次运行 KNN。如果标签改变，就以最终嵌入的邻居结果更新标签和分数。于是最终输出不是网络分类头直接给出的 ATAC softmax 类别，而是共享嵌入上的邻域迁移结果。

### 从图 1 到图 5 应该怎样读

- **图 1** 先证明任务和规模：共享编码器接收 gene expression 与 gene activity；超过一百万细胞的基准约两小时完成。这个规模结论同时依赖线性模型、批训练和代码中的 RNA KNN 抽样，并不等于任意硬件/新版本都能复现同一时间。
- **图 2** 在 19 个重叠小鼠细胞类型上检验“模态混合且类型分开”。scJoint 报告 84% 转移准确率，并在只保留 20% RNA 训练细胞时仍较稳定；这些是论文基准结果，不是本工作区重新运行所得。
- **图 3** 用独立 marker 证据检查全图谱重注释：原先 unknown/endothelial 中被转成 stromal/fibroblast 的细胞具有 Col1a1、Col1a2、Dcn、Ccdc80 活性。这里的论证链是“迁移标签 → 在 ATAC 原空间聚集 → marker 活性支持”，而非仅凭联合 tSNE 宣称新细胞类型。
- **图 4** 把输入扩展到 CITE-seq/ASAP-seq 的基因加蛋白特征，展示条件间 PBMC 整合和 142 个候选 NKT 细胞。NKT 解释来自 CD3/GNLY 及蛋白 marker 组合，不能只由 scJoint 标签本身推出。
- **图 5** 用配对 SNARE-seq 作验证，但 scJoint 运行时不使用配对关系；它与利用配对信息的方法比较的是嵌入和类型分离表现。因此“在配对数据上评估”不等于“scJoint 是配对整合模型”。

补充图进一步覆盖错标、训练子采样、超参数 $p$/$\lambda$、不同二值化阈值和更多细胞类型结果。它们支持稳定性范围，但不能证明方法对论文未测试的数据分布普遍稳健。

### 论文、代码与可复现性的边界

#### 与论文基本一致

- RNA 标签监督、ATAC 无标签输入，共享 64 维线性编码器。
- NNDR、top-$p$ 余弦对齐、RNA 交叉熵的阶段一结构。
- 30-NN 多数票、阶段三中心损失、最终再次 KNN。
- RNA/ATAC 基因部分二值化，蛋白特征连续拼接。

#### 部分一致或不一致

- 论文的“相关矩阵”在代码中是未标准化协方差。
- 论文中心是批次均值式更新，代码中心是可训练参数；论文用平方距离，代码用开方后的欧氏距离。
- 论文 KNN 分数是 softmax 概率均值，代码是 hit-count 加减权重。
- 代码有论文目标未明列的 L1 正则，系数默认为 0.1。
- 训练数据集的 `__getitem__` 会随机另取索引，形成有放回抽样；“一个 epoch”不严格等于每个细胞恰好访问一次。

#### 尚未在本工作区复现

本地仓库保留旧式 PyTorch 依赖、配置文件驱动的数据路径、预计算 checkpoint、编译的 `libutility.so` 和大体积示例数据。此次分析没有重建论文全部数据预处理、旧 CUDA/PyTorch 环境，也没有重新训练百万细胞基准或重画全部主/补充图。因此可以验证算法与本地提交的实现关系，但不能把论文的运行时间、准确率和所有生物学结论表述为本地复现实验结果。

### 最简心智模型

把 scJoint 看成五个连续动作最准确：

1. ATAC 峰先变成基因活性，两种模态的基因输入二值化；
2. 同一个线性投影把 RNA 和 ATAC 放进 64 维空间；
3. NNDR 防塌缩/冗余，余弦项对齐模态，RNA 标签保留细胞类型；
4. RNA 邻居给 ATAC 产生第一版伪标签；
5. 中心损失收紧同类细胞，再用 KNN 给出最终标签与联合嵌入。

它的优势来自“简单共享表示 + 强监督标签迁移 + 可扩展邻域分类”，而不是复杂深层网络；它的主要风险也由此而来：输出质量继承 RNA 参考标签、共同基因与 gene activity 构造的偏差，代码中的置信分数和中心更新又与论文公式并不完全相同。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## scJoint: Transfer Learning for Atlas-Scale scRNA-seq and scATAC-seq Integration

**Paper**: "scJoint integrates atlas-scale single-cell RNA-seq and ATAC-seq data with transfer learning"
**Authors**: Yingxin Lin, Tung-Yu Wu, Sheng Wan, Jean Y. H. Yang, Wing H. Wong, Y. X. Rachel Wang
**Journal**: Nature Biotechnology, 2022 (published online January 2022)
**DOI**: 10.1038/s41587-021-01161-6
**Code**: https://github.com/SydneyBioX/scJoint

---

### Motivation & Novelty

Single-cell ATAC-seq (scATAC-seq) reveals chromatin accessibility — which genomic regions are "open" in each cell — providing complementary epigenomic information to gene expression (scRNA-seq). However, ATAC data is extremely sparse (most peaks are zero), making cell-type identification difficult. Large, well-annotated scRNA-seq atlases exist (Tabula Muris, Human Cell Atlas) but there is no direct way to transfer their rich cell-type annotations to newly generated ATAC data.

**Limitations of existing methods**:
- **Manifold alignment** (MATCHER, *Genome Biol.* 2017; MAGAN, *ICML* 2018): requires globally matching distributions — too restrictive for atlas data from diverse tissues
- **Matrix factorization** (Liger, *Cell* 2019; coupled-NMF, *PNAS* 2018): requires separate feature selection before integration; sensitive to gene selection; OOM at >500k cells
- **Correlation-based** (Seurat v3, *Cell* 2019; Conos, *Nature Methods* 2019): require highly variable gene selection; fail at atlas scale
- **Autoencoder methods**: most require paired measurements; co-training multiple autoencoders simultaneously is unstable without pairing

**scJoint's contributions**:
1. **Integrated dimension reduction**: NNDR loss combines feature extraction with modality alignment in a single training objective — no separate "highly variable gene selection" step; low-dimensional features update throughout training
2. **Flexible partial-overlap alignment**: cosine similarity loss with $p=0.8$ accommodates RNA and ATAC datasets that don't share all cell types
3. **Semisupervised transfer via weight sharing**: one shared encoder for RNA and ATAC enables label transfer without paired data
4. **Atlas-scale scalability**: handles 1M+ cells in ~2h; Seurat and Liger fail above 500k cells due to OOM

---

### Method Overview

scJoint treats RNA-ATAC integration as **domain adaptation**: RNA is the labeled source domain, ATAC is the unlabeled target domain. A single shared linear encoder (input → 64-dim embedding) maps both modalities to a common space.

**Input**: Binarized gene expression (RNA) and gene activity scores (ATAC) — both converted to 0/1 presence/absence before training.

**Three training steps**:
1. **Step 1**: Joint dimension reduction (NNDR loss for orthogonal features) + cross-modal alignment (cosine similarity loss for best-matching ATAC-RNA pairs) + supervised classification (cross-entropy on labeled RNA)
2. **Step 2**: KNN label transfer — k=30 nearest RNA neighbors in the shared embedding space determine each ATAC cell's label via majority vote
3. **Step 3**: Metric learning refinement — center loss (pulls same-type cells toward shared class centers) and cross-entropy on both RNA and pseudo-labeled ATAC

**For developmental data** (continuous trajectories): Step 3 omits cross-entropy to preserve continuous structure.

See `doc_method.md` for full mathematical derivation and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets
| Dataset | Cells | Cell types | Modalities |
|---|---|---|---|
| Mouse atlas subset (Tabula Muris + Cusanovich) | 101,692 | 19 overlapping | scRNA-seq (FACS + droplet) + scATAC-seq |
| Mouse atlas full | 177,577 | 73 RNA / 29 ATAC | Same as above |
| Human fetal atlas benchmark | up to 1,089,769 | 54 | scRNA-seq + scATAC-seq |
| PBMC multimodal (Mimitou et al. 2021) | 18,088 | 8 | CITE-seq + ASAP-seq |
| SNARE-seq mouse cortex (Chen et al. 2019) | 9,190 | 22 | Paired RNA + ATAC |

#### Key Results
**Label transfer accuracy** (mouse atlas subset, 19 cell types):
- scJoint: **84%** vs. Seurat v3 70%, Conos 71% (+14%, +13%)

**Label transfer accuracy** (mouse atlas full):
- scJoint: **77%** vs. Seurat 60%, Conos 55%

**PBMC multimodal** (CITE-seq + ASAP-seq combined):
- Cell-type silhouette coefficient F1: **0.59** (scJoint) vs. 0.43 (Seurat), 0.31 (Conos), 0.53 (Liger)
- Label transfer: **87%** (scJoint) vs. 75% (Seurat), 56% (Conos)

**Scalability**: Only method completing >500k cell integration (Seurat, Liger OOM). 1M cell run: 2h.

**Paired data** (SNARE-seq, unpaired methods): scJoint 70.9% vs. Seurat 70.1%, Conos 49.5% — comparable to paired methods (scAI, MOFA+, Seurat WNN)

#### Evaluation Metrics
- **Label transfer accuracy**: fraction of ATAC cells correctly labeled (compared to original annotations)
- **Silhouette coefficient F1**: F1 score combining cell-type silhouette (high = good biological grouping) and 1-modality silhouette (high = good modality mixing)
- **Trajectory conservation score**: Spearman correlation of diffusion pseudotime before/after integration

#### Biological Discoveries
- Identified 5,954 stromal cells and fibroblasts in mouse atlas ATAC data originally labeled as 'unknown' or 'endothelials' — validated by Col1a1, Col1a2, Dcn, Ccdc80 marker genes
- Discovered natural killer T (NKT) cell subpopulation in PBMC — missed by Seurat and Conos; validated by CD3, CD56, CD57, CD244 protein expression

---

### Reproducibility

**Rating: 3/5**

**Strengths**:
- Code publicly available on GitHub with PyTorch implementation
- Five tutorial notebooks covering major use cases (10x PBMC, CITE-seq/ASAP-seq, Mouse Motor Cortex)
- All datasets publicly available (GEO accession numbers and URLs provided)
- R scripts for visualization and format conversion included
- Results reported to be stable across random seeds

**Weaknesses**:
- Data preprocessing (gene activity score generation from ATAC peaks) requires Signac (R package) and is not automated in the Python pipeline
- `config.py` must be manually edited for each dataset — no CLI interface
- `torch.set_num_threads(1)` is hardcoded in `main.py` for fair benchmarking; remove it for production use to enable multi-threaded loading
- C compiled library `libutility.so` may fail on some systems (architecture-dependent)
- PyTorch v1.0.0 requirement is outdated (2022 code); newer PyTorch versions may require minor updates
- KNN RNA subsampling (20k cap) is hardcoded and undocumented — could silently affect large atlas results
- No container/environment specification (no Dockerfile, conda yml, or requirements.txt with versions)

**Practical notes**:
- Input must be pre-processed to NPZ sparse format; use provided R scripts (`data_to_h5.R`) as starting point
- Gene activity matrices for ATAC must be pre-computed with Cicero or Signac before running scJoint
- For CITE-seq/ASAP-seq: protein data should NOT be binarized (only gene data is); concatenate after loading
- For mouse atlas-scale data: set `lambda=10` for strong batch correction between technologies; `lambda=1` is insufficient (visible in Supplementary Fig. S23)
- Training is deterministic given `config.seed = 1`; but Dataloader uses `random.seed(1)` (Python random, not PyTorch)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
