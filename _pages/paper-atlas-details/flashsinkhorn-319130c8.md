---
layout: default
permalink: /paper-atlas/flashsinkhorn-319130c8/
title: "FlashSinkhorn"
nav: false
wide: true
description: "给定带权点云 X\\in\\mathbb{R}^{n\\times d},a\\in\\Delta^n 与 Y\\in\\mathbb{R}^{m\\times d},b\\in\\Delta^m，熵正则最优传输（EOT）寻找耦合 P，使运输代价和熵正则的 KL 项之和最小。平方欧氏代价为 C{ij}=\\lVert xi-yj\\rVert2^2。传统 GPU 实现往往显式保存 n\\times m 的代价、分数或耦合矩阵；"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>FlashSinkhorn</h1>
    <p>FlashSinkhorn: IO-Aware Entropic Optimal Transport on GPU</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2602.03067" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for FlashSinkhorn">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ot-triton-lab/flash-sinkhorn" target="_blank" rel="noopener noreferrer" aria-label="Open code for FlashSinkhorn">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## FlashSinkhorn：把 Sinkhorn 写成流式注意力

### 它要解决什么问题？

给定带权点云 $X\in\mathbb{R}^{n\times d},a\in\Delta^n$ 与 $Y\in\mathbb{R}^{m\times d},b\in\Delta^m$，熵正则最优传输（EOT）寻找耦合 $P$，使运输代价和熵正则的 KL 项之和最小。平方欧氏代价为 $C_{ij}=\lVert x_i-y_j\rVert_2^2$。传统 GPU 实现往往显式保存 $n\times m$ 的代价、分数或耦合矩阵；当样本数大时，这既占显存又造成大量 HBM 读写。

论文比较的 GeomLoss tensorized、GeomLoss/KeOps 和 OTT-JAX 都能处理相关问题，但前者会受稠密矩阵限制，后两者没有采用本文针对该归约结构的融合内核。这里的比较背景和实验设置见 `paper.md:282-342`；

### 核心观察：Sinkhorn 半步就是带偏置的注意力式 LSE

标准 Sinkhorn 在对数域更新两个对偶势 $f,g$。令

$$\alpha_i=\lVert x_i\rVert^2,quad \beta_j=\lVert y_j\rVert^2,quad
Q=\sqrt2X,quad K=\sqrt2Y,$$

并把势移位为 $\hat f=f-\alpha$、$\hat g=g-\beta$。再令 $\delta=\varepsilon\log b$、$\gamma=\varepsilon\log a$，则

$$S_X(\hat g)=\big(QK^T+\mathbf1_n(\hat g+\delta)^T\big)/\varepsilon,qquad
\hat f\leftarrow-\varepsilon\operatorname{LSE}_{row}(S_X).$$

$\hat g$ 的更新只需交换 $X,Y$ 与相应偏置。也就是说，平方欧氏距离中的范数项被吸收到移位势，留下的是点积、列偏置和按行 log-sum-exp；这正是 FlashAttention 擅长的计算形状（`paper.md:123-142`）。

```text
输入 X,Y,a,b,epsilon
  -> 求平方范数、log 权重、初始化 hat f/hat g
  -> 固定一个 X 的行块到 SRAM
  -> 逐块流入 Y：计算点积 + 偏置，在线更新 max 与 exp-sum
  -> 写出该行块的新 hat f；反向同理得到 hat g
  -> 得到势、OT 损失或后续的 P@V / 梯度 / HVP
```

因此不会把完整 $n\times m$ 分数矩阵写进 HBM。论文的理论 IO 复杂度和单融合 Triton 内核说明见 `paper.md:145-157`。当前代码的 `flashsinkhorn_lse` 正是这个接口：它计算带 $2\,cost\_scale\,x y^T$ 的 LSE，并在内核内使用原始坐标，而不是额外分配 $Q,K$（`flash-sinkhorn/src/flash_sinkhorn/kernels/sinkhorn_flashstyle_sqeuclid.py:811-923`）。

### 两种迭代方式

- **交替式（alternating）**：先更新一个势，再用新势更新另一个势，等价于 Gauss--Seidel；实现需要每次迭代两个 kernel launch（`sinkhorn_solvers.py:57-64,191-220`）。
- **对称式（symmetric）**：从同一份旧势独立计算两个半步并平均；代码提供单融合步骤以减少启动开销（`kernels/sinkhorn_flashstyle_sqeuclid.py:1089-1123`）。

两者解决的是同一类 EOT 问题，但调度和性能取舍不同；论文在小规模时偏好 symmetric、在大规模/高维时观察到 alternating 更有利（`paper.md:313-319`）。

### 不显式构造 $P$，怎样得到梯度？

对任意当前势，

$$P_{ij}=a_ib_j\exp\left[(\hat f_i+\hat g_j+(QK^T)_{ij})/\varepsilon\right].$$

FlashSinkhorn 把 $PV$ 做成一次流式“softmax 加权求和”，并在最后乘上行边缘校正；同一接口也能算 $P^TU$（`paper.md:180-206`）。代码 `apply_plan_mat_flashstyle` 的 `axis=1` 和 `axis=0` 分别实现两种方向，且其 Triton 内核保持在线归一化统计量（`kernels/apply_flash.py:360-417,489-510`；`:84-201`）。在收敛时，这给出重心投影 $T_\varepsilon(X)$，从而

$$\nabla_X\mathrm{OT}_\varepsilon=2\operatorname{diag}(a)\big(X-T_\varepsilon(X)\big).$$

如果提前停止，代码用当前耦合诱导出的边缘质量，而不是把它误当成严格满足 $a,b$ 的最优耦合（`paper.md:1253-1260`; `hvp.py:322-357`）。

### 二阶信息：HVP

完整 Hessian 太大，但 Newton-CG 或 Lanczos 常只需要 $\mathcal{T}A$。论文把它分解为若干 $P$、$P^T$、矩阵应用和一个 Hadamard 加权 transport，再以 CG 解 Schur 补系统；目标工作内存为 $O((n+m)d)$（`paper.md:244-279`）。代码先通过流式 operator 求诱导边缘，再把这些 operator 组合成 Schur matvec（`hvp.py:302-400`）；`hvp_x_sqeuclid` 是端到端入口（`hvp.py:626-693`）。

### 证据、适用范围与复现边界

图 1--2 直接画出了行块驻留、键块流入及在线累积；图 3--8 展示论文报告的速度/内存、OTDD 和鞍点逃逸趋势，均已在本地逐图阅读。`SamplesLoss` 明确要求 CUDA tensor（`samples_loss.py:533-544`）。补充 Markdown 在此次 arXiv HTML 获取中为 **Not found**。此外，融合推导只覆盖可写成“逐点项 + 点积”的代价；原始非平方欧氏距离和任意神经网络代价不在论文的声明范围内（`paper.md:160-163`）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## FlashSinkhorn

### What problem does it solve?

Entropic optimal transport (EOT) is useful for point-cloud matching, OT dataset distance (OTDD), and OT-based optimization, but dense GPU implementations commonly create $n\times m$ cost, score, or coupling intermediates. That makes memory quadratic and repeatedly moves large arrays through HBM. Existing online approaches avoid some storage but, according to the paper's comparison, do not specialize the reduction as aggressively; tensorized methods are fast only while dense intermediates fit (`paper.md:282-325`).

### Method

FlashSinkhorn recasts squared-Euclidean Sinkhorn as biased dot-product log-sum-exp reductions. After shifting the potentials by point norms, each half-step is a FlashAttention-shaped tiled operation: retain a query row block and online LSE statistics in SRAM, stream key blocks, and write only the final potential tile. It also streams $PV$/$P^TU$ and builds an HVP using those plan applications inside a Schur-complement CG solve (`paper.md:120-157,180-279`). The method applies to costs with an affine dot-product decomposition; raw Euclidean and arbitrary learned costs are outside the stated fused scope (`paper.md:160-163`).

### Evaluation

The paper benchmarks on an NVIDIA A100-80GB against GeomLoss (tensorized/KeOps) and OTT-JAX. It reports 9--32x forward speedup over KeOps, up to 161x end-to-end at $d=512$, and linear resident-memory scaling, with HVP speedups of 3--6x at $d=64$ and up to 25x at $d=128$ in the stated tests (`paper.md:297-342`). The downstream plots cover MNIST--Fashion-MNIST OTDD and a 40k-cell shuffled-regression saddle-escape workflow (`paper.md:348-393`). These are paper-reported results, not independently reproduced results.

### Reproducibility assessment

The workspace includes the linked GitHub snapshot (commit `d538da39a148d44b3956e018a72cd982854b976a`) and direct source confirms the central shifted-potential kernels, streamed plan application, and HVP path. `SamplesLoss` is CUDA-only, and benchmark/test modules are present. Overall code-paper fidelity for the core squared-Euclidean path is **high**. However, no local GPU run was performed, no packaged command reproducing every paper table was found in the searched repository, and supplementary markdown was **Not found** in the arXiv HTML acquisition. Treat performance and numerical-parity claims as unreplicated.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
