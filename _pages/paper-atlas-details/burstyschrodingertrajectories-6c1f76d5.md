---
layout: default
permalink: /paper-atlas/burstyschrodingertrajectories-6c1f76d5/
title: "BurstySchrodingerTrajectories"
nav: false
description: "这篇论文没有发明新的 Sinkhorn 算法。它改变的是 Sinkhorn 之前的“参考过程”：传统方法默认细胞在表达空间中近似扩散，本文则从一个含转录爆发和基因调控网络（GRN）的随机动力学模型出发，估计细胞从初态走到各个终态的概率，再寻找既接近该机制参考、又严格匹配两个观测时点边缘分布的耦合。"
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
      <span>npj Systems Biology and Applications · 2026</span>
    </div>
    <h1>BurstySchrodingerTrajectories</h1>
    <p>Cell trajectory inference based on Schrödinger problem and a mechanistic model of stochastic gene expression</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41540-026-00743-x" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Bursty Schrödinger Trajectories：用随机基因表达机制约束细胞轨迹

### 一句话理解

这篇论文没有发明新的 Sinkhorn 算法。它改变的是 Sinkhorn 之前的“参考过程”：传统方法默认细胞在表达空间中近似扩散，本文则从一个含转录爆发和基因调控网络（GRN）的随机动力学模型出发，估计细胞从初态走到各个终态的概率，再寻找既接近该机制参考、又严格匹配两个观测时点边缘分布的耦合。

因此，方法回答的是“在给定 GRN 与动力学参数的前提下，哪些跨时点细胞配对最符合该机制”，而不是从快照数据中直接恢复已经被观测验证的单细胞谱系。

### 1. 问题、输入与输出

单细胞测量通常是破坏性的。时刻 $t_1$ 的细胞与时刻 $t_2$ 的细胞来自不同样本，不能按细胞编号直接相连。论文把两个时点分别写成

$$
X=(x_1,\ldots,x_N),\qquad Y=(y_1,\ldots,y_N),
$$

其中每个向量是 $G$ 个基因的蛋白或 mRNA 状态。目标是得到 $N\times N$ 耦合矩阵 $Q$；$Q_{ij}$ 表示初始细胞 $x_i$ 与末端细胞 $y_j$ 之间的概率质量。论文实验使用均匀边缘，因此每行、每列的和都必须等于 $1/N$。

除两个快照外，Bursty 路径还需要 GRN 结构及动力学参数。模拟实验中这些参数是已知的；Semrau 小鼠胚胎干细胞实验中，它们来自先前的 CARDAMOM/Harissa 推断。输出是跨时点概率耦合，而不是一条确定的、可验证的真实细胞轨迹。

### 2. 为什么扩散参考可能不够

标准扩散参考把状态间的平方欧氏距离变成核：

$$
D_{\mathrm{ref}}(x,y)\propto
\exp\left[-\frac{\lVert x-y\rVert^2}
{2\sigma^2(t_2-t_1)}\right].
$$

它偏好几何上相近的终点，却不知道某个基因会激活或抑制另一个基因，也不知道转录会以短促爆发的形式发生。相同的欧氏距离可能对应完全不同的动力学可达性。本文的核心假设是：若机制模型较可信，用它产生的转移概率比纯几何距离更适合作为参考。

### 3. Bursty GRN 参考过程

#### 3.1 连续流与随机爆发

对每个基因，爆发之间的 mRNA 与蛋白状态按确定性方程演化：

$$
\frac{dM}{dt}=-d_0M,\qquad
\frac{dP}{dt}=s_1M-d_1P.
$$

mRNA 在随机时刻发生爆发，爆发大小服从指数分布。基因 $i$ 的爆发频率受全部蛋白状态和 GRN 相互作用控制：

$$
k_{on,i}(P)=
\frac{k_{0,i}+k_{1,i}\exp(\beta_i+\sum_j\theta_{ji}P_j)}
{1+\exp(\beta_i+\sum_j\theta_{ji}P_j)}.
$$

$\theta_{ji}>0$ 表示基因 $j$ 激活 $i$，$\theta_{ji}<0$ 表示抑制。由此得到的是分段确定性马尔可夫过程（PDMP）：事件之间连续衰减和翻译，事件到达时产生随机 mRNA 跳跃。

本地代码把 GRN 参数写入 Harissa 的 `NetworkModel`，再调用 `model.simulate()`；对应 `inference_code_python/general_function.py:14-63`。论文的动力学由 Harissa 执行，并非在仓库里重新实现一个独立求解器。

#### 3.2 从动力学得到 $B_{ref}$

多基因情形没有直接使用解析转移密度。对每个初始细胞 $x_i$：

1. 从 $x_i$ 出发独立模拟 $n$ 条 Bursty 轨迹到 $t_2$；
2. 对这些模拟终点拟合 Gaussian KDE；
3. 在每个观测终点 $y_j$ 上评价密度；
4. 把这些数填入参考矩阵 $B_{ref}$。

这正是 Figure 13 从左到右表达的过程：紫色初始细胞 → 橙色模拟后代 → 平滑终态密度 → 在绿色观测终点上读出概率。代码位于 `general_function.py:102-149`。蛋白、mRNA 和三基因版本分别有不同函数；当 RNA 或三基因 KDE 输入秩不足时，代码加入 $10^{-8}$ 随机噪声避免奇异协方差。

需要注意一个实现细节：模拟数据先用两个端点共同的最大值加 `0.1` 做缩放（`general_function.py:65-99`），而 $B_{ref}$ 最后按整个矩阵总和归一化，不是先逐行归一化。真正的均匀行列边缘随后由 Sinkhorn 投影施加。

#### 3.3 单基因解析参照

单基因、无反馈的约化模型还能写出含“区间内无爆发”和“至少一次爆发”两部分的转移律。论文用正则化解析核构造 $RB_{ref}$，作为模拟近似 $B_{ref}$ 的参照。公开脚本没有逐项重写论文中的 Kummer 函数密度，而是调用 Harissa `BurstyBase.distribution()`；因此代码对论文解析推导是 **Partial**，不是逐公式 Exact。

### 4. Schrödinger 投影

给定任何正参考矩阵 $R$，论文求解

$$
\operatorname{Sch}(R;u,v)=
\arg\min_Q H(Q\mid R),
$$

满足

$$
\sum_jQ_{ij}=u_i,\qquad \sum_iQ_{ij}=v_j,
$$

其中

$$
H(Q\mid R)=\sum_{ij}Q_{ij}\log\frac{Q_{ij}}{R_{ij}}.
$$

Sinkhorn 交替缩放左右因子，使耦合达到指定边缘。将 $R$ 换成 Bursty、扩散或约化 Bursty 参考，分别得到 $B_{sch}$、$D_{sch}$ 和 $RB_{sch}$。

代码中有两套实现，不能混为一谈：

- 论文主要实验脚本调用 `general_function.py:163-179` 的 `sinkhorn()`；它以 Frobenius 范数相对变化小于默认 `0.1` 为停止条件，并用 $10^{-300}$ 防止除零。
- `sinkhorn_bridge.py:23-61` 是更独立的静态 Schrödinger 示例，实现更严格的默认容差 `1e-10`，但主时间间隔脚本并未导入它。

因此“仓库包含标准 Sinkhorn 逻辑”是 Exact；“所有论文结果都由独立 `sinkhorn_bridge.py` 产生”则不成立。

### 5. 论文如何比较方法

#### 单基因

Figure 1 比较 $D_{sch}$、模拟得到的 $B_{sch}$、解析约化模型的 $RB_{sch}$ 与按同一模拟细胞编号形成的对角真值。$RB_{sch}$ 的对角最清楚，扩散参考最分散。Figure 2 再以 $RB_{sch}$ 为参照，显示 $H_{D,R}$ 高于 $H_{B,R}$。

#### 小型 GRN 模拟

Figure 3–8 改用 $B_{sch}$ 作为机制参考，比较

$$
H_{D,B}=H(D_{sch}\mid B_{sch})
$$

与模拟误差控制量

$$
H_B=H(B_{ref}\mid B_{sch}).
$$

结果在 toggle switch、不同细胞数、不同 GRN 参数、多个二基因和三基因网络，以及 mRNA 模拟中都保持 $H_{D,B}>H_B$。Figure 4 还用总变差、Jensen–Shannon divergence 和 Frobenius 范数检查结论不是 KL 指标特有。

但这组证据有一个重要限定：数据本身由 Bursty 模型生成，用匹配的 Bursty 参考胜过扩散，证明的是机制匹配在这些模拟条件下有效，不等于对任意真实分化过程都更准确。

代码的 `entropy()`（`general_function.py:183-193`）在 $P$ 或 $R$ 为零时直接跳过该项。这与严格 KL 在 $P>0,R=0$ 时应为无穷大的定义不同；在核保持正值的常规运行中影响可能有限，但应视为数值实现边界。

### 6. Semrau 真实数据实验

实验数据含 41 个基因、9 个时间点。论文用 0 h 和 72 h 端点预测 36 h 分布：

1. 用先前推断的 Bursty GRN 构造 $B_{ref}(0,72)$；每个初始细胞默认模拟 10,000 次；
2. Sinkhorn 得到 $B_{sch}(0,72)$；
3. 按耦合抽取端点对，并按逐基因权重 $\alpha^*$ 插值得到 36 h 分布；
4. 与真实 36 h 快照比较逐基因 EMD；
5. 与正则化 OT/扩散参考的线性中点插值比较。

Figure 9 报告 $\Delta_{EMD}=EMD_D-EMD_B$：正值表示 Bursty 更好。论文称 11 个基因打平，其余 30 个中 22 个偏向 Bursty。这个实验验证的是中间时点的**边缘分布预测**，没有真实细胞谱系可用于验证个体配对。

公开代码对这里是 **Partial**。参考构建、耦合采样、插值和 EMD 路径都存在，但 `interpolation_code_python/main_analysis.py:22-27` 把 `num_iter` 设为 `0`。所以当前默认入口只使用初始化的时间比例权重，不会执行论文描述的 $\alpha^*$ 优化；需要显式修改迭代数才能启用 `optimization.py` 中的优化循环。

### 7. 代码—论文匹配结论

| 环节 | 结论 | 证据边界 |
|---|---|---|
| Harissa Bursty 模拟与 GRN 参数化 | Exact | `general_function.py:14-63` |
| 端点提取与共同缩放 | Exact | `general_function.py:65-99` |
| 多基因 KDE $B_{ref}$ | Exact | `general_function.py:102-149` |
| 扩散 $D_{ref}$ | Exact | `general_function.py:153-158` |
| 主实验 Sinkhorn 缩放 | Exact with caveat | `general_function.py:163-179`，停止条件较宽松 |
| 单基因解析核 | Partial | 公式在论文中，代码委托 Harissa |
| 指标与模拟实验脚本 | Exact / Partial | 核心计算存在；一个 metrics CSV 输出块疑似损坏 |
| Semrau 机制参考与 EMD | Partial | 流程存在，但默认 `num_iter=0` 禁用权重优化 |
| 一键复现全部图 | Not found | 脚本、预计算文件和绘图入口分散 |

### 8. 正确使用这篇论文的结论

最稳妥的结论是：Schrödinger 桥的结果强烈依赖参考过程；在转录爆发和 GRN 动力学合适时，用机制转移核替代纯扩散核能产生明显不同、在匹配模拟中更接近生成过程的耦合。真实数据结果支持其分布预测潜力，但尚不能证明恢复了真实单细胞谱系，也不能证明输入 GRN 错误时仍然可靠。

复现时应优先核对四件事：GRN 参数来源、状态是蛋白还是 mRNA、归一化与 log 变换、以及实际调用的 Sinkhorn/插值优化入口。后两项正是论文描述与公开默认代码之间最容易被忽略的边界。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## BurstySchrodingerTrajectories - Cell trajectory inference based on Schrödinger problem and a mechanistic model of stochastic gene expression

### Paper Information

- **Title**: Cell trajectory inference based on Schrödinger problem and a mechanistic model of stochastic gene expression
- **Journal**: npj Systems Biology and Applications (2026)
- **Published**: 2026
- **DOI**: `10.1038/s41540-026-00743-x`

### Motivation and Novelty

Single-cell RNA-seq gives destructive snapshots: cells can be measured at several times, but the same cell is not followed through differentiation. Trajectory inference therefore becomes a distribution-matching problem between time points. Standard optimal-transport approaches often use a diffusion-like reference process, which is mathematically convenient but biologically weak for transcriptional bursting and GRN-driven state changes.

This paper replaces the diffusion reference in the discrete Schrödinger problem with a mechanistic Bursty gene-expression reference. The novelty is not a new Sinkhorn solver; it is the construction of $B_{ref}$ from a stochastic Bursty GRN model and the demonstration that this reference produces better couplings than the usual diffusion reference on simulated GRNs and one experimental mESC time series.

Prior methods leave the specific gap targeted here:

| Method | Journal / Venue | Year | Limitation addressed here |
|---|---:|---:|---|
| Waddington-OT / Schiebinger et al. | Cell | 2019 | Uses OT with diffusion-like movement assumptions rather than a transcriptional Bursty reference |
| TrajectoryNet | arXiv | 2020 | Learns dynamic transport but does not encode a mechanistic GRN bursting process |
| Liu et al. learned transport cost | arXiv | 2019 | Learns costs for alignment; not a trajectory-specific mechanistic reference and less interpretable |
| scEGOT | bioRxiv | 2023 | Uses Gaussian-mixture OT with Euclidean geometry, not a GRN-driven stochastic reference |
| CellRank | Nature Methods | 2022 | Provides fate probabilities from velocity or transition kernels; used as validation context, not a mechanistic Schrödinger reference |
| CARDAMOM / Ventre et al. | PLOS Computational Biology | 2023 | Infers Bursty GRN parameters; this paper uses such parameters to infer trajectory couplings |
| Harissa | Computational Methods in Systems Biology | 2023 | Simulates/infer Bursty GRNs; this paper wraps that process into reference couplings for trajectory inference |

### Method Overview

The input is two empirical cell-state distributions, usually $\mu$ at $t_1$ and $\nu$ at $t_2$. In simulated benchmarks, states are protein or mRNA counts from a known Bursty GRN. In the Semrau application, states are experimental mRNA counts and the GRN parameters come from a previous CARDAMOM/Harissa inference.

The Bursty model describes deterministic mRNA/protein decay and synthesis between stochastic transcription bursts:

$$
\dot{M}(t)=-d_0M(t), \qquad \dot{P}(t)=s_1M(t)-d_1P(t).
$$

The burst rate for gene $i$ depends on protein levels and the GRN interaction matrix:

$$
k_{on,i}(P_1,\ldots,P_G)=
\frac{k_{0,i}+k_{1,i}\exp(\beta_i+\sum_{j=1}^G\theta_{ji}P_j)}
{1+\exp(\beta_i+\sum_{j=1}^G\theta_{ji}P_j)}.
$$

For a one-gene reduced model, the paper can compute a reference coupling $RB_{ref}$ from an analytical transition law. For multi-gene GRNs, it estimates $B_{ref}$ by repeatedly simulating the Bursty model from each initial cell, fitting a Gaussian/KDE density to simulated final states, and evaluating that density at observed final cells. The diffusion baseline $D_{ref}$ is a Gaussian kernel on Euclidean distances.

Given any reference matrix $R$, the method solves the discrete Schrödinger problem:

$$
Sch(R;u,v)=\arg\min_Q H(Q|R)
$$

subject to the row and column marginals matching $u$ and $v$. Sinkhorn scaling gives $B_{sch}$, $D_{sch}$, or $RB_{sch}$ depending on the reference. Simulated analyses compare these couplings using relative entropy plus total variation, Jensen-Shannon divergence, and Frobenius norm. The Semrau analysis uses $B_{sch}(0h,72h)$ to predict the 36 h distribution and compares per-gene Earth Mover's Distance against a regularized-OT/diffusion baseline.

### Evaluation

#### Datasets and Settings

| Dataset / Setting | Role | Metric |
|---|---|---|
| One-gene simulated protein model | Toy test with analytical reduced Bursty reference | Matrix visual structure; $H_{D,R}$, $H_{B,R}$, $H_R$ |
| Two-gene toggle-switch simulations | Main small-GRN benchmark | $H_{D,B}$ vs $H_B$ across time gap and cell count |
| Metric robustness toggle-switch simulations | Checks whether entropy drives the conclusion | Entropy, total variation, Jensen-Shannon divergence, Frobenius norm |
| Perturbed toggle-switch references | Tests sensitivity to alternate GRN parameter values | $H_{D,B}$ and $H_B$ under alternate $B_{ref}$ models |
| Other two-gene GRNs | Tests whether the result is toggle-specific | $H_{D,B}$ across five GRN motifs |
| Three-gene activation chain and repressilator | Tests small multi-gene motifs | $H_{D,B}$ and $H_B$ |
| Simulated toggle-switch mRNA data | Bridge from protein benchmark to mRNA experiments | $H_{D,B}$ vs $H_B$ |
| Semrau et al. mESC differentiation | Experimental validation with 41 genes, 9 time points | $\Delta_{EMD}=EMD_D-EMD_B$ for 36 h prediction from 0 h and 72 h |

#### Main Results

| Result | Evidence |
|---|---|
| Reduced one-gene Bursty coupling is visually closest to identity ground truth | Figure 1: $RB_{sch}$ is strongly diagonal, while $D_{sch}$ is diffuse |
| Non-reduced Bursty approximation beats diffusion in one-gene entropy comparisons | Figure 2: $H_{D,R}$ stays above $H_{B,R}$ for all tested transient time gaps |
| Toggle-switch diffusion coupling is much farther from Bursty coupling than the Bursty control | Figure 3: $H_{D,B}$ remains far above $H_B$ across time gaps and cell counts |
| The conclusion is not specific to KL/entropy | Figure 4: entropy, TV, JSD, and Frobenius indicators are all positive after control normalization |
| Moderate GRN parameter perturbations do not reverse the Bursty advantage | Figure 5: altered Bursty references still yield $H_{D,B}$ curves far above $H_B$ |
| The simulated advantage extends to several two-gene and three-gene GRNs | Figures 6-7: all tested motifs keep $H_{D,B} > H_B$ |
| Simulated mRNA data preserves the qualitative ordering | Figure 8: mRNA $H_{D,B}$ remains far above $H_B$ |
| Semrau 36 h interpolation favors Bursty for most non-tied genes | Figure 9: 11 genes tie; among the remaining 30 genes, 22 favor Bursty according to the paper |

The evidence is strongest for the simulation claim: if data are generated by a Bursty GRN, using a Bursty reference improves the inferred coupling relative to diffusion. The experimental Semrau result is encouraging but narrower. It evaluates distribution-level prediction at a held-out time point, not true single-cell lineage accuracy.

### Code Verification Summary

The public repository `https://github.com/fourniecl/inference_trajectories_PDMP` was cloned at commit `d24c17143faa377f942d571b555249199a274926`. Core paper components are present:

- Harissa Bursty simulation and GRN parameter setup: `inference_trajectories_PDMP/inference_code_python/general_function.py:14`
- Endpoint extraction and joint normalization: `inference_trajectories_PDMP/inference_code_python/general_function.py:65`
- KDE-based $B_{ref}$ construction: `inference_trajectories_PDMP/inference_code_python/general_function.py:102`
- Diffusive $D_{ref}$: `inference_trajectories_PDMP/inference_code_python/general_function.py:153`
- Sinkhorn/Schrödinger scaling used by main experiments: `inference_trajectories_PDMP/inference_code_python/general_function.py:163`
- Entropy, TV, JSD, and Frobenius metrics: `inference_trajectories_PDMP/inference_code_python/general_function.py:183`
- Semrau interpolation and EMD comparison: `inference_trajectories_PDMP/interpolation_code_python/main_analysis.py:95`

Important paper-code caveats are documented in `doc_code.md`: the one-gene analytical density is delegated to Harissa `BurstyBase.distribution()` rather than spelled out directly; main experiments use a research-script Sinkhorn with default norm-change tolerance `0.1`, not the stricter standalone `sinkhorn_bridge.py`; one metric script appears to have a malformed CSV/header block; and `interpolation_code_python/main_analysis.py` sets `num_iter = 0`, so the public default Semrau script does not actually run the advertised alpha/beta optimization loop unless edited.

### Reproducibility

#### Rating: 3/5

The analysis is reproducible enough to understand and partially rerun the method, but not polished enough for a clean one-command reproduction of every paper result.

Strengths:

- The paper PDF explicitly links the public code repository, and the cloned repository contains the main simulation, coupling, Sinkhorn, metric, and Semrau EMD workflows.
- Core algorithmic pieces map clearly to paper equations and claims.
- Precomputed outputs and visualization folders are present in the repository.
- Semrau data paths and CARDAMOM-derived parameter files are included in the public workflow.

Limitations:

- The code is research-script oriented, with hardcoded parameters, relative paths, and figure-specific scripts rather than a package or CLI.
- Exact figure regeneration is split across scripts, precomputed matrices, and visualization files.
- The default Semrau optimization script sets `num_iter = 0`, making the optimized interpolation claim only partially verified from public code.
- Fresh reruns may require repairing at least one metric-output script and running computationally heavy reference construction; the paper reports 23 minutes with parallelization and 168 minutes without parallelization for the Semrau $B_{ref}$ construction.
- The OCR source is usable with caveats because the Nature file is an early-access manuscript PDF and math/typography required manual interpretation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
