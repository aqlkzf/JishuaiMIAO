---
layout: default
permalink: /paper-atlas/mctogene-homi-4d6fbf17/
title: "MCToGene (HOMI)"
nav: false
wide: true
description: "MCToGene 的输入是 H&E 全切片图像中每个空间转录组 spot 对应的图像 patch 和二维坐标，输出是每个 spot 的多基因表达。它不只看单个 patch，也不只计算中心 spot 与邻居的成对关系，而是先做 pairwise attention，再显式构造三元关系的 many-body attention，并把两条路径层级融合；最终用条件流匹配从稀疏噪声逐步生成表达。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>CVPR 2026 · 2026</span>
    </div>
    <h1>MCToGene (HOMI)</h1>
    <p>Predicting Spatial Transcriptomics from Histology Images via High-Order Multi-Cell Interaction Modeling</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MCToGene（HOMI）：用高阶多细胞交互从 H&E 预测空间基因表达

### 一句话理解

MCToGene 的输入是 H&E 全切片图像中每个空间转录组 spot 对应的图像 patch 和二维坐标，输出是每个 spot 的多基因表达。它不只看单个 patch，也不只计算中心 spot 与邻居的成对关系，而是先做 pairwise attention，再显式构造三元关系的 many-body attention，并把两条路径层级融合；最终用条件流匹配从稀疏噪声逐步生成表达。

论文未提供 supplement 文件，当前也未找到官方代码仓库。因此以下机制可以由论文公式和图确认，但张量形状、邻居图构造、ZINB 参数、训练超参数和采样求解器不能由直接源码复核。

### 1. 任务定义

一张组织切片包含 $N$ 个 spot：

$$
C\in\mathbb{R}^{N\times2},\quad
I\in\mathbb{R}^{N\times3\times H\times W},\quad
G\in\mathbb{R}^{N\times N_G}.
$$

$C$ 是坐标，$I$ 是图像 patch，$G$ 是目标表达。训练时三者都可用；推断时只给 $(C,I)$，模型预测 $G$。这里的“multi-cell”是通过 spot 邻域建模实现的；一个 spot 可能包含多个真实细胞，因此论文的交互单元更准确地说是空间 spot/局部组织单元，而不一定是一一分割的细胞。

### 2. 整体流水线

图 1 给出五步主线：

1. 把 WSI 按 ST spot 切成图像 patch，用预训练病理 foundation model 得到视觉特征 $P$；
2. 把 spot 坐标编码为对旋转、平移和反射稳定的空间关系；
3. 在稀疏邻居图上做 pairwise attention，融合视觉、空间和当前时刻的表达差；
4. 通过 Readout 汇总局部上下文，再做 incoming/outgoing many-body attention，显式建模三元 spot 关系；
5. 层级解码器融合 pairwise 与 many-body 表示，流匹配解码器从先验噪声迭代生成表达。

图中 pairwise 和 many-body 模块重复 $N_x$ 次，但论文没有在正文给出 $N_x$、hidden dimension、head 数等完整实现参数。

### 3. 条件流匹配：从稀疏先验到真实表达

论文从零膨胀负二项（ZINB）先验采样 $G_0$，用真实表达 $G_1$ 定义线性路径：

$$
G_t=(1-t)G_0+tG_1,\qquad t\sim U(0,1).
$$

模型 $f_\theta(G_t,I,C,t)$ 同时看当前表达状态、图像、坐标和时间。推断从 $t=0$ 的 $G_0$ 出发，多步运输到数据分布。

这里有一处必须保留的论文内在歧义：正文称模型学习“velocity field”，线性路径的标准目标速度应为 $G_1-G_0$；但论文式 (1) 明写：

$$
\min_\theta\mathbb{E}\left[\|f_\theta(G_t,I,C,t)-G_1\|^2\right],
$$

即直接回归终点 $G_1$。没有代码时无法判断真实训练目标是 endpoint prediction、velocity prediction，还是论文公式漏写了 $-G_0$。复现者不能擅自把二者当成等价实现。

ZINB 先验被用于模拟 ST 表达的过度离散与零膨胀，但正文没有报告其均值、离散度、零膨胀概率是固定、按基因估计还是可学习，也没有明确推断采用 Euler、ODE solver 或其他离散更新。因此“flow matching”框架可确认，完整采样算法 `Not found`。

### 4. 视觉与空间编码

视觉分支使用预训练 UNI 病理基础模型：

$$
P=\{p_0,\ldots,p_N\}=f_{\mathrm{base}}(I_0,\ldots,I_N).
$$

使用 foundation model 的目的，是让形态表示具备跨癌种和跨批次迁移能力，而非从有限 ST 配对数据重新学习完整视觉编码器。

坐标分支用 $E(n)$-invariant attention 计算有向关系：

$$
C_{i\to j}=F_c(c_i,c_j).
$$

论文宣称它对二维欧氏变换中的旋转、平移和反射保持不变，以减少切片方向差异造成的批次效应。没有源码时，$F_c$ 使用距离、相对向量、球谐/几何张量还是其他不变量无法确认。

时间 $t$ 通过正弦余弦频率编码 $e(t)$ 加入 patch 表示，使早期高噪声阶段更依赖全局语义和粗空间结构，后期低噪声阶段更关注精细形态。这个“阶段性关注”是设计解释；论文没有展示逐时刻消融来独立证明网络确实形成该行为。

### 5. Pairwise attention：先建立局部二体关系

对中心 spot $i$ 和邻居 $j$，模型构造视觉 query/key、空间关系以及当前表达差：

$$
\Delta Y_{t,ij}=Y_{t,i}-Y_{t,j},
$$

$$
A_{ij}=\operatorname{Softmax}_i\!\left(
\operatorname{MLP}(Z_{Q,i}\|Z_{K,j}\|C_{i\to j}\|\Delta Y_{t,ij})
\right).
$$

注意式中写的是 $\operatorname{Softmax}_i$，但描述意图通常是对给定中心 $i$ 的邻居 $j$ 归一化；这可能是下标排版问题。无代码时归一化维度仍是复现边界。

值分支把视觉与空间信息分开聚合，再拼接并残差加回 $p_i$：

$$
Z_i^{\mathrm{pair}}=operatorname{MLP}\left(
\sum_{j\in\mathcal N(i)}A_{ij}Z_{V,j}\ Big\|\
\sum_{j\in\mathcal N(i)}A_{ij}C_{i\to j}
\right)+p_i.
$$

因此 pairwise 模块回答“邻居 $j$ 对中心 $i$ 有多重要”，但不能表示“两个邻居一起出现时才产生的协同或拮抗效应”。

### 6. Many-body attention：显式构造三元关系

Readout 先把 pairwise 邻域汇总为节点上下文。many-body 模块随后以一条关系为 query、另一条关系为 key/value，并用第三条关系产生 bias 与 gate。

#### Incoming 路径

固定 $(i,j)$，枚举 $(j,k)$：

$$
o_{ij}^{\mathrm{in}}=\sum_{k=1}^N a_{ijk}^{\mathrm{in}}v_{jk}^{\mathrm{in}},
$$

$$
a_{ijk}^{\mathrm{in}}=\operatorname{softmax}_k\left(
\frac{q_{ij}^{\mathrm{in}}\cdot p_{jk}^{\mathrm{in}}}{\sqrt d}
+b_{ik}^{\mathrm{in}}
\right)\sigma(g_{ik}^{\mathrm{in}}).
$$

它表示从 $i\to j\to k$ 的关系链；第三边 $(i,k)$ 不只提供几何偏置，还通过 sigmoid gate 调制强度。

#### Outgoing 路径

固定 $(i,j)$，枚举共享起点的 $(i,k)$：

$$
o_{ij}^{\mathrm{out}}=\sum_{k=1}^N a_{ikj}^{\mathrm{out}}v_{kj}^{\mathrm{out}}.
$$

两条方向共同覆盖不同的三元依赖，再按邻居平均并经 MLP 得到 $Z_i^{\mathrm{many}}$。图 2 显示 multi-head incoming/outgoing 更新和第三关系的 bias/gate，是理解 HOMI 的核心图。

复杂度并未真正消失。论文通过稀疏邻居图和有限 $K$ 个邻居把全局组合爆炸限制在局部搜索，但 many-body 仍比 pairwise 更耗内存。表 4 中 full MCToGene 为 8720 MB、2.01 s/epoch，STFlow 为 6164 MB、1.35 s/epoch；即约 1.41 倍内存和 1.49 倍时间（正文写“约 1.66× slower”，与表中直接比值略有差异）。

### 7. 层级解码：为何不是简单叠加

模型先用两个 MLP 对齐 pairwise 与 many-body 通道：

$$
\tilde Z^{\mathrm{pair}}=\operatorname{MLP}(Z^{\mathrm{pair}}),\qquad
\tilde Z^{\mathrm{many}}=\operatorname{MLP}(Z^{\mathrm{many}}),
$$

再拼接预测：

$$
Y'=\operatorname{Decoder}(\tilde Z^{\mathrm{pair}}\|\tilde Z^{\mathrm{many}}).
$$

表 3 显示 Pair only、MB only、简单 Pair+MB 均不如 hierarchical 版本稳定；表 5 显示邻居数从 4 增到约 16 往往改善性能，超过 20 后饱和或下降，说明更大邻域会引入过平滑与噪声。贡献来自“选择并耦合局部高阶关系”，不是无限增加邻居。

### 8. 结果与图怎样读

表 1 在 HEST-1k 十个 cohort 和 STImage-1K4M 七个器官子集上，以 top-50 HVG 的逐基因 Pearson correlation 为指标。MCToGene 平均分别为 0.435 和 0.316，相对最强基线提高 4.82% 和 7.85%；COAD 从 0.326 提高到 0.410。表 2 的四个 biomarker 平均从 STFlow 0.786 提高到 0.806。

图 3 比较 TP63 与 FGFBP1 的空间预测图，支持高表达区域定位更接近真实图。图 4 将注意力热点与表达热点对齐，并讨论 VIM/VIM/KRT5 等高分三元组。图 5 对高注意力 spot 做通路富集，得到表皮谱系、中间丝和基质重塑等主题。

这些可视化是“模型注意区域与已知生物模式一致”的支持证据，不是细胞间因果机制的证明。attention 权重受输入形态、表达路径和训练目标共同影响；之后再从高 attention spots 选择高表达基因做富集，也存在选择偏倚。

### 9. 复现清单与证据边界

论文可确认：UNI 编码器、$E(n)$ 不变空间模块、ZINB 起点、pairwise 与 incoming/outgoing many-body 公式、层级融合、数据拆分原则和评价指标。

以下内容 `Not found`：官方代码、配置文件、模型权重、完整 Appendix/supplement、本地可执行环境、邻居图具体 sparsification、ZINB 参数、网络深度/宽度/head、训练 schedule、flow 采样器和预处理脚本。当前不能做 paper-code Exact/Partial 映射，也不能声称表格已复现。

因此，MCToGene 最稳妥的定位是：一个用局部三元注意力增强 H&E→ST 条件生成的论文方法。其高阶交互设计和实验趋势有清楚公式与图表支持，但工程可复现性仍受未公开实现限制；“多细胞交互”应理解为预测模型捕获的统计依赖，而非已验证的生物因果作用。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MCToGene Summary

MCToGene predicts spatial gene expression from H&E by explicitly adding high-order local interactions to a flow-matching generator. UNI encodes histology patches; invariant spatial attention encodes geometry; pairwise attention selects local neighbors; incoming/outgoing many-body attention models triplets; a hierarchical decoder fuses both paths.

On HEST-1k and STImage-1K4M, the paper reports average Pearson correlations of 0.435 and 0.316, corresponding to relative improvements of 4.82% and 7.85% over the strongest listed baselines. Biomarker prediction averages 0.806 versus STFlow 0.786. Ablations favor hierarchical Pair+MB over either branch or uncoupled stacking, with neighborhood size around 16 generally strongest.

The accuracy gain costs additional resources: the full model reports 8720 MB and 2.01 s/epoch versus STFlow's 6164 MB and 1.35 s/epoch. Large neighborhoods saturate or degrade, consistent with noise and oversmoothing.

### Reproducibility

The CVPR 2026 paper and extracted figures are available, but no official code, weights, configuration, or supplement was found after title/method/author searches. The flow objective is also ambiguous: prose says velocity prediction, while Eq. 1 targets $G_1$. Consequently, the conceptual method is well documented but the numerical results are not independently reproducible from this workspace.

**Assessment: 2/5 for computational reproducibility; strong paper-level method traceability.**

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
