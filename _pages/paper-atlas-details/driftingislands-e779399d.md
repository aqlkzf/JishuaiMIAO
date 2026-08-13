---
layout: default
permalink: /paper-atlas/driftingislands-e779399d/
title: "DriftingIslands"
nav: false
description: "这篇工作故意训练了一个只追求细胞类型分类的模型 Islander：它能在主流单细胞嵌入指标上拿到最高分，却把连续的生物状态切成彼此孤立、位置随随机运行漂移的“细胞岛”。作者据此说明现有指标不完整，并提出 scGraph，用跨批次稳定的细胞类型几何关系来补充评价。 > 重要定位：Islander 不是推荐用于生物发现的整合算法，而是一个用于“压力测试指标”的反例或 null algorithm。"
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
      <span>Representation Models</span>
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>DriftingIslands</h1>
    <p>Limitations of cell embedding metrics assessed using drifting islands</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Genentech/Islander" target="_blank" rel="noopener noreferrer" aria-label="Open code for DriftingIslands">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Drifting Islands：用“高分但错误”的嵌入检验单细胞评估指标

### 一句话理解

这篇工作故意训练了一个只追求细胞类型分类的模型 **Islander**：它能在主流单细胞嵌入指标上拿到最高分，却把连续的生物状态切成彼此孤立、位置随随机运行漂移的“细胞岛”。作者据此说明现有指标不完整，并提出 **scGraph**，用跨批次稳定的细胞类型几何关系来补充评价。

> 重要定位：Islander 不是推荐用于生物发现的整合算法，而是一个用于“压力测试指标”的反例或 null algorithm。

### 1. 论文要解决什么问题？

单细胞数据整合通常希望同时做到：

1. 去除测序平台、样本处理等技术批次效应；
2. 保留细胞类型、状态、发育轨迹等生物差异。

现有评估大多重点检查：

- 不同批次是否在嵌入空间中充分混合；
- 相同细胞类型是否聚在一起；
- 不同细胞类型是否容易区分。

这些检查本身合理，但没有充分约束“不同细胞类型之间应该如何排列”。因此，一个模型可以把每个细粒度标签压成纯净小岛，在上述指标上获得高分，同时破坏：

- 连续细胞状态；
- 发育时间梯度；
- 谱系层级；
- 不同亚型之间的相对邻近关系。

论文的核心问题是：**如果一个生物学上明显不合适的嵌入也能赢得基准测试，那么基准究竟漏掉了什么？**

### 2. 为什么现有方法和指标还不够？

论文主要挑战的是 Luecken 等人在 *Nature Methods*（2022）系统化使用的 scIB 式评估框架，而不是宣称所有整合算法本身都无效。

论文比较的代表方法包括：

| 类别 | 方法及论文给出的来源 |
|---|---|
| 降维 | PCA、tSNE、UMAP |
| 批次整合 | Harmony（*Nature Methods*, 2019）、Scanorama（*Nature Biotechnology*, 2019）、BBKNN（*Bioinformatics*, 2020）、fastMNN（*Nature Biotechnology*, 2018）、scVI（*Nature Methods*, 2018）、scANVI（*Molecular Systems Biology*, 2021）、scGen（*Nature Methods*, 2019）、scPoli（*Nature Methods*, 2023） |
| 单细胞基础模型 | Geneformer（*Nature*, 2023）、scGPT（*Nature Methods*, 2024） |

scIB 式指标分别衡量标签保持和批次校正，再组合成总体分数。问题在于：如果模型直接使用最细粒度标签进行监督，它就能主动制造指标最喜欢的几何形态，却不必保存标签之间的生物关系。

### 3. 整体计算框架

```text
原始表达矩阵 + 细胞类型标签 + 批次标签
  |
  |  质量控制：>=1,000 reads；>=500 detected genes；
  |             每个基因至少出现在5个细胞中
  v
每细胞归一化到10,000总计数，再做 log1p
  |
  +----------------------+---------------------------+
  |                      |                           |
  v                      v                           v
Islander              13种基线方法                原作者嵌入
gene -> 128 -> 16 -> C  降维/整合/基础模型          若数据提供
交叉熵 + mixup
  |                      |                           |
  +----------------------+---------------------------+
                         |
                         v
                 scIB式12项指标评估
                         |
                         v
            Islander得分最高，但形成漂移细胞岛
                         |
            +------------+----------------+
            |                             |
            v                             v
       生物学与图像检查                 scGraph
       连续结构是否被破坏               批次内PCA类型图
                                       -> 共识图
                                       -> 加权相关
            |                             |
            +--------------+--------------+
                           v
                 联合使用 scIB + scGraph
```

### 4. 输入、符号和输出

设数据包含 $n$ 个细胞、$p$ 个基因：

- $X\in\mathbb R^{n\times p}$：预处理后的表达矩阵；
- $y_i\in\{1,\ldots,C\}$：细胞 $i$ 的统一细胞类型标签；
- $b_i\in\{1,\ldots,B\}$：批次、供体或样本标签；
- $Z^{(m)}\in\mathbb R^{n\times d_m}$：方法 $m$ 产生的细胞嵌入。

两个核心输出是：

1. Islander 的 16 维嵌入，用来构造“高分反例”；
2. 每个候选嵌入的 scGraph 分数，范围为 $[-1,1]$，越高表示越接近跨批次 PCA 共识几何。

论文没有编号公式。下文公式是根据论文方法文字和已验证代码整理的计算表达，不应被误认为原文公式编号。

### 5. 数据预处理

论文和代码均采用：

- 删除 reads 少于 1,000 的细胞；
- 删除检测基因数少于 500 的细胞；
- 删除少于 5 个细胞表达的基因；
- 每个细胞总计数缩放到 10,000；
- 使用 `log1p`。

对细胞 $i$、基因 $g$：

$$
x'_{ig}=\log\left(1+10^4\frac{x_{ig}}{\sum_h x_{ih}}\right).
$$

该行为可在 `code/Islander/src/Utils_Handler.py:23-41` 直接验证。仓库没有附带处理后的 11 个 atlas 矩阵，因此这里只能确认处理逻辑，不能核对最终数值文件。

### 6. Islander：如何构造“指标喜欢”的嵌入

#### 6.1 网络结构

论文描述的分类路径为：

```text
p维基因表达
  -> 128维隐藏层（BatchNorm + ReLU）
  -> 16维最后隐藏层（作为嵌入）
  -> C维细胞类型分类输出
```

形式化表示为：

$$
h_i=\operatorname{Dropout}\!\left(\operatorname{ReLU}(\operatorname{BN}(W_1x_i+a_1))\right),
$$

$$
z_i=W_2h_i+a_2\in\mathbb R^{16},
$$

$$
p_i=\operatorname{softmax}(W_3z_i+a_3).
$$

代码中的默认配置可直接确认：

- `scripts/_Islander_MixUp.sh:3-29` 设置 `MLPSIZE="128 128"`、`LEAKAGE=16`、`MODE="mixup"`；
- `src/scModel.py:103-147` 把 16 维瓶颈插入两个 128 之间，并用线性 projector 输出细胞类型；
- `src/scBenchmarker.py:595-614` 调用 encoder 的 `extra_repr`，将其写入 `adata.obsm["Islander"]`。

代码类名是 `AE_Concept`，内部还包含 decoder。但默认 `w_rec=0`，所以重构损失不参与优化；有效训练目标仍是论文所述的监督分类器。代码还在第一隐藏层使用了 $p=0.1$ 的 dropout，这是论文未明确说明的实现细节。

#### 6.2 在嵌入空间做 mixup

论文只说明使用 mixup。代码进一步表明，插值发生在 16 维嵌入 $z$ 上，而不是原始表达 $x$ 上。

随机打乱同一 minibatch，令 $\pi$ 为置换，并采样：

$$
\lambda\sim\operatorname{Beta}(1,1),
$$

$$
\tilde z_i=\lambda z_i+(1-\lambda)z_{\pi(i)}.
$$

代码中的分类损失为：

$$
\mathcal L_{\mathrm{cls}}
=\operatorname{CE}(z_i,y_i)
+\lambda\operatorname{CE}(\tilde z_i,y_i)
+(1-\lambda)\operatorname{CE}(\tilde z_i,y_{\pi(i)}).
$$

默认总损失为：

$$
\mathcal L
=w_{\mathrm{rec}}\mathcal L_{\mathrm{MSE}}
+w_{\mathrm{cet}}\mathcal L_{\mathrm{cls}},
$$

其中 $w_{\mathrm{rec}}=0$、$w_{\mathrm{cet}}=1$（`src/scTrain.py:82-100,125-140`）。

#### 6.3 训练设置

论文给出的设置是：

- minibatch：256 个细胞；
- Adam；
- 初始学习率：0.001；
- 训练 10 个 epoch；
- cosine annealing 学习率衰减；
- 默认使用 mixup。

这些设置在 `src/scDataset.py:11`、`src/ArgParser.py:55-72`、`src/scTrain.py:102-140` 和官方 mixup 脚本中均可验证。

但是有一处重要差异：论文说“使用全部细胞训练，以最大化过拟合”，而默认 mixup 脚本没有启用 `train_and_test=True`。`scDataset` 通常会随机保留约 10% 的 256 细胞块作为测试集（`src/scDataset.py:27-29,158-205`）。因此，默认发布入口与论文文字并非完全一致。

#### 6.4 为什么它能骗过指标？

Islander 的监督目标只要求：

- 同标签细胞靠近；
- 不同标签易分；
- 每个标签岛内部混合不同批次。

这正好对应很多现有指标的奖励方向。可是损失中没有任何项规定：

- airway fibroblast 应该靠近哪类 fibroblast；
- 发育早期和晚期细胞应形成何种连续关系；
- 不同细胞类型岛之间的全局排列应在不同随机运行中保持一致。

因此会出现：**岛内结构稳定、岛间结构任意**。这就是“drifting islands”。

#### 6.5 半监督损失变体

论文还测试了 triplet loss 和 supervised contrastive loss（SCL）。仓库中两者均有直接实现：

$$
\mathcal L_{\mathrm{triplet}}
=\max\left(\lVert z_a-z_p\rVert_2^2-\lVert z_a-z_n\rVert_2^2+1,0\right).
$$

SCL 对两个批次中的嵌入做 L2 归一化，再按标签构造正负对（`src/scLoss.py:57-66,109-155`）。论文报告：两种变体仍可取得较高 scIB 分数，但其几何结构不同；SCL 更容易被 scGraph 识别为有问题，而 triplet 变体可能保留更合理的空间。

### 7. scGraph：比较细胞类型之间的几何关系

#### 7.1 直觉

scGraph 不再只问“同类细胞是否聚集”，而是问：

> 候选嵌入中，细胞类型 A、B、C 的相对距离关系，是否与多个批次中反复出现的原始生物结构一致？

论文称其为 affinity/proximity graph；本地实现实际保存的是经过归一化的欧氏**距离矩阵**。

#### 7.2 为每个批次构建参考图

对每个细胞数足够的批次 $b$：

1. 选择 1,000 个高变基因；
2. 在该批次内计算 10 维 PCA；
3. 对每种细胞类型，在每个 PCA 坐标维度两侧各裁剪 5% 后求均值；
4. 计算类型质心之间的欧氏距离；
5. 按每一列的最大值归一化。

对批次 $b$、类型 $c$：

$$
\mu^{\mathrm{PCA}}_{b,c}
=\operatorname{trimmean}_{0.05}\{u_i:b_i=b,y_i=c\},
$$

$$
D_b(c,c')
=\left\lVert\mu^{\mathrm{PCA}}_{b,c}-\mu^{\mathrm{PCA}}_{b,c'}\right\rVert_2.
$$

代码默认忽略少于 100 个细胞的批次，以及全局少于 10 个细胞的类型（`src/scGraph.py:5-59`）。

论文使用“PCA loadings”一词，但本地 `src/scGraph.py:48-59` 读取的是 `obsm["X_pca"]`，即每个细胞的 PCA 坐标/score，而不是基因 loading matrix。这里应视为术语或实现层面的 **Partial** 对应。

#### 7.3 聚合成跨批次共识图

对某一对细胞类型，只平均同时存在这两个类型的批次：

$$
D^*(c,c')
=\operatorname{mean}_{b:\,(c,c')\text{可用}}D_b(c,c').
$$

代码通过带缺失值的 DataFrame 合并和分组平均实现，因此不要求每个批次包含所有细胞类型（`src/scGraph.py:61-65`）。

#### 7.4 为候选嵌入构建图

对待评估的 $Z^{(m)}$，在全数据上按细胞类型计算同样的 5% trimmed centroid，再得到距离矩阵 $D^{(m)}$（`src/scGraph.py:106-114`）。

#### 7.5 用加权 Pearson 相关评分

对每个焦点类型 $c$，比较候选距离向量和参考距离向量。越近的参考邻居权重越大：

$$
w_{c,c'}
=\frac{1/D^*(c,c')}{\sum_{k\ne c}1/D^*(c,k)}.
$$

每个类型的得分为：

$$
r_c
=\operatorname{corr}_{w_c}\left(D^{(m)}(c,\cdot),D^*(c,\cdot)\right).
$$

最终 scGraph 分数为：

$$
S_{\mathrm{scGraph}}^{(m)}
=\frac{1}{|C|}\sum_{c\in C}r_c.
$$

代码中的输出列名为 `Corr-Weighted`（`src/scGraph.py:84-138`）。它强调近邻关系，同时降低远距离类型的影响。

### 8. 实验如何证明指标存在问题？

#### 数据与基线

- 11 个 human cell atlas；
- 共 3,510,450 个细胞；
- 覆盖 10 个器官系统；
- 13 个基线方法；
- scIB 式 12 项指标；
- 可用时还比较原论文作者提供的整合嵌入。

#### 主要结果

1. **Islander 在全部 11 个 atlas 上都获得最高的标准化总体分数。**
2. 在 fetal lung 中，原作者嵌入保留 fibroblast 亚型连续体，Islander 则把它们切成完全分离的岛。
3. 三次 Islander 运行的总体分数相近，但 airway fibroblast 的最近邻组成明显不同，说明岛间位置具有任意性。
4. 使用较粗的 14 类标签时，Islander 得分降为 0.523，低于 PCA 的 0.557 和 scVI 的 0.701。
5. scGraph 对排名进行了明显重排：fetal lung 中 BBKNN 最高，Islander 接近零。
6. 在只含 31,020 个 fibroblast、9 个亚型、29 个批次的分析中，Islander 的 scIB 最高，但 scGraph 最低且略低于零。

这组结果说明：**细粒度标签分得越干净，不等于更好地保留了生物结构。**

### 9. 四张图应该怎么看？

- **主图 Fig. 1：** b、c 显示 Islander 在旧指标上全面领先；d、f、g 显示连续 fibroblast 和发育结构被拆散；e 显示不同运行的邻居漂移；i 显示 scGraph 将 Islander 判为接近零。
- **Extended Data Fig. 1：** 三次运行都有纯净岛，但大岛之间的相对位置明显改变，是“drifting”最直观的图像证据。
- **Extended Data Fig. 2：** 直接以全局 log1p counts 为参考不能有效识别 Islander；trim-rate 消融支持两侧各裁剪 5% 的稳健质心设计。
- **Extended Data Fig. 3：** 同一 fibroblast 子集上，scIB 排名把 Islander 放第一，scGraph 排名把它放最后；这是两类指标互补性的最清楚展示。

### 10. scIB 和 scGraph 应该如何联合使用？

| 数据场景 | 更应关注 | 原因 |
|---|---|---|
| 批次主要是技术噪声 | scIB | 批次混合是合理目标。 |
| 批次对应发育阶段、条件或真实生物差异 | scGraph + 生物学检查 | 过度混合可能消除真实结构。 |
| 技术与生物变化同时存在 | 两者联合 | 两个指标的分歧本身就是诊断信号。 |

论文指出，scGraph 差异约 0.05–0.1 可能有意义，但不存在跨数据集通用的“合格阈值”。

### 11. 方法局限

论文明确承认：

- scGraph 可能偏爱高维、PCA-like 嵌入；
- 它比较细胞类型质心，不是单细胞级局部结构；
- 它假设功能相似类型应在欧氏空间中相近；
- scIB 和 scGraph 都依赖统一标签；
- PCA 共识可能偏向 PCA 或受原作者注释影响的嵌入；
- scGraph 的绝对值依赖具体数据集。

### 12. 代码—论文一致性与可复现性

#### 已验证的 Exact 行为

- 官方 mixup 配置为 128 → 16 → cell types；
- 默认 `mode=mixup`、Adam、0.001、10 epochs、cosine scheduler；
- mixup 在 16 维嵌入空间中完成；
- preprocessing 阈值和归一化与论文一致；
- triplet、SCL 和 scGraph 加权相关均有直接源码。

#### Partial 或缺失

- 默认 mixup 脚本没有使用全部细胞训练；
- scGraph 源码使用 PCA cell scores，而论文写作 PCA loadings；
- 精确复现论文 12 项指标归一化总体分数的专用配置未找到；
- 仓库没有处理后的 atlas、训练 checkpoint；
- README 提到的 `Fibroblast_Case.ipynb` 和 `Geneformer_Skin.ipynb` 在该 commit 中 **Not found**；
- 没有找到自动化测试；
- `--seed` 被解析，但没有传入负责随机切分的 `scDataset` 路径。

综合判断：代码—论文匹配度为 **medium**，可复现性约 **3/5**。核心思想和主要实现可以核对，但完整重建论文所有图表仍需要外部数据、缺失 notebook 或额外配置。

### 13. 最值得记住的研究方法论

这篇论文的价值不只是增加一个指标，而是给出了一个很实用的评估原则：

> 设计基准时，应主动构造能够“钻指标空子”的反例；如果一个明显不合理的方法仍能高分，说明评估目标没有覆盖真正关心的科学结构。

Islander 负责暴露漏洞，scGraph 负责补充“类型之间的几何关系”，最终仍需与 scIB、图像检查和领域知识共同解释。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Limitations of Cell Embedding Metrics Assessed Using Drifting Islands

**Wang, Leskovec and Regev — Nature Biotechnology 44, 574–577 (2026; online 2025), DOI `10.1038/s41587-025-02702-z`.**

### One-sentence takeaway

A deliberately overfit, label-supervised network called **Islander** beats leading single-cell embedding methods on established scIB-style metrics while producing biologically misleading, run-dependent cell islands; the authors introduce **scGraph** to measure preservation of higher-order cell-type geometry and expose this failure mode.

### Problem

Single-cell integration is commonly evaluated through two lenses: whether batches mix and whether cells sharing an annotation remain close. Those criteria are useful, but incomplete. A model can optimize label separation and batch mixing without preserving trajectories, continua or meaningful relationships among different cell types.

The paper turns this concern into an explicit stress test: can a biologically poor embedding win the benchmark?

### Why existing evaluation is insufficient

The central target is the scIB-style benchmark introduced by Luecken et al. in *Nature Methods* (2022), which combines biological-conservation and batch-correction metrics. The paper compares against a broad set of methods whose own goals differ:

| Family | Named examples and source venue/year |
|---|---|
| Dimensionality reduction | PCA, tSNE, UMAP |
| Batch integration | Harmony (*Nature Methods*, 2019); Scanorama (*Nature Biotechnology*, 2019); BBKNN (*Bioinformatics*, 2020); fastMNN (*Nature Biotechnology*, 2018); scVI (*Nature Methods*, 2018); scANVI (*Molecular Systems Biology*, 2021); scGen (*Nature Methods*, 2019); scPoli (*Nature Methods*, 2023) |
| Foundation models | Geneformer (*Nature*, 2023); scGPT (*Nature Methods*, 2024) |

These methods are not all defective; rather, the benchmark can be gamed by a method designed around its observable targets. Fine annotation purity does not guarantee that distances between annotations remain meaningful.

### Proposed approach

#### Islander: a null integration algorithm

Islander maps normalized gene expression through a 128-unit hidden layer to a 16-dimensional embedding and then predicts the annotated cell type. It is trained with cross-entropy and mixup, Adam at 0.001 for ten epochs, and cosine learning-rate decay.

Because the model directly optimizes cell-type classification, each label becomes a compact, batch-mixed island. This is exactly what many established metrics reward. But the loss does not determine how different islands should be arranged, so their neighborhoods drift across runs and continuous biological structures are fragmented.

#### scGraph: a complementary geometry score

scGraph builds a reference cell-type distance graph from batch-wise PCA representations:

1. compute robust, 5%-per-side trimmed centroids for cell types within each batch;
2. convert centroid distances into normalized batch graphs;
3. average available relationships into a consensus graph;
4. construct the same centroid-distance graph for a candidate embedding;
5. compare candidate and consensus relationships with inverse-distance-weighted Pearson correlation, emphasizing close neighbors.

The result ranges from −1 to 1, with higher values indicating better preservation of the consensus cell-type geometry. scGraph is meant to complement, not replace, scIB.

### Evaluation and main results

- **Scale:** 11 human cell atlases, 3,510,450 cells, ten organ systems.
- **Comparators:** 13 baseline methods plus original authors' embeddings when available.
- **Established benchmark:** 12 biological-conservation and batch-correction metrics.
- **Metric stress test:** Islander achieved the best normalized overall score across all 11 atlases.
- **Biological failure:** fetal-lung fibroblast continua and developmental organization became disconnected islands; airway-fibroblast nearest neighbors changed strongly across three runs.
- **Coarse-label check:** with 14 broad fetal-lung annotations, Islander scored 0.523, below PCA at 0.557 and scVI at 0.701.
- **scGraph:** rankings changed substantially. On fetal lung, BBKNN ranked highest, while Islander runs scored near zero. In the fibroblast-only analysis, Islander ranked first by scIB but last, slightly below zero, by scGraph.

Together, the results show that high label coherence and batch mixing can coexist with lost developmental structure and arbitrary inter-cluster geometry.

### How to interpret scIB and scGraph

- When batches primarily represent technical noise, scIB's preference for mixing is valuable.
- When batches encode developmental stages, conditions or other biological differences, scGraph can reveal overcorrection and loss of structure.
- Disagreement between the metrics is a diagnostic signal requiring biological inspection, not proof that one metric is universally correct.

### Limitations

- scGraph favors higher-dimensional and PCA-like embeddings because its reference is PCA-derived.
- It evaluates cell-type centroids rather than single-cell neighborhoods.
- It assumes biologically similar types should be geometrically close.
- It requires harmonized labels and Euclidean embedding geometry.
- Scores are dataset dependent; there is no universal “good” threshold.
- The local implementation uses PCA cell coordinates, although the paper describes PCA “loadings.”

### Reproducibility assessment: **3/5**

**Strengths:** the official GitHub snapshot is available at commit `26782db...`; it includes a pinned environment, direct mixup/SCL/triplet scripts, preprocessing and model source, local scGraph code, metadata maps, two notebooks, logs and one stored scGraph result. The key 128→16 configuration and default mixup path are directly verifiable.

**Gaps:** processed atlas matrices and trained checkpoints are not bundled; the README-listed `Fibroblast_Case.ipynb` and `Geneformer_Skin.ipynb` are absent; no automated tests were found; and the exact paper-specific normalized aggregation over 12 scIB metrics is not isolated in a dedicated configuration. The released mixup script also keeps a default test split despite the paper's statement that all cells were used for training.

**Code-paper match:** **medium**. The core Islander and scGraph mechanisms are present and readable, but complete figure regeneration is not self-contained and several implementation details differ from or extend the paper description.

### Bottom line

The paper's durable contribution is methodological skepticism: an embedding benchmark must test more than annotation purity and batch mixing. Islander is useful precisely because it is a bad biological integration method that looks excellent to incomplete metrics. scGraph adds a second view—preservation of inter-type geometry—and the paper argues that both views, combined with biological inspection, are necessary.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
