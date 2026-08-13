---
layout: default
permalink: /paper-atlas/m3g-d98efd81/
title: "M3G"
nav: false
wide: true
description: "M3G（Multi-Marginal Matching Gap）不再把 k\\geq3 个视图拆成许多两两对比，而是问：已知的正确 k 元组配对，与在当前表示空间里通过多边际最优传输找到的最佳重新配对，二者的代价还差多少？ 差距越大，说明编码器把某些错误组合做得比真实组合更紧；最小化这个差距，就迫使同一对象的全部视图作为一个整体变得一致。"
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
      <span>PMLR · 2024</span>
    </div>
    <h1>M3G</h1>
    <p>Contrasting Multiple Representations with the Multi-Marginal Matching Gap</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2405.19532" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for M3G">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/mlrapp/m3g" target="_blank" rel="noopener noreferrer" aria-label="Open code for M3G">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## M3G：用多边际匹配差距同时对齐多个视图

### 一句话抓住核心

M3G（Multi-Marginal Matching Gap）不再把 $k\geq3$ 个视图拆成许多两两对比，而是问：**已知的正确 $k$ 元组配对，与在当前表示空间里通过多边际最优传输找到的最佳重新配对，二者的代价还差多少？** 差距越大，说明编码器把某些错误组合做得比真实组合更紧；最小化这个差距，就迫使同一对象的全部视图作为一个整体变得一致。

### 1. 论文要解决什么问题

设一个 minibatch 有 $n$ 个对象，每个对象有 $k$ 个视图。视图可以是同一图像的不同数据增强，也可以是 DomainNet 的不同视觉域，或 EEG 的六个通道。编码器把它们变成单位球面上的向量：

$$
\mathcal X=[\mathbf x_i^\ell]_{\ell,i}\in\mathbb R^{k\times n\times d},
\qquad \|\mathbf x_i^\ell\|=1.
$$

传统 InfoNCE、BYOL 等损失最初面向两个视图。扩到 $k$ 个视图时，常见做法有两种：

- pairwise extension：计算 $k(k-1)/2$ 个两两损失再平均；
- one-vs-average-of-rest：把其余 $k-1$ 个表示先求平均，再与当前视图比较。

前者只看局部配对，后者在比较前就压缩了其余视图。两者都没有直接评价“同一对象的 $k$ 个表示作为一个整体是否比任何错误组合更一致”。M3G 的新意正是把这个整体问题写成多边际最优传输（MM-OT）的 optimality gap。

### 2. 从二维匹配推广到 $k$ 维多匹配

普通最优传输用一个 $n\times n$ 双随机矩阵描述两个集合之间的软匹配。M3G 把它推广为含 $n^k$ 个元素的 $k$ 维张量 $\mathcal P$。它的每个一维边缘都必须是均匀分布：

$$
\mathcal B_{n,k}=\left\{\mathcal P\geq0:\
\mathrm m_\ell(\mathcal P)=\frac{\mathbf1_n}{n},\ \forall\ell\leq k\right\}.
$$

$\mathcal P_{i_1,\ldots,i_k}$ 表示把第一个视图中的对象 $i_1$、第二个视图中的对象 $i_2$，一直到第 $k$ 个视图中的对象 $i_k$ 组成一个软 $k$ 元组的权重。

训练数据已经给出正确配对：同一索引 $i$ 的所有视图属于同一对象。因此 ground-truth polymatching 是对角张量 $\mathcal J_{n,k}$，仅在 $i_1=\cdots=i_k$ 时取 $1/n$。

### 3. 先把表示变成 $n^k$ 个候选组合的代价

多元代价函数 $c$ 衡量一个 $k$ 元组有多分散。论文默认使用 circular variance：

$$
c_{\mathrm{cv}}(\mathbf z_1,\ldots,\mathbf z_k)
=1-R^2(\mathbf z_1,\ldots,\mathbf z_k),
\qquad
R^2=\left\|\frac1k\sum_{\ell=1}^k\mathbf z_\ell\right\|^2.
$$

同一方向的单位向量平均后长度接近 1，代价接近 0；方向分散时，平均向量缩短，代价增大。把每个视图中任选一个样本的所有组合都计算一遍，得到

$$
[\mathcal M_c(\mathcal X)]_{i_1,\ldots,i_k}
=c(\mathbf x_{i_1}^1,\ldots,\mathbf x_{i_k}^k)
=\mathcal C_{i_1,\ldots,i_k}.
$$

这里的关键代价也是主要瓶颈：$\mathcal C$ 有 $n^k$ 个元素。论文 Algorithm 2 利用单位向量间的两两距离矩阵，通过 broadcast/expand 组装 circular-variance cost tensor，避免逐个 $k$ 元组重复做 $d$ 维运算，但并没有消除 $n^k$ 的存储与张量运算。

需要特别注意：本地 OCR 对 $R^2$ 的两两距离系数识别不可靠，而 PDF 中该式与 Algorithm 2 的缩放写法也不宜在没有官方实现时自行“修正”。本解读保留论文正式定义和 Algorithm 2 的操作边界，不把推导猜测写成代码事实。

### 4. MM-Sinkhorn 找到当前表示下的最佳重新组合

给定 $\mathcal C$，熵正则多边际 OT 求解

$$
\mathrm{OT}_{k,\varepsilon}(\mathcal C)
=\min_{\mathcal P\in\mathcal B_{n,k}}
\langle\mathcal P,\mathcal C\rangle
+\varepsilon\langle\mathcal P,\log\mathcal P-1\rangle.
$$

Algorithm 1 用 $n\times k$ 个对偶变量 $\mathbf F=(\mathbf f^1,\ldots,\mathbf f^k)$ 做循环更新。每次用 log-sum-exp 调整一个视图的势函数，使对应边缘靠近 $\mathbf1_n/n$；随后恢复

$$
\mathcal P=\exp\!\left((\bigoplus\mathbf F-\mathcal C)/\varepsilon\right),
$$

并在所有边缘的 $L_1$ 误差之和低于 $\alpha=10^{-3}$ 时停止。输出既包括最优软多匹配 $\mathcal P_\varepsilon(\mathcal C)$，也包括对应的正则化 OT 目标值。

$\varepsilon$ 控制匹配的平滑程度：较小值更接近硬匹配，但通常需要更多迭代；论文实验发现归一化表示下 $\varepsilon=0.2$ 在 ImageNet-1k 上较稳健。

### 5. M3G 损失到底比较什么

论文 Definition 3.1 为

$$
\mathrm{M3G}_{c,\varepsilon}(\mathcal X)
=\langle\mathcal J_{n,k},\mathcal M_c(\mathcal X)\rangle
+\varepsilon\log n
-\mathrm{OT}_{k,\varepsilon}(\mathcal M_c(\mathcal X)).
$$

左边第一项是已知正确 $k$ 元组的代价；最后一项是允许任意重新组合时能达到的最佳代价。直观上：

- gap 大：当前表示空间中存在比真实配对更紧的错误 $k$ 元组；
- gap 小：真实配对已经接近最优多匹配；
- gap 为 0：ground-truth matching 达到该正则化问题的最优值。

Figure 1 用四种颜色表示四个对象、三种形状表示三个视图。开始时，彩色真实配对边界与灰色最优配对边界不同；梯度推动点移动，最终二者的目标值一致。图展示的是损失几何直觉，不是实际训练只需两步收敛。

### 6. 为什么不需要反向传播穿过 Sinkhorn 迭代

M3G 是 Fenchel–Young 型 optimality gap。Proposition 3.2 给出

$$
\nabla\mathrm{M3G}(\mathcal X)
=\partial\mathcal M(\mathcal X)^*
\left[\mathcal J_{n,k}
-\mathcal P_\varepsilon(\mathcal M(\mathcal X))\right].
$$

梯度信号是“真实多匹配减去当前最优软多匹配”，再通过 cost-tensor operator 的 vector–Jacobian product 传回表示。Danskin 定理允许把求解器输出当作最优解使用，不需要对每一次 MM-Sinkhorn 更新做反向传播。准确表述是：**仍需一次 MM-Sinkhorn 前向求解，也仍需通过代价张量构造反传；省掉的是穿过求解器迭代本身的 backward。**

### 7. 完整训练数据流

```text
n 个对象，每个对象 k 个视图/模态
        │
        ▼
编码器与投影头 → 单位归一化表示 X [k,n,d]
        │
        ▼
多元代价 c → cost tensor C [n,...,n]，共 n^k 项
        │
        ├── J[n,k]：数据给出的真实对角多匹配
        │
        └── MM-Sinkhorn(C, ε)：最优软多匹配 Pε 与 OT 值
                    │
                    ▼
M3G = 真实配对目标 − 最优配对目标
                    │
                    ▼
J − Pε 经 cost operator 的 VJP → 更新编码器
```

ImageNet-1k 和 DomainNet 使用 joint-embedding student–teacher 框架：$k-1$ 个视图走 student，另一个走 EMA teacher；视觉骨干为 ViT-B/16，projection/predictor head 使用 4096 维线性层、GeLU 和 256 维输出。EEG 则把六个通道作为自然视图，复用 Brusch 等人的卷积编码器实验设置。

### 8. 实验支持了哪些结论

#### ImageNet-1k

在 $k=2,3,4$ 的线性评估中，M3G 分别得到 74.75、75.61、75.75 top-1 accuracy。相对最强基线的优势为 0.13、0.25、0.49 个百分点，趋势随 $k$ 墦大，但绝对增益较小，不能把它描述成数量级提升。

#### DomainNet

训练时用五个域、把第六个域留作 unseen domain。Table 2 中 M3G 在六种 leave-one-domain-out 设置均为最高；Figure 2 的单域线性分类器跨域评估中，M3G 总平均 rank 为 1.4，InfoNCE average-of-rest 为 1.7，BYOL average-of-rest 为 2.9。图像证据支持 M3G 的整体排名优势，但不同域对之间仍有明显难度差异。

#### EEG

六个通道对应 $k=6$。在每类 10、50、100、1000 个标注样本时，M3G/InfoNCE-pairwise 准确率分别为 36.6/35.5、49.2/49.3、56.1/52.2、64.6/56.3。这里 M3G 的 batch size 为 16，基线为 64，且只比较了一个基线，因此结果有支持力但覆盖有限。

#### 稳健性与开销

Figure 3 显示 $\varepsilon=0.2$ 后不同 $k$ 的准确率大致稳定。Table 4 中 circular variance 与 circular standard deviation 在 $k=3,4$ 几乎相同。Figure 4 的实图显示训练 300 epochs、4×8 A100 时，M3G 约为 17、22、29 小时，对应基线约为 16、20–21、25 小时；这是约 5%–16% 的墙钟时间增量，而不是 1.4–2 倍。

### 9. 可复现性与真实代码边界

论文附录给出 MM-Sinkhorn、cost tensor、数据增强和主要超参数，算法描述较完整。

- 官方 `mlrapp/m3g` 当前仓库只含项目网页、README 和静态资源；网页 Code 链接仍是被注释掉的模板占位；
- `Multiview_TS_SSL` 是论文明确复用的 Brusch et al. EEG 基线代码快照，可验证数据加载器、卷积编码器和 pairwise/COCOA 等基线，但搜索不到 M3G、multi-marginal Sinkhorn 或 matching-gap 实现；
- ImageNet/DomainNet 训练脚本、MM-Sinkhorn PyTorch 实现、M3G loss 与官方环境版本均 Not found。

所以这个工作区应按 `paper-only` 阅读。可以依据论文重建算法，但不能声称本地代码与 Eq. 14 或 Algorithms 1–2 Exact 对齐，也不能用 EEG 上游代码替代缺失的核心实现。

### 10. 研究者应带走的判断

M3G 的概念贡献很清晰：把多视图一致性从“许多局部相似度”提升为“真实联合配对相对全局最优联合配对的差距”。它的梯度也有漂亮的结构，并避免穿过 Sinkhorn 迭代反传。代价同样明确：$n^k$ 张量使 batch size 与视图数互相制约；实验证明小 $k$ 下可运行，却没有解决大规模多模态场景的指数扩展问题。缺少官方实现进一步限制了复现与数值细节核验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## M3G (Multi-Marginal Matching Gap) — Paper Summary

### Paper Information

- **Title**: Contrasting Multiple Representations with the Multi-Marginal Matching Gap
- **Authors**: Zoe Piran, Michal Klein, James Thornton, Marco Cuturi
- **Venue**: ICML 2024 (Proceedings of the 41st International Conference on Machine Learning)
- **arXiv**: 2405.19532
- **Code**: M3G implementation Not found. The official repository currently contains only the project website; the local `Multiview_TS_SSL/` snapshot is an upstream EEG baseline, not M3G code.

### Motivation & Novelty

#### The Problem

Modern representation learning increasingly uses more than two views or modalities of the same object. Self-supervised learning employs multiple augmentations ($k \geq 3$) of images to improve representations. Multimodal learning combines images, text, sketches, and other modalities simultaneously. However, all existing contrastive losses (InfoNCE, Chen et al., ICML 2020; BYOL, Grill et al., NeurIPS 2020) were designed for exactly two views. When extended to $k \geq 3$, practitioners resort to:

1. **Pairwise sum**: Averaging all $\frac{1}{2}k(k-1)$ pairwise losses (Bachman et al., NeurIPS 2019; Tian et al., ECCV 2020) — ignores the joint structure of $k$-tuples.
2. **One-vs-rest averaging**: Comparing each view to the mean of remaining views (Pototzky et al., DAGM 2022; Liang et al., ICLR 2024) — collapses information before comparison.

Both approaches decompose the multiview problem into pairs, losing the holistic view of whether all $k$ representations of the same object are simultaneously coherent.

#### Limitations of Existing Approaches

- **Pairwise decomposition** treats each pair independently, missing correlations among $k$-tuples. If views 1-2 are close and 2-3 are close, this says nothing about the joint coherence of (1, 2, 3).
- **Averaging** reduces $k-1$ views to a single centroid before comparison, discarding the distributional structure of the embedding set.
- Neither approach leverages the combinatorial structure of $k$-tuples for contrasting positive vs. negative arrangements.

#### Unique Contributions

M3G introduces the **first contrastive loss that operates holistically on $k$-tuples** without reducing to pairwise comparisons. Key innovations:

1. **Multi-marginal optimal transport as contrastive mechanism**: Uses MM-OT to find the optimal rearrangement of $nk$ embeddings into $n$ groups of $k$, then contrasts this against the known ground-truth grouping.

2. **Fenchel-Young loss structure**: M3G is defined as an optimality gap, which means:
   - Non-negativity is guaranteed (the ground-truth can never beat the optimal matching)
   - The gradient requires only a forward pass through MM-Sinkhorn (Danskin's theorem) — no backpropagation through the solver iterations

3. **Flexible multiway cost**: The circular variance cost $c_\text{cv}$ measures dispersion of $k$ points on the unit sphere, with an efficient pairwise distance reformulation (Algorithm 2).

4. **Principled generalization**: For $k=2$, M3G recovers a meaningful OT-based loss distinct from InfoNCE, providing an alternative even for the bipartite case.

### Method Overview

M3G takes a batch of $n$ objects, each with $k$ views/modalities encoded as $d$-dimensional vectors on the unit sphere. The loss measures:

$$\text{M3G}_{c,\varepsilon}(\mathcal{X}) = \underbrace{\langle \mathcal{J}_{n,k}, \mathcal{M}_c(\mathcal{X}) \rangle}_{\text{ground-truth cost}} + \varepsilon \log n - \underbrace{\text{OT}_{k,\varepsilon}(\mathcal{M}_c(\mathcal{X}))}_{\text{optimal matching cost}}$$

- **Ground-truth cost**: Average circular variance of each object's own $k$ views.
- **Optimal matching cost**: The minimum-cost arrangement of all $nk$ embeddings into $n$ groups of $k$, found by the multi-marginal Sinkhorn algorithm.
- **Gap = 0**: The encoder already produces representations where each object's views form the tightest clusters.

The MM-Sinkhorn algorithm (Algorithm 1) iteratively projects onto polystochastic constraints, operating on an $n^k$-sized cost tensor. The gradient flows through the cost tensor construction but not through the Sinkhorn solver itself.

**Architecture**: Joint embedding student-teacher framework (ViT-B/16 encoder, MLP projector). The student processes $k-1$ views; the teacher (EMA of student) processes 1 view.

**Hyperparameters**: Only two — the multiway cost function $c$ (default: circular variance) and the entropic regularization $\varepsilon$ (default: 0.2, robust to perturbation).

See `doc_method.md` for the mathematical development, algorithm walkthrough, and explicit code-availability boundary.

### Evaluation

#### Datasets

| Dataset | Task | k | n | Metric | Details |
|---------|------|---|---|--------|---------|
| ImageNet-1k (Deng et al., CVPR 2009) | Multiview SSL | 2, 3, 4 | 64/GPU | Top-1 linear acc | 300 epochs, 5 seeds |
| DomainNet (Peng et al., ICCV 2019) | Multimodal DA | 5 | 16/GPU | Top-1 linear acc (unseen domain) | 569K images, 345 classes, 6 domains |
| PhysioNet EEG (Goldberger et al., 2000) | Multichannel SSL | 6 | 16 | Classification acc | 994 subjects, 5 sleep stages |

#### Baselines

All baselines use the same architecture; only the loss differs:
- **BYOL_pwe** / **BYOL_ave**: BYOL loss (Grill et al., NeurIPS 2020) with pairwise sum / one-vs-rest
- **InfoNCE_pwe** / **InfoNCE_ave**: InfoNCE loss (Oord et al., 2018; Chen et al., ICML 2020) with pairwise sum / one-vs-rest

#### Key Results

**ImageNet-1k** (Table 1): M3G consistently outperforms all multiview extensions:
- $k=2$: 74.75% (M3G) vs 74.62% (BYOL_ave) — +0.13%
- $k=3$: 75.61% (M3G) vs 75.36% (InfoNCE_pwe) — +0.25%
- $k=4$: 75.75% (M3G) vs 75.26% (InfoNCE_pwe) — +0.49%

The gap *increases* with $k$, validating that the holistic multiview approach becomes more valuable as more views are added.

**DomainNet** (Table 2): M3G ranked 1st on all 6 domain adaptation tasks:
- Mean improvement of 3.1% over 2nd best (InfoNCE_ave)
- Largest gain on clipart domain: 32.4% (M3G) vs 24.1% (BYOL_ave) — +8.3%
- The pwe baselines perform much worse here ($\varepsilon = 0.05$ for DomainNet)

**EEG** (Table 3): With $k=6$ natural channels:
- At $s=1000$ samples/class: 64.6% (M3G) vs 56.3% (InfoNCE_pwe) — +8.3%
- Benefits most with more training data

#### Ablation Studies

- **Entropic regularization $\varepsilon$** (Fig. 3): Performance robust across $\varepsilon \in [0.05, 1.0]$; $\varepsilon = 0.2$ is consistently good.
- **Cost function** (Table 4): Circular variance ($c_\text{cv}$) and circular standard deviation ($c_\text{csd}$) yield similar results. $c_\text{cv}$ used as default.
- **Compute overhead** (Fig. 4): approximately 5–16% additional wall-clock time over the plotted pairwise baselines on ImageNet (4 nodes × 8 A100 GPUs), increasing with $k$.

### Reproducibility

#### Rating: 2/5

**Justification**: While the paper provides extensive implementation details (full hyperparameters in Table A1, pseudocode for augmentations, algorithmic details for MM-Sinkhorn), the absence of released code is a critical barrier. The MM-Sinkhorn implementation requires careful handling of $n^k$ tensor operations, numerical stability in log-space, and efficient GPU memory management. Reproducing the student-teacher architecture with the M3G loss from scratch requires significant engineering effort.

#### Strengths

1. **Complete algorithmic specification**: Algorithms 1 (MM-Sinkhorn) and 2 (cost tensor) are fully specified with pseudocode
2. **Comprehensive hyperparameters**: Table A1 lists all training details; augmentation pipelines are given as pseudocode
3. **Statistical rigor**: 5 independent seeds for ImageNet, 4 for DomainNet; mean and std reported
4. **Theoretical grounding**: M3G properties (non-negativity, gradient form) are mathematically proven
5. **Ablation studies**: ε sensitivity and cost function robustness explored

#### Weaknesses

1. **No M3G code found**: A live check of the official repository found only `README.md`, `index.html`, and static website assets; its inactive Code link still has an unconfigured template target. This is the primary reproducibility barrier.
2. **Large compute requirements**: 4 nodes × 8 A100 GPUs for ImageNet experiments (Fig. 4). Not accessible to most researchers.
3. **Scalability limitation**: The $O(n^k)$ tensor complexity inherently limits batch sizes and number of views. The paper demonstrates only $k \leq 6$ with $n \leq 128$.
4. **Modest improvements on ImageNet**: The gains on ImageNet (+0.13% to +0.49%) are within noise range for some comparisons, though DomainNet and EEG show more substantial differences.
5. **Missing comparisons**: Poly-View Contrastive Learning (Shidani et al., ICLR 2024) is cited but not compared to — it also addresses multiview contrastive learning with a different aggregation strategy. The concurrent work by Liang et al. (ICLR 2024) is also only cited, not benchmarked.
6. **EEG experiment limited**: Only compared to InfoNCE_pwe on EEG; missing BYOL baselines, the ave aggregation strategy, and the COCOA loss (available in the Brusch et al. codebase).
7. **Formula-to-implementation check unavailable**: The OCR rendering of the pairwise-distance coefficient is unreliable, while the PDF and Algorithm 2 expose a scaling that cannot be reconciled against released source. The analysis therefore preserves the printed definitions and does not claim an implementation-level equivalence.

#### Practical Notes

- **Environment**: PyTorch with multi-GPU training (DDP). Exact library versions not specified.
- **Data**: ImageNet-1k and DomainNet are standard benchmarks. PhysioNet EEG data is publicly available. The EEG codebase (Brusch et al., 2023) is available at github.com/theabrusch/Multiview_TS_SSL.
- **Key parameter**: $\varepsilon = 0.2$ for ImageNet/EEG, $\varepsilon = 0.05$ for DomainNet. The paper suggests $\varepsilon$ should scale with batch size.
- **Memory bottleneck**: The $n^k$ cost tensor is the limiting factor. For $n=64, k=4$: ~67 MB per tensor. For $k=6, n=16$: also ~67 MB.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
