---
layout: default
permalink: /paper-atlas/nicheflow-58c892d3/
title: "NicheFlow"
nav: false
description: "时序空间转录组通常在不同发育阶段切取不同组织，测量是破坏性的，因此 t0 与 t1 没有同一个细胞可直接追踪。许多方法把每个细胞单独作为运输单位，只预测“这个细胞的后代可能在哪里”。NicheFlow 的核心改变是把一个中心细胞周围的局部邻域视为整体 microenvironment（niche），同时生成其中所有细胞的表达状态和空间坐标。 论文是 NeurIPS 2025 / arXiv:2511.00977v2 的方法论文。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>NeurIPS · 2025</span>
    </div>
    <h1>NicheFlow</h1>
    <p>Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## NicheFlow 中文方法解读：让局部细胞微环境作为点云跨时间演化

### 1. 它改变了什么建模单位

时序空间转录组通常在不同发育阶段切取不同组织，测量是破坏性的，因此 $t_0$ 与 $t_1$ 没有同一个细胞可直接追踪。许多方法把每个细胞单独作为运输单位，只预测“这个细胞的后代可能在哪里”。NicheFlow 的核心改变是把一个中心细胞周围的局部邻域视为整体 microenvironment（niche），同时生成其中所有细胞的表达状态和空间坐标。

论文是 NeurIPS 2025 / arXiv:2511.00977v2 的方法论文。输入是多个有序 spatial slides，每个细胞具有空间坐标、表达/PCA 特征、时间点和可选 cell-type label。输出不是一条传统 pseudotime 曲线，而是条件生成：给定 $t_0$ 的一个或一组 source niches，模拟 $t_1$ 对应 niches 的点云，并可连续递推到后续时间。

这使模型能回答“某个局部组织结构下一阶段可能长成什么样”，包括细胞组成和形状；但生成轨迹仍是分布级预测，不是实验 lineage tracing。

### 2. 微环境怎样表示成点云

一个 slide 可写为带属性点集

$$
\mathcal P_s=\{(x_i^s,c_i^s)\}_{i=1}^{N_s},
$$

其中 $x_i^s$ 是细胞状态特征（实现中为标准化 PCA），$c_i^s\in\mathbb R^2$ 是空间坐标。以细胞 $i$ 为中心、半径 $r$ 内的邻居构成

$$
\mathcal M_i^s=\{(x_j^s,c_j^s):\lVert c_j^s-c_i^s\rVert\le r\}.
$$

因此一个 niche 是无序 point cloud，而非规则图像 patch。点云中的每个点同时带“是什么细胞状态”和“位于哪里”两部分属性。

当前源码 `nicheflow/preprocessing/h5ad_preprocessor.py` 对每个时间点计算 radius neighborhoods。为便于 batching，它取该 slide 最常见的邻居数 $N$，按距中心最近的 $N$ 个点截取；训练 collate 也能用 padding/mask 处理批内大小差异。坐标按时间点标准化，PCA 特征在全数据上标准化。

这里有重要边界：半径 $r$ 与固定点数决定“niche”的空间尺度。太小只看到单细胞局部噪声，太大则把不同组织区域混合。每时间点独立标准化坐标有助训练，却会去除绝对尺度变化，解释生长幅度时必须回到原始坐标。

### 3. 先用 OT 给 source 和 target niches 配对

不同 slides 没有一一对应。NicheFlow 先采样一批 $t_0$ niches 和一批 $t_1$ niches，再把每个点云池化为：平均表达/PCA 特征与空间 centroid 的拼接。对两个 pooled niches $a,b$，代价同时考虑状态与位置：

$$
d_\lambda(a,b)=
\lambda\lVert\bar x_a-\bar x_b\rVert^2+
(1-\lambda)\lVert\bar c_a-\bar c_b\rVert^2.
$$

然后求 optimal transport coupling 并按 coupling 重采样 source-target pairs。$\lambda$ 越大越依赖表达相似性，越小越依赖空间位置。论文 Fig. 3 的 spinal cord 与 neural crest 案例展示不同 $\lambda$ 下的映射概率。

当前 `nicheflow/datasets/microenv_dataset.py::_mini_batch_ot()` 先对 `cat([X, pos])` 做点维平均，再用 $\lambda$ 和 $1-\lambda$ 缩放对应维度，调用 `torchcfm.OTPlanSampler`。源码默认是 `method="exact"`；论文文字强调 entropic OT，但本地代码没有显式 $\epsilon$/Sinkhorn 参数。这一处应标为 **Not verified / implementation boundary**，不能仅因依赖库名称就声称当前运行完全等同论文公式。

OT 配对不是 ground truth ancestry。它只是用 pooled summary 建立训练监督；两个内部结构不同的 niches 可能拥有相同均值，批次和坐标标准化也会影响 coupling。论文的 OT-$\lambda$ ablation 正是在检查这一敏感性。

### 4. 从噪声到目标 niche 的 flow matching

#### 4.1 条件生成设置

给定 source niche $\mathcal M^0$ 和目标时间标签，模型从与目标同形状的 Gaussian noise $\mathcal M^z$ 出发。训练时取 $t\sim U(0,1)$，在噪声与真实 target $mathcal M^1$ 之间线性插值：

$$
\mathcal M^t=(1-t)\mathcal M^z+t\mathcal M^1.
$$

网络输入包括 source point cloud、当前 noisy target、source/target time one-hot 和连续 flow time $t$。它学习向量场或目标后验参数，使 ODE 从 $t=0$ 的噪声流到 $t=1$ 的 target distribution。

当前 `BaseFlow.loss()` 对 feature 和 position 各采独立 Gaussian noise，按上式插值，然后调用 point-cloud backbone。`BaseFlow.sample()` 从噪声出发，用 `torchdyn.NeuralODE` 数值积分；配置通常使用 Euler 和有限步数，所以生成质量也依赖 solver 与 `num_steps`。

#### 4.2 CFM、GVFM 与 GLVFM

论文比较三种目标：

- **CFM** 直接回归线性路径速度 $x_1-x_0$；
- **GVFM** 预测 Gaussian posterior mean，对 features 与 coordinates 都用平方误差；
- **GLVFM** 对表达/PCA features 使用 Gaussian/L2，对空间 coordinates 使用 Laplace/L1。

NicheFlow 的主结果偏向 GLVFM，因为空间点云中边界和组织结构可能更适合对 outlier 不那么敏感的 L1 coordinate loss。当前 `nicheflow/models/losses.py::GLVFMLoss` 直接实现

$$
\mathcal L=lambda_x\operatorname{MSE}(\hat x,x_1)
+\lambda_c\operatorname{MAE}(\hat c,c_1).
$$

对 VFM，网络预测终点/后验均值 $\mu_t^\theta$，再转成速度：

$$
u_t=\frac{\mu_t^\theta-z_t}{1-t}.
$$

当前 `VFM.get_vf()` 的分母加入 `EPS=10^{-8}` 防止 $t\to1$ 数值发散。这是合理实现细节，也意味着公式与浮点代码不是字面完全相同。

#### 4.3 为什么叫 variational

模型不要求在每个中间 $t$ 观察真实组织，而是学习一个以 source niche 为条件的 target posterior family。训练通过可采样的 conditional paths，把难求的边际 vector field 回归转成可计算目标。生成时对 ODE 积分得到 target samples。这里的“variational”是生成模型后验参数化，不是给每个细胞估计传统 variational latent variable 的同义词。

### 5. Microenvironment Transformer 如何保留点云结构

单点 MLP 看不到邻域内部协调。NicheFlow 使用 encoder-decoder Transformer：

1. encoder 对 source niche 的点做 self-attention，编码局部组成；
2. decoder 对 noisy target 做 self-attention；
3. decoder 通过 cross-attention 读取 source encoder；
4. target time label 和 sinusoidal flow-time embedding 注入 decoder；
5. 最后分别预测 feature 与 coordinate 输出。

点云没有固有顺序，attention 与 mask 使模型能处理点排列和批内可变大小。当前 `PointCloudFlow._backbone_forward()` 将 source/target features、positions、time one-hot、$t$ 和 masks 传入 `PointCloudTransformer`。encoder 的 flow-time 输入被置零，时间主要作用于 target decoder，符合论文架构描述。

但 permutation handling 不自动保证旋转、平移或尺度不变；坐标预处理和训练数据分布仍决定这些性质。

### 6. 训练采样为何还要 K-means regions

若在整个 slide 均匀抽中心，巨大或高密区域会主导 mini-batch。代码先把每个时间点划成 $K$ 个 K-means spatial regions，再从各 region 采 niches。默认配置中 $K=64$，先采 256 个 microenvironments，再经 OT 重采 64 对。这使 batches 覆盖更多组织区域。

论文报告的 batch size、$K$ 与仓库默认并非全部一致；例如 doc/code 核对显示论文写 16 instances，而当前 base config 的 train batch size 是 2。配置漂移必须在复现时记录，不能只运行默认 YAML 后声称复现表格。

### 7. 如何评估生成的 tissue niche

论文同时评估空间和语义：

- **PSD (Point-to-Shape Distance)**：每个预测点到真实 target cloud 最近点的距离；检查生成点是否落在真实组织附近。
- **SPD (Shape-to-Point Distance)**：每个真实点到所有预测点的最近距离；检查真实组织是否被覆盖。
- **1NN-F1**：先用独立 classifier 从生成 PCA features 预测 cell type，再按空间最近真实细胞比较类别。
- 还报告位置/feature 回归、GW/FGW 和 Wasserstein 等附加指标。

当前 `tasks/flow_matching.py` 的 PSD/SPD 用 `torch.cdist` 返回普通 Euclidean distance 并取 mean/max，而论文公式写 squared distance。这会改变尺度，甚至可能改变对极端误差的敏感性，是明确的 **DIFF**，不是小数点格式问题。

另外，classifier 质量直接影响 1NN-F1；高 F1 表示生成 feature 能被分类并与附近真实类别一致，不等同于基因级表达完全准确。

### 8. 如何读主要图

- **Fig. 1**：蓝色 source niche 条件化绿色 noisy target，模型把噪声流向粉色 target niche；OT 决定训练配对。图示的是概率生成过程，不是单个细胞被实际观察到移动。
- **Fig. 2**：在 mouse embryo E9.5→E10.5→E11.5 上比较 SPFlow 与 NicheFlow 的 CFM/GVFM/GLVFM。单点模型生成模糊云，而 point-cloud 模型更能保持胚胎轮廓与 cell-type organization。
- **Fig. 3**：针对 spinal cord 和 neural crest source region，画出生成样本在 target slide 的 density 与 descendant cell-type proportions，并与 moscot 对照。
- **Fig. 4–5（Appendix）**：多步 neural crest 与 liver mapping。每一步生成结果作为下一步 source，误差会累积；中间不使用 ground truth source。
- **Fig. 6–9**：axolotl brain 的整体形状、hemisphere split、cavity 和 dorsal pallium composition，检验跨较长发育阶段的结构生成。

本次直接查看了 overview、Fig. 2 和 Fig. 3 的本地图像，并核对 `paper.md` 的全部图注与附录说明。图中更接近 target 的轮廓是定性支持，仍需结合 PSD/SPD、1NN-F1 和多次随机采样。

### 9. 生物学轨迹该如何解释

NicheFlow 对一个 source region 多次采样，形成“它在下一 slide 可能出现在哪里、组成什么 cell types”的概率分布。论文用 spinal cord、head neural crest、liver 和 axolotl brain 展示这一点。

它不能区分以下两种情况：同一 lineage 的细胞实际迁移到目标区域，或不同细胞群在目标区域形成相似 niche。OT pairing 与生成网络主要由表达/坐标统计监督，没有 lineage barcode。所谓 fate probability 应理解为模型条件分布下的 target association，而非单细胞实验命运概率。

连续多步 propagation 尤其要谨慎：模型在每步都接收自己生成的点云，分布偏差会累积。长期形态正确是有价值的测试，但不能消除 exposure bias。

### 10. 论文与源码的对应和缺口

本地源码与论文放在同一工作区，但 `nicheflow/` 不是独立 Git clone，没有 `.repo_commit` 或可验证的 upstream commit。PaperCode 根仓库 commit 不是 NicheFlow 版本号。因此这里的 provenance 是“local source snapshot, commit Not found”。

可直接确认的实现主链包括：

- `preprocessing/h5ad_preprocessor.py`：坐标/PCA 标准化、radius niches、评估中心网格；
- `datasets/microenv_dataset.py`：K-region 采样、pooled OT pairing 与 timepoint pairs；
- `models/flows.py`：noise interpolation、CFM/VFM target、ODE generation；
- `models/losses.py`：CFM/GVFM/GLVFM feature-position losses；
- `models/backbones/pc_transformer.py`：source encoder、target decoder 与 cross-attention；
- `tasks/flow_matching.py`：训练、PSD/SPD、classifier/1NN metrics；
- `configs/`：数据、模型、solver、batch 与 ablation 参数。

关键缺口：

- 论文的 entropic OT / $\epsilon$ 在当前代码中未显式验证，默认 sampler 是 exact；
- moscot/LUNA comparison scripts、KDE mapping likelihood、GW/FGW 和 Wasserstein metric 计算不在本地 package 主路径中；
- 三个预处理数据 `.pkl`、训练 checkpoints 和论文完整运行产物未包含；
- MBA 0.2 subsampling 等可能在导出数据前完成，源码中 Not found；
- PSD/SPD 的平方距离定义与当前代码普通距离不一致。

这些缺口不表示核心模型不存在，但限制“从仓库一键重现全部表图”的声称。

### 11. 一个最小数值直觉

设 source/target pooled niches 的 feature 均值差为 2，coordinate centroid 差为 1。若忽略平方向量维度并取 $\lambda=0.8$，配对代价约为

$$
0.8\times 2^2+0.2\times1^2=3.4.
$$

取 $\lambda=0.2$ 则为

$$
0.2\times2^2+0.8\times1^2=1.6.
$$

因此 $\lambda$ 不只是“微调参数”：它会改变哪些 niches 被视为对应，进而改变网络看到的监督 pairs。空间与表达尺度必须先标准化，否则某一项会仅因数值范围大而支配 OT。

### 12. 复现检查单

可靠复现至少要固定：数据版本与 cell-type labels、PCA 和坐标标准化、radius/每 slide 点数、$K$ regions、采样数、OT method/$\lambda$/正则、point-cloud Transformer 尺寸、CFM/GVFM/GLVFM、feature/position loss weights、ODE solver/steps、seed、classifier checkpoint，以及 PSD/SPD 的平方与否。

还应对不同 $r$、$K$、$\lambda$ 和随机 seeds 做敏感性分析；报告多步 rollout 误差；用独立 anatomical annotations 或 lineage data 验证 mapping。只看生成组织外形相似并不足以证明微环境命运正确。

### 13. 本工作区证据范围

- 论文：37 页 arXiv:2511.00977v2 / NeurIPS 2025 PDF。
- Markdown：`paper source/.../Sakalyan et al. - 2025 - ... NicheFlow.md`，包含正文、理论、算法和附录。
- 图像：主 overview 与 PDF 提取图像；已直接检查 overview、Fig. 2、Fig. 3。
- 代码：工作区本地 Python snapshot；upstream repo URL/commit MISSING / Not found。
- 未复现：训练、三个大数据集、checkpoints、全部 baselines 与所有论文表图。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## NicheFlow: Modeling Microenvironment Trajectories on Spatial Transcriptomics

### Paper Information
- **Title**: Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow
- **Authors**: Kristiyan Sakalyan*, Alessandro Palma*, Filippo Guerranti*, Fabian J. Theis, Stephan Günnemann
- **Venue**: NeurIPS 2025 (Neural Information Processing Systems)
- **Links**: [OpenReview](https://openreview.net/forum?id=5ofJyjgrth) | [Project Page](https://www.cs.cit.tum.de/daml/nicheflow/)
- **Paper markdown source**: `paper source/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow.md`

---

### Motivation & Novelty

#### Biological Problem
Understanding the evolution of cellular microenvironments in spatiotemporal data is essential for deciphering tissue development and disease progression. While spatial transcriptomics (ST) provides single-cell resolution mapping of gene expression while preserving spatial context, it only captures **static snapshots** of inherently dynamic biological systems.

> "How can we model the spatiotemporal evolution of cellular microenvironments preserving both local neighborhood relationships and cellular state transitions?" (Paper, Page 2)
> Reference: Paper Sec. 1 (Introduction), `paper source/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow.md`

#### Limitations of Existing Methods
Current computational methods fall short in modeling the evolution of tissue organization at the microenvironment level:

1. **Cell-centric approaches**: Velocity-based models (scVelo, SIRV) and optimal transport methods (moscot, DeST-OT) infer trajectories by modeling single-cell dynamics, fundamentally missing the **coordinated evolution of structured niches** within tissues.

2. **Scalability issues**: Exact OT methods do not scale well to large tissue sections and cannot generalize beyond the training data.

3. **Lack of generative capability**: Discrete OT approaches learn transition matrices but cannot generate new point clouds representing microenvironments.

#### Key Innovation
NicheFlow introduces a **microenvironment-centered trajectory inference paradigm** that shifts from modeling individual cells to modeling niches as point clouds:

1. **Microenvironment-centered trajectory inference**: Represents local cell neighborhoods as point clouds, enabling simultaneous prediction of spatial coordinates and gene expression profiles while preserving local tissue context.

2. **Mixed-Factorized Variational Flow Matching (VFM)**: A novel factorized VFM approach using different distributional families for different data modalities:
   - **Laplace distribution** for spatial coordinates (L1 loss - precise spatial modeling)
   - **Gaussian distribution** for gene expression features (MSE loss)

3. **Spatially-aware OT sampling**: Uses optimal transport over pooled microenvironment representations weighted by parameter $\lambda$ for scalable training.

---

### Method Overview

#### Core Technical Contributions

##### Microenvironment Representation
Local cell neighborhoods are defined as fixed-radius point clouds:
$$\mathcal{M}_i^s = \left\{ (\mathbf{c}_j^s, \mathbf{x}_j^s) \mid \|\mathbf{c}_j^s - \mathbf{c}_i^s\| \le r \right\}$$

Where:
- $\mathbf{c}_i^s \in \mathbb{R}^2$: 2D spatial coordinates
- $\mathbf{x}_i^s \in \mathbb{R}^D$: Gene expression profile (typically 50 PCA components)

Implementation note (code): microenvironments are precomputed by thresholding pairwise distances (`torch.cdist(coords, coords) < radius`) and then truncating to the most frequent neighbor count per timepoint for batching.
Code refs: `nicheflow/preprocessing/h5ad_preprocessor.py::H5ADPreprocessor._compute_radius_graphs`, `nicheflow/utils/preprocessing.py::chunked_cdist_sum_argsort`

##### Spatially-aware OT Sampling (Eq. 12)
Pooled representations balance spatial vs. transcriptomic similarity:
$$\bar{\mathbf{m}}_{i}^{s} = \left[ \frac{1 - \lambda}{|\mathcal{M}_{i}^{s}|} \sum_{(\mathbf{c}_{j}^{s}, \mathbf{x}_{j}^{s}) \in \mathcal{M}_{i}^{s}} \mathbf{c}_{j}^{s} \ \Bigg\| \ \frac{\lambda}{|\mathcal{M}_{i}^{s}|} \sum_{(\mathbf{c}_{j}^{s}, \mathbf{x}_{j}^{s}) \in \mathcal{M}_{i}^{s}} \mathbf{x}_{j}^{s} \right]$$

Where $\lambda \in [0, 1]$:
- Higher $\lambda$: Prioritizes gene expression similarity (for cell fate tracking)
- Lower $\lambda$: Prioritizes spatial proximity (for fixed structure evolution)

References:
- Paper Sec. 4.2 Eq. (12), `paper source/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow.md`
- Code: `nicheflow/datasets/microenv_dataset.py::MicroEnvDatasetBase._mini_batch_ot`, config `configs/data/nicheflow_base.yaml::datamodule.ot_lambda`

##### NicheFlow Loss Function - GLVFM (Eq. 14/38)
$$\mathcal{L}_{\text{NicheFlow}}(\theta) = \mathbb{E}_{t, (\mathcal{M}^0, \mathcal{M}^1) \sim \pi_{\epsilon, \lambda}^*} \left[ \sum_{(\mathbf{c}_1, \mathbf{x}_1) \in \mathcal{M}^1} \left( \|\mathbf{c}_1 - \bar{\mathbf{f}}_t^{\theta}\|_1 + \frac{1}{2} \|\mathbf{x}_1 - \bar{\mathbf{r}}_t^{\theta}\|_2^2 \right) \right]$$

The loss consists of:
- **L1 loss** on spatial coordinates (from Laplace posterior)
- **MSE loss** on gene expression features (from Gaussian posterior)

References:
- Paper Sec. 4.3 Eq. (14) / App. E.3 Eq. (38), `paper source/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow.md`
- Code: `nicheflow/models/losses.py::GLVFMLoss.forward` (note: code includes additional weighting terms `lambda_features/lambda_pos`)

##### VFM Velocity Field (Eq. 18)
$$u_t(\mathbf{x}) = \frac{\mu_t^{\theta}(\mathbf{x}) - \mathbf{x}}{1-t}$$
Code ref: `nicheflow/models/flows.py::VFM.get_vf` (uses $1-t+\texttt{EPS}$ with `nicheflow/models/flows.py::EPS`)

#### Architecture: Microenvironment Transformer
- **Encoder-decoder structure**: Processes source microenvironment via encoder, predicts posterior mean from noisy target via decoder
- **Cross-attention conditioning**: Decoder attends to encoded source points
- **Input embeddings**: Separate embeddings for features, coordinates, and sinusoidal time encoding
- **Key design**: Encoder receives **zero time embedding** (source is time-independent)
- Parameters (paper): 2 encoder layers, 2 decoder layers, 4 attention heads, 128 embedding dim (Paper Sec. F.7, `paper source/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow.md`)
- Parameters (code): `PointCloudTransformer(embed_dim=128, num_heads=4, ...)` but embed dim is rounded down to be divisible by $3\cdot\text{num\_heads}$ (128 -> 120 for 4 heads). Code ref: `nicheflow/models/backbones/pc_transformer.py::PointCloudTransformer.__init__`

---

### Evaluation

#### Datasets

| Dataset | Organism | Tissue | Timepoints | Cell Types | Cells | Technology |
|---------|----------|--------|------------|------------|-------|------------|
| MED | Mouse | Whole embryo | 3 | 24 | 54k | Stereo-seq |
| ABD | Axolotl | Brain | 6 | 33 | 36k | Stereo-seq |
| MBA | Mouse | Brain | 20 | 18 | 1.5M | MERFISH |

Reference: Paper Table 9, `paper source/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow.md`

#### Metrics

1. **1NN-F1**: Nearest-neighbor cell-type classification F1 score
2. **PSD (Point-to-Shape Distance)** (Eq. 39): Generated points → ground truth structure
$$\text{PSD} = \frac{1}{|\mathcal{G}|} \sum_{\mathcal{G}^t \in \mathcal{G}} \sum_{\mathbf{c}_i \in \mathcal{G}^t} \|\mathbf{c}_i - \text{NN}_{\text{ref}}^t(\mathbf{c}_i)\|_2^2$$
3. **SPD (Shape-to-Point Distance)** (Eq. 40): Ground truth → generated points coverage
$$\text{SPD} = \frac{1}{|\mathcal{R}|} \sum_{\mathcal{R}^t \in \mathcal{R}} \sum_{\mathbf{c}_j \in \mathcal{R}^t} \|\mathbf{c}_j - \text{NN}_{\text{gen}}^t(\mathbf{c}_j)\|_2^2$$

Paper reference: Sec. F.3 Eq. (39-40), `paper source/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow.md`

Code mismatch: this repo computes PSD/SPD using unsquared Euclidean distances from `torch.cdist` and logs mean/max (not squared). Code refs: `nicheflow/tasks/flow_matching.py::nn_of_x_in_y`, `nicheflow/tasks/flow_matching.py::ShapeToPointDistance.compute`

#### Key Results (Table 1)

| Model | Objective | MED 1NN-F1 | MED PSD | ABD 1NN-F1 | MBA 1NN-F1 |
|-------|-----------|------------|---------|------------|------------|
| LUNA | - | 0.540 | - | 0.331 | 0.222 |
| SPFlow | GLVFM | 0.251 | 2.249 | 0.173 | 0.195 |
| RPCFlow | GLVFM | 0.586 | 0.979 | 0.554 | 0.265 |
| **NicheFlow** | **GLVFM** | **0.664** | **0.883** | **0.628** | **0.285** |

NicheFlow with GLVFM consistently achieves the best performance across datasets.
Reference: Paper Table 1 (GLVFM rows), `paper source/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow/Sakalyan et al. - 2025 - Modeling Microenvironment Trajectories on Spatial Transcriptomics with NicheFlow.md`

#### Biological Validation

Comparison with moscot on mouse embryo development:
- **Spinal cord trajectory** (E10.5→E11.5): NicheFlow correctly maps to maturing spinal cord; moscot leaks to unrelated regions (urogenital ridge, branchial arches)
- **Neural crest differentiation**: NicheFlow captures differentiation into mesenchymal and cranial tissues; moscot shows off-target leakage
- **Liver evolution** (E10.5→E11.5): NicheFlow accurately retrieves liver structure; moscot shows density leakage to GI tract

#### Why GLVFM Works Better
- Laplace distribution has **heavier tails and sharper peak** than Gaussian
- Better models the **precise localization** required for spatial coordinates
- Gene expression is naturally noisy → Gaussian appropriate

---

### Reproducibility Assessment

#### Status: PARTIAL (code present; data/ckpts external; several code-paper deltas)

#### Strengths
- **Complete code implementation** with clear, modular structure
- **Preprocessed datasets** available on FigShare
- **Detailed hyperparameters** documented in Hydra configs
- **Configuration files** for all experiments
- **Ablation eval scripts** for paper tables: `nicheflow/eval_state_dict_ckpts.py::main`, `nicheflow/eval_state_dict_ckpts_kregion_ablations.py::main`, `nicheflow/eval_state_dict_ckpts_ot_ablations.py::main`

#### Code-Paper Fidelity
Key checks (with caveats):
- Losses (CFM/GVFM/GLVFM): implemented; `nicheflow/models/losses.py::CFMLoss`, `nicheflow/models/losses.py::GVFMLoss`, `nicheflow/models/losses.py::GLVFMLoss.forward`
- VFM velocity field: implemented with stabilizer `EPS`; `nicheflow/models/flows.py::VFM.get_vf`, `nicheflow/models/flows.py::EPS`
- OT pooling with $\lambda$: implemented; `nicheflow/datasets/microenv_dataset.py::MicroEnvDatasetBase._mini_batch_ot`
- PSD/SPD: **DIFF** vs paper squared-distance definition; `nicheflow/tasks/flow_matching.py::nn_of_x_in_y`
- OT entropic regularization $\epsilon$: **NOT VERIFIED** in this repo (delegated to `torchcfm.OTPlanSampler`)
- Transformer embed dim: paper reports 128; code rounds down for divisibility; `nicheflow/models/backbones/pc_transformer.py::PointCloudTransformer.__init__`

#### Potential Blockers
1. **Data download**: Requires FigShare access for preprocessed data
2. **Classifier checkpoints**: Required for evaluation, also on FigShare
3. **Path configuration**: May need adjustment in `configs/paths/default.yaml`

#### Computational Requirements
- Single NVIDIA GTX 1080 Ti (11GB)
- Training time: 12-16 hours per model
- Dependencies: `pyproject.toml` includes `lightning`, `torch-geometric`, `torchdyn`, `torchcfm` (and `moscot` via git; requires network access to install)

---

### Key Takeaways

1. **Paradigm shift**: From single-cell to microenvironment-level trajectory inference
2. **Distribution-aware modeling**: Using appropriate distributions (Laplace for coordinates, Gaussian for features) improves spatial precision
3. **OT-based pairing**: Spatially-aware sampling with tunable $\lambda$ enables flexible trajectory modeling for different biological scenarios
4. **Scalable design**: Mini-batch OT and point cloud representation enable application to large tissue sections
5. **Exemplary reproducibility**: Code faithfully implements all paper equations with thorough documentation

---

### Limitations (from paper)

1. Fixed $\lambda$ during training limits inference flexibility
2. Radius-based niche definitions may be suboptimal for irregular microenvironments
3. Requires pre-aligned spatial slides
4. Does not explicitly model cell division or death events
5. Focused on in-distribution testing; generalization to unseen slides not evaluated
6. Cannot extrapolate spatial arrangements without prior exposure to associated regions

---

### References to Paper

Key equations referenced:
- **Eq. 12**: Pooled microenvironment representation with $\lambda$ weighting
- **Eq. 13**: Factorized posterior distribution
- **Eq. 14/38**: NicheFlow GLVFM loss function
- **Eq. 18**: VFM velocity field formula
- **Eq. 39-40**: PSD and SPD metrics
- **Section F.6**: Microenvironment Transformer architecture details
- **Section F.7**: Hyperparameters and computational costs

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
