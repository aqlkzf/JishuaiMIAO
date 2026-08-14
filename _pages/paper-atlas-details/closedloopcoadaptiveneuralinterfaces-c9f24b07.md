---
layout: default
permalink: /paper-atlas/closedloopcoadaptiveneuralinterfaces-c9f24b07/
title: "ClosedLoopCoAdaptiveNeuralInterfaces"
nav: false
wide: true
description: "Madduri 等人在 Nature Machine Intelligence（2026）研究闭环神经接口中的“双学习者”问题：用户会根据光标反馈改变肌肉控制策略，解码器也会在线改变 EMG 到光标速度的映射。若只把用户视为适应者或只让解码器跟随用户，就无法预测两者同时变化时的稳定性、性能和最终策略。论文提出把控制理论和博弈论结合起来的分析/预测框架，并在 14 人的表面肌电接口实验中验证。"
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
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>ClosedLoopCoAdaptiveNeuralInterfaces</h1>
    <p>Computational framework to predict and shape human–machine interactions in closed-loop, co-adaptive neural interfaces</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-026-01194-z" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ClosedLoopCoAdaptiveNeuralInterfaces">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 闭环协同自适应神经接口：方法中文解读

### 论文要解决什么问题？

Madduri 等人在 *Nature Machine Intelligence*（2026）研究闭环神经接口中的“双学习者”问题：用户会根据光标反馈改变肌肉控制策略，解码器也会在线改变 EMG 到光标速度的映射。若只把用户视为适应者或只让解码器跟随用户，就无法预测两者同时变化时的稳定性、性能和最终策略。论文提出把控制理论和博弈论结合起来的分析/预测框架，并在 14 人的表面肌电接口实验中验证。

### 实验平台与数据流

参与者用优势前臂的 64 通道高密度表面 EMG 控制二维光标，跟踪由多组正弦波组成的不可预测目标轨迹。每人完成两个 block、每个 block 8 个 5 分钟 trial。EMG 以 2,048 Hz 采集，经 10/130 Hz 高低通、整流和移动平均后降采样到 60 Hz。光标和目标也以 60 Hz 更新。

```text
前臂 64 通道 EMG
  -> 滤波/整流/移动平均 (u_t, 60 Hz)
  -> Wiener 速度解码器 D: v_t = D u_t
  -> 积分: y_t = y_(t-1) + v_t Delta t
  -> 用户看到 tau-y 与 tau_dot-y_dot 的反馈
  -> 每约 18-20 s 用过去 20 s 求最优 D*，再 SmoothBatch 更新 D
  -> 同一 20 s 估计用户编码器 E
  -> 计算误差、EMG 调谐、D-E 矩阵乘积和统计检验
```

解码器每 trial 随机初始化，测试慢学习率 alpha=0.75、快学习率 alpha=0.25；解码器努力惩罚 lambda_D 测试 10^2 和 10^3；另有两个符号相反的随机初始化 D1/D2。主要性能指标是欧氏跟踪误差 ||tau-y||_2，采用配对 Wilcoxon signed-rank 检验（论文 Methods，lines 251-356）。

### 控制理论模型：把用户和解码器拆开

用户编码器把目标位置/速度和位置/速度误差转换为 EMG：

$$u=E\left[\begin{array}{c}\tau\\\dot{\tau}\\\tau-y\\\dot{\tau}-\dot{y}\end{array}\right]+\beta 1_t^\top,$$

其中 E 是 64x8，beta 是静息活动偏置。按前馈/反馈和位置/速度阶次分块：

$$E=[F_0\;F_1\;B_0\;B_1],$$

即

$$u=F_0\tau+F_1\dot{\tau}+B_0(\tau-y)+B_1(\dot{\tau}-\dot{y}).$$

每 20 s 用 1,200 个样本做线性回归，得到与当前解码器匹配的 E。将重建 EMG 再送入 D，比较重建光标与真实光标的 R^2，并以时间打乱 EMG 作为基线。

由于 dot{y}=D u，精确跟踪要求

$$D F_0=0,\qquad D F_1=I.$$

因此 D F_0 衡量位置前馈残差，D F_1 是否接近单位阵衡量速度前馈是否正确。闭环稳定性可由 D B_0、D B_1 近似负定对角矩阵来保证。实验中 D F_1 逐渐接近单位阵，反馈乘积接近负对角稳定区域，而 F_0 的偏离与跟踪误差相关。

编码器/解码器的变化用矩阵范数差和子空间主角度衡量。结果显示：用户和解码器都在 trial 内发生有方向的变化；解码器从随机初值快速趋稳，但用户编码器不会在 5 分钟内完全停止变化；跨 trial 的用户变化逐渐减小，说明用户在学习。

### 博弈论模型：预测协同自适应的结局

为获得可解析预测，论文把 E、D 简化为标量。两方共享任务误差，但分别惩罚自身努力：

$$c_E=e(E,D)+\lambda_E f_E(E),\qquad c_D=e(E,D)+\lambda_D f_D(D),$$

其中 e=(1-DE)^2，f_E(E)=E^2，f_D(D)=D^2。两者构成势函数

$$\phi(E,D)=(1-DE)^2+\lambda_E E^2+\lambda_D D^2.$$

驻点满足 partial_E phi=partial_D phi=0。原点是鞍点；在论文讨论的惩罚范围内，另有一对镜像局部极小点：

$$E^*=\pm\sqrt{\sqrt{\lambda_D/\lambda_E}-\lambda_D},$$

$$D^*=\pm\sqrt{\sqrt{\lambda_E/\lambda_D}-\lambda_E}.$$

离散适应规则是用户梯度下降、解码器平滑最佳响应：

$$E^+=E-\alpha_E\partial_E\phi(E,D),$$

$$D^+=\alpha_DD+(1-\alpha_D)\arg\min_D\phi(E,D).$$

在驻点附近线性化并计算最大特征值模 rho，得到误差衰减率 e(i) <= e(0) rho^i；所有特征值模小于 1 才满足离散稳定性。模型因此预测：

1. 用户和解码器的学习率共同决定收敛，过快的解码器可能扰乱用户学习；
2. 增大解码器努力惩罚会改变驻点，使解码器和用户在努力上互相补偿，而不一定改变任务误差；
3. 多个驻点意味着随机初始化可能偏置最终的用户/解码器策略。

### 关键结果

* 误差在 trial 内下降，第二个 block 的中段和末段误差进一步降低；EMG 调谐曲线的早晚差异大于相邻 30 s 波动，证明用户和解码器共同适应。
* 快解码器条件的误差更高、用户编码器变化更小，D F_1 和 D B_1 离理想跟踪/稳定值更远，符合“解码器适应太快，用户跟不上”的预测。
* 高 lambda_D 减小解码器范数、增加用户编码器努力；任务误差变化无显著差异，但低惩罚条件光标速度更快。参与者呈现保持努力、保持速度或同时改变两者的不同折衷策略。
* D1/D2 对早晚误差和总体性能没有显著影响；扩展图只显示最终乘积的细微初始化效应。

### 如何理解、哪些地方不能过度外推？

控制模型把用户近似成线性、即时反馈控制器，未建模感觉延迟等真实运动控制因素。博弈模型是标量近似，不是对 64 通道用户动态的拟合；E^2、D^2 只是努力的代理变量，且模型没有显式优化光标速度。用户学习率无法预先估计，实验只比较了两个解码器速率，因此不能把结果外推为完整的速率曲线。

在本地搜索范围内属于 **Not found/MISSING**，所以不能进行实现级复跑或代码行为核验。上述解释仅依据 Nature 主文、方法公式和 11 张本地图像。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Closed-loop co-adaptive neural interfaces: summary

### Problem

Adaptive neural interfaces contain two learners: the user changes the biological control policy while the decoder changes the mapping from biosignals to device commands. Existing user-leading or decoder-following designs do not predict the outcomes of this two-learner interaction, making choices such as decoder learning rate and regularization largely empirical.

### Proposed framework

Madduri et al. introduce an experimentally validated framework combining control theory and game theory. In a 64-channel surface-EMG cursor interface, a linear encoder model maps target position/velocity and position/velocity error to EMG. Linear regression on matched 20-s windows estimates E=[F_0 F_1 B_0 B_1], and products D F_0/D F_1 test exact tracking while D B_0/D B_1 test closed-loop stability. A scalar potential game then assigns task error plus effort penalties to user E and decoder D, with gradient-descent user updates and smoothed-best-response decoder updates. Linearization and spectral radius provide a convergence/error-decay diagnostic.

### Experimental evidence

Fourteen volunteers tracked pseudorandom 2D trajectories for 16 five-minute trials (two eight-trial blocks). EMG was sampled at 2,048 Hz, filtered/rectified and downsampled to 60 Hz. The decoder was reinitialized randomly and updated approximately every 18–20 s using SmoothBatch. Slow (alpha=0.75) versus fast (0.25) learning rates, low (lambda_D=10^2) versus high (10^3) effort penalties, and two signed initializations were crossed.

Tracking error decreased within trials and across blocks, while EMG tuning amplitudes and preferred directions changed more across a trial than across adjacent 30-s intervals. Encoder reconstructions predicted cursor position/velocity better than time-shuffled controls. D F_1 approached identity, D F_0 was near zero but correlated with residual error, and feedback products were near negative-diagonal stability values.

The model predicted and experiments confirmed that fast decoder adaptation can disrupt co-adaptation: fast trials had higher error, less encoder change, and poorer tracking/stability products. Increasing decoder penalty reduced decoder norm, increased user encoder effort and reduced cursor speed without a significant tracking-error change. Decoder initialization had no significant gross performance effect and only subtle effects on final encoder–decoder products. Participants displayed heterogeneous effort/speed trade-offs.

### Reproducibility and limitations

The paper provides equations, experimental parameters, statistical tests and figure-level results. It states that raw data and scripts are publicly available in Code Ocean capsule `10.24433/CO.4049054.v3`, but no capsule, archive, raw data, supplementary markdown, or executable notebook was available in this workspace. Implementation behavior is therefore **Not found/MISSING** beyond the published description. The control model assumes linear instantaneous feedback and omits sensory delays; the game model is scalar and uses effort proxies E^2/D^2. User learning rates are unknown, only two decoder rates were tested, and the penalty model does not explicitly optimize cursor speed. Reproducibility rating: **3/5 (published method and figures are detailed; local code/data rerun unavailable)**.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
