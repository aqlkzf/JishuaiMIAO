---
layout: default
permalink: /paper-atlas/fast-higashi-73eda661/
title: "Fast-Higashi"
nav: false
wide: true
description: "Fast-Higashi 把每条染色体上“基因组区间 × 基因组区间 × 单细胞”的 scHi-C 数据看成三阶张量，用一个跨染色体共享的细胞因子解释细胞差异，同时为每条染色体学习可回溯到具体接触区域的“元相互作用（meta-interaction）”；为处理极稀疏接触图，它在小批次基因组区间上先做 partial random walk with restart（partial RWR），再用无需反向传播的交替分解求解。"
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
      <span>Cell Systems · 2022</span>
    </div>
    <h1>Fast-Higashi</h1>
    <p>Ultrafast and interpretable single-cell 3D genome analysis with Fast-Higashi</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.cels.2022.09.004" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Fast-Higashi">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ma-compbio/Fast-Higashi" target="_blank" rel="noopener noreferrer" aria-label="Open code for Fast-Higashi">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Fast-Higashi 中文方法解读

### 一句话理解

Fast-Higashi 把每条染色体上“基因组区间 × 基因组区间 × 单细胞”的 scHi-C 数据看成三阶张量，用一个跨染色体共享的细胞因子解释细胞差异，同时为每条染色体学习可回溯到具体接触区域的“元相互作用（meta-interaction）”；为处理极稀疏接触图，它在小批次基因组区间上先做 partial random walk with restart（partial RWR），再用无需反向传播的交替分解求解。

### 1. 它解决的不是普通降维问题

单细胞 Hi-C 的每个细胞只有极少量被观测到的染色质接触。直接把接触矩阵展平后做 PCA，会同时遇到三个问题：零值主要代表“未采到”而非“没有接触”；完整插补矩阵占用大量内存；降维轴很难直接解释成哪段染色质结构在区分细胞。

Fast-Higashi 的目标因此有两层：

1. 得到跨染色体统一的细胞嵌入，用于聚类、可视化和轨迹分析；
2. 让嵌入维度能够对应到染色体上的接触模式，而不是只输出一个黑箱向量。

论文把第二类输出称为 meta-interaction，可类比 scRNA-seq 中的 metagene：一个 metagene 是多个基因的共变模式，一个 meta-interaction 是多个基因组区间对共同变化的接触模板。

### 2. 输入张量与共享细胞坐标

对染色体 $c$，令

$$
X^{(c)}\in\mathbb R^{N_c\times N_c\times M},
$$

其中 $N_c$ 是该染色体的 bin 数，$M$ 是细胞数。第三维第 $\ell$ 个切片就是细胞 $\ell$ 的染色体接触图。不同染色体的 $N_c$ 不同，不能简单沿空间维拼接；它们唯一严格对齐的是同一批细胞。

模型把细胞共享因子记为

$$
V\in\mathbb R^{M\times R}.
$$

$V$ 是最终最重要的细胞嵌入。每条染色体再有投影 $D^{(c)}$，将公共细胞空间变为染色体特异的载荷：

$$
C^{(c)}=VD^{(c)}.
$$

代码 `parafac2_intergrative.py:21` 明确记录了因子命名，`init_params()` 在 `:283-299` 用跨染色体初始特征的 SVD 初始化 `meta_embedding`（即 $V$）和各染色体的 `D_dict`。

### 3. core-PARAFAC2 如何产生可解释接触模板

对染色体 $c$、细胞 $\ell$，模型用染色体的基因组因子、核心交互矩阵和细胞载荷重建接触图。直观地写，可理解为

$$
\widehat X^{(c)}_{:,:,\ell}
=A^{(c)}\,G^{(c)}_\ell\,A^{(c)\top},
$$

其中 $A^{(c)}$ 把低维因子映射回实际 genomic bins，$G^{(c)}_\ell$ 由公共嵌入 $V_{\ell,:}$、染色体投影 $D^{(c)}$ 与染色体核心矩阵 $\bar B^{(c)}$ 共同决定。论文采用 core-PARAFAC2 形式，是为了允许不同染色体具有不同空间大小和基因组因子，同时约束它们共享细胞维结构。

从解释角度看，某个嵌入分量对应的 $A^{(c)}$ 与 $\bar B^{(c)}$ 可以重新组合成一张染色体接触模板；细胞在该分量上的载荷说明这张模板在该细胞中有多强。因而可以从“某细胞群在嵌入轴上偏高”追溯到“哪些 bin-bin 接触贡献了这个差异”。

要避免一个误解：meta-interaction 不是原始接触矩阵里直接挑出的若干条边，而是分解后由基因组因子和核心矩阵组成的低秩接触模式。第一分量通常捕获全体细胞共有的主接触结构，后续分量更容易承载细胞类型特异偏差；这是论文图 3A 的经验观察，也与求解时的奇异值排序有关。

### 4. 为什么需要 partial RWR

普通 RWR 需要完整的 bin-bin 转移矩阵。若先为每个细胞生成全染色体稠密插补矩阵，再训练分解模型，内存优势就消失了。Fast-Higashi 改为每次只取连续的一批行 $x^{(i)}$，在批次内部构造局部相似度并传播。

代码 `partial_rwr.py:83-138` 显示了真实计算：

1. 二阶相似度由 $AA^\top$ 得到，对角线清零；
2. 一阶相似度取当前行批次对应的直接接触子矩阵；
3. 两者分别归一化后按 0.25 和 0.75 加权；
4. 构造转移矩阵 $P$，从单位阵 $Q_0=I$ 开始迭代

$$
Q_{t+1}=\rho Q_tP+(1-\rho)I,
$$

其中实现固定 $\rho=0.5$；当最大变化量小于 0.01 或达到迭代上限时停止；
5. 用 $Q$ 左乘原始批次 $A$，得到传播后的局部接触信号。

一个三-bin 小例子：若 bin 1 与 bin 2 有直接接触，bin 2 与 bin 3 接触，而 bin 1–3 未被采到，二阶共接触会提高 bin 1 与 bin 3 的相似性；RWR 传播可为 bin 1 的局部表示补入来自 bin 3 的间接证据。restart 项保证传播不会无限远离起点。

partial 的含义是只对当前 bin 批次构图，而不是把所有 bin 的全图一次放入内存。论文补充实验报告，小批次近似与完整 RWR 保持较高相关，同时大幅降低显存；这个相关性是特定实验设置的测量，不应理解成所有分辨率和稀疏度下的理论保证。

### 5. 优化流程：交替闭式更新而非神经网络训练

Fast-Higashi 的速度主要来自矩阵分解的交替更新，而非“更小的神经网络”。核心类是 `Fast_Higashi_core`：

1. `init_params()` 对 partial-RWR 特征做截断 SVD，初始化公共细胞嵌入和染色体投影；
2. `fit()` 创建染色体/批次投影，并进入坐标下降循环（`parafac2_intergrative.py:544-738`）；
3. `update_meta_embedding_interactions()` 逐染色体、逐 bin 批次、逐 cell 批次读取稀疏数据，在线做 partial RWR 并累计足够统计量；
4. 公共细胞嵌入通过正交 Procrustes/SVD 更新，`project2orthogonal.py:6-29` 计算截断 $UV^\top$；
5. 投影后的核心张量交给 `parafac_integrative.py` 的 PARAFAC 交替最小二乘更新 $A^{(c)}$、$\bar B^{(c)}$、$D^{(c)}$；
6. 根据重建误差的相对变化停止。

因此“训练一次迭代”不是遍历样本、计算梯度、反向传播，而是按块累计张量收缩和 SVD/ALS 更新。代码广泛使用 `torch.no_grad()`，这与论文的闭式坐标下降描述一致。

### 6. 从原始接触到最终 embedding 的真实代码路径

用户入口位于 `FastHigashi_Wrapper.py`。高层数据流是：

1. 读取配置、细胞列表和稀疏 contact pairs；
2. `fast_process_data()` 将接触对转换成每条染色体的稀疏表示；
3. `prep_dataset()` 建立按染色体、bin 和 cell 切分的 `Chrom_Dataset`；
4. `run_model()` 创建 `Fast_Higashi_core` 并执行分解；
5. `fetch_cell_embedding()` 取公共因子，并通过 `parse_embedding()` 组合各染色体投影、再做 TruncatedSVD 得到指定维数的最终 embedding。

`parse_embedding()` 在 `FastHigashi_Wrapper.py:92-108` 先归一化每条染色体投影，把 `fac @ p` 拼接，再降到目标维数。因此用户拿到的最终 embedding 不一定就是未经处理的内部 `meta_embedding`；解释某一最终坐标时应同时考虑染色体投影和最后一次 SVD 旋转。

### 7. 图 1–4 应怎样阅读

#### 图 1：方法图

图 1A 从左到右是多染色体 scHi-C 张量、共享细胞因子与染色体特异因子、可解释 meta-interaction。图 1B 是 partial RWR：取局部行块、算一阶/二阶亲和、迭代重启随机游走、将平滑结果交给分解。它说明了“可解释”和“可扩展”分别来自哪里。

#### 图 2：embedding 与效率

图 2A–C 展示发育小鼠脑、人前额叶和小鼠海马的 UMAP；D 汇总聚类/分类指标，E 比较运行时间，F/G 聚焦更细神经元亚型。论文报告 Fast-Higashi 在三个复杂组织数据上通常为最佳或次佳，并在其基准环境中比 3DVI 快 40 倍以上、比 Higashi 快 9 倍以上。Lee 数据中它能分离 Pvalb、Sst、Vip、Ndnf 以及 L2-3/L4/L5/L6；Liu 数据中能区分 CA1/CA3 并显示稀有血管相关细胞群。

UMAP 上“看起来分开”也不是独立证据，论文同时使用 ARI、AMI、micro/macro-F1、modularity 和 silhouette 来支持其判断。

#### 图 3：解释性验证

图 3A 显示细胞对不同 meta-interaction 的载荷；B/C 将按细胞类型聚合的 meta-interaction 与 bulk Hi-C 差异图比较；D/E 把全基因组载荷和 marker gene 附近的差异接触联系起来。重要结论不是“分解轴天然等于某个细胞类型”，而是经细胞类型聚合后，其接触模板与独立 bulk 差异及表达标志呈一致关系。

#### 图 4：发育亚群与轨迹

图 4A 将原注释中的 interneuron 和 neonatal neuron 细分；B/C 用 marker gene gene-body 的 scA/B 值支持 Vip 对 Pvalb/Sst、抑制性对兴奋性新生神经元的解释；D/E 联合另一个视觉皮层数据集后显示按年龄衔接的抑制性与兴奋性分支。这里的轨迹来自 embedding 几何与年龄顺序的一致性，不是显式拟合的动力学模型。

### 8. 论文结果的适用边界

- 论文主要在 500 kb 等较粗分辨率和特定 scHi-C 数据集上评估；更高分辨率会显著增加 bin 数和稀疏性。
- “rare cell type” 是基于已有或多组学注释对 embedding 小簇的生物学解释，不意味着算法自动输出细胞类型名称。
- meta-interaction 与 marker expression 的相关支持功能关联，但不建立三维接触导致转录变化的因果关系。
- 最终 embedding 受 rank、分辨率、最大距离、bin/cell batch、RWR 和质量过滤共同影响。

### 9. 论文—代码一致性与缺口

核心机制匹配度高：局部 RWR 的 0.75/0.25 混合、restart 0.5、分块读取、共享 `meta_embedding`、染色体 `D_dict`、正交 SVD 更新和 PARAFAC 内循环都可在直接代码中定位。

仍需保留三条边界：

3. 本地 `paper.md` 来自 Elsevier XML，包含正文、STAR Methods 与补充图表引用，但没有独立的补充 Markdown 或论文主图原图目录；`figure_analysis.md` 以正文图注和论文叙述为依据。

### 10. 推荐阅读路径

先读本文第 2–5 节建立张量因子与 partial RWR 的关系，再看论文 `paper.md` 的 Figure 1 叙述和 STAR Methods；随后对照 `partial_rwr.py:83-138`、`parafac2_intergrative.py:283-299,304-539,544-738`、`project2orthogonal.py:6-29`。最后阅读 `figure_analysis.md`，把模型输出与图 2–4 的生物学证据连接起来。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Fast-Higashi: Ultrafast and Interpretable Single-Cell 3D Genome Analysis

**Paper**: "Ultrafast and interpretable single-cell 3D genome analysis with Fast-Higashi"
**Authors**: Ruochi Zhang, Tianming Zhou, Jian Ma
**Journal**: Cell Systems 13:798-807.e6 (2022)
**DOI**: 10.1016/j.cels.2022.09.004
**Code**: https://github.com/ma-compbio/Fast-Higashi

---

### Motivation and Novelty

#### Biological Problem

Single-cell Hi-C (scHi-C) technologies can map the 3D genome structure in individual cells, enabling study of chromatin compartments (A/B), TADs, and loops at single-cell resolution. The key challenge is that scHi-C data is extremely sparse — each cell captures at most thousands of contacts across billions of possible genomic bin pairs. This sparsity makes it difficult to distinguish true structural variation from noise, identify rare cell types, or interpret what drives cell-type differences in 3D genome organization.

#### Limitations of Existing Methods

| Method | Limitation |
|---|---|
| HiCRep/MDS (*Bioinformatics* 2018) | Requires dense imputed maps in memory; no scalability |
| scHiCluster (*PNAS* 2019) | Full-matrix RWR fills memory at high resolution; batch effects |
| LDA (*PLoS Comput. Biol.* 2020) | Cannot resolve rare cell subtypes in complex tissues |
| 3DVI (*biorXiv* 2021) | Per-distance per-chromosome VAEs → thousands of models; very slow; batch effects |
| Higashi (*Nat. Biotechnol.* 2022) | Hypergraph neural network → iterates over all contacts; slow convergence; not interpretable |

None of the above methods could (1) resolve neuron subtypes in human PFC, (2) identify rare cell types in complex tissues, and (3) directly link embeddings to specific genomic regions.

#### Key Contributions

1. **Speed**: >40× faster than 3DVI, >9× faster than Higashi, enabling ultrafast analysis of large cohorts
2. **Interpretability**: Introduces "meta-interactions" — directly interpretable genomic patterns analogous to metagenes in scRNA-seq — each linked to specific cell embedding dimensions
3. **Rare cell type identification**: First method to separate all 8+ neuron subtypes in human PFC (including excitatory neuron layers L2-3, L4, L5, L6) using chromatin conformation alone
4. **Scalability**: GPU-compatible mini-batch optimization handles tens of thousands of cells and high-resolution contact maps with ~300 MB GPU RAM
5. **Multi-modal generalization**: Framework supports incorporation of non-scHi-C single-cell omics data

---

### Method Overview

Fast-Higashi models scHi-C data from $M$ cells across $|C|$ chromosomes as a collection of 3-way tensors $X^{(c)} \in \mathbb{R}^{N_c \times N_c \times M}$. It decomposes each tensor using an extension of **core-PARAFAC2** (a flexible tensor decomposition that allows non-aligned factors) into four matrices:

| Factor | Symbol | Size | Biological Meaning |
|---|---|---|---|
| Cell embedding | $V$ | $M \times R$ | Shared latent space across all chromosomes |
| Chromosome transformation | $D^{(c)}$ | $R \times r_c$ | Maps shared embedding to chromosome-specific interactions |
| Bin weights | $A^{(c)}$ | $N_c \times r_c$ | Per-bin importance in each meta-interaction (captures accessibility variation) |
| Meta-interactions | $\bar{B}^{(c)}$ | $r_c \times r_c$ | Shared interaction templates (analogous to metagenes) |

**Meta-interactions** are the key interpretability output: each meta-interaction represents a recurring chromatin contact pattern; cells are characterized by the combination of meta-interactions they use (via $VD^{(c)}$). The first meta-interaction captures general population-level patterns; subsequent ones represent cell-type-specific deviations.

**Partial random walk with restart (Partial RWR)** imputes sparse contact maps within mini-batches: local affinity between bins combines 1st-order (direct contacts, 75%) and 2nd-order (indirect co-contacts, 25%) similarities; standard RWR diffuses these with restart probability $\rho = 0.5$. Batch size 64 achieves correlation >0.9 with full RWR while requiring 1000× less memory.

**Optimization** uses coordinate descent: $V$ and per-bin rotations $U^{(c)}_i$ have closed-form SVD updates; $\bar{B}^{(c)}, A^{(c)}, D^{(c)}$ are updated via alternating least squares (PARAFAC). Typical convergence in 20–40 outer iterations.

For full mathematical detail see `doc_method.md`. For code-paper mapping see `doc_code.md`.

---

### Evaluation

#### Datasets

| Dataset | Cells | Tissue | Resolution | Source |
|---|---|---|---|---|
| Lee et al. 2019 | 2,869 | Human prefrontal cortex | 500 kb | GEO: GSE130711 |
| Liu et al. 2021 | 4,869 | Mouse hippocampus | 500 kb | GEO: GSE156683 |
| Tan et al. 2021 | ~4,000 | Developing mouse brain | 500 kb | GEO: GSE162511 |
| Ramani et al. 2017 | ~10,000 | Sci-Hi-C 4 cell lines | 1 Mb | GEO: GSE84920 |
| Kim et al. 2020 | ~5,000 | Sci-Hi-C 5 cell lines | 1 Mb | 4DN Data Portal |

#### Metrics

- **Modularity score**: graph modularity between embedding-based KNN graph and reference labels
- **ARI / AMI**: Adjusted Rand Index / Mutual Information between Louvain clustering and reference labels (grid search over neighbor count and resolution; top-5 averaged)
- **Micro-F1 / Macro-F1**: Logistic regression classifier trained on 10% of cells, predicting the rest
- **Silhouette score**: per-cell distance to cluster centroid vs. other cluster (neuron subtype analysis)
- **Spearman correlation**: meta-interaction maps vs. differential bulk Hi-C contact maps

#### Key Quantitative Results

- **Lee et al. (human PFC)**: Fast-Higashi separates all 8+ neuron subtypes including all excitatory neuron layers (L2-3, L4, L5, L6) — first method to achieve this. Other methods: Higashi separates most but not layer subtypes; scHiCluster/3DVI fail on layer separation; 3DVI shows batch effects.
- **Liu et al. (mouse hippocampus)**: Only Fast-Higashi identifies rare VLMC, PC, and EC populations (<50 cells each) while separating CA1/CA3. All other methods (except Higashi) miss these rare types.
- **ARI comparison** (Lee et al., avg across all cell type pairs): Fast-Higashi ≥ all methods on all three main datasets
- **Speed** (vs. 1 RTX 2080 Ti, 16-core Intel Xeon Silver 4110): Fast-Higashi ~1 min, Higashi ~10-60 min, 3DVI ~hours
- **Meta-interactions (Kim et al.)**: Spearman correlation between Fast-Higashi cell-type-specific meta-interactions and bulk Hi-C differential contact maps is highest for the correct cell type (~0.4–0.7 range)
- **Marker gene correlation (Lee et al.)**: Differential contact values at top 200 marker gene loci are highest in the matching cell type (Fig. 3E)
- **Partial RWR validation**: Pearson/Spearman correlation with full RWR > 0.9 at batch=64 (Fig. S10)
- **Downsampling robustness**: Fast-Higashi maintains separation at 10–50% coverage; outperforms Higashi at all downsampling rates (Figs. S5-S6)

#### Biological Validation (Tan et al. developing mouse brain)

Fast-Higashi identifies 4 sub-clusters within annotated neuron types. Validation via:
- scA/B values at marker gene bodies (inhibitory: Pvalb/Sst; excitatory vs. inhibitory neonatal)
- Joint embedding with Takei et al. visual cortex dataset recovers age-ordered developmental trajectories with P7→P28 cells connecting neonatal to mature neuron states

---

### Reproducibility

**Rating: 3/5**

**Justification**: The code is publicly available and reasonably documented, with a tutorial notebook. However:
- No requirements.txt or conda environment file (setup.py has empty `install_requires`)
- Input format requires same Higashi preprocessing pipeline — the `data.txt` format is not well-documented
- Hyperparameter choices (r_c, R, off_diag) require domain knowledge to tune
- Evaluation code (ARI, F1, silhouette, UMAP) is not included in the repo
- The zenodo release is separate from the GitHub repo

**Strengths**:
- Core algorithm is cleanly separated into modules
- GPU and CPU paths both supported
- Mini-batch design makes large-scale analysis feasible
- Informative progress output during training

**Weaknesses**:
- No automated tests
- Missing evaluation/downstream analysis scripts
- Config JSON format not well-documented (fields inferred from code)
- The `do_col` flag (column normalization) is undocumented

**Environment**:
```
Python ≥ 3.7
PyTorch ≥ 1.8.0 (with CUDA for GPU support)
opt_einsum
scikit-learn
scipy
numpy
pandas
tqdm
h5py
```

**Data availability**: All datasets in GEO (GSE130711, GSE156683, GSE162511, GSE84920) or 4DN data portal. Fast-Higashi code and processed data at zenodo: https://doi.org/10.5281/zenodo.7023632

**Common pitfalls**:
1. GPU OOM: reduce `bs_cell` or `bs_bin` in the config
2. RWR convergence warning: sparse datasets with very few contacts per cell may fail RWR; try reducing `off_diag`
3. Large datasets (>20K cells): consider increasing `rank` and expect 30-60 min runtime
4. The `size_ratio=0.3` parameter means r_c depends on resolution; at 500 kb with 2280 bins, r_c = min(2280 × 0.3 × 0.5, 64) = 64

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
