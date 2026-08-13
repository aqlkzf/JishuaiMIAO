---
layout: default
permalink: /paper-atlas/causalged-8aeb9849/
title: "CausalGeD"
nav: false
description: "CausalGeD 的任务是：已知 scRNA-seq reference 中较完整的基因表达，预测空间转录组 spots 上未测或被遮蔽的基因。它先用双输入头 VAE 把“每个基因在所有 ST spots 上的表达向量”和“该基因在所有 single cells 上的表达向量”映射到同一潜空间，再给 ST latent 加噪；"
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
      <span>KDD 2025 · 2025</span>
    </div>
    <h1>CausalGeD</h1>
    <p>CausalGeD: Blending Causality and Diffusion for Spatial Gene Expression Generation</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2502.07751" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CausalGeD">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Rumi07/CausalGeD" target="_blank" rel="noopener noreferrer" aria-label="Open code for CausalGeD">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CausalGeD：用自回归因果遮罩约束空间基因表达的潜扩散生成

### 一句话理解

CausalGeD 的任务是：已知 scRNA-seq reference 中较完整的基因表达，预测空间转录组 spots 上未测或被遮蔽的基因。它先用双输入头 VAE 把“每个基因在所有 ST spots 上的表达向量”和“该基因在所有 single cells 上的表达向量”映射到同一潜空间，再给 ST latent 加噪；Causality-Aware Transformer（CAT）以 scRNA latent 为条件，在一种分组自回归 attention mask 下预测噪声，最后 reverse diffusion 与 VAE decoder 生成 ST expression。

这套方法把“causal”实现为生成顺序上的单向可见性：较早 AR groups 的干净 token 可以影响较晚 groups，反向信息被 mask。它没有从数据显式恢复一个带生物学方向和边类型的 GRN，因此更准确的名称是 causality-aware autoregressive dependency，而不是经干预识别的因果图。

### 1. 输入、预测单位与数据切分

论文记一个 ST 基因向量为 $x_{st}^i\in\mathbb R^p$，即基因 $i$ 在 $p$ 个 spots 上的表达；scRNA 基因向量 $x_{sc}^j\in\mathbb R^q$ 是基因 $j$ 在 $q$ 个 cells 上的表达。官方代码 `ConditionalDiffusionDataset` 也把 genes 作为 samples，因此训练/验证/测试按 gene 以 70%/20%/10% 切分（`main.py:103-112`）。

这点很关键：模型不是随机遮掉同一基因的部分 spots 后测试，而是用训练 genes 学到跨模态映射，再为 held-out genes 生成完整 spatial profile。若预处理阶段让同一 gene 的信息跨 split 泄漏，指标会虚高；官方代码把 split indices 写入 JSON，复现时必须保存。

主入口默认 ST/sc 输入为 `.h5ad`，数据路径硬编码到 `datasets/data/<document>/st|sc/`。README 指向 Zenodo 数据，但仓库自身没有打包全部 benchmark matrices。

### 2. 双头 VAE：两个不同长度的输入映射到同一 latent

VAE 为 ST 与 scRNA 设置两个输入 linear heads：

$$
h_{st}=W_{st}x_{st},\qquad h_{sc}=W_{sc}x_{sc},
$$

随后共享 encoder 输出 $\mu,\log\sigma^2$，用

$$
z=\mu+\sigma\odot\epsilon,qquad\epsilon\sim\mathcal N(0,I)
$$

采样。官方 `VAE` 在 `model/diff_train.py:116-178` 实现：`lin1`/`lin2` 处理 spot_num 与 cell_num，两者进入同一个 MLP encoder；decoder 只输出 ST spot dimension。主入口默认 hidden 1024、latent 256，并令 decoder 末端为 Sigmoid（`main.py:53-74,114-129`）。

论文常说 two-headed encoder；代码的精确含义是“两个输入投影 + 共享 posterior network”，不是两个完全独立 VAE。它也不是先单独预训练完整 VAE 再冻结：当前 `normal_train_diff()` 在 diffusion training 时联合优化 CAT 与 VAE encoder；默认 `decoder_train=0` 时 optimizer 不含 decoder parameters（`diff_train.py:224-232`）。

### 3. 潜扩散：模型学什么噪声

ST latent $z_0$ 经 cosine schedule 加噪：

$$
q(z_t\mid z_0)=\mathcal N(\sqrt{\bar\alpha_t}z_0,(1-\bar\alpha_t)I),
$$

$$
z_t=\sqrt{\bar\alpha_t}z_0+\sqrt{1-\bar\alpha_t}\epsilon.
$$

主入口默认 `diffusion_step=2000`，每个 batch 随机采样 timestep。ST latent 中的 nonzero/zero elements 又按不同 mask ratio 部分保留或加噪；默认 raw-space mask ratios 是 nonzero 0.2、zero 0.3（`main.py:55-64`; `diff_train.py:249-290`）。

loss 并非论文最简洁叙述中的单一 MSE。代码对 nonzero-masked elements 用 MSE，对 zero-masked elements 用 Huber loss 并加 penalty factor，然后乘 AR weight 的均值（`diff_train.py:27-49,295-310`）。这是一条重要 paper-code 边界：实现显式区分稀疏矩阵中零与非零位置。

### 4. 分组自回归：不是逐基因一个接一个

latent dimension $L$ 被随机分成若干连续 groups $\kappa_1,\ldots,\kappa_S$。`split_integer_exp_decay()` 先按 decay 分布采样 group 数，再从 latent positions 随机选 boundaries（`diff_train.py:52-63`）。主入口暴露 `--ar_step_decay` 默认 0.9；论文主要 ablation 讨论 0.8，二者并不一致。

早期 groups 还得到较高 loss weights：默认从 2.0 线性降到 1.0（`diff_train.py:66-87`）。因此所谓“earlier regulators influence later targets”在代码里包含两个机制：单向 attention visibility 与早期 token 较大训练权重。

但 group boundaries 是对 latent positions 的随机划分，tokens 在 forward 中还会随机 shuffle（`causalfusion/models.py:369-378`）。它并没有把已知 TF 排在 target gene 之前；“biological ordering”是论文的建模解释，而不是可审计的固定 gene order。

### 5. causal attention mask 怎样工作

token sequence 分为三段：

1. `cond`：scRNA latent 经 linear embedding 得到的 64 condition tokens；
2. `visible clean context`：除最后一个 AR group 外的 clean ST latent tokens；
3. `noisy sample tokens`：全部 noisy ST latent tokens。

`get_attn_mask()` 初始化为全部禁止，再设置：condition 对所有 query 可见；clean context 按 AR group 形成下三角可见；noisy group 只能看对应/更早 clean groups与自身 group（`model/diff_train.py:90-113`）。mask 在 attention 中转成 $-\infty$ additive bias（`causalfusion/models.py:162-170`）。

直观例子：若 groups 大小是 `[2,2,3]`，第三组的 noisy tokens 可以读取第一、二组的 clean context与第三组内部 noisy tokens，但第一组不能读取后两组 clean results。这样一次 transformer forward 并行预测全部噪声，同时保留 group-level autoregressive dependency。

这不是从 Granger test 构造 mask。图 1 的 Granger analysis 只用于证明某些 gene pairs 有方向统计关联；模型 mask 的结构来自随机 AR grouping。

### 6. 官方 CAT 实现

主入口实际实例化 `causalfusion.models.CausalFusion_L`，而不是 `model/diff_model.py` 中另一套 `DiT_diff`。`CausalFusion_L` 默认 hidden 1024、16 heads、64 condition tokens，depth 由 CLI 默认 4（`causalfusion/models.py:227-399,447-470`; `main.py:58`）。

forward 将 ST clean/noisy latent reshape 成 token sequence，随机统一打乱二者，删去最后 AR group 的 clean tokens，将 scRNA condition tokens放在开头，给 noisy tokens加 timestep embedding，随后通过带 mask 的 transformer blocks，最后只对 noisy token位置输出预测（`models.py:344-399`）。

仓库还保留 `model/diff_model.py` 中一个 `DiT_diff`/UNet 路径，但其 `forward()` 在当前代码中没有使用定义好的 transformer blocks，也不消费 causal mask；不能把这条备用路径当作论文 CAT 证据。主运行链应以 `main.py → causalfusion.models → model.diff_train` 为准。

### 7. 训练目标与默认参数

主入口当前默认：

- batch size 1024；
- hidden size 1024，VAE latent 256；
- 2,000 epochs、2,000 diffusion steps；
- AdamW learning rate $3\times10^{-6}$；
- transformer depth 4，16 heads（CLI 的 `--head=64` 并未传入主模型）；
- AR decay 0.9，AR weights 2→1 linear；
- seed 3407；
- decoder frozen (`decoder_train=0`)。

`normal_train_diff()` 还使用 StepLR 每 100 epochs 乘 0.1，gradient norm clip 1.0（`diff_train.py:224-234,312-318`）。函数参数虽接收 `ar_step_decay`，内部调用却硬编码 `0.9`；CLI 改 `--ar_step_decay` 在当前主路径不会改变 split decay。这是直接代码发现的复现陷阱。

同样，函数计算 per-token `ar_weights` 后，loss 只乘 `ar_weights.mean()`，没有逐 token 应用权重；因此主入口的 `max-ar-weight/min-ar-weight/schedule` 也未真正传入该函数。论文关于 decay influence 的解释与当前 release code 不能视为完全一一对应。

### 8. reverse diffusion 与已知值约束

推断从高斯 $x_T$ 开始，按 timestep 逆序调用模型并用 `NoiseScheduler.step()` 更新。`sample_diff()` 每步都计算 PCC/RMSE（这要求测试 ground truth，仅适合 benchmark），并将未被 mask 的位置重新替换为真实 `gt`：

$$
x_t\leftarrow M\odot x_t+(1-M)\odot x_{gt}.
$$

这相当于 conditional imputation：只生成指定 missing/masked positions，保留已知 ST values（`model/sample.py:51-122`）。主入口传 `sample_intermediate=diffusion_step`，执行完整 2,000 steps；尽管函数默认 200，实际 main 覆盖了它。

需要注意主入口训练指定 `pred_type='noise'`，采样却传 `model_pred_type='x_start'`（`main.py:138-149,172-187`）。这可能是 scheduler API 的设计，也可能是 release code 中的命名/配置不一致；在未运行端到端 benchmark前不能声称完全确认。

### 9. 逐图读证据

#### 图 1：Granger causality 是动机，不是模型监督

MC 数据若干 gene pairs 的 F-statistic/p-value 显示方向统计依赖。它支持“相关模型可能遗漏信息”，但 Granger causality 在非时间、共享混杂的表达数据上不等价于干预因果，也没有被转换为训练 graph。

#### 图 2：训练/推断总图

ST 与 scRNA 经过两个输入头得到 S-latent/C-latent；S-latent 加噪，CAT 接收 condition/clean/noisy tokens并预测 noise；reverse diffusion 后 decoder 输出空间表达。图中的 causal mask 必须结合图 10 才能理解。

#### 图 3：diffusion × AR 二维网格

横轴是 diffusion timestep，纵轴是 AR group。每个 group 有自己的 noisy states，但后续 group依赖早期 clean context。代码用一次 parallel transformer forward实现，不是外层 Python 逐 group训练完整 DDPM。

#### 图 4–5：预测结构与表达相似

十个数据集上比较 predicted vs true UMAP 和 gene hierarchical clustering。UMAP overlap 支持 global geometry，heatmap 支持 gene pattern；二者均不能代替逐 spot calibration 或 held-out biological validation。

#### 表 1 与主要指标

论文报告 CausalGeD 在 PCC、SSIM、RMSE、JS across 10 datasets 总体优于九个 baselines，提升 5–32%。split 是按 genes，结果回答“未测基因 spatial profile prediction”，不等于新 spots/cells 的泛化。

#### 图 6–9：消融

- decoder training 在多数数据集略差，支持默认冻结 decoder；
- VAE encoder、AR decay、transformer depth 与 diffusion steps均被比较；
- 约 3+ blocks 已接近稳定，说明 mask/grouping 比单纯加深网络更关键；
- 论文称较少 diffusion steps仍保持较好结果，但官方 main 默认完整 2,000。

#### 图 10：mask构造

白色为允许、黑色为禁止；condition column 全局可见，clean context与 noisy groups形成块状单向结构。官方 `get_attn_mask()` 与该图能直接对应，是当前最强 paper-code Exact 证据之一。

### 10. 论文—代码匹配结论

| 机制 | 官方代码 | 匹配 | 关键边界 |
|---|---|---|---|
| ST/sc 双输入头 + shared VAE encoder | `model/diff_train.py:116-178` | Exact | decoder只输出ST维度 |
| cosine latent diffusion | `diff_train.py:216-290` | Exact | zero/nonzero mask额外存在 |
| random decayed AR grouping | `diff_train.py:52-63` | Exact/Partial | 调用硬编码0.9 |
| block causal mask | `diff_train.py:90-113` | Exact | condition全局可见 |
| CAT transformer | `causalfusion/models.py:227-399` | Exact | 主路径不是备用 `DiT_diff` |
| noise loss | `diff_train.py:27-49,304-315` | Partial | MSE+Huber，AR weight仅取mean |
| reverse imputation | `model/sample.py:51-122` | Exact/Partial | 每步使用 benchmark ground truth mask |
| 论文默认/ablation | `main.py` CLI | Partial | ar_decay、head等参数有未生效/未传递问题 |

### 11. 版本与复现边界

官方仓库由作者主页直接链接，本地快照 commit 为 `8474310e4d6acacf01dd712766d7aa16e32d49a2`。环境锁定 Python 3.10、PyTorch 2.0.1+cu118、scanpy 1.10.4、anndata 0.11.1 等。README 只给 `python main.py`/`bash HBC.sh` 的短入口；数据需从 Zenodo下载并放入特定目录。

精确复现仍有边界：无自动测试；主脚本强制查询当前 CUDA device；部分 CLI 参数未传到实际模型/训练函数；存在两套 diffusion model code；训练/采样 pred-type naming不一致；checkpoint/data未随 repo提供。核心机制可直接审计，但论文全部数值需要数据、GPU、HBC/各dataset配置和对上述差异的谨慎处理。

### 12. 正确理解“causal”

1. Granger analysis证明条件预测依赖，不证明无混杂因果。
2. CAT mask强制信息单向流动，但 direction来自随机 token order/grouping。
3. 没有输出 TF→target edge list或可干预 structural causal model。
4. 性能提升说明该 inductive bias对预测有用，不能单独证明学到真实 gene regulation。

所以最稳妥结论是：CausalGeD 是 causality-inspired/autoregressive diffusion imputer；若要提出生物因果关系，还需 perturbation、time-course或可信 GRN prior 验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CausalGeD: Blending Causality and Diffusion for Spatial Gene Expression Generation

**Authors**: Rabeya Tus Sadia, Md Atik Ahamed, Qiang Cheng (University of Kentucky)
**ArXiv**: 2502.07751 | **Year**: 2025 | **Venue**: arXiv preprint (IEEE format)
**Code**: Not publicly released

---

### Motivation & Novelty

#### Biological Problem

Spatial transcriptomics (ST) platforms capture the spatial distribution of gene expression in tissue sections, but are fundamentally limited: imaging-based methods (MERFISH, seqFISH, STARmap) measure only a small panel of pre-selected genes, while sequencing-based platforms (10X Visium, Slide-seqV2) offer broader gene coverage but at coarser resolution. Single-cell RNA sequencing (scRNA-seq) provides genome-wide expression profiles but loses spatial information during cell dissociation. A critical task in spatial genomics is therefore to **impute missing spatial gene expression** using paired scRNA-seq as a reference.

#### Limitations of Existing Approaches

Prior methods approach this task without modeling gene-gene causal dependencies:

- **SpaGE** (Nucleic Acids Research, 2020): learns gene-gene relationships from scRNA-seq for transfer, but correlation-based, not causal
- **novoSpaRc** (Nature Protocols, 2021): optimal transport for spatial reconstruction; ignores regulatory dynamics
- **SpatialScope** (Nature Communications, 2023): deep generative model for ST-scRNA-seq integration; no explicit regulatory modeling
- **stDiff** (Briefings in Bioinformatics, 2024): first diffusion model for this task; learns spatial continuity, not causality
- **SpaDiT** (Briefings in Bioinformatics, 2024): diffusion + transformer for spatial gene prediction — previous best method
- **Tangram** (Nature Methods, 2021): deep learning alignment; supervised by predefined cell-type annotations
- **scVI** (Nature Methods, 2018): latent variable model for scRNA-seq; not spatially aware
- **stPlus** (Bioinformatics, 2021): reference-based enhancement; limited to observed gene types
- **SpaOTsc** (Nature Communications, 2020): optimal transport for signaling; correlation-based

All of these methods model gene co-expression (what genes are expressed together) but not **gene co-regulation** (how one gene's expression mechanistically drives another's). This is the gap CausalGeD addresses.

#### What's New

1. **Causal gene modeling without predefined relationships**: CausalGeD incorporates gene-gene causal structure through an autoregressive generation process, where later-predicted genes are conditioned on earlier-predicted genes — without requiring a pre-specified gene regulatory network
2. **CAT module**: A Causality-Aware Transformer that fuses diffusion (global noise removal) with autoregression (local regulatory conditioning) via a purpose-built causal attention mask
3. **AR step decay**: Stochastic step-size generation with geometric decay ($\alpha = 0.8$) that mirrors gene regulatory hierarchies — dominant regulatory genes processed first in larger blocks
4. **Validated causal motivation**: Granger causality F-statistics >200 (p < 1e-16) across gene pairs in the MC dataset validate that causal gene dependencies are real and statistically robust

---

### Method Overview

CausalGeD is a **latent diffusion + autoregressive generation** framework with the following pipeline:

1. **Preprocessing**: Log-library-size normalization; top 25% HVG selection; 70/20/10 train/val/test split
2. **Two-headed VAE encoder**: Separate encoder heads map ST spots ($\mathbb{R}^p \to \mathbb{R}^d$, S-latent) and scRNA-seq cells ($\mathbb{R}^q \to \mathbb{R}^d$, C-latent) to a shared latent space
3. **Forward diffusion**: Adds Gaussian noise to S-latent over $T = 2000$ steps (Eq. 1)
4. **CAT module** (Causality-Aware Transformer):
   - Stochastically divides genes into AR step groups with exponentially decaying sizes (Algorithm 1, $\alpha = 0.8$)
   - Assembles tokens: [C-latent (condition) | clean S-latents from previous AR steps (visible) | noisy S-latents for current step]
   - Applies causal attention mask (Algorithm 2) enforcing left-to-right AR dependencies
   - Predicts noise $\hat{\varepsilon}$ via ≥3 transformer blocks
5. **Reverse diffusion** (inference): Iterates from $t = T$ to $1$, denoising AR step-by-step guided by scRNA-seq C-latent
6. **Decoder**: Frozen VAE decoder upsamples denoised latent $\mathbb{R}^d \to \mathbb{R}^p$ to reconstruct ST expression

The biological assumptions:
- ST genes must be a subset of scRNA-seq genes (required for shared vocabulary)
- Gene expression follows a loose causal ordering (upstream regulators before downstream targets) that can be learned implicitly from data

See `doc_method.md` for full equation derivations and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets (10 paired ST + scRNA-seq)

| Code | Tissue | ST Platform | scRNA Platform |
|------|--------|------------|---------------|
| MG | Mouse brain (hippocampus region) | Slide-seqV2 | 10X Chromium |
| MH | Mouse hypothalamus | MERFISH | Smart-seq |
| MHPR | Mouse hypothalamic preoptic region | STARmap | Smart-seq |
| MVC | Mouse visual cortex | STARmap | Smart-seq2 |
| MHM | Mouse heart muscle | 10X Visium | 10X Chromium |
| HBC | Human breast cancer | 10X Visium | 10X Chromium |
| ME | Mouse embryo | seqFISH | Smart-seq2 |
| MPMC | Mouse primary motor cortex | MERFISH | Smart-seq |
| MC | Mouse cortex | Slide-seqV2 | Smart-seq2 |
| ML | Mouse muscle (limb) | 10X Visium | 10X Chromium |

Datasets span diverse sparsity levels; MH dataset downsampled to create high-sparsity conditions.

#### Metrics

- **PCC** (Pearson Correlation Coefficient, ↑): linear correlation between predicted and ground-truth spatial expression vectors
- **SSIM** (Structural Similarity Index, ↑): similarity accounting for luminance, contrast, and structure
- **RMSE** (Root Mean Square Error, ↓): z-score prediction error
- **JS** (Jensen-Shannon divergence, ↓): dissimilarity between predicted and true expression probability distributions

#### Key Results (Table I)

CausalGeD vs. SpaDiT (best baseline):

| Dataset | CausalGeD PCC | SpaDiT PCC | Improvement |
|---------|--------------|------------|-------------|
| MG | 0.836 | 0.657 | +27.2% |
| MH | 0.612 | 0.621 | -1.4% (SpaDiT wins) |
| MHPR | 0.825 | 0.770 | +7.1% |
| MVC | 0.853 | 0.725 | +17.7% |
| MHM | 0.918 | 0.573 | +60.2% |
| HBC | 0.921 | 0.772 | +19.3% |
| ME | 0.912 | 0.590 | +54.6% |
| MPMC | 0.877 | 0.808 | +8.5% |
| MC | 0.879 | 0.812 | +8.3% |
| ML | 0.895 | 0.784 | +14.2% |

CausalGeD wins on 9/10 datasets in PCC; SpaDiT wins on MH (MERFISH mouse hypothalamus, notably high sparsity post-downsampling).

**Biological significance**:
- HBC (human breast cancer): 21.8% SSIM improvement — better identification of tumor microenvironment spatial patterns
- ME (mouse embryo): 34.9% PCC improvement — enables study of developmental gene regulation
- SSIM results follow similar pattern (e.g., HBC: 0.895 vs SpaDiT 0.717; MHM: 0.886 vs 0.495)

**JS divergence**: CausalGeD dramatically reduces distribution divergence (e.g., MHM: 0.111 vs SpaDiT 0.463; ME: 0.101 vs 0.549), indicating much better-calibrated expression distributions.

#### Ablation Studies

| Component | Finding |
|---|---|
| VAE decoder training | Frozen decoder better on 4/5 datasets; skip decoder fine-tuning |
| Encoder variation (VAE) | Helps on 7/8 datasets (avg +2% PCC); keep VAE reparameterization |
| AR step decay α | α=0.8 optimal; α→1.0 (uniform) degrades all datasets |
| Transformer blocks | ≥3 blocks stable (~0.92-0.94 PCC); 1-2 blocks insufficient |
| Diffusion timesteps | T/20 (100 steps) within 1% of T=2000; robust across strategies |

---

### Reproducibility

**Rating: 3/5** — 官方训练与采样源码已公开，可审计核心路径；但缺少权重、处理后输入和一键复现实验资产。

**What is missing**:
- Model weights and checkpoints
- Model weights and paper-ready processed inputs
- A single command that reproduces all reported tables and figures
- Documentation resolving the code's hard-coded AR decay and training/sampling prediction-type boundary

**Practical notes**:
- The method is inspired by [14] Deng et al. "Causal Diffusion Transformers" (arXiv 2412.12095, 2024) — reading that paper's codebase (if available) may provide architectural details
- All 10 datasets are publicly available; preprocessing described in sufficient detail to reproduce
- Direct code inspection resolves many architecture defaults, but paper-level numerical reproduction remains unverified
- Contact: {rabeya.sadia, atikahamed, qiang.cheng}@uky.edu

**Strength**: Novel conceptual contribution (causality-aware diffusion for gene expression) clearly motivating and biologically grounded.
**Weakness**: Without released weights and fully prepared inputs, direct numerical comparison still requires substantial reconstruction. The MH dataset underperformance (where SpaDiT wins) is not explained.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
