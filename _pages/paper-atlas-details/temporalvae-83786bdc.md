---
layout: default
permalink: /paper-atlas/temporalvae-83786bdc/
title: "TemporalVAE"
nav: false
description: "TemporalVAE 的任务是监督式时间映射：参考图谱中的细胞已有胚胎日、Carnegie stage 或其他采样时间标签，模型学习“转录组 → 图谱时间”的关系，再给新胚胎、新平台或新物种的 query cells 预测与参考时钟对齐的时间。 这与 DPT、Monocle 或 RNA velocity 的无监督排序不同。TemporalVAE 的方向与时间尺度来自训练标签；"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Cell Biology · 2025</span>
    </div>
    <h1>TemporalVAE</h1>
    <p>TemporalVAE: atlas-assisted temporal mapping of time-series single-cell transcriptomes during embryogenesis</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41556-025-01787-7" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for TemporalVAE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/StatBiomed/TemporalVAE" target="_blank" rel="noopener noreferrer" aria-label="Open code for TemporalVAE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TemporalVAE 方法解读：用发育图谱训练一个“细胞生物时间”回归器

### 它解决的不是普通 pseudotime 问题

TemporalVAE 的任务是**监督式时间映射**：参考图谱中的细胞已有胚胎日、Carnegie stage 或其他采样时间标签，模型学习“转录组 → 图谱时间”的关系，再给新胚胎、新平台或新物种的 query cells 预测与参考时钟对齐的时间。

这与 DPT、Monocle 或 RNA velocity 的无监督排序不同。TemporalVAE 的方向与时间尺度来自训练标签；预测值应读作“在该参考图谱上最像哪个发育时间”，不是从单个细胞观察到的真实年龄，也不是细胞未来状态的动力学模拟。

### 输入与输出

输入是 cells × selected genes 的预处理表达矩阵 $\mathbf x_i$ 和参考细胞的连续时间标签 $t_i$。论文流程包括低质量过滤、HVG 选择、每细胞总量归一到 $10^6$、log transform、逐基因标准化及时间缩放。Query 必须与 reference 使用同一基因空间和兼容的变换。

模型输出包括：50 维默认 latent posterior、表达重构、标准化时间预测及反变换后的 atlas-aligned time。固定模型后还可逐基因做 in silico perturbation，得到每个细胞的预测时间变化并对时间敏感基因投票排序。

### 三个网络共享一个潜在状态

#### 1. 编码器

编码器把表达向量映射到对角高斯：

$$
q_\phi(\mathbf z_i\mid\mathbf x_i)=
\mathcal N(\boldsymbol\mu_i,\operatorname{diag}(\boldsymbol\sigma_i^2)).
$$

源码用全连接层、BatchNorm、Tanh/LeakyReLU 逐步压缩表达，最后由 `fc_mu` 与 `fc_var` 输出 $\mu$ 和 log variance。重参数化为

$$
\mathbf z_i=\boldsymbol\mu_i+
\exp(\tfrac12\log\boldsymbol\sigma_i^2)\odot\boldsymbol\epsilon,
\quad\boldsymbol\epsilon\sim\mathcal N(0,I),
$$

使随机采样仍可反向传播。默认 latent dimension 是 50。

#### 2. 表达解码器

Decoder 从同一 $\mathbf z_i$ 重构 $\hat{\mathbf x}_i$。它迫使 latent 保留足以解释细胞状态的转录组信息，避免网络只记住一个狭窄的时间回归轴。论文的消融图显示移除 time predictor 后 latent 的时间预测能力下降；反过来，若移除 reconstruction，模型则更接近普通监督 MLP，而非 VAE 表征模型。

#### 3. 时间预测头

另一个 MLP 从 $\mathbf z_i$ 输出标量 $\hat t_i$。源码类名仍叫 `clf_decoder`，但最终损失是连续标签 MSE，并不是类别交叉熵，因此这里实际是 regression head。其宽度还受 `label_num` 影响：默认 `label_num=10` 时中间层为 20；这是一项实现超参数，不是时间类别数的概率模型。

### 联合目标如何平衡三件事

论文写出表达与时间的联合条件似然：

$$
p(\mathbf x_i,t_i\mid\mathbf z_i)=
p_\theta(\mathbf x_i\mid\mathbf z_i)
p_\psi(t_i\mid\mathbf z_i),
$$

并用带 KL 的 negative ELBO 优化。公开实现具体为

$$
L=\operatorname{MSE}(\hat{\mathbf x},\mathbf x)
+\lambda_{KL}D_{KL}[q_\phi(\mathbf z\mid\mathbf x)\|\mathcal N(0,I)]
+\lambda_t\operatorname{MSE}(\hat t,t).
$$

默认配置中 `kld_weight=0.00025`、`clf_weight=1`，Adam learning rate 为 0.005，每 epoch 乘 0.95。因此实际训练是高斯假设对应的 MSE surrogate，而不是显式学习 $\sigma_x^2,\sigma_t^2$ 后计算完整 Gaussian NLL。

一个简单例子：某 batch 的 reconstruction MSE 为 0.20，KL 为 40，time MSE 为 0.03，则总损失约为

$$
0.20+0.00025\times40+1\times0.03=0.24.
$$

此时 reconstruction 仍占主导；若把 `clf_weight` 调到 5，时间项变为 0.15，总损失为 0.36，模型会更强地牺牲其他结构去拟合时间。不同数据集配置不能只按模型名字比较，还要核对这两个权重。

### 训练、验证与 query mapping

参考训练通常按 embryo、stage、dataset 或 species 整批留出，而不是随机拆散细胞。这样能减少同一胚胎/批次同时出现在 train 和 test 所造成的泄漏。输出用 Spearman、Pearson 和 Kendall correlation 评价：Spearman/Kendall 主要看顺序，Pearson 还要求预测刻度近似线性。

应用新 query 时，必须将基因对齐到训练输入、复用相同 preprocessing/scale，再取 latent 和 time head 输出。论文将 mouse atlas 模型映射到 Stereo-seq，将 human peri-implantation reference 映射到独立 in vitro/in vivo datasets，并做跨灵长类 leave-one-species-out。好的相关性说明 reference clock 可迁移，不自动排除 platform、cell-type composition 或 species differences 被模型当作时间。

论文 Methods 报告 mouse 训练 100 epochs、human embryo 70 epochs；检查到的 human notebooks 使用 50 epochs。因此“论文 human 70-epoch 完整运行”在当前公开 notebook 证据中未找到，不能声称默认命令精确复现。

### in silico perturbation 到底测量什么

先用固定模型得到原始预测 $\hat t_i$。对基因 $j$，把所有细胞该基因的**预处理表达**设为本数据中的最小值，重新预测 $\check t_{ij}$：

$$
\Delta t_{ij}=\hat t_i-\check t_{ij}.
$$

每个细胞按 $|\Delta t_{ij}|$ 选 top 50 genes，再跨细胞计票。若某细胞原预测 8.0 天，把基因 $j$ 设到最小后变成 7.4 天，则论文定义 $\Delta t=+0.6$ 天；绝对值 0.6 表示该模型对该基因敏感。

源码若干输出实际计算 `perturbed - original`，符号与论文定义相反；排序使用绝对值时排名不变，但解释“加速/延迟”前必须统一符号。把一个标准化基因直接设到全局最小还可能制造超出真实共表达分布的细胞，因此这不是 knockout simulation，也不能从大 $|\Delta t|$ 推出基因对发育时间具有因果作用。它更接近 feature sensitivity / counterfactual stress test。

### 如何读论文图和补充证据

- **图 1** 展示 reference training、query staging 与 perturbation 三个用途；模型预测的是 reference-aligned time，不是 trajectory vector field。
- **图 2** 在 acinar、embryonic beta cells 和 germline datasets 上比较 Psupertime、Calderon22、Seurat、OT-Regressor 等；小数据集结果支持监督时间回归，但每种方法的 preprocessing/超参会影响公平性。
- **图 3** 在 mouse prenatal atlas 的大规模细胞上做 embryo-level validation，并映射 Stereo-seq；高相关性说明可扩展和跨平台一致性，不代表每类细胞都同样准确。
- **图 4** 整合 human peri-implantation reference 并预测 Xiang、Tyser 等 query；不同数据集与 stage 高度混杂，需同时检查 dataset-specific bias。
- **图 5** 做 human/marmoset/cynomolgus 跨物种时间映射；跨物种相关性依赖 ortholog selection 和共同发育程序。
- **图 6** 汇总时间敏感基因、时间 cluster 和功能富集；这些是模型敏感性与关联证据，论文没有提供对应 wet-lab perturbation 验证。
- **Extended Data Fig. 1–5** 给出架构、额外 benchmark、time-head 消融、Xiang 映射和共享敏感基因。消融支持 time head 的预测作用，但不单独证明 VAE reconstruction 或 KL 的因果贡献。

本地 supplement 目录有 `MOESM2.pdf` 与 `MOESM3.pdf`，主要承载补充表格/报告材料；主论文 OCR 已含 extended-data captions。完整原始数据和训练模型另依赖 Zenodo 与论文所述外部资源。

### 论文—源码对应与版本边界

| 论文机制 | 直接源码 | 对应程度 |
|---|---|---|
| Gaussian encoder / reparameterization | `model_master/...noAdversarial.py` | Exact |
| expression decoder + time regression head | 同一模型类 | Exact |
| joint ELBO-style objective | `loss_function()` | Partial：用 weighted MSE + KL surrogate |
| Adam + exponential scheduler | `experiment_temporalVAE.py` | Exact |
| group-held-out tests / query prediction | `utils_project.py` 与 notebooks | Partial：内部函数齐全，高层 API 未完成 |
| gene-minimum perturbation与投票 | `utils_project.py` | Exact，部分输出符号与论文相反 |
| 标准 preprocessing / HVG | utilities + notebooks / preprocessed objects | Partial：generic utility 不包办所有 manuscript feature selection |
| 一条高层 `train/predict/cross_validate` API | `tools/_training.py` | Not implemented：函数体为 `pass` |
| 全部论文图一键复现 | notebooks、外部 data/submodule | Partial |

CodeGraph 已定位核心 VAE 类、runtime model registry 和训练/perturbation入口；本次又直接核对模型、loss、optimizer、配置及 notebooks。未下载全部外部 atlas、未训练大模型、未复算论文相关系数或富集结果。

### 实际使用时的最低检查清单

应按 embryo/donor/dataset 分组留出而非随机细胞拆分；分别报告 cell types、stages 和 batches 的误差；检查 query 中缺失基因及 reference 不存在的 cell states；用多个随机种子和模型 posterior uncertainty 评估稳定性；比较 `clf_weight`、KL weight、HVG set 与 time scaling；对 perturbation 检查是否离开训练分布，并把候选基因称为“模型时间敏感”而非“控制发育时间”。若训练时间与平台或物种完全共线，任何高相关预测都需要额外的外部验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TemporalVAE Summary

### Motivation and Novelty

TemporalVAE tackles supervised temporal staging of single cells: given a time-series reference atlas, predict the biological time of query cells from their transcriptomes. This is useful in embryogenesis because large mouse, human and primate atlases now provide dense developmental clocks, while individual in vitro, in vivo, spatial or cross-species datasets need to be synchronized to those clocks.

The paper positions this task apart from classical pseudotime and trajectory methods. DPT (Nature Methods, 2016), Monocle2 (Nature Methods, 2017) and RNA velocity (Nature, 2018; scVelo, Nature Biotechnology, 2020) infer ordering or local future state, but they are not primarily reference-trained cell staging models. Psupertime (Bioinformatics, 2022) is closer because it is supervised, but the paper argues that its ordinal treatment of time can limit extrapolation across uneven intervals. Optimal-transport approaches (Cell, 2019), Pseudodynamics (Nature Biotechnology, 2019), PRESCIENT (Nature Communications, 2021) and CLADES (Nature Communications, 2025) model dynamics or trajectories rather than atlas-assisted time-label prediction for arbitrary query cells.

The novelty is a dual-objective VAE: one branch reconstructs expression, while another predicts biological time from the same latent state. The reconstruction branch regularizes the latent space so it retains cell-state structure instead of learning a narrow time-only regressor. The paper also adds in silico perturbation to rank genes whose minimum-expression perturbation changes model-predicted time.

### Method Overview

TemporalVAE starts from filtered, normalized, log-transformed and scaled expression matrices with biological time labels. An encoder MLP maps each cell expression vector $\mathbf{x}_i$ to Gaussian latent parameters $\boldsymbol{\mu}_i$ and $\boldsymbol{\sigma}_i^2$ for $q_\phi(\mathbf{z}_i\mid\mathbf{x}_i)$. A decoder reconstructs expression from $\mathbf{z}_i$, and a time predictor maps $\mathbf{z}_i$ to $\hat{t}_i$.

The paper writes the objective as a VAE likelihood over expression and time plus a KL term. The public code implements this practically as MSE reconstruction loss, weighted KL loss and weighted MSE time-prediction loss. Default public configs use `latent_dim=50`, Adam with learning rate 0.005 and exponential decay 0.95, and `kld_weight=0.00025`.

For deployment, a reference model is trained on atlas cells and then applied to held-out stages, embryos, platforms, datasets or species. For interpretation, each gene is set to its minimum preprocessed expression value, the fixed model predicts time again, and genes are ranked by per-cell absolute time shifts and vote counts.

### Evaluation

On small datasets, TemporalVAE outperforms Psupertime, Calderon22, Seurat and OT-Regressor in leave-one-stage-style tests. Reported examples include acinar cells with Spearman $\rho=0.755$ and embryonic beta cells with $\rho=0.931$, with stronger separation of distant stages such as P60.

On the mouse prenatal atlas, the model is applied after filtering to 881,168 cells and 979 HVGs. The fold-test plot reports Spearman 0.890, Pearson 0.914 and Kendall's tau 0.729, showing broad agreement between embryo stage and predicted biological time. The model is then transferred to a mouse Stereo-seq query dataset, supporting cross-platform staging.

In human peri-implantation, TemporalVAE integrates multiple in vitro and in vivo datasets and predicts held-out Xiang and Tyser/T datasets. The visuals show reference-aligned predicted times in both query settings. Cross-primate experiments use leave-one-species-out prediction for marmoset and cynomolgus, with reasonable temporal correlations despite species and time-range differences.

The perturbation analysis identifies early, middle and late time-cluster genes and highlights shared candidates such as Snhg11, Ell2, Slc25a21, March3 and Rbfox1. Functional enrichments, especially neuronal and synaptic terms in later clusters, support biological plausibility but do not constitute causal perturbation validation.

### Reproducibility

Rating: **3.5 / 5**.

The core model is public and source-verifiable. The repository implements the encoder, decoder, time predictor, loss, optimizer setup, dataset loaders, cross-validation utilities, query prediction helpers and perturbation/voting routines. The code availability statement points to the GitHub package, and the repository includes example notebooks plus Zenodo-backed human embryo dataset loaders.

The main limitations are practical. High-level `train`, `predict` and `cross_validate` wrappers are placeholders, so users must rely on notebooks and internal utilities. Some manuscript reproduction materials are referenced through an external submodule rather than fully present in the normal clone. The paper's Gaussian likelihood is implemented as MSE surrogate losses, and the checked human notebooks use 50 epochs rather than the Methods' stated 70. Large atlas and full figure reproduction also depend on substantial external datasets and GPU resources.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
