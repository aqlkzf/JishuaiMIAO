---
layout: default
permalink: /paper-atlas/predictivevirtualembryos-1468c9c5/
title: "PredictiveVirtualEmbryos"
nav: false
wide: true
description: "本工作区是 paper-only。可访问的 paper.md 是 Nature Methods 的订阅预览， 只有标题、摘要式 standfirst、两条图注、参考文献和出版信息；正文、Methods、 补充材料和代码均未提供。因此下面把论文明确陈述、图像可见内容和解释性推断 分开，并对无法核验的细节标为 Not found。"
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
      <span>Nature Methods · 2026</span>
    </div>
    <h1>PredictiveVirtualEmbryos</h1>
    <p>Towards predictive virtual embryos with genomics and AI</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法中文解读：Towards predictive virtual embryos with genomics and AI

### 证据边界

可访问的 `paper.md` 是 Nature Methods 的订阅预览，
只有标题、摘要式 standfirst、两条图注、参考文献和出版信息；正文、Methods、
补充材料和代码均未提供。因此下面把论文明确陈述、图像可见内容和解释性推断
分开，并对无法核验的细节标为 `Not found`。

### 论文要解决什么问题

文章提出，若把单细胞数据、空间数据和人工智能结合起来，就有望构建能够跨尺度
描述哺乳动物胚胎发生的 predictive virtual embryo（预测性虚拟胚胎）系统。其潜在
用途是帮助理解发育过程，并研究先天性疾病。这里的证据是 standfirst 的概括，
不是一个已经给出全部实现细节的软件规格。

### 为什么现有方法不足

预览正文没有提供作者对既有方法的逐项局限、基线或定量比较。Fig. 1 的图像把活体
成像、单细胞测序、谱系追踪、测序/成像三维测量以及多种胚胎样模型并列展示，提示
单一测量或单一模型难以覆盖所有尺度；但这是图示层面的解释，不能替代正文中的
正式论证。参考文献涉及 Cell、Nature、Science、Nature Genetics、Nature Methods
等期刊的相关工作，不过预览没有给出各文献在论证中的具体角色。

### 提出的方向与新意

标题和 standfirst 所支持的新意是一个整合方向：以 genomics、空间测量和 AI 为核心，
把异质的胚胎证据组织为可预测的虚拟胚胎。Fig. 1 强调技术和胚胎模型是基础，Fig. 2
展示三类走向虚拟胚胎的计算方法。三类方法的正式名称、接口和算法在预览中均为
`Not found`，所以不能声称作者已经发布了某个具体模型。

### 计算流程（概念层面）

```text
单细胞/空间/成像/谱系数据 + 胚胎或胚胎样模型
                    |
                    v
        AI 与其他计算表示（Fig. 2）
                    |
                    v
      跨尺度、含时间的虚拟胚胎表示
                    |
                    v
          对胚胎发育的预测与假设
```

输入格式、细胞状态变量、时间索引、空间坐标、输出结构和不确定性表达均为
`Not found`。同样没有可核验的网络结构、损失函数、优化器、训练轮数、预处理或
推理步骤；`scratch/evidence_index.json` 也没有公式或代码锚点。

### 评估与可复现性

预览没有公开数据集、数据划分、基线、指标、数值结果或验证实验。两幅图是路线图和
概念示意，不构成准确率或优越性证据。获取清单及 `github_links.json` 均未找到论文
专属代码仓库，也没有补充 Markdown；需要完整
正文、Methods、补充材料及作者发布的数据/代码后，才能完成算法级复现和结果核验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Towards predictive virtual embryos with genomics and AI

### Problem

The Nature Methods preview frames predictive virtual embryos as a way to
integrate single-cell and spatial data with artificial intelligence for
multiscale modeling of mammalian embryogenesis. The intended scientific uses
are understanding development and investigating congenital disease.

### Existing-method limitations

The accessible source does not contain the article's discussion of prior-method
limitations. Figure 1 visually surveys existing measurement technologies and
embryonic/embryo-like models, implying that no single source captures all
relevant scales, but the preview does not state a formal gap, baseline, or
quantitative comparison. The references span Cell (2012, 2018, 2022, 2024,
2025), Science (2020), Nature (2023/2024), Nature Genetics (2022/2023), Nature
Cell Biology (2025), Nature Methods (2024), and Cell Stem Cell (2025); their
titles and roles are not exposed in the preview, so they are not assigned
specific limitations here.

### Proposed contribution

The title and standfirst propose a predictive virtual-embryo direction that
combines genomics, spatial measurements, and AI. Fig. 1 presents technologies
and embryonic models as foundations; Fig. 2 presents three broad computational
approach types. This is a conceptual roadmap in the available evidence, not a
fully documented software method.

### High-level method view

```text
single-cell + spatial/imaging + lineage evidence
                 + embryo models
                              |
                              v
      AI / computational representations (Fig. 2)
                              |
                              v
  multiscale, spatiotemporal virtual-embryo predictions
```

The exact representation, model architecture, training objective, temporal
state, and prediction target are **Not found** in `paper.md`.

### Evaluation

No datasets, train/test splits, baselines, metrics, numerical results, or
validation experiments are present in the subscription preview. Evaluation is
therefore **Not found**, and the figures should be read as conceptual diagrams
rather than result plots supporting accuracy claims.

### Reproducibility and limitations

Reproducibility is currently unrated/not reproducible from this workspace: the
article body and Methods are inaccessible, no supplementary markdown was
acquired, and `github_links.json` plus the acquisition manifest report no
paper-specific code repository. Reproduction requires the full article and any
associated data/code. The primary residual limitation is source access, not a
demonstrated failure of the proposed virtual-embryo concept.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
