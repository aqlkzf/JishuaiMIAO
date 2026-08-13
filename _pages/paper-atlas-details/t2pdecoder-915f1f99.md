---
layout: default
permalink: /paper-atlas/t2pdecoder-915f1f99/
title: "T2Pdecoder"
nav: false
wide: true
description: "RNA 测量很普遍，质谱蛋白组却昂贵且覆盖不足；更关键的是，RNA 丰度并不是蛋白丰度的可靠替身。现有 RNA→蛋白方法多针对单细胞，常只覆盖数百个蛋白，难以支撑 bulk 队列中的蛋白通路、分型和临床关联分析。T2Pdecoder 的目标不是宣称 RNA 能完全决定蛋白，而是在已有转录组的样本上预测 5,738 个蛋白的轮廓，从而获得可用于“蛋白质中心”分析的补充视角。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Communications · 2026</span>
    </div>
    <h1>T2Pdecoder</h1>
    <p>T2Pdecoder enables protein-centric analyses from transcriptomic data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-74209-3" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for T2Pdecoder">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Lucienxy/T2Pdecoder" target="_blank" rel="noopener noreferrer" aria-label="Open code for T2Pdecoder">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## T2Pdecoder：把转录组转换为可做蛋白质组解释的预测谱

### 它要解决什么问题？

RNA 测量很普遍，质谱蛋白组却昂贵且覆盖不足；更关键的是，RNA 丰度并不是蛋白丰度的可靠替身。现有 RNA→蛋白方法多针对单细胞，常只覆盖数百个蛋白，难以支撑 bulk 队列中的蛋白通路、分型和临床关联分析（论文 paper.md:27-39）。T2Pdecoder 的目标不是宣称 RNA 能完全决定蛋白，而是在已有转录组的样本上预测 5,738 个蛋白的轮廓，从而获得可用于“蛋白质中心”分析的补充视角。

### 核心想法：把两类训练数据拼成一条推断链

方法把数据按是否同时拥有 RNA 和蛋白分工：配对数据负责学会“同一样本的 RNA 和蛋白在潜空间应相遇”，蛋白-only 数据负责学会“怎样从潜变量还原完整蛋白谱”。最后把 RNA 端接到蛋白解码器。

```text
配对 RNA x + 蛋白 y
      │
      ├─ RNA 编码器 f_R(x) ─┐
      └─ 蛋白编码器 f_P(y) ─┴─> 对齐的低维 code

蛋白-only y ─> VAE 编码器 ─> z_mean ──MSE──> 固定的 f_P(y)
                         │
                         └─> VAE 解码器 g_P ─> 重建蛋白 y_hat

新 RNA x* ─> 固定 f_R ─> code ─> 固定 g_P ─> 预测蛋白 y_hat*
```

这正是 Fig. 1b 的三块：CLIP 模型、蛋白 VAE、以及推断时的固定 RNA encoder + 固定 decoder；Fig. 1a 还区分了 RNA-only、配对 RNA/蛋白、protein-only 三种输入来源。

### 第一步：配对 RNA--蛋白表示对齐

对同一样本，RNA encoder 和 protein encoder 分别输出 $r_i=f_R(x_i)$ 与 $p_i=f_P(y_i)$。论文用正样本损失拉近同一人的 $(r_i,p_i)$，用负样本损失推远不同人的配对：

$$L_{CLIP}=L_{pos}+wL_{neg}.$$

其中相似性基于 cosine similarity（论文 paper.md:213-227）。它先在 CPTAC 泛癌配对数据上预训练，再在胶质瘤配对数据上微调（paper.md:47,55-61）。论文报告泛癌阶段 1,351 个样本、18,860 个 RNA 特征和 5,738 个蛋白特征；胶质瘤微调用 210 个配对样本（paper.md:57-61）。

代码确实实现了这一训练意图：`src/CLIP_pre_train.py:31-59` 为 batch 内全部非同索引配对创建负样本，并以 `CosineEmbeddingLoss` 的 +1/-1 标签计算正负损失；`src/CLIP_pre_train.py:121-125,152-162` 同时优化两个 encoder。需要保留一个细节边界：这与论文公式在语义上相符，但不是逐字公式实现（代码没有显式 $w$）。而且 `EmbeddingModel` 是三段 Linear--BatchNorm--ReLU 后接线性投影（`src/model.py:14-45`），与论文“五层且末端 ReLU”的文字描述不完全一致。

### 第二步：用大量 protein-only 样本训练带监督的 VAE

仅靠配对数据会浪费更多没有 RNA 的蛋白组。VAE 从蛋白 $y$ 得到潜变量、再重建 $\hat y$；同时要求 VAE 的均值表示 $z_{mean}$ 接近已经学好的蛋白 CLIP 表示 $f_P(y)$。论文的组合目标可写为：

$$L_{VAE}=L_{rec}+w_{KL}L_{KL}+w_{t2}\mathrm{MSE}(z_{mean},f_P(y)).$$

论文还使用 BN-VAE 的缩放参数，以缓解 KL 项消失（paper.md:245-323）。源码中的 `Scaler`、`Sampling` 和 `VAE` 对应这条路径：包括缩放、重参数采样、解码、重建 MSE 与 KL（`src/model.py:56-144`）。训练脚本把 protein embedding CSV 读入，`Task2Loss` 就是 MSE，且默认 `t2_w=1`（`src/T2Pdecoder_VAE_train.py:27-34,63-84,111-135`）。

一个容易忽略的实现差异是模型选择：脚本按验证集的重建 MSE 最小保存 `BN_VAE_best.pth`，并非按包含 KL 与对齐项的完整总损失保存（`src/T2Pdecoder_VAE_train.py:137-159`）。所以“训练目标”和“早停/选模型准则”不能混为一谈。

### 第三步：新 RNA 如何变成预测蛋白？

概念上只需 $\hat y=g_P(f_R(x))$。代码分成两步：`CLIP_ft_app.py:52-67` 加载 RNA encoder，对 RNA CSV 产生并标准化 embedding；`T2Pdecoder_generator.py:55-93` 加载 VAE checkpoint，读取带 `PID` 的 embedding CSV，调用 `vae.decode` 写出预测蛋白 CSV。换言之，代码可支持这条链，但 generator 的直接输入是**预先计算的 RNA embedding**，不是原始 RNA。

`process.py:16-19,33-42,53-62` 还规定了输入列顺序：按固定 gene/protein list 重排，缺失特征补 0。这让输入形状兼容，也意味着“未测到/缺失的特征”被作为零值处理；实际应用时应确认这是否符合数据的归一化和缺失含义。

### 结果该怎样读？

论文报告预测蛋白相对直接 RNA 与实测蛋白的相关性有稳定但有限的提高，且在独立 cohort 的增益更小；通路层面突出细胞增殖和 OXPHOS（paper.md:69-81，Fig. 2--3）。Fig. 4 用预测蛋白做单细胞细胞状态/标记分析，Fig. 5 用 bulk 胶质瘤预测蛋白分群并展示生存关联。最稳妥的结论是：它为蛋白层面的富集、分群和标记分析提供了一个可扩展的推断表征；不能据此推论每一个单蛋白都被同等准确地恢复，更不能把关联结果理解为因果。

### 可复现性边界

已检索仓库根目录及 `src/*.py`。**未找到** requirements 或环境文件、训练/评测数据、预训练 checkpoint、测试以及一个从原始 RNA 直达预测蛋白的统一命令。因此，这个快照足以核查关键实现路径，但不足以在不补齐外部资产的情况下独立复跑全文实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## T2Pdecoder: protein-centric analysis from transcriptomes

### Problem and contribution

Mass-spectrometry proteomics is much less available than RNA sequencing, while RNA abundance is an imperfect proxy for protein abundance. Existing RNA-to-protein tools are largely single-cell oriented and commonly cover at most a few hundred proteins, limiting bulk clinical applications and proteome-scale interpretation (paper.md:27-39). T2Pdecoder is a transfer-learning framework intended to predict 5,738 proteins from transcriptomes by combining paired RNA--protein data with protein-only data.

It has three components: paired-modality CLIP-style encoders learn a shared RNA/protein embedding; a protein VAE learns to reconstruct protein profiles while matching the CLIP protein embedding; and the fixed RNA encoder is connected to the VAE decoder for inference (paper.md:43-51). This explicitly exploits unpaired proteomics rather than relying only on paired RNA/protein samples.

### Evaluation and findings

For glioma, the paper reports pan-cancer pretraining on 1,351 paired samples, cancer-specific fine-tuning on 210 paired samples, and VAE training on 1,422 protein profiles (paper.md:57-67). Predictions showed higher concordance with measured proteins than direct RNA baselines across training, validation, and unseen cohorts, with smaller gains in the independent cohort; pathway comparisons emphasized proliferation and oxidative-phosphorylation signals (paper.md:69-81). The manuscript also compares Lasso and random-forest ensemble baselines, evaluates a CITE-seq GBM setting, and applies predicted profiles to single-cell markers and bulk glioma subgroup/survival analyses (paper.md:77-152).

The five local main figures visually support the intended chain from architecture (Fig. 1) to alignment/prediction comparisons (Fig. 2), enrichment (Fig. 3), single-cell analysis (Fig. 4), and bulk clinical association (Fig. 5). Claims should be read as evidence for useful protein-centric analysis, not as proof that all individual protein abundances are accurately recovered.

### Reproducibility assessment

**Code-paper fidelity: medium.** The repository snapshot directly implements the paired contrastive encoders, protein VAE with MSE latent supervision, and embedding-to-protein decoder. Key qualifications are that the provided encoder ends in an unnormalized linear projection rather than the paper's stated final ReLU, and the VAE checkpoint is selected by validation reconstruction MSE rather than the full objective (`doc_code.md`).

The snapshot is not independently runnable end to end: requirements/environment files, datasets, pretrained checkpoints, tests, and a unified raw-RNA-to-protein command were **Not found** after searching the repository root and `src/*.py`. The generator accepts a precomputed RNA-embedding CSV. Supplementary files are PDFs only in this workspace, with no supplementary Markdown. These documented gaps limit reproduction but do not invalidate the source-grounded method analysis.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
