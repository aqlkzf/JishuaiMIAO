---
layout: default
permalink: /paper-atlas/alphatensor-quantum-reusability-report-06e88b50/
title: "AlphaTensor_Quantum_Reusability_Report"
nav: false
wide: true
description: "容错量子计算中，T 门的实现成本很高，因此需要在上硬件前尽量降低量子线路的 T count。AlphaTensor-Quantum 把线路优化改写为二元签名张量的分解搜索；本文进一步问：能否训练一个覆盖多个量子比特数的通用 agent，避免每遇到新的线路族就重新训练？ 编译得到只含 CNOT+T 的线路后，构造对称的二元签名张量 S。"
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
      <span>Computational Tools</span>
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>AlphaTensor_Quantum_Reusability_Report</h1>
    <p>Reusability report: Optimizing T count in general quantum circuits with AlphaTensor-Quantum</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-025-01166-9" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for AlphaTensor_Quantum_Reusability_Report">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/google-deepmind/alphatensor_quantum" target="_blank" rel="noopener noreferrer" aria-label="Open code for AlphaTensor_Quantum_Reusability_Report">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## AlphaTensor-Quantum 方法说明

### 要解决的问题

容错量子计算中，T 门的实现成本很高，因此需要在上硬件前尽量降低量子线路的 T count。AlphaTensor-Quantum 把线路优化改写为二元签名张量的分解搜索；本文进一步问：能否训练一个覆盖多个量子比特数的通用 agent，避免每遇到新的线路族就重新训练（`paper.md:25-34,71-80`）？

### 核心表示与动作

编译得到只含 CNOT+T 的线路后，构造对称的二元签名张量 `S`。一个动作选择非零二元因子 `u`，执行

`S <- S - (u tensor u tensor u) mod 2`。

公开代码在 `src/factors.py:32-54,75-90` 中实现因子编码和 GF(2) 秩一更新。环境在张量变为全零或达到最大步数时结束；Toffoli/CS gadget 完成时给予奖励折扣（`src/environment.py:109-196`）。线路到签名张量的通用转换不在该仓库中，README 指向独立的 `circuit-to-tensor` 仓库。

### 计算流程

```text
量子线路 -> CNOT+T 编译 -> 二元签名张量 S
       -> 零填充/随机换基 -> TensorGame 状态
       -> 张量、历史因子平面、步数标量
       -> 对称轴向注意力网络 + MCTS
       -> 选择因子并做 GF(2) 秩一更新
       -> 全零张量/步数上限 -> 分解与线路重建 -> T count
```

网络先把张量、最近因子外积平面和已进行步数投影到共同 embedding，再交替沿两个轴做 Transformer self-attention，并使用可学习的转置对称化层 `A X + (1-A) X.T`（`src/networks.py:145-182,185-253,256-310`）。默认配置是 16 个 attention heads、每头深度 32、4 层 torso（`src/config.py:82-114`）。

### 训练与评估

作者比较 Demo、RL 和 Demo + RL 三种训练。通用 agent 同时覆盖 5-8 个 qubit，single agent 每个 qubit 数单独训练；RL 使用 100,000 条随机线路，训练 100,000 步，每个 qubit 数评估 1,000 条线路。评估选择 MCTS 策略概率最大的动作，并以 PyZX+TODD 作为 baseline（`paper.md:77-91,138-146`）。新增的 improvement percentage 是 agent 严格优于 baseline 的线路比例。

### 主要结论

小规模复现可行，但 gadget 化的 NC Toff_3 和 Barenco Toff_3 结果与原报告不一致；增大 batch 和 MCTS 模拟数后有所改善（`paper.md:46-57`）。通用 agent 通常优于固定 qubit 的 agent，Demo + RL 最好；优势在 5-6 qubit 明显，到了 8 qubit 平均不如 baseline。训练很贵，但训练好的 agent 单次评估约 20 秒，因此适合被大量复用的线路 primitive（`paper.md:80-110`）。

### 可复现性边界

仓库 commit `3def81a2a42666416a4a8041eea6e1bc98bc8e9f` 提供 TensorGame、网络、gadget demonstration 和 MCTX demo，但没有原始 AlphaZero/MCTS 训练器、精确 checkpoint、通用随机线路生成器、PyZX/TODD 评估脚本或线路转换完整流程。论文明确说明公开 MCTX 版本不是生成本文结果的内部代码（`paper.md:40-49`），因此应将本工作视为中等可复现的独立复核与泛化实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

Fault-tolerant quantum circuits are costly, particularly in their number of T gates. AlphaTensor-Quantum uses reinforcement learning to search tensor decompositions that reduce this count, but the original approach trains separately for circuit families and can take minutes to hours per new circuit (`paper.md:25-34,40-49`).

### Contribution

This reusability report reproduces selected AlphaTensor-Quantum experiments and trains a general agent across random CNOT+T circuits with 5-8 qubits. It compares that agent with fixed-qubit single agents and with a PyZX+TODD baseline, using Demo-only, RL-only, and Demo + RL training (`paper.md:71-91,138-146`).

### Results

Small-scale reproduction is feasible. Mod 5_4 matches the reported T count with and without gadgets; public-code runs miss the reported gadgetized counts for NC Toff_3 and Barenco Toff_3, although larger batch/MCTS budgets improve them (`paper.md:46-57`). For random circuits, the general agent usually beats the single agent and Demo + RL is strongest. Gains are clearest at 5-6 qubits, weaken at 7, and at 8 qubits all agents are worse than the baseline on average, despite roughly 23% improvement (`paper.md:80-91`). A pretrained rollout averages about 20 seconds, versus hours of training, making amortization central to the use case (`paper.md:94-110`).

### Reproducibility

The public GitHub snapshot at commit `3def81a2a42666416a4a8041eea6e1bc98bc8e9f` contains the TensorGame, factors, signature-tensor examples, symmetrized axial-attention network, synthetic gadget demonstrations and an MCTX demo. It does not contain the result-producing AlphaZero/MCTS trainer, exact checkpoints, arbitrary circuit-to-tensor conversion, or the paper's general random-circuit and baseline runners. The paper explicitly says its results were not produced with this exact public MCTX implementation (`paper.md:40-49`); reproducibility is therefore medium rather than complete.

### Limitations

Action-space growth makes training time scale steeply with qubits; older GPUs run out of memory at 15 qubits (`paper.md:60-68`). The evaluation starts from circuits already optimized by PyZX and TODD, and the general-agent advantage declines with size. Exact original hyperparameters and internal infrastructure are unavailable, so the reproduction should be treated as evidence of feasibility and generalization, not a byte-for-byte replication.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
