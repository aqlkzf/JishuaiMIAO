---
layout: default
permalink: /paper-atlas/preimplantationembryomodels-d10b766e/
title: "PreimplantationEmbryoModels"
nav: false
wide: true
description: "植入前胚胎发育经历合子、卵裂、桑椹胚、内细胞团（ICM）、上胚层（EPI）、原始内胚层（PrE）和滋养外胚层（TE）等连续状态。单细胞 RNA 测序已经积累了许多数据集，但这些数据很难直接合并：样本数量小、测序技术和深度不同、批次效应明显、细胞标签不统一，而且人胚材料稀缺并严重偏向 TE。 传统分析通常先聚类，再由专家根据少数经典 marker 手工命名。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>PreimplantationEmbryoModels</h1>
    <p>Deep learning-based models for preimplantation mouse and human embryos based on single-cell RNA sequencing</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/brickmanlab/proks-salehin-et-al" target="_blank" rel="noopener noreferrer" aria-label="Open code for PreimplantationEmbryoModels">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 基于单细胞 RNA 测序的植入前小鼠与人胚胎深度学习参考模型

### 这篇论文要解决什么问题？

植入前胚胎发育经历合子、卵裂、桑椹胚、内细胞团（ICM）、上胚层（EPI）、原始内胚层（PrE）和滋养外胚层（TE）等连续状态。单细胞 RNA 测序已经积累了许多数据集，但这些数据很难直接合并：样本数量小、测序技术和深度不同、批次效应明显、细胞标签不统一，而且人胚材料稀缺并严重偏向 TE。

传统分析通常先聚类，再由专家根据少数经典 marker 手工命名。这种方式依赖经验，难以扩展到大量数据，也可能忽略更有判别力、但尚未成为经典 marker 的基因。另一方面，深度神经网络可以整合数据，却常被视为“黑箱”。

论文因此希望建立一个能够持续扩展的胚胎转录组参考：

1. 合并跨研究的体内胚胎 scRNA-seq；
2. 自动预测细胞类型和发育状态；
3. 解释模型用哪些基因做出预测；
4. 将新的体外胚胎模型映射到体内发育参考。

### 现有方法为什么不够？

- 线性整合方法在批次效应小、结构简单时有效，但早期胚胎发育高度动态，不同技术产生的噪声也不同。
- scVI（*Nature Methods*, 2018）用变分生成模型学习单细胞潜在空间，适合批次整合，但本身不直接解决标签解释问题。
- scGen（*Nature Methods*, 2019）主要面向扰动响应。它在本文的小鼠综合指标上得分最高，却把部分发育阶段分成不连通的“岛”，提示过度校正。
- scANVI（*Molecular Systems Biology*, 2021）在 scVI 上加入半监督标签，适合分类与查询映射，但类别不平衡时少数类型容易被忽略。
- SHAP（2017）可以解释预测，然而标准 DeepExplainer 不能直接处理 scANVI 所需的计数矩阵、批次和标签协变量。

### 论文提出了什么？

论文的贡献不是重新发明 scVI 或 scANVI，而是把数据整理、生成模型、分类器、轨迹验证和解释算法组合成一个针对植入前胚胎的参考系统，并实现了自定义的 `scANVIExplainer`。

```text
多个公开胚胎 scRNA-seq 数据集
        │
        ▼
nf-core 下载与定量 + 物种特异的标签和表达标准化
        │
        ▼
选择 3,000 个高变基因（HVG）
        │
        ▼
scVI / scANVI / scGen / PCA 比较
  ├─ 批次校正与生物保真指标
  └─ PAGA、UMAP、FA、伪时间的发育结构检查
        │
        ▼
scVI 参考潜在空间 z
        │
        ├─ scANVI 概率分类（含每类 n=15 的平衡训练）
        ├─ 解码表达矩阵 -> XGBoost 分类
        └─ scANVIExplainer -> 稳定的基因贡献
        │
        ▼
新数据查询：适配参考模型 -> 类型概率 -> 不确定性
```

### 第一步：建立小鼠和人的参考数据

作者只选择有同行评审、具有采样时间和细胞类型标注的体内野生型数据。最终汇总了 13 个小鼠和 6 个人类数据集，覆盖 11 年和 5 种测序技术。小鼠最终矩阵包含 2,004 个细胞和 34,346 个基因。

人类数据更困难：原始细胞中约 55% 被标注为 TE，许多早期或过渡状态标签不确定。作者把不确定标签设为 `Unknown`，把 8C 之前的阶段合并为 `prelineage`，并保留原始标签以便追溯。

SMART-seq 全长测序的计数按平均基因长度标准化，以提高与 UMI 数据的兼容性。之后进行基因/细胞过滤、深度标准化和 `log1p` 转换。

### 第二步：学习发育潜在空间

每个物种选择 3,000 个 HVG。自动调参搜索如下范围：

- 似然：负二项（NB）或零膨胀负二项（ZINB）；
- 离散度：`gene` 或 `gene-batch`；
- 隐藏层宽度：128、144、256；
- 层数：2–5；
- 学习率：$10^{-4}$ 到 $0.6$；
- 50 次模型试验，每次最多 100 个 epoch。

最终参考使用两层、NB 似然的 scVI，最多训练 400 个 epoch并早停；scANVI 从 scVI 初始化，再训练 15 个 epoch。代码笔记本与这些设置一致。

模型选择并不只看一个综合分数。小鼠中 scGen 的综合指标最高，但其二维表示产生不连通群体，轨迹不符合连续胚胎发育。因此作者选择更能保留发育结构的 scVI/scANVI。

### 第三步：分类细胞类型

作者比较两条路线：

1. scANVI 直接输出每个细胞属于各发育类型的概率；
2. 从 scVI、scANVI 或 scGen 解码得到去噪表达，再训练 XGBoost。

小鼠结果如下：

| 分类器 | Balanced accuracy |
|---|---:|
| 普通 scANVI | 0.650 |
| 平衡 scANVI（每类每轮 15 个细胞） | 0.880 |
| XGBoost + scVI 去噪表达 | 0.963 |
| XGBoost + scANVI 去噪表达 | 0.917 |
| XGBoost + scGen 去噪表达 | 0.917 |

XGBoost 的初始准确率最高，但对少数关键基因过度依赖：移除前 10 个 HVG 后，多个指标接近 10%。scANVI 要移除约 200 个顶级 HVG 后才明显下降。因此，scANVI 更适合做可迁移的参考模型。

平衡训练显著改善少数类别，但 E3.5 ICM 仍然异质：只有 46% 被继续预测为 E3.5 ICM，其他细胞被分配到邻近的 ICM、EPI、PrE 或少量 TE 状态。

### 第四步：用 scANVIExplainer 找出模型依据

设细胞 $i$ 的计数为 $x_i$，批次为 $b_i$，标签为 $y_i$，scANVI 潜在表示为 $z_i$。标准 DeepExplainer 不能直接处理这三个输入，也不知道分类器位于潜在空间之后。作者的 `SCANVIDeep` 做了两项修改：

1. 把 `X`、`batch` 和 `labels` 一起传给 scANVI；
2. 先计算 `model(...)["z"]`，再调用 `classifier(z)`，把类别输出的贡献反传到输入基因。

每个细胞类型的解释流程是：

1. 按该类型进行 90:10 的背景/测试划分；
2. 用背景细胞估计模型期望输出；
3. 计算测试细胞相对背景的基因贡献；
4. 重复 10 次 bootstrap；
5. 只保留 10 次都出现且贡献非负的基因；
6. 按平均 SHAP 贡献排序。

结果说明模型使用的是“组合证据”。例如小鼠中既有 *Gata3*、*Sox17*、*Spp1*，也有 *Omt2a*、*Obox8*、*Dppa3*；人类中既有 *PDGFRA*、*NODAL*、*GDF3*、角蛋白，也有 *NLRP4* 和 *OOSP2*。一些经典 marker（如小鼠 *Cdx2*、*Gata6*、*Nanog*）并没有进入最重要特征列表。

### 第五步：把新数据映射到参考

查询数据先与参考基因空间对齐，然后调用：

```text
prepare_query_anndata
-> load_query_data
-> 训练 100 epochs，weight_decay = 0
-> 输出类别概率和潜在坐标
```

预测类别是最大概率对应的类型。不确定性定义为：

$$
u_i = 1 - \max_c p_i(c).
$$

论文称其为 entropy，但代码表明它不是 Shannon entropy，而是“1 减去最高类别概率”。这个量直观、容易使用，但不是严格校准的分布外检测分数。

作者用参考模型分析了三类新数据：

- 小鼠 ES 细胞向 PrE 分化：Hhex 阳性群体主要映射到 PrE，Sox2 阳性群体主要保持 EPI-like；
- 人类 blastoid：能够识别 PrE 和 TE 成熟，但不确定性高于小鼠；
- 人类 8C-like 诱导：在 e4CL 和分选的 8CLC 中识别出更明显的 8C/桑椹胚倾向。

### 如何理解这篇工作的价值？

最有价值的不是某个单一准确率，而是四个层次同时存在：

1. scVI 提供跨批次潜在空间；
2. scANVI 提供可迁移的概率标签；
3. 平衡训练保护稀有发育类别；
4. scANVIExplainer 把黑箱预测转化为稳定的基因组合证据。

同时，作者用发育轨迹是否合理来约束模型选择，避免只追求综合指标。

### 局限与复现性

- 人类数据量小且类别极不平衡，参考不一定覆盖真正的新细胞类型。
- PAGA 和伪时间只能支持结构一致性，不能证明因果谱系。
- 只使用 HVG，未被选择的基因无法直接贡献分类。
- 论文没有写出 scVI/scANVI 的完整目标函数，需要参考原始方法和 scvi-tools。
- 本地代码与核心流程高度对应，但仓库以 Jupyter 笔记本为主，没有自动化测试和单一入口。
- 原始数据、处理后的 AnnData、训练模型、nf-core 实现、网页 portal 和后续 `scanvi-explainer` 包分散在外部资源中。

因此，这个代码快照适合核对方法和复用局部模块，但要完整重跑全部图表，仍需重建环境、下载外部数据并手动串联笔记本。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Deep-Learning Models for Preimplantation Mouse and Human Embryos

### Overview

Proks, Salehin, and Brickman assemble a dynamic scRNA-seq reference for mouse and human preimplantation development. The resource integrates many small, heterogeneous embryo datasets, learns developmental cell states, explains which genes support each predicted identity, and transfers the reference to in-vitro embryo and stem-cell systems. It was published in *Nature Methods* in 2025 (DOI `10.1038/s41592-024-02511-3`).

The key problem is unusually hard: embryo material is scarce, human samples are ethically and technically difficult to obtain, studies use different sequencing technologies and depths, cell labels are inconsistent, and human data are strongly imbalanced toward trophectoderm. Traditional linear integration may not capture dynamic developmental structure; manual annotation depends on expert-selected markers; and neural integration models are difficult to interpret.

### What the resource does

The authors curate 13 mouse and six human in-vivo datasets, reprocess reads through nf-core workflows, harmonize annotations, normalize full-length SMART-seq counts by gene length, and select 3,000 HVGs. They compare PCA, scVI, scANVI, and scGen integration, using both scIB-style metrics and developmental-trajectory sanity checks. The final workflow uses scVI for integration and scANVI for semi-supervised classification.

Two classifier routes are evaluated:

- scANVI, including a balanced version that samples 15 cells per class in each training epoch;
- XGBoost trained on denoised expression decoded by scVI, scANVI, or scGen.

The paper’s custom methodological component is `scANVIExplainer`, an adaptation of SHAP DeepExplainer/DeepLIFT that accepts scANVI’s count, batch, and label inputs, passes contributions through latent $Z$ and the classifier, and retains genes with recurrent positive contributions across ten bootstrap runs.

For a new query dataset, the reference is adapted for 100 epochs with zero weight decay. Each cell receives a maximum-probability label and an uncertainty score

$$
u_i = 1 - \max_c p_i(c).
$$

The paper calls this entropy, but the released code confirms that it is maximum-probability uncertainty rather than Shannon entropy.

### Main findings

- The final mouse reference contains 2,004 cells and 34,346 genes; the human reference is more difficult because 55% of cells were originally labeled TE and several early/intermediate labels are ambiguous.
- scGen has the best aggregate mouse integration score but creates disconnected developmental groups, so the authors reject a metric-only choice and favor scVI/scANVI for more plausible developmental geometry.
- On mouse, XGBoost on scVI-denoised expression has the highest reported balanced accuracy (0.963). Ordinary scANVI is lower (0.650), while balanced `n=15` scANVI improves to 0.880.
- Balanced scANVI improves rare-stage prediction but E3.5 ICM remains heterogeneous: only 46% is retained as E3.5 ICM.
- XGBoost is highly brittle to missing top features: removing ten top HVGs reduces performance to near 10%. scANVI remains robust until roughly 200 top HVGs are removed.
- The human classifier reassigns some previously labeled ICM cells toward TE, supported by their location and expression of GATA3 rather than ICM/EPI/PrE markers.
- scANVIExplainer recovers canonical markers such as *Gata3*, *Sox17*, *PDGFRA*, *NODAL*, and *GDF3*, but also prioritizes less conventional predictors including *Omt2a*, *Obox8*, *Dppa3*, *NLRP4*, and *OOSP2*.
- Query transfer produces biologically plausible labels for mouse PrE differentiation, human blastoids, induced 8C-like cells, and an E12/E14 extension of the human model. Human blastoid predictions are visibly less certain than the mouse differentiation example.

### What is genuinely new

The paper does not introduce scVI, scANVI, scGen, XGBoost, or SHAP. Its novelty lies in their embryo-specific integration into a maintained resource, the balanced training strategy for scarce classes, the custom scANVI explanation interface, and the use of developmental topology—not only aggregate benchmark scores—to select a reference representation.

### Limitations

- Ground-truth labels inherit historical annotation choices and may contain errors.
- Rare and imbalanced human classes remain difficult, and the available cells may not span genuinely new states.
- PAGA and pseudotime recover broad structure but also produce biologically questionable ordering, especially for TE and human terminal states.
- Only HVGs are modeled; the authors argue full-genome integration adds little, but omitted genes cannot contribute directly.
- Maximum-probability uncertainty is useful but is not a formal or calibrated out-of-distribution detector.
- The paper provides no explicit scVI/scANVI objective equations and contains a few source ambiguities, including mouse filtering thresholds and test-set wording.
- Experimental validation is insufficient to guarantee correct identification of novel cell types.

### Reproducibility

**Reproducibility rating: 3/5.**

The primary GitHub snapshot matches the main computational story: scVI/scANVI settings, autotuning, XGBoost training, the custom `SCANVIDeep` implementation, query adaptation, and many saved notebook outputs are present. The code-paper fidelity is medium overall and high for the central reusable functions.

End-to-end reproduction is nevertheless nontrivial. The repository is notebook-led, contains no automated test suite or single execution command, and depends on external raw/processed datasets, Hugging Face models, nf-core pipelines, a separate preprocessing fork, a separate portal repository, and a later formalized `scanvi-explainer` package. The frozen snapshot is therefore well suited to method verification and targeted reuse, but not turnkey figure reproduction.

### Bottom line

This is a useful developmental reference because it combines batch-aware latent modeling, probabilistic transferable annotation, rare-class balancing, trajectory checks, and gene-level explanations. Its strongest lesson is methodological: for scarce developmental data, a model should be selected not only by integration metrics or classifier accuracy, but also by robustness, interpretable features, and preservation of plausible biological geometry.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
