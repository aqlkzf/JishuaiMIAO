---
layout: default
permalink: /paper-atlas/scp-nano-9989a54e/
title: "SCP-Nano"
nav: false
description: "纳米载体（LNP、脂质体、聚合物复合物、DNA origami、AAV 等）是否真正到达目标细胞、是否在低水平下进入非目标器官，是药物递送安全性和有效性的核心问题。PET、CT、MRI 和常规活体光学成像能观察全身，但通常只能达到器官尺度，在低剂量下也可能缺乏灵敏度；传统组织学能看到单细胞，却只能检查预先选择的二维切片，容易产生抽样偏差。"
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
      <span>Technology Platforms</span>
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>SCP-Nano</h1>
    <p>Nanocarrier imaging at single-cell resolution across entire mouse bodies with deep learning</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/erturklab/SCP-Nano" target="_blank" rel="noopener noreferrer" aria-label="Open code for SCP-Nano">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SCP-Nano 方法详解

### 1. 它要解决什么问题？

纳米载体（LNP、脂质体、聚合物复合物、DNA origami、AAV 等）是否真正到达目标细胞、是否在低水平下进入非目标器官，是药物递送安全性和有效性的核心问题。PET、CT、MRI 和常规活体光学成像能观察全身，但通常只能达到器官尺度，在低剂量下也可能缺乏灵敏度；传统组织学能看到单细胞，却只能检查预先选择的二维切片，容易产生抽样偏差（`paper.md:18-27`）。

论文还指出，已有图像分析方案不能稳定处理全鼠体、跨器官、信号强弱差异巨大的数据：商业软件 Imaris 和 2019 年发表于 *Cell* 的 DeepMACT 在该任务上的 F1 均低于 0.50（`paper.md:65`, `paper.md:560`）。因此，SCP-Nano 的目标不是只训练一个分割网络，而是建立一条从实验制样到全身定量的完整技术链：

> 在完整固定小鼠中，以接近单细胞的空间分辨率定位荧光纳米载体或其货物表达产物，并生成器官级、组织级和全身级的三维定量图。

### 2. 核心创新

SCP-Nano（Single Cell Precision Nanocarrier Identification）把四个原本分离的环节接在一起：

1. **保留弱荧光的全身透明化**：改进 DISCO 流程，减少会损伤荧光的处理。
2. **全身光片显微成像**：获得约 1–2 µm 横向、6 µm 轴向分辨率的三维体数据。
3. **VR 器官标注 + 3D 深度学习分割**：先确定器官体积，再识别纳米载体阳性细胞/团簇。
4. **相对强度定量与密度重建**：把局部预测转为器官得分、密度图和全身分布图。

这使它既能看到常见的肝、脾富集，也能发现稀疏的心脏信号、器官内部热点以及不同给药途径造成的空间差异。

### 3. 输入与输出

#### 输入

- 带荧光标记的纳米载体、mRNA/脂质成分，或对货物表达蛋白进行免疫染色后的信号；
- 固定并透明化后的整鼠光片图像；
- 由 VR 标注得到的脑/头、心、肺、肝、脾、肾等器官标签；
- 针对 LNP、EGFP 表达或 AAV 等任务训练/适配的三维分割模型。

单个扫描可达到约 `30,000 × 10,500 × 2,000` 体素，无法一次装入常规 RAM/VRAM（`paper.md:407-410`）。

#### 输出

- 每个器官中的二值分割结果；
- 论文描述的连通“点”或细胞/团簇实例及其相对强度；
- 器官级纳米载体相对对比度得分；
- 平滑的器官密度图和合并后的全身密度图；
- 可进一步做组织学、免疫染色或蛋白质组学的候选区域。

### 4. 从实验到计算结果的完整流程

```text
荧光标记纳米载体 / 货物表达蛋白
                ↓
小鼠给药与固定终点（常见为 6 h、72 h 或 AAV 的 2 周）
                ↓
优化 DISCO 全身透明化，尽量保留荧光
                ↓
光片显微镜采集全鼠三维体数据
                ↓
VR 标注器官 → 得到器官掩膜和包围盒
                ↓
按器官裁剪 → 切成重叠三维 patch → 强度归一化
                ↓
五折 3D U-Net 集成推理
                ↓
重叠区域平均 + 0.5 阈值 + 器官掩膜
                ↓
连通事件 / 相对背景强度定量
                ↓
16 × 16 × 4 局部密度窗口 + 3D 高斯平滑
                ↓
器官图放回全身坐标并合并
```

#### 4.1 透明化和成像

小鼠经 PBS 灌流和 PFA 固定后，使用循环系统进行脱色、PBS 清洗和 EDTA 脱钙，再经过 THF 梯度脱水、缩短至 20 分钟的 DCM 处理以及 BABB 透明化（`paper.md:308-323`）。论文报告，去除尿素和叠氮化钠、缩短 DCM 时间是保留 Alexa 荧光的关键（`paper.md:47-56`）。

成像使用 UltraMicroscope Blaze，常用 ×1.1 或 ×4 物镜，高倍率拼接重叠 25%，z 步长 6 µm，曝光 100 ms（`paper.md:356-359`）。这一步决定了 SCP-Nano 的“单细胞分辨率”首先是空间成像能力，而不是仅由网络产生的计算分辨率。

#### 4.2 训练数据和模型

LNP 数据集包含 31 个跨器官 3D 标注块：21 个训练/验证块含 13,927 个实例，10 个独立测试块含 6,424 个实例（`paper.md:392-398`）。器官和细胞事件使用 VR 标注；该标注思想基于 2024 年发表于 *Nature Methods* 的工作（`paper.md:561`）。

最佳模型是六层编码、五层解码、带跳跃连接和 Leaky ReLU 的 3D U-Net。论文给出的训练设置为：

| 项目 | 设置 |
|---|---|
| 训练 patch | `128 × 128 × 128` |
| batch size | 2 |
| 损失 | Dice loss 与 cross-entropy loss 的平均 |
| 优化器 | SGD |
| 学习率 | `0.0001` |
| 训练轮数 | 1,000 epochs |
| 验证方式 | 五折交叉验证 |
| 推理 | 每折最低验证损失模型的五模型集成 |

如果用公式表达论文的“平均组合”损失，可以写成：

$$
\mathcal{L}=\frac{1}{2}\left(\mathcal{L}_{\mathrm{Dice}}+\mathcal{L}_{\mathrm{CE}}\right).
$$

论文以实例 F1（也称 instance Dice）评估：

$$
F_1=\frac{2TP}{2TP+FP+FN}.
$$

LNP 独立测试集平均 F1 为 `0.7329`，各器官为 `0.6857–0.7967`；图 2 中 Imaris 的平均值仅 `0.0659`。这说明模型优势主要体现在复杂、密集、跨器官的三维事件识别，而不是简单强度阈值。

#### 4.3 大体积切块和重建

论文将过大的全身/器官体数据切成最大约 500³ 的 patch。发布代码的默认值是 300³，重叠 30 个体素（`SCP-Nano/2_image_cropping.py:9-28`）。对每个 patch 推理后，代码按照保存的空间偏移把预测累加到器官体积，并用重叠次数取平均：

$$
P(v)=\frac{\sum_p P_p(v)}{N(v)},\qquad M(v)=\mathbf{1}[P(v)>0.5].
$$

随后再乘器官掩膜，避免器官外假阳性（`SCP-Nano/5_seg_rebuild.py:26-77`）。

#### 4.4 相对背景强度定量

设器官 $o$ 中体素强度为 $I_o(v)$，预测前景为 $M_o(v)$，器官背景均值为 $B_o$。论文描述的单个连通事件 $c$ 得分为：

$$
q(c)=\sum_{v\in c}\frac{I_o(v)-B_o}{B_o},
$$

器官总量再对所有事件求和。这样不仅考虑事件个数，也考虑局部荧光相对背景的强弱（`paper.md:413`）。

发布代码能计算器官级正 Weber 对比度总和，但没有保留每个连通事件的独立测量表。它还先膨胀前景、排除其邻域，并截去背景强度最低和最高各 5% 后估计背景（`SCP-Nano/6_seg_analysis.py:22-120`）。因此，**器官级相对强度概念是 Partial 匹配，论文所述逐点测量实现为 Not found**。

#### 4.5 密度图

论文在 `16 × 16 × 4` 体素窗口内累加相对对比度，并用 3D 高斯滤波得到连续密度图（`paper.md:416`）。发布代码在每个窗口内先用 cc3d 删除小于 3 体素的连通域，再计算正对比度的**平均值**，随后平滑、归一化和缩放（`SCP-Nano/6_seg_analysis.py:123-236`）。

这里存在重要差别：

- 论文写的是局部对比度**求和**；
- 代码实现的是过滤后的正对比度**均值**。

二者都会突出热点，但对“事件数量/体积”和“平均亮度”的权重不同。

### 5. 主要实验结果

- **低剂量灵敏度**：在 `0.0005 mg kg^-1` 下，常规生物发光成像信号很弱，而优化透明化后的全身光片图像仍可见大量细胞尺度事件（Fig. 1）。
- **不同给药途径**：鼻腔给药主要富集于肺；静脉、皮内、肌肉等途径呈现不同的肝脾比例，并能看到器官内部热点和淋巴结差异（`paper.md:88-114`; Fig. 3）。
- **弱脱靶区域**：在心脏中观察到稀疏 LNP/蛋白表达信号，并结合组织学和蛋白质组学发现血管与免疫相关变化（Fig. 4）。这是小鼠中的相关性证据，不能直接推导成人类疫苗不良反应的因果机制（`paper.md:152`, `paper.md:231`）。
- **跨载体泛化**：LNP 模型在 DNA origami 数据上 F1 为 `0.8583`；AAV 适配模型 F1 为 `0.8019`（`paper.md:181`, `paper.md:213`）。
- **AAV 空间差异**：PHP.eB-AAV 在脑中标记 `245,229` 个细胞，Retro-AAV 为 `6,300`，约 38.9 倍；同时 Retro-AAV 显示广泛脂肪组织靶向（Fig. 6）。

### 6. 代码与论文的一致性

总体代码—论文一致性为 **medium**：

- **Exact**：器官裁剪、重叠 patch 生成、器官密度图放回并合并到全身空间。
- **Partial**：归一化、预训练模型推理、patch 重建、器官对比度、密度图计算。
- **Not found**：能完整证明论文训练配置的 SCP-Nano 专用训练入口/配置，以及逐连通点大小和强度的输出实现。

此外，预训练权重需从 README 的外部 Google Drive 链接下载；本地快照不包含权重。编号脚本依赖手动填写路径和器官名，`5_seg_rebuild.py` 的函数体还使用全局输出变量而非对应参数（`SCP-Nano/5_seg_rebuild.py:8-24`, `SCP-Nano/5_seg_rebuild.py:82-85`）。详细映射见 `doc_code.md`。

### 7. 如何正确理解 SCP-Nano

SCP-Nano 最重要的贡献，是把“全身覆盖”和“细胞尺度空间信息”放进同一条可定量技术链。它特别适合比较不同载体、给药途径和组织热点，并为后续分子实验提供空间导航。

但它不是实时药代动力学工具：小鼠必须固定和透明化，无法在同一动物上连续追踪；载体必须能被荧光标记或通过蛋白表达/免疫染色显现；原始全身数据、外部权重、计算资源和手工配置也限制了开箱复现。因而，这项工作在方法理解和空间发现方面证据很强，在从当前代码快照完整复现论文训练与逐点定量方面仍有明确缺口。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SCP-Nano summary

### Problem

Nanocarrier development needs whole-organism measurements that resolve individual targeted cells and weak off-target sites. PET, CT, MRI and conventional optical imaging provide longitudinal or organ-scale information but lack the required cellular resolution and low-dose sensitivity; histology provides high resolution but samples only selected 2D sections (`paper.md:18-27`). Existing computational options were also insufficient for this dataset: filter-based Imaris and DeepMACT—the latter introduced in *Cell* in 2019—produced F1 scores below 0.50, and Imaris averages only 0.0659 in the displayed benchmark (`paper.md:65`; Fig. 2c).

### What SCP-Nano introduces

Single Cell Precision Nanocarrier Identification (SCP-Nano) is an integrated experimental and computational technology for mapping fluorescent nanocarriers across entire fixed mouse bodies at cellular resolution. It combines fluorescence-preserving DISCO clearing, whole-body light-sheet microscopy, VR organ annotation, 3D U-Net segmentation, connected-event/relative-intensity analysis, organ density maps and whole-body reconstruction (`paper.md:27`, `paper.md:314-323`, `paper.md:389-419`). The VR annotation approach builds on work reported in *Nature Methods* in 2024; the selected model builds on the 3D U-Net family introduced at MICCAI 2016 (`paper.md:561`, `paper.md:567`).

The central computational strategy is to divide scans as large as roughly `30,000 × 10,500 × 2,000` voxels into overlapping patches, ensemble five trained 3D U-Net folds, stitch the patch predictions, restrict them to annotated organ volumes, and summarize positive fluorescence relative to organ background. Local `16 × 16 × 4` windows are smoothed into density maps and placed back into whole-body coordinates (`paper.md:401-416`).

### Evaluation and main findings

The LNP training resource contains 31 manually annotated 3D patches from multiple organs: 21 training/validation patches with 13,927 instances and 10 test patches with 6,424 instances (`paper.md:392-398`). The selected six-encoder/five-decoder 3D U-Net uses leaky ReLU, 128³ training crops, batch size 2, averaged Dice-plus-cross-entropy loss, SGD at `10^-4`, 1,000 epochs and five-fold ensembling (`paper.md:404`).

On the independent LNP test set, SCP-Nano achieves average instance F1/Dice `0.7329`, with organ scores from `0.6857` to `0.7967`, outperforming the displayed VNet, U-Net++, Attention U-Net, UNETR, SwinUNETR, nnFormer and Imaris results (`paper.md:79`; Fig. 2c). The platform detects LNP distributions at `0.0005 mg kg^-1`, shows strong route-dependent tropism, and exposes intra-organ hotspots and lymph-node patterns (`paper.md:88-114`; Fig. 3).

The study also demonstrates broader utility:

- an expression-adapted model detects EGFP protein across organs, while sparse heart signals guide histology and proteomics follow-up (`paper.md:123-152`; Fig. 4);
- the LNP-trained model reaches F1 `0.8583` on DNA origami and identifies liver-dominant distribution (`paper.md:178-181`; Fig. 5);
- an AAV-adapted model reaches F1 `0.8019` and measures approximately 40-fold more brain-labeled cells for PHP.eB-AAV than Retro-AAV, while revealing widespread Retro-AAV targeting of adipose tissue (`paper.md:190-216`; Fig. 6).

The heart findings should be interpreted as mouse associations, not evidence of a causal human vaccine mechanism. The authors used laboratory-produced formulations, observed proteomic and vascular-marker changes, and explicitly state that formulation differences and causality require further study (`paper.md:152`, `paper.md:231`).

### Reproducibility and limitations

**Reproducibility: 3/5.** The paper provides detailed clearing, imaging, training and analysis descriptions; the code repository exposes the seven-stage inference-to-density workflow and task-specific inference commands. Code-paper fidelity is **medium** (`doc_code.md`). Direct source reads verify organ cropping, patching, normalization, nnU-Net inference dispatch, patch reconstruction, organ contrast/density computation and whole-body merging.

Important gaps remain:

- trained models are downloaded from an external Google Drive link and are not in the local snapshot;
- SCP-Nano-specific training scripts/configuration and the paper's per-dot connected-component measurement output were **Not found**;
- several stages require editing module-level paths and organ names, and reconstruction uses global output variables despite function parameters;
- the released density implementation uses mean positive contrast per window, whereas Methods describes a sum;
- whole-body image data are available only on reasonable request, although source data accompany the paper and proteomics data are deposited as PRIDE `PXD056871` (`paper.md:516-525`);
- the method is destructive and endpoint-based, requires fluorescent labeling, complex clearing/imaging and substantial computing resources, and cannot replace longitudinal PET or live optical imaging (`paper.md:237`).

Overall, SCP-Nano's strongest contribution is a scalable bridge between whole-body spatial coverage and cell-scale nanocarrier analysis. The evidence supports sensitive mapping, comparative biodistribution and discovery of sparse targets across multiple carrier classes; it supports turnkey reproduction of the published training and quantification pipeline less strongly.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
