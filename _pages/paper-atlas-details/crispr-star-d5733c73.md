---
layout: default
permalink: /paper-atlas/crispr-star-d5733c73/
title: "CRISPR-StAR"
nav: false
wide: true
description: "CRISPR-StAR 的关键不是发明更复杂的统计模型，而是改变比较对象：不再用经历不同瓶颈的起始库和终点肿瘤比较，而是在同一个已经植入的 UMI 克隆内部，用 inactive 后代作为 active 敲除后代的配对对照。"
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
      <span>Technology Platforms</span>
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>CRISPR-StAR</h1>
    <p>CRISPR-StAR enables high-resolution genetic screening in complex in vivo models</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/EstherU-gith/CRISPR-StAR" target="_blank" rel="noopener noreferrer" aria-label="Open code for CRISPR-StAR">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CRISPR-StAR 方法详解：把“同一个克隆”变成自己的对照

### 1. 这篇论文要解决什么问题？

常规 pooled CRISPR 筛选通常比较两样东西：起始质粒库/起始细胞群中的 sgRNA 丰度，以及筛选结束后的 sgRNA 丰度。如果某条 sgRNA 在终点显著减少，就推断其靶基因对细胞生存或增殖重要。

这个逻辑在体外大规模培养中通常成立，因为每条 sgRNA 可以由数百到上千个独立细胞承载。但在移植瘤、类器官或其他复杂模型中，实验会遭遇两个远大于真实基因效应的噪声源：

1. **瓶颈效应**：注入很多细胞，真正成功植入的只有很少一部分；
2. **克隆生长异质性**：植入后的不同克隆扩增速度可相差多个数量级。

论文测得，不同模型注入最多约 $10^6$ 个细胞后，通常只回收到约 4,800–20,500 个条形码；一个典型全基因组库却含有数万至十万条 sgRNA。Yumm450R 全基因组体内筛选虽然使用了 143 个肿瘤，平均仍只有 2.3 个 UMI/sgRNA、8.7 个 UMI/基因（`paper.md:30-30,82-82`）。

因此，常规“终点 active sgRNA 对比起始质粒库”的分析无法区分：

- 这条 sgRNA 因靶向必需基因而消失；
- 承载它的细胞只是没有植入；
- 它所在的克隆碰巧长得特别慢或特别快。

CRISPR-StAR 的目标不是在统计模型里事后消除这些噪声，而是在实验设计阶段给每个克隆制造一个同源内部对照。

### 2. 现有技术为什么还不够？

CRISPR-StAR 建立在几项已有技术之上，但解决的是它们单独无法解决的问题：

- **常规 pooled CRISPR–Cas9 筛选**需要约 500–1,000 个细胞/sgRNA 才能抵抗随机漂移；复杂体内模型往往无法达到这一覆盖度。
- **CRISPR-Switch**（*Nature Communications*, 2019）可以通过 Cre 重组开关 sgRNA，但单纯“延迟打开”并不会自动产生一个与实验细胞同克隆、同环境的对照群体。
- **CRISPR-UMI**（*Nature Methods*, 2017）可用 UMI 追踪单细胞来源的克隆，能看见哪些克隆植入和扩增，却不能仅凭追踪判断某个克隆的变化来自基因敲除还是微环境。
- **MAGeCK**（*Genome Biology*, 2014）可以从计数中计算基因效应和 RRA 排名，但统计工具无法挽救起始库与终点肿瘤之间不可比的采样过程。

CRISPR-StAR 的新意是把“可诱导 sgRNA”和“克隆 UMI”组合成一个主动/失活双结果系统：同一个植入克隆在肿瘤建立后，随机产生实验细胞和对照细胞。

### 3. 核心直觉：不要拿肿瘤和质粒库比，拿同一克隆的两类后代比

设某个带有 sgRNA $g$ 和 UMI $u$ 的单细胞成功植入并扩增。等这个克隆已经建立后，再用 tamoxifen 激活 CreERT2。CRISPR-StAR 构建体发生两种互斥且不可逆的重组结果：

- **active**：删除 STOP 片段，保留可工作的 tracr RNA，sgRNA 生效；
- **inactive**：删除 tracr RNA，sgRNA 失活，但保留相同的 sgRNA 身份和 UMI。

于是，同一个克隆中会交错出现 active 与 inactive 后代。它们共享：

- 相同的植入事件；
- 相同的克隆遗传背景；
- 相似的营养、氧气、酸度、免疫压力和空间位置；
- 相同的 sgRNA 与 UMI 序列来源。

主要差别是 sgRNA 是否真正发挥作用。若 active 后代相对 inactive 后代减少，才更有理由把差异归因于靶基因敲除。

```text
一个已植入的 UMI 克隆
          |
          |  tamoxifen -> CreERT2
          v
   随机、互斥重组
      /          \
 active          inactive
 sgRNA生效       sgRNA失活
      \          /
   同一克隆、同一局部环境
          |
   比较 active / inactive
```

这就是论文标题中 StAR（Stochastic Activation by Recombination）的含义。

### 4. 为什么要把 active:inactive 比例调到接近 1:1？

第一代载体只有约 35–41% active 细胞，active 群体较小，会限制检测负向选择的动态范围。作者调整 loxP/lox5171 的相对位置、间距和序列背景，最终得到 StAR 4GN 载体，在多种细胞中约为 55:45 active:inactive（`paper.md:50-53`；`figure_02.png`、`figure_11.jpg`）。

接近 1:1 的好处是：

- active 与 inactive 两侧都有足够计数；
- active 细胞发生强烈耗竭时仍有可测动态范围；
- 两种构象的 PCR 扩增偏差更容易控制。

载体还把选择盒放在两种重组结果都会删除的位置，减少病毒逆转录期间提前重组带来的污染；未重组构建体因扩增片段过长，也不会进入特异 PCR 读出。

### 5. 从实验到计算的完整流程

```text
每基因5条sgRNA + 每条sgRNA超过10^3个UMI
                    |
                    v
        克隆进优化后的 StAR 4GN 载体
                    |
                    v
       低MOI转导 Cas9/CreERT2 单克隆细胞
                    |
          +---------+---------+
          |                   |
        体外                植入小鼠
          |                   |
          +------建立细胞群/肿瘤------+
                              |
                    tamoxifen诱导重组
                              |
                    active / inactive
                              |
                       竞争生长14天
                              |
                gDNA、构象特异PCR、NGS
                              |
         状态识别 -> UMI过滤 -> 批次归一化
                              |
              active为treatment，inactive为control
                              |
                  MAGeCK LFC/RRA与命中基因
```

#### 5.1 建库与细胞准备

人和小鼠全基因组库每个基因设计五条 sgRNA，并按可成药基因、细胞表面、代谢、转录/表观遗传、信号、RNA 生物学等类别拆成九个 subpool。每条 sgRNA 与超过 $10^3$ 个随机 UMI 组合，使独立植入克隆可被追踪（`paper.md:67-70`）。

细胞先稳定表达 Cas9 与 CreERT2。作者筛选诱导后报告基因下降至少 80–90%、未诱导时泄漏很低的单克隆。病毒转导使用 MOI 0.25，尽量让一个细胞只获得一个构建体（`paper.md:222-237`）。

#### 5.2 先建立肿瘤，再启动敲除

Yumm450R 细胞注射后第 10 天才给予 tamoxifen，A375R 为第 14 天；之后再筛选 14 天（`paper.md:246-249`）。这个顺序很关键：早期“能否植入”的差异发生在 sgRNA 激活之前，因此不应直接被当成基因效应。

#### 5.3 NGS 读出

论文的测序设计至少读取：

- read 1：75 bp，用于区分 active/inactive 构象；
- 两个实验 index：各 9 bp；
- UMI：11 bp。

论文称使用 Bowtie、SAMtools 与 FASTX-Toolkit 提取 sgRNA 和 UMI，并根据 read 1 末端序列把 `TTTT` 判为 inactive、含 `CAGC` 判为 active（`paper.md:252-264`）。

**代码证据边界：**仓库没有 BAM 到计数表的实现。较早 R 脚本从已经带有 sample index 的表开始，通过 index 中是否含 `inactive` 来分配状态（`Yumm_Apools_July2021_fullAnalysis_2023.R:16-36`）。因此，序列级状态分类在当前代码快照中是 **Not found**。

### 6. 体内 UMI 数据如何清洗？

对 sgRNA $g$、UMI $u$ 的观测，先定义总读数

$$
s_{g,u}=A_{g,u}+I_{g,u},
$$

其中 $A$、$I$ 分别为 active 与 inactive 读数。

#### 6.1 UMI hopping

同一个 UMI 如果被错误分配给多条 sgRNA，通常会有一个高读数主配对和若干极低读数伪配对。论文计算

$$
r_{g,u}=\frac{s_{g,u}}{\max_{g'}s_{g',u}},
$$

当高丰度 UMI 的最大计数仍超过 100,000 时，删除 $r_{g,u}\le0.001$ 的低比例配对。较早脚本在 `Yumm_Apools_July2021_fullAnalysis_2023.R:167-179` 直接实现这一规则。

#### 6.2 聚合型 UMI

删除包含以下同聚物的 UMI：

- 连续至少 7 个 C、A 或 T；
- 连续至少 5 个 G。

G 的阈值更严格，是因为 NextSeq 2000 的双通道测序把“无颜色”解释为 G，更容易产生假 G 延伸（`paper.md:279-282`）。

#### 6.3 总读数与 UMI 数量

论文写的是删除总读数 ≤20 的 sgRNA–UMI–replicate；最终脚本却使用 `filter(sumReads >= 20)`，会保留恰好 20 的观测（`20231123_Combine_A_B.E.FC2_screens8.R:882-900,1069-1084`）。这是明确的论文—代码边界差异，应视为 **Partial** 而不是 Exact。

基因层面只保留至少三个 UMI 支持的基因。代码在 MAGeCK 结果中使用 `num >= 3`（`:1127-1140`）。

### 7. 两个筛选批次如何合并？

全基因组实验分批次 A 与 B.E 完成。代码不是只用一个总 reads 数做 library-size normalization，而是使用非必需基因的 active/inactive 中位比例，分别计算两个通道的缩放因子：

$$
f_A=\frac{\operatorname{median}(p_{A,\mathrm{batch\ A}})}
{\operatorname{median}(p_{A,\mathrm{batch\ B.E}})},
$$

$$
f_I=\frac{\operatorname{median}(p_{I,\mathrm{batch\ A}})}
{\operatorname{median}(p_{I,\mathrm{batch\ B.E}})}.
$$

B.E 批次的 active 和 inactive 读数分别乘以 $f_A$、$f_I$，再与 A 批次合并。体外实现在 `20231123_Combine_A_B.E.FC2_screens8.R:150-205`，体内实现在 `:1007-1063`。

这个细节很重要：它校正的是两个批次的重组通道平衡，而不是笼统地把所有计数乘同一个系数。

### 8. 如何计算效应？

#### 8.1 sgRNA 层面的直观分数

active 与 inactive 都加 0.5 伪计数后，代码中的 StAR guide score 为

$$
\operatorname{LFC}^{\mathrm{StAR}}_g=
\log_2\left(\frac{A_g+0.5}{I_g+0.5}\right).
$$

- LFC < 0：active 后代相对 inactive 后代减少，提示靶基因缺失不利；
- LFC > 0：active 后代相对富集，提示潜在抑癌基因或生长限制因子。

直接代码位于 `20231123_Combine_A_B.E.FC2_screens8.R:1886-1903`。

#### 8.2 基因层面的 MAGeCK 分析

代码把 active 计数作为 MAGeCK treatment，把 inactive 计数作为 control，并对两个通道加 0.5（`:1085-1099`）。MAGeCK 输出基因的中位 `neg.lfc` 与 RRA score。体外筛选使用 paired 设计。

作为 conventional 对照，体内 active reads 与质粒库 reads 比较（`:2501-2575`）。这种比较无法使用 UMI 公平匹配质粒库，因为质粒库复杂度远高于肿瘤中的少量植入 UMI（`paper.md:297-297`）。

#### 8.3 dAUC、ROC 与 PR

代码先按 LFC 排序 essential 与 non-essential sgRNA，计算累计曲线，再用梯形法积分：

$$
\operatorname{AUC}=\sum_i(x_{i+1}-x_i)\frac{y_i+y_{i+1}}{2},
$$

$$
\operatorname{dAUC}=\operatorname{AUC}_{\mathrm{essential}}-
\operatorname{AUC}_{\mathrm{nonessential}}.
$$

直接实现见 `20231123_Combine_A_B.E.FC2_screens8.R:1900-1934`。ROC 与 precision-recall 的 pROC/绘图逻辑见 `:3240-3281`。

### 9. 实验结果是否支持这个设计？

#### 9.1 人工瓶颈

作者把覆盖度依次降到约 1、4、16、64、256 和 1,024 个细胞/sgRNA：

- conventional 在 1 个细胞/sgRNA 时重复相关性降到约 $R=0.07$；
- CRISPR-StAR 在所有条件都保持 $R>0.68$；
- 扩展图中 StAR dAUC 约维持在 0.40–0.43，最低覆盖时 AUROC 仍约 0.91–0.93；
- conventional 在低覆盖下出现明显 dropout 条带，dAUC 与 AUROC 均显著下降。

这些结果由 `figure_01.png`、`figure_08.jpg`、`figure_09.jpg` 和 `figure_10.jpg` 直接支持。

#### 9.2 全基因组体内筛选

在极稀疏的 Yumm450R 筛选中：

- 两批次相关性 conventional 为 $R=0.14$，StAR 为 $R=0.54$；
- Figure 3 的 AUROC：in vitro 0.995、StAR 0.892、conventional 0.695、random 0.500；
- 12.8% sgRNA 没有 active reads，其中 45.9% 同时没有 inactive reads，更像是激活前就没有植入，而不是强必需基因。

Figure 3 最有解释力的不是“红色 essential 更低”，而是 StAR 把黑色 non-essential 基因的噪声分布显著收紧。方法主要通过减少中性基因噪声提高命中质量。

### 10. 生物学发现

体内与体外基因效应比较显示，线粒体内膜、TCA 循环、电子传递链、氧化磷酸化和线粒体核糖体相关基因在体内更依赖；相关基因集合富集约两倍，$P=7.5\times10^{-5}$（`paper.md:105-105`；`figure_04.png`）。

验证库在论文判据下确认了：

- 23 个候选富集基因中的 12 个；
- 80 个候选体内特异耗竭基因中的 23 个。

TripleColour-StAR 使用三种荧光状态追踪未重组、active 和 inactive 构象。单基因竞争实验支持 Aip、Birc6、Uba6、Stk40、Wdr48、Zbtb10 在体内比体外更重要（`figure_06.png`、`figure_13.jpg`）。跨物种热图还显示多项依赖可从小鼠 Yumm450R 延伸至人 A375/A375R 黑色素瘤模型（`figure_05.png`）。

### 11. 方法的局限

1. **依赖稳定的 Cas9/CreERT2**：植入后沉默会削弱敲除与信噪比。
2. **tamoxifen 暴露不均**：肿瘤血管化差会导致重组不完全；特异 PCR 可排除未重组构建体，但无法补救低编辑效率。
3. **需要工程化细胞**：并非所有原代组织都能直接应用。
4. **生物学验证范围有限**：全基因组发现主要来自治疗耐受小鼠黑色素瘤异种/同种移植背景。
5. **计算仓库不自包含**：大量输入、对照基因表和 MAGeCK 输出来自绝对 `/Volumes/...` 路径。

### 12. 代码能复现到什么程度？

代码—论文一致性为 **medium**。两份 R 脚本确实包含关键下游逻辑：

- active/inactive 合并与 0.5 伪计数；
- 用非必需基因做 active/inactive 分通道批次归一化；
- active 对 inactive 的 MAGeCK 输入方向；
- 至少三个 UMI 的基因过滤；
- StAR LFC、dAUC、ROC、PR；
- conventional active 对质粒库比较。

但从仓库快照单独重跑论文结果是 **Not found**：

- BAM demultiplex、Bowtie/SAMtools/FASTX 映射和序列级状态分类缺失；
- 最终 A/B.E `poly_hop.filtered` 输入的生成过程缺失；
- 原始/中间表、对照基因集、MAGeCK 输出均不在仓库；
- MAGeCK 命令是注释，脚本随后直接从绝对路径读取结果；
- 没有环境锁、测试或可移植入口。

因此，这个仓库更像“分析过程记录”，而不是可一键执行的软件包。

### 13. 一句话理解 CRISPR-StAR

CRISPR-StAR 的关键不是发明更复杂的统计模型，而是改变比较对象：**不再用经历不同瓶颈的起始库和终点肿瘤比较，而是在同一个已经植入的 UMI 克隆内部，用 inactive 后代作为 active 敲除后代的配对对照。**

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CRISPR-StAR Summary

### Paper at a Glance

**CRISPR-StAR enables high-resolution genetic screening in complex in vivo models** introduces CRISPR-StAR (Stochastic Activation by Recombination), an internally controlled pooled CRISPR screening platform. It was published in *Nature Biotechnology* 43, 1848–1860 (2025), DOI `10.1038/s41587-024-02512-9`.

The central problem is that conventional pooled screens require hundreds of independent cells per sgRNA. In tumors, organoids and other heterogeneous models, most cells fail to engraft and a small number of survivors expand very unevenly. Starting-library versus endpoint abundance then mixes gene effects with stochastic dropout and clone-specific growth.

### What Is New

CRISPR-StAR creates its control after the bottleneck, inside each UMI-marked clone. An inducible construct undergoes one of two irreversible Cre recombination outcomes:

- an **active sgRNA** that produces the perturbation;
- an **inactive sgRNA** with the same sgRNA identity and UMI, serving as the matched control.

Because active and inactive descendants arise from the same engrafted cell and grow in the same local environment, their comparison controls for clonal identity, engraftment history and microenvironmental exposure. The design combines CRISPR-Switch (*Nature Communications*, 2019) with CRISPR-UMI lineage tracing (*Nature Methods*, 2017), while MAGeCK (*Genome Biology*, 2014) supplies gene-level LFC and RRA analysis.

### Method Overview

```text
sgRNA library + many UMIs per guide
        -> transduce Cas9/CreERT2 cells
        -> establish culture or tumor
        -> tamoxifen induces stochastic active/inactive recombination
        -> 14-day competition
        -> NGS of state, guide and UMI
        -> UMI artifact filtering + batch normalization
        -> active-versus-inactive MAGeCK analysis
        -> LFC/RRA, dAUC, ROC/PR and context-specific hits
```

The genome-wide libraries use five sgRNAs per gene and more than $10^3$ UMIs per sgRNA. The optimized StAR 4GN vector produces an approximately 55:45 active:inactive balance. In vivo, perturbations are induced after tumors are established, excluding initial engraftment from the intended gene-effect readout.

Computationally, the paper filters UMI hopping and polymeric UMIs, removes low-read sgRNA–UMI observations, normalizes the two screen batches with non-essential controls, adds a 0.5 pseudocount, and analyzes active reads as treatment versus inactive reads as control. The directly visible guide score is

$$
\operatorname{LFC}^{\mathrm{StAR}}_g=
\log_2\left(\frac{A_g+0.5}{I_g+0.5}\right).
$$

Gene effects and RRA scores are then obtained with MAGeCK, retaining in-vivo genes supported by at least three UMIs.

### Evaluation and Main Results

#### Artificial bottlenecks

The pilot screen tested approximately 1, 4, 16, 64, 256 and 1,024 cells per sgRNA. At one cell per sgRNA, conventional replicate correlation fell to about $R=0.07$, while CRISPR-StAR remained above $R=0.68$ across all tested coverages. Extended-data figures show StAR dAUC staying near 0.40–0.43 and AUROC near 0.91–0.93 even at the lowest coverage, whereas conventional performance deteriorates sharply.

#### Genome-wide in-vivo screen

The Yumm450R melanoma screen used 143 tumors but averaged only 2.3 cells per sgRNA and 8.7 cells per gene. In this sparse setting:

- batch reproducibility improved from $R=0.14$ for conventional analysis to $R=0.54$ for CRISPR-StAR;
- Figure 3 reports AUROC of 0.892 for StAR versus 0.695 for conventional analysis and 0.500 for random;
- essential/non-essential separation improved in LFC/RRA, dAUC, ROC and precision-recall analyses;
- among guides with no active reads, 45.9% also lacked inactive reads, revealing likely pre-induction dropout that conventional analysis would misclassify as strong essentiality.

The improvement is driven primarily by suppression of neutral-gene noise rather than stronger depletion of essential genes.

#### Biological discoveries

Comparing in-vivo and in-vitro effects revealed an in-vivo-specific dependency on mitochondrial-inner-membrane and oxidative-phosphorylation genes (two-fold enrichment, $P=7.5\times10^{-5}$). The validation library confirmed 12 of 23 nominated enriching genes and 23 of 80 nominated in-vivo-specific depleted genes under the paper's criteria. TripleColour-StAR single-gene assays supported stronger in-vivo dependence for Aip, Birc6, Uba6, Stk40, Wdr48 and Zbtb10. Cross-species screens indicated that many dependencies extend from mouse Yumm450R to human A375 melanoma models.

### Limitations

- CRISPR-StAR requires stable Cas9 and CreERT2 expression. Silencing and incomplete tamoxifen exposure reduce editing and dynamic range.
- It requires engineered cell populations and is not immediately applicable to every primary tissue or model.
- The genome-wide biological demonstration is centered on a therapy-resistant mouse melanoma allograft; broader generality remains to be tested.
- UMI/state sequencing and recombination-specific PCR add experimental complexity.
- The paper's read-filter prose removes totals ≤20, while the final R script retains `sumReads >= 20`.

### Code and Reproducibility

**Code-paper fidelity: medium.** The two R scripts directly implement important downstream steps: active/inactive pooling, channel-specific batch normalization, 0.5 pseudocounts, active-versus-inactive MAGeCK inputs, three-UMI filtering, StAR LFC, dAUC, ROC/PR and conventional active-versus-library comparison.

- inputs, control lists, normalized plasmid tables and MAGeCK outputs are loaded from unavailable absolute `/Volumes/...` paths;
- MAGeCK commands are comments rather than an executable workflow;
- BAM demultiplexing, Bowtie/SAMtools/FASTX mapping and state classification are **Not found**;
- the final A/B.E poly-UMI and UMI-hopping generation step is **Not found**;
- no environment lock, tests or portable entry point is provided.

The paper states that primary/processed screen data are in GEO (`GSE262309`, batches `GSE262307` and `GSE262308`) and links the GitHub repository. Those external assets were not reacquired in this constrained Author-only recovery. Supplementary markdown and local source-data spreadsheets are **Not found** in the workspace.

### Bottom Line

CRISPR-StAR's main contribution is not a new statistical model but a better experimental comparison: active perturbation and inactive control are born inside the same post-bottleneck clone. That design converts clone-to-clone heterogeneity from a confounder into a matched background and makes high-resolution pooled screening feasible at representation levels where conventional active-versus-library analysis fails. The paper presents strong benchmark and validation evidence, while the released code snapshot only partially supports independent computational reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
