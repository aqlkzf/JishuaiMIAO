---
layout: default
permalink: /paper-atlas/multigrate-9eff4560/
title: "multigrate"
nav: false
description: "Multigrate 是一个面向多模态单细胞数据的条件变分自编码器（cVAE）。每种模态有独立编码器，将可用证据变成高斯后验；Product-of-Experts（PoE）按精度合并这些后验，得到同一个细胞的联合潜变量；各模态解码器再从联合潜变量重建 RNA、蛋白、染色质或代谢物。缺失模态不参与 PoE，但仍可由对应解码器预测，因此同一模型可以处理配对、mosaic、单模态 query 和缺失模态插补。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>multigrate</h1>
    <p>Integration and querying of multimodal single-cell data with PoE-VAE</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1101/2022.03.16.484643" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for multigrate">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/theislab/multigrate" target="_blank" rel="noopener noreferrer" aria-label="Open code for multigrate">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Multigrate 中文方法解读

### 一句话理解

Multigrate 是一个面向多模态单细胞数据的条件变分自编码器（cVAE）。每种模态有独立编码器，将可用证据变成高斯后验；Product-of-Experts（PoE）按精度合并这些后验，得到同一个细胞的联合潜变量；各模态解码器再从联合潜变量重建 RNA、蛋白、染色质或代谢物。缺失模态不参与 PoE，但仍可由对应解码器预测，因此同一模型可以处理配对、mosaic、单模态 query 和缺失模态插补。

### 证据与版本边界

`pyproject.toml` 标记包版本 `0.1.0`，源地址为 `https://github.com/theislab/multigrate`。因此代码行为可以直接核验，不能声称它恰好就是论文实验使用的提交。

### 1. 数据怎样进入模型

同一细胞最多有 $m$ 种模态 $x_1,\ldots,x_m$。源码 `organize_multimodal_anndatas()` 用“模态 × 数据集”的嵌套 AnnData 表组织 paired 或 mosaic 数据；不存在的模态用空块补齐。推理时，`MultiVAETorch.inference()` 按 `modality_lengths` 切开拼接矩阵，并以每一模态行和是否大于零构造存在掩码。

这个默认掩码规则有实际边界：如果一个真实测量的细胞在某模态所有输入特征恰好为零，代码会把该模态判为缺失。`inference()` 虽接受显式 `masks`，但高层数据加载路径是否传入它需要调用方保证。

类别与连续协变量可以嵌入并连接到编码器/解码器。批次、供体、技术等因素因此能作为条件，而 MMD 还可以用 `integrate_on` 指定的分组主动对齐分布。这两者不是同一件事：条件化让解码器知道技术环境，MMD 则惩罚组间潜空间差异。

### 2. 每个模态先得到一个高斯“专家意见”

第 $i$ 个编码器输出隐藏表示，再由独立线性头得到 $\mu_i$ 与 `logvar_i`，形成

$$
q_i(z\mid x_i)=\mathcal N(\mu_i,\sigma_i^2).
$$

当前源码默认每个编码器/解码器 2 层、隐藏宽度 128、latent 维度 16、dropout 0.2、LayerNorm 和 LeakyReLU；论文补充表 5 也给出 128→16 的结构。注意“论文实验配置”和“当前构造器默认值”并非完全同义，尤其补充表 1 的 paired integration 默认层数写为 1，而源码中 `n_layers_encoders=None` 会展开为每模态 2 层。可能是层数计数口径或版本漂移，不能强行抹平。

### 3. PoE 如何合并可用模态

若 $M_i\in\{0,1\}$ 表示模态 $i$ 是否存在，并加入标准正态先验专家，联合方差与均值为

$$
\sigma^2_{joint}=\left(1+\sum_iM_i\sigma_i^{-2}\right)^{-1},
$$

$$
\mu_{joint}=\sigma^2_{joint}\sum_iM_i\mu_i\sigma_i^{-2}.
$$

源码 `_product_of_experts()` 正好执行这组精度加权：先把 `logvar` 指数化成方差，用 mask 去掉缺失专家，精度求和时额外从 1 开始表示标准正态先验，再求联合均值与 `logvar_joint`。

直觉上，方差小的专家更确定，权重更大；缺失专家权重为零。一个简单例子：两个模态均值分别为 2 和 5，方差分别为 1 和 4，再加标准正态先验，联合精度为 $1+1+0.25=2.25$，联合均值约为 $(2+1.25)/2.25=1.44$。先验把结果向 0 拉回，而不是简单平均 3.5。

源码也支持 `mix="mixture"`。这里并不是一般高斯混合分布，而是把独立潜变量取平均，使结果仍为高斯：均值按可用模态平均，方差按平方权重求和。论文用 PoE 与此 MoE 变体比较，并最终选择 PoE 为默认。

### 4. 从联合潜变量重建或预测模态

重参数化采样

$$
z_{joint}=\mu_{joint}+\epsilon\sigma_{joint},\qquad\epsilon\sim\mathcal N(0,I)
$$

后，同一个 $z_{joint}$ 被复制给每个模态解码器。`generative()` 可拼接批次和其他协变量，然后分别产生 `rs`。`impute()` 把这些输出写入 `adata.obsm["imputed_modality_i"]`；`get_model_output()` 把联合表示写入 `X_multigrate`。

重建分布由每个模态的 `losses` 选择：

- `mse`：连续归一化特征；
- `nb`：以 size factor 缩放均值，并学习分组相关 dispersion；
- `zinb`：在 NB 外增加零膨胀头；
- `bce`：二元特征。

因此“预测缺失模态”不是单独训练一个翻译网络，而是只用已观测专家推断 $z_{joint}$，再调用缺失模态的解码器。预测质量依赖训练参考中是否存在连接这些模态的 paired/bridge 细胞。

### 5. 损失：重建、KL 与分布对齐

VAE 主体最小化可用模态的重建损失与联合后验对标准正态先验的 KL。当前源码默认系数是 `recon=1`、`kl=1e-6`、`integ=0`，每模态重建权重为 1；训练默认 200 epoch、AdamW、学习率 $5\times10^{-4}$、batch 256、weight decay $10^{-3}$，并默认用前 1/3 epoch 做 KL warm-up。这些是本地 `0.1.0` 快照默认值，不是所有论文 benchmark 的最终超参数。

MMD 用多尺度高斯核比较两组潜表示：

$$
\operatorname{MMD}(P,Q)=E[k(a,a')]+E[k(b,b')]-2E[k(a,b)].
$$

论文用它做两类对齐：不同技术批次之间的 joint latent 对齐，以及不同模态 marginal latent 对齐。源码以 `modality_alignment="MMD"`、`alignment_type` 和 `integrate_on` 控制；默认 `integ=0` 意味着仅选择 MMD 类型还不够，还需设置非零整合损失系数。源码额外实现 Jeffreys divergence，而论文讨论部分只把它作为未来方向；这是本地代码超出论文主方法的功能。

### 6. Query-to-reference 为什么能工作

论文使用 scArches 思路把 query 映射到已训练 reference，而不是将所有数据从头重整合。本地 `MultiVAE.load_query_data()` 提供该入口。概念上，reference 的生物状态空间与大部分网络参数保持稳定，query 通过新增协变量/可训练参数适配到同一 latent。

但复现时必须核对冻结集合。当前源码提供 `freeze=True`，具体哪些参数可训练由 `ArchesMixin` 和加载逻辑决定；不能只根据“scArches”名称假定与某个 scvi-tools 版本完全相同。本地依赖约束为 `scvi-tools<1.0.0`、`anndata<0.11`、`numpy<2.0`，这是重要的运行版本边界。

### 7. 论文实验支持什么

论文评估四类场景：paired CITE-seq/multiome integration、PoE 与 MoE 的 query mapping、CITE-seq 与 multiome 的 mosaic/trimodal reference 和 query、以及 Visium RNA 与 MALDI-MSI 代谢物的空间整合和缺失代谢物预测。

结果支持 Multigrate 能在这些数据上构造有竞争力的联合表示并进行 query/imputation，但不能概括为所有指标和数据集都第一。论文自己指出 PoE/MoE 差异依赖 query 场景；空间代谢应用只有配准后的特定切片与代谢特征，真实与预测空间图和相关性不等于跨组织泛化。

补充材料在同一 PDF 中，包含超参数搜索、默认架构、稳健性实验和 Supplementary Figures 1–6。

### 8. Paper-code 对应与已知漂移

已直接核验的核心对应包括：PoE/MoE 公式→`_product_of_experts()`/`_mixture_of_experts()`；模态存在掩码→`inference()`；解码与插补→`generative()`/`impute()`；MMD→`distributions/_mmd.py`；query mapping→`load_query_data()`；mosaic 数据组织→`organize_multimodal_anndatas()`。

仍需保留的版本/复现边界：

- 上游源码 commit 与论文实验 commit Not found；
- `multigrate_reproducibility` 不在工作区；
- 论文补充默认学习率 $10^{-3}$、KL $10^{-5}$ 等与当前 API 默认值不同；
- 当前源码加入 Jeffreys、更多损失/初始化选项，不能倒推为论文全部实验使用；
- 测试集 `tests/test_basic.py` 主要是基础 API smoke coverage，不能证明论文全部数值可复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Multigrate: Integration and querying of multimodal single-cell data with PoE-VAE

### Executive Summary

**Paper**: "Integration and querying of multimodal single-cell data with PoE-VAE"
**Authors**: Anastasia Litinetskaya, Maiia Schulman, Fabiola Curion, Artur Szalata, Alireza Omidi, Mohammad Lotfollahi, Fabian Theis
**Repository**: https://github.com/theislab/multigrate
**Version Reviewed**: 0.1.0
**Paper version**: bioRxiv, posted 15 February 2025, DOI 10.1101/2022.03.16.484643

**Version boundary**: The local source snapshot exposes package version 0.1.0 but does not preserve the upstream Git commit. The paper's separate `multigrate_reproducibility` repository is not stored here, so benchmark reproduction is not locally verified.

#### Reproducibility Rating: 4/5

| Criterion | Score | Notes |
|-----------|-------|-------|
| Code availability | 5/5 | Complete implementation with scvi-tools integration |
| Documentation | 4/5 | Good API docs, tutorials available in Colab |
| Data availability | 4/5 | Public datasets referenced, reproducibility repo exists |
| Equation-to-code correspondence | 4/5 | PoE formulation implemented correctly; minor differences in MMD scale |
| Test coverage | 2/5 | Only basic package test; no algorithmic tests |

---

### 1. Biological Problem and Motivation

#### 1.1 The Multimodal Integration Challenge

Modern single-cell technologies enable simultaneous measurement of multiple cellular modalities:
- **CITE-seq**: Gene expression + 134 surface proteins
- **Multiome (10x)**: Gene expression + chromatin accessibility (ATAC-seq)
- **Spatial multiomics**: Visium (spatial transcriptomics) + MALDI-MSI (metabolomics)

**Critical Challenge**: Efficiently integrating these heterogeneous datasets while:
1. Handling **mosaic scenarios** where different experiments measure different modality combinations
2. Enabling **query-to-reference mapping** for atlas construction
3. Preserving biological signal while removing technical batch effects

#### 1.2 Limitations of Existing Methods

| Method | Limitation |
|--------|------------|
| MOFA+ | Poor scalability; struggles with batch effects |
| Seurat WNN | kNN computational bottleneck with multiple modalities |
| totalVI | Cannot handle mosaic integration or unimodal queries |
| multiVI | Limited to RNA+ATAC; no flexible query mapping |

#### 1.3 Key Innovations

1. **Product-of-Experts (PoE) VAE**: Combines unimodal evidence with precision weighting
2. **Mosaic Integration**: Seamlessly handles missing modalities via binary mask $M_i$
3. **Unimodal Query Mapping**: Maps RNA-only data onto multimodal references
4. **scArches Transfer Learning**: Enables federated atlas construction

---

### 2. Method Overview

#### 2.1 Core Architecture

Multigrate uses a conditional Variational Autoencoder with Product-of-Experts fusion:

```
Input: x = [x_RNA, x_ATAC, x_ADT]
         ↓
   Modality Encoders: E_i(x_i) → (μ_i, σ_i)
         ↓
   Product-of-Experts: PoE(μ_1...μ_m, σ_1...σ_m, M) → (μ_joint, σ_joint)
         ↓
   Reparameterization: z_joint ~ N(μ_joint, σ_joint²)
         ↓
   Modality Decoders: D_i(z_joint | batch) → x̂_i
```

#### 2.2 Product-of-Experts Formulation

For $m$ modalities with presence masks $M_i \in \{0,1\}$:

$$\mu_{joint} = \sigma_{joint}^2 \cdot \left( \sigma_0^{-2}\mu_0 + \sum_{i=1}^m M_i \mu_i \sigma_i^{-2} \right)$$

$$\sigma_{joint}^{-2} = \sigma_0^{-2} + \sum_{i=1}^m M_i \sigma_i^{-2}$$

Where $(\mu_0, \sigma_0) = (0, I)$ is the standard normal prior.

**Code Reference**: `src/multigrate/module/_multivae_torch.py:309-318`

#### 2.3 Loss Function

$$\mathcal{L} = \lambda_{recon} \mathcal{L}_{recon} + \lambda_{KL} \mathcal{L}_{KL} + \lambda_{integ} \mathcal{L}_{MMD}$$

| Component | Description | Default Weight |
|-----------|-------------|----------------|
| $\mathcal{L}_{recon}$ | Modality-specific reconstruction | 1.0 |
| $\mathcal{L}_{KL}$ | KL divergence to prior | 1e-6 |
| $\mathcal{L}_{MMD}$ | Maximum Mean Discrepancy | 0 (off by default) |

**Code Reference**: `src/multigrate/module/_multivae_torch.py:172-180`

---

### 3. Key Results

#### 3.1 Benchmark Performance

**NeurIPS 2021 Multimodal Dataset**:
- CITE-seq: 90,261 cells, 4 sites, 12 batches
- Multiome: 69,249 cells, 4 sites, 13 batches

Multigrate outperformed totalVI, multiVI, MOFA+, Seurat WNN on:
- Graph connectivity
- Batch ASW (silhouette width)
- Clustering metrics (ARI, NMI)

#### 3.2 Spatial Metabolomics Prediction

Novel application to Visium + MALDI-MSI mouse brain data:
- **Pearson correlation**: 0.943 on top 500 highly variable lipids
- **Spearman correlation**: 0.866

This enables metabolomic profiling of existing spatial transcriptomics datasets.

#### 3.3 Query-to-Reference Mapping

Successfully demonstrated:
- Unimodal RNA → multimodal (RNA+protein+ATAC) reference
- Cross-batch mapping with new experimental sites
- Mosaic integration of CITE-seq + multiome datasets

---

### 4. Code-Paper Correspondence Map

| Paper Claim | Code Implementation | File:Lines | Verified |
|-------------|---------------------|------------|----------|
| PoE distribution fusion | `_product_of_experts()` | `_multivae_torch.py:309-318` | Yes |
| Mixture-of-Experts (alternative) | `_mixture_of_experts()` | `_multivae_torch.py:320-329` | Yes |
| MMD batch alignment | `MMD.forward()` | `_mmd.py:72-113` | Yes |
| Multi-scale Gaussian kernel | `MMD.gaussian_kernel()` | `_mmd.py:20-70` | Yes |
| Negative Binomial for RNA | `_calc_recon_loss()` with `loss="nb"` | `_multivae_torch.py:656-664` | Yes |
| ZINB for sparse counts | `_calc_recon_loss()` with `loss="zinb"` | `_multivae_torch.py:665-678` | Yes |
| scArches transfer learning | `load_query_data()` | `_multivae.py:491-595` | Yes |
| Modality-specific encoders | `self.encoders = [MLP(...)]` | `_multivae_torch.py:192-205` | Yes |
| Conditional decoders | `self.decoders = [Decoder(...)]` | `_multivae_torch.py:210-224` | Yes |
| Covariate embeddings | `cat_covariate_embeddings` | `_multivae_torch.py:229` | Yes |

---

### 5. Critical Implementation Details

#### 5.1 Hidden Design Choices (Not in Paper)

1. **Default KL weight is very small** (`1e-6`): Reconstruction dominates training
   - Code: `_multivae_torch.py:173`
   - Impact: Less regularization, potentially better reconstruction but more overfitting risk

2. **Integration loss disabled by default** (`integ: 0`):
   - Code: `_multivae_torch.py:175`
   - Users must explicitly enable MMD via `loss_coefs={"integ": X}`

3. **Stratified sampling for balanced training**:
   - Code: `StratifiedSampler` in `_ann_dataloader.py:14-137`
   - Ensures each batch contains samples from all integration groups

4. **Softmax normalization for NB decoder**:
   - Code: `_base_components.py:128`
   - Outputs are normalized to sum to 1, then scaled by size factor

5. **Jeffreys divergence alternative to MMD**:
   - Code: `_jeffreys.py`
   - Not mentioned in paper; provides symmetric KL divergence option

#### 5.2 Discrepancies Between Paper and Code

| Aspect | Paper | Code | Impact |
|--------|-------|------|--------|
| Default encoder conditioning | Not specified | `condition_encoders=True` | Affects batch correction |
| MMD kernel scales | Not specified | 19 scales from 1e-6 to 1e6 | Determines sensitivity |
| Prior variance $\sigma_0$ | Explicit | Implicitly 1 (adds 1 to precision) | Minor numerical difference |
| KL warmup | "Linear warmup" | 1/3 of epochs | Training dynamics |

#### 5.3 Numerical Stability Tricks

1. **Logvar instead of variance**: `_bottleneck()` outputs log-variance for stability
   - Code: `_multivae_torch.py:296-300`

2. **Clipping in Jeffreys divergence**: `sigma.clamp(min=1e-6)`
   - Code: `_jeffreys.py:67-68`

3. **Skip MMD when single sample**: Returns 0 if `len(x) == 1 or len(y) == 1`
   - Code: `_mmd.py:94-95`

---

### 6. Reproducibility Assessment

#### 6.1 Strengths

- Complete implementation following scvi-tools conventions
- Tutorials with Google Colab integration
- Separate reproducibility repository with notebooks
- PyPI package available (`pip install multigrate`)

#### 6.2 Gaps

- **No unit tests for core algorithms**: Only package version test
- **Hyperparameter sensitivity not documented**: Default values may not generalize
- **Memory requirements not specified**: Large multimodal datasets may require tuning
- **No pre-trained models provided**: Must train from scratch

#### 6.3 Environment Requirements

```
Python >= 3.10
scvi-tools < 1.0.0
anndata < 0.11
numpy < 2.0
jax < 0.6
PyTorch (via scvi-tools)
```

---

### 7. Biological Validation Summary

#### 7.1 Validated Applications

1. **CITE-seq integration**: PBMCs with RNA + 134 proteins
2. **Multiome integration**: RNA + ATAC with proper batch correction
3. **Trimodal reference**: RNA + ATAC + protein atlas
4. **Spatial prediction**: Gene expression → metabolomics

#### 7.2 Biological Assumptions

1. **Shared latent space**: All modalities reflect same cellular state
2. **Conditional independence**: Given cell state, modalities are independent
3. **Batch additivity**: Technical effects can be modeled as additive embeddings

#### 7.3 Limitations

- Cannot model modality-specific biological variation
- Requires pre-aligned features across modalities
- Sensitive to normalization choices (especially CLR for proteins)

---

### 8. Usage Recommendations

#### 8.1 When to Use Multigrate

- Integrating multiple multimodal experiments with different modality combinations
- Building reference atlases for query mapping
- Cross-modal imputation (e.g., predicting proteins from RNA)

#### 8.2 When to Consider Alternatives

- Single paired multimodal dataset: totalVI may be simpler
- Only RNA+ATAC: multiVI has more specific features
- Very large datasets (>1M cells): May need batch processing

#### 8.3 Recommended Hyperparameters

```python
# For paired CITE-seq integration
model = MultiVAE(
    adata,
    losses=["nb", "mse"],  # RNA, protein
    integrate_on="Modality",
    loss_coefs={"integ": 500},  # Enable MMD
    z_dim=16,
    dropout=0.2,
)
model.train(max_epochs=200, batch_size=256, lr=5e-4)
```

---

### References

1. Litinetskaya et al. (2022). "Integration and querying of multimodal single-cell data with PoE-VAE." bioRxiv.
2. Lopez et al. (2018). "Deep generative modeling for single-cell transcriptomics." Nature Methods.
3. Gayoso et al. (2021). "Joint probabilistic modeling of single-cell multi-omic data with totalVI." Nature Methods.
4. Gretton et al. (2012). "A Kernel Two-Sample Test." JMLR.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
