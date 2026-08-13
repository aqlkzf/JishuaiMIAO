---
layout: default
permalink: /paper-atlas/unitvelo-002e689e/
title: "UniTVelo"
nav: false
wide: true
description: "UniTVelo 解决的是单细胞 RNA velocity 推断问题：给定每个细胞中 spliced 和 unspliced mRNA 的计数，推断细胞沿发育、分化或状态转变方向的动态轨迹。论文沿用 RNA velocity 的一阶动力学系统，将 unspliced RNA u(t)、spliced RNA s(t)、转录率 \\alpha(t)、剪接率 \\beta 和降解率 \\gamma 联系起来。"
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
      <span>Nature Communications · 2022</span>
    </div>
    <h1>UniTVelo</h1>
    <p>UniTVelo: temporally unified RNA velocity reinforces single-cell trajectory inference</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/StatBiomed/UniTVelo" target="_blank" rel="noopener noreferrer" aria-label="Open code for UniTVelo">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## UniTVelo 方法中文解读

### 这篇文章解决什么问题？

UniTVelo 解决的是单细胞 RNA velocity 推断问题：给定每个细胞中 spliced 和 unspliced mRNA 的计数，推断细胞沿发育、分化或状态转变方向的动态轨迹。论文沿用 RNA velocity 的一阶动力学系统，将 unspliced RNA $u(t)$、spliced RNA $s(t)$、转录率 $\alpha(t)$、剪接率 $\beta$ 和降解率 $\gamma$ 联系起来（`paper.md:33-45`）。

传统方法的困难在于：许多基因并不呈现清晰的“诱导-抑制”杏仁形相图，unspliced 信号噪声大，一些基因存在多速率动力学，单个基因独立拟合时容易过拟合或给出错误方向。论文在红系分化、骨髓、肠类器官等数据中展示了这些问题（`paper.md:70-123`）。

### UniTVelo 的核心创新

UniTVelo 有两个关键设计（`paper.md:55-69`）：

1. **以 spliced RNA 为中心的 top-down 模型。** 传统思路通常先假设转录率 $\alpha(t)$ 的形式，再推导 unspliced/spliced RNA。UniTVelo 反过来，先直接设计 spliced RNA 的时间函数 $s_g(t)=f(t;\theta_g)$，再由动力学方程推导 unspliced RNA 和 velocity（`paper.md:199-222`）。默认的 $f$ 是径向基函数（RBF），可以统一表示诱导、抑制和瞬时表达三类模式。
2. **统一潜在时间（unified latent time）。** 默认 unified-time mode 不让每个基因完全独立决定自己的时间，而是先为基因投影/排序，再把多个基因的信息聚合成一个细胞级潜在时间。这使得方向性弱但随时间单调变化的基因也能帮助稳定整体轨迹（`paper.md:270-291`）。

### 数学模型

UniTVelo 默认将 spliced RNA 写成 RBF 形式（`paper.md:199-213`）：

$$\begin{array}{lll}\,\,\,\,\,\,\,\,\,\,\,\,\,{s}_{g}(t)={h}_{g}*{e}^{-{a}_{g}*{({t}_{ng}-{\tau }_{g})}^{2}}+{o}_{g}\\ {u}_{g}(t)=\frac&#123;&#123;s}_{g}^{\prime} (t)+{\gamma }_{g}*{s}_{g}(t)}&#123;&#123;\beta }_{g}}+{i}_{g}\end{array}$$

这里 $h_g,a_g,\tau_g,o_g$ 控制基因 $g$ 的表达曲线形状；$\gamma_g,\beta_g,i_g$ 把 spliced 曲线与 unspliced 观测联系起来。速度直接定义为 spliced 曲线的一阶导数（`paper.md:216-222`）：

$$velocity=\frac{d{s}_{g}(t)}{dt}={s}_{g}(t)*(-2{a}_{g}*({t}_{ng}-{\tau }_{g})).$$

代码中，`unitvelo/optimize_utils.py:130-148` 分别实现了 spliced 拟合函数、导数速度、以及由导数和动力学参数得到的 unspliced 预测。

### 推断流程

可以把 UniTVelo 理解为下面的计算管线：

```text
spliced/unspliced count + 细胞类型标签
        |
        v
预处理 AnnData，选择 velocity genes
        |
        v
为每个基因拟合 RBF 形式的 s_g(t)，并推导 u_g(t)
        |
        v
Adam 更新基因参数 θ_g；每隔若干轮重新分配细胞时间
        |
        v
unified mode：多个基因时间聚合成共享细胞时间
independent mode：保留基因特异时间矩阵
        |
        v
velocity = ds_g(t)/dt，并构建 velocity graph / embedding / latent time
```

论文将参数估计写成残差似然和负对数似然（`paper.md:227-254`），并说明使用 Adam 梯度下降、周期性固定参数后按欧氏距离重新分配细胞时间（`paper.md:256-269`）。代码中，`unitvelo/model.py:182-342` 负责 TensorFlow 损失、Adam 优化和停止条件；`unitvelo/optimize_utils.py:204-244` 负责把细胞投影到预测相图上并寻找最小欧氏距离的时间点。

### 如何从 gene-specific time 得到 cell-specific time？

这里最容易混淆的是：$t_{ng}$ 不是最终输出的一个细胞时间，而是“细胞 $n$ 在基因 $g$ 的相图上被分配到的时间位置”。也就是说，模型先得到一个“细胞 × 基因”的时间矩阵，然后 unified-time mode 再把每个细胞跨多个基因的时间压成一个 cell-specific latent time。

第一步，固定当前的基因参数 $\theta_g$，为每个基因生成一条预测相图曲线。代码在 `compute_cell_time` 中先为每个基因构造 3000 个候选时间点 `x`，形状近似为 `3000 × G`；再用当前 RBF 参数算出这些候选时间上的 `s_predict` 和 `u_predict`。观测矩阵 `Ms`、`Mu` 被扩展成 `N × 1 × G`，预测矩阵被扩展成 `1 × 3000 × G`，这样就可以对每个细胞、每个基因、每个候选时间同时计算距离（`unitvelo/model.py:52-65`）。

第二步，对每个基因单独匹配细胞时间。`match_time` 逐个基因循环：对基因 $g$，它把每个细胞的观测点 $(s_{ng}^{obs},u_{ng}^{obs})$ 与该基因在 3000 个时间网格上的预测点 $(\hat{s}_g(t),\hat{u}_g(t))$ 比较，距离为

$$d_{nkg}=\sqrt{(s_{ng}^{obs}-\hat{s}_g(t_k))^2+(u_{ng}^{obs}-\hat{u}_g(t_k))^2}.$$

然后 `argmin` 找到距离最小的网格位置：这个位置就是代码里的 `assign_loc`，概念上对应论文的 gene-specific time $t_{ng}$（`unitvelo/optimize_utils.py:204-224`）。这一点和论文 Methods 的优化描述一致：多数迭代用 Adam 更新 $\theta_g$，每隔固定轮数就固定 $\theta_g$，再用网格搜索重新分配 $t_{ng}$（`paper.md:260-267`；`unitvelo/model.py:333-336`）。

第三步，UniTVelo 默认不直接平均这些原始相图投影位置，而是先把每个基因内部的细胞位置变成相对顺序。论文说“projection 后按 relative positions 重新排序”，再用每个基因内的分位数 $\mathbb{Q}[t_{ng}]$ 做聚合（`paper.md:281-290`）。代码默认 `REORDER_CELL='Soft_Reorder'`，因此会先对 `assign_loc` 做 `reorder`，把细胞在该基因上的网格位置转换成排序名次，再用 `col_minmax` 归一化到 0 到 1（`unitvelo/config.py:53-61`；`unitvelo/optimize_utils.py:225-230,240-248`）。直观地说，这一步把“基因 $g$ 认为这个细胞落在第几个时间网格”转换成“基因 $g$ 认为这个细胞在该基因轨迹中的相对早晚位置”。这样不同基因即使 RBF 峰值位置、表达幅度和可用时间范围不同，也可以在同一个 0 到 1 的相对尺度上比较。

第四步，跨基因聚合，得到每个细胞一个时间。经过前面三步后，`cell_time` 是一个 `N × G` 矩阵：每一行是一个细胞，每一列是一个基因给出的相对时间。论文 Eq. (7) 写成

$${t}_{n}=\frac{1}{G}*\mathop{\sum }\limits_{g}^{G}{\mathbb{Q}}[{t}_{ng}],$$

也就是对同一个细胞 $n$，把多个基因给出的相对位置做平均，得到 gene-shared / cell-specific time（`paper.md:281-290`）。代码里当 `AGGREGATE_T=True` 时，`match_time` 不返回完整的 `N × G` 矩阵，而是只取参与拟合的 velocity genes，然后调用 `max_density(cell_time[:, self.index_list])` 得到长度为 `N` 的向量（`unitvelo/optimize_utils.py:235-238`）。

需要注意代码默认不是最朴素的直接平均。配置中 `DENSITY='SVD'` 是默认值（`unitvelo/config.py:53-55`），所以 `max_density` 会对 `N × G_selected` 的时间矩阵做 SVD，保留最多 50 个奇异成分，重建低秩近似后再对每个细胞按行求均值（`unitvelo/optimize_utils.py:171-177`）。这正对应论文提到的可选去噪版本：先把基因空间投影到低维，再跨维度/基因求平均（`paper.md:290`）。如果配置为 `DENSITY='Raw'`，它才是直接对每行求均值，更接近 Eq. (7) 的表面写法；如果配置为 `DENSITY='Max'`，它会在每个细胞的一组基因时间中找最密集的窗口并取窗口均值，用更保守的局部共识代替全体平均（`unitvelo/optimize_utils.py:157-181`）。

第五步，把 cell-specific time 写回 AnnData。`compute_cell_time` 收到长度为 `N` 的聚合结果后，会 reshape 成 `N × 1`，再 broadcast 成 `N × G`，所以 `adata.layers['fit_t']` 在 unified-time mode 下看起来仍是一个细胞 × 基因矩阵，但同一个细胞在所有基因列上共享同一个时间值（`unitvelo/model.py:65-69,336-340`）。随后 `lagrange` 把这个共享时间取出并归一化为 `adata.obs['latent_time_gm']`，`fit_velo_genes` 在 `FIT_OPTION='1'` 时再把它作为最终的 `adata.obs['latent_time']`（`unitvelo/model.py:416-420`；`unitvelo/velocity.py:286-288`）。

所以，gene-specific 到 cell-specific 的转换可以概括为：

```text
每个基因的 RBF 相图
        |
        v
每个 cell-gene 对找最近时间网格：t_ng
        |
        v
在每个基因内部排序/归一化：Q[t_ng]
        |
        v
跨 velocity genes 聚合：Raw 平均 / 默认 SVD 去噪后平均 / Max 局部密度
        |
        v
每个细胞一个 unified latent time：t_n
```

这个设计的动机是减少“每个基因都自己解释一套时间”的自由度。许多基因只有单调上升或下降、方向性弱、相图不呈典型杏仁形；如果完全保留 gene-specific time，模型容易让每个基因过度适配自己的噪声。unified-time mode 先让每个基因投票给细胞的相对早晚，再在细胞层面形成共识时间，因此弱动态但随发育稳定变化的基因也能贡献整体排序（`paper.md:273-290`）。

### 两种时间模式

- **Unified-time mode（默认）**：论文用 Eq. (7) 表示把基因特异时间的分位数聚合为细胞共享时间（`paper.md:270-291`）。代码默认 `FIT_OPTION='1'`、`AGGREGATE_T=True`、`DENSITY='SVD'`（`unitvelo/config.py:45-66`），因此默认实现更接近上面解释的“先做低维去噪再聚合”的版本。
- **Independent mode**：适合 cell cycle 或稀疏细胞类型等复杂情况。论文说明该模式固定 $(\tau_g,o_g,i_g)=(0.5,0,0)$，并直接使用基因特异时间矩阵（`paper.md:293-307`）。代码通过 `FIT_OPTION='2'` 改变可优化参数集合（`unitvelo/optimize_utils.py:267-283`）。

论文还提到 `utils.choose_mode` 可辅助选择模式（`paper.md:309-323`）；代码中 `unitvelo/utils.py:360-411` 会检查 S/G2M cell-cycle genes 和稀疏细胞类型邻域比例，然后打印推荐模式。

### 实验结果如何支持方法？

- **Fig. 2 红系分化**：UniTVelo 在小鼠和人红系分化中给出更符合预期的 velocity 方向；对 MURK genes 和方向性弱的动态基因，统一时间减少了单基因过拟合（`paper.md:70-89`；`figure_analysis.md`）。
- **Fig. 3 骨髓发育**：UniTVelo 在 HSC 到多个分支的骨髓轨迹中恢复了更合理方向，并通过基因相图解释 `CD44`、`CELF2`、`TAOK3` 等基因（`paper.md:90-106`；`figure_analysis.md`）。
- **Fig. 4 肠类器官**：UniTVelo 区分 stem cells 到 secretory / enterocyte 两条分化分支，并用基因级 $R^2$ 评价哪些基因更好解释轨迹（`paper.md:107-123`；`figure_analysis.md`）。

### 代码可复现性

论文声明代码在 GitHub/Zenodo 可用，且结果复现流程写在仓库 notebooks 中（`paper.md:365-367`）。核心算法与论文匹配度较高：入口在 `unitvelo/main.py:5-65`，配置在 `unitvelo/config.py:1-139`，速度基因选择和拟合调度在 `unitvelo/velocity.py:43-133,254-285`，RBF/速度/时间匹配在 `unitvelo/optimize_utils.py:130-148,204-244`，训练和损失在 `unitvelo/model.py:182-342`。

需要注意的是：外部数据需要从 paper 的 Data availability 中列出的 scVelo、GEO、Human Cell Atlas、Kharchenko Lab 或 request-only 来源获取（`paper.md:356-363`）；论文似然公式在代码中体现为残差损失和 log-likelihood 诊断，并带有交替优化的工程实现细节。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## UniTVelo Summary

### What problem does the paper solve?

UniTVelo targets RNA velocity inference from single-cell spliced and unspliced mRNA counts. The goal is to infer directed developmental or state-transition trajectories, but existing RNA velocity models can fail when genes have weak directionality, multiple kinetic rates, noisy unspliced counts, or complex cell-cycle/sparse-cell settings. The paper frames the standard velocity problem with the first-order transcription/splicing ODE for unspliced $u(t)$ and spliced $s(t)$ RNA (`paper.md:33-45`).

### What is new?

The method makes two main changes (`paper.md:55-69`):

1. **Spliced-RNA-oriented top-down modeling.** Instead of specifying transcription rate first, UniTVelo directly models the spliced RNA profile $s_g(t)=f(t;\theta_g)$ and derives unspliced expectation and velocity from it. The default function is an RBF that can represent induction, repression, and transient patterns (`paper.md:199-222`).
2. **Unified latent time.** In default unified-time mode, gene-specific time assignments are aggregated into a shared cell time, allowing weakly directional but dynamically informative genes to reinforce a common trajectory (`paper.md:270-291`). An independent mode remains available for cell-cycle or sparse-cell scenarios (`paper.md:293-323`).

### How does it work?

At a high level, UniTVelo takes spliced/unspliced count matrices, selects velocity genes, fits an RBF curve for spliced RNA, derives unspliced RNA from the ODE, computes velocity as $ds_g(t)/dt$, and alternates between updating gene-specific parameters and reassigning cell times. The paper describes Adam-based gradient descent with periodic time reassignment by minimizing Euclidean distance to phase trajectories (`paper.md:256-269`).

The cloned implementation matches this structure. `run_model` prepares data/configuration and calls `Velocity.fit_velo_genes` (`UniTVelo/unitvelo/main.py:5-65`). The RBF spliced function, derivative velocity, and unspliced transformation are implemented in `UniTVelo/unitvelo/optimize_utils.py:130-148`. The TensorFlow optimization loop and time reassignment are implemented in `UniTVelo/unitvelo/model.py:182-342` and `UniTVelo/unitvelo/optimize_utils.py:204-244`.

### Evaluation

The paper evaluates UniTVelo across erythroid maturation, human bone marrow, intestinal organoids, dentate gyrus, retina, scNT-seq, oligodendrocyte lineage, and pancreas datasets. Main figure evidence shows:

- **Figure 2:** UniTVelo corrects mouse and human erythroid velocity directions where scVelo dynamical mode is distorted, including examples of MURK and weak-directionality genes (`paper.md:70-89`; `figure_analysis.md`).
- **Figure 3:** UniTVelo recovers direction and latent time in human bone marrow branches, while scVelo shows reversed/distorted flows (`paper.md:90-106`; `figure_analysis.md`).
- **Figure 4:** UniTVelo resolves intestinal organoid secretory and enterocyte branches and uses gene-wise $R^2$ to interpret fitted genes (`paper.md:107-123`; `figure_analysis.md`).

The paper also defines CBDir and ICCoh metrics for trajectory-direction correctness and within-cluster coherence (`paper.md:325-349`).

### Code and reproducibility

The paper states that UniTVelo is available as a Python package at GitHub/Zenodo and that detailed figure workflows are provided as Jupyter notebooks (`paper.md:365-367`). This workspace cloned `https://github.com/StatBiomed/UniTVelo` at commit `0a3d3020d34ffdf83d7e32368d2c0314128b23e1`. The code-paper fidelity is **high** for the core algorithm: RBF functions, derivative velocity, time reassignment, Adam optimization, configuration defaults, and mode-choice utility are present and line-verifiable in the package (`doc_code.md`).

Reproducibility caveats: several datasets are external or request-based (`paper.md:356-363`), supplementary material was not converted to markdown in this workspace, and figure notebooks were located but not exhaustively audited cell-by-cell. The paper's likelihood equations are implemented as residual losses/log-likelihood diagnostics with alternating optimization rather than a literal single expression, so that mapping is best described as partial at the equation-code level.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
