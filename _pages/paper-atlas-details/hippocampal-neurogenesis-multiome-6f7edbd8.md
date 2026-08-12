---
layout: default
permalink: /paper-atlas/hippocampal-neurogenesis-multiome-6f7edbd8/
title: "Hippocampal Neurogenesis Multiome"
nav: false
description: "成人海马是否持续产生新神经元长期存在争议。困难不只是“能否检测到某个标记”，而是成人脑中的神经干细胞（NSC）、神经母细胞和未成熟颗粒神经元数量极少，表达谱又分别接近星形胶质细胞、少突胶质细胞或成熟颗粒神经元。死后组织质量、取材是否真正包含齿状回、不同物种标记能否外推以及计算注释方式，都可能改变结论。"
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
      <span>Data Sources &amp; Technologies</span>
      <span>Nature · 2026</span>
    </div>
    <h1>Hippocampal Neurogenesis Multiome</h1>
    <p>Human hippocampal neurogenesis in adulthood, ageing and Alzheimer&#x27;s disease</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-026-10169-4" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 成人海马神经发生 multiome：如何从稀有细胞、染色质和调控网络理解衰老、阿尔茨海默病与认知韧性

### 1. 研究要解决的争议

成人海马是否持续产生新神经元长期存在争议。困难不只是“能否检测到某个标记”，而是成人脑中的神经干细胞（NSC）、神经母细胞和未成熟颗粒神经元数量极少，表达谱又分别接近星形胶质细胞、少突胶质细胞或成熟颗粒神经元。死后组织质量、取材是否真正包含齿状回、不同物种标记能否外推以及计算注释方式，都可能改变结论。

这项研究同时测量单个细胞核的 RNA 和染色质可及性，希望回答四个问题：

1. 成人齿状回能否识别出相互衔接的 NSC–神经母细胞–未成熟神经元状态；
2. 这些状态由哪些转录因子、开放染色质和基因调控网络控制；
3. 健康衰老、临床前中间病理（PCI）和阿尔茨海默病（AD）如何改变神经发生；
4. SuperAger（SA）的卓越记忆是否对应一种不同于普通衰老和 AD 的“韧性”分子网络。

### 2. 队列和数据结构

研究对 38 名供体的死后海马齿状回进行 10x Genomics Multiome：

- 年轻健康成人（YA）：8 人，20–40 岁，85,977 个核；
- 健康老年人（HA）：8 人，73,093 个核；
- 可能从健康衰老向 AD 过渡的 PCI：6 人，58,281 个核；
- AD：10 人，87,209 个核；
- 80 岁以上且延迟回忆达到 50–60 岁常模水平的 SuperAger：6 人，51,437 个核。

合计 355,997 个核。每个核有配对的 RNA 计数和 ATAC 片段，因此可表示为：

$$
\mathcal{D}=\{(\mathbf{x}^{RNA}_i,\mathbf{x}^{ATAC}_i,c_i,s_i)\}_{i=1}^{N},
$$

其中 $c_i$ 是细胞类型，$s_i$ 是供体与诊断组。统计独立重复是 38 名供体，不是 355,997 个细胞核。细胞数差异和分子差异都必须在供体层面处理，否则会产生伪重复。

组织来自快速尸检，死后间隔通常小于 12 小时；研究者从冷冻组织块中激光或解剖富集齿状回。死后 multiome 可以读取稳定的核转录和染色质状态，但不能实时观察细胞分裂、新生神经元迁移或并入回路。

### 3. 原始 multiome 处理和质量控制

每个样本加载约 16,000 个细胞核。Cell Ranger ARC 同时生成 gene × nucleus 与 peak × nucleus 矩阵，再用 `aggr` 合并捕获。作者去除：

- 线粒体表达 >10%；
- 表达基因 <1,000；
- RNA UMI <2,000；
- ATAC peaks <200；
- ATAC counts <500。

Scrublet 与 DoubletDetection 的并集用于去除双细胞。RNA 侧用 Seurat `NormalizeData`，选择 6,000 个高变基因，计算 200 个主成分，经 JackStraw 和热图检查后保留 125 个 PC；Louvain 在多个 resolution 下比较，最终使用 resolution 1。

这些阈值保证分析对象同时有可用 RNA 和 ATAC 信号，但对稀有、低 RNA 的真实细胞可能更苛刻。先在 RNA 空间聚类也意味着细胞身份主要由转录组定义，ATAC 更多用于正交支持和调控解释。

### 4. 为什么稀有神经发生细胞不能靠一个 marker 注释

#### 4.1 scVI/scANVI 标签迁移

作者把人发育前脑和成人海马参考数据与本研究整合。scVI 用生成模型学习批次校正的低维表示，scANVI 再利用参考标签对查询核做半监督分类。初步得到星形胶质、神经母细胞、发育未成熟神经元、CA 神经元、抑制神经元、成熟颗粒细胞、少突谱系和其他主要细胞。

标签迁移是候选生成器，不是最终真值。参考标注错误、不同年龄或脑区的 domain shift，以及稀有状态与大群体相似，都可能造成错误匹配。

#### 4.2 神经母细胞与未成熟神经元

作者对初步“发育未成熟”细胞再次亚聚类，并用 CytoTrace 估计相对成熟度。9 个亚群中，0、2、6 归为神经母细胞，其余归为未成熟神经元。神经母细胞在 UMAP 上接近成熟少突胶质细胞，因此作者检查 MAG、MOG 等髓鞘基因，比较了 4,166 个 DEGs 和 169 条通路；其中 80 条涉及轴突、树突、突触与神经递质功能，支持两者并非同一群体。

#### 4.3 NSC 与星形胶质细胞

NSC 与星形胶质细胞最难区分。作者把 NSC/astrocyte 群与神经母细胞、未成熟和成熟颗粒神经元共同做 scVelo RNA velocity。根据 latent time，选择位于其余星形胶质和神经发生细胞之间、分化时间更早的亚群为 NSC。

RNA velocity 使用未剪接与已剪接转录本比例估计局部状态变化：

$$
\frac{du}{dt}=\alpha-\beta u,\qquad
\frac{ds}{dt}=\beta u-\gamma s,
$$

其中 $u$ 与 $s$ 分别是 unspliced 和 spliced RNA。latent time 来自动力学模型在状态图上的相对排序，不是核的真实出生时间。

### 5. NSC/神经母细胞身份的多层验证

论文没有只依赖 velocity。作者还进行了：

1. NSC 相对星形胶质的 766 个 DEGs 和 65 条通路，其中 25 条与轴突发育、轴突导向、生长锥、树突棘等相关；
2. NSC 中 multilineage potential 区域更开放，而神经母细胞和未成熟神经元中神经成熟 proxy 的染色质更开放；
3. NSC 与星形胶质在 ATAC UMAP 和 SCENIC+ eRegulon 空间中分离；
4. 与另一份成人海马研究的 NSC/神经母细胞 signature 显著重叠；
5. 构建 131 基因 NSC score，在外部海马 NSC 中高、星形胶质中低；
6. 在预期无明显神经发生的前额叶和多个脑区数据中做负向检验，并要求同时存在 NSC、未成熟神经元和成熟颗粒神经元端点。

签名分数本质上是标准化表达均值：

$$
S_i^{NSC}=\frac{1}{|G|}\sum_{g\in G}z_{ig}.
$$

这些证据显著降低单一注释方法的风险，但仍不能等价于 BrdU/碳年代测定或活体谱系追踪。论文支持“存在与神经发生连续谱一致的分子状态”，而不是直接计数某时间窗口内新生神经元的生成率。

### 6. 青年成人中的神经发生分子轨迹

YA 队列用于建立相对不受衰老和病理影响的基线。结果支持：

$$
\mathrm{NSC}\rightarrow\mathrm{neuroblast}
\rightarrow\mathrm{immature\ neuron}
\rightarrow\mathrm{mature\ granule\ neuron}.
$$

NSC 的 top DEG/DAR 随神经母细胞和未成熟神经元逐步下降；未成熟神经元 signature 则从 NSC 的低水平，经神经母细胞过渡到高水平。NSC 富集 $\beta$-catenin、细胞极性和干性相关程序；未成熟神经元富集突触功能和可塑性。

motif 层也发生转换：NSC 开放区域富 STAT3/4/5、PLAGL1、NFIB；未成熟神经元富 RFX2、FOS–JUN、NFE2、MEIS2、PBX2。motif enrichment 表示含某序列模式的 peaks 更常开放，不证明对应 TF 蛋白实际结合或具有唯一作用。

### 7. 两套 GRN：TF–peak–gene trio 与 SCENIC+

#### 7.1 TF–peak–gene trio

作者去除在 <10% 细胞表达的基因和 <2% 细胞开放的 peak。每个 peak 连接到 200 kb 内或基因体重叠的基因；FIMO 在 JASPAR motif 上用 $P<10^{-5}$ 筛 TF–peak 候选。为降低稀疏性，RNA/peak 信号在每个细胞 20 个最近邻中平均。

对 TF 基因 $T$、peak $P$ 和 target $G$ 计算三类相关，交互强度是绝对相关的几何平均，并由 TF–target 的符号决定激活或抑制方向：

$$
S_{TPG}=\operatorname{sign}(r_{TG})
\left(|r_{TP}|\,|r_{PG}|\,|r_{TG}|\right)^{1/3}.
$$

TF–peak 相关小于 0 被设为 0。该分数组合 motif、距离与相关性，可用于排序候选调控边，但 200 kb 邻近不是物理 enhancer–promoter 接触，相关也不是因果。

#### 7.2 SCENIC+ eRegulon

SCENIC+ 使用 ATAC topics、DARs、motif 和 RNA 共变推断 TF–enhancer–gene eRegulon，并用 gene/region AUC 表示单细胞活性。eRegulon UMAP 与 diffusion map 再现 NSC–神经母细胞–未成熟神经元连续性。

YA 中 NSC 突出的 eRegulon 包括 RORA/RORB、SMAD1、SOX6、PRRX1、NFIA；神经母细胞有 NEUROD1、FEZF2、EGR1/3；未成熟神经元有 TFDP1、ONECUT2、E2F3 等。两套 GRN 互补：trio 分数强调具体三元关系，SCENIC+ 强调 enhancer-driven regulon 活性。二者都依赖统计推断，并非 TF 扰动实验。

### 8. 诊断差异为什么要在供体层面做 pseudobulk

作者在每个细胞类型和每位供体内汇总 gene 或 peak counts，去除少于 25% 样本表达或总计数 <50 的特征，再用 edgeR `exactTest` 比较组别，FDR <0.05 判显著。概念上：

$$
Y_{gsc}=\sum_{i\in(s,c)}y_{gi},qquad
Y_{gsc}\sim NB(\mu_{gsc},\phi_g).
$$

这样每位供体才是重复，避免把同一脑中的数千细胞当作独立样本。细胞丰度也先按样本计数，用 edgeR（不做 TMM）或广义线性模型分析诊断和连续认知指标。

样本量仍小：每组 6–10 人，且死后间隔、组织质量、性别、年龄、病理负担和细胞捕获率可造成变异。特别是稀有神经发生细胞，单个供体的高/低捕获会强烈影响组均值。

### 9. PCI 与 AD：DAR 多于 DEG 的含义

与 HA 相比，PCI 和 AD 的 NSC 数量升高；AD 的神经母细胞和未成熟神经元减少。跨年龄和诊断比较中，DAR 数量显著多于 DEG，尤其神经母细胞和未成熟神经元中的开放染色质在 PCI 已下降、AD 中进一步下降。相关 targets 富集神经结构、突触可塑性、神经发育和神经传递。

作者据此提出染色质可及性可能是认知恶化的更早、强烈分子特征。合理表述是“PCI 中已观察到与 AD 同方向的 DAR，而相应 RNA 变化较少”。不能仅由横断面组别比较证明染色质变化在同一人中时间上先于转录变化。DAR 多还可能受 ATAC 动态范围、peak 数、统计功效和 RNA 降解差异影响；论文讨论也承认 mRNA 对采集过程可能更敏感。

motif 分析显示认知恶化相关开放区中 zinc-finger motif 上升、RFX family motif 下降。SCENIC+ 则发现 HA 驱动神经发生的多个 eRegulon 在 PCI/AD 中下降，而另一套 NSC-like 网络在 PCI 及 AD 增强。AD 中 NSC 数量上升并不自动表示有效神经发生增强；它也可能代表停滞、补偿或无法完成分化。

### 10. SuperAger “韧性分数”如何构造

SA 中未成熟神经元数相对 AD 显著升高；一个供体是明显高值，去除后仍约 2.5 倍，但对 HA/YA/PCI 的约 2 倍差异未达显著。SA 相比其他组在未成熟神经元有 7,058 个上调 DAR、神经母细胞有 674 个，DEG 少得多。

韧性分析要求某特征在 AD–YA、AD–HA 和 SA–AD 三个比较中方向一致地体现“YA/HA/SA 保持而 AD 偏离”。每个比较先构造：

$$
u_k=\log_2FC_k\times[-\log_{10}(q_k)],
$$

再以三者绝对值的几何平均作为强度：

$$
R=\left(|u_1u_2u_3|\right)^{1/3},
$$

仅保留方向符合韧性模式的特征。

神经母细胞和未成熟神经元中，大量基因/peaks 在 YA、HA、SA 相对稳定，在 AD 下降；开放染色质模式最明显。BDNF、CALB1 以及神经分化 zinc-finger motif 是候选。SA 与 YA 共享部分 eRegulon，也具有独特网络。

“韧性 signature”是观察性对比定义，不证明这些特征产生卓越记忆。SA 样本仅 6 人、细胞丰度有离群值，且 SA 的年龄、病理和选择标准与其他组并非完全可交换。韧性分数还把效应大小与显著性相乘，容易受每组方差和样本量影响。

### 11. HIPPI：从全海马网络理解成功与不成功衰老

HIPPI（hippocampal cognitive integrity）寻找 SA–HA 与 PCI–HA/PCI–YA 方向相反的基因或 peaks，且至少一个比较 $q<0.2$。得到 1,001 个 DEGs 和 579 个 DARs：DEG 主要在 CA1 神经元，DAR 主要在星形胶质细胞。

CA1 候选包括 GABRB1、NRGN 等神经传递/可塑性基因；astrocyte DAR 富集 FOS–JUN bZIP motif。通路涉及突触、核糖体、能量代谢、线粒体、内体和溶酶体。CellChat 在 astrocyte、CA neurons 与合并的神经发生细胞间推断信号，突出 neurexin–neuroligin、NCAM、contactin、APP–SORL1 和谷氨酸受体相关交互。SA/HA 中较强、PCI/AD 中较弱。

CellChat 根据配体、受体表达和数据库规则计算通信概率：

$$
P_{A\rightarrow B}^{(l,r)}=f(\bar{x}_{A,l},\bar{x}_{B,r},\text{database}).
$$

该数据没有空间坐标，海马组织已解离，因此这些是细胞类型级共表达候选，不表示两个细胞原位邻近或发生了直接突触/旁分泌作用。

HIPPI 的 $q<0.2$ 是探索性阈值，且“方向相反”筛选可能放大噪声。它更适合生成成功认知衰老的候选网络，而非临床 biomarker 或干预靶点结论。

### 12. 图 1–5 应怎样连起来读

- **图 1**：在 YA 中定义 NSC–神经母细胞–未成熟神经元的 DEG、DAR、motif 和 eRegulon 基线。
- **图 2**：比较 YA/HA/PCI/AD/SA，显示认知恶化的 DAR 数量和方向比 DEG 更突出，PCI 已有部分 AD-like 染色质变化。
- **图 3**：把差异特征组织成 eRegulon 网络，展示 HA、PCI、AD 和细胞类型的不同调控程序。
- **图 4**：用方向约束定义 SA 韧性基因和 peaks，发现神经母细胞/未成熟神经元开放染色质的保持。
- **图 5**：跳出稀有神经发生细胞，指出 CA1 表达、astrocyte 染色质及与神经发生细胞的候选通信共同关联认知完整性。

这是一条从“定义正常轨迹”到“诊断扰动”再到“韧性与全海马网络”的逻辑，而不是同一人的病程时间序列。

### 13. 可复现性与代码边界

工作区没有论文配套代码仓库，论文只公开 GEO `GSE268609` 的原始和处理数据。Methods 提供软件、阈值和算法描述，但没有可直接执行的 notebooks、环境锁定文件、SCENIC+ region sets、trio interaction tables 生成脚本、韧性/HIPPI 筛选代码或 CellChat workflow。

因此：

- **论文中明确**：QC、Seurat/scVI/scANVI/scVelo/CytoTrace、peak recalling、edgeR pseudobulk、FIMO motif、trio score、SCENIC+、CellChat、韧性和 HIPPI 规则；
- **本地代码证据**：Not found；`doc_code.md` 合理跳过；
- **可重新分析**：理论上可从 GEO 下载数据按 Methods 重建，但需自行实现大量参数、输入转换和统计流程；
- **无法由代码直接验证**：本文工作区内所有具体 cell counts、DAR/DEG/eRegulon 与 interaction 结果只能由论文、源数据和补充表核对。

### 14. 结论与不可越过的边界

研究提供了支持成人海马存在神经发生相关连续分子状态的多组学证据，并显示认知恶化尤其对应开放染色质和调控网络改变；SA 则保留或重组部分神经发生网络。最有说服力的是标签迁移、velocity、RNA/ATAC、外部海马复现和非神经发生脑区负向检验相互补充。

仍不能由此直接证明某个核是近期出生的神经元、NSC 实际分裂率、PCI 必然进展为 AD、DAR 在个体内先于 DEG、SA signature 导致卓越记忆，或 CellChat 边代表真实原位通信。死后横断面、小供体数、稀有细胞捕获、队列差异与缺少公开代码，是解释和复现的主要限制。

### 15. 源证据导航

- 论文：`paper source/paper/auto/paper.md`
- 报告补充：`output_paper_supp_md/paper_supp1/auto/paper_supp1.md`
- 主图：`paper source/paper/auto/images/`
- 方法细节：`doc_method.md`
- 逐图分析：`figure_analysis.md`
- 概览与复现说明：`summary.md`
- 分析笔记：`claude_notes.md`

本文件解释论文的计算链与证据边界。最终事实应以论文、补充表和 GEO 数据为准；由于本地没有代码，任何重分析都需要重新实现并明确记录参数。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Human Hippocampal Neurogenesis in Adulthood, Ageing and Alzheimer's Disease

### Paper Information

- **Authors**: Ahmed Disouky, Mark A. Sanborn, K. R. Sabitha, et al.
- **Journal**: Nature (2026)
- **DOI**: 10.1038/s41586-026-10169-4
- **Data**: GEO GSE268609
- **Code**: No custom repository (uses standard bioinformatics tools)

---

### Motivation & Novelty

#### The Problem

Adult hippocampal neurogenesis — the generation of new neurons from neural stem cells (NSCs) in the dentate gyrus — has been one of the most contentious topics in neuroscience. While rodent neurogenesis is well established and linked to learning and memory, evidence in humans has been contradictory:

- **Pro-neurogenesis**: Boldrini et al. (*Cell Stem Cell*, 2018) reported neurogenesis persists throughout life; Moreno-Jiménez et al. (*Nature Medicine*, 2019) found abundant immature neurons that decline in AD
- **Anti-neurogenesis**: Sorrells et al. (*Nature*, 2018) argued neurogenesis drops to undetectable levels in children
- **Recent resolution**: Dumitru et al. (*Science*, 2025) identified proliferating neural progenitors in adult human hippocampus using single-cell sequencing

Even accepting neurogenesis exists, critical gaps remained: the **epigenetic regulation** of human neurogenesis was unknown, the **gene regulatory networks** governing the process were undefined, the relationship between neurogenesis and **cognitive function** was unclear, and the molecular signature of neurogenesis in **preclinical Alzheimer's** and **exceptional cognitive aging** (SuperAgers) was uncharacterized.

#### What's New

This study provides the first **multi-omic** (snRNA-seq + snATAC-seq) atlas of human hippocampal neurogenesis across the cognitive spectrum:

1. **First epigenetic characterization**: identifies chromatin accessibility landscapes of NSCs, neuroblasts, and immature neurons
2. **First GRN map of human neurogenesis**: uses SCENIC+ (Bravo González-Blas et al., *Nature Methods*, 2023) to infer enhancer-driven regulatory networks (eRegulons) governing neurogenic cell types
3. **Discovery that DARs > DEGs**: chromatin accessibility differences capture more cognitive aging signatures than gene expression differences — suggesting epigenetic changes are more fundamental
4. **PCI as a molecular transitional state**: identifies chromatin changes in preclinical AD that precede transcriptomic alterations, offering potential early biomarkers
5. **SuperAger resilience signature**: reveals that SA neurogenesis shares eRegulon networks with young adults while exhibiting unique additions (PROX1, ZNF423, ZIC1), with a striking absence of the NEUROD1-driven differentiation program in neuroblasts
6. **HIPPI network**: identifies that CA1 neuron gene expression and astrocyte chromatin accessibility, particularly glutamatergic pathways (NRXN1-NLGN, GRIA, GRIK), distinguish successful from unsuccessful cognitive aging

---

### Method Overview

#### Data Generation
- **10x Genomics Multiome** (snRNA-seq + snATAC-seq) from the same nuclei
- 355,997 nuclei from 38 post-mortem hippocampi across 5 cognitive cohorts: Young Adults (YA, n=8), Healthy Agers (HA, n=8), Preclinical Intermediate (PCI, n=6), Alzheimer's Disease (AD, n=10), SuperAgers (SA, n=6)
- Dentate gyrus isolated by laser dissection; post-mortem interval <12h

#### Computational Pipeline
1. **Preprocessing**: CellRanger-arc → Seurat (6,000 HVGs, 125 PCs, Louvain res=1)
2. **Cell annotation**: scANVI label transfer from developmental forebrain + adult hippocampus references → 12 cell types
3. **NSC identification**: RNA velocity (scVelo) latent time on astrocyte subcluster → developmental trajectory: NSC → neuroblast → immature neuron → mature granule cell
4. **Differential analysis**: Pseudo-bulk edgeR for DEGs/DARs between diagnosis groups
5. **GRN inference**: TF-peak-gene trios (200kb window) + SCENIC+ eRegulons
6. **Resilience/HIPPI scoring**: Custom metrics comparing AD to YA/HA/SA patterns
7. **Cell-cell interaction**: CellChat for ligand-receptor communication between neurogenic, CA1, and astrocyte populations

See doc_method.md for detailed step-by-step pipeline documentation.

---

### Evaluation

#### Datasets
- **Primary**: 38 human hippocampi (GEO GSE268609)
- **Validation references**: Dumitru et al. (*Science*, 2025), Siletti et al. (*Science*, 2023), Liu et al. (*Cell*, 2025), Mathys et al. (*Cell*, 2023), Habib et al. (*Science*, 2016), Smajić et al. (*Brain*, 2022)

#### Key Results

##### 1. Neurogenic Trajectory (Fig. 1)
- 12 cell types identified including NSCs, neuroblasts, immature neurons
- NSCs show high stemness chromatin accessibility, low neuronal markers
- Developmental pathway: $\beta$-catenin/STAT TFs (NSCs) → NEUROD1/FEZF2/EGR (neuroblasts) → RFX2/FOS-JUN/MEIS2 (immature neurons)
- Distinct eRegulon networks per cell type (SCENIC+)

##### 2. Epigenetic > Transcriptomic (Fig. 2)
- Only 172 DEGs distinguish AD vs HA in NSCs; DARs substantially more numerous across all neurogenic types
- DARs show clear opposite directionality in AD vs other conditions
- PCI-specific DARs (downregulated in neuroblasts/immature neurons) predict AD progression — pathways: synaptic plasticity, neurotransmission

##### 3. GRN Alterations in Cognitive Decline (Fig. 3)
- NSCs form distinct cluster in eRegulon-based UMAP
- 5/6 top HA eRegulons downregulated in PCI/AD; replaced by NSC-associated eRegulons (ZNF98, SMAD1, RORB, PRRX1, NFIA)
- This may explain increased NSC numbers in AD (NFIA repressor downregulated)
- SA exhibits unique eRegulon signature distinct from all other groups

##### 4. SuperAger Resilience (Fig. 4)
- 2.5× increase in immature neurons in SA (vs other groups; significant vs AD at q=0.0002)
- 7,058 DARs upregulated in SA immature neurons; few DEGs
- BDNF and CALB1 upregulated; NEUROD6 and NECTIN3 downregulated
- Resilience genes: stable in YA/HA/SA, substantially downregulated in AD (especially in chromatin)
- SA shares YA eRegulon network with unique additions: PROX1 (immature neurons), ZNF423/ZIC1/SOX2/NFE2L2 (NSCs)
- **Critical finding**: SA neuroblasts lack the coordinated NEUROD1/FEZF2/EGR differentiation program seen in YA

##### 5. Successful vs Unsuccessful Aging (Fig. 5)
- HIPPI analysis: 1,001 DEGs (mostly in CA1 neurons) and 579 DARs (mostly in astrocytes) distinguish aging trajectories
- CA1 neurons: GABRB1, NRGN, KCNF1, APOE, EGR1, GRASP, glutamate receptors
- Astrocyte DARs: FOS-JUN bZIP motifs enriched
- CellChat: NRXN1-NLGN, NRXN1-CLSTN1/2, NCAM1, APP-SORL1, glutamatergic receptor pathways enhanced in SA/HA, attenuated in PCI/AD

#### Validation Strategy
- Multi-level: machine learning annotation + RNA velocity + chromatin accessibility + external dataset comparison
- NSC signature validated against 6 independent datasets (positive and negative controls)
- Neuroblast vs oligodendrocyte distinction: 4,166 DEGs, 169 pathways, RNA velocity latent time

---

### Reproducibility

#### Rating: 3/5

**Justification**:

| Aspect | Status |
|---|---|
| Raw data availability | ✓ GEO GSE268609 |
| Software versions specified | ✓ All major tools with versions |
| Custom code repository | ✗ None provided |
| Parameter documentation | ~ Mostly complete, some defaults assumed |
| Reference datasets accessible | ✓ Published datasets |
| Computational resources needed | High (≥128 GB RAM, GPU for scVI) |

#### Strengths
- **Unprecedented multi-omic atlas**: First combined snRNA-seq + snATAC-seq of human hippocampal neurogenesis across the cognitive aging spectrum
- **Rigorous cell annotation**: Multiple orthogonal validation strategies (ML, velocity, chromatin, external datasets, negative controls)
- **Clinical cohort design**: Five well-characterized cognitive groups including the rare SuperAger cohort
- **Comprehensive GRN analysis**: Both TF-peak-gene trios and SCENIC+ eRegulons provide complementary regulatory network views
- **Discovery of chromatin > transcriptomic principle**: Potentially transformative for how the field studies cognitive aging

#### Weaknesses
- **No custom code**: Analysis uses standard tools, but the specific pipeline (QC thresholds, parameter choices, custom scoring) is not provided as reproducible code
- **Small sample size**: n=6 for PCI and SA cohorts; high inter-individual variability acknowledged
- **Post-mortem tissue**: Inherent limitations of working with post-mortem samples (mRNA stability, cell death artifacts)
- **SA immature neuron increase**: While 2.5-fold even excluding outlier, SA vs HA/YA comparisons were not significant — only SA vs AD reached significance
- **Causality gap**: All findings are correlational; the study cannot establish whether neurogenesis differences cause or result from cognitive differences
- **Limited supplementary data**: Supplementary tables referenced but not all bioinformatic details provided (e.g., exact SCENIC+ configuration beyond what's in Methods)

#### Practical Notes
- Requires substantial computational resources for full replication (SCENIC+ alone can take days on full dataset)
- Seurat v4.0.5 (now several versions behind) — some API changes in newer versions
- edgeR pseudo-bulk is the recommended approach for multi-sample scRNA-seq DE (vs cell-level tests)
- The 125 PCs is unusually high — suggests complex biological heterogeneity in hippocampal samples

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
