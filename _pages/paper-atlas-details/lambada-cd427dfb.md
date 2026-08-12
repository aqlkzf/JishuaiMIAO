---
layout: default
permalink: /paper-atlas/lambada-cd427dfb/
title: "LAMBADA"
nav: false
description: "作者建立了 P3–P21 的发育脑三维图谱 LAMBADA，把透明脑光片成像、血管图、MRI、空间转录组和三维原位杂交统一到年龄匹配的坐标系中。结果显示，小鼠出生后脑血管不是匀速变密，而经历三个阶段：P3–P7 随脑体积等比例扩张，P7–P21 出现区域特异的快速增密与重塑，P21 后进入稳定和精修；驱动环境也从早期经典缺氧/血管生成信号转向神经元成熟与活动相关程序。 本地代码是通用 ClearMap 3.1 快照。"
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
      <span>Atlases &amp; Resources</span>
      <span>Cell · 2026</span>
    </div>
    <h1>LAMBADA</h1>
    <p>The spatiotemporal dynamics of postnatal vascularization in the mouse brain</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2026.03.013" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## LAMBADA：把出生后脑血管的三维生长放进同一个发育坐标系

论文：*The spatiotemporal dynamics of postnatal vascularization in the mouse brain*（Cell, 2026；DOI: 10.1016/j.cell.2026.03.013）

### 一句话理解

作者建立了 P3–P21 的发育脑三维图谱 LAMBADA，把透明脑光片成像、血管图、MRI、空间转录组和三维原位杂交统一到年龄匹配的坐标系中。结果显示，小鼠出生后脑血管不是匀速变密，而经历三个阶段：P3–P7 随脑体积等比例扩张，P7–P21 出现区域特异的快速增密与重塑，P21 后进入稳定和精修；驱动环境也从早期经典缺氧/血管生成信号转向神经元成熟与活动相关程序。

本地代码是通用 ClearMap 3.1 快照。它直接覆盖图像拼接、配准、血管二值化、骨架化、图构建、简化与图谱注释，但论文专用的 Swin3D-S 终点分类器、84 特征 cube 分析、scVI/cNMF、ADMBA 相关和生长曲线脚本没有随仓库提供。

### 1. 为什么先要建发育图谱

成年脑可注册到 Allen CCFv3，但幼年脑的体积、形状和各区域比例快速变化，透明化还会带来年龄依赖的非均匀变形。若把 P3 和 P21 都强行配准到成年模板，同一坐标不再代表同一发育解剖位置，密度差异还会混入组织收缩差异。

LAMBADA 为 P3、P5、P7、P9、P12、P14、P21 分别建立 25 μm 模板。每个年龄扫描 15–20 个透明脑，选择接近群体平均体积的样本作参考，左右对称化，再注册其余样本。专家依据自发荧光和神经解剖参考手工标注 62 个区域，并沿用 CCFv3 本体命名，使发育模板与成年图谱可以在层级上对接。

“年龄匹配模板”解决几何对应，“共同 ontology”解决区域命名对应，两者缺一不可。

### 2. MRI 为什么是透明脑之外的校准尺度

iDISCO+ 便于整脑成像，却改变组织体积。作者用年龄匹配的 MRI 提供更接近体内的区域体积，再把透明脑模板和标注转移到 MRI 平均图。

区域生长用 S 型曲线描述：

$$
V(t)=\frac{V_{max}}{1+e^{-k(t-t_0)}}.
$$

$V(t)$ 是年龄 $t$ 的体积，$V_{max}$ 是接近成年时的上限，$k$ 控制增长速度，$t_0$ 是增长最快的拐点。这个模型把离散 MRI 时间点转换成连续体积估计，用于修正透明脑中的长度密度和区域体积。

曲线是平滑校准模型，不表示所有脑区共享同一生物机制。MRI 样本数有限，置信区间和区域差异仍要保留。

### 3. 多模态如何对到 LAMBADA

作者把三类信息放到同一个参考空间：

- iDISCO+ 光片成像提供全脑血管或细胞的三维坐标；
- Visium 提供 P5、P7、P9、P12、P21、P60 三个冠状面的全转录组；
- TRISCO/HCR 与 Allen developmental mouse brain atlas（ADMBA）提供三维基因表达验证。

Visium 切片通过 ABBA 对齐到模板。初始解剖边界再用 Leiden 分群和分子标记校正。作者把三维 *Cck* 等原位信号投影到相同切面，与 Visium reads 比较；MBP 蛋白与 RNA 的空间一致性也作为跨模态检查。

这里的对齐不是像素完全相同：Visium spot、光片 voxel 和图谱 voxel 分辨率不同，因此最终相关分析必须先做空间聚合。论文的目标是宏观区域/空间程序对应，而非宣称单细胞一一匹配。

### 4. 从透明脑图像到血管图的 ClearMap 主线

血管以 CD31/podocalyxin 标记，动脉壁以 SM22/Tagln 标记。透明半脑经光片显微镜采集后，ClearMap/TubeMap 依次执行：

1. 拼接多块图像并校正照明；
2. 阈值、背景扣除、形态学处理及 deep filling 得到血管二值体；
3. 把三维二值体细化成单 voxel 骨架；
4. 以骨架 voxel 为顶点、26 邻域连接为边构建原始图；
5. 测量每个骨架点到背景的距离，作为局部半径；
6. 清理分支点 clique、孤立点和自环；
7. 把连续 degree-2 顶点链压缩成一条边，同时保留 edge geometry；
8. 将坐标变换到年龄匹配图谱，并写入脑区、半球与表面距离属性。

代码中的 `VesselGraphProcessor.pre_process()` 直接按 `skeletonize_and_build_graph → clean_graph → reduce_graph → register` 调用。`clean_graph()` 合并复杂分支点时用平均坐标并保留最大半径；`reduce_graph()` 将链的长度相加，但保留坐标和半径序列，因此简化后仍能计算真实弯曲路径。

### 5. 图结构中的关键量怎样定义

在简化血管图中：

- degree ≥ 3 的节点代表分叉；
- degree = 1 的节点代表断端候选；
- 边长是 edge geometry 相邻坐标的欧氏距离之和；
- 血管半径来自骨架到二值背景的距离；
- tortuosity 可写成：

$$
\tau=\frac{L_{path}}{\|x_{end}-x_{start}\|_2}.
$$

直血管的 $\tau$ 接近 1，越弯曲则越大。分支点密度、断端密度和长度密度通过 250 μm 半径球形 kernel voxelize 到三维图谱空间。

“密度”必须有分母。总长度增加可能只反映脑变大；长度密度稳定则表示血管网络与组织体积近似等比例扩张。论文据此区分第一阶段的 isometric expansion 与第二阶段真正的局部增密。

### 6. 为什么 degree-1 不能直接当作新生血管

真实断端可能是生长 tip、停滞或 pruning 中的血管，但成像弱信号、二值化缺口和骨架锐角也会制造假断端。作者设置多层校正：

1. 空间上相邻的明显断端重新连接；
2. 删除极短末端支路；
3. 用图连通性与距表面距离排除脉络丛和软脑膜血管；
4. 用 Swin3D-S 对断端中心的 30×30×30 图像块判断真实/伪影。

分类器在 3,735 个手工标注 patch 上训练，报告 AUC 0.9617，准确率 90.69%，召回率 95.36%，使成年图中的伪断端减少 91%。P5/P7 剩余断端超过 80% 带可见 tip cell，支持其作为活跃生长/重塑指标；到 P30 比例约一半，解释更偏重塑和稳定。

关键边界是：ClearMap 仓库包含通用图处理和部分过滤基础设施，但论文的 Swin3D-S 训练代码、权重和标注数据不在本地。因此“91%”是论文验证结果，不能由当前快照重新训练确认。

### 7. 三阶段模型怎样从多条曲线共同得到

论文分析 9 个年龄、50 个半脑血管重建。不是用单一 change-point 算法自动分段，而是综合多项结构指标确定阶段。

#### 阶段 1：P3–P7 等比例扩张

总血管长度随脑体积增加，但长度密度和分支点密度大体稳定。ERG$^+$ 内皮细胞密度先增加，说明细胞扩增在结构分叉明显增加之前发生。此时网络跟随脑整体长大，局部组织类型差异较小。

#### 阶段 2：P7–P21 快速扩张和区域特化

长度密度与分支点密度明显增加，断端密度在 P12 左右达到峰值，区域轨迹开始分离。阶段 2 又分 2a（P7–P12）与 2b（P12–P21）：后者出现高密度与低密度区域分组、皮层层特异方向、局部网络成熟类型和动脉壁变化。

#### 阶段 3：P21–P60 精修与稳定

总长度密度趋于平台或轻微下降，断端仍提示一定重塑，tortuosity 与 collagen IV 阳性末支变化显示网络继续精修。此时不是“发育停止”，而是从大规模增密转向修剪、稳定和成年比例建立。

阶段边界是多指标支持的生物学概括，不应解释为所有脑区都在同一天瞬间切换。

### 8. 区域差异：为什么全脑平均会掩盖阶段 2b

所有大区共享三阶段轮廓，但 P12–P21 分成两组：hindbrain、midbrain、thalamus、cerebellum 加速增密；striatum、hypothalamus、hippocampus、cortex 相对低密度。长度密度时间导数显示 P7–P9 和 P12–P14 两次增速变化。

感觉系统小区更接近所属大区的血管化时间，而不简单跟随各自神经关键期。这反驳了“局部神经活动在宏观尺度单独决定血管增密”的过度简化，但并不否定活动依赖信号在较细尺度的作用。

阶段 3 才出现部分性别差异，集中在胼胝体和神经内分泌相关区；P5/P12 未见同样差异。因此这些结果更接近青春期相关变化，不能回推为早期普遍性别效应。

### 9. ERG 与血管方向说明“细胞增加”不等于“立即形成分支”

ERG 标记内皮细胞核。P5 某些背侧区域 ERG$^+$ 细胞很多，却没有同等高的分支密度；到 P21 两者相关更强。这支持先增加或聚集内皮细胞、随后重排进入成熟网络的过程。

作者还用血管方向与皮层表面法向量比较，把血管分为更 radial 或更 planar。P5 各层方向较平，P14 后 layer 4 的 planar 网络和上层 radial 网络逐渐分开。

方向不是由二维图像目测，而是沿三维 edge geometry 计算局部切向量，再相对表面 normal 分类。ClearMap 图保留 edge geometry 与 `distance_to_surface`，为这类计算提供数据结构；论文专用方向分析脚本未完整包含在仓库。

### 10. 84 特征 cube 分析怎样得到六种血管结构

作者把配准后的血管图切成 300 μm 立方块。每个 cube 对 42 个量计算均值和标准差，形成 84 特征，包括边/点数、degree、半径、长度、tortuosity、断端/分叉数、方向、各阶邻域 hop 距离等。

处理步骤为：

1. StandardScaler 标准化；
2. PCA 保留 12 个成分，解释约 95% 方差；
3. 从各年龄抽取 cube 训练 K-means，初始 $k=10$；
4. 结合原始 CD31 图像去除 4 个边缘伪影簇；
5. 保留 6 种可解释的局部血管组织类型。

阶段 2b 中 dense/connected 的类型 5、6 增加；type 5 同时有高密度和 pruning 特征，只在高密度区短暂出现；成熟 type 6 在不同区域出现时间不同。

这里包含人工质控：六类不是纯粹由无监督模型自动宣布为“生物类型”。去除四个簇和解释结构类型都依赖图像复核。该论文专用 cube/PCA/K-means 脚本不在 ClearMap 快照中。

### 11. Visium、scVI 与 cNMF 如何寻找阶段性分子环境

Visium 覆盖 6 个年龄、3 个冠状面，每个平面 2–3 个重复。Space Ranger 生成 spot count 后，经 QC 和 log normalization，再选取 2,451 个与细胞通讯和脑细胞类型相关的基因。

scVI 学习 10 维潜表示以整合批次，后续使用模型推断的表达而非原始 counts。随后在 cortex、striatum、brainstem、hindbrain 四区分别运行 consensus NMF，每区 $k=30$：

$$
X\approx WH,
$$

其中 $W$ 表示基因对程序的权重，$H$ 表示每个 spot 的程序 usage。NMF 的非负约束使每个 spot 可由多个正向程序叠加，而不是被迫只属于一个 cluster。

程序 top genes 用细胞类型/过程基因集注释，再把 program usage 与配准到 Visium 平面的断端密度做 Spearman 相关。$r>0.3$ 的程序作为候选，不能直接称为血管生长的因果驱动。

scVI、cNMF 和选择阈值在论文方法中描述，但本地 ClearMap 仓库没有这些分析脚本与训练状态，因此只能由论文文字和图 7验证逻辑。

### 12. 分子环境为何从 Vegfa 转向神经成熟程序

ADMBA P4 全脑表达与断端密度的相关中，*Vegfa*、*Wnt7b* 可达到较强正相关；到 P14 相关显著减弱。Visium 同样显示经典因子主要对应阶段 1，阶段 2 后出现 *Sema3e*、*Apln*、*Wnt9a* 等候选，以及 *Slit2*、*Agt*、*Sema4a* 等负相关信号。

cNMF 程序的时间顺序从早期未成熟神经元（*Sox4*、*Dcx*），转向神经身份/轴突导向（*Satb1*、*Cux1*），再到活动与突触成熟（*Fos*、*Egr1*、*Pvalb*、*Syt2*）。这与结构三阶段在时间上对齐，支持神经血管环境随脑成熟改变。

相关的准确表述应是“空间表达模式与断端密度共同变化”。断端本身混合 sprouting、stalling、pruning，基因也可能由血管、胶质或神经元表达。真正的 ligand 功能需要细胞来源解析和扰动实验，论文在讨论中也保留这一边界。

### 13. ADMBA 与 TRISCO 各自提供什么验证

ADMBA 提供 P4/P14 的全脑原位表达，可补足 Visium 只有几个切面的限制。作者把 voxelized 表达注册到 LAMBADA，与三维断端密度逐 voxel 做 Spearman 相关并进行多重校正，得到阶段特异与共享基因集合。

TRISCO 对 *Vegfa*、*Cck* 等做整脑 HCR 成像，ClearMap/CellMap 检测阳性细胞并 voxelize。它验证某些 Visium 关系在三维仍存在，例如 *Vegfa* 与阶段 1 断端的联系更强，后来减弱。

两种验证仍是空间相关。ADMBA 年龄只有 P4/P14，TRISCO 基因数有限，不能等同于全时间、全基因独立重复。

### 14. ClearMap 代码中的直接实现证据

#### 图像和图谱准备

`PreProcessor.run()` 依次 stitch、resample、align。`setup_atlases()` 读取 atlas ID、annotation、hemisphere、reference 和 distance-to-surface 文件，并建立 affine/B-spline elastix 路径。它支持年龄模板，但 LAMBADA 模板生成和 62 区手工标注本身不在代码中自动完成。

#### TubeMap 图处理

`BinaryVesselProcessor` 负责二值化和组合 block；`VesselGraphProcessor` 负责 skeleton、raw graph、cleaned graph、reduced graph、atlas annotation 和动静脉追踪。代码明确：

- 半径最大搜索到 150 voxel；
- clean 时分支 clique 坐标取均值、半径取最大；
- reduce 时 edge length 求和并保留 geometry；
- 坐标先 resample，再依次通过 sample→autofluorescence 和 autofluorescence→reference 的 elastix 变换；
- 每个 vertex/edge 可写入 annotation、hemisphere 与最小 surface distance。

#### 通用批处理

`batch_process.process_sample()` 可选择 `align`、`cells`、`vasc`，血管路径依次调用 `binarize/combine_binary` 和 `pre_process/post_process`。这证明 ClearMap 是通用处理引擎，而不是论文统计分析的一键脚本。

### 15. Exact / Partial / Not found 对应边界

#### Exact / 高度对应

- 图像拼接、重采样、elastix 配准及 atlas annotation；
- 血管二值化框架、骨架化、graph-from-skeleton；
- 半径测量、clique 清理、degree-2 链压缩和 edge geometry 保留；
- 坐标、区域、半球、表面距离等图属性；
- CellMap 点检测和 voxelization 的通用基础；
- TubeMap 动脉信号属性与 graph tracing 基础。

#### Partial / 部分对应

- LAMBADA 可被 ClearMap 加载，但模板构建、参考选择、MRI 校准和人工标注不可由仓库自动重建；
- 论文使用的断端重连、pial/choroid 过滤可依赖 ClearMap 图属性，但具体实验参数和完整执行脚本不齐；
- vessel orientation、density voxelization 与 region statistics 有通用模块，论文图表生成链不完整；
- 仓库包含大量 ClearMap 测试与外部工具，但没有这 50 个样本的固定配置和最终分析 notebook。

#### Not found / 本地仓库没有

- Swin3D-S 终点分类训练代码、权重和 3,735 个 patch；
- 300 μm cube 的 84 特征/PCA/K-means 论文流程；
- scVI、cNMF 与 program–vessel correlation 脚本；
- ADMBA 全基因相关和阶段基因筛选脚本；
- MRI sigmoid 拟合、ABBA/Visium 精确对齐自动化；
- 论文全部统计图、性别差异与实验湿流程。

因此，本地代码对“如何从三维血管图像生成可配准图结构”覆盖较强，对“如何从这些图得出三阶段和分子驱动结论”只有部分或没有覆盖。

### 16. 最重要的解释边界

1. degree-1 断端不是纯粹 angiogenic tip，校正后仍可能混合生长、停滞和 pruning。
2. 密度变化必须用 MRI 校准后的组织体积解释，不能只看总长度。
3. 三阶段是多指标综合模型，不是对所有区域的硬 change point。
4. K-means 六种类型包含人工排除伪影簇的判断。
5. scVI imputation 和空间聚合会影响相关结构。
6. gene–vessel Spearman 相关只生成候选分子，不证明因果。
7. 当前 ClearMap 快照未记录明确 commit，且通用仓库可能与论文运行版本存在差异。

### 17. 证据入口

- 论文正文：`paper.md`
- 主图与补充图：`images/`
- 本地代码：`ClearMap/`
- 详细方法：`doc_method.md`
- 代码—论文对应：`doc_code.md`
- 逐图证据：`figure_analysis.md`

本文档的结构与分子结论以论文和图为最终依据；代码细节来自本地 ClearMap 快照的直接读取。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary: The Spatiotemporal Dynamics of Postnatal Vascularization in the Mouse Brain

**Authors**: de Launoit E, Skriabine S, Doumazane E, Bizou M, ..., Dubrac A, Renier N
**Journal**: *Cell* (2026) | **DOI**: 10.1016/j.cell.2026.03.013
**Code**: ClearMap 3.1 — https://github.com/ClearAnatomics/ClearMap
**Atlas**: LAMBADA — https://lambada.icm-institute.org/ (RRID: SCR_025382)
**Data**: GEO GSE313896 (Visium) | Zenodo 10.5281/zenodo.18876865 (vascular graphs)

---

### Motivation & Novelty

The cerebral vasculature is immature at birth, and postnatal vascular development must keep pace with both rapid brain growth and experience-dependent neuronal maturation. Despite its importance, brain-wide characterization of this process has been limited because (1) most structural studies focused on the cortex alone (Wang et al., *J. Cereb. Blood Flow Metab.* 1992; Harb et al., *J. Cereb. Blood Flow Metab.* 2013; Coelho-Santos et al., *PNAS* 2021), (2) molecular insights derived primarily from retinal models (Dubrac et al., *Dev. Cell* 2021), and (3) no developmental brain atlases existed for 3D tissue clearing approaches.

**Unique contributions**:

1. **LAMBADA atlas**: The first light-sheet-compatible developmental mouse brain atlas with 7 postnatal time points (P3–P21), 62 manually annotated regions following CCFv3 conventions, MRI-based volume corrections, and aligned spatial transcriptomics. This enables any lab using iDISCO+ to register developing brains to a common reference.

2. **Three-phase model of vascular development**: Through brain-wide quantitative analysis of 50 vascular reconstructions at capillary resolution, the study identifies three distinct phases — isometric expansion (P3–P7), regional specialization (P7–P21), and refinement (P21–P60) — that were not previously delineated at the whole-brain level.

3. **Molecular drivers across phases**: By correlating spatial transcriptomics with vascular remodeling maps, the study reveals a developmental shift from canonical angiogenic signaling (Vegfa, Wnt7b) in phase 1 to neuronal activity-dependent ligands (Apln, Wnt9a, Sema3e) in phases 2–3, with astrocytic braking mechanisms (Agt, Slit2) providing stabilization.

4. **ClearMap 3.1**: An updated open-source toolkit with improved graph corrections for developmental studies, including AI-based artifact detection (Swin3D-S, AUC = 0.96) and support for developmental brain atlases.

---

### Method Overview

The study integrates three data modalities through the LAMBADA atlas framework:

**Structural imaging**: iDISCO+-cleared brains immunolabeled for vessels (CD31/podocalyxin) and arteries (SM22) are imaged with light-sheet microscopy and reconstructed into vascular graphs using ClearMap's TubeMap pipeline (binarization → skeletonization → graph construction → cleaning → reduction → atlas registration). Custom correction layers — endpoint reconnection, short branch pruning, pial vessel removal, and Swin3D-S endpoint classification — reduce artifacts by 91%.

**Spatial transcriptomics**: Visium data from 3 coronal planes × 6 ages (P5–P60) are processed with SpaceRanger, integrated with scVI (10-dimensional embedding), and decomposed into gene programs via cNMF (k=30 per brain region, 4 regions). These programs are correlated with voxelized interrupted vessel density maps.

**3D molecular imaging**: Whole-mount in situ hybridization (TRISCO) for key genes (Vegfa, Cck) provides independent 3D validation of transcriptomic correlations.

All modalities are registered to LAMBADA developmental templates at 25 μm resolution, enabling cross-modal spatial correlation analyses.

For detailed methodology, see `doc_method.md`. For code-paper mapping, see `doc_code.md`.

---

### Evaluation

#### Datasets

| Dataset | Scale | Purpose |
|---------|-------|---------|
| Vascular reconstructions | 50 hemispheres, P3–P60, 9 time points | Structural vascular analysis |
| Visium spatial transcriptomics | ~12 sections (3 planes × 6 ages × 2–3 reps) | Molecular correlation |
| MRI scans | 24 mice (3 per age, P1–P21) | Volume correction |
| ADMBA (Allen Dev Brain Atlas) | Genome-wide ISH at P4, P14 | 3D molecular validation |
| ERG immunolabeling | Whole-brain, P5–P21 | Endothelial cell density |
| SM22 arterial staining | P7–P30 | Arterial wall maturation |

#### Key Metrics & Results

- **Vascular graph quality**: Swin3D-S endpoint classifier achieves ROC AUC = 0.9617, reducing artefactual endpoints by 91%
- **Atlas validation**: MBP protein (3D iDISCO+) correlates strongly with MBP mRNA (Visium), confirming multimodal alignment
- **Three-phase model**: Supported by concordant trends in branch point density, interrupted vessel density, tortuosity, and vascular length density across all brain regions
- **Molecular correlations**: Vegfa shows Spearman r > 0.5 with interrupted vessels at P4 but not P14; Sema3e strengthens in phase 2; Slit2 consistently anticorrelated
- **cNMF programs**: Neuronal programs temporally align with vascular phases — immature markers (Sox4, Dcx) in phase 1, identity genes (Satb1, Cux1) in phase 2, activity markers (Fos, Egr1) in phase 3
- **ADMBA validation**: 220 phase-specific genes (P4 vs P14 exclusive), with P4-specific genes enriched for hypoxia/angiogenesis and P14-specific for synaptic processes

#### Biological Validation

- ERG+ endothelial cell density dynamics diverge from vessel branch density, revealing a maturation/redistribution process (not just sprouting)
- Cortical layer-specific vessel orientations emerge during phase 2, coinciding with known critical periods
- Sex differences in vascular density appear in phase 3 (puberty-related regions: dbn, bnst, corpus callosum), not phase 1
- Collagen IV staining shows that terminal branches become increasingly stabilized after P21

---

### Reproducibility

**Rating: 3/5** (Moderately reproducible)

#### Strengths

1. **Data availability**: All major datasets are publicly available — Visium on GEO (GSE313896), vascular graphs on Zenodo, atlas at lambada.icm-institute.org
2. **Open-source toolkit**: ClearMap 3.1 is publicly available with documentation, GUI, and example notebooks
3. **Detailed STAR Methods**: Comprehensive descriptions of immunolabeling protocols, imaging parameters, and computational pipelines
4. **Multiple validation modalities**: Results confirmed across light-sheet, Visium, TRISCO, MRI, and ADMBA datasets

#### Weaknesses

1. **Analysis scripts not included**: The most paper-specific analyses — cube feature extraction (84 features), cNMF pipeline, scVI configuration, ADMBA correlation, sigmoidal growth fitting — are not in the ClearMap repository. Reproducing these requires significant reimplementation.
2. **Swin3D-S not in ClearMap**: The endpoint classifier (key to 91% artifact reduction) is described but neither code nor model weights are provided. Training data (3,735 annotated patches) is also not shared.
3. **Manual steps**: Atlas template selection, 62-region annotation, and ABBA alignment require neuroanatomical expertise and ITK-SNAP — these are not automatable.
4. **Large computational requirements**: Processing 50 hemispheres at capillary resolution requires substantial compute and storage. Imaging alone is 9–12 hours per hemisphere on specialized light-sheet microscopes.
5. **Python 3.7 dependency**: ClearMap's conda environment specifies Python 3.7, which is end-of-life. The graph_tool dependency further constrains the environment.
6. **No formal equations**: As a data/atlas paper, mathematical formulations are implicit (Spearman correlation, PCA, K-means, cNMF, sigmoidal fitting). Parameters are given in STAR Methods but the analytical pipeline requires careful reimplementation from textual descriptions.

#### Practical Notes

- **Environment**: ClearMap requires conda/mamba with graph_tool, PyTorch, PyQt5, vispy, elastix binary. Use provided `.yml` files for environment creation.
- **Hardware**: GPU required for vessel filling CNN and Swin3D classifier. Light-sheet microscope (UltraMicroscope II) and 11.7T MRI for data generation.
- **Time investment**: Expect weeks for a full developmental dataset (clearing, imaging, processing, analysis). Single time-point analysis is feasible in days.
- **Atlas access**: LAMBADA templates downloadable from lambada.icm-institute.org. Must be configured in ClearMap's atlas system to replace default ABA_25um.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
