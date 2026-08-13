---
layout: default
permalink: /paper-atlas/clonalscope-b5f65896/
title: "Clonalscope"
nav: false
wide: true
description: "Clonalscope 的目标不是把表达相似的细胞分群，而是从 scRNA-seq、scATAC-seq 或空间转录组这类“没有直接测 DNA”的数据中，尽量恢复由 DNA 拷贝数改变（CNA）定义的癌症亚克隆。 它先把高维、噪声很大的基因计数压缩为“细胞/spot × 基因组区段”的相对覆盖度矩阵，再用嵌套 Chinese Restaurant Process（CRP）同时决定：应该有多少个亚克隆、每个细胞属于哪个亚克隆，以及新亚克隆…"
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
      <span>Computational Tools</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Clonalscope</h1>
    <p>Cancer subclone detection based on DNA copy number in single-cell and spatial omic sequencing data</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/seasoncloud/Clonalscope" target="_blank" rel="noopener noreferrer" aria-label="Open code for Clonalscope">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Clonalscope 方法详解

### 一句话理解

Clonalscope 的目标不是把表达相似的细胞分群，而是从 scRNA-seq、scATAC-seq 或空间转录组这类“没有直接测 DNA”的数据中，尽量恢复由 DNA 拷贝数改变（CNA）定义的癌症亚克隆。

它先把高维、噪声很大的基因计数压缩为“细胞/spot × 基因组区段”的相对覆盖度矩阵，再用嵌套 Chinese Restaurant Process（CRP）同时决定：应该有多少个亚克隆、每个细胞属于哪个亚克隆，以及新亚克隆在哪些区段采用已有或新生的拷贝数状态。

### 为什么普通表达聚类不够

scRNA-seq 和 scATAC-seq 中的染色体级信号只是 DNA 拷贝数的间接代理。细胞谱系、转录调控或染色质重塑也可能造成大片连续区域的表达/可及性偏移，因此“表达不同”不等于“DNA 亚克隆不同”。

已有方法的主要限制是：

- inferCNV（相关方法发表于 *Science*, 2014）和 CopyKAT（*Nature Biotechnology*, 2021）主要依靠相邻基因平滑，并通常再做层次聚类；它们不直接把配对 bulk DNA 的 CNA 轮廓作为亚克隆先验。
- HoneyBADGER（*Genome Research*, 2018）与 CaSpER（*Nature Communications*, 2020）利用等位基因信息，但稀疏的 allele-specific reads 限制了收益。
- STARCH（*Physical Biology*, 2021）利用邻近空间 spot 稳定 CNA 推断；这会引入空间平滑假设，而 Clonalscope 刻意不让坐标参与亚克隆聚类。
- CONICS（*Bioinformatics*, 2018）能使用配对 DNA 分段，但面向全长 scRNA-seq，也没有 Clonalscope 这种从未知亚克隆数出发的嵌套非参数模型。

层次聚类还需要人为选择切树位置，并且在低信噪比的 segment-level CNA 矩阵上容易不稳定。Clonalscope 把“是否产生新亚克隆”和“新亚克隆是否产生新的区段状态”都写进概率模型。

### 输入与输出

输入可以包括：

- scRNA-seq、scATAC-seq 或 ST 的基因/特征 × 细胞/spot 计数矩阵；
- 基因坐标与基因组大小；
- 一小组高置信度二倍体正常细胞/spot；
- 可选的配对 WGS/WES、pseudobulk scDNA-seq 分段及 CNA 状态；
- 等位基因模式下，由 Alleloscope 等工具得到的 coverage 与 major-haplotype proportion 矩阵。

核心输出是：

- 亚克隆数 (K)；
- 每个细胞/spot 的亚克隆标签 (Z_i\)；
- 每个亚克隆在每个区段的拷贝数轮廓 \(\mu_{kr}\)；
- 可选的恶性/非恶性标签；
- 对 ST 数据，将标签叠加到组织坐标后的空间亚克隆图。

### 整体流程

```text
配对 WGS/WES（可选）
  -> HMM 分段 + bulk 肿瘤 CNA 先验
             |
原始单细胞/空间计数矩阵
  -> 选择二倍体参考细胞/spot
  -> 按区段估计相对覆盖度 X_hat[i,r]
  -> 得到 cell/spot × segment 矩阵
  -> 嵌套 CRP：
       beta 决定是否产生新细胞亚克隆
       alpha 决定新区段状态是否出现
  -> MCMC burn-in + 多数投票
  -> 删除过小亚克隆并重新分配细胞
  -> 亚克隆 CNA 轮廓、标签与恶性判定

没有配对 DNA：
  染色体臂初始分段 -> 第一轮聚类
  -> 各亚克隆 pseudobulk bin profile
  -> HMM 精细分段 -> 第二轮聚类
```

### 第一步：基因组分段

有配对 DNA 时，Clonalscope 对 WGS/WES 或 pseudobulk scDNA-seq 的 bin count 使用四状态 HMM：缺失、中性、单拷贝扩增和双拷贝扩增。转移矩阵为

$$
\left(\begin{array}{cccc}1-3t & t & t & t\\ t & 1-3t & t & t\\ t & t & 1-3t & t\\ t & t & t & 1-3t\end{array}\right),
$$

默认 (t=1\times10^{-6}\)，发射分布为 Normal，默认标准差 0.2，最后用 Viterbi 解码得到分段状态。

没有配对 DNA 时，第一轮直接把染色体臂当作区段。根据初步亚克隆，把细胞在固定大小 bin 上聚合为 clone-specific pseudobulk，再逐 clone 做 HMM 分段，汇总断点并进行第二轮 Clonalscope。代码对应 `R/CreateSegtableNoWGS.R:31-161`。

### 第二步：选择二倍体参考

Clonalscope 只需要少量高置信度正常参考，例如免疫、基质细胞或病理学明确的正常区域。仓库中的 `FindNormalReference` 支持 marker 与 PCA/SVD 两条路线（`R/IdentifyNormalCells.R:35-172`）。

论文还描述了 cell-wise SVD control，但细节放在 Supplementary Text。核心导出路径中没有找到与论文描述逐式对应的 cell-wise synthetic-control fold-change 实现，因此这里必须保留为 **Not found/部分实现**，不能把 PCA 参考选择直接等同于完整的 cell-wise control。

### 第三步：从基因计数估计区段覆盖度

对细胞 (i\)、基因 (g\) 和所属区段 (r\)，论文假设

$$
N_{ig}\sim\mathrm{Poisson}(s_i b_g X_{ir}),
$$

其中 (s_i\) 是细胞文库大小因子，(b_g\) 是基因基线表达，(X_{ir}\) 是目标区段相对覆盖度。

归一化因子为

$$
s_i=\frac{\sum_g N_{ig}}{\operatorname{median}_i(\sum_g N_{ig})},
$$

并得到

$$
\hat b_g=\frac{\sum_c N_{cg}}{\sum_c s_c},
\qquad
\hat X_{ir}=\frac{\sum_{g\in r}N_{ig}}{s_i\sum_{g\in r}\hat b_g}.
$$

代码没有数值优化 Poisson 似然，而是实现推导后的直接比值：过滤高变/低支持基因，基因与区段做 overlap，按文库大小归一化，再用正常细胞区段总和的中位数作为基线（`R/EstRegionCov.R:42-159`）。`PrepCovMatrix` 过滤基因或细胞支持不足的区段，形成最终 cell × segment 矩阵。

### 第四步：嵌套 CRP 亚克隆模型

coverage-only 模式为

$$
X_{ir}\sim N(\theta_{ir},\sigma_r^2),\qquad \theta_{ir}=\mu_{Z_i r}.
$$

如果有配对 DNA，初始设置两个轮廓：

$$
\mu_{1r}^{(0)}=1,
\qquad
\mu_{2r}^{(0)}=\begin{cases}
0.5,&r\in R^{\mathrm{Del}},\\
1.5,&r\in R^{\mathrm{Amp}}.
\end{cases}
$$

第一个 CRP 用 (\beta\) 控制细胞加入已有亚克隆还是创建新亚克隆：

$$
p_{i,k}^{(t)}\propto
\phi(X_i\mid\mu_k^{(t-1)},\hat\sigma^{(t)})\,n_{k,-i}^{(t)}.
$$

若创建新亚克隆，第二个 CRP 在每个区段上复用已有状态或创建新状态，创建概率由 (\alpha\) 控制。论文写为

$$
\mu_r^{\mathrm{new}}=\begin{cases}
\delta_j,&m_j/(N-1+\alpha),\\
\sim U[0,3],&\alpha/(N-1+\alpha).
\end{cases}
$$

coverage 模式默认 (\alpha=2,\beta=2\)。代码确实执行“已有状态/新状态”和“已有亚克隆/新亚克隆”的两层抽样，但连续新状态用的是 `runif(0.3, 2.5)`，不是论文写的 (U[0,3]\)（`R/BayesNonparCluster.R:159-220`）。这是明确的 paper-code 差异。

完成一轮细胞更新后，亚克隆均值与区段噪声更新为

$$
\mu_{kr}^{(t)}\sim N\!\left(\bar X_{kr},\frac{(\sigma_r^{(t-1)})^2}{n_k^{(t)}}\right),
$$

$$
\sigma_r^{(t)}=\sqrt{\frac{1}{N}\sum_i(X_{ir}-\mu_{Z_i r}^{(t)})^2}.
$$

### 第五步：稳定化和最终标签

默认运行 200 次迭代，去掉前 100 次 burn-in。每个细胞用剩余迭代中的多数票确定亚克隆。小于 (n_{\min}\) 的亚克隆被删除；默认 (n_{\min}\) 约为细胞数的 1%，被删除亚克隆中的细胞按保留亚克隆的似然重新分配。

代码还隐藏了一条重要迭代路径：若某亚克隆与 bulk CNA 先验相关性低于 `threshold_2nd=-0.2`，这些细胞会被用作新的正常参考，整套覆盖度估计和聚类最多重新运行十轮（`R/RunCovCluster.R:168-250`）。

### coverage + allelic ratio 模式

当得到区段覆盖度 (\rho_{ir}\) 与 major-haplotype proportion (\Theta_{ir}\) 时，模型使用两个独立 Normal 项：

$$
\rho_{ir}\sim\mathrm{Normal}(\mu_{Z_i r}^{(\rho)},\sigma_r^{(\rho)}),
$$

$$
\Theta_{ir}\sim\mathrm{Normal}(\mu_{Z_i r}^{(\theta)},\sigma_r^{(\theta)}).
$$

`BayesNonparAlleleCluster` 实现联合似然，`genotype_neighbor` 把 coverage/allele 中心投影到离散基因型网格。局限是仓库没有与 `RunCovCluster` 对称的顶层 allele wrapper；用户需自己串联 sampler、`MCMCtrim(allele=TRUE)` 和 `AssignCluster(allele=TRUE)`。低层 allele 函数默认 (\alpha=1,\beta=1\)，也与 coverage wrapper 不同。

### 恶性细胞/spot 判定

有配对 DNA 时，亚克隆 (k\) 与肿瘤 CNA 轮廓的修正余弦相似度为

$$
S_c=\frac{\sum_r[(\hat\mu_{kr}-1)(\mu_{1r}-1)]}
{\sqrt{\sum_r(\hat\mu_{kr}-1)^2}\sqrt{\sum_r(\mu_{1r}-1)^2}}.
$$

默认 (S_{\min}=0.2\)，超过阈值即标为恶性。`AssignCluster` 实现了相应的中心化相似度与阈值逻辑。没有配对 DNA 时，`MalignantAssignment` 使用低 CNA-load 亚克隆作为内部正常参考，这是一条替代启发式，不等同于 matched-DNA 公式。

### 空间信息的角色

空间坐标不参与 Bayesian clustering。Clonalscope 先只根据 CNA-like 信号给 spot 分亚克隆，再将标签叠加回组织位置。这避免预设“相邻 spot 必须同 clone”，但也意味着模型不会利用邻域信息去补救特别稀疏的 spot。

跨切片或原发/转移灶 tracing 依靠亚克隆 CNA 轮廓相似性和空间图进行比较。仓库中没有找到可复用的谱系/系统发育推断函数，因此这里的“tracing”应理解为 profile matching，而不是完整的肿瘤进化树重建。

### 评估结果如何理解

- Fig. 2 中，Clonalscope 在多数样本上与配对 DNA 的 CNA correlation 约为或高于 0.75；P6198 的恶性标注准确率报告约 0.974，而 CopyKAT 约 0.408。
- P5931 中，Clonalscope 的 scRNA 亚克隆与三个 scDNA 克隆的对应更紧凑。
- scATAC 的 coverage + allele 模式恢复了可辨识的等位基因 CNA 结构，但比监督的六克隆结果更细。
- 空间验证中，Slide-seq 两个 clone 与 DNA 轮廓的相关性为 0.841 和 0.888；SCC P6 相邻切片 region mean 相关性为 0.84。
- 原发/转移灶两个 clone profile 的相关性为 0.661 和 0.725，支持相似性 tracing，但不是严格谱系证据。
- Fig. 6-7 展示亚克隆与分化、耐药/生存相关基因表达的空间共定位；这些是观察性关联，不能直接解释为 CNA 导致耐药。

### 代码、数据与可复现性

论文权威代码仓库为 `https://github.com/seasoncloud/Clonalscope`，本地快照固定在 commit `07dd0c576b6754d18dda86ec8905d8a9be5e77b0`。仓库包含核心 R 包、五类教程、基因组注释、示例矩阵和大量中间结果，但没有覆盖论文中的全部外部队列。

权威数据来源包括 dbGaP `phs001818`、`phs001711`；BioProject `PRJNA598203`、`PRJNA674903`、`PRJNA768453`；GEO `GSE284061`、`GSE144240`；Broad SCP `SCP1278`；OEP `OEP001756`；scCRLM 门户；以及 10x Genomics 的乳腺癌 ST 数据。部分患者数据需要 dbGaP 授权。

可复现性评价约为 **3.5/5**：核心代码和示例充分，但缺少自动测试、容器/锁定环境和一键复现全部图的流程；很多队列依赖外部或受控数据。三个补充 PDF 已保留，但 `SUPP_MD=(none)`，因此 Supplementary Text/Table 专属参数仍是明确缺口。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Clonalscope

### Overview

Clonalscope is a CNA-based cancer subclone detection method for scRNA-seq, scATAC-seq and spatial transcriptomics (ST). It converts noisy gene- or accessibility-level counts into segment-level relative coverage, then uses nonparametric Bayesian clustering with a nested Chinese Restaurant Process to infer the number of clones, clone-specific CNA profiles and cell/spot assignments. When matched WGS/WES or pseudobulk scDNA-seq is available, it supplies genome segments and a tumor CNA prior that also improves malignant-cell labeling.

The central contribution is not another smoothed expression clustering method. Clonalscope explicitly links RNA/ATAC/ST coverage to DNA-level copy-number structure, permits new clones and new regional states to emerge without fixing (K), supports joint coverage plus allelic-ratio inference, and can run without matched DNA through a two-pass chromosome-arm/HMM refinement strategy.

### Why Existing Approaches Are Insufficient

RNA expression and chromatin accessibility are indirect, noisy proxies for DNA copy number. Broad lineage-specific transcriptional or epigenetic programs can resemble CNAs, so a transcriptomic cluster need not be a genetic subclone.

- inferCNV (introduced through the glioblastoma scRNA-seq study in *Science*, 2014) and CopyKAT (*Nature Biotechnology*, 2021) smooth adjacent genes and commonly use hierarchical clustering; they do not directly exploit matched bulk CNA priors.
- HoneyBADGER (*Genome Research*, 2018) and CaSpER (*Nature Communications*, 2020) incorporate allelic information, but allele-specific reads can be too sparse for large gains.
- STARCH (*Physical Biology*, 2021) uses neighboring spatial spots to stabilize CNA inference, which imposes spatial structure that Clonalscope intentionally avoids during clone assignment.
- CONICS (*Bioinformatics*, 2018) uses matched DNA segmentation, but was designed around full-length scRNA-seq and does not provide the same de novo nonparametric subclone model.

Hierarchical clustering additionally requires a chosen cut and is brittle when segment-level signals have low signal-to-noise ratio. Clonalscope instead treats clone creation and regional state creation as coupled probabilistic decisions.

### Method in Brief

```text
matched DNA (optional) -> HMM segments + tumor CNA prior
                                  |
gene/feature x cell/spot counts --+
              |
              v
normal-reference normalization -> cell/spot x segment fold changes
              |
              v
nested nonparametric Bayesian clustering
  beta: create/select cell cluster
  alpha: create/select regional CNA state
              |
              v
burn-in trimming + majority vote + small-cluster reassignment
              |
              +-> clone CNA profiles and cell/spot labels
              +-> matched-DNA cosine score for malignant labeling
              +-> spatial overlay after inference
```

Without matched DNA, the first pass uses chromosome arms. Cluster-specific pseudobulk bin profiles are then HMM-segmented and pooled into refined regions for a second pass. In allele-aware mode, the observation for each region is bivariate: relative coverage and major-haplotype proportion.

### Evaluation and Main Findings

The study covers four 10x scRNA-seq datasets, one Slide-seq dataset, ten Visium ST datasets and one SNU601 scATAC-seq dataset. Validation uses matched scDNA-seq, WGS/WES, pseudobulk DNA profiles, pathology labels, adjacent tissue sections and previously characterized allele-specific clones.

- Across seven displayed RNA/ST samples, Clonalscope's CNA profiles usually show correlations near or above 0.75 with matched DNA and visually exceed CopyKAT/inferCNV in most cases (Fig. 2a).
- In P6198, matched-DNA-informed malignant labeling is reported at approximately 0.974 accuracy versus approximately 0.408 for CopyKAT; Fig. 2b also shows substantial gains in several ST/scRNA samples, though Clonalscope is not the top bar for every dataset.
- In P5931, inferred RNA-based clones map more cleanly to three scDNA-defined clones than the alternative hierarchical-clustering outputs (Fig. 2c).
- Joint coverage/allelic-ratio clustering recovers recognizable scATAC clone structure without fixing the published number of clones, but produces a more granular solution than supervised scDNA classification (Fig. 3).
- Spatial validations show clone CNA correlations of 0.841 and 0.888 against Slide-DNA clone profiles and a replicate-region correlation of 0.84 in SCC P6 (Fig. 4).
- Primary/metastasis clone-profile correlations of 0.661 and 0.725 support similarity-based tracing, not a fully inferred phylogeny (Fig. 5).
- Figures 6-7 show spatially segregated clones with different expression programs, differentiation-associated markers and candidate resistance/survival genes. These are observational associations rather than causal drug-response tests.

### Code-Paper Match

Overall fidelity is **medium**. The public R package implements the core pipeline at commit `07dd0c576b6754d18dda86ec8905d8a9be5e77b0`:

- `RunCovCluster` orchestrates coverage estimation, matrix construction, Bayesian clustering, burn-in and final assignment.
- `EstRegionCov` and `PrepCovMatrix` implement segment-level normalization and filtering.
- `BayesNonparCluster` implements clone/state proposals and Gaussian updates.
- `BayesNonparAlleleCluster` implements the joint coverage/allelic-ratio likelihood.
- `CreateSegtableNoWGS` implements two-round segmentation refinement.
- `AssignCluster` implements matched-DNA clone scoring and postprocessing.

Important differences remain. The coverage sampler draws a new continuous regional state from `runif(0.3, 2.5)` rather than the manuscript's stated (U[0,3]). Allele-aware inference is exposed as lower-level functions rather than an end-to-end wrapper, and its sampler defaults to (alpha=1,\beta=1). A literal exported cell-wise SVD synthetic-control estimator and a reusable cross-sample lineage-tracing function were **Not found**.

### Reproducibility

The code snapshot is more complete than a minimal demonstration repository.

Reproduction is still nontrivial:

- no automated tests, container or environment lockfile was found;
- several tutorials depend on a large R/Bioconductor/Seurat stack and cohort-specific files;
- many paper datasets remain in external repositories, including controlled-access dbGaP studies;
- no one-command workflow reproduces all figures;
- three supplementary PDFs are local, but `SUPP_MD=(none)`, so Supplementary Text/Table-only settings were not fully text-verified.

The authoritative data sources named by the paper include dbGaP `phs001818` and `phs001711`, BioProjects `PRJNA598203`, `PRJNA674903` and `PRJNA768453`, GEO `GSE284061` and `GSE144240`, Broad SCP `SCP1278`, OEP `OEP001756`, the scCRLM portal and 10x Genomics breast-cancer ST datasets.

### Bottom Line

Clonalscope is most useful when the scientific target is a DNA-like subclone structure rather than a generic expression cluster. Its strongest feature is the combination of segment-level normalization, optional matched-DNA priors and a nonparametric clone/state model that transfers across single-cell and spatial assays. The evidence supports robust CNA concordance and useful malignant/spatial clone mapping on selected datasets, while lineage, differentiation and resistance interpretations should remain profile-similarity or co-localization claims rather than causal conclusions.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
