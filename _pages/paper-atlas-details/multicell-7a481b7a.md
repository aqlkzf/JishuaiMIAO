---
layout: default
permalink: /paper-atlas/multicell-7a481b7a/
title: "MultiCell"
nav: false
description: "MultiCell 把发育中的果蝇胚胎表面表示成图：细胞是节点、相邻细胞是边，细胞形状放在节点特征中，连接处的几何放在边特征中。Graph Transformer 通过多层邻域信息聚合，为每个细胞生成隐藏表示；随后按任务把隐藏表示汇总到整个胚胎、单个细胞或一对相邻细胞，分别预测发育时间、距未来事件的时间或细胞连接是否会消失。 它预测的是基于当前及前一帧几何的统计结果，并不是从力学方程模拟胚胎，也没有直接输入基因表达或细胞命运标签。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>MultiCell</h1>
    <p>MultiCell: geometric learning in multicellular development</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02983-x" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MultiCell：如何用组织几何预测单细胞未来行为

### 一句话理解

MultiCell 把发育中的果蝇胚胎表面表示成图：细胞是节点、相邻细胞是边，细胞形状放在节点特征中，连接处的几何放在边特征中。Graph Transformer 通过多层邻域信息聚合，为每个细胞生成隐藏表示；随后按任务把隐藏表示汇总到整个胚胎、单个细胞或一对相邻细胞，分别预测发育时间、距未来事件的时间或细胞连接是否会消失。

它预测的是基于当前及前一帧几何的统计结果，并不是从力学方程模拟胚胎，也没有直接输入基因表达或细胞命运标签。

### 1. 为什么叫 dual graph

论文用两种互补的物理视角描述上皮组织：

- granular view：每个细胞是一个粒子，细胞为节点 $\mathcal C$，相邻关系为边 $\mathcal E_{c-c}$；
- foam view：三个细胞相交处的顶点为节点 $\mathcal V$，细胞连接为边 $\mathcal E_{v-v}$。

完整概念表示还包括把细胞连到其边界顶点的 $\mathcal E_{c-v}$。这套表示的意义是：未来行为既可能由整个细胞的形状决定，也可能由局部连接是否短、两端三角结构是否畸变决定。

实际 Python 模型采用论文 Eq. 3 的高效表示，而不是直接运行一个包含两类节点的异构图网络。它保留细胞节点和 cell–cell adjacency，把与该连接对应的顶点/连接几何折叠为 edge attributes。因而“dual”指信息来源仍覆盖两张互为对偶的图，不代表代码中同时存在两个 Graph Transformer。

### 2. 输入特征从哪里来

每个细胞节点主要包含：

- 面积 $a$；
- 周长 $p$；
- $K_1=\sqrt{k_1k_2}$，即论文所称 Gaussian curvature 的平方根；
- $K_2=(k_1+k_2)/2$，即 mean curvature。

每条相邻细胞边包含连接长度 $l_{v-v}$，以及连接两端 Delaunay 三角形的面积、shear 和 opening-angle 特征的平均/差值。论文用 $\theta$ 记 opening angle；当前 MATLAB 预处理在 `MC_Drosophila_preprocess_main.m:648-725` 实际计算并保存 $\cos\theta$，且差值取绝对值。因此代码特征与论文符号不是数值相同的量。

特征先用 $l_0=10\,\mu\mathrm m$ 无量纲化。短连接更容易丢失，所以连接长度再变换为

$$
\tilde l \mapsto \exp(-\gamma\tilde l),
$$

论文与 demo 使用 $\gamma=10$，而命令行默认值是 1。shear 特征取对数。程序还把前一帧与当前帧之差拼接进输入，提供几何变化率；所以它不只是静态形状分类器。

### 3. Graph Transformer 在做什么

`MC_model.py:76-123` 的 `GT` 使用 PyTorch Geometric `TransformerConv`。对一个细胞而言，每层都会从相邻细胞接收信息，注意力权重同时受 edge attributes 影响。多层堆叠后，一个细胞的隐藏状态包含更远邻域的几何环境。

代码默认主干为 6 层、每头 24 channels、4 heads（`MC_main.py:31-34`）；每层后使用 LayerNorm 和 ReLU。节点与边原始特征先各自通过带残差的 MLP 投影到相同特征维度。时间若以 `concat` 模式输入，会作为一个额外节点特征拼入；三个 demo 都明确指定了各任务参数，不能只依赖 argparse 默认值来复现实验。

### 4. 三种读出层对应三种空间尺度

#### 胚胎级：视频时间对齐

对每一帧，把全部细胞隐藏状态做 `global_mean_pool`，再经线性层预测一个标量时间（`MC_model.py:287-292`）。训练时选择一个胚胎作为有时间标签的参考，另一个胚胎的每帧输入同一模型，从而得到相对于参考胚胎的发育时间。所谓“unsupervised alignment”是指没有人工标注形态事件作为对齐锚点；模型训练本身仍使用参考视频的时间做回归监督。

#### 边级：未来 junction loss

对一对相邻细胞，代码先逐元素相乘两个隐藏向量，再通过 MLP 和 sigmoid 得到连接丢失概率（`MC_model.py:274-298`）。补充材料称其为 inner-product decoder，但默认 `agg_type="mlp"` 并不是纯内积；只有 `agg_type="sum"` 才对乘积求和。训练对正、负边分别计算对数损失后相加。

#### 节点/边多任务：距未来事件还有多久

`MC2` 共享一个编码器，然后使用三个独立 Graph Transformer head（`MC_model.py:131-224`）：

- `y1`：相邻边距 rearrangement 的时间；
- `y2`：细胞距 invagination 的时间；
- `y3`：细胞距 division 的时间。

三者经 sigmoid 输出 $[0,1]$。预处理将分钟数按 30 分钟截断并归一化；没有在窗口内发生的事件也映射到 1。因此输出不是直接的分钟数，评估或可视化时需要恢复尺度。

### 5. 多任务损失如何强调近期事件

补充材料的目标可概括为每个任务的加权绝对误差加相关性惩罚：

$$
L_j=\frac{1}{N_j}\sum_i \alpha_i^{(j)}|y_i^{(j)}-\hat y_i^{(j)}|
+\epsilon(1-\rho^{(j)}).
$$

近期事件权重大，窗口外样本权重为 0.05。当前 demo 传入 `weighted_loss_factor=20`，`MC_loss.py:89-92` 因而对归一化标签等于 1 的样本赋权 $1/20=0.05$；`corr_loss_factor=0.1` 对应相关性项。代码计算相关性时先过滤标签等于 1 的窗口外样本（`MC_loss.py:67-70,122-139`）。

### 6. 从原始视频到预测的完整数据流

1. MATLAB 从分割、追踪后的 3D 胚胎网格计算细胞、连接和顶点几何，并根据未来帧生成 junction loss、invagination、division、rearrangement 标签。
2. `preprocess/MC_preprocessing.py` 把 `.mat` 结构转换为 PyTorch Geometric `Data`，最终训练入口固定读取 `MultiCell.pkl`。
3. `MC_dataprep.py` 划分独立胚胎的训练/测试集，替换 NaN、转为无向边、标准化特征、做长度/shear/变化率和标签变换。
4. `MC_utils.get_model()` 根据任务构造 `MC_binary` 或 `MC2`。
5. `MC_train.py` 用 AdamW、mixed precision、gradient clipping 和可选 cosine scheduler 训练。
6. `MC_test.py` 在整个测试集上计算 AUC 或 Pearson correlation；论文数值来自跨独立胚胎验证，不是本工作区重新运行得到的结果。

### 7. 主图应如何阅读

Figure 1 展示的是表示与读出层：同一图编码器输出既可以由 graph decoder 做边预测，也可以 pooling 后做组织级预测。Figure 2 的时间对齐与 activation map 表明模型学到的几何信号与 ventral furrow、cephalic furrow、posterior midgut 等形态事件相对应，但 activation 只是模型贡献图，不等同于因果力学场。

Figure 3 检验未来 junction loss。论文报告完整模型 AUC 为 $0.950\pm0.021$；只用连接长度的 MLP 为 $0.821\pm0.018$，加入长度变化率为 $0.869\pm0.025$。消融支持“细胞几何与连接几何共同提供预测信息”，但不能单凭预测性能断言某个特征是事件的生物学原因。

Figure 4 的三项 30 分钟预测相关系数按图中顺序是 invagination 0.79、division 0.87、rearrangement 0.78。UMAP 中组织域分离说明共享编码器的表示包含域相关信息；域标签未用于该基础训练，但这仍是表示关联，不是证明模型恢复了真实分子身份。

### 8. 论文与当前代码的关键边界

- 完整 dual graph 是论文的统一表述；主要 Drosophila Python 管线使用折叠后的单一 cell graph。
- 论文称 inner-product decoder；默认代码是 elementwise product 后接 MLP。
- 补充材料称通用 MLP 有 32 channels；代码把 `hidden_channels=24` 传给输入/输出 MLP，形成如 24→12→1 的输出头。
- 论文/实验使用 $\gamma=10$；CLI 默认 `edge_attr_gamma=1.0`，demo 才覆盖为 10。
- 论文写 opening angle；MATLAB 保存的是 cosine。
- `requirements.txt` 缺少 `transformers`，但 `MC_main.py:5` 无条件从中导入 scheduler。
- 当前代码快照没有 `MultiCell.pkl`，所以无法仅凭仓库完成训练或复现论文指标；需要作者处理后的数据或先运行 MATLAB 预处理。

### 9. 一个小例子

假设一条细胞连接正在缩短。只看长度，模型可能认为它即将消失；但若两侧细胞整体形状和更远邻域不支持重排，Graph Transformer 可以通过消息传递降低该概率。相反，两条长度相同的连接处于不同组织域和不同邻域应力几何时，模型可以给出不同预测。这正是 MultiCell 相比“短边阈值”基线多出的信息来源。

### 证据入口

- 主论文：`paper source/paper/vlm/paper.md`。
- 补充方法：`output_paper_supp_md/paper_supp1/vlm/paper_supp1.md`。
- 主图：`paper source/paper/vlm/images/`。
- 图模型与任务头：`MultiCell/run/scripts/MC_model.py`。
- 训练与损失：`MultiCell/run/scripts/MC_train.py`、`MC_loss.py`、`MC_main.py`。
- Python 数据准备：`MultiCell/run/scripts/MC_dataprep.py`、`MC_utils.py`。
- MATLAB 几何与标签预处理：`MultiCell/preprocess/MC_Drosophila_preprocess_main.m`。
- 代码来源记录：`MultiCell/.repo_source`，提交 `9d02e218341e555df7c5b49956f17980d0231117`。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## MultiCell — Paper Summary

> **MultiCell: geometric learning in multicellular development**
> Yang, H., Roy, G., Nguyen, A.Q., Bi, D., Stern, T., Buehler, M.J. & Guo, M.
> *Nature Methods* (2025). DOI: [10.1038/s41592-025-02983-x](https://doi.org/10.1038/s41592-025-02983-x)

---

### Motivation & Novelty

#### Biological Problem

During embryogenesis, multicellular organisms self-organize from populations of cells into specific three-dimensional structures through coordinated single-cell behaviors — junction remodeling, cell shape changes, cell division, and cell invagination. In *Drosophila* gastrulation, these processes occur across thousands of cells within ~1 hour. Despite advances in cell tracking and segmentation, predicting the behavior of every cell in a developing tissue at single-cell resolution has remained out of reach.

#### Limitations of Existing Approaches

Prior computational approaches to multicellular dynamics fall into several categories, each with limitations:

- **Continuum-field descriptions** (Supekar et al., *PNAS*, 2023; Lefebvre et al., *bioRxiv*, 2023): Coarse-grain away single-cell resolution, cannot make cell-level predictions.
- **Individual trajectory inference** (LaChance et al., *PLoS Comput. Biol.*, 2022; Brückner et al., *Phys. Rev. Lett.*, 2020): Focus on single-cell trajectories without capturing multicellular geometry.
- **Task-specific predictions**: Mitotic timing (Di Talia & Wieschaus, *Dev. Cell*, 2012), T1 transitions (Brauns et al., *eLife*, 2024; Claussen et al., *PNAS*, 2024), cell fate (Yamamoto et al., *PLoS Comput. Biol.*, 2022), glassy dynamics (Yang et al., *PRX Life*, 2024). These address individual behaviors but lack a unified framework for multiple modalities simultaneously.
- **Mechanistic models**: Vertex models (Bi et al., *Nat. Phys.*, 2015; Kim et al., *Nat. Phys.*, 2021) provide physical understanding but cannot generate whole-embryo predictions.

No prior method can predict multiple types of cell behavior (junction loss, invagination, division, rearrangement) simultaneously at single-cell resolution across whole embryos.

#### Unique Contributions

1. **Dual-graph representation**: A unified data structure that combines the granular (cells as particles) and foam-like (cells as polygons with junctions) physical pictures of multicellular systems, enabling both cell-level and junction-level predictions.
2. **Geometric deep learning for morphogenesis**: The first application, to the authors' knowledge, of graph neural networks for predicting multiple types of cell behavior at single-cell precision during embryogenesis.
3. **Interpretable predictions**: Neural activation maps and ablation studies reveal which geometric features drive predictions, identifying cell and junction geometry as essential features for predicting junction remodeling.
4. **Unsupervised temporal alignment**: The model achieves robust video sequence alignment using only geometric features, identifying developmental landmarks without explicit landmark annotation.

---

### Method Overview

MultiCell represents 4D embryo data as dual graphs — cells and their adjacencies form the primary graph; cell junction vertices and their connections form the auxiliary graph. For efficiency, vertex features are folded into edge attributes of the cell graph.

Input features include invariant geometric quantities: cell area, perimeter, curvatures (from quadratic surface fitting), junction length, Delaunay triangle area/shear, and opening angles. Features are non-dimensionalized, transformed (exponential for edge length, logarithmic for shear), and augmented with temporal derivatives.

A Graph Transformer encoder (6 layers, 24 channels, 4 attention heads) processes the graph via multi-head attention message passing. Task-specific output heads make predictions:
- **Tissue-level**: Global mean pooling for developmental time alignment
- **Edge-level**: Pairwise decoder for junction loss prediction
- **Node-level**: Separate heads for time-until-invagination, division, and rearrangement

See doc_method.md for full mathematical details and doc_code.md for implementation mapping.

---

### Evaluation

#### Datasets

- **Drosophila whole embryos**: 4 time-lapse 3D videos of gastrulating embryos (2 from Stern et al., *Curr. Biol.*, 2022; 2 newly collected). Frame rates: 15s, 60s, 40s.
- **Regional tissue**: 4 germband extension movies from Cupo et al. (*PRX Life*, 2024), used for fine-tuning validation.
- **Synthetic**: Self-Propelled Voronoi (SPV) model simulations under shear (Huang et al., *Phys. Rev. Lett.*, 2022), 50 seeds × 3000 frames.

#### Metrics and Results

| Task | Metric | Performance |
|---|---|---|
| Video alignment | MSE of aligned time vs. morphological events | Good correspondence with VFF, CF, PMI landmarks |
| Junction loss | AUC-ROC | 0.950 ± 0.021 (full model) |
| Junction loss | Accuracy | 90% (loss) / 84% (no loss) |
| Time until invagination | Pearson ρ (30 min) | 0.87 |
| Time until division | Pearson ρ (30 min) | 0.79 |
| Time until rearrangement | Pearson ρ (30 min) | 0.78 |
| Synthetic rearrangement | AUC-ROC | Good (solid and fluid-like tissues) |
| Synthetic stress | Pearson ρ | 0.98 (solid) / 0.99 (fluid) |

#### Ablation Study (Junction Loss)

| Model | AUC |
|---|---|
| Full model (all features) | 0.950 ± 0.021 |
| MLP + edge length only | 0.821 ± 0.018 |
| MLP + edge length + rate | 0.869 ± 0.025 |
| Junction geometry only | 0.916 ± 0.028 |
| Cell geometry only | 0.861 ± 0.027 |
| Without vertex geometry | 0.949 ± 0.020 |
| Without rate of change | 0.947 ± 0.020 |

Key finding: both junction and cell geometry are essential; vertex geometry and rate of change contribute marginally.

#### Biological Validation

- Activation maps spontaneously identify ventral furrow, cephalic furrow, and posterior midgut regions before visible morphological events
- UMAP embeddings of encoder outputs show tissue domain segregation without domain label supervision
- Adding domain labels during training produces only minor performance improvement (Fig. 4n), confirming the model learns domain-relevant features independently

---

### Reproducibility

**Rating: 4/5** — High-quality code release with clear documentation, but MATLAB preprocessing dependency and data availability limit full end-to-end reproduction.

#### Strengths

- Complete code at [GitHub](https://github.com/HaiqianYang-MechE/MultiCell) with demo scripts for all three tasks
- Data archived on Zenodo (DOI: 10.5281/zenodo.17605530)
- PyTorch Geometric implementation with standard dependencies
- Clear MATLAB preprocessing pipeline
- Cross-validation protocol with 3 random seeds per split

#### Weaknesses

- **MATLAB dependency**: Preprocessing requires MATLAB R2024a for feature extraction from raw embryo meshes — not open-source
- **Data format**: Raw segmented embryo data referenced from Stern et al. 2022 (Figshare); additional embryos "available upon request"
- **Hyperparameter discrepancies**: Some paper-stated values (32-channel MLP, γ=10) differ from code defaults, requiring demo scripts for exact reproduction
- **Missing intermediate data**: The preprocessed `MultiCell.pkl` file is not included in the repo; users must run MATLAB preprocessing first
- **Hardware**: Trained on NVIDIA A100/L4 GPUs; the ~5000-cell graphs should be manageable on consumer GPUs

#### Practical Notes

- The demo scripts (`run/exec/*.sh`) contain the exact hyperparameters used in the paper
- **Missing dependency**: `requirements.txt` does NOT list `transformers` (HuggingFace), which is required for the cosine LR scheduler (`from transformers.optimization import get_scheduler` in `MC_main.py:4`). Install with `pip install transformers` to avoid ImportError
- The preprocessing script expects a specific directory structure for the raw embryo data
- NaN values in features (boundary cells) are silently replaced with 0.0

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
