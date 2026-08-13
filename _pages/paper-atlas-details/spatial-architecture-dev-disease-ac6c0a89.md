---
layout: default
permalink: /paper-atlas/spatial-architecture-dev-disease-ac6c0a89/
title: "spatial-architecture-dev-disease"
nav: false
wide: true
description: "这篇文章不是介绍一种新仪器、算法或数据集，而是提出一套阅读空间组学研究的生物学框架：组织中的分子和细胞不仅“有哪些”，还以梯度、区域、邻域、克隆边界和跨器官模式组织起来。疾病可能改变这些空间关系，而空间位置也可能反过来塑造细胞状态和疾病进程。 作者把不同器官、疾病和技术得到的结果归入四个通用层级： 异常分子梯度与空间模式； 发育或疾病相关细胞状态的空间追踪； 作为疾病枢纽的多细胞生态位； 疾病的器官内和器官间空间异质性。"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature Reviews Genetics · 2025</span>
    </div>
    <h1>spatial-architecture-dev-disease</h1>
    <p>Spatial architecture of development and disease</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41576-025-00892-5" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for spatial-architecture-dev-disease">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Spatial architecture of development and disease：空间组学如何把“在哪里”变成机制证据

### 1. 这篇综述的核心贡献

这篇文章不是介绍一种新仪器、算法或数据集，而是提出一套阅读空间组学研究的生物学框架：组织中的分子和细胞不仅“有哪些”，还以梯度、区域、邻域、克隆边界和跨器官模式组织起来。疾病可能改变这些空间关系，而空间位置也可能反过来塑造细胞状态和疾病进程。

作者把不同器官、疾病和技术得到的结果归入四个通用层级：

1. 异常分子梯度与空间模式；
2. 发育或疾病相关细胞状态的空间追踪；
3. 作为疾病枢纽的多细胞生态位；
4. 疾病的器官内和器官间空间异质性。

这四层从“单个分子如何随位置变化”逐步扩展到“多个器官如何形成系统性疾病地图”。综述随后讨论这些发现如何进入临床，以及二维空间数据如何向三维、多组学和时间维度扩展。

### 2. 空间组学真正增加了什么信息

普通 bulk 测量把一个组织块平均为一个数，单细胞组学保留细胞差异，却通常在解离时丢失原位坐标。空间组学的基本数据对象可抽象为：

$$
\mathcal{D}=\{(x_i,y_i,[z_i],\mathbf{m}_i,\mathbf{h}_i)\}_{i=1}^{N},
$$

其中 $(x_i,y_i,[z_i])$ 是测量点或细胞坐标，$\mathbf{m}_i$ 是 RNA、蛋白、代谢物或表观遗传等分子向量，$\mathbf{h}_i$ 是组织学图像特征。空间信息让研究者能够问：某个分子是否形成梯度？某类细胞靠近谁？某种状态是否局限在病灶边缘？两个位置相近的细胞是否可能交流？

但“相邻”只表示几何关系，“相关”只表示统计共变，都不能自动等同于直接分子作用或因果机制。空间组学最有价值的用途，是把候选机制限制在真实组织结构中，再交给扰动、成像或临床验证。

### 3. 四类数据获取策略

图 1 把平台按空间坐标如何与分子读出绑定分成四类。

#### 3.1 原位探针或抗体检测

FISH、原位测序、循环荧光和多重抗体成像在组织中直接识别目标。它们常有单细胞甚至亚细胞分辨率，但通常需要预先选择靶标；覆盖越广，成像轮次、解码复杂度和误差累积越高。

#### 3.2 规则网格或栅格扫描

质谱成像等方法逐像素扫描组织，每个像素得到一组分子信号。坐标天然存在，但像素不一定等于单细胞，分子鉴定、灵敏度和绝对定量仍是主要限制。

#### 3.3 空间条形码捕获

测序型空间转录组把带坐标的条形码阵列与组织接触，捕获 RNA 后通过测序恢复“表达—坐标”对应。它可覆盖全转录组，但捕获效率、分子侧向扩散和一个 spot 中混合多个细胞会影响下游聚类与去卷积。

#### 3.4 感兴趣区域分子切割

GeoMx 一类方法先用形态标记定义区域，再以光诱导释放标签等方式读取区域分子。它适合临床病理指导下的定向测量，但区域平均会牺牲细胞级异质性，结果也依赖 ROI 的人为选择。

不存在所有指标都最优的平台。Box 1 的雷达图比较空间分辨率、分子覆盖、样本兼容性、可及性和成本，其重点是展示取舍，而不是给平台排出一个统一名次。成像型转录组趋向更高靶标数，测序型平台趋向更高分辨率，但低捕获效率仍是共同瓶颈。

### 4. 框架一：异常分子梯度和空间模式

若某个特征 $g$ 在位置 $s$ 的值为 $Y_g(s)$，空间变异分析要判断它是否显著偏离“位置与表达无关”的零假设。最简单的直觉是比较相邻位置是否更相似：

$$
I_g \propto \frac{\sum_{i,j}w_{ij}(Y_{gi}-\bar{Y}_g)(Y_{gj}-\bar{Y}_g)}
{\sum_i(Y_{gi}-\bar{Y}_g)^2},
$$

其中 $w_{ij}$ 表示位置 $i$ 与 $j$ 的邻接权重。高空间自相关提示聚集、区域或梯度，但具体工具可能使用高斯过程、图模型或其他统计量。

发育中，形态发生素梯度指导迁移、分化和器官分区；梯度受到遗传或环境扰动时，可能导致发育异常。疾病中也会产生新的空间梯度，例如肿瘤缺氧、pH、代谢物和细胞因子从中心到边缘变化，进而关联巨噬细胞状态、血管生成、免疫检查点和侵袭边界。类似模式还见于纤维化、感染、炎症和伤口修复。

这一框架的关键不是寻找“热区”本身，而是解释模式由什么产生。观察到表达梯度后，仍需区分真实生物过程与组织厚度、RNA 质量、捕获效率、批次、坏死区和细胞组成变化造成的假梯度。

### 5. 框架二：空间追踪细胞状态

空间数据常借助单细胞参考，把测量点映射为细胞类型或状态。若一个 spot 混有多个细胞，可写成近似混合模型：

$$
\mathbf{y}_s \approx \sum_{k=1}^{K}a_{sk}\boldsymbol{\mu}_k+\boldsymbol{\epsilon}_s,
\qquad a_{sk}\ge 0,
$$

其中 $\boldsymbol{\mu}_k$ 是参考中的细胞类型表达谱，$a_{sk}$ 是位置 $s$ 中类型 $k$ 的丰度。cell2location 等方法进一步用概率模型估计丰度及不确定性；Tangram 等方法学习单细胞与空间位置的对应。

映射完成后，研究者可以区分“某类细胞数量变化”和“同一类细胞在特定位置进入新状态”。这对于发育中祖细胞分化、肿瘤边缘 EMT 连续谱、神经退行性疾病中的区域易感细胞以及损伤后的再生状态尤其重要。

参考图谱并非绝对真值。不同供体、平台和处理造成的 domain shift，参考中缺失的稀有状态，以及混合 spot 都会影响映射。样本匹配的单细胞参考通常更贴近实际组织，但成本更高；公共 atlas 更易获得，却可能把疾病特异状态强行归入健康标签。

### 6. 框架三：多细胞生态位是疾病枢纽

生态位不是简单的细胞类型清单，而是重复出现的局部组成、空间排列和潜在交互。分析通常先建空间邻接图 $G=(V,E)$，再用每个细胞邻域内的类型比例、状态或分子信号聚类：

$$
\mathbf{n}_i=\sum_{j\in\mathcal{N}(i)}w_{ij}\mathbf{c}_j,
$$

其中 $\mathbf{c}_j$ 是邻居 $j$ 的细胞类型或状态向量。BANKSY 等方法在细胞自身表达之外加入邻域特征，以发现组织域和空间感知的细胞亚群。

在癌症中，肿瘤细胞、成纤维细胞、髓系细胞、淋巴细胞和血管可组成免疫抑制或治疗响应相关生态位；三级淋巴结构是具有明确组织结构的免疫生态位。纤维化、感染和损伤中也可形成促炎、修复或异常重塑的局部社区。

配体—受体分析进一步预测细胞间通信。COMMOT 等空间方法将表达与距离约束结合，并用最优传输描述潜在信号分配。但配体和受体共表达、距离接近仍不等于真正发生信号传递；分泌扩散尺度、蛋白水平、受体活化和下游响应需要额外证据。

细胞分割是此类分析的隐性风险。边界错误会把 RNA 分给相邻细胞，既改变细胞类型，又人为制造配体—受体共现。对分割敏感性、邻域半径和不同算法进行稳健性检查，应是空间生态位结论的重要组成部分。

### 7. 框架四：克隆、边界和跨器官异质性

空间位置能把基因组改变、克隆谱系和组织形态连接起来。在肿瘤中，可由拷贝数、SNP、条形码或空间基因组读出推断克隆，再观察克隆是否形成边界、侵袭前沿或治疗耐受区域。这里的空间共定位帮助重建克隆扩张，但从转录表达间接推断 CNV 的精度低于直接 DNA 测量。

疾病并不总局限于一个器官。转移癌的器官嗜性、系统性免疫疾病、感染和代谢病会在不同组织形成不同微环境。跨器官比较要在共同坐标或可比较的细胞状态上整合数据，同时保留器官特异结构。简单批次校正若过强，可能消除真正的器官差异；若过弱，又会把技术差异误作生物学异质性。

图 3 用分子—细胞—器官三个尺度说明：空间病理不是某一种疾病专属，而是可跨发育异常、肿瘤、纤维化、神经退行、感染、炎症和损伤使用的组织原则。

### 8. 从探索性图谱走向临床闭环

图 4 描绘的不是“做一次空间组学即可诊断”，而是双轨迭代：研究端在组织队列中做无偏空间分析、发现候选生物标志物；临床端结合病理和临床数据完成患者分层；最终把候选压缩成低成本、快速、可解释的定向空间 panel，再在独立队列评估诊断或治疗价值。

临床落地的主要门槛包括：

- FFPE 等常规样本兼容性与前处理标准化；
- 跨中心、批次和平台的可比性；
- 周转时间、成本和低通量；
- 大型图像与分子矩阵的存储和算力；
- 遗传信息隐私及监管要求；
- 在独立、多样化人群中的临床效用验证。

因此，合理路线通常是用高维平台发现标志物，再转为小面板验证，而不是把高成本研究平台直接复制进常规病理科。

### 9. AI 能做什么，不能做什么

文章把 AI 的作用分为若干层次：组织域识别、细胞分割、表达插补、多模态对齐、跨切片三维重建、病理图像到分子状态预测，以及面向诊断的视觉—语言助手。早期 spaGCN、ST-Net 等工具多解决局部任务；XFuse、DeepSpaCE 等引入概率或更可扩展的图像模型；后续模型尝试融合病理、空间先验、通路和临床结局。病理 foundation model 和多模态助手则希望把大规模切片知识迁移到新任务。

这里要区分三种输出：

1. **实测值**：由空间实验直接获得；
2. **插补值**：依据周围位置或单细胞参考补全；
3. **预测值**：仅由图像或模型生成。

预测分辨率高于原始测量分辨率，并不意味着获得了额外的实验真值。模型可能学习到组织类型、染色强度、中心偏倚或队列构成，而非目标机制。跨医院外部验证、校准、不确定性、数据偏倚和可解释性是临床使用前的硬门槛。

“虚拟细胞”和“数字孪生”代表更远期目标：用多层数据模拟细胞或患者组织对扰动和治疗的响应。当前更可靠的定位是生成可检验假设和优先实验，而非替代真实患者试验。lab-in-the-loop 的价值恰在于模型预测必须反复接受实验反馈。

### 10. 从二维切片走向完整组织

图 5 总结三条扩展轴。

#### 10.1 三维空间

常规切片厚约 $5$–$10\,\mu\mathrm{m}$，二维图像会压缩 z 轴信息并产生细胞重叠。三维重建可对连续切片做形态与分子配准：

$$
T_k^*=\arg\min_T\left[L_{\mathrm{image}}(T(I_k),I_{k+1})+
\lambda L_{\mathrm{molecule}}(T(M_k),M_{k+1})\right].
$$

配准误差、切片形变、缺失组织和跨切片细胞对应不确定性会逐层累积。组织透明化和三维成像提供更直接的结构，但成本、体积、分子覆盖和分析复杂度仍高。

#### 10.2 空间多组学

同一切片或相邻切片联合 RNA、DNA/表观遗传、蛋白、脂质、代谢物和形态，可连接调控、状态与功能。难点不是简单拼接矩阵，而是不同模态的动态范围、捕获效率、分辨率和锚点均不同。MUSE、SpatialGlue、MISO 等方法学习共享表示，但共享空间不应抹掉各模态独有的生物信息。

#### 10.3 时间维度

单张切片只是瞬时快照。时间信息可来自连续采样、发育 atlas、同位素或大分子标记、空间克隆条形码、空间轨迹推断，以及患者来源类器官的纵向扰动。轨迹和“空间转录组时钟”仍多为推断；在人类组织难以重复取样时，时间顺序尤其容易与个体差异混淆。类器官提供可控动态模型，却不能完整复现血管、免疫、神经和全身环境。

### 11. 如何选择平台和分析方法

选择应从生物问题倒推，而不是从最热门平台正推：

- 若目标是发现未知转录程序，优先广覆盖测序型平台，并接受分辨率或捕获效率取舍。
- 若目标是验证少量标志物的亚细胞定位，优先高分辨率定向成像。
- 若目标是细胞生态位，分割质量、邻域尺度和足够的组织面积比单纯基因数更重要。
- 若目标是临床分类，优先 FFPE 兼容、周转时间、批间稳定性和可解释的小面板。
- 若目标是调控机制，考虑同位点多组学或相邻切片对齐，并用扰动实验验证推断边。
- 若目标是系统性疾病，应设计多器官、共享元数据和共同坐标框架，而非事后拼接互不兼容队列。

分析报告至少应记录样本选择、组织处理、平台版本、捕获单位、分割算法、质量阈值、批次整合、参考 atlas、邻域定义、空间统计零模型、多重检验和独立验证。否则漂亮的空间图很难跨实验复现。

### 12. 证据边界与正确结论

这篇综述的结论是：空间组织为理解发育和疾病提供了单细胞表达矩阵之外的关键维度，且不同疾病可用共同的梯度、状态、生态位、边界和跨器官框架比较。它并未证明某一种平台或 AI 模型已经解决临床空间医学，也没有提供可运行的统一分析代码。

应保留以下边界：平台性能随样本、版本和评测指标变化；分割与去卷积是主要误差源；邻近和配体—受体共现不是因果通信；二维切片不能代表完整三维组织；多组学整合和 AI 插补会引入模型假设；临床可用性需要独立队列、监管和效用验证；时间动态通常无法从单次横断面测量直接得到。

### 13. 源证据导航

- 论文全文：`paper source/paper/vlm/paper.md`
- 原始图像：`paper source/paper/vlm/images/`
- 方法分类与数学解释：`doc_method.md`
- 逐图证据：`figure_analysis.md`
- 综述范围、比较表和开放问题：`summary.md`
- 深读批注与选型建议：`reading_notes.md`

上面提到的 BANKSY、COMMOT、cell2location 等是综述讨论的外部工具示例，不应误写为本论文实现或本地源码证据。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spatial architecture of development and disease

**Authors**: Enikó Lázár & Joakim Lundeberg
**Journal**: Nature Reviews Genetics
**Published**: 30 September 2025
**DOI**: [10.1038/s41576-025-00892-5](https://doi.org/10.1038/s41576-025-00892-5)
**Type**: Review article
**References**: 264

---

### Review Scope

**Field**: Spatial omics applications in human development and disease
**Time period**: 2019–2025 (primary coverage), with historical context
**Approach**: Application-driven — focuses on biological frameworks for interpreting spatial data rather than technology reviews
**Target audience**: Computational biologists, spatial omics practitioners, clinical researchers, oncologists
**Diseases covered**: Developmental disorders, cancer (10+ types), fibrosis, neurodegeneration (Alzheimer, Parkinson), infection (COVID-19), autoimmune (psoriasis, Sjögren's), wound healing
**Technologies**: Spatial transcriptomics, proteomics, epigenomics, metabolomics, multi-omics

The review is explicitly scoped to **application-driven spatial molecular profiling** — it delegates technology benchmarking to companion reviews (ref. 7, 8) and focuses instead on proposing **biologically interpretable, universal frameworks** for understanding how spatial organization shapes health and disease.

---

### Field Landscape

**~2000s**: FISH and IHC — inherently finite, limited multiplexing
**2019**: Visium spatial transcriptomics commercialized; first spatial transcriptomic atlas (heart)
**2020–2022**: Explosion of imaging-based platforms (Xenium, MERSCOPE, CosMx); sequencing-based whole-transcriptome
**2022**: Nature lists spatial multi-omics among "technologies to watch"; spatial epigenomics (CUT&Tag, ATAC) enabled
**2023–2024**: VisiumHD, Xenium Prime 5K achieve cellular-to-subcellular resolution; convergence of sequencing/imaging approaches
**2024**: Spatial proteomics named **Nature Methods "Method of the Year 2024"**
**2025**: Spatial metatranscriptomics, AI-driven 3D reconstruction, multi-sample harmonization tools emerging

**Key turning point**: Spatial omics technologies now enable high-throughput molecular profiling at single-cell or subcellular resolution, creating the opportunity for **spatial precision medicine** and the narrowing gap between spatial research and clinical diagnostics.

---

### Method Taxonomy

The review proposes **4 universal biological frameworks** for spatial omics data interpretation, organized hierarchically from molecular to organismal scale:

#### Framework 1: Aberrant Molecular Gradients and Patterns
Spatial distributions of molecules including sharp domains, gradients, and concentration continua.
- **Healthy context**: Morphogen gradients in embryogenesis (Wnt, BMP, FGF)
- **Disease context**: Hypoxia gradients in tumours; EMT state continuum; cytokine/chemokine distribution; epigenetic modification gradients
- **Key tools**: BANKSY (spatially-aware clustering), SpaceWalker, Monkeybread, NMF decomposition

#### Framework 2: Spatial Tracing of Disease-Associated Cell States
Mapping individual cell type positions and states within their spatial context.
- **Healthy context**: Developmental progenitors, differentiation trajectories
- **Disease context**: Cancer cell clones, tumour-associated macrophages, cancer-associated fibroblasts, oligodendrocyte disease signature in neurodegeneration
- **Key tools**: SPOTlight, cell2location, Tangram, stereoscope, RCTD, DestVI; slide-tags; Xenium/MERSCOPE for direct mapping

#### Framework 3: Cellular Niches as Disease Hubs
Multicellular communities defined by spatial co-localization that mediate disease.
- **Subtypes**: Infection foci, tumour microenvironment, TLS (tertiary lymphoid structures), stem cell niches, wound healing niches, fibrogenic microenvironments
- **Key tools**: SpaTalk, COMMOT, Spacia; spatial V(D)J; TLS scoring; ligand-receptor analysis tools

#### Framework 4: Inter-Organ Heterogeneity of Diseases
Shared pathophysiology manifesting variably across different organs.
- **Context**: Metastasis organotropism, multi-organ diseases (sepsis, lupus, arthritis)
- **Atlases**: HuBMAP, Human Cell Atlas, Tabula Sapiens, organ-specific developmental atlases

---

### Key Findings

#### Technology Convergence
Sequencing-based (whole-transcriptome, lower resolution) and imaging-based (subcellular resolution, limited panel) spatial transcriptomics platforms are rapidly converging in both resolution and analyte coverage. Low capture efficiency remains the major technical challenge.

#### Clinical Translation Framework
The review proposes a **stepwise strategy**: exploratory spatial analysis in defined cohorts → identify key biomarkers → design targeted spatial panels optimized for clinical throughput, cost, and interpretability. Greatest clinical advances so far are in oncology (spatial biomarkers correlating with tumour growth, metastasis risk, immunotherapy response).

#### AI Integration
AI tools represent a **paradigm shift** from task-specific models (spaGCN, ST-Net) through probabilistic inference (XFuse, DeepSpaCE) to multimodal foundation models (ENLIGHT-DeepPT, OmiCLIP, PathChat). ENLIGHT-DeepPT is highlighted as clinically driven: predicts treatment response from H&E slides by imputing transcriptomics and integrating drug response frameworks.

#### Harmonization as the Bottleneck
Single-cell integration tools (Seurat, Harmony) are routinely applied to spatial data but neglect spatial relationships. Dedicated spatial tools (STalign, STAligner, Popari, Smoothie) remain nascent. Common coordinate frameworks (CCFs) from HuBMAP/HCA provide anatomical backbone but fail with complex morphologies (tumours, development).

#### Segmentation as a Major Noise Source
A 2025 benchmarking study (ref. 161) found that segmentation errors introduce substantial technical noise. The field is shifting toward **segmentation-free approaches** (SSAM, FICTURE) that infer cell types without requiring predefined boundaries.

#### Key Controversial Points
1. Universal single-cell atlases are insufficient for disease state annotation — sample-matched references needed
2. Current CCC methods use cluster-based co-localization rather than primary spatial data
3. Spatial metabolomics remains semi-quantitative — fully quantitative methods lacking

---

### Open Problems

1. **Harmonization across datasets**: Spatial relationships neglected by current tools; CCFs fail for pathological morphologies
2. **Segmentation errors**: Major source of technical noise; segmentation-free paradigm emerging
3. **Temporal dimension**: Most platforms provide static snapshots; time-series, organoids, and lineage tracing partially address this but remain challenging in humans
4. **3D reconstruction**: 2D tissue sections miss z-axis information; AI-based serial section alignment and microCT offer alternatives but remain costly
5. **Dataset size for AI**: Insufficient spatial datasets for training large models (HEST-1K is early effort)
6. **Spatial metabolomics maturity**: Semi-quantitative, complex workflows, not yet standardized
7. **Spatial epigenomics**: Low signal-to-noise from few target molecules per cell; aggregation obscures single-cell dynamics
8. **Species translation**: Mouse → human translational gap remains; spatial studies on human samples difficult to obtain
9. **CCC spatial grounding**: Methods must transition from cluster-level predictions to primary spatial data
10. **Clinical infrastructure**: Cost, throughput, ethics (genetic data), sample processing standardization

---

### Method Comparison Table

#### Spatial Transcriptomics Platforms

| Method | Year | Category | Resolution | Coverage | Sample | Key Innovation | Limitation |
|---|---|---|---|---|---|---|---|
| Visium | 2019 | Sequencing | 55 µm | Whole transcriptome | FFPE/FF | First commercial whole-transcriptome | Multi-cell spots |
| VisiumHD | 2024 | Sequencing | 2 µm bins | Whole transcriptome | FFPE/FF | Single-cell resolution | Low capture efficiency |
| Stereo-seq | 2022 | Sequencing | 0.5–50 µm | Whole transcriptome | FF | Huge capture area, DNB patterning | Requires fresh-frozen |
| GeoMx DSP | 2020 | Sequencing | ROI | Targeted/WTS | FFPE | ROI-based bulk profiling | Not single-cell |
| Xenium | 2023 | Imaging | Subcellular | Targeted panel | FFPE/FF | In situ hybridization chains | Panel limited |
| Xenium Prime 5K | 2024 | Imaging | Subcellular | 5000 genes | FFPE/FF | Largest imaging panel | Panel vs. WTS |
| MERSCOPE | 2022 | Imaging | 100–200 nm | 140–500 genes | FFPE/FF | MERFISH technology | Panel design needed |
| CosMx | 2022 | Imaging | Subcellular | Targeted/WTP | FFPE/FF | Multiplexed RNA+protein | Panel limited |
| Open-ST | 2024 | Sequencing (open) | 0.5 µm | WTS | FF | Open-source, 3D capable | Requires expertise |
| Seq-Scope | 2021 | Sequencing (open) | 0.5–1 µm | WTS | FF | Repurposed flow cell | Limited to FF |
| Spatial V(D)J | 2023 | Sequencing (specialized) | Spot | Immune receptors | FF | Long-read B/T clone mapping | FFPE incompatible |

#### Computational Tools for Spatial Analysis

| Method | Year | Journal | Category | Key Innovation | Limitation | Input |
|---|---|---|---|---|---|---|
| BANKSY | 2024 | Nat. Genet. | Clustering | Neighbor-enriched cell typing | Computationally heavy | ST expression |
| spaGCN | 2021 | Nat. Methods | Clustering | Graph CNN integrates histology | Low scalability | ST + H&E |
| SSAM | 2021 | Nat. Commun. | Segmentation-free | KDE density maps for cell typing | Limited resolution | Imaging ST |
| FICTURE | 2024 | Nat. Methods | Segmentation-free | Scalable submicron analysis | Factorization interpretation | Imaging ST |
| Popari | 2025 | bioRxiv | Multi-sample | Probabilistic factor decomposition | Preprint | Multi-sample ST |
| Smoothie | 2025 | bioRxiv | Denoising/integration | Gaussian smoothing + co-expression networks | Preprint | ST |
| STalign | 2023 | Nat. Commun. | Registration | Diffeomorphic metric mapping | Requires morphological anchors | ST images |
| STAligner | 2023 | Nat. Comp. Sci. | Expression alignment | Preserves spatial relations | — | ST expression |
| cell2location | 2022 | Nat. Biotechnol. | Deconvolution | Bayesian hierarchical model | Reference needed | ST + scRNA |
| Tangram | 2021 | Nat. Methods | Deconvolution | Deep learning alignment | Reference needed | ST + scRNA |
| RCTD | 2021 | Nat. Biotechnol. | Deconvolution | Robust cell type decomposition | Reference needed | ST + scRNA |
| SpaTalk | 2022 | Nat. Commun. | CCC | Spatially constrained LR | Reference dependent | ST |
| COMMOT | 2023 | Nat. Methods | CCC | Optimal transport CCC | Computationally intensive | ST |
| Spacia | 2023 | Nat. Methods | CCC | Single-cell spatial CCC | — | ST single-cell |
| ST-Net | 2020 | Nat. Biomed. Eng. | Histology→expr | CNN from H&E | Small training set | H&E + ST |
| XFuse | 2022 | Nat. Biotechnol. | Histology→expr | Probabilistic super-resolution | Training required | H&E + ST |
| iSTAR | 2024 | Nat. Biotechnol. | Histology→expr | Super-resolution beyond assay | Validation needed | H&E + ST |
| ENLIGHT-DeepPT | 2024 | Nat. Cancer | Clinical AI | Treatment response from H&E | Training data bias | H&E slides |
| OmiCLIP | 2025 | Nat. Methods | Foundation model | Visual-omics foundation | Large data needs | H&E + ST |
| Virchow | 2024 | Nat. Med. | Foundation model | 100K slide pretraining | No molecular data | H&E slides |
| CHIEF | 2024 | Nature | Foundation model | Pan-cancer diagnosis/prognosis | No molecular data | H&E slides |
| MUSE | 2022 | Nat. Biotechnol. | Multi-omics | Morphology + transcriptome | FFPE challenges | Imaging + ST |
| SpatialGlue | 2024 | Nat. Methods | Multi-omics | Domain detection multi-omics | — | Multi-modal ST |
| MISO | 2025 | Nat. Methods | Multi-omics | Resolves tissue complexity | New, limited validation | Multi-modal ST |
| inferCNV | ~2019 | — | CNV inference | Repurposes scRNA for CNV | False positives | scRNA/ST |
| CalicoST | 2024 | Nat. Methods | CNV inference | Allele-specific CNV via SNP | Frozen tissue | ST |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
