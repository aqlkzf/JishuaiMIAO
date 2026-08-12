---
layout: default
permalink: /paper-atlas/scdec-a959a807/
title: "scDEC"
nav: false
description: "scATAC-seq 的峰计数矩阵既高维又稀疏。常见流程先降维，再在所得坐标上运行 K-means 或 Louvain；这样“什么表示适合重构数据”和“什么表示适合区分细胞群”由两个互不反馈的步骤决定。scDEC 把连续表示和离散簇标签一起放入生成模型，使编码器在训练表示的同时直接输出聚类概率。 这里尤其不能被名字误导：本论文的 scDEC 不是经典 DEC 中基于 Student-t 分布和 KL 目标分布迭代的算法。"
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
      <span>Representation Models</span>
      <span>Nature Machine Intelligence · 2021</span>
    </div>
    <h1>scDEC</h1>
    <p>Simultaneous deep generative modelling and clustering of single-cell genomic data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-021-00333-y" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scDEC：用成对生成对抗网络同时学习 scATAC 表示与细胞簇

### 1. scDEC 解决的核心矛盾

scATAC-seq 的峰计数矩阵既高维又稀疏。常见流程先降维，再在所得坐标上运行 K-means 或 Louvain；这样“什么表示适合重构数据”和“什么表示适合区分细胞群”由两个互不反馈的步骤决定。scDEC 把连续表示和离散簇标签一起放入生成模型，使编码器在训练表示的同时直接输出聚类概率。

这里尤其不能被名字误导：本论文的 scDEC 不是经典 DEC 中基于 Student-t 分布和 KL 目标分布迭代的算法。它是一个双向、成对的 GAN 系统，核心约束是 Wasserstein 对抗损失和 round-trip loss。

### 2. 从峰矩阵到模型输入

论文 Methods 的预处理顺序是：保留至少在 3% 细胞中有 reads 的峰，进行 TF-IDF，再用 PCA 降至默认 20 维。设预处理后的细胞向量为 $x\in\mathbb{R}^{d_y}$。

本地 `scATAC_Sampler` 对应 `scDEC/util.py:65-97`：它读取 peaks × cells 矩阵，按非零比例筛峰，计算 TF-IDF，转成 cells × peaks，随后还执行 MinMax scaling，再做 PCA。MinMax 这一步存在于代码 `util.py:83`，但正文方法没有明确写出，因此属于代码额外步骤，不能假装为论文公式的一部分。

多模态 PBMC 案例走另一条预处理路径：RNA 与 ATAC 分别归一化、对数变换和 PCA，再拼接后送入同一个模型（`util.py:119-154`）。因此“多模态扩展”主要是输入特征拼接，而不是引入了模态专用的交叉注意力或配对损失。

### 3. 一个潜空间拆成“状态”和“类别”

scDEC 为每个细胞设置两类潜变量：

$$z\sim\mathcal N(0,I),\qquad c\sim\mathrm{Cat}(K,w).$$

- 连续变量 $z$ 表达簇内变化、供体差异等连续状态；
- 离散 one-hot 变量 $c$ 表达 $K$ 个候选细胞簇；
- $w$ 是类别先验比例，训练中根据当前预测动态更新。

生成器 $G$ 将二者拼接后生成细胞表示：

$$\tilde x=G(z,c).$$

编码器 $H$ 做反方向映射：

$$H(x)=(\tilde z,\tilde c).$$

其最后一层前 $d_z$ 个节点是连续表示，后 $K$ 个 logits 经 softmax 得到簇概率。硬标签为 $\arg\max_k\tilde c_k$。代码在 `main_clustering.py:55-72` 完成两条正反向回路，在 `model.py:114-151` 切分连续输出与分类 logits。

### 4. 为什么需要两个判别器

scDEC 有四个网络：

| 网络 | 方向 | 作用 |
|---|---|---|
| $G$ | $(z,c)\rightarrow x$ | 生成类似真实细胞的预处理特征 |
| $H$ | $x\rightarrow(\tilde z,\tilde c)$ | 编码连续表示并预测簇 |
| $D_x$ | 数据空间 | 区分真实 $x$ 与生成 $G(z,c)$ |
| $D_z$ | 连续潜空间 | 区分先验 $z$ 与编码出的 $\tilde z$ |

数据判别器迫使生成分布靠近真实细胞分布，潜空间判别器迫使编码器输出的连续部分靠近标准高斯先验。两边都用 WGAN-GP：Wasserstein 判别目标外加梯度范数接近 1 的惩罚，代码中惩罚系数固定为 10（`main_clustering.py:91-121`）。

代码命名与论文符号容易混淆：数据空间在代码里是 `y`，所以论文 $D_x$ 对应 `dy_net`；连续潜空间在代码里是 `x`，所以论文 $D_z$ 对应 `dx_net`。判断含义应看输入维度和调用路径，而不能只看变量名。

### 5. round-trip loss 把“生成”和“聚类”真正连起来

只有两个对抗目标时，$G$ 和 $H$ 仍可能学到彼此不一致的映射。scDEC 要求两个方向绕一圈后回到起点：

$$x\rightarrow H(x)\rightarrow G(H(x))\approx x,$$

$$ (z,c)\rightarrow G(z,c)\rightarrow H(G(z,c))\approx(z,c).$$

连续部分使用平方误差，离散类别使用交叉熵：

$$\mathcal L_{RT}=\alpha\|x-G(H(x))\|_2^2
+\alpha\|z-H_z(G(z,c))\|_2^2
+\beta\,CE(c,H_c(G(z,c))).$$

论文和默认命令均设置 $\alpha=\beta=10$。本地代码 `main_clustering.py:77-89` 逐项实现这三个损失；分类交叉熵使用 softmax 前 logits。最后，$G,H$ 联合最小化两个生成端对抗项与 round-trip loss，而两个判别器联合最小化带梯度惩罚的判别损失。

离散交叉熵很关键：它要求“指定类别 $c$ 生成出的细胞，再编码回来仍是 $c$”。因此类别不是训练结束后额外跑聚类得到的，而是在表示学习过程中受到生成一致性约束。

### 6. 实际训练循环

本地 `main_clustering.py:158-215` 的一次循环是：

1. 从当前类别先验 $w$ 抽取 $(z,c)$，从真实数据抽取 $x$；
2. 连续更新判别器 5 次；
3. 更新一次 $G$ 与 $H$；
4. 每 100 batch 用 $H$ 编码全部细胞，以 softmax argmax 统计经验簇比例 $\hat w$；
5. 用 $w\leftarrow r w+(1-r)\hat w$ 更新类别先验，默认 $r=0.2$；
6. 若某簇权重低于 0.02，代码随机抬高它并重新归一化，以降低簇直接消失的风险；权重变化长期稳定且训练超过 30,000 batch 后停止。

这套先验更新让不平衡簇比例可以从模型预测反馈回来，但它不是严格的贝叶斯后验更新。随机救活小簇也是工程启发式：能防止明显塌缩，却不保证每个保留下来的簇都有生物学意义。

当 $K$ 未知时，论文建议在预处理数据上用 gap statistic 比较不同 $K$；本地 `util.py:38-61` 有对应实现。代码使用 100 个随机参考矩阵，而论文 Methods 描述 1,000 次 Monte Carlo，属于数值设置不完全一致的边界。

### 7. 输出究竟是什么

推断时，`predict_x()` 将真实细胞送入 $H$，返回连续输出和 softmax 类别概率（`main_clustering.py:279-294`）。`evaluate()` 以 argmax 得到簇标签，并在有真标签时计算 NMI、ARI 与 homogeneity（`:237-261`）。

论文下游使用的低维表示不是只有 $\tilde z$，而是编码器最后一层中连续部分与 softmax 前离散 logits 的拼接。图 4e 说明前十维主要是连续特征、后三维对应离散类别；连续维仍可能携带供体和簇内变化。

### 8. 四张主图如何构成证据链

- 图 1：模型结构图。展示 TF-IDF/PCA、$(z,c)$、$G/H$ 双向映射、两个判别器以及 $H$ 的连续/离散双输出。
- 图 2：四个 scATAC 基准与 dropout 实验。scDEC 在四组数据中最好或接近最好，并在 Forebrain 50% dropout 时报告 ARI 0.279；这些是论文实验结果，不是结构上的必然保证。
- 图 3：从“聚类是否准”扩展到生物学用途。用 chromVAR 做 motif 富集、用 Slingshot 在 scDEC 表示上拟合造血轨迹，并通过类别指示器插值生成 MPP 与 CLP 之间的 LMPP-like 状态。
- 图 4：考察供体差异、大规模数据和多模态。它显示不同 $K$ 可以分别表达细胞类型和供体内差异，81,173 个 mouse atlas 细胞上的扩展性，以及 RNA+ATAC 拼接优于单模态的案例。

补充材料包含 18 张补充图和 5 张表：补充图 2–6 展开基准比较，图 8 检查维度鲁棒性，图 10–13 展开供体效应，图 15–17 覆盖 mouse atlas 和多模态，图 18 检查 gap statistic；补充表 1 与 5 给出网络和训练设置。

### 9. 生成中间细胞状态应谨慎解释

论文令相邻类型的类别指示器线性插值：

$$\tilde c=\gamma c_1+(1-\gamma)c_2,\qquad x_{gen}=G(z,\tilde c).$$

在留出 LMPP、仅用 MPP 与 CLP 训练的实验中，$\gamma=0.5$ 的生成细胞与真实 LMPP meta-cell 更相似。它支持生成模型捕捉到该数据中的中间结构，但不证明任意两个簇的线性插值都是真实发育路径，也不替代时间、谱系追踪或扰动证据。

此外，这段插值公式在论文 Methods 和图 3 实验中存在，但当前主训练代码未找到实现，`doc_code.md` 将其标为 **Not found**。所以本地仓库能直接验证 $G$ 的条件生成接口，却不能仅凭主脚本复现图 3d–e 的完整生成流程。

### 10. 论文—代码一致性与边界

当前代码快照固定在提交 `eed14c37a1db354d484e28382a20320f507030a2`。

| 机制 | 状态 | 直接证据 |
|---|---|---|
| $G/H$ 双向回路与连续/离散输出 | Exact | `main_clustering.py:55-89` |
| WGAN-GP 与系数 10 | Exact | `main_clustering.py:91-121` |
| round-trip L2 与类别交叉熵 | Exact | `main_clustering.py:77-89` |
| 10 层 $G/H$、2 层判别器 | Exact | `main_clustering.py:354-357`、`model.py` |
| 峰筛选、TF-IDF、PCA | Exact/Partial | `util.py:65-97`；代码另有正文未写的 MinMax |
| 类别先验更新与防塌缩 | Exact | `main_clustering.py:158-235` |
| 预测簇与评价指标 | Exact | `main_clustering.py:237-294` |
| gap statistic 重复次数 | Partial | 代码 100 次，论文写 1,000 次 |
| 中间状态插值实验 | Not found | 论文 Methods 与图 3；主代码没有对应流程 |
| 全部基准数值复现 | Not verified | 本次恢复未重跑 TensorFlow 1.13.1 大规模实验 |

### 11. 使用与解释限制

1. $K$ 仍需给定或先估计；不同 $K$ 可能揭示不同层级结构，也可能产生不稳定拆分。
2. GAN 训练与类别先验的启发式更新可能出现模式塌缩或随机性，预训练结果不能替代新数据上的稳定性检查。
3. 输入是经过 PCA 的特征；生成输出首先是这一预处理空间中的向量，不应直接当成未经处理的原始 peak counts。
4. 供体效应“缓解”是特定无监督案例观察；代码没有显式 batch covariate 或通用批次校正模块。
5. motif、轨迹和多模态结果依赖 chromVAR、Slingshot、标签注释及外部处理，不是 `main_clustering.py` 单独完成的。
6. 本快照依赖 Python 2.7 / TensorFlow 1.13.1 风格 API，现代 TensorFlow 环境不能假定直接运行。

一句话概括：scDEC 用 $H$ 同时输出连续表示和离散簇，用 $G$ 反向生成，再以双重对抗约束和 round-trip 一致性让“表示是否像数据”与“类别能否往返保留”共同塑造聚类。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## scDEC Summary

**Paper**: Simultaneous deep generative modelling and clustering of single-cell genomic data
**Authors**: Qiao Liu, Shengquan Chen, Rui Jiang, Wing Hung Wong
**Journal**: Nature Machine Intelligence (2021)
**DOI**: 10.1038/s42256-021-00333-y

---

### Motivation & Novelty

#### Biological Problem

scATAC-seq profiles chromatin accessibility in individual cells, revealing the epigenetic landscape of gene regulation. The data is extremely sparse (1–10% peaks detected per cell) and high-dimensional (hundreds of thousands of peaks), making cell-type identification challenging.

#### Limitations of Existing Methods

Prior methods treat dimensionality reduction and clustering as sequential independent steps:
- **scABC** (Nat. Commun. 2018): weighted K-medoids on raw data
- **cisTopic** (Nat. Methods 2019): LDA topic modeling, then external clustering
- **Cusanovich2018** (Cell 2018): TF-IDF + SVD, then Louvain clustering
- **Scasat** (Nucleic Acids Res. 2019): Jaccard similarity + MDS, then clustering
- **SnapATAC** (Nat. Commun. 2021): genome binning + PCA, then clustering
- **SCALE** (Nat. Commun. 2019): VAE for latent features, then K-means

The decoupling means the embedding is not optimized for clustering, and clustering does not inform the representation. External clustering (K-means, Louvain) on a representation not designed for it is suboptimal.

#### Unique Contributions

1. **Joint optimization**: scDEC simultaneously learns the latent representation and infers cluster labels in a single end-to-end model — no external clustering step needed.
2. **Dual GAN architecture**: A pair of GANs with round-trip (cycle-consistency) loss ties the forward (latent→data) and backward (data→latent+cluster) transformations together.
3. **Adaptive category distribution**: The categorical prior $\text{Cat}(K, \mathbf{w})$ is updated during training based on inferred cluster frequencies, allowing the model to handle imbalanced cell populations.
4. **Generative power for trajectory inference**: The generator $G$ can interpolate between cell types in latent space to generate intermediate cell states, enabling trajectory analysis without external tools.
5. **Multi-modal extension**: Straightforward extension to joint scRNA-seq + scATAC-seq analysis by concatenating PCA-reduced features.

---

### Method Overview

scDEC is built on a pair of GANs with a shared latent space:

- **Latent space**: Continuous $\mathbf{z} \sim \mathcal{N}(0,I)$ (style/variation) + Discrete $\mathbf{c} \sim \text{Cat}(K,\mathbf{w})$ (cluster identity)
- **Generator G**: Maps $(\mathbf{z}, \mathbf{c}) \to \tilde{\mathbf{x}}$ (latent → scATAC-seq profile)
- **Encoder H**: Maps $\mathbf{x} \to (\tilde{\mathbf{z}}, \tilde{\mathbf{c}})$ (scATAC-seq → latent + cluster label)
- **Discriminators $D_x$, $D_z$**: Enforce that generated data matches real data distribution and encoded latent matches prior

Training minimizes: adversarial losses (WGAN-GP) + round-trip cycle-consistency loss (L2 for continuous, cross-entropy for discrete).

**Preprocessing**: Peak filtering (>3% cells) → TF-IDF → MinMax scaling → PCA(20).

**Architecture**: G and H each have 10 fully-connected layers; discriminators have 2 layers. All networks are fully connected (no convolutions).

See `doc_method.md` for full mathematical derivation and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets

| Dataset | Cells | Cell Types | Source |
|---------|-------|-----------|--------|
| InSilico | ~3,000 | 6 | GEO GSE65360 |
| Forebrain | ~2,000 | 8 | GEO GSE100033 |
| Splenocyte | ~3,000 | 12 | ArrayExpress E-MTAB-6714 |
| All blood | ~2,000 | 13 | GEO GSE96772 |
| Mouse atlas | 81,173 | 40 | atlas.gs.washington.edu |
| PBMC 10k | ~10,000 | 14 | 10x Genomics |

#### Metrics

NMI (normalized mutual information), ARI (adjusted Rand index), Homogeneity — all compared against FACS-sorted ground truth labels.

#### Key Results

| Dataset | scDEC NMI | Best Baseline | Baseline NMI |
|---------|-----------|---------------|--------------|
| InSilico | 0.871 | scABC | 0.822 |
| Forebrain | 0.750 | cisTopic | ~0.65 |
| Splenocyte | 0.839 | — | — |
| All blood | — | cisTopic | — (ARI: scDEC 0.309 best) |
| Mouse atlas | 0.732 | SCALE | lower |

- scDEC achieves best or second-best clustering across all 4 benchmark datasets
- Robust to dropout: at 50% dropout rate, ARI=0.279 vs cisTopic 0.202
- Donor effect: NMI=0.754, ARI=0.805 on mixed-donor data (outperforms all baselines)
- Multi-modal (PBMC): NMI=0.779, ARI=0.718 — outperforms MOFA+ (Genome Biol. 2020), comparable to scAI (Genome Biol. 2020)
- Scalable: handles 81k cells while most methods fail due to memory limits

#### Biological Validation

- Cluster-specific motif discovery (chromVAR + JASPAR): recovers known TF markers (En1 for astrocytes, Neurod2 for excitatory neurons, Sox9 for oligodendrocytes)
- Trajectory inference: haematopoiesis tree consistent with known differentiation paths
- Intermediate state generation: generated LMPP-like cells (α=0.5) have higher Pearson correlation with true LMPP meta-cell than direct interpolation or PCA interpolation

---

### Reproducibility

**Rating: 3/5**

**Justification**: Code is available and well-organized. Pre-trained models are provided for all 5 benchmark datasets. However, the code uses TensorFlow 1.13.1 (deprecated), which requires specific environment setup. The data generation interpolation experiment (Fig. 3d) is not implemented in the main code. Supplementary tables (hyperparameters, dataset statistics) were not OCR'd.

**Strengths**:
- GitHub repo with pre-trained models: https://github.com/kimmo1019/scDEC
- CodeOcean capsule with example datasets
- Preprocessed data on Zenodo (DOI: 10.5281/zenodo.3977858)
- Clear command-line interface with documented hyperparameters

**Weaknesses**:
- TensorFlow 1.x only — requires TF 1.13.1, not compatible with TF 2.x
- Data generation (trajectory interpolation) not in main code
- Supplementary Table 1 (hyperparameters) and Table 5 (training details) not accessible from OCR
- No conda/pip environment file provided
- Batch size (64) is small for WGAN-GP; may need tuning for new datasets

**Setup**:
```bash
# Requires TF 1.13.1
pip install tensorflow-gpu==1.13.1
# Run with pre-trained model
python main_clustering.py --data Forebrain --K 8 --dx 15 --dy 20
# Train from scratch
python main_clustering.py --data Forebrain --K 8 --dx 15 --dy 20 --train True
```

**Common pitfalls**:
- TF1 vs TF2 incompatibility: `tf.contrib` removed in TF2
- Data must be in `datasets/<name>/sc_mat.txt` (tab-separated, peaks as rows, cells as columns) and `label.txt`
- For PBMC10k: requires MTX format (matrix.mtx, features.tsv, barcodes.tsv)
- K must be set correctly; use gap statistic (`util.py:compute_gap`) if unknown

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
