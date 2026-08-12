---
layout: default
permalink: /paper-atlas/mmfm-9df85fcf/
title: "MMFM"
nav: false
description: "MMFM（Multi-Marginal Flow Matching）面对的是同一类系统在多个时间点、多个实验条件下采集的群体分布快照。以单细胞药物实验为例，0、24、48、72 小时测到的是不同细胞；某些药物—时间组合还可能完全缺失。模型需要从这些未配对分布中学习连续向量场，补出缺失时间点，并借其他条件的信息改善稀疏条件。"
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
      <span>ICLR · 2025</span>
    </div>
    <h1>MMFM</h1>
    <p>Modeling Complex System Dynamics with Flow Matching Across Time and Conditions</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MMFM：从多时间点、多条件的群体快照学习连续动力学

### 它解决的不是普通时间序列

MMFM（Multi-Marginal Flow Matching）面对的是同一类系统在多个时间点、多个实验条件下采集的**群体分布快照**。以单细胞药物实验为例，0、24、48、72 小时测到的是不同细胞；某些药物—时间组合还可能完全缺失。模型需要从这些未配对分布中学习连续向量场，补出缺失时间点，并借其他条件的信息改善稀疏条件。

输入可写成

$$\{p_{t_k}(x\mid c):c=1,\ldots,C,\ k=0,\ldots,K\},$$

输出是条件化向量场 $v_t(x,c;\theta)$。从初始样本 $x_0$ 解 ODE

$$\frac{dx}{dt}=v_t(x,c;\theta)$$

即可得到一条合成轨迹及任意时间的预测分布。这里的单条轨迹是由分布耦合与模型先验推断出来的，不是真实细胞谱系。

### 证据与版本

- 论文：`paper source/source_paper/hybrid_auto/source_paper.md`，题为 *Modeling Complex System Dynamics with Flow Matching Across Time and Conditions*，ICLR 2025。
- 图像：同目录 `images/`，共 83 个 OCR 图像对象；主要证据是图 1–3、表 1–4 与附录图 4–13。
- 代码：`MMFM/`，来源 `https://github.com/Genentech/MMFM.git`，本地提交 `a6f0cbf9d4c05bd86476845e97915fa779b8e283`（2024-11-25）。
- 无独立 supplement Markdown；理论、训练细节和额外实验已包含在 25 页会议 PDF 附录 A–J 中。

### 从双边 Flow Matching 到多边快照

普通 conditional flow matching 从一对端点 $(x_0,x_1)$ 构造条件概率路径，训练网络拟合其已知速度：

$$L_{CFM}=\mathbb E\|v_t(x;\theta)-u_t(x\mid z)\|_2^2.$$

MMFM 把条件变量扩展成跨所有观测时刻的元组

$$z=(x_0,x_1,\ldots,x_K),$$

并使用同形式的目标

$$L_{MMFM}=\mathbb E_{t,z,x}\|v_t(x;\theta)-u_t(x\mid z)\|_2^2.$$

论文 Proposition 1 在正密度条件下证明该条件目标与边际 flow-matching 目标对参数有相同梯度。关键变化不在平方误差形式，而在于 $z$ 同时含多个时间点、路径 $p_t(x\mid z)$ 必须穿过所有边际。

### 为什么用自然三次样条

MMFM 定义

$$p_t(x\mid z)=\mathcal N(x\mid\mu_t(z),\sigma_t^2I).$$

默认 $\mu_t$ 是穿过所有 $(t_k,x_k)$ 的自然三次样条，即在插值约束下最小化

$$\int_{t_0}^{t_K}\|\gamma''(t)\|_2^2dt.$$

它相当于把“长期轨迹尽量少弯曲”作为先验，同时允许连续曲率。线性消融 L-MMFM 则逐段直连。代码 `MMFM/src/mmfm/multi_marginal_fm.py:309-342` 在每批数据上构造 cubic/linear/Lagrange 插值，并同时取得 $\mu_t$ 与 $\mu'_t$。

这只是先验路径，不是最终预测：神经网络回归大量路径附近的速度后，可以利用跨条件规律修正它。合成图 2 中，三次样条 MMFM 对弯曲轨迹优于线性版；但北京空气数据中 L-MMFM 最好，说明曲率先验必须由验证集选择，不能把 cubic 当成普适物理规律。

### 时间变化噪声的作用

论文在相邻观测点间令 $\sigma_t$ 在边界为零、中间增大。一般条件速度为

$$u_t(x\mid z)=\frac{\sigma'_t}{\sigma_t}(x-\mu_t)+\mu'_t.$$

噪声让网络不只看到一条细线，而在观测间隔内学习邻域向量场，从而更容易跨条件共享。代码 `multi_marginal_fm.py:45-268` 实现常数以及四种 `adaptive*` 形式，`286-307` 实现完整速度公式。论文公式与代码并非只有唯一一个 `adaptive` 名称的一一映射；精确复现要追踪实验命令中的 `flow_variance`。

数值边界也很清楚：自适应速度含 $\sigma'_t/\sigma_t$，靠近观测结点可能不稳定。代码在随机采样 $t$ 的位置留下 TODO，要求避免太接近 knot（`321-325`），但没有实现显式排除。

### 多时间点样本怎样被连成元组

不同时间的细胞没有配对。论文用平方欧氏代价做 optimal transport，在每个条件内依次连接相邻时间点。由于假设总代价是相邻对的可加和，多边 OT 可由 $K$ 个相邻双边 OT 计划组合，而无需直接求指数规模的完整张量。

这使 $z=(x_0,\ldots,x_K)$ 比独立随机拼接更平滑稳定，但 OT 配对仍是成本最优的计算耦合，不等于真实生物祖先—后代。附录 J 指出需解的 OT 问题数随条件数和时间间隔数线性增长；单个 OT 本身仍受样本规模影响。

### 条件共享与 classifier-free guidance

每个观测带条件 $c$，如药物—剂量或空气监测站。MMFM 使用同一个网络权重处理所有条件，只给条件一个 embedding。训练时以概率 $p_u$ 把真实条件替换为可学习的 null condition：

$$L_{C-MMFM}=\mathbb E\|v_t(x,(1-b)c+b\varnothing;\theta)-u_t(x\mid z^c)\|^2.
$$

因此一个网络同时学有条件与无条件动力学。推断时组合两者：

$$\tilde v_t=(1-w)v_t(x,\varnothing)+wv_t(x,c).$$

`MMFM/src/mmfm/models.py:8-39` 精确实现该式；$w>1$ 也允许。药物训练脚本 `experiments/iccite/train_mmfm.py:264-280` 随机屏蔽条件并用速度 MSE 训练。

论文主要实验使用每个类别独立的可学习 embedding。它能从其他条件共享网络参数，但不能直接为从未出现过的类别生成 embedding；论文建议固定网络、仅微调新 embedding。代码另支持 value/fixed embedding，适合剂量等有序条件外推，但这不是主要报告设置。故“泛化到新条件”必须区分：缺失时间点的已知条件、训练中完全未见的离散条件、具有数值描述的可外推条件，这三者难度不同。

### 网络与采样

论文描述先用三层前馈网络编码状态 $x$，用 sinusoidal embedding 编码时间，再拼接条件 embedding，经另一组三层网络预测速度。代码 `models.py:106-280` 支持该结构以及更多激活、归一化、embedding 和深度选项；实验参数决定真正网络。

训练阶段不需要解 ODE，只需在解析路径上采样 $(t,x_t,u_t)$ 并回归速度。生成阶段才从 $x_0$ 数值积分。论文 Algorithm 1 说使用 RK4；`trajectory.py:8-68` 的通用函数默认却是 `dopri5`。这不是证明论文没有用 RK4，而是说明默认 API 与报告配置不同，复现必须显式传 `method="rk4"` 或核对调用脚本。

### 三组实验怎样支持方法

#### 合成动力学

12 个条件具有已知二维时变向量场，条件 3/5 缺部分时间点。图 2 直接比较真实场、FSI 与 MMFM；表 2 在 21 个时间点评估 MSE/MMD。MMFM 对两个稀疏条件最好，并显著优于 L-MMFM，支持“多时间曲率先验 + 跨条件共享”在这个构造场景中的价值。附录图 8 同时显示从训练区域外起步会 overshoot，给出了真实外推失败边界。

#### 单细胞激酶抑制剂

数据含 T 细胞在 0/24/48/72 h 的 18,250 基因表达、93 个抑制剂和多个剂量。论文过滤出 123 个 treatment，再抽 60 个分析，以 scVI/常规处理后的前 25 PCs 建模；每个非零时间点随机留出十个处理。图 3 的 UMAP只展示时间与药物异质性，真正评估来自表 3 的 held-out MSE 与 $W_2$。

MMFM 在三个时间的均值 MSE均最低，在 48/72 h 的 $W_2$ 最低；24 h 的 $W_2$ 是 L-MMFM略好。72 h 优势最大，符合长程曲率信息更重要的解释。但这些是五折论文结果，不是本工作区重跑。

#### 北京 PM2.5

12 个站点作条件，2015-01 至 2017-02 的 26 个月作时间快照；部分站只给 6–7 个月训练。表 4 的 MMD 和附录表 8 的 MSE显示 L-MMFM 优于 cubic MMFM。它提醒读者：空气污染月度轨迹在该设置下不需要同样的曲率先验。

### Paper–code 与复现边界

#### 已由直接代码确认

- 多时间 cubic/linear 路径、解析速度与 flow-matching MSE；
- 自适应/常数方差家族；
- classifier-free null 条件和 guidance 组合；
- 状态/时间/条件网络与 `torchdiffeq` ODE采样；
- synthetic、iccite、weather 训练脚本、grid search 与评估 notebook。

#### 需要保留的差异

- README 示例导入 `mmfm.conditional_flow_matching`，本提交实际模块是 `mmfm.multi_marginal_fm`，示例路径已陈旧；
- 论文采样写 RK4，通用代码默认 `dopri5`；
- 论文突出一个自适应 $\sigma_t$，代码有多个变体；
- 最佳超参数/引导强度由 held-out 数据选择，不是单一固定模型；
- 本地 `MMFM/` 保留嵌套 `.git`，这里只作证据快照，未做发布清理。

#### 未复现

仓库 `data/` 只有说明和占位文件；原始/处理后的药物与天气数据、网格搜索输出和最佳 checkpoint 不在工作区。此次没有安装环境、训练模型或执行 notebooks。因此可以验证算法实现和实验编排，但不能把表 2–4 数值称作本地复现。

### 最简心智模型

MMFM 可拆成五步：

1. 每个条件内，用相邻 OT 把多时刻群体样本串成候选元组；
2. 对每个元组构造穿过全部时间点的 spline/linear 高斯路径；
3. 随机采样路径位置和解析速度；
4. 用共享、条件化且可 classifier-free guidance 的网络回归速度；
5. 从初始分布解 ODE，得到缺失时刻或未来时刻的合成分布。

它的优势来自跨时间、跨条件共享；它的风险也集中在同一处：OT 配对、样条形状、噪声函数和条件表示都是建模先验，数据稀疏时既能提供帮助，也能把错误结构传播到未观测区域。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Multi-Marginal Flow Matching Summary

**Paper:** *Modeling Complex System Dynamics with Flow Matching Across Time and Conditions* (ICLR 2025).

MMFM learns a condition-aware neural vector field from unpaired population snapshots observed at multiple, potentially irregular time points. Instead of fitting independent flows between consecutive snapshots, it samples multi-time tuples using condition-wise optimal-transport couplings, constructs a natural-cubic-spline Gaussian probability path through every tuple, and regresses the path derivative with flow matching. Classifier-free guidance shares dynamics across conditions while retaining condition-specific control.

The method outputs ODE trajectories and missing-time distributions. Synthetic experiments favor cubic MMFM over linear MMFM and pairwise baselines when trajectories curve. On 123 filtered drug-dose treatments from a four-time-point single-cell screen, MMFM reports the best 48 h/72 h distribution imputation and lowest mean error at all three held-out times. On Beijing PM2.5, linear MMFM is best, showing that the spline prior is data-dependent rather than uniformly superior.

Local code at `MMFM/` is repository commit `a6f0cbf9d4c05bd86476845e97915fa779b8e283`. It implements spline/linear paths, adaptive variance families, classifier-free training, guided ODE sampling, experiment scripts and evaluation notebooks. Reproduction still requires externally downloaded datasets and grid-search artifacts; no benchmark was rerun here.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
