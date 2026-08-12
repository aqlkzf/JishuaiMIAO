---
layout: default
permalink: /paper-atlas/driftingmodels-fe6047b0/
title: "DriftingModels"
nav: false
description: "Drifting Models 不在推断时把噪声逐步搬运成图像，而是在训练过程中不断更新同一个生成器，使其输出分布沿一个“真实样本吸引、生成样本排斥”的向量场移动。训练结束后，生成仍然只是一次前向计算。"
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
      <span>Representation Models</span>
      <span>arXiv · 2026</span>
    </div>
    <h1>DriftingModels</h1>
    <p>Generative Modeling via Drifting</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2602.04770" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Drifting Models：把生成器训练看成分布的“漂移”

### 一句话理解

Drifting Models 不在推断时把噪声逐步搬运成图像，而是在训练过程中不断更新同一个生成器，使其输出分布沿一个“真实样本吸引、生成样本排斥”的向量场移动。训练结束后，生成仍然只是一次前向计算。

### 1. 问题设置：变化发生在训练期

令噪声为 $\epsilon\sim p_\epsilon$，生成器为 $f_\theta$。生成分布是推前分布

$$
q_\theta=(f_\theta)_\#p_\epsilon.
$$

论文把训练轮次 $i$ 下的生成器写成 $f_i$，其分布为 $q_i$。一次更新不是沿推断时间积分 ODE/SDE，而是让当前生成点 $x_i=f_i(\epsilon)$ 朝漂移场移动：

$$
x_{i+1}=x_i+\eta\,V(x_i;p,q_i).
$$

因此图 1 的横向演化表示优化过程中的 $q_0,q_1,\ldots$，不是单张图像在推断时经历的多步轨迹。这正是它能保持 1-NFE 推断的关键。

### 2. 漂移场：真实分布吸引，模型分布排斥

对一个生成点 $x$，论文用核加权均值位移构造两部分：

$$
V(x;p,q)=V_p^+(x)-V_q^-(x),
$$

其中 $V_p^+$ 把 $x$ 拉向附近真实样本，$V_q^-$ 则描述附近生成样本形成的聚集方向；减去后产生排斥，防止所有质量挤在少数模式上。核采用

$$
k_\tau(x,y)=\exp\!\left(-\frac{\lVert x-y\rVert}{\tau}\right).
$$

图 2 直接画出了这两个向量的合成。实现同时使用三个温度 $R=(0.02,0.05,0.2)$：小温度关注局部结构，大温度提供更长程的校正。

该场满足交换两种分布时变号的反对称性：$V(x;p,q)=-V(x;q,p)$。所以 $p=q$ 时必有 $V=0$。需要保留一个理论边界：一般情况下，$V=0\Rightarrow p=q$ 并非仅由反对称性自动保证；论文附录 C.1 给出的是额外条件下的论证与启发式说明。

### 3. 如何把向量场变成可训练损失

当前生成点和漂移目标都依赖模型。论文用停止梯度固定右侧目标：

$$
\mathcal L_{\mathrm{drift}}
=\left\lVert
f_\theta(\epsilon)-
\operatorname{sg}\!\left[f_\theta(\epsilon)+V(f_\theta(\epsilon);p,q_\theta)\right]
\right\rVert^2.
$$

直观上，先根据当前分布算出每个生成点应该去哪里，再只让左侧生成器追这个冻结目标。这样避免梯度穿过“目标如何由当前模型产生”的整条路径。`drifting/drift_loss.py` 中的 `old_gen_scaled + force_across_R` 就是冻结目标，最终返回与当前生成特征的均方误差。

### 4. 小批量与记忆队列

真实分布和生成分布都无法在一次训练中完整枚举，因此实现使用记忆队列近似邻域：

- 每个类别维护正样本队列，提供同类真实特征；
- 全局队列提供无条件真实负样本；
- 当前批次中的生成特征也作为排斥项，生成样本自身用对角掩码排除；
- `ArrayMemoryBank` 是环形缓冲区，配置中每类正队列大小为 128、全局负队列为 1000，每次分别采样 64 和 32 个特征。

代码还加入了论文公式之外、但对数值稳定重要的实现细节：用批内距离尺度归一化距离；分别对目标轴和查询轴做 softmax 后取几何平均；每个温度下先归一化力，再跨温度相加。这些是已发布实现的稳定化选择，不应误写成纯理论公式的唯一实现。

### 5. 在特征空间而不是像素空间比较

高维图像中的欧氏距离未必表达语义邻近性。论文因此把真实图像和生成图像送入冻结的特征编码器 $\phi_l$，在多个层级上计算漂移，再求和：

$$
\mathcal L=\sum_l \mathcal L_{\mathrm{drift}}
\bigl(\phi_l(x_{\mathrm{gen}}),\phi_l(x_{\mathrm{real}})\bigr).
$$

默认潜空间实验用预训练 MAE 特征。特征编码器只在训练时服务于损失；推断时不需要它。潜空间版本还依赖预训练 SD-VAE，把 $32\times32\times4$ 潜变量解码为 $256\times256$ 图像。

### 6. 训练期 CFG 与一次推断

通常的 classifier-free guidance 会在推断时分别计算条件和无条件输出。本文把 guidance 作用移到训练损失里：同类真实特征形成条件吸引，来自所有类别的无条件真实特征作为加权负项。`train.py::train_step` 中

```python
uncond_w = (cfg - 1) * (gen_per_label - 1) / n_uncond
```

把随机采样的 CFG 强度转换成无条件负样本权重。随后生成器只前向一次，特征编码器生成多尺度特征，逐层调用 `drift_loss`，再执行梯度裁剪和 EMA 更新。

推断路径更短：`inference.py` 加载本地或 Hugging Face 权重，调用生成器一次，并在需要时解码潜变量。这里没有扩散采样循环，也不需要训练期的记忆队列或特征编码器。

### 7. 从代码左到右看一次训练步

1. `train_gen` 建立按类别的正样本队列和一个全局负样本队列。
2. `train_step` 为每个标签采样噪声及 CFG 强度，并从队列取同类正样本和全局无条件样本。
3. 生成器根据噪声、类别和 `cfg_scale` 产生一批图像或潜变量。
4. 冻结特征编码器把生成样本、正样本和无条件样本映射成多尺度特征字典。
5. 每个尺度调用 `drift_loss`：计算成对 L2 距离、核权重、吸引/排斥力和停止梯度目标。
6. 各尺度损失相加，反向传播后裁剪梯度，并更新参数 EMA。
7. 新的真实特征写回环形队列，供后续批次使用。

论文机制与本地代码的对应关系总体为 **Exact/implementation-extended**：推前分布、吸引减排斥、停止梯度、多尺度特征损失和训练期 CFG 均有直接实现；距离缩放、双向 softmax 和逐温度归一化属于代码中的额外稳定化。

### 8. 图和实验说明了什么

- 图 3–4 的二维实验显示，从模式之间、远离目标或塌缩的初始化出发，生成分布都能向双峰真实分布移动，同时漂移损失下降。这是机制演示，不等同于一般收敛证明。
- 图 5 展示 CFG 的典型质量—覆盖权衡：更强 guidance 提高 IS，但超过最佳点后 FID 变差。
- 图 6 用 CLIP 最近邻检查生成样本与 ImageNet 训练图，支持“不是简单复制训练图”的经验结论，但不能证明不存在更隐蔽的记忆。
- 图 7–15 给出无筛选样本和与 improved MeanFlow 的并列比较，支持一次前向也能得到有竞争力的视觉质量。
- 论文报告 ImageNet $256\times256$、1-NFE 条件生成中，潜空间模型 FID 1.54、像素空间模型 FID 1.61。该数字来自论文表格，本工作区没有重新完成 TPU 规模训练与 50k 样本 FID 复现。

### 9. 适用范围与复现边界

- 证据覆盖论文正文及同一 `paper.md` 中的附录 A–C；没有独立补充材料文件。
- 本地代码来自 `https://github.com/lambertae/drifting`，固定到提交 `accd0cf09c33b70892d33941d2a287ca86cb92e1`。
- 上游训练面向 ImageNet 和 TPU 规模环境，还要求数据路径与 FID 参考统计；本次完成的是源码—论文核对，不是大规模数值复现。
- 图像结果依赖预训练特征网络，潜空间配置还依赖预训练 VAE；“一次生成”不表示整个训练系统不借助外部表征。
- 反对称场、队列采样和多温度归一化共同构成当前方法；只保留“真实吸引、生成排斥”的口号会遗漏实现中决定稳定性的部分。

### 证据入口

- 论文与附录：`paper source/paper/vlm/paper.md`
- 图：`paper source/paper/vlm/images/Fig*.jpg`
- 漂移损失：`drifting/drift_loss.py`
- 训练路径：`drifting/train.py`
- 队列：`drifting/memory_bank.py`
- 一步推断：`drifting/inference.py`
- 默认潜空间配置：`drifting/configs/gen/latent_sota_L.yaml`

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Drifting Models: Generative Modeling via Drifting

### Paper Metadata

- **Title**: Generative Modeling via Drifting
- **Authors**: Mingyang Deng, He Li, Tianhong Li, Yilun Du, Kaiming He
- **Venue**: arXiv (2026-02-04; v2 2026-02-06)
- **arXiv**: 2602.04770v2
- **DOI**: 10.48550/arXiv.2602.04770
- **Project**: https://lambertae.github.io/projects/drifting/
- **Code**: https://github.com/lambertae/drifting (JAX release; commit recorded in `drifting/.repo_source`)

---

### Motivation & Novelty

Diffusion and flow-matching models implement a distribution pushforward *at inference time* via many small steps, which makes sampling expensive (many network evaluations per sample). This paper reframes generative modeling around the **training-time evolution** of the generator’s pushforward distribution: as SGD updates the network parameters, the induced distribution should “drift” toward the data distribution, enabling **single-step (1-NFE) inference**.

The core idea is to define a **drifting field** $\mathbf{V}_{p,q}(\mathbf{x})$ that becomes zero at equilibrium when the generated distribution $q$ matches the target data distribution $p$. Training then minimizes the drift magnitude (implemented via a stop-gradient regression loss), so that iterative optimization evolves $q$ toward $p$.

---

### Method Overview

1. **Generator** $f_\theta$: one forward pass maps noise $\epsilon$ (plus conditioning) to a sample $\mathbf{x}=f_\theta(\epsilon, c, \alpha)$.
2. **Drifting field** $\mathbf{V}_{p,q}$: computed from *positive* samples $\mathbf{y}^+\sim p$ (real data) and *negative* samples $\mathbf{y}^-\sim q$ (generated samples and optional “unconditional” negatives for CFG). Anti-symmetry (Prop. 3.1) ensures $p=q \Rightarrow \mathbf{V}=0$.
3. **Stop-grad drift loss (Eq. 6)**: regress current samples toward a frozen drifted target $\operatorname{sg}(\mathbf{x}+\mathbf{V}(\mathbf{x}))$.
4. **Feature-space drifting (Eq. 13–14)**: compute drift in a pretrained encoder feature space (multi-scale / multi-location), which stabilizes and improves training for high-dimensional images.
5. **Training-time CFG**: incorporate extra unconditional real samples as weighted negatives to support classifier-free guidance while keeping inference single-step.

See `doc_method.md` for the derivation and algorithm, and `doc_code.md` for the exact code mapping.

---

### Evaluation

- **ImageNet 256×256**
  - Latent-space (SD-VAE latents): **FID 1.54** (1-NFE), reported for the best latent model.
  - Pixel-space: **FID 1.61** (1-NFE) in the paper’s pixel protocol.
- **Robotics control (Diffusion Policy replacement)**: a 1-NFE “Drifting Policy” matches or exceeds a 100-NFE diffusion-policy baseline on several tasks, following Diffusion Policy (RSS 2023; Chi et al.) protocols (paper Table 7).

---

### Reproducibility (Code + Practicality)

**Rating: 4 / 5.**

- The repo provides a full JAX training pipeline, inference/FID evaluation scripts, and pretrained weights via HuggingFace (`hf://...` IDs in the README).
- Practical caveats:
  - Reproducing paper-scale numbers expects **TPU** availability and access to **ImageNet** plus precomputed FID reference statistics (configured in `drifting/utils/env.py`).
  - The training is nontrivial to rerun end-to-end on commodity GPUs due to batch sizes / evaluation scale.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
