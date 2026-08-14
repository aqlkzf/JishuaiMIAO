---
layout: default
permalink: /paper-atlas/fbno-9df4415b/
title: "FBNO"
nav: false
wide: true
description: "自由边界问题（FBP）里，未知量不只是物理场 u，还包括 u 所在的区域 \\Omegat 与边界 \\Gamma。例如 Stefan 融化问题中，温度决定冰水界面的移动，而温度又只定义在该移动界面限定的区域内。普通神经算子通常假定输出函数定义在预先给定的固定紧集上；FBP 的输出域事先未知，因此不能直接套用这一假设。"
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
    <h1>FBNO</h1>
    <p>Deep neural operator for free boundary problems</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/ZongjiaLong/FBNO-Deep-neural-Operator-for-Free-Boundary-Problems" target="_blank" rel="noopener noreferrer" aria-label="Open code for FBNO">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## FBNO 方法解读：在固定参考域上学习自由边界问题

### 它要解决什么问题？

自由边界问题（FBP）里，未知量不只是物理场 $u$，还包括 $u$ 所在的区域 $\Omega_t$ 与边界 $\Gamma$。例如 Stefan 融化问题中，温度决定冰水界面的移动，而温度又只定义在该移动界面限定的区域内。普通神经算子通常假定输出函数定义在预先给定的固定紧集上；FBP 的输出域事先未知，因此不能直接套用这一假设（`paper.md:55-93`）。

FBNO 的核心贡献是把“移动域上的动力学”转换为“固定参考域 $\Omega_{\rm ref}$ 上的动力学”，再把结果映射回物理域。

### 两个算子

论文引入共轭关系

$$
\mathcal F^t=\mathcal H\circ\mathcal G^t\circ\mathcal H^{-1}.
$$

- $\mathscr H(u_0,\psi)=\chi$ 学习坐标映射：参考点 $\xi$ 在时刻 $t$ 到物理位置 $x=\chi(\xi,t)$。
- $\mathscr G(u_0,\psi)$ 学习固定参考域上的共轭场 $v(\xi,t)$。
- 预测时用 $\widehat{\mathscr H}^{-1}$ 找到物理点对应的参考点，再由 $\widehat{\mathscr G}$ 给出场值（论文 Eq. 3--7，`paper.md:109-127`）。

```text
初始条件 u0、外部函数 psi、参考坐标 (xi,t)
                |                 |
                |--> H-hat ------> chi(xi,t) = x
                |
                +--> G-hat ------> v(xi,t) -> u(x,t)
```

这相当于把“域怎样移动”和“域内物理量怎样演化”分开表示，但在最终输出处重新耦合。图 1 直接展示了共享 trunk、两个 branch 子网、映射嵌入以及内部/自由边界/微分同胚损失（`figure_01.png`）。

### 为什么需要微分同胚约束？

$\chi$ 必须可逆且可微，否则既无法稳定地从物理坐标回到参考坐标，也无法正确计算 PDE 导数。论文使用

$$
\det\left(\frac{\partial\chi}{\partial\xi}\right)>\delta>0
$$

来避免局部折叠或退化（Eq. 13，`paper.md:317-328`）。不同任务还能添加专门约束：Stefan 问题限制一维变形的 Jacobian；热--结构问题利用质量守恒；肿瘤问题另加 $\|\Delta\chi\|$ 与自编码器式可逆正则化（`paper.md:212-287`）。

### 怎样训练？

有数据时，可直接以 $u(x,t)$ 做监督学习，不必人工标注参考域到物理域的逐点对应。物理信息充分时，则用自动微分构造初值、固定边界、自由边界、PDE 与微分同胚损失的加权和（Eq. 16，`paper.md:329-379`）。网络采用 MIONet 风格：$u_0$ 与 $\psi$ 走 branch，$(\xi,t)$ 走 trunk，特征逐元素相乘并汇总（Eq. 24--25，`paper.md:465-478`）。

### 实验读法

- Stefan：图 2 显示三组温度/界面预测与参考解接近，论文报告平均相对 $L^2$ 误差约为 $u=0.0125$、$\Gamma_f=0.0072$（`figure_02.png`；`paper.md:212-217`）。
- 热--结构耦合：图 3 同时比较温度、密度、速度和映射；加入物理约束的 DD+PI 曲线优于纯数据驱动曲线（`figure_03.png`；`paper.md:218-256`）。
- 肿瘤生长：图 4 覆盖三类初始形状，预测边界与真值视觉上对齐；论文报告训练后 85 cases/s 的推理速率（`figure_04.png`；`paper.md:257-287`）。

### 代码与可复现性

本地仓库的 Stefan 实现直接输出 `phi`（映射）和 `out`（场），并对二者求导以组成 PDE/边界损失（`Stefan/model/stefan_model.py:23-50`，`Stefan/stefan_run.py:43-64,116-169`）。肿瘤实现也有映射预训练和冻结预训练模型后的场值训练。代码快照未包含 Zenodo 数据集或训练权重，关键脚本硬编码 CUDA 和 Windows 风格路径，因此这里验证的是方法结构与源代码对应，不是对论文数值的端到端复现。完整对应表见 `doc_code.md`。

### 适用边界

论文仅处理奇异性形成前、方程仍良定的平滑单相 FBP；多相系统需要额外的相间耦合设计。实际泛化还受数据量、优化局部极小值与训练/数据生成成本限制（`paper.md:293-301`）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Deep neural operator for free boundary problems

### Problem and contribution

Free-boundary problems jointly determine a physical field and the domain on which it is defined. This violates the fixed-output-domain assumption behind standard neural-operator approximation theory (`paper.md:55-93`). FBNO resolves this by learning a diffeomorphic coordinate map from a fixed reference domain and a conjugate-domain field operator, then composing them to predict the field on the moving physical domain (Eq. 3--7, `paper.md:109-127`).

The paper supplies a universal-approximation theorem under common-reference-domain/diffeomorphism assumptions and instantiates the idea with MIONet-style branch/trunk networks (`paper.md:128-174,465-478`). Geometry is protected by a positive Jacobian constraint; physics-informed, supervised, and hybrid learning are all supported (`paper.md:317-379`).

### Evaluation

The paper evaluates Stefan melting, a thermal--structural coupling problem, and tumour growth. In the Stefan example it reports most field errors within 1.5% and boundary errors below 1% over 300 test samples (`paper.md:212-217`; Fig. 2). For thermal--structural coupling it reports more than 95% lower test errors than a data-only approach (`paper.md:218-256`; Fig. 3). For tumour growth it uses 3,660 simulations across three initial geometries and reports a $10^4$ inference speed-up with 85 cases/s versus $1.6\times10^{-4}$ for the traditional baseline (`paper.md:257-287,395-399`; Fig. 4).

### Reproducibility

The article links GitHub, Zenodo, and Code Ocean (`paper.md:491-497`). This workspace contains the GitHub snapshot at commit `474baecdd93a848b96e518acc5fa2909518e632a`, plus a 105 KB Nature HTML conversion and four local figures. The checked Stefan code does implement a jointly predicted map/field and differentiable PDE/boundary losses; tumour code contains a frozen map-pretraining stage and supervised whole-model training. The snapshot has no downloaded datasets or checkpoints, hard-codes CUDA and Windows-style local paths in key entrypoints, and one Water data import/layout mismatch remains. Consequently, source correspondence is **medium fidelity** and no end-to-end result was reproduced.

### Scope

FBNO is aimed at smooth, well-posed, single-phase FBPs. The paper explicitly excludes post-singularity regimes and notes data scarcity, optimization, and total training/data-generation cost as limitations (`paper.md:293-301`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
