---
layout: default
permalink: /paper-atlas/multi-embed-c40df9dd/
title: "Multi-Embed"
nav: false
wide: true
description: "同一块肿瘤组织有两种互补描述：H&E 图像告诉我们细胞形态和组织结构，RNA、甲基化、蛋白或突变谱告诉我们分子状态。Multi-Embed 的目标不是只完成一次“图像预测 RNA”，而是先从配对图像—分子数据中学习一个共享嵌入空间，再把这个空间复用于跨模态预测、空间聚类、预后建模、TLS 识别和轨迹分析。 最关键的设计是区分两种配对尺度： bulk/slide 级：一张切片包含很多 tile，却只配一个患者级分子谱；"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>Multi-Embed</h1>
    <p>Systematically decoding pathological morphologies and molecular profiles with unified multimodal embedding</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03070-5" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Multi-Embed">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Epoch1128/Multi-Embed" target="_blank" rel="noopener noreferrer" aria-label="Open code for Multi-Embed">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Multi-Embed 中文方法解读：把病理形态与分子谱放进同一个坐标系

### 1. 核心问题

同一块肿瘤组织有两种互补描述：H&E 图像告诉我们细胞形态和组织结构，RNA、甲基化、蛋白或突变谱告诉我们分子状态。Multi-Embed 的目标不是只完成一次“图像预测 RNA”，而是先从配对图像—分子数据中学习一个共享嵌入空间，再把这个空间复用于跨模态预测、空间聚类、预后建模、TLS 识别和轨迹分析。

最关键的设计是区分两种配对尺度：

- bulk/slide 级：一张切片包含很多 tile，却只配一个患者级分子谱；
- spot/cell 级：一个图像 tile 与同位置的 spot 或 cell 分子谱一一对应。

因此，Multi-Embed 不是把所有任务强行改成相同输入，而是共享编码器思想、按配对粒度改变对比约束。

### 2. 从原始输入到两个模态的表示

#### 2.1 形态侧

一张 WSI 被切成 $m_i$ 个 tile，预训练病理基础模型 UNI 把每个 tile 转成 $d$ 维特征：

$$
X_i=f_{\mathrm{UNI}}(U_i),\qquad X_i\in\mathbb{R}^{m_i\times d}.
$$

本地仓库的 `extract_features.py` 负责 UNI 特征提取入口，Multi-Embed 本体接收已提取的特征，并不在训练时端到端更新 UNI。论文数据预处理和完整数据下载流程分散在公开数据源与补充说明中，本地快照没有包含研究所用的全部 WSI、组学矩阵和预训练权重。

#### 2.2 分子侧

经过预处理的分子矩阵直接作为输入。bulk 样本被视为只有一个“spot”，因此 $Y_i\in\mathbb{R}^{1\times q}$；空间数据则有 $p_i$ 个 spot/cell，$Y_i\in\mathbb{R}^{p_i\times q}$。这一定义让同一套分子编码器能处理 bulk 和空间数据，但不意味着一个 bulk RNA 向量能为每个 tile 提供真实标签。

### 3. 双编码器、注意力池化和共享投影

论文用两个 MLP 分别编码分子和形态：

$$
g_{y_i}=f_{\mathrm{mol}}(Y_i),\qquad g_{x_i}=f_{\mathrm{mor}}(X_i).
$$

代码 `models/arch.py` 中，`GeneEmbedding` 使用 SNN blocks，`ImageEmbedding` 使用普通回归 blocks。实际训练脚本构造 `hidden_size=[512,512]`，之后由同一个线性层加 ReLU 投到默认 256 维共享空间：

$$
h_x=f_{\mathrm{shared}}(g_x),\qquad h_y=f_{\mathrm{shared}}(g_y).
$$

“共享投影层”意味着两个模态使用相同的最后一层参数，而不只是输出维数相同。`models/arch.py:103-106` 的 `self.share` 被基因和图像两条路径共同调用。

#### 3.1 为什么 slide 需要注意力池化

bulk RNA 只对应整张切片，无法知道哪块 tile 与哪些基因直接对应。图像编码器先为每个 tile 计算 gated attention 分数，再在 tile 维做 softmax：

$$
\alpha_{ik}=\operatorname{softmax}_k\left[W_c\left(\tanh(W_ag_{ik})\odot\sigma(W_bg_{ik})\right)\right],
$$

$$
g_{\mathrm{slide},x_i}=\sum_k\alpha_{ik}g_{x_{i,k}}.
$$

论文公式把第二支也写成 `tanh`，而本地 `Attn_Net_Gated` 明确使用 `Sigmoid`；因此代码更接近常见 gated-attention 形式 `tanh × sigmoid`。`ImageEmbedding.forward` 返回 tile embedding、注意力聚合后的 slide embedding 和注意力权重。

### 4. 自重构负责“别把各自模态的信息丢光”

共享空间若只追求跨模态接近，可能只保留少量共同信号。模型因此为两个模态配置解码器，从共享表示重构输入特征，并用 Frobenius 范数衡量误差。论文写为：

$$
L_{\mathrm{recon}}=
\frac1n\sum_i\frac1{m_i}\|X_i-X_i^r\|_F+
\frac{\lambda}{n}\sum_i\frac1{p_i}\|Y_i-Y_i^r\|_F,
$$

并报告 $\lambda=0.1$。代码的 `recon_loss` 确实是归一化 Frobenius norm，但当前 bulk 脚本实际把分子重构乘 0.05、正负图像重构各乘 1；ST 脚本先把三项相加，再把总重构项乘 0.1。两者都不能简化成论文所写的统一 $\lambda=0.1$ 实现。

### 5. 对比学习如何处理 bulk 的弱配对

#### 5.1 整张切片级 triplet

以患者 $i$ 的分子嵌入为 anchor，同一患者的 slide embedding 是 positive，另一患者切片是 negative。优化目标要求 positive 的余弦相似度高于 negative 至少一个 margin。代码的 `Tripletloss` 默认 margin 为 1，实际计算：

$$
\max(1-s_{+}+s_{-},0).
$$

#### 5.2 tile 集合级 triplet

整张切片聚合只能约束 slide 表示，不能保证每个 tile 落在有意义的位置。作者把一张 slide 的 tile embedding 看作集合 $S_i$，用 smooth-Chamfer similarity 比较这个集合与患者分子向量，再构造第二个 triplet loss。直观上，它同时考虑“各 tile 与分子向量的平均关系”和“最匹配区域的平滑最大关系”，从而在没有 tile 级 RNA 标签时提供弱监督。

`models/loss.py:64-88` 实现 `smooth_chamfer_distance`，`train.py:102-103` 同时调用 set triplet 和 aggregated triplet。这是 bulk 路径最有辨识度的部分。

一个小例子：若同患者切片与 RNA 的相似度为 0.8，负切片为 0.2，margin=1，则 triplet 损失为 $1-0.8+0.2=0.4$；若 positive=0.95、negative=-0.2，截断后为 0，说明排序间隔已经满足。

### 6. ST 路径不是 bulk 路径的完整复制

在 spot/cell 数据里，图像 tile 和分子向量一一配对，因此论文的式 (17) 直接比较同位置 positive 与其他位置 negative。本地 `train_st.py` 确实使用 aggregated `Tripletloss`；但 set-level triplet 调用被注释掉。这是合理的粒度变化，因为每个样本已经是单个 spot/cell，不需要再把一张 WSI 的 tile 当集合。

实际 ST 训练损失为：

$$
L_{\mathrm{code,ST}}=0.1L_{\mathrm{recon}}+L_{\mathrm{MMD}}+L_{\mathrm{triplet}}.
$$

bulk 当前实现为：

$$
L_{\mathrm{code,bulk}}=L_{\mathrm{recon,weighted}}+L_{\mathrm{MMD}}
+\alpha(L_{\mathrm{set-triplet}}+L_{\mathrm{agg-triplet}}),
$$

其中命令行 `alpha` 默认 0.1。两条训练路径均在反向传播后做梯度范数裁剪 `max_norm=1.0`。

### 7. 论文总损失与代码提交之间的硬边界

论文式 (11) 写为：

$$
L=L_{\mathrm{recon}}+\beta L_{\mathrm{SSL}}+L_{\mathrm{div}}+2L_{\mathrm{mmd}}.
$$

其中 divergence regularizer 用于避免同一模态的表示槽位坍缩，MMD 用于避免两个模态早期分离。然而，在本地固定提交 `4c4fa44831b54eb5fa57cb729d22e9b2edcab8ee` 中：

- `models/loss.py` 有 MMD 实现，没有 divergence loss 实现；
- `train.py` 与 `train_st.py` 都只把 `rbf_loss` 加一次；
- 没有 `2 * rbf_loss`，也没有任何 `L_div` 项。

因此，论文公式与当前代码并非逐项一致。不能声称本地脚本完整实现了式 (11)，也不能把预生成结果自动归因于当前脚本中的精确损失。更稳妥的说法是：核心双编码器、重构、triplet 和 MMD 思路有直接实现，而 divergence 与若干权重存在 paper-code gap。

### 8. 学到共享空间以后，任务如何接上

#### 8.1 图像到分子谱

下游 `Emb2RNA` 是两层线性网络：每个 tile embedding 被映射为分子预测，再对 tile 维求平均得到 slide 预测。训练使用 MSE，评估用预测与真实分子特征的 PCC。它不是论文某些文字所暗示的四层网络；当前 `downstream/rna_pred.py:39-54` 只有两层 Linear，中间含 Dropout。

图 1b–j 展示了 RNA、甲基化、蛋白和突变预测。主图可直接读到：TCGA 1,550 个 HVG 上 Multi-Embed 总体平均 PCC 0.37，而 DeepPT 为 0.32、HE2RNA 为 0.29；空间平台、甲基化、蛋白、突变和 ORION-CRC 蛋白任务也分别与对应基线比较。这些结果证明在作者的评估协议中有优势，不表示任何分子状态都能从 H&E 准确恢复。

#### 8.2 分子到图像检索

因为图像和分子表示处于同一个空间，可以按相似度寻找接近某个基因/分子表示的 tile。这是检索，不是从分子向量生成像素级病理图像。

#### 8.3 空间聚类与轨迹

Multi-Embed embedding 可输入 k-means 或后续空间/轨迹工具。图 1k 在 TNBC 数据上比较 ARI；图 2 的胃癌和乳腺癌轨迹还依赖 GraphST、Monocle3 与 SpatialInferCNV。因此“轨迹”不是 Multi-Embed 网络内部端到端输出，而是共享表示支持的下游分析。

#### 8.4 预后模型

`downstream/survival.py` 将图像 embedding 与分子 embedding 送入注意力/SNN 和低秩双线性融合，再做离散时间生存预测。论文补充说明修订后的十折流程在每一折内重新学习 embedding、训练预后模型并确定风险 cutoff，再应用到测试折；这一点是为了避免测试样本参与自监督 embedding 学习造成泄漏。

本地代码提供模型组件和脚本，但数据划分、预训练权重、所有折的运行产物并未随快照完整提供，本轮没有重跑十折或六个外部队列。

### 9. 读图时应抓住什么

- 图 1a 的三段是“特征提取 → 自监督共享空间 → 跨模态推断/整合”，不是一个单一监督预测器。
- 图 1b–j 的指标随任务变化：连续分子谱主要用 PCC，突变用 AUC；不能横向把数值直接比较。
- 图 1k 用 ARI 评价聚类，反映与病理标注的一致性，不等同于生物学机制已经验证。
- 图 2 的预后结果来自下游融合模型；TLS 和轨迹还涉及聚类、人工确认或外部算法。它们展示共享表示的用途，而不是基础预训练目标本身。
- 补充材料明确强调按癌种训练和严格的训练—测试分离。论文 Discussion 同时承认模型受配对数据规模限制，当前并非可直接零样本使用的 foundation model。

### 10. 代码—论文对应表

| 机制 | 本地证据 | 对应程度 |
|---|---|---|
| UNI tile 特征入口 | `extract_features.py` | Partial：需外部权重与原始 WSI |
| 双 MLP 编码器 | `models/arch.py:31-50` | Exact |
| gated attention 与 slide 聚合 | `models/arch.py:6-29,53-70` | Partial：代码为 tanh×sigmoid，论文式 (4) 写成 tanh×tanh |
| 共享 256 维投影 | `models/arch.py:96-122`、训练脚本默认参数 | Exact |
| 重构、triplet、smooth-Chamfer、MMD | `models/loss.py:23-88` | Exact：函数存在 |
| bulk 组合损失 | `train.py:102-108` | Exact for code；与论文式 (11)/(12) 不完全一致 |
| ST 组合损失 | `train_st.py:113-120` | Exact for code；set triplet 被注释 |
| divergence regularizer | 论文式 (18) | Not found in code |
| 图像到连续分子预测 | `downstream/rna_pred.py` | Exact：两层预测头与 MSE |
| 预后融合 | `downstream/survival.py`, `fusion.py` | Partial：模型代码在，完整数据/折结果不在 |

### 11. 复现边界

- 代码快照记录了上游 URL 与提交 `4c4fa44831b54eb5fa57cb729d22e9b2edcab8ee`，可作为版本锚点。
- `requirements.txt` 只列依赖名，没有精确版本锁；当前环境不能据此重建论文环境。
- 工作区没有研究所用的全部数据、UNI 权重、Multi-Embed checkpoints、逐折结果或 source-data 表。
- README 提供的是脚本示例，不是从原始数据到全部主图的一键流水线；许多下游结果还依赖外部软件。
- 主论文、补充说明、审稿往来和代码显示训练—测试分离曾是关键修订点；最终论文描述了折内重训，但本轮未执行实验来独立验证所有结果文件。
- 论文的总体损失、注意力公式和下游预测头描述与当前提交有可定位差异，复现时应以具体脚本为准，并把这些差异记录在报告中。

### 12. 左到右读整条方法链

$$
\text{WSI tiles}\xrightarrow{\mathrm{UNI}}X
\xrightarrow{f_{\mathrm{mor}}}\text{tile/slide embeddings}
$$

$$
\text{molecular profiles }Y\xrightarrow{f_{\mathrm{mol}}}\text{molecular embeddings}
$$

$$
(X,Y)\xrightarrow{\text{shared projection + reconstruction + triplet + MMD}}
\text{Multi-Embed space}
$$

$$
\rightarrow
\begin{cases}
\text{molecular prediction or image retrieval}\cr
\text{spatial clustering / TLS / trajectory}\cr
\text{multimodal survival or treatment response}
\end{cases}
$$

它的贡献是提供跨尺度、跨分子层的统一表示框架；它的主要证据边界则是依赖成对数据、不是即插即用基础模型，且论文公式与公开提交的训练损失并未完全对齐。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Multi-Embed: Summary

**Paper**: Systematically decoding pathological morphologies and molecular profiles with unified multimodal embedding
**Journal**: Nature Methods | **Year**: 2026
**DOI**: 10.1038/s41592-026-03070-5
**Authors**: Peng Zhang, Chaofei Gao, Kui Hua, Zhuoyu Zhang, Shao Li (Tsinghua University / Cambridge)

---

### Motivation & Novelty

#### Biological Problem

Pathological tissue morphology (H&E images) and molecular profiles (RNA-seq, methylation, proteomics, mutations) are complementary views of the same biological system. Jointly analyzing them could reveal how molecular networks govern tissue phenotypes in cancer — but this requires a method that can align these fundamentally different data types across multiple scales (patient-level bulk, spot-level ST, single-cell-level).

#### Limitations of Existing Approaches

| Method | Limitation | Reference |
|--------|-----------|-----------|
| HE2RNA | Supervised, task-specific, limited generalizability | Nat. Commun. 2020 |
| DeepPT | Supervised end-to-end, interpretability dilemma | Nat. Cancer 2024 |
| PORPOISE | Multimodal prognosis only, no cross-modality inference | Cancer Cell 2022 |
| OmiCLIP | Trained on small-scale ST data, limited generalizability | Nat. Methods 2025 |
| MUSE | Self-supervised but limited to ST scale | Nat. Biotechnol. 2022 |
| MISO | Multimodal ST integration, no bulk data support | Nat. Methods 2025 |
| iStar | ST gene prediction only, no multi-omics | Nat. Biotechnol. 2024 |

#### Unique Contributions

1. **Unified framework**: single model handles bulk (TCGA), spot-level (Visium), and single-cell-level (Xenium, Visium HD) data
2. **Multi-layer molecular profiles**: simultaneously infers gene expression, DNA methylation, protein abundance, and somatic mutations from morphology
3. **Bidirectional**: image→molecule inference AND molecule→image retrieval (gene-to-image)
4. **Self-supervised**: no task-specific labels required during pretraining; generalizes across cancer types
5. **Interpretable**: attention weights identify which tiles drive predictions; embedding proximity reveals morphological biomarkers

---

### Method Overview

Multi-Embed is a self-supervised dual-encoder framework with three components:

**1. Feature Extraction**: UNI (ViT-L/16 pathology foundation model, Chen et al. Nat. Med. 2024) extracts 1024-dim features from WSI tiles. Molecular profiles are normalized and HVG-selected externally.

**2. Dual Encoder + Shared Projection**: Separate MLP encoders for image (Reg_Block with ReLU) and omics (SNN_Block with ELU + AlphaDropout) project features to 512-dim latent spaces. A shared linear layer maps both to a 256-dim Multi-Embed space.

**3. Training Objective**: Four loss terms:
- Reconstruction loss (Frobenius norm): preserves intra-modality information
- Aggregated triplet loss: aligns slide-level morphology with bulk molecular profile
- Set-based triplet loss (smooth-Chamfer): aligns tile sets with molecular profiles without tile-level labels
- MMD regularizer: prevents early-stage distribution divergence between modalities

For ST data, spot-level triplet loss replaces the set-based approach. The model is pretrained once per cancer type per technology and reused for all downstream tasks.

**Downstream tasks**: gene expression prediction (Emb2RNA, 2-layer MLP), spatial clustering (k-means in embedding space), survival prediction (attention MIL + SNN + LR bilinear fusion), trajectory inference (Monocle3 on embeddings), TLS identification, drug response prediction.

---

### Evaluation

#### Datasets

| Dataset | Technology | Cancer Types | Samples | Task |
|---------|-----------|-------------|---------|------|
| TCGA | Bulk WSI + RNA-seq/methylation/protein/mutation | 12 | 14,695 WSIs | Pretraining + inference |
| CPTAC | Bulk WSI + RNA-seq | 7 | 4,173 WSIs | External validation |
| HER2ST | 10x Visium | Breast | 8 | ST gene prediction |
| TNBC | 10x Visium | Triple-negative breast | 321 | Clustering, TLS, prognosis |
| Xenium | 10x Xenium | Breast + Lung | 4 | Single-cell gene prediction |
| Visium HD | 10x Visium HD | Colorectal + Lung | 3 | Single-cell gene prediction |
| ORION-CRC | Spatial proteomics | Colorectal | 41 | Protein prediction |
| Gastric cancer ST | 10x Visium | Gastric | 1 | Trajectory inference |
| SurGen | Bulk WSI | Colorectal | 427 | External prognosis |

#### Key Results

**Cross-modality inference (gene expression)**:
- TCGA bulk: Multi-Embed PCC=0.37 vs. HE2RNA PCC=0.29 (P<0.01) and DeepPT PCC=0.32 (P<0.01), across 12 cancer types
- ST (HER2ST, n=785 HVGs): significantly higher PCC than OmiCLIP and iStar
- External validation: outperforms comparison models on all 7 CPTAC cancer types

**Cross-modality inference (multi-layer)**:
- Methylation (n=4096 sites): outperforms DEPLOY (Nat. Med. 2024)
- Protein abundance (n=487): outperforms WSI2RPPA (NPJ Breast Cancer 2024)
- Mutation (TP53 AUC): outperforms CHIEF (Nature 2024) and MUSK (Nature 2025)
- Spatial proteomics (ORION-CRC, n=16 proteins): outperforms OmiCLIP and ROSIE

**Cross-modality integration**:
- Spatial clustering (TNBC, n=94): significantly higher ARI than OmiCLIP, MISO, MUSE, SpaGCN, GraphST, STAGATE, BayesSpace
- Prognosis (TCGA 10-fold CV): higher C-index than PORPOISE across all 12 cancer types; stratifies 3 cancer types (HNSC, LUSC, STAD) that PORPOISE cannot
- External prognosis (6 datasets): outperforms PORPOISE on all 6
- TLS identification (TNBC): F1=0.45 vs. OmiCLIP F1=0.32 (P<0.01) and MISO F1=0.17 (P<0.01)

#### Statistical Methods

- Two-sided t-test for PCC comparisons; paired t-test for ARI/F1/C-index
- 95% CI via bootstrap (n=1000 iterations)
- Log-rank test for survival stratification
- Proportional hazards assumption verified by scaled Schoenfeld residuals

---

### Reproducibility

**Rating: 3/5**

**Justification**: Code is publicly available and covers the core training pipeline. However, several practical barriers exist:

**Strengths**:
- GitHub repo with training scripts for all data types (bulk, ST, Xenium, VisiumHD)
- Clear modular structure; well-separated preprocessing, training, evaluation, downstream
- UNI model publicly available via HuggingFace (requires license agreement)
- All datasets are publicly available (TCGA, CPTAC, HER2ST, TNBC, ORION-CRC, 10x Genomics)

**Weaknesses**:
- No preprocessing scripts for WSI tiling or omics normalization — these are described in Supplementary Note 1 (not OCR'd)
- No configuration files or example commands in README for reproducing specific benchmark results
- Hyperparameters (β, λ, margin, epochs) not systematically documented; must be inferred from code
- Divergence regularizer (Eq. 18) is described in the paper but absent from the pinned code; the reported experiments cannot be attributed to this term from local evidence
- Kronecker product fusion described in paper but code uses LR bilinear fusion — may affect prognosis results
- No pretrained model weights provided; must retrain from scratch on TCGA (14,695 WSIs)
- UNI feature extraction requires GPU and significant compute time for large cohorts

**Environment setup**:
```bash
pip install -r requirements.txt
# Key dependencies: torch, timm (UNI), scanpy, scikit-survival, h5py, pandas
# UNI model: requires HuggingFace license agreement at hf.co/MahmoodLab/UNI
```

**Common pitfalls**:
- `batch_size=1` for bulk training is intentional (variable tile counts per slide)
- ST training uses `hidden_size=[512, 512]` not `[512, 256]` as implied by paper
- Negative sampling for ST is purely random; cluster-aware sampling requires external cluster labels
- Downstream `rna_pred.py` expects pre-extracted embeddings (run `eval_slide.py` first)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
