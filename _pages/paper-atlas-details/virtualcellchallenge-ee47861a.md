---
layout: default
permalink: /paper-atlas/virtualcellchallenge-ee47861a/
title: "VirtualCellChallenge"
nav: false
wide: true
description: "《Virtual Cell Challenge: Toward a Turing test for the virtual cell》不是一个新虚拟细胞模型的论文，也不是已经完成并公布排行榜的 benchmark-results paper。它是一篇前瞻性 challenge/position article：作者解释为什么需要社区竞赛，并给出 2025 年首届挑战的任务、数据生成方案、数据切分和三类评价指标。"
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
      <span>Representation Models</span>
      <span>Cell · 2025</span>
    </div>
    <h1>VirtualCellChallenge</h1>
    <p>Virtual Cell Challenge: Toward a Turing test for the virtual cell</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2025.06.008" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for VirtualCellChallenge">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Virtual Cell Challenge 中文解读：怎样为“虚拟细胞”设计一场可检验的比赛

### 1. 这篇文章是什么，不是什么

《Virtual Cell Challenge: Toward a Turing test for the virtual cell》不是一个新虚拟细胞模型的论文，也不是已经完成并公布排行榜的 benchmark-results paper。它是一篇前瞻性 challenge/position article：作者解释为什么需要社区竞赛，并给出 2025 年首届挑战的任务、数据生成方案、数据切分和三类评价指标。

因此，这里的“方法”是基准设计方法，而不是神经网络架构。文章没有提供可供逐行映射的模型仓库，也没有比较参赛算法；本地工作区同样没有代码目录。正确的阅读目标是理解：挑战究竟要求预测什么、怎样限制泛化场景、如何生成测试数据，以及三类指标为什么要组合使用。

### 2. “虚拟细胞”愿景如何被缩成一个可测任务

广义虚拟细胞希望模拟细胞在遗传、药物和环境变化下的行为，最终还可能覆盖蛋白、表观遗传、时空和多细胞系统。这样的目标太大，无法用一次比赛完整检验。

首届 Virtual Cell Challenge 把问题缩成：

> 已知未扰动的 H1 人胚胎干细胞状态，并给出部分基因敲低在 H1 中的实测响应，模型能否预测其余单基因 CRISPRi 扰动在 H1 中造成的单细胞转录变化？

输入至少包含：未扰动 H1 参考表达、训练扰动的 H1 单细胞谱，以及公共数据中同一或相关扰动在其他细胞背景的观测。输出是每个待测扰动后的基因表达预测，随后与完全独立生成的实验真值比较。

图 1A 用两个细胞背景说明这件事：在 context 1 中已经看到扰动 $p_i$ 从状态 A 到 A'；在 context 2 中，模型要推断同一扰动后的未知状态。它不是“生成一张看起来像细胞的表达矩阵”，而是要求预测特定干预所导致的状态变化。

### 3. 泛化轴：为什么不是纯 zero-shot

文章把虚拟细胞的泛化拆成两个主要轴：

1. **跨细胞背景泛化**：细胞类型、细胞系、培养条件、遗传背景，以及体内/体外环境变化；
2. **跨扰动泛化**：未见过的遗传或化学扰动，以及它们的组合。

首届挑战主要考查第一个轴：目标 H1 hESC 是新的细胞背景，但待预测的基因扰动在其他公共细胞背景中至少有过观测。图 1B 可读作“扰动 × context”的矩阵：浅蓝是已观测条目，白色是缺失条目，H1 列中的深蓝是需要预测的条目。

作者明确认为，在现有公共遗传扰动数据只覆盖少数细胞系的情况下，真正跨新细胞状态的 zero-shot 还不成熟。因此比赛提供 H1 中 150 个扰动作为训练样例，让参赛者进行 few-shot adaptation，再预测 H1 中的其余扰动。

这是一项务实选择，但也限定了结论：比赛测到的是“给目标 context 少量标定数据后的迁移能力”，不能直接宣称模型已经学会对任意新细胞做零样本模拟。

### 4. 数据如何从大筛选变成高质量测试集

#### 4.1 第一阶段：广而浅的候选筛选

作者先在 H1 hESC 中进行约 2,500 个 CRISPRi 扰动的低深度单细胞功能基因组筛选。这个阶段的目的是覆盖更多基因，估计每个扰动的响应强度和表达变化形态，而不是直接作为最终真值。

#### 4.2 选择 300 个扰动

候选扰动按下游差异表达效应大小分箱，同时兼顾两项标准：

- 用聚类最大化响应形态的多样性，避免测试集只包含相似通路或相似效应；
- 尽量与已有公共扰动数据重叠，使参赛模型可以利用其他 context 的信息做迁移。

这里存在一个有意设计的张力：公共数据重叠提高任务的现实性和可学习性，但也使数据泄漏、基因身份记忆和 split 透明度变得格外重要。文章只描述原则，没有给出完整基因清单和具体泄漏审计规则。

#### 4.3 第二阶段：窄而深的参考测量

选出的 300 个基因在 H1 中重新进行高深度 10x Genomics Flex 测量，形成约 30 万个单细胞 profile。图 1D 报告：

- 每个扰动约 1,000 个细胞；
- 约 93,000 reads/cell；
- 约 50,000 gene UMIs/cell。

正文把 Flex 的理由概括为可扩展、固定细胞有助于降低批次效应，并能获得更好的 residual knockdown efficiency。这个“两阶段漏斗”比直接拿现有杂合数据做排行榜更重视测试真值的覆盖深度和可重复性。

### 5. 训练、验证与最终测试如何隔离

300 个 H1 扰动被拆成：

| 数据部分 | 扰动数 | 约单细胞数 | 用途 |
|---|---:|---:|---|
| Training | 150 | 150,000 | 比赛启动时发布，供 H1 few-shot 适配 |
| Validation | 50 | 50,000 | 驱动 live leaderboard，允许开发期迭代 |
| Test | 100 | 100,000 | 最终评分的 held-out 扰动 |

最终排名仅根据 100 个 held-out 扰动。文章还说 test 数据在提交截止前一周释放；这意味着公平性不仅依赖标签隐藏，也依赖提交规范、可执行时间窗和对外部数据使用的规则。文章没有收录这些完整运营细则，复现实务必须以挑战门户当期规则为准。

训练资源还包括 Arc Virtual Cell Atlas 的 scBaseCount、Tahoe-100M，以及与测试扰动有重叠的公共 Perturb-seq / 化学基因组数据。这些数据帮助模型学习跨 context 的扰动效应，但它们与 H1 高深度真值的实验平台和细胞背景不同，域偏移本身正是挑战的一部分。

### 6. 为什么要同时使用三种指标

图 1C 把指标放在“生物学可解释性—全局表达精度”的轴上。三项指标各自回答不同问题。

#### 6.1 Differential expression score

第一项检查模型能否预测真实扰动产生的差异表达基因。它最接近实验生物学家通常关心的输出：哪些基因上调、哪些下调，以及哪些变化足够显著。

它的弱点是容易受到共同应激反应或高频 DE 基因影响。一个总是预测训练集中最常见 DE 基因的朴素模型，可能得到看似尚可的分数，却没有学会区分具体扰动。

#### 6.2 Perturbation discrimination score

第二项比较某个预测与各个真实扰动响应的相似度排序：正确扰动是否比其他扰动更接近预测。它主要检验“扰动身份”是否保留，而不只看响应幅度。

它能惩罚所有扰动都输出同一平均答案的模型。不过，模型也可能在 latent space 中区分扰动，却无法产生可靠的基因级 DE 列表，所以该指标不能单独代表实验替代价值。

#### 6.3 Mean absolute error

第三项在所有基因上计算预测表达与真实表达的平均绝对误差：

$$
\mathrm{MAE}=\frac{1}{G}\sum_{g=1}^{G}|\hat x_g-x_g|.
$$

它覆盖未显著差异表达的多数基因，提供全局误差视角。弱点是大量基本不变的基因可能主导总体分数，使预测“接近平均细胞”也显得不错。

#### 6.4 组合而不是三选一

文章计划构造 combined score，并对每个分量设置最低阈值，同时单独公布每项排名。这种设计试图防止模型只优化一个容易利用的指标。

但文章没有给出 differential expression score、perturbation discrimination score 的精确数学公式，也没有给出组合权重和最低阈值。因此，本文可以解释指标逻辑，却不能据此实现官方 scorer。任何精确复现都必须查阅挑战门户的实际版本；不能凭文章概念自行补全公式后称为官方实现。

### 7. 图 1 四个面板怎样连成完整合同

- **A：挑战目标**——输入初始状态和扰动，输出扰动后的细胞状态。
- **B：泛化结构**——从其他 contexts 与 H1 的少量已观测扰动，补全 H1 的 held-out 扰动响应。
- **C：评价结构**——DE、扰动区分和所有基因 MAE 共同约束模型。
- **D：证据结构**——2,500 基因的广筛选选择 300 个多样扰动，再用高深度实验形成 150/50/100 的比赛切分。

四个面板分别规定“预测什么、在哪里泛化、怎样判分、真值如何生成”。这也是这篇短文最接近正式 benchmark contract 的部分。

### 8. “Toward a Turing test”应怎样理解

标题借用 Turing test，是希望建立一个外部、盲测、可重复的标准：如果模型产生的扰动响应足够接近真实实验，它在这个任务上就表现得像一个可用的“虚拟细胞”。但首届挑战远不是对完整细胞行为的总体验证：

- 只测转录组，不测蛋白、表观遗传、形态或功能表型；
- 只测单基因 CRISPRi，不测组合扰动；
- 目标 context 只有 H1 hESC；
- 主要是 few-shot context generalization；
- 只比较固定时间点的群体/单细胞表达，不覆盖动态、空间或多细胞环境。

因此更准确的说法是：它建立了“虚拟细胞转录扰动预测”的首个受控测试场，而不是一次通过就证明模型与真实细胞等价。

### 9. 与既有挑战和数据资源的关系

文章把 CASP 视为组织范式：持续生成盲测数据、公开比较、逐年调整标准，可以让领域围绕可测目标迭代。它还指出两个直接前身：Cancer Immunotherapy Data Science Grand Challenge 预测 T 细胞的较粗表型变化；2023 NeurIPS-Kaggle 比赛预测免疫细胞的化学扰动表达变化。首届 Virtual Cell Challenge 改为基因 CRISPRi，并强调新细胞背景中的基因级响应。

scPerturb、Perturb-seq、scBaseCount、Tahoe-100M 等资源既提供训练素材，也暴露了平台差异、重复性不足和 context 覆盖有限的问题。挑战的价值不只是给模型排位，还在于用 purpose-built、深测序的 held-out H1 数据检验这些资源上学到的表示是否能真正迁移。

### 10. 尚未被本文解决的问题

1. **官方评分细节**：精确公式、权重和门槛不在文章中。
2. **基因清单与泄漏规则**：文章给出 split 大小，没有给出完整扰动身份及外部数据审计办法。
3. **批次与对照建模**：Flex 和固定流程旨在降低批次效应，但文章没有把批次校正纳入明确评分合同。
4. **不确定性**：指标评价点预测，没有要求预测置信区间或细胞间分布的不确定性。
5. **机制解释**：高预测分数不自动意味着学到了正确调控机制；模型可能利用相关性、共享应激或 context shortcuts。
6. **挑战结果**：文章发布时没有参赛模型、排行榜、胜出方法或事后分析，不能用它支持“某类模型已经最好”的结论。

### 11. 未来路线

作者希望后续扩展到组合扰动、跨细胞类型、更多生物模态、时间和空间维度，以及逆向设计——给定期望状态，寻找能够达到该状态的干预。每次扩展都需要新的真值和指标：例如组合扰动要区分加性与相互作用，动态任务需要多时间点，逆向设计还要考虑多解、安全性和实验可实施性。

文章最重要的观点不是某一个指标，而是评价标准也必须与模型共同演化：每年用新实验数据做真正 held-out 的检验，公开模型在哪些 context 和响应类型上失败，再反向改进数据生成、指标和方法。

### 12. 证据与代码边界

| 项目 | 本地证据 | 状态 |
|---|---|---|
| 首届任务、few-shot H1 context generalization | `paper.md` Task 段与图 1B | Source-grounded |
| 三类评价指标的概念与互补性 | `paper.md` Evaluations 段与图 1C | Source-grounded |
| 2,500 → 300 的数据生成漏斗 | `paper.md` Datasets 段与图 1D | Source-grounded |
| 150/50/100 切分 | 正文与图 1D | Source-grounded |
| 精确官方 scoring functions / weights / thresholds | 文章未提供 | Not found |
| 具体扰动基因清单与完整竞赛规则 | 文章未提供 | Not found |
| 参赛模型结果或排行榜 | 本文是赛前设计文章 | Not applicable / Not found |
| 论文配套实现仓库 | `paper.md` 与 acquisition sidecars 未链接 | Not found |

综上，这篇文章应按 paper-only challenge/review 合同理解。它给出了一个严谨但范围有限的“虚拟细胞”测试框架；本地不存在可以被诚实描述为该论文方法实现的代码，因此不创建 `doc_code.md`，也不伪造代码—论文 Exact 对应。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Virtual Cell Challenge: Toward a Turing Test for the Virtual Cell

**Authors**: Yusuf H. Roohani et al.
**Journal**: Cell | **Year**: 2025 | **DOI**: 10.1016/j.cell.2025.06.008
**Type**: Position / challenge-design article
**Route**: reviewerpaper paper-only analysis

---

### Review Scope

This Cell article announces and motivates the Virtual Cell Challenge, an annual open competition for evaluating AI models that predict cellular responses to perturbations. Its scope is not a new algorithm or codebase. It defines why virtual-cell models need standardized tests, proposes an initial task around genetic perturbation response prediction in H1 human embryonic stem cells, and describes a new Arc Institute benchmark dataset plus evaluation metrics. The article targets model developers, perturbation-screening researchers, and benchmark organizers.

The paper is short and programmatic: it covers one challenge design, one main figure, 18 references, and a small number of benchmark components rather than a broad survey of many algorithms.

### Field Landscape

The paper places virtual cells in a long arc from first-principles whole-cell simulation in the late 1990s and early 2000s to modern single-cell perturbation modeling. Earlier efforts were limited by sparse data, simplifying assumptions, and computational constraints, while current single-cell profiling and machine learning make the goal plausible again [paper.md:20]. The authors argue that the missing piece is not only model capacity but also a shared evaluation infrastructure [paper.md:22].

The historical analogy is CASP: protein structure prediction advanced through recurring community benchmarks, and the authors want a comparable mechanism for predictive cell-state models [paper.md:22]. They distinguish the proposed challenge from prior competitions: the Cancer Immunotherapy Data Science Grand Challenge assessed broad T-cell phenotype shifts, and the 2023 NeurIPS-Kaggle competition focused on chemical perturbations, while this challenge centers genetic perturbation effects at gene-expression resolution [paper.md:28].

### Method Taxonomy

The article's taxonomy is a benchmark-design taxonomy:

| Dimension | Options / components | Paper evidence |
|---|---|---|
| Generalization target | Biological context, novel perturbations, combinations | The paper names context and perturbation generalization as the two core axes [paper.md:38]. |
| First challenge task | Few-shot context generalization to H1 hESC | Participants predict held-out single-gene perturbations in H1 after seeing a subset of H1 perturbations [paper.md:40-42]. |
| Prediction output | Post-perturbation counts and DE gene sets | These are named as the core outputs of in silico perturbation experiments [paper.md:46]. |
| Metrics | Differential expression score, perturbation discrimination score, MAE | The three metrics are introduced as complementary readouts [paper.md:46-50]. |
| Dataset split | 150 training genes, 50 validation genes, 100 final test genes | The H1 benchmark split is reported in the dataset section [paper.md:58]. |
| Training resources | Arc Virtual Cell Atlas and selected public perturbation datasets | The paper names these as additional training resources [paper.md:54-66]. |

### Key Findings

1. The central claim is that virtual-cell models need an open, recurring benchmark to determine whether they capture generalizable biology rather than dataset-specific artifacts [paper.md:26].

2. The inaugural task intentionally avoids a pure zero-shot setting. The authors argue that true zero-shot generalization to new cell states is likely premature because published perturbation datasets cover only a few cell lines; the first challenge therefore uses few-shot adaptation in the held-out H1 hESC context [paper.md:42].

3. Genetic perturbations are emphasized because their targets are precise and causal, even though transcriptional effects may be subtle and hard to predict [paper.md:28].

4. The metric set is designed to catch different failure modes: a model can score well on common DE genes while failing perturbation discrimination, or distinguish perturbations in embedding space while failing to produce useful DE gene sets [paper.md:48].

5. The benchmark dataset is intentionally higher depth than a broad screen: about 300,000 scRNA-seq profiles across 300 CRISPRi perturbations, with median about 1,000 cells per perturbation and more than 50,000 UMIs per cell [paper.md:58].

### Open Problems

1. **Metric specification and weights.** The article states the three metric families and says a combined score with minimum thresholds will be used, but it does not provide exact formulas, weights, or calibration rules [paper.md:50].

2. **Generalization scope.** The first task tests context generalization to one held-out H1 hESC setting. That is realistic and measurable, but it is still far from broad claims about virtual cells across cell types, modalities, time, and multicellular systems [paper.md:74].

3. **Leakage and overlap.** The challenge maximizes overlap with existing perturbation datasets to support training [paper.md:58, paper.md:66]. That makes few-shot learning feasible, but the challenge must carefully define train/test boundaries.

4. **Modality expansion.** Future virtual-cell benchmarks need transcriptomic, proteomic, epigenetic, temporal, spatial, and multicellular readouts; the current article names this target but does not yet define those tasks [paper.md:74].

5. **Inverse perturbation design.** The authors identify the inverse task, choosing perturbations to achieve a desired cellular effect, as therapeutically important, but this remains a future challenge direction [paper.md:74].

### Benchmark Component Comparison Table

| Method / resource | Year | Journal / venue | Category | Key innovation | Limitations | Data types |
|---|---:|---|---|---|---|---|
| E-CELL | 1999 | Bioinformatics | Whole-cell simulation | Early software environment for whole-cell simulation | Historical first-principles models were limited by data and assumptions | Mechanistic cell models |
| The Virtual Cell software | 2001 | Trends Biotechnol. | Computational cell biology | Software environment for quantitative cell biology | Not a modern data-driven perturbation benchmark | Mechanistic models |
| CASP | ongoing | Prediction Center | Community benchmark | Recurring open benchmark that catalyzed protein-structure prediction | Protein structure differs from cell behavior complexity | Protein structures |
| Cancer Immunotherapy Grand Challenge | not specified | Topcoder | Public competition | Phenotype-shift prediction in T cells | Did not evaluate gene-expression response resolution | T-cell phenotypes |
| NeurIPS-Kaggle perturbation benchmark | 2024 | NeurIPS Datasets and Benchmarks | Public competition | Transcriptomic response prediction to chemical perturbations across cell types | Chemical perturbations have less precise targets than genetic perturbations | scRNA-seq chemical perturbation |
| Virtual Cell Challenge | 2025 | Cell | Benchmark proposal | Few-shot prediction of genetic perturbation effects in held-out H1 hESC context | Initial task is one cell context and exact scoring details are outside the article | scRNA-seq CRISPRi |
| New H1 CRISPRi benchmark dataset | 2025 | Cell article / Arc | Dataset | 300 perturbations, about 300,000 profiles, high cell coverage and sequencing depth | Gene lists and raw files are not in the article Markdown | 10x Flex scRNA-seq |
| Arc Virtual Cell Atlas | 2025 | Arc resource | Training resource | scBaseCount plus Tahoe-100M, over 350 million cells and counting | External resource; data composition evolves | Observational and perturbational scRNA-seq |
| scPerturb | 2024 | Nature Methods | Harmonized data resource | Standardized single-cell perturbation data | Existing datasets still vary in reproducibility | Perturbation scRNA-seq |
| Perturb-seq landscape | 2022 | Cell | Public perturbation atlas | Information-rich genotype-phenotype mapping | Cell contexts and platforms differ from the challenge setting | Perturb-seq |
| PerturBench | 2024 | arXiv | Benchmark reference | Perturbation discrimination metric framing | Preprint; not itself the challenge dataset | Perturbation model evaluation |
| Tahoe-100M | 2025 | bioRxiv | Perturbation atlas | Giga-scale single-cell perturbation atlas | Preprint at article publication | Perturbation scRNA-seq |

### Reproducibility and Publishability

The analysis is paper-only. No code repository is linked in the article or acquisition sidecars. The acquired paper Markdown, XML, one main figure, evidence ledger, and review outputs are sufficient for publish prep. Remaining gaps are benchmark-rule gaps in the paper itself, not missing analysis work.

### What This Paper Does Not Establish

This article should not be read as evidence that a particular virtual-cell model works. It does not benchmark submitted models, report leaderboard results, compare architectures, or validate a learned simulator. Its empirical contribution is the design and description of the inaugural H1 hESC benchmark dataset and competition framing. Therefore, any downstream claim such as "model X passes the Virtual Cell Challenge" must come from later challenge results, not from this paper.

The article also does not prove that success on the first challenge is equivalent to a full virtual-cell Turing test. The first task tests a narrow but important slice of the vision: few-shot genetic perturbation response prediction in one cell context. The authors themselves frame broader capabilities, including combinatorial perturbations, cross-cell-type generalization, multimodal modeling, temporal and spatial dimensions, multicellular systems, and inverse design, as future directions [paper.md:74].

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
