---
layout: default
permalink: /paper-atlas/spapros-a60d5dd3/
title: "Spapros"
nav: false
description: "Spapros 把“保留变化”当作主候选来源，把“细胞类型必须分得开”当作约束，再把探针可设计性和实验先验放进选择过程，因此比单纯 marker 排名或单纯方差排名更适合小型靶向空间转录组面板。"
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
      <span>Computational Tools</span>
      <span>Nature Methods · 2024</span>
    </div>
    <h1>Spapros</h1>
    <p>Probe set selection for targeted spatial transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Spapros 方法详解：如何为靶向空间转录组选择一组“既能分细胞类型，又能保留空间状态”的基因

### 1. 这篇论文要解决什么问题？

Xenium、MERFISH、seqFISH+、SCRINSHOT 等靶向空间转录组技术只能测量预先指定的一小组基因。实验开始后无法再补测，因此面板设计决定了后续分析能看见什么。

一个实用面板至少需要同时满足五个目标：

1. 能区分已知细胞类型或状态；
2. 能保留细胞类型内部的连续变化，而不只是离散 marker；
3. 不要浪费有限名额在高度冗余的基因上；
4. 避免过低表达、过高表达或光学拥挤等技术问题；
5. 每个基因都必须能设计出足够多、特异、互不重叠的探针。

传统方案往往只优化其中一部分。例如 NS-Forest（*Genome Research*, 2021）和 ActiveSVM/ASFS（*Nature Computational Science*, 2022）强调细胞类型判别；SCMER（*Nature Computational Science*, 2021）、geneBasis（*Genome Biology*, 2021）和 PERSIST（*Nature Communications*, 2023）强调流形、表达重建或稳健性。PCA 能保留总体变化，DE 能找 marker，但它们都没有独立解决“探针能否真正设计出来”的问题（`paper.md:470-506,560-573`）。

Spapros 的核心思想是：**先用 PCA 找“变化信息”，再用 DE 决策树定义“分类性能上限”，最后只把分类中真正缺失的 DE 基因补回 PCA 候选池。**

### 2. 输入与输出

#### 输入

- 一个经过归一化和 `log1p` 的 scRNA-seq `AnnData`；
- 每个细胞的类型或状态标签；
- 候选基因集合，通常是 HVG；
- 目标面板大小 (n)；
- 可选的必选基因、优先基因和文献 marker；
- 可选的表达、探针可设计性等逐基因惩罚因子。

论文基准通常先用 scran 归一化，再取 8,000 个 HVG（`paper.md:383-386`）。代码接口集中在 `ProbesetSelector`（`selection_procedure.py:316-415`）。

#### 输出

基因选择模块输出一个排序表，其中包括：

- 是否进入最终面板；
- 总排名、树排名和特征重要性；
- PCA 分数；
- 是否来自预选、先验、PCA、DE 或 marker 列表；
- 该基因帮助区分哪些细胞类型。

如果给定 (n)，代码按最终优先级取前 (n) 个基因（`selection_procedure.py:966-1184`）。随后外部 Oligo Designer Toolsuite 负责输出可订购的探针序列。

### 3. 全流程概览

```text
scRNA-seq 表达矩阵 + 细胞类型标签 + 用户先验
                     |
                     v
       探针可设计性过滤 + 表达惩罚
                     |
          +----------+----------+
          |                     |
          v                     v
     PCA 变化候选池          DE marker 候选池
          |                     |
          v                     v
   每类一个浅层二分类森林   针对难区分细胞优化的参考森林
          |                     |
          +----------+----------+
                     |
      若 PCA 森林某类性能低于 DE 参考森林，
      按特征重要性补入缺失的 DE 基因并重训
                     |
      加入必选基因、文献 marker、缺失类型 marker
                     |
     按优先级、树排名、重要性和 PCA 分数排序
                     |
              取前 n 个基因
                     |
    生成、过滤、选择互不重叠的探针并构建最终序列
```

### 4. 第一步：先处理“实验上能不能测”

论文不是先选基因、再被动删除无法设计探针的基因，而是把探针可行性放在前面。

对于每个候选基因，外部 Oligo Designer Toolsuite 会：

1. 从 NCBI、Ensembl 或自定义基因组/注释生成候选序列；
2. 按 GC、熔解温度、同聚核苷酸、二级结构、交叉杂交和脱靶进行过滤；
3. 搜索每个基因最优的、互不重叠的探针集合；
4. 删除探针数不足的基因；
5. 根据 SCRINSHOT/HybISS、MERFISH 或 seqFISH+ 的化学设计增加 backbone、readout 和 primer（`paper.md:365-380`）。

表达约束采用软惩罚。设原始分数为 (s_g)，第 (k) 个技术惩罚为 (p_{gk}\in[0,1])，则

$$
\tilde{s}_g=s_g\prod_k p_{gk}.
$$

过低或过高表达的基因不会被简单“一刀切”，而是通过平滑高斯衰减降低分数（`paper.md:284-287`）。代码中的 `apply_penalties()` 直接实现逐基因乘法（`selection_methods.py:68-90`）。

### 5. 第二步：PCA 候选池保留总体变化

Spapros 默认先选 100 个 PCA 基因。代码计算前 (J) 个主成分的绝对 loading 之和：

$$
s_g^{\mathrm{PCA}}=\sum_{j=1}^{J}|l_{gj}|.
$$

默认 (J=20)。之后再乘表达/设计惩罚并取高分基因（`selection_methods.py:93-193`）。

这个池的作用不是直接给出最终面板，而是尽量保留参考数据中的主变化轴。它能够捕获细胞状态梯度，但单独使用时不保证所有细胞类型都容易区分。

代码还提供一个可选的相关性惩罚：每选一个基因，就重新计算剩余基因与已选基因的最大绝对相关，并降低高度冗余基因的分数（`selection_methods.py:15-65`）。该功能不是默认配置。

### 6. 第三步：用浅层决策树建立细胞类型分类参考

Spapros 为每个细胞类型 (c) 建立一个二分类任务：

$$
c\quad\text{vs.}\quad\text{其他细胞类型}.
$$

默认参数与论文相符：

- 每个细胞类型训练 50 棵树；
- `max_depth=3`；
- 每类最多抽 1,000 个训练细胞和 3,000 个测试细胞；
- 各细胞类型均匀抽样；
- 每棵树使用不同训练抽样；
- 用宏平均 (F_1) 对树排序（`evaluation.py:1719-1815,1885-1975`）。

浅树有两个意义：一是降低过拟合，二是产生可解释的组合 marker 规则，而不是只输出一张基因排行榜。

#### 为什么还需要 secondary tree？

一个细胞类型可能总体分类不错，但会和某几个近邻类型混淆。论文用特异度

$$
s_c(r)=\frac{\mathrm{TN}_{c,r}}{N_r}
$$

衡量目标类型 (c) 对参考类型 (r) 的排除能力。如果某些参考类型特异度低，就只针对这些“难负样本”训练下一层树。代码默认总共运行三层 forest，即 primary 加两层 secondary（`evaluation.py:2145-2243`）。

### 7. 第四步：针对难区分类型做定向 DE

对于目标类型 (c)，如果某参考类型 (r) 满足

$$
s_c(r)<s_{\min}
$$

或者同时满足

$$
s_c(r)<\bar{s}_c-n_\sigma\sigma_c,
\qquad
s_c(r)<\bar{s}_c-\delta,
$$

它会被视为难区分参考。默认 (s_{\min}=0.9)、(n_\sigma=1)、(delta=0.02)（`selection_procedure.py:338-345`）。

随后算法在“目标类型 vs 难区分参考集合”上重新做 DE，加入新基因、重训森林，并重新检测难区分类型。停止条件包括：

- 已无低特异度参考；
- 同一组难参考重复出现；
- 达到最大迭代次数。

实现位于 `add_DE_genes_to_trees()`（`selection_methods.py:392-697`）。这样得到的 DE 森林可以看成“如果只追求细胞类型判别，当前候选池能达到的参考水平”。

### 8. 第五步：只补 PCA 池真正缺失的分类信号

接下来，PCA 候选池也训练同样的森林。对每个细胞类型比较 PCA 森林和 DE 参考森林：

$$
\Delta_c=f_c^{\mathrm{DE-ref}}-f_c^{\mathrm{PCA}}.
$$

当 (Delta_c>\tau) 时，从 DE 参考树中按特征重要性加入基因，然后重训。默认 (	au=0.02)，每轮最多加入 5 个基因（`selection_procedure.py:346`; `selection_methods.py:706-1009`）。

这一步是 Spapros 最关键的设计：

- 不把 PCA 和 DE 排名简单拼接；
- 不让 DE marker 完全挤掉连续变化基因；
- 只在某个细胞类型确实分类不足时，补入它需要的 DE 信号。

因此最终面板既保留总体变化，又满足已知细胞类型的最低分类要求。

### 9. 第六步：加入用户先验和 marker 覆盖

Spapros 区分两类先验：

- `preselected_genes`：强制优先，最终排名最靠前；
- `prior_genes`：加入候选池，但不具有同样的最终优先级。

文献 marker 列表还可以覆盖参考数据中不存在的细胞类型。对于参考中存在的类型，代码检查已选基因是否与 marker 的相关性超过默认阈值 0.5；数量不足时补 marker。对于参考中缺失的类型，直接从列表加入指定数量（`selection_procedure.py:930-965`; `selection_methods.py:1017-1095`）。

### 10. 第七步：最终排序

最终优先级大致是：

1. 强制预选基因；
2. 最优树中使用的基因；
3. 参考中缺失类型所需的 marker；
4. 参考中已有类型所需的 marker；
5. 其他树基因。

同一层内再看树特征重要性和 PCA 分数。最后取前 (n) 个（`selection_procedure.py:966-1184`）。

如果设置 `n_pca_genes=0`，就得到只强调细胞类型分类的 SpaprosCTo。代码提醒这种模式可能少于 (n) 个基因，需要重复运行补足（`selection_procedure.py:442-448,797-805`）。

### 11. 如何评价一个面板？

论文把评价拆成多组指标：

- **变化恢复**：粗/细 Leiden 聚类 NMI AUC、kNN 邻域重叠；
- **细胞类型恢复**：分类准确率、捕获细胞类型比例；
- **marker 对应**：marker 与面板基因的最大相关；
- **冗余性**：基因两两相关；
- **技术约束**：过低/过高表达、探针设计失败；
- **空间效用**：Moran’s (I) 与 NCEM CCI recovery。

例如聚类相似度使用

$$
{\rm NMI}(U,V)=\frac&#123;&#123;\rm MI}(U,V)}&#123;&#123;\rm mean}(H(U),H(V))},
$$

邻域相似度使用不同 (k) 下平均邻居交集的 AUC（`paper.md:197-236`）。包内 `ProbesetEvaluator` 实现聚类、kNN、分类、marker correlation 和 gene correlation 的调度（`evaluation/metrics.py:72-352`）。Moran’s (I) 和 NCEM CCI 的实现没有在本地包中找到。

### 12. 主要实验结果

- 解离参考指标与匹配 MERFISH 空间指标正相关：细胞类型与变化恢复分别为 (r=0.67) 和 (r=0.68)，细粒度聚类与空间变化为 (r=0.79)（Extended Data Fig. 3）。
- 在肺和心脏、50/150 基因、12 个数据集的比较中，Spapros 在作者定义的综合指标上总体领先；50 基因时与 geneBasis 的差异是一个统计学例外（`paper.md:135-161`）。
- Spapros 在细胞类型分类与变化恢复的二维空间中处于独特 Pareto 前沿位置，而不是每个单项指标都第一。
- 先选基因再删除不可设计探针的基因会显著损失性能；Spapros 因为提前做可行性过滤，保留更完整的面板（Fig. 4f）。
- 64 基因 SCRINSHOT 肺面板识别了目标细胞类型，并在 basal cell 内观察到与 *KRT15*–*S100A2* 层次轴正交的 *FOS* 空间梯度；邻近切片 IF 对 *FOS* 趋势提供了正交验证（Fig. 3；Extended Data Fig. 6）。

### 13. 代码与论文的一致性

本地 `theislab/spapros` 版本 0.1.6、commit `88f18b...` 对基因面板核心流程的支持较强：PCA、惩罚、DE、浅树、secondary forest、难参考优化、DE→PCA 补基因、marker 和最终排序都有直接实现。因此总体 fidelity 评为 **medium**，不是 high，原因有三点：

1. 论文写 DE 使用 *t*-test，本地代码固定为 Wilcoxon（`selection_methods.py:231-241`）；
2. 论文描述每次补两个 DE 基因、最多 12 次，而 `ProbesetSelector` 默认传入每次 1 个、3 次（`selection_procedure.py:338-345`）；
3. 探针序列设计、Moran’s (I)/NCEM、Snakemake benchmark 和论文制图位于其他仓库，不在当前 `code source`。

此外，构造函数虽然接收 `seed`，但该版本内部写成 `self.seed = 0`（`selection_procedure.py:348-419`）。

### 14. 使用时最需要注意的局限

- scRNA-seq 与空间测量的表达分布并不相同，平台、探针、分割和组织处理都会造成偏差；
- PCA 可能把 batch effect 当作主要变化；
- 参考中缺失的状态无法自动恢复，必须依赖先验 marker；
- 病理研究中最重要的微弱信号未必是最大方差，需要强制加入疾病相关基因；
- 论文空间实验样本量有限，不能证明这些空间梯度在人群中的发生频率；
- 完整复现需要 Spapros、Oligo Designer Toolsuite、`spapros-smk`、`spapros_reproducibility` 和多个公共数据源，单一本地包不够。

### 15. 一句话理解

Spapros 把“保留变化”当作主候选来源，把“细胞类型必须分得开”当作约束，再把探针可设计性和实验先验放进选择过程，因此比单纯 marker 排名或单纯方差排名更适合小型靶向空间转录组面板。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spapros — probe set selection for targeted spatial transcriptomics

### Problem

Targeted spatial transcriptomics measures only a limited, predefined gene panel. A good panel must recover known cell types, retain variation within cell types, avoid redundant or technically unsuitable genes, and contain genes for which specific oligonucleotide probes can actually be designed. Selecting marker genes alone can miss continuous states and novel spatial patterns; selecting high-variance genes alone can blur cell-type identities; designing probes only after gene selection can remove essential genes and collapse panel performance.

### Existing-method limitations

Prior methods largely optimize one side of the problem. Marker/classification approaches such as NS-Forest (*Genome Research*, 2021) and ActiveSVM/ASFS (*Nature Computational Science*, 2022) emphasize minimal cell-type discrimination. Variation-preserving approaches such as SCMER (*Nature Computational Science*, 2021), geneBasis (*Genome Biology*, 2021), and PERSIST (*Nature Communications*, 2023) preserve manifolds, reconstruct expression, or improve robustness, but do not jointly implement the paper’s full combination of cell-type recovery, general variation, expression constraints, and probe-design feasibility (`paper.md:470-506,560-573`). Basic PCA and DE also excel at different objectives rather than all of them (`paper.md:56-71`).

### Proposed method

Spapros is an end-to-end probe-set design framework with two linked components:

1. **Gene-panel selection.** It begins with a PCA-derived pool of variation-rich genes and an independently optimized DE/tree pool for cell-type discrimination. Shallow binary forests are trained for every cell type; when a PCA-based forest underperforms the DE reference for a cell type, high-importance DE-tree genes are imported and the forest is retrained. Mandatory genes, curated markers, and smooth expression/design penalties are integrated before a final ranked panel is capped at the requested size.
2. **Probe design.** Oligo Designer Toolsuite generates candidate oligonucleotides, filters sequence properties and off-targets, searches non-overlapping probe sets, removes genes with too few feasible probes, and constructs protocol-specific sequences for SCRINSHOT/HybISS, MERFISH, and seqFISH+ (`paper.md:347-380`).

The central innovation is the reconciliation step: PCA proposes genes that preserve broad transcriptional variation, while DE reference forests specify only the additional genes needed to recover difficult cell identities. The final trees also provide combinatorial annotation rules.

### Evaluation

The paper defines 12 metrics covering coarse/fine clustering similarity, neighborhood overlap, cell-type classification, percentage of captured cell types, marker correlation, gene redundancy, expression-constraint violations, and runtime. Dissociated-reference metrics translated positively to matched MERFISH data: cell-type and variation-recovery scores correlated with spatial counterparts at (r=0.67) and (r=0.68), and fine clustering similarity correlated with spatial variation at (r=0.79) (`paper.md:41-53`; Extended Data Fig. 3).

The large benchmark compared Spapros with ten recent gene-selection methods, PCA, DE, curated/manual panels, two tissues, panel sizes of 50 and 150 genes, bootstrap samples, and 12 datasets. Under the authors’ aggregate metric, Spapros was consistently the top or statistically indistinguishable top method; for 50 genes, geneBasis was the exception without a significant aggregate-score difference. SpaprosCTo led cell-type classification, while dedicated variation methods remained strongest on some variation-only metrics. Spapros occupied a distinct Pareto-optimal position by balancing both objectives (`paper.md:135-161`; Fig. 4 and Extended Data Figs. 4, 7, 8).

Probe feasibility materially affected results. Removing genes lacking adequate probes reduced alternative methods’ scores, whereas Spapros filtered feasibility before selection and retained the strongest aggregate performance (Fig. 4f; Extended Data Fig. 10).

### Experimental validation

The authors designed a 64-gene SCRINSHOT panel from a human lung scRNA-seq reference. In an intralobar section, the panel recovered all targeted cell types with anatomically plausible organization. Within tracheal basal cells, *FOS* showed a spatial gradient orthogonal to the *KRT15*–*S100A2* epithelial-layer axis, and adjacent-section immunofluorescence supported the *FOS* trend. Other selected genes showed within-type spatial differences in endothelial cells and macrophages (`paper.md:115-132`; Fig. 3 and Extended Data Fig. 6).

### Main limitations

- The method assumes dissociated scRNA-seq variation transfers to the spatial assay; modality effects, probe failures, segmentation, and older high-plex platform noise can break this assumption.
- Strong batch effects or dominant irrelevant variation can enter the PCA pool; disease-relevant subtle signals may require explicit priors.
- The spatial experimental validation used one sample from each of two lung regions and does not establish interindividual prevalence (`paper.md:509-515`).
- Rankings depend on the authors’ aggregate metric definition and benchmark preprocessing.
- The paper prose and package defaults differ in DE details: the paper states *t*-tests and a larger hard-reference refinement budget, while package version 0.1.6 uses Wilcoxon scores and shorter default refinement (`doc_code.md`).

### Reproducibility and code–paper match

**Reproducibility rating: 3/5.** The paper provides public data locations and separate public repositories for the Spapros package, Oligo Designer Toolsuite probe design, the Snakemake evaluation pipeline, and paper analyses (`paper.md:524-533`). The acquired `theislab/spapros` snapshot is version 0.1.6 at commit `88f18b0291f4e98482a3022edc270ed9644c37d9` and has **medium** overall paper-code fidelity.

Direct source inspection confirms the core gene-panel algorithm: PCA scoring, multiplicative constraints, balanced shallow forests, hard-reference DE refinement, DE-to-PCA gene transfer, marker coverage, final ranking, and the package’s main evaluation metrics. However, protocol-specific probe sequence design, Moran’s (I)/NCEM spatial metrics, Snakemake orchestration, and paper figure-reproduction scripts are outside the acquired repository. The package CLI’s `run_selection` path is also not the complete `ProbesetSelector` algorithm. A full paper reproduction therefore requires the other linked repositories and substantial public datasets, not this package alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
