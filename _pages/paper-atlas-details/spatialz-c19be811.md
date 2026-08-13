---
layout: default
permalink: /paper-atlas/spatialz-c19be811/
title: "SpatialZ"
nav: false
wide: true
description: "SpatialZ 不是真的“测量”了切片之间的组织，而是把相邻真实切片看成两个端点，分别对细胞位置分布、细胞类型组成、局部生态位和基因表达做受约束的插值，生成中间虚拟切片，再把真实与虚拟切片堆叠成高密度的“伪三维”细胞图谱。"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>SpatialZ</h1>
    <p>Bridging the dimensional gap from planar spatial transcriptomics to 3D cell atlases</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02969-9" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SpatialZ">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/senlin-lin/SpatialZ" target="_blank" rel="noopener noreferrer" aria-label="Open code for SpatialZ">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpatialZ：从稀疏二维切片补出三维细胞图谱

### 一句话理解

SpatialZ 不是真的“测量”了切片之间的组织，而是把相邻真实切片看成两个端点，分别对细胞位置分布、细胞类型组成、局部生态位和基因表达做受约束的插值，生成中间虚拟切片，再把真实与虚拟切片堆叠成高密度的“伪三维”细胞图谱。

### 1. 它要解决什么问题？

空间转录组通常得到一组二维组织切片。PASTE/PAST0E 一类方法可以把不同切片配准到共同坐标系，Allen CCFv3 等参考框架也可以提供标准三维坐标，但配准后的结果仍然只是“稀疏二维切片堆栈”：相邻切片可能相隔约 100 µm，中间没有细胞、表达或空间域信息。

实验性三维空间组学又受到组织厚度、成本、通量和实验复杂度限制。同一个组织也通常无法同时沿冠状面、矢状面和水平面完整切片并测量。因此，论文的核心问题是：

> 能否只用稀疏测得的二维切片，生成合理的中间切片，从而形成可用于三维分析的密集单细胞图谱？

SpatialZ 的答案是可以，但生成结果必须称为 **pseudo-3D atlas（伪三维图谱）**，因为中间切片是推断结果，不是直接实验观测。

### 2. 输入和输出

对第 $k$ 个真实切片，输入包括：

- 表达矩阵 ${\bf X}^{k}\in\mathbb{R}^{N_k\times M}$；
- 已配准二维坐标 ${\bf S}^{k}\in\mathbb{R}^{N_k\times2}$；
- 细胞类型 ${\bf C}^{k}$；
- 可选的空间域、脑区等标签。

输出的每个虚拟切片包含：

- 新生成的细胞坐标；
- 每个细胞的类型；
- 可选的转移标签；
- 合成的表达向量。

多个真实切片和虚拟切片按 $z$ 轴排列后，就得到密集伪三维图谱。

### 3. 整体流程

```text
稀疏真实切片
  表达 + 二维坐标 + 细胞类型 + 可选标签
                    │
                    ▼
        ① 切片配准到共同坐标系
                    │
                    ▼
        ② 生成虚拟细胞的位置
           初始化两端坐标样本
           优化切片 Wasserstein 重心
                    │
                    ▼
        ③ 分配细胞类型和其他标签
           距离加权 kNN 投票
           最近同类型真实细胞标签转移
                    │
                    ▼
        ④ 合成基因表达
           MENDER 编码多尺度细胞生态位
           同类型候选细胞
           按生态位相似度逐基因采样
                    │
                    ▼
真实切片 + 虚拟切片 → 密集伪三维图谱
                    │
     任意角度切片 / 三维渲染 / 三维样本搜索
```

### 4. 第一步：先对齐真实切片

SpatialZ 的核心函数不负责从头学习切片配准。论文对已有标准坐标的 BICCN MERFISH 数据直接使用 Allen Mouse Brain CCFv3；没有标准坐标的数据则使用 PASTE/PAST0E 做相邻切片配准。

这一步是一个重要前提：后面的 Wasserstein 插值直接比较坐标分布。如果配准错误，SpatialZ 仍可能生成平滑的中间形状，但“平滑”并不等于“解剖正确”。

### 5. 第二步：生成虚拟细胞的位置

#### 5.1 先决定虚拟切片有多少细胞

相邻两张真实切片分别有 $N_k$ 和 $N_{k+1}$ 个细胞。虚拟切片的估计细胞数为

$$
N_{\rm estimate}=\left\lfloor
(\alpha N_k+(1-\alpha)N_{k+1})\rho_{\rm mag}
\right\rfloor.
$$

$\alpha\in[0,1]$ 表示虚拟切片更靠近哪一端，$\rho_{\rm mag}$ 控制平面内细胞密度。代码也允许直接指定 `n_cell`。

实现中会按 $\alpha$ 从两端切片各取一部分坐标，拼成初始虚拟点云。注意它不是建立真实细胞之间的一一对应，而只是初始化一个分布。

#### 5.2 用切片 Wasserstein 距离优化点云

SpatialZ 最小化虚拟点云到两端真实点云的加权距离：

$$
{\rm L}({\bf S}_{\rm vir})=
\alpha\,{\rm SWD}({\bf S}_{\rm vir},{\bf S}_{k+1})+
(1-\alpha)\,{\rm SWD}({\bf S}_{\rm vir},{\bf S}_{k}).
$$

SWD（sliced Wasserstein distance）的直观含义是：随机选很多方向，把二维点投影成一维分布，在一维上计算 Wasserstein 距离，再综合这些方向。代码默认使用 80 个随机投影和 3,000 次梯度更新。

因此，这一步得到的是两个空间分布之间的 Wasserstein 重心。它回答的是“中间切片的细胞整体应该分布在哪里”，而不是“某个上层细胞在下层变成了哪个细胞”。

### 6. 第三步：分配细胞类型和标签

对于虚拟细胞 $i$，SpatialZ 分别在上下两个真实切片寻找邻居，用欧氏距离计算权重：

$$
\varphi_{ij}=\frac{1}{d_{ij}+\epsilon}.
$$

然后对候选细胞类型做加权投票：

$$
c_i=\arg\max_c
\sum_{j\in I_1[i]\cup I_2[i]}
\varphi_{ij}\delta(c,C[j]).
$$

代码默认在每个真实切片各取一个最近邻，$\epsilon=0.1$。选出细胞类型后，如果用户要求转移脑区、空间域等标签，代码会找到最近的同类型真实细胞并复制标签。

这里的关键假设不是“单个细胞类型沿 $z$ 轴连续”，而是“局部细胞生态位的组成沿 $z$ 轴连续”。

### 7. 第四步：合成基因表达

#### 7.1 用 MENDER 表示局部生态位

同一种细胞在不同邻域中的表达可能不同。因此 SpatialZ 不只看细胞类型，还使用 MENDER 统计多个空间尺度内各种细胞类型的数量，把它们拼成生态位向量 ${\bf E}_i$。

两个细胞的生态位相似度用余弦相似度计算：

$$
S(i,j)=\frac&#123;&#123;\bf E}_i\cdot{\bf E}_j}
{\lVert{\bf E}_i\rVert\lVert{\bf E}_j\rVert}.
$$

代码把两个真实切片和虚拟切片拼在一起运行 MENDER，固定使用 6 个尺度、半径模式和半径 15。

#### 7.2 按生态位相似度从真实细胞采样

对虚拟细胞 $i$，先找邻近且同类型的真实候选细胞，再用

$$
w_{ij}=\frac{\exp(\beta S(i,j))}
{\sum_{j\in N_i^{\rm ref}}\exp(\beta S(i,j))}
$$

得到采样概率。每个基因 $g$ 都独立抽一个参考细胞，并复制该细胞的真实表达值：

$$
{\bf X}_i[g]={\bf X}_{J_i[g]}[g],
\qquad
J_i[g]\sim{\rm Categorical}(\{w_{ij}\}).
$$

这种做法的优点是不会让神经网络凭空解码出任意数值；表达值来自真实参考细胞。但一个虚拟细胞的不同基因可能来自不同参考细胞，所以最终表达向量仍是计算合成的。

#### 7.3 代码中的重要偏差

论文公式最自然的理解是“直接找最近的 $k_{sam}$ 个同类型细胞”。代码实际先在全部细胞上做空间 kNN，再过滤细胞类型，因此可能留下少于 $k_{sam}$ 个候选，甚至没有候选。这是论文描述与实现之间最重要的部分匹配，而不是完全等价。

代码还提供 `fast` 模式：在十个最近邻里选择同类型细胞并平均表达；如果没有同类型邻居，就退化为全局最近的同类型细胞。该模式更快，但不是论文主推的生态位加权逐基因采样。

### 8. 如何生成完整三维图谱？

`Generate_multiple_spatialz` 在一对真实切片之间遍历多个 $\alpha$，生成多张中间切片；`Generate_multiple_slices` 再遍历整个有序切片列表，对每一对相邻切片重复这一过程，并保存 `.h5ad`。

论文在大规模鼠脑 MERFISH 图谱中，对 129 对连续真实切片各插入 9 张虚拟切片，最终得到 1,281 张切片、超过 3,800 万个细胞和 1,100 多个基因。论文报告总计算时间约 801 小时，说明方法结构虽然简单，大规模运行仍然昂贵。

### 9. 任意角度的计算切片

有了三维坐标后，SpatialZ 先把所有细胞坐标移到几何中心，再组合 $x$、$y$、$z$ 三个轴的旋转矩阵：

$$
R_{3\rm D}=R_z(\theta_z)R_y(\theta_y)R_x(\theta_x),
\qquad
{\bf S}_{\rm rotated}={\bf S}_{\rm centered}R^T.
$$

旋转后，在新的 $z$ 轴上选择平面位置

$$
z_{\rm slice}=\frac{z_{\min}+z_{\max}}{2}+a_{\rm offset},
$$

并保留满足

$$
|z_&#123;&#123;\rm rotated},i}-z_{\rm slice}|\le d/2
$$

的细胞。这样可以得到矢状面、水平面或任意斜切面。

代码 `synthesize_view` 与这些公式基本一致，但有一个隐藏行为：它返回的是选中切片细胞的固定 13% 子样本，并且总会触发绘图；这不是数学定义的一部分。论文的式 23 和式 24 还把两个投影坐标都写成了 $y_{\rm section,i}$，而代码明确使用 `x_slice` 和 `y_slice`，所以第一项很可能是排版错误。

### 10. 论文如何验证它？

#### 10.1 最关键：真实三维数据的留出验证

作者使用 STARmap 真实三维视觉皮层数据，把组织切成 7 个连续平面，故意删掉第 2、4、6 层，再由 SpatialZ 重建。被删掉的真实切片就是直接的 ground truth。

Fig. 2 中：

- 虚拟切片和真实切片在 UMAP、空间 marker pattern 和八种表达/细胞统计量上相近；
- real-versus-virtual 的 Moran’s $I$ 和 Geary’s $C$ 相关性约为 $R=0.95$–$0.98$；
- 稀疏切片堆栈与完整三维数据的相关性约为 $R=0.98$，加入虚拟切片后的 dense volume 约为 $R=0.99$。

补充材料还设置了两个简单基线：随机生成坐标后做邻居表达平均，以及直接使用相邻切片坐标后做邻居表达平均。SpatialZ 在八项统计量和结构相似性评估中优于这两个基线。

#### 10.2 其他验证

- MERFISH 下丘脑：虚拟切片保持细胞类型、脑区和 marker pattern，并提高 STAGATE/BINARY 的 ARI、NMI。
- 大规模 BICCN 鼠脑：验证 3D 图谱的规模化应用。
- Allen Brain Atlas 对照：比较合成矢状/水平/斜切面中的基因空间模式。
- CAST 三维搜索：先在 150 个多角度切片中做仿射粗搜索，再用 B-spline 精定位。
- 人乳腺癌 IMC：显示框架可扩展到蛋白空间数据，而不仅是转录组。

### 11. 代码复现性

核心插值代码与论文高度一致：位置、细胞类型、生态位和表达合成都能在 `SpatialZ.py` 中找到明确实现，任意角度切片在 `Synthesize.py` 中实现。官方仓库还提供两个 notebook、Dockerfile 和依赖版本。

但它不是“一键复现全部论文”的软件包：

- 没有找到自动化测试；
- 主要示例是大型 notebook；
- 依赖版本较旧，安装说明绑定 CUDA 11.7/PyTorch 1.13；
- 连续三维网格构建和 CAST 三维搜索的可复用库函数 **Not found**；
- 完整数据在 Figshare、Dryad、CELLxGENE、Zenodo 等外部来源；
- 3,800 万细胞图谱需要大量计算资源。

综合复现性可评为 **3.5/5**：核心算法透明、代码匹配度高，但完整应用链条和大规模结果复现门槛较高。

### 12. 怎样正确理解 SpatialZ 的结论？

SpatialZ 最适合回答的是：

> 如果相邻真实切片之间的组织变化相对连续，那么怎样生成一个同时满足空间分布、细胞类型、生态位和表达约束的合理中间状态？

它不保证找回从未在两端出现的突发结构，也不能把虚拟细胞当作真实观测。其科学价值在于把稀疏平面数据变成可供三维探索、任意角度切片和空间搜索使用的计算参考图谱，同时通过真实三维留出实验说明这种插值在连续组织中具有较高保真度。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpatialZ — Summary

### Problem

Spatial transcriptomics usually produces isolated 2D tissue sections. Registration tools can stack these planes, but large unmeasured gaps remain along the $z$ axis, so the result is still a sparse stack rather than a dense 3D cell atlas. Experimental 3D ST remains limited in thickness, cost, and throughput, while measuring the same specimen in multiple anatomical planes is generally impossible.

### Contribution

SpatialZ is a computational framework for converting registered, sparsely sampled 2D spatial-omics sections into a dense **pseudo-3D** atlas by inserting virtual slices. It is designed for single-cell data and uses cell type and local niche context rather than relying on a specific gene panel. The reconstructed atlas supports arbitrary-plane in silico sectioning, 3D gene/domain visualization, and query-section localization.

The method has four core steps:

1. Align adjacent measured sections using an existing registration method or reference coordinate system.
2. Generate virtual-cell coordinates by optimizing an $\alpha$-weighted sliced-Wasserstein barycenter between adjacent spatial point clouds.
3. Assign cell types by distance-weighted nearest-neighbor voting and optionally transfer labels such as spatial domains.
4. Synthesize expression by matching same-type cells and sampling observed gene values according to MENDER-derived niche similarity.

This niche-conditioned sampling is the main modeling idea. It avoids directly decoding arbitrary expression profiles, but it still produces inferred transitional states rather than new measurements.

### Evaluation

The strongest test uses a real 3D STARmap mouse visual-cortex dataset. The authors divide the volume into seven sections, withhold sections 2, 4, and 6, and reconstruct them from the remaining planes. Virtual and real sections show similar gene/cell summary statistics and spatial marker patterns; real-versus-virtual Moran’s $I$ and Geary’s $C$ correlations are roughly $R=0.95$–$0.98$. Relative to a sparse stack, the reconstructed dense volume is closer to the complete real volume, reaching approximately $R=0.99$ for both spatial-autocorrelation measures in Fig. 2.

Supplementary benchmarking compares SpatialZ with two simple interpolation baselines: random positions plus nearest-neighbor expression averaging, and adjacent-section positions plus the same averaging. SpatialZ performs better across eight summary statistics and structural-similarity analyses.

Further applications include:

- MERFISH mouse hypothalamus, where virtual slices preserve cell types, regions, and improve STAGATE/BINARY ARI and NMI;
- a BICCN MERFISH mouse-brain atlas expanded to 1,281 slices, more than 38 million cells, and over 1,100 genes by inserting nine slices between 129 consecutive real pairs;
- sagittal, horizontal, and oblique in silico sections, with marker patterns compared against Allen Brain Atlas ISH images;
- CAST-based 3D localization of query tissue sections;
- human breast-cancer imaging mass cytometry, demonstrating extension beyond transcriptomics.

### Strengths

- The held-out real-3D experiment provides direct ground truth for missing-section reconstruction.
- The method is transparent: coordinate, label, niche, and expression steps are separately interpretable.
- It operates on cell-level `AnnData`-like inputs and supports limited gene panels.
- The core paper equations closely match the acquired `SpatialZ.py` implementation.
- Code, tutorials, supplementary information, source-data workbooks, processed data, and public input datasets are all identified.

### Limitations

- “Pseudo-3D” is literal: abrupt structures or cell states absent from both neighboring sections cannot be recovered reliably.
- Registration error propagates into interpolation.
- The main baseline comparison is against simple heuristics rather than a broad set of modern generative models.
- The default code queries global spatial neighbors before filtering by cell type, which is only a partial implementation of the paper’s same-type-kNN description.
- `synthesize_view` returns a hard-coded 13% subsample and always performs plotting, behavior not stated in the method equations.
- Automated tests are **Not found**; major workflows live in notebooks.
- Reusable code for continuous 3D mesh reconstruction and CAST-based search is **Not found** in the acquired two-module Python library.
- Full-scale reproduction is expensive: the reported mouse-brain construction required about 801 hours on an A100-equipped server.

### Reproducibility

**Rating: 3.5/5.** Core two-slice and serial interpolation code is concise, source-available, and has high paper–code fidelity. The official repository includes notebooks, a Dockerfile, pinned dependencies, and an archived commit snapshot. Reproduction is reduced by old GPU-specific environment pins, absent tests, external large datasets, substantial compute, and missing reusable modules for some headline downstream applications.

Code: `https://github.com/senlin-lin/SpatialZ` (acquired commit `e1b5ed01e933729149e08399febca08db16ced14`). Code archive: `https://doi.org/10.5281/zenodo.17416727`. Processed data: `https://doi.org/10.6084/m9.figshare.30418285`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
