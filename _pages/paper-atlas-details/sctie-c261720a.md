---
layout: default
permalink: /paper-atlas/sctie-c261720a/
title: "scTIE"
nav: false
description: "scTIE 面向同一细胞同时测得 RNA 表达和染色质可及性的时间序列 multiome 数据。它先用两个模态专属的自编码器把 RNA 与 ATAC 投影到共同低维空间，再反复用相邻时间点之间的最优传输（optimal transport, OT）更新“哪些早期细胞可能流向哪些晚期细胞”；"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Genome Research · 2024</span>
    </div>
    <h1>scTIE</h1>
    <p>Data integration and inference of gene regulation using single-cell temporal multimodal data with scTIE</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/gr.277960.123" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scTIE：把时间、多组学整合与命运调控解释连成一条证据链

### 一句话理解

scTIE 面向同一细胞同时测得 RNA 表达和染色质可及性的时间序列 multiome 数据。它先用两个模态专属的自编码器把 RNA 与 ATAC 投影到共同低维空间，再反复用相邻时间点之间的最优传输（optimal transport, OT）更新“哪些早期细胞可能流向哪些晚期细胞”；训练完成后，以 OT 转移概率作为监督信号微调一个命运预测器，再把预测梯度反传到原始基因和开放峰，从而寻找对某条细胞命运最有预测力的基因、顺式调控元件和候选调控网络。

这不是简单的“先做整合，再做差异分析”。它的关键设计是让表示学习和时间对齐形成反馈：当前表示决定 OT 运输矩阵，运输矩阵又作为损失把下一轮表示拉向更合理的时间连续结构。

### 1. scTIE 解决的三个相互牵制的问题

#### 1.1 多模态整合

每个细胞有两个高维向量：基因表达 $x^{(t,R)}$ 与 ATAC 峰可及性 $x^{(t,A)}$。RNA 连续且动态范围大，ATAC 极稀疏且近似二值；直接拼接容易让某一模态的尺度或噪声主导距离。scTIE 分别编码二者，但要求同一细胞的两种表示在共同空间靠近。

#### 1.2 跨时间对齐

不同时间点测到的不是同一批活细胞，不能提供逐细胞真值配对。scTIE 用 OT 估计从时点 $t$ 到 $t+1$ 的软转移矩阵 $\gamma^{(t,t+1)}$。矩阵的一行描述某个早期细胞向所有晚期细胞分配的概率质量。

#### 1.3 命运相关调控解释

差异表达/差异可及性回答“两个群体平均上哪里不同”，不直接回答“哪些早期特征能预测将来流向哪条分支”。scTIE 把 OT 汇总出的命运概率作为预测目标，通过输入梯度排序基因和峰，再结合 motif、峰—基因连接等证据构建 lineage-specific GRN。

### 2. 输入、预处理与输出

#### 2.1 输入

论文的核心输入是多个已知时间点的 paired multiome：每个细胞同时具有 RNA count 和 ATAC peak matrix。ATAC 峰直接输入，不先转成 gene activity。代码按时点读取稀疏 NPZ：RNA count 先做

$$
x_g\leftarrow \log\left(1+10^4\frac{x_g}{\sum_jx_j}\right),
$$

ATAC 则按是否大于零二值化（`util/dataloader.py:13-29`）。代码不要求先选 HVG；论文把这一点归因于 RNA 编码器/解码器之间的 coupled batch normalization。

#### 2.2 主要输出

- 每个细胞的 64 维 joint embedding；
- 相邻时间点的 RNA、ATAC 或共同空间 OT transport matrices；
- 用户指定来源群体到若干目标命运的转移概率；
- 每条命运的基因和峰梯度排名；
- 在额外 motif、peak-to-gene 等注释规则支持下得到的候选 GRN。

“GRN”不是从自编码器权重直接读出，也不是 OT 矩阵本身；它是预测性特征筛选与外部调控连接证据的下游组合。

### 3. 第一阶段：学习共同表示

#### 3.1 模态专属编码器

对模态 $s\in\{R,A\}$，编码器 $f_s$ 把原始向量映射为共同表示：

$$
z_i^{(t,s)}=f_s\left(x_i^{(t,s)}\right).
$$

当前代码的 `BN_common_encoder` 为 RNA 和 ATAC 各设两层 1,000 节点隐藏层，LeakyReLU 后输出 64 维；两条支路各自先用无 affine 参数的 `BatchNorm1d` 标准化输入（`util/model_residual.py:120-167`）。解码器从 64 维经 500、1,000 节点恢复原始维度（`model_residual.py:209-249`）。

代码还实例化 `BN_resid_encoder`，但主训练把它的输出替换成全零再交给 decoder（`trainingprocess_bnresidualpretrain.py:196-203`）。所以当前有效训练路径是 common embedding 重构；不能因为类名存在就宣称论文结果使用了一个活跃的 residual 分支。

#### 3.2 重构损失：别把生物信号全洗掉

每种模态都要求从低维表示恢复输入：

$$
L_{recon}=\sum_s\left\|\tilde X^{(s)}-d_s(f_s(X^{(s)}))\right\|_2^2.
$$

RNA 的目标是 batch-normalized 输入，ATAC 的目标是二值化后再 batch-normalize 的输入。重构损失防止只为了混合时间或模态而丢掉细胞类型差异。

#### 3.3 模态配对损失：同一细胞的 RNA 与 ATAC 应靠近

paired multiome 给出了可靠的一一对应关系。代码用 `PairLoss` 约束同一细胞的 $z^{(R)}$ 与 $z^{(A)}$：

$$
L_{pair}=\frac{1}{Bq}\sum_{i=1}^{B}\left\|z_i^{(R)}-z_i^{(A)}\right\|_2^2,
$$

其中 $q$ 是 embedding 维度。它提供了“模态是否对齐”的真值，也能用于选择 OT 权重：论文补充图显示 OT 权重太大会改善时间混合，却可能损害 RNA–ATAC 配对。

#### 3.4 时间 OT 损失：把高概率后代拉近

在当前表示中，相邻时点细胞的代价为

$$
C^{(t,t+1)}_{kl}=\left\|f(x_k^{(t)})-f(x_l^{(t+1)})\right\|_2.
$$

Waddington-OT 根据代价、熵正则和生长率估计 $\gamma^{(t,t+1)}$。训练 mini-batch 取运输矩阵子块，按行重新归一化，然后最小化

$$
L_{ot}=\frac{1}{T-1}\sum_t\operatorname{mean}\left(
\tilde\gamma^{(t,t+1)}\odot\tilde C^{(t,t+1)}
\right).
$$

直观上，若 OT 认为早期细胞 $i$ 很可能到达晚期细胞 $j$，$\gamma_{ij}$ 大，模型就会因二者在 embedding 中过远而受到更大惩罚。

代码在 `get_total_ot_loss()` 中用 `torch.cdist` 计算 batch 欧氏距离，并逐元素乘运输概率（`util/ot_solvers.py:49-69`）。完整 OT 求解前还把平方欧氏代价矩阵除以其中位数（`ot_solvers.py:95-120`），这一实现细节未在论文公式中显式说明，会改变正则参数的有效尺度。

#### 3.5 “迭代 OT”到底怎么迭代

初始 `gammas` 为空，因此先只靠重构和模态损失学习可用表示。每隔 $K$ 个 epoch（默认 10），代码提取所有细胞的当前 embedding，重新求解相邻时点 OT 并覆盖运输矩阵。之后 mini-batch 又用新矩阵计算 $L_{ot}$。循环为：

$$
\text{embedding}\rightarrow C\rightarrow\gamma\rightarrow L_{ot}
\rightarrow\text{new embedding}\rightarrow\cdots
$$

这区别于在固定预处理空间只求一次 OT。优点是时间关系与表示共同改善；风险是二者可能互相强化初始偏差，因此必须检查细胞类型保留、模态配对和跨时间混合，而不能只看一个 loss。

#### 3.6 当前代码的优化步骤不是论文公式的一次联合反传

概念上可写

$$
L=\lambda_{recon}L_{recon}+\lambda_{pair}L_{pair}+\lambda_{ot}L_{ot}.
$$

但当前实现每个 batch 先对重构+模态损失执行一次 `zero_grad → backward → step`，再重新前向，对 OT 损失执行第二次优化步骤（`trainingprocess_bnresidualpretrain.py:205-255`）。两组梯度没有在同一次 backward 中相加。

另一个重要差异是优化器：论文方法描述 Adam，而当前 Stage-1 代码用 SGD、momentum 0.9、默认 learning rate 0.1（同文件 89-99；`config.py:5-10,69-83`）。Adam 出现在后续命运分类微调中。这是明确的 paper-code discrepancy，不能平滑成“完全一致”。

### 4. 训练顺序与锚定策略

README 和代码体现两步训练：先训练 RNA 模型，再把 checkpoint 作为 joint RNA+ATAC 训练的 anchor。joint 阶段前 `anchor_epochs`（默认 300）冻结 RNA encoder 与 decoder，只训练 ATAC 去对齐已有 RNA 表示；之后解冻 RNA 联合调整（`trainingprocess_bnresidualpretrain.py:154-171`）。默认总 epoch 500、batch size 256、embedding 64、hidden 1,000、OT weight 0.1、pair weight 1、reconstruction weight 10（`config.py`）。

最终写出的 common embedding 是 RNA 与 ATAC embedding 的平均值：

$$
z_i=\frac{z_i^{(R)}+z_i^{(A)}}{2}.
$$

这些是本地代码快照的默认值。论文中的符号权重与代码绝对数值并不完全相同，例如论文记 $\lambda_{recon}=1$，代码 `restored_loss_weight=10`；复现时应保存完整命令和配置，而不是只抄论文符号。

### 5. 第二阶段：从转移概率到命运预测特征

#### 5.1 将 OT 质量汇总为分支概率

用户先指定来源细胞群 $G_0$，以及未来两个或多个目标群 $G_1,G_2$。对于来源细胞 $i$，代码把 transport matrix 中流向目标群的质量相加：

$$
p_{ic}=\sum_{j\in G_c}\gamma_{ij},
\qquad
\bar p_{ic}=\frac{p_{ic}}{\sum_{c'}p_{ic'}}.
$$

若使用多个未来时点，再做加权汇总。`infer_deconv.py:107-152` 直接实现了索引、求和、归一化和低置信样本过滤。这些 $\bar p_i$ 是 OT 模型给出的软标签，不是实验直接观测到的真实命运。

#### 5.2 微调命运分类器

代码载入 epoch 500 的 pretrained common encoder，分别在 RNA 和 ATAC embedding 上接 `Linear(64, number_of_fates) + Softmax`，用 KL divergence 拟合 OT 概率，并同时优化 encoder（`infer_deconv.py:163-220`）。此处使用 Adam，而非 Stage-1 的 SGD。

#### 5.3 梯度显著性排序

微调后对某个命运输出 $h_c$ 反向传播到输入：

$$
s_{ig}^{(R)}=\left|\frac{\partial h_c(x_i)}{\partial x_{ig}^{(R)}}\right|,
\qquad
s_{ip}^{(A)}=\left|\frac{\partial h_c(x_i)}{\partial x_{ip}^{(A)}}\right|.
$$

代码将 RNA 梯度乘以跨全部时点计算的 gene standard deviation，再在细胞间汇总和排序；论文示例选择 top 200 genes 与 top 500 peaks。含义是“在局部模型中，改变这个输入对命运预测输出有多敏感”，不是因果效应，也不等于该基因一定直接调控该命运。

### 6. 从预测特征到 GRN：还需要哪些连接证据

高梯度 genes 和 peaks 只是候选节点。论文进一步用 peak 中的 TF motif、开放峰与基因的关联/位置等规则形成 TF—CRE—target gene 边，得到 anterior primitive streak、endoderm 与 mesoderm 的 lineage-specific GRN。图 5 展示 scTIE 特征比传统 DE/DA 排名前列特征更能预测 fate probabilities，并将候选 peaks 与发育期 enhancer database 比较。

因此最稳妥的解释层级是：

1. OT 给出模型估计的转移概率；
2. 梯度找出预测该概率的输入特征；
3. motif/peak-gene 数据库提出候选调控连接；
4. 已知发育 TF、enhancer 富集和外部实验提供生物学支持。

它不等同于通过扰动实验验证的因果网络。

### 7. 逐图读懂论文证据

#### 图 1：算法合同

图 1A 是整合阶段：RNA/ATAC 分别编码和重构，以 reconstruction、modality alignment 和 temporal OT 联合塑造共同表示，同时迭代更新 transport matrix。图 1B 是解释阶段：用户选定转移，微调网络，反传梯度并组建 GRN。该图明确区分“整合模型”与“下游命运特征模型”。

#### 图 2：整合不是只追求混得越匀越好

论文在鼠早期器官发生 multiome 数据上人工加入 batch effect 和噪声，与 Seurat、multiVI、MOFA 等比较。评价同时看 batch purity、time purity 与 cell-type ARI：理想表示要混合批次/时间，又保留细胞类型。scTIE 在三维权衡中包围面积最大。这里的 synthetic perturbation 提供受控 benchmark，但不能替代在所有真实数据集上的普适保证。

#### 图 3：真实 mESC 时间序列中的亚群

joint embedding 用于聚类 differentiating mouse embryonic stem cells，得到覆盖三个胚层与胚外谱系的 17 个 cluster，并用 marker、label transfer 和 motif enrichment 注释。两个 pseudoreplicate 的总体细胞类型一致率为 81%。该结果支持表示保留生物信号，但聚类数和标签仍受下游参数与参考标记影响。

#### 图 4：embedding 维度可被哪些生物过程解释

论文逐维反传输入梯度，用细胞类型 marker 和 GO pathway 做富集。RNA 与 ATAC 的富集模式相似，dimension 39 富集 activin receptor signaling，排名靠前包含 *Lefty1*、*Fst*、*Nodal*。这是“共同表示捕获了已知处理与发育信号”的证据，而不是说单一 latent dimension 对应唯一通路。

#### 图 5：命运预测特征与候选网络

图 5A 比较 gradient-selected 与 DE/DA-selected features 对 fate probabilities 的预测能力；图 5B 检查 peaks 与发育 enhancer 的组织/阶段特异重叠；图 5C 展示三条命运的候选 GRN。补充分析用 60% cell subsampling、50 次重复检查梯度稳定性。这条证据链比只列高梯度基因更完整，但最终网络仍是计算候选。

补充 PDF 还系统改变 OT weight、更新频率、hidden/embedding size，并检验 coupled batchnorm、32/96 维表示与 feature ranking 稳定性。它支持默认设置附近的稳健性，同时也显示 OT weight 是影响时间与模态平衡的重要旋钮。

### 8. 论文与本地代码映射

| 机制 | 本地入口 | 状态 | 边界 |
|---|---|---|---|
| RNA/ATAC 专属 encoder 和 64D common space | `util/model_residual.py` | Exact | residual encoder 在当前训练路径被置零 |
| coupled batchnorm 与无 HVG 输入 | `model_residual.py`, `dataloader.py` | Exact | 必须匹配输入预处理 |
| reconstruction MSE | `trainingprocess_bnresidualpretrain.py:205-213` | Exact | RNA 目标是 BN 后数据 |
| paired modality loss | 同文件 215-224，`util/closs.py` | Exact | paired multiome 是必要真值 |
| 相邻时点 OT loss | `util/ot_solvers.py:39-69` | Exact | 完整矩阵计算有二次内存成本 |
| iterative OT 每 10 epoch 更新 | training process 284-309 | Exact | `K` 可配置 |
| Waddington-OT 生长率 | `ot_solvers.py:39-46,95-121` | Exact/Partial | growth files 是外部数据产品 |
| Stage-1 optimizer | training process 89-99 | Discrepant | 论文写 Adam，代码为 SGD |
| 命运概率汇总 | `infer_deconv.py:107-152` | Exact | 概率是 OT 派生软标签 |
| KL 微调和输入梯度 | `infer_deconv.py`, `embedding_grad_all.py` | Exact | 梯度是预测敏感性，不是因果效应 |
| 论文完整 GRN 图 | 脚本提供部分梯度/筛选流程 | Partial | motif、数据库、绘图与完整数据需另行准备 |

`doc_code.md` 的 Match Assessment 提供更细的公式—文件—行号映射。

### 9. 版本与复现边界

本工作区包含从 GitHub 获取的源代码目录，但没有保留可验证的 `.git` commit 元数据，`local metadata` 因而不能声称一个精确 commit。README 说明代码在 PyTorch 1.9.1 开发测试；主路径硬编码 `.cuda()`，需要 CUDA 环境；OT 默认调用已编译的 `util/libot.so`，新环境可能要执行 `util/build.sh`。数据路径、growth estimate `.npy`、cluster index CSV 和 pretrained checkpoint 也不是仓库中完整自带的轻量输入。

因此可复现性应拆开评价：

- **方法结构**：编码器、损失、迭代 OT、概率汇总、KL 微调和 saliency 路径都可在源码中定位；
- **教程运行**：仓库提供 HSPC notebook 和命令框架，但依赖旧 PyTorch/CUDA、外部数据与 C++ 扩展；
- **论文逐图复现**：需要 GSE223041/GSE205117 等数据、作者预处理结果、growth estimates、cluster annotations、数据库和精确运行配置；当前 workspace 不能开箱一键生成全部图；
- **paper-code 一致性**：Stage-1 optimizer 与 loss 权重表示存在明确差异，应以实际脚本为准并报告。

### 10. 使用时的检查清单

1. 确保 RNA 与 ATAC 来自同一细胞，时点顺序和 cell index 完整对应。
2. 记录 RNA normalization、ATAC 二值化、峰过滤和所有外部 growth 文件。
3. 先跑 RNA pretraining，再 joint training；保存每次 checkpoint 与完整 `config.py`。
4. 同时评估 paired-modality FOSCTTM/距离、time purity 和 cell-type ARI，不把时间混合当唯一目标。
5. 检查 OT transport row sums、NaN、低概率细胞及不同 OT weight/seed 的稳定性。
6. 做 fate analysis 时明确来源群、目标群、未来时点与概率过滤阈值。
7. 对 gradient ranking 做重复/子采样验证，并用 motif、peak-gene 与外部发育证据交叉核验。
8. 报告候选调控关系，不把 saliency 或相关网络写成已验证因果。

### 11. 最容易误读的五点

- **共同空间不是把两个矩阵简单拼接。** 两条编码器由重构、配对与时间 OT 共同约束。
- **OT 不是谱系真值。** 它是依据距离、生长率和正则得到的软耦合。
- **时间混得更好不一定模型更好。** OT 权重过大可能牺牲模态配对或细胞类型结构。
- **高梯度不等于高表达，也不等于因果调控。** 它表示模型输出对输入的局部敏感性。
- **当前代码存在重要实现边界。** Stage-1 使用 SGD，residual 分支被置零，且无可验证 commit；复现必须以快照和实际配置为准。

### 本地证据入口

- 主文：`paper source/PMC10903952/paper.md`
- 主文 PDF：`paper source/PMC10903952/119.pdf`
- 补充 PDF：`paper source/PMC10903952/Supplemental_Materials.pdf`
- 方法与公式：`doc_method.md`
- 逐图分析：`figure_analysis.md`
- 代码对应：`doc_code.md`
- 训练主路径：`scTIE/util/trainingprocess_bnresidualpretrain.py`
- 模型：`scTIE/util/model_residual.py`
- OT：`scTIE/util/ot_solvers.py`
- 命运与梯度：`scTIE/infer_deconv.py`, `scTIE/embedding_grad_all.py`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scTIE Summary

### Motivation & Novelty

#### Biological Problem

During development, cells transition from pluripotent states to specialized cell types through a series of gene regulatory events. Understanding which transcription factors (TFs) and cis-regulatory elements (CREs) drive these transitions is fundamental to developmental biology. Single-cell multiome technologies now enable simultaneous measurement of gene expression (scRNA-seq) and chromatin accessibility (scATAC-seq) from the same cell over a time course, providing an unprecedented window into the regulatory landscape.

#### Limitations of Existing Approaches

**Integration methods** (Seurat WNN, *Nature Biotechnology* 2021; MultiVI, *Nature Methods* 2023; MOFA+, *Genome Biology* 2020; scAI, *Genome Biology* 2020) focus on aligning cells across modalities and batches but do not address downstream GRN inference. They treat integration as a standalone problem.

**GRN inference methods** (SCENIC, *Nature Methods* 2017; ArchR, *Nature Genetics* 2021; Pando, *Nature Genetics* 2023; GLUE, *Nature Methods* 2022) infer regulatory relationships but either ignore the integration problem or produce global (non-context-specific) GRNs. They select features via differential expression/accessibility (DE/DA) analysis, which captures marginal correlations but does not identify features *predictive of cell fate transitions*.

**Trajectory methods** (Waddington-OT, *Cell* 2019; Monocle3, *Nature* 2019) infer cell trajectories but do not jointly model multimodal data or extract interpretable regulatory features.

#### Unique Contributions

1. **Unified framework**: First method to jointly address temporal multimodal integration and context-specific GRN inference in a single model.
2. **Iterative OT**: Unlike WOT which solves OT once, scTIE incorporates OT into the autoencoder loss and updates the transport matrix iteratively throughout training, achieving a better balance between time-point alignment and cell-type separation.
3. **Coupled batchnorm**: A pair of batchnorm layers (input normalization + output rescaling) eliminates the need for HVG selection, making the method more robust and generalizable.
4. **Fate-predictive feature selection**: Selects genes and peaks based on their ability to predict cell transition probabilities (via gradient saliency), rather than marginal DE/DA significance. This captures regulatory signals missed by conventional approaches.

---

### Method Overview

scTIE is an autoencoder-based framework with two main stages. See `doc_method.md` for mathematical details and `doc_code.md` for implementation specifics.

**Stage 1 — Temporal Multimodal Integration**:
- Modality-specific encoders (RNA, ATAC) project cells into a shared 64-dimensional embedding space
- Three loss functions: reconstruction (preserve cell-type signals), OT (align time points), modality alignment (pair RNA/ATAC from same cell)
- Waddington-OT estimates cell transition probabilities between consecutive time points; transport matrices updated every 10 epochs
- Coupled batchnorm on RNA input removes scale variation without HVG selection
- Three-phase training: RNA pretraining → ATAC training with frozen RNA → joint fine-tuning
- Final embedding = average of RNA and ATAC embeddings

**Stage 2 — GRN Inference**:
- User selects source ($G_0$) and destination ($G_1$, $G_2$) cell groups
- OT-derived transition probabilities computed for each source cell
- Linear classifier finetuned on pretrained embeddings with KL divergence loss
- Gradient backpropagation identifies top 200 genes and 500 peaks predictive of cell fate
- GRN constructed by linking peaks (within 250kb of TSS) to genes via correlation, then to TFs via motif matching

**Key biological assumptions**:
- Paired measurements (same cell profiled for RNA and ATAC) — removes computational pairing errors
- Temporal data with known time points — OT models cell transitions between consecutive days
- Cell fate is predictable from current gene expression and chromatin accessibility

---

### Evaluation

#### Datasets

| Dataset | Description | Cells | Time Points | Source |
|---------|-------------|-------|-------------|--------|
| Mouse early organogenesis (synthetic) | 10x Genomics multiome; 5 time points E7.5–E8.75 | 24,188 (subset) | 5 | GEO: GSE205117 |
| mESC multiome (real) | Activin A/LiCl differentiation; days 2, 4, 6 | 11,440 | 3 | GEO: GSE223041 |

#### Metrics

- **ARI** (Adjusted Rand Index): clustering agreement with cell type annotations
- **Neighborhood purity**: proportion of same-day/same-batch cells among k-nearest neighbors (lower = better mixing)
- **FOSCTTM**: fraction of samples closer than true match (modality alignment; lower = better)
- **Paired data proportion**: fraction of cells whose matched pair is within k neighbors
- **RMSE**: root mean squared error of transition probability prediction (SVM with radial kernel, 20×5-fold CV)
- **Jaccard index**: overlap of selected peaks with known enhancer databases

#### Comparative Results

**Synthetic data benchmarking** (5 scenarios with batch effects and noise):
- scTIE achieves the largest area in radar plots combining ARI, day purity, and batch purity
- Outperforms Seurat WNN, MultiVI, MOFA+ across all 5 synthetic scenarios
- scAI excluded due to >2 day computational time

**mESC real data**:
- Identifies 17 distinct clusters including all three germ layers and extraembryonic lineages
- Better day alignment and modality alignment than competing methods (Supp Figs S8-S9)
- 81% annotation consistency across pseudoreplicates (random 50/50 splits)

**GRN inference**:
- Gradient-selected features achieve significantly lower RMSE in transition probability prediction vs DE/DA-selected features (Fig 5A)
- Top gradient peaks show tissue-specific enhancer enrichment (mesoderm → facial/limb; endoderm → stomach) vs non-specific DA peaks (Fig 5B)
- Key mesoderm TFs (HHEX, SMAD3, ZIC3, TWIST1, NFAT5) have insignificant DE p-values but high gradient rankings (Supp Table S1)

#### Biological Validation

- Embedding dimension 39 uniquely enriched for activin receptor signaling pathway (consistent with activin A treatment protocol)
- Three distinct definitive endoderm clusters identified, including a Wnt-active cluster potentially linked to lung progenitors
- Epiblast subpopulations with hypoxia-related gene upregulation identified
- Mesoderm GRN captures cardiac development TFs (ZIC3, HHEX, NFAT5) missed by DE analysis

---

### Reproducibility

**Rating: 3/5**

**Justification**: Code is available and functional, but several gaps exist:
- Evaluation code (ARI, purity, SVM benchmarking) is not in the Python repo — likely in R scripts not provided
- Tutorial notebook uses HSPC data, not the mESC data from the paper
- No pre-processed data or pre-trained model weights provided
- The mESC data (GSE223041) is available but requires Cell Ranger Arc preprocessing
- Paper states Adam optimizer but code uses SGD — reproducibility of exact results uncertain

**Environment setup**:
```bash
# Python dependencies
pip install torch==1.9.1 scipy numpy pandas scikit-learn
# Build C++ OT library
cd util && bash build.sh
# Input: sparse NPZ matrices (use process_db.py to convert from H5)
```

**Data availability**:
- Synthetic data: GEO GSE205117 (mouse organogenesis multiome)
- mESC data: GEO GSE223041 (generated by authors)
- Code: https://github.com/SydneyBioX/scTIE

**Common pitfalls**:
1. C++ library (`libot.so`) must be compiled for your platform — `build.sh` may need adjustment
2. OT solving is memory-intensive for large datasets; requires sufficient RAM for full N×N cost matrices
3. Growth rate files must be pre-computed with `calculate_growth_rate.py` or set to uniform (default)
4. Config presets in `config.py` are dataset-specific — new datasets require custom config entries
5. The `anchor_epochs` parameter controls when RNA model is unfrozen — critical for training stability

**Strengths**:
- Unified framework eliminates need for separate integration + GRN tools
- No HVG selection required (coupled batchnorm handles scale variation)
- Gradient-based feature selection is biologically interpretable
- Iterative OT provides better time-point alignment than one-shot methods

**Weaknesses**:
- Requires paired multimodal data (same cell profiled for RNA and ATAC)
- Computational cost of iterative OT solving scales quadratically with cell number
- Evaluation code not fully provided (R-based benchmarking missing)
- Optimizer discrepancy (paper: Adam; code: SGD) raises reproducibility concerns
- Residual encoder branch is initialized but unused — vestigial code

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
