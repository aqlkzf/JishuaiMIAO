---
layout: default
permalink: /paper-atlas/gbm-tme-74bb430b/
title: "GBM_TME"
nav: false
description: "这项研究把单细胞 RNA、空间转录组、单细胞 ATAC、原位杂交和 Patch-seq 叠加在同一套细胞类型参考上，不只问“胶质母细胞瘤（GBM）里有哪些细胞”，而是问“哪些细胞稳定地住在一起、如何相互作用”。跨 32 张空间切片，作者归纳出 4 个可重复的恶性 cellular communities（CCs），进一步区分两种 MES-like 肿瘤细胞生态位，并用电生理证明形成神经胶质瘤突触的肿瘤细胞主要是 OPC-like 状态。"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature Neuroscience · 2026</span>
    </div>
    <h1>GBM_TME</h1>
    <p>Spatial and single-cell characterization of human glioblastoma tumor microenvironment reveals malignant cellular communities</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41593-026-02265-5" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GBM_TME：人胶质母细胞瘤恶性细胞群落的空间多组学解读

### 一句话理解

这项研究把单细胞 RNA、空间转录组、单细胞 ATAC、原位杂交和 Patch-seq 叠加在同一套细胞类型参考上，不只问“胶质母细胞瘤（GBM）里有哪些细胞”，而是问“哪些细胞稳定地住在一起、如何相互作用”。跨 32 张空间切片，作者归纳出 4 个可重复的恶性 cellular communities（CCs），进一步区分两种 MES-like 肿瘤细胞生态位，并用电生理证明形成神经胶质瘤突触的肿瘤细胞主要是 OPC-like 状态。

### 为什么需要空间多组学

GBM 内的 malignant cells 可处于 MES-like、AC-like、OPC-like 和 NPC-like 状态，同时混有 TAM、单核细胞、血管细胞、T 细胞和神经元。scRNA-seq 能识别细胞状态，却丢失邻接关系；Visium 保留位置，但每个 spot 混合多个细胞。论文因此用单细胞图谱定义“成分”，用空间数据定义“位置”，再用单细胞分辨率 ISH、PhenoCycler 和 Patch-seq 验证关键预测。

研究整合 17 名患者的 30,725 个新 scRNA cells、公开 scRNA/snRNA 数据，得到 85,597 个高质量 cells/nuclei；Harmony 与 Seurat 得到 25 类细胞，inferCNV 标出 36,247 个 malignant cells（论文第 31–43 行）。

### 主流程

```text
scRNA/snRNA reference：25 种细胞 + 4 种 malignant states
             ↓
cell2location：把细胞类型丰度分解到 32 张 Visium 切片
             + chr7 gain / chr10 loss CNV 特征
             ↓
SPACEL/Splane：跨切片对齐 10 个 recurrent spatial domains
             ↓
低 CNV 的 D9/D10 = peritumoral
其余 malignant domains → 4 个 cellular communities (CC-1…CC-4)
             ↓
MES 亚型、trajectory、TF、ligand–receptor、synapse 分析
             ↓
ISH / PhenoCycler / organoid / Patch-seq 正交验证
```

### 1. 从混合 spot 到跨患者空间群落

cell2location 以 scRNA reference 估计每个 Visium spot 的细胞类型组成。随后 Splane 同时使用细胞丰度、空间坐标和 chr7/chr10 CNV，把 32 张切片对齐到 10 个 recurrent domains（论文第 41–47、452–459 行）。D9/D10 CNV 低且富集正常神经/胶质细胞，被认作瘤周区；恶性 domains 再按组成归成四个 CC。

公开 `Fig1_Splane_with_CNV.py` 直接读取 cell2location 结果和 CNV，归一化并裁剪极端丰度，加入 23 个 cell types 与 chr7/chr10，然后调用：

```python
Splane.init_model(..., n_clusters=c, k=k, gnn_dropout=gnn_dropout)
splane.train(d_l=d_l)
splane.identify_spatial_domain()
```

对应代码见 `GBM/Fig1_Splane_with_CNV.py:1-103`。关键边界是：cell2location 与 inferCNV 的生成流程不在仓库，脚本读取作者内部绝对路径中的预计算结果；所以 domain calling 可追踪，端到端输入构建不可复现。

Fig. 1 从 UMAP、domain composition、跨切片 domain 关系到 ISH 单细胞地图，支持四个 CC 不是单张切片的偶然 cluster。它们是统计上重复出现的邻域模式，不应理解为每个肿瘤都有清晰且互斥的四块组织。

### 2. MES-Hyp 与 MES-Ast：同一状态的两个生态位

作者对 19 名患者的 18,139 个 MES-like cells 分患者做 Leiden clustering，收集能稳定区分 cluster 的 gene sets，筛出 54 个程序，再聚成两个跨患者模块（论文第 75–94、468–475 行）：

- **MES-Hyp**：NDRG1、ERO1A、VEGFA、LIF、IL11 等缺氧/细胞因子程序，主要位于 CC-1，并靠近 TAM5-GPNMB 与单核细胞；
- **MES-Ast**：COL1A1/COL1A2、CHI3L1、GAP43 等基质/astrocyte-like 程序，更常见于血管丰富的 CC-2，也分布于 CC-4。

高分辨率 ISH 以组合 marker 而非单一基因定义细胞，并把图像分成 192 μm 窗口按成分聚类。MES-Hyp 与 TAM5-GPNMB 的共定位、MES-Ast 与 endothelial/pericyte 的共定位均显著。Fig. 2 的 gene-program heatmap、ISH 图与 window composition 将“表达亚型”连接到“空间生态位”。公开实现主要是 notebooks，适合标为 Notebook 证据，不能因文件存在就称逐行 Exact。

### 3. 肿瘤状态转换：关联轨迹而非直接谱系

Palantir/PHATE 在 scRNA 和公开 scATAC 中都得到 AC-like → MES-Ast → MES-Hyp 的连续变化，Tangram 映射后 scVelo arrows 多指向富含 MES-Hyp 的 CC-1（论文第 95–103、476–491 行；Fig. 3）。缺氧 organoid 实验也推动 MES-Ast 向 MES-Hyp signature 转移。

这些结果支持 MES-Ast 是向缺氧 MES 状态过渡的候选中间状态，但 pseudotime 是转录/染色质相似性排序，不是同一细胞的真实时间追踪。起始细胞由高 MKI67 或 cell-cycle score 选择，也带有分析者设定。

### 4. 单核细胞如何转向 TAM5-GPNMB

作者新生成 6,736 个高质量 scATAC cells，用 ArchR gene score 与 Signac 将其锚定到 scRNA 类型，再将 scATAC 通过 Tangram 放回空间。RNA 与 ATAC 的 Palantir 都支持 monocyte → TAM5-GPNMB 轨迹；沿轨迹同时上升的 RNA expression、chromVAR motif deviation 和 SCENIC regulon activity 给出 9 个候选 TF（论文第 171–184、480–505 行；Fig. 4）。

空间 TF 活性用细胞组成加权：

$$
D_{st}=\frac{\sum_i d_{it}P_{si}}{\sum_i P_{si}},
$$

其中 $d_{it}$ 是细胞类型 $i$ 对 TF motif $t$ 的平均 deviation，$P_{si}$ 是 spot $s$ 中该细胞类型的映射丰度。它是线性混合近似：能把单细胞 ATAC 投到空间，但假设同一 cell type 的 TF activity 不随局部位置产生额外变化。

### 5. CC 内的 ligand–receptor 网络

COMMOT 把配体/受体表达和空间距离结合，作者要求 LR pair 在至少 20% 的 32 张切片中对某 CC 显著增强，得到 CC-1/2/3/4 分别 37、300、50、13 个 pairs（论文第 185–200、508–515 行）。细胞亚型间连接分数是：

$$
\text{connectivity}_{ij,LR}=
\overline e_{L,i}\,\overline e_{R,j}\,S_{LR,spatial}.
$$

它同时要求 sender 有 ligand、receiver 有 receptor，且空间模型认为该 pair 有通信强度。Fig. 5 的 quadrant、triangle heatmaps 与 PhenoCycler 图显示 CC-specific networks；但这仍是通信优先级，不等于分子结合或功能因果。作者用 organoid 中 TGFβ2/VEGFA 干预等实验补强部分通路，而非验证全部 LR pairs。

### 6. 哪一种 GBM 细胞真正接收神经输入

CC-3 富集神经元与 OPC-like/NPC-like/AC-like cells，预测 NRXN–NLGN、NPTX2–GRIA 等突触相关通信。作者对新鲜 GBM 切片做 whole-cell recording 后收集细胞做 Smart-seq2：21 个细胞中 10 个有 spontaneous EPSCs；这 10 个全部由 Seurat anchors 和 SCANVI 分到 OPC-like malignant cluster（论文第 201–289、516–519 行）。

Fig. 6 把整片空间图、Patch-seq traces、cell-type UMAP 和频率/振幅统计放在一起，是全文最强的“计算预测 → 功能测量”证据。结论应限定为本队列中 sEPSC-positive cells 均为 OPC-like，不宜外推成所有 OPC-like cells 都形成突触。

### 如何读主图

- **Fig. 1**：25 类细胞、10 domains 与 4 CCs 的定义及 ISH 验证。
- **Fig. 2**：MES-Hyp/MES-Ast gene programs 与不同邻域。
- **Fig. 3**：RNA、ATAC、空间三种视角下的 tumor-state transition。
- **Fig. 4**：monocyte→TAM5 的 RNA/ATAC trajectory 与 TF candidates。
- **Fig. 5**：四个 CC 的 LR networks 和多重成像验证。
- **Fig. 6**：OPC-like synaptic input 的 Patch-seq 功能证据。
- **Fig. 7**：把 CC-1 缺氧免疫、CC-2 血管、CC-3 neuronal、CC-4 proliferative interaction 汇总为模型。

这些内容来自对 `paper.pdf` 主图页的直接检查；逐 panel 说明见 `figure_analysis.md`。

### 代码与复现边界

仓库提供 1 个 Python domain-calling 脚本和多个 figure notebooks，覆盖 Splane、MES programs、trajectory、COMMOT、空间 ATAC 和 Patch-seq label mapping 的后半段。核心 scRNA/Harmony、inferCNV、cell2location、ISH image processing、电生理统计及若干实验分析缺失；notebooks 还依赖 Zenodo 大对象和预训练模型。

因此，这项工作的主要方法贡献是跨模态、跨尺度的证据拼接，而不是单一新算法。最稳妥的使用方式是把四个 CC 当作跨患者可复现的空间组织框架，并对具体 trajectory、TF 或 LR 因果解释保留模型和验证范围。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## GBM_TME Summary

### Paper
**Title**: Spatial and single-cell characterization of human glioblastoma tumor microenvironment reveals malignant cellular communities
**Journal**: Nature Neuroscience | **Year**: 2026
**DOI**: 10.1038/s41593-026-02265-5
**Authors**: Jun Lin, Chunpeng Chen, Shouzhen Li, et al. (Kun Qu lab, USTC)

---

### Motivation & Novelty

**Biological problem**: Glioblastoma (GBM) is the most prevalent malignant primary brain tumor, with a median survival of ~15 months despite surgery, radiotherapy, and chemotherapy. Treatment failure is driven by extreme cellular heterogeneity and a complex immunosuppressive tumor microenvironment (TME). While single-cell sequencing had identified four canonical malignant cell states (MES-like, AC-like, OPC-like, NPC-like; Neftel et al., *Cell* 2019), the *spatial organization* of these cells — who lives next to whom, and how neighboring cells communicate — was unknown at population scale.

**Limitations of prior approaches**:
- Neftel et al. (*Cell* 2019): single-cell classification of tumor states but no spatial context
- Greenwald et al. (*Cell* 2024): identified multi-layered spatial organization in GBM but with limited cohort size
- Ravi et al. (*Cancer Cell* 2022): spatially resolved multi-omics but focused on 12 samples from one dataset
- Prior MES-like characterization used limited single-cell or low-resolution ST data; MES heterogeneity was under-explored
- Neurogliomal synapses (Venkataramani et al., *Nature* 2019; Venkatesh et al., *Nature* 2019) were established but the specific tumor cell subtype responsible was unknown

**What's new**:
1. **Largest integrated GBM spatial atlas**: 100 patients, 121 data profiles, 6 modalities — enabling detection of conserved patterns that small cohorts miss
2. **Four malignant cellular communities (CCs)**: Recurrent, patient-invariant spatial neighborhoods with consistent cell type compositions, gene expression, and intercellular interactions
3. **MES-Hyp vs. MES-Ast subpopulations**: Comprehensive characterization of two functionally distinct MES-like subtypes with defined niches, validated at single-cell resolution by ISH
4. **Transcriptional regulation of TAM5-GPNMB**: Nine TFs (SREBF1, MAFB, + 7 others) identified driving monocyte → pro-tumoral macrophage polarization, with spatial chromatin accessibility evidence
5. **OPC-like tumor cells form neurogliomal synapses**: Patch-seq directly demonstrates that sEPSC-positive GBM cells are exclusively OPC-like; GDF11-ACVR1B feedback mechanism proposed
6. **SPACEL Splane with CNV augmentation**: CNV scores from inferCNV integrated as spatial features to separate malignant from peritumoral domains

---

### Method Overview

The paper deploys a multi-stage integration pipeline rather than a single novel algorithm.

#### Data scale
| Modality | Samples | Cells/Spots |
|---|---|---|
| scRNA-seq + snRNA-seq | 53 patients | 118,639 cells |
| ST (10x Visium) | 27 patients | 78,944 spots (32 slices) |
| scATAC-seq | 20 patients | 20,650 cells (6,736 in-house) |
| ISH (padlock probe + RCA) | 8 patients | 340,568 cells |
| Patch-seq (Smart-seq2) | 7 patients | 21 cells |

#### Core analytical steps
1. **scRNA-seq atlas**: Harmony batch correction + Seurat V4 clustering → 25 cell types; InferCNV → 36,247 malignant cells → Neftel classification → 4 tumor subtypes
2. **Spatial domain identification**: cell2location deconvolution (25 cell types) → SPACEL Splane GNN with CNV augmentation → 10 domains across 32 slices → 4 CCs
3. **MES subtype identification**: Patient-level Leiden clustering → 54 gene sets (DEG>50, FC>2) → 2 clusters (MES-Hyp, MES-Ast); validated by ISH at single-cell resolution
4. **Tumor cell trajectories**: PHATE + Palantir pseudotime (scRNA-seq and scATAC-seq independently) + scVelo spatial velocity → AC-like → MES-Ast → MES-Hyp, driven by hypoxia
5. **TF regulation**: ArchR gene scores + Signac → chromVAR TF motif deviations + SCENIC regulon activity → 9 TFs along monocyte→TAM5-GPNMB trajectory; spatial TF mapping using $D_{st} = \sum d_{it} P_{si} / \sum P_{si}$
6. **LR interactions**: COMMOT (v0.0.3, 200µm constraint) + CellChat library → CC-specific LR pairs (FDR<1×10⁻²⁰, FC>1.25, in ≥20% slices) → connectivity score = ligand × receptor × spatial strength
7. **Experimental validation**: ISH (single-cell resolution), PhenoCycler multiplex imaging (21-antibody panel), GBO perturbation assays (TGFβ2/VEGFA), Patch-seq electrophysiology + transcriptomics

See `doc_method.md` for full algorithm walkthrough.

---

### Evaluation

#### Spatial domain reproducibility
- High correlations between spatial domains across slices: "high correlations in gene expression and cellular composition between spatial domains" (Extended Data Fig. 2c)
- D9/D10 peritumoral domains confirmed by H&E staining and CNV levels (P=0.0 by Wilcoxon test)

#### MES subtype validation
- ISH with 36-gene panel: MES-Hyp ($\text{CD44}^+, \text{LIF}^+, \text{COL1A2}^-$) vs. MES-Ast ($\text{CD44}^+, \text{COL1A1}^+, \text{COL1A2}^+, \text{LIF}^-$) — confirmed distinct spatial distribution
- Colocalization statistics: MES-Hyp with TAM5-GPNMB P=4.3×10⁻⁹; MES-Ast with vascular cells P=0.00012

#### Cell interaction validation
- PhenoCycler on 6 patients with 21-antibody panel confirms: NDRG1⁺ MES-Hyp near GPNMB⁺ TAM5; COL1A2⁺ MES-Ast near ITGA1⁺ endothelial; NRXN1⁺ neurons near NLGN3⁺ OPC-like
- Spatial permutation tests: CC-1 P=3.7×10⁻¹⁷², CC-2 P=7.4×10⁻¹⁴⁹, CC-3 P=1.4×10⁻¹⁰⁹ (1000 random label permutations)
- GBO perturbation: TGFβ2 treatment increases endothelial/pericyte proliferation (17.5% vs 12.6% in P244; 38.4% vs 18.8% in P245)

#### Patch-seq validation
- 10/10 sEPSC-positive cells = OPC-like (confirmed independently by Seurat anchors and scArches/SCANVI)
- sEPSC frequency lower in OPC-like vs neurons: P=9.9×10⁻⁴
- sEPSC amplitude lower: P=0.042
- GDF11 treatment of primary rat neurons: significant increase in PSD-95 and synaptophysin fluorescence
- Concordance with HC cells in low-grade glioma (Curry et al., *Cancer Cell* 2024)

#### Datasets used
- In-house: 20 IDH wild-type patients for scRNA-seq/scATAC-seq/ST/ISH/Patch-seq (USTC First Affiliated Hospital)
- Public scRNA-seq: Couturier et al. (*Nat Commun* 2020), Wang et al. (*Cancer Cell* 2021)
- Public ST: Ravi et al. (*Cancer Cell* 2022) n=12, Mei et al. (*Nat Cancer* 2023) n=7, Ren et al. (*Nat Commun* 2023) n=2, 10x dataset n=1
- Public scATAC-seq: Sundaram et al. (*Science* 2024) n=9
- GBmap database: Ruiz-Moreno et al. (*Neuro Oncol* 2025) for 92,256 malignant cells

---

### Reproducibility Rating: 3/5

**Justification**: The paper provides extensive methodological detail, all software versions, and data availability (Zenodo + NGDC). The code repository covers 9 key analytical notebooks. However:

**Strengths**:
- All processed data available (Zenodo 10.5281/zenodo.8085502)
- Pre-trained SCANVI model available (Zenodo 10.5281/zenodo.15699049)
- All software tools are publicly available with versions specified
- Code covers all major figure-level analyses (Figs 1–6)

**Weaknesses/Caveats**:
- Core preprocessing is absent from code: cell2location deconvolution pipeline, ISH preprocessing (ASHLAR/DeepCell/Starfish), scRNA-seq Harmony integration scripts — these require independent implementation
- Pseudotime starting point (MKI67-high cell; cycle-high cell) is manually selected; not scripted
- "Ecoregion" → "Cellular Community" naming change not reflected in code — confusing for reproducers
- Multi-round ISH is a specialized protocol requiring padlock probe synthesis (Sangon Biotech) and custom imaging setup — not easily reproduced without the original equipment
- Patch-seq requires fresh surgical tissue and electrophysiology expertise — practically limited to neurosurgical centers
- No conda/pip environment file; versions listed in Methods/README but no lockfile

**Practical entry point**: Download Zenodo data → run `Fig1_Splane_with_CNV.py` to reproduce spatial domain calling; use `Fig2_*` notebooks for MES subtype and trajectory analyses; `Fig4_*` for LR interactions; `Fig5_*` for TF accessibility; `Fig6_*` for Patch-seq cell typing.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
