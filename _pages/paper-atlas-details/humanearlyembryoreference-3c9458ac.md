---
layout: default
permalink: /paper-atlas/humanearlyembryoreference-3c9458ac/
title: "HumanEarlyEmbryoReference"
nav: false
description: "这项工作把多个稀缺的人类早期胚胎单细胞数据集整理成稳定参考，并通过“邻域聚合 + 重复 MNN + 固定参考投射 + 20D SVM + 多重拒识”把新数据映射到该参考，从而以全转录组证据审查胚胎模型的谱系身份和发育阶段，同时明确保留对参考缺失、稀有群体和混淆谱系的不确定性。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>HumanEarlyEmbryoReference</h1>
    <p>A comprehensive human embryo reference tool using single-cell RNA-sequencing data</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 人类早期胚胎单细胞转录组参考图谱与投射工具：方法详解

### 1. 这篇论文要解决什么问题？

人类胚胎样本稀缺，而且受到伦理、法律和技术条件限制。近年来出现了多种由干细胞构建的胚胎模型，例如 blastoids、着床后胚胎模型和滋养层样细胞。这些模型能否真正代表体内胚胎，关键在于它们产生的细胞是否具有正确的发育阶段和谱系身份。

传统验证往往只看少数标志基因，但早期胚胎谱系之间共享大量表达程序。例如：

- 滋养外胚层（TE）与羊膜细胞可能表达相似基因；
- 胚外中胚层与胚胎中胚层边界模糊；
- 某些“滋养层样”培养物可能同时包含羊膜样或胚外中胚层样细胞。

因此，单个或少量 marker 很容易造成误注释。更可靠的策略是把待测细胞的全转录组与覆盖多个发育阶段的体内胚胎参考进行比较。

论文的目标可以概括为：

> 建立一个从受精卵到原肠胚的人类胚胎单细胞参考图谱，并把任意新的 scRNA-seq 数据投射到一个固定的参考坐标系中，给出细胞类型、发育位置和不确定性判断。

### 2. 为什么已有方法还不够？

在这项工作之前，已经有多个胚胎 scRNA-seq 数据集，也有通用细胞类型注释工具，但缺少一个统一、稳定、经过发育生物学校验的人类早期胚胎参考。

论文比较了三类通用方法：

- **SingleR**：发表于 *Nature Immunology*（2019），通过参考表达谱相似性进行标签转移；
- **scmap**：发表于 *Nature Methods*（2018），把新细胞或细胞群投射到已有 scRNA-seq 数据集；
- **ScType**：发表于 *Nature Communications*（2022），根据特异 marker 组合进行自动细胞类型识别。

这些工具本身并不提供：

1. 从受精卵到原肠胚、经过统一整理的人类发育参考；
2. 对低测序深度数据进行邻域聚合的机制；
3. 固定参考几何、避免每次联合整合都改变参考坐标的设计；
4. 同时结合 MNN、相关性、SVM 概率和邻域质量的拒识机制；
5. 针对 TE、羊膜和胚外中胚层等高混淆谱系的专门处理。

因此，这篇论文的创新重点不是提出一种全新的分类器，而是把参考图谱构建、稳定投射、批次校正、分类和不确定性过滤组合成一个适合胚胎模型认证的完整框架。

### 3. 方法的核心思想

方法分为两个阶段：

```text
阶段 A：构建一次固定的人类胚胎参考
六个人类胚胎数据集
  → 统一预处理与归一化
  → fastMNN 批次整合
  → 固定的 PCA/UMAP 坐标
  → 谱系注释、轨迹与跨物种验证
  → 保存中心、SVD、批次向量、UMAP 模型、SVM 和伪时间

阶段 B：重复处理新的查询数据
新的 gene × cell 原始计数矩阵
  → 必要时进行 Milo 邻域聚合
  → 与参考对齐并归一化
  → 分窗、重复计算查询—参考 MNN
  → 过滤冲突或低相关 MNN
  → 投射到固定参考 PCA 并校正批次
  → 转换到固定 2D/20D UMAP 空间
  → SVM 预测 + 多重质量门控
  → 输出坐标、谱系、状态和伪时间
```

最重要的设计是“**参考不动，查询进入参考**”。如果把参考和每个新数据集重新联合降维，参考细胞的位置可能每次都变化，不同实验的结果就难以直接比较。本文保存参考构建时的数学状态，用同一套变换处理后续查询，从而获得稳定坐标。

### 4. 阶段 A：建立人类胚胎参考

#### 4.1 数据范围

参考由六个公开人类 scRNA-seq 数据集组成，共 3,304 个细胞，覆盖：

- 受精卵和卵裂期；
- 桑椹胚；
- 囊胚和着床前谱系；
- 三维培养的着床后早期胚胎；
- Carnegie stage 7、约胚胎第 16–19 天的原肠胚。

参考包含从早期未分化状态到 epiblast、hypoblast、TE，以及后续 CTB、STB、EVT、羊膜、原条、中胚层、定形内胚层和部分胚外谱系的连续结构。

#### 4.2 统一预处理

作者尽可能把原始数据重新比对到同一个 GRCh38 参考。10x 数据使用 Cell Ranger，其他数据使用 STAR 和 RSEM。Smart-seq2 细胞的主要质量门槛包括至少 2,000 个检测基因、线粒体比例低于 0.125；其他平台采用数据集相关阈值。

过滤线粒体基因后，只保留至少在五个细胞中表达的基因。随后：

1. 使用 scran 的 deconvolution 方法估计 size factor；
2. 计算 log-normalized expression；
3. 使用 batchelor 的 `multiBatchNorm` 重新缩放不同批次，使覆盖深度可比较。

#### 4.3 fastMNN 整合

作者选择 4,000 个整合特征。由于六个参考中有四个是着床前数据，为避免特征选择被着床前数据“多数表决”主导，先在这四个数据集中选 2,000 个特征，再与着床后和原肠胚数据综合。

不同批次按发育时间顺序线性合并，通过 fastMNN 寻找相互最近邻并估计批次校正向量。校正后的 50 维表示用于构建 UMAP 和邻接图。

参考构建后保存的不只是二维 UMAP 图，而是完整的投射状态：

- 参考基因顺序；
- grand center；
- SVD 左奇异向量；
- 批次校正方向和校正后坐标；
- 2D 与 20D UMAP 模型；
- 细胞注释；
- 每个谱系的 SVM；
- 发育伪时间。

#### 4.4 生物学验证

作者结合多个证据确认参考注释：

- 已知谱系 marker；
- SCENIC 转录因子调控活性；
- Slingshot 发育轨迹；
- 人、食蟹猴和狨猴的跨物种整合；
- 对部分历史注释的重新聚类和空间信息校正。

Slingshot 从 zygote 出发，得到通向 epiblast、hypoblast 和 TE 的三条主轨迹。跨物种分析先在每个物种内部去除批次，再用 Seurat anchors 整合三个物种，用于识别保守谱系并帮助解释胚外细胞边界。

### 5. 阶段 B：把新数据投射到参考

#### 5.1 输入格式

离线代码期望：

- 行是 gene symbol；
- 列是细胞；
- 数值为原始 read/count；
- 可选 metadata 可提供时间点、处理组等分组信息。

主要参数包括是否运行 Milo 聚合以及相关性阈值 `cor.cutoff`，默认值为 0.5。

#### 5.2 Milo 邻域聚合

10x 等 droplet 数据较稀疏，单个细胞可能无法稳定找到参考 MNN。方法先在表达相似的细胞之间建立 Milo neighborhood，再把邻域内的原始计数相加，相当于构建局部 pseudo-bulk。

代码中的具体规则包括：

- 查询超过 2,000 个细胞时强制聚合；
- 少于 200 个细胞时跳过聚合；
- 分组中至少要有 20 个以上细胞才构建邻域；
- `makeNhoods` 使用 `prop=0.15`、`k=21`、`d=30`。

聚合后的预测会回填给构成该邻域的细胞。无法形成邻域的细胞标为 `nb_failed`。

这一机制能减轻稀疏性，但有明确代价：极少见的亚群可能无法形成独立邻域，或者被并入最接近的常见谱系。

#### 5.3 基因对齐和归一化

查询与每个参考分别取共有基因。参考中存在而查询缺失的基因补零，再按照参考顺序重排。

如果查询样本数大于 50，size-factor 计算使用 \(k=30\)；否则使用 \(k=5\)。查询随后被重新缩放到覆盖深度最低的参考批次，并进行 cosine normalization。

这一步的目标不是让查询单独“看起来均匀”，而是让查询和参考在 MNN 与相关性计算所使用的表达尺度上可比较。

#### 5.4 重复分窗的 MNN 搜索

查询细胞数和近邻数 \(K\) 会影响 MNN。为降低一次下采样的偶然性，方法把大查询拆成 200 个细胞的窗口，并重复随机取样五次。每个窗口分别与六个参考数据集计算 MNN。

随后进行严格过滤：

- 同时匹配 TE 和羊膜参考的冲突 MNN 被删除；
- 相关性过低的 MNN 被删除；
- 某参考谱系的 top-20 相关性支持低于 0.5 时被拒绝。

相关性使用 cosine-normalized expression 上的 Spearman correlation。作者用胰腺、巨噬细胞、胎肾和肝脏数据测试“非胚胎细胞”的分布，以确定 0.5 的拒识阈值。

#### 5.5 固定坐标投射与批次校正

论文没有给出编号公式，但 Fig. 2 和代码对应的主要操作可以写成：

\[
Z_q^{(0)}=(C_q-c_r)^\top U_r,
\]

其中：

- \(C_q\) 是归一化后的查询表达；
- \(c_r\) 是参考构建时保存的 gene grand center；
- \(U_r\) 是参考 SVD 的左奇异向量；
- \(Z_q^{(0)}\) 是查询在参考子空间中的初始坐标。

接下来，代码删除沿参考批次向量的变化，再根据过滤后的 MNN 估计细胞特异的校正向量，对查询坐标进行修正。最后调用参考已经训练好的 `umap_transform`，获得：

- 2D 坐标：用于可视化；
- 20D 坐标：用于谱系分类。

由于所有变换都来自已有参考，查询不会改变参考 UMAP。

### 6. SVM 谱系预测与拒识

作者为每个谱系训练一个 radial-basis SVM。训练采用五折交叉验证，以 Kappa 选择超参数。代码搜索：

- sigma：0.1、0.5、1；
- cost：0.1、1、10。

作者比较了 2D、5D、10D、20D UMAP latent space 和原始 50D 校正 PCA，20D 的总体表现最好。

对查询坐标 \(z\)，SVM 首先给出概率最大的候选谱系：

\[
\hat{\ell}=\arg\max_{\ell}p_{\ell}(z).
\]

但候选结果还要经过四类门控：

1. 最大 SVM 概率必须不低于 0.5；
2. 该谱系必须有 MNN 支持；
3. 与参考的 top correlation 必须通过 0.5 阈值；
4. 如果使用 Milo，细胞必须成功进入邻域。

因此，最终结果可能是：

- 一个具体参考谱系；
- `Ambiguous`：分类概率低或缺少 MNN 支持；
- `low_cor` / nonrelated：与参考整体相关性不足；
- `nb_failed`：没有成功形成聚合邻域。

这说明该工具不是单纯的 SVM，而是“**SVM 候选 + MNN 证据 + 相关性拒识 + 邻域质量**”的混合决策系统。

### 7. 评估结果

作者使用五个未参与参考构建的胚胎数据集进行测试，覆盖 2-cell 到着床后阶段，同时包括 Smart-seq2、Trio-seq 和 10x 等不同平台。

主要结果为：

- 合并主谱系：Kappa = **0.961**，accuracy = **0.982**；
- 更细亚谱系：Kappa = **0.874**，accuracy = **0.912**；
- 在论文给出的 Kappa 和 accuracy 比较中优于 SingleR、scmap 和 ScType；
- 在线工具处理少于 7,000 个细胞时，报告运行时间低于 15 分钟。

参数实验还验证了 Milo 的 `prop`、MNN 的 \(K\)、200-cell 分窗、重复抽样、20D 分类空间和非相关组织过滤。

### 8. 对胚胎模型研究的意义

这个工具最有价值的地方不是“给每个细胞贴标签”，而是把不同研究中的模型放到同一个体内胚胎坐标系中比较。

论文得到的代表性结论包括：

- naïve 人多能干细胞更接近早期 epiblast；
- primed 多能干细胞更接近晚期 epiblast；
- 某些 trophoblast-like culture 确实包含 TE/滋养层样细胞；
- 但 primed-derived TLC 中也存在明显的羊膜样和胚外中胚层样群体；
- 多种 blastoid 能产生预期谱系样细胞，但与体内囊胚仍有系统性表达差异；
- 不同着床后胚胎模型只能覆盖参考中的不同子集。

因此，论文强调：模型细胞与参考相邻，只能说明转录组相似，不能直接证明形态、功能或发育潜能等价。

### 9. 方法的局限性

#### 9.1 参考中不存在的细胞

MNN 假设查询中存在可与参考对应的细胞。如果查询是参考未覆盖的新状态，它仍可能错误匹配到最相似的已知谱系。相关性过滤只能降低风险，不能完全解决。

#### 9.2 PGC 无法可靠识别

参考中的 primordial germ cell 数量太少，而且与 primitive streak 表达相似，论文明确指出当前工具不能可靠识别 PGC。

#### 9.3 难分谱系仍然存在

TE 与羊膜、胚外中胚层与胚胎中胚层之间有共享程序。代码对 TE/羊膜冲突进行特殊过滤，但这不等于问题已经完全解决。

#### 9.4 聚合会损失稀有群体

Milo 聚合增强信号，也可能把极少见细胞并入更大的相似邻域；失败细胞会成为 `nb_failed`。

#### 9.5 数据质量和覆盖范围

浅测序、细胞数过少、缺失关键谱系或参考本身不完整都会降低精度。空间转录组 spot 也可能混合多个细胞类型，不能当作真正单细胞解释。

### 10. 代码复现情况

论文在 Zenodo 记录 12189592 提供 GPL-3.0 代码。权威归档中可以直接对应到论文核心方法的部分包括：

- 六数据集 fastMNN 参考构建；
- Milo 邻域聚合；
- 基因对齐、size factor 和 cosine normalization；
- 200-cell、五次重复的 MNN 搜索；
- 固定 SVD/PCA/UMAP 投射；
- SVM 训练和多重门控预测；
- Slingshot 三条发育轨迹；
- 人—狨猴—食蟹猴跨物种整合。

但归档并不是完整的“一键复现论文”：

- 没有在线 Shiny/ShinyCell 应用的源代码和部署配置；
- 没有 Dockerfile 或依赖 lockfile；
- 没有测试套件；
- 参考构建脚本含作者本地绝对路径，并依赖未全部提供的 `tmp_data` 中间对象；
- 没有从全部原始数据到全部图表的统一工作流入口。

因此，对核心离线投射算法可以进行较可靠的阅读、运行和改造；对整篇论文的完全复现则需要重新整理外部数据、路径、依赖和分析工作流。

### 11. 一句话总结

这项工作把多个稀缺的人类早期胚胎单细胞数据集整理成稳定参考，并通过“邻域聚合 + 重复 MNN + 固定参考投射 + 20D SVM + 多重拒识”把新数据映射到该参考，从而以全转录组证据审查胚胎模型的谱系身份和发育阶段，同时明确保留对参考缺失、稀有群体和混淆谱系的不确定性。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## A Comprehensive Human Embryo Reference Tool Using scRNA-seq

**DOI:** 10.1038/s41592-024-02493-2
**Journal:** Nature Methods
**Year:** 2025

### Problem

Stem-cell-derived embryo models are increasingly used to study stages of human development that are difficult to access experimentally. Their value depends on whether the cells they produce genuinely resemble in vivo embryonic lineages and stages. Individual marker genes are often inadequate for this task because early lineages share transcriptional programs, especially around trophectoderm, amnion, and extraembryonic mesoderm.

Before this study, human embryo scRNA-seq datasets existed across zygote-to-gastrula development, but they were fragmented across studies, platforms, processing pipelines, and annotation systems. There was no stable, comprehensive reference onto which a new embryo or embryo-model dataset could be projected and audited.

### What the Paper Introduces

The authors integrate six published human embryo datasets into a 3,304-cell transcriptional reference spanning zygote to Carnegie stage 7 gastrula. They validate and refine lineage annotations with marker genes, regulatory programs, developmental trajectories, and human–cynomolgus–marmoset comparisons.

On top of this atlas, they build an early embryogenesis prediction tool that:

1. normalizes a new gene-expression matrix against the stored reference;
2. optionally aggregates sparse cells into Milo neighborhoods;
3. finds robust mutual nearest neighbors between query and reference;
4. projects and batch-corrects the query in the fixed reference PCA/UMAP geometry;
5. predicts lineages with pretrained SVM classifiers in a 20-dimensional latent space; and
6. rejects weak assignments through probability, MNN, correlation, and neighborhood-quality gates.

The important design choice is that the query is transformed into a fixed atlas rather than jointly reintegrated with it. Reference positions therefore remain stable across analyses.

### Why Existing Approaches Were Insufficient

Generic annotation tools can transfer labels, but they do not by themselves provide a curated, developmentally ordered human embryo reference with explicit handling of sparse queries, difficult lineage boundaries, out-of-reference cells, and fixed-atlas visualization.

The paper benchmarks against:

- **SingleR**, introduced in *Nature Immunology* (2019), which annotates cells by reference-based transcriptomic similarity;
- **scmap**, introduced in *Nature Methods* (2018), which projects cells or clusters across scRNA-seq datasets; and
- **ScType**, introduced in *Nature Communications* (2022), which scores cell types using marker combinations.

The proposed tool adds a domain-specific atlas and combines stable latent projection with repeated-window MNN evidence, lineage SVMs, and rejection logic. It also addresses shallow droplet data through conditional neighborhood aggregation.

### High-Level Method

#### Reference construction

The six datasets are processed against a common human genome reference when raw data are available, quality-controlled, normalized with scran, and rescaled across batches with `multiBatchNorm`. Four thousand integration features are selected, and fastMNN merges batches in developmental order. The resulting 50-component corrected space supports a fixed UMAP and stores the centers, singular vectors, correction state, and UMAP models needed to transform future queries.

Lineage validity is checked with marker expression, SCENIC regulatory activity, Slingshot trajectories, and cross-species integration. The reference resolves major early lineages and stage transitions but cannot robustly identify primordial germ cells because too few are represented.

#### Query projection

The input is a raw-count matrix with gene symbols by cells. For sparse or large datasets, Milo neighborhoods aggregate similar cells before mapping. The query is aligned to reference genes, missing genes are zero-filled, and expression is rescaled and cosine-normalized.

Large queries are divided into 200-cell subsets, sampled five times. MNNs are identified separately against each of six references. TE/amnion-conflicting pairs and weak correlations are removed. The query is centered using stored reference values, projected with stored singular vectors, orthogonalized against reference batch directions, and corrected using MNN-derived cell-specific vectors. Stored UMAP models produce 2D visualization coordinates and a 20D classifier representation.

One-vs-rest radial SVMs propose identities. A label is accepted only with sufficient probability (at least 0.5), MNN support, and correlation support. Cells with top-reference correlation below the 0.5 threshold are treated as unrelated/low-correlation; uncertain predictions become `Ambiguous`; cells lost during neighborhood construction become `nb_failed`.

### Evaluation and Main Results

The authors evaluate the tool on five additional embryo datasets covering prelineage, blastocyst, peri-implantation, and postimplantation stages and spanning Smart-seq2, Trio-seq, and 10x data.

- Main-lineage predictions: **Kappa 0.961**, **accuracy 0.982**.
- Granular sublineage predictions: **Kappa 0.874**, **accuracy 0.912**.
- Reported classification performance exceeds SingleR, scmap, and ScType on Kappa and accuracy.
- Tests on pancreas, macrophage, fetal kidney, and liver datasets support the 0.5 correlation rejection threshold.
- The online tool is reported to process fewer than 7,000 query cells in under 15 minutes.

Applied to stem cells and embryo models, the reference recovers expected relationships—naïve pluripotent cells map to early epiblast and primed cells to later epiblast—but also reveals likely misannotation and mixed identities. Primed-derived trophoblast-like cultures include notable amnion- and extraembryonic-mesoderm-like populations. Blastoids contain expected lineage-like states yet remain transcriptionally different from in vivo blastocyst counterparts. Postimplantation models reproduce different, incomplete subsets of reference lineages.

### Main Contribution

The work is both an atlas and an authentication framework. Its novelty is not a wholly new classifier; it is the combination of:

- a curated zygote-to-gastrula human reference;
- stable reuse of learned reference geometry;
- MNN-based query correction without moving the atlas;
- sparse-data neighborhood aggregation;
- lineage-specific SVM prediction with explicit rejection states; and
- comparative application across many human embryo models.

This makes model evaluation less dependent on a few shared markers and encourages reporting uncertainty when a query is not adequately represented.

### Limitations

- MNN matching can still falsely align an identity absent from the reference.
- PGCs cannot be resolved as a distinct class with the current cell coverage.
- TE versus amnion and embryonic versus extraembryonic mesoderm remain difficult boundaries.
- Milo aggregation may hide rare populations or leave cells as `nb_failed`.
- Accuracy depends on reference breadth, cell number, and sequencing depth.
- Spatial transcriptomic extensions are not single-cell measurements and may mix identities.
- Projection establishes transcriptional resemblance, not morphological or functional equivalence.

### Reproducibility Assessment

The paper explicitly deposits original code at Zenodo record 12189592 under GPL-3.0. The authoritative archive was downloaded, checksum-verified, extracted, indexed with a workspace-local CodeGraph, and directly mapped to the paper.

The code-paper match is strong for the central offline method: reference construction, Milo aggregation, normalization, repeated MNN matching, fixed-basis projection, SVM annotation, pseudotime, trajectories, and cross-species integration are all represented. Overall fidelity is assessed as **medium**, because the deposit does not provide the hosted Shiny/ShinyCell application source, a Dockerfile or lockfile, tests, or a one-command raw-data-to-all-figures workflow. Reference-construction scripts also require author-specific path changes and external intermediate data.

In practical terms, the archive is a useful and relatively transparent implementation of the projection engine, but complete paper reproduction requires additional workflow reconstruction and source datasets.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
