---
layout: default
permalink: /paper-atlas/bivi-87d6ed16/
title: "biVI"
nav: false
description: "biVI 是一个“在观测层加入机制约束”的 VAE：它用转录—剪接—降解模型规定 nascent/mature RNA 的联合分布，再利用预训练神经近似器解决 bursty 条件概率难以解析计算的问题，从而在保持 scVI 可扩展潜表示能力的同时，把细胞间差异解释为 burst size 或相对降解等模型条件下的调控变化。"
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
      <span>Nature Methods · 2024</span>
    </div>
    <h1>biVI</h1>
    <p>Biophysical modeling with variational autoencoders for bimodal, single-cell RNA sequencing data</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## biVI 方法详解：把转录动力学嵌入变分自编码器

### 1. 这篇论文要解决什么问题？

单细胞 RNA 测序可以从同一个细胞中得到两类彼此相关的计数：未剪接 RNA（论文把它近似视为 nascent RNA，记为 $N$）和已剪接 RNA（近似视为 mature RNA，记为 $M$）。两者并不是两个独立模态：新生 RNA 会经过剪接变成成熟 RNA，成熟 RNA 随后被降解。

传统做法可以把两张计数矩阵拼接后送入 VAE，但在解码时分别使用两个独立的计数分布。这样虽然能获得低维表示，却忽略了

$$
N\stackrel{\beta}{\longrightarrow}M\stackrel{\gamma}{\longrightarrow}\varnothing
$$

这一明确的生物学方向。因此，模型输出的均值和离散度主要是统计参数，很难直接解释为转录、剪接或降解机制。

biVI 的目标是：保留 scVI 的可扩展变分推断框架，同时把“观测计数的条件分布”替换成由化学主方程推导出的双变量分布，使解码参数具有动力学含义。

### 2. 为什么已有方法不够？

- **scVI（*Nature Methods*, 2018）**：使用 VAE 编码单细胞计数，能有效学习低维细胞表示，但其 Poisson、负二项或零膨胀负二项似然主要作为适配离散过度离散数据的统计模型。
- **totalVI（*Nature Methods*, 2021）等多模态 VAE**：可以把多个模态联合编码到共享潜空间，但通常为每种模态设置各自的条件似然。对于同一基因的 nascent/mature RNA，这种条件独立假设没有利用二者之间的加工关系。
- **直接数值求解化学主方程**：bursty 转录模型的双变量稳态分布没有简单闭式解。对每个细胞、每个基因、每组参数都在二维状态空间上进行数值求解，计算量过大，而且不利于自动微分，无法直接放入 VAE 的反复优化中。

biVI 的关键不是发明新的编码器，而是为 VAE 提供一个既有生物物理来源、又能高效计算和求梯度的联合似然。

### 3. 核心思想

可以把 biVI 概括为：

```text
scVI 的编码器、潜变量和 ELBO
                +
转录—剪接—降解的化学主方程
                +
预训练神经网络近似难以解析计算的条件分布
                =
具有动力学参数输出的双变量 VAE
```

论文给出三种生物物理模型：

1. **Constitutive 模型**：恒定转录，双变量似然为两个 Poisson 分布的乘积。
2. **Extrinsic 模型**：转录速率受外源随机性影响，得到相关的双变量负二项分布。
3. **Bursty 模型**：基因以几何分布大小的 burst 产生 RNA，是主文分析的重点。

### 4. Bursty 转录模型

#### 4.1 反应过程

bursty 模型写作

$$
\varnothing\stackrel{k}{\longrightarrow}B\times\mathcal N
\stackrel{\beta}{\longrightarrow}\mathcal M
\stackrel{\gamma}{\longrightarrow}\varnothing.
$$

其中：

- $k$：burst 发生频率；
- $B$：每次 burst 产生的 nascent RNA 数，服从均值为 $b$ 的几何分布；
- $\beta$：nascent 到 mature 的转换/剪接速率；
- $\gamma$：mature RNA 降解速率。

稳态均值为

$$
\mu_N=\frac{kb}{\beta},\qquad
\mu_M=\frac{kb}{\gamma}.
$$

#### 4.2 联合分布如何计算？

论文把联合概率分解为

$$
P(n,m)=P_{\rm NB}(n)P(m\mid n).
$$

nascent 边缘分布 $P_{\rm NB}(n)$ 是可解析计算的负二项分布；困难在于成熟 RNA 的条件分布 $P(m\mid n)$ 没有简单闭式表达式。

biVI 使用一个在独立任务上预训练好的小型神经网络来近似它。该网络并不直接输出单个概率，而是输出十个解析基函数的混合权重：

1. 根据 $b,\beta/k,\gamma/k$ 计算系统均值、方差和协方差；
2. 近似得到给定 $n$ 时 mature RNA 的条件均值和条件方差；
3. 在条件分布的若干固定分位点上放置十个负二项基函数；
4. 神经网络输出十个 softmax 权重和一个控制基函数宽度的辅助参数；
5. 对十个基函数加权求和，得到 $P(m\mid n)$ 的近似；
6. 再乘以解析的 $P_{\rm NB}(n)$，得到联合概率。

直接代码验证显示，这个预训练网络从 `models/best_model_MODEL.zip` 加载，进入 evaluation mode；训练 biVI 时更新的是 VAE 参数，而不是这个概率近似器。

### 5. biVI 的生成模型

对于细胞 $c$ 和基因 $g$，论文的 bursty 生成过程为

$$
\begin{aligned}
\mathbf z_c&\sim\operatorname{Normal}(0,I),\\
\ell_c&\sim\operatorname{LogNormal}(\ell_\mu,\ell_{\sigma^2}),\\
\rho^N_{cg},\rho^M_{cg}&=f(\mathbf z_c,s_c),\\
\mu_{cN},\mu_{cM}&=\rho^N_{cg}\ell_c,\rho^M_{cg}\ell_c,\\
x^N_{cg},x^M_{cg}&\sim P_{\rm bursty}(n,m;\alpha_g,\mu_{cN},\mu_{cM}).
\end{aligned}
$$

含义是：

- 编码器根据细胞计数得到近似后验 $q_c(\mathbf z)$；
- 从后验采样潜变量 $\mathbf z_c$；
- 解码器 $f$ 输出 nascent 和 mature 的组成比例 $\rho^N,\rho^M$；
- 组成比例乘以细胞测序深度 $\ell_c$，得到条件均值 $\mu_N,\mu_M$；
- 每个基因还有一个跨细胞共享的正形状参数 $\alpha_g$；
- 三个量共同参数化双变量 bursty 似然。

代码中最重要的结构修改是：输入有 $2G$ 个特征，解码器仍输出 $2G$ 个均值，但离散度/形状参数 `px_r` 只有 $G$ 个。也就是说，同一基因的 nascent 和 mature 计数共享一个 $\alpha_g$，而不是各自拟合一个独立形状参数。

### 6. 如何从统计参数恢复动力学参数？

论文令

$$
\alpha=\frac{k}{\beta}
$$

并在稳态下设 $k=1$。于是

$$
b=\frac{\mu_N}{\alpha},\qquad
\frac{\beta}{k}=\frac{1}{\alpha},\qquad
\frac{\gamma}{k}=\frac{\mu_N}{\mu_M\alpha}.
$$

源代码默认的 `NAS_SHAPE` 分支完全按照这些关系计算：

```text
beta  = 1 / alpha
b     = mu_N * beta
gamma = b / mu_M
```

这里输出的是相对速率而不是绝对时间尺度。设置 $k=1$ 消除了尺度不可辨识性，但也意味着不能把 $\beta/k$ 或 $\gamma/k$ 直接解释为带绝对时间单位的真实反应常数。

### 7. 完整计算流程

```text
FASTQ
  |
  v
kallisto|bustools 得到 unspliced / spliced 计数
  |
  v
去除 low-quality 和 doublet 细胞
在 spliced 矩阵上选择 2,000 个高变基因
  |
  v
[unspliced | spliced] 拼成 C x 2G 原始计数矩阵
  |
  v
编码器 -> 高斯近似后验 q_c(z)
  |
  v
采样 z_c -> 解码器 -> rho_N, rho_M
  |
  v
乘以 library size -> mu_N, mu_M
共享基因参数 -> alpha_g
  |
  v
选择联合似然：constitutive / extrinsic / bursty
  |
  v
ELBO 优化
  |
  +-----------------------------+
  |                             |
  v                             v
细胞潜表示                    细胞-基因动力学参数
用于聚类/可视化              b, beta/k, gamma/k
                                  |
                                  v
                          后验采样 Bayes factor
                          比较不同细胞群
```

#### 输入和预处理

Allen B08 的代码流程先根据已有注释去除低质量细胞和 doublet，再对 spliced 数据进行归一化和 log1p，仅用于筛选 2,000 个高变基因。随后回到原始计数，把 unspliced 放在前半、spliced 放在后半。这一列顺序是实现契约：似然函数直接按最后一维对半切分，如果顺序错误，动力学解释也会错误。

#### 训练目标

局部代码把重构项实现为联合对数概率的负和：

$$
\mathcal L_{\rm recon}(c)=-\sum_g\log P(x^N_{cg},x^M_{cg}\mid\mathbf z_c).
$$

潜变量先验、后验 KL 项和总体 ELBO 优化继承自 scvi-tools。论文实验使用三层、每层 128 个节点的编码器和解码器，潜空间维度为 10，训练 400 个 epoch。

### 8. 组间差异检验

biVI 不只给每个细胞一个点估计，还可以从各细胞的潜变量后验反复采样。对于两个细胞群 $A,B$，代码执行：

1. 分别从两组细胞的后验采样；
2. 解码得到标准化 burst size、相对降解率和均值等参数；
3. 随机组成跨组参数对；
4. 计算每个基因的 $\log_2$ fold change；
5. 用

$$
\operatorname{BF}=
\frac{P(|\operatorname{LFC}|\ge T)}{P(|\operatorname{LFC}|<T)}
$$

比较“差异超过阈值”和“差异未超过阈值”两个假设。

主文分析使用 LFC 绝对值阈值 1 和 Bayes factor 阈值 1.5。burst size 和均值在测序深度标准化后比较；相对降解率本身不依赖测序深度，因此直接检验。

### 9. 实验结果说明了什么？

#### 模拟数据

- bursty 模拟数据上，biVI 的平均重构 KLD 为 0.014，scVI 为 0.0212；
- 同类细胞最近邻比例分别为 90.0% 和 90.4%，说明 biVI 的潜空间结构与 scVI 大体相当；
- 某些聚类指标略逊于 scVI，提示机制可解释性与纯表示性能之间可能存在小幅权衡。

#### 外部实验验证

- 两个 seqFISH+ 重复中，基因平均 burst size 的对数相关系数为 0.704 和 0.728；
- 在代谢标记时间序列数据中，bursty 模型推断的降解率与实验报告值在所有时间点和对照中的 Pearson 相关均大于 0.5。

#### Allen 小鼠运动皮层

主图中，biVI 对 *Foxp2* 和 *Rorb* 双变量计数分布的 KLD/HD 略优于 scVI，但提升幅度不大。更重要的是，模型把这两个 marker 基因在相应细胞亚类中的上调主要解释为 burst size 增大。

图中还展示了均值难以发现的差异：*Trem2* 的相对降解率和 *Ndnf* 的 burst size 在细胞亚类之间明显移动，而 scVI 推断的 mature 均值分布高度重叠。这正是 biVI 的主要科学用途：比较“表达调控方式”，而不仅是比较平均表达量。

### 10. 应该怎样理解这些参数？

biVI 的输出应当被理解为**给定模型假设下的机制参数**，而不是直接测量值。

- 如果稳态假设、两阶段 Markov 过程以及 unspliced/nascent、spliced/mature 的对应关系合理，那么 $b$ 和 $\gamma/k$ 能提供有意义的调控比较。
- 如果存在强瞬态过程、复杂剪接、核输出延迟、基因长度偏差或明显 assay-specific noise，参数可能吸收模型未描述的效应。
- 解码器仍是神经网络，因此“为什么某个潜变量产生某个参数”并没有完全透明；可解释性主要来自观测似然，而不是整个网络。
- 当前一次训练只能为所有基因选择同一种生物物理模型，不能在训练时自动决定某个基因更适合 constitutive、extrinsic 还是 bursty 模型。

### 11. 代码复现情况

直接源代码检查确认了核心方法：双变量似然、共享 $G$ 维形状参数、预训练 bursty 条件近似器、Eq. 15 参数转换、重构损失、Allen 预处理和 Bayes factor 均存在。

但代码—论文一致性只能评为**中等**：

- 仓库 README 声称提供手稿分析 notebook 和 `Example/Demo.ipynb`，本地快照中没有这些文件；
- 未找到实现论文 Eqs. 20–22 细胞类型后验预测混合以及生成主图重构分布的源码；
- 论文写明基于 scVI 0.18.0，`setup.py` 却固定 scvi-tools 1.2.2；
- 论文报告学习率 0.01，现有训练脚本设置为 `1e-5`；
- 没有环境锁文件和自动测试来证明该快照就是产生论文结果的完整运行环境。

本工作区只做了论文、补充材料、主图和源码的静态核验，没有重新安装、训练或复现数值。因此，论文中的性能结果属于作者报告结果，而不是本工作区重新计算的结果。

### 12. 一句话总结

biVI 是一个“在观测层加入机制约束”的 VAE：它用转录—剪接—降解模型规定 nascent/mature RNA 的联合分布，再利用预训练神经近似器解决 bursty 条件概率难以解析计算的问题，从而在保持 scVI 可扩展潜表示能力的同时，把细胞间差异解释为 burst size 或相对降解等模型条件下的调控变化。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## biVI: Biophysical Variational Inference for Paired RNA Counts

### Problem

Single-cell workflows can quantify paired RNA species—here, unspliced/nascent and spliced/mature counts—from the same cell. Standard multimodal VAEs can encode both measurements into a shared latent space, but often decode them with separate likelihoods. That choice ignores the biological direction from nascent RNA to mature RNA and makes fitted distribution parameters descriptive rather than mechanistic.

scVI (*Nature Methods*, 2018) supplies the scalable variational framework but normally treats count likelihoods as statistical observation models. totalVI (*Nature Methods*, 2021) and related multimodal extensions jointly encode modalities while retaining modality-specific likelihoods. For nascent and mature counts from the same gene, independent conditional distributions discard known transcription, splicing, and degradation coupling.

### Proposed Method

biVI keeps scVI's encoder, latent Gaussian posterior, decoder, library-size model, and ELBO optimization, but replaces the observation likelihood with a bivariate distribution derived from a chemical master equation. The input is a $C\times2G$ raw-count matrix ordered as unspliced followed by spliced genes. The decoder produces cell- and gene-specific nascent and mature means plus one shared gene-wise shape parameter.

The main bursty model is

$$
\varnothing\stackrel{k}{\rightarrow}B\times\mathcal N
\stackrel{\beta}{\rightarrow}\mathcal M
\stackrel{\gamma}{\rightarrow}\varnothing,
$$

where bursts occur at frequency $k$, have geometric mean size $b$, nascent RNA is spliced at $\beta$, and mature RNA degrades at $\gamma$. Its joint stationary likelihood factorizes into an analytic nascent negative-binomial marginal and an intractable conditional mature distribution. biVI evaluates the latter using a frozen pretrained neural network that predicts weights over ten analytic basis functions.

With the convention $\alpha=k/\beta$ and $k=1$, decoded means give interpretable parameters:

$$
b=\frac{\mu_N}{\alpha},\qquad
\frac{\beta}{k}=\frac{1}{\alpha},\qquad
\frac{\gamma}{k}=\frac{\mu_N}{\mu_M\alpha}.
$$

The framework also implements constitutive Poisson and extrinsic-noise bivariate negative-binomial models. Only one model family can be fit to all genes in one run.

### Evaluation and Main Findings

The paper evaluates biVI on simulated data, orthogonal experimental validations, and mouse primary motor cortex scRNA-seq.

- On bursty simulations, biVI reported lower average distribution-reconstruction KLD than independent-NB scVI (0.014 versus 0.0212) while retaining similar local cell-type structure (90.0% versus 90.4% same-cell-type nearest neighbors). Some clustering metrics were slightly worse, indicating an interpretability–representation tradeoff.
- In seqFISH+ mouse embryonic stem-cell data, log-average inferred burst sizes correlated with reported burst sizes at 0.704 and 0.728 across two replicates.
- Against metabolic-labeling estimates, the bursty model's inferred degradation rates had Pearson correlations above 0.5 for all fitted time points and control.
- On Allen sample B08, the two displayed genes had modestly better biVI reconstruction scores than scVI. *Foxp2* in L6 CT and *Rorb* in L5 IT showed subclass-associated increases chiefly in inferred burst size.
- biVI identified kinetic differences without corresponding mature-mean differences: the main figure shows a relative degradation-rate shift for *Trem2* and a burst-size shift for *Ndnf* where scVI mature means overlap substantially.

These results support biVI as a way to preserve a useful latent representation while exposing a hypothesis-driven decomposition of expression changes. They do not establish absolute kinetic rates or causal intervention effects; all interpretations depend on the selected steady-state two-stage model.

### Limitations

The paper explicitly notes that one biophysical model must currently be chosen for all genes, technical biases such as nascent-RNA length effects are not modeled, and the neural encoder/decoder remain opaque. The supplement further emphasizes that identifying unspliced with nascent and spliced with mature RNA is a tractable proxy that omits elongation, nuclear export, complex splicing, and assay-specific noise. Fixing $k=1$ yields relative rather than absolute rates.

### Reproducibility Assessment: 3/5

**Available:** the paper and supplement are complete; both main figures are local; processed data and results are referenced through Zenodo; the GitHub snapshot includes the core biVI model, bundled pretrained likelihood weights, preprocessing and training scripts, installation metadata, and a small example input. Direct source inspection verifies the paired likelihood, shared gene-wise shape parameter, bursty conditional mixture, Eq. 15 conversions, reconstruction loss, preprocessing, and Bayes-factor routine.

**Code–paper match:** **medium**. Core method behavior is present, but the acquired snapshot lacks the manuscript and demo notebooks promised by its README, and no source was found for the cell-type posterior-predictive mixture used to create the main reconstruction panels. The paper states scVI 0.18.0 while package metadata pins scvi-tools 1.2.2; the paper reports learning rate 0.01 while the supplied training script sets `1e-5`. No environment lockfile or automated tests establish the published runtime.

**Not rerun:** this Author phase performed static source and figure verification only. It did not install dependencies, train models, or reproduce metrics. The exact published environment and figure-generation path therefore remain unresolved.

### Bottom Line

biVI's main contribution is a structured observation model: it embeds established transcription kinetics inside a scalable VAE so paired RNA counts are fit jointly and decoder outputs can be expressed as burst size and relative processing rates. The method's scientific value is strongest when its kinetic assumptions are plausible and the goal is to compare regulatory strategies beyond mean expression; its conclusions should be treated as model-conditioned mechanistic hypotheses rather than direct measurements of molecular rates.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
