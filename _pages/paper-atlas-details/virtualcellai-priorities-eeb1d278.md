---
layout: default
permalink: /paper-atlas/virtualcellai-priorities-eeb1d278/
title: "VirtualCellAI_Priorities"
nav: false
description: "这篇 Cell Perspective 不是一个已经发布的软件方法或可运行模型，而是一篇关于 AI virtual cell，AIVC 的路线图论文。作者把 AIVC 定义为一种多尺度、多模态、基于大型神经网络的细胞模型，用来表示和模拟分子、细胞和组织在不同状态下的行为。因此，下文讲的是论文提出的概念架构和优先事项，不是代码实现说明。"
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
      <span>Cell · 2024</span>
    </div>
    <h1>VirtualCellAI_Priorities</h1>
    <p>How to build the virtual cell with artificial intelligence: Priorities and opportunities</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2024.11.015" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## AI 虚拟细胞论文方法解释

### 一句话定位

这篇 Cell Perspective 不是一个已经发布的软件方法或可运行模型，而是一篇关于 **AI virtual cell，AIVC** 的路线图论文。作者把 AIVC 定义为一种多尺度、多模态、基于大型神经网络的细胞模型，用来表示和模拟分子、细胞和组织在不同状态下的行为（`paper.md:31`）。因此，下文讲的是论文提出的概念架构和优先事项，不是代码实现说明。

### 论文想解决什么问题？

传统虚拟细胞模型通常依赖显式规则、微分方程、随机模拟或 agent-based 模型等人工设定的数学/计算框架（`paper.md:27`）。这些方法可以解释或模拟细胞生物学中的某些局部过程，例如转录翻译、细胞骨架行为、生化网络或代谢通量，但很难覆盖更复杂的细菌系统和人类细胞系统（`paper.md:27-29`）。

论文指出主要困难有三类：

1. **多尺度**：细胞过程跨越原子、分子、细胞、组织等空间尺度，也跨越从极短反应到多年疾病进展的时间尺度（`paper.md:29`, `paper.md:131`）。
2. **成分和相互作用数量巨大**：基因调控、代谢、信号转导等过程包含大量相互作用的分子和状态（`paper.md:29`）。
3. **强非线性动态**：小扰动可能导致复杂输出，局部模型难以外推到整体细胞行为（`paper.md:29`）。

作者认为，AI 和组学数据的进展使得从数据中直接学习细胞模型成为可能（`paper.md:31-35`）。

### AIVC 的核心目标

论文提出 AIVC 应该具备三类能力（`paper.md:45`）：

- 建立跨物种、跨模态、跨数据集、跨上下文的 **universal representation，UR**。
- 预测细胞功能、行为和动态，并帮助提出机制假设。
- 进行 **in silico** 实验，用计算方式生成和测试假设，并指导后续数据采集。

这里的重点是“应该具备”。论文没有展示一个已经训练完成的 AIVC，也没有给出性能表格或代码仓库。

### 总体架构

论文把 AIVC 看成一个由多个互联 foundation model 组成的 AI 框架，覆盖从分子到细胞、组织乃至更高层级的动态生物系统（`paper.md:71`）。核心结构有两部分：

1. **多模态、多尺度的生物状态 UR**：把高维生物数据压缩成连续向量空间中的嵌入，同时保留有意义的生物关系和模式（`paper.md:73`）。
2. **virtual instruments，VI**：在 UR 上操作的神经网络，用于解码或操控这些表示（`paper.md:77`）。

可以把论文提出的流程理解为：

```text
多模态生物数据
    |
    v
分子 UR -> 细胞 UR -> 多细胞/组织 UR
    |
    +-----------------------------+
    |                             |
    v                             v
decoder VI                   manipulator VI
    |                             |
    v                             v
可理解输出                    改变后的/未来的 UR
细胞类型、图像、表型、药物反应  扰动响应、状态转移、动态模拟
    |
    v
实验验证、主动学习、开放基准、机制解释
```

这是一种概念性计算图，不是论文提供的实际代码结构。

### 三个尺度的 UR

#### 1. 分子尺度

分子层首先表示 DNA、RNA、蛋白质等中心法则相关分子，也可以扩展到代谢物、小分子和其他细胞成分（`paper.md:87`）。DNA/RNA/蛋白质可以被看成字符序列，因此适合借鉴自然语言处理中的 LLM 或 sequence model；但原子级模型可能更通用，不过计算负担更重，训练数据也更有限（`paper.md:87`）。

论文没有指定一个必须采用的模型，只是说明 sequence model、atomic model 等都是可能方向。

#### 2. 细胞尺度

细胞 UR 要把分子表示、分子数量、空间位置、时间戳和成像/组学特征整合成统一的细胞状态表示（`paper.md:91`）。可用数据包括 scRNA-seq、scATAC-seq、染色质修饰、转录因子结合、蛋白组、亚细胞成像、活细胞成像、冷冻电镜、超分辨显微镜、质谱和 proximity labeling 等（`paper.md:91-99`）。

从模型角度，论文提到 vision transformer、CNN、autoencoder 和 transformer 都可以用于不同模态的数据表示学习（`paper.md:95`）。但这些只是候选架构方向，不是本文验证过的统一实现。

#### 3. 多细胞/组织尺度

多细胞 UR 关注细胞与细胞、细胞与非细胞环境之间的空间组织和相互作用（`paper.md:103`）。数据可以来自组织切片、3D 组织体积、空间转录组、空间蛋白组、H&E 图像等。相对空间结构可以表示为 graph 或 point cloud，因此 GNN、equivariant neural network、CNN 或 vision transformer 都可能用于建模（`paper.md:103-107`）。

Figure 2 直观展示了这种从分子 UR 到细胞 UR 再到多细胞 UR 的逐级结构（`images/gr2_lrg.jpg`; `paper.md:355-356`）。

### VI：让 UR 变成可用工具

论文把 VI 定义为在 UR 上操作的神经网络（`paper.md:77`, `paper.md:111`）。主要有两类：

| VI 类型 | 输入 | 输出 | 作用 |
|---|---|---|---|
| decoder VI | UR | 人能理解的输出 | 细胞类型、合成显微图像、表型、fitness、表达量、药物反应等 |
| manipulator VI | UR | 另一个 UR | 扰动后的细胞状态、未来状态、分化/迁移/分裂轨迹、治疗反应等 |

Manipulator 的思想是把复杂动态抽象成 UR 空间中的转移（`paper.md:111`）。论文提到 diffusion model、autoregressive transformer、conditional generative model 等可以作为未来建模方向（`paper.md:113`, `paper.md:123`）。另外，VI 最好能给出不确定性，用 Bayesian inference、ensemble、conformal prediction、active learning 或 expected value of information 等方式指导后续实验（`paper.md:125`）。

### In silico 实验和 lab-in-the-loop

AIVC 的一个关键用途是把实验变成可查询的虚拟实验。论文举例说，AIVC 可以模拟难培养细胞类型中的实验，或者用低成本读数预测高成本读数，例如从 label-free imaging 推断单细胞转录组（`paper.md:65`）。它也可能在实验室无法枚举的大规模组合扰动空间中做虚拟筛选（`paper.md:65`, `paper.md:139`）。

一个可理解的闭环是：

1. 在 UR 空间中提出扰动或实验问题。
2. manipulator VI 预测扰动后的 UR 或未来状态。
3. decoder VI 把 UR 转成可解释读数。
4. 模型给出置信度或不确定性。
5. 低置信度但高价值的问题被送回湿实验。
6. 新数据再用于改进 AIVC。

论文明确把这种自我识别知识缺口、推荐高价值实验的能力写成愿景，而不是已经完成的结果（`paper.md:67`, `paper.md:125`）。

### 数据需求

AIVC 的构建不只是模型问题，也是数据问题。论文强调，训练数据应覆盖不同领域和模态，捕捉生物异质性，区分技术噪声、生物随机性和生理差异（`paper.md:127-129`）。

关键数据需求包括：

- 覆盖时间和空间尺度，包括快速分子反应、细胞分裂、肿瘤多年发展、神经退行性疾病长期进展等（`paper.md:131`）。
- 桥接分子、空间和组织尺度，例如把单细胞转录组与组织形态结合（`paper.md:133`）。
- 引入扰动数据，因为只有观察数据不足以学习因果和动态（`paper.md:57`, `paper.md:123`）。
- 包含 org organoid、模型生物和跨物种数据，以弥补人体体内扰动实验受限的问题（`paper.md:135-137`）。
- 关注数据多样性和质量，避免物种、性别、疾病和人群祖源偏倚降低模型影响（`paper.md:145`）。

### 如何评价 AIVC？

论文说，关键问题不仅是“怎么构建 AIVC”，更是“怎么建立对其能力和真实性的信任”（`paper.md:151`）。它提出未来需要综合、可适应的 benchmark，而不是只针对单个生物任务。

评价重点包括：

- **泛化能力**：能否处理未见过的细胞类型、遗传背景和生物上下文（`paper.md:155`）。
- **跨模态重建**：例如用形态预测基因表达，或预测显微图像序列的下一帧（`paper.md:155`）。
- **OOD 外推**：新分子、新细胞状态、新物种或设计出来的非自然生物实体（`paper.md:153`）。
- **发现新生物学的价值**：能否生成可实验验证的假设，例如细胞生长率、分子谱、蛋白互作破坏或转录因子结合等（`paper.md:157`）。
- **可解释性和因果性**：统计指标可能不够，随着模型能力增强，解释和因果会更重要（`paper.md:159`）。

本 workspace 中没有已完成的 AIVC benchmark 结果。

### 可解释性、交互和治理

论文承认，AIVC 可能不能像传统机制模型那样完全解释细胞行为，但仍然需要提升可解释性（`paper.md:163`）。作者希望每个预测都能关联到决定结果的多尺度相互作用，并利用模块化结构定位相关基因、蛋白或分子过程（`paper.md:165`）。

交互层面，论文设想 LLM-based AI agents 可以作为虚拟研究助手，帮助不同背景的研究者理解和使用 AIVC 预测（`paper.md:167`）。Figure 1C 也把 interaction、evaluation、interpretability、privacy、collaboration、responsibility 放在 AIVC 发展的核心层（`images/gr1_lrg.jpg`; `paper.md:353`）。

治理层面，论文强调开放数据、数据标准、协作平台、开放 benchmark、共同验证策略、多样性、隐私保护、计算资源可及性、监管协作和生物伦理（`paper.md:171-173`）。这些是开放科学路线图的一部分，不是本文给出的工程协议。

### 证据边界和缺口

- **代码实现**：Not found。`github_links.json` 没有仓库 URL，`code source=none`。
- **补充材料**：MISSING。没有 `SUPP_MD`。
- **公式/目标函数**：Not found。公式抽取结果为 0。
- **Box 内容**：Not found。正文引用 Box 1/2/3，但转换后的 `paper.md` 没有对应 box 内容（`paper.md:39`, `paper.md:83`）。
- **图像证据**：主图 Figure 1 和 Figure 2 已本地查看；它们支持概念能力图和架构图，但不支持性能结论。

### 最重要的理解

这篇文章的“方法”不是一个传统算法，而是一套 AIVC 建设蓝图：先学习跨分子、细胞、多细胞尺度的 universal representations，再用 decoder/manipulator virtual instruments 在这些表示上进行预测、扰动模拟、假设生成和实验设计。真正落地还需要数据体系、开放 benchmark、可解释性、隐私治理、协作平台和后续实验验证。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Fast Overview

This Cell Perspective defines an AI virtual cell (AIVC) as a multi-scale, multi-modal, large-neural-network-based model for representing and simulating molecules, cells, and tissues across diverse states (`paper.md:31`). It is a roadmap and priorities paper, not a report of a trained AIVC system or a code release. The stated goal is to motivate a collaborative research agenda for developing, implementing, and deploying AIVCs across data generation, AI models, benchmarking, interpretation, safety, and open science (`paper.md:39`, `paper.md:175`).

### Problem

Traditional virtual-cell models have relied on explicit rule-based, mathematical, or computational descriptions such as differential equations, stochastic simulations, and agent-based models (`paper.md:27`). These approaches have supported important whole-cell and process-specific models, but the paper argues that they fall short for more complex bacterial and human systems because cells span multiple time/space scales, contain many interacting molecular components, and exhibit nonlinear dynamics (`paper.md:29`).

### Proposed Architecture

The proposed AIVC scaffold has two central pieces (`paper.md:71-77`):

1. **Universal representations (URs)**: learned embeddings that map high-dimensional, multi-modal biological measurements into representation spaces while preserving meaningful biological relationships (`paper.md:73`).
2. **Virtual instruments (VIs)**: neural networks operating on URs. Decoder VIs map URs to human-understandable outputs such as labels, images, phenotypes, or drug responses; manipulator VIs map one UR to another, such as a predicted altered state after perturbation (`paper.md:77`, `paper.md:111`).

The AIVC is organized across molecular, cellular, and multicellular scales. Molecular URs start from DNA/RNA/protein and other molecular entities; cellular URs integrate molecular abundance, organization, location, timestamps, imaging, and omics; multicellular URs model cell-cell and cell-environment organization through spatial data, graphs, point clouds, or tissue images (`paper.md:87-107`).

### Capabilities and Use Cases

The paper proposes three primary AIVC capabilities: represent biological states across species/modalities/contexts, predict function/behavior/dynamics/mechanisms, and perform in silico experiments that guide hypothesis generation and data collection (`paper.md:45`). Figure 1 visualizes these as reference atlases, continuous dynamics, intrinsic/extrinsic perturbations, spatial niches, novel state discovery, in silico experimentation, digital twins, and community layers for interaction/evaluation/interpretability/privacy/collaboration/responsibility (`images/gr1_lrg.jpg`; caption at `paper.md:352-353`). Figure 2 visualizes the architecture of scale-specific URs plus decoder/manipulator VIs (`images/gr2_lrg.jpg`; caption at `paper.md:355-356`).

These are intended capabilities, not demonstrated benchmark results.

### Data and Evaluation Priorities

The paper treats data generation as a core requirement. Training data should span domains and modalities, capture biological heterogeneity, distinguish technical noise from biological variation, cover temporal and physical scales, include perturbations, bridge molecular and spatial scales, and address diversity/quality biases (`paper.md:127-147`). It also stresses that combinatorial biological spaces are too large for exhaustive experiment, motivating new exploration and active-learning strategies (`paper.md:139`, `paper.md:125`).

For evaluation, the authors call for comprehensive and adaptable benchmarks that test competence, fidelity, generalizability, dynamic distribution shifts, cross-modal reconstruction, out-of-distribution extrapolation, and hypothesis-generation value (`paper.md:149-159`). No completed AIVC benchmark suite or performance result is provided in this workspace.

### Interpretability and Governance

The paper acknowledges that AIVCs may rely on learned interactions rather than fully mechanistic models, so interpretability remains a key adoption requirement (`paper.md:163-165`). It proposes modular multi-scale interactions, mechanistic hypothesis generation, and an interactive layer where AI agents or LLMs help researchers use AIVC predictions (`paper.md:165-167`).

Open science is also part of the proposed system design: the authors call for open data resources, standards, collaborative platforms, open benchmark datasets, validation strategies, diversity-aware data collection, privacy safeguards, compute/model-hosting infrastructure, regulatory coordination, and bioethics participation (`paper.md:171-173`).

### Reproducibility and Evidence Status

- **Mode:** paper-only.
- **Code:** **Not found**. `github_links.json` contains no repository URLs, and `code source=none`.
- **Supplement:** **MISSING**. No supplementary markdown was acquired.
- **Equations/objectives:** **Not found**. No formal formulas were extracted from `paper.md`.
- **Boxes:** **Not found**. Box 1/2/3 are referenced in text but their contents are absent from the converted Markdown (`paper.md:39`, `paper.md:83`).
- **Figures:** 10 local image assets exist. The two captioned main figures were inspected directly: `gr1_lrg.jpg` and `gr2_lrg.jpg`.
- **Runnable reproducibility:** not applicable as a method implementation; the paper is a conceptual roadmap without scripts, model weights, datasets, or executable examples in this workspace.

### Bottom Line

The technical contribution is a community roadmap for AIVC construction: learn universal representations across molecular, cellular, and multicellular scales, then attach reusable decoder and manipulator virtual instruments for prediction, perturbation simulation, hypothesis generation, and lab-in-the-loop data collection. The strongest evidence is conceptual and architectural; implementation, benchmarking, and governance protocols remain future work.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
