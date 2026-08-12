---
layout: default
permalink: /paper-atlas/flashdeconv-6d553648/
title: "FlashDeconv"
nav: false
description: "FlashDeconv 要回答的是：每个空间测量 bin 中，各细胞类型分别占多少。它先从空间数据和单细胞参考中挑出有用基因，再把数千个基因随机压缩到默认 512 个特征，在压缩空间中求带空间平滑和稀疏约束的非负回归。关键卖点不是一种新的概率生成模型，而是用 leverage score 加权 CountSketch 与稀疏邻接图，把主要计算量做成对 bin 数 N 近似线性增长。"
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
      <span>Deconvolution</span>
      <span>bioRxiv · 2025</span>
    </div>
    <h1>FlashDeconv</h1>
    <p>FlashDeconv enables atlas-scale, multi-resolution spatial deconvolution via structure-preserving sketching</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2025.12.22.696108" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## FlashDeconv 方法解读：为什么“压缩基因维度”能把空间解卷积扩展到百万级 bin

### 一句话理解

FlashDeconv 要回答的是：每个空间测量 bin 中，各细胞类型分别占多少。它先从空间数据和单细胞参考中挑出有用基因，再把数千个基因随机压缩到默认 512 个特征，在压缩空间中求带空间平滑和稀疏约束的非负回归。关键卖点不是一种新的概率生成模型，而是用 leverage score 加权 CountSketch 与稀疏邻接图，把主要计算量做成对 bin 数 $N$ 近似线性增长。

### 输入与输出

输入包括：空间表达矩阵 $Y\in\mathbb R^{N\times G}$、按细胞类型聚合的参考签名 $X\in\mathbb R^{K\times G}$ 和坐标 $C\in\mathbb R^{N\times2}$。公开便捷 API 也能从两个 AnnData 对象提取共享基因和参考均值。

核心优化得到非负丰度 $\beta\in\mathbb R_+^{N\times K}$；随后逐行归一化为比例。它不输出单细胞位置，也不把一个 bin 硬分类成单一类型。`beta_` 是未归一化系数，`proportions_` 才是行和为 1 的组成。

### 第一阶段：HVG 与参考 marker 的并集

空间矩阵先按 library size 做 log-CPM，再依据均值分箱后的标准化离散度选默认 2000 个 HVG。参考矩阵按每个类型的相对表达，使用“最高类型与第二高类型之差”选每类默认 50 个 marker。两者取并集：HVG 保留空间数据中变化大的信号，marker 防止只靠方差漏掉罕见类型。

这里的 marker 是由类型平均签名算出的，不等同于单细胞差异表达检验；参考标签质量和缺失类型会直接传入结果。

### 第二阶段：leverage score 表示什么

论文把参考矩阵的右奇异向量写成 $V$，基因 $g$ 的 leverage score 为

$$
\ell_g=\sum_{j=1}^{r}V_{gj}^{2}.
$$

直观上，方差问“这个基因有多响”，leverage 问“这个基因是否定义了参考签名空间中难以被其他方向替代的一条轴”。因此低丰度类型的特异 marker 即使总体方差不高，也可能得到高 leverage。图 2 的降采样、GOLD/NOISE 象限、GO 富集和空间结构实验是论文对这一主张的证据。

当前代码并非逐字使用论文公式：`compute_leverage_scores` 先对原始参考签名按基因中心化，再对 $X^\top$ 做 SVD，并以 $s_j^2/(s_j^2+\epsilon)$ 加权 $U$ 行平方；论文描述的是预处理后 $\tilde X$ 的未加权右奇异向量行范数。二者目的相近，但必须标为 Partial。

### 第三阶段：加权 CountSketch

每个入选基因只被哈希到一个压缩维度，并随机乘正负号：

$$
\Omega_{g,j}=\begin{cases}
s_gw_g,&j=h(g),\\
0,&\text{otherwise},
\end{cases}
\qquad
w_g=\sqrt{p_gG},\quad p_g=\frac{\ell_g}{\sum_{g'}\ell_{g'}}.
$$

于是

$$
Y_{\text{sketch}}=\tilde Y\Omega,\qquad
X_{\text{sketch}}=\tilde X\Omega.
$$

高 leverage 基因在哈希碰撞中被放大，减少被高表达公共基因淹没的风险。代码还把幅度截断到 `[0.1, 10]`，并按每个实际哈希桶的范数重新缩放到 $\sqrt{G/d}$；这些是论文主公式未写出的稳定化细节。投影后 $Y_{\text{sketch}}$ 会转成稠密 $N\times d$ 数组，因此内存仍是 $O(Nd)$，所谓线性扩展不代表常数成本为零。

### 第四阶段：空间图

默认从坐标构建 $k=6$ 的 kNN 图，并对有向近邻关系取并集得到无向邻接矩阵 $A$。图拉普拉斯为

$$
L=D-A.
$$

空间惩罚

$$
\operatorname{Tr}(\beta^TL\beta)
$$

等价于让相邻 bin 的组成更接近。它借邻居降低低深度噪声，但也可能把真实的尖锐边界和小生态位抹平。默认 `lambda="auto"` 用

$$
\lambda=0.005\frac{\overline G}{\operatorname{mean}(\deg A)},
\qquad \overline G=\operatorname{mean}(\operatorname{diag}(X_sX_s^T))
$$

匹配数据项的尺度。

### 第五阶段：求解非负空间回归

目标函数是

$$
\min_{\beta\ge0}
\frac12\lVert Y_s-\beta X_s\rVert_F^2
+\frac\lambda2\operatorname{Tr}(\beta^TL\beta)
+\rho\lVert\beta\rVert_1.
$$

代码预计算 Gram 矩阵 $X_sX_s^T$ 和交叉项 $X_sY_s^T$。每次迭代从旧 buffer 读所有 spot，以 Jacobi 方式并行写入新 buffer；每个系数结合本 bin 的残差、相邻 bin 同类型丰度、非负投影和 L1 阈值更新。Numba 让内层循环接近编译代码速度。单次迭代复杂度约为 $O(NK(K+k))$，在 $K$、$k$ 固定时对 $N$ 线性。

不过，论文将这种 Jacobi 式并行更新称为 BCD 并声称凸问题全局收敛；标准逐坐标下降的收敛结论不能自动证明任意同步 Jacobi 更新都收敛。代码以最大相对变化为停止条件，最多 100 轮，实践收敛与理论保证应分开表述。

### 七张主图的证据层级

- 图 1：算法示意，不是性能证据。
- 图 2：leverage 与丰度解耦的机制证据，包括降采样、基因象限、GO 和 Visium 空间结构。
- 图 3：Spotless 56 个 Silver Standard 数据集的准确度及合成规模扩展。FlashDeconv 的指标来自作者运行，竞争方法取官方 Spotless 结果；这不是同一代码环境下重新运行所有方法。运行时间来自 M2 Max。
- 图 4：三位 CRC 患者、约 159.6 万个 8 µm bin 的应用。FlashDeconv 对所有 bin 给连续比例，而 RCTD doublet 模式会分类、拒绝或限制类型数；“100% coverage”主要是输出形式差异，不能单独等价为更准确。19/22 marker 方向一致是间接验证。
- 图 5：由预测中性粒细胞比例定义热点，再分析其邻域和 marker 富集。marker 与 UMI 分层增加可信度，但热点和生态位仍依赖模型输出。
- 图 6：同一肠组织逐级聚合，展示 8–16 µm 间纯度和边界锐度快速下降，以及 Paneth–Goblet 相关符号反转。它证明聚合尺度可改变统计结论；“resolution horizon”是该组织/分析定义下的经验范围，不是所有平台的通用常数。
- 图 7：预测 Tuft 热点附近 stem 和 enteroendocrine 富集。15.3 倍是模型比例与置换检验结果，不是直接成像计数；应视为待实验验证的生态位假设。

### 论文的强证据与弱证据

强证据是已知比例的合成 Spotless benchmark、Xenium 辅助验证和明确的运行硬件/规模报告。较弱证据是 CRC 与 Tuft 的发现性分析，因为热点定义、组成和邻域都来自同一套解卷积结果；marker 富集能提供正交支持，却不能完全排除参考偏差或空间平滑造成的结构。

论文是 bioRxiv 预印本，未经同行评议。当前 OCR 文本还出现 DOI/版本信息混入 Data Availability 的排版异常，因此书目信息应以工作区元数据和原始 PDF 为边界，不应把 OCR 中的每处文字都当作可靠元数据。

### 当前代码快照的匹配判断

总体为 **Partial-to-High**：主链——Log-CPM、HVG+marker、加权 CountSketch、稀疏 kNN、图拉普拉斯目标、Numba/Jacobi 求解和行归一化——都存在。明确差异包括：leverage 的输入和加权公式、幅度截断与桶归一化、未在论文中说明的 Pearson `theta=100`，以及同步更新收敛保证的表述边界。

本工作区代码目录没有嵌套 `.git`，也没有 `.repo_source`，因此无法从本地文件确认采集 commit。父 PaperCode 的 HEAD 不是 FlashDeconv 代码版本，不能填作上游提交号。

### 实际使用时应记录什么

至少记录共同基因、参考类型及聚合方式、HVG/marker 数量、随机种子、sketch 维度、图构建方式、$k$、实际 `lambda_used_`、$\rho$、迭代次数和是否收敛。要判断结果是否被过度平滑，应与 `lambda_spatial=0`、多个 $k$ 和多个随机种子比较；对稀有类型发现，还要回看原始 marker 表达和独立成像/原位证据。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## FlashDeconv 论文与代码复核摘要

### 结论

FlashDeconv 是面向超大空间转录组的参考型细胞组成解卷积：它以 HVG 与参考 marker 选基因，以 leverage 加权 CountSketch 压缩基因轴，再用稀疏空间图正则化的非负回归估计每个 bin 的连续细胞类型比例。固定细胞类型数、邻居数和 sketch 维度时，迭代成本随 bin 数近似线性。

论文在 Spotless 合成基准中报告平均 Pearson 0.944，并在 M2 Max 上报告百万级 bin 的分钟级运行；CRC 三患者 1,595,565 个 bin 的处理时间为 153 秒。真实组织应用展示中性粒细胞微域、8–16 µm 的经验“resolution horizon”和 Tuft–Stem 候选生态位。这些真实数据结果主要是模型推断与 marker/外部数据一致性证据，不是直接细胞计数验证。

### 最重要的阅读边界

- “100% bin coverage”表示连续回归对每个 bin 都输出比例，和 RCTD doublet 分类的 coverage 定义不同，不能单独解释成准确率优势。
- 竞争方法基准值来自官方 Spotless 结果，未必是同硬件、同代码版本的并行重跑。
- 8–16 µm resolution horizon 是小鼠肠数据上的经验结果，不是通用物理常数。
- Tuft–Stem 15.3 倍富集和 CRC 微域是需要独立实验验证的假设。
- 论文是 bioRxiv 预印本，尚未同行评议。

### 代码匹配

**Partial-to-High。** 主算法模块完整存在，但不是“逐公式完全一致”：

- 论文在预处理后的参考矩阵上用未加权右奇异向量 leverage；代码在原始选定参考签名上中心化，对 $X^T$ 做 SVD，并用奇异值权重修正。
- CountSketch 代码额外把权重截断到 `[0.1, 10]`，再按实际桶范数缩放。
- 可选 Pearson 模式硬编码 `theta=100`，论文未给出该值。
- 求解器采用同步 Jacobi 双缓冲更新；实践停止条件存在，但不能直接把标准顺序 BCD 的全局收敛结论无条件移植过来。

### 复现性

本地包有单元/集成测试和清晰 API，但工作区未包含论文完整 reproducibility 仓库或全部数据，也没有执行论文七张图的端到端重算。代码目录缺少嵌套 `.git` 与 `.repo_source`，无法确认上游 commit；父仓库 HEAD 不可作为替代。

### 来源

- 论文：`paper source/paper/auto/paper.md`
- 主图：`paper source/paper/auto/images/`
- 原始 PDF：`paper.pdf`
- 代码：`code/`
- 预印本 DOI：`10.64898/2025.12.22.696108`

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
