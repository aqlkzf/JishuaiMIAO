---
layout: default
permalink: /paper-atlas/scmeformer-bf8728a0/
title: "scMeFormer"
nav: false
wide: true
description: "对一个待预测的 CpG 位点，scMeFormer 同时读取其上下约 2 kb DNA 序列，以及前后邻近 CpG 在多个细胞簇中的甲基化模式；两条 CNN–Transformer 分支分别提取序列和群体甲基化上下文，融合后一次输出该 CpG 在所有细胞中的甲基化预测。只有真实测到的“CpG—细胞”标签参与训练损失，未测位置不会被错误当成未甲基化。"
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
      <span>Cell Genomics · 2025</span>
    </div>
    <h1>scMeFormer</h1>
    <p>Deep learning imputes DNA methylation states in single cells and enhances the detection of epigenetic alterations in schizophrenia</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.xgen.2025.100774" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scMeFormer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/LieberInstitute/scMeformer" target="_blank" rel="noopener noreferrer" aria-label="Open code for scMeFormer">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scMeFormer 方法解释：从稀疏单细胞甲基化到可分析的致密甲基化图谱

### 一句话理解

对一个待预测的 CpG 位点，scMeFormer 同时读取其上下约 2 kb DNA 序列，以及前后邻近 CpG 在多个细胞簇中的甲基化模式；两条 CNN–Transformer 分支分别提取序列和群体甲基化上下文，融合后一次输出该 CpG 在所有细胞中的甲基化预测。只有真实测到的“CpG—细胞”标签参与训练损失，未测位置不会被错误当成未甲基化。

### 1. 为什么单细胞 DNA 甲基化需要插补

单细胞/单核甲基化测序在每个细胞中只能覆盖一小部分 CpG。同一 CpG 可能在少数细胞有读段、其余细胞全是空缺，导致聚类和差异甲基化区域（DMR）统计功效不足。scMeFormer 利用两类互补规律：

- DNA 序列决定局部 motif 和远距离序列组合，对 CpG 甲基化倾向有影响；
- 相邻 CpG 具有空间相关性，相似细胞群也共享甲基化结构。

模型输出的是目标 CpG 对每个细胞的连续预测，后续可阈值化为甲基化/未甲基化状态，并组成更致密的“CpG × 细胞”矩阵。

### 2. 监督标签怎样构造

代码把读段证据明确的观测转成二元标签：所有覆盖读段均甲基化的细胞记为 1，均未甲基化记为 0；混合证据不作为确定标签。对目标 CpG $p$ 和细胞 $i$，记标签为 $y_{pi}\in\{0,1\}$，观测掩码为 $m_{pi}$。

训练、验证、测试按染色体隔离：论文使用 chr1–20 训练、chr21 验证、chr22 测试，从而避免相邻位点泄漏。公开脚本确实固定 chr21/chr22 为验证和测试，但训练循环仅写 `chroms=["chr1"]`，更像演示入口，而不是完整论文编排。

### 3. CpG 上下文如何压缩细胞维度

细胞先依据 100 kb bin 的甲基化轮廓聚类。对某个邻近 CpG $q$ 和细胞簇 $c$，簇级特征是

$$
r_{qc}=\frac{\text{cluster }c\text{ 中覆盖 }q\text{ 的甲基化读段数}}
{\text{cluster }c\text{ 中覆盖 }q\text{ 的总读段数}}.
$$

因此 CpG 分支不把几千个细胞的原始稀疏矩阵直接送进 Transformer，而是先形成“邻近 CpG × 细胞簇”的较致密上下文。代码 `run_feature.py:111-132` 直接计算这个比例；`datasets.py:427-442` 取目标附近窗口并构造训练样本。

### 4. 双分支网络从左到右怎样读

#### DNA 分支

模型截取目标 CpG 两侧合计约 2 kb 的参考序列，经过三层一维卷积/池化提取局部 motif，再经过 8 层、8 头 Transformer 聚合较远位置之间的组合关系，最后取得 256 维摘要。

#### CpG 分支

邻近 CpG × 细胞簇矩阵先经二维卷积提取局部甲基化图案，再分别沿两个轴建模：一条 Transformer 强调 CpG 位置关系，另一条强调细胞簇关系。两个摘要与 DNA 摘要共同形成预测信息。

#### 多细胞输出

融合头把 DNA 与 CpG 表示拼接，并输出长度等于细胞数的向量：

$$
\hat{\mathbf y}_p=(\hat y_{p1},\ldots,\hat y_{pN}).
$$

这就是论文所说的 multi-task：每个细胞相当于一个相关预测任务，共享目标位点的序列和邻域表示。代码的 `single_cell_regression` 在 `modeling_bert.py:601-645` 明确实例化两套 CNN–Transformer 与一个多值预测头。

### 5. 缺失标签怎样被排除

理想化损失可写为

$$
\mathcal L_p=\frac{\sum_i m_{pi}w_i(\hat y_{pi}-y_{pi})^2}
{\sum_i m_{pi}}.
$$

代码先把所有目标初始化为 $-1$，只把观测到的 high/low cell IDs 设为 1/0，再以 `targets >= 0` 选出有效位置（`modeling_utils.py:980-1008`）。此外实现给未甲基化标签权重 3、甲基化标签权重 1；这是直接代码证据，但论文方法文字没有解释这一不对称权重。

举例：某 CpG 在四个细胞的标签为 $(1,\text{缺失},0,\text{缺失})$，预测为 $(0.8,0.4,0.3,0.7)$，有效项只有第 1、3 个，代码损失与 $1(0.8-1)^2+3(0.3-0)^2$ 成正比；两个缺失位置完全不进入损失。

### 6. 为什么需要插补质量分数

论文定义目标 CpG 的预测与上下游各 5 个 CpG 预测之间的平均绝对差：

$$
Q_{pi}=\frac{1}{10}\sum_{q\in\mathcal N_{10}(p)}
|\hat y_{pi}-\hat y_{qi}|.
$$

$Q$ 小表示局部更一致，被视为更可靠。sn-m3C-seq 无下采样时，AUPRC 从不过滤的 0.855 提升到阈值 0.1 时的 0.935。这个指标是经验置信度代理，不是概率校准；真实调控边界也可能出现局部突变。公开仓库中未找到该分数和过滤管线的实现。

### 7. 七张图怎样形成证据链

- **图 1** 给出双分支架构：2 kb DNA、簇级邻近 CpG、三个 Transformer 摘要和全细胞输出。
- **图 2** 在五个数据集上比较模块消融和基线；从头训练平均 AUPRC 0.871，微调 0.869。高变 CpG 明显更难，不能只看总体高分。
- **图 3** 显示即使只保留 1% CpG 覆盖，scMeFormer 仍高于簇均值基线。
- **图 4** 证明更严格质量阈值通常提高 AUPRC，呈现覆盖率—准确率权衡。
- **图 5** 用 ARI 验证插补后能更好恢复原始细胞簇，过滤版本总体最佳。
- **图 6** 显示细胞类型 DMR 富集多种脑/精神性状遗传力，而身高和 2 型糖尿病缺乏相似模式。
- **图 7** 将方法用于 2534 个前额叶细胞核、4 个 SCZ 病例和 4 个对照；原始稀疏数据未检出 DMR，插补后检出数千个，并连接 GWAS、DEG 与突触相关 GO 信号。

图 7 的生物发现依赖完整下游链，而不只是神经网络输出。公开模型仓库没有 DMRfind、S-LDSC、MAGMA、DEG、染色质环和 GO 分析脚本，因此这些结论是论文证据，不是本地代码可重跑证据。

### 8. 论文与代码对应

| 环节 | 直接代码证据 | 对应程度 |
|---|---|---|
| 2 kb DNA 输入 | `datasets.py:433-435` | Exact |
| DNA CNN 与 Transformer | `models/modeling_bert.py:387-427`, `models/modeling_bert.py:637-641` | Partial |
| 邻近 CpG/簇特征 | `run_feature.py:111-132`, `datasets.py:437-442` | Exact/Partial |
| 双分支融合与每细胞输出 | `models/modeling_bert.py:601-645`, `models/modeling_utils.py:962-978` | Exact |
| 观测掩码与加权 MSE | `models/modeling_utils.py:980-1008` | Exact，含论文未写权重 |
| chr21/chr22 验证测试 | `training.py:641-642` | Exact |
| chr1–20 完整训练 | 公开脚本 `training.py:701-718` 只遍历 chr1 | Partial |
| 质量过滤、DMR 与 SCZ 富集 | 搜索公开仓库未找到 | Not found |

### 9. 复现时必须记住的边界

- 论文描述融合全连接隐藏层 768 单元，发布 `config.json` 和预测头实际使用 512；没有另一份配置解释差异。
- DNA/CpG dropout 也与论文文字不完全一致。
- AUPRC helper 存在，但验证/预测循环中的相关块被注释。
- 预训练—微调接口存在，论文各数据集的完整调度脚本未发布。
- 模型对训练分布、细胞聚类质量和局部平滑假设敏感；插补新增的大量 DMR 必须通过过滤与外部功能证据约束。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scMeFormer

**Paper**: Deep learning imputes DNA methylation states in single cells and enhances the detection of epigenetic alterations in schizophrenia
**Journal**: Cell Genomics, 2025
**DOI**: 10.1016/j.xgen.2025.100774
**Code**: https://github.com/LieberInstitute/scMeformer
**Category**: representation_models

### Motivation and Novelty

Single-cell DNA methylation assays can reveal cell-type regulatory states at cytosine resolution, but each nucleus covers only a small fraction of CpG sites. This makes downstream analyses such as clustering, DMR detection, and disease enrichment underpowered unless missing CpG states can be imputed reliably.

scMeFormer is a Transformer-based model for imputing CpG methylation states across thousands of single cells. Its main novelty is the combination of:

- local 2 kb DNA sequence context around a target CpG,
- neighboring-CpG methylation context summarized across predefined cell clusters,
- a multi-task output head that predicts the target CpG state for all cells at once,
- post-imputation filtering based on local CpG consistency.

Compared with prior methylation-imputation methods, the paper emphasizes scalability and combined sequence/methylation context. Melissa (Genome Biology, 2019) targets regions of interest rather than genome-wide per-CpG imputation. DeepCpG (Genome Biology, 2017) and CpG Transformer (Bioinformatics, 2022) model sequence/methylation context but are described as hard to scale to thousands of cells. GraphCpG (Bioinformatics, 2023) uses neighboring methylation graphs but lacks DNA-sequence input and predicts one CpG-cell pair at a time. CaMelia (Bioinformatics, 2021) is a gradient-boosting/local-similarity baseline rather than a deep sequence-context model.

### Method Overview

For each target CpG, scMeFormer builds two inputs. The DNA module receives a 2 kb sequence centered on the CpG and processes it with three CNN layers followed by an eight-layer Transformer. The CpG module receives methylation levels of neighboring CpGs across cell clusters and processes them with convolutional and Transformer layers. The learned DNA and CpG features are concatenated and passed to a fully connected prediction head that outputs one methylation value per cell.

Training labels are binary: CpG-cell observations are 1 if all reads support methylation and 0 if all reads support unmethylation; mixed-read sites are excluded. Only measured CpG-cell pairs contribute to the loss. The paper splits CpGs by chromosome, using chromosomes 1-20 for training, chromosome 21 for validation, and chromosome 22 for testing.

After prediction, the paper defines an imputation quality score from local consistency between the target CpG and nearby CpGs. Stricter filtering improves retained-call quality but reduces coverage. The denser methylome is then used for cell-type clustering, DMR detection, heritability enrichment, and a schizophrenia case study.

### Evaluation

The paper evaluates scMeFormer on five single-nucleus DNAm datasets: four human brain datasets and one mouse embryo dataset. Reported average AUPRC is 0.871 when trained from scratch and 0.869 with fine-tuning. Ablations show both sequence and CpG modules contribute: CpG-only remains strong but below the full model, while DNA-only is substantially weaker.

Under downsampling, scMeFormer outperforms a cluster-imputation baseline across four human datasets, including at very low coverage. The filtering score improves AUPRC and DMR precision, supporting its use as a confidence proxy. Imputed data also recover cell-type clusters better than raw downsampled data or cluster imputation at low coverage.

For biological validation, cell-type-specific DMRs from imputed data are enriched for H3K27ac-marked enhancers and brain/psychiatric trait heritability. In the schizophrenia case study, scMeFormer is applied to 2,534 prefrontal cortex nuclei from four SCZ cases and four neurotypical controls. The paper reports no detectable DMRs before imputation, but thousands after imputation, with up-regulated DMR-linked genes showing convergence with SCZ GWAS signals, down-regulated DEGs in excitatory neurons, and synaptic GO terms.

This should be interpreted as candidate regulatory evidence, not causal proof. The SCZ analysis is observational, small in sample count, and depends on imputation plus downstream enrichment rather than perturbational validation.

### Code Verification

The public repository supports the core neural model: DNA/CpG modules, eight-layer Transformer config, multi-cell output head, sparse observed-label masking, chromosome 21/22 validation/test handling, baseline variants, and basic training/prediction commands.

Important paper-code gaps remain. The released config uses a 512-hidden-unit prediction head rather than the paper’s 768-unit prose description. The DNA/CpG module dropout values differ from the paper text. The public training loop is demo-oriented and hardcodes `chr1` for training, while full-paper training uses chromosomes 1-20. AUPRC code exists but is commented out in validation/prediction loops. Scripts for imputation quality filtering, DMRfind, S-LDSC, MAGMA, DEG enrichment, chromatin-loop target assignment, and GO enrichment were not found in the public repository.

### Limitations

- The quality score assumes local CpG methylation smoothness, which can fail in heterogeneous regulatory regions.
- The model uses reference-genome sequence rather than individual-specific sequence.
- CpG sites with mixed methylated/unmethylated reads are excluded from supervised labels.
- The public code is not a complete end-to-end reproduction package for all figures.
- The SCZ application has a small case-control sample and should be treated as hypothesis-generating.
- The method currently focuses on CpG methylation; CpH methylation, important in neurons, is not directly imputed.

### Reproducibility Rating

**3 / 5**

The main architecture and training machinery are public and code-verifiable, and the repository includes demo data plus command examples. However, full reproduction of the paper’s benchmark tables and biological figures is incomplete from the public code alone. Several downstream analysis components are missing, some preprocessing scripts are hardcoded to local paths/sample names, and some implementation details diverge from the Methods prose.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
