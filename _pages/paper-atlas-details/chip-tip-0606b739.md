---
layout: default
permalink: /paper-atlas/chip-tip-0606b739/
title: "Chip-Tip"
nav: false
wide: true
description: "Chip-Tip 不是一个数学模型，而是一套端到端的单细胞蛋白质组技术：它用 cellenONE 挑选并分配单个细胞，在 proteoCHIP EVO 96 中以 300 nl 体积完成油层覆盖的一锅式裂解和酶切，再把芯片直接倒扣到 Evotip 上离心转移，最后通过 Evosep One 快速液相、Orbitrap Astral 和窄窗口 DIA（nDIA）完成无标记定量。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Chip-Tip</h1>
    <p>Enhanced sensitivity and scalability with a Chip-Tip workflow enables deep single-cell proteomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Chip-Tip 方法详解：把单细胞样本损失压到最低的深度蛋白质组工作流

### 一句话理解

Chip-Tip 不是一个数学模型，而是一套端到端的单细胞蛋白质组技术：它用 cellenONE 挑选并分配单个细胞，在 proteoCHIP EVO 96 中以 300 nl 体积完成油层覆盖的一锅式裂解和酶切，再把芯片直接倒扣到 Evotip 上离心转移，最后通过 Evosep One 快速液相、Orbitrap Astral 和窄窗口 DIA（nDIA）完成无标记定量。它的核心价值是少用液体、少暴露表面、少做移液，同时把制样并行化，从而在单个 HeLa 细胞中达到中位数 5,204 个蛋白和 41,700 条肽段，并把检测通量推进到每天 120 个样本。

### 1. 它要解决什么问题？

单细胞蛋白质组（single-cell proteomics, SCP）直接测量蛋白和翻译后修饰，比 mRNA 更接近细胞的执行层。但单个细胞的蛋白总量极低，任何一个普通实验步骤都会变成主要误差源：

- 蛋白或肽段吸附在管壁、孔板和枪头表面；
- 纳升级液滴蒸发，导致酶和缓冲液浓度漂移；
- 多次移液造成不可逆损失和孔间差异；
- LC–MS 串行采集限制通量；
- 数据库搜索中的跨运行匹配会提高鉴定数，但也可能改变误差结构。

论文把当时常见的单细胞深度概括为每个细胞约 1,000–2,000 个蛋白组。Chip-Tip 的目标不是只优化某一个搜索算法，而是同时改造“制样—转移—色谱—质谱—搜索—误差验证”整条链路。

### 2. 与已有方法相比，它新在哪里？

论文引用的相关路线包括：

- Li 等人在 *Analytical Chemistry*（2018）提出的纳升级油–气液滴芯片；
- SCoPE-MS（*Genome Biology*, 2018）代表的同位素标记多重化路线；
- Matzinger 等人的无标记一锅式方法（*Analytical Chemistry*, 2023）；
- plexDIA（*Nature Biotechnology*, 2023）和 mDIA（*Molecular Systems Biology*, 2023）代表的非同位素/二甲基多重 DIA；
- One-Tip（*Nature Communications*, 2024）代表的极少量细胞直接处理路线。

Chip-Tip 的差异化创新是把多个已知原则做成一个高度匹配的物理接口：

1. **300 nl 一锅式反应**：尽量提高样本浓度，降低接触面积和稀释损失。
2. **己烷十六烷油层覆盖**：在 50 °C 酶切时阻止水相蒸发。
3. **96 位并行芯片**：制样可以并行，而不是逐管处理。
4. **芯片直接倒扣 Evotip**：靠离心完成转移和净化，避免再吸一次、再打一次。
5. **Whisper 快速 LC + nDIA**：在灵敏度和每天样本数之间寻找可用平衡。
6. **载体蛋白组搜索与 entrapment 验证并行**：既利用匹配提高深度，也单独估计经验错误率。

### 3. 输入、输出与关键符号

#### 输入

- cellenONE 根据形态学选择的单个细胞；
- proteoCHIP EVO 96、己烷十六烷、DDM、TEAB、trypsin 和 Lys-C；
- Evotip 与 Evosep One；
- Orbitrap Astral 产生的 nDIA 原始谱图；
- UniProt 2022 人类数据库（20,588 条序列）和 246 条常见污染物序列；
- 可选的 20-cell 或 1-ng 高输入匹配样本，用作搜索上下文中的“carrier proteome”。

#### 输出

- 每个细胞的肽段、蛋白组鉴定和丰度；
- 磷酸化位点及糖相关诊断离子证据；
- 药物处理、干细胞分化等下游单细胞比较结果。

#### 论文保留的采集记号

`4Th6ms` 表示 DIA 隔离窗口宽度为 4 Th、最大离子注入时间为 6 ms。论文比较了：

| 方法 | 窗口 | 最大注入时间 | 单细胞中位蛋白数 |
|---|---:|---:|---:|
| `2Th3ms` | 2 Th | 3 ms | 5,093 |
| `4Th6ms` | 4 Th | 6 ms | 5,204 |
| `8Th12ms` | 8 Th | 12 ms | 4,449 |
| `16Th24ms` | 16 Th | 24 ms | 3,782 |

论文没有需要复现的核心数学公式；关键“参数”主要是体积、温度、时间、窗口宽度、注入时间、质量范围和搜索阈值。

### 4. 从单个细胞到蛋白定量的完整流程

```text
细胞悬液
  |
  v
cellenONE 成像与形态筛选
  |  Chip-Tip: 直径 22–30 µm，elongation <= 1.6
  v
单细胞落入 proteoCHIP EVO 96
  |  300 nl master mix，己烷十六烷覆盖
  |  50 °C、85% RH、1.5 h
  v
同孔裂解 + trypsin/Lys-C 酶切
  |
  v
加甲酸，冷却凝固油层
  |
  v
芯片倒扣到 Evotips，800 x g 离心
  |
  v
肽段捕获、清洗
  |
  v
Evosep Whisper LC：40/80/120 SPD
  |
  v
Orbitrap Astral nDIA
  |
  v
Spectronaut directDIA+ / DIA-NN library-free
  |  可选 carrier/MBR + mimic entrapment
  v
蛋白/肽段定量、PTM 与生物学分析
```

#### 4.1 单细胞选择

HeLa 细胞在约 80% 汇合度时收集，用 PBS 洗三次，再以约 200 cells/µl 重悬。Chip-Tip 路线中，cellenONE 选择直径 22–30 µm、最大 elongation factor 1.6 的细胞。排序器标记为多细胞的事件会被排除。

这意味着论文中的“单细胞”是经过成像和形态门控的单细胞，不是悬液中无条件抽取的全部事件。

#### 4.2 油层覆盖的 300 nl 一锅式反应

每个芯片孔先人工加入 2 µl 己烷十六烷，并在 8 °C 冷却使其凝固。随后加入 300 nl master mix：

- 0.2% DDM；
- 100 mM TEAB；
- 20 ng/µl trypsin；
- 10 ng/µl Lys-C。

单个细胞进入孔中后，芯片在 50 °C、85% 相对湿度下孵育 1.5 h。己烷十六烷熔点为 18.2 °C，因此加热时会覆盖水相，限制蒸发并保持酶和试剂浓度。反应结束后降到 20 °C。

**为什么可能更灵敏？** 论文的解释是：纳升级体积让样本更集中，油层减少蒸发，一锅式反应减少器壁和移液损失。这个机制合理，但论文没有给出“单个细胞理论总肽量—最终回收量”的绝对回收率，也没有逐项拆解每个部件贡献了多少增益。

#### 4.3 芯片到 Evotip 的直接转移

反应后每孔人工加入 4 µl 0.1% 甲酸并冷却，使油层重新凝固。Evotip 预处理后先加入 15 µl 0.1% 甲酸；proteoCHIP 随即倒扣到 Evotip 上，在 4 °C、800×g 下离心 20 s。

之后：

1. 800×g 离心 60 s，让肽段充分结合；
2. 用 20 µl Solvent A 清洗，再离心 60 s；
3. 加 100 µl Solvent A，离心 10 s；
4. 进入 LC–MS/MS。

这一步的隐含技巧是**让芯片孔和固相萃取尖端直接对接**，不再用移液器转移微量消化液。

#### 4.4 LC 通量设计

40SPD 使用 15 cm × 75 µm 色谱柱；80SPD 和 120SPD 使用 5 cm × 75 µm 短柱。因此三种通量不仅梯度时间不同，柱长也不同，不能把性能变化只归因于“速度”。

主图直接显示：

- 40SPD：中位 5,204 个蛋白；
- 80SPD：中位 4,503 个蛋白；
- 120SPD：中位 4,567 个蛋白。

这说明加速后存在一定深度损失，但每天 120 个样本时仍能维持 >4,500 个蛋白。制样可在 96 孔并行完成，真正剩下的瓶颈是质谱逐个样本采集，论文也明确把 120SPD 视为当前上限。

#### 4.5 nDIA 参数为什么要平衡？

更窄的 DIA 窗口通常降低共碎裂复杂度，但每个循环需要覆盖的窗口更多；更长注入时间能积累更多离子，却会牺牲循环速度并可能积累化学噪声。论文通过实验比较而不是公式优化，发现 `4Th6ms` 在单细胞中最好。

作者把 `8Th12ms` 和 `16Th24ms` 的下降解释为更高化学噪声。这是论文解释，不是单独完成的因果噪声实验。

### 5. “Carrier proteome”到底是什么？

这里的 carrier 不是把高输入样本和单细胞在同一个 TMT 通道中混合。它指的是**数据库搜索上下文**：

- Spectronaut directDIA+ 把单细胞文件和匹配的 20-cell/1-ng 文件一起搜索；
- DIA-NN 使用 MBR，把高输入运行中的证据用于跨运行匹配。

主图显示，在 Spectronaut `4Th6ms` 中，无 carrier 时为 4,024 个蛋白，有 carrier 时为 5,204 个。随着参与联合搜索的单细胞文件增加，鉴定数也逐步上升；加入高输入文件时增幅最大。

但“鉴定数增加”不能自动解释为每个单细胞都独立产生了同等强度的证据。因此论文又做了两个校验：

1. **跨软件/跨细胞比较**：两个单细胞之间，DIA-NN 定量相关 *R*=0.89，Spectronaut 为 *R*=0.91；同一细胞跨软件只有 *R*=0.83。
2. **Entrapment 错误率实验**：在人类数据库中追加打乱序列的 mimic 数据库，观察错误命中。

### 6. 经验 FDR 验证

论文使用保留氨基酸组成的 shuffled-human mimic 数据库，并按同样参数分别搜索 Spectronaut 和 DIA-NN。在软件名义蛋白 FDR=0.01 时，校正 mimic 数据库大小后，经验蛋白 FDR 约为：

- Spectronaut：3%；
- DIA-NN：1%。

Extended Data Fig. 4 中，单细胞的 mimic/target 数分别为 51/2,762（Spectronaut）和 24/3,034（DIA-NN）。这说明高鉴定深度有一定错误控制证据，同时也提醒：软件设置的 1% 不一定等于实际 1%。

本地材料中没有找到 mimic 大小校正的完整公式，因此不能从主文独立重算这个 3% 和 1%。

### 7. 不富集也能看 PTM，能看到什么程度？

Chip-Tip 数据的肽段深度足够高，作者直接把 Ser/Thr/Tyr 磷酸化设为可变修饰，并使用 `PTM.SiteProbability >= 0.75` 过滤。单细胞中位数为：

- phospho-Ser：120；
- phospho-Thr：28；
- phospho-Tyr：13。

此外，作者用 XIC 检查：

- phospho-Tyr immonium ion：约 *m/z* 216.043；
- HexNAc oxonium ion：*m/z* 204.087；
- NeuAc：*m/z* 274.092；
- Hex-HexNAc：*m/z* 366.139。

**证据边界很重要：** 磷酸位点搜索给出了位点概率过滤；糖相关 oxonium ion 只能说明谱图里存在相应糖碎片，不能据此确定是哪条肽、哪个氨基酸位点发生了糖基化。论文也明确承认当前搜索算法仍难以精确鉴定修饰肽。

### 8. 两个生物学应用

#### 8.1 5-FU 处理的 HCT116 球体

每个球体由 7,000 个细胞形成，培养 72 h，使用 2 µM 5-FU 处理 24 h，再用专用球体解离缓冲液震荡解离。80SPD 单细胞分析得到总计 >2,500 个蛋白。图中可见处理组球体更快失去完整性，并出现 TYMP 上调、NME1 下调，以及核苷酸代谢和中间丝相关 GO 改变。

这些结果与 5-FU 的已知代谢和结构效应一致，但属于机制线索。形态学实验只做了一次，且专用缓冲液的成分未公开，因此不能把图中差异视为充分重复的解离性能验证。

#### 8.2 hiPSC 向胚状体（EB）分化

hi12 细胞在 LN-521 上培养，用 TrypLE Express 解离，在含 10 µM Y-27632 的低黏附悬浮条件下形成 EB；一周后铺到明胶包被皿，再培养一周并解离成单细胞。

结果包括：

- hiPSC 最多约 4,700 个蛋白；
- 大型 EB 细胞最多约 6,200 个蛋白；
- PCA 清楚分离 hiPSC 和 EB，同时显示 EB 内部高度异质；
- hiPSC 中 OCT4、SOX2 更高；
- EB 中出现 GATA4（内胚层）、HAND1（中胚层）和 MAP2（外胚层）的细胞间差异。

需要注意两个混杂因素：一是 Extended Data Fig. 7 直接显示 EB 细胞比 HeLa 大，更高蛋白数可能部分来自更大的物质量；二是缺失值通过 `imp4p::impute.pa` 从数据分布的 2.5% 低分位随机抽样填补，本地没有脚本和随机种子，PCA、聚类和显著性结果无法逐步复算。

### 9. 论文真正证明了什么？

#### 主文和图像直接支持

- 96 位纳升级并行制样和芯片到 Evotip 的直接转移确实构成一条连贯工作流；
- 主 Chip-Tip 配置在单 HeLa 细胞中达到中位 5,204 个蛋白、41,700 条肽段；
- 80/120SPD 加速方法仍保持 >4,500 个蛋白；
- carrier/MBR 会显著改变鉴定深度，entrapment 可用于估计经验错误率；
- 深度足以支持无富集磷酸位点分析、糖诊断离子筛查和复杂生物样本分群。

#### 合理解释，但不是直接测量

- “接近无损”来自设计逻辑和最终深度，不是绝对回收率实验；
- 油层、体积、芯片材料、直接转移、LC 和 Astral 各自贡献多少，没有逐项消融；
- 更长注入时间导致化学噪声增加，是作者解释而非独立因果测试。

#### 用于提出假设

- 5-FU 影响嘌呤/嘧啶代谢和细胞骨架的具体链路；
- EB 不同细胞中三胚层标志物和功能通路的组合；
- SBDS 与早期分化状态的关系。

这些都适合后续验证，但不能仅凭当前单细胞相关性分析下因果结论。

### 10. 复现时缺少什么？

- proteoCHIP 的精确孔几何和制造参数；
- 聚丙烯与 Teflon 材料的定量对比；
- 专用球体解离缓冲液配方；
- 完整 Evosep 梯度表、Solvent A 成分和所有 vendor conditioning 细节；
- Spectronaut/DIA-NN 的本地参数导出文件；
- mimic FDR 校正公式；
- Fig. 5–6 的脚本、完整软件版本、随机种子和全部重复结构；
- 公开分析代码仓库。

论文公开了原始 MS 数据编号 PXD049211、PXD049181 和 PXD054944，也链接了 source data 与 Supplementary Data 1，但本 Author 阶段没有下载或重跑这些数据。因此，当前文档可以帮助理解和设计复现实验，却不能声称已经独立复现。

### 11. 最实用的学习结论

Chip-Tip 的方法学价值不只是“换了一个更灵敏的质谱”。它展示了单细胞技术里一个普遍原则：当输入逼近检测极限时，样本处理接口本身就是算法的一部分。反应体积、蒸发控制、材料表面、转移次数、色谱速度、DIA 窗口和搜索上下文必须作为一个系统联合优化；同时，越依赖跨运行匹配提高深度，就越需要 blank、跨软件一致性和 entrapment 这样的独立误差检查。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Chip-Tip

### In one paragraph

Chip-Tip is a label-free single-cell proteomics technology that combines cellenONE sorting, oil-covered 300-nl one-pot lysis/digestion in a 96-position proteoCHIP, direct centrifugation transfer to Evotips, rapid Evosep LC and narrow-window DIA on an Orbitrap Astral. The best tested Evosep/Astral setting (`4Th6ms`) identified a median 5,204 proteins and 41,700 peptides in single HeLa cells, while faster 80- and 120-sample-per-day methods retained >4,500 proteins. The workflow also enabled phosphosite and glycan-diagnostic-ion analysis without enrichment and resolved drug-treated spheroids and hiPSC differentiation. These are paper- and figure-supported system results; no code repository or local supplementary parameter bundle was available for independent implementation verification.

### Problem and prior limitations

Single-cell proteomics measures functional molecules and post-translational modifications that mRNA cannot directly capture, but extremely small input makes peptide loss, evaporation, contamination, sequence depth, throughput and reproducibility dominant concerns. The paper describes then-current workflows as typically identifying roughly 1,000–2,000 protein groups per cell, with peptide adsorption and manipulation losses remaining major constraints.

Relevant predecessors cited by the paper include the nanoliter oil-air-droplet chip of Li et al. (*Analytical Chemistry*, 2018), the label-free one-pot workflow of Matzinger et al. (*Analytical Chemistry*, 2023), and One-Tip (*Nature Communications*, 2024). Multiplexed alternatives such as SCoPE-MS (*Genome Biology*, 2018), plexDIA (*Nature Biotechnology*, 2023) and mDIA (*Molecular Systems Biology*, 2023) improve throughput but introduce labeling or reference-channel considerations. Chip-Tip instead pursues a nearly lossless, high-depth LFQ route in which each cell is acquired separately.

### What is new

The key engineering idea is to reduce liquid handling and surface exposure across the full preparation-to-LC handoff:

```text
cellenONE-selected cell
  -> 300-nl DDM/TEAB/trypsin/Lys-C reaction under hexadecane
  -> 96-well parallel incubation
  -> invert chip directly onto Evotips and centrifuge
  -> Evosep Whisper LC (40/80/120SPD)
  -> Orbitrap Astral nDIA
  -> library-free Spectronaut or DIA-NN analysis
```

The hexadecane layer limits evaporation during the 50 °C digestion, and the chip-to-tip inversion avoids an extra pipetting transfer. The system then uses short LC gradients and nDIA window/injection-time tuning to balance sensitivity and throughput. A separate low-bind plate/Vanquish Neo–FAIMS route reached still greater depth but omits the proteoCHIP-to-Evotip cleanup and should be treated as an alternative configuration, not the same component chain.

### Evaluation and main results

#### Analytical depth

- Main Chip-Tip benchmark: median 5,204 proteins and 41,700 peptides in single HeLa cells with `4Th6ms`; some preparations exceeded 6,000 proteins.
- Twenty-cell samples exceeded 7,000 proteins and reached a median 98,054 peptides; median sequence coverage increased from 12.9% in single cells to 25% in 20-cell samples.
- The protein abundance range spans several orders of magnitude and includes proteins from all major subcellular localizations, including >200 plasma-membrane proteins.

#### Throughput and blanks

- Evosep medians were 5,204 proteins at 40SPD, 4,503 at 80SPD and 4,567 at 120SPD in the displayed benchmark.
- Matched blanks yielded far fewer identifications (242 and 121 in the displayed 40SPD and 80SPD controls), supporting low—but not zero—background.
- The separate Vanquish Neo–FAIMS workflow reported a median 6,556 protein groups and 42,821 peptides across 80 single cells; the paper flags the lack of cleanup as a possible long-term robustness concern.

#### Search strategy and error control

Including matched higher-input “carrier proteome” files in Spectronaut directDIA+ or DIA-NN MBR increases single-cell identifications. For Spectronaut `4Th6ms`, the displayed median rises from 4,024 without carrier to 5,204 with carrier. Quantitative correlations are high within tool across two cells (*R*=0.89 DIA-NN; *R*=0.91 Spectronaut) but lower across tools for the same cell (*R*=0.83), showing that software choice materially affects results.

Using a shuffled-human mimic entrapment database and nominal 1% protein-level FDR, the paper estimates corrected empirical protein FDR at about 3% in Spectronaut and 1% in DIA-NN. This makes the identification gain more credible while also showing that nominal and empirical error can differ.

#### PTMs and biological applications

- Without phosphopeptide enrichment, single cells yielded medians of 120 phospho-Ser, 28 phospho-Thr and 13 phospho-Tyr sites, with a `PTM.SiteProbability ≥ 0.75` filter.
- Diagnostic immonium/oxonium-ion traces support widespread phosphorylation and glycan-related fragments, but do not localize glycosylation to exact peptides/sites.
- In 5-FU-treated HCT116 spheroids, >2,500 proteins were identified and the data showed TYMP/NME1 and nucleotide/structural changes consistent with drug response; the displayed morphology experiment was performed once.
- In hiPSC/embryoid-body analysis, the workflow quantified up to 4,700 proteins in hiPSCs and 6,200 in large EB cells, separated the populations in PCA and detected OCT4, SOX2 and lineage markers GATA4, HAND1 and MAP2.

### What the study establishes—and what it does not

**Established by the paper and inspected figures:** Chip-Tip is a deeply sensitive, scalable LFQ-SCP workflow; the system reaches >5,000 median proteins in the best main benchmark, can operate at 120SPD, benefits from carefully evaluated search context and supports unusually deep PTM/biological analyses.

**Interpretation:** minimizing evaporation, adsorption and transfer steps plausibly drives much of the gain, but no component-by-component ablation or absolute peptide-recovery measurement attributes effect sizes. Wider/longer nDIA settings are hypothesized to suffer more chemical noise, but that mechanism is not directly isolated.

**Hypothesis-generating outputs:** pathway changes in 5-FU spheroids and heterogeneous lineage programs in EB cells are biologically coherent starting points, not causal validation of specific mechanisms.

### Reproducibility and limitations

**Reproducibility assessment: 3/5.** The paper gives substantial wet-lab, LC–MS and search-method detail, visually reports blank and entrapment controls, and deposits raw MS data in ProteomeXchange/PRIDE/iProX: PXD049211, PXD049181 and PXD054944. Source data and supplementary parameter/log archives are linked by the article.

However, this acquired workspace contains no code repository and no supplementary Markdown. `Not found` after searching the full main paper and all local figures: exact chip geometry/manufacturing, proprietary spheroid-buffer composition, full gradient/conditioning recipes, local Spectronaut/DIA-NN exports, empirical-FDR correction formula, analysis scripts, random seeds and complete replicate structure for several experiments. The hiPSC/EB analysis uses low-quantile random imputation, so scripts and seeds matter. No raw data or settings were downloaded or rerun in this Author phase.

The main scientific caveats are the remaining 120SPD MS bottleneck, incomplete quantitative validity across the full reported dynamic range, sensitivity to chip material/volume, search-context dependence, larger EB cell size as a depth confounder, and limited replication of the spheroid morphology demonstration.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
