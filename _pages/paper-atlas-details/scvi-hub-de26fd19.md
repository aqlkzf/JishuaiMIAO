---
layout: default
permalink: /paper-atlas/scvi-hub-de26fd19/
title: "scvi-hub"
nav: false
description: "scvi-hub 解决的不是“怎样再设计一个 scVI 变体”，而是一个更靠后的基础设施问题：一个实验室训练好的 scVI、scANVI、totalVI 或 DestVI 模型，怎样连同必要的数据表示、元数据和质量证据交给另一个实验室复用。 论文把模型共享拆成两侧。贡献者训练参考模型，检查模型是否复现了原数据的重要统计结构，把大数据压缩成可随模型分发的表示，再上传模型与模型卡；"
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
      <span>Representation Models</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>scvi-hub</h1>
    <p>Scvi-hub: an actionable repository for model-driven single-cell analysis</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02799-9" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scvi-hub：把训练好的单细胞生成模型变成可检查、可复用的研究对象

### 先说清楚：它不是一种新的生成模型

scvi-hub 解决的不是“怎样再设计一个 scVI 变体”，而是一个更靠后的基础设施问题：一个实验室训练好的 scVI、scANVI、totalVI 或 DestVI 模型，怎样连同必要的数据表示、元数据和质量证据交给另一个实验室复用。

论文把模型共享拆成两侧。贡献者训练参考模型，检查模型是否复现了原数据的重要统计结构，把大数据压缩成可随模型分发的表示，再上传模型与模型卡；使用者搜索和下载模型，先判断参考模型是否适合自己的问题，再做参考数据分析、查询映射、标签迁移或空间解卷积。因而 scvi-hub 的核心贡献是“可发现、可评估、可行动”的模型仓库工作流，而不是新的潜变量目标函数。

### 贡献者一侧：模型、证据和数据表示一起发布

一个可复用条目不应只有权重文件。论文中的条目还包括模型类型、训练数据和基因集合等元数据、面向读者的模型卡，以及可选的原始或精简 AnnData。`HubModel` 负责把模型和数据作为一个对象组织并推送或拉取；`HubMetadata` 与模型卡帮助使用者知道模型来自哪里、适合什么输入。这里的实现位于外部 `scvi-tools`，不是本工作区的复现仓库。

发布前的关键动作是 posterior predictive check（PPC）。对输入计数 $x$，已训练模型通过后验和生成分布产生复制数据

$$
x^{\mathrm{rep}} \sim p_\theta(x\mid z,\ell),\qquad z\sim q_\phi(z\mid x),
$$

再比较 $x$ 与 $x^{\mathrm{rep}}$ 的统计量。其问题不是“生成图看起来像不像”，而是“模型是否保留了下游分析真正会用到的变异与差异表达结构”。

### 数据精简：保存模型需要的后验，而不是保留全部计数

对于已经训练好的 scVI 类模型，很多参考端任务不需要再次把每个细胞送入编码器。论文的数据精简保留每个细胞的潜变量后验参数，例如

$$
q_\phi(z_n\mid x_n)=\mathcal N(\mu_n,\operatorname{diag}(\sigma_n^2)),
$$

以及生成时需要的文库大小信息；原始计数矩阵被清空并用稀疏形式保存。之后可从保存的 $(\mu_n,\sigma_n^2)$ 采样 $z_n$，绕过编码器进入生成器。这样仍可得到潜表示、模型表达量和后验预测样本，却大幅降低磁盘、下载和内存开销。论文给出的 Census 实例从约 500 GB 降至 30 GB，下载由数小时缩短到 30 分钟以内。

这是一种有意的有损压缩。它依赖具体模型及其特征集合，不能恢复被移除的原始计数，也不适合必须重做原始质控、重新选基因或用原始计数拟合另一模型的任务。精简数据让“用这个模型继续分析”更容易，并不等于保存了原数据的所有用途。

复现代码的 `suppl_fig1_minified_benchmark.ipynb` 和 `suppl_fig1_profile_memory.ipynb` 测量内存与时间；后者还实际调用 `HubModel.pull_from_huggingface_hub(...)`。真正的精简逻辑仍在安装的 `scvi-tools` 中。

### 模型批判：比较模型生成数据与观测数据

#### 1. 细胞和基因层面的变异系数

对一组计数 $y_1,\ldots,y_m$，变异系数为

$$
\mathrm{CV}(y)=\frac{\operatorname{sd}(y)}{\operatorname{mean}(y)}.
$$

逐细胞计算时，它衡量每个细胞在基因维度上的离散程度；逐基因计算时，它衡量一个基因在细胞间的离散程度。PPC 分别在原始计数和生成计数上计算 CV，再报告 MAE、Pearson、Spearman 和 $R^2$。`ppc_plot_utils.py:71-159` 直接读取 `cv_cell` 或 `cv_gene`，计算这些量并画出拟合线与恒等线。

论文讨论中提出细胞级 CV 的 $R^2>0.4$ 作为实践目标，但明确把 criticism 定位为同一数据上比较候选模型、帮助判断，而不是越过某条线就证明模型正确。扩展图的心脏模型实验更能说明正确用法：训练集很好、验证集明显变差可能是过拟合；训练和验证都差可能是欠拟合或潜空间容量不足。

#### 2. 差异表达是否被保留

论文还分别在观测计数和后验预测样本上做 one-versus-all 差异表达，并比较：前 100 个基因集合的 F1、所有基因 log-fold change 的 Pearson/Spearman 相关、以及以原始数据显著基因为真值的 auPRC。HLCA 图 2 使用 $P<0.2$，而代码/方法中的默认显著性阈值是另一配置，因此不能把 0.2 当作平台固定默认值。

`ppc_plot_utils.py:190-278` 从 `diff_exp/summary` 取出这些量；摘要图保留 F1、两种 LFC 相关和 auPRC，并不展示已计算的 ROC AUC。论文建议 marker overlap F1 超过 0.8 作为经验目标，同样不是跨数据集的质量保证。

#### 3. PPC 能证明什么，不能证明什么

PPC 能发现模型没有复现观测分布的症状，也能比较欠拟合、过拟合和参考域不匹配。扩展图显示 HLCA 对肺和气管的契合优于无关组织，totalVI 的 RNA 与蛋白模态也可能有不同表现。但统计吻合不自动证明批次效应已经正确消除、稀有细胞状态真实存在，或后续生物学因果结论成立；这些仍需独立标签、设计与实验验证。

### 使用者一侧：参考分析、查询映射和标签输注

#### 参考模型直接分析

图 2 从 scvi-hub 下载 HLCA 的 scANVI 模型和精简数据，不重新训练参考模型，就能画潜空间、生成模型表达、做 CV 与差异表达 PPC，并比较免疫细胞 marker。这展示的是“已发布模型作为分析对象”的最短路径。

#### scArches 查询映射

当新查询数据 $X_q$ 到来时，scArches 通过 `SCANVI.load_query_data` 从参考权重初始化查询模型，只调整查询适配部分，使查询细胞进入参考潜空间而不重训数百万参考细胞。肺气肿 notebook 在 `fig3_hlca_emphysema.ipynb:328` 建立查询模型；论文方法给该案例 200 个 surgery epochs，并使用早停。

映射后还必须重新做 criticism：新数据可能不在参考分布内。图 3 的肺气肿细胞映射到 HLCA 后用于标签迁移、Milo 差异丰度与差异表达；图 4 把 CAR T 数据映射到超过 3000 万人细胞的 Census 模型，说明精简模型和 query surgery 如何把图谱级资源带到普通分析流程。

#### KNN 标签迁移与不确定度

复现 notebook 用 PyNNDescent 在参考潜空间建立近邻索引，将查询细胞到参考邻居的距离转为 affinity，并按类别累加权重。若类别 $c$ 的归一化权重为

$$
p(c\mid q)=\sum_{i\in N(q)} w_i\,\mathbf 1(l_i=c),
$$

则预测为 $\arg\max_c p(c\mid q)$，不确定度为

$$
u(q)=1-\max_c p(c\mid q).
$$

肺气肿分析为混淆矩阵保留 $u\leq0.4$ 的细胞；notebook 的实际输出显示过滤 4.50%，论文正文写作 4.8%。这是该案例的筛选选择，不是 scvi-hub 的全局默认阈值。

“标签输注”把方向反过来：用一个更专门、标签更细的查询集给大型参考图谱补充标签。图 3 用跨器官免疫参考细化 HLCA，图 4/扩展图进一步把 Treg 等专门标签输注到 Census。方向反转并没有消除域偏移；输注结果仍要用 marker、聚类和差异表达检查。

### 从图中怎样读出论文的证据链

- 图 1 是合同图：贡献者训练、批判、精简并发布；消费者搜索、下载、检查并分析。它解释平台组件之间的关系。
- 图 2 是参考端闭环：HLCA 的模型表达与原始表达对照，细胞级 CV $r^2=0.84$，并用 DE 指标和 marker 检查模型保留的结构。
- 图 3 是查询端闭环：肺气肿映射支持差异丰度/表达分析；免疫标签输注展示标签可沿相反方向传播。
- 图 4 是规模证据：精简 Census 模型承载 CAR T 查询映射，细胞级 CV $r^2=0.65$，随后做标签细化、Milo 与 CD8 亚群分析。
- 扩展图 5 用训练/验证分离识别欠拟合和过拟合；扩展图 6 检查参考组织适配性；扩展图 7 将 PPC 扩展到 totalVI 的 RNA/蛋白；扩展图 8 展示 DestVI 空间解卷积；扩展图 9 比较泛免疫参考与 Census 的标签结构。

这些图共同支持“模型可共享之后仍然要被批判”。它们不是证明一个模型对任何新数据都能安全复用。

### 本地代码究竟覆盖了多少

本工作区固定到复现仓库 commit `bb19c43d7e0c19cc0a2d18be8632f09feb2f5367`。它以 Jupyter notebooks 为主，CodeGraph 没有得到有效的符号图，因此代码证据来自直接读取 notebook JSON 和 `ppc_plot_utils.py`。

覆盖较直接的部分包括 HLCA PPC、scArches 查询映射、PyNNDescent 标签迁移、Census/CAR T 分析、Milo、DestVI 和精简基准。`fig2_hlca_only_reference.ipynb:448`、心脏 criticism notebook 的多处单元把 `n_samples=2` 传给 PPC；这是论文复现的计算选择，样本数很少，不应被解释成稳定性已经充分评估。

平台核心类、三维稀疏后验预测存储、模型上传/下载和实际 minify 实现来自外部 `scvi-tools`。本地 notebooks 确实展示了部分 `HubModel` 拉取，但不能仅凭这个仓库审计核心库的全部行为。仓库也没有环境锁文件，而且若干 notebook 含作者机器的绝对路径，因此从干净环境端到端重跑仍需补依赖版本、数据下载与路径配置。

### 最稳妥的使用顺序

1. 先读模型卡，确认物种、组织、模态、基因集合、训练批次和模型版本。
2. 下载模型与精简数据，先在参考数据上复核 PPC 与已知 marker。
3. 对查询数据做特征对齐和 scArches 映射，再在查询上重新做 criticism。
4. 查看潜空间混合、CV/DE 指标、标签不确定度和独立 marker；不要只看 UMAP。
5. 只有在参考适配性和标签质量都通过后，才做差异丰度、差异表达或标签输注。
6. 对关键生物学结论回到原始计数、样本层重复和实验验证；不要把模型生成表达或标签迁移本身当作因果证据。

scvi-hub 的价值最终不在“下载预训练模型”这一动作，而在把来源说明、模型质量、数据体积和下游用途放进同一个可追踪工作流。它降低了模型复用的工程门槛，但没有取消对模型适配性和生物学有效性的判断责任。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## scvi-hub Summary

### Motivation & Novelty

#### Biological Problem

The explosion of single-cell omics atlases (10s of millions of cells) has created a reuse bottleneck: raw reference datasets are too large to download (HLCA: ~several GB; CZI Census: 500 GB), require specialized HPC to process, and rely on each group reinventing integration pipelines. Transfer learning with parametric models (scVI/scANVI) can solve this — a trained model encodes the reference in its weights — but there was no standardized infrastructure for sharing models, evaluating their quality, or applying them to new data.

#### Limitations of Prior Approaches

| Prior Approach | Limitation |
|---|---|
| Seurat v3 integration (*Nat. Biotechnol.* 2019, Butler et al.) | Non-parametric (mutual nearest neighbors); requires downloading full reference |
| FastMNN (*Nat. Biotechnol.* 2018, Haghverdi et al.) | Non-parametric; no generative model → cannot simulate expression |
| scVI / scArches (*Nat. Methods* 2018, Lopez et al.; *Nat. Biotechnol.* 2022, Lotfollahi et al.) | Methods exist, but no platform for sharing trained models or standardized quality control |
| Symphony (*Nat. Commun.* 2021, Kang et al.) | Reference compression via anchor cells; limited to embedding, no expression generation |
| scPrint (Preprint 2024) | Foundation model approach; less efficient than scVI-based models per [46] |
| Geneformer (*Nature* 2023, Theodoris et al.) | Requires GPU, does not generate count data for downstream analysis |
| scGPT (*Nat. Methods* 2024, Cui et al.) | Requires GPU; large compute footprint |

#### Unique Contributions

1. **scvi-hub platform**: First standardized repository for pretrained single-cell probabilistic models, integrated with Hugging Face Model Hub (Git versioning, search, Model cards)
2. **Data minification**: Novel compression scheme storing only latent posterior parameters (z_mean/z_var) instead of raw counts — 94% storage reduction for Census (500 GB → 30 GB)
3. **scvi.criticism module**: Standardized, label-agnostic model evaluation via posterior predictive checks (CV + DE metrics) usable before and after upload
4. **Label infusion**: Bidirectional label transfer — propagate high-resolution query annotations back to the reference atlas, enriching atlas annotations
5. **API design**: Lazy-loading HubModel class that does not trigger data download until accessed; single-line switch from minified to raw data

---

### Method Overview

scvi-hub is a platform, not a new algorithmic method. It wraps existing scvi-tools probabilistic models (scVI, scANVI, totalVI, DestVI, and any model built with the scvi-tools developer API) with:

**Sharing infrastructure** (scvi.hub module):
- `HubModel` class: wraps a pretrained scvi-tools model + AnnData for upload/download
- `HubModelCardHelper`: auto-generates standardized documentation (Model card)
- `HubMetadata`: structured metadata schema (tissue, species, model type, training details)
- Storage backends: Hugging Face (Git-versioned, public) or AWS S3 (private/custom)

**Data minification**:
- Store encoder output {z_mean, z_var} in `adata.obsm` (2 × D floats per cell)
- Zero count matrix, store as CSR sparse (near-zero disk cost)
- Generation bypasses encoder → faster inference on CPU
- One function call restores full raw data via CELLxGENE Census API when needed

**Model evaluation** (scvi.criticism module):
- Posterior Predictive Check (PPC) class: generates `n_samples` posterior predictive samples as 3D sparse tensor (n_cells × n_genes × n_samples)
- Cell-wise CV correlation: target R² > 0.4
- Gene-wise CV correlation: additional fidelity check
- DE metric: F1 of top-100 marker genes, LFC Pearson/Spearman, auPRC (target F1 > 0.8)
- Label-agnostic fallback: Leiden clustering when cell-type labels are unavailable

**Consumer workflows**:
1. Reference-only: download minified data + model → generate expression → UMAP, DE, correlation
2. Query mapping: scArches surgery on query data → joint embedding → KNN label transfer (with uncertainty)
3. Label infusion: reverse KNN (query → reference) to enrich reference annotations
4. Spatial deconvolution: download CondSCVI/Stereoscope model → apply to Visium data

---

### Evaluation

#### Datasets

| Dataset | Cells | Task | Reference |
|---|---|---|---|
| HLCA (Human Lung Cell Atlas) | ~580k | PPC validation + emphysema query | Sikkema et al., *Nat. Med.* 2023 |
| Heart Cell Atlas | ~500k | Model quality comparison (4 models) | Litviňuková et al., *Nature* 2020 |
| Tabula Sapiens (epithelial) | ~200k | Reference suitability check (out-of-distribution) | Jones et al., *Science* 2022 |
| Emphysema dataset | ~6 donors | Query-to-reference mapping + DA | Wang et al., *Immunity* 2023 |
| Cross-tissue immune atlas | Millions | Label infusion to HLCA | Domínguez Conde et al., *Science* 2022 |
| COVID PBMC CITE-seq | ~800k | totalVI multimodal PPC | Stephenson et al., *Nat. Med.* 2021 |
| CZI CELLxGENE Census | >30M | Census model scalability | CZI, 2023 |
| CAR T cell dataset | ~24 donors | Census query mapping + DA | Deng et al., *Nat. Med.* 2020 |
| 10x Visium prostate | Spots | DestVI deconvolution | 10x Genomics data release |

#### Key Metrics and Results

**Data minification**: CELLxGENE Census 500 GB → 30 GB minified (94% reduction); download time: hours → <30 minutes; inference time: 50%+ faster at large batch sizes

**PPC model quality**:
- Well-trained HLCA scANVI: high cell-wise CV R² for both train and validation cells
- 5-epoch underfitted model: low R² on both
- Overfit model (5000 epochs, 100 latent dims): high R² on train cells, lower on validation
- 2-latent-dim model: low CV and DE metrics
- Leiden-cluster-based DE: comparable PPC metrics to cell-type-label-based DE

**Emphysema query**:
- Well-integrated joint embedding (scArches)
- Label transfer identified sub-types (venous systemic/capillary, arterial, aerocyte) not in original study
- Fibroblast upregulation: CXCL1/CXCL2/CXCL8 (neutrophil recruitment), CCL2/CSF3 (monocyte) — new biological finding not in original publication
- Validated: these results NOT reproducible with pseudobulk DE alone or full model retraining from scratch

**CAR T census analysis**:
- Terminally differentiated CD8+ T cells → reduced CAR T response (FDR < 10%)
- Tregs → reduced response (FDR < 10%; aligns with Good et al., *Nat. Med.* 2022)
- Identified CCR7+/MKI67+/GZMB+ CD8 subset negatively associated with CRS
- Unexpected: CCR7+/CCL17+/CCL22+ dendritic cells in infusion products

**Reference suitability**: Out-of-distribution tissues (bladder, cornea, kidney) show near-zero CV correlation when mapped to HLCA — demonstrates that PPC correctly detects reference mismatch

#### Biological Validation

- Emphysema fibroblast chemokines: validated with existing neutrophil/macrophage emphysema literature
- Treg identification in Census: 300,000 Tregs identified; activated Treg state linked to cancer across diverse solid tissues
- COVID-19 CD8 T exhaustion: LAG3/CD38/TIMD4/HAVCR2 upregulation, consistent with targeted COVID-19 T cell studies

---

### Reproducibility

**Rating: 3/5**

**Justification**: All notebooks are provided and code reproduces specific figures, but:
- Core scvi-hub functionality (`HubModel`, `HubModelCardHelper`, `HubMetadata`) lives in scvi-tools, not in this repo
- Census model training not fully reproducible (requires 500 GB Census download; CZI model uses different hyperparameters than custom training run in paper)
- No environment file (`requirements.txt`, `environment.yml`) — package versions unspecified
- Notebooks were developed on a specific machine (`/home/cane/Documents/yoseflab/...` hardcoded paths in fig2 notebook) → require path updates
- HLCA and Census datasets access via CELLxGENE requires active API; data was frozen at 2023-12-15 Census version

**Practical notes**:
- Install: `pip install scvi-tools huggingface_hub pynndescent milopy pydeseq2 decoupler-py`
- For GPU: scVI training benefits from GPU but inference runs on CPU
- Common pitfall: minified AnnData models require specific scvi-tools version matching the model file; use `revision` argument to pin versions
- Models available at https://huggingface.co/scvi-tools (~90+ tissue models from Tabula Sapiens + HLCA + Census)

**Strengths**:
- scvi-tools is actively maintained; API stable since v1.0
- Hugging Face hosting provides indefinite availability + versioning
- Google Colab tutorials cover key workflows (no local install required)

**Weaknesses**:
- Reproducibility repo lacks version pinning — notebook-only implementations
- Several analyses depend on large dataset downloads not feasible without HPC
- Hardcoded paths in notebooks require modification

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
