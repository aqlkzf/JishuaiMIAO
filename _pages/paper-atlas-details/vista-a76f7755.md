---
layout: default
permalink: /paper-atlas/vista-a76f7755/
title: "VISTA"
nav: false
wide: true
description: "成像型或高分辨率空间转录组保留细胞位置，却常只测数百到数千个基因；scRNA-seq 没有原位坐标，却能覆盖更完整的转录组。VISTA 输入同一或相近组织的全转录组 scRNA-seq 参考 X^{N\\times G} 和空间计数 X'^{N'\\times G'}，其中 G'\\subset G，目标是在每个空间细胞上预测 G-G'，同时给出基因级和细胞级不确定性排序。"
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
      <span>Communications Biology · 2026</span>
    </div>
    <h1>VISTA</h1>
    <p>VISTA uncovers missing gene expression and spatial-induced information for spatial transcriptomic data analysis</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42003-025-09479-6" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for VISTA">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/HelloWorldLTY/VISTA" target="_blank" rel="noopener noreferrer" aria-label="Open code for VISTA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## VISTA：用单细胞参考与空间邻域补齐未测基因

### 问题不是普通缺失值填补

成像型或高分辨率空间转录组保留细胞位置，却常只测数百到数千个基因；scRNA-seq 没有原位坐标，却能覆盖更完整的转录组。VISTA 输入同一或相近组织的全转录组 scRNA-seq 参考 $X^{N\times G}$ 和空间计数 $X'^{N'\times G'}$，其中 $G'\subset G$，目标是在每个空间细胞上预测 $G-G'$，同时给出基因级和细胞级不确定性排序。

它的核心是 gimVI 风格联合变分模型再加入空间图：MLP 从表达中提取细胞内在状态，GAT 从邻居提取空间上下文，协议指示变量区分 scRNA-seq 与空间实验，解码器产生完整基因计数分布。论文的问题定义见 `paper source/PMC12891734/paper.md:156-160`，Fig. 1 是模型与不确定性总览。

预测出的矩阵仍是“给定参考、已测基因和空间邻域后的模型期望”，不是补做了一次实验。参考组织不匹配或空间状态在 scRNA-seq 中不存在时，模型可能给出平滑但错误的结果。

### Anchor gene：先筛掉不可信的跨平台桥梁

如果两侧有共享 cell-type 标签，VISTA 先按 cell type 分别做 pseudo-bulk。对每个共同基因 $g$，比较两种技术中的 cell-type 平均表达向量，保留 Pearson

$$
r_g>0.5,\qquad p_g<0.05
$$

的基因作为 anchor；其余共同基因不参加模型桥接（`paper.md:162-168`）。这一步避免负相关或技术偏差大的基因把联合空间拉错。若没有共同标签可以跳过，但此时所有 overlap genes 被默认同等可信。

当前 anchor 选择主要位于 `VISTA/demo_imputation.ipynb`，不是稳定的包 API。阈值也依赖标签粒度：粗 cell type 可能掩盖空间状态，稀有类型的 pseudo-bulk 又可能不稳定。因此 anchor 是对齐启发式，不是跨技术一致性的证明。

### 联合生成模型：两种实验共享潜在生物状态

每个细胞有低维潜变量

$$
z_n\sim\mathcal N(0,I),
$$

并由协议条件解码器输出全基因相对频率 $\rho_n=f_\eta(z_n,s_n)$。对 scRNA-seq，模型可用 ZINB 或 NB；论文实验声明使用 ZINB：

$$
x_{ng}\sim\operatorname{ZINB}(\ell_n\rho_{ng},\theta_g,\pi_{ng}).
$$

对空间数据，只观察 $G'$，于是先在该子集重新归一化：

$$
\rho'_{ng'}=\frac{\rho_{ng'}}{\sum_{g\in G'}\rho_{ng}},\qquad
x'_{ng'}\sim\operatorname{NB}(\ell'_n\rho'_{ng'},\theta'_{g'}).
$$

代码 `VISTA/vista/_module.py:641-665` 实现 ZINB/NB likelihood，`:695-725` 在当前 mode 的观测基因索引上重新归一化并乘 library size。损失只在该模态真实观测的基因上计算（`:780-789`），而 decoder 仍覆盖 union gene space，所以空间 latent 可以解码缺失基因。

该设计的关键假设是两种技术能够用共同 $z$ 表达生物状态，协议条件和对抗对齐能吸收平台差异。若参考缺少目标中的病变/区域细胞，解码器只能外推。

### 空间图怎样进入后验

VISTA 以空间坐标用 FAISS 近邻搜索构图，代码入口 `VISTA/vista/faiss_neig.py:21-44`。训练时对空间 mini-batch 根据样本索引切出子 AnnData，并令邻居数不超过 batch 长度（`_module.py:762-769`）。两层面上的作用不同：表达 encoder 先给 $q(z)$ 的 location 与 scale；GAT 再从邻接细胞聚合并做残差更新：

$$
\mu_s=\mu+\operatorname{GAT}_\mu(\mu,E),\qquad
\sigma_s=\sigma+\exp(\operatorname{GAT}_\sigma(\sigma,E)).
$$

当前实现见 `_module.py:770-773`。这使空间邻居改变训练损失中的后验分布，理论上把局部组织结构注入 latent。

但源码存在一个必须保留的执行边界：常规 forward 先在 `_run_forward()` 中用 `inference()` 的原始 $z$ 计算 generative output（`:574-597`），之后 `loss()` 才原位修改 `qz.loc/qz.scale`。已生成的 `px_rate` 没有在该函数中用更新后的 $qz$ 重算。公开 `get_imputed_values()` 也走标准 inference/decode 路径，未明确再次应用 GAT。因而“代码中 GAT 确定地直接改变最终 imputed counts”不能被现有调用链完全证实；更稳妥的结论是 GAT 参与损失/KL 相关计算，但公开推断路径的空间更新存在歧义。这是 paper-code Partial match，不应被润色成 Exact。

### 对抗对齐在做什么

scRNA-seq 和空间数据即使来自同一组织也有 protocol shift。`VISTA/vista/_task.py:8-65` 继承 scvi-tools `AdversarialTrainingPlan`，用模态/协议分类器对 latent 施加对抗目标，使两种数据较难被技术来源区分。它帮助联合空间混合，却也可能在真实模态差异与生物差异纠缠时过度校正。

训练 API `VISTA/vista/_model.py:171-340` 组织两个 dataloader、KL warm-up、对抗 plan 与自适应 batch。默认图邻居和 batch 会按内存限制调整，因而不同硬件可能走不同局部图，不能只报告随机种子而忽略实际 batch/neighbor 设置。

### 缺失基因怎样生成

训练完成后，对空间细胞用空间 mode 编码，再用全基因 decoder 输出 `px_scale` 或 `px_rate`；`GIMVI_GCN.get_imputed_values()` 位于 `_model.py:388-456`。缺失基因预测本质上是

$$
\hat x'_{ng}=E[x'_{ng}\mid X',X,E,s=1],\quad g\in G-G'.
$$

如果从 NB/ZINB 抽样而非只取均值，还可生成多次 posterior predictive realization。注意 decoder 的表达并非“把最近邻 scRNA 细胞复制过来”，而是共享 latent 中学到的基因共变结构与协议条件输出。

### 不确定性：排名而非校准区间

论文从输出 NB 分布抽 $L=\min(N'/10,100)$ 次。对基因 $g$，每次抽样形成跨全部空间细胞的向量 $v_{jg}$，与均值向量 $\bar v_g$ 比较：

$$
\delta_g=1-\operatorname{median}_{j=1}^L\cos(v_{jg},\bar v_g).
$$

细胞不确定性同理，只是向量换成该细胞跨基因的 profile。越小表示抽样形状越稳定（`paper.md:221-233`）。它主要受模型 dispersion 与均值影响，并不测量参考缺失、模型结构错误或真实空间状态外推风险，所以不是覆盖率经过校准的置信区间。

实现层面更需谨慎：分布类在 `VISTA/uncertainty/scvi_distribution.py`，实际工作流只存在 `demo_imputation.ipynb`。当前 notebook 的 gene 代码用 mean cosine 而非论文 median；cell 片段把整张 sampled matrix 与一个 cell vector 比较，形状/语义可疑。故论文不确定性公式有清晰定义，但仓库示例属于 Partial/Notebook，不能声称稳定公共 API 精确复现。

### 六幅主图的证据链

- Fig. 1 说明 anchor、联合 VAE、FAISS/GAT、缺失基因解码及 uncertainty sampling，是方法合同而非性能证明。
- Fig. 2 在 osmFISH brain 隐藏部分已测基因，以 SCC、SSIM、RMSE、JS 和 marker 恢复比较 gimVI、SpaGE、TransImp、ENVI、SpaIM、Tangram 等。held-out 已测基因是可量化代理，但未测基因可能更难。
- Fig. 3 扩展到 Xenium breast/brain、seqFISH embryo 和 Visium mouse，展示规模与跨平台表现；部分比较采用抽样，不能等同于所有方法都完整运行全图。
- Fig. 4 研究 imputation 后的 spatially variable genes 与 cell–cell interaction。检测数量增加不自动表示真阳性增加；数据库和表达阈值可能放大预测偏差。
- Fig. 5 展示将 spliced/unspliced 分别补齐后运行 scVelo/VeloVI，以及 COMMOT 信号方向。论文明确这些应用缺少直接 ground truth（`paper.md:330-340`），应视为可行性展示。
- Fig. 6 把 imputed matrix 输入外部 SIMVI 分解 cell-type 与 spatial effects。这里证明的是 VISTA 输出可作为 SIMVI 输入，不是 VISTA 自己内生识别因果空间效应。

主图文件位于 `paper source/PMC12891734/images/`，逐图解释见 `figure_analysis.md`。本地还保存 PMC MOESM 和 `supplementary/MOESM*.pdf`；没有独立转换出的 supplement Markdown。本次利用正文中的补充锚点、现有分析和本地附件核对证据边界，不声称已重算 Supplementary Data 或所有 baseline。

### 评估和应用最容易越界的地方

SCC 衡量逐基因秩相关，SSIM 衡量空间图形，RMSE 衡量标准化数值误差，JS 衡量分布差异。任何单一指标都可能偏爱平滑或高表达基因。基因/细胞 uncertainty 过滤在某些数据上提升指标，只说明模型内稳定性排序有用，不证明被保留基因全部正确。

下游 RNA velocity、CCI、SV gene、spatial effect 与 in-silico perturbation 都会把 imputation bias 继续传播。特别是速度需要 spliced/unspliced 动力学结构，单独补两层计数并不能创造真实时间信息；perturbation transfer 也反映参考数据和 decoder 假设，而不是空间组织真正接受了扰动。

### 版本与复现边界

核心模型和 metric snippets 可审计，但 anchor、uncertainty、velocity、SIMVI 等关键环节散落在 notebook；多个 notebook 使用绝对 HPC 路径。完整的 seeds 0–9 baseline orchestration、全部数据预处理和可移植 figure generation 未找到。环境文件锁定较旧的 scvi-tools 等依赖，论文报告使用一张 A5000、最高约 150 GB RAM并限制 24 h；这不保证在任意新环境直接复现。

### 实际使用建议

优先选择组织、物种、条件和 cell states 匹配的 scRNA 参考；把 GAT 推断歧义与 notebook uncertainty 差异写入方法记录；对关键候选基因用 held-out 测量或独立技术验证。VISTA 最适合作为生成候选的参考引导模型，而不是把低 panel 空间实验无条件升级成真实全转录组。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## VISTA Summary

### Motivation and Novelty

High-resolution spatial transcriptomics preserves where cells are located but often measures only a restricted gene panel. scRNA-seq measures many more genes but loses spatial context. VISTA addresses this gap by predicting genes missing from spatial transcriptomic data using a paired or related scRNA-seq reference.

The paper's novelty is a joint probabilistic imputation model that combines a gimVI-like variational count model with spatial graph information and sampling-based uncertainty scores. The intended result is a completed spatial expression matrix that can support downstream analyses that require broader gene coverage, including spatially variable gene detection, ligand-receptor inference, RNA velocity, spatial-effect decomposition, and perturbation transfer.

Compared methods include SpaGE (Nucleic Acids Research, 2020), Tangram (Nature Methods, 2021), gimVI (arXiv preprint, 2019), ENVI (Nature Biotechnology, 2024), SpatialScope (Nature Communications, 2023), TransImp/TransImpute (Cell Reports Methods, 2024), TISSUE (Nature Methods, 2024), and SpaIM (Nature Communications, 2025). The paper also evaluates downstream tasks with tools including SpatialDE (Nature Methods, 2018), CellPhoneDB (Nature Protocols, 2020), CellChat (Nature Communications, 2021), COMMOT (Nature Methods, 2023), scVelo (Nature Biotechnology, 2020), and VeloVI (paper metadata not preserved in the converted Markdown).

### Method Overview

VISTA takes two AnnData-style count matrices: reference scRNA-seq $X^{N,G}$ and spatial expression $X'^{N',G'}$, with $G' \subset G$. If shared cell-type labels are available, it filters shared genes into anchors by pseudo-bulk Pearson correlation, using default thresholds $r>0.5$ and $p<0.05$.

The model uses a joint VAE. scRNA-seq counts are modeled with a ZINB likelihood, while spatial measured counts are modeled with an NB likelihood after renormalizing decoder frequencies over the spatial gene subset. Spatial coordinates are used to construct mini-batch neighbor graphs, and a GAT component is intended to inject local spatial context into the spatial latent representation.

After training, the model decodes spatial cells across the full scRNA-seq gene axis. It estimates gene- and cell-level reliability by sampling from the output NB distribution and comparing samples with the mean by cosine similarity.

### Evaluation

The paper evaluates imputation on osmFISH-brain, Xenium-breast, Xenium-brain, seqFISH-embryo, and Visium-mouse style paired datasets. Metrics include SCC, SSIM, RMSE, and JS divergence. VISTA often ranks first or near first, especially after uncertainty filtering.

For biological utility, the paper evaluates clustering preservation, SV-gene discovery, and CCI inference using metrics such as NMI, ARI, ASW, Moran's I, SpatialDE, and CellPhoneDB/CellChat/COMMOT-derived scores. It also presents application case studies for RNA velocity, SIMVI spatial-effect analysis, and perturbation or condition transfer.

These downstream results should be interpreted conservatively. Some tasks have no direct spatial ground truth, so they demonstrate plausible utility of imputed expression rather than experimental validation of every inferred gene, interaction, velocity, or perturbation effect.

### Code Verification

The repository contains a real implementation centered on `vista.GIMVI_GCN`. Code review verified the scvi/gimVI-style model, default ZINB/NB likelihoods, spatial gene mapping, FAISS KNN graph construction, GAT layers, adversarial classifier, public imputation API, and basic metric scripts.

Important caveats:

- The GAT update is applied inside `JVAE.loss()` after generative outputs appear to have already been computed, and public imputation does not appear to reapply the GAT block. This makes the graph contribution to reconstructed/imputed expression ambiguous.
- Anchor-gene preprocessing is in `demo_imputation.ipynb`, not the package.
- Uncertainty estimation is notebook-level, not a packaged API.
- The notebook gene-uncertainty code uses mean cosine similarity where the paper states median, and the cell-uncertainty snippet appears to have an indexing problem.
- Full benchmark and application reproduction scripts are not portable; notebooks contain absolute Yale HPC paths.

### Reproducibility Rating

**2.5 / 5**

The model code and demo are available under an MIT license, and the main algorithmic skeleton is present. However, several paper-critical workflows are notebook fragments, uncertainty does not exactly match the manuscript, application notebooks are not portable, and the inspected GAT placement raises a substantive paper-code ambiguity. A user can learn and run the core imputation workflow, but reproducing the paper's claims end to end would require manual repair and access to external datasets and compute.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
