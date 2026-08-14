---
layout: default
permalink: /paper-atlas/large-language-models-for-drug-discovery-and-development-9748f546/
title: "Large_language_models_for_drug_discovery_and_development"
nav: false
wide: true
description: "这篇 2025 年发表于 Patterns 的论文是一篇综述与技术框架总结。它没有提出一个可直接训练或运行的单一模型，也没有给出新的损失函数。它真正提供的是一套“把已有 LLM 工作放回药物开发流程中理解”的方法： 先判断模型属于哪一种范式； 再判断它服务于药物开发的哪个阶段、哪个具体任务； 最后按照验证环境，而不是只看论文指标，评估它的成熟度。 因此，学习这篇论文的关键不是记住一长串模型名，而是掌握这套分类和决策框架。"
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
      <span>Computational Tools</span>
      <span>Patterns · 2025</span>
    </div>
    <h1>Large_language_models_for_drug_discovery_and_development</h1>
    <p>Large language models for drug discovery and development</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.patter.2025.101346" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Large_language_models_for_drug_discovery_and_development">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 大语言模型如何进入药物发现与开发流程：方法框架详解

### 先明确：这篇论文不是一个新算法

这篇 2025 年发表于 *Patterns* 的论文是一篇综述与技术框架总结。它没有提出一个可直接训练或运行的单一模型，也没有给出新的损失函数。它真正提供的是一套“**把已有 LLM 工作放回药物开发流程中理解**”的方法：

1. 先判断模型属于哪一种范式；
2. 再判断它服务于药物开发的哪个阶段、哪个具体任务；
3. 最后按照验证环境，而不是只看论文指标，评估它的成熟度。

因此，学习这篇论文的关键不是记住一长串模型名，而是掌握这套分类和决策框架。

### 论文要解决什么问题

传统药物开发通常需要 10-15 年，单个药物成本可能超过 20 亿美元。耗时不仅来自分子设计，还来自疾病机制理解、靶点确认、安全性筛选、临床受试者匹配和长期随访等多个环节（论文第 31 行）。

LLM 已经出现在这些环节中，但现有工作有三个问题：

- 任务差异很大：DNA 序列模型、蛋白质模型、化学智能体和临床文本模型不能用同一指标直接比较。
- “模型能输出答案”不等于“模型已经可用”：纯计算验证、实验室验证和医院部署是完全不同的证据等级。
- 专用模型与通用模型各有优势，不能用参数量大小代替任务匹配。

论文因此提出三个问题：LLM 应该放在药物开发的什么位置？目前成熟到什么程度？走向可信应用还缺什么？对应原文见论文第 37-45 行。

### 两套不能混淆的分类轴

#### 分类轴一：专用模型与通用模型

| 范式 | 主要输入 | 擅长任务 | 典型短板 |
|---|---|---|---|
| 专用语言模型 | SMILES/IUPAC/SELFIES、DNA/RNA 序列、蛋白质序列、组学数据 | 变异预测、结构/功能预测、分子和蛋白生成、相互作用预测 | 任务范围窄，跨领域推理和真实环境验证不足 |
| 通用大语言模型 | 论文、网页、书籍、代码、临床文本等广泛语料 | 检索、解释、规划、对话、代码生成、调用工具 | 科学符号理解、定量精度、幻觉和版本可复现性问题 |

图 2 用“工具式使用”和“助手式使用”进一步解释了二者的差别：专用模型通常接收结构化科学输入并给出预测；通用模型更像一个交互式助手或编排器。

#### 分类轴二：LM、LLM 与混合方法

论文还按照规模和系统组成给出另一套分类：

- **LM-based**：参数量 $\leq 100$ million；
- **LLM-based**：参数量 $>100$ million；
- **Hybrid methods**：语言模型与图神经网络、强化学习模块或其他科学工具组合。

这套分类与“专用/通用”不是同一件事。一个模型可以规模很大但仍然是专用模型；一个通用 LLM 也可以作为混合系统中的编排器。100 million 是论文采用的分类阈值，不是已证明的性能分界线。

### 四级成熟度框架

论文用验证环境定义成熟度（论文第 41-45 行）：

| 等级 | 含义 | 需要什么证据 |
|---|---|---|
| **Not applicable（不适用）** | 该模型范式不适合此任务 | 没有合理的任务角色 |
| **Nascent（萌芽期）** | 只在 *in silico* 环境研究 | 尚无真实实验验证 |
| **Advanced（进展期）** | 已在实验室或现实条件下的试点中显示效果 | 超越纯计算结果的验证 |
| **Matured（成熟期）** | 已在医院、制药流程等操作环境部署，并有实际效用记录 | 真实生产/临床使用证据 |

最重要的理解是：成熟度评的是“**某类模型在某个具体任务上的验证状态**”，不是给整个 LLM 领域打一个总分，也不是只看准确率。

### 从输入到输出的完整分析流程

```text
已有论文、案例和部署证据
          |
          v
判断模型范式：专用 or 通用
判断方法类别：LM / LLM / Hybrid
          |
          v
定位药物开发阶段和具体任务
  疾病机制 -> 药物发现 -> 临床试验
          |
          v
明确任务输入、模型动作和决策输出
          |
          v
依据验证环境分配成熟度
  不适用 -> 萌芽 -> 进展 -> 成熟
          |
          v
识别技术、数据、伦理和监管缺口
```

这就是论文的“计算框架”。它是一条从文献证据到任务地图的分析流水线，而不是一段训练代码。

### 阶段一：理解疾病机制

#### 业务流程

```text
患者数据 + 多组学数据
        |
        v
临床数据收集与患者分层
        |
        v
建立靶点-疾病联系
  变异 + 表达 + 通路 + 扰动实验
        |
        v
迭代靶点验证
  安全/可行性 <-> 作用机制 <-> 治疗模态选择
        |
        v
候选靶点 + 机制证据 + 治疗模态
```

图 3 左侧把这一阶段分成临床数据收集、靶点-疾病关联、靶点验证三部分。靶点验证被画成循环，说明安全性、可成药性、作用机制和治疗模态需要反复权衡，而不是一次性线性决策（论文第 47-51 行）。

#### LLM 在其中做什么

- **基因组分析**：识别功能变异，预测启动子、转录因子结合位点、剪接位点和表观遗传标记。专用和通用模型都仍处于萌芽期。
- **转录组分析**：对单细胞表达进行表征、细胞分型、基因网络推断和 *in silico* 扰动。Geneformer（*Nature*, 2023）等专用模型已有实验验证，属于进展期；通用模型仍处于萌芽期。
- **蛋白质靶点分析**：从序列推断进化约束、折叠、功能、相互作用和配体结合位置。专用模型已有较强验证，通用模型仍缺少广泛真实验证。
- **疾病通路分析**：把组学信号与文献、数据库和知识图谱结合，用于通路组装、候选基因排序和假设生成。两类模型都有进展，但尚未广泛部署。
- **辅助任务**：通用模型进行信息检索、知识解释和跨学科沟通。这是该阶段最成熟的通用模型用途。

这一阶段的输出不是药物，而是“**值得继续投入的靶点假设及其证据包**”。

### 阶段二：药物发现

#### 业务流程

```text
已验证靶点 + 治疗模态
          |
          v
Hit identification（找到活性命中物）
          |
          v
Hit-to-lead（筛成先导物）
          |
          v
Lead optimization（效力/选择性/安全/稳定性优化）
          |
          v
Preclinical（临床前验证）
          |
          v
可进入人体试验的候选药物
```

图 4 用漏斗显示候选数量逐步收缩，同时把 LLM 任务放在流程右侧（论文第 119-121 行）。

#### 关键模块

1. **化学实验与合成规划**
   - 通用模型可把自然语言协议转换为机器人代码，进行逆合成规划和反应预测。
   - ChemCrow（*Nature Machine Intelligence*, 2024）与 Coscientist（*Nature*, 2023）代表工具调用路线。
   - 实验室中已有真实演示，因此通用模型属于进展期；但尚不能据此声称制药工业已普遍自动化。

2. ***In silico* 模拟**
   - 包括新分子生成、新蛋白生成和蛋白质-配体相互作用预测。
   - 专用模型能够利用序列、SMILES、结构口袋和分子指纹，通常比通用模型更适合精确预测。
   - 专用模型达到进展期；通用模型因 SMILES 理解和定量能力不足，多数仍处于萌芽期。

3. **ADMET 预测**
   - 对吸收、分布、代谢、排泄和毒性进行预测，用于 hit-to-lead 和先导优化阶段淘汰高风险分子。
   - 论文举出 LLM4SD 使用 Galactica 提取 ADMET 假设并由药理学家复核的进展期例子，但没有统一基准证明所有范式都达到同一水平。

4. **分子与蛋白优化**
   - 输入是已有候选结构和目标属性，输出是修改后的候选及预测属性。
   - 专用模型已有真实实验验证；通用模型主要停留在 *in silico* 测试。

5. **信息辅助**
   - 通用模型检索论文、专利和化合物数据库并解释复杂概念，属于进展期应用。

一个常见误解是把“生成新分子”视为终点。图 4 明确表明，生成结构之后仍需相互作用预测、ADMET、优化和临床前实验。

### 阶段三：临床试验

#### 业务流程与任务

```text
临床前候选药物
      |
      v
Phase 1 安全/剂量
  -> Phase 2 有效性/副作用
  -> Phase 3 与现有治疗比较
  -> Phase 4 上市后长期监测
      |
      +-- ICD 编码和 EHR 结构化
      +-- 患者-试验匹配
      +-- 试验设计、站点选择和结果预测
      +-- 文档生成、检索和解释
      |
      v
可审计的试验决策和患者结果
```

图 5 把临床四期与临床实践、患者结果和辅助任务并列显示。患者-试验匹配需要解析 EHR 和纳入/排除标准；试验规划需要处理协议、站点和历史结果；结局预测需要纵向临床数据（论文第 191-229 行）。

临床实践类通用模型总体仍在萌芽期，因为真实验证有限。患者结局预测已有 NYUTron（*Nature*, 2023）等健康系统级例子，但仍不能替代临床判断。文档写作、检索和解释相对更成熟。专用科学语言模型对以对话和文档为核心的部分任务并不适用。

### 论文如何“评估”这些方法

这篇论文没有运行统一实验。它从被引用研究中提取案例，再用四级成熟度框架做定性归纳。不同证据包括：

- Geneformer 推导出的心脏靶点得到实验验证；
- 通用 LLM 控制化学机器人；
- 生成的候选分子得到 *in vitro* 或 *in vivo* 验证；
- 临床预测模型接入健康系统；
- 信息助手进入真实工作环境。

这些例子支持“成熟度不均衡”这一结论，但不构成统一排行榜。各研究的数据集、任务、指标和验证环境不同，不能把 884 个细胞的基因网络案例、机器人控制成功率和医学问答准确率放在同一张性能表里比较。

### 证据边界：论文结论、分析解释与代码验证

#### 论文直接主张

- LLM 可以覆盖药物开发三个阶段，但成熟度非常不均衡。
- 专用模型通常更适合科学预测和生成；通用模型更适合检索、解释和工具编排。
- 临床和高风险用途必须加强可信度、溯源、审计和监管。

#### 本文档的分析性解释

- 实际选型应从任务和所需证据等级出发，而不是先选最大模型。
- 最合理的系统形态通常是：专用模型执行预测，经过验证的科学工具提供约束，通用模型负责编排和解释，人类专家把守高风险决策。
- 成熟度标签只适用于具体“任务 × 模型范式”组合。

#### 代码验证状态

**Not applicable / Not found。结构化文章、正文和后期代码发现均未找到与论文直接关联的 GitHub 实现、固定提交、运行示例、提示词或模型资产。因此，本文档没有把任何行为标记为“代码已验证”，也没有用无关 GitHub 仓库替代论文实现。

### 可复现性与缺失证据

**可复现性评分：2/5。** 正文、引用和五张编号图可核查，但这套综述评估不能直接重新运行。

- **Not found**：可复现的文献检索式、纳入/排除标准、研究质量评分和评审者一致性过程。
- **Not found**：边界案例如何分配成熟度的数值公式或详细判定程序。
- **Not found**：统一数据集、基线、置信区间和跨任务统计比较。
- **Not found**：论文关联代码、固定模型版本、提示词和机器可读成熟度标签。
- Markdown 引用了 Boxes/Tables，但当前主 Markdown 主要提供正文和五张图；本文档没有猜测缺失表格单元格。

### 论文提出的未来假设，而非已验证结果

以下内容是研究方向，不应写成论文已经证明的结果：

1. 先用物理或图方法过滤 $10^{8}$-$10^{9}$ 个分子，再让 LLM 重排较小候选集，以解决自回归评分过慢的问题（论文第 261 行）。
2. 将分子动力学轨迹等大数据压缩为潜在表示，再通过流式记忆和 RAG 访问。
3. 建立多模态混合生态：专用模型做领域分析，通用模型编排、解释并规划下一步（论文第 265-267 行）。
4. 按风险分配自治程度：低风险检索可自动化，中风险筛选必须人工核验和留审计日志，临床决策还要有不确定性、解释和监管（论文第 241-249 行）。
5. 建立同时覆盖化学图、三维结构、成像、组学、时序模拟、临床终点和数据溯源的开放基准。

### 给研究者的使用建议

使用这套框架评估一个新系统时，依次回答：

1. 它解决药物开发中的哪个具体决策？
2. 输入和输出是什么，输出是否能被实验或临床流程验证？
3. 它是专用预测器、通用助手，还是混合系统？
4. 当前证据只来自 *in silico*，还是已经进入实验室、试点或真实部署？
5. 高风险输出是否保留人工检查、模型溯源、审计记录和不确定性说明？

这五个问题比单独询问参数量或榜单分数更贴近论文的核心方法。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Large Language Models for Drug Discovery and Development

### At a glance

This 2025 *Patterns* review organizes LLM applications across the full drug-development pipeline: understanding disease mechanisms, discovering and optimizing drug candidates, and conducting clinical trials. Its main contribution is not a new model but a **stage-based taxonomy plus a four-level maturity framework** that distinguishes computational demonstrations from laboratory validation and operational deployment.

### Problem

Drug development commonly takes 10-15 years and more than $2 billion per successful drug, with delays across target selection, candidate design, preclinical work, and clinical evaluation (paper line 31). LLM research is expanding in all of these areas, but evidence is fragmented across incomparable tasks and model types. The review asks where LLMs fit, how mature each use is, and what prevents trustworthy deployment (lines 37-45).

### Limitations of the existing landscape

- **Specialized scientific-language models** can learn from DNA/RNA, proteins, molecules, and omics data, but are usually narrow and often lack real-world experimental validation.
- **General-purpose LLMs** offer reasoning, retrieval, conversation, and tool use, but GPT-4 (*arXiv*, 2023) is reported to struggle with SMILES and quantitative scientific tasks; fluent outputs can also conceal hallucinations.
- Evidence is usually task-specific. A Geneformer study (*Nature*, 2023), ChemCrow (*Nature Machine Intelligence*, 2024), Coscientist (*Nature*, 2023), and TrialGPT (*Nature Communications*, 2024) answer different questions and cannot be ranked with one shared metric.
- Scientific applications still rely heavily on ad hoc case studies rather than standardized multimodal benchmarks (paper lines 269-273).

### Framework

The review uses three linked views:

1. **Paradigm:** specialized models trained on scientific languages versus general-purpose models trained on broad text.
2. **Method class:** LM-based ($\leq 100$ million parameters), LLM-based ($>100$ million), or hybrid language-model systems.
3. **Pipeline task and maturity:** each application is placed within a drug-development stage and assessed as not applicable, nascent, advanced, or matured.

The maturity levels have concrete evidence boundaries: **nascent** means only *in silico* investigation, **advanced** means laboratory or realistic pilot evidence, and **matured** means operational deployment with documented utility (paper lines 41-45).

```text
Published application
      -> classify model paradigm and method class
      -> locate task in the drug pipeline
      -> identify its decision output
      -> rate the validation setting
      -> expose gaps and required oversight
```

### Pipeline synthesis

#### 1. Understanding disease mechanisms

Patient and multi-omics data support clinical stratification, target-disease linkage, and iterative target validation. Specialized models analyze variants, gene expression, protein structure/function, and interactions. General models synthesize literature and databases, assist pathway reasoning, and explain knowledge. The review rates specialized transcriptomics, protein, and pathway applications as advanced, while general-purpose genomics, transcriptomics, and protein analysis remain nascent. General information assistance is the most mature use in this stage (paper lines 47-117; Figure 3).

#### 2. Drug discovery

A validated target moves through modality selection, hit identification, hit-to-lead, lead optimization, and preclinical testing. LLMs support chemistry robotics, retrosynthesis, reaction prediction, molecule/protein generation, protein-ligand prediction, ADMET filtering, and candidate editing. Specialized models are generally more advanced for scientific prediction and generation; general tool-using models are advanced in chemistry and assistance but remain nascent for precise *in silico* generation and lead optimization (paper lines 119-189; Figure 4).

#### 3. Clinical trials

LLMs can assist ICD coding, patient-trial matching, trial planning, outcome prediction, document writing, retrieval, and knowledge explanation across phases 1-4. Clinical-practice applications remain largely nascent because real-world validation is limited, while assistance is more advanced. The paper repeatedly preserves a human role in ambiguous or high-stakes decisions (paper lines 191-229; Figure 5).

### Evaluation and principal findings

The authors do not run a common experiment. Evaluation is a qualitative synthesis of cited case studies using the four-level rubric. Representative evidence includes experimental validation of Geneformer-derived cardiac targets, laboratory chemistry automation, *in vitro*/*in vivo* validation of generated molecules, health-system outcome models, and deployed information assistants.

The central result is **uneven maturity**:

- Specialized models lead in domain prediction and generation.
- General models lead in retrieval, explanation, and tool orchestration.
- Operational maturity is concentrated in assistance rather than autonomous scientific or clinical decisions.

Because tasks, datasets, endpoints, and study designs differ, the review provides no shared baseline suite, aggregate metric, confidence interval, or statistical comparison. Individual cited values must not be interpreted as a head-to-head benchmark.

### Reproducibility

**Rating: 2/5 (source-accessible synthesis, not computationally reproducible).**

- The article text, references, and five numbered figures are locally available and support the taxonomy and maturity narrative.
- **Not found:** paper-linked GitHub code, frozen model versions, prompts, runnable examples, or machine-readable task/maturity labels.
- **Not found:** a reproducible search strategy, inclusion/exclusion criteria, study-quality assessment, maturity-adjudication rule, or inter-rater analysis.
- The workspace is correctly `paper-only`; `doc_code.md` is intentionally absent. No implementation behavior has been verified.
- The review's cited case studies may have their own resources, but unrelated repositories were not used as if they implemented this paper.

### Limitations and risk boundaries

The maturity framework is useful but qualitative. Opaque commercial model versions, data leakage, population bias, dual use, hallucinations, weak numerical/spatiotemporal reasoning, and slow autoregressive screening all constrain deployment. The authors recommend autonomy proportional to risk: low-stakes triage may be automated, moderate-stakes work requires human verification and audit logs, and clinical decisions require uncertainty estimates, explanations, regulatory oversight, and mandatory human checkpoints (paper lines 241-263).

### Forward-looking hypotheses, not demonstrated results

- Use fast physics or graph filters for $10^{8}$-$10^{9}$ molecule libraries and let LLMs re-rank only the reduced candidate set.
- Compress trajectories and other large biological data into latent summaries accessed through retrieval.
- Couple specialized scientific models to a general LLM orchestrator in a multimodal hybrid ecosystem.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
