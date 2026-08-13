---
layout: default
permalink: /paper-atlas/dual-memory-pathways-3e33b560/
title: "Dual_memory_pathways"
nav: false
wide: true
description: "脉冲神经网络（SNN）适合事件驱动计算，但普通的 LIF 神经元只把输入保存在会衰减的膜电位中，因此很快忘记较早的证据。加入稠密循环连接可以延长记忆，却带来近似 O(N^2) 的参数和访存开销；可学习的轴突延迟则需要深的时间缓冲区以及每条连接的时序元数据。 这篇论文提出的问题是：能否用一个足够小、稳定、可在芯片上保存的状态来提供长时上下文，同时保留脉冲计算的稀疏性？"
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
      <span>Machine Learning Algorithm</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>Dual_memory_pathways</h1>
    <p>Algorithm-hardware co-design of neuromorphic networks with dual memory pathways</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/sunpengfei1122/Dual_memory_pathways" target="_blank" rel="noopener noreferrer" aria-label="Open code for Dual_memory_pathways">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Dual Memory Pathways（DMP-SNN）方法说明

### 1. 论文要解决什么问题？

脉冲神经网络（SNN）适合事件驱动计算，但普通的 LIF 神经元只把输入保存在会衰减的膜电位中，因此很快忘记较早的证据。加入稠密循环连接可以延长记忆，却带来近似 `O(N^2)` 的参数和访存开销；可学习的轴突延迟则需要深的时间缓冲区以及每条连接的时序元数据。

这篇论文提出的问题是：能否用一个足够小、稳定、可在芯片上保存的状态来提供长时上下文，同时保留脉冲计算的稀疏性？作者把这种算法设计和硬件数据流一起优化，形成 Dual Memory Pathways（DMP-SNN）。

### 2. 核心想法

每一层同时保留两种记忆：

- **快速路径**：当前时刻的脉冲通过 `W_f` 直接驱动神经元；
- **慢速路径**：先把脉冲压缩成一个标量，再更新低维状态 `m[k] in R^d`，最后把状态投影回神经元。

其中 `d` 远小于神经元数 `N`，论文中通常只占隐藏层宽度的几个百分点。慢状态是共享的上下文调制器，不是独立的状态-only 网络；论文的去掉快速路径消融会让准确率降到接近机会水平。

```text
输入脉冲 s[k]
   ├── W_f s[k] ────────────────────────────┐  快速电流
   └── W_x s[k] + b -> f_x -> x[k]          │
                       └-> m[k]             │  慢速状态
                           └-> W_m m[k] ────┘
             beta*u[k-1] + 两种电流 -> 阈值/复位 -> 输出脉冲
```

### 3. 慢速状态的数学形式

连续时间状态空间模型为：

```text
m'(t) = A m(t) + B x(t)
```

`A` 和 `B` 采用 Legendre Memory Unit（LMU）风格的 Legendre 基构造。对 `i,j = 0,...,d-1`：

```text
A_ij = (2i+1) * {-1            (i < j)
                 (-1)^(i-j+1) (i >= j)}
B_i  = (2i+1) * (-1)^i
```

经过零阶保持离散化后得到冻结的 `Abar`、`Bbar`：

```text
Abar = exp(A Delta t)
Bbar = A^(-1) (exp(A Delta t)-I) B
m[k] = Abar*m[k-1] + Bbar*x[k]
```

状态窗口长度 `theta` 控制这组基函数覆盖的时间范围。代码中先构造连续系统，再用 `cont2discrete(..., method="zoh")` 离散化，并将矩阵注册成不参与训练更新的 buffer（`smnist/src/dual_pathway.py:29-63`）。

### 4. 从输入到输出的完整流程

#### 第一步：快速脉冲电流

```text
I_f[k] = W_f s[k]
```

事件输入通常很稀疏，因此硬件只访问非零脉冲对应的权重列。这个路径负责当前刺激的即时响应。

#### 第二步：标量驱动

```text
x[k] = f_x(W_x s[k] + b)
```

论文把 `f_x` 保持为一般映射；本地 Python 代码使用 `ReLU`。把输入压缩成一个标量，使慢状态的更新复杂度主要由 `d` 决定，而不是由输入维度或神经元宽度决定。

#### 第三步：更新慢状态

用上一时刻状态和当前标量驱动计算 `m[k]`。在 Python 实现中，代码先生成冲激响应 `H_i = Abar^i Bbar`，然后对整个序列做零填充 FFT 卷积，而不是在 Python 中逐步循环。这是训练时的向量化实现；数学上等价于零初始状态下的因果线性递推（`smnist/src/dual_pathway.py:65-73,123-129`）。

#### 第四步：注入神经元膜电位

```text
I_m[k] = W_m m[k]
u[k]   = beta*u[k-1] + I_f[k] + I_m[k]
s_i[k] = Theta(u_i[k] - theta_u)
```

慢状态提供较长时间尺度的上下文，快速路径仍然提供当前刺激的具体信息。SpikingJelly 的多步 LIF 节点负责代码中的阈值、复位和替代梯度。

#### 第五步：堆叠和读出

本地 PS-MNIST、S-MNIST、SHD、SSC 代码各自定义一个两层 `ConvLMU2`，再接线性分类器（例如 `shd/src/dual_pathway.py:159-198`）。代码把每个时间步的分类 logits 做平均；论文 Methods 则描述为使用最后一层平均膜电位。因此读出细节应视为部分匹配，不能直接假设两者完全相同。

### 5. 为什么能改善长程梯度？

忽略输入驱动项，把膜电位和慢状态拼成：

```text
z[k] = [u[k]; m[k]]

z[k+1] = F z[k]

F = [ beta*I_N   W_m*Abar
      0          Abar    ]
```

因此 `partial z[T] / partial z[k] = F^(T-k)`。由于 `F` 是块上三角矩阵，其特征值由膜电位的 `beta` 和 `Abar` 的特征值组成。普通 FSNN 只有 `beta^(T-k)` 这一类快速衰减；DMP 还拥有由 `Abar` 决定的慢模式，并通过 `W_m` 持续注入膜电位。论文的 Extended Data Fig. 4 显示，在最后时间步监督下，DMP-SNN 在较早时间仍能保留可见梯度尾巴。

这是线性化分析，不包括阈值非线性、复位和替代梯度的全部细节。Python 代码中的 gradient taps 可以观测这种效应，但不会自动证明论文的谱分析。

### 6. 膨胀（dilation）和延迟权衡

论文还定义了每隔 `d_s` 个时间步才刷新一次慢电流：

```text
k_d = floor(k/d_s) * d_s
I_m[k] = W_m m[k_d]
```

在两次刷新之间，膜电位只演化快速路径。图 3 显示，S-MNIST/PS-MNIST 等规则序列可以承受较大的跳步，而 SHD/SSC 等不规则事件流更依赖细粒度更新。Extended Data Fig. 3 则显示，增大状态窗口后，学习到的轴突延迟整体向较短范围移动。

**代码边界：**在本地四组 `dual_pathway.py` 和 `train_spiking.py` 中没有找到 `d_s` 或跳步递推的实现。因此这部分结论来自论文和图像，不能声称已经由当前代码复现。

### 7. 硬件如何利用双路径？

硬件把慢电流改写为：

```text
W_m m[k]
 = W_m Abar m[k-1] + W_m Bbar x[k]
 = P m[k-1] + v x[k]
```

这样每个时间步暴露出四类操作：

1. 稀疏 `W_f s[k]`；
2. 稠密 `P m[k-1]`；
3. 标量条件项 `v x[k]`；
4. 下一状态 `Abar m[k-1] + Bbar x[k]`。

Chisel 实现中：

- `SpikeIntegration` 用输入驻留方式按脉冲地址累加 `W_f`；
- `ScalarDrive` 累加 `W_x` 后加 bias、做 ReLU 和饱和；
- `MemoryUpdate` 保存 `m[k-1]`，逐行读取 `Abar`，等待 `x[k]` 后加入 `Bbar*x[k]`；
- `MemoryIntegration` 用输出驻留累加 `P*m[k-1]` 和 `v*x[k]`；
- `NeuronBank` 将漏电、两个电流、阈值、减阈值复位和写回融合到一次神经元 SRAM 读写中。

这些行为可在 `dmp-hw-chisel/src/main/scala/dmpsnn/` 的源代码中直接核对。一个重要限定是：`MemoryIntegration` 模块内部先完成 `P*m[k-1]`，再进入 `v*x[k]` 的 FSM 状态；它和其他顶层路径并行，但两个子路径本身并没有完全重叠。

硬件默认采用 8-bit 权重、16-bit 膜电位/状态、24-bit 电流累加器、`beta/256` 漏电和饱和算术。`DmpGoldenModelSpec.scala` 提供逐时间步的定点参考模型并检查膜电位和脉冲输出。

### 8. 评测与复现状态

论文评测：

- S-MNIST、PS-MNIST：784 步的视觉序列；
- SHD：700 通道事件语音；
- SSC：35 类语音事件流；
- 指标：准确率、参数量、状态/缓冲区配置，以及硬件吞吐、每步能耗和面积。

论文报告 S-MNIST 99.3%、PS-MNIST 97.3%，并声称相对同类 SNN 减少约 40-60% 参数；硬件部分报告相对 Loihi2 延迟实现超过 4 倍吞吐、超过 5 倍能效。Extended Data Fig. 5 显示将 LIF 层加倍后吞吐大体保持，能耗约增 2.4 倍、面积约增 3.1 倍且 SRAM 占主导。

上述数值均为论文报告，本地没有重新训练或执行 22FDX QuestaSim/Innovus 后布局流程。当前仓库可以：

- 阅读并部分运行四个 Python 训练入口；
- 编译、测试和生成通用 Chisel/SystemVerilog；
- 用定点 golden model 检查硬件状态更新。

当前仓库不能一键重现论文全部结果，因为缺少预训练权重、统一五次运行脚本、源数据表/本地 XLSX、权重转换和物理设计脚本。综合判断：核心算法和硬件结构的代码匹配度为**中等**，可用于方法学习和局部复现，但不能把它当作完整的结果再现包。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Dual Memory Pathways for Neuromorphic Temporal Computing

### Problem

Spiking neural networks are naturally sparse and event driven, but standard leaky integrate-and-fire neurons forget old evidence as their membrane state decays. Dense recurrent connections extend memory at quadratic parameter and traffic cost, while learnable axonal delays require deep buffers and per-connection timing support. The paper asks whether long-range context can be retained in a form that is both learnable and inexpensive to implement in neuromorphic hardware.

### Proposed method

Dual Memory Pathways (DMP-SNN) adds a compact slow state `m[k] in R^d` to each layer of `N` feedforward spiking neurons, with `d << N`. Presynaptic spikes follow two paths:

```text
fast:  s[k] -> W_f s[k] -----------------------------+
slow:  s[k] -> scalar x[k] -> stable state m[k]      |
                              -> W_m m[k] ------------+-> LIF update -> spikes
```

The slow state follows a frozen Legendre-derived linear state-space recurrence,

`m[k] = Abar m[k-1] + Bbar x[k]`,

and acts as shared temporal context rather than a replacement for the direct feedforward path. In software, the released model evaluates the recurrence as FFT convolution. In hardware, the slow current is rewritten as `P m[k-1] + v x[k]`, exposing sparse spike integration, dense memory integration, and memory update paths that can be scheduled around a fused neuron-state pass.

### Why it matters

The joint membrane-memory transition contains both fast modes governed by the membrane leak and slower modes governed by `Abar`. The paper argues that these slow modes carry gradients over longer horizons, and the local Extended Data figure visibly shows broader early-time gradient tails than a feedforward SNN. A dilation option updates the memory current less often, allowing computation to be traded for temporal resolution; paper-reported experiments show dense sequential vision tolerates coarser updates better than irregular auditory streams.

### Evaluation and reported results

The algorithm is evaluated on S-MNIST and PS-MNIST (784-step visual sequences) and on SHD and SSC event-based speech. Baselines include feedforward, recurrent, delay-based, adaptive/parametric-neuron, dendritic, and recent spiking sequence models. The paper reports 99.3% on S-MNIST and 97.3% on PS-MNIST, competitive SHD/SSC performance, and 40-60% fewer parameters than comparable state-of-the-art SNNs. The available figures support the qualitative findings that compact memory can be sufficient, removing the fast path collapses the architecture, and longer state windows shift learned delays toward shorter values.

For hardware, the authors compare a 22FDX post-layout DMP design against Loihi2, DenRAM, ReckOn, and an ElfCore-derived design using throughput, energy per timestep, and area. They report more than 4x higher throughput than a Loihi2 delay implementation, more than 5x better energy efficiency than delay-based platforms, and more than 2x better area efficiency than ReckOn. When the LIF layer is doubled, the local scaling figure shows throughput largely retained, approximately 2.4x energy growth, and approximately 3.1x area growth dominated by SRAM.

These numbers are **paper reported**. This workspace did not retrain the networks or rerun the proprietary/technology-dependent physical-design flow.

### Code and reproducibility

The repository includes dataset-specific PyTorch implementations for PS-MNIST, S-MNIST, SHD, and SSC, plus a parameterized Chisel accelerator, generated SystemVerilog, unit tests, and a bit-accurate fixed-point golden model. Direct source comparison gives **medium overall paper-code fidelity**: the state-space equations, FFT memory, dual-path addition, four hardware computations, fused LIF update, and stationarity choices are directly represented.

Important limitations remain:

- the Python LIF dynamics and surrogate gradient are delegated to SpikingJelly;
- the code averages classifier logits, while the paper describes a mean last-layer membrane readout;
- the dilation experiments are not implemented in the released snapshot;
- dataset copies show minor drift, including an SHD memory gate that is declared but not used in its forward expression;
- no pretrained checkpoints, five-run orchestration, local source-data tables, weight-to-hardware conversion flow, or 22FDX synthesis/place-and-route/power scripts were found;
- the Chisel memory-integration module serializes `P m[k-1]` then `v x[k]` internally, although it runs concurrently with the other top-level paths.

The available code is sufficient to inspect the method, run partial software experiments after reconstructing datasets, and test/generate generic RTL. It is not a one-command reproduction package for the paper's headline accuracy or silicon comparisons.

### Limitations and interpretation

DMP is most compelling when long temporal context is the bottleneck and a small shared state captures task-relevant history. The results themselves show that temporal resolution remains task dependent: compact slow state does not eliminate the need for a direct fast path, and noisy multiscale auditory tasks tolerate dilation less well. The fixed Legendre dynamics also constrain the temporal basis; learned projections adapt how information enters and leaves it, but the method does not demonstrate that each state coordinate has a unique interpretable role.

**Reproducibility rating: 3/5.** The core algorithm and synthesizable architecture are open and structurally well matched, with unusually useful hardware tests. Exact end-to-end results remain blocked by missing experiment orchestration, artifacts, source data, and physical-design evidence.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
