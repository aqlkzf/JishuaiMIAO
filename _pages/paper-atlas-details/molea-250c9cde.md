---
layout: default
permalink: /paper-atlas/molea-250c9cde/
title: "MOLEA"
nav: false
wide: true
description: "离子化脂质决定了脂质纳米颗粒（LNP）的包封、内体逃逸和组织分布。传统筛选通常只最大化目标细胞转染，但许多 LNP 天然偏向肝脏；一个在软骨细胞中很强、在肝细胞中同样很强的候选，并不是真正的软骨选择性载体。 MOLEA（multiobjective LNP engineering with AI）把问题拆成两个预测量：候选脂质 p 在软骨细胞中的 mRNA transfection potency Cp，以及在肝细胞中的 potency…"
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
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>MOLEA</h1>
    <p>A multiobjective AI model for LNP engineering enhances tissue-selective mRNA delivery</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-026-03109-0" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for MOLEA">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/bowenli-lab/MOLEA" target="_blank" rel="noopener noreferrer" aria-label="Open code for MOLEA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MOLEA 中文方法解读：把“高效”与“少进肝”写进同一个脂质筛选目标

### 1. 为什么需要多目标 LNP 设计

离子化脂质决定了脂质纳米颗粒（LNP）的包封、内体逃逸和组织分布。传统筛选通常只最大化目标细胞转染，但许多 LNP 天然偏向肝脏；一个在软骨细胞中很强、在肝细胞中同样很强的候选，并不是真正的软骨选择性载体。

MOLEA（multiobjective LNP engineering with AI）把问题拆成两个预测量：候选脂质 $p$ 在软骨细胞中的 mRNA transfection potency $C_p$，以及在肝细胞中的 potency $H_p$。模型分别预测两者，再用 targeting score（TS）把“目标效力”和“目标/脱靶差异”合成排序分数。这里的“多目标”主要发生在预测结果的组合与候选排序，不是一个端到端 Pareto 优化器。

### 2. Figure 1 的四阶段工作流

Figure 1（主流程图 `52e855...jpg`）从左到右分成四段：

1. 在 1,549 万个虚拟离子化脂质上做自监督持续预训练，学习脂质结构表示；
2. 用 1,152 个实测 Ugi-4CR 脂质在软骨细胞和肝细胞中的 mTP 微调预测器；
3. 对 40,755 个可合成候选预测两种细胞效力，用 TS 排序并兼顾结构多样性；
4. 合成 K1–K9，在原代细胞和小鼠中验证，最终选出 K9。

这张图的重要信息是：计算模型只完成“候选优先级压缩”，真正结论来自后续化学合成、体外筛选和体内验证。

### 3. 化学空间怎样建立

论文 Methods 说明，预训练库由 64 种胺、62 种异腈、64 种醛和 61 种羧酸通过 Ugi 四组分反应穷举组合，得到 15,491,072 个虚拟脂质。Figure 2a（`e9e85e...jpg`）把四类模块对应为 headgroup、linker、tail A 和 tail B。

微调库更小但有实验标签：6 种胺、6 种异腈、4 种醛、8 种羧酸组合为 1,152 个离子化脂质，分别在原代软骨细胞和肝细胞测定 mTP。候选筛选库按试剂可得性与尾链范围过滤为 40,755 个结构（23 headgroups、12 linkers、23 tails）。

本地仓库列出了这些 CSV 路径，但内容都是 Git LFS pointer，未实际取回；所以规模与组成来自论文证据，不能从当前 CSV 行数独立复核。

### 4. 分子怎样进入 MOLEA

#### 4.1 图表示

每个 SMILES 由 RDKit 转为图 $G=(V,E)$。节点的两个离散特征是原子类型与手性；边的两个特征是键类型与键方向。初始节点表示是两种 embedding 之和：

$$
V_v^{(0)}=\operatorname{Emb}_{atom}(V_v[0])+\operatorname{Emb}_{chirality}(V_v[1]).
$$

代码 `scripts/molea_finetune.py:85-88,151-167` 与该路径直接对应。每层 `GINEConv` 给图加自环，将键类型和键方向 embedding 相加，再把邻居表示与边表示相加后聚合（`molea_finetune.py:16-48`）。默认五层、每层 batch normalization，最后 global mean pooling 得到图级表示。

#### 4.2 双分支表示

微调模型同时使用 GNN 分支和 Mordred descriptor 分支。后者把上千个物化描述符投影到至多 100 维，再与图表示拼接。`molea_finetune.py:113-148,169-173` 实现描述符投影和预测头。这个双分支让有限的 1,152 个实验样本同时利用学习到的拓扑表示和预定义物化信息。

### 5. 先自监督预训练，再监督微调

#### 5.1 脂质领域持续预训练

模型先从 MolCLR 权重初始化，再在 15,491,072 个虚拟脂质上进行对比学习。对同一脂质产生两种增强视图，以 NT-Xent 损失拉近正对、推远同批次负对：

$$
L_{i,j}=-\log\frac{\exp(\operatorname{sim}(z_i,z_j)/\tau)}{\sum_{k\ne i}\exp(\operatorname{sim}(z_i,z_k)/\tau)}.
$$

`utils/nt_xent.py:41-68` 实现余弦相似度和温度缩放损失；`scripts/molea_pretrain.py:50-119` 是五层 GINE 与 projection head。配置为 batch 512、15 epochs、温度 0.1、初始学习率 $5\times10^{-4}$。

论文写有 atom masking 与 bond deletion 两种增强，但当前 `config_pretrain.yaml:22` 选择 `aug: node`，即这一公开配置走节点掩码分支；不能由此证明同一运行同时使用两种增强。

#### 5.2 两个细胞类型的监督回归

微调以 MSE 拟合 log-transformed mTP：

$$
L_{\mathrm{MSE}}=\frac1N\sum_i(y_i-\hat y_i)^2.
$$

代码以 scaffold split 划分 80%/10%/10%，使用 200 epochs、batch 32，并为 backbone 与预测头设置不同学习率。仓库含 `model_finetuned_Chondrocyte.pth` 与 `model_finetuned_Hepatocyte.pth` 两个独立 checkpoint；软骨与肝细胞并非一个共享双输出头共同训练，而是两个模型的预测在下游组合。

### 6. Targeting Score 是多目标核心

论文定义：

$$
\mathrm{TS}_p=\alpha\ln\frac{C_p+\epsilon}{H_p+\epsilon}+\beta\ln(C_p+\epsilon),
$$

其中 $\alpha=2$、$\beta=1$、$\epsilon=10^{-10}$。

第一项奖励软骨相对肝细胞的选择性，并给两倍权重；第二项防止“两个细胞都几乎不转染、但比值很高”的假优选。例如候选 A 的 $C=100,H=10$ 时 TS 约为 $2\ln10+\ln100=9.21$；候选 B 的 $C=1,H=0.1$，比值相同但 TS 仅约 4.61，因此 A 优先。

这一公式是论文 Methods 的直接证据，却没有出现在本地 Python。`scripts/infer.py:860-897` 只把 SMILES 转图并输出单模型预测；两个预测 CSV 也是未取回的 LFS pointer。故 TS 排序与 K1–K9 选择不能由当前快照端到端重跑。

### 7. 一个隐藏但重要的推理差异

微调时模型把 Mordred 描述符送入 descriptor branch；但 `molea_finetune.py:175-202` 的 `forward_only_h()` 在没有描述符时创建全零向量。`infer.py:860-897` 明确调用这个函数，因此该筛选入口实际上以 GNN 表示加零描述符进行预测。

这不等于模型完全没有 descriptor branch，而是说明公开的虚拟库推理入口没有计算或提供 Mordred 特征。论文正文把双分支作为完整模型描述，复现者必须报告这一训练–推理输入差异。

### 8. 图和实验结果支持什么

Figure 2 将化学组合、两种细胞 mTP、TS、UMAP、结构富集、K1–K9 选择和体内 IVIS 串联起来。九个候选位于训练化学空间相对稀疏区域，说明选择不只是取训练样本近邻；最终 K2/K9 进入体内验证。

Figure 3 的实验流程局部图（`942a86...jpg`）显示关节内注射 mFluc-LNP 后 6 小时做 IVIS。论文正文报告优化后的 K9 与临床基准 SM-102 相比，膝/肝与膝/脾选择性分别提高 13.15 倍和 18.82 倍。随后研究用 K9 递送 CRISPR–Cas9 和腺嘌呤碱基编辑器，靶向 Mmp13，在 MIA 与 DMM 骨关节炎小鼠模型中观察软骨保护。

这条因果链包含模型优选、配方 DoE 优化、体内递送、基因编辑和疾病表型；不能把全部疗效简单归因于 GNN 预测器本身。

### 9. 代码与论文证据边界

| 项目 | 本地证据 | 判断 |
|---|---|---|
| GINE、pooling、descriptor branch、预测头 | `molea_finetune.py:16-173` | Exact |
| 对比学习结构与 NT-Xent | `molea_pretrain.py:50-119`, `nt_xent.py:41-68` | Exact |
| MSE、优化器、配置 | `finetune.py` 与 YAML | Exact/Partial |
| 两个细胞 checkpoint | `ckpts/*.pth` 为真实 PyTorch 文件 | Available |
| 数据、候选库、预测 CSV | 仅 Git LFS pointer | Not available locally |
| TS Eq. 9–10 | Python 中未找到 | Not found |
| RF/LightGBM/MLP、SCC、$R^2$ | 对应脚本未找到 | Not found |
| 湿实验与体内验证 | 论文 Methods/figures | 不属于代码仓库 |

### 10. 适用范围与限制

- 训练标签来自体外软骨细胞和肝细胞，体外预测与体内分布不必然一致；论文也把缺少大规模体内数据列为限制。
- 初始 Ugi-4CR 模块集合限制可搜索化学空间，模型不能提出集合之外的新 scaffold。
- 当前权重 $\alpha=2,\beta=1$ 代表特定软骨高/肝低偏好；换组织必须重新定义目标与数据。
- K9 经额外配方 DoE 优化，最终 LNP 表现不是离子化脂质结构一个因素决定。
- 动物模型和关节内局部给药不能直接外推到系统给药或人类骨关节炎治疗。
- 当前快照缺少 LFS 数据载荷和 TS 实现，不能宣称一键复现 K1–K9 排名。

一句话概括：MOLEA 用脂质领域对比预训练提升结构表示，用两个细胞回归器预测目标与脱靶效力，再用 TS 结合选择性和绝对效力；其创新在“以脱靶约束重写筛选目标”，而不是一个神秘的联合优化黑箱。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MOLEA Summary

**Paper**: A multiobjective AI model for LNP engineering enhances tissue-selective mRNA delivery
**Authors**: Zhou, M., Xu, Y., Li, G. et al. (Bowen Li lab, University of Toronto)
**Journal**: Nature Biotechnology (2026)
**DOI**: 10.1038/s41587-026-03109-0

---

### Motivation & Novelty

#### The Biological Problem

Lipid nanoparticles (LNPs) are the dominant delivery vehicle for RNA therapeutics, enabling clinical success of mRNA vaccines (Comirnaty, Spikevax) and siRNA drugs (Patisiran). However, virtually all LNPs exhibit strong **hepatic tropism** — they accumulate preferentially in the liver because endogenous apolipoprotein E directs them to LDL receptors on hepatocytes. This creates two barriers for extrahepatic RNA medicine:

1. **Reduced target-cell delivery**: Off-target liver accumulation competes with delivery to the intended tissue.
2. **Dose-limiting hepatotoxicity**: Even intra-articular (joint) injections can result in systemic liver exposure at therapeutic doses, restricting safe dose escalation.

Osteoarthritis (OA) exemplifies this challenge. Chondrocytes — the primary cells maintaining joint cartilage — are notoriously resistant to transfection with standard LNPs. Existing vectors achieve poor chondrocyte delivery and unacceptable liver off-target activity even after local intra-articular administration.

#### Limitations of Existing Methods

Prior AI-guided LNP design systems all optimize for a **single objective** — transfection efficiency in one target cell type — ignoring off-target liver delivery:

- **AGILE** (Xu et al., *Nat. Commun.* 2024): deep learning for LNP discovery in HeLa cells and macrophages; single-objective; no selectivity constraint
- **LUMI-lab** (Xu et al., *Cell* 2026): foundation model platform for ionizable lipid discovery; single target cell
- **LiON** (Wang et al., *Nat. Commun.* 2024): AI-guided pulmonary LNP design; single target tissue
- **Witten et al.** (*Nat. Biotechnol.* 2025): AI for pulmonary gene therapy; single-objective
- **Li et al.** (*Nat. Mater.* 2024): ML + combinatorial chemistry; single-objective

Single-objective optimization creates a systematic blind spot: a lipid that is moderately efficient in both target and liver will always score below one that is highly efficient in the target alone, even if the latter is therapeutically unusable due to hepatotoxicity.

#### What MOLEA Contributes

MOLEA (Multiobjective LNP Engineering with AI) is the **first AI framework to jointly optimize LNP potency in a target cell type and minimization of off-target liver delivery** within a single design loop:

1. **Multiobjective training**: Fine-tuned on experimental data from both chondrocytes (target) and hepatocytes (off-target), enabling the model to learn selectivity patterns rather than just potency patterns.
2. **Lipid-specific pretraining**: Continual contrastive pretraining on 15M virtual lipids shifts the model latent space from generic chemistry to the ionizable lipid domain, improving downstream fine-tuning efficiency.
3. **Composite Targeting Score (TS)**: A post-inference ranking metric (TS = 2·ln(C/H) + ln(C)) that penalizes liver delivery 2× more than it rewards potency, embedding the selectivity requirement into the candidate selection process.
4. **Validated platform**: Predicts K9, a novel ionizable lipid achieving >90% chondrocyte transfection and 13.5-fold knee/liver selectivity improvement over the clinical benchmark SM-102, with durable CRISPR-Cas9 gene editing effects in both acute and chronic OA models.

---

### Method Overview

MOLEA is a graph-based deep learning system built around a modified **Graph Isomorphism Network (GINEConv)** architecture. For a detailed mathematical treatment see `doc_method.md`; for code verification see `doc_code.md`.

**Architecture**: Dual-branch encoder
- **Graph branch**: 5-layer GINEConv with batch normalization and mean pooling → 512-dim molecular embedding
- **Descriptor branch**: Mordred physicochemical descriptors (~1,825 features) → 100-dim compressed representation
- **Fusion**: Concatenation → 2-layer Softplus MLP regression head predicting log₂(mTP)

**Training pipeline**:
1. Self-supervised pretraining on 15M virtual lipids using NT-Xent contrastive loss (τ=0.1, cosine similarity; atom masking augmentation)
2. Supervised fine-tuning on 1,152 lipids with scaffold splitting (80/10/10); separate models for chondrocyte and hepatocyte targets; tiered Adam (backbone lr=1×10⁻⁴, head lr=5×10⁻⁴); 200 epochs
3. Virtual library screening of 40,755 synthetically accessible candidates using GNN-only inference (descriptor branch zero-padded)
4. Post-hoc TS ranking → experimental validation → DoE formulation optimization → in vivo testing

**Key biological assumption**: In vitro transfection efficiency in primary chondrocytes and hepatocytes predicts in vivo intra-articular selectivity. This assumption holds for K9 but has not been systematically validated across diverse cell types or delivery routes.

---

### Evaluation

#### Computational Benchmarks

| Metric | MOLEA | Random Forest | LightGBM | MLP |
|--------|-------|--------------|----------|-----|
| RMSE | Lowest | Higher | Higher | Higher |
| PCC | Highest | Lower | Lower | Lower |
| SCC | Highest | Lower | Lower | Lower |
| R² | Highest | Lower | Lower | Lower |

*(Exact numbers in Supplementary Table 1; scaffold-split test set)*

Ablation results confirm all model components are necessary: removing the Mordred descriptor encoder, edge embeddings, pooling module, or batch normalization each reduces performance (Supplementary Table 1).

#### In Vitro Validation

- **Library screen hit rate**: 2/9 MOLEA-predicted candidates (K2, K9) achieved strict multiobjective criterion (high chondrocyte TS) ≈ 22% hit rate; estimated dramatically better than chance (Figure 2l)
- **K9 chondrocyte mTP**: ~14.5 log₂ vs SM-102 baseline; K9 hepatocyte mTP: ~4.0 (Figure 2l)
- **K9 chondrocyte translation at 6 h**: ~70-fold higher GFP expression than SM-102 (Figure 3i)
- **K9 hepatocyte translation**: only 40–60% of SM-102 (Figure 3i) — bidirectional selectivity

#### In Vivo Selectivity (n=5 mice/group, C57BL/6)

- **Knee/liver bioluminescence ratio**: K9 = 40×; SM-102 = 5× → **13.15-fold improvement** (Figure 3d)
- **Knee/spleen ratio**: K9 = 130×; SM-102 = 10× → **18.82-fold improvement** (Figure 3e)
- Absolute joint delivery: comparable between K9 and SM-102 — selectivity is gained without potency sacrifice

#### Chondrocyte Specificity (Ai9 reporter, n=3 mice)

- K9: **90.30% chondrocyte tdTomato+** vs SM-102: 56.01% (Figure 4b)
- K9 hepatocyte off-target: ~7% vs SM-102 liver: higher off-target (Figure 4c)
- Within joint: **>60% of K9-transfected cells are chondrocytes**, despite chondrocytes being only ~3% of joint cells (Figure 4h) — ~20-fold enrichment

#### Gene Editing In Vivo

| Cargo | Model | K9 joint editing | K9 liver editing | LP01 joint editing |
|-------|-------|-----------------|-----------------|-------------------|
| CRISPR-Cas9 (sgTOM) | Ai9 | ~45% | ~8% | ~22% |
| Cas9 functional (flow) | Ai9 | 77.1% tdTomato+ | — | 43.2% |
| Base editing (ABE8e) | LumA | 7.24% A→G | 0.017% | 0.64% |

K9 achieves >400-fold joint/liver selectivity ratio for base editing vs LP01's 1.8-fold.

#### Therapeutic Efficacy

**Acute OA (MIA model, n=3–6 mice)** (Figure 6):
- OARSI score: untreated 5.5 → K9 × 2 doses 1.5 (vs WT 0.5)
- MMP13 protein: reduced to ~33% of untreated (100 vs 300 pg/mg)
- Cartilage thickness (SHG): 68.40 μm untreated → 150.00 μm after K9 × 2

**Chronic OA (DMM model, n=3–6 mice, 4-month follow-up)** (Extended Data Fig. 1):
- 10.97% editing maintained 4 months post-treatment
- Cartilage thickness: 55.65 μm untreated → 100.01 μm after K9 × 2 (sham: 125.39 μm)
- microCT: reduced ectopic mineralization and osteophyte formation
- Proteomics (Extended Data Fig. 2): NF-κB, PI3K-Akt, mTOR pathway suppression; complement pathway modulation

**Safety**: No elevation in TNF, IL-1β, IL-6, ALT, AST, creatinine, or BUN across all models (Supplementary Figs. 38–41).

---

### Reproducibility

**Rating: 3 / 5**

**Strengths**:
- Full codebase is publicly available (GitHub: `bowenli-lab/MOLEA`, MIT license; Zenodo: `10.5281/zenodo.18943783`)
- Pre-trained and fine-tuned model checkpoints are provided (`ckpts/model_pretrained_15M.pth`, `model_finetuned_Chondrocyte.pth`, `model_finetuned_Hepatocyte.pth`)
- Fine-tuning dataset (1,152 lipids with mTP labels) and virtual screening candidates (40,755 SMILES) are included in `data/`
- Pre-computed prediction results (`results/preds_Chondrocytes.csv`, `results/preds_Hepatocytes.csv`) allow immediate TS ranking without re-running inference
- All equations (Eqs. 1–9) are reported; most hyperparameters match code exactly

**Limitations**:
- **TS formula (Eq. 9) not implemented in code**: Users must manually compute the targeting score from prediction CSVs; no standardized pipeline is provided
- **Baseline comparison scripts absent**: RF, LightGBM, MLP benchmarks referenced in Supplementary Table 1 are not reproducible from the repo
- **Descriptor branch zero-padding undocumented**: Virtual library screening silently drops Mordred descriptors via `forward_only_h()`; users replicating the screening pipeline may be unaware
- **Epoch 14 checkpoint hardcoded**: `finetune.py` loads `model_14.pth` by name, not best validation checkpoint — requires matching training setup exactly to reproduce
- **Environment setup is non-trivial**: PyTorch 1.12.1 + PyTorch Geometric 2.2.0 with CUDA 11.3 dependencies; torch-scatter and torch-sparse require matching versions; no Docker container or conda lock file provided
- **In vivo data not deposited**: mRNA sequencing data available (PRJNA1440167); raw flow cytometry and IVIS quantification data are "available in the main text or Supplementary Information" but not in a structured data repository

**Practical notes for reproduction**:
1. Install with: `conda create -n molea python=3.9`, then `pip install torch==1.12.1+cu113 torch_geometric==2.2.0` and the matching `torch-scatter`, `torch-sparse` versions
2. Fine-tuning requires absolute data path hardcoded in `finetune.py:357` — must modify before running
3. For virtual library screening, use `infer.py <model_folder>` with the provided checkpoint folders; TS must be computed post-hoc from the output CSVs
4. Scaffold splitting is deterministic given the same RDKit version; metrics should reproduce exactly

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
