---
layout: default
permalink: /paper-atlas/metcell-8ef2454c/
title: "MetCell"
nav: false
description: "MetCell 的核心不是把 600 个细胞平均成一个“虚拟细胞”，而是先把多个细胞中位置一致的弱信号叠加起来，建立一张可靠的峰坐标表；随后回到每个原始细胞，只在这些已知坐标附近提取强度。这样既利用群体信息提高检出率，又保留每个细胞自己的代谢丰度。 论文把这一计算策略与离子淌度分离、选择性离子积累和靶向单细胞 MS2 结合，形成 ion mobility-resolved mass cytometry 平台。"
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
      <span>Nature Methods · 2026</span>
    </div>
    <h1>MetCell</h1>
    <p>Deep-coverage single-cell metabolomics enabled by ion mobility-resolved mass cytometry</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/ZhuMetLab/MetCell" target="_blank" rel="noopener noreferrer" aria-label="Open code for MetCell">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MetCell 方法详解：先用“细胞叠加”看清峰，再回到单细胞定量

### 一句话理解

MetCell 的核心不是把 600 个细胞平均成一个“虚拟细胞”，而是先把多个细胞中位置一致的弱信号叠加起来，建立一张可靠的峰坐标表；随后回到每个原始细胞，只在这些已知坐标附近提取强度。这样既利用群体信息提高检出率，又保留每个细胞自己的代谢丰度。

论文把这一计算策略与离子淌度分离、选择性离子积累和靶向单细胞 MS2 结合，形成 ion mobility-resolved mass cytometry 平台。

### 1. 论文要解决什么问题？

质谱流式单细胞代谢组学具有较高通量，但面临四个相互关联的问题：

1. **灵敏度不足**：单细胞代谢物常处于 amol 量级，而单个细胞的采集时间约为 0.1 s。
2. **峰检测不稳定**：低 SNR 和技术噪声会造成大量随机缺失值。
3. **代谢物覆盖有限**：传统方法通常只能得到几十到几百个候选代谢物。
4. **注释置信度不足**：短采集时间往往只够获得 MS1；许多研究的 MS2 来自 bulk 样品，而不是被测单细胞。

论文补充表 3 给出了直观对比：SpaceM（*Nature Methods*, 2021）报告 88 个候选、1 个标准品确认代谢物；Nunes 等的 CCS 方法（*Nature Methods*, 2024）报告 112 个候选但没有 MS2；Qin 等（*Nature Communications*, 2024）报告 348 个候选、6 个标准品确认代谢物。MetCell 平台希望同时提高灵敏度、稳定性、覆盖度和注释可信度。

### 2. 整个平台由哪些部分组成？

```text
活细胞悬液
   |
   v
压力驱动的单细胞连续进样
   |
   v
电喷雾离子化 -> TIMS 离子积累与淌度分离 -> 多维质谱检测
   |
   v
连续 IM-MS 数据帧（m/z × mobility × intensity）
   |
   v
MetCell：
  1) 单细胞帧识别
  2) 细胞叠加
  3) EIM 峰检测
  4) 回到每个细胞做靶向定量
  5) 电荷/同位素/MS1+CCS 候选匹配
   |
   v
靶向 PRM-PASEF MS2 + 共识谱 + 标准品/公共库/SIRIUS
   |
   v
Level 1-4 最终代谢物注释
```

这里要区分两个“MetCell”含义：论文常用它指完整数据分析流程；公开 GitHub R 包的可执行主流程则止于 MS1+CCS 候选匹配。靶向 MS2、共识谱、四级置信度和最终综合打分由论文与补充材料描述，但在当前代码快照中没有完整实现。

### 3. 为什么需要离子淌度？

离子淌度（IM）在几十毫秒内按离子的大小、形状和电荷相关特征进行气相分离，并提供碰撞截面 CCS。它在本平台中有三重作用：

- 与单细胞短脉冲采集时间匹配，保持较高占空比；
- 在积累阶段通过参数调整偏向低质量代谢物，减少高质量细胞组分的干扰；
- 为每个峰增加 mobility/CCS 维度，帮助峰检测、区分干扰物和减少候选代谢物数量。

选择性离子积累把 TIMS accumulation/ramping time 从 100 ms 缩短为 50 ms，并调整电压和传输参数。Fig. 1 显示 HepG2 中 *m/z* < 200 Da 离子的相对比例提高约 12 倍，*m/z* < 400 Da 提高约 4 倍；部分代谢物灵敏度提高到约 20 倍。这是仪器采集策略，不是 R 代码中的后处理。

### 4. 第一步：识别哪些 IM–MS 帧对应单细胞

连续原始数据由许多 IM–MS frame 组成。每个 frame 内有 489 个固定 mobility 的 MS scan。MetCell 选择一个细胞标志离子，例如 PC(34:1)，在每个 frame 中对指定的 *m/z* 和 mobility 窗口积分，得到随时间变化的 marker trace。

然后它做三件事：

1. 寻找 marker trace 的局部峰；
2. 要求峰强度高于下限，避免把噪声当细胞；
3. 要求峰强度低于上限，减少双细胞或异常宽峰。

论文示例参数包括 marker *m/z*=760.5845、mobility=1.402 V s cm$^{-2}$、20 ppm、mobility window 0.05 V s cm$^{-2}$ 和五点峰宽。代码实现位于 `MetCell/R/Functions-CellSuperposition.R:153-207`，另有多 marker 版本。

高速相机提供了独立验证：88 个可见事件中 83 个是单细胞（94.3%）；尖锐质谱脉冲通常对应单细胞，较宽脉冲更可能对应 doublet。

### 5. 第二步：细胞叠加为什么能提高 SNR？

假设某个真实代谢物在不同细胞中都出现在相近的 *m/z* 和 mobility 位置。虽然单个细胞里的信号很弱，但多个细胞对齐后，这个信号会在同一位置累加。随机噪声的位置不稳定，叠加后不容易形成同样尖锐的峰。

如果信号近似线性累加、噪声近似独立，SNR 常随细胞数 $N$ 的平方根增长。论文对 acetylcarnitine 的拟合为：

$$\mathrm{SNR}=13.7+6.04\sqrt{N}, \qquad R^2=0.96.$$

单细胞的 SNR 为 3.3，叠加 600 个细胞后达到 157.6；100 个代谢离子的中位 SNR 增益为 33 倍。

#### 代码实际怎样叠加？

默认选取前 600 个单细胞 frame：

1. 按 scan index 把所有细胞对齐；
2. 对每个 mobility scan，把所有细胞的谱合并；
3. 从当前强度最高的未分配离子开始，在 20 ppm 范围内建立 m/z 组；
4. 把组内强度求和，并计算强度加权平均 m/z；
5. 清除已使用的数据点，重复直到该 scan 处理完；
6. 将 489 个聚合谱重新组合成一个 cell superposition frame。

对于离子组 $G$：

$$I_G=\sum_{j\in G}I_j,$$

$$
(m/z)_G=\frac{\sum_{j\in G}I_j(m/z)_j}{\sum_{j\in G}I_j}.
$$

直接源码为 `MetCell/R/Functions-CellSuperposition.R:299-375`。

### 6. 第三步：从三维 superposition frame 中检测峰

#### 6.1 bottom-up 组装 EIM

MetCell 从整个 superposition frame 中强度最高的未使用离子出发，沿 mobility scan 向前和向后搜索：

- 每个 scan 选择最接近 seed m/z、且落在 tolerance 内的数据点；
- 允许默认最多跳过一个 scan；
- 连续长度至少为 15 点才保留；
- 已使用的数据点被置零，避免重复生成峰。

这部分由 Rcpp 实现：`MetCell/src/search_peak_target_in_superposition_frame.cpp:62-218`。

#### 6.2 平滑、峰顶和质量过滤

对每条候选 EIM：

- 用窗口 10 的 LOESS 平滑；
- 在 21 点范围内寻找局部最大值；
- 用峰顶两侧共 27 点的固定窗口积分；
- 计算强度加权 m/z、mobility apex 和总强度；
- 如果归一化残差标准差不小于 0.35，则过滤该峰；
- 根据 *m/z*–mobility 平面中的用户定义直线粗略区分单电荷与多电荷；
- 从 mobility apex 计算 CCS。

论文的 CCS 公式为：

$$
{\rm{CCS}}={\rm{convertor}}\times \frac{z}&#123;&#123;K}_{0}}\sqrt{\frac{1}&#123;&#123;TM}}}\sqrt{\frac{M+m}{m}}.
$$

其中 $1/K_0$ 是 mobility，$T=305$ K，$M$ 是分析物质量，$m$ 是 N$_2$ 质量。公开代码在 `MetCell/R/Utils-TimsData.R:343-351` 使用等价的固定常数表达式。

### 7. 最关键的一步：回到每个细胞做靶向提取

细胞叠加只负责回答“哪些峰是真的、坐标在哪里”，不能用叠加强度代替单细胞强度。于是 MetCell 用 superposition frame 中的峰作为模板，在每个原始细胞中建立窗口：

$$[(m/z)-\delta_{mz},(m/z)+\delta_{mz}]\times[u-\delta_u,u+\delta_u].$$

论文默认 $delta_{mz}=20$ ppm，$delta_u=0.04$ V s cm$^{-2}$。代码在每个 mobility scan 中选择最接近目标 m/z 的数据点，再把强度相加；没有点时记为 `NA`。

这里有一个容易误解但非常重要的设计：**单细胞提取阶段不再对每个细胞单独做峰真实性检查。** 峰真实性已经由 600 个细胞的 superposition frame 建立。这样，一个在单细胞中 SNR 很低的真实峰仍能被定量，而不会因为没有单独跨过检测阈值而变成 dropout。

这解释了 Fig. 2 的结果：

- acetylcarnitine dropout 从 83% 降到 1%；
- carnitine 从 13% 降到 0%；
- 100 个代谢物的平均 dropout 从 82% 降到 6%。

源码位于 `MetCell/R/test_targeted_extraction_function.R:1-72` 和 `MetCell/R/test_targeted_extraction.R:31-87`。文件名虽然含 `test_`，但它们实际承载导出的生产流程。

### 8. 同位素和候选代谢物注释

#### 8.1 电荷状态

只对单电荷峰进行候选代谢物匹配。用户在 *m/z*–mobility 平面定义一条直线，线上方视为单电荷，线下方视为多电荷。代码只赋值为 1 或 2，因此并不显式区分补充 Fig. 22 中的二、三、四电荷。

#### 8.2 同位素间隔

峰按 superposition frame 强度排序。最高的未分配峰作为 base peak `[M]`，候选同位素位置为：

$$
{m/z}_&#123;&#123;\rm{isotope}}}={m/z}_&#123;&#123;\rm{base}\_{peak}}}+1.003355\times N,
$$

其中 $N=1,2,3$，即搜索 `[M+1]` 到 `[M+3]`。默认 m/z tolerance 为 20 ppm，mobility tolerance 为 0.01 V s cm$^{-2}$。

同位素强度比误差为：

$$
{\Delta }_{\mathrm{ratio}}=\frac{|{\mathrm{Int}}_E-{\mathrm{Int}}_T|}&#123;&#123;\mathrm{Int}}_T}\times100.
$$

默认容许误差为 500%。代码实现了该百分比误差，但有一个论文未强调的近似：它不是根据已知候选分子式计算理论同位素分布，而是仅根据 m/z 推测一个烷烃分子式，再调用 Rdisop。因此“同位素强度验证”应视为部分实现，而不是严格的分子式级验证。

#### 8.3 MS1+CCS 候选搜索

论文构建了包含 20,566 个内源代谢物的数据库，来源包括 KEGG、HMDB 和 MetaCyc。对 `[M]` 峰，MetCell 根据允许的 adduct 计算理论 m/z，并用实验或 AllCCS 预测值提供 CCS。

研究参数为 MS1 10 ppm、CCS 最大 6%。公开代码采用矩形窗口同时筛 m/z 和 CCS，返回所有候选 ID、化合物名、adduct、m/z error 和 CCS error。这一步生成的是**候选**，不是论文最终的 770 或 809 个高置信度注释。

### 9. 最终代谢物身份怎样确定？

论文对候选峰在另一批单细胞中进行靶向 PRM-PASEF MS2：

- precursor isolation window：±0.6 Da；
- mobility window：±0.03 V s cm$^{-2}$；
- collision energy：30 eV；
- 每个 PRM-PASEF scan 可安排约 2–6 个候选；
- 每个代谢物采集 1 min，获得 10–50 张 MS2 谱。

同一代谢物的 fragment ions 按默认 20 ppm 分组并累加强度，再归一化到最高 fragment，形成 consensus spectrum。HepG2 中每个共识谱使用的 MS2 数量中位数为 31。

随后按证据来源划分置信度：

- **Level 1**：MS1 + 标准品实验 CCS + 与标准品 MS2 匹配；
- **Level 2**：MS1 + AllCCS 预测 CCS + 公共库 MS2 匹配；
- **Level 3**：MS1 + 预测 CCS + SIRIUS 结构注释；
- **Level 4**：MS1 + 预测 CCS + SIRIUS 分子式预测。

最终综合分数为：

$$
{\rm{Score}}={W}_&#123;&#123;\rm{CCS}}}{\rm{Score}}_&#123;&#123;\rm{CCS}}}+{W}_&#123;&#123;\rm{MS}}2}{\rm{Score}}_&#123;&#123;\rm{MS}}2}+{\rm{Score}}_&#123;&#123;\rm{Level}}},
$$

其中 $W_{\rm CCS}=W_{\rm MS2}=0.5$；level 加分分别为 4、3、2、1。CCS 分数在 3% 以内不扣分，3%–6% 线性下降，超过 6% 为 0：

$$
{\rm{Score}}_{\rm CCS}=\begin{cases}
1,&\Delta {\rm CCS}\le3\%,\\
1-\dfrac{\Delta {\rm CCS}-3\%}{6\%-3\%},&3\%<\Delta {\rm CCS}\le6\%,\\
0,&\Delta {\rm CCS}>6\%.
\end{cases}
$$

$$
\Delta {\rm CCS}=\frac{|{\rm CCS}_{\rm experiment}-{\rm CCS}_{\rm library}|}&#123;&#123;\rm CCS}_{\rm library}}\times100\%.
$$

这些 MS2、置信度和综合打分操作在当前 GitHub 代码快照的单细胞主流程中 **Not found**。因此不能把 `03_metabolite_annotation_table.csv` 直接解释为论文最终注释表。

### 10. 实验结果说明了什么？

#### 10.1 稳定性与覆盖度

- HepG2：5,718 个峰、770 个最终代谢物；
- 其他常见细胞系：5,074–6,975 个峰、533–622 个代谢物；
- 多种细胞类型合计 389 个唯一 Level 1 代谢物经标准品确认。

这比多数既有单细胞代谢组方法的 80–300 个候选更深，且最终身份不只依赖 MS1。

#### 10.2 定量灵敏度

作者用 LC–MS 的群体平均/中位数量标定单细胞 mass-cytometry 强度：

- adenine 的估计 LOD 为 8.2 amol；
- nicotinamide 为 54.7 amol；
- arginine 为 0.9 fmol；
- alanine 为 2.8 fmol。

在 FK866 抑制 NAD$^+$ 的实验中，荧光传感器和 IM-resolved mass cytometry 都观察到 NAD$^+$ 下移，treated/control 比值分别为 0.727 和 0.856。该结果支持扰动方向与近似效应量的一致性。

#### 10.3 45,603 个小鼠肝细胞

平台检测 5,659 个峰并注释 809 个代谢物。作者用单独分离的肝细胞筛选代谢 marker：

- hepatocyte：maltotetraose、maltotriose；
- 非实质细胞：PC(32:0)、PE(P-36:4)；
- HSC：retinol、retinal；
- LSEC：vitamin D$_3$、25-OH vitamin D$_3$；
- Kupffer cell：DG(34:2)、DG(36:2)。

这些 marker 支持主要肝细胞类型注释，并把 HSC 分成 retinol-high 与 retinol-low 两类。retinol-high HSC 同时具有更高 retinal、更低 glutathione，与更强氧化应激相符。

对 hepatocyte 的 Monocle 分析得到四个状态。衰老细胞在 state 3 和 4 中富集：state 3 更偏向 diacylglycerol，state 4 更偏向 maltopentaose/maltotetraose/maltotriose，提示脂质积累与糖原储存相关的两条代谢分支。

### 11. 代码真正覆盖到哪里？

#### 直接源码确认的部分

- marker pulse 单细胞 frame 识别；
- 600-cell scan-wise superposition；
- Rcpp bottom-up EIM 组装；
- LOESS、局部峰顶、noise filter 和 CCS；
- 每个细胞的靶向窗口提取；
- 同位素间隔与强度误差过滤；
- MS1+CCS 候选匹配；
- `01_feature_table.csv`、`02_isotope_annotation_table.csv`、`03_metabolite_annotation_table.csv`。

#### 当前快照中未找到的部分

- PRM-PASEF 靶向 MS2 调度；
- 10–50 张 MS2 谱生成 consensus spectrum；
- Level 1–4 自动分配；
- 论文公式 (4)–(6) 的综合排名；
- 小鼠肝 Seurat integration、marker 分析与 Monocle pseudotime 脚本；

代码–论文整体一致度因此评为 **medium**：最关键、最有方法创新性的峰提取核心有直接实现，但论文最终化学身份和生物学分析不由仓库单独完成。

### 12. 如何复现？

仓库提供 Docker 环境、R 包、示例 `run.R` 和参数表。补充材料报告：120-min HepG2 数据在 Intel Core i7-12700、7 threads 下约需 40 min，占用约 6–20 GB 内存。原始 `.d` 数据需要从外部 accession 获取，且依赖 timsTOF/OpenTIMS 环境。

一个现实的复现路径是：

1. 用 Docker 和 demo `.d` 数据验证 `01`–`03` 三张表；
2. 对照源码确认 superposition、EIM 和 targeted extraction 的中间结果；
3. 单独复现 PRM-PASEF 与共识 MS2；
4. 根据论文公式实现 confidence/ranking；
5. 从公开 liver count tables 重建 Seurat/Monocle 分析。

复现评级为 **3/5**：核心算法透明、参数充分，但完整论文结果还需要外部实验、谱库、软件和缺失的下游脚本。

### 13. 阅读时最容易踩的坑

1. **cell superposition 不是把细胞混成一个用于下游统计的样本。** 它只建立峰模板，最终强度仍来自每个单细胞。
2. **“检测峰”不等于“确认代谢物身份”。** 5,000–7,000 是 feature 数；数百个是经过多维证据后的 metabolite 数。
3. **`03_metabolite_annotation_table.csv` 仍是 putative candidate 表。** 最终 Level 1–4 需要外部 MS2/标准品/SIRIUS。
4. **CCS 同时帮助检测和注释，但不是万能身份标签。** 当前 IM 分辨率仍可能无法区分某些 isomer。
5. **pseudotime 是横断面推断。** 论文用染色和中间年龄组增强解释，但仍需要更完整年龄序列验证。

### 结论

MetCell 的方法学价值在于把仪器端的离子淌度与计算端的“全局检峰、局部定量”紧密结合。细胞叠加让弱而一致的离子从噪声中显现，靶向回提取则保留单细胞差异；随后 MS1、CCS、MS2 和标准品证据提高代谢物身份可信度。公开代码充分支撑前半段核心算法，但完整复现论文的高置信度注释和肝脏图谱仍需补齐实验性 MS2 与下游分析链。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MetCell: deep-coverage single-cell metabolomics with ion mobility-resolved mass cytometry

### Problem

Mass-cytometry-based single-cell metabolomics is fast, but each cell is measured for only about 0.1 s and contains many metabolites at attomole abundance. Low SNR, technical dropouts, ion interference and MS1-only acquisition limit sensitivity, robustness, chemical coverage and annotation confidence. Existing studies generally reported tens to a few hundred putative metabolites, often using MS2 acquired from bulk rather than the measured single cells. For context, Supplementary Table 3 lists SpaceM (*Nature Methods*, 2021) with 88 putative annotations and one standard-confirmed metabolite, a CCS-based method by Nunes et al. (*Nature Methods*, 2024) with 112 annotations and no MS2, and Qin et al. (*Nature Communications*, 2024) with 348 annotations and six standard-confirmed metabolites.

### Proposed technology

The paper combines a pressure-driven single-cell injector with trapped ion mobility–mass spectrometry and the MetCell computational workflow. The key ideas are:

- **Selective ion accumulation:** shorter TIMS accumulation/ramping and adjusted voltages favor low-mass metabolite ions while reducing interference.
- **Cell superposition:** align mobility scans across hundreds of cells and aggregate coherent ions to detect reliable EIM peaks at high SNR.
- **Targeted per-cell extraction:** use those globally detected peaks as targets and quantify them in every original cell, preserving single-cell resolution while reducing dropout.
- **Multidimensional annotation:** narrow candidates using MS1 and CCS, acquire targeted PRM-PASEF MS2 from single cells, build consensus spectra, and assign confidence levels using standards, public libraries or SIRIUS.

MetCell's computational path is:

```text
raw IM-MS -> cell-frame detection -> 600-cell superposition
          -> bottom-up EIM peak detection -> targeted per-cell quantification
          -> charge/isotope annotation -> MS1+CCS candidates
          -> external targeted MS2 and level 1-4 final annotation
```

### What is novel

The central novelty is the global-then-local detection strategy. Weak but coherent metabolite signals are first amplified across cells only to establish trustworthy peak locations; the method then returns to each cell for quantification. This avoids requiring every weak single-cell trace to independently pass a detection threshold. Ion mobility is also used twice: physically, to separate and selectively accumulate ions, and computationally, as a second coordinate for peak detection and candidate filtering.

### Evaluation and main results

- **Measurement sensitivity:** selective accumulation increased the relative contribution of ions below 200 Da by about 12-fold and below 400 Da by about fourfold in HepG2 cells, with individual metabolite gains up to 20-fold.
- **Robustness:** acetylcarnitine SNR increased from 3.3 in one cell to 157.6 after superposing 600 cells. Across 100 metabolites, median SNR improved 33-fold and mean dropout decreased from 82% to 6%.
- **Coverage:** MetCell detected 5,718 peaks and finalized 770 metabolites in HepG2 cells. Across other common cell lines it detected 5,074–6,975 peaks and 533–622 metabolites. Mixed liver cells yielded 5,659 peaks and 809 metabolites.
- **Annotation confidence:** 389 unique metabolites across cell types were level 1 and validated with chemical standards. CCS filtering reduced candidate ambiguity, while consensus MS2 improved representative dot-product scores.
- **Quantification:** LC–MS calibration and an NAD$^+$ fluorescent sensor supported attomole-to-low-femtomole sensitivity and recovery of perturbation direction/magnitude.
- **Biological application:** in 45,603 mouse liver cells, metabolite markers annotated hepatocytes, LSECs, Kupffer cells and HSCs; retinol-high/low HSC subtypes and two aging-associated hepatocyte states were resolved.

### Code–paper match

Overall fidelity is **medium**. The released R package at commit `2057592a4d0cbb96ebfcc5f2e7799afbf052273f` directly implements the novel MS1/ion-mobility feature-extraction core: marker-pulse detection, scan-wise superposition, bottom-up EIM assembly, local-maximum/noise filtering, CCS calculation, targeted per-cell extraction, isotope labeling, MS1+CCS candidate matching and the three documented CSV outputs.

Important gaps remain. The package's `03_metabolite_annotation_table.csv` contains putative MS1+CCS candidates, not the paper's final confidence-level identities. Executable PRM-PASEF acquisition, consensus MS2 construction, equations (4)–(6) combined ranking, confidence-level assignment, Seurat liver integration and Monocle pseudotime were **Not found** in the snapshot. The isotope-intensity check also uses an m/z-derived alkane approximation in Rdisop, a detail not stated in the paper.

### Reproducibility

**Rating: 3/5 — the core algorithm is inspectable and plausibly rerunnable, but the full paper is not reproduced by the repository alone.**

The supplement reports about 40 min and 6–20 GB RAM for a 120-min HepG2 run with seven threads.

Constraints include external raw `.d` data and instrument dependencies, no included automated tests or recorded successful run, a package data file over 10 MB, and missing executable code for the final MS2/confidence and biological-analysis layers. Reproducing the headline annotation and atlas results therefore requires the external datasets, PRM-PASEF acquisition, spectral libraries/SIRIUS, and reimplementation of the described Seurat/Monocle workflow.

### Limitations

- positive-ion mode only in the reported platform;
- incomplete cell disruption, ion suppression and reduced recovery of nonpolar metabolites;
- current IM resolution may not separate some isomers, including maltotetraose and maltotriose;
- chimeric MS2 spectra occur and about half of acquired spectra remain unannotated;
- rare cell types and dissociation-sensitive metabolites may be missed or perturbed;
- aging trajectories are cross-sectional and need broader intermediate-age cohorts.

### Bottom line

MetCell's strongest contribution is a coherent technology stack that couples IM-enabled sensitivity with a source-verified cell-superposition/targeted-extraction algorithm. It substantially improves peak detectability and depth while retaining individual-cell measurements. The public code supports that core claim, but the final high-confidence metabolite annotations and liver-atlas conclusions depend on experimental and downstream analysis stages beyond the released package's executable main workflow.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
