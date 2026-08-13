---
layout: default
permalink: /paper-atlas/spacia-e6076d31/
title: "Spacia"
nav: false
wide: true
description: "Spacia 把每个接收细胞看成一个“袋子（bag）”，把它周围的多个候选发送细胞看成袋子里的“实例（instance）”，再用贝叶斯多实例学习同时回答两个问题： 哪些邻近细胞真正可能影响这个接收细胞？ 这些发送细胞中的哪些基因或通路，与接收细胞的表达变化相关？ 论文发表于 Nature Methods（2024），DOI：10.1038/s41592-024-02408-1。"
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
      <span>Cell-Cell Communication</span>
      <span>Nature Methods · 2024</span>
    </div>
    <h1>Spacia</h1>
    <p>Mapping cellular interactions from spatially resolved transcriptomics data</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/yunguan-wang/Spacia" target="_blank" rel="noopener noreferrer" aria-label="Open code for Spacia">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Spacia 方法详解：从空间转录组推断细胞间相互作用

### 一句话理解

Spacia 把每个接收细胞看成一个“袋子（bag）”，把它周围的多个候选发送细胞看成袋子里的“实例（instance）”，再用贝叶斯多实例学习同时回答两个问题：

1. 哪些邻近细胞真正可能影响这个接收细胞？
2. 这些发送细胞中的哪些基因或通路，与接收细胞的表达变化相关？

论文发表于 *Nature Methods*（2024），DOI：`10.1038/s41592-024-02408-1`。

### 1. 它想解决什么问题？

细胞间通讯（cell–cell communication, CCC）常通过配体—受体关系分析。CellChat（*Nature Communications*, 2021）、NicheNet（*Nature Methods*, 2020）和 CellPhoneDB（*Nature Protocols*, 2020）等方法推动了这一方向，但通常存在几个限制：

- 往往先把单细胞聚合到细胞类型层面，无法指出具体是哪两个细胞在相互作用；
- 依赖已有的配体—受体或信号通路数据库，难以发现数据库之外的关系；
- 常以配体和受体的共表达作为证据，但真正发生变化的可能是受体下游基因，而不是受体基因本身；
- scRNA-seq 没有空间坐标，难以排除在组织中相距很远、实际上不可能直接通讯的细胞。

SpaTalk（*Nature Communications*, 2022）、COMMOT（*Nature Methods*, 2023）和 SpatialDM（*Nature Communications*, 2023）等空间方法利用了位置信息，但论文认为，已有方法仍没有充分统一处理“多个发送细胞共同作用于一个接收细胞”的数据结构，同时输出明确的单细胞配对和发送基因—接收基因效应。

单细胞分辨率空间转录组恰好提供了 Spacia 所需要的信息：每个细胞的表达、位置、细胞类型，以及一个接收细胞周围的多个候选发送细胞。

### 2. 最关键的建模视角

设第 $i$ 个接收细胞为袋子 $B_i$，它附近有 $m_i$ 个候选发送细胞。每个发送细胞 $j$ 都有两类特征：

- 表达特征 $\mathbf{x}^{e}_{ij}$：发送基因、通路或主成分；
- 距离特征 $\mathbf{x}^{d}_{ij}=(1,d_{ij})^\top$：截距和发送—接收距离。

接收细胞的某个基因或通路表达被二值化为 $y_i\in\{0,1\}$。此外，引入隐变量

$$
\delta_{ij}\in\{0,1\},
$$

其中 $\delta_{ij}=1$ 表示发送细胞 $j$ 是接收细胞 $i$ 的“主要实例（primary instance）”，即它被模型认为真正参与了该接收状态的形成。

这种表示可以自然处理：

- 多个发送细胞作用于一个接收细胞；
- 同一个发送细胞同时出现在多个接收细胞的袋子中，因此也能表达一对多关系。

### 3. 两层嵌套的 Probit 模型

#### 3.1 第一层：距离决定谁更可能是主要发送细胞

Spacia 用一个 Probit 模型描述 $\delta_{ij}$：

$$
\delta_{ij}=\operatorname{sign}(U_{ij}),
$$

$$
U_{ij}=(\mathbf{x}^{d}_{ij})^\top\mathbf b+e_{ij},
\qquad e_{ij}\sim\mathcal N(0,1).
$$

因此

$$
\Pr(\delta_{ij}=1\mid \mathbf{x}^{d}_{ij},\mathbf b)
=\Phi\left((\mathbf{x}^{d}_{ij})^\top\mathbf b\right).
$$

$\mathbf b=(b_0,b_1)^\top$ 中的 $b_1$ 表示距离效应。如果 $b_1<0$，距离越近，发送细胞越可能被判定为主要实例。这也是论文在很多结果中要求 $b<0$ 的原因。

但代码中的 $\delta$ 更新并不是只看距离。它还比较“加入这个发送细胞”与“不加入这个发送细胞”时，接收细胞表达状态被解释得有多好。也就是说，空间接近只是先验倾向，发送表达与接收状态的一致性也参与判断。

#### 3.2 第二层：主要发送细胞的表达解释接收状态

接收细胞的潜在响应为

$$
Z_i=\sum_{j=1}^{m_i}\delta_{ij}(\mathbf{x}^{e}_{ij})^\top\boldsymbol\beta+\epsilon_i,
\qquad \epsilon_i\sim\mathcal N(0,1),
$$

$$
y_i=\operatorname{sign}(Z_i).
$$

等价地，

$$
\Pr(y_i=1\mid X_i^e,\boldsymbol\beta,\boldsymbol\delta_i)
=\Phi\left(\sum_{j=1}^{m_i}\delta_{ij}(\mathbf{x}^{e}_{ij})^\top\boldsymbol\beta\right).
$$

只有 $\delta_{ij}=1$ 的发送细胞会进入求和。$\beta_r$ 描述第 $r$ 个发送基因或通路与接收表达状态之间的条件关联：

- $\beta_r>0$：发送特征升高与接收状态升高相关；
- $\beta_r<0$：发送特征升高与接收状态降低相关。

这使 Spacia 不必局限于“配体—受体”。只要 SRT 测到了相关基因，就可以研究任意发送特征与任意接收特征之间的关系。

#### 3.3 先验与后验推断

论文默认使用零均值、对角单位协方差的高斯先验：

$$
\boldsymbol\beta\sim\mathcal N(\mathbf 0,I),
\qquad
\mathbf b\sim\mathcal N(\mathbf 0,I).
$$

所有参数与隐变量记为

$$
\Theta=(\boldsymbol\beta,\mathbf b,\Delta,Z,U).
$$

Spacia 用 MCMC 从后验分布 $p(\Theta\mid X,y)$ 抽样。代码采用 Gibbs 更新，并把最密集的条件更新放在 Rcpp/C++ 中。

### 4. 从输入到输出的完整流程

```text
单细胞表达矩阵 + X/Y 坐标 + 细胞类型
                    │
                    ▼
        指定发送细胞类型和接收细胞类型
                    │
                    ▼
      为每个接收细胞构建邻域和候选发送袋子
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
   构造发送表达特征        构造接收表达特征
 基因/基因集/聚类/PCA      基因或通路聚合
         │                     │
         │                     ▼
         │            阈值化为二值接收标签
         └──────────┬──────────┘
                    ▼
         每个接收特征建立一个独立 MCMC 任务
                    │
                    ▼
      推断 beta、b、delta/PIP、FDR 和诊断量
                    │
                    ▼
    基因/通路相互作用表 + 发送—接收细胞配对表
```

#### 步骤 1：选择分析方向

用户需要明确谁是发送细胞、谁是接收细胞。同一种细胞可以在不同运行中扮演不同角色。方向性不是模型自动发现的，而是由分析设计给定。

#### 步骤 2：建立空间邻域和袋子

用户可以直接给距离阈值，也可以指定期望邻居数，让程序估计邻域半径。程序会：

1. 找到每个接收细胞附近的候选发送细胞；
2. 删除发送实例过少的袋子；
3. 在袋子过多时进行子采样。

初始距离阈值可以较宽松，因为模型随后用 $b$ 和 $\delta$ 学习哪些距离范围真正有信息。

#### 步骤 3：处理发送/接收表达特征

Spacia 支持五种策略：

| 模式 | 做法 | 适合场景 | 风险 |
|---|---|---|---|
| 不聚合 | 每个基因单独建模 | 已有明确候选基因、数据质量较好 | 稀疏、噪声和共线性 |
| 知识驱动 | 用户定义通路/基因集 | 有明确先验知识 | 受基因集定义影响 |
| 相关性驱动 | 用相关基因增强种子基因 | 想平滑单基因信号 | 可能偏离原始基因含义 |
| 聚类驱动 | 层次聚类形成表达模块 | 探索性通路分析 | 难以回到单基因解释 |
| PCA 驱动 | 用前几个主成分建模，再按载荷回映射 | 数百基因、探索性分析 | 回映射增加一层解释 |

论文中的 MERSCOPE 500 基因面板主要采用 PCA 模式；Xenium 的针对性验证采用不聚合模式；CosMx 使用知识驱动聚合。

#### 步骤 4：把接收表达变成二值标签

默认可使用分位数阈值。自动模式会拟合两个高斯成分：如果分布明显双峰，使用两个均值的中点；如果不够双峰，则使用较低均值加一个标准差，并对极端不平衡情况退回中位数。

这是一个重要敏感点：接收表达本来是连续值，二值化后，阈值会改变哪些细胞被标成高表达，因此也可能影响最终推断。

#### 步骤 5：运行 MCMC

Python 端准备数据后，为每个接收基因/通路生成一个独立 R 任务。默认 Python 参数是：

- 总迭代数：50,000；
- 预热：25,000；
- thinning：10；
- 链数：3。

每次 Gibbs 迭代的核心顺序是：

1. 根据当前 $\delta$ 汇总主要发送细胞的表达；
2. 更新接收层潜变量 $Z$；
3. 更新 $\boldsymbol\beta$；
4. 综合距离和接收表达似然更新每个 $\delta_{ij}$；
5. 更新距离层潜变量 $U$；
6. 更新 $\mathbf b$。

Figure 1 显示，MCMC 太短时细胞配对识别很差，达到约 10,000 次及以上后 ROC AUC 超过 0.95。这说明链长不是纯粹的工程参数，而是直接影响结果质量。

#### 步骤 6：汇总结果

主要输出包括：

- `Pathway_betas.csv`：发送特征—接收特征的 $\beta$；
- `Interactions.csv`：具体发送细胞—接收细胞的主要实例分数；
- `B_and_FDR.csv`：距离系数 $b$、Bayes FDR 和派生显著性。

代码还计算 MCMC 中的主要实例频率，以及一个只基于平均 $b$ 和距离重新计算的 `pip_recal`。源码明确提醒：`pip_recal` 更适合作为排序分数，不能当作校准后的概率。

### 5. 论文怎样验证 Spacia？

#### 模拟数据

- MCMC 足够长时，正确细胞配对的 ROC AUC > 0.95；
- 主要实例与非主要实例的分数明显分离；
- 真正相互作用的 $\beta$ 能被恢复，噪声基因的 $\beta$ 接近零；
- 扩展图中的轨迹和自相关支持所展示链的稳定性。

#### 与其他 CCC 方法比较

在前列腺癌 MERSCOPE 数据中：

- Spacia 的细胞配对边主要是局部短距离连接；
- CellPhoneDB 和 CellChat 的可视化出现大量跨组织长距离边；
- Spacia 推断的相互作用中，92.7% 只出现在一个或两个发送细胞类型中；
- 其他方法有更多相互作用在多个发送细胞类型间广泛共享，COMMOT 在该分析中报告的相互作用全部共享于九种发送细胞类型。

这些结果支持“更具空间局部性和细胞类型特异性”的主张，但不同软件的输出对象和过滤规则并不相同，因此不能只凭边更少或更局部就断言绝对准确。

#### 生物学应用

论文进一步把 Spacia 用于：

- 肿瘤微环境诱导 EMT 和谱系可塑性；
- 肿瘤 PD-L1 对免疫细胞状态的影响；
- CD8–PD-L1 相互作用特征与生存和免疫治疗响应；
- 健康肝脏与肝癌中的 $\gamma\delta$ T 细胞通讯差异。

这些分析跨越 MERSCOPE、CosMx、Xenium、GeoMx、scRNA-seq 和 TCGA 派生数据，显示方法具有较广的应用接口。但它们仍然是观察性关联和假设生成证据，不等于实验因果验证。

### 6. 代码实现与论文是否一致？

核心一致性较高。公开代码中可以直接找到：

- Python 中的邻域、袋子、表达聚合和接收阈值；
- R 中的 MIL 数据组织和多链 MCMC；
- Rcpp/C++ 中的 $Z\rightarrow\beta\rightarrow\delta\rightarrow U\rightarrow b$ Gibbs 更新；
- $b$、$\beta$、PIP/FDR 和诊断输出。

执行路径为：

```text
spacia.py
  → spacia_job.R
  → MIL_wrapper.R
  → MICProB_MIL_C2Cinter.R
  → Fun_MICProB_C2Cinter.cpp
```

需要注意的实现细节：

1. 距离在 Python 和 R 接口两侧都有归一化，因此 $b$ 的数值尺度依赖接口处理。
2. 公共输出中的 $\beta$ 是标准化和汇总后的结果，不是原始链样本。
3. PCA 回映射路径已经定位，但本次有界代码审查没有穷尽所有辅助函数，因此其细节标记为 **Partial**。
4. 仓库列出了依赖版本并提供测试数据、教程和 Singularity 配方，但没有找到锁定环境文件。

### 7. 可复现性与计算代价

代码可复现性评分为 **3.5/5**：

- 优点：官方仓库、固定 commit、核心代码清楚、依赖版本、测试数据、三种 smoke test、教程和容器配方齐全；
- 不足：没有 `environment.yml`/`requirements.txt`/lock file，完整论文数据来自外部，跨 Python/R/Rcpp 环境较复杂，完整图表脚本没有全部验证。

本次在固定快照上执行了 `python3 test.py`。三个测试都在导入阶段因当前 Python 环境没有 `matplotlib` 而停止。这是当前环境缺依赖，不是算法失败；本次分析没有在机器上新建或安装 Spacia 环境。

补充图 30 显示：Spacia 相对省内存，但运行很慢。它的优势是不同发送/接收细胞类型和接收特征任务相互独立，可以分配到多台机器；这种并行降低的是墙钟时间，不会减少总计算量。

### 8. 使用和解释时最重要的限制

1. 需要真正的单细胞分辨率 SRT、细胞分割和可靠注释；普通 Visium 多细胞 spot 不适合。
2. 主要建模空间局部的通讯，可能漏掉长距离或与距离无关的效应。
3. 接收表达二值化使阈值选择非常重要。
4. MCMC 计算昂贵，大规模筛查需要大量独立任务。
5. 空间共定位和表达关联不能自动证明因果或直接分子结合。
6. 分割误差、细胞类型误标、归一化、邻域半径和组织结构混杂都可能影响结果。
7. 不依赖配体—受体数据库提高了发现能力，也扩大了多重检验和实验验证负担。

### 9. 如何正确理解 Spacia 的输出

最稳妥的表述是：

> Spacia 在给定空间邻域、发送/接收细胞类型和表达处理方式下，优先排序与接收状态一致的局部发送细胞及其表达特征。

不宜直接表述为：

> Spacia 已经证明某个发送细胞通过某个分子直接导致了接收细胞变化。

因此，Spacia 最适合作为局部 CCC 假设生成工具：用 $b$ 检查空间局部性，用 $\beta$ 解释发送表达效应，用主要实例分数定位具体细胞对，再结合组织学、已知通路、独立数据和扰动实验做后续验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spacia: mapping cellular interactions from spatial transcriptomics

### At a glance

Spacia is a Bayesian multiple-instance learning framework for inferring localized cell–cell communication from single-cell-resolution spatial transcriptomics. It jointly estimates which nearby sender cells influence each receiver, how interaction probability changes with distance, and which sender genes or pathways are associated with receiver-gene/pathway expression.

Published in *Nature Methods* (2024), DOI `10.1038/s41592-024-02408-1`.

### Problem

Common CCC methods built for scRNA-seq—such as CellChat (*Nature Communications*, 2021), NicheNet (*Nature Methods*, 2020), and CellPhoneDB (*Nature Protocols*, 2020)—usually aggregate cells by type, rely on known ligand–receptor databases, or infer interaction from ligand/receptor coexpression without resolving individual cell pairs. Spatial methods such as SpaTalk (*Nature Communications*, 2022), COMMOT (*Nature Methods*, 2023), and SpatialDM (*Nature Communications*, 2023) use spatial information, but the paper argues that they do not fully model the multiple-senders-to-one-receiver structure while simultaneously producing gene-level and cell-pair-level effects.

Single-cell SRT creates exactly this structure: every receiver may have many plausible neighboring senders, only some of which are truly relevant, and the effective spatial range can vary by cell type and signaling mechanism.

### Core idea

Spacia represents each receiver cell as a **bag** and its nearby candidate sender cells as **instances**. It links two probit models:

1. A distance model estimates latent primary-sender indicators $\delta_{ij}$ and coefficient $b$.
2. A receiver-response model uses only senders with $\delta_{ij}=1$ to estimate expression effects $\beta$.

MCMC jointly samples $b$, $\beta$, $\delta$, and the probit latent variables. The outputs include sender–receiver cell-pair scores, sender-gene/pathway-to-receiver-gene/pathway effects, spatial-range estimates, FDR/significance, and optional chain diagnostics.

```text
expression + coordinates + cell types
        → receiver-centered sender neighborhoods
        → gene/pathway/PCA features + binary receiver response
        → nested probit Bayesian MIL
        → MCMC posterior
        → cell-pair interactions + gene/pathway interactions
```

The method is not restricted to curated ligand–receptor pairs: any measured sender feature and receiver feature may be tested. It supports individual genes, user-defined pathways, correlation/clustering aggregation, and PCA-driven aggregation.

### Evaluation and main findings

- **Simulation:** with more than 10,000 MCMC iterations, cell-pair identification reached ROC AUC above 0.95. Primary versus non-primary sender scores separated strongly, and truly interacting $\beta$ values were distinguished from null features.
- **Comparator analysis:** on prostate MERSCOPE, Spacia produced localized explicit cell-pair edges. Of its inferred gene interactions, 92.7% were unique to one or two sender cell types, whereas the compared tools shared more interactions broadly across sender types; COMMOT's reported interactions were all shared across the nine tested sender types in this analysis.
- **Technology coverage:** the study applied Spacia to MERSCOPE, CosMx, and Xenium, spanning three commercial single-cell-resolution SRT platforms.
- **Biological applications:** Spacia linked microenvironmental sender programs to tumor EMT and lineage plasticity, identified PD-L1-associated tumor-to-immune effects and a CD8–PD-L1 signature associated with survival and checkpoint response, and detected altered $\gamma\delta$-T-cell communication in liver cancer versus healthy liver.
- **Scaling:** supplementary benchmarking shows relatively low memory use but slow runtime. Independent cell-type/receiver-response jobs can be distributed across systems; some comparators exceeded 512 GB on larger subsets.

The most convincing evidence is the combination of matched simulation, direct visualization of local cell-pair edges, differentiated sender-type programs, and analyses across several SRT technologies. The clinical/biological results remain observational hypotheses rather than experimental proof of causal signaling.

### Code and paper match

Official code: `https://github.com/yunguan-wang/Spacia`, pinned here at commit `11809bbe38e9107ab2b4444466958fdf7ab1e369`.

The core paper–code fidelity is **high**. Direct source inspection verified:

- receiver-centered bag construction and sender instances;
- receiver-expression thresholding;
- both probit layers;
- Gaussian priors and Gibbs MCMC;
- posterior $b$, $\beta$, primary-instance, FDR, and diagnostic outputs;
- the Python → R → Rcpp execution path.

Important implementation details include double normalization of distance across the Python/R boundary, standardized/processed public $\beta$ summaries, and a recalculated primary-instance quantity that the code explicitly says is a score rather than a calibrated probability. PCA back-mapping was located but only partially traced within the bounded review.

### Reproducibility

**Rating: 3.5/5.**

Strengths:

- official repository and pinned commit;
- readable core implementation with direct equation correspondence;
- documented package versions;
- synthetic test data and three smoke-test modes;
- Python and R tutorials;
- Singularity recipe;
- public links for the major external datasets.

Gaps:

- no `environment.yml`, `requirements.txt`, or lock file was found;
- the current machine has no prepared Spacia environment;
- `python3 test.py` was attempted, but all three cases stopped at import because `matplotlib` is absent from the active interpreter;
- paper-scale MERSCOPE/CosMx/Xenium/TCGA/scRNA-seq inputs and compute were not recreated;
- full figure-by-figure analysis scripts were not exhaustively verified.

The failed smoke test is an environment failure, not evidence that the algorithm fails. This analysis deliberately did not install a new machine-wide environment.

### Limitations

1. Requires segmented, annotated, single-cell-resolution SRT; conventional multi-cell spots are outside the intended use.
2. Models proximity-dependent communication and can miss long-range or spatially uncoupled effects.
3. Converts receiver expression into a binary label, making cutoff selection consequential.
4. MCMC is computationally slow and large screens require many independent jobs.
5. Spatial co-variation and expression association do not establish biochemical causality.
6. Results can be affected by segmentation, cell typing, normalization, feature aggregation, neighborhood radius, and unmeasured tissue structure.
7. Searching beyond ligand–receptor databases increases discovery potential but also expands the hypothesis space and validation burden.

### Bottom line

Spacia makes a strong methodological contribution by treating CCC as a latent cell-pair-selection problem coupled to sender-to-receiver expression modeling. The core Bayesian MIL model is faithfully represented in the public code, and the paper demonstrates useful cross-platform applications. Its main practical costs are MCMC runtime, demanding input preparation, and careful interpretation: inferred edges are prioritized localized associations, not automatically validated causal interactions.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
