---
layout: default
permalink: /paper-atlas/cellanova-56978e0f/
title: "CellANOVA"
nav: false
description: "单细胞研究常常包含多个样本，而每个样本都可能受到组织处理、细胞解离、建库、测序平台、操作人员等因素影响。整合算法希望让“相同状态”的细胞跨样本对齐，但对齐越强，越可能把真实的疾病、治疗或时间效应一起抹掉。结果可能出现两类问题： 生物信号丢失：不同条件的细胞被过度混合； 数值失真：校正后的基因表达偏离原始数据，影响差异表达和通路分析。"
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
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>CellANOVA</h1>
    <p>Recovery of biological signals lost in single-cell batch integration with CellANOVA</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellANOVA 方法详解

### 1. 它要解决什么问题？

单细胞研究常常包含多个样本，而每个样本都可能受到组织处理、细胞解离、建库、测序平台、操作人员等因素影响。整合算法希望让“相同状态”的细胞跨样本对齐，但对齐越强，越可能把真实的疾病、治疗或时间效应一起抹掉。结果可能出现两类问题：

1. 生物信号丢失：不同条件的细胞被过度混合；
2. 数值失真：校正后的基因表达偏离原始数据，影响差异表达和通路分析。

Harmony（*Nature Methods*, 2019）、Scanorama（*Nature Biotechnology*, 2019）、scVI（*Nature Methods*, 2018）、Seurat（*Cell*, 2019）和 LIGER（*Cell*, 2019）等方法都能进行跨样本整合，但“批次混合得好”并不等价于“保留了真实生物学”，也不保证校正后的基因表达仍适合统计推断。论文把这一缺口概括为：我们通常不知道应该把样本对齐到什么程度，也没有原则来区分批次差异与样本间真实差异（`paper.md:21-33`, `paper.md:134-166`）。

CellANOVA 的核心不是再发明一种黑箱式对齐，而是把**实验设计**引入批次效应定义。

### 2. 最关键的概念：控制池

用户先指定一个或多个控制池（control pool）。同一个控制池中的样本，在当前研究问题下被认为“不应该存在感兴趣的差异”。因此，在控制了细胞状态之后，控制池内部的样本差异就被定义为批次效应或其他不需要的变异（`paper.md:39-51`）。

控制池是问题依赖的：

- 病例–对照研究：健康样本可以组成控制池；
- 纵向研究：治疗前基线样本可以组成控制池；
- 时间与技术人员混杂：不同时间点的未处理样本共同组成控制池；
- scRNA-seq 与 snRNA-seq 混合：健康的单细胞和单核样本共同覆盖协议差异。

这意味着“批次效应”不只等于纯技术噪声。只要某种样本间差异在当前问题中不感兴趣，并且被纳入控制池，它就可以被视为需要去除的变异。反过来，控制池之外、且不落在批次空间中的差异会被保留或恢复。

控制池有两个作用：

1. 提供生物学比较的基线；
2. 采样实验中可能出现的不需要变异。

如果控制池太窄，可能漏掉某些批次方向；如果控制池把真正感兴趣的差异也包含进去，这些差异可能被当作批次删除。

### 3. CellANOVA 的统计模型

设第 $i$ 个样本的预处理表达矩阵为 $X^{(i)}\in\mathbb{R}^{n_i\times p}$。CellANOVA 写成：

$$
X^{(i)}=C^{(i)}\left[M+B^{(i)}V^\top+T^{(i)}W^\top\right]+Z^{(i)}.
$$

这是论文 Eq. (1)（`paper.md:92-100`）。各部分含义如下：

| 符号 | 含义 |
|---|---|
| $C^{(i)}$ | 每个细胞的低维状态编码 |
| $M$ | 跨样本共享的主效应：某种细胞状态的平均表达模式 |
| $B^{(i)}V^\top$ | 第 $i$ 个样本的批次效应；$V$ 是跨样本共享的批次基底 |
| $T^{(i)}W^\top$ | 第 $i$ 个样本中剩余的、希望保留的生物变异 |
| $Z^{(i)}$ | 低秩结构之外的残差或噪声 |

真正重要的是前面的 $C^{(i)}$：批次效应不是“每个样本给所有细胞加同一个偏移”，而是可以随细胞状态变化。于是，同一技术因素可以对不同细胞类型、不同基因产生不同影响。主图 6 中，估计出的批次效应既按样本分离，也在同一样本内呈现细胞类型结构，直接支持这一建模选择。

### 4. 从输入到输出的完整流程

```text
原始计数 + 样本标签 + 控制池定义
        |
        v
步骤 1：归一化、log1p、HVG、标准化
        |
        v
步骤 2：初始整合，估计细胞状态 C
        |
        v
步骤 3：每个样本内用 C 回归原始表达，得到 R^(i)
        |
        +------------------------------+
        |                              |
        v                              v
所有样本平均得到 M             控制池内部按组中心化
                                       |
                                       v
                              堆叠残差并做 SVD
                                       |
                                       v
                                 得到批次基底 V
                                       |
                                       v
步骤 4：把表达残差投影到 V 的正交补空间
        |
        v
步骤 5：可选地估计剩余变异基底 W 和处理效应
        |
        v
批次校正的 cell-by-gene 矩阵
```

#### 步骤 1：预处理

论文对每个细胞做总量归一化到 10,000，再取 $\log(1+x)$ 并按基因中心化（`paper.md:325-328`）。当前源码 `preprocess_data` 则按最小整合单元分别处理，使用目标总量 100,000、log1p、批次感知的高变基因选择和 `sc.pp.scale`（`cellanova/model.py:265-308`）。因此，论文与代码的预处理思想一致，但参数并非完全相同。

#### 步骤 2：估计细胞状态 $\widehat C$

论文先用 Harmony 或其他可比方法得到初始整合，再取整合结果的前 $k_C$ 个左奇异向量：

$$
\widehat C=
\left[(\widehat C^{(1)})^\top,\ldots,(\widehat C^{(m)})^\top\right]^\top.
$$

这是 Eq. (3)（`paper.md:352-363`）。它代表跨样本共享的细胞状态坐标。当前 `calc_ME` 会直接运行 PCA 和 Harmony，重构到基因空间后再做 SVD，默认 `k_harmony=70`、`dim_ME=70`（`cellanova/model.py:21-77`）。

这一初始整合可以比较“保守地强”：作者建议先优先达到良好批次混合，即使损失一部分生物信号，再让 CellANOVA 恢复与批次空间正交的部分（`paper.md:307-313`）。

#### 步骤 3：把细胞状态映射回基因表达

对每个样本，把 $X^{(i)}$ 对 $\widehat C^{(i)}$ 做无截距普通最小二乘，得到回归系数矩阵 $R^{(i)}$。它描述“这个样本中，细胞状态如何映射到各基因表达”。代码使用 `LinearRegression(fit_intercept=False)`，每个 integration unit 单独拟合（`cellanova/model.py:60-68`, `model.py:143-150`）。

所有样本的平均给出主效应：

$$
\widehat M=\frac{1}{m}\sum_{i=1}^m R^{(i)}.
$$

这是 Eq. (7)。

#### 步骤 4：只用控制池学习批次基底 $\widehat V$

若只有一个控制池，先计算控制样本的平均回归效应：

$$
\widehat M_0=\frac{1}{m_0}\sum_{i=1}^{m_0}R^{(i)},
$$

再对每个控制样本中心化：

$$
E_0^{(i)}=R^{(i)}-\widehat M_0.
$$

把所有 $E_0^{(i)}$ 纵向堆叠，对矩阵做 SVD，前 $k_B$ 个右奇异向量构成 $\widehat V$（Eqs. (4)–(6)，`paper.md:372-396`）。

如果有多个控制池，每个控制样本只减去所属池的均值：

$$
E_0^{(i)}=R^{(i)}-
\sum_{j=1}^q\mathbf 1_{i\in\mathcal C_j}\widehat M_{\mathcal C_j}.
$$

这是 Eq. (10)（`paper.md:453-464`）。源码 `calc_BE` 的 `control_dict` 循环与这一逻辑直接对应（`cellanova/model.py:134-168`）。

#### 步骤 5：投影掉批次空间

批次校正结果为：

$$
\widetilde X^{(i)}=
\widehat C^{(i)}\widehat M+
\left(X^{(i)}-\widehat C^{(i)}\widehat M\right)
\left(I-\widehat V\widehat V^\top\right).
$$

这是 Eq. (2)（`paper.md:117-125`）。理解它可以分成两部分：

1. 保留由细胞状态决定的平均表达 $\widehat C^{(i)}\widehat M$；
2. 对剩余表达做正交投影，只保留不在批次基底 $V$ 中的部分。

源码 `calc_BE` 等价地先计算残差在 $V$ 上的投影，再从标准化表达中减去（`cellanova/model.py:168-173`）。输出 `adata.layers['corrected']` 仍然是 cell-by-gene 矩阵，可以继续做 DEG、GSEA 或轨迹分析。

#### 步骤 6：估计剩余/处理效应

从每个样本的回归效应中减去 $\widehat M$，再去掉 $V$ 方向，堆叠后做 SVD 得到 $\widehat W$；随后：

$$
\widehat T^{(i)}=F^{(i)}\widehat W.
$$

这是 Eq. (9) 附近的估计步骤（`paper.md:424-444`）。源码 `calc_TE` 生成 `trt_effect`，并把它与 `main_effect` 相加得到 `denoised`（`cellanova/model.py:214-244`）。论文在生物信号检测中使用的正是“主效应 + 处理效应”重构（`paper.md:496-505`）。

### 5. 为什么这个方法能“恢复”被整合抹掉的信号？

初始整合主要提供细胞状态坐标 $C$，而不是最终的基因表达答案。CellANOVA 回到原始/标准化表达空间，比较不同样本中“同一种细胞状态对应的表达系数” $R^{(i)}$。控制池告诉模型：这些系数差异中的哪些方向应该被看作批次。只要非控制样本的生物差异有一部分落在 $V$ 的正交补空间，该部分就不会被删除。

因此，恢复能力有一个清楚的边界：

> 与批次空间平行的生物信号无法被区分，也无法被恢复。

CellANOVA 是保守的：宁可删除控制池中出现的方向，也不把它们重新解释为阳性生物信号（`paper.md:128`）。

### 6. 论文如何验证它？

论文没有只看 UMAP，而是把评价拆成三个问题。

#### 6.1 批次是否真的被去掉？

在控制池中每次留出一个样本，用其余控制样本估计 $V$，再检查被留出的样本是否仍与控制池混合。主图 3 显示 CellANOVA 的 iLISI 与初始整合相当或更好，说明恢复信号没有明显重新引入不需要的变异（`paper.md:134-151`）。

#### 6.2 校正是否扭曲表达？

论文比较每个细胞校正前后的基因表达相关性，并比较同一批次内差异表达的调整后 $P$ 值。初始整合后的平均相关性低于 0.5，CellANOVA 后稳定高于 0.9；主图 3 的 $P$ 值散点也更接近 $y=x$（`paper.md:154-166`）。

#### 6.3 是否恢复了真实生物差异？

oobNN 只在其他批次中寻找邻居，再检查邻居是否富集于相同生物条件。主图 4 中，CellANOVA 恢复了 T1D、治疗组和时间点相关的邻域结构，而 Harmony 或 Seurat 初始整合常把这些差异混在一起（`paper.md:169-198`）。

更强的证据来自正交验证：

- 肾脏 scRNA+snRNA 中恢复的疾病通路可在独立 KPMP scRNA 数据中重复；
- TNF–NF-κB 活性与 Visium 空间切片中的损伤近端小管区域共定位；
- 免疫治疗纵向数据中的 G2–M、干扰素信号与同一队列的 Ki-67、ISG15 流式结果一致（`paper.md:201-242`）。

在四个综合基准图中，CellANOVA 的可见归一化总分分别为 0.79、0.81、0.80、0.82，四个数据集均排第一。模拟实验中，Harmony-based CellANOVA 的 AUC 为 0.869，Harmony 为 0.552（直接读取扩展数据图 5–9；详见 `figure_analysis.md`）。

### 7. 源码实现与论文的对应关系

```text
preprocess_data
    -> calc_ME   : Cmat, Mmat, main_effect
    -> calc_BE   : V_BE_basis, corrected
    -> calc_TE   : W_TE_basis, trt_effect, denoised
```

README 和教程 notebook 给出的调用顺序与上述一致。核心模型实现与论文总体相符，但需要注意：

- 预处理目标总量：论文 10,000，源码 100,000；
- `calc_BE`/`calc_TE` 的自动秩选择使用 `np.argmax` 的零基索引，存在少取一维、甚至得到 `k=0` 的风险；
- `calc_oobNN` 默认 15 个邻居而论文使用 30，并在已经排除同批细胞后仍删除第一个返回邻居；
- 仓库有 5 个教程 notebook，但没有覆盖全文所有图表的一键脚本；
- 两个示例数据文件只是 Git LFS 指针，当前快照没有真实矩阵；
- 自动化测试 **Not found**。

因此，代码–论文整体一致性评为中等：核心线性代数与投影步骤可直接对应，但默认值、评价辅助函数和完整复现链存在明确缺口（详见 `doc_code.md`）。

### 8. 什么时候适合用，什么时候要谨慎？

适合：

- 有明确健康、基线、未处理或参考样本；
- 控制样本覆盖主要技术变化；
- 目标是恢复样本间、细胞状态特异的表达差异；
- 需要可用于 DEG/GSEA 的 cell-by-gene 校正矩阵。

谨慎：

- 控制池很小或不能代表非控制样本的技术变化；
- 批次与真实效应几乎完全重合；
- 初始整合没有得到可信的细胞状态；
- 只凭 UMAP 分离就把恢复的差异解释为生物学。

实践中应优先运行留一控制样本诊断：如果被留出的控制样本不能与其余控制良好混合，说明控制池可能不足以覆盖批次变化（`paper.md:301-307`）。

### 9. 尚未找到的细节

- 每个发表数据集最终使用的 $k_B$、$k_T$：**Not found**；
- 能重建全部主图和扩展图的统一执行入口：**Not found**；
- 当前快照中的真实示例 H5AD/RDS 数据：**Not found**，仅有 LFS 指针；
- 自动化测试：**Not found**；
- 补充材料 Markdown：未获取，因此未作为本讲解证据。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellANOVA: Recovery of Biological Signals Lost in Single-Cell Batch Integration

### Problem

Single-cell integration is usually tuned to mix samples, but aggressive alignment can erase real condition-specific variation and distort gene-level expression. Because technical and biological differences are confounded across samples, existing workflows often treat integration as a black-box parameter search and provide no principled answer to how much variation should be removed (`paper.md:21-33`).

CellANOVA reframes the problem through experimental design. Users declare one or more **control pools** whose within-pool sample differences are irrelevant to the scientific question. Those differences define unwanted variation; biological variation outside the learned batch subspace can then be recovered (`paper.md:39-51`, `paper.md:89-128`).

### Relation to existing methods

CellANOVA is a post-integration statistical layer rather than a replacement for all integrators. The paper initializes it with Harmony (*Nature Methods*, 2019) and also evaluates Seurat integration (*Cell*, 2019), LIGER (*Cell*, 2019), Scanorama (*Nature Biotechnology*, 2019), scVI (*Nature Methods*, 2018), Symphony, scANVI and scGen. These methods can mix batches effectively, but the paper shows that mixing alone does not ensure preservation of between-sample biology or valid gene-level comparisons (`paper.md:134-166`, `paper.md:245-251`).

### Method in brief

For each sample $i$, CellANOVA models expression as

$$
X^{(i)}=C^{(i)}\left[M+B^{(i)}V^\top+T^{(i)}W^\top\right]+Z^{(i)}.
$$

$C^{(i)}$ encodes cell state, $M$ is the cross-sample main effect, $B^{(i)}V^\top$ is state- and sample-specific batch variation, and $T^{(i)}W^\top$ is remaining biological variation. The algorithm:

1. obtains a cell-state representation from an initial integration;
2. regresses original expression on that representation within each sample;
3. learns the batch basis $V$ from centered control-pool regression effects;
4. projects residual expression into the orthogonal complement of $V$;
5. optionally estimates a low-rank remaining/treatment basis $W$.

The output is a batch-corrected cell-by-gene matrix suitable for differential expression, pathway analysis and trajectory reconstruction, not only a low-dimensional embedding (`paper.md:89-128`, `paper.md:346-450`).

### Evaluation

The paper tests four primary study designs: a type 1 diabetes case–control dataset, a longitudinal NSCLC immunotherapy trial, a technician-confounded mouse radiation study, and a kidney scRNA-seq/snRNA-seq atlas. It also evaluates a three-platform NSCLC atlas, independent KPMP kidney data, spatial transcriptomics, flow cytometry and simulations.

Evaluation separates three objectives:

- **batch removal:** held-out controls, iLISI, silhouette batch and kBET;
- **distortion:** cell-wise pre/post expression correlation and preservation of within-batch DEG adjusted $P$ values;
- **biological signal:** oobNN condition composition, cLISI, replicated pathways, spatial colocalization and orthogonal flow measurements.

The main evidence is consistent across these views. CellANOVA keeps held-out controls mixed while raising average pre/post expression correlations from below 0.5 after initial integration to above 0.9 after recovery (`paper.md:148-166`). It restores condition-associated neighborhood structure in T1D, immunotherapy and radiation data (`paper.md:169-198`). In the kidney atlas, recovered disease pathways replicate in independent KPMP scRNA-seq data, and TNF–NF-κB activity colocalizes with injured proximal tubule regions in spatial data (`paper.md:201-224`). Longitudinal G2–M and interferon signals agree with matched Ki-67 and ISG15 flow-cytometry measurements (`paper.md:230-242`).

Across the four broad benchmark figures, the displayed normalized overall scores for CellANOVA are 0.79, 0.81, 0.80 and 0.82, ranking first in each dataset. In the simulation benchmark, Harmony-based CellANOVA reaches an AUC of 0.869 versus 0.552 for Harmony alone; these values were read directly from Extended Data Figs. 5–9 (`figure_analysis.md`).

### Interpretation and limitations

CellANOVA can recover only the component of biological variation orthogonal to the learned batch basis. If meaningful signal shares the same directions as unwanted variation, the conservative projection removes it. Performance also depends on a representative control pool and a useful initial cell-state integration. The shared-batch-basis assumption should be checked with the paper's hold-one-control-out diagnostic (`paper.md:289-319`).

The method is therefore strongest when the study includes well-chosen baseline/control samples spanning expected technical variation. It is not a guarantee that every between-sample difference is biological, and UMAP separation alone is insufficient evidence.

### Reproducibility assessment: 3/5

The local GitHub snapshot contains the installable `cellanova` 0.1.0 package, direct implementations of preprocessing and the three model stages, a quick start, and five tutorial notebooks. The core paper-to-code fidelity is medium: the main factorization and projection are directly implemented, but the code uses a normalization target of 100,000 rather than the paper's 10,000, automatic SVD-rank selection has an apparent zero-based-index issue, and the oobNN helper differs from the published procedure (`doc_code.md`).

The snapshot does not contain automated tests or a complete driver for all paper panels. Its example H5AD and RDS files are unresolved Git LFS pointers, so external data retrieval is required. Exact experiment-specific ranks for every published analysis were **Not found**. Code is publicly linked by the article (`paper.md:634-637`), but the snapshot alone is insufficient for one-command full-paper reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
