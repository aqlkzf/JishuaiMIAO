---
layout: default
permalink: /paper-atlas/spatialmeta-8e89ce68/
title: "SpatialMETA"
nav: false
description: "SpatialMETA 面向一类特殊而困难的数据：空间转录组（ST）给出离散基因计数，空间代谢组（SM）给出连续质谱强度；二者往往来自相邻而非同一张组织切片，分辨率、坐标和组织形状也不同。它的任务不是简单拼接两个矩阵，而是依次解决几何对齐、分辨率统一、跨模态整合和跨样本批次校正，最后提供空间聚类、模态贡献、代谢物注释和空间网络分析。 本解读以 PMC 正文、主图 1–4、补充 PDF papersupp1."
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
      <span>Nature Communications · 2025</span>
    </div>
    <h1>SpatialMETA</h1>
    <p>Integrating cross-sample and cross-modal data for spatial transcriptomics and metabolomics with SpatialMETA</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-63915-z" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SpatialMETA">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/WanluLiuLab/SpatialMETA" target="_blank" rel="noopener noreferrer" aria-label="Open code for SpatialMETA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpatialMETA：把相邻切片的空间转录组与空间代谢组放进同一坐标系

SpatialMETA 面向一类特殊而困难的数据：空间转录组（ST）给出离散基因计数，空间代谢组（SM）给出连续质谱强度；二者往往来自相邻而非同一张组织切片，分辨率、坐标和组织形状也不同。它的任务不是简单拼接两个矩阵，而是依次解决**几何对齐、分辨率统一、跨模态整合和跨样本批次校正**，最后提供空间聚类、模态贡献、代谢物注释和空间网络分析。

本解读以 PMC 正文、主图 1–4、补充 PDF `paper_supp1.pdf`，以及官方代码快照 `SpatialMETA/` 为证据。代码快照来自 `https://github.com/WanluLiuLab/SpatialMETA`，commit 为 `909844e03c2ddffa331e8c45212830f8ffc85553`，包内版本为 `0.0.3.0`。以下“代码实现”均指该固定快照，而不是当前 PyPI 或 GitHub 最新状态。

### 1. 输入为什么不能直接拼接

ST 的每一行是一个 Visium spot，每一列是基因，原始值是带大量零的计数。SM 的每一行是质谱像素，每一列是一个 $m/z$ 特征，值是连续强度。相邻切片还带来三重错位：

1. SM 像素与 ST spot 的坐标不一致；
2. SM 的空间分辨率通常更高，一个 ST spot 周围对应多个 SM 像素；
3. 多个患者或组织样本之间存在实验批次差异。

因此 SpatialMETA 的四段流程是：对齐 → 重分配 → 条件变分自编码整合 → 下游分析。Figure 1 从左到右正好画出了这四段信息流。

### 2. 对齐：先让两张相邻切片在几何上可比较

对齐模块以 ST 空间坐标/组织图像为目标，把 SM 坐标经过旋转、平移、尺度变化和可微形变映射到 ST 坐标系。论文采用改写自 STalign 的 LDDMM；本地 `spatialmeta/model/_alignment_module.py` 调用 `external/stalign/STalign.py` 的仿射加微分同胚变换。其目的不是根据基因—代谢物相关性强行配对，而是让组织边界和可用的对应点在空间上靠拢。

这一步有明确边界：相邻切片若形态差异很大、组织缺损明显或初始旋转相差过大，自动优化可能落入错误解。论文流程允许预旋转和人工检查；复现时必须把对齐前后坐标叠图作为质控，不能只依赖最终损失值。

### 3. 重分配：把高分辨率 SM 汇总到 ST spot

对齐后，代码 `spot_align_byknn()` 以每个 ST spot 为查询点，在变换后的 SM 坐标中寻找默认 5 个近邻，并对合格邻居的代谢强度求平均。距离阈值按最近空间尺度乘默认系数 1.5 控制，避免把远处 SM 像素错误分给组织边缘的 ST spot。

得到的不是“原始 SM 像素”，而是与 ST spot 一一对应的重分配 SM 矩阵。后续联合模型假定两种模态已经按行配对；因此几何对齐或 KNN 重分配的错误会直接进入潜空间，CVAE 本身不会重新估计空间变换。

### 4. 特征选择：空间变化不等于生物变化

SpatialMETA 用 Moran's I 选择空间变异基因（SVG）和空间变异代谢物（SVM）。多样本模式还会删除明显由单一样本驱动的特征：代码默认条件是相对其他样本 fold change 大于 3，且该样本中至少 80% spot 出现该特征。这样做是为了避免模型把“某批次独有的高值”当作跨样本生物区域。

这里的空间信息主要用于对齐、重分配、特征选择和下游空间分析；核心 CVAE 并没有空间邻接图或 GNN 消息传递。不能把 SpatialMETA 描述成空间图神经网络。

### 5. 编码：两种分布先分开，再形成联合潜变量

对同一个配对 spot，输入可写成 $X_{ST}$ 与 $X_{SM}$。`ConditionalVAESTSM.encode()` 先把 ST 做 `log(X_ST + 1)`，SM 不在此处做 log；二者进入独立、无批次标签的编码器：

$$
q_{ST}=F^{ST}_{enc}(\log(X_{ST}+1)),\qquad
q_{SM}=F^{SM}_{enc}(X_{SM}).
$$

编码结果拼接后由线性层得到联合高斯分布参数：

$$
q=[q_{SM}\|q_{ST}],\qquad
\mu=F_{\mu}(q),\qquad
\sigma^2=\exp(F_{\sigma}(q))+10^{-4},
$$

$$
z\sim\mathcal N(\mu,\operatorname{diag}(\sigma^2)).
$$

$10^{-4}$ 防止方差退化为零。代码还把两个模态各自的编码结果通过同一个单模态投影层得到 $\mu_{ST}$ 与 $\mu_{SM}$。联合 $z$ 用于整合表示，两个单模态均值用于模态校正重建和贡献度解释。

### 6. 解码：共享解码器把联合与单模态表示拉到可比较空间

模型有一个 ST 解码器和一个 SM 解码器，但每个解码器都会被调用两次：

- 联合潜变量 $z$ 分别重建 ST 和 SM；
- $\mu_{ST}$ 经过同一个 ST 解码器重建 ST，$\mu_{SM}$ 经过同一个 SM 解码器重建 SM。

这四条重建路径共享输出头，迫使联合表示和单模态表示保持可比较。批次标签只在解码阶段拼接到潜变量上；编码器不接收批次标签。直观上，编码器负责抽取尽可能批次不变的生物状态，解码器再根据样本身份解释平台或样本特有偏移。

Figure 1d 中纵向的 ST/SM 编码、联合嵌入、模态嵌入和两套 batch-variant decoder 正是这一结构。图中的“angular similarity”也说明贡献度不是直接读取某个注意力权重。

### 7. 为什么 ST 用 ZINB，而 SM 用 Gaussian

ST 原始计数由零膨胀负二项分布建模：

$$
p(x)=\pi\mathbf 1[x=0]+(1-\pi)\operatorname{NB}(x;\mu,\theta).
$$

代码的 ST 输出头产生均值、离散度和零膨胀 logits；均值再乘该 spot 的文库大小。SM 是归一化后的连续强度，默认使用 Gaussian 负对数似然，输出均值和方差。`ConditionalVAESTSM` 还支持 MSE 或零膨胀 Gaussian 选项，但论文主路径与构造默认是 ST=`zinb`、SM=`g`。

总目标包含六类量：联合潜变量对 ST/SM 的两项重建、单模态潜变量对 ST/SM 的两项校正重建、联合高斯到标准正态的 KL 散度，以及多批次之间联合均值的 MMD：

$$
\mathcal L=
w_{ST}L_{ST}+w_{SM}L_{SM}+
w_{ST,c}L_{ST,c}+w_{SM,c}L_{SM,c}+
w_{KL}L_{KL}+w_{MMD}L_{MMD}.
$$

`fit(mode='single')` 把 ST 两条重建权重设为 5、SM 设为 1、KL 设为 0.5；`mode='multi'` 分别设为 8、2、1，并把 MMD 权重设为 10。多样本横向整合真正依赖显式传入 `mode='multi'` 和批次键，不能只创建 batch 标签就假定高权重 MMD 自动启用。

### 8. 训练实现中一个容易读错的细节：KL warm-up

默认训练 35 epoch、batch size 128、AdamW 学习率 $5\times10^{-5}$、weight decay $10^{-6}$。接口参数 `n_epochs_kl_warmup=400` 看似远大于 35，但 `fit_core()` 会先执行：

```python
n_epochs_kl_warmup = min(max_epoch, n_epochs_kl_warmup)
```

因此默认运行中 warm-up 实际被截为 35，KL 权重在训练期内线性升到目标值；它不是只达到 $35/400$。这是直接代码证据对旧解释的校正。

代码类里还定义了 `self.v` 与 `self.to_k`，但它们没有进入 `encode()`、`decode()` 或主损失。公开实现的融合是编码拼接和共享解码约束，不应把这两个未使用参数描述成已生效的 mixture-of-experts 路由。

### 9. 模态贡献度究竟表示什么

模型计算联合嵌入与两个单模态嵌入的夹角相似度：

$$
s_m=1-\frac{\arccos(\cos(\mu_m,z))}{\pi},
$$

再用 $s_{ST}-s_{SM}+0.5$ 构造 ST 贡献分数，SM 则取互补方向。它反映一个 spot 的联合表示更接近哪一个模态表示，不是因果贡献、特征重要性或注意力概率；数值也未必天然严格落在 $[0,1]$，解释时应结合代码输出与图例范围。

Figure 3a–d 将这一量画成 cluster 分布和空间图。后续面板在 ccRCC 的 Imm_4 区域同时显示基因 `CYP2J2`、`ACSM2A` 与脂质相关代谢物富集，支持“联合表示能联结转录与代谢空间模式”，但不证明这些分子之间存在直接调控关系。

### 10. 主图和补充图共同支持了什么

- **Figure 1**：方法结构证据。它明确显示 alignment、KNN reassignment、SVF、联合/横向整合与下游分析，并显示 ST 和 SM 使用不同输出分布。
- **Figure 2**：垂直整合 benchmark。ccRCC、GBM 和小鼠脑示例把重建、空间连续性、marker score、生物保留与资源开销分开评价。图支持 SpatialMETA 在这些数据/指标组合上取得均衡表现，但不是所有单项都绝对最优。
- **Figure 3**：解释性和生物发现。贡献度空间图与 Imm_4 的基因—代谢物共同富集展示了分析用途。
- **Figure 4**：五个 ccRCC 样本的纵向+横向整合。按样本着色的 UMAP 混合、按 cluster 着色的结构保留、空间网络与 benchmark 一起说明 MMD 路径在这些样本上兼顾了批次校正和生物结构。
- **补充材料**：包含对齐/重分配细节、更多样本、消融、归一化、benchmark 指标与可扩展性。它也提醒结果依赖预处理、对齐质量和比较方法配置。

### 11. 论文—代码对应表

| 论文机制 | 固定快照入口 | 判断 |
|---|---|---|
| LDDMM 仿射与非线性空间对齐 | `model/_alignment_module.py`, `external/stalign/STalign.py` | Exact，源自内嵌改写实现 |
| KNN 重分配到 ST 分辨率 | `preprocess/_preprocess.py::spot_align_byknn` | Exact，默认邻居数 5 |
| Moran's I SVF 与批次偏置过滤 | `preprocess/_preprocess.py::spatial_variable_joint_adata_sm_st` | Exact |
| ST/SM 双编码器与联合 Gaussian | `model/_moe.py::encode` | Exact |
| 联合与单模态共享解码器 | `model/_moe.py::decode` | Exact |
| ST-ZINB、SM-Gaussian 重建 | `model/_moe.py::forward`, `util/loss.py` | Exact，另有可选损失 |
| 多批次 MMD | `model/_moe.py::forward/fit` | Exact，但需批次索引和 multi 配置 |
| 模态贡献 | `model/_moe.py::get_modality_contribution` | Partial：实现是角相似度，不是裸 cosine |
| MoE 路由参数 | `model/_moe.py::__init__` | Not found in active forward path |

### 12. 复现边界与检查清单

2. 保存原始 ST/SM 坐标、预旋转、LDDMM 参数和对齐叠图；邻接切片形态不一致是首要误差源。
3. 记录 KNN 邻居数、距离阈值与被排除 spot，确认重分配后两模态行顺序完全一致。
4. 多样本运行显式设置 batch keys 与 `mode='multi'`；同时报告生物保留和 batch correction，不能只看样本 UMAP 混合。
5. 区分模型的 denoised reconstruction 与原始测量；重建相关性高不代表未测代谢物的因果预测。
6. 本次核验覆盖论文正文、四张主图、补充 PDF 和直接源代码，但没有下载所有外部数据、重跑 GPU 训练、全部 benchmark 工具或复现论文数值。因此静态机制映射可确认，端到端数值复现仍是 `Not run`。

一句话概括：SpatialMETA 先把相邻切片在物理空间中对齐并统一分辨率，再用符合各自数据分布的双编码/共享解码 CVAE 做跨模态融合，用 decoder batch condition 与 MMD 做跨样本校正；空间信息包围着模型，但核心潜变量模型本身不是空间图网络。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpatialMETA — Paper Summary

### Motivation & Novelty

**Biological problem**: The tumor microenvironment (TME) is shaped by both gene expression programs (transcriptomics) and metabolic states. Spatial transcriptomics (ST) captures the former; spatial metabolomics (SM) via mass spectrometry imaging captures the latter. Combining them enables the identification of spatially resolved metabolic reprogramming — for instance, immune clusters with dysregulated lipid metabolism in renal cell carcinoma. However, most ST+SM data are collected from adjacent tissue sections, creating computational challenges that no existing method adequately addresses.

**Limitations of existing methods**:
- **spaVAE / spaMultiVAE** (*Nature Methods*, 2024, Tian et al.): designed for same-section multi-omics (ST + spatial proteomics/epigenomics); vertical and horizontal integration done in separate frameworks; no alignment step.
- **SpatialGLUE** (*Nature Methods*, 2024, Long et al.): GNN-based; assumes same-section data; optimized for ST+SP/SE, not ST+SM; modality weighting biased toward SM in ST+SM settings.
- **MISO** (*Nature Methods*, 2025, Coleman et al.): integrates ST+SM+histological images; works best for same-section data with histology; computationally heavier.
- **totalVI** (*Nature Methods*, 2021, Gayoso et al.): handles paired count+continuous data but is non-spatial and not designed for mass spectrometry data distributions.
- **Stabmap** (*Nature Biotechnology*, 2024, Ghazanfar et al.): mosaic integration using unshared features; not designed for spatial or metabolomics data.
- **scPoli / SCALEX / scAtlasVAE**: good at batch correction but spatial and metabolomics-specific features are absent.

**What SpatialMETA contributes uniquely**:
1. **Simultaneous vertical + horizontal integration in one CVAE framework** — no two-step approach.
2. **Modality-matched likelihoods**: ZINB for ST (count data), Gaussian for SM (continuous intensities).
3. **Shared decoders** for joint and single-modal embeddings — forces modality fusion and enables modality contribution quantification.
4. **Integrated spatial alignment** (LDDMM, adapted from STalign) + KNN reassignment — handles adjacent-section morphological discrepancies.
5. **Batch-biased SVF removal** — removes features that are spatially variable due to batch, before feeding into CVAE.

---

### Method Overview

SpatialMETA is a four-module pipeline:

#### Module 1: Alignment
Adjacent ST and SM sections are aligned via a diffeomorphic transformation (rotation, scaling, non-linear deformation) optimized by gradient descent. The tissue boundary (AlphaShape concave hull) of SM spots is matched to the ST histology image outline. Implemented via a modified STalign (LDDMM).

#### Module 2: Reassignment
SM data is down-sampled to match ST spatial resolution: each ST spot collects the average of its K=5 nearest SM neighbors (within a distance threshold of 1.5× minimum inter-spot distance).

#### Module 3: CVAE Integration
Core model is `ConditionalVAESTSM`, a CVAE with:
- **Two batch-invariant encoders** (SAE stacks): separate encoders for ST and SM, no batch information.
- **Joint latent space**: encoder outputs concatenated → single linear layers produce joint μ and σ² → z ~ N(μ, σ²).
- **Single-modal means**: additional shared linear layer outputs μ_st and μ_sm for interpretability.
- **Two shared decoders**: ST decoder and SM decoder, each called twice — once with z_joint, once with μ_st/μ_sm. This shared decoder architecture constrains single-modal embeddings to stay close to the joint embedding.
- **Modality-specific outputs**: ST decoder → ZINB parameters (μ, θ, gate); SM decoder → Gaussian parameters (μ, σ²).
- **Batch conditioning** via one-hot batch embeddings concatenated to z before decoding.
- **MMD loss** on q_mu between batches for horizontal integration.

#### Module 4: Downstream Analysis
- Leiden clustering on UMAP of latent embedding
- Marker gene/metabolite identification (rank_genes_groups / Wilcoxon)
- Metabolite annotation via HMDB m/z matching (±5 ppm tolerance)
- Pathway enrichment (hypergeometric test)
- Modality contribution per spot (angular similarity)
- Spatial network analysis, interactive ROI/TOI visualization (Plotly Dash)

---

### Evaluation

**Datasets**: Human clear cell renal cell carcinoma (ccRCC: 5 IM2 samples, 10X Visium + DESI/MALDI), glioblastoma (GBM: 248_T, Cancer Cell 2022), mouse brain (m3_FMP, Nat. Biotechnol. 2023).

**Benchmark metrics** (vertical integration):
- Reconstruction accuracy: mean PCC and Cosine Similarity between original and reconstructed data
- Continuity score: (1-CHAOS) + (1-PAS) from SDMBench (*Nature Methods*, 2024)
- Marker score: Moran's I + (1-Geary's C) + Specificity + Logistic + MI
- Biology conservation: ARI + NMI + Cell type ASW + Isolated label silhouette + cLISI (scIB, *Nature Methods*, 2022)

**Benchmark metrics** (horizontal integration, added):
- Batch correction: Batch ASW + iLISI + PCR batch (scIB)
- Cross-modality + cross-sample scores combined for overall

**Comparative results**:
- SpatialMETA achieves highest overall vertical integration score across 11 samples (ccRCC, GBM, mouse brain)
- Superior PCC and CS reconstruction vs totalVI (*Nat. Methods* 2021) and spaMultiVAE (*Nat. Methods* 2024)
- Generates coherent spatial clusters (low CHAOS/PAS) comparable to MISO (*Nat. Methods* 2025) and SeuratV5_BNN (*Nat. Biotechnol.* 2024)
- MISO_3m (with histology) achieves best biology conservation — SpatialMETA without histology is close
- For horizontal integration: SpatialMETA achieves highest overall score across 5 ccRCC samples, balancing batch correction and biological conservation (scPoli has good vertical but poor batch correction; Seurat CCA/RPCA has poor vertical but good batch correction)

**Biological validation**:
- Identified Imm_4 sub-cluster in ccRCC Y7_T with upregulated lipid metabolism (CYP2J2, ACSM2A transcripts; Phosphatidylglycerol, PA(24:0/24:1(15Z)) metabolites)
- Pathway enrichment confirms lipid metabolism both transcriptionally (GO analysis) and metabolically (HMDB annotation)
- CYP2J2 is a known diagnostic biomarker for immune infiltration in RCC (consistent with literature)
- Network analysis confirms endothelial clusters co-localize with malignant clusters across IM2 samples (consistent with original Nat. Genet. 2024 study)

**Computational efficiency**:
- Memory <2GB, runtime <100s for typical datasets (~2000 spots); approximately linear scaling to 100K spots (benchmarked by simulation)

---

### Reproducibility

**Rating**: 3/5

**Justification**: Code is publicly available with tutorials and documentation. Data is deposited in Zenodo (ccRCC), Dryad (GBM), and Mendeley (mouse brain). However, exact benchmark reproduction requires downloading large pre-processed datasets, multiple comparison methods (scVI, scANVI, totalVI, scPoli, Seurat v5, etc.) with specific version pinning, and running compute-intensive benchmarks. The benchmark scripts are available but require significant setup.

**Practical notes**:
- Python package installable via `pip install spatialMETA` (setup.py)
- 7 tutorial notebooks with step-by-step workflows
- Key dependency: PyTorch (GPU recommended), scanpy, anndata, pyimzml (for imzML loading), Squidpy (for Moran's I), Plotly Dash (for interactive analysis)
- AlignmentModule requires STalign (included in `external/stalign/`)
- SM data must be in imzML format OR CSV format with x/y coordinates
- SM normalization is crucial: MaxAbsScaler without normalization leads to poor integration (ablation shown in Supp. Fig. 4)

**Common pitfalls**:
- SM and ST sections with large angular misalignment (>90°) require manual pre-rotation before automated alignment
- Although `n_epochs_kl_warmup` defaults to 400, `fit_core()` caps it with `min(max_epoch, n_epochs_kl_warmup)`; at the default 35 epochs the KL weight ramps to its target over those 35 epochs.
- Mode 'multi' is not automatically selected when batch_keys is set — must pass `mode='multi'` explicitly
- MoE routing parameters (self.v, self.to_k) are defined but unused — will not cause errors but are wasted compute

**Strengths**:
- All-in-one framework: alignment → reassignment → integration → analysis
- Modality contribution scores provide unique interpretability
- Supports SM-only horizontal integration as a bonus

**Weaknesses**:
- Designed for low-resolution ST (10x Visium); single-cell resolution ST requires separate cell segmentation
- Currently limited to two modalities (ST + SM); cannot easily extend to 3+
- Alignment module requires similar tissue morphology; works poorly for highly distorted adjacent sections
- No spatial graph/GNN component — spatial neighbors used only for SVF identification, not in the latent space

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
