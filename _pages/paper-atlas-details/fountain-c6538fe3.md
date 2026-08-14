---
layout: default
permalink: /paper-atlas/fountain-c6538fe3/
title: "Fountain"
nav: false
wide: true
description: "单细胞 ATAC-seq（scATAC-seq）记录每个细胞在大量染色质区域上的可及性。数据通常具有三个特点：维度极高、矩阵极稀疏、不同实验批次之间存在明显技术偏差。整合算法需要同时做到： 让同一细胞类型在不同批次中对齐； 不把真实存在的细胞类型差异或批次特有细胞群抹掉； 最好不仅修正低维嵌入，还能得到原始 peak 空间中的校正矩阵。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>Fountain</h1>
    <p>Rigorous integration of single-cell ATAC-seq data using regularized barycentric mapping</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/BioX-NKU/Fountain" target="_blank" rel="noopener noreferrer" aria-label="Open code for Fountain">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Fountain 方法详解：用正则化重心映射整合 scATAC-seq 数据

### 1. 论文要解决什么问题？

单细胞 ATAC-seq（scATAC-seq）记录每个细胞在大量染色质区域上的可及性。数据通常具有三个特点：维度极高、矩阵极稀疏、不同实验批次之间存在明显技术偏差。整合算法需要同时做到：

1. 让同一细胞类型在不同批次中对齐；
2. 不把真实存在的细胞类型差异或批次特有细胞群抹掉；
3. 最好不仅修正低维嵌入，还能得到原始 peak 空间中的校正矩阵。

论文指出，Harmony（*Nature Methods*, 2019）等从 scRNA-seq 迁移来的方法没有直接建模 scATAC-seq 的极端稀疏性；Signac（*Nature Methods*, 2021）、PeakVI（*Cell Reports Methods*, 2022）和 scBasset（*Nature Methods*, 2022）等方法也可能只输出低维表示，或者需要在批次混合与生物结构保留之间权衡。经典重心映射在批次大小或细胞组成不平衡时还可能发生过度校正。

Fountain 的核心思想是：先用 VAE 得到可去噪的低维表示，再用非平衡最优传输寻找跨批次对应关系，用局部图结构约束重心映射，最后把映射结果作为训练编码器的目标。训练后既可以输出整合嵌入，也可以通过解码器生成增强后的原始维度可及性矩阵。

### 2. 输入、输出与符号

设共有 $B$ 个批次、$p$ 个 peaks。第 $b$ 个批次的数据为

$$
X^{(b)}\in\mathbb R^{n_b\times p}.
$$

| 符号 | 含义 | 形状 |
|---|---|---|
| $X^{(b)}$ | 第 $b$ 个批次的细胞-peak 矩阵 | $n_b\times p$ |
| $z_i,\mu_i,v_i$ | VAE 的采样隐变量、均值和方差 | $d$ 维向量 |
| $Z^{(0)}$ | 参考批次的小批量隐表示 | $n_0'\times d$ |
| $Z^{(b)}$ | 待校正批次的小批量隐表示 | $n_b'\times d$ |
| $T^{(b)}$ | 参考批次与批次 $b$ 的 UOT 传输矩阵 | $n_0'\times n_b'$ |
| $L^{(b)}$ | 批次 $b$ 的局部图拉普拉斯矩阵 | $n_b'\times n_b'$ |
| $\bar Z^{(b)}$ | 正则化重心映射得到的目标 | $n_b'\times d$ |

最终输出有两种：

- 低维整合嵌入：所有细胞的后验均值 $\mu\in\mathbb R^{n\times d}$；
- 原始维度增强矩阵：二值稀疏矩阵 $\tilde X\in\{0,1\}^{n\times p}$。

仓库教程先对输入进行二值化，并过滤只在极少数细胞中出现的 peaks。细胞类型标签只用于评估，不参与训练。

### 3. 整体计算流程

```text
AnnData 可及性矩阵 + batch 标签
             |
             +--> 将细胞数最多的批次设为参考批次 0
             |
             +--> 随机小批量 (x, domain_id, row_index)
                              |
                              v
                         VAE 编码器
                              |
                +-------------+----------------+
                |                              |
          第一阶段：预热                  第二阶段：批次映射
          重构损失 + KL          参考批次 Z^(0) 与 Z^(b)
                                               |
                                      非平衡最优传输 T^(b)
                                               + 局部图 L^(b)
                                               |
                                   正则化重心目标 Zbar^(b)
                                               |
                              MSE(Z^(b), stopgrad(Zbar^(b)))
                |                              |
                +--------------+---------------+
                               v
             解码器输入 [z ; one-hot(batch)]
                               |
                 +-------------+-------------+
                 |                           |
             输出后验均值                 用参考批次 token 解码
             作为整合嵌入                 期望计数阈值化并补回原矩阵
                                             |
                                    原始 peak 空间增强矩阵
```

### 4. 第一步：选择参考批次

补充材料 Note S11 的出发点是：小批量最优传输依赖抽样稳定性，细胞数更多的批次通常更适合作为参考。代码并不是按用户输入顺序选择参考，而是把细胞数最多的 batch 移到 domain 0（`Fountain/data.py:70-87`）。随后，训练只对 $b>0$ 的批次计算到 domain 0 的映射。

这一点非常重要：Fountain 的对齐方向不是完全对称的。参考批次的选择会影响映射，但补充实验显示大批次通常比较稳健，最小批次作为参考时表现最差。

### 5. 第二步：VAE 学习低维流形

编码器为每个细胞产生均值和方差，并使用重参数化采样：

$$
v_i=\exp(f_v(h_i))+10^{-6},
\qquad
z_i=\mu_i+\sqrt{v_i}\epsilon_i,
\quad \epsilon_i\sim\mathcal N(0,I).
$$

对应实现位于 `Fountain/layer.py:174-201`。补充材料 Note S14 将 VAE 解释为去噪投影器：重构项迫使隐变量保留可解释的细胞差异，KL 项则让隐空间连续、平滑并接近标准正态先验。

代码默认使用负多项式（negative multinomial, NM）重构损失，并学习一个非负参数 $r$。KL 项为

$$
\mathcal L_{\mathrm{KL}}
=-\frac12\mathbb E_i\sum_k
\left[1+\log(v_{ik}+10^{-6})-\mu_{ik}^2-v_{ik}\right].
$$

对应代码为 `Fountain/loss.py:11-35`。补充材料 Note S15 报告：相对于 Bernoulli 重构，NM 在 MB、BMMC 和 HL 数据集上得到更好的聚类和过度校正表现，同时批次去除能力相近。

### 6. 第三步：非平衡最优传输

普通最优传输通常要求两侧质量严格匹配，但不同批次的细胞数量和细胞类型比例可能不同。Fountain 使用非平衡最优传输，使边缘分布可以通过 KL 惩罚软约束，而不是强制完全相等。

补充材料 Note S13 给出的目标为

$$
T^*=\arg\min_{T\ge0}
\sum_{i,j}C_{ij}T_{ij}-\epsilon H(T)
+\lambda_{\mathrm{OT}}
\left[
\mathrm{KL}\!\left(T\mathbf1\middle\|\frac1{n_x}\mathbf1\right)
+\mathrm{KL}\!\left(T^\top\mathbf1\middle\|\frac1{n_y}\mathbf1\right)
\right].
$$

其中 $C_{ij}$ 是参考细胞和目标细胞在隐空间中的平方距离，$H(T)$ 是熵项。补充材料设定内循环 2 次、外循环 50 次。代码 `unbalanced_ot_z` 使用一致的默认次数，并以

$$
s=\frac{\lambda_{\mathrm{OT}}}{\lambda_{\mathrm{OT}}+\epsilon}
$$

控制非平衡更新（`Fountain/loss.py:80-128`）。传输矩阵在返回前会被 `detach`；若出现 NaN，该批次本轮映射会被跳过。

### 7. 第四步：用局部几何正则化重心映射

经典重心映射本质上用传输矩阵对参考细胞隐表示做加权平均。如果批次严重不平衡，单纯追求跨批次对应可能把不同细胞类型错误地拉到一起。

Fountain 先在待校正批次内部构建 $k$ 近邻图，将距离转成热核权重，并得到图拉普拉斯矩阵

$$
L^{(b)}=D^{(b)}-W^{(b)}.
$$

直接代码位于 `Fountain/loss.py:132-144`。设传入 `Transform` 的矩阵 $T$ 已转置为“目标细胞乘参考细胞”，且 $a=T\mathbf1$，代码通过下面的线性系统计算正则化重心目标：

$$
\left(\lambda_L L^{(b)}+2\operatorname{diag}(a)\right)\bar Z^{(b)}
=2TZ^{(0)}.
$$

默认 `mean` 模式使用

$$
\lambda_L=
\frac{2\lambda_e}
{\operatorname{mean}\left(\operatorname{diag}(L^{(b)})\oslash a\right)}.
$$

该公式是对 `Fountain/loss.py:148-164` 的直接代码描述。它不能被声称为论文主文 Eq. (7) 的逐字复现，因为本地 `paper.md` 缺少主文 Methods 和 Eq. (7)。

当 $\lambda_L=0$ 时，解退化为经典重心映射

$$
\bar Z^{(b)}=\operatorname{diag}(a)^{-1}TZ^{(0)}.
$$

加入 $L^{(b)}$ 后，相邻目标细胞的映射结果受到平滑约束，从而减少把局部生物结构拉散或错误混合的风险。Figure 3 和补充材料 Note S4 的消融实验支持这一设计，特别是在批次大小或共享细胞类型数量不平衡时。

### 8. 第五步：两阶段训练

代码把训练分为两个阶段：

1. `0 -> mid_iteration`：只训练 NM 重构与 KL，让 VAE 先形成可用的隐空间；
2. `mid_iteration -> max_iteration`：加入 UOT 与正则化重心目标，并逐步增大映射 MSE 权重。

代码层面的总损失是

$$
\mathcal L=
\lambda_{\mathrm{recon}}\mathcal L_{\mathrm{NM}}
+\lambda_{\mathrm{KL}}\mathcal L_{\mathrm{KL}}
+\lambda_{\mathrm{ramp}}\mathcal L_{\mathrm{map}},
$$

其中

$$
\mathcal L_{\mathrm{map}}
=\sum_{b>0}\left\|Z^{(b)}-\bar Z^{(b)}\right\|_F^2.
$$

默认参数包括 `lambda_recon=1`、`lambda_kl=0.5`、`lambda_mse=0.005`、`lambda_Eigenvalue=0.5`、`reg=0.1`、`reg_m=5`、`mid_iteration=3000` 和 `max_iteration=30000`（`Fountain/fountain.py:92-143`）。

一个容易忽略的实现细节是：参考隐变量、传输矩阵、图拉普拉斯矩阵和重心目标都被停止梯度。因此 UOT 和矩阵求逆不是端到端可微模块；它们更像每一步重新计算的“教师目标”，MSE 只推动当前批次编码器产生的 $Z^{(b)}$ 靠近该目标。

### 9. 两类输出如何产生？

#### 9.1 低维整合嵌入

`get_latent` 输出 VAE 后验均值 $\mu$，而不是随机采样的 $z$（`Fountain/fountain.py:54-63`）。编码器本身不接收 batch token，因此训练好的编码器可以直接应用到包含新批次的数据。`Tutorials/Online integration.ipynb` 展示了“不重新训练，直接编码新旧细胞”的流程；但仓库没有独立的在线更新 API 或自动化测试。

#### 9.2 原始维度增强矩阵

训练解码器时，输入为

$$
[z_i;\operatorname{onehot}(b_i)].
$$

生成增强矩阵时，代码统一使用参考批次 token 0 解码，计算 NM 期望计数，将大于 1 的位置设为可及，并与原始二值矩阵取并集（`Fountain/fountain.py:67-89`）。因此输出不是连续概率矩阵，而是保留原观测并补充高置信缺失 peaks 的二值 CSR 矩阵。

这解释了 Fountain 与只修正低维坐标的方法的差别：它试图把“批次校正”传递回可用于差异可及性、组织富集、遗传力和 motif 分析的原始特征空间。

### 10. 实验如何验证？

论文使用 MB、BMMC、HI、HL、MM、PBMCA 和 PBMCB 七个真实数据集。数据规模从 13,671 到 136,463 个细胞，最高有 1,050,819 个 peaks，稀疏度最高为 99.62%；HL 含 11 个批次。另有一个 720,613 细胞的人胎儿图谱用于效率测试。

对比方法包括 PeakVI、SCALEX、BAVARIA、Harmony、Signac 和 scBasset。评估指标包括：

- AMI、ARI、NMI：细胞类型聚类保留；
- GC：生物邻接图连接性；
- iLISI：批次混合；
- OC：过度校正。

Supplementary Table S2 中的代表结果包括：

- MB：AMI 0.764、ARI 0.723、iLISI 1.742、OC 0.193；
- BMMC：AMI 0.721、ARI 0.686；
- HL：AMI 0.694、iLISI 4.977、OC 0.236；
- 在线整合：AMI 0.620、ARI 0.500、iLISI 4.605、OC 0.263。

Fountain 并非每个单项指标都第一，但在聚类、混合和防止过度校正之间取得了较稳定的整体平衡。补充材料 Note S3 报告：对每个对比方法进行单侧 Wilcoxon 配对检验，在两种失败任务处理方式下均得到 $P\le0.05$。需要注意，BAVARIA 在 BMMC 和 HL 上 72 小时内未完成，并在 PBMCB 上报错；scBasset 在 MM 和 PBMCA 的预处理阶段失败。

Figure 3 验证不平衡条件和正则化消融；Figure 4 展示原始空间增强及疾病相关遗传力信号；Figure 5 展示组织富集和 motif 偏差信号。后两类结果说明增强矩阵有下游分析价值，但属于关联证据，不能直接解释为因果调控关系。

### 11. 如何理解 Fountain 的关键创新？

可以把 Fountain 看成三个层次：

1. **VAE 负责表示学习。** 它把极稀疏的高维可及性矩阵投影到更稳定的隐空间。
2. **UOT 负责跨批次对应。** 它允许批次质量和细胞组成不完全匹配，比严格平衡 OT 更适合真实单细胞数据。
3. **图正则化重心目标负责防止过度校正。** 它不只要求目标细胞接近参考批次，还要求目标批次内部的局部几何关系不要被轻易破坏。

真正更新神经网络的不是传输矩阵本身，而是“当前隐表示与停止梯度的正则化重心目标之间的 MSE”。这是理解代码的关键。

### 12. 证据边界与未解决问题

- **论文明确主张：** Fountain 通过正则化重心映射同时实现批次校正和生物异质性保留，支持在线嵌入与原始维度增强（`paper.md:12`，Figures 1-5）。
- **代码已验证：** 最大批次参考规则、VAE/NM/KL、UOT 更新、图拉普拉斯、线性系统重心目标、两阶段训练、后验均值输出和增强阈值逻辑。
- **本文解释：** 将停止梯度的映射结果视为动态教师目标，是对代码训练机制的解释，不是论文原文表述。
- **Not found：** 本地主文 Methods、Eq. (7)、完整超参数选择规则、统一 benchmark/制图脚本、随机种子策略、自动化测试、保存的训练结果与数值收敛验证。
- **补充材料状态：** 42 页 PDF 的文字层可直接读取，但没有 `SUPP_MD`；本次没有运行 OCR。
- **代码-论文一致性：** 中等。核心机制有直接实现，主文公式级一致性和完整实验复现仍无法确认。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Fountain: Rigorous Integration of scATAC-seq Data

### Overview

Fountain is a deep-learning framework for integrating sparse single-cell ATAC-seq batches with regularized barycentric mapping. It was published in *Nature Machine Intelligence* in 2025 (DOI `10.1038/s42256-025-01099-3`). The method aims to remove batch effects without erasing biological heterogeneity and, unlike embedding-only correction, can also generate a corrected binary accessibility matrix in the original peak space.

### Why another integration method?

The paper identifies two central problems. First, scRNA-seq integration tools such as Harmony (*Nature Methods*, 2019) do not directly model the extreme sparsity and distributional characteristics of scATAC-seq. Second, scATAC-seq methods such as Signac (*Nature Methods*, 2021), PeakVI (*Cell Reports Methods*, 2022), and scBasset (*Nature Methods*, 2022) may focus on low-dimensional representations or trade batch mixing against biological conservation. Classical barycentric mapping can additionally over-correct when batch sizes or cell-type compositions are imbalanced.

### Method in brief

Fountain first trains a negative-multinomial VAE on binarized, peak-filtered accessibility data. The largest batch is assigned as the reference. After a warm-up stage, mini-batch unbalanced optimal transport couples each other batch to the reference in latent space. A k-nearest-neighbor graph Laplacian regularizes the barycentric target so that latent cells align to the reference while retaining local geometry. Training uses reconstruction, KL, and a gradually introduced mapping MSE loss.

The trained encoder returns posterior means as the integrated embedding. A batch-conditioned decoder can also decode with the reference-domain token, convert negative-multinomial probabilities to expected counts, threshold them, and combine the result with observed accessibility to produce an enhanced original-space matrix. The paper further proposes applying the frozen encoder to new cells for online integration without retraining.

### Evaluation and main evidence

The study evaluates seven real-world integration datasets: MB, BMMC, HI, HL, MM, PBMCA, and PBMCB. They range from 13,671 to 136,463 cells, 21,017 to 1,050,819 peaks, and up to 99.62% sparsity; HL contains 11 batches. A separate Human Fetal Atlas with 720,613 cells and 1,050,819 peaks is used for efficiency testing.

Comparisons include PeakVI, SCALEX, BAVARIA, Harmony, Signac, and scBasset. Metrics cover cell-type clustering (AMI, ARI, NMI), biological graph conservation (GC), batch mixing (iLISI), and over-correction (OC). Fountain is not the best method on every individual metric, but it provides the strongest overall balance across datasets. Examples from Supplementary Table S2 include:

- MB: AMI 0.764, ARI 0.723, iLISI 1.742, OC 0.193.
- BMMC: AMI 0.721 and ARI 0.686, both highest among completed runs.
- HL: AMI 0.694, iLISI 4.977, and OC 0.236.
- Online integration: AMI 0.620, ARI 0.500, iLISI 4.605, and OC 0.263.

Supplementary Note S3 reports one-sided Wilcoxon signed-rank tests with $P\le 0.05$ against every tested comparator under both zero-imputation and pairwise-omission handling of failed runs. Some baselines did fail: BAVARIA did not finish within 72 hours on BMMC and HL and errored on PBMCB, while scBasset preprocessing failed on MM and PBMCA. On the 720,000-cell efficiency benchmark, Supplementary Table S3 reports 36 minutes for Fountain, compared with 48 for Harmony, 106 for SCALEX, 236 for PeakVI, and 875 for scBasset; hardware and full run configuration are not available in local Markdown.

Figures 3-5 add three kinds of evidence: robustness under batch-size and shared-cell-type imbalance; ablations supporting adaptive geometric regularization; and stronger tissue-expression, heritability, pathway, and motif signals in enhanced profiles. These downstream enrichments are associations and do not by themselves establish causal regulation.

### Reproducibility assessment: 3/5

**Available:** the paper names public datasets, provides GitHub and Zenodo code, and the analyzed repository snapshot includes core Python modules plus tutorials for batch correction, enhancement, online integration, downstream analysis, and an scRNA-seq example. Direct source inspection finds a coherent implementation of the VAE, UOT solver, graph Laplacian, regularized linear-system target, two-stage training, latent export, and enhancement routine. Overall code-paper fidelity is **medium**.

**Limitations:** the acquired `paper.md` lacks the main Methods/results body and Eq. (7); the supplementary PDF has a readable text layer but no `SUPP_MD`. The repository has no automated tests, deterministic seed policy, stored checkpoints/results, or single script/configuration that recreates every baseline, significance test, and figure. Tutorials cover the main user workflow, but the large `requirements.txt` is an environment dump with build-path-pinned packages rather than a minimal portable specification. No training run was executed in this analysis.

### Bottom line

Fountain's main contribution is not simply another latent batch correction model. It uses UOT to define cross-batch correspondences, local geometry to regularize barycentric targets under imbalance, and a decoder to carry correction back into the original accessibility space. The public source substantially supports this mechanism, while exact equation-level fidelity and full paper-wide reproducibility remain only partially verifiable from the locally available evidence.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
