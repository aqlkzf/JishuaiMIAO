---
layout: default
permalink: /paper-atlas/olfactoryspatialcode-83bd4e32/
title: "OlfactorySpatialCode"
nav: false
wide: true
description: "这篇工作把“嗅觉受体（OR）在嗅上皮的若干宽分区内随机选择”改写成一条更精细的链：细胞所在的背腹（dorsoventral, DV）位置先形成连续的转录身份，这个身份限制它可能选择哪些 OR；同一套身份又携带轴突导向信息，因此鼻腔中的受体地图能与嗅球中的肾小球地图对齐。 这里的关键不是训练一个端到端预测模型，而是把单细胞转录组、空间转录组、谱系追踪、药理扰动、遗传杂交和嗅球空间坐标串成一条因果证据链。"
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
      <span>Spatially Variable Genes</span>
      <span>Cell · 2026</span>
    </div>
    <h1>OlfactorySpatialCode</h1>
    <p>A spatial code governs olfactory receptor choice and aligns sensory maps in the nose and brain</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2026.03.051" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for OlfactorySpatialCode">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/dattalab/Brann_olfactory_dorsoventral" target="_blank" rel="noopener noreferrer" aria-label="Open code for OlfactorySpatialCode">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 《A spatial code governs olfactory receptor choice and aligns sensory maps in the nose and brain》方法解读

### 一句话抓住这篇论文

这篇工作把“嗅觉受体（OR）在嗅上皮的若干宽分区内随机选择”改写成一条更精细的链：细胞所在的背腹（dorsoventral, DV）位置先形成连续的转录身份，这个身份限制它可能选择哪些 OR；同一套身份又携带轴突导向信息，因此鼻腔中的受体地图能与嗅球中的肾小球地图对齐。

这里的关键不是训练一个端到端预测模型，而是把单细胞转录组、空间转录组、谱系追踪、药理扰动、遗传杂交和嗅球空间坐标串成一条因果证据链。

### 1. 研究对象与输入输出

输入主要包括约 230 万个成熟嗅觉感觉神经元（OSN）的单细胞转录组、约 40 万个分化中细胞、MERFISH 和 Stereo-seq 空间数据、克隆条形码、视黄酸（RA）扰动、CAST/EiJ × C57BL/6NJ F1 数据，以及嗅球肾小球三维坐标。每个成熟 OSN 还带有其单一高表达 OR 的身份。

方法最终产生三层输出：

1. 每个细胞的连续 DV 身份；
2. 每个 OR 亚型的平均 DV 地址，即表达该 OR 的细胞通常位于哪里；
3. 从上游 RA 信号到 OR 选择、再到嗅球投射位置的机制解释。

### 2. 核心量：从两个表达程序压成一条 DV 轴

作者先在不包含 OR 基因的高变基因上做共识非负矩阵分解（cNMF），得到若干基因表达程序（GEP）。其中两个程序分别富集背侧和腹侧相关基因。对细胞 $c$：

$$
DV_c = U_{c,\mathrm{Dorsal}}-U_{c,\mathrm{Ventral}},
$$

其中 $U$ 是该细胞对相应 GEP 的 usage。论文中的文字定义和 Figure 1B 支持这一运算。因为分解时排除了 OR，$DV_c$ 不是把“细胞表达哪个 OR”偷偷编码回特征，而是由约 250 个共同变化的非 OR 基因描述其位置身份。

对 OR $r$，再把所有表达它的细胞取平均：

$$
DV_r = \frac{1}{N_r}\sum_{c:\,OR(c)=r}DV_c.
$$

本地实现从预计算 parquet 读取这些量；`load_df_dv()` 默认只保留至少 150 个细胞的 OR 亚型（`code/dv_score/io.py:52-83`），`load_gep_mean()`读取亚型平均 GEP usage（`code/dv_score/io.py:86-112`）。因此这个仓库能重做下游统计，却不能单独从原始表达矩阵重新发现 GEP：cNMF 位于伴随仓库，属于明确的复现边界。

跨条件比较时，代码把分数映射到 0–100 的分位尺度：

$$
DV^{qt}=100\,Q(DV),
$$

其中 $Q$ 是 `QuantileTransformer(random_state=42)`（`code/dv_score/util.py:44-56`）。这保留排序而不保留原始距离，所以“相差 10 个百分点”应读作相对位置差，不应解释为原始 GEP usage 的线性差。

### 3. 为什么它不是旧式“分区模型”

Figure 1 从三个层面建立连续性：OR 亚型平均分数平滑铺满 DV 轴，没有明显的 4–13 个簇；同一 OR 的单细胞分数集中在窄窗口；不同 OR 对仅靠 DV 分数就能较好区分。论文报告跨 363 个样本的 OR 排序相关为 $\rho=0.987$，成对区分的中位 auROC 为 0.96。

代码中的分类检查先筛选 `has_OR`、排除 `opto`，再执行每个 OR 至少 150 个细胞的门槛（`code/scripts/analysis/run_dv_classification.py:80-103`）。成对五折交叉验证使用 `SVC(C=0.5, kernel="rbf")`，而 auROC 本身直接由一维 DV 值计算（同文件 `112-132`）。因此 SVC 准确率和 DV-auROC 是同一脚本中的两项指标，不能混写成“auROC 来自 SVC 概率”。

### 4. 把转录分数锚定到真实组织位置

只有转录梯度还不能证明它是空间坐标。作者用 MERFISH 同时观测 OR 与 DV 基因，在切片中建立共同坐标，并以 DV 基因表达的主成分形成空间侧的 $DV_{ISH}$。Figure 2 显示单细胞 RNA-seq 得到的 $DV_r$ 与 MERFISH 中该 OR 的平均位置高度相关（论文报告 $\rho=0.969$），Stereo-seq 又给出独立复核。

本地 `load_merfish()`读取已经完成细胞识别、对齐和预测的 parquet，并用 `1-pwl_rescale`统一坐标方向（`code/dv_score/io.py:256-283`）。仓库也含空间处理脚本，但共同坐标依赖人工分段，发布数据主要是预计算结果。因此“空间结果可从发布 parquet 重画”是 Exact/Partial 之间的边界；“仅凭本仓库从原始图像全自动重建共同坐标”则不成立。

### 5. 时间顺序：位置身份先于 OR 选择

Figure 3 把约 40 万个细胞沿 GBC → INP → immature OSN → mature OSN 排成伪时间。论文的方法用 scVI 潜空间的近邻图，从一个 GBC 起点迭代传播并排序；DV GEP 在前体阶段已出现，而 OR 选择稍后才从低水平多 OR 共表达进入竞争，最终收敛为单 OR 高表达。

代码的下游摘要只分析伪时间大于 0.4 的 class II OR，并要求足够细胞数（`code/dv_score/differentiation.py:13-35`）。这个 0.4 是检测可靠性的操作阈值，不是某个生物学瞬间的硬边界。

谱系追踪提供第二条证据：同一祖细胞克隆的姐妹 OSN 虽不一定选择相同 OR，却倾向选择 DV 地址相近的 OR。条形码脚本对 14 bp 和 30 bp 区段按 Hamming 距离折叠，并保留可信条形码；`pair_corr()`每次从克隆中抽取两个细胞，做 10,000 次 Spearman 比较并与随机细胞对照（`code/dv_score/lineage.py:11-27`）。这支持“祖细胞继承一个位置许可范围”，但不等于克隆决定唯一 OR。

### 6. 上游信号：RA 改变可供选择的 DV 范围

论文观察到产生 RA 的 ALDH1A2 及 RA 响应沿组织形成梯度，并在损伤再生时用 RA 合成抑制剂、RAR 抑制剂或全反式 RA 做扰动。关键判别是：扰动改变不同 DV 地址 OR 的总体丰度分布，却基本不改变“给定 OR 对应什么细胞 DV 身份”的映射。因此 RA 更像在 OR 选择之前移动/重塑位置身份分布，而不是在选择后改写 OR 标签。

`delta_or()`用宽 100、步长 10 的重叠 DV 窗口统计各条件细胞比例（`code/dv_score/retinoic.py:10-37`）；`log_fc()`按 DV 分位箱计算条件相对对照的 $\log_2$ fold change，并做 100 次有放回 bootstrap 置信区间（同文件 `47-87`）。重叠窗口使曲线平滑，但相邻点高度相关，不能把每个点当成独立检验。

### 7. 中间机制：位置如何约束离散 OR 选择

论文把连续 DV 身份与 OR 选择的已知步骤连接起来：前体先低水平共表达多个候选 OR，随后未被选中的 OR 被异染色质沉默，最终单个等位基因稳定高表达。H3K9me3 在 OR 位点上的富集与 OR 的 DV 地址相关，HP1 蛋白交换实验则显示异染色质机制受扰会使细胞 DV 身份与所选 OR 解耦。

应谨慎区分证据层级：论文的 ChIP-seq、Micro-C 和 HP1 实验支撑这一机制，但本地仓库没有完整的独立处理流水线；相关结果主要存在论文、预计算数据和 notebook 中。因此异染色质桥梁是论文结论，不是本仓库可从原始测序完整复现的模块。

### 8. 顺式遗传证据：同一 OR 名称也能有不同地址

CAST/EiJ 与 C57BL/6NJ F1 中，两条等位基因处在相同细胞环境；若同一 OR 的两个等位基因仍出现不同 DV 地址，更符合顺式序列决定局部可选择性的解释。代码先按 OR 和 strain 计算 GEP 分位均值差（`code/dv_score/cast.py:39-51`），筛选绝对差大于 0.5 且两品系都有足够细胞的 OR，再在每个 OR 内打乱 strain 标签 1,000 次，以第 99 百分位作为阈值（同文件 `54-81`）。

这是一项候选发现与验证流程，不应把所有关联 SNP 都称为因果突变；论文对 Olfr938、Olfr916 等候选的原位证据加强了定位结论，但单个变异的因果性仍需专门编辑实验。

### 9. 从鼻腔地图到嗅球地图

每个 OR 亚型的轴突汇聚到嗅球中较固定的肾小球。作者把每个 OR 的 GEP 特征与三维坐标配对，用弹性网络预测位置。代码特征组包括 DV 的 `Dorsal, Ventral, DV`、AP 的 `Anterior, Posterior, AP`，以及两者组合（`code/scripts/analysis/run_OB_regression.py:22-30`）。模型为：

$$
\hat{\mathbf y}_r=\mathrm{ElasticNet}(\mathbf x_r),\qquad
\mathbf y_r=(x_r,y_r,z_r),
$$

并使用 `StandardScaler`、`alpha=1`、`l1_ratio=0.9`，五折交叉验证重复 1,000 个随机划分（同文件 `32-53`）。Figure 7 表明少数空间 GEP 已能接近用全部高变基因预测的精度。这里证明的是同一转录坐标同时关联鼻腔位置和投射位置；它不单独证明每个轴突导向基因的因果贡献。

### 10. 端到端阅读图

```text
非 OR 高变基因表达
        ↓ cNMF（伴随仓库；本仓库读取预计算 usage）
Dorsal / Ventral GEP usage
        ↓ 相减、按 OR 聚合
细胞 DV 身份 → OR 的平均 DV 地址
        ↓ MERFISH / Stereo-seq
真实嗅上皮位置
        ↑
RA 梯度 → 前体 DV 身份 → 候选 OR 范围
                         ↓ 异染色质/HP1 选择过程
                      单一 OR 身份
                         ↓ 同时携带的轴突导向程序
                    嗅球肾小球三维位置
```

### 11. 论文—代码对应与复现边界

| 环节 | 本地证据 | 判断 |
|---|---|---|
| DV/分位分数读取、亚型门槛 | `dv_score/io.py:52-112`, `util.py:44-56` | Exact（从预计算表开始） |
| cNMF 发现 GEP | 伴随仓库，不在当前代码快照 | Not found here |
| OR 成对区分 | `run_dv_classification.py:80-132` | Exact |
| MERFISH 共同坐标 | 脚本 + 预计算 parquet + 人工步骤 | Partial |
| 分化后续统计 | `differentiation.py:6-35` | Exact；上游伪时间预计算 |
| 克隆相关 | `lineage.py:11-65`、条形码脚本 | Exact/Partial（依赖发布表） |
| RA 分布移动 | `retinoic.py:10-87` | Exact（从发布表开始） |
| F1 置换检验 | `cast.py:39-81` | Exact（依赖等位基因表） |
| H3K9me3、Micro-C、HP1 | 论文与 notebook；无完整独立流水线 | Partial / Not found |
| 嗅球坐标回归 | `run_OB_regression.py:16-80` | Exact（从预计算坐标开始） |
| DV=0 的 MLP 插补 | 发布值存在，模型代码缺失 | Not found |

### 12. 最容易误读的三点

第一，DV score 是连续的转录坐标，不是显微镜直接测得的毫米距离；空间实验负责把它锚定到组织坐标。第二，OR 的平均地址不是说表达该 OR 的所有细胞都在同一点，而是一个窄但非零宽度的分布。第三，RA、异染色质和轴突导向组成的是多实验支持的机制链；当前代码仓库对各段的复现覆盖不均，不能把“论文有证据”与“代码可从原始数据重跑”混为一谈。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary: A Spatial Code Governs Olfactory Receptor Choice

**Brann, Tsukahara et al., Cell 2026**
**DOI**: 10.1016/j.cell.2026.03.051
**Code**: https://github.com/dattalab/Brann_olfactory_dorsoventral

---

### Motivation & Novelty

For 30 years, the olfactory field accepted a "zonal model" (Ressler/Sullivan/Buck 1993, Vassar/Ngai/Axel 1993): ~1,100 OR genes are organized into 4–13 broad zones along the dorsoventral axis of the olfactory epithelium (OE). Within each zone, OR choice is stochastic. The finest version of this model (Zapiec & Mombaerts 2020) had 13 zones. No molecular mechanism was known to specify zone boundaries.

**This paper overturns the model entirely**: OR choice is not random within zones — each of ~1,100 ORs occupies a *unique, continuous* mean DV position in the epithelium, quantifiable as a single scalar "DV score." The result is a fine-grained spatial code where every OR has a stereotyped address, not a broad territory.

**Prior method shortcomings addressed**:
- Zonal models couldn't explain why OR spatial positions are stereotyped across animals; finest model (Zapiec & Mombaerts, Cell Reports 2020) had only 13 zones
- Microdissection + bulk RNA-seq (Tan & Xie, Chem Senses 2018; Ruiz Tejada Segura et al., Cell Reports 2022) provided indirect positional estimates at coarse resolution
- Tsukahara et al. (Cell 2021) identified the same GEPs but interpreted them as activity markers, not spatial organizers

**Key contributions**:
1. Reinterpretation of cNMF GEPs as spatial positional codes, not just activity/zone markers
2. Demonstration that DV identity is established in stem cells *before* OR choice (not after)
3. Identification of the RA gradient as the upstream signal establishing DV identity
4. Proof that heterochromatin (HP1β/H3K9me3) mechanistically translates DV position into OR choice
5. Demonstration that the DV code aligns the nose-to-brain sensory map (OB glomerular positions)

---

### Method Overview

#### Problem Framing

Given ~2.3 million scRNA-seq-profiled OSNs from ~360 replicates, the paper seeks to characterize the continuous transcriptional identity of each OSN along the dorsoventral axis and demonstrate that this identity dictates OR gene selection.

#### Key Ideas

1. **cNMF decomposition** (upstream in Tsukahara et al. 2021): Non-negative matrix factorization of ~1,300 HVGs (ORs excluded) identifies 6 gene expression programs (GEPs). Two GEPs cleanly capture the DV axis: GEP_Dorsal and GEP_Ventral.

2. **DV score** = GEP_Dorsal_usage − GEP_Ventral_usage per cell. A receptor-independent scalar capturing spatial identity. Quantile-normalized to 0–100 percentile scale for cross-condition comparisons.

3. **OR DV score** = mean(DV_score) over all cells expressing OR_i, filtered to subtypes with ≥150 cells. Reproducibility: ρ=0.987 across 363 replicates.

4. **Validation**: MERFISH spatial transcriptomics (300-plex, ~200 ORs + 100 DV genes) confirms OR DV scores predict physical epithelial positions (ρ=0.969). Stereo-seq (ρ=0.986) and 5 external bulk datasets corroborate.

5. **Causal chain**: Retinoic acid (RA) from subepithelial mesenchyme → establishes DV identity in precursors → heterochromatin (H3K9me3) accumulates preferentially on dorsal OR loci (most-often-expressed-and-silenced) → HP1β translates DV position into appropriate OR choice → OR's axon targets specific OB glomerular position (ρ=0.95, ~300 μm error).

#### Computational Pipeline

```
scRNA-seq FASTQs → Cell Ranger → filter_bam → make_adata → scVI (30-latent) →
cNMF (6 GEPs, companion repo) → DV = Dorsal − Ventral → mature OSN filter (vc_thresh=150) →
2.3M OSN parquet → analysis notebooks
```

**Evaluation strategy**:
- AUROC pairwise classification: median 0.96 across 506,521 OR subtype pairs
- Elastic-net regression for OB glomerular positions: 5-fold CV × 1000 restarts, median error ~300 μm
- Spearman correlation for clonal DV similarity (n_boot=10,000)
- Permutation tests for F1 hybrid allele-specific DV shifts (1000 shuffles, 99th percentile)

---

### Evaluation

| Metric | Value | Comparison |
|---|---|---|
| OR DV score reproducibility | ρ = 0.987 | 363 independent replicates |
| MERFISH DV position correlation | ρ = 0.969 | vs. microdissection-derived estimates |
| Stereo-seq vs. MERFISH agreement | ρ = 0.986 | independent technologies |
| Pairwise AUROC (OSN subtype discrimination) | Median = 0.96 | vs. 0.5 shuffled |
| H3K9me3 vs. DV score | ρ = 0.891 | ChIP-seq reanalysis of Bashkirova 2023 |
| OB glomerular 3D prediction (DV alone) | ρ = 0.95, ~350 μm | ElasticNet 5-fold CV × 1000 restarts |
| OB prediction (DV+AP combined) | ~300 μm | Matches all-HVG baseline |
| Clonal DV correlation | ρ ≈ 0.4–0.6 | vs. ~0 shuffled |
| Precursor DV predicts OR choice | ρ = 0.943 | MERFISH INP → mature OSN |

---

### Reproducibility Assessment

**Rating: 2.5/5** — Core claims are reproducible in principle, but reproduction requires significant infrastructure.

**Reproducible with this repo + Zenodo data** (3/5):
- All 7 figure notebooks can be re-run after downloading Zenodo parquets
- DV score loading, quantile normalization, RA analysis, clonal analysis, F1 hybrid permutation tests, OB regression — all implemented in clean Python modules
- `dv_score` package is installable; entry points documented

**Reproducibility gaps** (what prevents full reproduction):
1. **cNMF not included** — The GEP identification requires running the companion repo `Tsukahara_Brann_OSN` on ~5M cells of scRNA-seq (public data, but requires substantial compute). The actual NMF factorization is absent from this repo.

2. **MLP imputation absent** — The PyTorch MLP used to impute DV scores for ~3% of cells with DV=0 is not in the public repo. Only the pre-imputed values are available via Zenodo.

3. **MERFISH pipeline is partial** — Scripts for STalign alignment and DBSCAN cell calling are present, but the common coordinate alignment requires manual segment annotation. Actual results served as pre-computed Zenodo files.

4. **ChIP-seq and Micro-C analyses not included** — H3K9me3 reanalysis (ρ=0.891) and interchromosomal contacts analysis require external datasets and processing pipelines not in the repo.

5. **scANVI requires full 5M-cell dataset** — The reference model and full cell annotation require the complete dataset and compute, neither of which is in the public repo.

**What works very well**:
- All core quantitative analyses (AUROC, OB regression, RA shifts, clonal correlation) are fully reproducible from Zenodo parquets
- Clean code architecture with installable package and clear entry points
- Consistent use of random seeds for all stochastic operations (QuantileTransformer random_state=42, KFold random states, etc.)
- Comprehensive Zenodo data release with 50+ pre-processed parquet files

---

### Biological Insights (Key Findings)

1. **Each of ~1,100 ORs has a unique DV address**: OR choice in the olfactory epithelium follows a continuous positional code, not discrete zones. The 30-year-old "zone model" is replaced by a gradient model.

2. **DV identity precedes OR choice**: DV score is already established in GBCs and INPs before OR selection. The cell's position in the epithelium determines which ORs it can choose — a causally upstream constraint.

3. **RA gradient is the instructive signal**: ALDH1A2 (RA-synthesizing enzyme) is graded in dorsal mesenchyme. Pharmacological RA manipulation bidirectionally shifts OR choice distributions without altering the DV→OR mapping, placing RA upstream of the DV code.

4. **Heterochromatin is the molecular mechanism**: All precursors transiently express dorsal ORs first (early competing phase), then progressively silence them with H3K9me3. Dorsal OR loci accumulate more heterochromatin (ρ=0.891) because they are silenced in most OSNs. HP1β causally enforces this (HP1 swap mice show DV→OR decoupling, not just shifted distribution).

5. **The spatial code aligns nose-to-brain maps**: OR DV scores predict 3D OB glomerular positions (ρ=0.95, ~300 μm error) — tighter than zone-based predictions and as accurate as all-gene models. AP score predicts the OB anteroposterior axis. Together, just 6 GEP values explain the spatial layout of ~1,100 glomeruli in 3D.

6. **Cis-regulation determines DV address**: F1 hybrid experiments with CAST/C57 alleles show specific ORs (Olfr938, Olfr916) have allele-specific DV positions, confirmed by in situ. The allele with higher DV has more H3K9me3. A single upstream SNP in CAST likely explains the shift.

---

### Paper-Code Fidelity: Medium-High

Core analyses (DV score definition, quantile normalization, AUROC, OB regression, RA analysis, clonal correlation, F1 hybrid permutation test, development analysis) are all present and verified. Key gaps: cNMF is upstream (companion repo), MLP imputation is absent, MERFISH alignment is pre-computed, ChIP-seq reanalysis is not included.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
