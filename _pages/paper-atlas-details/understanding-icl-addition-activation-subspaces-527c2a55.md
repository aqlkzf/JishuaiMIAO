---
layout: default
permalink: /paper-atlas/understanding-icl-addition-activation-subspaces-527c2a55/
title: "Understanding_ICL_Addition_Activation_Subspaces"
nav: false
description: "给大模型看几个“输入→输出”样例后，它常常能临时学会一个规则，并把规则用于新输入。这叫上下文学习（in-context learning, ICL）。论文追问的不是“模型答对了吗”，而是更细的机制问题：规则信息从哪些 token 被读出，存在哪些注意力头里，以什么几何结构表示，又怎样汇总到最终预测位置？ 作者选择了一个可控任务族 add-k。五个示例都满足 随后模型要补全查询 xq\\rightarrow。"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>Understanding_ICL_Addition_Activation_Subspaces</h1>
    <p>Understanding In-context Learning of Addition via Activation Subspaces</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2505.05145" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 用激活子空间理解大模型如何做上下文加法学习

### 这篇论文想解决什么问题？

给大模型看几个“输入→输出”样例后，它常常能临时学会一个规则，并把规则用于新输入。这叫上下文学习（in-context learning, ICL）。论文追问的不是“模型答对了吗”，而是更细的机制问题：**规则信息从哪些 token 被读出，存在哪些注意力头里，以什么几何结构表示，又怎样汇总到最终预测位置？**

作者选择了一个可控任务族 *add-$k$*。五个示例都满足

$$
y_i=x_i+k,
$$

随后模型要补全查询 $x_q\rightarrow$。实验令 $x\in[1,100]$、$k\in[1,30]$。不同任务的输入域完全相同，只是隐藏的 $k$ 不同，所以模型不能仅凭查询猜任务，必须从示例中提取差值。

### 现有方法为什么还不够？

Todd 等人在 ICLR 2024 的 function vector 工作表明，把若干注意力头在示例上的平均输出加到零样本提示的残差流中，可以恢复部分 ICL 能力。但这留下三个问题：

1. 独立按平均间接效应给每个头排序，可能找不到需要协同工作的头组合；
2. 即使知道某个头重要，也不知道任务变量 $k$ 在其高维激活中如何编码；
3. 最终 token 上的 function vector 不能告诉我们信息最初来自哪个示例、哪个 token。

本文依次解决这三层定位：**头 → 子空间 → token 信号流**。

### 整体计算流程

```text
五个 add-k 示例
      │
      ▼
对每个 k、每个注意力头，平均 100 个提示的末 token 输出 h_k
      │
      ▼
在 1024 个头上联合学习稀疏系数 c_h
      │
      ▼
得到 33 个显著头
      │
      ▼
分层、分头做均值消融
      │
      ▼
定位三个聚合头：(15,2)、(15,1)、(13,6)
      │
      ▼
每个头对 30 个任务向量做 PCA
      │
      ▼
定位 6 维任务子空间
      │
      ▼
旋转到周期特征方向
      ├── 2、5、10 周期：个位信息
      └── 25、50 周期：粗粒度大小信息
      │
      ▼
利用注意力矩阵恒等式回溯到早期 label token
      │
      ▼
发现每个示例提取自己的 y_i-x_i，并呈现自校正相关性
```

### 第一步：联合稀疏优化找重要注意力头

记 $h_k$ 为某个头在大量 add-$k$ 五样本提示上的平均末 token 输出。作者给所有 1024 个头各设一个 $c_h\in[0,1]$，构造

$$
v_k(c)=\sum_h c_hh_k.
$$

把 $v_k(c)$ 加到零样本查询的残差流后，优化

$$
\mathcal L(c)=\mathbb E_{k,x_q}\left[\ell\bigl(x_q,x_q+k;v_k(c)\bigr)\right]
+\lambda\lVert c\rVert_1.
$$

第一项要求干预后预测正确，第二项用 $\ell_1$ 正则促使只有少量头的系数非零。实验用 25 个 $k$ 训练和分布内测试，另留 5 个 $k$ 做分布外测试；AdamW 学习率为 0.01，batch size 为 128，$\lambda=0.05$。

结果有 33 个头满足 $c_h>0.2$。它们的非加权总和达到 0.85 干预准确率，而 Todd 等人的平均间接效应方法选出的 33 个头只有 0.31。这说明重要的是联合寻找能协作的稀疏组合，而不是逐头排名。

### 第二步：均值消融把 33 个头缩到 3 个

有些头可能只提供“输出应该像数字”之类的通用格式信息，而不携带 $k$。作者用跨任务均值 $\bar h$ 替换某些头的任务特异向量：

$$
v_k=\sum_{h\in\mathcal H_0}\bar h+
\sum_{h\in\mathcal H_{\mathrm{sig}}\setminus\mathcal H_0}h_k.
$$

这样保留该头的一般作用，却擦除随 $k$ 变化的信息。先做层级消融，只保留第 13、15 层的任务特异信号仍有 0.83 准确率；再逐头消融，最终定位到 $(15,2)$、$(15,1)$、$(13,6)$。

三个头直接求和可达到 0.79 干预准确率。反过来，在真实五样本提示里把这三个头均值消融，准确率从 0.87 降到 0.43；随机消融其他三个显著头通常几乎不影响准确率。这分别提供了接近“充分性”和“必要性”的证据。

### 第三步：从 128 维压缩到 6 维任务子空间

每个头的激活有 128 维。作者对每个重要头的 30 个任务向量做 PCA，前六个方向解释 97% 的任务方差。仅把 $h_k$ 投影到六维子空间后，三个头的干预准确率从 0.79 只降到 0.76。因此这不只是统计上的高方差子空间，也保留了大部分因果功能。

原始主成分坐标随 $k$ 呈现混合周期。作者搜索周期和相位，并用最小二乘把六个 PC 旋转到更容易解释的方向，得到周期 2、5、10、10、25、50。由此形成：

- 1 个奇偶方向（周期 2）；
- 4 维个位子空间（周期 2、5、10、10）；
- 2 维大小子空间（周期 25、50），表示较粗的十位/数值幅度。

作者不仅观察曲线，还做投影干预。“投影到子空间”检查该子空间是否足以保留对应信号，“投影出子空间”检查去掉它是否破坏信号。例如只保留个位子空间时，个位错误率仍低；去掉它后，个位错误几乎解释了全部答案错误。

### 第四步：把末 token 的聚合信号追溯到每个示例

注意力头在最后位置的输出可以写成

$$
h(p)=\sum_{t\in p}\alpha_tO_hV_hz_t.
$$

投影到六维任务子空间后，每个早期 token 的贡献为

$$
\alpha_tW_hO_hV_hz_t.
$$

这自然分成两部分：$W_hO_hV_hz_t$ 是从 token $t$ 提取的内容，$\alpha_t$ 是末 token 对它的聚合权重。两者都在每个示例的标签 $y_i$ token 处达到峰值。

为了判断提取了什么，作者比较 $W_hO_hV_hz_t$ 与不同任务向量 $\tilde h_k$ 的内积。在故意让五个示例具有不同 $k_i$ 的 mixed-$k$ 提示中，每个标签 token 的最大匹配位置稳定落在 $k=y_i-x_i$。也就是说，每个示例先各自贡献一个规则信号，随后才在末位置聚合。

### “自校正”是什么意思？

作者比较五个示例位置上的任务对齐信号。在 Llama 模型中，不同示例之间的负相关远强于正相关。因此，如果较早示例产生偏离正确方向的噪声，后续示例更可能写入反方向信号，使最终表示稳定。作者把这称为 self-correction。

这个结论应谨慎理解：论文观测到的是经过机制定位后的信号负相关，并非直接证明模型显式实现了某个误差控制算法。该模式在 Llama 家族最强，在 Qwen-2.5 中只有部分头成立。

### 跨模型结果与边界

Llama-3.2-3B-instruct 和 Llama-3.2-3B 也能定位到同一层的三个头，并出现周期表示。Qwen-2.5-7B 的三个头整体恢复能力较弱，其中只有一个头明显呈周期结构，另两个头在 $[1,10]$、$[11,20]$、$[21,30]$ 区间出现不连续。论文推测这与 Qwen 逐位 token 化数字、而 Llama 对 100 以下数字常用单 token 有关，但没有做受控 tokenizer 实验，所以这仍是推测。

### 如何评价这项工作？

最有价值的不是“加法由三个头完成”这一孤立结论，而是一套可迁移的机制分析路线：

1. 用行为保持目标联合定位组件；
2. 用均值消融区分任务特异信息和通用贡献；
3. 用低维化压缩机制；
4. 用可解释基旋转揭示几何结构；
5. 用投影干预测试子空间的充分性和必要性；
6. 用注意力代数把聚合表示回溯到 token 来源。

但结论目前只覆盖窄范围加法、少数模型和有限 $k$。**本地获取的论文中未找到公开代码仓库**，也缺少完整随机种子、训练轮数/停止条件、模型精确 revision 和运行环境。因此本工作区是 `paper-only`：方法和结果由论文直接支持，但没有代码级复核。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Understanding In-context Learning of Addition via Activation Subspaces

### Problem

The paper asks how a large pretrained transformer turns a handful of demonstrations into a task rule during one forward pass. It uses a controlled family of five-shot *add-$k$* tasks, $x_i\rightarrow x_i+k$, where every task shares the same input domain. This removes a common confound in semantic ICL benchmarks: the query alone cannot reveal which $k$ should be applied.

### Limitations of earlier approaches

Prior function-vector work (Todd et al., ICLR 2024) showed that averaged attention-head outputs can carry task information, but selected heads independently by average indirect effect and did not explain how task information is encoded or assembled across demonstrations. Coarse analyses of induction or function-vector heads also leave the internal computational structure unresolved. Here, the authors jointly optimize all heads, restrict the mechanism to low-dimensional activation subspaces, and trace final-token aggregation back to individual label tokens.

### Method

For each attention head, the authors average its final-token output over 100 five-shot prompts for every $k\in[1,30]$. They learn coefficients $c_h\in[0,1]$ for all 1,024 Llama-3-8B-instruct heads by minimizing zero-shot intervention cross-entropy plus $\lambda\lVert c\rVert_1$. Thirty-three heads survive the sparse search. Layer-wise and head-wise mean ablation then reduces these to $(15,2)$, $(15,1)$, and $(13,6)$.

PCA over the 30 task vectors localizes each selected head to six dimensions that explain 97% of task variance. A least-squares rotation exposes feature directions with periods 2, 5, 10, 10, 25, and 50. Causal projections associate four directions with the unit digit and two with coarse magnitude. Finally, the attention identity

$$
h(p)=\sum_t\alpha_tO_hV_hz_t
$$

decomposes the final head output into token-wise extraction and aggregation. Mixed-$k$ prompts show that label tokens encode their own $y_i-x_i$, while negative correlations across demonstration signals motivate a self-correction interpretation.

### Main evidence

- Weighted sparse heads reach 0.83 in-distribution and 0.87 held-out intervention accuracy, close to clean accuracies 0.89 and 0.92.
- The 33 unweighted selected heads reach 0.85, versus 0.31 for 33 heads selected by the prior average-indirect-effect approach.
- The three-head sum reaches 0.79 intervention accuracy. Mean-ablating those heads in five-shot prompts lowers clean accuracy from 0.87 to 0.43; random three-head ablations usually leave it at least 0.86.
- Projecting the three heads to six dimensions retains 0.76 intervention accuracy versus 0.79 before projection.
- Llama-3.2 variants show similar head and periodic-subspace patterns. Qwen-2.5 is weaker and less uniform: one selected head is periodic, while two show digit-interval discontinuities and the self-correction pattern is only partial.

### Interpretation and limitations

The strongest contribution is a reusable mechanistic workflow: jointly localize components, test necessity and sufficiency, compress activations, rotate toward interpretable features, and exploit attention algebra to follow information across positions. The results provide unusually fine-grained causal evidence for one structured ICL family, but they do not establish a universal ICL circuit. The arithmetic range is narrow, model families are few, some ablation choices involve qualitative judgment, and the proposed tokenizer explanation for Qwen is conjectural.

### Reproducibility

**Rating: 2.5/5 (paper-only).** The paper reports prompt ranges, dataset sizes, splits, optimizer, learning rate, batch size, sparsity weight, selected heads, PCA dimensionality, and intervention results. No public implementation repository was found in the acquired arXiv source, and exact scripts, seeds, epoch/stopping settings, model revisions, and runtime details are not provided. Reproduction is conceptually possible but would require rebuilding the activation-patching pipeline and matching tokenization and prompt formatting.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
