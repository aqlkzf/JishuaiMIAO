---
layout: default
permalink: /paper-atlas/photon-76ed4124/
title: "PHOTON"
nav: false
description: "PHOTON（photoselection of transcriptome over nanoscale）先在固定样本的所有 RNA 上原位合成“被光锁住”的 cDNA，再用荧光图像找到目标细胞或亚细胞区域，以 405 nm 激光只解锁这些区域中的 cDNA。后续连接、扩增和测序只能通过已解锁的分子，因此显微镜中的空间选择被转换成一份可测序的 ROI 转录组。"
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
      <span>Nature Communications · 2025</span>
    </div>
    <h1>PHOTON</h1>
    <p>Subcellular level spatial transcriptomics with PHOTON</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-59801-3" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PHOTON 方法解释：用显微镜选区域，再只测这些区域里的 RNA

### 一句话理解

PHOTON（photoselection of transcriptome over nanoscale）先在固定样本的所有 RNA 上原位合成“被光锁住”的 cDNA，再用荧光图像找到目标细胞或亚细胞区域，以 405 nm 激光只解锁这些区域中的 cDNA。后续连接、扩增和测序只能通过已解锁的分子，因此显微镜中的空间选择被转换成一份可测序的 ROI 转录组。

### 1. 它解决的不是坐标重建，而是定向取样

许多 RNA 的功能与亚细胞定位有关，例如核仁中的 snoRNA、线粒体 RNA、应激颗粒中的 mRNA。生化分离通常需要大量细胞，对瞬态、无膜结构还容易污染或丢失；MERFISH、seqFISH 等成像方法需要预先设计目标探针；APEX-seq 一类邻近标记又常依赖基因工程。

PHOTON 的取舍不同：研究者先用形态、染料或抗体在图像中定义一类 region of interest（ROI），再把所有被选 ROI 汇总成一个测序文库。它不为每个 RNA 返回原始二维坐标，也不能区分同一次实验中每个 ROI 的独立转录组；当前版本输出的是所选区域的聚合 RNA 丰度及其相对 whole-cell input 的富集。

### 2. 双重光笼为什么能把空间选择变成分子选择

#### 2.1 先在原位合成带“锁”的 cDNA

PHOTON 同时使用 poly-dT 和 random-hexamer 两类定制 RT 引物，以覆盖 poly(A) mRNA 和部分非 poly(A) RNA。光敏结构位于 RT 引物本身：

- 5′ 端荧光基团通过 photocleavable linker 相连；
- 引物中有四个 N-POM 修饰的 dT，未解锁时阻止 splint oligo 正常配对；
- 引物还带 biotin，供后续链霉亲和素磁珠富集。

这里不是把“NPOM-caged dUTP 掺入新生 cDNA”。论文明确描述的是定制 RT primer 中的 N-POM-modified dTs。

#### 2.2 图像决定照哪里

原位逆转录后，样本中的 cDNA 可通过引物荧光观察。卵巢颗粒细胞按组织形态手动选择；核仁和应激颗粒则由 Nikon NIS-Elements 的 JOBS/GA3 模块实时分割。核仁用染料识别，线粒体用 MitoTracker，应激颗粒用 anti-eIF3eta 标记。

选定 ROI 后，XY galvo 用 405 nm 激光扫描目标区域。激光同时：

1. 切断 5′ 端的光敏 linker，释放荧光并暴露 5′ phosphate；
2. 去除 N-POM 光笼，恢复 dT 与 splint oligo 的碱基配对能力。

这两个门必须同时打开。未照射分子既没有可连接的 5′ phosphate，又不能稳定配对 splint，因此难以进入后续 PCR 文库。

#### 2.3 为什么要在灵敏度与空间特异性之间取舍

激光功率或 dwell time 越高，解锁产量会上升，但 ROI 外的非特异光解也会扩大。论文因而对亚细胞 ROI 采用 2.5 mW、100 µs，强调空间特异性；卵巢组织 ROI 使用更高功率和更长 dwell time。作者报告横向空间分辨率可到光学衍射极限约 200–300 nm，但轴向上激光会穿过样本厚度，仍可能解锁焦平面上下的分子。

### 3. 从已解锁 cDNA 到测序文库

激光选择后，样本被消化并提取核酸。splint oligo 将带 P7 PCR handle 的接头与 RT 引物 5′ 端桥接，T4 DNA ligase 只连接已暴露 phosphate 且可完成 splint 配对的分子。

随后流程为：

1. 利用 RT 引物上的 biotin，以 streptavidin beads 拉下已连接 cDNA；
2. 在磁珠上进行 template switching，加入第二个 PCR handle；
3. 先做 5 个 PCR cycle，再以 qPCR 到达饱和信号三分之一所需的 cycle 数决定追加扩增量；
4. 用 Nextera XT 制作文库；
5. 多数实验用 DASH/Cas9 去除 rRNA 等高丰度序列；线粒体实验改用 SEQuoia，以保留线粒体 RNA 信号；
6. 在 Illumina NextSeq 2000 或 NovaSeq X Plus 上测序。

未曝光样本产生的背景主要来自意外光照或引物合成缺陷。论文测得双重 photocaging 对未选择分子的抑制效率为 $99.1\%\pm0.26\%$；在约 5,000 个 HeLa 细胞中即使只选择约 0.5% 的细胞，低功率条件下信号仍高于噪声。

### 4. 计算分析：ROI 与 whole cell 做成对比较

论文方法描述的上游步骤是：去接头和低质量碱基，删除短于 35 bp 的序列，用 HISAT2 比对，再用 featureCounts 计数，最后用 DESeq2 做差异分析。

本地 `code/Enrichment_Analysis.R` 从 BAM 开始。它对三份 Input 和三份 Target BAM 调用 `featureCounts()`，要求 paired-end、`minMQS=20` 且不计 chimeric fragments；之后保留总计数至少为 2 的 feature，并建立：

$$
\text{design}=\sim\text{BATCH}+\text{GROUP}.
$$

其中 `GROUP` 区分 `ROI` 与 `Whole_cell`，`BATCH` 吸收配对实验批次。最终对比是：

$$
\log_2\mathrm{FC}=\log_2\frac{\mathrm{ROI}}{\mathrm{Whole\ cell}}.
$$

正值表示 RNA 在所选区域相对富集，负值表示相对耗减。它不是某个 RNA 的绝对空间概率，也不能消除图像分割、光学串扰、RNA 回收效率等实验偏差。

本地示例元数据的一行把 `ROI` 写成 `R0I`（数字零），实际运行前必须修正，否则 DESeq2 会把它当作第三个 group level。

### 5. 四组实验如何证明方法可用

#### 5.1 图 1：光化学门控与信噪比

HeLa 实验显示，405 nm 照射后目标细胞的引物荧光下降 $86.9\%\pm4.3\%$；无逆转录酶对照不产生文库；未光解引物基本无法扩增。随目标细胞比例和激光功率提高，信号增加，但更高功率或更长 dwell time 会牺牲空间特异性。

#### 5.2 图 2：在组织中选择卵巢颗粒细胞

作者在 10 µm 小鼠卵巢切片中按形态选择约 600 个 granulosa cells。PHOTON 数据富集已知颗粒细胞标记，并与 Slide-seqV2 空间数据的表达模式相符。与机械分离的颗粒细胞 RNA-seq 差异更大，作者认为组织解剖时混入邻近细胞可能是原因之一；这是一种解释，而不是由实验直接证明的唯一原因。

#### 5.3 图 3：核仁、线粒体和应激颗粒

核仁 PHOTON 的顶部富集 RNA 以 snoRNA 为主，并检测到已知核仁相关 lncRNA `RMRP`。线粒体 ROI 中多种线粒体基因显著富集。对 sodium-arsenite 诱导的应激颗粒，PHOTON 与传统纯化数据总体显著重叠。

对存在分歧的 RNA，HCR-FISH 支持 `ZMIZ1`、`EP400` 与 SG 共定位，也支持 `AHNAK2`、`ZACN` 在 PHOTON 中“不富集”的结果。论文谨慎表述为传统纯化可能受污染；不能据此把整个公共数据集或所有差异直接定义为假阳性。

#### 5.4 图 4：m⁶A 与长转录本进入应激颗粒

正常 HeLa 中，长 mRNA 更倾向富集于 SG。作者先用诱导型 `Mettl3` knockout MEF 对四个基因做 qPCR，观察到 m⁶A 位点越多，m⁶A 降低后 SG 富集下降越明显；随后用 METTL3 抑制剂 STM2457 降低 HeLa mRNA 的 m⁶A 水平。100 µM、6 h 条件下，原有的转录本长度依赖富集消失。

论文据此结论是：转录本长度与 SG 富集的相关性“至少部分”由 m⁶A 介导。数据没有证明 m⁶A 是唯一驱动因素；YTHDF 蛋白介导分配是作者结合先前研究提出的可能机制，本研究未直接扰动 YTHDF 来完成因果链。

### 6. 论文与本地代码的对应程度

| 环节 | 本地证据 | 判断 |
|---|---|---|
| ROI/whole-cell featureCounts 与 DESeq2 | `code/Enrichment_Analysis.R` | Exact：主要参数、批次设计和 contrast 可核查 |
| 应激颗粒自动分割与光解 | `code/Phtoselection_of_Stress_Granules.ga3` | Partial：Nikon GA3 二进制工作流存在，但不可作为普通文本审计，且平台专用 |
| FASTQ trimming 与 HISAT2 | 本地未提供 | Not found：论文只给方法描述 |
| Fig. 4 长度分箱、CDF 和 m⁶A 分析 | 本地未提供 | Not found：核心生物学图缺少分析脚本 |
| 核仁、线粒体、HCR-FISH 等实验 | 论文 Methods | Not executable locally：属于湿实验流程 |

### 7. 复现边界

1. 当前代码仓库不是端到端 pipeline；从原始 FASTQ 到 BAM 的命令和配置缺失。
2. `.ga3` 依赖 Nikon NIS-Elements/JOBS/GA3 与特定显微镜硬件，不能直接迁移到其他平台。
3. 定制 N-POM RT 引物、显微镜光路、ROI 分割阈值和样本厚度都会影响空间选择质量。
4. 当前一次实验只选择一类空间区域，并聚合所有 ROI；不能还原单个 ROI 或每条 RNA 的坐标。
5. 本地代码足以核查富集统计骨架，但不足以声称复现全部主图或关键 m⁶A 结论。

### 证据入口

- 论文：`paper.md`
- 主图：`images/41467_2025_59801_Fig1_HTML.jpg` 至 `Fig4_HTML.jpg`
- 富集分析：`code/Enrichment_Analysis.R`
- Nikon 自动光选工作流：`code/Phtoselection_of_Stress_Granules.ga3`
- 代码范围：`code/README.md`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PHOTON: Subcellular Level Spatial Transcriptomics

### Overview

**Method**: PHOTON (PHotoselection of Transcriptome over Nanoscale)
**Type**: Experimental sequencing technology
**Paper**: Rajachandran S et al., *Nature Communications* 16, 2025
**DOI**: 10.1038/s41467-025-59801-3
**Code**: https://github.com/HaiqiChenLab/PHOTON

---

### Motivation & Novelty

#### The Problem

RNA subcellular localization is tightly linked to function. Cells compartmentalize RNA into organelles (nucleus, mitochondria) and membrane-less condensates (stress granules, P-bodies, nucleolus) to regulate translation, processing, storage, and degradation. Understanding which RNA species reside in which compartments — at transcriptome-wide scale — is essential for understanding gene regulation.

Existing methods have critical limitations:
- **Biochemical fractionation** (immunoprecipitation, density gradient): requires millions of cells; impossible for membrane-less condensates (stress granules cannot be purely isolated); significant contamination during isolation
- **Imaging-based methods** — MERFISH (*Xia et al., PNAS, 2019*) and seqFISH (*Eng et al., Nature, 2019*): require pre-designed probe libraries; high cost and technical expertise; cannot profile the entire transcriptome
- **Proximity labeling** — APEX-seq (*Fazal et al., Cell, 2019*; *Padron et al., Mol Cell, 2019*): requires genetic engineering to fuse labeling enzyme to a compartment-specific protein; not flexible across compartment types
- **Spatial transcriptomics** — Slide-seqV2 (*Mantri et al., PNAS, 2024*), Seq-Scope (*Cho et al., Cell, 2021*), Stereo-seq (*Chen et al., Cell, 2022*): tissue-scale resolution only; does not achieve subcellular compartment-level profiling

#### PHOTON's Approach

PHOTON draws from prior work on DNA photo-selection (PSS method, Chen lab) and adapts it to RNA. The key insight: photocaged cDNA molecules can be generated throughout a cell, then selectively *de-caged* by targeted near-UV laser illumination of fluorescence-identified regions of interest (ROIs) — with no genetic modification required.

#### Unique Contributions
1. **No genetic manipulation**: Works in primary cells, tissue sections, any organism
2. **Compatible with membrane-less condensates**: No isolation required — samples directly from intact, in situ compartments
3. **Flexible scale**: Demonstrated from selected regions in 10 µm ovarian tissue sections to subcellular stress granules, with lateral selection approaching the optical diffraction limit
4. **Dual photocaging**: Photocleavable linker + N-POM modified dTs create a dual-gate specificity mechanism achieving 99.1% background suppression
5. **Uses standard microscopy infrastructure**: FRAP laser module available in most microscopy core facilities (Nikon Ti2-LAPP)

---

### Method Overview

PHOTON is a four-step wet-lab protocol:

1. **In situ photocaged cDNA library**: Custom RT primers containing (a) photocleavable 5' linker blocking ligation, (b) N-POM modified dTs blocking splint annealing, (c) 5' fluorophore for visualization, (d) biotin for pulldown. Two primer types used simultaneously: poly-dT (mRNA) and random hexamer (ncRNA/mt-RNA).

2. **Fluorescence imaging + targeted photocleavage**: Compartments visualized by staining (nucleolus bright green dye, MitoTracker, anti-eIF3eta for SGs, morphology for GCs). Automated segmentation (Nikon JOBS/GA3 modules) generates ROI coordinates. 405 nm laser (Ti2-LAPP XY galvo) illuminates each ROI, uncaging both the 5' phosphate and the N-POM dTs.

3. **Selective ligation + streptavidin pulldown**: Splint oligo bridges the photocleaved RT primer 5' end to a P7 PCR handle. T4 DNA Ligase seals the nick — only in photocleaved molecules with restored 5' phosphate and base pairing. Streptavidin beads capture biotin-tagged cDNA. Template switching on-bead adds the second PCR handle.

4. **Library prep + sequencing**: Adaptive PCR amplification (qPCR-guided cycle number), Nextera XT library prep, DASH Cas9-based rRNA depletion, Illumina sequencing. Computational: HISAT2 → featureCounts → DESeq2 (~BATCH + GROUP) to quantify ROI vs whole-cell enrichment.

**Laser parameters**: 2.5 mW, 100 µs for subcellular (specificity-first); 15–37.5 mW, 300 µs for tissue-level.

---

### Evaluation

#### Datasets Used
- HeLa cells: Feasibility, SNR characterization, nucleolus, SG profiling
- Mouse ovary (C57BL/6): Granulosa cell transcriptome (10 µm tissue sections, ~600 GCs)
- Mouse embryonic fibroblasts (MEF) with conditional *Mettl3* KO
- Public SG dataset: Khong et al., *Mol. Cell*, 2017 (conventional SG purification)
- Public Slide-seqV2 ovary: Mantri et al., *PNAS*, 2024 (GEO: GSM7689280)
- Public GC RNA-seq: Bianco et al., *Cell Rep.*, 2019 (GEO: GSE119508)

#### Key Results
| Experiment | Result | Metric |
|---|---|---|
| Photocaging efficiency | Near-perfect background suppression | 99.1 ± 0.26% |
| Photocleavage efficiency | Efficient uncaging in targeted cells | 86.9 ± 4.3% fluorescence decrease |
| SNR | Strong signal above noise at low cell fractions | SNR = 357 × f (25mW); SNR >1.2 at 0.5% cells |
| GC specificity | Known GC markers enriched, other cell-type markers absent | GC markers >5× enriched |
| GC vs Slide-seqV2 | High correlation with gold-standard spatial method | r = 0.71 |
| GC vs isolation RNA-seq | Lower correlation, attributed to isolation contamination | r = 0.48–0.51 |
| Nucleolus | snoRNA enrichment confirmed | Majority of top-enriched: snoRNAs + RMRP |
| SG accuracy | False positives in purification identified | AHNAK2, ZACN: HCR-FISH confirms NOT in SGs |
| SG length-dependence | Long mRNAs prefer SGs | Confirmed CDF shift, >6 kb vs <1 kb |
| m6A role in SGs | Reducing m6A abolishes the observed length-SG correlation under the tested condition | STM2457 100 µM (6h) eliminates length stratification; the paper concludes m6A mediates it at least in part |

#### Biological Validation
- HCR-FISH independently validated 4 transcripts predicted by PHOTON SG data (ZMIZ1, EP400 — true positives; AHNAK2, ZACN — true negatives in SGs)
- Mitochondrial gene transcripts enriched in mitochondria PHOTON data
- Heat shock and sodium arsenite SGs show overlapping but distinct RNA content (hypergeometric p < 0.001)
- m6A depletion (*Mettl3* KO MEF, qPCR on 4 genes) shows progressive reduction in SG enrichment with increasing m6A site count

---

### Reproducibility: 3/5

**Justification**: The paper provides good experimental detail in the Methods, but key barriers exist:

**Strengths**:
- Detailed wet-lab protocol with specific reagent catalog numbers, concentrations, and timing
- Oligonucleotide sequences in Supplementary Table 1 (available)
- Raw sequencing data deposited: NCBI BioProject PRJNA1152621
- Enrichment analysis R code provided (Enrichment_Analysis.R)

**Limitations**:
- **Instrumentation**: Requires Nikon CSU-W1 + Ti2-LAPP system with FRAP module — uncommon and expensive. The `.ga3` Nikon-specific Galaxy workflow is not portable to other platforms.
- **Custom RT primers with N-POM modification**: Must be custom-synthesized at IDT. N-POM dT is a non-standard modified nucleotide. Synthesis complexity and quality control are not trivial.
- **Incomplete computational pipeline**: Read trimming and alignment (HISAT2) steps not provided. Key figure analyses (length-binned SG enrichment, hypergeometric overlap tests) have no code.
- **DASH rRNA depletion**: Requires custom crRNA design for each target species/cell type
- **m6A analysis scripts**: Fig 4A, 4D methodology (length-binned CDF analysis) not in code
- **Automated segmentation**: Nikon JOBS/GA3 scripts not fully documented; parameter tuning (size, intensity, circularity thresholds) requires expertise
- **Mettl3 KO MEF cell line**: Shared by Jaffrey lab (Cornell); requires material transfer agreement

**Practical notes**:
- Start with HeLa cell SG experiment (most straightforward: no tissue sectioning, immunostaining well-established)
- For nucleolus: nucleolus bright green dye (Dojindo c511) is critical; nucleolus ROIs are ~1-3 µm, requiring careful laser calibration
- RNA degradation risk increases with total experiment time — minimize handling time per sample
- For tissue: PMSG/hCG hormone priming and careful cryosectioning (10 µm) are essential

---

### Limitations and Future Directions

1. **Single-selection per specimen**: Only one class of ROI can be selected per sample. Multiplexed spatial barcoding is a proposed future direction.
2. **Axial resolution**: 405 nm laser passes through full specimen thickness; some z-axis contamination possible. Addressable by two-photon excitation (proposed but not demonstrated).
3. **Instrumentation accessibility**: While FRAP modules are common, the Ti2-LAPP galvo scanning system is Nikon-specific and expensive.
4. **Code completeness**: Full bioinformatics pipeline not provided — researchers must independently set up HISAT2 + featureCounts pipeline.
5. **Throughput per experiment**: Thousands of ROIs can be targeted, but each PHOTON experiment is fundamentally 1 spatial selection per specimen (though multiple ROIs of the same type can be aggregated).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
