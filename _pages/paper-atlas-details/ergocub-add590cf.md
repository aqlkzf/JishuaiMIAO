---
layout: default
permalink: /paper-atlas/ergocub-add590cf/
title: "ergoCub"
nav: false
wide: true
description: "这篇工作不是先造好机器人、再让控制器尽量配合人，而是把人—机器人—负载的耦合动力学作为统一计算底座：先用它优化机器人的肢体比例，再在真实机器人上用人的实时状态调节运动，从而把人的工效学指标同时嵌入硬件设计和物理智能。 论文将这种思路称为 shared embodied intelligence（共享具身智能）。其实体实现是 ergoCub：36 自由度、身高 1.50 m、质量 56.7 kg，面向协同搬运和稳健行走。"
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
    <h1>ergoCub</h1>
    <p>Towards shared embodied intelligence in humanoid robots through optimization, development and testing of the human-aware ergoCub robot</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/ami-iit/paper_sartore_2025_ergocub_nature_machine_intelligence" target="_blank" rel="noopener noreferrer" aria-label="Open code for ergoCub">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ergoCub 方法详解：把“人的负担”同时写进机器人身体与控制器

### 一句话抓住核心

这篇工作不是先造好机器人、再让控制器尽量配合人，而是把**人—机器人—负载的耦合动力学**作为统一计算底座：先用它优化机器人的肢体比例，再在真实机器人上用人的实时状态调节运动，从而把人的工效学指标同时嵌入硬件设计和物理智能。

论文将这种思路称为 **shared embodied intelligence（共享具身智能）**。其实体实现是 ergoCub：36 自由度、身高 1.50 m、质量 56.7 kg，面向协同搬运和稳健行走。

### 1. 它要解决什么问题？

传统人形机器人开发通常分成两步：机械结构先定型，控制器再负责走路、操作和人机协作。这样做有一个根本限制：如果机器人的身高、臂长、腿长、质心和质量分布本身不适合协作，后续控制只能在既定身体上补救，无法改变人的可达范围和载荷分配。

已有的人机协作控制强调安全、效率或工效学，但论文指出，共同行动仍受限于对伙伴的内部表示不足。另一方面，机器人形态与控制协同设计已有研究，例如：

- Rasmussen 等在 *Structural and Multidisciplinary Optimization*（2002）中讨论面向工效属性的设计优化；
- Bravo-Palacios 与 Wensing 在 IROS 2022 中研究腿式机器人的大规模协同设计；
- Fadini 等在 *IEEE Robotics and Automation Letters*（2022）中研究仿真辅助的鲁棒机器人优化；
- Sartore 等在 Humanoids 2022/2023 中研究人形机器人面向协同搬运的工效设计。

但这些方向通常没有把“人的身体模型 + 人的控制/感知状态 + 机器人硬件 + 机器人控制”放进一个贯穿设计期和运行期的统一架构。本文的推进点正是：**设计机器人时，人不是外部约束；机器人运行时，人也不是一个简单扰动源。**

### 2. 两个串联的架构实例

整套方法可看成两个前后衔接的计算实例：

```text
实例 1：离线硬件优化
iCub3 拓扑 + 参数化连杆 + 人体模型 + 箱体 + 多个静态搬运高度
    -> 耦合动力学与接触约束
    -> 最小化人/机器人关节力矩，抬高机器人质心
    -> 最优连杆长度 π*
    -> 机械制造与工程细化
    -> ergoCub 实体

实例 2：固定硬件上的物理智能
ergoCub + 人体实时状态 + 预规划轨迹 + 传感器反馈
    -> 轨迹规划
    -> 由人手高度驱动的轨迹进度调节
    -> 全身逆动力学/QP 控制
    -> 协同搬运

或：去掉人体分支
    -> 质心 MPC + jerk 调节 + 全身控制
    -> 稳健行走
```

这不是端到端学习策略。主要工具是参数化多刚体动力学、非线性优化、逆运动学、约束投影、模型预测控制和二次规划。

### 3. 先把机器人身体变成可优化变量

#### 3.1 单个连杆如何参数化

论文把机器人连杆简化成球体、圆柱和长方体。对于几何参数为 $l$、密度为 $\rho$ 的刚体，其质量、惯量和质心写成：

$$
\begin{array}{l}
m(l,\rho )={\displaystyle\iiint }_&#123;&#123;\mathcal{V}}(l)}\rho (r) dr,\\
I(l,\rho )=-{\displaystyle\iiint }_&#123;&#123;\mathcal{V}}(l)}\rho (r){\left[S(r)\right]}^{2}dr,\\
c(l,\rho )=\displaystyle\frac&#123;&#123;\displaystyle\iiint }_&#123;&#123;\mathcal{V}}(l)}r\rho (r) dr}{m(l,\rho )}.
\end{array}
$$

其中 $l_m$ 是沿主方向拉伸形状的长度乘子。改变 $l_m$ 不只是改变外观：质量、惯量、质心位置、运动学链长度和接触雅可比都会变化，因此协作时人和机器人的受力也会随之变化。

#### 3.2 整机参数化动力学

将同一做法应用到浮动基多刚体链的所有连杆，得到：

$$
M(q,\pi)\dot{\nu}+h(q,\nu,\pi)=B\tau+J_c^T(q,\pi)f,
$$

并满足接触速度约束

$$
J_c(q,\pi)\nu=0.
$$

这里：

- $q=[{}^{\mathcal I}p_{\mathcal B},{}^{\mathcal I}R_{\mathcal B},s]$ 是基座位姿和关节角；
- $\nu=[{}^{\mathcal I}v_{\mathcal B},\dot{s}]$ 是广义速度；
- $\pi$ 是连杆硬件参数集合；
- $M$ 是质量矩阵，$h$ 包含科氏力和重力；
- $B$ 选择可驱动关节，$\tau$ 是关节力矩；
- $J_c$ 和 $f$ 分别是接触雅可比与接触力/力矩。

**代码验证。** `OptimalHardware/Optimizer.py:79-116` 确实把连杆长度乘子、关节构型和基座位姿建成 CasADi 变量；`Optimizer.py:130-160` 从外部 ADAM 库取得参数化的 $M$、重力项、雅可比、正运动学和质心函数。论文一般性地讨论长度和密度，但发布脚本设置 `add_denstiy = False`，实际实验只优化长度（`eCub_lengthWithHumanOptimization.py:124-145`）。

### 4. 人体模型不是一个点质量

论文使用 34 关节浮动基人体模型：每条手臂 6 个关节，每条腿 9 个，背部 4 个。人体各节段质量依据人体测量表分配；600 多块肌肉的合效应被压缩为人体关节力矩 $\tau_H$。

在线协作时，论文描述了两类估计：

1. 由 iFeel 和跟踪器传感器通过逆运动学恢复人体构型；
2. 将 IMU、足底力/力矩和人体动力学合并，用最大后验估计得到关节动力学量。

紧凑形式为：

$$
\left[\begin{array}{c}Y(s_H)\\D(s_H)\end{array}\right]d+
\left[\begin{array}{c}b_Y(s_H,\dot{s}_H)\\b_D(s_H,\dot{s}_H)\end{array}\right]
=\left[\begin{array}{c}\gamma\\0\end{array}\right],
$$

并求

$$
[\mu_{d\mid\gamma},\Sigma_{d\mid\gamma}]
=\mathop{\rm argmax}\limits_d \mathcal P(d\mid\gamma).
$$

$\gamma$ 汇集传感器观测，$d$ 包括连杆/关节的运动学与动力学量。由此估计人体关节力矩，尤其监控腰骶关节 L5–S1 的负荷。

**证据边界。** 发布代码中的搬运脚本会读取人体关节状态并把人体模型放入控制回路，但最大后验估计、窗口为 2 的移动平均、L5–S1 提取和 LCD 压力反馈逻辑在本地仓库中 **Not found**。这些是论文陈述，不是本次直接代码验证结果。

### 5. 关键一步：耦合人、机器人和箱体

分别用 $R$、$H$、$o$ 表示机器人、人和物体。三个子系统的质量矩阵组成分块对角矩阵；脚与地面、手与箱体之间的速度一致性约束被堆叠进 $Q(q,\pi)$。于是整个系统变成：

$$
M(q,\pi)\dot{\nu}+h(q,\nu,\pi)=B\tau+Q^T(q,\pi)f,
$$

以及加速度层接触约束：

$$
\dot Q(q,\pi)\nu+Q(q,\pi)\dot\nu=0.
$$

这一步为何重要？因为它建立了一条可计算的因果链：

```text
机器人连杆长度 π
 -> 机器人质量/惯量/雅可比变化
 -> 人—机器人—箱体的受力分配变化
 -> 人体关节力矩变化
 -> 人体工效代价可以反向优化机器人身体
```

**代码验证。** `OptimalHardware/OptimizerHumanRobot.py:102-220` 组装机器人、人体和箱体的质量矩阵与接触雅可比块；`OptimizerHumanRobot.py:668-754` 将双方的手位置约束到箱体四个接触框架。

### 6. 硬件优化到底在算什么？

#### 6.1 决策变量

$$
y=[\tilde q\quad\pi]^T,
$$

其中 $\tilde q$ 是多个搬运高度下的人体与机器人静态构型集合，$\pi$ 是机器人连杆长度。

#### 6.2 目标函数与约束

论文的优化问题为：

$$
y^*=\mathop{\rm argmin}\limits_y(W_1T_1+W_2T_2+W_3T_3),
$$

约束包括耦合动力学、接触一致性、手/脚/箱体目标位姿 $H_i=H_i^*$，以及静态条件 $\nu=0,\dot\nu=0$。三个代价分别是：

$$
T_1=\|S_R\tau(q,\pi)\|_2^2,
\qquad
T_2=\|S_H\tau(q,\pi)\|_2^2,
$$

$$
T_3=\left\|\frac{1}&#123;&#123;}^{\mathcal I}p_{z0,com}}\right\|_2^2.
$$

$T_1$ 降低机器人力矩，$T_2$ 降低人体力矩，$T_3$ 通过最小化质心高度的倒数来提高机器人质心。论文认为较高质心有利于提高系统带宽和行走鲁棒性。报告的权重为 $W_1=10^5$、$W_2=10^{10}$、$W_3=1$，说明人体力矩是极强优先级目标。

#### 6.3 为什么要做约束投影？

若直接把所有接触力作为设计约束中的显式变量，数值问题会更复杂。论文把动力学投影到接触约束的零空间：

$$
N_\Lambda=I-Q^T(QM^{-1}Q^T)^{-1}QM^{-1}.
$$

在静态构型下只剩重力项，于是最小范数关节力矩为：

$$
\tau(y)=(N_\Lambda(q,\pi)B)^\dagger N_\Lambda(q,\pi)g(q,\pi).
$$

这条式子既用于优化代价，也用于 Fig. 3 的人体背部力矩比较。

**代码验证。** `OptimizerHumanRobot.py:168-239` 和 `Optimizer.py:171-197` 直接构造同型的 $N_\Lambda$ 并通过伪逆计算 $\tau$。入口脚本在 `eCub_lengthWithHumanOptimization.py:142-175` 依次构造三个优化器、加入机器人/人体/接触/箱体项、用 CasADi/IPOPT 求解、导出修改后的 URDF，再计算力矩与接触力。

**部分匹配。** 本地代码中没有在一个位置直接声明论文的 $W_1,W_2,W_3$；代价缩放分布在多个方法中，因此论文三权重与代码的逐项对应只能标为 **Partial**。

### 7. 从优化模型到真实 ergoCub

非线性形态优化对初值敏感，作者从成熟的 iCub3 拓扑开始，并保留电子系统和电机类型、限制最大高度，以提高制造可行性。两个候选设计分别覆盖 0.8–1.2 m 和 0.8–1.5 m 搬运高度。最终选择绿色模型，不是因为它在每个高度都最优，而是因为它在大多数中高位背部力矩上更好，同时把可达高度扩展到 1.5 m。

图像直接显示：优化绿色模型为 1.44 m、70 kg、CoM 0.70 m；真实 ergoCub 为 1.50 m、56.7 kg、CoM 0.72 m。差异来自 LCD 头部、沿用的电子部件和电机、金属延长件、线缆/外壳、均匀密度假设和制造细化。因此，这一阶段的正确理解是：

> 优化器给出全身比例与动力学目标，制造过程在保持总体设计意图的同时做工程落地，而不是把简化模型一比一制造出来。

### 8. 固定身体后，如何跟随人搬箱子？

物理智能采用规划—调节—控制三级级联。

#### 8.1 轨迹规划

给定允许的箱体高度范围，通过逆运动学求出下端构型 $s_1$ 和上端构型 $s_2$。报告实验使用 0.8–1.2 m。这个几何路径预先算好，在线阶段主要调节沿路径的进度。

#### 8.2 轨迹调节：人是主信号

用 $\psi(t)\in[0,1]$ 表示路径相位：

$$
s_R^r(t)=s_1+\int_0^t\dot{s}_R(\psi(t))dt,
\qquad
\dot{s}_R^r(\psi(t))=(s_2-s_1)\dot\psi(t).
$$

机器人期望手速由人手和机器人手的高度差产生：

$$
\dot z_R=k_\psi(z_H-z_R),
\qquad
\dot\psi=[J_s^z(s_2-s_1)]^\dagger\dot z_R.
$$

因此，人抬高手，机器人沿预规划路径向上；人降低手，机器人反向；超出 $s_1$–$s_2$ 范围则停止继续跟随。这一机制是反应式的，没有预测未来人体动作，所以结果曲线中存在延迟。

**代码验证。** `PhysicalIntelligence/launch_lifting_controller_with_human.py:282-318` 把人手高度、机器人手高度、手部雅可比、3 ms 步长和增益 6.2 送入外部状态机。但 `StateMachine.get_state` 的实现不在当前快照中，因此 Eq. (19) 只能标为 **Partial**。

#### 8.3 轨迹控制：高频全身 QP

内环采用任务空间逆动力学，在满足耦合动力学、接触和任务雅可比约束的前提下，最小化关节与任务空间加速度跟踪误差：

$$
\min_\tau\ \|\ddot s_R-\ddot s_R^*\|^2+
\sum_{n=0}^{N-1}\|\ddot x_{R,n}-\ddot x_{R,n}^*\|^2.
$$

任务空间使用 PID 形式，关节空间使用 PD 形式。目标是二次函数、约束为线性形式，所以可用 QP 高频求解，并通过关节力矩实现人机协作所需的柔顺性。

**代码验证。** 搬运脚本读取人和机器人的关节状态，更新运动学/动力学，建立姿态与动量任务、投影动力学和接触力 QP，最后发送关节力矩和位置命令（`launch_lifting_controller_with_human.py:203-382`）。核心控制器位于外部 `wholebodycontrollib/shared-controllers`，所以 Eq. (15–17) 的精确实现仍是 **Partial**。

### 9. 行走分支

行走时去掉人体模型：

1. 非线性质心 MPC 规划 CoM、角动量、脚步与接触力；
2. jerk 控制器根据实际状态调整 CoM 和接触力；
3. 瞬时逆动力学/任务栈 QP 生成关节命令。

论文报告规划/调节层约 50 Hz，轨迹控制层约 500 Hz。硬件阶段提高质心的目标与这个控制栈互补。但本地发布快照中只有行走数据，没有可见的行走控制源码，因此这部分属于**论文方法与结果陈述，代码 Not found**。

### 10. 结果应该如何解读？

#### 10.1 形态输出

绿色模型覆盖 0.8–1.5 m，并在多数中高位降低人体背部力矩。但 Fig. 3 也清楚表明它在 0.8 m 并非处处最好，因此不能写成“所有高度全面支配”。

#### 10.2 真实协同搬运

论文报告三种载荷下平均手高误差 0.0084 m，平均最大误差 0.0339 m。Fig. 4 显示 L5–S1 最大估计力矩：

| 载荷 | 人单独搬运 | 人机协作 | 约降幅 |
|---|---:|---:|---:|
| 空载 | 43.95 Nm | 24.88 Nm | 43% |
| 1 kg | 50.66 Nm | 25.77 Nm | 49% |
| 2 kg | 43.88 Nm（图） | 31.82 Nm | 27% |

论文正文把 2 kg 人单独搬运写成 44.88 Nm，与图中 43.88 Nm 相差 1 Nm；两者不应被悄悄合并。力矩是模型估计的生物力学指标，不等同于临床伤害风险或主观舒适度。

#### 10.3 行走

相同指令/控制架构下，ergoCub 最大步长 0.35 m（iCub3 为 0.28 m），最短步时 0.5 s（iCub3 为 0.8 s）。论文还描述了负载、推扰和意外触地恢复实验。但本地缺少 Fig. 5 图像和行走源码，故这些只能作为论文报告结果，不能声称已由本次图像/代码核验。

### 11. 代码—论文一致性与复现边界

总体一致性为 **medium**：硬件优化部分匹配较强，物理智能部分依赖外部库且不完整。

- **Exact：** 形态决策变量、参数化动力学接口、耦合矩阵块、约束投影、最小范数力矩、力矩/CoM 目标、CasADi/IPOPT 求解和 URDF 导出。
- **Partial：** 三个论文权重的逐项代码映射；人手驱动的 $\dot\psi$；全身逆动力学与 QP；实验日志到 Fig. 4 的生成链。
- **Not found：** 行走控制器、人体 MAP 力矩估计、移动平均、LCD 工效反馈、自动化测试、完整图表重现脚本。
- **外部依赖：** 参数化动力学依赖 `adam`；物理智能核心依赖 `shared-controllers/wholebodycontrollib`；硬件优化还需要单独许可的 Coin-HSL；真实实验依赖 YARP、机器人和人体传感器接口。

因此，代码最适合用来理解和在具备完整实验环境时重跑两个主工作流，而不是一个开箱即用、能从零生成论文所有结果的复现包。

### 12. 已知局限与可研究方向

#### 论文明确陈述的局限

- 硬件优化只用静态搬运姿态，动态工效由运行期控制承担；
- 基本几何体和均匀密度造成 sim-to-real 差距；
- 非线性优化对初值和局部极值敏感；
- 搬运控制没有人体动作预测，因此存在滞后；
- 实验集中在受约束的搬运与行走任务，不能直接外推到长期、多用户或临床场景。

#### 假设生成，不是本文已验证结论

- 可把短时人体动作预测加入轨迹规划，以提前优化未来工效代价；
- 可将连杆拆为电机、电子件、结构件和外壳等子组件，逐级缩小制造差距；
- 可为多个人体/多种负载复制耦合动力学与目标，形成鲁棒或人群级硬件设计；
- 可在样机完成后将实测惯量和执行器参数反馈给优化器，形成设计—制造—标定闭环。

这些方向与论文讨论一致或由其框架自然导出，但不能与已实现、已验证结果混为一谈。

### 最后记忆点

理解 ergoCub 方法时，最值得记住的不是某个单独的 QP，而是下面这条闭环：

```text
人的身体/行为表示
  -> 进入耦合动力学
  -> 让人体负担成为机器人形态的优化目标
  -> 制造成真实机器人
  -> 再用人的实时状态驱动机器人的轨迹与控制
```

这条“设计期考虑人、运行期继续表示人”的连续性，正是 shared embodied intelligence 相对于普通硬件优化或普通人机协作控制的主要方法价值。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ergoCub: Shared Embodied Intelligence Through Human-Aware Hardware and Control Co-design

### Problem

Humanoid collaboration is usually improved at the behavior/control level after the robot body is fixed. This can make a controller safer or more ergonomic, but it cannot recover performance lost because the morphology, mass distribution, reach, sensing, and actuation were designed without the human partner. Standard cascade controllers also have limited partner representation: trajectory planning, adjustment, and control primarily optimize robot/task quantities, while human awareness is appended rather than embedded across the stack.

The paper proposes **shared embodied intelligence**: optimize both robot hardware and physical-intelligence parameters using coupled representations of the robot, human partner, payload, and environment. The concrete realization is ergoCub, a 36-DoF, 1.50 m, 56.7 kg humanoid developed for ergonomic payload collaboration and robust walking.

### Core Method

The framework has two sequential instances:

1. **Human-aware morphology optimization.** Robot links are represented by parametrized basic shapes. Their lengths determine inertial properties and therefore floating-base dynamics. A 34-joint human model and rigid payload are coupled to the robot through feet/environment and hand/payload constraints. At static lifting heights, contact forces are projected out and minimum-norm human/robot joint torques are computed. A nonlinear program chooses robot link lengths to minimize robot torque, strongly weighted human torque, and inverse robot CoM height (the latter encourages locomotion bandwidth/robustness).
2. **Physical intelligence on fixed hardware.** For collaborative lifting, inverse kinematics supplies lower/upper robot configurations; human hand height advances a scalar path phase; and a high-frequency task-space inverse-dynamics/QP layer sends compliant joint commands. Human kinematics and joint torques are estimated online to personalize collaboration and monitor L5–S1 stress. For locomotion, the human branch is removed and a centroidal-MPC/jerk-control/cascade stack is used.

This is a model-based co-design and optimal-control architecture, not an end-to-end learned policy.

### Main Evidence

- **Morphology:** the selected green optimization supports payload heights from 0.8 to 1.5 m and improves most reported human back-torque values at mid/high heights relative to the original model. It is a compromise, not uniformly best at every height. Manufacturing refines the result: the optimized model predicts 1.44 m and 70 kg, while ergoCub is 1.50 m and 56.7 kg with close limb lengths.
- **Collaborative tracking:** with empty, 1 kg, and 2 kg payloads, the paper reports 0.0084 m average hand-height error and 0.0339 m mean maximum error. Estimated peak L5–S1 torque decreases from 43.95 to 24.88 Nm (empty), 50.66 to 25.77 Nm (1 kg), and 44.88 to 31.82 Nm (2 kg). The local Fig. 4 image instead shows 43.88 Nm for the last unassisted value; this text/figure discrepancy is retained.
- **Locomotion:** compared with iCub3 under the same walking command/control architecture, ergoCub reaches 0.35 m maximum step length versus 0.28 m and 0.5 s minimum step duration versus 0.8 s. The paper also reports push/carrying/recovery tests, but the local Fig. 5 image is MISSING.
- **Scope of validation:** the results demonstrate feasibility and internal consistency on structured lifting and walking tasks. They are not a population-level ergonomic or clinical study, and no broad baseline comparison isolates the contribution of each architecture component.

### Code and Reproducibility

**Reproducibility: 3/5 (medium).** The public snapshot at commit `ba233b9224ec663fc238447f8fc1b8eccab259d9` contains a clear CasADi/IPOPT hardware-optimization path, parametric dynamics wrappers, coupled human–robot–box constraints, projected torque objectives, modified-URDF export, physical-intelligence launch scripts, models, Docker/dependency files, and selected walking data.

The strongest match is the hardware instance: direct source implements the morphology variables, block coupled dynamics, constraint projection, pseudoinverse torque, CoM/torque objectives, nonlinear solve, and output model. Physical-intelligence fidelity is only partial because core state-machine, whole-body controller, and QP behavior resides in external `shared-controllers`/`wholebodycontrollib`; parametric dynamics relies on external `adam`; and the Coin-HSL solver requires separate licensing. The local snapshot does not contain the locomotion controller, MAP human-torque estimator, moving-average/LCD feedback logic, automated tests, or scripts that regenerate every reported figure from bundled data. Robot middleware, sensors, and hardware are additionally required for the real-time experiments.

### Limitations and Open Gaps

- Hardware optimization uses static configurations, simplified geometry, and uniform densities; nonlinear sensitivity and manufacturing constraints create a documented sim-to-real gap.
- Collaborative trajectory adjustment is reactive and visibly lags because no human-motion forecast is used.
- Supplementary information was linked but not locally converted, so appendices and supplementary figures were not available for source verification.
- Fig. 5 and locomotion implementation are not present locally; locomotion findings remain paper claims rather than image/code-verified results.
- Exact paper weights and Eqs. (15–19) are only partially traceable to local source because scaling and controller internals are distributed across methods and external dependencies.

### Takeaway

The paper's important contribution is not a single controller equation: it is an engineering methodology that puts a human model inside both morphology selection and run-time control. ergoCub provides a tangible demonstration that the same coupled human–robot representation can guide link proportions, ergonomic lifting behavior, and locomotion-oriented design, while the released code most convincingly supports the offline co-design portion and only partially exposes the full experimental control stack.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
