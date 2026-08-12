---
layout: default
permalink: /paper-atlas/sotmgf-aa034768/
title: "SOTMGF"
nav: false
description: "SOTMGF 面向空间转录组、空间蛋白组以及推断得到的空间表观组数据。它认为仅用表达或物理邻接会漏掉两类信息：一个 spot 周围的细胞组成，以及分子之间的条件关联。方法因此把同一批空间观测表示成多个“视图图”，分别学习表示，再以注意力和自训练聚类融合。 输出是每个 spot/细胞的低维表示与预先指定数量的空间域。论文还在这些域上做空间伪表达（SPE）去噪、暗基因/暗蛋白发现、RNA velocity、配体–受体、转录因子和生存分析；"
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
      <span>Domain Clustering</span>
      <span>Advanced Science · 2026</span>
    </div>
    <h1>SOTMGF</h1>
    <p>Combining Spatial Multi-Omics Data to Decipher Spatial Domains and Elucidate Cell Heterogeneity Based on Self-Supervised Graph Learning</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1002/advs.75533" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SOTMGF：把空间多组学拆成多个图，再用伪标签循环融合

### 方法解决什么问题

SOTMGF 面向空间转录组、空间蛋白组以及推断得到的空间表观组数据。它认为仅用表达或物理邻接会漏掉两类信息：一个 spot 周围的细胞组成，以及分子之间的条件关联。方法因此把同一批空间观测表示成多个“视图图”，分别学习表示，再以注意力和自训练聚类融合。

输出是每个 spot/细胞的低维表示与预先指定数量的空间域。论文还在这些域上做空间伪表达（SPE）去噪、暗基因/暗蛋白发现、RNA velocity、配体–受体、转录因子和生存分析；这些是依赖域与嵌入的下游分析，不都属于核心训练代码。

### 全流程

```text
表达矩阵 + 坐标 + 细胞组成 + 分子关联矩阵
       │
       ├─ DAEGC 图注意力预聚类 → 初始伪标签
       ├─ Transformer 表达重构/聚类 → 稠密表达特征
       │
       ├─ SLG：纯空间邻接
       ├─ SLG-C：按伪标签剪枝的空间邻接
       ├─ MEG：细胞组成直方图的 EMD 微环境图
       └─ GAG：条件分子关联图
               │
         每个视图的 AE+GCN 多尺度融合
               │
         软 KL + 高置信伪标签硬监督
               │
         四视图注意力融合 → 新伪标签
               └───────────────循环更新
```

### 1. 预聚类：DAEGC

论文先用共享近邻/半径空间图与细胞类型组成做 DAEGC。两层图注意力编码器为邻居分配权重，内积解码器重构邻接矩阵。嵌入与簇中心之间用 Student-t 分布形成软分配 $Q$，再构造强化的目标分布 $P$；KL 散度推动高置信分配进一步变尖。代码中的典型目标是图重构 BCE 加 $50\,KL(P\|Q)$。

这一步所需的细胞组成并非仓库内端到端生成：DLPFC 等脚本直接读取 CARD 结果 CSV。因此“细胞类型感知”依赖外部 R 流程和参考数据。

### 2. Transformer 表达潜表示

原始表达经过总量归一化、`log1p`、高变特征选择与标准化后进入 Transformer 编码–解码器，并同时接受聚类伪标签约束。论文意图是把稀疏表达变成稠密潜表示。

实现有重要边界。`d_model` 实际等于输入特征维数，1024 是 feed-forward 层宽度，不应写成“Transformer 表示维度 1024”。代码默认 `batch_first=False`，却把输入变成 `(batch, 1, features)`；PyTorch 会把第一维解释为序列长度、第二维解释为 batch，因此注意力在当前数据批中的样本之间计算，而不是在单个样本的一维 token 序列内部。解码器查询还是新生成的随机张量，并被强制 `.cuda()`，所以 CPU 路径不可运行且每次前向含额外随机性。

### 3. 四个视图如何构造

- **SLG**：半径内的空间邻边。
- **SLG-C**：如果两个相邻点的预聚类标签不同，就删除该边。它能强化域内连续性，也可能把早期错误伪标签固化到图结构中。
- **MEG**：统计每个点邻域的细胞类型频率，以 PAGA 拓扑引导的 ground distance 和 Earth Mover's Distance 比较微环境，再构图。
- **GAG**：利用逐细胞/spot 的条件分子关联矩阵。仓库主要读取预计算的 c-CSN/CCSN CSV，并未提供完整通用的关联矩阵生成管线。

这四个视图并非完全由一次 Python 调用获得。CARD、CCSN、部分 Tangram 映射和数据整理都是外部或预计算依赖。

### 4. 每个视图的 DAGC

每个图视图进入结合自编码器与图卷积的 SDCN/DAGC。代码包含三类融合：

1. HWF 在每一层融合自编码器隐藏状态与 GCN 状态；
2. SWF 将多个深度的表示与 AE latent 重新加权；
3. DWF 融合图分支的类别分布与 Student-t 聚类分布。

软监督通过 $KL(P,Q)$、$KL(P,Z)$ 及分布一致性项约束；硬监督只选择阈值 0.7 以上的伪标签，用 BCE/交叉熵推动分类。伪标签来自模型自身前一轮聚类，因此这是循环自训练，不是外部真值监督。它能逐步锐化结构，也存在确认偏差风险。

### 5. 多视图融合与循环

四个视图各自产生表示/分布，注意力模块拼接并加权，再经图层得到最终表示和标签。主数据脚本把新的 `label_tem` 回灌到下一轮的图剪枝、簇中心初始化和训练。论文强调“统一优化”，但仓库实际是多个脚本阶段与外层循环串联，包含预训练文件、CSV 中间件和数据集专用超参数，不是单一可配置模型对象。

### 论文七张主图怎样读

- Fig. 1 给出五模块架构、四视图以及模拟数据消融。图中 SOTMGF 在多数指标领先，但部分消融并非所有指标都严格单调改善。
- Fig. 2 比较模拟双/三模态与小鼠脾数据；显示空间域、指标和去噪效果。
- Fig. 3 在 DLPFC 展示与人工皮层层标注的对比、指标、旋转实验、轨迹和分子关联变化。
- Fig. 4 在乳腺癌 ST+SP 中展示联合域、mRNA–蛋白差异、SDG/SDP、通路图与生存关联。生存 p 值属于候选关联，不是临床验证。
- Fig. 5 在发育小鼠脑展示空间域、RNA velocity 和分化相关分子网络。
- Fig. 6 在 IDC 中展示肿瘤边界、差异基因和 CHEMERIN 等细胞通讯；配体–受体分析是下游推断。
- Fig. 7 把 MERFISH RNA 与 SHARE-seq RNA/ATAC 经 Tangram 对齐，展示推断空间 ATAC 与暗基因；空间 ATAC 是计算映射结果，不是同一切片直接测量。

### 代码保真度与关键缺陷

整体保真度评为 **中等**。核心 DAEGC、Transformer、四视图思想、AE/GCN 融合、软硬自监督和外层伪标签循环都能定位，但公开代码更像研究快照而非可复用包。

关键证据边界包括：

- `model.py` 的第四视图分支在融合时错误复用第三视图的 `z1_3`–`z4_3`，所以 GAG 视图并非论文描述的完全独立处理。
- Transformer 和多处训练代码硬编码 `.cuda()`；CPU fallback 只存在于部分入口表面。
- Transformer 解码器使用随机 query；论文没有说明这种随机解码机制。
- 注意力权重多处使用 L2 归一化而不是和为 1 的 softmax，不能直接解释成概率权重。
- SPE 的“15 近邻伪表达”没有在核心 Python 路径中找到完整实现。
- 主脚本依赖绝对本机路径、外部 CARD/c-CSN/Tangram 产物以及数据集专用轮数，缺少统一 CLI、测试和下载流程。
- 预聚类训练用真实标签计算 NMI/ACC 并按验证 ACC 保存“最佳”模型的替代路径存在于 `model_EDC.py`；核心论文宣称无监督时，应避免把这些评估变量误解为训练必需真值，但代码研究流程存在评测耦合。

### 复现结论

仓库 `.repo_source` 记录提交 `a1fea6d7cfb51e1f27873ffd7dedf0ccbc20b31e`，提供模型文件、多个数据集脚本、基线和若干预计算数据。它足以核对论文机制并复跑部分作者环境，但不足以从原始公开数据一键生成全部七张图。对新数据应用时，必须先补齐细胞组成与分子关联视图、修复第四视图变量错误、消除硬编码 CUDA/路径，并明确域数量与各阶段超参数。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SOTMGF: Self-Supervised Multi-View Graph Fusion for Spatial Multi-Omics

SOTMGF integrates molecular expression, physical proximity, inferred cellular microenvironment, and molecular-association information for spatial-domain clustering. Its staged self-training workflow combines DAEGC preclustering, Transformer-based expression representation, four graph views (spatial, pseudo-label-pruned spatial, microenvironment EMD, and association), per-view AE/GCN fusion, soft KL supervision, hard high-confidence pseudo-label supervision, and attention-based view fusion. Updated pseudo-labels feed the next outer iteration.

The paper evaluates simulated dual/tri-modal data, paired spatial transcriptome/proteome mouse tissues, 12 DLPFC slices, kidney, developing mouse brain, invasive ductal carcinoma, and a computational MERFISH–SHARE-seq integration. Seven main figures support strong domain metrics in the shown benchmarks and use learned domains for dark gene/protein discovery, RNA velocity, ligand–receptor analysis, TF prediction, and survival associations. These downstream results are hypothesis-generating: inferred spatial ATAC is Tangram-mapped rather than directly measured in the same tissue, and biomarker/survival associations lack independent clinical validation.

The GitHub snapshot (`a1fea6d7cfb51e1f27873ffd7dedf0ccbc20b31e`) contains the central model and dataset scripts but has **medium** paper-code fidelity and low turnkey reproducibility. CARD cell compositions, c-CSN association matrices, and some Tangram products are external/precomputed; the SPE 15-neighbor reconstruction was not found as a complete core path. The fourth graph-view branch reuses third-view intermediate tensors, Transformer decoding uses random CUDA-only queries, multiple scripts hard-code CUDA and local absolute paths, and the repository lacks a unified configuration/CLI and automated tests. It is a traceable research snapshot rather than an end-to-end package.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
