---
layout: default
permalink: /paper-atlas/reusability-ssl-in-scg-9f4b91ba/
title: "Reusability_SSL_in_SCG"
nav: false
wide: true
description: "这篇文章不是提出一个新的神经网络，而是对已有单细胞自监督学习（self-supervised learning, SSL）模型做一次系统的跨域可复用性测试。 源域是大规模单细胞 RNA 测序（scRNA-seq），目标域是空间转录组。论文测试三种已经在 scRNA-seq 上预训练的表示模型： Random Mask：随机遮住一部分基因，让模型重建被遮住的表达值。"
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
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>Reusability_SSL_in_SCG</h1>
    <p>Reusability report: Exploring the transferability of self-supervised learning models from single-cell to spatial transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/CSHCY/Reusability_SSL_in_SCG" target="_blank" rel="noopener noreferrer" aria-label="Open code for Reusability_SSL_in_SCG">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 从单细胞到空间转录组：SSL 模型可复用性方法详解

### 1. 这篇论文真正研究的是什么

这篇文章不是提出一个新的神经网络，而是对已有单细胞自监督学习（self-supervised learning, SSL）模型做一次系统的**跨域可复用性测试**。

源域是大规模单细胞 RNA 测序（scRNA-seq），目标域是空间转录组。论文测试三种已经在 scRNA-seq 上预训练的表示模型：

- Random Mask：随机遮住一部分基因，让模型重建被遮住的表达值。
- GP Mask：按基因程序（gene programme）成组遮挡基因，再进行重建。
- Barlow Twins：对同一个细胞构造两个视图，通过冗余消除目标学习一致表示。

论文的核心问题是：这些模型在 scRNA-seq 中学到的表示，换到 MERSCOPE、Xenium、Slide-seqV2 等空间平台后，是否仍然能支持细胞类型预测和空间区域聚类？

### 2. 为什么已有结果不够

Richter 等人在 *Nature Machine Intelligence*（2024）中系统研究了 SSL 在单细胞基因组学中的有效用法，但主要证据仍处于 scRNA-seq 域内。本论文要补上的空白，是预训练模型能否跨到空间转录组。

这种迁移不能被默认成立，原因包括：

1. 空间平台常只测一个靶向基因面板，而预训练模型的输入空间更宽。
2. 不同技术的计数分布、稀疏性和噪声机制不同。
3. 空间数据除了表达矩阵，还有坐标和邻接图；细胞类型预测与空间域发现需要的表示可能不同。
4. 人到小鼠的迁移还增加了同源基因映射损失。

空间聚类方面，论文使用 STAGATE（*Nature Communications*, 2022）和 GraphST（*Nature Communications*, 2023）作为代表方法，并测试冻结的 SSL 表示能否改善它们。

### 3. 证据边界

2-6 的源数据表。因此下文严格区分：

- **论文结论**：摘要和图像直接表达的结果。
- **代码已验证行为**：从 Python 源码和代表性 notebook 直接读取的实现。
- **解释**：为了帮助理解而给出的机制推断，不等于论文已经证明的因果关系。
- **Not found**：在当前论文和代码快照中没有找到的细节。

### 4. 整体计算流程

```text
源域：约 2220 万个 scRNA-seq 细胞（Fig. 1）
                    |
          预训练三个 SSL 编码器
      +-------------+-------------+
      |             |             |
 Random Mask     GP Mask     Barlow Twins
      |             |             |
      +-------------+-------------+
                    |
目标数据：新 scRNA-seq / MERSCOPE / Xenium / Slide-seqV2
                    |
        归一化 + log1p（代表性 notebook）
                    |
 与预训练的 19,331 个基因按名称对齐
 目标平台未测到的基因位置直接填 0
                    |
      +-------------+------------------+------------------+
      |                                |                  |
 冻结编码器                         部分微调          插补/降质数据
 zero-shot                         fine-tuning         再送入编码器
      |                                |                  |
      +---------------------- 64 维表示 ------------------+
                               |
                  +------------+-------------+
                  |                          |
             5-NN 细胞分类             STAGATE / GraphST
                  |                          |
       accuracy、macro/weighted F1       空间域、ARI、NMI
```

这里的 zero-shot 指“不更新 SSL 编码器”，并不表示完全不用目标域标签。代码仍用目标数据训练部分的标签拟合 5-NN 分类器。

### 5. 三种 SSL 表示是怎样学出来的

当前论文文本没有公式，下面的符号是依据代码整理出的教学性表达，不冒充论文原始记号。

令：

- $x_i \in \mathbb{R}^{G}$ 表示第 $i$ 个细胞的表达向量；代表性 notebook 中 $G=19{,}331$。
- $f_\theta$ 为编码器，$d_\phi$ 为解码器。
- $h_i=f_\theta(x_i)$ 为低维表示，验证的网络最终输出 64 维。
- $m_i$ 为 0/1 遮挡向量。

#### 5.1 Random Mask

代码在 `cellnet_autoencoder.py:655-673` 中对每个基因独立采样保留掩码：

$$
m_{ij}\sim\operatorname{Bernoulli}(1-r).
$$

保留下来的输入会按保留率做缩放：

$$
\widetilde{x}_i=\frac{x_i\odot m_i}{1-r}.
$$

编码器和解码器重建原始表达，但损失只计算在被遮挡的位置：

$$
\mathcal{L}_{\mathrm{RM}}
=\operatorname{mean}\left[(1-m_i)\odot
\ell\left(d_\phi(f_\theta(\widetilde{x}_i)),x_i\right)\right].
$$

代表性迁移 notebook 使用 0.5 的遮挡率，编码器宽度为
$19{,}331\rightarrow512\rightarrow512\rightarrow256\rightarrow256\rightarrow64$。

直观上，Random Mask 强迫模型利用剩余基因预测随机缺失的基因，从而学习全局共表达结构。

#### 5.2 GP Mask

GP Mask 不独立选择基因，而是先把每个基因程序编码成一行 0/1 向量。代码在 `cellnet_autoencoder.py:28-50` 中随机选择一部分基因程序，并将这些程序包含的所有基因一起置零。

若选中的程序集合为 $S$，则属于这些程序的基因满足 $m_j=0$。由于基因程序大小不同且可能重叠，实际遮掉的基因比例记为 $q$，输入缩放为：

$$
\widetilde{x}_i=\frac{x_i\odot m}{1-q}.
$$

损失同样只落在被遮挡的基因位置（`cellnet_autoencoder.py:675-693`）。

这种任务希望模型学习模块化的生物过程，而不只是任意基因之间的相关性。但在代表性 GP zero-shot notebook 中，代码加载 `GPMask.ckpt` 时却传入 `masking_strategy="random"`。推理阶段直接调用 encoder，不会执行遮挡分支，所以权重仍然可用；不过这个参数不一致使实验来源不够清晰。

#### 5.3 Barlow Twins

Barlow Twins 为同一个细胞构造两个视图。代码中第一个视图加入负二项噪声和 dropout，第二个视图保留原输入（`bt.py:160-173`）：

$$
y_i^{(1)}=\operatorname{Dropout}(\operatorname{NegBinNoise}(x_i)),
\qquad y_i^{(2)}=x_i.
$$

两个视图经过共享 MLP 编码器和投影头，得到 $z^{(1)}$、$z^{(2)}$。批内交叉相关矩阵为：

$$
C=\frac{\operatorname{BN}(z^{(1)})^\top\operatorname{BN}(z^{(2)})}{B}.
$$

损失要求对角线接近 1，同时压低非对角项：

$$
\mathcal{L}_{\mathrm{BT}}
=\sum_i(C_{ii}-1)^2+\lambda\sum_{i\ne j}C_{ij}^2.
$$

代码默认 $\lambda=0.0051$，投影头为 `256-256-512-512`，并使用 LARS 和手动优化（`bt.py:57-96`; `cellnet_autoencoder.py:1705-1881`）。

### 6. 空间数据如何进入预训练模型

以 MERSCOPE notebook 为例，代码执行：

1. 从 `adata.raw.X` 恢复表达矩阵。
2. 使用 Scanpy 做总量归一化和 `log1p`。
3. 从预训练模型的 `var.parquet` 读取 19,331 个基因及其固定顺序。
4. 将目标基因名和预训练基因名转成小写后匹配。
5. 创建 `细胞数 x 19,331` 的全零矩阵。
6. 把目标平台实际测到的匹配基因复制到对应列。
7. 预训练词表中存在、但目标平台没有测到的基因保持为 0。

这一步只是**输入空间对齐**，不是基因插补。它解决了张量维度问题，却不会自动消除平台差异。

**解释而非论文已证实机制：**大量零填充可能改变预训练模型看到的表达结构，是空间域迁移困难的一种合理来源。但摘要明确说，域差异的根本原因仍是开放问题。

### 7. 细胞类型预测的两种迁移方式

#### 7.1 Zero-shot 编码器

代表性代码将数据按 70%/15%/15% 划分为训练、验证、测试集。编码器保持冻结，只提取训练集和测试集的表示。随后：

```python
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(train_embeddings, y_train)
predictions = knn.predict(test_embeddings)
```

评价包括 accuracy、weighted F1、macro F1 和每类 classification report。

#### 7.2 Fine-tuning

代表性 Random Mask notebook 的微调过程是：

1. 在 64 维 encoder 输出后增加线性分类头。
2. 先冻结所有 encoder 参数。
3. 只重新开放最后五个参数张量。
4. 用交叉熵训练，优化器为 AdamW，`lr=9e-4`，`weight_decay=0.05`。
5. 最多训练 500 epoch，patience 为 20，按验证损失提前停止。
6. 恢复最佳权重。
7. 最终仍用微调后的 embedding 训练 5-NN，而不是直接用线性分类头打分。

这意味着论文中的 fine-tuning 结果，在代表性实现里衡量的是“微调后表示的 KNN 可分性”。

#### 7.3 从头监督训练

论文结论是：在空间数据上从头训练的模型优于从 scRNA-seq 迁移并微调的 SSL 模型。

作为代码核对，MERSCOPE seed 42 notebook 中：

- Random Mask zero-shot macro F1：0.722。
- Random Mask fine-tuning macro F1：0.791。
- 从头监督模型 macro F1：0.869。

这些数值只是 notebook 内保存的单个随机种子输出，不等于论文图中的多重复汇总值。

### 8. 为什么还要测试插补

一种自然想法是：空间平台测到的基因较少，那么先把未测基因补出来，再输入 scRNA-seq 预训练模型，是否能缩小域差异？

代码中有三条插补路线：

- Tangram：把单细胞映射到空间，再调用 `project_genes` 生成扩展表达矩阵。
- SpaGE：利用空间数据和 scRNA-seq 参考进行基因表达预测。
- uniPort：联合处理空间和单细胞输入，并输出预测特征矩阵。

SpaGE 的多稀疏度 notebook 还会先随机丢弃 20%、40%、60% 或 80% 的共享基因，每个比例重复五次，再进行插补。

**论文结论：**插补没有改善 SSL 细胞类型预测，反而降低性能；缺失程度越高，下降越明显。

**解释而非已证实机制：**插补值可能改变模型预训练时依赖的均值、方差和基因协方差结构。当前证据只能证明性能下降，不能确认这就是原因。

### 9. 跨物种实验

小鼠 Slide-seqV2 notebook 先读取 `ensembl_homologs.csv`，把小鼠 Ensembl ID 映射为人类 Ensembl ID，再对齐到人类预训练模型的 19,331 基因空间。

因此跨物种流程为：

```text
小鼠表达矩阵
  -> 小鼠 Ensembl ID
  -> 人类同源基因 ID
  -> 19,331 维人类预训练词表
  -> SSL encoder
  -> 5-NN 细胞分类
```

Fig. 5 显示，从人肾到小鼠肾的性能变化总体为负，说明同源映射并不能消除物种差异。这里混合了至少三类因素：物种差异、基因映射损失和空间平台差异；当前材料不能把它们分别定量。

### 10. SSL 表示如何帮助空间聚类

论文的一个重要结果是：SSL 对直接空间细胞分类的迁移有限，但冻结表示仍能改善空间域聚类。

#### STAGATE 路线

验证的 notebook：

1. 按 MERSCOPE 切片建立半径为 150 的空间网络。
2. 用 `adata.obsm['SSL_RM_ZS_42']` 构造新的 AnnData，其 `X` 就是 Random Mask embedding。
3. 训练 STAGATE 100 epoch。
4. 在 STAGATE 表示上构图。
5. 用 `mclust_R` 聚成 10 个空间域。
6. 对每个切片计算 NMI 和 ARI。

#### GraphST 路线

验证的 notebook：

1. 读取已经保存的邻域和邻接矩阵。
2. 将 `SSL_RM_ZS_42` 作为新 AnnData 的 `X`。
3. 对每个切片训练 GraphST 100 epoch。
4. 聚成 10 个空间域。
5. 计算 NMI 和 ARI。

一个重要实现细节是：在检查到的 STAGATE/GraphST 路线中，代码不是把原始表达和 embedding 拼接，而是直接让空间方法使用 embedding 作为输入矩阵。

Fig. 6 和摘要共同支持 Random Mask 增强版本 STAGATE-RM、GraphST-RM 的空间聚类效果更好。这说明“是否可迁移”依赖任务：同一个表示可能不够支持精细的细胞类型决策，却能提供更平滑、更稳定的空间域结构。

### 11. 如何理解整篇论文的结论

最准确的总结不是“SSL 能迁移”或“SSL 不能迁移”，而是：

| 场景 | 结论 |
|---|---|
| 新 scRNA-seq 数据 | 预训练表示仍保留有用信号 |
| 空间细胞类型预测 | 存在明显域差异，从头监督训练更强 |
| 插补后再迁移 | 通常更差，稀疏度越高下降越明显 |
| 人到小鼠 | 同源映射后仍有显著性能损失 |
| 空间域聚类 | Random Mask embedding 可改善 STAGATE/GraphST |

Random Mask 在整体基准中表现最好，但文章并没有证明其优势来自某个唯一机制。

### 12. 代码与论文的对应关系

| 论文概念 | 代码位置 | 状态 |
|---|---|---|
| Random Mask 重建目标 | `self_supervision/models/lightning_modules/cellnet_autoencoder.py:655-673` | Exact |
| GP Mask 程序级遮挡 | `cellnet_autoencoder.py:28-50,675-693` | Exact |
| Barlow Twins 目标 | `self_supervision/models/contrastive/bt.py:57-96,160-173` | Exact |
| 模型选择入口 | `self_supervision/estimator/cellnet.py:49-69` | Exact |
| MERSCOPE zero-shot | `MERSCOPE_human_neocortex_random_mask_zero_shot_42.ipynb` | Notebook |
| MERSCOPE fine-tuning | `MERSCOPE_human_neocortex_random_mask_fine_tune_42.ipynb` | Notebook |
| Xenium 插补 | `imputation_to_generate_imputed_datasets/*.ipynb` | Notebook |
| 小鼠同源基因映射 | `slide_seq_mouse_kidney_random_mask_zero_shot_42.ipynb` | Notebook |
| STAGATE-RM | `spatial_clustering_MERSCOPE_human_neocortex/random_mask_zero_shot_stagate_*.ipynb` | Notebook |
| GraphST-RM | `spatial_clustering_MERSCOPE_human_neocortex_GraphST/random_mask_zero_shot_GraphST_*.ipynb` | Notebook |

### 13. 复现时需要特别注意

当前代码快照的可复现性约为 **2.5/5**：

- 优点：三种核心 SSL 实现都在；数据集/任务 notebook 很丰富；代表性结果保存在 notebook 输出中。
- 外部依赖：数据集和预训练 checkpoint 不在仓库内。
- 路径问题：notebook 使用 `../../dataset/`、`../../sc_pretrained/`，个别文件还包含 `[local path omitted]` 绝对路径。
- 环境问题：主 requirements 未包含 STAGATE、CellCharter、Tangram、SpaGE、uniPort 等多个 notebook 依赖。
- 安装问题：两个 `setup.py` 都读取缺失的 `requirements.txt` 和 `README.rst`。
- 组织问题：113 个 notebook 高度重复，没有统一的参数化 benchmark driver。
- 证据缺口：没有当前论文的 Methods 正文、补充材料、Fig. 2-6 源数据表和汇总结果 CSV。

### 14. 尚未找到的细节

- **Not found：**论文原始公式和完整 Methods/Results 叙述。搜索范围：`paper.md:1-307`。
- **Not found：**Supplementary Notes 1-8、Supplementary Table 1、Supplementary Figs. 1-11。
- **Not found：**Fig. 2-6 的 XLSX 源数据，只保留了下载链接和说明。
- **Not found：**所有随机种子的准确汇总规则、统计检验名称和完整超参数表。
- **未验证：**当前机器上的端到端运行结果。本阶段没有下载外部数据/checkpoint，也没有执行实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Reusability of scRNA-seq SSL Models in Spatial Transcriptomics

### Overview

Han et al. present a reusability benchmark for three self-supervised learning models pretrained on single-cell RNA sequencing: **Random Mask**, **gene programme (GP) Mask**, and **Barlow Twins**. The question is not whether these encoders work in their original setting, but whether their learned representations survive a shift to spatial transcriptomics, where assays measure different gene panels, exhibit different sparsity, and add spatial structure.

The study extends Richter et al.'s scRNA-seq SSL evaluation (*Nature Machine Intelligence*, 2024), which had not established transfer to spatial data. It evaluates cell-type prediction, gene-imputation/degradation scenarios, cross-species transfer, and spatial clustering. Spatial baselines include STAGATE (*Nature Communications*, 2022) and GraphST (*Nature Communications*, 2023).

### Benchmark Design

The pretrained encoders are assessed in two main transfer modes:

- **Zero-shot encoder:** keep the SSL encoder frozen, extract target-domain embeddings, and train a downstream 5-nearest-neighbour classifier on target labels.
- **Fine-tuning:** attach a classification head, update a small tail of the encoder on target labels, then evaluate the resulting embedding with the same KNN protocol.

The verified notebooks normalize and log-transform target data, align genes case-insensitively to a fixed 19,331-gene pretrained vocabulary, and set unmeasured genes to zero. Additional workflows generate imputed Xenium data with Tangram, SpaGE, or uniPort; map mouse genes to human homologues; and feed frozen embeddings into STAGATE or GraphST for spatial-domain clustering.

### Evaluation

The paper covers:

- New scRNA-seq datasets: developing human neocortex and human breast cancer.
- Spatial cell typing: MERSCOPE human neocortex, Xenium breast cancer, and Slide-seqV2 kidney data.
- Cross-species transfer: Slide-seqV2 human versus mouse kidney.
- Spatial clustering: MERSCOPE human neocortex with STAGATE/GraphST and SSL-enhanced variants.
- Metrics visible in the paper/code: macro and weighted F1 for cell typing; ARI and NMI for spatial clustering; pairwise statistical comparisons in Figs. 2-6.

### Main Findings

1. **Random Mask is the strongest SSL model overall.** The abstract and figures consistently place it ahead of GP Mask and Barlow Twins across the combined benchmark, although no single transfer mode dominates every dataset.
2. **The spatial domain gap remains substantial.** Models trained from scratch on spatial data outperform fine-tuned scRNA-seq-pretrained models for cell-type prediction. The paper leaves the underlying causes open.
3. **Imputation does not repair the gap.** Imputed genes generally reduce prediction performance, and the degradation becomes stronger as more genes are removed before imputation.
4. **Cross-species transfer is difficult.** Performance falls from human to mouse kidney even after mouse-to-human homology mapping.
5. **Reuse is task-dependent rather than uniformly unsuccessful.** Frozen Random Mask embeddings improve selected spatial clustering workflows, notably STAGATE-RM and GraphST-RM, even though direct spatial cell typing remains limited.

As a representative code check, the stored MERSCOPE seed-42 notebooks report macro F1 values of 0.722 for Random Mask zero-shot, 0.791 after Random Mask fine-tuning, and 0.869 for the supervised from-scratch comparison. These are notebook outputs, not the paper's multi-seed aggregate.

### Interpretation

The results argue against treating a pretrained single-cell encoder as a universally reusable foundation model. The representation can preserve useful biological structure while still being mismatched to the exact target task. Zero-filled gene-panel alignment may be sufficient for spatial clustering features but insufficient for accurate cell-type decision boundaries. This is an interpretation of the verified pipeline, not a causal mechanism established by the paper.

### Reproducibility

**Rating: 2.5/5.** The public snapshot contains the core implementations of all three SSL objectives and 113 dataset/task notebooks, so the intended workflows are inspectable. However, reproduction is not turnkey:

- Datasets and pretrained checkpoints are external.
- Many notebooks contain hard-coded relative or machine-specific paths.
- The environment file is incomplete and mostly unpinned; several notebook dependencies are absent.
- Both setup scripts refer to missing `requirements.txt` and `README.rst` files.
- The acquired paper lacks the Methods/Results narrative, Supplementary Notes, and source-data spreadsheets for Figs. 2-6.
- No consolidated result tables or single end-to-end benchmark driver are retained.

The documentation therefore supports a medium-confidence paper-code match for the core methods and representative experiments, but not a complete numerical reproduction of every published aggregate.

### Evidence Limits

- **Paper claim:** qualitative conclusions above are grounded in the abstract and opened figure images.
- **Code-verified:** preprocessing, encoder objectives, representative transfer loops, imputation generation, homology mapping, and STAGATE/GraphST embedding inputs were directly inspected.
- **Not found:** exact paper equations, complete hyperparameter tables, statistical test definitions, replicate aggregation, supplementary experiments, and source-data values.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
