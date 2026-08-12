---
layout: default
permalink: /paper-atlas/cytovi-3e097ce5/
title: "CytoVI"
nav: false
description: "CytoVI 用带 batch/协变量条件的概率 VAE 把不同抗体技术和 panel 投到共享 latent，通过 backbone-only encoder、全 marker decoder 和 masked likelihood 学习缺失蛋白分布，并以 posterior uncertainty 支持插补与临床迁移；结果强度取决于预处理、panel overlap、参考覆盖和批次–生物混杂。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>CytoVI</h1>
    <p>CytoVI: Deep generative modeling of antibody-based single cell technologies</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2025.09.07.674699" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CytoVI：面向抗体单细胞数据的概率整合、缺失 panel 插补与临床迁移

### 为什么不能把所有蛋白单细胞数据当作同一种矩阵

流式细胞术、质谱流式和 CITE-seq 都测蛋白，但信号尺度、批次、技术平台和抗体 panel 不同。不同研究常只共享一部分 backbone markers，其余蛋白在整批样本中完全缺失。CytoVI 用一个条件变分自编码器同时处理批次校正、跨技术整合、重叠 panel 插补和不确定性估计。

论文是 bioRxiv 预印本 *CytoVI: Deep generative modeling of antibody-based single cell technologies*（DOI `10.1101/2025.09.07.674699`），本地 PDF 56 页并包含补充证据；它不是综述，且预印本结论不应写成已同行评审定论。

### 生成模型

对细胞 $i$ 的预处理蛋白向量 $x_i$，encoder 给出近似后验

$$q_\phi(z_i\mid x_i),$$

其中 $z_i$ 表示尽量去除技术差异后的内在细胞状态。decoder 以 $z_i$ 加 batch、技术或连续/分类协变量为条件，输出蛋白分布

$$p_\theta(x_i\mid z_i,b_i,c_i).$$

默认观测似然是 Normal，适合 arcsinh 后的连续相对信号；若表达严格缩放到 $(0,1)$，可选 Beta。源码在 `src/cytovi/_module.py:19-170,257-325` 直接实现两类似然与条件 decoder。预处理仍是模型合同的一部分：arcsinh cofactor、补偿、门控和缩放不同会改变似然适配与整合结果。

训练最大化 ELBO，即重建项与 latent KL 的折中。标准正态先验之外，默认可用 Gaussian mixture：

$$p(z)=\sum_{k=1}^K\pi_k\mathcal N(\mu_k,\Sigma_k).$$

若提供细胞类型标签，标签会提高对应混合成分的 logit，使困难整合得到半监督引导；它不是训练后的标签预测真值。MoG 的 KL 通过 10 次后验采样估计，而普通 Normal 使用解析 KL（`_module.py:297-359`）。默认 KL warm-up 400 epochs、early stopping patience 30、batch size 128（`src/cytovi/_model.py:315-418`）。

### 重叠 panel 为什么能够插补

多个 panel 合并后，模型输出维度是所有 marker 的并集，但 encoder 在缺失 panel 情景只读取每批都观测到的 backbone markers。训练重建损失用 mask 排除未测值：

$$
\mathcal L_{rec,i}=-\sum_p m_{ip}\log p_\theta(x_{ip}\mid z_i,b_i,c_i).
$$

源码自动从 `_nan_mask` 找 backbone，禁止把批次特异 marker 放进 encoder（`_model.py:146-189`），并在 `_module.py:327-357` 对未观测蛋白屏蔽 loss。插补时将相同 $z$ 在目标 batch 条件下解码，得到未测 marker 的后验预测。

这不是凭空恢复任意蛋白：只有当 backbone 表达与目标蛋白的关系能跨 panel/样本泛化时才可靠。模型同时输出后验预测方差，可提示不确定性，但校准仍需 held-out marker 验证。缺失 panel 时自动启用 latent adversarial classifier 以减弱 panel/batch 可辨识性；过强混合也可能移除与 batch 混杂的真实生物差异。

### 输出和下游

- latent embedding：用于批次校正、可视化、邻居与标签转移。
- normalized expression：可指定 `transform_batch` 做反事实 batch 条件解码（`_model.py:483` 以后）。
- posterior predictive samples：保留预测分布而非只给点估计（`_model.py:420-481`）。
- 差异蛋白与无标签差异丰度：在模型后验上比较条件/样本；仍是统计关联。
- scArches 式映射：冻结参考知识并将新患者映入 latent；新技术/人群超出参考分布时需重新验证。

### 图证据链

论文图 1 验证不同技术的观测分布与 posterior predictive fit；图 2 检验 batch 校正和 latent 生物保持；图 3 在 12 个 mass-cytometry panels 上整合 350 个蛋白并插补 B 细胞成熟图谱；图 4 跨 flow/CITE-seq 分析 B 细胞淋巴瘤并做 label-free DA；图 5 展示 CLL 临床 panel、参考映射和肿瘤细胞检测。补充图覆盖 likelihood、预处理、消融、imputation uncertainty 和更多基准。它们支持论文内数据情景，不保证任意 panel/疾病直接迁移。

### 版本与复现边界

- 参考实现 `.repo_source`：`https://github.com/YosefLab/cytovi-reference-implementation`，提交 `7b77adb0ec10962008bfe0bc0281311254e61d54`。
- `pyproject.toml` 声明包版本 `0.0.1`、Python `>=3.10`、`scvi-tools>=1.3`；工作区还有测试与按 Figure 1–5 组织的独立 reproducibility repo。
- 代码 URL 元数据与 pyproject 中历史主页 URL 不同，应以采集记录和当前工作区快照为复现来源。
- 部分原始/临床数据受申请、伦理或作者提供限制；FlowJo 门控、补偿与 cofactor 也难由 Python 脚本完全重现。
- 本轮重读论文 Markdown、56 页 PDF 图/图注、补充证据、CodeGraph 与直接源码；未重建环境、运行测试/训练或重画论文结果。

### 一句话总结

CytoVI 用带 batch/协变量条件的概率 VAE 把不同抗体技术和 panel 投到共享 latent，通过 backbone-only encoder、全 marker decoder 和 masked likelihood 学习缺失蛋白分布，并以 posterior uncertainty 支持插补与临床迁移；结果强度取决于预处理、panel overlap、参考覆盖和批次–生物混杂。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## CytoVI Summary

### Motivation & Novelty

#### Biological Problem

Flow cytometry, mass cytometry (CyTOF), and CITE-seq collectively constitute the most widely used quantitative profiling technologies in immunology, generating billions of single-cell measurements across thousands of patients and studies. However, the resulting data are analyzed in isolation because:

1. **Batch effects** prevent joint analysis even within the same technology
2. **Panel heterogeneity** — different studies measure different proteins — makes accumulation of knowledge across studies impossible
3. **Cross-technology integration** requires reconciling fundamentally different measurement scales and missing modalities

#### Limitations of Existing Approaches

- **cyCombine** (Pedersen et al., *Nature Communications*, 2022): Requires data standardization (z-score/rank transform), does not natively handle overlapping panels, batch correction only
- **Harmony** (Korsunsky et al., *Nature Methods*, 2019): General single-cell integration, no protein imputation, performs poorly with min-max-scaled cytometry data
- **TotalVI** (Gayoso et al., *Nature Methods*, 2021): Designed for CITE-seq, not cytometry; uses negative-binomial likelihood inappropriate for transformed cytometry data; no imputation for missing panels
- **InfinityFlow** (Becht et al., *Science Advances*, 2022): Machine-learning-based imputation for flow cytometry, requires matched reference data, not probabilistic

None of these methods simultaneously perform batch correction, panel imputation, differential expression, label-free differential abundance, and transfer learning under a unified probabilistic framework.

#### What CytoVI Contributes

1. **Unified VAE** with Gaussian/Beta likelihood appropriate for arcsinh-transformed cytometry data (validated empirically)
2. **Flexible prior**: Isotropic Gaussian or mixture-of-Gaussians (MoG) with optional label-weighting for semi-supervised integration
3. **Overlapping panel imputation** via masked reconstruction loss and counterfactual decoding — the decoder learns to reconstruct the full protein union even when only shared proteins enter the encoder
4. **Adversarial training** automatically activated for multi-panel scenarios to encourage panel-invariant latent spaces
5. **Label-free differential abundance** based on aggregate posterior distributions per sample — requires no a priori cell type annotation
6. **Transfer learning via scArches** — new patients are embedded via a single forward pass, enabling scalable clinical deployment
7. Integrated into **scvi-tools** (Gayoso et al., *Nature Biotechnology*, 2022) with multi-GPU support and AnnData compatibility

---

### Method Overview

CytoVI is a variational autoencoder (VAE) trained on arcsinh-transformed and min-max-scaled protein expression matrices. The encoder maps each cell's protein expression (or backbone proteins for overlapping panels) to a low-dimensional Gaussian posterior $q(z|x)$. The decoder reconstructs the full protein union from the latent vector conditioned on batch identity.

**Prior**: A learnable mixture of $K=d$ Gaussians (default), where $d = \lfloor P/2 \rfloor$ clamped to [10, 20]. Cell type labels optionally bias the MoG mixing weights ($\lambda = 10$) for semi-supervised integration.

**Noise model**: Gaussian likelihood (default) or Beta likelihood (for strictly [0,1]-scaled data).

**Training**: Adam optimizer, KL annealing over 400 epochs, batch size 128, early stopping with patience 30. KL divergence computed analytically for isotropic Normal prior; via Monte Carlo (10 samples) for MoG prior.

**Imputation** of missing proteins: counterfactual decoding — encode from shared features, decode with target batch identity. The decoder was trained to predict all proteins, so missing-protein reconstruction is a natural consequence of the generative model.

**Differential abundance**: Per-sample aggregate posteriors are formed by averaging cell-level posteriors. Log-ratios between disease and control groups yield cluster-free enrichment scores that can be clustered to identify disease-associated cell states.

**Transfer learning**: New query samples are passed through the frozen reference encoder (scArches integration), yielding batch-corrected embeddings without retraining. Cell type labels and continuous covariates are imputed via KNN (k=20) in the shared latent space.

---

### Evaluation

#### Datasets

| Dataset | Technology | N cells | P proteins | Used for |
|---------|-----------|---------|------------|---------|
| Nunez et al. (2023, *Nat Immunol*) | Full-spectrum flow cytometry | 100,000 | 35 | Baseline PPC, batch integration, imputation benchmark |
| Ingelfinger et al. (2022, *Nature*) | Mass cytometry (CyTOF) | 100,000 | 36 | PPC, cross-technology integration |
| Hao et al. (2021, *Cell*) | CITE-seq | 1 donor | 228 | PPC |
| Kreutmair et al. (2021, *Immunity*) | Full-spectrum flow cytometry | 100,000 | 30 | Panel integration (15 backbone) |
| Glass et al. (2020, *Immunity*) | Mass cytometry, 12 panels | 48,000 B cells | 350 (union) | B cell atlas imputation |
| Roider et al. (2024, *Nat Cell Biol*) | Flow cytometry + CITE-seq | 63 patients (BNHL) | 12+8 overlap | DA analysis, γδ T cell discovery |
| Clinical CLL cohort (Basel) | 10-color flow cytometry | 95 patients | 10 | CLL diagnosis + transfer learning |

#### Metrics

- **PPC** (Posterior predictive checks): Mean absolute error, Pearson's r, Spearman's r of coefficient of variation (CV) across proteins and cells
- **scIB metrics**: Batch correction (batch mixing ASW, kBET, graph connectivity) + bio conservation (cell type ASW, ARI, NMI) aggregated into consensus score
- **Imputation**: Pearson's r between imputed and held-out expression; AUC-ROC for binary marker positivity
- **Uncertainty**: Correlation between imputation std and imputation error
- **Clinical**: Pearson's r (CLL frequency vs. hematologist annotation), AUC-ROC for CLL classification (5-fold CV)

#### Key Results

- **PPC**: CytoVI (Gaussian, arcsinh+scaled) outperforms Factor Analysis baseline across all three technologies; Pearson's r ≈ 0.85–1.00 for CV across features
- **Batch correction**: CytoVI outperforms cyCombine and Harmony across all three preprocessing strategies; uniquely handles min-max-scaled data which other methods fail on
- **Imputation**: Superior to cyCombine and KNN; Pearson's r > 0.9 for lineage markers (CD3, CD4, CD14), >0.6 for activation markers (Ki67, CD103); uncertainty estimate strongly correlates with actual error
- **B cell atlas**: Integrated 350 proteins across 12 panels from 24 samples; identified class-switching-associated proteins (CD62L, CD71, CD100) along differentiation trajectory
- **BNHL**: Discovered a γδ T cell subset (KLRG1+, CD31+, CD69+, PD1+, TIM3+) enriched in DLBCL/MCL patients via label-free DA — not reported in original study; confirmed by CITE-seq transcriptome imputation
- **CLL clinical**: Reference model (20 patients) enables automated detection of CLL cells in query patients; Pearson's r = 0.69, p=3.76e-06 (query dataset N=35, Fig 5I); AUC-ROC = 0.74±0.09 for minimal residual disease detection (including challenging low-burden cases)

---

### Reproducibility

**Rating: 3 / 5**

**Justification**:
- Code is released as open-source Python library integrated into scvi-tools (pip-installable), well-documented with examples
- Reference implementation at https://github.com/YosefLab/cytovi-reference-implementation
- Reproducibility scripts at https://github.com/YosefLab/cytovi-reproducibility (organized by figure)
- Most datasets are publicly accessible (GEO, Flow Repository, Figshare, EGA) — but raw clinical CLL data requires request, and two datasets (Nunez et al., Ingelfinger et al.) required author provision
- The paper is a bioRxiv preprint (as of April 2026) — not yet peer-reviewed
- Potential reproducibility challenge: arcsinh cofactor selection is technology/experiment-specific and not universally documented; different cofactor choices can substantially affect integration quality
- Potential challenge: cytometry data preprocessing in FlowJo (gating, compensation) before Python import is manual and non-reproducible
- scvi-tools version dependencies are managed via `pyproject.toml`

**Strengths**:
- Modular API consistent with scvi-tools ecosystem (familiar to single-cell community)
- `pp.merge_batches` automates the most error-prone preprocessing step (NaN mask creation)
- Transfer learning via existing scArches infrastructure reduces deployment friction

**Weaknesses**:
- No automated selection of arcsinh cofactor (user must know their technology conventions)
- Benchmark depends on manual cell type annotations that are not always provided with public datasets
- The CLL clinical dataset is institutional and requires ethical approval to access — clinical results not fully reproducible externally

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
