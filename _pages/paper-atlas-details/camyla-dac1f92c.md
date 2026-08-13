---
layout: default
permalink: /paper-atlas/camyla-dac1f92c/
title: "Camyla"
nav: false
wide: true
description: "Camyla 的输出可以包含新网络，但 Camyla 本身是一个自主研究系统。输入是医学图像分割数据集和配置，系统负责建立强 baseline、检索文献、生成研究提案、编写候选网络、训练与评估、根据失败诊断继续搜索、对最终方法做消融，并生成可编译论文。 它要解决的不是单次代码生成，而是长达许多轮实验时的三个管理问题：有限 GPU 预算该投到哪个提案；大量日志怎样压缩而不遗忘关键经验；一个实验失败后怎样避免围绕同一个小修小补反复打转。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>arXiv · 2026</span>
    </div>
    <h1>Camyla</h1>
    <p>Camyla: Scaling Autonomous Research in Medical Image Segmentation</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2604.10696" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Camyla">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/yifangao112/camyla" target="_blank" rel="noopener noreferrer" aria-label="Open code for Camyla">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Camyla：把医学图像分割研究组织成可执行的自主实验循环

### 先澄清：Camyla 不是一个分割网络

Camyla 的输出可以包含新网络，但 Camyla 本身是一个自主研究系统。输入是医学图像分割数据集和配置，系统负责建立强 baseline、检索文献、生成研究提案、编写候选网络、训练与评估、根据失败诊断继续搜索、对最终方法做消融，并生成可编译论文。

它要解决的不是单次代码生成，而是长达许多轮实验时的三个管理问题：有限 GPU 预算该投到哪个提案；大量日志怎样压缩而不遗忘关键经验；一个实验失败后怎样避免围绕同一个小修小补反复打转。对应机制分别是 Quality-Weighted Branch Exploration（QWBE）、Layered Reflective Memory（LRM）和 Divergent Diagnostic Feedback（DDF）。

### 实验底座 CamylaNet

所有候选方法必须在同一训练和评价合同下比较。论文把底座抽象为三个操作：

$$
\operatorname{plan\_and\_preprocess}(d,C)\rightarrow\pi,
$$

$$
\operatorname{training\_network}(d,c,\mathcal T,\pi)\rightarrow(\mathcal R,\ell),
$$

$$
\operatorname{evaluate}(d,\mathcal R)\rightarrow\mathcal M.
$$

$d$ 是数据集，$C$ 是 2D/3D 配置，$\pi$ 是 nnU-Net 式 fingerprint/预处理计划，$\mathcal T$ 是 trainer，$\mathcal R$ 是 checkpoint/预测目录，$\mathcal M$ 包含 Dice 和 HD95。LLM 主要覆盖一个 trainer 的 `build_network_architecture`，而数据加载、增强、soft Dice+cross-entropy loss、poly 学习率、checkpoint 和验证沿用基础设施。

候选代码先跑完整的一 epoch 验证，确保加载、前向、反向、梯度更新和预测导出都能执行，再投入昂贵的全训练。这只能排除运行级错误，不保证方法合理或最终性能好。

Stage 1 从 14 种已预训练架构中按数据集选择最强 baseline；本地 `screen_trainers.py:22-42` 列出 2D/3D 兼容的 SwinUNETR、SegResNet、U-Mamba、MedNeXt 等 trainer。baseline bank 是外部结果资产，Camyla 仓库本身没有随代码打包全部 checkpoint。

### 四阶段主流程

#### Stage 1：建立公平基线

数据先转换为 nnU-Net 合同并做统一预处理，再载入每个兼容 baseline 的结果。最优 baseline $b^*$ 不只是最终比较对象，也进入后续 agent context，决定 Q 值归一化和何时从广度搜索切到深度优化。

论文规定 primary metric 是前景类 mean Dice，secondary metric 是 HD95。候选若 Dice 比 baseline 高超过 0.005 即胜出；若 Dice 差异小于 0.005，则 HD95 严格更低者胜。代码 `TIEBREAK_THRESHOLD=0.005` 并允许配置覆盖（`camyla/treesearch/utils/metric.py:8-17`）。0.5 percentage point 是防止微小 Dice 波动被宣称为改进的操作阈值，不等于统计显著性。

#### Stage 2：文献驱动的实验发现

系统先从 Semantic Scholar/OpenAlex/PubMed 检索与数据模态、解剖部位和分割困难相关的工作，迭代提取未解决 challenge，再汇聚成约三个主题。每个主题由 creative、technical、medical 三种生成角色提出候选，assessment agent 按可验证性、创新性、可信度、目标一致性和逻辑一致性等维度评估。当前 `config_example.yaml` 的公开权重实际列出五项；论文正文称六维并包含 modularity，说明完整 tournament 规则还部分依赖 prompt/skills 文档，不能只从 Python dataclass 推断。

被接受提案进入负约束列表，要求后续提案与已有方向不同。每个提案应明确模块、数学动机和可消融组件，使“创新”能变成 trainer 中可执行的网络修改。

#### Stage 3：消融验证

搜索到胜者后，系统规划每个模块的替代版本，以 identity 或标准卷积等最小替代物移除模块，并从头训练。这比只关一个开关更接近模块贡献验证，但自动生成的消融仍需检查是否真的只改变目标组件、训练预算是否一致。

#### Stage 4：论文生成

写作不是直接总结聊天记录。`generate_paper()` 主链先做 proposal–implementation reconciliation，用最终代码纠正原提案中被删减、简化或新增的组件；再汇总结果和消融，生成数据驱动图、方法图、LaTeX 正文与引用，最后执行结构和风格修订。入口 `launch_camyla.py:451-488` 依次调用 baseline、QWBE 实验和 `generate_paper`；具体写作流程在 `paper_generation_api.py:311` 之后。

自动编译 PDF 证明工件完成，不证明论文的临床意义、创新性或统计结论已经通过真实同行评审。

### QWBE：把多提案搜索变成带新分支动作的 bandit

每个 proposal 是一个 branch，branch 下的节点是连续修改/实验。尚未打败 baseline 时，Phase 1 用 PUCT 式分数：

$$
\operatorname{Score}_i=Q_i+c_{puct}P(Q_i)\frac{\sqrt{N_{total}}}{1+N_i}.
$$

$Q_i$ 是该分支非 stale 节点的平均归一化质量，$N_i$ 是分支访问/扩展数。风险规避 prior 为

$$
P(Q_i)=\max(0,1+Q_i)^p,
$$

默认 $p=3$。差分支的探索 bonus 被强烈压低，正质量分支获得放大；这使预算更快集中，但也可能过早放弃尚未实现正确的高潜力方向。

“再开一个新提案”也作为选择：

$$
\operatorname{Score}_{new}=c_{puct}\frac{\sqrt{N_{total}}}{1+K},
$$

$K$ 是已有 branch 数。实现中 `N_total = K + sum(N_i)`（`parallel_agent.py:1766-1772`），所以它与最常见的“总访问次数”定义略有区别。branch score 和 risk prior 逐项计算于 `:1783-1798`。

实现还排除旧周期的 `is_stale` 节点，避免过时试验污染 branch 均值（`parallel_agent.py:1686-1709`）。分支内部选择当前最佳可扩展 leaf，而不是再跑一次同样的全局 PUCT。

一旦任何节点按 Dice/HD95 规则打败 baseline，系统进入 Phase 2，改成围绕全局最好节点深度优先优化。也就是说，QWBE 的目标是尽快找到一个胜者后精炼，而不是穷尽整个创新空间。

### Q 值归一化与失败节点

原始 Dice $m$ 相对 baseline $m_0$ 映射到 $[-1,1]$：

$$
q(m)=\begin{cases}
\dfrac{m-m_0}{\max(1-m_0,\varepsilon)},&m\ge m_0,\\
-\min\left[1,\left(\dfrac{m_0-m}{\max(m_0,\varepsilon)}\right)^e\right],&m<m_0.
\end{cases}
$$

代码 `parallel_agent.py:1562-1584` 精确实现，默认 $e=1$，$\varepsilon=10^{-8}$。这个非对称缩放让 baseline 映射为 0、完美 Dice 映射到约 1，而下降按 baseline 比例惩罚。

若 OOM、shape mismatch 或 NaN 导致无有效 metric，系统不一定把整个研究方向判死。它找最近一个有 metric 的 ancestor，并设

$$
q_{error}=\max[-1,q_{ancestor}-\delta],\qquad\delta=0.2.
$$

实现位于 `parallel_agent.py:1586-1609`。这体现“bug 通常是局部实现失败”的假设；若根本设计不可行，这种继承可能又过于宽容，因此还需要 DDF 判断 `proposal_infeasible`。

### LRM：不是保留全部日志，而是分层蒸馏

每轮实验产生代码差异、训练日志、metric、异常和诊断。把全部原文塞回 agent 会让上下文膨胀并重复旧错误。LRM 分为：

- trial-level：当前实现、运行结果、错误与直接建议；
- cycle-level：一个 proposal/周期内多个 trial 的结构化总结；
- global-level：跨 branch 保留哪些策略有效、哪些失败模式重复、胜者具有什么特征。

下一轮编码 agent 主要收到决策相关摘要，而不是所有 raw logs。`log_summarization.py` 中的 `generate_paper_ready_summary` 与 `overall_summarize` 负责不同层级的压缩。压缩提高长程可用性，也可能丢掉看似次要却关键的配置细节；所以论文生成前还要用最终代码和结构化结果重新对齐，而不能只信 memory 文本。

### DDF：强制产生五种可选修复，而不是一个答案

当 trial 低于预期，DDF 接收 proposal、当前代码、历史和 performance gap，输出 diagnosis 与恰好五条建议。JSON schema 将 `improvement_suggestions` 的 `minItems`、`maxItems` 都设为 5（`proposal_diagnostic.py:45-97`），类别限制为 architecture、hyperparameter、code_fix、proposal_gap。

这不是普通提示语，而是结构约束。若 diagnosis 判为 `proposal_infeasible`，系统可请求修改提案；提案修改预算耗尽后，第二 schema 只允许 `code_issue`。五条建议形成 portfolio，两个 coding agents 独立挑选 1–2 条实现，从同一诊断派生不同分支。

论文强调至少包含 proposal_gap，以检查提案里承诺的模块是否在代码中缺失/简化。schema 允许该类别，但“每次至少一条”的硬保证还依赖 prompt/后处理，单从 `enum` 与数组长度不能证明类别覆盖必然满足。

### 双 agent 竞争与实验隔离

选定节点后，两名 agent 独立生成实现，系统在相同数据、训练 budget 和评估协议上竞争。代码执行放到隔离 subprocess，减少上个 trial 的 Python/GPU 状态泄漏。动态 timeout 会随 epoch 数放大，避免把长训练误判成挂起；这也意味着配置中的基础 timeout 不是每次实验的实际固定上限。

竞争可以扩大局部多样性，但两个 agent 仍受同一 LLM 能力、提示、trainer 接口和建议 portfolio 限制。需要自定义 CUDA、改变整个优化框架或不能适配 nnU-Net trainer contract 的想法更难进入搜索空间。

### 图和实验结果怎样支持论文主张

- 图 1 给出两个独立 run 相对 baseline 的逐数据集增益、与六种开放式研究 agent 的完成率，以及自动论文的 reviewer tier。它支持“系统能完成任务并常超过 baseline”，但 tier 分数不是正式期刊录用。
- 图 2 是方法总图：baseline bank → 文献提案 → QWBE/双 agent/训练评估 → LRM/DDF 回路 → 消融与论文。它定义 Camyla 本体的边界。
- 结果增益图把 Camyla_D 与 Camyla_S 的 $\Delta$Dice/$\Delta$HD95 分开显示，说明不同 idea model 找到的收益模式互补，也清楚展示多个数据集回退。
- 机制消融在五个开发数据集上移除 LRM、QWBE、DDF：完整系统胜出数、平均增益和 first-success position 整体更好。样本只有五个验证任务，因此证据支持互补性，但不足以精确估计每个机制在全部医学分割域的独立因果效应。
- Appendix 图展示 dataset 难度、搜索轨迹、proposal 分配、失败恢复与论文评价细节，为过程主张提供证据；附录位于同一 `paper.md` 与抽取图片中，没有独立 supplementary 文件。

论文报告 CamylaBench 31 个 2025 年数据集、12 个解剖区域、10 种模态；两个 run 在全 31 个数据集分别超过 strongest baseline 22 和 18 个，union 为 24/31。盲测 26 个数据集上两个 run 都完成 26/26。这里的“超过”遵循 0.5pp Dice/HD95 tiebreak，不应与所有数据集上的统计显著或临床改善混为一谈。

### 本地代码覆盖与复现边界

固定快照是 `https://github.com/yifangao112/camyla` commit `df4434f9d4aef5b7394ed03a4e877a8130c1b6cf`。

**直接覆盖**：CLI 编排、baseline 加载、文献 agent、proposal 队列、QWBE 分数/Q 归一化/stale 过滤、DDF schema、metric tiebreak、LRM 总结、消融规划和六步论文生成均有实现。核心公式与代码高度一致。

**外部依赖**：CamylaNet、nnPrep、nnU-Net 数据/结果目录、14 baseline checkpoint、OpenHands/容器环境、多个 LLM 与文献 API、方法图生成 API。公开仓库不能单独重建 31 数据集的 28 天双 run。

**随机与时变因素**：proposal、诊断、代码和写作依赖特定服务端模型版本；即使固定 temperature/config，供应商模型更新和非确定采样也会改变轨迹。复现更合理的层级包括验证单一已记录 trajectory、重放 CamylaTrace，或在一个数据集上确认机制，而不是期待逐节点完全相同。

**评价边界**：每数据集最强的 14-architecture baseline 很强，但同一开发框架与训练预算仍限制比较范围；2025-only benchmark 降低预训练数据污染风险，却不能证明任意闭源 LLM 从未接触这些网页/摘要。医学分割性能也没有覆盖部署安全、校准、亚组公平和临床效用。

### 怎样正确阅读 Camyla 的贡献

Camyla 的核心创新不是它在某个数据集上自动写出的卷积模块，而是把自主科学搜索变成带状态的闭环：强 baseline 给出共同零点，QWBE 决定预算去向，LRM 保存跨轮经验，DDF 产生结构化分歧，双 agent 把分歧变成可比较实现，统一训练合同产生证据，最后用代码–提案 reconcile 和消融约束论文叙述。

这个闭环显著提高了任务完成率和超过 baseline 的频率，但“系统成功运行”“Dice 更高”“自动论文可读”仍是三个不同层级的结论。真正使用时应分别审计搜索公平性、代码正确性、统计独立性、临床意义和写作证据，不能由最后生成了 PDF 就自动推导科学结论成立。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Camyla: Scaling Autonomous Research in Medical Image Segmentation

**Paper:** arXiv 2604.10696 | **Journal:** arXiv preprint (2025/2026) | **DOI:** 10.48550/arXiv.2604.10696
**Authors:** Yifan Gao, Haoyue Li, Feng Yuan, Xin Gao, Weiran Huang, Xiaosong Wang

---

### Motivation & Novelty

#### The Problem

Medical image segmentation is a demanding scientific domain with well-defined benchmarks and strong automated baselines. Despite this, developing competitive new methods remains labor-intensive: generating hypotheses, writing and debugging code, running experiments across diverse datasets, and synthesizing findings into papers requires sustained human expertise over weeks or months.

Prior automation approaches address parts of this pipeline but not the whole:
- **NAS / AutoML** (nnU-Net, Auto-nnU-Net [AutoML conf., 2025], DiNTS [CVPR, 2021], AutoSeg3D): optimize within a fixed, human-designed search space; cannot propose qualitatively new modules; produce no research insights or manuscripts.
- **General-purpose research agents** (autoresearch [Karpathy, GitHub, 2026], AI Scientist [arXiv, 2024], AI Scientist-v2 [arXiv, 2025]): can plan, code, and write papers but lack domain-specific infrastructure to enforce experimental rigor; completion rates of 46–69%; substantial proposal drift.
- **Domain-specific research** (Medical AI Scientist [arXiv, 2026]): tailored to clinical research but defines success as executable code (not baseline-surpassing performance); single-pass pipeline without tree search or performance-aware diagnostic feedback; evaluated on 5 papers against 15 references from a single task.

#### What's New

Camyla occupies a new position: an **open-ended research agent with domain-specific infrastructure** that:
1. Generates literature-grounded research proposals (not generic suggestions)
2. Implements and evaluates them through **structured tree search with quality-weighted resource allocation** (QWBE) — not random or greedy
3. Maintains **hierarchically compressed experimental knowledge** across trials (LRM) — not raw log injection
4. Recovers from failure through **categorically diverse diagnostics** (DDF) — not single-point prescription
5. Produces complete manuscripts from experimental evidence, with reproducibility

The three coupled mechanisms (QWBE + LRM + DDF) form a mutually conditioning system: DDF generates the diversity that LRM compresses and QWBE exploits. Removing any one degrades performance (ablation: −50% wins without LRM on most demanding datasets).

---

### Method Overview

#### Algorithmic Framework

Camyla operates as a four-stage closed-loop pipeline:

**Stage 1 — Baseline Establishment:** A precomputed bank of 14 architectures (nnU-Net, U-Mamba, MedNeXt, SwinUNETR, STU-Net, UKAN, UNETR, nnFormer, 3D UX-Net, TransUNet, UTNet, SwinUMamba, SegResNet, U-Net++) is evaluated on the target dataset. The per-dataset best ($b^*$) serves as the reference.

**Stage 2 — Experimental Discovery:** Literature search generates up to $K$ research proposals via a multi-agent tournament. QWBE allocates the iteration budget $N$ across proposals using PUCT-style scoring (Eq 4-6) with a risk-averse prior $P(Q_i) = \max(0, 1+Q_i)^3$ that suppresses exploration of consistently low-quality branches. LRM maintains three memory tiers (trial-level modification records, cycle-level structured histories, global scientific digest) to bound context contamination. DDF generates 5-suggestion portfolios (architecture / hyperparameter / code_fix / proposal_gap) after each underperforming trial; dual coding agents independently select which suggestions to pursue.

**Stage 3 — Ablation Verification:** Each proposed module is systematically removed and the model retrained from scratch.

**Stage 4 — Manuscript Generation:** A 6-step pipeline (methodology reconciliation → result analysis → figure generation → paper writing → citation management → automated revision) produces a LaTeX-compiled PDF. Architecture diagrams are generated post-text to match notation.

#### Key Technical Components

- **CamylaNet:** Domain-specific workbench wrapping nnU-Net v2. A new architecture requires only overriding `build_network_architecture(channels, classes, params) → nn.Module`; all other infrastructure (preprocessing, augmentation, soft Dice + cross-entropy loss, polynomial LR decay, evaluation) is inherited. One-epoch verification catches shape mismatches before full training.
- **QWBE:** The risk-averse prior is the mathematical key — a branch with $Q_i = -1$ receives zero exploration pressure, while one at $Q_i = +0.5$ receives $3.4\times$ amplification. This prevents budget waste on demonstrably failing directions while aggressively deepening promising ones. Phase 2 switches to deterministic depth-first once $b^*$ is beaten.
- **LRM:** Trial-level records are 2-3 sentence compression of what changed and why. Cycle-level records include structured history with outcome status (baseline/success/underperforming/error), metrics, and truncated diagnostic. Global memory grows sublinearly via progressive compression.
- **DDF:** The `proposal_gap` category is the most distinctive — it forces the diagnostic agent to explicitly compare the proposal against the implementation and identify cases where a coding agent substituted a sophisticated proposed module with a trivial placeholder (e.g., adaptive tokenization → fixed-grid pooling).

#### Biological / Clinical Assumptions

- Performance measured by mean Dice coefficient and HD95 following nnU-Net protocol
- All datasets preprocessed identically (fingerprint-based, modality-appropriate normalization)
- Evaluation on held-out fold(s) via nnU-Net cross-validation
- Results are dataset-specific — no claims about generalizability beyond medical image segmentation

---

### Evaluation

#### Benchmark: CamylaBench

31 datasets sourced exhaustively from *Scientific Data* 2025 (all segmentation datasets published that year with publicly available images and annotations), ensuring zero contamination. Spans 12 anatomical regions, 10 imaging modalities, training sizes 24–10,662 cases, foreground classes 1–10. Baseline Dice range: 14.2% (endoscopic instrument segmentation) to 96.2% (dental panoramic radiography), median 71.4%.

5 datasets (1–5) served as validation during development; 26 are blind-test.

#### Main Results

| System | Completed | >Baseline | Mean Dice |
|---|---|---|---|
| **Camyla_D (DeepSeek V3.2)** | 26/26 (100%) | 18/26 (69.2%) | 65.91% |
| **Camyla_S (Claude Sonnet 4.6)** | 26/26 (100%) | **18/26 (69.2%)** | 65.16% |
| **Union (24/31 all datasets)** | — | **20/26 (76.9%)** | — |
| Claude Code + Opus 4.6 | 18/26 (69%) | 10/26 | 63.14% |
| Claude Code + MiniMax 2.5 | 15/26 (58%) | 12/26 | 62.58% |
| AI Scientist | 18/26 (69%) | 5/26 | 60.24% |
| AI Scientist-v2 | 12/26 (46%) | 3/26 | 58.73% |
| Auto-nnU-Net | 31/31 | — | 64.27% |
| DiNTS | 31/31 | — | 58.03% |

Key points:
- **100% completion** for both runs vs. 46–69% for all research agent baselines
- **Zero proposal drift** (structured proposal management prevents implementation shortcuts)
- **Camyla_S wins 11/22 by HD95** (boundary precision), vs. Camyla_D which wins predominantly via Dice (+16/18) — different LLM idea generators produce complementary improvement modalities
- **Largest single-dataset gain:** NLSTseg (Dataset 5, baseline 23.2%) → above 41% for both runs (+18.58 pp for Camyla_D)

#### Statistical Significance

- Camyla_S win rate (22/31): binomial test $p = 0.015$ under conservative null ($p_0 = 0.5$)
- Union rate (24/31): $p = 0.002$
- 70% of winning experiments significant on at least one metric (Wilcoxon signed-rank per-sample)
- 20/40 survive Bonferroni correction ($\alpha = 0.05/40 = 0.00125$)

#### Failure Analysis

7 datasets resist both runs (Datasets 2, 13, 17, 22, 23, 27, 29). Two structural patterns:
1. High-ceiling baselines with narrow improvement margin (Dataset 13: 96.2%, Dataset 29: 92.2%)
2. Multi-class tasks with high inter-structure variability where a single modification cannot produce uniform gains (Dataset 2: 10 foreground classes; Dataset 22: 4 classes)

#### Manuscript Quality

- Senior human reviewers (5): Internal = 3.311, T1 = 3.364, T2 = 3.217 → **at T1/T2 boundary**
- AI average (5 frontier models): Internal = 3.610, T1 = 3.644 → **at T1 level**
- Stanford Agentic Reviewer: Internal blind-test = 4.766, T2 = 4.603, T1 = 5.690 → **above T2, approaching T1**

Ablation results (5 validation datasets): Full Camyla (4/5 wins, mean ΔDice +1.85 pp, mean FSP 4.8) vs. −LRM (2/5 wins, +0.47 pp, FSP 6.3), −QWBE (3/5, +1.31 pp, FSP 9.5), −DDF (3/5, +1.02 pp, FSP 7.3).

#### Computational Cost

- Total: 5,461.9 GPU-hours on NVIDIA RTX 4090 48GB across 62 experiments (~28 days)
- Mean 88.1 h/experiment (median 34.2 h)
- LLM API cost: $23–$26 per dataset
- Successful experiments: 64.9 h/experiment (vs. 130.3 h for failed — early stopping saves budget)

---

### Reproducibility Rating: **3 / 5**

**Justification:**

**What enables reproducibility (+):**
- Code is publicly released at https://github.com/yifangao112/camyla
- CamylaBench is sourced from public 2025 Scientific Data publications (all datasets publicly available)
- CamylaTrace-232k trajectory dataset released (232,499 agent events, 1,343 code files)
- Config-driven architecture: `config_example.yaml` fully documents all hyperparameters
- CamylaNet wraps nnU-Net v2 — a well-established, reproducible baseline

**What limits reproducibility (−):**
- **14 baseline models must be pretrained externally** via `camylanet_results` env var; no automated download script for precomputed results
- **External sister repos required:** CamylaNet (`yifangao112/CamylaNet`) and nnPrep (`yifangao112/nnPrep`) must be installed separately; not bundled
- **LLM API dependency**: Results depend on specific model versions (DeepSeek V3.2, Claude Sonnet 4.6); output will vary with model updates
- **OpenHands dependency**: Code generation requires OpenHands framework (separate installation, Docker)
- **28-day compute requirement**: Full reproduction requires an 8-GPU cluster and ~4 weeks per run; not feasible for most labs
- **Prompt templates are markdown files** in `skills/` — minor prompt changes could substantially affect proposal quality
- **Stage 4 uses Gemini 3.1 Flash Image Preview** for architecture diagram generation — requires Google API key

**Practical notes:**
- The system can be run on individual datasets (not all 31 simultaneously), which greatly reduces compute
- For verification purposes, CamylaTrace-232k enables replay/analysis without re-running experiments
- The `--debug-baseline` flag enables quick testing with fake metrics (dice=0, hd95=200)

---

### Cross-References

- Mathematical derivations: → `doc_method.md` (QWBE Equations 4-8, Q normalization, LRM tiers, DDF portfolio)
- Code-paper mapping: → `doc_code.md` (exact line references for all core mechanisms)
- Figure analysis: → `figure_analysis.md` (panel-by-panel breakdown of all 10 figures)
- Experimental trajectories: → `claude_notes.md` (evidence ledger, dataset-16 full trajectory)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
