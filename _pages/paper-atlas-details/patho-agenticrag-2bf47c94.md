---
layout: default
permalink: /paper-atlas/patho-agenticrag-2bf47c94/
title: "Patho-AgenticRAG"
nav: false
description: "Patho-AgenticRAG 的贡献不是把更多文本塞给病理 VLM，而是学习一条条件化工具路径：必要时把问题拆成候选诊断查询，在器官分区的图文教材页中先召回再用尖峰相似度重排，多轮汇总证据后交给 Patho-R1；核心推理 demo 与 fusion 代码可查，但强化学习训练和大规模知识库仍是明确的复现缺口。"
robots: noindex, nofollow
sitemap: false
---

<!-- Generated locally by bin/export_paper_atlas.py. -->
<section class="paper-detail" id="paper-detail">
  <a class="paper-detail__back" href="{{ '/paper-atlas/' | relative_url }}">
    <i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Back to Paper Atlas
  </a>
  <header class="paper-detail__hero">
    <div class="paper-detail__chips">
      <span>Representation Models</span>
      <span>arXiv · 2025</span>
    </div>
    <h1>Patho-AgenticRAG</h1>
    <p>Patho-AgenticRAG: Towards Multimodal Agentic Retrieval-Augmented Generation for Pathology VLMs via Reinforcement Learning</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2508.02258" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Patho-AgenticRAG 方法解读：让病理 VLM 学会决定何时查书、查什么、怎样用图文证据

### 1. 它解决的不是单纯“检索”，而是检索决策

病理问答常需要同时判断形态线索和医学定义。只靠 VLM 参数记忆容易生成貌似合理但没有图像或文献依据的答案；文本 RAG 又会丢掉教材页面上的组织学图片、图注和排版关系。Patho-AgenticRAG 因而把问题拆成三层：先由 router 判断是否需要外部知识、如何改写查询及是否限制器官分区；再由 VRAG agent 多轮检索和摘要；最后由 Patho-R1 结合原图、问题与证据完成诊断推理。

这是一篇方法论文，不是 review。论文主体给出系统、fusion score、router 的 hierarchical reward 与 GRPO 目标；Appendix A–D 补充知识库、四阶段诊断流程、训练数据/参数和评估协议。当前本地代码覆盖知识库检索、融合重排、agent demo 和遗传编程搜索工具，但没有 router 的 SFT/GRPO 训练脚本，也没有 600 本教材构成的实际数据库。

### 2. 知识库为什么以“页面图像”为单位

作者收集 600 余本病理教材、约 30 万页，去除封面、前言、目录和参考文献后保留 20 万余诊断相关页面，并按 19 个解剖/诊断类别分区。每一页作为完整图像输入 ColQwen2，因而页内文字、显微图、图注和相对布局一起进入 token-level embedding。向量存入 Milvus，使用 HNSW approximate nearest-neighbor index。

图 1顶部把传统 text RAG、普通 multimodal RAG 和本方法并列：前者丢视觉内容，普通多模态检索仍是静态单轮，本方法增加 router、multi-turn interaction、tissue classification 和 Patho-R1。图的下半部同时画出教材页清洗、SFT cold start、reinforcement learning 以及 evolutionary search 得到 fusion formula。

源码可验证 Milvus collection 的 128 维向量字段、HNSW/IP index，以及按 `partition_names` 过滤搜索（`code/search_engine/milvus.py:20-145`）。但实际 20 万页/1.5 亿向量和 19 个 partition 不在仓库里，规模只能引用论文，不能本地计数复核。

### 3. 两阶段检索：先文字召回，再图文重排

router 可以为一个问题生成多个 candidate-specific queries。例如图 2的 invasive lobular carcinoma 题目被拆成“Indian-file morphology”和“与 ductal/papillary/mucinous 的鉴别”，并选择 Breast partition。每个 query 先做 text retrieval，取 top 20 教材页；随后使用原始病理图像对这 20 页做 multimodal reranking。

代码中的 `batch_search` 先通过 ColQwen2 processor 得到 text token embeddings，经 Milvus 搜索 top-20；再生成 query image patch embeddings，并把二者交给 `_rerank_and_return_results`（`milvus_search_engine.py:157-250`）。这就是“召回要快、重排要精”的计算折中。

### 4. Patho-Fusion score 实际计算什么

对候选教材页，令 $S_t\in\mathbb{R}^{N_t\times N_d}$ 是 query text tokens 对 document tokens 的相似度，$S_v\in\mathbb{R}^{N_v\times N_d}$ 是 image patches 对 document tokens 的相似度。论文式 (1)为：

$$
\operatorname{std}(\operatorname{std}(S_t))
\,[\operatorname{mean}(\kappa(S_t))]^2
\,\operatorname{mean}(\kappa(S_v))
+\operatorname{mean}(\max(S_t)).
$$

最后一项是 late-interaction MaxSim：每个文字 token 找最匹配的页面 token，再平均。乘积项偏好“少数位置高度匹配、其他位置不匹配”的尖峰分布；如果整页所有 token 都均匀相似，作者把它视为泛化噪声。图 3显示 synovial sarcoma 正确页面虽然初始文字排序第二，但相似度热图更集中，fusion score 0.6671，高于错误页的 0.6638，因而升到 top 1。

源码逐项计算 `text_embed @ db_embed.T`、`img_embed @ db_embed.T`、双层 std、kurtosis 和 mean-max（`milvus_search_engine.py:266-298`），属于可直接验证的核心实现。值得注意：image modality 只通过 kurtosis 进入式子，没有平均 image similarity；这不是通用的图文加权平均。

论文和代码还表明该式并非手工从概率模型推导，而是用 evolutionary heuristic/genetic programming 在 100 个专家标注 image-question-page pairs 上搜索得到；50%用于优化，50%用于测试。因此它是小型特定检索集上选择出的经验公式，跨教材、染色或器官的稳定性仍需外部验证。

### 5. Router 的四级决策路径

router 输入原始图像与问题，输出结构化 `<tool_call>`：

1. 是否调用 RAG。简单常识或纯视觉可直接进入 Patho-R1。
2. 若调用，生成一个或多个高信息量 query rewrites。
3. 是否使用 tissue classifier 缩小 Milvus partition。
4. 若使用，选择正确的 19 类 partition。

hierarchical reward 按路径逐级给分，总分范围 0–4。正确“不检索”直接得 4；正确“检索”先得 1，再根据 rewrite count、是否需要 classifier 和 partition 是否正确逐步加分。这个设计让 agent 不只学习最终答案，而是学习与 ground-truth tool trajectory 一致的操作结构。

训练集来自 Quilt-VQA 和 Path-VQA：先由 Patho-R1 推理，筛出 2200 个答错（应需要 RAG）与 2200 个答对（应不需要 RAG）的样本，并平衡 MCQ/YORN；QwenMax 蒸馏决策轨迹，最终 400 个样本用于 SFT cold start、4000 个用于 RL。图 5的 Sankey diagram展示了这条数据流。

### 6. 为什么是小 SFT 加大 GRPO

router policy 以 GRPO 学习。同一 query 采样多条路径，先在组内标准化 reward：

$$
A_i=\frac{r_i-\mu_Q}{\sigma_Q+\eta},
$$

再用 clipped policy ratio 和 KL penalty 更新。论文消融表明直接 GRPO 不易收敛，大规模 SFT 又会形成僵硬格式；400 SFT + 4000 GRPO 在六个评估集上总体最好。图 4可直接看到这一配置在 Path-VQA 达 80.34%、Quilt-VQA 达 75.80%，但各配置变化也包含 base router/Qwen3 能力的贡献，不能把全部提升都归因于 RAG。

当前仓库没有 SFT、GRPO、reward parser 或训练入口。`agent_prompt.md` 和 demo 只能证明推理时的 tool-call format，不能证明论文训练流程可重跑。因此 GRPO 数学、样本构建与超参数属于 paper-only evidence boundary。

### 7. VRAG 如何做多轮证据汇总

router 产生的多个 rag queries 在 demo 中并发执行。VRAG 最多运行 3 步：模型输出 `<think>` 后选择 `<search>`、`<bbox>` 或 `<answer>`；search 会访问检索服务，bbox 可裁剪新页面，answer 只总结诊断特征而不直接选答案（`code/demo/vrag_agent.py:52-102,229-280`）。

`MyAgent.run` 解析 `<tool_call>` 中的 rag queries 和 classifier partition，并发调用 VRAG，将返回证据拼成 context，最后调用 Patho-R1 HTTP endpoint（`patho_agenticrag.py:154-282`）。图 2展示的 Indian-file case 是这种流程的定性示范，不是总体准确率的证据。

一个重要源码边界是 `verify_rag_result`：函数确实让 Qwen 判断证据是否有用，但 `run` 的 else 分支仍把判为无用的结果加入 context（`patho_agenticrag.py:246-255`）。所以发布 demo 并没有真正过滤失败验证结果，旧文档若声称“验证门控保证只保留有用证据”会过度解读。

### 8. 最终回答与实验结果如何读

最后的 Patho-R1 接收原图、原问题和 evidence summaries，输出 reasoning 与答案。论文在 PathMMU、Path-VQA、Quilt-VQA、MedXpertQA pathology subset 和 OmniMedVQA BRIGHT 上评估。表 3报告 Patho-AgenticRAG 相比 Patho-R1：Quilt-VQA 75.80 vs 64.72，Path-VQA 80.34 vs 46.97，MedXpert 60.00 vs 22.00，OmniMed BRIGHT 90.11 vs 70.79。

这些数字表明整套系统在选定 close-ended benchmarks 上更准，但论文没有提供临床前瞻试验、病理医师 reader study、calibration 或真实幻觉率测量。结论应限于 benchmark answer accuracy 与 retrieval metrics，不能改写成“已证明临床安全”或“消除 hallucination”。

检索评估使用 recall@k、MRR@k 和 NDCG@k；NDCG 中目标页 relevance=2，相邻页 ±1 relevance=1，因为教材相邻页可能包含延续内容。本地 `SimilarityEvaluation` 确实按 page ±1 计算 NDCG，并以固定 random state 把 100 条数据切分一半（`code/multimodal_fusion/code_evaluation.py:83-197`），但 `rag_dataset/dataset.json` 与 cache 并未作为完整可运行资产提供。

### 9. 五张主图的证据层级

- **图 1**：系统和训练概览，是架构证据，不是性能证明。
- **图 2**：一个乳腺病例的多 query、多轮检索示例，是可解释 workflow illustration。
- **图 3**：一个 synovial sarcoma 重排案例，直接展示式 (1)如何改变 top-1。
- **图 4**：六数据集上的 training recipe ablation，支持 small-SFT cold start + larger GRPO。
- **图 5**：训练样本筛选与蒸馏组成，说明 400 SFT/4000 RL 的来源。

本地 OCR 提取了五张主图，并在本次恢复中逐张视觉检查。Appendix A–D 在同一论文 PDF/Markdown 中，没有发现独立 supplementary 文件；因此可说“附录已读”，不能说“独立补充包已核验”。

### 10. 代码 provenance 与可复现边界

工作区记录的上游 URL是 `https://github.com/Wenchuan-Zhang/Patho-AgenticRAG`，旧 metadata 写短 commit `cae8a66`。但本地 `code/` 没有独立 `.git`，从其中运行 Git 会落到 PaperCode 外层仓库，并显示完全无关的 commit。故本次把代码来源标为 `local_dir`，保留旧短 hash 仅作为 acquisition 记录，不宣称当前文件已由 Git 验证对应那个 commit。

可直接验证：Milvus schema/index/search、ColQwen2 query/image embedding、式 (1)重排、VRAG interaction、router demo orchestration、fusion evaluation 与 evolutionary search utilities。

不可本地验证：教材数据库本体、完整训练/评估数据、router SFT/GRPO、QwenMax distillation、Patho-R1/VRAG weights 与服务、论文端到端 benchmark reproduction。

### 11. 一句话总结

Patho-AgenticRAG 的贡献不是把更多文本塞给病理 VLM，而是学习一条条件化工具路径：必要时把问题拆成候选诊断查询，在器官分区的图文教材页中先召回再用尖峰相似度重排，多轮汇总证据后交给 Patho-R1；核心推理 demo 与 fusion 代码可查，但强化学习训练和大规模知识库仍是明确的复现缺口。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## summary.md — Patho-AgenticRAG

### Motivation & Novelty

**Biological problem**: Pathology diagnosis requires matching visual evidence (cellular morphology, staining patterns, tissue architecture in H&E/IHC slides) against structured diagnostic knowledge from textbooks. This reasoning process is multimodal — both visual and textual cues matter — and demands grounding in authoritative reference material. Vision-Language Models (VLMs) applied to pathology generate hallucinated diagnoses because they cannot reliably access or leverage reference knowledge during inference.

**Why existing methods fall short**:
- **MMed-RAG** (ICLR 2025): Built a multimodal medical RAG system but its knowledge base categorizes images only by imaging modality (CT, X-ray), not by organ/tissue system — insufficient precision for pathology where breast vs. lung context is essential for correct retrieval.
- **Text-only RAG approaches** (Jabal et al., arXiv 2024; Cheetirala et al., arXiv 2025): Discard diagnostic visual cues entirely; cannot retrieve the textbook figures that show tissue morphology.
- **MedRAG** (WWW 2025) and **Medical Graph RAG** (arXiv 2024): Use knowledge graphs for reasoning enhancement but are architecturally complex, lack scalability, and have poor adaptability to diverse clinical tasks.
- **Patho-R1** (arXiv 2025, baseline VLM): The pathology-specialized VLM used as the inference engine; strong reasoning but still hallucinates without retrieval grounding.

**Novel contributions**:
1. **First page-level multimodal pathology knowledge base**: 200k+ textbook pages embedded with ColQwen2 as joint image-text vectors, partitioned into 19 anatomical categories. Enables searching for textbook pages that are visually and semantically similar to the query — not just keyword matching.
2. **Agentic Router with GRPO training**: A Qwen3-4B model trained with RL to decide (a) whether to invoke retrieval at all, (b) how many times to rewrite the query, (c) whether to restrict search to an organ-specific partition. Trained on balanced examples of cases where Patho-R1 needs vs. doesn't need external knowledge.
3. **Patho-Fusion Re-ranking (Eq. 1)**: A novel re-ranking formula that uses kurtosis of similarity distributions to distinguish focused (relevant) matches from diffuse (noisy) matches. Notably, this formula was discovered via evolutionary algorithm (EoH/genetic programming), not analytically designed.

---

### Method Overview

Patho-AgenticRAG is a modular pipeline:

1. **Knowledge Base**: ColQwen2 embeds 200k+ pathology textbook pages as per-token vectors (dim=128). Stored in Milvus with HNSW indexing, partitioned into 19 anatomical categories.

2. **Agentic Router** (Qwen3-4B, GRPO-trained): Receives the query and decides: no-RAG (for simple/visual-only questions), RAG-only (for factual questions), or RAG+classifier (for organ-specific questions). Outputs structured tool calls in JSON format.

3. **VRAG Agent**: For each sub-query from the router, performs up to 3 rounds of: text retrieval (top-20 via ColQwen2) → fusion re-ranking (Eq. 1) → image retrieval of the top page → optional crop → summarize evidence. Returns structured evidence per diagnostic candidate.

4. **Patho-R1 VLM**: Receives the original query, its image, and the retrieved evidence summaries. Performs contrastive reasoning constrained to the evidence and outputs a diagnosis.

See `doc_method.md` for equations, algorithm walkthrough, and Mermaid diagram.

---

### Evaluation

**Datasets**:
- **PathMMU-test** (8,454 MCQ): Atlas, EduContent, PathCLS, PubMed, SocialPath subsets (ECCV 2024)
- **PathMMU-test-tiny** (1,139 MCQ): Same subsets
- **MedXpertQA** (90 pathology MCQ): Expert-level medical reasoning (arXiv 2025)
- **OmniMedVQA BRIGHT Challenge** (890 cases): Medical specialty diagnostic reasoning (CVPR 2024)
- **Quilt-VQA** (343 YORN): Histopathology yes/no questions (NeurIPS 2023)
- **Path-VQA** (3,362 YORN): Medical visual QA (arXiv 2020)
- **Retrieval eval**: 100 expert-curated image-question-answer pairs; 50/50 train/test split

**Retrieval results** (Table 1, test set):

| Method | Rec@1 | Rec@5 | MRR@1 | NDCG@1 | NDCG@20 |
|---|---|---|---|---|---|
| CoPaLi (Text) | 0.640 | **0.900** | 0.640 | 0.740 | 0.796 |
| CoPaLi (Image) | 0.060 | 0.220 | 0.060 | 0.080 | 0.359 |
| WeiMoCIR | 0.060 | 0.200 | 0.060 | 0.080 | 0.342 |
| **Patho-Fusion (ours)** | **0.720** | 0.880 | **0.720** | **0.820** | **0.827** |

- Patho-Fusion achieves +12.5% Recall@1 over CoPaLi (Text), showing the fusion formula adds real value beyond text-only search
- Image-only and WeiMoCIR perform poorly, confirming that general-purpose image embeddings are insufficient for pathology

**Downstream QA results** (Table 3):

| Model | Quilt-VQA | Path-VQA | MedXpert | OmniMed BRIGHT |
|---|---|---|---|---|
| Patho-R1-7B (baseline) | 64.72 | 46.97 | 22.00 | 70.79 |
| **Patho-AgenticRAG** | **75.80** | **80.34** | **60.00** | **90.11** |
| Improvement | +11.08 | +33.37 | +38.00 | +19.32 |

- Largest gain on MedXpert (+38%), a knowledge-intensive expert benchmark — confirms RAG most benefits factual recall tasks
- Path-VQA gain (+33.37%) is surprisingly large for a yes/no task — suggesting RAG helps the model avoid false positives
- vs. InternVL3-8B: +41.88 on Quilt-VQA (75.80 vs 33.82), +61.78 on Path-VQA (80.34 vs 18.56)

**Ablation** (Figure 4): SFT400+GRPO4k is the best configuration. Key insight: a small SFT cold-start (400 samples) before GRPO prevents training instability and improves generalization. Large SFT (4k) causes overfitting to rigid output patterns.

---

### Reproducibility: 2/5

**Justification**: The codebase provides the inference pipeline (demo) and the offline retrieval evaluation tools, but omits three critical components:

1. **Training code absent**: No GRPO training loop, no SFT code, no verl/LLaMA-Factory configuration files. Cannot reproduce the trained Agentic Router.
2. **Knowledge base not included**: 200k+ textbook page embeddings not provided (as expected given copyright), and no automated pipeline to recreate it from publicly available sources.
3. **Benchmark evaluation absent**: No code to evaluate on PathMMU, Path-VQA, etc. Numbers in Tables 2-3 cannot be reproduced without Patho-R1 model weights (not released in this repo) and the evaluation harness.
4. **What IS reproducible**: The fusion formula evaluation (Table 1) can be reproduced if you have the 100-pair retrieval dataset and a Milvus instance with ColQwen2 embeddings. The `multimodal_fusion/` code provides everything needed for that.
5. **Unexpected finding**: The fusion formula was evolved by EoH genetic programming — the code to rediscover the formula is present, but the paper doesn't mention this. A reader implementing from the paper alone would need to manually transcribe Eq. 1.

**Practical notes**:
- Requires 5 running services: Milvus, FastAPI search server, VRAG LLM server, Agentic Router LLM server, Patho-R1 VLM server
- The `pdf_datasets/` directory has only 3 demo images per partition — insufficient for real evaluation
- Port hard-coding in `milvus_search_engine_api.py` (localhost:8001/19530) requires local deployment

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
