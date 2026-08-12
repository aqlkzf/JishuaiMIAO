---
layout: default
permalink: /paper-atlas/espresso-a2f903c0/
title: "ESPRESSO"
nav: false
description: "ESPRESSO 不是把 RNA、蛋白或代谢物直接测出来，而是把活细胞内四类细胞器的形态、空间关系和功能敏感荧光强度编码成每个细胞的 3,328 维“细胞器表型”，再在连续成像中追踪这些表型如何随空间、时间和处理条件变化。"
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>ESPRESSO</h1>
    <p>ESPRESSO: spatiotemporal omics based on organelle phenotyping</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ESPRESSO 方法详解

### 一句话理解

ESPRESSO 不是把 RNA、蛋白或代谢物直接测出来，而是把活细胞内四类细胞器的形态、空间关系和功能敏感荧光强度编码成每个细胞的 3,328 维“细胞器表型”，再在连续成像中追踪这些表型如何随空间、时间和处理条件变化。

### 1. 它要解决什么问题？

scRNA-seq 等单细胞组学可以分辨细胞异质性，但通常需要裂解细胞，因此很难反复观察同一个细胞。空间组学补上了位置，却仍常是静态切片。真正的生物过程——分化、免疫极化、应激适应、肿瘤侵袭——往往是连续变化的。

ESPRESSO 的思路是：细胞器不是普通的图像结构，而是细胞状态的“环境传感器”。线粒体膜电位、溶酶体酸度、脂滴储脂和染色质组织都会随细胞状态变化。如果能同时、长期、单细胞地读取这些变化，就能得到一种可重复成像的时空组学表型。

### 2. 四个通道分别测什么？

| 染料 | 细胞器 | 主要功能代理量 |
|---|---|---|
| LysoTracker Green | 溶酶体 | 酸度 |
| TMRM | 线粒体 | 膜电位 |
| SMCy5.5 | 脂滴 | 脂肪酸储存 |
| SiR-Hoechst | DNA/细胞核 | 染色质组织 |

这些染料可以在活细胞中稳定成像至少 24 小时。它们的光谱高度重叠，所以 ESPRESSO 不用传统的逐通道滤光片，而是对每个像素采集完整发射光谱，再做光谱解混。

### 3. 从输入到输出的完整计算流程

```text
活细胞 + 四种细胞器染料
        ↓
高光谱显微镜获取 tiled .lsm 图像
        ↓
光谱 phasor 变换 + 线性解混
        ↓
每个细胞器通道分别用 CARE 去噪
        ↓
拼接 tiles、平滑、截断负值
        ↓
CellPose 分割单细胞
        ↓
对每个细胞提取强度分布 + ICS/ICCS 空间相关特征
        ↓
每个细胞得到 3,328 维特征向量
        ↓
归一化 + KS 检验 + Bonferroni 校正 + 人工阈值选特征
        ↓
3D PaCMAP 降维
        ↓
GMM 聚类；用 Davies–Bouldin 曲线辅助人工选聚类数
        ↓
ESPRESSO phenotype
        ↓
映射回显微图像，并进行空间邻域和时间轨迹分析
```

#### 3.1 光谱 phasor 解混

对每个像素的光谱沿光谱轴做傅里叶变换 $F$。源码在第 $h$ 个谐波计算

$$
g_h = \frac{\operatorname{Re}(\overline{F_h})}{\operatorname{Re}(F_0)},
\qquad
s_h = \frac{\operatorname{Im}(\overline{F_h})}{\operatorname{Re}(F_0)}.
$$

这里 $(g_h,s_h)$ 是光谱在 phasor 空间中的坐标。已知四种纯染料的 phasor 坐标矩阵 $P$ 后，代码用

$$
A=P^{-1}G
$$

求出每个像素中各染料的线性成分，再乘以该像素附近的总强度，重建四个细胞器通道。对应实现位于 `script_DEMO_ESPRESSO_LSM2IMG.py:41-57,88-122`。这一步把严重重叠的荧光光谱转换成可分别分析的细胞器图像。

#### 3.2 CARE 去噪为什么重要？

高信噪比通常需要更长曝光或更多扫描，会增加光毒性并降低时间分辨率。论文训练四个 CARE 模型，将快速低信噪比图像恢复为接近高信噪比的图像，从而把采集速度提高 16 倍。

公开代码验证了推理过程：解混后的每个通道分别进入 CARE 模型，再保存为 `.npy`（`script_DEMO_ESPRESSO_LSM2IMG.py:128-136,180-195`）。论文给出了训练数据、64×64 patch、80/20 划分、batch size 8、250 epochs 等参数，但公开包里 **Not found** CARE 训练脚本；只有配置、权重和推理代码。

#### 3.3 tile 拼接和 CellPose 分割

显微镜把大视野分成多个 tile。`LS_Functions.py:461-478` 按行列顺序重建图像，也支持双向扫描和重叠裁剪。随后代码对通道做平滑、把负值设为 0，并构造 CellPose 输入：

- 核通道：SiR-Hoechst；
- 胞质通道：其余细胞器通道之和；
- 2×2 binning；
- 99 百分位归一化；
- `cyto2` 预训练模型。

对应源码是 `script_DEMO_ESPRESSO_CARE_tiling.py:217-309`。一个值得复现时检查的细节是：代码虽然计算了 `Cellpose_channels=[1,2]`，实际 `model.eval` 却传入 `channels=[0,0]`。

#### 3.4 为什么正好是 3,328 个特征？

ESPRESSO 不只计算“平均强度”或“平均大小”，而是保留完整分布。

##### 功能特征：强度直方图

四个通道分别使用 512 个对数强度 bin：

$$
4\times512=2{,}048.
$$

##### 形态特征：ICS 自相关

每个通道计算二维自相关函数，再做旋转平均，保留 128 个径向 bin：

$$
4\times128=512.
$$

##### 细胞器空间关系：ICCS 互相关

四个通道有 ${4\choose2}=6$ 个不同通道组合，每个组合保留 128 个径向 bin：

$$
6\times128=768.
$$

因此

$$
2{,}048+512+768=3{,}328.
$$

源码 `ESPRESSO_v6p2_func_tiling_tracking.py:146-236` 直接实现了强度直方图、FFT 相关、mask 校正、径向平均和裁剪/补零。该函数还返回可视化用的单细胞 RGB 图像；外层脚本再加入细胞坐标、CellPose ID 和文件名（`script_DEMO_ESPRESSO_CARE_tiling.py:313-357`）。

#### 3.5 特征选择不是完全自动的

代码先把不同条件、重复或时间点的 DataFrame 合并。强度特征按细胞归一化，再做 1/99 百分位缩放；相关函数只保留至少 99% 细胞非零的 lag。

随后对每一对实验条件、每一个特征计算两样本 Kolmogorov–Smirnov 检验和中位数差，并进行 Bonferroni 校正（`script_DEMO_ESPRESSO_FeatureSelection.py:351-418`）。程序绘制类似 scRNA-seq volcano plot 的图，但最终阈值由用户在终端输入。也就是说，哪些特征进入 PaCMAP 不是一个完全固定的自动规则，这是 ESPRESSO 的重要自由度。

#### 3.6 PaCMAP、GMM 和 phenotype

选出的功能—形态特征进入三维 PaCMAP，源码固定 `random_state=1`（`:500-516`）。然后代码尝试不同 GMM 聚类数和随机种子，计算 Davies–Bouldin index：

$$
DB = \frac{1}{K}\sum_i\max_{j\neq i}\frac{S_i+S_j}{M_{ij}},
$$

其中 $S_i$ 是簇内离散度，$M_{ij}$ 是簇中心距离。DB 越低，簇越紧凑、分离越好。但最终聚类数和随机种子仍由用户结合曲线和期望分辨率输入（`:566-609`）。这些 GMM 簇就是论文所说的 ESPRESSO phenotypes。

### 4. 空间和时间维度从哪里来？

ESPRESSO 的空间位置天然来自显微图像和 CellPose mask 的中心坐标。论文把坐标与 phenotype 放入 SquidPy，计算邻域富集 z-score。

时间维度来自反复成像。论文使用 TrackPy，以 50 pixels 搜索范围、memory 1、adaptive stop 1 和 adaptive step 0.95 把不同帧中的细胞连接成轨迹。若一条轨迹从簇 $i$ 开始、在簇 $j$ 结束，就给转移矩阵 $(i,j)$ 加一。

这两个步骤在论文方法中写得清楚，但对应的 SquidPy 和 TrackPy 代码在公开的五个 Python 文件中都 **Not found**。所以它们是论文层面的可复述方法，但不是本地源码可完整验证的模块。

### 5. 论文用哪些实验验证？

- **四种细胞系：** 8,838 个细胞形成明显不同的 phenotype 区域。
- **六种应激处理：** 有些处理改变已有 phenotype 比例，有些产生处理特异 phenotype。
- **角质形成细胞分化：** 73,430 个细胞在 22.5 小时内出现四个钙诱导 phenotype，并形成空间斑块。
- **巨噬细胞 M1 极化：** 67,381 个细胞中，LPS 富集的 phenotype 与更高 *NOS2* reporter、较低迁移和不同状态转移相关。
- **与 scRNA-seq 对比：** 11,907 个转录组细胞和 15,414 个 ESPRESSO 细胞在脂代谢、干性/染色质等趋势上部分一致，但对溶酶体酸度给出相反结果。
- **3D 肿瘤球：** 侵袭时间序列包含 375,964 个细胞；处理实验包含 97,150 个细胞。simvastatin 明显减少侵袭 phenotype，而 CoCl~2~ 下这些 phenotype 仍大量存在。

### 6. ESPRESSO 和 scRNA-seq 的关系

两者测量的层次不同：

- scRNA-seq 测上游基因表达；
- ESPRESSO 测下游细胞器功能和形态。

图 5 不是同一细胞的一对一多组学配对。实验先成像，再把培养物消化做 scRNA-seq，比较的是群体结构和宏观 phenotype。GitHub 仓库中的 `code_for_plot.pdf` 有 21 页 R 代码，能验证 Seurat、UCell、MSigDB/ssGSEA assay 的下游绘图与矩阵导出，但没有可执行 `.R` 文件，也缺少引用的 Seurat `.Rdata` 输入和上游 CellRanger/QC/doublet 代码。因此这一分支只能评为 **Partial**。

### 7. 代码—论文一致性

总体 fidelity：**medium**。

#### Exact

- phasor 坐标和线性解混；
- CARE 推理；
- tile 拼接和 CellPose；
- 3,328 维强度/ICS/ICCS 特征；
- KS + Bonferroni 特征选择；
- PaCMAP；
- GMM + Davies–Bouldin 和结果可视化。

#### Partial

- scRNA-seq 下游代码仅以 PDF 形式提供，且缺输入对象。

#### Not found

- CARE 训练脚本；
- TrackPy 时间轨迹实现；
- SquidPy 空间邻域实现。

### 8. 复现时最容易踩的坑

1. Zenodo demo 是 Spyder/GUI 工作流，不是命令行 pipeline。
2. 输入/条件依赖文件名和人工输入，容易产生不可追踪差异。
3. feature threshold、聚类数和随机种子由用户选择。
4. NumPy 文件启用 `allow_pickle=True`，只能加载可信来源。
5. CARE/Torch/CUDA 版本需要与旧环境兼容。
6. 论文全部成像数据不是公开下载，只能向作者申请；Zenodo 是 demo。
7. 3D 结果只覆盖染料和激光可到达的表层/侵袭细胞，不能外推到肿瘤球深部。

### 9. 最终理解

ESPRESSO 的创新不是某个单独的神经网络，而是把“可长期成像的细胞器环境传感器”组织成一条组学式计算链：每个细胞被表示为完整的功能分布和空间相关函数，再映射成可追踪的 phenotype。它在描述细胞状态变化方面很有力量，但 phenotype 的具体边界仍受人工特征阈值、聚类选择和实验参数影响。公开代码足以理解并静态验证核心 imaging-to-phenotype 方法，也原则上支持运行两细胞系 demo；要完整复现全文，还需要申请全量成像数据并补齐训练、空间、时间和 scRNA 上游代码。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ESPRESSO: Summary

### Problem

Single-cell and spatial omics provide high-dimensional snapshots but generally do not follow the same living cells through rapid biological transitions. ESPRESSO addresses this gap by using the morphology, organization and functional state of organelles as a live-cell phenotype that can be measured repeatedly in image space. The target use cases are dynamic processes such as differentiation, immune polarization, stress adaptation and tumor invasion.

### What ESPRESSO introduces

ESPRESSO (Environmental Sensor Phenotyping RElayed by Subcellular Structures and Organelles) combines:

1. four live-cell, organelle-specific dyes reporting lysosomal acidity, mitochondrial membrane potential, lipid-droplet fatty-acid storage and chromatin organization;
2. simultaneous hyperspectral imaging and spectral-phasor unmixing;
3. CARE denoising and CellPose single-cell segmentation;
4. full intensity-distribution and image auto/cross-correlation features;
5. condition-aware feature selection, PaCMAP dimensionality reduction and Gaussian-mixture clustering; and
6. image-space localization and, in the paper, TrackPy/SquidPy temporal and spatial analysis.

The method generates 3,328 features per cell: four 512-bin intensity histograms, four 128-bin auto-correlation profiles and six 128-bin cross-correlation profiles. It retains the full profiles rather than fitting a prespecified organelle model, which makes the representation broadly applicable but also high dimensional and sensitive to downstream selection choices.

### Main findings

- **Cell-type discrimination:** 8,838 cells from four lines occupy distinct phenotype regions and show interpretable differences in chromatin, mitochondrial and organelle-distance features.
- **Stress response:** six perturbations either redistribute existing phenotypes or create stress-specific populations, revealing more structure than a single viability/readout score.
- **Keratinocyte differentiation:** 73,430 cells imaged over 22.5 h show four calcium-specific phenotypes with different emergence times and spatial patch formation.
- **Macrophage polarization:** in 67,381 cells, LPS-enriched phenotypes correlate with increased *NOS2* reporter expression, lower motility and altered cell-state transitions.
- **Comparison with scRNA-seq:** ESPRESSO (15,414 cells) and scRNA-seq (11,907 cells) agree on several calcium-differentiation programs, including fatty-acid/adipogenesis and stemness/chromatin trends, but disagree on lysosomal acidity. ESPRESSO additionally reports spatial structure and an approximately 0.1% rare morphology-rich cluster.
- **3D spheroids:** the method follows 375,964 cells during invasion and 97,150 cells under stressor treatment. It suggests that simvastatin depletes collagen-invading phenotypes more strongly than CoCl~2~, while measurements remain limited to optically/dye-accessible layers.

### What the code verifies

The Zenodo demo contains the complete five-file Python imaging-to-clustering pipeline, environment specification, model configurations and a public inventory of raw demo data, CARE weights and stored outputs. Direct source reads verify phasor unmixing, CARE inference, tile stitching, CellPose segmentation, the exact 3,328-feature construction, KS tests with Bonferroni correction, PaCMAP, GMM/DBI evaluation and phenotype visualization.

The paper-code fidelity is **medium** rather than high:

- CARE training, TrackPy tracking and SquidPy neighborhood-analysis implementations were **Not found**.
- Feature thresholds, cluster count and GMM random state are chosen interactively.
- The demo is Spyder/GUI driven, uses pickled NumPy objects and broad exception handling, and has no test suite or automated reproduction command.
- The GitHub scRNA repository contains tables/plots and a 21-page PDF R-code listing, but no executable `.R` files or the input Seurat objects referenced by the listing.
- Full paper imaging datasets are request-only; Zenodo provides a demonstration dataset and model assets.

### Limitations

- The dyes are indirect functional proxies and require stable staining/imaging conditions.
- Only four organelles are targeted, and tissue/dye penetration limits deep 3D analysis.
- Several experiments have limited biological replication; sample sizes were not predetermined statistically.
- Manual feature and cluster choices reduce pipeline determinism.
- Population-level ESPRESSO/scRNA comparisons do not match the same individual cells.
- Phenotype associations are descriptive and do not on their own establish causal molecular mechanisms.

### Reproducibility assessment

**3/5 — partially reproducible.** The public materials support a credible static reconstruction of the core method and a runnable demo in principle, including public raw demo inputs and model weights. Reproducing every manuscript panel requires request-only imaging data, experiment-specific parameters, absent CARE-training/spatial/temporal code and missing scRNA input objects. The most defensible reproduction target is the two-cell-line Zenodo demo, not the entire paper.

### Bottom line

ESPRESSO is a technology platform rather than a single predictive model. Its important contribution is to turn repeatedly imaged organelle properties into an interpretable, high-dimensional phenotype anchored to cell location and time. The results show substantial descriptive power across diverse biological systems, while the public release is strongest for the core imaging-to-phenotype workflow and weaker for the experiment-specific temporal, spatial and transcriptomic branches.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
