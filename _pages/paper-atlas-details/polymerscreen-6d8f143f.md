---
layout: default
permalink: /paper-atlas/polymerscreen-6d8f143f/
title: "PolymerScreen"
nav: false
description: "膜蛋白的构象、复合体和功能受到周围脂质环境影响。传统去污剂虽然提取效率高，却常把这层环境破坏掉。膜活性聚合物（MAP）可以直接从细胞膜中“挖出”含膜蛋白的原生纳米盘，但不同聚合物对不同蛋白和细胞器膜的效果差异很大，不能靠一种固定配方解决。 PolymerScreen 的核心贡献是把“选哪种聚合物”变成一个可量化、可查询的问题：作者测量 11 种聚合物条件下 2,065 个膜蛋白的相对提取效率，并为每个蛋白给出最优条件。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>PolymerScreen</h1>
    <p>A proteome-wide quantitative platform for nanoscale spatially resolved extraction of membrane proteins into native nanodiscs</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PolymerScreen 方法详解

### 它解决什么问题？

膜蛋白的构象、复合体和功能受到周围脂质环境影响。传统去污剂虽然提取效率高，却常把这层环境破坏掉。膜活性聚合物（MAP）可以直接从细胞膜中“挖出”含膜蛋白的原生纳米盘，但不同聚合物对不同蛋白和细胞器膜的效果差异很大，不能靠一种固定配方解决。

PolymerScreen 的核心贡献是把“选哪种聚合物”变成一个可量化、可查询的问题：作者测量 11 种聚合物条件下 2,065 个膜蛋白的相对提取效率，并为每个蛋白给出最优条件。

### 整体流程

```text
聚合物库
  -> 荧光淬灭实验筛选总体溶膜能力
  -> 选择表现较好的 MAP 条件
  -> 提取细胞膜并形成原生纳米盘
  -> 超速离心去除未溶解膜
  -> 蛋白沉淀、还原、烷基化、胰酶消化
  -> LC–MS/MS 与 MaxQuant LFQ
  -> 去污染、膜蛋白与细胞器人工校订
  -> 每个蛋白在不同条件间归一化
  -> 建立可查询数据库
  -> 为单蛋白或复合体选择聚合物并实验验证
```

### 两个关键量化步骤

第一步用连二亚硫酸盐淬灭区分开放纳米盘与封闭小囊泡。淬灭前后荧光分别为 `fl1` 和 `fl2`：

$$
{\rm bulk}\; {\rm solubilization}=100-\left[\frac{\left(2\times&#123;&#123;\rm fl}}2\right)}&#123;&#123;\rm fl}1}\times 100\right].
$$

第二步对每个蛋白单独归一化。若 $L_{p,c}$ 是蛋白 $p$ 在条件 $c$ 下的平均 LFQ 强度，则：

$$
R_{p,c}=100\frac{L_{p,c}}{\max_{c'}L_{p,c'}}.
$$

因此 100% 表示该蛋白在已测试条件中的最佳条件，不代表不同蛋白之间的绝对产量相同。

对于含 $n$ 个蛋白的复合体，作者把各成员的归一化效率取平均，形成 solubilization index。Syp–VAMP2 案例说明最终决策不只看分数：ChloroSMA40 平均分最高，但 ChloroSMA80 形成更大的纳米盘，更适合容纳复合体，所以实验选择后者。

### 主要结果

- 数据库覆盖 2,065 个膜相关蛋白和多个细胞器膜。
- 1,897 个蛋白在所有条件中都可定量，83 个蛋白只在 MAP 条件而非去污剂条件中检测到。
- 不同聚合物对蛋白分子量、跨膜螺旋数和细胞器来源表现出系统性偏好。
- 数据库指导五种细胞器膜蛋白获得约 65–96% 的提取效率。
- 提取后的 TGN46 可进入 NativeNanoBleach 单分子寡聚状态分析；Syp–VAMP2 可在原生纳米盘中共同纯化。

### 代码与局限

Zenodo 中的两个 Python 脚本验证了 LFQ 重复平均、按蛋白最大值归一化和细胞器基因匹配等核心步骤。但代码是交互式脚本，依赖 Excel、人工校订和硬编码路径，没有测试、环境文件或完整命令行流程；公开 Streamlit 前端源码也未在 Zenodo 文件列表中找到，论文链接的 GitHub 仓库无法匿名克隆。此外，当前数据库主要来自 HEK 细胞，换细胞类型、膜脂组成、pH 或新聚合物后需要重新测量。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PolymerScreen summary

This Nature Methods technology paper addresses a central membrane-protein problem: detergents often extract proteins efficiently but disrupt their native lipid context, whereas native-nanodisc-forming polymers vary unpredictably by protein and membrane. The authors build a quantitative platform that screens membrane-active polymers (MAPs), profiles their protein-specific extraction by LFQ proteomics, and exposes normalized results through a searchable database.

The platform first uses a dithionite fluorescence-quenching assay to distinguish open MAP nanodiscs from residual closed vesicles. It then subjects HEK293 membranes to 11 polymer conditions, isolates soluble nanodiscs, and analyzes them by LC–MS/MS and MaxQuant. After filtering and organelle-aware curation, the database contains 2,065 membrane-associated proteins. For each protein, the best LFQ condition is scaled to 100%, yielding a relative condition ranking.

The results show broad organelle coverage, 1,897 MPs quantified across all conditions, and 83 MPs detected under MAP but not detergent conditions. Polymer preferences correlate with molecular weight, transmembrane-domain count, and organelle. Database-guided experiments achieved high extraction for five targets spanning plasma membrane, ER, Golgi, lysosome, and mitochondria; enabled TGN46 oligomer analysis with NativeNanoBleach; and guided purification of a Syp–VAMP2 complex in ChloroSMA80 nanodiscs.

Reproducibility is **3/5**. Proteomics data and supporting datasets are public, and the Zenodo code deposit contains scripts that match the central LFQ averaging, per-protein normalization, and organelle-matching steps. However, the scripts are interactive, rely on Excel workbooks and manual curation, include hard-coded paths, and lack tests or an environment specification. The Streamlit application source was not found in the Zenodo file listing, and the paper-linked GitHub repository was unavailable to anonymous cloning. The database should therefore be interpreted as a strong experimental resource whose exact rankings remain cell-type and condition specific.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
