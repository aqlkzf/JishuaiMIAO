---
layout: default
permalink: /paper-atlas/dbit-plus-652da08b/
title: "DBiT-plus"
nav: false
description: "空间转录组测得的基因很多，但一个 25–50 μm 的 DBiT 点位通常含有多个细胞；多重免疫荧光可以看到单细胞，却只能测有限的蛋白标记。若分别在相邻切片上做两种实验，即使切片来自同一组织块，细胞组成和几何结构也不会完全一致。 DBiTplus 的核心思路是：在同一张组织切片上先做空间转录组，再做多重蛋白成像，并让图像中真正看到的细胞约束 RNA 点位的拆分。 因此它把“全转录组覆盖”和“成像的单细胞空间分辨率”接到了一起。"
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
    <h1>DBiT-plus</h1>
    <p>Integration of imaging-based and sequencing-based spatial omics mapping on the same tissue section via DBiTplus</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02948-0" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DBiTplus 方法详解

### 它要解决什么问题？

空间转录组测得的基因很多，但一个 25–50 μm 的 DBiT 点位通常含有多个细胞；多重免疫荧光可以看到单细胞，却只能测有限的蛋白标记。若分别在相邻切片上做两种实验，即使切片来自同一组织块，细胞组成和几何结构也不会完全一致。

DBiTplus 的核心思路是：**在同一张组织切片上先做空间转录组，再做多重蛋白成像，并让图像中真正看到的细胞约束 RNA 点位的拆分。** 因此它把“全转录组覆盖”和“成像的单细胞空间分辨率”接到了一起。

### 实验创新：取走 cDNA，但保留组织

DBiT 的两组垂直微流道分别递送 $A_i$ 和 $B_j$ 条形码，组合后形成二维点位 $(i,j)$。难点是：怎样回收已条形码化的 cDNA，同时不把组织裂解掉？作者比较了 NaOH、DMSO 和 RNase H，最终采用耐热 RNase H 加 Triton X-100。RNase H 降解 RNA–DNA 杂交体中的 RNA，使 cDNA 从通透化细胞中释放，而切片仍能继续做 CODEX/CellScape 和 H&E。

这一步是 DBiTplus 与普通“相邻切片整合”的根本差异：RNA、蛋白和形态学信号都来自同一物理切片。

### 计算流程

```text
同一张切片
  ├─ DBiT 条形码 → RNase H 回收 cDNA → 测序 → 点位×基因矩阵 X
  └─ CODEX/CellScape 图像 → Mesmer 分割 → 细胞×蛋白矩阵 P
                                         │
单细胞 RNA 参考图谱 ── MaxFuse 配对 ─────┤
                                         ↓
                              已注释的成像细胞
                                         │
DBiT 与成像掩膜 ── 几何配准 ─────────────┤
                                         ↓
                          每个点位内各细胞类型数量 n
                                         │
参考表达特征 + 条件期望分配 ─────────────┤
                                         ↓
                        细胞类型纯化的 sub-spot 表达 Y
                                         │
                              Seurat WNN 联合分析
```

#### 1. 分割并提取蛋白信号

代码把核标记和膜/胞质标记组成 Mesmer 的双通道输入，得到整细胞标签掩膜。随后对每个细胞记录质心、面积，并在每个抗体通道上求像素强度总和。因此输出是“细胞 × 蛋白”矩阵。分割阈值需要针对样本调节，是重要误差来源。

#### 2. 给成像细胞赋予类型

MaxFuse 利用 RNA 与蛋白之间可对应的共享标记，把 mxIF 细胞同已注释的 scRNA-seq 参考细胞匹配。高可信配对形成 pivot cells，并继承参考标签。代码再用这些 pivot cells 的蛋白特征训练 RBF-SVM，把标签传播给未配对细胞。

#### 3. 把细胞放回 DBiT 点位

代码对 DBiT 和 mxIF 的组织掩膜做裁剪、翻转、缩放、旋转和平移，用均方误差寻找相似变换参数，再把成像细胞质心变换到 DBiT 坐标系。由此得到 $n_{st}$：点位 $s$ 中类型 $t$ 的细胞数。优势是它来自同一切片；局限是公开脚本中的裁剪范围和变换参数明显依赖具体样本。

#### 4. 条件期望拆分点位

令 $X_{sg}$ 是点位 $s$ 中基因 $g$ 的观测计数，$r_{tg}$ 是参考数据中类型 $t$ 的平均表达，则该点位的期望混合表达为

$$
\widehat{x}_{sg}=\sum_t n_{st}r_{tg}.
$$

代码把观测计数按各细胞类型的期望贡献比例分配：

$$
Y_{stg}=X_{sg}\frac{n_{st}r_{tg}}{\widehat{x}_{sg}}.
$$

这里的 $Y_{stg}$ 是“点位 $s$ 中细胞类型 $t$ 的纯 sub-spot 表达”。它不是每个成像细胞各自独立测得的转录组。如果一个点位有三种细胞类型，通常得到三个类型 sub-spots，而不是按细胞数生成很多单细胞表达谱。

#### 5. RNA–蛋白联合邻域

拆分后的 RNA 和相应蛋白特征作为 Seurat 的两个 assay，分别归一化和 PCA，再用 WNN 构造联合邻域、UMAP 和聚类。公开代码还把 RNA 权重乘以 3 并截断到 1，然后令蛋白权重为其补数；这是论文正文没有强调、但复现时必须注意的实现细节。

### 论文如何验证？

作者在冷冻小鼠胚胎、FFPE 小鼠胚胎、正常人淋巴结、边缘区淋巴瘤以及 CLL 向 DLBCL 转化样本中应用 DBiTplus。FFPE E11 胚胎与相邻切片标准 DBiT-seq 的相关系数为 $R=0.99$，共有 27,884 个基因；每个点位约检测 1,200 个基因和 3,300 个 UMI。

在人淋巴结中，作者把同切片 CODEX 得到的点位细胞组成作为参照，比较 TACCO、Cell2location 和 RCTD。TACCO 有 50% 的点位 Pearson 相关系数超过 0.6，Cell2location 为 36%。图像还直接显示了 RNA 区域、蛋白标记和组织结构之间的空间一致性。

### 怎样正确理解“单细胞分辨率”？

DBiTplus 的单细胞信息首先来自成像：细胞边界、位置和蛋白类型是真正逐细胞获得的。RNA 部分仍然从多细胞点位出发，通过图像中的组成和参考表达进行分配。因此更准确的说法是“成像指导的细胞类型分辨空间转录组”，而不是“每个细胞都被直接测序”。

### 复现边界

- 公开代码覆盖分割、蛋白提取、配准、MaxFuse、SVM、条件期望拆分、去卷积比较和 WNN，代码—论文一致性为中等。
- 未找到完整 FASTQ 到计数矩阵的流程、锁定的软件环境和单命令端到端入口。
- 多个脚本使用样本专属路径、裁剪和变换参数，并依赖仓库外的中间文件。
- Cell2location 以多个 notebook 提供，不是封装好的流水线。
- 湿实验 RNase H、成像和染色步骤没有代码对应，这是合理边界。
- `paper_supp1.md` 可读；`paper_supp2.pdf` 没有 Markdown，可能只存在于该 PDF 中的文字细节未被核验。

因此，这个仓库足以理解并审计关键计算思想，但不足以从原始数据一键重建论文全部结果。

### 本轮源码复核补充

本轮没有沿用旧 terminal 状态，而是重新核对当前 commit。Mesmer 以 `image_mpp=0.5`、`maxima_threshold=0.06` 和 `interior_threshold=0.25` 生成 whole-cell mask（`integration/segmentation_extraction/cell_segmentation.py:121-166`）；marker extraction 对每个 mask label 计算质心、面积和各通道总强度（`marker_extraction.py:29-68`）。这些量直接进入 MaxFuse/SVM 和几何映射，因而分割参数改变会贯穿全部 sub-spot 结果。

代码来源与论文匹配：repository URL、commit 和 DBiTplus 方法身份一致。需要保留的 mismatch 是覆盖范围而非来源身份：公开仓库从已生成的空间矩阵和成像文件开始，缺少 FASTQ-to-count、完整样本输入和湿实验 RNase H 实现；`ready_to_publish=true` 不代表端到端可执行。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## DBiTplus

### What problem does it solve?

Sequencing-based spatial transcriptomics measures many genes but at multicellular spot resolution; multiplexed imaging resolves individual cells but only for a selected protein panel. Combining adjacent sections is imperfect because the cells and tissue geometry differ. DBiTplus performs spatial transcriptomics, multiplexed immunofluorescence and H&E on the same section, then uses the imaged cells to constrain decomposition of the RNA spots.

### What is new?

The assay uses RNase H-mediated cDNA retrieval after DBiT spatial barcoding. This releases barcoded cDNA while retaining tissue architecture for CODEX/CellScape imaging. Computationally, Mesmer segments cells, MaxFuse transfers reference cell identities to the protein profiles, geometric registration maps those cells into DBiT spots, and a reference-signature conditional-expectation calculation divides each spot into pure cell-type sub-spots. Seurat WNN can subsequently combine sub-spot RNA and protein features.

The important interpretation is that “single-cell-resolved” means image-guided cell typing and cell-type-specific sub-spots. The method does not directly sequence a separate transcriptome from every segmented cell.

### Evidence and evaluation

The paper applies DBiTplus to frozen and FFPE mouse embryos, benign human lymph node, marginal-zone lymphoma and CLL-to-DLBCL transformation. In an FFPE E11 embryo, DBiTplus and standard DBiT-seq on an adjacent section had Pearson $R=0.99$, 27,884 overlapping genes, and roughly 1,200 genes and 3,300 UMIs per spot. Same-section imaging showed spatial agreement between RNA and protein markers.

For benign lymph node, CODEX-derived cell composition provided a ground truth for comparison of TACCO, Cell2location and RCTD. TACCO performed best among the reported comparisons: 50% of spots had Pearson correlation above 0.6, versus 36% for Cell2location. WNN separated cell types and exposed modality-specific contributions, with protein more informative for several T-cell subtypes and RNA more informative for some B-cell subtypes.

### Reproducibility assessment

**3/5 — conceptually reproducible, not turnkey.** The GitHub snapshot at commit `c1d1e010f590b371e7a46963a116f3e97c66c380` contains direct implementations of segmentation, marker extraction, registration, MaxFuse matching, SVM label propagation, conditional-expectation splitting, deconvolution comparisons and WNN. The overall code–paper fidelity is medium.

However, scripts use specimen-specific paths, image crops and transforms; many required intermediate matrices are absent; no locked environment or end-to-end runner is provided; and raw sequencing preprocessing is not included. Cell2location is represented by a notebook chain rather than a packaged pipeline. The wet-lab RNase H and imaging protocol naturally has no code analogue. `paper_supp1.md` is available, while `paper_supp2.pdf` has no Markdown conversion.

### Main limitations

- The spot-splitting model depends on accurate same-section segmentation, cell typing and registration.
- Reference mean expression is assumed to represent each cell type within the tissue.
- A sub-spot is a cell-type component of one spot, not necessarily one physical cell.
- Antibody-panel composition limits protein-based cell typing and affects modality weights.
- Several clinical demonstrations are discovery-oriented applications with limited sample counts rather than broad cohort validation.
- The released repository supports forensic reconstruction of the analysis but not one-command reproduction from raw data.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
