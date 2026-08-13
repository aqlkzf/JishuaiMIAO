---
layout: default
permalink: /paper-atlas/gravity-3a7a55fd/
title: "GRAVITY"
nav: false
wide: true
description: "GRAVITY 是一个把 RNA velocity、基因动力学参数和动态基因调控网络放在同一个神经模型里学习的方法。它输入 unspliced/spliced RNA、二维细胞嵌入和先验 TF-target 网络，输出细胞速度、基因速度、\\alpha,\\beta,\\gamma 动力学参数，以及基于 attention 的调控因子和调控模块解释。"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>GRAVITY</h1>
    <p>GRAVITY: Dynamic gene regulatory network-enhanced RNA velocity modeling for trajectory inference and biological discovery</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.01.31.702983" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GRAVITY">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/CSUBioGroup/GRAVITY" target="_blank" rel="noopener noreferrer" aria-label="Open code for GRAVITY">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GRAVITY 方法中文解读

### 一句话概览

GRAVITY 是一个把 RNA velocity、基因动力学参数和动态基因调控网络放在同一个神经模型里学习的方法。它输入 unspliced/spliced RNA、二维细胞嵌入和先验 TF-target 网络，输出细胞速度、基因速度、$\alpha,\beta,\gamma$ 动力学参数，以及基于 attention 的调控因子和调控模块解释。

更准确地说，GRAVITY 不是只问“每个基因未来表达怎么变”，而是先问“这个细胞整体应该往哪里走”，再用这个整体方向约束基因级动力学。

### 1. 它解决什么问题

传统 RNA velocity 从 unspliced 和 spliced RNA 推断细胞未来状态。问题在于，很多方法先逐基因估计转录、剪接和降解速率，再把这些基因速度汇总成细胞速度。论文认为这种 bottom-up 方式会漏掉发育过程中的调控协同：一个细胞命运分支往往由 TF 和多个 target gene 的调控程序共同推动，而不是由孤立基因独立变化决定。

GRAVITY 的核心想法是：把先验调控网络放进 velocity 模型中，让模型在推断速度时同时学习“哪些基因/TF 在这个细胞状态下更像调控驱动因素”。因此它的输出有两层含义：

- **速度和动力学参数**：模型直接预测的 cell/gene velocity 与 $\alpha,\beta,\gamma$。
- **调控解释**：attention 矩阵导出的 TF 分数、cell-type GRN、pathway/module 和 perturbation 结果，属于需要外部证据验证的调控假设。

### 2. 输入、输出和关键变量

| 元素 | 论文/代码名称 | 含义 | 证据锚点 |
|---|---|---|---|
| unspliced RNA | $u_{ij}$ / `unsplice_mat` | 基因 $i$ 在细胞 $j$ 的未剪接 RNA | `gravity_model.py:105-117` |
| spliced RNA | $s_{ij}$ / `splice_mat` | 成熟 RNA | `gravity_model.py:106-119` |
| 细胞嵌入 | $\mathbf c_j$ / `points`, `cell_mat` | UMAP 等二维坐标 | `cell_model.py:303-305`, `gravity_model.py:120-124` |
| 先验网络 | $Net_{prior}$ / `attn_mask` | TF-target 候选调控边 | `datasets.py:117-160`, `cell_model.py:56-74` |
| 动力学参数 | $\alpha,\beta,\gamma$ | 转录、剪接、降解速率 | `gravity_model.py:145-151` |
| attention 矩阵 | $M_{attr}$ / `self.GravityModel.attention` | 动态调控关系的模型解释信号 | `cell_model.py:352-437` |
| future anchor | $p(j)$ / `future_positions.npy` | stage 2 用的未来邻居细胞 | `future.py:87-110` |

代码中的输入不是直接读论文里的矩阵形式，而是读 cellDancer 风格长表或 AnnData 导出的 CSV，再转成内部 `combine.csv`。这个实现细节很重要，因为细胞坐标不仅用于画图，也进入模型、neighbor 构建和 future projection。

### 3. 计算流程：每一步输入、输出、维度、含义

先定义维度记号，后面的表都按这个读：

- $N$：整个数据集的细胞数。
- $B$：一个 mini-batch 的细胞数。
- $G$：进入模型的基因数，代码中是 prior/HVG 过滤后的 `hvgs`。
- $C=2$：细胞坐标维度，默认是 UMAP 的 `embedding1, embedding2`。
- $D$：模型 hidden 维度；默认 `embedding_size=16`，同时等于 `model_dimension=16`。
- $E=D/2$：表达 embedding 和 cell-coordinate embedding 各占一半，默认是 8。
- $H=8$：multi-head attention 的 head 数。
- $d_h=D/H$：每个 head 的 key/query/value 维度。
- $K^+$、$K^-$：stage 1 的近邻正样本数和远端负样本数。

论文把核心模型写成：

$$
(\alpha_j,\beta_j,\gamma_j)=f_\theta(\mathbf u_j,\mathbf s_j,\mathbf c_j,Net_{prior}),
$$

也就是对每个 cell $j$，同时输入全部基因的 unspliced 向量 $\mathbf u_j\in\mathbb R^G$、spliced 向量 $\mathbf s_j\in\mathbb R^G$、二维 cell embedding $\mathbf c_j\in\mathbb R^2$ 和先验网络，输出该 cell 内所有基因的 kinetic rates：$\alpha_j,\beta_j,\gamma_j\in\mathbb R^G$。源码里这个函数主要对应 `FullModelCellWise.forward -> GravityModel.forward`。

| 步骤 | 代码位置 | 输入及维度 | 计算 | 输出及维度 | 含义 |
|---|---|---|---|---|---|
| 1. 读入一个 batch | `CustomDataset.__getitem__`, `cell_model.py:303-309` | `x`: $[B,3+2G]$，前三列是 `cellIndex, embedding1, embedding2`，后面是 `u_1,s_1,\dots,u_G,s_G` | 拆出 `cell_info`、`gene_info`，再按奇偶列取 `unsplice` 和 `splice` | `points`: $[B,2]$；`unsplice`: $[B,G]$；`splice`: $[B,G]$ | 把表格数据变成模型真正吃的三个张量：坐标、未剪接、成熟 RNA |
| 2. 生成 prior mask | `datasets.py:117-160`, `cell_model.py:56-74` | prior edge list: `from -> to`；`gene_list`: 长度 $G$ | 构建 `TF -> targets` 和 `target -> TFs`；`mask_generate` 生成 boolean mask | `attn_mask`: $[G,G]$，`True` 表示禁止 attention，`False` 表示允许 | mask 的行是 query/target gene，列是 key/value 候选 regulator gene |
| 3. 表达 broadcast | `gravity_model.py:115-119` | `unsplice`, `splice`: $[B,G]$ | `einops.repeat(..., 'b g -> b g k', k=G)` | `unsplice_mat_broadcast`, `splice_mat_broadcast`: $[B,G,G]$ | 代码把每个 gene 的标量表达扩展成长度为 $G$ 的向量，再交给线性层；这是实现细节，不是论文公式里的显式写法 |
| 4. 表达和坐标 embedding | `gravity_model.py:116-124` | RNA broadcast: $[B,G,G]$；`points`: $[B,2]$ | `unsplice_embedding`, `splice_embedding`, `cell_embedding`，再把 cell embedding 复制到每个 gene 上并 concat | `unsplice_channel`, `splice_channel`: $[B,G,E]$；`cell_repeated`: $[B,G,E]$；`us_final`, `s_final`: $[B,G,D]$ | 每个 cell 内每个 gene 变成一个 token；token 同时包含表达信息和该 cell 的二维位置 |
| 5. prior-masked cross-attention | `gravity_model.py:126-130`, `core.py:67-90` | `q=us_final`: $[B,G,D]$；`k=s_final`: $[B,G,D]$；`v=us_final`: $[B,G,D]$；mask: $[G,G]$ | 投影为 $Q,K,V\in[B,H,G,d_h]$；计算 score $[B,H,G,G]$；对 mask 为 `True` 的位置填 `-1e9`；沿最后一维 softmax | `attn_matrix`: $[B,H,G,G]$；attention 输出再合并为 $[B,G,D]$ | 对每个 cell、每个 target gene，只从 prior 允许的 regulator genes 汇总上下文 |
| 6. FFN 更新 gene 表示 | `gravity_model.py:128-132`, `core.py:17-38` | attention 输出: $[B,G,D]$ | 1x1 conv FFN、residual、LayerNorm | `encoder_output`: $[B,G,D]$ | 得到带 regulatory context 的 unspliced/gene 表示；代码存在 `self.unsplice_enc` |
| 7. kinetic solver | `gravity_model.py:134-147` | `encoder_output`: $[B,G,D]$；`s_final`: $[B,G,D]$ | reshape 为 $[BG,D]$，拼成 `solver_input`: $[BG,2,D]$，转置为 $[BG,D,2]$；MLP 输出后对 hidden 维平均 | `solver_output`: $[BG,3]$；`alphas`, `betas`, `gammas`: $[B,G]$ | 预测每个 cell-gene 的转录、剪接、降解速率。论文写作 $\Psi:\mathbb R^{2D}\to\mathbb R^3$；代码实际是按 hidden 维的二元输入共享 MLP，再对 $D$ 个位置平均 |
| 8. rate 缩放 | `gravity_model.py:149-151`, `cell_model.py:316-320` | raw $\alpha,\beta,\gamma$: $[B,G]$；`alpha0,beta0,gamma0`: $[G]$ | `Softplus` 保证非负，再乘 batch-derived scale | scaled $\hat\alpha,\hat\beta,\hat\gamma$: $[B,G]$ | 把神经网络输出放回 RNA count 的量级；`alpha0=2*max(u)`，`beta0=1`，`gamma0=max(u)/(max(s)+eps)` |
| 9. ODE 小步外推 | `gravity_model.py:153-155` | 当前 `unsplice`, `splice`: $[B,G]$；rates: $[B,G]$ | 固定 $\Delta t=0.5$，计算 $u'=u+\Delta t(\hat\alpha-\hat\beta u)$ 和 $s'=s+\Delta t(\hat\beta u-\hat\gamma s)$ | `unsplice_predict`, `splice_predict`: $[B,G]$ | 得到每个 cell-gene 的未来 RNA abundance；velocity 就是 $u'-u$ 和 $s'-s$ |

#### 3.1 cross-attention 到底针对什么

论文原文说 regulatory network aware module 用 masked multi-head cross-attention 识别 cell-specific regulatory relationships，并强调 target gene 的 unspliced abundance 受 upstream regulatory factors 影响。源码对应得更具体：

- attention 不是在 cell-cell 图上做，也不是在 pseudotime/time point 上做；
- attention 是在**同一个 cell 内部的 gene-by-gene 矩阵**上做；
- attention 的每一行是一个 target/query gene，每一列是一个候选 regulator/key gene；
- `attn_matrix[b, h, i, r]` 可以读成：在 cell $b$、head $h$ 中，target gene $i$ 从 candidate regulator gene $r$ 接收多少 attention。

论文公式把 mask 写成乘以 $Net_{prior}$：

$$
CrossAttr(H_i^u,H_{g'}^s)=softmax\left(\frac{(H_i^uW_q)(H_{g'}^sW_k)^T}{\sqrt{d_k}}\times Net_{prior}\right)(H_i^uW_v).
$$

代码实现要更准确地表述为 boolean mask：`mask_generate` 根据 `target -> [TFs]` 把允许的 regulator 列设为 `False`，其他列为 `True`；`MultiHeadAttention.forward` 在 softmax 前执行 `scores.masked_fill(mask, -1e9)`。因此它和论文意图一致，都是优先允许先验 TF-target 边；但数学实现不是“score 数值乘以 0/1 邻接矩阵”，而是“softmax 前屏蔽不允许的列”。

需要特别注意 query/key/value 的来源：`self.cross(us_final, s_final, us_final, mask)` 表示 target gene 的 unspliced token 做 query，候选 regulator gene 的 spliced token 做 key，候选 regulator gene 的 unspliced token 做 value。输出仍然是一组 $[B,G,D]$ 的 target-gene 表示，随后进入 kinetic solver，而不是直接输出一张最终 GRN。

#### 3.2 kinetic solver 的输入输出

论文说 updated unspliced embedding 和 spliced embedding 拼接后进入共享 MLP，输出 $\alpha_i,\beta_i,\gamma_i$。代码里确实共享同一个 `MLPTranslator` 给所有基因使用，但形状处理有一个实现细节：

1. `encoder_output.reshape(-1, D)` 得到 $[BG,D]$，代表每个 cell-gene 的 regulatory-updated unspliced 表示。
2. `s_final.reshape(-1, D)` 得到 $[BG,D]$，代表同一个 cell-gene 的 spliced 表示。
3. 二者先拼成 $[BG,2,D]$，再转置成 $[BG,D,2]$。
4. `MLPTranslator(2,3,...)` 对最后一维的二元组做映射，再对 $D$ 个 hidden 位置求平均，得到 $[BG,3]$。
5. reshape 后得到 `alphas/betas/gammas`: $[B,G]$。

所以从含义上看，solver 仍然是在为每个 cell-gene 预测三个 kinetic parameters；从代码形状看，它不是简单把 $2D$ 维向量展平后一次性映射到 3 维，而是按 hidden 位置共享处理后聚合。

### 4. 训练、导出和 stage 2 的计算流程

GRAVITY 的训练逻辑是先抓细胞整体方向，再细化基因动力学。论文称这能缓解“逐基因动力学”和“整体 cell velocity coherence”之间的冲突；源码里分别由 `FullModelCellWise` 和 `FullModelGeneWise` 实现。

| 阶段 | 输入及维度 | 关键计算 | 输出及维度 | 含义 |
|---|---|---|---|---|
| Stage 1 forward | `x`: $[B,3+2G]$；prior mask: $[G,G]$ | 完整执行 embedding、prior-masked attention、FFN、solver、ODE update | $u',s',\alpha,\beta,\gamma$: 都是 $[B,G]$；attention: $[B,H,G,G]$ | 学到 cell-level velocity 和 attention-derived regulatory context |
| Stage 1 attention weight | attention: $[B,H,G,G]$ | 先对 head 平均成 $[B,G,G]$，再对 query/row 方向平均，得到 key-centric gene weight | `loss_weight`: $[B,G]$ | 权重更像“某个 gene 作为 regulator/key 被多少 target 关注”，用于加权 velocity loss |
| Stage 1 positive/negative directions | 当前 $u,s,u',s'$: $[B,G]$；近邻表达: $[K^+,B,G]$；远端表达: $[K^-,B,G]$ | 正样本取近邻平均方向，负样本取远端平均方向；对 unspliced 和 spliced 分别算 weighted triplet loss | scalar loss | 让预测 velocity 接近局部邻域方向、远离远端细胞方向 |
| Stage 1 export | 每个 batch 的预测和 attention | 写 `stage1.csv`；attention 按 cell type 平均；TF score 按 `TF -> target` map 聚合 | `stage1.csv`、`attentions/attention_TF_scores_with_types.h5ad`、mean attention matrices | stage 1 的 velocity 是后续 future projection 和调控解释的主要来源 |
| Future projection | 全体细胞 embedding: $[N,2]$；stage 1 embedding velocity: $[N,2]$ | `new_positions = embeddings + directions`；半径是 `norm(direction)*tau`；半径内取最近真实细胞，否则取自己 | `future_positions.npy`: $[N,3]$，前两列是 future anchor 坐标，第三列是 anchor cell index | 把连续 future point 映射回可比较的真实细胞 |
| Stage 2 forward | `x`: $[B,3+2G]$；future index: $[N]$ | 加载 stage 1 checkpoint；冻结几乎全部参数；只开放 solver 最后最多三层；forward 使用全 `False` mask | $u',s',\alpha,\beta,\gamma$: $[B,G]$ | stage 2 是 kinetic solver refinement，不是第二次 prior-masked GRN discovery |
| Stage 2 loss/export | 当前 cell 的预测 velocity: $[B,G]$；future-neighbor 表达差: $[B,G]$ | `velocity_calculate_gene` 用 MSE-like 差异对齐 predicted velocity 和 future-neighbor expression difference | scalar loss；`stage2.csv` | 用 stage 1 得到的全局方向约束逐基因 kinetic rates |

Stage 1 的 cell-wise loss 对应论文 Eq. 8-9。代码中 `WeightedFeatureTripletLoss` 的核心形式是：

$$
d_w(a,p)=\sqrt{\sum_g w_g(a_g-p_g)^2},\qquad
\mathcal L=\max(0,d_w(a,p)-d_w(a,n)+m).
$$

其中 anchor 是模型预测的 velocity，positive 是近邻平均方向，negative 是远端平均方向，$w_g$ 来自 attention 的 key/column 聚合。这个设计把“哪些 gene 更像 regulator/driver”的信息带入整体 cell velocity 训练。

Stage 2 对应论文 Eq. 10-11，但有两个代码层面的边界要写清楚：

- `FullModelGeneWise.forward` 构造的是 `torch.zeros((G,G), dtype=torch.bool)`，即 attention 不再用 prior-derived mask 屏蔽边。
- `gene_stage.py` 加载 stage 1 checkpoint 后冻结所有参数，只把 solver MLP 最后最多三层设为 trainable。因此 stage 2 的主要作用是微调 kinetic rates，使每个 gene 的 $u',s'$ 更贴近 future-neighbor 的表达差，而不是重新学习一张动态 GRN。

### 5. 论文结果怎么理解

论文的证据分成三类。

#### 速度推断证据

SERGIO 模拟数据包含 linear、bifurcating、trifurcating、quadrifurcating 四种轨迹。GRAVITY 在 BATC 指标上平均比第二名 scVelo 高 5.3%，并在加入 1 到 5 倍 prior network 噪声时保持相对稳定。

真实数据中，human forebrain 用连续神经发育轨迹检验速度方向；RPE-1 scEU-seq 用 FUCCI cell-cycle phase 和代谢标记的 kinetic pattern 检验伪时间和动力学参数。论文报告 GRAVITY 的 pseudotime Spearman 相关为 0.999，并在 100 个 cell-cycle 相关基因中正确分类 51 个 turnover pattern，而 CellDancer 为 32 个。

#### 调控解释证据

在 mouse E15.5 pancreas 中，论文用 attention 构建 cell-type-specific GRN，调控相似性聚类能恢复 endocrine lineage 结构。Pdx1 的 beta-cell top 25 target 中，15 个由 ChIP-seq 或文献支持。insulin signaling pathway activity 和 GO enrichment 也与 beta-cell 功能一致。

在 E18 mouse embryonic brain 中，GRAVITY 区分 Upper Layer 和 Deeper Layer 两个 endpoint，并用 Bcl11b/Foxp2 标记解释 Deeper Layer 内的 L5/L6 subterminal states。论文还把 top 100 cell-type GRN edges 与 scATAC-derived ChromVAR/JASPAR 关系比较，报告四类细胞 accuracy 高于 0.69，IPC 为 0.80。

#### Perturbation 证据

论文描述了 in silico perturbation：抑制时把目标基因的 unspliced/spliced 表达设为 0，并移除它及 incident edges；激活时上调目标基因表达，然后重新推断 velocity。pancreas 例子包括 Ghrl KO 和 Dnmt1/Arx/PMN 相关 alpha-to-beta shift。

代码审查结论是：核心 package 中没有找到一个可复用的 perturbation workflow 函数。因此这个部分在文档中应标为“论文下游分析/假设生成”，不能写成核心包可直接复现的 API。

### 6. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| 表达和细胞坐标嵌入 | `gravity/models/gravity_model.py:94-124` | broadcast RNA，线性嵌入，并拼接 cell embedding | Exact |
| masked cross-attention | `gravity/models/core.py:80-83`; `gravity/train/cell_model.py:56-74` | boolean mask + `-1e9` before softmax | Partial, implementation detail differs |
| $\alpha,\beta,\gamma$ | `gravity/models/gravity_model.py:145-151` | Softplus 后乘尺度因子 | Exact |
| fixed `dt=0.5` update | `gravity/models/gravity_model.py:153-154` | Euler-style future RNA update | Exact |
| cell-wise triplet loss | `gravity/train/cell_model.py:189-198`; `gravity/train/losses.py:21-33` | attention 加权近邻/远端 triplet loss | Exact |
| future neighbor | `gravity/tools/future.py:87-110` | 半径内最近真实细胞，否则 self | Exact |
| stage 2 冻结策略 | `gravity/train/gene_stage.py:307-329` | 只训练 solver 最后最多三层 | Exact |
| stage 2 loss | `gravity/train/gene_model.py:39-76` | 与 future-neighbor expression difference 对齐 | Partial, 代码为 MSE-like 实现 |
| BATC | `gravity/analysis/batc.py:205-391` | branch-aware tangent cosine | Exact |
| TF attention scoring | `gravity/train/attention.py:70-177` | 按 TF-target mapping 聚合 attention | Exact |
| pathway score | core package 未找到通用函数 | 论文 Eq.15/README notebook context 有描述 | Not found as reusable core API |
| perturbation | core package 未找到通用函数 | 论文 Methods 描述抑制/激活流程 | Not found as reusable core API |

### 7. 读这个方法时最容易误解的点

1. **attention 不是因果证明。** 它是先验网络约束下的模型权重，可以生成调控假设；论文用部分 ChIP、ChromVAR/JASPAR、marker 和文献做验证，但不是每条边都有实验因果证据。
2. **UMAP/二维 embedding 是模型输入，不只是可视化。** 它参与 cell embedding、近邻/负样本构建和 future projection，所以 embedding 偏差会影响模型。
3. **prior 缺失会改变模型语义。** 如果 prior 不存在或过滤后为空，代码会退回到所有 HVG 作为候选 TF/TG，这时解释性不等同于“可靠先验约束”。
4. **stage 2 不是重新发现 GRN。** 它主要微调 kinetic solver；动态 GRN 解释主要来自 stage 1 attention export。
5. **perturbation 不外推到未知状态。** 论文也明确说 perturbation confined to observed expression space，因此它适合提出假设，不适合直接宣称能预测未观测细胞类型。

### 8. 推荐阅读顺序

1. 先看 `summary.md`：掌握贡献、证据和复现边界。
2. 再看 `doc_method.md`：按公式和 pipeline 理解模型。
3. 查 `doc_code.md`：确认哪些论文模块由源码支持，哪些是 Not found。
4. 看 `figure_analysis.md`：逐图判断每个实验支持什么。
5. 需要追证据时看 `claude_notes.md`：那里有公式、claim、code line 和 open question ledger。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## GRAVITY Summary

### Metadata

| Field | Value |
|---|---|
| Title | GRAVITY: Dynamic gene regulatory network-enhanced RNA velocity modeling for trajectory inference and biological discovery |
| Venue | bioRxiv preprint |
| Year | 2026 |
| DOI | 10.64898/2026.01.31.702983 |
| Code | `https://github.com/CSUBioGroup/GRAVITY.git`, local commit `6e0f2b5af8310fa469f8744df9a2e4ffbecbeeb0` |

### Core Problem

GRAVITY addresses a structural weakness in RNA velocity. Classical and many neural velocity methods infer transcription, splicing, and degradation kinetics for each gene and then aggregate gene velocities into a cell-level direction. The paper argues that this bottom-up design misses two linked biological facts: genes act in coordinated regulatory programs, and the regulatory contribution of a gene can change across developmental stages and branches.

The method therefore treats RNA velocity as a system-level problem. For each cell, kinetic rates for all genes are predicted jointly from unspliced RNA, spliced RNA, a 2D cell embedding, and a prior regulatory network. The attention matrix learned under this prior mask is then used as a dynamic GRN proxy for regulator ranking, module analysis, and perturbation-style hypotheses.

### Main Contribution

The paper's central contribution is not just "another neural RNA velocity model"; it is a coupling of velocity inference and regulatory interpretation:

1. **System-level kinetic inference.** GRAVITY models all genes in a cell together as $(\alpha_j,\beta_j,\gamma_j)=f_\theta(\mathbf u_j,\mathbf s_j,\mathbf c_j,Net_{prior})$, instead of estimating each gene in isolation.
2. **Prior-aware cross-attention.** Unspliced target-gene representations attend to spliced regulator-gene representations under a binary prior GRN mask, intended to reduce indirect regulatory confounding and improve interpretability.
3. **Top-down two-stage optimization.** Stage 1 optimizes coherent cell-level velocity with an attention-weighted triplet loss. Stage 2 projects stage-1 velocity to future-neighbor anchors and refines gene-level kinetics by fine-tuning only the last up-to-three solver layers.
4. **Attention-derived biological readouts.** The paper uses attention as a weighted regulatory network for TF importance, cell-type GRNs, regulatory modules, pathway activity, GRN validation, and in silico perturbation analysis.

### Method Overview

Inputs are unspliced/spliced counts, cell labels, a 2D cell embedding such as UMAP, and a prior TF-target network. The package consumes either a cellDancer-style long CSV or an AnnData export, then converts it to an internal wide `combine.csv` layout.

The forward model embeds unspliced RNA, spliced RNA, and 2D coordinates; applies masked multi-head cross-attention; predicts kinetic parameters with a shared MLP and Softplus; and updates future RNA states with a fixed step size $\Delta t=0.5$. The predicted difference between future and current RNA states is the basis for cell/gene velocity.

The code implements the core model in `GRAVITY/gravity/models/gravity_model.py`, attention in `GRAVITY/gravity/models/core.py`, stage-1 training in `GRAVITY/gravity/train/cell_model.py`, stage-2 refinement in `GRAVITY/gravity/train/gene_model.py` and `gene_stage.py`, future-neighbor projection in `GRAVITY/gravity/tools/future.py`, BATC in `GRAVITY/gravity/analysis/batc.py`, and TF attention scoring in `GRAVITY/gravity/train/attention.py`.

### Paper Evidence

The paper evaluates GRAVITY on simulated and real datasets:

- **SERGIO simulations.** Four trajectory topologies are tested: linear, bifurcating, trifurcating, and quadrifurcating. GRAVITY reports clearer velocity directions than scVelo, CellDancer, and TFvelo, and its average BATC is 5.3% higher than the next-best method, scVelo. A prior-noise experiment adds one- to five-fold noise edges and reports relatively stable BATC values.
- **Human forebrain.** GRAVITY reports smoother velocity along the radial-glia-to-neuron trajectory and better phase portraits for genes such as CNTNAP2 and GNAO1 than the compared methods.
- **RPE-1 scEU-seq cell cycle.** GRAVITY reports the highest pseudotime Spearman correlation with FUCCI-derived cell-cycle phase (0.999), classifies 51/100 top cell-cycle genes into the correct turnover pattern versus 32/100 for CellDancer, and obtains a higher kinetic-pattern correlation (0.30 versus -0.08).
- **Mouse E15.5 pancreas.** The paper reports four endocrine differentiation directions, gene-wise kinetic correction after stage 2, cell-type GRN similarity matching endocrine lineage structure, insulin-pathway activity, Pdx1 target support (15/25 top targets validated by ChIP/literature), and perturbation simulations such as Ghrl inhibition and alpha-to-beta reprogramming factors.
- **E18 mouse embryonic brain.** GRAVITY identifies upper-layer and deeper-layer endpoints and assigns L5/L6 subterminal states using Bcl11b and Foxp2. Top 100 cell-type GRN edges are validated against scATAC-derived ChromVAR/JASPAR relationships with reported accuracy above 0.69 for selected cell types and 0.80 in IPC.

These results support GRAVITY as a strong trajectory-and-regulatory hypothesis generator on the selected datasets. They do not prove that every attention edge is causal or that perturbation predictions generalize outside the observed expression/state space.

### Code Match Assessment

**Overall fidelity: medium-high.** The local code implements the core architecture and training pipeline described in the paper:

| Paper element | Code status | Evidence |
|---|---|---|
| Expression + cell coordinate embeddings | Exact | `gravity_model.py:94-124` |
| Prior-aware cross-attention | Partial implementation detail | paper writes multiplication by `Net_prior`; code uses boolean `masked_fill(mask, -1e9)` before softmax in `core.py:80-83` |
| Softplus kinetic rates and fixed RNA update | Exact | `gravity_model.py:145-154` |
| Attention-weighted triplet cell-wise loss | Exact | `cell_model.py:149-198`, `losses.py:21-33` |
| Future-neighbor projection | Exact | `future.py:87-110` |
| Stage-2 parameter freezing | Exact | `gene_stage.py:307-329` |
| BATC metric | Exact | `batc.py:205-391` |
| TF score / attention export | Implemented | `cell_model.py:352-437`, `attention.py:70-177` |
| Reusable perturbation workflow | Not found in core package reads | paper Methods describes it, but no first-class package function was verified |
| Reusable pathway score function | Not found in core package reads | README/notebook context documents pancreas attention activity, but core reusable function was not verified |

### Reproducibility

**Rating: 3/5.**

Strengths:

- Public Python package is cloned locally and includes the main model, training stages, preprocessing, velocity plotting, BATC, and attention export utilities.
- README documents a pancreas demo with reference checkpoints, gene-order handling, and expected outputs such as `combine.csv`, `stage1.csv`, `future_positions.npy`, `stage2.csv`, attention exports, and plots.
- Core paper equations 1-14 have clear implementation anchors in the source.

Weaknesses:

- Full benchmark scripts for every paper figure are not obvious in the public package.
- The paper's in silico perturbation procedure and Eq. 15 pathway score are described in the manuscript, but direct reusable core functions were not found in verified source reads.
- Reproduction depends on large external datasets/checkpoints and GPU memory; gene-to-gene attention scales with selected gene count.
- The method depends heavily on a meaningful 2D embedding and prior network, because both training neighbors and future-cell anchors are built from embedding geometry.

### Main Limitations

GRAVITY's attention-derived GRNs should be read as model-based regulatory hypotheses. The paper validates selected edges and programs with ChIP, literature, ChromVAR/JASPAR, and known marker genes, but attention weights alone are not causal proof.

The perturbation analysis is explicitly confined to observed expression space: if a perturbed state does not exist in the original single-cell data manifold, GRAVITY cannot evaluate it reliably. The current implementation also focuses on intrinsic gene regulation and does not directly model chromatin accessibility, DNA methylation, spatial context, or cell-cell communication in the velocity model.

The package is strongest as a reusable implementation of the GRAVITY model and pancreas-style pipeline. It is weaker as a complete figure-reproduction repository for all manuscript analyses.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
