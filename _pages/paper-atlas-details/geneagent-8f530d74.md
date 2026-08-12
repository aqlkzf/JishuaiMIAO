---
layout: default
permalink: /paper-atlas/geneagent-8f530d74/
title: "GeneAgent"
nav: false
description: "基因集分析的目标，是给一组看起来共同发挥作用的基因找到一个合适的生物学功能解释。传统的 GSEA 等富集分析依赖 GO、MSigDB 等人工整理数据库，优点是证据清楚，缺点是常常只能返回已有的数据库术语；如果一个基因集只和已知功能弱相关，传统方法就不容易给出新的、可解释的功能命名。普通 LLM 可以根据背景知识生成更自然的功能名称和分析文字，但也可能编造看似合理、实际没有证据支持的内容，即 hallucination。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>GeneAgent</h1>
    <p>GeneAgent: self-verification language agent for gene-set analysis using domain databases</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02748-6" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GeneAgent 方法中文解读

### 这篇论文要解决什么问题？

基因集分析的目标，是给一组看起来共同发挥作用的基因找到一个合适的生物学功能解释。传统的 GSEA 等富集分析依赖 GO、MSigDB 等人工整理数据库，优点是证据清楚，缺点是常常只能返回已有的数据库术语；如果一个基因集只和已知功能弱相关，传统方法就不容易给出新的、可解释的功能命名（`paper.md:18-24`）。普通 LLM 可以根据背景知识生成更自然的功能名称和分析文字，但也可能编造看似合理、实际没有证据支持的内容，即 hallucination（`paper.md:24-30`）。

GeneAgent 的核心思路是：保留 GPT-4 生成解释的能力，但不要直接相信初始回答；让一个自验证模块主动访问生物医学数据库，把生成结果拆成 claim，再用数据库证据支持、部分支持或反驳这些 claim，最后根据验证报告修改和总结输出（`paper.md:30-41`）。

### 输入、输出和符号

论文把输入基因集记为：

$$D=\&#123;&#123;{g}_{i}|}_{i=1}^{N}\}$$

其中每个 `g_i` 是一个基因名。GeneAgent 的输出是：

$$\mathrm{GeneAgent}(D)=(P,A)$$

`P` 是代表性的生物学过程名称，`A` 是解释这些基因功能的分析文本。评估时还会有人工整理的 ground truth 功能术语 `G`（`paper.md:237-240`）。

关键中间变量包括：

| 符号 | 含义 |
|---|---|
| `P_ini` | GPT-4 初始生成的过程名称 |
| `A_ini` | GPT-4 初始生成的分析文本 |
| `R_P` | 针对过程名称 claim 的验证报告 |
| `P_mod`, `A_mod` | 根据 `R_P` 修改或保留后的过程名称和分析文本 |
| `R_A` | 针对修改后分析文本 claim 的验证报告 |
| `P`, `A` | 最终过程名称和最终分析文本 |

论文没有提出新的训练损失函数。GeneAgent 更像一个带工具调用和证据回写的 LLM 工作流，而不是一个重新训练的深度学习模型。

### 整体流程

```text
输入基因集 D
   |
   v
1. Generation
   GPT-4 生成初始过程名称 P_ini 和分析文本 A_ini
   |
   v
2. Self-verification for process name
   把 P_ini 转成 claim，调用数据库验证，得到 R_P
   |
   v
3. Modification
   根据 R_P 保留或修改 P_ini/A_ini，得到 P_mod/A_mod
   |
   v
4. Self-verification for analytical narratives
   对 A_mod 中的基因功能 claim 再验证，并再次检查过程名称，得到 R_A
   |
   v
5. Summarization
   根据 R_A 汇总，输出最终 P 和 A
```

论文文字把 GeneAgent 概括为四个模块：generation、self-verification、modification、summarization（`paper.md:237-240`）。但从实际流程看，self-verification 会发生两次：第一次检查过程名称，第二次检查修改后的分析文本并再次检查过程名称（`paper.md:249-255`）。图 1 也清楚显示了 self-verification 和 modification 之间的迭代结构，以及最终 summarization 输出 final process name 和 final analytical narratives（`figure_01.png`）。

### 第一步：Generation

输入基因集 `D` 会被逗号分隔后放入 generation prompt。GPT-4 根据 prompt 生成初始生物学过程名称 `P_ini` 和初始解释文本 `A_ini`（`paper.md:243-249`）。论文说明详细 prompt 在 Supplementary Document 1 中，但该补充文档没有作为 markdown 被当前工作区获取，所以不能从本地文本复原完整 prompt（`paper.md:570-573`）。

当前获取到的代码仓库可以部分对应这一环节。`query_llm_for_analysis.py` 会读取基因集表格、切分基因列表、生成 prompt、调用模型后端，并把 LLM name、analysis、score 写入输出表（`llm_evaluation_for_gene_set_interpretation/query_llm_for_analysis.py:94-175`）。`utils/prompt_factory.py` 中的 prompt 会要求模型写出关键生物过程分析、给出简短过程名称并附置信分数（`llm_evaluation_for_gene_set_interpretation/utils/prompt_factory.py:62-154`）。但是这只能证明“LLM 基因集命名/解释”代码存在，不能证明完整 GeneAgent cascade 存在。

### 第二步：selfVeri-Agent 验证过程名称

GeneAgent 会从 `P_ini` 生成一组 claim，例如“这些基因 involved in 某个过程”。selfVeri-Agent 从 claim 中抽取基因符号和过程名称，选择合适 API，访问领域数据库，然后生成 `R_P`。`R_P` 里包含 evidence 和 decision，decision 类型包括 supported、partially supported、refuted（`paper.md:249-252`）。论文 Box 1 还定义了 claim、curated function、verification report 等概念（`paper.md:77-92`）。

selfVeri-Agent 使用四类 Web API 访问 18 个数据库（`paper.md:258-278`）：

| API | 论文中的用途 |
|---|---|
| g:Profiler | 调用 GO、KEGG、Reactome、WikiPathways、Transfac、miRTarBase、CORUM、HPO 等数据库做富集分析，返回 top enrichment terms |
| Enrichr | 调用 KEGG_2021_Human、Reactome_2022、BioPlanet_2019、MSigDB_Hallmark_2020 等 pathway 数据库 |
| E-utils | 访问 NCBI Gene 和 PubMed，为单个基因功能提供信息 |
| AgentAPI | 作者自建 API，涉及 gene-disease、gene-domain、PPI、gene-complex 等数据库 |

图 1c 用 ERBB2/ERBB4/FGFR2/FGFR4/HRAS/KRAS 与 RTK signaling 的 claim 举例，显示 selfVeri-Agent 会在 g:Profiler、Enrichr、E-utils、AgentAPI 和领域数据库之间选择证据来源，最后报告该 claim 不能被确认（`figure_01.png`）。图 3 进一步显示过程名称验证主要依赖 Enrichr/g:Profiler，分析文本验证更多依赖 E-utils/AgentAPI（`figure_03.png`）。

当前代码仓库只部分支持这一机制。`utils/reference_checker.py` 能从段落中提取基因和功能关键词，调用 MyGene 做符号规范化，用 Entrez 搜 PubMed，并让 LLM 判断题目或摘要是否支持段落（`llm_evaluation_for_gene_set_interpretation/utils/reference_checker.py:13-122`, `llm_evaluation_for_gene_set_interpretation/utils/reference_checker.py:230-313`, `llm_evaluation_for_gene_set_interpretation/utils/reference_checker.py:418-510`）。但它不是论文中完整的 selfVeri-Agent：没有直接看到 claim list builder，也没有看到 supported/partially supported/refuted 三分类 report assembler。

### 第三步：Modification

Modification 是 GeneAgent 区别于普通“检查一下答案”的关键环节。它会根据 `R_P` 判断是否需要修改初始过程名称。如果 `P_ini` 被判定需要修改，`A_ini` 也会同步调整：

$$\mathrm{GeneAgent}_{m}(P_{\rm ini},A_{\rm ini},\mathcal{R}_{P})=(P_{\mathrm{mod}},A_{\mathrm{mod}})$$

这一阶段把数据库证据真正反馈到答案生成中，而不是只做事后评分（`paper.md:252-253`）。在当前获取的 `idekerlab/llm_evaluation_for_gene_set_interpretation` 仓库中，没有找到可直接验证这一状态转移的源码或 notebook 片段。

### 第四步：第二次自验证

修改后，GeneAgent 会对 `A_mod` 中不同基因及其功能名称生成 claim，再次调用 selfVeri-Agent 验证，并且会再次检查修改后的过程名称。最终得到第二份报告 `R_A`（`paper.md:252-253`）。这解释了图 1 中 self-verification 与 modification 的迭代结构。

当前仓库中的 reference checking 工具可以检查段落与 PubMed 证据是否匹配，但没有直接证据显示它被组织成 GeneAgent 第二轮自验证流程。因此这一阶段在代码层面应标记为 Not found，而不是 Partial。

### 第五步：Summarization

最后，GeneAgent 根据 `R_A` 对 `P_mod` 和 `A_mod` 做总结，输出最终 `P` 和 `A`：

$$\mathrm{GeneAgent}_{s}(P_{\mathrm{mod}},A_{\mathrm{mod}},\mathcal{R}_{A})=(P,A)$$

论文说最终输出会整合中间验证报告（`paper.md:55-60`, `paper.md:255-255`）。当前仓库没有找到可验证的 summarization prompt、报告整合函数或最终 GeneAgent output writer。

### 评估设计

论文主要用三类自动指标和一类人工评估：

1. **ROUGE**：比较生成名称和 ground truth 名称的 token 重叠，包括 ROUGE-1、ROUGE-2、ROUGE-L。论文给出了 ROUGE-N 和 ROUGE-L 的公式（`paper.md:279-291`）。这些是评估公式，不是训练目标。
2. **MedCPT 语义相似度**：把生成名称 `P` 和 ground truth `G` 用 MedCPT 编码为 embedding，再算 cosine similarity（`paper.md:294-300`）。
3. **背景语义相似度分布**：把生成名称与 12,320 个候选术语逐一比较，看 ground truth pair 在所有候选中的百分位排名（`paper.md:301-304`）。
4. **人工检查 selfVeri-Agent decision**：随机抽取 10 个 NeST 基因集共 132 个 claim，让人工判断 GeneAgent decision 是否 correct、partially correct 或 incorrect（`paper.md:319-327`）。

当前代码仓库有相似但不完全一致的语义相似度实现。`semanticSimFunctions.py`、`run_omics_sem_sim.py`、`rank_GOterm_LLM_sim_rand.py` 会用 SapBERT 相关模型计算 embedding、cosine similarity 和背景排名（`llm_evaluation_for_gene_set_interpretation/semanticSimFunctions.py:10-41`, `llm_evaluation_for_gene_set_interpretation/run_omics_sem_sim.py:1-53`, `llm_evaluation_for_gene_set_interpretation/rank_GOterm_LLM_sim_rand.py:58-155`）。论文方法写的是 MedCPT，因此这里只能算评估思路的部分匹配。

### 主要结果

论文报告 GeneAgent 在 GO、NeST、MSigDB 三类数据上相对 GPT-4 baseline 有更高 ROUGE 和语义相似度。比如 MSigDB 中 ROUGE-L 从 0.239 +/- 0.038 提升到 0.310 +/- 0.047，ROUGE-2 从 0.074 +/- 0.030 提升到 0.155 +/- 0.044（`paper.md:104-110`）。图 2 中 GeneAgent 的 ROUGE 柱状图整体高于 GPT-4，语义相似度分布也更靠上（`figure_02.png`）。

self-verification 的证据也很强。论文报告 15,903 个 claim 中 99.6% 成功得到验证；成功验证的 claim 中 84% supported、1% partially supported、8% refuted、7% unknown。16% claim 不被支持，分布在 794 个基因集，其中 703 个后续被修改（`paper.md:157-174`）。图 3 显示了这些验证类别、API/数据库使用频率和人工检查结果（`figure_03.png`）。

在 MSigDB enrichment-term test 中，把 GeneAgent verification report 当作 gene synopsis 时，精确匹配准确率为 80.7%，高于 SPINDOCTOR ontological synopsis 的 68.8% 和无 synopsis 的 56.0%（`paper.md:145-148`, `figure_02.png`）。这说明验证报告不仅用于判断初始回答，还能作为更有信息量的基因功能摘要。

### 与代码的对应关系和复现限制

这次工作区中的代码不是论文官方 GeneAgent 仓库。论文明确写到 GeneAgent 代码发布在 `https://github.com/ncbi-nlp/GeneAgent/`，并且有 Supplementary Code 1（`paper.md:366-369`, `paper.md:576-579`）。但当前获取到的是 `https://github.com/idekerlab/llm_evaluation_for_gene_set_interpretation`，其 README 标题和引用都指向早一篇 “Evaluation of large language models for discovery of gene set function”（`llm_evaluation_for_gene_set_interpretation/README.md:1-6`, `llm_evaluation_for_gene_set_interpretation/README.md:186-188`）。

因此，代码匹配结论应保持保守：

- **可以直接验证的部分**：LLM 基因集命名 prompt、OpenAI/Gemini/server 模型调用、输出解析、PubMed reference checking、SapBERT 风格语义相似度、GO 背景排名、Jaccard/coverage/enrichment 评估工具。
- **没有直接验证的核心 GeneAgent 部分**：完整 selfVeri-Agent claim -> report -> modification -> summarization cascade、AgentAPI、masking strategy、最终 GeneAgent source workflow。
- **缺失证据**：Supplementary Documents 1-5 没有获取成 markdown，Supplementary Code 1 和官方 `ncbi-nlp/GeneAgent` 源码不在当前工作区。

换句话说，这个工作区足够理解论文方法，也能检查相关的旧评估代码；但不能从当前代码复现完整 2025 Nature Methods GeneAgent 系统。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## GeneAgent Summary

GeneAgent addresses a common problem in gene-set analysis: LLMs can produce useful biological process names and explanatory narratives, but they may also hallucinate plausible claims that are not supported by curated biological knowledge. The paper frames this as a limitation of both conventional enrichment analysis, which is constrained by predefined database terms, and plain GPT-4 prompting, which lacks autonomous fact verification (`paper.md:18-30`, `paper.md:101-110`).

The proposed method is a GPT-4-based language agent for gene-set annotation. Given a gene set `D`, GeneAgent outputs a process name `P` and analytical narratives `A`, formally described as `GeneAgent(D) = (P, A)` (`paper.md:237-240`). Its pipeline has generation, self-verification, modification and summarization stages. The key novelty is the selfVeri-Agent: it turns raw outputs into claims, extracts genes and process terms, queries domain-specific databases through g:Profiler, Enrichr, E-utils and AgentAPI, and produces verification reports with supported, partially supported or refuted decisions (`paper.md:243-278`). Figure 1 visually confirms this cascade and the iteration between self-verification and modification (`figure_01.png`).

The evaluation covers 1,106 gene sets from GO, NeST and MSigDB, plus a seven-gene-set melanoma case study. GeneAgent improves ROUGE and semantic-similarity metrics over GPT-4 with Hu et al. prompts; for MSigDB, ROUGE-L improves from 0.239 +/- 0.038 to 0.310 +/- 0.047, and ROUGE-2 improves from 0.074 +/- 0.030 to 0.155 +/- 0.044 (`paper.md:104-110`). Semantic similarity also improves across the three datasets, and GeneAgent produces more names in high-percentile background similarity bands (`paper.md:124-139`). Verification reports are useful as gene synopses: exact-match enrichment-term accuracy reaches 80.7% with verification reports compared with 56.0% without a synopsis and 68.8% with SPINDOCTOR ontological synopsis (`paper.md:145-148`, `figure_02.png`).

The self-verification evidence is substantial at the paper/figure level. The paper reports 15,903 claims, 99.6% successful verification, 84% supported, 1% partially supported, 8% refuted and 7% unknown among successful reports, with 703 of 794 potentially revision-worthy gene sets modified (`paper.md:157-174`). Figure 3 shows API/database usage split between process-name and analytical-narrative verification, and a human-checking heatmap where most sampled decisions are correct (`figure_03.png`). Extended Data Fig. 4 supports the full cascade by showing better scores than process-name-only or narrative-only verification (`figure_07.jpg`).

Reproducibility from this workspace is limited by a code-source mismatch. The paper states that GeneAgent code is released at `https://github.com/ncbi-nlp/GeneAgent/` and as Supplementary Code 1 (`paper.md:366-369`, `paper.md:576-579`), but the acquired repository is `idekerlab/llm_evaluation_for_gene_set_interpretation`, whose README describes the earlier paper “Evaluation of large language models for discovery of gene set function” (`llm_evaluation_for_gene_set_interpretation/README.md:1-6`, `llm_evaluation_for_gene_set_interpretation/README.md:186-188`). Direct code reads verify related prompt-generation, model-calling, semantic-similarity, enrichment-overlap and PubMed-reference-checking utilities, but not the end-to-end GeneAgent self-verification -> modification -> summarization cascade.

Code-paper match assessment: **low for the 2025 GeneAgent implementation**, **partial for reused evaluation machinery**. The workspace is strong enough to explain the paper method and inspect related baseline/evaluation code, but not to reproduce the full GeneAgent system without the official `ncbi-nlp/GeneAgent` source, Supplementary Code 1, and Supplementary Documents 1-5 for exact prompts, verification-report schemas and API-call details.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
