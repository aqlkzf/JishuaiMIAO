---
layout: default
permalink: /paper-atlas/cellvoyager-48482658/
title: "CellVoyager"
nav: false
description: "CellVoyager 不是新的细胞表示模型或统计检验，而是一套“研究问题生成—代码执行—结果解释—动态重规划”的智能体工作流。它读取已处理的 .h5ad、研究背景和作者已经做过的分析，提出一个不重复的探索假设，在持续存在的 Jupyter kernel 中逐步运行代码，并依据输出决定下一步；一个分析完成后，它把摘要加入历史，避免后续假设重复。"
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
      <span>Nature Methods · 2026</span>
    </div>
    <h1>CellVoyager</h1>
    <p>CellVoyager: AI CompBio agent generates new insights by autonomously analyzing biological data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03029-6" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellVoyager：自主提出并执行单细胞分析的计算生物学智能体

### 一句话理解

CellVoyager 不是新的细胞表示模型或统计检验，而是一套“研究问题生成—代码执行—结果解释—动态重规划”的智能体工作流。它读取已处理的 `.h5ad`、研究背景和作者已经做过的分析，提出一个不重复的探索假设，在持续存在的 Jupyter kernel 中逐步运行代码，并依据输出决定下一步；一个分析完成后，它把摘要加入历史，避免后续假设重复。

论文关注的不是“LLM 会不会按指令画 UMAP”，而是更困难的问题：当研究者已经完成一批分析后，智能体能否自主找到遗漏但有科学意义的方向，并把方向落实为可检查的 notebook。

### 1. 输入与最终产物

主要输入有三类：

- 已处理的单细胞 AnnData 数据；
- 一份论文或背景报告，其中包含生物问题和既往分析；
- 可用 Python 环境及包信息。

预处理阶段把 `adata.obs`、`adata.var`、`obsm`、`layers` 等结构转换成文本摘要，并把论文总结为生物背景、已执行分析和数据集描述。智能体不直接把整个表达矩阵塞进 LLM；矩阵留在 Python/Jupyter 中，LLM 看到元数据摘要并通过生成代码访问真实对象。

每条探索轨迹输出一个独立 notebook，其中交替记录：假设与计划、代码、执行输出、图像、错误修复、结果解释和更新后的方向。多条轨迹结束后可形成报告。这个 notebook 是审计载体，但“代码成功执行”仍不保证分析设计、统计单位和因果解释正确。

### 2. 两阶段工作流

#### 阶段 1：生成 exploration blueprint

智能体基于以下上下文生成结构化计划：

- `adata_summary`：数据字段与样例值；
- `paper_txt`：生物背景和论文既往分析；
- `past_analyses`：此前已尝试轨迹的摘要；
- 可选 deep-research 背景；
- 编码与单细胞分析规范。

输出包含假设、分步分析计划、第一步 Python 代码、代码说明和简短摘要。`past_analyses` 是关键设计：它使第 $n$ 条轨迹显式知道前 $n-1$ 条已经探索什么，从而把“新颖性”变成 prompt 中的可执行约束，而不是事后人工去重。

#### 阶段 1.5：自我批评

初稿不是立即执行。critic 角色检查：

- 与原论文和既往轨迹是否重复；
- 假设是否聚焦且生物学相关；
- 分析步骤是否在剩余预算内；
- 第一段代码是否符合规范；
- Scanpy 函数参数是否与检索到的文档一致。

随后第二次调用把反馈合并回结构化计划。论文只采用一轮 critique，因为更多轮没有明显收益且增加成本。代码中的 `critique_step()` 与 `incorporate_critique()` 直接实现这两次调用。

### 3. 阶段 2：在 notebook 中执行、解释和重规划

对每个分析步骤，legacy 流程执行：

1. 写入说明 markdown 与代码 cell；
2. 在同一 Jupyter kernel 中运行代码；
3. 若失败，向 LLM 提供代码、错误、最近代码上下文和函数文档，最多修复 $F=3$ 次；
4. 若成功，把文本和 PNG 输出交给 GPT-4o 解释；
5. 将解释写回 notebook；
6. 结合当前结果重新规划剩余步骤；
7. 直到达到最多 $T=8$ 步或分析完成。

持续 kernel 很重要：后续步骤可以直接复用前面生成的子集、评分和图，而无需每轮重载数据。另一方面，它也带来隐式状态风险：某个变量可能来自早期失败或被覆盖的 cell，单看最后一段代码未必能完整复现。

论文图 1把一个完整实验写成 $N$ 条探索轨迹，每条最多 $T$ 步，每步最多 $F$ 次修复。这里的“自主”是有严格预算和 prompt 护栏的自主，不是无限循环。

### 4. 错误修复并不是验证科学正确性

代码执行失败时，系统会截取错误尾部、相关代码、最近五个 code cell 和文档片段，让模型返回修正版。补充图 1显示执行成功率在三次修复左右趋于饱和，因此默认 $F=3$。legacy executor 对单个 cell 使用 300 秒 timeout；长时间的 scVI 训练、轨迹推断或大规模差异分析可能超时。

修复环主要处理语法、API、变量和运行时错误。它不能自动发现以下科学错误：

- 把细胞而不是 donor 当独立重复；
- 在同一数据上筛选再检验而没有校正；
- 混淆 association 与 causation；
- 用不合适的归一化层或批次变量；
- 在过小子群上做不稳定推断。

COVID-19 案例正好说明这个边界：专家要求把 cell-level 比较改为按 donor pseudobulk，智能体接受反馈后才得到更严谨的分析。人类反馈不是装饰，而是控制伪重复等风险的重要环节。

### 5. 函数文档检索的真实范围

论文描述智能体检查单细胞函数文档。当前 `get_documentation()` 用 AST 找函数调用，但实际只解析 `sc.*`/`scanpy.*`；scvi-tools、celltypist、SciPy 等调用不会自动得到同等文档支持。legacy executor 的 `AVAILABLE_PACKAGES` 字符串只列出 scanpy、anndata、matplotlib、numpy、seaborn、pandas、scipy，虽然环境文件还包含更多包。

因此“文档增强”应理解为对常用 Scanpy API 的局部保护，而不是任意生物信息学库的实时、完备 API 验证。

### 6. CellBench 实际测量了什么

CellBench 收集 76 篇以 scRNA-seq 数据分析为主的论文。对每篇论文，策展流程提取背景和原作者实际执行的独立分析。测试时模型只看到背景，提出分析方案；LLM judge 判断提案是否命中 held-out 的作者分析。

这测量的是“在给定背景下，能否猜到一篇论文可能会做哪些合理分析”，不是：

- 在真实数据上代码是否运行；
- 结论是否正确；
- 是否发现论文之外的新生物学；
- 是否比专家完成更完整的统计审计。

论文报告 CellVoyager(o3-mini) 的 micro/macro accuracy 约 79.0%/80.3%，基础 o3-mini 约 60.5%/61.6%，基础 GPT-4o 约 55.2%/55.6%。相对基础 GPT-4o 和 o3-mini，论文分别报告提高 23.8% 和 18.5%。消融提示显式分析计划和编码规范贡献明显。26 篇论文被刻意选为晚于模型训练 cutoff 至少一年，前后 cutoff 组未见显著性能差异；这降低了直接记忆论文的疑虑，但不能完全排除训练数据或任务模板偏差。

judge 仍是 LLM。论文用两名博士研究者在子集上核对，报告约 89% 和 85% 一致率；这说明自动评分可用但不是完美金标准。

### 7. 三个真实案例与证据强度

每个案例先生成八条分析，再按成功执行 cell 比例选出五条给两名博士研究者评估，其中一名是原论文作者。这个筛选有现实意义，也会偏向容易运行的分析；不能把入选的 15 条当作随机样本估计智能体总体成功率。

#### COVID-19 PBMC：焦亡信号

智能体比较 apoptosis 与 pyroptosis gene scores，并在专家反馈后按 donor pseudobulk。它发现 COVID-19 患者 CD8+ T 细胞 pyroptosis score 更高（原案例 $P=0.001$），并在两个独立数据集中复核（$P=0.002$、$P=0.038$）。

这是一条有外部数据支持的表达签名发现，但 gene-module score 表示“更富集焦亡相关转录程序”，不等于直接观测到细胞发生焦亡。

#### 子宫内膜图谱：旁分泌信号

智能体探索月经周期中 stromal fibroblast 与其他细胞的 ligand–receptor 表达相关，专家建议从少数 pair 扩展到 40 个组合。结果突出 TGFβ 和 FGF2–FGFR1 等候选通路。图 5展示的是跨 donor/周期的表达相关与候选通信，不是配体结合或功能阻断实验。

#### 脑衰老：转录噪声

智能体计算不同细胞型的单细胞转录噪声，报告 oligodendrocyte、microglia、mural cells 等随年龄增加，并在独立数据中验证部分模式。该指标容易受测序深度、零膨胀、细胞周期和批次影响；论文案例提供重复数据支持，但仍需要对技术噪声定义保持谨慎。

图 3汇总专家评价：15 条入选分析的平均创造性约 3.03/4，12/15 的假设被认为值得进一步研究。专家评价支持“生成值得检查的假设”，不是对全部结论的实验确认。

### 8. 六张主图的逻辑

- 图 1：输入、blueprint、自我批评、执行—修复—解释—重规划循环。
- 图 2：CellBench 的策展与命中率，回答“规划结构是否优于直接问基础 LLM”。
- 图 3：专家对三个案例的创造性、生物相关性、方法正确性和后续价值评价。
- 图 4：COVID-19 pyroptosis 分析及 donor-level 修订和外部数据复核。
- 图 5：子宫内膜月经周期中的 fibroblast ligand–receptor 候选关系。
- 图 6：脑衰老不同细胞型的 transcriptional noise 与验证集结果。

前三图评估系统，后三图展示系统可能产生的科学发现。二者不能互换：CellBench 高分不直接证明病例结论正确；病例中的有趣结论也不证明所有自动分析都可靠。

### 9. 当前代码与论文版本的对应

| 论文机制 | 本地代码 | 状态 |
|---|---|---|
| 初始结构化 blueprint | `cellvoyager/hypothesis.py` | Exact |
| critic 与反馈合并 | 同上 | Exact |
| `past_analyses` 防重复 | `agent.py` + prompt 模板 | Exact |
| Jupyter code execution 与 300 秒 timeout | `execution/legacy.py` | Exact |
| 最多三次修复 | `execution/legacy.py` | Exact |
| GPT-4o 解释文本和图像 | `execution/legacy.py` | Exact（论文路径） |
| 动态 next-step replanning | `execution/legacy.py` | Exact |
| CellBench base/agent/judge | `CellBench/` | Exact/Partial |
| 论文 o3-mini 默认 | 当前 CLI 默认 `claude-sonnet-4-6` | 版本差异 |
| 论文 legacy 执行器 | 当前 CLI 默认 Claude Agent SDK 模式 | 版本差异 |
| AnnData 前十个 unique 值 | 当前摘要默认 cutoff 25 | Partial |
| Scanpy/scvi-tools/celltypist 可用描述 | legacy package 字符串遗漏后两者 | Partial |

仓库新增了 LiteLLM/instructor 多模型路由、Claude Agent SDK、MCP Jupyter 工具、Streamlit GUI、交互暂停/恢复和 seeded hypothesis。这些是论文之后的工程扩展，不应反向写成论文实验使用过的机制。

### 10. 可复现论文结果的实际要求

若目标是复现论文而不是运行最新版，应至少固定：

1. 论文指定的 o3-mini checkpoint 和中等 reasoning effort；
2. legacy Jupyter execution mode；
3. GPT-4o 图像解释器；
4. 论文 prompt、$T=8$、$F=3$ 和一轮 critique；
5. 相同 `.h5ad`、论文摘要与既往分析文本；
6. 多个重复运行，因为 LLM 输出非确定；
7. CellBench 的 judge checkpoint 与评分 prompt。

当前代码目录嵌在 PaperCode checkout 中，不是独立 Git 仓库；旧合同记录的上游 commit 无法由当前本地 Git 元数据核验。

### 11. 最重要的使用边界

第一，CellVoyager 产生“可执行候选分析”，不是自动同行评审。任何新发现都应核对统计单位、协变量、多重检验和外部验证。

第二，背景报告与 `past_analyses` 决定新颖性的参照系。如果既往分析摘要遗漏，智能体可能把已做工作误认成创新。

第三，CellBench 是分析意图匹配 benchmark，不是端到端数据分析 benchmark。它不能衡量代码失败、数据污染或错误统计结论。

第四，病例展示经过成功执行率筛选并有人类反馈；真实无人值守运行的平均质量可能更低。

第五，论文结果对应特定模型版本，而当前默认模型与执行模式已经变化。比较或复现时必须报告实际模型、prompt、运行日期、执行模式和随机重复。

### 源证据入口

- 主论文：`paper source/paper/auto/paper.md`
- 补充材料与完整 prompts：`output_paper_supp_md/paper_supp1/auto/paper_supp1.md`
- 主图：`paper source/paper/auto/images/`
- 规范代码：`CellVoyager/cellvoyager/`
- 论文一致路径：`CellVoyager/cellvoyager/execution/legacy.py`
- 当前 CLI：`CellVoyager/run_cellvoyager.py`
- 论文—代码映射：`doc_code.md`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellVoyager — Summary

### Motivation & Novelty

Single-cell RNA sequencing data harbors a vast space of possible analytical hypotheses, but researchers typically explore only a narrow subset constrained by time, expertise, and analytical preconceptions. While LLM-based agents have shown promise in scientific coding and hypothesis generation, existing approaches either respond to user prompts in isolation or lack domain-specific capabilities for single-cell analysis. Google's Data Science Agent in Colab, for example, struggled with scRNA-seq data manipulation and produced superficial analyses.

CellVoyager introduces a domain-specialized AI agent that **autonomously generates and executes scRNA-seq analyses that complement a researcher's prior work**. Unlike CellAgent (an LLM multi-agent framework for scRNA-seq; *ICLR*, 2026), SCassist (an AI workflow assistant; *Bioinformatics*, 2025), and SpatialAgent (for spatial biology; *bioRxiv*, 2025), CellVoyager uniquely: (1) explicitly conditions on the researcher's past analyses to prevent redundancy and find complementary insights; (2) operates within a live Jupyter notebook for transparent, reproducible workflows; and (3) includes a self-critique mechanism that retrieves function documentation to verify correct API usage. The system generates "exploration blueprints" (hypothesis + step-wise analysis plan + code) and iteratively executes and refines them based on intermediate results.

### Method Overview

CellVoyager is a two-phase agentic framework built on large language models (o3-mini for code generation, GPT-4o for visual interpretation):

**Phase 1 — Idea Generation**: Given a processed scRNA-seq dataset and a paper/report describing prior analyses, the agent generates an exploration blueprint containing a hypothesis, a step-wise analysis plan, and Python code for the first step. The plan undergoes a self-critique cycle where the LLM identifies weaknesses and refines the approach, using retrieved scanpy function documentation to verify correct API usage.

**Phase 2 — Iterative Execution**: The blueprint is executed within a fixed Jupyter kernel (scanpy, scvi-tools, anndata, seaborn, scipy). Each step involves: (1) code execution; (2) error handling with up to $F = 3$ fix attempts; (3) VLM-based interpretation of text and image outputs; and (4) adaptive replanning based on results. This loop repeats for up to $T = 8$ steps per analysis, and the full process runs for $N$ independent analyses.

Key architectural components include: redundancy prevention via accumulated analysis history, structured JSON output via instructor/litellm, optional deep research for biological background retrieval, and a complete Streamlit GUI for interactive monitoring. See `doc_method.md` for detailed algorithm walkthrough and `doc_code.md` for implementation mapping.

### Evaluation

#### CellBench Benchmark

CellBench evaluates analysis prediction across 76 published scRNA-seq studies (659 total analyses). Given only a paper's biological background section, the agent proposes analyses; an LLM judge measures overlap with the paper's actual analyses. Human concordance with the LLM judge: 89% and 85% (two PhD raters).

| Model | Micro-Avg | Macro-Avg |
|-------|-----------|-----------|
| GPT-4o (base) | 55.2% (3.0) | 55.6% (2.7) |
| o3-mini (base) | 60.5% (1.0) | 61.6% (0.6) |
| **CellVoyager (o3-mini)** | **79.0% (1.2)** | **80.3% (1.1)** |

CellVoyager outperforms GPT-4o by 23.8% ($P < 0.01$) and o3-mini by 18.5% ($P < 0.001$). Ablations show that the analysis plan module contributes ~17 percentage points and coding guidelines contribute ~9 percentage points (Supplementary Table 2). No significant performance difference between pre- and post-training-cutoff papers.

#### Case Studies

Three published scRNA-seq studies evaluated by PhD-level researchers (including original paper authors):

| Case Study | Dataset | Mean Creativity (1–4) | Insightful | Further Investigation |
|---|---|---|---|---|
| COVID-19 PBMCs (Wilk et al., *Nat. Med.*, 2020) | 7 COVID + 6 healthy | 2.7 | 3/5 | 3/5 |
| Endometrium Atlas (Wang et al., *Nat. Med.*, 2020) | 73K cells, 29 donors | 3.3 | 3/5 | 3/5 |
| Brain Aging (Buckley et al., *Nat. Aging*, 2023) | SVZ, multiple ages | 3.1 | 4/5 | 4/5 |

**Key findings by CellVoyager**:
- **Pyroptosis in CD8+ T cells**: Discovered significantly elevated pyroptosis gene scores in CD8+ T cells from COVID-19 patients ($P = 0.001$), validated in two independent datasets (Stephenson et al., *Nat. Med.*, 2021: $P = 0.002$; Ren et al., *Cell*, 2021: $P = 0.038$). This finding was not in the original paper.
- **Paracrine signaling in endometrium**: Identified TGFβ1–TGFβR1 and FGF2–FGFR1 signaling between stromal fibroblasts and other cell types across menstrual cycle phases, expanding on the original paper's cell-type characterization.
- **Transcriptional noise in aging brain**: Found significantly increased transcriptional noise in oligodendrocytes, microglia, and mural cells with age ($P < 0.001$), validated in an independent dataset (Dulken et al., *Nature*, 2019).

Average creativity score across all 15 analyses: **3.03/4**. 12 of 15 proposed hypotheses were judged interesting enough for further investigation.

### Reproducibility

**Rating: 4/5** — Well-structured and mostly reproducible, with minor friction points.

**Strengths**:
- Complete codebase publicly available on GitHub (zou-group/CellVoyager) with Zenodo DOI
- Fixed environment specification (environment.yml with pinned package versions)
- All prompt templates included in the repository
- CellBench benchmark data available
- Case study datasets referenced from published studies with public data availability

**Weaknesses and Practical Notes**:
- Requires OpenAI API key (and costs) for the original o3-mini + GPT-4o setup
- CellBench evaluation code has a hardcoded Stanford path (`run_agent.py:44`) that needs modification
- `AVAILABLE_PACKAGES` string omits scvi-tools and celltypist despite environment.yml including them
- Paper says AnnData summary uses "first 10 unique values"; code uses 25 (`length_cutoff=25`)
- Results are non-deterministic (LLM stochasticity); CellBench SD ~1–3% across runs
- Case study h5ad files must be obtained from original publications' data repositories
- 300-second kernel timeout may silently fail on long-running analyses
- Documentation extraction limited to scanpy functions only
- The codebase has evolved significantly beyond the paper (Claude mode, GUI, multi-model support); reproducing the exact paper results requires using the original model checkpoints and legacy execution mode

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
