---
layout: default
permalink: /paper-atlas/multipartite-entanglement-classification-qda-b23417b5/
title: "Multipartite_Entanglement_Classification_QDA"
nav: false
wide: true
description: "对多体量子态，仅判断“有无纠缠”还不够，还需要判断各模式按什么结构可分。例如三模态 \\(A,B,C\\) 可分为三类：完全可分 \\(1\\otimes1\\otimes1\\)、某一个模式与另外两个模式分开的 \\(1\\otimes2\\)、以及完全不可分。 对于任意非高斯连续变量（CV）态，这件事很难：完整量子态层析代价高；只依赖二阶矩的判据又可能看不到高阶非高斯关联。"
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
    <h1>Multipartite_Entanglement_Classification_QDA</h1>
    <p>Classifying multipartite continuous-variable entanglement structures through data-augmented neural networks</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-026-01284-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Multipartite_Entanglement_Classification_QDA">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/XiaotingGaoPhys/Multipartite-Entanglement-Classification-QDA" target="_blank" rel="noopener noreferrer" aria-label="Open code for Multipartite_Entanglement_Classification_QDA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 用量子数据增强识别多体连续变量纠缠结构

### 1. 这篇论文要解决什么问题？

对多体量子态，仅判断“有无纠缠”还不够，还需要判断各模式按什么结构可分。例如三模态 \(A,B,C\) 可分为三类：完全可分 \(1\otimes1\otimes1\)、某一个模式与另外两个模式分开的 \(1\otimes2\)、以及完全不可分。

对于任意非高斯连续变量（CV）态，这件事很难：完整量子态层析代价高；只依赖二阶矩的判据又可能看不到高阶非高斯关联。神经网络可以直接学习“实验上可测的零差探测统计量到纠缠结构”的映射，但训练集生成、完整密度矩阵计算和可靠标注会随模式数与非高斯复杂度迅速变贵。

论文的核心思路是：先用物理模拟产生少量可靠样本，再利用不改变纠缠结构标签的物理变换，在相关图样层面廉价扩充数据。这就是 quantum data augmentation（QDA，量子数据增强）。

### 2. 输入、输出和监督信号

**输入**不是密度矩阵，也不是简单的二阶相关系数，而是二维联合正交分量概率分布经过离散化后得到的 \(24\times24\) 相关图样。

**输出**是纠缠结构类别的 softmax 概率：三模态为 3 类，四模态为 5 类，五模态为 7 类。

**训练标签**来自模拟态的完整密度矩阵。论文先按目标可分结构组合种子态，并用量子 Fisher 信息（QFI）判据筛选完全不可分的种子态，因此训练时的 \({\mathcal S}_{\rm True}\) 是由完整态信息确定的；推理时才只需要零差探测图样。

### 3. 完整计算流程

```text
随机生成有限/无限 stellar rank 的 CV 种子态
  -> 随机高斯操作与光子损耗
  -> 按目标多重划分组合量子态
  -> 用完整密度矩阵和 QFI 判据生成可靠标签
  -> 平衡分束器混合模式 + 零差探测联合概率
  -> 每个联合分布离散为 24 x 24 图样
  -> 每 4 个图样组成一个“面向某个划分”的输入组
  -> 对训练图样做 QDA
       1. 模式置换：交换/转置图样，标签不变
       2. 凸组合：混合完全可分样本，标签不变
  -> 各输入组经过共享参数 CNN
  -> 拼接特征 -> 全连接层 -> softmax 类别
  -> 在未见测试态上计算准确率与归一化混淆矩阵
```

论文描述了整条流程；当前代码快照只从“读取已经生成好的 HDF5 图样与标签”开始，前面的量子态生成、QFI 标注、概率计算和离散化都不在仓库中。

### 4. 量子态和标签如何构造？

有限 stellar rank 的 \(m\) 模种子态写为

$$
\hat{\sigma}_m=\left(\prod_{l=1}^{m}\hat L_l(\eta_l)\right)\hat G|C(r)\rangle\langle C(r)|\hat G^\dagger
\left(\prod_{l=1}^{m}\hat L_l^\dagger(\eta_l)\right).
$$

其中 \(|C(r)\rangle\) 是 stellar rank 为 \(r\) 的有限 Fock 支撑核心态，\(\hat G\) 是随机多模高斯幺正操作，\(\hat L_l(\eta_l)\) 是第 \(l\) 个模式的损耗通道。论文考虑 \(r\in\{0,1,2,3,+\infty\}\)，无限 rank 的样本包含纠缠猫态。

将一模、二模等种子态做张量积即可构造不同可分结构。为避免“本应完全不可分的种子态实际还能再分”，作者优化局域算符 \(\hat A\)，检查所有 \(k\)-可分态应满足的关系

$$
F_Q(\hat\rho_k,\hat A)\leq4V(\hat\rho_k,\hat A).
$$

这里的关键区别是：QFI 只用于模拟训练集的可靠标注，并不是部署时的输入。仓库没有实现这一步，也没有本地补充材料给出足以重建数据集的全部随机参数分布。

### 5. 为什么输入是 12 张相关图样？

以三模态为例，平衡分束器先混合 \(B,C\)，再联合测量未混合模式 \(A\) 与一个输出模式 \(M_{BC}\)。代表性联合概率为

$$
{\mathcal P}(X_A,X_{M_{BC}})=
\left\langle X_A;\frac{X_B+X_C}{\sqrt2}\middle|\hat\rho\middle|X_A;\frac{X_B+X_C}{\sqrt2}\right\rangle.
$$

对一个划分方向，取 \((X,X),(X,P),(P,X),(P,P)\) 四种组合；再考虑 \(A-BC\)、\(B-AC\)、\(C-AB\) 三个方向，一共得到 12 个联合分布。每个分布被分箱为 \(24\times24\)，形成

$$
{\mathcal C}=\&#123;&#123;\mathcal C}_{AM_{BC}}, {\mathcal C}_{M_{AC}B}, {\mathcal C}_{M_{AB}C}\},
$$

其中每个集合含 4 个通道。代码直接验证了这个张量接口：`main.py:73-88` 将 `[N,12,24,24]` 切成三个 `[N,24,24,4]` 输入。四模态和五模态对应 16 与 20 个通道。

### 6. QDA 的两个操作

#### 6.1 模式置换

如果任务标签只描述每个子系统的大小，那么给模式重新命名不会改变标签。例如 \(A|BC\) 与 \(B|AC\) 都属于 \(1\otimes2\)。模式交换在图样上表现为：交换四通道分组、对部分图样做对角转置/翻转，并交换相应的中间通道。

这一步不需要重新计算密度矩阵和零差概率，因此成本远低于重新模拟量子态。理论上 \(m\) 模态最多可由排列扩充到 \(m!\) 倍。代码中：

- `QDA.py:4-54` 实现三模态和四模态的一次模式对换；
- `QDA.py:68-233` 组合出 6 个三模态顺序和 24 个四模态顺序；
- `QDA.py:242-290` 从五模态的 120 个排列中选取指定数量并保持标签。

#### 6.2 完全可分态的凸组合

完全可分态集合是凸集：

$$
\rho'=\lambda\rho_1+(1-\lambda)\rho_2,
\qquad 0\leq\lambda\leq1.
$$

测量概率对 \(\rho\) 线性，因此可以直接对两组相关图样做相同比例的加权平均，得到新的完全可分样本。论文主结果中的增强样本由 97% 模式置换和 3% 凸组合构成。

代码的 `QDA.py:56-66` 有一个仅面向 12 通道输入的 `data_aug_add`，会从同一 one-hot 标签中选两个样本做随机混合。但它没有接入 `TripartiteQDA`，`main.py` 也从未调用它。因此“论文方法包含两种 QDA”是论文事实，而“当前入口可执行两种联合增强”并不成立。

### 7. CNN 如何处理这些图样？

每个四通道组进入同一个共享参数特征提取器：

```text
24 x 24 x 4
  -> 3x3 Conv(32) + ReLU + 2x2 MaxPool
  -> 3x3 Conv(64) + ReLU + 2x2 MaxPool
  -> 3x3 Conv(128) + ReLU + 2x2 MaxPool
  -> Flatten -> Dense(1024) -> Dropout(0.7)
  -> Dense(256) -> Dropout(0.5) -> Dense(8)
```

三/四/五个分组的 8 维特征随后被拼接，再经过小型全连接分类头。`sharedCNN.py:5-85` 直接实现了 3、5、7 类 softmax 输出。共享分支让不同划分方向使用同一种特征提取规则，这是代码可验证的结构事实；它是否是性能提升的独立原因，论文图表并没有单独消融。

`main.py:56-88` 使用 Adam（学习率 0.001）、categorical cross-entropy、batch size 256、30% validation split 和 patience 50 的 early stopping。当前文件实际设置 `Nepochs=10`，旁边却写着 `# 2000`，无法从快照确定论文实验使用的精确配置。

### 8. 论文报告了什么结果？

三模态任务中，基于有限图样重建密度矩阵再做 QFI 的基线为 0.370，欧氏最近邻为 0.575。CNN 从未增强的 0.961 提升到六倍数据下的 0.986；Fig. 3 的三个类别对角值为 0.995、0.983、0.984。

四模态最近邻为 0.485，CNN 从 0.796 提升到 24 倍增强下的 0.928。初始输入对 \(2\otimes2\) 划分表达不足，该类仅 0.835；加入针对性的附加相关图样后，该类提升到 0.922，平均准确率达到 0.969。

有限采样测试中，只用理想图样训练的 QDA 模型在 100 个 Monte Carlo 噪声样本上达到 0.950；训练时加入 300 个噪声样本后达到 0.970。五模态任务经 100 倍排列增强后由 76.7% 提升到 92.4%。这些是论文报告值，并由本地 Figs. 3-5 的可见曲线/矩阵部分支持；本分析没有重新运行实验。

### 9. 如何理解这个方法的价值与边界？

QDA 的价值不是凭空创造新的量子信息，而是把已知的目标不变性变成训练数据：昂贵的量子态模拟只做一次，之后在小型图样数组上生成等价视角。它特别适合“有效样本昂贵、但标签对某些操作不变”的任务。

边界同样重要：论文主要评估模拟数据与模拟噪声，尚不能等同于真实实验设备上的泛化；当原始数据越来越多时，增强的边际收益下降；模式数继续增加时，状态生成、标注、特征设计和训练成本仍会增长。

### 10. 代码可复现性结论

**代码-论文匹配度：中等。** 四个 Python 文件确实覆盖数据加载、输入分组、共享 CNN、模式置换、一个独立凸组合辅助函数、训练以及准确率/混淆矩阵。但当前 `main.py` 的所有 QDA 调用都被注释，实际入口只训练未增强的三模态分支。

**Not found / 缺失范围：**仓库没有 HDF5 数据、依赖版本或环境文件、测试、量子态生成、QFI 标注、零差概率模拟、分箱代码、论文所述 97/3 联合增强流程或逐实验配置。仓库 README 提供外部数据链接，但该数据未进入本地工作区。因此快照适合核对分类器和置换逻辑，却不能独立复现论文数值结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Classifying Multipartite Continuous-Variable Entanglement with QDA

### Problem

Multipartite entanglement detection must identify not just whether a state is entangled, but how its modes separate into subsystems. For arbitrary non-Gaussian continuous-variable (CV) states, full tomography is costly and second-order criteria can miss higher-order correlations. A neural classifier could use experimentally accessible homodyne measurements instead, but generating diverse, reliably labelled training states becomes rapidly more expensive as mode count and non-Gaussian complexity grow.

### Proposed Approach

Gao et al. introduce a data-augmented CNN that maps binned homodyne joint-probability distributions to multipartition classes. Random Gaussian and non-Gaussian seed states are composed into known separability structures and checked with a quantum Fisher information criterion. Balanced beamsplitters expose correlations between one mode and mixed combinations of the others; four \(X/P\) probability distributions per splitting are binned to \(24\times24\) patterns. A shared CNN processes each four-pattern group, concatenates the learned features, and predicts one of 3, 5, or 7 classes for three-, four-, or five-mode systems.

The main novelty is **quantum data augmentation (QDA)** derived from label-preserving physics. Mode permutations rearrange/transpose correlation patterns while leaving the partition-size label unchanged, expanding an \(m\)-mode dataset toward \(m!\) orderings without recomputing density matrices. Convex mixtures of fully separable states provide a second valid augmentation because separability is convex and measurement probabilities are linear. The reported main experiments use 97% permutation-derived and 3% convex-combination samples.

### Evaluation and Results

On unseen simulated data, a QFI baseline applied after imperfect maximum-likelihood reconstruction reaches 0.370 accuracy for tripartite states; Euclidean nearest neighbour reaches 0.575 for tripartite and 0.485 for quadripartite states. The CNN without QDA reaches 0.961 and 0.796, respectively. With sixfold tripartite augmentation, accuracy rises to 0.986 and every class exceeds 0.983 in the displayed confusion matrix. With 24-fold quadripartite augmentation, accuracy rises to 0.928; the initial \(2\otimes2\) class remains weakest at 0.835 because the original inputs underrepresent that split. Adding targeted correlation patterns raises that class to 0.922 and average accuracy to 0.969.

The paper also reports robustness to finite homodyne sampling: QDA models trained on ideal patterns score 0.950 on 100 Monte Carlo-noisy samples, increasing to 0.970 when 300 noisy samples are added to training. For five modes, 100-fold permutation augmentation raises accuracy from 76.7% to 92.4%. Local figure reads support the accuracy curves, classwise confusion patterns, feature-space separation, and the form of the finite-sampling perturbation.

### Interpretation and Limitations

QDA is most useful when valid quantum training examples are expensive but the target property has known invariances. It moves work from costly state simulation to cheap transformations of measured-feature arrays. The paper's own training-size study shows diminishing benefit as the original dataset grows, and scaling still faces increasing costs in state generation, labelling, feature construction, and model training. All evaluations are based on simulated data, including simulated experimental imperfections; transfer to real hardware remains to be demonstrated.

### Reproducibility Assessment

**Code-paper fidelity: medium.** The four-file GitHub snapshot directly implements HDF5 loaders, 12/16/20-channel grouping, shared CNNs, mode-permutation QDA, a standalone tripartite convex-mixture helper, categorical-cross-entropy training, accuracy, and normalized confusion matrices. However, all QDA calls are commented in the active `main.py`; the convex-mixture helper is never integrated; and the checked-in default trains only 10 epochs despite a `# 2000` comment.

The snapshot contains no HDF5 datasets, dependency/environment manifest, tests, state-generation code, QFI labelling, homodyne simulation, or binning pipeline. The repository README links an external data bundle, but it was not acquired into this workspace. The supplementary PDF is linked by the paper but not available as local Markdown. Consequently, the paper's numerical results were **not reproduced** here, and a fresh user cannot run a paper-matching experiment from this snapshot alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
