---
layout: default
permalink: /paper-atlas/flowsig-e0b896c9/
title: "FlowSig"
nav: false
description: "单细胞 RNA 测序和空间转录组通常产生两类互补结果： 细胞通讯分析给出可能发生的配体–受体作用； 基因表达模块（GEM）描述细胞内部协同变化的转录程序。 传统分析往往把二者分开。我们可能知道“哪些细胞在发信号”，也可能知道“哪些基因模块在变化”，但仍不知道：某个被接收的信号，是否通过一个细胞内转录程序，进一步驱动了另一个信号的输出？ FlowSig 把这个问题写成一个图结构学习问题。"
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
      <span>Cell-Cell Communication</span>
      <span>Nature Methods · 2024</span>
    </div>
    <h1>FlowSig</h1>
    <p>Inferring pattern-driving intercellular flows from single-cell and spatial transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## FlowSig 方法详解：从单细胞与空间转录组推断细胞间“信息流”

### 1. 这篇论文要解决什么问题？

单细胞 RNA 测序和空间转录组通常产生两类互补结果：

- 细胞通讯分析给出可能发生的配体–受体作用；
- 基因表达模块（GEM）描述细胞内部协同变化的转录程序。

传统分析往往把二者分开。我们可能知道“哪些细胞在发信号”，也可能知道“哪些基因模块在变化”，但仍不知道：**某个被接收的信号，是否通过一个细胞内转录程序，进一步驱动了另一个信号的输出？**

FlowSig 把这个问题写成一个图结构学习问题。图中只有三类节点：

```text
流入信号（inflow） → 细胞内 GEM → 流出信号（outflow）
                            ↕
                          其他 GEM
```

最终输出不是简单的配体–受体清单，而是“流入→模块→流出”的有向依赖网络。

### 2. 为什么已有方法不够？

CellChat（*Nature Communications*, 2021）和 COMMOT（*Nature Methods*, 2023）可以推断候选细胞通讯，但它们本身不回答两个通讯事件之间是否存在依赖，也不明确给出中间的细胞内转录模块。

DIALOGUE（*Nature Biotechnology*, 2022）、Tensor-cell2cell（*Nature Communications*, 2022）、MOFAcellular/MOFAtalk（*eLife*, 2023）和 MultiNicheNet（bioRxiv, 2023）能够提取多细胞程序、因子或差异通讯，但通常不直接学习一个由流入信号、GEM 和流出信号共同组成的数据驱动有向图。

这种区别在 Kang PBMC 数据上很直观：CellChat 输出可组合成 6,886 个潜在“流入–流出”关系，而 FlowSig 最终保留了 44 条流，涉及 6 个流入、20 个 GEM 和 12 个流出。FlowSig 的价值不是简单减少边数，而是加入“依赖关系”和“细胞内中介”两个层次。

### 3. 核心创新

FlowSig 的关键创新可以概括为三点：

1. 把细胞通讯变量和 GEM 放进同一个“流表达矩阵”；
2. 对有扰动的 scRNA-seq 使用条件独立性与条件不变性，对空间数据使用空间化流入估计和分块 bootstrap；
3. 用明确的生物学方向约束，把统计 CPDAG 转换为可解释的流入→GEM→流出假设。

需要强调：FlowSig 学到的是稳定的统计依赖与部分方向，不是已经被实验完全证明的分子因果链。

### 4. 三类变量如何构造？

#### 4.1 非空间 scRNA-seq 的流入信号

scRNA-seq 不能直接测量每个细胞实际接收了多少配体。FlowSig 用受体表达和已知下游 TF 活性构造代理量：

$$
R\times\overline{TF},
\qquad
\overline{TF}=\frac{TF_1+\cdots+TF_m}{m}.
$$

$R$ 表示接收信号的潜力，$\overline{TF}$ 表示受体下游通路是否已经激活。下游 TF 来自 OmniPath 或 exFINDER 等先验数据库。

如果受体包含多个亚基，则使用几何平均：

$$
R=(R_1\cdots R_n)^{1/n}.
$$

当前代码的默认 `v1` 分支与论文公式一致；代码还增加了一个论文未描述的 `v2` 构造。

#### 4.2 空间转录组的流入信号

空间数据可以利用位置约束更直接地估计“收到的信号”。对于位置 $S$ 上的配体 $L$：

$$
\operatorname{inflow}(L,S)=\sum_R C_S^{(L-R)},
$$

其中 $C_S^{(L-R)}$ 是 COMMOT 对 $L$–$R$ 作用在该位置的接收侧通讯分数。代码会把同一配体对应的 receiver 列相加。

#### 4.3 GEM 变量

一般矩阵分解写为

$$
X=WH^T,
$$

$W$ 表示每个细胞或空间点对各 GEM 的成员权重，$H$ 表示基因对 GEM 的载荷。

非空间多条件数据使用 pyLIGER：

$$
X^{(c)}=F^{(c)}\left(W+V^{(c)}\right)^T,
$$

把条件共享和条件特异的载荷分开。空间数据使用 NSF：

$$
X=FW^T,
$$

其中 $F$ 随空间位置变化。

论文还描述了对成员权重进行归一化和 $\log(1+\alpha\widetilde W)$ 缩放；当前代码在已检查的流矩阵组装函数中只明确执行了按行归一化，因此精确复现时应核对这一差异。

#### 4.4 流出信号

流出变量定义为通讯分析涉及的配体基因表达。它表示细胞“表达了多少待发送信号”，并不保证该信号最终被别的细胞接收。

### 5. 完整计算流程

```text
归一化表达 + 原始计数 + CellChat/COMMOT 输出
                    │
                    ├─ pyLIGER/NSF 构造 GEM
                    ├─ 构造流入变量
                    └─ 提取配体流出变量
                              │
                       流表达矩阵 X_flow
                              │
                筛选“信息量高”的信号变量
             ├─ scRNA-seq：Wilcoxon + q 值 + logFC
             └─ 空间数据：Moran's I
                              │
                    多次 bootstrap 图学习
             ├─ 有扰动 scRNA-seq：UT-IGSP
             └─ 空间/无扰动数据：GSP
                              │
                      平均得到加权 CPDAG
                              │
              施加 inflow→GEM→outflow 方向约束
                              │
                     删除低频、低置信度边
                              │
                    有向加权细胞间流网络
```

### 6. 如何筛选变量？

候选变量太多会增加计算量和假阳性，因此 FlowSig 只筛选流入和流出，所有 GEM 都保留。

对于有扰动的 scRNA-seq，流入和流出分别进行 Wilcoxon 秩和检验。论文常用阈值是校正后 $P<0.05$ 且 $\log(FC)>0.5$，多扰动条件取并集。

对于空间数据，使用 Squidpy 计算全局 Moran's $I$，保留空间自相关超过阈值的信号变量。论文给出 $I>0.1$ 的示例，鼠胚脚本使用 0.15。

### 7. 图是怎样学出来的？

FlowSig 使用偏 Pearson 相关构造条件独立性检验。

- GSP 根据条件独立关系搜索稀疏 DAG，并输出对应 CPDAG；
- UT-IGSP 在此基础上加入对照与扰动之间的条件不变性检验，同时估计未知干预靶点。

CPDAG 表示一组具有相同骨架和 $v$-structure 的 Markov 等价 DAG，例如：

$$
x\to z\leftarrow y.
$$

因此，原始统计结果不会给出所有边的唯一方向。

### 8. Bootstrap 与边置信度

FlowSig 对每次重采样学习一个邻接矩阵 $A^{(b)}$，再计算

$$
\widetilde A=B^{-1}\sum_{b=1}^{B}A^{(b)}.
$$

非空间数据在每个条件内重采样细胞；空间数据先把组织划分为块，再在块内重采样，尽量保留空间相关结构。

对于一条无向骨架边：

$$
w(i,j)=A_{ij}+A_{ji}.
$$

当 $w(i,j)<w^*$ 时删除该边。胰岛和类器官分析使用 0.7 左右的阈值，空间分析通常使用更严格的阈值。

代码中还有一个重要细节：每次 bootstrap 会删除标准差为零的变量，避免偏相关和不变性检验在常数列上失败。

### 9. 生物学方向约束是什么意思？

FlowSig 最后只保留以下方向：

- inflow→GEM；
- GEM→GEM；
- GEM→outflow。

原本无向的 GEM–GEM 边在最终 NetworkX 有向图中会变成双向边。这一步是结构先验与后处理，不是从数据单独识别出的完整因果方向。

因此，路径

```text
FGFR1 inflow → GEM-6 → BMP4 outflow
```

应该解释为：这些变量之间存在稳定依赖，方向与预设的生物流顺序一致，值得进一步实验验证；不能直接解释为已证明的具体生化反应链。

### 10. 论文如何验证 FlowSig？

#### 合成数据

三种 SHH/BMP 模型提供已知真值。更准确的“已接收信号”测量和扰动信息主要提高或稳定 TNR，说明 FlowSig 的主要收益是减少假阳性，而不是在所有场景中提高 TPR。

#### 皮层类器官

FlowSig 从 D18/D35 数据中提出 FGF→EOMES、BMP→PAX6/NR2F1 等候选调控。随后加入 FGF8b 或 BMP4 并做 RT–qPCR：EOMES 和 PAX6 下调，NR2F1 上调。该实验支持部分候选关系，但没有验证整张网络的每条边。

#### 胰岛 IFN-γ 刺激

FlowSig 找到 FGF、IL-6、MDK 和 SST 等主要流入，以及共享或刺激特异的 GEM→outflow 路径，展示了如何把差异表达与网络中介联系起来。

#### COVID-19 多扰动

从健康到中度、重度 COVID-19，推断的调控性流入和 GEM 数量减少，而炎症趋化因子流出增加。这里是疾病组间关联，不能直接解释为病程中的实验干预因果。

#### 小鼠胚胎空间数据

论文提出 Shh–Wnt5a 激活–抑制反馈：Shh 通过 Foxa2 等促进自身和 Wnt5a，Wnt5a 通过 Myc 相关机制抑制 Shh。这个结果是具有空间和 TF 支持的候选模式，但尚未直接证明存在 Turing 不稳定性。

### 11. 代码与论文的一致性

核心方法的一致性较好：流变量构造、差异/Moran's $I$ 筛选、GSP/UT-IGSP、bootstrap 平均、生物学方向约束和低置信度边过滤都能在代码中找到直接实现。

但存在三个重要复现问题：

1. 当前包版本为 0.5.4，论文分析脚本使用较老的参数接口，需要改写少量关键字参数；
2. 数据保存在外部 Zenodo，脚本依赖相对路径，不能直接开箱运行；
3. 图 6 的 random forest/pyGAM TF 排名实现未在已获取的两个仓库中找到，仓库中也没有自动化测试套件。

因此，代码–论文总体一致性评为 **中等**，复现性约为 **3/5**：核心算法透明，但端到端复现仍需数据下载、环境配置和 API 适配。

### 12. 如何区分证据与推断？

| 类型 | 本文中的例子 | 应当如何解读 |
|---|---|---|
| 论文直接声明 | 流入公式、UT-IGSP/GSP 路由、bootstrap 平均、各应用的实验结果 | 表示作者在论文中报告了该方法或结果，不等于本地独立重现 |
| 代码直接验证 | `v1` 流入构造、变量筛选、图学习、零方差列删除、边方向约束 | 表示已在当前代码快照的具体源码行中确认 |
| 分析性解释 | 把 FlowSig 视为“机制假设优先级排序器”，把新冠结果视为疾病严重度关联 | 是对论文和代码证据的保守综合，不是论文的逐字结论 |
| `Not found` / 缺失证据 | 图 6 的 random forest/pyGAM 执行代码、自动化测试套件 | 在已获取的两个仓库和针对性搜索范围内未找到；不应改写成“不存在” |

### 13. 局限与正确使用方式

- 偏相关依赖线性高斯假设，未必适合原始单细胞分布；
- 样本量不足会导致条件检验不稳定；
- CCC 或 GEM 方法的选择会改变输入节点和最终路径；
- GEM 是粗粒度中介，不能替代精确 GRN；
- 静态图不能描述信号传播的时间动态；
- 生物学方向约束是先验，不等于完整因果识别。

最合适的使用方式是把 FlowSig 当成一个**机制假设优先级排序器**：它把庞大的通讯候选压缩成少量“流入→模块→流出”路径，帮助研究者选择后续 perturbation、成像或多组学验证对象。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## FlowSig — concise paper summary

### Problem

Single-cell and spatial transcriptomics can reveal ligand–receptor communication and intracellular gene-expression programs, but these are usually analyzed as separate descriptions. FlowSig addresses the missing middle: it infers which received signals are linked through intracellular gene-expression modules (GEMs) to subsequent ligand outflows, producing a compact intercellular-flow network rather than an unstructured set of pairwise communication events.

### Why existing approaches are insufficient

CellChat (*Nature Communications*, 2021) and COMMOT (*Nature Methods*, 2023) infer candidate cell–cell communication, but do not determine whether one signaling activity statistically depends on another through an intracellular mediator. Multicellular-program methods such as DIALOGUE (*Nature Biotechnology*, 2022), Tensor-cell2cell (*Nature Communications*, 2022), MOFAcellular/MOFAtalk (*eLife*, 2023) and MultiNicheNet (bioRxiv, 2023) find coordinated programs or differential communication, but generally do not learn a data-driven directed graph joining signal inflows, intracellular GEMs and signal outflows. Direct CCC results can also be combinatorially broad: in the Kang PBMC benchmark, CellChat implied 6,886 potential inflow-to-outflow relationships, whereas FlowSig retained 44 flows over 6 inflows, 20 GEMs and 12 outflows (`paper.md:67-73`).

### Method

FlowSig constructs an augmented matrix with three variable types:

- **inflow:** for non-spatial scRNA-seq, receptor expression multiplied by mean expression of known immediate downstream TFs; for spatial data, summed received-signal scores from COMMOT;
- **intracellular module:** cell/spot membership in GEMs constructed with methods such as pyLIGER or NSF;
- **outflow:** ligand gene expression.

It filters for informative signal variables—differentially flowing signals across perturbations or spatially variable signals by Moran's $I$—while retaining all GEMs. It then learns a CPDAG using partial-correlation-based causal structure learning: UT-IGSP for control-versus-perturbed scRNA-seq and GSP for spatial data. Results are bootstrap-aggregated, biologically implausible directions are removed or reoriented to obey inflow→GEM→outflow, and low-frequency edges are discarded (`paper.md:192-212`).

### Evaluation and main findings

- **Synthetic validation:** across three SHH/BMP models, more accurate received-signal measurement and perturbation information primarily improved or stabilized true-negative rates, supporting reduced false positives rather than a universal sensitivity gain (Fig. 2).
- **Organoid experiment:** FlowSig nominated EOMES downstream of FGF and PAX6/NR2F1 downstream of BMP. Growth-factor exposure followed by RT–qPCR showed FGF-associated EOMES downregulation and BMP-associated PAX6 downregulation/NR2F1 upregulation (Fig. 3).
- **Pancreatic islets:** IFN-γ stimulation altered FGF, IL-6, MDK and SST inflows and produced shared plus response-specific GEM-mediated outflow paths (Fig. 4).
- **COVID-19:** increasing severity was associated with fewer inferred regulatory inflows/GEMs but stronger inflammatory chemokine outflow, particularly from macrophage/neutrophil-associated programs (Fig. 5).
- **Mouse embryo spatial data:** FlowSig generated a candidate Shh–Wnt5a activator–inhibitor feedback in which Shh promotes itself and Wnt5a, while Wnt5a inhibits Shh through Myc-associated regulation (Fig. 6). This is a mechanistic hypothesis, not direct proof of a Turing instability.

### What is novel

The central contribution is the integration of CCC variables and intracellular modules into one causal-dependency problem. Perturbation information or spatially resolved received-signal estimates help restrict the graph, while an explicit biological ordering converts the partially directed statistical result into interpretable inflow→module→outflow hypotheses. FlowSig therefore complements, rather than replaces, CCC and GEM-construction methods.

### Limitations

- Partial-correlation CI/invariance tests assume a linear-Gaussian model and need adequate sample size.
- The output depends on the chosen CCC and GEM methods; alternative inputs can change nodes and paths.
- The biological orientation is an imposed structural prior, so final arrows are not fully identified causal effects.
- GEMs are coarse mediators and do not expose the exact intracellular GRN.
- The graph is static and does not model signaling dynamics.
- Zero-variance variables and large candidate sets create practical failure modes or false positives.

### Reproducibility

The paper provides a Python package (`axelalmet/flowsig`), a separate manuscript-analysis repository (`axelalmet/FlowSigAnalysis_2023`) and processed data through Zenodo DOI `10.5281/zenodo.10850397`. The current package commit implements the core inflow construction, informative-variable filtering, GSP/UT-IGSP learning, bootstrap aggregation and biological edge filtering with high conceptual fidelity.

Reproduction is not turnkey. The manuscript scripts use an older API and need adaptation for FlowSig 0.5.4; processed H5AD and communication outputs are external; no automated tests were found; and code for the Fig. 6 random-forest/pyGAM TF interpretation was not located. Overall code-paper fidelity is **medium**, with a reproducibility rating of **3/5**.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
