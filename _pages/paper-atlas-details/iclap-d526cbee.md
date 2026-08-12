---
layout: default
permalink: /paper-atlas/iclap-d526cbee/
title: "iCLAP"
nav: false
description: "FFPE 是临床病理最常见的保存形式，但固定会遮蔽表位，许多转录因子、免疫调节因子和衰老相关蛋白本来又很少。CODEX、CyCIF、IMC 等方法可以在同一切片上检测几十个蛋白，却主要依靠直接偶联抗体，灵敏度对低丰度抗原往往不够。TSA 利用 HRP 催化荧光酪胺在抗原附近沉积，可以放大信号，但沉积后的强荧光不容易被常规循环成像的温和漂白步骤去除，因此传统 TSA 面板通常难以继续扩展。"
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
      <span>Nature Communications · 2026</span>
    </div>
    <h1>iCLAP</h1>
    <p>iCLAP: an innovative method for integrable co-detection of low-abundance antigens with high-plex immunostaining</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-69752-y" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## iCLAP：把低丰度蛋白的放大检测接入高通量空间蛋白组

### 它要解决的矛盾

FFPE 是临床病理最常见的保存形式，但固定会遮蔽表位，许多转录因子、免疫调节因子和衰老相关蛋白本来又很少。CODEX、CyCIF、IMC 等方法可以在同一切片上检测几十个蛋白，却主要依靠直接偶联抗体，灵敏度对低丰度抗原往往不够。TSA 利用 HRP 催化荧光酪胺在抗原附近沉积，可以放大信号，但沉积后的强荧光不容易被常规循环成像的温和漂白步骤去除，因此传统 TSA 面板通常难以继续扩展。

iCLAP 的核心不是新的成像仪或机器学习模型，而是一条可循环的实验协议：先用 TSA 检测低丰度蛋白，成像后用强碱性过氧化氢加光照把荧光降回背景，再进入下一轮；所有 TSA 轮次结束后，同一张切片还能接入 IF、CyCIF、CODEX 或 IMC 检测高丰度标记。

### 从切片到多重图像的流程

```text
4 μm FFPE 切片
  → 脱蜡、复水、一次 HIER 抗原修复
  → [每个成像轮次通常顺序标记 3 个低丰度抗原]
       每个抗原：封闭 → 一抗 → anti-HQ → anti-HQ-HRP
                 → 一种 Opal-TSA 染料 → VectaPlex 去抗体
  → Hoechst 染核、整片成像
  → 2 M H₂O₂ + 3 mM EDTA / PBS, pH 12.5
    两块 5000 lux 光板之间处理 1 h
  → 下一轮 TSA，直到低丰度标记完成
  → 接 IF / CyCIF / CODEX / IMC 高通量面板
  → 跨轮次配准、细胞分割、强度与形态定量
```

这里有两个容易误读的细节。第一，“一轮 3 个抗原”不是三个抗体同时做 TSA；论文方法是顺序处理三个抗原，每次沉积一种 Fluorescein、Cy3 或 Cy5，期间用 VectaPlex 去除抗体，三个通道完成后才统一成像。第二，HIER 只在最开始做一次，之后依靠化学洗脱去抗体，避免每轮重复高温修复。

### 漂白为什么是关键

漂白液为 2 M H₂O₂、3 mM EDTA、PBS pH 12.5，并在两块 5000 lux 光板之间处理 1 小时。论文图 1 的四个时点是：染色前背景 r1、PAX6/Islet1 TSA 染色 r2、漂白后 r3、随后 insulin/glucagon IF 染色 r4。五个胰岛区域中，r3 与 r1 在 Cy5、TRITC 通道均无显著差异，而 r2 与 r3 显著不同。这支持“在该实验条件和两个通道中降到背景水平”，但不能外推为所有染料、组织和任意循环次数都完全无残留。补图报告 10 个循环后约 2% 组织损失，也仍需在新组织和新面板中重新验证抗原性与形态保持。

### 图 2–5 分别证明什么

图 2 直接比较 TSA 与常规 IF。P16 的图示 SNR 为 47.7 对 5.0；53BP1 即使把常规 IF 的抗体浓度提高 20 倍、孵育时间延长 20 倍，信号仍弱于 TSA。P21 和 P53 在所测试的常规 IF 条件下没有清晰阳性。这个结论限定于论文测试的抗体、组织和条件，并不等于每一种低丰度蛋白都固定获得十倍增益。

图 3 用两轮获得 6 个衰老相关标记：P16、P53、P21、53BP1 用 TSA，HMGB1、Lamin B1 用常规 IF。作者从超过 7 万个细胞中报告 9 个表达亚群，并看到 P16/53BP1 较高的亚群偏向胰岛、P53 较高的亚群偏向腺泡、P21 较高的细胞偏向导管。方法部分却写 K-means 识别 20 个表达亚型，公开代码没有说明 20 如何变成图中的 9，因此这一合并步骤不可复现。

图 4 把 iCLAP 接入 CyCIF，形成 12 标记面板。胰岛层面，P16 强度与胰岛面积正相关（$r=0.41$，$P<0.001$，$N=67$），与 insulin 的相关为 $r=-0.17$ 且不显著。单细胞层面的 P16、53BP1 与 insulin/glucagon 强度和核大小关系，是同一组切片中的关联，不是 P16 或 53BP1 改变胰岛功能的因果实验。

图 5 的面板数量应按图注读取：iCLAP-CODEX 是 3 个 iCLAP 标记加 40 个 CODEX 标记，共 43；iCLAP-IMC 是 3 加 28，共 31。图中 P21 与 panCK 共表达更常见，P53 与 panCK 共表达较少，并在多个供体及 IMC 数据中得到一致观察。它支持平台兼容性和细胞表型关联，不足以单独定义“衰老细胞身份”或机制。

### 计算分析如何接上实验

论文描述的分析链为：以 DAPI 做全局刚性加局部网格形变配准；StarDist 分割细胞核；将核边界外扩 4.5 μm 近似细胞边界；提取强度与形态；PCA 保留 95% 方差后做 K-means；UMAP 仅用于展示。胰岛则由 insulin 或 glucagon 阳性区域阈值化，再经开闭运算和填洞，并去掉小于 400 μm² 的区域。

这些核心步骤在本地 Zenodo 代码包中 **Not found**。代码包只有四个 notebook：

- `anova.ipynb` 内嵌图 1d 的 40 个强度值，用 Python 重做双因素 ANOVA 和 Tukey；论文原统计软件写的是 GraphPad Prism，因此这是重分析，不是原始执行路径。
- `Clusters similarity statistics.ipynb` 从手工写入的 9 维比例向量计算相关与分布距离，不能从图像得到聚类。
- `SNRana.ipynb` 使用机构内网 TIFF 路径，并曾保存 `IndexError` 输出；本地没有原图，不能复跑。
- `Venn diagram.ipynb` 从硬编码计数画图，而且注释的 tuple 顺序与 `matplotlib-venn` 的顺序不一致；主图 5c 实际是强度散点图，不是 Venn 图。

因此，公开代码对图 1d 提供较强的统计复核，对补充统计和绘图仅提供部分证据，不能重现从全切片到图 3–5 的完整分析。论文数据可用性声明称 ROI 定量和统计代码已存入 Zenodo，但当前本地记录没有找到 MATLAB 主流程，这是明确的论文—代码缺口。

### 如何正确使用 iCLAP

研究者首先应按目标丰度分层设计面板：只有确实需要放大的低丰度标记进入耗时的 TSA 循环，高丰度组织和细胞类型标记留给后续高通量平台。每一轮都要保留染色前、染色后、漂白后对照，并在目标组织上验证残留、抗原性和组织损失。图像分析要保存阈值、ROI 选择、配准误差和 20→9 聚类合并规则。生物学解释上应把“强度和空间共现”写成关联；若要证明衰老机制或功能改变，还需要独立的衰老判据、干预和功能实验。

### 结论

iCLAP 的实质贡献是把 TSA 的高灵敏度与 CODEX、CyCIF、IMC 的高 plex 能力串在同一 FFPE 切片上。论文对湿实验步骤给出了较细的可操作参数，并用五张主图展示漂白、灵敏度、6/12/31/43 plex 组合与胰腺应用。最大的复现边界在计算端：公开 notebook 主要从预计算值开始，核心 MATLAB 图像分析和原始整片数据不可直接获得。因此最稳妥的评价是“实验协议描述充分、平台兼容性得到示范，完整计算复现仍不成立”。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## iCLAP Summary

**Paper:** iCLAP: an innovative method for integrable co-detection of low-abundance antigens with high-plex immunostaining
**Authors:** Fan Wu, Shuyuan Zheng, ..., Denis Wirtz, Pei-Hsun Wu (Johns Hopkins University)
**Journal:** Nature Communications 17 (2026-02-24)
**DOI:** 10.1038/s41467-026-69752-y
**Type:** Technology platform

---

### Motivation & Novelty

#### Biological Problem

Spatial proteomics of FFPE tissue is valuable for studying disease pathology, but many senescence regulators, transcription factors, immune checkpoint markers, and secreted factors are difficult to detect with directly conjugated antibodies. TSA can enzymatically amplify local fluorescence; in this paper's P16 comparison, TSA produced about tenfold higher SNR than conventional IF under the tested conditions.

#### Limitations of Existing Methods

| Method | Journal | Year | Limitation |
|---|---|---|---|
| CODEX | Cell | 2018 | Primary-conjugated antibodies; intrinsically low sensitivity for low-abundance proteins |
| CyCIF / t-CyCIF | eLife | 2018 | Bleaching inadequate for TSA-deposited fluorophores; effectively limits TSA use to ≤8 markers |
| IMC (Imaging Mass Cytometry) | Nat Methods | 2014 | Metal-tagged antibodies; same sensitivity ceiling as other primary-conjugated platforms |
| 4i | Science | 2018 | Iterative immunofluorescence but no TSA integration |
| Standalone TSA (Opal) | Methods (Stack et al.) | 2014 | High sensitivity but ≤8 markers per section; cannot integrate with high-plex platforms |
| DNA-barcoded amplification for IMC | Nat Methods | 2023 (Hosogane) | IMC-specific; does not generalize to fluorescence platforms |

The fundamental trade-off: high-plex platforms (30-40 markers) use direct conjugation and cannot achieve TSA sensitivity, while TSA-based platforms achieve high sensitivity but cap at ≤8 markers because existing bleaching protocols cannot extinguish the intense TSA-deposited fluorescence.

#### What iCLAP Does Differently

iCLAP's core innovation is a bleaching chemistry — 2 M H₂O₂ + 3 mM EDTA in PBS at pH 12.5, between two 5000-lux light pads for 1 hour — that reduced the tested TSA-deposited signals to measured background levels in Figure 1 (r1 background versus r3 post-bleach). This enables:
1. Iterative TSA staining cycles (one antigen per cycle with intermediate antibody stripping)
2. Seamless handoff to CODEX, CyCIF, or IMC at the end of all TSA cycles
3. Total panel sizes exceeding 40 markers with TSA-level sensitivity for the low-abundance subset

The bleaching chemistry is superior to CyCIF's H₂O₂/NaOH protocol, which leaves residual TSA fluorescence after equivalent or longer exposure times (Supplementary Fig 1).

---

### Method Overview

iCLAP operates in two phases on the same FFPE tissue section:

**Phase 1 — Cyclic TSA staining** (for low-abundance antigens):
- Single heat-induced epitope retrieval (HIER) performed once
- Per antigen: casein block → primary antibody (40 min or overnight) → anti-HQ secondary (8 min) → anti-HQ-HRP (6 min) → TSA Opal dye (10 min) → VectaPlex chemical antibody strip
- 3 antigens per imaging cycle (Fluorescein/Cy3/Cy5 channels)
- Hoechst counterstain → whole-slide fluorescence imaging
- iCLAP bleaching: 2M H₂O₂ + 3mM EDTA, pH 12.5, 5000 lux, 1 hour → repeat

**Phase 2 — High-plex platform integration** (for high-abundance antigens):
- iCLAP-IF: fluorophore-conjugated antibodies (conventional IF)
- iCLAP-CyCIF: cyclic immunofluorescence protocol with iCLAP bleaching between cycles
- iCLAP-CODEX: PhenoCycler-Fusion with standard oligo-barcoded antibody panels
- iCLAP-IMC: Hyperion mass cytometry acquisition with metal-tagged antibody cocktail

**Image processing pipeline**:
- Registration: DAPI-based, global rigid + local deformable (500-pixel grid, libvips OME-TIFF)
- Segmentation: StarDist on DAPI channel, 4.5 μm expansion for cell boundaries
- Feature extraction: Intensity (nucleus/cell), morphology (area, aspect ratio, circularity)
- Clustering: Methods state K-means identifies 20 expression subtypes on PCA-reduced z-scored features, while Figure 3 reports 9 clusters; the unreported 20→9 mapping is a reproducibility gap. UMAP is used for visualization.

For detailed mathematical formulation, see `doc_method.md`. For code-paper mapping, see `doc_code.md`.

---

### Evaluation

#### Sensitivity Validation (Figure 2)

TSA provides 10-fold SNR improvement over conventional IF for P16 (SNR 47.7 vs 5.0). For 53BP1, TSA at 1:1000/40 min outperforms IF at 1:50/12 h (20× higher antibody concentration, 20× longer incubation). P53 and P21 are not detectable with IF under any tested condition. 29 total antibodies against senescence markers validated for TSA-based detection in FFPE.

#### Bleaching Efficiency (Figure 1d)

Quantitative validation across 5 biological replicates: post-bleach signal (r3) is statistically indistinguishable from pre-staining background (r1): P=1.00 for CY5, P=0.999999997 for TRITC. Tissue integrity across 10 cycles: ~2% loss, comparable to CyCIF.

#### 6-Plex Senescence Profiling (Figure 3)

In 63-year-old healthy pancreas (>70,000 cells, 10 ROIs): 9 distinct senescence subtypes identified. Senescence markers are largely mutually exclusive at single-cell level (no dominant P16+P21+P53 triple-positive population). Compartment-specific patterns: P16/53BP1 enriched in islets (cluster 9); P53 in acini (cluster 4); P21 in ducts (cluster 6). Cluster composition reproducible across adjacent sections (Pearson r=0.959 between sections).

#### iCLAP-CyCIF Islet Biology (Figure 4)

At islet level: P16 positively correlates with islet area (r=0.41, P<0.001, N=67 islets) and negatively with insulin (r=−0.17, ns). At single-cell level: P16+ β cells have HIGHER insulin (+16-39%) than P16- β cells — the apparent paradox explained by islet composition shifts (larger islets lose insulin+ cells while individual beta cells upregulate insulin in senescent state). 53BP1+ β cell nuclei are ~50% larger than 53BP1- cells, consistent with senescence-associated nuclear morphology.

#### 40+ Plex Integration (Figure 5)

iCLAP-CODEX (43 markers = 3 iCLAP + 40 CODEX) showed more frequent panCK co-expression among P21+ than P53+ cells; the paper reports 65% of P21+ cells and 10% of P53+ cells as panCK+. A 31-marker iCLAP-IMC experiment (3 + 28) showed the same qualitative association. These are phenotype associations, not causal or definitive senescence-state assignments.

#### Tissue Generalizability

iCLAP 6-plex senescence panel applied to pancreas, cervix, breast, ovary, skin, and liver (TMA sections). Consistent detection of P21/P53/P16 in tumor vs normal tissues across all organs. Healthy tissues show low senescence marker signal; tumor tissues show substantial expression.

---

### Reproducibility

**Rating: 2/5**

**Justification**:
- The core experimental workflow (TSA staining, bleaching chemistry, microscopy setup) is described in detail with sufficient specificity for a wet lab to reproduce. Bleaching solution composition (2M H₂O₂, 3mM EDTA, pH 12.5, 5000 lux, 1 h) is precisely specified.
- Antibody catalog numbers and dilutions are provided in Supplementary Data 2.
- However, the computational analysis pipeline — the most complex part — is only partially public. The MATLAB custom code for cell segmentation, K-means clustering, UMAP, islet segmentation, and morphological analysis is NOT deposited. Only 4 statistical post-processing notebooks (Zenodo) are available.
- The collapse from 20 K-means clusters to 9 reported clusters is undocumented in public code.
- Quantitative data (Zenodo deposits) and representative ROIs are available, but raw whole-slide images are not public (size + ethics restrictions).
- Reproducing the biological findings requires the proprietary MATLAB pipeline, custom microscopy hardware (Nikon Ti-E with SpectraX), and institutional-grade tissue archives.

**Practical notes**:
- The bleaching chemistry is equipment-agnostic and accessible (household-grade H₂O₂ + light pads)
- The VectaPlex antibody removal kit (Vector Laboratories) is a commercial product
- StarDist segmentation (Python, pre-trained model) is fully public and reproducible
- `anova.ipynb` can reanalyze embedded Figure 1d values after an environment is assembled. Other notebooks depend on hard-coded intermediates or institutional network TIFF paths and are not end-to-end runnable from this snapshot.

**Environment**: Python 3.x; notebooks use numpy, pandas, statsmodels, scipy, matplotlib, matplotlib-venn, tifffile. No conda/pip requirements file provided.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
