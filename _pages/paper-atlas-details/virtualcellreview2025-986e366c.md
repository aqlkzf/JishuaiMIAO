---
layout: default
permalink: /paper-atlas/virtualcellreview2025-986e366c/
title: "VirtualCellReview2025"
nav: false
wide: true
description: "这是一篇综述，不提出一个统一的“Virtual Cell 算法”，也没有配套代码仓库。它把虚拟细胞视为一个跨层级研究框架：将多模态组学、生成模型、图模型和机理约束组合起来，模拟细胞在药物、基因编辑或疾病条件下的状态变化，再用计算评估、CRISPR、类器官和器官芯片逐级验证。 因此，阅读重点不应是寻找一套可照抄的网络结构，而应问三个问题：不同方法分别模拟什么；什么证据足以证明预测可靠；模型怎样从细胞层面走到药物研发和监管语境。"
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
      <span>npj Digital Medicine · 2025</span>
    </div>
    <h1>VirtualCellReview2025</h1>
    <p>AI-driven virtual cell models in preclinical research: technical pathways, validation mechanisms, and clinical translation potential</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41746-025-02198-6" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for VirtualCellReview2025">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## AI 驱动虚拟细胞综述解读：从模型目录走向可验证的证据闭环

### 先说明这篇文章是什么

这是一篇综述，不提出一个统一的“Virtual Cell 算法”，也没有配套代码仓库。它把虚拟细胞视为一个跨层级研究框架：将多模态组学、生成模型、图模型和机理约束组合起来，模拟细胞在药物、基因编辑或疾病条件下的状态变化，再用计算评估、CRISPR、类器官和器官芯片逐级验证。

因此，阅读重点不应是寻找一套可照抄的网络结构，而应问三个问题：不同方法分别模拟什么；什么证据足以证明预测可靠；模型怎样从细胞层面走到药物研发和监管语境。

### 1. 综述给“虚拟细胞”划出的范围

文章把虚拟细胞定义为模拟细胞功能状态、信号网络及其在扰动下动态变化的计算模型，并以“virtual cell”统摄 digital cell 和部分 digital twin 文献。但三者仍有尺度差异：虚拟细胞主要落在分子、单细胞和细胞群层面；数字孪生常进一步连接组织、器官和个体。

这个定义很宽，既包含纯数据驱动的单细胞生成模型，也包含 ODE/PDE、粒子模拟、细胞 Potts 模型和药代毒理平台。其好处是能组织技术生态，风险是把“预测转录响应”“重建组织空间”和“模拟器官毒性”等证据标准不同的任务放在同一标签下。

### 2. 四类技术路线不是互相替代

#### 多模态整合：先建立共同状态空间

scRNA-seq 有高基因覆盖却缺少位置，空间转录组保留组织结构但覆盖或分辨率受平台限制，蛋白组和表观组又提供不同层面的调控信息。scVI/totalVI、GLUE、MultiVI、SpatialScope 和 moscot 等方法的共同目标，是把异构模态对齐到可比较的细胞状态或时空轨迹。

这类方法通常回答“哪些观测属于同一状态”，并不天然回答“给药后会发生什么”。若整合阶段把批次、组织或技术差异误当成生物信号，后续生成和药物预测都会继承偏差。

#### 生成模型：模拟未观测状态

VAE、conditional VAE、VAE-GAN、diffusion 和 flow matching 学习状态分布或状态间变换。scGen、CPA、UNAGI、scDiffusion 和 GEARS 分别覆盖条件扰动、组合扰动、疾病轨迹或图先验。

文章同时引用一个关键反证：单细胞扰动预测中的深度学习方法尚未稳定大幅超过简单线性基线。由此可见，“能生成看似合理的表达谱”不等于“对未见细胞类型、剂量和组合扰动有可靠外推”。

#### 图神经网络：显式表示关系

GNN 把基因调控、蛋白互作、细胞邻域或空间接近编码为图，适合建模信息怎样沿网络传播。scGNN、PINNACLE、DrugCell-GNN、SpaGCN 和 GraphST 对应的节点与边含义并不相同：有的图是细胞邻域，有的是分子网络，有的是药物—靶点结构。

图结构提升可解释性只在边的来源可信时成立。错误或不完整的先验网络会把偏差固化进模型；注意力权重也不能直接等同于因果机制。

#### 物理/机理约束：限制不合理预测

PINN 和混合模型把守恒关系、动力学方程、FBA 约束或 Hodgkin–Huxley 电生理方程加入训练/模拟。VCBA 等平台把细胞内毒理过程与暴露剂量、时间联系起来。

这一路线牺牲部分灵活性以换取生物合理性，但上限取决于方程和参数是否完整。一个错误的机理先验可能比无约束模型更有迷惑性，因为输出看起来更“可解释”。

### 3. 基础模型解决的是迁移，不是自动跨尺度

GeneFormer、scFoundation 和 State 通过大规模预训练获得可迁移细胞表示或扰动预测能力；CODE-AE、scDEAL 和 CSG2A 尝试把细胞系、群体和单细胞知识迁移到患者或药物反应。

但从细胞到患者不是简单增加层数。组织微环境、细胞间通讯、ADME、剂量、器官功能和个体遗传背景都可能成为新的状态变量。细胞级 embedding 在分类任务上成功，并不能单独支持患者级疗效或安全性结论。

### 4. 文章最有价值的贡献是验证框架

文章把验证组织成由内向外的闭环：

```text
计算评估 -> 实验验证 -> 跨平台/转化评估 -> 失败反馈 -> 模型更新
```

计算层需要同时检查：重建/分布一致性、预测精度、跨数据集泛化、复杂度和不确定性。Wasserstein、KL 或 MMD 可测整体分布差异，分类指标可测任务输出，但任何单项低误差都可能漏掉关键稀有亚群或因果方向。

实验层使用 CRISPR 验证候选调控因子，用类器官测试个体化药物反应，用器官芯片或 hiPSC-CM 检查组织动力学和心脏毒性。实验不应只挑模型最有信心的成功案例，而应包含盲法、阴性对照、剂量梯度、重复实验和失败模式。

转化层关心跨实验室复现、前瞻验证、风险分级和监管用途。用于假设生成的模型可接受较低证据门槛；若要替代动物毒理或支持 IND，所需可信度、审计和外部验证必须更高。

### 5. 六幅图怎样组成综述叙事

- 图 1 将技术、验证、应用和转化挑战压缩成完整生命周期，并把减少动物实验放在闭环中央。
- 图 2 展开“多模态数据 -> 生成模型/GNN/PINN -> 谱系、轨迹、药物响应”的三条技术路线。
- 图 3 区分计算评估与实验验证，是全文最重要的证据结构图；图中标题 `Experimental Aerification` 是明显排版错误，应为 verification。
- 图 4 划分虚拟细胞与数字孪生的尺度边界，并展示药物靶点、候选化合物、作用机制和毒性预测的应用链。
- 图 5 把监管、隐私、公平、知识产权与责任分配放进同一治理环，提醒临床转化不是单纯提高 AUROC。
- 图 6 汇总术语标准化、开放科学、技术瓶颈和多尺度融合四个未来方向。

六幅图均为作者绘制的概念示意，没有原始实验数据、误差条或方法间量化比较；它们是分类与论证工具，不是效果证据。

### 6. 方法选择应由问题和验证资源决定

| 研究问题 | 更合适的起点 | 最少验证要求 |
|---|---|---|
| 批次校正、多组学共同状态 | scVI/totalVI、GLUE、MultiVI | 留出批次、保留生物差异、跨平台复现 |
| 药物/基因扰动表达预测 | conditional VAE、CPA、GEARS、diffusion | 未见扰动与未见细胞类型、线性基线、剂量梯度 |
| 空间域和细胞邻域 | SpaGCN、GraphST 等图模型 | 空间留出、组织学对照、邻域扰动敏感性 |
| 代谢/电生理/毒理动力学 | PINN、FBA 混合模型、VCBA | 参数可辨识性、守恒检查、体外时间序列 |
| 跨任务细胞表示 | foundation model | 数据泄漏审计、外部数据集、简单表示基线 |
| 患者级数字孪生 | 多尺度混合模型 | 前瞻队列、个体校准、风险分层和监管审计 |

### 7. 对临床转化主张保持分层

FDA Modernization Act 2.0 为非动物方法打开政策空间，但不等于 AI 模型可以自动替代动物试验，也不保证某个虚拟细胞输出会被监管接受。文章讨论的政策方向应理解为“允许提交多种证据”，而不是“降低有效性和安全性要求”。

隐私方面，联邦学习和差分隐私可以减少原始数据共享，但会引入性能、通信和审计权衡。公平方面，需要按人群、平台、组织和疾病亚型分别报告误差。解释性工具如 SHAP 或 integrated gradients 可以定位输入贡献，却不能单独提供生物因果解释。

### 8. 这篇综述本身的证据边界

文章是叙述性综述，没有报告系统检索式、纳入/排除标准、质量评分或元分析，也没有生成或分析新数据。表格汇总了数据库、模型和平台，但不同条目的任务、数据规模和指标不可直接横向排名。

文中部分参考文献与附近论述的匹配关系可疑，需要读者回到原始论文核验；作者还声明使用 ChatGPT-5Auto 做语言润色。AI 润色本身不否定内容，但结合术语错误和引文错配，意味着这篇综述更适合作为导航地图，而不是未经复核的事实数据库。

### 9. 给研究者的实用结论

1. 先定义预测对象和干预尺度，再选模型；“虚拟细胞”不是一个统一 benchmark。
2. 每个复杂模型都应配简单基线，尤其是扰动预测。
3. 表示学习、生成逼真度、机制正确性和临床效用是四种不同证据。
4. 计算指标必须连接到可证伪实验，且要记录失败预测。
5. 从细胞到组织/患者需要新的状态变量和验证层，不能只靠迁移学习口号。
6. SBML、CellML、开放 benchmark 和报告标准是可复用生态的基础。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## AI-Driven Virtual Cell Models in Preclinical Research — Summary

### Paper Identity

| Field | Value |
|-------|-------|
| **Title** | AI-driven virtual cell models in preclinical research: technical pathways, validation mechanisms, and clinical translation potential |
| **Authors** | Chunyu Ma, Han Zhang, Yiwei Rao, Xinyu Jiang, Boheng Liu, Zhikang Sun, Zhenyu Song, Yuan Gao, Yuhao Cui, Xinyu Liu, Zedong Li |
| **Affiliations** | Department of General Surgery, Xiangya Hospital, Central South University; Bengbu Medical University; Wenzhou Medical University |
| **Journal** | npj Digital Medicine, vol. 9 (2025) |
| **DOI** | [10.1038/s41746-025-02198-6](https://doi.org/10.1038/s41746-025-02198-6) |
| **Paper Type** | Review article |
| **Code** | None (review paper — no original method or code) |

---

### Motivation & Scope

#### Problem Statement

Preclinical drug development relies on a slow, expensive pipeline of animal experiments and in vitro assays. Meanwhile, single-cell omics and spatial transcriptomics are generating unprecedented volumes of molecular data at cellular resolution. The central challenge is: **can AI models simulate cellular responses to drugs, genetic perturbations, and disease progression with enough fidelity to partially replace traditional wet-lab experiments?**

The term "virtual cell" — a computational model that simulates functional cellular states, signaling networks, and their dynamics under diverse perturbations — sits at this convergence of biological data and AI methods. Despite growing activity, the field suffers from terminological fragmentation ("virtual cell," "digital cell," "digital twin"), scattered technical approaches, unresolved validation standards, and unresolved regulatory questions.

#### Scope of This Review

This review provides a systematic survey of AI-driven virtual cell models in preclinical research, covering:
1. **Technical pathways**: multimodal data integration, foundation models, deep generative models, GNNs, PINNs, and modeling platforms
2. **Validation mechanisms**: computational evaluation metrics and experimental verification (CRISPR, organoids, organ-on-chip)
3. **Application scenarios**: drug screening, mechanistic inference, digital twin synergy
4. **Clinical translation**: regulatory trends (FDA Modernization Act 2.0), data privacy, IP, algorithmic fairness
5. **Future directions**: terminology standardization, multiscale integration, open science initiatives

#### What Distinguishes This Review from Prior Work

The review's central organizing principle is an **evidence-progression framework**: from model construction → evaluation/validation → use cases → translational barriers → forward outlook. This differentiates it from prior reviews that focus on individual technical components (e.g., foundation models alone, or perturbation prediction alone). Key prior reviews for comparison:
- Bunne et al. (*Cell*, 2024): priorities and opportunities for building virtual cells — focuses on the vision and open problems
- Johnson et al. (*Biophys. J.*, 2023): next-generation virtual cells — emphasizes biophysical modeling approaches
- Gangwal & Lavecchia (*Drug Discov. Today*, 2025): digital twins and organ-on-chip — focuses on the regulatory and ethical side

This review attempts to unify all three perspectives (technical, validation, regulatory) in a single narrative arc.

---

### Method Overview

#### Four Technical Pillars

The review organizes virtual cell construction around four complementary AI approaches:

1. **Multimodal Data Integration**: Methods that bridge scRNA-seq (high resolution, no spatial context) with spatial transcriptomics (spatial structure, lower gene coverage). Examples: SpatialScope (deep generative projection), scVI/totalVI (VAE-based integration), GLUE (graph-linked embedding with regulatory priors), moscot (optimal transport for spatiotemporal trajectories). Foundation for all downstream modeling.

2. **Deep Generative Models**: VAEs, VAE-GANs, diffusion models, and flow matching for generating synthetic expression profiles under hypothetical perturbations. Key examples: scGen (conditional VAE for perturbation response, *Nat. Methods* 2019), CPA (compositional perturbation autoencoder for combinatorial effects), UNAGI (VAE-GAN for IPF dynamics), scDiffusion (diffusion + foundation model for high-fidelity transcriptome generation), GEARS (knowledge-graph-guided, ~40% improvement for multi-gene perturbation prediction, *Nat. Biotechnol.* 2024). **Critical caveat acknowledged**: Ahlmann-Eltze et al. (*Nat. Methods*, 2025) show that current DL perturbation methods do not substantially outperform simple linear baselines.

3. **Graph Neural Networks**: scGNN for cell-type identification via graph convolution, PINNACLE for integrating PPI networks with scRNA-seq, DrugCell-GNN for drug response prediction, SpaGCN/GraphST for spatial domain identification. Natural representation for cell-cell interactions and biological networks.

4. **Physics-Informed Neural Networks (PINNs)**: Embedding known biophysical laws (ODE/PDE constraints) into neural network training. VCBA platform for drug metabolism/toxicology simulation, FBA+NN hybrids for metabolic pathway prediction, Hodgkin-Huxley embedding for cardiac electrophysiology. Improves interpretability but faces challenges with incomplete biological knowledge and training complexity.

#### Foundation Models & Cross-Scale Transfer

A distinct theme is the role of large-scale pretrained models: GeneFormer (*Nature*, 2023), scFoundation (*Nat. Methods*, 2024), and State (Arc Institute) — trained on >10^8 cells. These models learn transferable representations that can be fine-tuned for downstream tasks. Cross-scale transfer from gene/cell level to patient level is achieved via CODE-AE (cell line → patient tumor) and scDEAL (population + single-cell → individualized drug sensitivity).

#### Modeling Platforms Landscape

The review catalogs **15 cell-scale modeling platforms** spanning three scales:
- **Molecular/intracellular**: VCell, COPASI, BioNetGen, PySB, CellNOpt, VCBA
- **Multicellular/tissue**: PhysiCell, CompuCell3D, Morpheus
- **Subcellular particle-based**: Smoldyn, MCell/CellBlender, ReaDDy
- **Organ-system**: Chaste, OpenCOR/CellML, OpenSim/Physiome
- **AI-driven**: DeepCell, CellPose, NVIDIA Modulus

#### Validation Framework

The review proposes a **tri-loop closed-loop validation architecture**:
- **Computational inner loop**: Data partitioning, batch harmonization, distributional concordance testing, uncertainty quantification (Monte Carlo dropout, model ensembling). Key metrics: Wasserstein distance, KL divergence, MMD
- **Experimental middle loop**: CRISPR-based gene function verification, organoid drug response testing, organ-on-chip validation. Concrete examples: hiPSC-CM cardiotoxicity prediction for doxorubicin/trastuzumab; VCBA hepatocyte/mitochondrial toxicity simulation
- **Translational outer loop**: Cross-platform replication, prospective validation, safety review, failure-mode analysis

---

### Evaluation

#### Computational Evaluation Dimensions
1. **Reconstruction error and distribution consistency**: t-SNE/UMAP comparison, distributional distances
2. **Prediction accuracy and stability**: Cross-validation, extrapolation to unseen scenarios
3. **Model complexity and generalization**: Parameter count, compute time, cross-dataset performance
4. **Uncertainty quantification**: Monte Carlo dropout for confidence intervals, ensemble consistency

#### Experimental Validation Examples
- **hiPSC-CM platform** (Sang et al., *Pharm. Res.*, 2024): Predicted cardiotoxicity for doxorubicin and trastuzumab matching clinical observations
- **VCBA** (Worth et al., *Toxicol. In Vitro*, 2017): Simulated mitochondrial membrane potential changes matching in vitro data for FCCP, caffeine, amiodarone
- **Intestinal organoids** (Harter et al., *Nat. Biomed. Eng.*, 2024): EpCAM-targeted bispecific antibody toxicity in healthy organoids aligned with clinical reports

#### Benchmarking Initiatives
- Virtual Cell Challenge (2025): Perturbation-response prediction on unseen cell types (Roohani et al., *Cell*, 2025)
- Therapeutic Data Commons (PyTDC): Unified evaluation framework for drug discovery benchmarks
- Open Problems in Single-Cell Analysis: Community benchmark datasets and metrics

---

### Clinical Translation Landscape

#### Regulatory Progress
- **FDA Modernization Act 2.0** (2022): Removes mandatory animal testing for IND submissions; permits AI/ML models, organoids, organ-on-chip as alternatives
- **FDA AI Guidance** (2025): First draft guidance proposing risk-based credibility assessment for AI models in drug development
- **EU REACH/ECHA**: Incorporating computational modeling and bioinformatics into toxicology frameworks

#### Key Challenges
1. **Regulatory ambiguity**: Case-by-case review with no unified standards for predictive accuracy thresholds
2. **Data privacy**: PIPL, HIPAA, GDPR compliance; technical solutions include differential privacy and federated learning
3. **IP & liability**: No precedent for AI model output ownership; ambiguous liability allocation between data providers, model developers, and end users
4. **Algorithmic fairness**: Population bias in training data (predominantly Western populations) leading to reduced accuracy for underrepresented groups
5. **Interpretability**: Black-box nature of deep learning undermines clinical and regulatory trust; XAI approaches (SHAP, integrated gradients) as partial solutions
6. **Cross-scale coupling**: Bridging single-cell models to tissue/organ level remains technically challenging

---

### Strengths

1. **Comprehensive scope**: Covers technical methods, validation, applications, regulation, and future directions in a single coherent narrative
2. **Honest about limitations**: Directly acknowledges that DL perturbation methods don't clearly outperform linear baselines
3. **Practical platform catalog**: Table 3 with 15 platforms, their URLs, strengths, and limitations is immediately useful
4. **Tri-loop validation framework**: Novel organizational contribution for thinking about model validation stages
5. **Regulatory awareness**: Good coverage of FDA Modernization Act 2.0 and emerging policy landscape

### Weaknesses

1. **Reference quality concerns**: Multiple citations appear to be errors — the cited paper is clearly unrelated to the context in which it appears (e.g., refs for "scAdapt," "conditional normalization," several platform references). This is a significant quality issue for a review paper
2. **AI-assisted writing declared**: Authors used "ChatGPT-5Auto for language polishing" — likely contributing to the citation errors and occasionally awkward phrasing
3. **Breadth over depth**: No individual method is analyzed in sufficient depth for a reader to understand its actual mechanism; the review reads more as a literature catalog
4. **Limited critical analysis**: Beyond the linear baseline caveat, the review does not systematically evaluate which methods actually work vs. which are aspirational
5. **No original analysis or benchmarks**: Purely narrative review with no computational experiments, no head-to-head comparisons, no original figures with data
6. **Overuse of "driven by" framing**: Repetitive sentence structures throughout
7. **Some factual concerns**: E.g., incorrectly labels GDPR as "(generative adversarial network)" in Section 5.3 (should be "General Data Protection Regulation"); Figure 3 Panel B misspells "Verification" as "Aerification"

---

### Reproducibility Assessment

**Rating: N/A** — Review article, no original method or experiments to reproduce.

For the reviewed methods, the review provides GitHub URLs for 12 key tools (Table 2), platform URLs for all 15 modeling platforms (Table 3), and database references (Table 1). This enables readers to access the underlying tools, though no reproduction protocol is provided.

---

### Key Takeaways for the Field

1. The virtual cell concept is a useful organizing framework for thinking about how AI + multimodal omics can simulate cellular behavior
2. Foundation models (GeneFormer, scFoundation, State) are establishing the infrastructure for cross-task transfer learning at the cellular level
3. **The linear baseline problem is real**: Until DL methods convincingly outperform simple baselines on perturbation prediction, claims of transformative impact should be treated cautiously
4. Validation remains the biggest gap — very few virtual cell predictions have been experimentally confirmed via targeted interventions
5. The regulatory landscape is opening up (FDA Modernization Act 2.0), but standardized evaluation frameworks are still missing
6. Platform interoperability and terminology standardization are prerequisites for field maturation

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
