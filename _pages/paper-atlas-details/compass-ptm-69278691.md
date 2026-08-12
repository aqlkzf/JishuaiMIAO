---
layout: default
permalink: /paper-atlas/compass-ptm-69278691/
title: "COMPASS-PTM"
nav: false
description: "COMPASS-PTM 把 PTM 预测拆成一个“先粗后细”的两阶段问题：第一阶段 MSPN 先在蛋白序列上预测哪些残基可能发生哪些 PTM，第二阶段 ESPS 再把这些候选 PTM 位点和可能的调控酶连接起来，形成 enzyme-resolved 的调控假设。"
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
      <span>Protein &amp; Sequence Models</span>
      <span>Nature Communications · 2026</span>
    </div>
    <h1>COMPASS-PTM</h1>
    <p>Learning the PTM code through a coarse-to-fine mechanism-aware framework</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-73148-3" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## COMPASS-PTM 方法中文解读

### 一句话概括

COMPASS-PTM 把 PTM 预测拆成一个“先粗后细”的两阶段问题：第一阶段 MSPN 先在蛋白序列上预测哪些残基可能发生哪些 PTM，第二阶段 ESPS 再把这些候选 PTM 位点和可能的调控酶连接起来，形成 enzyme-resolved 的调控假设。

### 论文声称的核心逻辑

论文认为 PTM code 不只是“某个位置有没有某种修饰”，而是由多个 PTM 类型、局部序列环境、蛋白整体表示和调控酶共同决定的组合规则。传统方法常常把不同 PTM 类型或不同位点当成独立分类问题，因此难以表达 phosphorylation、ubiquitination、acetylation 等修饰之间的协同或拮抗关系，也无法回答“这个修饰可能由哪个 enzyme 调控”。

COMPASS-PTM 的解决方式是：

1. **MSPN**：学习 residue-level 的 multi-label PTM profile，也就是每个残基对应多个 PTM 类型的概率。
2. **ESPS**：在 MSPN 的 PTM-aware substrate representation 基础上，引入 enzyme embedding，预测 enzyme-substrate pairing。

这就是论文所谓 coarse-to-fine：Stage 1 给出粗粒度的 PTM program，Stage 2 给出更细的 enzyme-resolved regulatory map。

### Stage 1: MSPN 怎么做 PTM site profiling

论文中 Stage 1 的输入是蛋白序列片段 $S_{peptide}$，输出是每个位置对多个 PTM 类型的预测。论文描述的训练片段来自一个 greedy adaptive segmentation：每段最长 50 aa，并且覆盖至少一个已知 PTM site（`paper.md:183-187`）。

代码可验证的是：`models/dataset.py` 中 `load_data_` 读取已经准备好的 peptide、site、PTM 标签，并构造 residue-by-PTM 的 multi-label tensor（`models/dataset.py:91-155`）。推理辅助函数 `preprocess_sequence` 使用 50 aa 窗口并加 10 aa flank（`models/dataset.py:226-248`）。代码中未找到论文所说的完整 greedy annotated-site segmentation 脚本，因此这里是 **Partial**。

#### 1. PLM 分支

论文使用 ESM2-150M，并用 LoRA 做参数高效微调（`paper.md:189-197`）。代码中 `config_pep.py` 设置 `model_checkpoint = "facebook/esm2_t30_150M_UR50D"`（`models/config_pep.py:17-21`），`create_model_trans_bias` 用 PEFT 的 `LoraConfig` 设置 `r=16`、`lora_dropout=0.1`，目标模块是 attention 的 query/key/value（`models/model.py:289-329`）。

#### 2. 化学分支

论文说 chemical representation 包括 CLM 产生的 320 维表示，以及显式 physicochemical descriptors（`paper.md:197-198`）。代码中 `LoRAESMWithTransformer` 加载 `aa2selfies_embeddings.pt`，同时 `PhysChemEmbedder` 为氨基酸提供 molecular weight、pI、hydrophobicity、volume 四类特征（`models/model.py:70-113`, `models/model.py:215-236`）。

#### 3. Bio-Coupled and Augmented Fusion

论文把融合写成：

$$
\mathbf{H}_{s}^{\text{fused}} = \alpha\Phi(\mathbf{H}_{s}^{\text{prot}}, \mathbf{H}_{s}^{\text{chem}}) + \beta\Psi(\mathbf{H}_{s}^{\text{prot}}, \mathbf{H}_{s}^{\text{chem}})
$$

其中 $\Phi$ 是 gate，负责让化学特征只以有用方式调制主蛋白表示；$\Psi$ 是 residual mapping，负责保留跨模态互补信息（`paper.md:199-209`; `supplementary/supp.md:1531-1549`）。

代码可验证的是：`model.py` 把 ESM hidden、CLM feature、physicochemical feature 拼接，然后通过 `gated_feature_composer` 和 `res_info_composer` 分别生成 gated 和 residual 成分，最后用 learnable weights 组合（`models/model.py:240-277`）。

#### 4. Crosstalk-aware prompting

这是论文最关键的机制之一。论文先从 PTM co-occurrence 得到先验矩阵 $R_{prior}$，再学习矩阵 $R$。模型先生成每个位置的 preliminary PTM probability $\mathbf{p}_i$，再计算：

$$
B_{ij}=\mathrm{Dropout}(\tanh(\mathbf{p}_i^\top R\mathbf{p}_j))\gamma
$$

然后把 $B$ 加到 self-attention logits 上（`paper.md:211-237`）。

代码中 `CustomTransformerLayer` 直接对应这个逻辑：`crosstalk_matrix` 被设为可学习参数，经过两个 linear layer 投影，`ptm_predictor` 给出 `ptm_probs`，再用 `einsum` 计算 `B`，最后加到 `attention_scores`（`models/model.py:332-398`）。`preprocess_matrix.py` 中还有 NPMI matrix 的构建工具（`models/preprocess/preprocess_matrix.py:19-67`）。

#### 5. Hybrid loss

论文用 macro Dice/magnification loss 处理 PTM 类型长尾，用 micro focal loss 处理大量 unmodified residues 带来的样本不平衡：

$$
\mathcal{L}_{stage1}=\eta\mathcal{L}_{macro}+(1-\eta)\mathcal{L}_{micro}
$$

代码中 `HybridMacroMicroLoss` 组合 `ImprovedDiceLossWithMag` 和 `SimplifiedFocalLoss`，并且 `macro_weight` 是 learnable parameter（`models/loss.py:8-109`）。这部分代码和论文公式匹配较好。

### Stage 2: ESPS 怎么做 enzyme-substrate assignment

论文 Stage 2 使用 Stage 1 学到的 PTM-aware substrate representation，再加入 enzyme representation。核心融合公式是：

$$
\mathbf{H}_{fused} =
\alpha_0(\mathbf{g}_{substrate}\odot\mathbf{H}_{substrate})
+\alpha_1(\mathbf{g}_{enzyme}\odot\mathbf{H}_{enzyme})
+\alpha_2\mathbf{H}_{residual}
$$

代码中 `fusion_model_binary_2` 直接实现这个思路。它加载 `kinases_dict.json` 和 `kinase_embeddings_150m.npz`，根据 batch 中的 kinase id 取出 enzyme embedding；然后把 substrate hidden 和 kinase embedding 拼接，分别经过 `gate_substrate`、`gate_kinase` 和 `res_info_composer`，最后用 learnable 参数 `self.a` 加权求和并送入 MLP 预测二分类得分（`models/model.py:116-194`）。

`preprocess_kinase.py` 用 ESM 模型对 enzyme full-length sequence 做 mean pooling，生成 kinase embeddings（`models/preprocess/preprocess_kinase.py:31-72`）。这支持论文中“enzyme representation 来自 ESM2-150M”的说法。

### 代码和论文的边界

代码可验证的是核心模型结构：ESM2/LoRA、CLM+physicochemical fusion、crosstalk prompt attention、hybrid loss、ESPS dual-gated fusion。这些都能在 `models/model.py` 和 `models/loss.py` 中找到。

代码中未找到直接实现的是：完整 benchmark split 构建、MMseqs2 40% identity clustering、所有下游 variant/pathway rewiring case-study 脚本，以及论文描述的完整 greedy adaptive training segmentation。因此这些结果应视为论文和外部数据/脚本支持的结论，而不是当前 public snapshot 中完全可复现的代码行为。

### 学习这篇方法时最重要的抓手

理解 COMPASS-PTM 不要只看它用了 ESM2。真正的方法贡献在三个连接上：

1. **PTM 类型之间的连接**：用 crosstalk matrix 把 PTM co-occurrence 变成 attention bias。
2. **蛋白表示和化学表示的连接**：PLM 是主表示，CLM/physicochemical features 是辅助调制信号。
3. **site prediction 和 enzyme assignment 的连接**：Stage 2 不重新孤立建模，而是复用 Stage 1 的 PTM-aware substrate representation。

所以，COMPASS-PTM 更适合被理解为一个“PTM program representation + enzyme-resolved refinement”的框架，而不是单纯的 PTM site classifier。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## COMPASS-PTM

### Citation

Zhang, J., Cao, H., Gao, Z. et al. **Learning the PTM code through a coarse-to-fine mechanism-aware framework.** *Nature Communications* (2026). DOI: `10.1038/s41467-026-73148-3`.

### What Problem It Solves

Post-translational modifications form combinatorial regulatory patterns, but many predictors score one PTM or one site at a time and do not connect predicted sites to the enzymes that write or erase them. COMPASS-PTM reframes this as a two-stage problem: first infer a residue-level PTM program, then refine candidate sites into enzyme-substrate assignments.

### Method Overview

Stage 1, MSPN, is a multi-label site profiling network. It combines ESM2/LoRA protein representations, amino-acid chemical language embeddings, explicit physicochemical descriptors, a bio-coupled fusion module, and a crosstalk-aware prompt matrix initialized from PTM co-occurrence information. A hybrid Dice/magnification plus focal loss addresses class imbalance.

Stage 2, ESPS, reuses the PTM-aware substrate representation and pairs it with enzyme embeddings. A dual-gated residual fusion module combines substrate, enzyme, and interaction features to score enzyme-substrate compatibility.

### Evidence From The Paper

The paper reports strong improvements for multi-label PTM site prediction and enzyme assignment, including a 122% relative F1 improvement for multi-label site prediction and a 54% gain in zero-shot enzyme assignment (`paper.md:33-35`). It also reports motif recovery, variant-to-PTM disruption analysis, and case studies linking variants to inferred enzyme-network rewiring.

### Code Availability And Match

The paper's Code availability section lists `https://github.com/ZhangJJ26/COMPASS-PTM` and a Zenodo archive (`paper.md:285-287`). The cloned public code implements the central two-stage architecture:

- ESM2/LoRA, CLM/physicochemical fusion, crosstalk attention, and site classification in `models/model.py`.
- Hybrid stage-1 loss and binary stage-2 loss in `models/loss.py`.
- Stage-specific data loaders and training loops in `models/dataset.py` and `models/train.py`.
- NPMI prompt-matrix and kinase embedding preprocessing utilities in `models/preprocess/`.

Overall code-paper fidelity is **medium-high**. Core architecture is present, but full benchmark construction, MMseqs2 split scripts, and variant/pathway rewiring scripts were `Not found` in the searched public source snapshot. Reproduction depends on external datasets and checkpoints linked from the README.

### Reproducibility Rating

**Medium.** The public repository contains the core model/training code, mini data for format inspection, environment file, checkpoint download instructions, and a notebook inference path. It does not, by itself, contain every script needed to reproduce all benchmark tables and biological case-study analyses.

### Main Caveats

- The paper's broad "mechanism-aware" claims are best read as enzyme-resolved, specificity-aware predictions and hypotheses, not causal biochemical proof.
- Stage 2 is meaningful only for enzyme-mediated PTMs with curated enzyme-substrate annotations.
- Case-study rewiring figures should be treated as hypothesis generation unless independently validated.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
