---
layout: default
permalink: /paper-atlas/regvelo-62d9538e/
title: "regvelo"
nav: false
description: "RegVelo 用可学习 GRN 将各基因的转录率耦合进高维剪接 ODE，使速度、局部有效网络和网络扰动来自同一个生成模型；它显著增强了假设生成能力，但模型权重、数值求解、先验网络和 CellRank 下游共同限定了因果与复现解释。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>bioRxiv · 2024</span>
    </div>
    <h1>regvelo</h1>
    <p>RegVelo: gene-regulatory-informed dynamics of single cells</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2024.12.11.627935" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## RegVelo 方法解读：让转录调控直接进入 RNA 速度方程

### 1. RegVelo 补上了哪块缺口

传统 RNA velocity 用未剪接 RNA $u$ 和已剪接 RNA $s$ 估计每个基因的瞬时变化，但通常把基因逐个拟合，并把转录率设为常数或分段常数。GRN 方法能够给出转录因子与靶基因的关系，却常是静态相关网络。RegVelo 的核心是把两者合成同一个生成模型：上游调控因子的表达决定靶基因转录率，转录率再进入剪接 ODE，所有基因因此成为一个耦合动力系统。

它接收同一批细胞的 spliced/unspliced 矩阵以及可选先验 GRN，联合输出潜在时间、动力学参数、速度后验和一个可用于扰动的调控权重矩阵。这里的“可解释”和“可操作”是模型层面的：权重与局部 Jacobian 可产生调控假设，修改网络后可重新模拟速度；它们仍需独立扰动实验验证。

### 2. 核心方程：基因不再彼此独立

对靶基因 $g$，剪接动力学为

$$
\frac{du_g(t)}{dt}=\alpha_g(t)-\beta_g u_g(t),
\qquad
\frac{ds_g(t)}{dt}=\beta_g u_g(t)-\gamma_g s_g(t).
$$

$\beta_g$ 和 $\gamma_g$ 分别是剪接与降解率。区别在于转录率不是常数，而是

$$
\alpha_g(t)=h\!\left([Ws(t)+b]_g\right).
$$

$W_{gj}$ 表示调控因子 $j$ 对靶基因 $g$ 的权重，$b_g$ 是基础转录偏置，$h$ 默认是 softplus，保证转录率非负。正权重可解释为激活方向，负权重为抑制方向，但这是拟合模型中的有效作用：共同调控、遗漏变量和表达相关性仍可能造成间接边。

当前源码直接实现这条链：`src/regvelo/_module.py` 的 velocity encoder 构造 $\alpha=h(Ws+b)$，再返回 $du=\alpha-\beta u$ 和 $ds=\beta u-\gamma s$；`VELOVAE.__init__` 位于 `:435-605`，把 GRN 权重、动力学率、潜在编码器和 ODE 批处理器装进同一模块。

因为 $\alpha_g$ 依赖所有调控因子的 $s(t)$，系统不再能按基因独立解析求解。RegVelo 用 torchode 的 Dopri5 步进器并行积分高维 ODE。当前代码使用 `FixedStepController`，不能把“Dopri5”自动理解成带误差容忍度的自适应积分；步长和数值稳定性是复现边界。

### 3. 潜变量和基因特异时间

编码器把每个细胞的 spliced 与 unspliced 拼接后映射到低维潜变量 $z$。解码器从 $z$ 输出每个靶基因的潜在时间 $t_{ng}$，而不是强迫一个细胞只有单一全局时间。这样可以表达某些基因较早启动、另一些基因较晚启动。

源码 `inference()` 在 `_module.py:654-705` 形成 $q(z|u,s)$ 并取动力学率，`generative()` 在 `:724-775` 解码时间并生成观测分布。基因特异时间增加了灵活性，也增加可辨识性问题：不同时间、速率和网络权重组合可能产生相近表达。论文 Methods 专门做参数可辨识性检查，但一次模型收敛不等于每个参数都具有唯一生物解释。

### 4. 先验 GRN 如何进入训练

先验可来自 ATAC/multiome、SCENIC+、数据库或其他 GRN 推断。RegVelo 提供两种约束。

#### 4.1 硬约束

不在先验中的边梯度被掩蔽，训练不能创建这些边。源码在 `_module.py:568-583` 注册 mask 并设置梯度 hook。优点是参数少、解释集中；缺点是错误或不完整先验会永久删除真实边。

#### 4.2 软约束

先验外边仍可学习，但用

$$
R_{prior}(W;G)=\|W\odot(1-G)\|_2
$$

惩罚。源码损失在 `_module.py:888-894`。软约束能修正先验，但惩罚系数 $\lambda$ 决定模型更相信数据还是先验。当前构造还可限制调控因子集合并默认去除自调控；这不是普适生物事实，而是模型选择。

### 5. 训练目标不只是 ELBO

模型以标准正态为 $z$ 先验，以 Gaussian likelihood 重建目标基因的 $u,s$，用变分推断优化重建项与 KL 项。当前 `loss()` 位于 `_module.py:820` 以后，此外还有多种正则项：

- 先验图惩罚限制先验外权重；
- Jacobian L1 惩罚鼓励局部有效网络稀疏；
- velocity constraint 鼓励 $du$ 具有合适动力学变化，源码中乘以 100；
- bias constraint 抑制不合理基础转录；
- alpha–unspliced 相关项沿排序时间约束转录活动与随后未剪接 RNA 的一致性，见 `:872-875`。

这些项共同决定结果。“由数据学习 GRN”不是无约束识别：网络结构会受到先验、稀疏性、相关项、率参数夹断和超参数共同影响。当前源码把 $\beta,\gamma$ 经 softplus 后夹在 $[0,50]$，这是数值稳定设计，不应误解为论文证明的生物范围。

### 6. 训练后速度与 GRN 各是什么

spliced velocity 为

$$
v_{gn}=\beta_g\bar u_{gn}-\gamma_g\bar s_{gn},
$$

其中 $\bar u,\bar s$ 是模型在潜在时间处的拟合丰度。通过从 $q(z|u,s)$ 多次采样，可以得到速度后验和不确定性。后验不确定性只覆盖模型表示的随机变量，不覆盖先验 GRN 错误、缺失调控层、批次效应或模型错设。

全局 $W$ 经过转录函数的局部导数得到状态依赖 Jacobian：

$$
J_\alpha(s)=\operatorname{diag}(h'(Ws+b))W.
$$

softplus 下 $h'$ 是 sigmoid。对某类细胞平均 Jacobian 可形成 cell-type-specific 有效 GRN。由于同一个 $W$ 被状态依赖系数调制，同一条边在不同状态的有效强度可以不同。它仍是模型局部敏感性，不等于直接 DNA 结合证据。

### 7. in silico 扰动怎样工作

敲除调控因子可通过屏蔽 $W$ 中对应调控输出边，得到扰动网络 $W^*$，然后重新计算速度。RegVelo 再把原始/扰动速度交给 CellRank，比较终末命运概率。局部效应用速度余弦差异，命运效应用命运概率变化、t 统计量或 depletion score 汇总。

这条链包含两层模型：RegVelo 从表达推速度，CellRank 从速度核推命运。任何变化都依赖邻域图、kernel、terminal states 和宏状态设置。网络屏蔽也近似瞬时丢失调控关系，没有显式建模蛋白半衰期、补偿反馈和组织环境。因此 in silico KO 是筛选实验优先级的工具，不是 KO 表型的替代品。

源码工具位于 `src/regvelo/tools/`：`_in_silico_block_simulation.py` 和 `_in_silico_block_regulation_simulation.py` 改变网络并重算动态；`_perturbation_effect.py`、`_TFscreening.py` 和 `_regulation_scanning.py` 汇总扰动；`metrics/` 提供 fate、depletion、abundance 与 TSI 等指标。

### 8. 六张主图的证据链

- 图 1：模型架构、FUCCI 细胞周期速度/潜时与 GRN 基准，建立“联合动力学 + 调控”主张。
- 图 2：胰腺内分泌和细胞周期扰动，展示网络屏蔽如何改变 CellRank 命运概率，并与已知 `E2f1` 调控比较。
- 图 3：人造血中比较速度、终末状态、GATA1/SPI1 调控和命运驱动排序。
- 图 4：斑马鱼神经嵴 Smart-seq3 数据、先验 GRN、速度与 Perturb-seq，系统筛选命运调控因子。
- 图 5：聚焦 `tfec`，用计算、Perturb-seq、ChromBPNet/ATAC 和胚胎表型支持其早期色素命运作用及冗余网络。
- 图 6：聚焦新候选 `elf1`，结合 KO、HCR、靶位点和 toggle-switch 模型提出其与色素/间充质命运的调控回路。

补图 1–9覆盖速度/GRN基准、胰腺和造血命运、`E2f1` 扰动、神经嵴表达、与 CellRank/Dynamo 的驱动基因比较以及 `elf1` 支持证据。16 个本地图像抽取物已逐一视觉检查；OCR 将部分主图与补图各保存为一个整图。

### 9. 论文结果应怎样读

FUCCI 数据提供近似方向与时间参考，支持 RegVelo 在周期系统中恢复速度方向、潜时和部分调控边。胰腺与造血基准比较 scVelo、veloVI 等方法的终末状态和已知驱动。斑马鱼部分证据最强，因为模型预测的 `tfec` 与 `elf1` 后续接受 Perturb-seq、CRISPR、HCR 和染色质结合位点支持。

但验证强度并不均一：已知 marker/driver 列表可能偏向文献充分的 TF；GRN AUROC 依赖选定正负边；CellRank 终末状态和命运指标是下游推断；`tfec` 三重 KO 还涉及冗余解释；`elf1` 回路是多证据支持的候选机制而非完整因果网络。

### 10. 论文—代码与版本边界

当前论文是 bioRxiv v1，DOI `10.1101/2024.12.11.627935`，PDF 创建于 2024-12-11，不能标成 Nature Methods 正式发表。源码链接为 `https://github.com/theislab/regvelo`，本工作区根就是一个源码快照，含 `src/`、测试和文档；但没有 `.repo_source`、独立 `.git` 或固定 commit。`pyproject.toml` 用 setuptools-scm 动态生成版本，因此脱离 Git 元数据不能确定快照包版本。

依赖只给范围而非锁文件，例如 Python `>=3.10`、scvi-tools `<1.2.1`、torch `<2.6.0`、torchode `>=0.1.6`。工作区也未保存全部论文数据和逐图 notebook。因此可验证的是核心实现与论文方程的对应，不是精确环境或所有图的一键复现。

现有源码还包含需要谨慎记录的实现细节：固定步长 ODE 控制器、率夹断、velocity loss 的 100 倍权重、额外 alpha 相关项，以及部分工具对设备/AnnData 键的假设。复现应从论文数据、先验 GRN、预处理层、基因/调控因子索引、随机种子、依赖和 CellRank 配置逐层锁定。

### 11. 最安全的一句话总结

RegVelo 用可学习 GRN 将各基因的转录率耦合进高维剪接 ODE，使速度、局部有效网络和网络扰动来自同一个生成模型；它显著增强了假设生成能力，但模型权重、数值求解、先验网络和 CellRank 下游共同限定了因果与复现解释。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## RegVelo: Gene-Regulatory-Informed Dynamics of Single Cells

### Paper Information
- **Title**: RegVelo: gene-regulatory-informed dynamics of single cells
- **Source**: bioRxiv preprint v1 (posted 11 December 2024)
- **DOI**: 10.1101/2024.12.11.627935
- **Repository**: https://github.com/theislab/regvelo

### Reproducibility Rating: 3/5 (algorithm source available; full paper reproduction incomplete)

**Overview**: RegVelo is the first end-to-end deep learning model that couples RNA splicing dynamics with gene regulatory networks (GRNs), enabling both cellular trajectory inference and in silico perturbation predictions.

**Strengths**:
- Full open-source implementation with scvi-tools integration
- API documentation and tutorial narratives are present
- Standard AnnData input format
- All core paper equations verified in code
- GPU-accelerated ODE solving via torchode

**Minor Blockers**:
- Prior GRN construction requires external tools (Pando, ChIP-seq databases, SCENIC+)
- Hyperparameters `lam`, `lam2` require dataset-specific tuning
- Exact paper environments, full per-figure scripts and all dataset snapshots are not stored in this workspace
- ODE solver uses `FixedStepController` by default, not adaptive stepping
- `inferred_grn()` function hardcodes `cuda:0` device

---

### Motivation and Novelty

#### Biological Problem Addressed

RegVelo addresses a fundamental disconnect in single-cell biology between two crucial but isolated research areas:

1. **RNA velocity methods** (scVelo, veloVI) that model cellular dynamics but assume gene independence and constant transcription rates
2. **GRN inference methods** that identify regulatory relationships but omit the dynamically changing nature of biological systems

From the paper (Methods section):
> "Both models neglect gene-gene dependencies and assume a piecewise constant transcription rate for each gene, thereby overlooking the dynamic changes in the transcription rate itself. Biological systems fulfill these assumptions only approximately, however, and exhibit more complex dynamics."

#### Key Innovation

RegVelo introduces **regulation-dependent transcription rates** where:
- Traditional RNA velocity: $\alpha_g = \text{constant}$
- RegVelo: $\alpha_g(t) = h\left(\sum_{j=1}^{N_G} W_{g,j} s_j^{(n)} + b_g\right)$

This couples gene dynamics through a shared regulatory weight matrix $W$, enabling:
1. In silico perturbation predictions by modifying $W$
2. Cell-type-specific GRN inference via Jacobian analysis
3. Mechanistic insight into developmental regulation

---

### Method Overview

#### Core Mathematical Framework

**Paper Equations 1-2** (ODEs for spliced/unspliced dynamics):
$$\frac{du_g(t)}{dt} = \alpha_g \mathbb{I}_{\{t < t_s\}} - \beta_g u_g(t)$$
$$\frac{ds_g(t)}{dt} = \beta_g u_g(t) - \gamma_g s_g(t)$$

Where:
- $u_g$: Unspliced (pre-mRNA) abundance
- $s_g$: Spliced (mature mRNA) abundance
- $\alpha_g$: Transcription rate
- $\beta_g$: Splicing rate
- $\gamma_g$: Degradation rate

**Paper Equation 2** (GRN-informed transcription rate):
$$\alpha_{gn} = h\left(\sum_{j=1}^{N_G} W_{g,j} s_j^{(n)} + b_g\right)$$

Where:
- $W \in \mathbb{R}^{N_G \times N_G}$: Learnable GRN weight matrix
- $s^{(n)}$: Spliced RNA abundances for cell $n$
- $b_g$: Basal transcription rate (bias term)
- $h(x) = \log(1 + e^x)$: Softplus activation ensuring $\alpha > 0$

**Biological Interpretation**:
- $W_{g,j} > 0$: TF $j$ activates gene $g$
- $W_{g,j} < 0$: TF $j$ represses gene $g$
- $W_{g,j} = 0$: No regulatory relationship

#### GRN Constraint Strategies

**Hard Constraints** (Paper Eq. 3):
$$W_{j,k} = \begin{cases} 0 & \text{if } G_{j,k} = 0 \\ \omega \in \mathbb{R} & \text{otherwise} \end{cases}$$

**Soft Constraints** (Paper Eq. 3):
$$R_{\text{prior}}(W;G) = \|W \odot (1 - G)\|_2$$

Where $G$ is the binary prior GRN and $\odot$ is element-wise product.

#### Gene-Specific Latent Time

RegVelo models gene-specific latent times via a decoder network:
$$t_{ng} = [T(z^{(n)})]_g$$

Where:
- $z^{(n)} \sim \mathcal{N}(0, I_d)$: Latent cell representation ($d=10$ dimensions)
- $T: \mathbb{R}^d \to (0,1)^{N_G}$: Neural network decoder with sigmoid output

**Biological rationale**: Different genes can undergo different biological processes simultaneously (e.g., cell cycle vs. differentiation).

#### ODE Integration

Given initial conditions and latent times, RNA abundances are computed by numerical integration:
$$\bar{u}^{(g)}(t_{ng}) = u_g(0) + \int_0^{t_{ng}} \dot{u}_g(s(t_g), u(t_g)) dt_g$$
$$\bar{s}^{(g)}(t_{ng}) = s_g(0) + \int_0^{t_{ng}} \dot{s}_g(s(t_g), u(t_g)) dt_g$$

**Implementation**: torchode library with Dopri5 method (5th-order Runge-Kutta).

#### Multi-Component Loss Function

$$L(\theta, \phi) = -\text{ELBO} + \lambda_1 R_{\text{prior}}(W;G) + \lambda_2 L_{\text{Jacobian}} + L_{\text{velocity}} + L_{\text{base}}$$

**ELBO** (Evidence Lower Bound):
$$\text{ELBO}(\theta,\phi;u,s) = -\text{KL}[q_\phi(z|u,s) \| p(z)] + \mathbb{E}_{q_\phi}[\log p_\theta(u,s|z)]$$

**Jacobian Regularization** (Paper Eq. 6) - Promotes sparse GRN:
$$L_{\text{Jacobian}} = \frac{1}{N_C} \sum_{n=1}^{N_C} \left\| \text{diag}(\text{sigmoid}(Ws^{(n)} + b))W \right\|_1$$

**Velocity Regularization** (Paper Eq. 7) - Encourages smooth dynamics:
$$L_{\text{velocity}} = \sum_{n=1}^{N_C} \|\text{softplus}(Ws^{(n)} + b) - \beta u^{(n)}\|_2$$

**Base Transcription Regularization** (Paper Eq. 8):
$$L_{\text{base}}(b) = \|b + b^*\|_2 \quad \text{where } b^* = 10$$

---

### Downstream Analysis

#### Velocity Computation
$$v_{gn} = \beta_g \bar{u}^{(g)}(t_{gn}) - \gamma_g \bar{s}^{(g)}(t_{gn})$$

#### Cell-Type-Specific GRN Inference
The learned regulatory function is linearized via Taylor expansion:
$$\text{GRN}_c = \sum_{j \in \mathcal{S}(c)} \text{diag}(\text{sigmoid}(Ws^{(j)} + b))W$$

Where $\mathcal{S}(c)$ is the set of cells of type $c$.

#### In Silico Perturbation
To simulate TF $l$ knockout:
$$\hat{W}_{j,k} = \begin{cases} W_{j,k} & \text{if } k \neq l \\ 0 & \text{if } k = l \end{cases}$$

**Cell Fate Perturbation Metric** (t-test statistic):
$$t = \frac{\bar{\Pi}^*_{:,k} - \bar{\Pi}_{:,k}}{\sqrt{2S^2/N_C}}$$

**Depletion Score**:
$$\Delta_d = 1 - 2\ell_d$$

Where $\ell_d$ is normalized Mann-Whitney U statistic.

---

### Evaluation Strategy

#### Datasets Used

| Dataset | Cells | System | Ground Truth |
|---------|-------|--------|--------------|
| Cell Cycle (U2OS-FUCCI) | 1,146 | G1 -> S -> G2M | FUCCI markers |
| Pancreatic Endocrinogenesis | 3,696 | Mouse E14.5-E15.5 | Terminal states |
| Human Hematopoiesis | 1,947 | HSPC differentiation | 5 lineages |
| Zebrafish Neural Crest | 1,180 | Smart-seq3 | CRISPR validation |

#### Key Performance Metrics

1. **Cross-Boundary Correctness (CBC)**: RegVelo: 0.864
2. **Velocity Consistency**: 0.873
3. **Latent Time Correlation**: Spearman r=0.683 with FUCCI scores
4. **Terminal State Identification (TSI)**: Outperformed scVelo, veloVI across all datasets
5. **GRN Validation**: AUROC=0.95 for lineage driver prediction in hematopoiesis

#### TSI Metric Definition
$$\text{TSI} = \frac{\text{Area under } f_\kappa}{\text{Area under } f_{\text{opt}}}$$

Where:
- $f_\kappa(j)$: Number of correctly predicted terminals with $j$ macrostates
- $f_{\text{opt}}(j) = \min(j, m)$: Optimal recovery function

#### Experimental Validation

- 14 single-TF + 8 multiple-TF CRISPR/Cas9 knockouts in zebrafish
- Single-cell Perturb-seq validation
- 2-fold improvement over competing methods (Spearman r=0.35 vs <0.17)

---

### Implementation Verification

#### Code-Paper Equation Mapping

| Paper Element | Code Location | Fidelity |
|--------------|---------------|----------|
| Eq. 1: $du/dt = \alpha - \beta u$ | `_module.py:312` | Exact |
| Eq. 2: $ds/dt = \beta u - \gamma s$ | `_module.py:313` | Exact |
| GRN transcription: $\alpha = h(Ws + b)$ | `_module.py:238-267` | Exact |
| Softplus $h(x) = \log(1+e^x)$ | `_module.py:258-259` | Exact (clamped [0,50]) |
| Hard GRN constraint | `_module.py:569-571` | Exact (gradient hook) |
| Soft GRN constraint (Eq. 3) | `_module.py:889-893` | Exact |
| Jacobian regularization (Eq. 6) | `_module.py:170-203, 896-898` | Exact |
| Velocity regularization (Eq. 7) | `_module.py:880-886` | Exact (100x scaling) |
| Base regularization (Eq. 8) | `_module.py:901-904` | Exact |
| ODE solver (Dopri5) | `_module.py:1038-1044` | Partial* |
| In silico perturbation | `tools/_in_silico_block_simulation.py:47-57` | Exact |
| TSI metric | `metrics/_tsi.py:93-141` | Exact |

*Note: Code uses `FixedStepController()` by default, not adaptive `IntegralController`.

#### Verified Hidden Implementation Details

1. **Kinetic parameter clamping**: All rates clamped to [0, 50] for numerical stability
2. **GRN weight initialization**: Zero matrix (not Xavier uniform as stated for NN weights)
3. **Base transcription regularization**: Penalizes $\|b + 10\|_2$ (not $\|b\|$)
4. **Alpha-unspliced correlation loss**: Additional undocumented term encouraging lag correlation
5. **Min-max scaling**: Applied to both Ms and Mu layers before training
6. **Velocity loss scaling**: Multiplied by 100 (arbitrary scaling factor)

---

### Discrepancies and Limitations

#### Minor Discrepancies

1. **ODE Step Controller**: Paper mentions "parallelized numerical integration solver dopri5" suggesting adaptive stepping; code uses `FixedStepController()` by default
2. **Weight Initialization**: Paper states "xavier_uniform_" for neural networks but GRN weights initialized as zeros
3. **Alpha Correlation Loss**: Additional loss term (`alpha_constraint * pearson_correlation_loss`) not explicitly described in paper
4. **Device Hardcoding**: `inferred_grn()` hardcodes `cuda:0` device - will fail on CPU-only systems

#### Known Limitations

1. **Single-time GRN assumption**: Assumes constant $W$ across development (biological simplification)
2. **Induction-only dynamics**: No explicit repression phase modeling (unlike scVelo)
3. **Prior GRN dependency**: Performance degrades significantly with >80% GRN corruption
4. **Memory scaling**: Quadratic in gene number due to full GRN matrix
5. **Additive regulation**: TFs contribute additively to transcription rate

---

### Model Assumptions

1. **Constant GRN**: Weight matrix $W$ is time-independent
2. **Initial conditions**: $u(t_0) = s(t_0) = 0$ at $t_0 = 0$
3. **Time scale**: All genes on same scale with $t_{\text{max}} = 20$
4. **Additive regulation**: TFs contribute additively to transcription rate
5. **Positive transcription**: Softplus ensures $\alpha > 0$
6. **Sparse regulation**: Real biological GRNs have ~1-5% connectivity

---

### Key Biological Insights Enabled

1. **Toggle-switch circuits**: e.g., GATA1/SPI1 competition in hematopoiesis
2. **Regulatory cascades**: e.g., tfec -> mitfa in pigment specification
3. **Driver gene discovery**: Identify novel regulators like elf1 in neural crest
4. **Cell fate prediction**: Quantify perturbation effects before experiments

---

### Requirements for Reproduction

- Python 3.9+
- PyTorch 2.0+
- scvi-tools >= 1.0.0
- torchode >= 0.1.6
- cellrank >= 2.0.0
- CUDA-enabled GPU recommended
- Prior GRN from ChIP-seq, multiome, or database sources (SCENIC+, Pando, ChIP-Atlas)

---

### Comparison with Related Methods

| Feature | scVelo | veloVI | RegVelo |
|---------|--------|--------|---------|
| Transcription model | Constant $\alpha$ | Constant $\alpha$ | GRN-dependent $\alpha(s)$ |
| Gene coupling | Independent | Independent | Coupled via $W$ |
| Prior knowledge | None | None | GRN prior |
| Perturbation prediction | No | No | Yes |
| Uncertainty | No | Yes | Yes |
| ODE solver | Analytical | Analytical | Numerical (Dopri5) |
| Cell fate analysis | Via CellRank | Via CellRank | Integrated |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
