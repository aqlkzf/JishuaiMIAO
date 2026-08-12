---
layout: default
permalink: /paper-atlas/celltransformer-7ce430de/
title: "CellTransformer"
nav: false
description: "CellTransformer 不直接对整张组织切片建全局图。它以每个细胞为中心截取一个固定物理尺度的局部邻域，遮住中心细胞的表达，只保留它的细胞类型；模型必须用周围细胞的类型和表达预测中心细胞的基因计数。为了完成这个自监督任务，编码器把整个邻域压缩成一个 384 维“neighborhood representation”。训练后丢掉表达预测头，把每个中心细胞对应的邻域表示拿去做跨切片、跨动物的 k-means，得到空间域。"
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
      <span>Domain Clustering</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>CellTransformer</h1>
    <p>Data-driven fine-grained region discovery in the mouse brain with transformers</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-64259-4" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellTransformer 方法解读：把每个细胞的局部组织环境压缩成一个可聚类 token

### 一句话理解

CellTransformer 不直接对整张组织切片建全局图。它以每个细胞为中心截取一个固定物理尺度的局部邻域，遮住中心细胞的表达，只保留它的细胞类型；模型必须用周围细胞的类型和表达预测中心细胞的基因计数。为了完成这个自监督任务，编码器把整个邻域压缩成一个 384 维“neighborhood representation”。训练后丢掉表达预测头，把每个中心细胞对应的邻域表示拿去做跨切片、跨动物的 k-means，得到空间域。

### 输入、输出与问题边界

输入是单细胞分辨率空间转录组：每个细胞的坐标、探针计数和外部细胞类型标签。论文主要使用 3,737,550 个细胞、500 基因的 Allen 1 MERFISH，以及四只小鼠、1129 基因的 Zhuang MERFISH；另在全脑 Slide-seqV2 上展示迁移。

输出不是 CCF 解剖标签预测，而是用户指定 $k$ 后的无监督聚类编号。域数 $k$ 和邻域物理尺度均由用户给定，因此“发现多少区域”并非模型自动决定。CCF 只用于事后比较和解释，没有进入训练标签。

### 第一步：围绕参考细胞构造局部集合

对参考细胞 $r$，选同一组织切片中位于固定轴对齐方框内的邻居。论文写 MERFISH 使用 85 µm box。当前 loader 实现为

$$
[x_r-w_x/2,x_r+w_x/2)\times[y_r-w_y/2,y_r+w_y/2),
$$

而配置中 `patch_size=[17,17]`；训练脚本把重建坐标乘 100。85 µm 与 17 个内部单位之间的精确换算依赖数据坐标语义，仓库配置本身没有形成独立、显式的单位合同。

中心细胞从 observed tokens 中移除。若邻居超过上限（配置 250），代码随机下采样；因此同一中心细胞的训练上下文可能随采样变化。固定方框而非固定邻居数允许邻域 token 数量随细胞密度改变，也使模型编码部分局部密度信息。

### 第二步：把细胞类型与表达组合成 token

每个邻居细胞有两部分表示：

$$
e_i=[f_\theta(x_i);g_\theta(c_i)]\in\mathbb R^{384}.
$$

$f_\theta$ 是把 500 或 1129 个基因投影到 192 维的两层 MLP，含 LayerNorm 和 GELU；$g_\theta$ 是细胞类型的 192 维 embedding lookup。二者拼接后再做 LayerNorm。模型还为每个邻域加入一个可学习的 CLS-like register token。

细胞类型标签来自 ABC-WMB 的 scRNA-seq taxonomy 映射。它们隐含了全转录组参考信息，所以模型虽不使用空间域标签，却并非“只靠 MERFISH 原始计数、完全无外部监督”。论文的消融显示去掉类型条件仍能工作，但与 CCF 的相似度和空间一致性略降。

### 第三步：只允许同一邻域内自注意

多个不等长邻域在 batch 中展平，通过 attention mask 阻止不同样本的 token 互相通信。编码器默认 4 层、8 头、384 维；Slide-seqV2 使用 10 层编码器。自注意让一个细胞的更新依赖邻域内其他细胞：

$$
\operatorname{Attn}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^T}{\sqrt d}+M\right)V.
$$

它可被理解为动态学习细胞间相互作用权重，但 attention 权重不是已验证的生物相互作用边。

论文说 key/query/value 的 bias 有助于稳定训练。配置把 `bias=True` 传给 encoder/decoder，当前工厂代码确实将它传入 MultiheadAttention；旧文档把默认构造参数 `False` 误当成实验配置，需以实际 Hydra 配置为准。attention pooling 则强制使用 `bias=False, bias_kv=True`，是另一组参数。

### 第四步：注意力池化形成组织上下文瓶颈

一个可学习 query 对邻居 token 和 register token 做多头注意力池化：

$$
z_r=\operatorname{MHA}(q_{pool},E_r,E_r)\in\mathbb R^{384}.
$$

这就是核心的 neighborhood representation。所有细胞级信息必须先通过单个 384 维 token，才能参与中心细胞表达预测。这个强瓶颈迫使模型学习对预测有用的细胞组成、密度和分子环境统计，而不是记住完整邻域。

### 第五步：以中心细胞类型为 query 重建表达

中心细胞真实表达被遮住，但其细胞类型 $c_r$ 仍已知。解码器将独立的类型 embedding $q(c_r)$ 与 $z_r$ 配成长度 2 的序列，只允许同一邻域的两者互相注意。随后从参考细胞 token 投影四组基因参数：

$$
\mu_g=e^{a_g},\quad \theta_g=e^{b_g},\quad
s_g=e^{d_g},\quad \pi_g=\operatorname{logit}^{-1}(u_g).
$$

当前训练代码用 scvi-tools 的 `ZeroInflatedNegativeBinomial` 最大化被遮表达的似然。论文方法段先明确输出 mean、dispersion、scale、zero-inflation logit，却随后称“negative binomial”；以代码为准实际是 ZINB。这是术语不一致，不是“找不到损失”。

训练输入假定为 `log1p` 表达，损失前执行 `exp(x)-1` 还原计数。若输入不是自然对数 `log1p`，计数似然会被错误解释。

### 第六步：训练后只取 neighborhood representation

推理时对每个细胞构建邻域，取 $z_r$ 并跨切片拼接。论文使用 GPU cuML k-means，`n_init=3`、`oversampling_factor=3`、`max_iter=1000`；仓库脚本默认 CLI `maxiter=1500`，可由参数改写。可选步骤会在聚类前用 40 µm FWHM 的 Gaussian filter 平滑 embedding。论文同时指出平滑能去除某些高频 Crym+ 域，却会侵蚀细皮层边界，因此它不是无条件改进。

### 六张主图怎样读

- 图 1 是训练与推理示意：局部邻域、遮住中心细胞、单 token 瓶颈、跨切片聚类。
- 图 2 是主要整体评估：25/354/670 个域与 CCF 对照，并比较邻域同标签比例、离散域比例和细胞类型组成相关。所谓 4091.2% 相对提升来自对手基线非常低，绝对曲线更应优先阅读；空间平滑指标还天然偏好连续区域，不能独立证明解剖正确。
- 图 3 将自动域与 subiculum 文献分区、细胞类型和基因表达对应，是跨模态/既有研究一致性证据，不是训练时监督。
- 图 4 在 superior colliculus 中给出 CCF 未细分的层状候选域，并用已注释细胞类型组成支持。它是可信的发现线索，但“新层级已证实”仍需独立解剖验证。
- 图 5 在 midbrain reticular nucleus 提出四个亚域，并用 cell type 和 Bnc2/Six3/Pax5 等探针梯度解释。相同 MERFISH 数据既参与表示学习又参与解释，证据并非完全独立。
- 图 6 展示四只小鼠约九百万细胞的联合域和 Slide-seqV2 应用。跨动物域一致，但线性 probe 也能以超过 94% 准确率读出 donor，说明 embedding 保留明显个体信息；“整合”不等于去除 batch/donor 信号。

### 论文支持与不支持的结论

支持：局部 mini-batch 设计能处理多百万细胞；域在空间同质性和 CCF 组成对应上优于文中可运行的基线；表示能恢复多种已知层状结构；多动物联合聚类可产生广泛共享的域。

不支持：域等同于真实解剖边界；所有未编目亚域已被生物学验证；模型自动选择邻域尺度或域数；embedding 已消除个体差异；attention 可直接解释为细胞通讯。

### 当前代码快照的复现边界

核心 library 模型、loader、ZINB loss、聚类和平滑脚本均存在，论文–核心实现匹配度为 **Partial-to-High**。但完整复现入口存在明显工程漂移：训练与 embedding 脚本引用旧包名 `brainformr`，Hydra `config_path` 写死作者本机 `/home/ajl/...`，配置 `_target_` 也仍是 `brainformr.model.CellTransformer`；`pyproject.toml` 显式只声明 `packages=["celltransformer"]`，构建 wheel 时可能漏掉 `celltransformer.model/data/training` 子包。优化配置中的 weight decay 是 `1e-9`，与论文 `0.00005` 不符；batch 32、梯度累积 16 和两张 GPU 的组合也不能直接对应论文报告的 effective batch 256。

本地代码目录无嵌套 `.git` 或 `.repo_source`，无法确认采集提交；不能用 PaperCode 父仓库 HEAD 替代。测试覆盖模型基本块与数据 loader，但不覆盖论文全流程、cuML 聚类、百万级训练或主图重现。

### 使用时必须记录

应记录坐标单位、box 尺寸、最大邻居数、细胞类型 taxonomy 版本、基因面板、encoder 深度、随机下采样种子、checkpoint、embedding 是池化前后哪一个 token、是否平滑及其带宽、k-means 的 $k$ 和随机重复。没有这些信息，同一组织可能产生不同的空间域层级。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellTransformer 论文与代码复核摘要

### 结论

CellTransformer 通过“遮住中心细胞表达、用局部邻域预测它”的自监督任务，把每个细胞周围的类型、表达和密度信息压缩成 384 维 neighborhood representation，再跨切片、跨动物用 k-means 得到用户指定粒度的空间域。局部 neighborhood mini-batching 避免建立全数据集距离矩阵，使模型能处理多百万细胞。

论文在 3.74M 细胞 Allen MERFISH、四动物约 5.82M 细胞 Zhuang MERFISH 和全脑 Slide-seqV2 上展示方法。域与 CCF 的空间结构和细胞类型组成高度对应，并复现 subiculum、superior colliculus 等已知分层；MRN 与若干 CCF 未细分区域属于模型提出并由同数据 marker 支持的候选亚域，不应写成独立实验确认。

### 最重要的证据边界

- CCF 不参与训练，但用于评估和选择解释；对应性不等于域边界的唯一真值。
- 邻域同标签比例天然奖励空间平滑。4091.2% 相对提升由极低对手值放大，应同时看绝对曲线。
- 平滑可去掉高频域，也会侵蚀真实的细层边界。
- 跨动物域可一致，同时 donor identity 仍能从 embedding 以 >94% 准确率读出。
- 邻域半径和域数 $k$ 都需要用户指定。

### 代码匹配

**Partial-to-High。** 核心架构、mask、attention pooling、ZINB、ZINB NLL、embedding 提取、cuML k-means 和平滑脚本均存在。主要差异/工程边界：

- 论文文字称 NB，但代码明确训练 ZINB；论文同时列出 zero-inflation 参数，属于术语不一致。
- 论文 k-means `max_iter=1000`，脚本默认 1500。
- 论文 weight decay `0.00005`，仓库基础配置为 `1e-9`；batch/梯度累积/双 GPU 配置也不能直接对应报告的 effective batch 256。
- 训练脚本、Hydra targets 和绝对配置路径仍使用旧项目名 `brainformr`/作者本机路径，不能从干净安装直接运行。
- `pyproject.toml` 只显式列出根包，wheel 可能漏装子包。
- 稳定性 criterion 的 20 次聚类实现未在当前仓库找到。

### 复现性

核心块有测试，但本工作区未下载多百万细胞数据、未训练模型、未执行 cuML 聚类，也未重建主图。代码目录没有独立 git/provenance sidecar，所分析上游 commit 未知。当前结论是“论文与核心代码可追踪，但发布快照不是开箱即用的完整复现包”。

### 来源

- 论文：`paper source/PMC12504640/paper.md`
- 主图：`paper source/PMC12504640/images/`
- 补充材料：`paper source/PMC12504640/*MOESM*.pdf`
- 代码：`code/`
- DOI：`10.1038/s41467-025-64259-4`

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
