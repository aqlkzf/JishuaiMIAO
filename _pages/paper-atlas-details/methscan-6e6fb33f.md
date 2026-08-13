---
layout: default
permalink: /paper-atlas/methscan-6e6fb33f/
title: "MethSCAn"
nav: false
description: "MethSCAn 不直接把一个区域内读到的 0/1 甲基化状态做简单平均，而是先估计每个 CpG 位点在所有细胞中的“局部背景甲基化”，再计算单个细胞相对背景的残差；随后用滑动窗口寻找跨细胞差异最大的可变甲基化区域（VMR），构造更有信息量的细胞 × 区域矩阵，并用相似的窗口扫描和置换策略检测两组细胞之间的差异甲基化区域（DMR）。"
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
      <span>scATAC — Single-Cell Chromatin &amp; DNA Methylation</span>
      <span>Nature Methods · 2024</span>
    </div>
    <h1>MethSCAn</h1>
    <p>Analyzing single-cell bisulfite sequencing data with MethSCAn</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/anders-biostat/MethSCAn" target="_blank" rel="noopener noreferrer" aria-label="Open code for MethSCAn">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MethSCAn 方法详解：从稀疏单细胞甲基化读段到 VMR、细胞表征与 DMR

### 一句话理解

MethSCAn 不直接把一个区域内读到的 0/1 甲基化状态做简单平均，而是先估计每个 CpG 位点在所有细胞中的“局部背景甲基化”，再计算单个细胞相对背景的残差；随后用滑动窗口寻找跨细胞差异最大的可变甲基化区域（VMR），构造更有信息量的细胞 × 区域矩阵，并用相似的窗口扫描和置换策略检测两组细胞之间的差异甲基化区域（DMR）。

### 1. 论文要解决什么问题？

单细胞亚硫酸氢盐测序（scBS）可以在单细胞、单碱基分辨率上观察 DNA 甲基化，但原始数据非常稀疏：同一细胞只覆盖全基因组 CpG 位点中的一小部分，不同细胞覆盖的位置也不同。

传统流程通常把基因组切成固定的大窗口，例如 100 kb，然后计算每个细胞在每个窗口中的甲基化比例，再对细胞 × 窗口矩阵做 PCA。这个做法有两个核心问题：

1. **信号稀释。** 真正具有细胞类型差异的调控区可能很小，放进 100-kb 大窗口后会被大量稳定、高甲基化或低甲基化的 CpG 淹没。
2. **读段位置混淆。** 一个区域内部的平均甲基化可能沿基因组位置显著变化。如果两个细胞的读段分别落在区域的不同部分，即使重叠位置上的甲基化状态一致，简单平均也可能给出很不同的区域甲基化比例。

论文 Fig. 1 的实际图像直接展示了第二个问题：cell 1 和 cell 2 的原始区域甲基化比例分别显示为 22% 和 77%，但两条读段在重叠位置并不矛盾。差异主要来自它们覆盖了区域内不同的局部背景。

### 2. 与已有方法相比，MethSCAn 补了什么缺口？

- Luo 等人在 *Science*（2017）中用 100-kb 窗口汇总神经元单细胞甲基化数据。这种表示容易丢失局部信号。
- Melissa（*Genome Biology*, 2019）和 scMET（*Genome Biology*, 2021）对单细胞甲基化或异质性进行贝叶斯建模；EpiScanpy（*Nature Communications*, 2021）提供单细胞表观组分析框架。MethSCAn 论文强调，这些工具通常需要用户预先指定要量化的基因组区间，而 MethSCAn 可以从数据本身发现一组紧凑的 VMR。
- MOFA+（*Genome Biology*, 2020）能够处理多组学和缺失数据，论文把它作为下游降维基线之一；但它不负责回答“应当在基因组的哪些区间量化甲基化”以及“如何避免读段位置偏差”这两个上游问题。
- 论文引用的 DMR 方法主要面向 bulk 或 targeted bisulfite sequencing。MethSCAn 提供了针对 scBS 两组细胞的可变长度 DMR 扫描和经验 FDR 估计。

因此，MethSCAn 的主要创新不在于创造一种新的通用聚类器，而在于为 scBS 构造更好的上游特征和区域分数。

### 3. 输入、输出与整体流程

#### 输入

- 每个细胞一个甲基化报告文件，可来自 Bismark、methylpy/allc、BISCUIT 或兼容的自定义格式；
- 若要量化指定区域，需要一个 BED 文件；
- 若要检测 DMR，需要一个把细胞分成恰好两组的标签文件。

#### 输出

- 按染色体存储的稀疏甲基化矩阵和细胞 QC 统计；
- 每个 CpG 的平滑跨细胞甲基化背景；
- VMR BED 表；
- 细胞 × 区域的甲基化比例、残差分数和覆盖度矩阵；
- DMR 坐标、Welch 统计量、两组甲基化比例和调整后的经验 FDR。

#### 计算流程

```text
每细胞甲基化报告
        |
        v
prepare：解析 0/1 调用，按染色体存为稀疏矩阵，生成细胞 QC
        |
        v
smooth：估计每个 CpG 的局部跨细胞背景甲基化 x~_i
        |
        +-------------------------------+
        |                               |
        v                               v
scan：滑动窗口计算残差方差             用户提供的 BED 区域
选高方差窗口并合并成 VMR                 |
        |                               |
        +-----------> 待量化区域集合 <---+
                         |
                         v
matrix：细胞 × 区域残差/比例/覆盖度矩阵
                         |
                         v
迭代 PCA 或其他矩阵分解 -> 邻居图、UMAP、聚类、轨迹

两组细胞标签 + 已准备并平滑的数据
        |
        v
diff：滑动窗口 Welch 统计
      + 每 2 Mb 更换一次的标签置换
      + 合并窗口 + 经验 FDR
        |
        v
DMR 表
```

论文 Fig. 6 的实际图像与这条流程一致。当前代码直接实现 `prepare`、`smooth`、`scan`、`matrix` 和 `diff`；论文描述的迭代 PCA 在本次获得的源码快照中 **Not found**。

### 4. 数据表示：如何保存极稀疏的 scBS 数据？

论文把 CpG 位点 $i$ 在细胞 $j$ 中的甲基化状态记为

$$
x_{ij}\in\{0,1,\mathrm{NA}\},
$$

其中 0 表示未甲基化，1 表示甲基化，NA 表示该细胞没有读段覆盖这个位点。

定义覆盖位点 $i$ 的细胞集合：

$$
{C}_{i}=\{j\in C:{x}_{ij}\ne \mathrm{NA}\},
$$

以及细胞 $j$ 覆盖的 CpG 集合：

$$
{G}_{j}=\{i:{x}_{ij}\ne \mathrm{NA}\}.
$$

源码使用一个适合稀疏矩阵的存储编码：甲基化为 $+1$，未甲基化为 $-1$，缺失值存为稀疏零。`prepare` 先把数据分块写成 COO，再转成按染色体的 CSR 矩阵，同时输出每个细胞的覆盖 CpG 数量和全局甲基化水平（`MethSCAn/methscan/prepare.py:16-71,113-165`）。

如果同一位点的多个读段互相矛盾，默认会丢弃为缺失；可选多数表决，但 50:50 的情况仍然丢弃。这与论文的原始数据规则基本一致。

### 5. 第一步：估计 CpG 的局部背景甲基化

先在每个 CpG 位点上，对所有有覆盖的细胞求平均：

$$
{\overline{x}}_{i}=\frac{1}{|C_i|}\sum_{j\in C_i}x_{ij}.
$$

由于单个位点覆盖的细胞可能很少，${\overline{x}}_i$ 会很噪。MethSCAn 再沿基因组位置做核平滑：

$$
{\tilde{x}}_{i}=
\frac{\sum_{i'}{\overline{x}}_{i'}k_h(d_{ii'})}
{\sum_{i'}k_h(d_{ii'})},
$$

其中使用 tricube 核：

$$
k_h(d)=
\begin{cases}
\left(1-|d/h|^3\right)^3, & |d|<h,\\
0, & \text{其他情况}.
\end{cases}
$$

论文默认 $h=1{,}000$ bp。${\tilde{x}}_i$ 可以理解为：如果不知道某个细胞在该 CpG 的特殊状态，仅根据所有细胞和附近位点，预期它的甲基化水平是多少。

#### 代码验证与带宽歧义

当前 v1.1.0 源码明确构造了 tricube 核，并可选用 $\log(1+\mathrm{coverage})$ 作为额外权重（`MethSCAn/methscan/smooth.py:16-45`）。但是，源码把 CLI 的 `bandwidth=1000` 转成 `hbw=500`，窗口大致使用两侧各 500 bp；论文公式则把 $h=1{,}000$ 写成核支持半径。因此这是 **Partial** 匹配：可能只是“总宽度”和“半径”的命名约定不同，也可能造成实际平滑范围差异。

### 6. 第二步：用“收缩残差均值”量化细胞在区域中的甲基化

传统区域甲基化比例为

$$
m_{Ij}=\left\langle x_{ij}\right\rangle_{i\in I\cap G_j}.
$$

MethSCAn 先计算位点残差：

$$
r_{ij}=x_{ij}-{\tilde{x}}_i,
$$

再对区域 $I$ 中该细胞实际覆盖的 CpG 求收缩平均：

$$
r_{Ij}=\frac{1}{n_{Ij}+1}
\sum_{i\in I\cap G_j}\left(x_{ij}-{\tilde{x}}_i\right),
$$

其中 $n_{Ij}=|I\cap G_j|$ 是该细胞在该区域中观测到的 CpG 数量。

这个分数的含义是：

- $r_{Ij}>0$：该细胞在此区域比跨细胞局部背景更甲基化；
- $r_{Ij}<0$：比背景更低甲基化；
- 绝对值接近 0：没有强证据表明它偏离背景；
- 覆盖越少，分母中的 `+1` 带来的收缩越强。

源码 `_calc_mean_shrunken_residuals` 逐个观测 CpG 减去平滑值，并除以 `n_obs + 1`，与核心公式直接对应（`MethSCAn/methscan/numerics.py:5-61`）。

#### 公式记号中的一个问题

转换后的论文 Eq. 1 在分母和求和集合中写成了 $I\cap C_i$，但 $I$ 是 CpG 位点集合，$C_i$ 是细胞集合，二者不能直接相交。结合前文定义和源码，实际计算量应是细胞 $j$ 在区域中的覆盖位点集合 $I\cap G_j$。这里不把排版问题伪装成新公式，而是明确说明其可执行含义。

#### 缺失值：论文描述与当前代码不同

论文说完全没有覆盖的 cell-region 元素可以先填 0，再由迭代 PCA 改进。当前 `numerics.py` 和 dense `matrix.py` 保留为 `NaN`，稀疏输出则省略该元素。这样可以区分“观测后残差恰好接近 0”和“根本没有观测”，但要求下游工具显式处理缺失值。

### 7. 第三步：从数据中发现 VMR

对任意区域 $I$，论文定义残差分数在有覆盖细胞中的方差：

$$
v_I=\frac{1}{|C_I|}\sum_{j\in C_I}
\left(r_{Ij}-\left\langle r_{Ij'}\right\rangle_{j'\in C_I}\right)^2.
$$

VMR 扫描过程为：

1. 沿染色体放置大量相互重叠的窗口；
2. 在每个窗口中计算所有细胞的 $r_{Ij}$；
3. 计算跨细胞方差 $v_I$；
4. 选择高方差尾部，默认含义为前 2%；
5. 合并相互重叠的高方差窗口；
6. 对合并后的区域重新计算方差，并按覆盖细胞数过滤。

当前 CLI 默认 VMR 窗口宽度 2,000 bp、步长 100 bp、高方差比例 0.02、至少 6 个细胞有覆盖。论文 benchmark Methods 对 Kremer 数据报告的步长是 10 bp，因此“论文 benchmark 参数”和“当前 CLI 默认值”不能混为一谈。

#### 当前实现的近似

论文用“全基因组窗口中方差最高的 2%”来解释方法。当前 `scan.py` 先按文件大小选最大的染色体，在该染色体上确定方差分位数阈值，然后把同一阈值用于其他染色体（`MethSCAn/methscan/scan.py:117-171`）。这是一个提高效率的实现近似，并不等价于先汇总所有染色体窗口再求统一分位数。

### 8. 第四步：构造细胞 × 区域矩阵

`methscan matrix` 可以接收 VMR，也可以接收任意 BED 区域。dense 输出包括：

- 甲基化比例；
- 收缩残差均值；
- 总观测 CpG 数；
- 甲基化 CpG 数。

sparse 输出只保留有观测的 cell-region 配对，并记录残差、比例和覆盖度（`MethSCAn/methscan/matrix.py:13-157,171-276`）。

这个矩阵相当于 scRNA-seq 中的细胞 × 基因矩阵，但列是 VMR 或其他基因组区域，数值不是表达量，而是相对局部背景的甲基化偏离。

### 9. 第五步：迭代 PCA 如何处理缺失值？

论文提出的迭代 PCA 为：

1. 对矩阵 $A$ 按特征中心化；
2. 把缺失值暂时填成 0；
3. 做截断 SVD/PCA，得到 $A\approx X R^\top$；
4. 只用低秩重构值替换原来的缺失元素；
5. 再做 PCA；
6. 重复直到收敛。

PCA 得到的前 $R$ 个分量作为每个细胞的低维向量，细胞间欧氏距离可以用于近邻图、UMAP、Leiden/Louvain 聚类和轨迹分析。

**Not found：** 在本次获得的 MethSCAn Python/YAML 源码中，没有找到 PCA、SVD 或反复低秩插补的实现；benchmark Snakemake 工作流也不在快照中。当前仓库负责产生矩阵，但论文中的迭代 PCA 很可能位于教程或 benchmark 分析层。

### 10. 第六步：检测两组细胞之间的 DMR

对细胞组 $A$ 和 $B$，先计算区域残差均值和组内方差：

$$
\mu_I^g=\left\langle r_{Ij}\right\rangle_{j\in g},\qquad g=A,B,
$$

$$
v_I^g=\frac{1}{|C_g|-1}\sum_{j\in g}\left(r_{Ij}-\mu_I^g\right)^2,
$$

再计算 Welch 统计量：

$$
t_I=\frac{\mu_I^A-\mu_I^B}
{\sqrt{v_I^A/|C_A|+v_I^B/|C_B|}}.
$$

与 VMR 类似，DMR 算法扫描重叠窗口，分别选取正负两侧的极端 $t$ 值窗口，按符号合并，再对合并区域重新计算统计量。

#### 为什么需要置换？

直接套用普通 Welch *t* 检验的理论分布不可靠，因为：

- 不同细胞覆盖度不同；
- 先选择极端窗口、再合并窗口改变了候选区域的统计分布；
- 常规多重检验假设不能直接覆盖这套选择流程。

因此，MethSCAn 对细胞组标签做置换，并让置换每 2 Mb 改变一次，从一次全基因组扫描中收集许多局部 null 峰。当前源码直接实现了这一步（`MethSCAn/methscan/diff.py:26-38,163-225,385-535`）。

把真实峰统计量集合记为 $T$，置换峰集合记为 $T_0$，则阈值 $|t_i|$ 对应的经验调整值为

$$
p_i^{\mathrm{adj}}=
\frac{|\{t_j\in T_0:|t_j|>|t_i|\}|/|T_0|}
{|\{t_j\in T:|t_j|>|t_i|\}|/|T|}.
$$

源码再从尾部取累计最小值，使调整值单调且不超过 1（`MethSCAn/methscan/diff.py:41-74,553-573`）。

#### 统计结论的边界

这里的统计单位是细胞，不是独立生物样本。显著 DMR 表示：如果从同一个生物样本再抽取一批细胞，较可能再次检测到该区域；它不自动证明该差异可以推广到其他动物或患者。

### 11. 论文如何评估方法？

#### 主数据集

Kremer 等人的小鼠前脑配对多组学数据包含 1,566 个细胞，同时有单细胞甲基化组和转录组。转录组聚类标签作为“参考真值”，用于检查甲基化表示是否能恢复相同细胞类型或状态。

比较维度包括：

- 区域：VMR、ENCODE cCRE、启动子、100-kb 窗口；
- 量化：原始甲基化比例、收缩残差均值；
- 降维：迭代 PCA、高质量特征 PCA、均值插补 PCA、MOFA+；
- 指标：15 维空间中的 mean neighbor score，即每个细胞的近邻中有多少比例与其参考标签相同。

#### 其他数据集

- Luo 等人的小鼠神经元亚型，*Science*（2017）；
- Argelaguet 等人的小鼠原肠胚形成，*Nature*（2019）；
- Bian 等人的人结直肠癌多组学，*Science*（2018）；
- Liu 等人的约 10 万小鼠脑细胞甲基化图谱，*Nature*（2021）。

### 12. 图像证据支持了哪些结论？

- **Fig. 3：** 最近 VMR 的甲基化与附近基因表达的相关分布比启动子更宽、更偏负；*Htra1* 下游 VMR 随表达升高而低甲基化。它支持关联，不证明因果调控。
- **Fig. 4：** VMR 残差得到的 UMAP 比 100-kb 平均甲基化更清楚地区分多个细胞类型；neighbor score 中 VMR 和调控元件通常领先于大窗口和启动子。
- **Extended Data Fig. 1：** VMR 在较少特征数下与完整 ENCODE cCRE 集合竞争，并显著节省运行时间和内存。图中 Kremer VMR 数为 63,618，而正文写 63,421；本分析保留这个不一致。
- **Extended Data Fig. 2：** VMR/残差组合在多个数据集上总体有竞争力，但最佳方法随数据集和降维方式变化，不能概括成“任何情况下都绝对最好”。
- **Extended Data Fig. 3：** 默认参数位于较宽的稳定区；特别大的窗口会降低较难的连续状态数据集表现。
- **Extended Data Fig. 4：** 方法可用于 CH 甲基化，并在 100,350 个脑细胞上完成分析。论文报告 256 GB RAM、48 CPUs 下约一周，按染色体并行 prepare 后约两天。
- **Fig. 5：** 真实标签产生的 DMR 效应强于置换标签；少甲基化于少突胶质细胞的 DMR 富集于髓鞘相关功能，少甲基化于 NSC 的 DMR 富集于干细胞维持功能；*Mbp* 附近给出一个具体实例。

### 13. 代码与论文的一致性

总体保真度：**中等**。

| 模块 | 状态 | 说明 |
|---|---|---|
| 稀疏数据准备与 QC | Exact | 当前源码直接实现按染色体 CSR 和细胞统计 |
| 收缩残差均值 | Exact | 明确计算观测甲基化减平滑背景，并除以 `n_obs + 1` |
| VMR 窗口扫描与合并 | Exact/实现近似 | 核心过程一致，但阈值从最大染色体校准 |
| 区域矩阵输出 | Exact | dense/sparse 均实现残差、比例和覆盖度 |
| DMR Welch、置换和经验 FDR | Exact | 每 2 Mb 更换置换并计算累计 null/real 比例 |
| 平滑带宽 | Partial | 论文的 $h$ 与当前源码的总带宽/半径约定不清楚 |
| 迭代 PCA | Not found | 论文有完整算法描述，当前源码快照没有实现 |

版本也需要区分：论文 benchmark 使用 MethSCAn v0.6.2；本地源码 commit `72f38fbec6995b849726dd508765e327c298a307` 的 `pyproject.toml` 声明 v1.1.0。核心算法可识别，但不能据此宣称数值完全复现论文 benchmark。

### 14. 研究者应如何理解 MethSCAn 的价值？

MethSCAn 最关键的思想是把“区域甲基化”拆成两个问题：

1. 这个 CpG 在所有细胞和附近位置上的正常背景是多少？
2. 某个细胞在实际观测到的位置上，相对这个背景偏离多少？

这样做把由读段落点不同造成的技术变异，与相对背景的生物学偏离尽量分开。再用 VMR 把注意力集中到真正跨细胞变化的区域，可以得到更紧凑、更适合计算细胞距离的特征集合。DMR 模块则把同一残差表示扩展到两组细胞比较。

### 15. 已知缺口与复现建议

- 无科学补充材料 Markdown；本分析以完整 Nature HTML 论文和本地图像为主证据。
- 迭代 PCA、benchmark Snakemake 工作流和精确的 v0.6.2 快照 **Not found**。
- 当前平滑带宽约定和 VMR 最大染色体阈值近似需要在精确复现时单独核对。
- 论文与扩展图的 VMR 数量有 63,421 与 63,618 的小不一致。
- 若目标是理解或重实现核心方法，论文公式和当前源码已足够覆盖 prepare、smooth、residual、VMR、matrix 和 DMR。
- 若目标是精确复现论文所有 benchmark，应进一步取得 v0.6.2、原始 Snakemake 流程、迭代 PCA 代码、对应数据预处理和固定软件环境。

### 总结

MethSCAn 的贡献是一套适合稀疏 scBS 的特征工程和区域统计框架：局部背景校正减少读段位置偏差，收缩降低低覆盖噪声，VMR 提高特征信息密度，置换 DMR 扫描增强组间差异的可解释性。论文图像和多个数据集 benchmark 支持它在测试场景中改善细胞邻域恢复并降低部分计算成本；但源码快照缺失迭代 PCA 和原始 benchmark 流程，因此“核心算法可验证”与“整篇论文可一键精确复现”必须分开评价。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MethSCAn: concise paper summary

### What problem does it solve?

Single-cell bisulfite sequencing (scBS) measures DNA methylation at single-cell and single-base resolution, but each cell covers only a sparse and uneven subset of genomic CpGs. A common analysis strategy divides the genome into large fixed tiles, averages observed methylation within every cell and tile, imputes missing values, and then applies PCA. MethSCAn argues that this can lose signal in two ways: a small informative region can be diluted inside a large tile, and cells can appear different simply because their reads cover different subparts of a spatially heterogeneous interval.

The paper introduces a preprocessing and comparison toolkit that is aware of local read position, discovers informative variably methylated regions (VMRs) from the data, and detects differentially methylated regions (DMRs) between two cell groups.

### Context and limitations of prior approaches

- Luo et al., *Science* (2017), analyzed neuronal single-cell methylomes using CH methylation in 100-kb genomic tiles. This supplies PCA-compatible features but fixed large bins can dilute localized CpG signals.
- Melissa, *Genome Biology* (2019), and scMET, *Genome Biology* (2021), model single-cell methylation and heterogeneity, while EpiScanpy, *Nature Communications* (2021), provides general single-cell epigenomic analysis. The MethSCAn paper's stated distinction is that these workflows require the genomic intervals to be supplied rather than discovering a parsimonious set of variable intervals directly from the scBS data.
- MOFA+, *Genome Biology* (2020), handles missing multimodal measurements and is included as a downstream benchmark baseline. It does not itself solve MethSCAn's upstream question of where and how to quantify methylation along the genome.
- Existing DMR tools cited by the paper target bulk or targeted bisulfite sequencing. The authors state that a variable-width, FDR-controlled DMR scan specifically for scBS cell groups had not previously been reported.

### Core method

MethSCAn converts per-cell methylation reports into chromosome-wise sparse matrices, estimates a smoothed across-cell methylation baseline at each CpG, and scores a cell in a region by the shrunken mean of its residuals from that baseline:

$$
r_{Ij}=\frac{1}{n_{Ij}+1}\sum_{i\in I\cap G_j}\left(x_{ij}-{\tilde{x}}_i\right).
$$

Here $x_{ij}$ is the observed binary methylation call, ${\tilde{x}}_i$ is the local ensemble baseline, and $n_{Ij}$ is the number of CpGs observed for cell $j$ in interval $I$. The extra one shrinks low-coverage measurements toward zero.

To discover VMRs, MethSCAn slides overlapping windows along each chromosome, calculates the variance of $r_{Ij}$ across cells, selects a high-variance tail, and merges overlapping selected windows. These adaptive regions become columns of a cell-by-region matrix for PCA, UMAP, clustering, or other downstream analyses.

For two-group DMR detection, it replaces variance by a Welch statistic, separately merges extreme positive and negative windows, and estimates false discovery rates from label permutations that change every 2 Mb. Cells—not biological samples—are the statistical units, so significance supports repeatability under resampling cells from the same sample rather than generalization to independent organisms.

### What is novel?

1. **Read-position-aware quantitation:** each observed CpG is compared with a locally smoothed across-cell expectation before regional aggregation.
2. **Data-driven feature discovery:** overlapping-window variance identifies compact VMRs instead of requiring fixed tiles or external regulatory annotations.
3. **Coverage-aware shrinkage:** a pseudocount reduces the influence of weakly covered cell-region pairs.
4. **Single-cell DMR scanning:** Welch statistics, variable-width peak merging, and a spatially varying permutation null provide empirical FDR estimates.
5. **Integrated command-line workflow:** preparation, QC support, smoothing, VMR discovery, matrix construction, and DMR discovery are exposed through a Python CLI.

### Evaluation

The primary paired multi-omics benchmark contains 1,566 mouse-forebrain cells. Transcriptome-derived cell labels serve as the reference for evaluating methylation-derived neighborhoods. The comparison crosses:

- four feature sets: VMRs, ENCODE candidate cis-regulatory elements, promoters, and 100-kb tiles;
- two quantitation methods: raw methylation fractions and shrunken residual means; and
- four dimension-reduction strategies: iterative PCA, two mean-imputed PCA variants, and MOFA+.

The main metric is the mean fraction of same-label neighbors in a 15-dimensional representation. The authors also repeat the benchmark on neuronal subtypes, mouse gastrulation, and colorectal-cancer sampling regions, subsample cells to test small datasets, sweep VMR parameters, analyze CH methylation, and run the default workflow on 100,350 mouse-brain cells.

#### Main results supported by the figures

- Nearest-VMR methylation has a broader and more negative correlation with nearby gene expression than promoter methylation in the paired forebrain data; the *Htra1* locus illustrates a downstream VMR losing methylation as expression increases.
- VMR residuals produce clearer separation of several cell types than average methylation in 100-kb tiles and generally yield higher neighbor scores than tiles or promoters.
- In the primary benchmark, VMRs are competitive with 339,815 ENCODE regulatory elements while using roughly 63,000 regions; the extended figure shows lower runtime and memory than the full regulatory-element set.
- Cross-dataset results are broadly favorable but not uniformly dominated by one method: regulatory elements or alternative factorizations are comparable in some settings.
- Performance is stable across a useful range of VMR parameters, although very wide windows degrade the harder continuous-state forebrain dataset.
- DMRs between 58 oligodendrocytes and 130 neural stem cells show stronger effects than permuted labels and are enriched near genes with coherent myelination or stem-cell functions. An example near *Mbp* is hypomethylated in oligodendrocytes.
- The paper reports analysis of 100,350 cells in about one week on 256 GB RAM and 48 CPUs, with chromosome-parallel preparation reducing the total to about two days.

### Verified code behavior

The acquired repository implements the central preparation, smoothing, regional residual, VMR, matrix, and DMR algorithms. Direct source reads confirm sparse $+1/-1$ methylation storage, the residual denominator `n_obs + 1`, merged sliding-window peaks, Welch statistics, a new label permutation every 2 Mb, and cumulative empirical FDR ratios.

Overall paper-code fidelity is **medium**:

- **Exact core matches:** preparation, shrunken residual scoring, VMR scanning/merging, matrix construction, and permutation-based DMR calling.
- **Partial:** the smoothing CLI calls 1,000 bp a bandwidth, while the current implementation uses half that value as its kernel radius.
- **Not found:** iterative PCA, the benchmark Snakemake workflow, and the exact benchmarked v0.6.2 code snapshot.
- **Version caveat:** the acquired commit `72f38fbec6995b849726dd508765e327c298a307` declares v1.1.0, whereas the paper reports benchmarks with v0.6.2.
- **Threshold caveat:** current VMR code calibrates its variance cutoff on the largest chromosome and reuses it, an implementation shortcut relative to the paper's genome-wide top-2% description.

### Reproducibility assessment: 3/5

**Strengths:** open paper, public GEO accessions, public Python package, tutorial/documentation link, inspectable core algorithms, explicit parameter defaults, and local availability of all main and extended-data figures.

**Limitations:** the acquired snapshot lacks iterative PCA and the benchmark workflow, differs from the reported benchmark release, and no scientific supplementary Markdown was acquired. The paper also contains a small VMR-count inconsistency: Results report 63,421 regions, while Extended Data Fig. 1 labels 63,618.

The core method can be understood and largely reimplemented from the paper and source, but exact reproduction of every benchmark requires the original v0.6.2 release, workflow, and downstream iterative-PCA code.

### Bottom line

MethSCAn's main contribution is an upstream representation of sparse scBS data: quantify cells relative to a local methylation baseline and let the data define compact variable regions. The tested results indicate that this representation can improve biological neighborhood recovery while reducing feature count and enabling interpretable DMR discovery. Its strongest evidence is methodological and benchmark-based; causal regulation and cross-sample statistical generalization remain outside the claims supported here.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
