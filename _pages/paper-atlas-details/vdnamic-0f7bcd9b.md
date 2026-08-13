---
layout: default
permalink: /paper-atlas/vdnamic-0f7bcd9b/
title: "vdnamic"
nav: false
wide: true
description: "体积 DNA 显微镜先用短程 RCA 边和长程 IVT 边把组织内部的空间关系写成一张千万节点 DNA 邻接图，再用 hierarchical GSE 从局部子图解出候选坐标、插值到全图、构造测地谱基底，最后在该基底中优化 UEI 似然，从而得到带有基因序列标签的三维分子图像。"
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
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>vdnamic</h1>
    <p>Spatial transcriptomic imaging of an intact organism using volumetric DNA microscopy</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-025-02613-z" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for vdnamic">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/wlab-bio/vdnamic" target="_blank" rel="noopener noreferrer" aria-label="Open code for vdnamic">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 体积 DNA 显微镜：从分子邻接网络到完整胚胎三维转录组图像

### 这篇论文解决什么问题？

论文要解决的是一个很特别的三维成像问题：不依赖显微镜预先定义的坐标、不预设目标基因探针，也不知道样本内部结构时，能否仅通过测序恢复完整生物体内数百万到千万级 RNA 分子的三维位置，并把转录本序列重新放回这些位置上？

传统方法各有边界：

- 顺序杂交式单细胞原位 RNA 检测（*Nature Methods*, 2014）和高通量多重 RNA 成像（*Science*, 2015）能提供空间信息，但需要预先选定目标序列，通量和可扩展性受光学采集限制。
- 完整组织三维原位测序（*Science*, 2018）能解析三维转录状态，但仍依赖专门的成像和读出流程。
- 阵列式空间转录组把外部空间条形码坐标赋给样本，通常需要在空间分辨率、测序深度和信号密度之间取舍。
- 第一代 DNA microscopy（*Cell*, 2019）已经证明可以把空间关系编码进 DNA 并通过测序重建二维图像，但其原位 PCR 需要热循环，主要使用较宽的单一扩散尺度，而且对包含空洞、弯曲和多尺度结构的千万节点三维网络，原有 sMLE 重建并不充分。

这项工作的核心贡献是“实验化学 + 计算推断”的协同设计：用两种长度尺度的分子扩散构造既局部精细又全局连通的邻接图，再用 geodesic spectral embedding（GSE，测地谱嵌入）从这张图中恢复三维坐标。

### 输入、输出和基本假设

#### 输入

1. 两类 UMI（type I、type II）节点。每个 UMI 标记一个原始 cDNA/转录本分子。
2. UMI 对之间的 UEI 数量 $n_{ij}$。一个 UEI 表示一次被测序记录下来的邻近相互作用。
3. 可选的 cDNA 插入序列及其 UMI，用于后续基因组比对和基因标注。

计算上，数据是一张带权二部图：节点是 UMI，边权是 UEI count。写成对称矩阵：

$$
{\bf n}\equiv
\begin{pmatrix}
0 & {\bf n}_{m_{\bf I}\times m_{\bf II}}\\
{\bf n}_{m_{\bf II}\times m_{\bf I}} & 0
\end{pmatrix}.
$$

#### 输出

- 每个保留 UMI 的三维坐标 $\overrightarrow{x}_i\in\mathbb{R}^3$；
- 与这些坐标关联的 cDNA 序列、基因名、基因类型和突变信息；
- 最终得到一个“从样本内部编码并由测序解码”的三维空间遗传图像。

#### 基本假设

UMI $i$ 和 $j$ 越近，生成 UEI 的期望速率越高。论文用高斯型距离衰减描述这种关系，并把不同 UEI 事件近似视为相互独立的邻近测量。这个假设把空间重建转化成统计逆问题：寻找一组坐标，使其产生的期望边概率与观测 UEI count 尽量一致。

### 实验部分如何把空间写进 DNA？

#### 1. 给转录本加上唯一标签

固定、通透后的斑马鱼胚胎中，RNA 被逆转录成 cDNA；每个 cDNA 末端连接含 31 个随机核苷酸的 UMI。实验使用两类 UMI，避免后续同类分子自身配对。

#### 2. 锚定 RCA 编码短距离

环化 UMI 模板在原位进行 rolling-circle amplification（RCA）。聚合产物的一端仍锚定在原始转录本附近，形成约 1 μm 尺度的 DNA nanoball。相邻 nanoball 之间通过随机 UEI 序列连接，因此这部分边主要记录短距离邻接。

#### 3. 非锚定 IVT 编码长距离

随后在可逆 PEG 水凝胶中进行原位 IVT。RNA 复制产物可以在更大范围内扩散和重组，生成长距离 UEI。第一代 DNA microscopy 的非锚定扩散尺度约为几十微米。

#### 4. 为什么必须有两个尺度？

只有短距离边时，局部位置精确，但组织中 UMI 分布不均会造成图断裂；只有长距离边时，图容易保持整体连通，但单条边的空间不确定性更大。短边提供局部几何，长边负责跨越组织空洞，两者共同支撑完整胚胎的全局重建。

一个重要限制是：RCA-UEI 和 IVT-UEI 测序后不可区分。算法接收的是混合后的统一边图，不能逐条判断某个 UEI 来自哪种化学过程。

### 从 FASTQ 到可推断的 UEI 图

```text
FASTQ
  │
  ├─ 按读段结构拆出 type-I UMI、type-II UMI、UEI、cDNA insert
  ├─ 质量过滤
  ├─ 各序列类别按 1-bp 差异聚类
  ├─ 每个 UEI 通过 plurality 确定最可能的 UMI 对
  ├─ 删除并列歧义 UEI
  ├─ 迭代删除低支持 UMI 和低支持 UMI–UMI association
  └─ 保留最大连通分量 → link_assoc → GSE
```

论文要求体积数据中每个 UMI 至少有两个 UEI，每个 UMI–UMI association 至少由两个 UEI 支持。

代码与论文高度一致：

- `hashAlignments.py:6-234` 对每个字符位置做一次删除哈希，将相差 1 bp 的序列放入等价组，再根据 read-neighborhood abundance 迭代传播聚类标签。
- `dnamicOps.py:557-618` 对每个 UEI 的候选 UMI 对按 read count 排序，保留 plurality pairing；最高票并列时排除。
- `dnamicOps.py:620-790` 对 association 和两侧 UMI 交替迭代过滤，直到稳定。
- `dnamicOps.py:793-902` 找出图的连通分量；推断在保留的主要连通子图上运行。

### 为什么普通谱方法不够？

先对 UEI count 矩阵做行归一化：

$$
{\bf N}=\operatorname{diag}(n_{i\cdot})^{-1}{\bf n}.
$$

设观测边概率 $p_{ij}=n_{ij}/n_{\cdot\cdot}$，给定坐标后的模型概率为

$$
q_{ij}(\overrightarrow{x})=
\frac{e^{-\lVert\overrightarrow{x}_i-\overrightarrow{x}_j\rVert^2}}
{\sum_{ij}e^{-\lVert\overrightarrow{x}_i-\overrightarrow{x}_j\rVert^2}}.
$$

目标是最小化

$$
D_{\rm KL}(p\parallel q)=\sum_{ij}p_{ij}\log\frac{p_{ij}}{q_{ij}(\overrightarrow{x})}.
$$

其二次部分可写成

$$
\sum_{ij}n_{ij}\lVert\overrightarrow{x}_i-\overrightarrow{x}_j\rVert^2,
$$

求导后得到近似条件 ${\bf N}\overrightarrow{x}\approx\overrightarrow{x}$。因此，${\bf N}$ 中特征值接近 1 的特征向量可以作为平滑坐标函数。

sMLE 的做法是：只允许坐标位于前 $E$ 个特征向量张成的线性子空间中，再在这个子空间内做投影梯度优化。这样能抑制噪声，但相当于用一组全局线性模式描述组织。对于弯曲胚胎、空洞、细长结构和多尺度形态，全局线性组合会逐渐失真。

GSE 的关键不是更换最终统计目标，而是先改造用于优化的谱基底，使它更接近真实非线性流形的坐标。

### GSE 的核心步骤

#### 步骤 1：重标度初始特征空间

若 ${\bf N}$ 的第 $i$ 个方向对应特征值 $\lambda_i$，其在二次目标中的贡献与 $1-\lambda_i$ 有关。论文把方向按

$$
\overrightarrow{z}_i^{\rm rescaled}
=\frac&#123;&#123;\bf U}\overrightarrow{v}_i}{\sqrt{1-\lambda_i}} \tag{2}
$$

缩放，使不同方向对目标的平均贡献尽量均匀。代码在 `optimOps.py:496-534` 实现了相同的 $(1-\lambda)^{-1/2}$ 缩放，并用 $10^{-10}$ 下界避免数值发散。

#### 步骤 2：在重标度空间中寻找邻居

对每个 UMI，在 $E$ 维空间 ${\bf Z}$ 中寻找 $k=2E$ 个近邻。选择 $2E$ 是为了让邻域通常能够覆盖所有谱维度。

代码在 `optimOps.py:1244-1266` 中执行近邻搜索并缓存 `nbr_indices.npy` 与 `nbr_distances.npy`。

#### 步骤 3：估计局部切空间

对每个点的邻域差分矩阵做 SVD，取前 $d$ 个方向作为局部切空间 ${\bf U}_i$。为减轻邻域密度不均的影响，每个邻居按其在其他邻居表中出现次数的倒数加权。

#### 步骤 4：用切空间修正距离

令 $\overrightarrow{z}_{ij}=\overrightarrow{z}_j-\overrightarrow{z}_i$，GSE 定义

$$
g_{ij}=(1-\beta_{ij})
\left(\lVert{\bf U}_i^T\overrightarrow{z}_{ij}\rVert+
\lVert{\bf U}_j^T\overrightarrow{z}_{ij}\rVert\right)
+\beta_{ij}\lVert\overrightarrow{z}_{ij}\rVert.
$$

$\beta_{ij}$ 是两个切空间相似度矩阵 ${\bf U}_i^T{\bf U}_j$ 的奇异值几何平均。两个切空间一致时，更接近欧氏距离；切空间转向明显时，投影距离权重增加。

`optimOps.py:1080-1155` 直接实现了这个公式。代码还加入多级 SVD 失败回退，这是论文未展开的工程稳健性细节。

#### 步骤 5：构造稀疏测地核

以点 $i$ 的邻居距离中位数作为局部尺度 $\sigma_i$：

$$
W_{ij}\leftarrow
\frac{(\sigma_i^2+\sigma_j^2)^{-d/2}
e^{-g_{ij}^2/(\sigma_i^2+\sigma_j^2)}}{\text{row norm}}.
$$

只有近邻位置是非零，因此这是稀疏核。随后定义

$$
{\bf W}_{\rm GSE}=\widetilde{\bf W}{\bf N}. \tag{3}
$$

对它的归一化对称形式求前几个特征向量，得到比原始 ${\bf N}$ 特征向量更能反映全局曲率的候选坐标基底。

代码对应 `optimOps.py:1801-1844,1902-1932`，其中指数计算使用行内减最小值的稳定化技巧，再做行归一化。

#### 步骤 6：在 GSE 基底中优化完整似然

GSE 最后仍然优化 UEI 的 multinomial likelihood，它与上面的 KL divergence 最小化等价。直接计算所有 $m^2$ 分子对不可能，因此每次迭代为每个点采样三组配对：

1. 当前坐标中的最近邻；
2. 从最近的 $1/2^d$ 分位区域随机抽样；
3. 从其余远距离点中随机抽样。

每组乘以其代表的总体比例：

$$
f_{\bf I}=\frac{k}{m},\qquad
f_{\bf II}=\frac{1}{2^d}-\frac{k}{m},\qquad
f_{\bf III}=1-\frac{1}{2^d}.
$$

`optimOps.py:1707-1770` 实现了这三组采样与权重。`spec_GSEobj` 从 $d$ 个特征向量开始，每次增加一个谱分量，并用 `trust-krylov` 优化器更新线性系数（`optimOps.py:663-721`）。

### Hierarchical GSE 为什么能扩展到千万节点？

完整 GSE 仍需要在全局初始谱空间中搜索近邻。若初始空间本身因稀疏和非线性而失真，近邻就不可靠。Hierarchical GSE 先在许多较小、连通性较好的子图上获得粗坐标，再把这些子解扩展到全图。

```text
全局 UEI 图
  │
  ├─ 交替选择均匀覆盖子图和局部目标子图
  ├─ 每个子图保留最大连通分量
  ├─ 对每个子图运行完整 GSE
  ├─ 用 UEI 图上的正则化共轭梯度把子图坐标插值到其余节点
  ├─ 多个子解随机旋转、rank transform、拼接、SVD
  └─ 构成全局候选基底 → 再运行完整 GSE
```

插值从

$$
({\bf N}-{\bf I})\overrightarrow{x}\to 0 \tag{7}
$$

出发。已知子集记为 ${\bf S}$，未知部分记为 $\bar{\bf S}$，求解

$$
({\bf M}_{\bar{\bf S}\times\bar{\bf S}}+\lambda{\bf I})
\overrightarrow{x}_{\bar{\bf S}}
=
{\bf M}_{\bar{\bf S}\times{\bf S}}\overrightarrow{x}_{\bf S}.
$$

正则项 $\lambda=\sigma^2|\bar{\bf S}|$ 防止图连接不足时解不稳定。代码使用最多 1,000 次、容差 $10^{-3}$ 的共轭梯度，并可对局部目标子图的插值结果做 empirical quantile transform（`optimOps.py:1157-1216`）。

论文在模拟数据中使用 25 个子图，在真实数据中使用 50 个子图。仓库示例命令确实给出三维、$E=25$、最终基底 250、50 个子图和每个子图 25,000 个点，但没有冻结到每个斑马鱼样本的运行清单，因此属于 **Partial** 复现证据。

### 0.2% 过离散节点过滤

论文对三维数据分两轮过滤，每轮删除 UEI 邻域 RMS dispersion 最大的 0.1% UMI，总计 0.2%。每轮在三维下使用六个子图。

仓库的 `gse_fulldata.sh` 使用 `-filter_criterion 0.1,0.1`；`run_GSE` 在过滤层把子图数设为 `2*inference_dim`，三维即 6；`filter_data` 按 percentile 删除高 dispersion 节点。代码还会继续删除少于两个 link count 的节点并只保留最大连通分量，这一额外清理没有在论文过滤段落中单独说明。

### 基因序列如何放回三维坐标？

对属于同一 cDNA UMI 的 reads，代码逐碱基多数投票得到 consensus，按终止/接头序列截断，并过滤过短插入。若提供 STAR index 和 GTF：

1. 用 STAR 比对 consensus insert；
2. 按 alignment score 和 match percentage 保留高质量结果；
3. 把 alignment 与 GTF feature 合并；
4. 记录 mismatch/mutation 字符串；
5. 优先标记 rRNA/Mt_rRNA；
6. 允许一个 UMI 碱基错配，把 cDNA library 的标注匹配回 UEI library 的 UMI cluster。

主要代码在 `dnamicOps.py:95-345,382-440,493-542`。

**Not found：** 本地仓库没有论文使用的 GRCz11 STAR index、Ensembl release 109 GTF，也没有找到将 rRNA 区域向两侧各扩展 1 kb 的冻结预处理命令。

### 评估结果如何理解？

#### 模拟数据

- 2D：$10^4$ 个 UMI、$10^5$ 个 UEI；
- 3D：$5\times10^4$ 个 UMI、$2.5\times10^6$ 个 UEI；
- UEI count 用 negative binomial 分布生成，$p=0.8$；
- 比较 sMLE、GSE、hierarchical GSE 和 UMAP。

图 4 显示 GSE 比 sMLE 更好地恢复数字和三维雕像的局部/全局几何，UMAP 虽能保留部分邻域，但会改变整体拓扑。decoherence curve 在不同邻域尺度上做刚性配准后计算 RMSD；它衡量的是局部配准误差，而不是未经配准的绝对坐标误差。

#### 完整斑马鱼胚胎

四个 24 hpf 样本分别重建了 7.7、7.2、12.0 和 12.6 million UMI。三维点云重复出现头部高密度区和弯曲尾部，说明推断捕获了 gross morphology。

UMI 的 UEI count 中位数为 5–6；结合约 1 μm 的短扩散尺度，论文估计 conditionalized median 3D resolution 约为 1.5 μm。这里“conditionalized”很重要：单个 UMI 的位置精度依赖其邻居的位置和图连通性。图中仍可见明显空洞，所以不能把这个数直接理解为全胚胎均匀的单细胞分辨率。

#### 与 Stereo-seq 的基因表达比较

论文从 Stereo-seq（*Developmental Cell*, 2022）中构造五组沿前后轴极化的 type-A/type-B 基因集合，再对 DNA microscopy UMI 做相同的局部平滑。图 6 显示两种技术都产生大尺度红/蓝极化模式。

**Not found：** 公开代码中没有找到 Stereo-seq 数据处理、随机参考点、type-A/type-B 排名或十近邻平滑脚本。因此这是论文图像支持的生物学验证，但不能由当前代码快照独立重现。

### 代码与论文的一致性结论

总体一致性为 **high**：核心算法不是只有接口或伪代码，而是从一碱基聚类、UEI plurality、图过滤，到 GSE 核、hierarchical interpolation、采样似然优化和两轮 0.1% 过滤都有直接源码对应。

需要保留的边界：

- 核心算法：**Exact** 为主；
- cDNA reference 资产、完整 Fig. 4 sweep、真实样本运行参数：**Partial**；
- Fig. 6 Stereo-seq 比较、完整出版级制图流程、每个样本的冻结中间结果：**Not found**；
- 仓库包含模拟测试和 CLI 文档，但本分析没有实际执行流水线，因此文中所有运行效果仍以论文结果为准。

### 一句话抓住方法

体积 DNA 显微镜先用短程 RCA 边和长程 IVT 边把组织内部的空间关系写成一张千万节点 DNA 邻接图，再用 hierarchical GSE 从局部子图解出候选坐标、插值到全图、构造测地谱基底，最后在该基底中优化 UEI 似然，从而得到带有基因序列标签的三维分子图像。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spatial transcriptomic imaging of an intact organism using volumetric DNA microscopy

### Problem

The paper asks whether a whole, intact organism can be imaged in three dimensions while retaining transcript sequences, without a microscope-defined coordinate grid, targeted probe panel, or prior knowledge of spatial organization. Conventional in situ RNA imaging—including sequential hybridization (*Nature Methods*, 2014), highly multiplexed single-cell RNA imaging (*Science*, 2015), and intact-tissue sequencing (*Science*, 2018)—either requires predefined targets or specialized optical workflows. Array-based spatial transcriptomics imposes external coordinates and trades among spatial resolution, molecular depth, and signal density. The original DNA microscopy method (*Cell*, 2019) avoided optics and prior templates, but used high-temperature in situ PCR, encoded mainly one broad diffusion scale, and had not addressed nonlinear reconstruction of approximately $10^7$ molecules in intact 3D tissue.

### Proposed technology

Volumetric DNA microscopy combines a multiscale chemical proximity-recording system with geodesic spectral embedding (GSE):

1. RNA is reverse-transcribed and each cDNA is tagged with a random UMI.
2. Anchored rolling-circle amplification creates roughly 1-μm UMI nanoballs; adjacent products generate short-range UEIs.
3. Unanchored IVT in a reversible PEG hydrogel generates longer-range UEIs that bridge the specimen.
4. Sequencing yields cDNA–UMI reads and UMI–UEI–UMI associations.
5. One-base clustering, plurality consensus, support filtering, and largest-component extraction produce a sparse weighted UMI graph.
6. GSE rescales leading UEI-matrix eigenvectors, estimates local tangent spaces, builds a sparse geodesic Gaussian kernel, and uses its eigenvectors as the basis for projected likelihood optimization.
7. Hierarchical GSE solves many smaller subgraphs, interpolates their coordinates to the full graph, and constructs a consensus spectral basis for million-node inference.
8. cDNA consensus sequences and gene annotations are matched back to the inferred UMI coordinates.

The key computational idea is that the final objective remains the UEI likelihood/KL-divergence objective used by earlier spectral maximum-likelihood inference, but the search basis is preconditioned to reflect nonlinear manifold geometry. Hierarchical inference makes that basis practical and more stable for large, undersampled graphs.

### Evaluation and main results

- **Controlled simulations:** 2D benchmarks used $10^4$ UMIs and $10^5$ UEIs; 3D benchmarks used $5\times10^4$ UMIs and $2.5\times10^6$ UEIs, with negative-binomial sampling ($p=0.8$). GSE visually and quantitatively preserved local/global geometry better than sMLE and UMAP. Hierarchical GSE corrected sparse-graph instabilities and recapitulated the expected inverse-square-root resolution scaling.
- **Prior 2D DNA microscopy:** hierarchical GSE reconstructed an earlier unanchored-diffusion dataset consistently with fluorescence ground truth.
- **Whole-organism scale:** four 24-hpf zebrafish datasets produced 3D embeddings of 7.7, 7.2, 12.0, and 12.6 million UMIs. The point clouds reproduced gross head–tail morphology across specimens.
- **Multiscale signal:** observed embedded edge distances fit a two-length-scale Maxwell–Boltzmann model better than a single scale; the short component corresponds to about 1 μm, consistent with RCA-polony size.
- **Resolution:** with median 5–6 UEIs per UMI, the paper estimates median conditionalized 3D UMI resolution near 1.5 μm. This is not uniform organism-wide single-cell resolution because the transcript-derived graph contains gaps.
- **Biological validation:** broad anterior–posterior gene-set enrichment patterns in reconstructed specimens qualitatively mirrored Stereo-seq (*Developmental Cell*, 2022) patterns.

### Limitations

- Short- and long-range UEIs are indistinguishable after sequencing, reducing the positional information carried by an individual edge.
- UMI density is nonuniform and does not space-fill the organism; large gaps prevent uniform single-cell segmentation.
- The four whole-organism reconstructions lack an external matched 3D coordinate ground truth. Gross morphology and gene-pattern agreement support plausibility, while simulation provides the controlled accuracy evidence.
- Gene-sequence capture remains incomplete, and the paper identifies chemistry optimization as necessary for cellular/subcellular resolution.
- Supplementary Markdown was unavailable locally, so supplementary robustness and chemistry details could not be independently incorporated beyond main-paper references.

### Reproducibility and code match

**Reproducibility rating: 4/5.** The public repository is a high-fidelity implementation of the core computational pipeline. Direct source reads verify one-base EASL-style clustering, plurality UEI assignment, iterative graph filtering, cDNA consensus and STAR/GTF annotation, the row-normalized UEI eigenspace, Eq. 2 rescaling, tangent-space geodesic smoothing, the sparse GSE kernel, hierarchical interpolation, sampled likelihood optimization, and the two-pass 0.1% + 0.1% dispersion filter. The repository includes environment specifications, documented CLI usage, example UEI/cDNA settings, simulators, and a five-minute end-to-end test harness.

4 sweep, and the Stereo-seq/Fig. 6 analysis are **Not found** in the snapshot. The code therefore supports understanding and rerunning vDNAmic/GSE on prepared inputs, but it is not a frozen capsule that regenerates every paper panel from one command.

### Bottom line

This work extends DNA microscopy from dense 2D specimens to intact-organism 3D spatial transcriptomic imaging by co-designing multiscale molecular proximity encoding and a scalable nonlinear spectral reconstruction algorithm. Its strongest demonstrated outcome is a sequence-derived, million-node 3D molecular map that recovers gross zebrafish morphology and broad gene-expression polarity without an optical coordinate template; uniform single-cell resolution remains future work.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
