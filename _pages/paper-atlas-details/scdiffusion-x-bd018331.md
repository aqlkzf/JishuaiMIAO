---
layout: default
permalink: /paper-atlas/scdiffusion-x-bd018331/
title: "scDiffusion-X"
nav: false
description: "scDiffusion-X 先用两个模态专属自编码器把 RNA 计数和二值 ATAC 峰压到各自 100 维潜空间，再在这两个潜变量上联合加噪和去噪；去噪网络的两条分支由三个双向交叉注意力模块（DCA）连接，使 RNA 在每个去噪阶段读取 ATAC 信息，同时 ATAC 也读取 RNA 信息。"
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
      <span>Nature Communications · 2026</span>
    </div>
    <h1>scDiffusion-X</h1>
    <p>Multi-modal Diffusion Model with Dual-Cross-Attention for Multi-Omics Data Generation and Translation</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-71744-x" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scDiffusion-X：从配对 RNA–ATAC 到生成、翻译与调控解释

### 它要解决什么问题

单细胞 multiome 在同一个细胞中同时测量 RNA 表达和染色质可及性，因此比把两个单模态数据集事后对齐更直接地保留了“峰开放—基因表达”的细胞内联系。但配对实验昂贵、样本量有限，也很难覆盖稀有细胞或所有扰动条件。scDiffusion-X 的目标不是只做一个低维整合图，而是学习配对 RNA–ATAC 的联合生成分布，使同一模型可以生成成对数据、按细胞类型生成、从一个模态翻译另一个模态，并从模型内部的跨模态交互提取候选调控关系。

论文将它与 MultiVI、CFGen、scDesign3、scVI/peakVI 和 BABEL 比较。这里要避免把作者的动机写成普遍定论：这些基线各自面向整合、生成或翻译中的不同任务；本文证据支持的是在作者选定的数据、预处理和指标上，scDiffusion-X 的生成或翻译结果更接近真实数据，而不是证明扩散模型在所有 multi-omics 场景都优于 VAE、flow 或统计模型。

### 一句话抓住方法

scDiffusion-X 先用两个模态专属自编码器把 RNA 计数和二值 ATAC 峰压到各自 100 维潜空间，再在这两个潜变量上联合加噪和去噪；去噪网络的两条分支由三个双向交叉注意力模块（DCA）连接，使 RNA 在每个去噪阶段读取 ATAC 信息，同时 ATAC 也读取 RNA 信息。

```text
配对 multiome + 条件标签
  RNA counts ──RNA AE──> r0 ─┐
                              ├─ 独立加噪到 (rt, at)
  binary ATAC ─ATAC AE──> a0 ─┘
                                  │
                      双分支 U-Net 式去噪器
                    RNA branch ⇄ DCA ⇄ ATAC branch
                                  │
                    预测两模态噪声并反向采样
                                  │
                   (r0*, a0*) ──各自 decoder──>
                    生成 RNA + 生成 ATAC
```

### 第一步：先训练两个自编码器

RNA 解码器采用负二项分布。论文写为

$$
\mu=s\rho,\qquad \rho=\operatorname{softmax}(D_R(r)),
$$

其中 $s$ 是该细胞的总 RNA 计数，$r$ 是 RNA 潜变量，基因离散度 $\theta$ 可学习。ATAC 已被二值化，解码概率为

$$
\pi=\operatorname{sigmoid}(D_A(a)).
$$

代码直接实现了这两个似然：`encoder_model.py:125-163` 计算 size factor，并以负对数似然训练 RNA/ATAC；`encoder_model.py:308-323` 用 softmax 乘 size factor 得到 RNA 均值，用 sigmoid 得到 ATAC 开放概率。补充图 S12a 给出自编码器结构；配置把两个模态都压到 100 维。这里的训练顺序很重要：必须先有自编码器 checkpoint，并生成潜空间标准差文件 `norm_factor.npz`，扩散训练和翻译脚本才有完整输入。

### 第二步：在潜空间学习联合扩散

对配对潜变量 $r_0,a_0$，前向过程分别加入高斯噪声：

$$
q(r_t\mid r_{t-1})=\mathcal N(\sqrt{1-\beta_t}r_{t-1},\beta_t I),
$$

$$
q(a_t\mid a_{t-1})=\mathcal N(\sqrt{1-\beta_t}a_{t-1},\beta_t I).
$$

去噪网络同时接收 $(r_t,a_t)$、时间步 $t$ 和可选条件 $c$，预测两个模态的噪声。条件（例如细胞类型）被嵌入后加到时间嵌入中。代码默认 1000 个扩散步，训练损失是两模态噪声预测 MSE；实际生成脚本还提供 20 步 DPM-Solver/DPM-Solver++ 快速采样。因此，“训练扩散步数 1000”不等于“论文结果一定逐步运行 1000 次 DDPM 反演”。

潜变量进入扩散网络前还会除以 `norm_factor.npz` 中的逐维标准差。这个实现细节在主论文方法公式中没有展开，却是复现时不能漏掉的接口。

### 第三步：DCA 如何让两个模态互相读取

对 RNA 表示 $R$ 与 ATAC 表示 $A$，DCA 分别构造 $Q,K,V$。RNA 从 ATAC 取信息：

$$
M_{R,A}=\operatorname{softmax}\left(\frac{Q_RK_A^\top}{\sqrt d}\right),
\qquad R'=M_{R,A}V_A;
$$

反方向为

$$
M_{A,R}=\operatorname{softmax}\left(\frac{Q_AK_R^\top}{\sqrt d}\right),
\qquad A'=M_{A,R}V_R.
$$

两边再投影回原通道并与输入做残差相加。`multimodal_unet.py:998-1040` 是这部分最直接的实现证据。代码仍沿用音视频项目命名：`video` 表示 RNA，`audio` 表示 ATAC，阅读时不要按字面理解。

论文说三个 DCA 的“feature dimensions”为 256、128、256；代码确实把 DCA 放在编码器、中间层、解码器三个深度，但 `CrossAttentionBlock_cell` 在 `multimodal_unet.py:946-984` 将 Q/K/V 投影维度统一硬编码为 64。更合理的解释是 256/128/256 描述所在网络层的通道宽度，而注意力内部的 $d$ 在这份发布快照中是 64；若把两者当成同一个参数，论文与代码并不一致。

### 四类推断任务是怎样从同一个模型得到的

1. **成对生成**：从两个独立高斯噪声开始联合反向采样，再由两个 decoder 还原 RNA 与 ATAC。
2. **条件生成**：把细胞类型或其他离散条件的 embedding 加入时间 embedding，生成指定条件下的细胞。
3. **模态翻译**：已知一个模态时，每个反向步都用该真实潜变量的前向加噪版本替换对应分支，只让未知模态从噪声去噪。`multimodal_gaussian_diffusion.py:690-707` 实现了这种 replacement 机制；`multimodal_translation.py:114-193` 负责真实数据编码、标准差归一化和采样。
4. **扰动翻译**：把扰动后的已知模态作为翻译输入，预测另一模态的变化方向。它是条件翻译的应用，不等同于从随机对照实验中识别因果效应。

### 注意力怎样转成候选调控网络

论文不是直接把一个 attention 值叫作 gene–peak 边。它先在指定细胞类型下汇总双向注意力，选高分 RNA/ATAC 潜元素，再对目标注意力元素反向传播：

$$
\operatorname{grad}_R=\frac{\partial M^c_{ij}}{\partial x_R},\qquad
\operatorname{grad}_A=\frac{\partial M^c_{ij}}{\partial x_A}.
$$

梯度幅度把潜元素追溯回输入基因和峰；论文实验取每个元素梯度最大的 100 个基因/峰，并为展示选择高注意力潜元素。发布库能输出 DCA attention vectors，但完整网络筛选、统计和作图主要位于 `evaluation_script/regulatory_multi_diff.ipynb`，不是一个参数化命令行流水线。因此这些边应称为“模型解释产生的候选调控关系”，不能仅凭 attention/gradient 当作已验证的生物学因果边。

### 论文用什么证据支持它

- **生成**：OpenProblem 和 PBMC10k 上比较 MultiVI、CFGen、scDesign3、scVI 与 peakVI。图 2 同时展示 UMAP 和 SCC、MMD、LISI、AUC；AUC 越接近 0.5，外部分类器越难区分真实与生成细胞。论文报告 ATAC AUC 从最佳基线 0.846 改善到 0.575。
- **翻译**：BABEL 数据上，图 3 报告 RNA/ATAC 翻译 LISI 为 0.55/0.67，而 BABEL 为 0.05/0.31；MMD 分别降低 83%/54%。补充图 S3 增加外部 GM12878 测试，但审稿记录也提醒跨研究批次效应会影响这种比较。
- **不确定性**：对 ATAC→RNA 翻译独立生成 100 次，构建 95% prediction interval；论文报告平均覆盖率 93.94%。这是生成分布的经验校准检查，不是模型参数后验置信区间。
- **调控解释**：图 4 展示细胞类型特异 attention、梯度排名和异质网络；补充表 S2 中 scDiffusion-X 的 HiChIP 命中为 237/366、precision 0.6475，高于所列基线。该验证支持候选边富集于已有染色质互作，但不证明每条边都具有方向性因果调控。
- **消融**：图 5 比较 DCA 数目、用线性层替换 DCA，以及有/无 DCA；结果支持跨模态注意力有用，但更多 DCA 同时也增加模型容量，不能把提升完全归因于“生物可解释性”。

### 复现与版本边界

- 本工作区代码快照固定在提交 `7d1342e4bc3b76f3449dc0ef292f9e4ce877c7f0`，包版本为 `0.0.2`；2026-07-19 查询官方仓库 HEAD 已是 `d60d928b635ab7a52ace030a641efd02137c193f`，所以这里的代码结论只对固定快照负责。
- 主论文、三份补充 PDF、主图 1–5 和补充图 S1–S12 已在本地核读。`paper_supp3.pdf` 是审稿/作者回复材料，不应当作独立实验结果来源。
- 发布仓库提供训练和采样脚本以及三个评估 notebook，但 README 仍留有待补说明，路径需要人工修改；数据、预训练权重和完整论文结果未在本次工作区执行。
- `pyproject.toml` 同时约束旧版 `pytorch_lightning<1.9.0`、`scvi-tools<=1.0.0` 和较新的 `torch>=2.1.2`，环境求解存在风险。本次只做静态源代码映射，没有验证从零安装或端到端数值复现。
- 补充表 S1 的显存和时间是在作者环境下测得；它不能推出任意“至少 12 GB GPU”都必然可复现全部训练与评估。

### 阅读顺序

先看论文图 1 建立 AE→潜扩散→DCA 的结构，再看图 3 的 replacement translation，最后看图 4 理解 attention 与梯度如何组合。代码侧依次读 `encoder_model.py`、`multimodal_unet.py`、`multimodal_gaussian_diffusion.py`、`multimodal_translation.py`；若要核对论文结果，再进入三个评估 notebook，并把 notebook 结果与可复用库接口区分开。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scDiffusion-X: Latent Diffusion Model with Dual-Cross-Attention for Multi-Omics Generation and GRN Inference

**Paper**: Multi-modal Diffusion Model with Dual-Cross-Attention for Multi-Omics Data Generation and Translation
**Authors**: Erpai Luo, Lei Wei, Minsheng Hao, Xuegong Zhang, Qiao Liu
**Journal**: Nature Communications, 2026
**DOI**: 10.1038/s41467-026-71744-x
**Code**: https://github.com/EperLuo/scDiffusion-X

---

### Motivation & Novelty

#### Biological Problem

Paired single-cell multi-omics profiling (e.g., 10x Multiome capturing scRNA-seq + scATAC-seq in the same cell) provides unique opportunities to study gene regulation: which chromatin accessibility peaks control which genes in which cell types. However, these datasets are expensive, scarce, and limited in scale compared to single-modality experiments.

Computational simulators that generate realistic multi-omics data are essential for:
1. **Benchmarking** computational methods (need ground-truth multi-omics data)
2. **Data augmentation** (rare cell types, underrepresented conditions)
3. **Modality translation** (predict scRNA-seq from scATAC-seq data, expanding single-omics into multi-omics)
4. **Understanding regulation** (extract gene-peak regulatory networks from the generative model)

#### Limitations of Existing Approaches

| Method | Type | Limitation |
|--------|------|-----------|
| MultiVI (Nature Methods, 2023) | VAE | Unimodal posterior; overly smooth; no explicit cross-modal attention |
| CFGen (arXiv, 2024) | Flow | Invertible transforms limit expressiveness; no modality interaction modeling |
| scDesign3 (Nature Biotechnology, 2024) | Statistical | Fails beyond ~10,000 cells; cannot model complex multi-modal distributions |
| scVI (Nature Methods, 2018) | VAE (unimodal RNA) | Single modality only |
| peakVI (Cell Reports Methods, 2022) | VAE (unimodal ATAC) | Single modality only |
| BABEL (PNAS, 2021) | Encoder-decoder | Translation only; no generation; yields point estimates; limited performance |

#### Unique Contributions

1. **Dual-Cross-Attention (DCA)**: A bidirectional cross-attention mechanism operating in the latent diffusion process that explicitly models information flow between RNA and ATAC modalities. Unlike concatenation-based integration, DCA learns which features of one modality most influence the other at each denoising step.

2. **Multi-task framework**: A single trained model supports (a) unconditional generation, (b) conditional cell-type-specific generation, (c) modality translation, (d) in-silico perturbation, and (e) uncertainty quantification — all from one architecture.

3. **Gradient-based GRN inference**: The DCA attention matrices, combined with gradient backpropagation to the input, enable construction of cell-type-specific heterogeneous gene regulatory networks linking genes to peaks via learned regulatory latent elements. This is a novel use of diffusion model interpretability for biology.

4. **Scalability**: Successfully trained on MiniAtlas (133,549 cells, 56 cell types); performance improves monotonically with dataset size.

---

### Method Overview

scDiffusion-X is a **latent diffusion model** operating in the 100-dimensional latent space of two separate autoencoders (one for RNA, one for ATAC). The architecture has three main components:

**1. Multimodal Autoencoder**: Two MLP autoencoders trained with biologically appropriate likelihoods — Negative Binomial for RNA counts (size-factor-normalized), Bernoulli for binarized ATAC data. Latent dimension = 100 per modality.

**2. Multimodal Denoising Network**: Two parallel U-Net-like branches (one per modality) coupled at three depths via DCA modules. The network receives cell-type labels as conditions (embedded and added to sinusoidal time embeddings). Trained with T=1000 linear beta schedule; inference uses DPM-Solver++ (20 steps).

**3. Dual-Cross-Attention (DCA)**: At each DCA module, $Q_R, K_R, V_R$ (from RNA) and $Q_A, K_A, V_A$ (from ATAC) are computed by projecting each scalar feature position through Linear(1, 64) weight matrices. RNA attends to ATAC ($\text{Att}_{R,A} = \text{softmax}(Q_R K_A^\top/\sqrt{64})$) and vice versa. Outputs are projected back and added as residuals.

**Key assumption**: Paired RNA and ATAC from the same cell are mutually informative — the regulatory relationship between chromatin accessibility and gene expression is real, learned, and can be reversed (translation) and interpreted (GRN).

For implementation details, see doc_method.md. For code-paper correspondence, see doc_code.md.

---

### Evaluation

#### Datasets

| Dataset | Cells | Cell Types | Genes | Peaks | Use |
|---------|-------|-----------|-------|-------|-----|
| OpenProblem (GEO GSE194122) | 69,249 | 22 | 13,431 | 36,553 | Main generation benchmark |
| PBMC10k (10x Genomics) | 10,000 | 14 | 25,604 | 40,086 | Generation comparison |
| BABEL (combined) | 40,465 | — | 34,861 | 223,897 | Translation benchmark |
| MiniAtlas (bioRxiv 2025) | 133,549 | 56 | 36,601 | 165,564 | Scalability + pretraining |

#### Generation Performance

**scRNA-seq quality** (OpenProblem vs. MultiVI, CFGen, scDesign3, scVI, peakVI):
- MMD: **33.3% improvement** over second-best
- LISI: **15.5% improvement** over second-best
- AUC: top performer (closest to 0.5 = indistinguishable from real)

**scATAC-seq quality** (OpenProblem):
- AUC: **0.575** vs 0.846 (best baseline) — 32% improvement

**Cell-type conditional generation** (OpenProblem):
- scRNA AUC: **0.747** vs 0.864 (best baseline)
- scATAC AUC: **0.640** vs 0.802 (best baseline)

#### Modality Translation Performance (BABEL dataset)

vs. BABEL (PNAS, 2021):
- LISI: **0.55/0.67** (scDiffusion-X) vs 0.05/0.31 (BABEL) for RNA/ATAC translation
- MMD: **83% and 54% lower** than BABEL for RNA and ATAC translation respectively
- KLD (marker genes): **59.8% lower** on average across 10 marker genes

#### Perturbation Prediction (cross-modality)

- >80% accuracy for top 20-50 differential peaks when perturbing ZAP70, CD3E, CD4
- >80% accuracy (ACTL6A) and >70% (SMARCC1) on real multiome perturbation dataset (Metzner et al., Cell Systems, 2025)
- Outperforms MultiVI in all perturbation tasks

#### Uncertainty Quantification

- 95% nominal PI coverage: **93.94%** achieved (well-calibrated)
- PI length vs gene S.D.: PCC=**0.9537**, SCC=**0.9460** — the model correctly represents gene-level uncertainty

#### GRN Inference (CD4+ T activated cells)

- 366 gene-peak pairs identified within 120 kbp
- **Precision: 0.6475** (validated by HiChIP loops) vs 0.5191 (SCENIC+, Nature Methods 2023) vs 0.5167 (baseline)
- Marker genes significantly higher gradient rank in **18/22 cell types** (rank sum test)
- Key peaks significantly overlap with ENCODE H3K27ac enhancers and TSS regions (p<0.05, one-sample t-test)

#### Ablation Studies

- 1 DCA → 3 DCA → 5 DCA: performance improves monotonically
- 3 linear layers replacing 3 DCAs: substantially worse than DCA
- Model without DCA: lower MMD, LISI, AUC on both modalities
- 2nd DCA, timestep 1000 identified as most information-rich (highest IE, highest MSE change)

---

### Reproducibility

**Rating: 3/5 (static evidence assessment; no end-to-end rerun in this workspace)**

**Strengths**:
- Complete code on GitHub (https://github.com/EperLuo/scDiffusion-X)
- All 4 datasets publicly available with accession numbers
- Pretrained model weights on Figshare (ID: 28582061)
- Training scripts with hyperparameters included
- ReadTheDocs tutorial site (https://scDiffusionX.readthedocs.io/)

**Weaknesses / Practical Challenges**:
- **Environment**: Requires `pytorch_lightning < 1.9.0` (old version), `scvi-tools <= 1.0.0` (old API), `torch >= 2.1.2`. These version constraints can conflict. Installation may require careful dependency pinning.
- **Data format**: Requires `.h5mu` format (MuData). Preprocessing scripts not fully automated.
- **`norm_factor.npz` dependency**: Diffusion training and inference require a normalization file generated during AE training. This is not documented in the main README — users discovering this through debugging.
- **Code naming**: `video`=RNA, `audio`=ATAC throughout the codebase (inherited from MM-Diffusion). Confusing for readers.
- **DCA parameter discrepancy**: Paper claims feature_dim=256/128/256 but code uses 64 for all DCAs. Generated results may differ from paper if using modified dims.
- **GRN notebooks**: The regulatory analysis lives in Jupyter notebooks, not a scripted pipeline. Reproducibility depends on correct AE+diffusion checkpoint paths.
- **GPU evidence boundary**: Supplementary Table S1 reports roughly 4.45 GB diffusion inference memory and 2.56 GB AE training memory for the normal configuration in the authors' environment. This does not establish that every experiment is reproducible on an arbitrary ≥12 GB GPU.
- **Version boundary**: The local snapshot is commit `7d1342e4bc3b76f3449dc0ef292f9e4ce877c7f0`, package version `0.0.2`; the official repository HEAD observed on 2026-07-19 was `d60d928b635ab7a52ace030a641efd02137c193f`, so the source mapping is snapshot-specific.
- **Execution boundary**: Paper, supplements, figures, scripts, and notebooks were inspected, but datasets, checkpoints, and reported numerical results were not rerun here.

**Data availability**: All data publicly available. OpenProblem: GSE194122; PBMC10k: 10x website; BABEL: Google Drive; MiniAtlas: bioRxiv 2025 (Wu et al.). ENCODE H3K27ac: encodeproject.org; HiChIPdb: health.tsinghua.edu.cn/hichipdb/; PerturBase: perturbase.cn.

**Known pitfalls**:
- Preserve the recorded source snapshot when comparing results; current upstream has moved beyond the local commit.
- AE must be trained before diffusion; latent std must be computed and saved
- Translation inference requires the model to have been trained without cell-type conditioning (unconditional), or with the same label set as translation targets
- DPM-Solver++ is used for inference (not DDPM); the 20-step approximation may introduce slight quality difference vs full 1000-step sampling

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
