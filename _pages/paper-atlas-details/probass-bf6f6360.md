---
layout: default
permalink: /paper-atlas/probass-bf6f6360/
title: "ProBASS"
nav: false
wide: true
description: "ProBASS 将 ESM-2 的 mutant-minus-WT 全链平均差分与 ESM-IF1 的 WT 复合体平均结构向量拼成 1792 维特征，再用实验标签训练 CatBoost。它的核心推理代码可以核查，但高性能强依赖数据划分，结构分支不随突变变化，完整 benchmark 与 final training 配置尚未公开复现。"
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
      <span>Protein &amp; Sequence Models</span>
      <span>Bioinformatics · 2025</span>
    </div>
    <h1>ProBASS</h1>
    <p>ProBASS---a language model with sequence and structural features for predicting the effect of mutations on binding affinity</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1093/bioinformatics/btaf270" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ProBASS">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/sagagugit/ProBASS" target="_blank" rel="noopener noreferrer" aria-label="Open code for ProBASS">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ProBASS：用序列变化与野生型结构上下文预测突变的结合自由能变化

### 1. 它预测的究竟是什么

ProBASS 处理蛋白—蛋白相互作用（PPI）中的点突变：输入复合体 PDB、被突变链、partner chain、野生型残基、PDB residue number 和目标氨基酸，输出突变引起的结合自由能变化 $\Delta\Delta G_{bind}$（kcal/mol）。论文把它做成监督回归：ESM-2 提供序列表征，ESM-IF1 提供结构表征，再用实验 $\Delta\Delta G_{bind}$ 标签训练 CatBoost。

这个输出应理解为候选突变的排序和近似能量变化，而不是物理自由能计算。模型没有显式模拟溶剂、离子、质子化状态、构象采样或侧链重排；预测也受实验条件、训练 PPI 构成和 PDB 质量影响。Spearman 相关高表示排序较好，不保证每个突变的绝对 kcal/mol 都准确。

### 2. ESM-2 分支：用“突变复合体均值减野生型复合体均值”表示序列变化

公开 notebook 使用 `esm2_t33_650M_UR50D`，取第 33 层每个 token 的 1280 维表示。对同一个复合体构造三条序列：被突变链的 WT、该链的 mutant，以及不变的 partner chain。

设三条 per-residue embedding 分别为 $H_{WT}$、$H_{mut}$ 和 $H_p$。代码先沿 residue 维拼接 partner 与目标链，再分别做全序列平均：

$$
\bar h_{mut+p}=\operatorname{mean}([H_p;H_{mut}]),
$$

$$
\bar h_{WT+p}=\operatorname{mean}([H_p;H_{WT}]).
$$

序列变化向量是

$$
d=\bar h_{mut+p}-\bar h_{WT+p}\in\mathbb R^{1280}.
$$

直接源码证据在 `ProBASS.ipynb` 的代码源约 454–460 行（ESM-2 33 层提取）以及 713–727 行（partner 拼接、mean pooling、相减和融合）。这个设计让 partner 出现在两边，意图是比较同一 PPI 上下文中 mutant 与 WT 的语言模型差异。

但它有一个容易忽略的数学结果。设 partner 长度为 $L_p$、目标链长度为 $L_m$，两边长度相同，则 partner 的 embedding 在相减时逐项贡献相同，因而

$$
d=\frac{\sum_iH_{mut,i}-\sum_iH_{WT,i}}{L_p+L_m}.
$$

partner 并未与目标链一起送入 ESM-2 做联合 attention；它只是单独编码后拼接再平均。因此 partner 的具体序列内容在差分中抵消，主要留下一个由总长度决定的缩放。不能把这个实现描述成 ESM-2 显式建模跨链相互作用。真正的复合体上下文主要来自后面的 ESM-IF1 结构分支和监督标签。

此外，全链平均会稀释单个位点的局部信号，长蛋白尤其明显。ESM-2 的 mutant 表示确实会因一个 token 改变而在上下文传播，但 ProBASS 没有显式截取界面邻域或 mutation-site embedding。

### 3. ESM-IF1 分支：同一 PDB 的野生型结构向量

ESM-IF1 是 inverse-folding 模型。公开 notebook 加载 `esm_if1_gvp4_t16_142M_UR50`，从 PDB 中读取 mutated chain 与 partner chain 的坐标，然后调用 `get_encoder_output_for_complex(..., Mutated_chain)`，取得被突变链处于复合体坐标上下文中的 per-residue 512 维状态（notebook 源约 464–534 行）。

这些状态再按 residue 平均：

$$
s=\frac{1}{L_s}\sum_{i=1}^{L_s}Z_i\in\mathbb R^{512}.
$$

代码约 634–660 行执行 mean、reshape 为 `[1,512]`；训练特征 notebook 还把它 tile 给同一 PDB 的所有突变。也就是说，结构向量来自 WT backbone，并且对同一个复合体/被突变链的不同突变通常完全相同。它告诉 CatBoost“这是哪个结构环境”，却不直接表示某个突变引起的侧链 packing、backbone relaxation 或水网络变化。

论文的理由是 WT 与大多数 mutant 的 Cα backbone 近似相似，从而无需为每个突变重新建模结构。这带来效率，也构成主要失败边界。论文 outlier 分析发现 proline substitution 显著富集，并提到小残基到芳香残基等可能诱发局部构象变化；这与当前 WT-backbone、全链平均表征的盲点一致。

### 4. 1792 维融合与 CatBoost

最终特征只是两个向量拼接：

$$
x=[d;s]\in\mathbb R^{1280+512}=\mathbb R^{1792},
$$

$$
\widehat{\Delta\Delta G}_{bind}=f_{CB}(x).
$$

公开推理 notebook 加载 `Probass_model.cbm` 并调用 CatBoost prediction。CatBoost 适合中等样本量的连续 tabular embedding：它能用树的分裂组合 PLM feature，而不必在有限实验标签上端到端微调两个大模型。

这里论文所说的 “fine-tuning” 更准确地理解为：冻结预训练 PLM 做特征抽取，再训练下游 CatBoost。公开代码没有反向更新 ESM-2 或 ESM-IF1 参数。若把它描述成端到端微调 PLM，会夸大实现范围。

论文说训练采用 RMS loss；但 `cb_with_autoencoder_yw.ipynb` 的直接代码只调用默认 `CatBoostRegressor()`，没有显式记录 final model 的 loss、iterations、depth、learning rate 或 random seed。序列化 `.cbm` 可用于推理，却不足以重建训练过程。该 notebook 同时训练 XGBoost，并分别打印 Spearman，属于训练草稿而非完整可追溯 pipeline。

### 5. 输入 PDB 到特征的真实执行路径

公开 `ProBASS.ipynb` 是 Colab-first 单突变推理流程：

1. 下载用户给定 PDB，或使用上传文件。
2. 检查 mutated/partner chain 是否存在、PDB residue number 是否存在、三字母 WT residue 是否匹配输入（源约 154–276 行）。
3. 用 Bio.PDB 从 ATOM residue 提取两条链的氨基酸序列。
4. 将 PDB 编号换算为序列下标，替换目标残基并写 WT/mutant/partner FASTA（约 306–430 行）。
5. 分别运行 ESM-2 extract，保存 layer-33 token representation。
6. 用 ESM-IF1 编码 WT complex backbone。
7. 做 mean/delta/concatenate，加载 `.cbm` 并预测。

输入校验是必要的，但编号换算使用“position - first residue number + 1”。它假设残基编号连续且抽取序列与编号一一对应。PDB insertion code、missing residue、负编号、非标准残基、多 model 或 altloc 都可能破坏这个假设。校验扫描原始 ATOM 行也不等于保证后续 Bio.PDB 序列索引完全一致。

### 6. 六幅主图应该怎样解释

- **图 1：架构示意。** 展示 mutant/WT sequence 经 ESM-2、WT PPI structure 经 ESM-IF1、融合后由 CatBoost 输出 $\Delta\Delta G_{bind}$。图表达概念主干，直接 notebook 支持这一核心路径。
- **图 2：同一 PPI 内插。** 在 3OTJ 与 1CBW 内随机 80/20 划分并重复三次，论文报告相关约 0.77–0.91、RMSE 约 1.2 kcal/mol。同一复合体的 train/test 共享 PDB-level structural vector和相近 sequence landscape，因此这是较容易的内插场景。
- **图 3：跨 PPI 与多 PPI 训练。** 只用 3OTJ 训练、在 3SGB 测试时相关降到 0.41、RMSE 2.6；用 131 个 PDB 的 2135 个单突变训练、在 3SGB 的 190 个突变测试时相关升到 0.81。它说明多复合体标签可改善新 PPI 排序，同时正文也承认绝对值仍可能偏移。
- **图 4：全数据随机划分。** 所有单突变随机 80/20、重复五次，平均相关 0.81±0.02、RMSE 1.2。由于同一 PDB 的突变可以同时进入 train/test，这不是严格的 unseen-complex generalization。
- **图 5：双突变。** 在拥有约 13,000 个双突变的 3OTJ 和 1CBW 内训练测试，相关约 0.7、RMSE 2.3；跨 PPI 相关约 0.4，扩大多 PPI 训练也没有明显改善。数据被两个复合体主导，不能据此宣称一般双突变或 epistasis 已解决。
- **图 6：baseline 比较。** 论文比较 ProBASS、ESM-IF1、ProteinMPNN、ThermoMPNN 在多个 PDB 的 Spearman。ProBASS 在报告任务上最好，但仓库没有 baseline scoring、版本锁定、输入规范化和绘图脚本，因此这些数值是 paper-reported，而非当前代码可完整复算。

补充图/表进一步覆盖单 PPI、实验噪声上限、多个 leave-PDB-out、去掉结构特征、双突变 transfer、训练样本量和 outlier residue enrichment。补充 PDF 本地存在，但这些实验也没有对应完整脚本。

### 7. 数据划分比模型名字更影响结论

论文整合 SKEMPI 与实验室数据。训练/测试方式至少有四种含义不同的场景：

- 同一 PPI 内随机划分：测试插值与相似 landscape；
- 全数据库 mutation-level 随机划分：同一 PDB 可跨 split；
- 单 PPI 训练、另一 PPI 测试：最难且表现明显下降；
- 多 PPI 训练、held-out PPI 测试：更接近新复合体泛化。

不能把图 2/4 的约 0.8 相关直接当成任意新 PPI 的预期性能。论文在六个 unseen PDB 测试中给出的平均相关约 0.68、RMSE 1.85，更接近外推边界。数据中约 44% 来自 serine protease/inhibitor complexes，也可能让模型偏向这类 landscape；论文做了比例敏感性分析，但公开仓库没有可复查 split manifest。

同样，SAAMBE 在部分 SKEMPI PDB 上可能见过训练数据，论文因此改用实验室 3OTJ/1CBW 做更公平比较。这个例子说明 baseline 是否训练见过测试对象，比“模型总体排名”更重要。

### 8. 符号与方向必须在实际使用前确认

$\Delta\Delta G_{bind}$ 在文献中可能定义为 mutant minus WT，也可能采用相反符号；有的数据库还混合 affinity、dissociation constant 和不同实验条件的换算。论文与发布模型的训练标签方向应以 `Data_set.xlsx`、示例输出和论文定义联合确认。高正值究竟表示 destabilizing 还是 stabilizing，不能凭一般习惯推断。

当前 notebook 输出列名写作 predicted $\Delta\Delta G$ kcal/mol，但没有在 UI 中强制展示符号解释和适用温度/标准态。用于实验决策时应先用已知 mutation 做方向 sanity check，并同时报告预测值、PDB/chain/numbering、模型 snapshot 和输入结构来源。

### 9. 代码版本与可复现边界

克隆仓库的 `.git` 已被移除；合同必须使用 manifest 记录的 `91ae179…`。

仓库中可直接支持：单突变 Colab 输入验证、PDB/FASTA 处理、ESM-2/ESM-IF1 embedding、1792 维融合、已训练 CatBoost 推理，以及一个本地绝对路径驱动的 80/20 training sketch。仓库未完整支持：

- SKEMPI/实验室原始数据到 `Data_set.xlsx` 的可追溯清洗；
- 论文所有 repeated split 与 leave-PDB-out split manifests；
- double-mutant 全流程与 epistasis 处理；
- ESM-IF1、ProteinMPNN、ThermoMPNN、SAAMBE baseline 复算；
- final CatBoost 超参数、loss、seed 与训练日志；
- Figures 2–6 和补充图的生成脚本；
- outlier enrichment 的实现。

notebook 还在运行时安装未锁版本的 `facebookresearch/esm` 等依赖，并包含作者机器 `/home/PC/Desktop/...` 与 Colab `/content/ProBASS/...` 路径。没有环境 lockfile，未来依赖漂移可能改变加载行为。`Probass_model.cbm` 提供可部署快照，但若 CatBoost/ESM 版本不一致，完整复现仍需额外锁定。

### 10. 最可靠的使用姿势

把 ProBASS 当作候选排序器：先验证 PDB chain 与 numbering；尽量使用与训练分布相近、结构质量可靠的 soluble PPI；同时查看相关性和绝对误差；对 proline、glycine、bulky aromatic、界面重排或多突变尤其谨慎；最终用 SPR、ITC 或其他实验验证。

如果要证明新 PPI 泛化，必须按 PDB 或同源 cluster 隔离 split，而不是 mutation-level random split。如果要研究双突变，应显式建模/评估 epistasis，而不是假设两个单突变特征相加即可。

### 11. 一句话抓住 ProBASS

ProBASS 将 ESM-2 的 mutant-minus-WT 全链平均差分与 ESM-IF1 的 WT 复合体平均结构向量拼成 1792 维特征，再用实验标签训练 CatBoost。它的核心推理代码可以核查，但高性能强依赖数据划分，结构分支不随突变变化，完整 benchmark 与 final training 配置尚未公开复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ProBASS Summary

### Motivation and Novelty

ProBASS addresses a practical bottleneck in protein engineering and disease-variant interpretation: predicting how mutations change protein-protein binding affinity. The target is $\Delta\Delta G_{bind}$, the change in binding free energy caused by mutation. Measuring this value experimentally is slow, and even high-throughput mutational scans require substantial calibration.

Prior binding-affinity-change predictors often rely on hand-crafted structural energy terms, statistical potentials, graph features, or smaller machine-learning datasets. The paper cites earlier physics/statistical approaches as typically reaching only moderate correlations around 0.4-0.6, and notes that many machine-learning methods degrade sharply for double or higher-order mutations. ProBASS's novelty is to combine two pretrained protein language models as fixed feature extractors: ESM-2 for sequence context and ESM-IF1 for structure context, then fine-tune a CatBoost regressor on a large experimental $\Delta\Delta G_{bind}$ dataset.

Compared methods include BeAtMuSiC (Nucleic Acids Research, 2013), mCSM (Bioinformatics, 2014), MutaBind2 (iScience, 2020), SAAMBE-SEQ (Bioinformatics, 2021), ELASPIC2 (Journal of Molecular Biology, 2021), ESM-IF1 (2022), ProteinMPNN (Science, 2022), and ThermoMPNN (PNAS, 2024). The paper's core argument is that PLM features are useful, but task-specific fine-tuning on binding-affinity labels is essential.

### Method Overview

For each mutation, ProBASS builds WT, mutant, and partner-chain sequence representations. ESM-2 produces 1280-dimensional per-position sequence embeddings. The method averages the mutant-plus-partner and WT-plus-partner representations, then subtracts WT from mutant to obtain a sequence-delta feature.

In parallel, ProBASS runs ESM-IF1 on the WT complex structure. The structural embedding is averaged into a 512-dimensional vector. This WT structural vector is concatenated with the 1280-dimensional sequence delta to form a 1792-dimensional mutation feature. A CatBoost regressor maps this feature to predicted $\Delta\Delta G_{bind}$.

The public notebook implements single-mutation inference from a PDB ID or uploaded PDB plus chain/residue inputs. It validates the requested chain and WT residue, creates FASTA files, extracts PLM embeddings, loads the serialized CatBoost model, and outputs predicted $\Delta\Delta G$.

### Evaluation

The paper evaluates several regimes. Same-PPI single-mutation train/test splits for 3OTJ and 1CBW reach correlations around 0.8. Training on one PPI and testing on another performs poorly for 3SGB ($R=0.41$), but training on a multi-PPI dataset excluding 3SGB improves held-out prediction to $R=0.81$. A random whole-dataset single-mutation split reports $R=0.81\pm0.02$ / about $R=0.82$ in the figure, with RMSE around 1.2 kcal/mol.

For double mutations, ProBASS reaches lower but still meaningful within-PPI correlations: about $R=0.71$ for 3OTJ and $R=0.67$ for 1CBW. The authors do not claim broad double-mutation generalization, because double-mutant labels are dominated by these two complexes. Baseline comparisons show ProBASS outperforming ESM-IF1, ProteinMPNN, and ThermoMPNN across the displayed PDB panels, with SAAMBE discussed separately because of SKEMPI training overlap.

The most important interpretation nuance is that Figure 4's random split can include mutations from the same PDB in both train and test, while Figure 3's held-out-PPI test is the stronger generalization evidence.

### Reproducibility

**Rating: 3/5.**

The public repository is useful for inference and partially useful for understanding training features. It includes a Colab notebook, a serialized CatBoost model, a dataset workbook, example input, and notebooks that show feature construction and a basic train/test split. The core paper-code match for ESM-2 + ESM-IF1 feature construction is strong.

The main limitation is that the repository does not include full scripts for repeated evaluations, leave-PDB-out experiments, double-mutation figure generation, baseline scoring, SAAMBE filtering, or outlier enrichment. CatBoost hyperparameters and the exact RMS-loss configuration are also not transparent from the released training notebook. The work is therefore runnable as a predictor but not fully reproducible as a paper benchmark package.

### Practical Takeaway

ProBASS is best viewed as a PLM-feature-based regressor for prioritizing PPI interface mutations. It is strongest for single mutations and for settings represented by the training distribution. It is less certain for absolute calibration on new PPIs, double mutations outside the two high-data complexes, and mutations likely to induce local structural rearrangements not captured by WT C-alpha backbone embeddings.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
