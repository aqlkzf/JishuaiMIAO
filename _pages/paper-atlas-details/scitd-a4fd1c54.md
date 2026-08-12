---
layout: default
permalink: /paper-atlas/scitd-a4fd1c54/
title: "scITD"
nav: false
description: "scITD 把多供体单细胞数据压缩为一组可解释的多细胞因子：每个因子同时告诉研究者“哪些人沿这个过程不同”以及“哪些基因在每种细胞中共同构成这个过程”，再用临床关联、通路、独立队列和遗传证据逐层解释这些无监督轴。"
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
      <span>Representation Models</span>
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>scITD</h1>
    <p>Coordinated, multicellular patterns of transcriptional variation that stratify patient cohorts are revealed by tensor decomposition</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scITD 方法详解：从多供体单细胞数据中发现跨细胞类型协同变化

### 1. 它想解决什么问题？

在多人群 scRNA-seq 数据中，同一种细胞的表达状态会因遗传、环境、疾病严重程度、药物和技术批次而在供体之间变化。更重要的是，一个系统性过程往往同时影响多种细胞：例如免疫刺激可能让髓系细胞上调趋化因子，同时让另一类细胞改变受体或黏附相关基因。

传统做法常常对每种细胞分别做 PCA，再尝试匹配各细胞类型的主成分。但不同细胞类型的 PC 往往存在中等强度、非一一对应的相关，难以判断哪些变化属于同一个跨细胞过程。

scITD（single-cell interpretable tensor decomposition）要回答的是：

> 哪些基因在不同细胞类型中以共享或细胞特异的方式共同变化，并形成能够区分供体的“多细胞表达模式”？

它是无监督方法：疾病、治疗等供体标签不参与因子提取，只在得到因子后用于解释。这一点适合复杂患者队列，因为同一个临床标签可能由多个相互独立、只在部分患者中出现的分子过程组成。

### 2. 为什么已有方法不够？

- **逐细胞类型 PCA**：能找到单个细胞类型内的供体差异，却没有天然的一一对应机制来组合不同细胞类型的轴。
- **DIALOGUE**（*Nature Biotechnology*, 2022）：可发现多细胞程序，但论文中的成人 SLE 比较显示，多个 DIALOGUE 因子都强烈对应同一个干扰素轴，独立过程之间较难区分。
- **Multicellular factor analysis**（*eLife*, 2023）以及其他专门模型：论文指出，这类方法可能需要估计较多参数、受异常供体影响或计算成本较高。
- **MOFA / 展平张量后的 PCA**：可以产生类似的供体因子，但不一定同时兼顾复杂模式下的恢复精度、细胞类型可解释性、稳定性和速度。

scITD 的设计重点不是发明新的临床关联检验，而是先得到结构清晰的无监督表示：一个因子同时包含“哪些供体不同”和“哪些细胞类型中的哪些基因不同”。

### 3. 输入、输出与基本假设

#### 输入

- 原始整数 UMI 计数矩阵（基因 × 细胞）；
- 细胞元数据，至少包含供体和细胞类型；
- 要分析的细胞类型集合；
- 每个供体/细胞类型的最少细胞数、归一化、变异基因、方差缩放和可选批次变量；
- Tucker 分解的供体秩和基因秩。

补充材料特别提醒：用于 scITD 的表达矩阵应保留原始、未按供体对齐的数据。若在输入前做与供体混杂的样本对齐或批次校正，可能先把真正的供体间变化消掉。可先清除空液滴、双细胞和高线粒体比例细胞；若需要批次校正，应在 scITD 内按供体级批次变量处理。

#### 输出

每个因子 $p$ 有两个核心部分：

1. **供体得分向量**：每个供体在该表达模式上的位置；
2. **基因 × 细胞类型载荷矩阵**：该模式由哪些基因、在哪些细胞类型中以何种方向构成。

后续还可计算解释方差、基因显著性、供体元数据关联、GSEA、细胞组成关联、投影到新队列和配体–受体推断。

#### 假设与边界

- 保留的每个供体都必须在所有选定细胞类型中有足够细胞，否则无法组成完整张量。
- 细胞类型注释在供体间应具有一致含义。
- 主要过程能够形成低秩、以线性协变为主的结构。
- 目标过程必须在供体间有足够高的变化，才会成为无监督高方差因子。
- pseudobulk 的解释分辨率受注释粒度控制：过粗会混入亚群比例变化，过细则容易造成细胞不足和供体缺失。

### 4. 一张图看懂完整流程

```text
原始 UMI + 供体/细胞类型元数据
            |
            v
检查输入，按细胞类型拆分
            |
            v
保留在所有细胞类型中都有足够细胞的供体
            |
            v
每种细胞分别按供体求和 -> pseudobulk
            |
            v
TMM 校正库大小 -> ×10000 -> log1p
            |
            v
各细胞类型估计过度离散基因 -> 取基因并集
            |
            v
每个“细胞类型-基因”在供体间中心化和单位方差化
            |
            v
按 normalized variance^0.5 恢复生物变异权重
            |
            +--> 可选：按细胞类型做 ComBat
            |
            v
堆叠为 X[供体 × 基因 × 细胞类型]
            |
            +--> SVD/置换选秩 + 下采样稳定性诊断
            |
            v
Tucker / HOOI 分解
            |
            v
基因因子做 ICA，核心张量做 varimax，供体因子反旋转
            |
            v
供体得分 A-hat + 多细胞载荷 F-hat
            |
            v
按单因子解释方差排序
            |
            +--> 元数据 / GSEA / LR / 新队列投影
```

### 5. 第一步：把单细胞数据变成供体张量

#### 5.1 为什么要 pseudobulk？

scITD 研究的是供体间变化，统计单位应是供体而不是细胞。对每种细胞类型，它把同一供体的 UMI 计数按基因求和，得到供体 × 基因矩阵。这避免把同一人的大量细胞误当成相互独立的重复样本。

#### 5.2 归一化和变异基因

默认流程使用 edgeR 的 TMM 因子修正 pseudobulk 库大小，然后除以调整后的库大小、乘以 10,000 并做 `log1p`。

接着，每种细胞分别估计考虑均值–方差趋势后的 normalized variance，并选出过度离散基因。不同细胞类型选出的基因取并集，原因是一个重要过程可能只在某一种细胞中变化；若要求每种细胞都显著变异，会错误丢掉细胞特异信号。

#### 5.3 为什么还要中心化和方差缩放？

对每个细胞类型中的每个基因，scITD 在供体间中心化并缩放到单位方差。这样，细胞类型之间的基线表达差异不会成为主要轴，模型看到的是同一细胞类型内部的供体差异。

随后它把标准化后的表达乘以

$$
({\rm normalized\ variance})^{\alpha},
$$

默认 $\alpha=0.5$。因此高生物变异基因仍可比低变异基因贡献更多，而不是所有基因被永久压成相同权重。

最后把 $C$ 个供体 × 基因矩阵堆叠为

$$
X\in\mathbb{R}^{n\times G\times C},
$$

三个维度依次是供体、基因和细胞类型。

### 6. 第二步：Tucker 分解如何变成可解释因子？

标准 Tucker 分解为

$$
X\approx G{\times }_{1}A{\times }_{2}B{\times }_{3}C.
$$

其中：

- $A$：供体因子矩阵；
- $B$：基因因子矩阵；
- $C$：细胞类型因子矩阵；
- $G$：核心张量；
- ${\times}_m$：沿第 $m$ 个张量维度做矩阵乘法。

原始的 $A,B,C,G$ 不容易直接解释。scITD 把后面三项重新组合：

$$
\begin{array}{c}
X\approx G{\times }_{1}A{\times }_{2}B{\times }_{3}C\\
=(G{\times }_{2}B{\times }_{3}C){\times }_{1}A\\
=F{\times }_{1}A.
\end{array}
$$

$F$ 的维度是“供体因子 × 基因 × 细胞类型”。因此第 $p$ 个切片 $F_{p,:,:}$ 就是第 $p$ 个多细胞表达模式，而 $A_{:,p}$ 是其供体得分。

主分析保留完整细胞类型秩：代码会把第三个秩覆盖为细胞类型数，并在 hybrid 分支把细胞类型因子矩阵设为单位矩阵。这意味着模型不会把几个细胞类型先压缩成一个难以辨认的混合轴。

### 7. 第三步：为什么还要 ICA 和 varimax 旋转？

Tucker 因子具有旋转不唯一性：只要对应项做反旋转，重构误差可以不变。scITD 利用这一自由度提高解释性。

#### 第一步旋转：基因因子 ICA

它先对基因因子做 ICA，希望不同基因模块尽量独立。代码中的 `ica::icafast()` 完成旋转，并重新把每个向量归一化到长度 1。

#### 第二步旋转：核心张量 varimax

然后对沿供体模式展开的核心做 varimax，使每个基因模块尽量主要参与少数供体因子，得到更简单的结构。同时对供体得分做逆转置反旋转，从而保持重构。

论文写为：

$$
\hat{G}=X{\times }_{1}{A}^{T}{\times }_{2}{\hat{B}}^{T}{\times }_{3}{C}^{T},
$$

以及

$$
\begin{array}{c}
X_{(1)}\approx A\times R^&#123;&#123;T}^{-1}}\times R^{T}\times\hat{G}_{(1)}\times(C\otimes\hat{B})^{T}\\
=\hat A\times\hat F_{(1)}.
\end{array}
$$

直觉上，ICA 让“基因程序”更独立，varimax 让“哪些程序组合成某个供体轴”更稀疏清晰。

### 8. 解释方差和因子排序

只用第 $p$ 个因子重构张量为 $\widetilde X_p$，其解释方差为

$$
{\rm explained}\,&#123;&#123;\rm variance}}_{p}=1-\frac&#123;&#123;\Vert X-{\tilde X}_{p}\Vert}_{F}^{2}}&#123;&#123;\Vert X\Vert}_{F}^{2}}.
$$

代码把结果乘以 100 作为百分比，并按该值从高到低重排因子。它还能只保留一个细胞类型的重构分量，计算某因子中每个细胞类型的解释方差。

旋转后的因子不必像 PCA 主成分那样保持相互正交，因此各单因子解释百分比不一定简单相加为 100%。

### 9. 如何选因子数？

scITD 区分：

- **供体秩**：最终要解释的多细胞因子数；
- **基因秩**：Tucker 中用于压缩基因维度的因子数。

`determine_ranks_tucker()` 把张量沿不同模式展开，计算增加 SVD 成分时重构误差改善了多少，再与打乱细胞–供体对应或张量纤维后的随机基线比较。当新增成分不再明显优于随机数据时，后续维度更可能是噪声。

该过程需要多次置换和 SVD，计算较慢，所以论文还结合因子稳定性和每个因子显著基因数做判断。成人 SLE 中，诊断建议约 7–12 个供体因子；作者保守选择 7 个供体因子和 20 个基因因子。

### 10. 因子得到以后怎么解释？

#### 10.1 先同时看得分和载荷

因子整体符号可任意翻转。若供体得分为正，则相对于负得分供体，它倾向于高表达正载荷基因、低表达负载荷基因。论文的成人 SLE 脚本手动把第一个因子乘以 $-1$，只是为了让高 ISG 表达显示为正方向，并不改变模型。

#### 10.2 元数据关联

因子提取后，供体得分可与连续、二分类或有序临床变量做回归。成人 SLE 使用线性模型 F 检验、logistic 回归卡方检验和有序 probit 回归，并做 BH 校正。

#### 10.3 基因显著性和 GSEA

jackstraw 路径随机打乱“基因–细胞类型纤维”在供体间的值，重新分解并形成 F 统计量零分布；真实基因–因子关联再与零分布比较。显著载荷可按细胞类型做 GSEA。

#### 10.4 配体–受体推断

作者不是只枚举同时表达的 LR 对，而是检验：源细胞中的配体表达是否跨供体预测目标细胞的 WGCNA 模块 eigengene，同时要求目标细胞表达相应受体。这个步骤建立在 scITD 已识别的供体协变上，但本身仍是统计推断，不等于干预证据。

#### 10.5 投影到独立队列

补充材料描述了用未做核心旋转的原始载荷计算新供体得分，再归一化并应用已保存的 varimax 旋转。这样可检验独立队列是否表达同一个模式，而不必假设重新分解会得到完全同序的因子。

### 11. 论文如何验证 scITD？

#### IFNβ 控制实验

16 个供体中 8 个接受 IFNβ 刺激。不给模型治疗标签时，因子 1 完全分开对照和刺激组，并恢复共享及细胞特异的响应基因。这证明“供体得分 + 基因×细胞类型载荷”能表达一个已知多细胞扰动。

#### 模拟和方法比较

SplatPop 模拟包含 50 个供体、500 个基因、2 种细胞和已知多细胞模式。作者用供体分组恢复的 $R^2$ 与真实基因集合的 AUC 比较 scITD、DIALOGUE、MOFA 和 PCA。随着真实模式数增加，scITD 的供体分层 $R^2$ 仍保持很高，而其他方法下降更明显。

成人 SLE 中，scITD 因子在供体下采样后较稳定；运行时间仅比 PCA 慢数秒，明显快于图中 DIALOGUE。不同方法的预处理和供体数无法完全一致，因此这是该实验设计下的比较，而不是所有数据上的普遍定理。

#### SLE 应用

- **aSLE_F1**：跨多细胞类型的干扰素刺激基因模式，与疾病活动相关。
- **aSLE_F2**：与 aSLE_F1 交互预测肾炎（交互 $P=0.0038$），包含细胞周期、迁移、p38-MAPK 和 TCR 相关结构。
- **aSLE_F3**：与泼尼松使用及剂量相关，呈现多细胞糖皮质激素响应。
- 在独立儿童 SLE 队列中，论文报告这些模式和关联具有复现性，而且因子相关基因比直接监督式 DE 基因集合更稳定。

#### 从因子到机制假设

在 aSLE_F2 中，cMonocyte 的 *ICOSLG* 与 Th_m5 模块和因子得分均相关。作者进一步用 NicheNet、儿童队列、孟德尔随机化和共定位加强 *ICOSLG*–*ICOS* 假设。这里的因果结论仍依赖工具变量等假设；图中第二个遗传峰的未条件化 JLIM 并不显著。

#### COVID-19 应用

83 名 COVID-19 患者和 20 名健康供体中，CVD_F2 随严重程度升高，结合了淋巴细胞增殖、单核细胞 MHC-II 降低和候选 Th→单核细胞 *IL16*–*CD4* 关系。论文还在独立 COVID-19 数据中评估该模式。

### 12. 最容易误读的地方

1. **因子与临床变量相关，不代表临床变量参与了训练。** scITD 先无监督分解，再做关联。
2. **正负号没有绝对生物学意义。** 得分和载荷必须成对解释，整体可同时翻转。
3. **LR 箭头不都是直接证据。** 主图用颜色区分观测相关、推断关系和文献支持假设。
4. **pseudobulk 因子可能包含亚群比例变化。** 特别是在粗粒度注释下，需要结合细胞组成诊断。
5. **“公开代码”不等于“一键复现论文”。** 核心 R 包与图形脚本都已获取，但图形脚本依赖作者本机绝对路径、未随快照提供的 RDS/XLSX 对象和未锁定的 R 环境。

### 13. 代码与论文的一致性结论

核心方法一致性为 **高**：源码直接实现了供体 pseudobulk、TMM/log 归一化、过度离散基因并集、方差缩放、ComBat、张量堆叠、rTensor Tucker/HOOI、hybrid ICA–varimax 旋转、解释方差、秩选择和 jackstraw。

复现性边界为 **Partial/Not found**：成人 SLE 脚本能验证关键参数和执行顺序，但本工作区无法仅凭现有文件从零生成所有论文图。应把“算法实现可信”和“整篇论文可移植复现”分开评价。

### 14. 一句话总结

scITD 把多供体单细胞数据压缩为一组可解释的多细胞因子：每个因子同时告诉研究者“哪些人沿这个过程不同”以及“哪些基因在每种细胞中共同构成这个过程”，再用临床关联、通路、独立队列和遗传证据逐层解释这些无监督轴。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## scITD — Summary

### Problem

Population-scale scRNA-seq makes it possible to ask how expression states in different cell types covary across people. Standard PCA can find donor axes within one cell type, but matching separate cell-type PCs is ambiguous. Earlier multicellular approaches such as DIALOGUE (*Nature Biotechnology*, 2022) and multicellular factor analysis (*eLife*, 2023) address joint structure but, as framed by the paper, can require many parameters, be sensitive to outliers or be computationally expensive.

scITD (single-cell interpretable tensor decomposition) is an unsupervised method for finding donor-stratifying “multicellular patterns”: coordinated sets of genes whose expression varies across donors in shared or cell-type-specific ways.

### Core idea

For each cell type, scITD aggregates cells into donor pseudobulks, normalizes them, selects the union of overdispersed genes, centers expression across donors and rescales by normalized variance. The aligned matrices are stacked into a donor × gene × cell-type tensor.

The method applies Tucker decomposition/HOOI and rearranges the result into two interpretable objects per factor:

- a donor-score vector, the axis that stratifies people;
- a gene-by-cell-type loading matrix, the associated multicellular expression pattern.

A hybrid rotation—ICA on gene factors followed by varimax on the core with a counter-rotation of donor scores—seeks more independent gene programs and simpler factor structure without changing reconstruction error. Factors are ordered by single-factor Frobenius reconstruction variance. Donor metadata, pathways, cell composition and ligand–receptor relationships are analyzed after factor extraction, so clinical labels do not drive the decomposition.

### Evaluation and main findings

The paper first uses a controlled IFNβ experiment with 16 donors. Without treatment labels, factor 1 perfectly separates the eight stimulated and eight control donors and recovers shared plus cell-type-specific response genes.

In SplatPop simulations (20 replicates; 50 donors, 500 genes and two cell types), scITD is compared with DIALOGUE, MOFA and unfolded-tensor PCA using donor-assignment $R^2$ and loading-based AUC. scITD retains high donor-stratification accuracy as the number of programmed multicellular patterns increases. On the adult SLE data, it produces factors that are stable under donor downsampling and runs second fastest after PCA in the reported benchmark; preprocessing and donor counts were not identical across methods, so the comparison is design-specific.

The principal disease applications are:

- **Adult SLE:** 115 persons with SLE, 518,310 cells and seven broad cell types; the main decomposition uses 7 donor factors and 20 gene factors. aSLE_F1 captures a multicellular interferon-stimulated-gene program associated with disease activity. aSLE_F2 interacts with aSLE_F1 in predicting nephritis ($P=0.0038$) and includes cell-cycle, migration, p38-MAPK and TCR-related structure. aSLE_F3 tracks prednisone exposure and a multicellular glucocorticoid response.
- **Replication:** factor associations and gene programs are projected to or compared with a pediatric SLE cohort. The paper reports stronger cross-study reproducibility of scITD factor-associated genes than direct supervised DE gene sets.
- **Cell–cell interaction hypothesis:** cMonocyte *ICOSLG* expression correlates with a Th-cell module and aSLE_F2. NicheNet support, pediatric replication, Mendelian randomization and colocalization strengthen the proposed *ICOSLG*–*ICOS* link, although the causal interpretation remains assumption-dependent.
- **COVID-19:** 83 persons with COVID-19 plus 20 healthy donors, 452,740 cells and five major cell types. CVD_F2 tracks severity and combines lymphocyte proliferation, reduced monocyte MHC-II expression and a candidate Th-to-monocyte *IL16*–*CD4* interaction. The severity-associated pattern is evaluated in an independent COVID-19 dataset.

### Strengths

- Jointly models donor variation across cell types while retaining cell-type-specific loadings.
- Produces an intuitive score-plus-loading representation rather than raw Tucker factors alone.
- Fully unsupervised factor extraction separates discovery from phenotype testing.
- Handles shared and cell-type-specific genes in the same factor.
- Includes rank diagnostics, stability analysis, gene significance, metadata testing, projection, GSEA and LR utilities.
- Main equations and core pipeline have high agreement with the acquired R source.

### Limitations

- Only sufficiently high-variance unsupervised processes can be recovered; weak phenotype-linked signals may be missed.
- The current decomposition is primarily linear.
- Results depend on cell-type annotation granularity. Coarse clusters can turn cell-subtype composition shifts into apparent expression factors.
- Donors without enough cells in every selected cell type are removed to maintain a complete tensor.
- Rank selection is computationally expensive and still requires judgment.
- Ligand–receptor arrows are statistical hypotheses, not direct perturbation evidence.
- The full paper workflow is not self-contained in this snapshot: analysis scripts use author-local absolute paths and unavailable precomputed RDS/XLSX objects.

### Reproducibility

**Rating: 3.5/5.** The primary R package and paper-linked analysis repository are present at recorded commits; the core preprocessing, Tucker/HOOI, rotations, variance calculations and adult-SLE parameter choices can be verified directly. The paper lists public datasets and a tutorial. However, the workspace does not include the large input datasets, a locked R environment or a portable driver for regenerating all figures. Core method fidelity is **high**, while end-to-end numerical and figure reproduction is **Partial/Not found** within the acquired scope.

### Bottom line

scITD's main contribution is a practical donor-level representation of multicellular covariation: each latent axis links who differs to which genes differ in each cell type. The paper supports this representation through a controlled perturbation, simulations, real-cohort benchmarks, independent validation and disease applications. Its biological diagrams are most useful when read as layered evidence—observed covariance, statistical inference and literature/genetic support—rather than as uniformly proven causal networks.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
