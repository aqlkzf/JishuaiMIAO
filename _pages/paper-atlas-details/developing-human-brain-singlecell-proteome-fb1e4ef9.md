---
layout: default
permalink: /paper-atlas/developing-human-brain-singlecell-proteome-fb1e4ef9/
title: "Developing_Human_Brain_SingleCell_Proteome"
nav: false
description: "这项工作把每个胎儿脑细胞单独送入一次液相色谱–质谱（LC–MS）分析，在 2,310 个通过质控的细胞中建立蛋白质图谱，再与同一批组织的单细胞 RNA 测序比较。它要回答的核心问题不是“哪些基因被转录”，而是“哪些蛋白真正出现、出现在哪类细胞、又如何随神经发生而变化”。 这不是一个单一机器学习模型，而是一条由实验技术、单细胞聚类、跨组学校正、伪时间和网络模块分析组成的完整流水线。"
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
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>Developing_Human_Brain_SingleCell_Proteome</h1>
    <p>Single-cell proteomic landscape of the developing human brain</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/SingleCellProteomics/Brain" target="_blank" rel="noopener noreferrer" aria-label="Open code for Developing_Human_Brain_SingleCell_Proteome">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 发育中人脑单细胞蛋白质组：方法详解

### 一句话理解

这项工作把每个胎儿脑细胞单独送入一次液相色谱–质谱（LC–MS）分析，在 2,310 个通过质控的细胞中建立蛋白质图谱，再与同一批组织的单细胞 RNA 测序比较。它要回答的核心问题不是“哪些基因被转录”，而是“哪些蛋白真正出现、出现在哪类细胞、又如何随神经发生而变化”。

这不是一个单一机器学习模型，而是一条由实验技术、单细胞聚类、跨组学校正、伪时间和网络模块分析组成的完整流水线。

### 1. 为什么需要直接测蛋白质？

RNA 是蛋白质生产的上游信息，但 RNA 多并不保证蛋白质也多。翻译效率、RNA 核滞留、蛋白降解、膜蛋白/不溶性蛋白提取困难等因素都会改变 RNA 与蛋白的对应关系。论文特别指出，人脑皮层的 RNA–蛋白不一致在既往组织研究中非常明显，而且 bulk 数据会把细胞间差异平均掉 (`paper.md:21-36`)。

已有单细胞蛋白技术也有边界：

- **CyTOF、CITE-seq** 属于抗体驱动的靶向测量。CITE-seq 发表于 *Nature Methods*（2017），优点是可与转录组结合，缺点是依赖抗体数量、特异性和预先选择的靶点，总体只能覆盖很小一部分蛋白质组。
- **SCoPE-MS** 发表于 *Genome Biology*（2018），代表载体通道和同位素标签的多重单细胞蛋白质组路线。它能提高通量和深度，但可能带来 ratio compression、批次效应、载体干扰和额外变异。
- 后来的无标记单细胞质谱减少了标签伪影，但很多研究仍集中在培养细胞、少量细胞，或卵母细胞、心肌细胞、肝细胞等体积较大的细胞。胎儿皮层神经元直径约 7–10 µm，估计只有约 5–50 pg 蛋白，对样本损失和仪器灵敏度都非常苛刻 (`paper.md:27-33`)。

因此，这篇论文的技术目标是：在不按细胞类型预富集的情况下，对真实、微小、异质的原代人脑细胞进行大规模、无标记、全局蛋白质测量。

### 2. 输入、输出和总体流程

#### 输入

- GW13、GW15、GW19 的新鲜产前人脑组织；
- GW15/GW19 分为生发区（GZ）和皮层板（CP），GW13 使用包括神经节隆起在内的额叶端脑；
- 同一份组织一分为二，分别进入单细胞蛋白质组和单细胞 RNA 测序；
- 蛋白可观测性特征、TrIP-seq、pLI、SFARI、de novo 突变和小鼠同源基因等外部数据。

#### 输出

- 2,310 个通过质控细胞的蛋白质定量矩阵，其中 1,505 个为脑细胞；
- RG、oRG、IPC–EN、EN、CGE-IN、OPC、小胶质细胞、血管细胞等蛋白质定义的细胞类型；
- RNA–蛋白一致性和不一致性结果；
- RG → IPC–EN → EN 的蛋白质伪时间；
- 六个沿发育变化的 WGCNA 蛋白模块；
- 与进化约束、ASD/NDD 遗传风险相关的模块和基因集合。

#### 流程图

```text
产前人脑组织（GW13 / GW15 GZ+CP / GW19 GZ+CP）
                        │
                 同一组织分成两路
                        │
          ┌─────────────┴─────────────┐
          │                           │
          v                           v
  单细胞蛋白质组                 10x Flex scRNA-seq
  解离 → 活细胞 FACS             Cell Ranger → QC
  每孔一个细胞                         │
  2 µl 裂解/酶切                       │
  EvoTip → Evosep → Orbitrap DIA       │
          │                           │
        DIA-NN                        │
          │                           │
  QC → 标准化 → PCA/Harmony            │
  图聚类 → UMAP → 蛋白标记注释  ←── 同细胞类型伪 bulk 比较
          │
          ├── ORBIT 可观测性校正
          │      → RNA–蛋白回归残差
          │      → A/B 两类不一致基因
          │      → tau 细胞类型特异性
          │
          └── RG → IPC–EN → EN 伪时间
                 → 30 个时间 bin
                 → WGCNA 六个模块
                 → dN/dS、pLI、SFARI、de novo 突变
```

### 3. 单细胞样本如何进入质谱？

组织经 papain 解离后，使用 Sony SH800 流式分选仪把活细胞逐个放入 384 孔低吸附板。每孔预先加入 1 µl 裂解液：100 mM TEAB、10 mM TCEP、40 mM chloroacetamide 和 0.1% n-dodecyl-β-D-maltoside。样本先在 95 °C 加热 5 分钟，再加入 2.5 ng trypsin，使总反应体积只有 2 µl，并在 37 °C 过夜酶切。随后用三氟乙酸终止反应，EvoTip 脱盐，再进入 LC–MS (`paper.md:246-258`)。

这里的关键不是某个复杂公式，而是尽量减少微量样本的吸附、稀释和转移损失。每个细胞单独一次质谱运行，牺牲通量来换取定量精度，并避免同位素标签的比例压缩和载体干扰。

### 4. 质谱采集与 DIA-NN 定量

质谱平台为带 FAIMS 的 Orbitrap Eclipse。肽段经 31 分钟梯度分离；MS1 覆盖 *m/z* 400–800，分辨率 240,000；每个循环包含十个 DIA MS2 扫描，使用相邻重叠 1 *m/z* 的 50-*m/z* 隔离窗，MS2 分辨率 120,000 (`paper.md:261`)。

DIA-NN 搜索 UniProt 人类参考蛋白质组，允许 Trypsin/P 两个漏切、7–30 aa 肽段、1–4 价前体，并控制前体、肽段和蛋白鉴定 FDR 为 1%。片段离子峰面积逐级汇总到前体和蛋白，启用 match-between-runs (`paper.md:264-267`)。

**证据缺口：** GitHub 快照中没有 DIA-NN 命令、配置文件、原始文件清单或从 raw 到蛋白矩阵的脚本。因此这一层只能依据论文方法描述，不能从本地代码复现。

### 5. 从蛋白矩阵构建细胞图谱

论文描述的下游步骤是：

1. 空孔对照和总离子流、蛋白数、角蛋白污染质控；
2. 每个细胞中位数标准化并做 log 转换；
3. Seurat v5 缩放、PCA、Harmony 批次校正；
4. 基于 Harmony 分量构图、Louvain 聚类和 UMAP；
5. 删除高角蛋白污染群；
6. 先分离红系和脑细胞，再分别重聚类；
7. 使用已知标记蛋白注释细胞类型 (`paper.md:267-270`)。

图 2 中可直接看到：红系细胞与脑细胞形成分离的 UMAP 岛；脑细胞中 HOPX/TNC 对应 oRG，EOMES 对应 IPC–EN，TBR1 对应 EN，SCGN/CALB2 对应 CGE-IN，S100B/SIRT2 对应 OPC，P2RY12 对应小胶质细胞，PDGFRB 对应血管细胞。

#### 代码实际做了什么？

- `Brain/script/1.cluster_all_proteome.R:12-82` 创建 protein assay 的 Seurat 对象，运行 SCTransform、PCA、Harmony、邻居图、Louvain 和 UMAP，删除两个 cluster，并把 cluster 硬编码为 Blood/Brain。
- `Brain/script/2.sub_cluster_proteome.R:11-96` 分别重聚类血细胞和非血细胞。
- 代码与论文参数并非完全相同：初始邻居图使用 15 个 Harmony 维度，而 UMAP 使用 50 维；脑细胞重聚类的 resolution 为 2、`min.dist=0.5`。因此是 **Partial** 对应，不是 Exact。

### 6. 配对 RNA 数据怎样比较？

同一组织的另一半使用 10x Flex。论文质控阈值为 `nCount_RNA` 1,000–100,000、线粒体比例 ≤5%，并删除 Scrublet score >0.1 的 doublet；最终保留 31,639 个细胞，经过 SCTransform、50 PCs、Harmony、SNN 聚类和标记基因注释 (`paper.md:291-300`)。

比较时不直接比较两种技术得到的细胞比例，因为捕获率、过滤阈值和解离偏好都不同。作者只在已经匹配好的细胞类型内部比较分子信号。图 3 显示整体细胞类型能够对齐，但 MKI67、TBR1、SCGN 等基因出现明显 RNA–蛋白偏差。

`Brain/script/3.pairRNA_cluster.R:17-109` 覆盖标准化、SCTransform、Harmony、聚类、UMAP 和手工标签，但从一个已经构建好的 RNA `qs` 对象开始，不包含 Cell Ranger、论文质控和 Scrublet 步骤。

### 7. ORBIT：为什么不同蛋白不能直接比 DIA-NN 强度？

DIA-NN 很适合比较“同一个蛋白在不同细胞/条件中的变化”，因为它持续追踪相同的 proteotypic peptides。但若比较“同一细胞类型中蛋白 A 与蛋白 B 谁更多”，原始强度会受到可检测性影响：长蛋白通常产生更多胰蛋白酶肽段，疏水性影响离子化，跨膜区影响提取和 LC–MS 回收。

ORBIT 使用三个蛋白特征校正这些偏差：

- 理论 tryptic peptide 数 $T_p$；
- 平均疏水性 $H_p$；
- 预测跨膜螺旋长度 $M_p$。

论文没有在本地正文中给出明确公式。为了理解，可以把论文文字写成下面的示意模型：

$$
I_{p,c}=\beta_{0,c}+\beta_{T,c}T_p+\beta_{H,c}H_p+\beta_{M,c}M_p+\varepsilon_{p,c},
$$

其中 $I_{p,c}$ 是蛋白 $p$ 在细胞类型 $c$ 的 DIA-NN 强度，残差 $\varepsilon_{p,c}$ 被当作校正后的相对丰度。**这是解释性重写，不是论文原文公式。**

#### 代码证据与重要差异

`Brain/script/5.ORBIT.jl:21-51` 对每个细胞类型列拟合 ridge regression，默认正则参数 `r=0.5`，只拟合正值，随后可按列 z-score。

但代码存在两处必须单独记录的行为：

1. `Brain/script/5.ORBIT.jl:14-19` 使用 `.=`，把跨膜螺旋结束坐标覆盖成开始坐标；按代码字面执行，并没有计算“结束−开始”的长度。
2. ridge 模型提取了截距 `b`，但返回的是 $y-XA$，不是完整残差 $y-(XA+b)$ (`Brain/script/5.ORBIT.jl:34-44`)。

这些差异对论文数值结果的影响没有被本次分析测试，因此不能进一步推断结果是否改变。

### 8. RNA–蛋白不一致的 A/B 两组

作者在每个细胞类型中回归蛋白丰度与 RNA 表达。可以用示意式表示：

$$
P_{g,c}=\alpha_c+\gamma_cR_{g,c}+\delta_{g,c}.
$$

- 大的正残差：**A 组**，RNA 低、蛋白相对高；
- 大的负残差：**B 组**，RNA 高、蛋白相对低。

论文正文以 $P\leq0.05$ 描述极端残差；嵌入式 Pluto 源码则把所有细胞类型残差合并排序，选择最高 2.5% 和最低 2.5% (`Brain/notebook/notebook.html:6`，解码后的 `Group A and group B Genes` cell)。完整 bootstrap 和显著性细节位于缺失的 Supplementary Note，因此两种描述如何完全对应仍不清楚。

论文结果显示：

- A 组富集干细胞分化、细胞周期、RNA 剪接，并与较高翻译效率相关；
- B 组富集神经元生成、迁移和轴突发育，并与 RNA 核滞留、较长 3′ UTR、较低翻译效率、较低预测溶解度和短蛋白半衰期相关；
- B 组同时富集高 pLI、SFARI 高置信基因和 ASD/NDD 截短突变 (`paper.md:140-157`)。

这些是统计关联，不是因果证明。

### 9. 为什么蛋白的细胞类型特异性更高？

论文使用 tau score。嵌入式 notebook 中的实际公式是：

$$
\tau(x)=\frac{1}{n-1}\sum_{i=1}^{n}\left(1-\frac{x_i}{\max_j x_j}\right).
$$

- $\tau\approx0$：多个细胞类型都表达；
- $\tau\approx1$：集中在少数细胞类型。

图 5 显示：全部基因和 SFARI 基因的蛋白 tau 通常高于 RNA tau；B 组尤其明显。A 组则相反，因为它们的蛋白在多个细胞类型中都比较高，反而降低了特异性 (`paper.md:160-169`)。

图 4 的组织验证非常关键：TBR1、ZBTB18、CHD3、MAPT 等 RNA 空间范围较广，但对应蛋白集中在更窄的细胞/皮层区域。这说明较高蛋白特异性并不只是 UMAP 或缺失值造成的视觉假象。

### 10. 蛋白质伪时间与 WGCNA

#### 伪时间

论文重建 RG → IPC–EN → EN 轨迹。EOMES 在中间阶段升高，TBR1 和 ZBTB18 在后期升高 (`paper.md:172-175`)。

`Brain/script/4.brain_pseudotime.py:9-26` 的实现是：

1. 仅保留 RG、IPC-EN、EN；
2. 在 Harmony 表征上建立 30 邻居图；
3. 运行 PAGA；
4. 选第一个 RG 细胞为根；
5. 计算 diffusion map 和 DPT；
6. 输出带 `dpt_pseudotime` 的 `brain_pseudotime.h5ad`。

正文没有明确写 PAGA/DPT，因此这里也是 **Partial** 对应。

#### WGCNA

作者把伪时间划成 30 个 bin，对蛋白变化做 WGCNA，得到六个模块。代码使用 signed adjacency、TOM、Ward.D2 聚类、dynamic tree cut 和 module eigengene (`Brain/script/6.module_analysis.jl:8-115`)。

代码中的具体选择包括：

- 先估计 soft-threshold，随后强制设为 4；
- 最小模块大小为 50；
- merge cutoff 为 0.3；
- bin 1–7 为 RG，8–20 为 IPC–EN，21–30 为 EN。

但脚本所需的 `precomputed/wgcna_merge_matrix.csv` 和 `precomputed/wgcna_30bin_anno.csv` 并不在仓库中，所以无法仅凭快照重跑模块发现。

### 11. 从模块到 ASD 风险

进化速率使用：

$$
\omega=\frac{dN}{dS}.
$$

较低 $\omega$ 代表更强的进化保守。论文报告模块 4/5 更保守，模块 1/4/5 富集高 pLI，模块 5 富集 SFARI 基因，模块 4 富集 ASD proband 的有害 de novo missense 变异 (`paper.md:183-195`)。

本地 `notebook.html` 内嵌的 Pluto 代码确实包含 Fig. 6d–g：

- 一对一人鼠同源基因的 $dN/(dS+\epsilon)$；
- pLI >0.9 的模块比例；
- SFARI 基因比例；
- REVEL >0.5 的 affected/unaffected Fisher 检验和多重校正。

不过这些代码只存在于预编译 HTML 中；可编辑 `.jl` notebook 和自包含 Julia 环境缺失。Fig. 6i 的 GO 富集代码也没有找到。

### 12. 论文怎样验证结果？

这项工作的验证不是单一 accuracy 指标，而是多层证据：

- 空孔背景和每细胞蛋白数；
- 与既往单细胞蛋白质组规模比较；
- 经典正/负标记蛋白；
- 与 CP/GZ bulk proteome 和突触后致密区蛋白组比较；
- 配对 scRNA-seq 与大规模参考 snRNA-seq；
- TBR1、SCGN、TRIM33、ZBTB18、CHD3、MAPT 的 RNAscope/免疫染色；
- bootstrap 相关性、tau、pLI、SFARI、de novo 突变和人鼠 $dN/dS$。

最强的图像证据是：图 2 的多标记细胞图谱、图 4 的六个 RNA–蛋白空间验证，以及图 6 中阶段化的模块曲线。

### 13. 代码可复现性判断

**总体：3/5，代码–论文匹配度为 medium。**

能够直接核对的部分：蛋白/RNA 聚类、DPT 伪时间、ORBIT 主体、WGCNA 主体，以及 notebook 中的 Fig. 5 和 Fig. 6d–g 统计。

不能完整复现的部分：

- DIA-NN 原始处理；
- 本地 Supplementary Note；
- WGCNA 的预计算矩阵和 bin 注释；
- 自包含 Julia/Pluto 环境；
- Fig. 6i GO 富集；
- Fig. 6h 完整突变高亮流程；
- 部分处理后 CSV 的生成过程。

因此，仓库能解释很多下游分析“怎样做”，但不能从原始质谱数据一键重建全部论文结果。

### 14. 如何正确理解结论？

论文证据支持以下**描述性解释**：

1. 直接测量蛋白能比 RNA 更清楚地定位细胞身份；
2. 一部分发育/疾病基因处于“RNA 已准备、蛋白被限制”的状态；
3. IPC–EN 过渡期出现一个进化保守且富集 ASD 变异的蛋白模块。

但它没有证明 RNA–蛋白不一致导致 ASD，也没有证明模块 4 是唯一因果通路。论文进一步提出：神经元激活后，B 组中被核滞留的 RNA 可能释放到胞质并出现快速翻译 (`paper.md:207`)。这是**论文假说**，不是本研究直接干预验证的机制。

### 15. 最终要点

这项工作的真正价值不只是“测到了很多蛋白”，而是把蛋白丰度放回具体细胞类型和发育时间轴中。它显示：如果只读 RNA，某些神经发育疾病基因会显得广泛而模糊；读蛋白后，这些基因的活跃细胞和脆弱发育窗口会变得更具体。与此同时，代码证据也提醒我们，ORBIT 的实现差异和缺失的定量补充材料必须保留为不确定性，不能把论文主张、代码行为和解释性推断混为一谈。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Single-cell proteomic landscape of the developing human brain

### Overview

Wu et al. present a label-free single-cell mass-spectrometry workflow and prenatal human-brain proteome atlas. By dedicating one LC–MS run to each FACS-isolated cell, the study profiles 2,310 QC-passed cells from GW13, GW15 and GW19 tissue, including 1,505 brain cells, and reports an average of roughly 800 quantified proteins per nonerythroid brain cell. Paired scRNA-seq, tissue imaging and developmental trajectory analyses show that protein abundance often conveys sharper cell identity than RNA expression and reveals an IPC–EN transition protein program associated with autism risk.

### Problem and limitations of prior approaches

The study addresses two gaps. First, transcript abundance is an imperfect proxy for protein abundance, with especially strong bulk RNA–protein discordance previously reported in cerebral cortex. Second, many single-cell protein assays do not provide unbiased proteome-wide measurement in small primary cells.

- Targeted CyTOF and CITE-seq (introduced in *Nature Methods*, 2017) depend on antibody availability/specificity and collectively cover less than 1% of the proteome.
- Multiplexed carrier approaches such as SCoPE-MS (*Genome Biology*, 2018) improve depth/throughput but can introduce ratio compression, batch effects and variability.
- Many label-free MS studies before this work focused on cultured cells, modest cell counts or large primary cells such as oocytes, cardiomyocytes and hepatocytes. Prenatal neurons are only about 7–10 µm in diameter and may contain roughly 5–50 pg protein (`paper.md:21-33`).

### Proposed workflow and atlas

Fresh prenatal tissue was split for paired proteomic and transcriptomic profiling. For proteomics, dissociated live cells were sorted individually into 384-well low-bind plates, lysed and digested in a 2-µl reaction, desalted on EvoTips and analyzed on an Orbitrap Eclipse using label-free DIA. DIA-NN quantified protein groups; empty-well comparison, protein-yield/contamination QC, normalization, PCA, Harmony, graph clustering and UMAP produced the atlas (`paper.md:42-56,231-270`).

The 1,505-cell brain subset resolves RG, oRG, IPC–EN, EN, CGE-IN, OPC, microglia and vascular populations. Marker-protein overlays support these labels, while erythroid cells form a separate compartment with fetal, maternal and progenitor substructure (Fig. 2).

The paired RNA arm contains 31,639 QC-passed cells. Rather than compare raw cell-type fractions across modalities, the study compares molecular profiles within matched cell types. Global identities align, but specific markers—including MKI67/KI67, TBR1, SCGN, TRIM33, ZBTB18, CHD3 and MAPT—show broader or shifted RNA expression relative to protein abundance. Immunostaining and RNAscope reproduce these discrepancies in tissue (Figs. 3–4).

### Key computational analyses

#### ORBIT and RNA–protein discordance

For comparing different proteins within one cell type, the authors introduce ORBIT (Observability-Regularized, Biochemistry-Integrated Transformation). It adjusts DIA-NN intensities using theoretical tryptic peptide count, hydrophobicity and predicted transmembrane-helix length, then uses adjusted residuals for cross-protein ranking (`paper.md:134-140`).

Per-cell-type protein-versus-RNA regressions identify:

- **group A:** low RNA but relatively high protein, enriched for stem-cell regulation, RNA processing/splicing and high translational efficiency;
- **group B:** high RNA but relatively low protein, associated with neuronal-development programs, nuclear enrichment, longer 3′ UTRs, reduced translation efficiency/solubility, short protein half-life and genetic dosage sensitivity.

Even in EN—the most concordant cell type—the mean RNA–protein Spearman correlation is only 0.36. Group B is enriched for high-pLI genes, high-confidence SFARI genes and truncating mutations in ASD/NDD cohorts (`paper.md:140-157`).

#### Protein specificity

Tau scores show that protein abundance is generally more cell-type-specific than RNA expression. This holds for all detected proteins and SFARI genes and is supported by spatial validation. Group A is an exception, with broadly high protein abundance reducing specificity; group B shows especially sharp protein specificity (`paper.md:160-169`).

#### Developmental trajectory and modules

Proteomic pseudotime orders RG → IPC–EN → EN cells, with EOMES peaking at the intermediate stage and TBR1/ZBTB18 increasing later. WGCNA over pseudotime yields six protein modules. Module 4 activates near the IPC–EN transition; module 5 rises with EN emergence. Modules 4 and 5 show lower mouse–human $dN/dS$, modules 1/4/5 are enriched for high-pLI genes, module 5 is enriched for SFARI genes, and module 4 carries excess deleterious de novo missense variants in ASD probands (`paper.md:172-195`).

The paper interprets module 4 as a coordinated program spanning cytoskeleton, RNA processing/translation, proteostasis, chromatin regulation, mitochondrial metabolism and vesicle trafficking during the progenitor-to-neuron transition.

### Evaluation and main evidence

The evaluation is multi-layered rather than a single benchmark:

- **Technical scale/depth:** empty controls versus cell yields; comparison with prior single-cell proteomics studies; approximately 800 proteins per brain cell on average.
- **Atlas validity:** canonical marker proteins and negative controls; comparison with GZ/CP bulk proteomes and postsynaptic-density references.
- **Cross-modal validity:** paired scRNA-seq and a population-scale snRNA-seq reference; within-cell-type correlations and bootstrap uncertainty.
- **Orthogonal validation:** RNAscope and immunostaining for six discordant genes across multiple fetal brains.
- **Specificity and disease association:** tau, pLI, SFARI, de novo ASD/NDD mutations, and mouse–human evolutionary rates using Wilcoxon/Fisher tests with multiple-testing correction.

The figures visibly support the descriptive narrative: Fig. 1 establishes scale, Fig. 2 the cell atlas, Figs. 3–4 the cross-modal discrepancies and spatial validation, Fig. 5 genome-wide specificity/disease associations, and Fig. 6 developmental modules.

### Reproducibility assessment: 3/5 (medium code–paper fidelity)

The GitHub snapshot directly supports much of the downstream analysis:

- R scripts implement proteome and paired-RNA Harmony/UMAP/clustering.
- Python implements RG→IPC–EN→EN PAGA/diffusion-map/DPT pseudotime.
- Julia implements ORBIT and WGCNA logic.
- Embedded Pluto source in `notebook.html` contains major Fig. 5 analyses and Fig. 6d–g evolutionary/genetic statistics.

However, the repository is not an end-to-end reproduction package:

- no DIA-NN command/configuration or raw-MS processing workflow was found;
- the local Supplementary Note is missing, leaving quantitative-analysis details incomplete;
- the WGCNA standalone script requires unavailable `precomputed/` matrices;
- the editable Pluto notebook and self-contained Julia environment are absent;
- Fig. 6i GO-enrichment code was not found, and Fig. 6h highlighting is incomplete;
- ORBIT code as written does not calculate transmembrane-helix length and returns an adjustment that omits the fitted intercept, differences whose numerical impact was not tested.

Processed proteome/transcriptome data, raw proteomics accession PXD071075, scRNA-seq accession GSE310125 and the project portal are reported by the paper (`paper.md:330-339`).

### Limitations and hypothesis boundary

Paper-reported limitations include loss of distal processes during dissociation, under-recovery of insoluble/membrane proteins, pseudobulk rather than same-cell RNA–protein comparison, and limited donors, regions and developmental stages (`paper.md:222`).

The data establish association, not causality: protein-specific expression and module-4 ASD enrichment do not prove that translational regulation or the IPC–EN transition causes disease. The proposed activation-triggered release and translation of nuclear-retained group-B transcripts is a **paper hypothesis** (`paper.md:207`), not an experimentally tested mechanism in this study.

### Take-home message

The study's main contribution is a technically demanding primary-tissue resource showing that protein measurements add biological resolution unavailable from RNA alone. The most compelling result is not simply widespread RNA–protein discordance, but that protein-level specificity reorganizes where neurodevelopmental-disease genes appear active and exposes a conserved, genetically vulnerable protein program at the IPC–EN transition.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
