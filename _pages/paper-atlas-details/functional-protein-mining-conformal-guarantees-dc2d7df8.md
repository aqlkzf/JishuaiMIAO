---
layout: default
permalink: /paper-atlas/functional-protein-mining-conformal-guarantees-dc2d7df8/
title: "Functional_Protein_Mining_Conformal_Guarantees"
nav: false
description: "Protein-Vec、CLEAN、Foldseek 等模型能够给蛋白对打分，但“分数很高”不等于“功能一定相同”，更不能告诉实验人员应该保留多少候选。本文的核心不是训练一个新蛋白模型，而是在任意现有打分模型之后增加一个校准与风险控制层：用户先指定可以接受的错误，例如 10% 假发现率，再由独立校准集自动求出阈值。 输入：查询蛋白 Q、检索数据库 D、模型分数 S{ij}、带真实标签的校准查询，以及风险容忍度 \\alpha。"
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
      <span>Machine Learning Algorithm</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>Functional_Protein_Mining_Conformal_Guarantees</h1>
    <p>Functional protein mining with conformal guarantees</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-024-55676-y" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 用共形保证进行功能蛋白挖掘

### 这篇论文解决什么问题？

Protein-Vec、CLEAN、Foldseek 等模型能够给蛋白对打分，但“分数很高”不等于“功能一定相同”，更不能告诉实验人员应该保留多少候选。本文的核心不是训练一个新蛋白模型，而是在任意现有打分模型之后增加一个**校准与风险控制层**：用户先指定可以接受的错误，例如 10% 假发现率，再由独立校准集自动求出阈值。

### 核心输入与输出

- 输入：查询蛋白 $Q$、检索数据库 $D$、模型分数 $S_{ij}$、带真实标签的校准查询，以及风险容忍度 $\alpha$。
- 输出：

  $$
  C_{\hat\lambda}(Q_i)=\{D_j:S_{ij}\ge\hat\lambda\},
  $$

  即超过校准阈值的候选集合。集合可以为空，这能避免强迫模型给非酶蛋白分配 EC 编号。

### 方法流程

```text
蛋白序列/结构
    ↓
Protein-Vec、CLEAN 或其他黑盒模型产生相似度/距离
    ↓
校准数据提供真实 Pfam、EC、SCOPe 或 DALI 标签
    ↓
定义生物学损失：FDR / FNR / 层级错配
    ↓
共形风险控制或 Learn-then-Test 扫描阈值
    ↓
得到 lambda_hat 并筛选未来蛋白
    ↓
可选：Venn-Abers 把分数转为概率区间
```

#### 1. 三类损失

- **FDR**：返回候选中错误匹配的比例，适合实验验证成本高、希望候选更“纯”的场景。
- **FNR**：所有真实匹配中被漏掉的比例，适合先过滤大型数据库、但又不希望漏掉结构同源物的场景。
- **层级损失**：EC 和 SCOPe 都是树形分类。第四位 EC 号不同只产生小损失，而酶大类不同产生大损失。用户还可以按应用重新设置惩罚权重。

#### 2. 如何求阈值

对于单调、有界损失，共形风险控制在校准集上寻找满足有限样本修正条件的最宽松阈值：

$$
\frac1n\sum_{i=1}^n\ell(X_i,C_\lambda(X_i))
\le \alpha-\frac{B-\alpha}{n}.
$$

FDR 随阈值不一定单调，因此论文使用离散的 Learn-then-Test：对每个候选阈值构造高概率风险上界，再选择其后所有更保守阈值都通过检验的位置。

#### 3. 概率校准

原始 Protein-Vec 分数几乎都挤在 0.9995–1，难以解释。Venn-Abers 对同一个测试分数分别假设标签为 0 和 1，拟合两次单调等距回归，得到 $(\hat p^0,\hat p^1)$。理论上应把它理解为概率区间/二选一校准保证，而不是每个蛋白都有精确概率。

### 三个应用

1. **JCVI Syn3.0 未知功能基因**：在 $\alpha=0.1$ 的 FDR 阈值下，149 个未知功能编码基因中有 59 个（39.6%）得到 exact-Pfam 候选。结构叠合给出一个核酸外切酶例子，但这些仍是计算注释，不能替代生化验证。
2. **CLEAN 酶功能分类**：使用相同 CLEAN 嵌入，只替换标签选择规则。New-392 上 F1 为 57.65、AUC 为 81.50，高于 max-separation 和 p-value；对明显非酶的 SARS-CoV-2 抗体片段，共形方法可以返回空集。
3. **DALI 前置过滤**：先用快速 Protein-Vec 过滤 230 万条 clustered AFDB，再运行昂贵的 DALI。平均删除 31.5% 数据，同时保留 82.8% 高于 DALI $Z'$ 拐点的命中。

### 如何正确理解“保证”

- 保证依赖校准损失与未来损失的**可交换性**；物种、家族、时间或数据质量分布变化都可能破坏它。
- 保证是总体平均的边际保证，不是每个蛋白、每个家族都达到同一错误率。
- New 到 Price、SCOPe 到 DALI 属于跨任务/跨分布测试，其结果是经验鲁棒性，不是严格继承的名义保证。
- 结构或嵌入相似不等于相同生化功能；活性位点的少数突变就可能改变功能。

### 代码与复现

官方代码固定在 `paper-biorxiv` 标签、提交 `53fd47375fa4682da0cfd505f0778c961cf56828`。核心 FDR/FNR、Venn-Abers、层级损失和实验 notebook 都能定位，论文—代码匹配度为 **medium**。但 UniProt、CLEAN、SCOPe、DALI、AFDB 和预训练模型属于大型外部依赖；仓库还包含绝对集群路径、不完整 CLI、未固定依赖及一个 `TabError`。因此可以审查算法并部分复跑，但不能从仓库一键完整重现全部图表。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Functional protein mining with conformal guarantees

### Paper summary

Protein embedding and structure-search systems can rank millions of candidates quickly, but their raw scores do not tell a biologist which proteins are safe to characterize or how much error a returned set contains. Boger et al. add a model-agnostic conformal calibration layer to protein retrieval: a held-out labeled set selects a global score threshold for a user-chosen expected loss, such as false discovery rate (FDR), false negative rate (FNR), or hierarchical EC/SCOPe mismatch. A separate Venn-Abers procedure converts compressed similarity scores into calibrated probability intervals. The method changes selection, not the underlying Protein-Vec or CLEAN representation.

The framework is demonstrated in three settings. At 10% FDR, calibrated Protein-Vec retrieval proposes exact-Pfam matches for 59 of 149 (39.6%) previously unknown-function genes in the JCVI Syn3.0 minimal genome. Applied to CLEAN enzyme embeddings, hierarchical conformal selection improves New-392 F1 from about 51–52 to 57.65 and AUC from about 75–76 to 81.50, and can correctly return no EC label for a SARS-CoV-2 antibody fragment; on shifted Price-149 it gives the best F1 (49.62) and AUC (74.59), but not the best precision. Finally, a Protein-Vec prefilter removes 31.5% of the 2.3-million-entry clustered AlphaFold Database while retaining 82.8% of DALI hits above a per-query $Z$-score elbow.

### Method in brief

1. Score every query–lookup pair with an existing protein model.
2. On independent labeled calibration queries, define exact/partial matches or hierarchy-depth losses.
3. Choose an application loss and tolerance $\alpha$.
4. Scan score thresholds and apply conformal risk control for monotone bounded loss, or Learn-then-Test for non-monotone FDR.
5. Deploy the selected $\hat\lambda$ to return $C_{\hat\lambda}(x)$; empty sets are allowed.
6. Optionally fit two isotonic regressions with hypothetical test labels 0 and 1 to obtain a Venn-Abers probability interval.

### What is novel

The contribution is a statistical decision layer for biological retrieval rather than another protein model. It makes the error metric task-specific, retains black-box compatibility, supports adaptive/empty retrieval sets, and connects fast embeddings to costly experimental or structural follow-up. The hierarchical loss is especially useful for EC numbers because it distinguishes a small fourth-digit substrate error from a wrong enzyme class.

### Evidence and limitations

All 4 principal and 7 supplementary figures were acquired and visually inspected. The main theoretical assumption is exchangeability of calibration and future losses; guarantees are marginal rather than per-query or per-family. The authors' temporal CDF checks only diagnose approximate exchangeability, and the New-to-Price and SCOPe-to-DALI transfers should be interpreted as empirical robustness tests. Similarity-based function assignment remains a hypothesis for experimental validation, particularly when small sequence changes alter activity.

### Reproducibility

The official repository is pinned to the paper release tag `paper-biorxiv` at commit `53fd47375fa4682da0cfd505f0778c961cf56828`; publisher Source Data and Supplementary Information are local. Code-paper fidelity is **medium**: core losses, threshold rules, Venn-Abers logic, FAISS helpers, and experiment notebooks are present, but the snapshot depends on large external UniProt/CLEAN/SCOPe/AFDB assets and cluster paths. Several utility scripts are incomplete, the probability-grid script has a `TabError`, dependencies are not pinned, and there is no automated end-to-end reproduction. The paper's old Zenodo code/data record pages were unavailable during acquisition, although DataCite still identifies the code DOI and the GitHub release provides a fixed snapshot.

**Reproducibility rating: 3/5** — strong source transparency and inspectable core algorithms, but substantial environment/data reconstruction is required for full results.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
