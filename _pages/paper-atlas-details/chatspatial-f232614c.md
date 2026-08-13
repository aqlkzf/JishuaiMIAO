---
layout: default
permalink: /paper-atlas/chatspatial-f232614c/
title: "ChatSpatial"
nav: false
description: "ChatSpatial 不是新的聚类、解卷积或细胞通信算法，而是一个 software orchestration layer。它把 60 多种已有空间转录组方法封装到 20 个高层 MCP 工具中，让大语言模型负责理解用户意图和选择参数，而真实计算仍由 Scanpy、Squidpy、CellChat、RCTD、inferCNV 等确定性程序执行。"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>ChatSpatial</h1>
    <p>ChatSpatial: Schema-Enforced Agentic Orchestration for Reproducible and Cross-Platform Spatial Transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.02.26.708361" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ChatSpatial">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/cafferychen777/ChatSpatial" target="_blank" rel="noopener noreferrer" aria-label="Open code for ChatSpatial">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ChatSpatial：用受约束工具调用编排空间转录组分析

### 方法定位

ChatSpatial 不是新的聚类、解卷积或细胞通信算法，而是一个 software orchestration layer。它把 60 多种已有空间转录组方法封装到 20 个高层 MCP 工具中，让大语言模型负责理解用户意图和选择参数，而真实计算仍由 Scanpy、Squidpy、CellChat、RCTD、inferCNV 等确定性程序执行。

核心目标是把 LLM 从“现场写 Python/R 代码”改造成“在预先定义的表单里选择工具和填写参数”。这减少了不存在的包、错误 API、语法错误和跨语言转换代码等失败模式，但并不保证统计方法选择一定正确，也不消除 LLM 对模糊问题的误解。

### 三层执行架构

#### 1. MCP Tool Layer

`chatspatial/server.py` 创建 FastMCP server，并用 20 个 `@mcp.tool()` 暴露高层任务，例如数据加载、预处理、空间域识别、注释、解卷积、细胞通信、空间统计、CNV、轨迹、速度、配准和结果导出。每个工具的输入由 Pydantic model 描述。

论文统计 441 个参数，其中 358 个（81.2%）通过 `Literal` 枚举、数值边界或默认值受到约束，83 个主要是数据集 ID、列名等自由文本。这个数字来自论文；本次源码核验确认约束机制广泛存在，但没有重新实现论文的参数统计脚本，因此不把 441/358 当成本地独立复算结果。

例如解卷积的 `method` 不能随意写成一个包名，而必须落在 schema 允许的集合中。Pydantic 在工具执行前检查类型和范围，因此 schema 能阻止无效方法名和越界参数进入算法层。

#### 2. Method Dispatch Layer

server wrapper 接收经过验证的 parameter object，创建 `ToolContext`，再调用相应类别模块。一个类别可继续依据 `params.method` 路由到具体实现；`tools/deconvolution/__init__.py` 的 registry 保存方法名、模块名、依赖和能力，`_dispatch_method()` 用动态 import 载入 RCTD、CARD、Cell2location 等实现。

这种设计把面向 LLM 的接口数量压到 20 个，同时保留 60 多种算法。用户看到的是“deconvolve data”这一类任务，schema 中的方法枚举决定底层执行哪一个算法。

#### 3. Algorithm Wrapper Layer

具体 wrapper 负责：

- 从 `DefaultSpatialDataManager` 按 `data_id` 取得 AnnData；
- 检查表达矩阵、空间坐标、分组列和参考数据；
- 转换底层库要求的数据格式；
- 调用原始算法；
- 把结果写回 AnnData 或标准化为 Pydantic result；
- 将结果缓存在当前会话的内存数据管理器中。

因此 reproducibility 的含义主要是“相同工具和参数进入同一软件路径”，而不是所有数值结果跨环境必然逐位相同。底层包版本、随机数、硬件和算法自身仍可产生差异。

### 生物学知识怎样进入 LLM 决策

ChatSpatial 不训练一个新的领域模型，而是把经验写入两类文本：

1. **Field descriptions**：每个 schema 字段描述参数含义、适用平台和建议范围，例如 Visium 六邻域、单细胞分辨率平台更大的邻居数，以及不同 clustering resolution 的解释。
2. **MCP Server Instructions**：会话启动时注入总体流程和工具关系，例如先 `load_data`，多数分析前运行 `preprocess_data`，spot-based 平台适合解卷积，而 MERFISH/Xenium/CosMx 通常不需要。

这是一种 documentation-driven parameter inference。优点是不需要微调；缺点是建议依赖人工维护，且描述中的经验规则不等于自动优化后的最佳参数。

### 状态和多步对话

`DefaultSpatialDataManager` 用内存字典保存数据和结果，以 `data_1`、`data_2` 等 ID 连接后续工具。`ToolContext` 让所有算法以统一方式读取、更新或新增 AnnData，并把进度发回 MCP context。这样后续提示可以引用已有 `data_id`，不必重新加载数据。

边界是状态默认不跨 server session 持久化；简单计数器也不是全局数据版本标识。论文强调 stateful conversation，本地代码同时说明这种状态目前是进程内状态。

### Python 与 R 如何跨生态执行

Python 侧以 AnnData 为共同对象。R 工具按需加载 `rpy2` 和 `anndata2ri`，并将表达矩阵、metadata、坐标或 SingleCellExperiment/Seurat 所需对象送入 R。例如 RCTD wrapper 把空间与参考计数、细胞类型和坐标转为 R 对象，再把 weight matrix 转回 Python；CellChat wrapper 直接调用 R CellChat。

因此“自动桥接”是对用户和 LLM 隐藏转换细节，并不表示无需安装 R。缺少 R、rpy2、anndata2ri 或目标 R package 时，dependency/error 层会返回明确错误。

### 论文怎样验证系统

#### OSCC 复现

ChatSpatial 在 12 个 GSE208253 Visium 样本上复现 Tumor Core 与 Leading Edge 结构。它使用 Leiden + 空间邻接和 FlashDeconv，而原研究使用 Louvain/CCA 与 CARD，因此是“中心生物结论的复现”，不是逐步骤复制。Leading Edge 中 macrophage 为 11/12、fibroblast 为 10/12；CellChat 找到 ECM–syndecan 方向性相互作用，Moran's $I$ 又把 COL1A1 和 FN1 排在空间变异基因前 1%。

#### HGSOC 复现

在 GSE211956 的 8 个样本中，RCTD 定义 tumor-enriched spots，inferCNV 加 Leiden 得到每位患者 3–6 个 CNV clusters。与原研究的 12 类参考和人工 dendrogram 分割不同，本分析使用公开的 8 类参考与自动聚类，所以结果应解释为异质性模式一致，而不是 clone 标签完全对应。P3 的 cell-type markers 空间结构显著，而 CNV markers 相对背景的 Moran's $I$ 差异不显著（图 3f，$p=0.07$）。

#### 功能覆盖和跨模型一致性

- 28 个功能场景全部完成，其中 3 个模糊提示需要一次对话修正。
- 8 prompts × 3 LLMs × 10 repeats = 240 trials，温度为 1.0。
- 在这些刻意映射到单一工具类别的提示中，tool selection 为 100%；schema-constrained parameters 跨模型一致率 75.7%，free-text 为 58.3%。
- 自由代码基线中，Python-native tasks 的 syntax error rate 为 Gemini 41.7%、Claude Haiku 15.0%；GPT-5 Mini 在 8 项中的 5 项没有生成代码。

这些结果证明的是受控提示下的 workflow-level consistency，不代表任意真实问题都是确定性的。主案例使用 Claude Sonnet 4.5，跨模型实验使用 Gemini 2.5 Flash、Claude Haiku 4.5 和 GPT-5 Mini；摘要所说“seven LLM platforms”还包括部署客户端/平台层面的验证，不能与三模型重复实验混为同一统计设计。

### 三张主图怎么读

- **图 1**：从 free-form code 与 schema tool-calling 对比开始，再看 MCP server、Python/R bridge、工具类别和三轮对话。
- **图 2**：OSCC 中从空间域到解卷积、CellChat，再到 Moran's $I$ 的跨方法链。
- **图 3**：HGSOC 中从 RCTD tumor fraction 到 inferCNV clusters、患者比较和空间统计。

OCR 目录还含 Table 1、Table 2 与补充表图像。补充方法和表格文本被合并在同一 `paper.md` 后半部分；没有找到独立的补充 PDF/Markdown。

### 论文—代码对应

- **Exact**：20 个 MCP tools、FastMCP server、Pydantic schema、三层 wrapper/dispatch 结构、内存 data manager、server instructions、rpy2/anndata2ri 路径和语义错误处理均可在本地源码定位。
- **Partial**：60+ 方法及论文工具表总体有实现，但当前源码还包含论文表未突出的方法；85 个 test files 也不与论文 28 个对话场景一一对应。
- **Paper-only experiment**：240 次跨模型实验、自由代码 baseline、OSCC/HGSOC 结果不是 package unit tests 的直接产物，本地源码存在不等于这些数值已重跑。

### 局限

- 模糊查询仍可能选错参数，且 3/28 场景需要修正。
- LLM API 有延迟、成本和临床数据隐私问题。
- 已发表案例可能进入过模型预训练；未公开数据的盲测更有说服力。
- 方法集合由维护者策展，不能覆盖所有新工具。
- 上游包 API 漂移要求持续维护 wrapper。
- 科学有效性最终继承底层方法及输入数据质量；schema 只能减少接口错误，不能修复错误生物学假设。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ChatSpatial — Paper Summary

### Motivation & Novelty

Spatial transcriptomics analysis requires navigating 60+ computational tools split across incompatible Python and R ecosystems, with each tool demanding distinct data formats (AnnData vs Seurat), conflicting dependencies, and specialized programming expertise. A typical workflow — e.g., spatial domain identification (Python, SpaGCN) followed by cell-cell communication (R, CellChat) — requires manual data conversion scripts and environment management, creating a bottleneck for biomedical researchers.

**Limitations of existing approaches:**
- **Direct programming**: High technical barrier; 15-42% syntax error rates when LLMs generate bioinformatics code (measured in this paper's experiments)
- **GUI platforms** (Loupe Browser, Giotto Viewer): Limited analytical scope, single-ecosystem, no cross-method chaining
- **LLM co-pilots** (QUST-LLM, SCassist): Assist with specific tasks within one ecosystem; no cross-platform integration
- **Autonomous agents** (STAgent, Lin et al., *bioRxiv* 2025; SpatialAgent, Wang et al., *bioRxiv* 2025): Generate free-form code → non-deterministic, hallucination-prone, poor reproducibility

**ChatSpatial's unique contributions:**
1. **Schema-enforced orchestration** via the Model Context Protocol (MCP): the LLM selects from pre-validated tool schemas with Literal enumerations and bounded parameters, rather than generating arbitrary code. This shifts the LLM's role from "writing a free-form essay" to "solving a fill-in-the-blank problem"
2. **Cross-ecosystem integration**: 60+ methods spanning Python and R unified through a single conversational interface, with automated AnnData ↔ Seurat conversion via rpy2
3. **Systematic validation**: Replication of two published studies (OSCC and HGSOC) + cross-model reproducibility experiments across 3 LLMs (Claude Haiku 4.5, Gemini 2.5 Flash, GPT-5 Mini)

---

### Method Overview

ChatSpatial is built on a 3-layer MCP architecture:

- **MCP Tool Layer**: 20 tools registered via `@mcp.tool()` with strict Pydantic schemas (441 parameters total, 81.2% schema-constrained)
- **Method Dispatch Layer**: Routes requests to algorithm-specific implementations based on `Literal` enum parameters
- **Algorithm Wrapper Layer**: Handles data preparation, library calls, and result standardization; rpy2 bridge for R methods

Domain expertise is injected directly into parameter schema descriptions (e.g., "For Visium, recommended k=6 for immediate neighbors; for MERFISH, k=10-15"), enabling the LLM to make context-aware parameter selections without fine-tuning or RAG.

**Analytical categories (60+ methods):** preprocessing, integration, cell type annotation (6 methods), spatial domain ID (6), deconvolution (8), cell-cell communication (4), SVG detection (3), differential expression (4), enrichment (5), spatial statistics (10+), trajectory (3), RNA velocity (2), CNV analysis (2), spatial registration (2).

See `doc_method.md` for detailed architecture and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Case Study 1: OSCC Tumor Architecture (Arora et al., *Nat. Commun.* 2023)
- **Dataset**: 12 OSCC Visium samples (GSE208253)
- **Replicated findings**: Tumor Core vs Leading Edge spatial domains; fibroblast/macrophage enrichment at LE (macrophages 11/12 samples, 92%; fibroblasts 10/12, 83%); COL1A1–SDC1 and FN1–SDC1 ECM-syndecan signaling via CellChat
- **Methodological differences**: ChatSpatial used Leiden clustering (vs Louvain + CCA in original) and FlashDeconv (vs CARD) — core biological conclusions concordant
- **Beyond replication**: Moran's I spatial autocorrelation showed CellChat-identified ligands (COL1A1 rank 20, FN1 rank 23) in top 1% of spatially variable genes

#### Case Study 2: HGSOC Subclone Analysis (Denisenko et al., *Nat. Commun.* 2024)
- **Dataset**: 8 HGSOC Visium samples (GSE211956)
- **Replicated findings**: RCTD deconvolution → inferCNV subclone identification → 3-6 CNV clusters per patient; tumor burden 2-98% across patients
- **Beyond replication**: Moran's I analysis showed cell type markers (CD14, KRT7, CDH5) in top 2% spatially variable genes; CNV-cluster markers not enriched (Mann-Whitney p=0.99)

#### Cross-Model Reproducibility (§2.3)
- **Setup**: 8 prompts × 3 LLMs × 10 repetitions = 240 trials at temperature=1.0
- **Tool selection**: 100% consistent (expected — unambiguous prompts)
- **Schema-constrained parameters**: 75.7% cross-model consistency (vs 58.3% for free-text)
- **Code generation baseline**: 15-42% syntax error rates for Python-native tasks; hallucinated non-existent packages (pyrctd, pyCellChat)

#### Functional Coverage
- 28 test scenarios across 4 categories (data handling, core analysis, conversational workflows, scalability)
- Validated from 300 spots (STARmap) to 930K+ cells (Xenium)
- All 28 passed; 3 required one round of conversational refinement for ambiguous prompts

---

### Reproducibility

**Rating: 4/5** — High for a software platform paper.

**Strengths:**
- Code fully open source (MIT license): https://github.com/cafferychen777/ChatSpatial
- Comprehensive test suite: 84 test files (66 unit, 16 integration, 2 e2e)
- Separate reproducibility repository for case study analysis scripts
- All datasets publicly available (GEO accessions provided)
- Detailed INSTALLATION.md and documentation site
- MCP server.json for standardized deployment

**Weaknesses:**
- R dependency installation non-trivial (requires rpy2 + multiple R packages)
- Case study reproducibility depends on LLM API access (Claude Sonnet 4.5 used for main results)
- Cross-model experiments at temperature=1.0 with deliberately unambiguous prompts — real-world queries would show more variability
- Authors acknowledge possible pretraining contamination (LLMs may have seen published study protocols)
- In-memory data management means no persistence across sessions

**Practical notes:**
- Python 3.11-3.13 required (3.12 recommended)
- 8GB+ RAM minimum, 16GB+ for large datasets
- Install tiers: core (27 packages) → extended → full (60+ methods)
- R environment optional but needed for CellChat, RCTD, scType, SingleR, CARD, Numbat, SCTransform

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
