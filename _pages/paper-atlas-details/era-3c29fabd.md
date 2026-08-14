---
layout: default
permalink: /paper-atlas/era-3c29fabd/
title: "ERA"
nav: false
wide: true
description: "科学计算软件通常需要大量手工实现和试错。设计选择容易受直觉和时间限制影响，很难系统地比较大量替代方案。ERA（Empirical Research Assistance）把这类工作改写成一个可评分的程序搜索问题：只要任务有数据、可执行程序和自动质量指标，系统就可以让语言模型持续改写代码，并根据分数保留有价值的候选解。 ERA 不是只调用一次 LLM 生成代码，而是维护一个候选程序树。每个节点保存程序、任务分数、父节点和访问次数。"
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
      <span>Technology Platforms</span>
      <span>Nature · 2026</span>
    </div>
    <h1>ERA</h1>
    <p>An AI system to help scientists write expert-level empirical software</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-026-10658-6" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ERA">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/google-research/era" target="_blank" rel="noopener noreferrer" aria-label="Open code for ERA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ERA：帮助科学家编写专家级经验软件的 AI 系统

### 它要解决什么问题？

科学计算软件通常需要大量手工实现和试错。设计选择容易受直觉和时间限制影响，很难系统地比较大量替代方案。ERA（Empirical Research Assistance）把这类工作改写成一个可评分的程序搜索问题：只要任务有数据、可执行程序和自动质量指标，系统就可以让语言模型持续改写代码，并根据分数保留有价值的候选解（`paper.md:25-42`）。

### 核心想法

ERA 不是只调用一次 LLM 生成代码，而是维护一个候选程序树。每个节点保存程序、任务分数、父节点和访问次数。搜索在整棵历史树上选择节点：高分节点有 exploitation 优势，访问较少的节点有 exploration 优势。这样一条改写路径停滞时，系统可以回到任意历史节点继续探索。

论文将任务分数转换成树内的秩分数，并使用 PUCT：

$$\operatorname{PUCT}_i=r_i+c_{\rm puct}P_T(i)\frac{\sqrt{N_{\rm total}}}{1+V(i)},\qquad N_{\rm total}=\sum_{u\in T}V(u).$$

其中 `P_T(i)=1/|T|` 是平坦先验，`V(i)` 是访问次数，论文在 Kaggle 基准上发现 `c_puct=1` 表现良好（`paper.md:226-237`）。

### 计算流程

```text
任务描述 + 数据 + 评分指标 + 可选研究想法
                    |
                    v
        LLM 读取父程序和父分数，生成新程序
                    |
                    v
           沙箱执行新程序并计算分数
                    |
                    v
       加入节点，更新 PUCT，沿父链回传访问次数
                    |
                    +---- 重复固定次数
                    v
             返回观察到的最高分程序
```

1. 用一个初始程序建立根节点。
2. 计算所有节点的秩分数和 PUCT，选择全局 PUCT 最大的节点。
3. 把任务描述、父代码、父分数和研究指导放入 prompt，让 LLM 产生一个完整子程序。
4. 在沙箱中运行子程序，并用任务指标得到 `TaskScore`。
5. 把子程序加入树中，把访问次数递归回传给父节点。
6. 重复搜索，最后返回原始任务分数最高的节点，而不是最后生成的节点。

公开仓库的 `futs.search`、`compute_rank_scores`、`compute_pucts` 和 `backpropagate_visit` 分别对应上述步骤（`era_repo/implementation/futs.py:69-155`）。其 playground 生成器要求候选代码提供 `train_and_predict(train_path, test_path)`，执行器把 RMSE 取负作为待最大化分数（`playground_s3e1.py:66-186`）。

### 研究想法如何进入搜索？

研究想法可以来自专家建议、论文摘要、搜索代理、Deep Research、AI co-scientist，或来自两个已有方法的成对总结。LLM 将这些想法翻译成代码约束或实现方向，然后 ERA 继续搜索。单细胞实验中，55 个成对重组方案有 24 个同时超过两个父方法；COVID 实验中，26 个重组方案有 11 个超过两个父方法（`paper.md:145-161`, `303-332`）。

### 实验结果

- Kaggle Playground：16 个 2023 赛季竞赛中，树搜索超过单次采样、best-of-1,000 和 AIDE；专家建议及从零实现 boosted tree 的提示进一步提高结果（`paper.md:69-81`）。
- 单细胞批次整合：OpenProblems v2.0.0 的留出集有 1,747,937 个细胞、6 个数据集和 13 类指标。BBKNN (TS) 比最佳已发表方法整体高 14%，并在 11/13 指标上不低于对应的已发表 BBKNN。所有基础、重组和研究代理方案中有 40/87 超过当时排行榜（`paper.md:87-115`）。
- COVID 住院预测：滚动六周验证覆盖 52 个辖区和四个预测时距，Google Retrospective 的平均 WIS 为 26，CovidHub ensemble 为 29；14 个生成策略超过 ensemble（`paper.md:116-161`）。
- GIFT-Eval：系统既搜索每个数据集的模型，也搜索一个最多八种配置的统一预测库；该库逐步处理水平、趋势、季节性、日期特征和残差修正（`paper.md:396-420`）。论文还报告了地理分割、斑马鱼全脑神经活动预测和困难积分上的专家级表现。

### 如何理解代码实现的边界？

论文链接的 GitHub 仓库 `google-research/era`（commit `b836730b5c000526af95116b1d0e2c60c8cf0a10`）能够核对通用 Flat-UCB/PUCT 核心和一个 California Housing playground。但当前快照的 `sandbox.py:22-34` 中 `Sandbox.run` 仍是 `NotImplementedError`，广泛的单细胞、CovidHub、GIFT-Eval 等实验驱动、数据和补充表格也没有在本地实现快照中出现。因此不能声称仅凭此仓库就能重现实验数字；这些缺口在 `doc_code.md` 中明确标为 `Partial` 或 `MISSING`。

### 局限与风险

ERA 擅长优化可自动评分的经验软件，不等同于理解因果机制或完成真正的理论科学发现。结果依赖 LLM 版本、推理预算、数据划分和指标设计。系统也降低了部署复杂模型的门槛，在敏感领域使用时需要真正实现的沙箱隔离、资源限制、数据治理、审计和人工复核；当前代码快照无法验证这些安全属性。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ERA: An AI System for Expert-Level Empirical Software

### Problem

Scientific software is often bottlenecked by manual implementation, intuition-driven design choices and limited ability to test alternatives. ERA formulates software creation as a scorable optimization problem: an LLM rewrites executable programs, a sandbox evaluates them, and a flat PUCT search decides which historical candidate to expand (`paper.md:25-42`, `217-245`).

### What the paper introduces

Empirical Research Assistance (ERA) combines (1) LLM code mutation, (2) global flat-tree search with rank-normalized PUCT, (3) automatic execution/scoring and (4) optional expert, literature, research-agent and recombination guidance. The same primitive is instantiated across Kaggle Playground, scRNA-seq batch integration, COVID hospitalization forecasting, GIFT-Eval, geospatial segmentation, ZAPBench neural activity prediction and numerical integration (`paper.md:48-66`).

### Core method

Each node stores a program, score, parent and visit count. At every iteration, ERA recomputes rank scores and

$$\operatorname{PUCT}_i=r_i+c_{\rm puct}P_T(i)\frac{\sqrt{\sum_u V(u)}}{1+V(i)}.$$

It selects the global maximum, prompts the LLM with the parent code/score and task guidance, executes the new code, appends the child and backpropagates visits. The best raw-score node is returned. The checked `google-research/era` snapshot implements this generic loop and a California Housing playground binding, but leaves `Sandbox.run` unimplemented; therefore it is an algorithmic reference rather than a turnkey reproduction (`doc_code.md`).

### Main evidence

- **Kaggle Playground:** across 16 competitions, tree search beats a single sample, best-of-1,000 and AIDE; expert advice and a from-scratch boosted-tree instruction improve the benchmark further (`paper.md:69-81`; Fig. 1).
- **scRNA-seq:** on OpenProblems v2.0.0, the holdout contains 1,747,937 cells, six datasets and 13 metrics. ERA's BBKNN implementation improves the best published method by 14% overall and beats its published counterpart across 11/13 metrics. Recombination and research-agent prompts yield 40/87 methods above the current leaderboard (`paper.md:87-115`; Fig. 2 and Extended Data Figs. 1-4).
- **COVID forecasting:** rolling six-week validation over 52 jurisdictions and four horizons gives Google Retrospective average WIS 26 versus 29 for the CovidHub ensemble. Fourteen generated strategies beat the ensemble; 11/26 recombinations beat both parents (`paper.md:116-161`; Fig. 3 and Extended Data Figs. 5-7).
- **GIFT-Eval and other domains:** per-dataset searches outperform the dated GIFT-Eval leaderboard; a unified library uses up to eight configurations and sequential level/trend/seasonality/residual components. The paper reports expert-level performance on geospatial segmentation, zebrafish neural activity and difficult integrals (`paper.md:163-174`, `396-436`).

### Strengths and interpretation

The strongest design choice is retaining the full candidate history. It allows global backtracking when a local mutation path plateaus, while rank normalization makes one exploration constant usable across score scales. Prompt-level idea injection lets the system search conceptual methods, not only hyperparameters; the BBKNN/ComBat result is a concrete example of useful recombination.

These results demonstrate high performance on machine-scorable empirical software tasks, not autonomous scientific explanation or causal discovery. They also depend on frontier LLM sampling, large inference-time budgets, task-specific data/evaluators and retrospective/public leaderboard snapshots.

### Reproducibility

**Rating: 3/5 (paper and core algorithm are well specified; end-to-end reproduction is incomplete).** The paper Markdown and all 11 main/extended images are local. The paper-linked GitHub repository is present at commit `b836730b5c000526af95116b1d0e2c60c8cf0a10`, and direct source reads verify `futs.search`, rank/PUCT computation, visit backpropagation, generator/executor contracts and score polarity. However, `Sandbox.run` raises `NotImplementedError`, the broad benchmark drivers/data are not in the indexed implementation, supplementary Markdown was not acquired, and no runtime benchmark was executed. These are explicit gaps, not evidence that the paper's reported scores are incorrect.

### Safety and scope

The paper itself notes that systems capable of producing expert-level empirical software lower the barrier to deploying sophisticated models in sensitive domains. Practical use therefore requires sandbox hardening, resource limits, data governance, audit trails and human review. The acquired snapshot cannot verify those controls because its sandbox implementation is missing (`paper.md:183-208`; `sandbox.py:22-34`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
