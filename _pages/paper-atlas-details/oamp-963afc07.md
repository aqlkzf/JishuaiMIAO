---
layout: default
permalink: /paper-atlas/oamp-963afc07/
title: "OAMP"
nav: false
description: "OrchAMP / OAMP 解决的是单细胞多模态 atlas 构建和跨模态查询问题：参考数据中同一批细胞有 ATAC、RNA、protein 等多个模态，但新查询细胞可能只测到一个模态。方法把高维 RNA/ATAC 建模为低秩信号加噪声，把低维 protein 建模为对低维潜变量的带噪线性观测，并用 orchestrated approximate message passing 在多个模态之间同步去噪。"
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
      <span>arXiv · 2024</span>
    </div>
    <h1>OAMP</h1>
    <p>Multimodal data integration and cross-modal querying via orchestrated approximate message passing</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2407.19030" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## OAMP / OrchAMP 方法中文解读

### 一句话概览

OrchAMP / OAMP 解决的是单细胞多模态 atlas 构建和跨模态查询问题：参考数据中同一批细胞有 ATAC、RNA、protein 等多个模态，但新查询细胞可能只测到一个模态。方法把高维 RNA/ATAC 建模为低秩信号加噪声，把低维 protein 建模为对低维潜变量的带噪线性观测，并用 orchestrated approximate message passing 在多个模态之间同步去噪。最终输出是拼接后的多模态细胞潜在表示，以及查询细胞在完整潜在空间中的 posterior center 和 prediction ball。

### 1. 生物学问题与建模目标

论文关注 PBMC 这类 matched single-cell multimodal 数据：同一个细胞可以有 chromatin accessibility、gene expression 和 surface protein。计算目标不是发现全新细胞谱系，而是构建一个能区分已知细胞状态的 multimodal latent atlas，并在查询细胞只观测到部分模态时给出带不确定性的 atlas 位置。

这个输出可用于 cell-state visualization、clustering、label transfer 和 uncertainty-aware querying。它不能直接证明新的生物机制；UMAP 和聚类指标只说明 atlas 与已有标签的一致性，真实数据中的 prediction-set 图也主要是定性案例，而不是大规模真实 holdout 校准实验。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| 高维模态矩阵 | $\bm X_h$ / `X_list[k]` | RNA、ATAC 等 $N\times p_h$ 矩阵 | `doc_method.md`, `doc_code.md` |
| 低维模态矩阵 | $\wt{\bm X}_\ell$ / `X_low_dim_list` | protein / targeted panel 的 $N\times \wt r_\ell$ 观测 | `doc_method.md`, `doc_code.md` |
| 细胞侧潜变量 | $\bm U_h$, $\wt{\bm U}_\ell$ | 每个模态对应的 cell-state latent coordinate | `claude_notes.md` |
| 特征侧载荷 | $\bm V_h$ | 高维模态的 feature programs / loadings | `doc_method.md` |
| 信号强度 | $\widehat{\bm D}_h$ | spiked-matrix 校正后的低秩因子强度 | `OrchAMP/simulation/Python_Scripts/pca_pack.py:75-100` |
| 低维载荷 | $\widehat{\bm L}_\ell$ | protein-like 模态的线性 loading estimate | `OrchAMP/simulation/Python_Scripts/preprocessing.py:207-229` |
| 联合细胞先验 | $\widehat{\mu}$ | 所有模态细胞潜变量的 joint GMM prior | `OrchAMP/simulation/Python_Scripts/complete_pipeline.py:174-203` |
| 特征先验 | $\widehat{\nu}_h$ | 每个高维模态单独的 feature-loading prior | `OrchAMP/simulation/Python_Scripts/emp_bayes.py:311-362` |
| atlas 输出 | concatenated $\widehat U$ | TEA-seq 中为 $6323\times75$ integrated embedding | `summary.md` |
| 查询输出 | $\widehat U$, $\mathcal C_\alpha$ | 查询细胞的 posterior center 与 Euclidean prediction ball | `doc_method.md` |

### 3. 方法主流程

1. 预处理 matched modalities：对 RNA/ATAC/protein 做 normalization、feature selection、centering/scaling。TEA-seq 示例保留 6,323 cells、5,000 ATAC features、2,000 RNA genes 和 40 proteins。
2. 对每个高维模态做 truncated SVD 和 spectral initialization，选择 rank，例如 TEA-seq 用 ATAC rank 15、RNA rank 20。
3. 用 spiked-random-matrix 公式估计 $\widehat{\bm D}_h$、alignment/noise parameters，并从低维 covariance 估计 $\widehat{\bm L}_\ell$。
4. 拟合 empirical-Bayes priors：细胞侧拟合一个 joint GMM $\widehat{\mu}$，高维特征侧为每个模态分别拟合 $\widehat{\nu}_h$。
5. 运行 OrchAMP iterations：每轮先做 feature-side denoising，再用 Onsager-corrected $Xv$ 更新 cell-side estimates，随后通过 joint subject denoiser 同步整合所有模态，最后用 Onsager-corrected $X^\top u$ 更新 feature-side estimates。
6. 拼接最终 subject factors 得到 atlas embedding；UMAP、Louvain 和 metrics 是下游评价，不是 AMP 模型本身。
7. 对 partially observed query cell，先用观测模态和 learned feature loadings 做 latent projection，再用 $\widehat{\mu}$ 条件化推断完整 latent vector，并给出 prediction ball。

### 4. 数学目标与直觉

高维模态模型为：

$$
\bm X_h = \frac{1}{\sqrt{N}}\bm U_h\bm D_h\bm V_h^\top+\bm W_h.
$$

这里 $\bm U_h$ 是细胞状态坐标，$\bm V_h$ 是该模态的特征载荷，$\bm W_h$ 是噪声。这个模型把 RNA/ATAC 的高维表达或可及性矩阵近似成低秩生物信号加 Gaussian noise。

低维模态模型为：

$$
\wt{\bm X}_\ell=\wt{\bm U}_\ell\bm L_\ell^\top+\wt{\bm W}_\ell.
$$

protein 这类低维 panel 不再有 feature-side AMP orbit，而是作为 joint subject denoiser 的直接观测进入。

OrchAMP 的核心更新是：

$$
\begin{aligned}
\bm v_{t,h} &= v_{t,h}(\bm V_{t,h};\widehat{\nu}_h),\\
\bm U_{t,h} &= \wb{\bm X}_h\bm v_{t,h}
-\gamma_h\bm u_{t-1,h}\left(\bm J^R_{t,h}\right)^\top,\\
\bm u_{t,h} &= u_{t,h}(\bm U_{t,1},\ldots,\bm U_{t,m},\wt{\bm X}_1,\ldots,\wt{\bm X}_{\wt m};\widehat{\mu}),\\
\bm V_{t+1,h} &= \wb{\bm X}_h^\top\bm u_{t,h}
-\bm v_{t,h}\left(\bm J^L_{t,h}\right)^\top.
\end{aligned}
$$

直觉上，$v_{t,h}$ 是每个高维模态自己的 feature denoiser，$u_{t,h}$ 是跨模态共享信息的 joint cell denoiser。$\bm J^L,\bm J^R$ 是 Onsager corrections，用来抵消迭代中重复使用噪声造成的偏差，使 state evolution 近似成立。

查询阶段的输出是：

$$
\mathcal C_\alpha=B_{r+\wt r}(\widehat U,\widehat b_\alpha).
$$

这不是单点 label transfer，而是在完整 latent space 中给出一个可信区域。若该区域集中在某个已知 cell-type cluster 内，查询标签较可信；若跨多个 cluster 或远离 reference atlas，则表示不确定或分布偏移。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| Spectral initialization 和 singular-value correction | `OrchAMP/simulation/Python_Scripts/pca_pack.py:41-100` | 对高维模态做 SVD、缩放 singular vectors、估计 corrected signal strengths | ✓ Exact |
| 低维 loading estimator | `OrchAMP/simulation/Python_Scripts/preprocessing.py:207-229` | covariance 减 identity，负特征值 clipping 后取 square root | ✓ Exact |
| Joint subject prior $\widehat{\mu}$ | `OrchAMP/simulation/Python_Scripts/complete_pipeline.py:174-203`; `emp_bayes.py:107-167` | 拼接 cell-side noisy embeddings 并拟合 GMM EB model | ✓ Exact |
| Separate feature priors $\widehat{\nu}_h$ | `complete_pipeline.py:191-194`; `emp_bayes.py:311-362` | 为每个高维模态独立拟合 feature-side GMM prior | ✓ Exact |
| Core OrchAMP update | `OrchAMP/simulation/Python_Scripts/amp.py:96-210` | 实现 feature denoise、joint subject denoise、Onsager-corrected updates | ✓ Exact |
| Query latent projection | `OrchAMP/simulation/Python_Scripts/complete_pipeline_pred.py:227-275`; `:345-386` | 用 learned $V$ 和 signal diagonal 对观测 query features 做 least-squares projection | ✓ Exact |
| Prediction radius / posterior sampling | `OrchAMP/simulation/Python_Scripts/pred_set.py:169-180`; `tea_seq_prediction.ipynb:cell 88-90` | synthetic code 计算 posterior quantile；真实 TEA-seq notebook 主要采样作图 | ~ Partial |
| TEA-seq/CITE-seq real-data workflow | `tea_seq/*.ipynb`, `cite_seq/*.ipynb`, plotting R scripts | notebook/R 脚本读取外部或预计算数据并导出图和指标 | ⚠ Notebook / ~ Partial |

代码可验证的是：simulation pipeline 对论文核心算法支持较强，包括 spectral correction、GMM denoisers、Onsager corrections、synthetic recovery 和 prediction-set calibration。代码未完全验证的是：一键 raw-data-to-paper 真实数据复现、所有 manuscript table 的 line-stable 生成路径、以及 TEA-seq/CITE-seq 查询图的系统性真实 coverage benchmark。

### 6. 结果如何解读

Synthetic recovery 实验显示，在论文设定的 dependent factor model 下，OrchAMP 通常优于 SVD，并在弱信号时通过跨模态 borrowing strength 获益；EB-PCA 在部分高 SNR 单模态恢复中可接近或超过 OrchAMP，因为 OrchAMP 需要估计更高维 joint prior。

Synthetic prediction-set 实验报告 95% prediction sets 的 coverage 约为 0.92-0.98，接近 nominal level。需要注意的是，论文文字说 radius 用 10,000 posterior samples，而 public `pred_set.py` 使用 `num_samples=100000`。

TEA-seq atlas 中，OrchAMP 在 silhouette、V-measure、ARI 上最好，MOFA+ 在 cLISI 上最好；UMAP 视觉上三种方法都能分离主要 PBMC 类型，因此结论应读作 competitive atlas construction 加 formal uncertainty machinery，而不是视觉上压倒性优胜。TEA-seq 查询图对 DnT、CD8 effector、pre-B 三个 held-out cells 展示 500 个 95% prediction-set samples，多数落在正确 cell-type 区域，但这仍是定性展示。

CITE-seq benchmark 中，OrchAMP 的 V-measure 和 cLISI 最好，WNN 的 silhouette 和 ARI 最好。rank ablation 显示 atlas 结构对附近 rank 设置相对稳定，但不同指标偏好的 rank 不完全一致。

### 7. 局限性与未验证部分

- 理论依赖 Gaussian low-rank model、i.i.d. row prior、BBP-supercritical singular values、合适的 prior class 和 reference/query 同分布；真实 count data 只能通过 preprocessing 近似满足。
- 真实数据 workflow 依赖外部下载、未提交的大型中间文件、notebook 执行状态和用户本地绝对路径，不是 portable command-line pipeline。
- 代码中未找到完整 public raw-data-to-paper CITE-seq/TEA-seq pipeline；plotting scripts 多读取已存在 CSV/H5AD/embedding 文件。
- 真实 query 结果只有三个 held-out TEA-seq cells 的 qualitative visualization，不能替代广泛的真实数据 calibration 或 label-transfer accuracy 评估。
- 当前 `doc_code.md` 中有多处 `Exact`/`Partial` 行缺少严格 `file:startLine-endLine` 范围；虽然正文包含许多 line anchors，Reviewer 应重点检查这些行是否达到当前发布门槛。
- 输出更适合作为 hypothesis generation 和 uncertainty-aware label-transfer 辅助，而不是实验验证结论。

### 8. 快速阅读路线

1. 先读 `summary.md`：快速了解问题、方法、评价和复现等级。
2. 再读 `doc_method.md`：按公式和流程理解 OrchAMP atlas construction 与 query prediction set。
3. 读 `doc_code.md`：检查论文步骤与 public code 的对应关系、缺口和 reproducibility caveats。
4. 读 `figure_analysis.md`：理解每个主图支持的结论和不支持的结论。
5. 最后读 `claude_notes.md`：查看完整 evidence ledger、equation/claim map、assumption ledger 和代码核查依据。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## OAMP / OrchAMP Summary

### Paper

**Title:** Multimodal data integration and cross-modal querying via orchestrated approximate message passing

**Method:** OrchAMP / OAMP

**Venue and year:** arXiv preprint, 2024

**Code:** `https://github.com/Sagnik-Nandy/OrchAMP`, analyzed at commit `b23af4c061bf8218b58de0097cbfa83c0fc760fd`

### Motivation

Single-cell multimodal datasets measure the same cells through different feature systems, such as ATAC accessibility, RNA expression, and surface proteins. Existing integration methods can build useful atlases, but they often treat integration and query mapping as heuristic embedding tasks. The paper targets a more statistical formulation: construct a multimodal latent atlas and provide a prediction set for the latent position of a partially observed query cell.

The key biological use case is uncertainty-aware label transfer. A new cell may be measured in only one modality, but the reference atlas was built from several modalities. OrchAMP uses the learned dependence among modality-specific latent factors to infer the query's full latent representation and quantify how concentrated or ambiguous the inferred atlas location is.

### Novelty

The paper generalizes empirical-Bayes approximate message passing from a single spiked matrix to multiple dependent modalities with unequal ranks and mixed high-/low-dimensional observations. High-dimensional modalities such as RNA and ATAC have their own feature-side AMP orbits, while all modalities share a joint subject-side empirical-Bayes denoiser.

The second contribution is cross-modal querying with asymptotically valid prediction sets. Rather than returning only a nearest-neighbor label or point embedding, the method estimates a posterior center and an Euclidean prediction ball for the query's full latent representation.

The paper positions OrchAMP against WNN / Seurat v4 (Cell, 2021), MOFA+ (Genome Biology, 2020), totalVI (Nature Methods, 2021), EB-PCA (JRSS Series B, 2022), JIVE (Annals of Applied Statistics, 2013), and classical SVD/PCA baselines.

### Method Overview

For each high-dimensional modality, OrchAMP models the observed matrix as low-rank signal plus Gaussian noise. Low-dimensional modalities are modeled as direct noisy linear observations of low-dimensional latent factors. The latent subject factors across modalities are dependent through a joint prior, which is the statistical object that lets the method borrow information across modalities.

The pipeline is:

1. Preprocess matched multimodal matrices by normalization, transformation, feature selection, and centering.
2. Choose ranks and compute spectral initialization for each high-dimensional modality.
3. Estimate signal strengths, alignment/noise parameters, and low-dimensional loading matrices.
4. Fit empirical-Bayes priors: one joint GMM prior for subject factors and separate GMM priors for high-dimensional feature loadings.
5. Run Onsager-corrected OrchAMP iterations with feature-side denoising, joint subject-side denoising, and low-dimensional factor updates.
6. Concatenate final subject factors into the multimodal atlas.
7. For a query cell, project observed modality features into latent coordinates, condition on the learned joint prior, and form a prediction ball.

### Evaluation

**Synthetic signal recovery:** The paper simulates two high-dimensional modalities plus one low-dimensional modality with \(N=10000\), \(\gamma_1=\gamma_2=0.25\), \(\lambda\in\{2.0,2.4,2.8\}\), \(\rho\in\{0.8,0.9,1.0\}\), 4-component GMM priors, 25 AMP iterations, and 50 replicates. OrchAMP and EB-PCA both beat SVD across settings. OrchAMP gains most when signal is weak, but EB-PCA can match or exceed it in some higher-SNR within-modality recovery settings because OrchAMP estimates a higher-dimensional joint prior.

**Synthetic prediction sets:** The paper evaluates 95% prediction-set coverage with \(N\in\{2000,3000,4000\}\), \(\lambda\in\{5,7,9\}\), \(\rho=0.8\), and 50 replicates. Reported coverage ranges from 0.92 to 0.98, close to nominal. The public code uses 100000 posterior samples in `pred_set.py`, while the paper text says 10000 samples.

**TEA-seq atlas:** The real-data TEA-seq example uses 6,323 PBMC cells with ATAC (5,000 features), RNA (2,000 features), and protein (40 features). OrchAMP uses ranks 15 for ATAC and 20 for RNA, 4 GMM components for the joint subject prior, 11 for the ATAC loading prior, 6 for the RNA loading prior, and 15 iterations. The integrated atlas has 75 dimensions. Compared with WNN and MOFA+, OrchAMP has the best silhouette (0.395), V-measure (0.762), and ARI (0.634), while MOFA+ has the best cLISI (1.181).

**TEA-seq querying:** The paper holds out one double-negative T cell, one CD8 effector cell, and one pre-B cell, rebuilds the atlas on 6,320 cells, and visualizes 95% prediction sets from ATAC-only, RNA-only, and protein-only queries using 500 sampled points. The prediction sets generally map to the correct cell-type regions, but this is qualitative real-data evidence rather than a broad real-data coverage benchmark.

**CITE-seq benchmark:** The appendix uses 10,000 CITE-seq PBMC cells with RNA and protein, retaining 5,000 variable genes and 30 protein markers after preprocessing/Harmony correction. OrchAMP uses RNA rank 50 and GMM component counts 8 for the joint subject prior and 4 for the feature prior. Against WNN, totalVI, and MOFA+, OrchAMP has the best V-measure (0.796) and cLISI (1.186), while WNN has the best silhouette (0.393) and ARI (0.622).

### Reproducibility

**Rating: 3/5.**

The core algorithm is publicly available and the simulation code maps well to the paper: spectral correction, GMM empirical-Bayes denoisers, low-dimensional loading estimation, Onsager-corrected OrchAMP updates, EB-PCA/SVD baselines, and prediction-set simulation scripts are all present. This is enough to understand and re-run the main algorithmic components with work.

Reproducibility is limited by the real-data workflow. Raw TEA-seq and CITE-seq data are external downloads, large intermediates and saved embeddings are not committed, several scripts assume user-specific absolute paths, and real-data analyses are split across notebooks plus R plotting scripts rather than a portable command-line pipeline. The public code verifies the existence of the manuscript workflows, but it is not a one-command raw-data-to-paper reproduction.

### Main Caveats

- The theory depends on Gaussian low-rank models, i.i.d. row priors, BBP-supercritical singular values, suitable empirical-Bayes prior classes, and same-distribution reference/query assumptions.
- Real single-cell count data only approximately match the model after preprocessing, feature selection, and centering.
- UMAP and clustering metrics support atlas quality but do not prove new biological discovery.
- Real-data prediction-set figures show three held-out cells qualitatively; broad real-data calibration is not established.
- The code release is strongest for simulations and method mechanics; real-data reproduction requires manual data download, path edits, notebook execution, and generated intermediates.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
