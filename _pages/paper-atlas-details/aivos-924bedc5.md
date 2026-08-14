---
layout: default
permalink: /paper-atlas/aivos-924bedc5/
title: "AIVOs"
nav: false
wide: true
description: "AIVO（Artificial Intelligence Virtual Organoid，也称 virtual/silicon organoid）不是“用 AI 分析一次类器官数据”，而是一个持续维护的类器官尺度数字孪生：它把多模态、纵向实验与临床观测编码为虚拟细胞状态，再加入细胞间、细胞-基质、物质传输和力学耦合，通过“预测 -> 实验测量 -> 状态更新 -> 下一轮干预”形成闭环（论文第 25-31、41-59、63-83 行）。"
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
      <span>Bioactive Materials · 2026</span>
    </div>
    <h1>AIVOs</h1>
    <p>Artificial Intelligence Virtual Organoids (AIVOs)</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.bioactmat.2025.12.030" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for AIVOs">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## AIVOs 方法详解：从虚拟细胞到类器官尺度数字孪生

### 先说结论

AIVO（Artificial Intelligence Virtual Organoid，也称 virtual/silicon organoid）不是“用 AI 分析一次类器官数据”，而是一个持续维护的类器官尺度数字孪生：它把多模态、纵向实验与临床观测编码为虚拟细胞状态，再加入细胞间、细胞-基质、物质传输和力学耦合，通过“预测 -> 实验测量 -> 状态更新 -> 下一轮干预”形成闭环（论文第 25-31、41-59、63-83 行）。

这篇论文的主要贡献是概念边界、系统架构和构建路线，而不是一个已经发布、可以直接运行的统一模型。因此，下文会严格区分论文主张、便于理解的工程化解释和仍未验证的设想。

### 为什么需要 AIVO

实体类器官能够重现细胞异质性、空间组织和部分器官功能，但存在几个系统性限制：Matrigel 等基质成分复杂且批次差异大；培养和操作依赖人工；细胞来源、培养基和操作细节会造成技术变异；显微和组学读出多为终点测量；长期、无创、高内涵监测仍不足；大规模药筛和临床流程还受到成本、产量和伦理约束（论文第 21-23 行）。

已有路线各解决了一部分问题：

* 传统 Virtual Cell（*Trends in Cell Biology*, 2003）用微分方程、随机模拟或代理模型表达特定细胞过程，但一般不是与具体患者/类器官长期同步的数字孪生。
* AIVC 构想（*Cell*, 2024）提出通用表示 UR 和虚拟仪器 VI，能够表达细胞状态并模拟扰动，但单细胞状态本身不足以描述三维几何、细胞-基质作用和组织尺度场。
* AI-enabled organoid 往往把实体类器官作为数据源，完成图像识别或药物反应预测后即结束；AIVO 则要求对象具有身份、版本和时间状态，并能够被新测量持续更新（论文第 25-29、35-59 行）。

因此，AIVO 的关键升级不是更大的神经网络，而是把“细胞状态表示 + 组织尺度耦合 + 实验闭环”组织成一个可追踪的系统。

### 输入、状态与输出

#### 输入

论文要求的输入跨越多个尺度（第 69-73、129-147 行）：

* 分子/细胞：基因变异、bulk 和单细胞转录组、表观组、蛋白组、代谢组；
* 空间/结构：空间转录组、质谱成像、荧光与无标记成像、活细胞成像、光镜/电镜；
* 环境：培养条件、ECM 组成、基质刚度、氧和营养、药物剂量与时序；
* 临床：患者身份与人口学信息、治疗史、反应、结局；
* 时间：实体类器官的形态、代谢、电生理和药物反应纵向监测。

这些数据不能只做简单拼接。至少要明确患者-类器官对应关系、采样时间、终点定义、平台、空间坐标、批次和混杂因素，否则临床变量可能退化成错误的弱标签（第 72-73 行）。

#### 内部状态

最小可执行单元是虚拟细胞 VC。VC 不是平均表达谱，而是受多组学、时空成像和扰动实验约束，能够接受输入、改变状态并给出预测的模型（第 245-249 行）。AIVC 为它提供两个接口：

1. **UR（Universal Representation）**：将分子、细胞和多细胞观测编码为数值状态；
2. **VI（Virtual Instrument）**：decoder VI 把 UR 还原为可解释读出，manipulator VI 模拟药物、基因或环境扰动后的状态变化（第 43-51 行）。

下面只是帮助理解的工程化记号，不是论文给出的公式：

```text
观测 x_t --编码器--> 状态 UR z_t
干预 u_t --manipulator VI(z_t, u_t)--> 新状态 z_(t+1)
状态 z_t --decoder VI--> 可观测预测 y_hat_t
```

如果不同 AIVC 使用互不兼容的潜空间，不能假定两个 UR 可以直接拼接。论文要求使用共享的基因/蛋白/影像锚点、具有本体类型的状态变量和能传播不确定性的适配器（第 65-67 行）。具体适配算法 **Not found**。

#### 输出

输出不是单一分类结果，而包括当前类器官状态、可观测表型、反事实扰动结果、药物/剂量排序、下一项最有信息量的实验、置信度和分布外警报。组织尺度输出还可包括生长、分化、迁移、屏障功能、营养/药物扩散、力学应力和治疗反应。

### 三层架构

#### 1. 数据层

数据层负责采集、身份/时间对齐、质量控制和多尺度表示。空间转录组和质谱成像尤其重要，因为 VO 是三维多细胞对象，组织功能来自空间结构和细胞-基质作用，单细胞表达不能恢复微环境梯度（第 129-141 行）。预处理包括 ComBat/SVA 批次校正、低表达和背景噪声过滤、图像配准/空间变换、Z-score 或 min-max 标准化；深度生成模型与域适配可用于非线性平台对齐（第 149-155 行）。论文没有给出统一的预处理参数。

#### 2. 模型层

模型层不是一种模型，而是一组互补模块（第 75-79、159-209 行）：

* 自监督/对比学习与大规模预训练：在标签稀缺时学习可迁移 UR；
* CNN/Transformer：处理图像、高维表达和长距离依赖；
* GNN：把细胞及其邻接/信号关系表示为图；
* VAE/GAN：在稀缺状态区域生成表达或图像样本、模拟未测试扰动；
* ABM：逐个虚拟细胞执行增殖、凋亡、迁移、接触和信号规则；
* 连续体/反应扩散模型：表示细胞密度、营养、氧和药物场；
* FEM：表示基质、组织应力应变和边界条件；
* 混合模型：用生物物理先验约束神经网络，或用机理模拟产生训练/正则化数据。

这些模块的分工可以概括为：学习模型负责“从数据中估计状态和响应”，机理模型负责“让空间、传输和力学满足可解释约束”。但边界条件或简化物理如果缺少数据约束和敏感性分析，可能让模型“稳定但错误”（第 79、119-121 行）。

#### 3. 交互层

交互层把数字模型和实体对象连起来：新成像、组学、功能或临床数据用于修正漂移、参数和状态；模型反向建议药物组合、剂量时序、细胞系、培养条件或下一项读出（第 81-83 行）。只有持续完成这一步，AIVO 才是数字孪生，而不是静态数据库。

### 从输入到输出的完整流程

```text
多模态 + 纵向观测
        |
        v
去噪 / 批次校正 / 空间配准 / 尺度标准化 / 临床与时间对齐
        |
        v
自监督与对比学习 + 预训练
        |
        v
分子、细胞、多细胞 UR
        |
        +--> decoder / manipulator VI
        +--> GNN / Transformer 交互模块
        +--> ABM + 连续体/PDE + FEM 物理模块
        +--> VAE / GAN 稀缺状态增强
        |
        v
虚拟细胞群 + 共享微环境场 + 类器官表型
        |
        v
虚拟药筛 / 机制扰动 / 不确定性 / 下一实验优先级
        |
        v
实体类器官或 organ-on-chip 验证并更新模型
```

流程中最难的并不是任选一个模型训练，而是接口和校准：多模态观测通常在时间、空间上不对齐；状态与参数可能不可辨识；不同 UR 不兼容；离散细胞与连续物理场需要交换变量；不确定性要跨模块传播。论文准确指出这些问题，但没有提供完整耦合方程、时间步进、参数估计或数值稳定性方案。

### 可以装入 VO 的虚拟细胞模块

论文把 VC 分成三组（第 245-331 行）：

* **虚拟干细胞**：iPSC 提供带个体遗传背景的多能起点和分化轨迹；ESC 提供胚胎时间/谱系标尺与扰动基准；ASC 表达自我更新、组织稳态、损伤和再生的慢时间过程。
* **虚拟功能细胞**：免疫细胞表达发育历史、记忆、浸润、细胞因子和检查点；代谢细胞耦合跨细胞/区室的代谢通量、清除和毒性；上皮细胞表达分裂-分化-脱落、WNT/细胞周期、黏附迁移、微生物响应和屏障完整性。
* **虚拟肿瘤细胞**：同时表示克隆遗传/物理异质性、氧和营养选择、信号网络、集体侵袭、抗原性/免疫检查点以及治疗反应，再与血管、免疫、氧场和组织几何耦合。

图 3-5 的确支持这种模块化分工，但它们是架构示意，不证明一个统一实现已经把所有模块集成并验证。

### 训练、评价与具体结果

论文没有规定统一损失函数或优化器。建议的评价体系包含任务指标（Pearson、MSE、accuracy、AUC）、预测不确定性与置信度、物理假设敏感性、留出扰动验证、FAIR 数据/模型共享、版本和审计轨迹、亚组公平性与监管可追溯性（第 217-243、367-375 行）。

ODFormer（bioRxiv, 2025）是最具体的案例，但不是完整 AIVO 架构的统一实现。论文报告其在 30,000 个泛癌 bulk 转录组和 100 万个胰腺癌单细胞谱上预训练，再使用来自 183 个 PDO、98 种药物、约 14,000 次药物反应实验训练；标准化药物反应预测的 Pearson 相关系数超过 0.9，并报告回顾性临床结局关联（第 91 行）。

### 论文主张、解释与假设生成

**论文主张：** AIVO 应由多模态数据、UR/VI 虚拟细胞、组织交互/物理模块以及测量-更新-干预闭环组成；可服务药筛、疾病建模、organ-on-chip、临床支持和实体类器官设计（第 25-31、63-83、333-391 行）。

**本文解释：** 可以把 AIVO 看成“带类型接口和不确定性的状态估计 + 多尺度模拟 + 主动实验设计系统”。这是对论文架构的工程化整理，不是已验证代码行为。

**可检验的研究假设：** 共享锚点和不确定性感知适配器是否能让异构 UR 在同一 VO 中稳定协作；混合模型是否比纯深度模型更能外推到新扰动；主动实验选择是否能用更少实体实验达到同等校准精度；物理敏感性分析能否识别由边界假设主导的伪预测。这些是由论文框架导出的实验问题，不是论文已经证明的结论。

### 可复现性边界

当前证据中 **Not found**：论文关联实现、`code source`、统一数据模式、完整方程与损失、求解器和步长、参数辨识、优化器和训练日程、ODFormer 数据划分与权重、不确定性校准实现、可运行示例。检索范围包括 XML/Markdown 可用性信息、精确 DOI/标题 GitHub 查询和 OpenAlex 仓库位置；没有找到论文关联代码。

对研究者而言，最合理的下一步不是直接实现“全功能数字器官”，而是先选择一个可验证闭环：一种实体类器官、一个纵向表型、一个 VC 状态接口、一个组织尺度场、一个明确扰动和一个独立验证集；随后再逐步增加细胞模块、空间尺度和临床接口。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Artificial Intelligence Virtual Organoids (AIVOs)

### Quick take

Bai and Su propose Artificial Intelligence Virtual Organoids (AIVOs), also called virtual or silicon organoids, as persistent organoid-scale digital twins. An AIVO integrates multimodal and longitudinal observations into virtual-cell state representations, couples those cells through learned and mechanistic tissue models, and closes a prediction-measurement-update loop with physical organoids, organ-on-chip platforms, or patient data. The paper is a review and architectural synthesis, not a report of one executable AIVO implementation.

### Problem and prior limitations

Physical organoids reproduce important human tissue features but remain sensitive to poorly defined matrices, manual protocol variation, incomplete spatial organization, endpoint-biased readouts, cost, and limited scale (paper lines 21-23, 37-41). Earlier mechanistic Virtual Cell work (*Trends in Cell Biology*, 2003) formalized selected cell processes with differential equations, stochastic simulation, or agent models, but typically did not maintain a patient- or organoid-specific longitudinal twin. The AIVC agenda (*Cell*, 2024) introduced universal representations (URs) and neural virtual instruments (VIs) for cell-level state and perturbation prediction, yet single-cell representations alone do not capture organoid geometry, microenvironmental fields, or tissue interactions. AI-enabled organoid studies likewise often use an organoid as a static data source rather than a persistent, versioned object synchronized with experiments (paper lines 25-29, 41-59; references at lines 449-450).

### Proposed framework

The AIVO blueprint has three layers (paper lines 63-83):

1. **Data layer:** genomic, transcriptomic, epigenomic, proteomic, metabolomic, spatial, imaging, clinical, culture, matrix, mechanical, and treatment data, aligned by identity, space, time, endpoint, and platform.
2. **Model layer:** self-supervised/contrastive representation learning and pretraining; decoder/manipulator VIs; GNNs and Transformers for interactions; VAE/GAN augmentation; and hybrid agent-based, continuum/reaction-diffusion, and finite-element modules for cellular rules, transport, and mechanics.
3. **Interaction layer:** new measurements update state and parameters, while virtual perturbations prioritize drugs, doses, culture conditions, and follow-up assays. Uncertainty and out-of-distribution detection are required to prevent the system from becoming only a static database.

Virtual cells are the smallest executable units. The review organizes them as stem cells (iPSC, ESC, ASC), functional cells (immune, metabolic, epithelial), and tumor cells. Their roles span lineage initialization, homeostasis and regeneration, immune memory and checkpoint response, metabolic/toxicity coupling, epithelial barrier dynamics, and clonal evolution under microenvironmental and treatment pressure (paper lines 245-331).

### Construction and evaluation

The proposed construction sequence is: collect multimodal/longitudinal evidence -> correct noise, batch, scale, spatial and clinical alignment -> learn transferable state representations -> augment sparse regions -> couple cell models to interaction and physical fields -> run virtual interventions -> validate and update against physical measurements (paper lines 123-243). Evaluation should combine task metrics such as Pearson correlation, MSE, accuracy, and AUC with uncertainty/confidence, sensitivity tests for mechanistic assumptions, independent perturbation validation, FAIR data/model sharing, versioning, audit trails, subgroup fairness, and regulatory traceability.

ODFormer (bioRxiv, 2025) is the paper's main concrete example, not the implementation of the whole AIVO blueprint. The review reports pretraining on 30,000 pan-cancer bulk transcriptomes and one million pancreatic-cancer single-cell profiles, followed by approximately 14,000 drug-response assays from 183 patient-derived organoids and 98 drugs. It reports Pearson correlation above 0.9 for standardized response prediction and retrospective outcome associations (paper line 91; reference line 471). Those claims cannot be independently reproduced from this workspace because no ODFormer code, raw data, split definitions, configurations, or weights accompany the paper.

### Applications and evidence boundary

The review positions AIVOs for high-throughput drug and dose screening, disease-subtype and resistance discovery, mechanistic hypothesis generation, organoid and organ-on-chip experiment design, toxicity prediction, clinical decision support, and bone-organoid material/mechanics optimization (paper lines 333-391). Figures 1-6 visually support the architecture, cell-module taxonomy, cross-scale tumor coupling, application loop, and governance requirements. They are conceptual schematics rather than quantitative validation of an integrated system.

The paper's strongest contribution is a coherent vocabulary and system architecture connecting virtual cells to organoid-scale digital twins. Its main unresolved issues are data completeness and alignment, incompatible latent representations, ill-posed parameter identification, computational scaling, simplified physical assumptions, causal validation, interpretability, privacy, fairness, and regulation (paper lines 101-121, 393-423).

### Reproducibility assessment: 1/5

**Mode:** paper-only. No supplementary markdown or paper-linked implementation was found after XML/Markdown availability inspection, exact DOI/title GitHub searches, and OpenAlex repository checking. There is no `code source`, runnable example, complete objective, coupling equation set, solver specification, optimizer schedule, benchmark split, uncertainty-calibration procedure, or model checkpoint. The conceptual pipeline can be reasoned about, but the integrated AIVO framework cannot be executed or reproduced from the supplied artifacts.

### Bottom line

AIVOs define a useful research program: encode virtual-cell state, enforce tissue interactions and physics, and repeatedly recalibrate an organoid-scale twin with experiments. The architecture is technically plausible and supported by examples from adjacent virtual-cell, organoid, and digital-twin literature, but most benefits remain framework-level hypotheses. A reproducible realization will require a shared interface for heterogeneous URs, longitudinal benchmark datasets, explicit hybrid coupling equations, uncertainty-aware validation, and an open versioned reference implementation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
