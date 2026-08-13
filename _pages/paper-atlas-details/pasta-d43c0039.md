---
layout: default
permalink: /paper-atlas/pasta-d43c0039/
title: "PASTA"
nav: false
description: "成像型空间转录组可以在单细胞分辨率保留组织坐标，但通常只测一个预选基因面板。PASTA（PAthway-oriented Spatial gene impuTAtion）借助全转录组 scRNA-seq 参考，将未测基因投影回空间。它与多数逐基因补全方法的区别是：训练时就指定一个通路，用该通路中已测基因、细胞类型和同类型空间邻域约束映射，最终直接输出每个空间细胞的通路总表达。 PASTA 的核心假设有三条。"
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
      <span>Nature Communications · 2025</span>
    </div>
    <h1>PASTA</h1>
    <p>Accurate imputation of pathway-specific gene expression in spatial transcriptomics with PASTA</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-67421-0" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for PASTA">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/rx-li/PASTA" target="_blank" rel="noopener noreferrer" aria-label="Open code for PASTA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PASTA 中文方法解读：以通路为目标的空间基因表达补全

### 方法要解决的不是“再补一个基因”

成像型空间转录组可以在单细胞分辨率保留组织坐标，但通常只测一个预选基因面板。PASTA（PAthway-oriented Spatial gene impuTAtion）借助全转录组 scRNA-seq 参考，将未测基因投影回空间。它与多数逐基因补全方法的区别是：训练时就指定一个通路，用该通路中已测基因、细胞类型和同类型空间邻域约束映射，最终直接输出每个空间细胞的通路总表达。

PASTA 的核心假设有三条。第一，ST 与参考 scRNA-seq 的共享基因足以建立细胞映射。第二，同一细胞类型的近邻具有较相似的通路表达。第三，把功能相关基因聚合为通路可降低单基因稀疏和噪声。第三条是统计上的稳健性假设，不意味着任意基因集聚合都会改善预测；补充图 S1、S2显示通路过大或完全没有已测通路基因时性能会下降。

### 输入、输出与映射矩阵

设空间表达矩阵为

$$T\in\mathbb R^{n_T\times G_T},$$

参考单细胞矩阵为

$$S\in\mathbb R^{n_S\times G_S}.$$

两者共享基因集合为 $\mathcal O=\mathcal G_T\cap\mathcal G_S$。对通路 $l$，完整基因集 $\mathcal G_l$ 被拆成 ST 已测的 $\mathcal G_l^{obs}$ 与只在参考中存在的 $\mathcal G_l^{miss}$。

PASTA 学习未经约束的矩阵 $\widetilde A\in\mathbb R^{n_S\times n_T}$，对每个参考细胞的一行做 softmax：

$$
A_{ij}=\frac{\exp(\widetilde A_{ij})}
{\sum_{j'=1}^{n_T}\exp(\widetilde A_{ij'})}.
$$

因此每个参考细胞向所有空间位置分配总和为 1 的概率质量。投影表达为

$$S^*=A^\top S,$$

其行对应空间细胞。完整通路活动是投影后该通路所有基因的和：

$$T_l=S^*_{:,\mathcal G_l}\mathbf 1.$$

这仍然是一种软映射加重心投影：它没有为每个 ST 细胞生成新的测序读段，也不提供单基因的实验观测。输出是由参考与约束推断出的空间通路分数。

### 四个损失分别保护什么

#### 全局相似度

全局项比较所有共享基因在空间上的预测与观测：

$$
L_{global}=-\sum_{g\in\mathcal O}
\operatorname{CosSim}(S^*_{:,g},T_{:,g}).
$$

它使映射服从总体转录相似性，但高表达或数量众多的非通路基因可能淹没目标通路。

#### 通路相似度

通路项只看当前通路中已测基因：

$$
L_{pathway}=-\sum_j
\operatorname{CosSim}(S^*_{j,\mathcal G_l^{obs}},
T_{j,\mathcal G_l^{obs}}).
$$

它让每个空间细胞的通路基因向量与真实观测方向一致。补充图 S17的消融显示去掉该项性能下降最大，S18也显示结果对该权重敏感。

#### 邻域相似度与重构

对空间细胞 $j$，PASTA 在相同细胞类型内寻找默认 $k=10$ 个最近邻 $N(j)$。论文定义邻域余弦项，用于保持同类近邻的通路模式；另有重构 MSE，使预测通路基因与邻域观测接近。总目标写为：

$$
L=\lambda_1L_{recon}+\lambda_2L_{global}+
\lambda_3L_{pathway}+\lambda_4L_{neighbor}.
$$

论文给出的默认权重为 $\lambda_1=1$、$\lambda_2=2$、$\lambda_3=1$、$\lambda_4=10$。这些项体现两个不同层次：全局项建立参考与空间数据的总体对应；通路与邻域项避免映射只优化容易预测的全局结构。

### 从数据到结果的实际流程

第一步将 ST 和 scRNA-seq 的基因名对齐，移除全零共享基因。第二步准备 ST 坐标、细胞类型标签和目标通路。第三步在每个细胞类型内部计算欧氏距离并选最近邻。第四步随机初始化映射 logits，使用 Adam 对映射矩阵优化，默认 API 为 500 epochs、学习率 0.01。第五步对最终 logits 做 softmax，得到 $A$。第六步用 $A^\top S$ 投影参考的全基因表达，并对目标通路求和。

源码的 `mapper.mapping()` 负责输入检查、共同基因矩阵和邻居索引；`optimizer.Mapping` 保存 $S$、$T$ 和可训练矩阵，计算损失并训练；`utils.project_genes()` 做投影和通路聚合。模型没有编码器、图神经网络或生成扩散过程，主要参数就是一个 $n_S\times n_T$ 的稠密矩阵，因此内存随参考细胞数与空间细胞数的乘积增长。

### 六张主图提供的证据

图 1A 是算法图，明确显示 ST、坐标、细胞邻域、参考 scRNA-seq 和通路映射进入四项损失。图 1B–E 是 30 次模拟，覆盖随机拆分、不同组织区域、不同受试者和不同细胞类型。PASTA 在 Pearson、Spearman 和 MSE 上通常优于 Tangram、Seurat 与 LIGER，但参考与查询差异增大时性能仍下降。

图 2在 Xenium 肺癌切片上展示三条 Hallmark 通路的空间图案。Hedgehog 通路报告相关性 0.907，说明聚合图案可接近用已测基因构造的“真值”。图 3汇总 44 条通路、细胞类型富集和肿瘤区域聚类；PASTA 的分布更接近作者定义的真值，并用于后续伪时间分析。

图 4是 MERFISH 小鼠脑，展示脑干发育等通路、24 条通路相关性、皮层层次伪时间和 pathway-by-cell 聚类。图 5是 ISS 小鼠视觉皮层，PASTA 对若干脑发育通路相关性很高，并给出细胞类型富集与伪时间。图 6是 CosMx 人额叶皮层，除相关性外还报告 TISSUE calibration score 和不确定性分布。

这些实验跨 Xenium、MERFISH、ISS、CosMx 与模拟 Stereo-seq，说明方法适用于多种定向面板。但所谓“ground truth”通常是通路中与 ST 面板重叠的已测基因之和，而不是被遮盖基因的独立全转录组空间测量。因而评估同时衡量映射能否重建已测部分，不能完全证明所有未测基因的真实性。

### 补充材料补足的边界

补充图 S1显示通路规模增大带来异质性；S2显示完全没有通路基因被 ST 测到时，所有方法的中位 Pearson 降到约 0.3；这说明 PASTA 不是“零锚点”外推器。S4显示参考细胞小于约 2,000 时增加参考规模有益，之后收益趋于饱和。S5、S6说明稀有细胞类型和过度聚类会降低稳定性。

S15测试只保留 5% 面板基因的极端稀疏场景。S17的消融支持四项信息均有贡献，尤其通路项；S18显示超参数敏感性，特别是通路损失权重和学习率。由此可见论文题目中的“accurate”依赖通路仍有可观测锚点、参考覆盖、细胞类型质量和权重设置。

### 论文与当前代码的关键差异

本地快照固定为完整提交 `a21907241630a1d4238d8e38bcb3247e22b134bb`。主链路能在代码中找到，但损失权重实现与论文存在直接差异。

第一，`mapper.py` 的 `hyperparameters` 字典连续两次写入键 `lambda_3`：先赋传入的 `lambda_3`，随后又赋 `lambda_4`。Python 字典会让后者覆盖前者。因此构造 `Mapping` 时，实际 `lambda_3` 收到调用者的 `lambda_4`，而 `lambda_4` 没有传入，回落到构造函数默认值 1。

第二，`optimizer.py` 计算总损失为 `-expression_term + pathway_term`。其中全局余弦乘 `lambda_2`、通路余弦乘 `lambda_3`、邻域余弦乘 `lambda_4`，但 MSE 的 `pathway_term` 没有乘 `lambda_1`。`lambda_1 * pathway_term` 只用于日志变量 `pathway_reg`，不进入反向传播。因而 API 中的 `lambda_1` 不能按论文所述调节重构项。

第三，论文默认权重写为 `(1,2,1,10)`，源码函数默认全为 1，README 示例又使用 `(2,1,1,1)`。复现时不能笼统说“使用默认值”，必须说明论文、API 或示例中的哪一套。

第四，`mapper.py` 文档字符串写学习率默认 0.1、1000 epochs，而函数签名实际是 0.01、500 epochs；README 示例使用 0.05、500 epochs。文档与入口同样存在版本漂移。

因此当前提交支持算法框架、矩阵方向和邻域构造，但不能作为论文四项加权目标的 Exact 实现。若要按论文复现，应先修正重复键，将 `lambda_4` 正确传入，并在总损失中显式使用 `lambda_1`，再依据论文或 Zenodo 发布版核对参数。

### 统计与生物解释的注意事项

通路求和会降低随机噪声，也会把基因集大小、重叠和少数高表达基因带入分数。不同大小通路的原始和不可直接比较。通路数据库的先验边界也可能过宽或与当前组织不匹配。

同类型近邻相似是平滑先验。在真实组织边界、激活梯度或同一类型的状态转换处，这个先验可能抹平真实异质性。细胞类型标签若来自待补全面板本身，其错误会直接影响邻域约束；过细聚类又可能让邻居不足。

作者利用预测通路做 K-means、富集和 Monocle3 伪时间。这些属于下游示范，不是独立验证。伪时间与已知层次或 MET 分布一致能增加可信度，但预测误差会传播到聚类与轨迹，不能把下游图案当成新的实验测量。

论文报告 stAI 无法在肺癌全切片上运行，因为需要超过 100 GB GPU 内存。基准中方法缺失并非随机缺失，性能与资源比较应一起解读。PASTA 本身的稠密映射也可能在大规模参考×空间细胞组合上成为瓶颈，论文没有给出完整复杂度和峰值内存曲线。

### 复现边界

论文代码可用，发表版还归档于 Zenodo DOI `10.5281/zenodo.17336118`；本地工作区是 GitHub 提交 `a2190724...`。数据来自 10x、Allen Brain Atlas、SpaceTx、NanoString、GEO 等多个外部来源，仓库只带示例 pickle，不能离线重现全部六张主图。环境文件列出依赖，但跨 GPU/PyTorch 版本和随机初始化仍需固定种子并记录硬件。

最稳妥的结论是：PASTA 将通路锚点、共享基因、细胞类型和同类空间邻域组合到一个可解释的软映射框架，在多种面板型 ST 数据上获得较高的通路重建相关性；但其未测基因真值验证仍有限，而且当前代码提交的超参数传递和损失加权与论文公式不一致，必须在精确复现前修正或对照 Zenodo 版本。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PASTA: Accurate Imputation of Pathway-Specific Gene Expression in Spatial Transcriptomics

> Li R, Yang P, Di Pilato M, Zhang J, Flowers CR, Shang L, Li Z. *Nature Communications* **17**, 2025.
> DOI: [10.1038/s41467-025-67421-0](https://doi.org/10.1038/s41467-025-67421-0)
> Code: [https://github.com/rx-li/PASTA](https://github.com/rx-li/PASTA)

### Motivation & Novelty

#### The problem

Targeted spatial transcriptomics platforms (Xenium, MERFISH, CosMx, ISS) measure only a pre-selected panel of hundreds to thousands of genes, missing the majority of the transcriptome. Computational imputation methods bridge this gap by predicting unmeasured gene expression using matched scRNA-seq references. However, existing methods — SpaGE (*Nucleic Acids Res.*, 2020), stPlus (*Bioinformatics*, 2021), Tangram (*Nature Methods*, 2021), gimVI (*Bioinformatics*, 2020), stDiff (*Brief. Bioinform.*, 2024), SPRITE (*Bioinformatics*, 2024), stAI (*Nucleic Acids Res.*, 2025) — all operate at the individual gene level, producing high-variance predictions and requiring separate downstream pathway analysis.

#### Limitations of existing approaches

1. **High noise at gene level**: individual gene imputation is inherently noisy due to sparsity in both scRNA-seq and ST data
2. **No pathway-level guidance**: existing methods do not incorporate biological pathway knowledge during the imputation process
3. **Limited use of spatial structure**: most methods either ignore spatial information or apply uniform spatial smoothing without cell-type awareness
4. **No cell-type-informed alignment**: few methods explicitly use cell type annotations to constrain the mapping between scRNA-seq and ST data

#### PASTA's contributions

1. **Pathway-oriented imputation**: aggregates functionally related genes during training (not just post-hoc), reducing noise through pathway-level regularization
2. **Cell-type-stratified spatial neighborhoods**: computes k-nearest neighbors within each cell type separately, enforcing that spatial smoothing respects cell identity boundaries
3. **Multi-objective optimization**: four complementary loss terms (reconstruction, global similarity, pathway similarity, neighborhood coherence) provide multi-scale regularization
4. **Direct pathway activity output**: eliminates the need for post-hoc pathway enrichment analysis, producing spatially resolved pathway scores that are directly interpretable

### Method Overview

PASTA learns a soft alignment matrix $A$ (scRNA-seq cells $\times$ spatial locations) via softmax normalization of a trainable matrix $\tilde{A}$. The imputed spatial expression $S^* = A^T S$ is optimized per pathway using four loss terms that enforce: (1) local reconstruction accuracy within same-cell-type neighborhoods, (2) global transcriptome-wide agreement, (3) pathway-specific gene fidelity, and (4) neighborhood-level pathway coherence.

After training, the alignment transfers to all scRNA-seq genes (including unmeasured ones in ST), and pathway activity is computed as the sum of imputed expression across pathway gene members. See doc_method.md for full mathematical details and algorithm walkthrough.

The method is inspired by Tangram but adds cell-type-stratified spatial neighborhoods and pathway-level regularization. Training uses Adam optimization in PyTorch, with one model per pathway.

### Evaluation

#### Simulation studies

Simulations used Stereo-seq data from axolotl regenerative telencephalon (3,000 cells, 1,000 genes per simulated dataset, 30 independent runs). PASTA was tested under increasingly challenging conditions:

| Scenario | Key Finding |
|----------|-------------|
| Random split (same distribution) | PASTA achieves highest correlation, lowest MSE across all pathway sizes (35-70 genes) |
| Different regions (same subject) | Stable performance despite expression variability between regions |
| Different subjects | Superior accuracy maintained with cross-subject reference |
| Different cell types | Several methods (Seurat) became unstable; PASTA showed moderate decline but remained best |
| Partial pathway coverage | When only subset of pathway genes observed in ST, PASTA still outperforms; all methods degrade when 0% observed |

Additional findings:
- Reference size: improvement plateaus above ~2,000 cells (Fig. S4)
- Major cell types impute slightly better (more neighbors available; Fig. S5)
- Over-clustering hurts: unnecessary cell type splitting adds noise (Fig. S6)

#### Real-world datasets

| Dataset | Platform | Cells | ST Genes | Pathways | PASTA vs. best competitor |
|---------|----------|-------|----------|----------|--------------------------|
| Human lung cancer | Xenium | 161,000 | 480 | 44 Hallmark | Better in 79.5% of pathways vs. SpaGE; 100% vs. Tangram |
| Mouse brain | MERFISH | 82,075 | 1,122 | 24 GOBP | Highest correlation; brainstem development pathway r=0.958 |
| Mouse visual cortex | ISS | 82,785 | 119 | 26 GOBP | Better in ~70% pathways vs. Tangram; SpaGE/Seurat struggled |
| Human frontal cortex | CosMx | 188,686 | 6,000+ | 40 GOBP | Superior in ~70% pathways; best calibration score |

#### Biological validation

- **Pathway enrichment**: PASTA correctly identified MYC TARGETS V1/V2 enriched in tumor cells, immune pathways in T cells/macrophages (lung cancer data). Seurat generated false positives.
- **Trajectory analysis**: pathway-by-cell matrix with Monocle3 recovered inside-out neurogenesis ordering (L6→L4→L2/L3) in cortical layer cells. Tangram failed to capture the developmental time shift.
- **Spatial clustering**: K-means on PASTA pathway matrix cleanly separated astrocytes/OPCs/vascular cells from neurons (mouse brain). Tangram and Seurat produced mixed clusters.
- **Meta-program prediction**: PASTA predicted tumor-associated meta-programs enriched in basal cells within tumor areas (lung cancer).
- **Calibration**: TISSUE calibration scores showed PASTA achieved stable predictions with lower within-cell-type variability (human frontal cortex).

#### Ablation analysis (Fig. S17)

All four loss components contribute. Removing the pathway loss ($L_{pathway}$) causes the largest drop: Pearson correlation from 0.91 to 0.5. The reconstruction and neighborhood losses improve stability.

### Reproducibility

**Rating: 3/5** (Moderate)

#### Strengths
- Code publicly available under MIT license (GitHub + Zenodo archive)
- Example data bundled (`test.pkl`)
- Dependencies specified in `environment.yml`
- Simple API: `pp_adatas()` → `mapping()` → `project_genes()`

#### Weaknesses
- **Code bugs**: lambda parameter overwrite bug (`mapper.py:185`) means λ3 and λ4 are conflated when set to different values; λ1 is not applied in the actual loss function despite being a paper parameter
- **No cell-type-free mode**: paper claims cell type was not used for ISS dataset, but code requires `sp_celltypes` as mandatory argument
- **Default hyperparameters don't match paper**: code defaults all λ=1, but paper recommends λ2=2, λ4=10
- **No evaluation code**: Pearson/Spearman correlation, Wilcoxon tests, trajectory analysis, and calibration scores are not included in the package — must be implemented externally
- **No notebook/scripts for paper figures**: the repository contains only the core package, not the analysis scripts that generated the paper's results
- **Outdated dependencies**: requires PyTorch 1.4.0 (2020), which may not install on modern systems

#### Practical notes

- The alignment matrix is $n_S \times n_T$, so memory scales quadratically. For large datasets (>100K cells each), GPU memory may be limiting.
- stAI was excluded from real-data comparisons because it required >100 GB GPU memory.
- Pathway selection is critical: tissue/disease-relevant pathways perform best. Broad/generic pathways may not capture meaningful spatial signal.
- No internal data normalization — users must pre-normalize expression data appropriately.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
