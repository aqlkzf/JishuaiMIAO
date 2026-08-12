---
layout: default
permalink: /paper-atlas/umaia-bf742961/
title: "uMAIA"
nav: false
description: "uMAIA（unified Mass Imaging Analyzer）解决的是一个“多次质谱成像采集如何真正放到同一坐标系里比较”的问题：它先从每张 MALDI-MSI 原始谱中自适应地找峰并生成离子图像，再用网络流把不同切片中属于同一分子的峰连接成统一特征，最后用分层概率模型校正跨采集的强度畸变，从而支持 3D/4D 代谢图谱分析。"
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>uMAIA</h1>
    <p>Unified mass imaging maps the lipidome of vertebrate development</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## uMAIA 方法详解：把多张质谱成像切片统一成 3D/4D 代谢图谱

### 1. 一句话理解

uMAIA（unified Mass Imaging Analyzer）解决的是一个“多次质谱成像采集如何真正放到同一坐标系里比较”的问题：它先从每张 MALDI-MSI 原始谱中自适应地找峰并生成离子图像，再用网络流把不同切片中属于同一分子的峰连接成统一特征，最后用分层概率模型校正跨采集的强度畸变，从而支持 3D/4D 代谢图谱分析。

论文将这套框架用于斑马鱼 8、24、48、72 hpf 四个发育阶段，重建了百余种脂质的时空分布，并发现脂质组成能够精细描绘胚胎解剖结构。

### 2. 为什么这个问题难

一张 MSI 图像不是普通的显微图像。每个像素位置都对应一条质谱，横轴是 $m/z$，纵轴是信号强度。若只分析一张切片，研究者尚可手动选择峰区间；但要把几十张甚至上百张切片合成一个 3D/4D 图谱，会遇到三个层层传递的问题。

#### 2.1 同一个分子的峰位置会漂移

仪器误差和空间依赖的质量偏移使同一种离子在不同像素、不同切片中的 $m/z$ 不完全相同。固定宽度 bin 可能：

- 把两个准同量异位分子合并成一张图；
- 把同一个峰拆成多个互补的“棋盘状”图像；
- 对不同分子使用相同宽度，忽略其质量漂移范围不同。

Mirion（*Journal of the American Society for Mass Spectrometry*, 2013）属于静态 bin 方法。MALDIquant（*Bioinformatics*, 2012）能够自适应分箱，但主要从强度峰出发，容易让高强度峰主导区间边界。

#### 2.2 不同 acquisition 的峰表不在同一特征空间

每张切片独立找峰后，峰数量和精确 $m/z$ 均不同。窄 bin 会漏配，宽 bin 会把同一切片里的多个峰分到同一特征，形成歧义。数据规模增大后，简单最近邻或参考峰对齐很难同时保证召回率和一致性。

#### 2.3 强度的批次效应不是简单的均值平移

MALDI-MSI 的对数强度常呈双峰：低强度背景峰和高强度前景峰。不同切片中的前景峰会发生不同程度的平移和展宽。ComBat（*Biostatistics*, 2006）等转录组批次校正方法假设的数据分布并不适合这一结构；scArches（*Nature Biotechnology*, 2021）会通过深度模型重组特征，也不符合论文希望“尽量少做假设、不插补、不改变特征定义”的保守原则。

### 3. 输入、输出与整体流程

#### 3.1 输入

- 每个 acquisition 的 `.IBD` 和 `.imzML` 原始文件；
- 每条质谱对应的空间坐标；
- 仪器质量分辨率、待分析 $m/z$ 范围；
- 多张切片的组织 mask；
- 可选的协变量/设计矩阵；
- 下游脂质注释所需的 LC–MS/MS 定量结果。

#### 3.2 核心输出

- 每个 acquisition 的峰区间表 `ranges.csv`；
- 每个 acquisition 的离子图像 `images.h5ad`；
- 跨 acquisition 的 `molecule_ID` 统一特征表；
- 按“统一分子 × 切片”组织的 Zarr 图像堆栈；
- 归一化参数与归一化后的图像堆栈；
- 下游 3D/4D 体数据、脂质 territory 和发育 pseudolineage。

#### 3.3 计算链

```text
每张切片的原始 .IBD/.imzML
        │
        ▼
① 自适应峰调用
  像素检测次数直方图 → 平滑 → 找种子 → 扩展峰区间
  → 在每个区间内积分强度并做 TIC 归一化
        │
        ├── ranges.csv
        └── images.h5ad
        │
        ▼
② 网络流跨切片匹配
  按 1 Da 分块 → 构造候选边 → 二元最小费用流
  → 多个 acquisition 排列中选最优解 → 连通分量成为统一特征
        │
        ├── molecule_ID 表
        └── matched Zarr
        │
        ▼
③ 分层贝叶斯归一化
  mask / 平滑 / log → GMM 初始化 → NumPyro MAP 拟合
  → 观测 CDF 映射到参考 inverse CDF
        │
        └── normalized Zarr
        │
        ▼
④ atlas 分析
  切片配准 → 3D 重建 → 特征过滤 → PCA / k-means / Moran's I
  → 脂质 territory、发育关系与解剖解释
```

### 4. 模块一：基于“检测次数”的自适应峰调用

### 4.1 为什么不用强度找峰边界

设 $S_{p,m}$ 为稀疏谱矩阵：$p$ 是像素，$m$ 是离散化后的质量位置。uMAIA 首先只关心“这个位置是否检测到信号”，定义：

$$
f_m=\sum_p\left(S_{p,m}>0\right).
$$

$f_m$ 是某个 $m/z$ 在多少像素中出现的频数。它反映的是峰在空间样本中的重复出现范围，而不是峰有多强。这样，一个强度低但在明确组织区域稳定出现的离子不会被高强度峰掩盖。

代码对应：

- `uMAIA/uMAIA/peak_finding/peak_finder.py:69-99`：把谱矩阵二值化、统计出现次数、构造直方图并高斯平滑；
- `uMAIA/uMAIA/peak_finding/_run.py:75-94`：在低频位置附近切分大 $m/z$ 范围，便于并行处理。

### 4.2 Algorithm 1：逐步降低阈值寻找峰种子

论文先把直方图最大值位置放入种子集合 $\mathcal{M}$，再让阈值 $t$ 从最大频数逐步下降。每次找到所有 $f_m>t$ 的连续区间；如果某个新区间还没有已有种子，就在其中加入一个新种子。

```text
M ← {arg max_m f_m}
t ← max_m f_m
while t ≠ 0:
    t ← t - 1
    找出 f > t 的所有连续区间 D
    对每个 d ∈ D:
        若 d 中没有已有种子:
            将 d 的中心加入 M
```

直觉上，这相当于让“水位”从峰顶逐渐下降：一个真正独立的峰会在某个水位形成新的岛屿，因此获得自己的种子。

代码 `PeakFinder.fit` 在 `peak_finder.py:121-145` 中按下降阈值收集连续区域，并加入尚未被已有种子覆盖的位置。

### 4.3 Algorithm 2：从种子向两侧扩展

对每个种子 $m\in\mathcal{M}$，算法向左、向右扩展，直到：

- 直方图不再向外下降；
- 达到背景阈值；
- 或接近另一峰的影响范围。

所有峰区间构成 $\mathcal{B}$。这种一维 watershed 思路允许不同峰拥有不同宽度，适应峰特异的质量漂移。

直接实现位于 `peak_finder.py:147-185`。

### 4.4 从峰区间生成图像

对像素 $p$ 和峰/化合物 $c$：

$$
X_{p,c}=\sum_{m\in\mathcal{B}_c}S_{p,m}.
$$

随后按像素总离子流做归一化：

$$
X_{pc}\leftarrow \frac{X_{pc}}{\sum_cX_{pc}}.
$$

最终写出：

- `ranges.csv`：`min`、`max`、`mz_estimated`、检测像素数、浓度等；
- `images.h5ad`：每个峰对应一列空间图像。

对应源码为 `_run.py:42-59,195-255` 和 `extract_images.py:68-118`。

### 4.5 论文与代码的一个细节差异

论文写的是 $10\times10^{-5}$ 的质量 bin；当前 `PeakFinder.process` 使用 `mz_resolution * 7` 作为直方图步长（`peak_finder.py:71-74`）。CLI 和库函数默认参数也不完全相同。因此“频数 + watershed”核心逻辑是 **Exact**，但具体离散化属于 **Partial**，复现时应保存真实调用参数。

### 5. 模块二：用网络流建立统一特征空间

### 5.1 把峰看成图节点

第 $i$ 个 acquisition 的峰集合记为 $\mathcal{A}_i$，全部峰的并集为：

$$
\mathcal{A}=\bigcup_i\mathcal{A}_i,\qquad |\mathcal{A}|=L.
$$

每个峰是一个节点。若两个峰来自不同 acquisition，且 $m/z$ 距离小于阈值 $t$，就允许一条候选边，记为 $G_{ij}=1$。真正选中的同分子连接由二元变量 $X_{ij}$ 表示，边代价 $C_{ij}$ 是 $m/z$ 距离。

### 5.2 最小费用流目标

论文的核心优化是：

$$
\begin{array}{lll}
\mathop{\min}\limits_{\boldsymbol{X}}&&
\mathop{\sum}\limits_{i=1}^{L}\mathop{\sum}\limits_{j=1}^{L}X_{ij}C_{ij}\\
{\rm subject\;to}&&X_{ij}\in\{0,1\}\\
&&X_{ij}\le G_{ij}\\
&&\mathop{\sum}\limits_jX_{ij}=\mathop{\sum}\limits_iX_{ij}=1,
\quad \forall i,j\notin\{\rm start,end\}.
\end{array}
$$

这些约束的作用是：

- 只能选择允许的候选边；
- 每个普通节点恰有一条进入边和一条离开边；
- 一条路径不能在同一 acquisition 中吸收多个峰；
- 若找不到可信连接，可以通过高代价的 start/end 边结束路径。

Gurobi 实现位于 `uMAIA/uMAIA/molecule_matching/_moleculematch.py:184-240`。

### 5.3 为什么要分块和打乱 acquisition 顺序

直接在全部峰上解整数规划太大。论文采用：

1. 按 1 Da 区间拆成许多小问题；
2. 只连接一定范围内的相邻 acquisition；
3. 随机打乱 acquisition 顺序，多次求解并选择目标值最优的结果。

代码入口 `match` 位于 `_match.py:18-71`，排列评估在 `_moleculematch.py:259-287`。选中边最后被转成无向连通分量，每个连通分量就是一个 `molecule_ID`（`_match.py:173-188`）。

### 5.4 一个重要的代码—论文差异

论文明确写所有分析使用 $k=2$ 个连续 acquisition。当前公开 wrapper 却传入：

```python
NUM_SKIP = ceil(NUM_S / 2)
```

并让 `K` 至少等于 `NUM_SKIP`（`_match.py:89-94`; `_moleculematch.py:42-50`）。当切片很多时，代码检查的前驱范围明显大于论文的 $k=2$。因此：

- 二元流目标和约束：**Exact**；
- 随机排列和选最优解：**Exact**；
- 候选邻域：**Partial**。

### 5.5 实际输出与失败模式

输出表包含 `molecule_ID`、每张切片的峰边界、`mz_estimated`、`section_ix`、浓度和共识 $m/z$。教程还会用 `filter_matches` 保留在所有 acquisition 中出现的完整特征，再通过 `to_zarr` 写成统一图像堆栈。

需要特别注意：`retrieve_setlist` 使用宽泛的 `except`；一旦 Gurobi 或数据形状出错，它返回空匹配，外层代码会给每个峰分配独立 ID（`_match.py:39-48,89-95`）。因此“成功生成表格”不等于“成功完成跨切片匹配”，必须检查特征数、完整性和 Gurobi 日志。

### 6. 模块三：分层双高斯模型校正强度

### 6.1 从测量畸变到分位数映射

设化合物 $c$ 在 acquisition $a$ 的像素 $p$ 中真实强度为 $y_{cp}$，测量畸变为 $T_{ca}$：

$$
x_{cp}=T_{ca}(y_{cp}).
$$

目标是估计逆变换：

$$
\hat y_{cp}=\hat T_{ca}^{-1}(x_{cp}).
$$

令参考分布 CDF 为 $F_c$，观测分布 CDF 为 $G_{ca}$，则：

$$
G_{ca}=F_c\left(T_{ca}^{-1}(x)\right),
$$

所以归一化可以写为：

$$
\hat T_{ca}^{-1}(x)=\hat F_c^{-1}\left(\hat G_{ca}(x)\right).
$$

即先问“该值在本切片观测分布中处于哪个分位数”，再把这个分位数映射到统一参考分布。

### 6.2 为什么需要联合概率模型

若逐张图做普通 histogram matching，会把真实生物差异也抹掉，因为某张切片可能天然没有某个前景组织。uMAIA 因此联合所有 acquisition 和分子，假设对数强度由背景、前景两个高斯成分组成：

$$
\begin{aligned}
g(x_{pc}\mid\theta_{ca})={}&
\rho_{ca}\,\mathcal{N}\!\left(x_{pc};\mu_{ca}^{0},(\sigma_{ca}^{0})^2\right)\\
&+(1-\rho_{ca})\,\mathcal{N}\!\left(x_{pc};\mu_{ca}^{1},(\sigma_{ca}^{1})^2\right).
\end{aligned}
$$

最关键的低秩假设是：

$$
\mu_{ac}^{1}=\mu_{ac}^{0}+\gamma_a\lambda_c+\delta_c,
$$

$$
\sigma_{ac}^{1}=\Sigma_a+\Sigma_c.
$$

其中：

- $\gamma_a$：acquisition/切片特异因子；
- $\lambda_c$：分子特异因子；
- $\delta_c$：前景和背景的基础间隔；
- $\Sigma_a$、$\Sigma_c$：前景尺度的切片和分子成分。

论文用经验 batch-effect 矩阵做 SVD，发现 rank-one 近似解释约 31% 变异，为乘积项 $\gamma_a\lambda_c$ 提供依据。

### 6.3 初始化和 MAP 拟合

代码首先对每个特征分别拟合一成分和二成分 GMM，用 BIC 选模型。若选择单峰，就把该成分复制成两个模式，作为后续模型初始化（`normalization/_initialize.py:31-93`）。

NumPyro 模型位于 `_model.py:14-112`，包括：

- `b_gamma` 对应 $\gamma_a$；
- `b_lambda` 对应 $\lambda_c$；
- `sigma_s + sigma_v` 对应 $\Sigma_a+\Sigma_c$；
- `weights` 对应混合权重；
- `locs`、`scale1` 对应背景参数；
- `delta`/`delta_` 对应前景—背景间隔；
- 代码额外加入 `error[s,v]` 和协变量层级。

`normalize` 用 `AutoDelta` guide 和 SVI 求点估计/MAP，默认 Adam 学习率 0.001、5,000 步（`_normalize.py:58-101`）。教程保存的输出显示：3,882 个特征的 GMM 初始化约 53 秒，CPU 上 5,000 步 SVI 约 48 分 47 秒。

### 6.4 数据预处理中的隐藏细节

教程在归一化前：

- 使用每张切片的二维 mask；
- 设置高斯平滑 $\sigma=0.4$；
- 对强度做 $\log(x+0.0002)$；
- 把不同切片 padding 到统一像素维度。

实现位于 `utils/tools.py:174-251` 和 `uMAIA_tutorial.ipynb:504-510`。

默认 subsampling 还会取前 500 个像素，再从索引 2,000 以上随机取 2,000 个像素（`_initialize.py:9-18`; `_normalize.py:45-52`）。如果有效像素不足，必须显式关闭 subsample 或传入合法索引。

### 6.5 CDF 变换与论文公式的差异

论文的参考分布使用跨 acquisition 的参数平均：

$$
\mu_c^0={\rm mean}_a(\mu_{ca}^0),\quad
\sigma_c^0={\rm mean}_a(\sigma_{ca}^0),
$$

$$
\mu_c^1={\rm mean}_a(\mu_{ca}^1),\quad
\sigma_c^1={\rm mean}_a(\sigma_{ca}^1).
$$

当前 `_transform.py:39-89` 确实执行“观测 mixture CDF → 参考 inverse CDF”，但参考参数采用 `locs + delta_` 和 `sigma_v * 3`，而且观测/参考 CDF 都固定为两个成分各 0.5，没有使用拟合得到的 `weights`。因此变换类别吻合，但 Eq. (7) 的精确参数化是 **Partial**。

### 6.6 `delta_v_dist` 分支命名反转

论文写 $\delta_c\sim\mathrm{normal}(3,1)$。源码 `_model.py:48-58` 中：

- `delta_v_dist == 'gamma'` 时实际采样 Normal；
- 其他值时实际采样 `Gamma(5,2)`。

而 `normalize` 默认传入 `'gaussian'`。因此默认路径实际上使用 Gamma 先验。复现论文模型时不能只根据参数名判断，必须核对分支行为。

### 7. 从统一特征到 4D 脂质 atlas

三大模块完成后，论文执行以下下游分析：

1. 对 8、24、48、72 hpf 的连续矢状切片做仿射配准；
2. 拼接为 3D 数组，并用 $\sigma=0.4$ 的高斯滤波平滑；
3. 保留在 80% 切片中、至少 15% 像素非零的分子；
4. PCA 后保留解释超过 90% 方差的前十个成分；
5. 用 $k$-means 聚类像素，得到空间连续的“脂质 territory”；
6. 用 Moran's $I$ 和分层置换检验筛选具有空间结构的脂质；
7. 对相邻时间点 territory 的共享脂质均值计算平方欧氏距离，用 Hungarian algorithm 建立发育 pseudolineage；
8. 用 bulk LC–MS/MS 的候选脂质和 0.01 Da 最近邻进行注释，再用 bulk–MSI 相关性过滤可疑注释。

本地 Supplementary Table 1 有 296 行注释记录，包含观测/理论 $m/z$、adduct、formula 和 LC–MS/MS 物种；Supplementary Table 2 有 1,145 行脂质定量，并提供 transition 和内标信息。这些表格支撑注释与生物学解释，但不是三大核心模块自动产生的结果。

### 8. 评估结果应该怎样理解

#### 8.1 峰调用

- 在一个准同量异位峰评估中，uMAIA 图像含聚合峰的比例为 2.3%，Mirion 为 42%；
- 相对次优方法，最多获得 55% 更多高质量图像；
- 模拟数据互信息：uMAIA 0.98，binning 0.80，$P=2.03\times10^{-16}$；
- 标准谱对齐后仍多获得 33% 高质量图像。

这表明频数直方图对峰特异质量漂移有价值，但性能仍依赖阈值、仪器分辨率和图像质量指标。

#### 8.2 跨切片匹配

uMAIA 在模拟、同位素共现和 MALDI matrix peak 上均减少缺失/歧义。相对最宽的固定 bin，跨所有 acquisition 的信号从约 1,000 增加到 1,200。论文报告超过 50 张切片、20,000 个分子可在 15 分钟内 featurize。

需要注意：该速度不包含所有原始数据读取、峰调用、Gurobi 安装和归一化时间。

#### 8.3 归一化

在 Allen Brain Atlas 模拟中：

- uMAIA 的 RMSE 平均改善 89%；
- ComBat 改善 23%；
- $z$ normalization 反而恶化 17%。

区域差异检验中，uMAIA 的 FPR/FNR 为 0.07/0.12，优于 ComBat 的 0.18/0.22 和 $z$ normalization 的 0.15/0.24。真实斑马鱼数据没有 ground truth，因此论文以相邻切片的 PCA/cluster 连贯性作为代理指标。

### 9. 论文得到的主要生物学结论

- 研究共获得 96 次 MSI acquisition；
- 在发育 atlas 中注释 176 种脂质；
- 具有显著空间模式的脂质数量从 8 hpf 的 26 种增加到 24 hpf 的 58、48 hpf 的 77、72 hpf 的 100；
- 72 hpf 数据中识别 142 种脂质，其中 122 种为膜脂；
- 脂质 territory 能描绘卵黄、神经系统、后脑、肌肉、脊索、脊髓、鳔和多个脑区；
- PC 物种按不饱和度逐渐形成前后轴分离；
- 长链、高不饱和 TG 出现在头部软骨/骨原基相关间充质区域，而非仅局限于卵黄；
- sphingomyelin 在鳔周围呈同心层样分布；
- `sptlc1` knockdown 导致鳔充气受损和 Oil Red O 染色降低，支持 sphingolipid 参与表面活性物质形成。

论文同时明确：当前数据不能区分脂质运输和原位合成；MSI 只捕获部分分子，碎裂和样本质量会影响丰度估计。

### 10. 代码可复现性与可信边界

#### 综合判断：**medium fidelity，3/5 可复现性**

正面条件：

- 论文作者仓库与 DOI 明确对应；
- 本地保留 commit `fc5e495c495cac6ab4d1d9e01208c7ca52c10e18`；
- 三大核心模块源码均存在；
- README 提供 Linux/macOS 安装和峰调用 CLI；
- `uMAIA_tutorial.ipynb` 提供匹配、Zarr、初始化、SVI、保存和 transform 的调用；
- 原始数据入口、补充图和补充表可获得。

主要障碍：

- 分子匹配依赖 Gurobi 安装和许可证；
- 当前 `requirements.txt`、旧 `analysis.yml` 和论文版本表不完全一致；
- 没有找到自动测试或 CI；
- 没有找到一个命令重建全部论文图的完整脚本；
- 匹配邻域、$\delta_c$ 默认先验和参考 CDF 参数与论文存在已验证差异；
- 本次分析未执行原始数据下载、Gurobi 求解、SVI 数值复现或 atlas 重建。

因此，代码足以帮助研究者理解并运行核心思想，但“运行当前公开仓库”不应直接等同于“逐公式、逐数值完全复现论文”。

### 11. 建议的阅读和复现顺序

1. 先看 `summary.md`，掌握论文问题、结果和复现评级；
2. 看本文件，形成完整输入—输出心智模型；
3. 看 `doc_method.md`，核对英文公式、变量和下游 atlas 细节；
4. 看 `doc_code.md` 的 Match Assessment，优先理解所有 `Partial` / `Not found`；
5. 看 `figure_analysis.md`，区分图像可见证据和正文解释；
6. 运行前阅读 `uMAIA/README.md` 与 `uMAIA/uMAIA_tutorial.ipynb`；
7. 首次复现建议从少量 acquisition 开始，显式记录峰调用参数、Gurobi 版本、`NUM_SKIP`、`delta_v_dist`、mask、平滑、log epsilon 和 subsampling 索引。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## uMAIA — Unified Mass Imaging Analyzer

### Problem

Mass spectrometry imaging (MSI) can map metabolites and lipids at micrometer resolution, but a single acquisition is only a two-dimensional section. Building organism-scale 3D or developmental 4D atlases requires integrating tens of acquisitions whose spectra differ because of mass shifts, missing detections, corrupted images and nonbiological intensity distortions. Standard fixed-bin or alignment-based workflows become ambiguous at this scale, while batch-correction tools developed for transcriptomics do not match the bimodal, spatially structured intensity distributions of MSI.

The paper introduces uMAIA, a Python framework for joint analysis of large MSI collections, and uses it to construct a 4D lipid atlas of zebrafish development at 8, 24, 48 and 72 hours post-fertilization (hpf).

### Limitations of Existing Approaches

- **Fixed/static peak bins** do not adapt to molecule-specific mass-shift envelopes and can merge quasi-isobaric ions. Mirion (*Journal of the American Society for Mass Spectrometry*, 2013) is the main non-adaptive comparator.
- **Intensity-adaptive peak bins** can favor high-intensity signals even when lower-intensity ions carry useful spatial information. MALDIquant (*Bioinformatics*, 2012) is the adaptive comparator.
- **Cross-sample binning/alignment** faces a precision–recall trade-off: narrow bins miss matches, while wide bins create multiple same-section detections in one feature.
- **Generic batch correction** assumes distributions unlike MSI. The paper compares against ComBat (*Biostatistics*, 2006), $z$ normalization and scArches (*Nature Biotechnology*, 2021), a deep transfer-learning integration method that recombines features.

### Method

uMAIA has three explicit computational modules:

```text
raw .IBD/.imzML spectra
  → (1) adaptive peak calling
      detection-frequency histogram across pixels
      + watershed-like seed/interval expansion
      → ranges.csv + per-ion images.h5ad
  → (2) network-flow feature matching
      candidate cross-acquisition edges within m/z tolerance
      + binary minimum-cost flow over acquisition permutations
      → unified molecule_ID feature space + matched Zarr stack
  → (3) probabilistic normalization
      hierarchical foreground/background Gaussian mixture
      + acquisition × molecule batch factor
      + MAP fitting and CDF-to-inverse-CDF transformation
      → normalized cross-section image stack
```

Peak calling uses how often an $m/z$ is detected across pixels, not its intensity, to define peak-specific intervals. Matching casts candidate links as a constrained flow problem so each feature contains at most one peak from an acquisition. Normalization models logged pixel intensities as background and foreground modes; the foreground shift contains acquisition-specific $\gamma_a$ and molecule-specific $\lambda_c$ factors, and observed quantiles are mapped to a reference mixture distribution.

The normalized sections are registered into 3D volumes. Features detected in at least 15% of pixels in 80% of sections are retained, and PCA, $k$-means, Moran's $I$, nonnegative matrix factorization and diffusion maps are used to identify lipid territories and developmental relationships.

### Evaluation

#### Peak calling

Across real datasets and simulations, uMAIA better separated nearby peaks and recovered more high-quality images than Mirion, MALDIquant and static binning. The paper reports:

- 2.3% versus 42% of images containing aggregated peaks for uMAIA versus Mirion in one assessment;
- up to 55% more high-quality images than the runner-up, depending on MSI technology;
- simulated mutual information 0.98 for uMAIA versus 0.80 for binning ($P=2.03\times10^{-16}$);
- 33% more high-quality images after standard spectral alignment, with runtime in the same order of magnitude.

#### Feature matching

Matching was tested on simulations, isotopolog co-occurrence and MALDI matrix peaks. uMAIA produced fewer missing/ambiguous features than fixed bins and increased signals represented across all acquisitions from about 1,000 to 1,200 relative to the widest tested bin. The paper reports that more than 50 sections and 20,000 molecules can be featurized in under 15 minutes.

#### Normalization

The empirical batch-effect matrix was low rank, with about 31% of variability explained by its rank-one approximation. On Allen Brain Atlas-based simulations, uMAIA improved RMSE by a mean 89%, compared with 23% for ComBat and a 17% decline for $z$ normalization. Regional tests produced FPR/FNR of 0.07/0.12, compared with 0.18/0.22 for ComBat and 0.15/0.24 for $z$ normalization. In real zebrafish data, uMAIA yielded the most cross-section-consistent pixel clusters among the shown methods.

### Atlas Findings

The study generated 96 MSI acquisitions and annotated 176 lipids across the developmental atlas. The number of spatially patterned lipids rose from 26 at 8 hpf to 58 at 24 hpf, 77 at 48 hpf and 100 at 72 hpf. Lipid-defined territories became progressively more structured and aligned with anatomy.

At 72 hpf, 142 lipids were identified in the MSI dataset, including 122 membrane lipids. Unsupervised lipid components and clusters delineated yolk, nervous system, hindbrain, musculature, notochord, spinal cord, swim bladder and brain subdivisions. Important biological observations included:

- phosphatidylcholine species separating along the anterior–posterior axis by unsaturation degree;
- long-chain, highly unsaturated triglycerides localizing to craniofacial mesenchymal/bone-primordium regions rather than only the yolk;
- sphingomyelins accumulating in concentric swim-bladder regions;
- `sptlc1` knockdown impairing swim-bladder inflation and reducing Oil Red O staining, supporting a role for sphingolipids in surfactant production.

The atlas cannot distinguish lipid transport from local synthesis, and MSI captures only a fraction of molecular species; fragmentation and sample quality can alter abundance estimates.

### Code–Paper Match

Overall fidelity is **medium**. The retained paper-owned repository at commit `fc5e495c495cac6ab4d1d9e01208c7ca52c10e18` contains all three core modules plus an end-to-end tutorial for peak calling, matching, Zarr assembly, GMM initialization, 5,000-step SVI fitting and transformation.

The main verified discrepancies are:

- the paper states matching to $k=2$ consecutive acquisitions, while the checked wrapper uses `NUM_SKIP=ceil(NUM_S/2)`;
- the normalization argument named `delta_v_dist='gaussian'` selects a Gamma prior in the current branch, while `'gamma'` selects a Normal prior;
- the code's reference inverse-CDF transform uses equal mixture weights and parameters that are not the exact acquisition averages written in Eq. (7);
- no automated tests/CI or one-command exact regeneration of every paper figure was found.

### Reproducibility

**Rating: 3/5 (moderate).** Positive factors are open source code, an exact retained commit, pinned requirements, Linux/macOS installation guidance, raw-data portals, supplementary figures/tables and runnable tutorials with saved outputs. Barriers are the Gurobi installation and academic/commercial license, large external MSI datasets, divergent environment specifications, lack of tests, long SVI runtime (the tutorial records about 49 minutes on CPU for 5,000 steps) and formula-level differences between paper and code.

No end-to-end execution was performed for this analysis. Gurobi optimization, numerical normalization equivalence and atlas reconstruction therefore remain unverified at runtime.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
