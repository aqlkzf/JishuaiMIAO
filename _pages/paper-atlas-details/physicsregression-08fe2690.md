---
layout: default
permalink: /paper-atlas/physicsregression-08fe2690/
title: "PhysicsRegression"
nav: false
wide: true
description: "论文研究的是从观测数据中恢复可解释的物理公式。传统符号回归在表达式复杂、候选空间很大时搜索成本高，也难以同时保证拟合精度、符号正确性和物理量纲一致性（PAPERMD:12）。 PhyE2E 将神经网络的表示能力与符号表达式的结构约束结合起来：先用二阶神经网络导数进行 divide-and-conquer 分解，再由 Transformer 将数据翻译成符号 token 序列，解码时加入物理单位信息，最后用 Monte Carlo tre…"
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
      <span>Machine Learning Algorithm</span>
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>PhysicsRegression</h1>
    <p>A neural symbolic model for space physics</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Jie0618/PhysicsRegression" target="_blank" rel="noopener noreferrer" aria-label="Open code for PhysicsRegression">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PhyE2E 方法说明

### 要解决的问题

论文研究的是从观测数据中恢复可解释的物理公式。传统符号回归在表达式复杂、候选空间很大时搜索成本高，也难以同时保证拟合精度、符号正确性和物理量纲一致性（`paper source:12`）。

### 核心想法

PhyE2E 将神经网络的表示能力与符号表达式的结构约束结合起来：先用二阶神经网络导数进行 divide-and-conquer 分解，再由 Transformer 将数据翻译成符号 token 序列，解码时加入物理单位信息，最后用 Monte Carlo tree search（MCTS）和遗传编程精修表达式。图 1 直接展示了这一流水线（`paper source:58-60`）。

```text
观测/合成数据
   -> 表达式分解与重采样
   -> Transformer 编码器-解码器
   -> 符号 token 与单位解码
   -> MCTS / 遗传编程 / 系数精修
   -> 可解释的物理公式
```

代码中 `TransformerModel` 定义编码器、解码器、注意力和可选量纲 mask，并提供自回归生成；`Equation.decode` 将 token 还原为表达式树，`check_units` 检查加减乘除、幂和变量的单位约束；`evaluate_oracle_mcts` 串联 oracle 候选、MCTS 和遗传编程精修（代码位置见 `doc_code.md`）。这些是直接代码证据。论文预览没有给出 Methods 全文，因此二阶导数的精确定义、损失函数、训练超参数和数据划分属于 `MISSING`。

### 评估与空间物理应用

图 2 在 Synthetic 和 AI Feynman 数据集上比较符号准确率、\(R^2>0.99\) 的比例和单位准确率。Extended Data Fig. 1 展示了不同分解/阈值策略以及去掉单位解码和物理先验后的消融；标准配置在图示指标上更好。图 3–5 覆盖太阳黑子强度、近地等离子体片压力、太阳差分自转、发射线贡献函数和月潮等离子体层信号五个应用。

### 可复现性边界

论文提供 GitHub/Zenodo 代码链接和 Figshare 预训练数据链接（`paper source:87-90`, `176-177`）。因此应将本分析的复现评级视为中等，并在运行前补齐这些外部材料。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## A neural symbolic model for space physics

### Problem

Symbolic regression can discover interpretable physical laws but is difficult to scale and search reliably over complex expressions. The paper proposes PhyE2E, a neural-symbolic framework for recovering formulas from observational datapoints (`paper source:12`).

### Proposed method

PhyE2E decomposes expressions using second-order neural-network derivatives, trains a Transformer to translate datapoints into symbolic token sequences, enforces physical-unit structure during decoding, and refines candidates with MCTS and genetic programming. Fig. 1 visually confirms this staged architecture (`paper source:58-60`); the linked implementation contains the corresponding Transformer, token/unit encoder, evaluator, MCTS, GP and BFGS components.

### Evaluation and applications

Fig. 2 compares PhyE2E with symbolic-regression baselines on synthetic and AI Feynman data using symbolic accuracy, fit quality (including the fraction with \(R^2>0.99\)) and unit accuracy. Extended Data Fig. 1 ablates decomposition strategies, unit decoding and physical priors. Figs. 3–5 show applications to sunspot intensity, near-Earth plasma-sheet pressure, solar differential rotation, emission-line contribution functions and lunar-tide plasma signals. The figures support the direction of the reported gains, but the acquired Nature HTML does not expose the full Results text or numeric tables.

### Reproducibility

The paper links the `Jie0618/PhysicsRegression` repository and a Zenodo release (`paper source:87-90`, `paper source:176-177`). The snapshot includes training/evaluation Python code, six application/benchmark artifacts, pretrained `model.pt`, Feynman data and result CSVs. Code-paper fidelity is **medium**: core architecture and refinement paths match directly, but exact paper equations, dataset manifests, hyperparameters, supplementary source data and executed application runs are **MISSING**. Reproduction therefore requires consulting the supplementary PDF/data links and running the provided scripts/notebooks in a compatible environment.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
