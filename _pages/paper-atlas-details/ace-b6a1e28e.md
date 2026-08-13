---
layout: default
permalink: /paper-atlas/ace-b6a1e28e/
title: "ACE"
nav: false
description: "ACE 的本质是把“一个抗体只能带少量金属离子”的限制，改写为“一个抗体携带一条可循环延伸、可分支、并能共价固定数百个金属 detector 的 DNA 支架”；它最有说服力的贡献是让原本低于质谱流式检测阈值的单细胞蛋白信号变得可量化，而公开代码只提供部分图形分析的审计线索，不能代表完整复现包。"
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
    <h1>ACE</h1>
    <p>Signal amplification by cyclic extension enables high-sensitivity single-cell mass cytometry</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/xiaokanglun/ACE" target="_blank" rel="noopener noreferrer" aria-label="Open code for ACE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ACE 方法详解：用循环延伸把一个抗体事件放大成数百个金属报告信号

### 1. 这篇论文要解决什么问题？

质谱流式（mass cytometry / CyTOF）用不同金属同位素标记抗体，因此可以在单细胞上同时测量约 50 种蛋白或蛋白修饰。但“通道多”不等于“灵敏度高”：常规抗体只能携带有限数量的金属离子，一个表位往往需要结合数百个金属标记抗体，才能超过仪器检测阈值。

这使许多生物学上关键、但丰度很低的分子难以可靠检测，例如：

- 转录因子 Zeb1、Snail/Slug；
- TCR 信号通路中的低丰度磷酸化位点；
- 组织切片中的低表达空间标志物。

ACE（Amplification by Cyclic Extension，循环延伸扩增）的核心问题可以表述为：

> 在不改变抗体识别对象、也不牺牲多重检测能力的前提下，如何让一次抗原–抗体结合产生数百个稳定的金属报告信号？

论文发表于 *Nature Biotechnology*（2025），主要依据见 `paper source/nature_html/paper.md:1-24`。

### 2. 为什么已有放大方法不够用？

| 方法 | 论文所述代表来源 | 对质谱流式的主要障碍 |
|---|---|---|
| TSA（酪胺信号放大） | *Journal of Immunological Methods*, 1992 | 酶促沉积容易产生非特异背景，而且难以高重多重化。 |
| 碱性磷酸酶放大 | *Analytical Chemistry*, 2018 | 同样存在背景和多重化限制。 |
| RCA（滚环扩增） | *PNAS*, 2000 | 抗体检测场景中容易出现非特异抗体背景；分子拥挤也会影响扩增效率。 |
| HCR（杂交链式反应） | *PNAS*, 2004 | 同时测量的蛋白表位数量通常有限。 |
| Immuno-SABER | *Nature Biotechnology*, 2019 | 组织成像中可进行多重放大，但悬浮细胞不能承受其严格清洗；非共价 DNA 双链还会在质谱流式高温汽化时解离。 |

ACE 的设计分别对应这些问题：使用短 9-mer 条形码减少长 DNA 的非特异结合；用原位循环延伸形成大量结合位点；用正交序列支持 30 多重检测；最后用 CNVK 光交联把检测链共价固定，避免汽化过程丢失金属报告物（`paper.md:21-24,30-44`）。

### 3. 最重要的直觉

常规质谱流式大致是：

```text
1 个蛋白表位
  → 1 个抗体结合事件
  → 抗体携带有限金属离子
  → 信号可能低于检测阈值
```

ACE 改成：

```text
1 个蛋白表位
  → 1 个带 DNA initiator 的抗体
  → 原位循环延伸出很长的 DNA concatemer
  → concatemer 上形成数百个 detector 结合位点
  → 每个 detector 携带金属聚合物
  → 一个抗体事件产生大量金属离子信号
```

因此，ACE 放大的不是抗体数量，也不是抗原数量，而是“每个已识别抗原能够携带的报告物数量”。

### 4. 分子元件与符号

| 元件 | 论文符号 | 作用 |
|---|---|---|
| initiator 条形码 | `a`，9-mer | 决定抗体/靶标身份。 |
| 抗体偶联 initiator | `TT-a`，11-mer | 固定在抗体上的延伸起点。 |
| 互补序列 | `a*` | 与 `a` 杂交。 |
| extender | `a*-T-a*`，19-mer | 提供模板，使已有 initiator 继续延伸出新的 `a` 重复。 |
| *Bst* DNA polymerase | — | 在 22 °C 延伸 initiator。 |
| CNVK | 3-cyanovinylcarbazole phosphoramidite | 经 365-nm UV 激活后，把 detector 与 concatemer 共价交联。 |
| detector | 带 `a*-T-a*` 的检测链 | 与重复的 `a` 位点杂交，并携带金属报告物。 |
| DTPA–Ln$^{3+}$ | 金属螯合聚合物 | 携带质谱流式可区分的镧系同位素。 |

单轮反应可简化为：

$$
\mathrm{TT\!-!a}
\xrightarrow[22\,^{\circ}\mathrm{C}]{\mathrm{a^*\!-!T\!-!a^*},\ Bst}
\mathrm{TT\!-!a\!-!A\!-!a\!-!A}
\xrightarrow[58\,^{\circ}\mathrm{C}]{\text{变性}}
\text{进入下一轮延伸}。
$$

不断重复后，一个抗体偶联位点上就形成数百个 `a-A` 重复单元（`paper.md:30-33`）。

### 5. ACE 从样本到信号的完整流程

```text
固定细胞 / 固定组织切片
        │
        ▼
用正交 initiator–抗体进行多靶标染色
        │
        ▼
交联抗体并洗去游离抗体
        │
        ▼
循环延伸：22 °C 杂交与聚合，58 °C 变性
        │
        ▼
每个抗体上得到线性 DNA concatemer
        │
        ├── 信号仍不足？
        │       └── 加 branching primer → UV 固定 → 再循环延伸
        ▼
加入金属标记 detector
        │
        ▼
CNVK + 365-nm UV，将 detector 共价固定
        │
        ▼
Helios 质谱流式 / Hyperion IMC 采集
        │
        ▼
FCS 或空间像素离子计数
        │
        ▼
arcsinh 变换、去条形码、门控/分割、UMAP/轨迹/网络分析
```

#### 5.1 抗体与短 initiator 偶联

5′-巯基化 initiator 经 SM(PEG)$_2$ 与抗体偶联；论文使用 5:1 的寡核苷酸:抗体摩尔比。短 9-mer 是一个重要设计：它既能作为正交地址，又比长 DNA 条形码更不容易带来非特异结合（`paper.md:24,213-216`）。

#### 5.2 线性循环延伸

悬浮细胞实验中，反应液包含 ThermoPol buffer、0.2 mM dA/C/TTP、1 μM extender 和 1,200 units ml$^{-1}$ *Bst* polymerase。每轮包括：

1. 22 °C、40 s：extender 与 initiator/新生 concatemer 杂交，*Bst* 完成延伸；
2. 58 °C、20 s：双链变性，暴露新增长链；
3. 重复下一轮。

除 Fig. 2 的 500-cycle 标定实验外，悬浮细胞通常使用 100 cycles，约 2 小时（`paper.md:225-228`）。

#### 5.3 分支放大

如果线性 ACE 仍不足以检测某个极低丰度靶标，可以让 branching primer 结合到主 concatemer，并先用 CNVK/UV 固定，然后再做 50 cycles 延伸。一次分支在测试中相对线性 ACE 增强约 9 倍；第二次分支再增加约 5 倍，使总增益超过 500 倍（`paper.md:64`；Supplementary Fig. S5）。

分支并非所有通道都必须使用。Fig. 4 中大部分 TCR 标志物采用线性 ACE，而 p-AKT(p-T308) 因信号过低，额外使用一次分支并获得约 15 倍提升。

#### 5.4 CNVK 光交联为什么是关键“隐藏步骤”？

只做 detector 杂交并不够。质谱流式会把单细胞液滴加热汽化，普通 DNA 双链会解离，金属 detector 因此从细胞上脱落。论文用 55 °C、1 min 的实验复现了超过 90% 的荧光信号损失。

CNVK 经 UV 激活后，在 detector 与互补链之间形成共价键，使复合物在加热和汽化中保持完整。Supplementary Fig. S1 的加热前后散点图直接显示了“无交联丢失、交联后恢复”的区别。

论文 Results 写的是短暂 1-s UV，而 Methods 给出 365 nm、5 s。复现实验应优先采用 Methods 的 5-s 操作值，并记录这一文本差异（`paper.md:44,219-228`）。

### 6. 多重化如何实现？

每个抗体使用不同的 9-mer `a`，并配置对应的 extender 和 detector。理想情况下，只有 `a` 与其 `a*` 发生有效反应。

作者测试了 33 个 initiator。Fig. 2h 的 33 × 33 矩阵以对角线为主，说明大多数序列能正确配对。四个超过 10% 的串扰组合位于相邻质量通道，提示一部分串扰来自质谱仪的 ±1 channel spillover，而不是 DNA 序列本身。

需要保留一个论文内部不一致：Results/Fig. 2 caption 报告平均串扰 1.02%，前文总结写 1.07%（`paper.md:24,58,70-73`）。因此更稳妥的结论是“平均约 1%，但存在少数需避开的高串扰配对”。

### 7. 采集后的计算分析

ACE 是实验测量技术，但论文的生物学结论仍依赖计算分析。

#### 7.1 共同预处理

悬浮质谱流式原始离子计数使用 cofactor 5 的反双曲正弦变换：

$$
\mathrm{data}=\operatorname{arcsinh}\left(\frac{\mathrm{dataraw}}{5}\right).
$$

论文在 `paper.md:252-261` 给出该公式；Fig. 3 和 Fig. 4 Rmd 分别在 `ACE/Fig.3/Fig.3.Rmd:79-85`、`ACE/Fig.4/Fig.4.Rmd:71-77` 直接实现。

#### 7.2 Fig. 2：扩增是否保持比例关系？

代码把 1、50、100、200、500 cycles 的 5 个 FCS 文件合并，去除常规抗体参考通道两端各 5% 的极端值，再按参考信号的 arcsinh 值分成 10 个等宽 bin。随后计算：

- 各 bin 的 ACE 中位数；
- 相对 bin 10 的比例；
- ACE 与常规抗体之间的 Pearson 相关系数。

直接代码证据：`ACE/Fig.2/Fig.2code.Rmd:29-135`。可视结果显示相关系数从 0.927 上升到最高 0.975，同时 ACE 动态范围扩大，支持“增强信号但基本保持丰度排序”。

#### 7.3 Fig. 3：EMT–MET 的状态与轨迹

Fig. 3 Rmd 的主要数据流是：

```text
12 个 FCS + marker/sample 字典
  → long-format 单细胞通道表
  → arcsinh(count/5)
  → 每个条件最多抽取 1,000 个细胞
  → 按 marker 的 0.1%/99.9% 分位缩放到 [0,1]
  → cell × marker 矩阵
  → UMAP + SCORPIUS
  → Zeb1/cyclin B1 分群与 marker 箱线图
```

作者用 CK14、E-cadherin、EpCAM、EGFR、vimentin、Zeb1 推断 SCORPIUS 轨迹，并用图中边界

$$
\mathrm{Cyclin\ B1}>\frac{7}{6}\,\mathrm{Zeb1}+1
$$

定义 Zeb1-low/cyclin-B1-high 候选群体。该群体在 MET 中表现为 vimentin 降低、E-cadherin 和 CK14 升高。

但这里存在明确的代码边界：论文 Methods 给出 UMAP `min_dist=0.4`，Rmd 使用 `0.6`；代码虽然声明 `rand_seed=1234`，却没有调用 `set.seed`；signed SCORPIUS 和 gate 的 subset 赋值也较脆弱。因此 Fig. 3 的总体分析路径是 **Partial**，不能把仓库脚本当作无修改即可复现的最终实现。

#### 7.4 Fig. 4–5：TCR 动态与 POF 信号积分

Fig. 4 Rmd 提供了线性、分支和无扩增组的密度图、fold-change 和 dynamic-range 分析。论文还使用 BP-R$^2$ 评估任意两个磷酸化位点的关系，强关系阈值为 8 个时间点平均值大于 0.775：

$$
\frac{1}{8}\sum_{t=1}^{8}\mathrm{BP\!-!R}^{2}_{ij,t}>0.775.
$$

由此得到 73 条强关系，但 BP-R$^2$ 代码在仓库中 **Not found**。

POF 分析先取所有处理条件和时间点中的最大平均信号的一半作为 HMP，再计算轨迹高于 HMP 的梯形积分。论文给出了方法定义，但 Fig. 5 代码 **Not found**（`paper.md:288-291`）。

#### 7.5 Fig. 6：空间 IMC

论文使用 Mesmer 做单细胞分割，用 CellProfiler 去除小于 30 pixels 的对象并计算细胞内平均离子计数，再用 UMAP 和 Phenograph（20 nearest neighbors）得到 18 个 cluster、归纳为 6 类肾组织区室（`paper.md:264-297`）。对应实现和原始 IMC 图像在仓库中 **Not found**。

### 8. 论文如何证明 ACE 有效？

| 任务 | 主要结果 |
|---|---|
| GFP 标定 | 500 cycles 约 13 倍信号、6 倍信噪比；主要增益发生在前 100 cycles。 |
| 分支扩增 | 测试配置中总增益超过 500 倍。 |
| 多重化 | 33 个 initiator，平均串扰约 1%，少数高串扰组合需避开。 |
| EMT–MET | 32-parameter panel 同时测量低丰度转录因子、表型和信号标志物。 |
| TCR 信号 | 30-parameter panel 平均约 17 倍、最高 41 倍增强；动态范围约提高 10 倍。 |
| 原代 T 细胞 | 相对常规方法，分支 ACE 使相关信号约提高 10 倍。 |
| POF | 区分强、中等和近乎无免疫抑制的 POF 样本。 |
| 肾组织 IMC | 20-antibody panel 解析 18 个 cluster 和 6 类主要组织区室。 |

### 9. 图像证据应该怎样理解？

- Fig. 2 是最强的定量对照：同一细胞中 ACE 与常规抗体保持高相关，同时 ACE 信号随 cycles 增加。
- Fig. 4c 最直观地说明“灵敏度带来新的可观测性”：无扩增 p-AKT 轨迹被噪声淹没，分支 ACE 后出现可解释的时间响应。
- Fig. 3、5、6 说明 ACE 可以支持新的生物学应用，但其结论更依赖 UMAP、轨迹、积分、聚类和有限样本，不能与 Fig. 2 的技术标定等量齐观。

更完整的逐图证据见 `figure_analysis.md`。

### 10. 代码与论文的一致性

总体 code–paper fidelity：**low**。

原因不是三个 Rmd 毫无价值，而是它们只覆盖部分 Fig. 2–4 绘图，并不是 ACE 技术或整篇论文的端到端实现。

#### 已直接验证的部分

- cofactor-5 arcsinh 变换：**Exact**；
- Fig. 2 cycle/bin/correlation 分析：**Exact**；
- Fig. 3 FCS → marker matrix 的主数据流：**Exact**；
- Fig. 4 amplification/dynamic-range 绘图：大部分 **Exact**。

#### 部分匹配或缺失

- Fig. 3 UMAP 参数和若干赋值逻辑：**Partial**；
- Fig. 4 p-AKT 最后一个 chunk 使用未定义的 `data_mean_amp`：**Partial / 无法从干净会话运行**；
- 33-sequence 串扰计算：**Not found**；
- BP-R$^2$、POF、IMC 分析：**Not found**；
- R 包版本锁定、runner、测试和执行入口：**Not found**。

CodeGraph 数据库为当前状态，但由于解析器不支持这三个 Rmd，索引为 0 files / 0 nodes；最终判断全部来自 Rmd 的直接行号，而不是图索引。

### 11. 局限性与复现注意事项

1. ACE 只能放大抗体已有的特异性，不能修复差抗体造成的高背景。
2. Triton X-100 通透化要求表面蛋白按兼容顺序预先染色。
3. 100–500 cycles 以及分支反应会增加实验时间与操作复杂度。
4. 正交性高但并非零串扰，DNA 配对和相邻质量通道都要纳入 panel 设计。
5. POF 只有 3 个样本，肾组织是聚焦示范，不能视为临床验证。
6. Nature Reporting Summary 说明未做随机化和盲法；质谱流式样本通过条形码后混池以降低批次差异，POF 显著性使用 3 个重复。
7. 公开仓库没有完整分析代码和锁定环境，端到端复现需要人工修复和重新实现缺失模块。

### 12. 一句话总结

ACE 的本质是把“一个抗体只能带少量金属离子”的限制，改写为“一个抗体携带一条可循环延伸、可分支、并能共价固定数百个金属 detector 的 DNA 支架”；它最有说服力的贡献是让原本低于质谱流式检测阈值的单细胞蛋白信号变得可量化，而公开代码只提供部分图形分析的审计线索，不能代表完整复现包。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ACE — summary

### What problem does the paper solve?

Mass cytometry can measure dozens of proteins per cell, but its detection threshold excludes many low-abundance transcription factors, receptors and phosphorylation sites. Conventional metal-labeled antibodies carry too few ions per binding event, so sensitivity—not multiplex capacity—is often the limiting factor.

The paper introduces **Amplification by Cyclic Extension (ACE)**, a DNA-based signal-amplification technology for suspension and imaging mass cytometry. An antibody-linked 9-mer initiator is repeatedly extended by *Bst* polymerase under 22 °C/58 °C thermal cycles, producing a long concatemer with hundreds of detector-binding sites. Metal-loaded detector oligonucleotides are then hybridized and covalently stabilized by CNVK-mediated UV photocrosslinking so they survive mass-cytometer vaporization (`paper source/nature_html/paper.md:24,30-44`).

### Why existing approaches were insufficient

- Tyramide signal amplification (*Journal of Immunological Methods*, 1992) and alkaline-phosphatase amplification (*Analytical Chemistry*, 2018) can introduce nonspecific signal and are difficult to multiplex.
- Rolling circle amplification (*PNAS*, 2000) can be multiplexed, but antibody-based implementations suffer from background binding and crowding-dependent efficiency.
- Hybridization chain reaction (*PNAS*, 2004) has limited protein-epitope multiplexing.
- Immuno-SABER (*Nature Biotechnology*, 2019) can amplify many tissue-imaging targets, but stringent washing is unsuitable for suspended cells and noncovalent DNA duplexes dissociate during hot mass-cytometry sample introduction (`paper.md:21`; references `:332-341`).

ACE addresses these constraints with short initiators, in situ cyclic extension, orthogonal barcode families and covalent detector stabilization.

### Method at a glance

```text
antigen
  → initiator-conjugated antibody staining
  → repeated extender hybridization / Bst extension / heat denaturation
  → linear DNA concatemer
  → optional branching amplification
  → metal-detector hybridization
  → CNVK + 365-nm UV crosslinking
  → mass cytometry or IMC
  → arcsinh(count/5) and experiment-specific single-cell analysis
```

Most suspension experiments used 100 one-minute cycles; the calibration series extended to 500 cycles. Branching adds new primer-bearing arms followed by additional cycling. Tissue IMC used 220-cycle blocks. The molecular protocol is described in `paper.md:213-246`; downstream ion-count processing uses

$$
\mathrm{data}=\operatorname{arcsinh}(\mathrm{dataraw}/5).
$$

### Main evaluations and results

#### GFP calibration and multiplex orthogonality

In GFP-expressing HEK293T cells, ACE retained high correlation with a conventional secondary-antibody reference while signal increased across 1–500 cycles (Pearson 0.927 initially, maximum 0.975). At 500 cycles, the paper reports about 13-fold signal amplification and sixfold signal-to-noise improvement. Primary and secondary branching produced stepwise gains reaching more than 500-fold over the unamplified signal in the tested configuration (`paper.md:50-64`; Figs. 2 and S3–S5).

Thirty-three initiators were pooled to test multiplexing. The Fig. 2 matrix is strongly diagonal; four high-crosstalk pairs were associated with adjacent mass channels. The detailed Results report 1.02% mean crosstalk, while the introductory summary reports 1.07%, an internal discrepancy (`paper.md:24,58,70-73`).

#### EMT–MET profiling

A 32-parameter panel measured low-abundance transcription factors, phenotypic markers and signaling proteins across 11 Py2T timepoints. UMAP and SCORPIUS linked Zeb1/vimentin gain to EMT and their reversal to MET. A Zeb1-low/cyclin-B1-high population showed lower vimentin and higher E-cadherin/CK14, supporting the proposed MET hallmark (`paper.md:76-93`; Fig. 3).

#### T-cell signaling

A 30-parameter panel measured Jurkat TCR signaling over one hour. ACE gave an average 17-fold and maximum 41-fold gain across markers, a tenfold dynamic-range increase, and an extra 15-fold p-AKT(p-T308) gain with branching. BP-R² analysis selected 73 strong signaling relationships; branching exposed a p-AKT trajectory that was dominated by noise without amplification (`paper.md:96-119`; Figs. 4, S7 and S8).

#### POF perturbation and tissue imaging

ACE distinguished postoperative drainage fluids with strong, moderate and negligible suppression of T-cell proliferation/signaling. POF1 and POF2 produced lower and more transient TCR responses than control/POF3, although only three POF samples were studied (`paper.md:125-142`; Fig. 5 and S9).

For spatial profiling, a 20-antibody ACE–IMC panel analyzed a polycystic-kidney cortex. Linear amplification was applied to all markers and branching to ten low-abundance targets. Mesmer/CellProfiler, UMAP and Phenograph resolved 18 clusters spanning six broad renal compartments and exposed heterogeneous nestin expression in glomerular cells (`paper.md:145-165,264-297`; Fig. 6 and S10).

### What the figures establish

- Fig. 2 provides the strongest controlled evidence: cycle-dependent gain, stable proportionality, branching enhancement and a mostly diagonal multiplex crosstalk matrix.
- Fig. 4 shows the measurement value of sensitivity directly: branching reveals a time-dependent p-AKT response that is not visible without amplification.
- Figs. 3, 5 and 6 demonstrate biological usefulness across cell-state, perturbation and spatial settings, but depend more on downstream analysis choices and limited application samples.

See `figure_analysis.md` for panel-by-panel image evidence.

### Reproducibility and code–paper match

**Reproducibility: 3/5.** The paper provides detailed wet-lab protocols, supplementary figures, public raw data at Cytobank project 1561 and a GitHub snapshot. The Nature Reporting Summary identifies R 4.0.5 and states that findings were reproduced, no analysis data were excluded, three replicates supported POF significance, and randomization/blinding were not performed (`supplementary/41587_2024_2316_MOESM2_ESM.pdf`, pp. 1–2).

The local repository contains 41 FCS files, metadata CSVs and three Rmd scripts for selected Fig. 2–4 analyses. It does **not** implement the ACE assay, and it omits BP-R², Fig. 5 POF and Fig. 6 IMC analysis code. There is no environment lockfile, runner or test. The code also contains a Fig. 3 UMAP mismatch (`min_dist=0.6` in source versus `0.4` in Methods), fragile subset assignments and an undefined object in the Fig. 4 p-AKT chunk. Overall code–paper fidelity is therefore **low**, despite several exact local matches for arcsinh preprocessing and plot construction. See `doc_code.md`.

### Limitations

- ACE cannot improve nonspecific antibody binding; antibody quality and availability remain hard limits.
- Triton X-100 permeabilization constrains surface-protein staining order.
- Long cycling and branching increase experimental time and complexity.
- Crosstalk is low but nonzero and must be considered jointly with mass-channel spillover.
- The POF and kidney demonstrations are small, focused applications rather than clinical validation cohorts.
- Several analysis components are unavailable as author code, so complete end-to-end reproduction requires reimplementation.

### Bottom line

ACE is best understood as a sensitivity layer for mass cytometry: it preserves antibody-defined target identity while replacing one low-yield metal-labeling event with a covalently stabilized, extensible DNA scaffold carrying many metal reporters. The paper convincingly demonstrates large signal gains and >30-plex operation, then uses that sensitivity to measure transcription-factor dynamics, TCR signaling and spatial kidney markers that are difficult to quantify conventionally. Its experimental contribution is substantially stronger than its public computational reproducibility package.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
