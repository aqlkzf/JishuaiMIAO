---
layout: default
permalink: /paper-atlas/gleam-006a47f7/
title: "GLEAM"
nav: false
description: "GLEAM 把单细胞缺失模态预测改写成异质图上的链接预测：细胞和基因、峰、染色质互作或电生理指标都是节点，已测量值是带权的 cell–feature 边；模型先借助跨模态相似细胞传播信息，再预测未观测 cell–feature 边是否存在以及边权是多少。它还用分裂保形预测给出零/非零预测集合和非零数值区间，使预测能进入带不确定性的下游分析。"
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
      <span>Manuscript · 2026</span>
    </div>
    <h1>GLEAM</h1>
    <p>GLEAM links single-cell 3D genome and cellular electrophysiology with calibrated uncertainty</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GLEAM 方法中文解读

### 一句话理解

GLEAM 把单细胞缺失模态预测改写成异质图上的链接预测：细胞和基因、峰、染色质互作或电生理指标都是节点，已测量值是带权的 cell–feature 边；模型先借助跨模态相似细胞传播信息，再预测未观测 cell–feature 边是否存在以及边权是多少。它还用分裂保形预测给出零/非零预测集合和非零数值区间，使预测能进入带不确定性的下游分析。

### 为什么需要这种图表示

许多单细胞技术不能在同一个细胞上共同测量。例如 Patch-seq 同时得到转录组、电生理和形态，而 sn-m3C-seq 需要破坏细胞核来测量甲基化与三维染色质结构。直接把两个矩阵拼接，会遇到细胞不配对、特征类型不同、稀疏度不同和某些模态没有自然共享特征的问题。

GLEAM 用两类节点统一这些对象：cell 节点代表各数据集中的细胞，feature 节点代表每个模态的测量维度。cell–cell 边表达跨模态或模态内相似性，cell–feature 边的权重就是观测值。于是“给一个细胞补出另一个模态”变成“预测这个细胞与目标模态每个 feature 节点的边”。这种抽象不要求 feature 一定是基因，因此能容纳染色质互作和电生理指标。

### 第一步：把不同模态的细胞放进共同坐标系

若模态之间存在共享表示，例如 RNA 表达和 ATAC gene-activity score，论文先用 CCA 得到初始联合嵌入，再建跨模态近邻图。若没有直接共享特征，则使用可同时连接两侧的桥接数据；论文的关键应用以 Patch-seq 转录组为桥，将 sn-m3C-seq 与电生理联系起来。

初始近邻图随后用加权 Metapath2vec 细化。随机游走按边权而不是均匀采样，推荐元路径让游走同时经过模态内和跨模态边。负采样目标拉近实际上下文节点、推远随机节点。代码 `emb.py:18-66` 实现加权 Metapath2vec，`emb.py:251-311` 完成初始近邻、嵌入细化和重建近邻图。

需要注意，外部新数据并不是训练图中的节点。论文补充材料描述先把新细胞投影到训练数据的 CCA/Seurat 空间，再学习线性映射进入 GCN 编码空间，最后调用已训练解码器。当前 Python 包没有完整封装这条外部投影链，因此包内 `predict` 不能等同于论文全部外推实验流程。

### 第二步：构造 cell–feature 异质图

对非零膨胀模态，代码把每个 cell–feature 组合建成带权边。对 RNA、ATAC 等稀疏模态，模型把任务拆成两部分：先判断边是否存在（零或非零），再只对非零边预测连续权重。这比对大量零值直接做均方误差更符合测序 dropout 的结构。

论文用局部邻域中的非零比例区分技术性零和更可信的生物学零。代码在 `preprocess.py:173-238` 计算该统计，并保留非零值作为正样本。不过 `mask_sparse_zero` 在 `193-195` 创建后没有用于负采样；实际 `211-216` 依据全局零比例生成随机掩码，甚至没有显式限制到零元素。这是重要的 paper–code 差异，意味着当前包的负例集合并不严格实现论文所述 sparse-zero 规则。

### 第三步：GNN 同时更新细胞与特征

初始 cell 嵌入经过线性投影，feature 节点由可学习 embedding 初始化。两层图卷积在 cell–cell 与 cell–feature 边上传播消息，输出更新后的细胞和特征表示。概念上可写为

$$
h_v^{(l+1)}=W_{\mathrm{self}}h_v^{(l)}+
\sum_{u\in\mathcal N(v)}a_{uv}W_{\mathrm{type}(u,v)}h_u^{(l)}.
$$

代码 `model.py:18-138` 在不同边类型间使用固定标量权重，同类型 cell–cell 消息为 0.3，跨类型 cell–feature 消息为 1.0；`141-155` 固定串联两层卷积。论文描述层间 ReLU，但当前实现没有激活，这会改变编码器表达能力，不能把文中网络结构与本地包视为完全一致。

### 第四步：混合解码器预测缺失模态

GLEAM 同时使用边级 MLP 与全谱 Transformer。对于一个 cell–feature 对，链接 MLP 接收两端 embedding 的拼接，输出非零概率；权重 MLP 输出连续测量值。Transformer 则从一个 cell embedding 一次生成目标模态的完整 feature 向量。代码 `model.py:243-296` 定义两条分支，训练和预测阶段再组合其输出。

这种组合兼顾局部图结构和整条特征谱的相关性，但当前实现也有明确偏差：论文中的 MLP dropout 和权重输出 ReLU 在代码 `model.py:158-194` 中缺失；Transformer 在零膨胀模态上训练的是二值化矩阵，而不是连续表达量；预测函数在 `model.py:459-478` 使用 `data['cell'].x`，没有使用缓存的 GNN cell embedding，和训练前向 `336-430` 的路径不完全相同。

### 训练目标

核心损失可以概括为

$$
\mathcal L=\mathcal L_{\mathrm{binary}}+
\mathcal L_{\mathrm{weight}}+
\lambda\mathcal L_{\mathrm{emb}}+
\mathcal L_{\mathrm{transformer}}.
$$

二元交叉熵学习零/非零，均方误差学习非零边权，嵌入正则项约束编码前后表示，Transformer 分支另有重建损失。直接代码 `model.py:550-583` 显示本地实现使用 `0.05 * ||·||_2`，而论文写的是系数 0.01 的 Frobenius 范数；代码还包含论文主损失式未单列的 Transformer 损失。训练器默认 500 epochs、Adam、学习率 0.001，使用混合精度，但没有验证集早停或固定随机种子。

### 分裂保形预测如何表达不确定性

GLEAM 的不确定性分两部分。分类部分为每个元素构造“零”“非零”预测集合：阈值由独立校准集上的真实类别概率分位数得到，集合可能只含一个类别，也可能两个都含，后者表示模型无法确定是否存在链接。回归部分仅对非零值构造区间，非一致性分数为

$$
s_{cf}=\frac{|x_{cf}-\hat x_{cf}|}{p_{cf}^{\mathrm{nonzero}}},
$$

并按 feature 稀疏度分层估计分位数；最终区间宽度随预测的非零概率缩放。`CP.py:81-127` 与 `129-266` 实现这两部分。

理论覆盖依赖校准样本与测试样本的可交换性以及投影分布稳定等条件，不是对任意分布漂移都自动成立。代码若未提供校准集，会在分类部分回退到测试真值估阈值，这只适合演示或诊断，不能当作有效的独立测试覆盖证明；回归部分则直接不返回区间。

### 图与实验怎样形成证据链

图 1 从完整管线出发，并在 Patch-seq 电生理预测上比较部分配对和完全不配对设置。图 2 用 LOCTO 与 LPSO 检查未见细胞类型和外部 Yao atlas 的外推。图 3 同时评价嵌入整合和 RNA–ATAC 缺失模态预测。图 4 检查三种训练/校准可用性下的保形覆盖，并显示不确定性感知的基因–电生理关联可降低假发现。图 5 才进入生物学发现：将 Patch-seq 与 sn-m3C-seq 对齐，预测电生理，再筛选相关染色质互作、GO 和 motif。

因此，Dpp10、Tle4 等例子是“整合—预测—稳定性选择—功能解释”链条的结果，不应被表述为 GLEAM 单靠链接预测证明了因果调控。详细主图和补充图说明见 `figure_analysis.md`。

### 复现和版本边界

- 本地源码声明包版本 0.1.0、Python ≥3.9；README 给出 PyTorch 2.8.0/CUDA 12.8 和 PyG 2.7.0 的安装组合。
- 本地 `GLEAM/` 没有 `.git` 或 `.repo_source`，不能核验具体上游 commit；仓库 URL来自论文和 README。
- README 明确称工具仍在统一 Python/R 流程，示例 notebook 与 conformal 示例仍“under construction”。论文的完整评估、外部投影、Seurat/R 预处理和生物学下游分析并未全部进入 Python 包。
- `pyproject.toml` 仅声明 NumPy、pandas、SciPy、scikit-learn，实际还需要 PyTorch、PyG、Scanpy 等 README/requirements 环境，单靠项目元数据不能完成安装。
- 本地源为 2026-02-14 打包的未发表稿及补充材料；正文未给 DOI、期刊或正式接受信息，因此这里保留为 2026 manuscript，而不虚构出版状态。

### 最终理解

GLEAM 的关键价值是把不同模态、不同 feature 类型和不配对细胞放进一个统一的图预测问题，并将不确定性显式带到下游分析。其论文方法链完整，但当前 Python 快照仍是研究代码：负采样、激活、损失系数、预测嵌入路径和外部数据投影都存在论文与代码不完全一致之处。理解或复现时，应分别报告论文设计、当前包行为和未随包提供的分析流程。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## GLEAM: Graph Neural Network Link Prediction for Missing Single-Cell Modalities

> **Authors**: Siqi Shen, Sündüz Keleş (UW–Madison) | **Code**: [github.com/keleslab/GLEAM](https://github.com/keleslab/GLEAM) | **Reproducibility**: 4/5

### Motivation

单细胞多组学（scRNA-seq、scATAC-seq、sn-m3C-seq、Patch-seq）可分析基因表达、染色质可及性、3D基因组构象、电生理和形态学，但多数实验仅测量一种模态。例如，Patch-seq需活细胞记录电位，sn-m3C-seq需核裂解，两者无法联合检测。现有方法（BABEL、CMOT、JAMIE、scButterfly、MIDAS、MultiVI、StabMap）存在三个关键缺陷：(1) 要求部分配对或辅助标签；(2) 不支持3D基因组/电生理等非常规模态；(3) 缺乏预测不确定性量化。

### Core Contributions

1. **异质图链接预测框架**：以cell和feature为节点的GNN，将缺失模态预测转化为链接预测问题
2. **零膨胀建模**：集成edge-level MLP + Transformer的混合解码器，处理scRNA/scATAC的技术性dropout
3. **分裂保形预测(Split Conformal Prediction)**：首次为单细胞缺失模态预测提供理论覆盖保证的不确定性量化
4. **模态无关设计**：统一支持3D染色质（sn-m3C-seq）、电生理（Patch-seq）、RNA/ATAC等多种模态
5. **新生物发现**：揭示神经元3D染色质交互与电生理特性的关联

### Method Overview

```
Module 1: Cell Embedding Generation
  共享特征 → CCA联合嵌入 → kNN图 → 加权Metapath2vec细化
  无共享特征 → 桥接图集(如Patch-seq)作为锚点

Module 2: Heterogeneous Graph Construction
  G = (V_cell, V_feature, E_cell-cell, E_cell-feature)
  Cell-cell: 跨模态kNN边 | Cell-feature: 带权二部图边（测量值）
  零膨胀: 邻域分析区分技术性/生物性零值

Module 3: GNN Encoder-Decoder
  Encoder: 2层CustomGraphConv（类型感知权重: cell-cell=0.3, cell-feature=1.0）
  Decoder (Hybrid):
    - EdgePredictor MLP: P(link存在 | e_c, e_f)
    - WeightPredictor MLP: E(表达量 | e_c, e_f, link存在)
    - Transformer: 从cell嵌入预测完整特征向量
  集成: f_b = ½(f₁(e_c||e_f) + [f₂(e_c)]_f)

Module 4: Split Conformal Prediction (Optional)
  分类集合(零/非零) + 分层回归区间，覆盖保证 ≥ 1-α
```

**Loss**: $L = L_{mse} + L_{binary} + \lambda L_{emb}$ + transformer loss (code中$\lambda=0.05$，论文写$0.01$)

### Key Results

| Benchmark | Setting | GLEAM | Best Competitor | p-value |
|-----------|---------|-------|-----------------|---------|
| Patch-seq电生理预测 | Partially paired | r=0.93 | kNN: r=0.87 | $6.76 \times 10^{-12}$ |
| Patch-seq电生理预测 | Unpaired | r=0.92 | kNN: r=0.82 | $4.35 \times 10^{-9}$ |
| sn-m3C-seq+Patch-seq整合 | LTA | 0.75 | Seurat-ref: 0.64 | — |
| 未见细胞类型泛化 | LOCTO vs LPSO | 差异0.01–0.13 | — | — |

**保形预测**: 经验覆盖率严格匹配名义水平（20次随机划分验证）；不确定性感知下游分析比点预测有更高统计功效。

**运行效率**: Zhu 2023数据集17m14s (1 GPU)，优于CMOT(22m)、MultiVI(23m)、BABEL(44m)、JAMIE(68m)等。

### Biological Discoveries

通过GLEAM整合sn-m3C-seq与Patch-seq，揭示神经元3D染色质交互与电生理/形态学的关联：

- **Dpp10基因座**: 细胞类型特异性染色质环与ISI Fano因子强负相关(r = -0.88)
- **Tle4基因座**: 染色质环与标准化皮层深度正相关(r = 0.75)，与Tle4在皮层丘脑投射神经元发育中的已知功能一致
- **转录因子motif富集**: 30个神经元相关motif显著富集（Dlx3-树突发育、Stat3/Ascl1-电生理/形态）

### Reproducibility

| 项目 | 状态 |
|------|------|
| Python包结构 (pip install -e .) | ✓ |
| 3个示例Jupyter notebook | ✓ |
| Scanpy/AnnData兼容 | ✓ |
| DataFrame + AnnData双接口 | ✓ |
| 依赖明确 (requirement.txt) | ✓ |
| $\lambda$参数不一致 (paper:0.01 vs code:0.05) | ⚠ |
| Encoder缺少ReLU激活 (论文有，代码无) | ⚠ |
| MLP Decoder缺少Dropout (论文有，代码无) | ⚠ |
| 外部测试数据投影流程未在Python包中 | ⚠ |
| 硬编码输出路径 `/storage10/siqishen/` | ⚠ |

**环境**: Python ≥3.9, PyTorch 2.8.0+CUDA 12.8, PyG 2.7.0, GPU推荐(A100)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
