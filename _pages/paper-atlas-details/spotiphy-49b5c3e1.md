---
layout: default
permalink: /paper-atlas/spotiphy-49b5c3e1/
title: "Spotiphy"
nav: false
description: "可以把一个 spot 想成一碗混合汤： scRNA 参考告诉我们每种“原料”通常是什么味道； spot 表达告诉我们整碗汤里有哪些分子、各有多少； H&E 图像告诉我们碗里大约有几颗“细胞”； Spotiphy 先估计每种细胞类型贡献了多少分子，再把每个基因的 spot 计数按这些贡献拆开，最后把拆出的类型标签随机放到图像中的细胞核上。 因此，输出是受约束的推断，不是对每个真实细胞重新测序。"
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Spotiphy</h1>
    <p>Spotiphy enables single-cell spatial whole transcriptomics across an entire section</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/jyyulab/Spotiphy" target="_blank" rel="noopener noreferrer" aria-label="Open code for Spotiphy">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Spotiphy 方法详解

### 1. 它想解决什么问题？

空间转录组长期存在一个“覆盖度—分辨率”矛盾：

- Visium、DBiT-seq 等测序型技术能在整张组织切片上测到成千上万个基因，但每个 capture spot 往往混合多枚细胞，而且 spot 之间的非捕获区域没有表达读数。
- Xenium、CosMx、MERFISH 等成像型技术可以定位单细胞，却通常只测预先选择的几百到约一千个基因。

Spotiphy 的目标不是创造新的测量，而是把三种已有信息拼起来：

1. spot 级空间表达；
2. 已标注细胞类型的 scRNA-seq 参考；
3. H&E 图像中的细胞核位置。

最终输出每个 spot 的细胞类型比例、推断的单细胞表达谱（iscRNA）以及覆盖整张切片的伪单细胞图像。

### 2. 为什么已有方法还不够？

论文把已有方法大致分成几类：

- Cell2location（*Nature Biotechnology*, 2022）和 RCTD（*Nature Biotechnology*, 2022）采用概率模型，重点是 spot 去卷积，并不直接生成论文定义的全基因 iscRNA。
- Tangram（*Nature Methods*, 2021）、CARD（*Nature Biotechnology*, 2022）和 CytoSPACE（*Nature Biotechnology*, 2023）把参考细胞或其组合映射到空间位置，结果对参考质量敏感，而且映射本身不一定增加新的表达分辨率。
- SpatialScope（*Nature Communications*, 2023）和 iStar（*Nature Biotechnology*, 2024）能够提高分辨率，但论文认为它们可能把输出限制在参考表达范围、只覆盖部分基因或扭曲空间变异基因。

Spotiphy 的新意是把“细胞类型比例估计”和“每个基因在不同细胞类型间的分配”连在一起，再用图像提供细胞数量与位置约束。

### 3. 一句话直觉

可以把一个 spot 想成一碗混合汤：

- scRNA 参考告诉我们每种“原料”通常是什么味道；
- spot 表达告诉我们整碗汤里有哪些分子、各有多少；
- H&E 图像告诉我们碗里大约有几颗“细胞”；
- Spotiphy 先估计每种细胞类型贡献了多少分子，再把每个基因的 spot 计数按这些贡献拆开，最后把拆出的类型标签随机放到图像中的细胞核上。

因此，输出是受约束的推断，不是对每个真实细胞重新测序。

### 4. 输入、输出与关键假设

输入：

- 空间计数矩阵 $\boldsymbol X\in\mathbb R^{S\times G}$；
- 单细胞矩阵 $\boldsymbol Y\in\mathbb R^{C\times G}$；
- 每个单细胞的类型标签 $\tau(c)$；
- 可选 H&E 图像与 spot 坐标。

输出：

- 每个 spot 的类型比例 $\boldsymbol P\in\mathbb R^{S\times T}$；
- spot × gene × type 的表达分解 $\boldsymbol U$；
- 类似 scRNA 的 `AnnData`，每一行是一个推断伪细胞；
- 每个细胞核的随机类型标注与近似边界。

关键假设：

- scRNA 参考必须包含组织中的主要细胞类型；缺失类型无法被算法自动发现。
- 参考中的 marker gene 足以区分不同类型。
- scRNA 和 ST 的技术差异可由逐基因 batch factor 近似吸收。
- 小尺度邻域内的细胞组成足够平滑，才能推断非捕获区域。
- 细胞核中心可以代表细胞位置，但核的形态目前不用于判定类型。

### 5. 完整计算流程

```text
scRNA + 类型标签
    │
    ├─ CPM/过滤/共有基因
    ├─ marker gene 选择
    └─ 构建类型 × gene 参考矩阵 Φ
                         │
spot ST ─ marker 子矩阵 ─┼─ Pyro 概率模型 ─> 每个 spot 的类型比例 P
                         │
H&E ─ StarDist ─> 核位置与每个 spot 的细胞数 Ns
                         │
                         ├─ P × Ns ─> 整数类型数 nst
                         ├─ 全基因表达按类型权重分配 ─> iscRNA
                         ├─ spot 内随机给核分配类型
                         ├─ spot 外核平滑插值后随机采样类型
                         └─ 从核中心向外生长近似细胞边界
                                      │
                                      v
                         伪单细胞全转录组切片图像
```

### 6. Marker gene 选择

对类型 $t$ 和基因 $g$，论文比较该类型与所有其他类型的平均表达，计算 fold-change 集合 $\boldsymbol F_{g,t}$、其 $v$ 分位数 $f_{g,t}(v)$、单侧检验 $P$ 值 $\lambda_{g,t,t'}$ 和非零覆盖率 $w_{t,g}$。基因需同时满足：

$$
f_{g,t}(v)>l_{\rm fold},\qquad
\max_{t'\ne t}\lambda_{g,t,t'}<l_\lambda,\qquad
w_{t,g}>l_{\rm cover}.
$$

论文使用 $l_{\rm fold}=1.5$、$l_\lambda=0.1$、$l_{\rm cover}=60\%$、$v=0.15$、$n_{\rm select}=50$。

代码保留了这些阈值结构，但实现使用 Welch 风格的 $t$ 统计量，而且每个基因只让平均表达最高的类型进入候选，再从排序后的比较量取值。因此这一部分是 **Partial**，不能说与论文的逐对 $z$ test 完全一致。

### 7. scRNA 参考矩阵

对每个细胞类型，把该类型所有细胞的表达相加，再按该类型的总表达归一化：

$$
\hat\varphi_{t,g}^{(m)}=
\frac{\sum_{\{c\mid\tau(c)=t\}}y_{c,g}^{(m)}}
{\sum_{\{c\mid\tau(c)=t\}}\sum_&#123;&#123;g}'=1}^{G_m}y_{c,{g}'}^{(m)}}.
$$

每一行因此是一个基因概率分布。`construct_sc_ref` 对应这一公式，是核心的 **Exact** 匹配。代码按字典序排列细胞类型，后续 `type_list` 必须保持同一顺序。

### 8. 概率去卷积

对 spot $s$，$q_{s,t}$ 表示类型 $t$ 对捕获分子的贡献比例：

$$
\rho_{s,g}=\sum_tq_{s,t}\varphi_{t,g}^{(m)}.
$$

为补偿 scRNA 与 ST 的平台差异，对每个基因加入 $r_g$：

$$
\widetilde\rho_{s,g}=
\frac{\rho_{s,g}2^{r_g}}
{\sum_&#123;&#123;g}'}\rho_{s,{g}'}2^{r_&#123;&#123;g}'}}}.
$$

然后令 spot 的 marker count 服从 Multinomial。代码用 Pyro 定义：

- $q_s\sim\operatorname{Dirichlet}(3\mathbf1)$；
- 基因 batch latent 经 sigmoid 后落在 0–1，再乘 `batch_prior`；
- Adam + `Trace_ELBO` 做 8,000 次 SVI 更新。

这里有一条重要边界：论文写的是每个 spot 的原始总 count $m'_s$，而代码使用全体 spot 的最大行和作为统一 `total_count`。教程先把所有 ST 行归一化到 CPM，使各行总量接近一致，所以教程路径能够工作，但它不是论文“原始计数 + 每 spot 总量”的字面实现。

### 9. 从分子贡献变成细胞比例

分子贡献比例不等于细胞数量比例：高 RNA 含量的细胞可能贡献更多分子。代码取 Pyro 的 `sigma`，除以每类细胞的平均总表达，再在 spot 内归一化：

$$
\hat p_{s,t}\propto
\frac{\sigma_{s,t}}
{\operatorname{mean}_{c:\tau(c)=t}\sum_gY_{c,g}}.
$$

这是很关键的隐藏步骤，但主文没有完整公式，而本 workspace 没有本地 Supplementary Methods，所以只能标为 **Partial / supplement-unverified**。

### 10. 图像分割与整数细胞数

Spotiphy 使用预训练 StarDist `2D_versatile_he` 分割 H&E 中的细胞核。若核中心落在 spot 半径内，就计入该 spot，得到 $N_s$。

随后把连续比例换成整数细胞数：

$$
\min\sum_t\left|\frac{n_{s,t}}{N_s}-p_{s,t}\right|,
\qquad \sum_tn_{s,t}=N_s.
$$

代码采用 largest-remainder：先取 $N_sp_{s,t}$ 的下整，再把剩余细胞分给小数余数最大的类型。这一步守恒 $N_s$，与论文目标一致。

### 11. 全基因表达分解

比例估计只使用 marker，但 iscRNA 要覆盖全部 $G$ 个基因。Spotiphy 重建全基因参考 $\boldsymbol\Phi$，并计算：

$$
\omega_{s,g,t}=
\frac{\widetilde p_{s,t}\varphi_{t,g}}
{\sum_{t'}\widetilde p_{s,t'}\varphi_{t',g}},
\qquad
\hat u_{s,t,g}=x_{s,g}\omega_{s,g,t}.
$$

直觉上，每个基因的 spot count 按“该类型在 spot 中的比例 × 该类型参考中该基因的相对表达”拆给不同类型。

代码直接计算这个后验均值式分配，没有真的对论文写出的 Multinomial 再采样。若一个 spot 内某类型有多个细胞，这些同类型伪细胞会得到相同的表达向量。因此：

- spot 级总表达能按构造近似守恒；
- 不能恢复同一 spot、同一类型内部的真实细胞间异质性。

### 12. 细胞核类型与非捕获区域

#### spot 内

代码随机打乱 spot 内的核，再按 $n_{s,t}$ 分配类型。这与论文描述一致，也意味着单个核的类型不是从图像或表达直接识别出来的。论文把这一点列为未来可由 vision transformer 改进的限制。

#### spot 外

论文主要描述 Gaussian process，同时明确 kernel density smoothing 是替代方案。当前教程调用的是 RBF 距离加权平滑：

$$
w_{ij}=\exp(-d_{ij}^2/h^2),\qquad
\widetilde p_i=\frac{\sum_jw_{ij}p_j}{\sum_jw_{ij}},
$$

再按 $\widetilde p_i$ 随机采样类型。真正使用 `GaussianProcessRegressor` 的实现存在，但函数名为 `archive_assign_type_out_gp`，不是教程默认路径。因此论文 GP、代码归档 GP、教程核平滑三者必须分开看。

#### 边界

`cell_boundary` 从每个核中心向外扩张像素，遇到最大距离、最大面积或其他细胞占用就停止，再用局部卷积提取边界。这是几何近似，不是膜染色分割。

### 13. 论文如何验证？

去卷积部分与 13 种方法比较，使用匹配 Xenium、CosMx、三个噪声等级的模拟数据和八组 scRNA–Visium 数据。六项指标为：

- 越低越好：absolute error、square error、JSD；
- 越高越好：Pearson correlation、cosine similarity、fraction correctly mapped。

代码完整实现了这六项指标。可见主图中，Spotiphy 在展示的方法里具有最高的中位相关和最低的绝对误差。

更重要的是，论文不只做算法自洽验证：

- 用 CosMx 验证脑区特异的星形胶质细胞与 DAM 表达 signature；
- 用 Resolve smFISH 验证乳腺肿瘤/正常 luminal signature；
- 用 Xenium 验证伪单细胞图像与 out-spot 插值；
- 用 Slide-tags 检查扩增后的伪细胞是否保持大体细胞类型结构。

这些证据更支持群体、区域与 signature 层面的可信度，不能直接证明每一个伪细胞都是真实的单细胞转录组。

### 14. 代码匹配与运行边界

总体匹配：**medium**。

- Exact 6：参考矩阵、StarDist spot 计数、整数细胞数、spot 内随机分配、模拟扰动、六项指标。
- Partial 7：预处理、marker 统计、Multinomial 总量、贡献到细胞比例、确定性分解、边界、out-spot 路径。
- Notebook 1：教程串起了完整流程，并保存了历史执行输出。
- Not found 2：论文声明的 version 1.0 在当前 `0.3.1` 快照中无法证明；完整发表分析脚本/配置不存在。

本次没有重新执行 Pyro、TensorFlow、StarDist 或整篇论文的 benchmark。CodeGraph 只用于静态导航，notebook 输出是历史运行痕迹，不是本次 runtime trace。workspace 中也没有本地 Supplementary Methods、自动化测试或重现全部发表图的脚本。

### 15. 应该怎样理解 Spotiphy 输出？

最稳妥的理解是：Spotiphy 把真实测得的 spot 表达，在参考类型、概率比例、核数量和空间平滑约束下，转换成可用于单细胞工具的伪细胞表示。

它适合回答：

- 某个区域是否富集某类细胞或表达程序？
- 不同组织域的细胞组成和信号通路是否不同？
- spot 级数据能否被转换成更密集、可视化友好的空间表示？

需要谨慎的问题：

- 某一个具体细胞核究竟是哪种类型？
- 同一 spot 中同类型细胞之间的真实异质性是什么？
- 非捕获区某个具体细胞的全转录组是否准确？
- 细胞–细胞相互作用能否精确到几十微米内的具体配对？

这些边界不是简单的软件缺陷，而是由输入数据本身缺少单细胞联合测量决定的。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spotiphy

### Problem

Sequencing-based spatial transcriptomics measures thousands of genes across whole sections but pools multiple cells in each capture spot and leaves noncapture gaps. Image-based assays resolve individual cells but are restricted to predefined panels. Spotiphy aims to combine the broad gene coverage of the former with the cellular localization of the latter by generating inferred single-cell RNA profiles (`iscRNA`) and pseudo-single-cell whole-section images.

### Why existing approaches are insufficient

Established deconvolution methods estimate spot composition but generally do not preserve both whole-gene spatial variation and pseudo-cell output. The paper contrasts probabilistic methods such as Cell2location (*Nature Biotechnology*, 2022) and RCTD (*Nature Biotechnology*, 2022), optimization/mapping methods such as Tangram (*Nature Methods*, 2021), CARD (*Nature Biotechnology*, 2022) and CytoSPACE (*Nature Biotechnology*, 2023), and decomposition methods such as SpatialScope (*Nature Communications*, 2023) and iStar (*Nature Biotechnology*, 2024). Their reported limitations include sensitivity to reference quality, limited recovery of new information, confinement to reference-like expression ranges or distortion/loss of spatially variable genes.

### Method

Spotiphy integrates three inputs: annotated scRNA-seq, spot-level ST and an H&E image. It:

1. selects cell-type marker genes and constructs a normalized cell-type reference matrix;
2. fits a Pyro variational generative model with per-spot Dirichlet gene-contribution scores and gene-wise batch factors;
3. converts contribution scores into cell-type proportions;
4. segments nuclei with pretrained StarDist and converts proportions into integer cell counts per spot;
5. allocates every spot's full-gene counts among cell types to create iscRNA pseudo-cells;
6. randomly assigns in-spot nuclei to the allocated types, smooths proportions into out-spot space and infers geometric cell boundaries.

The key conceptual boundary is that Spotiphy redistributes measured spot counts under reference and image constraints; it does not measure each physical cell's transcriptome. Multiple same-type pseudo-cells in one spot receive identical code-generated profiles, and nucleus identities are randomly assigned within spots.

### Evaluation and findings

The paper benchmarks deconvolution against 13 methods using matched Xenium, CosMx, simulated Visium data at three noise levels and eight paired scRNA–Visium datasets. Metrics include Pearson correlation, cosine similarity, correctly mapped fraction, absolute error, squared error and Jensen–Shannon distance. Spotiphy is reported as best or among the best across tissues and faster than competitors. The visible matched-Xenium figure places Spotiphy highest in median correlation and lowest in absolute error among the displayed methods.

Decomposition is compared with Tangram, SpatialScope and iStar. The paper reports that Spotiphy best preserves spatial-variable-gene distributions and leads the listed accuracy metrics while retaining whole-gene output. External validations show region-associated astrocyte and disease-associated microglia programs in mouse brain, tumor/normal luminal signatures and spatial domains in breast tissue, dense pseudo-cell images consistent with Xenium, and broad recovery of cell-type structure in a Slide-tags example.

### Code–paper match

Overall fidelity is **medium**: Exact 6, Partial 7, Notebook 1, Not found 2.

- Exact: reference-matrix formula, StarDist spot counts, integer type counts, random in-spot assignment, simulation perturbations and six metrics.
- Partial: preprocessing and marker statistics, Multinomial total-count handling, contribution-to-cell correction, deterministic decomposition, geometric boundaries and out-spot imputation.
- The active tutorial uses CPM-normalized ST and an RBF/kernel smoother; the paper describes raw spatial counts and a primary Gaussian-process path, while also allowing kernel smoothing as an alternative.
- The paper states Spotiphy version 1.0, but this snapshot packages version 0.3.1; equivalence is **Not found**.

### Reproducibility

**Rating: 3/5 — core algorithm inspectable, paper-scale reproduction incomplete.**

Strengths:

- GitHub snapshot fixed at commit `8167624a942fec97cf5cdfc8ed3a537622aa78f1`.
- Core Python source, documentation, executed tutorial notebooks and some tutorial inputs are present.
- Paper-linked datasets are publicly identified, and the main computational modules are readable.

Boundaries:

- No fresh end-to-end run was performed; CodeGraph paths are static and notebook outputs are historical.
- No local Supplementary Methods were acquired, leaving several implementation details unverified.
- No automated tests or complete scripts/configurations reproduce all 13 baselines, published downstream NetBID2/inferCNV/CellChat analyses or publication figures.
- PyTorch and TensorFlow require manual installation and are not declared in `install_requires`.
- In-spot labels, out-spot labels and pseudo-cell profiles are model-dependent; individual-cell truth should not be inferred from aggregate validations.

### Main limitations

- Results depend strongly on the completeness and quality of the scRNA reference; unseen cell types cannot be recovered.
- Random in-spot assignment ignores histological cell-type features.
- Smooth out-spot interpolation may blur abrupt biological boundaries.
- Pseudo-cells do not recover within-spot same-type heterogeneity.
- Best use cases are gene-rich spot platforms such as Visium or DBiT-seq; already high-resolution but low-coverage assays gain less.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
