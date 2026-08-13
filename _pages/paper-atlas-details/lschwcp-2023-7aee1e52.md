---
layout: default
permalink: /paper-atlas/lschwcp-2023-7aee1e52/
title: "LSCHWCP_2023"
nav: false
description: "这项工作把两个通常分离的问题连接起来： 如何在转录组测序数据中发现不局限于完整核酸参考基因组的 RNA 病毒样信号； 如何保留单细胞条形码，使病毒存在信息能够与同一细胞的宿主基因表达联合分析。 论文指出，既有流程往往至少缺少一项能力：参考覆盖范围受限、不能把核酸读段与蛋白参考做翻译搜索，或不能保留单细胞分辨率。"
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
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>LSCHWCP_2023</h1>
    <p>Detection of viral sequences at single-cell resolution identifies novel viruses associated with host gene expression changes</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-025-02614-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for LSCHWCP_2023">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/pachterlab/LSCHWCP_2023" target="_blank" rel="noopener noreferrer" aria-label="Open code for LSCHWCP_2023">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 单细胞分辨率病毒序列检测与宿主表达关联：方法详解

### 1. 论文要解决什么问题？

这项工作把两个通常分离的问题连接起来：

1. 如何在转录组测序数据中发现不局限于完整核酸参考基因组的 RNA 病毒样信号；
2. 如何保留单细胞条形码，使病毒存在信息能够与同一细胞的宿主基因表达联合分析。

论文指出，既有流程往往至少缺少一项能力：参考覆盖范围受限、不能把核酸读段与蛋白参考做翻译搜索，或不能保留单细胞分辨率（`paper.md:21-24`）。作者因此将 kallisto 的伪比对思想扩展到 PalmDB 的保守蛋白参考，并在下游建立宿主过滤、污染证据分层、病毒存在二值化和宿主表达预测模型。

本文档只解释公开论文中的计算框架和已审计的下游代码，不提供序列级操作、实验优化或病原体设计信息。

### 2. 核心创新

#### 2.1 从完整基因组依赖转向保守蛋白参考

PalmDB 收集了大量含 RNA 依赖性 RNA 聚合酶保守区域的蛋白参考。方法的核心思想是把核酸读段和氨基酸参考映射到同一种编码空间，再进行 kallisto 风格的伪比对，从而减少对完整病毒核酸基因组的依赖（`paper.md:174-183`）。对于单细胞数据，条形码随计数结果一起保留，因此输出不是只有样本级病毒总量，而是“细胞 × 病毒组”的矩阵。

需要明确区分论文方法与本地代码证据：**当前快照中不存在修改后的上游 kallisto 翻译搜索引擎源码**。本地仓库提供图表笔记本、参考资产、预计算结果和下游预测代码，但没有可逐行审计的 C/C++ 引擎补丁或构建系统。

#### 2.2 不把宿主—病毒歧义读段简单丢弃

宿主序列可能被误判为病毒，而过强的宿主过滤也可能删除真实或具有生物学歧义的信号。论文比较多种宿主 masking 策略，并允许把“同时支持宿主和病毒参考”的读段单独保留（`paper.md:67-81`）。因此，过滤强度本身成为敏感性分析的一部分，而不是隐藏在单一预处理选项中。

#### 2.3 在同一细胞中连接病毒存在与宿主状态

病毒计数在单细胞层面非常稀疏。论文把每个病毒在每个细胞中的计数转成存在/不存在，并对低频病毒进行阈值过滤（`paper.md:300-306`）。随后，将病毒矩阵与宿主表达矩阵按细胞条形码对齐，训练逐病毒的逻辑回归模型，检验宿主表达是否包含可重复的病毒存在信号。

### 3. 从输入到输出的完整计算框架

```text
转录组读段 + 单细胞条形码（若有）
        |
        v
核酸读段与蛋白参考进入共享编码空间
        |
        v
基于 PalmDB 的翻译伪比对，并保留条形码
        |
        +--> 可选宿主 masking；保留宿主—病毒歧义证据
        |
        v
细胞 × 病毒计数矩阵
        |
        v
宿主/病毒质控、条形码对齐、频率阈值、存在/不存在二值化
        |
        +--------------------------+
        |                          |
        v                          v
病毒在样本/时间/细胞类型中的分布     细胞 × 宿主基因表达矩阵
        |                          |
        +------------> 联合分析 <---+
                           |
                           v
逐病毒逻辑回归：宿主基因 + 可选供体/时间协变量
                           |
                           v
预测概率、准确率、敏感度、特异度、基因权重与富集分析
```

### 4. 逻辑回归部分的输入、变量与形状

对某一个病毒 $v$：

- 宿主表达矩阵：$X\in\mathbb{R}^{n\times G}$，$n$ 是细胞数，$G$ 是全部或高变宿主基因数；
- 病毒标签：$y_v\in\{0,1\}^{n}$，表示该细胞是否检测到病毒 $v$；
- 可选协变量矩阵：$C\in\{0,1\}^{n\times(A+T)}$，由 $A$ 个供体和 $T$ 个时间点的 one-hot 编码组成；
- 模型输出：每个测试细胞的病毒存在概率 $p_v$、分类指标，以及截距和各预测变量权重。

基础模型为：

$$
{\mathrm{ln}}\left(\frac{p}{1-p}\right)=\mathop{\sum }\limits_{i=1}^{N}{\beta }_{i}{x}_{i}+{\beta }_{0}.
$$

加入宿主基因、供体和时间协变量后：

$$
{\mathrm{ln}}\left(\frac{p}{1-p}\right)={\beta }_{0}+\mathop{\sum}\limits_{g\in G}{\beta }_{g}^{G}{x}_{g}+\mathop{\sum}\limits_{a\in A}{\beta }_{a}^{A}{y}_{a}+\mathop{\sum}\limits_{t\in T}{\beta }_{t}^{T}{z}_{t}.
$$

其中，$\beta_g^G$ 表示宿主基因与预测概率的关联权重；$\beta_a^A$ 和 $\beta_t^T$ 用于控制供体与时间结构。权重反映关联而不是因果作用。

### 5. 训练、测试与对照设计

论文对每个病毒随机抽取等量阳性和阴性细胞作为训练集，其余细胞作为测试集（`paper.md:324,342`）。由于部分病毒样信号高度集中在特定细胞类型，作者还设计了按细胞类型匹配阴性训练细胞的控制，以避免模型只是在识别细胞类型。另一个负对照是随机打乱训练标签；如果模型依赖真实的宿主—病毒关联，打乱后性能应回到随机水平附近。

四种主要模型组合是：

| 基因输入 | 协变量 | 目的 |
|---|---|---|
| 全部基因 | 无 | 最大表达信息的基础模型 |
| 全部基因 | 供体 + 时间 | 控制样本结构 |
| 高变基因 | 无 | 聚焦主要表达变异 |
| 高变基因 | 供体 + 时间 | 紧凑表达特征加样本控制 |

### 6. 本地代码如何对应论文

直接审计文件为 `LSCHWCP_2023/Notebooks/Figure_8/Figure_8bc/logisticRegression.py`：

- `51-77` 行：读取宿主与病毒 AnnData，构造共享条形码并对齐细胞；
- `79-101` 行：可选按测序深度和高变基因过滤；
- `203-300` 行：为单个病毒构造等量阳性/阴性训练数据，并可按细胞类型匹配；
- `303-329` 行：对供体和时间做 one-hot 编码；
- `348-377` 行：逐病毒抽样并拟合 sklearn 逻辑回归；
- `389-443` 行：计算测试准确率、敏感度、特异度、概率和模型权重；
- `445-459` 行：把结果序列化保存。

最终期刊 Fig. 6b,c 和 Extended Data Fig. 9 的 README 路由到同一 Figure_8bc 目录，因此图表笔记本与预测脚本形成了部分复现链。但笔记本内容和大型输出未被检查，六个随机种子的调度与聚合不能仅凭该 Python 文件确认。

### 7. 如何理解论文结果

- Fig. 2 显示翻译搜索计数与独立病毒载量测量在多种数据中一致，并报告较高的分类正确率。
- Fig. 3 显示宿主过滤越保守，保留的候选病毒组越少；大量歧义读段说明过滤策略会影响结论。
- Fig. 5-6 显示部分细胞类型特异的病毒样信号可以由宿主表达以超过 70% 的平均准确率预测，而低特异信号和打乱标签对照接近随机水平。
- Extended Data Fig. 10 的基因权重与通路结果适合生成假设。已知感染的相关通路达到显著性；论文明确指出两个重点新信号的校正后富集未达到显著，因此不能写成因果或确认性证据。

### 8. 复现性判断

总体代码—论文一致性为 **中等**，复现性约为 **3/5（部分复现）**：

- 可直接验证：下游矩阵对齐、基因/协变量选择、平衡抽样、逻辑回归、测试指标、权重和结果输出；
- 笔记本级证据：最终图号到原始分析目录的映射、回归运行与绘图文件存在；
- `Not found`：修改后的上游 kallisto 翻译搜索引擎源码、补丁和构建配置；
- 部分明确：具体图板的参数组合、六随机种子调度、环境版本和输入 AnnData 的完整生成链。

因此，这个快照足以学习论文的计算思想并审计下游预测分析，但不足以从源码端到端重现核心翻译搜索引擎。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Detection of viral sequences at single-cell resolution

### Problem

Most transcriptomic virus-detection workflows described by the paper depend on complete nucleotide reference genomes, lack translated nucleotide-to-protein search, or lose cell-barcode identity. This limits discovery beyond known references and prevents direct comparison of viral signal with host gene expression in the same cell (`paper.md:21-24`).

### Proposed technology

The paper extends kallisto conceptually with translated search against PalmDB, a broad collection of conserved RNA-dependent RNA polymerase references. Nucleotide reads and amino-acid references are mapped into a shared coded space for pseudoalignment while retaining sample or cell identity. The surrounding workflow adds alternative host-masking strategies, preserves host-virus ambiguous reads for downstream review, converts sparse cell-level viral counts to presence/absence, and joins the viral matrix with host expression.

At the downstream analysis stage, per-virus logistic-regression models predict viral presence from all or highly variable host genes, optionally adding donor animal and disease time point as covariates. Balanced positive/negative training samples, held-out evaluation, cell-type-aware controls, and scrambled labels are used to distinguish predictive host-expression structure from simple class or cell-type effects (`paper.md:321-348`).

### Evidence and main results

- Across bulk RNA-seq, SMART-Seq, and Seq-Well validation datasets, translated-search counts agree with independent viral-load measurements; displayed correlations include $r=0.83$, $r=0.90$, and $r=0.95$ (`paper.md:47-55`; Fig. 2).
- The paper reports 96.76% correct species-level taxonomic assignment in its reverse-translation validation, with 0.007% incorrect, 0.37% multimapped, and 2.86% not aligned (`paper.md:47`).
- Host-masking comparisons show a clear trade-off: more conservative masking reduces candidate viral groups, while explicit retention of ambiguous reads makes host overlap visible rather than silently discarding it (Fig. 3).
- In the macaque single-cell application, host-expression models predict several cell-type-specific viral signals at greater than 70% average accuracy, while low-specificity signals and scrambled-label controls remain near chance (`paper.md:136-150`; Figs. 5-6; Extended Data Figs. 9-10).
- Gene-weight analysis supports virus-related enrichment for the known infection. For highlighted novel signals, the paper reports suggestive immune-response associations but not adjusted-significant enrichment, so these results remain hypothesis-generating (`paper.md:147-150`).

### Interpretation and limitations

The work's main contribution is a connected detection-to-interpretation framework: broader conserved-protein search, barcode-preserving viral quantification, contamination-aware filtering, and cell-level host-response modelling. Its strongest evidence is methodological validation and controlled association, not definitive proof that every detected virus-like signal represents active infection. PalmDB is uncurated, reagent contamination is common, host-virus ambiguous reads are substantial, and sparse viral counts motivate binary rather than quantitative cell-level interpretation (`LSCHWCP_2023/README.md:13-15`; `paper.md:300-306`).

The regression coefficients are correlational. High prediction accuracy can reflect cell state, cell type, donor, or time structure even with controls, and pathway enrichment does not establish causality.

### Reproducibility: 3/5 (partial)

The repository snapshot is strong at the manuscript-analysis layer: it is organized by figure, maps final Nature Biotechnology figure numbers to the original notebooks, points to external intermediary data, and includes a directly auditable downstream prediction script. `Notebooks/Figure_8/Figure_8bc/logisticRegression.py` implements barcode-aligned input handling, gene/covariate choices, balanced training, logistic fitting, held-out metrics, coefficients, probabilities, and serialized outputs.

However, **the modified upstream kallisto translated-search engine source is absent from this snapshot**. No C/C++ source tree, patch, or build configuration for the central engine modification is present. Thus, figure notebooks and downstream prediction code provide partial reproduction, but the core translated-search implementation cannot be audited end to end from this workspace.

No local supplementary Markdown is available.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
