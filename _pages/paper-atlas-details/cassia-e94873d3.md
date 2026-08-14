---
layout: default
permalink: /paper-atlas/cassia-e94873d3/
title: "CASSIA"
nav: false
wide: true
description: "单细胞 RNA 测序的细胞类型注释常常依赖合适的参考图谱，也需要研究者同时具备计算和领域知识。单轮提示的 LLM 方法，例如 Hou 和 Ji 在 Nature Methods 2024 报道的 GPTCelltype，虽然降低了使用门槛，但可能幻觉、不给出可审计的推理过程，也没有能提示低可信结果的质量分数。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>Nature Communications · 2026</span>
    </div>
    <h1>CASSIA</h1>
    <p>CASSIA: a multi-agent large language model for automated and interpretable cell annotation</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/ElliotXie/CASSIA" target="_blank" rel="noopener noreferrer" aria-label="Open code for CASSIA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CASSIA 方法解读

### 它要解决什么问题？

单细胞 RNA 测序的细胞类型注释常常依赖合适的参考图谱，也需要研究者同时具备计算和领域知识。单轮提示的 LLM 方法，例如 Hou 和 Ji 在 *Nature Methods* 2024 报道的 GPTCelltype，虽然降低了使用门槛，但可能幻觉、不给出可审计的推理过程，也没有能提示低可信结果的质量分数（`paper.md:25-34`）。

CASSIA（Collective Agent System for Single-cell Interpretable Annotation）把这个问题改写为一个可检查的多智能体流程：不是让一个模型一次给出标签，而是让不同角色分别做注释、核验、格式化、评分和报告。

### 输入和输出

输入是每个细胞簇的物种、组织、按重要性排序的 marker 基因，以及可选的实验条件信息。marker 通常来自 Seurat `FindAllMarkers` 或 Scanpy `rank_genes_groups`；论文建议多数任务使用前 50 个 marker（`paper.md:233-236,359-365`）。

输出不只是一个标签，还包括广义细胞类型、最可能的亚型及候选亚型、是否混合群体、注释和验证推理、0--100 质量分数、可选的一致性分数（CS）以及 HTML 报告。

### 核心流程

```text
物种 + 组织 + 排序 marker + 实验背景
                |
                v
            注释智能体
                |  功能 marker、细胞类型 marker、数据库核对、
                |  广义类型和三个亚型候选
                v
            验证智能体 <----- 失败时反馈并最多迭代 3 次
                |
                v
            格式化智能体 ----> 评分智能体（读取完整对话）
                |                     |
                +----------> 报告智能体 <----------+

可选：一致性/不确定性、Annotation Boost、RAG、子聚类
```

#### 1. 注释与验证

注释智能体扮演有单细胞经验的计算生物学家：先整理功能/通路 marker，再整理细胞类型 marker，交叉核对数据库和文献，然后输出广义类型、前三个亚型和摘要（`paper.md:239-256`）。验证智能体检查用于论证的 marker 是否真实出现在输入列表中、是否支持该类型；失败时给注释智能体具体反馈。最多三轮后，不论最终验证是否通过，结果都会被送去格式化（`paper.md:259-271`）。

#### 2. 质量评分

评分智能体读取完整对话，评价科学正确性、是否平衡使用多个 marker、是否过度依赖单个基因，并给出 0--100 分及理由（`paper.md:274-280`；`evaluation/scoring.py:83-239`）。论文用

$$\mathrm{Total\ cost}=(w\times\mathrm{FP})+\mathrm{FN}$$

选择低质量阈值，其中 $w=2$，得到约 75 分。低于 75 分的注释会被标记为值得进一步检查，常可进入 Annotation Boost。

#### 3. 多次运行的一致性（CS）

因为 LLM 有随机性，CASSIA 可重复运行，默认建议 5 次。每次注释给出一对 $(g,s)$：广义类型 $g$ 和最可能亚型 $s$。系统先用 Cell Ontology 和 LLM 统一不同写法，再计算：

$$\mathrm{CS}_{\mathrm{CL}}=\frac{1}{|R|(w_g+w_s)}\sum_{r\in R}\left[w_g I(g_r=g_c)+w_s I(s_r=s_c)+w_gw_s\{I(g_r=s_c)+I(s_r=g_c)\}\right].$$

最终 CS 取基于 Cell Ontology、基于 LLM 的统一，以及独立共识智能体三种分数的最小值；低于 75% 时被视为不确定（`paper.md:295-312`）。这不是概率校准保证，而是帮助发现不稳定、混合或低质量簇的实践指标。

#### 4. Annotation Boost

默认流程主要看排名 marker。对低分簇，Annotation Boost 改为读取完整差异表达统计量：校正 *p* 值、平均 log2 fold change、目标簇和背景的表达比例。它提出多个身份假设，查询更多 marker 统计证据，再保留或修改假设；最多五轮（`paper.md:329-332`）。可把它理解为“先宽搜索，再深验证”的循环，而不是简单重问同一个模型。

#### 5. RAG 与子聚类

面对冷门组织、复杂脑区或非模式物种，RAG 通过 marker 数据库、组织本体、层级特征和跨物种模块，把额外的生物学上下文注入注释提示（`paper.md:335-344`）。子聚类模块则同时看一组密切相关的子簇，帮助区分 T 细胞状态等细微差异（`paper.md:289-292`）。

### 论文结果应如何理解？

论文在 GTEx、Tabula Sapiens、HCL、MCA 和 Azimuth 的 970 个细胞类型上比较 CASSIA 与 GPTCelltype、ScType、SingleR、CellTypist、scCATCH 等方法，报告 CASSIA 在多数数据集上提升准确率（`paper.md:67-84,407-415`）。图 2 的曲线也直观看到约 50 个 marker 后收益趋于平缓。图 3 展示了“标签 + 推理 + 验证 + 评分”的完整报告；图 5 展示低分案例如何被 Boost 细化；图 6 展示 CS/质量分数可提示混合群体或低质量簇。

当前快照直接验证了 Python 的流程入口、评分、报告、Boost、RAG/reference 和多提供商调用代码；没有运行任何付费 LLM，也没有完整复现 970 个标签的基准。

### 代码对应与局限

Python 主入口是 `CASSIA/CASSIA_python/CASSIA/pipeline/pipeline.py:16-49` 的 `runCASSIA_pipeline`。它把批量注释、可选合并、评分、报告和 Boost 串起来（`pipeline.py:256-407`）；`core/llm_utils.py:246-700` 处理 OpenAI、Anthropic、OpenRouter 和自定义兼容端点。代码与论文默认流程总体高度一致，但补充材料中的完整系统提示、所有 CS 权重/调用分支以及一次性复现全部基准的脚本，在本次可验证范围内为 `Partial` 或 `Not found`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CASSIA Summary

### Problem

Single-cell RNA-seq annotation is often reference-dependent, laborious, inconsistent, and difficult to audit. Single-prompt LLM methods such as GPTCelltype can hallucinate, omit reasoning, and lose accuracy on fine-grained or rare populations (`paper.md:25-34`).

### Method

CASSIA is a modular multi-agent LLM framework. Users provide species, tissue, and ranked marker genes; an Annotator proposes evidence-backed general and subtype labels, a Validator checks marker consistency in a feedback loop, a Formatter structures the result, a Scoring agent assigns a 0--100 quality score from the full conversation, and a Reporter emits an interpretable HTML record (`paper.md:43-64,221-286`). Optional agents provide consensus uncertainty, Annotation Boost using full differential-expression statistics, joint subclustering, and retrieval-augmented reference context. The public Python package matches this orchestration through `runCASSIA_pipeline` (`CASSIA/CASSIA_python/CASSIA/pipeline/pipeline.py:16-49,256-407`).

### Evaluation

Across 970 cell types from GTEx, Tabula Sapiens, Human Cell Landscape, Mouse Cell Atlas, and Azimuth, the paper reports 12--41% relative gains in fully correct annotations and 9--20% gains in fully-or-partially correct annotations over the next-best method; average accuracy improved by >20% on most datasets (`paper.md:67-84`). The framework remained strong on cancer, PBMC/T-cell states, and non-model organisms: reported counts include 20/22 shark, 57/64 cat, 66/79 tiger, and 41/54 pangolin cell types (`paper.md:95-112`). Scores below 75 were predominantly erroneous/partial, while an independent 132-label test retained 97% of correct labels above the threshold (`paper.md:115-135`). Annotation Boost corrected 24/27 low-quality incorrect labels and preserved all 15 originally correct labels in its 42-case study (`paper.md:138-147`).

### Interpretation

The central contribution is workflow-level self-verification and auditability, not a newly trained cell encoder. The report exposes marker reasoning and confidence so users can inspect errors, mixed populations, or questionable gold standards. Figure 6 illustrates this use: low consensus plus high mitochondrial content flags poor clusters, while marker heatmaps challenge apparently incorrect reference labels (`figure_06.png`; `paper.md:150-184`).

### Reproducibility

Reproducibility is **4/5** for the default package workflow: the paper-linked GitHub snapshot is present at commit `7a77067f2af4ac89e68e8424a80ccd5e3dc8c334`, the Python pipeline, provider abstraction, scoring, reporting, boost, and reference modules are readable, and local figures are available. It is not 5/5 because no supplementary Markdown or live API execution is available here, benchmark source-data reproduction was not verified end-to-end, and the repository contains parallel/legacy copies. API keys, model availability, provider pricing, and external Cell Ontology/CellMarker services remain runtime prerequisites.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
