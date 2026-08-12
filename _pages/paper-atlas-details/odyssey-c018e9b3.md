---
layout: default
permalink: /paper-atlas/odyssey-c018e9b3/
title: "Odyssey"
nav: false
description: "Odyssey 把蛋白序列和离散结构当作共同去噪的 source，用局部矩阵共识在残基邻域传播信息，并通过离散扩散完成联合生成；其数学与计算实验描述丰富，但在没有公开代码、权重、数据清单和湿实验验证时，最强结论仍应限定为 paper-reported computational evidence。"
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
      <span>Protein &amp; Sequence Models</span>
      <span>bioRxiv · 2025</span>
    </div>
    <h1>Odyssey</h1>
    <p>Odyssey: reconstructing evolution through emergent consensus in the global proteome</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2025.10.15.682677" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Odyssey：用离散结构词元、局部共识和扩散过程联合生成蛋白序列与结构

### 1. 方法要解决的不是普通“续写蛋白序列”

Odyssey 把蛋白设计看成同步的多模态生成问题。蛋白不是只有氨基酸序列：残基还受到主链几何、侧链堆积、二级结构、溶剂暴露、结构域和功能上下文的约束。若模型只逐个预测序列 token，它可以学到统计共现，却未必能让远距离突变共同形成可折叠的三维结构。

论文因此设置两条需要被生成的 source track：氨基酸序列和离散结构；再加入二级结构、SASA、orthologous group、语义描述、结构域和 pLDDT 等 context track。设计者可以用 mask 保留活性位点或指定上下文，让其余位置在反向扩散中被共同补全。最终输出是氨基酸序列和 atom-14 坐标，而不是单纯的语言模型 embedding。

Odyssey 的三项核心设计是：用 finite scalar quantization（FSQ）把连续坐标变成结构 token；用局部矩阵加权的 consensus 替代主干中的 self-attention；用 score-entropy discrete diffusion 学习逐步反转 mask 污染。论文还用 D2-DPO 对序列反向核做偏好对齐，但这个对齐依赖 pTM 与活性位点 constrained RMSD 的计算代理，并没有湿实验验证。

### 2. FSQ：先让三维结构进入离散词表

扩散主干处理离散 token，所以连续坐标要先编码。Odyssey 使用固定格点

$$
H=\{0,\ldots,6\}\times\{0,\ldots,4\}^4,
$$

词表大小为 $7\times5^4=4375$。投影后的五维向量分别截断、缩放并四舍五入到格点，再用字典序映射为一个整数 token：

$$
x_{\mathrm{quant},l}
=\left\lfloor
\operatorname{clip}(m_lx_{\mathrm{proj},l}+n_l,0,h_l-1)+\frac12
\right\rfloor.
$$

量化本身不可微，训练用 straight-through estimator 让梯度穿过取整。FSQ 没有 VQ-VAE 那种需要学习的 codebook，因此避免 codebook collapse 和额外 commitment loss；但“固定格点”不表示结构表示无需学习，格点前后的 encoder/decoder 仍决定哪些几何被压缩到哪些 token。

训练分两阶段。Stage 1 从被 mask 的三主链原子坐标编码并重建 backbone；预测与真值先做 Kabsch 对齐，再计算坐标误差，从而去除整体旋转和平移。Stage 2 冻结 encoder，训练更大的 decoder，根据结构 token 与序列 token 重建 atom-14 坐标。序列条件必不可少，因为不同氨基酸的侧链原子组成不同，仅凭同一个结构 token 不能确定 atom-14 各槽位的化学身份。

图 8 在 CAMEO、CASP15 和 CASP16 上报告 stage-1/backbone 与 stage-2/atom-14 RMSD，图 9给出 CAMEO 重建叠合。这些结果说明离散瓶颈仍可保留坐标，但 RMSD 是重建指标，不等于从零生成的新蛋白能表达或有功能。

### 3. source 与 context 是两类不同的信息

Odyssey 将

$$
z_{\mathrm{source}}=[z_{\mathrm{seq}},z_{\mathrm{struct}}]
$$

作为需要去噪生成的内容；二级结构、SASA、orthologous group、语义描述、结构域和 pLDDT 则构成 $z_{\mathrm{context}}$。序列和结构 embedding 按残基位置相加形成长度 $L$ 的 source 表示。

位置对齐的上下文（例如每个残基的二级结构、SASA、domain、pLDDT）通过 cross-consensus 注入；不与每个残基一一对齐的 orthologous-group tags 和语义描述通过 cross-attention 注入。这一区分很实用：局部几何标签可以与对应残基直接协商，而一串功能词或多个 OG 标签需要全局检索。

图 1 从左到右展示数据流：FSQ encoder 把坐标变成结构 token；序列/结构 source 与多种 context 合并；时间条件的 self-consensus blocks 预测序列和结构概率比；反向扩散得到 token 后，48-block FSQ decoder 生成 atom-14 坐标。图是论文架构声明，不是本地可执行 module tree。

### 4. Consensus：把 token 混合写成局部能量下降

Self-consensus 只连接序列窗口内的残基：

$$
E=\{(i,j):0<|i-j|\le w\}.
$$

每条有向边不是一个标量 attention weight，而是正定矩阵

$$
R^{(i,j)}=\alpha^{(i,j)}I+
\beta^{(i,j)}(\Lambda^{(i,j)})^\top\Lambda^{(i,j)}.
$$

$\alpha I$ 提供各方向稳定的收缩，低秩项选择需要更快达成一致的 feature directions。所有边定义局部分歧能量

$$
E(U)=\frac12\sum_{(i,j)\in E}
(u^{(i)}-u^{(j)})^\top R^{(i,j)}(u^{(i)}-u^{(j)}),
$$

一层 consensus 对每个 residue feature 做一次学习步长的梯度更新：

$$
u^{(i)}_1=u^{(i)}_0-\eta^{(i)}\nabla_{u^{(i)}}E(U_0).
$$

图 2 用二维平面直观画出中心残基与窗口邻居的差向量、各向同性和低秩作用、入边/出边梯度以及更新位置。与 attention 的区别不是“完全没有内容依赖”，而是内容依赖被编码为局部边上的矩阵 agreement operator，而非所有 token 两两归一化的标量权重。

论文给出的复杂度为

$$
O(Ld^2+Ldwr\xi),
$$

当窗口 $w$、秩 $r$ 和边网络宽度 $\xi$ 固定时对长度 $L$ 线性。但全局信息需要多层局部传播；常数项、层数和 $d^2$ 投影仍可能很大。Odyssey 最大模型达到 102B 参数，因此“长度线性”不等同于廉价训练。

### 5. 离散扩散：训练时逐步毁掉，生成时逐步恢复

正向过程把内容 token 独立变为吸收态。source track 使用 `MASK`，context track 使用 `IGN`，`PAD/BOS/EOS` 等特殊 token 不参与演化。几何噪声日程 $\sigma(t)$ 下，一个内容 token 保持不变的概率为 $e^{-\sigma(t)}$，被污染的概率为 $1-e^{-\sigma(t)}$。

$$
p_{t|0}(\gamma|z_0)=
\begin{cases}
e^{-\sigma(t)},&\gamma=z_0,\\
1-e^{-\sigma(t)},&\gamma=\mathrm{MASK/IGN}.
\end{cases}
$$

模型不直接回归坐标，而是估计每个位置、每个候选 token 的概率比，用它近似反向连续时间马尔可夫链（CTMC）的 generator。训练目标是 diffusion-weighted denoising score entropy（DWDSE），序列与结构 loss 各占一半。论文推导它在一个终端 KL 项之外上界负对数似然；因此图 6 的 hatched 区域提醒读者：DWDSE perplexity-like 数值与普通 MLM perplexity 并非完全相同的估计量。

生成从 designer mask 开始。被保留的位置固定原 token，待设计位置初始化为 `MASK/IGN`；tau-leaping/Tweedie 式离散更新沿时间从 $T$ 走到 0，逐步采样序列与结构 token。最后序列 token 映射为氨基酸，结构 token 经 stage-2 decoder 转成 atom-14 坐标。图 3 画的就是这个正向 mask 和反向恢复的时间方向。

与固定比例 MLM 的核心差别是：扩散训练覆盖不同污染程度，使模型在接近“整条蛋白都未知”的状态也学习恢复；这更接近从头生成。它不意味着反向过程真实模拟自然进化，也不保证每条采样轨迹满足物理能量最低。

### 6. Scaling 与两个关键消融怎样读

图 4 用 142M–1.2B 的模型和最多 80B token 拟合修改后的 Kaplan scaling law，报告 $r^2=0.993$，并推导 compute-optimal frontier。随后论文训练 1.2B、12B 和 102B production models，source validation perplexity 报告为 7.294、5.097 和 3.882，最大训练量超过 $1.1\times10^{23}$ FLOPs。

这支持“在论文扫描范围内，扩大模型改善所报告验证指标”，但 $r^2$ 是对拟合点的描述，不是超出范围后必然继续缩放的定律。102B 训练日志、checkpoint 和原始验证预测未公开，本地无法独立核查。

图 5 在 35M、142M、552M 的 MLM 架构中只替换 attention/consensus，并扫学习率。随着模型变大，attention 的近最优学习率区间变窄并出现 loss spike，而 consensus 保持更宽、下降更平缓。证据支持“在这些配置和日程中更稳健”，不证明 consensus 在所有任务、优化器和长度上都优于 attention。

图 6 在 35M、142M、1.2B 比较 simple masking、complex masking 和 discrete diffusion。验证统一使用生成式的多污染级别日程，diffusion 更好地匹配这个评估分布；simple MLM 尤其在 1.2B 上出现训练与验证落差。公平解读是“训练目标与生成时 corruption distribution 匹配更好”，而不是仅凭不同定义的 perplexity 断言普遍生成质量更高。

### 7. D2-DPO 对齐：优化的是计算代理，不是实测酶活

论文在六个 held-out M-CSA enzymes 上做对齐。每个蛋白生成 2048 条序列，再折叠并计算

$$
S_{\mathrm{val}}=\alpha\log(\mathrm{pTM})-
\mathrm{cRMSD}/\tau.
$$

pTM 衡量全局折叠置信，cRMSD 衡量受约束活性位点几何。winner/loser pair 用于 D2-DPO，只更新序列 reverse kernel，其他 tracks 作为条件。图 7 比较对齐前后的内部预测分数与代理真值：例如 1BS9 的 Spearman $\rho$ 从 0.090 升至 0.792，1CWY 从 -0.265 升至 0.654；不同酶改善幅度并不一致。

这说明对齐可以让模型排序更接近 pTM/cRMSD 目标，但“true score”只是论文命名的计算代理。它没有测量表达量、热稳定性、催化速率、底物特异性或细胞毒性；模型也可能学会代理漏洞。因此这个结果应定位为候选筛选信号，而不是成功设计功能酶的实验结论。

### 8. 数据与泄漏边界

论文预训练数据来自 UniRef、MERC、SRC、AntiRef、OMG、PDB、ESMAtlas 和 AlphaFoldDB，总计约 36.62 亿 expansion-level proteins。序列 cutoff 为 2024-01-01，结构 cutoff 为 2022-08-01；不同来源用不同相似度层级聚类并采样，以降低大蛋白家族的过度代表。

这些描述为概念复现提供框架，但本地没有原始 manifest、cluster assignments、去重脚本、annotation join、token vocabulary 文件或 split hash。因而不能独立验证时间 cutoff、同源泄漏、数据许可或每条 context track 的实际覆盖率。尤其是结构资源含预测结构时，训练指标同时反映实验结构和上游模型知识。

### 9. 为什么这里没有 paper-code “匹配率”

该 bioRxiv 稿及已获取页面没有公开仓库、checkpoint、训练日志或代码可用性链接；工作区也没有 Odyssey 源码目录。因此可核查的是论文公式、表格、图、图注和补充材料，不包括：

- FSQ encoder/decoder 的真实 tensor shape、mask 和 Kabsch 实现；
- consensus edge MLP、窗口/秩默认值、稀疏 kernel 与数值稳定措施；
- DWDSE loss、CTMC sampler 与 tau-leaping 实现；
- 36.62 亿数据的预处理、分片和混合采样；
- 102B 分布式训练配置、日志与 checkpoint；
- scaling/ablation 的原始曲线与绘图脚本；
- M-CSA 生成序列、折叠工具版本、pTM/cRMSD 脚本与 D2-DPO 代码。

`doc_code.md` 因此把所有实现敏感项标为 `Not found/MISSING`。这不是说论文方法不存在，也不是复现失败，而是当前证据不足以从“论文声称”升级为“源码已验证”。若未来作者发布代码，应重新锁定仓库 URL、commit、checkpoint 版本和数据 manifest，再重做 code-paper map。

### 10. 当前工作区能支持到哪里

本地有 bioRxiv PDF、PyMuPDF 转换的完整正文与补充材料、13 张抽取图、方法文档、figure analysis 和证据账本。它足以解释 FSQ、consensus、离散扩散、D2-DPO 以及图 1–9 的逻辑，也足以保留公式和论文报告的数值。

它不能执行模型推理、生成新蛋白、验证 checkpoint、复跑 102B scaling、确认数据泄漏或复现酶 alignment。`ready_to_publish=true` 只表示这份 paper-only 分析合同和不确定性标注完整，不表示 Odyssey 软件可复现或论文结论已被独立验证。

### 11. 一句话抓住 Odyssey

Odyssey 把蛋白序列和离散结构当作共同去噪的 source，用局部矩阵共识在残基邻域传播信息，并通过离散扩散完成联合生成；其数学与计算实验描述丰富，但在没有公开代码、权重、数据清单和湿实验验证时，最强结论仍应限定为 paper-reported computational evidence。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Odyssey Summary

### Motivation and Novelty

Odyssey targets multimodal protein generation: designing or editing proteins while jointly modeling amino-acid sequence, 3D structure, and functional context. The paper argues that proteins should not be treated as text alone. A residue's role is constrained by covalent backbone geometry, local contacts, side-chain packing, solvent exposure, domains, and functional annotations. This motivates a generator that treats sequence and structure as synchronized source tracks and uses auxiliary context tracks to condition design.

The main novelty is the combination of three design choices:

1. a finite scalar quantizer (FSQ) that converts continuous atomic coordinates into a 4,375-token structure vocabulary;
2. a consensus mechanism that replaces self-attention with local, matrix-weighted agreement updates over a sparse residue graph;
3. score-entropy discrete diffusion, which trains the model to reverse a mask-only corruption process for sequence and structure tokens.

This differs from prior protein language models and NLP-inspired baselines. BERT (NAACL 2019) popularized masked-token training, but Odyssey argues that fixed masked-language modeling does not match progressive generation. Transformer self-attention (NeurIPS 2017) gives powerful all-pairs mixing but has quadratic length cost and, in the paper's ablations, worse learning-rate robustness at larger model sizes. ProGen-style protein language modeling (Nature Biotechnology 2023) and ESM3-style multimodal modeling (Science 2025) are key points of comparison, but Odyssey emphasizes local consensus, FSQ-based structure tokens, and discrete diffusion as its central redesign.

### Method Overview

Odyssey first tokenizes protein sequence and structure. Sequence uses a 25-symbol amino-acid vocabulary plus special tokens. Structure uses an FSQ trained in two stages: stage 1 learns 3-backbone reconstruction from masked coordinates, and stage 2 freezes the encoder while training a larger sequence-conditioned decoder for atom-14 reconstruction. Kabsch alignment makes the reconstruction loss invariant to global rotation and translation.

The transformer stack receives sequence and structure embeddings summed position-wise. Context is then injected residually. Position-aligned tracks such as secondary structure, SASA, domains, and pLDDT use cross-consensus; global tracks such as orthologous groups and semantic descriptions use cross-attention. The main stack uses time-dependent self-consensus blocks conditioned on diffusion time.

Consensus constructs local residue-neighborhood edges and learns a positive-definite matrix for each edge. The update is one gradient step on a quadratic local disagreement energy. The paper claims this gives $O(Ld^2+Ldwr\xi)$ complexity, linear in sequence length $L$ for fixed window/rank/edge hidden size.

Training uses score-entropy discrete diffusion. At a sampled timestep, source tokens are corrupted to `MASK` and context tokens to `IGN`; the model predicts probability ratios needed to simulate the reverse CTMC. Generation starts from a designer mask, progressively unmasks source tokens, maps sequence tokens back to amino acids, and decodes structure tokens to atom-14 coordinates. An optional D2-DPO alignment stage adjusts only the sequence reverse kernel using winner/loser mutant pairs scored by a proxy combining pTM and constrained active-site RMSD.

### Evaluation

The paper reports several empirical findings:

- FSQ reconstruction: stage-1 and stage-2 FSQs are evaluated on CAMEO, CASP15, and CASP16 using RMSD for 3-backbone and atom-14 coordinates. The paper claims state-of-the-art reconstruction and shows qualitative CAMEO overlays.
- Scaling: smaller Odyssey variants are fit with a modified Kaplan-style scaling law. The reported fit has $r^2=0.993$, and production models scale to 1.2B, 12B, and 102B parameters. Validation source perplexity improves from 7.294 to 5.097 to 3.882 across these sizes.
- Consensus ablation: masked-language models using consensus are compared to attention across learning rates at 35M, 142M, and 552M parameters. Consensus has a broader near-optimal learning-rate interval, especially at larger sizes.
- Diffusion ablation: discrete diffusion is compared with simple and complex masked-language modeling at 35M, 142M, and 1.2B parameters. Diffusion validates better under the generation-like corruption schedule.
- Alignment: D2-DPO alignment is tested on six held-out M-CSA enzymes. The model generates 2048 sequences per protein and uses pTM plus constrained RMSD as a composite true score. Alignment increases Spearman correlations between internal predicted scores and proxy true scores.

The strongest evidence is computational and model-internal: reconstruction RMSD, validation perplexity, scaling fits, and proxy-fitness correlations. The paper does not provide wet-lab validation of generated proteins, and the alignment score should be interpreted as a computational design proxy.

### Reproducibility

**Rating: 1.5 / 5.**

The manuscript is mathematically detailed and includes model configurations, major training objectives, dataset sources, cutoff dates, and many equations. That helps conceptual reimplementation.

However, no public code repository, model weights, training logs, generated sequences, data manifests, or evaluation scripts were found in the acquired bioRxiv HTML or paper markdown. The largest claims involve 102B-parameter training, massive private-scale datasets, and custom consensus/diffusion implementation details that cannot be audited from the paper alone. Key reimplementation details remain missing: exact preprocessing scripts, vocabulary files, consensus MLP/rank/window settings, diffusion hyperparameters, optimizer/distributed training details, and scoring tool versions for pTM/cRMSD.

All code-dependent claims are therefore marked `MISSING` in `claude_notes.md`. The workspace is publishable as a paper-only analysis because the missing public implementation is explicitly documented rather than silently assumed.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
