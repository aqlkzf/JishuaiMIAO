---
layout: default
permalink: /paper-atlas/itec-c1fd207a/
title: "ITEC"
nav: false
description: "ITEC 解决的是胚胎 3D+t 活体成像中的长期全胚胎细胞谱系重建问题。输入是一系列按时间排列的三维核标记显微图像，输出是细胞实例、跨帧连接、分裂关系和可用于命运图谱分析的 lineage graph。核心思想是把 tracking 结果反过来作为 segmentation 的纠错证据：如果图中出现跳帧连接、断裂 track 或一对多/多对一模式，就回到局部图像中补检漏掉的细胞或修正过分割/欠分割。"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>ITEC</h1>
    <p>High-Fidelity Long-term Whole-embryo Lineage and Fate Reconstruction by Iterative Tracking with Error Correction</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.03.12.711203" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ITEC">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/yu-lab-vt/ITEC" target="_blank" rel="noopener noreferrer" aria-label="Open code for ITEC">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ITEC 方法中文解读

### 一句话概览

ITEC 解决的是胚胎 3D+t 活体成像中的长期全胚胎细胞谱系重建问题。输入是一系列按时间排列的三维核标记显微图像，输出是细胞实例、跨帧连接、分裂关系和可用于命运图谱分析的 lineage graph。核心思想是把 tracking 结果反过来作为 segmentation 的纠错证据：如果图中出现跳帧连接、断裂 track 或一对多/多对一模式，就回到局部图像中补检漏掉的细胞或修正过分割/欠分割。

### 1. 生物学问题与建模目标

胚胎发育研究希望知道每个后期组织或器官区域的细胞来自哪里，以及细胞群在 gastrulation、somitogenesis 等过程中如何混合、分离和迁移。人工标注长时间三维视频几乎不可行，因为全胚胎数据可达到 TB 级，且一个错误连接就会破坏后续整条谱系。

ITEC 把这个问题建模为“先检测每一帧的细胞核，再在时间上选择最一致的细胞身份连接”。这个建模对于高时间分辨率、核标记的胚胎图像是合理代理，但它不能直接证明分子因果机制；后续 fate mapping、mixing index 和 weMERFISH 关联更适合作为组织尺度的假设生成和现象描述。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| 原始图像 | `I(t)`, TIFF stacks | 每个时间点一个 3D 体数据 | `doc_method.md`, `doc_code.md` |
| 细胞实例 | `seg_res`, `refine_res`, `movieInfo` | 每帧检测出的核实例和属性 | `doc_code.md` |
| 运动场 | motion flow / `driftInfo` | 补偿组织形变和胚胎运动 | `doc_method.md`, `doc_code.md` |
| tracking 图 | detection/entry/exit/transition arcs | 最小费用循环优化的图结构 | `doc_method.md` |
| 纠错线索 | jump arcs, split/merge arcs | 漏检和分割错误的局部证据 | `figure_analysis.md` |
| 输出谱系 | lineage graph | 细胞身份延续和分裂关系 | `summary.md` |

### 3. 方法主流程

1. 读取 3D+t 图像和参数 CSV。参数包括 cell size、curvature threshold、foreground threshold、`maxIter`、`max_dist`、`useMotionFlow` 和 `division_thres`。
2. 论文描述可选的 deconvolution、rigid registration 和 motion flow。代码可验证的是非刚性 motion-flow 模块；deconvolution 和显式 rigid registration 在公开代码中未找到直接实现。
3. 初始检测阶段估计局部噪声/方差，计算多尺度 Hessian principal curvature，找 seed region，再用 graph-cut/min-cut 逻辑把 seed 扩展为 cell mask。
4. tracking 阶段把每个检测到的细胞转成图节点，生成 entry、exit、transition 和 detection arcs，并用 minimum-cost circulation / CINDA 求全局一致的 tracks。
5. 迭代纠错阶段读取 tracking 图中的异常模式。frame-skipping connection 暗示中间帧可能漏检；一对多或多对一局部模式暗示过分割或欠分割。ITEC 会局部重检、修正 segmentation，然后重新 tracking。
6. 后处理阶段合并 broken tracklets，并用候选 parent/child 的运动几何规则检测细胞分裂。
7. 最终 lineage graph 用于 fate mapping、somite mixing index、midline origin、dispersion index、velocity map 和 weMERFISH 区域级整合。

### 4. 数学目标与直觉

论文的 Eq. 1-4 把图像恢复写成 deconvolution 问题：观测图像是未知真实信号经过 PSF 模糊和噪声后的结果。直觉是先增强核信号再分割；但公开代码中没有找到 Landweber/deconvolution 实现。

Eq. 6-13 是非刚性 motion flow。它使用局部亮度一致性和 patch 邻接平滑约束，估计相邻时间点之间的三维位移场。这个位移场对应组织尺度运动，用于降低快速形变造成的错误连接。

Eq. 14-15 对应检测：多尺度 principal curvature 把核边界和间隙变成图像证据，min-cut/graph-cut 决定 seed 周围哪些 voxel 属于同一个细胞。生物学含义是把连续显微图像离散成可追踪的核对象。

Eq. 16-21 把 tracking 写成 MAP / binary-cost flow 问题。每个 detection 是否使用、track 是否进入/退出、两个 detection 是否相连，都对应二值变量和费用。minimum-cost circulation 选择总费用最低且满足流约束的细胞身份连接。

Eq. 25-29 对应 division detection。直觉是分裂后两个 daughter nuclei 的相对位置和运动应符合局部运动模型。代码中可验证的是 motion chi-square 规则；论文中更广义的 size/component 规则在公开代码里只部分对应。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| 主入口 | `ITEC/src/demo.m:3-14` | 读取参数，先 segmentation 再 tracking | 部分匹配 |
| 初始检测 | `InstanceSegmentation.m`, `varEst.m`, `PrcplCrvtr_scaleInvariant_3D.m`, `getSeedMap.m` | 方差校正、curvature map、seed 选择 | 高匹配 |
| graph-cut 区域生长 | `graphCut_negHandle_mat.m`, `regionGrow.m` | 用图割扩展细胞区域 | 高匹配 |
| motion flow | `MotionFlowEstimation_stable.m`, `registration_main.m` | 多尺度 patch-wise least-squares + 平滑 | 高匹配 |
| MCC tracking | `mcfTracking_cell.m`, `trackGraphBuilder_cell.m`, `mccTracker.m`, `cinda_funcs.c` | CINDA 最小费用循环 | 高匹配 |
| 漏检修复 | `missing_cell_module/` | jump arcs 定位后局部补检细胞 | 高匹配 |
| split/merge 修复 | `split_merge_module/` | 添加 split/merge 图选择并刷新区域 | 部分匹配 |
| division | `division_detection_module/` | 后处理候选分裂，主要用运动规则 | 部分匹配 |
| benchmark/生物分析 | 未找到 | Fig. 2 和 Fig. 5-7 脚本未在公开代码中发现 | 未找到 |

### 6. 结果如何解读

Fig. 2 在 FISH1、FISH2、MOUSE、DRO 四个跨物种数据集上比较 TGMM、Linajea、Ultrack 和 ITEC。ITEC 在 edge error、error-free tracks 和 average error-free length 上都领先，说明它不仅局部连接更准，也更能维持长谱系连续性。

Fig. 3 证明迭代纠错是核心贡献之一。第一轮纠错已经明显降低错误率，约三轮后趋于稳定；代码默认 `maxIter=5`，用于给困难场景留余量。

Fig. 4 展示 1001 time points、1.5 TB zebrafish 数据的长时程重建。论文报告在人工精选的 600 帧子集上达到 99.7% linkage accuracy，但这不是对全部 18.5M 累积细胞的完全人工审计。

Fig. 5-7 是生物应用：fate mapping、somite boundary mixing、midline origin、dispersion、velocity-gene correlation 和 GO enrichment。这些结果支持 ITEC lineage 对发育过程解释有用，但相关分析脚本没有在公开 repo 中找到。

### 7. 局限性与未验证部分

- 公开代码未找到 deconvolution/Landweber、显式 rigid registration、multi-view stitching 的直接实现。
- Fig. 2 benchmark、Fig. 5-7 下游生物分析、weMERFISH global mapping、GO enrichment 脚本未找到。
- 代码中的 active division test 主要是 frame relation + motion rule；size ratio 函数存在但在 `rule_based_test.m` 中被注释掉。
- 方法最适合核标记、高时间分辨率、胚胎类数据；对形态高度多样、低帧率或内部表达不均的细胞需要重新验证。
- weMERFISH 整合是区域级近似匹配，不应解读为同一单细胞的真实分子轨迹。

### 8. 快速阅读路线

1. `summary.md`：先看研究动机、主要结果和复现评分。
2. `doc_method.md`：理解完整数学目标和算法流程。
3. `doc_code.md`：检查论文步骤和公开 MATLAB 代码的逐项对应关系。
4. `figure_analysis.md`：按图理解 benchmark、纠错机制和生物应用。
5. `claude_notes.md`：需要证据表、claim ledger、assumption ledger 或开放问题时再读。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ITEC Summary

### Motivation and Novelty

ITEC addresses whole-embryo lineage reconstruction from long 3D+t live-imaging microscopy. The biological target is high-fidelity tracking of nuclear-labeled cells over gastrulation and organogenesis so that later tissue fates, boundaries, and movement programs can be traced back to earlier progenitors.

The paper's key novelty is iterative tracking with error correction: tracking is not treated as a one-way consumer of segmentation. Instead, the initial track graph reveals missing detections, over-segmentation, and under-segmentation patterns, which are then used to redetect cells or repair segmentation before rerunning tracking. This feedback loop is coupled to a minimum-cost circulation tracker, tracklet association, division detection, and optional multiview stitching.

Compared peer methods:

| Method | Journal / Venue | Year | Role in Paper |
|---|---:|---:|---|
| TGMM | Nature Methods | 2014 | Statistical embryo lineage reconstruction baseline. |
| Linajea | Nature Biotechnology | 2023 | Deep-learning/sparse-annotation tracking baseline. |
| Ultrack | Nature Methods | 2025 | Joint segmentation/tracking baseline using contour maps and ILP. |

### Method Overview

ITEC takes raw 3D+t embryonic image stacks as input. The paper describes optional preprocessing by deconvolution, rigid registration, and non-rigid motion-flow estimation. Initial detection estimates local variance, computes multi-scale principal curvature maps, selects seed regions, and grows them into cell instances using min-cut / graph-cut logic.

Detected cells are converted into a tracking graph. Candidate entry, exit, detection, and transition arcs are assigned costs, and the MAP tracking objective is solved as minimum-cost circulation using CINDA. ITEC then inspects the resulting graph for error patterns: frame-skipping arcs suggest missed cells, and one-to-many or many-to-one local patterns suggest split/merge segmentation errors. These repairs are iterated, followed by tracklet association and division post-processing.

The final lineage graph supports downstream biological analyses: fate mapping, somite and organ mixing indices, midline-origin analysis, velocity and dispersion maps, and approximate region-level integration with weMERFISH spatial transcriptomics.

### Evaluation

The paper evaluates ITEC on four cross-species datasets: FISH1 and FISH2 zebrafish embryos, MOUSE embryo, and DRO Drosophila embryo. Ground truth combines public and manual annotations, totaling 44,555 ground-truth edge linkages. In Fig. 2, ITEC has the lowest false-negative, false-positive, and total edge-linkage error across all four datasets, and also improves lineage-level metrics: proportion of error-free tracks and average error-free length.

Fig. 3 shows that iterative correction is a major contributor. One round of error correction reduces error rates by 45.0%, 50.0%, 56.4%, and 47.7% on FISH1, FISH2, MOUSE, and DRO. After iterative correction, reported final error rates are 1.54%, 0.69%, 2.64%, and 2.02%, with reductions of 51.6%, 57.9%, 59.0%, and 71.9% relative to pre-iteration error.

Fig. 4 evaluates long-term scale on a 1001-time-point zebrafish dataset spanning 16.7 hours and 1.5 TB. The authors report manual curation over the first 600 frames for 31 selected starting cells, covering over 30,000 linkage edges and a similar number of cell instances; 91 errors were found, giving 99.7% linkage accuracy in that curated subset and 48.4% error-free lineages.

Figs. 5-7 demonstrate biological use cases rather than independent tracker benchmarks. ITEC lineages are used for organ and somite fate mapping, mixing-index analysis of boundary formation, midline ancestor and dispersion analysis, and approximate region-level integration with weMERFISH to relate movement features to gene-expression programs.

### Code Reproducibility

**Rating: 3/5.**

The released GitHub repository is a substantial MATLAB implementation of the core ITEC pipeline. Verified code covers CSV/GUI setup, raw TIFF input, curvature-based initial segmentation, graph-cut region growth, non-rigid motion-flow estimation, minimum-cost circulation tracking through CINDA, iterative missing-cell redetection, split/merge correction, broken-track association, division post-processing, and user-facing exports.

The rating is not higher because several paper components are not present in the searched public code: deconvolution/Landweber preprocessing, an explicit rigid-registration module, multiview stitching, benchmark scripts for TGMM/Linajea/Ultrack comparisons, distributed orchestration for the 1.5 TB run, and downstream biological analysis scripts for fate maps, mixing indices, velocity/gene correlations, and GO enrichment. The active division code also appears narrower than the paper's prose: the motion rule is active, while the size-ratio helper exists but is commented out in the public rule test.

Overall, the repository is suitable for understanding and running the core ITEC tracking workflow, but it is not a complete reproduction package for every figure and biological analysis.

### Key Limitations

- ITEC is best matched to high-temporal-resolution nuclear imaging of embryos; the paper cautions that diverse morphologies or uneven internal expression can reduce performance.
- Several mathematical symbols in the OCR Markdown are corrupted, especially in equations around deconvolution, cost conversion, and division tests; the analysis therefore uses equation roles rather than over-precise symbol claims where needed.
- Benchmark and downstream analysis reproducibility depends on data, scripts, and curation not included in the public repository.
- weMERFISH integration is region-level and approximate because live-imaging and spatial-transcriptomics embryos are not the same individual cells.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
