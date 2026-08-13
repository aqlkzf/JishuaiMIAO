---
layout: default
permalink: /paper-atlas/protocloud-84b0acdf/
title: "ProtoCloud"
nav: false
description: "ProtoCloud 通过多个 cell-type prototypes 把 VAE latent space组织成可比较的“代表细胞云”，用 similarity 完成注释和不确定性判断，再用 PRP 把 prototype decision 追溯到 HRGs；"
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
      <span>Cell Genomics · 2026</span>
    </div>
    <h1>ProtoCloud</h1>
    <p>ProtoCloud: A prototypical self-explaining model for single-cell analysis</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.xgen.2026.101217" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ProtoCloud">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Ding-Group/ProtoCloud" target="_blank" rel="noopener noreferrer" aria-label="Open code for ProtoCloud">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ProtoCloud 方法解读：用“像哪个代表细胞、由哪些基因支持”解释单细胞注释

### 1. 为什么需要 prototype，而不只需要分类概率

常规 scRNA-seq 注释模型把表达向量映射到一个 label，但很难回答三个实际问题：这个细胞为什么被判成该类型；它是典型还是处在类型边界；训练集原标签与模型不一致时该信谁。ProtoCloud 将每种 cell type 表示成多个可学习 prototype。新细胞的预测来自它与这些代表点的相似度，因此可以沿着“this cell looks like these prototypes”解释；再通过 prototypical relevance propagation（PRP）把相似度反传到输入基因，得到 highly relevant genes（HRGs）。

图 1A概括整个结构：原始 UMI counts 经 encoder 进入 latent space；每个类别拥有一组 prototypes；与 prototypes 的相似度送入 classifier，完整 latent vector 同时进入 decoder 重建 counts。图 1B把 PRP 从 prototype relevance 传回 gene relevance；C、D展示 label transfer 和 similarity-guided correction；E展示各类 HRG 的块状特异性。

### 2. 输入和预处理

模型输入是 cells × genes 的表达矩阵与训练 cell-type labels。论文实验通常过滤低 counts cells/genes，去除 mitochondrial、ribosomal、MALAT1/MTRNR genes，并选约 3000 HVGs。若测试集缺少训练基因，则按训练 gene order 对齐并补零。

源码 `scRNAData` 可读取 AnnData，优先使用 `layers['counts']`，支持 normalize/log1p 和 Cell Ranger HVG selection（`ProtoCloud/data/scRNAdata.py:80-181,436-489`）。训练模型 `raw_input=1` 时内部再对 raw counts 做 `log1p`，同时保存每细胞 library size 用于 negative-binomial reconstruction（`model/model.py:190-245`）。因此复现时必须明确输入是 raw counts 还是已变换矩阵，避免重复 log transform。

稀有类型会被 oversample：低于约 $1/(2K)$ 比例的类别从原细胞 UMI proportions 进行 multinomial sampling，生成 50%–100% library size 的 synthetic cells（`scRNAdata.py:341-407`）。这能缓解训练不平衡，但生成样本不是新的生物观测，不能用于下游 abundance estimation。

### 3. VAE latent space 被有意分成两半

encoder 默认三层 1024→512→256，再输出 latent mean 与 log variance；默认 latent dimension $d=20$。训练时用 reparameterization 得到

$$
z=\mu+\exp(\log\sigma^2/2)\epsilon.
$$

前 $d/2$ 维 $z^{(1)}$ 用于 prototype similarity 和 cell-type classification；后 $d/2$ 维 $z^{(2)}$ 不进入 classifier，但 decoder 使用完整 $z$。目标是让 $z^{(1)}$ 聚焦 cell identity，$z^{(2)}$ 吸收 batch、donor、技术或其他 nuisance variation，而无需显式 batch labels。

图 3A的 latent-space metrics 支持这条分工：$z^{(1)}$ 在 cell-type conservation/aggregate score 上强，$z^{(2)}$ 在 batch correction 指标上相对更好；图 3B的 PBMC30K UMAP也分别按 cell type 与 batch 着色。不过“后半维度只包含 batch”仍是建模目标，不是可辨识性定理，其他生物变化也可能进入其中。

### 4. Prototype cloud 和相似度

每个类别默认有 $M=6$ 个 prototype，每个 prototype 是一个 $d$ 维可学习向量；总数为 $K\times M$。分类只比较 $z^{(1)}$ 与 prototypes 的前半维：

$$
s_{i,k,j}=\frac{1}{1+\kappa^2\lVert z_i^{(1)}-p_{k,j}^{(1)}\rVert_2^2},
$$

其中 $κ$ 是可学习 scale。距离为 0 时相似度为 1，距离增大时以 heavy-tail Cauchy-like kernel 衰减。源码用 `torch.cdist` 和 `1/(square(distance*scale)+1)` 直接实现（`model.py:343-383`）。

所有 $K\times M$ similarities 组成特征向量，再经无 bias 的 linear classifier 输出类别 logits（`model.py:133-185,225-226`）。因此预测并非简单选择“最近 prototype 的类别”：classifier 可以学习多个 prototypes 的组合权重。最大同类 prototype similarity 则作为直观 confidence signal。

称为“cloud”是因为一个 cell type 不只用一个 centroid。多个 prototypes 可覆盖同类内部亚状态、连续谱或技术差异；但 prototype 本身不是训练集中某个真实细胞。论文/代码随后用最近的真实细胞展示 prototype neighborhood，这才形成可查看的 exemplar。

### 5. 为什么还需要 VAE reconstruction

decoder 默认 20→512→1024，输出每基因均值。raw-count 模式把 softmax 输出乘回 library size，并用 negative-binomial likelihood；dispersion 默认是 cell-type × gene parameter（`model.py:168-182,228-243,386-429`）。

reconstruction 约束 latent space 保留表达结构，避免只为分类压缩到几个 discriminative features。代码还将 NB loss 乘 $d/(2G)$ 缩放，以避免几千个基因的 likelihood 数值压倒 prototype/classification losses（`model.py:420-423`）。

### 6. Prototype prior 如何塑造两半 latent space

对类别 $y_i$ 的每个 prototype，代码计算两部分 KL：

- $z^{(1)}$ 对以正确类别 prototype 为中心、单位方差的 Gaussian；
- $z^{(2)}$ 对 standard normal。

每个 prototype 的 KL 再按对应 similarity 加权。实现中第一部分乘 5，而第二部分乘 1：

$$
KL_i\propto \sum_j\tilde s_{ij}\left[5KL(q(z_i^{(1)})\Vert N(p_{y_i,j}^{(1)},I))+KL(q(z_i^{(2)})\Vert N(0,I))\right].
$$

直接源码位于 `model.py:432-483`。5× asymmetry 是理解模型的重要实现细节：它强力把 type-relevant dimensions 拉向 correct-class prototypes，同时把后半维规整到普通 Gaussian。论文解释 latent decomposition，但该具体权重必须以代码为复现证据。

### 7. Orthogonal 与 atomic losses 分别防止什么

若只做 classification/KL，同类 6 个 prototypes 可能坍缩到一个点。stage 2加入 orthogonality loss，使同类 prototype 围绕 class center 的方向尽量互异，从而覆盖 intra-class modes。Atomic loss 则具有同类吸引、异类排斥的作用：每个细胞至少靠近一个正确类别 prototype，同时远离错误类别 prototypes。

总训练损失是 reconstruction、KL、cross-entropy、orthogonal、atomic 的加权和（`model/train.py:180-244`）。默认两阶段切换点是 `min(30, epochs//2)`：stage 1的 ortho/atomic 为 0；stage 2设 KL=2、ortho=0.3、atomic=1，而 reconstruction=10、CE=1（`train.py:100-145`）。这比“固定前30 epoch”更准确：当总 epochs 小于 60 时，切换发生在一半。

代码还对总 gradient 做 norm 15 clipping。Prototype 初始化是随机 Gaussian，不是 k-means center，因此随机种子和训练收敛会影响 prototype geometry。

### 8. PRP 怎样从 prototype 回到基因

ProtoCloud 的 gene explanation 不是把 differential expression 直接贴到预测后面。PRP 从某个 target prototype 的相似度出发，对同类其他 prototypes 给较弱正 relevance，对异类 prototypes 给负 relevance，再通过 latent mean、encoder blocks 传播到输入 genes。靠近该 prototype 的细胞对结果贡献更大；最后把同一 cell type 的多个 prototype relevance 按其覆盖细胞数汇总，产生 HRG ranking。

这使 explanation 与模型实际 decision path 对齐。图 3C显示只用各类型 top-30 HRGs 的并集（约 184 genes）仍保留 3000 HVG UMAP 的主要拓扑；图 3D–H用 GO、Tau specificity、已知 markers 和 naive/mature B cell 差异支持 HRG 的生物合理性。HRG 是“对模型判别最相关”，不等于因果调控 gene，也不保证在独立实验中 differential expression。

本地 `ProtoCloud/prp/lrp.py` 实现 relevance propagation，且会把 BatchNorm 参数融合进线性层后传播。该代码路径存在，但完整实验生成的 HRG tables 不属于仓库内单元测试；图中生物结论仍以论文结果为证据。

### 9. 相似度如何变成“确定/模糊”和校准概率

每个 predicted class 在训练数据上计算最大 prototype similarity 的分布，以较低分位数形成 class-specific threshold。高于阈值标为 certain，低于阈值标为 ambiguous。若模型 confidently disagrees with original label，论文称 Type 1，建议结合 HRGs re-annotate；若模型自身也 ambiguous，则为 Type 2，不重标。

图 4A、B展示 similarity 与 correctness 的关系和阈值；D–F用 CD4 T、cytotoxic T、NK 的 HRG/marker 表达检查冲突；这不是自动证明原 annotation 错误，而是给出可审计证据供研究者决定。

此外使用 isotonic regression 把 raw similarity 映射为 empirical correctness probability。代码为常见类型拟合 per-type calibrator，样本不足时回退 global calibrator（`model/calibrator.py:70-154`）。论文报告 Brier score 从 0.092降至0.048、ECE 从0.198降至0.031；图 4G、H显示 calibrated probability 更贴近 observed accuracy。校准器跨数据平台是否仍可靠取决于 distribution shift，不能把一次校准永久复用为概率保证。

### 10. 六张主图的证据链

- **图 1**：模型结构、PRP、label transfer/correction 和 HRG 概览。
- **图 2**：九个基准数据集的 accuracy、macro-F1、kappa；训练比例与 perturbation robustness；支持性能与低样本稳定性。
- **图 3**：latent decomposition、batch/cell-type UMAP 与 HRG 的功能/特异性。
- **图 4**：similarity threshold、两类 label discrepancy 和 isotonic calibration。
- **图 5**：optic nerve crush RGC 的 sequential continue-training；certain cells 成为下一时点的 pseudo-labeled training set，ambiguous cells用于再评估。
- **图 6**：AtlasEoE 向独立 EoE datasets transfer，检查 rare macrophage/DC/ILC2 HRGs、细胞周期 HRGs 和 disease composition。

本次逐张视觉检查了本地 `gr1_lrg.jpg` 至 `gr6_lrg.jpg`；`fx1_lrg.jpg` 为 graphical abstract。论文正文同时引用 Figures S1–S6 和 Tables S1–S7，但工作区没有独立 supplement 文件，因此补充结果只能按正文/图注引用，不能声称逐页核验。

### 11. 代码与论文的可复现边界

本地源码覆盖 preprocessing、rare-type augmentation、ProtoCloud architecture、全部核心 losses、two-stage training、prediction、calibration、PRP、plotting 和 API。

缺口包括：论文使用的全部原始/处理后 datasets、训练 checkpoints、主图结果 tables 和独立 supplement。代码存在不等于本地已重跑所有 benchmark；依赖和大数据运行也未在本次文档恢复中执行。

### 12. 一句话总结

ProtoCloud 通过多个 cell-type prototypes 把 VAE latent space组织成可比较的“代表细胞云”，用 similarity 完成注释和不确定性判断，再用 PRP 把 prototype decision 追溯到 HRGs；它把准确率、cell-level confidence 与 gene-level explanation放进同一训练框架，但 prototype/HRG 仍是模型内部证据，生物重标与跨数据概率解释必须结合独立 marker、表达和实验背景审查。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ProtoCloud — Summary

**Paper:** ProtoCloud: A prototypical self-explaining model for single-cell analysis
**Authors:** Kaiyun Guo, Jiarui Ding
**Journal:** Cell Genomics (2026)
**DOI:** 10.1016/j.xgen.2026.101217
**Code:** https://github.com/Ding-Group/ProtoCloud
**Category:** representation_models

---

### Motivation & Novelty

#### Biological Problem
Single-cell RNA sequencing (scRNA-seq) enables transcriptome-wide profiling of individual cells, enabling the construction of comprehensive cell atlases (Human Cell Atlas, tissue-specific references). A critical task is **cell type annotation**: mapping newly profiled cells to known types using labeled reference datasets. This task is complicated by:

1. **Class imbalance**: Rare cell types (e.g., basophils < 1% of blood; eosinophils frequently undetected in esophagus) are systematically underrepresented, leading to poor recall
2. **Batch effects**: Technical variation from donor, protocol, and platform entangles with biology, complicating reference-to-query transfer
3. **Label noise**: Reference atlases contain misannotated cells accepted as ground truth by existing tools
4. **Black-box predictions**: Deep learning models achieve high accuracy but provide no insight into which genes drove classification decisions or how confident the model is

#### Why Existing Methods Fall Short

| Method | Journal | Year | Key Limitation |
|---|---|---|---|
| Seurat v4 | Cell | 2021 | Black box, no uncertainty, limited scalability |
| scANVI | Mol. Syst. Biol. | 2021 | Requires batch labels; no interpretability |
| CellTypist | Science | 2022 | Black box, poor calibration |
| TOSICA | Nat. Commun. | 2023 | Computationally expensive, no uncertainty |
| scPoli | Nat. Methods | 2023 | Requires batch info, no gene-level explanation |
| SIMS | Cell Genom. | 2024 | 10-epoch training, limited interpretability |
| scGPT | Nat. Methods | 2024 | Zero-shot here; expensive, no uncertainty |
| scBERT | Nat. Mach. Intell. | 2022 | Gene constraints, slow fine-tuning, black box |

#### Novel Contributions
1. **First dual-explainability** for scRNA cell type annotation: cell-level interpretability (which prototype does this cell resemble?) AND gene-level interpretability (which genes drove the decision?) via Prototypical Relevance Propagation (PRP)
2. **Self-supervised batch disentanglement** without requiring batch labels: latent space partitioned into cell-type ($\mathbf{z}^{(1)}$) and nuisance ($\mathbf{z}^{(2)}$) halves, with asymmetric KL regularization
3. **Similarity-based calibrated uncertainty**: max-similarity to nearest prototype as a natural confidence score, calibrated via isotonic regression; enables two-tier classification (certain/ambiguous)
4. **Annotation error correction**: high-confidence predictions conflicting with original labels are flagged as misannotations, with HRG expression as supporting evidence
5. **Multinomial data augmentation**: generates synthetic rare-cell transcriptomes by resampling from per-cell multinomial count distributions, improving rare-type recall

---

### Method Overview

ProtoCloud is a **variational autoencoder (VAE)** extended with cell-type-specific prototypes and an interpretability mechanism. Four components are jointly trained end-to-end:

1. **Probabilistic encoder** $g: \mathbb{R}^G \to \mathbb{R}^d$ (3 hidden layers [1024, 512, 256]): maps log1p-transformed UMI counts to a d=20 dimensional latent normal distribution
2. **Prototype matrix** $\mathbf{P} \in \mathbb{R}^{(K \cdot M) \times d}$ (6 prototypes per class): learnable cell-type representatives in the same latent space as cell embeddings
3. **Bias-free classifier** $h: \mathbb{R}^{KM} \to \mathbb{R}^K$: classifies based solely on cell-prototype similarities via a scaled Lorentz kernel
4. **NB decoder** $f: \mathbb{R}^d \to \mathbb{R}^G$ (2 hidden layers [512, 1024]): reconstructs UMI counts with cell-type-specific dispersion

The **latent space is split**: first half $\mathbf{z}^{(1)}$ encodes cell type (pulled toward class prototypes with 5× KL weight), second half $\mathbf{z}^{(2)}$ captures batch/nuisance (regularized toward $\mathcal{N}(0,I)$).

**Two-stage training** (100 epochs total, AdamW, lr=1e-3):
- Stage 1 (epochs 1–30): ELBO + CE only → prototypes converge to class centroids; batch effects channel to $\mathbf{z}^{(2)}$
- Stage 2 (epochs 31–100): adds orthogonal loss (prototype diversity) + atomic loss (attraction/repulsion forces) + L1 sparsity on first encoder layer

**PRP for gene-level explanation**: post-hoc, single backward pass per prototype using α1β0 / z⁺-rules. Contrastive initialization (+1 for target prototype, +1/M for same-class prototypes, −1 for others) identifies genes positively driving the classification decision.

See `doc_method.md` for full mathematical detail.

---

### Evaluation

#### Benchmark Performance (Figure 2)
ProtoCloud benchmarked against 8 methods across 8 datasets (9,000–421,312 cells) using accuracy, macro F1, and Cohen's kappa (5 random seeds each):

- **Best or near-best** on all three metrics across all 8 datasets using fixed default hyperparameters
- **Macro F1 rank #1** in >60% of experimental repetitions — especially important as macro F1 is sensitive to rare cell types
- **AtlasEoE** (421K cells, 72 types): 94.5% accuracy, 0.877 macro F1; 97% accuracy specifically on 12 rare cell types
- **Robustness**: accuracy ≥93.18% at 20% label corruption; macro F1 = 0.87 at only 10% training data

#### Latent Disentanglement (Figure 3A-B)
On PBMC30K with known batch annotations:
- $\mathbf{z}^{(1)}$: cLISI=1.00, NMI=0.95, KMeans ARI=0.98 → near-perfect cell type encoding
- $\mathbf{z}^{(2)}$: iLISI=0.00, NMI=0.06 → successfully captures batch with minimal cell type information

#### HRG Biological Validity (Figure 3C-H)
- 184 HRGs (top 30/cell type union) preserve the UMAP topology of 3,000 HVGs
- HRG Tau specificity score τ=0.828, comparable to curated ScType markers (non-significant difference); both far exceed random genes (p≤0.0001)
- GO enrichment yields lineage-appropriate terms (B cells: MHC-II assembly; CD14+ monocytes: inflammatory response)
- B cell HRGs include established markers (MS4A1, CD79A, IGKC, IGHM)
- Mature vs naive B cell differential HRGs identify *CD79B*, *BANK1*, *LY9* as key distinguishers (Figure 3H)

#### Uncertainty Calibration (Figure 4)
- Brier score before calibration: 0.092 → after isotonic regression: **0.048** (48% improvement)
- ECE before: 0.198 → after: **0.031** (84% improvement)
- Certain predictions: mean calibrated probability 0.960 = observed accuracy 0.960
- Ambiguous predictions: mean 0.779 = observed accuracy 0.783

#### Time-Course Application (Figure 5)
- RGC optic nerve crush dataset (0–14 days post-crush, 45 subtypes):
  - >94% accuracy for certain predictions before 4 dpc
  - Continued training improves ambiguous cell accuracy by 2–10%
  - C1 RGC survival rate revised from 1.2% → **5.6%** after re-annotating previously unassigned cells
  - 30–70% of unassigned cells confidently reclassified across time points

#### EoE Atlas Application (Figure 6)
- Trained on 421K-cell esophageal atlas (72 cell types, 22 donor batches)
- Three novel rare cell types identified in two independent EoE cohorts (10× Chromium and SeqWell): ALOX15+ macrophages, PRDM16+ cDC2C, ILC2
- PRDM16+ cDC2C is a previously uncharacterized dendritic cell subtype in esophagus
- Disease-enriched proportions consistent with EoE pathogenesis across both cohorts

---

### Reproducibility: 4/5

**Justification:**
- Code is clean, well-organized, and installable via pyproject.toml
- Default hyperparameters fixed across all experiments (no per-dataset tuning required)
- Tutorial notebook (`api_tutorial.ipynb`) demonstrates end-to-end usage
- All 11 benchmark datasets are publicly available with download links in the paper
- The similarity kernel formula discrepancy between paper and code (Cauchy vs squared Lorentz) could confuse users attempting to reimplement from the paper alone
- Loss coefficient values (recon=10, kl=2, ortho=0.3, atomic=1) and the critical 5× KL asymmetry are not disclosed in the paper — only discoverable from code
- No provided training scripts for specific benchmarks, requiring users to assemble the pipeline from API documentation
- GPU required for practical training on large datasets (300K cells takes ~hours on V100)

**Practical notes:**
- Install via `pip install .` in the repo directory
- Data must be in AnnData format with `gene_name` column in `.var` and `celltype` in `.obs`
- Preprocessing (remove MT/ribosomal genes, select HVGs) is handled internally by `scRNAData`
- CUDA recommended; CPU training is very slow for >50K cells

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
