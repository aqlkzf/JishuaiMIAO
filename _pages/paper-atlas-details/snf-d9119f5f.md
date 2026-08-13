---
layout: default
permalink: /paper-atlas/snf-d9119f5f/
title: "SNF"
nav: false
description: "SNF 先为每一种数据类型建立一个样本相似网络，然后让这些网络通过局部邻域反复交换信息，最后得到一个融合网络；这个融合网络既保留多个数据类型共同支持的相似性，也能保留某个数据类型独有但可信的互补信息。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Methods · 2014</span>
    </div>
    <h1>SNF</h1>
    <p>Similarity network fusion for aggregating data types on a genomic scale</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/nmeth.2810" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SNF">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SNF 方法中文解释

### 这篇论文要解决什么问题

SNF（Similarity Network Fusion）解决的是多组学数据整合问题：同一批样本或患者往往同时有 mRNA 表达、DNA 甲基化、miRNA 表达等不同数据类型。论文指出，直接把所有特征拼接在一起会进一步稀释每个数据类型本来就不高的信噪比；分别分析每个数据类型又会得到彼此不一致的亚型结论；先筛基因再聚类会引入偏差；iCluster 这类联合潜变量方法虽然强，但对基因预筛选敏感，且难以扩展到全基因组尺度 (`paper.md:21-24`)。

SNF 的核心思想是：不要先在特征空间里硬拼不同组学，而是先把每个数据类型都转成“样本-样本相似网络”，再融合这些网络。这样每个节点是患者或样本，边权是两个样本在某个数据类型上的相似程度 (`paper.md:27-30`, `paper.md:39-50`)。

### 一句话理解 SNF

SNF 先为每一种数据类型建立一个样本相似网络，然后让这些网络通过局部邻域反复交换信息，最后得到一个融合网络；这个融合网络既保留多个数据类型共同支持的相似性，也能保留某个数据类型独有但可信的互补信息。

### 输入、输出和变量

| 记号 / 变量 | 含义 | 维度 |
|---|---|---|
| `X^(v)` | 第 `v` 个数据类型的样本特征矩阵 | `n x d_v` |
| `x_i` | 第 `i` 个样本 / 患者 | feature vector |
| `rho(x_i, x_j)` | 两个样本在某个数据类型上的距离 | scalar |
| `W^(v)` | 第 `v` 个数据类型的样本相似矩阵 | `n x n` |
| `P^(v)` | 归一化后的完整状态/转移矩阵 | `n x n` |
| `S^(v)` | 只保留 K 近邻的稀疏局部核 | `n x n` |
| `W_fused` | 融合后的样本相似网络 | `n x n` |
| `C` | 聚类数 / 亚型数 | scalar |

代码里的主要对应关系：

| 论文概念 | 代码变量 / 函数 | 位置 |
|---|---|---|
| 距离矩阵 | `dist2`, `chiDist2` | `SNF_code/SNFtool/R/dist2.R:1-13`, `chiDist2.R:1-17` |
| 相似矩阵 `W` | `affinityMatrix(Diff,K,sigma)` | `SNF_code/SNFtool/R/affinityMatrix.R:1-17` |
| KNN 稀疏核 `S` | `dominateset(xx,KK)` | `SNF_code/SNFtool/R/dominateset.R:1-16` |
| 网络融合 | `SNF(Wall,K,t)` | `SNF_code/SNFtool/R/SNF.R:1-50` |
| 谱聚类 | `SpectralClustering(affinity,K)` | `SNF_code/SNFtool/R/SpectralClustering.r:1-32` |
| 新样本标签传播 | `group_predict`, `Cs_prediction` | `group_predict.r:1-20`, `Cs_prediction.r:1-15` |

### 计算流程

```text
多种数据类型的同一批样本
        |
        v
每个数据类型单独预处理
  - 缺失过多的样本/特征过滤
  - KNN 缺失值填补
  - 标准化
        |
        v
每个数据类型计算样本距离矩阵
        |
        v
距离矩阵 -> 相似矩阵 W^(v)
        |
        v
W^(v) -> 完整归一化矩阵 P^(v)
W^(v) -> KNN 稀疏局部核 S^(v)
        |
        v
不同数据类型的网络互相扩散信息，迭代 t 次
        |
        v
平均并对称化，得到融合网络 W_fused
        |
        +--> 谱聚类得到患者亚型
        +--> 标签传播预测新患者亚型
        +--> 后续生存分析 / 网络解释
```

### 第一步：每个数据类型建一个相似网络

论文把样本看成图的节点，把样本之间的相似度看成边权。对于第 `v` 个数据类型，先根据样本间距离构造 `W^(v)` (`paper.md:162-168`)。连续变量可以用欧氏距离，离散变量论文建议用卡方距离 (`paper.md:168-168`, `paper.md:246-246`)。

R 包的实现是：

- `dist2` 计算平方欧氏距离；
- `chiDist2` 计算卡方距离；
- `affinityMatrix` 把距离矩阵转成相似矩阵：先对称化距离矩阵，再用 K 近邻距离估计局部尺度，最后用高斯密度形式得到相似度并对称化 (`SNF_code/SNFtool/R/affinityMatrix.R:1-17`)。

### 第二步：保留局部邻域

论文强调 `P` 和 `S` 的区别：`P` 保存完整相似信息，`S` 只保存 K 近邻局部结构 (`paper.md:171-180`)。直觉是：近邻相似性更可信，远距离弱连接更容易是噪音，可以通过网络扩散间接恢复。

代码里 `dominateset` 对每一行排序，把非 top-K 的相似度置零，然后做行归一化 (`SNF_code/SNFtool/R/dominateset.R:1-16`)。这就是论文里稀疏局部核 `S` 的实现。

### 第三步：多网络迭代融合

论文的核心是迭代更新每个数据类型的状态矩阵：每个网络在自己的局部结构约束下，吸收其他网络的信息 (`paper.md:183-204`)。如果一条边只是噪音且没有其他网络支持，它会被削弱；如果某个数据类型里强支持一组样本相似性，这种信息可以传播给其他网络；如果多个网络在局部邻域里共同支持弱边，弱边也可能保留下来 (`paper.md:50-50`)。

`SNF.R` 的实现步骤：

1. `Wall` 是所有相似矩阵的列表。
2. `LW = length(Wall)` 表示数据类型个数。
3. 每个矩阵先用 `dominateset` 构造稀疏局部网络。
4. 每次迭代中，对每个目标网络 `j`，把其他网络求和。
5. 用 `newW[[j]] %*% (...) %*% t(newW[[j]])` 做扩散更新。
6. 每轮更新后归一化、加对角线、对称化。
7. 最后把所有网络平均并对称化得到 `W` (`SNF_code/SNFtool/R/SNF.R:1-50`)。

一个代码细节：实现里把其他网络的平均值和单位矩阵混合，权重是 `0.95` 和 `0.05` (`SNF_code/SNFtool/R/SNF.R:31-31`)。这属于代码可见的稳定化实现，论文转换后的 Markdown 没有清楚展示这部分公式。

### 第四步：在融合网络上聚类

论文用谱聚类从融合图里得到疾病亚型 (`paper.md:216-225`)。代码 `SpectralClustering` 构造图拉普拉斯矩阵，计算特征向量，离散化后得到标签；如果某个簇样本数小于等于 5，则退回到 k-means (`SNF_code/SNFtool/R/SpectralClustering.r:1-32`)。

README 里的标准示例是：

```text
Dist1, Dist2 -> W1, W2 -> W = SNF(list(W1,W2), K, T) -> SpectralClustering(W,C)
```

对应代码行见 `SNF_code/SNFtool/README:29-48`。

### 第五步：预测新患者标签

补充材料描述了一个基于标签传播的新患者预测方法：把新患者和已有患者放入同一个相似矩阵，构造转移核，然后反复传播标签，同时固定已有患者标签 (`supplementary/supplementary_text_figures.md:949-966`)。

代码里 `group_predict` 会把训练和测试数据合并，对每个 view 计算距离和相似矩阵，调用 `SNF` 得到融合网络，再调用 `Cs_prediction` 传播标签 (`SNF_code/SNFtool/R/group_predict.r:1-20`)。`Cs_prediction` 提供闭式解和 1000 次迭代传播两种模式 (`SNF_code/SNFtool/R/Cs_prediction.r:1-15`)。

### 评价结果

论文在五个 TCGA 癌症数据集上评估：GBM、BIC、KRCCC、LSCC、COAD，主要数据类型是 DNA 甲基化、mRNA 和 miRNA (`paper.md:79-85`)。评价指标包括 Cox log-rank P value、生存亚型分离程度、silhouette 聚类一致性和运行时间 (`paper.md:82-85`)。

GBM 例子中，SNF 融合 215 个患者的三种数据，得到比单一数据类型更清晰的患者网络结构，并且融合网络的边颜色可以显示每条边由哪些数据类型支持 (`paper.md:67-73`)。Figure 2 的图像也显示，单一组学网络各自有不同结构，而融合网络形成更清楚的三个亚型区域。

跨癌症比较中，Figure 3 显示 SNF 在 survival P value 和 silhouette 上通常优于 concatenation 和 iCluster，同时运行时间保持接近快速方法；iCluster 的运行时间曲线明显上升。论文据此认为 SNF 不需要强依赖基因预筛选，也能扩展到较大特征规模 (`paper.md:91-102`)。

### 代码复现边界

代码来自 Supplementary Software ZIP，不是 GitHub 仓库 (`paper.md:344-347`)。它能复现核心 SNF 算法：相似矩阵构造、KNN 稀疏核、网络融合、谱聚类、NMI 和标签传播。

但是有两个重要边界：

- **Not found**：论文 Methods 里描述的 network-regularized Cox survival prediction (`paper.md:228-240`) 在 `SNF_code/SNFtool/R` 里没有找到实现。
- **MISSING**：Nature HTML 转 Markdown 时，方法部分若干公式没有完整显示成 `$$...$$`，所以如果要逐字核对公式，需要回到原始 PDF/HTML。

因此，SNF 的核心算法可复现性较好；完整复现论文所有 TCGA/METABRIC 实验和 survival prediction 分析则需要额外数据和脚本。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Similarity Network Fusion (SNF)

### Problem

Modern cancer cohorts often contain several matched genomic data types for the same patients, such as mRNA expression, DNA methylation, and miRNA expression. The paper argues that concatenating all measurements lowers the signal-to-noise ratio, analyzing each data type independently produces inconsistent subtype calls, preselecting genes biases the analysis, and iCluster-style integrative clustering can become sensitive to the selected feature set and expensive at genome scale (`paper.md:21-24`).

### Proposed Method

Similarity Network Fusion integrates data in sample space. For each data type, SNF builds a patient-by-patient similarity network; it then iteratively diffuses information between networks and averages them into one fused similarity network (`paper.md:27-30`, `paper.md:39-50`). The fused network is intended to retain both common signals and complementary signals across data types: weak unsupported edges are suppressed, strong modality-specific edges can be propagated, and consistently supported low-weight edges can be retained through shared neighborhoods (`paper.md:50-50`).

The method workflow is:

1. Filter/impute/normalize each view.
2. Compute pairwise distances for each view.
3. Convert distances into view-specific affinity matrices.
4. Construct a sparse KNN kernel per view.
5. Iteratively update every view using the other views.
6. Average the diffused matrices into a fused network.
7. Use the fused network for spectral clustering, label prediction, or downstream network analysis.

### Evaluation

The main evaluation uses five TCGA cancer profiles: GBM, BIC, KRCCC, LSCC, and COAD, with DNA methylation, mRNA, and miRNA data (`paper.md:79-85`). Metrics include Cox log-rank P value for subtype survival separation, silhouette score for cluster coherence, and running time (`paper.md:82-85`, `paper.md:153-156`).

In GBM, SNF fuses three data types for 215 patients and produces a clearer subtype network than any single modality; the fused network also records which modality or modality combination supports each patient-patient edge (`paper.md:67-73`). Across cancer datasets, the paper reports that SNF had significant survival separation and higher silhouette scores across feature-selection sizes, while iCluster was more sensitive to gene preselection and scaled poorly in running time (`paper.md:91-102`). Figure 3 visually supports this: SNF's red curves are generally higher for survival/silhouette while remaining near the fast methods in runtime (`figure_analysis.md`).

### Code And Reproducibility

The available code is a Supplementary Software ZIP, not a GitHub repository (`paper.md:344-347`). It is an R package, `SNFtool`, whose metadata describes fusing multiple network views into a status matrix for retrieval, clustering, and classification (`SNF_code/SNFtool/DESCRIPTION:1-8`). The README gives a runnable example: set `K`, `alpha`, and `T`, compute distances, build affinity matrices, call `SNF(list(W1,W2), K, T)`, then run `SpectralClustering` (`SNF_code/SNFtool/README:7-48`).

The code-paper match is **medium-high** for the core SNF algorithm: affinity construction, KNN sparse kernels, iterative fusion, final averaging, spectral clustering, NMI utilities, and label propagation are implemented in compact R source files (`doc_code.md`). Important caveat: the paper's network-regularized Cox survival prediction model is described in the Methods section (`paper.md:228-240`) but was **Not found** in the extracted `SNFtool/R` source. The package also does not include the full TCGA/METABRIC benchmark scripts. Thus the supplementary package can reproduce the core algorithm and examples, but not every experiment in the paper.

### Rating

**Reproducibility: 4/5 for the core SNF algorithm, 2/5 for the full paper experiments.** The main algorithm is available as a small R package with example data and clear defaults; however, exact benchmark reproduction would require the supplementary data and additional analysis scripts not present in the software ZIP, and the survival-risk Cox regularization implementation is missing from the searched package.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
