---
layout: default
permalink: /paper-atlas/perturb-dbit-2a00375a/
title: "Perturb-DBiT"
nav: false
description: "Perturb-DBiT 解决的是“在真实组织空间里做 pooled CRISPR screen”的读出问题。传统 Perturb-seq / CROP-seq 这类单细胞 CRISPR 读出可以把 sgRNA 和转录组联系起来，但通常需要组织解离，因此丢失肿瘤结构、克隆位置、免疫细胞邻域等空间信息。"
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
      <span>Technology Platforms</span>
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>Perturb-DBiT</h1>
    <p>Large-scale, spatially resolved panoramic CRISPR screening in native tissue environments using Perturb-DBiT</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-026-03127-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Perturb-DBiT">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/abaysoy/Perturb_DBiT" target="_blank" rel="noopener noreferrer" aria-label="Open code for Perturb-DBiT">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Perturb-DBiT 方法解释

### 这篇论文解决什么问题

Perturb-DBiT 解决的是“在真实组织空间里做 pooled CRISPR screen”的读出问题。传统 Perturb-seq / CROP-seq 这类单细胞 CRISPR 读出可以把 sgRNA 和转录组联系起来，但通常需要组织解离，因此丢失肿瘤结构、克隆位置、免疫细胞邻域等空间信息。已有空间 CRISPR 或 FISH/成像方法能保留空间，但常常局限于预设探针 panel，难以做 unbiased total RNA，尤其难覆盖 lncRNA、miRNA、tRNA 等非编码 RNA (`paper.md:18-24`)。

论文提出的核心目标是：在同一张组织切片上，同时获得空间位置、sgRNA 身份、全转录组/total RNA 表达，并把这些信息用于解释肿瘤克隆扩增、迁移、非编码 RNA 调控和 TME 免疫状态 (`paper.md:12`, `paper.md:24`)。

### 方法核心

Perturb-DBiT 可以理解为把 DBiT-seq 的 deterministic barcoding 和 pooled CRISPR screen 结合起来。每个空间 spot 由两组正交微流控 barcode 的交叉位置定义；同一个 spot 中的 RNA 分子带上空间 barcode 和 UMI，后续测序后即可回推到组织坐标。论文提供两种捕获策略 (`paper.md:41`)：

- **PAC, polyadenylated capture**：先在组织原位给 RNA 分子加 poly(A) tail，让 mRNA 和 sgRNA 都可以被含 poly(dT) 的 primer 捕获；后续做 barcode ligation、template switching、PCR、size selection 和 rRNA depletion (`paper.md:287-314`)。
- **DC, direct capture**：用 sgRNA scaffold 互补 primer 直接捕获 sgRNA，同时用 poly(dT) 捕获 mRNA；sgRNA 和 mRNA 使用不同 barcode 设计，最后并行建库测序 (`paper.md:275-305`)。

一个简化流程是：

```text
CRISPR-mutagenized tissue section
        |
        v
PAC or DC in situ capture
        |
        v
orthogonal DBiT barcodes + UMI
        |
        v
lysis -> template switching -> PCR -> sequencing
        |
        v
FASTQ barcode reformat + ST-pipeline alignment
        |
        v
spatial expression matrix + spatial sgRNA count matrix
        |
        v
ROI filtering, Seurat clustering, perturbation assignment,
Mixscape/pUMAP, DE/GSEA, noncoding RNA, Xenium/CODEX comparisons
```

### 输入和输出

**输入**包括：带 CRISPR library 的组织切片、PAC/DC 试剂和微流控 barcode、空间 ROI 图像、测序 reads、参考基因组/注释、barcode index、以及 downstream R 分析需要的空间表达矩阵和 sgRNA 计数矩阵。论文实验覆盖 small library、288-sgRNA mTSG library、Brunello genome-scale human library 和 Brie mouse genome-scale library (`paper.md:47`, `paper.md:71`, `paper.md:144`)。

**输出**包括：

- 每个 spot 的空间坐标和表达矩阵；
- 每个 spot 的 sgRNA / perturbation identity 或 burden；
- 组织结构对应的 GEX cluster；
- perturbation response embedding，例如 Mixscape score 和 pUMAP；
- perturbation-specific DE、pathway、tRNA/miRNA/lncRNA/ceRNA-style 网络；
- 与 Xenium 或 CODEX 的邻近切片验证结果。

### 论文中的关键实验逻辑

1. **技术和中等规模 library 验证**：Fig. 1 展示 Perturb-DBiT 设计、捕获质量、liver mTSG screen、MIPS 对比和 top perturbation 空间分布。论文报告 Perturb-DBiT 在 mTSG liver ROI 中比 MIPS 检出更多 sgRNA，ROC AUC 为 0.724，并且生物重复间 Jaccard similarity 为 0.78-0.96 (`paper.md:59-65`)。

2. **HT29 lung Brunello 大规模 screen**：Fig. 2 用 77,441 sgRNA 的 Brunello library 做肺转移定植模型。论文在一个 ROI 中检测到 235 unique sgRNA 和 5,740 sgRNA UMI，并在连续切片中看到 sgATG4A、sgMT1E、sgS100A4 等 top hits 稳定富集 (`paper.md:71-82`)。

3. **total RNA / 非编码 RNA**：Fig. 3 说明 PAC 不只读 mRNA，还读到 tRNA、miRNA、lncRNA 等 RNA class。论文把 top perturbation 与 tRNA pattern、miRNA-mRNA interaction、lncRNA/ceRNA-style 模块联系起来；这些结论主要是空间相关和网络假设，不等于直接因果证明 (`paper.md:88`, `paper.md:120-129`, `paper.md:182`)。

4. **Xenium 验证**：论文用相邻 FFPE 切片做 Perturb-DBiT 和 10x Xenium 对比。Xenium 需要预设基因和 sgRNA probe；Perturb-DBiT 是 sequencing-based，所以不受预设 probe panel 限制。论文报告 gene expression、sgRNA abundance 和 pathway-level changes 有正相关 (`paper.md:108-114`)。

5. **E0771 / TME 模型**：Fig. 4 用 Brie library 的 E0771 syngeneic lung model 展示 sgRNA burden、GEX cluster、ligand-receptor interpretation 和 CODEX protein imaging。论文把 sgZc3h12a、sgPax8、sgNeu4 等扰动与免疫浸润、肿瘤结构和 myeloid-rich TME 联系起来 (`paper.md:144-167`)。

### 本地代码如何对应论文

本地 `Perturb_DBiT/` 不是一个 pip/R package，而是分析脚本、Rmd notebook、revision notebook 和一些已生成 data/figure 资产的集合。代码能帮助理解 post-sequencing 分析，但不能完整自动复现实验。

| 论文/方法步骤 | 本地代码证据 | 匹配程度 |
|---|---|---|
| FASTQ 到空间表达矩阵 | `Sequence alignment /1-effective.sh:15-19`; `Sequence alignment /2-stpipeline_mouse.sh:1-30`; `Sequence alignment /changeid_mouse.sh:11-16` | Exact，但路径是占位符，需要本地环境和参考基因组。 |
| ROI 坐标提取 | `Spatial Data Visualization/Image_Processing.m:1-35` | Exact；从二值化组织图像生成 `position.txt`。 |
| Seurat 空间对象和 GEX clustering | `Spatial Data Visualization/Perturb_DBiT_Clustering.Rmd:36-92`, `205-259` | Exact / Notebook。 |
| liver mTSG sgRNA assignment 和 top hits | `MediumLibrary_MultiOmics/01_liv_0325_Preprocessing_v2.1.Rmd:47-139`; `03_liv_0325_PtbProcessing_v2.1.Rmd:62-172`, `219-239` | Exact / Notebook。 |
| MIPS/ROC 对比 | `MediumLibrary_MultiOmics/02_liv_0325_GexProcessing_v2.1.Rmd:364-420`; `README.md:790-842` | Partial / Notebook；逻辑存在，但不是独立模块。 |
| HT29 大规模 screen pUMAP/DE/GSEA | `LargeLibrary_MultiOmics/03_lung1214_PtbProcessing_v2.3.Rmd:58-75`, `128-208`, `233-324`, `432-572` | Partial；Monocle3 pseudotime 是预先读入的 RDS。 |
| 非编码 RNA assays 和 DE | `Revisions/Rev01_LungMet_allRNA_v3.1.Rmd:64-79`, `112-412`; `Revisions/Rev02_LungMet_DE_v0.34.Rmd:75-139`, `248-330`, `575-665` | Partial / revision notebook。 |
| Xenium 对比 | `Revisions/Rev09_xen_vs_DBit_v0.3.Rmd:37-73`, `151-198`, `204-275`; `Revisions/Rev08_xen_processing_v0.3.Rmd:270-380` | Partial / revision notebook。 |
| CODEX/TME | `Codex Analysis /Codex_Analysis.Rmd:27-50`, `99-157`; `Revisions/Rev04_sgRNA_Distrib_Bias.Rmd:27-109` | Partial / Not found；没有完整 E0771 ligand-receptor/TME workflow。 |

### 需要特别注意的边界

- `MISSING in code`：PAC/DC wet-lab chemistry、微流控 reagent 操作、原位 polyadenylation / direct capture 实验步骤，只在论文方法和图中描述，不是可执行代码。
- `Partial`：HT29 lung screen、noncoding RNA、Xenium、CODEX 等 final paper 分析主要依赖 Rmd/revision notebooks、预计算 RDS 和本地数据路径。
- `Not found`：没有找到单一的 final figure build driver；没有找到完整 E0771 Perturb-DBiT/TME ligand-receptor 分析 notebook；没有从 raw FASTQ 到所有 main/extended figures 的一键复现路径。
- 论文自己也指出局限：单张组织切片只能捕获 library 的空间子集，还没有真正 single-cell resolution，非编码 RNA 网络目前仍然需要进一步 functional validation (`paper.md:182`)。

### 如何学习这篇方法

先把 Perturb-DBiT 当成“空间 barcode + sgRNA/total RNA co-sequencing”的实验平台，而不是一个纯计算模型。理解时按三层读：

1. **Assay 层**：读 `paper.md:41` 和 `paper.md:275-314`，弄清 PAC/DC、barcode A/B/C/D、UMI、template switching、size selection。
2. **矩阵构建层**：读 alignment scripts、ROI MATLAB、generic Seurat clustering，理解 raw reads 如何变成 spot x gene 和 spot x sgRNA。
3. **生物解释层**：读 medium/large library Rmd、revision notebooks 和 figures，理解 sgRNA burden、pUMAP、DE/GSEA、noncoding RNA、Xenium/CODEX 是如何从矩阵上叠加出来的。

一句话总结：Perturb-DBiT 的创新不是一个新的机器学习模型，而是把 pooled CRISPR guide identity、spatial whole-transcriptome/total-RNA profiling 和组织图像对齐在同一个分析坐标系里；本地代码证明了不少 post-sequencing 分析步骤，但完整复现仍需要外部数据、预计算对象和未封装的实验/figure 工作流。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Perturb-DBiT Summary

### What Problem It Solves

Perturb-DBiT targets in vivo pooled CRISPR screening when the phenotype is spatial: tumor architecture, tissue neighborhoods, clonal expansion, noncoding RNA regulation, and immune microenvironment state. The paper argues that single-cell CRISPR screens and dissociation-based methods link perturbations to transcriptomes but lose tissue context, while imaging/FISH-style spatial CRISPR methods are usually constrained to targeted panels or incomplete RNA coverage (`paper.md:18-24`).

### What The Paper Introduces

Perturb-DBiT is a spatial functional genomics platform that co-barcodes sgRNAs and total RNA on the same tissue section, then sequences both modalities. The assay has two capture modes: PAC, which polyadenylates RNA molecules including sgRNAs before poly(dT)-based capture, and DC, which directly captures sgRNAs with scaffold-complementary primers while also capturing mRNA (`paper.md:41`). The output is a spatial expression matrix plus spatial sgRNA/perturbation information for downstream clustering, perturbation scoring, DE, pathway analysis, noncoding RNA analysis, Xenium comparison, and CODEX/TME interpretation.

### Main Evidence

- Technical performance: across mouse models and library scales, the paper reports robust sgRNA capture, high spatial transcriptome quality, and detection from small guide sets up to genome-scale settings (`paper.md:47`, `paper.md:53`).
- Liver mTSG screen: Fig. 1 shows tissue-aligned spatial GEX clusters, MIPS comparison, and top perturbation maps; the paper reports better sgRNA diversity/recapitulation than MIPS and AUC 0.724 (`paper.md:59-65`).
- HT29 lung Brunello screen: Fig. 2 shows large-library perturbation distributions across serial sections, iStar-enhanced spatial maps, and Xenium validation; the paper reports 235 unique sgRNAs and 5,740 sgRNA UMIs in one ROI, with repeated top-hit enrichment across adjacent sections (`paper.md:71-82`, `paper.md:108-114`).
- Noncoding RNA: Fig. 3 links sgRNA hits to tRNA, miRNA, lncRNA, and ceRNA-style patterns; the paper emphasizes total RNA capture beyond protein-coding transcripts (`paper.md:88`, `paper.md:120-129`).
- E0771/TME: Fig. 4 applies the platform to a syngeneic Brie-library model and combines spatial transcriptomes, sgRNA burden, ligand-receptor interpretation, and adjacent CODEX imaging (`paper.md:144-167`).

### Code And Reproducibility

The public repo is useful but notebook-centered. It contains FASTQ/ST-pipeline wrappers, ROI masking, Seurat spatial preprocessing, medium/large-library analysis notebooks, MIPS/ROC notebook logic, noncoding RNA revision notebooks, Xenium comparison notebooks, ZINB simulation, guide-distribution checks, and a generic CODEX template. Directly verified examples include alignment (`Perturb_DBiT/Sequence alignment /2-stpipeline_mouse.sh:1-30`), ROI masking (`Perturb_DBiT/Spatial Data Visualization/Image_Processing.m:1-35`), liver sgRNA assignment (`Perturb_DBiT/MediumLibrary_MultiOmics/01_liv_0325_Preprocessing_v2.1.Rmd:47-139`), MIPS/ROC comparison (`Perturb_DBiT/MediumLibrary_MultiOmics/02_liv_0325_GexProcessing_v2.1.Rmd:364-420`), Mixscape/pUMAP/DE/GSEA (`Perturb_DBiT/LargeLibrary_MultiOmics/03_lung1214_PtbProcessing_v2.3.Rmd:128-208`, `432-572`), and Xenium comparison (`Perturb_DBiT/Revisions/Rev09_xen_vs_DBit_v0.3.Rmd:37-73`, `151-198`, `204-275`).

Reproducibility status: **medium**. The paper provides GEO data accessions and a GitHub code link (`paper.md:359-368`), but the local snapshot relies on external GEO inputs, reference genomes, barcode tables, local R/Python environments, precomputed RDS objects, and placeholder paths. Wet-lab PAC/DC chemistry is paper-described but not executable code. `Not found` in the probed repo: a single final figure driver, a complete E0771 Perturb-DBiT/TME ligand-receptor workflow, and a fully end-to-end raw-to-final reproduction path.

### Bottom Line

Perturb-DBiT is best understood as a spatial CRISPR-total-RNA assay plus an analysis workflow for linking guide identity, tissue position, transcriptomic state, and noncoding RNA responses in native tissue. The code repository supports many post-sequencing analyses at notebook level, but the strongest claims remain a combination of paper/figure evidence plus selected source-verified notebook fragments rather than a turnkey software package.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
