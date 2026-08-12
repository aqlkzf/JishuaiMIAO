---
layout: default
permalink: /paper-atlas/dyngen-9f49d3d3/
title: "dyngen"
nav: false
description: "dyngen 是一个用于生成动态单细胞组学数据的模拟器。论文的核心问题是：很多单细胞计算方法需要“真实答案”来评估，例如细胞在发育轨迹上的真实位置、真实 RNA velocity、每个细胞中每条调控边的真实活性；但真实实验数据通常无法提供这些 ground truth。合成数据如果能尽量模拟底层生物过程，就可以用于方法开发和定量 benchmarking。"
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
      <span>Nature Communications · 2021</span>
    </div>
    <h1>dyngen</h1>
    <p>Spearheading future omics analyses using dyngen, a multi-modal simulator of single cells</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## dyngen 方法中文解读

### 1. 这篇论文要解决什么问题？

`dyngen` 是一个用于生成动态单细胞组学数据的模拟器。论文的核心问题是：很多单细胞计算方法需要“真实答案”来评估，例如细胞在发育轨迹上的真实位置、真实 RNA velocity、每个细胞中每条调控边的真实活性；但真实实验数据通常无法提供这些 ground truth。合成数据如果能尽量模拟底层生物过程，就可以用于方法开发和定量 benchmarking（`paper.md:9-12`, `paper.md:15-28`）。

论文特别强调，dyngen 不是只模拟测序噪声，而是从基因调控网络（GRN）出发，模拟转录、剪接、翻译、降解等反应，再通过单细胞实验采样过程得到类似真实 scRNA-seq 的观测矩阵（`paper.md:30-45`）。

### 2. 为什么已有方法不够？

论文提到已有单细胞模拟器包括 Splatter、powsimR、PROSSTT 和 SymSim。作者认为这些工具已经广泛用于比较单细胞方法，但更多关注单细胞实验协议带来的技术效应，例如 RNA 捕获、扩增、测序等；相对而言，它们对底层生物调控过程（转录、剪接、翻译、调控网络动态）的建模不够深入，因此很难直接扩展到 RNA velocity、细胞特异调控网络推断、轨迹对齐等新任务（`paper.md:26-29`）。

另外，低分子数是单细胞数据的重要特征，普通 ODE 模型并不适合低分子数随机模拟；因此论文选择 Gillespie stochastic simulation algorithm（SSA）作为核心模拟机制（`paper.md:24-26`, `paper.md:315-324`）。

### 3. dyngen 的总体思路

论文说生成 in silico 单细胞数据包括六个主要步骤（`paper.md:73-78`）。代码中的 `generate_dataset()` 也直接按这个顺序调用核心函数（`R/generate_dataset.R:54-115`）：

```text
用户定义 backbone / module network
        |
        v
生成 TF 网络 generate_tf_network()
        |
        v
生成 target + housekeeping 网络 generate_feature_network()
        |
        v
生成动力学参数和反应公式 generate_kinetics()
        |
        v
生成 gold-standard 轨迹 generate_gold_standard()
        |
        v
GillespieSSA2 模拟单细胞 generate_cells()
        |
        v
模拟实验采样 generate_experiment()
        |
        v
输出 list/dyno/SCE/Seurat/AnnData 等格式 wrap_dataset()
```

`initialise_model()` 保存用户的 backbone、细胞数、TF/target/HK 数量、距离度量、网络参数、动力学参数、gold standard 参数、模拟参数和实验采样参数（`R/1_initialisation.R:45-126`）。

### 4. 模块网络和 GRN 生成

#### 4.1 模块网络

dyngen 的起点是 module network。一个模块代表一组基因；模块之间有上调或下调关系；模块可以有 basal expression，也可以在 burn phase 期间激活；模块间边有 strength 和 effect（`paper.md:79-95`）。这些模块定义了模拟细胞会经历什么动态过程，例如线性、循环、分叉、汇聚等。

#### 4.2 TF 网络

论文说 TF 是模拟中驱动分子变化的核心，用户提供 backbone 和 TF 数量，每个 TF 被分配到某个模块，并继承模块属性（`paper.md:97-104`）。代码中 `.generate_tf_info()` 把 TF 分配到模块并生成 ID；`.generate_tf_network()` 根据模块之间的调控边，从调控模块里抽样 TF 作为 regulator（`R/2_tf_network.R:25-116`）。

#### 4.3 target 和 housekeeping 网络

论文描述 target gene 会从 FANTOM5 GRN 中抽样，housekeeping gene 也从该网络抽样，并且与 TF/target 子网分离（`paper.md:105-113`）。代码实现的是一个更通用的 `realnet` 机制：`generate_feature_network()` 接收或下载稀疏真实网络，抽样 target 和 HK 子网，然后把它们加入 `feature_info` 和 `feature_network`（`R/3_feature_network.R:30-136`）。target 抽样使用图结构、PageRank、诱导子图和缺失 regulator 补齐（`R/3_feature_network.R:175-264`）；HK 抽样使用 BFS 子图（`R/3_feature_network.R:266-320`）。

需要区分：FANTOM5 是论文中的数据来源说法；当前直接代码证据验证的是 `realnet` 抽样机制，而不是某个本地 `realnet` 一定就是 FANTOM5。

### 5. 从 GRN 到随机反应系统

dyngen 对每个基因 `G` 追踪三类分子：pre-mRNA、mature mRNA 和 protein。论文把反应分为 transcription、splicing、translation、pre-mRNA degradation、mRNA degradation 和 protein degradation（`paper.md:115-132`）。代码中 `generate_kinetics()` 创建 `mol_premrna_*`、`mol_mrna_*`、`mol_protein_*` 三类分子 ID，并为每个 feature 生成六类反应（`R/4_kinetics.R:80-112`, `R/4_kinetics.R:329-368`）。

### 6. 核心公式：转录 propensity

dyngen 的关键数学对象是转录 propensity：在当前 regulator 蛋白丰度下，某个基因发生转录反应的倾向。

论文先用 promoter state 的期望活性表示：

$$f(y_1,\ldots,y_N)=\text{xpr}\cdot \sum_{j=0}^{2^N-1}\alpha_j\cdot P(S_j)$$

其中 `xpr` 是 pre-mRNA production rate，`S_j` 是 promoter 状态，`α_j` 是该状态下 promoter 的相对活性（`paper.md:133-146`）。

对于单个 regulator，论文使用 Hill equation，并定义：

$$\nu_i=\left(\frac{y_i}{k_i}\right)^{n_i}$$

最终单 regulator 形式为：

$$f(y_1)=\text{xpr}\cdot \frac{\alpha_0+\alpha_1\nu_1}{1+\nu_1}$$

（`paper.md:147-178`）。对于多个 regulator，论文进一步推广为乘积形式，并给出大 `N` 时的简化公式（`paper.md:192-288`）。最后加入 basal expression `ba` 和 synergism/independence 参数，得到：

$$f(y_1,\ldots,y_N)=\text{xpr}\cdot \frac{\text{ba}-\text{sy}^{|R^+|}+\prod_{i\in R^+}(\nu_i+\text{sy})}{\prod_{i\in R}(\nu_i+1)}$$

（`paper.md:288-310`）。

代码对应实现是在 `.kinetics_generate_formulae()` 中用字符串生成 propensity：

- `chi = strength * pow(protein / dissociation, hill)`；
- 分子项为 `bas - pow(ind, number_of_activators) + product(chi + ind)`；
- 分母为所有 regulator 的 `product(chi + 1)`；
- 最终 transcription propensity 是 `transcription_rate * numerator / denominator`（`R/4_kinetics.R:248-329`）。

### 7. Gillespie SSA 模拟细胞

论文使用 Gillespie SSA。每一步触发一个反应，时间增量为：

$$\tau = \frac{1}{\sum_j \mathrm{prop}_j}\ln\left(\frac{1}{r}\right),\quad r\sim U(0,1)$$

（`paper.md:315-324`）。代码用 `GillespieSSA2::compile_reactions()` 预编译反应，再用 `GillespieSSA2::ssa()` 运行 burn phase、主模拟和可选 knockdown（`R/6_simulation.R:112-134`, `R/6_simulation.R:200-415`）。默认模拟参数包括 `ssa_etl(tau = 30/3600)`、`census_interval = 4`、32 个 wild-type simulation，并且默认不计算 cellwise GRN 和 RNA velocity（`R/6_simulation.R:101-134`）。

### 8. 模拟实验采样

SSA 得到的是完整分子状态；真实单细胞实验只观察到采样后的分子计数。论文说 dyngen 会先从模拟轨迹中采样细胞，再使用真实 scRNA-seq 数据中的 library size 和 count distribution 模拟分子采样（`paper.md:327-354`）。代码中 `generate_experiment()` 先抽取 `step_ix` 并生成 `cell_id` 和细胞元数据，然后取出对应模拟状态的真实计数，再用 `.simulate_counts_from_realcounts()` 把 simulated CPM 和 library size 映射到 reference realcount 分布，并用 `rmultinom()` 抽样分子（`R/7_experiment.R:46-214`）。

### 9. 三类 ground truth 输出

#### 9.1 轨迹 ground truth

论文说 gold-standard trajectory 由 state network 和模块变化约束决定，然后把模拟细胞映射到最相似的 ground-truth 轨迹位置（`paper.md:363-372`）。代码中 `generate_gold_standard()` 计算模块变化、预编译反应、运行 gold-standard simulation、计算降维并生成 trajectory network（`R/5_gold_standard.R:29-58`, `R/5_gold_standard.R:135-278`）。后续 `.generate_cells_predict_state()` 使用 `dynutils::calculate_distance()` 找最近的 gold-standard 状态；默认距离度量为 Pearson（`R/6_simulation.R:492-542`, `R/1_initialisation.R:45-126`）。

#### 9.2 cell-specific GRN

论文定义 regulator `R` 对 target `T` 的调控效应为：把 regulator 蛋白丰度设为 0 前后，target transcription propensity 的变化，再除以 target 的 pre-mRNA production rate（`paper.md:375-390`）：

$$\text{regeffect}_G=\frac{\text{proptrans}_G(S)-\text{proptrans}_G(S[z_T\leftarrow 0])}{\text{xpr}_G}$$

代码在 `.generate_cells_compute_cellwise_grn()` 中逐个 cell 和 regulator 计算这个 knock-out effect，过滤很小的值，并返回 cell × edge 的稀疏矩阵（`R/6_simulation.R:416-490`）。

#### 9.3 RNA velocity

论文把 ground-truth RNA velocity 定义为 transcription propensity 减去 mRNA decay propensity，并用它评估 velocyto 和 scVelo（`paper.md:416-430`）。代码在 `.generate_cells_compute_rna_velocity()` 中提取相关反应的 propensity 和 effect，用稀疏矩阵乘法得到每个 gene 的 velocity（`R/6_simulation.R:544-639`）。

### 10. 论文评估结果与代码边界

论文用 dyngen 展示三类应用（`paper.md:47-64`）：

- trajectory alignment：DTW 和 cellAlign，在 40 个数据集上用 ABWAP 评估（`paper.md:431-449`）；
- RNA velocity：velocyto 和 scVelo，在 42 个数据集上用 velocity correlation 和 velocity arrow cosine 评估（`paper.md:416-430`）；
- CSNI：SCENIC、LIONESS、SSN，在 42 个数据集上用 mean AUROC/AUPR 评估（`paper.md:392-415`）。

但在本工作区分析的 `dynverse/dyngen` 包源码中，直接搜索没有找到 `ABWAP`、`DTW`、`cellAlign`、`velocyto`、`scvelo`、`SCENIC`、`LIONESS`、`SSN` 的 benchmark 脚本。论文的数据/代码可用性部分说明，manuscript analyses 在另一个仓库 `dynverse/dyngen_manuscript` 中，而 dyngen 包本身是核心模拟器（`paper.md:463-473`）。因此，本工作区可以验证核心模拟器实现，但不能用当前包源码验证论文 benchmark 图的全部复现实验脚本。

### 11. 实用建议

- 如果目标是生成带 ground truth 的动态单细胞数据，当前 `dyngen` 包就是核心实现。
- 如果需要 RNA velocity 或 cellwise GRN，必须打开相应参数；默认设置不计算所有可选 ground-truth 层（`R/6_simulation.R:101-134`, `R/6_simulation.R:396-415`）。
- 如果目标是复现论文 Fig. 2 的 benchmark boxplots 或 ABWAP/scVelo/SCENIC 比较，应额外获取 `dynverse/dyngen_manuscript` 和补充材料。本工作区没有 supplementary markdown，也没有 manuscript benchmark 脚本。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## dyngen Summary

### What problem does the paper solve?

The paper introduces **dyngen**, a simulator for dynamic single-cell omics data with known ground truth. The motivation is that real single-cell data rarely provide exact truth for trajectory position, RNA velocity, or cell-specific regulatory activity, while synthetic data can provide these labels for quantitative method development and benchmarking (`paper.md:15-28`).

### Why existing simulators were insufficient

The paper argues that earlier single-cell simulators such as Splatter, powsimR, PROSSTT, and SymSim are useful but emphasize technical protocol effects more than mechanistic biology. Because they focus less on transcription, splicing, translation, and regulatory dynamics, the authors say they are less reusable for tasks such as trajectory inference, RNA velocity, and cell-specific network inference (`paper.md:26-29`). The paper also notes that low molecule counts make ordinary differential equation approaches ill-suited for single-cell simulation (`paper.md:24-26`).

### Proposed method

Dyngen simulates cellular dynamics by:

1. defining a module/backbone network for a dynamic process;
2. expanding it into a gene regulatory network with TFs, targets, and housekeeping genes;
3. converting the GRN into stochastic reactions for transcription, splicing, translation, and degradation;
4. simulating cells with Gillespie’s stochastic simulation algorithm;
5. sampling cells and molecules to emulate single-cell protocols;
6. exporting ground-truth trajectory, RNA velocity, and cellwise regulatory-network information (`paper.md:30-45`, `paper.md:73-354`).

The package implementation mirrors this pipeline in `generate_dataset()`, which calls `generate_tf_network()`, `generate_feature_network()`, `generate_kinetics()`, `generate_gold_standard()`, `generate_cells()`, and `generate_experiment()`, then wraps the dataset in the requested format (`R/generate_dataset.R:54-115`).

### Key computational ideas

- **Mechanistic reaction system:** For every gene, dyngen tracks pre-mRNA, mRNA, and protein, with reactions for transcription, splicing, translation, and degradation (`paper.md:115-132`; `R/4_kinetics.R:80-112`, `R/4_kinetics.R:329-368`).
- **Regulatory propensity model:** Transcription propensity is derived from promoter-state/Hill-like terms and simplified for many regulators using basal and independence/synergy parameters (`paper.md:133-310`). The code builds the corresponding propensity strings using regulator protein abundance, dissociation, Hill coefficient, interaction strength, basal, and independence (`R/4_kinetics.R:248-329`).
- **SSA simulation:** Cells are simulated with GillespieSSA2, including optional propensity/firing logging, knockdowns, cellwise GRN, and RNA velocity (`paper.md:315-324`; `R/6_simulation.R:112-415`).
- **Experiment emulation:** The final data layer samples simulated states and maps molecule counts/library sizes to reference single-cell count distributions (`paper.md:327-354`; `R/7_experiment.R:46-214`).

### Evaluation in the paper

The paper uses dyngen for three illustrative downstream evaluations rather than an exhaustive benchmark (`paper.md:47-64`):

- **Trajectory alignment:** DTW and cellAlign are evaluated on 40 simulated paired linear trajectories with ABWAP (`paper.md:58-64`, `paper.md:431-449`).
- **RNA velocity:** velocyto and scVelo are evaluated on 42 datasets using velocity correlation and velocity arrow cosine (`paper.md:416-430`).
- **Cell-specific network inference:** SCENIC, LIONESS, and SSN are evaluated on 42 datasets using mean AUROC and AUPR against dyngen cellwise GRN truth (`paper.md:392-415`).

The two local figure images visually support these claims: Fig. 1 shows dyngen’s molecule/reaction/regulation outputs and applications; Fig. 2 shows the three benchmark settings and boxplots (`figure_analysis.md`).

### Code-paper match and reproducibility

The analyzed code is `https://github.com/dynverse/dyngen` at commit `620b3e8fabf9f6ee50362f9d38fb27eed2725b47`. The core simulator package has a **medium-high** match to the paper’s method pipeline: initialization, GRN generation, kinetics/reactions, Gillespie simulation, experiment sampling, ground-truth trajectory, RNA velocity, cellwise GRN, and output wrappers are present and directly verified in R source.

The main reproducibility gap is that manuscript benchmark scripts are **not** in this package snapshot. Direct searches under `code source/**/*.R` found no implementation of ABWAP, DTW/cellAlign benchmarking, velocyto/scVelo runs, or SCENIC/LIONESS/SSN evaluation. This is consistent with the paper’s availability statement, which distinguishes the dyngen package from the manuscript-analysis repository `dynverse/dyngen_manuscript` (`paper.md:463-473`). Supplementary markdown/images are also absent in this workspace.

### Practical takeaways

- Use this package to generate mechanistic, ground-truthed dynamic single-cell datasets.
- Enable optional flags if you need cellwise GRN or RNA velocity outputs; defaults do not compute all optional ground-truth layers (`R/6_simulation.R:101-134`, `R/6_simulation.R:396-415`).
- For reproducing the paper’s benchmark figures and ABWAP/scVelo/SCENIC comparisons, obtain the separate manuscript repository and supplementary/source data rather than relying on this core package alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
