---
layout: default
permalink: /paper-atlas/cellflow-eca5e2a3/
title: "CellFlow"
nav: false
description: "CellFlow 学习一个由实验条件控制的连续向量场，把对照细胞分布运输成扰动后的细胞分布。它的主要任务是未见条件下的单细胞表型生成；论文也展示发育时间插值和命运工程，但不能因此把模型输出理解为由谱系追踪直接验证的真实细胞轨迹。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>CellFlow</h1>
    <p>CellFlow enables generative single-cell phenotype modeling with flow matching</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1101/2025.04.11.648220" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CellFlow">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/theislab/cellflow" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellFlow">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellFlow 方法解读：把对照细胞群推送到条件特异的扰动表型

### 一句话定位

CellFlow 学习一个由实验条件控制的连续向量场，把对照细胞分布运输成扰动后的细胞分布。它的主要任务是**未见条件下的单细胞表型生成**；论文也展示发育时间插值和命运工程，但不能因此把模型输出理解为由谱系追踪直接验证的真实细胞轨迹。

### 输入和输出

输入由四部分组成：对照细胞的低维表示、扰动标识（药物、基因敲除、细胞因子等）、与扰动绑定的剂量或时间，以及供模型区分供体、细胞系或批次的样本协变量。扰动还可用分子指纹或 ESM2 等外部表示编码。输出是给定条件下生成的一群细胞表示；若训练在 PCA/VAE 空间，结果也首先位于该表示空间，而不是原始计数空间。

### 方法主线

#### 1. 把可变长度条件变成一个向量

组合处理没有固定顺序，因此 CellFlow 先分别处理扰动及其协变量，再用均值（DeepSets 思路）或 attention token/seed 做置换不变聚合，最后得到条件表示 $\mathcal A_\theta(\mathbf c)$。源码 `src/cellflow/networks/_set_encoders.py:20-196` 实现确定性或随机条件编码、mask、均值和两种注意力池化；`DataManager` 则负责把 AnnData 中的控制标签、组合处理和样本协变量整理成相应张量。

#### 2. 用最优传输构造训练配对

实验并没有同一细胞处理前后的成对观测。CellFlow 在每个条件内用最优传输把对照批次与扰动批次进行软配对，使训练路径偏向较短、较合理的群体运输。`src/cellflow/solvers/_otfm.py:135-146` 计算匹配矩阵并从联合耦合中重采样源、目标细胞。这里的“配对”是模型假设，不是实验谱系对应。

#### 3. 学习条件流

对源细胞 $\mathbf x$、目标细胞 $\mathbf y$ 和随机时间 $t$，概率路径产生中间点 $\mathbf x_t$ 及其目标速度 $\mathbf u_t$。网络学习

$$
\mathcal L_{\mathrm{FM}}=\mathbb E\left[\left\|v_\theta(t,\mathbf x_t\mid\mathcal A_\theta(\mathbf c))-\mathbf u_t\right\|_2^2\right].
$$

源码 `src/cellflow/solvers/_otfm.py:79-108` 直接计算中间点、目标速度和均方误差，并在随机条件编码时加入正则项。`src/cellflow/model/_cellflow.py:247-513` 组装条件编码器、向量场、概率路径和求解器。

#### 4. 推断为 ODE 积分

预测时固定条件，从 $t=0$ 的控制细胞出发积分到 $t=1$。`src/cellflow/solvers/_otfm.py:189-221` 使用 Diffrax/Tsit5 求解。每个输入细胞因此得到一个生成终点，但这是学习运输映射下的对应，不能自动解释为可观测的生物学迁移路线。

### 六张主图怎么读

- **图 1**：总架构。上半部分定义表型筛选任务，下半部分连接条件聚合、OT 配对、flow-matching 训练与 ODE 生成。
- **图 2**：近一千万 PBMC 的细胞因子实验。只要训练中见过该细胞因子在至少一个供体上的反应，预测明显改善；它也显示外部嵌入本身不足以恢复完全未见刺激的功能效应。
- **图 3**：斑马鱼敲除与发育阶段。模型预测全胚细胞分布和细胞类型比例，并展示时间插值；这是条件生成能力的证据，不是谱系追踪证据。
- **图 5**：组合 morphogen 的 iNeuron 命运工程。CellFlow 较好恢复异质细胞组成、协方差和部分新群体，同时论文也报告某些组合的浓度依赖误差。
- **图 6**：三套脑类器官筛选联合训练，并虚拟生成约 2.3 万个协议、超过七千万个细胞。该结果是 proof-of-principle 的计算筛选，不等同于所有协议都经湿实验验证。

### 论文与当前代码快照的对应

核心 API、数据管理、条件聚合、OT flow matching、GENOT 备选求解器、训练回调、预测和测试均在本地。`docs/notebooks/` 提供五个教程 notebook。当前快照未记录固定 Git commit；论文还单独指向 `cellflow_reproducibility` 仓库，因此本地软件包和教程并不包含产生论文全部图表的完整脚本与所有大型数据。这里验证的是机制和接口对得上，不是论文全部数值已重跑。

### 使用时最重要的边界

1. 预测质量依赖训练条件覆盖；图 2 明确显示完全未见细胞因子时优势有限。
2. OT 的最短运输是假设，生成路径不应直接作因果或谱系解释。
3. 外推到高阶组合、极端剂量或训练分布很远的协议，应以实验验证收尾。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellFlow enables generative single-cell phenotype modeling with flow matching

### Reproducibility Rating: 3/5

**Strengths**: The local JAX codebase includes the main API, solvers, documentation notebooks and automated tests; the PDF, converted Markdown and figures are local.

**Gaps**: The snapshot has no fixed Git commit, and the paper points to a separate `cellflow_reproducibility` repository for figure-generating analyses. Large datasets and the full end-to-end benchmark environment were not acquired or rerun; some organoid data were author-provided at preprint time.

**Evidence status**: Method and API claims below were checked against the local paper and `src/cellflow/`. Benchmark numbers are paper-reported rather than locally reproduced.

---

### Executive Summary

CellFlow is a generative framework for modeling single-cell phenotypes induced by complex perturbations using flow matching and optimal transport. The method learns conditional vector fields that map unperturbed (source) cellular distributions to perturbed (target) distributions, enabling prediction of transcriptomic responses to unseen perturbation conditions.

> "CellFlow, a flexible framework for modeling single-cell phenotypes induced by diverse internal or external cues. CellFlow leverages flow matching, a generative modeling technique that has been used to generate high-quality samples in computer vision, video, and molecular design, in part through modeling complex distributions." (Paper, Introduction p.1-2)

**Core Innovation**: CellFlow extends flow matching to handle arbitrary combinations of perturbations through a set-aggregation encoder architecture that processes variable-length perturbation sets in a permutation-invariant manner using attention mechanisms or deep sets.

> "To model multiple interventions at the same time, it is necessary to encode combinations of treatments in a permutation-invariant manner. Therefore, CellFlow implements two set aggregation schemes, multi-head attention and deep sets, followed by an encoder consisting of a feed-forward network." (Paper, Results p.2)

**Key Results** (from paper):
- Achieves R-squared > 0.76 for cytokine response prediction when cytokine is seen for at least one donor (vs 0.60 baseline)
- 2x improvement in energy distance for zebrafish developmental perturbation modeling (Fig. 3B)
- Outperforms chemCPA, biolord, CondOT, GEARS, and scGPT on established benchmarks
- Successfully predicts novel drug combinations with 66% error reduction over additive models (Fig. 4G)
- Scaling law: $\log(\text{Error}) \sim -0.22 \cdot \log(\text{n\_conditions})$ with $R^2 = 0.999$ (Fig. 2G)

---

### Biological Motivation

#### The Challenge

High-throughput perturbation screens (drug treatments, gene knockouts, morphogen manipulations) generate massive single-cell datasets, but:
1. **Combinatorial explosion**: Testing all perturbation combinations is experimentally infeasible
2. **Context dependency**: Cellular responses vary by donor, cell type, developmental stage
3. **Distributional heterogeneity**: Perturbations create complex cell state distributions, not simple mean shifts

> "However, the complexity of biological systems and combinatorial space of potential perturbations makes comprehensive experimental characterization infeasible. Computational models can help systematically explore the phenotypic space by learning from existing perturbation data and extrapolating to uncharacterized experimental conditions." (Paper, Introduction p.1)

#### CellFlow's Solution

The method models perturbation effects as continuous flows in gene expression space, preserving population-level distributional properties while enabling single-cell resolution predictions.

> "We use optimal transport to pair unperturbed and perturbed cells, enabling the distinction between inherent cellular heterogeneity and perturbation-induced distributional changes. To represent arbitrary types of perturbations and enable predictions for conditions out-of-distribution, CellFlow incorporates powerful pre-trained embeddings of biological entities." (Paper, Introduction p.2)

---

### Method Architecture

#### Three-Component Framework

```
Perturbation Variables ──┐
                        ├──> Condition Encoder ──> Condition Embedding
Sample Covariates ──────┘            │
                                     ▼
Control Cells ──────────────> Flow Matching ──────> Perturbed Cells
                              (Neural ODE)
```

#### 1. Condition Encoding (Paper Methods Section 1.1-1.2; `_set_encoders.py:20-234`)

**Input Variables** (Paper Methods Section 1.1):
- **Perturbations** $\{p_i\}_{i \in \mathcal{I}_p}$: Drug treatments, gene knockouts, cytokines
- **Perturbation covariates** $\{q_i\}_{i \in \mathcal{I}_q}$: Dosages, timing
- **Sample covariates** $s$: Donor, cell type, batch

> "We formulated a generic setup of phenotypic screens. We partition the set of variables defining a perturbation experiment into three groups, namely perturbations $\{p_i\}_{i\in\mathcal{I}_p}$, perturbation covariates $\{q_i\}_{i\in\mathcal{I}_q}$, and sample covariates $\{s_i\}_{i\in\mathcal{I}_s}$." (Paper Methods, Section 1.1)

**Set Aggregation** (Paper Methods Section 1.2):
$$\mathcal{A}_\theta(\mathbf{c}) = \text{MLP}\left(\text{Pool}\left(f(\{p_1, q_1\}, \ldots, \{p_n, q_n\})\right) \oplus g(s)\right)$$

Where Pool is either:
- **Mean pooling** (Deep Sets): $\frac{1}{n}\sum_j f(\{p_j, q_j\})$
- **Attention pooling**: $\sum_j \alpha_j f(\{p_j, q_j\})$ with learned attention weights

> "CellFlow processes the representations of perturbations, perturbation covariates, and sample covariates using modules consisting of feed-forward neural networks or self-attention layers. To obtain a single representation of all cell's covariates, all of the treatments that make up a single condition are aggregated using a permutation invariant pooling operation." (Paper Methods, Section 1.2)

**Code Reference** (`_set_encoders.py:91-96`):
```python
if self.pooling == "mean":
    self.pool_module = lambda x, mask, training: jnp.mean(x * mask, axis=-2)
elif self.pooling == "attention_token":
    self.pool_module = nn_utils.TokenAttentionPooling(**self.pooling_kwargs)
```

#### 2. Flow Matching Loss (Paper Methods Section 1.4-1.5; `_otfm.py:79-108`)

**Core Objective** (Eq. 12 in paper, Methods Section 1.5):
$$\mathcal{L}_{\text{CellFlow}}(\theta) = \mathbb{E}_{t, \mathbf{c} \sim \rho, (\mathbf{x}, \mathbf{y}) \sim \pi_{\mathbf{c}}, Z_t \sim p_t(\cdot | \mathbf{x}, \mathbf{y}, \mathbf{c})} \Big[ \| v_{t, \theta}(\mathbf{z}_t \mid \mathcal{A}_{\theta}(\mathbf{c})) - u_t(\mathbf{z}_t \mid \mathbf{x}, \mathbf{y}) \|_2^2 \Big]$$

> "Flow matching is a simulation-free way of training neural vector fields, enabling fast and stable optimization. It constructs a probability path $p_t$ that transitions from $p_0 \approx \mu$ to $p_1 \approx \nu$ by marginalizing individually constructed conditional paths $p_t(\cdot \mid \mathbf{x}, \mathbf{y})$ for data samples $\mathbf{x}$ from $\mu$ and $\mathbf{y}$ from $\nu$." (Paper Methods, Section 1.4)

**Code Implementation** (`_otfm.py:87-108`):
```python
x_t = self.probability_path.compute_xt(rng_flow, t, source, target)
v_t, mean_cond, logvar_cond = vf_state.apply_fn(...)  # Neural network prediction
u_t = self.probability_path.compute_ut(t, x_t, source, target)  # True velocity
flow_matching_loss = jnp.mean((v_t - u_t) ** 2)
```

#### 3. Optimal Transport Pairing (Paper Methods Section 1.3; `utils.py:14-66`)

> "Pairing samples from the source and the target distribution with OT has proved to improve the generative performance of flow matching models as it straightens paths between source and target populations. Given the complexity and heterogeneity of cellular distributions, mapping control cells to distributionally close perturbed cells is thus a promising direction to improve the generative capabilities of CellFlow." (Paper Methods, Section 1.3)

**Entropic OT** (Eq. EKP in paper):
$$\min_{\pi \in \Pi(\mu,\nu)} \iint \|\mathbf{x} - \mathbf{y}\|^2 d\pi(\mathbf{x}, \mathbf{y}) + \varepsilon \text{KL}(\pi \mid \mu \otimes \nu)$$

**Unbalanced Extension** (Eq. EUKP):
$$+ \lambda_1 \text{KL}(p_1\sharp\pi \mid \mu) + \lambda_2 \text{KL}(p_2\sharp\pi \mid \nu)$$

> "The Kantorovich formulation enforces mass conservation. For instance, this means that every unperturbed cell must be mapped. As a result, factors like apoptosis or asynchronous proliferation cannot be modeled. Unbalanced optimal transport (UOT) lifts this constraint by penalizing the deviation of $p_1\sharp\pi$ from $\mu$ and $p_2\sharp\pi$ from $\nu$." (Paper Methods, Section 1.3)

**Code Reference** (`utils.py:54-66`):
```python
geom = pointcloud.PointCloud(source_batch, target_batch, cost_fn=cost_fn,
                             epsilon=epsilon, scale_cost=scale_cost)
problem = linear_problem.LinearProblem(geom, tau_a=tau_a, tau_b=tau_b)
solver = sinkhorn.Sinkhorn(threshold=threshold, **kwargs)
out = solver(problem)
return out.matrix
```

---

### Velocity Field Architecture (Paper Section 1.6; `_velocity_field.py:19-300`)

#### Network Structure

```
Time t ──> Sinusoidal Encoding ──> Time MLP ──────┐
                                                  │
Cell x_t ──────────────────────> Cell MLP ────────┼──> Concatenation ──> Decoder MLP ──> v_θ
                                                  │
Condition c ──> Condition Encoder ──> Dropout ────┘
```

**Sinusoidal Time Encoding** (`_utils.py:24-55`):
$$\text{Enc}(t) = [\cos(2\pi f_1 t), \sin(2\pi f_1 t), \ldots, \cos(2\pi f_K t), \sin(2\pi f_K t)]$$

**Default Architecture** (Paper Section 1.6):
- `time_encoder_dims`: (2048, 2048, 2048)
- `hidden_dims`: (4096, 4096, 4096)
- `decoder_dims`: (4096, 4096, 4096)
- `condition_embedding_dim`: 256
- `cond_output_dropout`: 0.9

---

### Probability Paths (Paper Section 1.4)

#### Constant Noise Path
$$p_t(\mathbf{z} \mid \mathbf{x}, \mathbf{y}) = \mathcal{N}((1-t)\mathbf{x} + t\mathbf{y}, \sigma^2)$$
$$u_t(\mathbf{z} \mid \mathbf{x}, \mathbf{y}) = \mathbf{y} - \mathbf{x}$$

#### Brownian Bridge Path
$$\sigma_t(\mathbf{x}, \mathbf{y}) = \sigma\sqrt{t(1-t)}$$
$$u_t(\mathbf{z} \mid \mathbf{x}, \mathbf{y}) = \frac{1-2t}{t(1-t)}(\mathbf{z} - ((1-t)\mathbf{x} + t\mathbf{y})) + (\mathbf{y} - \mathbf{x})$$

**Implementation**: Uses `ott.neural.methods.flows.dynamics` for probability path computations.

---

### Evaluation Metrics (Paper Section 2; `_metrics.py`)

#### R-Squared on DEGs (`_metrics.py:25-39`)
$$R^2(\hat{\mu}_n, \hat{\nu}_n) = 1 - \frac{\sum_{j=1}^d (\tilde{\mathbf{y}}_j - \tilde{\mathbf{x}}_j)^2}{\sum_{j=1}^d (\tilde{\mathbf{x}}_j - \bar{\tilde{\mathbf{x}}})^2}$$

#### Energy Distance (`_metrics.py:70-87`)
$$\text{ED}^2(\mu, \nu) = 2\mathbb{E}_{X \sim \mu, Y \sim \nu}[\|X - Y\|] - \mathbb{E}_{X, X' \sim \mu}[\|X - X'\|] - \mathbb{E}_{Y, Y' \sim \nu}[\|Y - Y'\|]$$

#### Maximum Mean Discrepancy (`_metrics.py:179-201`)
$$\text{MMD}^2(\mu, \nu) = \mathbb{E}[k(X, X')] + \mathbb{E}[k(Y, Y')] - 2\mathbb{E}[k(X, Y)]$$

With RBF kernel $k_{\gamma}(\mathbf{x}, \mathbf{y}) = \exp(-\gamma\|\mathbf{x} - \mathbf{y}\|^2)$ averaged over $\gamma \in \{2, 1, 0.5, 0.1, 0.01, 0.005\}$.

#### Sinkhorn Divergence (`_metrics.py:42-67`)
$$S_{2,\varepsilon}^2(\mu, \nu) = W_{2,\varepsilon}^2(\mu, \nu) - \frac{1}{2}W_{2,\varepsilon}^2(\mu, \mu) - \frac{1}{2}W_{2,\varepsilon}^2(\nu, \nu)$$

---

### Key Experimental Results

#### PBMC Cytokine Screen (10M cells, 12 donors, 90 cytokines)

| Condition | CellFlow R² (DEGs) | Best Baseline |
|-----------|-------------------|---------------|
| 0 donors seen | 0.60 | 0.60 (identity) |
| 1 donor seen | **0.76** | 0.60 |
| 11 donors seen | **0.89** | 0.70 |

**Scaling Law** (Paper Fig. 2G): Performance follows $\log(\text{Error}) \sim -0.22 \cdot \log(\text{n\_conditions})$ with $R^2 = 0.999$.

#### Zebrafish Development (ZSCAPE Dataset)

| Metric | CellFlow | Best Baseline | Improvement |
|--------|----------|---------------|-------------|
| Energy Distance | **0.45** | 0.90 | 2x |
| Cell Type Accuracy | **0.89** | 0.85 | 5% |

#### Drug Combination (ComboSciPlex)

CellFlow reduced prediction error by **66%** compared to expression-space additive models on held-out drug combinations.

---

### Discrepancies and Limitations

#### Paper vs Code Gaps

1. **Hyperparameter Tables**: Paper references "Supplementary Tables 1-10" for hyperparameters, but these require reconstruction from reproducibility repository
2. **ESM2 Embeddings**: Paper mentions ESM2 for cytokine/protein representations; code provides interface but pre-computed embeddings must be generated
3. **Organoid Datasets**: Two of three organoid datasets (Sanchis-Calleja, Azbukina) were unpublished at paper submission

#### Known Limitations (from Discussion)

> "The effectiveness of predicting responses to entirely unseen perturbations strongly depends on the quality of condition embeddings and their ability to capture functional properties. While we leveraged existing embeddings like ESM2 for proteins and molecular fingerprints for small molecules, these representations may not optimally encode the functional roles relevant to cellular responses." (Paper, Discussion p.12-13)

- Out-of-distribution prediction for completely novel perturbations remains challenging
- ESM2/molecular fingerprints may not capture all relevant functional information
- Model tends to underestimate extreme perturbation effects (conservative predictions)

> "However, strong effects were often underestimated. This overly conservative behavior may in part be due to the variability of individual mutants and the high variability of the one-nearest neighbor classifier used for cell type annotation transfer." (Paper, Results p.5)

---

### Code-Paper Equation Mapping

| Paper Equation | Description | Code Location |
|----------------|-------------|---------------|
| Eq. (MP) | Monge OT problem | Theoretical background |
| Eq. (KP) | Kantorovich formulation | `utils.py:56-66` |
| Eq. (EKP) | Entropic regularization | `utils.py:56-66` (epsilon parameter) |
| Eq. (UKP) | Unbalanced OT | `utils.py:62-63` (tau_a, tau_b) |
| Eq. (9) | CFM loss | `_otfm.py:99` |
| Eq. (10) | OT-CFM loss | `_otfm.py:143-146` |
| Eq. (11) | UOT-CFM loss | `_otfm.py:143-146` with tau params |
| Eq. (12) | CellFlow loss | `_otfm.py:79-108` |
| Algorithm 1 | Sinkhorn | `ott.solvers.linear.sinkhorn` |
| Algorithm 2 | CellFlow training | `_trainer.py:82-157` |

---

### Quick Start

```python
import cellflow as cf
import anndata as ad

# Load data
adata = ad.read_h5ad("perturbation_data.h5ad")

# Initialize model
model = cf.CellFlow(adata, solver="otfm")

# Prepare data
model.prepare_data(
    sample_rep="X_pca",
    control_key="is_control",
    perturbation_covariates={"drug": ("drug_name",)},
    perturbation_covariate_reps={"drug": "drug_embeddings"},
    sample_covariates=["cell_type"],
)

# Configure and train
model.prepare_model(condition_embedding_dim=256)
model.train(num_iterations=100000, batch_size=1024)

# Predict
predictions = model.predict(control_adata, conditions={"drug": "DrugX"})
```

---

### References

- Klein, Fleck et al. "CellFlow enables generative single-cell phenotype modeling with flow matching." Nature Methods (2025, in review)
- Code: https://github.com/theislab/CellFlow
- Documentation: https://cellflow.readthedocs.io/

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
