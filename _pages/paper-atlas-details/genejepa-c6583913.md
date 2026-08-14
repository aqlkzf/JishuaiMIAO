---
layout: default
permalink: /paper-atlas/genejepa-c6583913/
title: "GeneJepa"
nav: false
wide: true
description: "单细胞 RNA 测序把一个细胞表示成高维、稀疏、带有大量技术噪声的基因表达向量。许多单细胞基础模型沿用语言模型思路：把基因和离散化后的表达量变成 token，再通过掩码重建或生成目标学习表示。论文认为这种做法存在三个结构性问题： 精确重建 count 会让模型过度关注 dropout、测序深度和实验批次等低层统计； 一个细胞中表达的基因本质上是集合，不存在自然的单词顺序； 表达量分箱会损失连续定量信息。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>GeneJepa</h1>
    <p>GeneJepa: A Predictive World Model of the Transcriptome</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/BiostateAI/GeneJEPA" target="_blank" rel="noopener noreferrer" aria-label="Open code for GeneJepa">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GeneJepa 方法详解

### 1. 这篇论文要解决什么问题

单细胞 RNA 测序把一个细胞表示成高维、稀疏、带有大量技术噪声的基因表达向量。许多单细胞基础模型沿用语言模型思路：把基因和离散化后的表达量变成 token，再通过掩码重建或生成目标学习表示。论文认为这种做法存在三个结构性问题：

1. 精确重建 count 会让模型过度关注 dropout、测序深度和实验批次等低层统计；
2. 一个细胞中表达的基因本质上是集合，不存在自然的单词顺序；
3. 表达量分箱会损失连续定量信息。

代表性对照包括 scBERT（*Nature Machine Intelligence*, 2022）、UCE（bioRxiv, 2023）和 scGPT（*Nature Methods*, 2024）。GeneJepa 的核心选择是：不预测被遮住基因的原始表达值，而是根据可见基因集合，预测被遮住基因集合的潜在表示。

换句话说，它学习的问题不是“这个 count 应该是多少”，而是“已观察到的基因状态能否推断出未观察部分所处的细胞状态”。

### 2. 核心思想：在表示空间中做 JEPA 预测

对于一个细胞，输入是无序稀疏集合

$$
x=\{(i_n,v_n)\}_{n=1}^{N},
$$

其中 $i_n$ 是基因词表索引，$v_n$ 是经过 `log1p` 和全局标准化后的连续表达值。

训练时随机把基因分成两个不相交的集合：

- 上下文集合 $x_{\mathrm{ctx}}$：学生编码器能看到的基因；
- 目标集合 $x_{\mathrm{tgt}}$：教师编码器能看到、但学生需要预测的基因。

学生编码器 $f_\theta$ 得到上下文表示

$$
z_{\mathrm{ctx}}=f_\theta(x_{\mathrm{ctx}}),
$$

预测器 $p_\phi$ 只接收这个向量：

$$
\hat z_{\mathrm{tgt}}=p_\phi(z_{\mathrm{ctx}}).
$$

教师编码器 $f_\xi$ 从目标基因得到监督信号：

$$
z_{\mathrm{tgt}}=f_\xi(x_{\mathrm{tgt}}).
$$

训练目标是让 $\hat z_{\mathrm{tgt}}$ 接近停止梯度后的 $z_{\mathrm{tgt}}$。因此，模型不需要逐基因解码 count，也不需要负样本。

### 3. 从输入到输出的完整计算流程

```text
Tahoe-100M 稀疏单细胞表达
        |
        v
基因映射 -> log1p -> 固定全局均值/方差标准化
        |
        v
批内拼接为 indices / values / offsets
        |
        v
每个细胞重新随机打乱基因位置
        |
        +-----------------------------+
        |                             |
  context，约 55%               target，约 45%
        |                             |
        v                             v
学生 Perceiver f_theta          EMA 教师 f_xi
        |                             |
      z_ctx                         z_tgt
        |                             |
        v                             | stop-gradient
MLP 预测器 p_phi                     |
        |                             |
        +------> z_hat_tgt <----------+
                     |
                     v
          余弦预测损失 + 防塌缩正则
                     |
                     v
      反向传播更新学生/预测器；EMA 更新教师

推理：完整或选定基因集合 -> EMA 教师编码器 -> 细胞向量 z
```

下面逐步拆解每个模块。

### 4. 数据预处理与变长批处理

论文在 Tahoe-100M 上预训练。代码中的每个样本包含基因 ID、表达值、药物和细胞系元数据。表达值先变换为

$$
u=\log(1+x), \qquad
v=\frac{u-\mu_{\mathrm{global}}}{\sigma_{\mathrm{global}}+10^{-6}}.
$$

这里的均值和标准差来自训练数据的大规模子集，而不是当前 mini-batch。这样可以避免不同 batch 的统计波动改变输入尺度。

不同细胞的非零基因数量不同。代码没有立刻把所有细胞补齐到同一长度，而是把基因索引和表达值分别拼接成一维向量，再用 `offsets` 标记每个细胞的起止位置：

- `indices`: `[总 token 数]`；
- `values`: `[总 token 数]`；
- `offsets`: `[batch size + 1]`。

进入 Perceiver 前才根据 offsets 拆分并 padding。对应实现位于 `genejepa/data.py:309-342`。

### 5. 连续表达 tokenizer

每个基因 token 同时编码“它是谁”和“它表达多少”。

#### 5.1 基因身份分支

$$
e_{\mathrm{id}}=\operatorname{Embedding}(i).
$$

这是普通的可学习 embedding table，使不同基因拥有不同身份向量。

#### 5.2 连续表达分支

论文 Markdown 转换丢失了部分显示公式；根据论文文字和代码，可以明确恢复实际计算：

$$
\phi(v)=[\sin(v\omega_1),\ldots,\sin(v\omega_{N_f}),
\cos(v\omega_1),\ldots,\cos(v\omega_{N_f})],
$$

$$
e_{\mathrm{val}}=\operatorname{MLP}_{\mathrm{val}}(\phi(v)).
$$

代码默认使用 64 个对数间隔频率，范围 0.1 到 100。Fourier 特征把一个标量映射到多尺度周期基底，使后续 MLP 更容易表达复杂的连续响应。

#### 5.3 融合

$$
t=\operatorname{Proj}([e_{\mathrm{id}};e_{\mathrm{val}}])\in\mathbb{R}^{768}.
$$

默认情况下，768 维中一半分配给身份分支，一半分配给表达分支。拼接后经过 LayerNorm、线性层、GELU 和第二个 LayerNorm。直接实现见 `genejepa/tokenizer.py:15-59`。

### 6. Perceiver 编码器：先读，再思考，再汇总

GeneJepa 使用 Perceiver 的原因是输入基因数 $N$ 可变，而且可能很大。它用固定数量的潜变量读取输入，从而把后续计算规模与 $N$ 解耦。

#### 6.1 Read：潜变量对基因 token 做交叉注意力

设 token 矩阵为 $T\in\mathbb{R}^{N\times d}$，固定可学习潜变量为 $L\in\mathbb{R}^{N_{\mathrm{lat}}\times d}$。代码实现的标准形式为

$$
Q=\operatorname{LN}(L)W_Q,\qquad [K,V]=\operatorname{LN}(T)W_{KV},
$$

$$
L'=L+\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_h}}\right)VW_O.
$$

默认 $N_{\mathrm{lat}}=512$，注意力头数为 12。

当输入较长时，代码把 key/value 按块处理，不构造完整的 `512 x N` 注意力矩阵。算法分两遍：第一遍找每个 query 的最大分数，第二遍累计 softmax 分子、分母和加权 value。内部统一用 float32，最后再转换回原 dtype。这一实现与论文附录中“在线 softmax + float32 accumulator”的描述一致，见 `genejepa/models.py:47-163`。

#### 6.2 Think：只在固定潜变量上做 Transformer

读入信息后，512 个潜变量经过 24 层 latent Transformer。每层包含自注意力和四倍扩展的前馈网络。因为潜变量数量固定，这部分主要计算量不随输入基因数增长。代码还使用 gradient checkpointing 降低训练显存，见 `genejepa/models.py:12-25,204-212`。

#### 6.3 Pool：得到一个细胞或基因子集向量

最后对归一化后的潜变量取平均：

$$
z=\frac{1}{N_{\mathrm{lat}}}\sum_{\ell=1}^{N_{\mathrm{lat}}}
\operatorname{LN}(L^{(D)}_\ell).
$$

输出维度默认是 768。上下文、目标以及常规推理都使用同一编码器结构。

### 7. 随机遮蔽与预测器

每次前向传播，代码都会对一个细胞中的 token 位置重新随机排列，再取约 45% 作为目标。默认只有一个大目标块，其余基因作为上下文。

实现还设置了硬约束：上下文至少 512 个基因，目标至少 16 个基因。因此少于 528 个已映射表达基因的细胞不会参与该次 JEPA 损失。这是重要的代码行为，但论文正文没有明确说明。

预测器是默认深度为 3 的 MLP。它只接收 $z_{\mathrm{ctx}}$，不会接收目标基因 ID、目标位置或目标内容提示。这迫使上下文向量包含足够完整的细胞状态信息，不能依靠目标泄漏完成任务。对应代码为 `genejepa/models.py:218-256,278-440`。

### 8. EMA 教师为什么能稳定目标

教师结构与学生相同，但不通过反向传播更新。更新规则是

$$
\xi\leftarrow\beta\xi+(1-\beta)\theta.
$$

这样，学生要追赶一个变化较慢的目标，而不是学生和教师同时通过梯度相互追逐。

代码在训练开始时把学生权重硬拷贝给教师，并冻结教师参数。EMA 衰减率随后按余弦曲线增加，且前 2,000 step 不做 EMA 更新。代码默认从 0.992 增加到 0.9995；论文举例从 0.996 到 0.9995，因此机制一致，但起始超参数不完全一致。

### 9. 损失函数

#### 9.1 余弦预测损失

$$
\mathcal{L}_{\mathrm{sim}}
=1-\frac{1}{B}\sum_{b=1}^{B}
\frac{\hat z_b^\top\operatorname{sg}(z_b)}
{\|\hat z_b\|_2\|z_b\|_2}.
$$

`sg` 表示 stop-gradient。代码先把预测和目标归一化，再计算平均余弦差异，见 `genejepa/train.py:189-193,303-308`。

#### 9.2 VICReg 防塌缩

如果所有输入都输出同一个向量，余弦预测可能得到退化解。代码使用两个正则项：

$$
\mathcal{L}_{\mathrm{var}}(P)
=\frac{1}{d}\sum_j\max\left(0,1-\sqrt{\operatorname{Var}(P_{:,j})+10^{-4}}\right),
$$

鼓励每个维度在 batch 中保持足够方差；以及

$$
\mathcal{L}_{\mathrm{cov}}(P)
=\frac{1}{d}\sum_{i\ne j}C(P)_{ij}^2,
$$

惩罚不同维度之间的冗余相关性。

论文描述在预测向量上施加 VICReg。代码除此之外还对学生上下文表示施加方差和协方差正则：

$$
\mathcal{L}_{\mathrm{code}}=
\mathcal{L}_{\mathrm{sim}}
+25\mathcal{L}_{\mathrm{var}}(P)
+\mathcal{L}_{\mathrm{cov}}(P)
+20\mathcal{L}_{\mathrm{var}}(S)
+\mathcal{L}_{\mathrm{cov}}(S).
$$

这是代码中存在、但论文没有说明的额外稳定化设计。论文引言还提到 centering，但检查到的训练路径没有实际执行 target centering。

### 10. 训练与推理

默认训练配置包括：AdamW、学习率 $10^{-4}$、权重衰减 $2\times10^{-4}$、5% warmup、之后 cosine decay、梯度裁剪 1.0、梯度累积 2。bias、归一化参数和 embedding table 不做 weight decay。多卡时使用 DDP；硬件支持时使用 bfloat16 mixed precision。

常规推理接口是：

```python
model.get_embedding(indices, values, offsets, use_teacher=True)
```

它默认使用 EMA 教师产生每个细胞的稳定向量。这个接口在 `genejepa/models.py:468-491` 中得到直接验证。

### 11. 实验结果应该怎样解读

论文把 backbone 冻结后，用简单分类或回归器评估表示质量。

- **PBMC3k：** GeneJepa 线性 probe 的 Macro F1/Accuracy 为 0.69/0.68，scGPT 为 0.23/0.20。图像显示大多数细胞类型上 GeneJepa 更好，但树突细胞是可见例外。
- **HLCA：** 混淆矩阵总体对角结构清楚，UMAP 有多个连贯区域；每类 F1 与样本量的 Spearman 相关为 0.85，说明稀有细胞类型仍然困难。
- **sci-Plex 剂量回归：** 论文报告 GeneJepa 的误差和偏差最低，rRMSE 为 0.94，但本地 Figure 4 图像因 HTTP 429 未下载，无法直接核对柱状图。
- **Open Problems 扰动预测：** 行级 cosine/Pearson/Spearman 分别为 0.3698/0.3509/0.3431。
- **测试时扩展：** 论文通过重复读取更多基因块提高表示质量，四次 read 时 Macro F1 约 0.35，接近完整输入。可用图像支持最终提升，但中间 cosine 曲线不是每一步都单调。
- **零样本 knockout：** 论文通过潜空间方向模拟 TP53 knockout，并用通路线性读出评分。这属于潜空间假设生成，不等同于转录组重建或湿实验因果验证。

### 12. 论文结论、代码事实与合理解释要分开

#### 论文结论

GeneJepa 的潜在预测目标能够学到比 token 重建更可迁移的单细胞表示，并支持测试时扩展和潜空间扰动推理。

#### 代码直接验证的事实

- Fourier 连续表达 tokenizer、Perceiver 编码器、随机 context/target 遮蔽、EMA 教师、余弦损失、VICReg、Tahoe 流式加载和普通 embedding 提取均存在；
- 核心训练实现与论文总体一致；
- 训练代码额外正则化 student context；
- 公开代码中没有重复 read 的测试时扩展实现，也没有 knockout 方向构建与验证脚本。

#### 解释

冻结表示在多个 probe 上表现好，说明向量包含可线性读取的生物学信息；但这不能单独证明模型学到了真实因果调控规则。潜空间中存在稳定方向也可能来自相关结构、数据偏倚或代理标签。论文自己也明确指出：Tahoe-100M 以癌细胞系为主，没有显式域不变目标，knockout 只在潜空间评估，必须通过湿实验验证。

### 13. 复现边界与缺失证据

- 核心训练代码匹配度高，但整体论文-代码匹配度为 **medium**。
- `MISSING / Not found`：PBMC3k、sci-Plex、Open Problems、multi-read scaling 和 knockout 的完整评估脚本。
- 没有自动化测试、随仓库 checkpoint 或完整评估数据。
- bioRxiv Markdown 丢失多处显示公式和附录超参数表；本文中的相关公式已标明为根据论文上下文和直接代码恢复。
- Figure 4 和 Figure 6 本地图像因 HTTP 429 缺失。
- 代码使用 `vevotx/Tahoe-100M`，论文数据可用性部分写 `tahoebio/Tahoe-100M`，两者是否完全等价尚未验证。
- TP53 段落存在符号不一致：给出的评分随 $\alpha$ 下降，Figure 6 caption 写 Spearman $-1.00$，但正文一处写成 $+1.0$；按数值方向应为负相关。

因此，现有仓库足以理解并重新运行 GeneJepa 的核心预训练框架，但不足以独立复现论文全部下游结果和零样本 knockout 主张。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## GeneJepa: A Predictive World Model of the Transcriptome

GeneJepa is a 2025 bioRxiv preprint proposing Joint-Embedding Predictive Architecture (JEPA) pretraining for single-cell RNA sequencing. Instead of reconstructing noisy counts or predicting masked gene tokens, it predicts the latent representation of a held-out gene subset from the representation of the visible genes in the same cell. The intended benefit is a representation focused on co-expression and cellular state rather than exact count recovery.

### Why It Was Proposed

The paper argues that sequence-style transcriptomic foundation models such as scGPT (*Nature Methods*, 2024) face three mismatches with scRNA-seq: counts are sparse and noisy; expressed genes form a set without a natural order; and token reconstruction can reward batch- or protocol-specific detail. GeneJepa replaces count reconstruction with non-contrastive latent prediction and does not require negative examples or binned expression values.

### Method in Brief

Each cell is represented as sparse `(gene ID, expression value)` pairs. Counts are log1p-transformed and standardized with fixed global statistics. A tokenizer concatenates a learned gene-identity embedding with an MLP encoding of continuous Fourier features. A Perceiver encoder lets 512 learned latents cross-attend to the variable gene set, processes those latents through 24 Transformer blocks, and mean-pools them to one 768-dimensional vector.

During training, about 45% of a cell's mapped genes form one random target block. The student encodes the remaining context, an MLP predicts the target representation, and an exponential-moving-average teacher encodes the target under stopped gradients. Cosine dissimilarity supplies the prediction objective; VICReg-style variance and covariance penalties prevent collapse. The checked code also regularizes the student context, an additional loss not described in the paper.

### Evaluation

The model is pretrained on Tahoe-100M and evaluated as a frozen feature extractor against scGPT and, where applicable, Universal Cell Embeddings (UCE).

- **PBMC3k cell identity:** GeneJepa's linear probe reaches Macro F1 0.69 and accuracy 0.68, versus 0.23 and 0.20 for scGPT. Its kNN probe reaches 0.38/0.52 versus 0.25/0.37. The local figure confirms the aggregate values and broad per-class gains, although dendritic cells are a visible exception.
- **Human Lung Cell Atlas:** the local figure shows a generally strong classification diagonal and structured embedding manifold. Per-class F1 rises with class support (Spearman $\rho=0.85$), revealing weaker performance for rare types.
- **sci-Plex dose regression:** the paper reports the lowest error and bias among compared embeddings, the only rRMSE below the median baseline (0.94), and median per-context error 0.99. The Figure 4 image was unavailable locally.
- **Open Problems perturbation prediction:** the GeneJepa-based ridge probe reports row-wise cosine 0.3698, Pearson 0.3509, and Spearman 0.3431 on 255 profiles and 18,211 genes.
- **Test-time scaling:** on PBMC68k, Macro F1 rises from about 0.02 after one read to about 0.35 after four reads, approaching the full-input result while latency stays near 26 ms/cell. The image reaches cosine fidelity 1 at four reads, but the intermediate fidelity curve is not monotonic.
- **Zero-shot knockout:** the paper constructs latent gene directions and reports a TP53 pathway response and held-out ablation test. This remains hypothesis-generating latent-space evidence, not biological validation. The text reports a Spearman sign inconsistent with its decreasing values and Figure 6 caption; the caption's $-1.00$ is directionally consistent.

### Code and Reproducibility

**Reproducibility: 3/5.** The public repository at commit `a2f4d7218b17f2f52cc5f1cc94420c8ef1ae3265` contains a coherent Lightning implementation of the tokenizer, Perceiver encoder, random JEPA masking, EMA teacher, cosine/VICReg training, Tahoe streaming, normalization, optimizer, and standard embedding extraction. Core training fidelity is high, but overall paper-code fidelity is **medium** because the repository does not include the reported PBMC3k, sci-Plex, Open Problems, multi-read scaling, or knockout analysis pipelines. No automated tests, bundled checkpoint, or evaluation data are present.

Other reproducibility gaps include incomplete equations/hyperparameter tables in the acquired bioRxiv Markdown, unavailable Figure 4 and Figure 6 assets after HTTP 429 failures, and a dataset identifier mismatch (`vevotx/Tahoe-100M` in code versus `tahoebio/Tahoe-100M` in the paper). The released package does expose EMA-teacher embeddings, so ordinary feature extraction is supported once compatible weights, vocabulary, and normalization statistics are available.

### Main Limitations

The paper's own limitations are substantial: pretraining is dominated by cancer cell lines; there is no explicit batch/domain-invariance objective; and knockout evidence is evaluated only in latent space. More broadly, good frozen-probe performance and coherent latent directions do not by themselves demonstrate that the model has learned causal regulatory mechanisms. Wet-lab perturbation validation and independently reproducible benchmark code are needed for that stronger claim.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
