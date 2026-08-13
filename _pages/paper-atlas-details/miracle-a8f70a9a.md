---
layout: default
permalink: /paper-atlas/miracle-a8f70a9a/
title: "MIRACLE"
nav: false
wide: true
description: "单细胞图谱不是一次性建成的：新的批次、组织、测序模态和疾病数据会持续到来。传统离线整合每次都把历史数据全部重新训练，数据越多，时间和内存开销越大。只做泛化的在线方法无需训练，但遇到训练集中没有的生物学或技术变化时适应性差；只对新批次微调的方法会逐步遗忘旧知识。很多已有在线方法还假定固定模态，无法处理不同批次具有不同模态的 mosaic 数据。"
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
      <span>Nature Computational Science · 2026</span>
    </div>
    <h1>MIRACLE</h1>
    <p>Continual integration of single-cell multimodal data with MIRACLE</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/sc-miracle/miracle" target="_blank" rel="noopener noreferrer" aria-label="Open code for MIRACLE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MIRACLE：持续整合单细胞多模态数据的方法说明

### 它要解决什么问题？

单细胞图谱不是一次性建成的：新的批次、组织、测序模态和疾病数据会持续到来。传统离线整合每次都把历史数据全部重新训练，数据越多，时间和内存开销越大。只做泛化的在线方法无需训练，但遇到训练集中没有的生物学或技术变化时适应性差；只对新批次微调的方法会逐步遗忘旧知识。很多已有在线方法还假定固定模态，无法处理不同批次具有不同模态的 mosaic 数据（论文 `paper.md:1-46`）。

### MIRACLE 的核心想法

MIRACLE（multimodal integration with continual learning）把 MIDAS 多模态 VAE 放进持续学习（continual learning, CL）框架中。每一步同时使用当前批次和一个有容量上限的 rehearsal memory：模型适应新数据，记忆抽样保留历史分布，再输出截至当前时刻的累计嵌入、批次校正值和模态补全结果。遇到新模态或新特征时扩展输入布局，并把旧模型中形状兼容的权重复制到新模型。

论文用三组方程说明差异：离线策略每次由 (f_{\rm off}(&#123;&#123;\mathcal X}}_{1:t})) 重训；泛化策略固定 (&#123;&#123;\mathbf{\uptheta}}}_{0}) 只推断新批次；微调策略用 (f_{\rm FT}(&#123;&#123;\mathcal X}}_{t};&#123;&#123;\mathbf{\uptheta}}}_{t-1})) 更新但会遗忘。MIRACLE 的更新是

$$
&#123;&#123;\mathbf{\uptheta}}}_{t}=f_{\rm CL}(&#123;&#123;\mathcal X}}_{t},&#123;&#123;\mathcal R}}_{t-1};&#123;&#123;\mathbf{\uptheta}}}_{t-1}),\quad
&#123;&#123;\mathcal R}}_{t}=h(&#123;&#123;\mathcal X}}_{t},&#123;&#123;\mathcal R}}_{t-1};&#123;&#123;\mathbf{\uptheta}}}_{t}),\quad
&#123;&#123;\mathcal Y}}_{1:t}=g(&#123;&#123;\mathcal X}}_{1:t};&#123;&#123;\mathbf{\uptheta}}}_{t}).
$$

其中 (\mathcal R_t) 是历史数据的有界代表集（论文 `paper.md:251-326`）。

### 计算流程

```text
第 t 批当前 MuData X_t + 上一步 replay R_{t-1} + checkpoint θ_{t-1}
                 │
                 ├─ 检查 current/replay 的 batch ID 不重叠
                 ├─ 合并模态，按参考特征顺序对齐，并给缺失模态/特征建立 mask
                 ├─ 当前批次与 replay 批次交替组成训练 minibatch
                 ├─ MIDAS 编码各模态，product-of-experts 得到 z=(c,b)
                 │      c：生物学/内容部分；b：批次/技术部分
                 ├─ 解码重构 RNA、ADT、ATAC，并可进行模态补全/翻译
                 ├─ 重构 + KL + 模态一致性 − 对抗批次分类损失，更新 θ_t
                 ├─ 推断累计嵌入 Y_{1:t}
                 └─ 先按批次比例分配 memory，再在每批 latent 空间用 BallTree 抽样得到 R_t
```

代码对应关系：`scmiracle/model.py:1229-1254` 建立第一步模型；`:1256-1365` 载入旧 checkpoint、合并 replay/current、进行特征布局和权重迁移；`:1367-1418` 训练、保存和提取 latent；`:1486-1580` 构建 replay。

### 模态与动态特征

一条细胞观测写作

$$
&#123;&#123;\mathbf x}}_{\tau,n}=\left\{\&#123;&#123;{\mathbf o}}_{\tau,n}^{m}\}_{m\in\mathcal M_{\tau}},s_{\tau,n}\right\},
$$

其中 (\mathcal M_{\tau}) 是该批次实际具有的模态，(s_{\tau,n}=\tau) 是批次 ID。输出包含每种累计模态的补全/批次校正向量和生物学嵌入 (\mathbf z)（论文 Eqs. 9–10，`paper.md:397-420`）。代码的 `_LazyMultiModalDataset` 按行读取 MuData、返回模态字典、批次 ID 和可见特征 mask（`scmiracle/model.py:196-275`）。

论文的动态架构公式为

$$
\hat&#123;&#123;\mathbf{\uptheta}}}_{t}=[&#123;&#123;\mathbf{\uptheta}}}_{t-1},\tilde&#123;&#123;\mathbf{\uptheta}}}_{t}],
$$

即为新增模态/特征准备新的参数块，再与旧参数一起训练（`paper.md:328-333`）。本地代码将其落实为“参考变量在前、新变量追加”的目标布局（`scmiracle/model.py:980-1044`），并在 checkpoint 中对兼容张量做整块或切片复制（`:1997-2167`）。外部 `scmidas` 内部的完整网络和新增参数初始化分布不在本地，因此这些细节应标成 **Not found**，不能从 wrapper 推断。

### MIDAS 编码、损失与 replay

legacy 实现显示了 MIDAS 风格的计算：每个模态有 encoder，batch ID 可经 one-hot encoder 进入模型；各高斯专家通过 product-of-experts 合并，得到 (z)，再分成 (c) 和 (b)；decoder 生成各模态，ATAC 还按染色体块处理（`reproducibility/modules/models.py:36-148`）。损失包括 RNA/ADT 的 Poisson NLL、ATAC 的 BCE、标签 CE、(z) 的 KL，以及模态 latent 一致性；batch discriminator 的对抗项用于让 (c) 少携带批次信息（`:190-351`）。现代 `_MIDASContinual.training_step` 在新旧数据上计算这些由 MIDAS 提供的项，并对 replay/current 施加归一化权重（`scmiracle/model.py:347-401`）。论文的补充损失公式和超参数在本地没有完整副本，不能宣称已逐项复现。

Memory 的 DPRS 分两层：先按原始批次规模分配容量 (M)，满足论文 Eq. 6 的 (\alpha M_{t-1}+\beta N_t=M) 和历史/新批次比例；再在每个批次的 latent 空间建 BallTree，从各分区抽样。legacy `BallTreeSubsample` 在 `reproducibility/continual.py:356-388`，现代 wrapper 的批次比例和抽样在 `scmiracle/model.py:1537-1567,1939-1995`。这说明“怎么抽样”已实现，但抽样本身不等于已经证明 MMD 更低；MMD、速度和 memory 容量的证据来自论文 Extended Data Fig. 1。

### 论文中的验证

- DHCM（523,369 个细胞、42 批）和 HLCA（约 230 万个细胞）验证了 BTS、memory 容量和效率；论文报告 BTS 的 MMD 最低，约 20K memory 后 scIB 趋于饱和。
- 八批 WNN CITE-seq PBMC 验证了批次校正和细胞类型保持；MIRACLE 接近 offline 基准，而无 replay 的 MIRACLE-transfer 出现遗忘。
- DOTEA/mosaic 数据验证了不同模态组合下的 batch、modality alignment 和 biological conservation。
- PBMC 与 tonsil、BMMC、spleen 的连续 atlas 及 label transfer 验证了新组织细胞类型识别；Unknown 区域对应新的细胞类型。
- 健康 PBMC → COVID-19 → flu A → TB 的应用将人工标签从 13 类细化到 23 类，并报告 CD4 cytotoxic T、HERC1+ T 和 MAIT 相关免疫信号（论文 Figs. 2–6 与 Extended Data Fig. 1）。

论文使用 scIB/scMIB 的 batch、modality 和 biological 指标，以及 ACC/BWT 评估遗忘（`paper.md:646-699`）。这些结果是论文/图像证据；本地代码的 notebooks 依赖外部数据，并未在本阶段重新运行。

### 如何理解“代码支持到什么程度”

已由源码直接确认：MuData 输入、current/replay 训练、交替 sampler、原始细胞数加权、BallTree replay、特征对齐/扩展、checkpoint 元数据、latent/补全/翻译接口。未能由本地源码确认：`scmidas` 内部全部 MIDAS 默认值和补充损失、Seurat/Signac 预处理阈值、完整 benchmark 数据与一键重现 Nature 图表、论文 label-transfer 的完整 kNN novelty 规则。因此，MIRACLE 的“机制如何工作”可以按上述代码学习；论文报告的数值和感染生物学结论仍应按原论文和 source data 阅读。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MIRACLE: continual multimodal single-cell integration

### Problem

Single-cell atlases are updated as asynchronous batches arrive, but conventional offline integration retrains on every historical cell. That makes repeated updates increasingly expensive and prevents rapid incorporation of new modalities, tissues, or diseases. Generalization-only online methods are cheap but cannot adapt to unseen biology/technical variation; fine-tuning-only methods adapt but progressively forget earlier batches; many existing online tools are modality-specific and do not support mosaic inputs (`paper.md:1-46`).

### Proposed method

MIRACLE (multimodal integration with continual learning) wraps the MIDAS multimodal VAE in a continual-learning loop. At each step it trains on the current batch plus a bounded rehearsal memory, expands the architecture for new modalities/features, updates cumulative embeddings and imputed/batch-corrected modalities, then rebuilds memory with distribution-preserving reservoir sampling (DPRS). DPRS combines batch-proportional reservoir allocation with BallTree sampling (BTS) in latent space. The design supports ATAC, RNA, and ADT mosaic batches, atlas sharing, and query label transfer (`paper.md:47-66`; `doc_method.md`).

### Evaluation and main results

- **Memory/scaling:** On DHCM snRNA-seq (523,369 cells, 42 batches), BTS had the lowest MMD and better variance than SRS, Sketch, and scSampler; MIRACLE-BTS performance saturated around 20K replay cells (about 1/26 of DHCM). MIRACLE-BTS-20K approached MIRACLE-offline quality while keeping incremental time and memory nearly constant. The paper reports similar advantages on the 2.3-million-cell HLCA (`paper.md:67-84`; Extended Data Fig. 1).
- **Continual batches/cell types:** On eight WNN CITE-seq PBMC batches with deliberately missing cell types, MIRACLE mixed batches while retaining cell-type structure and outperformed transfer-only controls and online versions of 11 comparators in scIB/scMIB-oriented evaluations (`paper.md:85-110`; Fig. 2).
- **Mosaic integration:** On DOTEA-style multimodal batches, MIRACLE’s batch, modality-alignment, and biological-conservation scores were generally highest or near the offline reference, while transfer baselines showed stronger fragmentation (`paper.md:111-133`; Fig. 3).
- **Cross-tissue atlas construction:** Sequential PBMC, tonsil, BMMC, and spleen updates retained tissue-specific states, identified new cross-tissue cell types, and showed higher neighborhood overlap with the offline reference than generalization or transfer (`paper.md:134-159`; Fig. 4).
- **Label transfer:** kNN transfer with an Unknown/novelty category gave higher micro/binary F1 than generalization and transfer controls for within- and cross-tissue queries; Unknown cells corresponded to new cell types (`paper.md:160-182`; Fig. 5).
- **Respiratory infections:** Sequential healthy PBMC → COVID-19 → flu A → TB integration expanded manual labels from 13 to 23 and supported multimodal evidence for COVID-19 CD4 cytotoxic T cells, a putative flu-A HERC1+ exhaustion-associated subset, and infection-associated MAIT depletion/function changes (`paper.md:183-214`; Fig. 6).

### Reproducibility and limitations

**Code-paper match: medium (3/5 reproducibility).** The snapshot directly exposes replay/current training, alternating source sampling, proportional replay weighting, BallTree selection, feature-layout expansion, compatible checkpoint transfer, MuData loading, and latent/imputation/translation interfaces (`scmiracle/model.py`; `reproducibility/continual.py`). The repository README gives a de-novo → replay → continual workflow (`code/README.md:45-128`).

Important boundaries remain: canonical MIDAS network/loss defaults are delegated to external `scmidas`; Seurat/Signac QC and feature selection are not implemented in the package; the exact supplementary objective and hyperparameter schedule are not locally available; many benchmark/application calculations are in notebooks and require external processed data; and no end-to-end rerun of the Nature figures was performed. Thus speed, metric values, statistical tests, and infection discoveries are paper/figure claims rather than newly verified runtime results. The code contains both a modern wrapper and legacy experiment scripts, and bit-identical behavior between them is not established (`doc_code.md` for exact/partial/not-found rows).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
