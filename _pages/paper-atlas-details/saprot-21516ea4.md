---
layout: default
permalink: /paper-atlas/saprot-21516ea4/
title: "SaProt"
nav: false
wide: true
description: "SaProt 的关键不是另造一种三维神经网络，而是先用 Foldseek 把每个残基周围的局部几何环境离散成一个 3Di 字母，再把“氨基酸字母”和“结构字母”合成一个 token。这样，普通双向 Transformer 读一条一维序列时，就能同时看到序列身份和结构环境。2025 年正式论文又在这个模型之上加入 ColabSaprot 和 SaprotHub，让非机器学习用户通过轻量 adapter 训练、分享、续训和聚合任务模型。"
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
      <span>Protein &amp; Sequence Models</span>
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>SaProt</h1>
    <p>Democratizing protein language model training, sharing and collaboration</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-025-02859-7" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SaProt">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/westlake-repl/Saprot" target="_blank" rel="noopener noreferrer" aria-label="Open code for SaProt">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SaProt：把蛋白质结构压缩成语言模型能读的字母

### 一句话理解

SaProt 的关键不是另造一种三维神经网络，而是先用 Foldseek 把每个残基周围的局部几何环境离散成一个 3Di 字母，再把“氨基酸字母”和“结构字母”合成一个 token。这样，普通双向 Transformer 读一条一维序列时，就能同时看到序列身份和结构环境。2025 年正式论文又在这个模型之上加入 ColabSaprot 和 SaprotHub，让非机器学习用户通过轻量 adapter 训练、分享、续训和聚合任务模型。

### 为什么不用原子坐标直接训练

只看氨基酸序列的蛋白语言模型能学习进化规律，却看不到同一氨基酸在螺旋、折叠核心或界面中的不同几何角色。直接输入三维坐标虽然信息丰富，但坐标网络计算重，并且在数千万个 AlphaFold2 预测结构上预训练时会受到预测误差、旋转平移处理和过拟合的影响。

SaProt 选择一个折中：结构先被压缩为离散字母，后续仍使用成熟的 ESM/BERT 式 Transformer。它牺牲原子级连续几何细节，换来规模化训练、标准 token 化以及和序列模型生态的兼容性。

### 第一步：从三维结构生成 3Di 序列

Foldseek 为每个残基分配 20 种 3Di 状态之一。3Di 描述的是一个残基与其空间邻居之间的局部几何关系，而不是简单的二级结构标签；相同氨基酸处在不同三维环境中可以得到不同 3Di 字母。于是长度为 $n$ 的蛋白得到两条等长序列：

$$
(s_1,s_2,\ldots,s_n),\qquad (f_1,f_2,\ldots,f_n),
$$

其中 $s_i$ 是第 $i$ 个氨基酸，$f_i$ 是对应 3Di 字母。本地 `utils/foldseek_util.py` 调用 Foldseek 的 `structureto3didescriptor`，读取氨基酸序列和 3Di 序列，再逐位拼接。

AlphaFold2 结构不是处处同样可靠。工具可读取 B-factor 栏中的 pLDDT，将低于阈值（README 示例和默认实现使用 70）的结构字母替换成 `#`。因此 `M#` 表示“知道这里是甲硫氨酸，但不信任其局部结构”，避免模型把低置信预测当成真实几何。

### 第二步：构造结构感知字母表

氨基酸集合和 3Di 集合都加入未知/遮蔽符号 `#`：

$$
\mathcal{A}_{SA}=(\mathcal V\cup\{\#\})\times(\mathcal F\cup\{\#\}),
\qquad |\mathcal{A}_{SA}|=21\times21=441.
$$

每个位置由两个字符组成，例如 `Md` 表示氨基酸 M 位于 3Di 状态 d；`M#` 只有序列信息，`#d` 只有结构信息，`##` 两者都被遮蔽。441 是论文定义的生物学组合词表；Hugging Face tokenizer 的实际输出维度还包含起止、padding、mask 等特殊 token，因此 README 示例中的 logits 最后一维是 446，二者并不矛盾。

这种表示的重点是“乘积 token”，不是把氨基酸 embedding 与结构 embedding 分别编码后相加。局部序列—结构组合从输入层就拥有独立词项，Transformer 随后通过双向 self-attention 建模长程上下文。

### 第三步：掩码语言模型预训练

SaProt 从 AlphaFold DB 的约 2.14 亿条结构中按 50% 序列一致性过滤，得到约 4000 万条结构感知序列，从头预训练 35M 和 650M 模型；正式论文还介绍了 1.3B 版本。训练目标与 BERT/ESM-2 相同：遮住部分输入 token，让模型从其余上下文恢复原 token：

$$
\mathcal L_{MLM}=-\sum_{i\in\mathcal M}\log p(x_i\mid x_{\setminus\mathcal M}).
$$

但 SaProt 的遮蔽具有结构语义。高置信位置可遮住氨基酸而保留 3Di，即从局部结构和上下文预测残基；低置信位置的 3Di 已变成 `#`，模型只能依靠序列上下文。本地 `dataset/saprot/saprot_lm_dataset.py` 实现 15% 位置采样以及 80% mask、10% 随机替换、10% 保持不变，`model/saprot/saprot_lm_model.py` 用交叉熵只监督被选位置。

论文图 1b 中“输入 `#c`，预测 `Kc`”容易被误读为只预测氨基酸。训练标签实际上是完整 SA token；保留结构字母 c 会把几何环境作为条件，输出同时恢复氨基酸—结构组合。

### 从基础模型到多种任务

预训练 backbone 可接不同任务头：蛋白级分类/回归、残基级预测、PPI、突变效应和逆折叠。本地代码分别提供 classification、regression、contact、annotation、PPI、mutation 和 inverse-folding 类，并通过 YAML 配置模型、数据与优化器。

#### 零样本突变评分

标准序列模型用突变与野生型残基的对数概率比。SaProt 一个氨基酸对应 21 个可能的结构后缀，因此代码先对所有结构状态边缘化：

$$
S=\sum_{t\in T}\left[
\log\sum_{f\in\mathcal F'}p(s_t^{mut}f\mid x_{\setminus T})-
\log\sum_{f\in\mathcal F'}p(s_t^{wt}f\mid x_{\setminus T})
\right].
$$

`model/saprot/saprot_foldseek_mutation_model.py` 正是把某个氨基酸对应的一段结构 token 概率求和，再取突变/原始概率比。可选 MSA 模式在代码中以 0.4 的模型分数和 0.6 的 MSA log-prior 混合；这个硬编码配比属于具体实现选择，不应泛化成所有 SaProt 推断的定义。

#### 逆折叠

给定结构序列，把所有氨基酸写成 `#`，模型一次前向传播同时预测全部残基。`SaProtIFModel.predict()` 支持 argmax 或 multinomial 采样。它不是 ProteinMPNN 那样逐残基自回归，因此论文报告约 16 倍推断加速；代价是位置间生成依赖只通过一次共享上下文体现，而不是把已生成残基逐步反馈。

#### 有监督微调与 PPI

蛋白级任务通常取 backbone 表示接分类/回归头。PPI 代码分别编码两条蛋白，将池化表示拼接后分类；它不是显式的复合物结构预测器，也不输出原子界面。任务表现依赖输入是否有可靠结构、数据切分和任务头训练，不能仅凭“使用 SaProt”保证优于序列模型。

### ColabSaprot 与 SaprotHub 如何协作

正式论文的第二层贡献是降低使用门槛。ColabSaprot 把环境安装、数据处理、训练、推断和分享包装进 Google Colab。微调时冻结 SaProt backbone，只训练插入 attention/MLP 的 LoRA adapter 和任务头。低秩更新可写为：

$$
W'=W+BA,
$$

其中主权重 $W$ 不变，$A,B$ 的维度远小于 $W$。论文称 adapter 约占完整模型参数的 1%，所以可单独上传、下载和管理。

SaprotHub 存放这些任务 adapter，而非用户的私有训练数据。已有 adapter 可以直接推断，或作为起点在小型私有数据上继续训练。模型聚合实验把训练集分成五份分别训练：回归任务平均多个模型输出，分类任务多数投票。图 2e 显示聚合优于单个子集模型，但这只是特定模拟设置，不能证明任意来源、任意标签定义的 adapter 都可安全组合。

### 论文证据怎样读

图 1a–c 从左到右给出完整机制：20+1 个氨基酸状态与 20+1 个 3Di 状态形成 441 个 SA token；token 经 embedding 和双向 Transformer 后接任务头；同一 backbone 可支持多种任务。图 1d 汇总 14 个任务，结构可用时 SaProt 整体优于 ESM-2 和 ProtBert。零样本任务中，正式论文报告 Mega-scale 0.574 对 0.478、ProteinGym 0.457 对 0.414、ClinVar 0.909 对 0.862。跨任务雷达图混合了相关系数、准确率、Fmax 等不同指标，只能逐轴比较同一任务，不能把多边形面积当成统一总分。

图 1e 比较逆折叠：SaProt 用一次并行预测把推断时间从 ProteinMPNN 的 633.49 秒降到 39.33 秒，但序列恢复率和结构指标略低。这里展示的是速度—质量权衡，不是全面取代自回归设计模型。

图 2a–d 描述 Colab 和 adapter 协作流程；图 2e、f 分别支持聚合和小数据续训；图 2g 是 12 名无 ML 背景生物研究者与一名 AI 专家的用户研究。多数任务表现相近，eYFP 上生物研究者使用了 SaprotHub 已有的更强任务模型，而专家从基础模型开始，因此该项不是同一起点的能力对照，论文也明确说明了这一设置。图 2h 展示逆折叠实例的结构重建，不等同于湿实验功能验证。

论文还报告社区湿实验案例：木聚糖酶前 20 个预测中 13 个活性提高；TDG 前 20 个中 17 个提高编辑效率；GFP 500 万个双突变候选中选择的前 9 个有 7 个荧光增强。这些结果支持具体筛选流程的实用性，但样本经过 top-k 选择，没有给出全突变空间的随机对照命中率，不能据此推断所有蛋白或所有 SaProt 分数都有相同成功率。

### 本地代码与正式论文的对应边界

本地目录是 SaProt 核心仓库快照，包含结构转 token、MLM 数据集、35M/650M 权重接口、下游任务、LoRA 封装和训练脚本。它对核心 SAA、pLDDT mask、突变边缘化与逆折叠提供直接实现证据。

但正式论文同时描述 ColabSaprot v1/v2、SaprotHub 搜索/分享服务、1.3B 模型、社区模型集合、用户研究和湿实验流程。Colab notebook 与 Hub 服务属于另一个 SaProtHub 仓库/在线资源，本地快照没有完整覆盖；预训练 4000 万结构序列、下游 LMDB、模型权重和 Foldseek 可执行文件也需外部下载。配置中的绝对数据/权重路径不能在新机器上直接工作。

因此本地代码可复现“给定权重和已准备数据后的核心训练/微调/推断”，不能单独复现完整预训练、在线平台、社区状态或湿实验。README 还持续包含早期 ICLR 2024 SaProt 论文与后续模型更新信息；解释正式 2025 Nature Biotechnology 论文时，应区分核心模型版本、1.3B 后续版本和在线平台版本。

### 使用时最容易忽略的边界

- 结构 token 来自预测结构时受 AlphaFold2 误差限制；低 pLDDT masking 只能降低而不能消除误差传播。
- 3Di 是离散局部描述，不保留完整原子坐标、配体、水分子或所有远程几何信息。
- 35M/650M 模型的 AA-only 模式需要专门微调；README 明确提醒其冻结 embedding 主要适用于 SA 输入。1.3B 才专门增强了 AA-only 能力。
- 结构相似蛋白可能跨越低序列一致性切分；评价必须检查具体数据切分。正式论文采用更严格的结构切分讨论，但本地各 YAML/数据集来源并不自动保证所有用户数据遵循同一规则。
- Hub adapter 的共享不泄露原始训练数据，不等于不存在模型反演、标签偏差、许可或数据治理风险。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SaProt: Democratizing Protein Language Model Training, Sharing and Collaboration

**Paper**: Su et al., *Nature Biotechnology*, 2025
**DOI**: https://doi.org/10.1038/s41587-025-02859-7
**Code**: https://github.com/westlake-repl/Saprot
**License**: MIT

---

### Motivation & Novelty

#### Biological Problem
Proteins are central to virtually all biological processes, yet deciphering protein structure–function relationships remains challenging. While protein language models (PLMs) have driven advances in function prediction, leveraging these models requires deep machine learning expertise—a barrier for most biology researchers. Existing tools like ColabFold democratized structure prediction but do not support **custom model training** for function prediction tasks.

#### Limitations of Existing Approaches
1. **ESM-2** and other PLMs use amino acid (AA) sequences only, ignoring structural context that is critical for function
2. Training/deploying billion-parameter PLMs requires ML expertise, GPU resources, and code debugging
3. No platform exists for biologists to **share, reuse, and collaboratively refine** fine-tuned PLMs
4. Incorporating explicit 3D coordinates causes scalability and overfitting problems when training on AlphaFold2-predicted structures

#### Unique Contributions
1. **Structure-Aware Alphabet (SAA)**: A novel protein representation combining AA identity with Foldseek 3Di structural tokens (20 AA × 20 3Di + mask = 441 tokens), encoding both sequence and local geometry in a single token
2. **SaProt Model**: A bidirectional Transformer PLM (35M/650M/1.3B parameters) pretrained on 40M AlphaFold2-derived SA sequences with masked language modeling
3. **ColabSaprot**: A Google Colab-based platform enabling biology researchers to train, fine-tune, and deploy PLMs without ML expertise
4. **SaprotHub**: A community repository for storing, sharing, searching, and collaboratively developing fine-tuned SaProt models via lightweight LoRA adapters
5. **Open Protein Modeling Consortium (OPMC)**: A community initiative for collaborative protein language modeling

---

### Method Overview

#### Algorithmic Framework
1. **Structure Encoding**: Protein 3D structures are discretized into 3Di tokens using Foldseek, producing per-residue structural letters from a 20-letter alphabet
2. **SA Token Construction**: Each residue is represented as a pair `(AA, 3Di)` — e.g., `Md` means methionine with 3Di class `d`. The SA vocabulary is $\mathcal{V} \times \mathcal{F}$ with size $21 \times 21 = 441$ (including mask `#`)
3. **Masked Language Modeling**: 15% of SA tokens are masked following BERT protocol (80% `[MASK]`, 10% random, 10% unchanged), and the model learns to reconstruct them
4. **pLDDT-based Masking**: For AlphaFold2-predicted structures, regions with pLDDT < 70 have their structural tokens replaced with `#`, so the model relies only on AA context for uncertain regions
5. **Adapter-based Fine-tuning (LoRA)**: Lightweight low-rank matrices are inserted into attention/MLP layers, enabling parameter-efficient fine-tuning (~1% of parameters) while keeping the backbone frozen

#### Key Technical Components
- **Architecture**: ESM-2 Transformer with expanded embedding layer (441 SA tokens vs 20 AA tokens)
- **Pretraining Data**: ~40M protein SA sequences from AlphaFold DB, filtered at 50% sequence identity
- **Training**: AdamW optimizer ($\beta_1=0.9$, $\beta_2=0.98$), weight decay 0.01, warmup to $4 \times 10^{-4}$ over 2,000 steps, linear decay from 150K to 1.5M steps
- **1.3B Model**: Constructed by stacking two copies of the pretrained 650M model (progressive stacking), with 30% of training sequences converted to AA-only format

#### Downstream Tasks
- **Supervised**: Classification (localization, metal-ion binding), regression (thermostability, fitness), residue-level (contact prediction), protein-protein interaction
- **Zero-shot**: Mutation effect prediction via log-odds ratio adapted for SAA (Equation 2: sum over all 3Di tokens for each AA)
- **Inverse Folding**: Structure-to-sequence prediction by masking all AA tokens and predicting residues in a single forward pass

---

### Evaluation

#### Datasets
| Task Type | Datasets | Metrics |
|-----------|----------|---------|
| Zero-shot mutation | ProteinGym, ClinVar, Mega-scale | Spearman ρ, AUC |
| Supervised classification | DeepLoc (2-class, 10-class), MetalIonBinding | Accuracy |
| Supervised regression | Thermostability, Fluorescence, Stability, AAV, β-lactamase | Spearman ρ, MSE |
| Residue-level | Contact prediction | Precision@L |
| Protein-protein interaction | HumanPPI | Accuracy |
| Sequence design | CATH inverse folding | Recovery rate |

#### Data Splitting Strategy
A notable methodological contribution is the adoption of **structure-based data splitting** (following ProteinShake) instead of the traditional sequence-identity-based splitting. Using a 70% LDDT structural similarity threshold provides more stringent evaluation because protein structures are more conserved than sequences — two proteins with low sequence identity may still have similar structures, making sequence-based splits potentially leak structural information. For tasks with only sequence data (single-protein variant datasets), original splits from the literature are retained.

#### Key Results
- **Zero-shot mutation**: SaProt substantially outperforms ESM-2 on Mega-scale (0.574 vs 0.478), ProteinGym (0.457 vs 0.414), and ClinVar (0.909 vs 0.862)
- **Supervised tasks**: Consistent improvement over ESM-2 and ProtBert across 14 diverse tasks when structural information is available
- **Inverse folding**: Competitive with ProteinMPNN while achieving 16× faster inference (single forward pass vs autoregressive generation)
- **Wet lab validation**:
  - Xylanase: 13/20 predicted variants showed enhanced activity (R59S: 2.55× improvement)
  - TDG: 17/20 variants enhanced editing efficiency; three achieved ~2× improvement
  - GFP: 7/9 predicted double-site variants enhanced fluorescence (one reaching >8× wild-type)
- **User study**: 12 biology researchers (no ML background) achieved performance comparable to an AI expert using ColabSaprot

#### Biological Validation
The collaborative approach is validated by showing:
- **Model aggregation** (ensemble of independently trained adapters) improves over individual models
- **Continual learning** from shared models on SaprotHub outperforms training from scratch, especially with limited data
- eYFP model achieving Spearman ρ = 0.94 on independent test set

---

### Reproducibility Assessment

**Rating: 4/5**

#### Strengths
- Complete open-source codebase (MIT license) with clear directory structure
- YAML-based configuration system for all tasks
- Model checkpoints hosted on Hugging Face (35M, 650M, 1.3B)
- ColabSaprot notebooks for interactive training/inference
- LMDB format for efficient data storage with clear data loading pipeline
- Standard PyTorch Lightning training framework

#### Potential Blockers
1. **Pretraining compute**: 3 months on 64 NVIDIA A100 80G GPUs (not reproducible for most labs, but pretrained weights are available)
2. **Foldseek binary dependency**: Requires specific Foldseek binary for structure encoding (provided in `bin/` directory)
3. **LMDB datasets**: Not all downstream task LMDB files are included; need to generate from raw data
4. **Hardcoded paths**: Some config files reference absolute paths (e.g., GPU device settings, weight paths)
5. **Version sensitivity**: Specific versions required (torch 1.13.1, transformers 4.28.0) — newer versions may cause compatibility issues

#### Data Availability
- Pretraining dataset: https://huggingface.co/datasets/westlake-repl/AF2_UniRef50
- Downstream datasets: https://huggingface.co/SaProtHub
- Model weights: https://huggingface.co/SaProtHub

---

### Key Concepts for Understanding This Paper

| Concept | One-Paragraph Explanation |
|---------|--------------------------|
| **Foldseek 3Di tokens** | Foldseek encodes local protein backbone geometry into one of 20 discrete structural letters per residue using vector quantization of torsion angle features between consecutive residues. This converts 3D structure into a 1D sequence that can be tokenized like amino acids. |
| **Structure-Aware Alphabet (SAA)** | The Cartesian product $\mathcal{V} \times \mathcal{F}$ creates a 441-token vocabulary where each token encodes both the amino acid identity and local structural environment (e.g., `Md` = methionine in structure class `d`). The `#` mask token for either component enables flexible partial masking. |
| **Masked Language Modeling (MLM)** | A self-supervised pretraining objective where 15% of input tokens are masked and the model learns to predict them from context. This forces the model to learn evolutionary and structural constraints governing protein sequences. |
| **pLDDT confidence masking** | AlphaFold2 provides per-residue confidence scores (pLDDT). Regions with pLDDT < 70 have unreliable predicted structures, so their 3Di tokens are replaced with `#` to prevent the model from learning spurious structural patterns. |
| **Log-odds ratio for mutation scoring** | A zero-shot approach where the model predicts how likely each amino acid is at a masked position. The mutation effect score is $\log(P_{mut}/P_{wt})$: positive means the model "prefers" the mutant, suggesting it may be tolerated or beneficial. |
| **LoRA adapters** | Low-Rank Adaptation inserts small trainable matrices into attention layers while freezing the backbone. This enables efficient fine-tuning (~1% of parameters) and makes model sharing practical via small adapter files. |
| **LMDB data format** | Lightning Memory-Mapped Database is a key-value store that maps integer keys to serialized JSON entries. It supports fast random access for large protein datasets without loading everything into memory. |
| **Non-autoregressive inverse folding** | Unlike ProteinMPNN which generates residues one-by-one conditioned on previous outputs, SaProt predicts all residues simultaneously in a single forward pass, trading some accuracy for ~16× speedup. |
| **Structure-based data splitting** | Instead of splitting train/test by sequence identity (common in prior work), SaProt adopts ProteinShake's structure-based splitting (LDDT threshold), providing a more stringent evaluation of generalization since structure is more conserved than sequence. |
| **Model aggregation via adapters** | Multiple researchers independently fine-tune LoRA adapters on their own data. At inference, predictions from all adapters are ensembled (mean for regression, majority vote for classification) without sharing any training data. |

---

### Cross-References
- Detailed methodology: doc_method.md
- Code audit and discrepancies: doc_code.md
- Figure analysis: figure_analysis.md

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
