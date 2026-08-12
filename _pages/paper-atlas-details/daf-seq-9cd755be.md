---
layout: default
permalink: /paper-atlas/daf-seq-9cd755be/
title: "DAF-seq"
nav: false
description: "DAF-seq 的关键想法是：先用双链 DNA 胞嘧啶脱氨酶 SsDddA 给“暴露在外”的胞嘧啶做化学标记，再通过 PCR/WGA 把这些标记永久转换成可测序的 C→T 或 G→A 变化。这样，同一条长 DNA 分子既保留遗传序列，也携带蛋白质占据、核小体保护和染色质开放状态的信息；在单细胞版本 scDAF-seq 中，这些随机标记还可以帮助把扩增产生的重叠读段重新拼回父系/母系、正链/负链四种原始模板。"
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
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>DAF-seq</h1>
    <p>Mapping single-cell diploid chromatin fiber architectures using DAF-seq</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DAF-seq 方法详解：把染色质状态写进 DNA 序列

### 一句话理解

DAF-seq 的关键想法是：先用双链 DNA 胞嘧啶脱氨酶 SsDddA 给“暴露在外”的胞嘧啶做化学标记，再通过 PCR/WGA 把这些标记永久转换成可测序的 C→T 或 G→A 变化。这样，同一条长 DNA 分子既保留遗传序列，也携带蛋白质占据、核小体保护和染色质开放状态的信息；在单细胞版本 scDAF-seq 中，这些随机标记还可以帮助把扩增产生的重叠读段重新拼回父系/母系、正链/负链四种原始模板。

论文：*Mapping single-cell diploid chromatin fiber architectures using DAF-seq*，*Nature Biotechnology*，2025，DOI `10.1038/s41587-025-02914-3`。

### 1. 它要解决什么问题？

真正执行基因调控的是单个细胞中的单条染色质纤维。同一个位点可能因为单倍型、细胞状态、随机蛋白结合或遗传变异而呈现完全不同的蛋白占据模式。但已有技术往往只能满足下面一部分需求：

- **Fiber-seq（*Science*, 2020）**可以读取长分子上的染色质结构，但甲基化模板在 DNA 扩增时会被擦除，因此主要是 bulk 实验，难以把一个细胞的全基因组放大后再恢复原始分子。
- **scATAC-seq（*Nature*, 2015）**及其他 Tn5 单细胞可及性方法依赖切割和抽样，单细胞数据稀疏，而且难以直接观测“关闭”状态。
- **单细胞脱氨酶足迹方法（*PNAS*, 2024；bioRxiv, 2024）**也受短片段和 Tn5 富集限制，不能连续追踪染色体尺度的同一条纤维。
- 传统长读长染色质标记通常只能覆盖一条 10–100 kb 分子，而单细胞 Tn5 数据往往是零散的约 100-bp 片段（`paper.md:21`）。

因此，核心问题不是“能否测到开放染色质”，而是：

> 能否让单条染色质纤维的蛋白保护图案在 DNA 扩增后仍然存在，并用它恢复单细胞、单倍型和整条染色体尺度的结构？

### 2. DAF-seq 的核心化学机制

SsDddA 是一种能作用于双链 DNA 的胞嘧啶脱氨酶。实验把它加入通透化的细胞核：

```text
开放 DNA 上的 C ──SsDddA──> U ──PCR/WGA──> T

被 TF/核小体保护的 C ──蛋白遮挡──> 大多仍为 C
```

于是，一条染色质纤维被转换成“序列模板 + 红色脱氨标记 + 蛋白保护空白区”的组合（Fig. 1；`paper.md:24-30`）。

#### 为什么会出现 C→T 和 G→A 两种信号？

如果原始模板是参考基因组的上链，胞嘧啶脱氨后测到 C→T；如果原始模板来自互补链，同一类事件映射到参考基因组时表现为 G→A。因此可按两类变化的比例给读段分链：

- CT read：C→T 占主导，代表 top-template；
- GA read：G→A 占主导，代表 bottom-template。

论文和代码都采用 90% 阈值。代码随后把可能的脱氨位置写成 IUPAC 模糊碱基：CT 读段用 Y，GA 读段用 R，并添加 `ST/DA/FD/LD` 标签（`paper.md:219-222`; `General/process_DddA_bam.py:26-123`）。

#### 这个设计为什么重要？

1. **标记可扩增。** U 在复制后变成 T，信息不再依赖容易丢失的表观化学修饰。
2. **同一读段可看遗传与染色质。** 互补链信息帮助区分 DddA 事件和真正的 C/T、G/A 变异。
3. **随机图案可以当分子条形码。** 同一原始模板产生的 PCR/PTA 读段会共享复杂的脱氨组合，可用于去重和拼接。

### 3. 从原始分子到分析结果的完整流程

```text
通透化细胞核 / 单细胞
        │
        ├─ SsDddA 标记可及胞嘧啶
        ▼
靶向 PCR、bulk WGA 或单细胞 PTA
        ▼
PacBio/ONT 长读长测序并比对 GRCh38
        │
        ├─ 根据 C→T / G→A 比例判定 CT/GA 链
        ├─ 用 Y/R 编码脱氨位点并重新比对
        └─ fibertools 识别 MSP、核小体和 TF 足迹
        ▼
    ┌───────────────┴────────────────┐
    │                                │
靶向 DAF-seq                    单细胞 scDAF-seq
    │                                │
TF 占据/共占据                    PTA 重叠读段分组
热力学相互作用                    四类 haplotype-strand 共识序列
遗传变异及其染色质效应            父母单倍型定相
单分子染色质状态聚类              FIRE 开放、CTCF、共激活与可塑性
```

### 4. 靶向 DAF-seq 如何分析 TF 调控逻辑？

#### 4.1 单分子足迹

在 NAPA 启动子中，研究者先用 FIMO/JASPAR 找候选 motif，再用 fibertools 在单条纤维上识别 TF footprint。只有在 CT 和 GA 两类纤维中都至少有 5% 占据的 motif 被保留，并把高度重叠的 motif 合并成调控元件（`paper.md:258-261`）。

对两个元件 $i,j$，只统计同时覆盖两个元件的开放纤维：

$$E_{ij}=p_i p_j$$

$$O_{ij}=\frac{n(i,j\ \text{同时结合})}{n(\text{同时覆盖}\ i,j)}$$

代码输出的共依赖分数为：

$$C_{ij}=4(O_{ij}-E_{ij}).$$

- $C_{ij}>0$：两者在同一分子上共同出现得比独立模型更多；
- $C_{ij}<0$：两者倾向互斥；
- $C_{ij}\approx 0$：观察值接近独立结合。

直接实现见 `Targeted/NAPA/footprinting/06_codependency_footprint_regions.py:13-28`。

#### 4.2 “谁在驱动合作？”

仅看到元件 1 和 2 共占据，还不能判断方向。代码建立 TF 元件图，边权为共依赖分数；随后逐个去掉某元件，并只保留“该元件可及但未结合”的纤维，再观察剩余网络平均边权下降多少：

$$\mathrm{essentiality}_i=\frac{\text{基线平均共依赖}}{\text{排除元件 }i\text{ 后的平均共依赖}}.$$

NAPA 数据中，元件 1 的排除造成最大下降，支持元件 1 驱动元件 2 占据（Fig. 2、Extended Data Fig. 5；`paper.md:57`）。

### 5. 热力学模型在算什么？

论文把 NAPA 启动子看成一组平衡附近的 TF 结合状态。以“所有位点都未结合”为参考状态，假设不同状态的读段频率服从 Boltzmann 分布。

单个 TF $i$ 的相对自由能：

$$\frac{Pr(\mathrm{TF}_i\mathrm{bound})}{Pr(\mathrm{unbound})}=e^{-\Delta G_i/RT}$$

论文忽略对所有状态共同的 RT，得到无量纲能量：

$$\Delta G_i=-\ln\left(\frac{\mathrm{count}(\mathrm{TF}_i\mathrm{bound})}{\mathrm{count}(\mathrm{unbound})}\right).$$

两个 TF 的额外相互作用能为：

$$\Delta G_{ij}=-\ln\left(\frac{\mathrm{count}(\mathrm{TF}_{ij}\mathrm{bound})}{\mathrm{count}(\mathrm{unbound})}\right)-\Delta G_i-\Delta G_j.$$

三个 TF 时继续减去所有单体和两两项：

$$\begin{aligned}
\Delta G_{ijk}={}&-\ln\left(\frac{\mathrm{count}(\mathrm{TF}_{ijk}\mathrm{bound})}{\mathrm{count}(\mathrm{unbound})}\right)\\
&-\Delta G_i-\Delta G_j-\Delta G_k-\Delta G_{ij}-\Delta G_{ik}-\Delta G_{jk}.
\end{aligned}$$

负值表示相对于低阶独立状态更有利，正值表示更不利。代码使用未结合读段作分母，按组合阶数递归减去低阶能量，并用 45 个二元组合和 120 个三元组合做 Bonferroni 校正（`paper.md:264-336`; `local/utils/daf_utils.py:97-169`）。

需要注意：这是“基于状态频率、近似平衡”的解释，不等同于直接测量生化结合常数。位点 11 因占据率超过 99%，缺少可靠未结合状态，被排除在热力学分析之外。

### 6. 如何同时读取遗传序列与染色质？

在一个 C/G 位点，DddA 只作用于其中一条链。即使 top 链的 C 被随机改成 T，bottom 链仍保留 G，因此把 top/bottom 读段的碱基比例放在一起，就能判断原始位点是 C/G、T/A，还是杂合状态（Fig. 3a；`paper.md:63`）。

这种互补证据使 DAF-seq 能：

- 在只有一个 C/T 杂合位点时给 UBA1 读段定相；
- 比较 SLC39A4 两个单倍型的染色质开放概率；
- 在低 VAF 肿瘤变异上同时计算变异比例和局部 CTCF/核小体效应。

COLO829 49:1 混合实验中，DAF-seq 得到 1.5% VAF，接近 PCR-free WGS 的 1.4%；携带 CC>TT 变异的纤维失去 CTCF 占据、开放性和核小体相位（`paper.md:87-93`）。

### 7. SLC39A4 单分子染色质聚类

每条纤维被表示成一个按基因组位置排列的二值向量：

- 1：该位置发生脱氨；
- 0：保留参考碱基；
- 同时附加组织与单倍型标签。

代码对每个组织/单倍型抽样 5,000 条 GA 纤维，用全部位置特征构建邻居图（`n_pcs=0`, `n_neighbors=200`），再做 UMAP 和 Leiden 聚类；小于或等于 1,000 条纤维的主簇被删除，活化簇再以 50 邻居重聚类，并删除小于或等于 200 条纤维的子簇（`Targeted/SLC39A4/clustering/02_cluster_msps_SLC39A4.py:9-185`）。

图中的 cluster 1 在代码内部是 cluster 6，绘图脚本明确记录了这个重标号（`05_cluster_plots.R:487-504`）。该簇几乎全部来自肝脏，且肝脏中 72% 来自 rs2280838-T 单倍型；T 单倍型更容易在 promoter module C 启动局部开放。

### 8. scDAF-seq 如何把单细胞扩增读段拼回原始纤维？

#### 8.1 四种 haplotype-strand 模板

二倍体常染色体的一个位置最多对应四条原始模板：

```text
父系 top    父系 bottom
母系 top    母系 bottom
```

单细胞 PTA 偏好从原始模板反复起始，产生大量部分重叠的扩增子。每条原始模板具有自己的普通变异、链方向和随机脱氨图案，因此可把重叠读段重新分组（Fig. 5；`paper.md:108`）。

#### 8.2 第一轮分组

代码把基因组划分为长度 150 bp、步长 25 bp 的重叠窗口。两条读段只有同时满足以下条件才视为相似：

1. 至少共享 11 个窗口，即总重叠约 400 bp；
2. 共享窗口中至少 80% 的窗口达到 ≥99% 序列一致性；
3. 最终组内的新读段不能与任何已有读段冲突，而不是只要通过一条“桥接读段”相连即可。

实现见 `Single_cell/collapse/kmer_align.py:29-205`。

#### 8.3 共识碱基

每个位置一般选择支持率 ≥50% 的碱基。如果主要冲突恰好是 CT 模板上的 C/T，或 GA 模板上的 G/A，代码优先选择原始 C 或 G，以降低扩增后额外脱氨造成的假变异。插入只有在所有读段中都存在时才保留，并选择最短插入；缺失只有在所有读段一致时才接受（`paper.md:384`; `kmer_align.py:212-276`）。

第二轮允许共识序列在至少 7 个窗口（300 bp）重叠时继续合并；冲突处选择该窗口中原始读段支持数最多的共识序列。之后用父母短读长变异通过 WhatsHap 分配父系/母系单倍型。

### 9. 单细胞染色质如何量化？

#### 9.1 FIRE 元件是否被激活

fibertools 在共识读段中识别 MSP。长度 >150 bp 的 MSP 如果与 Fiber-seq FIRE peak 互相满足至少 50% 的重叠，就把该元件记为 actuated：

- −1：该 haplotype-strand 没有覆盖；
- 0：有覆盖但没有 MSP；
- 1：有 MSP，元件激活。

代码与论文阈值一致（`paper.md:393-396`; `Single_cell/msp_analysis/01_call_msps.sh:5-23`; `02_intersect_MSP_FIRE.sh:14-31`）。

#### 9.2 染色质可塑性

对两个细胞或两个单倍型共同覆盖的 FIRE peaks，计算二值激活状态的 Jaccard distance。结果显示：

- 同一细胞两条单倍型平均相差约 61%；
- 不同细胞同一单倍型平均相差约 63%；
- promoter-proximal 元件、bulk 中经常开放的元件和高表达基因启动子更稳定（Fig. 6；`paper.md:123-126`）。

#### 9.3 同一条纤维上的共激活

对每对 FIRE peaks，计算 $4(O-E)$，并设置三种比较：

1. **same fiber**：同一 haplotype-strand；
2. **opposite haplotypes**：同一细胞的两条不同单倍型，用来控制共同的 trans 环境；
3. **different cells**：不同细胞，作为负对照。

R 脚本再按 $\lfloor\log_2(d)\rfloor$ 对距离分箱。same-fiber 信号主要出现在约 100 kb 以内，尺度接近 cohesin loop，而远距离趋近于零（Fig. 7e；`Single_cell/msp_codependency/03_msp_codependency.py:77-355`; `04_plot_msp_codependency.R:41-158`）。

#### 9.4 CTCF loop 验证

为了验证 scDAF-seq 的长程共占据，论文使用 ChIA-PET loop anchors。代码只保留 Fiber-seq actuation ≥30% 的 CTCF 元件，并要求至少 4 条 haplotype-strand 纤维覆盖。+/- 收敛方向的 CTCF 对共占据最高，且 ChIA-PET 强度越高，共占据越高（`paper.md:132`; `Single_cell/CTCF_occupancy/04_ctcf_analyses.py:96-212`）。

### 10. 关键结果应该怎样解读？

| 结果 | 数值 | 含义 |
|---|---:|---|
| 纯化 dsDNA 胞嘧啶脱氨 | 99.8% | SsDddA 催化活性很高 |
| NAPA/WASF1 可及区脱氨 | 82% / 73% | 开放区信号强 |
| 受保护足迹脱氨 | 2.6% / 2.3% | TF/核小体保护形成清晰负信号 |
| 靶向富集 | 最高约 230,000 倍 | 可对少数位点获得极深覆盖 |
| 最深细胞共识 N50 | 34.5 kb | PTA 重叠读段能延长为长共识纤维 |
| >100-kb 共识读段 | 5,608 条 | 可跨越远距离调控元件 |
| 单细胞可映射基因组覆盖 | 60–99% | 随测序深度增加而提高 |
| 单倍型可定相覆盖 | 27–80% | 父母变异决定可定相比例 |
| 细胞间激活差异 | ~63% | 单细胞染色质状态高度可塑 |
| 同细胞单倍型间差异 | ~61% | 不能主要用细胞间 trans 差异解释 |
| 最强 500 个 loop 的 CTCF 共占据 | 中位数 71% | 读出符合已知 loop 方向性与强度 |

### 11. 代码与复现性

本地代码快照与论文主要分析逻辑的匹配度为 **medium fidelity**：

- **Exact**：DddA 预处理、脱氨图案去重、NAPA 共依赖、单细胞共识分组、FIRE actuation、调控元件共激活、CTCF loop 分析；
- **Notebook**：热力学公式由 Jupyter notebook 和 `daf_utils.py` 实现；
- **Partial**：SLC39A4 代码只对 GA 纤维聚类且有图中重标号；UBA1 校正脚本存在疑似 BAM template 运行错误；
- **Not found**：ResolveServices 定制 PTA 实验协议、完整端到端工作流和所有本地原始/辅助数据。

仓库是按分析顺序编号的 manuscript scripts，而不是可一键运行的软件包。它依赖 SRA 原始数据、外部 Fiber-seq/FIRE 文件、Zenodo 附件和多个预生成中间文件。随机抽样也没有固定 `random_state`。详见 `doc_code.md`。

### 12. 局限与未解决问题

1. **单细胞成本高。** 每个细胞需要比常规单细胞开放性技术更深的长读长测序。
2. **细胞数量有限。** 主要单细胞结论来自 12 个 GM24385 淋巴母细胞，适合证明可行性，但不足以代表复杂组织的群体异质性。
3. **热力学解释依赖平衡假设。** 读段频率推导的 $\Delta G$ 是相对、无量纲的状态能量，不是直接测得的结合常数。
4. **胞嘧啶密度和 5mC 会影响信号。** SsDddA 对 5mCpG 的活性降低；真正分辨率仍受可脱氨位置分布限制。
5. **PTA 是关键但未公开实现。** 自定义商业协议对单细胞读段长度和偏好非常重要。
6. **本地补充材料缺失。** `SUPP_MD=none`；Supplementary Figs. 1–16、Supplementary Note 和补充表在当前工作区中为 **MISSING**，不能把补充材料独有的细节补写成确定事实。

### 13. 最终心智模型

可以把 DAF-seq 看成三层编码：

```text
第一层：普通 DNA 序列
        → 遗传变异、单倍型

第二层：SsDddA 随机脱氨图案
        → 原始模板指纹、PCR 去重、PTA 读段拼接

第三层：脱氨图案中的“保护空白”
        → TF 足迹、核小体、MSP、染色质开放与长程共调控
```

它最有价值的地方不是单独把开放染色质测得更深，而是让同一组序列变化同时承担“染色质读出”和“原始分子身份”的双重角色，从而把单分子足迹扩展到单细胞、单倍型和染色体尺度。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DAF-seq Summary

### What problem does the paper solve?

Gene regulation occurs on individual chromatin fibers within diploid cells, but existing assays generally trade off molecular length, footprint resolution, sequencing depth and single-cell coverage. Long-read methyltransferase-stenciling methods such as Fiber-seq (*Science*, 2020) measure rich 10–100-kb single-molecule architectures but are bulk assays because amplification erases their methylation marks. Tn5-based single-cell assays such as scATAC-seq (*Nature*, 2015) and later deaminase-footprinting approaches (*PNAS*, 2024; bioRxiv, 2024) are sparse and sample only short fragments, including inaccessible-state blind spots (`paper.md:21`; references 1, 8, 10 and 11).

DAF-seq addresses this by converting chromatin accessibility into ordinary, amplification-stable sequence changes. This enables deep targeted analysis and, with primary template-directed amplification (PTA), chromosome-scale reconstruction of genomic and chromatin states from a single cell.

### Core idea

DAF-seq treats permeabilized nuclei with the nonspecific double-stranded cytidine deaminase SsDddA. Accessible cytidines are converted to uridines, whereas cytidines protected by TFs or nucleosomes remain mostly unchanged. After PCR/WGA, the uridines appear as thymidines:

- top-template fibers contain C-to-T changes;
- bottom-template fibers contain G-to-A changes;
- the complementary strand helps distinguish induced deamination from germline or somatic sequence variation;
- each stochastic deamination pattern acts as a template-specific molecular identifier.

The computational pipeline assigns CT/GA strand, writes likely events as Y/R ambiguity codes, realigns reads, calls accessibility patches and footprints, and then branches into targeted or single-cell analyses. Targeted DAF-seq quantifies occupancy, co-occupancy, thermodynamic TF interactions, rare variants and chromatin-state clusters. scDAF-seq groups overlapping PTA reads into paternal/maternal top/bottom consensus fibers, phases them with parental variants and measures chromosome-scale actuation and co-occupancy (`paper.md:24,63,96-108,219-222`).

### What is technically new?

1. **An amplification-stable chromatin stencil.** Unlike methylation marks, DddA-induced sequence changes survive PCR and WGA, permitting both deduplication and single-cell read collapse.
2. **Synchronous sequence and chromatin measurement.** One molecule reports genotype/haplotype, protein footprints, nucleosomes and accessible elements.
3. **High-depth targeted footprinting.** Amplicon enrichment enables near-nucleotide TF occupancy and rare-allele analysis at very high coverage.
4. **A four-template single-cell model.** PTA products are reconstructed into paternal/maternal × top/bottom haplotype-strand consensus reads rather than treated as independent reads.
5. **Controls for cell-level trans effects.** Same-fiber regulatory-element codependency is compared with opposite haplotypes within the same cell and with different-cell controls.

### Main results

#### Assay performance

- Recombinant SsDddA deaminated 99.8% of cytidines in purified dsDNA and showed little genome-wide sequence-context bias under the chosen conditions (`paper.md:39`).
- At 4 μM for 10 min, median deamination in accessible NAPA and WASF1 promoter regions was 82% and 73%, compared with 2.6% and 2.3% in protected CTCF/nucleosome footprints (`paper.md:42`).
- Targeted DAF-seq achieved up to roughly 230,000-fold enrichment relative to genome-wide sequencing and agreed with Fiber-seq/ATAC-seq across ten targeted regions (`paper.md:42`; Fig. 1 and Extended Data Fig. 4).

#### TF occupancy and chromatin states

- At the NAPA promoter, 11 elements ranged from 13% to 96% occupancy. Element 2 was rarely bound without element 1; the inferred protein–protein interaction between elements 1 and 2 had approximately 180,000-fold greater relative affinity than element 2's solo protein–DNA interaction (`paper.md:48,57`).
- SLC39A4 fibers separated into distinct tissue- and haplotype-associated nucleosome/actuation states. The active cluster was almost entirely liver-derived, and 72% of its liver reads carried the rs2280838-T haplotype. A promoter position above the variant was twice as likely to be focally actuated on the T haplotype (*P* = 5.4 × 10^−10^) (`paper.md:78-81`).
- In a 49:1 COLO829 mixture, targeted DAF-seq measured a 1.5% CC>TT somatic-variant fraction, closely matching 1.4% from PCR-free WGS, and showed loss of CTCF occupancy, accessibility and nucleosome phasing on variant fibers (`paper.md:87-93`).

#### Single-cell genome and chromatin reconstruction

- Twelve GM24385 cells were sequenced from about 12 Gb to 133 Gb. The deepest cell reached a consensus-read N50 of 34.5 kb and produced 5,608 consensus reads longer than 100 kb (`paper.md:99-108`).
- At least one consensus read covered 60–99% of each cell's mappable autosomal genome; 27–80% could be assigned to a parental haplotype (`paper.md:108`).
- Only about 46% of bulk-defined regulatory elements were actuated in a typical single cell. Actuation differed by approximately 63% between cells and 61% between haplotypes within a cell, while promoter-proximal, consistently actuated and highly expressed loci were more stable (`paper.md:123-126`).
- CTCF loop anchors showed strongest co-occupancy in convergent +/− orientation; the strongest 500 3D contacts had median co-occupancy of 71%. Preferential same-fiber regulatory-element co-actuation was concentrated within roughly 100 kb (`paper.md:132,141`).

### How the paper is evaluated

The study combines biochemical validation, orthogonal chromatin assays and several biological test cases:

| Question | Evaluation evidence |
|---|---|
| Is SsDddA active and relatively unbiased? | Mass spectrometry, motif logos, concentration/time titration, CpG-methylation test |
| Does DAF-seq recover known chromatin features? | Agreement with DNase-seq, scATAC-seq, ATAC-seq and Fiber-seq at multiple loci |
| Can it infer local regulatory logic? | NAPA TF occupancy, thermodynamic states, pairwise/conditional codependency |
| Can sequence and chromatin be read together? | UBA1 haplotype phasing, SLC39A4 epialleles, low-VAF COLO829 variant |
| Can single-cell reads be reconstructed? | Consensus length, genome coverage, parental phasing and switch-error analyses |
| Are chromosome-scale chromatin claims biologically plausible? | FIRE enrichment, TSS enrichment, CTCF orientation, ChIA-PET/Micro-C strength and opposite-haplotype controls |

The evaluation is broad and internally coherent, although most single-cell biological conclusions are drawn from 12 cells of one lymphoblastoid line and the method requires unusually deep long-read sequencing per cell.

### Reproducibility and code–paper match

**Reproducibility rating: 3/5.**

The primary sequencing data are deposited under BioProject `PRJNA1203351`; processed tables are linked by the paper; custom code is available through GitHub and Zenodo (`paper.md:423-432`). The local snapshot at commit `1edd700ac9cfca687308a914d77ff67d9d698835` contains direct implementations of the major computational analyses.

The code–paper match is **medium fidelity**:

- exact source matches exist for DddA preprocessing, deamination-pattern deduplication, NAPA codependency, scDAF read grouping/consensus, FIRE actuation, distance-dependent codependency and CTCF loop analysis;
- the thermodynamic equations are implemented in a notebook plus utility module;
- SLC39A4 analysis is released as a GA-only clustering workflow with internal cluster labels remapped for the figure;
- an UBA1 correction script contains a likely output-BAM template defect;
- the repository is a hard-coded set of numbered manuscript scripts, not a self-contained workflow, and it requires external SRA, Fiber-seq/FIRE and Zenodo inputs.

See `doc_code.md` for the direct line-level map and `doc_method.md` for the full computational pipeline.

### Important limitations

- **Custom PTA is not released.** ResolveServices performed a customized commercial single-cell amplification protocol; the code starts from its reads (`paper.md:369-372`).
- **High sequencing cost per cell.** scDAF-seq uses substantially more sequencing than standard single-cell accessibility assays (`paper.md:147`).
- **Limited single-cell cohort.** Twelve cells demonstrate feasibility and biological patterns but do not establish population-scale generality.
- **Thermodynamic assumption.** NAPA interaction energies assume a near-equilibrium promoter and use state frequencies as Boltzmann probabilities.
- **Cytidine and methylation dependence.** Resolution is constrained by susceptible bases, and 5mCpG is deaminated less efficiently than unmethylated cytidine.
- **Operational reproducibility is incomplete.** No end-to-end workflow, tests or bundled example dataset are provided; several stages rely on external tools, generated intermediates and hard-coded paths.
- **Supplementary evidence is incomplete locally.** `SUPP_MD` and supplementary figures/tables are **MISSING** from this workspace and were not inferred.

### Bottom line

DAF-seq is a technically ambitious chromatin-stenciling platform that makes protein protection patterns survive amplification as sequence information. Its strongest contribution is not just higher-resolution footprinting, but the ability to use the same marks as occupancy signal, molecular identifier and single-cell consensus key. The paper convincingly demonstrates targeted rare-allele/TF applications and chromosome-scale single-cell reconstruction, while practical adoption will depend on access to the custom PTA workflow, deep long-read sequencing and a more portable end-to-end implementation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
