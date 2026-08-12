---
layout: default
permalink: /paper-atlas/candies-76895d72/
title: "CANDIES"
nav: false
description: "CANDIES 针对同一批空间 spots 上两个模态质量不对称的问题，采用严格的两阶段路线。第一阶段先分别用空间图自编码器压缩两个模态，再把高质量模态作为条件，用 Diffusion Transformer（DiT）在潜空间生成“修复后”的低质量模态；第二阶段对修复后的两模态同时建立空间邻接图和特征相似图，用共享参数 GCN、跨模态对比学习与注意力融合得到统一 spot representation。"
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
      <span>Advanced Science · 2026</span>
    </div>
    <h1>CANDIES</h1>
    <p>Cross-Modal Denoising and Integration of Spatial Multi-Omics Data with CANDIES</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1002/advs.202523754" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CANDIES：先用高质量模态修复低质量模态，再做空间多组学整合

### 一句话理解

CANDIES 针对同一批空间 spots 上两个模态质量不对称的问题，采用严格的两阶段路线。第一阶段先分别用空间图自编码器压缩两个模态，再把高质量模态作为条件，用 Diffusion Transformer（DiT）在潜空间生成“修复后”的低质量模态；第二阶段对修复后的两模态同时建立空间邻接图和特征相似图，用共享参数 GCN、跨模态对比学习与注意力融合得到统一 spot representation。

它的核心主张不是“把两个矩阵拼起来”，而是：在整合之前显式处理质量差异，避免低质量模态的 dropout/noise 直接污染共同空间。

### 1. CANDIES 解决什么问题

空间多组学的两个模态往往同时测在同一个 spot，却具有完全不同的信噪比。例如 spatial CITE-seq 中 RNA 可能受 capture efficiency 与 dropout 影响，而 protein 相对稳定；MISAR-seq 的某些样本中 RNA 的空间结构比 ATAC 清楚。若直接联合编码，优化器可能被噪声更大的模态拖偏，也可能让高质量模态完全支配表示。

记两个模态为

$$
X^1\in\mathbb R^{N\times d_1},\qquad
X^2\in\mathbb R^{N\times d_2},
$$

其中 modality 1 是待修复的低质量模态，modality 2 是条件模态，$N$ 个 spots 共享坐标 $S=\{(x_i,y_i)\}_{i=1}^N$。CANDIES 输出：

- 修复后的低质量模态矩阵 $\hat X^{1*}$；
- 每个 spot 的统一低维 embedding；
- 供 spatial domain、pseudo-Spatiotemporal Map（pSM）、DE/GO 与 GWAS trait-spot mapping 使用的下游表示。

“高/低质量”并非由 assay 名称固定决定。论文用 silhouette、Davies–Bouldin、Moran's I、Calinski–Harabasz 等空间/聚类指标综合判断；真实分析中应先以数据证据决定方向，而不是永远用 RNA 指导 ATAC 或反过来。

### 2. 第一阶段 A：用空间图自编码器建立扩散潜空间

#### 2.1 空间邻接图

根据 spots 坐标建立 KNN 图 $G_s=(V,E_s,A_s,X^m)$，论文默认 spatial $k=3$。加入 self-loop 并做对称归一化：

$$
\tilde A_s=D_s^{-1/2}(A_s+I)D_s^{-1/2}.
$$

每个模态分别通过 GCN encoder：

$$
Z_s^m=E_g^m(X^m,\tilde A_s),
$$

再由 decoder 重构原始 feature space。扩散不是直接在数万基因/峰上运行，而是在预训练 GAE 的 64 维潜空间运行，降低计算量并把空间邻域信息提前编码进去。

#### 2.2 模态特异的 count likelihood

论文不只用普通 MSE。对 RNA 等高 dropout count，decoder 估计 ZINB 的均值 $\mu$、dispersion $\theta$ 和 dropout $\pi$；对 ATAC/protein 等模态使用相应的 NB 或重构项。总的 modality-specific reconstruction loss 把普通 reconstruction 与 distributional negative log likelihood 加权：

$$
L_{rec1}^m=\alpha L_{rec}+\beta L_{dist}^m,
$$

实验默认 $\alpha=2$、$\beta=0.15$。这个设计意在让 embedding 保留适合该 assay 的观测分布，而不是把所有模态都当连续高斯矩阵。

### 3. 第一阶段 B：条件潜扩散如何修复低质量模态

#### 3.1 前向扩散只破坏低质量 embedding

将 $Z_s^1$ 视为干净起点 $Z_0$，逐步加高斯噪声：

$$
Z_t=\sqrt{\bar\alpha_t}Z_0+
\sqrt{1-\bar\alpha_t}\epsilon,qquad
\epsilon\sim\mathcal N(0,I).
$$

论文采用 cosine noise schedule。这里“干净起点”只是 diffusion training 的术语；$Z_s^1$ 本身来自低质量观测，模型希望借助条件模态学习其更可靠的条件分布。

#### 3.2 高质量模态提供两种条件

reverse model 的输入拼接 noisy low-quality embedding 与固定 high-quality embedding：

$$
\tilde Z_t=[Z_t,Z_s^2].
$$

同时 $Z_s^2$ 经过 MLP 得到额外 condition $Z_c^2=MLP(Z_s^2)$。预训练 GAE 产生的 spatial embedding 还作为 DiT positional encoding。这样 DiT 的 multi-head attention 可以在 spots 间同时读取分子与空间关系。

特别重要的是，拼接部分中属于 $Z_s^2$ 的 predicted noise 被 mask，不计入 diffusion loss。条件模态是 guidance，不是要被同时加噪、同时重建的 target。

#### 3.3 学习噪声预测器

reverse transition 写作

$$
p_\theta(Z_{t-1}\mid\tilde Z_t,Z_c^2)
=\mathcal N(\mu_\theta,\Sigma_\theta),
$$

通过预测真实噪声训练：

$$
L_{diff}=\mathbb E_{t,Z_t,\epsilon}
\left\|\epsilon-\epsilon_\theta(\tilde Z_t,Z_c^2)\right\|_2^2.
$$

推断时不是从观测 $Z_s^1$ 做一次 deterministic correction，而从 $Z_T^*\sim\mathcal N(0,I)$ 开始，经 800 个 reverse steps 在 $Z_s^2$ 条件下生成 $Z_0^*$，最后用预训练 modality-1 decoder 得到 $\hat X^{1*}$。

因此输出是条件生成结果。不同随机种子可能产生差异，严格分析应报告重复采样稳定性；论文主要把一次/汇总输出用于后续聚类，没有把 posterior uncertainty 作为核心产物。

### 4. 第二阶段：双图 GCN 同时保留空间邻近与分子相似

第一阶段完成后，modality 1 使用 $\hat X^{1*}$，modality 2 使用原数据。对每个模态建立两张图：

- spatial graph：按物理坐标 KNN，默认 $k_s=3$；
- feature graph：按 expression/profile cosine similarity KNN，默认 $k_f=20$。

物理相邻 spots 往往共享组织环境，但相同 cell type 也可能空间分离。两张图分别捕获 local tissue organization 与 long-range phenotypic similarity。

共享参数 GCN 分别传播：

$$
H_{s,l}^m=\sigma(\tilde A_sH_{s,l-1}^mW_l^m),
$$

$$
H_{f,l}^m=\sigma(\tilde A_f^mH_{f,l-1}^mW_l^m).
$$

“共享参数”意味着同一模态的 spatial 与 feature graph 使用共同映射，使两类 embedding 位于可比较空间；不是说所有模态、所有 GCN 都必然共享一套权重。

### 5. 跨模态对比学习：同 spot 是正样本，其余 spot 是负样本

对于空间分支，modality 1 的 spot $i$ 与 modality 2 的同一 spot $i$ 构成 positive pair；其他 spots 构成 negatives：

$$
L_s=-\sum_i\log
\frac{\exp(sim(h_{s,i}^1,h_{s,i}^2)/\tau)}
{\sum_{j\ne i}\exp(sim(h_{s,i}^1,h_{s,j}^2)/\tau)}.
$$

feature 分支同理得到 $L_f$，总对比损失

$$
L_{cl}=L_s+L_f.
$$

目的不是让两个模态逐 feature 一致，而是让同一 spot 在两个模态的表示彼此可识别，同时保留非匹配 spot 的差异。它依赖两个模态具有准确的 spot correspondence；若坐标配准错误，正样本标签本身就会错误。

论文的分母公式按 OCR/正文写法排除了 $j=i$，这与一些标准 InfoNCE 把 positive 同时放入 denominator 的写法不同。由于没有公开代码，无法核验实际实现是否逐字遵循该排版，重实现时必须明确选择并记录。

### 6. 注意力融合与表达重构

CANDIES 不固定按 50/50 混合 spatial 与 feature embeddings，而为每个 spot 学习注意力权重：

$$
h_i^m=a_{s,i}^mh_{s,i}^m+a_{f,i}^mh_{f,i}^m,
\qquad a_{s,i}^m+a_{f,i}^m=1.
$$

再跨模态汇总得到最终 fused representation。注意力允许组织结构强的区域偏向 spatial graph，空间上分散但 molecular profile 相似的细胞偏向 feature graph。

integration decoder 同时从 spatial 与 feature representations 重构模态数据，避免 contrastive alignment 把所有 spots 过度压在一起。总损失为

$$
L_{int}=\lambda_{cl}L_{cl}+\lambda_{rec}L_{rec2},
$$

论文默认 $\lambda_{cl}=\lambda_{rec}=0.5$。补充敏感性分析显示过度偏向任一项都会略降性能。

### 7. 三段训练顺序不能混在一起

论文 Methods 给出的训练合同是：

1. **GAE pretraining**：400 epochs，latent dimension 64；
2. **conditional diffusion**：AdamW，learning rate 0.001，最多 1,000 epochs，800 diffusion steps，默认按 spot 数分 3 folds；
3. **integration**：Adam，learning rate 0.001，最多 300 epochs。

GAE decoder 必须先学会将 latent 映回原空间，之后才能解码 diffusion 生成的 $Z_0^*$。integration 则必须使用修复后的 modality 1。把三者联合随机初始化或跳过 decoder pretraining 都不再是论文描述的算法。

800 reverse steps 解释了 CANDIES 较高运行时间。论文把 DDIM 等加速采样列为未来方向；当前方法合同没有证明减少到很少步数仍保留相同结果。

### 8. lower-quality modality 如何确定

论文综合四个指标评估单模态 embedding：

- silhouette index：cluster cohesion/separation；
- Davies–Bouldin index：越低通常越好；
- Moran's I：空间自相关；
- Calinski–Harabasz index：类间/类内变异比。

选择低质量模态后，方向在整个 denoising stage 固定。这里有两个限制：第一，指标依赖 clustering/neighbor choices；第二，一个模态可能只在部分组织区域更差，整体单向 guidance 未显式处理局部质量反转。三模态与动态选择也被论文列为未来扩展。

### 9. 逐图阅读主证据链

#### 图 1：完整算法合同

图 1a 是 GAE→conditional DiT→decoder 的去噪链，明确显示 `[Z_t,Z_s^2]` 拼接、MLP condition 与 conditional branch 的 masked loss；图 1b 是 spatial/feature dual GCN、cross-modal contrastive alignment、attention fusion 与 reconstruction；图 1c 列出 denoising、domain identification、pSM 与 trait mapping 四类输出。

#### 图 2：受控模拟中的去噪价值

模拟数据人为设定 RNA 比 protein 更噪，并逐步改变 Gaussian noise 与 ZINB dropout。CANDIES 在示例条件下仅用 refined RNA 做 domain identification 得到 ARI 0.92；完整 integration 得到 ARI 0.9470。`CANDIES (w/o denoise)` 消融低于完整方法，且噪声越高差距越大。这直接支持“先修复再整合”，但模拟生成机制和模型的 ZINB/NB 假设相近，仍需真实数据证据。

#### 图 3：MISAR-seq mouse brain

E15.5 样本中 RNA 作为较高质量条件修复 ATAC。完整 CANDIES integration ARI 0.5597，去掉 denoising 后为 0.5017，并更清楚分开 DPallm、DPallv、midbrain、thalamus 等区域。E18.5 补充实验给出相似趋势。

#### 图 4：human skin spatial CITE-seq

protein 指导低质量 RNA 后，CANDIES 揭示 pilosebaceous unit 内新的 immune-responsive niche，并以 marker、免疫相关基因与 GO enrichment 支持。图 4e 的 pSM 从共同 embedding 构造 pseudo progression；它反映 representation geometry，不是直接测得的真实时间或谱系。

#### 图 5：mouse embryo 多平台验证

在 spatial H3K27ac–H3K27me3 与 ATAC–RNA 数据中，CANDIES 区分主要组织区域并保留少见 domains；jaw region 的 DEG/GO 与发育基因提供外部一致性。跨数据平台结果支持方法适用范围，但各数据集的“高质量条件模态”及预处理并不相同。

#### 图 6：空间 trait mapping

用 CANDIES embedding 为每个 focal spot 建 homogeneous microdomain，按其中基因表达 rank 计算 gene specificity score，再用 S-LDSC 检验 GWAS heritability enrichment。mouse brain、embryo 与 human lymph node 的 trait-region 对应提供生物学可解释结果。这个模块依赖 gsMap/GWAS/S-LDSC，并非 CANDIES 训练 loss 的一部分；trait association 也不是个体层因果定位。

### 10. 支持材料与消融告诉我们什么

补充敏感性分析覆盖：GAE reconstruction 权重、spatial/feature neighbor 数、diffusion steps、contrastive/reconstruction trade-off。800 steps 和 0.5/0.5 loss 权重是实验选择，不是理论唯一解。补充 ablation 比较 no-denoise，证明性能提升来自两阶段组合，而非仅用更大 integration network。

论文还报告 CANDIES 相比 baseline 运行时间更长、GPU memory 大体可比。由于未公开实现，不能核验计时是否包含相同预处理、GAE pretraining 和全部 diffusion inference，也不能由表格推断真实新数据上的 wall-clock。

### 11. 代码与复现边界

截至本次核验，本工作区没有 CANDIES 源码、supplemental code archive 或可验证 Git commit；论文正文和当前 Wiley/bioRxiv 页面也没有提供官方 CANDIES GitHub。论文末尾只有 Data Availability 声明，且写“no new data were created or analyzed”，这与正文实际重分析多个公开数据集的叙述并不充分协调。

因此本工作区必须保持 `paper-only`：

- **可验证**：模型两阶段结构、公式、默认训练参数、主图/补充结果与公开数据集引用；
- **不可验证**：DiT layer/head/hidden dimension、具体 tensor shape/masking 代码、sampling variance、contrastive denominator、attention implementation、seed/device、package versions、data loaders 与完整 preprocessing scripts；
- **不能声称**：存在一个本地实现、某公式与某函数 Exact 匹配、或能一键复现全部图。

`doc_code.md` 应被理解为 paper-to-implementation specification：它列出若实现论文需要具备的模块，而不是对不存在源码的审计。

### 12. 若要重实现，最小可验证顺序

1. 固定两个模态的 spot 对应、坐标、count preprocessing 与 quality-direction rule。
2. 分别训练 GAE，检查 reconstruction 和 64D embedding 的空间/cluster structure。
3. 在 toy data 上验证 forward diffusion 的边际分布与 cosine schedule。
4. 确认 condition branch 不进入 noise target，比较有/无 condition 的 denoising MSE。
5. 从纯噪声做完整 800-step reverse sampling，并通过预训练 decoder 检查 count distribution。
6. 用修复后数据构建 $k_s=3$ spatial graph 和 $k_f=20$ feature graph。
7. 单独验证 same-spot contrastive positives、all-other negatives 与 temperature。
8. 检查 attention weights 是否归一化，重构损失是否防止 representation collapse。
9. 用论文 simulated settings 重现 noise/dropout 曲线与 no-denoise ablation，再进入真实数据。
10. 报告多个 seeds、sampling variance、runtime 与 preprocessing，不只报告最佳 ARI。

### 13. 最容易误读的地方

- **conditional denoising 不等于把高质量模态复制到低质量模态。** target 仍是低质量模态在 latent space 的条件分布。
- **denoised profile 不是真实无噪声 ground truth。** 它是模型在跨模态与空间假设下的生成估计。
- **空间平滑不总是好事。** 过强 spatial graph 会抹掉 rare/discontinuous domains，所以还需 feature graph 与重构。
- **attention weight 不是因果重要性。** 它只是当前模型组合两张图的门控系数。
- **pSM 不是实验时间。** 它是 joint representation 上推断的 pseudo-order。
- **GWAS trait-spot mapping 是下游统计关联。** 不能解释为某 spot 导致复杂性状。
- **目前没有直接代码证据。** 所有实现细节必须标成 Not found，而不是从公式猜测 Exact。

### 本地证据入口

- 论文 Markdown：`paper source/paper/auto/paper.md`
- 论文 PDF：`paper.pdf`
- 方法与公式：`doc_method.md`
- 逐图证据：`figure_analysis.md`
- paper-only 实现规格：`doc_code.md`
- 证据账本：`claude_notes.md`, `scratch/evidence_index.json`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CANDIES Summary

**Paper**: Cross-Modal Denoising and Integration of Spatial Multi-Omics Data with CANDIES
**DOI**: 10.1002/advs.202523754
**Journal**: Advanced Science
**Year**: 2026
**Authors**: Ye Liu, Wanpeng Zou, Yuekai Li, Jiayi Wang, Mingxuan Cai, Hongmin Cai
**Institutions**: South China University of Technology; City University of Hong Kong

---

### Motivation & Novelty

#### Biological Problem

Spatial multi-omics technologies simultaneously measure multiple molecular profiles (RNA, ATAC, histone modifications, proteins) at spatially resolved tissue locations. This enables comprehensive characterization of cellular states within their native tissue context — critical for understanding tissue organization, development, and disease.

However, different molecular assays have fundamentally different noise profiles:
- **RNA**: suffers from dropout (false zeros from low capture efficiency) and technical noise
- **Spatial CITE-seq protein**: competition between antibody-derived tags (ADTs) and mRNAs during reverse transcription reduces RNA detection efficiency
- **ATAC**: inherently sparse and high-dimensional chromatin accessibility data

When modalities have different noise levels, naive integration is dominated by the noisier modality, obscuring biologically meaningful signals and producing unreliable downstream analyses.

#### Limitations of Existing Methods

| Method | Limitation |
|--------|-----------|
| MultiVI (Nature Methods 2023) | Single-cell only; no spatial context |
| totalVI (Nature Methods 2021) | Single-cell only; RNA-ADT specific |
| SpatialGlue (Nature Methods 2024) | Spatial-aware but sensitive to noise; no denoising |
| PRESENT (bioRxiv 2024) | Cross-modal representation but no quality-aware denoising |
| COSMOS (Nature Communications 2025) | Cooperative integration but no explicit noise handling |
| PRAGA (arXiv 2024) | Prototype-aware aggregation but no denoising |
| SEDR (Genome Medicine 2024) | Single-modality denoising only |

None of these methods explicitly address the **quality imbalance** between modalities — the scenario where one modality is substantially noisier than another.

#### CANDIES Contributions

1. **Quality-aware denoising**: First spatial multi-omics method to use the higher-quality modality to denoise the lower-quality one via a conditional diffusion model
2. **DiT-based latent diffusion**: Applies Diffusion Transformer (DiT) in the latent space of a pre-trained GAE, enabling efficient denoising of high-dimensional omics data
3. **Automatic quality determination**: Unsupervised metrics (SI, DBI, Moran's I, CHI) automatically identify which modality to denoise — no user specification required
4. **Dual-graph integration**: Combines spatial proximity and molecular similarity graphs with per-cell attention for flexible, context-aware fusion
5. **GWAS integration**: Demonstrates that CANDIES embeddings improve spatially resolved mapping of complex human traits via gsMap + S-LDSC

---

### Method Overview

CANDIES is a two-stage framework:

**Stage 1 — Denoising**: A pre-trained dual Graph Auto-Encoder (GAE) compresses each modality into 64-dimensional latent embeddings. A DiT-based conditional diffusion model then refines the lower-quality modality embeddings, guided by the higher-quality modality as a conditioning signal. The denoised embeddings are decoded back to expression space via the pre-trained decoder.

**Stage 2 — Integration**: A parameter-sharing dual GCN processes both spatial proximity and feature similarity graphs for each modality. Cross-modal contrastive learning (InfoNCE) aligns same-spot embeddings across modalities. A per-cell attention mechanism dynamically weights spatial vs feature information to produce the final fused representation.

**Key technical components**:
- Modality-specific decoders: ZINB for RNA (models zero-inflation), NB for ATAC
- Cosine noise schedule for smooth diffusion
- Spatial embeddings from GAE as positional encoding in DiT
- All-negative contrastive learning (no manual positive/negative selection)
- η=1e-6 numerical stability in attention

**Downstream analyses**: Leiden clustering for spatial domain identification, `scanpy.tl.dpt` for pseudo-spatiotemporal maps, gsMap + S-LDSC for GWAS trait-spot mapping.

See `doc_method.md` for full mathematical derivations and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets

| Dataset | Technology | Tissue | Spots | Modalities |
|---------|-----------|--------|-------|-----------|
| Simulated | Synthetic (ZINB/NB) | — | 1,296 | RNA + protein |
| MISAR-seq E15.5 | MISAR-seq | Mouse brain | 1,949 | RNA + ATAC |
| MISAR-seq E18.5 | MISAR-seq | Mouse brain | 2,129 | RNA + ATAC |
| Spatial CITE-seq | Spatial CITE-seq | Human skin (COVID-19 vaccine site) | 1,691 | RNA + 283 proteins |
| Spatial-Mux-seq E13 | Spatial-Mux-seq | Mouse embryo | 2,102 | H3K27ac + H3K27me3 |
| Spatial ATAC-RNA-seq E13 | Spatial ATAC-RNA-seq | Mouse embryo | 2,186 | RNA + ATAC |
| 10x Visium lymph node | 10x Visium | Human lymph node | 3,484 | RNA + 31 proteins |

#### Metrics

**Supervised** (when ground truth available): ARI, NMI, AMI, V-measure, Homogeneity, Completeness, FMI, Mutual Information
**Unsupervised** (no ground truth): Silhouette Index, DBI, Moran's I, CHI

#### Key Results

**Denoising performance (simulated, dropout=0.2, σ=3.0)**:
- CANDIES ARI = 0.92 (denoised RNA only)
- Runner-up SEDR (Genome Medicine 2024): 11% lower ARI
- CANDIES maintains performance under high noise; SEDR degrades dramatically

**Multi-omics integration (simulated)**:
- CANDIES ARI = 0.9470 (best among 6 methods)
- CANDIES (w/o denoise) substantially lower — denoising is critical

**E15.5 mouse brain (MISAR-seq)**:
- CANDIES ARI = 0.5597 (best)
- CANDIES (w/o denoise) ARI = 0.5017 (similar to PRESENT)
- Correctly identifies midbrain, DPallm, DPallv, thalamus, subpallium_2

**E13 mouse embryo (ATAC-RNA-seq)**:
- CANDIES ARI = 0.4173 (8.44% above runner-up)
- Identifies hindbrain, spine, ventricle, eye tissues

**Human skin (spatial CITE-seq)**:
- Discovers cluster 6 = immune-responsive niche in pilosebaceous unit (not detectable in raw RNA)
- Mac-2 (Galectin-3) p = 5.68×10⁻⁴⁹, CD107a p = 1.40×10⁻³⁵ in cluster 6
- LAMP1 (CD107a gene) p = 9.82×10⁻³³, TRIM16 p = 4.33×10⁻⁶⁴ after denoising

**Mouse embryo (Spatial-Mux-seq H3K27ac/me3)**:
- Identifies jaw region (cluster 8) only detectable with multi-modal integration
- Hoxa3/Hoxaas3 enriched for H3K27me3; Hand2/Tbx2 enriched for H3K27ac in jaw

**GWAS mapping (32 complex traits)**:
- Psychiatric traits (BIP, IQ, MDD, SCZ) enriched in dorsal pallium, thalamus, hindbrain of mouse brain
- Height mapped to cartilage-forming regions in mouse embryo
- Hematological traits enriched in cortex, follicle, medulla, capsule of human lymph node
- CANDIES embeddings yield substantially higher significance than RNA-only embeddings

#### Computational Performance

CANDIES has higher running time than baselines (due to 800 diffusion steps) but comparable GPU memory. The paper notes this as a limitation and plans DDIM acceleration for future work.

---

### Reproducibility

**Rating: 2/5**

**Justification**: The paper was accepted March 30, 2026 and no code repository or data availability statement is present. The methods section is detailed enough to re-implement the method, but without code, exact reproduction is not possible.

**Strengths**:
- Detailed methods section with all hyperparameters specified (α=2, β=0.15, T=800, k_spatial=3, k_feature=20, λ=0.5)
- All datasets are publicly available (MISAR-seq, spatial CITE-seq, spatial-Mux-seq, spatial ATAC-RNA-seq, 10x Visium)
- Baseline methods are all publicly available with GitHub links provided
- Evaluation metrics are standard and well-defined

**Weaknesses**:
- No code repository at time of analysis
- No data availability statement (unusual — likely an oversight)
- DiT architecture details (number of layers, heads, hidden dim) not specified
- Exact contrastive temperature τ not reported
- Inference procedure (DDPM vs DDIM) not specified

**Practical notes**:
- Dependencies: PyTorch, scanpy v1.10.3, scvi-tools v1.3.0, gseapy v1.1.6, esda v2.7.0, scikit-learn v1.5.2
- ATAC preprocessing requires LSI (TF-IDF + SVD) — use `snapatac2` or `muon` for this
- gsMap tool available at: https://github.com/LeonSong1995/gsMap (Song et al., Nature 2025)
- The two-stage training (GAE → diffusion → integration) requires careful sequential execution

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
