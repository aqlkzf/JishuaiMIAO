---
layout: default
permalink: /paper-atlas/cellnest-72bad038/
title: "CellNEST"
nav: false
description: "CellNEST 面向空间转录组中的细胞间通信（cell–cell communication, CCC）推断。输入可以是细胞级数据，也可以是 Visium spot；输出不是笼统的“某两类细胞可能通信”，而是带空间位置、方向、配体–受体身份和强度排序的单细胞/单 spot 通信边，并进一步组合成两跳中继网络（relay network）。论文发表于 Nature Methods 2025，DOI 为 10."
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
      <span>Cell-Cell Communication</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>CellNEST</h1>
    <p>CellNEST reveals cell–cell relay networks using attention mechanisms on spatial transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/schwartzlab-methods/CellNEST" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellNEST">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellNEST 方法详解：从空间转录组到细胞间中继网络

### 1. 它要解决什么问题？

CellNEST 面向空间转录组中的细胞间通信（cell–cell communication, CCC）推断。输入可以是细胞级数据，也可以是 Visium spot；输出不是笼统的“某两类细胞可能通信”，而是带空间位置、方向、配体–受体身份和强度排序的单细胞/单 spot 通信边，并进一步组合成两跳中继网络（relay network）。论文发表于 *Nature Methods* 2025，DOI 为 `10.1038/s41592-025-02721-3`。

论文认为现有方法主要有四类不足（`paper.md:18-39`）：

1. 许多方法只看转录组共表达，缺乏真实空间邻近约束，因此假阳性/假阴性较高；
2. Scriabin（*Nature Biotechnology*, 2024）和 GraphComm（*bioRxiv*, 2023）先在解离的 scRNA-seq 上推断，再把结果映射回空间，空间位置不是推断本身的一部分；
3. NICHES（*Bioinformatics*, 2023）、COMMOT（*Nature Methods*, 2023）、CellChat、Giotto 等方法往往依赖共表达、通路先验或细胞类型/簇级汇总，难以同时给出单细胞、具体配体–受体和全组织排序；
4. 现有流程通常输出单条配体–受体边，而真实信号可能沿 $i\rightarrow j\rightarrow k$ 继续传递，形成“配体–受体–配体–受体”中继模式。

CellNEST 的核心想法是：先把所有“空间上可能、表达上也可能”的配体–受体关系建成候选图，再让无监督图注意力模型从整张组织图的重复结构中学习哪些边更重要。注意力高的边被解释为更可能的通信，连续的高分边则可组成中继网络。

### 2. 输入、输出与核心假设

#### 输入

- 空间表达矩阵：$A\in\mathbb{R}^{N\times M}$，$N$ 为细胞/spot 数，$M$ 为基因数；
- 每个细胞/spot 的二维或三维坐标；
- 配体–受体数据库；默认数据库合并 CellChat 与 NicheNet，共 12,605 对；
- 活跃基因百分位阈值 `--threshold_gene_exp`，默认 98；
- 空间邻域阈值 `--neighborhood_threshold`，或代码支持的 kNN 邻域（`paper.md:231-243`; `data_preprocess_CellNEST.py:25-67`）。

#### 输出

- 每条候选通信边的 sender、receiver、ligand、receptor、rank、attention score；
- 过滤后的强通信图及其连通分量；
- 配体–受体丰度直方图和空间可视化；
- 两跳中继模式及参与的三个细胞/spot；
- 可选的中继细胞类型组成与胞内信号置信度路径（`paper.md:297-345`）。

#### 核心假设

输入图的一条边不是“已经发生的通信”，只是空间和表达均允许的候选关系。CellNEST 假设：真正重要的通信会在组织中形成可重复的局部/全局图模式，无监督图编码器可以通过上下文学习这些模式，再用注意力对候选边排序。

这不是因果证明。空间转录组是静态表达快照，模型不能证明第一个受体的激活导致了中间细胞产生第二个配体；论文把中继结果定位为待实验验证的假设（`paper.md:216`）。

### 3. 从输入到输出的完整计算流程

```text
原始计数 + 空间坐标 + 配体–受体数据库
                 │
                 ▼
      基因过滤、分位数归一化、逐点活跃基因阈值
                 │
                 ▼
   建立有向候选多重图：i --(ligand,receptor)--> j
   节点特征：默认 one-hot
   边特征：距离、配体×受体表达、LR 关系 ID
                 │
                 ▼
       两层 edge-aware GATv2 风格编码器
               + DGI 无监督训练
                 │
                 ▼
       保存两层 normalized / unnormalized attention
                 │
                 ▼
   多次训练结果做几何 rank product，并合并两层
                 │
                 ▼
     过滤高分 CCC → 连通分量、组织图、直方图
                 │
                 ▼
       枚举 i→j→k 两跳中继，并可计算置信路径
```

### 4. 第一步：预处理和活跃基因判定

代码读取 Visium/Space Ranger 或 AnnData，按最少细胞数过滤基因，提取空间坐标，并默认执行分位数归一化（`data_preprocess_CellNEST.py:96-178`）。

关键点是：活跃阈值不是全组织共享一个数，而是对每个细胞/spot 单独计算。对第 $i$ 个顶点，代码取该行表达的 `threshold_gene_exp` 百分位作为 `cell_percentile[i]`。如果这个百分位仍等于该行最小值，代码逐步提高百分位，避免零值过多时几乎所有基因都被判为活跃（`data_preprocess_CellNEST.py:363-382`）。

因此，一个配体在 sender 中、一个受体在 receiver 中是否活跃，取决于各自顶点的局部阈值，而不是简单比较全局平均表达。

### 5. 第二步：建立候选通信多重图

对空间上满足邻域条件的有序顶点 $(i,j)$，如果 ligand $l$ 在 $i$ 中活跃、对应 receptor $r$ 在 $j$ 中活跃，就加入一条 $i\rightarrow j$ 有向边。同一对顶点可以由多个配体–受体对连接，所以这是多重图（`paper.md:237-243`; `data_preprocess_CellNEST.py:407-467`）。

每条边有三个特征：

$$
\vec e_{i,j}=[d_{i,j},\;A_{i,l}A_{j,r},\;\mathrm{LR\_id}(l,r)].
$$

也就是：

1. 物理距离；
2. 配体表达与受体表达的乘积；
3. 该配体–受体对在数据库中的整数编号。

代码把 `[row_col, edge_weight, lig_rec, total_num_cell]` 写入 `*_adjacency_records`，其中 `edge_weight` 正是上述三维向量（`data_preprocess_CellNEST.py:474-506`）。

论文默认用 one-hot 节点身份。源码建立 $N\times N$ 单位矩阵后随机打乱行，再作为 `Data.x`；每行仍是唯一 one-hot，只是节点与任意身份维的对应被重排。源码也允许用表达矩阵或用户提供的节点特征，这是论文默认描述之外的扩展（`CCC_gat.py:16-61`）。

### 6. 第三步：带边特征的图注意力

论文的 Eq. 1 写作：

$$
{\alpha}_{i,j}=\operatorname{Tanh}\left(\vec a^{T}\left[W_v\vec h_i+W_v\vec h_j+W_e\vec e_{i,j}\right]\right),
$$

随后对进入顶点 $i$ 的边做 Softmax：

$$
{\alpha}'_{i,j}=\operatorname{Softmax}_{j\in N_i}({\alpha}_{i,j}),
$$

并聚合邻居消息：

$$
\vec h'_i=\sigma\left(\sum_{j\in N_i}{\alpha}'_{i,j}W_v\vec h_j\right).
$$

直观理解：模型同时看 receiver、sender 和这条边的三维特征，再决定这条候选关系在当前组织图中有多重要。Softmax 后的分数适合局部消息传递；论文最终用于全组织边排序的是 Softmax 前的 unnormalized attention，因为它们可跨邻域比较（`paper.md:258-285`）。

源码在 `CCC_gat.py:64-113` 中堆叠两层定制 `GATv2Conv`，两层都接收 `edge_dim=3`，并保存 normalized 与 unnormalized attention。第二层后还有 PReLU。

#### 论文 tanh 方程与 GATv2Conv 源码并不完全相同

这是理解实现时最重要的细节之一：

- 论文 Eq. 1 是先做 $\vec a^T[\cdots]$，再在标量上做 `Tanh`；
- 源码先对“receiver 变换 + sender 变换 + edge 变换”的向量做 `tanh`，再与注意力向量点积（`GATv2Conv_CellNEST.py:268-291`）；
- 论文用同一个 $W_v$ 表示 sender/receiver 变换；源码默认 `share_weights=False`，使用独立的 `lin_l` 和 `lin_r`（`GATv2Conv_CellNEST.py:112-163,185-215`）；
- 论文的单个更新式没有写出源码的“两层 + 第二层后 PReLU”结构。

因此，tanh、节点/边加和、Softmax 和加权聚合这些核心思想吻合，但 Eq. 1 只能判为 **Partial**，不能称为源码的逐项精确公式。

### 7. 第四步：用 DGI 做无监督训练

因为没有已知的真/假 CCC 标签，CellNEST 把两层注意力编码器放进 Deep Graph Infomax：

- 正分支编码真实输入；
- 负分支编码 corruption 后的输入；
- 对节点嵌入求均值并经 sigmoid 得到 summary vector；
- DGI 判别器拉近真实节点嵌入与 summary 的关系，并区分负样本（`CCC_gat.py:140-200`）。

默认训练参数包括 60,000 epoch、隐藏维度 512、1 个 attention head、dropout 0、Adam 学习率 $10^{-5}$。代码保存最低损失 checkpoint、节点嵌入，以及两层的注意力 bundle（`run_CellNEST.py:19-35`; `CCC_gat.py:192-253`）。

#### 论文写“打乱边”，源码实际“打乱节点特征”

论文在 `paper.md:288-294` 中把 corrupted graph 描述为对边做随机 permutation/shuffling，形成 $G_C=(V,E')$。

但标准源码是：

```python
x = data.x[torch.randperm(data.x.size(0))]
return my_data(x, data.edge_index, data.edge_attr)
```

即随机置换 `data.x` 的行，同时保留原来的 `edge_index` 和 `edge_attr`（`CCC_gat.py:128-137`）。split 分支也采用同类特征置换（`CCC_gat_split.py:264-278`）。因此 released code 的负样本是“固定图结构上的节点特征 permutation”，不是论文所写的 shuffled edges。这是实质性的 **Partial** 差异。

### 8. 第五步：多次训练、两层注意力与 rank product

Adam 和随机初始化会导致不同 run 的分数略有变化，所以论文默认运行五次。后处理对每个 attention layer 分别执行：

1. 读取每个 run 的 unnormalized attention；
2. 在 run 内缩放分数；
3. 按每个 run 的分数给边排名；
4. 对跨 run 的名次取几何 rank product；
5. 对分数乘积先加 `0.01`，避免零值使乘积归零；
6. 缩放两个 layer 的结果，再独立筛选或整合（`output_postprocess_CellNEST.py:100-303`）。

论文分析默认保留 top 20%。当两个 layer 独立筛选时，代码取两层 top 边的并集；同一条边若两层都出现，则保留较好的 rank（`output_postprocess_CellNEST.py:246-303`）。

### 9. 第六步：从通信边到两跳中继网络

过滤后的强边先用于连通分量、组织网络和配体–受体丰度图。中继提取脚本则建立每个节点的 outgoing-edge 表，并枚举：

$$
i\xrightarrow{l_1-r_1}j\xrightarrow{l_2-r_2}k,
$$

同时排除 $k=i$ 或 $k=j$ 的返回路径，统计 `l1-r1 to l2-r2` 的频次并保存三元组细胞信息（`extract_relay_cellnest.py:141-216`）。

论文方法部分描述了可递归到预定义 hop 数的 DFS，并称用户可扩展到 $n$ hops（`paper.md:330-333`）；但在本次检查的主 relay 脚本中，只找到固定两跳枚举，通用 $n$-hop 实现为 **Not found**。这不影响论文实际展示的两跳结果，但限制了“任意深度”可复现性。

### 10. 第七步：给中继模式增加胞内证据

对 $(l_1,r_1)\rightarrow(l_2,r_2)$，置信度模块尝试寻找从第一个受体 $r_1$ 到调控第二个配体 $l_2$ 的转录因子的胞内路径：

1. 从 TF–target 数据库查询调控 $l_2$ 的 TF；
2. 以 0.5、0.4、0.3、0.2、0.1 五个 PPI 置信度阈值构建有向图；
3. 用 BFS 找从 $r_1$ 到任一候选 TF 的第一条路径；
4. 相乘路径上的 PPI 分数，再乘 TF–target 分数；
5. 保留总分最高的路径（`relay_confidence.py:10-179`; `paper.md:342-345`）。

这个分数回答的是“数据库中是否存在一条相容的胞内链路”，而不是“该链路在样本中已被实验观测”。

### 11. 论文如何评估 CellNEST？

#### 数据与基线

论文覆盖 Visium、MERFISH、3D MERFISH、Visium HD；人淋巴结、小鼠下丘脑、肺腺癌、结直肠癌和两例 PDAC；另构建 21 种 synthetic setup，包括规则网格、均匀分布、混合分布、不同噪声、relay/nonrelay 和 diffusion 模型（`paper.md:39,74-197,315-329`）。

淋巴结比较包括 NICHES、COMMOT、NicheCompass、CytoSignal、CellChat、Giotto 和 TWCOM；synthetic heatmap 使用 balanced accuracy 比较 CellNEST 与 COMMOT、CytoSignal、NICHES、Giotto、TWCOM、CellChat（Fig. 3）。

#### 主要结果

- 人淋巴结：`CCL19–CCR7` 在 T-cell zone 的 top-20%-attention 结果中丰度第二，并且空间定位明显；其注意力高，但原始共表达并不高（`paper.md:77-88`; Fig. 2）。
- 中继：`CCL19–CCR7 to CCL21–CXCR4` 在 T-cell zone 中高频出现；论文报告其置信度高于随机组合（`paper.md:91-102`; Fig. 3）。
- synthetic：Fig. 3i–j 中 CellNEST 在展示的多种条件下 balanced accuracy 接近色标高端。
- MERFISH：在 female parent 样本中识别到 `Oxt–Oxtr`，展示单细胞 neuron–microglia 边、两跳 Pnoc 相关 relay 和 3D 跨切片通信（`paper.md:105-125`; Fig. 4）。
- PDAC：两位患者共享多个高排名信号；`PLXNB2–MET/MST1R` 偏向 classical 区域，独立 organoid 中 classical 组 MET 表达更高（`paper.md:161-195`; Figs. 5–6）。
- LUAD 与结直肠癌扩展图显示通信分量和 relay 可以局部化到肿瘤、基质或侵袭区域（`paper.md:128-149,567-580`）。

### 12. 如何正确理解 CellNEST 的贡献

CellNEST 的贡献可以概括为三层：

1. **表示层**：把空间、表达和配体–受体身份统一为有向多重图；
2. **学习层**：在无标签条件下用 DGI 训练 edge-aware attention encoder，并用 unnormalized attention 做全组织边排序；
3. **结构层**：把连续通信边组合为可定位、可计数、可加数据库置信度的两跳 relay。

最值得借鉴的设计是“先宽松生成候选，再用组织级图模式排序”，而不是直接把高共表达等同于通信。最需要谨慎的地方是：attention 是模型重要性分数，不是物理概率；relay 是统计和数据库支持的候选链路，不是因果链；论文公式/文字与 released code 在 tanh 位置、source/target 权重共享、DGI corruption 和通用 $n$-hop 支持上存在明确差异。

### 13. 可复现性结论

本地代码快照对应 commit `2fd4f875ec2916ce51f674342aec1f59596c79ed`。主流程的图构建、两层 attention+DGI、注意力导出、跨 run rank product、两跳 relay 和置信度评分都有直接源码锚点，整体组件级一致性为 **high**。

仍需保留的缺口：未执行依赖安装、GPU 训练或数值复现；仓库内未找到自动化测试；通用 $n$-hop relay 实现 Not found；补充材料 Markdown 的大部分正文因字体编码而乱码，但原始 54 页 PDF 已保留。完整匹配表见 `doc_code.md`，英文技术流程见 `doc_method.md`，图像证据见 `figure_analysis.md`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellNEST

**Paper:** *CellNEST reveals cell–cell relay networks using attention mechanisms on spatial transcriptomics* — *Nature Methods* (2025), DOI `10.1038/s41592-025-02721-3`.

### Problem

Most cell–cell communication (CCC) methods infer isolated ligand–receptor pairs, often at cell-type or cluster resolution, and many either ignore spatial position during inference or use it only after predictions have been made. The paper argues that these choices contribute to high false-positive/false-negative rates, loss of autocrine/juxtacrine/paracrine context, and an inability to detect multi-cell relay patterns (`paper.md:18-39`).

Examples named by the paper include Scriabin (*Nature Biotechnology*, 2024) and GraphComm (*bioRxiv*, 2023), which start from dissociated scRNA-seq and map results to space; NICHES (*Bioinformatics*, 2023), which summarizes local coexpression into niches; COMMOT (*Nature Methods*, 2023), which uses collective optimal transport but requires pathway priors; NicheCompass (*Nature Genetics*, 2025), CLARIFY (*Bioinformatics*, 2023) and TENET (*Journal of Molecular Biology*, 2024), which the authors describe as binary interaction models; and cell-type/cluster-level approaches such as Giotto (*Genome Biology*, 2021), TWCOM (*Bioinformatics Advances*, 2024) and spatial CellChat (*Nature Protocols*, 2024) (`paper.md:27-33,406-420`). None is presented as directly recovering ligand–receptor-specific relay networks at single-cell/spot resolution.

### Proposed method

CellNEST turns a spatial transcriptomic sample into a directed ligand–receptor multigraph. Cells or spots are vertices; a candidate edge is created when sender ligand and receiver receptor genes are active and the pair satisfies a spatial neighborhood rule. Each edge carries distance, ligand–receptor coexpression and relation identity; vertices are one-hot encoded by default (`paper.md:225-243`).

A two-layer edge-aware graph attention encoder is trained without CCC labels through Deep Graph Infomax (DGI). CellNEST ranks candidate edges using globally comparable unnormalized attention, ensembles repeated runs with rank products, filters high-ranked edges and forms communicating tissue components. It then enumerates frequent two-hop patterns $i\rightarrow j\rightarrow k$ and can score a proposed relay by searching PPI and TF-target graphs for an intracellular receptor-to-next-ligand path (`paper.md:246-345`).

```text
spatial counts + coordinates + LR database
        -> candidate directed LR graph
        -> two-layer edge-aware GAT encoder inside DGI
        -> unnormalized attention per edge
        -> multi-run/layer rank aggregation
        -> top CCC edges, components and two-hop relays
        -> optional intracellular confidence paths
```

### Evaluation and main evidence

The paper evaluates CellNEST across Visium, MERFISH, 3D MERFISH and Visium HD; human lymph node, mouse hypothalamus, lung adenocarcinoma, colorectal cancer and two pancreatic ductal adenocarcinoma (PDAC) samples; and 21 synthetic configurations spanning equidistant, uniform and mixed spatial distributions, injected noise, relay/nonrelay settings and diffusion-based models (`paper.md:39,74-197,315-329`).

Baselines include NICHES, COMMOT, NicheCompass, CytoSignal, CellChat, Giotto and TWCOM for the lymph-node analysis, with broader synthetic comparisons shown against COMMOT, CytoSignal, NICHES, Giotto, TWCOM and CellChat. The primary synthetic metric shown in Fig. 3 is balanced accuracy (`paper.md:88-102`; `figure_03.png`).

Key results reported and visibly supported by the local figures include:

- In human lymph node, `CCL19–CCR7` is the second most abundant top-20%-attention signal in T-cell zones and is sharply localized there even though its raw coexpression is not among the highest; the paper reports Fisher's exact $P=9.16\times10^{-224}$ and higher CCR7-downstream expression in T-cell zones ($P=6.42\times10^{-164}$) (`paper.md:77-88`; Fig. 2).
- The lymph-node relay `CCL19–CCR7 to CCL21–CXCR4` is abundant and localized to T-cell zones. Relay confidence scores are reported as higher than random in that analysis ($P=4.5\times10^{-2}$) (`paper.md:91-102`; Fig. 3).
- Across the displayed synthetic and diffusion-based benchmarks, the CellNEST heatmap row remains near the top of the balanced-accuracy scale across conditions, whereas competitors vary substantially (Fig. 3i–j).
- MERFISH analyses recover context-specific signals such as `Oxt–Oxtr` in a female parent mouse, single-cell neuron–microglia communication, localized opioid-related relay patterns and 3D cross-section edges (`paper.md:105-125`; Fig. 4).
- Two PDAC samples share several high-ranked signals, including `LGALS3–ITGB4`, `PLXNB2–MET/MST1R`, `PTPRF–RACK1`, `TGFB1–ITGB5` and `TIMP1–LRP1`; `PLXNB2–MET/MST1R` is associated with classical regions, and independent organoids show higher MET expression in classical than basal-like samples ($P=3.18\times10^{-2}$) (`paper.md:161-195`; Figs. 5–6).
- Extended-data images show region-specific LUAD signals and relays, and a Visium HD colorectal sample in which an invasive-cancer-aligned communication component and a stromal `C3–CXCR4 to C3–LRP1` relay are spatially localized (`paper.md:128-149,567-580`).

### Interpretation

CellNEST's main innovation is not simply another ligand–receptor coexpression score. It uses spatially constrained candidate relations, an unsupervised graph encoder and recurring graph context to prioritize edges, then explicitly promotes multi-edge relay patterns to first-class outputs. This allows a weakly expressed but spatially coherent signal to rank above high-coexpression alternatives.

The outputs remain putative. Spatial transcriptomics is a static expression snapshot, so CellNEST cannot determine that the first receptor actually caused production of the second ligand. Relay confidence adds database consistency, not temporal or perturbational proof (`paper.md:216`).

### Reproducibility assessment — 4/5

Strengths:

- public primary repository and archived release; canonical local snapshot is commit `2fd4f875ec2916ce51f674342aec1f59596c79ed`;
- public CellNEST-Interactive repository, Singularity route, user guides, example commands, processed databases and cited public datasets;
- direct source correspondence is high for graph construction, two-layer attention/DGI training, attention export, rank-product postprocessing, two-hop relay extraction and relay confidence scoring;
- all eight article figures and the 54-page supplementary PDF are retained locally.

Important qualifications:

- the paper describes DGI corruption as shuffled edges, but released code permutes node-feature rows while retaining graph edges and attributes;
- paper Eq. 1 places tanh outside the attention dot product and uses a shared $W_v$, whereas the custom GATv2-style implementation applies tanh before the dot product and defaults to separate source/target transformations;
- the inspected relay script implements fixed two-hop enumeration; the paper's general recursive $n$-hop implementation was Not found;
- no automated test suite was found, and this analysis did not install dependencies or rerun training/numerical benchmarks;
- much of the extracted supplementary Markdown is font-encoded/garbled, although the original supplementary PDF is preserved.

Overall code–paper fidelity is **high at the component and pipeline level**, with the above equation-, corruption- and relay-generality differences explicitly documented in `doc_code.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
