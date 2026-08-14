---
layout: default
permalink: /paper-atlas/clifti-gpt-9ea4ca02/
title: "CLIFTI-GPT"
nav: false
wide: true
description: "临床单细胞 RNA 测序数据通常分散在不同医院，受患者隐私、机构治理和数据异质性限制，不能把原始计数矩阵集中到一个服务器。scGPT 等单细胞基础模型能够迁移到细胞类型注释和参考映射，但集中式微调会违反治理要求，完全本地训练又只能看到有限样本。论文将 Tabula 描述为已有的联邦单细胞基础模型工作，但其不包含 SMPC 隐私保护。 clifti-GPT 在 scGPT 上增加两条联邦路径： 联邦微调：每个客户端只用本地参考细胞训练；"
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
      <span>Research Square · 2025</span>
    </div>
    <h1>CLIFTI-GPT</h1>
    <p>Clifti-GPT: Privacy-preserving federated fine-tuning and transferable inference of foundation models on clinical single-cell data</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Mohammad-Bakhtiari/clifti-GPT" target="_blank" rel="noopener noreferrer" aria-label="Open code for CLIFTI-GPT">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## clifti-GPT 方法说明（中文）

### 1. 要解决的问题

临床单细胞 RNA 测序数据通常分散在不同医院，受患者隐私、机构治理和数据异质性限制，不能把原始计数矩阵集中到一个服务器。scGPT 等单细胞基础模型能够迁移到细胞类型注释和参考映射，但集中式微调会违反治理要求，完全本地训练又只能看到有限样本。论文将 Tabula 描述为已有的联邦单细胞基础模型工作，但其不包含 SMPC 隐私保护（`paper.md:63-71`）。

### 2. 方法核心

clifti-GPT 在 scGPT 上增加两条联邦路径：

1. **联邦微调**：每个客户端只用本地参考细胞训练；模型权重以加法秘密分享发送给计算参与方，再用 FedAvg 或 FedProx 聚合。
2. **可迁移的零样本参考映射**：客户端不发送原始表达、嵌入或本地模型，而只交换局部近邻距离/索引和标签投票；SMPC 保护这些中间统计量。

在微调前，客户端还要把表达值转换成一致的离散 token。联邦分箱先在各客户端计算非零表达的分位数边界，再按样本量合成全局边界，所有客户端使用同一组边界（论文 `paper.md:398-406`）。

### 3. 输入、变量与输出

- 客户端集合：\(i=1,\ldots,C\)，本地样本数为 \(n_i\)。
- 参考数据：\(\mathcal R_i\)，查询数据：\(\mathcal Q\)。查询集中的细胞类型必须在参考集中出现（`paper.md:494-498`）。
- 基础模型：scGPT \(\mathcal F\)，初始权重 \(W_0\)。
- 输出：联邦全局权重（微调任务）或每个查询细胞的预测标签（参考映射任务）。

### 4. 计算流程

```text
各站点 AnnData
   |
   +-- 基因/细胞类型协调，站点内归一化
   +-- 联邦分箱 -> 共享 bin edges
   |
   +-- 本地 scGPT 微调 -> 秘密分享权重 -> FedAvg/FedProx
   |                                      ^
   |                                      +-- 多轮同步
   |
   +-- F(Q), F(R_i) -> 各站点 top-k 距离/索引
                           -> 全局 top-k
                           -> 标签投票 -> 查询预测
```

#### 4.1 联邦分箱

客户端先得到本地边界 \(B_i\)，协调者计算：

\[
B_{global}=\frac{\sum_i n_i B_i}{\sum_i n_i}.
\]

随后每个客户端将非零表达值映射到同一离散 bin。代码中 `FedAnnotator.preprocess_data` 在 `federated/annotator.py:200-235` 选择本地归一化、可选过滤/HVG 和联邦分箱；`_federated_binning` 在 `:237-251` 将结果应用到所有客户端。明文加权聚合在 `preprocessor/aggregation.py:91-108` 校验边界长度后按样本数加权并重新分位数化；SMPC 版本在 `:111-128` 只公开全局计数并累加秘密分享。

#### 4.2 联邦微调

论文的 FedAvg 更新为：

\[
W_{t+1}=\frac{\sum_i n_iW_i}{N},\qquad N=\sum_i n_i.
\]

FedProx 在客户端目标中加入：

\[
\frac{\mu}{2}\lVert W_i-W_t\rVert^2.
\]

代码的 `tasks/utils.py:104-119` 为每一轮调用客户端本地更新、聚合、评估并检查停止条件；`federated/annotator.py:139-147` 在本地训练前加载全局权重。`federated/aggregator.py:81-116` 实现明文的样本量加权参数和，`:118-137` 实现加密权重的 SMPC 求和；`federated/client.py:13-29` 展示了客户端可先按样本比例缩放再加密。FedProx 惩罚项的代码钩子位于 `centralized/models.py:206-216,246-252`，但本次没有运行联邦 FedProx 或 Crypten 多方任务，因此收敛和实际隐私行为仍是**未验证**。

论文主比较使用每客户端一个本地 epoch、20 轮通信，并报告额外轮数/epoch 和 \(\mu\) 的调参结果（`paper.md:79-82,127-129`）。仓库默认 YAML 是 5 轮、启用归一化和分箱（`experiments/configs/annotation/fed_config.yml:1-11`），命令行可以覆盖轮数；默认值不应被误认为论文每次实验的最终配置。

#### 4.3 明文参考映射

各方用同一个 \(\mathcal F\) 计算：

\[
\mathcal Q'=\mathcal F(\mathcal Q),\qquad \mathcal R_i'=\mathcal F(\mathcal R_i).
\]

每个客户端对本地参考嵌入做 L2 距离搜索，只保留 top-k。协调者合并候选近邻，再把全局近邻索引发回客户端；客户端用本地细胞类型标签投票，最终取票数最多的标签（`paper.md:424-432`）。代码的 `ClientEmbedder.compute_local_distances` 使用 FAISS 并以客户端盐值进行 SHA-256 索引哈希（`federated/embedder.py:39-68,104-141`）；`FedEmbedder.federated_reference_map` 串起距离、全局合并、投票和预测（`:406-432`）。

#### 4.4 SMPC 参考映射

查询和参考嵌入以秘密分享表示。客户端计算加密平方距离：

\[
\langle D_i\rangle=\langle Q\rangle^2\mathbf1^T+\mathbf1\langle R_i\rangle^2{}^T-2\langle Q\rangle\langle R_i\rangle^T.
\]

重复 one-hot 最小值掩码得到每个客户端的 top-k 距离和索引，再拼接各客户端候选并选出全局 top-k。之后用索引匹配掩码把近邻映射为全局标签编号，对各标签累积投票，并通过 one-hot 最大值得到预测（论文 `paper.md:434-482`）。代码在 `federated/embedder.py:70-102` 实现加密距离，在 `:335-357` 合并加密 top-k，在 `:143-180,359-404` 完成加密/明文投票。全局标签排序与客户端偏移处理位于 `:434-463`。

### 5. 评估与结果

论文在 MS、Human Pancreas、Cell Line、Lung-Kim 和 Myeloid 五个数据集上，以 accuracy、precision、recall、macro-F1 比较 centralized、local、FedAvg、FedProx 及其 SMPC 变体。主图显示 CL、HP、Lung-Kim 接近 0.97-0.99，MS 约 0.88-0.89，Myeloid 约 0.57-0.62（`paper.md:79-96`）。调参后，MS/Myeloid 可在约两轮达到集中式 accuracy 的 99%；最多 30 客户端时准确率损失低于 2% 的结论来自论文报告和 Fig. 5（`paper.md:127-129,203-212`）。参考映射在 HP、Lung-Kim、CL、MS 上据称匹配或超过集中式基线（`paper.md:150-201`）。Covid-19 数据的 scGen 批次校正改善 UMAP 混合并使 FedAvg-SMPC 达到 0.93 accuracy（`paper.md:214-305`）。

### 6. 代码一致性与缺口

分箱、FedAvg/SMPC 聚合、加密 KNN 和投票均有直接源码证据，整体代码-论文一致性评为 **medium**。但本次没有执行依赖安装、训练/推理、CrypTen 多方协议或测试；没有验证预训练权重、数据下载、精确命令行配置和生成指标。scGen 的论文结果也未在本次检查的代码范围内找到可运行实现。上述项目必须视为 `Not found`/未验证，而不是由静态调用路径推断。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## clifti-GPT Summary

### Problem

Clinical scRNA-seq cohorts are heterogeneous and privacy-sensitive, so raw counts and derived model updates often cannot be centralized. Foundation models such as scGPT offer transferable representations, but ordinary centralized fine-tuning conflicts with governance constraints; local-only training loses cross-site coverage. The paper positions Tabula as prior federated scRNA-seq foundation-model work without secure multiparty computation (paper `paper.md:63-71`).

### Proposed Method

clifti-GPT combines scGPT with federated fine-tuning and transferable zero-shot reference mapping. Clients normalize and discretize local counts using common federated bin edges, train locally, and send additive secret shares for FedAvg or FedProx aggregation. For reference mapping, clients exchange only nearest-neighbor distances/indices and label votes; SMPC protects the embedding statistics and vote computation. The paper’s equations define sample-weighted binning (`paper.md:398-406`), FedAvg/FedProx (`408-422`), and secure squared-distance, top-k, and voting operations (`424-482`).

### Evaluation

Cell-type classification is evaluated on Multiple Sclerosis (MS), Human Pancreas (HP), Cell Line (CL), Lung-Kim, and Myeloid datasets using accuracy, precision, recall, and macro-F1. The main one-local-epoch/20-round comparison reports federated accuracy near centralized performance (e.g., CL 0.99, HP 0.98, Lung 0.97, MS 0.88-0.89, Myeloid 0.57-0.62; `paper.md:79-96`). The paper reports that tuned settings can reach 99% of centralized performance in as few as two rounds for MS/Myeloid and scale to 30 clients with less than 2% accuracy loss (`paper.md:82,127-129,203-212`). Zero-shot mapping on HP, Lung-Kim, CL, and MS is reported to match or exceed centralized metrics (`paper.md:150-201`). A Covid-19 batch-effect experiment uses scGen correction and reports a corrected FedAvg-SMPC accuracy of 0.93 (`paper.md:214-305`). These are paper-reported results; this workspace did not rerun them.

### Code and Reproducibility

The matching GitHub snapshot (`master`, commit `80e7795791068607410a2b3700203ea37368ad26`) directly implements federated preprocessing/binning, weighted plaintext and SMPC aggregation, local/global KNN selection, and vote aggregation (`doc_code.md`). The default federated YAMLs enable normalization/binning and set five rounds. Code-paper fidelity is medium: core paths match the described algorithm, while FedProx execution, Crypten deployment, pretrained weights/data, exact benchmark commands, and scGen integration were not validated end to end. No runtime execution or tests were performed, and no supplementary Markdown was acquired.

### Limitations

The paper’s privacy claims are protocol-level claims rather than an independently audited threat-model result in this workspace. Reported performance depends on dataset splits, client heterogeneity, local epochs, rounds, and proximal coefficient; the figures show that batch effects and 30-client heterogeneity can widen the gap. Alternative batch-correction methods were not evaluated by the paper (`paper.md:321`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
