---
layout: default
permalink: /paper-atlas/mucosalvax-865b23d6/
title: "MucosalVax"
nav: false
description: "MucosalVax 不是用一个抗原去识别所有病原体，而是用黏膜佐剂和抗原记忆共同训练肺组织：抗原特异 T 细胞维持并协调 AM、上皮和局部免疫结构，使再次遭遇异质威胁时更快控制病原体、减少组织损伤；公开代码精确覆盖其中的空间转录组证据链，但尚未覆盖整篇论文。"
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
      <span>Science · 2026</span>
    </div>
    <h1>MucosalVax</h1>
    <p>Mucosal vaccination in mice provides protection from diverse respiratory threats</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1126/science.aea1260" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 让肺提前进入“组织级戒备”：MucosalVax 方法与证据链解读

论文：*Mucosal vaccination in mice provides protection from diverse respiratory threats*（Science, 2026；DOI: `10.1126/science.aea1260`）

### 1. 论文要解决的核心矛盾

传统疫苗通常针对一个明确病原体或抗原，特异性强，但面对未知新病毒、变异株或细菌威胁时覆盖有限。单纯刺激先天免疫可以较快产生广谱反应，却往往不够持久。

这项研究试图把两者接起来：通过鼻内接种，把强烈但局部的先天刺激与抗原特异性 T 细胞记忆同时建立在肺中，使组织在数周到数月后仍保留一种“训练过、但不过度炎症化”的准备状态。

作者的核心主张不是 OVA 能识别 SARS-CoV-2 或细菌。OVA 只是用于建立可追踪的抗原特异 T 细胞；真正的异源保护来自这些 T 细胞、肺泡巨噬细胞（AM）、上皮细胞和空间免疫结构形成的协同网络。

### 2. 疫苗配方与实验设计

疫苗经鼻内给药，主要包含：

- `GLA`：TLR4 激动剂；
- `3M-052-LS`：脂质化 TLR7/8 激动剂；
- 脂质体递送体系；
- OVA，或在流感实验中使用 NP 抗原。

小鼠通常在第 0、7、14、21 天接受四次免疫，随后在第 21 天、第 42 天或约 3 个月接受挑战。挑战范围包括 SARS-CoV-2、其他冠状病毒、PR8 流感、*Staphylococcus aureus*、*Acinetobacter baumannii*、*Streptococcus pneumoniae*，以及 HDM 诱导的过敏性哮喘。

保护效果不靠一个单一指标判断，而是组合：

$$
\text{Protection}=f(\text{体重},\text{病毒量/CFU},\text{肺组织损伤},
\text{免疫细胞状态},\text{炎症因子}).
$$

体重曲线反映整体疾病程度，病毒滴度或 CFU 是更直接的病原负荷，组织学显示肺泡壁、上皮和炎症浸润是否改善。

### 3. 图 1：异源保护是否真实、是否持久

图 1 从不同病原体和时间尺度回答“保护是否存在”。接种后小鼠在 SARS-CoV-2 挑战中体重下降更少、病毒负荷和肺损伤更低；在多种细菌挑战中肺 CFU 也显著降低。部分效果可维持约 3 个月。

这一结果的重要含义是抗原不必来自随后挑战的病原体：OVA 免疫仍能改善 SARS-CoV-2 或细菌感染。但这不等于完全抗原无关。补充实验显示，仅用佐剂可提供早期部分保护，较晚时间点的持久保护需要加入抗原。用已有流感 NP 记忆的动物也能建立异源保护，提示平台可利用既往抗原记忆。

因此更准确的描述是：**抗原特异记忆负责维持和组织广谱效应，但最终被控制的病原体可以与该抗原不同。**

### 4. 图 2：持久性来自哪些细胞状态

接种早期，多类先天细胞提高 CD86 并进入 BAL；大部分反应一周内回落，但 AM 的 CD86、MHC 和抗原呈递状态能维持更久。与此同时，肺中形成 OVA 特异性的 CD4、CD8 和记忆驻留 T 细胞（TRM）。

TRM 用血管内 CD45 排除循环细胞，并结合 CD44、CD69、CD103 等标志定义。它们留在肺组织中，能在下一次威胁出现时快速响应。

作者还对 119,876 个肺细胞做 scRNA-seq，对 96,834 个细胞做 scATAC-seq。结果显示：

- AM、部分上皮和树突状细胞的抗原呈递基因长期提高；
- AM 中 `H2-Aa`、`Ccl5` 等区域保持更开放；
- AP-1、STAT、IRF、NF-κB 等 motif 的可及性改变持续存在。

scRNA 表达改变说明“现在正在表达什么”，scATAC 染色质开放说明“哪些调控程序更容易再次被启动”。二者共同支持长期训练状态，但并不能单独证明每个开放峰都直接导致保护。

### 5. 图 3：T 细胞是否只是伴随现象

作者同时清除 CD4 和 CD8 T 细胞后，疫苗对 SARS-CoV-2 体重下降和 *S. aureus* CFU 的保护消失。单独清除 CD4 或 CD8 不足以完全消除保护，说明两群 T 细胞具有部分冗余。

更关键的是，T 细胞清除不仅移除了适应性效应，还降低了 AM 和 DC 的 CD86/MHC 状态，并抹去空间转录组中的抗原呈递、吞噬和抗病毒程序。这建立了一条因果链：

$$
\text{抗原特异 T 细胞}
\longrightarrow \text{先天细胞持续编程}
\longrightarrow \text{异源保护}.
$$

论文还探查 RANKL 等 T—先天细胞信号，但空间配体—受体推断首先是候选相互作用，不等于逐条完成了受体阻断验证。

### 6. 空间转录组是怎样分析的

论文对未免疫、已免疫、以及免疫同时阻断 CD4/CD8 的肺组织做单核空间转录组，共得到 53,645 个空间定位细胞核。本次重分析纠正了旧工作区的一个关键错误：论文确实公开了这部分代码，位于 Zenodo record `17651970`，现已下载到 `zenodo_code/`。

代码流程为：

1. 合并四个空间样本，附加坐标；
2. 用 UMI、基因数、线粒体比例、doublet 和复杂度阈值做 QC；
3. Harmony 按小鼠校正批次，建立近邻图、UMAP 和多个分辨率的 cluster；
4. 依据 marker 和人工审核表给细胞类型命名；
5. 在细胞类型内做 Wilcoxon 差异分析；
6. 对 blood transcription modules（BTM）和 Reactome 做富集；
7. 用 Squidpy 计算空间邻域、共现和距离；
8. 用 SOAPy 估计条件特异的配体—受体通信。

代码中的核心 QC 条件包括：

$$
200\le \mathrm{UMI}\le 5000,
\quad n_{gene}\ge 200,
\quad \%mito<10,
$$

并要求 `scDblFinder.class == singlet` 和 `log10GenesPerUMI >= 0.85`。

差异分析常使用调整后 $P<0.05$，再加表达比例和 fold change 过滤。BTM 富集以命中比例相对背景的富集倍数概括：

$$
E=\log_2\left(\frac{k/m_1}{m_2/n}\right),
$$

其中 $k$ 是查询基因中的通路命中数，$m_1$ 是查询集合大小，$m_2/n$ 是背景命中率。

### 7. 空间通信结果应怎样理解

`5.0.squidpy-linana-analysis.ipynb` 通常用半径 75 建立空间邻接图，比较不同细胞类型是否更常相邻。`5.3 SOAPy-cc.ipynb` 分别分析 Naive、IMM 和 CD4/CD8 blocking 条件，估计接触型与分泌型配体—受体通信。`circle_plot.py` 把显著通信矩阵画成有向圆形网络，边宽表示相互作用权重，节点大小表示总输出。

这些计算支持图 3F 中“免疫后 T—B、T—先天细胞和 AM—肺泡上皮通信增强，而 T 细胞阻断后减弱”的比较。但必须保留边界：

- 共定位不是物理结合证明；
- 配体和受体表达不保证信号真实传递；
- 半径、细胞注释和空间分辨率都会影响通信分数。

因此它们用于提出组织协同机制，并与 depletion 实验共同解释，而不应单独作为因果证据。

### 8. 图 4：肺泡巨噬细胞是否为必要效应器

用 clodronate liposome 清除 AM 后，疫苗降低 *S. aureus* 负荷的能力明显减弱，说明 AM 是保护链条的重要组成部分。分选或体内追踪还显示，免疫后 AM 更容易吞噬标记细菌、凋亡/坏死中性粒细胞和感染上皮细胞。

这一步把“AM 有转录和染色质变化”推进到“AM 功能增强且对保护有必要贡献”。但 AM 清除不一定绝对特异，仍可能改变其他吞噬细胞和肺环境，因此结论应是 AM 具有重要因果贡献，而非它们是唯一效应器。

### 9. 图 5：训练后的肺怎样应对真正感染

SARS-CoV-2 挑战后，PCF 多重蛋白成像和 CytoMap 邻域分析显示，免疫肺更快形成 B/T 细胞、巨噬细胞、血管和其他细胞组成的结构化区域，呈现 TLS-like 组织。PR8 挑战后，NP 特异 CD8 T 细胞和 BAL 抗体更快上升，炎症因子却更受控，组织损伤也更轻。

这揭示“准备状态”的两面：它不是让肺长期保持高炎症，而是让适应性召回和组织重组更快，从而缩短病原控制时间并减少无效炎症。

当前 Zenodo 归档不包含 PCF/CytoMap 分析代码，所以图 5 的空间蛋白分支仍是 Not found，不能因为空间转录组代码已公开就认为整个空间分析都已复现。

### 10. 图 6：为什么疫苗还能改善过敏性哮喘

在 HDM 模型中，免疫小鼠的 BAL 嗜酸性粒细胞、ILC2、Th2 细胞、IL-4/IL-5/IL-13、血清 IgE 和气道黏液减少，效果在 21 天和约 3 个月仍可见。

这说明平台建立的不是简单“更强免疫”，而可能重塑肺的反应阈值和细胞互作，使感染防御增强的同时抑制某些 II 型炎症。由于该结论仍来自小鼠 HDM 模型，不能直接推出对人类哮喘有效。

### 11. 代码—论文对应关系

| 环节 | 本地证据 | 对应程度 |
|---|---|---|
| 空间数据导入与 QC | `zenodo_code/0.scanpy.ipynb`, `1.0.seurat.ipynb` | Exact |
| Harmony、UMAP、聚类和 marker | `2.0 clustering.ipynb` | Exact/Partial，含人工注释 |
| DEG 与 BTM/ORA | `3.0 clusters.DEG.GSEA.ORA.ipynb` | Exact |
| 空间邻域、距离、共现 | `4.2...ipynb`, `5.0...ipynb` | Exact |
| SOAPy 通信 | `5.3 SOAPy-cc.ipynb` | Exact |
| 圆形通信图 | `circle_plot.py` | Exact |
| T/AM 亚群分析 | 两个 `6.*_sub_clustering.ipynb` | Exact |
| scRNA-seq / scATAC-seq | Zenodo 记录中未找到 | Not found |
| PCF/CytoMap | Zenodo 记录中未找到 | Not found |
| 感染、depletion、哮喘统计 | 无完整分析脚本 | Not found |

总体代码忠实度是 **Partial**：图 3 空间转录组分支覆盖较好，但论文主体远大于这一分支。

### 12. 复现时会立即遇到的问题

1. Zenodo 有约 1 GB H5AD 和 5.2 GB RDS，本工作区只下载了代码，没有复制大数据。
2. Notebook 使用作者机器的绝对路径和外部 GMT 文件。
3. 条件拆分依赖未归档的 cell-ID 文本文件。
4. 最终细胞注释、选区和配体—受体筛选依赖缺失的 Excel 文件。
5. 没有 Conda/renv/容器或锁定版本。
6. R 与 Python notebook 串联依赖中间 RDS/H5AD，不能从原始 GEO 数据一键执行。
7. scRNA、scATAC、PCF 和大部分动物实验没有对应本地代码。

因此当前代码适合审计分析逻辑与部分图的实现，不等于开箱即用的端到端复现包。

### 13. 生物学结论的关键边界

1. 主要保护证据都来自小鼠；成年人的既往黏膜免疫史和 TLR 响应可能不同。
2. OVA 是工具抗原，不是可直接转化的人类疫苗抗原。
3. 四次鼻内免疫的频率、剂量和安全性需要人体研究。
4. “训练免疫”由长期表型、转录和染色质证据支持，但各细胞的维持机制仍未完全解析。
5. T 细胞或 AM depletion 支持因果贡献，却可能伴随非目标组织变化。
6. TLS-like 结构是形态和邻域相似，不应自动等同于成熟人类三级淋巴结构。
7. 感染与 HDM 结果不能直接外推到所有呼吸道病原体或哮喘亚型。

### 14. 一句话总结

MucosalVax 不是用一个抗原去识别所有病原体，而是用黏膜佐剂和抗原记忆共同训练肺组织：抗原特异 T 细胞维持并协调 AM、上皮和局部免疫结构，使再次遭遇异质威胁时更快控制病原体、减少组织损伤；公开代码精确覆盖其中的空间转录组证据链，但尚未覆盖整篇论文。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## MucosalVax Summary

### Motivation and Novelty

Zhang et al. address a practical vaccine problem: strain-matched vaccines are powerful but narrow, while respiratory threats evolve quickly and can emerge before matched vaccines are available. The paper proposes an intranasal mucosal vaccine that uses TLR4/7/8 agonism plus antigen-specific T-cell engagement to induce integrated lung immunity.

The novelty is biological and translational rather than algorithmic. The formulation GLA-3M-052-LS + antigen is designed to create durable tissue readiness in mouse lung. The evidence chain combines challenge experiments, flow cytometry, scRNA-seq, scATAC-seq, spatial transcriptomics, multiplexed spatial protein imaging, depletion experiments, and asthma models.

### Method Overview

Mice are immunized intranasally with a liposomal adjuvant containing GLA and 3M-052-LS plus OVA or influenza NP antigen. They are then challenged with respiratory viruses, bacteria, or allergens at multiple time points. Protection is measured by weight loss, pathogen burden, histology, asthma inflammation, and immune readouts.

Mechanistically, the vaccine induces antigen-specific CD4+ and CD8+ lung memory T cells, including TRM cells. These T cells help imprint alveolar macrophages, which show persistent activation, enhanced antigen presentation, chromatin accessibility changes, and stronger phagocytosis. After infection, vaccinated lungs rapidly form organized immune microenvironments resembling tertiary lymphoid structures and mount faster pathogen-specific recall responses.

### Evaluation

The main evidence is strong within mouse models:

- Fig. 1 shows reduced SARS-CoV-2 weight loss and lower bacterial burdens after vaccination.
- Fig. 2 shows durable OVA-specific T cells, TRM accumulation, AM activation, and scATAC evidence for persistent regulatory remodeling.
- Fig. 3 shows that combined CD4+ and CD8+ T-cell depletion abolishes protection and reduces innate/spatial immune programs.
- Fig. 4 shows that AM depletion weakens protection and that vaccinated AMs have higher phagocytic activity.
- Fig. 5 shows rapid TLS-like organization, faster NP-specific CD8+ recall, higher BAL antibody responses, and lower inflammatory cytokines after challenge.
- Fig. 6 shows reduced HDM-induced asthma features at 21 days and about 3 months.

The most important limitation is translational: all major protection claims are mouse-based. The authors explicitly note that adult human mucosal immune history may affect responsiveness and that controlled human studies are needed.

### Reproducibility

**Rating: 3.5/5.**

The experimental methods are detailed, sequencing data are deposited under GEO `GSE310116`, and the spatial-transcriptomics notebooks from Zenodo record `17651970` have now been acquired and audited locally. They directly expose QC, Harmony clustering, differential expression, BTM enrichment, Squidpy spatial analysis and SOAPy communication for the Fig. 3 branch.

The rating is not higher because the deposited notebooks are dataset-specific, lack a locked environment, contain author-local paths, and depend on unarchived annotation spreadsheets, region selections and intermediate objects. The archive does not cover the scRNA-seq, scATAC-seq, PCF/CytoMap or animal-experiment branches. The spatial workflow is code-auditable, but the full paper is not an end-to-end reproducible package.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
