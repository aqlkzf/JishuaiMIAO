---
layout: default
permalink: /paper-atlas/semanticlens-d736fc4d/
title: "SemanticLens"
nav: false
wide: true
description: "SemanticLens 把一个神经网络内部的每个神经元或特征方向，翻译成基础模型语义空间中的向量：先找出最能激活该组件的样本，再用 CLIP 一类模型编码这些样本。这样，研究者便能像搜索向量数据库一样搜索、标注和比较网络内部知识，并结合归因分数判断这些知识是否真正参与了预测。"
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
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>SemanticLens</h1>
    <p>Mechanistic understanding and validation of large AI models with SemanticLens</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-025-01084-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SemanticLens">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/jim-berend/semanticlens" target="_blank" rel="noopener noreferrer" aria-label="Open code for SemanticLens">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SemanticLens 方法详解

### 一句话理解

SemanticLens 把一个神经网络内部的每个神经元或特征方向，翻译成基础模型语义空间中的向量：先找出最能激活该组件的样本，再用 CLIP 一类模型编码这些样本。这样，研究者便能像搜索向量数据库一样搜索、标注和比较网络内部知识，并结合归因分数判断这些知识是否真正参与了预测。

### 它要解决什么问题

高精度不等于可靠。模型可能因为水印、肤色、背景植物、尺子或创可贴等偶然相关特征做出正确预测，却没有学到任务真正需要的规律。传统方法各自只看到局部：

- 输入归因解释某一次预测，却不直接说明某个内部组件长期代表什么；
- 探针通常只能检验研究者预先想到的概念；
- 激活可视化需要人工逐个查看神经元，无法扩展到大型模型；
- 只知道组件“检测了什么”还不够，还要知道它是否影响预测、来自哪些训练样本。

SemanticLens 的目标是把“数据 -> 内部组件 -> 预测”连成一条可审计的证据链，并让这条链可以在数千乃至更多组件上自动运行（`paper.md:22-44`）。

### 核心思想

设待分析模型为 ${\mathcal M}$，数据集为 ${\mathcal D}$，基础模型为 ${\mathcal F}$。SemanticLens 不直接解释难以理解的隐藏激活，而是为每个组件 $k$ 构造一组“概念样本” ${\mathcal E}_k$，再把这些样本映射到基础模型的语义空间 ${\mathcal S}$。

```text
待分析模型 M + 数据集 D
        |
        v
找出每个组件最强响应的 top-m 样本
        |
        v
用组件归因图裁剪真正相关的图像区域
        |
        v
基础模型 F 编码每个概念样本
        |
        v
对样本向量求平均，得到组件语义向量 vartheta_k
        |
        +----------------+-------------------+
        v                v                   v
   文本/图像搜索      模型间比较         可解释性度量
        |                                    |
        +----------------+-------------------+
                         v
            结合预测相关性 R 做有效/伪相关审计
                         |
                         v
              回溯训练数据，剪枝或重新训练
```

### 步骤 1：用概念样本描述组件

对第 $\ell$ 层的组件 $k$，论文选择使该组件响应最大的 $m$ 个样本，并按组件归因图裁剪：

$$
{\mathcal E}_{k,\ell}=\left\{\operatorname{crop}({\bf x}):{\bf x}\in\operatorname{top}_m({\mathcal M}_k^\ell,{\mathcal D})\right\}.
$$

裁剪很重要。若神经元实际响应的是鸟的眼睛，而整张图还包含树枝和天空，直接编码整图会把背景混入语义向量。论文对低于最高归因值 1% 的区域进行裁剪；对当时缺少组件级归因的 ViT，则使用上采样空间图（`paper.md:298-312`）。

代码中的 `ActivationComponentVisualizer` 会注册层钩子、扫描数据集、维护每个组件的 top 激活样本编号（`activation_based.py:309-358`）。但默认路径随后编码的是基础模型数据集中的原始样本；归因裁剪位于另一套 relevance 工具中，因此这里与论文 Eq. 1 是部分匹配，而不是完全匹配。

### 步骤 2：构造组件的语义向量

每个概念样本经基础模型编码后求平均：

$$
\boldsymbol{\vartheta}_k
=\mathbb E_{x\sim {\mathcal E}_k}[{\mathcal F}(x)]
\approx\frac{1}{|{\mathcal E}_k|}\sum_&#123;&#123;\bf x}\in {\mathcal E}_k}{\mathcal F}({\bf x})
\in {\mathcal S}\subseteq\mathbb R^d.
$$

平均相当于平滑：多个样本共同出现的语义被保留，偶然背景被削弱。论文在 ImageNet 实验中发现 30 个概念样本已使向量基本收敛（`paper.md:315-329`）。所有组件向量组成

$$
{\mathcal V}_{\mathcal M}=\{\boldsymbol{\vartheta}_1,\ldots,\boldsymbol{\vartheta}_K\},
$$

即模型内部知识的可搜索数据库。

公共代码会一次性编码视觉数据集，再用 top 样本编号为每层组装形状为“组件数 x 样本数 x 嵌入维数”的张量（`activation_based.py:360-433`）。`Lens` 支持把结果缓存为 `safetensors`；平均操作在 README quickstart 中由调用者执行，而不是在 `compute_concept_db()` 内自动执行。

### 步骤 3：搜索、标注和比较

语义空间中的基本运算是余弦相似度：

$$
s_{\cos}({\bf x},{\bf y})=
\frac{\langle{\bf x},{\bf y}\rangle}{\|{\bf x}\|_2\|{\bf y}\|_2}.
$$

查询概念可以来自文本，也可以来自图像。文本查询还可使用多个提示模板，并减去空模板向量，减少句式本身造成的偏差。论文的检索规则为：

$$
\boldsymbol{\vartheta}^{*}=\arg\max_{\boldsymbol{\vartheta}\in {\mathcal V}_{\mathcal M}}
\left[s(\boldsymbol{\vartheta}_{\rm probe},\boldsymbol{\vartheta})-
s(\boldsymbol{\vartheta}_{<>},\boldsymbol{\vartheta})\right].
$$

公共代码准确实现了文本/图像编码、空模板相减和余弦打分（`lens.py:59-214`）。但“超过阈值才赋标签”和论文定义的模型集合比较没有独立公开 API，需要调用者在分数之上实现。

### 步骤 4：区分“检测到”与“真正使用”

一个神经元能检测某个概念，不代表该概念参与了当前预测。论文因此使用 LRP/CRP 类反向归因，为内部组件计算相关性 ${\mathcal R}$。如果多个组件有同一标签，可以聚合它们的相关性；也可以把中间组件作为归因目标，构造跨层概念流图（`paper.md:374-383`）。

这是 SemanticLens 区别于纯粹概念搜索的关键：

- 语义向量回答“组件像什么”；
- 相关性回答“这个组件对哪次预测重要”；
- top 激活样本回答“它从哪些数据学到这种模式”。

代码包含 CRP/LRP relevance visualizer，但源码明确注明该实现“正在重度开发且当前损坏”（`relevance_based.py:27`）。因此公共仓库只部分覆盖论文中的完整归因图流程。

### 步骤 5：有效概念与伪相关概念审计

用户先定义有效概念集 ${\mathcal V}_{\rm valid}$ 和伪相关概念集 ${\mathcal V}_{\rm spur}$。对组件 $k$，分别计算它与两类概念的最大去背景相似度：

$$
a_k^{\rm valid}=\max_{\boldsymbol{\vartheta}_{\rm v}\in {\mathcal V}_{\rm valid}}
\left[s(\boldsymbol{\vartheta}_{\rm v},\boldsymbol{\vartheta}_k)-s(\boldsymbol{\vartheta}_{<>},\boldsymbol{\vartheta}_k)\right],
$$

$$
a_k^{\rm spur}=\max_{\boldsymbol{\vartheta}_{\rm s}\in {\mathcal V}_{\rm spur}}
\left[s(\boldsymbol{\vartheta}_{\rm s},\boldsymbol{\vartheta}_k)-s(\boldsymbol{\vartheta}_{<>},\boldsymbol{\vartheta}_k)\right].
$$

理想的相关组件满足 $a_k^{\rm valid}>0$ 且 $a_k^{\rm spur}<0$。若伪相关分数为正且预测相关性很高，就是优先调查对象；若两者都不对齐，则代表“意外概念”，不能简单当成安全组件（`paper.md:386-398`）。公共代码提供通用相似度原语，但未找到专门的有效/伪相关审计接口。

### 步骤 6：量化组件是否容易被人理解

SemanticLens 不只解释模型，也试图衡量“模型内部是否天然可解释”。

**清晰度（clarity）**：同一组件的概念样本在语义空间中越一致，越容易概括共同主题。代码实现论文给出的高效归一化均值公式（`scores.py:18-47`）。

**相似度与冗余度（similarity/redundancy）**：每个组件找最相似的另一个组件，再对最大相似度求平均：

$$
I_{\rm red}({\mathcal V})=\frac{1}{m}\sum_{k=1}^{m}
\max_{j\ne k}I_{\rm sim}(\boldsymbol{\vartheta}_k,\boldsymbol{\vartheta}_j).
$$

需要注意，语义冗余不一定等于功能冗余。例如斑马条纹和条纹鱼在语义上相似，但对分类器可能承担完全不同的作用。

**多义性（polysemanticity）**：先把同一组件的样本聚成 $h$ 个簇，再计算簇中心的不一致程度：

$$
I_{\rm poly}=1-I_{\rm clarity}(\text{cluster centres}).
$$

代码默认使用 KMeans、$h=2$、随机种子 123，并处理空簇情况（`scores.py:131-185`）。

### 主要实验说明了什么

1. **可搜索的内部知识**：在 ImageNet ResNet50v2 上，文本查询能找到与人、肤色、水印和生物发光相关的神经元。Fig. 2 进一步把这些神经元连到 ox 预测、训练样本和其他受影响类别。
2. **组合伪特征会放大风险**：单独使用 Indian person、palm tree 或 cart 的生成图像时，ox 与真实 ox 输出仍有 AUC > 0.98；三种伪特征组合后 AUC 降到 0.91，而且超过一半样本让 ox 进入 top-5（`paper.md:180-183`；Fig. 3）。
3. **问题并非个例**：审计的另外 26 个 ImageNet 类别中，每个类别的相关组件都包含某些背景或伪相关概念（`paper.md:186-195`）。
4. **医学模型调试**：在 ISIC 2019 黑色素瘤任务中，方法发现红皮肤、蓝色创可贴和测量尺组件。剪掉 40 个组件和清洗/增强数据后重训都提高干净测试集准确率，但只有重训明显降低伪影敏感性（`paper.md:198-233`；Fig. 4）。
5. **度量与人类判断一致**：超过 218 名参与者的研究中，计算度量与人类判断的相关性约为 0.72-0.81；稀疏正则化同时提高了清晰度并降低冗余和多义性（`paper.md:236-271`；Fig. 5）。

### 如何正确解读这些结果

SemanticLens 最有价值的地方不是给神经元贴一个漂亮标签，而是建立可行动的审计链：

```text
发现可疑语义 -> 确认它是否影响预测 -> 找到对应训练样本
-> 做受控扰动 -> 剪枝或修复数据 -> 重新评估
```

图 4 的结果说明，只删除可疑组件未必能消除模型对伪影的整体依赖；通过清洗和增强数据重新训练更有效。这也提醒我们，组件标签是诊断工具，不是因果修复本身。

### 局限与复现状况

- 方法依赖基础模型的领域语义能力；错误或缺失的语义会直接传递到解释。
- 审计只能覆盖用户定义的有效/伪相关词表，未对齐组件仍需人工检查。
- 分布式概念和特征叠加可能使单神经元基底不忠实；SAE 是潜在改进方向。
- 这是事后解释方法，不能替代从设计上可解释的模型。
- GitHub 快照包含核心收集、嵌入、探测和度量代码，论文-代码整体匹配度为中等；未找到论文全部实验、医学重训、用户研究和完整审计的端到端脚本。
- 当前环境缺少 PyTorch，测试套件在收集阶段停止；这里不声称代码已在本机成功运行。

更精确的论文-代码对应关系见 `doc_code.md`，完整公式和假设见 `doc_method.md`，图像证据见 `figure_analysis.md`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SemanticLens

### Problem

Large neural networks can predict accurately while relying on opaque, biased, or shortcut features. Input attribution, probing, and activation visualization each expose only part of the story and do not scale to a holistic connection among component meaning, component use, prediction, and source data (`paper source/nature_html/paper.md:22-44`).

### Proposed Method

SemanticLens embeds the concept examples of individual model components into the semantically structured space of a foundation model such as CLIP. Top-activating samples describe what a neuron responds to; averaged foundation-model embeddings turn those samples into searchable vectors; component-level relevance connects the vectors to predictions. The resulting representation supports text/image search, labeling, model comparison, valid-versus-spurious alignment audits, source-data tracing, and scalable interpretability scores (`paper.md:45-75`; detailed pipeline in `doc_method.md`).

### Technical Core

For component $k$ in layer $\ell$, the paper defines concept examples as the top-$m$ activating samples with attribution-based cropping (Eq. 1), then computes a mean semantic vector $\boldsymbol{\vartheta}_k$ (Eq. 2). Cosine similarity drives text/image search and model comparison (Eqs. 3-5). Valid and spurious alignment scores are maxima over user-defined probe sets after null-embedding subtraction; combining those scores with relevance identifies harmful components. Clarity, redundancy, and KMeans-based polysemanticity quantify how understandable and overlapping the resulting concepts are (Eqs. 6-10; `paper.md:298-459`).

### Evidence and Results

- On ResNet50v2/ImageNet, queries retrieve person, watermark, and bioluminescence components; UMAP, attribution graphs, and reference examples connect those components to ox predictions and affected classes (`paper.md:86-147`; Fig. 2).
- In an ox audit, single spurious concepts yield AUC values above 0.98, whereas Indian-person + cart + palm-tree composites reduce AUC to 0.91; all 26 additionally audited ImageNet classes use some spurious/background relevant component (`paper.md:159-195`; Fig. 3).
- In a VGG-16 melanoma model on ISIC 2019, SemanticLens identifies red-skin, band-aid, and ruler components. Pruning 40 neurons and retraining both improve clean accuracy, but only cleaned/augmented retraining strongly reduces artefact sensitivity (`paper.md:198-233`; Fig. 4).
- More than 218 human participants rated concept examples. Similarity, clarity, and polysemanticity correlate positively with human judgement (roughly 0.72-0.81 in Fig. 5); sparsity regularization improves the measured interpretability profile (`paper.md:236-271`).

### Reproducibility

**Rating: 3/5.** The public GitHub snapshot is attributable and contains a usable PyTorch toolbox with activation-max collection, foundation-model image/text probing, caching, and the three interpretability metrics (`code/README.md:46-100`; `doc_code.md`). However, the inspected package has no dedicated valid/spurious audit, label/compare API, paper-figure training scripts, or end-to-end medical/user-study reproduction. The relevance visualizer is explicitly marked under development. The article references supplementary notes and Supplementary Code 1, but those artifacts were not acquired. The local test suite could not be collected because PyTorch is unavailable in this environment; no runtime success is claimed.

### Limitations

SemanticLens inherits the semantic blind spots of its foundation model, depends on a sufficiently faithful component basis, and evaluates alignment only against user-specified concept vocabularies. It is post hoc rather than ante hoc, may miss distributed concepts, and semantic similarity does not guarantee functional redundancy. The paper also leaves generative-model adaptation and several training controls for future work (`paper.md:274-283`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
