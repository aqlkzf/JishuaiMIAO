---
layout: default
permalink: /paper-atlas/sage-net-450837c0/
title: "SAGE-Net"
nav: false
description: "SAGE-Net（small and good enough CNN）不是单纯追求更大的序列模型，而是提供一套可扩展的个人基因组训练框架：它从参考序列预测群体平均表型，再从个人双倍体序列相对参考序列的表示差异预测个体偏移。论文最重要的结论带有明确边界——这种训练能改善“见过的基因、没见过的个体”的表达预测，却不能把表达调控规律推广到“没见过的基因”；在 DNA 甲基化任务上，随着训练区域增多，才观察到对未见区域的改善。"
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
      <span>Representation Models</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>SAGE-Net</h1>
    <p>A scalable approach to investigating sequence-to-function predictions from personal genomes</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2025.02.21.639494" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SAGE-Net：从个人基因组学习个体差异，真正学到了什么？

### 一句话结论

SAGE-Net（small and good enough CNN）不是单纯追求更大的序列模型，而是提供一套可扩展的个人基因组训练框架：它从参考序列预测群体平均表型，再从个人双倍体序列相对参考序列的表示差异预测个体偏移。论文最重要的结论带有明确边界——这种训练能改善“见过的基因、没见过的个体”的表达预测，却不能把表达调控规律推广到“没见过的基因”；在 DNA 甲基化任务上，随着训练区域增多，才观察到对未见区域的改善。

证据来源为本地 42 页 bioRxiv v4 PDF、主图 1–3、补图 S1–S22 及官方代码快照 `59fe0d120e9ea99bdeb98daf0796f448a105739b`。

### 1. 问题为什么难

传统 sequence-to-function 模型主要在一个参考基因组上学习“不同基因座之间”的功能差异。个人基因组任务却要求模型解释同一基因座上很小的等位基因差异如何造成个体间表达或甲基化差异。二者不是同一个泛化问题：模型可能很会区分高表达基因和低表达基因，却仍然无法预测同一基因在两个人之间谁更高。

SAGE-Net 因此把评价轴拆成两条：

- **跨个体、同一基因/区域**：测试模型是否抓住个人变异效应；
- **跨基因/区域**：测试模型是否学到可迁移的顺式调控语法。

论文把 ROSMAP 的个体拆为 689/85/85（训练/验证/测试），GTEx 205 人只用于外部测试；基因按染色体拆分，训练为 chr1–16，验证为 chr17、18、21、22，测试为 chr19、20。这个二维拆分使“未见个体”和“未见基因”不会被混为一谈。

### 2. 输入怎样构造

表达任务对每个“基因 $g$、个体 $i$”构造三条以 TSS 为中心的 40 kb one-hot 序列：参考序列 $S_g^{ref}$、母源单倍型 $S_{gi}^{mat}$ 和父源单倍型 $S_{gi}^{pat}$。`PersonalGenomeDataset` 用 `pysam` 从 VCF 按需插入 SNV/indel，而不是预先展开所有人的整套序列；负链基因可在 one-hot 后做反向互补。代码入口见 `SAGEnet/data.py:433-760`。

DNAm 任务沿用同一构造，但窗口缩短为以探针为中心的 10 kb。这里的“on-the-fly”主要解决存储和 I/O 扩展性，并不自动保证统计泛化。

### 3. r-SAGE-net：先学群体平均

r-SAGE-net 只接收参考序列，目标是训练人群的平均表达或平均 DNAm：

$$
\hat m_g=f_{ref}(S_g^{ref}).
$$

它由卷积、残差卷积与池化逐步压缩序列，再通过全连接层输出一个标量。论文的超参数搜索覆盖卷积通道数、核大小、池化方式、深度、dropout 和学习率；当前官方实现的类默认值是首层 900 通道、后续 256 通道、5 个卷积块、平均池化大小 10、学习率 $5\times10^{-4}$，见 `SAGEnet/models.py:167-341`。因此旧文档中“首层 256、默认最大池化”的说法不应作为当前代码事实。

r-SAGE-net 的作用有两个：一是提供跨基因的平均功能预测；二是给 p-SAGE-net 初始化共享卷积层。论文报告它比 Enformer 推断快约 70 倍，但这不等于它在精度上超过经组织特异性微调的 Enformer。

### 4. p-SAGE-net：把平均与个人偏移拆开

p-SAGE-net 让参考序列与两个个人单倍型经过同一个卷积骨干。代码先平均两条单倍型的卷积表示：

$$
h_{gi}^{personal}=\frac{h(S_{gi}^{mat})+h(S_{gi}^{pat})}{2}.
$$

当前默认的差异表示是

$$
h_{gi}^{diff}=h_{gi}^{personal}-h_g^{ref},
$$

然后两个输出头分别产生群体平均预测 $\hat m_g$ 与个人差异预测 $\hat d_{gi}$。代码还支持拼接参考/个人表示，或非对比地直接用个人表示，但默认是 subtract；直接实现见 `SAGEnet/models.py:421-655`。

这里所谓“contrastive”不是常见的 InfoNCE 或正负样本对比损失，而是显式比较个人表示与参考表示，并把目标拆成平均项和个人差异项。表达实验的个人目标通常是相对于训练个体分布的 z-score；非 z-score 是论文消融之一。

### 5. 损失如何把两种任务绑在一起

训练损失为两个均方误差的加权和：

$$
\mathcal L=\lambda_m\,\mathrm{MSE}(\hat m_g,m_g)
+\lambda_d\,\mathrm{MSE}(\hat d_{gi},d_{gi}).
$$

当前 `pSAGEnet` 类默认 $\lambda_m=1,\lambda_d=10$，训练脚本可以从命令行覆盖；实现见 `SAGEnet/models.py:657-670` 和 `script/train_model/train_model.py:185-260`。较大的差异权重迫使模型关注微小的个体变异信号。论文消融表明，不强调差异项或直接预测个人表达都会损害跨个体性能，但改变权重、窗口、初始化或加入 Transformer 都没有解决未见基因泛化。

训练使用 Adam、weight decay $10^{-5}$、循环学习率和梯度裁剪 1。r-SAGE-net 最多训练 100 epoch、早停 patience 10；最佳表达 p-SAGE-net 最多 25 epoch，其他消融常为 10 epoch，批量大小 6；DNAm p-SAGE-net 因规模与研究目标只训练一轮。

### 6. 怎样读三个主图

#### 图 1：正结果与关键负结果同时出现

图 1a 左到右展示参考序列预测平均表达、个人双单倍型与参考共同预测差异；图 1b 划分“见过/未见个体”和“见过/未见基因”。图 1c 显示，在 734 个训练基因上，p-SAGE-net 对 ROSMAP 和 GTEx 未见个体的逐基因相关性明显高于参考模型，接近 PrediXcan。图 1d 则显示 116 个未见基因的相关性仍围绕零：模型没有获得可跨基因迁移的表达调控语法。

#### 图 2：为何作者认为模型主要在识别预测性变异

随着个人训练 epoch 增加，训练基因逐基因性能上升，但验证基因逐基因性能不稳定，跨基因性能下降。过滤低频变异对结果影响很小，而移除更多常见变异后性能明显下降；高排名基因约 400 名训练个体后趋于平台；增加训练基因反而降低核心基因集性能。这组结果更符合“记住训练基因上的常见预测性变异”，而非“形成统一调控语法”。

#### 图 3：DNAm 给出不同答案

图 3a 显示个人训练改善见过的 CpG 区域；图 3b 显示当训练区域增加到 100k 时，对 339 个未见区域也优于 r-SAGE-net（单侧 Wilcoxon $p=4.96\times10^{-4}$）。图 3c–d 的全局归因将 seqlet 聚类后与 HOCOMOCO v12 匹配，p-SAGE-net 富集簇包括与 DNAm 生物学有关的 CTCF、ZFX 等模式。这个结果支持“DNAm 的局部序列决定因素可能更容易跨区域学习”，但不能直接外推到表达。

### 7. 归因分析到底说明什么

论文对个人模型做 ISM 时同时突变两个单倍型，并记录 difference 输出变化；梯度和 ISM 均按位置零中心化。全局分析再用 `recursive_seqlets` 找片段、聚类并用 TOMTOM/HOCOMOCO 匹配。代码对应 `SAGEnet/attributions.py:23-208` 及 `script/attributions/analyze_attribs.py`。

GSTM3 个例提示个人训练可能捕捉到 HLF 样的抑制 motif，且总体 seqlet 相对参考模型更远离 TSS。不过，个例或 motif 匹配不能证明模型学到了可泛化的因果语法；主图 1d 的未见基因测试仍是更严格的边界。

### 8. 使用时必须保留的边界

- **个人差异预测不等于跨基因泛化。** 见过基因上的高相关性可能来自基因特异的常见变异。
- **平均项与差异项的尺度不同。** 当前表达差异目标通常是 z-score，不能直接把 $\hat m+\hat d$ 当作原始表达单位相加。
- **归因不是因果验证。** seqlet、motif 匹配和 ISM 反映模型敏感性，需要实验验证。
- **数据访问是复现瓶颈。** ROSMAP/GTEx WGS 与表型需要受控访问，完整训练未在本工作区重跑。
- **版本边界。** 本地 PDF 是 2026-01-06 发布的 bioRxiv v4，尚未同行评议；本地源码固定为上述提交。

### 9. 从数据到结论的最短路径

1. 用参考 FASTA、phased VCF 和区域坐标按需构造三条序列。
2. 先训练 r-SAGE-net 学群体平均，并可用其卷积权重初始化个人模型。
3. p-SAGE-net 共享编码参考与双单倍型，平均两个单倍型表示，再与参考表示相减。
4. 两个头分别预测平均与个体差异，以加权 MSE 联合训练。
5. 同时报告未见个体/见过区域和未见个体/未见区域，防止把记忆误判为语法。
6. 用 ISM/梯度、seqlet 聚类和 motif 匹配解释模型关注序列，但把这些结果限定为模型证据。

SAGE-Net 的价值因此不只是一个小 CNN，而是一套把“可扩展个人序列训练”和“严格二维泛化诊断”放在一起的实验框架；其最诚实、也最有信息量的产出，正是表达任务上的负泛化结果与 DNAm 任务上的相对正结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SAGE-Net: A Scalable Approach to Investigating Sequence-to-Function Predictions from Personal Genomes

**Journal**: bioRxiv (preprint), 2025
**DOI**: 10.1101/2025.02.21.639494
**Authors**: Anna E. Spiro, Xinming Tu, Yilun Sheng, Alexander Sasse, Rezwan Hosseini, Maria Chikina, Sara Mostafavi
**Code**: https://github.com/mostafavilabuw/SAGEnet

---

### Motivation & Novelty

Sequence-to-function (S2F) deep learning models promise to predict how genomic DNA maps to cell-type-specific regulatory functions. However, current S2F models trained on a single reference genome (reference-S2F) struggle to accurately predict inter-individual variation in gene expression from personal genomes. This limitation severely constrains their utility for personalized genomics applications.

**Key limitations of existing approaches:**
- **Computational scalability**: State-of-the-art models like Borzoi (>100M parameters) require weeks of GPU time for fine-tuning on personal genomes
- **Poor generalization**: Models trained on reference genomes fail to predict direction of genetic effects across individuals
- **Limited investigation scope**: High computational costs restrict comprehensive exploration of model architectures and training regimes

**Novel contributions of SAGE-Net:**
1. **Scalable CNN architecture**: Compact model achieving 70x faster inference than Enformer while maintaining competitive performance
2. **On-the-fly personal dataset**: Efficient conversion of personal genomes (from VCF files) to one-hot-encoded matrices with configurable MAF thresholds
3. **Contrastive learning framework**: Decouples "mean" and "personal" components of gene expression to capture cis-regulatory grammar underlying inter-individual variation
4. **Comprehensive ablation system**: Systematic exploration of training regimes across multiple datasets (ROSMAP, GTEx, Geuvadis)

---

### Method Overview

#### Core Architecture: p-SAGE-net (personal-SAGE-net)

The model takes three 40 kb one-hot-encoded sequences centered at gene transcription start sites (TSS):
- Reference sequence (hg38)
- Two personal haplotype sequences (from phased WGS)

**Two-head prediction:**
1. **Mean expression head**: Predicts average expression across individuals from reference sequence
2. **Difference head**: Predicts individual z-score deviation from mean using contrast between reference and personal sequences

**Loss function:**
$$\mathcal{L} = w_{\text{mean}} \cdot \text{MSE}(\hat{y}_{\text{mean}}, y_{\text{mean}}) + w_{\text{diff}} \cdot \text{MSE}(\hat{y}_{\text{diff}}, y - y_{\text{mean}})$$

Where $w_{\text{diff}} = 10$ (default) emphasizes learning individual differences.

#### Key Technical Components

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| Convolutional backbone | 5 conv blocks + dilated conv blocks | Capture cis-regulatory patterns |
| Pooling | Max pooling (size 10) | Reduce sequence dimensionality |
| Contrastive split | Separate FC heads | Isolate mean vs. personal variation |
| Input window | 40 kb (gene expression), 10 kb (DNAm) | Balance context and computation |

#### Training Strategy

- **Initialization**: From r-SAGE-net (reference-only pre-training)
- **Data**: ROSMAP cortex RNA-seq (n=689 train, n=85 val, n=85 test)
- **External validation**: GTEx cortex (n=205 individuals)
- **Optimization**: Adam with learning rate scheduling, early stopping (patience=10)

---

### Evaluation

#### Datasets

| Dataset | Tissue | Individuals | Modality |
|---------|--------|-------------|----------|
| ROSMAP | Dorsolateral prefrontal cortex | 859 | WGS + RNA-seq |
| GTEx V8 | Cortex | 205 | WGS + RNA-seq |
| Geuvadis | Lymphoblastoid cell lines | 462 | WGS + RNA-seq |
| ROSMAP DNAm | Dorsolateral prefrontal cortex | 634 | WGS + 450K array |

#### Key Results

**Gene Expression (seen genes, unseen individuals):**
- p-SAGE-net achieves **comparable performance to PrediXcan** on training genes (Pearson R ~0.3-0.4 for top heritable genes)
- Performance matches fine-tuned Borzoi/Enformer at ~70x lower computational cost
- Pre-training from r-SAGE-net provides modest improvement over random initialization

**Generalization to unseen genes:**
- **Critical limitation**: p-SAGE-net does NOT generalize to unseen genes (test genes show ~0 correlation)
- Increasing training epochs progressively degrades cross-gene prediction (model "forgets" generalizable grammar)
- Loss function design matters: contrastive approach outperforms single-output models

**DNA Methylation (promising direction):**
- Personal genome training enables **improved generalization to unseen genomic regions** (p=4.96e-04)
- Models trained on 100k+ regions show better unseen-region performance
- Attribution analysis reveals known biology (CTCF, ZFX motifs)

#### Model Interpretability

- **In-silico mutagenesis (ISM)**: Identifies repressive HLF motif disrupted by causal variant at GSTM3 locus
- **Seqlet analysis**: p-SAGE-net seqlets distributed farther from TSS than r-SAGE-net, suggesting improved distal variant utilization
- **Global attribution**: Clustering reveals model-learned motifs matching HOCOMOCO database

---

### Reproducibility

**Rating: 4/5** (Excellent for preprint)

| Aspect | Status | Notes |
|--------|--------|-------|
| Code availability | Available | https://github.com/mostafavilabuw/SAGEnet |
| Data access | Controlled | ROSMAP via Synapse (access required), GTEx via dbGaP |
| Documentation | Good | Clear README, hyperparameter specifications |
| Reproducible claims | Partial | Main results reproducible; some supplementary analyses lack full details |
| Environment | Manageable | PyTorch, standard dependencies |

**Reproducibility strengths:**
- Complete hyperparameter grid search documented
- Clear chromosome splits for train/val/test
- Multiple gene sets analyzed (top 1000, 4000-5000)
- Ablation experiments systematically reported

**Reproducibility limitations:**
- Pre-trained r-SAGE-net weights not explicitly provided (may need re-training)
- Exact random seeds not specified
- Some figure analyses (e.g., specific ISM visualizations) may require careful reproduction

---

### Key Findings

#### What Works

1. **Personal genome training improves seen-gene predictions**: Models learn individual-specific patterns
2. **Compact CNNs are sufficient**: No need for 100M+ parameter models for this task
3. **DNA methylation shows promise**: Epigenomic traits may be more amenable to S2F modeling than gene expression
4. **Attribution methods reveal biology**: ISM and seqlet analysis uncover meaningful regulatory patterns

#### What Doesn't Work

1. **No generalization to unseen genes**: Models memorize training genes rather than learning generalizable grammar
2. **More training genes = worse performance on core genes**: Adding genes dilutes rather than improves predictions
3. **Low-frequency variants contribute little**: MAF filtering shows minimal impact until excluding common variants
4. **Cross-gene performance degrades with training**: Models "forget" reference-learned grammar

---

### Implications

#### For Computational Genomics

- Current S2F models face a fundamental trade-off: optimizing for seen-locus predictions vs. generalizable regulatory grammar
- DNA methylation may be a more tractable target for S2F modeling than gene expression
- Pre-training on random DNA sequences (not constrained by natural selection) may help uncover broader regulatory principles

#### For Personalized Medicine

- Direct prediction from personal genomes to gene expression remains challenging
- Linear methods (PrediXcan) still competitive for TWAS accuracy
- Deep learning strength lies in evaluating arbitrary sequences (including rare/de novo variants)

#### Future Directions

1. Multi-modal integration (RNA-seq + DNAm + ATAC-seq)
2. Per-gene adaptive training based on heritability
3. Pre-training on synthetic DNA sequences
4. Larger input windows and more fine-grained predictions

---

### Related Work

| Method | Journal, Year | Relationship |
|--------|---------------|--------------|
| Enformer | Nature Methods, 2021 | Large-scale S2F baseline (196 kb input, 5313 tracks) |
| Borzoi | Nature Genetics, 2025 | State-of-the-art S2F with RNA-seq coverage prediction |
| PrediXcan | Nature Genetics, 2015 | Linear baseline for gene expression prediction |
| Fine-tuning Enformer (Rastogi et al.) | bioRxiv, 2024 | Concurrent work on personal genome fine-tuning |
| Deep-learning personal genomes (Drusinsky et al.) | bioRxiv, 2024 | Concurrent work with similar findings |

---

### Citation

```bibtex
@article{spiro2025sagenet,
  title={A scalable approach to investigating sequence-to-function predictions from personal genomes},
  author={Spiro, Anna E. and Tu, Xinming and Sheng, Yilun and Sasse, Alexander and Hosseini, Rezwan and Chikina, Maria and Mostafavi, Sara},
  journal={bioRxiv},
  pages={2025.02.21.639494},
  year={2025},
  doi={10.1101/2025.02.21.639494}
}
```

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
