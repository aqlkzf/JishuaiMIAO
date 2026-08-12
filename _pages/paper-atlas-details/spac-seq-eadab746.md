---
layout: default
permalink: /paper-atlas/spac-seq-eadab746/
title: "SPAC-seq"
nav: false
description: "SPAC-seq 把 pooled CRISPR 扰动、全转录组和组织坐标同时测出来；TARDIS 再以非靶向 sgRNA（sgNTC）为参照，从“全组织位置改变”和“局部微环境富集”两个尺度给扰动排序，并连接空间生态位、基因程序和细胞互作。 论文为 Zhang 等发表于 Cell（2026），DOI 10.1016/j.cell.2026.04.049。"
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
      <span>Technology Platforms</span>
      <span>Cell · 2026</span>
    </div>
    <h1>SPAC-seq</h1>
    <p>Uncovering spatially resolved functional genomics with CRISPR screen sequencing</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SPAC-seq 与 TARDIS：从“哪个基因重要”到“扰动细胞在哪里、和谁互作”

### 一句话理解

**SPAC-seq** 把 pooled CRISPR 扰动、全转录组和组织坐标同时测出来；**TARDIS** 再以非靶向 sgRNA（sgNTC）为参照，从“全组织位置改变”和“局部微环境富集”两个尺度给扰动排序，并连接空间生态位、基因程序和细胞互作。

论文为 Zhang 等发表于 *Cell*（2026），DOI `10.1016/j.cell.2026.04.049`。

### 1. 为什么需要空间 CRISPR 筛选？

传统 pooled CRISPR screen 通常只能看到某条 sgRNA 在筛选前后变多还是变少，因此擅长回答“这个基因是否影响增殖/存活”，却看不到细胞位于肿瘤核心、边缘、免疫浸润区还是排斥区。

Perturb-seq（*Cell*, 2016）和 CROP-seq（*Nature Methods*, 2017）把单细胞转录组加到扰动读出中，但组织被解离后，原始空间位置仍然丢失。随后出现的成像型空间扰动技术能够保留位置，却常受限于成像通量、预选标记或分子读出范围。论文希望建立一种基于测序的框架，同时回答：

1. 哪个基因扰动改变了细胞行为？
2. 携带该扰动的细胞在组织中移动到了哪里？
3. 它偏好哪种转录组定义的微环境？
4. 周围有哪些细胞、配体–受体或趋化信号？

### 2. 整体框架

```text
pooled sgRNA 文库
      ↓ 转导、FACS、体内选择
组织切片（Stereo-seq / Visium HD）
      ↓ 同一坐标捕获
空间 RNA 矩阵 + 空间 sgRNA 矩阵 + 组织学图像
      ↓ 比对、质控、guide 归属、分箱
空间生态位 / 基因程序 / 细胞状态
      ↓
TARDIS 全局模式：整个组织中的位置是否改变？
TARDIS 局部模式：是否富集于某类微环境或克隆区域？
      ↓
通路、细胞组成、配体–受体、趋化分析
      ↓
FISH / mIF / PLA / 流式 / 共培养 / 小鼠实验验证
```

需要特别区分三层证据：

- **论文声明：** `paper.md` 描述了完整 SPAC-seq/TARDIS 方法和实验结果。
- **代码已验证行为：** acquired `SPAC-seq/` 中可直接读到部分预处理和下游分析。
- **缺失实现：** acquired 快照中没有 TARDIS 和跨切片 SSIM 的核心实现，不能仅凭论文公式声称代码已经复现。

### 3. SPAC-seq 如何让同一条 sgRNA 既做扰动又做读出？

#### 3.1 mRNA embedding

SPACseq 是逆转录病毒载体：U6 启动子驱动用于 Cas9 编辑的 sgRNA，同时把**同一条 guide 序列**嵌入 GFP mRNA。Stereo-seq 的 poly(dT) 探针捕获普通 mRNA 时，也能捕获含 guide 的 GFP 转录本。

关键设计是“编辑序列 = 检测序列”。这避免了另建 guide–barcode 对照表，也降低了 guide 与独立 barcode 重组错配的风险（`paper.md:31-34`）。

#### 3.2 direct capture

Visium HD 使用针对 protospacer/scaffold 的 splint-ligated 探针直接捕获 guide。这样不必把 guide 嵌进 mRNA，也更容易兼容不同 CRISPR 载体、CRISPRa/i、ORF 或其他带空间条码的扰动策略。

两条路线最终都要得到同坐标的：

- bin/cell × gene 表达矩阵；
- bin/cell × sgRNA 计数矩阵；
- H&E 或其他组织图像。

### 4. 从 FASTQ 到空间 guide 矩阵

论文中的 Stereo-seq 流程（`paper.md:283-291`）如下：

1. 普通转录组 FASTQ 用 SAW v6.0.0 比对。
2. SeekSeq 在 paired-end guide reads 中寻找锚点：
   - R1：`TTGTCTTCCTAAGAC`，锚点前 25 bp 是 CID，后 10 bp 是 UMI；
   - R2：`GTTTTAGAGCTAGAA`，邻近 21-bp guide；
   - 允许 Levenshtein distance ≤ 1，以容忍 PCR/测序错误。
3. CID 对 chip coordinate whitelist，允许 1 个碱基不匹配。
4. guide 用 STAR 对自定义 SPAC-seq 文库参考比对，保留 MAPQ > 10。
5. 相同 CID 与 guide 的 UMI 合并，也允许 1 个碱基误差。
6. guide GEM 与 RNA GEM 合并，保留组织范围内坐标，输出 AnnData。

#### acquired 代码能支持到哪一步？

- `SPAC-seq/fig_3_seekseq.py:32-76` 确实包含 Levenshtein 锚点搜索；`:141-156` 暴露 CLI 参数。
- `SPAC-seq/fig_3_saw_run.sh:46-137` 是 SAW 的环境特定 wrapper。
- 但 deposited SeekSeq 在 R1 FASTQ 索引、`current_count`、`output_files` 和终止条件上存在明确运行时错误，而且 CLI 默认 R2 scaffold 只有 `GTTTTAGA`。因此它**不能原样运行**。
- CID whitelist、MAPQ、UMI collapse 和 combined GEM 的具体实现，在 acquired 快照全部 16 个分析脚本中均 **Not found**。

所以，当前代码快照只能说明作者公开了部分思路/图分析脚本，不能证明 raw FASTQ 到最终矩阵已经可一键复现。

### 5. RNA 与 guide 预处理

论文规定（`paper.md:295-305`）：

- 去除 housekeeping、线粒体、核糖体、非编码 RNA，以及少于 10 个 bin 检出的基因；
- 通常保留组织内低 UMI bin，但肺转移单细胞 bin 注释要求至少 300 UMI；
- library-size 归一化到 10,000，加 pseudocount 1 后取 log；
- guide 少于 2 的 bin 被去除；同一基因的多条 guide 合并；冲突/歧义 guide 被去除；
- 六张 T-cell 切片中少于 100 个 bin 的扰动被剔除。

代码中可直接确认：

- `fig_3_perturbation_preprocessing.py:12-42` 分开 RNA 与 `sg*` 特征，合并 non-targeting 通道和 guide replicate，并做 10,000 归一化与 `log1p`；
- `fig_3_utils.py:62-75` 按 guide 名称前缀合并 replicate；
- `fig_3_utils.py:109-139` 通过“样本 + 空间坐标”对齐 RNA/guide，缺失 guide 行补零。

但所有论文所述过滤/归属规则并没有在一个完整可执行 pipeline 中出现，因此代码匹配是 **Partial**。

### 6. 先问一个基础问题：空间模式是不是随机的？

作者用 serial sections 检查相同扰动是否跨切片保持空间结构（`paper.md:309-336`）。

设：

- $S=\{s_i\}_{i=1}^{k}$：切片集合；
- $G=\{g_j\}_{j=1}^{l}$：扰动集合；
- $I_{g,s}\in\mathbb{R}^{H\times W}$：扰动 $g$ 在切片 $s$ 的 guide-count 图；
- $M_s$：组织 mask；
- $R$：把其他切片刚性配准到第一张切片的变换。

配准后：

$$
\tilde I_{g,s}=R(I_{g,s}),\qquad
X_{g,s}=N(\tilde I_{g,s}\odot M_s).
$$

对切片对 $(s,t)$，真实自相似度为：

$$
S_{\mathrm{self}}(g;s,t)=\operatorname{SSIM}(X_{g,s},X_{g,t}).
$$

随机背景不是均匀撒点，而是在该切片所有 guide 的空间密度上，保持扰动总 read 数 $N_{g,t}$ 进行多项式抽样：

$$
X^{\mathrm{background}}_{g,t}\sim
\operatorname{Multinomial}(N_{g,t};P_{x_1},\ldots,P_{x_{H\times W}}),
$$

$$
P_{x_i}=\frac{\sum_gx_{gi}}{\sum_i\sum_gx_{gi}}.
$$

比较量为：

$$
\Delta_g(s,t)=S_{\mathrm{self}}(g;s,t)-S_{\mathrm{background}}(g;s,t).
$$

检验：

$$
H_0:\operatorname{median}\Delta_g\le0,
\qquad
H_1:\operatorname{median}\Delta_g>0,
$$

用单侧 Wilcoxon signed-rank test，再做 BH-FDR 校正。

直觉是：**高 SSIM 本身不够**，因为组织形状和 guide 总密度也会造成高相似；必须证明真实跨切片相似度高于保留计数/密度的随机背景。Figure S1V–W 的图像正好显示了“原始 SSIM 很高”和“delta-SSIM 相对背景显著”之间的区别。

**重要缺口：** `paper.md:317` 的完整 SSIM 展开式存在疑似排版符号问题；acquired 代码中又没有 SSIM 实现可用于裁决。SSIM/配准/随机背景/检验实现均为 **MISSING / Not found**。

### 7. TARDIS 全局模式：整个组织里的位置是否变了？

全局模式不先定义生态位，而把空间 bin 当作类别，比较某扰动与 sgNTC 的全组织分布（`paper.md:401-442`）。

令 $P_{\mathrm{sgNTC}}$ 为 non-targeting 分布，$Q_g$ 为扰动 $g$ 的分布。默认效应量是定向 KL divergence：

$$
D(Q_g\parallel P_{\mathrm{sgNTC}})
=\sum_{i=1}^{N_{\mathrm{bin}}}q_i^g\log\frac{q_i^g}{p_i}.
$$

- $D$ 小：扰动细胞的位置接近 sgNTC；
- $D$ 大：扰动引起明显全局位置偏移。

#### 显著性怎么来？

随机打乱所有检测 bin 上的 guide 标签 $M$ 次，每次重新算 KL：

$$
p_g=
\frac{\#\{m:D^m_{\mathrm{null}}\ge D_{\mathrm{obs}}\}}{M}.
$$

随后做 BH 校正。多张切片先分别排名，再用 **Borda count** 汇总；置换得到的多切片排名也用相同方法汇总，从而形成每个扰动的 null Borda 分布。

#### 可选平滑和距离

空间噪声大时可用 Gaussian KDE。二维数据默认 Silverman bandwidth：

$$
h=\left[\frac{4}{N_{\mathrm{bin}}(d+2)}\right]^{1/(d+4)},\qquad d=2.
$$

也可用 Wasserstein distance 替代 KL：

$$
W(P_g,P_{\mathrm{ntc}})=
\inf_{\gamma\in\Gamma(g,\mathrm{ntc})}
\mathbb{E}_{(x,y)\sim\gamma}d(x,y).
$$

**解释边界：** 全局模式告诉我们“位置改变了多少”，但不直接告诉“偏向哪个微环境”。而且论文没有给出 KL 遇到零概率时的 pseudocount/平滑规则，这会影响数值稳定性。

**代码边界：** acquired `SPAC-seq/` 中 KL、置换、Borda、TARDIS KDE/Wasserstein 均 **Not found**；它们属于论文另行链接但本次未 acquire 的 TARDIS 包。

### 8. TARDIS 局部模式：扰动是否偏好某种微环境？

#### 8.1 Top-down：适合“响应环境”的效应细胞

用于 T 细胞等主要响应环境线索的细胞：

1. scVI 对多切片 RNA 做降维和批次校正；
2. 同一切片建空间图；
3. 聚合三跳邻域；
4. CellCharter + Gaussian mixture/Auto-K 定义 micro-niches；
5. 每个 guide 形成跨生态位比例向量；
6. 与 sgNTC 的 compositional distribution 比较。

论文给出的 scVI 参数为 `n_hidden=128`、`n_latent=20`、`n_layers=10`、Poisson likelihood、normal latent。它们可在 `fig_3_transcriptomic_preprocessing.py:183-210` 直接确认。

若有 $K$ 个生态位，guide $g$ 的组成是：

$$
X_g=[x_{C_1},\ldots,x_{C_K}],\qquad
x_{C_i}\ge0,\quad\sum_i x_{C_i}=1.
$$

用 Aitchison distance 与 sgNTC 比较：

$$
d(X_g,Y_{\mathrm{sgNTC}})=
\sqrt{\sum_{i=1}^{K}
\left(
\log\frac{x_{C_i}}{g(X_g)}-
\log\frac{y_{C_i}}{g(Y_{\mathrm{sgNTC}})}
\right)^2},
$$

其中 $g(\cdot)$ 是几何均值。生态位标签置换得到显著性，BH 校正控制 FDR；生态位内 log2 fold change 说明富集方向。

这里有一个关键未说明细节：CLR/Aitchison 遇到 0 组成时必须做 zero replacement 或 pseudocount，但论文和 acquired 代码均未给出精确规则。

#### 8.2 PERMANOVA 备选

论文还把生态位内 guide counts 分成 $N$ 个区间，构造更细粒度的分布矩阵，计算 pseudo-$F$：

$$
SSA=SST-SSW,
$$

$$
F(A_g,A_{\mathrm{sgNTC}})=\frac{(2N-2)SSA}{SSW}.
$$

再通过置换生成 null pseudo-$F$。实际 OT1 infiltration 分析使用 Bray–Curtis distance、1,000 permutations、10 个区间（`paper.md:541-547`）。acquired 快照没有这段实现。

#### 8.3 Bottom-up：适合“形成微环境”的细胞

用于肿瘤转移克隆等会主动塑造局部环境的扰动：

1. 对相同 guide 的空间点用 DBSCAN 找局部扩增；
2. 用 Gaussian KDE 平滑并画边界；
3. 提取区域转录组，用 scVI/GMM 聚成不同微环境；
4. 相对 sgNTC 检验扰动在各环境中的富集。

肺转移分析设置 $\varepsilon=40\,\mu\mathrm{m}$、至少 20 个细胞，KDE 的第二低等密度轮廓作为区域边界（`paper.md:393-400`）；最终富集分析采用 chi-square test（`paper.md:541-545`）。DBSCAN/KDE clone reconstruction 和 TARDIS bottom-up 实现均未出现在 acquired 快照。

### 9. 排名之后如何解释机制？

#### 9.1 空间生态位与基因程序

论文对高变基因做 NMF，多次拟合后合并相似 factor，再做 consensus clustering，得到稳定 gene programs。guide 按生态位富集模式分成 perturbation modules，模块与 gene program 的关系用相对 sgNTC 的平均 fold change 表示。

`fig_3_transcriptomic_preprocessing.py:246-308` 与 `fig_3_module_program_analysis.py:14-66` 直接实现了 NMF、factor correlation 和 consensus/agglomerative clustering；但论文所述“三次 NMF、Jaccard >0.6、program intercorrelation <0.3 过滤、top-100 genes”的完整链没有在单一可运行函数中出现，因此为 **Partial**。

#### 9.2 细胞组成与共定位

论文把某些分析称为“beta regression with ElasticNet”。直接代码显示 `fig_3_utils.py:141-197` 和 `fig_5_interaction_beta_regression.py:65-136` 使用的是 `sklearn.linear_model.ElasticNet` 最小二乘回归，五折交叉验证选择 alpha，`l1_ratio=0.5`。因此这些系数可以解释为正则化关联分数，但**不是带 beta 分布/link function 的 beta regression 参数**。

CIBERSORT 的论文设置是 `perm=1000`, `QN=FALSE`；`fig_2_cibersort.r` 只读取已算好的 CSV 并画图，CIBERSORT fitting 本身 **Not found**。

#### 9.3 配体–受体

`fig_5_ligand_receptor.r:1-64,88-121` 是匹配度最高的实现之一：加载 mouse NicheNet 网络，定义 T-cell receiver 与 macrophage sender，筛选表达基因，以 T-cell activity gene set 计算 corrected AUPR，取 top-30 ligand 并导出 ligand–receptor 权重。这为 SPP1–CD44 候选提供了计算入口，但真正机制还需要 Figure 5/S7/S8 的遗传、蛋白、抗体、PLA 和体内实验。

#### 9.4 Perturb-seq 状态映射回空间

`fig_6_mapping_sc_to_spatial.r:51-61` 用 CellTrek 将 Perturb-seq 状态映射到 Stereo-seq，参数 `intp_pnt=500`, `nPCs=10`, `ntree=200`, `top_spot=4`, `spot_n=10` 与论文一致。不过脚本依赖未在文件中创建的矩阵和 marker 对象，仍不是独立示例。

### 10. 论文的四个主要发现如何由方法得到？

#### 10.1 `Icam1` 与转移免疫逃逸

Bottom-up TARDIS 先从肺转移切片重建 guide-defined clones，再把 clone 分到免疫浸润/排斥环境。`Icam1` 扰动在免疫排斥区显著富集，并呈巨噬细胞多、CD8 T 细胞少的结构。H&E、mIF、基因程序、细胞组成和独立小鼠验证共同支持 ICAM1 loss 破坏免疫突触/TCR co-stimulation 并促进转移。

#### 10.2 `Cd44` 与 T 细胞空间定位

大规模 bulk screen 先把 2,135 个基因压缩到 33 个候选，再做 day 4/7/10 时序 SPAC-seq。全局 KL 和局部 PERMANOVA 都把 `Cd44` 排在强空间效应一端，而传统 bulk hit `Zc3h12a` 的空间变化较小。这说明“提高 T-cell abundance”与“改变 T-cell location”不是同一个问题。

后续实验显示 CD44 KO 降低线粒体 ROS/耗竭，增加 memory-like 状态并改善肿瘤控制。

#### 10.3 SPP1–CD44 轴

空间 ligand–receptor/NicheNet 把 SPP1 提为 CD44 候选配体；空间邻域、mouse mIF、human CosMx 与 PLA 支持 SPP1+ macrophage 和 CD44+ T cell 的邻近/相互作用。`Spp1` perturbation、SPP1 overexpression/protein、anti-SPP1、macrophage-specific `Spp1` KO 以及 CD44 KO 的互作实验显示：SPP1 对 T 细胞的 ROS、铁、代谢和功能抑制依赖 CD44。

#### 10.4 BHLHE40–CXCR4–CXCL12

作者先在超过 32 万人/鼠 TIL CD8 T cells 中找单细胞互斥表达对，再在 44 个空间数据集测试空间互斥，最后对 70 条 guide/32 个靶点做 Perturb-seq + SPAC-seq。`Bhlhe40` perturbation 增加 `Cxcr4`，改变 T-cell state，并让细胞更靠近 CXCL12-rich fibrotic margin。FISH/mIF 支持位置改变；同时肿瘤控制变差，即使 exhaustion 降低。这是空间筛选相对 bulk screen 的典型增量信息。

### 11. 评估结果与图像证据

- mini-pool genomic vs mRNA guide count：$\rho=0.9970$；
- 9,040-guide library：$\rho=0.9414$；
- direct capture 恢复 1,393/1,520 guides；mRNA embedding 恢复 1,161/1,520；两路线共享 1,068；
- 五张 serial sections 的 perturbation pairwise Spearman 全部 >0.92；
- Figure S17 显示中等 downsampling 下排名和 niche 较稳定，但极端 guide loss 时 clone recovery 与空间结构明显退化。

对本地 25 张 JPEG 的直接读取显示，最强证据不是某个单一 rank plot，而是多模态收敛：guide map、RNA niche、统计排序、mIF/FISH/PLA、流式、共培养和小鼠肿瘤曲线相互支持。人类 TCGA/CosMx/ICB 分析则应理解为关联性外部支持，而非临床干预验证。

### 12. 假设与局限

1. guide assignment 必须可靠；dropout、冲突 guide 和 lateral diffusion 会改变空间分布。
2. sgNTC 必须是合理空间参照；其偏差会传入所有 effect size。
3. label permutation 假设可交换性，但空间自相关会破坏这一假设；论文明确承认该限制。
4. KL 的零概率、Aitchison 的零组成必须处理，但精确规则 **Not found**。
5. 局部排名依赖 bin size、空间图、scVI、cluster number 与 niche annotation。
6. serial-section SSIM 依赖组织配准并假设相邻切片共享三维结构。
7. 空间共定位不等于因果机制；需要独立干预验证。
8. sgRNA 与转录组测序深度仍有限；这是论文明确列出的实验限制。
9. 研究主体是小鼠肿瘤模型，人类证据主要是回顾性数据。

### 13. 代码与论文一致性结论

acquired repo commit：`b671d4288843d94cfe1b8923892f16b1acffbf47`。

- **整体 fidelity：low。** 它是 figure-analysis scripts 集合，不是完整 SPAC-seq/TARDIS 包。
- **较强匹配：** NicheNet ligand–receptor、CellTrek mapping。
- **部分匹配：** guide/RNA 预处理、scVI/CellCharter、NMF、ElasticNet colocalization、neighborhood enrichment、BHLHE40–CXCL12 KDE。
- **MISSING / Not found：** TARDIS global/local（KL、置换、Borda、Aitchison、PERMANOVA）、serial-section SSIM、真正的 CIBERSORT fitting。
- **运行阻断：** deposited SeekSeq 有明确运行时/索引错误。
- **复现条件缺失：** 无 environment lockfile、测试、示例输入或 top-level driver；多个脚本依赖缺失模块、硬编码路径和未定义内存对象。

因此，当前快照适合**审计部分下游计算与参数**，不适合独立完成 raw FASTQ → TARDIS rank → 主图结果的端到端复现。真正复现还需固定单独 TARDIS repo、获取 GSA `CRA023189`/数据门户文件、重建环境并修复验证 SeekSeq。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SPAC-seq and TARDIS — Summary

### What problem does the paper solve?

Pooled CRISPR screens reveal which genes affect fitness, and Perturb-seq (*Cell*, 2016) or CROP-seq (*Nature Methods*, 2017) adds single-cell transcriptomes, but these approaches lose tissue position. Imaging-based spatial perturbation screens can retain position but have constrained molecular readouts or throughput. This 2026 *Cell* paper introduces a sequencing-based alternative that asks not only **which perturbation matters**, but also **where perturbed cells localize, which tissue niche they occupy, and which intercellular pathway accompanies that phenotype**.

### Proposed system

- **SPAC-seq (spatial CRISPR screen sequencing)** captures a pooled sgRNA library and whole-transcriptome RNA on the same spatial transcriptomics section. A retroviral plasmid embeds the guide in GFP mRNA for poly(dT)-based Stereo-seq, while a direct-capture probe supports Visium HD and reduces dependence on plasmid embedding.
- **TARDIS (target prioritization toolkit for perturbation data in spatial omics)** analyzes the resulting spatial guide distributions. Global mode ranks tissue-wide positional shifts relative to non-targeting guides with KL divergence and permutation tests. Local mode ranks enrichment in transcriptomic niches or reconstructed clonal regions using compositional/distance statistics, with multi-slide rank aggregation.

The computational flow is:

> aligned RNA + guide coordinates → guide/RNA QC and binning → spatial niches and gene programs → global/local perturbation ranks → cell-type, pathway, ligand–receptor, and chemotaxis analyses → independent experimental validation

### Evaluation and main evidence

#### Technical performance

The paper benchmarks plasmid transduction/editing, guide expression, genomic-versus-RNA guide counts, library recovery, and serial-section reproducibility. Reported genomic-versus-mRNA guide correlations include $\rho=0.9970$ for a mini-pool and $\rho=0.9414$ for 9,040 guides. In spatial tumor sections, direct capture recovered 1,393/1,520 guides and mRNA embedding recovered 1,161/1,520; 1,068 guides were shared. Across five serial sections, all pairwise perturbation correlations exceeded 0.92. The authors further compare observed cross-section SSIM with a count-preserving random background rather than treating high raw similarity as sufficient evidence.

Direct reads of Figure 1 and Figure S1 support these claims visually: guide maps recur across serial sections, genomic/RNA scatterplots track the diagonal, and delta-SSIM separates observed patterns from the randomized background.

#### Biological applications

1. **Tumor metastasis:** spatial guide-defined clones were paired with immune-infiltrated or immune-excluded niches. `Icam1` loss was associated with larger, macrophage-rich and CD8-T-cell-poor lung metastases. Histology, mIF, expression programs, and targeted in vivo validation converge on impaired immune surveillance.
2. **Temporal T-cell infiltration:** a bulk screen compressed the library to 33 targets for a day-4/7/10 spatial screen. TARDIS ranked `Cd44` as a strong regulator of localization. CD44 loss reduced mitochondrial ROS/exhaustion, increased memory-like and effector properties, and improved tumor control in the tested models.
3. **SPP1–CD44 mechanism:** spatial ligand–receptor analysis nominated macrophage-derived SPP1. Genetic perturbation, overexpression/protein treatment, antibody blockade, macrophage-specific `Spp1` knockout, mIF, and PLA support a CD44-dependent suppressive axis affecting ROS, iron handling, metabolism, and T-cell function.
4. **State–chemotaxis coupling:** a pan-cancer exclusivity screen plus Perturb-seq/SPAC-seq identified `Bhlhe40` as a regulator of `Cxcr4`-associated localization near CXCL12-rich tumor margins. This illustrates why a perturbation can reduce exhaustion yet worsen tumor control if it moves T cells away from tumor parenchyma.

The figures are strongest where several modalities agree; human TCGA/CosMx/ICB analyses are supportive associations rather than interventional clinical validation.

### Methodological strengths

- Couples perturbation identity, transcriptome, and histology in one coordinate system and supports two sequencing platforms.
- Uses non-targeting controls, permutations, multiple-section aggregation, and explicit global-versus-local hypotheses.
- Separates perturbations that change cell-intrinsic fitness from those that change tissue localization.
- Connects ranks to interpretable niches, programs, cell types, and ligand–receptor relationships, then validates major mechanisms experimentally.
- Supplementary sensitivity/downsampling figures show substantial rank stability while also revealing degradation under extreme guide loss.

### Limitations

- Guide and transcriptome depth remains limiting; dropout and multi-cell bins can obscure assignment and cell state.
- Label-shuffling tests may violate exchangeability under spatial autocorrelation, a limitation acknowledged for TARDIS.
- KL divergence and Aitchison distance require handling of zero-probability/count components, but the paper does not specify the exact pseudocount or zero-replacement rule.
- Niche-dependent results can change with bin size, graph construction, latent model, and cluster number. The text and deposited helper also disagree on Delaunay use and some Auto-K defaults.
- Spatial association does not by itself prove mechanism; the paper mitigates this for its major claims with targeted experiments.
- The study is centered on mouse tumor models; human analyses are retrospective associations.

### Reproducibility assessment: **2/5 (limited)**

The paper provides detailed STAR Methods, GSA accession `CRA023189`, a data portal, an SPAC-seq repository, and a separate TARDIS link/tutorial. However, the acquired commit `b671d4288843d94cfe1b8923892f16b1acffbf47` is a fragmented set of figure-analysis scripts with no environment lockfile, tests, example inputs, or top-level workflow.

Direct source review found:

- **MISSING / Not found:** the TARDIS KL/permutation/Borda and Aitchison/PERMANOVA implementations, and the serial-section SSIM framework, across all 16 acquired analysis scripts plus the repository README. They appear to belong to a separately linked TARDIS repository that was not acquired here.
- **Broken as deposited:** `SPAC-seq/fig_3_seekseq.py` has incorrect FASTQ indexing and undefined runtime names, so it cannot execute its core matching path without repair.
- **Method mismatch:** the reported “beta regression” is verified as ElasticNet least-squares regression, not beta-distribution regression.
- **Partial positives:** scVI/CellCharter setup, NMF/consensus logic, NicheNet ranking, CellTrek transfer, guide–RNA alignment, neighborhood enrichment, and the BHLHE40–CXCL12 KDE analysis have readable source anchors.

Thus the repository is useful for auditing selected downstream computations, but it is insufficient for an independent raw-data-to-main-result reproduction of SPAC-seq/TARDIS. Reproduction would require acquiring and pinning the separate TARDIS package, obtaining GSA/portal inputs and missing reference files, reconstructing an environment, and repairing/validating SeekSeq before rerunning analyses.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
