---
layout: default
permalink: /paper-atlas/deepdetails-8ad1372a/
title: "DeepDETAILS"
nav: false
description: "组织 bulk 测序把多个细胞类型的调控信号混在一起；而 PRO-cap、PRO-seq 与多种 ChIP-seq 往往没有可直接用于监督训练的单细胞真值。DeepDETAILS 用同类组织的 scATAC-seq/snATAC-seq 作为参考，把一个 bulk 信号分解为各细胞类型的碱基分辨率轨迹。训练时并不知道每个细胞类型的真实输出，只要求所有预测分支之和拟合 bulk 观测，因此是“准监督”而非普通监督学习。"
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
      <span>Deconvolution</span>
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>DeepDETAILS</h1>
    <p>High-resolution reconstruction of cell-type-specific transcriptional regulatory processes from bulk sequencing samples</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DeepDETAILS：从 bulk 调控组学信号中恢复细胞类型特异轨迹

### 它解决什么问题？

组织 bulk 测序把多个细胞类型的调控信号混在一起；而 PRO-cap、PRO-seq 与多种 ChIP-seq 往往没有可直接用于监督训练的单细胞真值。DeepDETAILS 用同类组织的 scATAC-seq/snATAC-seq 作为参考，把一个 bulk 信号分解为各细胞类型的碱基分辨率轨迹。训练时并不知道每个细胞类型的真实输出，只要求所有预测分支之和拟合 bulk 观测，因此是“准监督”而非普通监督学习（`paper.md:39-56,222-249`）。

已有统计去卷积通常需要同模态参考或多个 bulk 样本；本文在跨模态场景中与 BayesPrism、CIBERSORTx、BLADE、DSA 比较。Puffin-D 和 Enformer 是有细胞类型真值监督的序列预测基线；论文将它们用于不同任务对照（`paper.md:85-108`）。

### 输入、输出与核心想法

输入包括：

- 4,096 bp 的 DNA 序列；
- 每个细胞类型的 sc/snATAC 伪 bulk 可及性轨迹；
- 待分解的 bulk 链特异信号及候选区域。

输出是 $K$ 个细胞类型的预测轨迹，$K$ 为参考中的细胞类型数；把它们相加得到 bulk 重建。每个分支不直接预测一条任意曲线，而是预测“形状 × 总量”：位置 logits 经 softmax 变成形状，count 经 softplus 变成非负幅度，二者相乘（`paper.md:225-229`; `model/deconvolution.py:7-53`）。

```text
DNA 序列 ──> 共享 CNN 特征 ──> 每个细胞类型的门控分支 ──> shape × count
sc/snATAC ──> (fused 模式：共享 GRU 特征) ────────────────────────┘
                                    │
每个细胞类型的可及性比例 ────────────> 缩放 ─> 分支信号相加 ─> bulk 预测
                                                           │
bulk RMSLE + 分支相关性惩罚 <───────────────────────────────┘
```

### 可及性约束和损失

论文对细胞类型 $k$、区域 $r$ 定义固定缩放：

$$s(k,r)=\frac{\mathrm{RPM}(k,r)}{\sum_{i=1}^{K}\mathrm{RPM}(i,r)+\epsilon}.$$

这里 RPM 是中心 1 kb 的深度标准化 ATAC 信号，$\epsilon=10^{-16}$；不可及区域的分支不会贡献输出（`paper.md:231-237`）。代码把名为 `per_cluster_load` 的值作为 `cluster_weights` 使用并支持 early/late/late-ch 位置（`model/deconvolution.py:250-282`），但本工作区尚未证明所有数据路径中它都严格等于上述 RPM 比例，所以这一对应关系应保持 **Partial**。

训练最小化 bulk 重建 RMSLE，并惩罚不同分支预测之间过高的相关性，以避免多个分支学成相同信号（`paper.md:240-246`）。源码先将每个分支的 shape 和 count 相乘、再对分支求和（`helper/utils.py:216-249`），随后在 `training_step` 中计算 RMSLE 和非对角相关性惩罚（`model/wrapper.py:139-172`）。若 HDF5 带有 prior，代码还会加一个 `prior_loss`；这是真实代码行为，但主文公式没有说明它与论文惩罚项相同。

### 两种模式与实际流程

**fused**（默认）把 GRU 编码的可及性与序列特征结合，面向定量去卷积；**seq-only** 主要依靠序列与缩放约束，便于做 motif/input×gradient 解释（`paper.md:252-255`）。Fig. 1 的本地图像可见这三类输入、分支 shape/count 输出以及 seq-only/fused 归因轨迹；Fig. 3 显示与监督模型、统计方法的比较。

使用时先运行 `deepdetails prep-data`：按标签汇总 ATAC、读入 bulk track、生成 HDF5；再用 `deepdetails deconv` 训练；`build-bw` 导出 bigWig（`paper.md:264-280`; `cli.py:276-346`）。预检会估计 bulk 中的细胞类型并默认排除低于 3.5% 的参考细胞类型，CLI 默认值为 `0.035`（`paper.md:300-303`; `cli.py:156-177`）。

### 如何理解验证与边界

论文在模拟 PRO-cap/PRO-seq 和组蛋白修饰任务上报告与 Puffin-D/Enformer 接近的相关性，并报告对统计方法更高的跨模态 CCC（`paper.md:85-108`）；Fig. 4 图像还直接展示了测序深度、细胞类型数、参考不匹配和预检情形。资源层面覆盖 20 个器官、39 个组织、86 个细胞类型（`paper.md:143-160`）。

本快照可核证核心模型、训练、命令行和预检，但 `protocols.py:16` 导入的 `deepdetails.helper.attr` 文件不存在，因此普通 `protocols` 导入和 attribution 实现是 **MISSING**，不应声称端到端可复现。补充材料只有 PDF/XLSX；可逐行引用的 supplementary Markdown 为 **Not found**。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DeepDETAILS: bulk-to-cell-type regulatory deconvolution

### Problem and contribution

Bulk regulatory assays average signals across cell types, while many assays remain difficult to collect at single-cell resolution. DeepDETAILS reconstructs base-pair-resolution, cell-type-specific transcription-initiation or histone-modification tracks from a bulk assay plus matched scATAC/snATAC reference accessibility and DNA sequence (`paper.md:30,39-56`). It trains quasisupervisedly: latent branch tracks must sum to the observed bulk track rather than match unobserved per-cell-type targets.

The method combines a shared sequence encoder with $K$ cell-type branches, accessibility scaling, shape-and-count heads, bulk RMSLE reconstruction and a cross-branch redundancy penalty (`paper.md:222-249`). The fused default additionally uses GRU-encoded accessibility; seq-only is positioned for cleaner motif attribution.

### Evaluation and results

The paper evaluates simulated bulk PRO-cap/PRO-seq and histone ChIP-seq, comparing with supervised Puffin-D/Enformer and statistical BayesPrism, CIBERSORTx, BLADE and DSA (`paper.md:68-108`). At 128-bp resolution it reports DeepDETAILS Pearson $r$ of 0.704, 0.730 and 0.767 for initiation, pause–release and histone modification; it also reports $r=0.800$ for dominant TSSs and $r=0.837$ for pause sites (`paper.md:85-96`). Fig. 3 visibly supports the comparative layout, and Fig. 4 directly shows the tested depth, cell-number, unmatched-reference and preflight regimes.

The resulting resource covers 20 organs, 39 tissues and 86 cell types, with transcription-initiation and histone-mark maps (`paper.md:143-160`). Fig. 5 shows the tissue/assay coverage and trait-enrichment examples; Fig. 6 visualizes a macrophage-associated PSC candidate at rs5757584/PDGFB. These are paper interpretations, not independent causal validation in this workspace.

### Reproducibility assessment

**Medium fidelity.** The acquired GitHub snapshot at `d1bc71ac83478f1ec2d77b02ac1acd9030f6e6a1` directly implements core branch heads, fused/seq-only selection, aggregation, training objective, CLI and preflight. It does not fully reproduce the paper: `deepdetails.helper.attr` is absent despite being imported by `protocols.py`, making ordinary `protocols` import and attribution **MISSING** from this snapshot. The paper also links a separate `DeepDETAILS-analysis` result-generation repository that was not acquired. Supplementary files are available as PDF/XLSX, but supplementary Markdown is **Not found**. These gaps should be resolved before claiming an end-to-end reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
