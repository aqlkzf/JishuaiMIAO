---
layout: default
permalink: /paper-atlas/fx-cell-41e26bf1/
title: "FX-Cell"
nav: false
description: "FX-Cell 的核心不是“把传统原生质体法的温度调高”，而是先用 Farmer’s solution 固定植物组织，让细胞在更强的机械扰动和更高效的细胞壁消化条件下仍保持形态；再通过 GMP-Sepharose/agarose 去除消化酶中的真菌 RNase，并用 tRNA 与 tri-GMP 继续保护 RNA，最终得到可用于 scRNA-seq 的固定单细胞悬液。"
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
    <h1>FX-Cell</h1>
    <p>FX-Cell: a method for single-cell RNA sequencing on difficult-to-digest and cryopreserved plant samples</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02900-2" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for FX-Cell">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/WangLab-CEMPS/Xin_Ming_FX_Cell" target="_blank" rel="noopener noreferrer" aria-label="Open code for FX-Cell">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## FX-Cell 方法详解：从难消化植物组织到可分析的单细胞转录组

### 一句话理解

FX-Cell 的核心不是“把传统原生质体法的温度调高”，而是先用 Farmer’s solution 固定植物组织，让细胞在更强的机械扰动和更高效的细胞壁消化条件下仍保持形态；再通过 GMP-Sepharose/agarose 去除消化酶中的真菌 RNase，并用 tRNA 与 tri-GMP 继续保护 RNA，最终得到可用于 scRNA-seq 的固定单细胞悬液。

论文还给出两个冷冻衍生方案：

- **FXcryo-Cell**：先固定，再冷冻保存，之后解冻消化；
- **cryoFX-Cell**：先冷冻保存，之后解冻、固定并消化。

这三个方案共同解决“组织难消化、采样地点远离实验室、急性响应会被制样过程扰动”三个问题。

### 1. 论文到底在解决什么问题？

#### 1.1 传统植物 scRNA-seq 的入口瓶颈

植物 scRNA-seq 通常先去掉细胞壁，获得仍然存活的原生质体。但这一步有四类困难：

1. **细胞壁难以消化。** 次生壁增厚、木质化或特殊多糖成分会导致某些组织几乎不能释放高质量原生质体。
2. **必须及时处理。** 田间材料采下后通常需要立即进行 1–2 h 的酶解，而很多采样点没有分子实验条件。
3. **消化本身改变转录组。** 机械损伤与长时间酶解会诱导 wound/stress genes，尤其不利于研究急性胁迫。
4. **snRNA-seq 不是完全等价的替代。** 单核数据通常检测基因数更低，只代表核 RNA，并可能出现核聚集和较高 doublet 风险（`paper.md:21-33`）。

#### 1.2 相关先前方案及其局限

- Nelms 与 Walbot 在 *Science* 2019 的玉米花药工作提供了原生质体/CEL-Seq2 路线，但新论文显示，常规条件下难以快速、完整地释放多类细胞。
- Zhang 等在 *Nature Communications* 2021 构建了水稻根单细胞图谱，成为 FX-Cell 的主要传统原生质体参照；但这类方案依赖新鲜、可消化材料。
- Procko 等在 *The Plant Cell* 2022 构建了拟南芥叶片图谱；FX-Cell 论文用它显示，传统制备可能在所谓“未受伤”材料中引入 wound-like 状态。
- snRNA-seq 可跨越细胞壁障碍，但论文中的水稻根和叶片比较显示其每个核检测到的基因数更少。

### 2. FX-Cell 的设计逻辑

#### 2.1 固定解决“释放难”，但制造“RNA 暴露”问题

**[论文事实]** Farmer’s solution 为 3:1 的无水乙醇:冰醋酸。凝固型固定剂稳定细胞内部蛋白基质，并破坏脂质膜。固定后的细胞不再是活的原生质体，因此论文称其为 “cells”（`paper.md:42-45`）。

固定带来两个直接好处：

- 细胞质被稳定，细胞更能承受剪切与吹打；
- 可以在更接近 cellulase 高活性的温度下消化细胞壁。

但膜被破坏后，RNA 也暴露给溶液中的 RNase。商业植物细胞壁消化酶多为真菌复合物，含 T1/T2 类 RNase；常见针对脊椎动物 RNase A 的抑制剂效果有限（`paper.md:68-74`）。

#### 2.2 真正的关键是“固定 + RNase 工程”

**[论文事实]** 作者把 GMP 偶联到 amino-Sepharose/agarose 上。真菌 RNase 与 GMP 配体结合，而 cellulase、pectinase 等目标消化酶流出。最终优化方案进行重力柱和 FPLC 纯化，并可再做一次 FPLC 纯化（`paper.md:268-301`; `supp.md:14-151`）。

**[解释]** 可以把这一步理解为“从混合酶制剂中选择性拿掉最危险的 RNA 降解活性”，而不是直接抑制所有 RNase。之后加入 tRNA 与 tri-GMP，继续充当竞争性底物/配体，降低残余 RNase 对目标 RNA 的攻击。

#### 2.3 冷冻顺序让采样与实验室处理解耦

FXcryo-Cell 与 cryoFX-Cell 的差别不是分析算法，而是采样端能否立即固定：

```text
FX-Cell:      新鲜材料 → 固定 → 洗涤 ─────────→ 消化 → scRNA-seq

FXcryo-Cell:  新鲜材料 → 固定 → 洗涤 → 冷冻/保存 → 解冻 → 消化 → scRNA-seq

cryoFX-Cell:  新鲜材料 → 冷冻/保存 → 解冻 → 固定 → 洗涤 → 消化 → scRNA-seq
```

FXcryo-Cell 更适合采样现场能够快速固定的实验；cryoFX-Cell 更适合只能先快速冷冻的田间条件。

### 3. 输入、输出与变量

#### 3.1 湿实验输入

- 植物组织：新鲜、固定后冷冻或直接冷冻；
- Farmer’s solution；
- RNase-depleted 细胞壁消化酶；
- mannitol/MES/KCl/CaCl~2~/BSA 缓冲体系；
- tRNA 与 tri-GMP；
- 40-μm cell strainer、离心与细胞计数设备；
- 10× Genomics 3′ 或适合大细胞的 well-based 单细胞平台。

#### 3.2 计算输入

- 10× count matrix，抽象记为 $X\in\mathbb{N}^{G\times C}$，其中 $G$ 为基因数、$C$ 为细胞数；
- 样本与技术标签，例如 `orig.ident`、`tech`；
- 物种参考基因组与注释；
- 已发表的细胞类型 marker；
- 比较图谱与跨物种 ortholog 表；
- wound-response gene set，即 GO:0009611 对应基因集合。

这里 $X$ 的形状是为了帮助理解而引入的记号；论文没有显式定义该符号。

#### 3.3 输出

- 固定、去壁的单细胞悬液；
- 每个细胞的 UMI count matrix；
- QC 后的 Seurat object；
- UMAP、cluster、cell-type annotation；
- marker/GO overlap coefficient；
- wound-response AUCell score；
- 细胞类型特异的差异表达和 GO enrichment 结果。

### 4. 湿实验流程逐步拆解

#### 4.1 制备 GMP-Sepharose/agarose

1. 用 NaIO~4~ 氧化 5′-GMP。
2. 在 pH 9.0 borax 条件下与 NH~2~-Sepharose 偶联。
3. 用 NaBH~4~ 还原稳定连接。
4. 洗涤后用 1 M NaCl 保存。

**质量控制：** 取树脂在 1 M HCl 中沸水浴 1 h，使 GMP 水解产生 guanine；guanine 在 248 nm 有最大吸收。成功偶联的树脂应明显高于未偶联对照（`paper.md:286-289`; `supp.md:73-87`）。

#### 4.2 从消化酶中去除 RNase

1. 将 10× 细胞壁消化酶溶于 RNase binding buffer：150 mM NaCl、10 mM citrate、pH 7.0。
2. 低温离心两次去除不溶物。
3. 通过 GMP-Sepharose gravity column，收集流出液。
4. 用 10-kDa MWCO 超滤管浓缩至接近原始蛋白浓度。
5. 通过 GMP-Sepharose FPLC column；收集 A280 > 0.1 的 fractions。
6. 优化方案再次进行 FPLC 纯化。
7. 测 RNase activity，原始酶作为 positive control。

柱子可用 5 M NaCl、1 mM 5′-GMP、1 mM 2′(3′)-GMP 洗脱 bound RNase 后再生（`supp.md:94-155`）。

#### 4.3 最终 FX-Cell 固定步骤

1. 将 Farmer’s solution 预冷于冰上。
2. 放入植物材料，抽真空直到材料沉底。
3. 冰上固定 30 min。
4. 用预冷 0.1× PBS 洗两次，每次冰上 5 min。

**重要区分：** 论文早期开发实验常用 2 h 固定、50 °C/90 min 消化；最终高通量 protocol 为 30 min 固定、40 °C/30 min 消化。前者证明“固定可增强释放”，后者是为减少 RNA degradation 而优化后的操作条件（`paper.md:100,247,340-352`）。

#### 4.4 最终 5 ml 消化体系

| 成分 | 终浓度 |
|---|---:|
| mannitol | 0.4 M |
| MES, pH 5.7 | 20 mM |
| KCl | 10 mM |
| CaCl~2~ | 10 mM |
| BSA | 0.1% |
| 10× RNase-depleted enzyme | 1× |
| tRNA | 1 mg ml^−1^ |
| tri-GMP | 1 mM |

tri-GMP 是 5′-GMP 与 2′(3′)-GMP 的混合物。消化液经 0.45-μm filter 后使用（`supp.md:170-185`）。

#### 4.5 消化、释放与洗涤

1. 固定组织在 40 °C、80 rpm 下消化 10 min；
2. 机械破碎组织；
3. 继续在 40 °C、80 rpm 下消化 20 min；
4. 40-μm strainer 过滤；
5. 4 °C、300$g$、3 min 离心；
6. 0.1× PBS 重悬，再过滤；
7. PBS 洗两次；
8. 最终重悬于 50 μl 0.1× PBS 并显微计数。

**[解释]** 0.4 M mannitol 维持渗透环境，MES/KCl/CaCl~2~ 提供常见原生质体消化缓冲条件；这里最具方法特异性的变量是“固定状态、RNase-depleted enzymes、tRNA、tri-GMP、较短的 40 °C 消化”。

#### 4.6 不同组织的酶组合不是固定不变的

难消化的水稻分蘖节、野生稻根茎节与 *Selaginella* 茎尖需要 C + M + S + P：

- C：cellulase-RS；
- M：macerozyme-R10；
- S：snailase；
- P：pectinase。

论文建议先用更广的酶集合筛选是否能释放单细胞，再逐个去掉不必要的酶。原因是总酶量过高会加大 RNase depletion 难度（`paper.md:250-265`）。因此，不应把单一配方视为适用于所有植物组织的标准答案。

#### 4.7 建库与测序

最终高通量方案使用 Chromium Next GEM Single Cell 3′ v3.1，随后 150-bp paired-end sequencing。早期玉米花药验证则使用 BioSorter/Hana 分选到孔板并进行 modified CEL-Seq2（`paper.md:86,319-343`）。

选择平台时要考虑固定植物细胞的尺寸与形状。论文指出，某些植物细胞可达 10–100 μm，可能堵塞 droplet microfluidics；这类样本可考虑 well-based Rhapsody 或能处理较大细胞的分选平台。

### 5. 计算流程：从 count matrix 到论文结论

```text
raw reads
   ↓ Cell Ranger v7.0.0
gene × cell count matrix
   ↓ species-specific QC
NormalizeData → ScaleData → RunPCA
   ↓
FindNeighbors → FindClusters → RunUMAP
   ↓
外部图谱比较：IntegrateLayers + Harmony
三种 FX 衍生方法内部比较：merge，不做 Harmony
   ↓
marker genes → cell-type annotation
   ↓
overlap / GO / AUCell / differential expression
```

#### 5.1 QC、标准化、降维与聚类

**[论文事实]** Cell Ranger v7.0.0 负责 index building 与 gene expression quantification；Seurat v5 负责 QC、normalization、dimensionality reduction、clustering、integration 与 differential expression。不同物种使用不同 QC 阈值（`paper.md:379-382`）。

**[代码验证]** 水稻 FX-Cell 的一个具体脚本：

- `CreateSeuratObject(min.cells = 3, min.features = 200)`；
- 计算 `percent.mito` 与 `percent.chlo`；
- 保留 `500 < nFeature_RNA < 6000`、`nCount_RNA < 25000`、`percent.mito < 5`、`percent.chlo < 2` 的细胞；
- 保存为 RDS（`src/osroot/ggm/root_01QC.R:6-50`）。

这些值是特定水稻样本的实现参数，不能直接推广为所有 FX-Cell 样本的统一阈值。

#### 5.2 外部图谱整合

**[论文事实]** 为降低 cell-number imbalance，已发表的水稻根和拟南芥叶数据分别保留 51% 与 38% 细胞。与外部数据比较时使用 Seurat `IntegrateLayers`；FX-Cell、FXcryo-Cell 与 cryoFX-Cell 三个水稻根图谱之间则直接 `merge`（`paper.md:385-388`）。

**[代码验证]** 水稻 FX-Cell 与已发表根图谱的脚本依次执行：

```text
read prepared RDS → extract counts → rebuild Seurat objects → merge
→ NormalizeData → FindVariableFeatures → ScaleData → RunPCA(npcs=100)
→ HarmonyIntegration(theta=4)
→ dimensions 1:40 → neighbors → clusters(resolution=0.3) → UMAP
```

直接证据为 `src/osroot/ggm/root_03Merge_ggm2_tq2.R:7-59`。

**[代码验证]** 三个 FX 衍生方法的水稻根对象直接 merge 后进行 PCA/cluster/UMAP，脚本中没有 Harmony integration call，与论文“未做 batch correction”的图注一致（`src/osroot/merge_ggm_gdm_dgm.R:7-56`）。

#### 5.3 细胞类型注释

论文使用已发表 marker genes；野生稻则先通过 BlastP 找到水稻/拟南芥 ortholog，再借用已知 marker（`paper.md:391-394`）。

**[代码验证]** 根茎分析脚本将 cluster 显式映射到 `Xylem`、`Phloem & Companion-Cell`、`QC-like & Root-meristem`、`Shoot-meristem-like` 等标签，并用 marker DotPlot 检查表达（`src/tillering_node_rhizome/rhizome_04_addanno.R:5-28,30-125`）。

**[缺口]** 该脚本没有完整记录“每一个 marker 来自哪篇参考文献、如何形成最终 cluster-to-celltype 决策”的可追溯链，因此注释实现为 **Partial**，而不是完整自动化注释算法。

### 6. 两个 overlap coefficient

论文保留的符号为：

- $\mathrm{mFX}$：FX-Cell 某一 cluster 的 marker genes；
- $\mathrm{mPub}$：已发表图谱对应 cluster 的 marker genes；
- $\mathrm{goFX}$：FX-Cell cluster 的 enriched GO terms；
- $\mathrm{goPub}$：已发表数据对应 cluster 的 enriched GO terms。

marker overlap：

$$
{\rm{overlap}}\left(&#123;&#123;\rm{mFX}},{\rm{mPub}}}\right)=\frac{|{\rm{mFX}}\bigcap {\rm{mPub}}|}{\min (|{\rm{mFX}}|,|{\rm{mPub}}|)}
$$

GO overlap：

$$
{\rm{overlap}}\left(&#123;&#123;\rm{goFX}},{\rm{goPub}}}\right)=\frac{|{\rm{goFX}}\bigcap {\rm{goPub}}|}{\min (|{\rm{goFX}}|,|{\rm{goPub}}|)}
$$

论文把 coefficient ≥ 0.4 视为显著相似（`paper.md:403-421`）。

**[代码验证]** `calculate_overlap(set1, set2)` 直接计算 `length(intersect(set1,set2)) / min(length(set1),length(set2))`（`src/osroot/ggm/FindAllMarkers_ggm2_tq2.R:39-44`）。

代码还增加了论文方法段没有强调的过滤：

- 丢弃某数据集中少于 50 个细胞的 cluster；
- `FindAllMarkers(only.pos = TRUE)`；
- marker 保留 `pct.1 >= 0.2`；
- 只比较两个数据中共享的 cluster 名称（同文件 `:8-53`）。

这些是复现图表时必须注意的实现细节。

### 7. 急性伤口响应分析

#### 7.1 实验逻辑

完整叶片与受伤叶片在处理后 2 h 采样，固定、洗涤、冷冻，5 天后进行 FXcryo-Cell。因为固定发生在采样时，作者希望“冻结”当时的转录状态，避免之后 1–2 h 原生质体消化成为新的伤口刺激（`paper.md:173-182`）。

#### 7.2 AUCell

对 GO:0009611 的 wound-response genes 构建 gene set。对每个细胞 $c$，可把结果解释为 wound gene set 在该细胞表达排序中的富集分数 $A_c$；这是解释性符号，论文使用 AUCell score，但没有定义 $A_c$。

**[代码验证]**：

```r
GeneSets <- list(wound = unique(go))
CellsAUC <- AUCell_run(cts, GeneSets)
getAUC(CellsAUC)["wound", ]
```

代码从 counts layer 计算 AUC，将分数附加到 Harmony UMAP，并生成分组 UMAP 与 cell-type violin/box plot（`src/athleaf/07GO_AUCell.R:8-68`）。用于作图的 AUC 还经过 min–max scaling；这是代码细节，论文正文没有特别说明。

#### 7.3 细胞类型特异差异表达与 GO

**[代码验证]** 完整与受伤 FXcryo-Cell 叶片在 Bundle-Sheet、Phloem、Epidermis、Hydathode、Mesophyll 中分别做 `FindMarkers`。代码要求：

$$
p<0.05,\quad p_{\rm adj}<0.05,\quad |\mathrm{avg\_log2FC}|>1.58.
$$

之后对上调/下调基因分别运行 `enrichGO`，使用 BH adjustment（`src/athleaf/DE_LC_LPZ.R:19-81`）。

### 8. 评价结果应该怎样解读？

#### 8.1 细胞释放效率

**[论文事实]** 玉米花药：

- 新鲜、30 °C、90 min：平均 4,387 个原生质体；
- 新鲜、30 °C、16 h：11,333；
- 固定、30 °C、90 min：15,900；
- 固定、50 °C、90 min：45,033，接近约 50,000 个实际细胞数。

多数其他组织提高 10–364 倍，但玉米叶片例外：新鲜样本释放量约为固定方案的 3.6 倍（`paper.md:45-65`）。这说明固定并不对所有高含水、巨液泡细胞有利。

#### 8.2 RNA 完整性

玉米花药平均 RIN：

- 固定、不消化：9.3；
- 固定 + commercial enzymes：4.1；
- 固定 + RNase-depleted enzymes：6.7；
- 固定 + 50 °C buffer、无酶：6.1。

**[解释]** RNase depletion 明显改善 RNA，但不能完全恢复到未消化水平；buffer-only 也下降，提示残余 endogenous RNase 或热/时间因素仍然存在（`paper.md:80`）。

#### 8.3 水稻根高通量性能

优化后的 FX-Cell 两个 replicate：

- 9,474 与 8,874 个细胞；
- median genes/cell 为 1,494 与 1,661。

同一研究的 snRNA-seq：

- 1,428 与 1,835 个核；
- median genes/nucleus 为 635 与 629。

因此论文所说的“优于 snRNA-seq”主要指该实验中的 cell recovery 与 gene detection，而不是对所有样本、所有平台的普遍定理（`paper.md:89-112`）。

#### 8.4 冷冻与难组织应用

- FXcryo-Cell 水稻根：6,192/8,259 cells，median genes 1,637/1,711；
- cryoFX-Cell 水稻根：7,578/5,524 cells，median genes 1,660/1,465；
- 水稻分蘖节：5,822 cells，median genes 1,504；
- 野生稻根茎节：9,233 cells，median genes 891；
- 田间玉米冠根，保存 50 天：9,127 cells，median genes 1,857。

这些结果支持“冷冻保存后仍可构建有解释力的 atlas”，但不同组织的 gene complexity 差异很大，不能只用一个阈值评价成功与否。

#### 8.5 伤口响应

完整与受伤拟南芥叶片分别获得 7,815 与 8,979 个细胞，median genes 为 3,746 与 4,012。FXcryo-Cell 的完整叶片中 wound-like clusters 和 AUCell score 较弱；受伤材料与传统原生质体数据中更明显。不同 cell types 的响应不一致：dividing cells 最弱，epidermis、mesophyll、phloem、bundle sheath 更强（`paper.md:179-199`）。

**[解释]** 这不是简单地说“传统图谱都是错的”，而是提示：当研究目标正是快速应激时，制样过程可能成为重要混杂因素，固定时间点需要纳入实验设计。

### 9. 图像证据如何补强方法链？

本地 15 张图均已直接检查：

- Fig. 1/Extended Data 1 同时显示 release、RNase purification 与 RIN tradeoff；
- Fig. 2–3 显示优化后性能、两个 cryo 顺序及 replicate-level UMAP 一致性；
- Fig. 4 与 Extended Data 6–7 显示难组织/田间样本的 marker annotation 与 seq-FISH spatial validation；
- Fig. 5 与 Extended Data 8–9 显示 wound AUCell、cell-type-specific genes/GO，以及与 snRNA-seq 的比较；
- Extended Data 10 显示 *O. longistaminata* 与 *O. sativa* 以 syntenic blocks 为主，为野生稻 reads mapping/annotation 提供参考基础。

但 UMAP 重叠不是严格等价性证明，代表性显微图也不能单独证明无偏细胞回收；精确数值仍需 source data。

### 10. 代码与论文的一致性

总体 paper-code fidelity：**medium**。

#### Exact：代码中可直接核验

- 水稻根 QC；
- Seurat normalization/PCA/clustering/UMAP；
- Harmony integration；
- 三个 FX 衍生方法不做 Harmony 的 merge；
- marker 与 GO overlap equations；
- AUCell wound score；
- cell-type-specific DE 与 GO；
- 多个组织的 marker-based annotation/figure scripts。

#### Partial

- repository 有大量下游脚本，却没有 end-to-end runner、容器或 package lock。

#### Not found

- 固定、冷冻、柱纯化、消化、洗涤、建库等湿实验自动化代码；
- Cell Ranger 命令与 reference-index build commands。

Repository README 明确说明它包含的是 “downstream analysis of FX-Cell data” (`README.md:5-20`)。因此不能因为没有湿实验代码就说论文方法不存在，也不能因为下游脚本丰富就说 assay 已被完整计算复现。

### 11. 实际复现时最容易踩的坑

1. **把 50 °C/90 min 当成最终 protocol。** 那是开发阶段条件；最终高通量方案为 40 °C/30 min。
2. **只做固定，不做 RNase 工程。** 固定提高释放，但会暴露 RNA；双重纯化、tRNA 和 tri-GMP 是核心组成。
3. **把 C + M + S + P 当成所有组织的万能配方。** 应先做组织特异的 enzyme screen。
4. **忽略细胞尺寸。** 固定细胞可能保留不规则形态，droplet platform 可能堵塞。
5. **直接照搬 QC thresholds。** 不同物种和组织应重新检查 `nFeature_RNA`、UMI、mitochondrial/chloroplast fraction。
6. **认为 Harmony 后重叠就等于无 batch effect。** integration 是分析工具，不是实验等价性的证明。
7. **忽略代码路径依赖。** 多个脚本需要预先生成的 `dataLib/*.Rds` 和作者 home directory 下的 reference files。

### 12. 已知缺口与证据边界

- **[缺口]** 本地代码未执行，因此不声称数值复现。
- **[缺口]** 105 个 R 文件中未找到 Cell Ranger 命令、湿实验执行代码或统一环境定义。
- **[缺口]** 部分 RDS/raw/reference inputs 的完整可用性未验证；脚本含 `~/wkdir`、`~/ref` 路径。
- **[论文局限]** 大液泡细胞可能固定后更脆；大细胞可能堵塞微流控；固定破坏蛋白，不能用于依赖蛋白荧光的 FACS；部分组织仍需优化或改用 snRNA-seq。
- **[统计边界]** 部分 release/RIN 比较使用未做 multiple-comparison adjustment 的 Student’s t-test。

### 13. 研究者应如何选择三种方案？

```text
材料新鲜且可立即进实验室？
  ├─ 是：FX-Cell
  └─ 否：采样点能否立即完成固定/洗涤？
         ├─ 能：FXcryo-Cell
         └─ 不能，只能快速冷冻：cryoFX-Cell
```

在正式上机前，建议依次做三个小规模 gate：

1. **Release gate：** 固定后是否能释放目标细胞类型？
2. **RNA gate：** RNase-depleted enzyme 与最终温度/时间下 RIN 或等价指标是否可接受？
3. **Platform gate：** 细胞尺寸、聚集与形态是否适合计划使用的 capture system？

FX-Cell 最适合的问题不是“所有植物样本都必须改用固定细胞”，而是：当传统原生质体法因难消化、远程采样或制样诱导转录改变而失真时，能否用固定与 RNase 工程换取更可控的单细胞入口。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## FX-Cell

**Paper:** *FX-Cell: a method for single-cell RNA sequencing on difficult-to-digest and cryopreserved plant samples*. *Nature Methods* (2025). DOI: `10.1038/s41592-025-02900-2`.

### Problem

Plant scRNA-seq normally requires live protoplasts, but many cell walls resist enzymatic digestion. Fresh protoplasting also ties sampling to an equipped laboratory and takes 1–2 h, long enough to induce wound/stress transcription. snRNA-seq avoids cell-wall digestion but generally detects fewer genes, samples nuclear rather than whole-cell RNA and can have nucleus aggregation/doublet problems (`paper.md:21-33`).

The relevant predecessors include the maize-anther protoplasting/CEL-Seq2 workflow of Nelms and Walbot (*Science*, 2019), the published rice-root atlas used as the main comparison (Zhang et al., *Nature Communications*, 2021), and the Arabidopsis leaf atlas used in the wound analysis (Procko et al., *The Plant Cell*, 2022; references 31, 37 and 61).

### Proposed technology

FX-Cell fixes plant tissue in Farmer’s solution before cell-wall digestion. Fixation stabilizes the cytoplasm, allowing stronger mechanical disruption and elevated-temperature digestion, but it also exposes RNA to fungal RNases in commercial enzyme mixtures. The method therefore couples fixation to GMP-Sepharose/agarose affinity depletion of RNases, repeated purification, and tRNA/tri-GMP protection. The optimized high-throughput protocol digests at 40 °C for 30 min rather than the initial 50 °C/90 min condition.

Two derivatives change the cryopreservation order:

- **FXcryo-Cell:** fix and wash, then freeze/store; thaw before digestion.
- **cryoFX-Cell:** freeze/store first; thaw, fix and digest later.

The final digest is filtered and washed, then used for 10× Genomics 3′ library preparation. Cell Ranger generates count matrices; Seurat performs QC, normalization, dimensionality reduction, clustering, integration and marker discovery. Published atlases are integrated with Harmony when needed. Cell types are assigned using published markers/orthologs, marker and GO agreement are measured with the Szymkiewicz–Simpson overlap coefficient, and wound-response activity is scored with AUCell.

### Main evidence

- Fixed maize anthers released about 45,033 cells after 90 min at 50 °C, compared with 4,387 fresh protoplasts after 90 min at 30 °C. Fixation increased release in most additional tissues, though maize leaves were a notable failure case (`paper.md:45-65`; Fig. 1).
- Maize-anther RIN was 9.3 after fixation alone, 4.1 after conventional-enzyme digestion and 6.7 after RNase-depleted-enzyme digestion, showing partial—not complete—RNA protection (`paper.md:80`; Fig. 1).
- Optimized FX-Cell rice-root replicates captured 9,474 and 8,874 cells with median 1,494 and 1,661 genes per cell, compared with 1,428 and 1,835 nuclei and median 635 and 629 genes in the tested snRNA-seq datasets (`paper.md:89-103`; Fig. 2).
- FXcryo-Cell and cryoFX-Cell produced reproducible rice-root atlases with broadly preserved marker patterns, demonstrating that either freeze/fix order can work (`paper.md:115-138`; Fig. 3).
- FXcryo-Cell enabled atlases from difficult rice tiller nodes (5,822 cells) and wild-rice rhizome nodes (9,233 cells); cryoFX-Cell recovered 9,127 cells from field-grown maize crown roots after 50 days of storage (`paper.md:141-170`; Fig. 4).
- In Arabidopsis leaves, intact FXcryo-Cell samples had much weaker wound-response populations and AUCell signal than wounded FXcryo-Cell or conventional protoplasting data. Different cell types showed distinct wound programs, with dividing cells weakest and epidermal, mesophyll, phloem and bundle-sheath cells stronger (`paper.md:173-199`; Fig. 5).

Direct inspection of all 15 local figure files supports this evidence chain while also showing the tradeoffs: hotter/longer digestion worsens RIN, marker-based annotation remains necessary, and snRNA-seq still integrates broadly with the cell atlases.

### What is novel

The novelty is not fixation alone. It is the combined engineering of:

1. fixation-enabled aggressive wall digestion;
2. GMP-affinity depletion and regeneration for fungal RNases;
3. tRNA/tri-GMP protection during digestion;
4. flexible fixation/freezing order for field and stored samples; and
5. downstream whole-cell atlases that better preserve the sampled transcriptional state than conventional protoplasting in acute-response experiments.

### Limitations

- Large vacuolated cells can be fragile after fixation; maize leaf is the paper’s clearest example.
- Large or irregular plant cells can clog droplet microfluidics, motivating well-based alternatives for some tissues.
- Digestion enzymes remain tissue specific, and the method is not guaranteed to release every plant cell type.
- Protein denaturation makes the method incompatible with protein-dependent fluorescence-activated cell sorting.
- snRNA-seq remains more broadly applicable across tissues and can complement FXcryo-Cell.
- Several cell-release/RIN comparisons use unadjusted Student’s t-tests.

### Reproducibility and code-paper match

**Reproducibility: 3/5.** The paper provides a detailed supplementary bench protocol, reagent concentrations, data accessions and a public downstream-analysis repository. Raw scRNA-seq/snRNA-seq/RNA-seq data are deposited under BioProject `PRJCA035988`; the wild-rice assembly/annotation is at figshare record `28457807`; source data accompany the article (`paper.md:436-445`).

**Code-paper fidelity: medium.** The repository directly implements Seurat QC/clustering, Harmony integration, the marker/GO overlap equations, AUCell wound scoring, differential expression/GO analysis and marker-based annotations. However, it explicitly contains downstream analysis only. Wet-lab steps and Cell Ranger commands are **Not found**; many scripts depend on prebuilt RDS objects and user-specific reference paths; no environment lockfile or ordered runner is provided. The code was inspected at commit `29a1812f0f56fa3e307805e087166f76aa1c08a1` but not executed.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
