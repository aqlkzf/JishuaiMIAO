---
layout: default
permalink: /paper-atlas/teddy-c59c78bf/
title: "TEDDY"
nav: false
wide: true
description: "单细胞 RNA 测序基础模型通常把一个细胞视为“句子”，把该细胞表达的 基因视为“词”。这类模型可以从大量无标签细胞中学习通用表示，但已有 研究发现：预训练模型在下游任务中不一定稳定优于专用模型，零样本嵌入 也未必比低成本方法更好。论文列举的代表包括 Geneformer（Nature, 2023）、scGPT（Nature Methods, 2024）和 Nicheformer（bioRxiv, 2024）；"
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
    <h1>TEDDY</h1>
    <p>TEDDY: A Family of Foundation Models for Understanding Single Cell Biology</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TEDDY 方法详解：用粗粒度生物学监督训练单细胞基础模型

### 1. 这篇论文要解决什么问题？

单细胞 RNA 测序基础模型通常把一个细胞视为“句子”，把该细胞表达的
基因视为“词”。这类模型可以从大量无标签细胞中学习通用表示，但已有
研究发现：预训练模型在下游任务中不一定稳定优于专用模型，零样本嵌入
也未必比低成本方法更好。论文列举的代表包括 Geneformer（*Nature*,
2023）、scGPT（*Nature Methods*, 2024）和 Nicheformer（bioRxiv,
2024）；它们主要区别在表达值编码、训练规模和自监督任务（论文
第 2 节，lines 35-53）。

TEDDY 的核心问题是：**扩大预训练数据和参数规模，并把 CELLxGENE 的
生物学注释从“输入上下文”改成显式监督目标，能否得到更有疾病信息的
细胞表示？**

### 2. 方法的输入与输出

输入是单细胞的非零基因表达谱，以及四类元数据：疾病、组织、细胞类型
和性别。原始 CELLxGENE 数据含 160M 个细胞；论文去除基因计数少于
225、线粒体转录本比例高于 10% 的低质量细胞，以及 10x Chromium v1
数据，并排除下游测试数据，得到 116M 个预训练细胞（lines 62-69）。

输出是一个 Transformer 表示模型，可用于三类下游方式：

1. 加分类头并微调；
2. 冻结模型，用细胞嵌入训练线性或传统机器学习分类器；
3. 直接使用零样本嵌入进行聚类或基因扰动分析。

论文在零样本疾病分类实验中明确说明，细胞嵌入由 Teddy-G 400M 的
输出基因嵌入取平均得到（lines 239-245）。但微调时的池化方式、分类头
结构和检查点格式没有说明，属于 **Missing**。

### 3. 从原始表达矩阵到模型序列

预处理分为四步：

1. 每个细胞缩放到 10,000 总表达计数。
2. 对每个基因计算训练集中非零表达的中位数，再用该中位数缩放，使每个
   基因的非零表达中位数为 1（Appendix B.3, lines 394-400）。
3. 按归一化表达量排序，只保留最长 2,048 个基因。
4. 在序列前加入 `<disease>`、`<tissue_type>`、`<cell_type>`、`<sex>`
   四个特殊 token。

CELLxGENE 的 1,399 个本体标签被合并为 43 个粗粒度类别。这里的关键
设计不是把标签仅作为额外输入，而是要求模型**从基因表达预测这些
标签**。预训练时还对分类提示采样以平衡类别；疾病提示中正常与患病各占
50%（lines 71-90, 385-391）。

```text
单细胞非零表达谱
       |
质量控制 + 10,000 counts 缩放 + 基因中位数归一化
       |
按表达量排序，截断到 2,048 个基因
       |
   +-----------------------+
   |                       |
Teddy-G                 Teddy-X
仅用排序后的基因 ID      基因 ID + [-1,1] 连续秩
预测被遮蔽的基因 ID      预测被遮蔽的连续秩
   |                       |
   +-----------+-----------+
               |
疾病 / 组织 / 细胞类型 / 性别四个分类损失
               |
        Transformer 表示
               |
微调分类 / 线性探测 / 零样本嵌入
```

### 4. Teddy-G 与 Teddy-X 的差别

#### Teddy-G：预测“缺了哪个基因”

令 $V$ 为词表大小，${\bm t}_n=\{t_{nj}\}_{j=1}^{J_n}$ 为细胞
${\bm c}_n$ 中按表达量排序的基因 ID。模型均匀随机遮蔽 15% 的位置，
并用 $V$ 类分类分布预测被遮蔽的基因：

$$
\ell_{\mathrm{MLM-G}}(\theta)=
\mathbb{E}_&#123;&#123;\mathbf c}_n\sim{\cal D}}
\mathbb{E}_{m\sim{\cal M}}
[-\log\operatorname{Cat}(t_{nm}\mid g_\theta({\mathbf c}_{n\backslash m}))].
$$

因此，Teddy-G 保存的是表达量诱导的**顺序**，预测目标是基因身份，而
不是数值表达量。Figure 1 的图像直接显示：输入基因先按表达排序，随后
某个位置的 gene ID 被遮蔽。

#### Teddy-X：预测“该基因的表达秩是多少”

对细胞内每个基因，论文把表达秩线性缩放到 $[-1,1]$：最高表达映射为
1，最小非零表达映射为 -1。Teddy-X 保留基因 ID，并用单位方差高斯
似然预测被遮蔽的连续秩：

$$
\ell_{\mathrm{MLM-X}}(\theta)=
\mathbb{E}_&#123;&#123;\mathbf c}_n\sim{\cal D}}
\mathbb{E}_{m\sim{\cal M}}
[-\log {\cal N}(r_{nm}\mid f_\theta({\mathbf c}_n),1)].
$$

Figure 1 的 Teddy-X 分支显示，gene ID 仍在，而 “Rank ?” 是预测目标。
论文没有说明被遮蔽位置究竟使用专门 mask token、置零还是其他扰动，
这是 **Missing（检索范围：Section 3.3 与 Figure 1）**。

### 5. 生物学监督如何进入总目标

四个特殊 token 对应四个分类头，分别预测疾病、细胞类型、组织类型和
性别。以 Teddy-G 为例，分类损失是四个交叉熵之和：

$$
\ell_{\mathrm{CLS-G}}=
\ell_{\mathrm{disease}}+\ell_{\mathrm{cell}}+
\ell_{\mathrm{tissue}}+\ell_{\mathrm{sex}}.
$$

总目标为

$$
\ell_{\mathrm{pre-G}}(\theta)=
\ell_{\mathrm{MLM-G}}(\theta)+\ell_{\mathrm{CLS-G}}(\theta).\tag{1}
$$

Teddy-X 用对应的 $\ell_{\mathrm{MLM-X}}$ 和 $\ell_{\mathrm{CLS-X}}$ 替换。
论文称，改变自监督项和分类项的相对权重没有明显影响，因此最终直接
相加；但没有给出完整权重扫描或四个分类头的独立权重。

可以把这一设计理解为两个互补信号：遮蔽任务要求模型学习基因共表达
上下文，粗粒度分类要求细胞表示对较高层次生物属性敏感。这个解释是对
目标函数的**分析性解释**，不是代码或因果机制验证。

### 6. 训练规模与关键超参数

所有模型在 116M 细胞上训练一轮。词表含 48,308 个 token，覆盖人和
小鼠蛋白编码基因、micro-RNA、特殊 token 和注释标签。训练使用 batch
size 256、AdamW、10,000 step 线性 warmup、最大学习率 $10^{-4}$ 后
线性衰减到 0，以及 0.1 weight decay（lines 135-138）。

模型从约 10M 扩展到 400M 参数：10M/30M/70M/160M/400M 分别采用
3/6/12/12/24 层和 128/256/512/768/1024 维嵌入（Appendix B.1）。
Figure 2 显示数据量和参数量增加时验证损失下降，但 160M 到 400M 的
收益已减弱，不能简单当作无限延伸的幂律。

### 7. 评估设计与主要结果

#### Held-out donors

测试集的 82 个 donor 在预训练中完全排除，任务是 14 类疾病/正常状态
分类；训练与验证使用另外 524 个 donor，并确保 donor 不重叠。因为类别
不平衡，报告 accuracy 和 weighted F1。Teddy-G 400M 达到
0.72 accuracy / 0.68 F1，高于 Nicheformer 的 0.64/0.56 和 scGPT 的
0.64/0.54（Table 2）。Figure 3 还显示 Teddy-G 整体优于 Teddy-X，
本体监督对两个 70M 变体都有帮助；不过 400M 的 G 模型 F1 并未高于
160M，说明“随规模提升”不是严格单调。

#### Held-out diseases

五个疾病数据集连同相同疾病标签的数据都从预训练中移除。每个任务做
健康/患病二分类，采用 donor 不重叠的三折交叉验证并报告 accuracy。
Teddy-G 400M 对 Geneformer 12L 全部五项占优，但与训练数据量相近的
Nicheformer 基本处于误差范围内；因此这里的改进是有限、任务相关的，
不是全面领先（Table A3、Figure 4）。

#### 表示质量与扰动分析

- 用零样本 Teddy-G 400M 嵌入替代手工表达特征后，LightGBM、Linear
  SVC、逻辑回归和 XGBoost 在五个疾病任务上均提高（Table A2、Figure
  A2）。
- 在 536,207 个肠道细胞上，Teddy-G 400M 的 NMI、ARI、ASW 和 AvgBIO
  均高于相近规模的 Cell2Sentence 410M（Table A6）。
- GATA4 零样本敲除实验把直接靶基因、间接靶基因和 housekeeping 基因
  的嵌入变化排成符合预期的顺序；但这是特定转录因子、236 个细胞上的
 计算分析，不能单独证明模型普遍学到了因果调控网络（lines 257-280）。

### 8. 复现边界与已知缺口

在论文 Markdown、arXiv HTML/source bundle 与 GitHub 元数据搜索中均未
找到论文关联代码库，因此 `doc_code.md` 被跳过，所有实现行为均为
**Not found / 未验证**。

论文未给出完整 Transformer 注意力配置、mask 实现、微调池化和分类头、
训练精度与硬件、梯度累积、确切优化 step 数、检查点选择以及可运行命令。
此外，held-out-disease 的标签来自 donor 状态而非单细胞真实状态，可能
混入批次和采集伪影。方法思想与公式可以重建，但忠实复现实验仍需要
作者代码、数据处理脚本或更多实现细节。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TEDDY: quick summary

### Problem

Single-cell foundation models promise reusable representations for disease
biology, but prior studies found that they often improve only modestly over
task-specific classifiers and may not generalize across donors or unseen
diseases (paper lines 20-32, 35-53). TEDDY asks whether scaling the corpus and
adding explicit biological supervision can improve these representations.

### Proposed method

TEDDY is a transformer family trained on 116M quality-controlled CELLxGENE
cells. Teddy-G sorts expressed genes by normalized expression and predicts
15%-masked gene identities; Teddy-X uses the same rank ordering but predicts
masked ranks scaled to [-1, 1]. Both variants prepend coarse disease, tissue,
cell-type, and sex tokens and add four ontology-classification losses to the
masked objective. Models span roughly 10M–400M parameters, with 70M, 160M, and
400M variants used most heavily in evaluation (lines 56-90, 93-138; Appendix
B.1).

### Evaluation and results

The authors build two donor-disjoint benchmarks: five balanced binary
held-out-disease tasks and a 14-way held-out-donor task with 82 donors excluded
from pre-training (lines 149-170; Appendix C). On held-out donors, Teddy-G 400M
fine-tuning reaches 0.72 accuracy and 0.68 weighted F1, versus 0.64/0.56 for
Nicheformer, 0.64/0.54 for scGPT, and 0.39/0.22 for Geneformer (Table 2,
lines 182-188). Figure 3 and Table A5 show generally higher F1 with scale and
clear gains from ontology supervision, although the 400M G point is not strictly
higher than 160M. On held-out diseases, Teddy-G 400M is strongest on CKD and
competitive overall, but improvements over Nicheformer are modest and noisy
(Table A3, lines 214-222, 473-482).

Frozen Teddy-G embeddings are useful independently of fine-tuning: replacing
handcrafted expression features improves logistic regression, SVM, XGBoost, and
LightGBM across the five disease datasets (Table 3, Figure A2, lines 225-245).
On 536,207 gut cells, zero-shot Teddy-G 400M embeddings outperform
Cell2Sentence 410M on NMI, ARI, ASW, and AvgBIO at coarse and intermediate
cell-type resolutions (Table A6, lines 248-255, 508-525). A zero-shot GATA4
knockout assay further reports biology-consistent separation of housekeeping,
direct-target, and indirect-target genes using paired Wilcoxon tests (Table 4,
lines 257-280).

### Reproducibility and limitations

The acquired source is arXiv HTML (`paper.md`) with seven local figure images;
no paper-linked GitHub repository, checkpoint, supplementary markdown, or
training scripts were found. The paper specifies normalization, vocabulary,
context length, masking rate, optimizer, learning-rate schedule, weight decay,
model sizes, benchmark splits, and fine-tuning learning-rate sweep. It does not
specify the mask-token implementation, transformer attention configuration,
embedding pooling/head details, training hardware/precision, exact optimizer
step count, checkpoint selection, or a runnable command. These are **Missing**
for reproduction (searched scope: Sections 3–5 and Appendices B-D). The authors
also acknowledge that disease labels are donor-derived rather than cell-level,
so experimental and collection artifacts may limit held-out-disease conclusions
(Appendix A, lines 343-352).

**Reproducibility rating: 2/5.** The method and evaluation protocol are fairly
well described, but absent code/checkpoints and unspecified implementation
choices prevent a faithful rerun.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
