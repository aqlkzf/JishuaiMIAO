---
layout: default
permalink: /paper-atlas/sphenic-ec6fb59e/
title: "SPHENIC"
nav: false
wide: true
description: "空间转录组的空间域识别需要同时满足两件事：同一区域的 spots 在表达上相似，并且在组织切片上连续。普通表达聚类可能切断相邻组织；GCN 能利用邻接图，却主要依赖局部边，少量错误边也可能传播噪声。SPHENIC 的设想是用扩展持久同调提取跨尺度拓扑，再用空间约束显式修正最终嵌入。 这里分析的是测量 spot，而不是逐细胞真值。"
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
      <span>Domain Clustering</span>
      <span>arXiv · 2025</span>
    </div>
    <h1>SPHENIC</h1>
    <p>SPHENIC: Topology-Aware Multi-View Clustering for Spatial Transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SPHENIC：用持久同调增强空间转录组分区

### 1. 它要解决什么问题

空间转录组的空间域识别需要同时满足两件事：同一区域的 spots 在表达上相似，并且在组织切片上连续。普通表达聚类可能切断相邻组织；GCN 能利用邻接图，却主要依赖局部边，少量错误边也可能传播噪声。SPHENIC 的设想是用扩展持久同调提取跨尺度拓扑，再用空间约束显式修正最终嵌入。

这里分析的是测量 spot，而不是逐细胞真值。输入为表达矩阵 $X\in\mathbb R^{N\times G}$ 和坐标 $S\in\mathbb R^{N\times2}$，输出为每个 spot 的低维表示 $Z\in\mathbb R^{N\times d}$，之后再聚类为空间域。

### 2. 两张图与过滤序列

论文构造空间图 $G_s$ 与表达图 $G_x$。空间图来自坐标欧氏距离；表达图连接表达相似的 spots。对表达视图，论文还要求候选边的空间距离不超过固定半径 $r$：

$$
E_x^\epsilon=\{(u,v)\mid \omega_x(u,v)\le\epsilon,\ \omega_s(u,v)\le r\}.
$$

逐渐放宽阈值 $\epsilon$ 会得到嵌套子图序列。直观上，先出现的是最相似的局部连接，之后图逐渐连通并产生或填平环。遗憾的是，论文没有说明两张基础图究竟使用 kNN、半径图还是其他规则，也没有给出 $r$。

### 3. 从 EPH 到可训练的图像

扩展持久同调记录每个连通分量或环的出生和死亡阈值 $(b_k,d_k)$。生命周期 $|d_k-b_k|$ 较长的结构被视为稳定拓扑，短寿命结构更可能是噪声。论文用：

$$
w(\mu_k)=|d_k-b_k|^\theta
$$

给持久点加权，再以高斯核投影到规则网格，形成 Extended Persistence Image（EPI）。二维卷积、ReLU 和池化进一步把 EPI 编码成 EPE 特征。

该分支的概念是“不要只看某一张静态图，而要看图结构随阈值变化时哪些模式长期存在”。但论文没有给出同调维度、$\theta$、高斯带宽、网格大小、卷积核和步长，也没有说明使用哪个 EPH 软件库。

### 4. 多视图 GCN

空间图和表达图各自经过带独立参数的 GCN，得到 $Z_s$ 与 $Z_x$。另一个 Co-GCN 在两张图上共享参数，产生 $Z_{co,s}$ 与 $Z_{co,x}$，然后简单取平均：

$$
Z_{co}=\frac{Z_{co,s}+Z_{co,x}}{2}.
$$

论文还比较两个共识视图的归一化 Gram 矩阵，使两种模态保留相近的 spot–spot 关系。最终，EPE、两个单视图 GCN 和 Co-GCN 经注意力与 MLP 融合为 $Z$。

这里有一个未解决的维度问题：论文的 EPI/EPE 看起来是每个模态的一张全局持久图像，而 GCN 输出是每个 spot 一行的 $N\times d$ 矩阵。Eq. 10 直接相加两者，却没有解释 EPE 如何获得 spot 维度。因此不能仅凭论文重建这一接口。

### 5. DualRO 的三项损失

总目标为：

$$
\mathcal L_f=\mathcal L_{rec}+\lambda_1\mathcal L_{con}+\lambda_2\mathcal L_{sco}.
$$

- $\mathcal L_{rec}$：三层 MLP 从 $Z$ 估计 ZINB 的零膨胀概率、均值和离散度，以负对数似然重构原始表达。
- $\mathcal L_{con}$：对齐空间与表达 Co-GCN 的 spot–spot Gram 矩阵。
- $\mathcal L_{sco}$：设计意图是拉近空间邻居、推远非邻居。

但空间损失的书面公式存在逻辑缺口：外层只对 $j\in\mathcal N_i$ 求和，同时定义 $y_{ij}=1$ 当 $j\in\mathcal N_i$。所以所有实际进入求和的 pair 都有 $y_{ij}=1$，乘以 $(1-y_{ij})$ 的负样本项恒为零。若实现确实包含非邻居，它必然使用了论文没有写出的采样集合或不同求和域。没有代码时不能替作者补齐。

另一个疑点是论文把 $\sigma$ 明确称为 tanh。由于 tanh 可为负，而公式随后对含 $\sigma(S_{ij})$ 的量取对数，某些余弦相似度下可能没有定义。实际实现是否使用 sigmoid、平移后的 tanh 或数值截断均为 Not found。

### 6. 如何得到空间域

论文只说“对最终 $Z$ 进行聚类”，没有写 k-means、mclust、Leiden 或其他算法，也没有说明如何选择域数。因此旧文档中“最终使用 k-means”只能算推测，不能作为方法事实。

### 7. 实验应该怎样读

Table 1 汇总 HBC、MBA 和九个 DLPFC 切片。SPHENIC 平均 ARI 56.52、NMI 67.30。HBC 的 ARI 为 68.23，对比 Spatial-MGCN 的 64.04；MBA 为 48.79，对比 Scanpy 的 39.65。论文称提升 4.19% 和 9.14%，但这两个数字是直接相减得到的**百分点差**，不是相对百分比。

Table 2 支持 Topo 与 DualRO 都有贡献，但正文与表格并非完全一致。以 151507 为例，full 65.33、Topo-only 59.92、DualRO-only 62.03、baseline 53.22，因此：移除 DualRO 的下降是 5.41 点，不是正文的 5.61；full 相对 baseline 是 12.11 点，不是正文的 6.93。

Figure 3 的 HBC 结果显示 SPHENIC 与标注有较高一致性，但“专家级识别”是作者解释，并非独立病理专家验证。Figure 5 的 ARI/NMI 随训练阶段上升，阶段图是四个离散快照，不能证明每个 epoch 都单调改善。

### 8. 五幅主图

- 图 1：静态边表示与过滤拓扑表示的概念对照；它说明动机，不是噪声鲁棒性的定量实验。
- 图 2：完整架构图，确认 EPH、双 GCN、注意力、ZINB 与空间约束的组合，但没有解决张量维度和采样细节。
- 图 3：HBC 手工标注、九种方法的空间结果与 UMAP；支持该数据集上的相对性能。
- 图 4：$\lambda_1,\lambda_2$ 从 $10^{-3}$ 到 $10^3$ 的敏感性；稳定区主要是作者声称的 $10^{-3}$ 至 $10^{-1}$，不能据此指定未经报告的默认值。
- 图 5：0%、33%、67%、100% 训练快照，ARI 0.4253 到 0.6823；只能说明这四个检查点逐步改善。

### 9. 可复现性结论

缺失项包括预处理、图构造、EPH 参数、网络层数与维度、优化器、学习率、随机种子、运行次数、负样本策略及最终聚类。

因此可复现性为 **2/5**：数据集入口和整体数学框架可见，但完整重实现仍需要大量不可验证的选择。所有实现层面的结论都应标记 `Not found`，不能把合理猜测改写成作者代码行为。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SPHENIC Summary

### Answer First

SPHENIC is a 2025 arXiv paper proposing topology-aware spatial-domain clustering for spatial transcriptomics. It combines two graph views (physical coordinates and gene expression), extended persistent homology (EPH), modality-specific and shared GCNs, attention fusion, ZINB reconstruction, cross-view consistency and a spatial-coherence loss. On 11 reported slices it has the highest average ARI (56.52) and NMI (67.30) in Table 1.

The method is promising but not independently reproducible from this workspace. No implementation or supplement is available locally, graph construction and many architecture parameters are unspecified, and several equations leave dimensional or sampling ambiguities. The paper-only fidelity status is therefore **Not found / unverifiable**, not an implementation match.

### Method

Input consists of an $N\times G$ expression matrix and $N\times2$ spot coordinates. A spatial graph and an expression graph are constructed. For each view, an edge-threshold filtration yields an extended persistence diagram; long-lived birth–death pairs are rendered into a persistence image and encoded by a 2D convolution. In parallel, view-specific GCNs learn $Z_s$ and $Z_x$, while a parameter-shared co-GCN learns view embeddings whose mean is $Z_{co}$. Attention and an MLP fuse topological and graph features into final spot embeddings $Z$.

Training minimizes:

$$
\mathcal L_f=\mathcal L_{rec}+\lambda_1\mathcal L_{con}+\lambda_2\mathcal L_{sco},
$$

where ZINB reconstruction models sparse counts, a Gram-matrix loss aligns co-GCN views, and the spatial term is intended to attract neighboring spots and repel non-neighbors.

### Reported evaluation

The paper evaluates HBC, mouse brain anterior and nine DLPFC slices against eight baselines. Average reported SPHENIC performance is ARI 56.52 and NMI 67.30. HBC ARI is 68.23 versus 64.04 for Spatial-MGCN; MBA is 48.79 versus 39.65 for Scanpy. These are differences of 4.19 and 9.14 ARI **percentage points**, respectively, not relative improvements of 4.19% and 9.14%.

Ablations on HBC and DLPFC-151507 support both components. Removing topology from the full model reduces ARI by 4.84 and 3.30 points; removing DualRO reduces it by 10.24 and 5.41 points based on Table 2 (the prose reports 5.61 for the latter, which conflicts with 65.33−59.92=5.41). The full model exceeds the version without both modules by 15.34 and 12.11 points according to the table; the prose's 6.93 for 151507 is inconsistent with its own values.

### Critical evidence boundaries

- Eq. 11 sums only over $j\in\mathcal N_i$, so $y_{ij}=1$ for every included pair and the written non-neighbor term is never active. A negative-sampling domain is missing from the formula.
- EPI/EPE is described as one persistence image per modality, while final $Z$ is one vector per spot. The paper does not explain how image features acquire an $N$ axis before addition to GCN embeddings in Eq. 10.
- Attention for EPE is defined in Eq. 9, but weights for view-specific GCNs and the co-embedding in Eq. 10 are not defined.
- Graph construction, preprocessing, EPH dimensions/parameters, GCN depth, hidden size, optimizer, learning rate, number of runs and final clustering algorithm are not specified.
- The text names DLPFC slice “151569,” which is absent from Table 1; the 3.90-point comparison matches slice 151669 and is likely a typo.
- Scalability, EPI sensitivity and gene-enhancement evidence are deferred to supplementary material that is not present in this workspace.

### Reproducibility

Rating: **2/5**. The paper supplies public dataset names, PyTorch 2.1.0, CUDA 12.1, one 48-GB vGPU and 100 training epochs. Those details are insufficient to reconstruct the model or verify its reported results without code and the missing supplement.

### Evidence pointers

- Paper: `paper source/paper/vlm/paper.md`
- PDF: `paper.pdf`
- Figures: `paper source/paper/vlm/images/`
- Equation-level method notes: `doc_method.md`
- Missing-code assessment: `doc_code.md`

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
