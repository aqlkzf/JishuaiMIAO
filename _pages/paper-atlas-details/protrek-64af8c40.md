---
layout: default
permalink: /paper-atlas/protrek-64af8c40/
title: "ProTrek"
nav: false
description: "ProTrek 为同一个蛋白构造三种表示：氨基酸序列、由 Foldseek 压缩出的 3Di 结构序列、自然语言功能描述。训练时让同一蛋白的三种表示互相靠近、不同蛋白的表示分开。得到统一向量空间后，任意一种模态都能查询另外两种模态，也能进行同模态近邻搜索，因此形成序列、结构、文字之间的九种检索方向。"
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
    <h1>ProTrek</h1>
    <p>A trimodal protein language model enables advanced protein searches</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-025-02836-0" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ProTrek">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/westlake-repl/ProTrek" target="_blank" rel="noopener noreferrer" aria-label="Open code for ProTrek">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ProTrek 方法解读：把序列、结构和功能文字放进同一个检索空间

### 一句话理解

ProTrek 为同一个蛋白构造三种表示：氨基酸序列、由 Foldseek 压缩出的 3Di 结构序列、自然语言功能描述。训练时让同一蛋白的三种表示互相靠近、不同蛋白的表示分开。得到统一向量空间后，任意一种模态都能查询另外两种模态，也能进行同模态近邻搜索，因此形成序列、结构、文字之间的九种检索方向。

### 1. 三种模态各自表达什么

- sequence 是原始氨基酸串，650M 版本用 ESM-2 编码。
- structure 不是直接输入三维坐标，而是先用 Foldseek 把局部三维环境离散成 3Di token 序列，再交给约 150M 的 ESM/BERT-style 序列网络。
- text 是 UniProt 功能描述，以 PubMedBERT 编码。

三个编码器最后都通过线性层投影到 1024 维，并做 L2 归一化。直接代码显示，`protein_encoder.py:88-90`、`structure_encoder.py:79-81` 和 `text_encoder.py:82-83` 均取首 token 的 hidden state 再投影；这与旧分析中“序列/结构 mean pooling”的描述不符，应以当前源码为准。

设三种单位向量为 $z_s,z_r,z_t$，跨模态相似度就是内积；模型再除以可学习温度 $\tau$：

$$
\operatorname{score}(a,b)=\frac{z_a^\top z_b}{\tau}.
$$

分数适合排序，但不是结合概率、GO 置信度或可校准的功能概率。

### 2. 六个方向的对比学习

一个 batch 中第 $i$ 个序列、结构和文字来自同一蛋白。以序列查询文字为例，相似度矩阵是

$$
S_{ij}^{s\to t}=\frac{z_{s,i}^{\top}z_{t,j}}{\tau},
$$

对角线 $i=j$ 是正配对，其余 batch 样本是负例。InfoNCE/交叉熵要求正确文字在该行得分最高。ProTrek 对三个模态的每一对都做双向学习：sequence↔structure、sequence↔text、structure↔text，共六项损失。

当前 `protrek_trimodal_model.py:229-297` 确实枚举六个方向，跨 GPU 汇总候选表示，并对相似度矩阵使用对角标签做交叉熵。温度在 `141-147` 注册为可学习参数。因而旧 `doc_code.md` 所说“InfoNCE loss NOT FOUND”过强：损失函数存在；真正缺少的是可复现论文训练的完整数据加载、配置和启动入口。

### 3. 为什么还保留 MLM

只优化跨模态对齐，编码器可能过度压缩成检索捷径，削弱对氨基酸和 3Di token 本身的识别。论文因此在 sequence 与 structure 两个编码器上加入 masked language modeling：遮住部分 token，让模型恢复原 token。

最终训练目标是六项 InfoNCE 与两项 MLM 的平均：

$$
\mathcal L=\frac18\left(\sum_{m=1}^{6}\mathcal L_{\mathrm{InfoNCE}}^{(m)}+
\mathcal L_{\mathrm{MLM}}^{seq}+\mathcal L_{\mathrm{MLM}}^{str}
\right).
$$

代码 `protrek_trimodal_model.py:299-314` 在 `use_mlm_loss` 开启时计算两项 token 交叉熵，再与所有方向损失取简单平均。论文补充图显示两类损失在约 2,500 step 后达到相近量级，这是采用等权平均的经验依据，并非严格证明每项任务贡献相等。

### 4. 近四千万训练对如何形成

第一部分是约 1,400 万条高质量 SWISS-PROT 蛋白—文本对。第二部分从约 3 亿条 TrEMBL50 候选中筛出约 2,500 万对：先用较小的 ProTrek-35M 在高质量数据上学习，再给噪声候选打分并过滤，最终训练 650M 版本。

结构来自 AlphaFoldDB，并经 Foldseek 转成 3Di。文字由 UniProt 子字段组成，论文还使用 GPT-4 改写描述以增加表达多样性。这个数据课程是模型规模优势的重要来源，但发布仓库没有 GPT-4 处理脚本、3 亿候选过滤流水线或最终训练 manifest，因此不能从公共代码精确重建论文训练集。

论文报告 20 张 A100 80GB、batch size 1,280、约十万步和两周训练，并使用 AdamW、warmup 与 cosine schedule。仓库保留了 scheduler 和损失类，但没有将这些组件连成论文使用的端到端训练命令；不能把“类存在”写成“训练已可复现”。

### 5. 为什么统一空间能做九种搜索

三种模态各自都输出 1024 维单位向量，所以查询与数据库只需做最大内积搜索。三种查询乘三种数据库，得到：

- sequence→sequence/structure/text；
- structure→sequence/structure/text；
- text→sequence/structure/text。

跨模态方向直接利用训练过的对齐。同模态搜索虽然没有单独的同模态 InfoNCE，但共享的跨模态语义约束使相似功能的表示靠近。它不是 BLAST 或 TM-align 那样的局部对齐：返回高分说明全局表示相似，不提供残基对应、结构叠合或进化同源证据。

### 6. 本地推理和数据库代码怎样工作

`ProteinEncoder.get_repr()`、`StructureEncoder.get_repr()` 与 `TextEncoder.get_repr()` 分批编码并归一化；`ProTrekTrimodalModel` 负责跨模态打分。结构输入可由 `utils/foldseek_util.py` 调 Foldseek `structureto3di` 从 PDB/CIF 产生。

`scripts/generate_database.py` 将 FASTA 编码为持久化向量和 ID 表，再由 `utils/faiss_index.py` 建 FAISS 内积索引。小库可用 FlatIP，大库用 IVF；查询时 top-k 内积就是统一空间近邻。发布的 demo 进一步用 Gradio、FastAPI 和检索服务器串起前端、embedding 服务与 FAISS 服务。

本地生成脚本会跳过超过 2,048 token 的序列，并带有最多一千万条的实现约束；这与论文训练时最长 512 aa 的随机裁剪以及线上五十亿规模数据库是不同边界。

### 7. 图和实验分别支持什么

图 1 说明统一空间、九种检索与训练数据规模。图 2 的 4,000 个 SWISS-PROT 测试蛋白（与训练集序列同一性低于 50%）配合 100,000 个额外负例，显示 sequence↔text 等跨模态 MAP 显著优于早期多模态模型。MAP 评价排序，不代表文本生成质量。

在同模态/序列—结构搜索中，作者按共享 GO 注释判断正确命中并统计第五个假阳性之前的真阳性。ProTrek 的优势集中在序列/结构相似度较低的 twilight zone；这支持发现功能类似候选，但共享 GO 也可能粗粒度或受注释传播影响。

收敛进化案例用文字从 UniProt50 检索相同酶功能或 CRISPR 类型，再看返回蛋白之间的 TM-score 多样性。低结构相似却共享功能是“可能的功能类似/收敛”证据，不等于仅凭 embedding 已建立独立进化起源。

湿实验从 OMG_prot50 分别用人 UDG 序列和“UDGs remove uracil from DNA”文字检索候选。作者在候选相应活性位点引入类似 Y147A 的替换并融合 Cas9n；十个候选均有可检测胸腺嘧啶编辑，其中排名第一的 V1 在多个位点优于比较编辑器且 indel 更低。这是对检索实用性的强验证，但性能还包含位点替换、融合构建和细胞实验优化，不能归因于 embedding 分数本身。

### 8. 版本和复现边界

论文为 Nature Biotechnology 2025，DOI `10.1038/s41587-025-02836-0`；官方代码 URL 是 `https://github.com/westlake-repl/ProTrek`，MIT 许可。本地源码嵌在较大的归档仓库快照 `206cc19ca89d985245ca204fbc86772e5c2446d0` 中，并非独立官方 Git clone，因此该 commit 是本地来源标识，不应冒充官方 ProTrek release tag。

可复现的主要是：三编码器推理、3Di 转换、自定义 FASTA 数据库生成、FAISS 检索与 demo。不可完整复现的主要是：训练语料构造/GPT-4 改写、TrEMBL50 过滤、论文训练启动配置、全部评测脚本和线上五十亿向量库。模型权重与部分 SWISS-PROT 索引在 Hugging Face 提供，仍需下载外部资产。

还需保留源码事实边界：当前编码器取首 token，不是 mean pooling；结构网络使用 Hugging Face ESM 架构承载 3Di token，论文的“BERT-style”是架构描述，不等于代码调用 `BertModel`；训练损失函数存在，但完整训练流水线缺失。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ProTrek: A Trimodal Protein Language Model Enables Advanced Protein Searches

**Paper**: Su, J., He, Y., You, S., et al. *Nature Biotechnology* (2025)
**DOI**: https://doi.org/10.1038/s41587-025-02836-0
**Code**: https://github.com/westlake-repl/ProTrek
**Web Server**: http://search-protrek.com
**Model Weights**: [ProTrek_650M](https://huggingface.co/westlake-repl/ProTrek_650M), [ProTrek_35M](https://huggingface.co/westlake-repl/ProTrek_35M)

---

### Motivation & Novelty

#### Biological Problem
Proteins are the cell's principal molecular machines. Understanding the sequence–structure–function (SSF) relationship is a central goal of molecular biology. Yet over **30% of UniProt's 200M+ proteins remain unannotated** because they are phylogenetically distant from any characterized homolog. The problem is even more acute for the **5+ billion metagenomic protein sequences** (from MGnify, OMG, NCBI, etc.) that have no functional annotation at all.

#### Limitations of Existing Approaches

| Approach | Examples | Key Limitation |
|----------|----------|----------------|
| Sequence alignment | BLAST, MMseqs2, DIAMOND | Single-modality; local similarity only; miss convergent evolution |
| Structure alignment | TM-align, Foldseek | Single-modality; require 3D structures; miss functional analogs with divergent folds |
| Neural predictors | DeepFRI, ProtNLM | Fixed label vocabularies; cannot process or produce natural language |
| Prior multimodal PLMs | ProtST (~100K pairs), ProteinDT (~100K pairs) | Trained on 2 orders of magnitude less data; poor cross-modal retrieval (MAP < 0.01) |

#### Unique Contributions
1. **Trimodal alignment**: First protein language model jointly modeling all three SSF modalities through bidirectional contrastive learning, creating a unified embedding space.
2. **Nine search tasks**: Enables all 3×3 pairwise retrieval combinations (seq↔str, seq↔txt, str↔txt, plus 3 intra-modal searches).
3. **Scale of training**: ~40M protein–text pairs (14M high-quality SWISS-PROT + 25M noise-filtered TrEMBL50), two orders of magnitude beyond prior work.
4. **Billion-scale search platform**: Web server indexes >5 billion proteins across 7 databases (SWISS-PROT, UniRef50, PDB, OMG, MGnify, NCBI, Global Ocean). Embedding generation required >5 years of A100 GPU time.
5. **Convergent evolution detection**: Global representation learning identifies functionally similar proteins despite divergent sequences/structures — a fundamental limitation of alignment tools.
6. **Wet-lab validation**: ProTrek-discovered UDG analog (V1) outperformed existing thymine base editors (TSBE3 EK, gTBE) in HeLa cell editing experiments.
7. **Downstream impact**: ProTrek scores serve as training data for next-generation models (Pinal, 16B parameters; Evola, 80B parameters) and as evaluation metrics for protein-text alignment research.

---

### Method Overview

#### Architecture
ProTrek uses three dedicated encoders, each specialized for one modality:

```
                    ┌─────────────────────────┐
  AA Sequence ─────>│ ESM-2 (650M) + MeanPool │──> Linear ──> L2-norm ──> e_seq ∈ R^1024
                    └─────────────────────────┘
                    ┌─────────────────────────┐
  3Di Sequence ────>│ ESM-arch (150M) + MeanPool│──> Linear ──> L2-norm ──> e_str ∈ R^1024
                    └─────────────────────────┘
                    ┌─────────────────────────┐
  Function Text ───>│ PubMedBERT (130M) + CLS │──> Linear ──> L2-norm ──> e_txt ∈ R^1024
                    └─────────────────────────┘
```

All three embeddings live in the same 1024-dimensional space. Similarity = temperature-scaled cosine similarity.

#### Training
- **Loss**: 6 InfoNCE losses (bidirectional for seq–str, seq–txt, str–txt) + 2 MLM losses (seq + str encoders). Final loss = simple average of all 8.
- **Data**: 14M SWISS-PROT pairs + 25M filtered TrEMBL50 pairs. Structures from AlphaFoldDB converted to 3Di via Foldseek. Text descriptions paraphrased by GPT-4 for robustness.
- **Two-stage curriculum**: (1) Train 35M model on 14M SWISS-PROT pairs → (2) Use 35M model to score/filter 300M TrEMBL50 pairs → retain 25M → train 650M model on combined 39M.
- **Infrastructure**: 20 NVIDIA A100 80GB GPUs, AdamW (β₁=0.9, β₂=0.98, L₂ decay 0.01), cosine annealing from 4×10⁻⁴ to 4×10⁻⁵ after 2,000 warmup steps, batch size 1,280, ~100K steps, ~2 weeks. Mixed precision + DeepSpeed.
- **Sequence truncation**: Max 512 AA tokens (random crop for longer sequences), max 100 text tokens.

#### Inference
- Encoders produce L2-normalized 1024-d embeddings
- Similarity: $\text{score} = (e_a \cdot e_b) / \tau$ where $\tau$ is the learned temperature
- FAISS maximum inner-product search (MIPS) with FlatIP (<1M entries) or IVF (>1M entries)
- Sub-second query latency over billion-scale databases

---

### Evaluation

#### Datasets & Benchmarks

| Benchmark | Dataset | Task | Metric |
|-----------|---------|------|--------|
| Cross-modal retrieval | 4,000 SWISS-PROT test + 100K negatives (<50% seq id to train) | seq↔txt, str↔txt | MAP |
| Functional retrieval | 4,000 SWISS-PROT test (all-vs-all) | seq↔seq, str↔str, seq↔str | TP count at 5th FP |
| EC annotation | CLEAN enzyme datasets (post-training) | seq→text (EC descriptions) | Match rate (Wilcoxon test) |
| Convergent evolution | UniProt50 (6 EC classes + 6 CRISPR types) | text→seq | Hit rate + TM-score diversity |
| Literature validation | OmlCas9, SlugCas9, dsPETase, SsdA_tox (post-release papers) | seq→txt, txt→seq | Rank accuracy |
| Fine-grained retrieval | CRISPR, deaminase, family, organism categories | text→seq | Hit rate (single: 95.3%, dual: 65.8%) |
| Downstream fine-tuning | 11 tasks (AAV, β-lactamase, fluorescence, stability, etc.) | Classification/regression | Acc, MCC, Spearman |
| Wet-lab validation | UDG analog search → thymine base editors | seq→seq, txt→seq | Editing efficiency, indel rates |

#### Key Results

| Metric | ProTrek | Best Baseline | Fold Improvement |
|--------|---------|---------------|-----------------|
| Seq→Text MAP (global) | 0.233 | 0.007 (ProtST) | 33× |
| Text→Seq MAP (global) | 0.190 | 0.003 (ProteinDT) | 63× |
| Seq→Seq TP hits | 117 avg | 76 (BLASTp) | 1.5× |
| EC hit rate (6 classes) | 89% exact match | — | Comparable to CLEAN (NS) |
| CRISPR hit rate (6 types) | 67% avg (Cas3: 98%, Cas13: 18%) | — | Novel capability |
| Single-cat fine-grained | 95.33% | — | Novel capability |
| Speed (100 queries vs UniRef50) | 8.96 ± 0.58 s | 1506 s (Foldseek) | 168× faster |

#### Downstream Fine-Tuning (11 tasks)
ProTrek surpasses ESM-2 and ProtST on most tasks and is comparable to ESM-3 (which has ~2× ProTrek's parameters). Particular strengths in binding site detection, subcellular localization, and structural similarity prediction.

#### Wet-Lab Validation
- V1 protein (top-ranked by both seq→seq and txt→seq): ~60% thymine editing at Dicer 1 T5 vs. ~30% for TSBE3 EK and gTBE
- V1 achieves up to 80% editing at site 14 T7/T11
- V1 shows lower indel frequencies at Dicer 1 (~7% vs ~25%) and site 14 (~15% vs ~25%)
- All 10 candidates (S-V1–S-V5, T-V1–T-V5) showed detectable thymine editing after Y147A-analog substitution, confirming functional homology

#### Literature Validation
ProTrek correctly retrieves and annotates proteins from papers published **after** model release:
- **OmlCas9**: Novel Cas9 from ocean microbiome — correctly retrieved from 45M candidates using text description
- **dsPETase**: PET-degrading enzyme — correct functional annotation via seq→txt retrieval
- **SsdA_tox**: Toxin protein — high-ranking text retrieval

---

### Acknowledged Limitations

1. **Natural proteins only**: Trained exclusively on natural proteins; may not perform well on de novo designed proteins.
2. **Subtle variations insensitive**: Cannot precisely predict specific quantitative values (e.g., fluorescence wavelengths, exact stability) — analogous to AlphaFold2's limitations. Requires task-specific fine-tuning via ColabProTrek.
3. **Underrepresented families**: Some protein families (e.g., Cas13) have low representation in training data, leading to reduced retrieval accuracy (18% vs 98% for Cas3).
4. **Structure encoder weaker**: The 150M structure encoder consistently underperforms the 650M sequence encoder, likely due to smaller model size and lack of pretraining.

---

### Reproducibility Assessment

#### Rating: 4/5 (Good)

#### What You Can Reproduce
| Component | Available | Location |
|-----------|-----------|----------|
| Model weights (650M, 35M) | ✓ | HuggingFace |
| Inference code | ✓ | GitHub repository |
| Custom database construction | ✓ | `scripts/generate_database.py` |
| Web demo (Gradio + FastAPI) | ✓ | `demo/` |
| SWISS-PROT FAISS indices | ✓ | HuggingFace datasets |
| ColabProTrek fine-tuning | ✓ | Google Colab notebook |
| Foldseek 3Di conversion | ✓ | `utils/foldseek_util.py` + `bin/foldseek` |

#### What You Cannot Reproduce
| Component | Status | Impact |
|-----------|--------|--------|
| Training code (loss, optimizer, data loader) | ✗ Not provided | Cannot retrain model |
| GPT-4 text paraphrasing pipeline | ✗ Prompt only in paper | Cannot reproduce data augmentation |
| TrEMBL50 filtering pipeline | ✗ Not provided | Cannot reproduce dataset construction |
| Evaluation scripts (MAP, GO, EC) | ✗ Not provided | Cannot verify benchmark numbers independently |
| Wet-lab protocols | ✗ Require HeLa cells + HTS | Biology lab required |

#### Hardware Requirements
- **Inference (650M model)**: GPU with ≥8 GB VRAM
- **Database generation**: Multi-GPU recommended (parallel encoding via custom MPR framework)
- **Full training reproduction**: 20× A100 80GB GPUs, ~2 weeks

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
