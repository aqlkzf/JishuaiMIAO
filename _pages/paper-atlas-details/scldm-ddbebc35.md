---
layout: default
permalink: /paper-atlas/scldm-ddbebc35/
title: "scLDM"
nav: false
wide: true
description: "scLDM 的关键不是简单地“把扩散模型用于单细胞”，而是先用交叉注意力把无序、稀疏、计数型基因集合变成固定长度的潜在 token，再让 DiT 在这个结构正确的潜空间里学习细胞分布与联合条件响应，最后通过基因 ID 查询和计数似然还原到原始表达空间。"
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
      <span>arXiv · 2025</span>
    </div>
    <h1>scLDM</h1>
    <p>Scalable Single-Cell Gene Expression Generation with Latent Diffusion Models</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/czi-ai/scldm" target="_blank" rel="noopener noreferrer" aria-label="Open code for scLDM">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scLDM 方法详解：用潜在扩散生成可交换的单细胞基因表达

### 1. 论文要解决什么问题？

单细胞 RNA 测序记录的是每个细胞中各基因的离散表达计数。它有三个直接影响建模的特点：

1. **基因没有天然顺序。** 改变基因在输入向量中的排列，不应改变对同一个细胞的表示；解码时改变待查询基因的顺序，只应相应改变输出顺序。
2. **数据高维且稀疏。** 一个数据集可包含约两万至三万个基因，但单个细胞的大多数计数为零，直接对全基因序列做注意力计算代价很高。
3. **输出是过度离散的计数。** 只在连续的对数归一化空间中生成，可能忽略原始计数及测序深度的统计结构。

已有方法各有局限。scVI 是基于 VAE 的计数模型，但典型 MLP 把基因绑定到固定输入位置；scGAN 等 GAN 方法存在训练不稳定和模式坍塌风险；scDiffusion、SCLD、scVAEDer 和 CFGen 等扩散或潜在扩散方法通常依赖 MLP 自编码器。CFGen 已在 scVI 潜空间上使用流匹配，但其多属性引导采用各条件贡献相加的形式。scLDM 的核心目标是：**先用集合结构正确地压缩和还原基因计数，再在这个固定大小的潜空间中训练可条件控制的生成模型。**

### 2. 输入、输出与核心假设

设一个细胞由基因索引集合 $\mathcal{I}$ 和计数 $\mathbf{x}_{\mathcal{I}}$ 表示。模型要求满足

$$
p(\mathbf{x}_{\mathcal{I}}\mid\mathcal{I})
=p(\mathbf{x}_{\pi(\mathcal{I})}\mid\pi(\mathcal{I})),
$$

其中 $\pi$ 是任意排列。这就是可交换性：顺序本身不携带信息。

模型输入包括：

- 基因 ID 与原始表达计数；
- 细胞的文库大小；
- 可选条件，如细胞类型、组织、细胞系、细胞因子或被敲除基因。

模型输出包括：

- 对给定基因集合的重建或生成计数；
- 固定数量的潜在 token，可作为细胞嵌入；
- 条件生成时的无条件与有条件样本。

### 3. 从输入到输出的完整计算流程

```text
原始基因计数 + 基因 ID
        |
        v
选取表达基因 / 构造固定长度上下文
        |
        v
计数变换 + 基因嵌入
        |
        v
MCAB 以固定诱导点为查询进行集合池化
        |
        v
Transformer 编码器
        |
        v
固定大小潜在 token Z
        |
        +---------------------------+
        |                           |
        v                           v
Transformer 解码器             第二阶段 DiT 流匹配
        |                           |
基因嵌入作为查询                    | 高斯噪声 -> ODE -> 新 Z
        |                           |
MCAB 按基因展开 <-------------------+
        |
负二项分布参数（均值、离散度）
        |
        v
采样基因表达计数
```

这一流程把两个问题解耦了：自编码器负责“如何用集合结构表示计数”，潜在扩散负责“如何学习细胞状态在潜空间中的复杂分布”。

### 4. 第一步：稀疏基因 token 化

论文先找出表达量大于零的基因：

$$
\mathcal{J}=\{i\in\mathcal{I}:x_i>0\}.
$$

然后把这些 `(count, gene ID)` 对放入最大长度为 $d$ 的上下文；不足时用零计数的 `PAD` token 补齐。这不是让解码器只能预测表达基因，而是只缩短编码器上下文。解码器仍可对完整基因集合输出概率分布，因此也能为零计数分配概率质量。

代码验证了这种接口：`datamodule.py` 的 `expressed` 模式选择正计数基因，`TransformerVAE.forward` 用 `counts_subset/genes_subset` 编码，但用完整 `genes` 解码。观测数据配置采用 `sample_genes: expressed`；Parse1M 和 Replogle 按论文评测协议使用全部 2,000 个 HVG。

论文描述的 token 嵌入把计数信息与基因嵌入拼接后投影。代码提供多种投影方式，而当前基础配置使用 `log1p` 计数变换与基因嵌入的逐元素组合。因此，“融合计数与基因身份”是确定的设计，具体融合公式受配置影响。

### 5. MCAB 为什么能同时做池化和展开？

MCAB（Multi-head Cross-Attention Block）写作

$$
\mathrm{MCAB}_{\mathbf{S}}(\mathbf{X})
=F(\mathbf{X},\mathbf{S})+
\mathrm{MLP}(\mathrm{LN}_{F}(F(\mathbf{X},\mathbf{S}))),
$$

$$
F(\mathbf{X},\mathbf{S})=
\mathbf{Q}+\mathrm{Att}_{K}(\mathrm{LN}_{Q}(\mathbf{Q}),\mathbf{K},\mathbf{V}),
$$

其中查询 $\mathbf{Q}$ 来自伪输入 $\mathbf{S}$，键和值来自输入 $\mathbf{X}$。

在编码器中，$\mathbf{S}$ 是固定数量的可学习诱导点。无论输入基因如何排列，这些查询不变，而注意力对被排列的键值集合做聚合，因此输出是**置换不变**且长度固定的潜在 token。

在解码器中，$\mathbf{S}=\mathbf{E}_{\mathcal{I}}$，即待查询基因的嵌入。改变基因顺序就会以相同方式改变查询和输出，因此解码器是**置换等变**的。这种同一模块的双重用途是论文最重要的结构创新：不需要分别设计集合池化器和展开器。

### 6. 潜在表示：论文公式与公开默认代码的区别

论文从 VAE 出发，写出高斯变分后验

$$
q(\mathbf{Z}\mid\phi(\mathbf{x}_{\mathcal{I}}))
=\mathcal{N}(\mathbf{Z}\mid\mu(\mathbf{x}_{\mathcal{I}}),
\sigma(\mathbf{x}_{\mathcal{I}})),
$$

并用带 $\beta$ 权重的 ELBO 训练。论文也明确说明：当 $\beta=0$ 时，编码器可以只输出 $\mu$，这就成为潜在扩散常用的确定性自编码器。

**代码验证结论：**当前 `vae_base.yaml` 选择的 `TransformerVAE` 正是这种确定性 token 化路径。`Encoder.forward` 直接输出潜在 token，`VAE.loss` 只有重建似然，没有 KL 项。仓库中的另一个 `VAEScvi` 类具有显式高斯后验和 KL 权重，但它不是基础 Transformer VAE 配置。理解论文时必须把“论文讨论的模型族”与“公开默认配置”分开。

### 7. 负二项计数解码

对每个基因，解码器先产生未归一化输出 $h_i(\mathbf{Z})$，再计算

$$
p_i(\mathbf{Z})=
\frac{\exp(h_i(\mathbf{Z}))}{\sum_j\exp(h_j(\mathbf{Z}))},
\qquad
\eta_i(\mathbf{Z})=L\,p_i(\mathbf{Z}),
$$

最后令

$$
x_i\sim\mathrm{NB}(\eta_i(\mathbf{Z}),\alpha_i).
$$

$L$ 是细胞文库大小，$\alpha_i$ 是共享或基因特异的离散度。代码中的 `NegativeBinomialTransformerLayer` 与此直接对应：对均值 logits 做 softmax，乘以文库大小，并把离散度指数化，然后交给 scvi-tools 的负二项分布实现。代码也允许配置高斯输出头；论文指出高斯与负二项哪个更优依任务而定，目前不能端到端自动选择。

### 8. 第二阶段：潜空间流匹配

自编码器训练后被冻结。设真实细胞编码为潜在样本 $\mathbf{Z}_1$，高斯噪声为 $\mathbf{Z}_0$，在线性路径上采样时间 $t$ 并构造 $\mathbf{Z}_t$。DiT 学习该路径的速度场：

$$
\mathcal{L}_{FM}
=\mathbb{E}
\left[\|v_\theta(\mathbf{Z}_t,t,y)-u_t\|_2^2\right].
$$

代码中的默认配置是 `path_type: Linear`、`prediction: velocity`、`loss_weight: velocity`。`Transport.training_losses` 会采样时间和噪声、构造插值点与目标速度，再计算逐样本均方误差。

DiT 把潜在 token 当作一个短序列：先投影特征维度，加入固定位置编码，把时间嵌入与条件嵌入相加，然后通过使用自适应归一化的 Transformer 块预测速度。公开默认配置与论文表 9 在 8 个块、8 个头、宽度 256 等关键参数上相符。

### 9. 多属性分类器自由引导

论文的联合引导公式是

$$
\tilde{v}_{t,\epsilon}(\mathbf{Z},y)
=v_{t,\epsilon}(\mathbf{Z};\mathrm{Null})
+\omega\left[v_{t,\epsilon}(\mathbf{Z};y)
-v_{t,\epsilon}(\mathbf{Z};\mathrm{Null})\right].
$$

$y$ 可以是多个属性的联合取值，例如“CD4 Naive + IL-9”或“HepG2 + PPP6C”。训练时，模型随机把条件替换为专门的空 token；采样时，同时计算无条件与联合条件速度，再用强度 $\omega$ 外推。

代码有两条路径：

- `joint`：一次性嵌入所有条件组合，适合扰动数据；
- `mutually_exclusive`：逐条件计算差值并相加，类似加性引导。

一个重要实现细节是：联合路径接收一个条件权重字典，但实际使用这些权重的平均值。因此当各权重相同时，它与论文的单个 $\omega$ 一致；若权重不同，代码不会分别保留它们。

### 10. 生成时发生什么？

1. 检查基因、条件和引导权重的 batch 大小与键是否一致。
2. 根据条件标签和训练集统计量采样对数文库大小。
3. 生成形状为 `[batch, latent_tokens, latent_width]` 的高斯噪声。
4. 把噪声与条件复制成无条件、有条件两半。
5. 用 ODE 求解器积分 DiT 速度场，得到终点潜在 token。
6. 用目标基因 ID 作为查询，经 Transformer 解码器与 MCAB 展开。
7. 构造负二项或高斯分布并采样表达值。
8. 返回无条件/有条件计数和潜在表示。

**实现注意事项：**`LatentDiffusion.sample` 接收 `timesteps`，上层预测接口也读取该配置，但它调用 `sample_ode()` 时没有传入 `num_steps=timesteps`。在当前 commit 中，实际采用求解器默认的 50 个保存点。对自适应 Dopri5 来说，这 50 是保存/插值点，不等于内部函数评估次数。

### 11. 论文如何评测？

论文使用三个任务组：

- **观测数据重建与生成：**Dentate Gyrus、Tabula Muris、HLCA；比较 scVI、scDiffusion 和 CFGen。
- **多属性扰动生成：**Parse1M 与 Replogle；比较 CPA、scVI、scGPT、STATE-Tx、CellFlow 等，并留出未见的“细胞背景 + 扰动”组合。
- **嵌入评测：**在 CellxGene Census 上训练 20M、70M、270M 版本，再在 COVID-19 与 Tabula Sapiens 2.0 上做逻辑回归分类。

指标包括重建误差、PCC、MSE、Wasserstein-2、MMD、Fréchet Distance、1-NN accuracy、precision/recall，以及 ROC AUC、PR AUC 和 F1。

论文报告的代表性结果包括：Tabula Muris 上 scLDM 的 PCC 为 0.376，scVI 为 0.221，CFGen 为 0.136；联合引导把 Parse1M 的 W2 从加性方法的 15.850 降到 12.455，把 Replogle 的 W2 从 18.538 降到 11.288；270M Census VAE 的重建误差为 1441.7、PCC 为 0.783、MSE 为 0.091。

直接查看本地图像后，可以确认：Figure 1 清楚呈现两阶段结构；Figure 2-3 显示生成样本与真实样本在低维嵌入中广泛重合；Figures 6-8 中 scLDM 的基因方差散点整体更靠近对角线；Figures 13-15 显示部分潜在 token 对特定基因集有局部富集。最后一类结果只能用于提出“token 可能发生功能分化”的假设，不能把注意力分数当作因果解释。

### 12. 代码复现性与已知缺口

代码与论文的总体匹配度为**中等**。核心模型和采样路径都能在源码中找到直接对应：集合 token 化、固定潜在 token、基因查询解码、负二项参数化、流匹配损失、DiT、ODE 采样和两种 CFG 策略。

仓库 README 提供 Python 3.11 安装、从源码安装 `cellarium-ml`、公共 S3 模型工件下载、数据布局、VAE/LDM 训练和推理命令，配置文件也覆盖主要数据集。仓库中还未找到一个可一键重建全部表格和图像的脚本或 notebook。

本地转换包含 Figures 1-3 和 6-15；Figures 4-5、16、17 没有对应图像文件，不能把其图注当作已查看的视觉证据。论文自身还承认两个范围限制：似然类型需要按任务选择，且当前只处理转录组，没有整合染色质可及性或蛋白等模态。

### 13. 一句话理解

scLDM 的关键不是简单地“把扩散模型用于单细胞”，而是先用交叉注意力把无序、稀疏、计数型基因集合变成固定长度的潜在 token，再让 DiT 在这个结构正确的潜空间里学习细胞分布与联合条件响应，最后通过基因 ID 查询和计数似然还原到原始表达空间。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Scalable Single-Cell Gene Expression Generation with Latent Diffusion Models

### Problem

Single-cell expression profiles are high-dimensional, sparse count data in which gene order has no biological meaning. Many generative models nevertheless use fixed-position vectors, restrict analysis to highly variable genes, or model normalized continuous values. These choices make vocabularies inflexible, conflict with exchangeability, and may discard the count-generating structure. GAN-based alternatives also carry mode-collapse and optimization risks, while earlier latent diffusion methods commonly use shallow MLP autoencoders.

### Proposed Method

scLDM combines an exchangeable Transformer autoencoder with latent flow matching. Its Multi-head Cross-Attention Block (MCAB) has two roles: fixed inducing queries pool unordered gene/count tokens into a fixed number of permutation-invariant latent tokens, and requested gene embeddings query those tokens to produce permutation-equivariant likelihood parameters. A Negative Binomial head models raw counts using library-size-scaled gene means and dispersion.

Training proceeds in two stages. First, the autoencoder learns to reconstruct expression. Second, the autoencoder is frozen and a Diffusion Transformer learns a vector field over its latent-token distribution using linear interpolants and flow-matching loss. At generation time, an ODE maps Gaussian noise into latent tokens; classifier-free guidance can condition this process on one attribute or a joint tuple such as cell type plus cytokine. The decoder then samples gene-expression counts.

### Evaluation

The paper evaluates observational reconstruction/generation on Dentate Gyrus, Tabula Muris, and HLCA; perturbational conditional generation on Parse1M and Replogle; and out-of-distribution embedding quality on COVID-19 and Tabula Sapiens 2.0. Baselines include scVI, scDiffusion, CFGen, CPA, scGPT, STATE-Tx, CellFlow, TranscriptFormer, Geneformer, UCE, and AIDO.Cell. Metrics cover reconstruction error, PCC, MSE, Wasserstein-2, MMD, Fréchet distance, 1-NN accuracy, precision/recall, and classification metrics.

Paper-reported examples include PCC 0.376 on Tabula Muris versus 0.221 for scVI and 0.136 for CFGen, and MSE 0.095 on HLCA versus 0.117 for CFGen and 0.238 for scVI. On multi-attribute guidance, joint conditioning improves over additive guidance: Parse1M W2 falls from 15.850 to 12.455 and Replogle W2 from 18.538 to 11.288. Scaling the Census VAE from 20M to 270M parameters improves reconstruction error from 1742.7 to 1441.7 and PCC from 0.661 to 0.783. These values are paper claims and were not independently rerun in this workspace.

Direct image reads support the architecture, broad generated/true manifold overlap, closer gene-wise variance alignment for scLDM than displayed competitors, and localized cross-attention enrichment across latent tokens. The UMAP and attention panels are qualitative and do not by themselves prove quantitative superiority or causal biological interpretation.

### Code-Paper Match

Overall fidelity is **medium**. Direct source inspection verifies the main architecture and generation path: expressed-gene tokenization, fixed latent tokens, gene-query decoding, Negative Binomial parameters, velocity flow-matching loss, DiT conditioning, ODE sampling, and joint/additive CFG branches. Two differences matter:

- The paper presents a Gaussian posterior and beta-weighted ELBO as the model family, but the released default Transformer VAE is the beta-zero-style deterministic tokenizer with reconstruction-only loss.
- Joint CFG code averages the supplied per-condition scale values, and the public `timesteps` argument is accepted but not forwarded to the ODE sampler, which therefore uses its default 50 saved points.

### Reproducibility

The public repository is substantive: its README documents Python 3.11 installation, a required source install of `cellarium-ml`, public artifact download commands, dataset layouts, VAE and LDM training, and inference. Hydra configs cover the evaluated datasets and model variants. However, this acquired workspace contains no installed environment, benchmark datasets, or downloaded checkpoints, and no single checked script/notebook was found that regenerates all reported tables and figures. Runtime and numerical reproducibility are therefore **not verified**.

The paper also notes scientific limitations: Gaussian versus Negative Binomial likelihood must be selected per task, and the current framework covers transcriptomics rather than multimodal measurements. Some paper figures (4-5, 16, 17) were absent from the local image conversion and were not treated as visual evidence.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
