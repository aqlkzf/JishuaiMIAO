---
layout: default
permalink: /paper-atlas/gnn-singlecell-review-555e64bc/
title: "GNN_singlecell_review"
nav: false
description: "这篇综述收集了 107 篇 GNN 单细胞应用，覆盖六类变体、五类组学和 77 个常用公开数据集。最重要的主线不是背诵 100 多个方法名，而是回答三个问题： 什么被当作节点？细胞、基因、peak、空间 spot、蛋白还是多种对象？ 什么关系被画成边？相似性、空间邻接、共表达、PPI、GRN、配体–受体还是跨组学先验？ 消息传播后的表示用来做什么？插补、聚类、注释、网络推断、整合或预测？"
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
      <span>Representation Models</span>
      <span>Briefings in Bioinformatics · 2025</span>
    </div>
    <h1>GNN_singlecell_review</h1>
    <p>Graph neural networks for single-cell omics data: a review of approaches and applications</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1093/bib/bbaf109" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 单细胞组学中的图神经网络：如何读这张方法地图

### 综述讲的不是一个模型，而是一套建模语言

这篇综述收集了 107 篇 GNN 单细胞应用，覆盖六类变体、五类组学和 77 个常用公开数据集。最重要的主线不是背诵 100 多个方法名，而是回答三个问题：

1. 什么被当作节点？细胞、基因、peak、空间 spot、蛋白还是多种对象？
2. 什么关系被画成边？相似性、空间邻接、共表达、PPI、GRN、配体–受体还是跨组学先验？
3. 消息传播后的表示用来做什么？插补、聚类、注释、网络推断、整合或预测？

只有先回答这三个问题，GCN、GAT、VGAE 等名字才有意义。

### 1. 为什么单细胞数据适合图

表达矩阵本身是欧氏表格，但许多生物问题关心关系：相似细胞、相互作用基因、组织邻居、调控元件与靶基因。图写为 $\mathcal G=(\mathcal V,\mathcal E)$，节点 $v$ 的表示通过邻域更新：

$$
h_v^{(t+1)}=f_w\big(y_v,y_{co[v]},h_{N(v)}^{(t)},y_{N(v)}\big),
$$

再由 $g_w(h_v)$ 产生标签、重构值或边概率。图 1 用规则的一维序列、二维网格与不规则图比较，说明普通固定卷积核不能直接覆盖可变大小、无固定顺序的邻域。

但“单细胞天然是图”只是建模选择的一部分。cell–cell kNN 通常由同一表达矩阵推出来，并非实验直接观测的真实细胞联系；图的可信度决定 GNN 结论的上限。

### 2. 六种 GNN 变体如何选择

#### GCN

用归一化邻接矩阵平均并变换邻居特征，成熟、简单，因而在图 4 中使用最多。适合固定同质图上的半监督分类和表示学习；深层时容易 over-smoothing。

#### GraphSAGE

对每个节点采样固定数量邻居再聚合，适合大图和未见新节点的归纳推断。采样提升规模能力，也可能漏掉稀有但关键的生物邻居。

#### GAT

学习注意力系数，让不同邻居贡献不同。适合噪声或多种关系强弱不一的图；attention weight 是模型内部权重，不能直接解释成生物因果强度。

#### GTN

将 Transformer 式全局/动态注意力用于图，适合异构关系和长程依赖，但计算代价及结构编码更难设计。

#### GAE 与 VGAE

编码节点到潜空间，再重构邻接或特征；VGAE 额外学习概率分布并用 KL 约束。适合无监督表示、插补和链接预测，但重构技术噪声同样可能取得低损失。

图 2 视觉展示 GCN、GraphSAGE、GAT 和 VGAE；本地全文没有收录作者引用的 Supplementary Text S2–S7，因此不声称已经逐式核验补充推导。

### 3. 按图类型而不是按模型名分类

| 图 | 常见任务 | 主要假设 |
|---|---|---|
| cell–cell | 聚类、注释、插补、疾病/扰动预测 | 相似细胞应交换信息 |
| gene–gene | GRN、KO 响应、通路与扰动 | 共表达或先验边接近真实调控 |
| cell–gene 二部图 | 注释、异构表示 | 表达连接能联合表示细胞与基因 |
| spot–spot spatial graph | 空间域、表达预测、解卷积 | 物理邻近具有组织学意义 |
| feature–feature guidance graph | 多组学整合 | 跨模态先验可对齐语义 |
| 多类型异构图 | 稀有群体、网络推断、跨组学 | 不同边类型可被共同校准 |

例如，GLUE 用 feature guidance graph 对齐模态；MarsGT 把 cell、gene、peak 放入异构图；GraphCpG 把 cell–locus 甲基化矩阵写成二部图；STAGATE/SpaGCN 一类方法把空间邻接加入表达分析。这些差异常比换一个聚合器更根本。

### 4. 五类组学中的任务版图

#### 表观组学

scATAC 标签转移可从 scRNA 参考建混合图（scGCN、HyGAnno），也可用带标签 scATAC 参考直接训练（SANGO）。scDNAm 与 scHi-C 极稀疏，GraphCpG/HiC-SGL 将缺失值变成链接预测或图重构问题。方法数量仍明显少于 scRNA。

#### scRNA-seq

图 3 中方法最密集：插补、降维、聚类、注释、GRN、通讯、疾病与扰动预测都有多种实现。cell–cell kNN 最常见，gene–gene 与 cell–gene 图用于更机制化的任务。综述没有在同一数据划分上横评全部方法，因此不能从方法数量推导性能排名。

#### 空间转录组

最大任务群是 spatial domain identification。空间位置提供自然邻接，但边阈值、组织图像和表达相似性的融合方式会决定是否平滑掉真实边界。通讯推断还需要配体–受体先验，不能把近邻直接称为通讯。

#### 单细胞蛋白组

综述只列出 scPROTEIN 与 SNOWFLAKE 等少量应用，显示这是明显欠探索领域；少量方法不能支持稳定的架构结论。

#### 多组学

一类方法让各模态 encoder 进入共享潜空间，再用 discriminator/guidance graph 对齐（GLUE）；另一类直接构建 cell–gene–peak 等异构图（MarsGT、DeepMAPS）。任务还包括解卷积、多切片整合、蛋白丰度和代谢流预测。

### 5. 图 3 和图 4 应该怎样读

图 3 是“组学 → 任务 → 方法名”的目录，适合找候选方法，不是效果排行榜。图 4a 的数字是 GCN 46、GAT 25、GAE 21、VGAE 16、GTN 7、GraphSAGE 4；总和为 119，大于 107，因为方法可能同时使用多个变体。GCN 占比最大更可能反映成熟度与易用性，不能证明 GCN 在所有任务最优。

图 4b 显示 scRNA-seq 占据最大份额，空间转录组其次，多组学任务更加分散；这也暴露了 proteomics 和 epigenomics 的证据稀疏。

### 6. 作者总结的四个关键权衡

1. **图构建**：k、距离、相似度阈值与外部网络质量会改变传播路径。
2. **规模与特征保留**：HVG 筛选降低成本，也可能删掉低表达关键调控因子。
3. **局部与全局**：加深网络扩大感受野，却增加计算并导致 over-smoothing。
4. **知识与偏差**：PPI/GRN/配体–受体先验增强解释性，同时继承数据库偏差。

作者把 foundation models 与子细胞分辨率视为机会。这里是前瞻性判断，不是本文统一实验验证的结论。

### 7. 研究者使用这篇综述的正确方式

- 先用组学和任务缩小图 3 的方法范围；
- 再比较节点/边定义、是否支持新细胞、监督需求和输出类型；
- 检查建图是否泄漏测试信息，是否报告 k/阈值敏感性；
- 对网络边、attention 和通讯结果要求独立数据库或实验验证；
- 在同一数据上加入非 GNN 强基线，控制特征选择和计算预算。

### 8. 证据边界

这是一篇叙述性综述，不是系统评价或统一 benchmark。主文未给出检索式、纳排流程、偏倚评估或 107 个方法的统一复现。当前工作区只有 PMC 主文、表格和 4 张主图；论文引用的 Supplementary Text S1–S15 与补充表正文在本地文件中 Not found。因而这里可以可靠总结作者的分类与讨论，但不能把“successful applications”改写为 107 个经独立验证的成功案例，也不提供任何代码证据。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## GNNs for Single-Cell Omics：综述摘要

### 综述范围

本文系统整理图神经网络在单细胞组学中的应用，覆盖 107 篇方法论文、六类常见 GNN 变体和 77 个常用公开数据集。范围横跨单细胞表观组、转录组、空间转录组、蛋白组及多组学，任务包括插补、降维、聚类/注释、空间域识别、调控与细胞通讯推断、扰动预测、解卷积和跨模态整合。

### 核心组织框架

| 维度 | 主要类别 | 综述中的作用 |
|---|---|---|
| 图模型 | GCN、GraphSAGE、GAT、GTN、GAE、VGAE | 分别强调邻居卷积、采样聚合、注意力、Transformer、重构及概率潜变量 |
| 图对象 | cell–cell、gene–gene、cell–gene、spot–spot、feature–feature、异构图 | 把数据相似性、空间邻接或先验生物网络编码为可传播关系 |
| 组学 | epigenomics、scRNA-seq、SRT、proteomics、multi-omics | 决定节点/边的生物含义及数据稀疏性 |
| 任务 | 预处理、表示学习、预测、网络推断、整合 | 决定监督信号和输出解释 |

综述最有价值的洞见不是“GNN 普遍优于非 GNN”，而是图构建本身就是模型假设：kNN 相似图、空间邻接、PPI/GRN/配体–受体先验或异构 guidance graph 会决定信息能传播到哪里。换图可能比换 GCN/GAT 主干更改变生物结论。

### 领域分布

图 3 显示 scRNA-seq 方法数量最多，尤其集中于低维表示、聚类和细胞类型识别；空间转录组集中于空间域识别；多组学任务类型最分散；表观组和蛋白组方法明显较少。图 4a 统计的模型标签为 GCN 46、GAT 25、GAE 21、VGAE 16、GTN 7、GraphSAGE 4。合计超过 107，因为一个方法可同时使用多个变体，不能把这些数字当成互斥方法数。

### 主要挑战与机会

- **图构建敏感性**：邻居数、相似度、阈值和外部网络质量决定传播结构，但综述未提供统一稳健性基准。
- **规模与信息损失**：大图带来内存和训练成本；HVG/高表达基因筛选可降成本，也可能丢失关键生物信号。
- **局部传播与全局依赖**：加深网络扩大感受野，却增加计算并导致 over-smoothing，使不同细胞状态难以区分。
- **外部知识**：PPI、GRN、配体–受体等可增强生物相关性，但也会把数据库偏差带入模型。
- **未来方向**：大规模预训练/基础模型、子细胞分辨率和跨组学整合是作者强调的机会，但本文没有给出统一实验验证。

### 阅读边界

这是一篇叙述性方法综述，不是统一重跑 benchmark 的系统评测。论文列举许多方法并概述其报告表现，但没有一致的数据划分、计算预算、图构建和指标来做公平横评。附录 S1–S15 与补充表在主文中被引用，但当前 PMC Markdown 未包含其正文；因此本工作区不把补充方程、数据集细表或“优于基线”的汇总描述当成本地已核验细节。

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
