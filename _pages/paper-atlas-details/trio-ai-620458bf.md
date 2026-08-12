---
layout: default
permalink: /paper-atlas/trio-ai-620458bf/
title: "TRIO-AI"
nav: false
description: "TRIO-AI 不是一个在本工作区中可运行、可复核的软件实现，而是论文提出的一套三视角分析框架：Temporal GNN 用时间标签约束细胞图表示，Neural ODE 在聚合后的时间中心上描绘连续路径，Time-VAE 用条件潜空间中的低密度区域筛选候选过渡细胞。作者随后把低密度、稀有性、分支邻近性和时间不对称性合成 novelty score，并把 MPs3 解释为肝缺血再灌注损伤后的候选过渡巨噬细胞状态。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>TRIO-AI</h1>
    <p>TRIO-AI: Hybrid temporal graph, ODE, and VAE modeling for high-resolution cellular trajectory inference in liver injury</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2025.12.17.694956" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TRIO-AI 方法解读：论文提出了什么，现有证据又能支持到哪里

### 先给结论

TRIO-AI 不是一个在本工作区中可运行、可复核的软件实现，而是论文提出的一套三视角分析框架：Temporal GNN 用时间标签约束细胞图表示，Neural ODE 在聚合后的时间中心上描绘连续路径，Time-VAE 用条件潜空间中的低密度区域筛选候选过渡细胞。作者随后把低密度、稀有性、分支邻近性和时间不对称性合成 novelty score，并把 MPs_3 解释为肝缺血再灌注损伤后的候选过渡巨噬细胞状态。

这个思路有启发性，但当前论文和工作区只足以说明“作者如何组织分析以及结果图呈现了什么”，不足以证明算法性能、复现具体结果，或证明 MPs_3 是一条真实谱系中的因果性中间态。工作区没有代码仓库；论文也没有给出足够的网络结构、训练参数、随机种子、数据划分、ODE 求解器或 KDE 带宽。因此以下内容严格区分三类信息：论文明确写出的步骤、由图支持的观察，以及尚未被实现或实验验证的解释。

### 1. 输入与预处理

论文主分析围绕小鼠肝缺血再灌注后的时间序列数据展开，文中出现 D0、D1、D3、D5，也出现公共数据的 24 h、48 h 等时间描述。两套时间标记如何逐一映射并不清楚，某些图还使用 0–300 h 的连续坐标；因此不能把所有时间轴自动视为同一实验时钟。

论文描述的单细胞预处理包括：过滤线粒体比例高于 20%、检测基因少于 200 或总计数异常高的细胞；使用 Seurat 的方差稳定化特征选择、PCA 和 Harmony；再构建 Leiden 聚类、扩散伪时间、RNA velocity 等下游对象。空间部分涉及 Visium、cell2location、CellChat 或 LIANA 等工具名称。工具被点名不等于参数与版本可复现：论文未给出完整环境、关键命令或固定版本。

一个重要边界是，后续三个模块并非都直接作用于相同的原始量：GNN 使用 PCA 或其他细胞特征及图边；ODE 主要作用于分箱或聚类中心；VAE 使用归一化、对数化和缩放后的表达矩阵。三种输出在什么尺度上校准，论文没有完整说明。

### 2. Temporal GNN：用已知时间监督图表示

#### 2.1 图如何构建

论文列出多种候选边：kNN、互为近邻、表达相似性、扩散图、PAGA、RNA velocity 方向边，以及自环。图中节点是细胞，节点特征主要来自 PCA。这里最关键但没有解决的问题是：最终结果究竟使用哪一种边或哪几种边的组合、阈值和方向如何处理。图中比较若干 edge strategy，只能说明作者探索过多种图，不能替代完整的可执行定义。

#### 2.2 模型学什么

论文描述 GAT 层、ELU 和 dropout，并把输出保存为 `adata.obsm["X_temporalGNN"]`。训练目标包含三项：

$$
\mathcal{L}=\lambda_{cls}\mathcal{L}_{CE}+\lambda_{reg}\mathcal{L}_{SmoothL1}+\lambda_{edge}\mathcal{L}_{smooth}.
$$

交叉熵预测离散时间箱，Smooth L1 回归连续时间，边平滑项让相连细胞的表示接近。这个目标确实把采样时间引入表示学习，但它也带来解释上的循环性：如果模型以时间标签训练，再用其输出证明细胞具有时间结构，那么“按时间分开”首先是训练目标的结果，而不是独立的生物验证。

论文没有给出层数、隐藏维度、attention heads、dropout 比例、损失权重、优化器、学习率、epoch、早停、训练/验证划分或随机种子。所以我们可以解释目标函数的作用，不能重建作者的实际模型，也不能确认 `X_temporalGNN` 是由哪套参数得到。

#### 2.3 输出能说明什么

GNN 嵌入和 UMAP 上的时间排列可支持“表示与已知采样时间一致”。它们不能单独证明细胞沿该方向真实转化。UMAP 只是高维表示的二维投影，图上相邻、桥接或分叉不等价于谱系祖先—后代关系。

### 3. Neural ODE：在中心点之间拟合连续曲线

论文先按潜在时间的分位数把细胞划成 30 个箱，每箱计算中心；再对中心构建最小生成树，用几何结构寻找候选分支，并以 ODE 拟合连续演化。另一个视角以 Leiden 聚类中心、按平均潜在时间排序后拟合路径。

可把概念写成：

$$
\frac{d\mathbf{z}(t)}{dt}=f_\theta(\mathbf{z}(t),t),
$$

其中 $\mathbf{z}(t)$ 是中心在潜空间中的位置。注意，论文没有给出 $f_\theta$ 的网络结构、ODE solver、步长或容差、训练损失和正则化。公式表达的是方法类别，不是可复现实现。

把大量细胞压缩成 30 个中心能降低噪声，却会隐藏箱内异质性。MST 必须连接所有中心，因此出现边和分支并不自动证明真实发育分叉。ODE 在这些中心上生成平滑轨迹，证明的是“给定排序可以被连续曲线描述”，不是单细胞的真实运动，也不是命运承诺。将轨迹再投影到 UMAP 会进一步引入二维几何失真。

### 4. Time-VAE：低密度筛选是候选规则，不是过渡态证明

论文称该模块基于 scvi-tools，使用时间点作为条件变量训练 VAE。概念上它优化 ELBO：

$$
\mathcal{L}_{ELBO}=
\mathbb{E}_{q_\phi(\mathbf{z}|\mathbf{x},t)}[\log p_\theta(\mathbf{x}|\mathbf{z},t)]
-D_{KL}(q_\phi(\mathbf{z}|\mathbf{x},t)\|p(\mathbf{z})).
$$

随后作者把潜变量 PCA 到二维，用 KDE 估计局部密度，并把最低 25% 标成 candidate transitional cells。这个规则可以寻找潜空间中稀疏的点，但“低密度”有很多替代解释：采样不足、批次效应、群体边界、离群值、二维降维失真，以及 KDE 带宽选择。尤其论文没有报告 bandwidth、核函数设置、潜维数、VAE 架构、训练参数或敏感性分析。最低四分位数是固定筛选阈值，不是经过校准的生物学概率。

论文同时写到先做每细胞 10,000 归一化、对数化和缩放，再使用 scvi-tools。标准 scVI 类计数似然通常以原始 counts 为输入；由于没有代码，无法判断作者实际使用的是哪一种 scvi-tools 模型、是否自定义似然，或文字是否省略了数据层切换。这是实现不确定性，不能擅自补全。

### 5. 三模块合成与 novelty score

论文给出等权合成：

$$
Novelty=0.25(LD+RR+BR+VA),
$$

其中 LD 表示低密度，RR 表示稀有度，BR 表示分支相关分数，VA 表示时间或 velocity 不对称性。论文没有充分给出四项的精确归一化、边界条件和计算伪代码，也没有做权重消融或阈值校准。因此这个式子更像排序框架，而不是已验证的统计检验；得分不应被解释为置信度、后验概率或 FDR。

三个模块也并非完全独立：它们共享同一批细胞、预处理、时间标签和潜在结构。所谓“多方法收敛”可以提高候选结果的一致性，但不能据此宣称独立证据相乘或 FDR 必然下降。论文没有提供假阳性标注、空模型或 FDR 校准实验。

### 6. MPs_3 的证据链应该怎样读

作者把 MPs_3 描述为约 48 h 富集的巨噬细胞状态，展示其时间分布、潜空间位置、功能基因或通路，以及与其他细胞群的通讯和空间邻近。最稳妥的读法是：

1. 聚类和时间组成图显示一个被命名为 MPs_3 的表达群在中间时间附近富集；
2. 三种计算视角把这个群放在低密度、路径连接或时间变化显著的位置；
3. 标志基因和富集分析把它关联到脂质处理、凋亡细胞清除与基质重塑；
4. 通讯与空间分析提出 APOE–LRP1、FN1–ITGA9 等候选相互作用。

这是一条候选生成链，而不是谱系验证链。论文没有通过 lineage tracing、克隆追踪、时间分辨扰动或前后状态的直接转化实验证明 MPs_3 是必经中间态，也没有功能扰动证明相关配体—受体对驱动修复。因而宜称“候选过渡状态”或“与修复相关的计算候选”，不宜称“已验证的过渡细胞”。论文中“稀有”“短暂”等定性描述也没有在可复核表格中给出统一的细胞数、比例和置信区间；不能把“<5%”当作已核实事实。

### 7. 空间和细胞通讯证据的边界

CellChat/LIANA 类方法主要根据配体、受体表达和先验数据库给出通讯潜力；cell2location 把单细胞参考映射到空间转录组位置。它们可支持“表达兼容”和“空间共现”，但不能证明分子真的结合、信号方向、作用强度或因果关系。

Visium 是 spot 级空间转录组，不是纳米尺度蛋白测量。论文把相关结果称为“nanoscale protein-level evidence”超出了所述数据模态能够直接支持的范围。空间邻近与共表达至多用于提出待验证机制。

### 8. 本地 50 张图实际提供的证据

工作区保存了 50 张从 PDF 转出的图像，已逐张检查。它们主要包括流程图、UMAP、不同图边策略、VAE 密度与最低四分位标记、群体比例、路径投影、通讯点图、通路富集和空间图。许多面板标签或图注很简略，因此不能仅凭图像反推出未写明的数值。

图 1 给出三模块流程，但不是实现规格。GNN/ODE/VAE 面板展示作者得到的几何结构，未提供独立真值。低密度面板中，被标记的点经常位于整体流形外围；这与筛选规则一致，也说明离群或边界效应是必要的替代解释。通讯和富集图用于候选机制排序，不构成功能验证。

### 9. 论文内部必须保留的证据警报

- Figure 11 的文字图注明确转入 cardiac tissue、myocardium、infarct 和 ventricular structural integrity，甚至一句话同时出现 liver repair 与 ventricular integrity。无论图像外观如何，仅凭当前 PDF 无法确认该图的数据来源和器官归属；在作者澄清前不能把它作为肝脏验证证据。
- 正文后部引用 “Figure 18”，但本地 PDF 转换结果中没有可对应、可追溯的 Figure 18 图像和完整图注。
- 图号、正文引用和部分导出图片的对应关系存在错位，故 `figure_analysis.md` 中的面板映射只能作为导航，不能当作无歧义出处。
- 摘要宣称与五种 state-of-the-art 方法比较并表现更好，但当前稿件没有呈现可核查的五方法名单、量化基准表、指标、数据划分或统计检验。不能从引言中猜出五个方法并代替实验。
- “19 对比 3”“6.3-fold”等结果可复述为作者报告的计数，但缺少完整候选全集、阈值和统计校准，不宜提升为普遍性能结论。

### 10. 代码与复现边界

本工作区没有 `code source`，论文未提供代码仓库 URL，局部 CodeGraph 查询也没有发现实现源码。因此以下内容均无法直接验证：

- 实际采用的图边组合和预处理数据层；
- GAT、VAE、ODE 的网络结构与所有训练超参数；
- 损失权重、随机种子、训练划分和模型选择；
- ODE 求解器、容差、中心计算和分支判定；
- KDE bandwidth、四分位阈值敏感性和 novelty score 归一化；
- 图表从哪一份中间文件生成，以及 Figure 11 / Figure 18 的来源。

所以“paper-only”不是说论文没有方法，而是说当前工作区只能审读方法描述，不能进行实现级代码—论文匹配，也不能宣称复现成功。

### 11. 最安全的研究结论

TRIO-AI 的主要价值是把三个互补视角组织成一个候选筛选框架：时间监督图表示负责排序，中心级 ODE 负责连续几何，条件 VAE 的密度负责突出稀疏状态。它提示 MPs_3 及若干配体—受体关系可能值得进一步实验。

目前最稳妥的表述是：“论文提出 TRIO-AI，并在肝损伤时间序列数据上报告了 MPs_3 候选过渡状态。”不能据当前稿件进一步断言它优于五种方法、降低 FDR、精确重建真实谱系，或已经通过空间和功能实验验证 MPs_3。下一步真正需要的是公开代码与环境、完整基准与消融、时间轴和图号校正，以及独立 lineage/perturbation 验证。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## TRIO-AI: Summary

**Full title**: TRIO-AI: Hybrid temporal graph, ODE, and VAE modeling for high-resolution cellular trajectory inference in liver injury
**Authors**: Hui Li, Jinlian Wang, Yankai Wen, Hongfang Liu, Cynthia Ju
**Institution**: UTHealth Houston (McWilliams School of Biomedical Informatics + Department of Anesthesiology)
**Preprint**: bioRxiv, December 2025 | DOI: 10.64898/2025.12.17.694956
**Code**: Not publicly available (preprint)

---

### Motivation & Novelty

#### Biological Problem

The manuscript frames liver ischemia-reperfusion (IR) injury as a time-resolved macrophage response and reports MPs_3 as a candidate intermediate reparative state near 48 h. The available manuscript does not provide a single auditable table establishing a <5% frequency, a fixed 24 h lifetime, or that this state is a necessary mechanistic checkpoint; those descriptions should be treated as author interpretation.

#### Why Existing Methods Fall Short

| Method | Limitation | Citation |
|--------|-----------|---------|
| Monocle3 | Static pseudotime; fails to capture non-monotonic or reversible transitions | Nature Biotechnology, 2014 |
| Slingshot | Pseudotime-based; no actual timepoint integration | BMC Genomics, 2018 |
| scVelo | Uses RNA velocity for directionality, but snapshot-based; no timepoint data or cell-cell interaction graphs | Nature Biotechnology, 2020 |
| CellRank | Probabilistic fate mapping, but snapshot-based; limited temporal resolution | Nature Methods, 2022 |
| Tempora | Uses actual timepoints but aggregates to cluster level; loses single-cell granularity and rare states | PLoS Computational Biology, 2020 |
| TrajectoryNet | Optimal transport-based; lacks biological specificity, uses generic geometric priors | ICML, 2020 |
| Leiden/Louvain | Static clustering; temporally agnostic; systematically misses rare off-path populations | Scientific Reports, 2019 |

#### Unique Contributions of TRIO-AI

1. **Multi-timepoint temporal awareness**: Actual experimental timepoints (D0, D1, D3, D5) are explicitly incorporated into the GNN graph construction as training targets, not just used post-hoc for interpretation.

2. **Triple-convergence detection**: Three independent computational layers (GNN temporal enrichment, Neural ODE topology, Time-VAE density) must all flag a population for it to be designated high-priority. This substantially reduces false positives for rare populations.

3. **Dual-granularity trajectories**: Neural ODEs operate at both fine (30 temporal bins) and coarse (Leiden clusters) resolution simultaneously, capturing intermediates invisible at cluster level.

4. **Density-aware transitional state scoring**: The Time-VAE learns a probabilistic density model conditioned on timepoint, providing statistically grounded identification of low-probability (transitional) cell states.

5. **Structured novelty scoring**: The equal-weight composite score (LD + RR + BR + VA) provides a principled, reproducible ranking of candidate populations.

---

### Method Overview

TRIO-AI is a three-module hybrid computational framework for trajectory inference in time-series single-cell RNA-seq data. For detailed mathematics and algorithm, see `doc_method.md`.

**Module 1 — Temporal GNN**: Constructs a cell-cell graph $G=(V,E)$ using RNA velocity-directed + Leiden cluster edges. A Graph Attention Network (GAT) learns temporal embeddings trained with a composite loss: weighted cross-entropy for time-bin classification + Smooth L1 for continuous regression + edge smoothness. Output: `X_temporalGNN` per cell.

**Module 2 — Neural ODE**: Takes GNN embeddings and reconstructs continuous trajectories by fitting ODEs to temporal bin centroids ($N_b=30$) and Leiden cluster centroids separately. A minimum spanning tree identifies branch points in the 30-bin centroid space. Trajectories are projected onto UMAP for visualization.

**Module 3 — Time-VAE**: A timepoint-conditioned variational autoencoder (scvi-tools) learns a latent density model. Kernel density estimation (KDE) identifies the lowest-density 25th percentile as transitional states.

**Three-layer integration**: Temporal enrichment metrics (Rarity, Peak Prominence, Fold-Change vs. baseline, Resolution Drop) + Neural ODE topology (branch points, side paths) + Time-VAE density (KDE quartile) are combined into a composite Novelty score = 0.25×(LD + RR + BR + VA) to rank candidate populations.

---

### Evaluation

#### Dataset

- **In-house dataset**: Mouse liver IR injury, C57BL/6J males (12 weeks), two complementary cohorts:
  - Cohort 1: D0, D1, D3, D5 (n=2/timepoint); non-parenchymal hematopoietic cells (BD Rhapsody WTA)
  - Cohort 2: D0, D3, D5 (n=2/timepoint); enriched for endothelial cells + macrophage subsets
- **Public dataset**: GSE223561 — snRNA-seq + Visium spatial transcriptomics, human/mouse liver regeneration (ref: Matchett et al., Nature 2024)
- **Integration**: Harmony batch correction; joint analysis of in-house + GSE223561

#### Comparative Performance

The abstract states that TRIO-AI was compared against "five state-of-the-art methods," but the available manuscript does not identify a complete five-method benchmark with metrics and results. Methods mentioned in the Introduction must not be inferred to be the benchmark set.
- Superior detection of transitional states (MPs_3 detected by TRIO-AI; missed by conventional methods)
- More accurate branching trajectory reconstruction
- Identification of off-path populations missed by conventional approaches

**⚠ IMPORTANT LIMITATION**: The benchmark results are asserted in the abstract and Discussion but no quantitative comparison table or supplementary benchmark figures appear in the main text. The "five state-of-the-art methods" comparison is not formally documented in the available manuscript.

#### Key Quantitative Results

| Metric | Value | Context |
|--------|-------|---------|
| APOE→LRP1 pairs at 24h | 3 pairs | Visium proximity mapping |
| APOE→LRP1 pairs at 48h | 19 pairs | Visium proximity mapping (6.3× increase) |
| MPs_3 peak timing | 48h post-injury | Temporal proportion analysis |
| MPs_3 detection threshold | Lowest 25% KDE | Time-VAE transitional state cutoff |
| GNN embedding comparison | RNA vel. + Leiden edges best | Comparison across 9 edge strategies (Fig. 3) |

#### Biological Validation

- **MPs_3 transcriptional signature**: LRP1, LRP6, ABCA1, LDLR, SCARB1 (lipid handling); MARCO, MERTK, MSR1 (efferocytosis); ITGA9, ITGB1, SDC2 (ECM); TREM2, CX3CR1 (reparative macrophage)
- **Pathway enrichment**: PI3K-AKT, MAPK, NF-κB, ECM-receptor interaction, Fc-γ phagocytosis enriched; fatty acid degradation + PPAR suppressed (KEGG, adjusted p<0.01)
- **Spatial validation**: MPs_3 localizes to peri-necrotic borders in Visium sections; APOE-LRP1 co-localization hotspots confirmed at 48h in GSM6963518 and GSM6963526 samples
- **LIANA ligand-receptor**: APOE-LRP1 lr_means = 3.75 (highest confidence pair); hepatocytes dominate as APOE source (~40-60% of signal)

---

### Reproducibility

**Rating: 2/5**

**Justification**: The paper describes a complex multi-module framework requiring integration of Temporal GNN (custom code), Neural ODE (likely torchdiffeq), scvi-tools (for Time-VAE), scVelo, CellChat, LIANA, cell2location, and Harmony — all with non-trivial interactions. No code repository is publicly available, no pip-installable package is provided, no Docker container or conda environment file is given. The supplementary materials referenced in the text (Supplementary Table 1, Figure S2, Figure S1) are not attached to the preprint. Critical hyperparameters (GAT layers, hidden dimensions, ODE solver type, KDE bandwidth, bin count justification, novelty score normalization) are not specified. The data is partially available (GSE223561 on GEO; in-house BD Rhapsody data not deposited at time of analysis).

**Practical notes for reproduction**:
- scvi-tools installation: `pip install scvi-tools`; requires PyTorch
- RNA velocity: `pip install scvelo`; requires STAR-aligned BAM with splice site annotation
- CellChat: R package; significant version-sensitivity
- LIANA: Python (`liana-py`) or R package
- cell2location: `pip install cell2location`
- Data: In-house BD Rhapsody data — contact corresponding author (Hongfang Liu / Cynthia Ju, UTHealth Houston)
- Main reproducibility blocker: no TRIO-AI code released

**Strengths**:
- Biologically well-grounded framework targeting a real gap in trajectory inference
- Multi-view convergence provides a candidate-prioritization heuristic; no calibrated false-discovery-rate analysis is shown
- Spatial validation with Visium provides orthogonal confirmation
- Clear biological narrative connecting MPs_3 to APOE-LRP1 and FN1-ITGA9 axes

**Weaknesses**:
- **CellPhoneDB vs CellChat/LIANA discrepancy**: Figure 1b shows "CellPhoneDB + pathway enrichment" in the workflow schematic, but Methods §2.8 describes CellChat + LIANA as the actual tools. This suggests Figure 1 was drawn from an earlier pipeline version before tool substitution.
- No public code — method not reproducible from paper alone
- Benchmark comparison ("5 methods") is asserted but not documented quantitatively
- Figure 11 contains a critical provenance conflict: its legend describes **cardiac tissue** ("myocardium," "ventricular structural integrity") despite the paper being about **liver IR injury**. The current PDF cannot establish whether this is only a copy-editing error or a data-provenance problem.
- KDE 25th-percentile threshold for transitional state classification is arbitrary and not validated
- In-house dataset not deposited; spatial validation relies entirely on one public dataset (GSE223561)
- Hyperparameters not reported; no ablation study for the three modules
- The equal-weight composite novelty score (0.25 × each component) has no stated justification

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
