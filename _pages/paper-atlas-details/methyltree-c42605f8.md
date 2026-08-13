---
layout: default
permalink: /paper-atlas/methyltree-c42605f8/
title: "MethylTree"
nav: false
description: "MethylTree 用单细胞甲基化数据中自然积累的随机表观突变（epimutation）推断细胞之间的谱系关系。它面向无法进行遗传条形码标记的场景，尤其是人体样本、原位组织以及需要同时读取转录或染色质状态的实验。 传统路线各有明显限制。Mitchell 等（Nature, 2022）和 Fabre 等（Nature, 2022）的体细胞核基因组突变谱系研究通常依赖单细胞克隆扩增与深度全基因组测序，成本高、通量低，而且难以同时保留原始细…"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>MethylTree</h1>
    <p>High-resolution, noninvasive single-cell lineage tracing in mice and humans based on DNA methylation epimutations</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/ShouWenWang-Lab/MethylTree" target="_blank" rel="noopener noreferrer" aria-label="Open code for MethylTree">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MethylTree 方法详解：用 DNA 甲基化表观突变重建单细胞谱系

### 1. 方法要解决什么问题

MethylTree 用单细胞甲基化数据中自然积累的随机表观突变（epimutation）推断细胞之间的谱系关系。它面向无法进行遗传条形码标记的场景，尤其是人体样本、原位组织以及需要同时读取转录或染色质状态的实验。

传统路线各有明显限制。Mitchell 等（*Nature*, 2022）和 Fabre 等（*Nature*, 2022）的体细胞核基因组突变谱系研究通常依赖单细胞克隆扩增与深度全基因组测序，成本高、通量低，而且难以同时保留原始细胞状态。Ludwig 等（*Cell*, 2019）及 Weng 等（*Nature*, 2024）发展的线粒体突变路线提高了单细胞通量，但会受到线粒体遗传、漂变和选择的影响。两类 DNA 突变的积累速度也远低于 CpG 甲基化变化，因此不容易解析只相隔数天的发育分叉。

MethylTree 的核心观察是：CpG 位点每次细胞分裂发生甲基化改变的概率约为 $10^{-3}$，频率足够高，同时又能在一定时间尺度上保留共同祖先信号。不过，单细胞亚硫酸氢盐测序通常只覆盖约 5% 的基因组，两个细胞共同观测到的 CpG 更少，矩阵缺失率可超过 95%。因此，该方法不直接填补稀疏的“细胞 × 位点”矩阵，而是针对每一对细胞，只在双方共同观测到的区域上计算相似度。

### 2. 输入、输出与基本数据结构

#### 输入

1. 单细胞 CpG 甲基化调用结果，来源可以是 scBS-seq，也可以是修改后的 Camellia-seq 等多组学实验。
2. 作为特征的单 CpG 位点，或经过筛选、合并的基因组区域。
3. 可选的细胞类型标签或连续表型邻域；只有在需要去除细胞类型甲基化信号时才使用。
4. 可选的真实克隆或谱系标签，仅用于评价；它们不是论文概念算法的必要输入。不过，当前核心代码的接口要求提供一个存在重复值的 `clone_key`，这是实现层面的额外约束。

令 $A\in\mathbb{R}^{N\times P}$ 表示甲基化矩阵，$N$ 是细胞数，$P$ 是区域或 CpG 特征数。$A_{ix}$ 是细胞 $i$ 在区域 $x$ 的平均甲基化比例，未观测位置保留为 `NaN`。

#### 输出

- 校正后的 $N\times N$ 细胞相似度矩阵；
- 按谱系顺序排列的相似度热图和 UPGMA 谱系树；
- 通过区域重采样得到的子树支持度；
- 可选的甲基化克隆标签；
- 可选的谱系低维嵌入；
- 有真值时的谱系准确度 $Q$，以及克隆耦合、HSC 克隆总数等下游结果。

### 3. 从原始甲基化到谱系树的完整流程

```text
单细胞甲基化调用
        │
        ▼
细胞质控与特征构建
  ├─ 全部单 CpG，或
  └─ 500-bp 小窗筛选后合并成可变长度区域
        │
        ▼
稀疏细胞 × 区域矩阵 A（允许 NaN）
        │
        ▼
对每对细胞，在共同观测区域 Ωij 上计算 Pearson 相关 Sij
        │
        ▼
估计每个细胞的衰减因子 Zi，得到 S* = diag(Z) S diag(Z)
        │
        ├─ 若细胞类型信号占主导：估计 T，令 L = S* - T
        │
        ▼
相似度缩放到 [0,1]，距离 D = 1 - S
        │
        ▼
UPGMA 谱系树
  ├─ 80% 区域无放回重采样 × 100 次 → 分支支持度
  ├─ 支持度 + 子树内相似度 → 甲基化克隆
  └─ 谱嵌入 + 邻接图 + UMAP → 低维谱系表示
```

贯穿全流程的核心对象是细胞相似度矩阵，而不是经过插补的甲基化矩阵。这样可以尽量避免插补把随机、细胞特异的谱系表观突变平滑掉。

### 4. 质控与谱系信息区域选择

论文使用 Bismark v0.24.0 进行比对、去重和甲基化提取。单细胞质量通过转录起始位点附近预期的甲基化凹陷评价：计算平均甲基化 $m$ 与到 TSS 距离绝对值 $|x|$ 的 Pearson 相关 $C_{\mathrm{TSS}}$，保留

$$
C_{\mathrm{TSS}}>0.7
$$

且至少观测到 $5\times10^5$ 个不同 CpG 的细胞。仓库中的 `Preprocessing/scripts/run_bismark_only_met.sh:37-99` 直接实现了 Bismark 比对、去重、BAM 合并与甲基化提取；上述 TSS 质控的精确计算在该脚本中 **Not found**，笔记本目录只说明另有质控流程。

特征可以是全部单 CpG，但哺乳动物基因组包含两千多万个 CpG，计算代价较高。论文的加速方案先把基因组切成不重叠的 500-bp 小窗，再把所有细胞聚合为高覆盖 pseudobulk。对每个小窗计算平均甲基化 $m$，保留

$$
m_0\le m\le m_1,
$$

然后合并相邻小窗，并去掉在不足 10% 细胞中被观测到的区域。中等甲基化区域通常比极端低/高甲基化区域更容易包含随机谱系差异；过大的 100-kb 窗会把信号平均掉。

本地代码证据主要来自笔记本：`mouse_LK_downstream_analysis.ipynb:1072-1092` 使用 $m_0=0.1$、$m_1=0.6$、pseudobulk 最低读数 3，并设置 `merge=True`；底层辅助函数位于 `region.py:327-360`。

### 5. 稀疏条件下的细胞两两相似度

对细胞 $i,j$，令 $\Omega_{ij}$ 为双方都观测到的区域集合。MethylTree 计算

$$
S_{ij}=\operatorname{Corr}_{x\in\Omega_{ij}}(A_{ix},A_{jx}).
$$

不同细胞对可以使用完全不同的区域子集，因此不需要先填补缺失值。`similarity.py:11-109` 的精确慢速路线逐对求非空交集并计算 Pearson 相关，同时记录共享位点数。若相关系数为 `NaN`，代码会用所有有效矩阵元素的全局均值替换；论文没有描述这一细节。

代码还提供 `correlation_fast`（`similarity.py:111-155`）。它先按每个细胞所有已观测特征的全局均值中心化，再在共享位点上归一化。由于论文公式要求在每个细胞对的共享集合内计算 Pearson 中心，快速路线只是近似实现。论文全数据笔记本还直接读取预计算的 `correlation_fast` 相似度，而不是从原始调用重新生成。

### 6. 校正不同细胞的相关性衰减

测序噪声会降低相关性。若观测信号为 ${\bf x}_{\mathrm{o}}={\bf x}+{\boldsymbol\eta}_x$，则论文使用模型

$$
C({\bf x}_{\mathrm{o}},{\bf y}_{\mathrm{o}})
=\frac{C({\bf x},{\bf y})}{Z_xZ_y},
\qquad
Z_i=\frac{\sigma_{i_{\mathrm{o}}}}{\sigma_i}.
$$

因此校正后的细胞相似度为

$$
S^*_{ij}=Z_iS_{ij}Z_j.
$$

若所有 $Z_i$ 相同，只会整体缩放；真正改变树结构的是细胞间不均一的衰减。初始化为

$$
Z_i=\frac{1}{\sqrt{\max_{j\ne i}S_{ij}}},
\qquad
Z_i\leftarrow\frac{Z_i}{\operatorname{mean}(Z)}.
$$

优化目标是校正后非对角元素的变异系数：

$$
f_c(S^*)=
\frac{\sigma_{\mathrm{off}}(S^*)}{\mu_{\mathrm{off}}(S^*)}.
$$

论文用梯度下降更新

$$
Z_i\leftarrow Z_i-\epsilon
\frac{\partial f_c}{\partial S^*}
\frac{\partial S^*}{\partial Z_i},
$$

并报告 $\epsilon=0.01$、相邻两轮 $Z$ 的 L1 差异阈值 $\delta=0.01$。

`similarity.py:181-270` 与论文一致地实现了初始化、均值归一化、乘法校正、`std/mean` 目标和解析梯度。不过，高层接口默认把步长设为 0.05；代码按目标不再改善或权重越出 `[0.4,2.5]` 停止，并只执行一次外层校正调用，而不是按论文的 L1 阈值终止。因此原理与主体目标是 `Exact`，默认运行行为属于 `Partial`。

### 7. 去除细胞类型甲基化信号

当分化表型比共同祖先更强时，论文假设

$$
S=T+L,
$$

其中 $T$ 是细胞类型相似度，$L$ 是谱系相似度。对细胞 $i,j$，先选取与 $i$ 同类型、但排除 $j$ 的细胞，并用相似度不超过 $\mu+\sigma$ 的条件排除可能属于同一克隆的异常高相似细胞。记筛选后的集合为 $\Omega_i$ 和 $\Omega_j$，则

$$
T_{ij}=
\frac{
\sum_{k\in\Omega_i}S_{kj}+
\sum_{k\in\Omega_j}S_{ik}}
{|\Omega_i|+|\Omega_j|},
\qquad L=S-T.
$$

`similarity.py:324-386` 的离散细胞类型实现与此构造相符；`similarity.py:389-432` 还支持以邻域索引描述连续细胞状态。此步骤不应无条件使用：只有细胞类型明显主导相似度时才需要。论文图 2 和 Extended Data Fig. 3 直观展示了原始矩阵按表型聚类、去除 $T$ 后恢复克隆或胎儿来源的变化。

### 8. 缩放、建树与分支支持度

论文先将非对角相似度线性缩放到 $[0,1]$，并令对角线为 1：

$$
S_{ij}\leftarrow
\frac{S_{ij}-\min_{i\ne j}S_{ij}}
{\max_{i\ne j}S_{ij}-\min_{i\ne j}S_{ij}},
\qquad S_{ii}=1.
$$

代码 `similarity.py:435-442` 使用同样的仿射变换，但将非对角结果再乘 0.999，使只有对角线能达到 1。随后定义

$$
D_{ij}=1-S_{ij},\qquad D_{ii}=0,
$$

并用 UPGMA 重建树。`lineage.py:213-281` 的距离是与 $1-S$ 仿射等价的 `max(S)-S`，默认使用 UPGMA，也支持 NJ、FastME 和层次聚类。

分支置信度通过特征重采样计算：每次无放回抽取 80% 的区域，重新运行后续步骤得到一棵树，共重复 100 次；若原树某个子树的叶节点集合在重采样树中再次出现，不要求内部拓扑完全相同，就记为一次支持。`lineage.py:284-406` 的默认值正是 0.8 和 100，并按相同叶集合计数。各论文数据集在 bootstrap 中是否都重新执行相关性校正与细胞类型去除，在本地笔记本中 **Not found**。

### 9. 甲基化克隆识别

论文把子树内所有非对角相似度的中位数作为子树相似度，并要求：

1. 子树支持度 $>0.95$；
2. 子树内相似度高于整个相似度矩阵非对角元素的第 75 百分位。

仓库存在两条不同路线。`clone.py:17-290` 的 `identify_putative_clones_from_trees_with_support` 同时利用支持度和相似度，并可递归细分候选克隆；但默认支持阈值是 0.6，教程使用 0.8。高层 `perform_clone_inference` 分支实际调用 `clone.py:323-435` 的另一函数，只按子树权重中位数筛选，不使用 bootstrap 支持度。检索全部本地 Python 与笔记本后，论文特定的 0.95 调用 **Not found**。因此克隆识别的概念实现存在，但发布代码与论文的直接对应只能评为 `Partial`。

### 10. 低维谱系表示与评价指标

论文先对相似度矩阵进行谱嵌入，再构建近邻图并运行 UMAP，报告数据集特异的 `(n_components, n_neighbor, min_dist)`。`analysis.py:830-869` 也执行这三步，但把谱嵌入维数硬编码为 50，输入三元组实际控制近邻数、保留 PC 数和 UMAP `min_dist`，语义并不完全相同。

有真实克隆标签时，论文评价树的叶节点线性顺序。对克隆 $k$，令 $g_k$ 为其最大连续细胞块大小，$n_k$ 为克隆总细胞数，$M$ 为多细胞克隆数：

$$
Q=\left(\sum_k\frac{g_k-1}{n_k-1}\right)/M.
$$

$Q=1$ 表示每个克隆都形成连续区段。精确公式在本地包和笔记本中 **Not found**。`metric.py:14-149` 计算的是 `max_sum/tot_N`、连续性、熵和 Wasserstein 距离等另一组指标，只在特殊情况下可能与论文 $Q$ 一致，不能把它们等同于论文公式。

### 11. HSC 克隆总数估计

原位小鼠 HSC 实验只能抽样到总克隆库的一部分。令 $\phi$ 为样本中被判定为单细胞克隆的细胞比例。论文假设总体含 $M$ 个克隆，克隆大小分布取自 LL731 的经验分布，从中有放回抽取 $N$ 个细胞并得到 $\phi(M,N)$；对每只小鼠选择满足

$$
\phi(M_k,N_k)=\phi_k
$$

的 $M_k$，重复模拟 100 次估计变异。`test/MethylTree.ipynb:1300-1452` 有通用的重复抽样与插值教程，但连接三只论文小鼠及其参数的专用脚本 **Not found**。

### 12. 主要实验结果如何支撑方法

- 七轮分裂模拟中，在图示条件下即使只有 5% 或 1% 基因组覆盖，仍可重建 128 个细胞的完整层级。
- HEK 293T 连续扩增实验中，相关性偏差校正将谱系准确度从 $Q=0.845$ 提升到 $Q=1$；H9 胚胎干细胞和结直肠癌数据也达到 $Q=1$。
- 胎儿生殖细胞与性腺体细胞混合时，原始相似度主要反映细胞类型；去除表型背景后，胎儿来源恢复到 $Q=1$。
- 小鼠体外血液分化中，52 个多细胞 LARRY 克隆全部以 $Q=1$ 恢复；48 个多细胞甲基化克隆与 LARRY 标签的调整兰德指数约 0.98，覆盖 92% 细胞。
- 人脐带血分化中，20 个多细胞 LARRY 克隆以 $Q=1$ 重建。
- 小鼠和人类早期胚胎数据按胚胎来源高度准确聚类；同一人类第 5/6 天胚胎内推断出的四细胞期分支对内细胞团或滋养外胚层呈不同程度富集，支持早期命运随机承诺模型。
- 小鼠 HSC 数据 LL731 达到 $Q=0.90$、ARI 约 0.87–0.88；三只小鼠的单克隆比例模拟估计约有 250 个 EHT 来源 HSC 克隆，与经编辑效率校正的 DARLIN 估计 312 接近。

扩展图也给出了边界条件：区域选择和覆盖率显著影响结果，大窗口会失败；LL653E6 数据只有 $Q=0.68$、ARI=0.76。因此论文证据支持方法跨体系适用，但并不意味着每个数据集都接近完美重建。另一个应保留的原始证据差异是：Fig. 6 标题显示 ARI=0.88，而正文报告 0.87。

### 13. 代码入口与纸码对应关系

主要静态调用路径为：

```text
methylserver_call
  → comprehensive_lineage_analysis          analysis.py:84-279
    → methyltree_core                        lineage.py:18-281
      → compute_similarity_matrix            similarity.py:11-161
      → correct_similarity_matrix            similarity.py:164-321
      → remove_celltype_specific_similarity  similarity.py:324-432
      → rescale_similarity                    similarity.py:435-442
      → UPGMA / NJ / FastME tree              lineage.py:213-281
    → optional clone inference               clone.py
```

当前代码快照来自 `https://github.com/ShouWenWang-Lab/MethylTree`，提交 `33a693d0c41cfa56d61a6332e44163a9996ab416`。核心包固定了 Python 与依赖版本，提供教程、模拟、相似度校正、建树和 bootstrap 实现，但没有发现自动化测试套件。

综合评价为：**代码—论文一致性 medium；复现性 3/5。** 相似度主体、校正目标、细胞类型去除、UPGMA 和 bootstrap 有直接实现；快速相关、校正停止条件、缩放、嵌入和克隆路线存在明确偏差；主图笔记本依赖外部 AnnData 与预计算相似度，尚不能在本地形成单一的“原始数据到全部图表”执行链。

### 14. 假设、限制与必须保留的证据缺口

方法假设随机甲基化变化在目标时间尺度上足够稳定；筛选区域有足够的两两共同覆盖；测量衰减可分解为 $Z_iZ_j$；需要去表型时，细胞类型相似度和谱系相似度近似可加；并且 UPGMA 的聚类假设适合所需的谱系排序。

论文与本地证据共同表明，约 2% 覆盖在部分数据中可行，但推荐 5% 以提高稳健性；区域筛选依赖生物体系；差异很大的细胞类型需要已知标签或可靠邻域；树、克隆和胚胎命运结论都会继承相似度与建树的不确定性；HSC 总数是采样模型估计，不是直接计数。

以下缺口在严格检索后仍应写为 **Not found**，不能用推测补齐：

- `SUPP_MD` 不存在，Supplementary Table 1 的数据集参数未在本地获得；
- 论文谱系准确度 $Q$ 的精确代码 **Not found**；
- 支持度阈值 0.95 的论文特定克隆调用 **Not found**；
- 三只小鼠 HSC 克隆总数计算的论文特定脚本 **Not found**；
- 各论文数据集 bootstrap 中是否重新运行校正和细胞类型去除 **Not found**；
- 全数据笔记本读取外部处理数据和预计算相似度，缺少完整本地配置与原始数据执行链。

MethylTree 最重要的贡献，是把高度稀疏但积累快速的内源甲基化变化转换为可校正的细胞两两相似度，再以树、支持度和克隆结构表达谱系。它避免了遗传操纵，并能与细胞状态测量共存；但若要逐项复现论文的全部数值、克隆阈值和下游生物学分析，仍需要补充数据、配置以及对纸码差异的进一步澄清。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MethylTree

### What problem does it solve?

MethylTree is a computational framework for reconstructing single-cell lineage relationships from naturally accumulated DNA-methylation epimutations. It targets lineage tracing in humans and other settings where genetic barcoding is impossible or undesirable. The paper was published in *Nature Methods* in 2025 (DOI `10.1038/s41592-024-02567-1`).

Existing human lineage approaches have important tradeoffs. Whole-genome somatic-mutation studies such as Mitchell et al. (*Nature*, 2022) and Fabre et al. (*Nature*, 2022) require deeply sequenced single-cell-derived colonies, are expensive and provide limited cell-state information. Mitochondrial-mutation tracing, introduced for single-cell human lineage analysis by Ludwig et al. (*Cell*, 2019) and extended by Weng et al. (*Nature*, 2024), is higher throughput but can be confounded by mitochondrial inheritance, drift and selection. Both mutation classes accumulate far more slowly than CpG epimutations and therefore have limited ability to resolve lineage events separated by only days (`paper.md:21-30,535-543`; Extended Data Fig. 9).

### Core idea

CpG methylation changes at roughly $10^{-3}$ per site per cell division. MethylTree treats these frequent stochastic changes as endogenous lineage marks. It avoids imputing the extremely sparse single-cell methylation matrix. Instead, for each cell pair it computes Pearson correlation only across genomic regions observed in both cells, producing a cell–cell similarity matrix. It then:

1. corrects heterogeneous attenuation of correlations using per-cell factors $Z_i$;
2. optionally estimates and subtracts cell-type-specific methylation when phenotype dominates lineage;
3. rescales similarity and reconstructs a UPGMA tree;
4. estimates subtree support by resampling 80% of regions 100 times;
5. optionally calls methyl clones using tree support and within-subtree similarity;
6. generates lineage embeddings and downstream clone summaries.

Small or selected genomic regions are crucial. All individual CpGs are accurate but expensive; selected 500-bp bins, merged after pseudobulk methylation filtering, preserve lineage signal much better than conventional 100-kb bins (`paper.md:225-273,333-417`).

### Main evidence

The evaluation spans simulations, cell lines, cancer, fetal tissues, blood differentiation, embryos and native mouse HSCs.

- In seven-division simulations, MethylTree reconstructed the full 128-cell hierarchy at 5% and even 1% genomic coverage under the displayed conditions.
- In serially expanded HEK 293T cells, correlation-bias correction improved lineage accuracy from $Q=0.845$ to $Q=1$; H9 embryonic stem cells and a colorectal-cancer dataset also reached $Q=1$.
- In mixed fetal germ and gonadal somatic cells, raw similarity was dominated by cell type, whereas cell-type-aware transformation recovered fetus origin at $Q=1$.
- In mouse in vitro blood differentiation, all 52 multi-cell LARRY clones were recovered with $Q=1$; 48 inferred multi-cell methyl clones matched LARRY labels at adjusted rank index about 0.98 and covered 92% of cells.
- In a human cord-blood differentiation assay, 20 multi-cell LARRY clones were reconstructed at $Q=1$.
- Across early mouse and human embryo datasets, cells grouped by embryo origin with high accuracy. Within individual day-5/day-6 human embryos, inferred four-cell-stage branches showed variable enrichment for inner-cell-mass or trophectoderm fate, supporting a model of stochastic early commitment.
- In mouse HSCs, LL731 reached $Q=0.90$ and ARI about 0.87–0.88. Singleton-fraction simulations gave a consistent estimate of roughly 250 EHT-derived HSC clones across three mice, comparable to an editing-corrected DARLIN estimate of 312 (`paper.md:59-168`; Figs. 1–6).

The extended figures qualify the headline “near 100%” performance. Region choice and coverage matter, large bins fail, and the LL653E6 HSC dataset reached only $Q=0.68$ and ARI = 0.76. The evidence supports broad utility, but not uniformly exact reconstruction in every dataset.

### Reproducibility and code-paper match

**Reproducibility: 3/5. Code-paper fidelity: medium.**

The workspace contains versioned snapshots of the core MethylTree package, Bismark preprocessing scripts and paper-linked notebooks. The Python package has pinned dependencies, a tutorial notebook and direct implementations of sparse similarity, correction, cell-type subtraction, tree reconstruction, bootstrap support and simulation. Processed data are publicly referenced through GEO, GSA and Figshare (`paper.md:498-507`).

Important gaps remain:

- the all-dataset notebook loads prepared AnnData objects and precomputed similarities, so it is not a single raw-data-to-paper-figure workflow;
- external processed data, configuration and Supplementary Table 1 are not present locally;
- the exact paper equation for lineage accuracy $Q$ is **Not found** in the inspected code; the package reports different ordering metrics;
- the paper-specific methyl-clone call with support threshold 0.95 is **Not found**; code contains two divergent clone-calling routes;
- the released correction defaults/convergence, rescaling and embedding differ in documented ways from the Methods;
- a paper-specific script for the three-mouse HSC clone-number calculation is **Not found**, although a generic tutorial implementation exists.

### Limitations

MethylTree assumes that enough stable, lineage-informative epimutations remain after development and that per-cell correlation attenuation is well modeled by multiplicative factors. Cell-type subtraction requires phenotype labels or neighborhoods and enough cells/lineages to estimate a background. Informative-region selection is system-specific, low coverage produces failures, and methyl-clone or biological conclusions inherit uncertainty from the reconstructed tree. The embryo fate analysis is therefore an inference from reconstructed ancestral partitions, while the HSC total is a sampling-model estimate rather than a direct count.

Overall, MethylTree's strongest contribution is a practical similarity-based framework that converts sparse endogenous methylation variation into lineage structure without genetic manipulation, while remaining compatible with transcriptomic and chromatin-state readouts. Its empirical breadth is compelling; exact reproduction of every reported metric and clone call requires additional paper-specific artifacts and clarification of code-method differences.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
