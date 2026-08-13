---
layout: default
permalink: /paper-atlas/macaca30tissueaging-220106dd/
title: "Macaca30TissueAging"
nav: false
wide: true
description: "人体衰老并不是所有器官同步发生，但很难从同一个人获得几十种组织，因此人类全身组织衰老规律一直缺少系统证据。以往非人灵长类研究也大多局限于单个组织或单一组学。本文利用 17 只 3–27 岁的雌性恒河猴，采集 30 种实体组织，同时测量转录组、蛋白质组和代谢组，目标是回答：哪些衰老信号跨组织共享，哪些组织衰老更快，以及这种差异是否与翻译后调控有关。 输入是四个年龄阶段的横断面样本：幼年 5 只、青年 5 只、中年 3 只、老年 4 只。"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Macaca30TissueAging</h1>
    <p>A multi-omics molecular landscape of 30 tissues in aging female rhesus macaques</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02912-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Macaca30TissueAging">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/GonghuaLi/Macaca_30tissue_aging" target="_blank" rel="noopener noreferrer" aria-label="Open code for Macaca30TissueAging">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 30 种组织的雌性恒河猴衰老多组学图谱：方法解析

### 这项研究要解决什么问题？

人体衰老并不是所有器官同步发生，但很难从同一个人获得几十种组织，因此人类全身组织衰老规律一直缺少系统证据。以往非人灵长类研究也大多局限于单个组织或单一组学。本文利用 17 只 3–27 岁的雌性恒河猴，采集 30 种实体组织，同时测量转录组、蛋白质组和代谢组，目标是回答：哪些衰老信号跨组织共享，哪些组织衰老更快，以及这种差异是否与翻译后调控有关。

### 数据与输出

输入是四个年龄阶段的横断面样本：幼年 5 只、青年 5 只、中年 3 只、老年 4 只。每个组织分别形成 RNA、蛋白和代谢物丰度矩阵。主要输出包括：

- 每种组织中每个分子的年龄效应 $\beta_t$；
- 控制组织差异后的全身共享年龄效应 $\beta_p$；
- 组织特异的衰老分子；
- 八类分子衰老轨迹和 Type I / Type II / Undefined 组织标签；
- 翻译效率相对蛋白降解的 TED，以及 TED 随年龄变化的 cTED。

这里的“轨迹”来自不同年龄动物的横断面趋势，并不是同一只动物的纵向跟踪。

### 核心统计模型

单组织模型为：

$$
y_{it}=\beta_{0t}+\beta_t\,\mathrm{age}_i+\varepsilon_{it}.
$$

跨组织共享模型为：

$$
y_i=\beta_0+\beta_p\,\mathrm{age}_i+\delta_{\mathrm{tissue}(i)}+\varepsilon_i.
$$

公开代码用 limma 拟合第二个模型：构建设计矩阵 `~ age + tissue`，运行 `lmFit` 和 `eBayes`，再以 Benjamini–Hochberg 方法校正多重检验。常用判定还要求 $|\beta|>0.008$。

### 完整计算流程

```text
30 种组织 × 3 种组学
        │
        ├─ 各组织 abundance ~ age → 组织年龄效应 β_t
        ├─ 合并后 abundance ~ age + tissue → 共享效应 β_p
        ├─ 跨组织稀有且非共享的显著变化 → 组织特异标志物
        ├─ 与小鼠、人类的基因和通路衰老模式比较
        │
        ├─ 广泛表达的蛋白+代谢物 → 模糊 C 均值 → 8 类全身轨迹
        ├─ 每种组织计算对应轨迹
        ├─ 层次聚类 + 共识 k-means + MAA
        ├─ 再加入转录组轨迹并要求多方法一致
        └─ Type I / Type II / Undefined
        │
        └─ 匹配蛋白与 mRNA → TED=P/M → TED ~ age 的斜率 cTED
```

### 为什么要用三种组织分类方法？

单一聚类算法可能对距离、初始值或特征尺度敏感。作者同时使用完整轨迹的层次聚类、$k=2$ 到 6 的共识 k-means，以及分子改变幅度 MAA。MAA 比较老年与幼年端点的平均标准化差异，并保留正负方向。之后又分别在“蛋白+代谢物”和“三组学”框架中分类，只有在多个方法和两个框架中一致的组织才得到最终标签。这提高了标签的保守性，但也使七种组织保持未定义。

最终 Type I 有 12 种组织，Type II 有 11 种。Type I 在图像和分子层面表现出更强的衰老：代表组织中的 p16/p21 增加更明显，组织结构退化更多，炎症相关蛋白上调和翻译相关蛋白下调也更广泛。

### TED / cTED 的含义

蛋白动力学写为：

$$
\frac{dP}{dt}=\alpha M-\gamma P.
$$

稳态下 $dP/dt=0$，因此：

$$
\mathrm{TED}=\frac{P}{M}=\frac{\alpha}{\gamma}.
$$

$\alpha$ 是翻译效率，$\gamma$ 是蛋白降解率。TED 只能观察两者的比值，不能单独证明是翻译下降还是降解增强。作者对每个组织、每个基因拟合 `TED ~ age`，把年龄斜率定义为 cTED。多数 Type I 组织的平均 cTED 为负，而多数 Type II 接近零；平均 cTED 与平均蛋白年龄效应相关（$r=0.80$），说明翻译/降解平衡变化与更强的蛋白质组衰老同步出现。

### 主要结果

- 跨组织共同特征是炎症和免疫活动增强，以及翻译、线粒体等功能下降。
- 恒河猴与人类的衰老通路一致性总体高于小鼠与人类，尤其是下调通路。
- 组织衰老明显不同步，Type I 组织对全身共同衰老信号贡献更大。
- cTED 与蛋白年龄效应的关系为 Type I 的翻译相关衰退提供了机制线索，但证据仍是关联性的。

### 如何评价可重复性？

公开仓库中的 R Markdown 与 R 函数能够对应论文的核心回归、轨迹聚类和 TED 分析，代码—论文一致性为中等。问题是仓库依赖未随代码打包的 `./data` 处理对象，也没有锁定软件环境、自动化工作流或测试，因此不能直接一键复现。研究本身还受样本量小、仅包含雌性、年龄组不均衡、横断面设计和 bulk 组织细胞组成变化等限制。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## A multi-omics molecular landscape of 30 tissues in aging female rhesus macaques

### Problem and contribution

Human tissue aging is difficult to study systematically because matched samples from many organs across a wide age range are rarely available. Earlier nonhuman-primate studies generally focused on one tissue or one omics layer. This Nature Methods study (2025) builds a cross-tissue resource from 17 female rhesus macaques aged 3–27 years, profiling transcriptomes, proteomes and metabolomes across 30 solid tissues. It combines an atlas contribution with a statistical framework for shared, tissue-specific and trajectory-level aging analysis.

### Approach

The authors estimate age effects within each tissue using molecular abundance ~ age and estimate common changes with a pooled molecular abundance ~ age + tissue model. They identify tissue-specific aging markers, compare macaque transcriptomic aging with mouse and human data, and cluster standardized molecular trajectories across four age stages. Hierarchical clustering, consensus k-means and molecular alteration amplitude are reconciled across protein/metabolite and three-omics analyses to define Type I, Type II and undefined tissues.

To connect tissue type with post-transcriptional regulation, the paper uses a steady-state protein model. The protein-to-mRNA ratio estimates translation efficiency relative to protein degradation (TED), and the age slope of TED is called cTED. This is an interpretable ratio but does not separately measure translation and degradation.

### Main findings

- Across tissues, aging is associated with increased inflammatory/immune programs and decreased translation- and mitochondrial-related programs. The pooled analyses report 1,265 up- and 789 downregulated transcripts, 238 up- and 219 downregulated proteins, and 11 up- and 56 downregulated metabolites under the stated thresholds.
- Aging-related pathway patterns are more concordant between macaques and humans than between mice and humans, particularly for downregulated processes.
- Molecular trajectories divide tissues into distinct aging behaviors. The stringent agreement rule yields 12 Type I tissues, 11 Type II tissues and seven undefined tissues.
- Type I tissues show stronger p16/p21 accumulation, more structural degeneration in examined examples, more extensive inflammatory increases and translation-related protein decreases.
- Most Type I tissues have declining TED with age, and average cTED correlates with the mean protein age effect across tissues ($r=0.80$, $P=1.2\times10^{-7}$), associating post-transcriptional imbalance with stronger tissue aging.

### Evidence and limitations

The atlas is broad in tissue and molecular coverage, and the main figures provide coherent visual support for tissue identity, trajectory separation and the cTED–proteomic-aging relationship. However, the cohort is small and cross-sectional, contains only females, and has uneven age-group sizes. Bulk tissue signals can reflect changing cell composition. The Type I/II labels depend on trajectory preprocessing and agreement rules, and TED conflates translation with degradation; causal language should therefore remain cautious.

### Reproducibility

Reproducibility rating: **3/5**. The public GitHub repository contains a large R Markdown analysis and reusable R functions that directly match the pooled/tissue-specific regression, trajectory clustering and TED/cTED analyses. Code-paper fidelity is medium because core statistical logic is visible, but the repository is not a turnkey package: processed `./data` objects, exact environment versions, workflow automation and tests are absent. Data are deposited through the paper’s linked repositories, but this workspace did not convert the supplementary PDFs/data into local Markdown. The source snapshot is pinned to commit `12aa0341b6f627e6fbd0affad153bba62b5d7816`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
