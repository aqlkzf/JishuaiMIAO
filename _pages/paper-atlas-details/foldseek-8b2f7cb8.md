---
layout: default
permalink: /paper-atlas/foldseek-8b2f7cb8/
title: "Foldseek"
nav: false
description: "Foldseek 的核心技巧是把每个残基与空间近邻的三维关系压缩成 20 种 3Di 字母之一。一个蛋白结构由此变成“氨基酸序列 + 3Di 序列”，可以先用 MMseqs2 式 k-mer 预过滤排除绝大多数不相关结构，再只对少量候选做局部 Smith–Waterman 比对。它用少量结构信息损失，换来相对传统结构比对器四到五个数量级的速度提升。"
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
      <span>Protein &amp; Sequence Models</span>
      <span>Nature Biotechnology · 2024</span>
    </div>
    <h1>Foldseek</h1>
    <p>Fast and accurate protein structure search with Foldseek</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-023-01773-0" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Foldseek">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/steineggerlab/foldseek" target="_blank" rel="noopener noreferrer" aria-label="Open code for Foldseek">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Foldseek：把三维结构搜索改写成高速序列搜索

### 一句话理解

Foldseek 的核心技巧是把每个残基与空间近邻的三维关系压缩成 20 种 3Di 字母之一。一个蛋白结构由此变成“氨基酸序列 + 3Di 序列”，可以先用 MMseqs2 式 k-mer 预过滤排除绝大多数不相关结构，再只对少量候选做局部 Smith–Waterman 比对。它用少量结构信息损失，换来相对传统结构比对器四到五个数量级的速度提升。

### 为什么结构搜索很慢

同源蛋白的结构通常比序列保守，因此结构搜索能发现序列搜索漏掉的远缘关系。但 TM-align、Dali、CE 等方法直接操作坐标、反复优化对应关系或空间叠合；在上亿个 AlphaFold 结构中逐一运行代价不可接受。论文估计，用单 CPU 核把一个查询与一亿个结构比较，TM-align 约需一个月；对一亿结构做 all-versus-all，即使用 1000 核也会以千年计。

序列搜索快，是因为相似 k-mer 能先筛掉绝大多数目标。传统结构字母多描述连续 3–5 个 $C_\alpha$ 的局部骨架形状，相邻字母高度相关、状态频率偏斜，而且在可变 loop 中信息反而较高，不适合灵敏的 k-mer 过滤。Foldseek 因此不编码“这段骨架像螺旋还是转角”，而编码跨序列位置的三级接触几何。

### 3Di 字母如何得到

#### 1. 为每个残基选择空间邻居

对残基 $i$，算法先从其 $C_\alpha$、$C_\beta$ 和 N 原子构造一个虚拟中心。论文优化出的参数为角度 $\theta=270^\circ$、二面角 $\tau=0^\circ$、距离 $d=2$ 个 $C_\alpha$–$C_\beta$ 单位。与 $i$ 的虚拟中心最近的另一个残基记为 $j$。

虚拟中心并不是装饰性的坐标变换。若直接用 $C_\alpha$ 最近邻，序列相邻的 $i\pm1$ 往往总是最近，得到的仍主要是局部骨架信息。把中心朝侧链/接触方向平移后，更容易选到远距离序列位置上的三级接触。

#### 2. 提取十维几何描述

围绕 $i$ 和 $j$ 各取前一位、当前位和后一位的 $C_\alpha$，构造方向向量。特征包括七个向量点积、$C_{\alpha i}$ 与 $C_{\alpha j}$ 的欧氏距离，以及两个带方向的序列距离变换。于是每个残基得到十维向量 $x_i$。这组特征同时描述两个局部骨架怎样相向、接触距离多远，以及它们在序列上相隔多远。

#### 3. 用 VQ-VAE 学 20 个状态

作者不是手工划分十维空间，而是从 SCOPe40 的同源结构对中取得 TM-align 对齐的残基对，训练修改后的向量量化自编码器。编码器把十维特征压到二维，再选择最近的 20 个 codebook 中心之一。训练目标不是精确重构同一个输入，而是用一个残基的状态预测其同源对齐残基的几何特征，使字母优先保留进化上稳定的结构信号。

论文使用 TM-score 至少 0.6 且对齐 $C_\alpha$ 距离小于 5 Å 的训练对，按 SCOPe fold 切分训练/验证，训练 100 个初始化并选择验证表现最好者。最终推断只保留小型编码器与 codebook；本地 `data/encoder_weights_3di.kerasify` 存放已转换权重，结构创建代码调用内嵌编码器生成 3Di 状态。

### 从结构文件到搜索数据库

`createdb`/`createdb` 工作流把 PDB、mmCIF、Foldcomp 或归档中的结构转换为并行数据：氨基酸序列、3Di 序列和 $C_\alpha$ 坐标。坐标可压缩存储；仅有 $C_\alpha$ 时可借助 PULCHRA 重建骨架，甘氨酸缺少 $C_\beta$ 时使用几何规则补出虚拟位置。

这意味着 3Di 搜索本身主要在一维字母上运行，但最终 LDDT、TM-score、可视化和叠合仍需要坐标。“结构被转换成序列”不等于后续完全丢弃三维信息。

### 搜索漏斗

#### 第一层：双 k-mer 同对角线预过滤

Foldseek 复用 MMseqs2 的预过滤框架，在 3Di 序列中寻找高替换分数的 spaced k-mer。数据库规模决定 $k=6$ 或 $7$。只有两个相似 k-mer 落在动态规划矩阵同一对角线上，才形成候选；随后沿该对角线做无 gap 评分，至少 15 bit 的候选进入精细比对。

同一对角线意味着两个词之间的相对位移一致，随机命中的概率远低于单个 k-mer。局部 composition-bias correction 又抑制由重复或偏斜 3Di 字母造成的伪命中。预过滤是速度来源，也是灵敏度边界：没有形成双词命中的真实远缘结构不会进入下一阶段，提高 sensitivity 参数会增加候选和计算量。

#### 第二层：3Di 与氨基酸联合 Smith–Waterman

对留下的候选，`structurealign` 用 SIMD 向量化的局部 Smith–Waterman。每个对齐位置的分数线性组合氨基酸和 3Di 替换分数：

$$
S(i,j)=1.4\,S_{AA}(a_i,a_j)+2.1\,S_{3Di}(u_i,u_j).
$$

权重和 gap 参数在 SCOPe40 子集上优化。3Di 权重更高，但氨基酸仍可帮助区分几何相似却无进化关系的结构。代码中的 `StructureSmithWaterman.cpp` 建立 AA 与 3Di 两套 query profile，执行 SIMD 动态规划，并保留反向 query 序列用于后续校正。

#### 第三层：抑制偏斜和反向伪匹配

局部重复或低复杂度结构字母可能产生高分。Foldseek 对 AA 与 3Di 都做局部 composition-bias correction，并把反转 query 与 target 的比对 bit score 从正向分数中减去。反向序列保留组成但破坏真实顺序，因此仍能在反向上得高分的部分更像组成偏差，而不是可信同源排列。

#### 第四层：坐标质量重排

Smith–Waterman bit score 适合快速局部同源检测，但不直接衡量三维几何。默认结果以 structural bit score 排序：

$$
S_{struct}=S_{bit}\sqrt{LDDT_{avg}\,TM_{ali}}.
$$

LDDT 比较对齐残基局部邻域距离是否保持，不要求全局叠合；alignment TM-score 衡量整体几何一致性。几何平均要求二者共同较好，避免只靠字母分数或单一坐标指标占优。Foldseek 的快速 LDDT 用 15 Å 空间网格，只检查相邻网格中的原子对；每个距离差按 0.5、1、2、4 Å 四个阈值计分。

### E-value 是怎样校准的

传统序列搜索的极值分布参数不能直接套在 3Di 分数上。作者对 10 万个 AlphaFoldDB 查询与随机打乱目标做多次比对，为每个查询拟合 Gumbel 分布参数 $\mu$ 和 $\lambda$，再训练一个小型神经网络从查询长度和氨基酸组成预测这两个参数。

在打乱序列测试中，报告 E-value 与实际假阳性数量的 log–log 斜率约为 0.32 而非 1，因此最终对神经网络 E-value 取 $0.32$ 次幂作经验修正。E-value 是特定模型、数据库规模和校准流程下的期望随机命中数，不是“同源概率”；代码还可根据 SCOPe 真/假匹配分布另报同源概率。边界分数需要结合覆盖度、LDDT/TM-score、结构域组成与功能证据判断。

### Foldseek-TM 与局部搜索不是一回事

默认 Foldseek 用 3Di/AA 局部比对，擅长发现共享结构域，即使多结构域蛋白的相对取向不同也可命中。`--alignment-type 1` 的 Foldseek-TM 仍先用 3Di 预过滤，但候选阶段改用内置 TM-align，并按平均 query/target-normalized TM-score 排序；它强调全局可叠合性。

因此默认 Foldseek 高分而全局 TM-score 较低不必然是错误。论文检查 AlphaFoldDB 高分“假阳性”时，很多结构包含多个正确折叠片段，但域间相对方向不一致；局部方法正确对齐了片段，基于全局 TM-score 的标签却将其计为假阳性。反过来，若问题是完整 fold 的全局几何等价，Foldseek-TM 更合适。

当前本地工作流还列出 LoLAlign、多聚体搜索、GPU 预过滤和 ProstT5 相关路径，这些是论文核心实现之外的后续扩展。不能用当前 CLI 的所有功能倒推 2024 论文 commit 已包含它们。

### 怎样读论文两张主图

图 1a 是算法漏斗：结构先离散成序列，双 k-mer 同对角线命中后做无 gap 过滤，最后做有 gap 局部比对并返回结构对应。图 1b 从左到右解释 3Di：虚拟中心选择邻居、十维特征、VQ-VAE codebook、输出 3Di 字母。图中的 decoder 只在训练字母表时使用，不在每次数据库搜索中重建坐标。

图 2a、b 在 SCOPe40 上比较远缘同源检测。Foldseek 的 superfamily 灵敏度约为 Dali 的 86%、TM-align 的 88%，高于 CE；Foldseek-TM 的 precision–recall 表现最好。图 2c 把速度与灵敏度放在一起，显示 Foldseek 牺牲少量灵敏度换取巨大速度收益。不同工具的点来自特定版本、参数和硬件，不能当作今天所有版本的固定倍数。

图 2d 是多结构域、reference-free 基准：横轴是在第一个假阳性前找到的真阳性数，纵轴是 query 残基覆盖；Foldseek 与慢速结构工具接近。图 2e 同时展示多结构域局部对齐与 HOMSTRAD 专家对齐的 sensitivity/precision，说明搜索灵敏不等于每个残基对应都最准确。图 2f 比较 Foldseek 与 Dali 对齐 $F_1$，多数接近但存在离群点。

论文报告在 SCOPe40 上 Foldseek 比传统结构比对器快约 4,000–21,000 倍；在 AlphaFoldDB v1 案例中，一个 SARS-CoV-2 RdRp 查询用约 6 秒，而 TM-align 约 33 小时、Dali 约 10 天。这里的“秒级”依赖预建数据库、索引、硬件、线程与缓存，不能理解为从原始上亿结构建库也只需几秒。

### 本地代码与论文证据的边界

本地工作区包含 Foldseek 主 C++ 源码和 `foldseek-analysis` 训练/基准脚本。核心映射直接可见：

- `src/workflow/StructureSearch.cpp` 组织预过滤、alignment type 和结果阶段；
- `src/strucclustutils/structureto3didescriptor.cpp` 把结构转成 3Di descriptor；
- `src/commons/StructureSmithWaterman.cpp` 实现联合 AA/3Di SIMD 比对、反向 query 和 composition bias；
- `src/commons/LDDT.cpp` 与 TM-align 代码提供坐标重评分；
- `foldseek-analysis/training/` 保存 VQ-VAE、替换矩阵和基准复现脚本；
- `data/encoder_weights_3di.kerasify` 与 `data/evalue_nn.kerasify` 是训练后权重。

论文方法基准明确使用 Foldseek commit `aeb5e` 和固定的比较工具版本。当前目录没有保留可解析的 Git commit，`src/version/Version.cpp` 在没有构建时注入 `GIT_SHA1` 的情况下只会报告 `UNKNOWN`，而源码显然含有后续功能。因此核心原理可直接核对，但严格复现实验应检出论文 commit，而不是假定当前快照等同于 `aeb5e`。

补充材料没有作为单独 Markdown/PDF 存在；当前 paper Markdown 收录了大量 Methods 与扩展说明，但不能声称已独立核验所有补充图。CodeGraph 在本轮因数据库锁失败，最终代码结论来自上述聚焦源码直接读取。

### 实际使用边界

- 默认是局部结构同源搜索，不是保证全长全局叠合的分类器。
- 3Di 离散化会丢失原子细节；配体、侧链化学和柔性状态不由单条 3Di 序列完整表达。
- 预测结构的错折叠、低 pLDDT 区域和错误域取向会传到搜索结果。
- E-value 和 homology probability 是模型校准值，不替代人工检查覆盖、结构域边界和生物学背景。
- 灵敏度参数越高通常越慢；预建索引能加速重复查询，但需要显著存储/内存，建库成本也必须计入。
- 相似结构支持共同祖先或相似物理约束的假说，并不单独证明功能相同。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Foldseek: Fast and Accurate Protein Structure Search

**Paper**: van Kempen M, Kim SS, Tumescheit C, Mirdita M, Lee J, Gilchrist CLM, Söding J, Steinegger M. *Nature Biotechnology* 42, 243–246 (2024). DOI: [10.1038/s41587-023-01773-0](https://doi.org/10.1038/s41587-023-01773-0)

**Code**: [https://github.com/steineggerlab/foldseek](https://github.com/steineggerlab/foldseek) (GPLv3)

**Analysis Scripts**: [https://github.com/steineggerlab/foldseek-analysis](https://github.com/steineggerlab/foldseek-analysis)

---

### Motivation and Novelty

#### Problem
Structure prediction methods (AlphaFold2, ESMFold) have generated hundreds of millions of protein structures, but searching these databases for structural similarity is prohibitively slow. TM-align would take **one month per query** to search 100 million structures on a single CPU core. An all-versus-all comparison of 100 million structures would take **10 millennia** on a 1,000-core cluster.

#### Why Existing Approaches Fall Short
1. **Structural aligners** (TM-align, Dali, CE) are inherently slow because structural similarity scores are non-local — changing an alignment in one region affects scores globally, requiring iterative optimization.
2. **No fast prefilter** exists for structure comparison analogous to k-mer matching in sequence search.
3. **Traditional structural alphabets** (CLE, 3D-BLAST, Protein Blocks) discretize local backbone conformations of 3–5 $C_\alpha$ atoms, which suffer from high dependency between consecutive letters, uneven state frequencies, and low information density in conserved regions.

#### Key Innovation: 3Di Structural Alphabet
Foldseek introduces the **3Di (3D interaction)** alphabet — a 20-state discrete representation that encodes **tertiary residue–residue interactions** rather than backbone conformations. For each residue $i$, the 3Di state describes the geometric conformation with its spatially closest neighbor $j$, defined by a virtual center that preferentially selects long-range contacts.

Three critical advantages of 3Di over backbone alphabets:
1. **Weaker dependency between consecutive letters** — enhances k-mer prefilter sensitivity
2. **More uniform state frequencies** — reduces false positives
3. **Highest information density in conserved protein cores** (not in variable loops)

---

### Method Overview

#### Pipeline (Fig. 1a)
1. **Database creation**: Convert PDB/mmCIF structures → 3Di sequences + amino acid sequences + $C_\alpha$ coordinates
2. **Prefiltering**: Fast k-mer matching on 3Di sequences using MMseqs2's double-diagonal prefilter
3. **Alignment**: SIMD-accelerated Smith–Waterman combining 3Di ($\times 2.1$ weight) and amino acid ($\times 1.4$ weight) substitution scores
4. **Scoring**: Structural bit score = bit score $\times \sqrt{\text{LDDT} \times \text{TM-score}}$

#### 3Di Alphabet Construction (Fig. 1b)
1. Define **virtual center** ($\theta = 270°$, $\tau = 0°$, $d = 2$ CA–CB units) to select structurally informative nearest neighbors
2. Extract **10 conformational features**: 7 dot products between unit vectors along $C_\alpha$ backbone fragments, Euclidean $C_\alpha$ distance, and 2 sequence-distance features
3. Train a **modified VQ-VAE** (vector quantized variational autoencoder) on structurally aligned residue pairs from SCOPe40 to learn 20 states maximally conserved in evolution
4. The VQ-VAE encoder maps 10D features → 2D embedding → nearest of 20 centroids = 3Di state

#### Alternative Alignment Modes
- **Foldseek-TM**: Uses 3Di prefilter + TM-align for global structural alignment
- **LoLAlign**: Local log-odds alignment for multi-domain proteins

---

### Evaluation

#### Benchmarks
| Benchmark | Dataset | Metric |
|-----------|---------|--------|
| Homology detection | SCOPe40 (11,211 domains, 40% seq. id. clustered) | AUC up to 1st FP at family/superfamily/fold level |
| Precision-recall | SCOPe40 | Area under PR curve |
| Multi-domain sensitivity | AlphaFoldDB v1 (34,270 clusters, 100 queries) | Per-residue coverage vs. TP rank |
| Alignment quality | AlphaFoldDB v1 (100 queries × top 5 hits) | Sensitivity vs. precision of aligned residues |
| Reference alignment | HOMSTRAD (1,032 families) | Sensitivity/precision vs. expert curated alignments |

#### Key Results

The paper reports Foldseek achieves **86% of Dali's**, **88% of TM-align's**, and **133% of CE's** superfamily sensitivity (AUROC1). In precision-recall, Foldseek-TM has the highest AUC and Foldseek ranks 3rd.

| Metric | Foldseek | Foldseek-TM | Dali | TM-align | CE |
|--------|----------|-------------|------|----------|-----|
| SCOPe superfamily AUROC1 | 86% of Dali | Highest | Reference | Similar to FS-TM | 75% of Dali |
| SCOPe superfamily PR-AUC | 3rd | **1st** | 2nd | Below FS-TM | Lower |
| Multi-domain coverage | Competitive | Competitive | Competitive | Competitive | Competitive |
| HOMSTRAD $F_1$ | Slightly below | — | Good | Good | Good |
| **Speed (SCOPe40)** | **1× (ref)** | **47×** | **19,989×** | **34,822×** | **158,222×** |
| **Speed (AlphaFoldDB v1)** | **6 s/query** | — | **10 days** | **33 hours** | — |

#### Speed Summary
- **4,000–21,000× faster** than traditional structural aligners on SCOPe40
- **23,000–184,600× faster** on AlphaFoldDB v1
- Foldseek searches 100M structures in seconds; TM-align takes a month

---

### Reproducibility Assessment

#### Rating: **4 / 5** (High Reproducibility)

#### Strengths
1. **Open source** (GPLv3): Complete C++ codebase with CMake build system
2. **Analysis scripts provided**: VQ-VAE training, substitution matrix generation, all benchmarks at [foldseek-analysis](https://github.com/steineggerlab/foldseek-analysis)
3. **Pre-built databases**: AlphaFoldDB, PDB, ESM Atlas available via `foldseek databases` command
4. **Webserver**: [search.foldseek.com](https://search.foldseek.com) for immediate use
5. **Cross-platform**: Runs on x86_64, arm64, ppc64le via SIMDe library
6. **Comprehensive benchmarking**: SCOPe40, AlphaFoldDB, HOMSTRAD benchmarks are well-documented with exact command lines for all compared tools

#### Minor Blockers
1. **VQ-VAE training data**: Requires SCOPe40 structures + TM-align alignments, which are provided at [benchmark data URL](https://www.ser.gwdg.de/~compbiol/foldseek/scop40pdb.tar.gz)
2. **E-value NN training**: Requires 100,000 AlphaFoldDB structures for $\mu$/$\lambda$ fitting — dataset and procedure described but not a one-click reproduction
3. **Encoder weights baked into binary**: The pre-trained VQ-VAE encoder (`encoder_weights_3di.kerasify`) and E-value NN (`evalue_nn.kerasify`) weights are embedded as C headers, requiring Kerasify conversion to reproduce
4. **Exact benchmark versions**: Paper uses Foldseek commit `aeb5e`, specific tool versions documented

#### No Major Blockers
All claims in the paper can be verified against the code. The 3Di alphabet, substitution matrix, and scoring pipeline are fully implemented and match the paper descriptions.

---

### Real-World Application: SARS-CoV-2 RdRp

To demonstrate practical utility, the authors searched the SARS-CoV-2 RNA-dependent RNA polymerase (PDB: 6M71, chain A; 942 residues) against AlphaFoldDB v1. All top 10 hits were known RdRp homologs (Supplementary Table 4).

| Tool | Search Time | Speedup vs. Foldseek |
|------|------------|----------------------|
| Foldseek | **6 seconds** | 1× |
| TM-align | 33 hours | 23,000× slower |
| Dali | 10 days | 180,000× slower |

---

### High-Scoring False Positive Analysis

The authors searched all unfragmented AlphaFoldDB v1 models (average pLDDT $\geq 80$) against themselves. Among 133,813 high-scoring hits, 1,675 were FPs (score per aligned column $\geq 1.0$, TM-score $< 0.5$). Inspection revealed that these FPs had **multiple correctly folded segments but with incorrect relative domain orientations** — a known issue with AlphaFold2 predictions. Foldseek correctly aligned the individual folded segments. This highlights that local aligners like Foldseek and Dali can find homologous structures that 3D superposition–based tools like TM-align may miss because they require global superposability.

---

### Limitations

1. **3Di sensitivity ceiling**: Foldseek achieves 86–88% of Dali/TM-align's superfamily sensitivity — the encoding into 1D sequences loses some structural information
2. **Alignment quality**: On HOMSTRAD reference alignments, Foldseek performs slightly below CE, Dali, and TM-align in $F_1$ score
3. **SCOPe-only benchmark for single domains**: The SCOPe benchmark uses only single-domain proteins; the multi-domain benchmark is reference-free and relies on LDDT threshold choices (0.6 for TP, 0.25 for FP)
4. **E-value calibration**: The 0.32 power-law correction indicates the Gumbel model is an approximation; E-values should be interpreted with caution for borderline hits
5. **No profile search**: Unlike HHsearch/HHblits, Foldseek does not build structural profiles, limiting iterated search sensitivity

---

### Key Contributions

1. **3Di structural alphabet**: First structural alphabet based on tertiary interactions rather than backbone conformations, enabling sequence-like search speeds for structure comparison
2. **Integration with MMseqs2**: Leverages MMseqs2's highly optimized k-mer prefilter, enabling structure search at sequence-search speeds
3. **Combined 3Di + AA scoring**: Dual substitution matrix alignment (3Di weight 2.1, AA weight 1.4) captures both structural and sequence conservation
4. **Neural network E-values**: First neural network–based E-value prediction for structural alignments, with empirical power-law correction ($E_{\text{corr}} = E^{0.32}$)
5. **Practical impact**: Enables structure-based analysis at the scale of AlphaFoldDB (214M structures), previously impossible with existing tools
6. **Webserver**: Free search portal at [search.foldseek.com](https://search.foldseek.com) with pre-indexed databases (AlphaFoldDB, PDB, ESM Atlas, CATH) searchable in seconds; includes in-browser structure visualization via NGL viewer with WebAssembly-based PULCHRA backbone reconstruction and TM-align superposition

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
