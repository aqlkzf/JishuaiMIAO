---
layout: default
permalink: /paper-atlas/pepprclip-56a227c9/
title: "PepPrCLIP"
nav: false
description: "PepPrCLIP 只要求输入目标蛋白的氨基酸序列。它先在 ESM-2 的肽表示附近加高斯扰动，产生大量短肽；再用一个仿照 CLIP 的双编码器，把候选肽与目标蛋白投影到同一空间，用余弦相似度排序。生成器回答“哪些序列像可行的天然短肽”，判别器回答“这些肽里哪一些更像当前目标的配对肽”。"
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
      <span>Science Advances · 2025</span>
    </div>
    <h1>PepPrCLIP</h1>
    <p>De novo design of peptide binders to conformationally diverse targets with contrastive language modeling</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1126/sciadv.adr8638" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PepPrCLIP 方法解读：先生成“像天然肽”的候选，再按目标配对排序

### 一句话理解

PepPrCLIP 只要求输入目标蛋白的氨基酸序列。它先在 ESM-2 的肽表示附近加高斯扰动，产生大量短肽；再用一个仿照 CLIP 的双编码器，把候选肽与目标蛋白投影到同一空间，用余弦相似度排序。生成器回答“哪些序列像可行的天然短肽”，判别器回答“这些肽里哪一些更像当前目标的配对肽”。

### 1. 为什么不是直接枚举短肽

长度为 20 的肽有约 $20^{20}$ 种组合，绝大多数不一定可表达、稳定或具有天然蛋白序列的统计特征。作者没有从均匀随机序列开始，而是从 PDB 共晶中已知会结合蛋白的短肽出发，利用蛋白语言模型表示空间的局部结构产生候选。

这是一种“先验约束的搜索”，不是条件生成模型：生成阶段并没有看到目标蛋白。候选库可以复用到不同目标；目标特异性只在后续 CLIP 打分阶段引入。其好处是一次生成、多次筛选，代价是生成器本身不会主动朝某个目标的结合界面优化。

### 2. 数据怎样定义“肽—蛋白配对”

作者从 PDB 相互作用结构提取短链与较长蛋白的共晶对，并构造两个集合：

- noisy 集合允许 buried surface area（BSA）$\ge 50\ \text{Å}^2$，短链长度小于 50 aa，覆盖强弱不同的相互作用；训练/验证/测试分别有 11,597、1,241、1,376 对。
- strict 集合要求 BSA $\ge 400\ \text{Å}^2$、肽长 $\le25$ aa、目标长 $\ge30$ aa；训练/验证/测试分别为 7,388、737、1,002 对。

肽和蛋白均用 MMseqs2 按 30% 序列同一性聚类，以降低训练和测试之间的同源泄漏。论文最终选择在更杂、更难的 noisy 数据上训练，并在 strict 数据上监控和测试；这比只在严格但更窄的数据上训练有更好的排序性能。

仓库提供 `Noisy_Dataset.csv`（14,214 行）与 `Strict_Dataset.csv`（9,127 行），包括最终序列和 cluster 列，但没有从 PDB 计算 BSA、筛链和运行 MMseqs2 的预处理代码。因此可以检查模型输入和后续分割，不能从原始 PDB 完整重建作者的数据集。

### 3. ESM-2 表示：把可变长度序列变成 1280 维向量

notebook 加载 `esm2_t33_650M_UR50D`。对每条肽或目标序列，取第 33 层逐残基表示，去除 BOS/EOS 后做平均：

$$
e(s)=\frac{1}{L}\sum_{r=1}^{L}h_r^{(33)}\in\mathbb{R}^{1280}.
$$

这些向量预先计算并保存到 pickle；训练 CLIP 时 ESM-2 不参与梯度更新。`model.eval()` 只关闭 dropout，本身不等于冻结参数，但 embedding 计算放在 `torch.no_grad()` 中且结果离线缓存，所以实际训练的确只更新后面的轻量投影网络。

### 4. CLIP 判别器怎样学会正确配对

肽和蛋白分别经过结构相同但参数独立的两层 MLP：

$$
p_i=f_p(e(pep_i)),\qquad r_j=f_r(e(prot_j)),
$$

其中每个投影头为 `Linear(1280,640) → ReLU → Linear(640,320)`。投影后做 L2 归一化，批内所有肽—蛋白组合的相似度矩阵是

$$
K_{ij}=\frac{p_i^\top r_j}{\lVert p_i\rVert_2\lVert r_j\rVert_2}.
$$

若一个 batch 中第 $i$ 条肽与第 $i$ 个蛋白是真实共晶对，正确答案就是矩阵对角线。损失同时从两个方向训练：

$$
\mathcal L=\frac12\left[
\operatorname{CE}(K,[0,1,\ldots,n-1])+
\operatorname{CE}(K^\top,[0,1,\ldots,n-1])
\right].
$$

第一项要求“给定一条肽，在一批蛋白中找到配对目标”，第二项要求“给定一个蛋白，在一批肽中找到配对肽”。notebook 的 `MiniCLIP.forward()` 确实先 `F.normalize()` 再矩阵乘法；`training_step()` 对 logits 和 logits 转置各做一次交叉熵后取平均。与标准 CLIP 不同，这里没有学习温度参数，原始余弦值直接作为 logits。

需要谨慎解释批内负样本：非对角组合被当作负例，但某些天然肽可能真实结合多个蛋白。论文在约 50 万个错配组合中也看到一部分高分，并明确认为其中可能含真实的多特异性，而不全是模型错误。

### 5. 如何评价“会排序”

作者报告三个指标：

- binary accuracy：给两对肽—蛋白时能否选出正确配对；
- top-1：在 64 个随机肽中，真肽是否排第一；
- top-10%：真肽是否进入前 10%。

在 noisy 上训练、strict held-out 测试时，三个指标分别为 95.4%、0.53 和 0.82。top-10% 更贴近实验筛选：若实验预算只能测试少数候选，排序前段的富集程度比二分类阈值更有意义。但这些负候选主要是批内错配，不能当作经过实验确认的不结合肽。

### 6. 生成器：在残基表示上加噪，再借 ESM-2 解码

对一条来源肽的逐 token 表示矩阵 $H$，论文将生成写作

$$
\widetilde H=H+Z,
$$

并用尺度 $k$ 控制扰动强度。代码的实际操作更具体：

```text
noise = randn(H.shape) * k * H.var()
H_tilde = H + noise
```

然后把 $\widetilde H$ 送入 ESM-2 自带 `lm_head`，只保留 20 种标准氨基酸的 logits，并在每个位置取 argmax，最后去掉首尾特殊 token。它不是自回归采样，也没有显式保证电荷、溶解性或结构；“naturalistic”来自种子肽邻域与 ESM-2 词汇头的先验。

图 2a 通过 Hamming distance 选择 $k$ 大约 5–22：$k=5$ 通常只改少数位点，接近 22 时大部分序列改变。发布 notebook 实际使用 `range(5,22,4)`，即 5、9、13、17、21 五个离散尺度，而不是在连续区间随机抽样。

还有一个重要 paper-code 差异：代码乘的是单个全局标量 `token_representations.var()`，即方差；它不是逐维标准差。旧解释若把该实现写成“$k\times std$”会改变扰动尺度，必须以当前 commit 的 `var()` 为准。

### 7. 从输入目标到最终候选

实际数据流是：

1. 从 noisy 数据中的天然结合肽选择多个 source peptide。
2. 以不同 $k$ 对其 ESM-2 残基表示加噪，并经 `lm_head` 解码，形成约十万级候选库。
3. 对所有候选和输入目标计算 mean-pooled ESM-2 向量。
4. 经训练好的两个 MLP 投影并归一化。
5. 计算每条候选与目标的余弦分数，降序返回 top-k。

因此 PepPrCLIP 的输出是优先列表，不是结合位点、复合物结构或实验亲和力。相似度范围虽在 $[-1,1]$，也没有被校准成结合概率。

### 8. 图 2–5 的证据层级

结构化目标的计算比较用 AlphaFold-Multimer 的 ipTM：在 209 个 strict test 目标上，PepPrCLIP top peptide 达到或超过真实共晶肽 ipTM 的比例为 17.7%，RFDiffusion 为 30.1%；PepPrCLIP 在 33% 目标上得到更高 ipTM。这个基准偏向能够使用目标结构的 RFDiffusion，同时 ipTM 是预测复合物置信度代理，不是实测亲和力。

实验验证覆盖三种目标：

- 结构稳定的 UltraID：20 条 PepPrCLIP 抑制肽中 19 条显示一定抑制，4 条超过 75%；这是酶活功能读数。
- 部分无序的 β-catenin：候选作为 peptide-guided ubiquibody 的 guide，部分构建体降低 TOPFlash 活性并促进蛋白酶体依赖降解；BLI 给出两个构建体约 200 nM 和 150 nM 的 $K_D$。
- 高度无序的 SS18–SSX1 融合癌蛋白：一条 uAb 构建体降低报告信号和内源蛋白水平。

这些结果说明序列优先排序能产生可用候选，但不是随机盲测的总体成功率估计。候选经过 top ranking、构建体融合和具体实验筛选，且每个目标测试数量较小。

### 9. 代码快照与复现边界

本地代码来自 `https://github.com/SuhaasBhat/PepPrCLIP`，commit `b64e14ec80be9d153f48303f9c4ccdf980277567`。核心训练、生成和快速推理都在两个 Jupyter notebook 中，没有 Python package、CLI 或自动化测试。

可直接核对的部分包括 ESM-2 embedding、双 MLP、对称损失、加噪和 LM-head 解码；CSV 也已包含。但端到端复现仍有边界：

- PDB mining、BSA 过滤和 MMseqs2 聚类脚本缺失。
- embedding pickle、十万肽缓存和预训练 checkpoint 不在 GitHub 快照中；官方 Hugging Face 模型需签署非商业研究许可。
- notebook 使用 `/content/drive/MyDrive/PepPrCLIP/...` 等 Colab/Drive 绝对路径，本地运行需逐项改写。
- 论文说训练 56 epochs、early-stopping patience=6；发布 notebook 没有固定 `max_epochs`，patience=3，不能保证复现论文训练轨迹。
- AlphaFold-Multimer、ColabFold 与 RFDiffusion 比较代码不在仓库，相关数值只能由论文和 data file S1 核对。
- 原始和处理数据另存 Zenodo `10.5281/zenodo.13917484`；代码仓库本身不是完整数据归档。

因此该快照足以理解和重跑核心 notebook 逻辑，但不是无需外部模型、许可和路径适配即可一键重现全文结果的发布包。

### 证据入口

- 论文：`paper source/PMC11753435/paper.md`，重点为 Fig. 1–5、CLIP training、Gaussian perturbation、Materials and Methods 与 availability。
- 补充：`output_supp_md/sciadv.adr8638_sm/auto/sciadv.adr8638_sm.md`，含 Fig. S1–S4 与算法/实验补充。
- 代码：`PepPrCLIP_repo/PepPrCLIP.ipynb`、`PepPrCLIP Quickstart.ipynb`、两个 CSV。
- 图像：`paper source/PMC11753435/images/`；图像解释以正文和图注为最终依据。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PepPrCLIP: De Novo Design of Peptide Binders to Conformationally Diverse Targets with Contrastive Language Modeling

### Paper Information

- **Authors**: Suhaas Bhat*, Kalyan Palepu*, Lauren Hong, Joey Mao, Tianzheng Ye, et al.
- **Corresponding Author**: Pranam Chatterjee (Duke University)
- **Journal**: *Science Advances* 11(4), eadr8638
- **Published**: January 24, 2025
- **DOI**: [10.1126/sciadv.adr8638](https://doi.org/10.1126/sciadv.adr8638)
- **Code**: [GitHub (SuhaasBhat/PepPrCLIP)](https://github.com/SuhaasBhat/PepPrCLIP) | [HuggingFace (ubiquitx/pepprclip)](https://huggingface.co/ubiquitx/pepprclip) (license required)
- **Data**: [Zenodo (10.5281/zenodo.13917484)](https://doi.org/10.5281/zenodo.13917484)

---

### Motivation & Novelty

#### Problem

Over 80% of pathogenic proteins are "undruggable" — they lack stable binding pockets required by small-molecule inhibitors. Existing computational binder design methods like RFDiffusion (*Nature*, 2023) require 3D structural information, excluding intrinsically disordered proteins, fusion oncoproteins, and conformationally flexible targets from design. Experimental approaches (yeast/phage display) are laborious and low-throughput.

#### Limitations of Existing Approaches

- **RFDiffusion** (Watson et al., *Nature*, 2023): State-of-the-art structure-based protein design. Generates high-quality binders but requires target 3D structure; cannot design for disordered regions.
- **PepNN** (Lei et al., *Nature Machine Intelligence*, 2023): Deep attention model for peptide binding site prediction on targets. Sequence-based but discriminative only (no generation capability).
- **Phage/yeast display**: Experimental binder screening. Covers diverse libraries but requires months of iterative selection and is target-specific.
- **bioPROTACs / AdPROMs / ubiquibodies**: Protein degradation platforms that rely on pre-existing "off-the-shelf" binders — cannot design new binders for novel targets.

#### Unique Contributions

1. **First purely sequence-based de novo peptide binder design**: No 3D structural information needed — only the target amino acid sequence
2. **Generative-discriminative pipeline**: Combines Gaussian perturbation of ESM-2 latent space (generative) with CLIP-based contrastive screening (discriminative)
3. **Validated on conformationally diverse targets**: Demonstrated functional binding and degradation on structured (UltraID, pLDDT=96.2), partially disordered (β-catenin, pLDDT=78.4), and highly disordered (SS18-SSX1, pLDDT=46.9) targets
4. **Orders of magnitude faster than structure-based methods**: ~1000 peptides/min generation + ~100,000 scored/min vs RFDiffusion's ~2 min per single binder

---

### Method Overview

PepPrCLIP (Peptide Prioritization via CLIP) is a two-stage pipeline:

**Stage 1 — Generation**: Naturalistic peptide candidates are generated by adding Gaussian noise to ESM-2-650M embeddings of known binder peptides, then decoding perturbed embeddings back to sequences via ESM-2's language model head. Noise scaling factor $k \in \{5-22\}$ controls diversity from near-wildtype to fully novel sequences.

**Stage 2 — Discrimination**: A CLIP-inspired contrastive model is trained on PDB-derived peptide-protein pairs to predict binding. Both peptide and protein sequences are encoded via frozen ESM-2 embeddings → 2-layer MLP projectors → 320-dimensional normalized vectors. Cosine similarity in this joint latent space predicts binding affinity. The symmetric cross-entropy loss (rows + columns) jointly optimizes for peptide→target and target→peptide matching.

**Key design choices**: (1) Transfer learning from noisy (BSA ≥ 50 Å²) to strict (BSA ≥ 400 Å²) dataset improves generalization; (2) Generation is unconditioned on the target, producing a reusable candidate library; (3) ESM-2's pre-trained representations provide implicit structural awareness without explicit 3D information.

See `doc_method.md` for full mathematical details and algorithm walkthrough. See `doc_code.md` for code-paper mapping.

---

### Evaluation

#### In Silico Benchmarking

**CLIP discriminator performance** (trained noisy, tested strict):
- Binary accuracy: 95.4%
- Top-1 accuracy: 53.0% (correct peptide ranked #1 from 64 candidates)
- Top-10% accuracy: 82.1% (correct peptide in top 10%)

**AlphaFold-Multimer benchmarking** (209 test proteins):
- PepPrCLIP in silico hit rate: 17.7% (generated peptide ipTM ≥ ground truth)
- RFDiffusion hit rate: 30.1% (with structural advantage)
- PepPrCLIP outperforms RFDiffusion on 33% of targets
- 22% PepPrCLIP peptides achieve ipTM ≥ 0.7 (vs 40% for RFDiffusion)

**Ablation study** (Fig. S1): ESM-2 embeddings for both encoders vastly outperform nn.Embedding (learned) and BLOSUM62 substitution matrix embeddings across all metrics.

#### Experimental Validation

##### Target 1: UltraID (structured enzyme, pLDDT = 96.2)
- 20 PepPrCLIP IPs tested, 19/20 showed inhibition
- 4/20 achieved >75% UltraID inhibition
- PepPrCLIP IPs significantly outperformed RFDiffusion IPs (P = 0.0364 overall, P = 0.0055 for top candidates)

##### Target 2: β-catenin (partially disordered, pLDDT = 78.4)
- 6 PepPrCLIP peptides tested as uAb guide peptides
- 4/6 showed significant reduction in β-catenin transcriptional activity (TOPFlash)
- β-cat_PpC_3 and β-cat_PpC_4: >50% proteasome-mediated β-catenin degradation
- Binding affinity: K_D = 200 nM (PpC_3) and 150 nM (PpC_4) by BLI
- Specific binding confirmed by ELISA (no BSA cross-reactivity)

##### Target 3: SS18-SSX1 fusion oncoprotein (highly disordered, pLDDT = 46.9)
- 10 PepPrCLIP peptides tested as uAb constructs
- SS_PpC_4: significant reduction in SS18-SSX1-mCherry fluorescence (P < 0.0001)
- >40% reduction in endogenous SS18-SSX1 protein levels by immunoblot

---

### Reproducibility

**Rating: 3/5** — Code available but notebook-only; key preprocessing scripts missing.

#### Strengths
- Core training and generation code provided in Jupyter notebooks
- Training datasets (Noisy_Dataset.csv, Strict_Dataset.csv) included in GitHub repo
- Raw data deposited to Zenodo
- Colab notebook with guided walkthrough available for inference

#### Weaknesses
- **Notebook-only implementation**: No modular Python package; entire pipeline in Colab notebooks with Google Drive paths
- **Missing preprocessing**: PDB mining, BSA filtering, and MMSeqs2 clustering scripts not provided
- **HuggingFace license restriction**: Official model weights require signing a noncommercial research-only license
- **Pre-trained model not in GitHub repo**: Must either train from scratch or access HuggingFace
- **Hardcoded paths**: Notebooks reference Google Drive locations (`/content/drive/MyDrive/PepPrCLIP/...`)
- **Minor hyperparameter discrepancy**: Early stopping patience=3 in code vs patience=6 in paper

#### Practical Notes
- **Environment**: Standard PyTorch + `fair-esm` + `pytorch-lightning`. No complex dependencies.
- **GPU requirements**: ESM-2-650M requires ~3GB VRAM. CLIP training is lightweight.
- **Training time**: Not reported, but expected to be fast (small MLP, pre-computed embeddings)
- **Common pitfall**: Must pre-compute ESM-2 embeddings before training; the pickle files are not included in the repo

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
