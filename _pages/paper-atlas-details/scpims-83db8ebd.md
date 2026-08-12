---
layout: default
permalink: /paper-atlas/scpims-83db8ebd/
title: "scPiMS"
nav: false
description: "scPiMS（single-cell proteoform imaging mass spectrometry）把稀疏铺在玻片上的单细胞逐个扫过 nano-DESI 液桥，直接提取并测量完整蛋白质形态（proteoform），再把稀疏的“细胞 × proteoform”信号聚合到生物通路层面，用无监督聚类区分大类海马细胞群。"
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
      <span>Technology Platforms</span>
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>scPiMS</h1>
    <p>Proteoform profiling of endogenous single cells from rat hippocampus at scale</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scPiMS 方法详解：从单细胞完整蛋白质形态到通路分群

### 一句话理解

scPiMS（single-cell proteoform imaging mass spectrometry）把稀疏铺在玻片上的单细胞逐个扫过 nano-DESI 液桥，直接提取并测量完整蛋白质形态（proteoform），再把稀疏的“细胞 × proteoform”信号聚合到生物通路层面，用无监督聚类区分大类海马细胞群。

它的重点不是“每个细胞鉴定尽可能多的蛋白”，而是用较低但保留完整分子形态的单细胞覆盖深度，换取约每天 1,000 个细胞的采样规模。

### 1. 论文要解决什么问题？

蛋白质没有类似 DNA/RNA 的分子扩增手段，因此质谱单细胞蛋白组学同时受到两类限制：

1. **样本处理和灵敏度限制。** 单个细胞中的蛋白量极低，需要尽量减少转移、消化和分离损失。
2. **吞吐量限制。** 论文指出，当时多数 MS 单细胞蛋白组平台每天通常处理数百个细胞，难以达到单细胞转录组常见的千到百万级规模（`paper.md:21-27`）。
3. **proteoform 信息损失。** bottom-up 流程先把蛋白酶解为肽段，通常无法直接保留剪切、翻译后修饰和序列变体共同定义的完整 proteoform。

论文提到的代表性路线包括：

- SCoPE-MS，*Genome Biology*，2018：用多重标记和肽段质谱研究单细胞蛋白组异质性；
- nanodroplet 单细胞蛋白组，*Analytical Chemistry*，2019：缩小样本制备体积并提高并行度；
- deep visual proteomics，*Nature Biotechnology*，2022：结合成像选择和肽段蛋白组学定义细胞身份。

scPiMS 的选择是绕开单细胞分装、蛋白酶解和色谱分离，直接从细胞中提取完整蛋白质形态，并用 individual-ion MS 提高检测灵敏度。

### 2. 输入与输出

#### 输入

- 大鼠海马组织解离得到的单细胞；
- 稀疏铺在 ITO 玻片上的细胞位置与光学坐标；
- nano-DESI 扫描过程中连续采集的 I$^2$MS/STORI 数据；
- 海马来源的 proteoform 同位素包络参考库；
- proteoform 注释、细胞注释以及 KEGG/REACTOME 通路集合。

#### 中间数据

- processed-ion chronogram：每个扫描时刻的处理后离子数；
- cellogram：液桥经过一个细胞时形成的尖峰—衰减信号；
- 每个细胞的一组 individual-ion 质量；
- 细胞 × proteoform PAScore 矩阵；
- 细胞 × pathway 的 GSVA 分数矩阵。

#### 输出

- 每个细胞中通过 10% FDR 的 proteoform 指派；
- 5,272 个细胞 × 165 个已鉴定 proteoform 的分数矩阵；
- 147 条通路的 pathway-adjusted score，并进一步筛到 15 条高变通路；
- PAM 得到的三个无监督细胞群；
- 对三个群的生物学解释：神经元、小胶质细胞和星形胶质细胞。

### 3. 从输入到输出的完整流程

```text
海马组织
  ↓ 解离、低密度铺片、荧光/明场成像
细胞光学坐标
  ↓ 200 µm nano-DESI 液桥平行线扫描
连续 I²MS 扫描 + processed-ion chronogram
  ↓ 峰值阈值、峰间距和衰减形状过滤
单细胞 cellogram 与对应扫描区间
  ↓ STORI 电流斜率估计整数电荷
每个细胞的中性 individual-ion 质量
  ↓ 与理论同位素包络匹配（±0.3 Da）
每个“细胞—proteoform”的 PAScore
  ↓ 每个正向 proteoform 配 10 个 decoy；q < 0.1
FDR 过滤后的细胞 × proteoform 矩阵
  ↓ 同基因多个 proteoform 合并
细胞 × gene score 矩阵
  ↓ KEGG/REACTOME GSVA
细胞 × pathway score 矩阵
  ↓ 高变通路筛选、标准化
15 维通路表示
  ↓ silhouette + PAM(k=3) + PCA/heatmap
三个无监督群
  ↓ 通路、proteoform、形态和群体比例解释
Neuron / Microglia / Astrocyte
```

### 4. 步骤一：让液桥“刚好扫过一个细胞”

细胞被低密度铺在玻片上，目标是让相邻细胞平均距离大于液桥尺度。scPiMS 使用约 200 µm 的 nano-DESI 动态液桥覆盖扫描区域。论文先用光学坐标把表面划成近似 200 µm 的网格，估计每个网格包含 0、1 或多个细胞的概率（`paper.md:121-127`）。

公开 MATLAB 代码 `scAnalyzer.m:15-38` 直接实现了这个占用模型：读入二维坐标，按固定网格做 `hist3`，再统计 singleton、double 和 multiple features。这一部分与论文描述是 **Exact** 匹配，但输入路径和视野尺寸写死在脚本中。

液桥在一个细胞上停留时，蛋白信号先快速升高，再在约 5–7 秒内衰减到基线。论文据此定义扫描速度：

$$
\mathrm{Rastering\ scan\ rate}
=\frac{\mathrm{Probe\ size}+\mathrm{single\ cell\ size}}{\mathrm{Exposure\ time}}
\cong\frac{\mathrm{Probe\ size}}{\mathrm{Exposure\ time}}.
$$

以 200 µm 液桥和约 7 秒暴露时间计算，正式高通量实验使用 30 µm s$^{-1}$（`paper.md:130-141`）。质谱以每秒一个扫描周期采集数据。

### 5. 步骤二：从连续 chronogram 中找出单细胞事件

连续扫描会产生大量空白、化学噪声、单细胞峰和多细胞重叠峰。算法需要完成两件事：

1. 找到高于背景且相互间隔足够远的峰；
2. 根据峰右侧衰减宽度排除可能包含多个细胞的宽峰。

公开 MATLAB 脚本的实际流程是：

- 从 STORIBoard CSV 中保留 scan number 和 processed ion count（`scAnalyzer.m:52-71`）；
- 用 `findpeaks` 做峰高和最小峰距过滤（`scAnalyzer.m:87-90`）；
- 如果峰顶后第 5 个扫描仍高于半峰值，则删除该峰（`scAnalyzer.m:96-109`）；
- 在峰顶左右取扫描窗口，删除低于峰顶 5% 的点；
- 输出 `ScanIndex` 和 `FeatureIndex`（`scAnalyzer.m:119-151`）。

这里存在明确的参数不一致：

- Methods：500 ions、最小间隔 8 scans（`paper.md:156-160`）；
- Extended Data Fig. 1：750 ions、7 scans（`paper.md:375-380`）；
- 当前代码：`countThres=800`、`cellogram=8`，并检查峰后第 5 个扫描。

因此，公开代码验证了算法结构，但不能视为论文参数的唯一实现；该步骤是 **Partial**。

### 6. 步骤三：从带电离子得到中性完整质量

选出单细胞扫描区间后，流程把同一细胞对应的 STORI individual-ion 信号聚合起来。每个离子的整数电荷 $z$ 来自 induced image current 的斜率，再按下式计算中性质量：

$$
\mathrm{Mass}=\left(\frac{m}{z}\times z\right)-\left(z\times M_{\mathrm{proton}}\right).
$$

论文还说明，会比较不同电荷态下 isotopolog 的 STORI 斜率，以概率指标过滤低可信电荷指派（`paper.md:162-170`）。

**代码证据：Not found。** 当前仓库没有 STORI 电荷指派或 Eq. 2 的实现。`scAnalyzer.m` 只输出扫描—feature 对应关系，而 `ss_GSVA.qmd` 已经从 PAScore 工作簿开始。

### 7. 步骤四：PAScore 如何组合多个离子证据？

每个细胞的中性离子质量与候选 proteoform 的理论同位素峰比较，质量容差为 ±0.3 Da。第 $k$ 个匹配离子贡献两个量：

- $P_{\mathrm{isotopolog}}$：该理论同位素峰的预期相对强度；
- $P_{\mathrm{mass\ error}}$：观测质量与理论质量误差对应的概率。

多个离子证据通过 complement-of-products 形式合并：

$$
\mathrm{PAScore}=1-\prod_{k=1}^{n}
\left[1-\left(P_{\mathrm{isotopolog}}\times P_{\mathrm{mass\ error}}\right)\right].
$$

直觉上，如果每个匹配都提供一些独立支持，那么 $1-\prod(1-p_k)$ 表示“至少有一个可靠证据”的累积概率式分数。匹配离子越多、同位素相对强度越合理、质量误差越小，PAScore 越高。

质量误差项由以理论同位素质量为中心的正态 CDF 给出：

$$
P_{\mathrm{mass\ error}}=
\begin{cases}
\mathrm{CDF}(m_{\mathrm{ion}}), & m_{\mathrm{ion}}<m_{\mathrm{iso}},\\
1-\mathrm{CDF}(m_{\mathrm{ion}}), & m_{\mathrm{ion}}>m_{\mathrm{iso}}.
\end{cases}
$$

随后，每个真实 proteoform 配置 10 个等长度随机氨基酸 decoy，在单细胞层面对 target/decoy 分数排序并计算 q value，保留 $q<0.1$ 的指派（`paper.md:173-192`）。

**关键缺口：MISSING。** 仓库 README 说明 `SingleCellApp.exe` 负责打分，并给出 FDR=0.10、decoy/forward=10 的 demo 参数（`README.md:43-49`），但当前快照没有该 exe、C# 源码或 demo 输入。因此不能验证：

- PAScore 公式的具体数值实现；
- decoy 随机化、seed 和去重规则；
- q value 估计方法与并列分数处理；
- composite ion、缺失值和重复 isotopolog 的处理。

### 8. 步骤五：为什么要从 proteoform 聚合到 pathway？

Extended Data Fig. 3 显示，“细胞 × 165 proteoform”候选矩阵高度稀疏：约 87 万个候选项中，只有约 5% 是非零且通过指派的 PAScore，许多匹配仅依赖 2–3 个离子。直接在 proteoform 维度聚类会受到大量零值和采样波动影响。

论文先把同一基因对应的多个 proteoform 合并：

$$
\mathrm{PAScore}_{\mathrm{gene}}
=1-\prod_{k=1}^{n}\left(1-\mathrm{PAScore}_k\right).
$$

`ss_GSVA.qmd:89-115` 中的 `pas_merge()` 精确实现了这一公式，因此该部分是 **Exact**。

接下来，代码：

1. 载入 `pca_input.xlsx` 的 `ScoreFDR` sheet、proteoform 注释和细胞注释（`ss_GSVA.qmd:37-54`）；
2. 将 Entrez ID 映射到人类基因符号和 UniProt 信息（`ss_GSVA.qmd:58-82`）；
3. 删除全零细胞和全零基因（`ss_GSVA.qmd:117-140`）；
4. 从 `c2BroadSets` 选择 KEGG 和 REACTOME 通路（`ss_GSVA.qmd:142-153`）；
5. 对每个细胞运行 GSVA，得到 pathway × cell 分数（`ss_GSVA.qmd:155-174`）。

GSVA 把同一通路内多个基因的相对排序整合成样本级通路活性。这里每个单细胞被当作一个 sample。它牺牲了部分单一 proteoform 分辨率，但增强了稀疏信号的群体结构。

### 9. 步骤六：从通路矩阵得到三个细胞群

论文报告 147 条可映射通路，保留变异最大的前 10%，即 15 条通路。公开 QMD 使用：

```r
featurefilter(gsva.es, percentile=10, method='A', topN=25)
```

然后按通路做 z-score（`ss_GSVA.qmd:176-193`）。由于仓库没有包含输出矩阵，无法确认这些选项一定产生论文所述的 15 条通路；这里是 **Partial**。

聚类部分则非常清楚：

- 用 silhouette 图检查候选簇数；
- 明确选择 $k=3$；
- 运行 `cluster::pam(t(gsva.es2), k=3)`；
- 生成 heatmap 和 PCA（`ss_GSVA.qmd:240-347`）。

PAM 是 partitioning around medoids。与 k-means 使用均值中心不同，PAM 选择真实样本作为 medoid，对异常值通常更稳健。这里的输入是“细胞 × 标准化通路分数”。

三个簇的细胞类型名称不是监督学习标签，而是聚类后的生物学解释：

- **Cluster 1 → neuron：** 数量最大、内部异质性高，并有 ARP5L 等信号；
- **Cluster 3 → astrocyte：** glucose/carbohydrate metabolism 通路和 ALDOA、GFAP 等 proteoform 较高；
- **Cluster 2 → microglia：** 免疫相关通路和 ARF1、PP5-TPR、PSMD11 等信号较高。

少量光学形态图像和总体细胞比例提供辅助支持，但不是全体细胞的独立 ground truth。

### 10. 主要实验结果

- 两个数据集共测量 10,809 个细胞，约每天 1,000 个细胞（`paper.md:30`）。
- Dataset I：6,116 个光学 feature 中检测到 5,272 个单细胞事件，转换率 86%；旧制样流程的 Dataset II 约 50%（`paper.md:50-53`）。
- Dataset I 包含约 2,900 万个 verified ions、2,230 万个 charge-assigned ions、566 个检测到的 proteoform features（`paper.md:56`）。
- 165 个参考 proteoform 中，平均每个细胞指派 86 个；23 个得到额外 top-down MS/MS 支持（`paper.md:65`）。
- 4,927/5,272 个细胞进入三个群：3,817 neurons、317 microglia、793 astrocytes；345 个未分类（`paper.md:68-76`）。

图像证据显示三个群在 PCA 中是“偏移但重叠”的云团，不是完全分开的类别。因此 93% 更准确地理解为“93% 被聚类并赋予群体解释”，而不是有独立标签验证的 93% 分类准确率。

### 11. 代码与论文的一致性

总体评价：**medium fidelity**。

| 模块 | 状态 | 结论 |
|---|---|---|
| 光学网格占用统计 | Exact | 代码直接统计 singleton/double/multiple grids。 |
| cellogram 峰选择 | Partial | 算法结构一致，但论文内部与代码的阈值/间距不一致。 |
| STORI 电荷和中性质量 | Not found | 当前仓库没有实现。 |
| PAScore、decoy、q value | Not found | 仅 README 描述外部 `SingleCellApp.exe`。 |
| 同基因 proteoform 分数合并 | Exact | `pas_merge()` 对应公式。 |
| KEGG/REACTOME GSVA | Exact | QMD 中直接实现。 |
| 高变通路筛选 | Partial | 目标一致，但没有输出证明精确恢复 15 条通路。 |
| silhouette + PAM(k=3) | Exact | QMD 直接实现。 |
| PCA/heatmap | Exact | QMD 直接实现。 |

### 12. 复现时最容易踩的坑

1. `scAnalyzer.m` 不是通用命令行工具：坐标路径、chronogram 文件名、阈值和输出文件名都需要手工修改。
2. 公开脚本不能直接生成 `pca_input.xlsx`；README 说明该文件来自缺失的 WPF 应用。
3. QMD 还需要 `pfr_annotation.xlsx` 和 `cell_annotation.xlsx`，当前工作区没有这些 demo 输入。
4. QMD 会在运行时安装未固定版本的 R/Bioconductor 包，论文虽写 GSVA 1.50.5，但仓库没有 lockfile 强制该版本。
5. 当前 MATLAB 代码、Methods 和 Extended Data Fig. 1 给出的 peak 参数不一致，复现者必须先确定目标数据集对应的参数。
6. 离子深度在三个推断细胞群之间不同；图中未充分展示 depth-matched 或敏感性分析，需警惕技术深度对聚类的影响。这是待检验假设，不是已经证明的偏差。

### 13. 如何正确理解这项工作的贡献

scPiMS 最强的贡献是一个“测量平台 + 数据解释链条”：

- 用液桥和 I$^2$MS 直接测量完整 proteoform；
- 把吞吐量推进到 $10^4$ 细胞规模；
- 用参考库、PAScore 和 FDR 把 individual ions 组织成细胞级 proteoform 信息；
- 再用通路聚合与无监督聚类，从稀疏信号中恢复海马主要细胞群结构。

它目前不是一个可直接从 GitHub 一键复现的完整软件包。公开 MATLAB/R 源码足以理解上游 feature picking 和下游 pathway clustering，但中间最关键的 PAScore/FDR 实现仍然是 **MISSING**。因此，研究者应把论文的技术可行性结论与当前代码快照的端到端复现能力分开评价。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## scPiMS: Proteoform Profiling of Endogenous Single Cells at Scale

### Overview

scPiMS is a single-cell proteomics technology that directly extracts and measures intact proteoforms from surface-immobilized cells using a nano-DESI liquid bridge and individual-ion mass spectrometry (I$^2$MS). In rat hippocampus, the study profiles 10,809 cells in two datasets at approximately 1,000 cells per day and uses a dedicated informatics workflow to organize cells into neuron-, astrocyte- and microglia-associated populations (`paper.md:12-30`).

The central contribution is the combination of high-throughput physical sampling with proteoform-aware computation. Rather than digesting proteins into peptides, scPiMS preserves intact molecular forms up to roughly 70 kDa, constructs cell-specific ion/mass spectra, assigns proteoforms with a probability-based PAScore and transforms sparse proteoform scores into pathway-level features for clustering.

### Problem and Prior Limitations

Mass-spectrometry single-cell proteomics must work without molecular amplification. Bottom-up approaches can identify many proteins, but the paper highlights two constraints: daily throughput is usually in the hundreds of cells, and digestion removes direct information about intact proteoforms (`paper.md:21-27`). Examples cited by the article include:

- SCoPE-MS, *Genome Biology* (2018), which uses multiplexed peptide-level MS to quantify single-cell proteome heterogeneity;
- nanodroplet-based multiplexed SCP, *Analytical Chemistry* (2019), which miniaturizes sample preparation;
- deep visual proteomics, *Nature Biotechnology* (2022), which links imaging and peptide-level proteomics.

scPiMS takes a different route: it bypasses single-cell compartmentalization, proteolytic digestion and chromatographic separation, accepting lower per-cell proteome depth in exchange for direct intact-proteoform measurement and higher sampling scale.

### Method in Brief

```text
sparsely deposited hippocampal cells
  -> optical registration
  -> 200-µm nano-DESI liquid bridge rastered at 30 µm/s
  -> one I²MS scan/s and processed-ion chronogram
  -> cellogram peak picking / multicell filtering
  -> cell-specific STORI ion groups and neutral masses
  -> reference isotopic-envelope matching
  -> PAScore + ten-decoy cell-level FDR (q < 0.1)
  -> cell × 165-proteoform matrix
  -> merge proteoforms by gene
  -> KEGG/REACTOME GSVA
  -> top-variable pathways
  -> silhouette analysis + PAM(k=3) + PCA
  -> neuron / microglia / astrocyte interpretation
```

Dataset I contains 5,272 cells. The paper reports about 29 million verified individual ions, 22.3 million charge-assigned ions, 566 detected proteoform features and 165 identified reference proteoforms. PAScore/FDR produces an average of 86 assigned proteoforms per cell; 23 identifications receive additional top-down MS/MS support (`paper.md:53-65`).

For clustering, the 165-proteoform matrix is mapped to 147 KEGG/REACTOME pathways. The top 10% most variable pathways (15 pathways) feed PAM and PCA. The study assigns 4,927 of 5,272 cells (93%) to three groups: 3,817 neurons, 317 microglia and 793 astrocytes, with 345 cells unclassified (`paper.md:68-76`).

### Main Evidence

- **Throughput and event detection:** dataset I converts 6,116 optical features into 5,272 detected single-cell events (86%); the earlier dataset II protocol achieved about 50% (`paper.md:50-53`).
- **Proteoform-scale measurements:** aggregated spectra and collector's curves show intact-mass signals up to approximately 70 kDa and continuing proteoform discovery with more cells (Fig. 1; Extended Data Fig. 2).
- **Sparse but structured assignments:** only about 5% of all cell-proteoform candidate entries are nonzero assigned PAScores, most supported by a small number of ions (Extended Data Fig. 3). This motivates pathway aggregation.
- **Population structure:** a 15-pathway heatmap and PCA show three shifted, overlapping populations rather than perfectly separated classes (Fig. 2; Extended Data Fig. 4).
- **Biological coherence:** ARP5L is enriched in neurons; glucose-metabolism proteoforms and GFAP in astrocytes; ARF1/PP5-TPR/PSMD11-related signals in microglia (Fig. 2; Extended Data Figs. 6–10).
- **Qualitative validation:** selected optical morphologies and overall cell-type proportions agree with the cluster interpretations and prior hippocampal scRNA-seq expectations.

These results support large-scale label-free proteoform profiling and biologically coherent population discovery. They do not constitute a supervised classification benchmark: no exhaustive independent cell labels, held-out accuracy or confusion matrix are presented.

### Code-Paper Match

Overall fidelity of the acquired repository snapshot is **medium**.

- **Exact, directly verified:** optical grid occupancy modeling; gene-level complement-of-products PAScore merge; KEGG/REACTOME GSVA setup; PAM with $k=3$; PCA over pathway features.
- **Partial:** chronogram feature selection and variable-pathway filtering.
- **Not found:** charge assignment/neutral-mass reconstruction and the central PAScore/decoy/q-value implementation.

The MATLAB chronogram logic follows the paper's structure but parameters disagree across sources: Methods state 500 ions/eight scans, Extended Data Fig. 1 states 750 ions/seven scans, and the snapshot uses 800 ions/eight scans plus a five-scan decay test. The QMD implements downstream GSVA/PAM/PCA, but its `featurefilter` options do not demonstrate recovery of the exact reported 15-pathway set.

Most importantly, the repository README assigns scoring to a WPF `SingleCellApp.exe`. Neither that executable nor its C# source is present in the acquired snapshot, so PAScore, decoy generation and q-value behavior cannot be independently inspected.

### Reproducibility

**Current workspace reproducibility: 2/5 (partial).**

Positive evidence:

- the paper provides MassIVE accessions for raw and processed data;
- GitHub provenance is fixed at commit `de26509c729acfa85914fd26d8d3f9505a34935b`;
- MATLAB and Quarto/R source expose important upstream and downstream stages;
- the README describes a manual demo workflow and expected external files.

Blocking or weakening factors:

- `SingleCellApp.exe`/C# source and demo inputs are absent locally;
- MATLAB paths, filenames and thresholds are hard-coded;
- no package lockfile, tests or expected-output hashes are included;
- the QMD installs unpinned packages and depends on three external workbooks;
- the public source does not connect MATLAB feature export to the WPF `.dmt` input;
- the article and code do not provide one consistent cellogram parameter set.

Consequently, the snapshot is sufficient to understand and audit parts of the workflow, but not to regenerate the published cell × proteoform matrix end to end.

### Limitations and Open Questions

1. Per-cell proteoform coverage is sparse; pathway aggregation improves structure but reduces direct proteoform specificity in clustering.
2. PCA clusters overlap substantially, so population assignments are broad interpretations rather than clean single-cell diagnostic boundaries.
3. Total and assigned ion-depth distributions differ across inferred cell types; whether this contributes to clustering is not resolved by the presented normalization diagnostics.
4. The method depends on a reference proteoform library and IMT/homology choices, which may limit discovery of unrepresented or rare proteoforms.
5. Only three broad hippocampal cell populations are resolved; neuronal subtypes remain beyond the demonstrated depth.
6. Supplementary figures/data were not acquired as Markdown in this workspace, so supplementary-only details were not independently audited.

### Bottom Line

scPiMS demonstrates that intact-proteoform single-cell MS can reach a $10^4$-cell scale and recover biologically coherent hippocampal population structure without prior labeling or sorting. Its strongest novelty is the sampling/measurement platform and the direct proteoform readout. The current public snapshot exposes useful MATLAB and R stages, but the unavailable central scoring implementation and parameter inconsistencies prevent a full computational reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
