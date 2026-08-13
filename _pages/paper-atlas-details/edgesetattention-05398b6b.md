---
layout: default
permalink: /paper-atlas/edgesetattention-05398b6b/
title: "EdgeSetAttention"
nav: false
description: "ESA 不把“节点”当作 Transformer token，而把每条边写成一个 token；相邻边（共享端点）先通过带图结构掩码的注意力交换信息，再用无掩码自注意力补充全局联系，最后由一组可学习查询向量把可变长边集合汇总成图级表示。论文的核心不是发明新的注意力公式，而是把图结构变成注意力掩码，并把局部结构先验与全局注意力纵向组合。"
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
      <span>Nature Communications · 2025</span>
    </div>
    <h1>EdgeSetAttention</h1>
    <p>An end-to-end attention-based approach for learning on graphs</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-60252-z" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for EdgeSetAttention">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/davidbuterez/edge-set-attention" target="_blank" rel="noopener noreferrer" aria-label="Open code for EdgeSetAttention">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Edge-Set Attention（ESA）中文方法解读

### 一句话抓住方法

ESA 不把“节点”当作 Transformer token，而把每条边写成一个 token；相邻边（共享端点）先通过带图结构掩码的注意力交换信息，再用无掩码自注意力补充全局联系，最后由一组可学习查询向量把可变长边集合汇总成图级表示。论文的核心不是发明新的注意力公式，而是把图结构变成注意力掩码，并把局部结构先验与全局注意力纵向组合。

### 1. 为什么从边出发

给定图 $G=(V,E)$，节点 $i$ 的特征为 $\mathbf n_i$，边 $(i,j)$ 的特征为 $\mathbf e_{ij}$。ESA 为每条边构造

$$
\mathbf x_{ij}=\mathbf n_i\,\|\,\mathbf n_j\,\|\,\mathbf e_{ij}.
$$

在分子图里，这相当于把“键两端是什么原子、键本身是什么类型”装进同一个 token。代码在 `edge-set-attention/esa/models.py:305-318` 直接索引起点和终点节点特征，再拼接 `edge_attr`、经 MLP 投影，并将不同图的边序列补齐为批次张量。

把边当作集合元素有两个直接结果。第一，边的输入顺序不是语义，后续注意力和集合池化对同步置换保持等变/不变；第二，原图中的边邻接自然给出结构先验，不需要最短路、拉普拉斯特征或把图序列化。这里可把模型理解为在原图的线图上做注意力：原图的边成为线图的节点，两条边共享端点时在线图中相邻。

### 2. 掩码如何把图结构注入注意力

设两条边分别是 $(a,b)$ 与 $(c,d)$。只要

$$
a=c\;\lor\;a=d\;\lor\;b=c\;\lor\;b=d,
$$

它们就被视为相邻。代码 `masked_layers.py:49-70` 通过 source-source、target-target 和交叉端点比较生成布尔邻接矩阵，并将对角线清零。批处理版本再把各图的掩码放进同一个稠密张量。

掩码进入标准缩放点积注意力：

$$
\operatorname{Attn}(Q,K,V,M)=
\operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V.
$$

允许通信的位置取 $M_{rs}=0$，禁止的位置在实现中取很大的负数；softmax 后后者权重近似为零。`esa/mha.py:48-89` 生成独立的 Q/K/V 投影，并调用 xFormers 或 PyTorch 的高效 SDPA。因此 ESA 的 masked attention 仍是动态点积注意力，不是 GAT 那种把两个节点表示拼接后打分的静态形式。

一个小例子：若边集合是 $e_1=(1,2)$、$e_2=(2,3)$、$e_3=(4,5)$，则 $e_1$ 可看见 $e_2$，但看不见 $e_3$。经过一层 MAB，$e_1$ 已吸收节点 2 周围的关系；多层 MAB 可逐步扩展线图上的感受野。

### 3. MAB 与 SAB 为什么要混合

- MAB（Masked Attention Block）使用边邻接掩码，强调可靠的局部拓扑。
- SAB（Self-Attention Block）不传掩码，所有边可以直接通信，提供全局依赖。

`masked_layers.py:301-338` 中 `idx == 1` 才把 `adj_mask` 传入注意力，其余编码层传 `None`。`masked_layers.py:511-635` 则按配置字符串中的 `M`、`S`、`P` 组装网络；`P` 之前属于编码器，`P` 及其后的层属于解码/池化部分。

只堆 MAB 会把模型限制在线图的局部传播；只堆 SAB 又失去现成的拓扑先验。纵向交错二者，使模型先利用“共享端点”建立局部关系，再允许远距离边直接比较，也能在输入图缺边或连边不理想时绕过错误拓扑。论文表 5 的消融显示，最佳顺序随数据而变，但通常不是全 M，也不是机械的 MSMS 交替；不少强配置在前后放 SAB、中间放 MAB。

### 4. PMA：可学习的图级读出

编码器输出仍是一组边表示。图级预测需要把任意数量的边压成固定维度，ESA 使用 Pooling by Multi-head Attention（PMA）。设 $k$ 个可学习种子为 $S_k$，它们作为 query，全部边表示作为 key/value：

$$
H=\operatorname{MultiHead}(S_k,Z,Z).
$$

代码 `esa/mha.py:101-109` 把 `self.S` 定义成可学习参数；`models.py:234-257` 固定使用 32 个种子；`masked_layers.py:666-678` 在编码器输出上加输入残差，经过 PMA 后对 32 个种子取均值，再做线性层和 Mish。交叉注意力的代价为 $O(kL)$，其中 $L$ 是边数、$k=32$，比边-边全注意力小得多。

PMA 与普通 mean/sum readout 的差别是：每个种子可学会寻找一种对任务有用的边模式，再由多个种子共同形成图表示。论文方程给出 PMA 的种子表示，但代码中的 `out.mean(dim=1)` 是额外且关键的最终聚合步骤。

### 5. 完整数据流

1. 读取节点特征、`edge_index` 与边特征；可选地先把 RWSE/LapPE 拼到节点特征。
2. 对每条边拼接起点、终点和边属性，MLP 投影到隐藏维。
3. 按批次把边序列补齐到相同长度，并构造 $B\times L\times L$ 的边邻接掩码。
4. 按配置通过若干 MAB/SAB；编码器输出与最初的边嵌入相加。
5. PMA 的 32 个种子对边集合做交叉注意力；可在种子集合上继续使用 SAB。
6. 对种子维取均值，经输出层完成回归或分类。

左到右看论文图 4，就是“边集合 → 局部/全局注意力编码 → 学习式池化 → 图表示”。其中图 4A 是掩码 SDPA，4C/4D 分别是 SAB/MAB，4B 是 PMA，4E 才是完整模型堆叠。

### 6. 节点任务不是同一条 ESA 输出路径

论文在节点级基准中使用 NSA（Node-Set Attention）：token 改为节点，掩码改为原图节点邻接，且不需要 PMA，因为每个节点都要保留一个输出。代码 `models.py:320-325` 直接投影节点特征；`masked_layers.py:647-655` 构造节点掩码。论文也提到曾尝试 edge-to-node pooling，但当前实现面对百万级边图不可扩展，因此不能把节点任务结果解释为“边 token 经 PMA 后再还原到节点”。

### 7. 论文结果应该怎样读

作者覆盖 70 多个图级和节点级任务。重点不是每个数据集都绝对第一，而是同一套较简单的注意力骨架在分子、混合图、长程任务和异配节点分类中都很有竞争力。

- QM9 的 19 个性质中，论文报告 ESA 在 15 个上最佳；HOMO、LUMO、能隙与偶极矩等少数任务由 PNA 略胜。
- DOCKSTRING 的 5 个靶点中，ESA 在 4 个上最好，KIT 上 PNA 略优。
- 3D 原子系统原型和 QM9 高低保真迁移实验说明，边 token 可以加入距离等几何特征；迁移设置下 ESA 在 HOMO/LUMO 的归纳式和传导式任务均优于文中比较方法。
- 节点级的 NSA 覆盖同配、异配和最短路任务，说明“掩码注意力 + 全局注意力”的思想不依赖边 token，但这是相关架构变体。

这些结论来自论文的汇总实验，不等价于仓库在当前环境已复现实验。此工作区没有运行训练，也没有验证数据划分、随机种子和硬件条件下的数值复现。

### 8. 四张主图提供什么证据

- 图 1 比较 GAT 和 SAN，解释 ESA 为什么坚持标准 Q/K/V 点积注意力，并把结构作为加性掩码而非另一套手工打分器。
- 图 2 比较时间、显存、参数量与性能排名。ESA 通常比强 GNN/图 Transformer 更接近时间-性能帕累托前沿，但 GCN/GIN 仍更快、更省显存。
- 图 3 比较 HOMO 与 $u_0$ 的注意力 Gini 分布。作者把 HOMO 的更集中注意力解释为局部性质，把 $u_0$ 的较分散注意力解释为全局/广延性质；这是解释性相关证据，不是因果证明。
- 图 4 给出方法结构，是理解公式和代码的主入口。

### 9. 扩展性与真正的瓶颈

高效注意力内核可以避免显式保存完整注意力权重，但当前代码仍把边邻接掩码保存为稠密 $L\times L$ 矩阵，所以显存瓶颈仍是 $O(L^2)$。PMA 是 $O(kL)$，不是主要问题。论文估计若掩码能稀疏存储，规模可显著扩大；这是推算，不是当前代码已经实现的能力。实际使用时还要注意 `to_dense_batch` 的补齐长度由批次最大边数决定，大小差异悬殊的图混批会浪费显存。

### 10. 论文与代码的证据边界

1. 论文公式与图 4描述 pre-LN；代码同时支持 pre/post-LN，而 `esa/train.py` 的 CLI 默认是 `post`。因此不能仅凭论文公式断言默认命令运行的是 pre-LN。
2. 代码在注意力输出中使用 `out + Mish(fc_o(out))`，PMA 后还会对种子取均值；这些实现细节没有在论文主公式中完整展开。
4. 补充材料以 PDF 保存，当前证据索引以主论文 Markdown、主图和直接代码为主；未把补充 PDF 全文转换成可逐行引用的 Markdown。

### 11. 最短阅读路线

先看论文图 4，再读本文第 2–5 节；然后对照 `esa/models.py:286-325` 看 token 构造，`esa/masked_layers.py:49-70` 看边邻接，`esa/masked_layers.py:301-338` 看 M/S 分流，最后看 `esa/mha.py:48-109` 与 `esa/masked_layers.py:645-678` 串起注意力、PMA 和输出。这样可以把“论文概念—公式—真实张量流”一次对应起来。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ESA: summary.md — Paper Summary

### Motivation & Novelty

#### Problem
Graph neural networks (GNNs) dominate structured data learning but rely on **message passing** — an iterative, neighbourhood-aggregation scheme — that suffers from over-smoothing (representations blur with depth), over-squashing (information compression through bottleneck edges), and limited expressiveness bounded by the 1-WL isomorphism test. The standard fix is simple but suboptimal readout functions (sum/mean/max) that require nodes to embed all graph-level information.

Graph transformers (Graphormer, TokenGT, GraphGPS, SAN, Exphormer, Polynormer) attempt to replace message passing with attention but introduce new problems: expensive preprocessing (Floyd-Warshall shortest paths, centrality encoding: O(n³)), positional/structural encodings that break permutation invariance or require precomputed eigenvectors, virtual nodes and global tokens, and dependence on approximate attention (Performer). Despite the added complexity, **Tönshoff et al. (NeurIPS 2023) and Platonov et al. (NeurIPS 2023) showed that tuned GNNs match or outperform most graph transformers on standard benchmarks**.

#### Limitations of Prior Work
| Method | Journal/Year | Limitation |
|---|---|---|
| GCN | ICLR 2017 | Over-smoothing, weak expressiveness |
| GAT | ICLR 2018 | Static attention, limited expressiveness (1-WL) |
| GATv2 | ICLR 2022 | Dynamic attention but 2× parameter cost |
| PNA | NeurIPS 2020 | Hand-crafted aggregators, dataset-specific degree histogram |
| SAN | NeurIPS 2021 | Convex combination of graph + complement requires tunable γ; doubles compute |
| Graphormer | NeurIPS 2021 | O(n³) preprocessing (Floyd-Warshall), quadratic memory for edge features |
| TokenGT | NeurIPS 2022 | Requires positional encodings (breaks permutation invariance), tested on 1 dataset |
| GraphGPS | NeurIPS 2022 | Hybrid (not purely attention), requires structural/positional encodings |
| Exphormer | ICML 2023 | Needs expander graph preprocessing, approximate attention via expander graphs |
| Polynormer | ICLR 2024 | Hybrid local+global attention, gating mechanism, not purely attention-based |

#### Novelty
ESA treats **graphs as sets of edges** and uses a purely attention-based architecture with two innovations:
1. **Masked attention**: the edge adjacency matrix (two edges adjacent if sharing a node = line graph) serves as an inductive bias with no preprocessing
2. **Learnable readout (PMA)**: replaces fixed sum/mean/max with learned cross-attention over k=32 seed vectors

No positional encodings, no virtual nodes, no graph preprocessing beyond building the edge set. The approach is domain-agnostic.

---

### Method Overview

#### Algorithmic Framework

1. **Edge tokenization**: Each edge $(i,j)$ is represented as $\mathbf{x}_{ij} = \mathbf{n}_i \,\|\, \mathbf{n}_j \,\|\, \mathbf{e}_{ij}$ — concatenation of source/target node features and edge attributes
2. **MLP input projection**: Edge tokens projected to hidden dimension $d$
3. **Encoder** (interleaved MAB/SAB sequence): Masked attention blocks (MAB) use the edge adjacency mask restricting attention to adjacent edges; Self-attention blocks (SAB) allow global information flow across all edges
4. **PMA pooling** (graph-level tasks): 32 learnable seed vectors attend to all edge representations via cross-attention; seeds are averaged to produce graph embedding
5. **Output MLP**: Predicts graph or node properties

#### Key Technical Components
- **Edge adjacency mask**: Efficiently computed via tensor comparisons (source-source, target-target, cross-node matches). No Python loops — pure tensor ops via PyTorch Geometric
- **Flexible layer order**: Model configured as string of M (masked), S (self-attention), P (pooling) types, e.g., `MMMSP`. Ablation shows front-loaded self-attention layers followed by masked layers typically optimal
- **Memory-efficient attention**: xformers or PyTorch SDPA backend with chunking; $O(L)$ memory for attention computation (bottleneck is dense mask at $O(L^2)$)
- **NSA variant**: For node-level tasks, nodes replace edges as tokens; masking follows original graph adjacency

#### Biological Assumptions
For molecular tasks: bond-centric representation aligns with chemistry (bond formation/breakage drives reactions; bond type carries most predictive information about molecular properties). Line graph connectivity naturally captures chemical motifs like rings, triangles, and cliques that are critical for drug-likeness and property prediction.

---

### Evaluation

#### Datasets (70 total)
| Domain | Benchmarks |
|---|---|
| Quantum chemistry | QM9 (19 targets), PCQM4MV2 (3.3M molecules) |
| Molecular docking | DOCKSTRING (5 targets, 260K molecules) |
| Physical chemistry | MoleculeNet: ESOL, FreeSolv, Lipo (regression); BBBP, BACE, HIV (classification) |
| Drug discovery | NCI1, NCI109 (anti-cancer screening) |
| Long-range | PEPTIDES-STRUCT, PEPTIDES-FUNC (LRGB, longest avg. shortest path) |
| Vision graphs | MNIST, CIFAR10, MalNetTiny |
| Bioinformatics | ENZYMES, PROTEINS, DD |
| Social | IMDB-B/M, twitch_egos, reddit_threads |
| Synthetic | SYNTHETIC, SYNTHETICnew, Synthie |
| Node classification | PPI, Cora, CiteSeer, ROMAN EMPIRE, AMAZON RATINGS, MINESWEEPER, TOLOKERS, SQUIRREL, CHAMELEON |
| Shortest path | ER (15K nodes), ER (30K nodes) |
| 3D atomic | OCP (Open Catalyst Project) subset |
| Transfer learning | QM9 HOMO/LUMO with GW-level DFT labels |

#### Baselines
- **GNNs**: GCN, GAT, GATv2, PNA, GIN, DropGIN (all tuned)
- **Graph transformers**: Graphormer (NeurIPS 2021), TokenGT (NeurIPS 2022), GraphGPS (NeurIPS 2022), Exphormer (NeurIPS 2023), Polynormer

#### Key Results
| Benchmark | ESA | Best Baseline | Notes |
|---|---|---|---|
| QM9 (15/19 targets) | **Best** | PNA (4 targets) | Massive advantage on thermodynamic props (U₀ RMSE: 4.78 vs 14.50) |
| PCQM4MV2 | MAE **0.0235** | OGB leaderboard best: 0.0671 | 3× better than state-of-art; general-purpose, no 3D info |
| ZINC full | MAE 0.027 | GraphGPS 0.024 | Slightly below without encodings; ESA+RWSE: **0.015** (SOTA) |
| PEPTIDES-STRUCT | MAE **0.239** (ESA+) | GPS: 0.247 | SOTA with tuning |
| MNIST | Acc **98.92%** (ESA+) | GraphGPS: ~98% | SOTA |
| MalNetTiny | Acc **94.8%** (ESA+) | Previous best: ~93% | SOTA |
| Shortest path ER-15K | MCC **0.92** | PNA: 0.54 | Dramatic margin; other transformers fail (OOM or MCC≈0) |
| Heterophilous (CHAMELEON) | MCC **0.39** | GPS: 0.30 | +30% over best baseline |
| Transfer learning (HOMO trans.) | RMSE **0.119** | PNA: 0.121 | Best in all 4 transfer settings |

#### Scaling
- **Time**: ESA is 2nd fastest (after GCN/GIN), faster than PNA and GATv2
- **Memory**: Slightly above GCN/GIN; substantially below PNA, DropGIN, GATv2
- **Parameters**: Among lowest (comparable to GCN, far below PNA/GATv2)

---

### Reproducibility: 4/5

**Justification**: Strong reproducibility overall. GitHub repository provides all code, dataset loaders, and configuration system. Datasets are public (PyTorch Geometric, Figshare, HuggingFace). However:

**Strengths**:
- Full argument configs can be serialized to JSON and reloaded
- 5-run statistics reported for all main tables
- PCQM4MV2 training takes >24h (single run reported, which is standard)
- Clean separation of ESA, GNN baselines, and transformer baselines in repo

**Weaknesses / Pitfalls**:
- `xformers` version compatibility is sensitive; must match CUDA version
- `bitsandbytes` requires specific CUDA setup for 8-bit optimizer
- `flash-attn` needed for SwiGLU in GatedMLPMulti
- `admin_torch` for post-LN residuals is a less common dependency
- OCP evaluation requires `fairseq` (not listed in requirements)
- `pre_or_post` default in `train.py` is `post` but paper describes pre-LN — may reproduce slightly different results
- Hyperparameter configurations are not provided for all 70 experiments; researchers must tune from scratch for new datasets
- `max_edge_global` / `max_node_global` requires dataset-level preprocessing pass before training

**Environment**: Python 3.9+, PyTorch 2.0+, PyTorch Geometric 2.3+, xformers 0.0.20+, CUDA 11.8+ recommended

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
