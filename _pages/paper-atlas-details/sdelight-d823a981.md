---
layout: default
permalink: /paper-atlas/sdelight-d823a981/
title: "SDELight"
nav: false
description: "SDELight 面向多张空间转录组切片，串联三个阶段： Deconvolution：结合 H&E、scRNA-seq 参考和 spot-level ST，估计每个 spot 的细胞类型组成； Integration：把细胞组成加入表达特征，用 GCN 与域对抗训练减弱切片批次效应，并得到跨切片可聚类的生物 embedding；"
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
      <span>Manuscript · 2025</span>
    </div>
    <h1>SDELight</h1>
    <p>SDELight: Adversarial Learning and Gromov-Wasserstein Distance for Multi-Modal Integration of Spatial Transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SDELight 中文方法解读：先解卷积，再对抗整合，最后用 Gromov–Wasserstein 对齐切片

### 1. 方法解决的不是一个问题，而是三个连续问题

SDELight 面向多张空间转录组切片，串联三个阶段：

1. **Deconvolution**：结合 H&E、scRNA-seq 参考和 spot-level ST，估计每个 spot 的细胞类型组成；
2. **Integration**：把细胞组成加入表达特征，用 GCN 与域对抗训练减弱切片批次效应，并得到跨切片可聚类的生物 embedding；
3. **Alignment**：在共享空间域内部，以生物 embedding 距离和空间几何距离共同定义 Gromov–Wasserstein 代价，把相邻切片映射到参考坐标系。

因此它不是单纯“批次校正”或“图像配准”。前一阶段的输出是后一阶段的先验：细胞组成帮助空间域识别，空间域再限制哪些点应该参与最优传输。

目录名和旧合同写作 `SEDLight`，论文标题及图中实际名称是 `SDELight`。下文采用论文拼写。

### 2. 阶段一：用图像和 scRNA-seq 补足 spot 的细胞组成

#### 2.1 输入预处理

论文先对 scRNA-seq 与 ST 做低质量细胞/基因过滤、总量归一化与 log transform。总量归一化写成：

$$
X'_{ij}=\frac{X_{ij}}{\sum_jX_{ij}}T.
$$

H&E 侧使用 Squidpy 平滑图像、watershed 分割，再通过 `sq.im.calculate_image_features` 计算分割区域特征。论文没有给出 watershed 参数、筛选阈值或最终图像特征维数，因此这些步骤只能理解为方法意图，不能据此精确复现。

#### 2.2 点编码器

对一个 scRNA-seq cell 或 ST spot，初始表示由表达向量和位置嵌入相加：

$$
x_i^{(0)}=d_i+\operatorname{MLP}_{\mathrm{enc}}(p_i).
$$

$d_i$ 是转录组特征，$p_i$ 是空间位置。这里隐含要求两项维度一致，但论文没有说明表达如何投影到相同维数。

#### 2.3 自模态和跨模态注意力

作者把 scRNA-seq 与 ST 节点放入同一图：同一模态节点用 self edges，不同模态用 cross edges。每层残差更新为：

$$
x_{Ai}^{(l+1)}=x_{Ai}^{(l)}+\operatorname{MLP}\left[x_{Ai}^{(l)}\mid m_{\varepsilon\to i}\right],
$$

$$
m_{\varepsilon\to i}=\sum_{j:(i,j)\in\varepsilon}a_{ij}v_j.
$$

文本说 attention 类似 query-key-value，但式 (4) 把权重写成 $\operatorname{Softmax}(q_i^Tv_j)$，而不是常见的 $q_i^Tk_j$；紧接着式 (5) 又同时定义 $k_j$ 与 $v_j$。这是论文内部符号冲突，在无代码情况下不能替作者决定真正实现用 key 还是 value。

#### 2.4 从匹配矩阵到细胞比例

两模态节点的 matching descriptors 做内积：

$$
M_{ij}=\langle f_i^A,f_j^B\rangle.
$$

论文称优化目标同时约束 gene-wise 和 spot-wise cosine similarity，使 $M^TA$ 重构 ST 表达 $B$。但式 (7) 写成“minimize cosine similarity”且括号/下标损坏；通常若目标是匹配，应最大化 cosine similarity或最小化 $1-\cos$。论文也没有明确如何把 $M$ 规范化为非负且和为 1 的细胞类型比例。因此可确认的是“用注意力匹配 scRNA/ST 并生成权重矩阵”，精确损失符号和比例约束仍缺证据。

### 3. 阶段二：细胞组成增强的 GCN 与域对抗

每个 spot 的表达与细胞类型组成融合后，按空间邻接构图。10x Visium 设置 KNN=6，因为规则六角网格上每个内部 spot 有六个近邻。GCN 传播为：

$$
H_{l+1}=\operatorname{ReLU}\left(\hat D^{-1/2}\hat A\hat D^{-1/2}H_lW_l\right).
$$

模型共五层 $H_0\dots H_4$，中间层 $H_2$ 用于聚类/空间域识别，首尾层都保留细胞组成相关信息。

作者组合三项：

- $L_C$：约束 $H_0$ 与 $H_4$ 的重构一致性；
- $L_S$：让 $H_2(q_i)$ 接近邻居平均，保持局部空间连续；
- $L_D$：判别切片 batch ID。

总式写为：

$$
L=\alpha_CL_C+\alpha_SL_S-\alpha_DL_D.
$$

Gradient Reversal Layer 在前向保持输入不变，反向乘 $-1$，使 encoder 学到难以区分切片来源的表示。不过正文同时说 $L_D$ 被“minimized when embeddings are maximally different”，又说要让 batch ID indistinguishable；交叉熵式 (10) 还缺常见负号。可确信的是域对抗意图，不能从稿件确定实际优化器应采用哪套符号。

后文又把潜变量拆成 `bio` 与 `noise`，用 GRL 判别器从 bio 中移除 batch、用普通 classifier 让 noise 保留 batch，以便重构原表达。这一结构在方法图中没有完整画出，且式 (12)–(14) 周围 OCR/源稿有大段损坏，训练交替频率、各维数和超参数均未提供。

### 4. 阶段三：在共享空间域内做 fused Gromov–Wasserstein 对齐

先通过平移、缩放、旋转做粗配准，再对相邻切片共享 cluster $c$ 内的 spots 求 transport plan $\Pi$。目标由两部分组成：

$$
F_c(\Pi)=(1-\alpha)A+\alpha B,
$$

$$
A=\sum_{i,j}e(z_{iR}^{bio},z_{jd}^{bio})\pi_{ij},
$$

$$
B=\sum_{i,k,j,l}(d_{ik}-d_{jl})^2\pi_{ij}\pi_{kl}.
$$

$A$ 是跨切片 spot embedding 的直接特征匹配代价，$B$ 是 Gromov–Wasserstein 结构代价：不要求两个切片共享绝对坐标，而要求切片内部点对距离关系相似。$\alpha$ 决定更信任生物特征还是几何结构。

作者称使用 entropy-regularized Kantorovich、Sinkhorn 和 conditional gradient 优化 $\Pi$。但式 (15)–(16) 没写边缘分布、熵正则系数和求解停止条件；严格说这是 fused GW 风格目标，而不是只含 $B$ 的纯 GWD。

新坐标通过 $\Pi$ 关联的参考点坐标平均得到，再对非共享 cluster 使用共享 cluster 作为 landmarks 做旋转和平移。这种做法能表达非刚性局部变化，但论文没有给出 partial overlap、无共享 cluster 或一对多匹配的失败处理。

### 5. 三个阶段如何连起来

$$
\{\text{H\&E},\text{scRNA},\text{ST}\}
\xrightarrow{\text{cross/self attention}}
\text{spot cell-type composition}
$$

$$
\xrightarrow{\text{feature fusion + 5-layer GCN + domain adversarial}}
H_2\text{ biological embeddings + spatial domains}
$$

$$
\xrightarrow{\text{cluster-constrained fused GW}}
\Pi\xrightarrow{\text{coordinate transfer}}
\text{aligned adjacent slices}.
$$

单细胞分辨率的 MHypo MERFISH 数据已有 cell labels，论文直接跳过 deconvolution，只运行 integration 与 alignment。这说明 SDELight 是模块化流程，不要求所有数据都走完三段。

### 6. 图和结果支持了什么

#### DLPFC

12 张 DLPFC 切片来自三个成人，每个供体四张相邻切片。论文用人工皮层层级作为间接参照评价解卷积，因为没有真实 spot-level 细胞比例。Figure 2 显示 Oligodendrocytes 与 excitatory cell types 大体落在预期皮层区域，并给出一个 accuracy-score 排名。这个评价验证空间一致性，不等价于真实比例误差已测量。

Figure 3 对三个代表切片展示 spatial-domain 图以及 NMI/HOM/COM/ARI，并另以热图汇总 12 张切片。SDELight 在示例中通常较强，但正文“all selected slices highest”与图中某些并列或其他指标并不完全一致；没有误差条或跨切片显著性检验。

Figure 4 对九对 DLPFC 相邻切片比较 layer-wise alignment accuracy，并以蓝/红连线展示正确/错误层级匹配。可见 SDELight 的 shift=0 柱通常最高。连线图只下采样 300 条，属于代表性可视化，不是完整统计。

#### HBCA1 与 MHypo

HBCA1 只用于展示把 cluster 数从 4、10、15 调到 20 时仍能得到连续区域，并解释为肿瘤核心/外环。这是形态合理性案例，没有像 DLPFC 一样的独立真值量化。

MHypo 包含五张 MERFISH 切片、每张约 5,500 cells 和 155 genes。Figure 5 比较四对相邻切片，SDELight 的 layer-wise accuracy 最高；但图注最后误写为 DLPFC dataset，是稿件文本错误。单细胞数据跳过解卷积，因此该结果只验证后两阶段。

### 7. 论文证据和实现证据的边界

| 机制 | 论文证据 | 本地代码证据 |
|---|---|---|
| 图像分割与 Squidpy features | Methods 4.1 描述 | Not found |
| cross/self attention 解卷积 | 式 (2)–(7) | Not found |
| 五层 GCN、空间平滑损失 | 式 (8)–(9) | Not found |
| GRL 域对抗与 bio/noise 分解 | 式 (10)–(14) | Not found |
| fused GW alignment | 式 (15)–(17) | Not found |
| DLPFC/HBCA1/MHypo 结果 | Figures 1–5 | 只有论文图，无结果矩阵/脚本 |

工作区 CodeGraph 已存在，但查询没有找到任何实现；目录内也没有源码快照、`doc_code.md` 或代码仓库元数据。因此本工作区必须保持 `paper-only`，不能把 `doc_method.md` 中的伪代码当成作者实现。

### 8. 复现与可信度边界

- PDF 文件名为 `GENOME-2025-281490v1-Fu.pdf`，创建时间为 2025-09-27；正文没有 DOI、正式期刊卷期、预印本编号或 code availability。元数据应记作 2025 manuscript，而不是已发表论文。
- 没有补充材料文件。正文提到的额外切片结果、参数与消融也未在工作区出现。
- 没有代码、环境文件、随机种子、学习率、epoch、网络维数、损失权重、GW 熵正则或聚类参数。
- 解卷积没有 spot-level composition 真值；DLPFC 以 cortical-layer consistency 作间接评价。
- 多个损失公式存在符号或排版矛盾，不能据此写出唯一正确的可执行目标。
- benchmark 图缺少重复试验误差、显著性检验与运行成本；“outperforms”应理解为稿件所示数据上的报告结论。
- 需要高质量 H&E 和匹配的 scRNA reference；作者也承认这是适用条件限制。
- 对单细胞数据可跳过解卷积，说明所谓“multimodal”增益并未在所有 benchmark 上同时被验证。

### 9. 最稳妥的理解

SDELight 的概念贡献是把三个成熟思路串成有生物先验的多切片流程：跨模态图注意力估计细胞组成，域对抗 GCN 学习批次不敏感的空间域，fused Gromov–Wasserstein 用生物与几何结构共同对齐切片。现有稿件和图支持其设计动机与若干 benchmark 表现，但由于源码和关键训练细节缺失，它仍是“论文描述的候选方法”，而不是当前工作区可复现验证的软件实现。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SDELight: Multi-Modal Integration of Spatial Transcriptomics - Review Summary

### 1. Motivation and Novelty

#### Biological Problem Addressed
SDELight tackles fundamental challenges in spatial transcriptomics analysis:
- **Multi-resolution integration**: Spatial transcriptomics technologies like 10x Visium (55µm resolution) cannot achieve single-cell resolution, requiring deconvolution to estimate cell type composition within each spot
- **Batch effect correction**: Multiple tissue slices exhibit significant technical variations that confound biological signals (p.2: "ST slices may exhibit significant batch effects")
- **Spatial alignment limitations**: Existing methods rely on rigid transformations (ICP) that fail to account for local tissue distortions and biological variations

#### Limitations of Prior Approaches
The authors identify specific shortcomings in existing methods:
- **STAligner**: "May overlook non-MNN pairs in the same spatial domains and contain MNN pairs belonging to different spatial domains" (p.3) - relying solely on mutual nearest neighbors leads to incorrect pairings
- **DeepST**: "Gene expression is not effective in removing batch effect" (p.3) when used alone without spatial context
- **SPIRAL**: "Lacked the cell-type information to identify uniform domain across multiple slices" (p.3) - missing crucial biological context

#### Unique Contributions
SDELight introduces three key innovations:
1. **Multimodal deconvolution**: Jointly uses H&E images and scRNA-seq data (p.3: "we add image information as confirmation"), improving upon methods that use only transcriptomics
2. **Adversarial learning framework**: Employs generator-discriminator architecture with gradient reversal layer to minimize batch effects while preserving biological signals
3. **Flexible alignment via Gromov-Wasserstein Distance**: Enables non-rigid transformations that better capture tissue distortions compared to ICP-based approaches

#### Significance to the Field
- Addresses critical gap in integrating multi-slice spatial transcriptomics with varying resolutions
- Enables robust analysis of complex tissues like tumors with high heterogeneity
- Facilitates comparative studies across multiple samples/conditions by effective batch correction

### 2. Methodological Framework

#### Study Design
**Datasets Used:**
- **DLPFC dataset**: 12 slices from 3 donors, 4 adjacent slices per donor, with manually annotated cortical layers (ground truth)
- **HBCA1 dataset**: Invasive Ductal Carcinoma breast tissue from 10x Visium, known for high heterogeneity
- **MHypo dataset**: MERFISH data with 5 consecutive slices at single-cell resolution (155 genes per slice)

#### Computational Pipeline
The three-stage architecture processes data sequentially:

**Stage 1 - Deconvolution:**
- Image segmentation using watershed algorithm on H&E stained images
- Graph attention network integrating scRNA-seq and spatial data
- Message-passing equations enable information diffusion: "$x_{Ai}^{(l+1)} = x_{Ai}^{(l)} + \text{MLP}[\mathbf{x}_{Ai}^{(l)} | \mathbf{m}_{\varepsilon}]$" (Equation 3)
- Attention mechanism for weighted aggregation: "$m_{\varepsilon \to i} = \sum_{j:(i,j) \in \varepsilon} a_{ij} v_j$" (Equation 4)

**Stage 2 - Integration:**
- Graph construction with k-nearest neighbors (k=6 for 10x Visium hexagonal layout)
- 5-layer GCN with ReLU activation: "$f(H_l, A) = \operatorname{ReLU}(\widehat{D^{-\frac{1}{2}}\hat{A}D^{-\frac{1}{2}}}H_lW_l)$" (Equation 8)
- Discriminator with 4 fully-connected layers for batch identification
- Combined loss function: "$\text{Loss} = \alpha_C \text{Loss}_C + \alpha_S \text{Loss}_S - \alpha_D \text{Loss}_D$" (Equation 11)

**Stage 3 - Alignment:**
- Gromov-Wasserstein distance formulation balancing expression and spatial structure:
  "$F_c(\Pi; Z^R, D^R, Z^d, D^d, e, \alpha, c) = (1 - \alpha)A + \alpha B$" (Equation 15)
- Sinkhorn algorithm for entropy-regularized transport problem
- Coordinate transformation including rotation, translation, and scaling

#### Biological Assumptions
- Cell types cluster in specific cortical layers (validated in DLPFC)
- Spatial proximity correlates with biological similarity
- Batch effects are technical rather than biological in origin
- Tissue architecture is preserved across adjacent slices with local deformations

### 3. Results and Evaluation

#### Deconvolution Performance
**Benchmark comparison on DLPFC:**
- Outperformed 7 state-of-the-art methods: Tangram, RCTD, Cell2location, SpatialDWLS, Stereoscope, DestVI, Seurat
- Achieved "highest deconvolution accuracy score among all methods" (Fig. 2c)
- Successfully identified layer-specific cell types (e.g., Oligodendrocytes concentrated in white matter)

#### Spatial Domain Identification
**DLPFC dataset results:**
- Achieved highest NMI values across all test slices
- Superior homogeneity (HOM) indicating better within-cluster similarity
- Highest completeness (COM) in 2/3 slices, showing comprehensive cluster identification
- Stable ARI values with exceptional performance on slice 151670

**HBCA1 tumor tissue analysis:**
- Successfully partitioned complex tumor tissue into 4-20 hierarchical regions
- Identified biologically relevant structures: tumor core vs. outer ring with infiltrating TAMs/CAFs
- Maintained continuous boundaries without fragmentation despite high heterogeneity

#### Alignment Accuracy
**DLPFC alignment (9 slice pairs):**
- "SDELight achieved higher accuracy in all nine pairs of slices" (p.8)
- Layer-wise alignment accuracy superior to 9 comparison methods
- Spot-to-spot matching visualization showed "proportion of blue lines significantly higher" than STAligner

**MHypo dataset (single-cell resolution):**
- Highest layer-wise alignment accuracy in 4/4 slice pairs
- Significant advantage over SPACEL in complex regions (Bregma -0.09 to -0.14 mm)
- "Smallest decrease in accuracy" when handling complex spatial domains compared to simpler DLPFC

#### Biological Validation
- Cortical layer stratification matched known neuroanatomy
- Tumor microenvironment features aligned with literature (TAMs, CAFs in tumor periphery)
- Preserved biological structures after alignment without artificial distortions

#### Comparative Analysis Summary
SDELight consistently outperformed existing methods across:
- Multiple spatial technologies (10x Visium, MERFISH)
- Different tissue types (brain, tumor)
- Various evaluation metrics (NMI, HOM, COM, ARI, alignment accuracy)
- Both spot-resolution and single-cell resolution data

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
