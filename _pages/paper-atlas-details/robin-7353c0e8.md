---
layout: default
permalink: /paper-atlas/robin-7353c0e8/
title: "Robin"
nav: false
wide: true
description: "Robin 不是一个单一预测模型，而是一个把文献检索、LLM 假设生成、BTL 排名、湿实验反馈和 Finch notebook 数据分析连接起来的闭环发现系统；它在 dAMD 案例中产生了有体外证据支持的候选药物优先级，但临床有效性、体内验证和完整公共复现仍然是未完成问题。"
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
      <span>Machine Learning Algorithm</span>
      <span>Nature · 2026</span>
    </div>
    <h1>Robin</h1>
    <p>A multi-agent system for automating scientific discovery</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-026-10652-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Robin">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Future-House/robin" target="_blank" rel="noopener noreferrer" aria-label="Open code for Robin">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Robin 中文方法解读

### 1. 这篇论文要解决什么问题

Robin 解决的是一个实际科研瓶颈：生物医学发现需要不断在文献、疾病机制、实验设计、药物候选和新实验数据之间来回推理，但这些知识分散在大量论文和实验结果里。论文把这个问题表述为科学发现的闭环：观察、生成假设、做实验、分析数据、再更新假设。Robin 的目标不是直接给出临床治疗结论，而是把这个闭环里的“文献驱动假设生成”和“实验数据分析”自动化，再由人类科学家执行湿实验。论文摘要明确说 Robin 将文献搜索代理和数据分析代理结合起来，用于生成假设、提出实验、解释实验结果并产生更新后的假设；在 dry age-related macular degeneration (dAMD) 案例中，Robin 提出了增强 RPE 细胞吞噬作用的治疗策略，并在体外验证了 ripasudil 和 KL001 的活性（`paper source/paper/hybrid_auto/paper.md:40`）。

这个定位很重要：Robin 是一个 lab-in-the-loop 的发现系统。它自动化的是智力步骤和数据分析步骤，不是自动完成细胞培养、药物处理和测序等湿实验步骤。论文也写明，科学家会根据 Robin 的建议进行实验，并把 flow cytometry 或 RNA-seq 数据上传给 Robin/Finch 分析（`paper source/paper/hybrid_auto/paper.md:62-66`）。

### 2. 为什么已有方法不够

论文指出，已有 LLM 科学系统可以做假设生成、论文总结、工具调用或药物属性预测，但还没有把关键智力步骤串成一个连续的生物实验发现闭环：生成假设和实验策略、分析实验结果、再根据新数据 refine 假设（`paper source/paper/hybrid_auto/paper.md:48-50`）。因此 Robin 的新意不在于一个新的神经网络结构，而在于把多个专用代理和实验反馈组织成一个可迭代工作流。

与只做文献问答或候选药物生成的系统相比，Robin 多了两个关键环节：

1. 先选择可实验验证的 in vitro assay，而不是直接生成药名。
2. 实验数据经过 Finch 分析后，会变成下一轮候选药物生成的上下文。

这让 Robin 更接近“发现流程控制器”，而不是单次问答工具。

### 3. Robin 的系统组成

Robin 协调三个主要代理：

| 组件 | 作用 | 代码证据 |
|---|---|---|
| Crow | 简洁文献综述，支持疾病机制、assay 和候选药物检索 | `robin/robin/configuration.py:242-257` |
| Falcon | 对候选治疗分子生成更深入的评估报告 | `robin/robin/configuration.py:258-263` |
| Finch | 在 Jupyter notebook 中执行 flow cytometry 或 RNA-seq 等数据分析 | `robin/robin/analyses.py:17-202`; `finch/src/fhda/notebook_env.py:215-245` |

公共代码暴露的主 API 与论文阶段对应：`experimental_assay` 负责 assay 选择，`therapeutic_candidates` 负责候选药物生成，`data_analysis` 负责实验数据分析和结果解释（`robin/robin/__init__.py:1-12`）。这说明代码层面确实支持论文描述的三段式架构。

### 4. 输入、输出和核心变量

Robin 的最小输入是一个疾病名称。在论文案例中，输入是 dry age-related macular degeneration。工作流的输出不是“最终药物”，而是：

- 一个可实验测试的疾病相关 assay，例如 RPE phagocytosis enhancement；
- 一组排序后的候选治疗分子；
- 人类实验产生的数据分析结果；
- 可反馈到下一轮候选生成的实验 insight。

关键变量可以这样理解：

| 论文对象 | 代码变量 | 含义 |
|---|---|---|
| 疾病名称 | `disease_name` | 用户给定的研究对象；论文中为 dAMD（`robin/robin/configuration.py:283-285`） |
| 文献查询数 | `num_queries` | Crow/Falcon 检索问题数量；公共默认值小于论文运行规模（`robin/robin/configuration.py:271-278`） |
| assay 数量 | `num_assays` | 候选实验机制/模型数量；论文运行用 10 个（`robin/robin_full.ipynb:39-41`） |
| 候选药物数量 | `num_candidates` | 生成并排序的候选分子数量；论文运行用 30 个（`robin/robin_full.ipynb:39-41`） |
| 成对比较结果 | `pairs_list` / games | LLM judge 的 winner-loser 对，用于 BTL 排名（`robin/robin/utils.py:422-453`） |
| BTL 排名分数 | `strength_score` | assay 或候选药物的相对优先级（`robin/robin/assays.py:230-243`; `robin/robin/candidates.py:468-520`） |
| Finch 轨迹 | `PARALLEL_ANALYSIS` | 多条 notebook 分析轨迹；公共代码为 5，论文正文说 8（`robin/robin/analyses.py:13`; `paper source/paper/hybrid_auto/paper.md:66`） |

### 5. 计算流程

Robin 的计算流程可以概括为：

```text
疾病名称
  -> 生成 assay 文献查询
  -> Crow 总结疾病机制和 in vitro 模型
  -> LLM 生成 assay 候选
  -> LLM 成对 judge + BTL 排名
  -> 选择最高 ranked assay
  -> 生成候选药物查询
  -> Crow/Falcon 生成候选药物报告
  -> LLM 成对 judge + BTL 排名
  -> 人类执行湿实验
  -> Finch 进行 flow/RNA-seq notebook 分析
  -> consensus insight
  -> 作为下一轮候选生成上下文
```

#### 5.1 assay 选择

给定疾病后，Robin 先生成关于疾病病理和可测机制的问题，然后调用 Crow 回答这些问题。论文 dAMD 案例里，Robin 阅读并综合了大量 RPE phagocytosis 和 dAMD 相关文献，提出 10 个可测试机制，再为每个机制生成 in vitro model 报告（`paper source/paper/hybrid_auto/paper.md:60-74`）。

代码中，`robin/robin/assays.py:27-277` 实现了 assay query 生成、Crow 调用、assay hypothesis 生成、成对比较排名和 candidate goal 合成。这个模块把“疾病问题”转成“可实验测试的候选 assay”。

#### 5.2 候选药物生成

选定 assay 后，Robin 继续进行候选药物发现。论文中它生成 30 个候选药物，并调用 Falcon 对每个分子生成更深入的报告，报告包括为什么该药物适合干预对应疾病机制以及潜在限制（`paper source/paper/hybrid_auto/paper.md:62-76`）。代码中，`robin/robin/candidates.py:30-520` 对应候选生成、Falcon 报告、LLM 成对判断、BTL 排名和 CSV 输出。

这里的 ranked list 应该理解为“下一步实验优先级”，不是疗效预测。论文第一轮测试了 Exendin-4、Fingolimod、MFGE8、Y-27632、AICAR+TUDCA 等候选，其中 Y-27632 在 ARPE-19 phagocytosis assay 中增强吞噬信号（`paper source/paper/hybrid_auto/paper.md:82`）。

#### 5.3 成对比较和 BTL 排名

Robin 的主要数学结构是 pairwise tournament ranking。LLM judge 每次比较两个 assay 或两个候选药物，输出 winner 和 loser。然后代码把这些 winner-loser 对输入 Bradley-Terry-Luce 模型：

```text
choix.ilsr_pairwise(n_items, games, alpha=0.1)
```

其中 `games` 是成对比较结果。输出的 strength score 表示 LLM judge 在给定文献报告和评价标准下对某个候选的相对偏好。它不是药效大小，也不是实验成功概率。

当候选数为 $n$ 时，全部无序比较数为：

$$
\frac{n(n-1)}{2}
$$

公共代码最多抽样 300 个 pairwise games，并使用固定 seed 621（`robin/robin/utils.py:422-453`）。因此候选很多时，排名是一个抽样 tournament 的估计，而不是完整全比较。

#### 5.4 Finch 数据分析和 consensus

实验完成后，Robin 将 flow cytometry 的 `.FCS` 文件或 RNA-seq gene counts 交给 Finch。论文写明，由于 flow gating 和 RNA-seq 过滤标准会影响结果，而且 LLM agent 本身有随机性，Robin 配置了多条 Finch 分析轨迹，每条轨迹独立在 Jupyter notebook 中写代码、运行分析并输出结果，最后再做 consensus（`paper source/paper/hybrid_auto/paper.md:66`）。

代码确认 Finch 分析是 notebook-agent 式流程，不是固定的手写统计函数。`robin/robin/analyses.py:54-98` 规定 flow/RNA 分析输出文件和 consensus 文件，`finch/src/fhda/notebook_env.py:215-245` 与 `finch/src/fhda/notebook_env.py:286-339` 支持 notebook cell 编辑和重新执行。

### 6. dAMD 案例结果

Robin 首先把 dAMD 转换为 RPE phagocytosis enhancement 这个可测机制。Figure 2 显示第一轮 ARPE-19 pHrodo bead assay 中，Y-27632 相对 DMSO 增强 phagocytosis MFI，MFGE8 起到类似阳性对照的作用。这个结果支持 ROCK inhibition 是一个值得继续验证的 in vitro 方向，但不能直接推出临床 dAMD 疗效。

随后，Robin/Finch 建议并分析 Y-27632 处理后的 RNA-seq。论文报告 Finch 的 DGE 和 GO 分析发现 actin filament organization、small GTPase signaling、autophagy 等通路变化，并突出 ABCA1 约 3 倍上调、adjusted p = 2.13e-83（`paper source/paper/hybrid_auto/paper.md:86-88`）。这给出一个机制假设：ROCK inhibition 可能既影响吞噬时的 cytoskeleton dynamics，也影响脂质外排和自噬相关通路。但 ABCA1 是否因果驱动 phagocytosis 仍需进一步实验验证。

把第一轮实验 insight 加入下一轮候选生成后，Robin 提出了 ripasudil。论文第二轮 ARPE-19 实验中，ripasudil 的 phagocytosis 增强强于 Y-27632，且在人 primary RPE-SC / ROS assay 中也保持更强 potency；KL001 也在 RPE-SC 中被识别为 hit（`paper source/paper/hybrid_auto/paper.md:94-106`）。这支持“实验反馈能改进下一轮候选优先级”的核心 claim。

### 7. 图像证据怎么支持方法 claim

Figure 1 是系统结构图：疾病输入、假设生成、实验、Finch 数据分析和结果解释构成闭环。Figure 2 连接 assay 选择和第一轮 flow cytometry 分析，显示 Robin 选择 RPE phagocytosis 并由 Finch 进行 gating 和 phagocytosis readout。Figure 3 展示 RNA-seq 的 volcano plot、跨 Finch 轨迹的一致性和 GO enrichment。Figure 4 展示反馈迭代后 ripasudil 和 KL001 的实验支持，尤其是 ripasudil 在 ARPE-19 和 RPE-SC 中都优于 Y-27632。

因此，图像证据支持的是“体外发现循环”和“候选优先级改进”，不是 in vivo 治疗效果。

### 8. 代码和论文的一致性

代码与论文高度一致的部分包括：

- Robin API 暴露 assay generation、candidate generation、data analysis 三个阶段（`robin/robin/__init__.py:1-12`）。
- Crow/Falcon 的 agent role 在配置中明确存在（`robin/robin/configuration.py:242-263`）。
- assay 和 candidate 都使用 LLM 成对比较加 BTL 排名（`robin/robin/assays.py:230-243`; `robin/robin/candidates.py:468-520`）。
- flow cytometry prompt 要求 gating、MFI、DMSO 比较和 `flow_results.csv`（`robin/robin/prompts.py:279-314`）。
- Finch 确实是 notebook 执行型数据分析代理（`finch/src/fhda/notebook_env.py:215-245`）。

主要差异和缺口包括：

- 公共默认参数是 3 queries、3 assays、5 candidates，而论文运行规模是 5、10、30；论文规模出现在 `robin_full.ipynb:39-41`。
- 论文说 Finch 对实验分析启动 8 条轨迹，但公共 `robin/robin/analyses.py:13` 设置 `PARALLEL_ANALYSIS = 5`。
- 论文描述 RNA-seq demultiplexing、HISAT2 alignment 和 featureCounts 由人类完成；公共仓库没有完整的本地 raw RNA-seq alignment 脚本。
- 完整复现实验图需要 Edison/FutureHouse 平台、API key、部分实验数据和平台 trajectories；公共 repo 不能单独一键重现全部论文结果。

### 9. 复现性和使用注意

Robin 的公共代码适合理解和部分复现工作流结构，但不是完整实验复现包。Code Availability 写明 Robin 和 Finch 代码公开（`paper source/paper/hybrid_auto/paper.md:349`），代码仓库也包含示例 notebooks 和 dAMD 输出快照。然而 Crow、Falcon 和 Finch 的真实运行依赖 Edison/FutureHouse 平台，湿实验数据和人类 preprocessing 也不完全在 repo 中。

因此使用 Robin 时要区分三类结论：

- **论文 claim**：Robin 在 dAMD 体外实验中找到 ripasudil/KL001，并展示闭环工作流。
- **代码验证行为**：公共代码支持 Crow/Falcon/Finch 编排、pairwise judge、BTL ranking、Finch prompt/consensus。
- **未验证或缺失**：完整湿实验复现、全部平台轨迹、8 条 Finch trajectory 的公开配置、raw RNA-seq alignment pipeline。

### 10. 一句话总结

Robin 不是一个单一预测模型，而是一个把文献检索、LLM 假设生成、BTL 排名、湿实验反馈和 Finch notebook 数据分析连接起来的闭环发现系统；它在 dAMD 案例中产生了有体外证据支持的候选药物优先级，但临床有效性、体内验证和完整公共复现仍然是未完成问题。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Robin: A Multi-Agent System for Automating Scientific Discovery

### Motivation And Novelty

Robin is designed for a bottleneck in biomedical discovery: scientists often need to connect disease mechanisms, in vitro assays, drug pharmacology, and new experimental results across hundreds of papers. The paper argues that many repurposing opportunities are delayed because these connections are hard to synthesize manually.

The method's novelty is the full loop. Robin does not only search papers or propose hypotheses. It selects an assay, proposes therapeutic candidates, lets humans run wet-lab tests, analyzes the resulting data through Finch, and feeds the experimental interpretation back into the next candidate-generation round.

Compared with prior systems such as autonomous chemical research agents (Nature, 2023), AI Scientist (arXiv, 2024), TxGemma-style therapeutic agents (arXiv, 2025), and AI co-scientist systems (arXiv, 2025), Robin is positioned as a lab-in-the-loop biology discovery workflow rather than only a hypothesis generator, computational benchmark agent, or chemistry automation tool.

### Method Overview

The input is a target disease name. In the paper's demonstration, the disease is dry age-related macular degeneration (dAMD).

Robin first generates literature-search queries and uses Crow to summarize disease mechanisms and assay options. It asks an LLM to propose assay hypotheses, then ranks them by pairwise LLM judging and a Bradley-Terry-Luce model implemented with `choix`. The top assay is turned into a candidate-generation goal.

Candidate generation follows the same pattern: literature queries, Crow summaries, LLM-generated candidates, Falcon deep reports, pairwise judging, and BTL ranking. Human scientists then run wet-lab experiments. Finch analyzes flow cytometry or RNA-seq data through notebook trajectories and consensus analysis. The resulting experimental insights are appended to later candidate-generation prompts, closing the loop.

### Evaluation

In the dAMD case study, Robin selected RPE phagocytosis enhancement as an assay strategy. In the first ARPE-19 phagocytosis screen, Y-27632 increased phagocytosis relative to DMSO. Finch then analyzed RNA-seq follow-up data and highlighted ABCA1 plus actin/autophagy-related pathways.

After incorporating experimental feedback, Robin proposed a second candidate round. Ripasudil, an approved ROCK inhibitor, showed stronger phagocytosis enhancement than Y-27632 in ARPE-19 and primary human RPE-SC assays. KL001 was also identified as a hit in primary RPE-SC. These results support Robin as an in vitro hypothesis-generation accelerator, but they do not establish in vivo or clinical dAMD efficacy.

Architecture validation shows that removing Falcon or both Crow and Falcon increases hallucinated references or worsens proposal ranking. Finch outperforms a Claude 3.7 Sonnet no-harness baseline on a 170-question BixBench subset, but its overall accuracy remains modest, especially for multi-step bioinformatics.

### Reproducibility

**Rating: 3 / 5.**

The public code is useful and matches the main workflow structure. It includes the Robin package, Finch code, notebooks, prompts, and sample dAMD outputs. The source confirms Crow/Falcon configuration, pairwise LLM ranking, BTL scoring, Finch-style notebook execution, and flow/RNA analysis prompts.

The limiting factor is that the full paper is not locally reproducible from the repository alone. Crow, Falcon, and Finch depend on Edison/FutureHouse platform access and API keys. The public defaults are smaller than the manuscript run, and the paper says Finch used eight trajectories while the public code sets five. The raw wet-lab data, exact hosted trajectories, human analysis scripts, and full RNA-seq alignment pipeline are not packaged as a standalone reproduction path.

### Key Takeaway

Robin is best understood as a structured, literature-grounded, lab-in-the-loop discovery agent. Its strongest contribution is workflow integration: candidate generation and experimental data analysis inform each other. Its strongest limitation is that biological validation remains in vitro and public reproducibility depends on private platform infrastructure.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
