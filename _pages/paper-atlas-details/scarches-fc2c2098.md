---
layout: default
permalink: /paper-atlas/scarches-fc2c2098/
title: "scArches"
nav: false
description: "已有参考图谱通常由许多批次训练而成，但新实验到来时，研究者未必能重新取得全部参考原始数据，也不希望每来一个批次就从头训练。scArches 的目标是：只拿到参考模型参数和新查询数据，就把查询细胞放进参考潜空间，同时尽量不改写参考图谱已经学到的结构。 输入包括：与参考模型使用相同特征空间的查询表达矩阵、查询的 study/batch 条件标签，以及训练好的参考模型。输出是查询细胞在参考潜空间中的坐标；"
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
      <span>Nature Biotechnology · 2021</span>
    </div>
    <h1>scArches</h1>
    <p>Mapping single-cell data to reference atlases by transfer learning</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-021-01001-7" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scArches">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/theislab/scarches" target="_blank" rel="noopener noreferrer" aria-label="Open code for scArches">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scArches：用架构手术把新单细胞数据映射到既有参考图谱

### 1. 它要解决的不是“再做一次整合”

已有参考图谱通常由许多批次训练而成，但新实验到来时，研究者未必能重新取得全部参考原始数据，也不希望每来一个批次就从头训练。scArches 的目标是：只拿到参考模型参数和新查询数据，就把查询细胞放进参考潜空间，同时尽量不改写参考图谱已经学到的结构。

输入包括：与参考模型使用相同特征空间的查询表达矩阵、查询的 study/batch 条件标签，以及训练好的参考模型。输出是查询细胞在参考潜空间中的坐标；随后可以做可视化、邻域分析、标签转移，或在 totalVI 场景中补全查询未测量的蛋白模态。论文 Results“scArches enables mapping query data to reference”及图 1 给出了这一设定。

### 2. 参考模型先学什么

论文把 scArches 定义为一种可套在条件生成模型上的迁移学习策略，而不是一个固定的单一网络。其 base model 包括 trVAE、scVI、scANVI 和 totalVI。以 CVAE 表示时，编码器从表达 $x$ 和条件 $s$ 得到潜变量分布

$$q_\phi(z\mid x,s),$$

解码器用 $z$ 与 $s$ 重构表达

$$p_\theta(x\mid z,s).$$

训练目标以重构项和 KL 正则为核心；trVAE 还加入 MMD 项以对齐条件分布。这里的 $s$ 可以是实验、技术、组织、物种或疾病等离散标签。模型把条件效应交给条件分支解释，使潜变量 $z$ 更适合表达跨批次共享的生物结构。

本地 trVAE 代码把这件事写得很直白：`CondLayers` 将输入拆为表达和 one-hot 条件，并计算

$$h=W_xx+W_ss+b.$$

也就是说，表达权重 `expr_L` 与条件权重 `cond_L` 是分开的（`code_repo/scarches/models/trvae/modules.py:8-27`）；编码器和解码器的第一层都使用这种条件层（同文件 `:65-92`、`:139-188`）。这正是后续“手术”可以只扩条件权重、不动表达通路的结构基础。

### 3. 架构手术：只给新批次接一个小适配器

对查询批次 $s_{new}$，scArches 依次做四件事。

1. 读取参考模型参数和参考特征名，检查查询数据使用同一变量空间。
2. 找出参考模型未见过的 condition，并将它们加入条件列表。
3. 在编码器与解码器第一层的条件权重矩阵中新增列；旧列复制参考模型权重，新列随机初始化。这些新列就是论文所说的 adaptors。
4. 冻结绝大多数参考参数，只用查询数据训练新条件相关权重；训练后通过编码器取得查询潜表示。

本地实现有两条相互印证的路径。通用 `SurgeryMixin.load_query_data()` 在 `code_repo/scarches/models/base/_base.py:198-281` 中发现新 condition、构造扩展模型、载入扩展参数，并在冻结模式下只开放 `cond_L.weight`（以及模型需要的 `theta`）。旧式 trVAE 路径在 `code_repo/scarches/surgery/trvae.py:45-117` 中显式为编码器和解码器条件矩阵追加随机列、载入旧状态、冻结其余参数并训练查询模型。

这种强约束有两层作用：计算上只需优化很少的参数；统计上则限制查询数据把整个参考网络拉向自身，从而降低灾难性遗忘和过拟合小查询集的风险。图 2 比较了仅训练 adaptor、训练输入层和全网络微调：仅训练 adaptor 的方案在整合质量上有竞争力，同时将可训练参数减少四至五个数量级。它不是保证“新类型一定识别正确”，而是给查询数据一个受约束的入口。

### 4. 为什么不需要共享参考原始数据

映射时需要的是参考模型的结构、权重和特征约定，不必把参考细胞与查询细胞重新拼接训练。用户可以下载模型，训练自己的 adaptor，并选择是否分享更新后的模型。图 1b 将其画成去中心化迭代流程；图 1c–e 的胰腺实验则连续加入 SS2 和 CelSeq2 查询。参考中刻意移除的 alpha（以及补充实验中的 alpha、gamma）细胞，在映射后形成独立查询簇，而没有被强行压入已有类型。

这里应区分“无需共享参考原始数据”与“完全无隐私风险”：论文展示的是参数共享工作流，并未证明模型参数在所有攻击模型下都满足形式化隐私保证。

### 5. 映射之后怎样转移标签并表达不确定性

论文 Methods 在参考潜空间上训练加权 kNN。对查询细胞 $c$ 的邻居集合 $N_c$，先按潜空间欧氏距离施加高斯权重 $D_{c,n,N_c}$，再将同一标签邻居的权重归一化：

$$p(Y=y\mid X=c,N_c)=
\frac{\sum_{i\in N_c}I(y^{(i)}=y)D_{c,n_i,N_c}}
{\sum_{j\in N_c}D_{c,n_j,N_c}}.$$

预测标签取概率最大的类别，不确定性定义为

$$u_{c,y,N_c}=1-p(Y=y\mid X=c,N_c).$$

若最佳标签仍有 $u>0.5$，论文将该细胞报告为 `unknown`。因此它不是“永远给一个最接近的已知类型”，而是允许拒识。图 4 中，参考被移除的气管组织细胞具有较高不确定性；总体标签转移约为 84% 准确率。

重要实现边界：上述加权 kNN 公式位于论文分析流程，但在当前本地 `scarches` 库中未找到对应实现；`doc_code.md` 将其标为 **Not found**。不能把这段论文方法描述成当前包内可直接调用的稳定 API。

### 6. 多模态和疾病查询说明了什么

图 4f–h 用 totalVI 构建 CITE-seq 参考，把仅有 RNA 的查询映射进去，并由参考模型估计查询未测量的蛋白。这说明架构手术可以继承 base model 的生成能力；并不是 scArches 另行发明了蛋白补全模型。

图 5 把 COVID-19 查询映射到健康 PBMC 参考。映射保留了疾病严重度相关的细胞状态，并发现重症患者 CD14+ 单核细胞中的特异状态。这个结果支持“受约束映射仍可保留查询特有变化”，但不应解读为 latent 距离自动给出因果机制或临床诊断。

### 7. 五张主图应怎样连起来读

- 图 1：定义流程。先训练共享参考，再逐批加入 adaptor；胰腺案例说明迭代更新和参考未见类型的分离。
- 图 2：回答“该放开多少参数”。仅训练查询条件权重达到最好的精度、速度与参数量折中。
- 图 3：回答“参考模型够不够好”。免疫数据中，参考比例提高到约 50%、并包含多个批次后，映射明显更稳；结果依赖 base model 和参考数据构成。
- 图 4：展示知识转移。包括大规模跨技术映射、带拒识的标签转移，以及从 CITE-seq 参考补全蛋白。
- 图 5：测试生物学新状态。健康参考没有迫使 COVID-19 查询丢失疾病严重度信号。

补充材料扩展了这些结论：双重未见细胞类型、多个查询同时更新、稀有类型与连续轨迹、跨物种映射及标签分类器比较。它同时提示一个限制：极稀有群体在约 0.5% 以下可能与其他类型混合，不能把“能保留 OOD”理解成无条件保证。

### 8. 论文—代码对应与可复现边界

当前本地代码固定在仓库提交 `b5ae098242ccfd7e4bebaa98d801dc41d5c37798`。

| 机制 | 对应情况 | 直接证据 |
|---|---|---|
| 条件输入与表达输入分支相加 | Exact | `models/trvae/modules.py:8-27` |
| 编码器/解码器首层使用条件权重 | Exact | `models/trvae/modules.py:65-92,139-188` |
| 发现新 condition、扩展模型并载入参考参数 | Exact | `models/base/_base.py:235-267` |
| 冻结旧权重、开放 condition adaptor | Exact | `models/base/_base.py:268-281` |
| trVAE 重构、KL 与 MMD 损失 | Exact | `models/trvae/trvae.py:116-157`、`trainers/trvae/unsupervised.py:62-70` |
| scVI/scANVI/totalVI 的完整概率模型 | Partial | 依赖外部 scvi-tools；本地主要提供 surgery 接口，不能仅凭本快照验证其全部内部实现 |
| 论文加权 kNN 与 uncertainty 拒识 | Not found | 论文 `paper.md:322-326`；本地库未找到相应实现 |
| 全部论文基准数值复现 | Not verified | 本次恢复核对了论文、图注、补充材料和源码，没有重跑大规模数据实验 |

### 9. 使用时最容易忽略的前提

1. 查询与参考必须有兼容的特征空间；代码会校验变量名，但这不能替代数据质量控制。
2. 映射质量受参考覆盖度、批次数量和 base model 选择影响。图 3 的“约 50%”是实验观察，不是适用于所有数据集的定理。
3. 未见群体可能形成独立簇，也可能在极低丰度或与已知类型高度相似时混合；应结合不确定性、marker 和独立验证。
4. adaptor 保护参考结构，但强约束也限制了模型适应巨大 domain shift 的能力。
5. 潜空间整合、标签转移和生物学解释是三个层次；前两者的成功不自动证明第三层的机制结论。

一句话概括：scArches 把“重训整个图谱”改成“在冻结参考模型上为新条件接入少量可训练权重”，用受约束的迁移学习换取可共享、可迭代、计算较轻的查询映射。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scArches — Paper Summary

**Paper:** Mapping single-cell data to reference atlases by transfer learning
**Authors:** Lotfollahi et al. (13 authors), Theis Lab
**Journal:** Nature Biotechnology 40(1), 2021-08-30
**DOI:** 10.1038/s41587-021-01001-7
**Method:** scArches (single-cell architectural surgery)
**Code:** https://github.com/theislab/scarches

---

### Motivation & Novelty

#### Biological Problem

Single-cell atlases are now routinely generated by consortia (Human Cell Atlas, Tabula Muris, Tabula Muris Senis), but using them to contextualize new datasets faces three compounding problems:

1. **Batch effects**: new datasets come from different labs, protocols, and sequencing technologies. Integrating them into an existing reference requires re-running the full integration pipeline with access to all raw data.
2. **Data sharing restrictions**: patient data and data-protection regulations (GDPR, institutional policies) often prohibit centralized data aggregation.
3. **Biological perturbation confound**: disease states (e.g., COVID-19) may affect most cells. De novo integration methods treat such effects as batch noise and remove them — but for disease analysis, *preserving* disease-specific variation is the goal.

#### Limitations of Prior Approaches

- **Harmony** (*Nature Methods*, 2019, Korsunsky et al.): PCA-based, fast, but requires all data centrally and cannot be updated without full re-run.
- **Scanorama** (*Nature Biotechnology*, 2019, Hie et al.): graph-based, good performance but requires all datasets.
- **Seurat v3** (*Cell*, 2019, Stuart et al.): anchor-based, widely used, but computationally expensive for large datasets and requires raw data.
- **LIGER** (*Cell*, 2019, Welch et al.): matrix factorization, needs full data access.
- **mnnCorrect** (*Nature Biotechnology*, 2018, Haghverdi et al.): mutual nearest neighbors, fast but cannot scale to brain-size datasets (>300k cells).
- **scVI** (*Nature Methods*, 2018, Lopez et al.): deep generative model, strong performance but no transfer learning — every new dataset requires re-running the full model.
- **scGen** (*Nature Methods*, 2019, Lotfollahi et al.): perturbation prediction by vector arithmetic, but no reference mapping framework.
- **Transfer learning approaches in genomics**: Wang et al. 2019 (*Nature Methods*, SAVER-X) — denoising TL but doesn't account for batch effects. Stein-O'Brien et al. 2019 (*Cell Systems*) — variance decomposition TL but no systematic fine-tuning.

#### Unique Contributions

1. **Architecture surgery**: a minimal TL strategy that adds *m × (p + q)* new parameters (adaptors) for each new condition while freezing all reference weights. For a single new batch with default architecture: only **320 parameters** trained vs. >1 million in full model — 4–5 orders of magnitude reduction.
2. **Decentralized atlas building**: users share model weights (not raw data). Any user can download a reference model, fine-tune locally, and optionally share only the lightweight adaptors.
3. **Disease variation preservation**: because disease covariates are not seen during reference training, they are not regressed out by the model — they are preserved as distinct query structure.
4. **Base model agnosticism**: surgery applies to any conditional neural network (CVAE, trVAE, scVI, scANVI, totalVI, conditional GAN), enabling multimodal applications including missing modality imputation.

---

### Method Overview

#### Algorithmic Framework

scArches is a transfer learning wrapper around conditional variational autoencoders (CVAEs). The core concept is **architecture surgery**:

1. **Reference training**: Train a CVAE (e.g., scVI, trVAE) on multiple reference datasets, using one-hot study labels as condition inputs concatenated to both encoder and decoder first layers.
2. **Weight expansion**: For each new query batch, add new columns to the condition weight matrix (`cond_L.weight`) in the encoder's and decoder's first layers only. Initialize with Xavier scaling.
3. **Selective freezing**: Freeze all reference weights; allow gradients only through the new condition columns (adaptors) and condition-specific dispersion parameters.
4. **Fine-tuning**: Train on query data with the frozen backbone — adaptor weights and dispersion converge quickly (default: 20 epochs).

#### Key Technical Components

- **CondLayers** (`modules.py`): separate `expr_L` and `cond_L` linear layers summed additively. This additive design is the implementation prerequisite for surgery: new conditions require only appending columns to `cond_L`, not modifying the full weight matrix.
- **Reconstruction losses**: MSE (log-normalized data), NB (count data), ZINB (zero-inflated count data). NB/ZINB use condition-specific dispersion parameters `theta` [genes × conditions] that remain trainable during surgery.
- **MMD regularization** (trVAE variant): Maximum Mean Discrepancy with 19-scale RBF kernel, computed between reference and query condition groups. Penalizes distributional mismatch at the first decoder layer.
- **Label transfer**: Gaussian-kernel weighted kNN classifier in latent space with uncertainty scoring (cells with >50% uncertainty labeled "unknown").
- **Model sharing**: Zenodo API integration for uploading/downloading model weights and adaptor files.

#### Biological Assumptions

- Batch effects are captured by one-hot condition labels; the CVAE latent space should be condition-invariant.
- Disease effects are orthogonal to technical batch effects in high-dimensional space — if disease is not seen during reference training, it will not be removed.
- Query data must overlap with reference in gene space (missing genes zero-filled); performance degrades with >10–25% missing genes.
- At least ~50% of data (≥10,000 cells, multiple batches) should be used as reference for robust mapping.

---

### Evaluation

#### Datasets

| Dataset | Cells | Tissues | Task |
|---|---|---|---|
| Mouse brain (4 studies) | 978,734 (250k reference) | Brain regions | Fine-tuning strategy comparison (Fig. 2) |
| Human pancreas (5 datasets) | 15,681 | Pancreatic islets | Iterative reference building (Fig. 1) |
| Human immune (10 samples) | 20,522 | Bone marrow + PBMCs | Reference size effect; de novo comparison (Fig. 3) |
| Tabula Muris Senis | 356,213 | 23 tissues, 5 ages | Label transfer reference (Fig. 4) |
| Tabula Muris (query) | 90,120 | 24 tissues (incl. unseen trachea) | Label transfer query (Fig. 4) |
| CITE-seq PBMCs | 10,849 (ref) + 10,315 (query) | PBMCs | Protein imputation via totalVI (Fig. 4) |
| COVID-19 BALF | 62,469 | Lung/blood | Disease-to-healthy mapping (Fig. 5) |
| Healthy immune+lung (ref) | 154,723 | Bone marrow, blood, lung | COVID-19 reference (Fig. 5) |

#### Metrics (10 integration metrics from Luecken et al. 2020)

**Batch correction** (weighted 40%):
- Entropy of Batch Mixing (EBM)
- Principal Component Regression (PCR)
- kNN graph connectivity
- Batch ASW (inverted silhouette)

**Biological conservation** (weighted 60%):
- ARI / NMI (Louvain clustering vs. cell type labels)
- kNN accuracy
- Cell type ASW
- Isolated label F1 / silhouette (rare cell types)

**Overall score**: 40% batch correction + 60% bio conservation.

#### Results

| Comparison | Result |
|---|---|
| Fine-tuning strategy (adaptors vs. full retrain) | Adaptors competitive at 4-5 orders of magnitude fewer parameters (Fig. 2d) |
| scArches vs. Harmony, Scanorama, Seurat, Conos, LIGER, mnnCorrect | Overall scores comparable despite scArches using only ~⅔ of data as reference (Fig. 3e) |
| Label transfer accuracy (Tabula Senis→TM, 90k cells, 23 tissues) | ~84% overall accuracy; unseen trachea cells correctly flagged as high uncertainty |
| Tracheal cells (unseen in reference, n=9,330) | Correctly placed in distinct cluster; high uncertainty score |
| Reference size threshold | Robust performance at ≥50% data (~10,000 cells) as reference |
| Speed vs. de novo integration | 5× faster (scVI), 8× faster (scANVI) |
| COVID-19 disease states | TRAMs, MoAMs, activated CD8+ T cells preserved as distinct populations |

---

### Reproducibility

**Rating: 4/5** — Strong reproducibility with publicly available code, model weights on Zenodo, and public datasets. One point deducted for benchmark code (full 10 metrics) and annotation pipeline requiring external repositories.

**Environment:**
- Python + PyTorch, scarches package (pip install scarches)
- scvi-tools ≥0.12.1 required for scVI/scANVI/totalVI surgery
- GPU recommended but not required for inference
- All datasets publicly available; download links in Methods

**Code availability:**
- Library: https://github.com/theislab/scarches
- Reproducibility: https://github.com/theislab/scarches-reproducibility
- Pre-trained models: Zenodo model repository (links in tutorials)
- Tutorial notebooks: `notebooks/` directory for trVAE, scVI, scANVI, totalVI surgery pipelines

**Practical notes:**
- Start with `TRVAE.load_query_data(query_adata, reference_model_path)` for surgery
- Choose HVGs generously in reference (4000–5000 recommended) for robustness to missing query genes
- For count data: use NB or ZINB reconstruction loss; pass raw counts; model handles log-transform internally
- For missing query genes: replace with zeros; performance degrades beyond 25% missing
- Default surgery hyperparameters (20 epochs, lr=0.001) work well; avoid over-training adaptors
- **kNN annotation not in library**: the weighted kNN classifier with uncertainty scoring (paper §Methods "Cell type annotation") is not implemented in the main scarches package — reproduce from the scarches-reproducibility repo
- **Speed-up claims from Supplementary**: 5–8× speed-up over de novo methods reported in Supplementary Fig. 16a; not verified in main text
- **scVI/scANVI/totalVI surgery via scvi-tools**: scarches wraps scvi-tools ≥0.12.1; library encoder removal and scANVI classifier freezing are inside scvi-tools and not directly inspectable from the scarches codebase

**Strengths:**
- Highly accessible: no GPU needed for surgery; no hyperparameter tuning for query mapping
- True data privacy: only model weights shared, never raw data
- Handles disease/perturbation data without removing biological variation
- Generalizes to multimodal (CITE-seq protein imputation) and cross-species applications

**Weaknesses:**
- Output is latent embedding (not corrected expression matrix) — post-hoc differential expression requires special care
- Performance depends on reference quality: poor reference → poor query mapping
- Gene space must match; missing genes zero-filled (performance penalty at >25% missing)
- kNN annotation equations not implemented in the main library; users need to re-implement from paper
- scVI/scANVI/totalVI surgery internals hidden in scvi-tools (opaque to scarches users)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
