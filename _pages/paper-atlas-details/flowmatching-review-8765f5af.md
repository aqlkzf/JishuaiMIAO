---
layout: default
permalink: /paper-atlas/flowmatching-review-8765f5af/
title: "FlowMatching_Review"
nav: false
description: "这不是一篇提出单一新算法的论文，而是一张“理论—数据类型—生物任务”的地图。作者先解释 flow matching（FM）为何能把生成问题写成分布间的连续运输，再把现有工作分到小分子、蛋白质、核酸、复合物与动力学、单细胞、多细胞和生物成像等层次，最后提出把这些层次连接成 AI virtual cell 的研究愿景。 因此阅读时要区分三种证据：基础理论公式说明 FM 怎样训练；表格和时间线整理已有方法；"
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
      <span>Representation Models</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>FlowMatching_Review</h1>
    <p>Flow matching for generative modelling in bioinformatics and computational biology</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-026-01220-0" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 生物信息学中的 Flow Matching：中文综述解读

### 这篇综述在回答什么

这不是一篇提出单一新算法的论文，而是一张“理论—数据类型—生物任务”的地图。作者先解释 flow matching（FM）为何能把生成问题写成分布间的连续运输，再把现有工作分到小分子、蛋白质、核酸、复合物与动力学、单细胞、多细胞和生物成像等层次，最后提出把这些层次连接成 AI virtual cell 的研究愿景。

因此阅读时要区分三种证据：基础理论公式说明 FM 怎样训练；表格和时间线整理已有方法；“virtual cell”是面向未来的整合框架，不是已经完成并统一验证的系统。

### 1. FM 的最小理论骨架

设容易采样的源分布为 $p_0$，真实数据分布为 $p_1$。FM 学习一个随时间变化的向量场 $u_t^\theta(x)$，由常微分方程

$$
\frac{dX_t}{dt}=u_t^\theta(X_t)
$$

把 $X_0\sim p_0$ 连续运输到 $X_1\sim p_1$。生成时从噪声或已知生物状态出发，沿学到的速度场积分到终点。

直接监督真实边缘向量场通常不可行，因为它需要对所有可能的源—目标配对积分。Conditional Flow Matching（CFM）改为在训练时抽取一个具体端点或端点对，构造条件概率路径，并回归该路径上可计算的条件速度：

$$
\mathcal L_{\mathrm{CFM}}=
\mathbb E\left[\left\|u_t^\theta(X_t)-u_t(X_t\mid X_1)\right\|^2\right].
$$

综述强调的关键理论结论是：在相应条件成立时，CFM 损失与不可直接计算的边缘 FM 损失具有相同梯度。训练因此不必先用数值求解器模拟整条轨迹，这就是“simulation-free training”的准确含义；它不等于采样时完全不需要 ODE 步进，也不等于生物系统本身无需模拟。

### 2. 一次训练与一次生成分别发生什么

最常见的欧氏空间示例取线性插值：

$$
X_t=(1-t)X_0+tX_1,
\qquad
u_t=X_1-X_0.
$$

训练时抽样 $X_0$、$X_1$ 和 $t\sim U(0,1)$，计算 $X_t$ 与目标速度，然后让神经网络预测它。生成时则从 $X_0$ 出发，反复更新

$$
X_{t+h}=X_t+h\,u_t^\theta(X_t)
$$

或使用更高阶 ODE 求解器。

端点如何配对非常重要。独立配对容易产生相互交叉、弯曲的运输路径；optimal-transport coupling 试图用较低运输成本匹配批内源与目标样本，使路径更直、速度回归方差更小。Rectified flow、mean flow、Schrödinger bridge、stochastic interpolants 等方法进一步在路径直线性、随机性、一步生成或动态建模之间做取舍。

对单细胞问题，还需判断源和目标是否真实配对。多数扰动实验只提供处理前后两个细胞群，并不知道某个终点细胞由哪个起点细胞演化而来；此时模型学的是分布层运输，而不是逐细胞谱系追踪。只有加入时间、多边缘或谱系约束，才可进一步讨论轨迹一致性。

### 3. 为什么生物数据不能只套用欧氏直线

综述把 FM 扩展分成三个关键方向。

#### 离散 FM

DNA、RNA、蛋白序列和化学键是离散变量。可将类别松弛到 simplex 上，也可使用连续时间马尔可夫链，以满足非对角跳转率非负、每列/行总率守恒等条件。此时模型预测的是类别之间的跃迁率，而不是连续坐标速度。把 one-hot 向量直接线性插值虽然方便，却不自动保证中间状态是合法序列。

#### 几何 FM

三维蛋白和核酸同时包含平移与旋转。残基框架可位于 $\mathrm{SE}(3)^N$，旋转部分属于 $\mathrm{SO}(3)$；应沿流形测地线插值，并让向量场满足刚体变换等变性。这样旋转输入会同步旋转输出，而不会改变预测的内部结构。手性也要求谨慎：反射通常不是允许的生物变换。

#### 随机和分布值 FM

细胞群、空间 niche 或构象 ensemble 本身就是分布。Schrödinger bridge、stochastic FM、Wasserstein FM、Meta FM 等把不确定性、群体异质性或“分布的分布”纳入对象。选择确定性 ODE 还是随机 SDE，不是单纯工程偏好，而取决于任务是否需要一对多结果和真实随机动力学。

### 4. 分子层：四类任务不能混为一谈

#### 小分子生成

SemlaFlow、FlowMol 等同时处理三维坐标、原子类别和键。FM 的吸引力是采样步数可能少于扩散模型；但化学有效性仍依赖等变架构、离散—连续联合表示、价态与手性约束。论文中“更快”通常来自特定模型和 benchmark，不能推广为所有 FM 都固定快于所有 diffusion。

#### 蛋白质与肽

FrameFlow、FoldFlow、Multiflow 等在残基框架、序列或二者联合空间生成。这里评价不能只看几何相似，还要看 designability、diversity、novelty、序列可折叠性和条件满足程度。结构生成得像蛋白，并不等于具备目标功能。

#### 核酸

Dirichlet/Fisher FM 可处理 simplex 上的 DNA/RNA 序列；RNA 任务还需耦合二级结构、三维构象与蛋白条件。综述列举的 RNACG、RNAFlow、RNA-FrameFlow 等覆盖不同输出，不能用一个统一的“RNA FM 性能”概括。

#### 复合物与动力学

FlowDock、NeuralPLexer3、FlexDock、UniMoMo 等面向 docking、co-folding 或条件设计；AlphaFlow、FMRC、MDGen 等面向 ensemble、reaction coordinate 或轨迹。静态复合物预测和真实动力学生成目标不同：前者重视 pose/affinity，后者还需自由能、动力学时间尺度和路径统计。

### 5. 细胞与成像层：FM 学到的是条件分布映射

在单细胞扰动预测中，输入可以是对照细胞分布及药物、基因、剂量或细胞类型条件，输出是处理后表型分布。CFM、[SF]²M、GENOT、CellFlow、CFGen 等分别处理确定性/随机运输、跨模态对齐、组合泛化等问题。最重要的评价不是生成点云“看起来像”，而是未见条件下的分布距离、差异表达/通路保持、协方差与亚群比例，以及跨批次和跨供体稳健性。

多时间点问题可用 multi-marginal FM 约束多个边缘，避免逐时间段独立拟合造成全局不一致。Growth-aware 方法还要考虑增殖和死亡，因为细胞群的质量不一定守恒；普通平衡 OT 会把数量变化误解释为细胞移动。

多细胞和 bioimaging 目前相对早期。CellFlux 等在像素或表征空间模拟形态响应，能够生成从对照到药物处理的图像变化。但批次效应、显微平台差异与纹理捷径可能让模型学到非生物信号，必须用跨实验验证和可解释表型指标约束。

### 6. 三张主图如何组织全文

#### 图 1：从分布运输到生物应用

顶部以细胞群 A 到 B 的箭头展示时间依赖速度场；中部用从噪声到蛋白、小分子的图示说明生成；底部把分子、细胞与虚拟细胞愿景连接。工作区实际提取的 `Fig1_02.jpg` 显示两群细胞间的运输，`Fig1_03.jpg` 与 `Fig1_04.jpg` 分别显示蛋白和小分子生成；`Fig1_01.jpg` 只是很小的装饰图标，不应当被解释为完整面板。

#### 图 2：历史时间线

图 2从 normalizing flow、continuous normalizing flow/Neural ODE 追到 2022 年前后的 FM、rectified flow、stochastic interpolants，再到 2023–2025 年快速增长的生物应用。它支持的是领域发展脉络，不是方法数量增长即可证明科学有效性。OCR 没有把图 2单独提取成图片，当前解读来自全文时间线说明和图注。

#### 图 3：virtual cell 的层级分类

本地图像明确显示从 molecular modelling 向 single-cellular、multicellular、virtual cell 逐级上升，右侧“potential future directions”指向跨分子与细胞语境的 multiscale FM。箭头表达研究议程，不表示这些层级已经端到端连通。

### 7. 表 1–3 应怎样使用

- 表 1比较 GAN、VAE、normalizing flow、diffusion 和 FM 等生成范式。它是定性属性总结，具体项目仍需比较数据似然、采样成本、条件控制和约束满足。
- 表 2列出基础 FM 与改进方法及开源入口，是选算法和找实现的索引，不是性能排行榜。
- 表 3按数据模态、任务、数据源和指标汇总生物应用。不同条目的 benchmark 不同，不能跨任务直接按单一数值排名。

### 8. 实践选型：先问五个问题

1. 数据是连续坐标、离散序列、图、图像，还是它们的组合？
2. 目标是无条件生成、条件设计、群体映射、轨迹，还是动力学？
3. 是否有真实配对、时间、谱系、空间或物理约束？
4. 需要确定性的一对一运输，还是一对多不确定性？
5. 评价能否覆盖化学/结构有效性、分布泛化与实验验证，而不仅是生成质量代理指标？

欧氏 CFM 适合简单连续表征基线；离散 token 需要 discrete/simplex FM；三维构象需要流形与等变设计；群体数量变化需要 unbalanced 或 growth-aware transport；多个时间点需要 multi-marginal 约束；一对多结果则应考虑 stochastic flow 或 bridge。

### 9. 综述提出但尚未解决的边界

作者在 Outlook 中明确列出高维和数据稀缺条件下的最优性、收敛与表达力问题；大规模多模态训练成本；跨模态和跨尺度整合；缺少统一真实世界 benchmark；解释与实验验证；以及闭环实验设计。

这里还应加一层阅读警惕：显式速度场并不自动等于因果机制，最优运输路径也不自动等于真实生物时间轨迹。模型可能在观测分布之间找到数学上简洁的路径，但未观测中间状态、混杂因素和选择偏差会影响生物解释。要接近 virtual cell，需要将扰动实验、机制约束、不确定性、跨尺度因果关系和实验反馈真正连接起来。

### 10. 关于本地 companion code 的严格边界

工作区保留了 TorchCFM 的 `conditional-flow-matching/` 快照，它能帮助理解基础 CFM、OT coupling 和若干通用变体，但不是这篇综述的配套实现，也不实现表 3中几十个生物方法。按照 review 路由，本次分析不把该仓库作为论文代码证据，`local metadata` 记录 `has_code=false`，`code source` 仅作为历史参考资产保留。旧 `doc_code.md` 是过往对通用库的旁注，不参与 review 完整性或论文复现判断。

### 推荐阅读路线

先读图 1和“Workflow of flow matching”理解训练/生成差别，再读 discrete 与 geometric FM；随后按自己的数据类型跳到分子、单细胞或成像章节；最后用图 3、表 3和 Outlook 检查跨尺度愿景与真实证据之间的距离。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Flow Matching for Generative Modelling in Bioinformatics — Summary

**Paper**: "Flow matching for generative modelling in bioinformatics and computational biology"
**Authors**: Alex Morehead, Lazar Atanackovic, Akshata Hegde, Yanli Wang, Frimpong Boadu, Joel Selvaraj, Alexander Tong, Aditi Krishnapriyan, Jianlin Cheng
**Journal**: Nature Machine Intelligence (2026)
**DOI**: 10.1038/s42256-026-01220-0
**Type**: Review article

---

### Motivation & Novelty

#### The Biological Problem

Computational biology faces a recurring challenge: learning mappings between different states of biological systems. Examples include:
- Transforming diseased cell states back to healthy states
- Predicting cellular responses to genetic or chemical perturbations
- Generating novel protein/RNA structures with desired properties
- Simulating molecular dynamics trajectories
- Reconstructing single-cell developmental trajectories from snapshot data

These problems share a common mathematical structure: learning a transport map between two probability distributions.

#### Limitations of Existing Approaches

Prior generative models each have significant drawbacks:

| Model | Key Limitation |
|-------|---------------|
| **Diffusion models** (Ho et al., *NeurIPS* 2020; Yang et al., *ACM Comput. Surv.* 2023) | Require 100s–1000s of inference steps; slow sampling; Gaussian noise assumption |
| **GANs** (Dhariwal & Nichol, *NeurIPS* 2021) | Mode collapse; training instability; no likelihood |
| **VAEs** (Kingma & Welling, *ICLR* 2014) | Blurry outputs; posterior collapse; approximate likelihood only |
| **Normalizing flows** (Rezende & Mohamed, *ICML* 2015) | Expensive Jacobian computation; bijective architecture constraints |
| **Continuous normalizing flows** (Chen et al., *NeurIPS* 2018) | Require ODE simulation during training; slow |

#### What Flow Matching Contributes

Flow matching (FM), formalized by Lipman et al. (*ICLR* 2023) and extended by Tong et al. (*TMLR* 2024), offers four simultaneous advantages over diffusion models:
1. **Fewer inference steps** — straight-line OT paths require 10-100× fewer steps
2. **Simpler implementation** — no score function, no SDE; just MSE regression
3. **Explicit distribution coupling control** — source $p_0$ can be any distribution, not just Gaussian
4. **Geometric property preservation** — equivariance through network design

This review is the first comprehensive survey of FM applications across all of computational biology, covering 50+ methods spanning molecular modelling, single-cell biology, multicellular imaging, and bioimaging.

---

### Method Overview

#### Core Framework

FM learns a time-dependent vector field $u_t^\theta: [0,1] \times \mathbb{R}^d \to \mathbb{R}^d$ that transports samples from a source distribution $p_0$ to a target distribution $p_1$ via an ODE:

$$\frac{d}{dt}\psi_t(x) = u_t^\theta(\psi_t(x))$$

Training minimizes the **conditional FM (CFM) loss** — a simple MSE between predicted and target velocities:

$$\mathcal{L}_{CFM}(\theta) = \mathbb{E}_{t, X_1, X_{t|1}} \|u_t^\theta(X_{t|1}) - u_t(X_{t|1}|X_1)\|^2$$

For the optimal-transport path (most common), the target velocity is simply $u_t = X_1 - X_0$, and the interpolated point is $X_{t|1} = tX_1 + (1-t)X_0$.

#### Key Technical Components

1. **Probability path design**: Linear OT paths (straight lines), variance-preserving trigonometric paths, Schrödinger bridge paths — each with different tradeoffs in trajectory curvature and variance
2. **Minibatch OT coupling**: Pairs source and target samples via exact EMD or Sinkhorn to reduce estimator variance
3. **Discrete FM**: Extends to DNA/RNA/protein sequences via continuous-time Markov chains
4. **Geometric FM**: SE(3)-equivariant vector fields for 3D biomolecular structures on Riemannian manifolds
5. **Conditional generation**: Conditions on protein partners, ligand structures, perturbation embeddings, etc.

#### Biological Assumptions

- Biological state transitions can be modeled as continuous transport between distributions
- The source distribution (often Gaussian) is a reasonable prior for biological data
- For molecular data: chirality and geometric symmetries must be preserved (SE(3) equivariance)
- For single-cell data: cells can be treated as samples from a high-dimensional distribution

#### Computational Pipeline

See `doc_method.md` for full mathematical details and `doc_code.md` for implementation.

---

### Evaluation

#### Application Domains and Key Results

**Molecular Modelling**:
- Small molecule generation: SemlaFlow achieves 93.9% validity on GEOM-Drugs, 100× faster than diffusion
- Protein structure generation: Multiflow achieves 0.86 designability on PDB (+37% vs prior SOTA)
- Protein-ligand docking: FlowDock achieves 50.7% (RMSD<2Å + PoseBusters) on PDB
- Biomolecular dynamics: AlphaFlow achieves 0.48 pairwise RMSD correlation (+218% vs prior)

**Single-Cellular Modelling**:
- Cell phenotype prediction: CellFlow achieves R²=0.60 on PBMC (+200% vs prior)
- Compositional generation: CFGen achieves 10.7 2-WD on Human Lung Cell Atlas
- Cross-modal alignment: GENOT achieves 0.16 FOSCTTM on True Match dataset (+48%)

**Multicellular / Bioimaging**:
- Cell morphology: CellFlux achieves FIDc=84.4 on JUMP dataset (+16%)
- Cryo-EM: CryoFM achieves 0% fail rate on EMDB (first of its kind)
- MRI reconstruction: MOTFM achieves 3D-FID=7.93 (+73%)

#### Metrics Used
- **Molecular**: RMSD, TM-score, designability (scTM), validity (RDKit), perplexity
- **Single-cell**: Wasserstein distance (1-WD, 2-WD), R², FOSCTTM
- **Imaging**: FID, SSIM, fail rate

#### Comparative Methods
All comparisons are in silico benchmarks. The review notes that real-world experimental validation remains limited — OriginFlow is a notable exception with 90% expression/affinity/solubility rates in wet-lab validation.

---

### Reproducibility landscape

This review is not accompanied by one implementation that reproduces its survey. Tables 2 and 3 point to many independent repositories with different licenses, datasets, preprocessing, checkpoints and evaluation protocols. The article is reproducible as a literature map, but its cross-domain performance statements cannot be regenerated through a single environment or benchmark harness.

The retained TorchCFM snapshot in this workspace is a general foundational library and is not evidence for the surveyed biological methods. Reproducing any application requires following that primary method's own repository and data contract. The review itself identifies unified real-world benchmarks, experimental validation, open tooling and community standards as unmet needs.

**Strengths**:
- Theoretically grounded; gradient equivalence (Eq.7) is proven
- Simulation-free training is a major practical advantage
- Flexible: works for 2D toy problems, images, single-cell data, tabular data
- Active development; 2024-2025 saw rapid expansion of bioinformatics applications

**Weaknesses**:
- Review paper: no novel method or unified implementation is proposed
- Benchmark comparisons across methods are heterogeneous (different datasets, metrics, baselines)
- "Virtual cell" vision is aspirational; no integrated multi-scale FM system exists yet

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
