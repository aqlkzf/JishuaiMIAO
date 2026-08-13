---
layout: default
permalink: /paper-atlas/kpspatial-60962d12/
title: "KPSpatial"
nav: false
description: "传统单细胞谱系追踪能重建“哪些癌细胞来自共同祖先”，但组织解离会丢失这些细胞原来位于肿瘤内部、边缘还是转移灶的信息。空间转录组保留位置和微环境，却通常不能直接给出深层谱系。本文把两者结合，研究肿瘤亚克隆扩张、细胞状态可塑性、缺氧/纤维化/免疫抑制微环境以及转移如何在空间和时间上共同演化。 实验使用 KP-Tracer 小鼠：Cre 同时启动 Kras^{G12D}、敲除 Trp53 并激活 Cas9 谱系记录器。"
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
      <span>Atlases &amp; Resources</span>
      <span>bioRxiv · 2024</span>
    </div>
    <h1>KPSpatial</h1>
    <p>Spatiotemporal lineage tracing reveals the dynamic spatial architecture of tumour growth and metastasis</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1101/2024.10.21.619529" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for KPSpatial">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/mattjones315/KPSpatial-release" target="_blank" rel="noopener noreferrer" aria-label="Open code for KPSpatial">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 肺腺癌时空谱系追踪：把肿瘤进化树放回组织空间

### 核心问题

传统单细胞谱系追踪能重建“哪些癌细胞来自共同祖先”，但组织解离会丢失这些细胞原来位于肿瘤内部、边缘还是转移灶的信息。空间转录组保留位置和微环境，却通常不能直接给出深层谱系。本文把两者结合，研究肿瘤亚克隆扩张、细胞状态可塑性、缺氧/纤维化/免疫抑制微环境以及转移如何在空间和时间上共同演化。

实验使用 KP-Tracer 小鼠：Cre 同时启动 $Kras^{G12D}$、敲除 $Trp53$ 并激活 Cas9 谱系记录器。Cas9 在带随机 14 bp integration barcode（intBC）的靶位点持续产生不可逆、可遗传的 indel；这些靶位点以 poly(A) RNA 表达，因此可和转录组一起被空间测序捕获。作者在肿瘤诱导后 12–16 周取材，获得 44 张 Slide-seq 和 5 张 Slide-tags 阵列，覆盖 100 多个肿瘤（论文 Results “An integrated lineage and spatial platform”）。

### 1. 两种空间技术承担不同角色

Slide-seq 以约 10 μm spot 覆盖大视野，适合观察整个肿瘤及其周围组织，但一个 spot 可能混入多个细胞和多个谱系状态。Slide-tags 对单个细胞核测序，分子灵敏度和谱系状态更可靠，但只有约 50–70% 的细胞核能获得空间位置，覆盖也更稀疏。二者不是简单重复：Slide-seq 提供连续的组织生态图，Slide-tags 提供正交的单核细胞类型与谱系验证。

原始靶位点读段被整理成 character matrix：行是 spot/细胞，列是 intBC×切割位点，元素是 indel 状态，`-1` 表示缺失。Slide-seq spot 中若同时出现多个状态，作者比较 “all states”“collapse duplicates”“most abundant” 三种表示；模拟结果支持保留不同状态但折叠重复计数。代码通过 Cassiopeia 的 `collapse_duplicates` 参数生成这种矩阵（`utilities/reconstruct.py:427-435`）。

### 2. 利用空间邻域补全谱系条形码

Slide-seq 的靶位点缺失较多。作者基于一个经验前提：在迁移不强的局部区域，近邻癌细胞更可能共享谱系状态。对每个缺失字符，在 30 μm 邻域内收集有足够 UMI 支持的状态投票；只有一致比例达到阈值且预测状态既非缺失也非未切割状态 0 时才填入。代码建立 squidpy 半径图，并逐个缺失位置投票（`utilities/reconstruct.py:454-506`）。

论文报告使用 5 轮、0.8 一致性阈值，held-out 数据的中位插补准确率为 90%，平均恢复 31% 缺失值（范围 4–58%）。但发布代码的 API 默认是 1 轮和 0.7（`utilities/reconstruct.py:378-388`）。这可能意味着生产运行显式覆盖了默认值，也可能是版本差异；在缺少运行命令时只能标为 Partial，不能把默认参数写成与论文完全一致。

空间插补还有明确的生物学边界：如果细胞已经迁移，空间近邻不再意味着近亲，算法可能把邻居的条形码错误传给迁移细胞。作者用模拟、真实数据遮蔽和 Slide-tags 正交树检验其适用性，但这些检验不能消除所有迁移场景的偏差。

### 3. 从 character matrix 重建系统发育树

含冲突状态时，两个 spot 的字符距离取所有候选状态对中的最小加权 Hamming 距离；罕见 indel 由 $-\log p$ 获得更高信息权重。发布代码选择 Cassiopeia 的 `cluster_dissimilarity_weighted_hamming_distance_min_linkage`，并把 mutation priors 传入 `CassiopeiaTree`（`utilities/reconstruct.py:50-88`）。

Slide-seq 使用 Greedy+Neighbour Joining 混合树：Greedy 先恢复大分支，NJ 再解析较小亚克隆。代码确实组合 `VanillaGreedySolver` 和 `NeighborJoiningSolver`，但默认切换规模为 500 个细胞，而论文 Methods 写 1,000。Slide-tags 数据质量更高，采用 Greedy+ILP；代码给出 12,600 秒 ILP 收敛限制，并在求解后折叠无突变边（`utilities/reconstruct.py:158-229`）。

因此，这棵树代表由 Cas9 累积编辑支持的相对亲缘结构，不是具有绝对时间刻度的完整细胞历史。缺失编辑、同形突变和抽样不足都会降低分辨率。

### 4. 将空间表达压缩为 11 类组织 community

作者在每张 Slide-seq 阵列上用 Hotspot 寻找空间自相关基因模块，再按跨样本 Jaccard 相似度聚类，形成 11 个可重复 community，包括 alveolar、EMT、fibroblast、B cell、endothelial、inflammatory、scavenger macrophage 和 hypoxia 等。每个 spot 计算模块分数，并以最高分模块作为空间标签。

这些 community 是共定位的基因程序，不等于纯细胞类型。例如 hypoxia 或 EMT community 可以同时反映癌细胞状态与周围基质/免疫反应。发布仓库包含对既有共识模块的标准化和 `scanpy.score_genes` 评分代码，但没有最初的 Hotspot 运行及跨样本 Jaccard 聚类，因此该部分只能部分复现（`scripts/score_consensus_hotspot.py:43-79`；详见 `doc_code.md`）。

### 5. 谱系 fitness 与 plasticity

作者用 Local Branching Index（LBI）概括一个叶节点附近的分支密度；局部树分支越丰富，表示该亚克隆历史扩张越快。代码对 Slide-tags 用 IID exponential MLE 估计分支长度，对稀疏的 Slide-seq 则把每条边的突变数截到 0/1，再运行 `LBIJungle` 并按样本最大值归一化（`utilities/phylodynamics.py:31-59`）。

L2 plasticity 衡量一个细胞的空间表达 community 向量与谱系兄弟节点之间的差异：

$$
P_{L2}(i)=\frac{1}{|N_i|}\sum_{k\in N_i}\lVert C_i-C_k\rVert_2.
$$

代码先对每个细胞的 community 分数做 z 标准化，取同一父节点子树中的其他叶子，计算平均 Minkowski $p=2$ 距离，再归一化并截断极端分位数（`scripts/compute_slideseq_plasticities.py:40-48,95-108`）。高值表示同一近缘克隆内部状态更分散，不等于单个细胞正在即时转分化。

### 6. 主要生物学发现

Fig. 1 建立实验和计算流程，并显示空间插补后的谱系树。Fig. 2 将 11 类 community 映射到肿瘤进展：早期区域偏 alveolar、endothelial 和 inflammatory；晚期区域增加 EMT、hypoxia 和 fibroblast 程序。

Fig. 3 把树与空间生态结合。作者观察到一种动态：早期可塑性上升提供多样状态，随后高 fitness、低 plasticity 的亚克隆被选择并快速扩张；这些区域形成缺氧内部，同时伴随 Arg1+ 免疫抑制性巨噬细胞、myCAF、胶原与纤维化增加。配体–受体和类器官实验支持缺氧、TGFβ 与髓系/成纤维细胞重塑可能推动 EMT，但空间相关和计算通信本身不构成因果证明。

Fig. 4 追踪转移。多层组织切片用共享 indel 的 evolutionary coupling 对齐，从原发瘤中定位空间受限的 metastasis-initiating subclone。转移相关亚克隆在原发灶内已具有 EMT、缺氧、纤维化和免疫抑制特征；到达远端后仍维持 EMT，并把转移 niche 重塑为 TGFβ 活跃、富胶原的环境。56 位人类肺腺癌患者的单细胞数据（含 34 个脑转移）提供跨物种一致性支持，但不等于在人类中直接完成了同样的谱系追踪。

### 7. 可复现性和解释边界

本地代码可靠覆盖 character matrix、空间插补、Cassiopeia 混合树、LBI、L2 plasticity、watershed 分割和既有 community 评分。scVI/scANVI 注释、原始 Hotspot 共识构建、LARIS 配体–受体分析、inferCNV 和 Slide-tags DBSCAN 空间条形码处理未在仓库中找到。还应保留三处参数差异：一致性 0.7 默认值对论文 0.8；插补 1 轮默认值对论文 5 轮；Greedy–NJ 默认切换 500 对论文 1,000。

最稳妥的结论是：该平台揭示了快速扩张亚克隆与缺氧、纤维化、免疫抑制及低可塑性状态在空间上的共同出现，并定位了具有转移能力的原发灶亚克隆。它不能仅凭空间近邻或相关性证明微环境变化导致了亚克隆扩张，也不能把插补条形码当作直接测量。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## summary.md — Spatiotemporal Lineage Tracing in Lung Adenocarcinoma

**Paper**: Jones*, Sun* et al. "Spatiotemporal lineage tracing reveals the dynamic spatial architecture of tumour growth and metastasis"
**bioRxiv**: 10.1101/2024.10.21.619529
**Year**: 2024 (preprint, v2)
**Category**: datasource/atlases_resources — dataset + platform paper

---

### Motivation & Novelty

#### Biological Problem
Tumour progression is driven by sequential interactions between evolving cancer cells and their surrounding microenvironment, but the spatial and temporal ordering of these events — when hypoxia emerges, when cancer cells undergo epithelial-to-mesenchymal transition (EMT), from where metastases originate — has remained largely unknown because dissociated single-cell approaches destroy spatial context.

#### Limitations of Existing Approaches
- **Multi-region bulk sequencing** (Gerlinger et al., *N. Engl. J. Med.*, 2012; TRACERx, Jamal-Hanjani et al., *N. Engl. J. Med.*, 2017): captures genetic heterogeneity but lacks single-cell resolution and gene expression
- **Spatial genomics** (Zhao et al., *Nature*, 2022; Lomakin et al., *Nature*, 2022): resolves copy-number alterations spatially but cannot resolve deep phylogenetic relationships or simultaneously measure expression
- **Previous KP-Tracer single-cell** (Yang et al., *Cell*, 2022): high-resolution phylogenies but no spatial context; could not connect clonal expansions to microenvironmental niches

#### Unique Contributions
1. **First integration of spatial transcriptomics + Cas9 lineage tracing** in a tumour model at scale (44 Slide-seq + 5 Slide-tags arrays, >100 tumours)
2. **Novel computational methods** for phylogenetic reconstruction from spatial data: spatial imputation of missing lineage states, modified Hybrid Greedy+NJ for multi-cell spots, conflicting-state algorithms
3. **Discovery of spatial tumour architecture**: expanding subclones drive formation of a hypoxic core; hypoxia + immune/stromal remodelling together (not hypoxia alone) induce EMT
4. **3D metastatic origin mapping**: metastases traced to a spatially-confined subclone in one primary tumour; distant metastases show enhanced fibrosis on top of retained EMT/TGFβ signature
5. **Novel tumour cell state**: Piezo2+/Robo1+/Pecam1+/Nkx2-1+ neuronal-like cancer cells — invisible to CD31-depletion protocols used in dissociated scRNA-seq

---

### Method Overview

The platform integrates three components:

**1. KP-Tracer mouse model**: $Kras^{LSL-G12D/+}$; $Trp53^{fl/fl}$; Rosa26$^{LSL-Cas9}$ mice. Intratracheal adenovirus-Cre induces oncogene activation + lineage tracing in AT2 cells simultaneously. Cas9 introduces heritable indels at 13 intBCs (39 total cut sites) expressed as poly(A) transcripts — captured by spatial assays.

**2. Complementary spatial platforms**:
- **Slide-seqV2**: spot-based, 10µm resolution, large FOV; multiple cells per spot → conflicting allele states; high missingness
- **Slide-tags**: single-nucleus barcoding via UV-cleavable spatial barcodes; true single-cell resolution; lower throughput

**3. Computational pipeline** (see `doc_method.md`):
- Spatial imputation of missing lineage states from 30µm spatial neighbours (80% concordance, 5 iterations)
- Modified Cassiopeia-Greedy + Neighbour-Joining (Slide-seq) or Greedy + ILP (Slide-tags) handling conflicting allele states
- Phylogenetic fitness (LBI) and plasticity (L2 distance in community score space) quantified on reconstructed trees
- Spatial community detection via Hotspot → 11 consensus communities across 44 arrays
- Neighbourhood composition, evolutionary coupling, watershed segmentation for downstream analyses

---

### Evaluation

#### Datasets
- **Main cohort**: 44 Slide-seq + 5 Slide-tags arrays from KP-Tracer mice at 12–16 weeks post-initiation; >100 tumours across stages
- **3D metastasis experiment**: 4 Curio 1cm Slide-seq arrays (layers) + Slide-seq of mediastinal LN, rib, diaphragm metastases from one mouse
- **Validation — human LUAD**: 12 KRAS-mutant surgical resections (immunofluorescence)
- **Validation — published human NSCLC ST**: reanalysis of published spatial transcriptomics (Heiser et al., *Cell*, 2023)
- **Validation — human brain metastases**: Pan-cancer Brain Metastases Atlas (Xing et al., *Cancer Cell*, 2025); 22 LUAD primaries + 34 brain metastases

#### Key Metrics and Results
- Spatial imputation: 90% accuracy on held-out target sites (random baseline: 67%); recovers 31% of missing data on average (4–58% range)
- Phylogenetic fitness (LBI) correlates with transcriptional fitness signature (Pearson r=0.4, Extended Data Fig. 6b)
- Expanding subclones co-localise with hypoxic/EMT communities in systematic analysis of all 44 Slide-seq arrays
- Hypoxic community (C10) appears before EMT community (C3) along the fitness signature ranking (temporal ordering)
- Hypoxia alone: 2.5x induction of EMT markers (Vim, Twist1) vs normoxia in organoid co-culture
- Hypoxia + macrophage + mesenchyme co-culture: >2.5x fold-increase in Vim/Twist1 vs hypoxia alone
- All 3 metastatic sites (mediastinal LN, rib, diaphragm) traced to expanding subclone in T2 primary tumour
- Metastases show collagen gene upregulation (log2FC = 3.81, p < 1e-5) vs primary; sustained TGFβ signalling (log2FC = −0.14, p = 1.0)
- Human LUAD: GLUT1+/SPP1+ co-localisation significant (Fisher's Exact Test p < 1e-5)
- Human LUAD: VIM+ regions co-localise with GLUT1+ hypoxic regions (Fisher's Exact Test p < 1e-5)

---

### Reproducibility Rating: 3/5

**Justification**: The biological findings are reproducible in principle (with access to the raw data), but the computational pipeline requires significant effort beyond what is released.

**Strengths**:
- Core computational algorithms (imputation, reconstruction, fitness, plasticity) are released in a clean, well-structured Python package (`KPSpatial-release`) with Cassiopeia as the backbone
- Key parameters documented in paper Methods with sufficient detail
- Cassiopeia itself is a mature, published library (Jones et al., *Genome Biology*, 2020)
- Benchmark scripts for imputation accuracy are included

**Weaknesses / Pitfalls**:
- **Hardcoded developer paths** throughout: `sys.path.append("/Users/matthewjones/...")` must be corrected manually
- **Hotspot per-sample runs and cross-sample Jaccard clustering not in repo**: the 11 consensus communities cannot be reproduced without this code
- **scVI/scANVI cell typing not in repo**: cell type annotations (Fig. 2a-c, all neighbourhood analyses) cannot be reproduced
- **LARIS ligand-receptor analysis not released**: Supplementary Table 4 cannot be reproduced
- **Data not yet deposited**: "All raw and processed data will be made available on GEO and other public repositories" — not available at time of analysis
- **Parameter discrepancies**: imputation concordance 0.7 (code) vs 0.8 (paper); cell cutoff 500 (code) vs 1000 (paper); num_imputation_iterations default 1 vs 5 used in paper

**Practical notes**:
- Requires Cassiopeia 2.0.0, squidpy, scanpy, skimage, networkx; no requirements.txt provided
- Scripts process one sample at a time; sample lists are hardcoded in scripts
- The `evaluate_imputation_accuracy_semisynthetic.py` provides a standalone benchmark that is runnable

---

### Biological Significance

This study provides the first spatiotemporally resolved model of LUAD progression, revealing:

1. **Layered tumour architecture**: rapid subclonal expansion pushes early-stage AT2-like cells to the periphery, forming a hypoxic, immunosuppressive, fibrotic interior
2. **Causal ordering**: expansion → hypoxia → Arg1+ TAM + myCAF recruitment → EMT stabilisation (not the reverse)
3. **Synergistic EMT induction**: hypoxia alone is insufficient; immune and stromal co-culture required for full EMT (organoid experiment)
4. **Spatially-confined metastatic origins**: all metastases arise from a single expanding subclone; they co-opt the fibrotic niche and enhance collagen deposition at distant sites
5. **Human translation**: the hypoxia → immunosuppression → EMT cascade is conserved in human LUAD surgical resections and the Pan-cancer Brain Metastases Atlas

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
