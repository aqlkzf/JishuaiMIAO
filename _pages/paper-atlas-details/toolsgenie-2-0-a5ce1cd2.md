---
layout: default
permalink: /paper-atlas/toolsgenie-2-0-a5ce1cd2/
title: "ToolsGenie 2.0"
nav: false
wide: true
description: "生物信息学任务经常需要选择工具、安装依赖、下载参考基因组、检查中间文件并处理失败。传统 LLM 代理虽然可以生成代码，但在多轮交互、异构环境和大规模文件上容易失稳。ToolsGenie 2.0 的目标是让用户用自然语言和文件驱动可重复的分析流程（论文第 18-27 行）。 Supervisor 只处理会话、计划和摘要；KnowledgeAgent 查询网页和文献；"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>ToolsGenie 2.0</h1>
    <p>ToolsGenie 2.0: A Scalable and Extensible Multi-Agent System for Bioinformatics Automation</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ToolsGenie 2.0 方法解读

### 它解决什么问题

生物信息学任务经常需要选择工具、安装依赖、下载参考基因组、检查中间文件并处理失败。传统 LLM 代理虽然可以生成代码，但在多轮交互、异构环境和大规模文件上容易失稳。ToolsGenie 2.0 的目标是让用户用自然语言和文件驱动可重复的分析流程（论文第 18-27 行）。

### 核心架构

```text
自然语言 + 文件摘要
        |
        v
Supervisor（ReAct 计划与调度）
  |             |              |
Knowledge   Reference       Executor
联网/文献    参考资源         生成、执行、调试代码
        \      |              /
          LangGraph 共享状态
       元数据、结果、代码、参数
                |
                v
          验证后的结果与文件路径
```

Supervisor 只处理会话、计划和摘要；KnowledgeAgent 查询网页和文献；ReferenceAgent 从缓存或 AWS iGenomes 获取 FASTA、GTF 和预构建索引；ExecutorAgent 生成 Python、R 或 Shell 代码，在受控 Docker 环境运行，捕获 stdout/stderr，并循环调试。输出必须存在、非空且格式正确，超过重试上限后将失败交回 Supervisor（论文第 170-191 行）。

### 两层扩展与记忆

第一层是通过 LangGraph 工具调用接口注册新的领域或实用 sub-agent；第二层是通过配置注册 Biomni、STELLA 等外部工具，由 Executor 生成代码调用（第 206-218 行）。会话/计划记忆和执行状态分离：前者保持简洁，后者保存文件元数据、中间结果、已执行代码和参数。保存代码使后续轮次可以复用或重新执行（第 194-203 行）。

### Docker 选择

Executor 在生成代码时识别依赖，在执行时从本地缓存、Docker Hub、Quay.io 和 Wave 搜索匹配镜像，优先选择已安装依赖的精简镜像；Supervisor 将复杂任务拆成较小步骤以减少每次调用的依赖冲突（第 221-224 行）。论文没有给出排序打分、镜像 digest 固定、漏洞扫描或缓存失效规则，这些细节为 `Not found`。

### 结果

十个 GPT-4.1 任务、每项三次重复中，动态镜像的成功率为 83.3%，通用镜像为 56.7%；成功任务平均耗时从 913.0 秒降至 257.3 秒。一个 Q5 运行的 DESeq2 代码生成错误被归因于 LLM 的非确定性（第 87-104 行）。

与 Claude-4-Sonnet 配置的 Biomni 比较时，140 个内部问题上 ToolsGenie 为 68.6% 对 60.0%，成本 $0.51 对 $0.52；BixBench 205 题上为 51.7%（106/205）对 56.1%（115/205），但成本更低（$0.49 对 $0.67）。大文件集合的文件描述截断和跨代理摘要丢失是主要失败原因（第 122-140 行）。

### 可复现性边界

论文只指向 PromptBio 云平台，没有提供本文方法的公共代码仓库、提示词、数据集副本、镜像选择实现或完整运行脚本。上述架构和数字均有论文/图像证据，但本地不能据此重建一个可运行的 ToolsGenie 2.0 实例。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ToolsGenie 2.0

### Problem

Bioinformatics automation is limited by manual tool selection, dependency installation, reference-data acquisition, validation, and context management. Earlier LLM agents automate code generation but generally do not support multi-turn user guidance or reliable execution across heterogeneous software environments (paper, lines 18-27).

### Proposed System

ToolsGenie 2.0 is a cloud-deployed, LangGraph-based ReAct multi-agent system. A Supervisor Agent turns natural-language requests and pre-summarized file metadata into a plan, then invokes an ExecutorAgent for code generation/execution/debugging, a KnowledgeAgent for web and literature retrieval, and a ReferenceAgent for cached or public reference resources. Its two extension points are registered sub-agents and external toolsets invoked by the ExecutorAgent (lines 60-84, 170-218).

The execution design combines Docker image selection with a constrained sandbox, validation of input/intermediate/output files, and a two-branch memory model: concise conversation/plan context remains with the Supervisor, while file metadata, artifacts, code, and parameters remain in LangGraph shared state. Executed code is retained for later re-execution or reuse (lines 69-84, 188-203, 221-224).

### Evidence

On ten GPT-4.1 tasks repeated three times, Docker image selection produced 83.3% mean success versus 56.7% for generic images and reduced mean successful-task execution time from 913.0 s to 257.3 s; one Q5 failure was attributed to non-deterministic DESeq2 code generation (lines 87-104). A ReferenceAgent reduced the need to download/build STAR references, and Biomni integration made an ADMET workflow consistent across GPT-4.1 and Claude-4-Sonnet (lines 107-119).

Against Biomni with Claude-4-Sonnet, ToolsGenie reached 68.6% versus 60.0% on 140 in-house questions at similar cost ($0.51 vs $0.52), but 51.7% (106/205) versus 56.1% (115/205) on BixBench at lower cost ($0.49 vs $0.67). The BixBench deficit was concentrated in large, heterogeneous file collections whose descriptions were truncated or incompletely summarized between agents (lines 122-140). STELLA was not fully benchmarked because selected tasks took 7.59-7.81 hours and used far more tokens (line 143).

### Reproducibility

The paper is a bioRxiv preprint and names PromptBio (`platform.promptbio.ai`) as the deployment surface, but the acquisition search found no paper-owned public repository, supplementary Markdown, benchmark files, prompts, image-selection policy, retry thresholds, or implementation source. The local snapshot is therefore `paper-only`; the architecture, metrics, and limitations are source-grounded, while runnable reproduction is `Not found` in the searched article HTML, converted Markdown, and acquisition sidecars.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
