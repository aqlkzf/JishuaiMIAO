---
layout: default
permalink: /paper-atlas/array-seq-631e8194/
title: "Array-seq"
nav: false
description: "Array-seq 的核心不是提出新的机器学习模型，而是把成熟的定制寡核苷酸微阵列“改装”为大面积空间转录组芯片：先在已知坐标打印确定性的空间条形码，再通过片上延伸–连接反应补上 UMI 和 oligo(dT) 捕获端，最后用常规测序和空间分析流程得到“位置 × 基因”的表达矩阵。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Array-seq</h1>
    <p>Repurposing large-format microarrays for scalable spatial transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Array-seq 方法详解

### 一句话理解

Array-seq 的核心不是提出新的机器学习模型，而是把成熟的定制寡核苷酸微阵列“改装”为大面积空间转录组芯片：先在已知坐标打印确定性的空间条形码，再通过片上延伸–连接反应补上 UMI 和 oligo(dT) 捕获端，最后用常规测序和空间分析流程得到“位置 × 基因”的表达矩阵。

### 1. 它要解决什么问题？

测序型空间转录组通常在几个目标之间取舍：

- **面积**：能否同时放很多切片，或放下一张完整的大器官切片？
- **分辨率**：每个捕获点有多小、每平方毫米有多少点？
- **灵敏度**：单位面积能检测多少 UMI 和基因？
- **组织学兼容性**：能否在同一张切片上做 H&E？
- **可采用性与成本**：是否需要特殊仪器、复杂基底制备或预先测序定位条形码？

Visium 易用且兼容同片 H&E，但有效面积较小、成本较高。HDST、Slide-seqV2、Seq-Scope、Open-ST 等方法可以达到更高的物理分辨率，却往往需要专用基底、仪器、条形码定位步骤或较强的技术经验。Array-seq 的目标不是赢得最高分辨率，而是利用标准显微玻片和成熟微阵列制造能力，把有效面积扩展到 11.31 cm²，同时保留可预知的条形码坐标和常规病理流程。

### 2. 最关键的工程矛盾

传统微阵列探针通过 **3′ 端**固定在玻璃上；而 mRNA 捕获探针必须保留一个自由的 **3′ oligo(dT)**，用于结合 poly(A) 尾。微阵列原位合成也不适合直接加入随机 UMI。

Array-seq 的解决思路是：打印时只制造“骨架”，实验前再在玻片上组装完整捕获探针。

打印骨架为：

```text
玻璃—3′ [Anchor 1: 24 nt] [空间条形码: 12 nt] [Anchor 2: 16 nt] 5′
```

- Anchor 1 对应 Illumina read 1 引物的前 24 个碱基；
- 12-mer 空间条形码在每个 spot 上唯一，并且坐标预先已知；
- Anchor 2 使用 M13F 序列，作为连接 UMI–oligo(dT) 片段的短接口。

最终芯片有 1,068 × 912 = 974,016 个 spot；spot 直径为 30 µm，中心间距为 36.65 µm，总有效面积为 11.31 cm²。

### 3. 空间条形码怎样设计？

论文从 12-mer 序列池出发，控制 GC 含量、同聚碱基和局部碱基平衡，再要求最小 Hamming 距离至少为 2、避免自互补，最后选择 974,016 个条形码。

官方 `ArraySeq_Barcode_generation_n12.Rmd` 给出了更具体的实现：

1. `create.pool(n=12)` 生成候选池；
2. 限制任一碱基不能占到 6 个或更多；
3. 排除 `AAAA`、`CCCC` 等四连碱基，以及类似 `AAA?A` 的模式；
4. 要求 1–4、5–8、9–12 三个局部窗口中都同时含有 A/T 与 G/C；
5. `set.seed(1234)` 后抽取 640 万候选；
6. 用 `create.dnabarcodes(..., dist=2)` 保证条形码间距；
7. 排除以 `CC` 开头的序列；
8. 拼接 M13F、条形码和 partial read 1，并抽取 974,016 条探针。

需要保留一个差异：论文还写到排除了 `AC` 开头的条形码，但这份独立 Rmd 中没有看到对应过滤语句，因此不能假设代码与文字在这一点完全相同。

### 4. 如何把打印骨架变成 mRNA 捕获探针？

#### 第一步：杂交

向微阵列加入两条可溶寡核苷酸：

- 与 Anchor 1 配对的寡核苷酸；
- 5′ 磷酸化的 Anchor 2–UMI–oligo(dT)$_{30}$VN。

#### 第二步：片上延伸–连接（gap fill）

Phusion 聚合酶沿着打印模板复制空间条形码；T4 DNA ligase 把新合成的条形码与 Anchor 2–UMI–oligo(dT) 连接起来。Phusion 的低链置换活性很重要，否则可能在连接前把 Anchor 2 片段顶开。

#### 第三步：58 °C 选择性清洗

未连接的 Anchor 2–UMI–oligo(dT) 只通过 16-mer M13F 区域杂交，$T_m=50.7\ ^\circ$C；正确连接的探针与整段模板配对，平均 $T_m=71.3\ ^\circ$C。58 °C 位于两者之间，因此可以去除大部分未连接片段，同时保留完整捕获探针。凝胶图直接显示：连接后的高分子量捕获探针保留，而未连接的 Anchor 2 条带在清洗后消失。

该反应仍会产生过度延伸的 Anchor 1。作者估计它可能使理论最大 mRNA 结合容量降低约 25%，这是化学体系的真实损失，而不是可忽略的绘图伪影。

### 5. 从组织到测序文库

组织切片直接贴到 Array-seq 玻片上，同一切片完成甲醇固定、H&E 染色和扫描。随后用 pepsin 通透：人脾和小鼠嗅球为 20 min，其他组织为 15 min。

原位逆转录使用模板转换寡核苷酸生成全长 cDNA。去除组织并用 Exonuclease I 清理后，以 0.1 M KOH 从玻片洗脱 cDNA，进行单引物 PCR、tagmentation 和加索引。

测序结构为：

```text
Read 1（38 bp）: 空间条形码 1–12 + 中间锚序列 + UMI 29–38
Index（8 bp）  : 样本索引
Read 2（42 bp）: cDNA
```

### 6. 计算流程：从 FASTQ 到空间表达图

```text
R1: barcode + UMI          R2: cDNA
          \                /
           ---- STARsolo ----
           Exact 条形码匹配
           1MM_CR UMI 去重
                    |
                    v
             spot × gene 矩阵
                    |
          + 已知 Barcode,X,Y 表
                    |
                    v
       AnnData + UMI 强度 SVG/PNG
                    |
        在 Illustrator 中与 H&E 手工配准
                    |
                    v
         坐标缩放 + 组织掩膜过滤
                    |
       +------------+-------------+
       |            |             |
       v            v             v
  Leiden/DEG    CARD/RCTD     3D/GO/COMMOT
```

#### 6.1 STARsolo 计数

官方 shell 脚本与论文一致：cell barcode 位于 read 1 的 1–12 位，UMI 位于 29–38 位；条形码使用 `Exact` 白名单匹配，UMI 使用 `1MM_CR` 纠错折叠，输出 `GeneFull` 的 `matrix.mtx / features.tsv / barcodes.tsv`。

令 $C_{s,g}$ 表示 spot $s$ 上基因 $g$ 的 UMI 计数，最终核心输出是稀疏矩阵

$$
C\in\mathbb{N}^{S\times G}.
$$

#### 6.2 生成用于配准的 spot 图

`Write_images.py` 把坐标按 Barcode 合并到 AnnData 中。每个 spot 的颜色强度与总 UMI 成比例：

$$
I_s=255\frac{\sum_g C_{s,g}}{\max_j\sum_g C_{j,g}}.
$$

由此得到 SVG，再转成 PNG 与 H&E 图像对齐。

#### 6.3 H&E 配准与组织过滤

这里存在一个关键的“半自动”步骤：作者在 Illustrator 中手工对齐 spot 图和 H&E 图，并记录中心、宽度和高度。代码再将设计坐标变换为 H&E 像素坐标：

$$
x'_s=x_s\frac{W_{ST}}{\max_j x_j}+\Delta_x,
\qquad
y'_s=y_s\frac{H_{ST}}{\max_j y_j}+\Delta_y.
$$

随后将 H&E 转成灰度图，Gaussian 平滑后使用 Otsu 阈值获得组织掩膜，删除小物体、处理空腔，并仅保留落在组织像素中的 spot。可选的彩色人工掩膜还用于标记空腔、排除区域和选择区域。

#### 6.4 聚类与差异基因

论文描述的通用流程是：过滤低计数基因和 spot，归一化、对数变换、PCA、$k$NN、Leiden 聚类，再用 Scanpy 的 Wilcoxon 检验寻找 marker，并用每个 cluster 的前 15 个差异基因辅助人工组织学注释。

代码证实了流程，但参数并不统一：通用函数默认基因计数至少 20、spot 总 UMI 大于 100、2,500 个 HVG、Leiden resolution 1；multi-organ notebook 使用基因计数至少 25、spot 大于 100、5,500 个 HVG、resolution 0.98。研究者复现时必须按具体 notebook，而不能只依赖论文中的单组阈值。

#### 6.5 细胞类型、3D、功能和信号分析

- **CARD/RCTD/cell2location**：将空间矩阵与单细胞参考结合，估计每个 spot 的细胞类型比例；spot 仍是多细胞混合物。
- **3D 肾脏配准**：对相邻切片搜索平移和旋转，使组织掩膜的 Jaccard 重叠最大：

$$
J(A,B)=\frac{|A\cap B|}{|A\cup B|}.
$$

  官方 notebook 搜索 $\Delta x,\Delta y=-40,-35,\ldots,20$ 像素以及 $-7^\circ$ 到 $6^\circ$ 的旋转，再把最优变换应用到空间坐标。
- **GO 空间富集**：用 `sc.tl.score_genes` 为每个 spot 计算基因集得分，仅可视化最大得分大于 1 的集合。
- **人脾 COMMOT**：使用 CellChat 的趋化因子–受体对，距离阈值 150，方向性参数 $k=5$。箭头是基于表达与距离的计算推断，不是直接观测到的分子运动。

### 7. 结果应该怎样解读？

Array-seq 最有说服力的证据不是单个数值，而是多种空间证据相互吻合：H&E 结构、无监督 cluster、marker gene 和去卷积细胞类型在嗅球、肾脏、多器官和人脾中呈现一致的组织区域。

关键结果包括：

- 两个嗅球重复约检测 3,500 UMI 和 1,970 基因/spot，相关系数 0.986；
- 组织外 UMI 比例为 4.5%，与公开 Visium 数据的 5.4% 接近；
- 相比 Visium，spot 密度提高 8.1 倍、总 spot 数提高 216.8 倍、有效面积提高 26.7 倍；
- 8 张肾脏连续切片形成约 800 µm 深度的 3D 采样；
- 一张玻片同时分析 2 张脑、3 张肝、3 张肾切片；
- 一张完整人脾切片覆盖 750,640 个 spot，占玻片有效面积的 77%。

Visium 的单 spot UMI/基因更多，因为 spot 更大。按面积归一化后，Array-seq 与 Visium 的 UMI 灵敏度处于同一数量级，但 Array-seq 的基因数/µm²更高。这个结果说明它用“更多、更小的空间采样点”换取了更细的区域描绘，而不是在每个 spot 上捕获更多分子。

### 8. 局限与复现建议

- 30-µm spot 通常覆盖多个细胞，不是单细胞分辨率。
- 灵敏度低于若干专用高分辨率平台。
- 当前不支持多模态和 FFPE。
- H&E 配准依赖人工 Illustrator 操作。
- 人脾实验只有一个样本。
- 虽然制备成本约为 $0.75/mm²，但满载玻片需要约 50–100 亿 reads，测序仍然昂贵。
- 官方 Zenodo 代码覆盖面很广，但包含绝对路径，没有环境锁定、总工作流、测试或一键运行入口。

本工作区对代码–论文一致性的评价为 **medium**。推荐的复现方式是分阶段执行：先验证条形码 Rmd；再用对应 STARsolo shell 处理 FASTQ；修复路径并准备坐标/H&E 输入；最后运行与具体实验对应的 notebook，并逐级比较中间矩阵、spot 图、配准结果和生物学输出。不要把整个归档当成可直接执行的软件包。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Array-seq

### Problem

Spatial transcriptomics platforms face a persistent trade-off among capture area, resolution, histology compatibility, cost and ease of adoption. Visium—the commercial descendant of the original spatial transcriptomics platform published in *Science* in 2016—is broadly usable and compatible with same-section H&E, but its capture area is small and expensive. Academic high-resolution methods such as HDST (*Nature Methods*, 2019), Slide-seqV2 (*Nature Biotechnology*, 2021), Seq-Scope (*Cell*, 2021) and Open-ST (*Cell*, 2024) reduce feature size, but commonly require specialized substrates, instruments, barcode-localization procedures or expertise and are less widely deployed.

### Proposed technology

Array-seq repurposes custom Agilent oligonucleotide microarrays as large-format spatial mRNA-capture slides. Each printed spot contains a known 12-mer spatial barcode between two common anchors. Because conventional microarray probes are tethered through their 3′ ends and cannot directly carry a free 3′ oligo(dT) plus random UMI, the authors assemble the capture probe after printing:

1. hybridize an anchor-1 oligo and a phosphorylated anchor-2–UMI–oligo(dT) oligo;
2. extend across the spatial barcode and ligate the products in a “gap-fill” reaction; and
3. wash at 58 °C to remove unligated capture oligos while retaining the longer correctly assembled probe.

The resulting slide has 974,016 spots, each 30 µm in diameter with 36.65 µm center-to-center spacing, across 11.31 cm². The barcode coordinate is known from the design, avoiding a separate slide-decoding experiment. Standard glass-slide H&E imaging is retained.

### Computational workflow

Read 1 contains the spatial barcode at bases 1–12 and UMI at bases 29–38; read 2 contains cDNA. STARsolo 2.7.10a aligns read 2, matches barcodes exactly to the 974,016-barcode whitelist and collapses UMIs with `1MM_CR`. Counts and known barcode coordinates are joined in AnnData, rendered as a spot-intensity image, manually registered to H&E in Illustrator, rescaled into image pixels and filtered using tissue masks. Downstream analysis uses Scanpy normalization/PCA/neighbors/Leiden, Wilcoxon marker ranking, CARD/RCTD/cell2location deconvolution, Jaccard-based serial-section registration, GO gene-set scoring and COMMOT ligand–receptor directionality.

### Evaluation and main results

- **Mouse olfactory bulb:** two replicates yielded approximately 3,500 UMIs and 1,970 genes per spot, with Pearson correlation 0.986. Leiden clusters and marker genes recovered known tissue layers. Only 4.5% of UMIs were detected outside tissue, similar to 5.4% in a public Visium dataset.
- **Array-seq versus Visium:** Array-seq provided 8.1-fold more spots per mm², 216.8-fold more total spots and 26.7-fold more active area. Visium detected more molecules per larger spot, but area-normalized sensitivity was comparable in scale: 2.28 versus 3.10 UMIs µm⁻², while Array-seq detected 1.09 versus 0.55 genes µm⁻². Four pairs of adjacent kidney sections showed finer sampling of structures such as glomeruli and urothelium with Array-seq.
- **Three dimensions:** eight kidney sections, separated by roughly 80–120 µm over about 800 µm depth, were aligned into a coherent stack whose clusters and marker genes followed kidney anatomy.
- **Multi-tissue throughput:** eight sections—two brain, three liver and three kidney—were profiled on one slide. Spatial profiles correlated with matching whole-tissue RNA-seq at mean Pearson $r=0.794\pm0.030$.
- **Whole human organ:** one longitudinal spleen section covered 750,640 spots, or 77% of the slide. Clusters, immune markers and chemokine–receptor patterns recovered red pulp, white pulp and marginal-zone organization.
- **Platform landscape:** Array-seq has much greater active area than most sequencing-based spatial platforms and a reported preparation cost of $0.75 per mm². It is not the most sensitive or highest-resolution method. Sequencing a fully occupied slide at 5,000–10,000 reads per spot is estimated to require 5–10 billion reads and cost $3,550–$7,100.

### What is genuinely new

The main advance is not a new statistical model. It is an assay-engineering bridge between mature microarray manufacturing and next-generation sequencing: deterministic printed barcodes are converted into UMI-bearing, oligo(dT)-terminated capture probes after synthesis. This creates a very large, standard-slide-compatible surface without random bead decoding and allows the same physical format to support many sections, serial sections or a large organ section.

### Limitations

- Spots are 30 µm and commonly cover several cells; Array-seq is not single-cell resolution.
- Sensitivity per area is below several specialized high-resolution platforms.
- The current assay does not support multimodal readouts or FFPE tissue.
- H&E registration includes a manual Illustrator step.
- Cross-method sensitivity and cost comparisons combine heterogeneous public datasets and price sources.
- The whole human spleen experiment was performed once.
- Very large tissue occupancy shifts cost toward sequencing: a cheap capture surface can still generate an expensive library.

### Reproducibility

**Rating: 3/5 (moderate).** The paper's official Zenodo record (`10.5281/zenodo.10963424`) provides broad source coverage: barcode design, STARsolo commands, image-processing helpers, deconvolution scripts and notebooks for kidney, multi-organ, 3D, spleen, enrichment and benchmarking. Direct inspection found strong matches for read parsing, barcode generation, coordinate handling, CARD, 3D Jaccard alignment, GO scoring and COMMOT settings.

The archive is not turnkey. It contains machine-specific paths, no locked environment, no master workflow or tests, and manual registration geometry. QC and clustering parameters vary between the Methods, reusable helper and experiment notebooks. The standalone barcode Rmd visibly excludes `CC` prefixes but not the `AC` prefixes also described in the paper. This workspace selectively acquired all 67 non-checkpoint code files from the 15.4 GB archive, but not its bulk matrices/images. The best reproduction strategy is stage-wise with repaired paths and experiment-specific notebooks, not a one-command rerun.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
