---
layout: default
permalink: /paper-atlas/indiseek-f1e34ccf/
title: "IndiSeek"
nav: false
description: "IndiSeek 用对方模态的 shared 表示来清除本模态 specific 表示中的公共信息，再用本模态 shared+specific 重建防止信息被删光；它改善了独立性—完整性权衡，但没有公开代码时，优化细节和统计可识别性必须保持为复现边界。"
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
      <span>arXiv preprint · 2025</span>
    </div>
    <h1>IndiSeek</h1>
    <p>IndiSeek learns information-guided disentangled representations</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2509.21584" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## IndiSeek：同时寻找多模态共享信息与互补特异信息

### 核心问题

给定成对观测的两个模态 $X_1,X_2$，IndiSeek 希望把每个模态拆成

$$
X_1\mapsto(C_1,Z_1),\qquad X_2\mapsto(C_2,Z_2),
$$

其中 $C_i$ 是跨模态共享表示，$Z_i$ 是该模态独有的互补表示。理想状态同时满足：

1. $C_1,C_2$ 保留两模态共有信息；
2. $Z_1$ 与另一个模态的共享表示 $C_2$ 独立，$Z_2$ 与 $C_1$ 独立；
3. $(C_i,Z_i)$ 合起来仍足以重建 $X_i$，不能为了独立而丢掉有用信息。

它是通用多模态表示方法，不是专门的单细胞模型。论文用 CITE-seq RNA/ADT 作为主要生物应用，同时在视频、语言和临床 MultiBench 数据上评估。

### 为什么“特异表示”容易学错

如果只要求 $Z_i$ 与同模态共享表示 $C_i$ 独立，会遇到 shared encoder 冗余：$C_i$ 可能除了真正共有信息，还夹带本模态私有细节。此时强迫 $Z_i\perp C_i$ 会错误删除本应保留的私有信息。

IndiSeek 的关键切换是跨模态约束：

$$
I(Z_1;C_2)\approx0,qquad I(Z_2;C_1)\approx0.
$$

直觉上，$C_2$ 中额外冗余来自模态 2，不应包含模态 1 的私有信号；因此用“对方的 shared”定义需要排除的公共信息，更不容易误伤自己的特异信息。

这依赖一个重要假设：两个模态各自的私有因素彼此独立或至少不会大量泄漏进对方 shared。若真实数据存在私有因素间相关、技术批次共同作用或 shared encoder 严重失效，cross-modal independence 也不能保证理想分解。

### 第一阶段：CLIP 学共享表示

两个 encoder $f_1,f_2$ 产生

$$
C_1=f_1(X_1),\qquad C_2=f_2(X_2).
$$

InfoNCE 把同一样本的跨模态 pair 拉近，把 batch 中错配 pair 推远，从而近似最大化共享互信息。Figure 3 中红色虚线连接 $C_1,C_2$。

论文把后续阶段写成“given learned shared features”，通常应理解为共享特征先训练好再固定；但没有公开代码，正文也没有完全排除第二阶段联合微调 $f_i$。这会影响复现：若继续更新 shared encoder，$C_i$ 可能为适应 independence/reconstruction 目标而漂移。

CLIP 只能鼓励共有信息，不自动保证 minimal sufficiency；有限 batch、encoder 容量和 temperature 都可能让 $C_i$ 带冗余或漏信息。IndiSeek 第二阶段正是为这种不完美 shared 表示设计。

### 第二阶段之一：NCE-CLUB 压低跨模态依赖

特异 encoder $h_i$ 产生 $Z_i=h_i(X_i)$。以模态 1 为例，NCE-CLUB 估计互信息上界：

$$
L_{\mathrm{NCE-CLUB}}(Z_1;C_2)
=\mathbb E_{(Z_1,C_2)}\log q_\theta(Z_1\mid C_2)
-\mathbb E_{Z_1,\widetilde C_2}\log q_\theta(Z_1\mid\widetilde C_2).
$$

第一项用真实配对，第二项把 $C_2$ 打乱形成独立边际。若 $C_2$ 能很好预测 $Z_1$，两项差异大；最小化它会削弱 $Z_1$ 对跨模态 shared 的依赖。$q_\theta$ 是高斯条件密度辅助网络，需要在表示网络变化时持续拟合。

一个小例子：真实配对平均 log-likelihood 为 $-1.0$，打乱配对为 $-3.0$，CLUB 差为 2.0，说明依赖较强；训练若把两者变成 $-2.0$ 与 $-2.2$，上界降为 0.2，表示更难从 $C_2$ 预测 $Z_1$。

这个值只是依赖上界的神经估计。若 Gaussian $q_\theta$ 拟合不足或 inner optimization 不充分，上界可能松，低 loss 不等于统计独立已被严格证明。

### 第二阶段之二：重建防止信息被删光

只最小化依赖有一个平凡解：让 $Z_i$ 变成常数。IndiSeek 用 decoder

$$
\widetilde X_i=g_i(Z_i,C_i)
$$

和 MSE 要求 shared+specific 一起重建原模态。实用目标为

$$
L_{\mathrm{IndiSeek}}
=L_{\mathrm{NCE-CLUB}}(Z_i;C_{3-i})
+\frac{\lambda}{2\mathbb E\|X_i\|^2}
\mathbb E\|g_i(Z_i,C_i)-X_i\|^2.
$$

分母 $2\mathbb E\|X_i\|^2$ 让重建项近似 scale-free，减少不同模态量纲导致的权重失衡。$\lambda$ 控制独立与完整的权衡：小 $\lambda$ 更强调去依赖，可能丢特异信息；大 $\lambda$ 更强调重建，可能把共享冗余留在 $Z_i$。

论文用条件熵与重建误差的上界来说明 MSE 是 conditional mutual information 的代理，并称其来自 Fano 不等式。对连续变量而言，文中给出的 Gaussian 误差—熵上界需要分布与矩条件；不能把 MSE 小直接等同于完整捕获了全部互信息。

### 训练时左到右发生什么

```text
paired X1, X2
  → Stage 1: f1/f2 + InfoNCE
  → shared C1, C2
  → Stage 2: h1/h2
  → specific Z1, Z2
  → CLUB: Z1 vs C2，Z2 vs C1
  → decoder: (Z1,C1)→X1，(Z2,C2)→X2
  → independence upper bound + normalized reconstruction MSE
  → downstream uses C1,Z1,C2,Z2
```

Figure 3 的蓝色交叉虚线就是 $Z_1\leftrightarrow C_2$、$Z_2\leftrightarrow C_1$ 的 independence 约束；灰色回路是同模态重建。两模态的第二阶段目标可分开并行优化。

### CITE-seq 实例

论文使用 30,672 个骨髓细胞，15,000 训练、15,672 测试。RNA 经过标准化并取 200 个 PCA 成分，ADT 是约 25 个表面蛋白（正文/预处理描述中有效维度为 24）。MLP 学得 $C_{RNA},C_{ADT},Z_{RNA},Z_{ADT}$。

对每个测试细胞，分别在 $Z_{RNA}$ 与 $Z_{ADT}$ 中找 10 个最近邻，计算同 cell-type 邻居比例 $\beta_{RNA},\beta_{ADT}$，再定义

$$
\theta(c)=\log\frac{\beta_{RNA}(c)}{\beta_{ADT}(c)}.
$$

$\theta>0$ 表示 RNA-specific 空间更能保留该细胞类型的标签邻域，$\theta<0$ 表示 ADT-specific 更强。Figure 4 中 progenitor 多为正，T-cell 亚型多为负，与 WNN 中 RNA weights 排名一致。

这里的“importance”是相对于已知 cell-type annotation 的 10-NN 纯度，不是单细胞的因果模态贡献。若 $\beta=0$，log ratio 还需要实现中的平滑/数值处理，但论文没有公开代码说明。

Figure 4 散点图显示单次 $\lambda=10$ 的 Spearman $\rho=0.922$，正文写 0.910；二者存在来源差异，应分别保留，不能合并成一个精确复现实测值。Figure 5 的十随机种子均值显示 IndiSeek 在 $\lambda=10$–100 附近约 0.90，优于比较方法。

### 模拟与 MultiBench 证据

- 两个合成 setting 检查 learned $Z$ 是否依赖真正私有坐标，而非 shared 或其非线性冗余。IndiSeek 总体更集中于目标坐标，但某些图像 hash/面板对应在 OCR 资产中存在歧义，具体单柱高度不应过度解读。
- MOSI、MOSEI、UR-FUNNY、MUStARD 和 MIMIC 使用同样预提取特征与架构，最终把 $(C_1,Z_1,C_2,Z_2)$ 拼接做 linear probing。Table 1/附录中 IndiSeek 在报告任务上总体最好，但部分数据集增益很小。
- 每个 $\lambda$ 用 10 seeds，并从网格中报告最佳结果。这体现参数敏感性，也意味着“best over $\lambda$”需要明确验证集选择过程，不能视作无需调参的性能。

### 与相近方法的真正差别

| 方法 | independence 对象 | completeness 代理 | 主要风险 |
|---|---|---|---|
| IndiSeek | $Z_i$ vs 对方 $C_{3-i}$ | normalized MSE reconstruction | CLUB 密度拟合与 cross-modal independence 假设 |
| FactorizedCL | $Z_i$ vs 同方 $C_i$ | InfoNCE | shared 冗余可能误删特异信息 |
| InfoDisen | 同模态正交/vMF | InfoNCE | 线性正交难处理非线性依赖 |

IndiSeek 的创新不是单独使用 CLIP、CLUB 或 autoencoder，而是“跨模态 CLUB + 同模态 shared/specific 重建”的组合。

### 代码、版本与复现边界

1. 当前是 arXiv `2509.21584`（2025）paper-only 工作区。未找到公开 code repo、依赖文件、训练脚本或 checkpoint，因此无法验证 shared encoder 是否冻结、CLUB Gaussian 参数化、shuffle、epsilon、early stopping 和 seed 细节。
2. 工作区 `paper.pdf` 是有效原文 PDF；主 OCR Markdown 同时包含正文与附录，没有独立 `SUPP_MD`。图像目录含大量公式裁片和主/附录图，不应把文件数当作 figure 数。
3. 文中给出 CITE-seq 的 5-layer MLP、MultiBench 的 2-head/2-layer Transformer、2000 epochs、batch 128、学习率 $10^{-4}$ 等设置，但没有实现就不能确认所有实验一致使用。
4. Stage 1→Stage 2 的冻结边界、CLUB 每轮 5 个 inner epochs 的优化顺序，以及零邻居比例的 log-ratio 处理仍不可验证。
5. 表示“shared/specific”是由目标函数定义的统计分解，不保证可识别唯一；不同随机种子、encoder 容量或 $\lambda$ 可产生等效但坐标不同的表示。
6. `ready_to_publish=true` 表示 PaperCode 文档合同完成，不表示本地复现或理论结论被独立证明。

### 一句话记忆

IndiSeek 用对方模态的 shared 表示来清除本模态 specific 表示中的公共信息，再用本模态 shared+specific 重建防止信息被删光；它改善了独立性—完整性权衡，但没有公开代码时，优化细节和统计可识别性必须保持为复现边界。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## IndiSeek: Information-Guided Disentangled Representation Learning

> **Paper**: "IndiSeek learns information-guided disentangled representations"
> **Authors**: Yu Gui, Cong Ma, Zongming Ma
> **arXiv**: 2509.21584 | **Date**: September / December 2025
> **Affiliation**: UPenn, U Chicago, Yale
> **Status**: Preprint (no journal yet, no code released)

---

### Motivation & Novelty

#### The Biological Problem

Single-cell multi-omics technologies like **CITE-seq** (Stoeckius et al., 2017, *Nature Methods*, 14:865) simultaneously measure multiple molecular readouts per cell — RNA (transcriptome) and ADT (surface proteins) in the CITE-seq case. These modalities share information (both reflect the cell's identity) but also carry *complementary* signals. T cell subpopulations are better resolved by surface protein markers (ADT-specific), while progenitor cell hierarchies emerge from transcriptional programs (RNA-specific). Existing integration methods (e.g., Seurat WNN — Hao et al., 2021, *Cell*, 184:3573) combine both modalities empirically but do not provide a principled way to disentangle the unique contribution of each.

#### Why Existing Methods Fall Short

Disentangled multi-modal representation learning requires simultaneously:
1. **Independence**: modality-specific features ($Z_i$) independent of shared features ($C_{3-i}$)
2. **Completeness**: the pair $(C_i, Z_i)$ retains all information from modality $i$

These goals conflict, and both require estimating mutual information (MI) — an intractable quantity. Two SOTA methods handle this poorly:

- **FactorizedCL** (Liang et al., 2023b, *NeurIPS 2023*, 36:32971): Uses NCE-CLUB for independence (correct approach) but intra-modal independence ($Z_i \perp C_i$), not cross-modal. Uses InfoNCE for completeness, which introduces temperature sensitivity $\tau$ and can be an unstable surrogate. Most critically, without cross-modal disentanglement, redundant shared features cause information loss.

- **InfoDisen** (Wang et al., 2024a, arXiv:2410.23996): Uses an orthogonal loss based on von Mises–Fisher (vMF) assumptions — fundamentally linear, fails to capture nonlinear dependencies. Also uses InfoNCE for completeness.

Both methods fail in controlled simulations: given shared features from an oracle, neither correctly identifies that the ideal modality-specific representation depends only on the "leftover" coordinates independent of the shared component.

#### Unique Contributions

1. **Cross-modal CLUB disentanglement**: Enforce $Z_i \perp C_{3-i}$ rather than $Z_i \perp C_i$. This is theoretically motivated: even when the learned $C_1$ is redundant (absorbing some $X_1$-specific variation), the redundant part is independent of $X_2$, so $I(C^*; Z_1) = I(C_2; Z_1)$. Cross-modal CLUB thus correctly recovers the true disentanglement without losing modality-specific information.

2. **Reconstruction as MI surrogate**: Replace InfoNCE with a MSE reconstruction loss as a surrogate for $I(Z_i; X_i \mid C_i)$. By Fano's inequality, MSE upper-bounds the conditional entropy $H(X_i \mid Z_i, C_i)$, making it a principled surrogate. This eliminates temperature parameter $\tau$ and is more robust across datasets.

3. **Scale-free normalization**: The reconstruction term is normalized by $2\mathbb{E}\|X_i\|^2$, making it scale-invariant so that the same $\lambda$ range ($10^{-1}$–$10^1$) works across modalities and datasets.

---

### Method Overview

IndiSeek is a **two-stage representation learning framework** for paired multi-modal data:

#### Stage 1: Shared Feature Extraction (CLIP)
Contrastive learning (InfoNCE) trains encoders $f_1, f_2$ to produce shared representations $C_1 = f_1(X_1), C_2 = f_2(X_2)$ that capture all cross-modal mutual information while being minimally sufficient.

#### Stage 2: Modality-Specific Feature Extraction (IndiSeek)
With fixed $C_1, C_2$, learn encoders $h_i : X_i \to Z_i$ by minimizing:

$$
\mathcal{L}_{\text{IndiSeek}}(Z_i; \lambda) = \underbrace{\mathcal{L}_{\text{NCE-CLUB}}(Z_i; C_{3-i})}_{\text{independence}} + \underbrace{\frac{\lambda}{2\mathbb{E}\|X_i\|^2} \min_{g_i} \mathbb{E}\|g_i(Z_i, C_i) - X_i\|^2}_{\text{completeness}}
$$

The CLUB term is computed using a learned Gaussian auxiliary network $q_\theta(z \mid c)$ updated with a 5-step inner optimization at each outer epoch.

**Key architectural choices**: All encoders/decoders are 5-layer ReLU MLPs (width 50, output dim 50) for CITE-seq; Transformer (2 heads, 2 layers, width 128) for MultiBench video datasets. Training: batch 128, Adam with LR $10^{-4}$, 2000 epochs.

For more details, see `doc_method.md`.

---

### Evaluation

#### Dataset 1: Bone Marrow CITE-seq (Stuart et al., 2019, *Cell*, 177:1888)
- 30,672 cells, RNA + 25 ADT proteins
- Train: 15,000 cells; Test: 15,672 cells
- Preprocessing: ADT centering → 24 dims; RNA PCA → 200 components

**Primary metric**: Spearman rank correlation $\rho$ between IndiSeek's implied RNA vs ADT modality importance ranking across 27 cell types and the WNN-based benchmark ranking from Seurat (Hao et al., 2021).

| Method | Spearman $\rho$ (10 seeds) |
|--------|---------------------------|
| **IndiSeek** | **0.910** (text) / 0.922 (figure) |
| FactorizedCL | ~0.87–0.89 at best λ (Fig 5) |
| InfoDisen | ~0.81–0.82 at best λ (Fig 5) |

> **Note**: The paper text states Spearman ρ = 0.910 but Figure 4 (right panel) shows 0.922 for the same experiment (λ=10.0). This likely reflects a single-seed result displayed in the figure vs. the mean over 10 seeds reported in text.

*Biological insight*: T cell subpopulations (negative scores) → ADT-specific information dominates; progenitor cells (positive scores) → RNA-specific information dominates. This matches known biology — T cell subsets are resolved by surface markers, progenitors by transcriptional programs.

**Clustering quality** (Appendix, Fig 18-23): IndiSeek-learned representations produce better ARI and NMI under k-means clustering compared to FactorizedCL and InfoDisen at optimal $\lambda$ (0.1 for FactorizedCL, 1.0 for InfoDisen, 10.0 for IndiSeek).

#### Dataset 2: MultiBench (Liang et al., 2021, *NeurIPS 2021*)
5 datasets: MOSI (2,199 YouTube clips), MOSEI (22,777 monologue videos), UR-FUNNY (16,514 TED talks), MUStARD (690 TV clips), MIMIC (36,000+ ICU records). Text + vision modalities only.

**Metric**: Linear probing accuracy on concatenated $(C_1, Z_1, C_2, Z_2)$, best $\lambda$ over $\{10^j : j=-3,...,3\}$, averaged over 10 seeds.

| Method | MOSI | MOSEI | UR-FUNNY | MUStARD | MIMIC |
|--------|------|-------|----------|---------|-------|
| **IndiSeek** | **70.03** | **75.47** | **63.79** | **57.46** | **65.99** |
| FactorizedCL | 67.11 | 74.74 | 58.36 | 56.45 | 65.69 |
| InfoDisen | 67.52 | 74.73 | 58.08 | 56.16 | 65.47 |
| CLIP baseline | 67.61 | 74.70 | 58.32 | 55.36 | 64.56 |

IndiSeek shows pronounced gains on larger video datasets (MOSI, UR-FUNNY, MOSEI) where the disentanglement quality matters more. MUStARD (only 690 samples) shows comparable performance across methods.

**Training efficiency**: All methods have comparable wall-clock training times (Table 9). IndiSeek is marginally faster on some datasets (MIMIC: IndiSeek 132.74s vs FactorizedCL 135.93s per run).

#### Simulated Experiments
4 controlled settings (Gaussian and non-Gaussian) with known ground-truth modality-specific coordinates. IndiSeek correctly identifies the ideal coordinates at $\lambda = 0.01$–0.1; FactorizedCL partially succeeds; InfoDisen fails due to linear vMF assumption.

#### Ablation: Cross-modal Switching
IndiSeek vs IndiSeek0 (intra-modal pairing, no cross-modal switching) on MOSI: 70.09% vs 69.59% (max over $\lambda$). The cross-modal switching provides a consistent improvement.

---

### Reproducibility

**Rating: 2/5**

*Justification*: The paper presents complete mathematical details and reports all hyperparameters, making the method reproducible in principle. However:

**Strengths:**
- All equations clearly stated with justifications
- Hyperparameters fully specified (Table 9, App A.3-A.4)
- CITE-seq dataset publicly available (Stuart et al., 2019; Seurat preprocessing pipeline linked)
- MultiBench datasets and preprocessing follow published pipeline (Liang et al., 2023b)
- Extensive λ sensitivity tables (Tables 4-8) and ablations

**Weaknesses:**
- **No code released** — the paper is an arXiv preprint and no GitHub repository is available
- Inner CLUB optimization (5 epochs, Gaussian $q_\theta$) details are in appendix but the exact stopping criterion for the inner loop is not specified
- CLIP stage details (whether $f_1, f_2$ are frozen vs jointly finetuned in Stage 2) not explicitly stated
- UMAP visualizations lack numeric ARI/NMI values in the main text (only described qualitatively)
- "results with and without the PCA dimension reduction are [comparable]" — Table 5 reference is mismatched in appendix

**Common Pitfalls:**
- λ grid search is expensive; paper recommends $10^{-1}$–$10^1$ but no principled selection rule is given
- CLUB inner loop can be numerically unstable if the auxiliary Gaussian $q_\theta$ diverges — monitor gradients
- For CITE-seq, RNA → PCA 200 is a preprocessing choice that significantly affects performance; using raw 2000-dim RNA yields slightly different but comparable results (App A.3.1)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
