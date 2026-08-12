---
layout: default
permalink: /paper-atlas/spatial-brain-development-0121cc65/
title: "Spatial-brain-development"
nav: false
description: "这项工作开发了两种 DBiT 空间三组学技术，在同一张组织切片、同一个空间像素内联合测量表观层、转录层和蛋白层；再用时空回归把“随年龄变化”“随解剖位置变化”和“时间与位置共同变化”分开。由此发现，脑发育中染色质开放常早于或晚于 RNA，胼胝体髓鞘化具有双向空间顺序，而局灶脱髓鞘还能沿白质束诱发远端小胶质细胞反应。 论文同时包含技术平台、发育图谱和炎症机制三条主线。"
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
      <span>Nature · 2025</span>
    </div>
    <h1>Spatial-brain-development</h1>
    <p>Spatial dynamics of brain development and neuroinflammation</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-025-09663-y" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 空间脑发育三组学：同时看染色质、RNA 与蛋白如何随时间和位置变化

论文：*Spatial dynamics of brain development and neuroinflammation*（Nature, 2025；DOI: 10.1038/s41586-025-09663-y）

### 一句话理解

这项工作开发了两种 DBiT 空间三组学技术，在同一张组织切片、同一个空间像素内联合测量表观层、转录层和蛋白层；再用时空回归把“随年龄变化”“随解剖位置变化”和“时间与位置共同变化”分开。由此发现，脑发育中染色质开放常早于或晚于 RNA，胼胝体髓鞘化具有双向空间顺序，而局灶脱髓鞘还能沿白质束诱发远端小胶质细胞反应。

论文同时包含技术平台、发育图谱和炎症机制三条主线。仓库代码对条形码预处理与 RNA–ATAC 时空 GAM 覆盖较好，但只覆盖论文约一部分分析；CODEX、SpatialGlue、cell2location、CellChat、NICHES 和 TRIC-DISCO 等关键结果缺少对应脚本。

### 1. 为什么必须在同一位置测三层信息

RNA 告诉我们细胞当前在表达什么，染色质开放或抑制性组蛋白标记告诉我们哪些调控区处于可用或沉默状态，蛋白则更接近最终执行层。三个信号不必同步：

- 染色质可以先开放，而 RNA 尚未升高，表示“预备”或 priming；
- RNA 已下降，染色质仍开放，表示调控状态的持续；
- RNA 空间上很局限，但开放染色质扩展到邻近层，表示空间 spreading；
- 蛋白还受翻译、稳定性和运输影响，可能再次滞后。

如果三种模态来自不同切片或不同细胞，模态差异可能与组织位置不匹配混在一起。空间 ARP-seq 和 CTRP-seq 的价值，是尽量让三种信号共享同一个二维条形码坐标。

### 2. 空间 ARP-seq 怎样把 ATAC、RNA 和蛋白放到同一像素

空间 ARP-seq 是 ATAC–RNA–protein sequencing。流程可以从组织到三类文库顺序阅读：

1. 冷冻切片固定后，加入约 150 种带 DNA 标签的抗体；抗体识别蛋白，DNA 标签作为 ADT 读出。
2. Tn5 转座酶进入开放染色质并插入接头，产生 ATAC 片段。
3. 带生物素的 poly(T) 引物与 mRNA poly(A) 尾及 ADT 相关序列结合，在组织内逆转录。
4. 第一块微流控芯片沿一个方向送入 $A_i$ 条形码，第二块垂直送入 $B_j$ 条形码。
5. 两方向交点形成唯一组合 $(A_i,B_j)$，定义一个空间像素。
6. 释放条形码化 cDNA 和 gDNA，分别构建 RNA/ADT 与 ATAC 文库。

100×100 通道产生 10,000 个 20 μm 像素，220×220 通道产生 48,400 个 15 μm 像素。这个“像素”接近细胞尺度，但不自动等于单细胞：一个像素可能覆盖多个细胞片段或细胞边界，因此论文仍需要 deconvolution 和 CODEX 单细胞图像作为辅助。

### 3. 空间 CTRP-seq 与 ARP-seq 的关键差别

空间 CTRP-seq 把开放染色质 ATAC 换成针对 H3K27me3 的 CUT&Tag。抗 H3K27me3 一抗和二抗定位后，protein A–Tn5 在目标附近切割并接头化。

因此两平台的表观层含义相反：

- ARP-seq 的 ATAC/GAS 高，通常表示调控区域更开放；
- CTRP-seq 的 H3K27me3/CSS 高，通常表示该基因附近抑制性标记更强。

在 LPC 病灶中，髓鞘相关基因的 H3K27me3 与 RNA/开放性呈反向趋势，而免疫基因表现相反。这种三模态互证比单独一张 RNA 图更能区分“细胞组成改变”与“调控状态改变”，但 CSS 仍是基因周围信号聚合，不是某个启动子因果沉默的直接实验。

### 4. 原始 reads 如何被重新解释为空间 reads

仓库最完整的早期步骤是自定义条形码抽取。

`RNA_BC_process.py` 和 `CITE_BC_process.py` 从一条 FASTQ 序列固定位置截取：

```text
seq[22:30] + seq[60:68] + seq[98:108]
```

也就是两个 8 nt 区段加一个 10 nt 区段，组合成下游识别的条形码序列。`ATAC_BC_process.py` 则把第 117 位之后作为新的 ATAC read 1，把位置 22:30 与 60:68 拼成新的 barcode read 2。之后调用 Cell Ranger ARC 2.0.2 对 RNA 和 ATAC 比对与计数，ADT 交给 CITE-seq-Count。

这些切片位置是实验接头结构的硬编码知识。一旦读长、接头布局或测序方向改变，脚本不会自动推断，必须重新核对设计。

### 5. 为什么还要合并 2×2 spots

15–20 μm 像素空间精细，但 ATAC 或 RNA 每像素计数可能很稀疏。`merge_spots_squaredgrid.py` 默认按 2 行×2 列合并相邻点：

$$
r' = \left\lfloor\frac{r}{2}\right\rfloor,\qquad
c' = \left\lfloor\frac{c}{2}\right\rfloor.
$$

具有相同 $(r',c')$ 的原始 barcode 映射到一个新 barcode。ATAC fragments 的 barcode 被替换后重新 bgzip/tabix；RNA count matrix 用一个稀疏的原点到新点映射矩阵 $M$ 聚合：

$$
X_{merged}=M^T X_{original}.
$$

左到右理解：$M$ 指明每个原始像素属于哪个新像素，转置后乘原始计数，就把组内 counts 相加。这样提高覆盖度，但有效分辨率降低一倍，并可能把边界两侧的细胞混合。它是信噪比与空间精度的明确交换。

### 6. 单模态聚类和多模态空间域

RNA 端用 Seurat SCT、PCA 和 Harmony 整合不同年龄或重复，再做 UMAP/Louvain；ATAC 端用 Signac 构建 common peak set、TF–IDF/LSI 和整合。论文随后用 SpatialGlue 联合 RNA 与 ATAC，得到比单模态更精细的空间域。

图 1 中，P0–P21 小鼠识别出 22 个 RNA 簇与 15 个 ATAC 簇；SpatialGlue 得到 18 个联合空间域。RNA、ATAC、ADT 和 CODEX 对 *Mbp*、*Foxp4* 等标记的空间变化相互参照。

重要边界是：仓库有 Seurat、Signac 与 ArchR 的部分脚本，却没有 SpatialGlue 主分析脚本。因此 18 个空间域是论文结果，不能从当前仓库直接一键重建。

### 7. 时空 GAM：把年龄、位置和交互拆开

论文的核心计算组件是逐基因广义加性模型（GAM）。对于基因 $g$ 在像素 $c$ 的 RNA count：

$$
Y_{gc}\sim NB(\mu_{gc},\phi_g),
$$

$$
\log \mu_{gc}=\beta_{g0}+\beta_{g1}N_c+
f_{g,t}(t_c)+f_{g,s}(s_c)+f_{g,ts}(t_c,s_c).
$$

各项含义是：

- $Y_{gc}$：观测 RNA count；
- $N_c$：该像素的 library size，用于控制测序深度；
- $t_c$：P0、P2、P5、P7、P10、P21 编成数值时间；
- $s_c$：皮层层级或胼胝体位置；
- $f_t$：只随时间的平滑变化；
- $f_s$：只随空间的平滑变化；
- $f_{ts}$：不同位置具有不同时间轨迹的交互项。

负二项分布适合有过度离散的 count。代码用 `mgcv::gam(..., family=nb())`，并只拟合在超过 2% 像素中非零的基因。

一个直观例子：若某髓鞘基因所有位置都在 P10 后上升，主要是 $f_t$；若始终只在外侧胼胝体高，是 $f_s$；若 P10 先在外侧升高、P21 再向内侧移动，必须由 $f_{ts}$ 表达。

### 8. ATAC 为什么不直接逐 peak 套同一模型

ATAC peak 比 RNA 更稀疏。代码先用 FigR 将基因 TSS ±50 kb 内的可及性整合成 DORC score，再以 RNA PCA 空间中的 4 个近邻平滑，最后转换：

$$
Z_{gc}=\log_2(DORC_{gc}+1).
$$

对连续的 $Z_{gc}$ 使用 Gaussian GAM：

$$
Z_{gc}=f_{g,t}(t_c)+f_{g,s}(s_c)+f_{g,ts}(t_c,s_c)+\epsilon_{gc}.
$$

这提高稳定性，但产生一个解释边界：ATAC DORC 经过 RNA 邻域平滑，因此后续 RNA–ATAC 相似性并非完全来自两个独立模态。它仍可揭示不同动态，但不能把所有一致性都视为独立验证。

### 9. 基因如何通过筛选

代码不是只看一个平滑项的 P 值，而是三重条件交集：

1. 时间、空间或交互至少一项 BH 校正后 $P<0.01$；
2. full GAM 相比 null model 的 likelihood-ratio test $P<0.01$；
3. adjusted $R^2$ 超过实现阈值：RNA > 0.02，ATAC > 0.025。

第三个阈值在论文正文中没有充分明示，是代码层面的隐藏选择。它用于排除统计显著但解释量极低的基因，会影响进入聚类的基因集合。

皮层脚本还显式使用 $k=5$ 的时间 basis、$k=4$ 的空间与交互 basis；胼胝体脚本依赖 mgcv 默认 $k$。这意味着两个区域的平滑自由度不完全相同。

### 10. 从每个基因的曲线得到联合 RNA–ATAC 程序

筛选后，代码对每个基因取得 GAM 预测值，并按“时间点×空间区”求均值。对每个基因独立做 z-score：

$$
z_{gk}=\frac{\hat y_{gk}-\overline{\hat y_g}}{sd(\hat y_g)}.
$$

然后把同一基因的 RNA 与 ATAC 向量横向拼接，用 $1-r_{Pearson}$ 衡量动态形状差异，Ward.D2 层次聚类。

胼胝体实现先切成 20 个小簇，再分别把 RNA 归并为 6 类、ATAC 归并为 4 类，组合成 `R*_A*` 标签；皮层以更高的初始簇数再归并为 15 个 RNA 和 10 个 ATAC 模式。

“先过度聚类、再合并”不是一个概率模型自动估计最佳簇数，而是人为设定层次的工程策略。它便于发现 RNA 与 ATAC 不同步的组合，如 RNA 已关闭但 ATAC 仍开放。

### 11. 皮层发现：persistence、spreading 与 priming

图 2 将基因按 RNA 与 ATAC 时空动态分类。

- **时间持续**：*Sox4*、*Sox11*、*Sox5*、*Mef2c*、*Plxna4* 等 RNA 随发育下降后，开放染色质仍保留。
- **空间扩展**：*Fezf2*、*Tbr1*、*Bhlhe22* 等 RNA 保持层特异，但 ATAC GAS 扩展到更多皮层层级。
- **提前开放**：部分髓鞘基因在 RNA 明显上升前已有 ATAC 信号。

这些现象支持“染色质状态形成一个比瞬时 RNA 更宽的调控许可窗口”。但 GAS 是基因附近 peak 的聚合代理，不能直接证明某个 enhancer 驱动后续表达；需要位点级扰动才能建立调控因果。

人 V1 的第二孕期、第三孕期与婴儿期也显示相似的层标记和少突胶质发育顺序，说明部分模式跨物种保守。阶段对应是生物学对照，不意味着人和小鼠的绝对发育时间可直接线性换算。

### 12. 胼胝体发现：髓鞘化不是单一方向推进

作者把胼胝体从内侧到外侧划成 10 个空间 bin，再用同一 GAM 分解 P0–P21 动态。RNA 得到 6 类、ATAC 得到 4 类。

髓鞘程序 R6 在 P10 先于外侧上升，到 P21 向内侧扩展。与此同时，OPC/COP 在中央区域分化，提示髓鞘形成存在多源空间过程，而不是从一个中心均匀扩散。

retro-AAV-eGFP 分别追踪 callosal projection neurons（CPN）和 corticothalamic projection neurons（CThPN）：CPN 轴突偏内侧，CThPN 轴突偏外侧；P10 时外侧 CThPN 轴突与 MBP 共标记显著更多。图 3 用 AUC 后的双侧非配对 t 检验报告 $P=0.0001$。

因此论文提出双向模型：外侧 CThPN/SCPN 轴突较早髓鞘化，同时中央少突谱系分化，之后扩展到内侧 CPN 区域。GAM 提供时空模式，AAV 追踪提供投射神经元身份验证，两者缺一不可。

### 13. LPC 模型如何连接发育与神经炎症

作者在胼胝体注射 1% lysolecithin（LPC）造成局灶脱髓鞘，在 5、10、21 days post lesion（d.p.l.）比较急性损伤、炎症与再髓鞘化。

图 4 中，ARP-seq 同时显示 RNA、ATAC 和蛋白的损伤变化；CTRP-seq 增加 H3K27me3 抑制维度。病灶早期 *Olig2*、*Mog* 等髓鞘信号下降，*Ptprc*、*Csf1r* 等免疫信号升高，21 d.p.l. 出现恢复。

联合空间域和 lesion compartments 的完整生成涉及 SpatialGlue、cell2location 和自定义近邻选择。这些步骤在论文方法中描述，但仓库没有对应核心脚本，因此不能从现有代码验证所有病灶分区参数。

### 14. 远端炎症为什么不是简单的局部泄漏

图 5 在原发胼胝体病灶之外，于 stria medullaris、fornix、dorsal hippocampal commissure 等白质区域看到 CD11b/CD11c/Csf1r 信号。冠状、矢状 CODEX 和 TRIC-DISCO 全脑三维成像共同显示信号沿白质束向前后与腹侧分布。

“远端”并非任意远离注射点的像素，而是解剖上与白质通路相连、且多种模态出现一致免疫标记的区域。TRIC-DISCO 提供整脑连续结构证据，但其图像分析脚本未在代码仓库中提供，最终依据仍是论文图与方法。

### 15. 原发与远端小胶质细胞不是同一状态

图 6 先用 cell2location 和经典标记选择 lesion-like 区域，再联合 RNA/ATAC 得到 LC1–LC5；从 *P2ry12*、*Tmem119*、*Cx3cr1* 等小胶质像素中再分 MC1–MC3。

- MC1 富集 *Nrxn3*、*Cntn2* 等神经元/髓鞘支持相关信号；
- MC3 富集 *Apoe*、*Abca1*、*Btk* 等脂质处理、炎症和吞噬程序；
- 原发病灶 10 d.p.l. 更偏 MC3，远端白质更偏 MC1/MC2，提示远端反应具有延迟和不同状态。

CellChat 推断 MC1 更多与非小胶质 CNS 细胞通讯，MC3 更多与小胶质细胞互作；NICHES 展示 *Fn1–Itga4*、*Cntn2–Cntnap2*、*Apoe–Lrp1*、*Tgfb3–Tgfbr2* 等空间模式。这些是基于表达和数据库的候选互作，不是受体结合或因果通讯的直接测量。

### 16. 代码中可直接对应的部分

#### Exact / 高度对应

- RNA、ADT、ATAC 固定位置的 barcode 重排；
- Cell Ranger ARC、CITE-seq-Count 的命令入口；
- 2×2 空间像素合并、ATAC fragments barcode 改写与 RNA sparse-matrix 聚合；
- Seurat/Signac/ArchR 的部分聚类与可视化流程；
- RNA negative-binomial GAM 和 ATAC log-DORC Gaussian GAM；
- 2% 检出过滤、smooth-term/LRT/adjusted-$R^2$ 联合筛选；
- time×space 聚合、z-score、RNA–ATAC 拼接及 Ward.D2 两步聚类。

#### Partial / 部分对应

- 原始数据预处理脚本依赖 Yale HPC 绝对路径、外部软件和手工逐数据集运行，没有统一入口；
- DORC 与 RNA-neighbor smoothing 有实现痕迹，但依赖预生成 RDS；
- 聚类与图形脚本覆盖部分论文 panel，完整中间对象生成链不齐；
- 仓库可重建 GAM 核心，但输入对象、环境和参数配置未标准化。

#### Not found / 本地代码没有覆盖

- CODEX Cellpose 分割与完整聚类；
- SpatialGlue RNA–ATAC 联合空间域；
- cell2location deconvolution；
- lesion compartment 的完整 k-NN 选择实现；
- CellChat 与 NICHES 分析；
- TRIC-DISCO 图像处理；
- retro-AAV 图像定量和全部湿实验平台步骤。

所以“代码与论文一致性”应限定为：预处理和时空 GAM 主干具有直接实现证据，整篇论文的技术与生物学结论只获得中等覆盖。

### 17. 最重要的解释边界

1. 空间像素接近细胞尺度，不等于严格单细胞。
2. ATAC DORC 经 RNA 邻域平滑，RNA–ATAC 一致性并非完全独立。
3. GAM 是描述时空关联，不追踪单个细胞谱系，也不自动证明调控因果。
4. 预设 $k$、adjusted-$R^2$ 阈值和空间整数编码会影响聚类结果。
5. 远端炎症依赖论文图像与多模态证据，仓库无法完整复算。
6. ligand–receptor 结果是候选通讯，需要扰动实验确认。

### 18. 证据入口

- 论文正文：`paper source/PMC12589135/paper.md`
- 主图与扩展图：`paper source/PMC12589135/images/`
- 本地代码：`spatial_tri-omics/`
- 详细数学与流程：`doc_method.md`
- 代码—论文对应：`doc_code.md`
- 逐图解读：`figure_analysis.md`

本文档中的实现细节来自本地代码 commit `e2d1eb8ff0e0ce675340a8521c0a728ac04b6d81`；生物学结论最终以论文、图和直接代码证据为准。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spatial Dynamics of Brain Development and Neuroinflammation

### Motivation & Novelty

Understanding mammalian brain development requires simultaneous spatial mapping of the epigenome, transcriptome, and proteome — the three layers of the central dogma — within intact tissue. Previous spatial omics technologies could co-profile at most two molecular layers, limiting the ability to study how chromatin states coordinate with gene expression and protein levels across development and disease.

#### Key Limitations of Prior Work
- **Spatial ATAC-RNA-seq** (Zhang et al., *Nature*, 2023): Only epigenome + transcriptome, no proteome
- **Spatial CUT&Tag** (Deng et al., *Science*, 2022): Only histone modifications, no RNA or protein
- **CODEX** (Goltsev et al., *Cell*, 2018): Only proteins, limited to ~50 markers
- **DBiT-seq** (Liu et al., *Cell*, 2020): RNA + protein but no epigenome
- **Single-cell multi-omics** (various): Lack spatial resolution

#### Unique Contributions
1. **Two new spatial tri-omic technologies**: spatial ARP-seq (ATAC + RNA + ~150 proteins) and spatial CTRP-seq (H3K27me3 CUT&Tag + RNA + ~150 proteins) at 15–20 μm resolution
2. **Spatiotemporal atlas**: Mouse brain P0–P21 development + human V1 cortex (2nd trimester through infancy)
3. **Computational framework**: NB-GAM regression for joint spatiotemporal modeling of RNA and ATAC, with two-step hierarchical clustering
4. **Discovery of chromatin accessibility persistence and spatial spreading** for cortical layer TFs
5. **Bidirectional myelination model**: Lateral-to-medial CC myelination coordinated by projection neuron subtypes, validated with retro-AAV tracing
6. **Distal microglial activation**: First spatial multi-omic evidence of inflammatory spread along white matter tracts beyond the primary lesion

---

### Method Overview

#### Technologies
- **Spatial ARP-seq**: DBiT-based co-profiling of ATAC (Tn5 tagmentation), RNA (poly-A RT), and protein (ADT antibodies) within the same tissue section. Microfluidic barcoding creates a 2D grid of 10,000–48,400 pixels at 15–20 μm resolution.
- **Spatial CTRP-seq**: Same as ARP-seq but replaces Tn5 with CUT&Tag for H3K27me3 histone modification profiling.
- **CODEX**: 23-plex (mouse) / 19-plex (human) multiplexed immunofluorescence at single-cell resolution.
- **TRIC-DISCO**: Whole-brain 3D light-sheet imaging of specific RNA transcripts in cleared tissue.

#### Computational Pipeline
1. **Preprocessing**: FASTQ reformatting → Cell Ranger ARC alignment → Seurat/ArchR clustering → SpatialGlue multi-modal integration
2. **Spatiotemporal regression**: Per-gene NB-GAM (RNA) or Gaussian GAM (ATAC DORC scores) capturing time, space, and interaction effects
3. **Joint clustering**: Hierarchical clustering on concatenated RNA + ATAC predicted profiles → over-cluster then merge → combined spatiotemporal gene programs
4. **Downstream**: GO enrichment, cell2location deconvolution, CellChat communication analysis, NICHES ligand-receptor analysis

See `doc_method.md` for full mathematical details and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Datasets
| Dataset | Species | Timepoints | Technology | Replicates |
|---|---|---|---|---|
| Postnatal brain development | Mouse | P0, P2, P5, P7, P10, P21 | Spatial ARP-seq, CODEX | S1 (20μm), S2 (15μm) |
| V1 cortex development | Human | 2nd trimester, 3rd trimester, infancy | Spatial ARP-seq, CODEX | 1 per stage |
| LPC neuroinflammation | Mouse | 5, 10, 21 d.p.l. | Spatial ARP-seq, CTRP-seq, CODEX | S1, S2 |

#### Quality Metrics
- Spatial ARP-seq: 11,635 unique ATAC fragments/pixel, 1,230 genes/pixel, 59 proteins/pixel
- Replicate correlation: r = 0.99 (ATAC), r = 0.98 (RNA), r = 0.99 (protein)
- Spatial CTRP-seq: 9,102 unique fragments/pixel (H3K27me3), 1,318 genes/pixel

#### Key Results
1. **Cortical layers**: 15 RNA and 10 ATAC spatiotemporal patterns identified. Subset of layer-defining TFs (*Fezf2*, *Tbr1*, *Bhlhe22*) show chromatin accessibility spreading across layers even as RNA expression remains layer-restricted.
2. **Chromatin persistence**: *Sox4*, *Sox11*, *Mef2c*, *Sox5*, *Plxna4* retain ATAC signal after RNA expression declines — epigenetic memory of prior developmental states.
3. **CC myelination**: 6 RNA and 4 ATAC patterns in CC. Bidirectional myelination: OPCs/COPs from central CC + simultaneous oligodendrocyte differentiation at lateral CC. R6 (myelination program) activates laterally at P10, shifts medially by P21.
4. **PN-myelination coordination**: CThPN axon tracts (lateral CC) myelinated before CPN tracts (medial CC), validated by retro-AAV-eGFP tracing (P = 0.0001, two-tailed t-test).
5. **Distal inflammation**: CD11c⁺ microglia/macrophages detected in stria medullaris and fornix at 10 d.p.l., distant from primary LPC lesion. TRIC-DISCO confirmed spread along CC (anterior/posterior) and fornix.
6. **Microglial heterogeneity**: MC1 (neuron/myelin supportive: *Nrxn3*, *Cntn2*), MC2 (intermediate), MC3 (pro-inflammatory: *Apoe*, *Abca1*). CellChat: MC1 interacts with CNS cells; MC3 interacts with other microglia.

#### Cross-Species Conservation
- Most cortical layer TF patterns conserved between mouse and human (*BCL11B*, *FEZF2*, *TBR1*)
- Oligodendrogenesis temporal sequence conserved: human 2nd trimester ≈ mouse P0; 3rd trimester ≈ P2–P10; infancy ≈ P7–P21

---

### Reproducibility

**Rating: 3/5** — Moderate reproducibility challenges despite public data and code.

#### Strengths
- **Data availability**: All raw and processed data deposited at NeMO archive and GEO (GSE308623); CODEX at Zenodo
- **Interactive data portal**: https://spatial-omics.yale.edu/
- **Code repository**: https://github.com/di-0579/spatial_tri-omics (archived at Zenodo)
- **Detailed experimental protocols**: Methods section describes all wet-lab procedures in detail

#### Weaknesses
- **Incomplete code**: Repository covers only ~30% of computational analyses (GAM regression + preprocessing). Missing: CODEX analysis, SpatialGlue, cell2location, CellChat, NICHES, lesion compartment selection
- **Hardcoded paths**: All R scripts contain Yale HPC-specific absolute paths, requiring manual modification
- **No configuration**: No parameters files, no environment/conda specs, no containerization
- **Custom reagents**: Spatial ARP-seq requires custom Tn5 transposomes, PDMS microfluidic chips, and ADT conjugation — not commercially available as a kit
- **Custom hardware**: DBiT microfluidic barcoding devices (AtlasXomics for 220-barcode version)
- **Computational resources**: ≥64 GB RAM; GAM fitting on ~10,000 genes with 40 cores takes significant time
- **No unit tests**: Repository lacks any testing infrastructure

#### Practical Notes
- The spatiotemporal regression framework (NB-GAM) is the most reproducible component — standard R packages (mgcv, Seurat, ArchR)
- SpatialGlue and cell2location are established Python tools that can be applied independently
- The experimental technology is the main barrier to reproduction — computational analyses use standard bioinformatics tools

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
