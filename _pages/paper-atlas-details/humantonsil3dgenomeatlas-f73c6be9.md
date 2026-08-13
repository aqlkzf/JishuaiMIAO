---
layout: default
permalink: /paper-atlas/humantonsil3dgenomeatlas-f73c6be9/
title: "HumanTonsil3DGenomeAtlas"
nav: false
wide: true
description: "体细胞高频突变（somatic hypermutation, SHM）通过 AID 在免疫球蛋白基因中引入点突变，是抗体亲和力成熟的基础。但 AID 也可能误伤其他基因，造成致癌突变和染色体易位。已有研究知道 SHM 与转录、增强子、拓扑关联结构域（TAD）和染色质接触有关，却仍有两个关键缺口： 在真实的人类生发中心组织中，从核内径向位置、染色体区室、TAD 到局部环等多个尺度，三维基因组结构如何共同影响 SHM 易感性？"
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
      <span>Science · 2026</span>
    </div>
    <h1>HumanTonsil3DGenomeAtlas</h1>
    <p>A 3D genome atlas of human tonsil and the role of loop extrusion in B cell somatic hypermutation</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1126/science.adw4243" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for HumanTonsil3DGenomeAtlas">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Yyx2626/HTGTS_related" target="_blank" rel="noopener noreferrer" aria-label="Open code for HumanTonsil3DGenomeAtlas">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 人扁桃体三维基因组图谱与 B 细胞体细胞高频突变中的环挤出机制

### 这篇论文要解决什么问题？

体细胞高频突变（somatic hypermutation, SHM）通过 AID 在免疫球蛋白基因中引入点突变，是抗体亲和力成熟的基础。但 AID 也可能误伤其他基因，造成致癌突变和染色体易位。已有研究知道 SHM 与转录、增强子、拓扑关联结构域（TAD）和染色质接触有关，却仍有两个关键缺口：

1. 在真实的人类生发中心组织中，从核内径向位置、染色体区室、TAD 到局部环等多个尺度，三维基因组结构如何共同影响 SHM 易感性？
2. 这些结构只是与 SHM 相关，还是由 cohesin 驱动的环挤出对 SHM 具有因果必要性？

论文在引言中明确指出，多尺度 3D 基因组与 SHM 靶向之间的关系此前并不清楚，直接干预环挤出机器是区分相关性和因果性的关键（`paper.md:15-21,50-56`）。

### 为什么单一已有方法不够？

- 单细胞 Hi-C 能提供大范围接触图，但细胞解离后丢失了组织空间位置，也不能直接给出绝对的三维坐标。
- 染色质示踪能测量位点的三维位置并保留组织结构，但只能覆盖预先选择的位点。
- MERFISH 能在组织中同时测量大量 RNA，却不能单独回答染色质折叠问题。
- 既往 hot/cold TAD 报告给出了 SHM 易感性的关联，但尚未证明 cohesin 是否必需。

因此，论文把 Droplet Hi-C 与 MINA（染色质示踪 + RNA MERFISH/smFISH + 蛋白/边界染色）组合起来，再用 RAD21 急性降解做时间分辨的因果实验（`paper.md:21,53-56,65-76,128-162`）。转换后的论文 Markdown 没有保留完整参考文献条目，所以无法可靠补充这些既有方法的期刊和年份。

### 整体设计：先建图谱，再做因果干预

```text
原代人扁桃体
  ├─ 单细胞解离
  │   └─ Droplet Hi-C
  │       ├─ 基因体接触 -> scGAD 矩阵 -> 细胞类型/状态
  │       ├─ 100-kb A/B 区室
  │       └─ 10-kb 群体染色质环
  │
  └─ 8 μm 冷冻切片
      └─ MINA
          ├─ MERFISH/smFISH -> RNA 与细胞身份
          ├─ CD35/WGA/DAPI -> 生发中心分区、细胞边界和细胞核
          └─ 染色质示踪 -> 单细胞三维位点坐标
              ├─ 径向位置、压缩、异质性、demixing
              └─ hot/cold/filler 位点间距离

RAD21-degron RASH-1C + 可诱导 AID
  └─ dTAGV-1 急性降解 RAD21
      ├─ Mut-Seq：SHM 频率
      ├─ 精细示踪 + 3C-HTGTS：IGH/IGL 架构
      ├─ Pol II CUT&RUN + TT-TimeLapse-seq：转录
      └─ AID CUT&RUN：AID 占据
          -> 比较不同读出的时间顺序
```

### 第一部分：构建人扁桃体单细胞 3D 基因组图谱

#### 1. 设计成像靶点

全基因组染色质示踪包含 1151 个目标区域：49 个既往定义的 SHM-hot TAD、97 个 SHM-cold TAD 和 1005 个均匀分布的 filler 位点。每个目标用 50-bit、Hamming distance 2、Hamming weight 2 的编码标记，并以最多 400 条探针覆盖中心 100 kb（`paper.md:195`）。

RNA 面板包含 456 个基因，其中 447 个用 MERFISH、9 个用顺序 smFISH。精细染色质示踪则以连续 10-kb bin 覆盖工程化 RASH-1 的 *IGH* 和 *IGL* 区域（`paper.md:198-201`）。

#### 2. Droplet Hi-C 分支

论文对四个生物学重复、两个供体进行 Droplet Hi-C，最终得到 12,308 个高质量细胞，中位数为每细胞 145,950 对不同接触（`paper.md:65,258`）。计算步骤为：

1. `cellranger-atac mkfastq` 拆分数据；Bowtie 匹配 10x barcode；HiCTools 回写 barcode。
2. Trim Galore 去接头和低质量序列，BWA-MEM2 比对，SAMtools 转换格式。
3. Pairtools 解析、排序和去重复，自动肘点法筛选高质量细胞核（`paper.md:387-390`）。
4. 按 barcode 拆成单细胞 `.pairs`，转为 5-kb `.cool` 和 BED。
5. 从基因体内部接触构建 scGAD score × cell 矩阵。
6. PCA、UMAP、对称化 *k*-NN 图和 Louvain 聚类先分出 T/B 细胞；随后把 B 细胞投影到公开的扁桃体 scRNA-seq 参考空间，用 Harmony 和 *k*-NN 转移 NBC、MBC、GCBC、PC 标签（`paper.md:393-396`）。

scGAD 的完整数学定义在当前论文 Markdown 中 **Not found**；论文引用了既有方法，只描述了矩阵构建和下游聚类。

#### 3. MINA 成像分支

MINA 在同一张组织切片上整合染色质示踪、RNA MERFISH、顺序 smFISH、CD35、WGA 和 DAPI。五个重复来自三个供体（`paper.md:222-249`）。

全基因组染色质示踪先校正颜色偏移和样品漂移，再分割细胞并拟合 DNA 焦点三维坐标。有效焦点对需要匹配合法 barcode 且距离不超过 500 nm。算法根据强度、焦点间距离和到染色体领地中心的距离迭代连接轨迹，直到超过 99% 的焦点对不再变化，或 10 轮后超过 97% 不再变化（`paper.md:336-339`）。

MERFISH 把每个像素跨成像轮次的信号组成向量，单位化后与合法编码比较；最近编码距离阈值为 0.65。根据焦点面积、编码距离和信号幅度自适应筛选，使最终错误率低于 5%（`paper.md:348-351`）。

细胞注释综合 Seurat v5 聚类、AUCell/irGSEA marker 富集、经典 marker、组织坐标和 CD35 染色。这样不仅能区分主要免疫细胞，还能在组织中区分生发中心暗区（DZ）、亮区（LZ）和 mantle zone（`paper.md:354-357`）。

#### 4. 从坐标和接触图提取哪些量？

##### 径向分数

设细胞 $c$ 中位点 $\ell$ 的三维坐标为 $\mathbf{x}_{c\ell}$，所有已检测位点的质心为

$$
\bar{\mathbf{x}}_c=\frac{1}{|L_c|}\sum_{k\in L_c}\mathbf{x}_{ck}.
$$

论文的径向分数可写为

$$
r_{c\ell}=
\frac{\|\mathbf{x}_{c\ell}-\bar{\mathbf{x}}_c\|_2}
{\frac{1}{|L_c|}\sum_{k\in L_c}\|\mathbf{x}_{ck}-\bar{\mathbf{x}}_c\|_2}.
$$

$r$ 越大表示越靠近核周边（`paper.md:366-369`）。这是对论文文字定义的公式化，不是论文编号公式。

##### 染色体 demixing 分数

对某一细胞状态和染色体，把所有位点对的平均空间距离记为 $\{\bar d_p\}$：

$$
D=\frac{\operatorname{SD}_p(\bar d_p)}{\operatorname{Mean}_p(\bar d_p)}.
$$

论文用这一类似变异系数的量描述长程染色质混合程度（`paper.md:372-375`）。

##### 去除基因组距离影响后的空间距离

同一染色体上，先拟合空间距离随基因组距离变化的幂律：

$$
d^{exp}_{ij}=a_h|g_i-g_j|^{b_h},
\qquad
d^{norm}_{ij}=\frac{d^{obs}_{ij}}{d^{exp}_{ij}}.
$$

跨染色体位点对则除以相应染色体对的平均距离（`paper.md:378-381`）。这样比较 hot/cold TAD 时，不会简单地把“基因组上离得近”误认为“三维中更偏好聚集”。

##### A/B 区室与染色质环

100-kb 接触矩阵先做 Vanilla Coverage 归一化，再除以全基因组距离衰减期望：

$$
O/E_{ij}=\frac{C^{VC}_{ij}}{\widehat C(|g_i-g_j|)}.
$$

每条染色体的 O/E Pearson 相关矩阵做 PCA，PC1 方向按 CpG 密度校正，使正值对应活跃 A 区室（`paper.md:399-402`）。10-kb 环由 scHiCluster 的改进 SnapHiC 流程完成单细胞插补、背景建模、按细胞群聚合和 BEDPE 输出（`paper.md:405-408`）。

#### 5. 图谱得到什么结论？

- 大多数 A/B 区室跨细胞类型稳定，但仍有 3874 个 100-kb bin 呈细胞类型差异（`paper.md:85`）。
- 相比宏观区室，GAD 和局部增强子-启动子接触更贴近谱系决定基因的表达变化；例如 PC 中 *PRDM1* 接触明显增强（`paper.md:93-96`）。
- cold TAD 彼此的归一化距离更小、径向分数更低，说明它们更倾向聚集且更靠核内部；这一特征在 SHM 激活前已大体存在（`paper.md:114-125`）。
- hot TAD 在 GCBC 中具有更高 GAD，且其基因富集生发中心和 SHM 相关功能（`paper.md:125`）。

论文解释是：大尺度径向位置预先设置了易感背景，而局部接触和转录状态进一步决定 AID 是否高效作用。核内部位置可能让 cold TAD 远离核孔和 AID 进入/输出通道，但这一核孔机制仍属于解释性模型，并非本文直接操纵验证的因果结论（`paper.md:122,180`）。

### 第二部分：急性降解 RAD21，检验 cohesin 是否必需

#### 1. 构建干预系统

作者在 RASH-1 细胞的 RAD21 C 端加入 dTAG 降解标签。doxycycline 诱导高活性 AID7.3，使 GFP reporter、*IGH-V* 和 *IGL-V* 在短时间内积累可测 SHM；dTAGV-1 则快速清除 RAD21（`paper.md:131`）。

为了准确比对，作者构建了 RASH-1 专用参考基因组，其中包含 V(D)J 重排后的 *IGH*/*IGL*、AID7.3 插入片段和位于 *IGH-V* 上游约 38 kb 的 GFP reporter（`paper.md:417-420`）。

#### 2. 先看功能终点：SHM 是否还发生？

Mut-Seq 合并 paired-end reads，要求重叠至少 10 bp、错配率不超过 8%；只保留 mapping quality ≥60、base quality ≥30 的变异，并识别 AID 偏好的 WRC 位点（`paper.md:423-426`）。

结果非常直接：RAD21 降解后，三个主要靶点的突变积累几乎降到不诱导 AID 的背景；在对照细胞中 6 小时后突变持续上升，而 RAD21 缺失细胞基本不再积累（`paper.md:139`）。因此，“RAD21 对 SHM 必需”是这篇论文最强的因果结论。

#### 3. 再问 SHM 消失的近端原因

作者把多个读出的时间过程对齐：

| 读出 | 早期变化 | 晚期变化 | 结论边界 |
|---|---|---|---|
| SHM | 最早可检测的 6–12 h 窗口已近乎消失 | 持续受抑 | RAD21 对 SHM 必需 |
| 染色质结构 | 某些结构 2 h 内消失；关键增强子接触仍保留 | 逐步崩解 | 完全丢失增强子-启动子接触不是唯一解释 |
| 新生转录 | 2 h 基本保留；6 h 多数下降小于 2 倍 | 12 h 仍有明显信号 | 立即关闭转录不能解释早期 SHM 消失 |
| AID 结合 | 6 h 通常只中度下降 | 18 h 严重下降，部分接近背景 | cohesin 支持长期 AID 招募 |

直接依据为 `paper.md:139,148-162,183`。

关键推理不是“某一条环消失就关闭 SHM”，而是 cohesin 同时维持局部结构、转录动力学、AID 占据以及可能未测量的过程。多个因素共同形成许可状态；破坏整体状态后，SHM 可以在任一单项测量完全消失之前停止。

### 3C-HTGTS：论文与代码真正对应到哪里？

论文明确写到：3C-HTGTS 去除 bait 附近自连接背景，再按每个样本的有效 junction 数做 per-million 归一化，并直接链接当前 GitHub 子目录（`paper.md:429-432`）。

代码 `yyx_normalize_3CHTGTS_tlx.20240131.pl` 的行为可以直接验证：

1. 接收 signal 区间、artifact 区间和目标计数；默认目标为 1,000,000（代码 `:10-27,40-56`）。
2. 统计 total、signal、artifact 和 signal-minus-artifact junction（`:95-108`）。
3. 计算

$$
s=\frac{N_{target}}{N_{signal-artifact}},
$$

并把 bedGraph 信号乘以 $s$（`:118-179`）。

这是一个 **Exact 的算法/接口匹配**，但不是运行证据。 4I/J 映射。

`normalizeTLX_specific.py` 固定随机种子 `1234567`，把每个 TLX 精确下采样到指定行数（代码 `:6-46`）。它的行为是直接可验证的，但论文只写了 per-million scaling，没有说明研究样本使用了固定行数下采样，所以这里只能标为 **Inferred**。

CATG 位点折叠、局部 Poisson 峰调用和区间注释脚本同样是源代码中存在的静态工具链，但论文没有证明它们生成了任何报告结果，应保留 **Not found**，不能从文件名或静态调用路径推断实际运行。

### *IGH* “curl” 结构

*IGH* 空间距离矩阵中出现一条平行于主对角线的低距离带，连接重复形成的 *3′RR1* 和 *3′RR2* 超级增强子。作者用更严格的竞争性探针、独立 Hi-C 图样和具有方向预测的 3C-HTGTS 梯度进行交叉支持，认为两个区域倾向平行排列（`paper.md:165-174`）。

但论文也明确承认：curl 的生物学功能和形成机制仍未知。因此，它可以作为后续机制假说，不能写成已经证明的 SHM 必要结构。

### 如何评价这项工作？

这不是算法 benchmark，没有与一组计算方法比较精度。它的证据强度来自：

- 多供体、多生物学重复的两类单细胞图谱；
- 成像和测序对同一生物学问题的互补测量；
- RAD21 的快速、时间分辨干预；
- Mut-Seq、染色质示踪、3C-HTGTS、CUT&RUN 和 TT-TimeLapse-seq 的正交读出；
- SHM、结构、转录和 AID 结合的不同响应时间。

最可靠的结论是“RAD21/cohesin 对高效 SHM 必需”。更细的机制结论应表述为：数据支持多因素许可模型，但尚未识别唯一的充分和必要下游环节。

### 可检验的后续假说（不是论文既定结论）

1. 用径向分数、GAD、增强子接触、转录速率和 AID 占据构建联合模型，检验多变量是否比单一指标更好预测 SHM。
2. 对单个位点定向扰动 cohesin/CTCF，区分全局 RAD21 效应与局部环挤出的必要性。
3. 在不全局降解 RAD21 的条件下专门破坏 *3′RR1–3′RR2* curl，测试其是否直接稳定 *IGH* SHM。
4. 在单细胞中同时测量 AID 核内动态、核孔距离和 SHM 事件，直接检验径向位置模型。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## A 3D Genome Atlas of Human Tonsil and the Role of Loop Extrusion in B Cell Somatic Hypermutation

### Problem

Somatic hypermutation (SHM) enables antibody affinity maturation but can also mutate non-immunoglobulin loci and contribute to B-cell lymphoma. AID-driven mutagenesis is known to depend on transcription, enhancers, TAD context, and chromatin contacts, yet it had not been established how genome organization across nuclear position, compartments, local contacts, and loops shapes SHM susceptibility in native germinal-center tissue, or whether cohesin-mediated loop extrusion is functionally required (`paper.md:15-21,50-56`).

### Why existing approaches were insufficient

Earlier chromatin-tracing, MERFISH, MINA, single-cell Hi-C, and SHM reporter studies addressed individual layers of this problem. The gap was not simply resolution: sequencing methods provide broad contact coverage but lose tissue position and absolute nuclear coordinates, whereas imaging preserves tissue and 3D position but samples selected loci. Prior association of hot/cold TADs with SHM also did not establish a causal role for cohesin (`paper.md:21,53-56,114,183`). The converted primary text names the prior methods but does not preserve full reference entries with venue/year, so those details are not recoverable from the acquired paper Markdown.

### What the study introduces

The study combines:

- Droplet Hi-C on 12,308 high-quality human tonsil cells from four replicates and two donors;
- MINA on tissue sections, integrating 1151-locus genome-wide chromatin tracing, 447-gene MERFISH, nine-gene smFISH, CD35 staining, and cell/nuclear segmentation across five replicates and three donors; and
- a RAD21-degron RASH-1C perturbation system measured by Mut-Seq, fine-scale *IGH*/*IGL* tracing, 3C-HTGTS, Pol II/AID CUT&RUN, and TT-TimeLapse-seq (`paper.md:65,76,128-162,195-201`).

This design connects an observational tissue atlas to a controlled intervention on loop extrusion.

### High-level method

Droplet Hi-C contacts are converted into gene-body associating domain (GAD) scores for cell clustering and reference-based B-cell state annotation. Grouped contact maps yield 100-kb A/B compartments and 10-kb loops. MINA decodes RNA and 3D locus coordinates in intact tissue, enabling cell-type annotation and spatial features such as radial position, compaction, heterogeneity, demixing, and genomic-distance-normalized interlocus distances (`paper.md:333-408`).

The atlas then compares previously defined SHM-susceptible hot TADs, SHM-resistant cold TADs, and filler loci. The causal arm acutely removes RAD21 and aligns the time courses of mutation accumulation, chromatin architecture, transcription, and AID binding (`paper.md:111-162`).

### Main findings

1. **The atlas resolves both invariant and cell-state-specific organization.** Most compartments remain stable across cell types, while thousands of regions vary. GAD scores and local enhancer-promoter contacts more closely track lineage-defining gene expression at loci such as *PRDM1* than broad compartments alone (`paper.md:85-108`).

2. **Cold TADs occupy a distinct spatial environment.** Across multiple cell types, cold TADs show smaller normalized mutual distances and lower radial scores than hot TADs and filler loci, indicating stronger clustering and a more nuclear-interior position. Hot TADs show higher GAD scores in SHM-active GC B cells and contain genes enriched for GC and SHM biology (`paper.md:114-125`).

3. **RAD21 is required for productive SHM.** RAD21 degradation reduces mutation accumulation at the GFP reporter, *IGH-V*, and *IGL-V* nearly to no-AID background and also compromises non-Ig SHM targets (`paper.md:139-142`).

4. **The phenotype is not explained by immediate collapse of one measured process.** Some chromatin features disappear within 2 hours, but key enhancer-region contacts and substantial transcription persist during the 6–12-hour interval when SHM is already abolished. AID binding is only modestly reduced at 6 hours but becomes severely depleted by 18 hours (`paper.md:148-162,183`).

5. **The authors propose a multi-component cohesin model.** Loop extrusion sustains local architecture, transcriptional dynamics, AID recruitment, and possibly other functions that together create a permissive SHM environment. The atlas additionally suggests that large-scale radial position preconfigures susceptibility (`paper.md:36,180,183`).

6. **A distinctive *IGH* super-enhancer “curl” is observed.** Imaging, independent Hi-C patterns, stricter probes, and directional 3C-HTGTS evidence support preferential parallel alignment of *3′RR1* and *3′RR2*. Its function remains unresolved (`paper.md:165-174`).

### Evaluation and evidence

This is an atlas-and-mechanism paper rather than a benchmark against competing algorithms. Evidence comes from biological replicates, complementary modalities, orthogonal architectural assays, a rapid perturbation time course, and statistical comparisons using two-sided Student's *t* or Wilcoxon tests (`paper.md:65,82,114-117,134,157,411-414`). The main causal result is the near-background SHM phenotype after RAD21 loss; the mechanistic interpretation is strengthened by the different kinetics of architecture, transcription, and AID binding.

Important caution: the radial-position and hot/cold TAD analyses are associative. RAD21 degradation demonstrates a causal requirement for RAD21/cohesin but does not isolate which downstream change is necessary and sufficient.

### Reproducibility and code-paper match

**Workspace reproducibility rating: 3/5.** The primary article gives extensive experimental and computational methods, named tools, thresholds, data accessions, and a Zenodo availability statement (`paper.md:186-450,477-480`). However, this workspace lacks supplementary Markdown, the Zenodo analysis bundle, sample manifests, runtime commands, generated outputs, and figure-to-result mappings.

The acquired GitHub snapshot is a general HTGTS utility repository and has **low overall paper-code fidelity** because it covers only a narrow 3C-HTGTS subset. One match is direct: the paper explicitly links the module for artifact removal and per-million normalization, and the Perl source computes the scale factor from valid junction counts (`paper.md:429-432`; `yyx_normalize_3CHTGTS_tlx.20240131.pl:10-27,52-56,95-123,164-173`). Fixed-count TLX subsampling is only inferred as a possible supporting step. CATG collapse, peak calling, annotation, exact study invocation, sample mapping, generated tracks, and Fig.

### Key limitations

- The study maps selected imaging loci rather than every genomic position.
- Hot/cold TAD definitions originate from prior reporter work and may not capture all context-specific SHM susceptibility.
- Acute global RAD21 loss perturbs multiple processes, complicating assignment of a single proximal mechanism.
- The *IGH* curl's functional relevance remains a hypothesis.
- Full computational reproduction is blocked in this workspace by missing supplementary/Zenodo evidence and absent paper-specific workflow metadata.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
