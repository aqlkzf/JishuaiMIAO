---
layout: default
permalink: /paper-atlas/scale-1de4796e/
title: "SCALE"
nav: false
wide: true
description: "常规空间聚类通常输出一张分区图，但真实组织常同时具有粗粒度和细粒度结构。例如脑组织在高层可以分为皮层、海马和丘脑，在低层又可继续分成皮层层次和海马亚区。SCALE（Spatial Clustering At multiple LEvels）要解决的不是“选唯一最佳聚类”，而是从许多空间图尺度与聚类分辨率中，找出一组稳定且近似嵌套的分区。 方法依赖三项假设：同一功能域附近的表达环境相似；有意义的域在某个观察尺度上具有空间连续性；"
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
      <span>Domain Clustering</span>
      <span>Nucleic Acids Research · 2026</span>
    </div>
    <h1>SCALE</h1>
    <p>SCALE: unsupervised multiscale domain identification in spatial omics data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1093/nar/gkaf1456" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SCALE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/imsb-uke/scale" target="_blank" rel="noopener noreferrer" aria-label="Open code for SCALE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SCALE：无监督寻找空间组织的多个层级

### 先把问题说清楚

常规空间聚类通常输出一张分区图，但真实组织常同时具有粗粒度和细粒度结构。例如脑组织在高层可以分为皮层、海马和丘脑，在低层又可继续分成皮层层次和海马亚区。SCALE（Spatial Clustering At multiple LEvels）要解决的不是“选唯一最佳聚类”，而是从许多空间图尺度与聚类分辨率中，找出一组稳定且近似嵌套的分区。

方法依赖三项假设：同一功能域附近的表达环境相似；有意义的域在某个观察尺度上具有空间连续性；粗域通常包含更细的子域。第三项只是组织结构的常见倾向，并非普遍定律。论文也承认血管等低层结构可能跨越多个高层域，此时严格嵌套会遗漏真实结构。

### 输入和输出

输入是带有表达矩阵 `.X` 和二维坐标 `.obsm["spatial"]` 的 AnnData。输出包含用户指定数量的层级标签 `scale_l0_*`, `scale_l1_*`, …，以及不同空间尺度、损失权衡和 Leiden 分辨率下的嵌入、聚类稳定性和熵搜索结果。

默认搜索不是一次训练：代码会遍历多个距离阈值 $r$（默认 15 到 55）、15 个 $\lambda$ 值，并在选出的嵌入上遍历约 60 个 Leiden 分辨率。因此“自动选择”减少了人工标注调参，但代价是大量模型和聚类计算。

### 第一步：为每个空间尺度学习细胞表示

对每个距离阈值 $r$，SCALE 用坐标构建空间图：细胞是节点，距离小于 $r$ 的细胞对成为边。代码也支持 $k$NN 图。每个节点的表达向量会在图构建时逐基因 min–max 缩放到 $[0,1]$；若开启预处理，还会先过滤低计数细胞/低频基因、总量归一化并 `log1p`。

编码器由一层 GATv2、ReLU、BatchNorm 和线性层组成，输出细胞嵌入 $z_i$。两个解码器分别完成：

- 邻接重建：根据嵌入距离判断一对细胞是否是空间边，并用随机负边计算二元交叉熵；
- 表达重建：线性解码嵌入并以均方误差重建节点表达。

论文写作

$$
L=L_1+\lambda L_2,
$$

其中 $L_1$ 是表达 MSE，$L_2$ 是邻接 BCE。代码把函数名反过来叫：`loss1` 是 BCE，`loss2` 是 MSE，并计算 `lambda * loss1 + loss2`。虽然命名相反，代数作用与论文一致：$\lambda$ 控制空间邻接重建相对表达重建的权重。

### 第二步：为每个 $r$ 选择 $\lambda$

对每个 $r$，代码训练完整的 $\lambda$ 网格，并计算每个嵌入相对于一个四近邻空间图的平均 Moran's I。随后对 Moran's I–$\lambda$ 曲线拟合 sigmoid：如果曲线接近平台，选“饱和点”；否则选最高 Moran's I。这样保留每个空间尺度的一份嵌入。

这个步骤不是标准的多目标 Pareto 优化器，而是网格训练后用空间自相关选择一个权衡点。它会偏向空间结构，但并不保证选中的表达重建误差在统计意义上最优。实现还在二阶差分极小点上加了 3 个索引位置，这是论文算法未明确写出的选择偏移。

### 第三步：产生候选聚类并评估稳定性

每个保留嵌入都用一系列 Leiden 分辨率 $\gamma$ 聚类，并以不同随机种子重复。论文定义稳定性为重复聚类两两 ARI 之和：

$$
S(r,\gamma)=\sum_{i\ne j}\operatorname{ARI}
\left(D^{(i)}(r,\gamma),D^{(j)}(r,\gamma)\right).
$$

代码实际计算无序重复对的平均 ARI。重复数固定时，求和与平均只差常数，候选排名不变；若不同设置使用不同有效重复数，两者才不再严格等价。默认流程保留稳定性最高的 15% 设置。

### 第四步：用嵌套熵挑选多个层级

设低层细分域 $d_j^q$ 与高层粗域 $d_i^p$，论文定义

$$
P_{ij}=P(x\in d_i^p\mid x\in d_j^q)
=\frac{|d_i^p\cap d_j^q|}{|d_j^q|},
$$

并对每个细分域的高层归属计算熵：若一个细分域几乎完全落在某个粗域内，熵接近 0；若它跨越多个粗域，熵较高。搜索还要求层级之间的簇数增加达到阈值，避免选到几乎相同的两份聚类。

```text
表达矩阵 + 坐标
      │
      ├─ 遍历空间尺度 r
      │     └─ 遍历 λ：GAT 编码 + 邻接/表达双重重建
      │
      ├─ 每个 r 用 Moran's I 选一个 λ
      │
      ├─ 遍历 Leiden 分辨率 γ 并重复聚类
      │
      ├─ 按重复聚类 ARI 保留最稳定的 15%
      │
      └─ 在候选层级组合中最小化嵌套熵
            ↓
       多层空间域标签
```

对于两层搜索，代码熵与论文逻辑基本一致；对于三层及以上，论文说对相邻层级熵取平均，代码却取最大值，即最小化最差相邻层级的熵。这是更保守的 minimax 规则，会产生不同的多层答案。代码使用自然对数而论文写 $\log_2$，但若只比较排名，这只是固定比例缩放。

### 五张主图告诉了什么

- Fig. 1 展示从空间图、GNN 双解码、重复 Leiden 到稳定性/熵搜索的全流程。
- Fig. 2 在 MERFISH 脑数据上比较 NeST 与 SCALE。SCALE 的两层图更接近 Allen atlas 注释，特别是海马子区；论文报告高层和低层 AMI 中位数分别为 0.53 和 0.62。
- Fig. 3 在 Visium-HD 脑数据上再次得到粗粒度脑区与细粒度亚区，高/低层 AMI 约 0.55/0.62。
- Fig. 4 在人肾组织中给出肾小球与肾小管间质的高层划分，以及近曲小管、远曲小管、Henle 袢、血管等低层区域。专家 H&E 标注只直接评估了肾小球检测，报告敏感度 100%、特异度 88%，不能外推为所有低层域都有同等准确率。
- Fig. 5 是单尺度基准。SCALE 在 MERFISH 上领先，在 Xenium 上与 NichePCA 接近。所谓“提升 191.1 percentage points”是相对于较低 NeST 分数计算的相对提升表达，不是 AMI 绝对增加 1.911。

### 代码与论文的一致性和边界

整体保真度评为 **中等偏高**。GAT 编码、邻接/表达双重解码、$r$–$\lambda$ 网格、Moran's I 选模、重复 Leiden、ARI 稳定性和嵌套熵都能在源代码中定位；

需要保留的实现差异与缺陷：

- 多层熵用相邻层级熵的最大值，而不是论文所述平均值；两层时无差异。
- `train()` 只有在 `cfg.device is None` 时才给局部变量 `device` 赋值。用户显式设置设备字符串会在后续 `.to(device)` 处触发未绑定变量错误。
- sigmoid 曲线拟合失败时，异常分支试图把五元组解包给三个变量，异常恢复路径本身也会失败。
- GAT 输入忽略 `edge_attr` 距离权重；距离只决定是否存在边，不作为注意力消息的连续权重。
- `repeated_negative_sampling=False` 是默认值，意味着同一模型的负边在训练前采一次并沿 500 epoch 固定使用；论文主文没有突出这一点。
- 默认 `cfg.preprocess=False`，所以“原始 counts 自动预处理”不是入口函数的无条件行为；数据必须已经准备好，或显式开启。

### 如何正确理解“无监督自动化”

SCALE 不用真实区域标签选择 $r$、$\gamma$ 和层级组合，这一点成立。但用户仍需指定搜索范围、目标层级数、最小簇数或层级间最小簇数增量；稳定性与严格嵌套本身也是建模偏好。它适合细胞级空间数据和近似嵌套的组织结构，而对 50 µm Visium 等大 spot 数据、跨高层域延伸的低层结构，以及计算预算有限的场景，论文明确给出了限制。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SCALE: Unsupervised Multiscale Domain Identification in Spatial Omics

SCALE identifies several nested spatial-domain resolutions rather than returning one manually tuned clustering. It builds spatial graphs over a grid of distance thresholds (or $k$NN sizes), trains a GATv2 encoder with adjacency- and expression-reconstruction decoders across a grid of loss weights, selects one embedding per graph scale using Moran's I, and clusters each selected embedding over many Leiden resolutions. It retains stable solutions by repeated-clustering ARI and chooses the requested number of levels by minimizing conditional-entropy violations of nesting.

The paper evaluates simulated data, MERFISH and Visium-HD mouse brain, Xenium kidney, and Xenium mouse brain data. In the main multiscale comparisons, SCALE recovers coarse brain regions and finer cortical/hippocampal substructure more completely than NeST. The kidney example separates glomerular from tubulointerstitial tissue at a high level and identifies finer tubular/vascular compartments; expert H&E annotations directly support glomerular detection with 100% sensitivity and 88% specificity, not every inferred compartment. Single-scale benchmarks place SCALE first on MERFISH and approximately level with NichePCA on Xenium. Relative “percentage point” improvement language against low NeST scores should not be read as an absolute AMI increase larger than the metric's range.

Core fidelity is **medium-to-high**: the central graph-learning, model-selection, stability, and entropy components are present. Material differences remain: code averages rather than sums repeat ARIs; for three or more levels it minimizes the maximum adjacent-level entropy rather than the paper's stated average; and it uses natural-log entropy. Two clean-run defects also matter—an explicitly configured device leaves `device` undefined in `train()`, and the sigmoid-fit exception handler has an invalid tuple unpack. Default preprocessing is off, search remains computationally expensive, and the nesting assumption can exclude biologically meaningful structures crossing coarse-domain boundaries.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
