---
layout: default
permalink: /paper-atlas/range-9663d9b4/
title: "RANGE"
nav: false
wide: true
description: "RANGE（Relaying Attention Nodes for Global Encoding）不是另造一种分子图网络，而是在已有 MPNN 的每个交互层后插入“聚合—广播”回路：多个虚拟 master node 先用注意力收集全体原子的消息，再把全局摘要送回每个原子。这样任意两个原子只需经过虚拟节点就能通信，同时连接数随原子数 N 线性增长，而不是全局两两注意力的 O(N^2)。"
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
      <span>Representation Models</span>
      <span>Nature Communications · 2026</span>
    </div>
    <h1>RANGE</h1>
    <p>Extending the range of graph neural networks with global encodings</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-69715-3" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for RANGE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ClementiGroup/range" target="_blank" rel="noopener noreferrer" aria-label="Open code for RANGE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## RANGE 方法解读：给局部图网络增加可扩展的全局通信通道

### 一句话抓住核心

RANGE（Relaying Attention Nodes for Global Encoding）不是另造一种分子图网络，而是在已有 MPNN 的每个交互层后插入“聚合—广播”回路：多个虚拟 master node 先用注意力收集全体原子的消息，再把全局摘要送回每个原子。这样任意两个原子只需经过虚拟节点就能通信，同时连接数随原子数 $N$ 线性增长，而不是全局两两注意力的 $O(N^2)$。

### 1. 为什么普通分子 GNN 看不远

机器学习力场把原子当作节点，只连接截断半径 $r_c$ 内的邻居。若模型有 $T$ 个消息传递层，一个原子的有效视野大致受 $T r_c$ 限制。增加层数会使远处信息经过越来越窄的中间通道，产生 oversquashing；层数过深又会令节点表示趋同，产生 oversmoothing。直接把截断扩大到整个体系则可能产生 $O(N^2)$ 条边。

论文关注的并不是抽象的图分类，而是能量和力：静电、色散、掺杂引起的电子重排等效应可能跨越数十 Å。若局部网络从未建立远距离通信路径，即便单个局部 block 很强，也无法从输入中恢复完全位于视野外的信息（论文第 13–27 行）。

### 2. RANGE 插在基础模型的什么位置

标准 MPNN 在第 $t$ 层先聚合邻域消息：

$$
\mathbf m_i^{(t)}=\bigoplus_{j\in\mathcal N(i)}
\mu_t\!\left(\mathbf h_i^{(t)},\mathbf h_j^{(t)},\mathbf e_{ij}\right),
$$

再更新节点：

$$
\mathbf h_i^{(t+1)}=v_t\!\left(\mathbf h_i^{(t)},\mathbf m_i^{(t)}\right).
$$

RANGE 保留这一步，然后依次执行：

1. **Propagation**：基础 SchNet、PaiNN、So3krates 或 MACE 的局部消息传递；
2. **Aggregation**：真实原子 $\rightarrow$ 多个 master node；
3. **Broadcast**：master node 与原子自身的 self-loop $\rightarrow$ 真实原子。

代码把这个顺序直接写在 `RANGEInteractionBlock.forward()`：先调用 `propagation_block`，再以标量节点表示更新 `virt_embedding`，最后用 `broadcast_block` 覆盖 `system.embedding[0]`（`range_code/src/rangemp/nn/blocks.py:785-843`）。因此 RANGE 是可附着的通信模块，基础模型仍负责局部几何与等变特征。

### 3. 虚拟节点和边如何建立

每个分子有 $K$ 个可学习 master-node embedding。它们不是物理原子，也不对应新的势能中心；代码按虚拟节点编号查 embedding，再为 batch 中每个分子复制一份（`models/base.py:150-159`）。

对每个分子，所有真实原子都连接到每个 master node，形成 $N K$ 条 aggregation 边。广播时，每个原子接收 $K$ 个虚拟节点以及一个自身通道，因此有 $N(K+1)$ 条 broadcast 边（`models/base.py:161-213`）。当 $K$ 固定时，两类边都为 $O(N)$。

“master node 位于几何中心”主要用于构造连续位置编码。非周期体系中，代码计算

$$
w_i=\frac{\lVert\mathbf r_i-\bar{\mathbf r}\rVert_2}
{\max_{j\in G}\lVert\mathbf r_j-\bar{\mathbf r}\rVert_2},
$$

其中 $\bar{\mathbf r}$ 是同一分子的平均位置；`calc_weights()` 的输出位于 $[0,1]$（`nn/utils.py:8-35`）。周期体系则先转到分数坐标、使用最小镜像修正，再映回笛卡尔距离（`nn/utils.py:38-80`）。归一化距离随后送入 cutoff 为 1 的 Gaussian basis（`models/base.py:165-170`）。

这一编码有两个目的：对旋转和平移不变，并把不同尺寸体系的径向位置统一映射到有限区间。它只记录相对中心的径向位置，不等于保存完整三维几何；局部方向和高阶等变信息仍来自基础网络。

### 4. 聚合：原子如何写入全局记忆

AggregationBlock 对每条“原子 $i$ 到虚拟节点 $k$”的边计算加性注意力。代码分别投影 receiver、sender 和边特征：

$$
Q=A_Q M_k,\qquad K=A_K h_i,\qquad
V=A_V h_i,\qquad E=A_E e_{ik}.
$$

每个 head 的未归一化分数来自

$$
s_{ik}=a^\top\operatorname{LeakyReLU}(Q+K+E),
$$

再按接收虚拟节点做 softmax，最后对 $V$ 加权求和。源码中的 `Q/K/V/E`、`scatter_softmax` 和 `scatter(..., reduce="add")` 与这一路径逐项对应（`blocks.py:91-137`）。输出再经 LayerNorm 和激活函数，成为新的 master-node 表示。

直观上，不同注意力 head 和不同 master node 可以选择体系的不同区域或特征。它不是把所有原子简单平均成一个向量，而是产生多个、分头的全局摘要。

### 5. 广播：全局信息如何回到每个原子

BroadcastBlock 反向连接虚拟节点到真实原子，并额外拼接一条真实原子的 self-loop。虚拟节点的 key/value 采用逐 head 参数矩阵，原子自身的 key/value 走单独线性层；随后同样用 $Q+K+E$ 的加性注意力计算权重（`blocks.py:218-277`）。

self-loop 很关键：它让每个原子在接收全局信息时仍能保留刚刚完成局部 propagation 的表示。若只有全局广播，所有原子容易被同一个摘要过度同化。图 1d 用灰色自环展示了这条“memory effect”通道。

广播值还乘以每条虚拟边的正则权重：

$$
\hat h_i=\operatorname{MLP}\!\left[
\sum_{k=1}^{K}r_k(N)\,\beta_{ki}V_k
+\beta_{\mathrm{self},i}V_{\mathrm{self},i}
\right].
$$

这里 $\beta$ 是广播注意力，$r_k(N)$ 决定第 $k$ 个虚拟节点对特定尺寸体系的有效贡献。实现位于 `blocks.py:269-277`。

### 6. 为什么需要动态正则化

仅增加 master node 数量并不保证信息容量提升；论文观察到未约束时多个虚拟节点可能学成退化、近似相同的注意力模式。RANGE 让第一个虚拟节点权重恒为 1，其余节点用可学习参数和体系原子数生成权重：

$$
\hat N=\frac{N-N_{\min}}{N_{\max}-N_{\min}},\qquad
\alpha(N)=\left|A(1-\hat N)+B\hat N\right|,
$$

$$
A=1+|p_2|,\qquad B=A\tanh(|p_3|),\qquad
r_k(N)=|p_{1,k}|^{\alpha(N)}.
$$

`LinearReg.forward()` 逐项实现这些计算，并为 self-loop 追加权重 1（`regularization.py:49-74`）。模型输出还暴露 `param1` 为 `regL1`；`RegL1` 把它向零做 L1 正则（`regularization.py:76-83,137-185`）。这使多余虚拟通道可被压低，并允许有效容量随体系尺寸改变。

这是一种软门控，不是运行时真的创建或删除节点；张量里仍有配置的 $K$ 个节点，只是部分节点贡献接近零。

### 7. 从输入到能量和力的完整路径

一次前向传播可按下列顺序读：

1. 输入原子坐标、元素编号、batch，以及可选晶胞和周期边界；
2. 基础模型建立截断邻居表与局部几何特征；
3. `MakeVirtSystem()` 建立 master embedding、aggregation/broadcast 边、中心距离 basis 和正则权重；
4. 每个 `RANGEInteractionBlock` 依次进行局部传播、全局聚合和全局广播；
5. 最终真实原子的标量 embedding 经 LayerNorm 和输出网络得到逐原子能量；
6. `scatter(..., reduce="add")` 对同一体系求和得到总能量（`models/base.py:219-256`）；
7. 力由能量对坐标的负梯度获得；这一步依赖训练/模拟框架，而不在当前仓库的核心 forward 中显式计算。

对 PaiNN、So3krates 和 MACE，RANGE 只在 `system.embedding[0]` 的不变量通道中做聚合和广播；等变向量或高阶表示由基础 propagation 更新。这样避免全局模块破坏基础架构的旋转对称性，但也说明 RANGE 并没有直接全局传递全部等变张量。

### 8. 图 1–5 分别回答什么

- **图 1**：方法图。a 展示 propagation—aggregation—broadcast；b 展示虚拟表示进入两个 block；c/d 展示 $Q,K,V,E$ 投影和广播自环。
- **图 2**：长程能力。NaCl、Au/MgO 和 biodimer 任务比较 SchNet、PaiNN、So3krates、MACE 及其 RANGE 版本。论文报告 charged biodimer 的能量误差最多降低约四倍；这是特定训练/测试设置的结果。
- **图 3**：代价—精度关系。AQM 上比较不同 cutoff 的力 MAE、推理时间和峰值显存。图支持“较短 cutoff 的 RANGE 可优于较长 cutoff 基线”，而不是证明 cutoff 永远无用。
- **图 4**：分子动力学稳定性。PaiNN+RANGE、$5\AA$ cutoff 在 DHA、buckyball catcher 和 double-walled nanotube 上运行 16 ns，曲线显示半径或层间距离在模拟中保持有界并探索多个状态。
- **图 5**：注意力解释。将某个 head 的注意力权重做 SVD，把第一主成分映射回原子，显示 aggregation 与 broadcast 可形成跨体系的不同聚类模式。注意力可视化是机制线索，并不等同于严格的物理因果分解。

主文还在 Table 1 将 RANGE、Ewald MP 和 Neural $P^3M$ 应用于 PaiNN/MD22。论文结论是 RANGE 与 Neural $P^3M$ 精度相近，而 RANGE 在所测体系上推理和显存开销更低。不能把这一有限比较外推为所有尺寸、硬件和实现上的普遍排名。

### 9. 训练和数据证据边界

论文方法部分说明：除 MD22 最多 500 epochs、MACE 最多 600 epochs 外，其余训练 200 epochs；损失结合能量与力，优化器为 AdamW；MD 使用 $300\,\mathrm K$ Langevin、$1\,\mathrm{fs}$ 步长（论文第 139–145 行）。但是当前 `range_code/` 主要包含模型、数据加载器和测试，完整训练配置与轨迹由 Zenodo 数据记录和外部 `mlcg` 提供。

本地工作区没有单独的 supplementary PDF。主文多次引用 Supplementary Notes 1–4、Supplementary Figures 和 Tables；现有 `doc_method.md` 中源自这些材料的超参数可用于导航，但若需要逐字或逐表复核，应先取得论文在线补充文件，不能把本地缺失的补充材料说成已经核对。

### 10. 论文—代码对应程度

### 11. 最容易误解的四点

第一，master node 是神经网络通信节点，不是新粒子，也没有独立物理坐标或电荷。第二，线性复杂度以 $K$、head 数和隐藏维固定为前提；较大常数仍会增加时间与显存。第三，RANGE 缓解局部通信瓶颈，但不会自动保证学到正确的库仑渐近形式或严格物理分解。第四，论文在多个分子任务上展示外推和稳定模拟，并不意味着离开训练分布后天然可靠；能量守恒、数据覆盖和长时间稳定性仍需针对新体系验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## RANGE: Extending the Range of Graph Neural Networks with Global Encodings

### Paper Metadata

- **Title**: Extending the range of graph neural networks with global encodings
- **Authors**: Alessandro Caruso, Jacopo Venturin, Lorenzo Giambagli, Edoardo Rolando, Zakariya El-Machachi, Frank Noe, Cecilia Clementi
- **Journal**: Nature Communications, 2026, 17:1855
- **DOI**: 10.1038/s41467-026-69715-3
- **Code**: https://github.com/ClementiGroup/range

---

### Motivation & Novelty

#### Problem

Graph Neural Networks (GNNs) are the workhorse of Machine-Learned Force Fields (MLFFs) for molecular simulations, but they are inherently local. The receptive field of each atom is limited by the cutoff radius times the number of message-passing steps. This makes GNN-based MLFFs unable to capture long-range interactions that are critical in molecular physics:

- Electrostatic interactions spanning tens of Angstrom (e.g., at biomembranes)
- Dispersion forces driving collective structural changes in large molecules
- Dopant effects propagating across crystal lattices

Simply increasing the cutoff or number of layers fails due to oversquashing (information bottleneck through finite channels) and oversmoothing (node representations converge), as demonstrated by Alon & Yahav (*ICLR*, 2021).

#### Limitations of Existing Approaches

- **Ewald-based methods** (Ewald MP by Kosmala et al., *ICML*, 2023; Neural P$^3$M by Wang et al., *NeurIPS*, 2024): project node embeddings to reciprocal space via Fourier expansion. Accurate but computationally expensive — large FFT grids consume prohibitive memory during MD simulations.
- **Global self-attention** (e.g., FlashAttention by Dao et al., *NeurIPS*, 2022; Performers by Choromanski et al., *ICLR*, 2021): $O(N^2)$ scaling makes it impractical for large molecular systems. Linear attention approximations exist but are difficult to combine with equivariant architectures.
- **Previous virtual node approaches** (Gilmer et al., *ICML*, 2017; Neural Atoms by Li et al., *ICLR*, 2024): use a single fixed-size vector to represent the entire system, limiting information capacity. Architecture-dependent implementations restrict generalization.

#### Unique Contributions

RANGE (Relaying Attention Nodes for Global Encoding) introduces three key innovations:

1. **Multiple dynamically allocated virtual nodes**: Unlike single-vector approaches, RANGE uses $K$ virtual "master nodes" with learnable regularization that adapts the effective number of nodes to system size.
2. **Model-agnostic attention-based aggregation/broadcast**: A GATv2-style attention mechanism connects all atoms to virtual nodes, applicable on top of any MPNN (demonstrated on SchNet, PaiNN, So3krates, MACE).
3. **SE(3)-invariant positional encoding**: Continuous mapping of atom-to-centroid distances to $[0,1]$ via Gaussian RBF, enabling transferability across different molecular sizes without introducing a limited field of view.

---

### Method Overview

RANGE extends any MPNN with a two-phase global information exchange at each interaction layer:

1. **Propagation**: Standard local message passing within cutoff radius (using the base MPNN)
2. **Aggregation**: Multi-head attention collects atom information into virtual node embeddings — each virtual node acts as a "learnable mean field" capturing different aspects of the system
3. **Broadcast**: Multi-head attention with self-loops redistributes global information back to atoms, with regularization weights controlling each virtual node's contribution

Virtual nodes are positioned at the molecular centroid with SE(3)-invariant positional encodings. The regularization mechanism uses learnable parameters with an L1 penalty to dynamically suppress unnecessary virtual nodes for small systems while activating more for larger systems.

The entire RANGE extension scales linearly with system size ($O(N)$), adding only a constant overhead independent of cutoff radius. See `doc_method.md` for detailed equations and `doc_code.md` for implementation mapping.

---

### Evaluation

#### Datasets and Tasks

| Dataset | Task | Size | Key Challenge |
|---------|------|------|--------------|
| NaCl crystal | Energy profiles with displaced Na | 16-17 atoms | Long-range charge redistribution |
| AuMgO | Dimer approaching doped/undoped surface | Periodic | Dopant effect at long range |
| Biodimers | Energy/forces at 4-15 Angstrom separation | 2 molecules | Extrapolation beyond training cutoff |
| AQM | Intramolecular interactions | 30-92 atoms | Cost-accuracy tradeoff |
| QM7-X | Small molecule energies | Up to 23 atoms | Baseline comparison |
| MD22 (DHA, CC, DW) | Forces and energies | 56-370 atoms | Comparison with Ewald MP, Neural P$^3$M |

#### Key Results

**Long-range tasks (Fig. 2)**: All baseline models (SchNet, PaiNN, So3krates, MACE) fail to predict correct energy profiles beyond their cutoff. RANGE-extended versions accurately reproduce the behavior, including extrapolation to unseen interaction regimes. Energy errors for charged biodimers are reduced by up to 4x.

**Cost-accuracy tradeoff (Fig. 3)**: On AQM, RANGE models at 5 Angstrom cutoff outperform baselines even at 12 Angstrom cutoff, demonstrating that the accuracy gain is not achievable by simply increasing the cutoff (oversquashing saturates the baseline MAE). RANGE adds constant overhead in time and memory.

**Comparison with competitors (Table 1)**: On MD22 systems (DHA: 56 atoms, CC: 148 atoms, DW: 370 atoms):
- RANGE and Neural P$^3$M achieve comparable accuracy (both significantly better than baseline and Ewald MP)
- RANGE has consistently **lower inference time** (1.24-1.57x vs baseline, compared to 1.40-1.59x for Neural P$^3$M)
- RANGE has consistently **lower memory** (1.13-1.22x vs 1.79-3.97x for Neural P$^3$M)

**MD simulations (Fig. 4)**: 16 ns trajectories with PaiNN+RANGE remain stable, sampling multiple metastable configurations in DHA, buckyball catcher, and double-walled nanotube systems.

**Interpretability (Fig. 5)**: SVD analysis of attention weights reveals each head develops a distinct clustering strategy, with different regions of the molecule activating different virtual nodes — consistent with a "learnable mean field" interpretation.

---

### Reproducibility

**Rating: 4/5** (Good)

#### Strengths

- **Code availability**: Full model architecture publicly available at https://github.com/ClementiGroup/range (Python package `rangemp`)
- **Data availability**: All dataset splits, configuration files, and MD trajectories on Zenodo (doi:10.5281/zenodo.18390311)
- **Clear hyperparameters**: Default configurations provided via factory classes (e.g., `StandardRANGESchNet`)
- **Multiple baselines**: 4 MPNN architectures tested, enabling fair comparison
- **Detailed supplementary**: Architecture details, dataset preparation, training hyperparameters in Supplementary Notes 1-4

#### Weaknesses

- **External dependency on `mlcg`**: Training loop, loss composition, optimizer, and MD simulation all depend on the `mlcg` package (v0.1.0, https://github.com/ClementiGroup/mlcg), which is not yet widely adopted
- **No training scripts in repo**: The RANGE repo provides only model definitions and dataset loaders, not complete training workflows. Users must integrate with mlcg or write their own training loop.
- **Some datasets require external download**: MaterialsCloud, QM7-X, and MD22 datasets must be fetched from external sources

#### Practical Notes

- **Python ≥ 3.12** required
- Dependencies: `torch ≥ 2.6.0`, `torch-geometric ≥ 2.6.1`, `mlcg` (from GitHub), optional `mace` package for MACE models
- `torch.compile` compatible (custom pure-PyTorch scatter operations replace `torch_scatter`)
- GPU memory: RANGE overhead is small (12-22% increase over baseline), scales linearly with N
- Default hyperparameters: 144 hidden channels, 432 virtual hidden (3x), 8 attention heads, 3 interaction layers, 10-dim virtual basis

#### Common Pitfalls

1. The `mlcg` package must be installed first — it provides essential components (radial basis, cutoff functions, neighbor list, MLP, equivariant layers)
2. MACE variant requires separate `mace` package installation (v0.3.12)
3. For periodic systems, ensure `data.pbc` and `data.cell` are properly set — RANGE automatically switches between `calc_weights` and `calc_weights_pbc`
4. The `min_num_atoms` and `max_num_atoms` parameters in LinearReg should cover the dataset's atom count range for proper regularization behavior

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
