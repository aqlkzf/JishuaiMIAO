---
layout: default
permalink: /paper-atlas/ida-bench-998236ce/
title: "IDA-Bench"
nav: false
description: "IDA-Bench 研究的不是“LLM 能不能一次写出一段正确代码”，而是更接近真实数据分析的问题：当领域专家根据中间结果逐步提供知识、修改要求或纠正方向时，LLM Agent 能否持续记住上下文、正确执行代码、服从新指导，并最终交付合格的分析结果。 这不是生物信息学论文。它属于通用 LLM Agent 与数据分析 benchmark，任务涉及制造、商业、心理、天气、传统 NLP 等多种表格预测场景。"
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
      <span>Machine Learning Algorithm</span>
      <span>arXiv preprint · 2025</span>
    </div>
    <h1>IDA-Bench</h1>
    <p>IDA-Bench: Evaluating LLMs on Interactive Guided Data Analysis</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2505.18223" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## IDA-Bench 方法详解

### 这篇论文在解决什么问题？

IDA-Bench 研究的不是“LLM 能不能一次写出一段正确代码”，而是更接近真实数据分析的问题：当领域专家根据中间结果逐步提供知识、修改要求或纠正方向时，LLM Agent 能否持续记住上下文、正确执行代码、服从新指导，并最终交付合格的分析结果。

这不是生物信息学论文。它属于通用 LLM Agent 与数据分析 benchmark，任务涉及制造、商业、心理、天气、传统 NLP 等多种表格预测场景。

### 为什么现有评测不够？

DS-1000、DSBench、DSEval 等评测能够检查代码生成、执行环境交互或数据科学生命周期，但常把目标预先完整给出。真实分析中，很多关键决定只有看过数据后才会出现，例如异常值范围、缺失值处理、特征工程、领域评分规则和模型选择。静态单轮评测无法观察 Agent 是否会：

- 抢在专家指导前自行做出假设；
- 忽略后续纠正，固守早期方案；
- 在一次代码部分失败后错误地假设状态仍然完整；
- 口头声称已执行、调参或保存结果，但实际没有完成。

IDA-Bench 因而把完整的多轮轨迹作为评测对象。

### 一个任务由什么组成？

```text
Instruction material
  背景 + 目标 + 指标 + 领域/分析者 insight
                │
                ▼
       LLM 模拟用户 ──► Gatekeeper
                ▲          │纠正偏离目标的请求
                │          ▼
                └──── 被测 Agent
                         │ Python 代码
                         ▼
               持久化 Docker/Jupyter sandbox
                         │ submission.csv
                         ▼
       隐藏真值 + 任务指标 + 人类 notebook baseline
                         │
                         ▼
     有效提交、达到 baseline、相对分数、耗时/轮数/错误
```

#### Instruction material

每个任务包含数据背景、预测目标、评价指标和 6–10 条 reference insight。这些 insight 来自原 Kaggle notebook 中隐含的数据处理与建模决定，例如怎样填补缺失值、需要构造哪些特征、应采用什么模型或超参数。

#### 模拟用户

模拟用户不会一开始把全部 insight 原样告诉 Agent，而是先提出一般性要求；当 Agent 主动询问，或其行为与已知分析路径冲突时，再逐步给出指导。这是在测试“随着分析推进而变化的用户要求”。主实验使用 Claude-3.5-Sonnet-241022、temperature 0.4。

#### Gatekeeper

模拟用户本身也可能漂移或生成错误建议，因此 Gatekeeper 能看到更完整、更严格的 reference instructions。每条用户消息先经过它：一致则放行；冲突则生成一个保持原语气、但把方向拉回预定任务的 follow-up。论文的一组对话中，它纠正了 18/225（8%）条用户消息。

#### 被测 Agent 和 sandbox

Agent 在对话中生成 Python，sandbox 保留类似 Jupyter 的执行状态，并反馈输出或错误。数据只读挂载，Agent 必须最终写出指定路径的 `submission.csv`。实验限制为最多 30 轮对话、单次最多 5 个代码块、4,096 tokens、每段代码最多 200 秒。

### 25 个任务怎样构造？

1. 抓取 2025 年 5 月 1 日之前 90 天内上传的 15,108 个 Kaggle Python notebooks。
2. 过滤教程、初学者内容、GPU/TPU/深度学习任务、非 CSV 或不可下载数据、超过 1 GB 或运行超过 10 分钟的任务，剩下 1,288 个。
3. 根据数据规模、competition/time-series 信号、`groupby`/`merge`/`agg` 等复杂操作、代码量、单元格数、运行时间和图表惩罚等打分。
4. 人工检查前 100 个，保留 25 个目标清晰、可以执行、可以客观评分的 notebooks。
5. 用外部 LLM 辅助识别主要数值目标、裁剪无关代码、重构 train/test 接口、抽取评价函数、执行得到 baseline，并把隐含决定转成 reference insights；输出再经过人工检查。

最终得到 209 条 insights，平均每个任务 8.36 条。评测以表格预测为主，指标包含 accuracy、AUC、RMSE/RMSLE、MAE、MSE 和 log loss。

### 怎样评分？

最重要的三个结果是：

- **Valid Submission**：文件是否存在、列名/类型/格式是否能通过任务 evaluator；
- **Baseline Achieved**：Agent 分数是否等于或优于原 notebook 的人类 baseline；
- **Baseline Achieved / Valid Submission**：只在有效提交中计算的达标比例。

对误差型指标，理论最优值为 $L$：

$$
\mathrm{Score}=\frac{\mathrm{Eval(base)}-\mathrm{Eval(agent)}}{\mathrm{Eval(base)}-L}.
$$

对越大越好的指标，理论最优值为 $U$：

$$
\mathrm{Score}=\frac{\mathrm{Eval(agent)}-\mathrm{Eval(base)}}{U-\mathrm{Eval(base)}}.
$$

因此 0 表示等于 baseline，正数表示更好，负数表示更差。论文附录中第二个公式把分母文字写成 “theoretical lower bound”，与上下文不一致；官方代码使用 `theoretical_best`，实现的是上面的 $U$。

论文还采用严格的 $\mathrm{pass}^k$：同一任务连续 $k$ 次都达到 baseline 才算通过。DeepSeek-V3 从 $k=1$ 的 24% 降至 $k=3$ 的 4%；到 $k=5$，DeepSeek-V3 和 R1 都只剩 4%，说明一次成功并不代表稳定。

### 结果怎样理解？

六个被测 Agent 中，没有任何一个在超过 40% 的任务上达到 baseline：Gemini-2.5-Pro、o4-mini 和 Claude-3.7 都是 40%，DeepSeek-V3 为 24%，DeepSeek-R1 为 12%。不同 Agent 的失败模式明显不同：

- Gemini 更谨慎、频繁确认，平均轮数与耗时最长；
- Claude 更主动且 100% 能生成有效提交，但可能提前定型、忽略后续指导；
- o4-mini 达到同样 40% 时速度最快；
- o3 只有 12% 的运行产生有效提交；
- DeepSeek-R1 的 reasoning 定位并未带来更好的多轮服从性，反而弱于 V3。

无效提交中，69.4% 是根本没有提交文件；其他问题包括类型错误、超时、列名错误。论文还观察到幻觉式完成、过早坚持初始模型以及部分执行失败导致的状态级联错误。

### 方法边界

- 原 notebook baseline 是可比较目标，不等于全局最优模型。
- 模拟用户和 Gatekeeper 都是 LLM，其行为依赖模型与 prompt；它们不能等同于真实人类专家。
- 只有 25 个经过人工筛选的任务，主要是表格预测，不能代表全部数据分析。
- 不直接评测图像理解/生成、多模态分析、科学因果有效性或解释质量。
- 近期 notebook 设计只能降低数据污染风险，不能证明完全无污染。

### 代码与复现

官方代码仓库完整实现了多轮对话、Gatekeeper、Docker sandbox、提交评分与相对 baseline 分数，paper–code fidelity 为高。数据发布在 Kaggle，但需要认证；完整重跑还需要 Docker、多个模型 API 凭证和预算。仓库没有提交自动化测试，也没有附带论文中每次实验的完整 checkpoints，因此本工作区没有声称复现论文数值结果。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## IDA-Bench: summary

### Problem

Most data-science benchmarks give an agent one static task, even though real analysis is iterative: experts inspect intermediate results, reveal domain knowledge, revise feature choices, and correct the analyst as the workflow develops. IDA-Bench evaluates whether LLM coding agents can follow this evolving guidance and still produce a valid, competitive analysis result.

This is a general LLM/data-analysis benchmark, not a bioinformatics paper. Its tasks span manufacturing, business, psychology, weather, NLP, and other tabular predictive domains.

### What IDA-Bench introduces

Each task combines four components:

1. **Instruction material** derived from a real Kaggle notebook: background, goal, metric, and analyst-specific reference insights.
2. **LLM-simulated user** that reveals guidance gradually in response to the agent's behavior.
3. **Evaluated LLM agent** that writes and executes Python while maintaining state across rounds.
4. **Sandbox and evaluator** that expose task data, capture `submission.csv`, score it against withheld ground truth, and compare it with a reconstructed human-notebook baseline.

A gatekeeper LLM sees detailed reference instructions and corrects simulated-user requests that contradict the intended analysis. An alternative shard-user protocol tests whether the main findings persist when accurate instruction pieces are disclosed more mechanically.

### Benchmark construction

The authors crawl 15,108 recent Kaggle notebooks, filter to 1,288 candidates, rank them using code/data complexity signals, manually inspect the top 100, and retain 25 executable tasks. LLM-assisted preprocessing identifies the primary numerical objective, prunes and reconstructs the notebook, standardizes its evaluator, executes it to obtain a baseline, and narrates implicit analysis choices. Human checks are used throughout. The release contains 209 reference insights, 6–10 per task.

The evaluated set is predominantly tabular predictive modeling. Metrics vary by task—accuracy, AUC, RMSE/RMSLE, MAE, MSE, and log loss—but every run must create a correctly formatted submission and match or exceed the source notebook's score to count as baseline-achieved.

### Evaluation and results

The study evaluates Claude-3.7-Sonnet-thinking, DeepSeek-R1, DeepSeek-V3, Gemini-2.5-Pro, OpenAI o3, and OpenAI o4-mini under up to 30 user-agent turns, five code blocks per response, 4,096 output tokens, and 200 seconds per code execution.

No agent achieves the human baseline on more than 40% of the 25 tasks. Gemini-2.5-Pro, o4-mini, and Claude-3.7 reach 40%, but with distinct behaviors: Gemini is slow and confirmation-heavy, o4-mini is fastest, and Claude submits valid files consistently yet often advances prematurely. DeepSeek-V3 reaches 24% versus 12% for DeepSeek-R1; o3 produces valid submissions in only 12% of runs.

Failures include no submission/hallucinated completion, incorrect types or columns, timeout, premature commitment to an early approach, and cascading errors after partial code execution. Repeated-run stability is poor: the all-$k$ success rate falls to 4% by five attempts for both tested DeepSeek agents.

### Interpretation

IDA-Bench's central contribution is a protocol for measuring the joint ability to reason, execute code, retain state, and obey evolving expert guidance. The results suggest that more explicit reasoning does not automatically yield better interactive analysis: overly autonomous agents may ignore later guidance, while overly cautious agents exhaust the interaction budget.

The benchmark does **not** establish that its notebook baseline is optimal, that simulated users faithfully reproduce human behavior, or that performance transfers to multimodal/open-ended scientific analysis. Its 25 manually curated tasks are modest in scale, and the simulated user/gatekeeper introduce model- and prompt-dependent variation.

### Reproducibility

- **Paper:** arXiv:2505.18223v2, 51-page official PDF; no archival venue or journal reference was found in the arXiv record.
- **Code:** official repository `https://github.com/lhydave/IDA-Bench`, snapshot commit `5fb687fb3e4873b8b58baa6966451acd2206562d`.
- **Data:** official Kaggle dataset `lhydave/ida-bench`; requires Kaggle credentials and was not downloaded here.
- **Code-paper match:** high for the framework. Direct source implements the simulated user, gatekeeper, multi-round loop, Docker sandbox, submission evaluation, and baseline-normalized score.
- **Limitations:** full numerical reproduction requires Kaggle data, Docker, model-provider credentials, and substantial API budget. Exact published checkpoints are not bundled, and the repository has no committed automated tests.
- **Notable discrepancy:** the higher-is-better equation in Appendix D.2 says “theoretical lower bound”; the implementation uses `theoretical_best`, matching the intended normalization.

**Reproducibility rating: 3/5** — source and framework are public and closely aligned, but external data/authentication and proprietary API calls prevent a self-contained rerun.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
