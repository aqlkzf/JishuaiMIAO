---
layout: default
permalink: /paper-atlas/towards-autonomous-mechanistic-reasoning-in-virtual-cells-8d2b7cab/
title: "Towards_Autonomous_Mechanistic_Reasoning_in_Virtual_Cells"
nav: false
wide: true
description: "虚拟细胞需要回答“某个药物或基因扰动在特定细胞环境中会怎样影响细胞”，但普通大模型容易生成无法核验的自然语言解释。本文把解释限制为由生物学动作组成的有向无环图（DAG），使每一个步骤都具有明确参数，并可以被专门的生物学验证器检查。作者强调这描述的是机制合理性和可证伪性，不等同于严格的干预因果发现。 输入为 x=(p,c)：p 是化合物、敲低等扰动，c 是细胞类型、疾病模型等上下文。"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>Towards_Autonomous_Mechanistic_Reasoning_in_Virtual_Cells</h1>
    <p>Towards Autonomous Mechanistic Reasoning in Virtual Cells</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2604.11661" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Towards_Autonomous_Mechanistic_Reasoning_in_Virtual_Cells">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/yunhuijang/VC-TRACES" target="_blank" rel="noopener noreferrer" aria-label="Open code for Towards_Autonomous_Mechanistic_Reasoning_in_Virtual_Cells">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## VCR-Agent 方法说明

### 它解决什么问题？

虚拟细胞需要回答“某个药物或基因扰动在特定细胞环境中会怎样影响细胞”，但普通大模型容易生成无法核验的自然语言解释。本文把解释限制为由生物学动作组成的有向无环图（DAG），使每一个步骤都具有明确参数，并可以被专门的生物学验证器检查（`paper.md:52-106`）。作者强调这描述的是机制合理性和可证伪性，不等同于严格的干预因果发现（`paper.md:84`, `paper.md:327-330`）。

### 输入、输出与核心表示

输入为 $x=(p,c)$：$p$ 是化合物、敲低等扰动，$c$ 是细胞类型、疾病模型等上下文。输出为：

$$\mathcal{G}=(\mathcal{V},\mathcal{E}),\qquad f_\theta:x\rightarrow\mathcal{G}.$$

节点是预定义动作及参数，边表示一个动作启用或影响另一个动作。典型动作包括 `set_context`、`binds_to`、`modulates_molecule_activity`、`regulates_expression`、`localizes_to` 和 `induces_phenotype`；附录给出完整参数模式（`paper.md:385-414`）。例如：

```text
binds_to(id, actor, target, {affinity, unit, residues_actor, residues_target, via, confidence})
```

### 计算流程

```text
(扰动 p, 细胞上下文 c)
        -> HunFlair2 实体识别
        -> StarkPrimeKG/Harmonizome/PubMed/Wikipedia 检索
        -> Claude 4 生成知识支撑的报告
        -> Claude 4 将报告转成动作节点和 DAG
        -> DTI/DE（以及 LOC/PHENO）验证器
        -> 删除低可信度或与证据矛盾的声明
        -> VC-Traces: report + explain + dag + explain_verified
```

报告生成器先识别化合物、基因和疾病等实体，再从四类知识源收集关系、基因信息、文献和背景知识；没有精确图节点时使用 PubMedBERT 相似度回退。Claude 4 将检索结果总结为报告（`paper.md:127-148`）。解释构造器只接收这个报告并生成结构化动作，从而把知识获取与结构化推理解耦（`paper.md:112-118`, `paper.md:151-154`）。

验证器阶段中，DTI 用 Boltz-2 估计药物-蛋白结合可信度；DE 查询 Tahoe-100M 等扰动表达数据，检查调控方向。低于阈值 $\tau$ 的 `binds_to` 轨迹被丢弃，错误的 DE 基因参数被删除而不是修改其余声明（`paper.md:174-204`）。LOC 使用 UniProt/Human Protein Atlas，PHENO 查询 Cellular Phenotype Database（`paper.md:748-766`）。

### 数据集与下游任务

作者从 Tahoe-100M 的 18,950 个化合物-细胞上下文对构建 VC-Traces。公开数据的六列是 `perturbation`、`question`、`report_text`、`explain`、`dag` 和 `explain_verified`（`VC-TRACES/README.md:42-51`）。TahoeQA 为两个二分类任务：是否差异表达、表达方向。标签包括每个扰动的 top-25 上调、top-25 下调和 100 个非调控基因；通过 pseudo-bulk 负二项 GLM、Wald 检验和校正 $p<0.05$ 获得（`paper.md:252-279`）。

Qwen3-4B 有两种 SFT：SFT-Prompt 把验证后的解释作为输入上下文；SFT-Generate 先生成解释再给出答案（`paper.md:273-282`）。论文报告 VCR-Agent 原始输出的 validity=1.000、verifiability=0.945、DTI=0.725、DE=0.528，并称过滤掉 28.2% 错误 DTI 声明、修正 87.3% DE 动作（`paper.md:186-195`, `paper.md:237-243`）。

### 代码与局限

可获得的 GitHub 快照 `yunhuijang/VC-TRACES`（commit `607e466...`）包含 parquet 数据和 `demo.ipynb`。Notebook 能加载数据、展示样例并用正则表达式解析动作节点和 DAG 边（`demo.ipynb:81-84,601-711`），但没有检索器、LLM prompt、验证器、过滤器或 TahoeQA 训练代码。因此完整方法只能依据论文复现；数据查看也需要未在 `pyproject.toml` 声明的 parquet 引擎，当前环境因磁盘配额不足未能安装 `pyarrow`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Towards Autonomous Mechanistic Reasoning in Virtual Cells

### Problem

Virtual-cell models can predict perturbation responses but usually provide correlations or free-form rationales that are difficult to verify. The paper targets factual grounding, explicit mechanistic dependencies, and scalable reasoning-trace curation for chemical and genetic perturbations (`paper.md:17-51`).

### Proposed System

VCR-Agent is a two-stage multi-agent pipeline. A report generator extracts biomedical entities and retrieves evidence from StarkPrimeKG, Harmonizome, PubMed, and Wikipedia; Claude 4 synthesizes that evidence into a report. An explanation constructor converts the report into typed action primitives connected as a DAG. DTI and DE verifiers, with LOC and PHENO extensions, filter low-confidence or contradicted claims (`paper.md:109-204`).

The resulting VC-Traces dataset contains 18,950 Tahoe-100M compound/context pairs. Each record exposes the perturbation, question, report, structured explanation, DAG, and verified explanation (`paper.md:219-223`; `VC-TRACES/README.md:42-51`).

### Evidence and Results

On raw generation, VCR-Agent reaches validity 1.000, verifiability 0.945, DTI 0.725, and DE 0.528, outperforming the listed open and closed baselines. Subsequent filtering excludes 28.2% of faulty DTI claims and refines 87.3% of DE actions (`paper.md:186-195`, `paper.md:237-243`). In TahoeQA, Qwen3-4B SFT conditioned on verified explanations is the strongest configuration; the paper reports gains for both DE and direction-of-change prediction and better novel-compound generalization (`paper.md:252-285`).

### Reproducibility

The public `VC-TRACES` repository at commit `607e466602e00eafc1409e84d57a558f60d51f40` contains the 2.8 MB parquet release and a demo notebook, not the VCR-Agent retrieval/generation/verifier/training implementation. The notebook verifies the data schema and shows one trace/DAG parser (`VC-TRACES/notebook/demo.ipynb:81-84,601-711`), but full execution was not possible in this environment because `pyarrow` was absent and installation exceeded the disk quota. Its `pyproject.toml` declares pandas only, although `read_parquet` requires a parquet engine (`VC-TRACES/pyproject.toml:1-9`).

Overall reproducibility: **2/5** for the complete method; **4/5** for inspecting the released dataset. The method is clearly specified in the paper, but the core agent and verifier code, prompts, model assets, and end-to-end training scripts are not in the available public snapshot.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
