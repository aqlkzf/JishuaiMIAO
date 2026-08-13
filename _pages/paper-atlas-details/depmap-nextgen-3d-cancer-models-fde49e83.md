---
layout: default
permalink: /paper-atlas/depmap-nextgen-3d-cancer-models-fde49e83/
title: "DepMap_NextGen_3D_Cancer_Models"
nav: false
wide: true
description: "传统 DepMap 细胞系对部分癌症亚型覆盖不足，而且二维单层、含血清培养会改变基因依赖性。本文把患者来源的三维类器官和中枢神经系统肿瘤球体加入 DepMap，并用多组学与 CRISPR 筛选寻找更接近肿瘤状态的脆弱性。 研究包括 314 个 NextGen 模型、291 个 WGS、309 个 RNA-seq 和 147 个全基因组 CRISPR 筛选。"
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
      <span>Perturbation Resources</span>
      <span>Nature · 2026</span>
    </div>
    <h1>DepMap_NextGen_3D_Cancer_Models</h1>
    <p>A dependency map enhanced with next-generation 3D cancer models</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/broadinstitute/DepMap-NextGen-Public" target="_blank" rel="noopener noreferrer" aria-label="Open code for DepMap_NextGen_3D_Cancer_Models">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法中文解读

### 研究问题

传统 DepMap 细胞系对部分癌症亚型覆盖不足，而且二维单层、含血清培养会改变基因依赖性。本文把患者来源的三维类器官和中枢神经系统肿瘤球体加入 DepMap，并用多组学与 CRISPR 筛选寻找更接近肿瘤状态的脆弱性。

### 数据与总流程

研究包括 314 个 NextGen 模型、291 个 WGS、309 个 RNA-seq 和 147 个全基因组 CRISPR 筛选。计算流程是：

```text
WGS/RNA-seq/CRISPR + 模型元数据
        -> Chronos 整合与质控
        -> 依赖谱分类
        -> 表达成瘾、旁系同源依赖、突变关联
        -> Celligner 状态/谱系比较
        -> PDAC-classical/MUC 与 WNT 依赖关联
        -> 2D/3D 依赖尾部富集
        -> minipool 回归分离培养形态和培养基效应
```

### 关键计算

依赖基因被分为 non-dependency、weakly selective、strongly selective、high variance 和 pan-dependency 五类。代码用跨模型排名和 KDE 阈值识别 common essential，用偏度乘峰度与依赖概率识别 strongly selective，用未表达基因的方差 99% 分位数作为 high-variance 校准。之后分别在 NextGen/类器官与谱系匹配的传统二维模型中做表达、旁系同源和突变关联分析。

对于细胞状态，Celligner 从模型到肿瘤样本的距离矩阵中取近邻，再用前 25 个肿瘤近邻的多数谱系投票。NextGen 的谱系匹配率为 69%，高于传统细胞系的 35%。GBM 中，保留胶质转录状态的模型显示更强 CDK6 依赖；CDKN2A 拷贝数缺失进一步增强该依赖。

PDAC-classical/MUC 程序在胃肠道肿瘤和类器官中保留，而在传统细胞系中被压低。程序分数与 3,521 个强依赖基因的依赖分数相关，MESD、WLS、TCF7L2、FZD5 和 LGR4 等 WNT 成分位于关联前列。

minipool 分析使用如下模型：

$$Y_{g,k}=\beta _0+\beta _d I_d+\beta _s I_s+\beta _{ds}I_dI_s+\sum _{m\in M}\beta _m I_m$$

其中 `I_d` 表示 Matrigel dome 与塑料单层，`I_s` 表示 OPAC 无血清培养基与 RPMI-FBS，模型指标控制同一细胞模型的重复筛选。结果显示整合素/肌动蛋白依赖更受培养形态影响，脂质代谢依赖更受培养基影响。

### 结果与复现边界

论文报告了 SCD-KRAS、CDK6-CDKN2A 和 WNT-MUC 等可验证脆弱性。GitHub 仓库只包含下游分析；运行需要从 DepMap Portal 下载 `NextGen Model Manuscript 2026` 数据集。原始数据、上游处理和补充 XLSX 未在本地 workspace 中，因此本文档不把未运行的数值结果标记为代码复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

Traditional DepMap cell lines underrepresent cancer subtypes and can distort perturbation responses through monolayer, serum-containing culture. This study extends DepMap with patient-derived 3D organoids and CNS spheroids.

### Contribution

The authors profile 314 NextGen models with WGS, RNA-seq and 147 genome-scale CRISPR screens, integrate them with traditional models, and identify vulnerabilities tied to molecular state, genotype and culture environment. NextGen models improve tumour-lineage fidelity (69% versus 35% for traditional lines), preserve glial and PDAC-classical/MUC programs, and expose biomarker-linked dependencies including CDK6 in glial GBM, WNT components in MUC-high organoids and SCD in KRAS-amplified oesophagus-stomach organoids (`paper.md:34-68,95-136,162-170`).

### Evaluation and Findings

Comparisons use Celligner nearest-neighbor lineage agreement, dependency correlations, Mann-Whitney/t-test contrasts, CN/mutation associations, gene-set enrichment, drug/sgRNA validation and a focused 18-screen minipool experiment. Global 3D-versus-2D analysis highlights adhesion-cytoskeleton, cell-cycle, lipid, mTORC1 and oxidative-phosphorylation differences; minipool regression separates growth-format effects on integrins/actin regulators from medium effects on lipid metabolism (`paper.md:177-215`).

### Reproducibility

The public repository at commit `5c6f1e0ab23b132ce1a5c31ef8344cdb80e5afbb` contains downstream Python/R analyses and figure scripts. Reproduction requires the `NextGen Model Manuscript 2026` DepMap portal data and locked environments (`DepMap_NextGen_Public/README.md:20-78`). The raw portal package, supplementary tables and upstream processing are not in this workspace, so numerical reruns were not performed.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
