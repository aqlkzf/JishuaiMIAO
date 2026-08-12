---
layout: default
permalink: /paper-atlas/cellbehaviorhypothesisgrammar-a62cf96d/
title: "CellBehaviorHypothesisGrammar"
nav: false
description: "Cell Behavior Hypothesis Grammar 把细胞行为假设从隐藏在 C++ 里的条件逻辑，提升为可读的 CSV 规则；这些规则通过 Hill 响应函数和 PhysiCell phenotype 更新机制变成可执行的多细胞 agent-based model，从而让生物假设更容易编写、审查、复用和扩展。"
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
      <span>Cell · 2025</span>
    </div>
    <h1>CellBehaviorHypothesisGrammar</h1>
    <p>Human interpretable grammar encodes multicellular systems biology models to democratize virtual cell laboratories</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2025.06.048" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法中文解读：Cell Behavior Hypothesis Grammar

### 这篇文章解决什么问题

这篇 *Cell* 论文提出了一套“细胞行为假设语法”：研究者可以用接近自然语言的规则描述细胞如何响应环境信号，例如“在肿瘤细胞中，氧气增加细胞周期进入率”或“在某类 T 细胞中，IL-10 降低向 CD8 T 细胞转化的概率”。这些规则不会停留在文字层面，而是被转换成数学函数，并在 PhysiCell 的 agent-based model 中直接控制每个细胞 agent 的 phenotype 参数。

作者想降低多细胞系统建模的门槛。传统 PhysiCell/ABM 模型通常需要在 C++ 中手写条件逻辑，导致生物假设隐藏在源代码里，也不利于复现。这个语法把“细胞类型、信号、响应方向、行为、参数”拆成标准字段，让模型假设变成可读、可编辑、可解析的 CSV 规则。

### 核心思想

一个规则的基本结构是：

```text
cell type, signal, response, behavior, max response, half-max, Hill power, applies to dead?
```

含义分别是：

- `cell type`：规则作用于哪类细胞；
- `signal`：细胞感知到的信号，例如氧气、ECM、压力、细胞接触、时间等；
- `response`：信号是增加还是降低某个行为；
- `behavior`：被调节的细胞行为，例如 cycle entry、necrosis、migration speed、attack、phagocytosis、type transition；
- `max response`：信号很强时行为参数达到的目标值；
- `half-max`：响应达到半最大时的信号水平；
- `Hill power`：响应曲线的陡峭程度；
- `applies to dead?`：规则是否也作用于死亡细胞。

代码中，这个 CSV v3 格式由 `grammar_samples/core/PhysiCell_rules.cpp:1707-1818` 解析；XML 配置中的 `<cell_rules>` 和 `<ruleset>` 决定加载哪个规则文件，路径在 `grammar_samples/core/PhysiCell_rules.cpp:1824-1944`。

### 数学形式

单个信号调节单个行为时，论文使用：

`$b(s)=b_{0}+(b_{M}-b_{0})R(s)\text{,}$`

这里 `$b_{0}$` 是没有信号时的基础行为值，`$b_{M}$` 是强信号下的最大改变值，`$R(s)$` 是 0 到 1 之间的响应函数。默认响应函数是 Hill 函数。代码中的 `Hill_response_function` 按 `(s/half_max)^hill_power / (1+(s/half_max)^hill_power)` 计算，位置是 `grammar_samples/core/PhysiCell_basic_signaling.cpp:158-175`。

多个上调信号和下调信号同时存在时，论文定义两个合成响应：

- `$U=H_{M}(u;u_{\text{half}},p)$`：所有上调信号的合成响应；
- `$D=H_{M}(d;d_{\text{half}},q)$`：所有下调信号的合成响应。

最终行为值为：

`$b(u,d)=(1-D)\cdot[(1-U)\cdotb_{0}+U\cdotb_{M}\;]+D\cdotb_{m}$`

也就是说，上调信号先把行为从基础值推向最大值，下调信号再把结果推向最小值。代码中的 `multivariate_Hill_response_function` 位于 `grammar_samples/core/PhysiCell_basic_signaling.cpp:213-230`；`Hypothesis_Rule::evaluate` 在 `grammar_samples/core/PhysiCell_rules.cpp:348-354` 里计算 `HU`、上调后的目标值 `U`、下调响应 `DU` 和最终 `output`。需要注意：代码变量名 `U` 表示“上调后的行为目标值”，而论文里的 `$U$` 表示 0 到 1 的归一化上调响应；这是命名差异，不是公式差异。

### 运行时怎么作用到细胞

每个细胞在模拟过程中会读取自己的局部信号，例如当前氧气浓度、压力、是否与其他细胞接触、是否死亡、当前时间等。`Hypothesis_Rule::evaluate(Cell*)` 会调用 `get_single_signal` 逐项取信号，再根据该细胞是否死亡决定规则是否适用，最后返回新的行为参数值。`Hypothesis_Rule::apply(Cell*)` 用 `set_single_behavior` 把结果写回细胞 phenotype。对应代码在 `grammar_samples/core/PhysiCell_rules.cpp:362-390`。

这意味着规则不是离线注释，而是在每个细胞 agent 的动态模拟中实时影响行为。

### 论文中的几个例子

#### 低氧肿瘤模型

低氧模型用规则表达氧气对增殖、坏死和“motile tumor cell”状态转换的影响。对应代码在 `grammar_samples/user_projects/hypoxia/config/cell_rules.csv:1-8`。论文 Figure 2 的图像显示了 0 到 120 小时的肿瘤生长、中心坏死区、运动性肿瘤细胞分布，以及敏感性分析。

#### CAF/PDAC 侵袭模型

PDAC 例子把 CAF、ECM 和肿瘤细胞 EMT 联系起来。`epi_caf_invasion/config/cell_rules.csv` 中有 ECM 促进状态转换、ECM 对 migration speed 的双相影响等规则。`experimental_data_analysis/PancCAFAnalysis/FitRulesParams.m` 使用 `fmincon` 拟合 ECM 密度与迁移速度之间的响应曲线。

#### 肿瘤-免疫模型

Figure 4 包含简单版和扩展版模型。简单版用肿瘤细胞、巨噬细胞、CD8 T 细胞、促炎/抗炎因子和 damage/attack 规则表达免疫杀伤；扩展版加入 M0/M1/M2 巨噬细胞和 naive/effector/exhausted CD8 T 细胞状态。对应规则文件在 `tumor_immune_base` 和 `tumor_immune_extended`。

#### TAM-EGF 模型

Figure 5 比较 EGF 让肿瘤细胞“grow”、“go”或“go and grow”的假设。代码中 `tam_egf/config/cell_rules_grow.csv`、`cell_rules_go.csv`、`cell_rules_go_and_grow.csv` 分别编码这三种假设。这个例子很好地展示了语法的用途：同一个系统里只改规则文件，就能表达不同生物假设。

#### PDAC 治疗虚拟队列

Figure 6 用 scRNA-seq 推断的细胞比例初始化 PDAC 虚拟患者队列，并模拟 GVAX、Nivolumab/ICI、Urelumab/URU 组合治疗。代码中 `pdac_therapy/config/cell_rules.csv` 给出共享规则，`config/ic_cells` 下有不同组织和治疗条件的初始细胞 CSV。

#### 神经发育模型

Figure 7 把同一套语法用于非癌症系统：皮层层化。规则用时间控制 RGC 的不对称分裂、迁移、细胞层身份转换和凋亡。SOM 与 AUD 的规则分别在 `neuro_dev/config/cell_rules_SOM.csv` 和 `cell_rules_AUD.csv`，校准代码在 `neuro_dev/Calibration/CortexCalibration.py`。

### 代码复现程度

本工作区中的代码对“核心方法”的复现程度很高：

- 数学响应函数有直接 C++ 实现；
- CSV 规则解析与 XML 加载路径完整；
- 运行时规则会真实写入细胞 phenotype；
- 主要生物例子的项目目录、规则文件和配置文件都存在。

但对“论文每个图面板”的复现程度是中等。原因是本地没有 Methods S1 补充材料，也没有一个完整 manifest 说明每个图面板对应哪条命令、哪个随机种子、哪个输出快照、哪个外部实验数据文件。部分图还依赖外部原始数据或带有硬编码本地路径的绘图脚本。因此，更准确的说法是：这个仓库提供了核心语法实现和主要示例模型，而不是完整的一键论文制图流水线。

### 一句话总结

Cell Behavior Hypothesis Grammar 把细胞行为假设从隐藏在 C++ 里的条件逻辑，提升为可读的 CSV 规则；这些规则通过 Hill 响应函数和 PhysiCell phenotype 更新机制变成可执行的多细胞 agent-based model，从而让生物假设更容易编写、审查、复用和扩展。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Paper and Method

**Title:** Human interpretable grammar encodes multicellular systems biology models to democratize virtual cell laboratories.

This paper introduces a cell behavior hypothesis grammar for agent-based models: users write biological rules as controlled, human-readable statements connecting a cell type, a signal, a response direction, and a behavior. The authors implement the grammar in PhysiCell so these statements are parsed from CSV rows into mathematical response functions and applied to simulated cell phenotypes during runtime (`paper source/elsevier/paper.md:35-39`, `paper source/elsevier/paper.md:189-191`, `paper source/elsevier/paper.md:245-252`).

The central claim is not only that rules can be written plainly, but that they map one-for-one to computable equations. The paper gives a single-rule interpolation formula and a multivariate formulation for combined up- and down-regulating signals (`paper source/elsevier/paper.md:227-244`). The released repository is the paper-linked model snapshot: the paper identifies PhysiCell 1.14.1+ as containing the grammar implementation and points to `physicell-models/grammar_samples` for the result models (`paper source/elsevier/paper.md:157-159`, `paper source/elsevier/paper.md:195-203`).

### Verified Code Behavior

The local code snapshot at commit `125f2062df5125469f7ef3083796d48a47b86026` supports the core method. The implementation registers signal and behavior dictionaries in `grammar_samples/core/PhysiCell_signal_behavior.cpp:82-390`, parses CSV v3 rows in `grammar_samples/core/PhysiCell_rules.cpp:1707-1818`, loads XML-declared CBHG rulesets in `grammar_samples/core/PhysiCell_rules.cpp:1824-1944`, and applies rule results to cell behaviors in `grammar_samples/core/PhysiCell_rules.cpp:362-390` and `grammar_samples/core/PhysiCell_cell.cpp:315-324`.

The math match is exact for the active grammar engine. `multivariate_Hill_response_function` computes the normalized Hill response from signal, half-max, and Hill-power vectors (`grammar_samples/core/PhysiCell_basic_signaling.cpp:213-230`). `Hypothesis_Rule::evaluate` separates increasing and decreasing rules, computes up/down Hill responses, and writes the final behavior value (`grammar_samples/core/PhysiCell_rules.cpp:311-357`). One naming caveat matters: the C++ variable `U` is the up-regulated behavior target, while the paper's `$U$` is the normalized up response.

### Example Coverage

The public source contains project-level support for the main demonstrations:

- Hypoxia: oxygen-dependent proliferation, necrosis, and tumor-to-motile transitions in `grammar_samples/user_projects/hypoxia/config/cell_rules.csv:1-8`, matching the Figure 2 model described in `paper source/elsevier/paper.md:43-49`.
- CAF/PDAC invasion: ECM-driven phenotype transition and biphasic migration-speed rules in `grammar_samples/user_projects/epi_caf_invasion/config/cell_rules.csv:1-12`, matching the Figure 3 model and motility discussion in `paper source/elsevier/paper.md:53-59`.
- Tumor-immune models: base and extended immune rule files in `grammar_samples/user_projects/tumor_immune_base/config/cell_rules.csv:1-11` and `grammar_samples/user_projects/tumor_immune_extended/config/cell_rules.csv:1-23`, matching Figure 4 concepts in `paper source/elsevier/paper.md:87-93`.
- TAM-EGF: named grow, go, and go-and-grow rule files in `grammar_samples/user_projects/tam_egf/config/`, matching the Figure 5 hypotheses in `paper source/elsevier/paper.md:95-109`.
- PDAC therapy: immune/tumor response rules and treatment-specific initial-condition CSVs in `grammar_samples/user_projects/pdac_therapy/config/`, matching the virtual cohort setup in `paper source/elsevier/paper.md:111-119`.
- Neuro-development: SOM/AUD rule files and calibration code in `grammar_samples/user_projects/neuro_dev/`, matching the Allen Brain Atlas layer-calibration example in `paper source/elsevier/paper.md:121-125` and `paper source/elsevier/paper.md:313-315`.

### Figure Support

The local figure images support the paper's progression from grammar primitives to biological demonstrations. Figure 1 visually shows cell agents, dictionaries, hypothesis statements, and auto-generated mathematics. Figures S1-S3 show response-function behavior that matches the multivariate Hill implementation. Figures 2-7 show the hypoxia, CAF/PDAC, tumor-immune, TAM-EGF, PDAC therapy, and neuro-development examples (`paper source/elsevier/paper.md:484-512`).

The source repository supports the model layer behind these figures, but exact publication-panel reproduction is incomplete. I did not find a local manifest tying every panel to a command, random seed, output directory, or plotting script. Experimental panels such as microscopy or motility assays are described in the paper and external data sources, not fully contained in `grammar_samples`.

### Reproducibility Notes

To reproduce the method layer, use the released `grammar_samples` project and inspect or compile the relevant `user_projects/*` examples. The paper gives the build pattern `make list-user-projects` and `make load PROJ=myproject && make` (`paper source/elsevier/paper.md:195-203`). The most reliable code-reading path is:

1. `grammar_samples/core/PhysiCell_signal_behavior.cpp`
2. `grammar_samples/core/PhysiCell_rules.cpp`
3. `grammar_samples/core/PhysiCell_cell.cpp`
4. The target `grammar_samples/user_projects/<example>/config/cell_rules*.csv`
5. The target XML configuration under `grammar_samples/user_projects/<example>/config/`

Known gaps are explicit: no local Methods S1 markdown was supplied, exact figure-panel provenance was not found, GUI implementation details live in external PhysiCell Studio/nanoHUB resources, and some raw experimental datasets behind figure panels are outside the local code snapshot.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
