---
layout: default
permalink: /paper-atlas/dreams-38dcb96a/
title: "DreaMS"
nav: false
description: "LC–MS/MS 每分钟产生大量 tandem mass spectra，但通常不到 10% 能可靠匹配分子结构。传统学习方法主要依赖 MoNA、NIST20 等 annotated libraries，覆盖的分子空间远小于公共仓库中积累的 unannotated spectra。"
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
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>DreaMS</h1>
    <p>Self-supervised learning of molecular representations from millions of tandem mass spectra using DreaMS</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-025-02663-3" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DreaMS 方法解读：从数千万未注释串联质谱学习分子表示

### 核心问题

LC–MS/MS 每分钟产生大量 tandem mass spectra，但通常不到 10% 能可靠匹配分子结构。传统学习方法主要依赖 MoNA、NIST20 等 annotated libraries，覆盖的分子空间远小于公共仓库中积累的 unannotated spectra。DreaMS 的策略是先在没有结构标签的高质量 spectra 上做 self-supervised pre-training，再用少量 annotated spectra fine-tune 到谱图相似性、fingerprint、分子性质和含氟检测。

DreaMS 学到的是“一个谱图在训练分布中的 1,024-dimensional representation”，不是从谱图唯一反演分子结构。不同结构可能产生近似 spectra，同一分子也会随 collision energy、instrument、adduct 改变；embedding 主要用于相似性和下游预测，最终结构注释仍需数据库、formula/fragment evidence 或实验确认。

### 证据入口与版本边界

- 论文：`paper source/paper/vlm/paper.md`，Nature Biotechnology 2025，DOI `10.1038/s41587-025-02663-3`。
- 图像：`paper source/paper/vlm/images/`；现有 `figure_analysis.md` 已逐图读取这些主图。
- 代码：`code/`，上游 `https://github.com/pluskal-lab/DreaMS`。当前目录没有独立嵌套 Git 元数据，因此不能从 outer PaperCode commit 推断 DreaMS 上游 commit。
- 权重：Zenodo 10997887；GeMS/DreaMS Atlas 数据在 Hugging Face。当前 workspace 含完整软件与训练入口，但不含 24M/201M spectra 数据或预训练权重本体。

### GeMS：为什么先解决数据质量与冗余

作者从 GNPS/MassIVE 收集约 250,000 LC–MS/MS experiments 和约 700 million spectra，按 experiment-level 与 spectrum-level criteria 构建 GeMS-A/B/C：A 最严格，97% 来自 Orbitrap；C 更大但包含较多 QTOF。随后用 locality-sensitive hashing（LSH）近似 binned-spectrum cosine similarity，把高度重复 spectra 聚类，并限制每 cluster 的 representatives。

主模型使用 GeMS-A10：每 cluster 最多随机保留 10 条，约 24 million spectra。Extended Data Fig. 3 显示，扩大到更松散或低质量的数据反而降低 embedding quality。因此本文的 scaling 结论是“高质量且去冗余的数据量有帮助”，不是“任何更多 spectra 都更好”。

本地 `dreams/algorithms/lsh/` 实现 LSH，`MSData`/HDF5 支持 repository-scale minibatch access。DreaMS Atlas 进一步用 fine-tuned embeddings 构建 201 million spectra 的网络；Atlas node/edge 是算法聚合结果，不等于 201 million 已鉴定分子。

### 单条谱图如何变成 Transformer tokens

每个输入保留 top-$n$ fragment peaks，按 base peak 把 intensity 归一化到 $[0,1]$，不足时 zero-pad。再把 precursor 放在第 0 位：

$$
S=\begin{bmatrix}
m_0&m_1&\cdots&m_n\\
1.1&i_1&\cdots&i_n
\end{bmatrix}.
$$

人工 intensity 1.1 高于 fragment maximum，使 precursor token 可识别且永不被 mask，作用类似 `[CLS]`：Transformer 后该位置的 1,024-vector 汇聚全谱信息。本地 `SpectrumPreprocessor` 直接 prepend `(precursor_mz, 1.1)`；pre-training 通常保留 60 peaks，fine-tuning 可用 100。

这一预处理会丢弃低排名 peaks、absolute intensity 和部分 acquisition context。对弱谱/不同 ion mode、charge 或 $m/z>1000$ 的泛化不能仅由模型结构保证。

### 质量数编码：同时看整数质量与仪器精度

原始 $m/z$ 是连续高精度值。粗 binning 会混淆精确质量，直接 MLP 又难同时学习 1 Da 级组成差异与 $10^{-4}$ Da 级小数。DreaMS 为每个 mass 构造预定义 Fourier features：

$$
\Phi_b(m)=[\sin(2\pi bm),\cos(2\pi bm)],
$$

频率分成低频与高频组，分别强调 integer-like mass structure 和 fine decimal accuracy。论文主配置有 6,000 frequencies，即 12,000 sine/cos values，经多层 FFN 压到 980 dimensions。

另一条浅 FFN 接收 normalized $m/z$ 与 intensity，输出 44 dimensions。两路 concat 得 1,024-dimensional peak token：

$$
e_i=\mathrm{FFN}_F(\Phi(m_i))\;\|\;
\mathrm{FFN}_P(\tilde m_i,i_i).
$$

本地 `fourier_features.py` 与 `dreams.py` 实现该双路 PEAKENCODER。Fourier frequencies 默认是物理启发的固定 basis，后续 FFN 参数可学习；“频率本身学出元素组成”不是准确说法。

### Spectrum encoder 与 neutral-loss bias

主干是 7-layer、8-head、$d=1024$ 的 pre-norm Transformer。标准 attention 通过 query/key content 建峰间关系；DreaMS 还把每对 peaks 的 mass/Fourier differences 作为 Graphormer-style bias 加到 attention logits：

$$
a_{ij}^{(h)}\propto
\frac{q_i^Tk_j+b_h(\Phi(m_i)-\Phi(m_j))}{\sqrt{d_h}}.
$$

在 MS/MS 中，peak difference 对应 neutral loss 候选，常含 fragment chemistry 信息。本地 `MultiheadAttention.forward()` 将 `graphormer_dists` 线性映射到各 heads，并在 softmax 前加到 `att_weights`。它不是先给 neutral loss 指派化学式，而是让网络直接使用连续 mass-difference feature。

attention 较高表示该训练模型在当前前向中强使用某峰对，不等于该峰已经被化学结构注释。Extended Data Fig. 2 只说明可由 SIRIUS fragmentation tree 解释的 peaks 在统计上更受关注。

### 两个 self-supervised objectives

#### 1. Masked $m/z$ classification

每条 spectrum 随机 mask 30% fragment $m/z$，sampling probability 与 intensity 成正比；intensity 本身保留。模型不是回归一个 mass，而是在 0–1000 Da、0.05 Da bins 上预测 20,000-class distribution。

分类比 regression 更适合多峰不确定性：上下文可能允许多个 plausible fragments，回归会给出不存在的平均质量。论文消融显示 classification 是最关键设计之一。最终配置使用 focal loss $\gamma=5$，减少 easy bins 对梯度的主导；本地通用 `FocalLoss` 默认可退化成 cross-entropy，但训练配置决定最终 $\gamma$，解释时不能只看类默认值。

#### 2. Retention-order prediction

从同一 LC run 采样两条 spectra，concat 两个 precursor embeddings，预测哪个先 elute。它给 embedding 加入 polarity/hydrophobicity 等 chromatographic information，但 retention order 受 column、gradient 与实验条件影响，不是纯分子结构标签。

总 loss 为

$$
\mathcal L=0.8\mathcal L_{mask}+0.2\mathcal L_{order}.
$$

本地 `dreams.py` 按 `ret_order_loss_w` 组合 masked focal/CE 与 binary cross-entropy。预训练还做 random $m/z$ shift augmentation，鼓励模型不把绝对 precursor mass 当作捷径。

### “分子结构自发涌现”意味着什么

Figure 3 在训练期间冻结 backbone，用 precursor embeddings 线性预测 MACCS keys；probe recall 随 masked reconstruction 改善而上升。attention 也更偏向可解释 peaks，PCA/kNN 中同一结构在不同 acquisition conditions 下聚合。

这些证据说明 embedding 含有线性可读的结构信息，并非网络已完成 de novo structure elucidation。linear probe 使用了 labeled molecules 作评估，且 NIST20/MoNA 的 chemical space 与真实未知物分布不同。

### Fine-tuning tasks

#### Spectral similarity

zero-shot precursor embedding cosine 已优于多种基线的结构相似相关，但对小结构差异不敏感。作者用 anchor/positive（同分子）/hard negative（不同结构且 precursor mass 差不超过 0.05 Da）contrastive fine-tuning，使近质量异构体分开。

论文 margin $\Delta=0.1$，代码通用默认曾为 0.2；应以实际 checkpoint configuration 为准。fine-tuned similarity 是结构近似分数，不是 calibrated identity probability。

#### Fingerprint 与 molecular properties

fingerprint head 可聚合所有 peak embeddings，预测 4,096-bit Morgan fingerprint，以 cosine loss 训练；property head 回归 QED、synthetic accessibility、complexity 等 11 properties。代码支持 DeepSets-style head，但它取决于 `head_phi_depth` 配置，不能说每个默认 head 都必然使用论文图示的两层聚合。

#### Fluorine detection

binary head 以 focal loss 处理 class imbalance。作者用两个 thresholds 使含氟/不含氟两侧各达约 90% precision，中间约 5% 标作 uncertain。双阈值比固定 0.5 更符合部署，但 precision 与 coverage 依赖 test distribution，不能直接迁移到任意 instrument/sample。

### Murcko-histogram split：为何是评估核心

随机 spectrum split 会让相同或近似 scaffold 同时进入 train/validation，夸大 transfer。作者设计 Murcko histogram，以 ring/linker type counts 分层，使 validation molecules 在 scaffold composition 上更远。Extended Data Fig. 4 显示其近重复 leakage 少于 structure-disjoint baseline。

本地 `algorithms/murcko_hist/` 实现该 split。它降低已知 scaffold leakage，但不能保证所有 chemical similarity、stereochemistry 或 biosynthetic family 完全隔离。

### 图结果应如何读

- Figure 1–2 建立数据规模与 GeMS 构建逻辑；“700M unannotated”不等于高质量训练集，主训练用 24M A10。
- Figure 3 支持 self-supervised structural awareness，并通过消融确认 Fourier/classification/data quality 的作用。
- Figure 4 显示 fine-tuned similarity、fingerprint、properties 与 fluorine tasks 的 benchmark；不同任务的数据集和 metrics 不可互换。
- 后续 Atlas 图展示大规模 chemical neighborhood 与查询能力；network edge 仍是 embedding similarity，不是实验确认的 biochemical relationship。

### 论文—代码映射

| 环节 | 本地位置 | 程度 | 边界 |
|---|---|---|---|
| peak/precursor preprocessing | `utils/data.py` | Exact | top-n 与过滤受配置影响 |
| mass-tolerant Fourier encoder | `models/layers/fourier_features.py` | Exact | 最终频率/深度由 checkpoint args 决定 |
| 7-layer Graphormer Transformer | `models/dreams/` | Exact | attention 不等于 fragment annotation |
| masked mass + retention-order loss | `dreams.py`, `losses_metrics.py` | Exact | focal gamma/weights 依训练配置 |
| fine-tuning heads | `models/heads/heads.py` | Exact/Partial | paper margin 与通用 code default 有差异 |
| LSH / Murcko split | `algorithms/` | Exact | Atlas 构建还依赖大型外部数据 |
| embedding API | `api.py` | Exact | 权重需从 Zenodo 获取 |
| 24M GeMS pretraining/201M Atlas rerun | external data/weights | Not locally rerun | workspace 不含数据本体 |

### 最稳妥的结论

DreaMS 的贡献是把连续高精度 peak sets 编码成能利用 neutral-loss relations 的 Transformer tokens，并用 masked mass 与 retention order 从大量未注释 spectra 中学习通用表示。它显著减少了每个任务对大型 annotated library 的依赖，但没有消除 instrument/domain shift、谱图歧义和 chemical-space coverage 问题。实际注释应把 DreaMS similarity/heads 作为候选优先级，与 precursor formula、isotope/adduct、fragmentation tree、retention standard 和实验复核联合使用。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DreaMS Summary

**Paper**: Self-supervised learning of molecular representations from millions of tandem mass spectra using DreaMS
**Journal**: Nature Biotechnology (2025) | **DOI**: 10.1038/s41587-025-02663-3
**Authors**: Roman Bushuiev*, Anton Bushuiev*, Raman Samusevich, Corinna Brungs, Josef Sivic, Tomáš Pluskal
**Code**: https://github.com/pluskal-lab/DreaMS | **Data**: HuggingFace `roman-bushuiev/GeMS`

---

### Motivation & Novelty

#### The Problem

LC-MS/MS is the dominant technology for characterizing molecular composition of biological and environmental samples. When a molecule enters the mass spectrometer, it is fragmented and the fragment masses are recorded as a tandem mass spectrum (MS/MS). The challenge: given only the spectrum, identify the molecule. Currently:
- Only ~2% of MS/MS spectra can be annotated using reference spectral libraries
- State-of-the-art ML tools (SIRIUS, MIST) raise this to <10%
- Annotated libraries (MoNA, NIST20) cover only a small fraction of known chemical space
- ~700 million unannotated experimental spectra from GNPS/MassIVE remain unused

#### Limitations of Existing Approaches

- **Spectral similarity methods** (dot-product, modified cosine, spectral entropy — *Nat. Methods* 2021): Require the query molecule to already exist in a library; fail for novel compounds
- **MS2DeepScore** (*J. Cheminform.* 2021): Contrastive deep learning for similarity, but trained on annotated pairs — limited by library size
- **SIRIUS** (*Nat. Methods* 2019): Gold standard for annotation; uses fragmentation trees + combinatorial optimization + CSI:FingerID — computationally expensive, cannot exceed library coverage
- **MIST** (*Nat. Mach. Intell.* 2023): Replaces SIRIUS components with transformers but still requires formula annotations per peak (SIRIUS output) and pseudo-annotations (MAGMA)
- **Spec2Vec** (*PLoS Comput. Biol.* 2021): Statistical embeddings from occurrence patterns — no molecular structure learning

#### What DreaMS Contributes

1. **GeMS dataset**: First repository-scale standardized MS/MS dataset for deep learning — 700M experimental spectra from GNPS/MassIVE, with quality-controlled subsets up to 201M spectra
2. **Self-supervised pre-training for small-molecule MS/MS**: BERT-style masked peak prediction + retention order prediction on unannotated data — first such approach for metabolomics
3. **Mass-tolerant Fourier features**: Novel m/z encoding capturing both integer-mass (formula) and decimal-mass (instrument accuracy) information via 6,000 predefined sine/cosine frequencies
4. **Graphormer-style neutral-loss attention**: Explicit modeling of all pairwise m/z differences (neutral losses) in self-attention without extra tokens or computational overhead
5. **Murcko histogram splitting**: New scaffold-based train/val split protocol eliminating structural near-duplicates; reduces leakage ~2× vs. structure-disjoint splitting
6. **DreaMS Atlas**: Molecular network of 201 million MS/MS spectra with property annotations — first atlas of this scale enabling repository-scale metabolomics research

---

### Method Overview

DreaMS is a **116M-parameter transformer** pre-trained in a self-supervised manner on 24 million high-quality MS/MS spectra from the GeMS-A10 dataset.

#### Architecture

**PEAKENCODER** → **SPECTRUMENCODER** → **[task heads]**

- **PEAKENCODER**: Each peak $(m, i)$ is encoded into a 1024-dimensional vector by concatenating:
  - Fourier features of m/z → 4-layer FFN → 980-dim (captures precise masses)
  - Normalized m/z + intensity → shallow FFN → 44-dim (provides scale context)
- **SPECTRUMENCODER**: 7-layer pre-norm transformer encoder with 8 attention heads. Each attention layer incorporates Graphormer-style bias: element-wise differences of Fourier features between all peak pairs, enabling direct attention to neutral losses (fragmentation patterns)
- **Precursor token**: A special peak at position 0 with intensity 1.1 (above all fragment intensities) serves as a BERT [CLS] equivalent, aggregating spectrum-level information

#### Pre-Training Objectives

The model is trained on pairs of spectra from the same LC-MS/MS run:
1. **Masked m/z prediction** (80% of loss): Randomly mask 30% of peaks; predict their masses as distributions over 20,000 bins (0.05 Da resolution) using focal loss — forces learning of fragmentation chemistry
2. **Retention order prediction** (20% of loss): Binary classification: which spectrum elutes first in chromatography — forces learning of chemical property structure

#### Transfer Learning

Pre-trained backbone fine-tuned for:
- **Spectral similarity**: Triplet margin contrastive learning on 5,500 molecules from MoNA
- **Molecular fingerprints**: DeepSets aggregation over all peak embeddings, cosine similarity loss
- **Molecular properties**: 11 properties (QED, Bertz complexity, MW, etc.) via multi-output MSE regression
- **Fluorine detection**: Binary classification with focal loss for class imbalance correction

#### DreaMS Atlas

Applied pre-trained + fine-tuned models to annotate 201M GNPS spectra → 3-NN graph where edges = DreaMS embedding similarity. Enables annotation propagation from known to unknown compounds.

---

### Evaluation

#### Datasets

| Task | Train/Val | Test |
|------|-----------|------|
| Spectral similarity | MoNA subset (5,500 mols, [M+H]+, 60eV) | NIST20 (Murcko-disjoint from MoNA) |
| Fingerprint prediction | MIST CANOPUS benchmark (8,000 spectra) | MIST CANOPUS test set |
| Molecular properties | MoNA + NIST20 (Murcko split) | Held-out Murcko-disjoint |
| Fluorine detection | MoNA + NIST20 (Murcko split) | In-house library (17,052 spectra, 1,175 fluorinated) |

#### Results

**Spectral similarity** (Pearson correlation with Morgan Tanimoto similarity):
- Zero-shot DreaMS cosine > MS2DeepScore (trained supervised) — remarkable given DreaMS never saw molecular structures during pre-training
- Fine-tuned DreaMS further improves correlation and excels at library retrieval (AUROC) and analog search (MCES-based AUROC)

**Library retrieval** (AUROC, 10-ppm precursor window, NIST20):
- DreaMS (fine-tuned) > 44 classical similarity measures including spectral entropy

**Fingerprint prediction** (Top-k retrieval from PubChem, MIST CANOPUS benchmark):
- DreaMS top-1: **32.7%** vs MIST: 29.4% — DreaMS outperforms state-of-the-art despite not using per-peak formula annotations or SIRIUS preprocessing
- DreaMS top-5: 59.4% vs MIST: 55.3%

**Molecular property prediction** (Bertz complexity relative error, comparison to XGBoost and MS2Prop):
- DreaMS exceeds XGBoost and MS2Prop on all 11 properties
- Especially strong on high-complexity molecules (practically important for drug discovery)

**Fluorine detection** (precision-recall, 17,000 test spectra):
- DreaMS: **91% precision, 57% recall** vs SIRIUS: max 51% precision at any recall
- 95% of spectra receive high-confidence predictions (above 90%-precision threshold)

**Robustness to spectrum quality**:
- DreaMS performance drop on low-quality spectra (insufficient peaks) is substantially smaller than all compared methods

---

### Reproducibility

**Rating: 4/5**

**Strengths**:
- Full codebase publicly available with documentation (https://dreams-docs.readthedocs.io)
- 14 tutorial notebooks covering all analyses (embeddings, pre-training, fine-tuning, atlas)
- Model weights on Zenodo (https://zenodo.org/records/10997887)
- GeMS dataset on HuggingFace (`roman-bushuiev/GeMS`)
- Fixed random seeds, detailed hyperparameter tables in Supplementary Tables 3-4
- In-house fluorine test data deposited to MassIVE (MSV000094528)

**Weaknesses**:
- NIST20 not publicly available (commercial license) — affects fingerprint benchmark reproducibility
- Full pre-training requires 4× AMD MI250X or 8× NVIDIA A100 for 48h — significant compute
- GeMS dataset requires downloading 250,000 .mzML files from GNPS (~multi-TB storage)
- Linear probing procedure (every 2500 steps) appears to be in notebooks/experiments, not main training script
- Triplet margin Δ=0.2 in code default vs Δ=0.1 stated in paper — hyperparameter inconsistency

**Practical notes**:
1. Embedding inference only: `pip install dreams-ms` + `from dreams.api import dreams_embeddings` — no NIST20 needed
2. Fine-tuning for custom tasks: download weights from Zenodo, use `FingerprintHead` or `RegressionHead`
3. Environment: Python ≥3.10.13, PyTorch 2.2.1, PyTorch Lightning 2.0.8, RDKit 2023.9.6
4. Common pitfall: Fourier features use `lin_float_int` strategy by default, not the `random` or `voronov_et_al` alternatives — ablation shows this matters
5. DeepSets fingerprint head (Eq. 9) requires `head_phi_depth=1` flag; default is a simpler linear head on precursor embedding only

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
