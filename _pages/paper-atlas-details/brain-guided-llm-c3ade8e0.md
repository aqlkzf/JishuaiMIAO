---
layout: default
permalink: /paper-atlas/brain-guided-llm-c3ade8e0/
title: "Brain-guided_LLM"
nav: false
wide: true
description: "这项工作研究的不是通常意义上的“用脑数据预测文字”，而是两个更具体的问题： 大语言模型在做演绎推理时，内部表征能否预测人类推理相关脑区的任务态 fMRI？ 如果存在这种对应关系，脑信号能否从一种分析指标变成真正改善模型推理的训练或干预信号？ 以往的脑-模型研究大多停留在表征对齐：拟合一个映射，观察模型特征能预测多少脑活动。但相关性不等于功能等价。尤其是，人脑的语言系统和推理系统并不完全重合；"
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
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>Brain-guided_LLM</h1>
    <p>Beyond representational alignment with brain-guided language models for robust reasoning</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/pkuxmq/Brain-guided_LLM" target="_blank" rel="noopener noreferrer" aria-label="Open code for Brain-guided_LLM">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Brain-guided LLM 方法详解

### 1. 论文要解决什么问题？

这项工作研究的不是通常意义上的“用脑数据预测文字”，而是两个更具体的问题：

1. 大语言模型在做演绎推理时，内部表征能否预测人类推理相关脑区的任务态 fMRI？
2. 如果存在这种对应关系，脑信号能否从一种分析指标变成真正改善模型推理的训练或干预信号？

以往的脑-模型研究大多停留在**表征对齐**：拟合一个映射，观察模型特征能预测多少脑活动。但相关性不等于功能等价。尤其是，人脑的语言系统和推理系统并不完全重合；一个全局上与脑信号相关的模型，也未必知道怎样修正某一道推理题的错误。

论文因此提出两种脑引导方法：

- **NARI**（Neural Activation guided Representation Intervention）：推理时直接修改模型的中间表征。
- **NARF**（Neural Activation guided Representation Fine-tuning）：训练时用脑引导目标更新模型参数。

它们的共同核心是：先学习“模型表征 → 人脑表征”的线性映射，再利用这个映射对模型表征求梯度。

### 2. 输入、输出与数据

#### 输入

- 演绎推理题：三段论或传递关系题，由若干前提和一个待判断结论组成，答案为 True/False。
- LLM：论文覆盖 1.5B 到 72B 参数的十个模型。
- 人类 fMRI：被试回答相同类型推理题时的单试次脑响应。
- 脑区：主要分析演绎推理相关区域，也与语言网络和多需求网络（MD）比较。

OpenNeuro 数据包括三段论和传递推理。fMRI 经过切片时间校正、头动校正、MNI 标准化、平滑和 GLMSingle 单试次 beta 估计；每位被试在推理区域掩模内保留响应最强的 10% 体素（补充材料 123-172 行）。

#### 中间变量

| 符号 | 含义 |
|---|---|
| $r_l$ 或 $x$ | LLM 第 $l$ 层对一道题的表征 |
| $X$ | 多道配对题目的模型表征矩阵，列为样本 |
| $y$ | 一道题对应的单个被试脑响应向量 |
| $Y$ | 多道配对题目的脑响应矩阵，列为样本 |
| $W,b$ | 从模型空间映射到脑空间的岭回归参数 |
| $\Delta r_l^p$ | 经过范数约束投影的表征干预方向 |

#### 输出

- 神经可预测性分数：模型表征对留出 fMRI 的预测能力。
- NARI 干预方向：用于纠正当前错误或迁移到新题的加性向量。
- NARF 模型：经过脑信号监督微调的 LLM，可继续与语言标签监督结合。

### 3. 从输入到输出的完整流程

```text
同一类推理题 ───────────────┐
    │                       │
    v                       v
LLM 前向计算             人类完成任务时的 fMRI
    │                       │
提取每层最终输入 token       单试次 beta + 个体化体素选择
的 attention/layer 输出      │
    └──────────┬────────────┘
               v
      岭回归：模型空间 -> 脑空间
               │
        ┌──────┴────────┐
        v               v
  留出集神经可预测性   相似度目标 S = Sim(Wx, y)
                        │
               ┌────────┴────────┐
               v                 v
        NARI：修改中间状态    NARF：更新注意力参数
               │                 │
        平均成功方向做迁移    可叠加 True/False 标签损失
               └────────┬────────┘
                        v
   新词、更多前提、全部前提顺序、命题逻辑、FOLIO、HCP 测试
```

#### 第一步：提取 LLM 与脑表征

模型先接收任务说明、前提和结论，并被要求以 `True` 或 `False` 开头回答。标准非思考模型使用每一层**最终输入 token**的 self-attention 模块输出和层输出，而不是注意力权重矩阵。代码在 `get_activations.py:63-83,131-163` 完成生成、标签解析和保存，在 `LM.py:163-211` 通过 NNsight 捕获各层张量。

这一选择有一个重要的模型特例：DeepSeek 思考模型走不同分支，对答案 token 的状态取平均（`get_activations.py:83-129`）。因此不同模型的表征抽取并非完全同构。

#### 第二步：计算神经可预测性

论文对模型和脑数据做中心化：

$$
X_c=X-\bar{x}\mathbf{1}^{\top},\qquad
Y_c=Y-\bar{y}\mathbf{1}^{\top}.
$$

然后拟合岭回归（补充公式 S1）：

$$
W=Y_cX_c^{\top}(X_cX_c^{\top}+\lambda I)^{-1},
\qquad b=\bar{y}-W\bar{x}.
$$

对每位被试、每种推理类型、每一层分别拟合 $W,b$，再在留出题目上计算脑体素预测。原始分数还要除以人-人预测得到的噪声上限，避免把 fMRI 固有噪声误当成模型缺陷（补充材料 280-303 行）。

代码中，`utils.py:191-215` 拼接 attention 与 layer 特征，`make_analysis.py:78-89,102-219` 做重复分层交叉验证、逐层评估和最佳层保存。

这里必须谨慎解释：神经可预测性只说明两种表征共享可线性读取的信息。补充材料指出，未训练模型也可能因为三段论和传递题的语言形式不同而在总体分析中得到非零分数；分类型分析则接近零（507-515 行）。所以这不是“LLM 和人脑使用同一推理算法”的证据。

#### 第三步：把线性映射变成脑引导梯度

对单个模型表征 $x$ 和脑目标 $y$，方法定义：

$$
S(x,y)=\operatorname{Sim}(Wx,y),
$$

其中 `Sim` 默认是余弦相似度，也可使用负 MSE。余弦目标对 $x$ 的梯度为：

$$
\nabla_x S_{\mathrm{cos}}
=\frac{W^{\top}y}{\lVert Wx\rVert\lVert y\rVert}
-\frac{\langle Wx,y\rangle W^{\top}Wx}
{\lVert Wx\rVert^3\lVert y\rVert}.
$$

负 MSE 形式在论文采用的比例约定下为：

$$
\nabla_xS_{-\mathrm{mse}}=-W^{\top}Wx+W^{\top}y.
$$

这两个梯度都同时依赖模型表征结构、脑表征结构及二者的交互，而不是一个固定的“人脑方向”（补充公式 S2，324-399 行）。

一个容易忽略但很关键的设计是：**引导目标使用 $Wx$，不使用预测公式中的截距 $b$**。相对于直接优化 $\operatorname{Sim}(Wx+b,y)$，这会多出与系统均值偏移有关的 $W^{\top}b$ 成分。论文消融显示，只有脑结构或只有偏移都不够，二者的联合效果最好（400-420 行）。

### 4. NARI：在推理时修正表征

NARI 对模型当前答错的题逐步优化中间状态：

1. 根据 $S$ 对第 $l$ 层表征求梯度。
2. 用 Adam 得到更新后的 $r'_l$。
3. 计算位移 $\Delta r_l=r'_l-r_l$。
4. 将位移投影到与该层尺度 $\sigma_l$ 相关的范数球：

$$
\Delta r_l^p=
\frac{\min(\lVert\Delta r_l\rVert,\alpha\sigma_l)}
{\lVert\Delta r_l\rVert}\Delta r_l,
\qquad r_l^p=r_l+\Delta r_l^p.
$$

5. 在所有选定层的前向传播中加上 $\Delta r_l^p$。
6. 每五步检查答案；一旦从错误变为正确就停止并保存方向。

非思考模型最多优化 200 步，DeepSeek-Distill-Qwen-1.5B 最多 50 步（补充材料 432-451 行）。代码对应 `make_intervention_sep.py:180-230,300-465` 和 `utils.py:327-389`。

逐题 NARI 需要反复验证，成本可能是多次完整前向。为了迁移，**NARI (gen.)** 按推理类型和层平均成功方向，再用验证集选择缩放系数 $\gamma$。对新题只需加一次预计算向量，不再需要新 fMRI，也几乎不增加标准前向之外的开销（补充材料 457-478 行；`make_intervention_generaldir.py:154-260`）。

### 5. NARF：把脑引导写入参数

NARF 不在每次推理时改状态，而是微调模型。代码支持两类脑监督目标：

1. **成功状态监督**：若 NARI 已把一道错题纠正，就把 $r_l+\Delta r_l^p$ 当作训练目标；原本答对的题可保持原表征作为正则目标（`finetune_model_sep.py:340-388`）。
2. **直接脑目标**：使用每位被试、每层和每类任务的 $W$ 与 fMRI，最小化 MSE 或 $1-\operatorname{CosSim}$（`finetune_model_sep.py:390-430`；`LM_finetune.py:114-196`）。

`LM_finetune.py:48-82` 冻结基础模型，只打开所选 self-attention 参数，并用 forward hook 取得最终 token 的 attention 输出。脚本默认训练中间一半层，也可通过 `--all_layer` 覆盖所有层（`finetune_model_sep.py:220-264`）。

**NARF+Label** 再加入普通 True/False 下一 token 交叉熵。它要验证的是：脑信号能否提供标签中没有的结构信息。补充消融表明，用随机信号或 one-hot 标签表征替换 fMRI，效果不如真实神经结构（634-651 行）。

### 6. 怎样验证“稳健推理”？

测试不只重复原始 70 道 fMRI 题，而是加入多种分布变化：

- 新伪词、新人名和新形容词；
- 三到六个前提；
- 每道题的全部 $N!$ 个前提排列；
- 命题推理；
- FOLIO-wiki-curated-TF 的 315 道自然语言一阶逻辑题；
- 独立的 HCP 关系推理 fMRI 数据。

代码生成平衡的三段论/传递数据，并在 `test_model.py:50-138` 枚举前提顺序、报告总体/任务类型/子类型准确率。HCP 和命题推理有独立脚本入口。

论文报告的主要结果是：

- 模型表征能预测部分可解释脑活动，但分推理类型后的可预测性更低，说明既有对齐也有差异。
- NARI 优于随机信号和随机方向控制，并可通过平均方向迁移到新题。
- NARF 在大多数推理子类型和更困难分布上提高准确率；十个模型的最大绝对增益达到 13 个百分点。
- NARF+Label 通常优于纯标签微调，说明脑监督与语言标签具有互补性。
- 任务特定的脑目标相似度提高，不代表传统全局神经可预测性一定同步提高。性能提升与“整体更像人脑”不是同一个命题。

### 7. 如何理解这项方法

最准确的理解不是“把 LLM 变成人脑”，而是：

> 利用同一组任务上的模型-脑配对数据，学习一个局部线性接口；这个接口把个体脑表征的结构转换成模型状态空间中的可操作梯度，再用状态干预或参数微调检验这些梯度是否具有功能价值。

这种设计的价值在于从相关性走向了可干预性，但结论仍有边界：fMRI 噪声大且被试特异；人类答案并非全对；岭回归、ROI 和中间层选择都会影响方向；总体神经可预测性还有任务语言形式的混杂。因此，结果支持“脑信号能为这些模型和任务提供有效引导”，不支持“LLM 已实现人脑的推理机制”。

### 8. 代码复现情况与缺口

官方代码快照提交为 `f4c6f6b1b737a3885e198185456c7f1241fd2149`。静态核验确认了表征提取、岭回归分析、NARI 投影优化、通用方向平均、NARF 脑损失、标签损失和生成任务评估；详细行号见 `doc_code.md`。总体代码-论文一致性评为 **medium**。

- **Not found：**未发现锁定全部模型、数据、中间产物、随机种子和主图命令的一键复现清单。
- **未运行：**模型下载、GPU 推理、fMRI 预处理、NARI、NARF、统计分析和绘图。
- **部分核验：**HCP 专用脚本存在，但没有逐分支审计全部实现。
- **来源限制：**主文 HTML 只有摘要、主图和可用性信息；方法细节主要来自 1,806 行补充材料。补充公式的 Markdown 排版有错位，本文按符号定义和可见公式片段还原，若用于严格推导应回查原 PDF。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Beyond Representational Alignment with Brain-guided Language Models for Robust Reasoning

**Nature Machine Intelligence (2026)** · DOI `10.1038/s42256-026-01278-w`

### Problem

Language models can correlate with human neural activity, but correlation alone does not show whether neural signals contain useful guidance for model reasoning. This paper asks whether LLM representations align with fMRI responses in deductive-reasoning regions and, more importantly, whether task-evoked brain activity can improve model behavior.

Prior brain-model work largely used neural predictivity as an observational similarity measure. That is limited here for two reasons: language and reasoning recruit partly dissociable human systems, and high global representational alignment need not encode the information needed to correct a particular reasoning error. The paper therefore moves from measuring correspondence to using neural-conditioned gradients as interventions and training signals.

### Proposed Framework

The study pairs LLM representations with single-trial fMRI from people solving syllogistic and transitive reasoning problems. A participant-, layer-, and reasoning-type-specific ridge regression maps model representations into neural space. Held-out prediction, normalized by a human-to-human ceiling, measures **neural predictivity**.

The same map defines a guidance objective $S=\operatorname{Sim}(Wx,y)$ between the projected model state and a neural target. Two methods use its gradient:

- **NARI** modifies intermediate representations at inference time. It optimizes an erroneous item's layer states, projects each displacement to a bounded norm, checks whether the answer is corrected, and averages successful displacements to obtain a transferable general direction.
- **NARF** fine-tunes selected attention parameters toward brain-induced targets. It can use successful NARI states or a direct cosine/MSE neural objective and can be combined with ordinary answer-label cross-entropy as **NARF+Label**.

The key technical choice is that guidance omits the ridge intercept. This makes the update depend not only on centered model/brain structure but also on their systematic mean shift. The supplement's ablations argue that useful directions require the joint neural-model geometry rather than random signals, random directions, or labels alone.

### Evaluation and Main Findings

The study evaluates ten LLMs spanning 1.5B-72B parameters. The paired fMRI analysis uses an OpenNeuro deductive-reasoning dataset; transfer tests introduce new lexical items, three-to-six-premise chains, every premise ordering, propositional reasoning, FOLIO-wiki-curated-TF, and a separate HCP relational-processing dataset.

- **Partial alignment:** trained LLM states predict a meaningful fraction of explainable activity in deductive-reasoning regions, with middle-layer and attention-module outputs often strongest. Predictivity falls when syllogistic and transitive items are analyzed separately, so aggregate scores include coarse task-type structure and should not be read as mechanistic equivalence.
- **Functional guidance:** NARI corrects model errors more successfully than random-signal and random-direction controls. Averaged successful directions transfer to unseen problems without requiring new fMRI at inference time.
- **Training gains:** NARF improves performance across most reasoning subtypes and harder distribution shifts. The paper reports gains up to **13 percentage points** across the evaluated models.
- **Complementarity:** NARF+Label generally outperforms label-only fine-tuning. Random neural substitutes and one-hot label representations do not match the improvement, supporting a contribution from human neural structure beyond ordinary labels.
- **No simple alignment-performance identity:** the task-specific neural objective increases after NARF, but conventional global brain predictivity does not consistently increase. Better reasoning and greater global neural correlation are therefore not treated as the same outcome.

These are publication claims supported by the abstract, main figures, and supplementary analyses; this workspace did not rerun the experiments.

### Reproducibility Assessment: 3/5

**Strengths.** The paper identifies public OpenNeuro and HCP datasets, generated data, GitHub/Zenodo code, and source-data links. The official repository snapshot at commit `f4c6f6b1b737a3885e198185456c7f1241fd2149` includes activation extraction, fMRI preprocessing scripts, neural-predictivity analysis, NARI, NARI (gen.), NARF/NARF+Label, generated datasets, HCP extensions, and example shell commands. Direct inspection found six exact core paper-code matches, two partial matches, and one missing reproduction contract; overall static fidelity is **medium**.

**Limitations.** The workflow depends on large external model checkpoints, OpenNeuro/HCP files, preprocessed intermediate data, and outputs from earlier stages. No locked environment or one-command manifest regenerates every main figure. Model-specific branches and experiment variants are distributed across top-level scripts, and the main HTML conversion is paywalled beyond the abstract/figures, leaving some panel-level statistics available only indirectly through the supplement. GPU training, intervention, preprocessing, and numerical reproduction were not run.

### Important Caveats

- fMRI provides noisy, participant-specific task signals; it is not a ground-truth reasoning algorithm. Human accuracy in the paired dataset is itself imperfect.
- Aggregate neural predictivity is partly confounded by the linguistic distinction between reasoning types; within-type results are weaker.
- NARI's correction criterion and scale search can incur multiple model forward passes, whereas the averaged NARI (gen.) direction is the low-overhead deployment form.
- Participant quality matters: the supplement reports substantial subject-to-subject variation in intervention success.
- The work demonstrates useful neural-conditioned directions in the tested tasks. It does not establish biological equivalence, universal reasoning improvement, or independence from the chosen linear map and ROI pipeline.

For the full algorithm and equations, read `doc_method.md`; for verified implementation anchors, read `doc_code.md`; for panel-grounded evidence, read `figure_analysis.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
