---
layout: default
permalink: /paper-atlas/dusted-e44990d9/
title: "DUSTED"
nav: false
description: "DUSTED 先在整张切片上学习每个基因的通道门控，再沿空间邻接图用 GAT 融合 spot 信息，以 NB/ZINB raw-count likelihood 训练均值、离散度和额外零三个输出头，并把经 library-size 校准的预测均值作为去噪表达；算法设计清楚，但当前公开 commit 仍需修复运行 blocker 和补齐外部依赖才能严格复现。"
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
      <span>Spatially Variable Genes</span>
      <span>AAAI · 2025</span>
    </div>
    <h1>DUSTED</h1>
    <p>DUSTED: Dual-Attention Enhanced Spatial Transcriptomics Denoiser</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1609/aaai.v39i1.32110" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for DUSTED">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Lifeomics/DUSTED" target="_blank" rel="noopener noreferrer" aria-label="Open code for DUSTED">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DUSTED 方法中文解读：用基因通道注意力与空间图注意力恢复 SRT 计数

### 1. DUSTED 解决什么问题

空间转录组（SRT）同时提供 spot-by-gene 表达矩阵和组织坐标，但低捕获率、dropout、PCR amplification bias 与 library-size 差异会使矩阵稀疏、空间模式模糊。DUSTED（Dual-Attention Enhanced Spatial Transcriptomics Denoiser）希望在不使用组织学图像的前提下，以表达和空间邻接图恢复更平滑且符合计数分布的表达。

它的“双注意力”不是两个相同的 GAT：

- Gene Channel Attention（GCA）在所有 spot 上汇总每个基因，学习 gene-specific 权重；
- Graph Attention 在空间邻接图上学习 spot-to-spot 权重。

模型以 NB 或 ZINB likelihood 对 raw counts 自监督训练，把预测均值 $\mu$ 作为 denoised expression。DUSTED 本身不是 SVG ranking 方法；它是 SVG、空间模式可视化和 spatial clustering 的上游去噪步骤。

### 2. 输入、输出和前置处理

方法需要：

1. AnnData 表达矩阵；
2. `adata.raw.X` 中的 raw counts；
3. `adata.obsm['spatial']` 对应的坐标；
4. 由外部 `Cal_Spatial_Net` 构造并写入 `adata.uns['Spatial_Net']` 的邻接图；
5. `adata.obs['scale_factor']`，用于把预测均值恢复到各 spot 的 library-size 尺度。

教程选择约 3,000 个高变基因，保存 raw counts，再做 total-count normalization 和 log transform 作为网络输入。训练器读取归一化/HVG 表达为 `data.x`，但 likelihood 的目标是 `adata.raw.X`。这是一个重要的双尺度设计：encoder 看稳定化后的特征，NB/ZINB loss 对原始离散计数负责。

输出在 `save_reconstruction=True` 时写入：

- `adata.obsm[key_added]`：低维 latent embedding $h_2$；
- `adata.layers[key_added]`：预测均值矩阵，负数截零；
- `adata.uns[key_added+'_loss']`：训练期间最小 loss。

代码没有自动执行后续 normalization、log1p、SVG 检验或 clustering；这些在 tutorial notebook 中另行完成。

### 3. 空间图：谁可以给谁传递信息

论文以欧氏距离半径 $r$ 构造无向图 $G=(V,E)$，每个节点是 spot/cell，边表示空间邻居。实验调节半径，使每个节点约有 5–6 个邻居。

空间图决定信息传播的候选集合，但并不直接规定邻居贡献相同。Graph Attention 会根据当前 feature 学习边权。因此 DUSTED 的空间平滑不是简单邻居平均：同样距离内，表达结构不同的邻居可以获得不同权重。

本地代码只检查 `Spatial_Net` 是否存在，并通过外部 `STAGATE_pyG.utils.Transfer_pytorch_Data` 转成 PyTorch graph。图构造和 custom GATConv 源码不在当前仓库，因此内部实现只能标为 `Not found in snapshot`；不能仅依据 import 名称把论文的 attention 公式判为 Exact。

### 4. 第一种注意力：Gene Channel Attention

输入 $X\in\mathbb R^{N\times G}$ 含 $N$ 个 spot、$G$ 个基因。`GCALayer` 沿 spot 轴做 average pooling 和 max pooling，分别得到两个 $1\times G$ 向量：

$$
a_g=\frac1N\sum_{i=1}^{N}X_{ig},\qquad
m_g=\max_i X_{ig}.
$$

两者通过共享 MLP，相加后 sigmoid：

$$
A_{gc}=\sigma\{\operatorname{MLP}(a)+\operatorname{MLP}(m)\}.
$$

然后逐基因重标定：

$$
\widetilde X=A_{gc}\odot X,
$$

并以残差连接送入空间编码器：

$$
X'=X+\alpha\widetilde X.
$$

这里每个基因在整张切片上共享一个 attention weight，不是每 spot、每 gene 都单独一个权重。average 反映总体表达，max 保留局部高表达，二者组合可突出稳定或局部重要通道。但把权重解释成“真实噪声率”仍过强；它是为重建目标学习的可训练门控。

代码的 shared MLP 是 $G\rightarrow G/16\rightarrow G$，而论文文字把隐藏 activation 描述得像压到 1，因此维度细节为 `Partial`。还有一个阻断运行的 bug：构造器保存 `self.alpha`，`forward()` 却执行 `alpha * h1 + features`。模块中没有全局 `alpha`，原样运行会 `NameError`。正确算法意图显然是 `self.alpha * h1 + features`，但本任务只记录，不擅自改论文代码。

### 5. 第二种注意力：空间 Graph Attention Autoencoder

GCA 后的 feature 进入两层 encoder：

$$
H^{(1)}=\operatorname{ELU}(\operatorname{GAT}_1(X',E)),
$$

$$
Z=H^{(2)}=\operatorname{GAT}_2(H^{(1)},E).
$$

论文/实验常用维度 $G\rightarrow512\rightarrow30$，所以 $Z\in\mathbb R^{N\times30}$ 是 spatially informed latent representation。一般 GAT 更新可写为

$$
h_i^{(k)}=\operatorname{ELU}\left(\sum_{j\in\mathcal N_i}a_{ij}^{(k)}W_kh_j^{(k-1)}\right),
$$

其中 $a_{ij}$ 是在邻域内 softmax 归一化的可学习 attention。

decoder 先从 30 维回到 512 维。代码把 `conv3` 的线性权重设为 `conv2` 权重的转置，并把 encoder 第一层保存的 attention 传为 `tied_attention`，意图减少参数并对称解码：

$$
\widehat W_2=W_2^{\mathsf T},\qquad
\widehat A_1=A_1.
$$

权重赋值发生在每次 forward 内，并直接写 `.data`。调用形式依赖 STAGATE 的 custom `GATConv` 支持 `attention=True` 与 `tied_attention=`；PyG 标准 GATConv 没有相同合同。由于外部源码缺失，attention tying 的 call site 可验证，内部数学行为不能直接验证。

### 6. 为什么 decoder 输出三个矩阵

从 decoder feature $H^{(3)}$ 分出三个 GAT head：

$$
\mu=\operatorname{clip}(\exp(f_\mu(H^{(3)})),10^{-5},10^6),
$$

$$
\theta=\operatorname{clip}(\operatorname{softplus}(f_\theta(H^{(3)})),10^{-4},10^4),
$$

$$
\pi=\sigma(f_\pi(H^{(3)})).
$$

$\mu$ 是均值，$\theta$ 是 inverse dispersion，$\pi$ 是额外零概率。代码再按 spot scale factor 调整均值：

$$
\mu_{ig}\leftarrow s_i\mu_{ig}.
$$

这个 scale factor 没在论文主要公式中展开，却是连接“归一化网络输入”与“raw-count likelihood”的关键。数值 clamp 也未在论文公式中写明，作用是避免 `exp`、`log` 和 gamma 函数出现溢出或零值。

最终 denoised expression 取 $\mu$，而不是从 NB/ZINB 随机采样，也不是把 dropout probability $\pi$ 直接当作插补比例。

### 7. NB 与 ZINB 如何约束计数分布

NB 以均值 $\mu$ 与 inverse dispersion $\theta$ 描述过度离散计数：

$$
P(X=x)=\frac{\Gamma(x+\theta)}{\Gamma(\theta)\Gamma(x+1)}
\left(\frac{\theta}{\theta+\mu}\right)^\theta
\left(\frac{\mu}{\theta+\mu}\right)^x.
$$

当 $\theta$ 大时更接近 Poisson；当 $\theta$ 小时允许更大的 variance。`NB_loss()` 以 `lgamma` 和 log 表达计算 negative log-likelihood，避免直接计算大阶乘。

ZINB 再加入结构性零：

$$
P_{\mathrm{ZINB}}(X=x)=\pi\delta_0(x)+(1-\pi)P_{\mathrm{NB}}(x;\mu,\theta).
$$

对 $x=0$，代码使用 $-\log[\pi+(1-\pi)P_{NB}(0)]$；对非零值使用 NB NLL 再减 $\log(1-\pi)$。论文为 UMI 数据选择 NB、对更高 dropout 的非 UMI 数据选择 ZINB；但具体数据是否需要 zero inflation 应通过拟合与验证决定，不能只按平台名称机械指定。

### 8. 训练过程和最佳模型

`train_GAE()` 默认 500 epochs、Adam、learning rate 0.00025、weight decay $10^{-4}$、gradient clipping 5。论文实验按数据集另设 lr 与 $\alpha$：simulation 为 $10^{-4},0.3$；HOCWTA 为 $2\times10^{-4},1.0$；DLPFC 为 $10^{-4},1.5$。

每轮在整个图上计算 loss，保留 loss 最小时的 state dict，训练后重新载入。它不是 validation early stopping：没有验证集，也不会提前结束，只是 full 500 epochs 后选择最低 training loss。

当前 trainer 还有第二个直接运行 blocker：调用 `random.seed()` 却没有 `import random`。另外 `loss.backward(retain_graph=True)` 会保留计算图，可能增加内存；这属于实现选择而非论文算法。

### 9. 从输入到输出的数值例子

假设一个 spot 的归一化输入含三个基因 $(2,1,0.2)$，GCA 权重为 $(0.8,0.3,0.6)$，$\alpha=1$。残差后的 feature 为

$$
(2,1,0.2)+(1.6,0.3,0.12)=(3.6,1.3,0.32).
$$

它与空间邻居一起经过 GAT。若 decoder 对某基因预测未缩放均值 1.5，而该 spot `scale_factor=2`，最终 $\mu=3.0$。NB/ZINB loss 比较的是这个 3.0 与 raw count，而下游 denoised layer 保存的也是预测均值 3.0。

这个例子说明：GCA 改变 gene channel 权重，GAT 融合邻居，scale factor 恢复 spot 计数尺度，likelihood 负责决定这些参数是否能解释 raw counts。

### 10. 六张主图与表格支持什么

- 图 1 给出表达、空间邻接图、DUSTED、去噪矩阵与三个下游任务的总流程。
- 图 2 展示 GCA 在 GAT 之前，decoder 输出 $\Pi,\Theta,\bar M$，只取 $\bar M$ 作为 denoised expression。
- 图 3 展示 6 种模拟空间结构；结合 4 个 dropout setting 形成 24 个数据集。simulation code 在仓库中 `Not found`。
- 图 4 在 DLPFC section 151673 中显示 CARTPT 空间模式和 Moran's I；DUSTED 图更符合 cortical layer pattern，且论文报告跨 12 sections 的 Moran's I 更高。
- 图 5 比较 HOCWTA 的 PTPRC RNA 与 CD45 protein：论文报告 DUSTED 相对第二名 MAGIC 的 Pearson 提升 0.0264、Spearman 提升 0.0426。
- 图 6 比较 12 个 DLPFC sections 的 clustering；论文报告 DUSTED median ARI/NMI/HS 为 0.515/0.685/0.665。

表 2 中 DUSTED 在四个 simulation settings 的 average MSE 为 0.3839、0.3840、0.3842、0.3929，均低于列出的 baselines。图表支持论文设置下的相对性能，不证明任意数据经更强平滑都会改善生物结论。

本地论文没有独立 Supplementary/Appendix 文档；教程 notebook 是代码使用证据，不是论文补充材料。

### 11. 论文—代码匹配

| 环节 | 直接代码 | 判断 |
|---|---|---|
| GCA avg/max pooling 与 sigmoid | `DUSTED/model.py:55-91` | Exact |
| $X+\alpha(A\odot X)$ | `DUSTED/model.py:101-121` | Partial：意图一致，undefined `alpha` 阻断运行 |
| 两层 GAT encoder/decoder call sites | `DUSTED/model.py:104-135` | Partial：结构存在，custom GATConv 源码缺失 |
| decoder weight/attention tying | `DUSTED/model.py:125-129` | Partial：赋值与参数传递可见，外部实现 Not found |
| $\mu,\theta,\pi$ 激活 | `DUSTED/model.py:16-52,130-135` | Exact，并含额外 clamp/scale factor |
| NB/ZINB NLL | `DUSTED/loss.py:4-49` | Exact |
| 训练与 best-loss checkpoint | `DUSTED/trainer.py:17-132` | Partial：逻辑存在，missing `random` import 阻断运行 |
| simulation generation | 代码快照搜索范围 | Not found |
| HOCWTA correlation pipeline | 代码快照搜索范围 | Not found |

### 12. 必须保留的边界

1. 去噪会改变表达分布；高 Moran's I 既可能是信号恢复，也可能来自过度平滑。
2. 空间邻居可能跨组织边界，radius 选择直接影响信息泄漏范围。
3. GCA attention 是模型权重，不等同于实验测得的 gene noise rate。
4. $\mu$ 是条件均值估计，不是“真实无噪声表达”的直接观测。
5. NB/ZINB 假设需要与计数生成机制匹配；ZINB 并非越复杂越好。
6. 当前 commit `e6b8975…` 有 undefined `alpha`、missing `random` import 和外部 STAGATE dependency 缺失，不能声称开箱即跑。
7. notebook 中的绝对数据路径、参数拼写与 R/mclust 依赖还会影响复现。
8. 论文 simulation 与 HOCWTA 完整分析代码未随当前快照提供。
9. DUSTED 是 denoiser，不直接输出 SVG significance 或因果空间机制。

### 13. 一句话理解

DUSTED 先在整张切片上学习每个基因的通道门控，再沿空间邻接图用 GAT 融合 spot 信息，以 NB/ZINB raw-count likelihood 训练均值、离散度和额外零三个输出头，并把经 library-size 校准的预测均值作为去噪表达；算法设计清楚，但当前公开 commit 仍需修复运行 blocker 和补齐外部依赖才能严格复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DUSTED: Dual-Attention Enhanced Spatial Transcriptomics Denoiser

**Authors**: Jun Zhu, Yifu Li, Zhenchao Tang, Cheng Chang
**Published**: AAAI Conference on Artificial Intelligence, 2025 (Vol. 39, No. 1, pp. 1219-1227)
**DOI**: 10.1609/aaai.v39i1.32110
**Code**: https://github.com/Lifeomics/DUSTED

---

### Motivation & Novelty

#### Problem

Spatially Resolved Transcriptomics (SRT) data suffer from technical noise (dropout events, PCR amplification bias, library size variation) that produces sparse gene expression matrices and blurs spatial patterns. Denoising is essential before downstream analyses like spatial domain clustering, gene-protein correlation, and marker gene identification.

#### Limitations of Existing Approaches

- **scRNA-seq denoising methods** (DCA, Eraslan et al., *Nature Communications* 2019; MAGIC, Van Dijk et al., *Cell* 2018; kNN-smoothing, Wagner et al., *bioRxiv* 2017): Ignore spatial information, treating each spot independently
- **Spatial denoising with image dependency** (Sprod, Wang et al., *Nature Methods* 2022; SiGra, Tang et al., *Nature Communications* 2023; Smoother, Su et al., *Genome Biology* 2023; stSME, Pham et al., *Nature Communications* 2023): Require auxiliary histological images, limiting applicability to datasets without imaging
- **Spatial methods without gene-level noise modeling** (STAGATE, Dong and Zhang, *Nature Communications* 2022): Use spatial attention but model MSE loss, ignoring the count distribution of gene expression and heterogeneous noise levels across genes

#### Unique Contributions

1. **Dual-attention mechanism**: Combines Gene Channel Attention (GCA) for gene-level noise recalibration with Graph Attention for spatial feature integration — no external image data needed
2. **NB/ZINB distribution modeling**: Models gene expression as Negative Binomial (for UMI-based data) or Zero-Inflated NB (for non-UMI data), providing biologically appropriate loss functions
3. **Simulation benchmark**: Proposes a systematic SRT simulation pipeline using SymSim + scCube + spatially varying dropout for quantitative denoising evaluation

---

### Method Overview

DUSTED is a graph autoencoder with dual attention mechanisms for self-supervised SRT denoising. The pipeline:

1. **Preprocessing**: Select top 3000 HVGs, normalize, log-transform, build spatial neighborhood graph (Euclidean radius)
2. **Gene Channel Attention (GCA)**: Average and max pooling over spots → shared MLP → sigmoid → gene-specific attention weights. Applied via residual connection with weight $\alpha$
3. **GAT Encoder**: 2-layer Graph Attention Network (G→512→30) producing 30-dim latent embeddings that capture spatial gene expression patterns
4. **GAT Decoder**: Tied weights (transposed encoder) and tied attention coefficients → 3 output heads for NB/ZINB parameters (mean, dispersion, dropout rate)
5. **NB/ZINB Loss**: Negative log-likelihood computed against raw counts, enabling self-supervised training

The denoised output is the predicted mean parameter, post-processed with normalization and log-transform.

See `doc_method.md` for full equation derivations and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Datasets

| Dataset | Type | Size | Use |
|---------|------|------|-----|
| Simulated (24 datasets) | SymSim + scCube | Varied | Quantitative MSE evaluation |
| HOCWTA (10x Visium) | Human ovarian cancer | 1 section | Gene-protein correlation (PTPRC/CD45) |
| DLPFC (10x Visium) | Human prefrontal cortex | 12 sections | Spatial pattern recovery + clustering |

#### Metrics

- **MSE**: Mean squared error between denoised and ground truth (simulated data)
- **Pearson/Spearman correlation**: Between PTPRC gene and CD45 protein expression (HOCWTA)
- **Moran's I**: Spatial autocorrelation of layer marker genes (DLPFC)
- **ARI/NMI/HS**: Clustering metrics against manual annotations (DLPFC)

#### Comparative Results

**Simulated data (24 datasets, 4 noise settings)**:
- DUSTED achieves lowest average MSE across all settings (0.3839-0.3929)
- 69.6% MSE reduction vs raw data
- Competitive with DCA and MAGIC, outperforms STAGATE and Smoother

**HOCWTA (gene-protein correlation)**:
- Pearson: 0.339 (DUSTED) vs 0.312 (MAGIC, 2nd best) — 8.45% improvement
- Spearman: 0.422 (DUSTED) vs 0.380 (MAGIC) — 11.31% improvement

**DLPFC (spatial patterns)**:
- Moran's I: DUSTED achieves values closest to 1 with smallest standard deviation
- Clustering (original paper, STAGATE+mclust): ARI=0.515, NMI=0.685, HS=0.665 (median)
- Clustering (updated README, PCA+mclust): ARI=0.4825, NMI=0.6433, HS=0.6150 (mean across 12 sections)

**Ablation study**: Removing GCA reduces Pearson by 11.1%, Spearman by 4.4%, and clustering ARI by 14.53%.

#### Baselines Compared

| Method | Year | Venue | Type |
|--------|------|-------|------|
| DCA | 2019 | Nature Communications | scRNA-seq denoiser (autoencoder + NB/ZINB) |
| MAGIC | 2018 | Cell | scRNA-seq (diffusion-based smoothing) |
| STAGATE | 2022 | Nature Communications | Spatial (GAT autoencoder, MSE loss) |
| Smoother | 2023 | Genome Biology | Spatial (weighted graph + HMR field) |
| stlearn* | — | — | Added in README update |
| Sprod* | 2022 | Nature Methods | Added in README update |

---

### Reproducibility

**Rating: 2/5**

#### Strengths
- Core model code (model.py, loss.py, trainer.py) is clean and well-organized
- Two tutorial notebooks demonstrate the full DLPFC evaluation pipeline
- Updated evaluation results in README show transparency about methodology changes
- Model architecture is straightforward with few hyperparameters

#### Weaknesses
- **Critical bug**: `model.py:121` uses undefined global `alpha` instead of `self.alpha` — code cannot run as-is
- **Missing import**: `trainer.py:44` calls `random.seed()` but `import random` is missing
- **Tutorial typo**: `save_reconstrction=True` (misspelled) would crash with TypeError
- **Missing dependency**: STAGATE_pyG is not listed in requirements.txt but is essential for the custom GATConv, graph construction, and data transfer
- **Missing simulation code**: The 3-step simulation pipeline (SymSim → scCube → spatial dropout) is described but not provided
- **Missing HOCWTA code**: Gene-protein correlation analysis has no corresponding notebook
- **Hardcoded data paths**: Tutorial notebooks use absolute paths (`/databak/liyifu/`, `/data/DLPFC/`)
- **No pip/conda installable package**: No setup.py or pyproject.toml
- **R dependency**: Clustering evaluation requires mclust (R package) via rpy2

#### Practical Setup Notes

1. Install STAGATE_pyG first (from the STAGATE GitHub repo, PyG version)
2. Fix the alpha bug in model.py: change `alpha * h1` to `self.alpha * h1`
3. Adjust data paths in tutorial notebooks
4. Ensure R and mclust package are installed for clustering evaluation
5. GPU recommended: paper uses NVIDIA Quadro GV100 (32GB)

#### Key Hyperparameters

| Parameter | Simulated | HOCWTA | DLPFC |
|-----------|-----------|--------|-------|
| Learning rate | 1e-4 | 2e-4 | 1e-4 |
| $\alpha$ (residual) | 0.3 | 1.0 | 1.5 |
| Loss function | NB | NB | ZINB |
| Epochs | 500 | 500 | 500 |
| Hidden dims | [G, 512, 30] | [G, 512, 30] | [G, 512, 30] |
| Radius (rad_cutoff) | Adjusted | Adjusted | 150 |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
