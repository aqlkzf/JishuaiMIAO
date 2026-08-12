---
layout: default
permalink: /paper-atlas/jdrnet-6ffcd8a3/
title: "JDRnet"
nav: false
description: "JDRnet 不是一种新的 GRN 推断器，也不是一种新的生存模型。它是一条组合式分析流程：先用 PANDA–LIONESS 为每位患者构建转录因子到靶基因的加权网络，把整张网络压缩成基因入度和转录因子出度，再把这两类网络特征连同表达、甲基化和 miRNA 一起送入 MOFA+，最后比较加入网络前后是否出现更显著、且可解释的生存相关潜因子。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Briefings in Bioinformatics · 2025</span>
    </div>
    <h1>JDRnet</h1>
    <p>Gene regulatory network integration with multi-omics data enhances survival predictions in cancer</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1093/bib/bbaf315" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## JDRnet 方法中文解读：把患者特异调控网络接入多组学潜因子分析

### 一句话抓住核心

JDRnet 不是一种新的 GRN 推断器，也不是一种新的生存模型。它是一条组合式分析流程：先用 PANDA–LIONESS 为每位患者构建转录因子到靶基因的加权网络，把整张网络压缩成基因入度和转录因子出度，再把这两类网络特征连同表达、甲基化和 miRNA 一起送入 MOFA+，最后比较加入网络前后是否出现更显著、且可解释的生存相关潜因子。

### 1. 为什么不直接把整张网络塞进模型

每位患者的 PANDA–LIONESS 网络都是一个完整的 TF×gene 加权二部图，边数远大于样本数。论文选择两个节点级汇总量：

$$
\operatorname{indegree}_s(g)=\sum_t w_s(t,g),
$$

$$
\operatorname{outdegree}_s(t)=\sum_g w_s(t,g),
$$

其中 $w_s(t,g)$ 是患者 $s$ 的 TF $t$ 到基因 $g$ 的边权。入度表示一个基因从全部 TF 接收的总调控权重，出度表示一个 TF 指向全部靶基因的总权重。这里的边权允许为负，但符号不等同于激活或抑制；因此度也不能回答调控方向，只能概括相对调控强度或连接倾向。

源码中的 `code/networks/calculate_degree.R` 与这一定义直接对应：按 `tar` 分组求和得到 `indegree`，按 `reg` 分组求和得到 `outdegree`。

### 2. 患者特异网络从哪里来

#### 2.1 PANDA 的总体网络

PANDA 让三类证据通过消息传递达到一致：

- 启动子 motif 扫描给出 TF–gene 先验；
- TF–TF 蛋白互作给出协作关系；
- 表达数据给出 gene–gene 共表达关系。

其输出是该癌种或队列的聚合网络。论文明确称正式分析使用 PANDA 和 LIONESS 的 MATLAB 实现。本地 `code/networks/lib/PANDA.m`、`panda_run.m` 和 `panda_config.m` 保留了这条路径，其中配置给出 `alpha = 0.1`。

#### 2.2 LIONESS 的单样本拆分

对包含 $N$ 个样本的聚合网络 $A^{(N)}$，去掉样本 $s$ 后重新运行 PANDA 得到 $A^{(-s)}$，LIONESS 构造：

$$
A^{(s)}=N\left(A^{(N)}-A^{(-s)}\right)+A^{(-s)}.
$$

这不是从单个样本独立估计网络，而是在“每个样本线性贡献聚合网络”的假设下，用留一差异反推出该样本贡献。`code/networks/lioness_run.m` 的 `PredNet = NumConditions * (AgNet - LocNet) + LocNet` 是公式的逐字实现。

代码仓库还提供 `single_sample_networks_*` notebooks，说明可用 netZooPy 的 Python 实现生成网络。因此应区分：论文报告的正式方法路径是 MATLAB；仓库同时提供 Python 可运行替代路径。现有材料没有证明两条路径在所有数据和版本下逐元素产生完全相同的网络。

### 3. 为什么先对每一种组学单独做 PCA

原始层的维度差异很大。以论文图 2 的肝癌为例，表达约 20,169 个特征、入度约 15,920 个，而出度只有 644 个；直接联合分解容易让高维层对潜空间产生过大的结构性影响。

作者对每一层分别用 SVD-PCA，保留累计 $R^2\ge 0.85$ 的 PC，并规定至少保留 20 个 PC。图 2 显示肝癌各层经此处理后约为 20–193 个 PC，降到同一数量级。这个步骤不是挑选“最重要的若干原始基因”，而是让所有原始特征通过载荷参与少量 PC。

本地 `process_data.ipynb` 调用外部 MARMOT 的 `prepare_data(..., pca = TRUE)`。在此之前，notebook 对入度矩阵执行 `preprocessCore::normalize.quantiles()`；没有看到对出度做同样的分位数标准化。这个不对称处理是代码事实，但论文没有给出其生物学理由，不能进一步推断为某种特定分布修正。

### 4. 四组 MOFA+ 对照才是因果归因的关键设计

TCGA 的输入层依次为 expression、methylation、miRNA、indegree、outdegree。`JDR_net.ipynb` 构造四个模型：

1. `nonet`：前三种常规组学；
2. `indeg`：常规组学加入度；
3. `out`：常规组学加出度；
4. `both`：五层全部加入。

每个模型调用 `run_mofa2(..., n_fct = 5, seed = 13, convergence = "slow", use_basilisk = TRUE)`。MOFA+ 对第 $i$ 个数据层做共享因子分解：

$$
Y_i=W_iF+E_i,
$$

其中 $F$ 是样本共享的潜因子，$W_i$ 是该层各输入特征对潜因子的权重。论文还用五个随机种子做了敏感性分析，并报告生存结果没有显著差异；但当前 notebooks 中未定位到完整的五种子扫描代码，所以这一验证来自论文及补充表/图，不是本地脚本的直接再运行结果。

四组对照的重要性在于：不能仅看 `both` 模型里某个因子显著，就说网络带来了信息；必须与 `nonet`、`indeg`、`out` 比较。图 3 显示入度单独加入总体影响很小，出度在 AML 揭示额外信号，而同时加入入度和出度在 AML、肾癌、肝癌产生更明显的改进；肝癌出现三个生存相关因子。

### 5. “生存相关因子”究竟如何定义

对每个 MOFA+ 因子，作者分别拟合单变量 Cox 比例风险模型，并对 $P$ 值做 Benjamini–Hochberg FDR 校正。代码由 MARMOT 的 `surv_association(..., univariate = TRUE)` 和 `surv_compare(..., method = "BH")` 完成；论文指定 R `survival` 3.3.1。

这里的结论是“潜因子与生存统计相关”，不是个体级生存预测器性能已经提高。流程没有以独立测试集上的 C-index、时间依赖 AUC 或校准曲线评价预测模型，也没有证明 GRN 对生存具有因果作用。

图 4 进一步解释肝癌：含网络模型的 Factor 2、4、5 与生存相关；其中 Factor 2 和 4 分别与无网络模型中的因子高度相关，而 Factor 5 与无网络模型任一因子的最高相关仅约 0.31。这个结果支持“网络加入后捕捉到一个此前很弱或缺失的异质性轴”，但仍是相关性证据。

### 6. 从 PC 权重返回基因和 TF

因为 MOFA+ 的输入是 PC，模型直接给出的是“PC 对因子的权重”。补充方法从

$$
S_{\mathrm{PCA}}=XP
$$

和 MOFA 分解推导出原始特征空间近似权重：

$$
W_{\mathrm{MOFA}}\approx P_{\mathrm{filtered}}W_{\mathrm{PC-fil}}.
$$

`JDR_net.ipynb` 用 MARMOT 的 `map_wts()` 完成这个矩阵乘法。若保留全部 PC，该线性回映射可与原始特征空间分解对应；实际只保留达到 85% 方差阈值的 PC，丢弃部分引入误差，因此必须写成近似。论文认为特征排序不太可能被明显改变，但当前材料没有量化每一层、每个因子的回映射误差。

### 7. 生物学解释如何落到入度与出度两侧

#### 7.1 入度侧：通路富集

作者把生存相关因子的基因入度回映射权重直接作为排序，调用 `perform_gsea(..., differential = FALSE)`，对 MSigDB Hallmark 和 KEGG-legacy 做 GSEA。图 5 显示 TCGA 肝癌与独立 GEPliver 队列都富集到脂肪酸代谢、胆汁酸代谢、ABC transporters 等通路。这里排序量是潜因子权重，不是差异表达的 fold change。

#### 7.2 出度侧：关键 TF 重叠

作者在两个肝癌队列中，对每个生存相关因子取绝对回映射权重最高的 20 个 TF，再用 Fisher 精确检验评估集合重叠。论文报告九个共享 TF，odds ratio 2.68、$P=0.02$；图 6 展示 TBX15、RFX5、RFX1、RBPJ、MXI1、MESP1、JUND、HOXB1、ARID2 的因子权重。代码单元明确先按绝对值取 top 20，再构造列联表。

JUND 因而是值得后续验证的候选调控因子，而不是已经证实的肝癌驱动因子。论文的措辞也是“potentially interesting candidate”。

### 8. 证据与代码对应

| 论文机制 | 本地证据 | 对应程度 |
|---|---|---|
| PANDA 聚合 GRN | `code/networks/lib/PANDA.m`, `panda_run.m` | Exact：核心 MATLAB 算法在本地 |
| LIONESS 单样本公式 | `code/networks/lioness_run.m` | Exact：公式逐字实现 |
| 入度/出度求和 | `code/networks/calculate_degree.R` | Exact |
| PCA 85%、至少 20 PC | 论文方法；`process_data.ipynb` 调用 MARMOT | Partial：阈值逻辑在外部包中 |
| 四个 MOFA+ 模型及参数 | `code/notebooks/JDR_net.ipynb` | Exact：调用和层选择可见 |
| Cox、临床关联、权重回映射、GSEA | 同一 notebook 调用 MARMOT | Partial：调用可见，核心函数体不在工作区 |
| 图 2–6 | `code/figures/Figure2.pdf` 至 `Figure6.pdf` | Artifact：有预生成图，未在本轮重算 |
| 原始/中间数据与容器 | 论文指向 Zenodo 14525733 | Not local：当前工作区未包含完整数据包和容器 |

### 9. 复现与版本边界

- 本地代码目录没有可归属到 JDRnet 上游仓库的独立 Git 提交元数据，因此 `code_repo_commit` 保持 `null`；不能把 PaperCode 父仓库提交当成论文代码版本。
- notebook 注释建议从 `rtpop/MARMOT` 安装 `v0.0.1`，而论文和仓库 README 指向 `kuijjerlab/MARMOT`。这说明代码调用意图明确，但远端组织名存在历史迁移或别名差异，当前工作区没有 MARMOT 源码可核对。
- `JDR_net.ipynb` 默认可以加载预计算结果；Zenodo 数据、因子分解和容器并未全部纳入本工作区。本轮只验证了论文、补充材料、脚本、notebook 调用链和预生成图，没有重跑耗时网络推断或 MOFA+。
- 论文正式网络路径写为 MATLAB，仓库另有 netZooPy notebook。两条路径在公式层一致，但不能据此声称数值逐元素一致。
- GEPliver 是独立队列验证，但它与 TCGA 在队列构成和可用组学层上不同；这增强了生物学复现性，却不是完全同分布的预测测试。

### 10. 左到右读完整流程

$$
\text{表达 + motif + PPI}
\rightarrow \text{PANDA 聚合网络}
\rightarrow \text{LIONESS 患者网络}
\rightarrow \{\text{indegree},\text{outdegree}\}
$$

$$
\rightarrow \text{各层 PCA（85%，至少 20 PC）}
\rightarrow \text{四组 MOFA+ 对照}
\rightarrow \text{单变量 Cox + BH-FDR}
$$

$$
\rightarrow \text{权重近似回映射}
\rightarrow \begin{cases}
\text{入度权重：GSEA}\cr
\text{出度权重：TF 排名与 Fisher 检验}
\end{cases}
$$

真正的新意不在任何一个单独模块，而在把患者级 GRN 特征作为额外数据层，并用有/无网络的成组模型比较，检验调控结构是否补充传统组学的生存相关异质性。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## JDRnet — Summary

**Paper**: "Gene regulatory network integration with multi-omics data enhances survival predictions in cancer"
**Authors**: Romana T. Pop, Ping-Han Hsieh, Tatiana Belova, Anthony Mathelier, Marieke L. Kuijjer
**Journal**: Briefings in Bioinformatics | Year: 2025 | DOI: 10.1093/bib/bbaf315

---

### Motivation & Novelty

#### Biological Problem

Cancer is driven by coordinated dysregulation across multiple molecular levels. Multi-omics integration methods (JDR tools) can identify latent factors that explain variance across data types and associate with clinical outcomes. However, a critical regulatory layer — transcriptional regulation — is systematically excluded from these analyses. Transcription factors (TFs) coordinate the expression of hundreds of genes; their dysregulation is a hallmark of cancer. Existing JDR approaches treat gene expression as a read-out but not as the product of a regulatory process.

#### Why Existing Methods Fall Short

**MOFA+** (Genome Biology 2020; Argelaguet et al.) performs multi-omics factor analysis but recommends keeping omic dimensions within one order of magnitude — a difficult constraint when combining RNA-seq (20,000 features) with smaller omics. **JIVE** (Annals of Applied Statistics 2013; Lock et al.) is slow and less scalable. **MCIA** (Bioinformatics 2014) and **RGCCA** (Briefings in Bioinformatics 2017) use co-inertia and canonical correlation approaches that are disrupted by PCA pre-filtering. The **MOMIX benchmarking pipeline** (Genome Biology 2021; Cantini et al.) established how to compare JDR methods but did not include network-based features.

**PANDA** (PLOS ONE 2013; Glass et al.) + **LIONESS** (iScience 2019; Weighill et al.) can reconstruct patient-specific GRNs, but no study had systematically integrated these into multi-omics JDR for survival prediction.

#### Unique Contributions

1. **First systematic integration of patient-specific GRNs into JDR**: Treats PANDA+LIONESS indegree and outdegree as additional omics layers in MOFA+.

2. **PCA pre-filtering as a data-driven dimensionality equalizer**: Proposes using PCA with a variance threshold (R²=0.85, min 20 PCs) to normalize omic dimensions before JDR, rather than selecting top-N features. Shows this improves performance for MOFA+, JIVE, and MCIA (but not RGCCA).

3. **Mathematical weight back-mapping**: Derives an approximate mapping (Eq. 1: $W_{\text{MOFA}} \approx P_{\text{filtered}} \times W_{\text{PC-fil}}$) to recover feature-level biological interpretation after PCA pre-filtering.

4. **MARMOT tool**: Introduces an R package for JDR model comparison and analysis, extending the MOMIX pipeline.

5. **Biological finding**: Identifies GRN-based survival factors in liver cancer linked to fatty acid metabolism dysregulation and nominates JUND as a novel TF driver.

---

### Method Overview

JDRnet is a **framework** (not a single algorithm) that integrates patient-specific GRN features with multi-omics data for survival prediction.

**Core computational pipeline**:

1. **GRN inference**: PANDA constructs a population-level bipartite TF-gene regulatory network from motif priors, PPI data, and co-expression. LIONESS derives per-sample networks via linear interpolation: $\text{Net}_i = N \cdot (\text{AgNet} - \text{LocNet}_i) + \text{LocNet}_i$.

2. **Degree reduction**: The high-dimensional TF×gene×sample tensor is collapsed to two matrices: (a) indegree (genes × samples = total regulatory input per gene) and (b) outdegree (TFs × samples = total regulatory output per TF).

3. **PCA pre-filtering**: Each of the 5 omics (expression, methylation, miRNA, indegree, outdegree) is PCA-compressed to the PCs capturing ≥85% of variance (minimum 20 PCs), bringing feature counts within one order of magnitude.

4. **MOFA+ factorization**: 4 models trained (nonet, +indeg, +outdeg, +both) using 5 factors, seed 13, slow convergence, with PCA scores as input.

5. **Survival analysis**: Univariate Cox regression per factor with BH correction identifies survival-associated factors (SAFs).

6. **Biological interpretation**: MOFA+ weights back-mapped to original features via Eq. 1; GSEA on indegree weights; top-20 outdegree TFs per SAF; Fisher's test for cross-cohort overlap.

**Key assumptions**: Linear GRN contributions (LIONESS), linear omics relationships (MOFA+/PCA), TF degree as a sufficient summary of regulatory state.

See `doc_method.md` for full mathematical treatment and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets

| Dataset | Cancer types | Samples | Omics |
|---------|-------------|---------|-------|
| TCGA (MOMIX format) | 10 (AML, breast, colon, GBM, kidney, liver, lung, melanoma, ovarian, sarcoma) | ~100–400 per type | RNA-seq, miRNA, methylation |
| GEPliver | Liver (HCC + mixed) | ~370 | RNA-seq only |

#### Primary Results

**PCA pre-filtering** (Figure 2, S3): Reduces dimensionality range from 31× (raw) to ~10× (after PCA at R²=0.85) in liver cancer. Benchmarking shows MOFA+ performance improves or stays the same in 7/10 cancer types with PCA (Figure S4). RGCCA degrades with PCA in all cancer types.

**GRN contribution to SAFs** (Figure 3): The combined model (both indeg+outdeg) is the strongest:
- Liver cancer: 3 SAFs (vs. 1 without GRNs) — the headline result
- AML: 1 additional SAF from outdegree model
- Kidney: improvement with both model
- Most other cancer types: minimal change

**Liver cancer deep-dive** (Figure 4):
- Factor 2 (r=0.94 with nonet): GRN amplifies an existing signal
- Factor 4 (r=0.83 with nonet): preserved existing SAF
- Factor 5 (r=0.31 with nonet): genuinely novel GRN-derived factor — the most important finding

**Biological pathways** (Figure 5): GSEA on indegree weights of all 3 liver SAFs reveals consistent enrichment of fatty acid metabolism (negative NES = stronger regulation → better survival) in both TCGA and GEPliver. ABC transporters also enriched. Results replicate across independent cohorts.

**Key TFs** (Figure 6): 9 TFs shared between TCGA and GEP top-20 outdegree lists. Fisher's exact test: OR=2.68, p=0.02. Key candidates:
- **JUND** (AP-1): linked to hepatic lipid metabolism and NAFLD; novel in HCC context
- **RFX1/RFX5**: immune signaling TFs
- **ARID2**: chromatin remodeler frequently mutated in HCC

#### Validation

Independent validation in GEPliver (n≈370) confirms:
- 3 SAFs identified (Table S3)
- Same clinical associations (fibrosis, histological subtype)
- Same pathway enrichments (fatty acid metabolism, ABC transporters)
- 9 overlapping top TFs with TCGA (Fisher p=0.02)

---

### Reproducibility

**Rating: 3.5/5**

**What works well**:
- Full code on GitHub (`kuijjerlab/JDRnet`)
- Data on Zenodo (record 14525733) including intermediate files
- Container (Singularity/Docker) with exact software versions on Zenodo
- `precomputed=TRUE` flag allows skipping computationally expensive GRN inference
- MARMOT R package pinned to v0.0.1 for reproducibility
- Seed fixed at 13; seed sensitivity analysis in Table S2 and Figure S9
- All analysis in well-documented R notebooks

**Limitations**:
- PANDA+LIONESS is computationally very expensive (O(N²) in samples per cancer type) — 10 cancer types × GPU cluster time
- MARMOT is an external dependency that wraps most statistical logic; the source must be checked separately
- `pcamethods` R package version not pinned in notebooks
- Zenodo data URL must be manually downloaded; not scripted
- The Python/netZooPy path and MATLAB path produce equivalent results, but the paper describes only MATLAB — minor inconsistency
- GEPliver data requires separate download + processing (`get_gep_liver.sh` + `gep_data_process.r`)

**Practical notes**:
- Start with `precomputed=TRUE` and Zenodo intermediates to reproduce figures without running GRN inference
- MARMOT install: `devtools::install_github("rtpop/MARMOT", ref="v0.0.1")` — exact version required
- Container on Zenodo is the safest reproduction path; R package versions differ across systems
- `MOFA2` requires Python backend via Basilisk — `use_basilisk=TRUE` must be set

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
