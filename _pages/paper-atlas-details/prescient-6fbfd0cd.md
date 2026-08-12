---
layout: default
permalink: /paper-atlas/prescient-6fbfd0cd/
title: "PRESCIENT"
nav: false
description: "PRESCIENT 把多个真实时间点的单细胞转录组“快照”看成同一随机动力系统在不同时间的群体分布：它学习一个神经网络表示的势能地形，在这个地形上反复推进带噪声的细胞状态，使模拟群体尽量接近真实观测群体；训练好后，可以从任意细胞状态出发模拟未来轨迹，也可以先修改基因表达再预测终末命运分布。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Communications · 2021</span>
    </div>
    <h1>PRESCIENT</h1>
    <p>Generative modeling of single-cell time series with PRESCIENT enables prediction of cell trajectories with interventions</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PRESCIENT 方法详解

### 一句话理解

PRESCIENT 把多个真实时间点的单细胞转录组“快照”看成同一随机动力系统在不同时间的群体分布：它学习一个神经网络表示的势能地形，在这个地形上反复推进带噪声的细胞状态，使模拟群体尽量接近真实观测群体；训练好后，可以从任意细胞状态出发模拟未来轨迹，也可以先修改基因表达再预测终末命运分布。

### 1. 它要解决什么问题？

时间序列 scRNA-seq 在每个时间点测到的是不同细胞。我们知道“第 2 天有哪些细胞”“第 4 天有哪些细胞”，却不知道第 2 天的某个细胞具体变成了第 4 天的哪一个细胞。因此，核心问题不是简单排序，而是：

- 如何从没有细胞配对关系的群体快照中学习连续动力学？
- 如何在真实物理时间中模拟一个细胞未来可能走向哪些命运？
- 如何处理分化过程中的随机性与细胞增殖？
- 如何从训练时未见的初始状态，尤其是人为改变基因表达后的状态，继续向前模拟？

传统伪时间方法只能给出相对顺序，不能直接表示物理时间中的随机过程。FateID（*Nature Methods*, 2018）主要利用终末类型构建命运分类；Waddington-OT（*Cell*, 2019）计算时间点间的最优传输耦合，但不产生可反复查询的参数化动力系统；PBA（*PNAS*, 2018）和 pseudodynamics（*Nature Biotechnology*, 2019）虽显式描述动力学，但在求解方式或状态维度上受限。PRESCIENT 的新意是学习一个高维、随机、可生成的全局分化地形。

### 2. 核心直觉：学习一张“会推动细胞运动的地形”

论文把 PCA 空间中的细胞状态记为 \({\rm X}(t)\)，用随机微分方程描述其变化：

$$
{\rm{dX}}\left(t\right)=&#123;&#123;\mu }}\left({\rm{X}}\left(t\right)\right){\rm{dt}}+\sqrt{2{\sigma }^{2}}{\rm{dW}}\left(t\right).
$$

其中：

- \(\mu({\rm X}(t))\) 是确定性的漂移，表示当前位置受到的“力”；
- \({\rm W}(t)\) 是布朗运动，表示同一初始细胞可能产生不同未来；
- 论文定义 \(\mu({\bf x})=-\nabla\Psi({\bf x})\)，即细胞从高势能区域向低势能区域移动。

数值模拟使用一阶离散：

$$
{\rm{X}}\left(t+\Delta {\rm{t}}\right)={\rm{X}}\left(t\right)+ \mu \left({\rm{X}}\left(t\right)\right)\Delta {\rm{t}}+\sqrt{2{\sigma }^{2}\Delta {\rm{t}}}{\rm{Z}}\left(t\right).
$$

所以每个小步都由三部分组成：当前状态、地形决定的漂移、随机噪声。重复很多小步，就得到一条随机轨迹；从同一个细胞重复模拟很多次，就得到命运概率分布。

### 3. 训练时只有群体快照，怎么学地形？

关键是比较“模拟群体”和“真实群体”，而不是比较不存在的一一对应细胞。

假设从起始时间的细胞出发，用当前神经网络地形模拟到 \(t_i\)，得到预测分布 \(\rho_\Psi(t_i,{\bf x})\)；真实数据给出经验分布 \(\hat\rho(t_i,{\bf x})\)。论文最小化各时间点的 Wasserstein 距离并加入正则项：

$$
\mathop&#123;&#123;\rm{min }}}\limits_{\Psi \in {\rm{K}}}\left[\mathop{\sum}\limits _{i=1}^{n}&#123;&#123;\rm{W}}}_{2}(&#123;&#123;\hat{\rho }}}\left({t}_{i},{\bf{x}}\right),&#123;&#123;{\rho }}}_{\Psi }({t}_{i},{\bf{x}}))^{2}\right]+\tau \mathop{\sum }\limits_{j=1}^&#123;&#123;m}_{n}}\frac{\Psi (&#123;&#123;\bf{x}}}_&#123;&#123;\bf{j}}})}&#123;&#123;\sigma }^{2}}.
$$

Wasserstein 距离可以理解为：把模拟群体“搬运”成真实群体所需的最小总代价。代码用 GeomLoss 的 Sinkhorn 算法近似计算，并把梯度穿过所有模拟步反向传播到势能网络。

### 4. 为什么必须考虑细胞增殖？

一个起始细胞可能产生许多后代，另一个可能不增殖甚至死亡。如果所有起始细胞权重相同，模型会把后期某些细胞群体的扩张误解释成地形流向。

PRESCIENT 在最优传输中给源细胞设置权重 \(\alpha_i\)，令其与期望后代数成正比，而目标细胞权重保持均匀。后代数有两种来源：

1. 有谱系追踪时，用同一条形码在后期与当前时间的细胞数之比；
2. 没有谱系追踪时，用细胞周期和凋亡基因集估计出生率 \(b\) 与死亡率 \(d\)。

$$
n={\rm{exp }}\,\left({\rm{dt}}* \left(b-d\right)\right),\qquad
g=b-d=\frac&#123;&#123;\rm{log }}n}&#123;&#123;\rm{dt}}}.
$$

表达估计还包括：在 PCA 空间取 20 个近邻、迭代平滑 5 次，再用 logistic 函数把出生/死亡 signature 转成速率。图 2 直观显示：加入增殖不仅提高命运预测指标，也会改变早期区域的势能和漂移结构。

### 5. 完整计算流程

```text
归一化表达 + 真实时间标签 + 可选细胞类型
                    |
                    v
缩放表达 -> PCA -> 按时间点组织细胞
                    |
                    +--> 谱系条形码或表达 signature 估计增殖率
                    |
                    v
在末时间点群体上预训练标量神经网络
（对比散度式势能正则）
                    |
                    v
对每个训练 epoch、每个观测目标时间：
  按增殖权重采样起始细胞
  -> 多次随机一阶推进到目标时间
  -> 计算模拟群体与真实群体的加权 Sinkhorn 距离
  -> 加入势能正则
  -> 反向传播、梯度裁剪、Adam 更新、学习率衰减
                    |
                    v
保存训练后的地形与检查点
           |                         |
           v                         v
任意起点向前模拟              修改基因 z-score
           |                  -> 通过原 PCA 变换
           |                  -> 与未扰动细胞配对模拟
           +-----------+-------------+
                       v
ANN 终末类型分类、命运比例、Wasserstein 距离、
扰动前后终末群体差异
```

#### 数据预处理

论文不是对所有数据使用完全相同的预处理。Weinreb 造血数据使用 50 个 PC，并去除与细胞周期相关的高变基因；留出第 4 天的实验只在第 2、6 天拟合预处理。Veres 胰岛分化数据用 Seurat 处理、选 2,500 个高变基因，并在 30-PC 模型输入中去除与 TOP2A 相关的基因。当前包能完成标准化、PCA、UMAP 和按时间打包，但论文特定的上游特征选择仍需用户复现。

#### 势能网络与预训练

代码的 `AutoGenerator` 是输出单个标量的全连接网络。论文实验使用 2 层、每层 400 个单元、Softplus 激活。正式训练前，模型先在末时间点群体上做对比散度式预训练，使势能函数具有合理初始形状。

#### 多时间点训练

代码对每个目标时间都从同一个起始时间向前模拟，并不是逐个相邻时间点串接训练。各目标时间的 Sinkhorn 损失先累积梯度，然后统一做一次 Adam 更新；还可加入 \(\tau\) 控制的势能正则、梯度裁剪和每 100 次乘 0.9 的学习率衰减。

#### 推断和扰动

训练完成后，可以按时间点或细胞类型抽取初始细胞，反复调用随机推进得到轨迹。扰动分析先把目标基因在标准化表达中的值直接设为给定 z-score，再用已保存的 PCA 投影到模型空间。随后对同一模型运行未扰动和扰动模拟，并用近邻分类器统计终末细胞类型。

这一操作回答的是“在模型学到的地形中，这种人工初始状态会流向哪里”，不是“该基因在真实生物系统中必然因果控制该命运”。

### 6. 代码与论文真正对应在哪里？

| 环节 | 主要代码 | 结论 |
|---|---|---|
| 标量网络、漂移、一步模拟 | `prescient/train/model.py:36-91` | 结构存在，但势能符号有歧义 |
| Sinkhorn 损失 | `prescient/train/model.py:95-116` | 与加权群体距离训练直接对应 |
| 预训练与正式训练 | `prescient/train/run.py:17-192` | 包含模拟、正则、Adam、裁剪、调度、检查点 |
| 增殖率与权重 | `prescient/utils.py:52-138`; `commands/train_model.py:112-148` | 实现 signature 平滑、速率计算和时间指数权重 |
| 任意起点模拟 | `prescient/simulate/sim.py:19-73` | 可按时间/类型采样并逐步推进 |
| 基因扰动 | `prescient/perturb/pert.py:5-19` | 覆盖 z-score 替换和 PCA 投影 |
| 扰动前后配对模拟 | `commands/perturbation_analysis.py:32-78` | 加载检查点并保存两组模拟 |
| 论文 Weinreb 评估 | `depr/weinreb.py:150-363` | 在旧版实验模块中，属于 legacy 路径 |

### 7. 主要实验结论

#### 造血谱系追踪

- 留出第 4 天：用第 2、6 天训练后，模拟第 4 天的 Wasserstein 距离优于时间点基线和 WOT 插值。
- 克隆命运偏倚：不考虑增殖时 \(r=0.196\pm0.020\)、AUROC \(=0.601\pm0.006\)；加入谱系推导增殖后提高到 \(r=0.347\pm0.029\)、AUROC \(=0.692\pm0.012\)。
- 表达推导增殖与谱系推导增殖相关性虽弱，但模型达到 \(r=0.399\pm0.025\)、AUROC \(=0.725\pm0.008\)。
- 即使测试细胞没有出现在训练集中，命运预测性能也相近，说明模型不是简单记忆训练点。

#### 造血扰动

对已知中性粒细胞或单核细胞相关 TF 做上调/下调，模拟终末比例通常沿预期方向变化；更大扰动往往产生更大效应，多 TF 联合扰动比单基因更稳定，而随机非 TF 对照整体变化较弱。

#### 胰岛细胞分化

在 7 个时间点的数据中，早期增强 *NEUROG3/NKX6.1* 会提高内分泌命运，增强 *PTF1A/HES1* 产生相反方向；同样扰动若在较晚时间加入，效果明显衰减。200+ TF 的大规模模拟筛选恢复了多种已知 α、β 和 EC 相关因子，也给出新的候选与起始亚群依赖关系。

### 8. 必须保留的证据边界

- **MISSING：** 本工作区没有补充材料 Markdown；论文若把超参数选择细节只放在 Supplementary Note 中，目前不能完整核查。
- **Not found：势能符号。** 论文定义 \(\mu=-\nabla\Psi\)，但代码 `_drift` 返回 `_pot` 对输入的正梯度，并在 `_step` 中直接相加。没有找到证据证明 `_pot` 明确定义为 \(-\Psi\)。
- **Not found：噪声参数映射。** 论文离散式含 \(\sqrt{2}\sigma\)，代码使用标准差为 `train_sd` 的随机数再乘 \(\sqrt{dt}\)，两者的对应关系未写明。
- **论文设置不等于 CLI 默认值。** 论文为 2×400 网络、裁剪 0.1，并给出数据集特定学习率；当前 CLI 默认为 1×500、裁剪 0.25、学习率 0.01、`train_sd=0.5`。
- **Partial：完整复现。** 核心算法和大量评估逻辑存在，但没有找到覆盖全部论文图的统一配置、原始数据到图形的自动化流程和完整检查点集合。
- **实现细节差异：** 当前通用 `simulate` 函数接收增殖权重却没有用于初始采样；论文实验的加权采样逻辑主要见 legacy 评估代码。
- **因果边界：** 模拟扰动与已知生物学方向一致，说明模型具有预测价值，但不能替代真实扰动实验。

### 9. 如何正确使用这套方法？

研究者应把 PRESCIENT 看作“从群体时间序列学习出的随机生成模型”，而不是精确恢复真实单细胞谱系的工具。可靠使用需要：

1. 明确物理时间标签和数据集特定预处理；
2. 提供或认真估计增殖率；
3. 显式设置论文/任务所需超参数，不直接依赖当前 CLI 默认值；
4. 用留出时间点、独立谱系信息或已知扰动方向验证模型；
5. 将新扰动结果作为实验优先级排序和假设生成，而不是因果结论。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## PRESCIENT

### Problem

Time-series scRNA-seq observes different cells at each time point, so it gives population snapshots rather than continuous lineages. Pseudotime methods order cells without physical-time dynamics; FateID (*Nature Methods*, 2018) predicts fate from terminal labels; Waddington-OT (*Cell*, 2019) estimates couplings between snapshots but has no reusable parametric simulator; PBA (*PNAS*, 2018) and pseudodynamics (*Nature Biotechnology*, 2019) model dynamics with restricted solution or state spaces. None of these combinations directly provides a high-dimensional stochastic process that can be initialized with an unseen or computationally perturbed cell.

### Method

PRESCIENT (Potential eneRgy undErlying Single Cell gradIENTs) learns a neural scalar landscape in PCA space from physical-time scRNA-seq marginals. The paper defines a stochastic diffusion whose drift is the negative gradient of a potential. Training repeatedly simulates a source population forward with a first-order stochastic update and minimizes a proliferation-weighted, regularized Wasserstein discrepancy to observed populations, approximated with GeomLoss Sinkhorn. The trained landscape can then generate trajectories from arbitrary initial cells.

Cell proliferation enters as source weights proportional to expected descendant abundance. Rates can be computed from lineage barcodes or estimated from smoothed cell-cycle and apoptosis signatures. For perturbation analysis, selected standardized gene-expression values are replaced by requested z-scores, transformed through PCA, and used to initialize paired perturbed and unperturbed simulations.

### Evaluation and findings

On the Weinreb mouse hematopoiesis lineage-tracing data, PRESCIENT recovered a held-out day-4 population better than simple time-point baselines and WOT interpolation. For clonal fate bias, adding empirical proliferation improved performance from \(r=0.196\pm0.020\), AUROC \(=0.601\pm0.006\) to \(r=0.347\pm0.029\), AUROC \(=0.692\pm0.012\). Expression-derived proliferation achieved \(r=0.399\pm0.025\), AUROC \(=0.725\pm0.008\), despite correlating only weakly with lineage-derived rates.

The model gave similar fate performance for initial cells included or excluded from training. In silico hematopoietic perturbations generally shifted neutrophil/monocyte fractions in directions expected for known TFs, with dose and ensemble effects stronger than random non-TF controls. On a seven-time-point pancreatic differentiation dataset, early endocrine/exocrine perturbations had larger modeled effects than later perturbations. A screen of 200+ TFs recovered known α-, β-, and enterochromaffin-associated factors and produced stage-specific hypotheses.

### Reproducibility and limitations

The checked repository contains the core neural model, stochastic update, Sinkhorn training, proliferation utilities, simulation, perturbation commands, and legacy Weinreb/Veres evaluation logic. Code-paper fidelity is **medium**: the major computational components are present, but a full paper-run manifest and raw-to-figure workflow are **Not found**.

Two technical ambiguities matter. First, the paper defines \(\mu=-\nabla\Psi\), whereas code returns the positive gradient of `_pot`; no available source establishes that `_pot` intentionally represents \(-\Psi\). Second, the code's `train_sd` is not explicitly mapped to the paper's \(\sqrt{2}\sigma\) noise convention. Published settings also differ from current CLI defaults (notably 2×400 versus 1×500 units, clipping 0.1 versus 0.25, and paper-specific learning rates/noise).

Supplementary Markdown is **MISSING**, and some hyperparameter-selection details point to the unavailable Supplementary Note. The current generic simulator accepts but does not use proliferation weights for initial sampling, while legacy experiment code performs weighted sampling. Dependencies, dataset preprocessing, paper-specific checkpoints, and configurations require deliberate reconstruction. Finally, predicted gene perturbations are model-based hypotheses, not causal experimental validation, and PCA can discard low-expression fate regulators.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
