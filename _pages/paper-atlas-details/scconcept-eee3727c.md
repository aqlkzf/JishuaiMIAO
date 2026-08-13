---
layout: default
permalink: /paper-atlas/scconcept-eee3727c/
title: "scConcept"
nav: false
description: "scConcept 先用神经主题模型从单细胞表达矩阵中提取若干加权基因程序，再让 GPT-5 对这些程序做过滤、合并和命名，形成“名称—描述—代表基因—来源主题”四元组；最后用概念基因在每个细胞中的标准化表达计算概念分数。它的核心价值不是再造一种低维坐标，而是在基因列表和细胞状态之间建立可读、可计算的中间层。"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>scConcept</h1>
    <p>scConcept enables concept-level exploration of single-cell transcriptomic data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.04.21.719959" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scConcept">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/li-lab-mcgill/scConcept" target="_blank" rel="noopener noreferrer" aria-label="Open code for scConcept">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scConcept 方法解释：把“基因主题”提升为可读、可回映的生物概念

### 一句话理解

scConcept 先用神经主题模型从单细胞表达矩阵中提取若干加权基因程序，再让 GPT-5 对这些程序做过滤、合并和命名，形成“名称—描述—代表基因—来源主题”四元组；最后用概念基因在每个细胞中的标准化表达计算概念分数。它的核心价值不是再造一种低维坐标，而是在基因列表和细胞状态之间建立可读、可计算的中间层。

### 1. 为什么已有主题模型还不够

单细胞主题模型能把细胞表示为多个潜在主题的混合，并为每个主题给出高权重基因。但主题常有三个实际问题：一些基因列表缺乏一致生物含义，一些主题彼此冗余，即使主题有效也需要专家逐个解释。scConcept 把任务拆成两个角色：

- ECRTM 从表达数据中学习统计上可分离的基因程序；
- LLM 承担语义整理，将多个主题蒸馏为数量不固定、意义更连贯的概念。

因此 LLM 不直接读取数万细胞的表达矩阵，也不凭空为细胞分类；它只处理每个主题的前 100 个基因。

### 2. 第一层：ECRTM 如何得到主题

输入是细胞—基因矩阵 $X\in\mathbb R^{N\times G}$。对细胞 $i$，编码器给出潜变量的均值和方差，经重参数化与 softmax 得到主题比例

$$
\theta_i=\operatorname{softmax}(z_i),\qquad \theta_i\in\mathbb R^K.
$$

基因嵌入 $g_m$ 与主题嵌入 $t_k$ 的距离决定基因—主题权重；距离越近，基因越属于该主题。代码在 `ECRTM/models/ECRTM.py:77-91` 计算距离并以温度参数控制分布尖锐程度，在 `ECRTM/models/ECRTM.py:103-131` 编码细胞主题比例。解码器用 $\theta_i$ 和主题—基因矩阵重建表达，同时优化重建/KL 损失和 ECR 正则；ECR 通过最优传输式约束减少主题重叠。

训练完成后，每个主题按权重取前 $h=100$ 个基因，输出若干主题基因列表。这里的“100”只是给后续语义蒸馏的固定信息窗口，不表示所有基因同等重要。

### 3. 第二层：LLM 如何把主题蒸馏为概念

scConcept 将全部主题及其基因列表放入结构化提示，要求 GPT-5：

1. 丢弃不连贯或信息不足的主题；
2. 合并表达相近生物程序的冗余主题；
3. 为每个概念给出简短名称、自然语言描述、100 个代表基因和来源主题 ID。

一个概念可写成

$$
C_j=(S_j,n_j,d_j,T_j),
$$

分别表示基因集、名称、描述和来源主题集合。最终概念数由蒸馏结果决定，不必等于预设主题数 $K=50$。

这一步的证据边界很重要：名称和基因组成依赖托管 LLM 的输出。固定随机种子只能降低波动，不能保证未来的 GPT-5 服务返回逐字一致结果。代码 `scConcept.py:763-809` 虽接受 `temperature` 参数，却没有把它传给 OpenAI 请求。

### 4. 概念怎样映射回每个细胞

先对每个基因跨细胞做 z-score：

$$
\tilde x_{im}=\frac{x_{im}-\mu_m}{\sigma_m+10^{-6}}.
$$

再对概念基因集在细胞内取平均：

$$
z_{ij}=\frac{1}{|S_j|}\sum_{m\in S_j}\tilde x_{im}.
$$

例如某概念含三个基因，某细胞的标准化表达是 $(1.2,0.3,-0.6)$，概念分数就是 $(1.2+0.3-0.6)/3=0.3$。若做硬注释，细胞被分给得分最高的概念。`scConcept.py:826-846` 与论文这一计算完全对应；它是透明的均值打分，而不是另一个黑盒分类器。

### 5. 两个扩展：层级概念与发育潜能

#### 层级细化

对一个父概念，方法先检查高置信细胞比例、最小细胞数以及继续划分能否显著降低不纯度；满足阈值后，再让 LLM 把父概念细分为子概念。子层只在父层候选细胞内竞争，避免一个细胞跨到无关分支。论文在胰腺示例中把粗粒度的胰岛内分泌概念进一步分成 alpha、beta、delta/PP 等程序。

#### 发育潜能

另一套提示把主题基因映射到 totipotent、pluripotent、multipotent、oligopotent、unipotent、differentiated 六个预定义等级。此处细胞分数使用概念基因标准化表达的求和，以同时保留表达强度和基因集大小信号。图 5 显示 scConcept 在三个发育数据集上的潜能顺序与真值相符，并用概念基因的上/下调模拟状态转移。

### 6. 怎样读六张主图的证据链

- **图 1** 定义完整管线与五类下游用途。
- **图 2** 在 16 个数据集上比较聚类与解释性；论文报告相对最强基线聚类提升 27.1%、解释性提升 50.7%。这些是论文汇总结果，本地代码没有完整重跑脚本。
- **图 3** 用黑色素瘤展示概念注释、MITF 程序、扰动和 TCGA 生存关联。
- **图 4** 展示粗粒度概念递归细化为细胞亚型程序。
- **图 5** 比较发育潜能并模拟 multipotent 向 differentiated 的移动。
- **图 6** 在肺癌图谱中连接分期、生存、SCISSOR 和药物候选，是临床外推最强、同时也是本地仓库复现缺口最大的部分。

这些结果表明概念表示可以作为多种分析的接口，但不能把概念名称当作无需验证的生物事实；论文也承认 LLM 可能产生不准确的命名或基因组成。

### 7. 论文与代码的对应

| 环节 | 直接代码证据 | 对应程度 |
|---|---|---|
| ECRTM 编码、重建与 ECR 正则 | `ECRTM/models/ECRTM.py:77-229`, `ECRTM/models/ECR.py:23-80` | Exact |
| 主题训练与前 100 基因导出 | `ECRTM/Runner.py:37-125` | Exact |
| GPT 概念蒸馏与结构化 JSON | `scConcept.py:744-809` | Exact |
| 细胞概念 z-score 均值 | `scConcept.py:815-884` | Exact |
| 层级划分与受约束赋值 | `scConcept.py:1437-1520`, `scConcept.py:1832-1906` | Exact |
| 发育潜能提示和打分 | `scConcept.py:79-201`, `scConcept.py:1181-1435` | Exact |
| 16 数据集汇总、TC-LLM、跨数据迁移 | 完整运行器/结果未在快照中找到 | Not found |
| 黑色素瘤/肺癌生存、SCISSOR、PSICHIC | 相应分析脚本未在快照中找到 | Not found |

### 8. 实际复现时最容易踩的坑

- `scConcept.py:515-740` 的 `save_logged_matrix=True` 默认保存 log1p 后矩阵，但邻近 docstring 仍描述“原始表达默认值”，两者不一致。
- `.mat` 加载器会把稀疏矩阵转成 dense float32（`ECRTM/singlecell_dataset.py:54-93`），大数据集可能有明显内存压力。
- 论文主结果固定 $K=50$、种子 1；API 与 README 示例的 batch size 不完全一致。
- 仓库实现了 ARI、NMI、TC 和 TD，但未找到 TC-LLM；也没有论文所有主图的一键复现入口。

最准确的定位是：该代码快照较完整地实现了 scConcept 的“主题 → 概念 → 细胞分数”方法 API 和两个扩展，但只部分覆盖论文规模的基准、临床与药物分析。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scConcept: Summary

### Motivation And Novelty

scConcept addresses a familiar gap in single-cell analysis: embeddings and clusters can separate cells, but they do not automatically explain the biological programs behind those separations. Classical interpretable models such as NMF, LDA/cisTopic (Nature Methods, 2019), scVI-LD (Bioinformatics, 2020), and scETM (Nature Communications, 2021) expose factors or topics, but those topics still require manual interpretation and can be redundant or biologically vague. Foundation-model baselines such as scGPT (Nature Methods, 2024), CellPLM (bioRxiv, 2023), GenePT (bioRxiv, 2024), and Cell2Sentence (bioRxiv, 2024) provide learned representations but not structured, per-cell biological concepts.

The paper's novelty is to treat topic gene lists as an interface between neural topic modeling and LLM semantic curation. scConcept first learns gene-level topics with ECRTM, then uses GPT-5 to merge, filter, and name those topics as human-readable concepts. Each concept is a structured object containing a name, description, representative gene set, and source topics. These concept gene sets are then mapped back to individual cells as concept scores.

### Method Overview

The pipeline has three core steps. First, scConcept preprocesses a scRNA-seq matrix and trains ECRTM, a VAE-style neural topic model with embedding clustering regularization. The topic model learns cell-topic proportions and a gene-topic matrix. For each topic, the top 100 genes are extracted.

Second, an LLM receives only those topic gene lists. The prompt asks it to remove incoherent topics, merge redundant or related topics, and produce biological concepts as strict JSON. This is the main abstraction step: raw topic lists become named, semantically coherent gene programs.

Third, the concepts are scored in cells. Each gene is standardized across cells, and a cell-concept score is computed as the average standardized expression of the concept's genes. Each cell is assigned to the concept with the highest score. Extensions include hierarchical concept refinement, developmental potency concepts, in silico concept perturbation, TCGA survival transfer, and drug-target screening.

### Evaluation

The main benchmark covers 16 scRNA-seq datasets across multiple tissues, species, and sequencing protocols. The paper compares scConcept with CellPLM, scGPT, GenePT, Cell2Sentence, scVI, scVI-LD, scETM, d-scIGM, scE2TM, and Seurat. Metrics include ARI and NMI for clustering plus TC, TD, and TC-LLM for interpretability. The paper reports 27.1% clustering improvement and 50.7% interpretability improvement over the strongest competing method.

Case studies extend the claim beyond generic clustering. In melanoma, scConcept recovers a Melanocytic MITF program, links it to classifier SHAP importance, marker enrichment, perturbation shifts, and TCGA survival. In hierarchical pancreas/lung data, it refines broad concepts into sub-concepts. In developmental datasets, it performs comparably to CytoTRACE2 (Nature Methods, 2025) for potency prediction. In a large NSCLC atlas, it links B-cell and mitotic proliferation programs to stage, survival, SCISSOR associations, and candidate drugs.

### Reproducibility

**Rating: 3/5.**

The core method is implemented and readable in the public GitHub repository. The code includes ECRTM, topic extraction, GPT concept generation prompts, cell-concept annotation, evaluation for ARI/NMI/TC/TD, developmental potency scoring, and hierarchical refinement. The README and tutorials make the basic workflow approachable.

The missing piece is full manuscript reproducibility. I did not find scripts for the full 16-dataset benchmark, TC-LLM metric, cross-dataset transfer, melanoma SHAP/CellMarker/TCGA survival analysis, logistic-regression perturbation evaluation, SCISSOR analysis, or PSICHIC drug screening. The code is therefore strong for method use, but incomplete for independently regenerating all figures and headline claims.

Practical caveats: the pipeline depends on hosted GPT-5 outputs, the accepted `temperature` parameter is not passed to the OpenAI call, and generated concept JSON files for the paper datasets are not archived in the acquired repository.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
