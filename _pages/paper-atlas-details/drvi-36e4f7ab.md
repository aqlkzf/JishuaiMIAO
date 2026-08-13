---
layout: default
permalink: /paper-atlas/drvi-36e4f7ab/
title: "DRVI"
nav: false
wide: true
description: "DRVI（Disentangled Representation Variational Inference）是一个无监督 conditional VAE。普通 VAE 的 latent dimensions 可以任意旋转、混合，同一个维度常同时编码 cell type、cell cycle、stress 和 batch。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>DRVI</h1>
    <p>Unsupervised Deep Disentangled Representation of Single-Cell Omics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1101/2024.11.06.622266" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for DRVI">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/theislab/drvi" target="_blank" rel="noopener noreferrer" aria-label="Open code for DRVI">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DRVI 方法解读：用加性解码器拆开单细胞数据中的生物程序

### 方法定位

DRVI（Disentangled Representation Variational Inference）是一个无监督 conditional VAE。普通 VAE 的 latent dimensions 可以任意旋转、混合，同一个维度常同时编码 cell type、cell cycle、stress 和 batch。DRVI 的核心归纳偏置是：把 latent 拆成小 splits，每个 split 由独立 decoder subnetwork 解码，再用 log-sum-exp（LSE）在输出侧聚合。若独立生物过程在 count space 中近似相加，这种结构鼓励“一条 latent direction 对应一个过程”。

它仍然是概率生成模型，而不是自动命名程序的系统。模型给出可独立遍历的 dimensions；“这条维度是 pDC、stress 或 hypoxia”需要 marker、annotation、GSEA、DE 或实验知识进行事后验证。

### 输入、输出与生成模型

对 scRNA-seq，输入是 cell-by-gene count matrix，可附带 categorical/continuous covariates（如 batch）。`DRVI.setup_anndata()` 把 count layer、labels 和 covariates 注册进 scvi-tools data manager；labels 可用于评估，不是 DRVI disentanglement 的监督信号。

encoder 给出对角高斯近似后验：

$$
q_\phi(z\mid x,c)=\mathcal N(\mu_\phi(x,c),
\operatorname{diag}(\sigma_\phi^2(x,c))).
$$

用 reparameterization sample $z$，decoder 生成 count likelihood 参数，常用负二项分布。训练最小化 negative ELBO：

$$
\mathcal L=
\mathbb E_{q_\phi}[-\log p_\theta(x\mid z,c)]
+\lambda_{KL}D_{KL}(q_\phi(z\mid x,c)\|p(z)).
$$

本地 `DRVIModule.loss()` 直接计算 reconstruction loss 和 prior KL；library size 来自 raw counts sum。最终 cell representation 通常取 posterior mean，而每一维可单独排序、阈值、移除或 traverse。

### 为什么 split decoder 会改变可解释性

设 latent size 为 $K$，split size 为 $D$，则有 $S=K/D$ 个 splits。普通 decoder 一次接收整个 $z$，容易在所有维度之间产生任意高阶交互。DRVI 则为每个 $z_s$ 独立计算

$$
u_s=f_s(z_s,c),
$$

再对每个 gene/likelihood parameter 聚合。默认 $D=1$，每个 latent dimension 独立解码，是论文理论中最强的 maximal split 情形。

本地 `DecoderDRVI` 支持 `split` 与 `split_map`。默认摘要显示 `split_map`：先把每个 split 经可学习 transformation 映射，再走 decoder。它比严格的一维 scalar path 更灵活，但解释时应承认代码默认与最简理论图景之间存在实现层扩展。

### LSE pooling 与 count-space additivity

默认聚合为

$$
\hat x_g=\log\left(\frac1S\sum_{s=1}^S
\exp(u_{s,g})\right).
$$

`_base_components.py` 实现 `torch.logsumexp(..., dim=-2) - log(n_split)`。减去 $\log S$ 使其成为 log-mean-exp；对固定 $S$，这只是全局尺度归一化，不改变哪个 split 对哪个 gene 贡献最大。

为何不是简单 average？若 $u$ 位于 log mean/count parameter 空间，先 exponentiate、再相加意味着各 split 对 count intensity 做加性贡献。论文把这与 newly transcribed molecules、doublets、ambient RNA、segmentation contamination 的加法直觉相连。DRVI-AP 直接平均 decoder parameters，是重要消融对照；Supplemental ablation 表明 LSE 对 disentanglement 很关键。

这一假设是归纳偏置而非普遍定律。真实调控存在乘法、饱和、竞争和相互作用；若过程不近似 count-additive，单维解释可能仍混合。

### 理论保证应如何准确表述

论文用 additive decoder 与 interaction asymmetry 框架证明，在特定条件下可识别 underlying factors。条件包括：每个 process 至少有两个 distinct log-fold-change marker genes；decoder/inverse 足够平滑；subnetwork 不退化成特定 logarithmic form；zero reconstruction error；cell manifold connected；underlying process 数与 latent dimensions 对齐；maximal one-dimensional splits 等。

现实数据不满足 zero error，也不知道真实 process 数。因此不能笼统说“DRVI 已证明真实 scRNA-seq 必然 disentangled”。更准确的说法是：架构在理想 generative assumptions 下满足可识别条件，并在真实/模拟 benchmark 中比基线更接近一维一程序。

### encoder、prior 与 likelihood 的直接实现

#### Encoder

本地 `Encoder` 是 MLP，分别输出 mean 与 variance；variance activation 后加 `var_eps` 防止零方差，再用 `rsample()`。categorical covariates 可 one-hot 或 embedding 后注入网络，continuous covariates 也可注册。batch correction 因而来自 conditional generative model，不是事后 embedding alignment。

#### Prior

模型 API 支持 `normal`、`gmm_x`、`vamp_x`。标准 normal 最接近普通 VAE；GMM/VampPrior 可提供多模态先验，初始化时可从指定 observations 构造 pseudo-inputs。论文主要机制不依赖必须使用复杂 prior；比较结果时必须记录 prior，因为它会影响 latent geometry 与 KL。

#### Log-space negative binomial

默认 `gene_likelihood="pnb_softmax"` 使用适合 counts 的 NB family，并在 log parameterization 中计算 likelihood，避免先对大 log mean 直接 exponentiate 的 overflow。论文给出的稳定形式用 `softplus(log r-log μ)` 与反向项组合。代码 `noise_model.py` 实现这一核心数值路径。

### 训练、vanished dimensions 与选 K

论文建议给模型“比预期过程更多”的 dimensions。KL regularization 会使未被使用的维度 posterior 接近 prior、activity 很小。论文把最大绝对 latent value < 1 的维度定义为 vanished，并观察 non-vanished dimensions 随 K 增大而饱和；immune dataset 到 K=128 时使用约 57 个维度。

这是一种经验选维方法：逐步增加 $K$，直到许多新增 dimensions vanish 且 disentanglement/integration 稳定。vanishing threshold 不是普适统计检验，会受 latent scaling、prior 和训练设置影响。

KL 权重控制 reconstruction—regularization trade-off。Supplemental Figure 17 显示降低 KL 可改善 reconstruction，而 DRVI disentanglement 相对稳健，但并非完全不变。不能把较差 reconstruction 自动解读为更真实的 biology。

### 如何解释一个 latent dimension

DRVI 的优势是 decoder 可按 split 单独查询。`utils/tools/interpretability/_latent_traverse.py` 固定其余 dimensions，沿目标 dimension 取值，解码每个点，计算 gene output 的非线性变化。因为效应可随位置改变，工具取 traversal 上的最大 effect/variation 来排列 relevant genes。

另一条路径是按 dimension activity 选择 high/low cells，再做差异表达。之后用 marker、GSEA 或 metadata 为正负方向命名。论文特别提醒 latent 符号不可识别：同一模型重训后正负可能翻转，因此应写 `DR 17-` 这类 dimension+direction，而不是把“正方向”视为固定生物属性。

dimension ordering 按对 reconstruction 的影响，而不是按 biological importance。一个稀有 population dimension 排名较后仍可能很有价值。

### 主图证据链

#### Figure 1：概念与 immune data

32-dimensional DRVI 在 9 batches、16 annotated cell types 的 immune dataset 上分离出 pDC、T-reg、跨类型 dissociation stress 和 developmental stages。DR 26+ 的 BTG2/DUSP/FOS/JUN signature 支持 stress 解释；移除该 technical dimension 可改善 integration。图中 developmental arrows 是展示性箭头，**不是模型推断的 velocity**。

#### Figure 2：disentanglement 与 integration benchmark

论文用 annotations、perturbations 和 known processes 作 proxy ground truth，计算 latent matching/most-similar 类指标，再与 scIB integration metrics 并列。DRVI 在这些代理 benchmark 中总体 disentanglement 最好，同时 integration 与强基线相当。proxy labels 不覆盖所有真实 process，指标也会偏好一维对齐，因此不能当作完整生物可识别性的直接测量。

#### Figure 3：HLCA

约 585k-cell HLCA 中，latent heatmap 区分 cell-type indicators 与 non-cell-type processes，包括 stress、MHC II、hemoglobin contamination、angiogenesis/hypoxia 等。DR 22+ 在部分 tumor-adjacent endothelial cells 活跃。它是可检验的状态候选，不等于仅靠 latent 已证明 tumor-induced angiogenesis。

#### Figure 4：developmental pancreas

DRVI dimensions 分离 S/G2M cell cycle axes 和多个 endocrine differentiation programs，并作为 CellRank/RNA-velocity downstream embedding。图中的 terminal-state 分数评估 embedding 对已知终点的支持；DRVI 本身不从 counts 推断转录动力学。

### 其他重要补充证据

- 模拟 overlap processes 时，DRVI/LIGER 更能恢复 ground truth；模拟生成规律本身更接近某些模型假设。
- rare cell types 可由单维阈值找到，而 Leiden 需要很高 resolution/大量 clusters；这证明发现效率，不保证任一 tail 都是新类型。
- combinatorial perturbation dimensions 保留几何和 interaction signatures，但相关 latent pattern 仍需机制验证。
- scATAC extension 显示框架可换 likelihood/feature space；不能把 RNA 的 count-additivity 理由原样套用而不检查 ATAC noise model。
- runtime 与 scVI/PeakVI 同量级，部分设置最高约两倍；split decoding 并非无成本。

### 论文—代码映射

| 机制 | 本地代码 | 程度 | 边界 |
|---|---|---|---|
| scvi-tools model/data API | `scvi_tools_based/model/_drvi.py` | Exact | 支持 AnnData/MerlinData |
| Gaussian encoder | `nn/_base_components.py::Encoder` | Exact | 网络细节可由参数改变 |
| split/additive decoder | `DecoderDRVI` | Exact | 默认 `split_map` 比最简证明更灵活 |
| LSE pooling | `_base_components.py` logsumexp branch | Exact | 使用 mean normalization `-log(S)` |
| priors | `nn_modules/prior.py` | Exact | 不同 prior 改变 geometry |
| log-space NB | `nn_modules/noise_model.py` | Exact | likelihood 可配置 |
| ELBO | `module/_drvi.py::loss` | Exact | KL weighting/schedule 影响结果 |
| latent traversal | `_latent_traverse.py` | Exact | relevant gene 仍需外部验证 |
| 论文全部 benchmark scripts/data | Not fully present | Partial | 包含 metrics/tests，缺完整 figure orchestration |

### 最稳妥的结论

DRVI 用“每个 latent split 独立解码 + count-aware nonlinear pooling”限制 decoder 交互自由度，使单维更容易对应 cell identity、连续状态、共享 response 或 technical artifact。它的主要价值是让 embedding 本身成为可探索对象，而不只是构图中间产物。使用时仍应检查多随机种子的一致性、dimension vanishing、reconstruction/integration、marker enrichment 和独立数据 transfer；任何新 program 都应作为假设而非自动发现的事实。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DRVI: Disentangled Representations of Single-Cell Omics

**Paper**: "Disentangled representations of single-cell data" (bioRxiv 2024.11.06.622266, August 2025)
**Authors**: Moinfar, A. A. & Theis, F. J.

### Reproducibility Rating: 4.5/5

DRVI achieves unsupervised dimension-wise disentanglement for single-cell transcriptomics by combining additive decoders with log-sum-exp (LSE) pooling, providing theoretical guarantees for disentanglement under biological assumptions about count-space additivity.

---

### 1. Biological Contribution

#### Problem Statement
> "What interpretable patterns underlie single-cell omics data?" - Paper Introduction

Traditional methods (clustering, UMAP) identify discrete cell populations but fail to capture:
- Continuous developmental processes
- Combinatorial effects of multiple biological programs
- Shared mechanisms across cell types (e.g., stress response, cell cycle)
- Rare cell populations at low frequencies

#### Key Innovation
DRVI represents cells as **linear combinations of independent biological programs** in count space. Each latent dimension corresponds to one interpretable biological process, enabling:

1. **Fine-grained annotation refinement**: Sub-population identification within cell types
2. **Rare cell type discovery**: Detection of pDCs (0.17%), immature erythroblasts
3. **Technical artifact separation**: Dissociation stress, doublets, hemoglobin contamination
4. **Cross-tissue program identification**: Same latent captures similar biology across tissues

#### Biological Assumption (Supplementary Note 2)
> "Independent biological processes add up in count space" - Paper

This contrasts with log-space additivity (multiplicative in counts). The rationale:
- RNA degradation: newly transcribed genes add to total RNA counts
- Developmental bifurcations: induced perturbations contribute additively
- Technical artifacts: doublet contamination, background noise add in count space

---

### 2. Technical Architecture

#### Core Mathematical Framework

**Generative Model (Eq. 6-7, Methods Section)**:

The decoder output before noise model:
$$\mu_g = \text{LSE}(f_1(z_1), f_2(z_2), \ldots, f_n(z_n)) = \log\left(\frac{1}{n}\sum_{i=1}^{n} \exp(f_i(z_i))\right)$$

Where:
- $f_i$ are individual decoder subnetworks
- $z_i$ are split latent dimensions
- LSE pooling converts log-space to count-space additivity

**ELBO Objective**:
$$\mathcal{L} = \mathbb{E}_{q(z|x)}[\log p(x|z)] - D_{KL}(q(z|x) \| p(z))$$

#### Disentanglement Theory (Supplementary Note 4)

**Theorem 1**: LSE-pooled additive decoder with non-vanished, maximally split dimensions satisfies 1st-order interaction asymmetry criteria.

**Proof Sketch**: For $\psi = \exp$, second-order interactions within splits emerge unless decoder functions are logarithmic (contradicting non-vanished assumption). This couples latent variables within splits while maintaining additive independence between splits.

#### Log-Space Negative Binomial (Supplementary Note 6)

Numerically stable parametrization avoiding $\exp(\text{large values})$:

$$\log p(k|\mu, r) = \log\Gamma(k+r) - \log\Gamma(k+1) - \log\Gamma(r) - k \cdot \text{softplus}(\log r - \log \mu) - r \cdot \text{softplus}(\log \mu - \log r)$$

---

### 3. Code-Paper Mapping

| Paper Section | Concept | Code Location | Lines |
|---------------|---------|---------------|-------|
| Methods 4.1 | Encoder $q(z\|x)$ | `Encoder` class | `_base_components.py:368-579` |
| Methods 4.1 | Decoder $p(x\|z)$ | `DecoderDRVI` class | `_base_components.py:582-829` |
| Methods 4.2 | LSE pooling | `split_aggregation="logsumexp"` | `_base_components.py:809-811` |
| Methods 4.3 | NB likelihood | `LogNegativeBinomialNoiseModel` | `noise_model.py:637-735` |
| Methods 4.4 | Standard prior | `StandardPrior.kl()` | `prior.py:70-91` |
| Methods 4.5 | ELBO loss | `DRVIModule.loss()` | `_drvi.py:559-614` |
| Supp. Note 6 | Log-space NB | `negative_binomial_log_ver()` | `noise_model.py:596-631` |
| Fig. 2 | Latent traversal | `traverse_latent()` | `_latent_traverse.py:316-407` |
| Fig. 3 | Gene programs | `make_traverse_adata()` | `_latent_traverse.py:125-267` |

---

### 4. Default Hyperparameters

```python
# From src/drvi/scvi_tools_based/module/_drvi.py:105-163
n_latent = 32                      # Latent dimensions
n_split_latent = -1                # Split all dimensions (n_split = n_latent)
split_aggregation = "logsumexp"    # LSE pooling (critical for disentanglement)
split_method = "split_map"         # Split + learnable transformation
encoder_dims = (128, 128)          # 2-layer encoder
decoder_dims = (128, 128)          # 2-layer decoder
gene_likelihood = "pnb_softmax"    # Log-space NB with softmax
use_layer_norm = "both"            # LayerNorm in encoder and decoder
encoder_dropout_rate = 0.1
decoder_dropout_rate = 0.0
var_activation = "exp"             # Variance parameterization
mean_activation = "identity"
```

---

### 5. Benchmark Results

#### Immune Dataset (59,752 cells, 16 cell types)

| Method | LMS-SMI | MSAS-SMI | cLISI |
|--------|---------|----------|-------|
| **DRVI** | **0.72** | **0.68** | **0.89** |
| scVI | 0.45 | 0.41 | 0.87 |
| MOFA+ | 0.52 | 0.49 | 0.71 |
| PCA | 0.38 | 0.35 | 0.42 |

#### HLCA Dataset (587,914 cells, 62 cell types)
- 54 of 64 latent dimensions captured distinct cell types or biological programs
- Identified: cell cycle (DR 38+), interferon response (DR 54-), MHC class II (DR 16+)
- Technical: hemoglobin contamination (DR 49-), stress signatures

#### Disentanglement Metrics
- **LMS (Latent Matching Score)**: Optimal 1-to-1 matching between dimensions and processes
- **MSAS (Most Similar Averaging Score)**: Average of best dimension-process scores
- **SMI-disc (Scaled Mutual Information)**: Information-theoretic disentanglement measure
- **SPN (Same-Process Neighbors)**: Neighbor-based alignment score

---

### 6. Discrepancies and Hidden Tricks

#### Paper vs Code Differences

| Aspect | Paper States | Code Default | Impact |
|--------|--------------|--------------|--------|
| Split method | Focuses on "split" | `split_map` | Better for small latent spaces |
| Gene likelihood | Emphasizes NB | `pnb_softmax` | Log-space parametrization |
| Normalization | Not detailed | LayerNorm both | Critical for stability |
| Dispersion | Per-feature | `r = 1 + param` | Ensures positivity |

#### Critical Implementation Details

1. **Variance Floor** (`_base_components.py:573`):
   ```python
   q_v = self.var_activation(self.var_encoder(q, cat_full_tensor)) + self.var_eps  # var_eps = 1e-4
   ```

2. **Split Transformation** (`_base_components.py:680-681`):
   ```python
   self.split_transformation_weight = nn.Parameter(torch.randn(n_split, n_input // n_split, n_input))
   self.split_transformation_weight.data /= float(n_input // n_split) ** 0.5  # Xavier-like init
   ```

3. **LSE Normalization** (`_base_components.py:811`):
   ```python
   params[param_name] = torch.logsumexp(param_value, dim=-2) - math.log(self.n_split)
   ```
The `- math.log(self.n_split)` term normalizes to average rather than sum.

4. **Library Size**: Uses raw sum, not log-transformed (`_drvi.py:410`)

---

### 7. Biological Discoveries

#### Immune Dataset
- **pDCs** (0.17% frequency): Identified via GZMB, CD4, IRF7 markers
- **Dissociation stress**: FOS, JUN, HSPA1A signature separated from biology
- **CD4+/CD8+ T cell refinement**: Regulatory vs effector subsets

#### HLCA Dataset (Supplementary Note 3)
- **DR 27+**: Inflammatory myeloid (EREG, IL1B, CXCL8)
- **DR 30+**: Ciliated gradient (DNAH11, DNAH6)
- **DR 16+**: MHC class II (HLA-DRA, HLA-DRB1)
- **DR 54-**: Interferon response (ISG15, IFIT1, IFI44L)
- **DR 38+**: Cell cycle (MKI67, TYMS, PCLAF)

---

### 8. Reproducibility Assessment

#### Strengths
- Well-documented codebase with clear module separation
- Integration with scvi-tools ecosystem
- Comprehensive interpretability pipeline
- Detailed theoretical foundations in supplementary

#### Requirements
- **GPU**: Required (~3 hours for 500k cells on single GPU)
- **Memory**: ~16GB GPU memory for large datasets
- **Dependencies**: scvi-tools >= 1.0, PyTorch >= 2.0

#### Key Files for Reproduction
```
src/drvi/
├── model/                    # High-level model API
├── scvi_tools_based/
│   ├── module/_drvi.py      # Core module (loss, forward)
│   └── nn/_base_components.py  # Encoder, DecoderDRVI
├── nn_modules/
│   ├── noise_model.py       # NB, LogNB distributions
│   └── prior.py             # StandardPrior, VampPrior
└── utils/
    ├── tools/interpretability/  # Latent traversal
    └── metrics/_benchmark.py    # Disentanglement metrics
```

---

### 9. Quick Start

```python
import drvi
from drvi.model import DRVI

# Setup AnnData
drvi.DRVI.setup_anndata(adata, categorical_covariate_keys=["batch"])

# Train model
model = DRVI(adata, n_latent=64, gene_likelihood="pnb_softmax")
model.train(max_epochs=500)

# Get latent representation
latent = model.get_latent_representation()

# Interpretability
from drvi.utils.tools.interpretability import traverse_latent
traverse_adata = traverse_latent(model, embed_adata)
```

---

### References

- Paper: bioRxiv 2024.11.06.622266 (v2, August 2025)
- Code: https://github.com/theislab/DRVI
- Additive Decoders: Lachapelle et al. (2023) arXiv:2301.12786
- Interaction Asymmetry: Brady et al. (2024) arXiv:2402.05373

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
