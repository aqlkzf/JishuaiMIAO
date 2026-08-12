---
layout: default
permalink: /paper-atlas/spaim-b994709e/
title: "SpaIM"
nav: false
description: "SpaIM 不直接把单细胞映射到空间位置。它把每个基因当成一个训练样本：scRNA-seq 侧用该基因在 K 个细胞类型中的平均表达作为“content”，ST 侧用同一基因在全部空间位置的表达向量作为“style/目标”。一个 ST autoencoder 从已测共同基因学习 ST 风格，另一个 ST generator 把同样的风格施加到 scRNA-seq content 上；"
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
      <span>Nature Communications · 2025</span>
    </div>
    <h1>SpaIM</h1>
    <p>SpaIM: single-cell spatial transcriptomics imputation via style transfer</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-63185-9" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpaIM：把 scRNA-seq 的“基因内容”翻译成 ST 平台的空间表达“风格”

### 一句话理解

SpaIM 不直接把单细胞映射到空间位置。它把每个基因当成一个训练样本：scRNA-seq 侧用该基因在 $K$ 个细胞类型中的平均表达作为“content”，ST 侧用同一基因在全部空间位置的表达向量作为“style/目标”。一个 ST autoencoder 从已测共同基因学习 ST 风格，另一个 ST generator 把同样的风格施加到 scRNA-seq content 上；训练完成后，generator 可把只在 scRNA-seq 中存在的基因转换成跨 ST spot/cell 的预测表达向量。

主要证据为论文 `paper source/PMC12375071/paper.md`、六张主图、补充 PDF，以及固定代码快照 `SpaIM/`（GitHub `QSong-github/SpaIM`，提交 `3d8b76b2658797d5a124a80ab0076a622461a5e7`）。

### 1. 为什么把问题叫“风格迁移”

对同一基因，scRNA-seq 和 ST 都包含生物身份信号，但测量方式不同：scRNA-seq 有更完整的基因覆盖，却没有目标切片的空间坐标；ST 保存空间结构，却可能稀疏或只测少量基因。SpaIM 将两者拆成：

- content：跨数据集应较稳定的基因—细胞类型表达关系；
- style：目标 ST 平台、组织切片和空间位置共同形成的表达分布特征。

这里的“style”不是图像纹理，也不是一个可直接解释的批次标签，而是通过 ST 表达与 Gram matrix 约束学习的潜在统计结构。论文 Supplementary Fig. 9 的 GradientShap 分析为 content/style 分离提供后验解释，但不证明两者在生物学上严格独立。

### 2. 真正的输入张量是什么

论文在共同基因上训练。代码 `dataset.py::aggreate_cell_types` 先按 scRNA-seq 的 `merge_cell_type`（或 Leiden）分组求均值，得到 $K\times G$ 矩阵；随后转置。于是 DataLoader 每次取出的一个样本对应一个基因：

- `seq_x`：长度 $K$，该基因在各单细胞群的平均表达；
- `spa_x`：长度 $N_{ST}$，该基因在所有 ST 位置的表达；
- `st_style`：全 1 的虚拟风格向量，默认维度 1。

因此模型学习的是从“基因在细胞类型上的轮廓”到“基因在空间位置上的轮廓”的全局函数，而不是 cell-to-spot 对齐。输出维度 `st_dim` 等于目标 ST 的位置数，这也意味着训练好的权重与目标切片的 spot/cell 布局绑定，不能在任意新切片上直接零样本复用。

### 3. ReST 层：逐层提取并融合 content 与 style

一个 recursive style transfer（ReST）层有 content encoder、style encoder 和 decoder。论文写作：

$$
h^{(l+1)}=C^{(l)}(h^{(l)}),\qquad
g^{(l+1)}=S^{(l)}(g^{(l)}),
$$

并从深层向浅层递归融合。乘法 $h\otimes g$ 调制 content，残差式加法把不同层次的融合结果送回输出空间。

当前代码固定实现两层：

- ST content/style encoder 都是 `N_ST → 512 → 256`；
- SC content encoder 是 `K → 256 → 512` 的命名/顺序组合，使两边在两个隐层维度对齐；
- decoder 为 `256 → 512 → N_ST`；
- 每个 `mlp_simple` 是 Linear + LayerNorm + ReLU，最终输出层关闭归一化和 ReLU。

`model.py::Imputation.forward` 中，真实 ST 重构为：

$$
\hat x_{ST}=D_1\big(D_2(h_{ST,2}\odot g_{ST,2})+h_{ST,1}\odot g_{ST,1}\big),
$$

生成分支把 $h_{ST}$ 换成从 scRNA-seq 得到的 $h_{SC}$，把真实 ST style 换成从常量 `st_style=1` 编码出的 `fake_style`。两个分支共享 decoder，这迫使 generator 输出落入 ST 表达空间。

### 4. Autoencoder 与 generator 如何协同

#### 4.1 ST autoencoder

同一个共同基因的 ST 向量同时进入 content encoder 和 style encoder，得到多层 $h_{ST}$ 与 $g_{ST}$，共享 decoder 重构 `st_real`。它学习“目标 ST 数据长什么样”。

#### 4.2 ST generator

该基因的 scRNA-seq 细胞类型均值向量进入 SC content encoder；常量 style code 进入 style encoder，得到 `fake_style`；共享 decoder 输出 `st_fake`。训练后未测基因只需 scRNA-seq content 加同一 style code，就能预测其 ST 空间表达。

代码中 `sc_style` 虽由 dataset 构造并传入 `set_input`，正常训练的 `forward` 实际传 `None`，没有使用 SC style。这一点应区别于概念图中两种数据风格的泛化表述。

### 5. 三组损失具体约束什么

代码总损失是三项不加权相加：

$$
L=L_{content}+L_{style}+L_{cos}.
$$

#### 5.1 Content loss

在两个隐层分别用 MSE 拉近 $h_{ST}$ 与 $h_{SC}$：

$$
L_{content}=\sum_{l=1}^{2}\|h_{ST,l}-h_{SC,l}\|_2^2.
$$

它要求同一共同基因从 ST 和 scRNA-seq 提取出的内容表示一致。

#### 5.2 Style loss

对 batch 内隐表示计算 Gram matrix：`G = feat @ feat.T / (batch*dim)`，再让 fake style 与真实 ST style 的 Gram matrix 接近。因为 batch 轴是基因，Gram matrix刻画的是当前一批基因之间的风格相关结构，不是 spot 邻接矩阵。

#### 5.3 Cosine similarity loss

代码包含两项：让 `st_real` 与 `st_fake` 相似，同时让 `st_real` 与原始 `stx` 相似。后者承担 autoencoder 重构约束；前者把生成结果推向相同的空间方向。输出推断后小于 0 的值被截成 0。

补充材料的消融报告：移除 fusion 性能下降约 8%；分别移除 content 或 style loss 下降约 11%；同时移除二者下降约 16%。两层或四层优于一层/三层，作者选择两层平衡效率与准确率。

### 6. 数据切分、增强和训练

论文采用 10-fold 交叉验证：共同基因随机按 80:20 分成训练和验证基因；最终目标是预测仅在 SC 中存在的基因。代码从 `train_list.npy` / `test_list.npy` 读取每折列表；`run_SpaIM.sh` 对 53 个 Dataset、每个 10 folds 循环。

训练脚本对 `seq` 随机把 50% 元素置零并扩增 4 倍，而 ST 目标/style 复制 4 次。这是代码中明确的选择性数据增强，但论文核心 Methods 没有把这一默认调用写成公式。优化器为 Adam，学习率 $10^{-3}$。`options.py` 默认 50 epochs，而论文 Implementation 和 `run_SpaIM.sh` 使用 300；复现实验应以运行脚本覆盖值为准。

### 7. 六张主图如何组成证据链

- Fig. 1 只说明 ReST、autoencoder、generator 和共享 decoder 的概念结构；它不显示真实张量维度。
- Fig. 2 在乳腺癌 ST 上按被遮蔽共同基因验证。SpaIM 的 PCC/SSIM 排名最高；`CD52` 示例显示 Tangram 近乎失效，而 SpaIM保留局部表达。ligand–receptor 增多是基于插补后的下游推断，不是新实验测量。
- Fig. 3 在 CosMx 数据上比较 SSIM/JS、细胞类型 DEG 数量与五个基因空间图，说明插补可改善稀疏 imaging-based ST 的下游信号。
- Fig. 4 用 ARI 比较空间域：SpaIM 0.50，接近 raw/ground-truth pipeline 的 0.56，高于 Tangram 0.16 与 gimVI 0.25。这里不是说插补结果超过真实测量。
- Fig. 5 对 `MME/CD1C/DAG1/MYCN` 展示 SpaIM 与 Tangram 的 UMAP marker pattern；证据是视觉一致性，不是独立测序验证。
- Fig. 6 汇总 53 个数据集的 rank-based PCC、JS、accuracy。排名能缓和数据集量纲差异，但不等于所有数据集的绝对 PCC 都为 1。

### 8. 论文—代码对应关系

| 机制 | 代码入口 | 对应程度 |
|---|---|---|
| 基因作为样本、SC 按细胞类型聚合 | `src/dataset.py` | Exact，解释模型输入的关键 |
| 两层 ReST 编码/递归融合 | `src/model.py::Imputation` | Exact 当前实现；论文允许一般 $L$ 层 |
| 共享 decoder | 同一 `st_dec2/st_dec1` 用于 real/fake | Exact |
| content MSE | `compute_loss` lines 138–142 | Exact |
| Gram style MSE | `gram_matrix` + `compute_loss` | Exact |
| 双 cosine loss | `compute_loss` lines 151–156 | Exact |
| 10-fold、300 epochs | `run_SpaIM.sh` | Exact benchmark launcher；CLI 默认仅 50 |
| scRNA 50% masking ×4 | `main.py::Data_augmentation/train` | Code exact；论文正文描述不足 |
| 通用新数据推断 | `test/SpaIM_imputation.py` | Partial：仍需匹配切片、细胞标签、模型维度和 checkpoint |

### 9. 复现边界与使用风险

代码固定 CUDA 路径并默认使用特定 AnnData 字段 `merge_cell_type`；训练需要预先生成每折基因列表。仓库提供 environment、数据处理脚本、benchmark launcher 和 inference 脚本，但没有随本工作区保存 53 个完整数据集与所有训练 checkpoint，本次也未重跑 benchmark。

更重要的是，插补可能强化参考 scRNA-seq 的细胞组成或模型学到的共表达模式。对“未测基因”没有目标 ST 真值时，预测应视为模型估计；ligand–receptor、DEG、空间域和轨迹结论仍需用独立测量、原位验证或留出基因评估确认，不能因为空间图看起来平滑就视为真实表达。

### 10. 最终理解

SpaIM 的最小核心不是“MLP 替代图模型”，而是一个跨基因学习的翻译器：共同基因教会模型如何把 $K$ 维细胞类型 content 转成固定目标切片的 $N_{ST}$ 维空间表达；ST autoencoder 提供目标风格约束，generator 在共享 decoder 中完成迁移。这个视角同时解释了其优势——无需逐细胞对齐、能利用跨基因规律——以及边界——输出与目标切片维度绑定、依赖参考细胞类型质量、未测基因仍是推断而非观测。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpaIM: Single-Cell Spatial Transcriptomics Imputation via Style Transfer

**Paper**: Li et al. "SpaIM: single-cell spatial transcriptomics imputation via style transfer." *Nature Communications* 16 (2025). DOI: 10.1038/s41467-025-63185-9

**Category**: integration_multimodal

**Code**: https://github.com/QSong-github/SpaIM

---

### Motivation & Novelty

#### Biological Problem

Spatial transcriptomics (ST) platforms have two compounding limitations: **data sparsity** (high dropout rates due to molecular capture inefficiency) and **restricted gene coverage** (imaging-based platforms like NanoString CosMx measure only hundreds to ~1,000 genes out of ~20,000 in the transcriptome). These limitations prevent comprehensive characterization of cellular programs in tissue context — for instance, a tumor microenvironment study cannot assess the full immune signaling network if only 960 of 20,000 genes are measured.

Single-cell RNA sequencing (scRNA-seq) complements ST by providing near-complete transcriptome coverage, but loses spatial coordinates upon tissue dissociation. Computationally integrating both modalities to impute unmeasured ST genes is therefore a high-priority problem.

#### Limitations of Existing Methods

| Method | Approach | Limitation |
|--------|----------|-----------|
| Tangram (*Nat. Methods* 2021) | Regularized subset alignment | Assumes modalities share expression distributions |
| SpaGE (*NAR* 2020) | PCA + kNN alignment | Local alignment; ignores platform biases |
| gimVI | Deep generative model (VAE) | Requires paired training data; limited generalization |
| Seurat (*Cell* 2019) | Canonical correlation analysis | Local alignment; assumes shared variance structure |
| novoSpaRc (*Nature* 2019) | Optimal transport + spatial continuity | No single-cell reference needed but less accurate |
| stDiff (*Nature Comms* 2023) | Diffusion model | Limited gene coverage; poorer imaging platform performance |
| SpatialScope (*Nat. Comms* 2023) | Deep generative model | Lower accuracy on imaging-based ST |
| TISSUE (*Nat. Methods* 2024) | Uncertainty-aware prediction | Meta-approach, not end-to-end learned |
| SPRITE (*Bioinformatics* 2024) | Network regularization | Meta-approach; requires pre-built networks |

All methods primarily rely on **local alignment** — finding similar cells between modalities — and fail to account for the systematic stylistic differences between ST and SC platforms (capture efficiency profiles, noise distributions, gene-specific dropout patterns).

#### SpaIM's Innovation

SpaIM adapts **neural style transfer** from computer vision (Gatys et al., 2016) to transcriptomics. The key conceptual shift: instead of aligning cells, SpaIM disentangles gene expression into:
- **Content**: the shared biological signal (how a gene varies across cell clusters) — captured from SC data
- **Style**: the platform-specific representation (how a gene looks across cells in ST space) — learned from ST data

The ST generator can then produce spatial expression for **any** SC gene by taking SC content and applying learned ST style — even for genes never measured in the ST assay. This generalization beyond observed genes is the primary advantage over alignment-based methods.

---

### Method Overview

SpaIM consists of two co-trained components built on Recursive Style Transfer (ReST) layers:

1. **ST Autoencoder**: Takes ST expression as input, encodes it through parallel content encoder ($h_{st}^{(l)}$) and style encoder ($g_{st}^{(l)}$) branches, then reconstructs through a shared decoder via Hadamard-product fusion ($h \otimes g$).

2. **ST Generator**: Takes SC cluster-mean expression ($\tilde{X}_{sc}$) plus a constant style placeholder ($\mathbf{1}$), encodes SC content ($h_{sc}^{(l)}$), learns a "fake style" representation ($g_{sc}^{(l)}$) via a dedicated style encoder, and produces predicted ST expression through the **shared decoder** from the autoencoder.

**Training regime**: Both components are trained simultaneously on common genes (those present in both ST and SC data) using four losses:
- Content loss: MSE alignment of latent content representations across modalities
- Style loss: Gram matrix matching for second-order style statistics
- AE reconstruction loss: cosine similarity between original and reconstructed ST
- Generator reconstruction loss: cosine similarity between generated and autoencoder-reconstructed ST

After training, the ST generator is used standalone for imputation of any SC gene.

**Input data preparation**: SC cells are grouped by Leiden clustering (resolution=0.5), and cluster-mean expression profiles are computed ($\tilde{X}_{sc} \in \mathbb{R}^{G_2 \times K}$). Both modalities are log1p-transformed. Gene split: 80% train / 20% validation (10-fold CV). Each gene is treated independently as a training example.

See `doc_method.md` for full equation derivations and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Datasets
- **53 total datasets**: 28 sequencing-based + 25 imaging-based ST platforms
- **Sequencing-based**: 10× Visium (21 datasets), Slide-seq, Slide-seq V2, Seq-scope, HDST (7 additional)
- **Imaging-based**: seqFISH, seqFISH+, MERFISH, STARmap, ISS, osmFISH, NanoString CosMx SMI
- **scRNA-seq reference**: paired scRNA-seq from same tissue type for each ST dataset
- All datasets available at Zenodo (10.5281/zenodo.16684835)

#### Metrics
PCC (Pearson correlation), SSIM (structural similarity), RMSE (z-score normalized), JS (Jensen-Shannon divergence), ACC (rank-based composite). Higher PCC/SSIM/ACC and lower JS/RMSE indicate better performance.

#### Key Results

**Breast cancer (10× Visium, CID44971 + GSE176078 scRNA-seq)**:
- SpaIM: PCC 0.70±0.02, SSIM 0.60±0.02 vs Tangram (best competitor): PCC 0.62±0.02, SSIM 0.52±0.02 (n=991 genes)
- SSIM 10% higher than Tangram; JS: 0.11±0.01, RMSE: 0.81±0.01 (best among 12 competitors)
- Ligand-receptor detection: 33 strongly associated pairs identified vs 11 in raw data (10 overlap); key pairs *VEGFA-ITGB1* and *LTF-TFRC* detected only in SpaIM-imputed data

**NanoString CosMx lung cancer (Lung9-rep1, ~70k-130k cells)**:
- SpaIM SSIM: 0.21, JS: 0.43 vs Tangram SSIM: 0.15, JS: 0.47; ACC 0.96±0.05 vs Tangram 0.91±0.11 (n=2,038 genes)
- DEG analysis: 92 lymphocyte-specific DEGs (SpaIM) vs 59 in raw, 40 in Tangram, 22 in stDiff

**Spatial domain detection (CosMx Lung5-rep3)**:
- ARI: SpaIM 0.50 vs raw/truth 0.56, Tangram 0.16, gimVI 0.25
- Correctly distinguishes continuous tumor regions from dispersed immune cells

**Broad benchmarking**:
- 28 sequencing-based ST: PCC 1.0±0.0, ACC 0.97±0.06 (SpaIM) vs 0.87±0.04 (Tangram)
- 25 imaging-based ST: PCC 0.97±0.11, ACC 0.92±0.08 (SpaIM) vs 0.78±0.13 (Tangram)
- 53-dataset average ACC: 0.95±0.07 (SpaIM) vs 0.81±0.10 (Tangram), 0.50±0.15 (gimVI)

---

### Reproducibility

**Rating: 3/5**

**Justification**: The code is publicly available and functionally complete for training and inference. Key experimental components (data preprocessing, training script, baseline runners) are well-organized. However, several factors reduce full reproducibility:

**Strengths**:
- Full source code on GitHub with all major components
- `run_SpaIM.sh` provides the exact command-line for 53-dataset benchmark
- `test/run_baseline.py` implements all 12 competing methods for fair comparison
- `environment.yaml` specifies exact dependencies (Python 3.11, PyTorch 2.4.1)
- All datasets deposited on Zenodo (10.5281/zenodo.16684835)

**Weaknesses**:
- **Validation loop bug** (main.py:45-50): `model.set_input` and `inference` are accidentally outside the for loop; only the last batch is processed. This may mean reported metrics are computed on a subset of validation genes.
- **Mean vs median discrepancy**: Code uses `np.mean` for cluster aggregation but paper describes "median expression" — affects reproducibility if users follow paper description.
- **SC gene filter mismatch**: Paper says "≥10% cells threshold"; code uses `min_cells=3`. For large datasets (100k+ cells), 10% >> 3; different gene sets will be retained.
- **Data augmentation undocumented**: 50% masking with 4× replication is critical for training but not described in paper; cannot be reproduced from paper alone.
- **Decoder architecture discrepancy**: Paper equations describe external residual connections between decoder layers; actual code implements input-merged residuals inside a single decoder call.
- No pre-trained model weights are provided — full benchmark requires substantial compute (53 datasets × 10 folds × 300 epochs).

**Environment setup**: `conda env create -f environment.yaml`, then prepare datasets per `data/Data_Processing_README.txt`. Data preprocessing must be run before training (separate `Data_Processing.py` step).

**Common pitfalls**:
- `style_dim=1` is hardcoded; changing to larger values requires model architecture changes
- `cluster` argument defaults to `'annotate'` — requires `merge_cell_type` column in obs; switch to `'leiden'` for generic datasets
- Large ST datasets (CosMx with 100k+ cells) require significant GPU memory — the `st_dim` parameter sets the input/output dimension of several large MLPs

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
