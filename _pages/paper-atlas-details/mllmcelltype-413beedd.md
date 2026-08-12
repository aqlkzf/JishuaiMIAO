---
layout: default
permalink: /paper-atlas/mllmcelltype-413beedd/
title: "mLLMCelltype"
nav: false
description: "mLLMCelltype 接收已经聚类的单细胞数据所产生的 marker gene 列表、物种和组织背景，让多个大语言模型分别注释各 cluster；对意见一致的 cluster 直接输出，对有争议者进行最多三轮、按 Toulmin 论证结构组织的讨论，再用共识比例和 Shannon entropy 报告模型间一致程度。 它不是从原始表达矩阵学习分类器，也不负责归一化、降维、聚类和差异表达。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>bioRxiv · 2025</span>
    </div>
    <h1>mLLMCelltype</h1>
    <p>Large Language Model Consensus Substantially Improves the Cell Type Annotation Accuracy for scRNA-seq Data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2025.04.10.647852" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## mLLMCelltype 方法解读：让多个 LLM 用 marker 证据讨论，而不是只投票

### 一句话定位

mLLMCelltype 接收已经聚类的单细胞数据所产生的 marker gene 列表、物种和组织背景，让多个大语言模型分别注释各 cluster；对意见一致的 cluster 直接输出，对有争议者进行最多三轮、按 Toulmin 论证结构组织的讨论，再用共识比例和 Shannon entropy 报告模型间一致程度。

它不是从原始表达矩阵学习分类器，也不负责归一化、降维、聚类和差异表达。Python/R 包的入口是“cluster → marker genes”，因此前序 Scanpy/Seurat 分析质量仍然决定证据上限。方法也不是外部知识库检索系统：论文阶段主要依赖各 LLM 参数中已有的生物知识，RAG/Cell Ontology 动态核验被列为未来方向。

### 为什么单个 LLM 不够

marker 注释需要同时识别谱系标志、组织特异状态和相近亚型的反例。单个模型可能掌握其中一部分，却因训练语料、提示敏感性和模型偏好给出不同答案。论文图 1a 用细胞类型和组织上的互补表现说明：GPT、Claude、Gemini 没有一个在所有类别都占优。

mLLMCelltype 的假设是，各模型的错误至少部分不相关；共享 marker 证据和相互反驳可以纠正个体偏差。这个假设并非总成立：若模型共享过时知识或同一语料偏差，完全一致也可能是“collective error”。因此一致性衡量的是模型间分歧，不是概率校准后的生物学真值。

### 输入准备：真正决定上限的前置步骤

论文从已经 QC、标准化和聚类的数据中，对每个 cluster 做差异表达，通常提供约 20–30 个 marker。组织、物种、发育阶段和疾病背景一起进入提示。层次注释时，还可加入 sister markers：目标 cluster 与同一父类下 sibling clusters 的差异基因，用于区分共享大谱系 marker 的近邻亚型。

发布库不替用户执行论文基准中的 Wilcoxon、log fold-change 和多重检验筛选。用户可以直接传入 marker 字典，也可以从 AnnData/Seurat 上游产生它。若 marker 被 housekeeping genes、ambient RNA、doublet 信号或错误聚类污染，多模型讨论只能重新解释这份证据，无法恢复未提供的表达信息。

### 第一阶段：多个模型独立初始注释

论文实验使用六个模型：GPT-4o、Claude 3.5 Sonnet、Claude 3.5 Haiku、Gemini 1.5 Pro、Gemini 2.0 Flash Experimental 和 Qwen2.5-Max。每个模型接收同一 cluster marker 与背景，独立返回细胞类型。独立运行的作用是保留初始多样性，避免后一个模型一开始就被前一个答案锚定。

当前 Python 包通过 provider abstraction 支持 OpenAI、Anthropic、Gemini、Qwen 以及更多后来加入的服务；`interactive_consensus_annotation()` 负责总编排，单模型调用落在 `annotate_clusters()` 和 `providers/`。这些扩展是本地 v2.0.4 软件快照的能力，不应反推为论文六模型实验的原始配置。

### 第二阶段：CP 与熵把分歧变成可检查信号

对某 cluster，设共有 $|L|$ 个模型，语义归一后支持多数标签的模型集合为 $M$。共识比例为

$$CP=\frac{|M|}{|L|}.$$

若六个模型中四个支持同一标签，则 $CP=4/6\approx0.667$。设不同标签比例为 $p_i$，Shannon entropy 为

$$\mathcal{H}=-\sum_i p_i\log_2p_i.$$

全体同意时 $CP=1$、$\mathcal{H}=0$；意见越均匀分散，熵越高。论文将 $CP\ge 0.667$ 且 $\mathcal{H}\le1$ 作为共识判据。当前 `interactive_consensus_annotation()` 默认 `consensus_threshold=0.7`、`entropy_threshold=1.0`，因此复现论文 4/6 判据需要显式传入 `2/3`。

“语义归一”很关键：Natural Killer cell 与 NK cell 可能是同一答案，简单字符串计数会夸大分歧。实现优先让 consensus checker LLM 解释标签并返回是否共识、CP、熵和最佳标签；若 API 调用或解析失败，`_deterministic_consensus_metrics()` 使用字符串频数和 `math.log2` 做确定性后备。后备可验证公式，却不能自动理解同义词，因此两条路径不完全等价。

### 第三阶段：争议 cluster 的 Toulmin 讨论

未达到 CP/熵阈值的 cluster 才进入讨论。首轮提示要求每个模型按六部分作答：

- CLAIM：明确细胞类型结论；
- GROUNDS：列出支持结论的具体 marker；
- WARRANT：解释 marker 如何连接到结论；
- BACKING：补充已知生物学依据；
- QUALIFIER：说明确定程度；
- REBUTTAL：回应替代解释或其他模型答案。

后续轮次把其他模型的论证和讨论历史提供给参与者，使模型能根据反证修正答案。每轮后由 consensus checker 再计算/解释共识；达到阈值就提前停止，否则最多运行三轮。代码的 `_run_cluster_discussion_rounds()` 明确执行 `range(1,max_discussion_rounds+1)` 和早停，`process_controversial_clusters()` 只处理争议集合。

Toulmin 格式的作用是让推理可审计并要求模型正面处理反例，而不是保证引用真实或消除幻觉。BACKING 仍可能由模型生成错误文献知识；最终专家应核对关键 marker、组织背景和罕见标签。

### consensus checker 是裁判，但不是生物学 oracle

论文描述由 Claude 3.5 Sonnet 承担共识检查。当前软件允许通过 `consensus_model` 显式指定 provider/model，并对模型名与 provider 做一致性校验；若未显式指定，则运行时解析可用 provider。这说明复现实验时不仅要固定六个参与模型，也要固定裁判模型、模型版本、temperature、提示模板和 API 时间点。

为了减少品牌偏见，讨论检查提示可把模型来源匿名化为 Model 1、Model 2 等。实现还包含重试、fallback、日志和结果合并逻辑。它会保留每模型初始答案、争议 cluster、各轮讨论、CP 和熵，便于把低一致 cluster 交给专家，而不是只留下一个无法追踪的最终标签。

### 图 1：应该怎样读方法图

图 1b–c 显示输入准备：cluster marker、组织背景和可选 sister markers。图 1d 让 GPT、Claude、Gemini、Qwen 对同一 myeloid cluster 独立给出 macrophage 或 dendritic cell。图 1e 展示三轮讨论：CD68/MARCO 支持 macrophage，CD11c 提供 DC 反例；加入 lung context、MARCO 与 CD206 共表达后，模型收敛到 alveolar macrophage。

这是说明机制的示例，不是对该 marker 组合的独立实验验证。图 1f 的共识增长展示框架期望的早停行为；真实数据上是否收敛、收敛是否正确仍取决于输入和模型。

### 图 2：性能比较的证据与边界

图 2a 报告 50 个数据集上的 full/partial annotation match，并显示 mLLMCelltype 相对 GPTCelltype 的提升；论文总结均值约 77.3% 对 61.3%。图 2b–c 把 thymus 和 lung atlas 的 reference、mLLMCelltype、GPTCelltype 与 cluster-level popV 标注映射到 UMAP，用于展示近邻发育状态和罕见肺细胞亚型的差异。

论文的 accuracy 不是所有错误等价：完全匹配计 1，Cell Ontology 层级中的部分匹配计 0.5，错配计 0，即

$$\mathrm{Accuracy}=\frac{N_{full}+0.5N_{partial}}{N_{total}}.$$

当前核心包未定位到生成全部 50 数据集结果、Ontology partial-match 评分和作图的完整代码；论文指向单独的 Reproducibility 仓库。因而图 2数字是论文证据，不能宣称已由本地核心包重跑验证。

### 扩展图告诉我们什么

扩展图 1–3把讨论轮次、共识与作者定义的 hallucination probability 联系起来，并显示模型数增加时平均准确率上升。它们支持多模型与迭代的经验关联，但“幻觉”的判定过程和校准需要基准代码/人工标签才能独立审计，不能仅用高 CP 自证低幻觉。

扩展图 4对 marker loss、housekeeping/random/wrong-marker injection 做扰动，论文报告多模型框架比 GPTCelltype 退化更慢；噪声越大，讨论轮数和 uncertainty flag 越多。该扰动实验代码在当前核心包中 Not found。

扩展图 5–8覆盖神经类器官、免疫 atlas、HLCA 层次注释、Drop-seq 与 snRNA-seq；扩展图 9显示 marker 数与 API 成本的折中，20–30 个是论文推荐区间；扩展图 10显示 sister markers 对近缘亚型有帮助。这些都是特定 benchmark 下的经验设置，不是所有组织的硬阈值。

### 当前代码与论文的 Exact / Partial / Not found

Exact 的核心包括：CP 和 Shannon entropy 的确定性实现；争议 cluster 筛选；最多三轮讨论和早停；Toulmin 六段提示；匿名化讨论、日志、重试与 fallback；多 provider 抽象。直接源码集中在 `python/mllmcelltype/consensus.py`、`prompts.py`、`annotate.py` 和 `providers/`。

Partial 包括：论文阈值约 0.667，而当前主 API 默认 0.7；论文指定六个历史模型与 Claude 裁判，当前 v2.0.4 支持更多模型并允许/需要运行时选择 consensus model；论文 v1.0.0 与当前包版本存在演化。旧元数据记录代码 commit `5f283a6`，但当前目录没有独立 `.git` 或 `.repo_source` 可核对完整 SHA，因此精确代码 provenance 只能保留为“recorded short commit”，不能伪造完整哈希。

Not found/External 包括：50 数据集统一 benchmark orchestration、Cell Ontology 评分、marker 扰动实验、全部论文作图脚本以及论文层次注释的完整自动调度。这些被论文指向单独 Reproducibility 资源，不能由核心包相似函数替代。

### 最容易误读的七个边界

1. 输入是 cluster markers，不是原始细胞矩阵；聚类错误会整体传递。
2. 不需要表达参考 atlas，不等于不需要先验；LLM 内部知识本身就是不可完全追踪的先验。
3. CP 与熵衡量模型一致性，不是预测正确概率；共享偏见可产生高 CP 错误。
4. discussion 增加 token 成本和提示依赖，不能保证模型真的获得新证据。
5. API 模型会更新，同一名称在不同时点可能改变；完整复现需锁定可访问版本与请求参数。
6. 敏感或临床结论必须回到 marker 表达、原始 cluster 和专家审查，不能只引用讨论文本。
7. 论文仍是 bioRxiv 预印本；基准设计和结论尚应按预印本证据强度解读。

### 直接证据入口

- OCR 论文：`paper source/paper/auto/paper.md`
- 原始/布局 PDF：`paper.pdf` 与 `paper source/paper/auto/paper_origin.pdf`
- 论文图：`paper source/paper/auto/images/`
- 当前 Python 实现：`mLLMCelltype_repo/python/mllmcelltype/`
- R 实现：`mLLMCelltype_repo/R/`
- 细粒度映射：`doc_code.md`；图证据：`figure_analysis.md`

本工作区没有独立 supplementary Markdown/PDF；OCR `paper.md` 已包含 Extended Data 和 Supplementary Information 清单。对于未进入本地的 Reproducibility 代码继续保留 External/Not found 标签。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## mLLMCelltype — Paper Summary

**Paper**: Large Language Model Consensus Substantially Improves the Cell Type Annotation Accuracy for scRNA-seq Data
**Authors**: Chen Yang, Xianyang Zhang, Jun Chen
**Preprint**: bioRxiv 10.1101/2025.04.10.647852 (April 2025)
**Code**: https://github.com/cafferychen777/mLLMCelltype

---

### Motivation & Novelty

#### Biological Problem

Cell type annotation — assigning biologically meaningful labels to clusters in scRNA-seq data — is a critical bottleneck in single-cell analysis. As datasets grow to millions of cells across diverse tissues, manual curation by domain experts has become intractable. The core challenge is integrating marker gene evidence with contextual knowledge about developmental lineages, tissue microenvironments, and cell type ontology relationships.

#### Limitations of Existing Methods

**Supervised/unsupervised methods** (SingleR, Nat. Immunol. 2019; scCATCH, iScience 2020; CellAssign, Nat. Methods 2019) require either reference datasets for transfer or database lookups, limiting generalizability to novel tissues and rare populations.

**Ensemble ML** (popV, Nat. Genet. 2024) integrates multiple algorithms but is purely data-driven with no biological prior knowledge. It requires pre-training on reference data and is computationally demanding (GPU/large RAM).

**Single-LLM methods** (GPTCelltype, Nat. Methods 2024) harness biological knowledge embedded in LLM weights, but are subject to individual model biases, inconsistent reasoning, and no meaningful uncertainty quantification.

#### Unique Contributions

1. **Multi-LLM consensus**: First framework to systematically combine multiple LLMs via structured deliberation rather than simple majority vote.
2. **Toulmin argumentation**: Uses the academic argumentation framework (CLAIM-GROUNDS-WARRANT-BACKING-QUALIFIER-REBUTTAL) to force models to cite evidence and rebut alternatives, structurally suppressing hallucination.
3. **Calibrated uncertainty**: CP and Shannon entropy provide per-cluster confidence that identifies ambiguous cases requiring expert review.
4. **Hallucination mitigation**: Cross-model deliberation actively corrects errors that single LLMs make confidently.
5. **No reference data needed**: Unlike popV, mLLMCelltype requires no pre-training or reference datasets — only API access.
6. **Modular and extensible**: New LLMs can be seamlessly added; supports Python and R with Scanpy/Seurat integration.

---

### Method Overview

mLLMCelltype implements a **collective intelligence framework** with three phases:

#### Phase 1: Parallel Initial Annotation
Six LLMs (GPT-4o, Claude-3.5-Sonnet, Claude-3.5-Haiku, Gemini-1.5-Pro, Gemini-2.0-Flash-Exp, Qwen2.5-Max) independently annotate all clusters from the same marker gene + tissue context input. This phase produces 6 independent annotation maps.

#### Phase 2: Consensus Detection
For each cluster, annotations are semantically normalized (e.g., "NK cells" = "Natural Killer cells") and consensus metrics computed:
- **CP** (Consensus Proportion): fraction of LLMs supporting the majority annotation
- **H** (Shannon entropy): diversity of predictions across models
- Clusters with CP ≥ threshold AND H ≤ threshold proceed directly to output

#### Phase 3: Iterative Deliberation (controversial clusters only)
Clusters failing consensus undergo structured debate:
- Each LLM submits a Toulmin-structured argument citing specific marker genes as evidence
- All models see all arguments (full information sharing)
- Consensus Checker LLM evaluates agreement after each round
- Deliberation continues up to 3 rounds; early exit when consensus reached
- If no consensus after 3 rounds → flagged as ambiguous with complete reasoning chain

**Key architectural assumptions**:
- LLM diversity approximates complementary biological knowledge — errors are model-specific, not universal
- Structured argumentation constrains hallucination better than unconstrained generation
- Consensus quantifies reliability; disagreement signals genuine biological ambiguity

---

### Evaluation

#### Benchmark Datasets

| Category | Datasets | Cells | Source |
|----------|---------|-------|--------|
| Multi-tissue atlases | Tabula Sapiens, HCL, MCA | Millions | UCSC, figshare |
| Cross-tissue | GTEx cross-tissue | — | GTExportal |
| Lung | HLCA, LCA | 2.4M+ | CELLxGENE |
| Thymus | Developmental human thymus atlas | 250,000+ | CELLxGENE |
| Neural | HNOCA (neural organoids) | 1.7M | CELLxGENE |
| Immune | Lifespan immune atlas | ~220 donors | Synapse |
| Cancer | BCL, colon (GSE132465), lung (GSE131907) | — | Zenodo, GEO |
| Other tech | Drop-seq (HLCA subset), snRNA-seq | — | HLCA |

#### Key Results

**vs. GPTCelltype (Nat. Methods 2024)**:
- Mean accuracy across 50 datasets: **77.3% vs 61.3%** (+15%)
- Prostate(GTEx): 86.0% vs 48.0% (+38%)
- Esophagus(GTEx): 87.3% vs 52.5% (+34.8%)
- Lung(GTEx): 84.8% vs 52.2% (+32.6%)
- HNOCA (post-training-cutoff data): 96.45% vs 83.95%
- Lifespan immune atlas: 78.0% vs 65.3%

**vs. popV (Nat. Genet. 2024)**:
- Thymus atlas: +10.6% improvement
- Lung Cell Atlas: +13.17% improvement

**Robustness to marker gene noise**:
- Major cell types: >90% accuracy up to 30% noise level
- mLLMCelltype accuracy decline: 4.5% per 10% housekeeping injection (vs. GPTCelltype's 8.5%)
- mLLMCelltype advantages largest for rare populations (9.5% vs 16% decay rate)

**Hierarchical annotation** (HLCA):
- 89% accuracy at Level 3; 98% parent-level consistency
- Sister markers improved accuracy by 4.8%

**Optimal parameters**: 20-30 marker genes per cluster balances accuracy and API cost.

**Technology generalizability**: 95% accuracy on Drop-seq; robust on snRNA-seq.

#### Evaluation Metric

Weighted accuracy using Cell Ontology term hierarchy:
- Full match (identical terminology): 1.0
- Partial match (shared CL ancestry): 0.5
- Mismatch (divergent): 0.0

---

### Reproducibility

**Rating: 3.5/5**

**Strengths**:
- Clean Python and R packages, MIT license, easy pip/devtools install
- Comprehensive unit tests (Python: 13 files; R: 9+ files)
- Good documentation with tutorials and examples
- Support for 10 LLM providers via modular design
- Complete output including per-model predictions and deliberation logs for transparency

**Limitations**:
- **Benchmark evaluation code is not in the main repo**: Scripts to reproduce the 50-dataset comparison, perturbation experiments, and figure generation are in a separate "Reproducibility" repository (referenced in the paper but not directly available from the GitHub link).
- **API costs**: Reproducing full benchmarks requires API keys for 4+ providers and estimated $50–200 depending on dataset scale.
- **Default threshold mismatch**: The paper states 66.7% consensus threshold, but the code defaults to 70%. Reproducing paper results requires manually setting `consensus_threshold=2/3`.
- **No hardcoded consensus checker**: Paper says Claude-3.5-Sonnet is default; code uses first available API key. Results may vary if users have different key ordering.
- **Preprocessing not included**: Standard Scanpy preprocessing (normalization, clustering, DE) must be done by user.

**Environment setup**:
```bash
pip install mllmcelltype
# Set API keys in .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
QWEN_API_KEY=...
```

**Common pitfalls**:
1. Not setting `consensus_threshold=2/3` when reproducing paper results
2. API rate limits with parallel multi-model calls — built-in retry handles transient failures
3. LLM pricing changes — paper's cost estimates may be outdated
4. For large atlases (>2M cells), Leiden clustering can produce 100+ clusters — batch manually in groups of 30-50

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
