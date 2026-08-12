---
layout: default
permalink: /paper-atlas/calicost-8acbcc5f/
title: "CalicoST"
nav: false
description: "CalicoST 把空间转录组中的两类信号——表达量反映的总拷贝数变化（RDR）和杂合 SNP 反映的等位基因失衡（BAF）——放进同一个“基因组 HMM + 空间 HMRF”模型中，从而同时推断等位基因特异性 CNA、空间肿瘤克隆、肿瘤比例以及肿瘤系统地理史。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Methods · 2024</span>
    </div>
    <h1>CalicoST</h1>
    <p>Inferring allele-specific copy number aberrations and tumor phylogeography from spatially resolved transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CalicoST 方法详解

### 一句话理解

CalicoST 把空间转录组中的两类信号——表达量反映的总拷贝数变化（RDR）和杂合 SNP 反映的等位基因失衡（BAF）——放进同一个“基因组 HMM + 空间 HMRF”模型中，从而同时推断等位基因特异性 CNA、空间肿瘤克隆、肿瘤比例以及肿瘤系统地理史。

### 它要解决什么问题？

空间转录组可以告诉我们“肿瘤细胞在哪里”，但仅靠基因表达推断 CNA 有三个根本困难：

1. 表达受到细胞状态、微环境和技术噪声影响，不等同于 DNA 拷贝数。
2. 只看总表达无法区分 A、B 两条亲本等位基因，因此看不到拷贝数中性 LOH（CNLOH）和镜像亚克隆 CNA。
3. Visium 一个 spot 往往混有肿瘤与正常细胞，异常信号会被稀释；多个切片还会带来配准和批次问题。

已有方法各自只覆盖一部分需求。inferCNV 源于 Patel 等发表于 *Science* 2014 年的单细胞转录组分析，主要从表达推断总拷贝数；STARCH（*Physical Biology*, 2021）利用空间转录组推断总拷贝数和克隆，但没有等位基因分辨率；Numbat（*Nature Biotechnology*, 2021）能从单细胞转录组推断等位基因特异性 CNA，却不是为多细胞 spot 和显式空间连续性设计的。CalicoST 的目标是把这些缺口一次性连接起来（`paper.md:18-30`, `paper.md:91-108`, `paper.md:361-363`）。

### 关键创新

- 用群体参考单倍型加空间样本伪 bulk BAF，纠正远距离 phasing switch error。
- 联合建模表达计数与等位基因计数，而不是把 BAF 仅作为事后验证。
- 用 HMM 表示 CNA 沿基因组连续，用 HMRF 表示克隆在空间中连续。
- 显式建模一个 spot 中“一个癌克隆 + 正常细胞”的混合。
- 从 LOH 推断克隆树，再用高斯扩散模型估计祖先克隆的空间位置。
- 可通过 PASTE2 对齐矩阵联合分析相邻切片，也可联合分析没有空间对齐的区域切片。

### 输入与输出

输入包括：

- 每个 spot 的空间坐标 \(S\)；
- 按基因组位置排列的转录本计数 \(X^0\)；
- 杂合 SNP 的某一等位基因计数 \(Y^0\)；
- 两条等位基因总计数 \(D^0\)；
- 可选的肿瘤计数比例 \(\theta\)；
- 可选的多切片配准矩阵 \(W\)。

输出包括每个 spot 的克隆标签、每个克隆的 A/B 等位基因整数拷贝数、肿瘤比例、LOH 克隆树，以及带祖先空间位置的 phylogeography。

```text
Space Ranger / SNP reads / coordinates
                │
                ▼
  SNP 初始相位 + 伪 bulk HMM 纠错
                │
                ▼
   可变长度 bin：X、Y、D 聚合
                │
                ▼
 正常 spot / λ 基线 / ASE 与高变基因过滤
                │
                ▼
  BAF-first 初始化 ── 可选 LOH 肿瘤比例 θ
                │
                ▼
  HMM(Z, μ, p) ⇄ HMRF(克隆标签 ℓ)
                │
                ▼
  整数 A/B CNA → LOH 字符 → Startle 树
                │
                ▼
       高斯投影祖先空间位置
```

### 第 0–1 步：为什么先做 phasing 和 binning？

单个 spot 的 SNP 极其稀疏：论文报告每个 spot 中 98.8% 的 SNP 位点没有计数。CalicoST 先用 Eagle2 给 SNP 初始定相，再把所有 spot 合成伪 bulk，以提高 BAF 覆盖度。对每个 SNP，隐藏状态同时包含 BAF 类别 \(z_g\) 和相位 \(h_g\)。两种相位的 Beta-binomial 发射概率互为镜像：

\[
y_g^0\mid h_g=1,z_g=i\sim\mathrm{BetaBinom}(d_g^0,\tau p_i,\tau(1-p_i)),
\]

\[
y_g^0\mid h_g=2,z_g=i\sim\mathrm{BetaBinom}(d_g^0,\tau(1-p_i),\tau p_i).
\]

HMM 假设附近 SNP 的 CNA 状态和相位通常保持不变，从而定位远距离 switch error。得到统一相位后，方法把连续 SNP 聚合成 bin；bin 长度不是固定的，而是扩展到达到最小等位基因计数。这个设计用空间/基因组分辨率换取统计稳定性（`paper.md:190-226`）。

### 第 2 步：建立正常二倍体表达基线

表达深度必须和正常二倍体基线比较。若已有肿瘤比例，低 \(\theta\) spot 直接作为正常候选；否则先跑 BAF-only 聚类，选择全基因组 BAF 最接近 0.5 的组，再挑表达沿基因组最稳定的 spot。正常基线满足

\[
\lambda_g\propto\sum_{i\in J}x_{g,i},
\]

其中 \(J\) 是可信正常 spot 集合。正常区域 BAF 显著偏离 0.5 的 bin 被视为潜在等位基因特异性表达而删除；正常与肿瘤之间异常高表达且差异过大的基因也会被过滤（补充材料 S7–S8）。

### 第 3 步：HMM 和 HMRF 如何联动？

#### 观测模型

假设 spot \(n\) 属于克隆 \(m\)，bin \(g\) 处于状态 \(k\)。纯克隆情况下：

\[
x_{g,n}\sim\mathrm{NB}(T_n\lambda_g\mu_k,\phi),
\qquad
y_{g,n}\sim\mathrm{BetaBinom}(D_{g,n},\tau p_k,\tau(1-p_k)).
\]

\(\mu_k\) 是潜在 RDR，\(p_k\) 是潜在 BAF。它们分别近似对应总拷贝数和 B 等位基因占比：

\[
\mu_k=\frac{a+b}{\sum_g\lambda_g(a_g+b_g)},
\qquad p_k=\frac{b}{a+b}.
\]

#### 正常细胞混合

CalicoST 假设一个 spot 最多含一个癌克隆，但可与正常细胞混合。论文中的混合模型为

\[
x_{g,n}\sim\mathrm{NB}\{T_n\lambda_g[\theta_n\mu_{g,m}+1-\theta_n],\phi\},
\]

\[
q_{g,n}=\frac{\theta_n\mu_{g,m}p_{g,m}+0.5(1-\theta_n)}
{\theta_n\mu_{g,m}+1-\theta_n}.
\]

BAF 计数再以 \(q_{g,n}\) 为均值进入 Beta-binomial。这里的 \(\theta\) 是“转录本计数比例”，不严格等同于细胞比例（补充材料 S3）。

#### 基因组 HMM

每个克隆沿基因组有一条状态序列 \(Z_{\cdot,m}\)。默认自转移概率 \(t=1-10^{-5}\)，强烈偏好长连续片段，避免高噪声空间转录组产生大量伪断点。Baum-Welch 更新 \(\mu,p\)，forward-backward 给出每个 bin 的状态后验。为了缓解稀疏，属于同一克隆的 spot 被聚合成 pseudobulk 后拟合（补充材料 S4）。

#### 空间 HMRF

spot 的克隆标签使用 Potts 空间先验：

\[
\log P(\ell;S)\propto
\sum_{n,m}\alpha_m\mathbb{1}(\ell_n=m)+
\beta\sum_{n<n'}e_{n,n'}\mathbb{1}(\ell_n=\ell_{n'}).
\]

同一切片内，\(E\) 来自 Visium 六边形邻接或 KNN；切片之间，矩阵块可放入缩放后的 PASTE2 配准概率。迭代条件模式（ICM）更新标签（补充材料 S5–S6）。

#### 交替优化

算法采用 block coordinate ascent：固定克隆标签，用 HMM 更新 CNA 状态和参数；再固定 CNA 模型，用 HMRF 更新空间标签；重新形成 pseudobulk，直到标签稳定。用户给出初始克隆数，模型用基于似然比的 Neyman–Pearson 统计量合并 CNA 轮廓过于相似的克隆，而不是直接使用 AIC/BIC（`paper.md:255-266`，补充材料 S10）。

代码主路径与此一致：

- 输入：`CalicoST/src/calicost/parse_input.py:228-254`
- 总流程：`CalicoST/src/calicost/calicost_main.py:29-391`
- HMM/HMRF 交替：`CalicoST/src/calicost/hmrf.py:402-519`
- NB/Beta-binomial 发射：`CalicoST/src/calicost/hmm_NB_BB_phaseswitch.py:39-148`

### 可选步骤：从 LOH 估计肿瘤比例

若肿瘤发生 B 等位基因丢失，纯正常 BAF 约为 0.5，纯肿瘤 BAF 接近 0。混合 spot 的 BAF \(f\) 满足

\[
f=\frac{0.5(1-\theta)}{\theta\mu+(1-\theta)},
\qquad
\theta=\frac{0.5-f}{0.5+\mu f-f}.
\]

实际 LOH 区域未知，因此先跑 BAF-only 模型，将偏离 0.5 超过默认阈值 0.2 的状态视为 LOH，再跨多个 LOH 区域合并 UMI。实现入口为 `CalicoST/src/calicost/estimate_tumor_proportion.py:19-112`。

### 第 4 步：从连续参数恢复整数拷贝数

RDR/BAF 能约束 A/B 比例，却不能唯一决定绝对倍性：把 A、B 同时乘以同一整数，BAF 不变，归一化 RDR 也可能相近。CalicoST 因此对候选 A/B 和基因组倍性加边界，最小化候选整数状态与 \((\mu_k,p_k)\) 的加权误差；另一个设置把一个平衡二倍体状态固定为 `(1,1)`。当前代码在 `CalicoST/src/calicost/find_integer_copynumber.py:73-235` 用 hill climbing 搜索。

需要注意：当前 GitHub 代码可见的候选边界、倍性限制和附加惩罚与补充材料 S9 的文字并不完全相同。因此“整数化思想”是直接匹配的，但复现论文精确数值应使用论文所引用的 Zenodo 冻结版本。

### 第 5 步：从 LOH 树到空间进化史

CalicoST 选择足够长且有足够 SNP UMI 支持的 LOH，默认至少 3 个 bin、100 个 SNP-covering UMI。LOH 被当作不可逆二元字符，交给 Startle 构建克隆树。随后把叶节点放在对应克隆的空间中心，假设父子节点位移满足

\[
s_v\sim\mathcal{N}(s_{p(v)},w_{v,p(v)}I),
\]

其中边方差与突变/LOH 数量成正比；内部祖先位置由条件高斯期望得到。代码位置：

- LOH/Startle：`CalicoST/src/calicost/phylogeny_startle.py:17-223`
- 空间投影：`CalicoST/src/calicost/phylogeography.py:11-109`

当前 `phylogeography.py` 只保存 x/y 两维，而论文 Figure 4 展示 3D 多切片树；这是当前快照与论文展示之间的一个明确复现缺口。

### 评估与结果

#### 数据集

- HTAN WashU：12 位患者、26 个 Visium 切片，覆盖三种癌症；其中 9 位有足够纯度的匹配 WES 作为等位基因 CNA 参照。
- 两个多切片 3D 病例：HT112C1 两个相邻切片，HT268B1 五个切片。
- 五切片前列腺癌，用于镜像 CNA 和 phylogeography。
- Slide-tags 黑色素瘤单细胞空间数据。
- 90 个 CNA/克隆模拟样本和 135 个基于 WES 的空间/纯度模拟样本。

#### 指标与基线

- CNA：最佳匹配克隆准确率、异常 bin precision/recall、CNLOH F1。
- 克隆：adjusted Rand index（ARI）。
- 空间连续性：joincount z-score。
- 肿瘤比例：病理 tumor/normal 标签 AUC、与 RCTD 的 Pearson 相关。
- 基线：Numbat、STARCH、inferCNV；WES 侧由 HATCHet2 给出参照。

#### 主要结果

- 9 位 WES 可评估患者：最佳匹配克隆平均准确率 86%（68–97%），异常 bin precision 95%、recall 90%。
- 肿瘤比例：病理标签平均 AUC 0.85，与 RCTD 平均 Pearson 0.76。
- 4 个 CNA 丰富的 CRC 转移样本：相对 Numbat 的等位基因状态准确率平均高 25%；相对 STARCH、inferCNV 的总状态准确率平均高 59% 和 90%。
- 9 位 HTAN 患者中，CalicoST 比 Numbat 平均高 23%，且每位患者均更高。
- 远距离双切片分析相对五切片结果 ARI 0.996。
- 90 个模拟中，克隆 ARI 平均 0.87；Numbat 0.34、STARCH 0.50。CNLOH F1 为 0.52，Numbat 为 0.18。

### 如何正确解读输出

最可信的是大尺度等位基因 CNA、LOH、镜像事件和空间连贯的克隆区域。需要更谨慎的是：

- 精确断点和单基因 CNA：SRT 覆盖度通常不够，CalicoST CNA 中位长度为 77.4 Mb。
- 高倍扩增的绝对整数：RDR/BAF 归一化导致不可辨识。
- 祖先的精确空间坐标：它是高斯扩散模型下的估计，不是直接观测。
- 非常弱的空间组织：HMRF 可能过度平滑。
- 多癌克隆混合的单个 spot：当前模型只允许一个癌克隆加正常细胞。

### 复现建议与已知缺口

1. 优先使用论文引用的 Zenodo `10.5281/zenodo.10986535`，而不是默认认为当前 GitHub `main` 与论文完全相同。
2. 保留 Eagle2、1000 Genomes SNP panel、Space Ranger、PASTE2 和 Startle 的版本及参数。
3. 先检查 SNP-covering UMI、正常区域和 LOH 支持度，再解释整数 CNA 或树。
4. 对 3D 结果单独核对冻结版本/绘图代码；当前获取的投影函数只有二维接口。
5. 仓库中没有找到覆盖所有 HTAN 基准和论文图的单一端到端脚本；当前可确认的是方法级复现，而非一键重建全部论文结果。

### 总结

CalicoST 的核心价值不只是“在空间上平滑 CNA”，而是把 phasing、BAF、RDR、正常混合、基因组连续性和空间连续性统一进一个模型。它尤其适合研究 CNLOH、镜像 CNA、低纯度区域和多切片肿瘤扩散；与此同时，它的分辨率、绝对倍性和 phylogeography 仍受 SRT 覆盖度、模型假设与冻结版本可获得性的限制。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## CalicoST: concise paper summary

### Citation

**Inferring allele-specific copy number aberrations and tumor phylogeography from spatially resolved transcriptomics.** *Nature Methods* (2024). DOI: `10.1038/s41592-024-02438-9`.

### One-sentence takeaway

CalicoST jointly models transcript depth, phased allelic imbalance, genomic continuity, and spatial continuity to recover allele-specific tumor copy-number profiles, spatial clones, tumor purity, and LOH-based phylogeography from one or more spatial transcriptomics slices.

### Why the problem matters

Existing transcriptome-based CNA methods often infer only total copy-number states, ignore spatial structure, or assume single-cell measurements. Those choices hide copy-neutral LOH and mirrored allele-specific events, fragment spatial clones, and reduce accuracy in Visium spots containing mixtures of tumor and normal cells. CalicoST targets these gaps using both expression and SNP-covering transcripts (`paper.md:18-30`, `paper.md:39-59`).

### Core method

CalicoST proceeds in six stages:

1. Count alleles at germline heterozygous SNPs and obtain an initial Eagle2 population phase.
2. Correct long-range phase switches with a pseudobulk BAF HMM and aggregate transcript/allele counts into variable-length genomic bins.
3. Identify confident normal spots, estimate diploid expression baselines, and filter allele-specific expression or highly variable genes.
4. Alternate a genomic HMM for latent RDR/BAF copy-number states with a spatial HMRF for clone labels; optionally model tumor-normal admixture and PASTE2 cross-slice alignments.
5. Convert latent states to bounded integer A/B copy pairs.
6. Build an irreversible-LOH clone phylogeny with Startle and infer ancestral locations under a Gaussian diffusion model.

The relaxed objective combines an observation likelihood for expression and allele counts with a Markov prior along the genome and a spatial Potts prior over clone labels (`paper.md:232-266`).

### Main results

- On 12 HTAN patients (26 slices), nine had matched WES-derived allele-specific ground truth of sufficient purity. The best-matching CalicoST clone averaged **86% allele-specific accuracy** (range **68–97%**), with **95% precision** and **90% recall** for abnormal bins (`paper.md:65-68`).
- CalicoST's median detected CNA length was **77.4 Mb**, compared with **30 Mb** for HATCHet2/WES, although high-coverage events as small as **1 Mb** were detected. The method is therefore accurate mainly at broad genomic scales (`paper.md:68-76`).
- BAF-derived tumor proportions achieved mean **AUC 0.85** against histology-derived tumor/normal labels and mean **Pearson correlation 0.76** with RCTD, without requiring matched scRNA-seq (`paper.md:79`).
- On four CNA-rich CRC liver metastases, CalicoST was reported to be **25% more accurate than Numbat** for allele-specific states and **59%/90% more accurate than STARCH/inferCNV** for total-copy states. Across all nine WES-benchmarked patients it was **23% more accurate than Numbat** on average and better in every patient (`paper.md:94-108`).
- In multi-slice tumors, CalicoST recovered concordant clones across nearby and distant slices. For a two-slice subset separated by more than 200 μm, clone assignments had **ARI 0.996** relative to the five-slice analysis; WES agreement was **79.2%** and **68.0%** for the two slices (`paper.md:114-131`).
- In five prostate sections, the method found five clones, a left/right early bifurcation, and four mirrored events on chromosomes 2, 6, and 8. SNV localization supported the major lineage split (`paper.md:137-151`).
- In 90 simulations, the supplement reports mean clone ARI **0.87** versus **0.34** for Numbat and **0.50** for STARCH, and CNLOH F1 **0.52** versus **0.18** for Numbat. In 135 WES-derived simulations, CNA accuracy ranged approximately **76–92%**, while tumor/normal discrimination degraded in the smallest, lowest-purity tumor blocks (Supplement S15).

### What the paper establishes well

- Allele counts materially improve inference over expression-only total-copy methods, especially for CNLOH, mirrored events, and near-triploid genomes.
- Explicit normal admixture enables useful clone/CNA inference in low-purity spatial regions where adjacent bulk WES may fail.
- Coupling the genomic HMM with a spatial HMRF produces clone maps that are both more accurate against WES and more spatially coherent than non-spatial allele-specific inference.
- Joint analysis across slices uses stable BAF patterns to link clones even when expression embeddings are dominated by slice effects.
- The paper validates the method using matched WES, histology, RCTD, simulations, multi-slice consistency, and a small set of orthogonal SNVs.

### Important limitations

- Allele-specific inference requires enough heterozygous SNP-covering UMIs. Pooling can rescue sparse data but reduces spatial resolution; platforms without SNP capture cannot use the central BAF signal.
- Breakpoints are coarse and depend on gene/SNP coverage. Single-gene CNAs are generally not identifiable from these data.
- The tumor-mixture model assumes at most one cancer clone plus normal cells per spot and defines purity as a fraction of transcript counts rather than cells.
- Exact integer copy numbers, especially high-copy amplifications, are not fully identifiable from normalized RDR and BAF.
- LOH-based phylogeny requires enough high-confidence LOH events and cannot fully resolve lineages lacking them.
- Spatial regularization can over-smooth tumors with weak spatial organization; the initial clone count and HMRF weight require judgment.
- Reported runtime is roughly **2–8 hours per sample**, dominated by NB/Beta-binomial fitting (`paper.md:163-176`).

### Code and reproducibility

The acquired repository implements the central method path, including input parsing, phase-aware NB/Beta-binomial emissions, HMM/HMRF alternation, tumor-proportion estimation, integer-copy calling, Startle phylogeny generation, and Gaussian spatial projection. Method-level fidelity is strong, but exact paper-result reproduction is not yet established:

- the inspected GitHub snapshot is commit `c1abcae3e3657e01e547ee4529e3b9d039221453`, while the paper cites Zenodo `10.5281/zenodo.10986535` as the version used;
- the visible mixed-BAF expression and integer-copy constraints differ from the supplementary specification;
- the checked phylogeography function outputs x/y coordinates only, while the paper presents 3D reconstructions;
- a complete paper-wide HTAN benchmarking and figure-generation workflow was not located.

Accordingly, the code match is rated **medium overall**: high confidence for the core algorithmic architecture, moderate confidence for exact frozen-version behavior and publication-level reproduction. See `doc_code.md` for the detailed ledger.

### Bottom line

CalicoST convincingly shows that phased allelic information and spatial modeling can recover biologically meaningful tumor clones and evolutionary events from SRT that total-copy or non-spatial approaches miss. Its strongest use case is broad allele-specific CNA and clone reconstruction across heterogeneous, possibly multi-slice tissue. Users should treat exact integer amplification levels, fine breakpoints, and ancestral spatial coordinates as lower-confidence outputs and should reproduce against the paper's frozen code/data release when exact numerical fidelity matters.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
