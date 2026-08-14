---
layout: default
permalink: /paper-atlas/apexgo-e78ea4ab/
title: "ApexGO"
nav: false
wide: true
description: "ApexGO 解决的不是“从零生成任意抗菌肽”，而是一个更接近药物研发后期的任务：给定一条已经有实验基础的模板肽 x0，在尽量保留其序列骨架的前提下，寻找抗菌活性更强的衍生肽 x。 论文把目标具体化为两个条件： APEX 预测的最低抑菌浓度（MIC）要尽可能低； 候选肽与模板的编辑相似度至少为 75%。 因此，ApexGO 是一个“受约束的模板局部优化器”，而不是普通的无条件生成模型。 监督学习抗生素发现方法通常在已有分子或序列库中打分。"
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
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>ApexGO</h1>
    <p>A generative artificial intelligence approach for peptide antibiotic optimization</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Yimeng-Zeng/ApexGO" target="_blank" rel="noopener noreferrer" aria-label="Open code for ApexGO">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ApexGO 方法详解

### 1. 它真正要解决什么问题？

ApexGO 解决的不是“从零生成任意抗菌肽”，而是一个更接近药物研发后期的任务：给定一条已经有实验基础的模板肽 $x_0$，在尽量保留其序列骨架的前提下，寻找抗菌活性更强的衍生肽 $x$。

论文把目标具体化为两个条件：

1. APEX 预测的最低抑菌浓度（MIC）要尽可能低；
2. 候选肽与模板的编辑相似度至少为 75%。

因此，ApexGO 是一个“受约束的模板局部优化器”，而不是普通的无条件生成模型（论文：`paper.md:31-37,199-202,265-289`）。

### 2. 为什么已有方法不够？

#### 固定库筛选

监督学习抗生素发现方法通常在已有分子或序列库中打分。例如论文引用的深度学习抗生素筛选工作发表于 *Cell* 2020、*Nature Chemical Biology* 2023 和 *Nature* 2024。它们能高效排序固定候选，但不能主动提出数据库里不存在、又围绕某个先导骨架的局部修改。

#### 一次性生成

HydrAMP（*Nature Communications*, 2023）和 PepDiffusion（*Science Advances*, 2025）面向多样化抗菌肽生成。它们擅长从训练分布中采样“像抗菌肽”的序列，却没有把“与指定模板至少 75% 相似”作为闭环搜索目标。论文报告：HydrAMP 在该约束下只有少量样本可行，PepDiffusion 的一百万条候选中没有一条达到阈值（`paper.md:304-316`）。这些是论文/补充材料结论；

#### 早期潜空间贝叶斯优化

LOL-BO（NeurIPS 2022）会在生成模型潜空间中做局部 BO，并联合更新表示；ROBOT（AISTATS 2023）会同时寻找多个不同解。ApexGO 将两者的思想带到肽模板优化，并加入显式的序列相似性约束和 APEX MIC 预言机。

### 3. 核心思想

可以把 ApexGO 理解为：

> 用 VAE 学习“肽序列坐标系”，用 APEX 提供活性方向，用受约束的多信赖域 BO 在模板附近反复试探，并让坐标系随已观察到的 MIC 信号重新组织。

三个核心组件分别承担不同职责：

| 组件 | 输入 | 输出 | 作用 |
|---|---|---|---|
| Transformer VAE | 肽序列 $x$ 或潜变量 $z$ | 潜变量 $z$ 或解码序列 $x$ | 把离散序列搜索转成连续优化 |
| APEX 1.1 | 肽序列 | 11 个病原菌的预测 MIC | 充当 BO 的黑箱预言机 |
| 受约束多信赖域 BO | 已观察的 $(z,y,C)$ | 下一批潜变量候选 | 在可行模板邻域中平衡探索与利用 |

### 4. 输入、输出与关键变量

#### 输入

- 模板序列 $x_0$；
- 预训练的 6 层 Transformer 编码器/解码器 VAE；
- APEX 的 8 模型集成；
- 优化目标：7 个革兰阴性菌的平均 MIC，或全部 11 个菌株的平均 MIC；
- 相似性阈值 0.75；
- 目标解集大小 $M=20$。

#### 输出

一次优化运行最终返回 20 个信赖域中心，对应 20 条互不重复的高分可行肽。论文对 10 个模板分别运行革兰阴性和广谱目标，最终每个模板合成 10 条、共 100 条肽进行实验。如何从每次运行的 20 个中心确定最终 100 条序列，在论文正文和已搜索代码中均 **Not found**。

#### 变量

| 符号 | 含义 | 代码对应 |
|---|---|---|
| $x$ | 离散氨基酸序列 | `train_x`, `valid_xs` |
| $z\in\mathbb R^{256}$ | 两个 128 维 token 拼接后的潜变量 | `train_z` |
| $y$ | 为适配最大化框架而取负的预测 MIC | `train_y` |
| $C(x)$ | 模板相似性约束 | `train_c` |
| $D_t$ | 截至第 $t$ 步收集的序列、潜变量、分数和约束 | `train_x/y/z/c` |
| $M$ | 信赖域数量与最终解集大小 | `M=20` |
| $\tau$ | 解之间的最低多样性 | 演示脚本中为 1 个编辑 |

### 5. 两个关键损失

#### VAE 损失

论文写成最大化形式：

$$
\mathcal L_{\mathrm{VAE}}
=\mathbb E_{\mathcal E(Z\mid X)}[\log \mathcal D(X\mid Z)]
-\beta\,\mathrm{KL}(\mathcal E(Z\mid X)\Vert p(Z)),
$$

其中 $p(Z)=\mathcal N(0,I)$，$\beta=10^{-4}$（`paper.md:223-232`）。代码采用等价的最小化形式：token 交叉熵重构损失加 `kl_factor * kldiv`（`ApexGO/generation/vae.py:381-455`）。

编码器输出每个位置的 $\mu$ 和正的 $\sigma$，再采样

$$
z=\mu+\epsilon\sigma,\qquad \epsilon\sim\mathcal N(0,I).
$$

两个瓶颈 token、每个 128 维，因此 BO 看到的是 256 维向量。

#### 联合 VAE/代理模型损失

论文希望表示空间能按 MIC 重新排列：

$$
\mathcal L_{\mathrm{joint}}
=\mathbb E_{\mathcal E(Z\mid X)}
 [\mathcal L_{\mathrm{PPGPR}}(y,Z)]
+\mathcal L_{\mathrm{VAE}}(X).
$$

代码实际最小化 VAE 损失、目标 GP 的负边际似然以及各约束 GP 的负边际似然之和（`ApexGO/optimization/constrained_bo/gp_utils/update_models.py:46-130`）。这验证了联合学习信号，但触发方式与论文有差异：论文称每 10 步更新一次；代码在连续 10 次采集没有进步时才触发（`ApexGO/optimization/constrained_bo_scripts/optimize.py:242-269`）。

### 6. 从输入到输出的完整流程

```text
UniRef 中 450 万条短序列
        |
        v
预训练 Transformer VAE：序列 <-> 256 维潜空间
        |
        +-- 论文：为每个模板生成 20,000 条 >=75% 相似的随机衍生肽
        |          并单独微调 VAE（公开快照中 Not found）
        v
模板 x0 + 10,000 条随机突变初始化序列
        |
        v
编码 z + APEX 预测 MIC + 精确编辑相似性
        |
        v
拟合目标 PPGPR 和相似性约束 GP
        |
        v
20 个自适应信赖域并行提出潜变量候选
        |
        v
Thompson sampling -> 预测可行性过滤 -> VAE 解码
        |
        v
精确相似性/去重过滤 -> APEX 查询 -> 加入 D_t
        |
        +-- 常规重拟合代理模型
        +-- 停滞时联合更新 VAE/GP 并重编码数据
        +-- 扩缩、重启并重新居中各信赖域
        |
        v
20 个最终中心 -> 候选筛选 -> 合成与湿实验
```

#### 第 1 步：预训练肽 VAE

论文报告使用 450 万条长度小于 50 的 UniRef 裁剪序列，训练 118 个 epoch，并达到 99.94% 测试重构准确率（`paper.md:223-244`）。

**代码已验证：**

- `generation/data.py:30-140`：1-mer 词表、`<start>`/`<stop>`、批内补齐和 90/5/5 切分；
- `generation/vae.py:125-330`：6 层 Transformer、两个潜 token、自回归 Gumbel-softmax 解码；
- `generation/train.sh:1-12`：$d=128$、$\beta=10^{-4}$、前馈宽度 256、dropout 0.05；
- `generation/train_vae.py:77-155`：Adam、学习率 $2\times10^{-4}$、batch 512、bfloat16 和最佳验证损失保存。

**缺失证据：** 450 万条训练 CSV 需要外部下载；训练脚本本身没有把停止点固定为 118 epoch；99.94% 是论文报告值，本次未重训验证。

#### 第 2 步：让 VAE 靠近模板邻域

全局 VAE 大部分概率质量不在某个具体模板附近。论文因此为每个模板生成 20,000 条满足 75% 相似度的随机突变序列，再用相同超参数微调 VAE（`paper.md:274-277`）。

**论文主张 / 代码未验证：** 已搜索的公开快照中没有找到所称的模板突变生成和逐模板微调脚本。初始化 CSV 和穷举辅助脚本不能替代该流程，因此此步骤保留为 **Not found**，不能根据论文描述补写成已实现事实。

#### 第 3 步：建立初始观测

论文使用 10,000 条模板随机突变序列初始化 BO（`paper.md:289`）。代码仓库包含 `init_seqs.csv`、全 11 菌株均值分数和革兰阴性目标分数表；运行类读取指定数量的序列/分数，再用 VAE 计算潜变量（`optimization/constrained_bo_scripts/apex_oracle_constrained_diverse_optimization.py:75-128`）。

#### 第 4 步：APEX 预言机打分

`APEX_predict.py:14-75` 直接验证了以下行为：

1. 加载 8 个序列模型；
2. 对每条肽预测 11 个菌株的输出；
3. 把网络尺度还原成微摩尔 MIC；
4. 对 8 个模型取平均。

通用优化框架只做最大化，因此 `ApexObjective` 返回负 MIC。`mean` 是 11 菌株均值，`gramneg_mean` 是前 7 个革兰阴性菌均值（`your_tasks/your_objective_functions.py:74-150`）。

#### 第 5 步：拟合目标与约束代理模型

论文用 1,024 个诱导点的参数化 GP 拟合 $z\mapsto y$，并用第二个 GP 拟合相似性约束（`paper.md:247,271`）。约束的真实值为

$$
s(x,x_0)=\frac{|x_0|-d_{\mathrm{Lev}}(x,x_0)}{|x_0|},
$$

要求 $s(x,x_0)\geq0.75$。代码在 `your_blackbox_constraints.py:120-166` 中逐字实现了该定义。

#### 第 6 步：在 20 个信赖域内采集

每个信赖域围绕当前一个最优、可行且不同的序列中心。代码默认宽度为 0.8；连续 10 次成功后宽度翻倍，连续 32 次失败后减半，小于 $0.5^7$ 时重启（`constrained_bo/trust_region.py:14-65`）。

候选生成依次执行：

1. 在局部超矩形中用 Thompson sampling 采样潜变量；
2. 用约束 GP 去掉预测不可行候选；
3. 用 VAE 解码成字符串；
4. 计算真实编辑相似度；
5. 按编辑距离去掉前面信赖域已选的重复解；
6. 调用 APEX，并把新观测写回共享历史。

对应直接代码证据为 `constrained_bo/robot.py:328-389,424-466`。

#### 第 7 步：联合更新与重居中

正常循环只重拟合代理模型；停滞达到阈值时，`LolRobotState.update_models_e2e` 用近期样本和 top-$k$ 样本联合训练 VAE、目标 GP 和约束 GP，然后重新编码数据，使旧序列在新潜空间中获得新坐标（`constrained_bo/lol_robot.py:244-327`）。

这是 ApexGO 的关键：代理模型不仅在固定坐标里学习，坐标系本身也被活性信号塑形。

### 7. 实验结果如何解读？

#### 论文报告的主要数字

- 10 个模板、100 条合成优化肽、11 个临床相关菌株；
- 86/100 至少对一个菌株有可检测活性（MIC 不高于 64 μmol l$^{-1}$）；
- 68% 的候选平均 MIC 优于对应模板；
- 只看革兰阴性菌时，改善率为 72%；
- 实验 MIC 与 APEX 预测的 Pearson/Spearman 相关系数分别为 0.463/0.462（`paper.md:91-108`）。

这说明预言机有用但并不完美；ApexGO 的闭环优化收益不能等同于精确预测实验 MIC。

#### 基线

- 对可完全穷举的 mammuthusin-3 和 arctoterin-1，论文报告 ApexGO 找回全部 top-20 APEX 最优衍生肽；
- 论文报告 ApexGO 在 10 个模板上优于固定 VAE 的 LOL-BO 和标准潜空间 BO；
- 与 HydrAMP 相比，ApexGO 在陌生模板邻域更稳定；
- PepDiffusion 在该 75% 模板约束下没有产生可比较候选。

#### 湿实验与动物实验

图 2 显示若干最优衍生肽相对模板有 2 倍至至少 32 倍 MIC 改善。图 3 显示不同序列可采用不同二级结构和膜作用模式，多数展示候选在 HEK293T 上低毒。图 4 中，mylodonin-2-3 和 mammuthusin-3-6 在两个小鼠感染模型中降低细菌负荷。

必须保留两个限制：图 4 每组只有 $n=4$；不同肽和抗生素按各自 MIC 给药，并非等摩尔或等质量剂量。因此与多黏菌素 B、左氧氟沙星的比较是情境基准，不是临床等效性证明。

### 8. 代码与论文的一致性

**总体：medium。**

**Exact：** VAE 架构与基础损失、token 化和解码、APEX 8 模型/11 菌株集成、负 MIC 目标、75% 编辑相似性、多信赖域采集和信赖域扩缩规则。

**Partial：** 预训练协议、联合 VAE/GP 更新时机、公开演示配置。演示脚本把最大长度设为 30，而论文为 50；演示使用 `gramnegonly_mean`，它还惩罚预测为革兰阳性活跃的序列，并不等于论文所述的纯 7 菌株平均目标。

**Not found：** 每模板 20,000 条衍生肽的微调流程、全部 10 个模板的完整命令/随机种子/历史、从运行输出确定最终 100 条实验肽的确定性记录。

**运行未验证：** 本次没有启动 Docker/CUDA 推理，没有验证序列化模型兼容性和端到端导入路径。模型文件存在不等于运行成功。

### 9. 研究者应记住的三点

1. **ApexGO 优化的是 APEX，不是直接优化实验。** 实验验证是独立的第二阶段。
2. **VAE 是可调整的搜索坐标系。** 联合损失的意义不是单纯提高重构，而是让相近 MIC 的肽在潜空间中更容易被 GP 建模。
3. **约束定义很窄。** 75% 编辑相似性只保证字符串接近，不保证结构、机制、毒性、稳定性或药代性质接近；这些仍需多目标建模和实验验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

Antimicrobial-peptide discovery has many candidate sequences, but lead optimization requires improving a known scaffold while preserving similarity, manufacturability and a useful activity profile. Fixed-library screening and one-shot generative models do not directly solve this constrained derivative-design problem (`paper.md:25-37`).

### Proposed Method

ApexGO combines a transformer VAE, an APEX MIC predictor and constrained Bayesian optimization. The VAE embeds sequences in a 256-dimensional continuous space; BO proposes latent edits; the decoder turns each proposal back into a peptide; APEX supplies predicted MIC feedback; and a second GP rejects candidates below 75% edit similarity to the template. Twenty trust regions maintain a diverse set of high-scoring derivatives, while periodic VAE/GP updates adapt the latent coordinates (`paper.md:49-73,199-290`).

The intended search objective is low average predicted MIC against either seven Gram-negative pathogens or all 11 targets. Code implements minimization by maximizing negative MIC. The public demo is close but not identical to Methods: it sets a length cap of 30 rather than the paper's 50 and selects a `gramnegonly_mean` objective that additionally penalizes active Gram-positive predictions (`ApexGO/optimization/constrained_bo_scripts/optimize_gramnegative_only.sh:1-17`; `ApexGO/optimization/your_tasks/your_objective_functions.py:111-135`).

### Computational Pipeline

1. Train a six-layer transformer VAE on 4.5 million UniRef sequences shorter than 50 residues. The paper reports 118 epochs and 99.94% test reconstruction accuracy. Code exposes the same architecture, 1-mer vocabulary, $\beta=10^{-4}$, Adam learning rate $2\times10^{-4}$, batch size 512 and best-validation checkpointing (`paper.md:223-244`; `ApexGO/generation/vae.py:125-455`; `ApexGO/generation/train_vae.py:77-155`).
2. For each template, generate 20,000 random derivatives at >=75% similarity and fine-tune the VAE according to the paper. The public snapshot's claimed mutation/fine-tuning scripts were **Not found**.
3. Initialize BO with 10,000 template mutations and APEX scores. APEX averages eight neural predictors over 11 pathogen MIC outputs (`paper.md:289`; `ApexGO/optimization/apex_oracle/APEX_predict.py:14-75`).
4. Fit a 1,024-inducing-point parametric GP for the objective and a constraint GP for edit similarity. Thompson sampling proposes latent candidates inside 20 adaptive trust regions.
5. Decode, apply exact similarity and diversity filters, query APEX, append observations, refit, resize/restart regions and recenter them on the best 20 distinct feasible points.
6. When progress stalls, the code jointly updates the VAE and surrogate and re-encodes observations. The paper describes updates every ten steps; code triggers them after ten consecutive failures (`paper.md:250-256,289`; `ApexGO/optimization/constrained_bo_scripts/optimize.py:242-269`).
7. Return final region centres for synthesis and experimental validation.

### Evaluation

The study optimized ten extinct-organism peptide templates, produced 100 optimized candidates and tested them against 11 clinically relevant bacterial strains. Of 100 synthesized peptides, 86 had detectable activity (MIC <=64 micromolar); 68% improved over their templates, and the Gram-negative improvement rate was 72%. Pearson and Spearman correlations between experimental MIC and APEX predictions were 0.463 and 0.462 (`paper.md:91-108`). These are paper-reported results; the supplementary CSV is linked but not present in this workspace.

For representative best derivatives, Figure 2 shows 2- to >32-fold MIC gains against Gram-negative strains. Figure 3 shows broad secondary-structure states, heterogeneous membrane permeabilization/depolarization and mostly low HEK293T cytotoxicity. Figure 4 reports lower bacterial burdens for mylodonin-2-3 in a skin-abscess model and mammuthusin-3-6 in a neutropenic thigh model, with $n=4$ per group and dosing at each compound's respective MIC (`figure_analysis.md`; `paper.md:164-184`).

The paper also reports two computational checks that are not locally visualized: ApexGO recovered all top-20 APEX-ranked derivatives for the enumerable mammuthusin-3 and arctoterin-1 spaces, and outperformed LOL-BO and standard latent BO across ten templates (`paper.md:292-301`). Against HydrAMP, 84.9% of ApexGO designs improved predicted MIC across all seven Gram-negative organisms versus 50.3%, 55.7% and 32.9% for HydrAMP at temperatures 3, 5 and 10; PepDiffusion produced no >=75%-similar candidates (`paper.md:304-316`). These comparisons rely on unavailable supplementary figures and should remain paper claims.

### Reproducibility

**Rating: 3/5 (substantial core assets, incomplete exact reproduction).** The GitHub snapshot is pinned to commit `10a355a4220e6f8f432d62b267317b5b8b337dc8`, includes VAE and APEX checkpoints, a Docker image specification, package versions and a one-template optimization shell command. Direct source reads verify the central VAE, oracle, constraints, GP update, trust-region and logging logic (`doc_code.md`).

Important gaps remain:

- The per-template 20,000-derivative generator/fine-tuning workflow described in Methods is not present in the searched source snapshot.
- The complete ten-template run matrix, random seeds, final 100-peptide selection and experimental table are not bundled as deterministic artifacts.
- The demo configuration differs from the paper's objective and sequence-length cap.
- Imports, CUDA/Docker execution and checkpoint compatibility were not run here.
- Supplementary methods, figures and data were linked by the paper but not acquired locally.
- Biological mechanism, toxicity and animal efficacy are downstream experimental claims, not executable code behavior.

### Bottom Line

ApexGO's central contribution is a practical closed loop: learn a smooth peptide coordinate system, search it with constrained BO, and use an activity oracle to steer local edits around existing scaffolds. The public code supports that core design and exposes the important loss, constraint and trust-region mechanics, but a reader should treat exact paper reproduction and broad biological conclusions as conditional on the missing fine-tuning/experiment artifacts and runtime environment.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
