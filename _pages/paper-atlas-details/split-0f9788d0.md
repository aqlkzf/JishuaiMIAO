---
layout: default
permalink: /paper-atlas/split-0f9788d0/
title: "SPLIT"
nav: false
wide: true
description: "Xenium 给每个转录本一个空间坐标，再由分割边界把转录本归到“细胞”。一个分割对象中出现两种细胞类型的表达信号，至少有两种完全不同的解释： biological doublet：确实有两个完整细胞被当成一个对象； signal-level mixture：对象主体仍是一个细胞，但邻近细胞、z 轴重叠细胞或错误边界的转录本被分配进来。"
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
      <span>Computational Tools</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>SPLIT</h1>
    <p>Resolving sensitivity, specificity and signal contamination in Xenium spatial transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03089-8" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SPLIT">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/bdsc-tds/SPLIT" target="_blank" rel="noopener noreferrer" aria-label="Open code for SPLIT">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SPLIT 方法中文精讲：从“混合信号”到逐基因净化

### 1. 先建立正确的直觉

#### 1.1 transcript spillover 不等于 biological doublet

Xenium 给每个转录本一个空间坐标，再由分割边界把转录本归到“细胞”。一个分割对象中出现两种细胞类型的表达信号，至少有两种完全不同的解释：

- **biological doublet**：确实有两个完整细胞被当成一个对象；
- **signal-level mixture**：对象主体仍是一个细胞，但邻近细胞、$z$ 轴重叠细胞或错误边界的转录本被分配进来。

论文强调，Xenium 中 RCTD 所称的 “doublet” 很少等同于单细胞测序语境中的真实 doublet，更常是后一种混合信号。因此，SPLIT 不是在“拆开两个真实细胞”，而是在估计：**当前观测表达中，哪些比例更像 primary cell type，哪些比例更像 secondary contaminating type**（`paper.md:27-33`, `paper.md:124-133`）。

一个好用的心智模型是：

```text
观测到的细胞表达
  = 该细胞身份对应的主要信号
  + 由邻近、重叠或分割误差引入的次要信号

SPLIT 的目标：保留“主要信号”的模型估计值，而不是追踪每个物理转录本来自哪一个细胞。
```

#### 1.2 这篇文章真正回答了三个层次的问题

1. **Xenium 的数据特性是什么？** targeted panel 与 5K panel 的灵敏度、细胞类型分辨率和跨样本一致性如何？
2. **混合信号是否与空间邻域一致？** RCTD 的 secondary weight 是否随邻域中相同类型的丰度变化？
3. **能否用一个可解释的模型减少这种混合？** SPLIT 用参考表达谱与去卷积权重逐基因分配观测 counts。

研究包含 27 位供体的 41 个乳腺癌/肺癌组织切片，并结合多种 Xenium panel、Chromium snRNA-seq 参考与 IHC（`paper.md:36-45`）。所以它既是 Xenium benchmark，也是 SPLIT 方法论文。

### 2. 为什么只改分割、或只用已有校正方法还不够？

论文并不是说分割不重要。Baysor、ProSeg、Segger 等方法利用转录本空间坐标改善细胞边界；ProSeg 还显式建模三维空间中的转录本归属。问题是：

- transcript spillover 和 segmentation error 会产生相似的观测后果，改进边界并不保证所有混合信号消失；
- 即使使用 nucleus-only segmentation，Fig. 4 仍检测到污染代理信号（`paper.md:185`）；
- transcript-aware segmentation 与 count correction 可以组合，而不是互相替代（`paper.md:168-191`, `paper.md:221-224`）。

ResolVI 和 ovrlpy 也能减少混合，但论文报告了可解释性与数据保留的权衡：部分设置会大幅减少可检测基因或产生接近空的细胞。SPLIT 的设计重点不是建立更复杂的黑盒，而是把校正写成一个可以逐基因检查的参考谱分解（`paper.md:165-191`, `paper.md:218-221`）。

因此，SPLIT 的新意可以概括为：

> 用去卷积给出的“细胞类型权重”决定混合了多少，再用参考表达谱决定“每个基因应按什么比例拆分”。

### 3. 符号、维度与最容易踩错的转置

设：

- $G$：输入 counts 与 reference 共有的基因数；
- $C$：counts 与去卷积权重共有的细胞数；
- $T$：参考中包含的 cell type 数。

| 数学/代码对象 | 维度 | 含义 | 直接证据 |
|---|---:|---|---|
| $X$ / `counts` | $G\times C$ | 观测到的 gene × cell 原始 counts | `SPLIT/R/method_agnostic_purification.R:13-15`, `:87-90` |
| $p$ / `primary_cell_type` | 长度 $C$ | 每个细胞的 primary type；名字必须对应 cell ID | 同文件 `:17-19`, `:133-151` |
| $W$ / `deconvolution_weights` | $C\times T$ | 每个细胞对各 cell type 的权重 | 同文件 `:21-23`, `:141-149` |
| $R$ / direct `reference` | $T\times G$ | `rctd_free_purify()` 真正消费的 cell type × gene 参考矩阵 | 同文件 `:25-27`, `:87-151` |
| $\widetilde R$ / converter `reference` | $G\times T$ | `convert_rctd_result_to_purify_input()` 返回的 gene × cell type 矩阵 | `SPLIT/R/rctd_output_conversion.R:19-27`, `:91-113` |
| $D=WR$ | $C\times G$ | 每个细胞的加权参考混合谱 | `SPLIT/R/method_agnostic_purification.R:235-245` |
| $N$ | $C\times G$ | primary type 对每个基因的期望贡献 | 同上 |
| $F=N\oslash D$ | $C\times G$ | 每个 cell × gene 的 primary fraction | 同上 |
| $X_{purified}$ | $G\times C$ | 净化后的 fractional counts | 同文件 `:243-275` |

#### 3.1 两个接口的 reference 方向相反

这是复现时最危险的地方：

```text
convert_rctd_result_to_purify_input()
  输出 reference: G x T
            |
            |  transpose 一次
            v
rctd_free_purify() / direct purify()
  输入 reference: T x G
```

RCTD wrapper 在源码中明确执行 `Matrix::t(rctd$reference)`（`SPLIT/R/method_agnostic_purification.R:396-403`）。README 的文字说 direct reference 是 genes × cell types，这是错误的；但 README 示例又正确写了 `t(new_input$reference)`（`SPLIT/README.md:24-29`, `:89-100`）。

实践规则很简单：

- 只看 converter 输出时，它是 $G\times T$；
- 真正调用 `rctd_free_purify()` 或 direct `purify()` 时，传 $T\times G$；
- 不要根据 README 那一句 prose 再转错一次。

### 4. RCTD 先做什么？spot class 如何决定 SPLIT 分支？

RCTD 用 Poisson mixture 把一个空间对象表示成 cell-type reference 的加权和。在 doublet mode 中，它给出 primary/secondary type、$w_1/w_2$ 和 spot class。论文把 primary 当作真实身份，把 secondary 及其权重当作候选污染来源与强度（`paper.md:323-329`）。

当前 converter 的真实行为如下：

| RCTD spot class | 进入 $W$ 的权重行 | SPLIT 分支 | 最终命运 |
|---|---|---|---|
| 高置信 `singlet`，secondary 已被设为 `NA` | 只有 first type | 恒等变换 | 一个非零类型，counts 数值保持 raw，状态为 `raw`。 |
| 仍有 secondary 的 contaminated `singlet` | first + second | doublet-SPLIT | 两个非零类型，状态为 `purified`。 |
| `doublet_certain` | first + second | doublet-SPLIT | 按两类型公式净化。 |
| `doublet_uncertain` | RCTD 的完整 $T$ 维权重行 | full-SPLIT | secondary 不确定，因此所有候选类型进入分母。 |
| `reject` | converter 不生成该行 | 无 | 在与 counts 取 shared cells 时消失；balance 函数也显式移除 reject。 |

代码证据在 `SPLIT/R/rctd_output_conversion.R:146-183`；论文分支在 `paper.md:365-371`, `paper.md:383-390`。

这里还能解释一个版本陷阱：教程和 README 仍传 `DO_purify_singlets=TRUE`，但当前 generic path 会警告该参数已 deprecated 并**忽略**它（`SPLIT/R/method_agnostic_purification.R:100-117`）。当前 singlet 是否变化，取决于 converter 后的权重行是否还有 secondary type；只有 deprecated v0.1-style 实现真正读取这个参数（`SPLIT/R/deprecated_purification.R:75-90`, `:359-386`）。

### 5. 三个核心公式：doublet、full 与 shift

#### 5.1 doublet-SPLIT：保留 primary component

论文原式为：

$$
&#123;&#123;\bf{x}}}_{\mathrm{doublet}-\mathrm{SPLIT}}=\frac&#123;&#123;w}_{1}&#123;&#123;\bf{ref}}}_{1}}&#123;&#123;w}_{1}&#123;&#123;\bf{ref}}}_{1}+{w}_{2}&#123;&#123;\bf{ref}}}_{2}}\odot &#123;&#123;\bf{x}}}_{\mathrm{observed}},
$$

其中除法和 $\odot$ 都是逐基因运算（`paper.md:356-365`）。

不要把这个分式误读成常数 $w_1$。例如 $w_1=w_2=0.5$：

- 对 primary marker gene，若 $ref_{1g}=10,ref_{2g}=1$，primary fraction 是 $10/11$；
- 对 secondary marker gene，若 $ref_{1g}=1,ref_{2g}=10$，primary fraction 是 $1/11$。

所以，$w_1,w_2$ 描述**整细胞混合强度**，而 reference 决定**某个基因如何拆分**。

#### 5.2 full-SPLIT：secondary 不明确时让所有候选类型进入分母

$$
&#123;&#123;\bf{x}}}_{\mathrm{full}-\mathrm{SPLIT}}=\frac&#123;&#123;w}_{1}&#123;&#123;\bf{ref}}}_{1}}&#123;&#123;\sum }_{i=1}^{k}{w}_{i}\,&#123;&#123;\bf{ref}}}_{i}}\odot &#123;&#123;\bf{x}}}_{\mathrm{observed}}.
$$

它仍保留 primary numerator，但 denominator 从两种类型扩展到 $k$ 种候选类型（`paper.md:368-371`）。这对应 `doublet_uncertain`。

#### 5.3 SPLIT-shift：有证据认为标签反了时保留 secondary component

$$
&#123;&#123;\bf{x}}}_{\mathrm{SPLIT}-\mathrm{shift}}=\frac&#123;&#123;w}_{2}&#123;&#123;\bf{ref}}}_{2}}&#123;&#123;w}_{1}&#123;&#123;\bf{ref}}}_{1}+{w}_{2}&#123;&#123;\bf{ref}}}_{2}}\odot &#123;&#123;\bf{x}}}_{\mathrm{observed}}.
$$

思想不是“更强的净化”，而是换一个要保留的身份（`paper.md:374-380`）。代码如何决定 swap、如何处理 multi-component cell，见第 8 节。

### 6. Fig. 3h 应该怎样从左往右读？

Fig. 3h 是理解 SPLIT 最重要的一张示意图（原图：`paper source/nature_html/images/figure_03.png`）。

#### 6.1 左侧：observed gene profile

最左边的蓝色长条表示一个细胞的观测向量 $&#123;&#123;\bf x}}_{observed}$。它只告诉我们“这个分割对象里测到了什么”，并不携带每个转录本的真实来源标签。

#### 6.2 中间：RCTD 用两个参考谱近似这个对象

RCTD 给出一对 cell-level scalar weights，并写成：

$$
&#123;&#123;\bf x}}_{observed}\approx w_1&#123;&#123;\bf ref}}_1+w_2&#123;&#123;\bf ref}}_2.
$$

图中的蓝/棕饼图描述 $w_1,w_2$；两个竖直参考谱描述 $&#123;&#123;\bf ref}}_1,&#123;&#123;\bf ref}}_2$。权重在整个细胞层面是标量，但两个参考谱在不同基因上的高度不同（`paper.md:323-330`）。

#### 6.3 右侧：同一个 denominator 产生 primary 与 secondary fraction

对 focal cell 中的基因 $g$，先把两个参考贡献写开：

$$
m_{1g}=w_1ref_{1g},\qquad m_{2g}=w_2ref_{2g}.
$$

它们不是观测到的真实来源 counts，而是模型根据权重和参考谱得到的 expected contributions。再用共同 denominator 归一化：

$$
q_{1g}=\frac{m_{1g}}{m_{1g}+m_{2g}},\qquad
q_{2g}=\frac{m_{2g}}{m_{1g}+m_{2g}}.
$$

若这个基因的观测 count 为 $x_g$，默认 SPLIT 计算：

$$
x_{kept,g}=q_{1g}x_g,
$$

而理想两成分方程中被排除的估计残差是：

$$
x_{removed,g}=x_g-x_{kept,g}=q_{2g}x_g.
$$

关键是：

- 两个 fraction 共享同一个 denominator；
- 因为 $ref_{1g},ref_{2g}$ 随基因变化，$q_{1g},q_{2g}$ 也随基因变化；
- 它们通常不等于全细胞标量 $w_1,w_2$。

##### 一个逐基因去污染的数值例子

假设同一细胞有 $w_1=0.7,w_2=0.3$，两个基因的观测 count 都是 12。

| 基因 | $ref_{1g}$ | $ref_{2g}$ | $m_{1g},m_{2g}$ | $q_{1g}$ | kept | removed |
|---|---:|---:|---|---:|---:|---:|
| secondary marker A | 2 | 8 | 1.4, 2.4 | $1.4/3.8\approx0.368$ | $12\times0.368\approx4.42$ | $\approx7.58$ |
| primary marker B | 10 | 1 | 7.0, 0.3 | $7.0/7.3\approx0.959$ | $12\times0.959\approx11.51$ | $\approx0.49$ |

虽然两行使用完全相同的 $w_1,w_2$，secondary marker A 被移除得多，primary marker B 几乎保留。这就是“cell-level weights + gene-level references → gene-specific removal”。这里的 7.58 和 0.49 都是模型估计的 fractional counts，不是识别出的具体 RNA 分子。

在理想的非零两类型模型中，$q_{1g}+q_{2g}=1$，因此 kept 与 removed 两个分量逐基因加回 $&#123;&#123;\bf x}}_{observed}$。但是，当前代码为数值稳定加入 epsilon，而且只直接计算 retained primary component；所以“严格加回”是论文二成分方程的概念性质，不应被当作任意软件输入下的重建证明（`paper.md:353-371`; `SPLIT/R/method_agnostic_purification.R:213-245`）。

#### 6.4 Keep / Remove 到底是什么意思？

默认 SPLIT 把 primary estimate 送入下游，把 secondary estimate 排除。图中的 **remove** 是“根据 mixture/reference 模型扣除估计信号”，不是：

- 看见了某个物理转录本从邻居移动过来；
- 证明了这个转录本的真实来源；
- 把该转录本自动放回正确邻居。

更具体地说，default SPLIT 只修改 **focal cell 自己的下游表达向量**：它不读取某个特定邻居的 counts，也不从该邻居中减去相同数量；估计的 residual 默认直接从 focal cell 的 downstream profile 中丢弃。因此，default SPLIT 不保证 tissue-wide total counts 守恒。包中的 residual reassignment 是另一个非默认步骤，论文只把它列为未来需要测试的策略；不能用它来解释 Fig. 3h 的默认 keep/remove（见第 9 节）。

Fig. 3h 还隐含两个假设：primary label 是应保留的身份；混合只含两个分量。`doublet_uncertain` 用 full-SPLIT 多类型 denominator，primary 可能被颠倒时则需要 SPLIT-shift。因此它是一个解释算法的 schematic，不是完整 generative model 已被证明正确的证据。

### 7. 当前代码怎样一步步计算矩阵？

#### Step 1：先对齐 shared cells、shared genes 和 cell types

代码取：

$$
C_{shared}=\operatorname{intersect}(\operatorname{colnames}(X),\operatorname{rownames}(W)),
$$

$$
G_{shared}=\operatorname{intersect}(\operatorname{rownames}(X),\operatorname{colnames}(R)).
$$

随后要求 $W$ 的列名与 $R$ 的行名完全一致（排序后比较），否则停止（`SPLIT/R/method_agnostic_purification.R:120-151`）。因此输出只含 shared genes/cells。

代码确实会丢掉没有权重的细胞，但 missing-cell warning 的条件写成“原细胞数 < 交集细胞数”（`:166-170`），正常情况下不可能成立。不要依赖这个 warning；应自己记录输入/输出维度。

#### Step 2：检查并重标度 weight row

若任何 row sum 小于或大于 1，且 `DO_require_sumup_to_one=TRUE`，代码把每行除以自己的 row sum（`:156-164`）。

**风险：**没有显式检查 row sum 必须大于 0。全零行可能在除法时产生未定义值；随后 `epsilon/n_celltypes` 中的 `n_celltypes=0` 也不安全。

#### Step 3：可选地把“不净化细胞”改成 identity mixture

若给出 `cells_to_purify`，不在集合中的细胞会被改成 primary type 的 one-hot 权重。此时 numerator 与 denominator 相同，因此原 counts 保持不变（`:171-205`）。

#### Step 4：计算共同 denominator

$$
D=WR+\epsilon,
$$

其中 $W$ 是 $C\times T$，$R$ 是 $T\times G$，所以 $D$ 是 $C\times G$。代码设置 $\epsilon=10^{-10}$（`:213-245`）。

#### Step 5：构造 primary numerator

对细胞 $c$、基因 $g$：

$$
N_{cg}=W_{c,p_c}R_{p_c,g}+\frac{\epsilon}{n_c},
$$

其中 $n_c$ 是该细胞非零 cell-type weight 的数量。这个 epsilon 分配是代码细节，不在论文公式中。

#### Step 6：逐元素比值，再乘 observed counts

$$
F=N\oslash D,\qquad X_{purified}=F^\top\odot X.
$$

因此：

- observed count 为 0 时，输出仍为 0；
- 正整数 count 经比例缩放后通常变成小数；
- 这不是从多项分布重新采样，也不自动 round 为整数。

#### Step 7：chunking 只是省内存，不改变公式

默认 `chunk_size=50000` cells。每个 block 内形成 $C_b\times G$ 的 ratio，转置后与 $G\times C_b$ counts 逐元素相乘，再收集 nonzero triplets，最后重建一个稀疏矩阵（`:218-268`）。

#### Step 8：两种输出形状

- `DO_output_sce=FALSE`：`list(purified_counts, cell_meta)`；
- `DO_output_sce=TRUE`：`SingleCellExperiment`，包含 raw `counts`、`purified_counts`、`colData` 和 deconvolution summary。

两者的表达矩阵均为 $G_{shared}\times C_{shared}$（`:279-327`）。

### 8. 三条决策路径：default、score-based 与 shift

#### 8.1 一个紧凑决策树

```text
RCTD / generic deconvolution result
  |
  +-- reject? ------------------------------> remove
  |
  +-- default
  |     +-- one nonzero type --------------> raw
  |     +-- 2 types ------------------------> doublet-SPLIT
  |     +-- >2 / doublet_uncertain --------> full-SPLIT
  |
  +-- balance_score_based
        +-- doublet_uncertain -------------> full-SPLIT, regardless of score
        +-- score > threshold -------------> purified
        +-- otherwise ----------------------> raw
        |
        +-- DO_swap_lables = TRUE?
              +-- exact swap predicate true -> swap labels/weights
              +-- and already purified -----> raw - purified profile
              +-- but kept raw -------------> label-only swap
```

#### 8.2 default SPLIT

论文 default 是：有 secondary type 的 contaminated singlet 与 `doublet_certain` 做 doublet-SPLIT，`doublet_uncertain` 做 full-SPLIT（`paper.md:383-390`）。当前 generic code 的实际状态由非零 weight 数量决定，而不是 `DO_purify_singlets`（`SPLIT/R/method_agnostic_purification.R:283-303`）。

#### 8.3 balance_score_based

空间邻域中，每个 neighbor 同时贡献 first/second type 及其权重；对 cell type 聚合并归一化后，取 focal secondary type 对应的值作为 `neighborhood_weights_second_type`（`SPLIT/R/neighborhood_analysis.R:276-400`）。

`balance_raw_and_purified_data_by_score()` 的代码规则是：

- `score > threshold`：使用 purified counts；
- `doublet_uncertain`：无论 score 多大，都使用 full-SPLIT 结果；
- 其他 nonreject：保留 raw；
- `reject`：移除（`SPLIT/R/balanced_dataset.R:50-109`）。

注意是严格 `>`，刚好等于 threshold 不净化。library 默认 `threshold=0.15`，而 Xenium tutorial 显式使用 `0.05`（函数 `:50-58`; tutorial `:240-248`）。复现时必须报告你用的是哪一个。

另一个 `balance_raw_and_purified_data_by_spot_class()` helper 会把所有 singlet 保持 raw、其他 nonreject 替换为 purified（`SPLIT/R/balanced_dataset.R:139-190`）。它不等于论文 default，因为论文 default 会净化仍带 secondary 的 contaminated singlet。

#### 8.4 SPLIT-shift 的真实代码判据

论文概念规则是：若 primary 为 $ct_1$、secondary 为 $ct_2$，而 PCA-space transcriptomic neighborhood 主要是 $ct_2$，则怀疑标签颠倒（`paper.md:374-380`）。

当前代码只有同时满足以下三项才 swap：

1. focal `first_type` 不等于 neighborhood-majority first type；
2. focal `first_type_class` 不等于 neighborhood-majority first-type class；
3. focal `second_type_class` 等于 neighborhood-majority first-type class。

直接判据在 `SPLIT/R/balanced_dataset.R:1-6`；majority 定义在 `SPLIT/R/neighborhood_analysis.R:734-799`。代码还计算 entropy-based certainty，但 swap predicate 没有使用这些 certainty 值（`:803-881`）。

#### 8.5 swap 后的 profile 不是在所有情况下都等于 secondary component

代码先交换 first/second labels 与 weights，再对“已经 purified 且被 swap 的细胞”执行：

```text
shifted profile = raw counts - primary-purified counts
negative values -> 0
```

证据在 `SPLIT/R/balanced_dataset.R:8-26`。

- 对严格两成分模型，它就是论文 secondary complement；
- 对 full-SPLIT 多成分模型，它是**所有 non-primary residual 的总和**，不能说成唯一 secondary type 的纯表达；
- 若 cell 在 score gate 中保持 raw，代码会交换 label/weight，但不会替换 expression，因此是 **label-only swap**。

参数也有版本差异：论文写 transcriptomic PCA-kNN $k=10$（`paper.md:380`），当前 tutorial 用 `k_knn=100`（`SPLIT/doc/Run_RCTD_and_SPLIT_on_Xenium.R:262-283`）。tutorial 证明运行路径存在，但不是 paper-exact 参数。

### 9. residual reassignment 是可选/未来测试方向，不是主结果

核心 SPLIT 只保留 primary estimate，不会自动把 removed signal 放回邻居。包中另有 `reassign_residual_counts()`：

1. 对 purified sender 计算 $X_{residual}=X_{raw}-X_{corrected}$；
2. sender 是 operator 的行，receiver 是列；
3. 每个 sender 只向候选 secondary-type neighbors 分配；
4. 可 uniform 分配，或按 receiver 的 raw total counts 比例分配；
5. 没有 eligible receiver 的 sender 不产生 reassigned contribution；
6. 最后把 reassigned residual 加到 corrected counts。

直接实现见 `SPLIT/R/residual_counts_reassignment.R:48-116`, `:151-205`。roxygen 把 operator 称作 “column-stochastic”，但代码语义是有 receiver 的 sender row 分配总质量；`count_proportional` 也实际使用 receiver 的 `colSums(raw_counts)`。

论文把邻域重分配描述为“未来需要测试的 alternative strategy”，没有把它当作 Fig. 4 已验证的主结果（`paper.md:227-230`）。学习时不要把这个可选函数混入 SPLIT 的核心证据链。

### 10. 图像证据链：结果支持了什么，又没有证明什么？

#### 10.1 Fig. 3：先证明“secondary signal 与邻域一致”

Fig. 3 可见：

- $w_2$ 与邻域中同一 secondary type 丰度的 cosine similarity；
- primary–secondary cell-type pair 的 spillover index；
- malignant signal 与邻域关系；
- IHC 与 transcript dots；
- panel h 的 RCTD → SPLIT 分解示意。

这支持“secondary signal 常与邻域来源相符，因此 spillover 是合理解释”（`paper.md:124-147`）。但相关性不等于物理来源追踪，也不能排除 segmentation、overlap 或 reference mismatch。

#### 10.2 Fig. 4：再比较 purity 与 information retention

Fig. 4 同时比较 raw、SPLIT、ResolVI、ovrlpy 与多种 segmentation：

| 评估维度 | 指标 | 要防止的误读 |
|---|---|---|
| cell-type separation | SCIB biological conservation、Leiden ARI 等 | 分群更开不一定代表生物更真实，也可能过校正。 |
| batch behavior | iLISI 等 | batch 更混合不等于细胞身份更准确。 |
| data retention | 保留 cells、每细胞 genes | 只看 purity 会忽略空细胞与基因损失。 |
| contamination proxy | 邻近恶性细胞的 T 细胞中，top-20 coefficient 是否含恶性 marker | 这是模型代理指标，不是转录本来源的金标准。 |
| reference fidelity | Xenium 与 Chromium pseudo-bulk cosine similarity | SPLIT 本身使用 Chromium reference，因此高相似度部分是预期的。 |
| downstream biology | proximity GSEA / exhaustion-related genes | 支持更清晰的关联，不证明肿瘤邻近导致 exhaustion。 |

论文报告 SPLIT 在该 benchmark 中提高 cell-type separation 与 Chromium similarity，同时比一些替代方法更好地保留基因/细胞（`paper.md:165-194`, `paper.md:402-438`）。

#### 10.3 Extended Data Fig. 7–10 补齐什么？

- **Extended Data Fig. 7**：matched/external reference 下的 SPLIT UMAP，以及 default keep-$w_1$ 与 shift keep-$w_2$ 的概念图；它不展示代码中的三项 swap predicate。
- **Extended Data Fig. 8**：cycling tumor state 缺失于 reference 时，default 可能过度分解；neighborhood-aware gate 能保留该群。这是 reference completeness caveat 的可视化。
- **Extended Data Fig. 9**：把 Fig. 4 类似的 benchmark 扩展到 Breast panel，支持趋势并非只见于 lung。
- **Extended Data Fig. 10**：不同 correction 下，T-cell proximity logistic regression 的 top genes。SPLIT 后 `CXCL13`, `HAVCR2`, `LAG3` 等 exhaustion/T-cell genes 更突出，但仍是关联性特征排名。

所有 14 张本地图的逐图问题、可见内容、支持结论与证据边界见 `figure_analysis.md`。

### 11. 实现与版本 caveats：复现前必须知道

| Caveat | 影响 |
|---|---|
| `DO_purify_singlets` 在 generic v0.2 path 被忽略 | README/tutorial 参数不会控制当前结果；应检查 converter 后权重行。 |
| `DESCRIPTION` 为 0.2.3，README prose/badge 为 0.2.0 | 以 commit `f226987...` 和源码行描述行为，不要只报“v0.2.0”。 |
| direct reference 实际为 $T\times G$，README prose 写 $G\times T$ | 不正确的转置会导致维度/名称错误。 |
| all-zero weight row 没有安全 guard | 可能出现除零或未定义 epsilon 分配；运行前验证正 row sum。 |
| missing-cell warning 条件写反 | 细胞仍会在 intersection 中被丢弃，但 warning 可能不触发；手动核对 $C_{in}$ 与 $C_{out}$。 |
| score library default 0.15，tutorial 0.05 | 会改变 purified cell 集合；阈值必须显式记录。 |
| paper shift $k=10$，tutorial $k=100$ | 影响 neighborhood majority；不要把 tutorial 设置称为论文设置。 |
| outputs 是 fractional counts | 下游若要求 integer counts，需要明确方法选择；不要静默 round。 |
| `SUPP_MD` **MISSING** | Supplementary Notes/Tables 未被独立分析。 |
| `xenium_analysis_pipeline`、`Bilous2026` 在 scoped `code source` 中 **Not found** | 完整 Snakemake、logistic regression、ResolVI/ovrlpy benchmark、figure generation 尚未验证（`paper.md:441-474`）。 |

### 12. 建议的学习与复现检查清单

#### 理解论文

- [ ] 能解释为什么 RCTD doublet 在本文不等于 biological doublet。
- [ ] 能解释 $w_1/w_2$ 是 cell-level，而 SPLIT fraction 是 gene-specific。
- [ ] 能从 Fig. 3h 写出 primary 与 secondary 的共同 denominator。
- [ ] 能区分 doublet-SPLIT、full-SPLIT 和 SPLIT-shift。
- [ ] 能说清 Fig. 3 支持 spillover plausibility，Fig. 4 支持 benchmark performance，但两者都不证明物理转录本来源。

#### 准备输入

- [ ] counts 是 $G_0\times C_0$ raw counts；cell/gene names 唯一。
- [ ] weights 是 $C\times T$，每行有正总质量，cell-type names 与 reference 一致。
- [ ] reference 覆盖预期 phenotype；尤其检查 malignant/cycling states。
- [ ] converter 输出的 $G\times T$ reference 只 transpose 一次，direct API 接收 $T\times G$。
- [ ] 记录 shared genes/cells，避免静默丢失。

#### 选择分支

- [ ] 明确使用 default、score-based 还是 spot-class helper。
- [ ] score-based 时记录 score 名、threshold，以及 `doublet_uncertain` 无条件净化规则。
- [ ] shift 时记录 transcriptomic $k$，检查三项 predicate，而不是只写“邻居支持 secondary”。
- [ ] 检查 swapped raw cells 是否只是 label-only swap。

#### 验证输出

- [ ] 保留 raw counts；确认 purified counts 为 fractional。
- [ ] 同时评估 purity proxy、cell/gene retention 和 reference similarity。
- [ ] 对高变化细胞查看 primary/secondary reference 与逐基因 fraction。
- [ ] 把 reference-missing phenotype、all-zero weights、丢失 cells/genes 作为 QC failure 检查。
- [ ] 若要复现论文数值，另行获取并审计 external analysis repos 与 supplements。

### 13. 最后用五句话记住 SPLIT

1. **先判断问题类型：**本文主要处理的是分割对象里的表达混合，不是判定真实 biological doublet。
2. **权重决定混合强度，reference 决定基因拆分：**同一 $w_1/w_2$ 下，不同基因的保留比例可以完全不同。
3. **核心公式是 primary expected signal / total expected mixture × observed counts：**full-SPLIT 只是把 denominator 扩展到多类型。
4. **先选要不要净化，再决定要保留哪个身份：**score gate 控制 raw/purified，SPLIT-shift 控制 primary/secondary label 与 retained component。
5. **把结果当作可解释的模型估计，不当作物理来源真值：**它依赖 reference、deconvolution 与参数，图像证据支持实用性，但不消除这些假设。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SPLIT Summary

### One-sentence mental model

SPLIT treats a segmented Xenium cell's mixed expression as **primary biological identity plus secondary contaminating signal**, then uses deconvolution weights and cell-type reference profiles to retain the estimated primary contribution gene by gene.

The “doublet” here is usually not a biological doublet containing two intact cells. It is an expression-level mixture that can arise from horizontal transcript spillover, $z$-axis overlap or segmentation misassignment (`paper.md:27-33`, `paper.md:124-133`).

### Study problem and novelty

This *Nature Methods* 2026 study benchmarks Xenium sensitivity, specificity, panels, segmentation and contamination across 41 breast/lung tumor sections from 27 donors. Earlier Xenium studies were smaller or did not jointly compare targeted versus 5K panels, segmentation and signal contamination at this scale (`paper.md:21-36`).

Segmentation methods such as Baysor and ProSeg can improve transcript assignment, and correction methods such as ResolVI and ovrlpy address mixtures through probabilistic or spatial models. The paper argues that segmentation alone does not remove all contamination and that some correction methods trade purity for substantial gene/cell loss. SPLIT's novelty is a simple, reference-grounded and inspectable allocation: it estimates how much of each observed gene count belongs to the primary reference component (`paper.md:165-191`, `paper.md:218-224`).

### Core computation

For a two-type mixture, the paper defines

$$
&#123;&#123;\bf{x}}}_{\mathrm{doublet}-\mathrm{SPLIT}}=\frac&#123;&#123;w}_{1}&#123;&#123;\bf{ref}}}_{1}}&#123;&#123;w}_{1}&#123;&#123;\bf{ref}}}_{1}+{w}_{2}&#123;&#123;\bf{ref}}}_{2}}\odot &#123;&#123;\bf{x}}}_{\mathrm{observed}}.
$$

Although $w_1$ and $w_2$ are cell-level scalars, the retained fraction is gene-specific because the two reference profiles differ by gene. For uncertain contamination, full-SPLIT uses all candidate types in the denominator. SPLIT-shift can retain the secondary component when transcriptomic-neighborhood evidence supports a primary/secondary label swap (`paper.md:353-390`).

The current package consumes counts as genes × cells, weights as cells × cell types and the **direct** reference as cell types × genes. Its RCTD converter returns the reference as genes × cell types, so one transpose is required. README prose gets this direct orientation wrong, although its example transposes correctly (`SPLIT/R/rctd_output_conversion.R:19-27`; `SPLIT/R/method_agnostic_purification.R:87-151`; `SPLIT/README.md:24-29`, `SPLIT/README.md:89-100`).

### Evidence and conclusions

- **Why believe spillover matters?** Fig. 3 shows that RCTD secondary weight $w_2$ covaries with the local abundance of the same secondary type, and IHC/transcript overlays show tumor-associated transcripts in adjacent CD8 T-cell regions (`paper.md:124-147`).
- **How is SPLIT evaluated?** Fig. 4 and Extended Data Fig. 9 compare raw, SPLIT, ResolVI and ovrlpy across segmentation methods using SCIB conservation/batch metrics, retained cells/genes, malignant-marker contamination and Chromium pseudo-bulk similarity (`paper.md:165-194`, `paper.md:402-438`).
- **What does the paper report?** SPLIT improves reference-consistent cell-type separation and Chromium similarity while retaining more usable expression than some alternatives. Extended Data Fig. 8 shows why neighborhood-aware selection can avoid decomposing a reference-missing cycling-tumor state. After correction, tumor-proximal T cells show clearer exhaustion-associated signals (`paper.md:188-203`).
- **What is not proved?** These results do not identify the physical origin of each removed transcript, establish reference labels as ground truth or show that tumor proximity causally induces exhaustion. Chromium similarity is partly expected because SPLIT uses Chromium-derived reference profiles (`paper.md:188`).

### Implementation fidelity and reproducibility

The cloned `bdsc-tds/SPLIT` R package at commit `f226987f0fecf2847646bda50a64886e0ea432a9` directly verifies the core method:

- RCTD spot-class conversion and full versus two-type weights (`SPLIT/R/rctd_output_conversion.R:146-183`);
- numerator/denominator allocation, epsilon stabilization, chunking and sparse/list/SCE output (`SPLIT/R/method_agnostic_purification.R:120-327`);
- spatial score selection and strict threshold behavior (`SPLIT/R/neighborhood_analysis.R:276-400`; `SPLIT/R/balanced_dataset.R:50-109`);
- SPLIT-shift label/profile path (`SPLIT/R/balanced_dataset.R:1-26`);
- optional residual reassignment (`SPLIT/R/residual_counts_reassignment.R:48-205`).

Core code-paper fidelity is **medium-high**; full paper reproducibility from this package alone is **medium/incomplete**. Important caveats are:

- paper SPLIT-shift uses PCA-kNN $k=10$, but the Xenium tutorial uses `k_knn=100`;
- library score threshold defaults to 0.15, while the tutorial uses 0.05;
- `DO_purify_singlets` is still passed by README/tutorial code but ignored by the current generic path;
- `DESCRIPTION` says version 0.2.3 whereas README release prose says 0.2.0;
- all-zero weight rows lack an explicit safety guard;
- `SUPP_MD` is **MISSING**;
- full Snakemake, benchmark, logistic-regression and figure workflows are **Not found in the scoped `code source`** because `xenium_analysis_pipeline` and `Bilous2026` were not acquired (`paper.md:441-474`).

### Fast learning path

1. Read `Chinese method notes` for the intuition, dimensions, branch logic and practical checklist.
2. Study Fig. 3h in `figure_analysis.md` to connect RCTD mixture weights to gene-specific SPLIT allocation.
3. Use `doc_method.md` for the exact input → matrix computation → decision → output path.
4. Use `doc_code.md` before reproducing the package; it records the transpose, version and parameter mismatches.
5. Return to `paper.md:323-390` for the source equations and `paper.md:402-438` for evaluation definitions.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
