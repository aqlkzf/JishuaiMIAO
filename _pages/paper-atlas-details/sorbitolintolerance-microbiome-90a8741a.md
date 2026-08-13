---
layout: default
permalink: /paper-atlas/sorbitolintolerance-microbiome-90a8741a/
title: "SorbitolIntolerance_Microbiome"
nav: false
wide: true
description: "山梨醇本来就很难被宿主小肠吸收，但健康肠道中的微生物会在结肠内继续分解它。抗生素暴露与高脂饮食共同阻碍梭菌纲（Clostridia）恢复，使微生物山梨醇脱氢酶（SDH）能力长期下降；未被清除的山梨醇积聚并通过渗透作用引起腹泻。治疗既可以直接补充能吃掉山梨醇的菌，也可以通过“丁酸—上皮 PPAR-γ—低氧—厌氧梭菌恢复”轴重建整个代谢生态位。"
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
      <span>Cell · 2024</span>
    </div>
    <h1>SorbitolIntolerance_Microbiome</h1>
    <p>High fat intake sustains sorbitol intolerance after antibiotic-mediated Clostridia depletion from the gut microbiota</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2024.01.029" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SorbitolIntolerance_Microbiome">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/connor-reid-tiffany/Metagenomics-of-Sorbitol-Intolerant-Mice" target="_blank" rel="noopener noreferrer" aria-label="Open code for SorbitolIntolerance_Microbiome">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 山梨醇不耐受：从“宿主吸收差”转向“微生物清除能力不足”

论文：*High fat intake sustains sorbitol intolerance after antibiotic-mediated Clostridia depletion from the gut microbiota*（Cell, 2024；DOI: 10.1016/j.cell.2024.01.029）

### 一句话理解这篇论文

山梨醇本来就很难被宿主小肠吸收，但健康肠道中的微生物会在结肠内继续分解它。抗生素暴露与高脂饮食共同阻碍梭菌纲（*Clostridia*）恢复，使微生物山梨醇脱氢酶（SDH）能力长期下降；未被清除的山梨醇积聚并通过渗透作用引起腹泻。治疗既可以直接补充能吃掉山梨醇的菌，也可以通过“丁酸—上皮 PPAR-γ—低氧—厌氧梭菌恢复”轴重建整个代谢生态位。

这篇论文的核心不是提出一个新的计算算法，而是用逐层干预把一条微生物—代谢物—宿主环境因果链拆开验证。仓库中的代码只覆盖宏基因组结果的交互式可视化，不能从原始测序数据复现这条完整证据链。

### 1. 为什么传统“吸收不良”解释不够

乳糖或果糖不耐受可以由特定宿主酶或转运系统缺陷解释。山梨醇不同：人体没有专一的山梨醇转运体，主要依靠被动扩散，因此健康人本来也吸收得很差。如果“吸收差”本身足以导致疾病，就很难解释为什么只有部分人对较低剂量敏感，以及为什么抗生素后症状会随微生物群恢复而消失。

作者提出替代模型：进入结肠的山梨醇是一个需要微生物继续处理的渗透性溶质。保护能力不在于宿主把它全部吸收，而在于微生物是否能在它吸水致泻之前把它代谢掉。

论文用粪便含水率作为腹泻读数：

$$
\text{fecal water content} =
\frac{W_{wet}-W_{dry}}{W_{wet}}\times100\%.
$$

其中 $W_{wet}$ 和 $W_{dry}$ 分别是干燥前后的粪便质量。这个指标直接反映水分增加，但不是炎症严重度；作者另外用结肠长度等指标排除短期山梨醇处理本身显著加重炎症的解释。

### 2. 先建立“短暂”与“长期”两个小鼠模型

#### 2.1 单独抗生素只造成短暂窗口

低脂饮食小鼠接受一次链霉素（Str，20 mg/只）后，第 1 天开始饮用 5% 山梨醇会出现体重下降、粪便含水率升高和盲肠山梨醇积聚；若到第 5 天才挑战，表型已经消失。这说明一次抗生素扰动会短暂破坏微生物代谢，但正常饮食下群落可快速恢复。

#### 2.2 高脂饮食让恢复失败

长期模型把两个风险因素叠加：45% 脂肪饮食加一次 Str，等待 4 周后再给 5% 山梨醇。图 1 显示，此时仍有体重变化、粪便含水率升高和盲肠山梨醇积聚；高脂饮食单独并不足以产生这些表型。

因此，“高脂”在这里不是直接让山梨醇产生渗透作用，而是让抗生素后的微生物群恢复失败。实验中的关键对照是低脂、低脂加 Str、高脂、高脂加 Str 四组，它把饮食效应、抗生素效应和两者交互区分开。

### 3. SDH 把症状连接到微生物代谢能力

山梨醇脱氢酶（sorbitol dehydrogenase, SDH）使用 NAD$^+$ 将山梨醇氧化为山梨糖或果糖。高脂加 Str 小鼠的盲肠 SDH 活性显著降低，与山梨醇积聚和腹泻同向变化。

作者还检测既往队列的人粪便样本。粪钙卫蛋白升高但未达到活动性 IBD 水平的患者，粪便 SDH 活性低于健康对照和 IBS 组；低 SDH 者也更常报告食用无糖食品后的胃肠症状。这让 SDH 成为有临床潜力的候选生物标志物。

但需要保留证据边界：这是既往样本和问卷中的相关性，不是前瞻性诊断试验。论文支持“潜在标志物”，尚未确定临床阈值、敏感度、特异度或跨人群泛化能力。

### 4. 16S 与宏基因组分别回答什么

作者对同一批小鼠在 Str 前和 4 周后的粪便做 16S 扩增子和 shotgun 宏基因组测序。

#### 4.1 16S：谁变少了

V3–V4 区域经过 QIIME demultiplex、Trimmomatic 修剪和 DADA2 ASV 推断，再用 RDP 训练集做分类。结果显示高脂加 Str 后 *Clostridia* 明显减少，部分动物的 *Enterococcus*（*Bacilli*）增加。LEfSe 用于描述处理前后有差异的类群。

16S 可以回答“哪些分类单元发生变化”，但不能可靠地把功能基因归到具体基因组，因此还需要宏基因组。

#### 4.2 宏基因组：代谢能力由谁提供

shotgun 流程是：

1. NovaSeq 6000，双端 150 bp；
2. DOE JGI 流程做质量控制；
3. metaSPAdes 3.15.2 对全部样本共组装；
4. BBMap 把每个样本的 reads 映射回共组装 contig；
5. 在 IMG/M 中注释和分箱，仅保留中高质量 bins；
6. 从 GFF 和覆盖信息构建基因计数矩阵；
7. 用 KEGG BRITE/`omu` 给基因加 KO 层级；
8. DESeq2 median-of-ratios 归一化，并用配对 Wald 检验比较同一动物处理前后。

共得到 11,979 个独特基因，其中 421 个属于糖类分解。多元结果表明，高脂加 Str 后，多种多元醇代谢能力下降，而不是只影响山梨醇。

配对设计很重要：同一只动物的处理前样本是自己的基线，减少动物间初始菌群差异。概念上的效应量为：

$$
\log_2FC = \log_2\left(
\frac{\text{4 weeks after Str}}{\text{before Str}}
\right).
$$

DESeq2 实际在计数模型中估计该效应，并用 Benjamini–Hochberg 校正多个基因检验；它不是简单用两个均值相除。

### 5. 为什么论文把重点放在梭菌纲和 SDH

细菌有两条主要山梨醇利用路线。

第一条先由 ABC 或 MFS 转运系统把山梨醇送入胞质，再由 NAD$^+$ 依赖的 SDH 氧化。稳态样本中，大部分 SDH reads 来自 *Clostridia* bins；高脂加 Str 后，这部分 reads 显著下降，其他类群的增加不足以补偿。

第二条是 PTS 路线：转运同时把山梨醇磷酸化为山梨醇-6-磷酸，再由山梨醇-6-磷酸 2-脱氢酶生成果糖-6-磷酸。处理后，该酶的主要来源从 *Clostridia* 转向 *Bacilli*，但总丰度没有显著下降。

图 2 的关键不是“所有山梨醇基因都消失”，而是更丰富的 SDH 路线发生净损失。分类组成替换不等于功能完全补偿；*Bacilli* 接替部分 PTS 功能，却没有恢复整体 SDH 潜力。

### 6. 用 *E. coli* Nissle 把相关性推进到因果性

如果 SDH 缺失是原因，补入能够分解山梨醇的菌应当保护小鼠，而且保护应依赖这项代谢功能。

作者首先做剂量梯度。*E. coli* Nissle 1917 在粪便中达到约 $10^8$ CFU/g，或约 $10^6$ 个 16S 拷贝/20 ng DNA 以上时，才恢复 SDH 活性并防止腹泻。这个阈值说明“菌存在”不等于功能量足够。

随后删除 `srlAEB` 山梨醇利用基因。突变株仍能在体内达到保护阈值，却不能在体外清除山梨醇，也不能在体内防止腹泻；质粒回补恢复体外代谢。这里排除了“益生菌只是占位或非特异抑炎”的解释：保护需要菌本身的山梨醇分解功能。

### 7. 三种益生菌揭示两种治疗模式

在长期模型中，作者比较 *E. coli* Nissle、产丁酸梭菌 *Anaerostipes caccae* 和 *Lactiplantibacillus plantarum*。

第 3 天三者都能降低盲肠山梨醇并缓解腹泻，符合“直接清除”模式。到第 7 天：

- *E. coli* 仍高丰度，继续直接分解山梨醇；
- *L. plantarum* 被清除并失去保护；
- *A. caccae* 也接近被清除，却仍保持保护，并恢复整个 *Clostridia* 的绝对丰度和 ASV 丰富度。

这组时间差是机制转折点。*A. caccae* 前期既能吃山梨醇又能产丁酸；后期它不需要持续大量存在，因为它已经推动内源厌氧群落恢复。不能把这种持久效应简单归因于益生菌长期定植。

### 8. 丁酸—PPAR-γ—上皮低氧轴怎样恢复生态位

结肠上皮利用丁酸进行氧化代谢，并通过 PPAR-γ 信号增加耗氧，使上皮及靠近腔面的环境保持低氧。低氧限制氧向肠腔扩散，有利于严格厌氧的 *Clostridia*，不利于兼性厌氧菌在含氧生态位中扩张。

高脂加 Str 后，盲肠丁酸下降，*Lachnospiraceae* 和 *Ruminococcaceae* 等产丁酸梭菌减少，pimonidazole 染色显示上皮低氧丢失。*A. caccae* 同时恢复丁酸、低氧和梭菌群落；*E. coli* 与 *L. plantarum* 虽可直接处理山梨醇，却不恢复这三项指标。

因果链可写成一个正反馈恢复环：

$$
\textit{A. caccae}/\text{butyrate}
\rightarrow \text{epithelial PPAR-}\gamma
\rightarrow \text{oxygen consumption}
\rightarrow \text{epithelial hypoxia}
\rightarrow \textit{Clostridia recovery}
\rightarrow \text{butyrate + SDH capacity}.
$$

pimonidazole 在低氧组织中形成可检测加合物，因此荧光增强代表组织低氧增强；它不是直接测量肠腔氧分压。作者用 ImageJ 比较上皮—肠腔方向的信号峰值，支持但不等同于连续氧浓度测量。

### 9. Tributyrin 与上皮特异性 *Pparg* 敲除提供机制检验

tributyrin（TB）在大肠释放丁酸。治疗 3 天只产生有限效果，到第 7 天才明显恢复丁酸、上皮低氧、*Clostridia* 丰度和 *Lachnospiraceae*，并降低山梨醇及粪便含水率。这种延迟符合“先重建生态位，再恢复群落功能”，而不是 TB 直接分解山梨醇。

更关键的是上皮特异性 *Pparg* 缺失。在 *Pparg*^fl/fl^ *Villin*^cre/−^ 小鼠中，*A. caccae* 或 TB 都不能恢复低氧、不能阻止山梨醇积聚，也不能防止腹泻。由此可见，丁酸保护并非只靠直接作用于细菌，而需要宿主上皮 PPAR-γ 这个中介。

遗传实验支持“PPAR-γ 必要”，TB 实验支持“丁酸输入足以启动恢复过程”；二者与时间序列、菌群和代谢物读数共同构成因果证据。

### 10. 5-ASA 为什么更适合预防，而不是立即止泻

5-氨基水杨酸（5-ASA）可激活上皮 PPAR-γ。若在已经长期不耐受的小鼠开始山梨醇挑战时给药，3 天内不能立即缓解，到第 7 天才恢复丁酸、低氧和梭菌，并减少腹泻。这再次说明生态恢复需要时间。

若从 Str 当天开始预防性给 5-ASA，4 周后 *Clostridia* 已恢复，山梨醇挑战时不再积聚，粪便含水率也较低；该效果在上皮 *Pparg* 缺失小鼠中消失。图 7 因此把“可逆转的宿主生态位”连接到预防策略。

这仍是小鼠机制验证，不应直接解读为临床用药建议。剂量、适用人群、长期安全性和临床疗效需要人体试验。

### 11. 本地 Shiny 代码真正做了什么

代码仓库是一个预计算宏基因组结果浏览器，入口 `app.R` 组织四个 Shiny 模块：heatmap、volcano、dotplot 和按分类群显示基因 counts 的柱图。

#### 11.1 热图

`heatmap_module.R` 读取 `tidy_normalized_countdata_HF_Strep.rds`，对 abundance 做：

$$
x_{display}=\ln(1+x_{normalized}),
$$

再按用户选择的 KO 类别筛选基因，转换为 sample × KO 矩阵，并用 `heatmap.2` 显示。这里的 RDS 已经是上游 DESeq2 归一化结果；应用不会重新拟合归一化模型。

#### 11.2 火山图

`volcano_module.R` 读取 `HF_Strep_After_vs_Before.rds`，横轴是 `log2FoldChange`，纵轴是 $-\log_{10}(padj)$，并在 $padj=0.05$ 画虚线。界面允许把 fold change 乘以 $-1$ 来反转对比方向，但这只改变展示方向，不重新计算统计检验。

#### 11.3 点图与置信区间

`dotplot_module.R` 合并预归一化 abundance、样本时间点和预计算显著性，再按基因显示处理前后样本。代码还用 `log2FoldChange` 与 `lfcSE` 画近似 95% 区间。实现写成：

$$
\log_2FC \pm qnorm(0.025)\times lfcSE.
$$

由于 `qnorm(0.025)` 为负数，代码中的 `ymin`/`ymax` 表达式在符号次序上看似反向；绘图层通常仍能据两个端点显示区间，但这是值得在复用时检查的实现细节。

#### 11.4 按分类群分解 gene counts

`RA_plot_module.R` 从原始 counts 加 taxonomy 的 RDS 中选择一个基因，再按 Phylum、Class、Order、Family、Genus 或 species 聚合展示。它支持图 2E–F 式的来源分解，但不执行上游 reads mapping、binning 或分类注释。

### 12. 论文与代码的 Exact / Partial / Not found 边界

#### Exact：浏览器展示层高度对应

- 火山图使用预计算的 `log2FoldChange`、`padj` 和 `lfcSE`；
- 热图对归一化 abundance 做 $\ln(1+x)$；
- 点图合并时间点、KO 和预计算差异统计；
- gene-by-taxa 图读取带 bin taxonomy 的 counts；
- app 明确说明 metaSPAdes 共组装、BBMap 回贴和 IMG/M 注释背景。

#### Partial：结果存在，但生成过程不在仓库

- DESeq2 归一化与 paired Wald 结果以 RDS 形式存在，拟合脚本缺失；
- KEGG/BRITE 层级字段存在，`omu` 注释和 KEGG API 获取脚本缺失；
- taxonomy 与 gene counts 可以浏览，但从 GFF/coverage 构造矩阵的自定义脚本缺失；
- Shiny 能重画结果，不等于能复现论文宏基因组分析。

#### Not found：不能从本地代码快照重建

- QIIME/Trimmomatic/DADA2 的 16S 完整脚本；
- metaSPAdes、BBMap、IMG/M 分箱及质量过滤的可运行工作流和精确参数；
- DESeq2 paired design、LEfSe 和 `omu` 的上游分析脚本；
- 动物实验、菌株构建、培养、qPCR、SDH、GC–MS、pimonidazole 成像和人样本分析；
- *srlAEB*、上皮 *Pparg*、TB 与 5-ASA 干预本身。

因此，本地仓库对“论文数据如何交互展示”具有较高一致性，对“论文从原始数据到结果如何计算”只有部分覆盖，对湿实验机制没有可执行复现能力。

### 13. 读图时最重要的证据顺序

七张主图形成一条递进链：

1. 图 1：高脂加 Str 造成长期表型，SDH 与小鼠和人症状相关；
2. 图 2：梭菌减少与 SDH 基因功能净损失相连；
3. 图 3：剂量阈值和 `srlAEB` 突变证明直接山梨醇分解的必要性；
4. 图 4：三种益生菌的时间差揭示直接清除与生态恢复两种模式；
5. 图 5：*A. caccae* 特异恢复丁酸与上皮低氧；
6. 图 6：TB 与上皮 *Pparg* 敲除验证丁酸—PPAR-γ 轴；
7. 图 7：5-ASA 的延迟治疗和预防效果验证宿主生态位可被干预。

任何单张图都不足以独立证明完整链条；论文的力量来自代谢、菌群、组织环境、菌株遗传和宿主遗传证据相互闭合。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary — High fat intake sustains sorbitol intolerance after antibiotic-mediated Clostridia depletion

**Paper**: Lee et al., *Cell* 187:1191-1205 (2024)
**DOI**: 10.1016/j.cell.2024.01.029
**Category**: datasource/atlases_resources
**Type**: Mechanistic biology study (not a computational methods paper)

---

### Motivation & Novelty

**Biological problem**: Sorbitol intolerance affects up to 30% of people in high-income countries, causing diarrhea, abdominal distention, and flatulence. It was conventionally attributed to malabsorption — the same mechanism as lactose intolerance. However, unlike lactose, humans lack a dedicated sorbitol transporter, so poor absorption is universal. This raises the question: why do only some people develop intolerance?

**Clinical context**: Patients with a recent history of antibiotic use combined with high fat intake develop prolonged diarrhea with elevated fecal calprotectin (50-200 μg/g) — a syndrome at the intersection of IBS and IBD. Prior work (Lee et al., *Cell Host Microbe* 28:273-284, 2020) showed this combination impairs microbiota recovery, but the connection to specific dietary intolerances was unexplored.

**Limitations of existing approaches**:
- Conventional view: sorbitol intolerance = malabsorption (no experimental evidence for reduced passive diffusion in intolerant patients)
- Antibiotic-induced intolerance was known to be transient (resolves within 5 days), but prolonged intolerance in IBS/IBD patients was unexplained
- No mechanistic link between microbiota composition and sorbitol catabolism capacity had been established
- No diagnostic biomarker for sorbitol intolerance existed

**Unique contributions**:
1. Establishes that **microbial sorbitol catabolism** (not host malabsorption) is the primary protective mechanism
2. Identifies **Clostridia** as the dominant source of sorbitol dehydrogenase (SDH) genes during homeostasis
3. Demonstrates a causal chain: Str+HF → Clostridia depletion → impaired SDH → sorbitol accumulation → diarrhea
4. Identifies **fecal SDH activity** as a potential diagnostic biomarker (validated in human samples)
5. Demonstrates *A. caccae* as a "second-generation probiotic" with dual mechanism: direct sorbitol catabolism + butyrate-mediated microbiota recovery
6. Establishes the **butyrate → PPAR-γ → epithelial hypoxia → Clostridia recovery** axis using genetic (Pparg fl/fl Villin cre) and pharmacological (tributyrin, 5-ASA) approaches
7. Shows 5-ASA prophylaxis can prevent prolonged sorbitol intolerance

---

### Method Overview

**Experimental system**: C57BL/6J mice on LF (10% fat) or HF (45% fat) diet, treated with single-dose streptomycin (20 mg/mouse). Sorbitol challenge: 5% (w/v) in drinking water.

**Key readouts**:
- Fecal water content (diarrhea severity)
- Cecal sorbitol concentration (D-sorbitol colorimetric assay)
- Cecal SDH activity (colorimetric assay)
- Microbiota composition (16S rRNA amplicon sequencing, DADA2 → ASVs)
- Metagenomic gene content (shotgun sequencing, metaSPAdes co-assembly, IMG/M binning, KEGG annotation)
- Cecal butyrate (GC-MS with deuterated internal standards)
- Epithelial hypoxia (pimonidazole staining, ImageJ quantification)

**Probiotic interventions**: *E. coli* Nissle 1917 (WT and *srlAEB* mutant), *A. caccae*, *L. plantarum* NCIMB8826-R

**Pharmacological interventions**: Tributyrin (5 g/kg oral gavage), 5-ASA (1650 mg/kg/day in chow)

**Genetic model**: *Pparg*^fl/fl^ *Villin*^cre/−^ mice (intestinal epithelium-specific PPAR-γ knockout)

**Computational pipeline**: 16S → QIIME 1.8 → Trimmomatic → DADA2 → phyloseq → DESeq2/LEfSe; Metagenomics → metaSPAdes → BBMap → IMG/M → omu (KEGG) → DESeq2

**Code deposited**: R Shiny app for interactive visualization of metagenomic data (https://github.com/connor-reid-tiffany/Metagenomics-of-Sorbitol-Intolerant-Mice)

---

### Evaluation

#### Datasets
- **Mouse experiments**: C57BL/6J mice (n=14 per group for main experiments), multiple independent experiments
- **Human fecal samples**: Banked from Lee et al. 2020 (CHA Bundang Medical Center + Yonsei University, Korea); groups: healthy controls, IBS patients, patients with elevated calprotectin (50-200 μg/g)
- **Metagenomic data**: NCBI BioProject PRJNA892219 (16S), JGI IMG/M Taxon ID 3300051405 (metagenome)

#### Key Results
- Str+HF diet → prolonged sorbitol intolerance at 4 weeks (increased fecal water content, elevated cecal sorbitol, reduced SDH activity)
- HF diet alone: no sorbitol intolerance
- Metagenomic analysis: 11,979 unique genes from medium/high quality bins; Clostridia are dominant source of SDH genes during homeostasis
- SDH encoding reads significantly reduced after Str+HF (p<0.05, DESeq2)
- Probiotic protection threshold: ~10^8 CFU/g feces (E. coli) or ~10^6 16S copies/20 ng DNA (A. caccae)
- srlAEB mutant E. coli: no protection despite colonization above threshold (genetic causality)
- A. caccae at day 7: still protects despite being cleared (butyrate-mediated mechanism)
- A. caccae restores Clostridia absolute abundance and richness (qPCR + 16S ASVs)
- Pparg fl/fl Villin cre mice: A. caccae and tributyrin no longer protect (PPAR-γ required)
- 5-ASA prophylaxis: prevents sorbitol intolerance, restores Clostridia, requires epithelial PPAR-γ
- Human data: patients with elevated calprotectin have lower fecal SDH than IBS patients or healthy controls; low SDH correlates with sugar-free food intolerance (questionnaire)

#### Statistical Methods
- Two-way ANOVA + Tukey's multiple comparison (body weight over time)
- One-way ANOVA + Tukey's (most group comparisons)
- Student's t-test (two-group comparisons)
- Kruskal-Wallis test (pimonidazole staining intensities)
- DESeq2 paired Wald test + Benjamini-Hochberg FDR (metagenomic differential abundance)
- LEfSe LDA scores (microbiota profiling)
- All analyses: GraphPad Prism 8.0

---

### Reproducibility

**Rating: 3/5**

**Strengths**:
- Mouse model is well-described with specific doses, diets, and timepoints
- Genetic validation (Pparg fl/fl Villin cre) provides strong mechanistic evidence
- Raw sequencing data deposited (NCBI PRJNA892219, JGI IMG/M 3300051405)
- Shiny app allows interactive exploration of metagenomic data
- Key reagents (bacterial strains, plasmids, primers) are in the Key Resources Table

**Weaknesses**:
- **Critical gap**: The analysis pipeline (metaSPAdes assembly, BBMap mapping, IMG/M binning, DESeq2 scripts, DADA2 pipeline, omu annotation) is not deposited. Only the downstream visualization app is available.
- IMG/M binning requires institutional access and is not fully reproducible without the exact workflow parameters
- The custom GFF parsing script for gene count matrices is mentioned but not deposited
- The custom script for Anaerostipes primer design (NCBI Entrez + DEGEPRIME) is not deposited
- Human fecal samples are banked from a previous study — not directly available

**Practical notes**:
- To reproduce the Shiny app: `git clone https://github.com/connor-reid-tiffany/Metagenomics-of-Sorbitol-Intolerant-Mice` and run `shiny::runApp()` in R
- Required R packages: shiny, bslib, shinyWidgets, ggplot2, DT, officer, thematic, colourpicker, reshape2, RColorBrewer, gplots, gridExtra, cowplot, ggrepel, ggplotify
- The app is also deployed at https://clostridia-enjoyer.shinyapps.io/sorbitolMetagenome/
- Mouse experiments require specific diets (Teklad TD110675, TD06415, TD180827) and bacterial strains available from the Bäumler lab (UC Davis)
- Pimonidazole staining requires Hypoxyprobe-1 kit (HP1-1000)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
