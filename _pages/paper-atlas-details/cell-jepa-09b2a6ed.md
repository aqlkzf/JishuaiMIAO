---
layout: default
permalink: /paper-atlas/cell-jepa-09b2a6ed/
title: "Cell-JEPA"
nav: false
wide: true
description: "单细胞 RNA 测序把每个细胞表示成一个跨越数万基因的表达向量，但这个向量既稀疏又嘈杂：分子捕获效率、测序深度和随机采样都会改变观测到的表达值。许多单细胞基础模型把“恢复被遮盖的基因或表达值”作为预训练任务。这样做能提供密集监督，却也可能迫使模型记住测量噪声，而不是只保留决定细胞身份和调控状态的稳定结构。 Cell-JEPA 的核心问题因此是：能否让模型从不完整的表达谱中预测完整细胞的潜在表示，同时仍保留必要的基因级信息？"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>Cell-JEPA</h1>
    <p>Cell-JEPA: Latent Representation Learning for Single-Cell Transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Cell-JEPA 方法详解：在潜在空间中学习单细胞表示

### 1. 它要解决什么问题？

单细胞 RNA 测序把每个细胞表示成一个跨越数万基因的表达向量，但这个向量既稀疏又嘈杂：分子捕获效率、测序深度和随机采样都会改变观测到的表达值。许多单细胞基础模型把“恢复被遮盖的基因或表达值”作为预训练任务。这样做能提供密集监督，却也可能迫使模型记住测量噪声，而不是只保留决定细胞身份和调控状态的稳定结构。

Cell-JEPA 的核心问题因此是：**能否让模型从不完整的表达谱中预测完整细胞的潜在表示，同时仍保留必要的基因级信息？**

### 2. 现有方法为什么不够？

- **scGPT**（*Nature Methods*, 2024）在结构化注意力下预测未知基因的表达，并可通过置信度驱动的多轮生成逐步扩展已知基因集合。它的主要学习信号仍位于表达值空间。
- **Geneformer**（*Nature*, 2023）采用类似 BERT 的掩码基因 token 恢复任务，主要预测被遮盖的基因身份。
- **scVI**（*Nature Methods*, 2018）用概率生成模型和变分推断学习低维细胞状态，但其生成目标仍需解释观测计数。
- **UCE**（论文参考文献未给出正式期刊信息）遮盖已表达基因并预测表达存在性，以获得跨组织、跨物种表示。
- **GeneJEPA**（*bioRxiv*, 2025）同样把 JEPA 引入转录组，但侧重对被遮盖基因子集做潜在空间预测。Cell-JEPA 的区别是保留显式的基因表达重建项，并在细胞级 `<cls>` 表示上增加 JEPA 目标。

Cell-JEPA 并不证明重建目标本身无效；它提出的是一个互补设计：重建项保留局部表达细节，潜在预测项约束细胞级语义的一致性。

### 3. 输入、输出与基本假设

**输入：** 一个稀疏的 cell-by-gene 计数矩阵。对每个细胞，只保留非零基因，形成

$$
\{(y_k,v_k)\}_{k=1}^{L},
$$

其中 $y_k$ 是基因 ID，$v_k$ 是该基因的表达值。

**预训练输出：**

1. 学生网络的 `<cls>` 隐状态，即细胞表示；
2. 被遮盖基因的表达值预测；
3. 学生表示经 predictor 后对教师细胞表示的预测。

**下游输出：** 用于细胞类型聚类的细胞嵌入，或给定对照表达和扰动标签后的扰动表达预测。

方法隐含的关键假设是：细胞状态冗余地编码在多个基因中，因此局部观测足以预测较稳定的整体细胞表示；缓慢更新且读取完整视图的教师可以提供比单个噪声表达值更稳定的训练目标。

### 4. 从输入到表示的完整流程

```text
稀疏 cell × gene 计数
        │ 仅保留非零基因
        ▼
每个细胞的 (gene ID, expression) 集合
        │ 非零值做 50 档细胞内分位数离散化
        │ 超过 600 个表达基因时均匀随机采样 600 个
        ▼
gene embedding + value embedding + <cls>
        │
        ├── 完整视图 Z ─────────────► EMA 教师 g_T ─► 目标表示 e
        │                                  ▲              │ stop-gradient
        │                                  │ EMA          │
        └── 遮盖 15% 表达值                │              │
             ▼                             │              │
          遮盖视图 Z~ ─► 学生 g_S ─► ê ─► predictor ─► ẽ ┘
                              │
                              └── token 隐状态 ─► 表达预测头
                                                    │
                 被遮盖位置的 MSE ◄─────────────────┘

            优化：L_pre-train = L_rec + 1000 L_JEPA
```

#### 步骤 1：每个细胞内做表达离散化

对非零表达值做 $B=50$ 的细胞内分位数分箱。它保留细胞内部的相对表达顺序，同时降低不同细胞原始计数尺度的影响。若一个细胞表达超过 600 个基因，则均匀随机采样 600 个；不同 epoch 可能看到同一细胞的不同子集。

#### 步骤 2：构造 token

基因 ID 和分箱后的表达值分别嵌入，再逐元素相加：

$$
\mathbf y_i=f_{\mathrm{gene}}(y_i),\qquad
\mathbf v_i=f_{\mathrm{val}}(v_i),\qquad
\mathbf z_i=\mathbf y_i+\mathbf v_i.
$$

序列开头加入 `<cls>`，批内补齐到 $L_{\max}+1$。基因没有天然词序，所以这里的 Transformer 更接近处理一组带表达值的基因 token。

#### 步骤 3：为同一细胞生成两个视图

遮盖只作用于**表达值**，不遮盖基因 ID。被遮盖位置的值替换为 $v_{\mathrm{mask}}=-1$：

$$
\tilde{\mathbf z}_i=\mathbf y_i+f_{\mathrm{val}}(-1).
$$

学生读取遮盖视图 $\tilde{\mathbf Z}$，教师读取完整视图 $\mathbf Z$：

$$
\hat{\mathbf H}=g_{\mathrm S}(\tilde{\mathbf Z}),\qquad
\mathbf H=g_{\mathrm T}(\mathbf Z),
$$

$$
\hat{\mathbf e}=\hat{\mathbf H}_0,\qquad
\mathbf e=\mathbf H_0.
$$

这里有一个必须保留的论文歧义：第 2.2.2 节有一句话把两个视图写反；但显示公式、Figure 2 和后续损失定义都支持“遮盖学生、完整教师”。当前没有可归属于论文的官方代码来进一步裁决。

#### 步骤 4：阻止被遮盖目标之间的信息泄漏

每个被遮盖 token 可以关注全部未遮盖 token 和它自身，但不能关注其他被遮盖 token。这样模型不能从另一个同时被遮盖的目标直接获取答案，却仍能使用所有可见基因作为上下文。

#### 步骤 5：在细胞级潜在空间做预测

学生 `<cls>` 表示先经过 predictor：

$$
\tilde{\mathbf e}=p(\hat{\mathbf e}).
$$

然后最小化它与停止梯度后的教师表示之间的余弦距离：

$$
\mathcal L_{\mathrm{JEPA}}
=1-
\frac{\tilde{\mathbf e}^{\top}\mathrm{sg}(\mathbf e)}
{\|\tilde{\mathbf e}\|_2\,\|\mathrm{sg}(\mathbf e)\|_2}.
$$

教师不接收该损失的梯度，而是由学生参数的指数滑动平均更新：

$$
\theta_{\mathrm T}\leftarrow m\theta_{\mathrm T}+(1-m)\theta_{\mathrm S}.
$$

#### 步骤 6：同时恢复被遮盖的表达值

学生的 token 隐状态通过逐 token 的 MLP 预测表达值：

$$
\hat{\mathbf v}=r(\hat{\mathbf H}),
$$

$$
\mathcal L_{\mathrm{rec}}
=\frac{1}{|\mathcal U_{\mathrm{mask}}|}
\sum_{i\in\mathcal U_{\mathrm{mask}}}(\hat{\mathbf v}_i-v_i)^2.
$$

Cell-JEPA 一次前向同时预测所有被遮盖基因，而不是使用 scGPT 的多轮置信度扩展推断。

#### 步骤 7：联合优化

$$
\mathcal L_{\mathrm{pre-train}}
=w_{\mathrm{rec}}\mathcal L_{\mathrm{rec}}
+w_{\mathrm{JEPA}}\mathcal L_{\mathrm{JEPA}}.
$$

论文设置 $w_{\mathrm{rec}}=1$、$w_{\mathrm{JEPA}}=1000$，并说明这是为了补偿数值尺度差异，不能仅凭权重断言 JEPA 梯度一定占主导。

### 5. 下游任务如何使用这个表示？

#### PBMC 细胞表示微调

普通微调联合四个目标：

- **GEP：** 被遮盖表达值的 MSE；
- **GEPC：** 让全局细胞表示和基因查询共同预测表达值；
- **ECS：** 以同一细胞类型为正样本的监督对比损失；
- **JEPA：** 继续保持细胞级潜在预测。

总损失为四项的加权和。PBMC-10K 实验使用 40% 遮盖率、batch size 64、学习率 $10^{-4}$、30 个 epoch。

#### 扰动响应预测

模型把扰动 ID embedding 加入基因和值的 embedding：

$$
\tilde{\mathbf z}^{\mathrm{pert}}_i
=\mathbf y_i+\mathbf p_i+\mathbf v_i.
$$

学生预测完整的扰动后表达谱，并计算全基因 MSE；教师读取真实扰动后表达构成的目标视图，提供扰动版 JEPA 目标。该分支不遮盖输入，Appendix E.3 还把教师改为**冻结副本**而不是 EMA 教师。总目标由扰动重建、扰动 JEPA 和 ECS 组成。

### 6. 实验如何支持论文主张？

#### 预训练与对照

Cell-JEPA 和 scGPT 都在 800,000 个 CELLxGENE 人肾细胞上训练，论文称两者使用同一数据和训练 recipe，主要差别是预训练目标。这使比较更接近对 JEPA 项的受控检验，但比较只覆盖 scGPT 这一种骨干/基线。

#### PBMC-10K 微调

Cell-JEPA 在四个聚类指标上都高于 scGPT：AvgBIO 0.7830 对 0.7531，NMI 0.7761 对 0.7652，ASW 0.7256 对 0.7100，ARI 0.8472 对 0.7842。

#### PBMC-10K 零样本

论文报告 Cell-JEPA 的 AvgBIO 相对提高 36%，并称所有聚类指标均提高。不过本地转换文本没有给出 Table 2 的完整数值，本地图像也缺少两个零样本面板，因此这一结论只能标为**论文报告**，不能视为本地图像或代码复核结果。

#### K562 扰动预测

在 Norman 未见单基因扰动上，Cell-JEPA 的 all-gene / DE / top-20 DE Pearson 为 0.787 / 0.592 / 0.565，scGPT 为 0.631 / 0.276 / 0.278；在 Adamson 上分别为 0.937 / 0.741 / 0.720 和 0.905 / 0.699 / 0.677。它改善的是扰动后**绝对状态**拟合。change-from-control 的 delta 指标仍低且并不稳定提高，说明“识别细胞处于什么状态”和“精确预测状态如何改变”不是同一个问题。

### 7. 应当怎样理解它的贡献？

**论文主张：** 在相同 scGPT 骨干和训练数据下，加入细胞级 JEPA 目标能改善细胞类型表示的迁移，并改善扰动后绝对表达状态预测。

**合理解释：** 完整视图的慢教师为遮盖学生提供细胞级目标，可能减少模型对单个噪声表达值的依赖；重建项则防止表示丢失基因级细节。这是对架构的解释，并不是论文通过消融直接证明的机制。

**作者提出的假设：** JEPA 强调跨视图不变性，这可能有利于细胞身份，却压低对微小扰动偏移的敏感性，因此 delta 指标没有同步改善。论文将其写作合理解释而非已验证因果机制。

**代码验证：** 无。没有发现可归属于该论文的官方实现、checkpoint 或可运行评估脚本。一个同名 GitHub 项目因 README 表明其为独立 benchmark 项目且无法建立论文来源关系而被排除。

### 8. 复现时仍缺什么？

论文给出了 12 层、512 维、8 头的骨干，预训练 batch size 32、学习率 $10^{-4}$、4 个 epoch、单张 A5000 约一天等主要设置。但以下内容在完整 884 行论文、arXiv HTML、采集 sidecar 和三张本地图像中均 **Not found**：

- EMA 动量 $m$ 及其调度；
- ECS 温度 $\tau$；
- 分位数分箱在 ties/空箱时的精确规则；
- value MLP 和各 predictor/projector 的完整层宽；
- 随机基因采样与遮盖的精确 RNG/seed 规则；
- 官方代码、checkpoint、数据清单脚本和端到端评估命令；
- 零样本 Table 2 的完整数值与 Figure 3(b-d) 本地图像。

因此，Cell-JEPA 的算法思想和主要训练超参数可以从论文重建，但精确复现和论文结果核验仍需要作者实现、checkpoint 或更完整的补充材料。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Cell-JEPA: Latent Representation Learning for Single-Cell Transcriptomics

### Problem and motivation

Cell-JEPA addresses representation learning for sparse, noisy single-cell RNA-seq profiles. The paper argues that reconstruction-only objectives, used by models such as scGPT and Geneformer, can preserve sequencing-depth, capture-efficiency, and dropout variation because they optimize targets in the observed measurement space. Cell-JEPA instead adds a latent-space prediction objective while retaining gene-level reconstruction, with the goal of learning cell embeddings that better capture stable cellular programs.

### Proposed method

Each cell is represented by its nonzero gene/value pairs. Nonzero values are quantile-binned into 50 bins and cells longer than 600 expressed genes are uniformly subsampled. Gene and value embeddings are summed and a `<cls>` token provides a cell-level embedding. A student scGPT-style Transformer receives expression values masked at 15% of positions; an EMA teacher receives the corresponding unmasked view. A predictor maps the student `<cls>` embedding toward the teacher embedding using cosine distance with stop-gradient on the target. In parallel, an MLP reconstructs all masked expression values with mean squared error. The pre-training loss is

$$
\mathcal{L}_{\mathrm{pre-train}}=w_{\mathrm{rec}}\mathcal{L}_{\mathrm{rec}}+w_{\mathrm{JEPA}}\mathcal{L}_{\mathrm{JEPA}}.
$$

The paper's recipe uses weights 1 and 1000, respectively. The student/teacher view assignment is supported by Equation (2.2), Figure 2, and the masking rationale, although one prose sentence in Section 2.2.2 reverses it.

### Evaluation and reported results

The foundation models are pre-trained on 800,000 human kidney cells selected from CELLxGENE Census (2023-05-15). The controlled baseline is scGPT trained on the same corpus and recipe, differing in the pre-training objective. Downstream evaluation has three settings:

- **PBMC-10K finetuning:** 9:1 train/validation split with seed 42, 3,346 highly variable genes, and AvgBIO, NMI, ASW, and ARI metrics. Cell-JEPA scores 0.7830 AvgBIO versus 0.7531 for scGPT; NMI is 0.7761 versus 0.7652, ASW 0.7256 versus 0.7100, and ARI 0.8472 versus 0.7842.
- **PBMC-10K zero-shot:** pre-trained checkpoints are evaluated without task-specific finetuning. The paper reports a 36% relative AvgBIO improvement for Cell-JEPA and consistent gains across the clustering metrics. The corresponding result panels are not present in the local image extraction, so this comparison is supported by the paper text/table reference rather than direct local image comparison.
- **Perturbation prediction:** GEARS-processed Adamson and Norman K562 Perturb-seq data use perturbation-level held-out splits. Cell-JEPA improves absolute-state and DE-focused Pearson correlations: Norman 0.787/0.592/0.565 versus 0.631/0.276/0.278 for scGPT, and Adamson 0.937/0.741/0.720 versus 0.905/0.699/0.677 for scGPT (all-gene, DE, top-20 DE). Delta-from-control correlations remain low and are not consistently improved, especially on Adamson.

### Reproducibility and limitations

The paper reports a 512-dimensional, 12-block, 8-head Transformer; AdamW pre-training with batch size 32, learning rate $10^{-4}$, weight decay $2\times10^{-4}$, 0.9 epoch-wise decay, dropout 0.2, four epochs, and roughly one day on one A5000. PBMC finetuning uses mask ratio 0.40, batch size 64, 30 epochs, and about two hours on one A5000. Perturbation finetuning uses no masking, batch size 64, 15 epochs, JEPA/reconstruction weights 1, ECS weight 0.8, and about two hours on one A100.

No attributable official implementation, checkpoint, or runnable evaluation script was found in the acquired paper source or sidecars; this workspace is therefore **paper-only** and has no code-verified behavior. The EMA momentum, ECS temperature, exact value-MLP/binning conventions, masking RNG details, checkpoint availability, and full zero-shot Table 2 values are **Not found** after searching the 884-line paper, arXiv HTML metadata, acquisition sidecars, and local figures. The local `figure_03.png` contains only the scGPT finetuned UMAP (AvgBIO 0.7531), so comparative visual claims are not independently image-verified.

Overall, the evidence supports Cell-JEPA as a hybrid representation-learning objective that improves reported cell-type transfer and absolute perturbation-state prediction over scGPT, while leaving change-from-control prediction and implementation reproducibility as open limitations.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
