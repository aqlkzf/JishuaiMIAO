---
layout: default
permalink: /paper-atlas/jointmolecularmodel-82858455/
title: "JointMolecularModel"
nav: false
wide: true
description: "JMM 的贡献是把“模型能否重构这个分子”变成一个与预测不确定性互补的可靠性问题：分类头回答 \\(y\\)，重构头检查模型是否理解 \\(x\\)，而陌生度把后者量化为可用于 OOD 检测和虚拟筛选的分数。"
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
      <span>Machine Learning Algorithm</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>JointMolecularModel</h1>
    <p>Molecular deep learning at the edge of chemical space</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/molML/JointMolecularModel" target="_blank" rel="noopener noreferrer" aria-label="Open code for JointMolecularModel">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Joint Molecular Model 方法详解

### 1. 这篇论文要解决什么问题？

分子性质预测模型通常只在很小的已标注训练集上学习，却要被用于数百万甚至数十亿个候选分子。真正有价值的候选往往恰好含有训练集中没有见过的新骨架，因此模型必须面对严重的分布偏移（out-of-distribution, OOD）。此时会出现两个矛盾：

1. 基于分子相似度的适用域（applicability domain）能够拒绝离训练集太远的分子，但也会系统性排除我们最想发现的新颖结构。
2. 预测不确定性允许模型处理新结构，但深度模型在 OOD 样本上可能仍然非常自信，不能可靠地提示预测失效。

论文提出 Joint Molecular Model（JMM）：让一个模型同时做“预测分子性质”和“重构输入分子”。如果共享表示无法让解码器重构某个分子，说明这个分子对模型而言不熟悉。作者把这种重构困难度定义为 **unfamiliarity（陌生度）**，并把它作为传统相似度和预测不确定性的补充 (`paper.md:26-49`)。

### 2. 核心直觉

JMM 的关键不在于“用自编码器提高分类准确率”，而在于把重构任务当作一个针对当前模型的分布探针。

```text
同一个分子 x
      |
      v
共享编码器得到 z
   /          \
  v            v
重构 x        预测 y
  |            |
模型是否理解   模型认为它是否有活性
这个结构？     以及预测有多不确定？
```

一个分类器可能对陌生分子给出很高的活性概率和很低的不确定性；重构分支则额外检查：共享表示 \({\bf z}\) 是否保留了足够信息，能够重新生成输入 SMILES。图 1 的位图直接展示了这一双分支结构，以及重构损失与陌生度的对应关系 (`images/figure_01.png`)。

### 3. 输入、输出与符号

| 符号 | 含义 | 代码中的形式 |
|---|---|---|
| \(x\) | 清洗、规范化后的 SMILES | 整数 token 矩阵 \((N,C)\) |
| \(t_i\) | SMILES 中第 \(i\) 个非 padding token | 类别索引 |
| \({\bf z}\) | 编码器生成的共享分子表示 | 每个分子一个 128 维向量 |
| \(y\) | 二分类性质标签 | 每个分子一个类别索引 |
| \(p_m(y\mid x)\) | 第 \(m\) 个 MLP 的分类概率 | \((N,K,2)\)，\(K=10\) |
| \(\mathbb{E}(y\mid x)\) | 集成平均的活性概率 | 标量 |
| \(\mathbb{H}(y\mid x)\) | 熵型预测不确定性 | 标量 |
| \(\mathbb{U}(x)\) | 陌生度 | log 长度归一化重构损失 |

模型输出包括 token 预测、分类集成的 log probability、重构损失、分类损失、总损失、标签和原始 SMILES (`repo/jcm/models.py:559-640`)。

### 4. 从原始分子到最终筛选的完整流程

```text
原始分子记录
   |
   v
RDKit 清洗：去盐/溶剂/立体标记，规范化、电荷和元素过滤，canonical SMILES
   |
   +--------------------------+
   |                          |
   v                          v
ChEMBL 无标签分子             33 个有标签数据集
随机 80/10/10                环状骨架 + 谱聚类
   |                          train_ID / test_ID / test_OOD
   v                          |
预训练 SMILES 自编码器         v
   |                       预训练性质分类器
   +------------+-------------+
                v
        用预训练权重初始化 JMM
                |
   x -> token embedding -> 1D CNN -> z
                                / \
                  conditioned LSTM   10 个 anchored MLP
                      重构 x              预测 y
                                \       /
          L_JMM = L_reconstruction + gamma L_MLP
                |
                v
推理：活性 E(y|x)、不确定性 H(y|x)、陌生度 U(x)
                |
       可靠性/OOD 分析 或 多目标虚拟筛选
                |
          相似度过滤 + 实验验证
```

### 5. 数据清洗和人为构造 OOD 测试集

#### 5.1 分子清洗

论文将每个分子表示为 SMILES，并为对照实验计算半径为 2 的 2048-bit ECFP 和 CATS 药效团描述符。RDKit 流程去除立体化学 token、盐和溶剂，执行 sanitization、预定义中和反应和 canonicalization，并排除带形式电荷、不支持元素、复杂环编号或超过 100 个 token 的分子 (`paper.md:242-268`)。

33 个有标签数据集来自 29 个 MoleculeACE 靶点、3 个 LIT-PCBA 任务和 Ames 致突变性数据。约 120 万个 ChEMBL v33 分子用于自编码器预训练；与有标签数据集骨架过于相似的 ChEMBL 分子会被移除，避免预训练阶段泄漏测试骨架 (`paper.md:251-265`)。

#### 5.2 谱聚类切分

作者没有随机挑选 OOD 分子，而是先提取 cyclic skeleton，再根据 ECFP Tanimoto 相似度构造亲和矩阵 \(A\)。归一化图拉普拉斯矩阵为

$$
L_{\mathrm{sym}}=I-D^{-1/2}AD^{-1/2},
$$

并做特征分解

$$
L_{\mathrm{sym}}={\bf U}\Lambda {\bf U}^{T}.
$$

对特征值曲线找 elbow 来决定簇数 \(k\)，再对谱嵌入做 k-means。与其他簇平均相似度最低的簇依次加入 `test_OOD`，直到接近 25%；剩余分子随机分成约 50% 的 `train_ID` 和约 25% 的 `test_ID` (`paper.md:318-344`)。

这一流程在代码中是 **Exact**：`split_finetuning_data` 完成 cyclic skeleton、ECFP、Tanimoto 矩阵、谱聚类和低相似度簇选择；`split_data` 让 `test_ID` 的实际大小等于 `test_OOD` (`repo/experiments/2.0_split_data.py:156-243`)。图 1c 也直接画出了从骨架到谱聚类再到 50/25/25 切分的过程。

### 6. 模型内部：每一步究竟算什么？

#### 6.1 编码器：SMILES 到共享表示 z

整数 token 先进入可学习的 128 维 embedding。张量从 \((N,C,E)\) 转成 CNN 使用的 \((N,E,C)\)，经过 1D 卷积、ReLU、max pooling 和 dropout，flatten 后由全连接层压缩为 \({\bf z}\)。论文设置 \(\dim({\bf z})=128\) (`paper.md:410-414`)。

直接代码证据位于 `Encoder.forward` 和 `CNN.forward` (`repo/jcm/modules/encoder.py:15-136`)。JMM 实验会根据预训练模型配置决定是否使用 VAE；当前论文所用常规 AE 路径与论文“VAE 没有带来收益”的说明一致 (`repo/experiments/4.4_jmm.py:79-113`; `paper.md:449-460`)。

#### 6.2 解码器：z 到重构 SMILES

一个线性层把 \({\bf z}\) 扩展成 LSTM 每一层的初始 hidden state。解码从 start token 开始，每一步输出下一个 token 的 log probability。没有 teacher forcing 时，当前步的 `argmax` token 会作为下一步输入。

对分子 \(x\)，论文定义长度归一化的重构损失：

$$
&#123;&#123;\mathscr{L}}}_{\mathrm{reconstruction}}(x)
=-\frac{1}{|x|}\sum_{i\in x}\log p(t_i\mid t_{<i}).
$$

代码使用 `NLLLoss(reduction='none', ignore_index=padding)`，逐 token 累加后除以非 padding 长度；因此长 SMILES 不会仅因为 token 更多而天然得到更高损失 (`repo/jcm/modules/rnn.py:111-217`)。

#### 6.3 预测头：anchored MLP ensemble

同一个 \({\bf z}\) 被送入 10 个 MLP。每个 MLP 用不同随机种子初始化，并把初始参数保存为 anchor。训练时不仅最小化分类 NLL，还惩罚参数离开各自 anchor：

$$
&#123;&#123;\mathscr{L}}}_{\mathrm{MLP}}
=-\frac{1}{M}\sum_{m=1}^{M}\log p_m(y\mid x)
+\lambda\lVert\theta^m-\theta^m_{\mathrm{anchor}}\rVert^2.
$$

预测均值为

$$
\mathbb{E}(y\mid x)=\frac{1}{M}\sum_{m=1}^{M}p_m(y\mid x).
$$

`Ensemble`、`AnchoredLinear` 和 `anchored_loss` 直接实现了 10 个独立种子、anchor buffer、平均损失和 L2 anchor 正则 (`repo/jcm/modules/mlp.py:16-190`)。

#### 6.4 联合损失

论文的联合目标是

$$
&#123;&#123;\mathscr{L}}}_{\mathrm{JMM}}
= &#123;&#123;\mathscr{L}}}_{\mathrm{reconstruction}}
+\gamma &#123;&#123;\mathscr{L}}}_{\mathrm{MLP}},\qquad \gamma=0.1.
$$

`JMM.forward` 的数据流与这个公式一致：编码一次得到 `z`，分别送入 decoder 和 MLP，再把逐分子的重构损失与缩放后的预测损失相加 (`repo/jcm/models.py:504-557`)。

但当前代码快照存在一个重要 **Partial**：训练脚本传入的是 `mlp_loss_scalar=0.1`，而模型读取的是 `gamma`；默认 YAML 中 `gamma=1` (`repo/experiments/4.4_jmm.py:306-310`; `repo/experiments/hyperparams/jmm_default.yml:43-49`)。因此“模型代码实现了加权损失”是确定的，但“这个快照实际以 \(\gamma=0.1\) 训练”没有被现有文件证明。

### 7. 训练顺序

1. **自编码器预训练**：ChEMBL，batch 256，最多 1,000,000 steps，Adam，梯度范数截断为 5，每 10,000 steps 验证，early-stopping patience 最多 20。
2. **性质分类器预训练**：每个有标签数据集做十次 Monte Carlo 交叉验证，每次拿训练集 10% 验证；batch 64，类别平衡采样，最多 5,000 steps。
3. **JMM 微调**：decoder 从 ChEMBL AE 初始化，encoder/MLP 从目标数据分类器初始化；batch 64，最多 10,000 steps，每 20 steps 验证，patience 50。论文报告 encoder/classifier 学习率 \(3\times10^{-6}\)，decoder 学习率 \(3\times10^{-7}\) (`paper.md:469-501`)。

`setup_jmm_config` 合并预训练 AE 和分类器配置与权重；`run_models` 按 seed 恢复对应 split 并启动训练 (`repo/experiments/4.4_jmm.py:79-203`)。`Trainer.run` 实现采样、forward/backward、梯度截断、optimizer step、callback、early stopping 和最佳 checkpoint 恢复 (`repo/jcm/training.py:150-247`)。

### 8. 推理时如何得到三个筛选指标？

#### 8.1 陌生度

论文定义

$$
\mathbb{U}(x)=\log &#123;&#123;\mathscr{L}}}_{\mathrm{reconstruction}}(x).
$$

低值表示容易重构，模型对结构更熟悉；高值表示 token 概率低、重构困难。`JMM.predict` 返回每个分子的 `reconstruction_loss`，主回顾性分析的 R 脚本明确执行 `ood_score = log(reconstruction_loss)`，因此 Eq. (2) 在这条分析路径上是 **Exact** (`repo/jcm/models.py:559-640`; `repo/plots/scripts/1.0_data_prep.R:135-151`)。

#### 8.2 活性期望

代码把 10 个分类器的概率取平均，再取正类概率 `y_E`。这对应论文的 \(\mathbb{E}(y\mid x)\) (`repo/experiments/5.2_inference_jmm.py:78-105`)。

#### 8.3 预测不确定性

论文展示的 Eq. (12) 是各 ensemble member 熵的平均：

$$
\mathbb{H}(y\mid x)
=-\frac{1}{M}\sum_{m=1}^{M}p_m(y\mid x)\log p_m(y\mid x).
$$

但主要推理工具 `logits_to_pred` 调用 `predictive_entropy`：先对 ensemble 概率取平均，再计算一次熵 (`repo/jcm/utils.py:51-65`, `repo/jcm/utils.py:82-106`)。代码里虽然存在 `mean_sample_entropy`，但这条推理路径没有调用它。因此不确定性公式是 **Partial**，阅读结果时不应把论文公式和代码实现当成完全相同。

#### 8.4 一个不能误用的代码分支

`JMM` 还保存了一份冻结的预训练 decoder，并可计算“微调 decoder 重构损失 - 预训练 decoder 重构损失”的 `ood_score` (`repo/jcm/models.py:478-502`, `repo/jcm/models.py:611-617`)。这是已验证的代码行为，但论文展示的陌生度是 log 重构损失，主绘图脚本也使用后者。没有额外证据时，不能把这个差分分数解释成论文 Eq. (2)。

### 9. 实验如何证明陌生度有用？

#### 9.1 33 个数据集上的人为分布偏移

图 2 的位图直接显示：

- `test_OOD` 的骨架相似度、MCS 核心重叠和 CATS 药效团相似度都低于 train/test-ID；
- 所有模型在 OOD 上 balanced accuracy 下降；
- OOD 分子的陌生度整体右移；
- 陌生度越高，分子核心与训练集的重叠越低。

JMM 在 test-ID 上的 balanced accuracy 为 \(0.75\pm0.02\)，ECFP MLP 为 \(0.78\pm0.02\)。加入 decoder 没有产生显著分类性能损失 (`paper.md:111-120`)。这说明重构分支提供了额外可靠性信号，而不是用明显更差的分类器换来的。

#### 9.2 约 140 万个商业分子

图 3 中，商业库相对训练集的结构相似度更低；不确定性分布与 test-ID 大量重叠，而陌生度分布几乎整体右移。论文报告 library vs test-ID 的 KS 效应量：不确定性 \(D=0.181\)，陌生度 \(D=0.999\)。两者相关性接近零，\(r=-0.03\pm0.03\) (`paper.md:152-178`)。

这里必须注意：商业库没有标签，所以这个结果证明的是“陌生度能发现很强的分布偏移”，不能直接证明库中每个预测的实际误差。

#### 9.3 前瞻性激酶筛选

作者用三个目标做 utopia-point 排序：高预测活性、低/高不确定性、低/高陌生度。对每个目标设置三种组合：

- A：高活性、高不确定性、低陌生度；
- B：高活性、低不确定性、低陌生度；
- C：高活性、低不确定性、高陌生度。

各目标过滤掉与训练集或已选分子 ECFP Tanimoto 相似度不低于 0.70 的候选。标准化后的多目标距离为

$$
d_{\mathrm{utopia}}=\sqrt{\sum_{i=1}^{n}(\mathrm{norm}_i)^2}.
$$

代码实现了 min-max 归一化、最大化/最小化方向、三种组合和相似度过滤 (`repo/experiments/8.7_rank_molecules_prospective.py:32-215`)。

共购买并测试 60 个分子。论文报告 PIM1 有 5 个、CDK1 有 2 个化合物表现出清晰的 dose-response 抑制，hit rate 分别约 17% 和 7%；这些 hit 与训练分子的最大 ECFP 相似度都低于 0.38 (`paper.md:209-221`)。图 4 直接展示了三组候选在 uncertainty-unfamiliarity 空间的位置、单浓度活性和部分 IC50。

五个低微摩尔化合物来自策略 A，但每个策略每个靶点仅测试 10 个分子，而且不是完整的 2 x 2 因子设计。合理结论是“联合使用陌生度和不确定性能够找到结构新颖的活性分子”，而不是“策略 A 已被证明普遍最优”。

### 10. 读代码时最容易忽略的三点

1. **陌生度的 log 并不在模型类内部。** `JMM.predict` 返回重构损失，回顾性 R 数据准备才取 log。
2. **前瞻性流程使用 raw reconstruction loss。** `8.6_process_results_prospective.py` 直接把 `reconstruction_loss` 重命名为 `unfamiliarity`，没有取 log。log 是严格单调的，所以高低排序不变，但 min-max 距离和数值尺度会变化。
3. **不确定性和 gamma 均有纸码差异。** 一个是公式位置不同（mean entropy vs predictive entropy），另一个是配置字段不同（`mlp_loss_scalar` vs `gamma`）。这些差异不会否定 JMM 主体结构，但会影响精确复现。

### 11. 可复现性边界

- 本地代码快照包含模型、训练、推理、切分、绘图和筛选脚本，核心架构可直接定位。
- 本地 `repo/data/` 只有说明文件和 `__init__.py`，处理后的数据、商业分子结构和训练 checkpoint 不在快照中，需要 Zenodo/Figshare 及许可数据。
- 脚本依赖固定目录、实验名称和若干作者/HPC 绝对路径；没有发现自动化测试或面向任意数据集的统一 CLI。
- 本次分析没有运行训练或重生成论文数值，因此“代码行为”指静态源代码验证，不等价于运行时复现。

### 12. 一句话总结

JMM 的贡献是把“模型能否重构这个分子”变成一个与预测不确定性互补的可靠性问题：分类头回答 \(y\)，重构头检查模型是否理解 \(x\)，而陌生度把后者量化为可用于 OOD 检测和虚拟筛选的分数。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Molecular Deep Learning at the Edge of Chemical Space

### Problem

Molecular property models are often deployed on compounds structurally unlike their small labelled training sets. Similarity-based applicability domains can protect against unreliable predictions but also exclude the novel chemistry sought in drug discovery. Predictive uncertainty is more permissive, yet can remain overconfident under distribution shift. The paper therefore asks whether the model's ability to reconstruct a molecule can expose when its learned representation is operating outside familiar chemical space (`paper.md:26-49`).

### Proposed Method

The Joint Molecular Model (JMM) represents a canonical SMILES string with a one-dimensional CNN and shares the resulting 128-dimensional latent vector \({\bf z}\) between two branches:

1. a conditioned LSTM reconstructs the input SMILES;
2. an anchored ensemble of ten MLPs predicts a binary molecular property and supplies an entropy-based uncertainty score.

Training combines reconstruction and property losses. The paper defines **unfamiliarity** as the logarithm of length-normalized token reconstruction loss,

$$
\mathbb{U}(x)=\log &#123;&#123;\mathscr{L}}}_{\mathrm{reconstruction}}(x).
$$

Poorly reconstructed molecules have higher unfamiliarity and are interpreted as farther from the distribution learned by the shared model (`paper.md:58-80`, `paper.md:410-460`). Unlike a fixed scaffold or fingerprint threshold, the score is conditioned on what the model learned; unlike prediction uncertainty, it measures information retained about the input structure.

### Evaluation and Main Results

The study uses 33 labelled datasets: 29 MoleculeACE targets, three LIT-PCBA tasks and Ames mutagenicity. Cyclic molecular skeletons are spectrally clustered, with the most distant clusters assigned to a roughly 25% OOD test set; train and in-distribution test sets comprise roughly 50% and 25%. ECFP Tanimoto, maximum-common-substructure fraction and CATS pharmacophore similarity confirm that this split induces a structural distribution shift (`paper.md:83-105`, `paper.md:318-344`).

- All evaluated classifiers lose balanced accuracy on OOD molecules. On the in-distribution tests, JMM achieves \(0.75\pm0.02\) balanced accuracy versus \(0.78\pm0.02\) for an ECFP MLP. Adding the reconstruction decoder produces no significant classification penalty (`paper.md:111-117`).
- OOD molecules have significantly higher unfamiliarity than in-distribution molecules across the 33 datasets. Unfamiliarity relates to several complementary train-set similarity measures and to prediction performance, while being nearly independent of prediction uncertainty (reported Spearman \(r=0.10\pm0.05\) on labelled datasets; `paper.md:117-149`).
- Across about 1.4 million commercial molecules, unfamiliarity exposes a far larger shift relative to test-ID than uncertainty (reported KS \(D=0.999\) versus \(D=0.181\)). Uncertainty and unfamiliarity remain nearly independent (\(r=-0.03\pm0.03\); `paper.md:152-178`).
- A prospective screen combines predicted activity, uncertainty and unfamiliarity through distance to a normalized utopia point. Sixty low-similarity compounds were tested against PIM1 and CDK1. Five PIM1 and two CDK1 compounds showed clear dose-response inhibition, giving reported hit rates of about 17% and 7%; all identified hits had maximal ECFP similarity below 0.38 to training molecules (`paper.md:181-221`).

Five of the seven low-micromolar compounds came from the low-unfamiliarity/high-uncertainty strategy. The authors correctly frame this as preliminary: only ten molecules were tested per strategy and the design was not a full 2 x 2 factorial experiment, so the data support prospective feasibility rather than a definitive strategy ranking.

### Relation to Existing Reliability Approaches

Similarity-based applicability domains, formalized in prior cheminformatics work including *SAR and QSAR in Environmental Research* (2016) and *Molecular Informatics* (2016), impose a preselected structural metric and boundary. That is transparent but can systematically reject novel scaffolds. Modern uncertainty approaches, including molecular applications in *ACS Central Science* (2021), *Briefings in Bioinformatics* (2023), and OOD evaluations in *Journal of Chemical Information and Modeling* (2020, 2024), estimate confidence in \(p(y\mid x)\) but can be poorly calibrated after a large distribution shift. JMM contributes a complementary learned signal: reconstruction asks how well the shared representation explains \(x\), while the classifier estimates \(y\).

### Reproducibility and Code Match

**Reproducibility: 3/5. Code-paper fidelity: medium.**

The GitHub snapshot at commit `73ff464e013d70db76f0fdec32cde1b5dc9e0db6` contains the core architecture, length-normalized reconstruction loss, anchored ensemble, spectral split, training/inference scripts, plotting scripts and prospective utopia ranking. Direct source verifies the central dataflow (`repo/jcm/models.py:446-640`) and the retrospective plotting pipeline implements \(\log(\text{reconstruction loss})\) (`repo/plots/scripts/1.0_data_prep.R:135-151`).

Full reproduction is not turnkey. Processed datasets and trained checkpoints are external; commercial structures are restricted; the local `repo/data/` contains no experiment data; scripts assume fixed folder layouts and some hard-coded author/HPC paths; no automated tests or general arbitrary-dataset CLI were found. Three code-paper differences matter:

- the launcher supplies `mlp_loss_scalar=0.1`, while the model reads `gamma` and the checked default is `gamma: 1`, so the reported effective \(\gamma=0.1\) is not demonstrated;
- the paper's displayed uncertainty is mean per-member entropy, while inference uses entropy of the ensemble-mean probabilities;
- prospective ranking renames raw reconstruction loss as unfamiliarity, whereas the paper defines its logarithm. This preserves ordering but changes the numerical scale and min-max distances.

The local main figures were all inspected. Supplementary Figs. 1-12/Tables 1-4 and the source-data archives were not acquired as local evidence, and no training or result regeneration was run.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
