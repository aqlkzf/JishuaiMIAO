---
layout: default
permalink: /paper-atlas/pinnacle-d11c9a8b/
title: "PINNACLE"
nav: false
description: "PINNACLE 通过“细胞类型特异 PPI + 细胞/组织元图 + 双向注意力桥”，把同一个蛋白质变成随细胞类型变化的表示；它最有价值的输出不是一个全局蛋白质排名，而是“蛋白质–细胞类型”联合假设。"
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
      <span>Nature Methods · 2024</span>
    </div>
    <h1>PINNACLE</h1>
    <p>Contextual AI models for single-cell protein biology</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/mims-harvard/PINNACLE" target="_blank" rel="noopener noreferrer" aria-label="Open code for PINNACLE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PINNACLE 方法详解：把“细胞类型上下文”写进蛋白质表示

### 1. PINNACLE 要解决什么问题？

传统蛋白质表示学习通常为每个蛋白质生成一个固定向量。但同一个蛋白质在不同细胞类型中可能具有不同的表达状态、相互作用邻域和生物学功能。一个全局向量很难表达这种多效性，也难以回答“这个靶点在哪类细胞中最相关”之类的问题。

PINNACLE（Protein Network-based Algorithm for Contextual Learning）的核心目标是：

> 对同一个蛋白质，在不同细胞类型中生成不同的表示；同时让蛋白质、细胞类型和组织位于同一个多尺度潜在空间中。

论文最终生成了 394,760 个“蛋白质–细胞类型”表示、156 个细胞类型表示和 62 个组织表示（`paper.md:50-65`）。

### 2. 为什么已有方法不够？

- 传统随机游走模型能够利用 PPI 网络，但通常只有一个全局网络视角。
- GAT/GATv2 能学习图上的注意力表示，但若只应用于全局 PPI，仍然是上下文无关的。
- BIONIC（*Nature Methods*, 2022）可以整合多种生物网络，但输出仍是每个蛋白质一个全局表示。
- MaSIF（*Nature Methods*, 2019）从蛋白质三维表面学习结构表示，却不包含蛋白质所在的细胞类型。

PINNACLE 的创新不是简单地把更多数据拼在一起，而是把“上下文”作为模型中的显式状态：每个细胞类型有自己的 PPI 子图，同时所有细胞类型又通过细胞通信和组织层级连接起来。

### 3. 输入、输出与基本符号

#### 3.1 输入一：细胞类型特异的 PPI 图集合

令

$$
\mathcal G=\{G_1,\ldots,G_{|\mathcal C|}\},
\qquad G_{c_i}=(V_{c_i},E_{c_i}),
$$

其中：

- $\mathcal C$ 是细胞类型集合；
- $V_{c_i}$ 是在细胞类型 $c_i$ 中被激活的蛋白质；
- $E_{c_i}$ 是这些蛋白质之间的物理 PPI。

论文以 BioGRID、HuRI 和 Menche 等数据构建含 15,461 个蛋白质、207,641 条边的全局 PPI，再用 Tabula Sapiens 的单细胞表达信息截取每个细胞类型的子图（`paper.md:202-235`）。

#### 3.2 输入二：细胞类型与组织的元图

元图包含两类节点：

- 细胞类型 $c_i\in\mathcal C$；
- 组织 $t_i\in\mathcal T$。

包含四类有向关系：

- CC：细胞类型到细胞类型；
- CT：细胞类型到组织；
- TC：组织到细胞类型；
- TT：组织到组织。

CC 边来自 CellPhoneDB 预测的配体–受体通信；CT/TC 边来自样本的组织来源；TT 边来自 BRENDA Tissue Ontology 的父子层级。

#### 3.3 输出

- 每个蛋白质在每个有效细胞类型中的上下文表示 $\mathbf z_{u,c}$；
- 每个细胞类型的表示 $\mathbf z_c$；
- 每个组织的表示 $\mathbf z_t$。

代码中蛋白质输出是“细胞类型索引 → 蛋白质矩阵”的字典，元图输出是一个节点特征矩阵（`PINNACLE/pinnacle/train.py:218-230`）。

### 4. 从原始数据到模型输出的完整流程

```text
Tabula Sapiens 单细胞表达
        +
全局物理 PPI 网络
        │
        ├─ 对每个细胞类型进行基因排序
        ├─ 选择激活基因对应的蛋白质
        └─ 保留最大连通分量
                 │
                 ▼
       156 个细胞类型特异 PPI 图

CellPhoneDB 配体–受体结果 + 样本组织信息 + BTO 组织本体
                 │
                 ▼
      细胞–细胞–组织多关系元图
                 │
                 ▼
      共享身份的随机蛋白质初始特征
                 │
                 ▼
    第 1 层：蛋白质/细胞/组织向上传递
                 │
         蛋白质 → 细胞注意力汇聚
                 │
           元图关系消息传递
                 │
         细胞 → 蛋白质向下回注
                 │
      归一化 + LeakyReLU + Dropout
                 │
                 ▼
             重复第 2 层
                 │
                 ▼
 PPI 链路预测 + 元图链路预测 + 细胞类型中心损失
                 │
                 ▼
   上下文化蛋白质、细胞类型和组织表示
                 │
        ├─ 与 MaSIF 结构表示拼接
        └─ 用 MLP 进行治疗靶点排序
```

### 5. 第一步：如何构建细胞类型特异 PPI？

论文描述的流程是：

1. 对某个细胞类型与其余细胞进行 Wilcoxon 秩和检验；
2. 选取前 $K$ 个激活基因；
3. 重复 $N$ 次，保留至少在 90% 迭代中出现的基因；
4. 映射到全局 PPI；
5. 保留最大连通分量；
6. 丢弃少于 1,000 个蛋白质的网络。

代码确实实现了 Wilcoxon 排序、Top 基因截取、最大连通分量和 1,000 节点阈值（`PINNACLE/data_prep/0.constructPPI.py:37-84`），也存在 90% 稳定性聚合函数（`0.constructPPI.py:87-117`）。但需要注意：当前驱动脚本只有在 `-subsample` 分支中才执行多次聚合；普通非下采样路径只进行一次排序和提取。因此这一部分属于 **Partial**，不能说与论文流程完全一致。

### 6. 多尺度图神经网络

#### 6.1 蛋白质层注意力

对细胞类型 $c_i$ 中的蛋白质 $u$，论文的 Eq. 1 为：

$$
\mathbf h_u^{\rm PP}\leftarrow
{\rm AGG}\left(
\sigma\left(\sum_{v\in\mathcal N_u}
\alpha_{u,v}W^{\rm PP}\mathbf h_v^{\rm PP}\right)
\right).
$$

$\alpha_{u,v}$ 是 GATv2 注意力，AGG 表示拼接多个注意力头。重要的是，每个细胞类型都有独立的 GATv2 层（`PINNACLE/pinnacle/conv.py:22-32,121-124`）。因此，同一个蛋白质即使初始身份向量相同，也会因为邻居和参数不同而产生不同的上下文表示。

对于不同关系/元路径产生的表示，代码进一步计算语义注意力：

$$
\beta_r={\rm softmax}_r\left(
\mathbf q^\top\tanh(W\mathbf h^r+\mathbf b)
\right),
\qquad
\mathbf z=\sum_r\beta_r\mathbf h^r.
$$

对应实现位于 `PINNACLE/pinnacle/conv.py:57-72,140-156`。

#### 6.2 元图层注意力

细胞类型节点分别从 CC 和 CT 邻居接收消息，再用关系权重 $\beta^{\rm CC}$ 与 $\beta^{\rm CT}$ 融合；组织节点则融合 TT 与 TC 消息（论文 Eqs. 2–7，`paper.md:267-315`）。

代码把四类边编码成四组元路径邻接矩阵：

```text
0: tissue → tissue
1: tissue → cell
2: cell → tissue
3: cell → cell
4: protein → protein
```

对应 `PINNACLE/pinnacle/generate_input.py:93-120,139-168`。

#### 6.3 蛋白质–细胞类型桥

这是 PINNACLE 最关键的结构。模型先学习每个蛋白质对其细胞类型的重要性 $\gamma_{c_i,u}$，再执行两次方向相反的信息交换。

蛋白质向细胞类型汇聚：

$$
\mathbf h_{c_i}\leftarrow \mathbf h_{c_i}+
{\rm AGG}\left(\sigma\left(
\sum_{u\in V_{c_i}}\gamma_{c_i,u}\mathbf h_u
\right)\right).
\tag{8}
$$

细胞类型向蛋白质回注：

$$
\mathbf h_u\leftarrow
\mathbf h_u+\gamma_{c_i,u}\mathbf h_{c_i}.
\tag{9}
$$

实现位于 `PINNACLE/pinnacle/conv.py:85-107,158-170`。直观上：

- 第一次传递让细胞类型知道“哪些蛋白质最能代表我”；
- 元图传播让细胞类型获得细胞通信和组织层级信息；
- 第二次传递再把这些上下文写回蛋白质。

这使上下文不只是预先切分的 PPI 子图，还成为进入蛋白质表示的显式消息。

#### 6.4 两层结构与向量维度

`Pinnacle` 使用两个完整的上行/下行模块（`PINNACLE/pinnacle/model.py:22-32,39-74`）。两层之间使用 LayerNorm、LeakyReLU、BatchNorm 和 Dropout。

最终维度为：

$$
d_{final}=d_{head}\times K.
$$

论文规模的脚本设置 `output=16`、`n_heads=8`，所以最终表示维度为 $16\times8=128$（`PINNACLE/pinnacle/run_pinnacle.sh:5-22`）。

### 7. 训练目标

#### 7.1 总损失

论文 Eqs. 10–11 可合并为：

$$
\mathcal L=
\theta\mathcal L_{ppi}
+(1-\theta)\mathcal L_{metagraph}
+\lambda\mathcal L_{celltypeid}.
$$

代码在 `PINNACLE/pinnacle/minibatch_utils.py:78-97` 中直接按照这个形式组合损失。

#### 7.2 链路预测

- $\mathcal L_{ppi}$：预测每个细胞类型 PPI 中的真实边和负样本边；
- $\mathcal L_{metagraph}$：预测 CC、CT、TC、TT 四类关系。

PPI 使用点积解码，元图使用关系特异的双线性解码：

$$
\hat y_{u,v}=\sigma(
\mathbf z_u^\top {\rm diag}(\mathbf r_i)\mathbf z_v
).
$$

代码见 `PINNACLE/pinnacle/loss.py:8-20,33-38`。

#### 7.3 细胞类型中心损失

论文 Eq. 13：

$$
\mathcal L_{celltypeid}=
\sum_{c_i\in\mathcal C}\sum_{u\in V_{c_i}}
\lVert\mathbf z_u-\mathbf z_{c_i}\rVert_2^2.
$$

它迫使同一细胞类型中的蛋白质表示靠近相应的细胞类型中心，并与其他上下文区分开。代码把所有批次蛋白质拼接后，以元图前若干行作为细胞类型中心计算 `CenterLoss`（`PINNACLE/pinnacle/minibatch_utils.py:82-101`）。

### 8. 训练、验证与推理

- PPI 边按 80%/10%/10% 划分；元图边在训练、验证和测试中全部保留。
- 每条正边使用 `structured_negative_sampling` 生成一条负边，即 1:1。
- 训练使用 GraphSAINT 边采样。每个批次只用采样节点及其两跳邻居近似细胞类型的全局汇聚。
- 验证/测试阶段使用完整蛋白质特征，只对待预测边进行批处理。
- 最终输出通过 `torch.save` 保存为蛋白质字典和元图矩阵。

这些行为分别可在 `pinnacle/generate_input.py`、`minibatch_utils.py` 和 `train.py` 中直接验证。

### 9. 下游任务

#### 9.1 与三维结构表示结合

论文使用 MaSIF 得到 200 维结构表示，再与 128 维 PINNACLE 上下文表示拼接，形成 328 维向量。对于 PD-1/PD-L1 和 B7-1/CTLA-4，小规模实验显示 PINNACLE+3D 的结合/不结合分数差距大于仅使用 3D 结构的差距。

但是，本地代码仓库中 **Not found**：没有 MaSIF 数据处理、PDB patch 选择、向量拼接或置换检验实现。因此这部分只能按论文理解，不能声称已由代码验证。

#### 9.2 治疗靶点优先级排序

每个蛋白质的上下文表示输入 MLP，得到 0–1 的治疗靶点评分。阳性样本是至少完成临床二期的药物靶点；阴性样本是可成药但未与该治疗领域关联的蛋白质。

代码中的 MLP、BCEWithLogitsLoss、Adam 和按细胞类型测试均可直接验证（`PINNACLE/finetune_pinnacle/model.py:6-60`; `train_utils.py:15-106`）。数据划分使用 `StratifiedGroupKFold`，以蛋白质身份分组，确保同一蛋白质的不同上下文表示不会同时进入训练集和测试集（`finetune_pinnacle/data_prep.py:46-205`）。

### 10. 论文结果应该如何解读？

#### 论文直接报告的结果

- 同一细胞类型的蛋白质表示相似度明显高于不同细胞类型；去掉细胞/组织元图后差距大幅缩小。
- 组织表示距离与组织本体距离相关，但叶节点上的相关性较弱，说明是部分恢复而非完美恢复。
- 在 RA 和 IBD 靶点任务中，一部分细胞类型显著优于 GAT/BIONIC，但不是所有上下文都优于强基线。

#### 合理解释

PINNACLE 的优势来自两层上下文化：

1. 同一蛋白质在不同细胞类型中具有不同 PPI 邻域；
2. 细胞和组织元图的信息再通过 $\gamma$ 桥写回蛋白质。

因此，模型学习的不只是“蛋白质是谁”，还包括“蛋白质在哪个细胞和组织关系中工作”。

#### 假设生成，而非因果结论

JAK3、IL6R、ITGA4、PPARG 的高分细胞类型与已知生物学一致，可用于提出后续实验方向。但这些排名没有证明细胞类型是药物作用的因果场所，也没有证明模型能够直接预测临床疗效。

### 11. 代码–论文一致性与已知缺口

总体一致性为 **medium**：核心预训练和治疗靶点微调代码较完整，但并非所有论文实验都能从仓库直接复现。

- **Exact：** 两层多尺度 GATv2、关系注意力、PPI/元图链路预测、中心损失、边划分、负采样、论文规模超参数、嵌入保存和 MLP 微调。
- **Partial：** 论文写 ReLU，代码使用 LeakyReLU；论文写细胞/组织均值初始化，代码在首层使用 $\gamma$ 加权蛋白质和随机组织向量，并固定执行 100 轮组织邻居平均；重复基因筛选流程只在特定分支出现。
- **Not found：** MaSIF 三维结构下游流程，以及能够一次性重建论文十随机种子基线和全部图表的实验驱动。
- **指标差异：** 论文定义
  $$
  {\rm APR}@K=\frac{1}{r}\sum_{k=1}^{K}{\rm Precision}@k\,{\rm rel}(k),
  $$
  但仓库辅助函数对 Top-$K$ 子集调用 `average_precision_score`。两者通常不相等，因此论文 APR@K 不能直接由当前可见函数严格复现。
- **未执行验证：** 本次分析没有下载数据或运行训练；运行时张量形状和最终数值结果尚未验证。

### 12. 一句话理解 PINNACLE

PINNACLE 通过“细胞类型特异 PPI + 细胞/组织元图 + 双向注意力桥”，把同一个蛋白质变成随细胞类型变化的表示；它最有价值的输出不是一个全局蛋白质排名，而是“蛋白质–细胞类型”联合假设。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PINNACLE — Contextual AI Models for Single-Cell Protein Biology

### Problem

Most protein representation models assign one vector to each protein, even though protein expression, partners and function can vary across cell types and tissues. This context-free design makes it difficult to reason about pleiotropy, cell-specific mechanisms and therapeutic effects that depend on where a target acts (`paper.md:18-27`).

PINNACLE (Protein Network-based Algorithm for Contextual Learning) addresses this by generating a distinct representation for a protein in every cell type in which its gene is activated. The model integrates single-cell transcriptomics, physical PPIs, ligand–receptor cell communication and a tissue ontology into one multiscale graph-learning system.

### Relation to Prior Methods

The paper contrasts PINNACLE with methods that learn one global protein representation. Its principal downstream baselines are:

- a network random-walk disease model from the Pacific Symposium on Biocomputing (2018);
- GATv2, introduced at ICLR 2022, applied to the global PPI network;
- BIONIC, a context-free multimodal network-integration model published in *Nature Methods* (2022);
- MaSIF, a surface-based geometric deep-learning model published in *Nature Methods* (2019), for the 3D interaction case study (`paper.md:619,631,659-660`).

These methods can integrate network or structure information, but they do not directly produce a separate protein state for each cell type while jointly modeling cell communication and tissue hierarchy.

### Method in Brief

PINNACLE constructs 156 cell type-specific PPI networks from Tabula Sapiens and a global physical interactome. It also builds a metagraph with cell–cell ligand/receptor edges, cell–tissue membership edges and tissue–tissue ontology edges. A two-layer multiscale GNN then performs:

1. per-cell-type GATv2 message passing over protein networks;
2. typed attention over cell and tissue relations;
3. learned protein-to-cell pooling and cell-to-protein down-pooling;
4. self-supervised PPI and metagraph link prediction;
5. center loss that groups contextual proteins around their cell-type representations.

The resulting space contains 394,760 contextual protein vectors, 156 cell-type vectors and 62 tissue vectors (`paper.md:50-65`). The checked implementation matches the core two-layer encoder, multiscale losses, split/negative-sampling logic, embedding export and therapeutic fine-tuning. Overall paper–code fidelity is **medium**: 10 Exact, 4 Partial and 2 Not found mappings are documented in `doc_code.md`.

### Evaluation and Main Findings

#### Representation organization

SAFE enrichment and UMAP analyses show localized cell-type regions across all 156 contexts. Protein representations from the same cell type have much higher similarity than representations from different cell types; this gap largely disappears in a model without cellular/tissue context. Tissue embedding distance correlates with tissue ontology distance ($\rho=0.36$, $P=1.85\times10^{-119}$), although the leaf-only association in Extended Data is weak ($\rho=0.11$), indicating partial rather than exact hierarchy recovery (`paper.md:62-87`).

#### 3D interaction case study

The authors concatenate PINNACLE’s 128-dimensional context vector with a 200-dimensional MaSIF structural vector for two immune-checkpoint binding pairs and 20 nonbinding pairs. Contextualized structure representations show a binding/nonbinding gap of 0.0119 with $P<10^{-5}$, compared with 0.0047 and $P=0.2121$ for 3D structure alone (Extended Data Fig. 7). This supports complementarity between cell context and molecular surface information, but the experiment is small and its analysis code is absent from the repository.

#### Therapeutic target prioritization

For rheumatoid arthritis (RA) and inflammatory bowel disease (IBD), the paper fine-tunes an MLP on contextual protein vectors. Positives are targets of drugs that completed at least phase 2; negatives are druggable proteins without known association to the therapeutic area. Protein identities, not individual contextual vectors, are separated across train/validation/test to reduce leakage (`paper.md:485-536`).

At APR@5, all 156 RA and all 152 evaluated IBD contexts outperform random walk. For RA, 70/156 contexts outperform GAT and 29/156 outperform BIONIC; for IBD, 57/152 outperform GAT and 13/152 outperform BIONIC (`paper.md:113-119`). The result is therefore context-selective: some cell types are substantially better than context-free baselines, while many are not.

The highest-ranked contexts are biologically plausible—immune contexts for RA and immune/intestinal epithelial contexts for IBD. JAK3, IL6R, ITGA4 and PPARG examples align with known cell biology, but these are hypothesis-generating nominations rather than experimental causal validation.

### Strengths

- Represents the same protein differently across biological contexts.
- Couples protein networks to cell communication and tissue hierarchy in one model.
- Uses a shared latent space that supports protein, cell-type and tissue queries.
- Provides reusable pretrained representations and code for core pretraining and MLP fine-tuning.
- Includes ablations, network-construction sensitivity analyses and selected checks against degree and label-enrichment confounding.

### Limitations

- Cell type-specific PPIs are inferred by overlaying single-cell expression on a global interactome, not directly measured in each cell type. False positive and false negative interactions remain possible (`paper.md:178-187`).
- Tabula Sapiens represents healthy tissues and lacks important disease-specific contexts such as RA synovium, limiting disease modeling.
- The 3D experiment is based on only two binding pairs, and its implementation is not in the checked repository.
- Downstream gains are not uniform across cell types; selecting the best context can itself introduce optimistic bias.
- The repository’s AP@K helper uses scikit-learn average precision on a top-$K$ subset, which is not the paper’s stated APR@K equation.
- Paper/code differences include LeakyReLU versus the paper’s ReLU and learned/iterated bridge initialization versus the paper’s mean initialization.
- No supplementary Markdown was acquired, and training was not executed in this analysis.

### Reproducibility

**Rating: 3/5.** The official repository (commit `b0414827ffa88284af729ffd1ddf747e0e9cfb51`) contains install instructions, network-construction scripts, the core encoder, paper-scale hyperparameters, training/export code and the therapeutic MLP pipeline. Data, checkpoints and representations are available externally through the project site/Figshare (`paper.md:602-611`; `PINNACLE/README.md:33-118`).

Reproduction is incomplete from the clone alone: large data assets must be downloaded and paths configured; the MaSIF workflow and an end-to-end published benchmark/figure driver are missing; the APR@K implementation is inconsistent with the Methods definition; and no runtime/tensor-shape validation was performed here. The core algorithm is well exposed, but not every reported result is one-command reproducible.

### Bottom Line

PINNACLE’s main contribution is architectural, not merely a larger protein dataset: it makes context a first-class state variable by coupling context-specific PPI message passing with cell/tissue message passing and a learned bridge between them. The paper’s strongest evidence is that this design creates structured, biologically recognizable variation across protein contexts and that selected contexts improve downstream ranking. The results motivate context-specific protein modeling, while the missing 3D code, metric discrepancy and inferred interactomes define important boundaries on reproducibility and interpretation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
