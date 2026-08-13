---
layout: default
permalink: /paper-atlas/velocyto-8638cb10/
title: "Velocyto"
nav: false
description: "普通单细胞 RNA 测序给出的通常是某一时刻的静态表达量。对于发育、分化、再生这类动态过程，仅靠静态表达矩阵很难判断一个细胞下一步会往哪个状态走。La Manno 等人在 Nature 2018 提出 RNA velocity：利用同一份 scRNA-seq 数据中未剪接 mRNA（unspliced/nascent）和已剪接 mRNA（spliced/mature）的相对关系，估计每个细胞表达状态的时间导数，也就是“速度” 。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature · 2018</span>
    </div>
    <h1>Velocyto</h1>
    <p>RNA velocity of single cells</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-018-0414-6" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Velocyto">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/velocyto-team/velocyto.R" target="_blank" rel="noopener noreferrer" aria-label="Open code for Velocyto">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Velocyto / RNA velocity 方法中文解读

### 这篇文章解决什么问题？

普通单细胞 RNA 测序给出的通常是某一时刻的静态表达量。对于发育、分化、再生这类动态过程，仅靠静态表达矩阵很难判断一个细胞下一步会往哪个状态走。La Manno 等人在 *Nature* 2018 提出 **RNA velocity**：利用同一份 scRNA-seq 数据中未剪接 mRNA（unspliced/nascent）和已剪接 mRNA（spliced/mature）的相对关系，估计每个细胞表达状态的时间导数，也就是“速度” (`paper source/nature_html/paper.md:9-13`)。

### 为什么可行？

作者观察到，常见单细胞协议并不只捕获成熟 mRNA。SMART-seq2、STRT/C1、inDrop、10x Chromium 等数据中有相当比例 reads 来自内含子区域，论文报告约 15-25% reads 含有未剪接 intronic sequence，并用代谢标记验证这些 reads 可作为新生/前体 mRNA 信号 (`paper.md:20-27`)。

直觉是：

- 如果一个基因的未剪接 RNA 比稳态预期更多，说明这个基因刚被诱导，未来已剪接表达量会上升；
- 如果未剪接 RNA 比稳态预期更少，说明这个基因正在被抑制，未来已剪接表达量会下降。

### 核心模型

Fig. 1b 给出了最重要的动力学式子：

```text
ds/dt = u - γs
```

其中：

- `s`：已剪接 mRNA abundance；
- `u`：未剪接 mRNA abundance；
- `γ`：基因特异的降解/稳态斜率参数；
- `ds/dt`：RNA velocity，即已剪接表达量的变化率。

Fig. 1d 展示稳态线 `u = γs`。点在稳态线上方时 `u > γs`，表示 induction / 表达上升；点在下方时 `u < γs`，表示 repression / 表达下降。正文也说明 RNA velocity 是 spliced mRNA abundance 的一阶导数，由 unspliced 产生和 mRNA degradation 的平衡决定 (`paper.md:35-42`)。

### 计算流程

可以把 Velocyto 的流程理解为：

```text
输入：spliced count matrix s + unspliced count matrix u
        │
        ▼
按基因拟合稳态关系，估计 γ
        │
        ▼
计算 v = ds/dt ≈ u - γs
        │
        ▼
外推每个细胞的未来表达状态
        │
        ▼
把高维 velocity 投影到 PCA/t-SNE/其他 embedding 上，用箭头解释细胞命运方向
```

代码中，R 包的核心函数是 `gene.relative.velocity.estimates`，它接收 `emat`（表达/已剪接矩阵）和 `nmat`（nascent/未剪接矩阵），先检查细胞列是否一致，再交集基因 (`velocyto.R/R/momentum_routines.R:78-120`)。随后代码拟合并保存 `gamma`，计算 `deltaE` (`:397-418`)。辅助函数 `t.get.projected.delta` 的注释直接写明它根据 `x'=(y-o)-gamma*x` 计算 projected delta (`:2398-2412`)。可视化层面，`show.velocity.on.embedding.cor` 和 `show.velocity.on.embedding.eu` 负责把高维速度投影为 embedding 上的箭头 (`:1049-1140`, `:1335-1395`)。

### 论文中的主要验证

1. **Fig. 1：模型直觉**
   图中同时展示未剪接 reads 的比例、`ds/dt = u - γs` 动力学、稳态相图、以及 circadian 数据中的表达外推，是整篇方法的核心图。

2. **Fig. 2：chromaffin 分化**
   Velocity 箭头沿着 sympathoadrenal progenitors 到 chromaffin cells 的分化桥移动；论文还用 EdU pulse labelling 估计这个数据中的外推时间大约为 2.5-3.8 小时 (`paper.md:43-62`)。

3. **Fig. 3：小鼠 hippocampus 分支命运**
   Velocity field 描述 granule、CA、subiculum、neuroblast、OPC 等多个神经谱系分支，显示该方法不仅能给局部箭头，还能支持分支命运推断 (`paper.md:64-80`)。

4. **Fig. 4：人胚胎脑发育**
   沿 principal curve 观察 unspliced 与 spliced 曲线的时间错位，展示 glutamatergic neurogenesis 中的转录动力学 (`paper.md:90-97`)。

### 代码复现情况

论文 Code availability 写明 Velocyto 在 `http://velocyto.org` 提供 R 和 Python library 以及 notebooks (`paper.md:216-219`)。本 workspace 克隆的是 R 版本 `velocyto-team/velocyto.R`，commit 为 `83e6ed92c2d9c9640122dcebf8ebbb5788165a21`。核心估计函数与论文模型有直接对应关系，因此核心算法匹配度较好；但 Python library、远程 notebooks、Supplementary Notes markdown 没有纳入本 workspace，所以完整复现论文所有图仍然不完整。

### 学习这个方法时最重要的点

- RNA velocity 不是重新训练一个深度模型，而是从同一份单细胞数据中区分未剪接/已剪接 RNA 后做动力学外推。
- `γ` 的估计非常关键：它定义了每个基因的稳态线，决定哪些细胞/基因被判断为上升或下降。
- 高维 velocity 与二维图上的箭头不是同一层：先在基因表达空间计算 velocity，再通过邻域/相关性/投影方法显示到 embedding 上。
- 论文结论应区分三类证据：主文和图像支持的生物学结论、R 代码中验证到的实现行为、以及本 workspace 没有覆盖的 notebooks/Python/补充材料细节。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary — RNA velocity of single cells (Velocyto)

### Problem

Single-cell RNA-seq usually captures a static snapshot of each cell. That makes it difficult to infer where a differentiating cell is going next, especially in development or regeneration. La Manno et al. introduce **RNA velocity**, a way to estimate the time derivative of gene expression from standard scRNA-seq data by separating unspliced/nascent and spliced/mature mRNA counts (`paper source/nature_html/paper.md:9-13`).

### Key Idea

The method uses the fact that many scRNA-seq protocols contain intronic reads. The paper reports that 15-25% of reads in SMART-seq2, STRT/C1, inDrop, and 10x Chromium datasets contain unspliced intronic sequence, supporting the use of unspliced counts as precursor-mRNA signal (`paper.md:20-27`).

For each gene, Velocyto fits a steady-state relationship between spliced abundance `s` and unspliced abundance `u`. Fig. 1b gives the central model:

```text
ds/dt = u - γs
```

Cells/genes above the steady-state diagonal (`u > γs`) are interpreted as increasing/induced; those below (`u < γs`) as decreasing/repressed. The paper describes this as a first-order transcriptional dynamics model (`paper.md:35-42`).

### What the Pipeline Does

1. Count spliced and unspliced molecules for each gene and cell.
2. Normalize and smooth expression/nascent matrices.
3. Estimate a gene-specific slope/degradation-like parameter `γ`.
4. Compute a high-dimensional velocity vector, i.e. the expected change in expression.
5. Extrapolate each cell's near-future expression state.
6. Project velocities onto an existing PCA/t-SNE/other embedding for interpretation.

The cloned R implementation matches this core flow in `velocyto.R/R/momentum_routines.R`: `gene.relative.velocity.estimates` takes `emat` and `nmat` matrices (`:78-120`), fits/stores `gamma` and computes `deltaE` (`:397-418`), and `t.get.projected.delta` implements projected delta from `x'=(y-o)-gamma*x` (`:2398-2412`). Embedding visualization is implemented by `show.velocity.on.embedding.cor` and `show.velocity.on.embedding.eu` (`:1049-1140`, `:1335-1395`).

### Evidence and Results

- **Model demonstration**: Fig. 1 shows unspliced read fractions, the kinetic equation, phase portraits, and PC-space extrapolation.
- **Chromaffin differentiation**: velocity arrows recapitulate progression from sympathoadrenal progenitors through a differentiation bridge toward chromaffin cells; EdU analysis suggests a 2.5-3.8 h extrapolation window for this dataset (`paper.md:43-62`).
- **Developing hippocampus**: velocity fields describe branching neural lineages and support fate decisions among granule, CA, subiculum, neuroblast, OPC, and other populations (`paper.md:64-80`).
- **Human embryonic brain**: spliced/unspliced offsets along pseudotime reveal transcriptional kinetics during glutamatergic neurogenesis (`paper.md:90-97`).

### Reproducibility

The paper's code availability states that Velocyto is available at `http://velocyto.org` with complete R and Python libraries plus notebooks (`paper.md:216-219`). This workspace includes the R repository snapshot `velocyto-team/velocyto.R` at commit `83e6ed92c2d9c9640122dcebf8ebbb5788165a21`; it does **not** include the Python library or the remote notebooks. The README provides tutorial links for chromaffin SMART-seq2, dentate gyrus/loom, and dropEst/pagoda2 workflows (`velocyto.R/README.md:23-35`).

**Code-paper fidelity: medium.** The core estimator and visualization primitives are present and directly map to the paper's central model. Full figure reproduction is incomplete because supplementary notes, notebooks, and Python code are not local in this workspace.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
