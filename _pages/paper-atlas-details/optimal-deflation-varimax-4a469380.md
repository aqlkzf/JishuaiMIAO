---
layout: default
permalink: /paper-atlas/optimal-deflation-varimax-4a469380/
title: "optimal_deflation_varimax"
nav: false
description: "考虑因子模型 其中 X\\in\\mathbb R^{p\\times n} 是 n 个样本的 p 维观测，\\Lambda\\in\\mathbb R^{p\\times r} 是载荷矩阵，Z\\in\\mathbb R^{r\\times n} 是潜在因子，E 是噪声。 PCA 能较好地估计由 \\Lambda 张成的 r 维子空间，却不能唯一决定子空间中的坐标轴：对任意正交矩阵 Q，\\Lambda Q 张成同一子空间、解释同样的方差。"
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
      <span>Representation Models</span>
      <span>arXiv preprint · 2025</span>
    </div>
    <h1>optimal_deflation_varimax</h1>
    <p>Optimal Vintage Factor Analysis with Deflation Varimax</p>
    <a class="paper-detail__doi" href="https://doi.org/arXiv:2310.10545" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 最优 Deflation Varimax 方法解读：先用 PCA 找子空间，再逐方向找可解释因子

### 1. 为什么 PCA 后还要旋转

考虑因子模型

$$
X=\Lambda Z+E,
$$

其中 $X\in\mathbb R^{p\times n}$ 是 $n$ 个样本的 $p$ 维观测，$\Lambda\in\mathbb R^{p\times r}$ 是载荷矩阵，$Z\in\mathbb R^{r\times n}$ 是潜在因子，$E$ 是噪声。

PCA 能较好地估计由 $\Lambda$ 张成的 $r$ 维子空间，却不能唯一决定子空间中的坐标轴：对任意正交矩阵 $Q$，$\Lambda Q$ 张成同一子空间、解释同样的方差。原始主成分经常把多个真实因子混在一起，因此数值上有效，科学上却难以解释。

经典 varimax 在这个 PCA 子空间内寻找一个旋转，使每个方向的载荷更“尖锐”：少数坐标大，多数坐标小。在 PCA 得到的行正交表示上，varimax 等价于最大化四阶量。但传统算法直接在 $r\times r$ 正交矩阵流形上同时求所有方向，目标高度非凸，实际迭代可能落到不理想的驻点，而且长期缺少对算法输出的有限样本保证。

这篇论文的贡献是把问题改写为逐方向求解，并证明在独立、正超额峰度因子等条件下，实际的球面投影梯度法能够恢复正确旋转；再与 PCA 组合，得到在中高信噪比下接近 minimax 最优的载荷估计器。

### 2. 第一步：PCA 只负责找信号子空间

对样本协方差做特征分解：

$$
\frac1nXX^\top=\sum_j d_jv_jv_j^\top.
$$

取最大的 $r$ 个特征值与特征向量，定义标准化主成分

$$
U_{(r)}=D_{(r)}^{-1/2}V_{(r)}^\top X\in\mathbb R^{r\times n},
$$

于是 $U_{(r)}U_{(r)}^\top=nI_r$。这一步把原来的 $p$ 维问题压到 $r$ 维，并把尺度标准化。后续 deflation varimax 只在这个小空间中寻找旋转，因此主要迭代成本由 $r$ 和 $n$ 决定，而不是反复处理全部 $p$ 维特征。

论文的 Theorem 1 进一步说明，主成分可以分解为

$$
U_{(r)}=R^\top(AZ/\sigma+N+\Omega).
$$

这里 $R^\top A$ 是需要通过旋转辨认的正交方向；$N$ 是由观测噪声投影形成的加性误差；$\Omega$ 是 PCA 特征值/特征向量估计带来的近似误差。这个分解很重要，因为它把第二步的难度拆成“真实独立因子 + 两类误差”，而不是假设 PCA 已经精确给出无噪声 ICA 数据。

### 3. 第二步：一个方向就是一个球面四阶优化

对单位球面 $\mathbb S^r=\{q:\|q\|_2=1\}$，论文定义

$$
F(q;U_{(r)})=-\frac{1}{12n}\|U_{(r)}^\top q\|_4^4.
$$

最小化 $F$ 等价于最大化投影 $q^\top U_t$ 的四阶矩。若潜在因子相互独立且具有正超额峰度，正确的独立方向会产生更大的四阶峰度，因而成为目标函数的优良极值方向。

它的球面 Riemannian gradient 为

$$
\operatorname{grad}F(q)
=-\frac{1}{3n}(I-qq^\top)
\sum_{t=1}^n(q^\top U_t)^3U_t.
$$

$I-qq^\top$ 把普通梯度投影到球面在 $q$ 处的切空间，避免更新沿半径方向浪费。一次 PGD 更新是

$$
q^{(\ell+1)}=P_{\mathbb S^r}
\left(q^{(\ell)}-\gamma\operatorname{grad}F(q^{(\ell)})\right),
$$

其中 $P_{\mathbb S^r}(x)=x/\|x\|_2$。

MATLAB 的 `function_code/L4_Grad.m` 计算未归一化的四阶上升方向

```matlab
M1 = Y' * A;
M2 = M1 .* M1 .* M1;
dA = 4 * Y * M2;
```

而 `GD_L4_Onecol.m` 再做

```matlab
q = q + eta_ini * (eye(p) - q*q') * g;
q = q / norm(q);
```

代码吸收了目标中的常数与符号：它沿四阶矩上升，而论文沿负四阶目标下降，方向一致；缩放被并入 `eta_ini`，不能直接把代码的 0.003 与论文某个 $\gamma$ 数字逐字比较。

### 4. “Deflation”真正特别在哪里

常见 sequential deflation 在求第 $k$ 个方向时，会强制它与之前的 $k-1$ 个估计方向正交。如果早期方向有误差，后续可行空间也随之倾斜，误差可能逐步放大。

本文的核心设计不同：每一行都求解同一个、没有显式历史正交约束的球面目标；已有方向主要用于产生落在剩余方向附近的初始化。得到 $r$ 个候选向量后，才统一投影到正交群：

$$
\check Q=\arg\min_{Q\in\mathbb O_{r\times r}}
\|\widehat Q-Q\|_F.
$$

若 $\widehat Q=U\Sigma V^\top$，答案就是 $UV^\top$。代码 `proj_orthogonal_group.m` 正是这一步。

`GD_L4.m` 中存在多个 `prob_type` 和投影分支，用于论文比较实验与变体；主要的 unconstrained 路径 `prob_type=4` 对每列调用同一 `GD_L4_Onecol`。为了发现不同方向，代码会把随机初始化投影到已发现方向的 null space，或用 method-of-moments 产生初始化；求解阶段本身不等同于传统的逐列硬约束优化。最后，外层实验脚本显式调用 `proj_orthogonal_group`。

### 5. 三种初始化方案

非凸优化不能忽略初值。论文分析三种实用方案。

#### 5.1 RI：单次随机初始化

在单位球面随机抽取 $q^{(0)}$。它最简单，但初始方向与某个真实列的相关通常只有 $1/\sqrt r$ 量级，所以可能需要更多迭代或重试。

#### 5.2 MRI：多次随机初始化

在剩余子空间生成多个随机候选，计算各自的四阶目标，选择 $\sum_t(q^\top U_t)^4$ 最大者。`GD_L4.m:64-69` 直接实现这一筛选。它用更多计算换更好的起点，但没有改变最终目标。

#### 5.3 MoMI：矩方法初始化

论文构造随机 slicing matrix $G$，并计算四阶矩矩阵

$$
\widehat M(G)=\frac{1}{3n}
\sum_t U_tU_t^\top(U_t^\top G U_t)-G-G^\top.
$$

对多个 $G$，选择第一、第二奇异值间隙最大的矩阵，再取其首个左奇异向量作为初始化。直觉是：大的谱隙意味着某一个真实方向在这次随机切片下被突出。

`initialization_MRS.m` 用页式矩阵乘法和 `pagesvd` 批量完成这一流程，并投影到剩余 null space。代码变量名沿用了 MRS/MoMI 的历史命名；关键应看式 (5.5) 的矩阵、谱隙选择与首奇异向量，而不是仅凭函数名判断。

图 4 显示 RI、MRI、MoMI 的最终误差曲线几乎重合；图 5 则显示在相同迭代数下 MRI/MoMI 前期更快。这说明初始化主要影响进入正确吸引域与收敛速度，不一定改变充分迭代后的统计误差。

### 6. 从旋转矩阵回到载荷矩阵

得到 $\check Q$ 后，论文构造

$$
\widehat\Lambda=
\frac{V_{(r)}D_{(r)}^{1/2}\check Q}
{\|V_{(r)}D_{(r)}^{1/2}\check Q\|_{\mathrm{op}}}.
$$

分子先把低维旋转方向映回原始 $p$ 维特征空间；分母固定模型的整体尺度，因为 $\Lambda Z=(c\Lambda)(Z/c)$ 本来存在缩放不识别性。

载荷只能识别到 signed permutation：因子顺序可以交换，每个因子也可以整体乘 $-1$。代码 `error3.m` 因而不是逐列直接相减，而是在符号与排列匹配后评估 Frobenius error。真实应用中同样不应把“第 1 因子”跨运行机械对应；应先做符号/排列对齐或依据载荷含义命名。

### 7. 理论保证依赖什么

#### 7.1 独立且 leptokurtic 的因子

Assumption 1 要求 $Z_j$ 相互独立、零均值、方差相同，并具有正超额峰度

$$
\kappa=\frac13\left(\frac{\mathbb E[Z_j^4]}{\sigma^4}-3\right)>0.
$$

稀疏的 Bernoulli-Gaussian 因子是典型例子。正峰度让四阶目标偏好真实因子轴；如果因子接近 Gaussian、彼此相关或具有负峰度，论文的识别逻辑与收敛保证不能直接套用。

#### 7.2 载荷条件数受控

Assumption 2 固定 $\sigma_1(\Lambda)=1$，并要求最小奇异值不太小。这排除了几乎线性相关、难以区分的载荷方向。

#### 7.3 噪声模型与样本规模

Assumption 3 以带协方差 $\Sigma_E$ 的 Gaussian 噪声陈述理论；作者说明多数结论可放宽到中心 sub-Gaussian 噪声。误差率同时依赖 $r/n$ 和 $\epsilon^2p/n$，所以“允许 $p>n$”不代表任意高维高噪声都可恢复，仍需有效 SNR 与规模条件。

论文把

$$
\omega_n=\sqrt{\frac{r\log n}{n}}+
\sqrt{\frac{\epsilon^2p\log n}{n}}
$$

作为 PCA 近似误差的主要尺度，并证明 deflation rotation 恢复正交方向到 signed permutation。PCA-dVarimax 在中高 SNR 下达到 minimax lower bound（至多差对数因子）；“optimal”指特定因子模型和损失下的 minimax 速率，不是所有数据集上都优于所有旋转算法。

### 8. 低信噪比与结构噪声修正

低 SNR 时，普通 PCA 的特征值包含噪声偏移，四阶目标的梯度也包含噪声协方差带来的偏置。Section 6 提出两层修正：

1. 改善 PCA 特征值/信号尺度估计，减少 $\Omega$；
2. 在 PGD 梯度中减去估计噪声协方差导致的偏置，减少 $N$ 对四阶方向的影响。

`GD_L4_Onecol.m:29-38` 从 PCA 尾部特征值估计 isotropic noise variance，并构造修正矩阵；`64-69` 在切空间投影前减去对应 bias term。图 7 中 PCA-dVarimax-1 只做第一层，PCA-dVarimax-2 两层都做；噪声增大时，完整修正的误差最低。

这项改进需要 $\Sigma_E$ 可估或具备合适结构。若真实噪声强烈异方差、相关结构未知，直接使用 isotropic 修正式未必可靠。

### 9. 如何读实验图

#### 图 1–2：旋转改变解释，不改变子空间

MNIST 图中，左侧 PCA 基向量是混合的灰度纹理，右侧旋转后出现清晰数字/笔画结构。散点图中，未旋转 PC 是近似圆形云，旋转后出现沿坐标轴的 radial streaks。两图说明“simple structure”的视觉含义，但不是定量证明。

#### 图 3：混合图像信号恢复

五个潜在源包含海鸟、城市天际线和三个噪声图。PCA-dVarimax 与完整修正版分别在不同 rotated PCs 中恢复两幅真实图像；PCA 保持混合，FastICA 与经典 varimax 只稳定恢复部分信号。该实验直观支持噪声条件下的旋转质量，但样例规模小，不能替代广泛真实数据评估。

#### 图 4–5：初始化

图 4 随 $n,r,p,\epsilon^2$ 改变时三种初始化的最终误差几乎一致。图 5 显示迭代较少时 RI 误差更高，MoMI/MRI 更快到达稳定区。

#### 图 6：方法比较

PCA-dVarimax 与经典 varimax 在部分模拟条件下接近，且明显优于无旋转 PCA、sparse PCA 和两个 FastICA 变体。曲线支持方法的稳健性，但“理论 minimax optimal”来自 upper/lower bound，不是从这一组曲线本身推导。

#### 图 7：结构噪声改进

随着 $\epsilon^2$ 增大，两步修正带来的收益扩大；随 $p$ 增大时三者差距先缩小再可能变化，反映理论条件中 $p,n,\epsilon$ 的共同作用。

### 10. MATLAB 代码与论文的对应

| 论文组成 | 本地实现 | 判断 |
|---|---|---|
| 单方向四阶梯度 | `function_code/L4_Grad.m` | Exact，常数吸收到步长 |
| 球面 Riemannian PGD | `function_code/GD_L4_Onecol.m` | Exact core |
| 逐方向外循环与去重 | `function_code/GD_L4.m` | Exact core，含实验开关 |
| MRI 的多随机候选 + 四阶筛选 | `GD_L4.m:64-69` | Exact |
| MoMI / Eq. (5.5) 谱隙初始化 | `initialization_MRS.m` | Exact core |
| 最终 SVD 正交化 | `proj_orthogonal_group.m` | Exact |
| signed-permutation error | `error3.m` | Exact evaluation |
| 低 SNR 梯度偏置修正 | `GD_L4_Onecol.m` | Exact core |
| Algorithm 2 完整实验管线 | `compare_method.m` 等顶层脚本 | Partial-to-Exact |
| 论文停止准则/理论迭代预算 | 实验多用固定 `MaxIter1`，部分 early stop 使用 ground truth | Partial |
| 通用用户级 API、自动选 $r$、单元测试 | 未提供 | Not found |

代码是论文实验仓库，不是整理好的统计软件包。`GD_L4` 要求传入 `A_gt`，主要用于维度和实验误差/early-stop 逻辑；在正常固定迭代、关闭 ground-truth early stop 时，核心更新不需要真实载荷。复用者应把算法主体与仿真实验控制参数拆开，并自行实现数据检查、选秩、收敛准则和稳定性评估。

### 11. 实际使用建议与边界

1. 先用 scree plot、parallel analysis、交叉验证或领域知识选 $r$；算法本身不解决秩选择。
2. 对输入做中心化，并确认样本列/特征行方向；代码大量函数假定 $X$ 为 $p\times n$。
3. 同时运行多个初始化，检查载荷经 signed permutation 对齐后的稳定性。
4. 检查旋转分数的峰度、独立性和 sparsity；若因子明显相关，orthogonal varimax 可能不合适，应考虑 oblique rotation 或其他模型。
5. 不要把“载荷更稀疏”自动解释成真实生物通路或因果模块；需要外部注释、重复数据和下游验证。
6. 对高噪声数据，只有在噪声协方差结构可合理估计时才使用论文的修正版。

这篇论文最重要的思想是把“PCA 找子空间”和“高阶统计选择坐标轴”明确分开：PCA 保留主要二阶结构，deflation varimax 利用独立 leptokurtic 因子的四阶结构确定可解释方向。它提供的是特定模型条件下可证明的旋转与载荷恢复，而不是无需检查假设的通用解释器。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Optimal Vintage Factor Analysis with Deflation Varimax

**Authors**: Xin Bing (U. Toronto), Xin He (SHUFE), Dian Jin & Yuqian Zhang (Rutgers)
**arXiv**: 2310.10545v4 (April 2025)
**Code**: https://github.com/Jindiande/optimal_deflation_varimax

---

### Executive Summary

This paper provides **the first provably optimal algorithm** for the classical "PCA + varimax rotation" pipeline. The key innovation is a **deflation approach** that computes one rotation direction at a time, rather than optimizing all rotations simultaneously over the Stiefel manifold.

#### Core Problem

Given high-dimensional data $\mathbf{X} = \mathbf{\Lambda Z} + \mathbf{E}$:
- $\mathbf{\Lambda} \in \mathbb{R}^{p \times r}$: loading matrix (the target)
- $\mathbf{Z} \in \mathbb{R}^{r \times n}$: latent factors with independent, leptokurtic entries
- $\mathbf{E}$: additive Gaussian noise

**Goal**: Estimate $\mathbf{\Lambda}$ (up to signed permutation) with provable statistical guarantees.

#### Why This Matters

| Traditional PCA + Varimax | This Paper's Approach |
|---------------------------|----------------------|
| No theoretical guarantee | Minimax optimal rates |
| May get stuck in local optima | Provable convergence |
| Requires expensive Stiefel optimization | Sequential, efficient computation |
| Ambiguous statistical meaning | Rigorous identifiability |

---

### Motivation & Novelty

#### The "PCA + Varimax" Dilemma

1. **PCA alone**: Finds optimal low-rank approximation but factors are orthogonal mixtures—not interpretable
2. **Varimax rotation**: Seeks "simple structure" (sparse loadings) but requires solving:
   $$\max_{\mathbf{Q} \in \mathbb{O}_{r \times r}} \sum_{k=1}^{r} \sum_{i=1}^{n} \left[\mathbf{Q}\mathbf{U}_{(r)}\right]_{ki}^4$$
   This is **non-convex** over orthogonal matrices with many local optima.

#### Key Insight: Deflation

Instead of optimizing $r \times r$ orthogonal matrix at once, solve **one row at a time**:
$$\min_{q \in \mathbb{S}^r} -\|\mathbf{U}_{(r)}^\top q\|_4^4$$

**Why this works**:
- Each subproblem is optimization on the unit sphere (simpler geometry)
- Use projected gradient descent with theoretical guarantees
- Final orthogonalization via SVD

---

### Method Overview

#### Two-Step Pipeline

```
Step 1: PCA                    Step 2: Deflation Varimax
─────────────────             ──────────────────────────
X ──→ SVD ──→ U_(r)           U_(r) ──→ solve L4 problem r times ──→ Q̂ ──→ orthogonalize ──→ Q̌
     ↓                              ↓
V_(r), D_(r)                   Λ̂ = V_(r) D_(r)^{1/2} Q̌ / ||·||_op
```

#### Algorithm 1: Deflation Varimax Rotation

```
Input: U_(r) ∈ R^{r×n}, number of factors s
Output: Q̌ ∈ O_{r×s}

For k = 1 to s:
    1. Initialize q_k^(0) (random or Method of Moments)
    2. Run PGD until convergence:
       q_k^(ℓ+1) = P_{S^r}(q_k^(ℓ) - γ · grad F(q_k^(ℓ); U_(r)))
    3. Store Q̂_k = q_k^(final)

Orthogonalize: Q̌ = UV^T where Q̂ = UΣV^T
```

#### Algorithm 2: PCA with Deflation Varimax

```
Input: X ∈ R^{p×n}, number of factors r
Output: Λ̂ ∈ R^{p×r} with σ_1(Λ̂) = 1

1. Compute eigendecomposition: (1/n)XX^T = Σ d_j v_j v_j^T
2. Extract: V_(r), D_(r) (top r eigenvectors/values)
3. Compute: U_(r) = D_(r)^{-1/2} V_(r)^T X
4. Apply Algorithm 1 to get Q̌
5. Return: Λ̂ = V_(r) D_(r)^{1/2} Q̌ / ||V_(r) D_(r)^{1/2} Q̌||_op
```

---

### Theoretical Contributions

#### 1. PC Decomposition (Theorem 1)

$$\mathbf{U}_{(r)} = \mathbf{R}^\top (\mathbf{AZ}/\sigma + \mathbf{N} + \mathbf{\Omega})$$

where:
- $\mathbf{R}$: unknown random rotation
- $\mathbf{N} = \mathbf{S}^{-1}\mathbf{L}^\top\mathbf{E}/\sigma$: additive error from noise
- $\mathbf{\Omega}$: approximation error with $\|\mathbf{\Delta}\|_{\text{op}} \lesssim \omega_n + \epsilon^2$

#### 2. Optimization Landscape (Theorem 2)

Any stationary point $q$ satisfying alignment conditions estimates a column of $\mathbf{A}$ up to sign:
$$\min\{\|q - A_i\|_2, \|q + A_i\|_2\} \lesssim \omega_n + \epsilon^2$$

#### 3. Minimax Optimality (Theorems 5 & 6)

**Upper bound** (PCA-dVarimax):
$$\|\widehat{\mathbf{\Lambda}} - \mathbf{\Lambda}\mathbf{P}\|_F = \mathcal{O}_{\mathbb{P}}\left(\sqrt{\frac{r^2}{n}} + \sqrt{\frac{\epsilon^2 pr}{n}}\right)$$

**Lower bound** (minimax):
$$\inf_{\widehat{\mathbf{\Lambda}}} \sup_{\mathbf{\Lambda}} \mathbb{P}\left\{\|\widehat{\mathbf{\Lambda}} - \mathbf{\Lambda}\|_F \geq c\sqrt{\frac{r^2}{n}} + c\sqrt{\frac{\epsilon^2 pr}{n}}\right\} \geq c'$$

**Conclusion**: PCA-dVarimax achieves the minimax optimal rate.

---

### Key Assumptions

| Assumption | Description | Biological Interpretation |
|------------|-------------|---------------------------|
| **A1: Independent leptokurtic factors** | $Z_j$ independent with excess kurtosis $\kappa > 0$ | Gene programs have sparse, non-Gaussian activation |
| **A2: Bounded condition number** | $\sigma_r(\mathbf{\Lambda}) \geq c_\Lambda > 0$ | All factors contribute meaningfully |
| **A3: Gaussian noise** | $E \sim \mathcal{N}_p(0, \sigma^2\epsilon^2\mathbf{\Sigma}_E)$ | Technical convenience, relaxable |

---

### Initialization Schemes

#### Random Initialization (Section 5.1)
- Project random vector onto null space of previously found directions
- Requires $r^{5-13} \ll n$ depending on $\delta$
- Simple but slower convergence

#### Method of Moments (Section 5.2)
- Use 4th-moment tensor structure to find good starting point
- Compute: $\widehat{\mathbf{M}}(\mathbf{G}) = \frac{1}{3n}\sum_t U_t U_t^\top (U_t^\top \mathbf{G} U_t) - \mathbf{G} - \mathbf{G}^\top$
- Select $\mathbf{G}$ maximizing singular value gap
- Requires only $r(\omega_n + \epsilon^2) \leq c$
- **Recommended** for practical use

---

### Improvements for Structured Noise (Section 6)

When $\mathbf{\Sigma}_E = \mathbf{I}_p$:

#### Step 1: Improved PCs
Replace $\mathbf{D}_{(r)}$ with $\widehat{\mathbf{D}}_{(r)} = \mathbf{D}_{(r)} - \widehat{\epsilon^2\sigma^2}\mathbf{I}_r$

#### Step 2: Modified PGD
Add bias correction to gradient:
$$\widehat{\text{grad}} F = \text{grad} F + (1 + q^\top\widehat{\mathbf{\Sigma}}_N q)\mathbf{P}_q^\perp \widehat{\mathbf{\Sigma}}_N q$$

**Result**: Achieves optimal rate $\omega_n\sqrt{r}$ in **all SNR regimes**.

---

### Evaluation Summary

#### Datasets
1. **MNIST handwritten digits**: 8000 images, 784 pixels, r=49 factors
2. **Mixed images**: 2 signal + 3 noise images, 100 linear combinations

#### Compared Methods
- PCA (no rotation)
- Varimax (classical, no guarantee)
- FastICA (tensor-based)
- Sparse PCA (ADMM)

#### Key Results

| Experiment | Best Performer | Finding |
|------------|---------------|---------|
| Basis learning (MNIST) | PCA-dVarimax | Learns interpretable digit parts |
| Signal recovery | PCA-dVarimax-2 | Only method recovering both signals |
| Simulation (varying n,p,r,ε) | PCA-dVarimax | Consistently lowest error |

---

### Reproducibility Assessment

| Criterion | Rating | Notes |
|-----------|--------|-------|
| **Code availability** | ✓ Complete | MATLAB implementation provided |
| **Data availability** | ✓ | MNIST public; synthetic data generated |
| **Algorithm description** | ✓ Excellent | Pseudocode in paper |
| **Hyperparameters** | ✓ Specified | Step size γ=10⁻⁵, tolerance 10⁻⁶ |
| **Environment** | ⚠ Partial | MATLAB version not specified |

**Overall Reproducibility Score: 4/5**

#### Potential Blockers
- MATLAB-only implementation (no Python)
- Requires `rotatefactors` from Statistics Toolbox for comparison
- Large-scale experiments may need significant compute time

---

### Practical Takeaways

1. **When to use**: Factor analysis where interpretability matters (gene programs, image features)
2. **Key advantage**: Theoretical guarantees unlike classical varimax
3. **Computational**: O(r × n × iterations) per factor, linear in data size
4. **Initialization**: Use Method of Moments for best results
5. **Structured noise**: If noise covariance is known/estimable, use improved version

---

### Citation

```bibtex
@article{bing2025optimal,
  title={Optimal vintage factor analysis with deflation varimax},
  author={Bing, Xin and He, Xin and Jin, Dian and Zhang, Yuqian},
  journal={arXiv preprint arXiv:2310.10545v4},
  year={2025}
}
```

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
