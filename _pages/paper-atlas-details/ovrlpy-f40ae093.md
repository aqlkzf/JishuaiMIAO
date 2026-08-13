---
layout: default
permalink: /paper-atlas/ovrlpy-f40ae093/
title: "ovrlpy"
nav: false
description: "ovrlpy 不先问“每个转录本属于哪个细胞”，而是先把组织切片沿局部 z 中心虚拟地分成上、下两层，再比较同一平面位置两层的局部表达组成是否一致。两层越相似，垂直信号完整性（vertical signal integrity，VSI）越高；两层差异越大，越值得怀疑存在细胞垂直重叠、组织折叠、切片边界残缺或分割错误。"
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
      <span>Spatially Variable Genes</span>
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>ovrlpy</h1>
    <p>Identifying 3D signal overlaps in spatial transcriptomics data with ovrlpy</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/HiDiHlabs/ovrl.py" target="_blank" rel="noopener noreferrer" aria-label="Open code for ovrlpy">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ovrlpy 方法详解：用转录本的三维坐标发现垂直信号重叠

### 一句话理解

ovrlpy 不先问“每个转录本属于哪个细胞”，而是先把组织切片沿局部 $z$ 中心虚拟地分成上、下两层，再比较同一平面位置两层的局部表达组成是否一致。两层越相似，垂直信号完整性（vertical signal integrity，VSI）越高；两层差异越大，越值得怀疑存在细胞垂直重叠、组织折叠、切片边界残缺或分割错误。

这是一种无监督、无需细胞分割即可计算的质量控制方法，而不是直接修正 doublet 的去卷积模型，也不是“低 VSI 必然等于两个细胞重叠”的概率分类器。

### 1. 为什么需要这个方法？

成像型空间转录组平台可以记录每个 RNA 分子的三维位置 $(x,y,z)$，但常见分析仍会：

1. 把 5–15 µm 厚的组织切片投影到二维平面；
2. 用二维细胞或细胞核边界分配转录本；
3. 把同一二维区域里的信号当成一个细胞或一个组织结构。

如果两个细胞在 $z$ 方向上下重叠，或组织发生折叠，二维投影就会把不同表达程序混在一起。这会影响细胞类型注释、聚类、空间共定位以及空间差异基因分析（`paper.md:21-27,70,76`）。

直接使用三维分割也不能完全解决问题。论文比较了 Baysor（*Nature Biotechnology*, 2022）和 Proseg（*Nature Methods*, 2025）：三维成像的轴向分辨率通常较低，部分细胞被切片边界截断，DAPI、细胞大小等先验也可能在折叠或残缺组织中失效。ovrlpy 因此提供一个独立于分割边界的表达一致性信号（`paper.md:67,269-287`）。

### 2. 输入、输出与核心假设

#### 输入

最基本的输入是转录本表：

$$
T=\{(g_i,x_i,y_i,z_i)\}_{i=1}^{n},
$$

其中：

- $n$：转录本总数；
- $g_i$：第 $i$ 个转录本的基因；
- $(x_i,y_i,z_i)$：它在组织中的三维坐标。

代码中的 `Ovrlp` 会把用户指定的基因列和坐标列统一重命名为 `gene, x, y, z`（`ovrl.py/ovrlpy/_ovrlp.py:114-159`）。Xenium、MERSCOPE、Atera 和 CosMx 均有对应读取函数（`ovrl.py/ovrlpy/io.py:21-290`）。

#### 输出

- 每个平面网格位置的局部垂直中心 `z_center`；
- 无分割的“伪细胞”表达矩阵及 PCA/UMAP 模型；
- 二维 VSI 图；
- VSI 局部极小值对应的候选重叠位置；
- 候选区域的上层、下层和侧视 RGB 转录本图；
- 可选的细胞分割像素—VSI 对应表，用于后续按细胞聚合。

#### 核心假设

如果一个局部组织结构在垂直方向上是表达一致的，那么虚拟上层和下层的局部表达向量应指向相似方向；如果上下层来自不同细胞类型或不同组织结构，两个向量的方向会分离，余弦相似度降低。

### 3. 整体计算流程

```text
输入：gene, x, y, z 转录本表
              |
              v
1. 在 x-y 平面分箱，估计并平滑局部 z 中心
              |
       +------+------+
       |             |
       v             v
   z > center     z < center
   虚拟上层         虚拟下层
       |             |
       +------+------+
              |
2. 用全部三维转录本建立表达基底
   总信号 KDE -> 局部极大值（伪细胞）
   -> 伪细胞×基因矩阵 C -> PCA/UMAP
              |
              v
3. 分别计算上层和下层的逐基因二维 KDE
   -> 投影到 PCA 成分空间
              |
              v
4. 对应位置计算余弦相似度 VSI
              |
       +------+------+
       |             |
       v             v
     VSI 图       VSI 局部极小值
                         |
                         v
                 候选重叠区域可视化
```

需要注意：论文开头的球形细胞几何模拟只是说明二维投影可能受到垂直污染，并不进入 ovrlpy 算法（`paper.md:24,47`）。

### 4. 第一步：自适应的虚拟上下分层

#### 4.1 为什么不能直接用一个全局 $z$ 阈值？

样本的测量 $z$ 值可能随平面位置漂移，例如切片倾斜、组织厚度不均或光学系统造成的形变。主图 1b 直接显示：全局均值切分会产生明显左右不均，而局部平滑中心得到的上、下层计数更平衡。

#### 4.2 局部中心和平滑

ovrlpy 通常以 1 µm 网格离散 $x$–$y$ 平面，在每个网格中计算转录本 $z$ 均值；也可以选中位数。论文的四邻域消息传递为：

$$
&#123;&#123;\rm{COM}}}_{i}^{(t+1)}=
\frac{1}{|N_i|}\sum_{j\in N_i}
\frac&#123;&#123;{\rm{COM}}}_{j}^{(t)}+&#123;&#123;\rm{COM}}}_{i}^{(t)}}{2}.
$$

默认迭代 20 次（`paper.md:85-100`）。代码的高层 `analyse()` 路径也固定传入 20 次（`ovrl.py/ovrlpy/_ovrlp.py:443-474`）。

代码最后保留原始 `z`，额外增加 `z_center`，并用严格不等式切分：

$$
T_{\text{top}}=\{i:z_i>z_{\text{center},i}\},\qquad
T_{\text{bottom}}=\{i:z_i<z_{\text{center},i}\}.
$$

因此恰好满足 `z == z_center` 的转录本不会进入任一层（`ovrl.py/ovrlpy/_utils.py:163-165`）；论文没有说明这个平局规则。

#### 4.3 论文与代码的一个边界差异

对内部网格，代码的四个“当前值—邻居值”平均再求平均，与论文公式一致。但实现使用 `np.roll`，数组边缘会与另一侧边缘相连，形成周期边界，而普通四邻域图通常不会这样连接（`ovrl.py/ovrlpy/_subslicing.py:61-77`）。因此该步骤是 **Partial** 匹配；目前没有证据说明它对论文样本结果的实际影响大小。

### 5. 第二步：不用细胞分割学习表达基底

#### 5.1 用三维 KDE 找“伪细胞”

对全部转录本位置做高斯核密度估计：

$$
f(x)=\sum_{i=1}^{n}K\left(\frac{x-x_i}{\sigma}\right),
$$

其中 $sigma$ 是 KDE 带宽。算法在总信号 KDE 中寻找高于阈值、且相互距离足够远的局部极大值，把这些高信号采样点称为 pseudo-cells（伪细胞）（`paper.md:109-127`）。

这里的“伪细胞”不是分割得到的真实细胞，而是用于学习常见局部表达模式的采样位置。代码先把坐标除以 KDE 带宽，再用内部 `sigma=1` 的高斯滤波实现相同的有效带宽，然后调用 `peak_local_max` 进行阈值和最小距离筛选（`ovrl.py/ovrlpy/_kde.py:73-136,205-220`）。

代码把“最少转录本数”转换成 KDE 阈值时使用：

$$
\tau_{\text{code}}=\frac{1.1n}{2\pi\sigma^2},
$$

其中 1.1 是源码中的额外 10% 裕量，论文没有写出这一实现细节（`ovrl.py/ovrlpy/_ovrlp.py:181-182`）。

#### 5.2 构建伪细胞×基因矩阵

在每个伪细胞位置 $x_j^*$，分别采样每个基因的 KDE：

$$
C_{j,g}=\sum_{x\in X_g}K\left(\frac{x_j^*-x}{\sigma}\right).
$$

于是得到 $C\in\mathbb{R}^{m\times p}$：$m$ 个伪细胞，$p$ 个基因（`paper.md:130-136`）。代码逐基因、分 patch 计算，并把结果保存成 `AnnData`（`ovrl.py/ovrlpy/_kde.py:227-290`）。

局部极大值始终基于所有基因寻找；用户指定的基因子集只影响后续表达矩阵和 PCA。这意味着“在哪里采样”和“用哪些基因描述采样点”是两个不同选择（`ovrl.py/ovrlpy/_ovrlp.py:184-223`）。

#### 5.3 PCA 与两种 UMAP

论文用 PCA 学习低维表达空间：

$$
Z=(C-\boldsymbol{\mu})V,
$$

其中 $V$ 是前 $k$ 个主成分，代码默认 $k=30$（`paper.md:139-145`; `ovrl.py/ovrlpy/_ovrlp.py:114-158,225-250`）。

同一组 PCA 因子还用于：

- 二维 UMAP：默认 `n_neighbors=20, min_dist=0`；
- 三维 RGB UMAP：默认 `n_neighbors=10, min_dist=0`，先对 PCA 因子做 L2 归一化，再经过三维 UMAP、PCA 旋转、固定旋转矩阵和 min–max 缩放得到颜色（`ovrl.py/ovrlpy/_utils.py:16-20,57-88`）。

RGB 颜色只用于把相似表达程序显示为相似颜色，不是监督细胞类型标签。

### 6. 第三步：构造上下层的局部表达向量场

对每个基因 $g$，分别在虚拟上层和下层做二维 KDE：

$$
C_{\text{top},g}(l)=
\sum_{x\in X_{\text{top},g}}K\left(\frac{l-x}{\sigma}\right),
$$

$$
C_{\text{bottom},g}(l)=
\sum_{x\in X_{\text{bottom},g}}K\left(\frac{l-x}{\sigma}\right).
$$

这两个向量描述平面位置 $l$ 上方和下方各基因的局部密度。论文随后写成：

$$
Z_{\text{top}}(l)=(C_{\text{top}}-\boldsymbol{\mu}_{\text{top}})V,
$$

$$
Z_{\text{bottom}}(l)=(C_{\text{bottom}}-\boldsymbol{\mu}_{\text{bottom}})V.
$$

#### 关键的代码—论文差异

源码确实逐基因计算上下层 KDE，并用 `pca.components_` 的对应基因权重累加到潜在向量（`ovrl.py/ovrlpy/_utils.py:139-207`）。但源码没有减去 `pca.mean_`、$\boldsymbol{\mu}_{\text{top}}$ 或 $\boldsymbol{\mu}_{\text{bottom}}$。实际更接近：

$$
\widetilde Z_{\text{top}}(l)=C_{\text{top}}(l)V,\qquad
\widetilde Z_{\text{bottom}}(l)=C_{\text{bottom}}(l)V.
$$

因此论文这两条投影公式与代码为 **Partial** 匹配（`ovrl.py/ovrlpy/_ovrlp.py:402-438`）。平移可能改变向量方向和余弦值，不能在没有实验的情况下假设省略中心化完全无影响。

### 7. 第四步：计算 VSI

对每个平面位置，计算上、下潜在表达向量的余弦相似度：

$$
\operatorname{VSI}(l)=
\frac{Z_{\text{top}}(l)\cdot Z_{\text{bottom}}(l)}
{\|Z_{\text{top}}(l)\|\,\|Z_{\text{bottom}}(l)\|}.
$$

直观解释：

- VSI 接近 1：上下层的表达组成方向相似；
- VSI 较低：上下层包含不同表达程序，可能有垂直混合；
- 低信号区域：余弦不可靠，必须结合 `signal_map` 掩膜解释。

代码逐行实现点积和两个 L2 范数；若任一向量范数为 0，最终值为 0（`ovrl.py/ovrlpy/_utils.py:210-213`）。因此原始 `integrity_map` 中的 0 既可能代表低相似度，也可能代表没有足够信号，不能脱离信号图单独解释。

高层 `analyse(min_transcripts=...)` 中的 `min_transcripts` 用于伪细胞采样；随后 `compute_VSI()` 仍使用自己的默认 `min_transcripts=2` 作为 VSI 信号掩膜阈值（`ovrl.py/ovrlpy/_ovrlp.py:338-349,443-474`）。论文 Xenium 分析写的 `min_transcripts=20` 因而主要控制伪细胞采样，而不是自动把 VSI 掩膜也设成 20（`paper.md:242-245`）。

### 8. 第五步：找候选重叠位置并做局部检查

代码在

$$
(1-\operatorname{VSI})\,\mathbf 1\{\text{signal}>s_{\min}\}
$$

上寻找局部极大值，也就是 VSI 的局部极小值。默认参数为：

- `min_distance=10`；
- `min_integrity=0.7`；
- `min_signal=3`。

返回的候选按 integrity 从低到高排序（`ovrl.py/ovrlpy/_ovrlp.py:476-528`）。函数注释中有一句把阈值方向写反，但实际条件正确地寻找低于阈值的 VSI（`_ovrlp.py:491-517`）。

对候选区域，ovrlpy 会计算每个转录本的三维高斯加权表达邻域，投影到已拟合 PCA/UMAP，再绘制上层、下层和两个侧视图（`ovrl.py/ovrlpy/_utils.py:91-136`; `_ovrlp.py:556-625`; `_plotting.py:357-502`）。代码在 PCA 前先归一化基因表达向量，并在 RGB UMAP 前再次归一化 PCA 因子；论文只明确描述了 PCA 后归一化，因此该可视化路径也是 **Partial** 匹配。

### 9. 如何理解低 VSI？

低 VSI 的正确解释是：“这个位置的上下层局部表达方向不一致，值得进一步检查。”可能原因包括：

- 不同细胞在 $z$ 方向重叠；
- 组织折叠或样本制备伪影；
- 一个细胞只部分位于切片内；
- 二维或三维分割没有正确描述局部结构；
- 亚细胞 RNA 定位导致单个细胞内部上下不均；
- 切片厚度、平台 $z$ 分辨率或 DAPI 焦面限制；
- 网格、带宽、基因集、PCA 维数或阈值设置不合适。

因此 0.7 不是跨组织、跨平台的通用生物学阈值。论文也建议检查低 VSI 区域的细胞组成并做上下层、侧视图、marker 和 DAPI 验证（`paper.md:76,181-184`）。

### 10. 论文中的主要评估结果

#### Xenium 小鼠脑

- 62,384,369 个转录本、248 个基因、162,033 个原始细胞分割；
- 上下虚拟切片中只有 78% 的细胞得到相同 MapMyCells 类型；
- CA1 区域选择的 152 个抑制性/胶质细胞中，只有约 20% 上下层一致（`paper.md:41,242`）。

#### MERSCOPE 小鼠脑

- 48,574,461 个转录本、438 个基因；
- 全组织上下层一致率为 83%，CA1 非神经元细胞为 51%；
- 扩展数据图 4 中，选定低 VSI 位置在相隔 1.5 µm 的 DAPI 焦面上显示不同深度的细胞核信号（`paper.md:44,61,296-320,499-504`）。

#### 下游过滤

论文按细胞/细胞核分割内像素的平均 VSI，使用 `<0.7` 标记 doublet。扩展数据图 5 报告：

- Xenium 细胞分割：36,846 / 162,033；
- Xenium 细胞核：36,831 / 162,018；
- MERSCOPE 细胞核：15,780 / 83,505。

去除这些区域后重新计算的 UMAP 中，许多细胞类型之间的桥接和混合区域减少（`paper.md:70,507-512`）。

### 11. 代码可复现性与证据边界

#### 已验证

核心算法——局部分层、KDE 伪细胞、PCA/UMAP、上下表达场、余弦 VSI、局部极小值检测、RGB 区域视图和分割像素 VSI 导出——都有直接源码证据。总体代码—论文一致性为 **high**。

#### MISSING / Not found

- `SUPP_MD` **MISSING**：没有获取 Supplementary Methods、Results 和 Supplementary Figs. 1–15。
- 论文另行提供的 `ovrlpy-publication` Jupyter notebooks 不在当前 `code source`，其内容和 commit 未验证。
- 当前包快照中 **Not found**：测试、示例数据、环境锁文件、完整统计分析、benchmark 驱动、论文图生成脚本和按细胞平均 VSI 后重新跑 PCA/UMAP 的流程。

### 12. 给研究者的实践建议

1. 先把 VSI 当作 QC 热图和候选生成器，而不是自动删除规则。
2. 同时查看 `signal_map`，避免把无信号像素误认为真实低完整性。
3. 用组织结构、marker、上下层 RGB、侧视图和可用的 DAPI z-stack 验证候选。
4. 根据组织异质性调整基因集和 PCA 维数；根据结构尺度调整网格和 KDE 带宽。
5. 报告低 VSI 区域比例，并比较保留/去除这些区域时下游结论是否稳定。
6. 对关键样本检查代码中的三个实现细节：周期边界、`z == z_center` 的排除，以及 VSI 投影未执行论文公式中的中心化。

### 总结

ovrlpy 的核心贡献，是把通常被二维分析忽略的 $z$ 坐标转化为一个可解释的局部表达一致性指标。它不需要先相信某一套细胞边界，而是先比较同一位置上下两层的表达方向；低 VSI 再触发结构、marker、分割和成像证据的联合检查。这个设计非常适合作为空间转录组分析中的独立质量控制层，但其阈值和生物学解释必须依赖具体组织与平台。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ovrlpy: Identifying 3D Signal Overlaps in Spatial Transcriptomics

### Overview

Ovrlpy is an unsupervised quality-control method for imaging-based spatially resolved transcriptomics (SRT). It uses measured transcript $z$ coordinates to detect regions where a conventional 2D projection mixes vertically different expression structures—overlapping cells, tissue folds, partial cells, or segmentation errors. The work was published in *Nature Biotechnology* in 2026 (DOI `10.1038/s41587-026-03004-8`).

### Problem and Existing Limitations

Imaging-based SRT profiles tissue sections that are typically 5–15 µm thick, yet most analyses project molecules into $x$–$y$ and assign them to 2D cell boundaries. This loses vertical structure and can merge signals from different cells. Direct 3D segmentation is an incomplete solution because axial imaging resolution is lower, some cells are cut by the section boundary, and nuclear/size priors can fail in folded or partial tissue (`paper.md:21-27,67`).

The paper evaluates two representative 3D segmentation tools: Baysor (*Nature Biotechnology*, 2022) and Proseg (*Nature Methods*, 2025). Both are valuable segmentation methods, but in the studied Xenium fold they missed leptomeningeal structures that remained visible in marker expression, motivating an independent segmentation-free QC signal (`paper.md:67,269-287`). Ovrlpy's expression sampling is inspired by the segmentation-free SSAM method (*Nature Communications*, 2021) and related sainsc work (*Small Methods*, 2025), but adds an explicit top-versus-bottom consistency score (`paper.md:109,361-364`).

### Method

Ovrlpy first adapts to spatial drift in measured $z$ coordinates. It bins transcripts in the tissue plane, computes a local mean or median $z$ center, and by default smooths that field for 20 message-passing iterations. Molecules above and below the local center form virtual top and bottom subslices.

Independently, a 3D Gaussian KDE over all transcripts is used to find high-signal local maxima (“pseudo-cells”). Per-gene KDE values sampled at those maxima produce a pseudo-cell-by-gene matrix, which is fitted with PCA. The same PCA components project the top and bottom per-gene 2D KDE fields into local latent expression vectors. Their cosine similarity is the vertical signal integrity:

$$
\operatorname{VSI}(l)=
\frac{Z_{\text{top}}(l)\cdot Z_{\text{bottom}}(l)}
{\|Z_{\text{top}}(l)\|\,\|Z_{\text{bottom}}(l)\|}.
$$

High VSI means the two subslices have similar expression direction; low VSI means they differ. Local minima of VSI above a signal threshold are candidate overlap events. A 2D UMAP and a three-dimensional RGB UMAP provide unsupervised colors for inspecting the top, bottom, and side views of each candidate. Existing cell segments are optional downstream units for aggregating the segmentation-free map.

### Evaluation and Main Results

- **Xenium mouse brain:** 62,384,369 transcripts across 248 genes and 162,033 original cell segments. Only 78% of segments received the same supervised MapMyCells type in both virtual subslices. In a CA1 subset of 152 inhibitory/glial cells, only about 20% were consistent between top and bottom (`paper.md:41,242`).
- **MERSCOPE mouse brain:** 48,574,461 transcripts across 438 genes. The paper reports 83% whole-tissue top/bottom consistency and 51% for non-neuronal CA1 cells, with selected low-VSI events corroborated by 1.5-µm-spaced DAPI focal planes (`paper.md:44,299`).
- **Tissue and technology generalization:** low-VSI structures were shown in Xenium and MERSCOPE brain, artificial folds, and MERSCOPE liver. A thinner virtual subslice had higher overall VSI than the corresponding full sample, supporting the overlap interpretation (`paper.md:58-64`).
- **Segmentation QC:** VSI correlated with MapMyCells cell-typing confidence for Baysor/Proseg segments and highlighted fold regions those segmenters did not model correctly (`paper.md:67`).
- **Downstream filtering:** using mean segment VSI below 0.7 labeled 36,846/162,033 Xenium cell segments, 36,831/162,018 Xenium nuclei, and 15,780/83,505 MERSCOPE nuclei as doublets. Recomputed UMAPs showed cleaner cell-type separation after removal (`paper.md:70,507-512`).
- **Scale benchmark:** the paper benchmarked runtime and memory on a Xenium Prime dataset with 125,756,304 transcripts across varying genes, area, and thread counts (`paper.md:323-326`). Exact benchmark values are in missing supplementary material.

The main and extended-data images directly show a balanced local virtual split, widespread top/bottom inconsistencies, low-VSI regions aligned with discordant expression patterns, DAPI z-stack support for selected MERSCOPE events, and reduced UMAP bridges after filtering. These examples support VSI as a useful candidate-generating QC map, but not as a universal probability or tissue-independent threshold.

### Code-Paper Fidelity

The acquired package snapshot at commit `5e0ea7ffc6fd19e2d9d31f5b2b75a915130f1246` has **high** fidelity to the algorithmic core. Direct source reads verify KDE pseudo-cell sampling, PCA and both UMAPs, top/bottom KDE fields, cosine VSI, local-minimum detection, RGB region views, and segment-level VSI export.

Three implementation differences matter:

- COM smoothing uses `np.roll`, creating periodic connections at array boundaries; interior updates match the paper equation.
- The source projects VSI fields with `C_top V` and `C_bottom V` but does not subtract the centering terms written in the paper's two field-projection equations.
- Transcript-level RGB visualization normalizes the gene vector before PCA as well as PCA factors before RGB UMAP, whereas the paper describes normalization after PCA.

The code also excludes transcripts with `z == z_center` from both subslices and uses a VSI signal-mask threshold independent of the pseudo-cell `min_transcripts` value passed to `analyse()`. These are verified behaviors, not demonstrated failure modes.

### Limitations

- Low VSI can arise from biological overlap, tissue folds, subcellular RNA localization, uneven sectioning, or platform-specific resolution; candidate regions require contextual inspection.
- Grid size, KDE bandwidth, selected genes, PCA dimension, signal masks, and integrity cutoff affect the result. The paper explicitly recommends tissue-specific calibration rather than a universal 0.7 threshold.
- Small overlaps may be smoothed away; $z$-plane spacing and DAPI focus constrain validation.
- Evaluation uses selected tissues and examples rather than a systematic sensitivity/specificity benchmark against emerging 3D or multimodal segmentation.
- Removing low-VSI cells can itself introduce bias because overlaps are not uniformly distributed across tissue or cell types.

### Reproducibility

**Workspace reproducibility assessment: 3/5.** The package is open-source under MIT, installable through PyPI/Bioconda, and the paper names public raw/generated datasets plus a separate `ovrlpy-publication` notebook repository (`paper.md:335-344`). The acquired code is compact and traceable to a recorded commit, and its README contains a usable API quickstart.

However, this workspace contains only the package snapshot. The separate publication notebooks, example data, environment lockfile, statistical workflows, benchmark driver, and figure scripts were not acquired or verified. The package itself has no local tests. `SUPP_MD` and Supplementary Figs. 1–15 are **MISSING**, so supplementary parameter profiles, quantitative benchmarks, and several sensitivity analyses could not be checked. The current workspace supports close verification of the method implementation, but not end-to-end reproduction of the article's results.

### Bottom Line

Ovrlpy converts the otherwise discarded vertical coordinate in imaging-based SRT into an interpretable, segmentation-free consistency map. Its practical strength is not automatic correction: it localizes suspicious 3D-to-2D mixtures and provides expression-colored views so analysts can decide whether tissue overlap, folding, segmentation, or biology explains the signal. The released package implements that core method closely, while full paper reproduction requires evidence outside the acquired snapshot.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
