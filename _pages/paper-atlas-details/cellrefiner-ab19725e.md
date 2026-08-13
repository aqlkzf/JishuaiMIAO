---
layout: default
permalink: /paper-atlas/cellrefiner-ab19725e/
title: "CellRefiner"
nav: false
wide: true
description: "CellRefiner 不从 Visium spot 中真正测出每个细胞的位置。它把配对的 scRNA-seq 细胞先分配到 spot，再把这些细胞当作粒子，在组织边界、细胞间距和表达相似性等约束下移动；随后可把每个细胞展开成多个亚细胞元素，得到用于接触图和配体–受体分析的预测几何。输出是模型重建，不是成像分割或实验测量。"
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
      <span>Deconvolution</span>
      <span>Nature Communications · 2026</span>
    </div>
    <h1>CellRefiner</h1>
    <p>Reconstructing single-cell resolution from spatial transcriptomics with CellRefiner</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-70090-2" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CellRefiner">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/XiangyuKuang/cellrefiner" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellRefiner">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellRefiner 方法解读：从 spot 到“可分析的虚拟单细胞组织”

### 一句话理解

CellRefiner 不从 Visium spot 中真正测出每个细胞的位置。它把配对的 scRNA-seq 细胞先分配到 spot，再把这些细胞当作粒子，在组织边界、细胞间距和表达相似性等约束下移动；随后可把每个细胞展开成多个亚细胞元素，得到用于接触图和配体–受体分析的预测几何。输出是模型重建，不是成像分割或实验测量。

### 输入、输出与最重要的假设

输入是同一组织背景的 spot 级 ST、scRNA-seq、spot 坐标、细胞类型标签，以及可选的配体–受体数据库。主入口 `spatial_mapping` 返回从 scRNA-seq 复制出的细胞表达矩阵和精修坐标；每个 spot 默认选 5 个细胞。随后 `cell_shape_modeling` 可生成细胞轮廓和接触矩阵，`contact_communication` 再只在接触边上计算信号。

方法成立依赖三个假设：配对数据的表达空间可比较；每个 spot 的细胞数近似已知且默认较均一；表达相似或配体–受体互补的细胞更可能靠近。论文自己指出，批次差异、空腔或强烈变化的细胞密度、低丰度细胞类型和未知组织边界都会破坏这些假设。

### 第一阶段：把单细胞分配到 spot

论文把映射写成 fused Gromov–Wasserstein（FGW）最优传输。细胞–spot 代价是共享基因表达的余弦不相似度：

$$
M_{ij}=1-\frac{S_i\cdot G_j}{\lVert S_i\rVert_2\lVert G_j\rVert_2}.
$$

FGW 同时比较细胞之间的表达结构 $C_1$ 和 spot 之间的空间/表达结构 $C_2$。代码中，spot 表达与 alpha-complex 邻接图先由两层 GCN 的 Deep Graph Infomax 编码；嵌入余弦相似度再乘 spot 欧氏距离，归一化后作为 $C_2$。POT 的 `fused_gromov_wasserstein` 使用 `alpha=0.5` 和均匀边缘分布求传输矩阵 $T$。

然后代码对每个 spot 取传输权重最大的 `n_cell` 个细胞。这里有一个容易忽略的语义：同一个 scRNA-seq 细胞可以被不同 spot 重复选中，因此输出中的“细胞”更准确地说是参考细胞的空间实例，而不是输入细胞的一一定位。初始坐标是在相应 spot 中心附近加高斯扰动得到的。

### 第二阶段：粒子精修

论文将位置变化概括为四项：

$$
\dot{\mathbf x}_i=\mathbf F_{m,i}+\mathbf F_{s,i}+\mathbf F_{g,i}+\mathbf F_{LR,i}.
$$

#### 1. 细胞间距

双高斯形式的 Morse 势产生短程排斥和较远距离吸引，使细胞避免重叠和大空洞。代码只在由 spot 邻域定义的局部候选对上计算该力，并用 `-dt * spatial_forces` 更新位置。

#### 2. spot 约束

当细胞离最近 spot 中心超过半径 `x_r` 时，代码施加平方增长的回拉力；力的数值上限是 30。它实际寻找“当前最近的 spot”，不是始终绑定初次分配的 spot。论文写的是所属 spot、系数 $b=0.05$、上限 1.5，因此这里属于论文公式与快照代码的实质差异。

#### 3. 表达相似性

输出细胞的 PCA 表示两两求 Pearson 相关，负值截为 0。相关越高，局部邻居间的吸引越强。其退火系数在代码中是

$$
a_i=\left(1-\frac{i}{T-1}\right)^2,
$$

而论文公式还含 $1/20$；代码没有这个因子。

#### 4. 可选的配体–受体力

对每个配体–受体组合，异聚体受体的表达取各亚基最小值，再构造对称亲和矩阵

$$
W_0=T_LT_R^\top+T_RT_L^\top.
$$

谱稀疏化后，矩阵权重形成另一项局部吸引。当前 API 默认 `enable_lr_force=False`；论文消融也显示开启与关闭的位移差异很小，所以不应把它描述为主要性能来源。

#### 5. 组织边界

初始位置上的高斯核和定义组织密度场，阈值取最大值的 0.4。代码检测到越界时，只保留本轮位移的 10%，并不是论文所写的“投影到最近边界点”。这是一种软回退近似。

### 第三阶段：从中心点生成细胞形状

每个细胞用默认 20 个亚细胞元素表示。元素之间使用 Lennard–Jones 型细胞内/细胞间相互作用，细胞间强度由 PCA 表达相关缩放；退火噪声帮助系统搜索稳定形状。GPU 模拟默认运行 2000 步，之后以 alpha shape 构建轮廓并由轮廓相交得到接触矩阵。

论文的 Eq. 10 写有 $\gamma r^3$，当前 GPU 核的附加项在力层面实现为 `gamma*r`，不能直接视作逐字复现该势函数。另一个实际接口问题是 `cell_shape_modeling(…, ne, rd_ratio)` 在函数体内把 `ne` 重设为 20、`rd_ratio` 重设为 2.5，因此调用者传入这两个参数目前不会生效。

### 接触型细胞通讯怎样计算

`contact_communication` 不在所有细胞对上算信号，只遍历接触矩阵的非零边。对发送细胞 $i$、接收细胞 $j$ 和配体–受体对 $(L,R)$，边权是

$$
s_{ij}^{L,R}=\left(\prod_{g\in L}x_{ig}\right)\left(\prod_{h\in R}x_{jh}\right).
$$

异聚体在这个下游模块用各亚基表达的乘积，与前面构造 LR 精修力时使用的“最小亚基表达”不同。程序再按通路求和，并输出每个细胞的发送和接收总量。结果高度依赖预测位置、预测形状、接触判定和数据库；它适合提出接触信号假设，不等同于实验验证。

### 六张主图应怎样读

- 图 1 是方法链：映射、粒子精修、亚细胞元素和接触通讯。
- 图 2 是主要基准证据：从 MERFISH、seqFISH、Slide-seqV2、STARmap 等单细胞空间数据构造 pseudo-Visium，再比较重建与真值。KL、Wasserstein、最近同类邻居距离和 Ripley’s L 衡量的是分布或空间结构，不是逐细胞身份全部恢复。低于约 5% 的细胞类型表现下降。
- 图 3 展示小鼠皮层和淋巴结 Visium 应用。层状结构、空间域和邻域富集与已知组织结构一致，但这里没有真实单细胞坐标作为直接真值。
- 图 4 先在 seqFISH+ 上比较重建形状与接触图，再把形状模型用于低分辨率数据。补图 5 显示 CellRefiner 和 Tangram+Delaunay 的相关性表现较好，CellRefiner RMSE 更低；论文仍明确警告假阳性。
- 图 5 的鳞癌 EPHB、NOTCH、ICAM、CDH 等模式是“与既有知识一致”，不是本文实验确认。
- 图 6 展示小鼠皮层的预测信号和 spot 内 NOTCH 异质性。它说明模型能给出比 spot 平均值更细的假设，但细胞级异质性本身仍由重建产生。

### 论文证据支持什么，不支持什么

支持：在由单细胞空间数据聚合得到的伪低分辨率基准上，粒子精修常改善空间分布指标；形状模型可产生可用于接触图的几何；多种数据集展示了方法的适用面。

不支持：从普通 Visium 唯一恢复真实的逐细胞坐标和形状；把肿瘤或皮层信号图当作新机制的实验验证；认为 LR 力是性能提升的关键；忽略参考数据质量、细胞数设定和组织密度假设。

### 当前代码快照的复现边界

GPU 精修路径完整迭代 10 轮；CPU 函数的 `return` 位于循环体内部，首轮后即返回，而且返回的最后一帧仍是预分配初值。这意味着无 CuPy 环境的默认降级路径不能被当作与 GPU 等价。FGW 的 `max_iter=1000000` 也不同于论文文字中的较小设置。

### 实用阅读顺序

先看 `summary.md` 掌握结论和限制，再看 `doc_method.md` 对照论文公式；要复现时先读 `doc_code.md` 的 Match Assessment，尤其检查 GPU 可用性、每 spot 细胞数、输入归一化、随机种子和形状接口参数。最后再用 `figure_analysis.md` 区分真值基准、组织学一致性与模型推断。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellRefiner：论文与代码复核摘要

### 结论先行

CellRefiner 将配对 scRNA-seq 和 spot 级空间转录组重建为虚拟单细胞空间图：先用 FGW 将参考细胞分配到 spot，再以粒子力精修位置，最后可用亚细胞元素生成形状、接触图和接触型配体–受体信号。论文在多种由单细胞空间数据生成的 pseudo-Visium 基准上显示空间分布指标改善，并在 Visium 皮层、淋巴结和鳞癌中给出与组织学或先验知识一致的应用结果。

核心边界是：这些输出是模型预测而非实验测得的逐细胞坐标、轮廓或信号。论文明确报告低丰度细胞类型性能下降、密度细节与边界误差、配对数据质量依赖、均一细胞尺寸/密度假设，以及通讯假阳性风险。

### 方法链

1. 共享基因与每类前 100 个 marker 构成映射特征。
2. SpaceFlow 风格图表示与 FGW 同时约束表达相似和 spot 空间结构。
3. 每个 spot 取传输权重最高的若干参考细胞并随机初始化坐标。
4. Morse 间距力、spot 回拉、表达相关吸引和可选 LR 吸引迭代位置。
5. 每个细胞用多个元素模拟轮廓，轮廓接触形成接触图。
6. 仅在接触边上计算配体–受体和通路信号。

### 证据强度

- 强：图 2 的伪低分辨率基准有原始单细胞空间坐标作真值，覆盖 KL、Wasserstein、最近邻和 Ripley’s L 等指标。
- 中：图 4 的 seqFISH+ 形状/接触图比较及补图 5 通讯基准；模型接触图仍不是直接分割结果。
- 弱到中：图 3、5、6 的真实 Visium 应用主要依赖组织结构或既有生物学的一致性，没有逐细胞位置真值。肿瘤和皮层信号应视为候选假设。

### 代码匹配判断

**Partial（主体匹配，但存在重要实现差异和缺陷）。** 快照实现了 FGW、局部粒子力、边界约束、亚细胞元素、alpha shape、接触矩阵和通讯汇总。直接代码复核同时发现：

- spot 力使用最近 spot、上限 30，和论文所属 spot、系数 0.05、上限 1.5 不同；
- 表达/LR 力退火缺少论文的 `1/20`；边界是保留 10% 位移，不是投影到最近边界；
- CPU 精修在循环首轮内部返回，不能视作 GPU 等价降级；
- `cell_shape_modeling` 覆盖调用者传入的 `ne` 与 `rd_ratio`；
- 形状模型的代码力项与论文 Eq. 10 的势函数写法不逐字等价；
- FGW `max_iter=1000000`，与论文配置叙述不一致。

因此复现应优先使用并验证 GPU 路径，并把论文和代码结果分开记录。

### 复现性

论文数据来自多个外部数据集，结果重建还依赖预处理、每 spot 细胞数、硬件/GPU 和随机初始化。当前评估是“可追踪实现，尚未本地端到端复现”。

### 来源

- 论文：`paper source/paper/vlm/paper.md`
- 补充材料：`output_paper_supp_md/paper_supp1/vlm/paper_supp1.md`
- DOI：`10.1038/s41467-026-70090-2`

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
