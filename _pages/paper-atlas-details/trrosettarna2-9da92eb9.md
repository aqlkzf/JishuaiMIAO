---
layout: default
permalink: /paper-atlas/trrosettarna2-9da92eb9/
title: "trRosettaRNA2"
nav: false
wide: true
description: "RNA 的三维结构数据远少于蛋白质结构数据，而且同一条 RNA 会因内在柔性而形成多个构象。论文提出 trRosettaRNA2，目标是从序列及其多序列比对（MSA）端到端预测 RNA 的全原子三维坐标，并利用不同的二级结构（SS）先验探索构象集合。Nature HTML 中可直接获得的主要证据是摘要、图注和数据/代码可用性信息；详细方法和数值结果来自补充材料。"
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
      <span>Computational Tools</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>trRosettaRNA2</h1>
    <p>Predicting RNA 3D structure and conformers using a pre-trained secondary structure model and structure-aware attention</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-026-01223-x" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for trRosettaRNA2">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/YangLab-SDU/trRosettaRNA2" target="_blank" rel="noopener noreferrer" aria-label="Open code for trRosettaRNA2">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## trRosettaRNA2 方法详解

### 1. 研究问题

RNA 的三维结构数据远少于蛋白质结构数据，而且同一条 RNA 会因内在柔性而形成多个构象。论文提出 trRosettaRNA2，目标是从序列及其多序列比对（MSA）端到端预测 RNA 的全原子三维坐标，并利用不同的二级结构（SS）先验探索构象集合。Nature HTML 中可直接获得的主要证据是摘要、图注和数据/代码可用性信息（`paper source/nature_html/paper.md:9-12,58-97`）；详细方法和数值结果来自补充材料。

此前的 trRosettaRNA（*Nature Communications*, 2023）主要先预测几何约束再折叠；其他比较对象包括 RhoFold/DeepFoldRNA、RoseTTAFoldNA、AlphaFold 3、DRfold2 和 RNAbpFlow。补充材料指出，外部 SS 依赖、结构数据稀缺、局部相互作用误差及生成结构中的空间冲突，是需要改进的方面（`supplementary_information.md:505-647,734-765`）。

### 2. 核心思路

trRosettaRNA2 将大量 SS 数据提供的折叠先验迁移到较小的 RNA 3D 结构任务中，并把该先验放进三处：

- **SS 先验模块（trRNA2-SS）**：在 bpRNA 上预训练 8 个 RNAformer block，再用 PDB 衍生数据微调；三个微调模型的 SS 概率图可以取平均。
- **SS-aware Structure Module**：在结构模块的 invariant point attention（IPA）中，SS 概率参与注意力归一化，使可能成对的核苷酸更容易交换信息。
- **构象生成**：给模型不同的 SS 概率图即可得到不同空间构象；输出还可以经过轻量 relaxation 或可选的 PyRosetta 约束能量最小化。

补充材料将这三点列为方法贡献，并强调它从旧的“两步几何约束”流程转为直接预测全原子坐标（`supplementary_information.md:734-765`）。

### 3. 输入、表示与输出

设目标 RNA 长度为 `L`，MSA 行数为 `N`。推理接口 `predict(model, seq, msa, ss)` 接受目标序列、MSA 张量和可选的 `L × L` SS 图；若未提供 SS，脚本会调用三个 SS 模型并平均其输出（`code/trRNA2/predict.py:87-130,166-187`）。

`InputEmbedder` 对 MSA 做 5 类 token one-hot 编码和相似度重加权，计算目标序列的一维 one-hot/PSSM/信息量特征及 26 通道 DCA 特征，再拼接成 46 通道的二维 pair 特征；启用 SS 时再追加一个 SS 通道并用 `1 × 1` 卷积投影（`code/trRNA2/model_3d.py:14-60`）。因此主要表示为：

```text
MSA (N,L) ──> m (N,L,64)
       └──> pair features (L,L,46 [+ 1 SS]) ──> z
```

最终输出包括全原子坐标、C1' 坐标、残基刚体 frame、距离/接触几何分布、SS 概率和 pLDDT。`Folding.forward` 的 pLDDT 由 50 个区间的 softmax 期望得到（`code/trRNA2/model_3d.py:264-297`），`predict.py` 将坐标和几何结果写为 PDB、压缩数组及 `plddt.csv`（`code/trRNA2/predict.py:204-237`）。

### 4. 计算流程

```text
序列 + MSA + (可选 SS)
        │
        ├─ trRNA2-SS：RNAformer(8 blocks) -> SS 概率图
        └─ InputEmbedder：token/PSSM/DCA/SS -> m,z
                         │
              RecyclingEmbedder 加入上一轮 C1' 距离
                         │
                 RNAformer 两轨表示更新
                         │
          初始 frame（可选 InitStr_Network）
                         │
            SS-aware StructureModule（IPA）
                         │
     全原子坐标、frame、几何分布、SS、pLDDT
                         │
              可选 relaxation / PyRosetta
```

#### 4.1 RNAformer 与回收

RNAformer 同时维护 MSA track 和 pair track：MSA 行/列注意力及 transition 更新 MSA；outer-product mean、三角乘法、三角注意力和 pair transition 更新 pair 表示。补充材料 Algorithm 4 描述了该顺序，源码的 `BasicBlock.forward`/堆叠实现位于 `code/trRNA2/RNAformer.py:647-760`。

默认 `num_recycle=3`，所以执行 4 次结构 pass。每次将上一轮的 C1' 两两距离离散化后线性投影并加到 pair 表示，同时把上一轮 single 表示加回目标 MSA 行（`code/trRNA2/model_3d.py:104-119,209-234`）。这是静态推理路径的代码事实，并不等同于已验证的运行时轨迹。

#### 4.2 SS-aware IPA

普通 IPA 注意力 logits `a` 由 scalar、pair bias 和几何 point 项组成。没有 SS 时使用普通 softmax；有 SS 时，源码计算

$$w_{ij}=\exp(SS_{ij}/t_{SS})-0.99$$

并将 `weighted_softmax(a, w)` 用作归一化（`code/trRNA2/structure_module.py:370-383`）。`ss_usage` 还支持 `sum` 和 `linear` 模式，默认配置为 `multiply`（`code/trRNA2/structure_module.py:172-185,239-242`）。论文/补充材料的表述是“以 SS 加权替换 vanilla attention softmax”（`supplementary_information.md:771-778`）；源码进一步显示了具体温度和权重形式。

#### 4.3 结构生成与初始 frame

结构模块迭代 IPA、transition、backbone 更新和 torsion-angle ResNet，并把刚体 frame 转为核苷酸原子坐标（`code/trRNA2/structure_module.py:519-700`）。若配置 `init_str='nn'`，`InitStr_Network` 使用序列、MSA/pair 节点边特征和可选 SS，通过图 Transformer 预测 quaternion/translation 初始 frame（`code/trRNA2/InitStrGenerator.py:155-263`; 调用位于 `code/trRNA2/model_3d.py:241-251`）。

### 5. 训练目标

补充材料定义了但克隆代码没有实现训练驱动的目标函数：

- FAPE：以 10 Å 归一化并使用随机 10 Å clamp（`supplementary_information.md:891-903`）；
- `Lgeo2D`：六类离散距离交叉熵加二元 contact loss（`supplementary_information.md:905-923`）；
- torsion sine/cosine MSE 与 50-bin pLDDT 交叉熵（`supplementary_information.md:926-940`）；
- 原生 base-pair 界限、O3'-P/P-P/键角及 steric clash 的 L1 惩罚（`supplementary_information.md:944-961`）。

损失权重、训练数据预处理和训练脚本在 `code/` 的已搜索范围内 **Not found**；不能从推理代码反推出精确训练配方。

### 6. 评估与解释

SS 预测在 ArchiveII（50 条 RNA）和 PDB2D（19 条、2022 年后发布且去冗余）上与 RNAfold、SPOT-RNA、RNA-MSM、KnotFold、BPfold 等方法比较。trRNA2-SS 的 AUPRC 分别为 0.874 和 0.822（`supplementary_information.md:64-99,971-1029`）。

3D 评估使用 TS28、CASP15/CASP16，指标包括 RMSD、lDDT、TM-score、INF 和 clashscore。去掉 SS prior 后 TS28 平均 RMSD 从 9.07 Å 升至 11.8 Å（`supplementary_information.md:253-279`）。CASP15 六条自然 RNA 的表格给出 trRosettaRNA2 RMSD 9.19 Å、clashscore 2.6；合成 RNA 仍明显困难（`supplementary_information.md:505-565,1141-1209`）。论文摘要报告 Yang-Server 在 CASP16 中为最佳自动服务器；RNase P 图像和补充材料显示模型可生成与 AFM 观测相符的域级异质构象，而 AlphaFold 3 集合更均一（`paper.md:9-12,68-75`; `supplementary_information.md:759-765`）。

### 7. 代码一致性与缺口

**Exact**：MSA/SS 特征、RNAformer 主干、4-pass recycling、SS-aware IPA、神经初始 frame、几何/pLDDT 输出、三模型 SS ensemble 和 PDB 导出均有直接源码证据。**Partial**：结构模块的训练时细节和 PyRosetta refinement 的完整实现/默认值不完整。**Not found**：训练脚本、损失聚合、训练数据处理、权重文件。运行还需要外部 MSA 数据库/工具；权重和可选 PyRosetta 不随此快照提供。上述判断针对 GitHub commit `9839687f57a476df42323fe86d6effa78bf32a2e`，源码导航范围记录在 `scratch/evidence_index.json` 和 `doc_code.md`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## trRosettaRNA2: Summary

### Problem

RNA 3D prediction is constrained by the small number of experimentally determined structures and by RNA flexibility: a single sequence may occupy multiple conformations. Earlier pipelines often depend on externally predicted secondary structure (SS), predict restraints rather than coordinates, or require large ensembles and expensive refinement. The paper positions trRosettaRNA2 as an end-to-end method that uses abundant SS data to compensate for scarce 3D supervision (`paper.md:9-12`; `supplementary_information.md:48-58,734-765`).

Relevant predecessors include trRosettaRNA (*Nature Communications*, 2023), which uses a two-step restraint pipeline; RhoFold (*Nature Methods*, 2024) and RoseTTAFoldNA (*Nature Methods*, 2024); AlphaFold 3 (*Nature*, 2024); and DRfold2 and RNAbpFlow, whose resource or SS-dependence limitations are discussed in the supplement (`paper.md:109-126`; `supplementary_information.md:505-647,734-765`).

### Proposed Method

trRosettaRNA2 combines three ideas:

1. **A transferred SS prior.** An eight-block RNAformer is pre-trained on bpRNA and fine-tuned on PDB-derived labels. Three fine-tuned models can be averaged to produce the trRNA2-SS probability map.
2. **SS-aware end-to-end folding.** MSA-derived sequence, profile and covariance features are combined with the SS map, processed by a two-track RNAformer trunk, and converted directly to all-atom coordinates by a structure module. Within invariant point attention, SS-dependent weights replace ordinary softmax weighting.
3. **Recycling and conformer sampling.** The model performs four structure passes by default. Diverse supplied SS maps can steer different conformers, while optional relaxation or PyRosetta minimization can repair structural violations.

The released source verifies the inference path: feature construction in `code/trRNA2/model_3d.py:14-101`, four-pass recycling and coordinate/confidence outputs in `code/trRNA2/model_3d.py:209-298`, SS-weighted attention in `code/trRNA2/structure_module.py:370-383`, and the three-model SS ensemble plus output/refinement interface in `code/trRNA2/predict.py:87-130,166-252`.

### Evaluation

The SS predictor is evaluated on 50 ArchiveII RNAs and 19 post-2022, non-redundant PDB2D RNAs against energy/evolutionary and deep-learning baselines. The authors report AUPRC 0.874 on ArchiveII and 0.822 on PDB2D (`supplementary_information.md:64-99,971-1029`).

For 3D prediction, the paper uses TS28, CASP15 and CASP16 targets and reports RMSD, lDDT, TM-score, INF and clashscore. The SS-prior ablation raises average TS28 RMSD from 9.07 to 11.8 Å, supporting the value of transferred SS information (`supplementary_information.md:253-279`). On six natural CASP15 RNAs, trRosettaRNA2 reports RMSD 9.19 Å and clashscore 2.6; its synthetic-RNA accuracy remains well below the leading human group, a limitation the authors state directly (`supplementary_information.md:505-565,1141-1209`). The abstract reports Yang-Server as the top automated server in CASP16, and Fig. 4 plus the supplement support RNase P conformer sampling consistent with domain-level AFM heterogeneity (`paper.md:9-12,68-75`; `supplementary_information.md:759-765`).

These are paper-reported results, not independently rerun benchmarks in this workspace.

### Reproducibility and Evidence Limits

**Code-paper fidelity is medium-high for inference.** The checked GitHub snapshot at commit `9839687f57a476df42323fe86d6effa78bf32a2e` closely matches the supplementary pseudocode for inputs, RNAformer/recycling, SS-aware structure generation, confidence and PDB export. The repository provides examples and an inference entry point.

**Not found in the snapshot:** a training driver, the implemented aggregation of FAPE/geometry/torsion/pLDDT/base-pair/bond/clash losses, dataset preprocessing for training, and model checkpoints. Full reproduction also requires external MSA databases/tools and optionally PyRosetta. The accessible Nature HTML is subscription-limited to the abstract, captions, availability statements and references; detailed methods and numerical checks therefore rely on the acquired supplementary information. No training or benchmark run was executed here.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
