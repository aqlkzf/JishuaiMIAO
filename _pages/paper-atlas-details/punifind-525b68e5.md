---
layout: default
permalink: /paper-atlas/punifind-525b68e5/
title: "pUniFind"
nav: false
wide: true
description: "pUniFind 想用同一套“质谱编码器 + 肽段编码/解码器 + 跨模态打分器”，同时完成两个任务：给数据库搜索产生的候选肽段重新打分，以及在没有候选肽段时直接从 MS/MS 谱图做开放式 de novo 测序。论文摘要把它称为一个在超过一亿张开放搜索谱图上预训练的多模态基础模型。"
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
      <span>Protein &amp; Sequence Models</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>pUniFind</h1>
    <p>A large-scale unified deep learning model for peptide mass spectrum interpretation trained on multimodal data</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/pFindStudio/pUniFind" target="_blank" rel="noopener noreferrer" aria-label="Open code for pUniFind">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## pUniFind 方法详解

### 一句话理解

pUniFind 想用同一套“质谱编码器 + 肽段编码/解码器 + 跨模态打分器”，同时完成两个任务：给数据库搜索产生的候选肽段重新打分，以及在没有候选肽段时直接从 MS/MS 谱图做开放式 de novo 测序。论文摘要把它称为一个在超过一亿张开放搜索谱图上预训练的多模态基础模型（`paper.md:9-12`）。

### 先说明证据边界

正文 Methods、论文公式和补充材料文本均未获得。因此本文严格区分：

- **论文主张**：只来自可读摘要或可用性声明；
- **图像观察**：来自直接打开的六张本地图；
- **代码已验证行为**：来自论文链接仓库快照的具体源代码行；
- **解释**：将上述证据连接起来的教学性理解，不等同于论文原文；
- **MISSING / Not found**：在明确搜索范围内没有获得或没有找到的内容。

下面出现的数学表达式只是对代码运算的整理，**不是论文公式**。

### 1. 它要解决什么问题？

串联质谱给出的是一组峰，每个峰至少包含质荷比 m/z 和强度。研究者通常希望回答：

1. 数据库搜索给出的多个候选肽段中，哪个与当前谱图最匹配？
2. 如果数据库里没有正确肽段，能否直接从谱图恢复氨基酸序列和修饰？

传统数据库搜索依赖候选空间；开放修饰会迅速放大搜索空间。另一方面，许多深度学习模型只预测谱图、保留时间或生成辅助特征，再交给别的搜索/重打分模块。论文摘要明确指出，pUniFind 的目标不是继续做单独的特征提取器，而是建立开放的端到端肽段-谱图打分，并把同一表示用于 zero-shot 开放 de novo 测序（`paper.md:12`）。

论文参考文献和图中包含 pDeep（*Analytical Chemistry*, 2017）、Prosit（*Nature Methods*, 2019）、AlphaPeptDeep（*Nature Communications*, 2022）、MSBooster（*Nature Communications*, 2023）、open-pFind（*Nature Biotechnology*, 2018）、MSFragger（*Nature Methods*, 2017）以及 pNovo 3（*Bioinformatics*, 2019）等相关工具（`paper.md:113-134`）。但预览没有保留论文对每个方法局限的逐项论述，因此本文不把某个具体缺点强行归因给单一基线。

### 2. 核心思路

Figure 1 的图像直接显示两条分支：

```text
MS/MS 谱图 ----------------> 谱图编码器 ----> 谱图表示 H_s
                                               |
候选肽段/修饰 -------------> 肽段编码器 ----> 肽段表示 H_p
                                               |
                                               v
                              自注意力 + 跨注意力 + FFN
                                               |
                                               v
                                      肽段-谱图联合分数
```

代码中也确实存在这三个部件：`SpectrumEncoder`、`PeptideEncoder` 和 `PepMsJointEncoder`（`pUniFind_repo/PepMS/models/ms_pep.py:494-599`）。联合编码器先在肽段 token 内做 self-attention，再以肽段为 query、谱图为 key/value 做 cross-attention，最后把第一个肽段 token 投影为一个标量分数（`pUniFind_repo/PepMS/models/decoders.py:2169-2270`）。

这说明发布代码实现了一个真正的跨模态推理路径；但由于论文 Methods 缺失，代码结构与论文最终评估模型的对应关系只能标为 `Inferred`，不能标为 `Exact` 或 `Partial`。

### 3. 输入、表示和输出

为了便于理解，这里引入非论文记号：

- $X=\{(m_i,I_i)\}_{i=1}^{n}$：一张谱图的 m/z-强度峰列表；
- $c=(m_{prec},q)$：前体 m/z 与电荷；
- $P$：候选肽段序列及修饰；
- $H_s=E_s(X,c)$：谱图编码器输出；
- $H_p=E_p(P,c)$：肽段编码器输出；
- $s=J(H_p,H_s)$：联合编码器输出的兼容性分数。

代码中的两种任务接口为：

| 任务 | 主要输入 | 主要输出 | 代码位置 |
|---|---|---|---|
| 数据库候选重打分 | m/z、强度、候选序列/修饰、前体、仪器、NCE、候选分组 | 每个候选的 joint score | `PepMS/tasks/ms_pep_score.py:60-163`; `PepMS/models/ms_pep.py:631-693` |
| de novo 测序 | m/z、强度、前体、仪器、NCE、RT、长度范围 | 序列、修饰、分数、余弦相似度、质量偏差、缺失碎片位置 | `PepMS/tasks/ms_pep_denovo.py:60-115`; `PepMS/models/ms_pep.py:695-1039` |

### 4. 工作流 A：数据库搜索重打分

```text
pFind 搜索结果 + MGF + 候选肽段
                 |
                 v
       预处理并按谱图组织多个候选
                 |
                 v
谱图编码 E_s(X,c) + 肽段编码 E_p(P,c)
                 |
                 v
      跨模态联合打分 J(H_p,H_s)
                 |
                 v
        每个候选的分数 -> 重排/结果文件
```

#### 逐步解释

1. **组织候选。** score task 把谱图、候选序列、修饰、前体信息、仪器、NCE 和 `batch_index` 放入 `net_input`。`batch_index` 表明多个候选属于同一张谱图（`PepMS/tasks/ms_pep_score.py:60-163`）。
2. **编码谱图。** `forward_score` 将 m/z 和强度拼成形状为 `(batch, peaks, 2)` 的输入，再加入前体、电荷、仪器和碰撞能量上下文（`PepMS/models/ms_pep.py:631-674`）。
3. **编码肽段。** 候选序列和修饰被单独编码；这让模型能够比较同一谱图下多个不同候选（`:675-683`）。
4. **联合打分。** joint encoder 按候选数量复制相应谱图表示，对肽段 token 做 self-attention 和对谱图的 cross-attention，输出每个候选的标量分数（`PepMS/models/decoders.py:2257-2270`）。
5. **工作流输出。** 官方脚本加载外部 checkpoint，以 `strict=False` 载入权重，关闭梯度后调用 `forward_score`，再把候选分数与谱图标题写入 pickle；用户手册描述了最终的 `.spectra` 结果（`official_score_workflow.py:203-217`, `:264-338`; `User_guide.md:87-93`）。

**解释：** 这一路径的关键不是“先预测一个谱图特征，再交给任意分类器”，而是直接学习肽段和谱图的联合兼容性。这个结论有代码支持；训练这个分数所用的论文损失函数则 `Not found`。

### 5. 工作流 B：开放 de novo 测序

```text
MS/MS 谱图 + 前体信息
          |
          v
谱图编码器 -> 预测中心长度 L_hat
          |
          v
在 L_hat 附近生成 r 个长度候选
          |
          v
非自回归解码序列和修饰
          |
          v
20 ppm 前体质量约束
          |
          v
重新编码候选 + 联合打分 -> 选最佳长度候选
          |
          v
余弦相似度/缺失碎片/质量偏差 -> CSV、过滤结果和 FASTA
```

#### 5.1 先预测长度，而不是直接无限生成

`forward_faster_denovo` 先从谱图表示的特定 token 预测中心长度 $\hat L$，再围绕它构造奇数个候选长度：

$$
\mathcal{L}=\left\{\hat L-\lfloor r/2\rfloor,\ldots,\hat L+\lfloor r/2\rfloor\right\}.
$$

代码随后删除不在 `min_length` 和 `max_length` 内的候选（`PepMS/models/ms_pep.py:732-774`）。用户手册给出的常用肽长范围是 6-40，`range_pred` 默认思路是同时尝试相邻多个长度（`User_guide.md:154-188`）。

#### 5.2 非自回归预测序列与修饰

每个候选长度先生成一个占位序列，随后进入 `NonARPeptideDecoder`。解码器利用谱图 memory 和前体信息，并通过多轮并行预测更新氨基酸和修饰类别，而不是严格按 N 端到 C 端逐 token 生成（`PepMS/models/decoders.py:1706-1793`, `:1957-2055`; `PepMS/models/ms_pep.py:776-807`）。

#### 5.3 用物理质量约束砍掉不合理候选

代码根据残基质量、修饰质量和水分子质量重建候选肽质量，只保留满足下式的候选：

$$
|m_{prec}-m_{seq}|\le 20\times10^{-6}m_{seq}.
$$

这是 `PepMS/models/ms_pep.py:1061-1082` 的直接代码行为，也与用户手册中的 20 ppm 限制一致（`User_guide.md:154-155`）。

#### 5.4 再用联合分数选择长度

通过质量约束的序列会重新进入肽段编码器；联合编码器计算每个候选与原谱图的分数，并在相邻长度中选最高分者（`PepMS/models/ms_pep.py:837-897`）。因此长度头不是最终决策：它负责缩小候选集合，联合分数负责最后选择。

#### 5.5 输出可检查的质量特征

代码还计算：

- 预测谱图与实验谱图的 cosine similarity；
- 前体质量偏差；
- 缺失碎片离子位置；
- 修饰名称与位置；
- 最终 joint score。

这些字段在 `PepMS/models/ms_pep.py:943-1039` 生成，并由官方工作流写入 CSV（`official_denovo_workflow.py:391-425`）。这与 Figure 4 下半部分显示的碎片离子可视化相呼应。

### 6. 两种 de novo 应用方式

论文摘要称有两套面向不同应用的 de novo workflow，Figure 4 也直接显示了分支结构。仓库用户手册提供的可验证操作解释是：

- **regular de novo**：直接使用 pUniFind 输出，并用 pLabel 查看谱图匹配；
- **modification-rich de novo**：把 pUniFind 生成的肽段整理为 FASTA，再让 pFind 在关闭 open mode 的条件下搜索关注的修饰，最后用 pBuild 检查（`User_guide.md:206-227`）。

这是仓库文档支持的操作级解释。论文中两套流程的完整阈值、数据库构造和评估协议仍然 `MISSING`。

### 7. 结果过滤到底做了什么？

发布代码中的 `filter_unreliable` 不是不可见的黑盒。它先保留 score 大于 `-30` 的记录，对同组谱图选择 cosine similarity 最大者，再要求：

- score 高于均值减两倍标准差；
- cosine similarity 高于 `max(均值-标准差, 0.8)`；
- 缺失碎片分隔符数量不超过 1。

对应代码是 `official_denovo_workflow.py:192-253`。这是**代码已验证行为**。它是否就是论文所说、把 RNA-Seq 一致性从 65.4% 提高到 85.0% 的质量控制模块，当前只能标为 **Not verified**，因为论文 Methods 和 RNA-Seq 分析代码均不可用。

### 8. 训练阶段知道什么、不知道什么？

#### 论文主张

摘要称模型在超过一亿张开放搜索谱图上训练，通过跨模态预测对齐肽段和谱图，并配合其他预训练任务（`paper.md:12`）。Figure 1 的图像也显示谱图/肽段辅助任务和联合打分器。

#### 代码已验证

模型定义暴露了 spectrum prediction、de novo prediction、modification prediction、sequence-length prediction、joint encoding 等组件和开关（`PepMS/models/ms_pep.py:67-202`, `:526-599`）。

#### MISSING / Not found

在当前快照中没有找到与论文对应的预训练入口、完整训练循环、超过一亿张谱图的构建流程、总损失实现、优化器/学习率调度、checkpoint 生成步骤或论文公式。推理 shell 脚本里出现 loss-weight 变量，并不能证明这些目标在发布代码中被训练执行，因此本文不拼接一个“猜测的总损失”。

### 9. 论文报告了什么效果？

- 免疫肽组学中，鉴定肽段数提高 42.6%；
- 修饰丰富 de novo 在搜索空间扩大约 300 倍时，PSM 数仍比已有方法多 60%；
- 常规 de novo 额外恢复 38.5% 的肽段，其中 1,891 条可映射到基因组但不在参考蛋白组中；
- 使用质量控制后，与 RNA-Seq 证据的一致性从 65.4% 提高到 85.0%（`paper.md:12`）。

直接观察 Figures 2-6，可以确认论文进行了跨物种数据库搜索、验证/诱饵或 entrapment 检查、不同仪器数据、常规与修饰 de novo、多方法比较以及困难生物学场景分析。但本地图像是低分辨率预览，不能可靠抄录全部坐标、样本量和显著性统计。

### 10. 复现性与适用边界

**

有利条件：论文直接链接公开仓库；代码包含 CLI、两类推理 workflow、任务适配器、示例数据和依赖 checkpoint/GPU 的端到端测试（`paper.md:101-104`; `tests/test_e2e.py:1-15`）。

主要缺口：

- `MISSING`：论文 Methods、论文公式、补充材料文本；
- `Not found`：训练流程、完整评估脚本、RNA-Seq 分析、论文模型与具体 checkpoint 的身份对应；
- 本地 `ckpts/` 不含权重，用户手册要求从外部下载（`User_guide.md:65-68`）；
- 本分析按要求没有执行模型、权重、demo 或测试；
- 用户手册说明当前不支持 ITMS 或 ETD/EThcD，并提醒开放修饰中的质量重合问题（`User_guide.md:228-237`）。

### 11. 应该怎样理解 pUniFind 的真正亮点？

从已验证代码看，最有价值的设计不是单一 Transformer，而是任务之间复用同一组表示和分数：

1. 数据库搜索把联合分数用于候选排序；
2. de novo 先用谱图表示提出长度和序列，再复用联合分数选择候选；
3. 输出谱图相似度、质量偏差和缺失碎片，给结果过滤与人工检查提供依据。

这是实现驱动的解释，不是已证明的性能因果结论。一个可检验的工程假设是：联合打分器对 de novo 长度候选选择有独立贡献；

### 搜索范围

论文：`paper source/nature_html/paper.md:1-327`。图像：六张本地 `figure_01.png` 至 `figure_06.png`。代码：`PepMS/models/ms_pep.py:67-1110`、`PepMS/models/decoders.py` 中谱图编码器/非自回归解码器/联合编码器、两类 task、官方 Python/shell workflow、CLI、用户手册、模型注册和端到端测试。没有补充 Markdown，也没有执行模型或权重。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## pUniFind Summary

### Problem and Motivation

The paper presents pUniFind as a unified deep-learning framework for interpreting peptide tandem-mass spectra. Its stated target is broader than feature extraction: one model should score open-search peptide-spectrum matches and perform open, zero-shot de novo sequencing, including modified peptides (`paper.md:9-12`). The paper's framing contrasts this with earlier prediction/feature systems and conventional search workflows; the reference list places related tools such as pDeep (*Analytical Chemistry*, 2017), Prosit (*Nature Methods*, 2019), MSBooster (*Nature Communications*, 2023), open-pFind, and MSFragger (*Nature Methods*, 2017) in that context (`paper.md:113-129`).

### Proposed Method

The accessible abstract claims training on more than 100 million open-search-derived spectra and aligning peptide and spectrum modalities through cross-modality prediction plus auxiliary pretraining tasks. Figure 1 visibly shows separate peptide and spectrum branches feeding a joint scorer with self-attention, cross-attention, and feed-forward blocks, alongside spectrum/peptide prediction tasks (`figure_analysis.md`; `paper.md:12`).

The released code verifies a shared inference backbone. `MDProteinModel` encodes m/z-intensity spectra and peptide/modification candidates separately, then applies a joint encoder to return compatibility scores (`pUniFind_repo/PepMS/models/ms_pep.py:494-520`, `:631-693`; `PepMS/models/decoders.py:2169-2270`). Its de novo path predicts a central sequence length, explores neighboring lengths, decodes sequence/modification tokens with a non-autoregressive decoder, rejects candidates outside a 20 ppm precursor-mass condition, and joint-rescores the survivors (`pUniFind_repo/PepMS/models/ms_pep.py:695-897`, `:1061-1082`).

### Computational Workflows

- **Rescoring:** pFind-derived candidates and spectra are converted into task batches; spectrum and candidate peptide representations are jointly scored; the official workflow associates scores with titles and writes serialized results (`pUniFind_repo/PepMS/tasks/ms_pep_score.py:60-163`; `pUniFind_repo/official_score_workflow.py:264-338`).
- **Regular de novo:** spectra are decoded directly and results can be visualized with pLabel.
- **Modification-rich de novo:** the guide describes using predicted peptides/FASTA for a downstream closed-mode pFind search and pBuild visualization (`User_guide.md:94-115`, `:206-227`).
- **Quality features:** the de novo implementation emits score, cosine similarity, mass shift, and missing-fragment fields and applies a source-verified heuristic filter before writing merged CSV and FASTA (`official_denovo_workflow.py:425-488`).

The exact paper training objective, data construction, and end-to-end two-workflow protocol are **MISSING** because the acquired Nature HTML contains no body Methods or supplementary Markdown.

### Evaluation

The abstract reports a 42.6% increase in identified peptides for immunopeptidomics; 60% more peptide-spectrum matches for modification-rich de novo despite a 300-fold larger search space; 38.5% additional peptides for regular de novo, including 1,891 genome-mapped peptides absent from reference proteomes; and RNA-Seq consistency increasing from 65.4% to 85.0% after quality control (`paper.md:12`). Figures 2-6 visibly cover cross-species/database-search comparisons, validation and instrument checks, two de novo workflows, multi-method de novo benchmarks, modification distributions, and challenging applications. Exact benchmark splits, baselines, and uncertainty calculations are not recoverable from the preview.

### Reproducibility

**Rating: 2/5 for this workspace.** The paper links a public GitHub snapshot, and the repository includes CLI commands, workflow scripts, task adapters, demo inputs, and GPU/checkpoint-dependent end-to-end tests (`paper.md:101-104`; `User_guide.md:45-115`; `tests/test_e2e.py:1-15`). However, checkpoints are external and absent from the snapshot; model execution was intentionally not run. The paper Methods, equations, training loop, corpus construction, evaluated checkpoint identity, full evaluation scripts, and RNA-Seq quality-control analysis remain `MISSING`/`Not found`. Code-paper fidelity is therefore low in assessability: scoring and de novo inference behavior is directly verified, while correspondence to the paper's trained system is `Inferred`, not `Exact` or `Partial`.

### Evidence and Scope

Primary paper: `paper source/nature_html/paper.md:1-327`; figures: all six local PNGs; direct code: model, encoder/decoder/joint modules, task adapters, official workflows, CLI, guide, registry, and tests. No model/weight execution, OCR rerun, acquisition, or separate review was performed.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
