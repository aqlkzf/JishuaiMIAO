---
layout: default
permalink: /paper-atlas/decode-3c34eef0/
title: "DECODE"
nav: false
description: "DECODE 用带已知细胞比例的“伪组织”训练一个深度网络，把组织级转录组、蛋白组或代谢组向量映射成细胞类型/状态比例。它先用目标组织参与的对抗训练缩小 reference 与 target 的域差异，再用人工杂质细胞和注意力掩码学习相对去噪；推断时根据目标中是否可能含有 reference 未覆盖的细胞类型，选择绕过或经过 denoiser 的路径。"
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
      <span>Deconvolution</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>DECODE</h1>
    <p>DECODE: deep learning-based common deconvolution framework for various omics data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03007-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for DECODE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/forceworker/DECODE" target="_blank" rel="noopener noreferrer" aria-label="Open code for DECODE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DECODE 中文方法解读

### 一句话理解

DECODE 用带已知细胞比例的“伪组织”训练一个深度网络，把组织级转录组、蛋白组或代谢组向量映射成细胞类型/状态比例。它先用目标组织参与的对抗训练缩小 reference 与 target 的域差异，再用人工杂质细胞和注意力掩码学习相对去噪；推断时根据目标中是否可能含有 reference 未覆盖的细胞类型，选择绕过或经过 denoiser 的路径。

### 问题、输入与输出

设单细胞参考含 $n$ 个细胞类型、每个细胞有 $f$ 个共同分子特征。目标组织只有一个聚合向量 $X_{\mathrm{Target}}\in\mathbb{R}^f$，希望输出比例

$$
\hat P=(\hat p_1,\ldots,\hat p_n),\qquad \hat p_i\ge 0,\quad \sum_i\hat p_i=1.
$$

传统方法往往针对 RNA 或空间表达的特定统计结构。DECODE 尝试用相同网络处理 transcriptomics、proteomics 和 metabolomics，并进一步把离散的 pseudotime、cell-cycle phase、drug-response time point 当作“细胞状态类别”进行比例估计。

这里有一个重要边界：Stage 2 会把实际 target-tissue 数据作为无比例标签的目标域输入，因此训练是面向当前目标数据集的域适配，不是训练一次后对任意新队列直接零样本推断。

### 四阶段流程

```text
单细胞 reference（特征 + 类型/状态标签）
  │
  ├─ Stage 1：随机比例抽样并求和 → 有真值比例的 train-tissue
  │                                      │
目标 tissue（无比例真值） ─ Stage 2：encoder + discriminator + eDeconvolver
                                         │ 对抗对齐两个域，转移并冻结 encoder
train-tissue + 两份人工杂质 ─ Stage 3：DimExpander → denoiser → attention → deconvolver
                                         │ 比例监督 + contrastive loss
  └─ Stage 4：target → encoder → [可选 denoiser] → Softmax 比例
```

#### Stage 1：构造带标签的伪组织

先对每个类型抽取 $r_i\sim U(0,1)$，归一化得到

$$
p_i=\frac{r_i}{\sum_j r_j}.
$$

给定每个伪组织的总细胞数 $m$，按 $\operatorname{round}(p_i m)$ 从相应类型抽取细胞，必要时有放回抽样；实际计数再次归一化为训练标签。所有抽到的单细胞特征逐元素求和，形成一条组织级输入。代码对应 `data/data_process.py:118-150`。

为模拟 reference 缺少的细胞，代码还从每个已知类型抽一个细胞，并对每个特征独立生成跨类型的 Dirichlet 权重，再做加权求和，得到人工 impurity cell（`data_process.py:90-115`）。每个训练伪组织两次加入不超过 $0.1m$ 个杂质细胞，形成两个 noisy view。它不是一种真实未知细胞生成模型，而是有意制造“每个特征可能来自不同类型组合”的困难扰动。

#### Stage 2：用对抗训练对齐 reference 与 target

Stage 2 包含三个模块：

- Encoder：把 $f$ 维输入压到 256 维隐空间。
- eDeconvolver：从 train-tissue 隐表示预测已知比例。
- Discriminator：判断隐表示来自 train-tissue 还是 target-tissue。

每个 batch 做两次更新。第一次同时最小化比例预测误差和正常域分类 BCE；第二次交换域标签，迫使 encoder 生成不易区分来源的表示。论文把比例项称为 L1 loss，但本地 `model/utils.py:143-145` 实际计算 `mean(square(pred-gt))`，即 MSE。这会改变“异常大误差”的惩罚方式，是实质性 paper-code mismatch。

另一个结构差异是：论文模型段落描述 EncoderBlock 包含 LayerNorm，而 `model/stage2.py:19-27` 只有 Linear、LeakyReLU 和 Dropout。Stage 2 结束后，notebook 把最优 encoder state dict 载入 Stage 3；Stage 3 还在训练循环中冻结名称含 `encoder` 的参数（`deconv_model_with_stage_2.py:201-204`）。

#### Stage 3：分离“保留特征”与“噪声特征”

冻结 encoder 后，DimExpander 用一个线性层把 256 维表示扩展并 reshape 为 $(B,C,w)$。MaskingNet 对它做四头 self-attention，输出两个经 ReLU 的 mask；两个 mask 分别与输入逐元素相乘，产生代码命名的 `noise` 和 `extract_cell`。后者经线性 attention 汇聚、两层 decoder 和 Linear+Softmax 得到比例。

每个 batch 有三次比例预测：两个 noisy view 走 denoiser，干净伪组织走 `pure_forward()`。代码总损失是

$$
L=\alpha(L_1+L_2+L_3)+\beta\frac{L_{\mathrm{NCE}}}{2},
$$

其中三个所谓 $L_i$ 实际都是 MSE，论文公式则写成未显式加权的 L1 与 denoiser loss 之和。`Alpha`、`Beta` 和除以 2 是代码中的额外权重语义（`deconv_model_with_stage_2.py:250-264`）。

Contrastive 部分把同一采样位置的 clean 与 purified feature 作为正对，把 clean 与任意 noise position 作为负对，温度为 0.07。关键实现边界是 `PatchNCELoss` 在计算前对 purified 和 noise tensors 调用 `detach()`（`model/utils.py:161-188`）。因此 NCE 不直接回传进 MaskingNet；它主要更新 shared sampling MLP 和 clean-path 的非冻结投影。旧解释把“对比损失直接训练 denoiser”当作代码事实，证据并不支持这么强的说法。

#### Stage 4：两条推断路径

- reference 覆盖了目标的全部细胞类型：`pure_forward()`，绕过 MaskingNet。
- 目标可能含未知细胞类型：`forward()`，使用 denoiser，输出的是已知类型之间的相对比例。

路径由 notebook/调用者传入 `if_pure` 布尔值；代码没有自动检测未知细胞类型的机制（`model/utils.py:13-43`）。所以“自适应选择”在算法描述上成立，但实际需要用户预先判断并设置开关。

### 评估如何读

论文主要使用 CCC、RMSE 和 Pearson $r$。代码 `compute_metrics()` 先把所有样本×类型摊平成一维，再计算一个全局 CCC/RMSE/Pearson，而不是逐类型后平均（`model/utils.py:56-69`）。因此复现时必须区分“global”与图中按 cell type 展示的分布。

六张主图给出的证据是：

- Figure 1 展示四阶段结构、两条推断路径和 mask/contrastive 配对设计。
- Figure 2 在 7 个 transcriptomics/proteomics 场景中比较 CCC，并展示空间预测、真实 bulk、内存和时间；DECODE 在所示 CCC 中总体领先，但论文也承认部分场景的 Pearson 被其他方法略超。
- Figure 3 显示 liver metabolomics 的类型间 Kendall 相似度约 0.93-0.95，明显高于 RNA/蛋白；DECODE 在三组代谢组比较中总体最好，但 liver CCC 略低于 MuSiC。不能从图中推出“其他方法全部不可用”。
- Figure 4 支持三类细胞状态任务，但 pseudotime 被离散为 10 类，输出不是连续轨迹。
- Figure 5 显示 unknown cells、乘性噪声和 feature deletion 下的鲁棒性；DECODE 优势在代谢组最明显。图本身不单独证明优势只来自 contrastive module，需要结合消融。
- Figure 6 比较 CITE-seq RNA/蛋白的一致性，并把模型用于乳腺癌与肝脏多组学队列。后两者是应用性关联分析，不是已知真实细胞比例的基准。

旧 summary 中的许多 CCC 是从栅格箱线图估读的近似值，不应当作源数据精确数字；若需要精确复核，应使用论文 Source Data。

### 代码覆盖与可复现性

本地代码覆盖 Stage 1、Stage 2、Stage 3、预测与三项主要指标，并提供 lung RNA 与 bone-marrow metabolomics notebooks、示例 h5ad 和预训练权重。代码—论文总体匹配度为 **Medium**：核心数据流可以核查和运行示例，但存在以下边界。

- 论文称 L1，代码为 MSE。
- Stage 2 encoder 和最终 deconvolver 缺少论文描述的若干 LayerNorm/LeakyReLU。
- 论文总损失未写 `Alpha/Beta` 和 NCE `/2`。
- 论文说按“largest eigenvalue”归一化；代码是逐样本除以最大特征值（`data_process.py:152-160`）。
- `fit()` 中构造的 `test_with_noise_all` 随后被无条件置为空列表（`data_process.py:177-179`），影响该返回面上的噪声测试数据。
- Kendall、CV、KL、Spearman 等论文分析指标与多数比较/队列分析脚本在当前仓库 **Not found**；论文另指向 Experiment Records/Zenodo。
- 工作流以 notebook 为入口，没有 CLI、package API 或 tests；environment.yml 提供 Python 3.8/PyTorch 2.0/CUDA 11.8 环境线索。

### 最终理解

DECODE 的核心不是“一套网络天然理解所有 omics”，而是把不同模态都压成共同的 feature vector 学习问题：伪组织提供监督，目标组织提供无监督域信息，人工杂质提供鲁棒性训练。它在论文数据上展示了很广的适用范围，但实际使用者必须重新准备同维特征、针对目标队列做 Stage 2 适配、判断是否启用 denoiser，并注意论文公式与代码损失/层结构的差异。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DECODE: Deep Learning-based Common Deconvolution Framework for Various Omics Data

**Paper**: Zhao, T., Liu, R., Sun, Y., et al. *Nature Methods* 23(3), 2026.
**DOI**: [10.1038/s41592-026-03007-y](https://doi.org/10.1038/s41592-026-03007-y)
**Code**: [https://github.com/forceworker/DECODE](https://github.com/forceworker/DECODE)

---

### Motivation & Novelty

Cell-type deconvolution estimates cellular abundances from tissue-level (bulk) omics data using single-cell references. Existing methods are modality-specific: MuSiC (*Nature Communications*, 2019) and CIBERSORTx (*Nature Biotechnology*, 2019) handle bulk transcriptomics; RCTD (*Nature Biotechnology*, 2022), SPOTlight (*Nucleic Acids Research*, 2021), Tangram (*Nature Methods*, 2021), and cell2location (*Nature Biotechnology*, 2022) target spatial transcriptomics; scpDeconv (*Nature Communications*, 2023) specializes in proteomics. No method spans all three omics, and **metabolomics deconvolution** has no dedicated tool. Using different methods per omics introduces systematic biases in cross-omics cohort comparisons.

**DECODE** is presented as a common deconvolution framework for transcriptomics, proteomics, and metabolomics, addressing a sparsely served metabolomics setting. Its four-stage architecture combines adversarial domain adaptation (Stage 2) with contrastive-learning-based denoising (Stage 3), enabling:

1. **Cross-omics universality** — one model for three omics modalities
2. **Robustness to incomplete references** — handles unknown cell types via noise separation
3. **Batch-effect correction** — adversarial training aligns pseudo-tissue and target domains
4. **Cell state deconvolution** — extends beyond cell types to pseudotime, cell cycle, and drug response states

### Method Overview

DECODE operates in four stages:

1. **Stage 1 — Pseudo-tissue generation**: Sample cells from single-cell reference at random proportions, aggregate into pseudo-bulk profiles. Generate artificial "noise cells" (weighted mixtures across cell types) to simulate unknown cell types.

2. **Stage 2 — Adversarial batch-effect removal (DANN)**: Train encoder + discriminator + eDeconvolver jointly. Two optimization steps per batch: (a) minimize prediction loss + domain classification loss, (b) reverse domain labels to fool the discriminator. Freezes encoder weights afterward.

3. **Stage 3 — Contrastive denoising (MBdeconv)**: Adds noise cells to training pairs. Self-attention-based MaskingNet separates purified cell features from noise features. PatchNCE contrastive loss maximizes similarity between clean and purified features, minimizes similarity to noise features. Three parallel predictions (two noisy + one clean path) supervised by L1 loss.

4. **Stage 4 — Inference**: Two pathways — pure mode (when reference covers all tissue cell types) bypasses denoiser; denoising mode (when unknown cell types exist) routes through MaskingNet.

### Evaluation

#### Datasets
15 datasets across 7 scenarios: cross-donor (lung transcriptomics), cross-disease (breast transcriptomics), cross-health state (breast proteomics), cross-dataset (mouse islet transcriptomics + mouse cell line proteomics), spatial transcriptomics (STARmap + Slide-seqV2), multi-cell-type (17 cell types, retinal transcriptomics), real bulk tissue (3 PBMC datasets). Plus 3 metabolomics datasets (liver, bone marrow, colorectal cancer) and 3 cell-state datasets (monocyte pseudotime, cell cycle proteomics, drug response metabolomics).

#### Metrics
- **CCC** (Lin's concordance correlation coefficient): primary metric; range [-1, 1]
- **RMSE** (root mean squared error)
- **Pearson's *r*** (correlation coefficient)

#### Key Results

**Visual performance summary (approximate values from rasterized box plots; use source data for exact numbers):**

| Scenario | DECODE | Best Competitor | Runner-up |
|---|---|---|---|
| 1. Cross-donor (lung RNA, n=4) | ~0.97 | Scaden ~0.93 | TAPE ~0.90 |
| 2. Cross-disease (breast RNA, n=6) | ~0.95 | TAPE ~0.90 | CIBERSORTx ~0.85 |
| 3. Cross-health (breast prot., n=6) | ~0.97 | scpDeconv ~0.95 | Scaden ~0.93 |
| 4. Cross-dataset (islet RNA, n=6) | ~0.95 | TAPE ~0.90 | MuSiC ~0.85 |
| 5. Spatial (STARmap, n=12) | ~0.85 | RCTD ~0.82 | cell2location ~0.80 |
| 6. Multi-cell-type (retina, n=17) | ~0.60 | TAPE ~0.50 | Scaden ~0.45 |
| 7. Real bulk (3 PBMC datasets) | Best in all | TAPE competitive | Scaden competitive |
| Metabolomics (bone marrow, n=5) | ~0.80 | MuSiC ~0.30 | Others <0.3 |
| Cell state (pseudotime, n=10) | ~0.80 | TAPE ~0.60 | Scaden ~0.55 |

- DECODE achieves top CCC across nearly all scenarios, outperforming 11 state-of-the-art methods (TAPE (*Nature Communications*, 2022), Scaden (*Science Advances*, 2020), MuSiC, CIBERSORTx, scpDeconv, RCTD, Seurat, SPOTlight, Tangram, ucdselect, cell2location)
- **Metabolomics**: DECODE leads most comparisons; MuSiC is slightly better in liver CCC, and several competitors retain nonzero/moderate performance. High inter-cell-type similarity and few features make these tasks substantially harder.
- **Robustness**: Under 4 perturbation types (unknown cells, random noise ×0.9–1.1, random noise ×0.8/1.2, feature deletion), DECODE maintains highest accuracy. Gap is most dramatic in metabolomics where only DECODE remains usable
- **Cross-omics consistency**: On CITE-seq PBMC data, DECODE gives nearly identical deconvolution results from transcriptomic and proteomic profiles (lowest KL divergence, Spearman ~1.0)
- **Applications**: Applied to multi-omics breast cancer cohorts (238 samples, 4 studies) and mouse liver cohorts (285 samples, 10 studies, 3 omics), revealing biologically interpretable cell-type abundance shifts (e.g., T cell enrichment in nonmetastatic breast cancer, Kupffer cell expansion in NASH)

#### Ablation Study
- Stage 2 (DANN) contributes ~14% CCC improvement (batch-effect removal)
- Stage 3 (full MBdeconv) contributes ~3% CCC improvement
- Denoiser module contributes ~3% CCC improvement (incomplete reference handling)

### Reproducibility

**Rating: 4/5**

| Aspect | Status |
|--------|--------|
| Code availability | GitHub repo with model + data processing code |
| Example notebooks | Jupyter notebooks for lung RNA and bone marrow metabolomics |
| Pre-trained models | Saved models provided for lung RNA and bone marrow |
| Environment | `environment.yml` (Python 3.8, PyTorch 2.0, CUDA 11.8) |
| Data availability | All 15+ datasets publicly available (GEO, MassIVE, Mendeley, etc.) |

**Limitations**:
- No standalone CLI/API — workflow is notebook-driven only; no pip-installable package
- **Transductive training**: Stage 2 requires actual tissue samples during training (adversarial domain adaptation), meaning a new model must be trained for each target dataset
- Hyperparameters (`feat_map_w`, `feat_map_h`, `sample_size`, etc.) are dataset-specific with no automatic tuning guidance
- The "L1 loss" function in code is actually MSE (see doc_code.md Discrepancies)
- No spatial-aware module — spatial transcriptomics handled without exploiting spatial coordinates
- Limited single-cell metabolomics data availability constrains metabolomics evaluation breadth
- Computational cost of artificial noise cell generation scales with feature dimensionality (one-time per task)
- Stage 2 encoder architecture in code omits LayerNorm described in paper (see doc_code.md Discrepancies)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
