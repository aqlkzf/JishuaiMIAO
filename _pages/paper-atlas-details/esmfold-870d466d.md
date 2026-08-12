---
layout: default
permalink: /paper-atlas/esmfold-870d466d/
title: "ESMFold"
nav: false
description: "ESMFold 用大规模蛋白语言模型把跨序列进化规律压缩进单序列表示，再通过序列/pair 交替更新、三角几何约束、结构模块和 recycling 生成原子坐标。它的突破是去掉每个目标的 MSA 搜索并获得高吞吐，而不是消除进化先验、计算成本或结构预测的不确定性。"
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
      <span>Science · 2023</span>
    </div>
    <h1>ESMFold</h1>
    <p>Evolutionary-scale prediction of atomic-level protein structure with a language model</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1126/science.ade2574" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ESMFold：语言模型怎样从单条蛋白序列生成三维结构

### 1. 论文在改变哪一个瓶颈

AlphaFold2、RoseTTAFold 等方法的高精度很大程度上依赖多序列比对（MSA）：先为目标蛋白搜索同源序列，再从共同进化模式中推断哪些残基可能在空间中接触。这个路线有效，却把数据库搜索和 MSA 构建放在推理前端；当目标扩展到数亿条宏基因组序列时，搜索成本会成为吞吐瓶颈，缺少深同源序列的蛋白也难以获得信息丰富的 MSA。

ESMFold 的问题不是“完全不使用进化信息”，而是“能否把进化信息预先压进一个大规模蛋白语言模型，然后预测时只输入一条序列”。论文先训练 ESM-2 系列语言模型，再冻结 3B 参数的 ESM-2，把它的内部表示交给一个 folding trunk 和等变结构模块，直接输出原子坐标与置信度。这样省去了每个目标的 MSA 搜索，但计算并没有消失：它被前移到大规模语言模型预训练，并在推理中保留语言模型、二维 pair 表示和三角更新的成本。

### 2. ESM-2 学到的首先是序列条件分布

ESM-2 使用 masked language modeling。对序列 $x=(x_1,\ldots,x_L)$ 随机遮盖部分残基，优化

$$
\mathcal L_{\mathrm{MLM}}
=-\sum_{i\in M}\log p_\theta(x_i\mid x_{\setminus M}).
$$

这个目标没有直接输入三维坐标。论文图 1 的核心证据是：随着语言模型从 8M 扩展到 15B 参数，注意力中可线性读取的长程接触精度提高，仅在语言模型上接一个结构模块时的 TM-score 也提高；序列 perplexity 的改善与结构预测改善高度相关。这说明结构信息在规模化序列建模中逐步显现，但不是说注意力图本身就是最终结构，也不是说 15B 模型直接用作最终 ESMFold folding trunk 的输入。

最终发布的 ESMFold 论文模型使用 3B ESM-2。当前源码 `esm/esmfold/v1/esmfold.py:35-47` 注册从 8M 到 15B 的多种 ESM-2，默认模型配置由权重文件提供；`esmfold.py:59-67` 加载语言模型、冻结参数、转为半精度，并为所有层设置可学习组合权重。论文的“15B”主要承担规模涌现实验，ESMFold 主模型则在准确率、内存和速度之间采用 3B 骨干，二者不能混为一谈。

### 3. 从一维语言表示到二维残基对表示

给定长度为 $L$ 的氨基酸序列，ESM-2 产生每一层的残基表示。源码 `esmfold.py:118-145` 加入 BOS/EOS，提取第 0 层到最后一层的 representation；`esmfold.py:193-210` 将其转换为 trunk 精度、从语言模型计算图中 detach，再用 softmax 归一化的层权重做加权和：

$$
h_i=\sum_{k=0}^{K}\operatorname{softmax}(w)_k h_i^{(k)}.
$$

随后 MLP 把 $h_i$ 投影为单残基状态 $s_i\in\mathbb R^{1024}$，并叠加氨基酸类型 embedding。若不使用语言模型注意力图，二维状态初始化为零矩阵 $z_{ij}\in\mathbb R^{128}$（`esmfold.py:202-210`）；相对位置编码在 trunk 内加入。也就是说，最终二维几何表示不是由预计算 MSA 直接提供，而是从语言模型的一维表示开始，在 folding blocks 中反复构造和更新。

### 4. Folding block：让序列状态和 pair 状态互相校正

默认 trunk 有 48 个 block，序列维度 1024、pair 维度 128（`esm/esmfold/v1/trunk.py:35-49`）。一个 block 的信息流可概括为：

1. 从 $z_{ij}$ 生成 self-attention bias，让残基 $i$ 对残基 $j$ 的注意力受当前 pair 几何假设影响。
2. 对序列状态做 gated self-attention 和 MLP 更新。
3. 将新的序列状态通过 outer product 与 outer difference 写回二维 pair 状态。
4. 对 pair 状态执行 triangular multiplicative update、triangle attention 和 pair MLP。

若用简化符号表示，序列到 pair 的核心是

$$
z_{ij}\leftarrow z_{ij}
+W_o\,[q_i\odot k_j\,\Vert\,q_i-k_j].
$$

当前 `esm/esmfold/v1/misc.py:245-269` 直接计算 `prod = q * k` 与 `diff = q - k`；`tri_self_attn_block.py:25-160` 串起 pair-to-sequence bias、序列注意力、sequence-to-pair 和三角更新。三角操作很重要，因为一组三维距离必须满足跨三个残基的几何一致性；只分别预测每一对残基，很容易得到彼此矛盾的局部关系。

这个 trunk 是对 Evoformer 的简化，而不是完全抛弃 AlphaFold2 的结构思想：ESMFold 移除了显式 MSA 轴处理，却保留了 pair 表示、三角更新以及后续 OpenFold 结构模块。

### 5. 结构模块与 recycling

trunk 的最终序列/pair 状态被投影到 OpenFold 的 StructureModule（`trunk.py:138-146`）。该模块通过 invariant point attention 等几何等变操作输出 backbone frame、扭转角和 atom14/atom37 坐标。模型不是只跑一次：前一轮坐标被转换为 Cβ 距离分箱，与归一化后的序列/pair 状态一起送回下一轮，这就是 recycling。

论文正文写“三步 recycling”。当前代码需要谨慎读：`FoldingTrunkConfig.max_recycles=4`，`trunk.py:173-177` 在显式传参时把用户所说的 recycle 次数加 1，因为第一次只是标准 forward；默认则直接执行配置给出的总迭代数。`esmfold.py` 的两个 docstring 对“3 recycles”与配置“4”也使用了不同口径。最合理的对应是三次回收更新加一次初始 pass，而不是论文与代码必然训练了不同模型。复现实验时仍应记录实际权重配置和 API 参数，不能只凭文字猜循环次数。

训练时早期 recycle 在 `torch.no_grad()` 下执行，只有最后一次保留梯度；这节省显存。当前 `trunk.py:150-155` 还提供 chunked axial attention，用更顺序的计算换取更低内存。它主要缓解 attention 中间张量，不会把整个含 pair 状态和三角计算的模型简单变成全局 $O(L)$ 内存/时间。

### 6. 输出不只是坐标，还包括“我有多相信”

`esmfold.py:232-276` 从最终表示生成三类重要输出：

- distogram：对每个残基对输出 64 个距离分箱 logits，并对称化；
- pLDDT：由结构模块 hidden states 预测每个原子的 50-bin LDDT 分布，再求期望并缩放到 0–100；
- pTM 与 predicted aligned error：由 pair 表示上的 64-bin head 计算全局拓扑置信度和残基对齐误差。

pLDDT 偏向局部结构可靠性，pTM 更关注整体域排列。高置信度是模型校准后“更可能准确”的指标，不是实验验证，也不意味着功能注释或复合体界面一定正确。论文图 2C 在 CAMEO 上展示 pLDDT 与真实 LDDT 的校准；其结论适用于相似评估分布，不能无条件外推到任意无序蛋白、人工设计序列或超长多域蛋白。

### 7. 四幅主图怎样构成证据链

- **图 1：结构信息随语言模型规模显现。** A–D 看无监督接触预测，E–F 看只接结构模块后的原子级预测。较大模型总体更好，但具体蛋白可能在某个规模阈值发生跃迁；perplexity 是理解程度的相关指标，不是准确结构的充分保证。
- **图 2：ESMFold 的架构、比较、校准和失败案例。** A 是“ESM-2 → folding trunk → structure module → 坐标/置信度”；B 显示单序列 ESMFold 在 CAMEO 上接近 RoseTTAFold，但总体低于使用 MSA 的 AlphaFold2；C 展示置信度校准；D/E 同时给成功与失败案例。T1074 的高 perplexity 16.6 对应明显低于 AlphaFold2 的 TM-score，提醒模型不理解序列时不能相信几何输出。
- **图 3：把推理速度转化为宏基因组规模。** 论文折叠超过 6.17 亿条 MGnify90 序列，约 3.65 亿达到 mean pLDDT>0.5 且 pTM>0.5，约 2.25 亿达到两个分数均 >0.7。Foldseek 相似性分布、UMAP 和序列同源性分析描述预测结构空间；这些是预测与检索结果，不等同于发现了同等数量的新实验 fold。
- **图 4：预测结构的实例解释。** 将若干宏基因组预测同时与 AlphaFold2 预测和最近 PDB 结构叠合，并展示低序列一致但结构相似的案例。它支持远缘结构关系探索，却仍依赖预测置信度和 Foldseek/PDB 覆盖。

补充材料为数据集构建、训练、评估、复杂度、消融和 Atlas 分析提供细节。例如论文报告 folding head 使用约 25,000 个 PDB cluster（约 325,000 个实验结构）以及约 1,200 万个 AlphaFold2 蒸馏结构；消融显示移除语言模型导致明显下降，而关闭 recycling、三角更新或蒸馏也会带来较小但一致的下降。

### 8. 训练证据与本地代码证据不能混写

论文报告 ESM-2 预训练、PDB 时间切分、AlphaFold2 蒸馏、crop、损失和大规模 GPU 推理。这些是论文证据。本地仓库主要提供模型定义、权重加载与推理接口，没有完整发布：

- ESM-2/ESMFold 的端到端训练循环；
- PDB clustering 和约 1,200 万蒸馏结构的数据生产管线；
- 论文所用完整 loss 调度、采样与训练运行配置；
- 在约 2,000 张 GPU 上两周生成 6.17 亿结构的生产编排；
- CAMEO/CASP/Atlas 全部 benchmark 的一键复现环境。

因此 `doc_code.md` 将推理架构标为高匹配是合理的，但不能据此声称训练过程已由当前源码端到端复现。OpenFold 提供的模块和 loss 原语也不等于论文训练脚本存在。

### 9. 单体、复合体与多链推理的边界

当前 `ESMFold.infer()` 接受以冒号分隔的多链序列。`esmfold.py:280-304` 与 `misc.py:18-58` 用 25 个 glycine linker 连接链，并让不同链的 residue index 相隔 512；输出时 linker mask 被移除。这是一种实用推理编码，而不是独立的、显式建模化学计量和配对 MSA 的 multimer 训练体系。

论文图 2D 的二聚体和四聚体案例证明某些复合体可成功预测，不代表所有界面都达到单体同等可靠性。对于未知寡聚状态、诱导契合、配体/金属依赖、膜环境或无序区，仍需要实验与专门模型验证。

### 10. 版本与复现边界

本工作区当前代码实际状态为：

- Git HEAD：`206cc19ca89d985245ca204fbc86772e5c2446d0`；
- Python 包版本：`fair-esm 2.0.1`（`esm/version.py`）；
- 旧合同记录提交：`2b369911bb5b4b0dda914521b9475cad1656b2ac`，与实际 checkout 不一致；
- `esm/esmfold/v1/pretrained.py` 明确区分论文使用的 `esmfold_3B_v0` 与后续 `esmfold_3B_v1`。

因此，本次代码锚点描述当前 2.0.1 快照，并用 `esmfold_v0()` 的注释确认论文模型入口；不能假设默认加载的 v1 权重与论文所有表格逐点相同。真正重现论文数值还需锁定 v0 权重、ESM-2 权重、OpenFold/DeepSpeed/PyTorch 依赖、数据时间切分、硬件、推理 recycle/chunk 参数和评估脚本。

工作区包含 Science 论文及其补充内容的 HTML 合并稿、预印本 PDF、既有图分析和源码，但没有独立抽取的图像目录，也没有本地模型权重与全部大型数据集。这里完成的是“论文机制—图证据—当前推理源码”的可核查解释，不是对 6.17 亿 Atlas、训练过程或全部 benchmark 的重新执行。

### 11. 一句话抓住 ESMFold

ESMFold 用大规模蛋白语言模型把跨序列进化规律压缩进单序列表示，再通过序列/pair 交替更新、三角几何约束、结构模块和 recycling 生成原子坐标。它的突破是去掉每个目标的 MSA 搜索并获得高吞吐，而不是消除进化先验、计算成本或结构预测的不确定性。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## ESMFold: Evolutionary-Scale Prediction of Atomic-Level Protein Structure with a Language Model

**Authors**: Zeming Lin*, Halil Akin*, Roshan Rao*, Brian Hie* et al.
**Journal**: Science, Vol. 379, No. 6637, pp. 1123–1130 (March 2023)
**DOI**: 10.1126/science.ade2574
**Code**: https://github.com/facebookresearch/esm

---

### Motivation & Novelty

#### Biological Problem

Protein structure prediction from amino acid sequence is fundamental to understanding biological function. While AlphaFold2 (Jumper et al., *Nature* 2021) achieved near-experimental accuracy, it requires constructing multiple sequence alignments (MSAs) by searching large sequence databases — a process taking 10+ minutes with high-sensitivity protocols. This creates two bottlenecks: (1) MSA search doesn't scale to the billions of metagenomic protein sequences being discovered through environmental sampling, and (2) many metagenomic proteins lack sufficient evolutionary relatives for informative MSAs.

#### Limitations of Existing Approaches

| Method | Journal | Year | Key Limitation |
|--------|---------|------|----------------|
| AlphaFold2 | Nature | 2021 | Requires MSA search (10+ min per protein); Evoformer deeply integrates MSA processing |
| RoseTTAFold | Science | 2021 | Three-track architecture also MSA-dependent; degrades substantially on single sequences |
| ColabFold | Nature Methods | 2022 | Reduces MSA search time but still requires external database queries |
| ESM-1b | PNAS | 2021 | 650M params; showed contacts emerge but not atomic-resolution structure |
| AlQuraishi (2019) | Cell Systems | 2019 | End-to-end single-seq prediction but backbone only, pre-language-model era |

#### Unique Contributions

1. **Scaling law for structural emergence**: Demonstrates that atomic-resolution structure prediction emerges in protein language models scaled from 8M to 15B parameters, with near-perfect correlation (−0.99) between perplexity and prediction accuracy.

2. **MSA-free architecture (ESMFold)**: Replaces AlphaFold2's Evoformer with a simplified "Folding Block" that takes single-sequence language model representations. Achieves competitive accuracy (TM-score 0.83 on CAMEO vs 0.82 for RoseTTAFold with MSAs) while being 6–60× faster on forward pass alone.

3. **ESM Metagenomic Atlas**: First large-scale structural characterization of metagenomic proteins — 617M structures, 225M at high confidence, completed in 2 weeks on ~2,000 GPUs. Reveals millions of novel folds not represented in experimental databases.

---

### Method Overview

ESMFold is an end-to-end single-sequence protein structure predictor built on the ESM-2 language model. The pipeline has three components:

**ESM-2 Language Model** (pre-trained, frozen): A BERT-style masked language model trained on ~65M protein sequences from UniRef50/90 via the masked language modeling objective. The 3B-parameter variant (36 layers, 2560-dim) is used for ESMFold — the largest that fits in a single GPU's memory. All hidden layer representations are extracted and combined via a learned weighted sum.

**Folding Trunk** (48 blocks): Each block maintains a sequence representation (1024-dim) and a pairwise representation (128-dim). The key simplification over AlphaFold2's Evoformer: MSA axial attention is replaced with standard self-attention biased by pairwise features. A novel "outer product + outer difference" operation communicates from sequence to pairwise space. Triangular multiplicative updates and triangular attention (from AlphaFold2) process the pairwise representation. All output projections are zero-initialized for training stability in the deep stack.

**Structure Module + Recycling**: OpenFold's implementation of AlphaFold2's Invariant Point Attention (IPA) converts representations to 3D atomic coordinates. The system recycles 4 times, feeding back a distogram computed from predicted Cβ positions. See `doc_method.md` for full mathematical details.

---

### Evaluation

#### Structure Prediction Accuracy

| Metric | ESMFold | AlphaFold2 (MSA) | RoseTTAFold (MSA) | AF2 (single-seq) |
|--------|---------|-------------------|--------------------|--------------------|
| CAMEO TM-score | 0.83 | 0.88 | 0.82 | 0.41 |
| CASP14 TM-score | 0.68 | 0.85 | 0.81 | 0.38 |

ESMFold matches RoseTTAFold on CAMEO and massively outperforms both AF2 and RoseTTAFold when MSAs are ablated. The gap to AF2-with-MSA is larger on the harder CASP14 set (0.68 vs 0.85), where MSA information is more critical.

**Confidence calibration**: pLDDT correlates with true LDDT at r=0.86 on CAMEO. For high-confidence predictions (pLDDT > 0.7), ESMFold LDDT=0.83 vs AF2 LDDT=0.85. When pLDDT > 0.9, median all-atom RMSD₉₅ = 1.42Å — approaching experimental accuracy.

**Ablation** (Figure S3): Language model removal causes the largest degradation (LDDT 0.74 → 0.58, −0.16). Removing folding blocks (LM + structure module only): 0.74 → 0.66 (−0.08). Other ablations (recycling, triangular updates, distillation) cause 0.01–0.04 LDDT changes. This confirms the language model is the critical component.

#### Speed

ESMFold predicts a 384-residue protein in 14.2 seconds on V100, 6× faster than a single AF2 model on forward pass alone. For shorter sequences, speedup reaches 60×. Crucially, this excludes MSA search time (10+ min), making the practical speedup 1–2 orders of magnitude.

#### Metagenomic Atlas

617M MGnify90 sequences folded in 2 weeks on ~2,000 GPUs. Results:
- 365M predictions with good confidence (59%): pLDDT > 0.5 and pTM > 0.5
- 225M high-confidence predictions (36%): pLDDT > 0.7 and pTM > 0.7
- 113M very high-confidence predictions: pLDDT > 0.9

**Structural novelty** (from 1M high-confidence subsample):
- 76.8% distinct from UniRef90 (< 90% sequence identity)
- 12.6% have no similar fold in PDB (TM-score ≤ 0.5) — novel structures
- 2.6% have both low structural AND low sequence similarity — deeply novel
- Remote homology: structures enable functional annotation impossible from sequence alone (Figure 4B,C)

#### Multimer Prediction

ESMFold matches AlphaFold-Multimer's DockQ quality category for 53.2% of chain pairs on 2,978 recent complexes, despite never being trained on complexes. Uses a poly-glycine linker (25 residues) and residue index offset (512) to encode chain boundaries.

---

### Reproducibility

**Rating: 3/5**

#### Strengths
- **Inference code fully open-source** (MIT license): Complete model architecture, pre-trained weights, and inference pipeline. `pip install fair-esm` provides immediate access.
- **Pre-trained weights available**: All ESM-2 scales (8M–15B) and ESMFold variants (v0, v1, ablation models) downloadable.
- **Clear evaluation protocol**: Temporal holdout (May 2020 cutoff), standard test sets (CAMEO, CASP14), standard metrics (TM-score, LDDT, DockQ).
- **ESM Metagenomic Atlas**: All 617M structures publicly available (https://esmatlas.com).
- **Data available**: CC-BY license for data.

#### Limitations
- **Training code not released**: No training loop, loss computation, data loading, distillation pipeline, or optimization infrastructure. The 125K+25K step training protocol, rejection sampling, and 75/25 distillation ratio cannot be independently verified or reproduced.
- **Computational requirements**: ESM-2 15B required FSDP on multi-GPU clusters; ESMFold training presumably required similar scale. Not reproducible without large compute budgets.
- **OpenFold dependency**: Structure module, triangular operations, and loss functions come from OpenFold. Version compatibility and exact behavior depend on the OpenFold snapshot used.
- **No supplementary data released**: Intermediate datasets (AlphaFold2 distillation structures, filtered training PDB clusters) are not available.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
