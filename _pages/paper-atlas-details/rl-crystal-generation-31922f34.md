---
layout: default
permalink: /paper-atlas/rl-crystal-generation-31922f34/
title: "RL_crystal_generation"
nav: false
wide: true
description: "晶体生成模型通常通过最大化训练数据似然来学习“什么样的晶体常见”。这很适合生成看起来合理的样本，却与材料发现的目标存在错位：研究者更希望找到数据库中少见、同时又具有热力学可行性的结构。 这个矛盾可概括为新颖性—稳定性困境： 贴近训练分布，结构往往更稳定，但容易重复已知化学空间； 远离训练分布，新颖性提高，却更容易出现高能、不合理或不可合成的结构。"
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
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>RL_crystal_generation</h1>
    <p>Guiding generative models to uncover diverse and novel crystals via reinforcement learning</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/hspark1212/chemeleon2" target="_blank" rel="noopener noreferrer" aria-label="Open code for RL_crystal_generation">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Chemeleon2-RL 方法详解：用强化学习引导晶体生成模型探索新材料

### 1. 论文要解决什么问题？

晶体生成模型通常通过最大化训练数据似然来学习“什么样的晶体常见”。这很适合生成看起来合理的样本，却与材料发现的目标存在错位：研究者更希望找到数据库中少见、同时又具有热力学可行性的结构。

这个矛盾可概括为**新颖性—稳定性困境**：

- 贴近训练分布，结构往往更稳定，但容易重复已知化学空间；
- 远离训练分布，新颖性提高，却更容易出现高能、不合理或不可合成的结构。

已有 DiffCSP（*NeurIPS*，2023）、MatterGen（*Nature*，2025）和 Chemeleon1（*Nature Communications*，2025）等方法直接在晶体原子表示上做扩散。晶体 (C=(A,X,L)) 同时包含离散的原子种类 (A)、连续的分数坐标 (X) 和相互耦合的晶格 (L)。这种混合空间需要不同的扩散机制，难以计算统一的策略概率，也使强化学习需要的大批量 rollout 成本很高。潜空间方法 ADiT（ICML，2025）采样更快，但潜变量压缩又可能放大解码误差，并弱化稀有结构。

论文提出 Chemeleon2-RL：先把晶体压缩到连续潜空间，再把反向扩散过程视为策略，用 GRPO 和可验证的科学奖励进行后训练。

### 2. 核心创新

方法并不是从头训练一个新的晶体模型，而是在预训练 Chemeleon2 上增加一层“面向发现目标的策略优化”：

1. **连续潜空间动作**：VAE 把原子种类、坐标和晶格统一为连续潜变量，使每一步反向扩散都具有可计算的高斯转移概率。
2. **无 critic 的 GRPO**：对相同条件生成一组候选，用组内奖励均值和标准差构造优势，避免为高维扩散状态训练价值网络。
3. **多目标科学奖励**：同时评价创造性、稳定性、结构多样性和组成多样性；奖励权重可调整，也能替换成带隙等性质目标。
4. **只微调去噪策略**：VAE 解码器被冻结，强化学习只更新扩散去噪器，尽量保留预训练阶段学到的晶体先验。

### 3. 表示、输入与输出

晶体写为

$$
C=(A,X,L),
$$

其中：

- (A=(A_1,\ldots,A_N)\in\mathbb{Z}^N)：(N) 个原子的元素类型；
- (X\in[0,1)^{N\times3})：分数坐标；
- (L\in\mathbb{R}^{3\times3})：晶格矩阵，在 VAE 输入中表示为 (a,b,c,\alpha,\beta,\gamma)。

强化学习阶段的条件记为 \(\mathbf{x}\)。在无条件从头生成 benchmark 中，\(\mathbf{x}\) 仅包含晶胞原子数；在性质引导任务中还可以包含目标带隙等约束。最终输出是完整晶体

$$
c_0=D_\phi(\mathbf{z}_0),
$$

其中 (D_\phi) 是冻结的 VAE 解码器。

### 4. 预训练生成器

#### 4.1 VAE：把异构晶体变量压缩到连续空间

编码器近似后验 (q_\phi(\mathbf{z}\mid C))，解码器定义 (p_\theta(C\mid\mathbf{z}))。论文给出的 ELBO 为

$$
\mathcal{L}(\theta,\phi)=\mathbb{E}_{q_\phi(\mathbf{z}\mid C)}[\log p_\theta(C\mid\mathbf{z})]-\beta\mathrm{KL}[q_\phi(\mathbf{z}\mid C)\parallel p(\mathbf{z})].
$$

第一项要求潜变量能重建原子类型、坐标和晶格，第二项把潜空间正则到高斯先验附近。论文使用 8 维原子级潜变量，并报告 MP-20 测试集上 99.4% 的 StructureMatcher 重建准确率。

代码中，`VAEModule.encode` 构造对角高斯后验，`reconstruct` 把解码结果还原为原子种类、分数/笛卡尔坐标、晶格长度和角度（`src/vae_module/vae_module.py:57-74,236-263`）。RL 初始化时将 VAE 设为评估模式并冻结参数（`src/rl_module/rl_module.py:45-53`）。

#### 4.2 潜空间扩散：学习晶体先验

前向过程逐步向干净潜变量加入高斯噪声：

$$
q(\mathbf{z}_t\mid\mathbf{z}_{t-1})=\mathcal{N}(\sqrt{1-\beta_t}\mathbf{z}_{t-1},\beta_tI).
$$

扩散 Transformer 学习预测噪声：

$$
\mathcal{L}_{\mathrm{DDPM}}=\mathbb{E}_{t,\mathbf{z}_0,\epsilon}\left[\lVert\epsilon-\epsilon_\theta(\mathbf{z}_t,t)\rVert^2\right].
$$

论文预训练使用 1,000 个 DDPM 时间步，生成时用 50 步加速采样。仓库 RL 默认配置是 50 步 DDIM 且 `eta=1.0`，因此实际 RL rollout 保留随机性，并不是严格的确定性 DDIM（`configs/rl_module/rl_module.yaml:36-42`）。

### 5. 如何把扩散模型变成强化学习策略？

反向扩散被写成一个有限时域 MDP：

- 状态：\(\mathbf{s}_t=(\mathbf{z}_t,\mathbf{x},t)\)；
- 动作：去噪器预测的噪声 \(\mathbf{a}_t=\epsilon_\theta(\mathbf{z}_t,t)\)；
- 策略：

$$
\pi_\theta(\mathbf{a}_t\mid\mathbf{s}_t)\equiv p_\theta(\mathbf{z}_{t-1}\mid\mathbf{z}_t,\mathbf{x});
$$

- 轨迹：\(\tau=\{\mathbf{z}_T,\ldots,\mathbf{z}_0\}\)；
- 终止奖励：\(R(D_\phi(\mathbf{z}_0),\mathbf{x})\)。

优化目标是

$$
J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}[R(D_\phi(\mathbf{z}_0),\mathbf{x})].
$$

关键点在于：策略概率不是在 (A,X,L) 上直接计算，而是在连续潜空间中，根据每一步高斯转移的均值和标准差计算。这正是潜空间对 RL 的主要价值。

### 6. 从输入到参数更新的完整流程

```text
条件 x（从头生成时为原子数）
  │
  ├─ 对每个条件复制 G=64 份
  ▼
从 N(0,I) 采样初始噪声 z_T
  │
  ├─ 50 步随机反向扩散
  ├─ 保存每一步 z_t、mean、std、旧策略 log-prob
  ▼
终止潜变量 z_0
  │
  ├─ 冻结的 VAE 解码
  ▼
完整晶体 c_0=(A,X,L)
  │
  ├─ 创造性 + 稳定性 + 结构多样性 + 组成多样性
  ▼
每条轨迹的终止奖励 r_i
  │
  ├─ 在共享条件的 64 个样本内部标准化
  ▼
组相对优势 A_hat_i（复用于该轨迹所有时间步）
  │
  ├─ 重算当前策略 log-prob
  ├─ clipped surrogate + KL 近似 - entropy bonus
  ▼
仅更新扩散去噪器参数
```

#### 6.1 生成一组轨迹

每个训练 batch 含 5 个条件，每个条件复制 64 次，所以一次更新生成 320 个晶体。`RLModule.rollout` 在无梯度模式下调用潜扩散采样器，并保存所有潜状态、转移均值/标准差和行为策略 log-prob（`src/rl_module/rl_module.py:64-90,209-223`）。

代码对每个有效原子和潜变量维度计算高斯 log-prob，再利用 mask 排除 padding 并取平均（`src/rl_module/rl_module.py:340-364`）。

#### 6.2 只在终点计算科学奖励

冻结的 VAE 把 (\mathbf{z}_0) 解码成完整结构。奖励不在中间潜状态计算，也不对 MACE、AMD 或 StructureMatcher 反向传播；它们提供的是 policy-gradient 所需的标量反馈。`ReinforceReward` 先集中计算共享指标，再逐项求奖励并加权求和（`src/rl_module/reward.py:41-67`）。

总奖励为

$$
R_{\mathrm{total}}=w_cR_c+w_sR_s+w_{cd}R_{cd}+w_{sd}R_{sd}.
$$

默认权重分别为创造性 1.0、稳定性 1.0、组成多样性 1.0、结构多样性 0.1。

### 7. 四类奖励怎样计算？

#### 7.1 创造性奖励：二值判断加连续 AMD 回退

设 (u_i,v_i\in\{0,1\}) 分别表示样本在当前生成集合中是否唯一、相对参考数据是否新颖。令 (f(x)) 为约化化学式：

$$
R_{\mathrm{creativity}}(x_i)=
\begin{cases}
1,&u_i=1\wedge v_i=1,\\
0,&u_i=0\wedge v_i=0,\\
\min_{y:f(y)=f(x_i),y\ne x_i}\lVert\mathrm{AMD}(x_i)-\mathrm{AMD}(y)\rVert_\infty,&\text{其他情况}.
\end{cases}
$$

AMD 使用周期晶体前 100 个近邻距离构造等距不变量。这样，“既唯一又新颖”明确得 1，“既不唯一也不新颖”得 0；只有一个条件成立时，用同化学式结构间的最小 AMD 距离给出更细的排序。代码与这三个分支一致（`src/rl_module/components.py:90-129`）。

#### 7.2 稳定性奖励：凸包上方能量惩罚

MLFF 预测总能量后，形成能概念上为

$$
E_{\mathrm{form}}^{\mathrm{MLFF}}(x_i)=E_{\mathrm{total}}^{\mathrm{MLFF}}(x_i)-\sum_a\mu_an_a(x_i).
$$

与相同组成的竞争相比较得到凸包上方能量 (E_{\mathrm{hull}})，奖励定义为

$$
R_{\mathrm{stability}}=-\mathrm{clip}(E_{\mathrm{hull}}^{\mathrm{MLFF}},0,1).
$$

凸包上或以下不受惩罚，超过 1 eV/atom 的结构得到 −1。代码还把计算失败产生的 NaN 当作最大惩罚处理（`src/rl_module/components.py:132-149`）。

#### 7.3 结构与组成多样性：MMD 的留一边际贡献

结构特征来自 VAE 潜变量的晶体内均值；组成特征来自原子类型 embedding 的晶体内均值（`src/utils/featurizer.py:55-84`）。生成集合 (X_g) 与参考集合 (X_r) 用多项式核比较，整体奖励是负的无偏 MMD：

$$
r_{\mathrm{div}}(X_g;X_r)=-\frac{\sum_{i\ne j}K(z_g^i,z_g^j)}{M(M-1)}-\frac{\sum_{i\ne j}K(z_r^i,z_r^j)}{N(N-1)}+\frac{2\sum_{i,j}K(z_g^i,z_r^j)}{MN}.
$$

为给每条轨迹单独分配信用，删除第 (m) 个样本并计算差值：

$$
\hat r_{\mathrm{div}}(z_g^m)=r_{\mathrm{div}}(X_g)-r_{\mathrm{div}}(X_g\setminus\{z_g^m\}).
$$

如果一个样本能提高生成集合对参考分布的覆盖、同时减少内部重复，它的边际贡献就更高。`mmd_reward` 直接计算 `mmd_drop - mmd_full`，与上述负 MMD 的边际效用在代数上一致（`src/rl_module/components.py:234-262`）。参考特征超过 50,000 时会随机下采样，这降低成本，也引入一定随机性。

### 8. GRPO 如何更新策略？

#### 8.1 组相对优势

同一条件下的 (G) 条轨迹得到奖励 (r_1,\ldots,r_G)，优势为

$$
\hat A_i=\frac{r_i-\mathrm{mean}(r_{1:G})}{\mathrm{s.d.}(r_{1:G})}.
$$

它回答的是“这个候选相对同条件的其他候选好多少”，不需要额外 critic。因为奖励只在终点出现，整条轨迹的每个扩散时间步共享同一个 (\hat A_i)。代码按连续的 64 样本组进行标准化（`src/rl_module/rl_module.py:92-106`）。

#### 8.2 clipped surrogate

当前策略与 rollout 时旧策略的逐步概率比为

$$
\rho_t(\theta)=\frac{p_\theta(\mathbf{z}_{t-1}\mid\mathbf{z}_t,\mathbf{x})}{p_{\theta_{\mathrm{old}}}(\mathbf{z}_{t-1}\mid\mathbf{z}_t,\mathbf{x})}.
$$

GRPO 最大化

$$
\min\left(\rho_t\hat A_i,\mathrm{clip}(\rho_t,1-\varepsilon,1+\varepsilon)\hat A_i\right),
$$

并加入 KL 惩罚和熵奖励。论文参数为 (\varepsilon=10^{-3})、(\beta=1.0)、(\gamma=10^{-5})，AdamW 学习率 (10^{-5})，分两个 inner batch 更新；仓库默认和实验 overlay 与这些核心数值一致。

代码还会跳过标准差为零的最终 DDIM 步，将每步 loss 除以采样步数，手动反向传播，并把去噪器梯度范数裁剪到 1.0（`src/rl_module/rl_module.py:168-207,228-262`）。

### 9. 一个重要的论文—代码差异

论文把正则项写成当前策略相对“冻结的预训练参考策略” (\pi_{\mathrm{ref}}) 的 KL：

$$
-\beta D_{\mathrm{KL}}(\pi_\theta\Vert\pi_{\mathrm{ref}})+\gamma H(\pi_\theta).
$$

但 `v0.0.1` 的 `calculate_loss` 没有在该路径中单独运行一个冻结参考模型。它使用 rollout 保存的 `old_log_probs` 与当前重算的 `current_log_probs`，构造 k3 形式

$$
e^{\ell_{\mathrm{old}}-\ell_\theta}-1-(\ell_{\mathrm{old}}-\ell_\theta).
$$

因此：

- clipped importance ratio 与 GRPO 组优势是直接匹配的；
- 熵项是直接匹配的；
- “KL 约束到预训练参考策略”只能判为 **Partial**，代码实际约束更接近当前策略相对行为/旧策略的变化。

另一个较小差异是归一化。论文概括为各奖励都 min-max 到 `[0,1]`；代码中创造性不归一化，能量和两个多样性分量做 min-max，求和后再按组标准化。

### 10. 实验设计与结果

#### 10.1 从头生成

每个模型生成 10,000 个未做几何优化的晶体，只以原子数为条件。对比方法包括 MatterGen、DiffCSP、去掉文本编码器的 Chemeleon1、ADiT 和预训练 Chemeleon2。指标包括：

- uniqueness：生成集合内部不重复比例；
- novelty：相对参考数据库无匹配比例；
- compositional validity：SMACT 电荷中性和电负性兼容；
- metastability：(E_{\mathrm{hull}}<0.1\) eV/atom；
- mSUN：同时 metastable、unique、novel；
- (\mathrm{FMD}^{-1}=1/(1+\mathrm{FMD}))：潜空间覆盖度。

Alex-MP-20 上，RL 将 Chemeleon2：

- mSUN 从 15.9% 提升到 61.3%；
- novelty 从 62.3% 提升到 97.5%；
- metastability 从 51.2% 提升到 72.1%；
- uniqueness 从 99.4% 降到 88.7%。

这说明联合目标显著改善，但仍存在轻微模式坍塌。MP-20 上 mSUN 从 7.6% 提升到 26.0%，接近 MatterGen 的 24.5%，novelty 达 96.5%。

#### 10.2 3 eV 带隙引导

作者用 Alex-MP-20 的 43,295 个带隙标签训练预测器，把目标设为分布外的 3 eV，并对每种方法生成 512 个样本。与 CFG 和 CFG+LoRA 相比，Chemeleon2-RL 的 DFT 带隙分布更集中在目标附近，同时保持 45.3% mSUN；512 个样本中有 82 个落在 2.7–3.3 eV。论文还报告 DFT 松弛后 mSUN 为 60.8%、metastability 为 85.5%。这些是论文报告值，本分析没有重新运行 DFT。

### 11. 如何理解这项方法？

这项工作的本质不是让奖励函数“可微”，而是让它们**可快速验证、可比较，并能给同组候选排序**。AMD、凸包能量和 MMD 都不通过生成模型反向传播；梯度来自

$$
\nabla_\theta\log p_\theta(\mathbf{z}_{t-1}\mid\mathbf{z}_t,\mathbf{x})\times\hat A_i.
$$

潜空间解决的是策略概率和 rollout 成本问题，GRPO 解决的是无 critic 的相对信用分配问题，多目标奖励解决的是“新颖但不稳定”与“稳定但不新颖”的搜索偏向问题。三者必须同时存在：论文的无多样性奖励消融显示，只有创造性和稳定性仍可能让策略钻入局部捷径。

### 12. 局限与复现边界

- MLFF 凸包能量是 0 K 代理，对磁性、强关联或竞争相稀疏的多元体系可能不可靠。
- 模型生成有序周期晶体，不能区分无序固溶体和位点占据无序。
- 现有结构新颖性指标难以识别低对称原型、细微晶格畸变和真正的新结构母型。
- 提高多样性权重可能诱导“reward hacking”，偏向元素数很多的复杂组成。
- DFT 稳定或带隙合适不等于实验可合成；论文没有给出实验合成验证。
- 官方论文明确对应代码 tag `v0.0.1`；本地 tag 解析为 commit `acc0a6642dab3a6b362ad61df571f8fe0c7c0661`。代码包含核心模型、奖励、配置和 benchmark 样本，但未找到完整 VASP/Atomate2/Jobflow 流程、全部主图重绘脚本以及明确的 500-step reward-plateau early stopping 配置。
- 本次分析只做了论文、六张主图和源码的静态核验，没有安装依赖、下载模型或重新训练/评估。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Guiding Generative Models for Crystal Discovery with Reinforcement Learning

### Problem

Likelihood-trained crystal generators reproduce statistically common regions of their training data, but materials discovery seeks the opposite: underexplored compositions and structures that are novel without becoming thermodynamically implausible. Earlier crystal diffusion/RL approaches operate directly on the heterogeneous crystal representation—discrete atom types plus coupled continuous coordinates and lattice—which makes transition probabilities and rollout-intensive policy optimization difficult. Representative baselines include DiffCSP (*NeurIPS*, 2023), MatterGen (*Nature*, 2025), and Chemeleon1 (*Nature Communications*, 2025); latent ADiT (ICML, 2025) is cheaper to sample, but compression can blur geometry and underrepresent rare structures.

### Proposed Method

Park and Walsh introduce Chemeleon2-RL, published in *Nature Machine Intelligence* (2026). A pretrained VAE maps a crystal (C=(A,X,L)) into continuous atom-level latents; a diffusion transformer denoises these latents and acts as the policy; the frozen VAE decodes the terminal latent back to a crystal. Group-relative policy optimization (GRPO) samples 64 trajectories for each condition, standardizes their terminal rewards within the group instead of learning a critic, and applies a clipped policy-gradient update across all reverse-diffusion transitions.

The terminal reward combines four verifiable objectives:

- creativity: uniqueness and novelty, with a same-formula AMD-distance fallback for mixed cases;
- stability: negative clipped MLFF-predicted energy above the convex hull;
- structural diversity: leave-one-out marginal contribution to negative MMD in VAE structure space;
- compositional diversity: the analogous marginal MMD reward in atom-type embedding space.

This makes the exploration–validity trade-off adjustable through reward weights and permits other objectives, demonstrated with 3 eV bandgap targeting.

### Evaluation and Main Results

For de novo generation, the authors sample 10,000 as-generated structures per model, conditioned only on unit-cell atom count. Baselines include MatterGen, DiffCSP, Chemeleon1 without its text encoder, latent ADiT, and pretrained Chemeleon2. Metrics cover uniqueness, novelty, SMACT compositional validity, metastability ((E_\mathrm{hull}<0.1\) eV atom\(^{-1}\)), their joint mSUN fraction, and inverse Fréchet materials distance for coverage.

On Alex-MP-20, RL raises Chemeleon2 mSUN from 15.9% to 61.3%, novelty from 62.3% to 97.5%, and metastability from 51.2% to 72.1%. It exceeds the strongest baseline mSUN reported in the comparison (MatterGen, 41.0%), while uniqueness decreases from 99.4% to 88.7%, revealing residual mode collapse. On MP-20, mSUN rises from 7.6% to 26.0%, comparable to MatterGen's 24.5%, with 96.5% novelty. Figure 4 places both RL variants beyond their pretrained counterparts on the novelty–stability plane.

For property guidance, models target a deliberately out-of-distribution 3 eV bandgap using 43,295 Alex-MP-20 labels and 512 samples per method. DFT-evaluated Chemeleon2-RL concentrates near the target and retains 45.3% mSUN; CFG collapses to near zero and CFG+LoRA remains below 3%. Eighty-two RL samples lie within 2.7–3.3 eV. After DFT relaxation, the paper reports 60.8% mSUN and 85.5% metastability.

### What the Figures Add

The primary images form a consistent evidence chain: Figure 1 defines latent-policy and reward geometry; Figure 2 shows lower GRPO advantage variance and failure without diversity reward; Figure 3 demonstrates joint benchmark gains rather than a single-metric win; Figure 4 shows a shifted novelty–stability frontier; Figure 5 reveals a redistribution toward transition-metal chemistry; and Figure 6 shows transferable property control. The figures also expose trade-offs: reduced uniqueness, clustered RL sampling, and chemistry shifts that require physical interpretation rather than equating reward with synthesizability.

### Reproducibility and Limitations

**Reproducibility assessment: 4/5 for algorithm inspection, lower for full paper reproduction.** The paper explicitly releases Chemeleon2 `v0.0.1`; the local official snapshot resolves to commit `acc0a6642dab3a6b362ad61df571f8fe0c7c0661`. It includes VAE/LDM/RL modules, all four reward components, Hydra experiment configs matching the main GRPO hyperparameters, tests, checkpoint resolution, and 10,000-sample benchmark outputs. The paper also links source data and public Weights & Biases logs.

Direct source reading gives **medium code–paper fidelity**. Most core mechanisms match exactly, but the checked loss computes a k3-style penalty between stored rollout and re-evaluated current transition probabilities; it does not separately evaluate the frozen pretrained reference policy described by the paper's KL term. Component normalization also differs from the blanket paper wording: creativity is unnormalized, energy/diversity are min-max normalized, and the summed reward is standardized. The repository was not executed here, and the full VASP/Atomate2/Jobflow validation workflow, all figure-regeneration scripts, and the explicit 500-step reward-plateau early-stopping setting were not found.

Scientific limitations remain substantial. MLFF hull energy is a 0 K proxy and can be unreliable for magnetic/highly correlated or sparsely charted multicomponent systems. The generator represents ordered periodic crystals and does not model disordered solid solutions or site occupancy. Structural novelty metrics can miss prototype equivalence and subtle distortions, increased diversity weights can reward-hack toward complex multinary compositions, and generated/DFT-stable candidates are not experimentally demonstrated synthesizable materials.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
