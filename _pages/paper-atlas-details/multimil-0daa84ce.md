---
layout: default
permalink: /paper-atlas/multimil-0daa84ce/
title: "multimil"
nav: false
wide: true
description: "论文中的 MultiMIL 是“多模态 cVAE + 多实例学习（MIL）”的组合：先用模态特异编码器和 Product-of-Experts（PoE）把每个细胞的 RNA/ADT/ATAC 整合为联合表示，再把同一患者的细胞当作一个 bag，用门控注意力加权成患者表示，最后预测疾病分类、连续表型或有序阶段。高注意力细胞被用作疾病相关细胞状态的候选。 本工作区的代码版本是 0.3.1，但它只包含独立 MIL 预测模块：输入 ."
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
      <span>bioRxiv · 2024</span>
    </div>
    <h1>multimil</h1>
    <p>Multimodal weakly supervised learning to identify disease-specific changes in single-cell atlases</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1101/2024.07.29.605625" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for multimil">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/theislab/multimil" target="_blank" rel="noopener noreferrer" aria-label="Open code for multimil">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MultiMIL 中文方法解读

### 核心结论

论文中的 MultiMIL 是“多模态 cVAE + 多实例学习（MIL）”的组合：先用模态特异编码器和 Product-of-Experts（PoE）把每个细胞的 RNA/ADT/ATAC 整合为联合表示，再把同一患者的细胞当作一个 bag，用门控注意力加权成患者表示，最后预测疾病分类、连续表型或有序阶段。高注意力细胞被用作疾病相关细胞状态的候选。

论文前半段的 PoE-VAE 整合代码不在当前 `src/multimil/`。因此 MIL 部分可以直接代码核验，端到端 cVAE+MIL 只能按论文解释，不能声称当前快照完整实现论文模型。

### 证据与版本

- 论文：bioRxiv DOI `10.1101/2024.07.29.605625`，本地取回的是 2024-07-29 v1，50 页 PDF，主文、Methods 和 Supplementary Figures 1–10 在同一文件。
- 包源码：`pyproject.toml` 版本 `0.3.1`，来源声明为 `https://github.com/theislab/multimil`。

### 1. 论文中的第一阶段：每个细胞的多模态联合表示

对一个细胞的 $m$ 个模态 $x_1,\ldots,x_m$，每个编码器产生高斯后验参数 $(\mu_i,\sigma_i)$。若 $M_i$ 表示模态是否存在，PoE 联合后验为

$$
\sigma_{joint}=\left(\sigma_0^{-1}+\sum_iM_i\sigma_i^{-1}\right)^{-1},
$$

$$
\mu_{joint}=\left(\mu_0\sigma_0^{-1}+\sum_iM_i\mu_i\sigma_i^{-1}\right)\sigma_{joint},
$$

其中先验是标准正态。论文的 $\sigma$ 记号实际按方差/精度使用；理解时关键是“不确定性小的模态贡献更大，缺失模态贡献为零”。由重参数化得到 $z_{joint}$ 后，各模态解码器重建输入。

训练整合模块使用各模态重建损失、联合后验 KL，以及可选 MMD：MMD 可以对齐技术批次的 joint latent，也可以对齐不同模态的 marginal latent，以支持单模态 query 映射。论文允许先训练整合模块再训练 MIL，也允许端到端同时优化。

论文图 1/2 的整合实验因而不能由本地代码重跑。

### 2. MIL 的数据单位：患者是 bag，细胞是 instance

已有细胞嵌入记为 $z_i\in\mathbb R^h$。同一 `sample_key` 下的细胞组成一个 bag，bag 只有患者级标签，例如健康/疾病、COVID 严重程度、年龄或其他连续表型。模型不需要每个细胞的疾病标签，而是学习哪些细胞最有助于预测患者标签。

当前源码 `MILClassifier` 直接令 `z = x`，其中 `x` 来自 AnnData `.X`。它不是 VAE，也没有在该类中校正批次；所以使用独立 MIL 模块时，输入嵌入必须已经完成适当整合。把原始 count 矩阵直接放进 `.X` 并不会自动复现论文联合模型。

`setup_anndata()` 注册样本和预测目标。分类与有序标签必须是 categorical covariates，连续回归目标必须是 continuous covariates。构造器要求至少指定一种 classification/regression/ordinal regression。

### 3. 门控注意力怎样从细胞得到患者表示

论文与源码都支持普通 attention 和默认 gated attention。门控版本为

$$
s_i=w^T\left[\tanh(Vz_i)\odot\sigma(Uz_i)\right],
$$

$$
a_i=\frac{e^{s_i}}{\sum_{j\in bag}e^{s_j}},
\qquad
z_{bag}=\sum_{i\in bag}a_iz_i.
$$

从左到右看：$V$ 路径提取细胞内容，$U$ 的 sigmoid 路径作为门，逐元素筛选内容；线性权重 $w$ 变成一个分数；bag 内 softmax 把分数归一化；加权和得到患者表示。

当前 `Aggregator` 还有一个重要实现细节：softmax 后把注意力乘以

$$
\frac{n_{cells\ in\ current\ chunk}}{\texttt{sample\_batch\_size}}.
$$

所以保存的 `cell_attn` 不总是在整位患者范围内和为 1；它还受患者被切成多少个固定大小 chunk 影响。论文的公式是完整 bag softmax，而代码为了 mini-batch 训练按 `sample_batch_size=128` 切块。因而代码注意力更准确地说是“chunk 内相对权重，经大小缩放”，不能无条件当作跨患者可比的概率。

### 4. 数据加载为何决定模型语义

训练默认 `batch_size=256`、`sample_batch_size=128`，即一个训练 batch 可容纳两个患者 chunk。`GroupDataSplitter` 和 `GroupAnnDataLoader` 按 `sample_key` 组织细胞。教程要求先按 sample 排序；当前高层 API 没有在 `setup_anndata()` 自动排序或强制检查。

这不是普通格式细节。`MILClassifierTorch.inference()` 按每 128 行切分张量并把每段当作一个 bag。如果输入次序或 sampler 契约被破坏，不同患者可能被错误合并。构造器源码甚至保留一条待实现注释：“检查同一患者内 class 是否相同”，说明当前版本没有完整验证每个 sample 的标签一致性。

训练/验证必须按患者而非细胞划分，才能避免同一患者细胞同时进入两侧造成泄漏。论文的 benchmark 使用患者级 5-fold CV；当前 splitter 以 group 为单位，但复现时仍应检查实际 indices，而不能只凭类名断言无泄漏。

### 5. 预测头与损失

$z_{bag}$ 可同时进入多个任务头：

- 分类：每个目标一个多类线性/MLP 头，交叉熵；
- 连续回归：单输出头，MSE；
- 有序回归：仍以单输出 MSE 训练，评估时 round 后 clamp 到合法类别。

总损失是分类损失和回归类损失的加权和：

$$
\mathcal L=\lambda_{class}\mathcal L_{class}+\lambda_{reg}\mathcal L_{reg}.
$$

当前默认两个系数都是 1。`anneal_class_loss=True` 时会借用训练计划传入的 `kl_weight` 逐步放大分类损失；但 MIL-only 模块的 reconstruction loss 与 KL loss均返回零。高层 `train()` 仍配置 KL warm-up 和 `AdversarialTrainingPlan`，这是框架遗留/复用接口，不代表当前 MIL-only 模型含有 VAE KL 项或默认执行对抗训练。

默认训练参数包括 200 epochs、AdamW、学习率 $5\times10^{-4}$、weight decay $10^{-3}$、早停。若有回归任务，默认早停指标从 accuracy 改成 validation regression loss。

### 6. 输出和解释边界

`get_model_output()` 保存细胞注意力、bag 标识、细胞重复的预测以及 sample-level 真值/预测。工具函数可按每个 sample 选 top 10% 高注意力细胞。论文用这些细胞分析 COVID 阶段相关的单核细胞、树突细胞、浆母细胞、血小板，以及 HLCA 中 IPF 相关巨噬细胞和 KRT17+ 基底细胞。

注意力不是因果解释。高权重表示该细胞嵌入有助于当前模型在当前数据划分中预测标签；它可能捕捉细胞组成、技术批次、患者特异信号或相关生物状态。论文通过交叉验证、不同 embedding 和 top-cell 稳定性实验增加可信度，但不能证明被选细胞导致疾病。后续差异表达与富集还需患者级统计和独立验证。

### 7. 论文结果应怎样读

图 2 评估 paired/mosaic 多模态整合和 query 映射，这依赖论文完整 PoE-VAE；当前 MIL-only 快照不能复现。图 3 在 PBMC CITE-seq 上预测 COVID 阶段：论文报告回归设定准确率 75%、分类 72%，同时指出分类产生更稳定的 top-attention 细胞，因此建议解释注意力时默认分类。图 4 在 HLCA 健康/IPF 患者上展示高注意力巨噬细胞的 profibrotic signature 与候选基因。

旧工作区摘要声称 HLCA “100% accuracy、训练 52 epoch、M1 CPU 5 分钟”；这些像是教程单次运行输出，不是论文主结果的稳健概括，不能替代患者级交叉验证统计。

### 8. Paper-code 对应表

#### Exact / direct

- 论文 gated attention（Eq. 3/12）→ `nn/_base_components.py::Aggregator`。
- bag 加权和（Eq. 2）→ `Aggregator.forward()` 的 `torch.bmm`。
- 分类/回归/有序回归→`module/_mil_torch.py::_calculate_loss()`。
- sample-aware 加载→`dataloaders/` 与 `GroupDataSplitter`。
- 注意力与 bag 预测导出→`model/_mil.py::get_model_output()`。

#### Partial

- 论文 end-to-end MultiMIL：本地只保留 MIL prediction module，可接收预计算 embedding。
- query loading：本地可复制 MIL 模型权重到新 AnnData，但不是论文所述 PoE-VAE scArches 整合的完整实现。

#### Not found

- PoE-VAE 编码器/解码器、PoE、MMD、重建损失、端到端联合损失；
- 上游论文实验 commit；
- `multimil_reproducibility` 数据、脚本、权重和环境锁；
- 论文所有图表的本地可运行复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MultiMIL: Multimodal Weakly Supervised Learning for Disease-Specific Changes in Single-Cell Atlases

### Executive Summary

**Reproducibility Rating: 4/5**

**Version boundary**: This workspace contains package version 0.3.1, whose `src/multimil/` implements the MIL-only prediction module. The paper's PoE-VAE integration and end-to-end training module is not present, the upstream commit is not preserved, and the separate `multimil_reproducibility` repository is absent. Accordingly, full-paper reproducibility is lower than the original 4/5 label suggests.

MultiMIL introduces Multiple Instance Learning (MIL) to single-cell genomics, enabling sample-level disease prediction while identifying cell populations that drive disease signatures. The framework treats each biological sample as a "bag" of cells (instances) and uses attention-based aggregation to learn which cells are most informative for disease classification.

#### Strengths
- Clean, well-documented codebase following scvi-tools conventions
- Comprehensive tutorial notebook demonstrating end-to-end workflow
- Transfer learning capability via `load_query_data()` for applying models to new samples
- Multiple prediction tasks: classification, regression, ordinal regression
- Interpretable attention weights for biological discovery

#### Limitations
- Test coverage is minimal (only version check test)
- Reproducibility code in separate repository (theislab/multimil_reproducibility)
- Paper PDF not included; documentation relies on bioRxiv preprint
- Limited benchmarking against alternative methods in main repository

---

### Citation

Anastasia Litinetskaya, Maiia Shulman, Soroor Hediyeh-zadeh, Amir Ali Moinfar, Fabiola Curion, Artur Szalata, Alireza Omidi, Mohammad Lotfollahi, and Fabian J. Theis. 2024. "Multimodal Weakly Supervised Learning to Identify Disease-Specific Changes in Single-Cell Atlases." bioRxiv. https://doi.org/10.1101/2024.07.29.605625.

---

### Biological Problem and Motivation

#### The Challenge
Single-cell atlases contain millions of cells from hundreds of samples, but identifying disease-specific cellular changes remains challenging:

1. **Sample hierarchy ignored**: Traditional cell-level analyses lose the biological structure where cells belong to samples/patients
2. **Scalability limitations**: Existing methods struggle with atlas-scale datasets (100K-1M+ cells)
3. **Interpretability gap**: Current approaches provide limited insight into which cell populations drive disease

#### Why MIL is Biologically Appropriate

The MIL paradigm naturally aligns with single-cell data organization:

| MIL Concept | Biological Meaning |
|-------------|-------------------|
| Bag | Biological sample (patient, tissue biopsy) |
| Instance | Individual cell |
| Bag label | Sample-level diagnosis (healthy/disease) |
| Attention weight | Cell's importance for disease classification |

This framework respects biological sample boundaries while learning cell-level importance through attention mechanisms.

---

### Key Innovations

#### 1. Attention-Based Cell Importance Learning
MultiMIL uses gated attention to identify disease-relevant cells without explicit cell-level labels:

$$A_V = \tanh(x \cdot W_V + b_V) \quad \text{(content pathway)}$$
$$A_U = \sigma(x \cdot W_U + b_U) \quad \text{(gate pathway)}$$
$$\alpha = \text{softmax}(A_V \odot A_U \cdot w)$$

**Code Reference**: `src/multimil/nn/_base_components.py:120-134`

#### 2. Sample-Level Stratified Training
Custom data loaders ensure:
- Cells from the same sample stay together
- Balanced representation across disease classes
- No data leakage between training/validation

**Code Reference**: `src/multimil/dataloaders/_ann_dataloader.py:14-137`

#### 3. Multi-Task Prediction Framework
Simultaneous prediction of:
- Binary/multi-class classification (disease state)
- Continuous regression (age, severity scores)
- Ordinal regression (disease stages)

**Code Reference**: `src/multimil/module/_mil_torch.py:125-169`

---

### Validation Results

#### Tutorial-only HLCA snapshot (not a paper benchmark summary)

Based on tutorial notebook results:

| Metric | Value |
|--------|-------|
| Dataset size | 450,214 cells |
| Training samples | 80% (359,595 cells) |
| Query samples | 20% (90,619 cells) |
| Classification accuracy | 100% |
| Early stopping epoch | 52/200 |

These values were recorded from a tutorial run and must not be generalized as the paper's patient-level cross-validation result. The paper evaluates HLCA with patient-level five-fold CV and uses the case study primarily to analyze IPF-associated high-attention states.

#### Computational Efficiency

- Training time: ~5 minutes on CPU (M1 Mac) for 360K cells
- Memory efficient: Works with pre-computed embeddings (30 dimensions)
- Scalable: Processes samples independently through batch sampling

---

### Critical Code-Paper Mapping

#### Paper Claim 1: Gated Attention Mechanism

**Paper claim**: Uses gated attention for more expressive cell-level importance learning.

**Code implementation** (`_base_components.py:120-134`):
```python
self.attention_V = nn.Sequential(
    nn.Linear(n_input, self.attn_dim),
    nn.Tanh(),  # Content: what features matter
)
self.attention_U = nn.Sequential(
    nn.Linear(n_input, self.attn_dim),
    nn.Sigmoid(),  # Gate: whether to attend
)
self.attention_weights = nn.Linear(self.attn_dim, 1, bias=False)
```

**Verification**: MATCH - Code faithfully implements gated attention with tanh for content and sigmoid for gating.

#### Paper Claim 2: Sample-Preserving Data Splitting

**Paper claim**: Splits data at sample level to prevent data leakage.

**Code implementation** (`_data_splitting.py:10-82`):
```python
class GroupDataSplitter(DataSplitter):
    def __init__(self, adata_manager, group_column, ...):
        self.group_column = group_column  # Sample key
```

**Verification**: MATCH - Uses `GroupDataSplitter` which inherits from scvi-tools `DataSplitter` but operates on sample groups.

#### Paper Claim 3: Multi-Task Learning

**Paper claim**: Supports classification, regression, and ordinal regression simultaneously.

**Code implementation** (`_mil_torch.py:243-312`):
```python
# Classification loss
classification_loss += F.cross_entropy(predictions[i], classification[:, i].long())

# Ordinal regression loss
regression_loss += F.mse_loss(predictions[len(self.class_idx) + i].squeeze(-1), ordinal_regression[:, i])

# Standard regression loss
regression_loss += F.mse_loss(predictions[...].squeeze(-1), regression[:, i])
```

**Verification**: MATCH - All three task types implemented with appropriate loss functions.

---

### Identified Discrepancies and Hidden Tricks

#### 1. Attention Scaling (Undocumented)

**Code** (`_base_components.py:171-174`):
```python
if self.scale:
    self.A = self.A * self.A.shape[-1] / self.patient_batch_size
```

**Issue**: Attention weights are scaled by the ratio of actual cells to batch size. This compensates for variable sample sizes but is not clearly documented in the paper or code comments.

**Impact**: May affect reproducibility if users don't use default `sample_batch_size=128`.

#### 2. Sorted Data Requirement (Hidden Trick)

**Tutorial notebook instruction**:
```python
# For the training to work properly, we need to sort the data by samples.
idx = adata.obs[sample_key].sort_values().index
adata = adata[idx].copy()
```

**Issue**: Data MUST be sorted by sample key before training. This is mentioned only in the tutorial, not in the API documentation or `setup_anndata()`.

**Impact**: Users not following the tutorial may encounter silent failures or incorrect attention weights.

#### 3. KL Warmup Inherited but Unused

**Code** (`_mil.py:296-304`):
```python
n_epochs_kl_warmup = max(max_epochs // 3, 1)
update_dict = {
    "n_epochs_kl_warmup": n_epochs_kl_warmup,
    ...
}
```

**Issue**: KL warmup is configured but MultiMIL doesn't use a variational formulation. This is vestigial code from scvi-tools base classes.

**Impact**: Minimal - parameter is effectively ignored, but may confuse users.

#### 4. Adversarial Training Option (Unused)

**Code** (`_mil.py:223, 344`):
```python
adversarial_mixing: bool = False,
...
training_plan = AdversarialTrainingPlan(self.module, **plan_kwargs)
```

**Issue**: `AdversarialTrainingPlan` is used even when `adversarial_mixing=False`. The adversarial component is disabled by default but the infrastructure remains.

**Impact**: Potential for confusion; may want to use simpler `TrainingPlan` if adversarial mixing is not intended.

---

### Dependencies and Environment

#### Core Requirements
```
anndata<0.11
numpy<2.0
scanpy
scvi-tools<1.0.0
jax<0.6
pytorch
pytorch-lightning
```

#### Version Constraints
- Python >= 3.10
- scvi-tools < 1.0.0 (compatibility issues with newer versions)
- anndata < 0.11 (API changes in newer versions)

---

### Reproducibility Checklist

| Item | Status | Notes |
|------|--------|-------|
| Code matches paper equations | YES | Gated attention, loss functions verified |
| Default parameters documented | PARTIAL | Some defaults in docstrings, others only in code |
| Random seed handling | YES | Uses scvi.settings.seed |
| Tutorial notebook runnable | YES | Tested with provided data |
| Test suite comprehensive | NO | Only version check test |
| Paper figures reproducible | EXTERNAL | Requires separate multimil_reproducibility repo |

---

### Recommended Usage

```python
import multimil as mtm
import scanpy as sc

# 1. Load pre-integrated data (requires embeddings in .X)
adata = sc.read_h5ad("integrated_data.h5ad")

# 2. CRITICAL: Sort by sample key
adata = adata[adata.obs["sample"].sort_values().index].copy()

# 3. Setup AnnData
mtm.model.MILClassifier.setup_anndata(
    adata,
    categorical_covariate_keys=["disease", "sample"]
)

# 4. Initialize and train
model = mtm.model.MILClassifier(
    adata,
    sample_key="sample",
    classification=["disease"],
    class_loss_coef=0.1  # May need tuning
)
model.train(lr=1e-3)

# 5. Extract attention weights
model.get_model_output()
sc.pl.umap(adata, color="cell_attn")

# 6. Identify high-attention cells
mtm.utils.score_top_cells(adata, top_fraction=0.1)
```

---

### Summary

MultiMIL provides a principled approach to identifying disease-relevant cell populations in single-cell atlases using Multiple Instance Learning. The implementation is well-structured and integrates cleanly with the scvi-tools ecosystem. Key concerns for reproducibility include the undocumented data sorting requirement and limited test coverage. The method achieves excellent classification performance on the HLCA dataset and provides interpretable attention weights for biological discovery.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
