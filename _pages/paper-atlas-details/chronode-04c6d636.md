---
layout: default
permalink: /paper-atlas/chronode-04c6d636/
title: "chronODE"
nav: false
description: "发育时间序列中的基因表达和染色质开放度常只有少数时间点。样条或高阶多项式可以把点连成曲线，但系数通常不对应明确的生物过程。chronODE 用广义 logistic 常微分方程描述“早期协同加速、后期逐渐饱和”的信号，把每个动态基因或 cCRE 压缩成两个主要量：变化速率 k 和饱和水平 b。随后它根据拐点相对实验窗口的位置，将单调信号分为 accelerator、switcher、decelerator；"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>chronODE</h1>
    <p>The chronODE framework for modelling multi-omic time series with ordinary differential equations and machine learning</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-61921-9" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for chronODE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/gersteinlab/chronODE" target="_blank" rel="noopener noreferrer" aria-label="Open code for chronODE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## chronODE 方法解释：用两个动力学参数读懂多组学时间序列

### 方法要解决什么

发育时间序列中的基因表达和染色质开放度常只有少数时间点。样条或高阶多项式可以把点连成曲线，但系数通常不对应明确的生物过程。chronODE 用广义 logistic 常微分方程描述“早期协同加速、后期逐渐饱和”的信号，把每个动态基因或 cCRE 压缩成两个主要量：变化速率 $k$ 和饱和水平 $b$。随后它根据拐点相对实验窗口的位置，将单调信号分为 accelerator、switcher、decelerator；对峰形信号使用两段 logistic；最后用双向 RNN 从 cCRE 的染色质时间序列预测目标基因表达。

它不是推断单细胞谱系或细胞间速度，而是对**已有真实采样时间**的基因/调控元件信号做动力学参数化与跨模态序列预测。

### 1. 核心 ODE：协同增长与容量限制同时存在

论文从三参数广义 logistic ODE 出发：

$$
\frac{dz}{dt}=k(z-a)\left(1-\frac{z-a}{b-a}\right).
$$

$z(t)$ 是表达或染色质信号，$a$、$b$ 是下、上渐近线，$k$ 控制变化速度和方向。对激活曲线 $k>0$，对抑制曲线 $k<0$。当信号远离饱和点时，$(z-a)$ 带来类似协同的加速；接近 $b$ 时，容量项 $1-(z-a)/(b-a)$ 把变化压慢。

直接从八个时间点同时拟合 $k,a,b$ 很不稳定。chronODE 先平移并逐行 min–max 归一化，把下渐近线固定为 0：

$$
\frac{dy^*}{dt}=k^*y^*\left(1-\frac{y^*}{b^*}\right),
$$

只拟合 $k^*$ 和 $b^*$。解析解是

$$
y^*(t)=\frac{b^*C^*e^{k^*t}}{b^*+C^*e^{k^*t}},
$$

其中 $C^*$ 由首个时间点决定。补充注释的 Proposition 6–9 证明：平移和线性 min–max 变换不改变 $k$，故归一化空间的 $k^*$ 可以作为原始尺度上的速率参数；$a,b$ 则需要逆变换恢复。

这里的“生物可解释”仍是模型解释：$k$ 与 $b$ 描述符合 logistic 假设的有效速率和有效饱和值，并非直接测得的单分子结合常数或绝对物理容量。

### 2. 为什么每条曲线要拟合两个归一化区间

`min_max.norm.R` 把每行信号分别映射到 $[10^{-5},1]$ 和 $[1,2]$。两个区间让有限观察窗口能对应 logistic 的不同片段：近零区间更容易表示拐点前的加速段，$[1,2]$ 更容易覆盖拐点后、接近饱和的减速段。下界使用 $10^{-5}$ 而非精确 0，是为了避免后面计算 $\log(y^*)$ 时发散。

对每个区间，`ODE_fitting.py` 又分别从正、负 $k$ 初值拟合，并在两者中选 MSE 更低者；随后 `kinetic.classification.R` 再在两个归一化区间中选 MSE 更低的结果。因此一个信号最多比较四条候选：

- $[10^{-5},1]$、$k>0$；
- $[10^{-5},1]$、$k<0$；
- $[1,2]$、$k>0$；
- $[1,2]$、$k<0$。

一个数值例子：若归一化序列从 0.1 上升到 0.9，拟合得到 $k=0.8,b^*=1.05$，它表示在当前时间单位下较快上升且接近饱和；若另一条曲线同样上升，却得到 $k=0.15,b^*=3$，则观察窗口只覆盖缓慢的早段，模型预测的饱和水平远高于已观测值。两者可以有相似起止差值，却属于不同动力学阶段。

源码的拟合内核用 `odeint` 生成数值解供 `scipy.optimize.curve_fit` 优化，`maxfev=5000`；拟合后再用解析式重建曲线并计算 MSE，只接受 $b^*>0$。$C^*$ 的计算给首值加 $10^{-6}$，也是数值保护。Nextflow 把输入按行分块并行运行两套归一化/拟合/恢复流程，最后合并 `parameters`、`fitted.values`、`derivatives` 和 `restored.values` 四类结果。

### 3. 怎样从标准化曲线回到原始信号

若原始范围为 $[z_{\min},z_{\max}]$、归一化范围为 $[R_{\min},R_{\max}]$，逆变换为

$$
q=\frac{(q^*-R_{\min})(z_{\max}-z_{\min})}
{R_{\max}-R_{\min}}+z_{\min}.
$$

代码用 $q^*=0$ 恢复 $a$，用 $q^*=b^*$ 恢复 $b$；$k$ 不变。再结合原始首值 $z_{start}$ 重新计算积分常数，得到原始尺度的拟合曲线。

一个实现边界是 `kinetic.classification.R` 用 `seq(t_start,t_end,length.out=tp_len)` 生成恢复曲线的输出时间，而不是复用不规则的原始时间点。论文的鼠脑例中 E10.5–E16.5 后跳到 PN=21，属于不等间隔采样；因此 `restored.values.tsv` 的列名沿用原时间点，但内部恢复值实际上落在等距网格上。这不影响 `ODE_fitting.py` 用真实 `timesfile` 拟合参数，却会影响把恢复输出逐列当成原采样时刻的严格解释，应视为明确实现偏差。

### 4. Accelerator、Switcher、Decelerator 的含义

拐点满足二阶导为 0，此时 $y^*=b^*/2$，变化速率绝对值最大：

$$
t_{switch}=\frac{\log(b^*/C^*)}{k^*}.
$$

分类只比较这个理论拐点与观测窗口：

| 类型 | 条件 | 看到的是 logistic 哪一段 |
|---|---|---|
| Accelerator | $t_{switch}>t_{end}$ | 尚未到最大速率，仍在加速 |
| Switcher | $t_{start}\le t_{switch}\le t_{end}$ | 窗口内跨过拐点 |
| Decelerator | $t_{switch}<t_{start}$ | 开始观察时已越过拐点并减速 |

同一分类同时适用于上升和下降信号，方向由 $k$ 正负区分。代码还计算达到 $0.99b^*$ 的 saturation time，以及接近 $10^{-16}b^*$ 的 minimum time。这些时间可以远超实验窗口，是模型外推量，不等同于实际观察到的饱和或关闭时间。

图 1解释 logistic 的物理直觉；图 2和补充图 5展示三类动力学。论文在三个脑区发现 switcher 最多，同时 $|k|$–$b$ 呈 L 形：高速度和高饱和水平很少同时出现（$r=-0.44$）。这是该数据与建模流程中的经验规律，不能仅由 logistic 方程本身推出为所有系统的普适定律。

### 5. 质量门控与峰形 piecewise 拟合

论文把单调拟合的 MSE 分布用两组分 Gaussian mixture 分成 acceptable 与 unacceptable。鼠脑三个区域的阈值分别约 0.053、0.050、0.065。平均约 87% 的差异基因通过单调拟合；约 8% 的峰形信号再由 piecewise 拟合捕获，约 5% 仍不适配。

但 GMM 拟合和阈值生成代码**不在仓库中**。Nextflow 主线输出所有拟合及 MSE，不自动过滤 acceptable/unacceptable，也不把失败曲线自动送入 piecewise 脚本。用户需要在外部复现论文的门控。

论文的 piecewise 方法在极值左右各拟合一段 logistic，要求 $b_{left},b_{right}>0$ 且 $k$ 符号相反；还描述用二次 B-spline 检查/保证一阶连续性，并以

$$
k_{avg}=\frac{|k_{left}|+|k_{right}|}{2}
$$

汇总速率。`piecewise.fitting.py` 确实检测极值、分段、调用 `odeint`、拼接并以符号条件筛选，但它是带硬编码 `File_Name` 与鼠脑时间点的笔记本导出脚本；本地源码中找不到论文所述 B-spline 连续性步骤和明确的 $k_{avg}$ 输出。因此 piecewise 核心是 Partial，而非端到端 Exact。

### 6. 从 cCRE 时间序列预测基因表达的 biRNN

对每个基因，论文按线性基因组距离取最近 60 个 cCRE，把八个时间点的染色质信号组成序列。代码先形成 `(gene, 60, 8)`，训练前转置为 `(batch, 8, 60)`，网络为：

$$
\text{biRNN}(60\to30\times2)
\to\text{Linear}(60\to10)
\to\mathrm{ReLU}
\to\text{Linear}(10\to1)
\to\mathrm{ReLU}.
$$

双向 RNN 让每个时间点同时利用早、晚两侧上下文；最终 ReLU 约束预测非负。每个样本的八时点 MSE先取平均，再对 batch 求均值反向传播。数据按基因 80/20 随机划分，batch size 4，Adam，200 epochs。

模型按四类机制分别训练：enhancer/silencer × mono-pattern/poly-pattern。enhancer 与 silencer 依据 cCRE 信号与表达的正负相关划分；mono 表示关联 cCRE 的调控方向一致，poly 表示同时包含不同方向。图 4讨论这类调控结构，图 5展示网络、预测和 SHAP；补充图 8比较四组性能和线性基线。

代码中有一个必须澄清的学习率细节：`initial_lr=1e-4`，`LambdaLR` 的因子在前 1000 个 optimizer step 从接近 0 增到 1，之后保持 1；变量 `desired_lr=1e-6` 从未被调度器引用。因此实现是“warm up 到 $10^{-4}$ 后保持”，不是“从 $10^{-4}$ 衰减到 $10^{-6}$”。

`chronODE_biRNN_model.py` 仍含 `****.tsv` 占位文件名，`data_oc_rna` 的实际筛选语句被注释，且环境文件缺少 PyTorch、scikit-learn、matplotlib。四个 `.pth` 权重存在，但缺少与其严格配套的输入列清单、预处理对象和推理 CLI，所以不能把 README 中的 `python script` 理解为无需编辑即可端到端复现。

### 7. 论文的多组学分析怎样串起来

论文完整流程还包含仓库外步骤：Limma 批次校正、把信号整体平移为正数、maSigPro 时序差异分析、ENCODE cCRE 集合、BEDTools nearest-gene 配对、GMM 门控、GO/回归统计与 SHAP 解释。单细胞 41 个脑细胞类型的处理脚本也未提供。

因此可运行边界是：

- **较完整**：已准备好正值矩阵和真实时间列表后，Nextflow 单调 ODE 拟合、参数恢复、动力学分类；
- **需手工编辑**：piecewise 和 biRNN 研究脚本；
- **Not found**：从原始 ENCODE/单细胞数据到论文分析集、GMM、B-spline、cCRE 配对、SHAP/GO 和所有论文图的统一复现工作流。

近邻 cCRE 配对只按线性距离，是一种代理而非调控因果证据；远距离增强子、三维染色质接触和细胞类型特异配对均可能被错配。biRNN 的相关性说明这些输入具有预测信息，不证明每个近邻 cCRE 都直接调控该基因。

### 8. 怎样读主要结果图

- 图 1：先理解三参数 ODE、归一化成两参数以及激活/抑制曲线。
- 图 2：看 $k$–$b$ L 形、三类时间位置及跨脑区差异；不要把 quadrant 与 kinetic class 混为同一个分类。
- 图 3：把动力学应用到 41 个单细胞脑类型，显示晚出现细胞的参数空间更受限、必需基因变化更快。
- 图 4：从单个 cCRE 的动力学扩展到 enhancer/silencer 与 mono/poly 调控结构。
- 图 5：biRNN 的预测性能及 SHAP 分析；SHAP 是对模型预测的特征归因，不是实验因果强度。
- 补充图 2提供参数变换证据；补充图 3是 GMM 与拟合覆盖率；补充图 4验证 piecewise；补充图 5给出三类定义；补充图 8给出四组网络性能。

### 9. 论文—代码直接对应

| 机制 | 本地代码 | 判断 |
|---|---|---|
| 两区间逐行归一化 | `scripts/bin/min_max.norm.R:40-78` | **Exact**，但常数行会除以零且无显式保护 |
| logistic ODE、正负 $k$、解析重建与 MSE | `scripts/bin/ODE_fitting.py:19-145` | **Exact** |
| 双区间择优、逆变换与动力学分类 | `kinetic.classification.R:153-342` | **Exact / caveat**：恢复曲线改用等距时间网格 |
| Nextflow 分块和合并 | `scripts/chronode.nf:39-90` | **Exact** |
| GMM acceptable/unacceptable 门控 | 本地仓库 | **Not found** |
| piecewise 双 logistic | `scripts/piecewise.fitting.py` | **Partial**：硬编码且缺 B-spline/$k_{avg}$ 论文步骤 |
| biRNN 架构与训练 | `scripts/chronODE_biRNN_model.py:110-352` | **Partial / Notebook**：核心网络存在，输入选择和依赖未封装 |
| 四个预训练模型 | `models/biRNN/*.pth` | **Artifact only**：存在权重，但缺可直接复用的完整推理合同 |
| Limma、maSigPro、BEDTools、SHAP、GO 与单细胞全流程 | 本地仓库 | **Not found** |

本地快照与 `https://github.com/gersteinlab/chronODE` 的远端 HEAD 逐文件比较一致，对应提交 `203e17b7c17fad28149a20b18fba5e4253597175`（2025-08-14）。论文还给出 Zenodo 软件归档 DOI `10.5281/zenodo.15574976`；本轮以工作区内、与远端 HEAD 一致的固定源码作为代码证据。

CodeGraph 成功定位了 `ODE_fitting.py` 与 piecewise 的核心 ODE 函数；其余 Nextflow、R 和笔记本式脚本由直接逐行读取核验。最终结论同时使用主论文、补充 Markdown/Proposition 与源码，没有用代码导航替代原始证据。

### 10. 使用时最容易忽略的边界

1. ODE 只用两个自由动力学参数，但八个时间点仍可能不足以约束远离观察窗的 $b$、$t_{switch}$ 和饱和时间。
2. $k$ 的单位依赖输入时间单位；跨数据集比较前必须统一时间尺度和预处理。
3. MSE 是归一化空间的误差，跨信号可比性来自相同归一化流程；改变流程会改变 GMM 阈值。
4. 单调/峰形以外的多峰、振荡和高噪声轨迹被排除，不能强迫解释为三类动力学。
5. 常数序列会在 min–max 分母为零时产生非有限值，主脚本没有显式常数行检查。
6. 双向 RNN 利用了完整未来序列，适合重建/解释整段时间过程，不是只看历史预测未知未来的因果 forecasting 模型。

### 推荐阅读顺序

先读图 1、补充图 2和补充 Note 的 Proposition 1/5/7/8，抓住参数意义；再沿 `min_max.norm.R` → `ODE_fitting.py` → `kinetic.classification.R` → `chronode.nf` 跟完可运行主线；随后用补充图 3–5理解 GMM、piecewise 与动力学分类；最后再读图 4–5和 biRNN 脚本，并把预测性关联与调控因果分开。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## chronODE: Modeling Multi-Omic Time Series with ODEs and Machine Learning

**Paper**: Borsari, Frank et al., "The chronODE framework for modelling multi-omic time series with ordinary differential equations and machine learning," *Nature Communications* (2025)
**DOI**: [10.1038/s41467-025-61921-9](https://doi.org/10.1038/s41467-025-61921-9)
**Code**: [https://github.com/gersteinlab/chronODE](https://github.com/gersteinlab/chronODE)
**Affiliation**: Gerstein Lab, Yale University

---

### Motivation & Novelty

#### Biological Problem
During organismal development, gene activation and repression must occur with precise timing — aberrant temporal regulation drives diseases from cancer to neurodegeneration. Time-series functional genomic studies (RNA-seq, ATAC-seq) capture these dynamics, but extracting *quantitative kinetic parameters* from inherently noisy, sparse-timepoint data remains challenging. Existing curve-fitting approaches (B-splines, polynomials) lack biological interpretability — each gene gets a unique set of basis functions with no direct connection to the cooperative binding and saturation phenomena that govern transcriptional and epigenetic regulation.

#### Limitations of Existing Approaches
- **B-spline / polynomial methods** (Déjean et al., *EURASIP J. Bioinform. Syst. Biol.*, 2007; Chiu et al., *BMC Bioinform.*, 2015): Fit arbitrary smooth curves but yield opaque coefficients without biological meaning
- **RNA velocity methods** (La Manno et al., *Nature*, 2018; Bergen et al., *Nature Biotechnol.*, 2020): Model splicing dynamics but not chromatin kinetics or multi-omic integration
- **Genome-wide prediction approaches** (Zhou et al., *Nature Commun.*, 2017): Cross-cell-type prediction of chromatin from expression, but not temporal prediction with cCRE-level resolution
- **Single-cell multi-ome regression** (Mitra et al., *Nature Genet.*, 2024): Models enhancer-like regulatory effects but does not account for silencer regulation or temporal kinetics

#### Unique Contributions
1. **Biologically interpretable kinetic parameters**: Two parameters ($k^*$, $b^*$) with direct biophysical meaning — rate of change and saturation level — capturing cooperativity and saturation in genomic signals
2. **Three-class kinetic taxonomy**: Genes classified as accelerators, switchers, or decelerators based on when $t_{\text{switch}}$ occurs relative to the observation window
3. **L-shaped constraint discovery**: Genes cannot simultaneously have high rate ($k$) and high saturation ($b$), revealing fundamental biochemical limitations
4. **Multi-omic temporal prediction**: biRNN architecture predicting gene expression from cCRE chromatin signals across time, incorporating both enhancer and silencer regulation
5. **Mono-/poly-pattern gene classification**: Genes regulated by diverse cCRE types (poly-pattern) show larger expression changes and enrichment in brain-specific functions

---

### Method Overview

#### Algorithmic Framework
chronODE is a three-step computational framework:

1. **Data Preprocessing**: Batch correction (Limma), shift to positive range, time-series differential analysis (maSigPro)
2. **Kinetic Analysis**:
   - **Monotonic fitting**: Fit generalized logistic ODE ($\frac{dz}{dt} = k(z-a)(1-\frac{z-a}{b-a})$) via simplified two-parameter form on min-max normalized data
   - **Quality control**: GMM-based MSE filtering to identify acceptable vs. unacceptable fits
   - **Piecewise fitting**: For peak-like profiles, split signal at extremum and fit two logistic segments
   - **Kinetic classification**: Classify genes as accelerators ($t_{\text{switch}} > t_{\text{end}}$), switchers ($t_{\text{start}} \le t_{\text{switch}} \le t_{\text{end}}$), or decelerators ($t_{\text{switch}} < t_{\text{start}}$)
3. **Temporal Prediction**: biRNN model predicting gene expression from 60 nearest cCRE chromatin signals, trained separately for 4 regulatory mechanisms (enhancer/silencer × mono-/poly-pattern)

#### Key Technical Components
- **Dual-range normalization**: Each gene/cCRE normalized to both $[10^{-5}, 1]$ and $[1, 2]$ ranges; best fit selected by lowest MSE
- **Analytical solution**: $y^*(t) = \frac{b^*C^*e^{k^*t}}{b^* + C^*e^{k^*t}}$ used for curve reconstruction
- **Parameter invariance**: $k$ is preserved under both translation and min-max normalization (Propositions 7–8)
- **Nextflow pipeline**: Parallelized genome-wide ODE fitting with chunked processing

#### Biological Assumptions
- Genomic signals (gene expression, chromatin accessibility) follow cooperative then saturating dynamics, well-modeled by the logistic function
- The majority of gene expression changes are monotonic (verified: ~87% in mouse brain)
- cCRE-gene pairing based on linear proximity (nearest gene) is a reasonable first approximation

---

### Evaluation

#### Datasets
| Dataset | Source | Details |
|---------|--------|---------|
| Bulk RNA-seq | ENCODE (He et al., *Nature*, 2020) | 3 brain regions × 8 timepoints (E10.5–PN), polyA+ |
| Bulk DNase/ATAC-seq | ENCODE (Gorkin et al., *Nature*, 2020) | 3 brain regions, 405,554 active cCREs |
| scRNA-seq | Qiu et al., *Nature*, 2024 | 41 brain cell types, E8.5–E14.25 |
| ENCODE4 cCREs | Moore et al., *bioRxiv*, 2024 | 926,843 mouse cCREs |
| Essential genes | Funk et al., *Cell*, 2022 | Human essential gene catalog |

#### Metrics & Results

| Metric | Value | Context |
|--------|-------|---------|
| Monotonic fit rate | ~87% of DE genes | Acceptable MSE by 2-component GMM |
| Piecewise fit rate | ~8% additional genes | Peak-like profiles captured |
| Remaining unfitted | ~5% | Complex/variable patterns |
| L-shaped $k$–$b$ correlation | Pearson $r = -0.44$ ($p < 2.2 \times 10^{-16}$) | Fundamental constraint: high rate + high saturation excluded |
| Kinetic class distribution | Switchers ~60–75%, Decelerators ~12–32%, Accelerators ~2–17% | Varies by brain region and cell type |
| Essential gene $k$ | Significantly higher ($p = 4.2 \times 10^{-203}$, Wilcoxon) | n = 54,212 genes across 41 cell types |

**biRNN prediction performance (test set)**:

| Regulatory Mechanism | Cross-Gene $r$ | Cross-Timepoint $r$ (mean) |
|---------------------|----------------|---------------------------|
| Enhancer mono-pattern | 0.927 | 0.90 |
| Silencer mono-pattern | 0.969 | 0.86 |
| Enhancer poly-pattern | 0.867 | 0.68 |
| Silencer poly-pattern | 0.891 | 0.57 |

All cross-gene $r > 0.85$ and cross-timepoint correlations exceed equivalent cross-cell-type correlations reported by Zhou et al. (*Nat. Commun.*, 2017).

#### Biological Validation
- Q3 repressed genes enriched for nucleotide biosynthesis (expected: downregulated during lineage commitment)
- Q3 activated genes enriched for oxidative phosphorylation (expected: upregulated post-natally)
- Essential genes ramp up faster (higher $k$) and closer to saturation in early cell types
- Poly-pattern genes enriched for neurogenesis, trans-synaptic signaling (brain-specific functions)
- Proximal cCREs contribute most at initial/final timepoints; distal cCREs at intermediate timepoints (SHAP analysis)

---

### Reproducibility

#### Rating: 3/5

#### Strengths
- All data publicly available from ENCODE portal with specific accession numbers
- Complete Nextflow pipeline for monotonic ODE fitting with example data and quick-test (~5 min)
- Pre-trained biRNN models (`.pth` files) for all 4 regulatory mechanisms
- Conda environment specification (`chronode.yml`) for dependency management
- Mathematical proofs for all 9 propositions in Supplementary Note 1
- Software archived on Zenodo (DOI: [10.5281/zenodo.15574976](https://doi.org/10.5281/zenodo.15574976))

#### Blockers
- **biRNN training script is a Jupyter notebook export** (`.py` with `# In[N]:` markers): Contains hardcoded placeholder filenames (`'****.tsv'`, `'****.csv'`), making end-to-end training impossible without manual editing
- **Piecewise fitting script similarly notebook-derived**: Hardcoded filename `'File_Name'`, hardcoded mouse-specific timepoints `[10.5, 11.5, ..., 21]`
- **No end-to-end pipeline**: Data preprocessing (Limma batch correction, maSigPro differential analysis) and cCRE-gene linking (BEDTools closest) are not included in the repository
- **GMM filtering step** (critical for separating acceptable vs. unacceptable fits) is not coded — only the GMM cutoff values appear in Supplementary Figure 3D legend
- **Single-cell analysis scripts** not included — all 41 cell-type kinetic analyses are not reproducible
- **Missing dependencies**: `chronode.yml` omits PyTorch and scikit-learn, both required by biRNN script
- **SHAP analysis, GO enrichment, logistic regression** (Figs. 4D, 5D, Suppl. Fig. 7B–C) — none of these downstream analysis scripts are provided

#### Limitations Noted by Authors
- Logistic ODE limited to monotonic signals; peak-like fitting is a simplified piecewise approach
- The proximity-based cCRE-gene linking is approximate; more sophisticated methods (e.g., ENCODE enhancer-gene maps) could be substituted
- Only applied to mouse brain development; generalizability to other systems untested
- Fitting 2 parameters from 8 timepoints is near minimum; regularization suggested for more complex ODE forms

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
