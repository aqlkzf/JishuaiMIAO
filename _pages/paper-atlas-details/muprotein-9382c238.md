---
layout: default
permalink: /paper-atlas/muprotein-9382c238/
title: "MuProtein"
nav: false
wide: true
description: "蛋白质工程的突变组合空间极大，而实验筛选次数有限。论文提出 μProtein，用 μFormer 预测突变后的 fitness，再用 μSearch 通过强化学习在 fitness landscape 中寻找多位点突变。论文摘要明确说，模型只用单突变数据训练，也要预测含多个氨基酸突变的序列，并考虑上位性（epistasis）。 代码中的 Muformer 使用预训练编码器，然后将表示送入 mono decoder。"
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
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>MuProtein</h1>
    <p>Accelerating protein engineering with fitness landscape modelling and reinforcement learning</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-025-01103-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for MuProtein">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/microsoft/Mu-Protein" target="_blank" rel="noopener noreferrer" aria-label="Open code for MuProtein">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## μProtein 方法说明

### 解决什么问题

蛋白质工程的突变组合空间极大，而实验筛选次数有限。论文提出 μProtein，用 μFormer 预测突变后的 fitness，再用 μSearch 通过强化学习在 fitness landscape 中寻找多位点突变。论文摘要明确说，模型只用单突变数据训练，也要预测含多个氨基酸突变的序列，并考虑上位性（epistasis）（`paper source/nature_html/paper.md:9-12`）。

### 总体流程

```text
单突变实验数据
      ↓
预训练蛋白质语言模型编码器
      ↓
μFormer：语义分数 + motif 分数 + 语言模型概率分数
      ↓
局部 fitness oracle
      ↓
μSearch：从当前最好序列开始的 PPO 搜索
      ↓
按预测 fitness 排序的多位点候选序列
```

### μFormer 如何打分

代码中的 `Muformer` 使用预训练编码器，然后将表示送入 mono decoder（`Mu-Protein/mu-former/src/model.py:225-303`）。decoder 产生两类监督分数：

1. 语义/序列级分数 (s_{sem})：使用第一个 token 的全局表示。
2. motif 级分数 (s_{motif})：先经过残差一维卷积，再做长度维 max pooling。
3. 残基级语言模型分数 (s_{prob})：对目标残基的语言模型 log-probability 取平均（`.../model.py:273-284`）。

实现中最终输出为：

$$
s_{\mu Former}=\frac{s_{sem}+s_{motif}+s_{prob}}{2}。
$$

补充材料的消融实验显示，去掉语言模型时性能下降最明显；三个 scorer 一起使用通常最稳健（`supplementary/supplementary.md:37-71`）。这里的除以 2 是代码事实，论文正文中的正式方程在当前可访问的 Nature 预览中 **Not found**。

在 β-lactamase landscape 适配器中，模型还可将分数按野生型和 ESBL 中位数归一化：

$$
s_{norm}=\frac{s-s_{WT}}{s_{ESBL,median}-s_{WT}}。
$$

这是 `Mu-Protein/mu-search/src/flexs/flexs/landscapes/muformer.py:174-185,233-249` 的实现细节，正文定义仍是 **Not found**。

### μSearch 如何搜索

`MuSearch` 从输入 dataframe 中按 `true_score` 选择当前最佳序列作为起点，然后建立 `LandscapeEnv`，调用 PPO 学习（`mu-search/src/flexs/flexs/baselines/explorers/dirichlet_ppo.py:32-55`）。训练得到候选池后：

- 只保留超过 `score_threshold` 的序列；
- 将候选序列转换回字符串；
- 按预测分数排序；
- 返回需要实验验证的 batch（`.../dirichlet_ppo.py:57-74`）。

补充材料把多轮实验抽象成 ground-truth oracle φ 和用已测数据训练的局部 oracle φ̂′。每轮在固定模型调用预算内提议突变，再用 ground-truth 评价，并将结果用于下一轮更新（`supplementary/supplementary.md:140-152`）。

### 评估读法

补充材料报告了八组 DMS 数据上的 single-to-multi 任务、μFormer 消融、GB1/AAV 的 n-vs-rest 划分，以及 AdaLead、DyNA-PPO、CbAS、CMA-ES、Bayesian Optimization、PEX、GWG、EvoPlay 和随机搜索等比较（`supplementary/supplementary.md:37-90,117-180`）。GB1 残基留出实验中，只用 20% 残基训练时平均 Spearman ρ 为 0.46；两个位点都未见时为 0.36，一个位点未见时为 0.64（`supplementary/supplementary.md:92-115`）。

摘要还声称 μProtein 在 β-lactamase 湿实验中找到了高增益多位点突变，但完整实验步骤、全部数值表和正文 Methods/Results 在当前 Nature 访问范围内不可见，不能据此补写复现实验协议。

### 使用时的注意事项

仓库结构、核心模型和搜索路径是可追踪的，但复现度只能评为中等：主文 PDF 下载得到的是访问页面而非 PDF；模型 checkpoint 使用 Git LFS；一个 landscape 文件把 ESBL CSV 写成了作者机器的绝对路径。应先修正路径、准备数据/权重，并取得论文缺失的 Methods/Results 后再进行严格复现实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## μProtein Summary

### Problem

Protein engineering searches a combinatorial mutation space with far fewer laboratory measurements than possible sequences. The paper introduces μProtein to use single-mutation assay data to predict and search for high-fitness multi-point variants while accounting for epistatic interactions (`paper.md:9-12`).

### Existing-Method Limitations

The accessible paper preview does not include the full related-work or Methods narrative. The references and supplementary comparisons identify sequence/fitness predictors and search baselines including ECNet (*Nature Communications*, 2021), Tranception (ICML, 2022), AdaLead (arXiv, 2020), DyNA-PPO (2019), CbAS (arXiv, 2019), CMA-ES, Bayesian Optimization, PEX (ICML, 2022), GWG (2024), and EvoPlay (*Nature Machine Intelligence*, 2023). The supplementary setup motivates the need for data-efficient prediction of high-order mutants and for exploration under a fixed model-call budget (`supplementary.md:37-71,92-115,117-152`).

### Proposed Framework

μProtein couples:

1. **μFormer**, a pretrained protein-language-model encoder with semantic, motif and language-model probability scoring components. The checked-out implementation returns `(s_sem + s_motif + s_prob) / 2` (`mu-former/src/model.py:225-314`).
2. **μSearch**, a PPO-based explorer that uses μFormer as a fitness oracle, starts from the highest measured sequence, proposes candidates in a FLEXS environment, filters by a score threshold and returns a ranked batch (`mu-search/src/flexs/flexs/baselines/explorers/dirichlet_ppo.py:10-74`).

For TEM-1, the search landscape optionally normalizes predicted fitness relative to wild type and the median ESBL score (`mu-search/src/flexs/flexs/landscapes/muformer.py:172-185,233-249`).

### Evaluation

The supplementary ablation evaluates eight deep-mutational-scanning datasets in a single-to-multi setting. Removing the language model produces the largest average performance loss, and the full multi-level scorer generally outperforms ablated variants (`supplementary.md:37-71`; local Extended Data Fig. 1). On FLIP GB1, μFormer exceeds ECNet and its encoder-swapped variant across 1-vs-rest, 2-vs-rest and 3-vs-rest settings (Extended Data Fig. 1b). In a GB1 unseen-residue experiment, μFormer-SS reaches average Spearman $\rho=0.46$ with only 20% of residues used for training; at that ratio, $\rho=0.36$ for double mutants with both residues unseen and $0.64$ when one residue is seen (`supplementary.md:92-115`; Extended Data Fig. 2). μSearch is compared with eight exploration algorithms plus random selection over TF-binding, RNA, AAV, GFP and Rosetta FLEXS landscapes (`supplementary.md:117-173`). Supplementary Table 3 reports model-call ratios of 26.3 at threshold 0.05, 102.8 at 0.07 and greater than 143 at 0.08 for μSearch versus random sampling (`supplementary.md:174-190,282-316`). The abstract and Fig. 6 caption state that μProtein produced high-gain multi-point TEM-1 β-lactamase variants validated in wet laboratory (`paper.md:9-12,83-85`), but the full experimental narrative is inaccessible.

### Reproducibility

Code is publicly linked to GitHub and Zenodo, and FLIP/ProteinGym/split data are linked in the preview (`paper.md:96-100`). This workspace contains the Mu-Protein repository at commit `be65887f86628ade657dae2c14757f9f84ecee83`, model source, training scripts, FLEXS integration and README examples. It does **not** contain the large search checkpoints referenced by `mu-search/README.md`, and the landscape code reads the ESBL CSV through a hard-coded working-directory-relative path (`muformer.py:154-182`). Nature HTML is a subscription preview and the retained `paper.pdf` is an HTML access diagnostic, not a PDF; therefore this analysis cannot claim full article-level reproducibility.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
