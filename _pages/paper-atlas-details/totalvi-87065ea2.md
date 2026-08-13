---
layout: default
permalink: /paper-atlas/totalvi-87065ea2/
title: "totalVI"
nav: false
description: "totalVI 的本质是：用一个联合 VAE 学习 RNA+蛋白共同的细胞状态，同时把蛋白观测拆成“背景概率 + 背景均值 + 前景均值”。这样它不仅能做 embedding，还能把蛋白背景校正、缺失蛋白预测、差异表达和 RNA-蛋白相关性都写成同一个概率模型上的后验查询。"
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
      <span>Nature Methods · 2021</span>
    </div>
    <h1>totalVI</h1>
    <p>Joint probabilistic modeling of single-cell multi-omic data with totalVI</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/YosefLab/scvi-tools" target="_blank" rel="noopener noreferrer" aria-label="Open code for totalVI">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## totalVI 方法中文解读

### 这篇论文要解决什么问题？

CITE-seq 在同一个单细胞中同时测 RNA UMI 计数和细胞表面蛋白计数。难点是两种模态的技术噪声不同：RNA 有测序深度和过度离散问题，蛋白还有抗体背景、环境抗体和非特异性结合等背景信号（`paper.md:21-27`, `paper.md:77-83`）。如果先只用 RNA 聚类，再事后查看蛋白，分析会偏向 RNA；如果不同数据集测了不同抗体面板，还会出现蛋白缺失，阻碍整合分析（`paper.md:36-37`, `paper.md:106-109`）。

totalVI 的目标是用一个端到端概率模型同时完成：

- 学习 RNA 和蛋白共同决定的低维细胞状态；
- 对 RNA 和蛋白分别建模各自的技术噪声；
- 对蛋白背景做概率分解；
- 支持不同抗体面板的数据整合和缺失蛋白预测；
- 为差异表达、去噪表达和 RNA-蛋白相关性提供后验查询（`paper.md:47-50`, `paper.md:205-214`）。

### totalVI 的核心思想

totalVI 是一个 VAE。编码器把每个细胞的 RNA、蛋白和批次信息映射到潜在变量，解码器再从潜在变量和批次生成 RNA 与蛋白计数的分布（`paper.md:220-223`, Fig. 1）。

它的关键创新在蛋白部分：不是给每个蛋白设一个全局阈值来判断背景/前景，而是对每个“细胞-蛋白”组合建模背景概率。论文记这个背景概率为 $\pi_{nt}$，前景概率就是 $1-\pi_{nt}$（`paper.md:83-86`, `paper.md:714-722`）。

直观地说：

```text
同一个蛋白计数值
  如果出现在符合该蛋白生物学表达的细胞状态中 -> 更可能是前景
  如果出现在不应表达该蛋白的细胞状态中       -> 更可能是背景
```

Fig. 2 中 CD20 和 CD28 的例子正是这个逻辑：相似的蛋白计数会根据细胞在潜在空间的位置得到不同的前景概率（`paper.md:89-100`）。

### 生成模型怎么写？

对每个细胞 $n$，输入包括 RNA 计数 $x_n$、蛋白计数 $y_n$ 和批次/面板变量 $s_n$。模型估计条件分布 $p_\nu(x_n,y_n|s_n)$（`paper.md:220-223`）。

#### 潜在变量和先验

论文定义：

- $z_n$：细胞状态的低维表示，论文实验中为 20 维 logistic normal（`paper.md:229-229`）。
- $\ell_n$：RNA library size 因子，按批次设 log-normal 先验（`paper.md:232-232`）。
- $\beta_{nt}$：蛋白背景强度，按蛋白和批次设 log-normal 先验（`paper.md:232-232`）。

代码中 `TOTALVI` 默认 `n_latent=20`，但这个提交的 `latent_distribution` 默认是 `"normal"`，logistic normal 需要显式设置为 `"ln"`；`"ln"` 时编码器会对正态样本做 softmax（`scvi-tools/src/scvi/model/_totalvi.py:134-141`; `scvi-tools/src/scvi/nn/_base_components.py:1005-1031`）。这是当前代码默认值与论文实验设置的差异。

#### RNA 似然

论文写法：

$$\rho_n = f_\rho(z_n,s_n)$$

$$x_{ng}|z_n,\ell_n,s_n \sim \mathrm{NegativeBinomial}(\ell_n\rho_{ng},\theta_g)$$

其中 $\rho_n$ 是归一化基因频率，$\ell_n\rho_{ng}$ 是 RNA 计数均值（`paper.md:238-267`）。

代码对应关系：

- `px_["scale"]` 对应 $\rho_n$；
- `px_["rate"] = library_gene * px_["scale"]` 对应 $\ell_n\rho_n$；
- RNA 重构损失使用 `NegativeBinomial(mu=px_["rate"], theta=px_["r"])`（`scvi-tools/src/scvi/nn/_base_components.py:897-902`; `scvi-tools/src/scvi/module/_totalvae.py:317-328`）。

#### 蛋白似然

论文对蛋白使用负二项混合模型：

$$\pi_n = h_\pi(z_n,s_n), \qquad \alpha_n = g_\alpha(z_n,s_n)$$

$$v_{nt}|z_n,s_n \sim \mathrm{Bernoulli}(\pi_{nt})$$

$$r_{nt}|v_{nt},\beta_{nt},z_n,s_n \sim \mathrm{Gamma}(\phi_t, v_{nt}\beta_{nt}+(1-v_{nt})\beta_{nt}\alpha_{nt})$$

$$y_{nt}|r_{nt} \sim \mathrm{Poisson}(r_{nt})$$

论文说明 $\alpha_{nt}>1$，所以 $\beta_{nt}$ 是背景均值，$\beta_{nt}\alpha_{nt}$ 是前景均值；$\pi_{nt}$ 是背景概率（`paper.md:273-301`, `paper.md:310-316`）。

代码里这个映射是明确的：

| 论文符号 | 代码变量 | 含义 |
|---|---|---|
| $\beta_{nt}$ | `py_["rate_back"]` | 背景均值 |
| $\alpha_{nt}$ | `py_["fore_scale"]` | 前景相对背景的放大倍数 |
| $\beta_{nt}\alpha_{nt}$ | `py_["rate_fore"]` | 前景均值 |
| $\pi_{nt}$ | `sigmoid(py_["mixing"])` | 背景概率 |
| $1-\pi_{nt}$ | `1 - sigmoid(py_["mixing"])` | 前景概率 |

证据是：解码器设置 `rate_fore = rate_back * fore_scale`，并输出 `py_["mixing"]`；重构损失把 `rate_back` 作为混合分布 component 1，把 `rate_fore` 作为 component 2；混合分布实现说明 `mixture_logits` 是 component 1 的概率，而且 totalVI 中 component 1 是背景（`scvi-tools/src/scvi/nn/_base_components.py:903-928`; `scvi-tools/src/scvi/module/_totalvae.py:336-342`; `scvi-tools/src/scvi/distributions/_negative_binomial.py:144-158`, `595-666`）。

这也解释了公共 API 的符号方向：`get_protein_foreground_probability` 先算 `sigmoid(py_["mixing"])`，再返回 `1 - py_mixings`（`scvi-tools/src/scvi/model/_totalvi.py:593-715`）。

### 训练与推断

论文用变分推断近似后验：

$$q_\eta(\beta_n,z_n,\ell_n|x_n,y_n,s_n)
:= q_\eta(\beta_n|z_n,s_n)q_\eta(z_n|x_n,y_n,s_n)q_\eta(\ell_n|x_n,y_n,s_n)$$

训练目标是最大化 ELBO，使用小批量随机优化、KL warm-up、Adam、验证集早停和学习率调整（`paper.md:379-399`）。

代码中：

- `_regular_inference` 对 RNA/蛋白输入做缩放和 `log1p`，拼接后送入 `EncoderTOTALVI`，得到 `qz`、`ql`、`z` 和 `library_gene`（`scvi-tools/src/scvi/module/_totalvae.py:524-650`）。
- `TOTALVI.train` 使用 `AdversarialTrainingPlan` 和 `DataSplitter`，默认 batch size 256，并配置 early stopping、KL warm-up 和学习率 plateau 调整（`scvi-tools/src/scvi/model/_totalvi.py:239-357`）。
- `TOTALVAE.loss` 组合 RNA 重构损失、蛋白混合重构损失、$z$ 的 KL、可选 $\ell$ 的 KL，以及蛋白背景均值的 KL（`scvi-tools/src/scvi/module/_totalvae.py:652-760`）。

需要注意：代码没有一个直接命名为 `q_beta` 的对象。蛋白背景后验通过解码器输出的 `back_alpha/back_beta`、采样的 `log_pro_back_mean` 以及对应 KL 项来实现（`scvi-tools/src/scvi/nn/_base_components.py:906-913`; `scvi-tools/src/scvi/module/_totalvae.py:704-706`）。

### 缺失蛋白如何处理？

论文说，不同 batch 可以测不同蛋白面板。对编码器，缺失蛋白用 0 填充；对解码器/ELBO，只计算该 batch 中实际观测到的蛋白项（`paper.md:402-413`）。

代码中可以验证到后半部分和数据注册逻辑：

- `ProteinFieldMixin` 会按 batch 检查某个蛋白是否全为 0；如果全为 0，就认为该 batch 缺失这个蛋白，并生成 `protein_batch_mask`（`scvi-tools/src/scvi/data/fields/_protein.py:52-83`）。
- `TOTALVI.__init__` 读取这个 mask，传给 `TOTALVAE`，并在检测到缺失蛋白时启用 adversarial classifier（`scvi-tools/src/scvi/model/_totalvi.py:150-166`, `202-220`）。
- `TOTALVAE.loss` 用 mask 只保留观测蛋白的重构损失和蛋白背景 KL（`scvi-tools/src/scvi/module/_totalvae.py:672-685`, `713-719`）。

缺口：我没有在 `TOTALVAE` 内找到显式“把缺失蛋白赋值为 0”的代码。当前可见实现更像是：注册后的蛋白矩阵本身在缺失位置已经是 0，然后模型用 mask 防止这些 0 参与蛋白似然和 KL。也就是说，论文的“zero substitution”在这个代码快照中不是模块层的一句赋值，而是由输入数据表示和 field registration 共同承担。

### 下游分析怎么从模型得到？

#### 去噪蛋白表达

论文把背景强度设为 0，返回前景均值的后验期望：

$$ (1-\pi_{nt})\beta_{nt}\alpha_{nt} $$

也就是“前景均值乘以前景概率”（`paper.md:456-472`）。

代码中 `get_normalized_expression` 默认返回：

```python
protein_val = py_["rate_fore"] * (1 - protein_mixing)
```

如果设置 `include_protein_background=True`，才会再加上 `rate_back * protein_mixing`（`scvi-tools/src/scvi/model/_totalvi.py:541-548`）。

#### 缺失蛋白预测和批次转换

论文的思路是：先把细胞编码到共享潜在空间，再用目标 batch/panel 的条件解码，从而预测该 batch 中缺失的蛋白（`paper.md:475-494`）。

代码中对应 `transform_batch`：

- `get_normalized_expression` 可以传入目标 batch，并对多个 batch 取平均（`scvi-tools/src/scvi/model/_totalvi.py:510-555`）。
- `TOTALVAE.generative` 在解码前把 `batch_index` 替换为 `transform_batch`（`scvi-tools/src/scvi/module/_totalvae.py:436-451`）。

#### 差异表达

论文把 DE 写成后验 LFC 查询。RNA 使用 $\log_2\rho_a-\log_2\rho_b$；蛋白使用背景去除后的前景均值，并加入 prior count $\epsilon$；最后用 Bayes factor 比较 LFC 超出阈值区域与落在零假设区域的后验概率（`paper.md:500-570`）。

代码中：

- `_expression_for_de` 调用 `get_normalized_expression` 得到 RNA/蛋白表达，给蛋白加 `protein_prior_count`，再拼接成联合矩阵（`scvi-tools/src/scvi/model/_totalvi.py:717-759`）。
- `differential_expression` 把这个函数交给 `_de_core` 和 `DifferentialComputation` 做后验采样和 Bayes factor（`scvi-tools/src/scvi/model/_totalvi.py:761-879`; `scvi-tools/src/scvi/model/base/_de_core.py:160-205`; `scvi-tools/src/scvi/model/base/_differential.py:69-240`）。

设置差异：论文实验使用 $\delta=0.2$，当前代码默认 `delta=0.25`。复现实验时要显式传入 `delta=0.2`（`paper.md:516-516`; `scvi-tools/src/scvi/model/_totalvi.py:761-786`）。

#### RNA-蛋白相关性

论文强调不要直接对去噪均值做相关性，因为这会引入伪相关；它改为从控制技术因素后的后验预测分布中采样，再计算相关性（`paper.md:576-598`）。

代码中 `_get_denoised_samples` 生成去噪样本，`get_feature_correlation_matrix` 把多次采样展平后计算 Pearson 或 Spearman 相关矩阵（`scvi-tools/src/scvi/model/_totalvi.py:954-1127`）。设置差异是：论文描述固定 RNA library size 为 10,000，当前 API 默认 `rna_size_factor=1000`；复现实验应显式传入 `rna_size_factor=10000`（`paper.md:579-582`; `scvi-tools/src/scvi/model/_totalvi.py:1040-1048`）。

### 实验结果如何支持方法？

- Fig. 1 展示了总流程：RNA、蛋白、batch 输入编码器，解码器分别输出 RNA NB 和蛋白 NB-mixture 参数（`images/figure_01.png`; `paper.md:39-44`）。
- Fig. 2 显示 CD20/CD28 中，totalVI 的前景概率能根据细胞状态区分真实表达和背景，比单一 GMM 阈值更灵活（`paper.md:83-103`）。
- Fig. 3 显示 totalVI 能整合不同蛋白面板的数据，并对 held-out protein 做预测；论文报告在一个 SLN benchmark 中 totalVI 对显著不同的 80 个蛋白约 68% 表现优于 Seurat v3（`paper.md:123-129`）。
- Fig. 4 显示 totalVI 的蛋白 DE 通过背景校正减少假阳性，尤其是在 ICOS-high Treg 和 CD4+ T 的比较中（`paper.md:152-164`）。
- Fig. 5 展示 totalVI 在 B 细胞亚群分析中同时利用 RNA、蛋白、DE 和相关性，发现 transitional B cell 相关的 RNA-蛋白模块（`paper.md:173-201`）。

### 代码复现边界

论文同时说明完整结果复现代码在 `YosefLab/totalVI_reproducibility`（`paper.md:934-937`）。

- totalVI 核心 VAE；
- RNA NB 和蛋白 NB-mixture；
- 背景/前景概率符号；
- 去噪蛋白表达；
- missing-protein mask；
- posterior predictive sample；
- differential expression API；
- feature correlation API。

- SLN/PBMC/MALT 论文 benchmark 的完整脚本；
- Fig. 2-5 和 extended figures 的绘图脚本；
- B-cell subset 标注和 Vision gene signature 分析脚本；
- 论文专用的 reproducibility pipeline。

### 一句话总结

totalVI 的本质是：用一个联合 VAE 学习 RNA+蛋白共同的细胞状态，同时把蛋白观测拆成“背景概率 + 背景均值 + 前景均值”。这样它不仅能做 embedding，还能把蛋白背景校正、缺失蛋白预测、差异表达和 RNA-蛋白相关性都写成同一个概率模型上的后验查询。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## totalVI Summary

### Problem

CITE-seq measures RNA and cell-surface proteins in the same single cells, but the two modalities have different noise sources and technical biases. The paper argues that sequential workflows, often clustering on RNA and interpreting proteins afterward, bias the analysis toward one modality and become inefficient as protein panels grow (`paper.md:21-27`). A second challenge is integration: public and atlas-scale datasets may measure different antibody panels, or no proteins at all (`paper.md:36-37`, `paper.md:106-109`).

### Proposed Method

totalVI is a variational autoencoder for paired RNA and protein count data. It learns a shared latent representation of cell state while modeling modality-specific technical factors: RNA sequencing depth, protein background, batch effects, and missing proteins (`paper.md:36-50`, `paper.md:220-223`). The RNA likelihood is a negative binomial distribution with mean $\ell_n\rho_{ng}$ (`paper.md:238-267`). The protein likelihood is a negative-binomial mixture with a background mean $\beta_{nt}$, foreground mean $\beta_{nt}\alpha_{nt}$, and background probability $\pi_{nt}$ (`paper.md:273-301`).

The key modeling idea is not just joint embedding. totalVI makes protein background a cell- and protein-specific latent quantity, so downstream protein expression can use the foreground probability $1-\pi_{nt}$ instead of a global threshold (`paper.md:77-103`, `paper.md:714-722`).

### Pipeline

```text
RNA counts X + protein counts Y + batch/panel S
        |
        v
Encoder q_eta(z, l | x, y, s)
        |
        v
Shared latent cell state z
        |
        v
Decoder:
  RNA:     NB(mean = l * rho, dispersion theta)
  Protein: NB mixture(background beta, foreground beta * alpha, prob background pi)
        |
        v
Outputs:
  latent embedding, normalized RNA, foreground probability,
  denoised protein, missing-protein imputation,
  feature correlations, differential expression
```

The paper's missing-protein procedure keeps a common protein dimension across batches, uses zeros for proteins absent from a batch on the encoder side, and excludes unobserved protein terms from the decoder ELBO (`paper.md:402-413`). In the current `scvi-tools` code, this is visible as batch-wise protein masks computed during field registration and applied to protein reconstruction/KL terms; the explicit zero substitution is delegated to the registered data representation rather than a visible assignment in `TOTALVAE` (`scvi-tools/src/scvi/data/fields/_protein.py:52-83`; `scvi-tools/src/scvi/module/_totalvae.py:672-685`, `713-719`).

### Evaluation

The paper evaluates totalVI on murine spleen/lymph-node CITE-seq data and public PBMC/MALT CITE-seq datasets. It reports that posterior predictive checks preserve observed data properties better than baseline models such as factor analysis and scHPF (`paper.md:65-68`; `images/figure_06.jpg`; `paper.md:1108-1114`), and that held-out predictions are competitive for RNA and strong for proteins (`paper.md:68-71`; `images/figure_07.jpg`; `paper.md:1116-1121`).

For protein background correction, totalVI foreground probabilities separate cell-state-specific foreground from background for markers such as CD20 and CD28 better than a global GMM boundary (`paper.md:83-100`; `images/figure_02.png`). For integration, totalVI mixes datasets with matched and unmatched protein panels and can impute held-out proteins, with paper-reported improvement over Seurat v3 for a majority of significantly different proteins in one SLN benchmark (`paper.md:123-129`; `images/figure_03.png`). For DE, the totalVI test reduces apparent false positives among protein markers compared with Welch and Wilcoxon baselines by using background-corrected protein quantities (`paper.md:135-164`; `images/figure_04.png`).

### Code Match and Reproducibility

The cloned repository is the paper's named reference implementation in `scvi-tools`, not the separate `YosefLab/totalVI_reproducibility` repository named for reproducing manuscript results (`paper.md:934-937`). The core model implementation is high fidelity: `TOTALVI` constructs `TOTALVAE`, the decoder produces RNA/protein likelihood parameters, `NegativeBinomialMixture` uses background as mixture component 1, and the foreground API returns `1 - sigmoid(py_["mixing"])` (`scvi-tools/src/scvi/model/_totalvi.py:59-222`, `593-715`; `scvi-tools/src/scvi/nn/_base_components.py:897-928`; `scvi-tools/src/scvi/distributions/_negative_binomial.py:595-666`).

What is reproducible from this snapshot: training a totalVI model, extracting latent representations, normalized expression, foreground probabilities, denoised protein values, posterior predictive samples, feature correlations, and differential expression (`scvi-tools/src/scvi/model/_totalvi.py:239-357`, `401-478`, `593-715`, `717-879`, `881-952`, `954-1127`). What is not present here: paper-specific SLN/PBMC/MALT benchmark scripts, figure-generation notebooks, and B-cell analysis scripts. Those remain `Not found` in `code source` and are expected to live in the separate reproducibility repository named by the paper.

Notable implementation differences from the paper settings:

- The paper describes a 20-dimensional logistic-normal latent space; this commit defaults to `n_latent=20` but `latent_distribution="normal"`, with logistic normal available by setting `"ln"` (`scvi-tools/src/scvi/model/_totalvi.py:134-141`; `scvi-tools/src/scvi/nn/_base_components.py:1005-1031`).
- The paper states DE experiments used $\delta=0.2$, while the current `differential_expression` default is `delta=0.25` (`paper.md:516-516`; `scvi-tools/src/scvi/model/_totalvi.py:761-786`).
- The paper's correlation method fixes RNA library size at 10,000, while the current `get_feature_correlation_matrix` default is `rna_size_factor=1000` (`paper.md:579-582`; `scvi-tools/src/scvi/model/_totalvi.py:1040-1048`).

### Bottom Line

totalVI's contribution is a joint RNA-protein VAE that makes protein background an explicit probabilistic quantity. This supports a single workflow for embedding, batch/panel integration, protein denoising/imputation, DE, and correlation analysis. The available `scvi-tools` code strongly matches the core model and API-level downstream tasks, but not the paper's full result-reproduction workflow.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
