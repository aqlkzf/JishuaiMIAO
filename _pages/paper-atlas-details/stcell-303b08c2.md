---
layout: default
permalink: /paper-atlas/stcell-303b08c2/
title: "STCell"
nav: false
wide: true
description: "海马 CA3 中的位置细胞在动物到达特定地点时放电，时间细胞则在两个事件之间依次激活。传统理论常把它们分开：位置细胞来自连续吸引子网络，时间细胞来自不同时间常数的单神经元积分器。STCell 提出另一种解释：两者可以是同一 recurrent network 在不同输入相关结构下形成的两种动力学状态。 这里的“STCell”不是单细胞转录组方法，也不涉及空间组学；它是计算神经科学模型。"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>STCell</h1>
    <p>When and Where: A Model Hippocampal Network Unifies Formation of Time Cells and Place Cells</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.03.22.713480" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for STCell">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/qrsyu/STCell" target="_blank" rel="noopener noreferrer" aria-label="Open code for STCell">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STCell：同一个预测性海马网络为何会形成位置细胞或时间细胞

### 1. 论文要统一的两个现象

海马 CA3 中的位置细胞在动物到达特定地点时放电，时间细胞则在两个事件之间依次激活。传统理论常把它们分开：位置细胞来自连续吸引子网络，时间细胞来自不同时间常数的单神经元积分器。STCell 提出另一种解释：两者可以是同一 recurrent network 在不同输入相关结构下形成的两种动力学状态。

这里的“STCell”不是单细胞转录组方法，也不涉及空间组学；它是计算神经科学模型。输入是模拟的 sensory experience vectors，输出是对被遮挡经验的重建。隐藏层活动被解释为 CA3 神经元，再用时间场宽度和空间信息量判断是否呈现 time-cell 或 place-cell 表型。

核心假设是 CA3 进行 pattern completion：观察到部分、带噪的经验后，网络利用记忆和 recurrent dynamics 补全未见部分。如果经验中的主要相关性来自空间，隐藏单元形成稳定位置场；如果相关性来自两个相隔事件，隐藏单元形成按时间展开的序列。

### 2. 两类感觉经验如何生成

#### 2.1 空间输入

每个感觉通道先在二维场地上生成白噪声，再用标准差约 15 cm 的 Gaussian filter 平滑，形成弱空间调制场 $M_d(x,y)$。动物沿轨迹 $(x_t,y_t)$ 移动时，第 $d$ 个通道输入为

$$
e_{t,d}=M_d(x_t,y_t).
$$

本地 `WeakSMCell` 直接实现该过程：对每个通道采样二维正态噪声并进行 Gaussian filtering。它不是预设 place field；单个输入场通常宽而弱，位置选择性需要网络综合许多通道后产生。

圆环任务使用模拟的带噪角速度和半径变化产生轨迹；方形场任务使用自由探索。代码还包含不同 arena 形状和头方向调制组件，但论文主论证依赖弱空间场与时间事件，不应把仓库里所有 sensory 类都算作论文模型的必要组件。

#### 2.2 时间输入

时间任务中动物不移动，两个事件分别约在 2.5 s 与 17.5 s 出现。各通道的事件时刻带轻微 jitter，并以标准差约 200 ms 的 Gaussian pulse 平滑。网络在早期看到部分事件 1，随后输入完全遮挡，必须靠 recurrent state 在约 15 s 后重建事件 2。

这些时间通道并不是“时间细胞标签”。它们只是具有跨长延迟相关性的感觉信号；time-cell-like sequence 是隐藏层为完成预测任务而形成的内部表示。

### 3. CA3 被建模为怎样的 CTRNN

网络包含输入投影、512 个 recurrent units 和线性输出层。连续时间动力学经 Euler 离散后可写为

$$
\mathbf v_{t+1}=(1-\alpha)\mathbf v_t+
\alpha\left(
W^{\mathrm{rc}}\mathbf r_t+W^{\mathrm{in}}\tilde{\mathbf e}_t+
\mathbf b+\boldsymbol\epsilon_t
\right),
$$

$$
\mathbf r_t=\operatorname{ReLU}(\mathbf v_t),
\qquad
\hat{\mathbf e}_t=W^{\mathrm{out}}\mathbf r_t.
$$

$\tilde{\mathbf e}_t$ 是被遮挡、加噪后的输入，$\hat{\mathbf e}_t$ 要重建原始经验。旧文档记录代码使用 `nn4n.nn.LeakyLinearLayer`、隐藏维数 512、`alpha=0.01`，时间分辨率 100 ms；如果按 $\alpha=\Delta t/\tau$ 解读，相当于约 10 s 的长网络时间常数。

`nn4n` 是外部依赖，不随仓库提供，也没有 requirements 文件。训练逻辑主要位于 notebook，而非统一 CLI；运行目录依赖 `sys.path.append('..')`。因此代码是研究复现快照，不是可直接安装的一键包。

### 4. 遮挡任务为何会塑造 recurrent dynamics

训练目标是从 masked input 重建完整经验：

$$
\mathcal L_{\rm rec}=
\frac{1}{BTD}\sum_{b,t,d}
(\hat e_{btd}-e_{btd})^2.
$$

输入先接受模糊随机 mask，再在指定时间段硬置零。空间任务要求网络在感觉缺失时延续地点相关轨迹；时间任务要求网络跨越事件之间的 void interval；混合任务同时包含二者。遮挡不是普通数据增强，而是创建了预测压力：网络如果不在 recurrent state 中保存经验的空间/时间结构，就无法恢复后续输入。

另有 firing-rate regularization 抑制隐藏层过度活动。论文公式把归一化平方和写成含 $(BT)^2$ 的形式；`func.py:103-106` 实际只除一次 $BT$：

$$
L_{\rm fr}^{\rm code}=
\frac1N\sum_n
\frac{\left(\sum_{b,t}r_{btn}\right)^2}{BT}.
$$

若 batch/time product 为 6400，代码项比按论文公式直接计算大 6400 倍。`lambda_fr=10^{-4}` 的实际效果因此远强于公式表面暗示。这是 paper–code 的实质差异，不能只称作记号变化。

### 5. 如何定义 time cell 和 place cell

#### 5.1 时间细胞

对隐藏单元活动先去掉低平均 firing units，再对每个单元做 0–1 normalization，并按 peak time 排序。时间场宽度定义为归一化 firing rate 超过 0.5 的持续时间。论文用 peak time 与 field width 的 Pearson correlation 检查后出现的时间场是否更宽。

这个指标描述群体序列的尺度扩展，不等于每个达到阈值的单元都经过独立显著性检验。排序热图也会强化序列视觉感，因此相关系数与重建任务结果要一起阅读。

#### 5.2 位置细胞

空间信息量为

$$
I=\sum_m p_m\frac{r_m}{\bar r}
\log_2\frac{r_m}{\bar r},
$$

其中 $p_m$ 是 occupancy，$r_m$ 是位置 bin 的平均 firing rate。论文将 $I>8$ 的单元定义为 place cell；`func.py:SIC_analysis()` 默认 `threshold=3`。若 notebook 没有显式覆盖默认值，代码会比论文阈值识别更多 place cells。place-cell 比例的精确复现必须报告实际调用参数，而不能只引用函数默认或论文阈值中的一个。

圆环场使用 18 个角度 bin。occupancy 和 rate map 都来自模拟轨迹，因此 place selectivity 反映模型在特定运动采样分布下的空间编码，而非真实神经记录。

### 6. 从纯时间/空间到连续转变

#### 时间任务

图 2A 中，网络早期接收事件 1，之后在无输入区间内部产生连续隐藏序列，并在事件 2 前重建输出。论文报告 peak time 与 field width 的强正相关；同时也指出靠近第二事件的部分单元出现更窄场这一异常。这说明模型大体复现时间场展宽，并非完美遵从单调尺度理论。

#### 空间任务

图 2B 中，网络在方形场重建弱空间输入，隐藏单元形成局部二维 firing fields。它支持同一 CTRNN architecture 能产生 place-like activity，但任务、数据和训练实例与时间实验不同；不是同一组固定权重同时在两个任务中无训练切换地表现两类细胞。

#### 时空圆环任务

网络第一圈看到部分空间信号，第二圈信号被遮挡，必须沿 recurrent trajectory 预测。逐渐缩短可见空间窗口时，网络可由 anchored place representation 向靠内部动力推进的 time-like sequence 变化。混合时间与空间通道的实验也显示 place/time 指标连续变化。

因此论文支持的是“输入统计与预测要求可连续调节网络表示”，而不是证明生物 CA3 中每个位置细胞会真实变成时间细胞。

### 7. recurrent weights 的机制解释

理论部分分析 $W^{\mathrm{rc}}$、eigen spectrum、SVD 与隐藏轨迹。

- 空间任务需要在感觉输入存在或短暂缺失时保持接近某个地点相关状态，因此 recurrent flow 更接近局部稳定/吸引子样动力学。
- 时间任务在长时间完全无输入时必须持续前进，recurrent weights 形成沿隐藏流形推进的链式或非正规动力学。
- 当空间通道减少、时间间隔变宽或两类通道混合时，连接结构与 hidden trajectory 逐渐过渡。

图 6 还比较遮挡期间隐藏轨迹与完整感觉轨迹的高维距离：遮挡越早、持续越久，误差积累越大；输入恢复时距离下降。这是 predictive reconstruction 的诊断，不是对真实 CA3 recurrent connectivity 的拟合。

### 8. 六张图的论证角色

1. **图 1**：定义空间场、时间事件和 CTRNN 架构。
2. **图 2**：分别证明时间输入产生 time-like sequence、空间输入产生 place-like fields。
3. **图 3**：在圆环/混合任务中同时观察空间与时间表示，并量化两类单元。
4. **图 4**：改变可用空间证据或时间结构，展示表型比例连续变化。
5. **图 5**：分析混合通道和表示 transition，支持“连续谱”而非二分机制。
6. **图 6**：从 recurrent matrix、谱结构和 trajectory reconstruction distance 提供机制解释。

论文没有独立 supplementary Markdown；转换后的 `paper.md` 包含正文与图注，图像目录保存大量拆分 panel。仓库同时含许多已生成 PNG 与 notebook 输出，可以核对作者运行结果，但没有预训练权重让读者验证所有图是否来自同一随机种子。

### 9. 论文—代码对应

| 论文组件 | 本地实现 | 判断 |
|---|---|---|
| 弱空间调制输入 | `rtgym/.../weak_sm_cell.py` | **Direct**：随机场与 Gaussian smoothing 可见 |
| 时间事件输入 | `rtgym/agent/sensory/movement_modulated/` 与 time notebooks | **Partial**：生成逻辑存在，实验由 notebook 组织 |
| CTRNN | 外部 `nn4n` + 各实验 notebook | **Partial**：配置/权重访问可见，核心 layer 不在仓库 |
| masked reconstruction | notebooks + `rtgym/utils/masking.py` | **Direct/Partial**：两阶段 mask 存在，各任务参数不同 |
| reconstruction + firing loss | `func.py:86-108` | **Partial**：$L_{fr}$ normalization 与论文公式不一致 |
| time-cell sorting/correlation | `func.py:111-181` | **Direct** |
| place-cell SIC | `func.py:184-240` | **Partial**：公式一致，默认 threshold 3 vs paper 8 |
| representation transitions | `repre_transit_exp/` | **Notebook/script evidence**：实验脚本和图存在 |
| recurrent spectral analysis | `theory_exp/*.ipynb` | **Notebook evidence** |
| 全部预训练模型/统一复现入口 | 当前仓库未提供 | **Not found** |

### 10. 复现边界与常见误读

- **外部依赖边界**：`nn4n` 未 vendored，也无锁定版本/requirements。
- **notebook 边界**：主要训练流程分散在实验 notebook，执行顺序和相对路径重要。
- **随机性边界**：感觉场、轨迹、mask、初始化和训练均随机；没有完整预训练权重或种子清单。
- **指标边界**：SIC 默认阈值与论文不同，place-cell counts 可能显著变化。
- **损失边界**：firing regularizer normalization 不同，不能按论文公式直接推算实际权重。
- **warmup 边界**：论文描述前 3 s 部分可见，而部分代码路径使用 `t_warmup=10` 个 100 ms step，即 1 s；不同实验脚本需分别核对。
- **生物学边界**：模型证明一个 computational sufficiency result——单一预测 RNN 足以产生两类表型；它不证明真实海马只使用这一机制。
- **“统一”边界**：共享 architecture 与学习原则，不等于每张图使用完全相同的训练后网络。

STCell 最简洁的理解是：位置细胞和时间细胞都可以被看成“对缺失经验进行预测”的内部基函数。外部输入如果持续把状态锚定到地点，网络形成 place-like attractor；输入如果只在相隔事件处提供锚点，recurrent dynamics 必须在中间自行推进，形成 time-like sequence。论文的价值在于给出这一统一的充分性模型，而其生物真实性仍需要与真实 CA3 神经活动和连接数据进一步检验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## STCell: A Unified Hippocampal Model for Place and Time Cells

**Paper**: "When and Where: A Model Hippocampal Network Unifies Formation of Time Cells and Place Cells"
**Authors**: Qiaorong S. Yu, Zhaoze Wang, Vijay Balasubramanian
**Venue**: bioRxiv, March 2026 | DOI: 10.64898/2026.03.22.713480
**Code**: https://github.com/qrsyu/STCell

---

### Motivation & Novelty

#### The Biological Problem

Two types of neurons have been discovered in hippocampal area CA3:
- **Place cells**: fire selectively when an animal occupies a particular spatial location (O'Keefe & Dostrovsky, *Brain Research*, 1971; O'Keefe, *Experimental Neurology*, 1976)
- **Time cells**: fire sequentially during delay periods between events, with later-firing neurons having progressively *wider* temporal tuning fields (MacDonald et al., *Neuron*, 2011; Kraus et al., *Neuron*, 2013; Salz et al., *Journal of Neuroscience*, 2016)

Both cell types are found in the same CA3 subfield, yet existing computational models treat them as products of entirely separate mechanisms.

#### Limitations of Prior Approaches

**Continuous Attractor Networks (CANs)** — the dominant model for place cells (Samsonovich & McNaughton, *Journal of Neuroscience*, 1997; Fuhs & Touretzky, *Journal of Neuroscience*, 2006) — use local recurrent excitation to stabilize "activity bumps" at spatial locations. They can explain stable place fields but not sequential temporal dynamics.

**Leaky integrators / inverse Laplace** — the main model for time cells (Shankar & Howard, *Neural Computation*, 2012) — uses multiple single-neuron time constants to produce compressed temporal representations. It ignores the dense recurrent connectivity of CA3 and cannot explain place cells.

**Prior RNN work on place cells** (Wang et al., *NeurIPS 2024*; Benna & Fusi, *PNAS*, 2021) showed that predictive autoencoders of spatially structured input produce place-like representations, but did not address time cells or show the connection between the two.

#### What's New

The key contribution is showing that a **single CTRNN** trained as a **predictive autoencoder** on different input statistics produces either place cells or time cells depending solely on the task:

1. **Unified mechanism**: Both cell types emerge from reconstruction of incomplete sensory trajectories, not from separate mechanistic principles.
2. **Continuous transition**: Gradually changing task statistics (spatial ↔ temporal) smoothly interpolates network representations between place-cell-like and time-cell-like activity.
3. **Asymmetry explained**: Spatial inputs are dense and continuous, temporal inputs are sparse — this asymmetry explains why spatial representations are more robust under mixed inputs.
4. **Mechanistic insight**: Time cells arise from an asymmetric W^rc motif (forward excitation + backward inhibition); place cells from symmetric local excitation. These are empirically validated through eigenvalue and singular value spectrum comparison.

---

### Method Overview

#### Core Algorithmic Framework

A **Continuous Time Recurrent Neural Network (CTRNN)** with N=512 hidden units models CA3. It receives D=100-dimensional **experience vectors** (EVs) — either weakly spatially modulated (WSM) signals or temporally structured event signals — and is trained as a **masked autoencoder**: given partially occluded input, reconstruct the original signal.

The membrane potential dynamics follow:
$$\tau \frac{d\mathbf{v}_t}{dt} = -\mathbf{v}_t + \mathbf{W}^{rc}\mathbf{r}_t + \mathbf{W}^{in}\mathbf{e}_t + \mathbf{b} + \boldsymbol{\eta}^{pre}$$

with τ=10s, discretized via Euler method with α=dt/τ=0.01. Firing rates are ReLU activations with additive Gaussian noise. Training minimizes MSE reconstruction loss plus firing rate regularization (λ_fr=0.0001).

#### Key Technical Components

1. **Experience vector generation**: Spatial EVs are Gaussian-random fields (σ=15cm); temporal EVs are Gaussian-peaked event signals (σ=200ms) at two time points with jittered onsets.

2. **Two-stage masking**: (i) Gaussian-blurred random mask (up to 30%) for general denoising, plus (ii) hard zero-masking of specific intervals (the 2nd lap or the post-event period) to force temporal prediction.

3. **Cell identification**:
   - *Time cells*: sort by peak firing time, compute Pearson r between peak time and field width (positive = temporal broadening)
   - *Place cells*: Spatial Information Content (SIC) > threshold per angular bin of the track

4. **Mechanistic analysis**: After training, sort W^rc by neuron peak firing time and compare eigenvalue/singular value spectra with an idealized "forward excite, backward inhibit" matrix (gain=+0.2, loss=-0.1, window width Δ=150).

#### Biological Assumptions

- CA3 performs pattern completion = masked autoencoding of experience
- Both spatial and temporal sensory channels are modeled as D-dimensional EV streams (unified representation)
- The same recurrent network weights adapt to task statistics (not different sub-populations)

#### Five Experiments

| Experiment | Task | Key Result |
|---|---|---|
| Time task | Stationary agent, predict 2nd event from 1st | Sequential time cells, r=0.89 temporal correlation |
| Space task (square) | Free exploration | Place-like rate maps |
| Space task (circular) | Two-lap clockwise | Spatially selective fields covering full track |
| Spacetime task | 2 laps, 2nd lap masked | Mixed: narrow fields in lap 1, broader (time-cell-like) in lap 2 |
| Mixed input | Vary spatial/temporal channel ratio | Asymmetric transition: spatial dominates with few spatial channels |

---

### Evaluation

#### Datasets

All experiments use **simulated data** generated by the `rtgym` library (included in repository). No biological neural recordings are required.
- Square arena: 100cm × 100cm, free exploration, T=20s, batch_size=64
- Circular track: R_out=17cm, R_in=10cm, two laps, T=10s
- Temporal task: T=20s, events at t=2.5s and 17.5s
- Mixed input: 11 trial configurations from 100% temporal to 100% spatial channels (in steps of 2, 4, 10, 20, 40, 50 spatial channels)

#### Metrics

| Metric | What It Measures | Key Results |
|---|---|---|
| Temporal correlation r | Pearson r(peak_time, field_width) | Time task: r=0.89, widening ratio 0.53 |
| SIC (Spatial Information Content) | Bits/spike spatial selectivity | Place cells: SIC > 3 (code) / >8 (paper) |
| Number of place cells vs. trial | Effect of reducing spatial input | Rapid drop, then plateau around 50 |
| Number of time cells in gap | Effect of widening temporal events | Decreases as gap shrinks |
| Connectivity profile | Median connectivity vs. neuron rank | Time W^rc more similar to idealized than space W^rc |
| Eigenvalue spectrum shape | Circular (time) vs. square (space) | Distinct distributions for time vs. place tasks |
| SVD overlap | First 20 singular values | Idealized time W^rc matches trained time W^rc |
| Trajectory reconstruction distance | ||ŷ − y|| as function of missing segment | Increases with missing duration, recovers when input returns |

#### Biological Validation

All validation is in-silico. The paper makes three testable experimental predictions:
1. Recording CA3 during tasks with varying spatial/temporal cue availability should reveal gradual transitions in cell type
2. The transition should be asymmetric: degrading spatial input induces time cells more readily than adding temporal cues suppresses place cells
3. Different functional connectivity motifs should be measurable via pairwise correlations in large-scale CA3 recordings during temporal vs. spatial tasks

---

### Reproducibility

**Rating: 2/5** — Code is available but has significant barriers to full reproduction.

**Strengths**:
- Full code and experiment scripts are on GitHub (github.com/qrsyu/STCell)
- `rtgym` sensory environment library is self-contained and well-structured
- All hyperparameters are documented in Table 1

**Barriers**:
- **`nn4n` dependency**: The RNN model requires the `nn4n` package, which is not installed in standard Python environments, is not listed in any requirements file, and its source is not bundled with the code. The version used in the paper is unknown.
- **Notebook-centric training**: All training lives in Jupyter notebooks — no standalone training script. This makes systematic parameter sweeps difficult.
- **SIC threshold mismatch**: Paper says >8, code uses >3. Reproduced results may differ in reported place cell counts.
- **No pre-trained weights**: The repository does not include saved model weights. Stochastic initialization and early stopping mean different runs may produce qualitatively different W^rc patterns.
- **No requirements.txt**: Dependencies (`scipy`, `sklearn`, `torch`, `tqdm`, `seaborn`, `nn4n`) must be inferred from import statements.

**To reproduce**:
1. Install PyTorch (GPU recommended), scipy, sklearn, seaborn, tqdm
2. Install `nn4n` from PyPI or GitHub: `pip install nn4n`
3. Navigate to `code/spacetime_exp/` and run `python 2WSMS_mask.py` to generate data
4. Open `spacetime_task.ipynb` and run cells sequentially
5. For mechanistic analysis, run `theory_exp/test_RNN.ipynb` after training

**Common pitfalls**:
- The `rtgym` library uses `sys.path.append('..')` to find `func.py`. Must run notebooks from within their subdirectory.
- `generate_circular_trajectories()` uses rejection sampling (retry if trajectory hits wall) — can be slow for small arenas or high batch sizes.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
