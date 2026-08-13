---
layout: default
permalink: /paper-atlas/flag-52db4fbf/
title: "FLAG"
nav: false
description: "FLAG 的核心不是“把空间图也一起生成”，而是把空间图变成稳定条件，把生成难题集中在基因表达上，再用 GFM embedding 约束基因结构。论文证据支持它在结构保真度上的优势；代码则实现了核心 graph-conditioned DiT 与 GFM 对齐损失，但预处理、结构指标和完整复现实验仍需要外部脚本/数据。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>arXiv · 2026</span>
    </div>
    <h1>FLAG</h1>
    <p>FLAG: Foundation model representation with Latent diffusion Alignment via Graph for spatial gene expression prediction</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/darkflash03/FLAG" target="_blank" rel="noopener noreferrer" aria-label="Open code for FLAG">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## FLAG 方法中文解读

### 1. 这篇论文要解决什么问题？

FLAG 研究的是：给定常规 H&E 全切片图像（WSI），预测空间转录组（spatial transcriptomics, ST）中每个空间 spot 的基因表达。论文把每个 spot 表示为三类信息：二维空间坐标 $u_s\in\mathbb{R}^2$、由病理图像编码器得到的图像特征 $v_s\in\mathbb{R}^{d_v}$、以及高维基因表达向量 $x_s\in\mathbb{R}^G$；目标是从 WSI 特征、坐标和图结构中预测所有 spot 的表达向量（`paper.md:61`）。

论文认为，只看逐基因的 MSE/PCC 不够。许多模型能拟合每个基因的数值，却可能破坏两个重要结构：

- **基因-基因结构**：共表达、调控模块、通路相关性；
- **基因-空间结构**：一个基因在组织上的空间自相关、组织区域边界和空间纹理。

因此论文提出了两个结构指标：GSC（Gene Structural Correlation）衡量预测是否保留基因-基因相关矩阵，SSC（Spatial Structural Correlation）衡量预测是否保留 Moran's I 空间自相关模式（`paper.md:569-588`）。

### 2. 为什么旧思路不够？

论文先尝试一个自然方案：把 spot 表达矩阵 $\mathbf{X}$ 和 spot-spot 功能边 $\mathbf{A}$ 一起做图扩散，即学习 $p(\mathbf{X},\mathbf{A}\mid\mathcal{C})$。这里 $\mathbf{A}$ 可以是由表达相关性诱导的功能连接，条件 $\mathcal{C}$ 包括图像节点特征 $\mathbf{C}_v$ 和边条件 $\mathbf{C}_e$（`paper.md:78`）。这个方案在低维基因面板上有吸引力，因为显式边可以约束空间关系。

但论文发现 **Gene Dimension Curse（基因维度诅咒）**：当基因数 $G$ 增大时，spot-spot 相关性估计会越来越集中，一致性流形变得很薄，模型必须拟合非常尖锐的边分数场，优化难度随 $G$ 增长。论文用下面的下界概括这种额外困难（`paper.md:138-145`）：

$$
\mathcal{L}^{*}_{\mathrm{joint}}(G)-\mathcal{L}^{*}_{\mathrm{node}}\;\geq\;\Omega(G).
$$

Figure 2 和 Figure 4 的图像证据显示，联合 node-edge diffusion 在高基因维度下急剧退化，而 FLAG 曲线在大 $G$ 下仍明显更高（`figure_analysis.md`）。

### 3. FLAG 的核心思想

FLAG 不再把功能边 $\mathbf{A}$ 当作高维生成目标，而是把图变成**稳定的空间条件编码器**。最终方法可以理解为三个模块：

```text
H&E 图像 + spot 坐标
        |
        v
固定空间图 C_e = [距离核, 图像相似度]
        |
        v
Spatial Graph Encoder  --->  H_spatial
        |
        v
Graph-conditioned Gene DiT  --->  预测/生成基因表达
        |
        +-- 中间层与 GFM 基因嵌入对齐
```

#### 3.1 固定的空间边条件

论文在 Appendix G 中定义每对 spot $(i,j)$ 的边条件（`paper.md:955-972`）：

$$
w_{\text{dist}}(i,j)=\exp\left(-\frac{\|\mathbf{u}_i-\mathbf{u}_j\|_2^2}{2\sigma^2}\right),
\qquad
w_{\text{img}}(i,j)=\mathrm{CosSim}(\mathbf{v}_i,\mathbf{v}_j),
$$

$$
\mathcal{C}_{e,ij}=\big[w_{\text{dist}}(i,j),\,w_{\text{img}}(i,j)\big],
\qquad \sigma=224.
$$

代码中 `FLAG/dataset/utils.py:19-56` 直接实现了这个构造：遍历 spot 对，计算 Gaussian 距离核（`sigma = 112 * 2`）和图像特征 cosine similarity，然后拼成二通道 `edge_attr`。`FLAG/dataset/utils.py:58-121` 又把这些 `cond_e` padding 成 batch 张量。

#### 3.2 空间图编码器

论文的概念公式是（`paper.md:159-166`）：

$$
\mathbf{H}_{\text{spatial}}=\mathrm{GraphEncoder}\big(\mathbf{C}_{v},\mathbf{C}_{e}\big).
$$

含义是：图不再生成一个动态边矩阵，而是把图像节点条件和固定边条件聚合成每个 spot 的空间上下文 $\mathbf{H}_{\text{spatial}}$。

代码对应关系需要谨慎：`FLAG/models/graph_dit_repa.py:87-91` 调用 `self.graph_backbone(x, e, t_emb, cond_x, cond_e, mask)`，返回的节点输出 `z` 被 `node2gene` 投影成 DiT 条件。`FLAG/models/graph_model.py:53-68` 是 GraphModel 的 forward。也就是说，代码里的 `z` 承担了空间上下文的角色，但它不完全等同于论文简写的 `GraphEncoder(C_v,C_e)`，因为代码还传入 noisy gene state `x`、动态边输入 `e`、时间嵌入和 mask。

一个重要代码差异是：默认 `configs/graph_latent_diffusion.yaml:29-38` 里 `edge_dim: 1`、`edge_cond_dim: 2`，但 `use_cond_e_in_attn: False`。因此二通道固定边条件虽然被构造和 batching，默认 FLAG 配置并没有把 `cond_e` 传给图注意力层（`FLAG/models/graph_model.py:62-63`）。

#### 3.3 静态图注意力和代码里的额外项

论文 Eq.60 把静态边调制写成（`paper.md:992-999`）：

$$
\mathbf{S}_{ij}=\left(\frac{\mathbf{q}_{i}\mathbf{k}_{j}^{\top}}{\sqrt{d}}\right)\odot\left(1+\alpha\cdot\text{Linear}(\mathcal{C}_{e,ij})\right)+\gamma\cdot\text{Linear}(\mathcal{C}_{e,ij}).
$$

代码更一般。`FLAG/models/layer.py:125-128` 定义了 `alpha, beta, gamma, delta` 四个可学习标量；`FLAG/models/layer.py:199-218` 的注意力分数包含：

- edge 条件的乘法/加法项：`alpha*ce_mul`、`gamma*ce_add`；
- node 条件的乘法/加法项：`beta*cx_mul`、`delta*cx_add`；
- 动态 edge hidden state 的 `e_mul`、`e_add`。

因此，论文 Eq.60 是更简化的边条件表达；代码还有 `beta/delta` 节点条件调制和输出 FiLM 调制。默认配置下 edge-condition 项不激活，但 node-condition 项仍可使用。

#### 3.4 图条件如何进入基因扩散模型

论文把图输出投影成 DiT 条件（`paper.md:1002-1008`）：

$$
\mathbf{C}_{\text{graph}}=\text{Linear}_{D_{\text{hid}}}\circ\text{SiLU}\circ\text{Linear}_{D_{\text{gene}}}(\mathbf{H}_{\text{spatial}}).
$$

代码中 `FLAG/models/graph_dit_repa.py:43-47` 的 `node2gene` 就是 `Linear -> SiLU -> Linear`；forward 中 `cond_graph = self.node2gene(z)`，然后 `c = t_emb.squeeze() + cond_graph`（`FLAG/models/graph_dit_repa.py:89-99`）。这个条件 `c` 会送入每个 DiT block。

#### 3.5 基因维度上的 DiT 扩散

论文的 gene diffusion 公式是（`paper.md:166-219`）：

$$
\hat{\epsilon}=\epsilon_{\theta}\big(\mathbf{X}_{t}\,\big\|\,\mathbf{H}_{\text{spatial}},t\big),
$$

$$
\epsilon_{\theta}(\mathbf{X}_{t})=\mathrm{DiT}\!\left(\mathbf{X}_{t}\mid\mathbf{C}_{\text{graph}},\,t\right).
$$

代码中 `FLAG/models/utils.py:6-23` 的 `GeneJointEmbedding` 把每个基因的表达值 embedding 与可学习的 gene identity embedding 相加。`FLAG/models/graph_dit_repa.py:99-104` 依次运行 DiT blocks，并在最终层输出每个 gene token 的分数/噪声预测。默认配置为 12 个 DiT blocks、hidden dim 384、6 个 attention heads（`FLAG/configs/graph_latent_diffusion.yaml:41-46`）。

#### 3.6 GFM 对齐：训练时引入基因先验

论文认为 ST spot 数量有限，单靠训练数据很难学到可靠的基因-基因结构；因此用 Gene Foundation Model（GFM）预训练嵌入作为结构先验。论文强调这些嵌入不作为推理输入，而是在训练中约束中间表示（`paper.md:225-231`）：

$$
\mathcal{L}_{\mathrm{align}}=-\frac{\left\langle\mathrm{MLP}(\mathbf{H}^{(k)}),\,\mathbf{F}\right\rangle}{\left\|\mathrm{MLP}(\mathbf{H}^{(k)})\right\|_{2}\,\left\|\mathbf{F}\right\|_{2}+\epsilon}.
$$

代码中 `FLAG/models/graph_dit_repa.py:99-104` 在 `encoder_layer` 处取中间层表示并投影；`FLAG/losses/repa_graph_fixed_loss.py:29-57` 读取 `llm_gene_level_embeddings` 和 mask，归一化后计算负 cosine 平均。默认 `encoder_layer: 8`（`FLAG/configs/graph_latent_diffusion.yaml:44`）。不过代码没有包含 Geneformer/scGPT/CellPLM embedding 的提取脚本，只消费预计算文件。

#### 3.7 总损失、优化和采样

论文总损失是（`paper.md:244-247`）：

$$
\mathcal{L}_{\text{total}}=\mathcal{L}_{\text{score}}+\lambda_{\mathrm{align}}\,\mathcal{L}_{\mathrm{align}}.
$$

代码中 `FLAG/losses/repa_graph_fixed_loss.py:17-27` 实现 VE-SDE score loss，`FLAG/losses/repa_graph_fixed_loss.py:56-57` 把它和 alignment loss 相加：`loss = loss_x + 0.5 * proj_loss`。也就是说，代码把 $\lambda_{\mathrm{align}}$ 固定为 0.5，而不是 YAML 中的显式超参数。

扩散过程采用 VE-SDE。`FLAG/sdes/vesde.py:1-49` 实现 log-linear $\sigma(t)$ 和扰动 `x_t = x_0 + sigma(t) * noise`。采样时 `FLAG/samplers/graph_ode_sampler.py:9-49` 从 Gaussian gene expression 开始，用 Heun/RK2 形式的 probability-flow ODE 逐步反推，并在末尾做 Tweedie clean-up。

### 4. 实验和结论如何解读？

论文在 HEST-1k 的 HER2ST、KIDNEY、PRAD 数据集上评估，采用 7:2:1 slide-level split，并比较 HisToGene、BLEEP、TRIPLEX、Stem、STFlow（`paper.md:263-278`）。Table 1 显示 FLAG 在 PCC/MSE 上保持竞争力，同时在 GSC/SSC 上更强；例如 HER2ST 中 FLAG 的 GSC=0.8926、SSC=0.6386 是表中最高（`paper.md:177-201`）。

Ablation 结果说明三个组件各有作用（`paper.md:316-329`）：

- 去掉 diffusion，点位 PCC 还能维持，但 GSC 大幅下降；
- 去掉 GFM alignment，准确性和空间结构都下降；
- 去掉 spatial graph，SSC 明显下降；
- 完整 FLAG 在点位和结构指标上取得更平衡结果。

图像证据也支持这些叙述：Figure 4 显示大 $G$ 下 FLAG 比 node-only/joint node-edge diffusion 更稳定；Figure 5、6、10、11 展示 FLAG 在共表达热图、Moran's I 和 marker 空间纹理上更接近 ground truth（`figure_analysis.md`）。但 paper 提到的 Figure 7 在本地 `IMAGE_DIR` 中没有单独图片，所以 Figure 7 的视觉结论不能由本地图片验证。

### 5. 代码复现需要注意什么？

公开代码验证了核心模型，但不是完整复现实验包：

- **已验证的核心实现**：GraphDitRepa 顶层模型（`FLAG/models/graph_dit_repa.py:15-104`）、GraphModel（`FLAG/models/graph_model.py:5-68`）、GraphTransformerBlock（`FLAG/models/layer.py:27-256`）、固定拓扑构造（`FLAG/dataset/utils.py:19-56`）、GFM alignment loss（`FLAG/losses/repa_graph_fixed_loss.py:4-58`）、VE-SDE 和 ODE sampler（`FLAG/sdes/vesde.py:1-49`; `FLAG/samplers/graph_ode_sampler.py:9-49`）。
- **缺失/未找到**：HMHVG 选择脚本、UNI 图像特征提取、Geneformer/scGPT/CellPLM embedding 提取、GSC/SSC 和 DEG/ARI/NMI 等下游评价指标、论文图表复现脚本、原始数据和 checkpoints。
- **关键差异**：默认配置 `use_cond_e_in_attn: False`，因此 paper 中强调的二通道固定边条件在默认图注意力里没有被传入；这会影响对“严格实现 Eq.60”的判断。

### 6. 一句话总结

FLAG 的核心不是“把空间图也一起生成”，而是把空间图变成稳定条件，把生成难题集中在基因表达上，再用 GFM embedding 约束基因结构。论文证据支持它在结构保真度上的优势；代码则实现了核心 graph-conditioned DiT 与 GFM 对齐损失，但预处理、结构指标和完整复现实验仍需要外部脚本/数据。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## FLAG Summary

### Problem

FLAG addresses prediction of spatial gene expression from routine H&E whole-slide images. The paper frames each spatial spot as having coordinates, a histology feature vector, and a high-dimensional expression vector, and seeks to predict spot-level expression while preserving biological structure, not just pointwise expression values (`paper.md:61`).

### Why existing methods are insufficient

The paper argues that many histology-to-ST predictors behave like independent scalar regressors and are usually evaluated by MSE/PCC, which can miss gene-gene regulatory structure and spatial organization (`paper.md:23-31`). It benchmarks discriminative methods HisToGene (Pang et al., 2021), BLEEP (Xie et al., NeurIPS 2023), and TRIPLEX (Chung et al., CVPR 2024), plus generative baselines Stem (Zhu et al., ICLR 2025) and STFlow (Huang et al., ICML 2025) (`paper.md:263-275`).

A key negative result is the **Gene Dimension Curse**: joint node-edge graph diffusion can help at small gene panels but collapses as the number of genes increases, because high-dimensional correlation constraints become sharp and difficult to approximate (`paper.md:118-145`; Figures 2 and 4 in `figure_analysis.md`).

### Proposed method

FLAG, “Foundation model representation with Latent diffusion Alignment via Graph,” turns the task into structured conditional generation. Its final design avoids jointly diffusing node expression and edge correlations. Instead, it:

1. constructs a fixed observable tissue graph from spatial distance and image-feature cosine similarity (`paper.md:955-972`);
2. uses a graph encoder to produce per-spot spatial context,
   $$
   \mathbf{H}_{\text{spatial}}=\mathrm{GraphEncoder}(\mathbf{C}_{v},\mathbf{C}_{e});
   $$
3. runs a gene-level diffusion transformer conditioned on that spatial context,
   $$
   \epsilon_{\theta}(\mathbf{X}_{t})=\mathrm{DiT}(\mathbf{X}_{t}\mid\mathbf{C}_{\text{graph}},t);
   $$
4. aligns an intermediate DiT representation to frozen gene-foundation-model embeddings using a negative cosine-style loss (`paper.md:159-247`).

The total training objective is the VE-SDE score-matching loss plus GFM alignment:

$$
\mathcal{L}_{\text{total}}=\mathcal{L}_{\text{score}}+\lambda_{\mathrm{align}}\mathcal{L}_{\mathrm{align}}.
$$

### Evaluation and main results

The paper evaluates HER2ST, KIDNEY, and PRAD subsets of HEST-1k with slide-level 7:2:1 splits, HMHVG target genes, and metrics PCC/MSE plus structural GSC/SSC (`paper.md:263-278`, `paper.md:539-588`). Table 1 reports that FLAG is competitive on pointwise PCC/MSE and generally strongest on structural fidelity; for example, on HER2ST it reports FLAG GSC 0.8926 and SSC 0.6386, both best in the shown table (`paper.md:177-201`).

Ablations show that removing diffusion, GFM alignment, or the spatial graph degrades different aspects of performance: the supervised no-diffusion variant keeps reasonable PCC but has much lower GSC, removing GFM alignment lowers pointwise/spatial coherence, and removing the spatial graph strongly harms SSC (`paper.md:316-329`). Downstream paper evaluations claim stronger co-expression recovery, DEG overlap, Moran's I alignment, and spatial clustering (`paper.md:335-364`). The local figure reads support these qualitative trends, except the paper's Figure 7 is not present as a local image (`figure_analysis.md`).

### Code-paper match and reproducibility

The released code snapshot is a medium-fidelity implementation of the core model, not a complete paper-reproduction package. Verified matches include the graph-conditioned DiT top-level model (`FLAG/models/graph_dit_repa.py:15-104`), graph backbone (`FLAG/models/graph_model.py:5-68`), VE-SDE and ODE sampler (`FLAG/sdes/vesde.py:1-49`; `FLAG/samplers/graph_ode_sampler.py:9-49`), fixed topology construction (`FLAG/dataset/utils.py:19-56`), and GFM alignment loss (`FLAG/losses/repa_graph_fixed_loss.py:4-58`).

Important caveats:

- `GraphModel` is the implementation's spatial-context producer, but its mapping to paper Eq.5 is **Partial** because the code passes noisy expression, dynamic edge input, time, node conditions, optional edge conditions, and a mask, not only `(C_v,C_e)` (`doc_code.md`).
- `edge_dim=1` vs `edge_cond_dim=2` is an interface split: the one-channel `edge_dim` is the dynamic/PCC edge stream, while the two-channel `edge_cond_dim` is distance plus image similarity. However, the default `graph_latent_diffusion.yaml` sets `use_cond_e_in_attn: False`, so the released default does not pass `cond_e` into graph attention (`FLAG/configs/graph_latent_diffusion.yaml:29-38`; `FLAG/models/graph_model.py:62-63`).
- `GraphTransformerBlock` contains extra node-condition `beta`/`delta` terms beyond paper Eq.60's edge-only formula (`FLAG/models/layer.py:125-128,199-218`).
- The repo lacks scripts for HMHVG selection, GFM embedding extraction, GSC/SSC/downstream metrics, raw data preparation, checkpoints, and full paper figure/table reproduction; configs use placeholder data paths (`doc_code.md`; `FLAG/configs/graph_latent_diffusion.yaml:7-17,59-63`).

### Bottom line

FLAG's methodological novelty is the factorization of spatial structure and gene-level generative modeling: use a fixed spatial graph as conditioning instead of a high-dimensional generated edge target, then use GFM alignment to regularize gene-gene structure. The paper's evidence supports improved structural fidelity, while the public code verifies the core graph-conditioned DiT and alignment loss but leaves key preprocessing, evaluation, and reproduction steps outside the snapshot.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
