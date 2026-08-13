---
layout: default
permalink: /paper-atlas/erast-b7e4c8bc/
title: "ERAST"
nav: false
description: "ERAST 并不是用一个更大的模型直接取代 BLAST。它把同源序列搜索拆成三个可分别优化的环节：先用已有生物学标签缩小或调整候选范围，再用序列语言模型向量做快速召回，最后用序列对分类器 EHSM 判断候选与查询属于同一家族、超家族、折叠，还是不同折叠。论文的核心工程主张是：昂贵的十亿级数据库向量可以保持不动，而较小的重排器可以随新数据更新。"
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
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>ERAST</h1>
    <p>Scalable homology detection with ERAST</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-026-03051-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ERAST">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/TencentAILabHealthcare/ERAST" target="_blank" rel="noopener noreferrer" aria-label="Open code for ERAST">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ERAST 方法解读：把同源搜索拆成“召回、筛选、重排”

### 一句话理解

ERAST 并不是用一个更大的模型直接取代 BLAST。它把同源序列搜索拆成三个可分别优化的环节：先用已有生物学标签缩小或调整候选范围，再用序列语言模型向量做快速召回，最后用序列对分类器 EHSM 判断候选与查询属于同一家族、超家族、折叠，还是不同折叠。论文的核心工程主张是：昂贵的十亿级数据库向量可以保持不动，而较小的重排器可以随新数据更新。

### 1. 为什么要分三段

单纯依赖序列比对，远缘同源的序列相似度可能太低；单纯依赖语言模型向量，又会把“整体表示相近”误当成精确的进化层级关系。更现实的问题是数据库规模：论文汇集 UniParc、UniRef90、UniRef50、Swiss-Prot 和 RefSeq，覆盖超过十亿条蛋白质和核酸序列。若每次改进编码器都重算所有数据库向量，更新成本非常高。

因此 ERAST 将“数据库编码器”和“查询-候选重排器”解耦。图 1 把流程画成三个阶段：preretrieval filtering、vector retrieval、postretrieval reranking。这个分解比某一个具体模型更重要，因为每段解决不同错误：标签过滤提高候选先验，向量检索保证召回速度，EHSM 改善顶部名次。

### 2. 第一段：蛋白质 Pfam 信息先行

蛋白质模式下，代码读取 HMMER/Pfam 的家族与 clan 标注。设查询的 clan 集合为 $C_q$，候选的集合为 $C_t$；只要 $C_q\cap C_t\ne\varnothing$，候选就被提到向量结果前部。在这些 clan 匹配项内部，代码再把 Pfam family 匹配项提前。

这里应把论文系统和公开代码区分开。论文把该步骤称为 preretrieval filtering，服务端可以据元数据限制检索范围；公开的 `pipeline/utils.py:109-119` 则是在完整余弦排序已经产生后执行稳定重排，并把 clan 匹配段长度保存为 `lengths[i]`。它没有从本地矩阵乘法中省掉候选计算，因此公开脚本更准确地说是“检索后按 Pfam 先验前移”。

另一个代码边界是 `pipeline/utils.py:102-107`：`clan` 无条件加入集合。如果输入 JSON 用 `null` 表示无 clan，多条序列可能因共同的 `None` 被视为匹配；实际使用前应清洗这一值。

### 3. 第二段：向量召回

蛋白质用 ESM2-650M 的逐残基隐状态做平均池化，得到固定长度向量；核酸编码器由 Caduceus 微调而来，同样输出池化表示。对于查询向量 $q$ 与目标向量 $t_i$，排序依据是余弦相似度：

$$
\operatorname{sim}(q,t_i)=\frac{q^\top t_i}{\lVert q\rVert_2\lVert t_i\rVert_2}.
$$

公开代码 `pipeline/predict.py:23-37` 先逐行归一化，然后用 `np.dot(q_matrix, t_matrix.T)` 计算完整的查询×目标相似度矩阵。因此本地实现的时间和内存随 $N_qN_t$ 增长，适合示例或小规模数据库。

论文中的十亿级结果来自另一套未公开的服务端实现：向量按约一千万条一个 segment 存储，并使用 FAISS 的 IVFPQ+HNSW 索引并行检索。论文和补充材料支持这种架构及其计时结果，但当前代码快照中没有索引构建、分段并行查询或线上数据库文件，不能从本地脚本复现“十亿级、对数级搜索”的系统结论。

### 4. 第三段：EHSM 学习进化层级

EHSM 不是独立编码查询与候选，而是把两条蛋白质序列用分隔符拼接后交给 Ankh-base 分类器。论文写作：

$$
d=|\psi(S_1+S_2)|,
$$

再由三层全连接分类头产生四类输出。四个标签不是任意类别，而是 SCOP 层级距离：

| 标签 | 查询与候选的关系 | 排序优先级 |
|---|---|---|
| 3 | 同 family | 最高 |
| 2 | 不同 family、同 superfamily | 次高 |
| 1 | 不同 superfamily、同 fold | 再次 |
| 0 | 不同 fold | 最低 |

训练集 SCOPe40withScore 含 40,073,628 个训练序列对和 2,434,321 个测试序列对。代码 `erast_training/Protein/training/score_model_trainer.py:43-49` 确认基础模型为 `ElnaggarLab/ankh-base`、任务为四类单标签分类；`pipeline/utils.py:142-165` 对候选批量推理并取 `argmax`。

所谓 hybrid sorting 也可直接从代码读出：`pipeline/utils.py:120-126` 按 3、2、1、0 拼接列表，而同一标签内保持原向量顺序。于是最终排序可写成字典序键

$$
(\hat y_i,\operatorname{sim}(q,t_i)),
$$

先比较预测的进化层级，再用向量相似度打破同类平局。值得注意的是，公开实现 `rerank_batch()` 只重排 `lengths[i]:` 的尾部，clan 匹配前缀保持原顺序；这比“所有候选都送进 EHSM”的概念图更具体。

### 5. 从输入到输出的真实代码路径

1. `pipeline/pfam_scan.py` 调用 HMMER，产生查询和目标的 Pfam JSON。
2. `pipeline/encode.py` 读取 FASTA，以 ESM2 或 Caduceus 生成 `.npy` 向量。
3. `pipeline/predict.py:38-61` 载入向量，计算完整余弦排序；蛋白质模式再读取 Pfam 标签并可选加载 EHSM。
4. `pipeline/utils.py:109-119` 把 clan/family 匹配候选前移；`166-175` 对剩余候选执行四类重排。
5. 输出为 JSONL，每行含一个 query ID 和排好序的 target ID 列表。代码没有输出论文图 1 中展示的概率分数。

核酸模式走不同边界：`predict.py:56-57` 直接返回向量排序，不使用 Pfam 或 EHSM。Caduceus 在 NCBITaxonomic 上以 genus 隔离方式训练/测试，论文报告微平均 genus precision 从 0.507 提升到 0.805；这证明微调表示更有分类结构，但公开仓库没有十亿级核酸索引。

### 6. 图和实验告诉了什么

- 图 2 的 SCOPe40-test 是按 fold 隔离的测试，因此比随机切分更强调分布外泛化。论文报告完整 ERAST 的 P@1 从仅编码器的 0.741 提升至 0.821；消融表明 Pfam 前置与 EHSM 顶部重排共同贡献。
- 图 2e 比较四种重排器：EHSM 仅用序列，却在该测试上达到与 TM-align 相近的顶部精度。这个结论属于特定基准结果，不表示 EHSM 在所有蛋白或多结构域场景都等价于结构比对。
- 图 3 将核酸检索质量与服务端扩展计时并列展示。计时支持论文系统的并行分段设计，但不能作为当前公开 NumPy 实现的复杂度证明。
- 图 4 的 UniRef90 聚类展示了下游用途：把功能未知的 dark cluster 与已注释的 bright cluster 建立联系。聚类方法是 PCA 1280→256、两级 minibatch 聚类和 HDBSCAN；相关聚类代码未在本快照中找到。

### 7. 可复现性边界与代码风险

当前快照 `206cc19ca89d985245ca204fbc86772e5c2446d0` 提供推理脚本、EHSM 训练脚本和 Caduceus 训练代码，但不能直接一键复现论文全系统：

- 十亿级向量数据库、IVFPQ+HNSW 索引、分段并行服务和聚类实现未发布。
- `pipeline/predict.py` 使用 `@torch.no_grad()` 却没有 `import torch`，导入时即会失败。
- `pipeline/encode.py:78` 向只接受三个参数的 `get_embs()` 传入四个参数，并且 `get_embs()` 内调用 `infer_seq()` 时又漏传 `mode`；当前编码入口无法直接运行。
- 论文称 EHSM batch size 64、learning rate $10^{-5}$；训练脚本显示单卡 batch 1、梯度累积 4，且未显式给出该学习率。论文称 Caduceus batch 128、learning rate $10^{-4}$，仓库训练脚本也与之存在差异并含内部绝对路径。
- 训练对数据与已建数据库未随仓库提供；需要依据公开来源重建。论文提供的软件版本和在线服务，但这不等于本地端到端复现材料齐全。

因此最稳妥的结论是：ERAST 的方法创新是将生物学先验、快速向量召回和可独立更新的进化层级重排器组合起来；论文验证了线上系统的规模与精度，而公开代码主要证明局部算法路径，并暴露了尚需修补的工程与数据缺口。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ERAST Summary

**Paper**: Scalable homology detection with ERAST
**Journal**: Nature Biotechnology | **Year**: 2026
**DOI**: 10.1038/s41587-026-03051-1
**Code**: https://github.com/TencentAILabHealthcare/ERAST (PolyForm Noncommercial License)

---

### Motivation & Novelty

#### The Biological Problem

Homology search — finding sequences that share evolutionary ancestry — is the foundational step in characterizing any newly discovered biological sequence. The problem has become a computational bottleneck: metagenomics databases now contain billions of sequences (MGNify: 2.4 billion), and the speed–accuracy tradeoff of existing tools makes comprehensive searches impractical.

#### Limitations of Existing Approaches

| Method | Year/Journal | Type | Key Limitation |
|---|---|---|---|
| BLAST | J. Mol. Biol. 1990 | Sequence alignment | Misses distant homologs; heuristic alignment |
| Foldseek | Nat. Biotechnol. 2024 | Structure-based | Requires pre-computed structures; 50× slower than ERAST |
| TM-align | Nucleic Acids Res. 2005 | Structure alignment | Gold-standard accuracy but 50,000× slower than ERAST |
| TM-Vec | Nat. Biotechnol. 2023 | DL protein search | Brute-force FAISS; weak on OOD sequences; encoder updates require full re-embedding |
| PLMSearch | Nat. Commun. 2024 | DL protein search | Excellent in-distribution; poor OOD; full re-embedding on updates |
| DHR | Nat. Biotechnol. 2024 | DL protein search | Best OOD via contrastive learning; but requires massive training data and full re-embedding |

**The re-embedding bottleneck** is the key structural problem: all prior deep learning methods (TM-Vec, PLMSearch, DHR) couple the encoder to the vector database. Upgrading the encoder forces re-encoding all billion database sequences — prohibitively expensive.

#### ERAST's Unique Contributions

1. **Decoupled encoder + reranker**: The EHSM reranker can be retrained independently when OOD sequences appear, without touching the database embeddings. This is ERAST's most scalable architectural insight.
2. **Largest biological vector database**: >1 billion sequences (807M UniParc + 190M UniRef90 + 59M UniRef50 + 34M RefSeq nucleotides)
3. **Three-stage pipeline**: Preretrieval filtering + vector retrieval + postretrieval reranking; each stage targets a different precision layer
4. **Dual modality**: Both protein (ESM2-650M) and nucleotide (fine-tuned Caduceus/Mamba) supported in a unified framework
5. **EHSM achieves structure-comparable accuracy without structures**: At reranking, EHSM (sequence only, 1.3s) matches TM-align (structure, 5.4s) on SCOPe40-test (P@1: 0.820 vs. 0.816)

---

### Method Overview

ERAST combines three independently deployable components:

**1. Encoding Layer** (offline, one-time)
- Proteins: ESM2-650M mean-pooling → 1,280-dim vectors
- Nucleotides: Caduceus (Mamba + BiSSM + RCPS) → 256-dim vectors, fine-tuned on 30-phylum NCBITaxonomic dataset
- Stored as IVFPQ+HNSW indexed segments of 10M sequences each

**2. Preretrieval Filtering** (protein only)
- HMMER `hmmscan` against Pfam HMM database → clan and family labels per protein
- Filter target database to sequences sharing Pfam clans → narrows search space
- Within clan matches, elevate sequences sharing Pfam family to higher ranks

**3. Vector Retrieval**
- L2-normalize query and target embeddings
- Cosine similarity via FAISS IVFPQ+HNSW index
- Multi-threaded parallel search across 10M-sequence segments → O(log n) scaling

**4. EHSM Postretrieval Reranking**
- Cross-encoder: query + candidate concatenated → Ankh-base LM → 3-layer MLP classifier
- 4-class evolutionary distance prediction: same family (3) / superfamily (2) / fold (1) / different fold (0)
- Hybrid sorting: EHSM labels as primary key, original vector scores as tiebreaker
- Trained on SCOPe40withScore: 40M protein pairs labeled by SCOP structural hierarchy

For details, see `doc_method.md` and `doc_code.md`.

---

### Evaluation

#### Protein Homology: SCOPe40-test Benchmark

2,207 proteins, 4,870,849 all-vs-all pairs. Training/test split by fold (no fold overlap).

| Method | P@1 | P@10 | AUROC (Avg) | Speed (seconds) |
|---|---|---|---|---|
| MMseqs2 | 0.609 | 0.223 | 0.123 | 2 |
| Foldseek | 0.777 | 0.574 | 0.560 | 12 |
| TM-align | 0.816 | 0.602 | 0.658 | 11,303 |
| TM-Vec | 0.752 | 0.536 | 0.497 | 0.70 |
| PLMSearch | 0.792 | 0.588 | 0.731 | 4 |
| DHR | 0.720 | 0.526 | 0.475 | 0.69 |
| **ERAST** | **0.821** | **0.604** | **0.727** | **2.94** |
| ERAST (no reranker) | 0.810 | 0.600 | 0.636 | 0.23 |

ERAST achieves best P@1 (+2.9% vs PLMSearch, +6.9% vs TM-Vec) with 50× speed advantage over Foldseek. Statistical significance: P < 0.05 vs all baselines (two-sided t-test).

#### Out-of-Distribution (OOD) Benchmark

275 SwissProt-Pfam proteins selected as maximally distant from SCOPe40 training set (largest k=10 NN distances). Tests robustness to novel protein families.

| Method | AUROC (Clan) | AUROC (Pfam) | P@1 |
|---|---|---|---|
| Foldseek | 0.258 | 0.880 | 0.897 |
| TM-align | 0.021 | 0.735 | 0.769 |
| PLMSearch | 0.987 | 0.974 | 0.879 |
| DHR | 0.440 | 1.00 | 0.897 |
| **ERAST** | **1.00** | **1.00** | **0.974** |

ERAST achieves perfect AUROC on OOD dataset, outperforming TM-align by +0.622 absolute AUROC (1.00 vs 0.378 average AUROC — a 62.2 percentage-point improvement).

#### Reranking Strategy Comparison (SCOPe40-test)

| Reranker | P@1 | P@10 | Input | Latency |
|---|---|---|---|---|
| MMseqs2 | 0.706 | 0.322 | Sequence | 0.1s |
| Foldseek | 0.786 | 0.581 | Structure | 0.4s |
| TM-align | 0.816 | 0.599 | Structure | 5.4s |
| **EHSM** | **0.820** | **0.603** | Sequence | 1.3s |

EHSM matches structure-based accuracy using only sequence input.

#### Nucleotide Homology Search (NCBITaxonomic)

30 phyla, genus-separated train/test split. ERAST achieves highest F1 at all taxonomic levels:
- F1 macro/micro/weighted: 0.82/0.88/0.87 vs BLASTn 0.80/0.83/0.82
- AUROC at genus level: 0.186 vs BLASTn 0.051

#### Speed Benchmarks

- **Nucleotide search**: ERAST 60× faster than BLASTn, 2× faster than MMseqs2 for sequences >100,000 bp
- **Billion-scale**: Query time 43–200 μs regardless of database size from 500K to 20M (parallel strategy)
- **Parallel vs. sequential**: 2.9× speedup at 2B-scale database

#### Functional Clustering

8,841,389 functional clusters in UniRef90. 94% of dark clusters connect to bright clusters with known functions, providing evolutionary context for >158 million "dark" proteins. Dark protein annotation hit rate: 0.917 (ERAST) vs 0.863–0.886 (baselines).

---

### Reproducibility Rating: 3/5

**Justification**: The released code covers the local inference pipeline (encode + predict + pfam_scan) and training scripts for both models. However, significant components are missing or not portable:

**Strengths**:
- Local pipeline (encode.py + predict.py + pfam_scan.py) is functional for small-scale search
- Training scripts provided for both EHSM and Caduceus fine-tuning
- Pre-trained model checkpoints available (ESM2 from Meta, EHSM from Zenodo 16879060)
- Web interface with billion-scale DB accessible at https://ai4s.tencent.com/erast

**Weaknesses**:
- IVFPQ+HNSW billion-scale index not released (server-side only)
- Training code contains hardcoded internal Tencent absolute paths (phy_trainer.py)
- Two bugs in released code: `encode.py:78` wrong number of args to `get_embs`; `predict.py` missing `import torch`
- Effective batch size discrepancy: paper reports 64 for EHSM, code shows 1 + gradient accumulation 4 = effective 4
- Caduceus training LR discrepancy: paper 1e-4, code 1e-6
- Training datasets (SCOPe40withScore, NCBITaxonomic) not directly released; must reconstruct from scratch

**Setup Requirements**:
```bash
Python 3.8, PyTorch 2.2, transformers 4.38.1
mamba-ssm 1.2.0.post1, causal-conv1d 1.2.0.post2, flash-attn 2.5.6
HMMER (external, for Pfam scanning)
FAISS 1.7.2
```

**Common Pitfalls**:
1. Fix encode.py:78 before running: `get_embs(model, tokenizer, seqs)` (remove `args.mode`)
2. Fix predict.py: add `import torch` at top
3. EHSM checkpoint from Zenodo, not in repo
4. Caduceus checkpoint requires matching `mamba.bin` DDP weights
5. For nucleotide mode, Pfam scanning is skipped; only vector similarity ranking is used

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
