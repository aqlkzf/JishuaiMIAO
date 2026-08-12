---
layout: default
permalink: /paper-atlas/connectome-seq-14a115c0/
title: "Connectome-seq"
nav: false
description: "Connectome-seq 的真正价值不是“用测序替代所有 connectomics”，而是建立了一条可扩展的桥梁：把物理单突触中的成对 RNA 条形码，与两端神经元的单核转录组重新连接起来，从而在同一实验中同时获得连接关系和分子身份。"
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>Connectome-seq</h1>
    <p>Connectome-seq: high-throughput mapping of neuronal connectivity at single-synapse resolution via barcode sequencing</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Connectome-seq 方法详解

### 它要解决什么问题？

神经回路研究希望同时回答两件事：

1. 哪两个神经元在突触处直接相连？
2. 这两个神经元分别是什么细胞类型、表达哪些基因？

传统方法往往只能很好地回答其中一部分。串行电镜能够看到突触，但在哺乳动物大脑中跨脑区重建代价极高；mGRASP（*Nature Methods*, 2012）和 LICONN（*Nature*, 2025）等成像方法仍需要大规模体积成像与复杂重建；MAPseq（*Neuron*, 2016）、BARseq（*Cell*, 2019）和 BRICseq（*Cell*, 2020）擅长高通量投射追踪，却不直接给出一个突触的两个细胞伙伴；SBARRO（*Nature Communications*, 2022）等狂犬病毒条形码方法可能受到病毒毒性和高密度组织中条形码混合的影响。SYNseq（*Nucleic Acids Research*, 2017）已经提出“突触两侧各带一个条形码”的思路，但需要跨突触交联和条形码连接反应。

Connectome-seq 的核心转换是：**不在显微镜图像里重建每个突触，也不在液滴里把两个条形码化学连接起来；而是把一个完整的单突触体物理分离出来，分别测到它的突触前和突触后 RNA 条形码。**

### 核心创新

#### 1. 用 SynBar 把突触变成一对 RNA 标签

突触前侧表达 PreSynBar，突触后侧表达 PostSynBar。两者分别基于 neurexin 1β 和 neuroligin 1，并携带互补的 split-GFP 片段。它们在突触处相互作用时，GFP 得以重构，同时把两侧的 RNA 条形码带到同一突触界面。

每条 PreRNA/PostRNA 都含有：

- 一个随机 30 nt 区域 N30，用来标记来源神经元；
- 两个 BoxB 位点，与 SynBar 上的 λN22 RNA 结合结构域结合；
- PCR 扩增区；
- 适配 10× feature barcoding 的 CS1 或 CS2 捕获序列；
- poly(A)。

PreRNA 还加入 RPL7 5′ UTR，以增强沿长轴突运输到突触前末梢的能力。一个容易忽略但很关键的工程细节是：PreSynBar 的 λN22 不能简单放在最末端，而要放在 C 端内部位置，否则会破坏跨细胞相互作用。

#### 2. 同一块组织同时得到细胞身份和突触连接

脑组织温和匀浆后，细胞核与突触体走向两条并行路线：

- 慢速离心得到核组分；Sun1-Tag GFP 标记被感染神经元的细胞核，FACS 分选 GFP+ 单核；
- 上清高速离心得到粗突触体；通过噪声、单颗粒、膜完整性以及 V5+/HA+ 双阳性门控，富集同时含 PreSynBar 和 PostSynBar 的单突触体。

这样，细胞核提供“转录组 + 一侧条形码”，突触体提供“成对的两侧条形码”。把同一条 N30 在两种结构中对应起来，就能把突触连接映射回具体神经元。

#### 3. 为细胞核和突触体设计不同的 10× 文库

细胞核需要同时测 mRNA 和条形码，因此 10× gel bead 同时携带 poly(dT)、CS1 和 CS2 捕获序列。初次扩增后，按长度把较长的 mRNA cDNA 与较短的条形码 cDNA 分开，再分别建库。

突触体中线粒体 RNA 占比高，而且突触体转录组不能可靠地区分细胞身份，所以最终方案放弃突触体 mRNA，只专门扩增 PreRNA 和 PostRNA。为避免高丰度一侧压制低丰度一侧，作者使用了 LNA 修饰引物改善扩增平衡。

### 计算流程

```text
原始测序 reads
   |
Cell Ranger：核用 force-cells，突触体用 expect-cells
   |
从 BAM 提取 N30 + 10× cell barcode + UMI
   |
数据集内部 Hamming 距离 1 折叠，纠正局部测序错误
   |-------------------------------------|
   |                                     |
细胞核路线                              突触体路线
按 N30-细胞统计独立 UMI                 合并样本并去污染
Seurat/Harmony/MapMyCell 注释细胞类型    去除含 >100 个 N30 的复杂颗粒
按 5×/2× 规则消除 N30 多细胞归属歧义    保留可解释的 Pre/Post 条形码
   |                                     |
   |--------------- N30 匹配 ------------|
              逐步测试 Hamming 0–10
              报告阈值选择 5
                       |
      同一突触体的 PreRNA → 一个突触前核
      同一突触体的 PostRNA → 一个突触后核
                       |
       得到 单神经元 × 单神经元 连接矩阵
       并附加两侧细胞类型与基因表达信息
```

#### Hamming 距离的作用

对两个等长 N30 序列 $x$ 和 $y$：

$$
d_H(x,y)=\sum_{i=1}^{30}\mathbf{1}[x_i\neq y_i].
$$

流程中有两个不同层次：

- 在同一数据集中先用距离 1 折叠近似序列，主要纠正测序/PCR 错误；
- 再把突触体 N30 与细胞核 N30 做跨组分匹配，扫描距离 0–10，论文根据匹配率趋于平台以及随机 N30 的理论距离分布，选择距离 5 作为主要结果阈值。

阈值越大，召回率越高，但随机近邻和错误匹配也会增加。因此作者再加入生物约束：一个突触体不能同时来自多个神经元；多核候选无法唯一解释时删除。

#### 两个不对称的核条形码判定规则

如果同一 N30 关联多个细胞核，按 UMI 数排序。突触前 pons 数据要求第一名大于第二名的 5 倍；突触后 cerebellum 数据要求大于 2 倍：

$$
U^{pre}_1>5U^{pre}_2,\qquad U^{post}_1>2U^{post}_2.
$$

这种不对称阈值不是通用统计定律，而是当前数据和污染结构下的经验质量控制。代码中的可执行比较是严格 `>`。

### 在小鼠桥脑—小脑回路中的结果

研究使用六个生物学重复。QC 后得到 109,269 个 pons 细胞核和 78,358 个 cerebellum 细胞核；98.6% 的 pons 核含预期 PreRNA，98.7% 的 cerebellum 核含预期 PostRNA。

在 Hamming 距离 5：

- 81,452 个独特 PreRNA 中，32,269 个（39.6%）唯一匹配到突触前核；
- 147,164 个独特 PostRNA 中，62,205 个（42.3%）唯一匹配到突触后核；
- 单侧匹配得到 3,028 个 pons 核和 1,538 个 cerebellum 核；
- 最终双侧连接矩阵包含 327 个 pons 神经元、219 个 cerebellum 神经元和 464 个独特突触体。

主要输入来自 Fat2 Glut 和 Hoxb5 Glut 桥脑谷氨酸能神经元。小脑侧恢复了已知的 granule 和 Golgi 靶点，也出现了数量显著的 Purkinje 连接。后者不是只靠算法宣称：作者进一步使用 AAV1 顺行跨突触追踪、独立单核测序和蛋白免疫荧光验证，并发现 *Grid2ip*、*Cacna1g*、*Stac*、*Dlgap4*、*Abr* 等与连接阳性 Purkinje 细胞相关的标记。

### 如何正确理解“高通量”和“单突触分辨率”

“单突触分辨率”表示每个有效事件以一个被分选的双条形码突触体为物理单位，并不表示已经完整扫描了所有真实突触。“高通量”主要体现在一次实验可测数万细胞核和突触体，而不是最终连接覆盖率高。

当前灵敏度很低且强烈依赖细胞类型。论文估计 mossy fiber→granule cell 的灵敏度仅 0.00018%，而 mossy fiber→Golgi cell 为 0.23%。只有 23.6% 的突触体同时捕获两侧 RNA；最终矩阵只保留约 12% 的单侧匹配核。AAV 感染偏好、细胞大小、核 RNA 回收、突触体纯化、环境 RNA、PCR 偏倚以及匹配阈值都会改变不同细胞类型的表观连接频率。

因此，Connectome-seq 当前更适合：

- 在大规模样本中发现候选连接模式；
- 将连接状态与细胞类型/基因表达联合分析；
- 用独立追踪或成像方法验证意外连接。

它还不能替代电镜提供完整、无偏的解剖 connectome。

### 代码复现情况

论文自己的 GitHub 代码与计算方法总体对应良好：BAM 条形码提取、Hamming 折叠、核 UMI 聚合、5×/2× 去歧义、>100 N30 过滤、0–10 距离匹配、Harmony 与 MapMyCell 都能在源码中找到。

但仓库更像作者分析记录，而不是可直接复跑的软件包：没有端到端工作流、锁定环境、测试和小型示例；大量路径指向作者机器；若干中间文件和参考资源未打包；README 写的是 `connectome.py`，实际文件是 `cseq_BC_collapse.py`；突触体清洗脚本也没有清楚写出 README 声称的最终 CSV 文件。完整复现需要从 GEO `GSE312903` 重建数据路径、Cell Ranger 参考、依赖环境和中间文件。

### 一句话总结

Connectome-seq 的真正价值不是“用测序替代所有 connectomics”，而是建立了一条可扩展的桥梁：**把物理单突触中的成对 RNA 条形码，与两端神经元的单核转录组重新连接起来，从而在同一实验中同时获得连接关系和分子身份。**

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Connectome-seq

### Problem

Connectome-seq is a 2026 *Nature Methods* technology for mapping long-range mammalian neuronal connections at single-synapse resolution while retaining the transcriptomic identities of the connected cells. The central difficulty is scale: serial electron microscopy resolves synapses but is expensive and volume-limited; microscopy methods such as mGRASP (*Nature Methods*, 2012) and LICONN (*Nature*, 2025) require intensive imaging/reconstruction; projection-barcoding methods such as MAPseq (*Neuron*, 2016), BARseq (*Cell*, 2019; later variants) and BRICseq (*Cell*, 2020) do not directly identify both synaptic partners; rabies-barcode methods such as SBARRO (*Nature Communications*, 2022) face barcode mixing and toxicity. SYNseq (*Nucleic Acids Research*, 2017) proposed paired synaptic barcodes, but relied on crosslinking and barcode-joining chemistry.

### Method

Connectome-seq replaces barcode joining with physical isolation of single synaptosomes. Presynaptic and postsynaptic neurons receive AAV-delivered SynBar proteins carrying PreRNA and PostRNA N30 barcodes. PreSynBar and PostSynBar meet across the synaptic cleft; λN22–BoxB binding retains the corresponding RNAs at the two membranes. The tissue is then split into GFP-positive nuclei and V5+/HA+ double-positive synaptosomes. Modified 10× libraries jointly recover nuclear transcriptomes/barcodes and recover paired synaptosome barcodes.

Computationally, Cell Ranger and custom scripts extract N30–cell-barcode–UMI records, collapse within-dataset errors at Hamming distance 1, annotate nuclei with Seurat/Harmony/MapMyCell, remove ambiguous nucleus and synaptosome assignments, and iteratively match synaptosome N30s to nuclei. A five-mismatch threshold was selected from a 0–10 sweep. A synaptic edge is called when both sides of one synaptosome uniquely map to a presynaptic and postsynaptic nucleus.

### Main evidence

Across six mouse pontocerebellar replicates, the study recovered 109,269 high-quality pons nuclei and 78,358 high-quality cerebellar nuclei after QC, with expected barcode detection in 98.6% and 98.7% of nuclei. At Hamming distance 5, 32,269 PreRNAs (39.6%) and 62,205 PostRNAs (42.3%) uniquely matched nuclear sources. Single-side matching identified 3,028 pons and 1,538 cerebellar nuclei; the final double-sided matrix contained 327 pons neurons, 219 cerebellar neurons and 464 unique synaptosomes.

Recovered cell-type patterns included expected glutamatergic mossy-fiber inputs to granule and Golgi cells. Connectome-seq also reported substantial direct pons-to-Purkinje connectivity. The authors did not rely on barcode evidence alone: AAV1 anterograde transsynaptic tracing, single-nucleus profiling and protein-level marker validation supported the Purkinje connection and identified markers including *Grid2ip*, *Cacna1g*, *Stac*, *Dlgap4* and *Abr*.

### Limitations

Sensitivity remains low and strongly cell-type dependent. The paper estimates 0.00018% sensitivity for mossy-fiber→granule-cell connections versus 0.23% for mossy-fiber→Golgi-cell connections. Only 23.6% of synaptosomes captured both barcode RNAs, and the final matrix retained roughly 12% of the single-side-matched nuclei. AAV tropism, cell-size-dependent nuclear recovery, synaptosome purification, PCR bias, ambient RNA and barcode-matching thresholds all shape observed connection frequencies. Connectome-seq therefore provides sparse sampling rather than a complete anatomical connectome.

### Reproducibility assessment: 3/5

The paper provides GEO data (`GSE312903`), an MIT-licensed GitHub repository and a Zenodo release. The official code implements the main computational ideas with good paper-level fidelity: N30 extraction/collapse, UMI aggregation, 5×/2× disambiguation, >100-barcode filtering, iterative Hamming matching, Harmony integration and MapMyCell annotation are present.

The snapshot is not directly reproducible end to end. It lacks a workflow driver, locked environment, tests and small fixtures; notebooks/RMarkdown files contain author-local paths and require unbundled intermediate files and reference assets. The README names `connectome.py`, but the repository contains `cseq_BC_collapse.py`; clean synaptosome-output emission is unclear; and one tie-breaking branch references an undefined object. The code is best treated as a faithful analysis record that still needs substantial engineering before rerunning from raw data.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
