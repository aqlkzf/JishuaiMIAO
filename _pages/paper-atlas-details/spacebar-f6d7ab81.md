---
layout: default
permalink: /paper-atlas/spacebar-f6d7ab81/
title: "SpaceBar"
nav: false
description: "一个细胞为什么呈现某种表达状态，通常有两类来源： 内在/谱系来源：细胞从共同祖先继承了较稳定的遗传或表观遗传状态； 外在/空间来源：细胞因为处于肿瘤边缘、缺氧内部、血管附近等不同微环境而改变表达。 传统克隆追踪和成像型空间转录组很难同时测量这两件事。随机 DNA/RNA barcode 能提供很高的克隆多样性，但 seqFISH、MERFISH 一类方法依赖预先设计的探针面板，无法事先知道每个随机 barcode 的序列。"
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
      <span>Nature Methods · 2026</span>
    </div>
    <h1>SpaceBar</h1>
    <p>SpaceBar enables single-cell-resolution clone tracing with imaging-based spatial transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpaceBar 方法详解：在同一张组织切片里区分“克隆记忆”与“空间环境”

### 1. 这篇论文到底想解决什么问题？

一个细胞为什么呈现某种表达状态，通常有两类来源：

- **内在/谱系来源**：细胞从共同祖先继承了较稳定的遗传或表观遗传状态；
- **外在/空间来源**：细胞因为处于肿瘤边缘、缺氧内部、血管附近等不同微环境而改变表达。

传统克隆追踪和成像型空间转录组很难同时测量这两件事。随机 DNA/RNA barcode 能提供很高的克隆多样性，但 seqFISH、MERFISH 一类方法依赖预先设计的探针面板，无法事先知道每个随机 barcode 的序列。反过来，能够直接在原位读取的克隆标签往往多样性不足，或者需要额外的扩增、原位测序步骤。

补充说明列举了几类已有方案：Rewind（*Nature Biotechnology*, 2021）先通过测序筛选感兴趣的 barcode，再定向回看；MEMOIR、Zombie 和 PETracer 需要特殊记录阵列或额外扩增；BARseq 具有更高多样性，但原位测序更复杂、资源消耗更高，而且 barcode 检测效率低于杂交方法（Supplementary Note 1，`MOESM1_ESM.txt:17-33`）。

SpaceBar 的关键转变是：**不要让成像平台去适配未知随机 barcode，而是把 barcode 设计成成像平台本来就能测的、预先已知的 RNA 靶标。**

### 2. 核心创新：96 个已知 barcode 的组合，而不是 96 个克隆

作者设计了 96 条约 1 kb 的合成序列，将每条序列插入 GFP 的 3′ UTR，并构建成混合慢病毒文库。高 MOI 转导后，一个细胞通常会整合多个 barcode；同一个祖细胞的后代继承相同组合。

因此克隆身份不是一个单独标签，而是一个集合：

$$
B_i=\{b\mid \text{barcode }b\text{ 在细胞 }i\text{ 中被检测到}\}.
$$

96 个 barcode 本身并不意味着只能标记 96 个克隆。若每个细胞平均获得若干不同 barcode，可用的组合数近似来自 $\binom{96}{k}$，因此能够扩展到数十万甚至更多潜在身份。代价是必须保证足够高的 barcode 数量，否则不同祖细胞可能偶然获得相同组合。

补充 XLSX 直接提供了 96 条完整 barcode 序列、探针寡核苷酸和 GenePS 面板信息；`Barcode_sequences` 工作表有 96 行 barcode，`Probe oligo sequences` 给出每条 20-bp 探针的 GC、Tm 和 Gibbs 自由能。

### 3. 输入、输出与数据形状

#### 实验输入

- 96 个已知的合成 barcode RNA 靶标；
- 120 个黑色素瘤相关内源基因的成像面板；
- DAPI 核图像；
- GenePS/seqFISH 解码后的 transcript spot 坐标；
- Cellpose 生成的细胞核分割 mask；
- 体内样本还需要肿瘤区域 mask 和每个细胞的空间坐标。

#### 主要中间表示

对 $N$ 个细胞，barcode 部分可写成矩阵

$$
X^{(bc)}\in\mathbb{R}_{\ge0}^{N\times96},
$$

其中 $x_{ib}$ 是分配给细胞 $i$ 的第 $b$ 个 barcode transcript 数。内源基因部分是

$$
X^{(gene)}\in\mathbb{R}_{\ge0}^{N\times G}.
$$

论文称质量控制后 $G=113$；但源码 notebook 实际构造出 119 个 gene-like 列，这是后文需要特别注意的代码–论文差异。

#### 输出

- 每个细胞的 barcode 组合和定量 barcode 向量；
- 聚类得到的 clone ID；
- 每个基因的 clone score 与 space score；
- 经验 P 值与 Bonferroni 校正结果；
- 用于展示克隆结构、空间梯度和局部表达记忆的图。

### 4. 从图像 spot 到细胞×基因矩阵

论文的数据处理顺序是：

1. SG Analysis Program 0.6.8 对每个 ROI 的 spot 手动设阈值并解码；
2. Cellpose 根据 DAPI 分割细胞核；
3. 每个核向外扩张 10 像素，即 1.07 µm；
4. 将扩张范围内的 transcript 分配给该细胞；
5. 两个扩张核重叠时，把 spot 分给最近的细胞核；
6. 扩张范围以外的 spot 被忽略（`paper.md:160-163`）。

代码入口位于：

```text
SpatialBarcodes/extractionScripts/
1_process_to_SGobject_and_call_barcodes.py:36-108
```

它依次调用：

```text
SGobject.mask_to_objects(segmentation_file)
    → load_points(spots_file)
    → dilate_objects(10)
    → create_cell_gene_table()
    → get_cell_gene_table_df()
```

随后把核中心、扩张面积和几何对象合并到细胞表中。这个调用路径与论文 Methods 一致，属于 **Exact** 对应。

但 `SGanalysis.SGobject` 包的源码 **Not found**：本地快照只有调用，没有类内部实现。因此“重叠区域如何精确判定最近核”“mask 到 polygon 的边界规则”等细节不能从本仓库继续审计。

### 5. 第一次 clone assignment：每个 barcode 至少 3 个 transcript

对每个细胞 $i$ 和 barcode $b$，代码使用：

$$
I_{ib}=\mathbf{1}[x_{ib}\ge3].
$$

初始 clone identity 是所有 $I_{ib}=1$ 的 barcode 名称排序后拼接得到的组合。直接实现位于：

```text
1_process_to_SGobject_and_call_barcodes.py:86-108
```

这个规则很直观，但有两类不同错误：

#### 5.1 False clone：无亲缘细胞碰巧得到同一组合

barcode 太少时，碰撞概率很高。补充材料用 287 µm 作为“过远、可能不是同一真实克隆”的经验阈值，并报告：

- 只有 2 个 barcode：估计 false-clone rate 为 77%；
- 恰好 3 个 barcode：12%；
- 至少 4 个 barcode：0.3%。

所以在体外表达相似性分析中，作者要求一个 clone 至少有 4 个 barcode。

#### 5.2 Mis-assignment：真实姐妹细胞被拆成不同 clone

某个 barcode 表达低、掉失，或 spot 被邻近细胞“抢走”时，真实姐妹的二值组合会不同。Supplementary Note 3 的 Fig. 1 示例中，cell 1 同时混入自身和邻居的 barcode，单纯按出现/不出现会把它错误拆开。

这也是为什么 SpaceBar 还需要第二步定量聚类。

### 6. 定量 barcode 聚类：方法中最关键的计算步骤

先保留总 barcode spot 数至少为 10 的细胞：

$$
\sum_{b=1}^{96}x_{ib}\ge10.
$$

然后对每个细胞做行归一化：

$$
\tilde{x}_{ib}=\frac{x_{ib}}{\sum_{k=1}^{96}x_{ik}}.
$$

这样比较的是 barcode 的**相对组成**，而不是总表达强弱。两个细胞之间使用 Bray–Curtis dissimilarity：

$$
d_{ij}=\frac{\sum_b|\tilde{x}_{ib}-\tilde{x}_{jb}|}
{\sum_b(\tilde{x}_{ib}+\tilde{x}_{jb})}.
$$

接着进行 average-linkage agglomerative clustering：

- 体外样本阈值：0.2；
- 体内样本阈值：0.4。

代码在 `1_process_to_SGobject_and_call_barcodes.py:116-184` 中完整实现，属于 **Exact**。一个源码中隐藏但重要的细节是：聚类后，作者以簇内每个 barcode 的**中位数 count 是否大于 3**来重新生成 cluster-level barcode identity（lines 150-182）。论文只描述了基于相对丰度的聚类，没有明确写出这个中位数规则。

补充材料估计，聚类把 mis-assignment rate 从 14% 降到 9%。

### 7. 空间分组：不是直接算连续距离，而是逐层腐蚀肿瘤 mask

论文将细胞按距肿瘤外边缘的位置分成 25 组，每组约 18.6 µm。这个空间轴旨在近似肿瘤的外部–内部生理梯度：外部通常更富氧、更血管化，内部更缺氧、营养不足或坏死。

源码 `SpatialBarcodes/extractionScripts/2_erode_tumor.py` 的实际实现是：

1. 手工选择一个肿瘤 polygon mask；
2. 使用矩形 kernel 连续腐蚀 25 次；
3. 每次腐蚀前后 mask 的差集形成一个 ring；
4. 将细胞中心落入该差集的细胞标记为对应 `Ring`；
5. 用 ring area / outer perimeter 估计平均宽度，再用 107.11 nm/pixel 转成 µm。

也就是说，论文中的“distance from tumor edge”在代码里是**离散形态学腐蚀层**，而不是对每个细胞直接计算连续 Euclidean distance。这个区别不改变总体意图，但会影响不规则边界处的精确定义。

### 8. Clone score：真实 clone 间差异相对随机重排有多大？

clone score 的筛选比主文前面描述性分析更严格：

- 主文一般分析：至少 3 个 barcode、至少 10 个细胞，得到 149 个 clone / 11,619 个细胞；
- clone score：至少 3 个 barcode、至少 25 个细胞（`paper.md:193`；notebook code cell 5）。

对基因 $g$，先计算每个 clone $c$ 的平均表达 $\bar{x}_{gc}$，再取最大与最小 clone 均值之差：

$$
\Delta_{\mathrm{clonal},g}
=\max_c\bar{x}_{gc}-\min_c\bar{x}_{gc}.
$$

然后把细胞的 clone label 随机打乱 12,000 次。每次都重新计算同样的 max–min 差值，最后取平均作为 $\Delta_{\mathrm{scrambled},g}$。论文公式为：

$$
\mathrm{Clone}\,\mathrm{score}=
\frac{\mathrm{\varDelta clonal}}
{\mathrm{\varDelta scrambled}\,}.
$$

直观解释：

- score $\approx1$：真实 clone 分组没有比随机分组产生更大的表达范围；
- score 很大：至少存在某些 clone，其平均表达显著偏离其他 clone；
- 它不是方差解释率，也不能单独证明是遗传突变造成的，只说明表达与 clone identity 强关联。

Notebook 还计算经验 P 值：随机结果达到或超过真实差值的次数越少，P 值越小；代码使用 $(k+1)/(R+1)$ 的修正。对应实现位于：

```text
SpatialBarcodes/extractionScripts/3_calculate_clone_scores.ipynb
code cells 5, 7-9
```

### 9. Space score：同一个统计量，换成空间 ring

对基因 $g$ 和空间 ring $s$，计算 $\bar{x}_{gs}$，再定义：

$$
\Delta_{\mathrm{spatial},g}
=\max_s\bar{x}_{gs}-\min_s\bar{x}_{gs}.
$$

把细胞的 ring label 打乱 12,000 次后，得到：

$$
{\mathrm{Space}}\,\mathrm{score}=
\frac{\mathrm{\varDelta spatial}}
{\mathrm{\varDelta scrambled}\,}.
$$

只有至少检测到一个 barcode 的细胞进入 space-score 计算，以减少未转导的小鼠细胞。实现位于：

```text
SpatialBarcodes/extractionScripts/4_calculate_space_scores.ipynb
code cells 4-9
```

clone score 与 space score 的优点是使用同一统计框架，便于把“按祖先分组”和“按空间分组”的效应放在同一张图上。缺点是两者都用 max–min，容易由极端组驱动；它们也不能处理更复杂的二维空间模式，只测试作者选择的外部–内部轴。

### 10. 结果应该怎样读？

#### 10.1 体外验证：同 clone 细胞确实更相似

约 46,000 个细胞中：

- 89% 至少有一个 barcode；
- 59% 至少有三个；
- 44% 至少有四个。

对 2,465 个“至少 4 barcode、至少 2 cells”的 clone，作者对表达做 $\log(x+1)$、PCA，并在前 10 个 PC 中比较平均成对距离：

- 同 clone：2.86；
- 非克隆邻居：4.71；
- 随机细胞：4.87；
- 差异 $P<0.001$。

`IFIT2` 和 `OASL` 的姐妹细胞表达一致性也显著增强，odds ratio 分别为 4.9 和 3.5。对应 notebook 是 `plotScripts/in_vitro_sister_similarity.ipynb`，code cells 6、19-28。

#### 10.2 体内结果：空间效应总体强于克隆效应

五张肿瘤切片共测量超过 300,000 个细胞，并分配约 23,000 个 clone。论文报告，在 113 个基因中：

- 46 个具有高 space score；
- 5 个具有高 clone score；
- 判定阈值为 score 至少 2 且 Bonferroni 校正经验 $P<0.01$。

典型空间基因：

- `MITF`：靠近肿瘤外缘，在距边缘约 37 µm 处达到峰值；
- `VEGFA`：内部更高，在约 334 µm 处达到峰值，符合缺氧/坏死区域募集血管的生物学。

典型克隆基因：

- `SFRP1`：focal section 中 clone score 最高；
- clone 31 平均约 3.7 spots/cell；
- 58% 的 clone-31 细胞非零表达，而全肿瘤为 1.5%，邻居为 3.3%。

作者基于 barcode 证据对 clone 31 做了人工校正，但没有用 `SFRP1` 表达本身选择细胞。这一步在论文和 `plot_clone_space_examples.ipynb` code cells 12-19 中都明确存在。

### 11. 为什么单细胞分辨率很重要？

Extended Data Fig. 7 把 clone-31 区域模拟成 55-µm 网格。视觉上，原本穿插在其他细胞之间的 clone-31 细胞被聚合进粗网格，结果另外八个 clone 也与 `SFRP1` 呈显著空间相关。

这说明低分辨率平台容易把两种情况混淆：

```text
真实克隆模式：同一 clone 的细胞零散穿插，但共同高表达

表面空间模式：一个粗网格区域整体高表达，网格内多个 clone 都被关联
```

SpaceBar 的价值不只是“看见 barcode”，而是能在单细胞层面同时看到 clone label 和 gene spot，从而识别这种穿插结构。

### 12. 短暂表达记忆为什么可能被 clone score 漏掉？

一个体内 clone 平均约有 70 个细胞。如果某个状态只在最近分裂出的 3-5 个姐妹中短暂维持，那么整个 clone 的平均表达会被大量阴性细胞稀释。

Extended Data Fig. 8 中，`IFIT2` 高表达细胞只形成 clone 15 和 clone 72 内的小团簇，而不是覆盖整个 clone。这支持“短暂但可遗传若干代”的解释，也解释了为什么 `IFIT2` 在体外姐妹分析中显著，却不一定获得高的全-clone score。

### 13. 代码与论文的一致性

#### Exact

- 10-pixel 核扩张与 spot-to-cell 工作流：`1_process...py:36-76`；
- 每个 barcode 至少 3 transcripts：`:86-108`；
- 至少 10 barcode spots、行归一化、Bray–Curtis、average linkage、0.2/0.4 阈值：`:116-184`；
- 25 次 mask erosion 与 ring assignment：`2_erode_tumor.py:55-63,121-192`。

#### Notebook

- clone score：`3_calculate_clone_scores.ipynb` cells 5, 7-9；
- space score：`4_calculate_space_scores.ipynb` cells 4-9；
- 碰撞模拟、姐妹相似性、`SFRP1` 人工校正和图生成均有 notebook 代码。

#### Partial / Not found

最重要的差异是 113-gene QC：

1. 论文称排除 `BMP4`, `ITGA8`, `IGFBP2`, `KIT`, `NANOG`, `ROR2`, `SOX2`，剩余 113 个基因；
2. `helperScripts/tools.py:46-48` 的排除列表用 `ENSMUSG00000071361` 替代了 `IGFBP2`；
3. clone/space score notebooks 实际没有应用这个列表，而是按列名泛化选择；
4. notebook 缓存输出明确显示 `total: 119`。

因此，**公式和聚类逻辑可以复核，但产生论文最终“46 spatial / 5 clonal out of 113”统计的精确 QC 路径 Not found。**

此外，本地不能端到端运行：`SGanalysis.SGobject` 源码缺失，ROI 配置是作者机器上的 `/Users/grantkinsler/...` 绝对路径，原始 segmentation、decoded spots 和多个中间 pickle/CSV 不在工作区；论文也说明 raw data 需要向作者申请。

### 14. 如何正确理解 SpaceBar 的贡献与边界

SpaceBar 不是一个新的深度学习模型，也不是一个完整谱系树重建算法。它是一套“实验标签设计 + 成像读出 + 克隆聚类 + 置换评分”的技术平台：

- 实验端解决了随机 barcode 无法被预设计探针读取的问题；
- 计算端用多 barcode 的相对丰度修复 dropout 和错分配；
- 统计端用同构的 clone/space score 比较祖先与环境关联；
- 单细胞图像端提供了粗分辨率平台无法保留的穿插结构。

它最适合研究较稳定的细胞状态记忆，以及肿瘤、发育、再生中“谱系与位置共同作用”的问题。主要边界包括高 MOI 要求、固定标签不能记录后续分支、短暂状态会被 clone 平均稀释、多个手工分析环节，以及当前代码包不能直接复现最终 113-gene 结果。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpaceBar

**Paper:** *SpaceBar enables single-cell-resolution clone tracing with imaging-based spatial transcriptomics*
**Journal:** *Nature Methods* 23, 328–333 (2026)
**DOI:** `10.1038/s41592-025-02968-w`

### What problem does it solve?

Cell state in a tissue reflects both ancestry and local environment, but those influences are difficult to measure together. Random-barcode clone tracing provides lineage labels but imaging-based spatial transcriptomics uses predetermined probe panels and cannot readily read arbitrary barcode sequences. Earlier in-situ clone methods either provide limited diversity, require targeted follow-up after sequencing, add amplification/in-situ sequencing steps, or sacrifice single-cell resolution. SpaceBar makes the clone label itself compatible with a standard hybridization-based spatial-transcriptomics panel.

### Core idea

SpaceBar uses 96 known, approximately 1-kb synthetic RNA sequences inserted into the GFP 3′ UTR of a lentiviral vector. High-MOI transduction gives each founding cell a combination of barcodes; descendants inherit that combination. Because all sequences are predetermined, seqFISH/GenePS can detect the 96 barcode RNAs together with endogenous genes in the same tissue section.

The computational workflow is:

```text
decoded barcode/gene spots + Cellpose nuclei
    → expand nuclei by 10 pixels (1.07 µm) and assign spots
    → call a barcode when count >= 3
    → retain cells with >= 10 barcode spots
    → normalize the 96-count vector per cell
    → Bray–Curtis distance + average-linkage clustering
       (threshold 0.2 in vitro, 0.4 in vivo)
    → clone labels
    → compare gene variation across clones and across 25 tumor-depth rings
       against 12,000 label permutations
```

For each gene, the **clone score** is the max–min difference in clone means divided by the average difference after scrambling clone identity. The **space score** uses the same calculation over 25 distance-from-edge bins. High values identify expression variation stronger than expected after destroying the corresponding clone or spatial structure.

### Main evidence

- In vitro, approximately 46,000 melanoma cells were profiled; 89% had at least one barcode, 59% had at least three, and 44% had at least four.
- For 2,465 multi-cell clones with at least four barcodes, cells from the same clone were closer in top-10-PC expression space than random cells or non-clonal neighbors (mean distance 2.86 versus 4.87 and 4.71; $P<0.001$).
- Sister cells were more likely to share `IFIT2` and `OASL` expression states (odds ratios 4.9 and 3.5; both $P<0.001$).
- Across five xenograft sections, more than 300,000 cells were profiled and approximately 23,000 clones were assigned. The focal section contained approximately 67,000 cells and 3,400 clones.
- The paper reports that 46 of 113 genes had high space scores, whereas five had high clone scores. `MITF` peaked near the tumor edge and `VEGFA` in the interior; `SFRP1` showed the strongest clonal pattern in the focal section.
- Clone 31 had 3.7 `SFRP1` spots per cell and 58% non-zero expression, compared with 1.5% tumor-wide and 3.3% among neighboring cells. A simulated 55-µm grid blurred this specificity, illustrating the value of single-cell resolution.

All 10 local main/extended-data images were inspected. They visually support barcode-specific smFISH detection, combinatorial labels in single cells, reduced error after clustering, expression similarity within clones, clone structure in multiple tumors, opposing `MITF`/`VEGFA` gradients, clone-31 `SFRP1` enrichment, and small same-clone groups with transient `IFIT2` expression.

### Error controls and practical limits

Barcode multiplicity is essential. Supplementary analysis estimates a false-clone rate of 77% with two barcodes, 12% with exactly three, and 0.3% with at least four. Abundance-based clustering reduces an estimated misassignment rate from 14% to 9%. Barcode abundance is visibly nonuniform, so empirical barcode probabilities are used in collision simulations.

SpaceBar is clone tracing, not an evolving lineage recorder: it identifies descendants of a founder but does not reconstruct later branching events. It is best suited to persistent expression memory; short-lived states can be diluted when averaged across large clones. The experiments also require efficient lentiviral transduction, manual spot thresholding and threshold selection, and a custom-probe imaging platform.

### Code and reproducibility

**Reproducibility rating: 3/5.** The paper-linked repository is captured at commit `bde5a854a5115114999c464e9cbd61e4f32df6cc`. Core processing and analysis logic is inspectable:

- 10-pixel assignment, cutoff-3 barcode calls, Bray–Curtis clustering, and 0.2/0.4 thresholds are directly implemented in Python.
- Tumor-ring erosion and the clone/space permutation scores are present in Python/notebooks.
- Figure and validation notebooks cover collision estimates, in-vitro sister similarity, manual `SFRP1` curation, and plotting.

However, the snapshot is not runnable end to end without external `SGanalysis.SGObject`, raw segmentation/decoded-spot files, author-local path replacement, and intermediate pickles/CSVs. Raw data are available only upon request.

There is also a material code–paper mismatch: the paper says seven genes were removed to leave 113, but the score notebooks generically select 119 gene-like columns and do not apply the helper exclusion list; that list substitutes `ENSMUSG00000071361` for the paper-listed `IGFBP2`. The score equations are therefore well reproduced, but the exact QC path yielding the manuscript's final 113-gene counts is **Not found**.

### Bottom line

SpaceBar's novelty is the combination of a probe-addressable, high-diversity inherited label with single-cell imaging-based spatial transcriptomics. This allows clone identity and local gene expression to be measured in the same cells, making ancestry-versus-environment comparisons possible without sacrificing spatial resolution. The biological demonstration is convincing, especially for spatial `MITF`/`VEGFA` gradients and clonal `SFRP1`; the main technical caveats are barcode multiplicity, manual analysis steps, incomplete portable execution, and the unresolved 113-versus-119 gene-filtering handoff.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
