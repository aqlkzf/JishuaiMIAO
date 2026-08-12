---
layout: default
permalink: /paper-atlas/feast-8e90d2a1/
title: "FEAST"
nav: false
description: "FEAST 的输入是带空间坐标的 H&E 全切片图像 patch，输出是原始空间转录组 spot上的 250 个基因预测值。它不生成新的实验测量，也不从图像恢复单细胞真值；它学习“组织形态与已测 ST 表达之间的对应关系”，用于在同类数据分布上推断空间表达。 方法有三个主要设计：用全局自注意力替代预先规定的稀疏图；把注意力拆成正、负两个分支以得到有符号权重；"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>FEAST</h1>
    <p>FEAST: Fully Connected Expressive Attention for Spatial Transcriptomics</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2603.25247v1" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## FEAST：从 H&E 图像预测空间基因表达的全连接有符号注意力

### 先用一句话说清楚

FEAST 的输入是带空间坐标的 H&E 全切片图像 patch，输出是**原始空间转录组 spot**上的 250 个基因预测值。它不生成新的实验测量，也不从图像恢复单细胞真值；它学习“组织形态与已测 ST 表达之间的对应关系”，用于在同类数据分布上推断空间表达。

方法有三个主要设计：用全局自注意力替代预先规定的稀疏图；把注意力拆成正、负两个分支以得到有符号权重；在原始 spot 之间补采 off-grid pseudo-spot 图像以减少 patch 空隙中的形态信息损失。代码再用“局部全点注意力 + 原始点全局注意力”的两阶段结构控制计算量。

### 它要解决的三个具体问题

#### 1. 稀疏图把未连边关系提前判死

过去的图模型常按空间邻近或形态相似度连接少数 spot。如果两个位置未被构图规则连上，模型便无法直接学习它们的关系。FEAST 把每张切片的原始 spot 放进全局 self-attention，让边权由数据动态学习，而不是由固定 kNN 图完全决定。

#### 2. 普通 softmax 只有“重要”与“不重要”

标准注意力权重非负。低权重只能表示“没有被关注”，无法单独表达“相反或抑制方向”。FEAST 通过对相似度取正、负两个分支，并从正分支中减去负分支，构造可正可负的最终注意力。

需要谨慎理解这里的“negative”：它是模型学得的有符号关联，不等同于已被实验验证的细胞抑制、调控边或因果作用。论文用免疫抑制关系说明动机，Fig. 7/9/10 展示红蓝注意力图，但注意力图本身不能证明分子机制。

#### 3. 规则 spot 网格会漏掉中间形态

每个 ST spot 只截取一个固定图像 patch。相邻 patch 之间可能留空，病理结构也可能恰好被边界截断。FEAST 在网格中间添加 pseudo-spot，只提取该位置的图像特征，让局部注意力先吸收这些额外形态上下文。

### 从 WSI 到模型输入

#### 原始 spot 与 pseudo-spot

`sample_off_grid_pseudo_spots.py` 先根据 array 坐标与像素坐标估计仿射映射，在原始网格的中间位置建立更细候选网格，再删除离最近原始 spot 过远、可能落在背景中的候选点。输出坐标表用 `is_pseudo=0/1` 区分原始与伪 spot。

脚本还会为 pseudo-spot 插值表达矩阵，这是为了让特征、计数和坐标数组保持对齐；这些插值值**不是监督标签**。`FEAST.forward` 只对 `is_pseudo == 0` 的位置输出表达，`trainer.py` 也只对原始 spot 计算 loss 和指标。

#### UNI2-h 图像表示

`extract_image_embeddings_uni.py` 围绕每个原始或 pseudo 坐标裁剪 $256\times256$ patch，调用 `MahmoodLab/UNI2-h` 提取 1536 维特征。模型首先把它投影到 768 维。UNI2-h 在这里是固定的预训练病理图像编码器；仓库没有包含其权重，复现需要 Hugging Face 的 gated access。

### 第一层机制：带空间偏置的全连接注意力

对一张切片的 $N$ 个 spot 特征，标准缩放点积得分为

$$
\mathbf S=\frac{\mathbf Q\mathbf K^T}{\sqrt{d_k}}.
$$

$S_{ij}$ 是 query spot $i$ 与 key spot $j$ 的学习相似度。对所有原始 spot 同时计算便得到 $N\times N$ 的动态全连接图。

纯 self-attention 不知道坐标。FEAST 为第 $h$ 个 head 加入距离偏置

$$
B_h(i,j)=m_h\sqrt{(i_x-j_x)^2+(i_y-j_y)^2},
$$

其中 $m_h<0$ 且不学习。代码等价地用正系数 $2^{-(h+1)}$ 乘欧氏距离后从 score 中减去。不同 head 的衰减强度不同：惩罚强的 head 偏局部，接近零的 head 可保留长距离关系。因此“全连接”是候选关系全连接，不表示所有远处位置都会得到大权重。

### 第二层机制：negative-aware attention

FEAST 对每个 head 构造

$$
\mathbf S_{\mathrm{pos},h}=\mathbf S_h+\mathbf B_h,
\qquad
\mathbf S_{\mathrm{neg},h}=-\mathbf S_h+\mathbf B_h.
$$

正分支偏好点积大的位置，负分支偏好点积小的位置；两者使用同一个空间距离惩罚，所以“负关系”也不会自动忽略空间结构。随后

$$
\mathbf A_{\mathrm{pos},h}=\operatorname{softmax}(\mathbf S_{\mathrm{pos},h}),
$$

$$
\mathbf A_{\mathrm{neg},h}=\operatorname{softmax}(\mathbf S_{\mathrm{neg},h}/\tau_{\mathrm{neg}}),
$$

$$
\mathbf A_{\mathrm{final},h}
=\mathbf A_{\mathrm{pos},h}-\beta\mathbf A_{\mathrm{neg},h}.
$$

$\tau_{\mathrm{neg}}$ 控制负分支分布的尖锐程度，$\beta$ 控制减去多少负信息。代表性配置使用 $\tau_{\mathrm{neg}}=0.6$、$\beta=1.5$。最终用 $\mathbf A_{\mathrm{final}}\mathbf V$ 聚合 value，因此输出可以包含正贡献和负贡献。

一个极简例子：若某 query 对三个 key 的正分支 softmax 为 $(0.7,0.2,0.1)$，负分支为 $(0.1,0.2,0.7)$，取 $\beta=1$，最终权重是 $(0.6,0,-0.6)$。第一个 key 被正向聚合，第二个抵消，第三个被负向聚合。它表达的是表示空间里的方向性贡献，不代表第三个 spot 在生物学上直接抑制第一个 spot。

代码的局部块和全局块都逐字实现了这三步：`model/feast.py:235-251` 与 `427-443`。

### 第三层机制：两阶段层级注意力

若把原始 spot 和大量 pseudo-spot 全部做 $O(N^2)$ 注意力，显存和时间会快速增长。每个 `TwoStageAttentionBlock` 因此分两步：

1. **局部阶段**：原始与 pseudo-spot 一起参与，但每个位置只关注空间 kNN，代码默认 $k=32$。pseudo patch 中的形态通过这一阶段进入原始 spot 表示。
2. **全局阶段**：筛选 `is_pseudo == 0` 的原始 spot，在同一切片内部做全对全 negative-aware self-attention，再把更新结果写回。

这解释了一个容易混淆的边界：论文称 FEAST 是 fully connected，准确对应的是原始 spot 的全局阶段；包含 pseudo-spot 的第一阶段是刻意设计的局部 kNN，并非全连接。Fig. 2 也明确画出 “k-NNs only” 后接 “original spots only”。

代表性模型堆叠 3 个两阶段 block，使用 8 heads。经过 LayerNorm 后，MLP 把 768 维表示映射为 250 个基因，并以末端 ReLU 约束预测非负。

### 训练与评价

训练目标是原始 spot 的均方误差

$$
\mathcal L_{\mathrm{MSE}}=
\frac{1}{N_{\mathrm{real}}G}
\sum_{i\in\mathrm{real}}\sum_{g=1}^{G}
(\hat y_{ig}-y_{ig})^2.
$$

仓库配置使用 MSE，训练器还实现 MAE 和逐基因 Pearson correlation coefficient（PCC）。切分以 slide 为单位做 8-fold cross-validation，避免同一切片 spot 同时落入训练和验证。模型推理时使用原始与 pseudo 图像特征形成上下文，但监督和评价只覆盖原始 spot。

论文在 ST-Net、Her2ST 和 SCC 三个公共数据集上报告 9 个“数据集 × 指标”结果，FEAST 在其中 7 个最佳。消融实验支持 $k=32$、negative-aware 分支和 off-grid sampling。Fig. 5/13/14 的展示样本中 FEAST 热图较 MERGE 更接近 ground truth；Fig. 6/8 展示加入 pseudo-spot 后 PCC 上升。这些图是选取的定性例子，不能替代完整交叉验证统计。

### 左到右追踪一次真实数据流

```text
WSI + 原始 ST 坐标/表达
  → 中间网格采样 pseudo 坐标
  → 每个原始/pseudo 位置裁剪 patch
  → UNI2-h 得到 1536 维特征
  → 投影到 768 维
  → [局部 kNN signed attention：原始+pseudo]
  → [全局 all-pairs signed attention：仅原始]
  → 重复 L 次
  → 原始 spot MLP
  → 250 基因预测
  → 仅原始 spot 的 MSE/MAE/PCC
```

### 论文—代码证据映射

| 论文机制 | 直接代码 | 匹配判断 | 说明 |
|---|---|---|---|
| 全局原始 spot 全连接注意力 | `model/feast.py:393-443` | Exact | 同一 slide 内计算全对全 $QK^T$ |
| 空间距离偏置 | `model/feast.py:408-426` | Exact | 减去 $2^{-(h+1)}$ 缩放距离，与论文负斜率等价 |
| 正负分支与最终相减 | `model/feast.py:425-443` | Exact | 实现 $A_{pos}-\beta A_{neg}$ |
| pseudo 的局部 kNN 阶段 | `model/feast.py:213-251` | Exact | 所有点参与，但每点只看 k 个邻居 |
| 两阶段层级结构 | `model/feast.py:463-526` | Exact | local all spots → global original only |
| off-grid 采样 | `sample_off_grid_pseudo_spots.py:63-188` | Exact | 仿射坐标、细网格候选、距离过滤 |
| pseudo 表达插值 | `sample_off_grid_pseudo_spots.py:190-367` | Partial | 生成数组但不作为训练目标，论文正文交代较弱 |
| UNI2-h 特征 | `extract_image_embeddings_uni.py:20-199` | Exact | 256×256 patch、1536 维输出 |
| 原始 spot 输出与 loss | `model/feast.py:617-625`、`engine/trainer.py:106-148` | Exact | 明确通过 `is_pseudo` 屏蔽伪标签 |
| 论文定性热图/attention map | 本地仓库直接搜索 | Not found | 有模型与指标代码，未找到 Fig. 5/7/9–14 绘图脚本 |

### 版本与复现边界

- 当前论文证据是 arXiv `2603.25247v1`，DOI 形式为 `10.48550/arXiv.2603.25247v1`，不是期刊同行评审版本。后续版本可能改变实验或实现说明。
- 本地代码来自 `https://github.com/starforTJ/FEAST`，采集提交为 `c674f9e953d2eded911444cfb545be27c839cfc8`。代码目录没有独立嵌套 `.git`；提交值来自采集元数据。
- 完整训练需要外部 MERGE 风格数据归档和 gated UNI2-h 权重；它们不在工作区内。本轮没有实际重训 8 folds，因此这里只验证论文—实现对应，而非重新验证数值结果。
- 仓库提供数据准备、特征提取、训练和评价入口，但未找到论文定性热图及 attention-map 的生成脚本，不能声称图表可一键复现。
- “从 H&E 预测基因表达”依赖训练分布内的形态—表达相关性。域偏移、染色批次、癌种差异或低表达基因都可能降低泛化；预测值不能替代实验 ST 测量。
- signed attention 增强了表示能力和可视化区分，但没有施加已知调控网络约束，也没有实验干预，因此负权重只应解释为模型关联。

### 最后记住两点

第一，FEAST 不是简单把所有原始和伪 spot 一次性做全连接：它先用局部 kNN 吸收 off-grid 形态，再只对原始 spot 做全局全连接。第二，negative-aware attention 的“负”是可学习的有符号信息流，不是自动发现的抑制性生物机制。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## FEAST Summary

### What problem does FEAST solve?

FEAST predicts spatial transcriptomics gene-expression profiles from H&E whole-slide images. The paper targets the practical cost bottleneck of ST data generation and the modeling challenge that gene expression at a spot depends not only on the spot's own morphology but also on neighboring and distant tissue context (`paper.md:19-35`).

### Why prior approaches are limited

The paper argues that patch-only models such as ST-Net do not model spot interactions, while transformer/GNN successors still impose restrictive priors: fixed multi-resolution views, sparse spatial graphs, morphology-similarity graphs, or hierarchical sparse graphs (`paper.md:48-64`). Sparse graphs are the key limitation FEAST attacks: if a pair is not connected by the pre-defined graph, any potential biological interaction is ignored (`paper.md:71-76`). Standard attention also has non-negative softmax weights, so it cannot distinguish an inhibitory relationship from no relationship (`paper.md:108-116`). Finally, fixed patch extraction can miss off-grid morphology between original spots (`paper.md:149-158`).

### Proposed method

FEAST — **Fully Connected Expressive Attention for Spatial Transcriptomics** — replaces hand-designed sparse graph edges with attention, so original spots can model all-pair interactions in the global stage (`paper.md:77-90`). It adds:

1. **Spatially biased attention:** an ALiBi-like distance penalty per attention head, equivalent in code to subtracting distance scaled by `$2^{-(h+1)}$` (`paper.md:93-107`; `model/feast.py:226-237`, `model/feast.py:417-428`).
2. **Negative-aware attention:** separate positive and negative branches, with final attention `$A_{final}=A_{pos}-\beta A_{neg}$`, allowing signed attention weights (`paper.md:117-141`; `model/feast.py:235-251`, `model/feast.py:427-443`).
3. **Off-grid pseudo-spots:** additional patches sampled between original spot coordinates to capture missing morphology (`paper.md:149-166`; `sample_off_grid_pseudo_spots.py:63-188`).
4. **Hierarchical attention:** local kNN attention over original+pseudo spots, followed by global self-attention over original spots only (`paper.md:158-166`; `model/feast.py:463-526`).

The code implements the model in `model/feast.py`: 1536-d UNI2-h features are projected to 768 dimensions, passed through stacked two-stage attention blocks, and fed to an MLP that returns predictions only for original spots (`model/feast.py:529-626`).

### Evaluation

The paper evaluates on ST-Net, Her2ST, and SCC datasets with 8-fold cross-validation, MSE/MAE/PCC metrics, and the MERGE preprocessing protocol (`paper.md:183-210`). Table 1 reports FEAST best in 7 of 9 metrics and especially strong results on the two breast-cancer datasets (`paper.md:211-216`). Ablations support `$k=32$`, negative-aware attention, and off-grid sampling as useful components (`paper.md:232-263`, `paper.md:444-536`). Local figure reads support the qualitative claims: Figures 5/13/14 show FEAST heatmaps closer to ground truth than MERGE in the displayed examples, Figures 6/8 show higher PCC with pseudo-spots, and Figures 7/9/10 show signed attention maps with visible blue negative regions.

### Code-paper match and reproducibility

**Code-paper fidelity: high for the core algorithm.** Direct source reads verify the main equations and pipeline: spatially biased positive/negative attention, local/global hierarchy, original-only output/loss, off-grid pseudo-spot generation, UNI2-h extraction, 8-fold training, and MSE/MAE/PCC metrics (`doc_code.md`).

**Reproducibility constraints:**

- Full reproduction requires external MERGE-style data and gated Hugging Face access to UNI2-h (`README.md:41-98`, `extract_image_embeddings_uni.py:20-43`).
- The repo contains model/training/data scripts but no located scripts for regenerating qualitative heatmaps or attention-map figures; searched the direct `FEAST/` tree for plotting/heatmap/attention visualization code.
- Pseudo expression arrays are generated for alignment, but the model and trainer use only original spots for prediction/loss/metrics (`README.md:70-80`, `engine/trainer.py:106-144`).

Overall, FEAST is a well-matched paper+code workspace for the computational method, with missing evidence limited mainly to external assets and figure-generation workflows.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
