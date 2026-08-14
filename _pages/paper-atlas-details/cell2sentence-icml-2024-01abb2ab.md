---
layout: default
permalink: /paper-atlas/cell2sentence-icml-2024-01abb2ab/
title: "Cell2Sentence_ICML_2024"
nav: false
wide: true
description: "C2S 不是提出一种新的 Transformer 结构，而是提出一种新的数据接口： 因此，方法创新主要来自： 单细胞表达谱的文本化表示； 细胞与自然语言之间的双向任务设计； 使用自然语言预训练获得的语义结构来理解生物标签。"
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
      <span>PMLR · 2024</span>
    </div>
    <h1>Cell2Sentence_ICML_2024</h1>
    <p>Cell2Sentence: Teaching Large Language Models the Language of Biology</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/vandijklab/cell2sentence" target="_blank" rel="noopener noreferrer" aria-label="Open code for Cell2Sentence_ICML_2024">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Cell2Sentence 方法详解

### 1. 这篇论文要解决什么问题？

单细胞 RNA 测序通常把一个细胞表示成高维基因表达向量。传统方法会为这种向量设计专用神经网络，例如用于表示学习和生成的 scVI（Nature Methods, 2018）、用于扰动预测的 scGen（Nature Methods, 2019）、以及后来的 Geneformer（arXiv, 2022；相关工作发表于 Nature, 2023）和 scGPT（bioRxiv, 2023）。

这些模型能够处理单细胞数据，但它们不能直接利用通用大语言模型已经学到的自然语言语义，也不能自然地把“细胞类型、组织、疾病、药物、处理时间”等文本标签与表达谱放进同一种输入格式。

Cell2Sentence（C2S）的核心问题是：

> 能否把一个细胞的表达谱转换成“句子”，从而直接用因果语言模型完成细胞生成、标签预测和生物学文本生成？

论文的回答是：把非零表达基因按照表达量从高到低排列，写成由基因名组成的序列。这样得到的 `CD3D IL32 LTB ...` 就是一个 **cell sentence**。随后可把自然语言标签与 cell sentence 组合成提示词，使用标准的下一 token 预测训练 GPT-2 或 Pythia（`paper.md:17-31`, `paper.md:51-65`）。

### 2. 方法的输入和输出

#### 输入

设原始计数矩阵为：

$$
C \in \mathbb{R}^{n \times k},
$$

其中：

- $n$：细胞数；
- $k$：基因数；
- $C_{i,j}$：第 $i$ 个细胞中第 $j$ 个基因的转录本计数。

还可以输入细胞或研究层面的元数据，例如：

- cell type；
- tissue；
- disease；
- cytokine stimulation 和 exposure；
- 论文摘要或合成摘要。

#### 输出

根据提示方向不同，模型可以输出：

1. 给定细胞类型或条件，生成一个 cell sentence；
2. 给定 cell sentence，预测细胞类型或组合标签；
3. 给定 cell sentence，生成自然语言形式的生物学描述；
4. 给定部分基因序列，继续补全 cell sentence；
5. 将生成的 cell sentence 近似还原为表达向量。

### 3. 一句话理解 C2S

C2S 不是提出一种新的 Transformer 结构，而是提出一种新的数据接口：

```text
表达向量
  -> 按表达量排序的基因名序列
  -> 与自然语言元数据拼接
  -> 用标准因果语言模型训练和生成
```

因此，方法创新主要来自：

- 单细胞表达谱的文本化表示；
- 细胞与自然语言之间的双向任务设计；
- 使用自然语言预训练获得的语义结构来理解生物标签。

### 4. 从输入到输出的完整计算流程

```text
原始单细胞计数矩阵 C + 元数据
                |
                v
细胞/基因过滤 + 线粒体比例质控
                |
                v
每个细胞归一化到 10,000 + log 变换 -> C'
                |
                v
只保留非零表达基因，并按表达量降序排列
                |
                v
cell sentence: "GENE_1 GENE_2 ... GENE_m"
                |
                +-------------------------------+
                |                               |
                v                               v
加入 cell type / tissue / condition       拟合 expression ~ log(rank)
等自然语言提示                            的数据集特异线性模型
                |                               |
                v                               |
因果语言模型微调                           |
                |                               |
                v                               |
生成基因序列或自然语言文本                 |
                |                               |
                v                               |
无效基因处理 + 重复基因秩合并              |
                +-------------------------------+
                v
可选：还原为近似表达向量
```

### 5. 第一步：表达矩阵预处理

论文先执行以下过滤：

- 去除表达基因少于 200 个的细胞；
- 去除在少于 200 个细胞中表达的基因；
- 去除总 counts 超过 2,500 的细胞；
- 去除线粒体转录本比例超过 20% 的细胞。

随后对每个细胞把总计数归一化到 10,000，并进行 log 变换（`paper.md:57-65`）：

$$
C_{i,j}^{\prime} = \log_{10}\left(1 + 10^4 \times \frac{C_{i,j}}{\sum_{j=1}^{k} C_{i,k}}\right). \tag{1}
$$

这里的 $C'$ 是后续排序使用的预处理表达矩阵。

#### 论文事实与代码事实

- **论文事实：** 上述 Scanpy 质控与归一化属于方法流程。
- **代码验证：** 当前 `CSData.adata_to_arrow` 直接接收已经准备好的 `AnnData`，然后生成词表和 cell sentence（`cell2sentence_repo/src/cell2sentence/csdata.py:44-83`）。
- **Not found：** 当前代码快照没有论文 ICML 实验所用的完整预处理脚本，也没有 Equation 1 的端到端入口。

这意味着：相同的排序代码如果接收不同的预处理矩阵，最终 cell sentence 也可能不同。复现实验时，预处理缺失是重要风险。

### 6. 第二步：把一个细胞转换成 cell sentence

对第 $i$ 个细胞，把所有非零表达基因按照 $C'_{i,j}$ 从高到低排序：

```text
原始表达：
G1=0.4, G2=2.1, G3=0, G4=1.3

排序后：
G2 > G4 > G1

cell sentence：
"G2 G4 G1"
```

零表达基因不进入句子，因此句子长度等于该细胞的非零表达基因数。论文在 GPT-2 实验中常截取前 100 个基因；Pythia-160m 使用最长 9,200 token，以处理更完整的 cell sentence（`paper.md:198`）。

#### 代码如何实现？

`generate_sentences` 的实际步骤是（`cell2sentence_repo/src/cell2sentence/utils.py:81-119`）：

1. 把 `adata.X` 转成 CSR 稀疏矩阵；
2. 读取每个细胞的非零列索引和表达值；
3. 先随机打乱并列值，用于处理相同表达量的基因；
4. 使用稳定降序排序；
5. 把排序后的基因名用空格连接。

代码还会把基因名统一转换为大写（`utils.py:56-60`）。

一个隐藏细节是：`adata_to_arrow` 虽然暴露了 `random_state` 参数，但当前实现没有把它传给 `generate_sentences`；因此相同表达值的 tie breaking 实际使用工具函数默认 seed 42（`csdata.py:45-49`, `csdata.py:71-74`, `utils.py:81-96`）。

### 7. 第三步：为什么 rank 还能近似恢复表达量？

排序后精确表达值已经丢失。C2S 假设在一个数据集内部，基因表达与其排序位置之间存在稳定的 log-linear 关系。

对数据集 $d$，论文拟合：

```text
normalized expression ≈ a_d * log(rank) + b_d
```

其中 $a_d$ 和 $b_d$ 是该数据集特异的斜率和截距（`paper.md:99-103`）。

如果生成序列中同一个基因出现多次，论文先计算平均 rank：

$$
r_i^{\text{gen}} = \frac{1}{|G|}\sum_{j=1}^{|G|}\operatorname{rank}\left(g_j^{\text{gen}}\right). \tag{2}
$$

再计算近似表达：

$$
e_i^{\text{gen}} =
\begin{cases}
a_d \times \log\left(r_i^{\text{gen}}\right) + b_d, & g_i^{\text{gen}} \in G,\\
0, & \text{otherwise.}
\end{cases} \tag{3}
$$

不在句子中的基因表达量设为 0；无效基因名不写入表达向量，但论文在计算后续有效基因 rank 时保留其原始位置（`paper.md:101-117`, `paper.md:570-584`）。

#### 代码中的对应实现

- `benchmark_expression_conversion`：排序、拟合线性回归、预测表达，并计算 $R^2$、Pearson、Spearman（`utils.py:153-280`）。
- `post_process_generated_cell_sentences`：识别无效 token，并把重复基因重新插入到整数平均位置（`utils.py:401-443`）。
- `reconstruct_expression_from_cell_sentence`：按 `intercept + slope * log10(1 + position)` 构造表达向量（`utils.py:446-486`）。

#### Partial：代码与论文不是完全同一个端到端函数

当前代码把“清理生成序列”和“表达重建”拆成两个函数；重复位置还会转换为整数。它实现了论文的主要思想，但对无效基因和重复基因的边界行为不应视为 Equation 2-3 的完全等价实现。

### 8. 第四步：把任务统一成提示词和回答

C2S 用提示方向定义任务：

| 任务 | 输入提示 | 目标回答 |
|---|---|---|
| 条件细胞生成 | 细胞类型、组织或扰动条件 | cell sentence |
| 细胞标签预测 | cell sentence | cell type 或组合元数据 |
| 生物学文本生成 | cell sentence | 摘要式自然语言文本 |
| cell completion | 部分基因序列 | 后续基因序列 |

例如：

```text
输入：Generate the 100 highest expressed genes for a plasma cell
回答：MZB1 JCHAIN IGKC ...
```

或者反向：

```text
输入：Identify the cell type associated with: CD3D IL7R LTB ...
回答：The cell type is a CD4 T cell.
```

当前代码中的 `C2SPromptFormatter` 会截断到 `top_k_genes`、随机选择 JSON 模板、填充字段，并输出 `model_input` 与 `response`（`cell2sentence_repo/src/cell2sentence/prompt_formatter.py:31-48`, `prompt_formatter.py:69-152`）。

但当前模板是持续演化的软件包模板，不是论文全部 20 个实验模板的冻结副本，因此与 ICML 实验只能判定为 **Partial**。

### 9. 第五步：语言模型如何训练？

C2S 使用标准因果语言模型交叉熵。设 token 序列为 $x=\{x_0,\ldots,x_N\}$，位置 $i$ 的 logits 为 $z_i$，词表为 $\mathcal{V}$：

$$
L(x) = -\frac{1}{N}\sum_{i=1}^{N}
\log\left(
\frac{\exp(z_{i,v_i})}
{\sum_{v\in\mathcal{V}}\exp(z_{i,v})}
\right).
$$

论文实际上区分两种训练方式：

#### A. 从随机初始化开始训练

对提示词和回答的全部 token 计算 loss。否则自然语言提示 token 的 embedding 仍接近随机，模型难以学习提示与标签之间的条件关系（`paper.md:526-544`）。

#### B. 在自然语言预训练模型上微调

只对回答/标签部分计算 loss，即经典 instruction fine-tuning（`paper.md:546-550`）。

#### 代码验证

`CSModel.fine_tune` 提供 `loss_on_response_only` 参数（`cell2sentence_repo/src/cell2sentence/csmodel.py:77-150`）：

- `True`：提示 token 的 label 设为 `-100`，只训练回答；
- `False`：把完整提示与回答都作为训练 label。

对应实现位于 `utils.py:366-398`。代码默认值是 `True`，符合论文的预训练模型微调方式；如果要复现随机初始化训练，需要调用者显式设为 `False`。

### 10. 第六步：推理和生成

论文生成设置为：

- `top_p = 0.9`；
- `temperature = 0.7`；
- 生成到 EOS；
- 随机抽取训练时同类提示模板（`paper.md:570-586`）。

代码中的调用路径为：

```text
generate_cells_conditioned_on_cell_type
  -> 随机选择 prompt template
  -> CSModel.generate_from_prompt_batched
  -> tokenizer
  -> model.generate(**kwargs)
  -> 删除输入 prompt 和 EOS 文本
```

直接源码位置为 `tasks.py:28-99` 和 `csmodel.py:242-275`。

需要注意：`top_p` 和 `temperature` 并未写成函数默认值，而是通过 `**kwargs` 传给 Hugging Face `generate`。因此仅调用默认 API 并不等于复现论文推理配置。

### 11. 实验结果应该怎样理解？

#### 11.1 表达重建

PBMC 示例中，Figure 3 报告：

- Pearson $R=0.934$；
- Spearman $R=0.815$；
- $R^2=0.815$。

Figure 4 中原始细胞与重建细胞在 UMAP 上大范围重叠。跨 127 个数据集的 Figure 6 报告平均 Pearson $R=0.91$、Spearman $R=0.83$、$R^2=0.81$。

这些图说明 rank 保存了大量表达结构，但不是无损编码。Figure 7 的部分数据集可见曲线偏离和高 rank 区域扩散，因此必须使用数据集特异参数，不能假设一个全局线性模型适用于所有数据。

#### 11.2 条件细胞生成

在免疫细胞生成中，C2S Pythia-160m 在 Table 1 报告最优的 k-NN 和 Gromov-Wasserstein 指标，其中 k=10 accuracy 为 $0.2746 \pm 0.0073$，GW 为 $54.3040 \pm 0.3410$（`paper.md:320-322`）。

在未见过的细胞类型/细胞因子/暴露组合上，C2S 的整体 Pearson $R=0.9241 \pm 0.0002$，top-20 DE Spearman $R=0.9752 \pm 0.0016$（`paper.md:324-326`）。

但提示词鲁棒性有限：k=10 accuracy 从训练中见过的提示 $0.2746$ 降到语义相近但未见过的提示 $0.2083$（`paper.md:580-582`）。

#### 11.3 组合标签预测

论文在 cytokine stimulation、L1000 和 GTEx 上预测多部分标签。C2S 在 Table 3 的 partial-label 与 full-label 指标都优于列出的基线，但 full-label accuracy 仍只有 0.149、0.202 和 0.152。这说明模型经常能预测对部分元数据，却难以完整匹配高度组合化的标签（`paper.md:332-334`）。

#### 11.4 摘要生成

C2S 生成摘要与对应真实摘要在 embedding 空间中更接近，MMD 为 0.198，而列出的基线为 0.298 或更高（`paper.md:336-338`）。

但这里的评估重点是语义 embedding 对齐，不是逐条事实核验。附录示例中，一些生成摘要与对应原始研究的具体疾病、组织或实验内容并不一致（`paper.md:655-681`）。

### 12. 假设生成输出与论文证据必须分开

C2S 的自然语言输出适合以下用途：

- 为一个细胞提出可能的组织、状态或疾病解释；
- 为数据探索生成候选摘要或标签；
- 帮助研究者发现需要进一步验证的关联。

这些输出属于 **hypothesis generation**，不是实验验证结论。正确使用方式是：

```text
C2S 生成文本
  -> 提取可检验假设
  -> 回到表达矩阵、差异分析、通路分析和外部实验验证
  -> 决定是否支持该假设
```

不能因为语言流畅或 embedding 相似，就把生成文本直接写成已证实的生物学事实。Figures 9-10 的 attention 热图同样只显示模型内部关联模式，不能证明高 attention 基因是因果驱动基因。

### 13. 代码与论文的对应关系

| 方法环节 | 代码位置 | 匹配状态 |
|---|---|---|
| 非零基因按表达量降序排序 | `utils.py:81-119` | Exact |
| cell sentence + 元数据 Arrow 数据集 | `csdata.py:44-83`, `utils.py:292-328` | Exact |
| Equation 1 Scanpy 预处理 | 搜索完整代码快照 | Not found |
| log-rank 回归与重建评估 | `utils.py:153-280` | Exact |
| cell sentence 到表达向量 | `utils.py:446-486` | Exact |
| 无效/重复基因处理 | `utils.py:401-443` | Partial |
| 提示词格式化 | `prompt_formatter.py:69-152` | Partial |
| 全 token / response-only loss | `csmodel.py:77-150`, `utils.py:366-398` | Partial：支持两种模式，但缺实验调用 |
| 条件生成 | `tasks.py:28-99`, `csmodel.py:242-275` | Partial：采样参数由调用者提供 |
| ICML baseline 与表格评估代码 | 搜索完整代码快照 | Not found |
| ICML 摘要生成评估流水线 | 搜索完整代码快照 | Not found |

总体代码忠实度为 **medium**。核心表示和通用 API 可以验证，但当前仓库 README 主要面向后续 C2S-Scale，且缺少冻结的 ICML 实验脚本、配置、baseline 和完整评估流程。

### 14. 方法的真正优点与主要局限

#### 优点

1. **接口简单。** 任何因果语言模型都可以处理由基因名构成的序列。
2. **文本与细胞统一。** 元数据和表达谱进入同一 token 空间。
3. **任务方向灵活。** 同一模型可以 cell-to-text、text-to-cell 或 cell completion。
4. **复用成熟工具链。** 可以直接使用 Hugging Face 的 tokenizer、Trainer 和 generation API。
5. **rank 表示具有较强鲁棒性。** 多数据集结果表明表达结构可被大幅保留。

#### 局限

1. **表达重建不是无损的。** rank 丢失精确幅度，线性逆变换只是一种近似。
2. **预处理高度重要但代码缺失。** 当前快照不能直接复现论文的 Equation 1 流程。
3. **长序列成本高。** GPT-2 实验需要截断到 top-100 genes。
4. **提示词敏感。** 未见提示会降低生成分类指标。
5. **实验复现材料不完整。** 缺少 ICML launch configs、baseline 和指标脚本。
6. **生成文本可能事实错误。** 语言能力和语义相似度不等于科学真实性。

### 15. 最终理解

Cell2Sentence 的价值不在于把基因“当成普通单词”这么简单，而在于它建立了一个统一的序列接口：表达谱通过排序变成 gene-token 序列，自然语言元数据与该序列共同构成训练样本，因果语言模型则学习不同方向的条件生成。

从方法上看，最关键的三点是：

1. **rank-order transformation** 决定信息怎样进入模型；
2. **prompt-response direction** 决定模型学习哪一种生物任务；
3. **natural-language pretraining** 决定模型能否利用标签语义，而不是只记住基因序列。

论文和当前代码足以理解并重新实现核心 C2S 思想，但不足以逐项复现 ICML Tables 1-4。研究者应把代码视为核心方法库，把论文结果视为尚需原始脚本、数据版本和配置才能完整复现的实验声明。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Cell2Sentence: Teaching Large Language Models the Language of Biology

**Venue:** Proceedings of the 41st International Conference on Machine Learning (ICML), PMLR 235, 2024
**Analysis mode:** paper + code
**Code-paper fidelity:** medium
**Reproducibility rating:** 3/5

### Problem

Single-cell RNA-seq profiles are usually represented as high-dimensional count vectors and modeled with biology-specific architectures. This makes it difficult to reuse the mature training, prompting, and generation infrastructure of large language models. Cell2Sentence (C2S) asks whether a transcriptome can instead be expressed as a sequence that a causal language model can consume directly.

### Limitations of Existing Approaches

The paper contrasts C2S with specialized single-cell models for annotation and generation, including scVI (Nature Methods, 2018), scGen (Nature Methods, 2019), Geneformer (arXiv, 2022; a related transfer-learning Geneformer paper appeared in Nature, 2023), scGPT (bioRxiv, 2023), and scDiffusion (arXiv, 2024). These methods can be strong within specific single-cell tasks, but they do not directly expose transcriptomes to the natural-language interfaces and pretrained semantic structure of general causal LMs.

C2S does not eliminate all tradeoffs. Rank ordering discards exact abundance, long gene sequences are computationally expensive, and reconstruction is approximate. The paper also recreates scGPT's conditional generation because public code for that specific method was unavailable, which limits the strength of an exact implementation-to-implementation comparison (`paper.md:281-289`).

### Proposed Method

C2S preprocesses each cell, ranks its nonzero genes from highest to lowest normalized expression, and writes the ordered gene symbols as a space-separated “cell sentence.” Natural-language metadata such as cell type, tissue, disease, perturbation, or abstract text can be placed before or after that sentence to create prompt-response examples.

The same causal language model can then learn several directions:

- text to cell: generate a ranked gene sequence from a cell type or condition;
- cell to text: predict labels or generate a biological summary;
- cell to cell: complete a partial gene sequence;
- generated sentence to expression: apply a dataset-specific linear model from log rank to normalized abundance.

The key novelty is the representation and task framing, not a new transformer architecture. C2S turns transcriptomic modeling into standard next-token prediction and can therefore reuse GPT-2, Pythia, Hugging Face training, prompt templates, and autoregressive generation.

### Evaluation

The paper evaluates C2S on immune-tissue, cytokine-stimulation, multi-tissue, L1000, and GTEx data.

#### Transformation Robustness

On the PBMC example, rank-based reconstruction reports Pearson $R=0.934$, Spearman $R=0.815$, and $R^2=0.815$. Original and reconstructed cells substantially overlap in UMAP space. Across 127 datasets, the appendix reports mean Pearson $R=0.91$, Spearman $R=0.83$, and $R^2=0.81$. The local images support strong but visibly imperfect, dataset-dependent reconstruction.

#### Conditional Cell Generation

On immune-cell generation, C2S Pythia-160m reports the best values in Table 1 against scGen, scVI, scDiffusion, and the paper's scGPT recreation: k=10 accuracy $0.2746 \pm 0.0073$ and Gromov-Wasserstein distance $54.3040 \pm 0.3410$. For ten unseen cytokine perturbation combinations, C2S reports Pearson $R=0.9241 \pm 0.0002$ and top-20 differential-expression Spearman $R=0.9752 \pm 0.0016$.

Prompt wording still matters. On cell-type generation, k=10 accuracy falls from $0.2746 \pm 0.0073$ with seen prompts to $0.2083 \pm 0.0065$ with semantically similar unseen prompts (`paper.md:580-582`).

#### Cell Label Prediction

C2S GPT-2 Large reports the best partial- and full-label accuracy/AUROC values across cytokine stimulation, L1000, and GTEx in Table 3. The task remains difficult: full combinatorial-label accuracy is only 0.149, 0.202, and 0.152 on the three datasets, respectively. The stronger partial-label scores show that the model often recovers some metadata components without producing the complete exact label.

#### Abstract Generation

For 19 held-out studies, C2S-generated abstracts are more aligned with their matching original abstracts in embedding space than the tested GPT-3.5, Mixtral, Mistral, and unfine-tuned GPT-2 baselines. C2S obtains MMD 0.198 versus 0.298 or worse for the listed alternatives, and only the C2S rows show significant matching-versus-nonmatching similarity tests in Table 4.

This evaluation measures semantic embedding alignment, not strict factual correctness. The appendix examples include summaries that diverge from the corresponding original study details (`paper.md:655-681`), so abstract generation should be treated as exploratory hypothesis or caption generation rather than validated scientific reporting.

### What the Code Snapshot Verifies

The current `vandijklab/cell2sentence` snapshot directly implements:

- conversion of an `AnnData` matrix into ranked, uppercase nonzero-gene sentences;
- Arrow datasets carrying cell sentences and optional metadata;
- dataset-level rank/expression benchmarking and expression reconstruction helpers;
- prompt formatting for current cell-type generation and prediction tasks;
- response-only or all-token causal-LM loss using Hugging Face `Trainer`;
- batched conditional generation and cell-type prediction wrappers.

The package behavior agrees with the central representation and modern C2S workflow. However, the repository README now centers the later C2S-Scale framework, so it is not a frozen artifact of the ICML experiments.

### Reproducibility

**Available:** primary paper PDF/Markdown, ten linked figure images, a public code snapshot, core conversion/reconstruction/training/generation APIs, prompt assets, and package tests.

**Not found:** the paper-exact Scanpy preprocessing scripts, ICML experiment launchers and hyperparameter configs, the baseline implementations, table/metric generation code, abstract-generation evaluation pipeline, and a complete set of released checkpoints tied to every reported result. No supplementary Markdown was available.

The current code's default fine-tuning loss masks prompt tokens, matching the paper's pretrained-model fine-tuning regime. The paper's randomly initialized pretraining instead computes loss over prompt and label; this is supported by a flag but not bound to a preserved ICML run. Likewise, paper inference settings (`top_p=0.9`, temperature 0.7) must be supplied by the caller.

Overall, the central C2S idea is understandable and implementable from the paper and package, but exact reproduction of Tables 1-4 is not possible from this snapshot alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
