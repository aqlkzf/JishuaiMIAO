---
layout: default
permalink: /paper-atlas/simplemaskeddiffusionlanguagemodels-1f2f7727/
title: "SimpleMaskedDiffusionLanguageModels"
nav: false
description: "MDLM 把序列中的 token 随机变成 [mask]，训练一个双向 encoder-only denoiser 从带 mask 的序列恢复原 token；通过 SUBS 参数化，训练目标可以化简为一个带时间权重的 MLM loss，并且这个 loss 是一个有原则的扩散变分下界。 这意味着：它看起来像 BERT 的随机 mask 训练，但不是普通的启发式 MLM，而是来自扩散模型 NELBO 的训练目标。"
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
      <span>arXiv · 2024</span>
    </div>
    <h1>SimpleMaskedDiffusionLanguageModels</h1>
    <p>Simple and Effective Masked Diffusion Language Models</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/kuleshov-group/mdlm" target="_blank" rel="noopener noreferrer" aria-label="Open code for SimpleMaskedDiffusionLanguageModels">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Simple and Effective Masked Diffusion Language Models（MDLM）方法中文讲解

### 1. 这篇论文想解决什么问题？

论文研究的是：**怎样把扩散模型更有效地用于离散序列生成，尤其是文本和 DNA 序列**。扩散模型在图像生成中很成功，也有潜力用于文本，因为它不必像自回归（autoregressive, AR）语言模型那样严格从左到右生成；但过去的离散扩散语言模型在对数似然/困惑度上明显落后于 AR 模型（`paper.md:17-28`）。

作者的核心观点是：如果只关注最常用、最简单的“吸收态 mask 扩散”（absorbing-state masked diffusion），并把反向去噪模型设计得更贴合这个过程，就可以得到一个非常简单的、类似 BERT masked language modeling（MLM）的训练目标，同时显著提升扩散语言模型的困惑度（`paper.md:29-37`, `paper.md:111-123`）。

### 2. 一句话概括 MDLM

**MDLM 把序列中的 token 随机变成 `[mask]`，训练一个双向 encoder-only denoiser 从带 mask 的序列恢复原 token；通过 SUBS 参数化，训练目标可以化简为一个带时间权重的 MLM loss，并且这个 loss 是一个有原则的扩散变分下界。**

这意味着：它看起来像 BERT 的随机 mask 训练，但不是普通的启发式 MLM，而是来自扩散模型 NELBO 的训练目标（`paper.md:198-213`）。

### 3. 为什么已有方法不够？

论文主要指出三类不足：

1. **早期离散扩散语言模型困惑度较差**：D3PM、DiffusionBert、SEDD 等方法与 AR 模型仍有差距（`paper.md:17-28`, `paper.md:259-291`）。
2. **通用离散扩散框架较复杂**：D3PM 支持一般转移矩阵 `$Q_t$`，但这会带来复杂的 posterior / KL 计算；连续时间推广还常常需要 CTMC 理论（`paper.md:78-88`, `paper.md:421-431`）。
3. **BERT 本身不是原则化生成模型**：传统 BERT/MLM 可以做表示学习，但从 BERT 生成文本通常依赖 Gibbs sampling 或其他 ad-hoc 方法；MDLM 给 encoder-only 模型一个扩散生成解释和采样过程（`paper.md:434-438`）。

### 4. 基本符号

| 符号 | 含义 | 来源 |
|---|---|---|
| `${\mathbf{x}}` | 干净 token 的 one-hot 表示 | `paper.md:90-99` |
| `${\mathbf{m}}` | `[mask]` token 的 one-hot 表示 | `paper.md:90-99` |
| `${\mathbf{z}}_t` | 时间 `t` 时被污染后的 token | `paper.md:102-110` |
| `$\alpha_t$` | 单调递减的噪声日程；`t=0` 基本干净，`t=1` 基本全 mask | `paper.md:102-110` |
| `$\mathbf{x}_\theta({\mathbf{z}}_t,t)$` | 神经网络 denoiser，对干净 token 分布的预测 | `paper.md:130-132` |
| `${\mathbf{x}}^{1:L}` | 长度为 `L` 的 token 序列 | `paper.md:198-201` |

### 5. 前向过程：把 token 逐渐变成 `[mask]`

MDLM 的前向扩散是吸收态 mask 过程。对单个 token，边缘分布是：

$$
q({\mathbf{z}}_{t}\|{\mathbf{x}})=\text{Cat}({\mathbf{z}}_{t};\alpha_{t}{\mathbf{x}}+(1-\alpha_{t}){\mathbf{m}}).
$$

含义很直观：时间 `t` 越大，token 越可能变成 `[mask]`。一旦变成 `[mask]`，后续时间都会保持 `[mask]`，所以 `[mask]` 是吸收态（`paper.md:111-121`）。

这个过程的反向 posterior 是 Eq. 9：

$$
q({\mathbf{z}}_{s}\|{\mathbf{z}}_{t},{\mathbf{x}})=
\begin{cases}
\text{Cat}({\mathbf{z}}_{s};{\mathbf{z}}_{t})&{\mathbf{z}}_{t}\neq{\mathbf{m}},\\
\text{Cat}\left({\mathbf{z}}_{s};\frac{(1-\alpha_{s}){\mathbf{m}}+(\alpha_{s}-\alpha_{t}){\mathbf{x}}}{1-\alpha_{t}}\right)&{\mathbf{z}}_{t}={\mathbf{m}}.
\end{cases}
$$

解释如下：

- 如果当前 token 不是 `[mask]`，反向一步就直接复制它；
- 如果当前 token 是 `[mask]`，反向一步要么继续 mask，要么恢复成干净 token（`paper.md:113-123`）。

### 6. 反向过程：用 denoiser 近似未知的干净 token

反向生成时不知道真实 `${\mathbf{x}}`，所以论文用神经网络 `$\mathbf{x}_\theta({\mathbf{z}}_t,t)$` 预测干净 token 分布。Eq. 10 把真实 posterior 中的 `${\mathbf{x}}` 替换为模型预测（`paper.md:134-140`）：

$$
{p_{\theta}}({\mathbf{z}}_{s}\|{\mathbf{z}}_{t})=
\begin{cases}
\text{Cat}({\mathbf{z}}_{s};{\mathbf{z}}_{t}),&{\mathbf{z}}_{t}\neq{\mathbf{m}},\\
\text{Cat}\left({\mathbf{z}}_{s};\frac{(1-\alpha_{s}){\mathbf{m}}+(\alpha_{s}-\alpha_{t})\mathbf{x}_{\theta}({\mathbf{z}}_{t},t)}{1-\alpha_{t}}\right).&{\mathbf{z}}_{t}={\mathbf{m}}.
\end{cases}
$$

### 7. SUBS 参数化：两个关键“硬替换”

SUBS 是这篇论文最重要的设计之一。它把吸收态过程本来就应该满足的性质硬编码到 denoiser 输出中（`paper.md:144-160`）：

1. **Zero Masking Probabilities**：干净 token 不应该是 `[mask]`，所以把 `[mask]` 对应的 logit 设为 `$-\infty$`，强制模型对 `[mask]` 的干净预测概率为 0。
2. **Carry-Over Unmasking**：如果某个位置已经不是 `[mask]`，就直接复制该 token，而不是让网络重新预测它。

直觉上，SUBS 告诉模型：“你只需要预测被 mask 的位置；已经可见的位置不用学，也不要预测 mask 作为答案。”

### 8. 训练目标为什么会变简单？

标准扩散训练目标是 NELBO，包含重构项、扩散 KL 项和先验项（`paper.md:55-70`）。在 SUBS 约束下，扩散损失可化简为 Eq. 11：

$$
{\mathcal{L}_{\text{diffusion}}}
=\sum_{i=1}^{T}\mathbb{E}_{q}\left[
\frac{\alpha_{t(i)}-\alpha_{s(i)}}{1-\alpha_{t(i)}}
\log\langle\mathbf{x}_{\theta}({\mathbf{z}}_{t(i)}),{\mathbf{x}}\rangle
\right].
$$

这里的 `$\log\langle\mathbf{x}_{\theta}({\mathbf{z}}_t),{\mathbf{x}}\rangle$` 就是“模型给真实 token 的 log probability”。所以它本质上是交叉熵/MLM loss，只是前面有一个由扩散时间决定的权重（`paper.md:162-180`）。

连续时间极限给出 Eq. 13：

$$
{\mathcal{L}^{\infty}_{\text{NELBO}}}=\mathbb{E}_{q}\int_{t=0}^{t=1}\frac{\alpha^{\prime}_{t}}{1-\alpha_{t}}\log\langle\mathbf{x}_{\theta}({\mathbf{z}}_{t},t),{\mathbf{x}}\rangle{\text{d}}t.
$$

对序列来说，就是对所有位置求和，得到 Eq. 14（`paper.md:198-213`）：

$$
{\mathcal{L}^{\infty}_{\text{NELBO}}}=\mathbb{E}_{q}\int_{t=0}^{t=1}\frac{\alpha^{\prime}_{t}}{1-\alpha_{t}}\sum_{\ell}\log\langle\mathbf{x}_{\theta}^{\ell}({\mathbf{z}}_{t}^{1:L},t),{\mathbf{x}}^{\ell}\rangle{\text{d}}t.
$$

这就是论文说的“weighted average of MLM losses”。未 mask 的 token 因为 carry-over，log 概率项变为 0，不会贡献 loss（`paper.md:209-213`）。

### 9. 训练流程

论文中的训练流程可以理解为：

```text
干净序列 x^{1:L}
    ↓ 采样时间 t
按 α_t 随机把部分 token 变成 [mask]
    ↓
带 mask 的序列 z_t^{1:L}
    ↓ encoder-only denoiser
预测每个位置的干净 token 分布 x_θ^ℓ(z_t^{1:L}, t)
    ↓ SUBS
[mask] 不能作为干净 token；未 mask token 直接复制
    ↓
计算带时间权重的 MLM / NELBO loss
```

论文还提到一些工程要点：tokenizer 很关键；只在 masked token index 上稳定计算 KL；语言模型使用 DiT/Transformer 架构、rotary embedding 和低差异（low-discrepancy）时间采样来降低 ELBO 方差（`paper.md:214-222`, `paper.md:1341-1362`）。

### 10. 采样与生成

#### 10.1 固定长度 ancestral sampling

生成长度 `L` 的序列时，MDLM 从全 `[mask]` 序列开始，然后按反向扩散逐步 unmask。每一步根据 Eq. 10 独立采样每个位置的前一时刻 token（`paper.md:226-230`）。

如果 denoiser 不依赖时间，并且某一步没有 token 新变成 unmasked，那么可以复用之前算过的 `$\mathbf{x}_\theta({\mathbf{z}}_t)$`，跳过一次神经网络调用。这就是论文讨论的 caching 加速（`paper.md:231-234`）。

#### 10.2 半自回归任意长度生成

MDLM 还提出 semi-autoregressive（SAR）生成：先生成 `L` 个 token，再把最后 `L-L'` 个 token 当作下一轮生成的前缀，另外生成 `L'` 个新 token。由于 carry-over，前缀会被复制保留，于是可以反复扩展，生成任意长度文本（`paper.md:235-240`）。

### 11. 实验结果怎么理解？

- **LM1B / OWT 困惑度**：MDLM 超过已有扩散模型，并接近但没有全面超过 AR 模型。LM1B 上 327B tokens 的 MDLM 为 `≤23.00` PPL，AR baseline 为 20.86；OWT 上 MDLM 为 `≤23.21`，AR 为 17.54（`paper.md:259-291`）。
- **零样本泛化**：OWT 训练后的 MDLM 在表 3 中比 SEDD 更好，并在 Lambada、Pubmed、Arxiv 上优于 AR；但扩散模型数值是 perplexity upper bound，需要保留这个限定（`paper.md:294-307`）。
- **表示学习**：BERT 经过 MDLM fine-tuning 后可以有生成能力，同时 GLUE 平均分 82.06，略高于 BERT 的 81.62（`paper.md:309-322`）。
- **SAR 生成**：2048-token 生成中，MDLM 比 SSD-LM 有更低 generative PPL 和更快速度（`paper.md:324-337`）。
- **DNA 序列**：在 Caduceus DNA 模型上，MDLM 是表 6 中最好的扩散 fine-tuning 目标，并在 Genomics Benchmarks 上保持或提升若干下游分类结果（`paper.md:338-401`）。
- **消融**：连续时间、carry-over 和工程优化都重要；去掉 carry-over 会明显损害 LM1B PPL（`paper.md:402-417`）。

### 12. 图如何支持论文结论？

- **Figure 1**（`graphical_abstract_updated_3.png`）：直观展示 MDLM 的 mask/unmask 训练、简化目标、variational lower bound、ancestral sampling，以及 LM1B PPL 靠近 AR 参考线。
- **Figure 2**（`x1.png`）：显示 OWT 采样时，带 caching 的 MDLM 在时间-困惑度权衡上优于或接近其他扩散曲线。
- **Figure 3**（`x2.png`）：显示 MDLM 的训练 NLL 曲线比 SEDD 更平滑、方差更小，但 AR 曲线仍更低。

### 13. 需要保留的不确定性

- **代码不可用**：论文摘要给出 GitHub 地址 `https://github.com/kuleshov-group/mdlm`（`paper.md:8-14`），但本地 acquisition 因 GitHub 连接失败，没有获得 `code source`；日志见 `logs/code_acquisition_error.log:1-4`。
- 因此，本文档中的 SUBS、low-discrepancy sampler、caching、SAR decoding 等都是**论文描述的算法行为**，不是本地代码验证结果。
- **可执行复现实验命令 Not found**：论文提供许多超参数和算力信息（`paper.md:1341-1421`, `paper.md:1933-1936`），但本 workspace 没有可运行源码或脚本。

### 14. 总结

MDLM 的关键贡献是把 masked discrete diffusion 变成一个简单、稳定、类似 MLM 的训练目标，同时保留扩散模型的生成解释。它的价值不在于完全击败 AR 语言模型，而在于证明：只要把吸收态 mask 过程、SUBS 参数化和现代训练工程结合起来，离散扩散语言模型可以成为很强的文本与生物序列生成/表示学习基线。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Simple and Effective Masked Diffusion Language Models — Summary

### What problem does the paper address?

Diffusion models can generate discrete data such as text and biological sequences, but prior discrete diffusion language models were reported to lag autoregressive (AR) language models in log-likelihood/perplexity (`paper.md:17-28`). The paper asks whether a simpler, better-engineered masked diffusion setup can close much of this gap while preserving non-left-to-right generation and BERT-style bidirectional representations.

### Proposed method

The paper introduces **Masked Diffusion Language Models (MDLM)**: an absorbing-state discrete diffusion model where clean tokens are gradually replaced by a `[mask]` token and a neural denoiser learns to reverse the masking process (`paper.md:111-123`). Its main modeling choice is the **SUBS parameterization**, which hard-codes two constraints into the denoiser output (`paper.md:134-160`):

1. the clean token prediction never assigns probability to `[mask]`; and
2. already-unmasked tokens are copied forward unchanged.

These constraints make the likelihood objective simplify to a Rao-Blackwellized weighted masked language-modeling loss. In continuous time, the core objective is Eq. 14, a weighted sum over token-level log-probabilities across diffusion times (`paper.md:191-213`). This connects generative diffusion models with encoder-only masked language models, giving BERT-style models a principled generation objective and sampling procedure.

### High-level computational pipeline

1. Tokenize text or DNA sequences.
2. Sample a diffusion time `t` and mask tokens according to an absorbing-state schedule.
3. Feed the partially masked sequence to an encoder-only denoiser.
4. Apply SUBS substitutions: zero out `[mask]` clean-token probability and copy unmasked tokens.
5. Optimize the weighted MLM-like NELBO (Eq. 13/Eq. 14; appendix Eq. 50).
6. Generate by starting from all masks and ancestral unmasking; optionally use caching and semi-autoregressive continuation for arbitrary-length text (`paper.md:226-240`).

### Main results claimed in the paper

- **Language modeling**: On LM1B, MDLM improves over prior diffusion baselines and reports `≤23.00` PPL after 327B expected tokens, approaching but not beating the retrained AR Transformer at 20.86 (`paper.md:259-279`). On OpenWebText, MDLM reports `≤23.21` PPL versus retrained SEDD `≤24.10` and AR `17.54` (`paper.md:282-291`).
- **Zero-shot likelihood**: OWT-trained MDLM outperforms SEDD across the listed out-of-domain datasets and is better than AR on Lambada, Pubmed, and Arxiv in Table 3; diffusion values are explicitly upper bounds (`paper.md:294-307`).
- **Representation learning**: MDLM fine-tuning turns BERT-style models into generative models while preserving GLUE performance; the reported average is 82.06 for BERT+MDLM-FT versus 81.62 for BERT (`paper.md:309-322`).
- **Semi-autoregressive sampling**: For 2048-token sequences, MDLM reports better generative PPL and much lower seconds per sequence than SSD-LM (`paper.md:324-337`).
- **DNA modeling**: The method is also applied to Caduceus/Mamba DNA models; MDLM is the best diffusion generative fine-tuning objective in Table 6 and preserves/improves several downstream genomic classification metrics in Table 7 (`paper.md:338-401`).
- **Ablations**: Continuous time, carry-over, and engineering improvements contribute to likelihood; removing carry-over worsens LM1B PPL substantially in Table 8, whereas zero-masking removal has little additional effect in that ablation (`paper.md:402-417`).

### Figures at a glance

- **Figure 1** (`graphical_abstract_updated_3.png`) visually summarizes masked denoising losses, the weighted-MLM objective, variational lower-bound framing, ancestral sampling, and LM1B PPL approaching an AR reference.
- **Figure 2** (`x1.png`) shows MDLM sampling tradeoffs on OWT: caching generally reaches lower wall-clock time for a given generative perplexity than non-cached MDLM/SEDD over the plotted range.
- **Figure 3** (`x2.png`) shows training NLL on OWT: MDLM is visibly smoother/lower-variance than SEDD but AR remains lower-NLL.

### Reproducibility and code status

The paper advertises code at `https://github.com/kuleshov-group/mdlm` (`paper.md:8-14`), but this workspace is **paper-only** because the local clone failed with a GitHub connectivity error (`logs/code_acquisition_error.log:1-4`). Therefore:

- No source files or commit were verified locally.
- SUBS, low-discrepancy sampling, caching, and semi-autoregressive decoding are documented as paper claims, not code-verified implementation behavior.
- The paper provides substantial hyperparameters and compute details in Appendix D and the NeurIPS checklist (`paper.md:1341-1421`, `paper.md:1933-1936`), but runnable commands/scripts are **Not found** in this local workspace.

### Bottom line

MDLM is a focused masked-discrete-diffusion method that makes the diffusion objective look like a weighted MLM loss, enabling encoder-only models to become generative while improving diffusion-model perplexity. The strongest supported claim is not that MDLM surpasses AR language models overall, but that a simple absorbing-state diffusion model with SUBS and modern training recipes can become a competitive, lower-variance diffusion baseline for text and biological sequences.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
