---
layout: default
permalink: /paper-atlas/alzheimers-3dgenome-multiomics-061feb70/
title: "Alzheimers_3DGenome_Multiomics"
nav: false
description: "阿尔茨海默病（AD）的单细胞研究已经发现大量细胞类型特异的转录和染色质可及性变化，但仍缺少一个关键环节：同一个细胞中的三维基因组折叠是否也发生变化，并且这些变化是否与转录失调相联系？ 过去几类工作各自只覆盖问题的一部分： Mathys 等在 Nature 2019、Cell 2023 和 Nature 2024 的单细胞/单核转录组图谱解析了 AD 的细胞类型和基因表达变化，但没有在同一细胞测量 Hi-C。"
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
      <span>Atlases &amp; Resources</span>
      <span>Science · 2026</span>
    </div>
    <h1>Alzheimers_3DGenome_Multiomics</h1>
    <p>Single-cell multiomics connects 3D genome and transcriptome alterations in Alzheimer&#x27;s disease</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1126/science.adz1652" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Alzheimers_3DGenome_Multiomics">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ma-compbio/AD-multiome" target="_blank" rel="noopener noreferrer" aria-label="Open code for Alzheimers_3DGenome_Multiomics">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 阿尔茨海默病单细胞 3D 基因组-转录组图谱：方法详解

### 一、这篇论文要解决什么问题？

阿尔茨海默病（AD）的单细胞研究已经发现大量细胞类型特异的转录和染色质可及性变化，但仍缺少一个关键环节：**同一个细胞中的三维基因组折叠是否也发生变化，并且这些变化是否与转录失调相联系？**

过去几类工作各自只覆盖问题的一部分：

- Mathys 等在 *Nature* 2019、*Cell* 2023 和 *Nature* 2024 的单细胞/单核转录组图谱解析了 AD 的细胞类型和基因表达变化，但没有在同一细胞测量 Hi-C。
- Xiong 等在 *Cell* 2023 的 snATAC-seq 图谱给出了染色质可及性和候选顺式调控元件（cCRE），但没有同细胞的 RNA-3D 接触配对。
- Nativio 等 2024 年的皮层 Hi-C 预印本研究了整体构象变化，但 bulk 数据不能分辨细胞类型。
- GAGE-seq 在 *Nature Genetics* 2024 中建立了同细胞联合测量 RNA 和 3D 接触的技术。本论文不是重新发明 GAGE-seq，而是把它用于 20 位 ROSMAP 供体，并与 snATAC-seq、Xenium 空间转录组和深度学习模型整合。

因此，这篇论文最合适的定位是：**以数据资源/图谱为主体、以 Hicformer 为计算建模模块的多模态研究**。

### 二、研究输入和最终输出

#### 输入

1. 20 位前额叶皮层（PFC）供体：10 位晚期 AD、10 位年龄匹配的 non-AD。
2. GAGE-seq：同一细胞核中的 RNA 和 scHi-C。
3. 同一批供体已有的 snATAC-seq：用于标注 cCRE。
4. 4 位供体的 Xenium Prime 5K：2 位 AD、2 位 non-AD。
5. DNA 序列表示、1D Hi-C 特征和 2D 局部接触图：用于 Hicformer。

#### 输出

- 23,825 个高质量 GAGE-seq 细胞的 RNA-3D 联合图谱；
- AD 与 non-AD 的差异表达、通路和细胞衰老程序；
- 长/短程接触、A/B compartment、subcompartment、loop 和 cCRE 接触变化；
- Hicformer 的细胞类型-疾病状态特异表达预测；
- 213,271 个 Xenium 细胞的空间 metagene、邻域和配体-受体共定位结果；
- 可供后续实验验证的调控元件与基因程序假设。

### 三、从原始数据到生物学结论的完整流程

```text
20 位供体的 PFC 细胞核
        |
        +-- GAGE-seq RNA --------> 质控 -> 细胞注释 -> DEG/通路/衰老评分
        |
        +-- GAGE-seq scHi-C -----> 质控 -> 单细胞/伪 bulk 接触图
                                      |       |
                                      |       +-> A/B compartment、saddle、loop、距离分层
                                      +-> Fast-Higashi / scGHOST 单细胞结构状态
                                                      |
供体匹配 snATAC cCRE + CTCF --------------------------+
        |                                             |
        +-> cCRE 接触分层 + Hi-C ChromVAR             |
                                                      v
序列表示 + 1D/2D Hi-C ----------------------------> Hicformer
                                                      |
                                                      +-> 表达预测
                                                      +-> 论文报告的特征归因

4 位供体 Xenium -> 细胞/皮层注释 -> POPARI metagene
                                    -> 空间邻域、Moran's I、配体-受体共定位
```

这条流程中的箭头表示数据依赖，不表示因果。论文使用的是死后组织的静态横断面数据，作者也明确指出需要时间序列和功能扰动实验。

### 四、第一步：构建同细胞 RNA-3D 图谱

经过低覆盖细胞和 doublet 过滤后，作者保留 23,825 个细胞。每个细胞平均包含 22,704 个 UMI、2,477 个表达基因和 288,931 个染色质接触。RNA 标记基因把细胞分成 8 个大类和 22 个亚型。

一个重要的内部验证是：只使用 scHi-C 接触、通过 Fast-Higashi 得到的 UMAP，也能分开主要的神经元和胶质细胞群。Figure 1 的直接图像显示，3D 空间中的大类与 RNA 注释基本一致，但神经元亚型比 RNA 空间重叠更多。因此合理结论是“3D 接触包含广义细胞身份信号”，而不是“3D 接触可无误差替代 RNA 亚型注释”。

代码层面，仓库包含两条原始处理链：

- `GAGE_seq_pipeline_Hi-C/run.sh:6-60` 调度 demultiplex、alignment、bam2pair、merge、dedup 和 pair QC；
- `GAGE_seq_pipeline_RNA/pipeline_script/demultiplex.py:14-58,92-165` 对双 barcode 做唯一匹配，把 well ID 写入 FASTQ read name，并区分匹配/未匹配 reads。

但最终 23,825 个细胞的完整筛选命令无法公开复现：补充方法没有成功获取，ROSMAP 样本注释受控，部分配置和路径依赖作者集群。因此精确 QC 阈值属于 **Not found / MISSING evidence**。

### 五、第二步：把 3D 接触按尺度拆开

论文把同染色体接触距离 $d$ 分成四段：

$$
c(d)=
\begin{cases}
\text{short}, & 1\text{ kb}\le d<128\text{ kb},\\
\text{mid}, & 128\text{ kb}\le d<4.096\text{ Mb},\\
\text{long}, & 4.096\text{ Mb}\le d<65.536\text{ Mb},\\
\text{ultralong}, & d\ge65.536\text{ Mb}.
\end{cases}
$$

Figure 3 的可见模式不是“AD 中所有长程接触都绝对增强”，而是：

- short-range 接触比例下降；
- long-range 与 trans/cis 比例相对上升；
- 这一方向在多数细胞类型中一致，但效应不大。

这是理解全文的第一个关键点：作者观察的是**接触组成重分配**。

### 六、第三步：定义 A/B compartment mingling

伪 bulk A/B compartment 来自归一化 Hi-C 矩阵的第一特征向量。代码使用 100-kb `.mcool`，通过 GC phasing track 保证正分数对应活跃 compartment：

- `cell_pseudo_bulk.eigs_cis.py:31-84` 生成 `cooltools eigs-cis`；
- `cell_pseudo_bulk.saddle.py:33-101` 生成 cis/trans saddle 分析命令。

在单细胞层面，用 $N_{AB}$ 表示连接活跃与非活跃区域的异型接触，用 $N_{AA}$ 和 $N_{BB}$ 表示同型接触。论文的 mingling score 可概念化为：

$$
M=\frac{N_{AB}}{N_{AA}+N_{BB}}.
$$

AD 细胞的 $M$ 倾向更高，并伴随更低的 RNA UMI。氧化磷酸化和 RNA 代谢程序与 $M$ 正相关，而神经元、突触和 housekeeping 程序与 $M$ 负相关。

这里要避免因果误读：数据支持“更强 mingling 与这些转录程序共同出现”，不证明 mingling 导致转录下降。具体 pseudocount 和零分母处理在缺失的补充方法中，属于 **Not found**。

### 七、第四步：把变化定位到调控元件和 loop

作者利用同供体 snATAC-seq 把 cCRE 按 TSS 距离和 CTCF overlap 分类，再把接触分成：

- cCRE-cCRE；
- cCRE-non-cCRE；
- non-cCRE-non-cCRE。

主要模式是：局部接触普遍下降，而 128 kb 到 4.096 Mb 的 cCRE 相关接触相对增强，尤其是带 CTCF 的 anchor。Figure 4 中 short-range heatmap 以绿色下降为主，midrange 出现更多紫色增强；APA 在 astrocyte 和神经元中显示较明显的中心增强，microglia 较弱。

代码与论文距离定义一致：`cell_pseudo_bulk.loop_pileup.v2.py:47-109,164-170` 用 128 kb 和 4.096 Mb 分割 loop，区分 CTCF 与非 CTCF，并用 expected-cis 归一化和 ±200 kb flank 生成 `cooltools pileup`。

论文还提出 Hi-C ChromVAR：把 ChromVAR 的 motif enrichment 思路扩展到 3D 接触强度，并把 TF activity 与 mingling score 相关。CTCF 排名靠前，但这不等于 loop extrusion 活性已被证明改变。论文同时报告 CTCF binding 和 extrusion component expression 没有大变化。

**缺口：**完整 Hi-C ChromVAR 实现和 bias correction 细节在聚焦代码范围中 **Not found**。

### 八、第五步：Hicformer 如何整合序列和 3D 信息？

#### 8.1 论文描述

对每个基因，以 TSS 为中心取 ±200 kb，共 400 个约 1,024-bp bin。输入包括：

1. one-hot DNA sequence；
2. 1D Hi-C 特征：A/B、insulation、gene-body score；
3. 400×400 的局部 2D contact map。

模型在 7,598 个高变或差异基因、26 个细胞类型-疾病状态组合上训练。

#### 8.2 代码真实接收的张量

公开 trainer 并不直接接收 one-hot DNA，而是：

$$
S_g\in\mathbb{R}^{400\times1536},\qquad
H^{1D}_{gc}\in\mathbb{R}^{400\times5},\qquad
H^{2D}_{gc}\in\mathbb{R}^{400\times400}.
$$

- $S_g$ 从 `sequence_vector.pt` 加载，是已经计算好的 1536 维序列表示；
- 五个 1D channel 分别是 A/B、三个不同窗口的 insulation 和 gene-body score；
- 2D contact map 以稀疏格式读取，再转成对称 dense matrix。

这意味着公开训练入口从“序列编码之后”开始。如何从 one-hot 序列生成 `sequence_vector.pt` 在检查范围内 **Not found**。

#### 8.3 1D 特征如何进入模型？

序列向量先线性变换并池化，1D 特征经过 MLP 投影后直接相加：

$$
X_0=\operatorname{Pool}(W_S\operatorname{LN}(S_g))+W_HH^{1D}_{gc}.
$$

所以 1D 特征不是只在末端做回归，而是在 transformer 前就改变 token 表示。

#### 8.4 2D contact map 如何改变 attention？

每个 transformer layer 都计算 token 的相似度外积，再与 Gaussian blur 后的 Hi-C map 拼接：

$$
B_\ell=\operatorname{CNN}_\ell([
\operatorname{Blur}(H^{2D}_{gc});
\operatorname{norm}(X_{\ell-1}X_{\ell-1}^{\top})]).
$$

$B_\ell$ 被转换为每个 attention head 的 bias：

$$
A_\ell=\operatorname{softmax}(QK^\top+R+\alpha B_\ell),
$$

其中 $R$ 是相对位置项，$\alpha$ 是可学习参数，初始值为 100（`algo/module.py:253-333`）。这是真正的“3D-aware attention”：接触图直接调整 token 间注意力，而不是只作为最后一层的附加变量。

默认 11 层 transformer 后，模型 crop 到 240 个位置，通过 pointwise convolution 和 Softplus head 输出非负表达预测（`algo/Hcformer_pretrain.py:64-126,147-187`）。

#### 8.5 表达 target、数据划分和损失

raw expression 先在每个 cell type-condition 行内做 min-max normalization，再计算 $\log(1+10^4x)$。代码固定 20 个 cell type-condition index 训练、6 个留出；基因按 `genes.tsv` 顺序前 80% 与后 20% 划分，而不是运行时随机划分。

验证集由“seen cell / unseen gene”和“unseen cell / seen gene”两部分组成；测试集是“unseen cell × unseen gene”的笛卡尔积。这与论文的三类泛化问题相对应。

raw 模式的损失是：

$$
\mathcal{L}_{\text{Poisson}}=
\frac{1}{N}\sum_i\left(\hat y_i-y_i\log(\max(\hat y_i,10^{-20}))\right).
$$

验证 Pearson correlation 用于保存最佳 checkpoint；连续 10 个 epoch 没改善时 early stop。binary 模式改用 sigmoid BCE 和 ROC AUC。

#### 8.6 代码中容易忽略的细节

1. `sequence_vector.pt` 是预计算表示，不是原始 one-hot 序列。
2. 论文说“三类 1D 特征”，代码实际是五个 channel，因为 insulation 有三个窗口。
3. cell type-condition ID 是硬编码列表；生物标签依赖未公开 processed metadata 的顺序。
4. train/evaluation 都会跳过小于 `batch_size` 的最后一个 batch，因此 batch size 和样本顺序可能影响指标。
5. 公开 README 给出 baseline、1D、2D、1D+2D 四种训练命令，但 Fig. 5 使用的确切 sweep ID 和 checkpoint **Not found**。

### 九、Hicformer 的结果应该如何解释？

Figure 5 的四组 Pearson correlation 为：

| 场景 | Hicformer | sequence-only baseline |
|---|---:|---:|
| seen genes / seen cell types | 0.60 | 0.50 |
| unseen genes / seen cell types | 0.49 | 0.42 |
| seen genes / unseen cell types | 0.56 | 0.48 |
| unseen genes / unseen cell types | 0.49 | 0.42 |

这些结果支持：在该图谱的划分下，3D 特征提供了序列表示之外的预测信息。改善较大的基因富集于 interferon、cytokine 和免疫反应，以及与 compartment mingling 相关的 AD 通路。

但不能直接推出“3D 结构是这些表达变化的唯一原因”，因为 disease state、cell identity、1D/2D Hi-C 特征在同一数据集中共同变化，模型评估也不是独立外部队列。

论文通过 gradient attribution 报告 AD 中模型更依赖 A/B 和 gene-body 特征，并展示 SLC5A11 和 AQP4。Figure 5 的直接图像确实显示：

- SLC5A11 的 contact、gene-body score、RNA 和预测变化方向一致；
- AQP4 上游 distal cCRE 同时有 ATAC、CTCF、loop 和高 gradient；
- enhancer shuffle 后预测下降。

然而，公开代码中：

- gradient 的生成过程 **Not found**；
- AQP4 enhancer shuffle/3D perturbation 实现 **Not found**；
- R Markdown 只读取预计算 gradient table 做绘图。

因此，模型结构和训练属于 code-verified behavior；归因和 perturbation 属于 paper/figure-supported claim，而不是独立代码复现。

### 十、第六步：把核内变化放回组织空间

Xenium 质控后保留 213,271 个细胞。作者用 Seurat CCA 与 GAGE-seq 对齐细胞标签，并用 Visium marker 划分 L1-L6 和 white matter。POPARI 把表达分解为归一化 metagene，并学习疾病状态特异的空间 affinity。

Figure 6 显示：

- Xenium 与 GAGE-seq 的大类细胞表达变化方向一致；
- m15 富集与 compartment mingling 相关的基因；
- m0-m15 的空间共表达在 AD 中减弱；
- NCAM1-DPYSL2 等配体-受体对的表达和 imputed A/B score 共定位在 non-AD 更强。

作者用 bivariate Moran's I 衡量两个空间变量在邻接图上的共定位。其标准形式可写为：

$$
I_{xy}=\frac{n}{\sum_{ij}w_{ij}}
\frac{\sum_{ij}w_{ij}(x_i-\bar{x})(y_j-\bar{y})}
{\sqrt{\sum_i(x_i-\bar{x})^2\sum_j(y_j-\bar{y})^2}}.
$$

这里的 $w_{ij}$ 是空间邻域权重。论文具体邻域构造和 normalization 依赖缺失的补充方法/私有 processed input，因此属于部分可解释、不可完整复现。

还要注意 Xenium 只有 2 位 AD 和 2 位 non-AD。空间图像很适合生成机制假设，但不足以单独支持广泛人群外推。

### 十一、论文真正建立了什么证据链？

| 证据层 | 能支持的结论 | 不能支持的结论 |
|---|---|---|
| 同细胞 GAGE-seq | 3D 接触变化与 RNA 程序在同一细胞中关联 | 3D 变化导致 RNA 变化 |
| A/B 与 cCRE/loop 分析 | AD 中局部接触减弱、mingling 和部分中程调控接触增强 | CTCF 活性变化是唯一机制 |
| Hicformer | 3D 特征提高图谱内表达预测并提供候选调控位点 | 候选位点已获得功能验证 |
| Xenium | compartment-linked 程序与组织空间邻域相关 | 四位供体代表所有 AD 患者 |

最稳妥的总解释是：AD 伴随一种跨尺度的结构-功能状态，包括 compartment segregation 减弱、接触距离重分配、局部调控连接下降、部分中程 cCRE 接触增强，以及与之相关的转录和空间程序改变。

### 十二、复现边界和研究者应优先验证的内容

**可直接学习/改造：**

- GAGE-seq Hi-C/RNA 处理框架；
- pseudo-bulk compartment、saddle、APA 命令生成；
- Hicformer 数据 loader、1D/2D 融合、split、loss 和训练循环；
- 多个下游 R/Python 分析模块。

**当前不能端到端复现：**

- 受控 ROSMAP 数据和私有 sample annotation；
- 缺失的 Science supplementary methods；
- `sequence_vector.pt` 的完整生成流程；
- Fig. 5 的确切模型 checkpoint、sweep 和 processed tensor；
- gradient attribution 和 AQP4 perturbation 生成代码；
- 部分依赖作者 HPC 绝对路径的脚本。

因此，这个仓库的 paper-code fidelity 评为 **medium**：核心处理和 Hicformer 机制匹配良好，但最终图表的若干关键解释性步骤只公开了结果或绘图层。

对后续实验最有价值的假设包括：

1. 操纵特定细胞类型的 compartment 状态，测试 mingling 是否先于转录失调；
2. CRISPRi/CRISPR deletion 验证 AQP4 distal cCRE；
3. 扰动 CTCF/cohesin 或特定 loop，区分 compartment weakening 与 loop extrusion 机制；
4. 在独立 AD 队列和更多空间切片上检验 m0-m15、NCAM1-DPYSL2 等空间关联；
5. 用公开 checkpoint 和固定 processed tensor 重新发布 attribution pipeline，使模型解释可以独立复核。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Single-Cell 3D Genome and Transcriptome Alterations in Alzheimer's Disease

### Problem

Single-cell AD studies have cataloged transcriptional and accessibility changes, but they generally do not measure RNA and three-dimensional chromatin contacts in the same cell. Consequently, whether disease-associated gene programs coincide with altered genome folding in specific human brain cell types, and how those nuclear changes relate to tissue organization, had not been established.

Relevant precursors include the Mathys single-cell transcriptomic atlas (*Nature*, 2019), larger AD atlases from Mathys et al. (*Cell*, 2023; *Nature*, 2024), matched-donor snATAC-seq from Xiong et al. (*Cell*, 2023), and a bulk cortical Hi-C preprint from Nativio et al. (2024). These resolve expression, accessibility, or bulk conformation separately. GAGE-seq (*Nature Genetics*, 2024) provides the required same-cell RNA/Hi-C assay, but the present work is the first application at this AD cohort scale with matched accessibility and spatial context.

### Contribution

This Science 2026 study is best viewed as a **multimodal atlas/resource with a predictive-modeling component**. It profiles postmortem PFC from 10 late-stage AD and 10 age-matched non-AD ROSMAP donors using GAGE-seq, integrates matched snATAC-seq, adds Xenium spatial transcriptomics from two AD and two non-AD donors, and develops Hicformer to test whether 3D-genome features improve cell type-specific expression prediction.

The computational flow is:

```text
paired single-cell RNA + Hi-C
    -> cell annotation and AD/non-AD expression contrasts
    -> contact-distance, A/B compartment, subcompartment, and loop analyses
    -> cCRE/CTCF integration with matched snATAC-seq
    -> Hicformer: sequence representation + 1D/2D Hi-C -> expression
    -> Xenium/POPARI spatial programs and colocalization
```

### Main Results

- After QC, the atlas contains 23,825 GAGE-seq nuclei with an average of 22,704 UMIs, 2,477 expressed genes, and 288,931 chromatin contacts per cell. RNA and Fast-Higashi contact embeddings independently recover broad brain cell identities.
- GAGE-seq AD/non-AD differential expression agrees with an external AD scRNA-seq study across six major cell types (reported correlations 0.433 to 0.902). Neurons show broad down-regulation of synaptic and metabolic programs, while glial populations show stress and senescence-associated changes.
- Overall A/B patterns remain highly correlated between disease groups (0.914 to 0.989), but AD shows a reproducible redistribution from short-range (1-128 kb) toward longer-range contacts, higher trans/cis ratios, and increased A/B compartment mingling. Greater mingling associates with lower RNA output and with a shift from neuronal/housekeeping toward oxidative and RNA-processing programs.
- At regulatory elements, local contacts decline while midrange (128 kb-4.096 Mb) cCRE-associated interactions rise, particularly for CTCF-linked anchors. APA supports stronger midrange loop signal in astrocytes and neurons, with smaller changes in microglia.
- Hicformer integrates a sequence representation, five 1D Hi-C channels, and a 2D local contact map. In the four seen/unseen gene/cell-type settings shown in Fig. 5, Hicformer correlations exceed the sequence-only baseline: 0.60 vs 0.50, 0.49 vs 0.42, 0.56 vs 0.48, and 0.49 vs 0.42.
- The model preferentially improves genes in immune and compartment-linked AD programs and nominates SLC5A11 and an AQP4 distal cCRE as examples. These are model-supported hypotheses; no tissue perturbation establishes causality.
- Xenium retains 213,271 cells and recapitulates broad disease-expression trends. POPARI metagenes connect compartment-mingling programs to spatial neighborhoods, with reduced m0-m15 and selected ligand-receptor colocalization in the four analyzed sections.

### What Is Novel

The central novelty is not any single statistic. It is the same-cell and multiscale linkage of RNA, 3D genome structure, matched accessibility, predictive modeling, and spatial context. This makes it possible to relate cell-level compartment mingling directly to transcriptional output, stratify disease-associated contacts by regulatory annotation, and test whether measured 3D features add information beyond sequence.

### Interpretation and Limitations

The data support an AD-associated state with weakened compartment segregation and redistributed regulatory contacts. They do not show that compartment mingling initiates transcriptional dysregulation. The cohort is cross-sectional, GAGE-seq remains resource intensive, single-cell regulatory networks are not fully reconstructed, and Xenium generalization is limited by four donors. The paper itself calls for time-resolved and functional perturbation studies.

Hicformer provides predictive rather than causal evidence. Its held-out design tests genes and cell type-condition combinations within one processed atlas; it is not an external prospective cohort. A/B, disease, and cell identity covary, so improved prediction demonstrates additional information in 3D features but not a unique mechanistic pathway.

### Reproducibility

**Rating: 3/5 (substantial code, incomplete end-to-end reproduction).** The linked snapshot at commit `4cb92828bd0add1a93271b679a5cdc242c82ceb7` includes GAGE-seq processing, 3D feature calling, Hicformer training/ablation commands, and extensive analysis scripts. Direct source review verifies the multimodal loader, attention fusion, held-out split, Poisson objective, Pearson/AUC evaluation, compartment/saddle commands, and loop APA logic.

Important gaps remain:

- ROSMAP data and sample annotations are controlled/private, and scripts contain author-cluster paths.
- The supplementary methods could not be acquired, leaving some QC/statistical specifications unavailable.
- The trainer consumes precomputed `sequence_vector.pt`; its generation from one-hot sequence is **Not found**.
- Exact checkpoints, sweeps, and processed tensors behind Fig. 5 are **Not found**.
- Gradient-attribution generation and AQP4 in silico perturbation code are **Not found**; the repository contains downstream plotting references to precomputed gradients.
- No end-to-end run was attempted because required controlled inputs and model artifacts are unavailable.

The resource is therefore strong for inspecting and adapting the analysis architecture, but not currently a one-command reproduction of the published results.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
