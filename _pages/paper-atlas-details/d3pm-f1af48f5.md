---
layout: default
permalink: /paper-atlas/d3pm-f1af48f5/
title: "D3PM"
nav: false
description: "D3PM（Discrete Denoising Diffusion Probabilistic Models）把扩散模型从连续高斯噪声空间推广到离散类别空间：它不把文本 token 或量化图像像素先嵌入连续空间，而是直接用一系列类别转移矩阵 \\boldsymbol {Q} {t} 来逐步破坏离散数据，再训练神经网络学习反向去噪过程。"
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
      <span>NeurIPS · 2021</span>
    </div>
    <h1>D3PM</h1>
    <p>Structured Denoising Diffusion Models in Discrete State-Spaces</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## D3PM 方法中文解读：离散状态空间中的结构化去噪扩散模型

### 一句话概括

D3PM（Discrete Denoising Diffusion Probabilistic Models）把扩散模型从连续高斯噪声空间推广到离散类别空间：它不把文本 token 或量化图像像素先嵌入连续空间，而是直接用一系列类别转移矩阵 $\boldsymbol {Q} _ {t}$ 来逐步破坏离散数据，再训练神经网络学习反向去噪过程。

### 它要解决什么问题？

经典 DDPM 在图像、音频等连续空间中通常使用高斯噪声：每一步向实值数据加入一点噪声，再训练模型反向去噪。可是文本 token、字符、量化像素值本质上是离散类别。已有离散扩散工作主要使用均匀 multinomial corruption，也就是随机变成任意类别；这种方式没有充分利用离散数据内部结构。

D3PM 的问题设定是：如果每个变量 $x _ {t}$ 只能取 $K$ 个类别之一，怎样设计一个既可训练、又能表达领域结构的扩散模型？论文的答案是把前向噪声过程写成类别 Markov 链，并通过不同的 $\boldsymbol {Q} _ {t}$ 设计来注入结构。

### 核心思想：用转移矩阵代替连续高斯噪声

对单个离散变量，D3PM 用 $K \times K$ 的转移矩阵表示一步前向破坏过程：

$$
q (\boldsymbol {x} _ {t} | \boldsymbol {x} _ {t - 1}) = \operatorname{Cat} (\boldsymbol {x} _ {t}; \boldsymbol {p} = \boldsymbol {x} _ {t - 1} \boldsymbol {Q} _ {t}).
$$

这里 $\boldsymbol {x}$ 是 one-hot 行向量，$\operatorname{Cat}$ 是类别分布。直观地说，如果当前类别是 $i$，那么矩阵第 $i$ 行给出下一步变成各个类别 $j$ 的概率。

累积到第 $t$ 步时：

$$
q (\boldsymbol {x} _ {t} | \boldsymbol {x} _ {0}) = \operatorname{Cat} \left(\boldsymbol {x} _ {t}; \boldsymbol {p} = \boldsymbol {x} _ {0} \overline &#123;&#123;\boldsymbol {Q}}} _ {t}\right), \quad \overline &#123;&#123;\boldsymbol {Q}}} _ {t} = \boldsymbol {Q} _ {1} \boldsymbol {Q} _ {2} \dots \boldsymbol {Q} _ {t}.
$$

训练需要的后验也有闭式形式：

$$
q \left(\boldsymbol {x} _ {t - 1} \mid \boldsymbol {x} _ {t}, \boldsymbol {x} _ {0}\right) = \operatorname{Cat} \left(\boldsymbol {x} _ {t - 1}; \boldsymbol {p} = \frac {\boldsymbol {x} _ {t} \boldsymbol {Q} _ {t} ^ {\top} \odot \boldsymbol {x} _ {0} \overline &#123;&#123;{\boldsymbol {Q}}}} _ {t - 1}}{\boldsymbol {x} _ {0} \overline &#123;&#123;{\boldsymbol {Q}}}} _ {t} \boldsymbol {x} _ {t} ^ {\top}}\right).
$$

这个公式很关键：它让 D3PM 能像连续 DDPM 一样计算变分目标中的 KL 项，而不需要枚举整个高维样本空间；因为论文假设每个位置的前向转移按位置独立分解。

### 前向噪声可以怎样设计？

D3PM 的方法贡献主要体现在 $\boldsymbol {Q} _ {t}$ 的选择。

| 类型 | 直觉 | 适用场景 |
|---|---|---|
| 均匀转移（uniform） | 每个类别有概率变成任意类别，是已有 multinomial diffusion 的基线 | 通用离散基线 |
| 吸收态（absorbing / mask） | 非 mask 类别要么保持不变，要么变成 `[MASK]`；一旦成为 mask 就不再离开 | 文本生成；与 BERT/MLM 有联系 |
| 离散高斯（discretized Gaussian） | 更倾向变到数值相近的类别，而不是任意类别 | 量化图像像素等有序离散值 |
| token embedding 最近邻 | 在词/字符 embedding 图上向近邻扩散 | 尝试给文本 token 加入语义或字符相似性结构 |
| 带状矩阵 | 只允许局部邻近类别转移 | 论文提到但未用于实验 |

Figure 1 很好地展示了这些差异：uniform 会把点散得很开；Gaussian 保留更多局部几何；absorbing 会把大量状态吸收到某些 mask-like 状态。这个图说明，前向破坏过程不是无关紧要的技术细节，而是在定义模型的归纳偏置。

### 反向过程：先预测干净样本，再构造一步去噪分布

D3PM 不直接让神经网络输出 $p _ {\theta}(\boldsymbol {x} _ {t-1}|\boldsymbol {x} _ {t})$ 的 logits，而是让网络预测原始干净值的分布：

$$
\widetilde {p} _ {\theta} (\widetilde {\boldsymbol {x}} _ {0} | \boldsymbol {x} _ {t}).
$$

然后用已知的前向模型把它转换成一步反向分布：

$$
p _ {\theta} (\boldsymbol {x} _ {t - 1} | \boldsymbol {x} _ {t}) \propto \sum_ {\widetilde {\boldsymbol {x}} _ {0}} q (\boldsymbol {x} _ {t - 1}, \boldsymbol {x} _ {t} | \widetilde {\boldsymbol {x}} _ {0}) \widetilde {p} _ {\theta} (\widetilde {\boldsymbol {x}} _ {0} | \boldsymbol {x} _ {t}).
$$

这叫 $\boldsymbol {x} _ {0}$-parameterization。它的好处是：如果模型能把全部概率放在真实 $\boldsymbol {x} _ {0}$ 上，KL 项会达到最优；同时，反向转移的稀疏结构会自然继承前向矩阵 $\boldsymbol {Q} _ {t}$ 的稀疏模式。论文还指出，这种形式可以做跨步推断，即从 $t$ 直接跳到 $t-k$，从而减少采样步数。

对于图像这种有序离散值，论文还尝试用截断离散 logistic 分布来参数化 $\widetilde {p} _ {\theta}$，而不是直接输出每个类别的任意 logits。这相当于给像素值加入“邻近灰度/颜色更相似”的归纳偏置，并在 CIFAR-10 上提升了 FID 和 NLL。

### 训练目标

基础目标是扩散模型常用的变分上界 $L _ {\mathrm{vb}}$。它包含终点 KL、中间每步后验与反向模型之间的 KL，以及 $t=1$ 的重构项。D3PM 进一步提出混合目标：

$$
L _ {\lambda} = L _ {\mathrm{vb}} + \lambda \mathbb {E} _ {q (\boldsymbol {x} _ {0})} \mathbb {E} _ {q (\boldsymbol {x} _ {t} | \boldsymbol {x} _ {0})} [ - \log \widetilde {p} _ {\theta} (\boldsymbol {x} _ {0} | \boldsymbol {x} _ {t}) ].
$$

第二项是辅助去噪交叉熵：在任意时间步 $t$，都鼓励模型从带噪样本 $\boldsymbol {x} _ {t}$ 预测原始样本 $\boldsymbol {x} _ {0}$。论文报告：这个辅助目标对图像样本质量有帮助；在文本中，$L _ {\lambda=0.01}$ 对 absorbing/mask 模型效果最好，但对 uniform 模型并不总是有益。

### 噪声日程（noise schedule）

连续 DDPM 通常调节高斯方差。D3PM 中，不同转移矩阵需要不同 schedule：

- uniform：主要使用 cosine schedule。
- discretized Gaussian：使用类似连续 DDPM 的线性方差 schedule。
- absorbing 和 nearest-neighbor：使用基于互信息的 schedule。

互信息 schedule 的目标是让第 $t$ 步时关于原始数据的信息按比例减少：

$$
\frac {t}{T} = 1 - \frac {I (\boldsymbol {x} _ {t} ; \boldsymbol {x} _ {0})}{H (\boldsymbol {x} _ {0})}.
$$

在 absorbing `[MASK]` 的特例下，论文推导出它退化为：

$$
\beta _ {t} = \frac {1}{T - t + 1}.
$$

这意味着到第 $t$ 步时，大约 $t/T$ 的位置已经被 mask。Appendix Figure 6 用柱状图显示，在长度 50 的序列上，这种 schedule 对 mask 数量的权重接近均匀，只在边界略低。

### 整体算法流程

```text
训练数据 x0（离散 token / 量化像素）
        |
        v
选择转移矩阵族 Q_t 和 schedule
        |
        v
采样时间步 t，并用 q(xt|x0) 生成带噪样本 xt
        |
        v
神经网络预测 p~θ(x0|xt)
        |
        v
用已知 q(xt-1, xt | x0) 构造 pθ(xt-1|xt)
        |
        v
优化 L_vb 或 L_λ

生成时：xT ~ stationary/prior -> xT-1 -> ... -> x0
```

### 与 BERT、自回归模型和 MLM 的联系

论文第 4 节和 Appendix A.3 说明：

- 一步 absorbing+uniform D3PM 可以对应 BERT 的 denoising objective。
- 如果前向过程按固定顺序逐个 mask token，那么自回归模型也可视为一种离散扩散。
- absorbing `[MASK]` D3PM 在特定 schedule 和 $\boldsymbol {x} _ {0}$-parameterization 下，会变成一种重新加权的 generative masked language model 目标。

注意：这些部分的 OCR 数学比主方法部分更嘈杂，所以这里保留为论文主张的概念解释；若需要逐式引用，应回到原始 PDF 核对。

### 实验结论

#### text8

text8 是 27 个字符的字符级数据集。D3PM absorbing/mask 模型是表中最好的 D3PM 变体：1000 步时达到 $\leq 1.45 \pm 0.02$ bits/char，256 步和 20 步也保持相对较好。它优于 uniform 和 nearest-neighbor D3PM，但仍弱于 Transformer XL 等强自回归模型。

#### LM1B

LM1B 使用 8192 大小的 sentencepiece 词表和长度 128 的 packed sequences。D3PM absorbing 在 perplexity 上显著优于 uniform 和 nearest-neighbor D3PM，并且可以用较少推断步数得到合理结果。Figure 2 的曲线也显示 mask diffusion 的 perplexity 始终低于 uniform diffusion。不过它仍没有超过自回归 Transformer / Transformer XL。

#### CIFAR-10

图像实验把像素值当作有序离散类别。D3PM Gauss 比 uniform 和 absorbing 更适合图像；进一步结合 logistic 参数化和 $L _ {\lambda=0.001}$ 后，表中最佳 D3PM 结果为 IS $8.56 \pm 0.10$、FID $7.34 \pm 0.19$、NLL $\leq 3.435 \pm 0.007$ bits/dim。Figure 3 和 Figure 7 显示了可辨认的 CIFAR-10 样本，但连续扩散模型在若干 FID 指标上仍更强。

### 局限性和复现状态

论文自己指出，D3PM 在文本上仍落后于强自回归模型（例如 Transformer XL），在图像质量指标上也仍落后于一些连续扩散模型。nearest-neighbor 文本扩散的结果并不稳定：text8 上只小幅改善，LM1B 上反而比 uniform 差，说明“embedding 近邻”不一定是好的扩散局部性。

`github_links.json` 中只有 JAX 和 Flax 的参考文献链接，不是论文实现仓库；也没有 supplementary markdown。因此，本文档只能基于论文和本地图片解释方法，不能验证代码实现与论文是否一致。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary: Structured Denoising Diffusion Models in Discrete State-Spaces (D3PM)

### What problem does the paper solve?

D3PM extends denoising diffusion probabilistic models to categorical data such as text tokens and quantized image pixels. Continuous DDPMs typically corrupt data with Gaussian noise, but discrete data needs a categorical corruption process that can preserve or destroy information in domain-aware ways. The paper proposes a general discrete-state diffusion framework where the forward noising process is controlled by transition matrices $\boldsymbol {Q} _ {t}$ rather than by only continuous Gaussian variance (paper lines 9-11, 46-88).

### What is new?

The main novelty is structured categorical corruption. Instead of using only uniform multinomial noise, D3PM explores several transition families:

- **Uniform transitions** as a baseline categorical diffusion process.
- **Absorbing-state transitions** that send tokens/pixels to a mask-like state; for text this connects to `[MASK]` language modeling.
- **Discretized Gaussian transitions** that favor nearby ordinal states, useful for quantized image values.
- **Token-embedding nearest-neighbor transitions** that corrupt text toward nearby embedding-space tokens.

The method also uses an $\boldsymbol {x} _ {0}$-parameterized reverse process and introduces a hybrid objective $L _ {\lambda}$ that adds an auxiliary denoising cross-entropy term to the variational bound (paper lines 89-130, 304-356).

### High-level method

D3PM trains a neural reverse Markov chain to invert a fixed categorical forward Markov chain:

1. Represent each element of the data as a categorical variable.
2. Choose a sequence of transition matrices $\boldsymbol {Q} _ {t}$ that progressively corrupts data to a known stationary distribution.
3. Sample corrupted data $\boldsymbol {x} _ {t}$ from the cumulative transition $q(\boldsymbol {x} _ {t}|\boldsymbol {x} _ {0})$.
4. Predict a clean-data distribution $\widetilde {p} _ {\theta}(\widetilde {\boldsymbol {x}} _ {0}|\boldsymbol {x} _ {t})$.
5. Combine that prediction with the known forward posterior to obtain $p _ {\theta}(\boldsymbol {x} _ {t-1}|\boldsymbol {x} _ {t})$.
6. Train with $L _ {\mathrm{vb}}$ or the hybrid objective

$$
L _ {\lambda} = L _ {\mathrm{vb}} + \lambda \mathbb {E} _ {q (\boldsymbol {x} _ {0})} \mathbb {E} _ {q (\boldsymbol {x} _ {t} | \boldsymbol {x} _ {0})} [ - \log \widetilde {p} _ {\theta} (\boldsymbol {x} _ {0} | \boldsymbol {x} _ {t}) ].
$$

At generation time, the model starts from the terminal distribution and iteratively denoises back to a discrete sample. The reverse parameterization can skip steps, which enables fewer inference iterations than the training horizon in experiments (paper lines 109-130, 149-190).

### Evaluation and main findings

- **text8:** The absorbing/mask D3PM is the strongest D3PM variant in Table 1, reporting $\leq 1.45 \pm 0.02$ bits/char at 1000 steps and remaining competitive at fewer steps. It outperforms the paper's uniform and nearest-neighbor D3PM variants, though strong autoregressive baselines such as Transformer XL remain better in bits/char (paper lines 149-184).
- **LM1B:** The absorbing model reports substantially lower perplexity than uniform and nearest-neighbor D3PM variants at 1000, 128, and 64 inference steps. It approaches but does not beat autoregressive Transformer baselines (paper lines 180-190).
- **CIFAR-10:** Discretized Gaussian transitions perform best among the basic D3PM image variants, and Gauss + logistic with $L _ {\lambda=0.001}$ reports the best D3PM row: IS $8.56 \pm 0.10$, FID $7.34 \pm 0.19$, and NLL $\leq 3.435 \pm 0.007$ bits/dim. Continuous diffusion models still have stronger FID in several cited rows, while D3PM improves likelihood over the cited DDPM baselines (paper lines 192-210, 220-222).

### Figure-backed intuition

Figure 1 visually shows why transition choice matters: uniform corruption scatters states broadly, Gaussian-like corruption preserves local structure, and absorbing corruption collapses states to mask-like values. Figures 2, 3, 7, 8, and 9 show qualitative and scaling behavior for text and image sampling, with the strongest visual trend being that absorbing/mask diffusion gives better text curves than uniform diffusion, while Gauss+logistic produces recognizable CIFAR-10 samples.

### Limitations

The paper itself notes that D3PMs remain worse than strong autoregressive models such as Transformer XL for text generation and that continuous diffusion models still produce stronger image quality by standard metrics (paper lines 220-222). Nearest-neighbor token diffusion is a mixed result: it only narrowly improves over uniform on text8 and performs worse than uniform on LM1B, suggesting that embedding similarity is not automatically useful as a diffusion locality notion (paper lines 184-190).

### Reproducibility status

- **Mode:** paper-only.
- **Code:** Not found. The acquisition manifest reports no project repository URL, and `github_links.json` contains only JAX and Flax library URLs from the references, not a D3PM implementation repository.
- **Supplement:** Not found; `SUPP_MD=none`.
- **Implementation details in paper:** Appendix B gives architecture and training settings for image and text experiments, including JAX/Flax, transformer/U-Net configurations, optimizer settings, TPU training, and evaluation metrics (paper lines 774-810). However, no local scripts, configs, checkpoints, or direct source lines are available in this workspace.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
