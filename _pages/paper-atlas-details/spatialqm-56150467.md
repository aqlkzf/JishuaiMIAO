---
layout: default
permalink: /paper-atlas/spatialqm-56150467/
title: "SpatialQM"
nav: false
description: "SpatialQM 不是一个给样本打“合格/不合格”标签的模型，而是一套面向 Xenium、CosMx、MERSCOPE 等成像型空间转录组平台的多维质量度量体系：它把表达矩阵、转录本坐标、细胞分割、阴性探针和空间坐标转换为一组可解释指标，再结合组织、平台、探针面板和参考数据进行横向比较。"
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
      <span>Computational Tools</span>
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>SpatialQM</h1>
    <p>Standardized metrics for assessment and reproducibility of imaging-based spatial transcriptomics datasets</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Center-for-Spatial-OMICs/SpatialQM" target="_blank" rel="noopener noreferrer" aria-label="Open code for SpatialQM">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpatialQM 方法详解：如何系统评估成像型空间转录组数据质量

### 一句话理解

SpatialQM 不是一个给样本打“合格/不合格”标签的模型，而是一套面向 Xenium、CosMx、MERSCOPE 等成像型空间转录组平台的多维质量度量体系：它把表达矩阵、转录本坐标、细胞分割、阴性探针和空间坐标转换为一组可解释指标，再结合组织、平台、探针面板和参考数据进行横向比较。

### 1. 它要解决什么问题？

同一组织在不同空间平台、实验中心或探针面板下，可能得到很不一样的转录本数、背景噪声、细胞边界和细胞类型结果。造成差异的因素至少包括：

- 平台化学体系与检测灵敏度；
- 组织类型、病理状态和切片面积；
- 探针面板大小以及是否适合目标组织；
- 阴性探针设计；
- 细胞/细胞核分割方式；
- 样本制备、运输、成像和数据处理流程；
- 是否有技术重复、跨中心重复和匹配的单细胞参考。

论文指出，此前的比较研究虽然奠定了基础，但常见问题是样本少、组织范围窄、缺少重复或缺少匹配的单细胞参考，且很少在统一流程下做多中心比较（`paper.md:18-24`）。例如 Hartman 与 Satija 的平台比较发表于 *eLife* 2024，Cook 等的成像平台比较发表于 *bioRxiv* 2023，Rademacher 等的肿瘤切片技术比较发表于 *Genome Biology* 2025；SpatialQM 试图把这些零散比较推进到标准化、多中心和可复用的软件层面（`paper.md:556-562`）。

### 2. 论文的整体方案

论文实际上提供了三个相互配合的部分：

1. **Spatial Touchstone（ST）数据集**：来自多个中心、六类正常或肿瘤 FFPE 组织的受控数据，连续切片在 Xenium 和 CosMx 上测量。
2. **SpatialQM R 包**：本地读取平台文件并计算质量指标。
3. **Spatial Touchstone Portal（STP）**：把用户样本放入 ST 与公开数据的参考分布中比较。

核心思路可以概括为：

```text
平台原始/导出文件
  ├─ 细胞×基因表达矩阵
  ├─ 转录本级坐标与细胞归属
  ├─ 细胞面积、核内重叠、空间坐标
  └─ 阴性/空白探针
          |
          v
统一的样本表示（文件表或 Seurat 对象）
          |
          v
技术质量指标：丰度、背景、分割、覆盖度、分布复杂度
          |
          +--------------------+
          |                    |
          v                    v
跨样本/跨平台复现性       生物学有效性验证
标准化、PCA、Moran's I    参考相关、InSituType、RCTD
          |                    |
          +----------+---------+
                     v
      在组织/平台/面板背景下解释质量，而不是硬阈值判定
```

论文明确强调，这些指标是帮助排查实验、组织质量、仪器和探针设计问题的基础框架，不是永远固定的阈值（`paper.md:229-235`）。

### 3. 输入和输出

#### 3.1 最基本的输入

对一个样本，SpatialQM 通常需要：

- 表达矩阵 $X\in\mathbb{N}_0^{G\times C}$：$G$ 个目标基因，$C$ 个分割细胞；
- 转录本表：每个分子的基因、空间坐标、细胞归属，必要时还有是否位于细胞核；
- 细胞元数据：细胞面积、平台提供的计数和坐标；
- 阴性探针矩阵 $N\in\mathbb{N}_0^{K\times C}$；
- 平台类型；
- 可选的单细胞/单核参考，用于细胞类型注释和纯度验证。

代码中的文件批处理表要求 `sample_id`、`platform`、`expMat`、`tx_file`、`cell_meta` 五列（`vignettes/spatialqm-qc-workflow.Rmd:53-66`；`R/coercion-input.R:75-93`）。`readSpatial()` 也可以直接读取 Xenium、CosMx 或 MERSCOPE 输出并构建带有平台、路径、细胞元数据和组织坐标的 Seurat 对象（`R/utils.R:343-515`）。

#### 3.2 输出是什么？

输出不是一个总分，而是一组互补指标：

- 丰度/分割：TPC、TPA、TPN、FTC、MECR；
- 背景/特异性：specificityFDR、SNR、dynamic range；
- 矩阵分布：sparsity、entropy、complexity；
- 空间复现性：Moran's *I*；
- 生物学验证：细胞类型预测、参考相关性、RCTD 权重与纯度。

### 4. 技术质量指标逐项解释

#### 4.1 TPC：每个细胞平均检测到多少转录本

论文把 TPC 定义为按探针面板大小归一化的每细胞平均转录本数（`paper.md:372-375`）：

$$
\mathrm{TPC}_{\mathrm{norm}}
=\frac{1}{G}\frac{1}{C}\sum_{c=1}^{C}\sum_{g=1}^{G}X_{gc}.
$$

它反映总体灵敏度，但不能单独代表质量。扩大细胞边界也会提高 TPC，因为更多邻近分子被分到细胞里。

#### 4.2 TPA：单位细胞面积内的转录本密度

若 $a_c$ 是细胞 $c$ 的面积，则论文描述的归一化 TPA 可写为：

$$
\mathrm{TPA}_{\mathrm{norm}}
=\frac{1}{G}\frac{1}{C}\sum_{c=1}^{C}
\frac{\sum_g X_{gc}}{a_c}.
$$

TPA 用来减弱细胞大小差异的影响，但仍依赖细胞分割是否正确（`paper.md:378-381`）。

#### 4.3 TPN：每个细胞核中的转录本数

TPN 统计落在核分割掩膜内、且已分配给细胞的非控制转录本，再除以细胞数（`paper.md:384-387`）。由于 DAPI 核分割通常比完整细胞膜分割稳定，TPN 可以作为对 TPC/TPA 的补充；但高密度核区域仍可能产生边界误差。

#### 4.4 FTC：有多少转录本被分到细胞中

$$
\mathrm{FTC}=\frac{n_{\mathrm{assigned}}}{n_{\mathrm{all}}}.
$$

FTC 高表示大部分分子被细胞分割吸收，但它不保证分配给了正确的细胞。把边界扩得过大可能同时提高 FTC 和错误归属。

#### 4.5 MECR：互斥标记是否被错误地分到同一细胞

MECR 检查本应属于不同细胞区室/类型的标记对是否在同一细胞中共同出现。数值越低，一般说明分割后的转录谱越纯（`paper.md:426-429`）。

它的局限很明显：不同组织需要不同标记集合。代码使用固定的上皮、免疫、内皮、成纤维和肌细胞标记表，并对跨类型标记对计算共同表达率（`R/utils_update_final.R:1729-1826`）；因此论文也提醒 MECR 可能无法稳定泛化到所有组织（`paper.md:217-220`）。

### 5. 背景噪声与特异性

#### 5.1 specificityFDR

论文给出每个基因 $i$ 的公式：

$$
{\rm FDR}_{i}=
\frac{\sum \mathrm{NonSpecific}}
{\sum {\rm Probe}_{i}+\sum \mathrm{NonSpecific}}
\times
\frac{n{\rm Probe}}{n\mathrm{NonSpecific}}
\times \mathrm{SF}.
$$

其中 $mathrm{SF}=0.01$，最后对基因取平均（`paper.md:390-400`）。直觉上，阴性探针相对于真实探针越少，specificityFDR 越低，特异性越好。

#### 5.2 SNR

论文的印刷公式为：

$$
\mathrm{SNR}=\left[
\log_{10}\frac{\sum \exp\mathrm{Gene}+0.1}{n\mathrm{Genes}}
-\log_{10}\frac{\sum \exp\mathrm{Neg}+0.1}{n\mathrm{Neg}}
\right]\frac{1}{n\mathrm{Genes}}.
$$

正文同时把它解释为每个基因平均表达与阴性探针平均表达的对数差（`paper.md:402-411`）。数值越高，真实信号与背景越容易区分。

#### 5.3 Dynamic range

Dynamic range 比较最强基因的平均信号与阴性探针平均信号：

$$
\mathrm{DynamicRange}
=\log_{10}(\max_g\bar X_g)
-\log_{10}(\operatorname{mean}_k\bar N_k).
$$

值为 3 可解释为大约 $10^3$ 倍的信号差距。这个公式与本地代码的直接实现一致（`R/utils_update_final.R:1523-1604`）。

### 6. 覆盖度、熵和复杂度

- **Sparsity**：表达矩阵中零值所占比例。它既受检测灵敏度影响，也强烈受面板是否适合该组织影响。
- **Entropy**：论文称用 BioQC 计算 Shannon entropy（`paper.md:438-447`）。论文印刷公式把 $P(x)$、$x_i$ 和标准 Shannon 形式混在一起，符号并不严谨；本地代码的确定行为只是直接调用 `BioQC::entropy`。
- **Complexity**：先按基因总计数从高到低排序，找出累计达到总计数 50% 所需的最少基因数，再除以有效面板大小。值越小，说明少数高表达基因越主导样本。

### 7. 如何评价复现性？

SpatialQM 不是只比较两个重复样本的相关系数，而是组合三类证据：

1. **多指标标准化与 PCA**：把每个样本的技术指标缩放后做 PCA。论文报告 PC1 解释 34.39% 方差，Xenium 与 CosMx 明显分离，说明平台是主要变异来源之一（`paper.md:92-95`）。
2. **Moran's *I***：对跨平台和样本共同的基因计算空间自相关。论文的乳腺癌比较使用 203 个共同基因（`paper.md:115`）。本地代码会进行 log normalization，构建 $k=20$ 的逆距离近邻图，然后调用 Voyager（`R/utils_update_final.R:1850-1973`）。
3. **连续切片/跨中心相关性**：论文报告同中心重复的平均表达相关可达 $r=1.00$，跨中心相邻切片通常高于 0.95，平均 $r=0.97$（`paper.md:118`）。

直接查看图 3 还能看到一个更细的结论：CosMx 与 Xenium 的 Moran's *I* 呈正相关，图中标注 $r=0.77$，但多数点位于 $y=x$ 上方，因此是“相关”而不是“一致相等”（`figure_analysis.md`）。

### 8. 如何连接到生物学有效性？

#### 8.1 与 snPATHO-seq 参考相关

论文用匹配的 FFPE 单核 RNA 测序作为参考，但明确说明它不是绝对真值（`paper.md:135-144`）。报告的总体 Spearman 相关为：

- Xenium：0.78；
- CosMx：0.60，且不同样本间波动更大。

#### 8.2 InSituType 细胞类型注释

代码从参考对象构建伪 bulk 细胞类型表达谱，过滤总转录本数不超过 10 的空间细胞，调用 `insitutypeML`，并把结果写入 `celltype_pred`（`R/utils.R:626-648`）。阴性探针均值参与背景建模。

#### 8.3 RCTD 检查细胞谱是否“混合”

RCTD 把一个空间细胞表示为多个参考细胞类型的混合。若最大权重较低，可能意味着边界内混入多个细胞的转录本，也可能是噪声导致与参考不匹配。代码在过滤低计数细胞后运行 full-mode RCTD，并把每行权重归一化（`R/utils.R:2157-2190`）。

#### 8.4 分割策略的实验证据

论文比较核扩张、形态学多模态分割和 Proseg。随着核扩张距离增大，TPC 上升，但 MECR 和混合程度也上升。Proseg 的报告结果为 MECR 0.029、最大 RCTD 权重中位数 0.97，并比多模态分割获得 1.7 倍 TPC（128.3 对 74.6）（`paper.md:147-153`）。

这说明“检测到更多分子”与“得到更纯的细胞表达谱”不是同一个目标，必须联合看多个指标。

### 9. 图像证据告诉我们什么？

五张主图的直接读取支持以下结论：

- 图 1：ST 的多项指标分布通常比 PUB 更集中，但平台和组织差异仍然明显。
- 图 2：不同样本在不同指标上各有高低，没有一个指标能把所有样本简单排序。
- 图 3：跨平台空间自相关相关但不完全一致；多个前列腺切片保留了相似的大尺度空间结构。
- 图 4：Xenium 与 CosMx 都能保留粗粒度组织结构，但 Xenium 在示例中的 EPCAM/ACTA2 信号和转录邻域纯度明显更强；粗略细胞类型比例相似并不代表细粒度质量相同。
- 图 5：蛋白数据也表现出组织依赖的质量分布，RNA 与蛋白可在共享嵌入中部分对齐。

图 3 还存在一个未解决的标签问题：本地图像把 e(i–ii) 标为前列腺癌，而论文图注称其为乳腺癌（`figure_analysis.md`）。

### 10. 论文方法与本地代码并非完全一致

直接源码核对得到的总体保真度为 **medium**：

| 指标/模块 | 论文描述 | 本地代码行为 | 结论 |
|---|---|---|---|
| TPC/TPA | 按面板大小归一化 | 函数只计算每细胞或每面积均值 | Partial；需外部归一化 |
| specificityFDR | 逐基因 FDR 后取平均 | 聚合所有目标计数得到 global FDR | Partial |
| SNR | 印刷聚合公式，文字偏逐基因 | 平均逐基因对数差，文件路径还有向量长度风险 | Partial |
| Dynamic range | 最大目标均值与负探针均值的对数差 | 直接实现 | Exact |
| FTC | 已分配转录本比例 | Xenium/CosMx 直接实现 | Exact |
| Sparsity | 零值比例 | `coop::sparsity` | Exact |
| Entropy | BioQC Shannon entropy | `BioQC::entropy` | Exact（库调用层面） |
| Complexity | 达到 50% 总计数的最少基因数并归一化 | 两个重复源码文件的排序行为不同 | Partial/歧义 |

特别需要注意：`R/utils.R` 与 `R/utils_update_final.R` 重复定义了同名导出函数，而且实现有实质差异。后者还包含批处理参数传递和 `PanelSize` 调度问题。现有测试没有数值级回归断言，vignette 代码块也设置为不执行。因此，本地证据能较好支持“指标概念与大部分函数存在”，但不能完整证明论文中全部数值可由该提交端到端复现。

### 11. 复现性结论

**综合评分：3/5。**

优点：代码公开、R 包结构完整、大多数转录组 QC 指标有直接函数、论文提供 GEO/Zenodo/source-data 链接。

缺口：

- 本地没有论文补充材料、source-data 表、冻结的队列输入或精确的 203 基因列表；
- 没有生成图 1–5 和全部队列统计的脚本；
- 蛋白 FPC/meanSNR 与 MaxFuse 分析代码 **Not found**；
- 重复函数定义使实际执行路径存在歧义；
- 缺少指标数值回归测试和可直接运行的示例数据。

因此，SpatialQM 当前最可靠的使用方式是：把它作为透明、可检查的多指标比较工具，结合组织、平台、面板和分割背景解释结果；不要把任何一个指标或当前参考分布当作永久的通用质量阈值。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpatialQM: standardized metrics for imaging-based spatial transcriptomics

### Problem

Imaging-based spatial transcriptomics datasets are difficult to compare because measured quality depends on platform chemistry, panel size, tissue, field of view, sample handling and cell segmentation. Previous comparisons—including Hartman and Satija (*eLife*, 2024), Cook et al. (*bioRxiv*, 2023) and Rademacher et al. (*Genome Biology*, 2025)—provided important benchmarks, but the paper argues that the broader literature often used few samples, restricted tissues, no replicates or no matched single-cell reference and lacked controlled multi-site processing (`paper.md:18-24`, `:556-562`).

### What the paper introduces

The study combines three linked resources:

- **Spatial Touchstone (ST):** a controlled multi-site, multi-platform dataset generated from serial FFPE sections across six normal/cancer tissue types.
- **SpatialQM:** an open-source R package that computes technical, reproducibility and biological quality metrics from Xenium, CosMx and MERSCOPE-style inputs.
- **Spatial Touchstone Portal (STP):** a web comparison layer spanning 254 ST and public profiles, intended to contextualize user samples rather than impose one universal threshold.

The central contribution is a QC framework, not a classifier. It produces a profile containing abundance/segmentation metrics (TPC, TPA, TPN, FTC, MECR), background/specificity metrics (specificityFDR, SNR, dynamic range), distribution metrics (sparsity, entropy, complexity) and spatial/reproducibility measurements such as Moran's *I*. Matched snPATHO-seq references then connect technical quality with cell annotation, expression correlation and RCTD-derived purity.

### Main evidence

- The controlled ST cohort contained 77 spatial profiles within a larger portal of 254 profiles. Resource totals are internally inconsistent: the abstract reports approximately 33 million cells and approximately 7 billion high-quality transcripts, while the Results later state approximately 13.833 million accessible cells and approximately 2.3 billion transcripts (`paper.md:12`, `:24-33`).
- Scaled technical metrics separated platforms strongly: PC1 explained 34.39% of variance, with Xenium and CosMx visibly distinct (`paper.md:92-95`).
- Serial sections processed within one institution had reported mean-expression correlations of $r=1.00$ for the evaluated cases, and independent-site sections typically exceeded 0.95 (mean $r=0.97$) (`paper.md:118`).
- Against matched snPATHO-seq, the paper reports overall Spearman correlations of 0.78 for Xenium and 0.60 for CosMx; the latter showed more variable cell-type-level agreement (`paper.md:135-141`).
- Segmentation quality affected downstream biology: Proseg achieved a reported MECR of 0.029, median dominant RCTD weight of 0.97 and 1.7-fold more TPC than multimodal segmentation (`paper.md:147-153`).
- Direct figure inspection supports the same qualitative conclusion: broad tissue organization can remain recognizable while marker sensitivity and transcriptional purity differ substantially, particularly in the Xenium/CosMx prostate comparison (`figure_analysis.md`).

### Interpretation and limitations

SpatialQM is most useful as a comparative diagnostic panel. The paper itself cautions that FTC/TPC depend on segmentation, site, tissue and panel; sparsity and entropy are panel-sensitive; and MECR may not generalize across tissues (`paper.md:211-229`). The ST-versus-PUB comparison is also confounded by differing cohort composition, and centralized tissue sectioning reduces the amount of pre-analytical inter-site variability tested.

The paper's metric equations are not uniformly mirrored by the acquired code. Direct source review found **medium** code-paper fidelity: dynamic range, Xenium/CosMx FTC, sparsity and the BioQC entropy call match directly, while TPC/TPA omit paper-described panel normalization; specificityFDR is implemented as a global aggregate rather than a mean of gene-wise FDRs; and SNR, MECR, TPN and complexity have partial or ambiguous correspondence. Two R files redefine the same exported functions with meaningful differences (`doc_code.md`).

### Reproducibility assessment: 3/5

Strengths:

- open GitHub snapshot with package metadata, exported R functions, documentation and input workflows;
- public data links to GEO, Zenodo and paper source data (`paper.md:528-537`);
- direct implementations for most transcriptomic QC concepts.

Gaps:

- no local frozen cohort inputs, exact 203-gene list, source-data workbooks or scripts reproducing Figs. 1-5;
- spatial-proteomics FPC/meanSNR and MaxFuse analysis code **Not found** in the acquired repository;
- vignette chunks are non-executing and numerical metric regression tests are absent;
- duplicate/conflicting R definitions make the exact package execution path ambiguous;
- supplementary material was not acquired as Markdown and was not used as evidence.

Overall, the paper provides a valuable vocabulary and reference framework for spatial-transcriptomics QC, but the strongest reproducible unit in the local evidence is the reusable metric package—not the complete end-to-end reproduction of the published cohort analysis.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
