---
layout: default
permalink: /paper-atlas/neuralode-flowmatching-review-1bfdc04f/
title: "NeuralODE_FlowMatching_review"
nav: false
description: "这是一篇 2026 年发表于 Communications Biology 的叙述性综述，而不是提出新算法的原始研究。它的主线是：单细胞测序通常只能取得不同细胞在若干时刻的“群体快照”，研究者如何用连续动力系统把这些离散快照连接起来，并从 Neural ODE 进一步走向基于最优传输和 Flow Matching 的生成模型。 因此，文章提供的是概念框架、数学入口和代表性方法分类；"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Communications Biology · 2026</span>
    </div>
    <h1>NeuralODE_FlowMatching_review</h1>
    <p>Generative models of cell dynamics: from Neural ODEs to flow matching</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42003-026-09758-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for NeuralODE_FlowMatching_review">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 从 Neural ODE 到 Flow Matching：单细胞动力学生成模型的证据化解读

### 这篇文章是什么，不是什么

这是一篇 2026 年发表于 *Communications Biology* 的叙述性综述，而不是提出新算法的原始研究。它的主线是：单细胞测序通常只能取得不同细胞在若干时刻的“群体快照”，研究者如何用连续动力系统把这些离散快照连接起来，并从 Neural ODE 进一步走向基于最优传输和 Flow Matching 的生成模型。

因此，文章提供的是概念框架、数学入口和代表性方法分类；它没有统一数据集上的定量 benchmark，也没有系统综述式的检索与纳入流程。图表中的方法归类不等于性能排名。

### 1. 真正的观测缺口：我们没有同一个细胞的电影

标准 scRNA-seq 会破坏细胞。时序实验在 $t_0,t_1,\ldots,t_T$ 得到的是不同细胞的样本：

$$
\mathbf{x}(t_k)\sim \mathbb{P}(\mathcal{X})_{t_k}.
$$

这里必须区分两种“时间”：

- 实验时间是样本真实采集时刻，适合讨论群体分布如何随物理时间变化；
- pseudotime 是从表达相似性推断的排序，适合非同步群体，但不是钟表时间。

这一区分决定了模型能声称什么。只拟合 snapshot marginals 的方法并没有观测到真实的单细胞祖先—后代路径；在多个向量场都能连接相同边缘分布时，动力学并不唯一。

### 2. 从 configuration space 到 phase space

图 1 把单细胞表达矩阵映射到状态空间。configuration space 只记录位置，例如表达向量或低维嵌入；pseudotime 在这个空间中给细胞排序。phase space 还加入“动量”或速度信息，使状态写成 $(\mathbf{x},\dot{\mathbf{x}})$。

直观例子是两条分化支路上各有一个 pseudotime 都为 0.6 的细胞。标量顺序相同，不代表它们可以互相演化；若知道各自的速度方向，支路更容易区分。但加入速度并不会自动解决测量噪声、隐藏变量和不可识别性。

### 3. Neural ODE 学到的是向量场

综述写出的核心方程是

$$
\dot{\mathbf{x}}(t)=f_\theta(\mathbf{x}(t)),
$$

其中 $f_\theta$ 是神经网络。给定初始状态，数值 ODE 求解器积分这个瞬时速度场，得到未来状态：

$$
\widehat{\mathbf{x}}(t)=\mathbf{x}(t_0)+\int_{t_0}^{t}f_\theta(\mathbf{x}(\tau),\tau)\,d\tau.
$$

图 2 应从左到右读：初始表达向量进入神经网络；网络输出当前速度；ODE solver 反复积分；最后得到多个未来时刻的预测。网络和求解器不是同一件事：前者参数化动力学规律，后者执行数值积分。

综述用 universal approximation 解释神经向量场的表达力，但表达力不等于可识别性。有限、噪声且互不配对的快照可能支持许多不同向量场，所以需要稀疏性、已知 GRN、谱系信息、干预数据或其他先验来约束答案。

### 4. 从向量场到 GRN：依赖关系不自动等于因果

若第 $i$ 个基因的变化率只依赖其候选父节点，文章写作

$$
\dot{x}_i(t)=f_i\!\left(x_{\mathrm{pa}(i)}(t)\right).
$$

这为把 ODE 依赖图连接到结构因果模型提供了形式入口。PathReg、C-NODE、PHOENIX、FLeCS 和 RegVelo 等代表方法用稀疏约束、具有生物意义的动力学形式、RNA velocity 或先验 GRN 增强解释性。

但仅在观测数据上发现 $x_j$ 有助于预测 $\dot{x}_i$，不能排除间接效应、反馈环和未观测混杂。综述本身把因果性列为首要挑战，并建议结合 perturbation 与领域先验。因此输出的边应理解为候选调控关系，除非还有干预证据支持。

### 5. 为什么最优传输适合群体快照

离散 OT 在两个群体分布之间寻找低成本 transport plan。Waddington-OT、Moscot、Moslin 和 JKONet 等方法可在时点之间分配质量，回答“早期群体可能对应哪些后期群体”。其优点是输入正好匹配 destructive sampling 的群体快照；局限是 transport plan 本身不一定给出整个区间内唯一的连续向量场。

连续 normalizing flow 则用 ODE 把一个分布连续变换成另一个分布。TrajectoryNet、Action Matching、MIOFlow、Neural LSB 和 TIGON 等把 OT 几何、能量、流形结构、增长死亡或随机过程纳入连续动力学。

### 6. Flow Matching 的关键变化：训练时直接回归速度场

传统 Neural ODE 训练通常需要通过数值积分比较预测轨迹与观测。Flow Matching 改为在条件概率路径上构造可计算的目标速度，直接训练

$$
\mathcal{L}_{\mathrm{FM}}
=\mathbb{E}_{t,\mathbf{x}_t}
\left\|v_\theta(\mathbf{x}_t,t)-u_t(\mathbf{x}_t)\right\|^2.
$$

文章用 mini-batch OT 匹配相邻时点样本，并以连接样本的直线路径说明目标向量场。它所说的 “simulation-free” 特指训练目标不必为每次更新完整积分学得的 ODE；模型训练完后若要生成连续轨迹，仍可能需要积分。

因此 Flow Matching 的主要优势是把难训练的“解 ODE 后再比较”转为更直接的向量场回归，而不是保证任何实现都只有固定一次网络计算。CFM、[SF]²M、GENOT、WLF 与 MFM 分别扩展到连续转移、Schrödinger bridge、多模态或非平衡耦合、熵正则和流形度量等场景。

### 7. 确定性与随机性

Neural ODE 描述给定状态下的确定性漂移。若生物过程的随机性不能被平均轨迹吸收，可使用 Neural SDE：

$$
d\mathbf{x}=f_\theta(\mathbf{x},t)dt+g_\phi(\mathbf{x},t)dW_t.
$$

Schrödinger bridge 在给定起终分布之间寻找相对参考扩散最可能、熵代价较小的随机过程。[SF]²M 与 Neural LSB 是综述强调的代表。随机模型更贴近细胞异质性，但也引入漂移、扩散和增长死亡之间更强的可识别性问题。

### 8. 五幅图如何组成文章的论证链

1. 图 1：从表达矩阵到 configuration space，再到包含方向的 phase space。
2. 图 2：神经网络给速度，ODE solver 积分成轨迹。
3. 图 3：同一 Neural ODE 骨架可服务于轨迹、嵌入、状态不稳定性、因果/GRN、扰动和预测。
4. 图 4：用“神经/参数化 ODE”与“数据流形/动力学定律”两个轴组织方法，并扩展到药代和医疗时序。
5. 图 5：Neural ODE 从离散状态积分轨迹；Flow Matching 从分布路径的目标速度训练向量场；两者最终都输出动力场。

这五图是概念图，不是实验结果图。它们适合建立选择框架，不能用来判断某方法在具体数据集上优于另一方法。

### 9. 方法选择的实用判断

| 研究目标与数据 | 更合适的起点 | 主要风险 |
|---|---|---|
| 单一 snapshot、只需排序 | pseudotime / configuration-space 方法 | 分支与时间尺度含义 |
| 有 spliced/unspliced 信号 | RNA velocity / phase-space 方法 | 动力学假设与基因独立性 |
| 有多个真实实验时点 | OT、CNF 或 Flow Matching | 无配对快照导致路径不唯一 |
| 需要连续预测或 perturbation | 受先验约束的 Neural ODE | 外推、混杂和可识别性 |
| 需要 GRN 候选边 | 稀疏/生物约束 Neural ODE | 预测依赖不等于因果 |
| 随机性、增长死亡不可忽略 | Neural SDE / Schrödinger bridge / unbalanced OT | 漂移和扩散更难区分 |

### 10. 综述留下的三条硬边界

- **因果性**：稀疏网络仍可能是相关结构；需要 perturbation、时间信息和生物先验。
- **超越插值的泛化**：仅重建已见时点不能证明学到了 governing law；应测试未见时点、初始状态或干预条件。
- **真实数据鲁棒性**：技术噪声、批次、隐藏状态、随机性和多组学异质性都可能改变学得的向量场。

最稳妥的结论不是“Flow Matching 解决了单细胞动力学”，而是它提供了一种更直接训练连续生成向量场的方式。模型是否代表真实细胞机制，仍取决于时间设计、耦合假设、先验信息与外推验证。

### 证据与复现边界

本解读基于本地 PMC 全文、五幅主图及 reporting summary。该文没有原创代码或统一 benchmark；补充 PDF 是 Nature Portfolio Reporting Summary，本地文本抽取为空，未作为技术证据。软件包当前维护状态、API 和安装方式均未核验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary: Generative Models of Cell Dynamics — from Neural ODEs to Flow Matching

**Paper**: Richter T, Wang W, Palma A, Theis FJ. "Generative models of cell dynamics: from Neural ODEs to flow matching." *Communications Biology* 9 (2026-02-27). DOI: 10.1038/s42003-026-09758-w

**Type**: Review article | **Category**: dynamics_fate_trajectory | **Code**: None (review)

---

### Motivation & Novelty

#### Biological Problem

Single-cell RNA sequencing (scRNA-seq) provides high-dimensional snapshots of gene expression across thousands of cells, but each cell is destroyed during measurement. This prevents direct temporal tracking of individual cells. Understanding how cells differentiate — transitioning from progenitor states to specialized fates — requires reconstructing continuous dynamics from these discontinuous, noisy snapshots. Classical low-dimensional ODE models (e.g., gene circuit models) are too constrained; purely data-driven clustering and pseudotime methods lack dynamical interpretability.

#### Limitations of Existing Approaches

- **Pseudotime methods** (Monocle, *Nat. Biotechnol.* 2014; Slingshot, *BMC Genom.* 2018; Palantir, *Nat. Biotechnol.* 2019; DPT, *Nat. Methods* 2016): Infer an ordering in configuration space rather than a velocity field. The review highlights ambiguity when cells on different branches receive similar pseudotimes; this is a limitation, not a claim that every pseudotime method fails on every branched dataset.
- **RNA velocity** (La Manno et al., *Nature* 2018; scVelo, *Nat. Biotechnol.* 2020): Estimates directional dynamics from splicing kinetics but assumes gene independence and is restricted to the RNA velocity framework
- **Classical CNF / simulation-based Neural ODEs**: Powerful but computationally expensive (ODE solve in every training step); limited scalability to high-dimensional scRNA-seq
- **Discrete OT methods** (Waddington-OT, *Cell* 2019; Moscot): Infer transport plans but not continuous vector fields; assume linearity between time points

#### What the Review Contributes

This is a conceptual synthesis paper, not a method paper. Its contributions are:
1. A **unified mathematical framework** connecting Neural ODEs, Continuous Normalizing Flows (CNFs), Optimal Transport, and Flow Matching
2. A **structured comparison** of 20+ methods across trajectory inference, GRN inference, representation learning, and medical time-series applications
3. Identification of **three core challenges** (causality, generalizability, robustness) and future research directions
4. A clear explanation of why **Flow Matching** represents a practical advance over earlier ODE-based generative models

---

### Method Overview

#### Conceptual Framework

The review organizes the landscape along two orthogonal axes:

**Axis 1: What is modeled?**
- *Manifold* (phenotypic structure): learns the shape of the differentiation manifold
- *Governing law* (dynamical equations): learns the differential equation driving dynamics

**Axis 2: How are dynamics represented?**
- *ODE-based* (deterministic): $\dot{\mathbf{x}} = f_\theta(\mathbf{x}, t)$
- *SDE-based* (stochastic): $d\mathbf{x} = f_\theta dt + \sigma\, dW$ (Neural SDE)

#### Neural ODE Core

A neural network $f_\theta$ parameterizes a vector field in which an ODE is solved:
$$\dot{\mathbf{x}}(t) = f_\theta(\mathbf{x}(t))$$

Trajectories are computed with a numerical ODE solver (the review names `torchdiffeq` as an example). The review writes a loss that compares ODE-predicted and observed states; it does not specify a particular differentiation algorithm for the solver.

**Causal extension**: Restricting $f_\theta$ to depend only on causal parents ($\dot{x}_i = f_i(x_{\text{pa}(i)})$) yields a Structural Causal Model, enabling GRN inference. Sparsity regularization (L1 in C-NODE; L0-L1 in PathReg, *NeurIPS* 2022) enforces biologically realistic sparse regulatory networks.

#### Flow Matching Advance

Flow Matching (CFM, ref 20) avoids simulating the ODE during training by directly regressing the vector field against an analytically tractable target:
- Pairs of cells $(x_0, x_1)$ are matched using mini-batch optimal transport
- Interpolated points: $x_t = (1-t)x_0 + tx_1$; target velocity: $u_t = x_1 - x_0$
- Loss: minimize $\|v_\theta(x_t, t) - u_t\|^2$

This is **simulation-free during training** in the review's sense: the vector-field regression objective avoids repeatedly integrating an ODE to construct each training target. ODE integration can still be needed after training to generate trajectories, and the paper does not provide a universal one-pass complexity guarantee.

#### Stochastic Extensions

Both paradigms extend to **Schrödinger Bridges** — minimum-entropy stochastic processes connecting two distributions — via Neural SDEs. Methods including Neural LSB and [SF]²M (simulation-free score-flow matching) solve the Schrödinger Bridge problem without full trajectory simulation.

---

### Evaluation

This is a review paper with no original experimental results. The review characterizes methods across the following dimensions:

#### Method Landscape Coverage

| Category | Methods Covered | Key Publications |
|---|---|---|
| Classical ODE methods | scVelo, Dynamo, PRESCIENT, veloVI | Nat. Biotechnol. 2020; Cell 2022 |
| Neural ODE for trajectories | TrajectoryNet, DeepVelo, LatentVelo, scTour | Sci. Adv. 2022; Genome Biol. 2023 |
| GRN inference via Neural ODE | PathReg, C-NODE, PHOENIX, RegVelo, FLeCS | NeurIPS 2022; Genome Biol. 2024 |
| OT-based dynamics | Waddington-OT, Moscot, Moslin, TIGON | Cell 2019; Genome Biol. 2024; Nat. Mach. Intell. 2024 |
| Flow Matching | CFM, [SF]²M, GENOT, WLF, MFM, Action Matching | ~2022-2025 |
| Neural SDE / Schrödinger Bridge | Neural LSB, [SF]²M | — |
| Medical / clinical | Neural CDE, LHM, LNODE, Neural ODE-PK, TE-CDE | NeurIPS 2021 |

#### Three Core Challenges (the review's primary analytical contribution)

1. **Causal interpretability**: Regulatory interactions in GRNs must be distinguished from correlations. Feedback loops, unobserved confounders, and indirect effects pose fundamental difficulties. Sparsity regularization helps but is insufficient alone; interventional data (perturbations) is needed.

2. **Generalizability beyond interpolation**: Models trained on observed snapshots must learn governing laws, not just interpolate. Evaluation should focus on out-of-distribution (OOD) prediction of unseen time points, drug perturbation responses, and novel initial conditions — not just reconstruction accuracy.

3. **Robustness to confounders**: Real scRNA-seq data contains technical noise, batch effects, and latent biological variation. Regularization strategies, biological priors (known GRN databases), and multi-modal data integration are needed for robust dynamics estimation.

---

### Reproducibility

**Rating: N/A** (Review article — no original experiments or code)

This paper synthesizes and discusses existing computational methods. There is no novel algorithm, dataset, or implementation to reproduce.

**Practical notes for readers**:
- `torchdiffeq` is named as an example ODE-solver library, but the review does not benchmark software implementations.
- Tables 1–3 and Figures 3–4 are a taxonomy of representative methods, not an exhaustive or quantitative ranking.
- The evidence supports choosing methods by data regime and scientific target; package maintenance status and current installation details were not assessed here.

**Strengths of the review**:
- Clear mathematical derivation from first principles (ODE → Neural ODE → Flow Matching)
- Well-organized taxonomy of methods (Tables 1-3)
- Honest about open challenges; does not oversell any approach

**Weaknesses**:
- No quantitative comparison between reviewed methods
- The PMC Markdown extraction has non-consecutive visible reference numbering; this is an extraction caveat and was not treated as evidence that the published article omitted references.
- The medical applications section (Table 3) is comparatively brief
- Does not cover recent multi-modal integration methods that combine spatial transcriptomics with dynamics

---

### Key Concepts Reference

| Term | Definition |
|---|---|
| Neural ODE | ODE whose vector field is parameterized by a neural network |
| CNF | Continuous Normalizing Flow — generative model using Neural ODE |
| Optimal Transport (OT) | Mathematical framework for finding minimum-cost distribution transport |
| Flow Matching (FM) | Training CNFs via vector field regression; avoids ODE simulation in training |
| Mini-batch OT | Approximate OT computed on small batches; enables scalable FM training |
| Schrödinger Bridge | Minimum-entropy stochastic process connecting two distributions |
| Neural SDE | Neural ODE extended with a diffusion (noise) term |
| GRN | Gene Regulatory Network — directed graph of transcriptional regulation |
| SCM | Structural Causal Model — causal DAG relating variables via functional equations |
| Waddington landscape | Metaphor: cells roll down valleys representing differentiated fates |
| Phase space | State space including both position (gene expression) and momentum (velocity) |
| Configuration space | State space of positions only (no velocity) — used by pseudotime methods |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
