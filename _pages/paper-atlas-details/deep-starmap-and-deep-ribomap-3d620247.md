---
layout: default
permalink: /paper-atlas/deep-starmap-and-deep-ribomap-3d620247/
title: "Deep-STARmap and Deep-RIBOmap"
nav: false
description: "Deep-STARmap 与 Deep-RIBOmap 的真正创新，是用“通用低成本锚定 + RCA 扩增团二次水凝胶加固 + 六轮 SEDAL 解码”把靶向式三维原位转录/转译测量扩展到厚组织和数十万细胞；论文与源码足以支持平台原理和核心图像处理链，但完整复现仍需要研究专用配置、原始图像与下游分析脚本。"
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
    <h1>Deep-STARmap and Deep-RIBOmap</h1>
    <p>Scalable spatial single-cell transcriptomics and translatomics in 3D thick tissue blocks</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Deep-STARmap 与 Deep-RIBOmap：厚组织三维单细胞转录组与转译组方法详解

### 1. 方法要解决什么问题

空间转录组通常在薄切片上工作。切片足够薄时，探针扩散、光学成像和细胞分割都相对容易，但代价是细胞形态与真实三维邻域被截断。完整或厚组织成像能够保留空间结构，却同时遇到三个瓶颈：探针难以深入、扩增产物在多轮化学与成像中容易流失、深层荧光信号受散射和像差影响。

本文提出两个共享同一工程平台的方法：

- **Deep-STARmap**：在厚组织中检测预先选择的 RNA，得到三维单细胞空间转录组。
- **Deep-RIBOmap**：优先捕获与核糖体结合的 mRNA，以空间方式近似读取转译活性。

它们不是无偏的全转录组测序，而是针对目标基因面板的原位成像方法。核心价值在于把可扩展的探针锚定、滚环扩增产物加固、多轮 SEDAL 解码和三维图像分析组合成一个可用于 60–200 µm 组织块的平台。

### 2. 与已有方法的关系

本文建立在几条已有技术路线之上，而不是从零开始：

- **STARmap**（Wang 等，*Science*, 2018）将原位测序用于完整组织中的三维转录状态测量；早期演示面板较小，本文所引用的厚组织应用为线性编码的 28 个基因。
- **RIBOmap**把核糖体结合状态引入原位 RNA 检测，用 splint probe 选择与核糖体相关联的 mRNA，从而获得空间转译读出。
- **EASI-FISH**（Wang 等，*Cell*, 2021）展示了厚组织中的扩增型原位杂交，但它与本文在编码、扩增及读出设计上不同。
- 本文的下游数据整合使用 **FuseMap** 和 **Harmony**，细胞分割使用 Fiji 的 **Watershed 3D**，三维形态特征使用 Imaris，图像反卷积使用 Huygens。

Deep-STARmap / Deep-RIBOmap 的新增重点不是另造一种聚类算法，而是解决大面板探针成本和厚组织内扩增产物稳定性，使 STARmap/RIBOmap 式读出能够扩大到 1,017 个目标基因和数十万细胞。

### 3. 两个关键工程改进

#### 3.1 通用光交联锚定接头

传统设计如果要求每条基因特异探针都带昂贵的光交联和丙烯酰胺锚定基团，面板扩展到数千条探针时成本很高。本文把功能拆成两部分：

1. 大量普通的基因特异编码探针负责识别目标 RNA 和携带条形码信息。
2. 少量带 CNVK 光交联基团与 Acrydite 的通用接头负责把整套探针固定到聚丙烯酰胺网络。

通用接头与编码探针采用 5:1 的摩尔比。因为昂贵修饰只需合成一条通用序列，作者估算大于 4,000 条探针的专用修饰成本可超过 40 万美元，而通用接头成本低于 200 美元。这里的成本比较说明了扩展面板的工程优势，但不等同于完整实验成本。

#### 3.2 RCA 扩增产物二次水凝胶加固

目标序列经连接形成环状模板，再进行滚环扩增（RCA），形成局部高拷贝的 DNA 扩增团。厚组织需要经历清洗、透明化和多轮成像，未充分固定的扩增团会变形或流失。

本文在 RCA 时加入 aminoallyl-dUTP，使扩增产物带有可反应氨基；随后用 methacrylic acid NHS ester（MA-NHS）引入可聚合基团，再用 2% acrylamide、0.05% bis-acrylamide 进行第二次包埋。这样扩增团被共价连接到更致密的聚合物网络中。主图和扩展数据中的信噪比、荧光保留和循环稳定性实验共同支持这一改进。

### 4. 从分子捕获到六轮成像

#### 4.1 Deep-STARmap 的转录本捕获

基因特异探针在固定组织中与目标 RNA 杂交，通用接头经光交联并在凝胶聚合时嵌入网络。连接后的环状模板进行 RCA，随后按上节方式对扩增团二次包埋。每个目标基因对应一个六位颜色条形码，通过六轮 SEDAL 成像逐位读取。

#### 4.2 Deep-RIBOmap 的转译状态选择

Deep-RIBOmap 在共享流程前增加了选择步骤：splint probe 同时依赖目标 mRNA 与核糖体相关结构形成可连接模板，因此读出偏向核糖体结合的 mRNA。它测量的是目标 RNA 的相对核糖体关联/转译活动，而不是直接测定蛋白质数量或核糖体移动速率。

#### 4.3 SEDAL 循环

两种方法都使用六轮 SEDAL 荧光测序。每轮对扩增团读取一个颜色状态，完成成像后去除读出探针并进入下一轮。六轮颜色组合与预设 codebook 对应，从而把空间点还原为基因身份。多轮配准误差会直接影响条形码，所以三维配准与扩增团稳定性是解码可靠性的关键。

### 5. 图像到空间表达矩阵

#### 5.1 反卷积与强度标准化

论文使用 Huygens 的 maximum-likelihood estimation 反卷积，设置 SNR 10、10 次迭代。随后进行直方图均衡、三维快速傅里叶变换辅助处理和跨轮配准。论文还描述了二维中值滤波：参考轮使用 3×3 邻域，其余轮使用 2×2 邻域；这一操作未在所检查的 Starfinder 扩增团路径中找到，因此属于“论文描述、代码未核实”的步骤。

Starfinder 对每个候选点的四通道颜色向量做 L2 归一化。若某轮颜色强度为

\[
\mathbf{x}_r=(x_{r,1},x_{r,2},x_{r,3},x_{r,4}),
\]

则归一化为

\[
\widehat{\mathbf{x}}_r=\frac{\mathbf{x}_r}{\lVert\mathbf{x}_r\rVert_2}.
\]

最大分量决定该轮颜色，六轮结果组成条形码。代码还计算每轮主导颜色的对数质量，并对各轮取均值：

\[
Q=\frac{1}{R}\sum_{r=1}^{R}-\log(\max_c\widehat{x}_{r,c}),\qquad R=6.
\]

需要谨慎解释这个量：主导颜色越接近 1，`-log` 越接近 0，因此它不是常见的“越大越好”的 Phred 分数。仓库虽然声明了 `q_score_thershold` 参数，但检查到的过滤函数并未用它裁剪读段；实际过滤主要依据每轮信号结构、缺失状态和 codebook 匹配。

#### 5.2 三维配准与点检测

Starfinder 的 Snakemake 工作流调度 MATLAB 脚本完成图像准备、切分和读段识别。`STARMapDataset` 负责加载图像、预处理、全局/局部配准、候选点提取与保存。

- 全局配准通过 `RegisterImagesGlobal.m` 估计各轮到参考轮的变换。
- 局部非刚性配准通过 `RegisterImagesLocal.m` 实现，与论文提到的 `imregdemons` 相符。
- `SpotFindingMax3D.m` 在三维体素中寻找局部极大值。
- `ExtractFromLocation.m` 从每个候选位置提取各轮、各通道的强度。
- `FilterReads.m` 根据颜色调用和 codebook 过滤读段。

仓库存在不止一条执行路线。通用/低分辨率路线中可以看到局部配准调用，而 `deep_rsf_subtile.m` 的局部配准代码被注释。因此不能简单声称所有 Deep 路径都执行了论文描述的完整局部配准。

#### 5.3 切块、合并与细胞归属

厚组织图像体积大，工作流先按 FOV 和 subtile 分块运行，再合并结果。论文使用 Fiji Watershed 3D 获得细胞对象，删除小于 500 个体素的对象，然后以 10 个体素半径膨胀掩膜。`reads_assignment.py` 读取分割标签和解码点坐标，把每条读段分配到细胞，最终形成细胞×基因计数矩阵及空间坐标。

平均每细胞读段数在论文中报告为 Deep-STARmap 的 112.2±78.9 和 Deep-RIBOmap 的 84.0±59.9。由于 RCA 局部饱和与目标面板设计，这些计数更适合做同一实验中的相对比较，不宜等同于绝对分子计数。

### 6. 细胞类型、模态整合与空间分析

#### 6.1 鼠脑转录组—转译组整合

作者在相邻的 150 µm 小鼠半脑切片上分别运行 Deep-STARmap 与 Deep-RIBOmap，每种方法检测 1,017 个基因，获得 198,675 个转录组细胞和 164,029 个转译组细胞，共 362,704 个细胞。整合后得到 19 个主要细胞类型和 137 个亚群。

FuseMap 用于跨模态整合，Harmony 作为对照。主要细胞类型标签的一致率为 82.4%。这个结果说明两种读出在群体结构上高度相关，但两张相邻切片并不包含一一对应的同一批细胞，因此不能解释为单细胞配对多组学。基因层面的差异可用于提出转录丰度和转译状态不一致的候选机制，但仍需要独立实验验证。

#### 6.2 GO 与空间邻域富集

作者对模态差异基因做 Gene Ontology 分析。三维邻域用 Delaunay 图定义，并通过 1,000 次标签随机置换估计背景。若细胞类型 \(i\) 与 \(j\) 的真实邻接数为 \(O_{ij}\)，置换均值为 \(E_{ij}\)，可写成论文所用思想对应的对数富集：

\[
S_{ij}=\log_2\frac{O_{ij}+\epsilon}{E_{ij}+\epsilon}.
\]

这里的 \(\epsilon\) 只是为解释而写出的数值稳定项，论文并未给出该项的具体实现。该指标衡量空间共邻近而不是因果作用。

#### 6.3 人 cSCC 与三维邻域

作者在同一位患者的相邻 60 µm 皮肤鳞状细胞癌切片上检测 254 个基因，整合得到 51,471 个细胞和九类主要细胞。三维 Delaunay 邻域与二维投影得到的邻居数量和类型组成不同，说明把厚组织压成平面会改变微环境估计。由于样本来自同一患者且邻近关系是观察性的，图中所谓细胞“互作”应理解为空间关联，不能上升为配体—受体机制或因果作用。

#### 6.4 三维形态

保留厚度使神经元树突和细胞体形态可以用 Imaris 提取。论文使用 138 个形态特征训练随机森林分类器，并引用 Tetbow（Sakaguchi 等，*eLife*, 2018）作为神经元稀疏标记背景。该演示表明分子身份和三维形态可以关联，但测试集很小且类别不平衡，混淆矩阵不能作为成熟分类器的性能保证。

### 7. 实验结果应怎样理解

这项工作的主要证据链是：二次凝胶加固提高扩增团保留和信噪比；六轮读出在厚组织中仍能稳定解码；1,017 基因面板可扩展到数十万鼠脑细胞；转录和转译模态能恢复相似的主要细胞类型，同时显示基因层面的系统差异；厚组织能揭示二维投影丢失的邻域与形态信息。

作者报告大约 200 µm 内仍能获得可靠测量，但更深处性能下降。大规模脑图谱实际使用 150 µm 厚度，因此“可到 200 µm”应视为受样本、探针、透明化和显微镜共同制约的实用上限，而不是对所有组织都保证的固定深度。

Nature Reporting Summary 记录本研究总计分析 414,175 个细胞，主要发现基于一个生物学重复，第二重复用于分别展示验证结果。细胞数量非常大，但统计单位仍受动物、患者和切片层级限制，不能用海量细胞替代独立生物学重复。

### 8. 代码复现边界

本地 Starfinder 对应 GitHub 提交 `d6a1e2e0d88a04676d26ad17bf5d20a4ff895161`。已核实的核心静态调用链为：

```text
workflow/Snakefile
  → deep_create_subtile.m / deep_rsf_subtile.m / lrsf_single_fov_subtile.m
  → STARMapDataset.m
  → RegisterImagesGlobal.m / RegisterImagesLocal.m
  → SpotFindingMax3D.m / ExtractFromLocation.m / FilterReads.m
  → FOV 与 subtile 合并
  → reads_assignment.py
  → 细胞×基因矩阵
```

源码与论文的总体匹配度为**中等**：图像切分、配准、三维点检测、颜色提取、codebook 解码和细胞归属都有直接实现；但以下内容在有界搜索中仍缺失：

- 本研究实际使用的 YAML/参数配置；
- 原始成像数据与一次成功运行的环境记录；
- 论文描述的中值滤波在扩增团路径中的实现；
- 对声明质量阈值的实际使用；
- FuseMap、Harmony、GO、Delaunay 置换和 Imaris 分类的研究脚本。

论文报告 Python 3.8、MATLAB R2023b 和 R 4.2.1；Starfinder 环境文件固定 Python 3.9.16。Huygens 和 Imaris 还是商业软件。因此目前可以审计并重用核心图像解码代码，但不能仅凭工作区材料原样重跑论文的全部图表。

### 9. 方法的优势与局限

**优势**

- 通用锚定接头显著降低大规模探针面板的修饰成本。
- RCA 扩增团二次包埋增强了多轮成像中的稳定性。
- 同一平台兼容转录本和核糖体关联转录本读出。
- 厚组织保留真实三维邻域和更多细胞形态信息。
- 公开 Starfinder 使核心 image-to-count 路线能够被源码审计。

**局限**

- 必须预先选择基因并设计探针，无法发现面板外的转录本。
- RCA 饱和限制绝对定量，计数主要反映相对信号。
- 探针渗透、光散射和像差使有效厚度存在上限。
- 即使是厚切片，跨边界的完整细胞形态仍可能被截断。
- 转录与转译来自相邻切片，不是同一细胞内的配对测量。
- 生物学重复和人样本范围有限，部分空间与形态结论仍是概念验证。

### 10. 一句话总结

Deep-STARmap 与 Deep-RIBOmap 的真正创新，是用“通用低成本锚定 + RCA 扩增团二次水凝胶加固 + 六轮 SEDAL 解码”把靶向式三维原位转录/转译测量扩展到厚组织和数十万细胞；论文与源码足以支持平台原理和核心图像处理链，但完整复现仍需要研究专用配置、原始图像与下游分析脚本。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Scalable spatial single-cell transcriptomics and translatomics in 3D thick tissue blocks

### What problem does the paper solve?

Most image-based spatial transcriptomics methods are optimized for thin sections, while earlier intact-tissue implementations generally measured relatively small targeted panels, covered restricted fields of view or lacked a matched readout of translation activity. This paper introduces **Deep-STARmap** for targeted spatial transcriptomics and **Deep-RIBOmap** for targeted spatial translatomics in optically cleared tissue blocks. The aim is not whole-transcriptome discovery, but scalable, multiplexed three-dimensional mapping of selected RNAs or ribosome-associated RNAs at single-cell resolution in tissue up to hundreds of micrometres thick.

### Core technical contribution

The platform combines two main engineering changes with the existing STARmap/RIBOmap logic:

1. A universal photocrosslinkable and acrylamide-modified adapter anchors many gene-specific probes into the hydrogel without synthesizing the expensive anchoring chemistry on every probe. A 5:1 molar ratio of universal adapter to encoding probes is used.
2. After rolling-circle amplification (RCA), aminoallyl-dUTP is incorporated into the amplicons and coupled to methacrylic acid NHS ester. A second, denser acrylamide gel is then polymerized around the amplicons, improving their retention and signal stability during repeated imaging.

Deep-STARmap detects cellular RNAs directly. Deep-RIBOmap first uses a ribosome-bound splint probe to select ribosome-associated messenger RNAs, then applies the same amplification, re-embedding and six-cycle SEDAL sequencing workflow. Both assays therefore share most of the imaging and decoding pipeline while differing in what molecular state is captured.

### End-to-end workflow

Gene-specific probes are hybridized in fixed tissue, ligated into circular templates and amplified by RCA. The amplified products are covalently stabilized by hydrogel re-embedding, followed by six rounds of SEDAL fluorescence imaging. The paper describes deconvolution, intensity normalization, three-dimensional image registration, local-maximum spot detection, per-round color calling and codebook-based read decoding. Cell boundaries are derived with Fiji Watershed 3D, small objects below 500 voxels are removed, and masks are dilated by a radius of ten voxels before decoded reads are assigned to cells.

The released **Starfinder** repository implements the core image-to-count path with Snakemake, MATLAB and Python: image preparation, global and route-dependent local registration, three-dimensional peak detection, color extraction, codebook filtering, tile/FOV merging and read-to-cell assignment. The match between paper and code is useful but incomplete. In particular, the paper's median-filter step is not present in the inspected amplicon-processing route, the declared quality-threshold parameter is not applied during filtering, and the released repository does not contain the study-specific configuration or the downstream FuseMap, Harmony, enrichment, neighborhood and Imaris analysis scripts.

### Main evaluation

In adjacent 150-µm mouse hemibrain sections, Deep-STARmap and Deep-RIBOmap each target 1,017 genes and yield 198,675 transcriptomic cells and 164,029 translatomic cells, respectively—362,704 cells in total. Integration identifies 19 major cell types and 137 subclusters. Major cell-type labels agree for 82.4% of cells when the two modalities are compared after FuseMap integration, while gene-level comparisons expose structured differences between RNA abundance and translation activity.

In a 60-µm human cutaneous squamous cell carcinoma sample targeting 254 genes, the integrated analysis contains 51,471 cells and identifies nine broad cell types. Three-dimensional neighborhood analysis shows that full-volume measurements can produce different local-neighbor estimates from two-dimensional projections. The paper also demonstrates cell-morphology analysis in intact tissue, although the reported random-forest classifier is evaluated on a small and imbalanced test set and should be treated as a proof of concept.

The authors report useful measurements through approximately 200 µm of tissue; performance declines at greater depths because of probe penetration, optical attenuation and imaging constraints. The brain experiments use 150-µm sections, so the practical operating depth demonstrated at scale is below the nominal maximum.

### What the figures establish

The four main figures connect molecular stabilization to tissue-scale applications: improved amplicon retention and signal-to-noise after re-embedding; large-volume mouse-brain transcriptomic/translatomic mapping; cell-type and translation-state comparisons; and three-dimensional tumor-neighborhood analysis. Ten Extended Data figures add probe-design controls, depth and reproducibility measurements, codebook/read-quality diagnostics, expanded cell-type maps, replicate comparisons and morphology-classification details. All 14 retained figure assets were inspected directly. The figures support spatial association and modality comparison, but they do not establish causal cell–cell interactions, and adjacent brain sections cannot be interpreted as paired measurements of the same cells.

### Reproducibility assessment

Reproducibility is **moderate**. The paper provides extensive wet-lab parameters, a Zenodo data record and a public Starfinder repository pinned locally at commit `d6a1e2e0d88a04676d26ad17bf5d20a4ff895161`. The core image-processing code has clear static paths from Snakemake rules to MATLAB decoding and Python cell assignment. However, an end-to-end rerun is blocked by missing study-specific YAML/configuration files, unavailable raw imaging inputs in the inspected local materials, no recorded successful execution environment and absent downstream analysis scripts. The paper reports Python 3.8, whereas the Starfinder environment pins Python 3.9.16; commercial Huygens and Imaris software also affects full reproduction.

### Limitations and interpretation

- The assays are targeted and require prior selection and probe design; they are not unbiased transcriptome-wide profiling methods.
- RCA amplicons can saturate locally, so counts should be interpreted as relative rather than exact molecule numbers.
- Depth remains limited by chemistry and optics, with declining performance beyond roughly 200 µm.
- Thick-section morphology can still be truncated at sample boundaries, and light scattering complicates quantitative imaging.
- The Nature Reporting Summary states that major findings were based on one biological replicate, with validation shown separately; the very large cell counts do not replace biological replication.
- The mouse transcriptome and translatome maps come from adjacent sections, so concordance is population-level rather than within-cell paired multi-omics.

Overall, Deep-STARmap and Deep-RIBOmap are convincing technology-platform advances for targeted three-dimensional molecular mapping. Their strongest contribution is the combination of economical universal anchoring, mechanically stable re-embedded amplicons and a shared cyclic imaging/read-decoding workflow that scales to hundreds of thousands of cells. The released evidence supports the central platform claims, while exact computational reproduction of the published analyses still requires configuration, raw-image and downstream-script artifacts that are not present in the workspace.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
