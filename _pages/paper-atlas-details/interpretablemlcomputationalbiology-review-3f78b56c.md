---
layout: default
permalink: /paper-atlas/interpretablemlcomputationalbiology-review-3f78b56c/
title: "InterpretableMLComputationalBiology_review"
nav: false
description: "IML 的可信度不来自方法名称，而来自完整证据链：解释器是否忠实、结果是否稳定、数值是否经过合适的生物后处理、全体结果是否透明，以及候选机制是否经外部或实验验证。"
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
      <span>Machine Learning Algorithm</span>
      <span>Nature Methods · 2024</span>
    </div>
    <h1>InterpretableMLComputationalBiology_review</h1>
    <p>Applying interpretable machine learning in computational biology--pitfalls, recommendations and opportunities for new developments</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-024-02359-7" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for InterpretableMLComputationalBiology_review">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 计算生物学中的可解释机器学习：从“模型用了什么”到“生物学意味着什么”

### 这篇 Perspective 的核心问题

机器学习模型可以准确预测基因表达、表型、结构或疾病，但研究者往往还想知道：模型为什么这样预测，它是否捕获了真实生物机制？这篇综述的核心提醒是，**解释模型不等于解释生物学**。可解释机器学习（IML）首先说明模型输出依赖了哪些输入或内部组件；要把这种信号提升为生物发现，还需要后处理、可靠性评价、领域知识和实验验证。

文章不是提出一个新算法，而是建立使用 IML 的证据框架：先区分 post hoc 与 by-design 两条路线，再用 faithfulness 和 stability 评价解释，最后集中讨论三类常见陷阱及 LLM/生物基础模型时代的新问题。

### 两条解释路线

#### Post hoc：模型训练完后再问“为什么”

post hoc 方法通常不改变预测模型。给定训练好的函数 $f(x)$，解释器为输入特征产生重要性分数 $a_i$。在 DNA 序列中，$i$ 可以是一个碱基；在转录组中可以是一个基因；在细胞图像中可以是一个像素或区域。

文章把常见方法分为两类：

- 梯度类方法，例如 DeepLIFT、Integrated Gradients 和 Grad-CAM，利用输出对输入或中间表示的敏感度。
- 扰动类方法，例如 in silico mutagenesis、SHAP/DeepExplainer、LIME 和 Fourier-based attribution，通过改变输入观察预测变化。

Integrated Gradients 的典型形式可写为

$$
\operatorname{IG}_i(x)= (x_i-x'_i)\int_0^1
\frac{\partial f(x'+\alpha(x-x'))}{\partial x_i}\,d\alpha,
$$

其中 $x'$ 是 baseline。这个公式同时暴露了重要边界：解释依赖 baseline、数值近似和模型局部行为。不同 baseline 或超参数可给出不同排序，因此不能只报告一张漂亮的 attribution 图。

SHAP 的思想是按特征加入不同子集时的边际贡献求加权平均，但在高维、强相关生物数据中，背景分布和“缺失特征”如何定义会改变解释。基因、motif 和表观特征常高度相关，分数不一定能唯一归因于真正因果因素。

#### By-design：把可解释结构写进模型

传统 by-design 模型包括线性/逻辑回归、决策树、规则和 generalized additive model。计算生物学还发展了生物知识约束网络：DCell 把细胞子系统层级映射进网络，P-NET 利用通路组织，KPNN 使用基因调控或信号网络。隐藏节点因此具有基因、通路或细胞过程的名字。

这种结构使内部组件更容易对应生物概念，但“节点有生物名字”不等于节点权重忠实反映机制。架构依赖现有知识库；不完整或有偏的通路图会限制模型能学到的关系，自定义重要性分数仍需评价。P-NET、PAUSE 等例子也说明 by-design 与 post hoc 可以组合，而不是互斥。

文章把 attention-based 模型也放在 by-design 讨论中。Transformer 的 attention 权重能显示 token 间信息分配，Enformer、Geneformer 等工作据此探索增强子或调控层级。但 attention 是训练机制，不自动等于模型推理的因果解释；不同层和 head 可能学到不同关系，平均化、rollout 或 flow 会引入新的汇总选择。

### 两个评价轴：faithfulness 与 stability

#### Faithfulness：解释是否忠实于被解释对象

faithfulness（或 fidelity）问：解释器标出的特征，是否真的对应模型使用的机制或已知 ground truth？可以通过合成数据、已知 motif、特征删除/插入、模型行为变化或实验机制来检查。

必须区分两个目标：忠实于**模型**，与符合**真实生物机制**。模型可能依赖批次、测序深度或采集伪影；一个非常忠实的解释会准确揭示这种错误依赖，却不因此成为生物解释。相反，解释与已知通路一致，也可能只是相关性或先验偏好，而非模型真实决策路径。

文章指出，没有一种 IML 方法在所有 faithfulness benchmark 上普遍最好。合成数据有已知真值，却难以覆盖真实生物复杂度；真实数据更相关，但机制通常不完整。这是评价中的结构性困难，不应被一个分数掩盖。

#### Stability：解释是否经得起小变化

stability 问：相似输入、不同随机种子、数据折、baseline 或超参数下，解释是否一致。可以把同一特征多次得到的 attribution 视作随机变量，报告均值、方差、排序相关或集合重叠。

稳定不是正确。一个始终依赖伪影的模型可以给出高度稳定但错误的解释；一个真实存在异质性的系统也可能合理地产生不稳定解释。因此 stability 应与 faithfulness、预测性能和生物验证并读，而不是作为替代指标。

### 三个陷阱，以及它们为什么常见

#### 陷阱 1：只使用一个解释方法

不同方法的假设、局部性、参考输入和数值过程不同，同一模型可能产生不同 top genes 或 motifs。只选一个方法，研究结论可能只是解释器的偏好。

更可靠的做法是使用多类方法和多个超参数，公开一致与冲突之处。Enformer 同时比较 attention、input gradients 与扰动分数就是这种思路。多方法一致也不是证明，但能筛出对方法选择较稳健的候选；若结论冲突，则需要 ground truth、专家或实验来裁决，而不是挑选最符合预期的一种。

#### 陷阱 2：把原始 IML 输出直接叫作生物机制

碱基级 attribution 不是 motif，像素热图不是形态学概念，基因排序不是通路机制。必须进行与数据类型匹配的后处理：序列任务可用 TF-MoDISco 把碱基分数聚合成 motif，再做已知 motif 匹配或富集；转录组可对稳定的基因集合做 GO/通路分析；图像要把像素区域转为专家能检查的形态特征或 counterfactual。

后处理本身也包含阈值、聚类、数据库和背景集选择，可能制造看似清晰的故事。完整流程应同时记录原始分数、后处理参数、未匹配结果与负结果。

#### 陷阱 3：只展示成功案例

从大量细胞、序列或特征中挑几个符合已知机制的图，无法说明解释整体可靠。BPNet 的例子强调先完整报告发现的 motif，再选代表性案例深入讨论。更一般地，应说明分母：总共解释了多少样本、发现多少模式、多少匹配已知机制、多少不匹配、结论在多少折或队列中复现。

这种选择性报告与多重检验问题类似。若只看“命中”，读者无法判断它是系统信号还是大规模搜索后的偶然故事。

### 一个可执行的生物解释工作流

1. 先定义问题：要解释单样本预测、全局模型行为，还是寻找可实验机制。
2. 明确解释对象与单位：碱基、k-mer、基因、细胞、图像区域、通路或模态。
3. 选择至少两类互补方法，并预先记录 baseline、背景集、层/head、随机种子和阈值。
4. 在全数据范围计算解释，不先挑“好看”样本。
5. 做数据类型特异的后处理，把数值 attribution 转成 motif、通路、形态或候选机制。
6. 分别评估 faithfulness 与 stability，并报告预测性能；三者回答不同问题。
7. 与已知机制、外部队列、扰动数据或专家注释比较，保留冲突和未匹配结果。
8. 将最稳健的候选转成可证伪实验，例如 CRISPR、MPRA、Perturb-seq 或成像验证。

这条流程的关键是把 IML 放在“提出和筛选假说”的位置。只有后续干预证据才能更接近因果生物结论。

### 计算生物学基础模型带来的新难题

文章最后把 LLM interpretability 的研究方向映射到生物模型。首先是 tokenization：单碱基、固定 k-mer、BPE 片段、基因 token、图像 patch 和细胞 latent token 具有不同生物分辨率。如果 token 本身没有稳定生物含义，token attribution 也难以解释。

其次是 transformer-specific IML。attention 可用于诊断，但需要与扰动或 mechanistic interpretability 结合。所谓 circuits、learned programs 或内部特征是否能映射到 motif、通路和细胞状态，仍是开放问题。

第三是 multimodal explanation。RNA、ATAC、蛋白和图像常相关；一个模型同时给多个模态高分，不代表它发现了各模态独立因果贡献。应区分模态内重要性、模态消融后的性能变化，以及跨模态交互。

最后是 visualization。生物研究者需要看到 motif、基因组区段、细胞群、通路或空间区域，而非张量热图；但可视化必须连接定量评价，不能只追求直观。

### 怎样读这篇综述的证据边界

这是 Perspective，而不是系统综述或新 benchmark。它用代表性文献建立问题框架，没有报告系统检索、纳排标准、风险偏倚评价或 meta-analysis，因此不应把引用频率理解为方法排名。`SUPP_MD` 和直接代码证据均为 Not found。其强项是概念区分与实践建议，而不是证明某一种 IML 工具在所有生物任务中最好。

### 最重要的一句话

IML 的可信度不来自方法名称，而来自完整证据链：**解释器是否忠实、结果是否稳定、数值是否经过合适的生物后处理、全体结果是否透明，以及候选机制是否经外部或实验验证。**

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Applying Interpretable Machine Learning in Computational Biology

### Review Scope

This Nature Methods Perspective reviews how interpretable machine learning (IML) is being used in computational biology, with emphasis on genomics, transcriptomics, metagenomics, biomedical imaging, multimodal models and transformer/foundation models. It is not a catalog of every IML method; it is a practice-oriented review of the main explanation workflows, evaluation criteria, common misuse patterns and open opportunities.

The core audience is computational biologists who use machine-learning predictions to make biological claims, plus IML researchers looking for biology-specific interpretability problems. The article covers roughly 25 named methods, model classes, post-processing tools and evaluation practices, while citing 78 references across machine learning, genomics, single-cell analysis, imaging and foundation models.

### Field Landscape

The field has moved from relatively interpretable statistical models toward high-capacity neural networks for sequence, single-cell, imaging and multimodal biological data. This shift produced strong predictive performance but weakened the direct link between model behavior and biological mechanism. IML entered computational biology as a way to explain why a model predicts gene expression, identifies disease state, classifies an image or prioritizes sequence variants.

The review frames the current moment as a transition point. Classical explanation methods such as DeepLIFT, Integrated Gradients, SHAP, LIME, Grad-CAM and in silico mutagenesis are now routinely applied to biological models, but their outputs are often treated as biological evidence without enough evaluation. At the same time, transformer and large-language-model style architectures are entering molecular and cellular modeling, raising new interpretability questions about tokenization, attention, mechanistic circuits, multimodal fusion and visualization.

### Method Taxonomy

The paper distinguishes two main IML workflows:

| Workflow | Core idea | Typical outputs | Biological use |
|---|---|---|---|
| Post hoc explanation | Train a general model first, then apply an explanation method. | Feature-importance scores for nucleotides, genes, pixels, variants, regions or modalities. | Motif discovery, biomarker ranking, salient image-region detection, perturbation hypotheses. |
| By-design explanation | Build interpretability into the model architecture. | Inspectable coefficients, paths, hidden biological nodes, pathway modules or attention matrices. | Biologically informed networks, pathway-aware models, attention-based sequence/foundation models. |

The paper also emphasizes two evaluation concepts:

| Evaluation concept | Question answered | Typical evidence |
|---|---|---|
| Faithfulness | Does the explanation reflect the true mechanism of the model or a known biological mechanism? | Synthetic ground truth, known TF motifs, driver-gene enrichment, expert annotations, perturbation or lab validation. |
| Stability | Are explanations consistent for similar inputs or repeated workflows? | Error bars, random-seed variation, hyperparameter sweeps, training-subset repeats, cross-dataset replication. |

The practical taxonomy is completed by three pitfalls: relying on one explanation method, failing to translate raw IML output into biology, and presenting cherry-picked positive examples rather than full quantitative evidence.

### Key Findings

The most important conclusion is that IML output is not automatically biological interpretation. Raw attribution values, attention maps or saliency pixels need domain-specific post-processing and validation. In sequence tasks, this may mean motif discovery or enrichment analysis. In gene-expression tasks, it may mean pathway or Gene Ontology enrichment. In imaging, it may require mapping salient pixels or latent directions to human-interpretable morphology.

The second major conclusion is that method disagreement is expected rather than exceptional. Different explanation methods, baselines, hyperparameters and training runs can assign importance to different features. The review therefore recommends comparing multiple IML methods and evaluating faithfulness when conclusions conflict.

The third conclusion is that explanation evaluation should be systematic. A small set of examples that agree with known biology is not enough. More convincing studies quantify agreement across the whole dataset, report nonconforming signals, test stability and use independent validation where possible.

Finally, the paper argues that biology-specific IML is underdeveloped for foundation-model-era problems. Attention weights alone are not a mature explanation strategy for biological transformers, and current tools do not fully address tokenization, multimodal attribution, mechanistic interpretability or visualization for molecular and cellular data.

### Method Comparison Table

Inclusion rule: the table covers the major named IML methods, model examples, post-processing tools and evaluation practices that the review uses to build its taxonomy and recommendations.

| Method | Year | Journal | Category | Key Innovation | Limitations | Data Types |
|---|---:|---|---|---|---|---|
| DeepLIFT | 2017 | ICML | Gradient/reference attribution | Scores features by propagating activation differences from a reference. | Baseline/reference sensitivity; may disagree with other methods. | Sequence, gene expression, tabular data |
| Integrated Gradients | 2017 | ICML | Gradient attribution | Integrates gradients from a baseline to the input. | Baseline choice matters; repeated runs/hyperparameters can vary. | Sequence, tabular, images |
| Grad-CAM / Guided Grad-CAM | 2017 | ICCV | Image saliency | Localizes discriminative image regions using class activation maps. | Pixel heatmaps need expert/domain translation. | Biomedical imaging |
| In silico mutagenesis / fastISM | 2022 | Bioinformatics | Perturbation attribution | Measures prediction changes after sequence perturbations. | Computational cost and perturbation realism can be limiting. | DNA/RNA/protein sequences |
| SHAP / DeepExplainer | 2017 | NeurIPS | Game-theoretic attribution | Shapley-style contribution scores for model predictions. | Can be unstable and assumption-dependent. | Tabular, sequence, single-cell, multimodal |
| LIME | 2016 | KDD | Local surrogate explanation | Fits local interpretable approximations around a prediction. | Local sampling assumptions can affect stability. | General ML inputs |
| Fourier attribution priors | 2020 | NeurIPS | Attribution regularization | Encourages smoother, more stable genomic attributions. | Specific to settings where such priors are appropriate. | Genomics sequence models |
| Linear/logistic regression | Classical | General statistics | By-design interpretable | Coefficients directly expose feature associations. | Limited expressiveness and interaction modeling. | Tabular biological/clinical data |
| Decision trees/rules | Classical | Machine learning | By-design interpretable | Prediction path and splits are inspectable. | Can be unstable or low-performing at high dimension. | Tabular data |
| Generalized additive models | 1987 | JASA | By-design interpretable | Additive feature-response functions improve interpretability. | Interactions require explicit modeling. | Tabular data |
| DCell | 2018 | Nature Methods | Biologically informed neural network | Encodes Gene Ontology hierarchy in network architecture. | Architecture design is application-specific; hidden-node meaning still needs validation. | Genotype-phenotype/cell systems |
| P-NET | 2021 | Nature | Biologically informed neural network | Incorporates pathway organization for prostate cancer modeling. | Pathway priors can constrain or bias interpretation. | Cancer genomics |
| KPNN | 2020 | Genome Biology | Biologically informed neural network | Uses biological networks to prime single-cell model connectivity. | Robustness and importance scores require simulation/evaluation. | Single-cell sequencing |
| PAUSE | 2023 | Genome Biology | Hybrid by-design/post hoc | Explains biologically constrained autoencoders with game-theoretic attribution. | Depends on the quality of biological constraints and attribution assumptions. | Gene expression |
| Attention/self-attention | 2017 | NeurIPS | Transformer mechanism | Learns pairwise/token weighting inside sequence models. | Attention as explanation is debated; heads/layers are hard to summarize. | Sequence, gene expression, multimodal data |
| Enformer | 2021 | Nature Methods | Genomics transformer/CNN model | Uses sequence models for gene-expression prediction and compares attention, gradients and perturbations. | Attention validity remains debated; explanations need motif/element interpretation. | DNA sequence and gene expression |
| Geneformer | 2023 | Nature | Single-cell foundation model | Inspects attention layers for gene-regulatory hierarchy. | Attention-based interpretation may not faithfully explain model reasoning. | Single-cell transcriptomics |
| TF-MoDISco | 2018 | arXiv | Sequence post-processing | Converts nucleotide-level importance scores into motif patterns. | Motif discovery still needs comparison with known motifs and full reporting. | Regulatory sequence models |
| GO enrichment | Established | Bioinformatics practice | Gene-list post-processing | Maps important genes to biological functions. | Sensitive to gene ranking, background set and database coverage. | Gene expression, single-cell |
| IDMIL | 2020 | Bioinformatics | Metagenomic interpretability | Links high-attention fragments to species with local alignment search. | Requires downstream biological interpretation of aligned fragments. | Metagenomics |
| BERTology | 2021 biology example | ICLR | Transformer analysis | Probes attention heads/layers for learned biological sequence signals. | Head-level signals may not equal causal reasoning. | Protein/DNA language models |
| Attention rollout/flow | 2020 | ACL | Transformer post-processing | Aggregates attention across layers to summarize token influence. | Still inherits attention-faithfulness concerns. | Transformer models |
| BPNet | 2021 | Nature Genetics | Genomics model and evaluation workflow | Reports genome-wide motifs from attribution scores and compares with known TF motifs. | Requires careful motif filtering and prior-knowledge comparison. | TF-binding sequence data |
| CITRUS | 2022 | Nucleic Acids Research | Attention-based cancer genomics model | Tests enrichment of high-attention genes for cancer drivers. | Enrichment does not prove causal model reasoning. | Cancer genomics |
| IAIA-BL | 2021 | Nature Machine Intelligence | Interpretable imaging workflow | Uses activation precision against expert annotations. | Depends on expert annotation quality and metric definition. | Medical imaging |
| UnitedNet | 2023 | Nature Communications | Multimodal single-cell model | Evaluates SHAP robustness across hyperparameters and training subsets. | SHAP-based conclusions still require biological validation. | Multimodal single-cell data |
| C.Origami | 2023 | Nature Biotechnology | Multimodal transformer | Compares attention, perturbation and gradient-based explanations with stability checks. | Multimodal attribution remains hard when modalities are correlated. | DNA sequence, epigenomic features, 3D genome |
| Mechanistic interpretability/circuits | 2023 | NeurIPS | LLM-specific interpretability | Attempts to map transformer internals to human-readable circuits or programs. | Early-stage and mostly tested on simpler functions than biology. | Transformer/foundation models |
| DNABERT-Viz | 2023 | Cell Systems | Visualization | Visualizes attention over genomic regions and motifs. | Visualization helps inspection but does not guarantee faithfulness. | DNA sequence language models |

### Open Problems

1. Faithfulness without clean ground truth. Biological mechanisms are rarely known completely, and synthetic benchmarks may miss the complexity of real systems.
2. Stable explanations across seeds, baselines, hyperparameters and cohorts. Explanation uncertainty needs to be reported as routinely as predictive performance.
3. Domain-specific post-processing. Raw nucleotide, gene, pixel and attention scores require different translation layers before they can support biological claims.
4. Multimodal explanation. Models increasingly combine sequence, epigenomic, imaging and single-cell modalities, but most interpretability tools remain unimodal.
5. Interpreting biological foundation models. Tokenization, attention, mechanistic circuits and prompting-based explanations need biology-specific evaluation.
6. Lab-in-the-loop validation. IML is most useful when it generates testable hypotheses, but workflows for experimental validation remain under-standardized.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
