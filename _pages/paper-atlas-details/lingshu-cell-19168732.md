---
layout: default
permalink: /paper-atlas/lingshu-cell-19168732/
title: "Lingshu-Cell"
nav: false
description: "这份文件是合并后的中文方法说明。两个旧目录分析的是同一篇论文；最终保留 representationmodels/Lingshu-Cell/，并按 paper-only 处理。当前没有公开代码和模型权重，所有实现细节只能来自论文。 单细胞 RNA-seq 的原始数据是一个 cell-by-gene UMI count matrix。每个细胞是一行，每个基因是一列，矩阵值是非负整数计数。"
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
    <h1>Lingshu-Cell</h1>
    <p>Lingshu-Cell: A generative cellular world model for transcriptome modeling toward virtual cells</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/arXiv:2603.25240" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Lingshu-Cell">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Lingshu-Cell 方法解释

这份文件是合并后的中文方法说明。两个旧目录分析的是同一篇论文；最终保留 `representation_models/Lingshu-Cell/`，并按 paper-only 处理。当前没有公开代码和模型权重，所有实现细节只能来自论文。

### 1. 它想解决什么问题

单细胞 RNA-seq 的原始数据是一个 cell-by-gene UMI count matrix。每个细胞是一行，每个基因是一列，矩阵值是非负整数计数。这个数据有三个特点：

- 稀疏：一个细胞里大部分基因是 0。
- 离散：原始 UMI 是整数，不是连续高斯变量。
- 无序：基因没有天然的从左到右生成顺序。

Lingshu-Cell 的核心判断是：如果要生成真实的细胞状态或预测扰动后的转录组，不应该把 scRNA-seq 强行当作连续图像噪声，也不应该像语言模型一样按固定顺序逐基因生成。它采用 masked discrete diffusion：随机遮住一部分基因表达 token，让模型一次性预测这些被遮住的位置。

### 2. count 如何变成 token

模型先把每个基因的 raw UMI count 量化成离散 token。低表达区间保留更精细：

$$
q(x)=
\begin{cases}
x, & 0 \le x < 100 \\
100 + 90\max(0,k(x)-2)+r(x), & 100 \le x \le 9999 \\
\mathrm{OVF}, & x>9999
\end{cases}
$$

其中 $k(x)$ 表示十进制数量级，$r(x)$ 表示这个数量级内的 bin。最终是 280 个非溢出 bin，加 1 个 overflow token，所以表达词表大小是 281。一个细胞就变成长度 $G=18{,}080$ 的 token 序列，每个位置对应一个基因。

这里最重要的是：它不先选 HVG，也不只保留高表达基因，而是把 18,080 个参考基因都作为生成目标。

### 3. masked discrete diffusion 怎么训练

这一节对应论文 Methods 4.1 的 “Forward Process” 和 “Reverse Process and Training Objective”。先把一个细胞的 token 序列记为：

$$
\mathbf{x}_0=[x_0^1,x_0^2,\ldots,x_0^L],
$$

其中 $L$ 是序列长度；放到 Lingshu-Cell 里可以理解为 $L=G=18{,}080$ 个基因位置。$x_0^i$ 是第 $i$ 个基因位置的真实表达 token，也就是前面 $q(x)$ 得到的离散 token。

#### 3.1 forward process：先人为制造一个补全任务

训练时先从数据里拿到干净序列 $\mathbf{x}_0$，再随机采样一个连续时间 $t\sim\mathcal{U}(0,1)$。这个 $t$ 可以直接理解成“mask 比例”：$t$ 越大，被遮住的位置越多。

对每个位置 $i$，forward process 独立决定是否遮住：

$$
q_{t|0}(x_t^i|x_0^i)=
\begin{cases}
1-t, & x_t^i=x_0^i \\
t, & x_t^i=M
\end{cases}
$$

所以 $\mathbf{x}_t$ 是一个“部分可见、部分 mask”的序列。未被 mask 的位置仍然是真实 token，给模型作为上下文；被 mask 的位置变成特殊符号 $M$，要求模型恢复它原来的 token。

一个小例子：

$$
\mathbf{x}_0=(12,100,146,280)
$$

如果在某个 $t$ 下第二、四个位置被 mask，那么模型看到的是：

$$
\mathbf{x}_t=(12,M,146,M).
$$

训练目标不是让模型重建已经可见的 $12$ 和 $146$，而是只要求它在第二、四个位置预测原来的 $100$ 和 $280$。

#### 3.2 reverse model：输出的是每个 mask 位置的 token 分布

论文把 reverse model 写成参数化的 mask predictor：

$$
p_\theta(\cdot|\mathbf{x}_t).
$$

这里的 “predicts the original tokens for all masked positions simultaneously” 意思是：模型输入整个部分遮住的序列 $\mathbf{x}_t$，然后对每个被 mask 的位置输出一个 categorical distribution。这个 distribution 的类别就是表达 token 词表，例如非 overflow token $0,\ldots,279$ 加 overflow token。

对某个被 mask 的位置 $i$，模型不是直接输出一个确定答案，而是输出：

$$
p_\theta(v|\mathbf{x}_t),\quad v\in\mathcal{V}.
$$

如果真实 token 是 $x_0^i=100$，训练就希望模型给 token 100 更高概率。公式里的

$$
\log p_\theta(x_0^i|\mathbf{x}_t)
$$

就是“模型给正确答案的 log probability”。负号加上去以后，就是常见的 cross-entropy / negative log-likelihood：正确 token 概率越高，loss 越小。

#### 3.3 loss 为什么只在 masked tokens 上计算

论文的训练目标是：

$$
\mathcal{L}(\theta)=
-\mathbb{E}_{t,\mathbf{x}_0,\mathbf{x}_t}
\left[
\frac{1}{t}
\sum_{i=1}^{L}
\mathbb{I}[x_t^i=M]\log p_\theta(x_0^i|\mathbf{x}_t)
\right].
$$

逐项看：

| 符号 | 含义 |
|---|---|
| $\mathbb{E}_{t,\mathbf{x}_0,\mathbf{x}_t}$ | 对随机时间 $t$、真实训练样本 $\mathbf{x}_0$、以及随机 mask 后的 $\mathbf{x}_t$ 取平均 |
| $\sum_{i=1}^{L}$ | 遍历序列里的所有基因位置 |
| $\mathbb{I}[x_t^i=M]$ | 只有第 $i$ 个位置被 mask 时才计入 loss |
| $p_\theta(x_0^i|\mathbf{x}_t)$ | 模型在第 $i$ 个位置给真实原始 token 的概率 |
| $-\log p_\theta(x_0^i|\mathbf{x}_t)$ | 这个位置的 cross-entropy 损失 |
| $\frac{1}{t}$ | 对不同 mask 比例下的损失做归一化，同时对应论文说的 likelihood 上界形式 |

这个 indicator 很关键：未被 mask 的位置只是条件信息，不是训练目标。比如：

$$
\mathbf{x}_t=(12,M,146,M)
$$

loss 只包括第二、四个位置：

$$
-\log p_\theta(100|\mathbf{x}_t)
-\log p_\theta(280|\mathbf{x}_t).
$$

第一、三位置已经暴露给模型了，如果也让模型预测它们，任务会变成复制已知输入，不能训练模型“根据已知基因补全未知基因”的能力。

#### 3.4 为什么有 $1/t$

因为 $t$ 越大，被 mask 的位置期望数量越多。长度为 $L$ 的序列在时间 $t$ 下，平均会有大约 $tL$ 个位置被 mask。如果直接把所有 masked positions 的 cross-entropy 相加，那么大 $t$ 的样本天然贡献更大的 loss，只是因为它 mask 得更多。

乘上 $\frac{1}{t}$ 后，可以把不同 $t$ 下的损失拉回到更可比的尺度：小 mask 比例和大 mask 比例都会对目标有贡献。论文进一步说明，这个目标是 true data distribution 的 negative log-likelihood 的 variational upper bound。对阅读方法来说，可以先把它理解成：模型在所有噪声程度上学习同一个补全任务，而不是只偏向 mask 很多的样本。

#### 3.5 和生成时的 reverse process 有什么关系

训练时，模型见过从轻度 mask 到重度 mask 的各种 $\mathbf{x}_t$，学会在任意 mask 程度下预测缺失 token。生成时则反过来：

1. 从完全 mask 的序列 $\mathbf{x}_1=(M,M,\ldots,M)$ 开始。
2. 模型对所有 masked positions 输出 token 分布。
3. 采样一部分位置，把它们从 mask 变成具体表达 token。
4. 按 reverse schedule 逐步减少 mask，直到得到完整的表达 token 序列。

因此这不是 autoregressive 生成：模型不是先生成 gene 1，再生成 gene 2。它每一步都能看全局上下文，并同时给所有 mask 位置打分。这就是论文强调的 order-independent、bidirectional refinement：基因没有天然顺序，模型也不需要强加一个从左到右的生成顺序。

### 4. 为什么需要 sequence compression

18,080 个基因 token 直接进 Transformer 太贵。Lingshu-Cell 不减少输出基因，而是在 embedding 空间压缩内部序列：

1. 每个表达 token 变成 $D=640$ 维 embedding。
2. 对基因位置做一个固定随机排列 $\pi$。
3. 每 $S$ 个基因 embedding 分成一组。
4. 把 $S \times D$ 压成一个 $D$ 维 token。
5. Transformer 只处理压缩后的 $G_c=\lceil G/S\rceil$ 个 token。
6. Transformer 后再用 up-projection 解压回 gene-level embedding，并用 $\pi^{-1}$ 还原基因顺序。

论文里默认 $S=8$，即 18,080 个基因压到 2,260 个内部 token；遗传扰动预测用 $S=32$，压到 565 个内部 token。注意：压缩只是中间计算技巧，最终预测仍然是所有基因。

### 5. 条件生成如何做扰动预测

扰动预测时，模型不只是输入基因表达 token，还在序列前面加 condition tokens：

- source context：例如 cell line、donor。
- perturbation identity：例如被敲除基因或 cytokine 条件。

这些 condition tokens 不参与 masking，因此模型在每一步都能看到条件。

推理时使用 classifier-free guidance。它同时计算目标扰动条件 $c$ 和 control 条件 $c_{nt}$ 下的 logits：

$$
\tilde{a}_\theta(v|\mathbf{x}_t,c)
=a_\theta(v|\mathbf{x}_t,c_{nt})
+(w+1)\left(a_\theta(v|\mathbf{x}_t,c)-a_\theta(v|\mathbf{x}_t,c_{nt})\right).
$$

这相当于把“扰动相对 control 的差异”放大。论文中遗传扰动使用 $w=2$，cytokine 扰动使用 $w=3$。无条件生成用 256 个 reverse steps；条件扰动生成只用 3 个 reverse steps。

### 6. biological prior injection 是什么

对遗传扰动，论文还用了一个推理时的外部先验。它从其他 cell line 的 perturb-seq 数据中找出某个 perturbation 下显著下调的基因集合 $G_\downarrow$。生成开始时：

$$
\tilde{x}_g =
\begin{cases}
\mu=1, & g\in G_\downarrow \\
\mathrm{MASK}, & g\notin G_\downarrow
\end{cases}
$$

这些 prior genes 会被固定住，不再 remask。这样做的意义是给模型一个“这个扰动会下调哪些基因”的方向性提示。它不是因果机制建模，只是把外部差异表达结果作为采样约束。

### 7. 结果怎么看

论文有三类主要结果：

- **无条件生成**：在 PARSE-PBMC、多个 CZ CELLxGENE human tissues、以及 mouse/macaque/zebrafish/fly 数据上生成细胞。核心指标包括 Pearson、Spearman、MMD、1-WD、iLISI。
- **遗传扰动预测**：在 VCC H1 benchmark 上，论文报告平均排名 8.7、MAE 0.052、Pearson-$\Delta$ 0.306。
- **cytokine 扰动预测**：在 PARSE 10M PBMC 的 donor/cytokine holdout 任务上，与 PertMean、STATE、scGPT、scVI 比较，报告最佳平均分。

这些结果说明它在分布匹配和 pseudobulk perturbation prediction 上表现强，但不能直接推出模型学到了真实调控因果机制。

### 8. 复现边界

这篇论文方法写得比较完整，但复现仍然困难：

- 没有公开代码、训练脚本、模型权重。
- reverse cosine schedule 的精确公式没有写清楚。
- condition token 的具体编号、padding、batch 构造、EMA 同步细节需要实现者自己决定。
- 训练需要 A800 多卡资源，论文按任务报告 8 到 24 张 GPU。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Lingshu-Cell: A generative cellular world model for transcriptome modeling toward virtual cells

**Paper**: arXiv:2603.25240, 2026

**Authors**: Han Zhang, Guo-Hua Yuan, Chaohao Yuan, Tingyang Xu, Tian Bian, Hong Cheng, Wenbing Huang, Deli Zhao, Yu Rong

**Mode**: paper-only. No public implementation or released model weights were found in either previous workspace; the non-hyphenated duplicate only pointed to a homepage, not a source repository.

### Core Idea

Lingshu-Cell is a masked discrete diffusion model for single-cell transcriptomics. Instead of adding continuous Gaussian noise to normalized expression vectors, it quantizes raw UMI counts into discrete expression tokens and trains a Transformer to reconstruct randomly masked gene tokens. The paper positions this as a "cellular world model": a generator that can sample realistic cell states and condition on perturbation context to predict transcriptomic responses (paper lines 9, 27, 33).

The important modeling choices are:

1. **Discrete count tokenization**: each cell is represented over a fixed 18,080-gene feature set; raw counts are mapped to 281 expression tokens, preserving exact 0-99 counts and roughly two significant digits at higher counts (paper lines 165-207).
2. **Masked discrete diffusion**: at time $t$, each token is independently replaced by `[MASK]` with probability $t$; the network predicts masked positions with a $1/t$-weighted cross-entropy loss (paper lines 135-159).
3. **Embedding-space compression**: gene embeddings are randomly permuted, grouped, projected from $S \times D$ to $D$, processed by a bidirectional Transformer, then decompressed back to gene resolution (paper lines 209-225).
4. **Conditional perturbation generation**: source context plus perturbation identity are prepended as unmasked condition tokens; classifier-free guidance compares target condition logits against a control condition (paper lines 235-253).
5. **Biological prior injection**: for genetic perturbations, downregulated prior genes from external cell lines are initialized to low expression and kept fixed during sampling (paper lines 255-263).

### Evaluation

For unconditional generation, the model is evaluated on PARSE 10M PBMC control cells, eight human tissues from CZ CELLxGENE, and four non-human species. It reports high gene-expression concordance and better distributional metrics than scDiffusion and scVI on PARSE-PBMC, including MMD 0.0088 versus 0.0178 and 0.0343 (paper lines 52-57).

For genetic perturbation prediction, the benchmark is the Virtual Cell Challenge H1 dataset. Training combines H1 training targets with external perturbation datasets restricted to overlapping targets; the held-out evaluation includes 50 validation and 100 test targets. The paper reports average rank 8.7 on the VCC generalist leaderboard, with best MAE 0.052 and best Pearson-$\Delta$ 0.306 among listed teams (paper lines 69, 91-96, 507-509).

For cytokine perturbation prediction, the paper uses PARSE 10M PBMC from 12 donors and 90 cytokine conditions, holding out four donors with 70% of cytokines as test conditions. Lingshu-Cell reports the best average score among PertMean, STATE, scGPT, and scVI, especially on PDS, Pearson-$\Delta$, and Spearman #DEG (paper lines 102-121).

### What Matters Technically

- The method does **not** filter to highly variable genes; the full 18,080-gene reference set is central to the claim (paper lines 9, 27, 351).
- Compression is internal only. The input/output prediction target remains all genes, while attention cost is reduced from 18,080 tokens to 2,260 tokens for $S=8$ or 565 tokens for $S=32$ (paper lines 515, 538).
- Conditional generation uses only three reverse steps, while unconditional generation uses 256 steps; CFG weights are $w=2$ for genetic perturbation and $w=3$ for cytokines (paper line 547).
- The prior injection is a hard sampling constraint for selected downregulated genes, not a learned causal regulatory mechanism (paper lines 255-263).

### Reproducibility

**Rating: 2/5.** The paper contains enough equations, hyperparameters, data sources, and evaluation definitions to guide a reimplementation. However, no public code, checkpoint, exact reverse cosine schedule formula, or full preprocessing scripts are available in the merged workspace. Training also requires substantial compute: the paper reports DDP on NVIDIA A800 GPUs, with 8-24 GPUs depending on the setting (paper lines 536-547).

Key reproducibility strengths:

- Quantization, masking objective, compression/decompression, CFG, and prior-injection formulas are described in the paper.
- Architecture hyperparameters are tabulated: $D=640$, 13 Transformer blocks, 10 heads, head dimension 64, FFN dimension 2,560, RoPE, RMSNorm, SwiGLU, bidirectional attention (paper lines 515-538).
- Training settings are listed: AdamW, gradient clipping, cosine LR with warmup, bfloat16 DDP, EMA, global batch size 256, and per-task GPU counts (paper lines 536-547).
- Dataset composition and held-out splits are described for unconditional, genetic perturbation, and cytokine perturbation tasks (paper lines 349-379).

Main limitations:

- No source code or weights are available for exact verification.
- Reported generation quality is mostly measured by distributional and pseudobulk metrics, not direct wet-lab validation.
- High-fidelity transcriptome generation should not be interpreted as causal regulatory modeling.
- The model is transcriptomics-only and does not integrate epigenomic, proteomic, spatial, or metabolomic modalities (paper line 129).
- Exact details such as condition-token indexing, reverse schedule formula, training wall-clock time, and some preprocessing edge cases remain underspecified.

### Merged Workspace Note

This folder consolidates the previous `Lingshu-Cell/` and `LingshuCell/` analyses. The hyphenated path is kept as canonical because repo aliases and README routing already preferred it. The non-hyphenated folder contained duplicate paper analysis plus an inferred `doc_code.md`; its only substantive contribution was the explicit statement that no public code repository exists, which is now captured here and in `CLAUDE.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
