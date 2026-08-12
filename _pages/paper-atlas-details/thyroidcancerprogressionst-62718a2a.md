---
layout: default
permalink: /paper-atlas/thyroidcancerprogressionst-62718a2a/
title: "ThyroidCancerProgressionST"
nav: false
description: "这项研究要回答的不是“甲状腺癌有哪些差异基因”，而是这些分子与细胞状态在肿瘤组织中位于哪里，以及从癌旁组织（PT）、乳头状甲状腺癌（PTC）、局部晚期乳头状甲状腺癌（LPTC）到未分化甲状腺癌（ATC）时，肿瘤细胞、成纤维细胞和免疫细胞的空间关系如何改变。 作者对 17 个组织样本做 10x Visium 空间转录组：4 个 PT、5 个 PTC、4 个 LPTC、4 个 ATC，共得到 57,997 个空间 spot。"
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
      <span>Atlases &amp; Resources</span>
      <span>Cell Reports Medicine · 2025</span>
    </div>
    <h1>ThyroidCancerProgressionST</h1>
    <p>A spatially resolved transcriptome landscape during thyroid cancer progression</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.xcrm.2025.102043" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ThyroidCancerProgressionST：沿甲状腺癌进展重建空间细胞状态、侵袭边缘与细胞通信

### 1. 研究问题与设计

这项研究要回答的不是“甲状腺癌有哪些差异基因”，而是这些分子与细胞状态在肿瘤组织中位于哪里，以及从癌旁组织（PT）、乳头状甲状腺癌（PTC）、局部晚期乳头状甲状腺癌（LPTC）到未分化甲状腺癌（ATC）时，肿瘤细胞、成纤维细胞和免疫细胞的空间关系如何改变。

作者对 17 个组织样本做 10x Visium 空间转录组：4 个 PT、5 个 PTC、4 个 LPTC、4 个 ATC，共得到 57,997 个空间 spot。其中 PT、PTC 和 LPTC 各有 3 个样本同时做 scRNA-seq；为补足 ATC 和扩大参考，作者还整合两个公开单细胞数据集，最终得到 253,822 个高质量细胞。空间数据保留组织坐标，单细胞数据提供较精细的细胞类型和亚群表达参考，两者经 RCTD 连接。

整条方法链可概括为：

1. 在 Visium 上建立跨四个阶段的空间表达图谱；
2. 整合自有和公开 scRNA-seq，定义细胞类型与亚群；
3. 用 RCTD 将混合 spot 分解为细胞类型比例；
4. 聚焦 16 个甲状腺滤泡细胞亚群，计算分化、BRAF 和 RAS 程序；
5. 用 Monocle3 伪时间提出从正常样状态到晚期癌状态的候选顺序；
6. 由病理医师标注肿瘤侵袭前缘，比较边缘的细胞组成和表达程序；
7. 用相邻 spot 的配体—受体共表达筛选空间通信，并以多重免疫荧光验证 SERPINE1–PLAUR 轴。

这是跨患者、横断面的阶段比较，不是同一患者从 PTC 连续随访到 ATC。因此“进展轨迹”和“演化”主要是基于状态相似性与阶段关联的推断。

### 2. 空间转录组如何形成可分析矩阵

组织切片经 H&E 成像后覆盖到 Visium 捕获区。每个 spot 上的空间条形码记录坐标，UMI 记录捕获分子。Space Ranger 1.3.1 将 reads 比对到 hg38，生成基因 × spot 计数矩阵。论文过滤少于 200 个表达基因的 spot，并要求纳入基因至少有 10 个计数、在至少 3 个 spot 中被检测。

随后使用 Seurat 4.3.0 的 SCTransform 归一化，再以 30 个主成分进行邻居图、聚类和 UMAP。空间 spot 的向量可写成：

$$
\mathbf{y}_s=(y_{1s},y_{2s},\ldots,y_{Gs}),
$$

其中 $y_{gs}$ 是基因 $g$ 在 spot $s$ 的计数。SCTransform 试图从测序深度等技术因素中分离稳定的基因变异，但不会消除组织质量、肿瘤含量和样本来源的所有差异。

17 个样本被归为 8 个 ST cluster。PT 主要落在 cluster 3，PTC 主要为 cluster 1，ATC 大量落在 cluster 2；LPTC 在 cluster 1 与 2 之间转换，支持它在分子景观上具有中间特征。作者报告 PT 富集 *TFF3/TG/TPO*，PTC 富集 *SLC34A2/SERPINA1/CTSH*，LPTC 富集 *CXCL14/PCSK1N/NMB*，ATC 富集 *SAA1/C1QA/TFPI2*。ATC 还显示更强的 MYC targets、G2M checkpoint 和 E2F targets 等增殖程序。

这些是阶段相关表达模式。由于每组仅 4–5 个空间样本，不能把 57,997 个 spot 当作 57,997 个独立患者。

### 3. 单细胞参考：定义细胞类型和细分状态

自有 scRNA-seq 和 GSE184362、GSE148673 经 Cell Ranger/STAR 处理。作者去除基因数 <200、UMI <1,000 或线粒体 UMI >20% 的细胞，并用 DoubletFinder 去除双细胞。Seurat 选择 2,000 个高变基因，以 30 个主成分降维，Harmony 校正样本与数据集批次，随后构建邻居图、聚类并依据已知标记人工注释。

整合参考包含 7 个主要群体：T 细胞、甲状腺滤泡细胞、B 细胞、髓系细胞、成纤维细胞、内皮细胞和 NK 细胞。再在每类内部聚类，得到甲状腺细胞、成纤维细胞、巨噬细胞等亚群。论文采用 fold change >1.5 或 <0.67 且 BH 校正 $p<0.05$ 作为亚群差异基因阈值。

Harmony 的作用是降低技术批次差异，但如果疾病阶段与数据来源高度重合，校正可能同时削弱真实疾病信号，或保留来源特异信号。ATC 单细胞参考主要依赖外部数据，这一来源不对称应视为解释边界。

### 4. RCTD：把一个混合 spot 分解为细胞组成

Visium spot 往往覆盖多个细胞。RCTD 假设 spot 表达是单细胞参考中各细胞类型平均表达的混合：

$$
y_{gs}\sim \mathrm{Poisson}\left(d_s\sum_{k=1}^{K}w_{sk}\mu_{gk}\right),
\qquad w_{sk}\ge 0,
$$

其中 $d_s$ 表示 spot 测序深度，$\mu_{gk}$ 是参考中基因 $g$ 在类型 $k$ 的表达，$w_{sk}$ 是该类型对 spot 的贡献。代码 `2.0.RCTD.R` 从 Seurat 对象提取坐标和 raw counts，构造 `SpatialRNA` 与 `Reference`，并以 `doublet_mode='full'` 对每个样本运行 RCTD，最后标准化权重。

结果显示 PT 和 PTC 的 spot 主要由甲状腺细胞主导；LPTC 的甲状腺细胞下降而成纤维细胞增加；ATC 同时具有更多成纤维细胞、髓系和 NK 成分，呈现更强的免疫与基质浸润。图 2 把组织学、ST cluster、细胞签名和 RCTD 比例并列展示，使“空间域”和“细胞组成”不被混为一谈。

$w_{sk}$ 是模型估计比例，不是对每个细胞的直接显微计数。参考中缺少某种状态、不同平台的捕获偏差、共线的细胞类型表达和低 UMI spot 都会改变去卷积结果。作者与 cell2location、Tangram、DestVI、CARD、CytoSPACE、Redeconve 做了总体比较，但公开脚本读取预计算结果，不能从本地代码独立重建所有比较方法。

### 5. 16 个甲状腺细胞亚群及三类模块分数

作者把甲状腺细胞划分为 ThyC-1 至 ThyC-16。图 3 同时展示亚群 UMAP、标记基因、阶段组成、空间位置和三种模块分数。

模块分数的基本形式是目标基因集平均表达减去匹配的背景基因平均表达：

$$
S_i(G)=\frac{1}{|G|}\sum_{g\in G}x_{ig}
-\frac{1}{|C(G)|}\sum_{c\in C(G)}x_{ic}.
$$

TDS 使用 16 个甲状腺功能基因，包括 *TG, TPO, TSHR, PAX8, NKX2-1, SLC5A5* 等；分数越高表示保留更多分化功能。BRAF 与 RAS score 使用 TCGA 中对应突变样本高表达的程序，表示转录程序相似性，并不等同于该细胞实际携带 BRAF 或 RAS 突变。

ThyC-2 和 ThyC-6 主要来自 PT，TDS 高、BRAF score 低、RAS score 高；ATC 中占比最大的 ThyC-4 则 TDS 低、BRAF score 高、RAS score 低。ThyC-1、4、8、10、12 富集多种癌症 hallmark。由此作者提出从分化良好的正常样状态向低分化恶性状态变化的图景。

代码 `4.0.tds_ras_braf_score.R` 明确列出 16 个 TDS 基因并调用 `AddModuleScore`，再读取 BRAF/RAS 基因列表计算分数。公开快照不包含 `BRAF.txt` 和 `RAS.txt` 的实际内容，因此这两组 signature 无法仅凭仓库完全审计。

### 6. Monocle3 伪时间：状态排序不是谱系追踪

Monocle3 在低维表达空间中学习主图，再从指定根细胞沿图计算距离。作者把 PT 来源甲状腺细胞设为根，得到每个细胞的伪时间 $\tau_i$。概念上：

$$
\tau_i=d_{\mathcal{G}}(r,i),
$$

其中 $d_{\mathcal{G}}$ 是细胞状态主图上的路径距离，$r$ 是 PT 根状态。

ThyC-2、6、14、15 位于低伪时间，ThyC-1、4、10、12 位于高伪时间。伪时间与 TDS、RAS score 负相关，与 BRAF score 正相关。作者再用 silhouette width 在 1–10 个簇中选出 3 个 meta-cluster：meta-cluster 1 为正常/癌前样，meta-cluster 3 为癌样，meta-cluster 2 为晚期癌样。meta-cluster 1 高表达 *TG/IYD*，meta-cluster 2 高表达 HLA 基因，meta-cluster 3 高表达 *APOE/APOC1*。

`5.0.trajectoryInference.R` 直接从保存的 Monocle3 对象抽取 pseudotime 并按亚群画箱线图；真正的 Monocle3 建图和根节点选择发生在仓库未提供的上游对象生成步骤。因此本地代码对“如何生成轨迹”是 Partial，而对“如何读取和展示伪时间”是 Exact。

伪时间并不观察 DNA 克隆谱系，也没有纵向采样。PT、PTC、LPTC、ATC 可能来自不同分子路径，ATC 也不一定都由研究中的 PTC 状态线性演化而来。因此它应读作“与进展一致的候选状态轴”，不是证明细胞真实祖先—后代关系。

### 7. 把细胞状态重新放回空间邻域

作者利用 Visium 六边形格点，把含某一甲状腺 meta-cluster 的核心 spot 周围一圈 spot 定义为邻域，然后汇总周围成纤维细胞和免疫亚群的 RCTD 比例。若 $\mathcal{N}(s)$ 是核心 spot 的相邻 spot，则某类细胞 $k$ 的邻域丰度可表示为：

$$
A_{sk}=\frac{1}{|\mathcal{N}(s)|}\sum_{j\in\mathcal{N}(s)}w_{jk}.
$$

结果显示三类甲状腺 meta-cluster 周围普遍有成纤维细胞。PTC/LPTC 常见 Fib-3；ATC 中 meta-cluster 3 周围富集 Fib-10。免疫组成也随阶段和状态变化：正常/癌前样 meta-cluster 1 周围相对多 B/T 细胞，而癌样 meta-cluster 3 周围更多巨噬细胞。这里的“周围”是固定 Visium 邻接尺度，不等同于细胞直接接触，也不能区分组织结构造成的共同定位和真正相互作用。

### 8. 肿瘤 leading edge：由病理边界定义分析区域

肿瘤侵袭前缘不是算法自动推断。经验丰富的病理医师在 H&E 图像上反复标注正常—肿瘤边界，与标记线对应的空间 spot 被定义为 leading-edge spot。图 5 把病理边界、去卷积组成、亚群富集、差异表达和 GSEA 放在同一空间区域比较。

PTC 和 LPTC 前缘超过一半成分为甲状腺细胞；ATC 前缘中甲状腺细胞约 33.06%，成纤维细胞约 32.42%，且 NK 和髓系比例也更高。Fib-3 和 Mac-5 在多个阶段前缘富集，Mac-1 特异富集于 ATC 前缘。ATC 的成纤维细胞标记 *ACTA2, COL1A1, COL1A2, COL3A1, TAGLN* 更高。

论文使用供体/样本层面的 pseudobulk 和 edgeR likelihood ratio test 比较前缘与非前缘，避免直接把大量 spot 视为独立重复。LPTC 前缘具有最多差异基因，并显示 IL-2/STAT5、TNF-α/NF-κB 和 KRAS 等信号下降。公开代码中没有找到病理标线转为 spot 标签的实现，也没有完整的 edgeR pseudobulk 脚本；这一环节依赖预先生成的注释和结果对象，属于 Not found/Partial。

病理人工标注具有临床可解释性，但边界宽度、观察者差异和 spot 直径会改变“前缘”包含的细胞。前缘富集不能单独证明这些细胞推动侵袭。

### 9. 空间配体—受体分析

作者先从 CellPhoneDB 4.1.0 与 NicheNet 获得配体—受体列表，仅保留相对 PT 在 PTC、LPTC 或 ATC 中差异表达的分子。对每个配体 $l$，在表达它的核心 spot 中取表达值；对其受体 $r$，计算六个相邻 spot 的平均表达，再在同一癌症阶段计算 Spearman 相关：

$$
\rho_{lr}^{(c)}=\mathrm{cor}_{\mathrm{Spearman}}
\left(x_{l,s},\frac{1}{|\mathcal{N}(s)|}\sum_{j\in\mathcal{N}(s)}x_{r,j}\right).
$$

`6.0.CellCellInteraction.R` 的代码与这一描述直接对应：利用 Visium 行列坐标选择六邻域，计算受体邻域均值，按癌症阶段做 `rcorr(..., type='spearman')`，BH 校正后保留 `Padj < 0.05 & cor > 0`。随后结合 RCTD 主导亚群、平均表达和表达细胞比例，为发送—接收细胞组合计算通信分数。

论文得到 PTC 42 对、LPTC 52 对、ATC 56 对候选相互作用。重点是 ATC 中 **SERPINE1–PLAUR**：SERPINE1 主要见于成纤维和内皮细胞，PLAUR 主要见于甲状腺和髓系细胞；Fib-12 与 Mac-11 在空间上相邻。多重免疫荧光进一步显示，从 PTC 到 LPTC、ATC，带相应标记的成纤维细胞与巨噬细胞丰度和共定位增加。SERPINE1 在癌组织中升高，并与较短生存相关；自有 50 人队列中 SERPINE1/PLAUR 也与肿瘤阶段和状态相关。

空间邻接和共表达比纯 scRNA 配体—受体分析多了一层约束，但仍不是直接测量蛋白结合、信号方向或功能效应。多重免疫荧光支持蛋白共定位，却没有通过阻断 SERPINE1/PLAUR 证明该轴导致 ATC 侵袭。因此应称为“高优先级通信候选”。

### 10. 主要结果如何连成一条证据链

这项工作提出的进展图景是：

- PT/早期状态保留甲状腺分化功能；
- PTC 到 LPTC 出现甲状腺细胞亚群和基质组成过渡；
- ATC 显示低分化、高 BRAF 程序、增殖增强以及更强成纤维/髓系浸润；
- 癌样甲状腺状态周围由 B/T 细胞较多的环境转向巨噬细胞和特定成纤维亚群；
- ATC 前缘形成显著基质—免疫重塑，并出现 SERPINE1–PLAUR 候选通信轴。

最强证据来自多层一致性：空间表达、单细胞参考、RCTD 去卷积、病理边界、外部 TCGA、自有队列和免疫荧光相互补充。最弱环节是把跨患者阶段差异解释为单一路径演化，以及把空间共表达解释为功能通信。

### 11. 代码—论文对应与复现边界

- **Exact**：`1.1.STintegratedAnalysis.R` 实现 Visium Seurat/SCTransform/PCA/聚类；`2.0.RCTD.R` 实现 RCTD 去卷积；`4.0.tds_ras_braf_score.R` 实现模块评分及其与伪时间相关；`6.0.CellCellInteraction.R` 明确实现六邻域配体—受体相关和 BH 过滤。
- **Partial**：`1.0.scRNAintegratedAnalysis.R` 显示 QC、Harmony 和聚类骨架，但依赖未定义的外部对象，且合并后流水线中出现 `sce[[i]]` 这样的上下文缺失调用；它更像分析摘录而非可从零执行脚本。
- **Partial**：Monocle3 结果读取存在，但建图、根细胞设置和保存对象的完整代码未提供。
- **Not found**：病理前缘标注转为 spot 标签、论文所述 edgeR pseudobulk 完整实现、多重免疫荧光图像定量流程不在代码快照中。
- **环境依赖**：脚本大量使用 `~/ST/`、`~/Project/ST/`、`/data/ST/` 和 `/home/reference/` 等硬编码路径，并读取未随仓库分发的 RDS、signature 与配体—受体对象；无法一键从原始 FASTQ 重现论文。
- **版本/对象风险**：许多分析以已保存 Seurat/Monocle/RCTD 对象为起点，实际参数和中间筛选可能隐藏在对象生成历史中。

### 12. 正确解释与局限

研究建立了有价值的甲状腺癌空间进展 atlas，但不能由此断言所有 PTC 都沿同一轨迹变成 ATC，也不能将 BRAF/RAS 模块分数当作基因型。样本量为 17 个空间样本，阶段与患者不同，性别、突变背景、治疗和取材区域可能混杂。Visium spot 是多细胞混合，RCTD 和邻域分析依赖参考与空间尺度。病理前缘为人工定义，伪时间不等于谱系，配体—受体相关不等于因果信号，生存相关也不证明治疗靶点有效。

合理结论是：多模态和空间证据共同揭示了随甲状腺癌恶性程度增加而变化的甲状腺细胞状态、成纤维—免疫微环境和侵袭边缘，并把 SERPINE1–PLAUR 提升为值得进行功能扰动和临床验证的候选轴。

### 13. 源证据导航

- 论文全文与 STAR Methods：`paper.md`
- 主图：`images/gr1_lrg.jpg` 至 `images/gr6_lrg.jpg`
- 代码目录：`code/lishenglilab-Thyroid-cancer-ST-55c0cfd/code/`
- ST 整合：`1.1.STintegratedAnalysis.R`
- RCTD：`2.0.RCTD.R`
- TDS/BRAF/RAS：`4.0.tds_ras_braf_score.R`
- 伪时间结果：`5.0.trajectoryInference.R`
- 空间配体—受体：`6.0.CellCellInteraction.R`
- 详细代码匹配：`doc_code.md`
- 逐图解释：`figure_analysis.md`

最终事实判断应回到论文和直接源码；本文件负责解释数据流、假设和证据边界，不把生成文档当作原始证据。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ThyroidCancerProgressionST Summary

### Motivation And Novelty

This paper builds a spatially resolved atlas of thyroid cancer progression from para-tumor thyroid (PT), papillary thyroid cancer (PTC), locally advanced PTC (LPTC), and anaplastic thyroid carcinoma (ATC). Prior thyroid cancer single-cell studies, including Luo et al. (*Science Advances*, 2021) and Pu et al. (*Nature Communications*, 2021), characterized thyroid tumor cell states and immune ecosystems but could not show where those cells reside or interact in tissue. Standard ligand-receptor tools such as CellPhoneDB (*Nature Protocols*, 2020) and NicheNet (*Nature Methods*, 2020) also infer communication mostly from co-expression, which can overstate interactions when spatial adjacency is unknown.

The novelty is not a new algorithm. It is an integrated resource and analysis framework combining Visium ST, in-house and public scRNA-seq, RCTD deconvolution, thyrocyte pseudotime, pathologist-defined leading-edge regions, and spatially constrained ligand-receptor correlation to describe TME remodeling across thyroid cancer stages.

### Method Overview

The pipeline starts from Space Ranger ST matrices and Cell Ranger scRNA-seq matrices. ST spots are normalized and clustered with Seurat. In-house and public scRNA-seq datasets are filtered, merged, and batch-corrected with Harmony. RCTD uses the scRNA-seq reference to estimate cell-type proportions at each spatial spot.

The authors then subcluster thyrocytes, score them for thyroid differentiation (TDS), BRAF, and RAS programs, and use Monocle3 pseudotime to infer a progression axis. Tumor leading edges are manually annotated from H&E images and analyzed for cell composition, differential expression, and pathway enrichment. Ligand-receptor pairs from CellPhoneDB/NicheNet are filtered by differential expression and tested for spatial correlation between ligand-expressing spots and adjacent receptor-expressing spots.

### Evaluation And Biological Findings

The atlas contains 57,997 ST spots from 17 tissue components and integrates 253,822 high-quality single cells. The main findings are:

- PTC and PT are more thyrocyte-dominant, while ATC has greater fibroblast, myeloid, and NK-cell infiltration.
- Thyrocytes form 16 subpopulations and three meta-clusters: normal/pre-cancerous `TG/IYD`-high, HLA-high early cancerous, and `APOE/APOC1`-high late cancerous states.
- Pseudotime is negatively correlated with TDS and RAS scores and positively correlated with BRAF score, supporting a dedifferentiation/progression interpretation.
- Tumor leading edges differ by stage; ATC leading edges have high fibroblast abundance, while LPTC shows broad leading-edge transcriptional dysregulation.
- Spatial LR analysis identifies stage-specific crosstalk, especially SERPINE1-PLAUR in ATC. Multiplex immunofluorescence and TCGA THCA analyses support SERPINE1 as associated with malignancy and poorer survival.

### Reproducibility

Reproducibility rating: **3/5**.

The paper provides public raw data (`GSE250521`) and a Zenodo code archive (`10.5281/zenodo.14880735`). The archive contains scripts for the main computational stages and closely matches key methods such as RCTD, TDS/BRAF/RAS scoring, and spatial LR correlation.

The main limitation is that the code is not turnkey. It uses hardcoded absolute paths, assumes precomputed `.RDS` objects, lacks environment/data-download instructions, and omits public scripts for pathologist leading-edge spot assignment and some intermediate pseudobulk/Monocle construction steps. A motivated analyst could reconstruct much of the workflow from GEO plus the scripts, but exact figure regeneration would require additional author-side intermediate files or careful reimplementation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
