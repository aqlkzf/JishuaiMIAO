---
layout: default
permalink: /paper-atlas/perturbview-0cb1da5a/
title: "PerturbView"
nav: false
wide: true
description: "光学混池筛选（optical pooled screening, OPS）的目标，是在同一个细胞里建立两种信息的对应关系： 显微成像得到的表型，例如蛋白定位、细胞形态、RNA FISH 信号； 这个细胞携带的 CRISPR 扰动，即 sgRNA 条形码。 传统 OPS 的代表工作是 Feldman 等发表于 Cell（2019）的 “Optical pooled screens in human cells”，其标准化协议发表于 Nat…"
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
    <h1>PerturbView</h1>
    <p>Multiplexed, image-based pooled screens in primary cells and tissues with PerturbView</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Genentech/PerturbView" target="_blank" rel="noopener noreferrer" aria-label="Open code for PerturbView">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PerturbView 方法详解

### 1. 它要解决什么问题？

光学混池筛选（optical pooled screening, OPS）的目标，是在同一个细胞里建立两种信息的对应关系：

1. 显微成像得到的表型，例如蛋白定位、细胞形态、RNA FISH 信号；
2. 这个细胞携带的 CRISPR 扰动，即 sgRNA 条形码。

传统 OPS 的代表工作是 Feldman 等发表于 *Cell*（2019）的 “Optical pooled screens in human cells”，其标准化协议发表于 *Nature Protocols*（2022）。这类方法把细胞中原本表达的 sgRNA 转录本依次做逆转录、padlock gap fill、滚环扩增（RCA）和原位测序（ISS），从而读出扰动身份。

问题在于，许多原代细胞、神经元和组织中的慢病毒条形码表达很低；同时，高通量表型往往要反复染色、清洗、漂白，这些操作会让原有 RNA 降解或扩散。于是研究者面临一个矛盾：表型测得越复杂，最后越可能读不到 sgRNA。论文指出，传统 OPS 因而主要停留在癌细胞系和低复用表型中（`paper.md:18-37`）。

PerturbView 的核心思想可以概括为一句话：**不要依赖表型实验之前就存在的少量条形码 RNA，而是在表型测完以后，再在固定样本中大量制造条形码 RNA。**

### 2. 方法的新意在哪里？

PerturbView 将两个已有方向组合并做了针对性优化：

- CROP-seq（*Nature Methods*, 2017）提供兼容 Perturb-Seq 的 sgRNA 载体结构；
- Zombie（*Nature Biotechnology*, 2020）证明 T7 RNA 聚合酶可以在固定样本中通过体外转录（IVT）放大条形码。

作者没有简单地把一个 T7 启动子放到 U6 前后，而是在 U6 启动子内部嵌入 T7 序列，构建嵌合 U6/T7 启动子。原因是同一载体必须同时满足两个目标：

- U6 活性足够高，sgRNA 才能正常完成 CRISPR 编辑；
- T7 活性足够高，固定后 IVT 才能产生大量可检测 RNA。

作者测试了 13 种设计。不同设计的 IVT 核内信号相差超过 40 倍；最终构建只替换原 U6 启动子的 13 bp，保留了接近野生型 U6 的编辑效率，同时产生很强的核内条形码焦点（`paper.md:47-53`；Fig. 1b–d）。补充材料给出了完整 PerturbView U6/T7 序列、引物、padlock probe 和逐步实验协议（`supp.md:10-109`）。

### 3. 从扰动到结果的完整流程

```text
构建 PerturbView sgRNA 文库
        │
        ▼
低 MOI 转导 Cas9 细胞/组织来源细胞
        │
        ▼
扰动发生并形成表型
        │
        ▼
固定样本，先完成高复用表型成像
（免疫荧光、HCR FISH、循环染色、Xenium 等）
        │
        ▼
必要时去除探针/漂白荧光
        │
        ▼
热解交联 → T7 IVT，大量生成条形码 RNA
        │
        ▼
逆转录 → padlock gap fill/连接 → RCA → 多轮 ISS
        │
        ▼
图像校正/拼接/配准 → spot 检测 → 跨轮追踪
        │
        ▼
碱基识别 → 条形码与 guide codebook 匹配
        │
        ▼
将扰动身份与单细胞表型或空间转录组连接
```

#### 第一步：构建并导入扰动文库

PerturbView 保留 CROP-seq 兼容性，因此同一文库原则上可以用于光学筛选和 Perturb-Seq。实验通常采用低 MOI，使大多数细胞只携带一个扰动。BMDM 筛选中，作者为每个基因设计 4 条 sgRNA，并在克隆和病毒包装过程中维持超过 1,000× 覆盖度（`paper.md:270-276`）。

#### 第二步：先测表型，再生成条形码 RNA

这是 PerturbView 与传统 OPS 最关键的顺序差异。以多模态巨噬细胞实验为例：

1. HCR FISH 检测 *Gbp2*、*Ccl4* 和 *Ripk2*；
2. 去除 FISH 探针；
3. 免疫荧光检测 IRF1、NOS2、p65 和 phospho-RPS6；
4. 漂白抗体荧光；
5. 此后才进行 T7 IVT 和 ISS。

因此，表型成像阶段即使损伤了原有 RNA，也不会直接破坏最终的条形码来源，因为条形码 RNA 是后续重新转录出来的（`paper.md:94-100,285-300`）。

#### 第三步：解交联与 T7 IVT

PFA 固定会抑制聚合酶，因此细胞培养样本采用 65 °C、4 h 热解交联；组织可延长到 24 h。之后在 37 °C 进行 T7 IVT，补充协议推荐 4 h 至过夜，并可加入 5 mM DTT 以降低所需 T7 酶量（`paper.md:225-237`; `supp.md:62-77`）。

作者观察到：

- 解交联从 0 h 增至 4 h 时，灵敏度和精确率明显提高，之后趋于平台；
- 3 h IVT 已能获得很大提升，继续延长的收益较小；
- 甲醇固定不需要同样程度的热解交联；
- DTT 对低 T7 酶浓度尤其有帮助。

#### 第四步：把 RNA 变成可测序的扩增产物

IVT 后仍沿用 OPS 的下游化学：RT 引物杂交、PFA/戊二醛固定、逆转录、padlock gap fill 与连接、Phi29 RCA、测序引物杂交和多轮 ISS。换言之，PerturbView 改变的是 **ISS 之前的条形码供给方式和实验时序**，不是完全替换 ISS 化学。

### 4. 图像如何变成 sgRNA 身份？

#### 4.1 图像预处理与配准

细胞筛选需要处理照明不均、背景、自发荧光以及不同成像轮次之间的位移。论文的多模态流程使用 ASHLAR 拼接整孔图像，再进行粗配准、切成 5,000 × 5,000 像素小块，最后用 microaligner 做仿射和光流非线性配准。细胞核由 Stardist 分割，并作为 watershed 细胞质分割的种子（`paper.md:324-342`）。

组织/Xenium 流程使用 BaSiC、m2stitch 和 WSIReg，将 ISS 图像通过刚性变换和非线性样条变换对齐到表型或 Xenium DAPI 图像（`paper.md:426-456`）。

#### 4.2 spot 检测

论文中的细胞筛选算法使用 $\sigma=1$ 的 Laplacian-of-Gaussian（LoG）滤波、3 像素最大值滤波、跨 cycle 变化和 5 像素邻域局部极大值来定位 ISS spot（`paper.md:345-348`）。组织流程则使用 9 像素最大滤波，将各通道 LoG 局部极大值合并，并在 5 像素半径内聚合。

公开代码并非逐参数复现这段方法。其默认路径使用需要外部模型的 Spotiflow，也提供可配置的 LoG 路径；随后跨通道膨胀、合并 peak，并提取坐标和通道强度（`scripts/call_bases.py:45-78`; `utils/call_utils.py:68-313`）。因此这部分属于 **Partial** 匹配。

#### 4.3 跨测序轮次追踪

论文在组织数据中用 trackpy，以 10 像素搜索半径连接不同 cycle 的 spot，保留至少出现 5 个 cycle 的轨迹，并允许在其他 5 个碱基唯一对应文库 guide 时补一个缺失 cycle（`paper.md:444-447`）。

公开代码确实调用 `trackpy.link`，允许一个 cycle 的 memory，并删除少于 5 次观测的轨迹；随后估计通道串色矩阵并做线性校正（`utils/track_utils.py:47-100`）。但仓库 Snakefile 传入的搜索半径是 30 个坐标单位，不是论文的 10 像素；论文所述“唯一匹配时补缺失 cycle”也未在已检查代码中找到。

#### 4.4 碱基识别与质量分数

每个 cycle 都取校正后最强的通道作为碱基。细胞筛选方法还定义了最高和第二高通道之间的质量分数：

$$
Q=1-\frac{\log \left(2+&#123;&#123;\mathrm{second}}}\right)}{\log \left(2+&#123;&#123;\mathrm{first}}}\right)}.
$$

第一强度远高于第二强度时，$Q$ 较高；二者接近时，$Q$ 较低（`paper.md:351-360`）。公开代码实现了最大通道取碱基、跨 cycle 拼接序列和缺失位点填 `N`，但 **没有找到 $Q$ 的实现**（`utils/track_utils.py:92-144`）。

#### 4.5 与 guide 文库匹配

公开代码计算观测序列与所有参考 spacer 的 Hamming 距离，选择最近的参考，并保留距离 `<2`，即最多 1 个错配（`utils/track_utils.py:147-172`）。这与论文组织分析中 Hamming distance $\leq1$ 的标准一致。

论文的细胞筛选还会按细胞标签聚合 reads，为每个细胞记录最常见的两个条形码，再与表型表连接（`paper.md:359-372`）。公开的组织仓库以 tracked particle 为输出单位，**没有找到按细胞取 top-two barcode 的实现**。

### 5. 如何评价 PerturbView？

#### 灵敏度与精确率

frameshift reporter 实验利用 HA 表型和 targeting guide 构造真阳性、假阴性与假阳性：

$$
\mathrm{sensitivity}=\frac{TP}{TP+FN}, \qquad
\mathrm{precision}=\frac{TP}{TP+FP}.
$$

在 A549 ×10 实验中，PerturbView 为 $72\pm9.7\%$ 灵敏度、$94\pm1.3\%$ 精确率；传统 OPS 为 $62\pm3.5\%$ 和 $80\pm15.6\%$。在 ×4 下仍达到 67% 灵敏度和 94% 精确率，并将典型 12-cycle 筛选的单板成像时间估计从约 24 h 降到约 4 h（`paper.md:56-59`）。

#### 原代细胞与神经细胞

相对于传统 OPS，条形码检出率在 iNeuron、巨噬细胞和原代 T 细胞中分别提升 1.6、2.9 和 2.0 倍；而在原本就比较容易检测的 astrocyte 和 fibroblast 中，提升较小（`paper.md:62-65`）。这说明 PerturbView 的主要价值集中在低表达、难分割或不耐受复杂处理的体系。

#### NF-κB 原代巨噬细胞筛选

作者在 BMDM 中筛选 163 个基因，每基因 4 条 guide，并分别用 TNF、IL-1β 和 LPS 刺激。p65 免疫荧光后，传统 OPS 的条形码检出率降到约 11%，PerturbView 仍约为 80%。筛选恢复了多个经典调控因子，并观察到明显的刺激依赖性：

- *Tnfrsf1a* 在 TNF 下最强；
- *Il1r1* 在 IL-1β 下最强；
- *Myd88*、*Irak4* 作用于 IL-1β/LPS，但不作用于 TNF；
- *Map3k7* 在该原代细胞背景中主要影响 LPS，显示细胞类型和刺激背景的重要性。

统计上，单细胞 p65 强度先基于 NTC 做 robust $z$-score，再通过 100,000 次重采样形成 guide 和 gene 层面的经验零分布，最后用 Benjamini–Hochberg FDR 调整（`paper.md:402-405`）。

#### 多模态 RNA + 蛋白筛选

PerturbView 在 HCR FISH 和免疫荧光之后仍能同时恢复表型和 guide 身份的细胞比例为 49.5%，传统 OPS 仅 0.6%。作者进一步用 PCA、对照群体 sphering、Leiden 和 PHATE 分析 guide/gene 的联合表型，得到 TNF 和 IL-1β 条件下不同的功能模块（`paper.md:94-109,408-423`）。

#### 组织与空间转录组

在 DLD-1 异种移植瘤中，六轮测序后超过 90% 的 reads 能映射到 100-guide 文库。PerturbView 在 FFPE 和 fresh-frozen 样本中分别恢复 66 和 90 条 guide，并在 PRKDC 阳性的人肿瘤细胞中达到 51.4% 检出率。与 Xenium 联合后，可在同一空间坐标中连接转录组、sgRNA clone 和局部 Shannon 多样性（`paper.md:112-132`）。

### 6. 复现性与已知缺口

综合评价为 **3/5，代码—论文一致性 medium**。

优势：

- 论文 Methods 和 24 步补充协议很详细；
- 给出了启动子、引物和 probe 序列；
- 八张主图/扩展图能够直接检查核心性能；
- 公开代码覆盖组织图像到条形码的关键链路：peak、trackpy、串色校正、最大通道 base call、Hamming 匹配。

限制：

- 公开仓库主要是 tissue/Xenium 分析，不是全文所有细胞筛选的完整代码；
- Snakefile 含机构内部绝对路径，Spotiflow `general` 模型未随仓库提供；
- 默认 `call_bases.main()` 保存路径引用未定义的 `output_dir`；
- 依赖多未固定版本，仓库没有核心流程测试；
- $Q$ 公式、按细胞 top-two barcode、完整 NF-κB/多模态统计流程和论文特定缺失-cycle 补全均为 **Not found in inspected scope**。

因此，PerturbView 的实验思想和关键组织 base-calling 步骤是可以理解和部分复用的，但仅凭当前快照还不能一键重现论文全部图表。

### 7. 最值得记住的三个点

1. **核心创新是时序解耦：**先做复杂表型，再用 T7 IVT 生成条形码 RNA。
2. **载体工程不可忽略：**U6/T7 嵌合启动子必须同时维持编辑与 IVT，简单拼接会损伤其中一项。
3. **实验可复现性强于计算端到端复现性：**补充协议很完整，但公开代码仅覆盖组织/Xenium 子流程，且仍需外部模型、数据和路径配置。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PerturbView

### Problem

Optical pooled screening (OPS) links image-based cellular phenotypes to pooled genetic perturbations by reading expressed sgRNA barcodes with in situ sequencing (ISS). Its practical use has been concentrated in cancer cell lines and relatively low-plex imaging because primary cells often express lentiviral barcodes weakly, and repeated staining/washing can degrade or displace barcode RNA before it is sequenced (`paper.md:18-37`).

The original human-cell OPS method (*Cell*, 2019) and its protocol (*Nature Protocols*, 2022) established scalable image-to-perturbation mapping, but still depend on RNA surviving through phenotyping and multiple enzymatic steps. Zombie (*Nature Biotechnology*, 2020) showed that T7 in vitro transcription (IVT) can expose fixed-cell barcodes, while CROP-seq (*Nature Methods*, 2017) provides a Perturb-Seq-compatible guide architecture. PerturbView combines these ideas while specifically optimizing the promoter and workflow for pooled optical screens.

### Proposed technology

PerturbView is a CROP-seq-compatible vector and assay in which a minimally modified chimeric U6/T7 promoter supports both CRISPR editing and T7 transcription. Cells are perturbed and phenotyped first; after fixation and any multiplex imaging, heat decross-linking and T7 IVT generate abundant barcode RNA, followed by the usual RT, padlock gap filling, rolling-circle amplification, and ISS. This post-phenotyping barcode production is the key innovation: barcode availability no longer depends only on pre-existing RNA surviving the imaging workflow.

The selected promoter replaces 13 bp of U6, preserves editing in tested cell types, and produces bright nuclear foci. Nuclear localization also simplifies assignment in morphologically difficult cells. The assay can be used at ×4 magnification, after iterative RNA/protein imaging, and in fresh-frozen or FFPE tissue.

### Main results

- In A549 frameshift-reporter experiments, PerturbView achieved $72\pm9.7\%$ sensitivity and $94\pm1.3\%$ precision versus $62\pm3.5\%$ and $80\pm15.6\%$ for conventional OPS at ×10. At ×4 it reached 67% sensitivity and 94% precision, reducing a projected 12-cycle plate acquisition from about 24 h to about 4 h (`paper.md:56-59`).
- Barcode detection improved 1.6-fold in iNeurons, 2.9-fold in macrophages, and 2.0-fold in primary T cells, while remaining comparable in cell types where conventional OPS already worked well (`paper.md:62-65`).
- In primary bone-marrow-derived macrophages, barcode detection after p65 immunofluorescence was about 80% with PerturbView versus 11% with conventional OPS after phenotyping. A 163-gene, four-guides-per-gene screen recovered canonical and stimulus-specific NF-κB regulators, including receptor-specific effects for *Tnfrsf1a* and *Il1r1* and context-dependent behavior of *Map3k7* (`paper.md:68-88`).
- A multimodal macrophage screen combined HCR FISH for three RNAs with immunofluorescence for four proteins. PerturbView recovered phenotype and guide identity in 49.5% of cells versus 0.6% for conventional OPS after phenotyping, enabling PHATE/Leiden analysis of cofunctional perturbation modules (`paper.md:91-109`).
- In DLD-1 xenografts, six-cycle tissue ISS assigned more than 90% of reads to the 100-guide library. PerturbView recovered 66 guides in FFPE and 90 in fresh-frozen tissue, and detected guides in 51.4% of PRKDC-positive human cells. Combined Xenium–PerturbView maps related sgRNA clone identity and local Shannon diversity to spatial expression programs (`paper.md:112-132`).

### Computational analysis

The paper describes illumination correction, stitching, multistage image registration, Stardist/watershed segmentation, LoG-based spot detection, spectral cross-talk correction, maximum-intensity base calls, and per-cell barcode aggregation. Its cell-screen quality score is

$$
Q=1-\frac{\log(2+\mathrm{second})}{\log(2+\mathrm{first})}.
$$

The released repository is narrower: it is tissue/Xenium-oriented and implements Zarr-based preprocessing, peak detection, trackpy linking, cross-talk compensation, maximum-channel base calls, sequence construction, and nearest-codebook matching at Hamming distance $\leq1$.

### Reproducibility assessment — 3/5

**Code-paper fidelity: medium.** The public GitHub snapshot at commit `7e68003bc655ca1f8e6afb5602ac473027e2cd3a` exactly supports several tissue base-calling operations, including five-cycle retention, cross-talk correction, maximum-channel calls, and Hamming matching. Peak detection and tracking parameters only partially match the paper, and the repository does not contain the full cell-screen feature/statistics pipeline.

The paper provides detailed Methods, a 24-step supplementary protocol, promoter sequence, primer/probe sequences, and eight readable main/extended figures. The repository README now links an IDR dataset, but the checked-in Snakefile contains institutional paths, depends on an unbundled Spotiflow model, has mostly unpinned dependencies, and includes an undefined `output_dir` reference in the default `call_bases.main()` save path. The paper's $Q$ calculation, cell-level top-two barcode aggregation, and full downstream screen analyses were **Not found** in the inspected code. Additional reanalysis information is available only on request.

### Limitations

- Barcode RNA can diffuse, creating a sensitivity–precision tradeoff; improved anchoring remains a future direction.
- Fresh-frozen tissue is more sensitive than FFPE, and tissue experiments may require many cells and careful exclusion of necrotic/host regions.
- The demonstrated in situ experiment used ex vivo lentiviral transduction followed by xenografting, not direct pooled perturbation delivery in an intact animal.
- The assay retains the multistep RT–padlock–RCA–ISS chemistry and substantial image-registration burden.
- Public code is an informative tissue-analysis snapshot, not a turnkey reproduction of every published experiment or figure.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
