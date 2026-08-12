---
layout: default
permalink: /paper-atlas/petracer-7d3de11b/
title: "PEtracer"
nav: false
description: "PEtracer 不是根据转录组相似性猜谱系，而是让细胞在分裂过程中持续积累可遗传的 prime-editing 标记，再在实验终点同时读取这些标记、细胞转录状态和组织空间位置。标记提供“共同祖先”的证据，MERFISH 或 scRNA-seq 提供“现在是什么状态”的证据，二者联合后才能研究一个状态究竟更像长期遗传结果，还是局部环境诱导的短暂反应。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Science · 2025</span>
    </div>
    <h1>PEtracer</h1>
    <p>High-resolution spatial mapping of cell state and lineage dynamics in vivo with PEtracer</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1126/science.adx3800" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PEtracer：把细胞的“家谱、状态和位置”读在同一张组织图上

论文：*High-resolution spatial mapping of cell state and lineage dynamics in vivo with PEtracer*（Science, 2025；DOI: 10.1126/science.adx3800）

### 一句话理解

PEtracer 不是根据转录组相似性猜谱系，而是让细胞在分裂过程中持续积累可遗传的 prime-editing 标记，再在实验终点同时读取这些标记、细胞转录状态和组织空间位置。标记提供“共同祖先”的证据，MERFISH 或 scRNA-seq 提供“现在是什么状态”的证据，二者联合后才能研究一个状态究竟更像长期遗传结果，还是局部环境诱导的短暂反应。

### 1. PEtracer 解决的矛盾

演化式谱系记录器需要很多可能状态，才能区分大量细胞；但 FISH 成像只能可靠地区分预先设计好的有限探针。Cas9 随机 indel 虽然多样，却不适合为每种未知 indel 预制探针。PEtracer 的折中是：

- 用 prime editing 只写入预定义的 5-nt lineage mark（LM）；
- 每个 edit site（ES）有 8 种 LM，探针集合有限且可事先设计；
- 每个 lineage tracing cassette（LTC）含 3 个 ES；
- 一个细胞通常整合多个、由 integration barcode（intBC）区分的 LTC，因此可用字符位点数远多于 3。

论文最终使用 24 种 LM，即 3 个 ES 各 8 种。这里要区分两个条形码层次：intBC 标识某个基因组整合拷贝，并可用于判断克隆；LM 是该拷贝上随时间积累的可遗传编辑状态，用来重建克隆内部的谱系树。

### 2. 实验记录器怎样工作

系统包含三部分：

1. **PEmax-P2A-GFP**：执行 prime editing，并用 GFP 报告编辑器表达。
2. **LTC**：位于 `mCherry` 的 3' UTR，含一个 intBC、3 个 ES，以及用于原位扩增的 T7/T3 启动子。intBC 同时有测序和成像码。
3. **pegArray**：编码 24 个 pegRNA，即每个 ES 的 8 种候选 LM。

PEmax 在尚未编辑的 ES 上随机安装一个预定义 LM。所选编辑会改变 PAM/seed 区域，从而降低再次编辑的可能；该状态随 DNA 复制传给后代。两个细胞若共享较晚出现的稀有 LM，通常比只共享早期、几乎遍布全克隆的 LM 更可能拥有较近的共同祖先。

但“共享标记”不等于直接观测到一次分裂。LM 数目有限，独立分支可能碰巧得到同一 LM（homoplasy）；位点也可能尚未编辑或未被检测。因此结果是由字符矩阵推断的系统发育树，而不是逐次分裂录像。

### 3. 为什么要调编辑速率、饱和度和 LM 均衡性

#### 3.1 饱和不能太早，也不能太晚

若编辑过快，许多位点在实验初期就固定，后期分裂没有新信息；若编辑过慢，大量位点保持未编辑，早期分支难以区分。论文模拟和降采样实验支持把最终编辑饱和度控制在约 60%–80%，并通过 pegRNA protospacer mismatch 把记录时间尺度调到数周。

代码中的动力学拟合使用饱和指数模型：

$$
f(t)=s\left(1-e^{-rt}\right),
$$

其中 $f(t)$ 是编辑比例，$s$ 是饱和值，$r$ 是速率。`kinetics/estimate_rates.py` 还人为加入 $(t=0,f=0)$ 锚点，并把 $s$ 约束在 0.8–1.0、$r$ 约束在 $10^{-4}$–0.6；这些是实现选择，不应误当成适用于所有体系的生物常数。

#### 3.2 八种 LM 要尽量均匀

如果某一种 LM 占绝大多数，名义上有 8 种状态，实际信息量仍很低。论文用归一化 Shannon entropy 比较 LM 安装频率：

$$
H_{norm}=-\frac{\sum_{k=1}^{K}p_k\log p_k}{\log K}.
$$

$H_{norm}=1$ 表示 $K$ 种 LM 完全均匀。图 1 的模拟表明 LM 数量和均衡性共同决定 RF 重建误差；最终 LM 还需兼顾 prime-editing 效率与 FISH 杂交可区分性。该设计计算主要位于实验设计 notebook，而不是 `petracer/` 主包 API。

### 4. 同一记录如何被两种平台读取

#### scRNA-seq 路径

LTC 放在高表达 `mCherry` 转录本的 3' UTR，因此 intBC 和 LM 可随转录本被单细胞测序捕获。`scripts/alleles_from_bam.py` 与 `scripts/barcodes_from_bam.py` 从 BAM 的 CB/UB 标签和 CIGAR 比对中提取细胞条码、UMI、intBC 与插入序列，再按 UMI/reads 聚合。

#### MERFISH 路径

组织成像先读内源 RNA，再消化样品并对基因组 LTC 做 in-gel T7 原位转录，形成可被 FISH 探针检测的局部 RNA 扩增点。17 轮三色成像的 50 bits 包括公共位、intBC 编码位、24 个 LM 位和 3 个未编辑位。这样同一细胞可同时得到坐标、转录状态、intBC 和 LM。

论文在预编辑细胞上报告：scRNA-seq intBC true-positive rate 为 98.5%，已检测整合上的 LM 调用准确率为 99.9%；成像 intBC 检出率为 81.8%，排除低置信 LM 后准确率为 99.4%。这些是特定验证数据的论文结果，不是软件对新样本的保证。

### 5. 从原始调用到字符矩阵

一个细胞的一行字符可写成：

$$
\mathbf c_i=(c_{i1},c_{i2},\ldots,c_{iM}),
$$

代码中 0 表示未编辑，1–8 表示八种 LM，-1 表示未检测；`alleles_to_characters()` 将 `(intID, ES)` 展开为列。低于概率阈值的成像 LM 会被置为 -1；默认 `min_edit_prob=0.7` 来自体外训练的 logistic-regression classifier，换细胞类型或成像条件时需要重新校准。

测序和成像的若干 QC 位于实验 notebook，而非单一命令式流水线，包括双组分 GMM 阈值、ambient RNA/低 reads 过滤和冲突 allele 处理。因而“仓库有主包”并不等于从原始数据到论文图可一键运行。

### 6. 距离与树拓扑

PEtracer 用 Cassiopeia 的 weighted Hamming distance 计算细胞间距离。仓库 `petracer/tree.py:hamming_distance()` 的逐位代价是：

- 状态相同：0；
- 未编辑 0 与任一 LM 不同：1；
- 两种不同 LM：2；
- 任一状态为 -1：该位不参与分母。

因此

$$
d(i,j)=\frac{\sum_{m\in D_{ij}}\delta(c_{im},c_{jm})}{|D_{ij}|},
$$

其中 $D_{ij}$ 是两细胞都检测到的位点。

例如 A 的三个状态为 `(0, 2, -1)`，B 为 `(3, 5, 7)`。前两位可比较，代价分别为 1 和 2，第三位缺失被忽略，所以 $d(A,B)=(1+2)/2=1.5$。不同 LM 的代价为 2，表达的是从共同未编辑祖先产生两个不同编辑至少需要两次写入，而“未编辑—已编辑”只需要一次。

`reconstruct_tree()` 默认调用 UPGMA，也支持 neighbor joining 和 greedy solver。论文体外基准图展示了 NJ；实际分析可按数据选择 UPGMA/NJ，因此不能把某一图中算法写成全项目唯一默认。`mask_truncal_edits()` 还会移除在超过 95% 已检测细胞中共享的同一非零 LM，因为这类 founder/truncal edit 几乎不能区分后续分支。

### 7. 从无根聚类到有生物含义的树

#### 7.1 祖先状态

拓扑得到后，`reconstruct_ancestral_characters()` 调用 pycea 的 Sankoff 动态规划。默认代价矩阵把“从未编辑 0 离开”的代价设为 `edit_cost=0.6`，其余不同状态通常为 1，对角线为 0。论文没有为 0.6 提供独立标定，因此它是需要做敏感性检查的实现参数。

#### 7.2 枝长

`estimate_branch_lengths()` 把拓扑和祖先字符交给 Cassiopeia `IIDExponentialMLE()` 估计枝长。它假设字符按独立同分布的指数过程演化；论文把相关步骤称为 ConvexML。枝长是模型估计的相对演化时间，不应自动解释为真实小时或细胞分裂次数。

#### 7.3 无新突变边与多分叉

`collapse_mutationless_edges()` 会折叠父子字符没有变化的内部边。这样做诚实地保留“现有 LM 无法排序这些分裂”的不确定性，得到多分叉，而不是人为制造精确二叉顺序。

### 8. 如何验证树没有只是在“画得像树”

作者在第 5 天和第 7 天引入静态 barcode，作为已知时间的谱系分组，再比较这些分组与 LM 树上的最低共同祖先 clade。`get_barcode_clades()` 对每个 barcode 遍历所有节点，计算：

$$
FMI=\sqrt{precision\times recall},
$$

并选择 FMI 最大的节点。论文报告六棵体外树的 FMI 约 0.85–1.00；降采样显示超过约 20 个 ES 且检测率超过约 60% 时重建较稳健。这是 4T1/B16F10 和论文参数范围内的经验边界，不应直接当作其他组织的通用合格线。

### 9. 谱系怎样与空间和细胞状态连接

树的叶是细胞，MERFISH 为同一叶提供二维/三维坐标、基因表达和细胞类型。随后可问三类不同问题：

1. **空间与谱系是否一致**：比较细胞对的系统发育距离和欧氏空间距离，或观察 clade 是否形成空间域。
2. **状态是否可遗传**：在谱系邻接关系上用 Moran's $I$ 衡量表达模块/基因的系统发育自相关。实现调用外部 `pycea`，不是 `petracer` 自己实现的统计量。
3. **哪些分支近期扩张更快**：`estimate_leaf_fitness()` 用 Cassiopeia `LBIJungle()` 从带枝长的局部分支结构估计叶 fitness。它是谱系形状导出的相对扩张指标，不是直接测得的细胞增殖率，也不是基因型适合度的因果证明。

论文在 4T1 肺肿瘤中据此观察到：clade 占据不同空间区域；肿瘤—肺边界附近出现高 fitness 扩张；某些转录模块在谱系上更具遗传性，而另一些更随局部环境变化。PEtracer 的贡献在于让“遗传历史”和“当前微环境”能在同一细胞层面被区分，而不是单靠表达相似度推断因果。

### 10. 论文机制与本地代码的对应

| 环节 | 本地入口 | 对应程度 | 边界 |
|---|---|---|---|
| LM/编辑速率模拟 | `simulation/simulate.py` | Exact/Partial | 使用 Cassiopeia 模拟器；实验选择仍在 notebooks |
| BAM allele/intBC 提取 | `scripts/alleles_from_bam.py`, `scripts/barcodes_from_bam.py` | Exact | 后者含机构路径硬编码，移植前需修复 |
| allele 到字符 | `petracer/tree.py:alleles_to_characters()` | Exact | 0、1–8、-1 语义明确 |
| weighted Hamming | Cassiopeia solver 与 `tree.py:hamming_distance()` | Exact | 主 solver 调 Cassiopeia 实现；本地函数展示相同代价逻辑 |
| UPGMA/NJ/greedy | `tree.py:reconstruct_tree()` | Exact | UPGMA 是函数默认，论文不同实验也展示 NJ |
| Sankoff 祖先状态 | `tree.py:reconstruct_ancestral_characters()` | Partial | `edit_cost=0.6` 未由论文解释 |
| 枝长 | `tree.py:estimate_branch_lengths()` | Exact/Partial | 调 `IIDExponentialMLE()`；绝对时间解释受模型限制 |
| fitness | `tree.py:estimate_leaf_fitness()` | Partial | 代码为 `LBIJungle()`，与论文“Jungle”命名需谨慎对应 |
| 静态 barcode FMI | `petracer/barcode.py:get_barcode_clades()` | Exact | 每组选择 FMI 最大 clade |
| MERFISH LM classifier/QC | `preedited/`, `tumor_tracing/` notebooks | Notebook | 不是稳定的主包 API |
| Moran's I、状态模块、label transfer | notebooks + pycea/Hotspot/resolVI | Partial/External | 依赖外部工具和数据集特定步骤 |

### 11. 复现和解释时最容易越界的地方

- **树不是地面真值**：有限 LM、缺失、同形编辑和阈值都会改变拓扑。
- **阈值不是通用常数**：0.7 LM probability、60% intBC detection、95% truncal mask 都应在新实验中校准或做敏感性分析。
- **fitness 不是直接增殖测量**：它由树的局部分支模式推断，并依赖枝长和拓扑。
- **空间相关不等于环境因果**：谱系和位置都可能受共同的迁移、选择或采样过程影响。
- **代码快照不是完整原始数据包**：仓库提供分析包和大量 notebooks，但原始大型图像、显微镜流程及部分外部资源仍是复现边界。
- **入口脚本存在可移植性问题**：`scripts/barcodes_from_bam.py` 通过硬编码机构路径推导资源目录，不能原样视作通用 CLI。

### 12. 建议的阅读顺序

先读论文图 1 理解记录器设计，再读图 2 的双平台检测准确性、图 3 的静态 barcode 树验证、图 4–5 的空间肿瘤应用。代码侧依次看 `petracer/config.py`、`seq.py`、`tree.py`、`barcode.py`，最后再进入 `preedited/`、`barcoded_tracing/` 和 `tumor_tracing/` notebooks。这样能把“实验生成什么证据”“算法如何变成树”“论文如何用树解释生物学”三个层次分开。

### 证据范围

本文基于本地 `paper.md`、主图与图注、仓库快照 `PEtracer-2025`（commit `3a8076a2ac4d6a99f305c4ae1caa984b77188549`）及其直接源码整理。论文数值是对作者实验结果的转述；本次没有重新运行原始 MERFISH/scRNA-seq 数据，也没有独立复算论文树与统计检验。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## PEtracer: High-Resolution Spatial Mapping of Cell State and Lineage Dynamics In Vivo

**Paper**: Koblan LW, Yost KE, Zheng P, et al. "High-resolution spatial mapping of cell state and lineage dynamics in vivo with PEtracer." *Science* 390(6770), 2025. DOI: 10.1126/science.adx3800

**Authors**: Luke W. Koblan, Kathryn E. Yost, Pu Zheng, William N. Colgan, Matthew G. Jones, Dian Yang, Arhan Kumar, et al. (Weissman, Yosef, Zhuang labs, MIT/Harvard/UC Berkeley)

---

### Motivation & Novelty

#### Biological Problem

Charting how cells divide, differentiate, and migrate over time — and how this history shapes tissue organization in disease — is a fundamental challenge in biology. In cancer biology specifically, understanding which cell lineages grow fastest and why requires knowing simultaneously: (1) what transcriptional state each cell is in, (2) where the cell is in the tissue, and (3) which cells are related by descent.

#### Limitations of Existing Approaches

- **Static lineage tracers** (Cre-lox, dye injection): mark cells at one time point, reveal progenitor→progeny relationships but lose temporal dynamics. *Cell* 2019, *Nature Methods* 2020 (various).
- **Cas9-based evolving tracers** (GESTALT, LARRY, Cospar): continuously install marks and enable phylogenetic reconstruction with transcriptome-wide readout; however, Cas9 creates hundreds of distinct random indels — too many for imaging-based (FISH) readout. Yang et al., *Science* 2022; Weinreb et al., *Science* 2020; Frieda et al., *Science* 2017.
- **Imaging-based lineage tracers** (CloneTracer, seqFISH+lineage): preserve spatial context but have limited lineage depth or readout capacity. Frieda et al., *Science* 2017; Bhatt et al., *Nature Methods* 2023.
- **Existing spatial transcriptomics** (Slide-seq, Visium, MERFISH): provide cell state and spatial information but no lineage. Rodriques et al., *Science* 2019.

No prior system combined high-depth evolving lineage tracing with single-cell spatial transcriptomics at tissue scale in vivo.

#### Unique Contributions of PEtracer

1. **Prime editing-based lineage marks**: PE2 installs predefined, immutable 5-nucleotide (5nt) sequences at three edit sites. Only 8 LMs per site (24 total) are used — exactly enough for FISH-based discrimination without the complexity of Cas9 indels.
2. **Dual readout compatibility**: the same lineage cassettes are readable by both scRNA-seq and MERFISH imaging. This is enabled by in-gel T7 transcription of integrated cassettes for FISH amplification.
3. **First demonstration of spatially resolved evolving lineage tracing in vivo**: PEtracer × MERFISH applied to metastatic tumor growth, reconstructing 3D phylogenies with spatial coordinates and full transcriptomic annotation.
4. **Systematic system design**: guided entirely by in silico simulation (Robinson-Foulds, triplet metrics) → empirical tuning (1,024 LM screen, kinetics screen) → rigorous validation (static barcode FMI, downsampling).

---

### Method Overview

PEtracer has three components:
1. **PEmax editor**: lentiviral PE2 fused to GFP; constitutively expressed
2. **Lineage Tracing Cassettes (LTCs)**: integrated in 3' UTR of mCherry; each contains a 183nt imaging barcode (intBC), a 30nt sequencing barcode, and three edit sites (ES1/RNF2, ES2/HEK3, ES3/EMX1) with T7/T3 promoters for in situ amplification
3. **pegArrays**: 24-mer arrays encoding 8 LMs per ES; expressed from BFP-linked constructs

**Lineage recording**: PE2 stochastically installs one of 8 predefined 5nt sequences at each ES. These marks are immutable (PAM/seed altered to prevent re-editing) and heritable. Multiple LTCs per cell (mean 10–15) increase resolution.

**Computational pipeline**: Allele calling from BAM → GMM-based QC → character matrix → UPGMA/NJ tree reconstruction → Sankoff ancestral reconstruction → ConvexML branch lengths → LBIJungle fitness → Moran's I heritability.

**Key technical innovations**:
- NUPACK simulation for LM discriminability by hybridization (ΔΔG criterion)
- Orthogonalized edit sites prevent editing of endogenous genomic loci
- Modified in-gel T7 transcription with tissue clearing for in vivo FISH amplification
- Proseg (v1.1.3) for cytoplasm inference from nuclear expression profiles
- resolVI for MERFISH label transfer and cell type annotation

---

### Evaluation

#### Datasets

| Dataset | Cells | Platform | Purpose |
|---|---|---|---|
| In vitro 4T1 (fully edited) | 6,883 | scRNA-seq | Sequencing accuracy validation |
| In vitro 4T1 (imaging) | 5,614 | MERFISH | Imaging accuracy validation |
| In vitro 4T1 (static barcodes) | ~30,000 | scRNA-seq | Phylogenetic reconstruction validation |
| In vitro 4T1 colonies | 18,675 | MERFISH | Spatial-phylogenetic correlation |
| In vivo mice 1–2 (124-gene MERFISH) | 368,722 | MERFISH + lineage | Tumor evolution study |
| In vivo mouse 3 (175-gene MERFISH) | 104,219 | MERFISH + lineage | Module heritability study |

#### Key Metrics

| Measurement | Result |
|---|---|
| scRNA-seq intBC true positive rate | 98.5% |
| scRNA-seq LM calling accuracy | 99.9% |
| MERFISH intBC detection rate | 81.8% (in vitro), 55.2±9.7% (in vivo) |
| MERFISH LM decoding accuracy | 99.4% (after low-confidence exclusion) |
| In vitro FMI (static barcodes) | 0.85–1.00 (near-perfect phylogeny) |
| Reconstruction thresholds | >20 ESs, >60% detection rate |
| Edit saturation (optimal range) | 60–80% |
| Phylogenetic fitness: tumor-lung interface enrichment | p < 0.05; negative correlation with boundary distance |
| Lung-adjacent module heritability (Moran's I) | Highest across 4 modules (table S26) |

#### Biological Findings

1. **Tumor growth is structured by lineage**: Phylogenetic clades occupy distinct spatial territories with consistent patterns across tissue sections.
2. **Fitness is highest at the tumor-lung interface**, not the leading edge — despite the leading edge having slightly more cycling cells. This distinction requires simultaneously knowing lineage history (integrated over weeks) and spatial position.
3. **Four transcriptional modules** of cancer cells: "lung adjacent" (highest fitness, most heritable), "leading edge" (transient, environmentally driven), "hypoxic" (Vegfa+, near vasculature), "tumor core" (no distinct signature).
4. **Cell-intrinsic drivers**: *Cldn4* (Claudin 4) expression is heritable across many cell divisions, suggesting epigenetic stability. *Fgf1/Fgfbp1* expression is spatially restricted but less heritable — paracrine/autocrine signaling.
5. **Transcriptional plasticity**: Despite clear module heritability, cells show plasticity — neighboring clades mix modules. The lung-adjacent state can be partially acquired by moving cells.

---

### Reproducibility

**Rating: 4/5**

**Justification**:
- Complete code repository with exact analysis notebooks (https://github.com/jweissmanlab/PEtracer-2025)
- All plasmids deposited on Addgene (editor #238541, LTC library #238548, pegArrays #238542–238545)
- Conda environment with pinned versions provided (`environment.lock.yml`)
- Image processing SLURM scripts provided (but require institutional HPC)
- MERlin config files provided

**Strengths**:
- Python package `petracer/` is clean, modular, and well-structured
- Notebooks are per-experiment and highly reproducible within their scope
- Comprehensive table supplements (30 tables, including all barcode whitelists, edit rates, probe sequences)
- Full MERFISH probe library sequences in table S21/S25

**Weaknesses / Practical Notes**:
- Raw sequencing data and MERFISH images not in repository (large files; would need GEO/SRA deposit)
- MERFISH requires specialized custom microscope hardware (home-built system based on Zhuang lab design)
- In vivo experiments require specific mouse crosses (Balbc/J × SELECTIV, JAX #037553) with IACUC approval
- MERlin (external) requires installation and configuration separately
- The `petracer` package version is 0.0.1 (developmental) — no formal releases; breaking changes possible
- Core analysis depends on Cassiopeia, pycea, treedata — relatively niche packages with potential compatibility issues
- Kinetics/edit rate estimation requires running CROP-seq lentiviral screens before the actual experiment; computationally guided but empirically intensive setup

**Common pitfalls**:
- The `edit_cost=0.6` parameter in Sankoff ancestral reconstruction is not explained in the paper; changing it affects ancestral state inference
- The `min_edit_prob=0.7` logistic regression threshold (in `config.py:51`) was tuned on in vitro fully-edited data; may need re-calibration for other cell types
- GMM adaptive thresholding for LM QC is implemented in notebooks, not in the main package — each analysis re-runs this per experiment
- intBC detection rate >60% cutoff is validated for 4T1 and B16F10; other cell types/edit rates may require recalibration
- MERFISH alignment between imaging rounds uses TV-L1 optical flow — computationally expensive; requires scikit-image v0.24.0+ for the specific API used

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
