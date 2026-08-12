---
layout: default
permalink: /paper-atlas/acrnet-dad345ef/
title: "AcrNET"
nav: false
description: "AcrNET 用深度学习预测一个蛋白序列是否是 anti-CRISPR protein。它不是只看原始序列，而是把序列 one-hot、RaptorX 结构/可及性特征、POSSUM/PSSM 进化特征和 ESM-1b Transformer 特征融合起来，输出 Acr / Non-Acr 置信度。论文还声称可以进一步预测 Acr 类型，但当前公开代码只验证到二分类模型。"
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
      <span>Bioinformatics · 2023</span>
    </div>
    <h1>AcrNET</h1>
    <p>AcrNET: predicting anti-CRISPR with deep learning</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1093/bioinformatics/btad259" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## AcrNET 方法中文解读

### 一句话概览

AcrNET 用深度学习预测一个蛋白序列是否是 anti-CRISPR protein。它不是只看原始序列，而是把序列 one-hot、RaptorX 结构/可及性特征、POSSUM/PSSM 进化特征和 ESM-1b Transformer 特征融合起来，输出 Acr / Non-Acr 置信度。论文还声称可以进一步预测 Acr 类型，但当前公开代码只验证到二分类模型。

### 1. 生物学问题与建模目标

Anti-CRISPR 蛋白可以抑制细菌 CRISPR-Cas 免疫系统，对基因编辑安全、噬菌体治疗和 Acr 机制研究都有意义。难点是 Acr 蛋白变化快、序列差异大，传统实验或基于基因组上下文的发现方法成本高，也不适合大规模筛选。

AcrNET 把问题建模成蛋白功能分类：输入候选蛋白序列及其派生特征，输出它是否可能是 Acr。这个输出适合作为实验优先级排序，不等于证明该蛋白一定能抑制某个 CRISPR-Cas 系统。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| 蛋白序列 | `seq` | 待判断的候选蛋白 | `doc_code.md`, `AcrNET_code/train_five_fold.py:34-38` |
| 二级结构 | `ss3`, `ss8` | 3 类和 8 类结构状态 | `AcrNET_code/train_five_fold.py:40-63` |
| 溶剂可及性 | `acc` | 残基暴露程度 | `AcrNET_code/train_five_fold.py:40-63` |
| 进化特征 | PSSM features | 同源保守性和序列顺序信息 | `doc_method.md` |
| Transformer 特征 | ESM-1b layer 33 mean representation | 大规模蛋白语言模型表示 | `AcrNET_code/train_five_fold.py:180-187` |
| 预测输出 | Acr / Non-Acr | 二分类 log probability | `AcrNET_code/model.py:27-33` |

### 3. 方法主流程

1. 从 anti-CRISPRdb 收集 Acr 正样本，从 PaCRISPR 收集 non-Acr 负样本，并用 CD-HIT 去冗余。
2. 对每个蛋白计算外部特征：RaptorX 结构和可及性、POSSUM/PSSM 进化特征、ESM-1b Transformer 表示。
3. 将序列、SS3、SS8、accessibility 拼接后送入 CNN，学习局部序列/结构模式。
4. 将 PSSM 和 ESM 特征拼接后送入全连接层，压缩成全局特征。
5. 把 CNN 特征和全局特征融合，用 FCN 输出 Acr / Non-Acr 置信度。
6. 论文进一步做 Acr 类型预测、motif 分析、AlphaFold 结构预测和 HDOCK docking；这些更适合作为机制假设生成。

### 4. 数学目标与直觉

论文核心不是复杂公式，而是特征融合分类。PSSM 被描述为 $L \times 20$ 矩阵，$L$ 是蛋白长度，20 对应氨基酸类型；分数越高表示该位置越保守。

CNN 输入可写成：

$$
X_{\mathrm{cnn}} = \mathrm{concat}(X_{\mathrm{seq}}, X_{\mathrm{ss3}}, X_{\mathrm{ss8}}, X_{\mathrm{acc}})
$$

代码中这个拼接宽度是 34，对应 20+3+8+3。`model.py:17-22` 使用 `(5, 34)` 卷积核和 max pooling 把变长局部特征压成固定表示。PSSM+ESM 特征经过 `dnn_fc1/dnn_fc2` 压缩后，与 CNN 表示拼接，最后经过 `log_softmax` 输出二分类概率。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| CNN + FCN 二分类模型 | `AcrNET_code/model.py:5-33` | 拼接结构/序列特征，融合 PSSM+ESM，输出 2 类 | ✓ Exact |
| 五折训练 | `AcrNET_code/train_five_fold.py:192-223` | 单次 5-fold CV，输出平均指标 | ✓ Exact |
| 交叉熵 + Adam | `AcrNET_code/model.py:31`, `train_five_fold.py:205-211` | `log_softmax` + `NLLLoss`，Adam lr=0.001 | ~ Partial |
| 外部特征生成 | README 和训练脚本 | 代码读取预计算文件，不运行 RaptorX/POSSUM/ESM | ~ Partial |
| 五类 Acr 分类 | 未找到 | `model.py` 只有 2 类输出 | ✗ Not found |
| cross-dataset、motif、AlphaFold、docking | 未找到 | 公开仓库没有对应脚本 | ✗ Not found |

### 6. 结果如何解读

论文报告 AcrNET 在五折验证中 F1=0.9418、MCC=0.8883，优于 AcRanker、PaCRISPR 和 DeepAcr。cross-dataset separation 1 中，AcrNET 的 F1=0.7505、MCC=0.5924，说明它在低相似度测试上仍有优势。Figure 3 的 ablation 显示 Transformer 特征很关键，但完整特征融合最好。

Figure 4-6 展示 motif、AlphaFold 和 docking 例子，说明模型可能捕捉到保守 motif，并可用结构/对接帮助后续实验设计。但这些是计算证据，不是湿实验验证。

### 7. 局限性与未验证部分

- 公开代码没有实现论文声称的五类 Acr type classifier。
- 公开代码没有十个随机种子平均、cross-dataset、40/70% similarity 实验脚本。
- RaptorX、POSSUM、ESM-1b 特征需要外部预计算，本地代码不是 raw-sequence-only。
- motif mutation、AlphaFold、HDOCK docking 没有在仓库中找到实现。
- AcrNET 输出应作为候选筛选和假设生成，不能直接替代生物实验验证。

### 8. 快速阅读路线

1. 读 `summary.md`：快速了解论文动机、方法、结果和复现评级。
2. 读 `doc_method.md`：理解从输入特征到模型输出的完整流程。
3. 读 `doc_code.md`：看论文 claim 哪些被代码验证、哪些缺失。
4. 读 `figure_analysis.md`：理解六张主图分别支持什么结论。
5. 读 `claude_notes.md`：查看最完整的证据 ledger、行号和缺口。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## AcrNET Summary

### Motivation And Novelty

AcrNET addresses anti-CRISPR protein prediction. Anti-CRISPRs inhibit bacterial CRISPR-Cas immunity and are useful for gene-editing safety, gene-drive control, and phage therapy, but discovery is difficult because Acr proteins are diverse, fast-evolving, and often lack simple homology or genomic-context signals.

The paper's novelty is a deep feature-fusion model that combines local sequence/structure/accessibility features, PSSM-derived evolutionary features, and ESM-1b protein language-model features. The key idea is to use large-scale pretrained protein representations to reduce the small-labeled-dataset problem in Acr prediction. The paper also claims the first computational method for detailed Acr class prediction.

### Method Overview

AcrNET takes protein sequences and derived features as input. Sequence, 3-state secondary structure, 8-state secondary structure, and solvent accessibility are one-hot encoded and processed by a CNN. PSSM/evolutionary features and ESM-1b Transformer features are compressed by dense layers. The two branches are fused by fully connected layers to output Acr versus non-Acr confidence.

The paper then uses predictions for downstream tasks: Acr class prediction, MEME motif analysis, AlphaFold structure prediction, and HDOCK docking. These downstream analyses help interpret and prioritize candidates, but they are not part of the public AcrNET model implementation.

### Evaluation

The paper evaluates AcrNET using five-fold cross-validation, cross-dataset tests, lower sequence-similarity tests, feature ablations, Acr class prediction experiments, motif mutation, and docking examples. The main same-dataset baselines are PaCRISPR (Nucleic Acids Research, 2020), AcRanker from *Machine learning predicts new anti-CRISPR proteins* (Nucleic Acids Research, 2020), and DeepAcr (Molecular Cell, 2022). In the main five-fold table, AcrNET reports F1 score 0.9418 and MCC 0.8883, outperforming those baselines. In cross-dataset separation 1, it reports F1 score 0.7505 and MCC 0.5924, with stronger precision and F1 than the compared baselines.

Figure 3 supports the main empirical story: Transformer features are strong, full feature fusion performs best overall, and AcrNET has a higher ROC curve than AcRanker and PaCRISPR. Figures 4-6 support computational interpretation through motifs, AlphaFold structures, and docking.

### Reproducibility

**Rating: 3/5.**

The central two-class AcrNET architecture and a five-fold training script are public at `https://github.com/banma12956/AcrNET`, and the workspace includes a cloned snapshot at `AcrNET_code/`. The code directly verifies the CNN/FCN feature-fusion model, demo inference with a pretrained checkpoint, and five-fold binary training.

Reproducibility is not turnkey. Feature extraction with RaptorX, POSSUM, and ESM-1b is external. The public code does not include the paper's ten-random-seed loop, cross-dataset/similarity experiment scripts, five-class Acr type classifier, motif mutation pipeline, AlphaFold workflow, or HDOCK docking scripts. Therefore the core classifier is reproducible in principle, but the full results and interpretation pipeline are only partially code-supported.

### Key Caveats

- AcrNET predictions are computational priors for experimental validation, not direct proof of anti-CRISPR activity.
- The class-prediction claim is important but not implemented in the public code snapshot.
- The strongest generalization claims rely on evaluation scripts and splits absent from the repository.
- The method depends on precomputed structural, evolutionary, and ESM features; raw sequence alone is not enough for the local code path.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
