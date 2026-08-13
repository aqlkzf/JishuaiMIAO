---
layout: default
permalink: /paper-atlas/caml-b0fa4a16/
title: "CAML"
nav: false
wide: true
description: "这篇论文关注的是医疗 AI 的“可解释性鸿沟”。很多现有方法只能给出局部热图，告诉你某一张图哪里可能重要，但很难总结整个模型到底学会了什么规则；另一类全局解释方法又往往太简单，解释性提高了，准确率却掉得很厉害。作者提出 CAML，希望把“全局规则”和“单个病例解释”统一到同一个低维流形里 。 作者认为，一张医疗图像里既有真正和疾病判别相关的模式，也有很多“个体背景信息”，比如位置、形态、亮度、背景差异等。"
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
      <span>Nature Biomedical Engineering · 2026</span>
    </div>
    <h1>CAML</h1>
    <p>Bridging the interpretability gap for medical artificial intelligence models using class-association manifold learning</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41551-026-01676-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CAML">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/xrt11/XAI-CAML" target="_blank" rel="noopener noreferrer" aria-label="Open code for CAML">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CAML 方法解读

### 这篇论文要解决什么问题？

这篇论文关注的是医疗 AI 的“可解释性鸿沟”。很多现有方法只能给出局部热图，告诉你某一张图哪里可能重要，但很难总结整个模型到底学会了什么规则；另一类全局解释方法又往往太简单，解释性提高了，准确率却掉得很厉害。作者提出 CAML，希望把“全局规则”和“单个病例解释”统一到同一个低维流形里 (`paper source/nature_html/paper.md:21-33`)。

### CAML 的核心想法

作者认为，一张医疗图像里既有真正和疾病判别相关的模式，也有很多“个体背景信息”，比如位置、形态、亮度、背景差异等。如果把这些东西混在一起，解释就会很乱。所以 CAML 先把样本编码成两部分：

- **class-associated code**：和类别、诊断决策相关的编码；
- **individual code**：和个体背景、上下文相关的编码 (`paper source/nature_html/paper.md:53-56,275-276`)。

这样做的好处是：

1. 可以只看 class-associated code，分析模型的全局判别结构；
2. 可以沿着这个结构中的路径做“有方向的修改”；
3. 再把这些修改和同一个病例的 individual code 重新组合，生成一系列对比样本；
4. 观察黑盒分类器在这条路径上何时翻类，从而得到更有语义的解释 (`paper source/nature_html/paper.md:56-59,301-307`)。

### 整体流程

```text
训练数据 + 需要解释的黑盒分类器
    -> CAE 把每个样本拆成 class-associated code 和 individual code
    -> 通过重构、交叉重构、循环重构和对抗训练，逼迫两种信息分离
    -> 收集所有样本的 class-associated code
    -> 在低维空间里做 t-SNE + Mapper + DBSCAN，得到拓扑图
    -> 在图上寻找从当前样本到目标类别的最短路径
    -> 固定当前样本的 individual code，只替换路径上的 class-associated code
    -> 生成一串逐步变化的反事实样本
    -> 用原图和翻类后的生成图做差，得到显著区域
```

这个逻辑和论文的 Fig. 1、Fig. 8 是一致的 (`paper source/nature_html/paper.md:42-59,275-307`)。

### 代码里怎么实现？

公开代码里的核心网络在 `XAI-CAML/code/CAML_Train/networks.py`。

- `CAEGen` 里有两个编码器：
  - `enc_style` 对应论文里的 class-associated code；
  - `enc_content` 对应论文里的 individual code。
- `dec` 负责把这两部分重新拼起来生成图像。
- `mlp` 给解码器提供 AdaIN 参数，用 style code 控制生成结果 (`XAI-CAML/code/CAML_Train/networks.py:90-128`)。

判别器 `MultiClassDis` 不是只判断真假，它同时还输出类别信息：

- 前两维 logits 用来做 real/fake；
- 后面几维用来做类别判别 (`XAI-CAML/code/CAML_Train/networks.py:57-80`)。

这和论文 Methods 里说的 `D_r` 与 `D_c` 是对得上的 (`paper source/nature_html/paper.md:275-276`)。

### 训练时到底学什么？

训练逻辑在 `trainer_exchange.py` 很清楚：

1. 先编码 `x_a` 和 `x_b`；
2. 分别自重构；
3. 交换 class-associated code，得到跨类别生成图；
4. 再次编码这些生成图；
5. 再做 cycle decode 回到原图；
6. 同时优化多种损失：
   - 图像重构损失；
   - class-code 重构损失；
   - individual-code 重构损失；
   - cycle 重构损失；
   - 生成器的对抗/分类损失；
   - 判别器的对抗/分类损失 (`XAI-CAML/code/CAML_Train/trainer_exchange.py:88-154`)。

论文 Methods 里把这些损失分成 adversarial、classification、cyclic 和三种 reconstruction loss，代码和论文叙述是匹配的 (`paper source/nature_html/paper.md:286-289`)。

### 全局解释是怎么做的？

训练完后，作者不是直接在原图上解释，而是先把所有样本映射到 class-associated code 空间。

`CL_codes_extract.py` 会读取图像、跑编码器、把每个图像的 latent code 和标签写入 CSV (`XAI-CAML/code/CL_Analysis/CL_codes_extract.py:65-114`)。

然后 `topological_analysis.py` 做三件事：

1. 用 t-SNE 把 latent code 投到二维；
2. 用 KeplerMapper 建图；
3. 在每个 cover 里用 DBSCAN 聚类，最后得到拓扑图 (`XAI-CAML/code/CL_Analysis/topological_analysis.py:39-75`)。

这正对应论文 Methods 中“先 t-SNE，再 Mapper，再 DBSCAN”的拓扑分析流程 (`paper source/nature_html/paper.md:295-299`)。

这个拓扑图的意义是：它不是只告诉你点和点的距离，而是提供了一种更接近流形路径的全局结构。这样就可以回答：

- 哪些亚型彼此接近？
- 从正常到异常常见的过渡方向是什么？
- 哪些路径可能对应临床上有意义的疾病演化？

### 局部解释为什么和普通热图不一样？

普通 saliency 方法往往是局部梯度或局部扰动，很容易掉进噪声、背景偏差或 shortcut。CAML 的局部解释先借助全局流形来找“合理路径”。

代码里 `shortest_path_get_for_each_two_points.py` 的做法是：

1. 给每个拓扑节点一个中心向量；
2. 把起点图像和目标图像都映射到最近节点；
3. 在节点图上跑 Dijkstra，得到最短路径 (`XAI-CAML/code/Case_Show/shortest_path_get_for_each_two_points.py:63-80,137-147`)。

接着 `local_explanation_on_instance.py`：

1. 固定 exemplar 的 individual/content code；
2. 用路径上每个节点中心的 class-associated code 去解码；
3. 得到一串连续变化的生成图；
4. 用外部黑盒分类器检测什么时候翻类；
5. 取原图和翻类生成图的绝对差，生成热图 (`XAI-CAML/code/Case_Show/local_explanation_on_instance.py:115-137`)。

所以 CAML 的局部解释本质上不是“单步高亮”，而是“沿着全局规则路径生成反事实，再从变化中找关键区域”。这就是它和传统热图方法最大的不同 (`paper source/nature_html/paper.md:301-307`)。

### 论文结果说明了什么？

从论文和主图可以归纳出几件事：

- 低维 class-associated manifold 依然保留了很强的判别能力 (`paper source/nature_html/paper.md:62-81`)；
- 拓扑图能揭示亚型结构和疾病过渡路径，比如 OCT、OIA-DDR、RFMID 中一些临床上合理的近邻关系 (`paper source/nature_html/paper.md:82-118`)；
- 在局部解释上，CAML 的热图通常比 LIME、Grad-CAM、ICAM、Diffexplainer 等更聚焦，Fig. 5 的表格也给了对应指标支持 (`paper source/nature_html/paper.md:119-135`)；
- 临床专家盲评中，CAML 在多个任务上更受欢迎 (`paper source/nature_html/paper.md:136-155`)。

### 公开代码的局限

这份公开代码能证明核心机制是真的存在，但还不能当作论文全量复现实验包：

- 主训练代码更像是二分类/成对类别的任务模板；
- 并没有把论文里 13 个数据集的所有训练、评估、医生盲评流程都完整打包出来；
- 公开仓库偏向“方法主干 + 若干示例任务”，不是“一键复现整篇论文”。

所以更准确的结论是：**核心 CAML 机制在代码里是可验证的，但整篇论文的大规模实验体系只做到了部分公开。**

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CAML Summary

### Paper

**Bridging the interpretability gap for medical artificial intelligence models using class-association manifold learning** introduces CAML, a generative explainability framework for medical AI. The paper argues that existing explainers either provide local saliency without a global rule map or use globally interpretable models that lose too much predictive power, and proposes to bridge that gap by learning a low-dimensional class-associated manifold that can both summarize decision rules and drive counterfactual sample generation (`paper source/nature_html/paper.md:21-33`).

### Motivation

The paper’s core complaint is that conventional xAI methods leave clinicians with vague or unstable explanations, especially in medical images where pathology signal is subtle and background variation is large. CAML tries to separate disease-relevant variation from individual background variation, so that the rule structure of a black-box model can be inspected globally and then replayed locally on individual cases (`paper source/nature_html/paper.md:24-33,53-59`).

### Method Overview

CAML has three main stages. First, class-association embedding (CAE) learns two latent codes per sample: a class-associated code and an individual/background code. By swapping the class-associated code across paired samples and reconstructing synthetic images, the model is trained to preserve class-linked features while suppressing nuisance variation (`paper source/nature_html/paper.md:53-56,275-289`). Second, the learned class-associated codes are analyzed with a Mapper-style topology pipeline to produce a graph of clusters and approximate geodesic transition paths across the manifold (`paper source/nature_html/paper.md:56-59,295-299`). Third, those graph paths are used to generate ordered counterfactual samples for a chosen exemplar, and saliency-style ROI maps are derived from the change between original and generated images (`paper source/nature_html/paper.md:56-59,301-307`).

### Key Results

- On six benchmark medical image datasets, the paper reports that low-dimensional class-associated codes preserve enough decision signal that simple classifiers on the manifold outperform other global explanation baselines while staying close to the original black-box model (`paper source/nature_html/paper.md:65-80`).
- The topology graphs reveal subtype structure and clinically meaningful transition paths, for example among OCT disease subtypes and diabetic retinopathy severity (`paper source/nature_html/paper.md:82-110`).
- For local explanations, CAML saliency maps appear sharper and more pathology-focused than LIME, Fullgrad, Grad-CAM, ICAM, Diffexplainer, and related baselines, and the associated metric table in Fig. 5 reports best or near-best AOPC, PD, IOU, and DICE in several tasks (`paper source/nature_html/paper.md:119-135`).
- The paper also includes blind clinician evaluation on authenticity, disease-feature sorting, and pairwise trust/preference tasks, with CAML generally favored over several comparison methods (`paper source/nature_html/paper.md:136-155`).

### Code Match

The public code snapshot supports the central CAML mechanics at **medium fidelity**. The visible repository contains:

- a CAE training stack with paired class-A/class-B dataloaders, a `CAEGen` encoder/decoder, and a `MultiClassDis` adversarial classifier (`XAI-CAML/code/CAML_Train/main_train.py:18-49,65-99,165-230`; `XAI-CAML/code/CAML_Train/networks.py:11-38,90-128`);
- a training loss loop that combines reconstruction, code reconstruction, cycle reconstruction, and discriminator/classification objectives (`XAI-CAML/code/CAML_Train/trainer_exchange.py:88-154`);
- a latent-code extraction script and a topology-analysis script using t-SNE, KeplerMapper, and DBSCAN (`XAI-CAML/code/CL_Analysis/CL_codes_extract.py:60-114`; `XAI-CAML/code/CL_Analysis/topological_analysis.py:28-75`);
- a local explanation stack that computes shortest paths on node graphs and decodes guided counterfactual images before producing heatmaps from absolute image differences (`XAI-CAML/code/Case_Show/shortest_path_get_for_each_two_points.py:63-80,137-147`; `XAI-CAML/code/Case_Show/local_explanation_on_instance.py:115-137`).

Important limits remain. The repo is organized around prepared example datasets and pre-trained assets rather than a full paper-reproduction harness. The visible training path is pairwise and somewhat task-specific, while the paper’s broad multi-dataset evaluation and clinician-study infrastructure are not fully packaged in the public snapshot.

### Strengths

- Unifies global and local explanation in one representation-and-generation pipeline.
- Produces visually inspectable transition sequences instead of only heatmaps.
- Gives a concrete mechanism for discovering subtype or rule structure in the latent manifold.
- Public code exposes the core CAE, topology, path, and local-explanation mechanics rather than only figure notebooks.

### Limitations

- The HTML paper conversion contains no explicit display equations, so several loss definitions are only available as prose in the paper and as code in the repo.
- The visible code snapshot is not a full end-to-end reproduction of every dataset and user study reported in the paper.
- Some implementation details are task-shaped: for example, the main training script assumes paired `trainA`/`trainB` folders and the discriminator comment is written for a specific four-output setup (`XAI-CAML/code/CAML_Train/networks.py:30-37`).
- Local explanation is implemented as guided generation plus image-difference heatmaps, which is simpler than some readers may infer from the paper’s broader narrative.

### Reproducibility Rating

**3/5**

The main method is visible and inspectable in public code, and the route from latent code extraction to topology analysis and exemplar explanation is concrete. Full reproduction of the paper’s large benchmark set, non-image experiments, and blinded clinician evaluations still depends on external datasets, trained models, and missing orchestration details.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
