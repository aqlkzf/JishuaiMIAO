---
layout: default
permalink: /paper-atlas/patty-e9115f4a/
title: "PATTY"
nav: false
description: "PATTY 要解决的是 CUT&Tag 数据里的 open-chromatin bias：Tn5 更容易在开放染色质区域插入，因此一些本来不该有目标组蛋白修饰的开放区域也会出现 CUT&Tag 信号。PATTY 用同一样本或同类型细胞的 ATAC-seq 作为开放染色质参照，把 CUT&Tag 信号和 ATAC 信号一起输入预训练的、组蛋白标记特异的 logistic regression 模型，输出每个 200 bp genomic…"
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
      <span>scATAC — Single-Cell Chromatin &amp; DNA Methylation</span>
      <span>Nature Communications · 2026</span>
    </div>
    <h1>PATTY</h1>
    <p>PATTY corrects open-chromatin bias for improved bulk and single-cell CUT&amp;Tag profiling</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-73599-8" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PATTY 方法中文解读

### 一句话概括

PATTY 要解决的是 CUT&Tag 数据里的 open-chromatin bias：Tn5 更容易在开放染色质区域插入，因此一些本来不该有目标组蛋白修饰的开放区域也会出现 CUT&Tag 信号。PATTY 用同一样本或同类型细胞的 ATAC-seq 作为开放染色质参照，把 CUT&Tag 信号和 ATAC 信号一起输入预训练的、组蛋白标记特异的 logistic regression 模型，输出每个 200 bp genomic bin 的 bias-corrected score（`paper source:30-40`, `paper source:58-66`, `paper source:190-192`）。

### 为什么需要这个方法？

CUT&Tag 的实验目标是检测抗体靶向的 histone modification 或 TF binding，但 Tn5 的开放染色质偏好会把“开放”误读成“目标标记存在”。论文中特别强调这不是 SELMA 等 sequence-bias 方法主要处理的 intrinsic cleavage bias，而是由 chromatin accessibility/context 引起的偏差；传统 peak calling 工具也不是为这种 Tn5 open-chromatin bias 设计的（`paper source:38-40`）。

这个问题在 single-cell CUT&Tag 中更严重，因为每个细胞的 reads 更稀疏，开放区域的假信号会更容易影响矩阵结构和聚类结果（`paper source:30-40`, `paper source:198-206`）。

### 论文里的训练思路

论文先构建 true / false histone-mark regions，再比较模型和特征组合。

#### 1. 构造 true / false 区域

以 H3K27me3 为例：

- true H3K27me3：在不表达基因附近或 gene body 上，重复出现的 H3K27me3 CUT&Tag peak-covered 200 bp bins，并且没有 H3K27ac CUT&Tag reads。
- false H3K27me3：在高表达基因附近或 gene body 上，出现 H3K27me3 CUT&Tag signal，同时与 H3K27ac CUT&Tag peaks 重叠。
- 论文在 K562 中得到 1,428 个 true H3K27me3 200 bp regions 和 1,231 个 false H3K27me3 200 bp regions（`paper source:50-54`, `paper source:142-158`）。

Figure 2 的真实图像支持这个设计：true schematic 对应 silent gene，false schematic 对应 active gene、H3K27ac 和 mRNA；ATAC signal 分布图中 false H3K27me3 regions 的 ATAC signal 明显更高（`figure_analysis.md`）。

#### 2. 构造候选特征

对每个 200 bp candidate region，论文考虑这些特征：

| 特征 | 含义 | 论文证据 |
|---|---|---|
| CUT&Tag signal pattern | 目标组蛋白标记的局部信号 | `paper source:58-58`, `paper source:162-166` |
| ATAC-seq signal pattern | 开放染色质参照，用来建模 open-chromatin bias | `paper source:58-64`, `paper source:162-166` |
| IgG signal pattern | negative control | `paper source:58-58`, `paper source:162-166` |
| one-hot DNA sequence | 200 bp bin 的序列偏好信息 | `paper source:58-58`, `paper source:162-166` |

论文描述的 signal pattern 是以 200 bp bin 为中心的 1 kb 窗口，10 bp resolution 的 normalized pile-up count（`paper source:58-58`, `paper source:162-166`）。

#### 3. 比较模型

论文比较了 penalized logistic regression、random forest、GBM、CNN、MLP、RNN、GRU，并用 5-fold cross-validation 和 genome-wide biology-informed metrics 评估（`paper source:60-64`, `paper source:162-176`）。结果上，LR 模型加 CUT&Tag + ATAC 两类特征，在 H3K27me3 上给出更符合生物预期的负相关：corrected H3K27me3 score 与 gene expression、H3K27ac signal 的相关性更负（`paper source:62-66`）。

**重要边界：**这些训练和模型比较代码在本 workspace 的 `code source` 里是 `Not found`。已搜索 `PATTY/bin/PATTY`, `PATTY/lib/*.py`, `PATTY/setup.py`, `PATTY/README.md`，没有找到 RF/GBM/dNN 定义、TensorFlow/Keras 训练、cross-validation、IgG 分支、sequence 分支或训练数据构建脚本。当前包主要是 inference package。

### 已发布 package 实际做了什么？

代码实现的是预训练 LR 模型的推断流程。

```text
bulk CUT&Tag BED + ATAC BED + genome bins + factor
        |
        v
检查输入和选择 refdata/<factor>_LR_CnTATAC_model.joblib
        |
        v
对每个 200 bp bin 构造 1 kb CUT&Tag + ATAC 特征
        |
        v
LR predict_proba -> corrected score
        |
        v
bulk: bedGraph/bigWig
sc: bin x cell matrix
```

CLI 要求 `mode`, `cuttag`, `atac`, `factor`, `genome`, `genomebin`, `outname`，其中 `factor` 只能是 H3K27me3、H3K27ac、H3K9me3（`PATTY/bin/PATTY:62-75`）。`step0_check_data.py` 会检查 BED 文件、外部工具和 Rscript，并把模型路径设为 `refdata/<factor>_LR_CnTATAC_model.joblib`（`PATTY/lib/step0_check_data.py:37-91`, `PATTY/lib/step0_check_data.py:117-153`, `PATTY/lib/step0_check_data.py:186-188`）。`setup.py` 打包了三个预训练模型文件（`PATTY/setup.py:86-90`）。

### bulk PATTY 计算流程

#### 输入

- CUT&Tag BED 或 BED.GZ
- ATAC BED 或 BED.GZ
- genome-wide mappable 200 bp bin 文件
- histone mark factor
- 预训练 LR 模型

#### 关键变量

| 变量 | 含义 | 代码证据 |
|---|---|---|
| `binFile` | genome mappable bins | `PATTY/lib/step1_BULKscanSig.py:38-53` |
| `binmid` | 200 bp bin 中点，代码用 `start + 100` | `PATTY/lib/step1_BULKscanSig.py:52-59` |
| `binextsize` | 1 kb 上下文窗口大小 | `PATTY/lib/step1_BULKscanSig.py:52-65` |
| `binSig_CnT`, `binSig_ATAC` | CUT&Tag / ATAC 局部 coverage 数组 | `PATTY/lib/step1_BULKscanSig.py:67-72` |
| `X_row` | 拼接后的模型输入特征 | `PATTY/lib/step1_BULKscanSig.py:104-115` |
| `y_pred_all` | LR positive-class probability，即 PATTY score | `PATTY/lib/step1_BULKscanSig.py:114-119` |

#### 逐步解释

1. 对每个 200 bp bin，代码取 `binmid = start + 100`，然后以这个点为中心构造 1 kb 区间，从 `binmid - 500` 到 `binmid + 500`，每 100 bp 一个 internal bin（`PATTY/lib/step1_BULKscanSig.py:52-65`）。
2. 读取 CUT&Tag 和 ATAC reads，并把 reads 映射到这些 100 bp coverage arrays（`PATTY/lib/step1_BULKscanSig.py:69-72`）。
3. `Utility.read_in_reads` 会把 single-end 或 pseudo-end 片段扩展成 146 bp，再累加到 100 bp bins 中；这是代码实现细节，论文方法段没有明确写出这个 146 bp 扩展规则（`PATTY/lib/Utility.py:140-182`）。
4. 每个 100 bp 数组会 reshape 成 `(10, 10)`，再取均值，得到 10 个 summary values；10 个 100 bp segment 合起来就是 100 个 CUT&Tag values 和 100 个 ATAC values（`PATTY/lib/step1_BULKscanSig.py:89-99`）。
5. 代码把 CUT&Tag 和 ATAC 交错放入 200 维向量：`X_row[0::2] = CUT&Tag`, `X_row[1::2] = ATAC`（`PATTY/lib/step1_BULKscanSig.py:104-115`）。
6. LR 模型输出 `predict_proba(X_all)[:, 1]`，写入 bedGraph，再转 bigWig（`PATTY/lib/step1_BULKscanSig.py:114-127`）。

论文说 visualization 时低于 0.5 的 prediction score 可以归零（`paper source:190-192`），但 package 里没有找到这个 threshold 步骤；代码直接写 raw probability。

### single-cell PATTY 计算流程

论文的 single-cell 核心思想是：先用 meta-cell 降低 sparsity，再对每个细胞做类似 bulk 的 PATTY score。论文描述为先在 ArchR 预处理输出的 top 50 high-variance PC space 中计算细胞距离，然后每个 target cell 取 top 10 neighbors，和 target cell 一起合并成 11-cell meta-cell（`paper source:198-200`）。

代码实现如下：

```text
scCUT&Tag fragments
        |
        v
ArchR / IterativeLSI -> cell distance matrix + high-var bins
        |
        v
target cell + 10 nearest neighbors -> meta-cell CUT&Tag profile
        |
        v
meta-cell CUT&Tag + shared ATAC feature matrix
        |
        v
LR predict_proba for every bin
        |
        v
OUTNAME_correctMat.txt
```

#### ArchR 预处理

`Utility.scProcess` 写出并运行 R 脚本：用 ArchR 创建 ArrowFiles 和 ArchRProject，然后对 TileMatrix 做 IterativeLSI。代码中使用 `varFeatures = 25000` 和 `dimsToUse = 1:30`，再用 Euclidean distance 计算细胞距离，输出 `tmp_cellDist.txt` 和 `tmp_highVarBin.bed`（`PATTY/lib/Utility.py:249-311`）。

这里和论文有一个 partial mismatch：论文写的是 top 50 high-variance PC space，而代码是 ArchR LSI dimensions 1:30（`paper source:198-200`, `PATTY/lib/Utility.py:285-301`）。

#### meta-cell scoring

`step1_SCscanSig.py` 读取 `tmp_cellDist.txt`，设置 `K=10`，对每个 target cell 取最近的 10 个 neighbors（`PATTY/lib/step1_SCscanSig.py:53-62`, `PATTY/lib/step1_SCscanSig.py:146-159`）。然后：

- 把 target cell 和 neighbors 的 CUT&Tag signal 相加。
- 用总 reads 数归一化。
- 把 meta-cell CUT&Tag feature 与同一个 ATAC feature matrix 拼接。
- 调用 LR `predict_proba`。
- 写出 `OUTNAME_correctMat.txt`（`PATTY/lib/step1_SCscanSig.py:146-167`）。

代码把 scATAC 当成 bulk ATAC companion 来构造共享 ATAC 特征，这和论文“to reduce computing complexity, we treated the scATAC-seq data as bulk ATAC-seq data”的描述一致（`paper source:198-200`, `PATTY/lib/step1_SCscanSig.py:87-112`）。

### 论文结果怎么验证 PATTY 有用？

论文主要用生物学预期来评估：

- 对 H3K27me3/H3K9me3 这类 repressive marks，corrected score 应该和 gene expression、reciprocal active mark 更负相关（`paper source:178-184`）。
- 对 H3K27ac 这类 active mark，corrected score 应该和 gene expression 更正相关，和 reciprocal repressive mark 更负相关（`paper source:76-82`, `paper source:178-184`）。
- Figure 4 显示 H3K27me3 active promoter 假信号被 PATTY 压低；Figure 6 显示 H3K9me3 的开放染色质假峰也被压低；Figure 7 显示 corrected single-cell matrix 的聚类 ARI 更高（`figure_analysis.md`）。

single-cell 的 paper evaluation 是 PCA -> k-means -> ARI，并且 nano-CT 还描述了 WNN integration（`paper source:198-206`）。这些评估代码在当前 package 中是 `Not found`；`bin/PATTY` 里 clustering 相关部分是注释掉的（`PATTY/bin/PATTY:220-225`），parser 里的 cluster options 也是注释或未实现状态（`PATTY/bin/PATTY:145-148`）。README 提到 clustering options，但 package 里没有找到对应实现（`PATTY/README.md:142-147`）。

### 对研究者最重要的理解点

1. PATTY 不是普通 peak caller。它把每个 200 bp bin 看作一个分类/打分对象，用 CUT&Tag signal 和 ATAC signal 判断这个 bin 更像 true histone mark 还是 open-chromatin artifact。
2. 论文里的方法开发阶段很大，包括 true/false region curation、模型比较、feature ablation、genome-wide evaluation；但当前 package 主要发布的是最终 pretrained LR inference。
3. package 的 bulk 路径比较直接：BED reads -> 1 kb local feature -> LR score -> bigWig。
4. package 的 single-cell 路径先做 meta-cell：target cell + top 10 nearest neighbors，再用 bulk-like ATAC 作为共同参照。
5. 代码可以支持核心推断复现，但不能单独复现所有论文图和训练过程。论文也把 package code 和 all-analysis scripts 分开列出（`paper source:220-222`），README 指向单独的 figure scripts repository（`PATTY/README.md:153-161`）。

### 已知缺口

- `Not found`: LR/RF/GBM/dNN 训练和 cross-validation 代码。
- `Not found`: IgG feature branch 和 DNA sequence branch 的 package 实现。
- `Not found`: PCA/k-means/ARI single-cell evaluation 代码。
- `Not found`: WNN integration 代码。
- `Not found`: 低于 0.5 的 score 自动归零步骤。
- Partial mismatch: paper 写 top 50 PC space，package 使用 ArchR LSI dims 1:30。
- OCR caveat: 本 workspace 的公式抽取噪声较大，PATTY 方法主要应按 prose 和代码流程理解，而不是按公式清单重建。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PATTY Summary

### What Problem Does PATTY Solve?

PATTY corrects open-chromatin bias in CUT&Tag data. The paper argues that Tn5 transposase can enrich reads at accessible chromatin even when the assayed histone modification is absent, creating false CUT&Tag signal that conventional peak callers such as MACS2/SICER/SEACR were not designed to remove (`paper source:38-40`). This is especially problematic for sparse single-cell CUT&Tag, where open-chromatin artifacts can distort downstream clustering (`paper source:30-40`).

### Method In One Paragraph

PATTY uses matched ATAC-seq as an accessibility control. The paper benchmarks multiple supervised models and feature combinations on curated true/false histone-mark regions, then deploys factor-specific logistic-regression models using CUT&Tag and ATAC signal patterns around each 200 bp genomic bin (`paper source:58-66`, `paper source:160-192`). In the released package, bulk mode builds 1 kb CUT&Tag+ATAC feature windows around genome mappable bins, applies a pretrained LR joblib model, and writes corrected bedGraph/bigWig scores (`PATTY/lib/step1_BULKscanSig.py:52-127`). Single-cell mode uses ArchR-derived cell distances, merges each target cell with its top 10 nearest neighbors into a meta-cell, pairs that CUT&Tag signal with a shared ATAC feature matrix, and writes a bin-by-cell corrected score matrix (`PATTY/lib/step1_SCscanSig.py:34-167`).

### Main Results

The paper reports that LR with CUT&Tag+ATAC features gives the strongest biology-consistent H3K27me3 correction among tested models and feature combinations, measured by more negative correlations with gene expression and H3K27ac (`paper source:58-66`, `paper source:178-184`). Viewed figures support the main result claims: Figure 4 panels show reduced active-promoter H3K27me3 artifacts and stronger negative correlations after PATTY correction; Figure 5 extends the correction to H3K27ac and bivalent-domain interpretation; Figure 6 supports H3K9me3 correction; Figure 7 shows higher ARI bars and cleaner UMAP cluster/cell-type agreement after single-cell PATTY correction (`figure_analysis.md`).

### Code-Paper Match And Reproducibility

The package code-paper match is **medium**. The core deployed inference tool is present: CLI inputs, pretrained LR model selection for H3K27me3/H3K27ac/H3K9me3, bulk scoring, single-cell meta-cell scoring, and output writing all have direct source support (`doc_code.md`). However, the package is inference-focused. Training/model exploration across LR/RF/GBM/dNN, IgG and DNA sequence feature branches, PCA/k-means/ARI evaluation, WNN integration, and the paper's optional `<0.5 -> 0` visualization threshold are `Not found` in the package code searched. The paper's code availability statement separates package source from scripts for all analyses (`paper source:220-222`), and the package README points manuscript figure reproduction to a separate `PATTY_figure_scripts` repository (`PATTY/README.md:153-161`).

### Practical Rating

Reproducibility rating: **3/5** for package-level inference, **2/5** for full paper reproduction from this workspace alone.

- Strengths: compact CLI, bundled pretrained LR models, direct bulk/sc inference implementations, explicit BED input format, test-data links, and source-code coverage for the core deployed PATTY scoring path.
- Limitations: no local supplementary markdown; OCR is usable but formula inventory is noisy; model training and manuscript evaluation scripts are outside `code source`; several README-documented clustering options are not implemented in the package CLI.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
