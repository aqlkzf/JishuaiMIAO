---
layout: default
permalink: /paper-atlas/mousedevvis-f09776c2/
title: "MouseDevVIS"
nav: false
description: "MouseDevVIS 不是只给成年细胞类型拍一张“终点照片”，而是用从胚胎 E11.5 到成年 P56 的密集单细胞时间序列，把成年视觉皮层类型逐步向早期追溯。研究先校正个体发育速度，随后在相邻年龄间转移标签、计算 k 近邻连接并构建轨迹树，再叠加多组学染色质、MERFISH 空间位置、基因表达曲线和 TF–peak–gene 网络，得到“细胞类型从胚胎到出生后持续分叉”的图谱。"
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
      <span>Nature · 2025</span>
    </div>
    <h1>MouseDevVIS</h1>
    <p>Continuous cell-type diversification in mouse visual cortex development</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-025-09644-1" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 小鼠视觉皮层发育中的连续细胞类型多样化：方法解读

### 一句话理解

MouseDevVIS 不是只给成年细胞类型拍一张“终点照片”，而是用从胚胎 E11.5 到成年 P56 的密集单细胞时间序列，把成年视觉皮层类型逐步向早期追溯。研究先校正个体发育速度，随后在相邻年龄间转移标签、计算 k 近邻连接并构建轨迹树，再叠加多组学染色质、MERFISH 空间位置、基因表达曲线和 TF–peak–gene 网络，得到“细胞类型从胚胎到出生后持续分叉”的图谱。

### 论文要解决什么问题

成年皮层含有大量转录组细胞类型。传统观点常把胚胎神经发生看作“类型指定”，把出生后变化看作“成熟”；但过去的数据时间点稀疏，难以区分同一谱系的成熟变化与真正的新类型分叉。标准 pseudotime 工具还容易让强烈的时间梯度压过较细的类型差异。

论文建立 34 个 scRNA-seq 时间点（E11.5–P56）和 13 个 snMultiome 时间点，并用 P0 MERFISH 做空间检查。原始 913,297 个单细胞转录组经质控后保留 568,654 个细胞；331,831 个 Multiome nuclei 中保留 200,061 个高质量 nuclei（论文第 28–54、166–178 行）。

### 整体计算流程

```text
scRNA-seq：34 个年龄，E11.5 → P56
  ↓ QC、去 doublet、去非皮层细胞
给每个细胞估计 synchronized age
  ↓
P56 对齐 ABC-WMB 成年分类
  ↓ 逐个相邻年龄向早期做 RPCA label transfer
年龄 × cluster 的细胞类型图谱
  ↓
相邻年龄 bootstrapped k-NN 连接
  ↓ edge weight > 0.2；每个节点取最大权重边用于主树
完整发育轨迹 + global pseudotime
  ├─ GAM/DE：基因表达时间曲线
  ├─ P0 MERFISH：空间位置验证
  └─ snMultiome：peak、peak module、peak-gene、TF-GRN
```

### 1. synchronized age：先对齐“发育速度”

同一个实际采样日的细胞可能处在略不同的成熟状态。作者首先基于表达结构反复用 k-NN 推断年龄：每轮在 UMAP 空间找 10 个邻居，以距离加权的邻居年龄投票，连续更新 10 轮。代码中先把距离平移、归一化成权重，再用 `impute_knn` 汇总，选最大权重年龄作为下一轮 `pred.age`（`MouseDevVIS/scripts/Label transfer and clustering.RMD:2-57`）。

这一步不是连续时间回归，而是在预定义年龄/年龄箱之间做离散重分配。它减少同批动物发育不同步带来的模糊，但也可能把真实的同龄异质性压进相邻年龄箱，因此后续结果应理解为“转录状态同步年龄”，不是精确生理时钟。

### 2. 从成年向早期逐级转移标签

P56 细胞首先映射到 ABC-WMB 成年小鼠全脑 taxonomy。随后，较老年龄作为 reference、相邻较早年龄作为 query，通过 Seurat RPCA 找 anchor 并传递 cluster label，再继续向更早年龄迭代（论文第 40–54、274–280 行）。

本地 RMarkdown 明确执行：

- reference/query 分别 Normalize、选择变异基因和 PCA；
- `FindTransferAnchors(..., reduction="rpca", dims=1:30)`；
- `TransferData()` 传递 cluster label；
- 为相邻年龄联合整合时使用 2,000 features 和 50 PCs（`Label transfer and clustering.RMD:105-193`）。

这种“相邻年龄接力”比一次性整合所有年龄更能保留细类型，但存在误差逐级累积风险。作者用 scVI 的相邻年龄整合、外部发育数据集和空间数据检查其稳健性，而不是把 label transfer 当作无误差真值。

### 3. 轨迹边如何计算

对于相邻时间 $t_i$（早）和 $t_j$（晚），在联合低维空间中，对晚期每个细胞寻找早期 k 个最近邻。晚期 cluster $C_j$ 指向早期 cluster $C_i$ 的权重可写为：

$$
w(C_j\rightarrow C_i)=
\frac{\#\{C_j\text{ 中细胞的早期邻居属于 }C_i\}}
{\#\{C_j\text{ 中细胞的全部早期邻居}\}}.
$$

代码的 `BuildTrajectory()` 抽样细胞、把数据分成 `pre` 与 `nex`、从晚期向早期调用 `get.knnx`，再按 cluster 计数并逐行归一化成 `tmp2`（`Build_trajectory.R:86-188`）。多次 bootstrap 后取连接权重的稳定汇总；论文保留权重大于 0.2 的候选边，并为每个节点选最大权重边构建简化主树。987 条主边平均权重 0.71，超过 85% 大于 0.5（论文第 56–63 行）。

需要保留的论文—代码差异：论文方法描述 k=50、每轮保留 90% 细胞、100 次 bootstrap；仓库实际调用被现有文档追踪为 k=20、移除 5%（保留 95%）、100 次。函数默认值本身又是 k=5、移除 20%、500 次（`Build_trajectory.R:86`），说明必须看调用参数，不能把函数默认值当作论文参数。

代码还提供 MNN 和 entropy filtering 分支（`Build_trajectory.R:92-124,191-263`），但论文主方法未把它们作为最终轨迹流程，因此它们只能标为附加/推断路径。

### 4. 胚胎与出生后不用同一个时间坐标

出生后细胞以 synchronized age 为主轴；胚胎期同一年龄内部变化很快，作者先用 Monocle3 pseudotime，再应用类似的 k-NN 连接思想。最后把兴奋性/胶质、MGE GABA 和 CGE GABA 三条大轨迹分别累积 cluster centroid 间距离，得到 global pseudotime（论文第 286–303 行）。

这一胚胎 pseudotime 与全局累积算法没有出现在公开代码快照中，不能根据 RMarkdown 中引用的 `monocle.pst.combined` 变量反推为完整实现。公开仓库主要覆盖标签转移、后生期 k-NN 轨迹和基因模块示例。

### 5. 从轨迹树读出“连续多样化”

Fig. 1 展示整个时间轴、taxonomy 层级和年龄 UMAP；Fig. 2–3 把 glutamatergic、GABAergic 和 glia 的分支画成从 progenitor 到成年 cluster 的树。图中大量分支在出生后才出现，而非胚胎期一次性决定：P0 约 40 个 clusters，P8 为 48，P16 为 60，P25 为 93，最终 P56 为 148。

这并不意味着出生前没有 fate bias。更准确的解释是：class/subclass 的粗身份较早可辨，但成人 cluster 级别的转录组差异继续在眼睁开和关键期附近分化。MERFISH 在 P0 验证了 IP、immature neuron 与成熟 subclass 的层状空间位置，例如上层 IT immature neurons 的 subclusters 沿 SVZ 到皮层表面形成迁移梯度（论文第 65–84 行）。

### 6. 基因表达曲线与“变化速度”

作者对 4,973 个发育调控基因拟合 generalized additive model，将其归为 36 种轨迹，再概括为上升、短暂上升、短暂下降、下降和稳定五类（论文第 132–146、304–315 行）。相邻年龄之间还重复抽取细胞做 DE，用 log2 fold-change 的总量衡量各 subclass 的转录变化速度；出生后早期和眼睁开 P10–P15 附近出现明显峰值（Fig. 4–5）。

公开 `Identification of gene modules.RMD` 覆盖按年龄内 class 和按 class 内年龄的双向 pairwise DE，筛选 `rank < 15`、`lfc > 1.5`，并调用外部 `scrattch.bigcat`（第 23–87 行）。基因模块示例调用 `get_gene_mod(..., k=10, resolution=8)`（第 90–113 行），而论文不同模块处描述 k=5 或 resolution=2；这些对象与参数不能混为同一个分析。

### 7. 多组学如何连接 peak、gene 和 TF

snMultiome 同一 nucleus 给出 RNA 与 ATAC。作者用 scVI 把 Multiome RNA 映射到 scRNA taxonomy，用 ArchR 对 subclass、cluster 和年龄组合的 pseudobulk call peaks，共得 882,075 个 peaks；随后用 pairwise Chi-squared test 找 differential accessibility，按细胞类型与时间模式聚成 peak modules（论文第 166–187 行）。

若一个差异 peak 与 5 Mb 窗口内的差异基因在 subclass×age 组之间相关系数大于 0.5，就构成候选 peak–gene 对。SCENIC+ 风格的网络进一步结合 TF motif、TF expression、peak accessibility 与 target expression，形成 TF–peak–gene triplet，并区分激活与抑制方向（论文第 188–215、370–409 行）。

Fig. 6 的 RNA/ATAC UMAP 和 accessibility heatmaps 说明两模态的标签对应；Fig. 7 把 motif enrichment、peak module 时间模式与 GRN 网络并排显示。这些主分析代码（scVI、ArchR、SCENIC+ 改写）不在 MouseDevVIS 的四个脚本中，因此属于论文证据而非代码复现证据。

### 8. 眼睁开不是唯一原因，但构成明显转折

Fig. 5 显示许多 neuronal subclasses 在 P10–P15 附近有大量 DE，Multiome 也检测到睁眼前后 32,865 个差异 peaks。活动相关 AP-1 因子和不同细胞类型的 TF 网络随时间改变。但该研究是发育时间序列，不是把所有动物随机分配为“睁眼/不睁眼”的因果干预；因此“眼睁开附近变化”是强时间关联，不能把所有变化都归因于视觉经验。

### 如何读七张主图

- **Fig. 1**：数据规模、时间覆盖、taxonomy 和同步年龄后的全局结构。
- **Fig. 2**：早期 subclass 轨迹与 P0 MERFISH 空间位置。
- **Fig. 3**：glutamatergic、GABAergic、glial 的完整 cluster 分支树。
- **Fig. 4**：基因表达的 36 种时间模式及成年 marker 的早期可预测性。
- **Fig. 5**：cluster 数和 DE 变化速率，突出眼睁开附近的动态。
- **Fig. 6**：scRNA 与 snMultiome 对齐，以及 chromatin peak modules。
- **Fig. 7**：motif、peak module 与 TF–target GRN。

这些判断来自对 `paper.pdf` 主图页的直接检查；图像支持与局限详见 `figure_analysis.md`。

### 复现边界

公开仓库对“同步年龄 → 相邻年龄 RPCA label transfer → bootstrapped k-NN 轨迹 → DE/基因模块”提供了有价值的代表代码，但含 Allen 内部绝对路径，并依赖大型数据对象与 `scrattch.bigcat`。SCENIC+、ArchR、scVI、MERFISH、Monocle3 embryonic pipeline 和多数最终图表代码缺失。

因此，最可靠的学习结论是：论文以密集真实时间采样约束轨迹，再用空间和染色质信息交叉验证，支持视觉皮层细胞类型在胚胎和出生后连续分化；但公开代码只能部分复现这条证据链，不能把 repository availability 等同于 end-to-end reproducibility。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Continuous Cell-Type Diversification in Mouse Visual Cortex Development

### Motivation & Novelty

The mammalian cortex contains ~100 transcriptomic cell types per area, hierarchically organized into classes and subclasses, yet when and how these types emerge during development remains poorly understood. Previous single-cell studies of cortical development offered limited temporal resolution: Di Bella et al. (*Nature*, 2021) covered E10–P4, La Manno et al. (*Nature*, 2021) spanned E7–E18, and Telley et al. (*Science*, 2019) profiled four sequential neuronal cohorts. Standard trajectory inference tools (Monocle3: Cao et al., *Nature*, 2019; PAGA: Wolf et al., *Genome Biol.*, 2019; Slingshot: Street et al., *BMC Genomics*, 2018; RNA Velocity: La Manno et al., *Nature*, 2018) could not resolve developmental trajectories at the desired cell-type specificity, as they conflated temporal gradients with cell-type heterogeneity.

**Unique contributions of this study:**

1. **Unprecedented temporal density**: 34 time points from E11.5 to P56 for scRNA-seq (568,654 cells) and 13 time points for snMultiome (200,061 nuclei) — the densest sampling of cortical development to date
2. **Complete developmental trajectory map**: All excitatory, inhibitory, and non-neuronal cell types traced from progenitors to adult, with precise branching point timing and marker genes at each divergence
3. **Continuous diversification model**: Demonstrates that cell-type diversity is not established during embryonic neurogenesis but continues through postnatal development, with bursts of new types at eye opening (P11-14) and critical period (P21)
4. **Integrated epigenomic landscape**: Matched chromatin accessibility (snATAC-seq) with gene expression across cell types and ages, identifying 882,075 peaks, cell-type-specific peak modules, and peak-gene pairs
5. **Cell-type and temporally resolved GRNs**: SCENIC+-based identification of TF-peak-gene regulatory triplets that link transcription factors to downstream targets through accessible chromatin motifs

The paper fundamentally shifts the prevailing view from "cell types are specified embryonically and mature postnatally" to "cell-type diversification is a continuous process, with the majority of transcriptomic clusters emerging postnatally."

---

### Method Overview

The computational framework combines two parallel data modalities into a unified developmental atlas:

#### Transcriptomic Atlas (scRNA-seq)
- **QC**: 913,297 → 568,654 cells after stringent filtering (gene detection, QC score, doublets, non-cortical cells)
- **Synchronized age**: Iterative k-NN (k=10, 10 iterations) to normalize biological variability across collection times
- **Taxonomy**: Sequential Seurat RPCA label transfer from P56 (ABC-WMB Atlas reference) → younger ages; embryonic cells mapped to published developmental references
- **Trajectory**: Bootstrapped k-NN between adjacent age bins (postnatal) and Monocle3 pseudotime (embryonic); 987 main trajectory edges with average weight 0.71
- **Result**: 15 classes → 40 subclasses → 148 clusters → 714 subclusters

#### Epigenomic Atlas (snMultiome)
- snRNA-seq labels transferred from scRNA-seq taxonomy via scVI integration
- ArchR peak calling (882,075 peaks) per subclass × age group
- DA peaks via Chi-squared test; peak modules via Jaccard-Leiden clustering
- Peak-gene linkage: 5 Mb window, correlation >0.5
- GRN inference: Modified SCENIC+ framework identifying TF-peak-gene triplets

#### Spatial Validation (P0 MERFISH)
- 500-gene panel designed for P0 cell-type classification (98% subclass, 85% cluster accuracy)
- Custom Cellpose segmentation with human-in-the-loop training
- Validates spatial distribution of developmental cell types at P0

See `doc_method.md` for the full algorithm walkthrough, variable mapping, and implementation details. See `doc_code.md` for code-paper correspondence.

---

### Evaluation

#### Datasets

| Dataset | Cells/Nuclei | Time Points | Technology |
|---------|-------------|-------------|------------|
| scRNA-seq | 568,654 (QC) | 34 (E11.5–P56) | 10x v3 |
| snMultiome | 200,061 (QC) | 13 | 10x Multiome (RNA+ATAC) |
| P0 MERFISH | ~913K cells | P0 | Vizgen MERSCOPE (500 genes) |

#### Validation Approaches

1. **Taxonomy robustness**: scVI and Seurat RPCA integration compared between adjacent age bins — highly consistent results (Supplementary Fig. 1). Nine scVI model settings (varying n_hidden, n_layer, n_latent, HVG count) all produce similar results.

2. **External dataset integration**: Integrated with Di Bella et al., La Manno et al., and Telley et al. using scVI + random forest (Extended Data Fig. 4). Cell-type assignment broadly consistent across studies at subclass level.

3. **Cross-validation of cell-type predictability**: Fivefold cross-validation at each postnatal age using adult marker genes (Fig. 4c). Median subclass recall is generally high even at P0, demonstrating that subclass identities are present (though less distinct) from birth.

4. **MERFISH spatial validation**: P0 MERFISH confirms spatial distributions predicted by trajectory analysis — e.g., IMN IT upper-layer subclusters show graded cortical depth consistent with radial migration progression (Fig. 2e).

5. **MET-type correspondence**: Developmental trajectory groups match Patch-seq MET-types (Gouwens et al., *Cell*, 2020; Extended Data Figs. 9d, 10d), linking transcriptomic trajectories to morphoelectric properties.

6. **Trajectory confidence**: Edge weights quantified via bootstrapping (100 replications). Main trajectory edges average 0.71 weight; >85% have weight >0.5. Non-selected edges average 0.29 (all <0.5).

#### Key Quantitative Results

- **Cluster counts over time**: 40 clusters at P0 → 48 at P8 → 60 at P16 → 93 at P25 → 148 at P56
- **Gene trajectory patterns**: 4,973 developmentally regulated genes clustered into 36 temporal patterns
- **Eye-opening DE genes**: 1,200–2,000 DE genes per glutamatergic subclass; all subclasses show significant changes
- **Chromatin peaks**: 882,075 total; 32,865 DA between P7-10 and P11-15; more increasing peaks in IT subclasses after eye opening
- **GRN TF families**: bHLH, MEF2, SOX, POU, AP-1, nuclear receptors identified as key developmental regulators

---

### Reproducibility

**Rating: 3/5** (Moderate — data fully available, code partially available)

#### Strengths
- **Data availability**: All raw data deposited in BICAN and NeMO archives; processed h5ad files available on AWS S3
- **Detailed methods**: >5,000 words of methods with specific parameters for every analysis step
- **External validation**: Integration with 3 published datasets and MERFISH spatial validation
- **Supplementary tables**: 10 comprehensive tables covering all metadata, DE genes, trajectory edges, peak-gene pairs, and GRN triplets
- **Consistent reference**: Uses the well-established ABC-WMB Atlas as the adult reference taxonomy

#### Weaknesses
- **Incomplete code repository**: MouseDevVIS contains only 4 R scripts covering ~3 of ~10 major analyses. The SCENIC+ reimplementation, ArchR peak analysis, scVI integration, Monocle3 pseudotime, and MERFISH processing are absent.
- **scrattch.bigcat dependency**: Core analyses rely on this Allen Institute R package, which is publicly available but complex and poorly documented
- **Hardcoded paths**: All scripts reference Allen Institute internal filesystem paths (/allen/programs/celltypes/...)
- **Parameter discrepancies**: k-NN trajectory uses k=20 in code but paper says k=50; bootstrap retention is 95% in code vs. 90% in paper; gene module resolution is 8 in code vs. 2 in paper
- **Computational requirements**: Processing 568K cells with iterative clustering, PCA projection, and pairwise DE requires substantial memory (~100GB+) and compute time
- **No workflow orchestration**: No Snakemake/Nextflow/Makefile; analysis steps are in RMarkdown notebooks with manual execution order

#### Practical Notes for Reproduction
1. Install scrattch.bigcat (R, from GitHub: AllenInstitute/scrattch.bigcat) and scrattch.mapping
2. Processed h5ad files (~several GB each) available from S3 — start with these rather than raw data
3. For peak calling: need ArchR (R) and the ATAC fragment file (~large download)
4. scVI integration and random forest classification require Python (scvi-tools, scikit-learn)
5. Monocle3 for embryonic pseudotime is a standard R package installation
6. JASPAR 2024 CORE non-redundant motif database needed for TF motif analysis

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
