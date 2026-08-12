---
layout: default
permalink: /paper-atlas/maldi-msi-imc-a0723d18/
title: "MALDI-MSI-IMC"
nav: false
description: "研究者希望同时知道两个问题： 组织中某个位置有哪些代谢物、丰度多高？ 这些代谢信号来自哪类细胞，例如癌细胞、巨噬细胞或 T 细胞？ MALDI 质谱成像（MALDI-MSI）可以直接测量组织中的代谢物，但像素通常比单个细胞大，而且本身不能给细胞做丰富的免疫分型。成像质谱流式（IMC）可以在 1 µm 像素上检测多种金属标记抗体并分割细胞，却不直接测量完整代谢谱。"
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
      <span>Nature Methods · 2024</span>
    </div>
    <h1>MALDI-MSI-IMC</h1>
    <p>Integration of mass cytometry and mass spectrometry imaging for spatially resolved single-cell metabolic profiling</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MALDI-MSI–IMC：在同一张组织切片上实现空间单细胞代谢表型分析

### 1. 这篇论文要解决什么问题？

研究者希望同时知道两个问题：

1. 组织中某个位置有哪些代谢物、丰度多高？
2. 这些代谢信号来自哪类细胞，例如癌细胞、巨噬细胞或 T 细胞？

MALDI 质谱成像（MALDI-MSI）可以直接测量组织中的代谢物，但像素通常比单个细胞大，而且本身不能给细胞做丰富的免疫分型。成像质谱流式（IMC）可以在 1 µm 像素上检测多种金属标记抗体并分割细胞，却不直接测量完整代谢谱。论文的目标是把两者放到**同一张新鲜冷冻切片**上，并把 MALDI-MSI 的代谢信号分配给 IMC 分割出的单细胞（`paper.md:18-21`, `:35-38`）。

### 2. 为什么已有方案不够？

- 细胞解离后的单细胞转录组或蛋白组会丢失空间位置，而且基因或酶只是代谢状态的间接代理。
- Goossens 等在 *Cell Metabolism* 2022 中将多重免疫荧光与 MSI 用于髓系代谢环境分析，但不同或连续切片之间的配准困难，且并非同一批细胞。
- SpaceM（*Nature Methods*, 2021）等在 MALDI-MSI 后进行免疫荧光或免疫组织化学，可以保留同片空间信息，但可检测的蛋白靶标数量低于 IMC。
- 其他把 IMC 与 MSI 结合的方案可能受空间分辨率、灵敏度或固定组织代谢物损失限制。论文特别指出：相邻 5 µm 切片的组织形态和单个免疫细胞位置也会明显不同，因此“连续切片近似同一张切片”并不可靠（`paper.md:61`; `supplementary_information.md:41-47`, `:105-109`）。

### 3. 核心创新

这不是一个新的深度学习模型，而是一套实验与计算紧密配合的技术平台：

- 在 5 µm 新鲜冷冻切片上先做 MALDI-MSI，再做 IMC；
- 优化 MALDI 激光，避免组织损伤和抗原信号下降；
- 去除 MALDI 基质后加入甲醛固定，并改用适配 FFPE 的抗体面板；
- 把 5 × 5 µm 的 MALDI-MSI 像素配准到 1 × 1 µm 的 IMC 网格；
- 利用细胞分割掩膜，按照细胞与 MSI 像素的重叠面积计算每个细胞的代谢物相对丰度。

### 4. 整体流程

```text
5 µm 新鲜冷冻组织切片
    ↓
MALDI 基质升华
    ↓
MALDI-MSI
    ├─ 5 × 5 µm oTOF：高空间分辨率丰度图
    └─ 10 × 10 µm TIMS：利用 CCS 辅助代谢物注释
    ↓
去除 MALDI 基质
    ↓
甲醛固定 + 金属标记抗体染色
    ↓
1 × 1 µm IMC 成像
    ↓
背景去除、细胞分割、蛋白表型定义
    ↓
MALDI-MSI 与 IMC 视觉标志配准
    ↓
每个 5 × 5 µm MSI 像素映射到 25 个 IMC 像素
    ↓
按细胞覆盖面积计算蛋白和代谢物均值
    ↓
合并细胞表型、蛋白强度、代谢物相对丰度
    ↓
热图、Wilcoxon/FDR、UMAP、k-means 分析
```

### 5. 实验部分的关键技巧

#### 5.1 为什么使用 5 µm 切片？

IMC 常用约 4–5 µm 切片，而 MALDI-MSI 往往使用 10–12 µm。作者比较后发现，5 µm 与 10 µm 切片在信号强度和代谢物空间分布上没有明显差异，因此选择 5 µm 来兼容两种技术（`supplementary_information.md:18-26`）。

#### 5.2 为什么 MALDI-MSI 必须先做？

IMC 会烧蚀组织，所以顺序只能是 MALDI-MSI → IMC。MALDI 激光如果调得不好，会在组织上留下明显网格并降低后续 IMC 信号；补充图 1 直接展示了优化前后的差别。

#### 5.3 为什么使用 FFPE 抗体面板和后固定？

最初的新鲜冷冻抗体面板在 MALDI 流程后信号弱、形态标记失败。作者推测室温处理损伤了组织稳定性和表位，于是在去除基质后加入甲醛固定，并采用适配 FFPE 的抗体面板。补充图 1 显示该方案的形态和标记特异性明显更好（`supplementary_information.md:28-40`）。

### 6. 代谢物注释与 IMC 表型

MALDI-MSI 使用 timsTOF fleX MALDI-2。5 × 5 µm oTOF 数据用于单细胞空间丰度，10 × 10 µm timsON 数据用于离子淌度/CCS 辅助注释。作者在 T-ReX³ 检峰后，用 *m/z*、同位素模式和 CCS 与脂质数据库匹配，并保留质量误差 <10 ppm、CCS 误差 <5% 的去质子化离子（`paper.md:79`）。补充表 3 包含 112 个注释条目，主要是甘油磷脂。

IMC 端通过 Ilastik 去背景，Ilastik/CellProfiler 建立细胞掩膜，ImaCytE 提取单细胞标记强度，再依据蛋白组合定义癌细胞、成纤维细胞、血管、T 细胞、浆细胞、树突细胞、巨噬细胞、单核细胞等表型（`paper.md:88`; `supplementary_information.md:84-96`）。

### 7. 计算核心：如何把粗像素变成单细胞代谢值？

#### 7.1 网格映射

IMC 像素为 1 × 1 µm，MALDI-MSI 像素为 5 × 5 µm，因此每个 MSI 像素覆盖 25 个 IMC 像素。设 IMC 像素集合为

$$
{X}_{i}=\left\&#123;&#123;x}_{1},\,{x}_{2},\,\ldots,\,{x}_{N}\right\},
$$

MSI 像素集合为

$$
{Y}_{j}=\left\&#123;&#123;y}_{1},\,{y}_{2},\,\ldots,\,{y}_{M}\right\},
$$

则 $M=N/25$，映射函数 $y_j=f(x_i)$ 返回 IMC 像素 $x_i$ 所在的 MSI 像素（`paper.md:94-100`）。

代码把这个关系写得非常直接：

```python
def High_to_low(pixel_x, pixel_y):
    return int(pixel_x / 5), int(pixel_y / 5)
```

即两个坐标都除以 5 并取整（`MALDI_MSI_IMC_coregistration.py:35-36`）。

#### 7.2 单细胞 IMC 蛋白表达

若细胞 $c_k$ 包含 $m_k$ 个 IMC 像素，$P_{i,p}$ 是像素 $x_i$ 上蛋白特征 $p$ 的强度，则

$$
{\bar{P}}_{k,p}=\frac{1}&#123;&#123;m}_{k}}\mathop{\sum }\limits_{i=1}^&#123;&#123;m}_{k}}{P}_{i,p}.
$$

代码构建含 `Cell_idx` 和所有 IMC 通道的像素表，然后执行 `groupby("Cell_idx").mean()`，与论文公式完全一致（`paper.md:103-109`; `MALDI_MSI_IMC_coregistration.py:121-133`）。

#### 7.3 单细胞代谢物表达

若 $T_{j,t}$ 是 MSI 像素 $y_j$ 上代谢特征 $t$ 的强度，则细胞级代谢值为

$$
{\bar{T}}_{k,t}=\frac{1}&#123;&#123;m}_{k}} \mathop{\sum }\limits_{i=1}^&#123;&#123;m}_{k}}{T}_{f(i),t}.
$$

直观理解：先把一个 5 × 5 µm MSI 像素的值复制给它覆盖的 25 个 IMC 像素，再对属于某个细胞的全部 IMC 像素求平均。因此，一个 MSI 像素对某个细胞的权重等于该细胞在该像素内覆盖的 1 µm 像素数量，也就是近似覆盖面积（`paper.md:97`, `:112-115`）。

代码为每个 MSI 像素保存一个重叠细胞 ID 列表；某个细胞覆盖多少个高分辨率像素，其 ID 就出现多少次。随后 `explode()` 并按 `Cell_idx` 求均值，实现与公式一致的加权（`MALDI_MSI_IMC_coregistration.py:201-243`）。

#### 7.4 重要限制：这不是像素解混

如果一个 MSI 像素覆盖两个细胞，这两个细胞都会继承同一个代谢谱，只是权重不同。方法不能判断该像素内的代谢物到底由哪个细胞产生。Extended Data Fig. 1d 显示，含组织的 MSI 像素中只有约 30% 通常包含单个细胞，因此混合像素是核心限制，不是边缘情况（`paper.md:38`）。

### 8. 后续分析和主要结果

作者把表型、IMC 强度和代谢物相对丰度合并后进行：

- 细胞表型 × 甘油磷脂热图；
- Wilcoxon 检验和 FDR 校正；
- UMAP（`n_neighbors=5`, `min_dist=0.05`, `n_epochs=1000`）；
- 基于代谢物的 $k$-means 聚类（`paper.md:118-127`）。

主要发现包括：

- 癌细胞与基质–免疫细胞在代谢空间中明显分离；
- PI(34:1) 更偏向角蛋白丰富的癌细胞区域，PC(37:5) 更偏向波形蛋白丰富的基质区域；
- CD204⁺ 巨噬细胞富集 PG(40:7) 和 LPI(18:1)；
- 巨噬/单核细胞的代谢聚类并不等同于 IMC 蛋白表型，说明同一蛋白表型内部仍存在代谢状态差异；
- 一个代谢簇富集 PE(O-36:5)、PE(O-38:5) 和 PA(36:1)（`paper.md:41-55`）。

### 9. 代码与论文的一致性

总体一致性为**中等**：

- 5:1 网格映射：Exact；
- IMC 单细胞均值公式：Exact；
- MSI 重叠面积加权公式：Exact；
- 相对丰度归一化和表型合并：核心逻辑存在，但依赖固定列号和文件顺序；
- 图像配准：只有手工旋转和裁剪参数，没有自动配准；
- UMAP、Wilcoxon/FDR、热图、$k$-means 和完整作图 R 脚本：**Not found**。

仓库只有两个顶层 Python 脚本，没有依赖环境、测试、CLI、示例输入或端到端工作流。第二个脚本还假设三个目录的 `os.listdir()` 文件顺序一致，并用正则表达式解析字符串化的细胞 ID 列表，因此需要谨慎重构后再用于新数据。

### 10. 如何理解这项工作的价值？（分析性解读）

这项工作的价值主要在“实验对象的一致性”和“分辨率桥接”：同一个细胞先处于 MALDI-MSI 的代谢图中，随后又处于 IMC 的蛋白与形态图中；计算方法再用明确的像素覆盖关系把两者连接起来。它比连续切片更忠实，也比少数免疫荧光标记提供更丰富的细胞分型。

但输出应理解为“分割细胞所覆盖 MSI 像素的面积加权代谢信号”，而不是严格的、无混合的单细胞质谱。论文在三例 CRC 上证明了可行性和生物学信息量；更广泛的泛组织应用、细胞级解混和完全自动化仍是后续问题。

### 11. 证据边界

- **论文直接报告：** 同片顺序采集、两条像素聚合公式、三例 CRC/每例两个 ROI、22 种细胞表型、112 个代谢物注释以及文中列出的脂质差异。
- **代码直接验证：** 固定 5:1 坐标映射、IMC 按细胞求均值、MSI 按重叠像素数加权、细胞内相对丰度归一化和表型/强度表合并。
- **本文分析性解读：** 该输出更准确地说是“细胞覆盖区域的面积加权 MSI 信号”，不能等同于无混合的单细胞质谱。
- **缺失证据：** 自动配准、依赖环境、测试、仓库内示例输入、端到端运行器以及下游 R 分析/作图代码均未在完整 GitHub 快照中找到；因此不能仅凭公开代码复现全部统计图。
- **假设生成：** 本文未把潜在机制假设当作论文结论；例如脂质差异是否由特定细胞内代谢通路驱动，仍需独立实验验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MALDI-MSI–IMC: same-section spatial single-cell metabolic profiling

### What problem does the paper solve?

Metabolite imaging and cellular immunophenotyping usually operate at different spatial resolutions and often on different tissue sections. Dissociation loses tissue context, while consecutive sections do not contain the same individual cells. This paper develops a same-section workflow that measures metabolites by matrix-assisted laser desorption/ionization mass spectrometry imaging (MALDI-MSI), then measures protein markers by imaging mass cytometry (IMC), and assigns the coarse MSI signal to IMC-segmented cells (`paper.md:18-21`, `:35-38`).

### What is new?

The contribution is a coupled experimental and computational technology:

1. A 5-µm fresh-frozen section is analyzed first by MALDI-MSI and then, after matrix removal and formalin fixation, by IMC.
2. An adapted FFPE antibody panel preserves IMC signal after the room-temperature MALDI workflow.
3. MALDI-MSI at 5 × 5 µm is registered to IMC at 1 × 1 µm on the same section.
4. Each MSI pixel is mapped to 25 IMC pixels, and a cell's metabolite value is computed as an overlap-area-weighted mean of the MSI pixels it occupies.

The same-section design is important: supplementary images show that adjacent 5-µm sections differ in both tissue structure and individual immune-cell positions, even when roughly aligned (`supplementary_information.md:38-47`, `:105-109`).

### How does the computational integration work?

For a cell $c_k$ containing $m_k$ IMC pixels, protein feature $p$ is averaged as

$$
{\bar{P}}_{k,p}=\frac{1}&#123;&#123;m}_{k}}\mathop{\sum }\limits_{i=1}^&#123;&#123;m}_{k}}{P}_{i,p}.
$$

If $T_{j,t}$ is metabolite feature $t$ at MSI pixel $y_j$, and $f(i)$ maps IMC pixel $x_i$ to its containing MSI pixel, then

$$
{\bar{T}}_{k,t}=\frac{1}&#123;&#123;m}_{k}} \mathop{\sum }\limits_{i=1}^&#123;&#123;m}_{k}}{T}_{f(i),t}.
$$

Repeating the MSI value once for every overlapping 1-µm IMC pixel makes the mean proportional to overlap area (`paper.md:94-115`). It does not deconvolve mixed pixels: one MSI pixel may contribute to several cells, and only about 30% of tissue-containing MSI pixels contain a single cell (`paper.md:38`).

### Experimental and analysis pipeline

The study used three colorectal cancer specimens with two imaged areas per sample. High-resolution oTOF acquisition supplied 5 × 5 µm abundance images, while TIMS/CCS-assisted data supported annotation. T-ReX³ feature finding and MetaboScape/Lipid Maps matching yielded 112 selected metabolites, mainly glycerophospholipids (`paper.md:70-88`, `:127`; Supplementary Table 3).

IMC preprocessing used Ilastik, CellProfiler and ImaCytE for background removal, segmentation and cell-level marker extraction. Twenty-two phenotypes were defined from metal-labeled protein markers. After integration, the authors used phenotype heatmaps, Wilcoxon tests with FDR correction, UMAP and $k$-means clustering (`paper.md:88`, `:118-127`).

### Main findings

- Cancer cells separate from stromal–immune cells in metabolite-feature space. Spatial images associate PI(34:1) with keratin-rich cancer regions and PC(37:5) with vimentin-rich stromal regions (Figure 1).
- Plasma B cells and CD204⁺ macrophages show distinctive glycerophospholipid profiles, although most immune phenotypes are mixed in metabolite UMAP space.
- PG(40:7) and LPI(18:1) are enriched in CD204⁺ macrophages relative to other stromal/immune cells (Figure 2).
- Macrophage/monocyte $k$-means clusters reveal metabolic substructure not captured by IMC phenotype labels; one cluster is enriched for PE(O-36:5), PE(O-38:5) and PA(36:1) (`paper.md:41-55`).

These results are proof-of-principle evidence that direct metabolic measurements can distinguish both broad tissue compartments and finer within-lineage states.

### What do the figures establish?

Figure 1 visually connects the acquisition pipeline to compartment-level metabolic separation and shows that two example lipids spatially follow keratin- or vimentin-rich regions. Extended Data Figure 1 makes the pixel-weighted estimator explicit and shows that mixed-cell MSI pixels are common. Supplementary Figure 1 supports the critical experimental choices—laser tuning, 5-µm sections and the adapted FFPE panel—while Supplementary Figure 2 shows why same-section measurement is preferable to adjacent sections. Figure 2 and Extended Data Figures 2–3 support metabolic heterogeneity within myeloid cells.

### Code and data reproducibility

**Reproducibility rating: 3/5.**

Data and example inputs are linked through Figshare, and the GitHub repository is the paper's own implementation. The central equations match the released code well:

- integer division by 5 implements the fixed IMC-to-MSI mapping;
- `groupby(Cell_idx).mean()` implements IMC per-cell means;
- repeating cell IDs by overlapping mask pixels and grouping implements the weighted MSI mean;
- the second script normalizes metabolite vectors and merges phenotype/IMC tables.

Overall code fidelity is **medium**. The repository contains only two hard-coded top-level Python scripts. Registration uses a sample-specific 180° rotation and crop offsets rather than an automated optimizer. There is no environment file, test suite, bundled example data, CLI, or end-to-end runner. The R code for UMAP, Wilcoxon/FDR analysis, heatmaps, $k$-means and published figure reproduction is **Not found**. The integration script also assumes fixed column positions and matching unsorted file order across folders (`doc_code.md`).

### Limitations

- Only three CRC samples and two ROIs per sample were analyzed, limiting biological generalization.
- The biological analysis emphasizes glycerophospholipids.
- Coarse MSI pixels frequently contain multiple cells, so the method assigns shared signal rather than resolving the true contribution of each cell.
- Image registration is manual/sample-specific in the released code.
- Full reproduction depends on vendor software, external Figshare data, manual preprocessing/alignment and unreleased downstream R workflows.

### Bottom line

MALDI-MSI–IMC is a convincing same-section technology for linking spatial metabolite abundance to richly phenotyped individual cells. Its strongest contribution is the coordinated assay design and transparent overlap-weighted resolution mapping. The released Python code verifies that computational core, but the public repository is a research snapshot rather than a complete reproducible analysis package.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
