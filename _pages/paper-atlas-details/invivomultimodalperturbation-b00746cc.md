---
layout: default
permalink: /paper-atlas/invivomultimodalperturbation-b00746cc/
title: "InVivoMultimodalPerturbation"
nav: false
description: "Perturb-Multimodal（Perturb-Multi）要解决的是一个功能基因组学中的核心问题：在真实组织环境里，一个基因扰动到底如何改变细胞的转录状态、蛋白/RNA 强度、亚细胞形态和空间位置关系？ 传统 Perturb-seq 可以用单细胞测序大规模读出扰动后的转录组变化，但通常需要把组织解离成细胞悬液，因此会丢失空间结构、细胞形态和蛋白定位信息。"
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
      <span>Perturbation Resources</span>
      <span>Cell · 2025</span>
    </div>
    <h1>InVivoMultimodalPerturbation</h1>
    <p>Perturb-Multimodal: A platform for pooled genetic screens with imaging and sequencing in intact mammalian tissue</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2025.05.022" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Perturb-Multimodal 方法中文解读

### 这篇文章要解决什么问题？

Perturb-Multimodal（Perturb-Multi）要解决的是一个功能基因组学中的核心问题：在真实组织环境里，一个基因扰动到底如何改变细胞的转录状态、蛋白/RNA 强度、亚细胞形态和空间位置关系？

传统 Perturb-seq 可以用单细胞测序大规模读出扰动后的转录组变化，但通常需要把组织解离成细胞悬液，因此会丢失空间结构、细胞形态和蛋白定位信息。成像式 pooled screen 可以保留形态和空间信息，但通常缺少全转录组层面的 readout。本文的目标就是把这两类信息接到同一套体内 pooled perturbation 实验中：同一只小鼠肝脏中的相邻切片，一部分做 fixed-cell Perturb-seq，一部分做 RCA-MERFISH 和蛋白/RNA 成像，再用共同的 sgRNA/barcode 身份把不同 readout 对齐（`paper.md:25-35`, `paper.md:39-50`）。

### 方法的核心创新

本文不是提出一个单独的深度学习模型，而是提出一套“体内扰动 + 固定组织成像 + 固定细胞测序 + 多模态整合分析”的平台。

关键创新包括：

- 在活体小鼠肝脏中用 lentiviral sgRNA/barcode library 产生 mosaic perturbation，再通过 AAV-Cre 激活 Cas9（`paper.md:73-77`）。
- 在固定组织中同时保留形态和 RNA，使用 RCA-MERFISH 读取内源 mRNA 和扰动 barcode，并用 oligo-conjugated antibody / FISH 读取蛋白和 abundant RNA（`paper.md:45-49`, `paper.md:275-282`）。
- 用 10x Flex fixed-cell Perturb-seq 在相邻切片上获得全转录组和 sgRNA 调用（`paper.md:49`, `paper.md:233-239`）。
- 用机器学习过滤 MERFISH 解码得到的 molecule，把 coding barcode 和 blank barcode 区分开，并设置自适应 5% false-positive/misidentification 阈值（`paper.md:283-286`）。
- 用 Cellpose 分割细胞，把 molecule 分配到细胞 mask，导出 AnnData 风格的 cell-by-feature 矩阵（`paper.md:286-289`）。
- 用 VQ-VAE 风格的 autoencoder 把每个细胞的多通道形态图像压缩成 morphology embedding，再和转录组、扰动、空间位置一起分析（`paper.md:295-305`）。

### 从输入到输出的计算流程

可以把 Perturb-Multi 理解成下面这条 pipeline：

```text
体内 sgRNA/barcode mosaic liver
        |
        | 固定后切相邻组织切片
        |
        +------------------------------+
        |                              |
        v                              v
fixed-cell Perturb-seq                 RCA-MERFISH + 蛋白/RNA 成像
全转录组 + sgRNA UMI                   mRNA/barcode/protein/morphology
        |                              |
sgRNA threshold calling                图像配准
转录组 count matrix                    molecule decoding
        |                              XGBoost + blank barcode 过滤
        |                              Cellpose segmentation
        |                              molecule-to-cell assignment
        |                              morphology crop / embedding
        +--------------+---------------+
                       v
              单细胞整合分析
              - QC / normalize / log transform
              - Harmony integration
              - Leiden clustering
              - wildtype label transfer
              - perturbation-level DE / score / correlation
                       |
                       v
        genotype -> transcription / protein intensity /
        morphology / zonation / spatial phenotype map
```

#### 1. 扰动设计和双 readout

每个 lentiviral vector 同时携带 sgRNA 和一个 185-mer RNA barcode。成像时可以通过 RCA-MERFISH 读取 barcode，测序时可以通过 fixed-cell Perturb-seq 读取 sgRNA。这样，成像和测序虽然来自相邻切片和不同 assay，但都能回到同一个 perturbation identity（`paper.md:73-77`）。

图 3 的 vector、实验时间线、barcode-call pie chart 和 Alb positive-control 都在说明：这套系统不是只做成像，也不是只做测序，而是通过共同的扰动标签把两个 readout 接起来。

#### 2. RCA-MERFISH 图像处理

论文中的 RCA-MERFISH 处理包括：

1. 多轮成像配准；
2. 对 mRNA/barcode molecule 做 decoding；
3. 用 XGBoost 训练 coding barcode vs blank barcode 分类器；
4. 用自适应 5% false-positive/misidentification 阈值过滤 molecule；
5. 导出高置信度 molecule 给后续 cell assignment（`paper.md:283-286`）。

代码中能直接验证的部分包括：

- fiducial-based registration：`registration.py:107-142`；
- spot finding 和 trace extraction：`spot_decoding.py:239-352`；
- RCA pixel decoder 的参数、tile decoding 和 molecule 保存：`merfish.py:27-153`, `merfish.py:155-241`；
- XGBoost molecule classifier 和 5% target rate：`barcode_classifier.py:10-112`, `merfish.py:313-338`；
- blank-fraction / misidentification threshold：`moleculeutil.py:437-499`。

因此，成像处理主干在代码中是有较好对应的。

#### 3. 细胞分割、molecule 分配和 AnnData 导出

论文说细胞分割使用 custom Cellpose model，输入包括 polyA staining 和 Na+/K+ ATPase membrane signal，并对 60X 和 40X 数据分别训练模型（`paper.md:286-288`）。

代码中验证到的是：

- `CellSegmentationParameters` 支持 Cellpose 参数、channel 设置和 `pretrained_model_path`（`segment.py:33-65`）；
- `segment_cells` 从 tile 中取 cytoplasm/nuclei channel，预处理后调用 Cellpose，并把 z-plane mask 合并成 3D mask（`segment.py:162-205`）；
- Cellpose wrapper 里设置随机种子、加载 pretrained model 或 Cellpose model type，并进行 mask prediction（`cellpose_segment.py:15-29`）；
- 2D mask 到 3D mask 的 relabel/merge 逻辑在 `cellpose_segment.py:40-146`；
- molecule assignment 把全局坐标和 cell polygon/mask 对齐，然后累计每个 cell 的 barcode counts 并写出 `cellxgene.h5ad`（`molecules.py:40-182`）。

需要注意：代码有 Cellpose 推理/分割流程，但没有找到论文所说 custom 60X/40X Cellpose model 的训练代码或模型权重。因此这里是“流程代码存在，paper-specific model asset 未找到”。

#### 4. 单细胞整合和聚类

论文的整合流程是：过滤细胞/基因，按每个 cell 总量归一到 10,000，log transform，回归 cell area 和 molecule count，z-score，PCA，然后用 Harmony 整合 MERFISH 和 Flex scRNA-seq，最后 Leiden clustering，少于 10 个差异基因的小 cluster 被 greedily merge（`paper.md:289-291`）。

代码中有对应的 reusable helper：

- `preprocess_data` 做 QC、filter、normalize_total、log1p、可选回归和 scale（`sc_processing.py:46-62`）；
- PCA/UMAP/Leiden/Harmony helper 在 `sc_processing.py:124-142`；
- `greedy_merge_clusters` 使用 ranksum 和 FDR correction，按少于 10 个 DE genes 的规则合并 cluster（`sc_processing.py:74-96`）。

但这些 helper 的默认参数不完全等于论文中的参数。比如论文写 top PCs、Leiden resolution 等具体选择，而代码中的函数需要外部 caller 传参。因此这里应理解为：操作步骤有代码支持，但不是完整的 figure-level reproduction script。

#### 5. label transfer

论文说：把 wildtype RCA-MERFISH/Flex 整合后的 cluster labels 转移到 perturbed RCA-MERFISH 数据中。具体做法是 Harmony integration 后，在 top 20 PCs 上训练 K=10 的 KNN classifier，用 wildtype RCA-MERFISH labels 去预测 perturbed RCA-MERFISH cells（`paper.md:291-292`）。

代码中找到的相关部分：

- `impute_data` 使用 KDTree 在 PCA 空间做 nearest-neighbor matching，默认 `n_neighbors=10`（`sc_processing.py:98-122`）；
- `allcools_integrate` 中有 generic `label_transfer` 分支（`sc_processing.py:144-183`）；
- `util.py` 里也有基于坐标的 nearest-neighbor / mutual-nearest-neighbor 工具（`util.py:25-56`）。

但是，没有找到论文所说“top 20 PCs + K=10 classifier + cluster label prediction”的精确实现。所以 label transfer 应该标为代码部分匹配，而不是完全匹配。

#### 6. morphology embedding / VQ-VAE

这是论文中最重要、但代码缺口最大的部分。

论文描述的模型是：

- 对每个 segmented cell 和每个 morphology channel，取中间 z-plane，按 cell mask crop 出单细胞图像；
- 60X 数据 crop 为 300x300，40X 数据 crop 为 256x256，再 rescale 到 128x128；
- 每个 single-color protein/RNA image 与 polyA fiducial channel 拼接；
- 用 VQ-VAE 第二代结构：ResNet 产生 bottom representation，再产生 top representation，两个 representation vector quantization 后 concat，再通过 decoder reconstruct image；
- MLP classifier 预测 protein/RNA channel identity，其中 hidden layer 是 512 维 embedding；
- 所有 channel 的 embedding concat 成 cell morphology representation；
- 另一个 MLP 预测 cell type 或 diet condition；
- loss 包含 latent loss、image reconstruction MSE、protein/RNA classification cross entropy、cell-type/diet-condition classification cross entropy（`paper.md:293-305`）。

图 2 和图 S4 清楚展示了这个模型在方法中的地位：Figure 2 用 morphology embedding 分析 cell state，Figure S4 画出 VQ-VAE 架构和训练/验证 loss 曲线。

但是，在本地 repo 的 `pipeline/**`、`README.md`、`notebooks/README.md`、notebook 文本/HTML 搜索范围内，没有找到 VQ-VAE/autoencoder/ResNet/latent/reconstruction loss 的实现。因此这部分只能说是 paper-verified，不能说是 code-verified。

### 评价结果怎么支持方法有效？

本文的评价不是单一 metric，而是多层验证。

#### screen call 是否可靠？

在大规模体内 screen 中，论文分析了约 79,000 个 imaging single-perturbation cells 和约 55,000 个 sequencing single-perturbation cells（`paper.md:75-77`）。Alb-targeting sgRNA 在测序和成像中都降低 Alb signal，Gapdh-targeting sgRNA 降低 anti-GAPDH signal，说明 perturbation identity 和 phenotype readout 之间能对上（`paper.md:79-83`）。

#### 多模态 phenotype 是否有信号？

论文报告：

- Perturb-seq 中 109/406 targeting sgRNAs 有显著转录 phenotype，而 0/50 control sgRNAs 显著；
- morphology imaging 中 84/406 targeting sgRNAs 和 3/50 control sgRNAs 显著；
- 同一基因的两个 sgRNA 在转录和形态 phenotype 上有较高相关性；
- transcriptional 和 morphological effects 整体正相关，但不是完全重复的信息（`paper.md:81-83`）。

这说明成像和测序不是互相替代，而是互补。

#### 生物学 case study

论文重点展示了三个 liver physiology case：

- **Zonation**：Wnt、oxygen sensing、metabolism-related perturbations 会改变 periportal/pericentral gene-expression state。空间成像显示 perturbed cells 在 zone 中的位置比例没有明显改变，因此作者倾向于解释为 trans-differentiation/state shift，而不是细胞迁移或 zone-specific survival（`paper.md:117-123`）。
- **Stress response**：`Sel1l` knockout 提高 calreticulin 和 UPR gene expression，同时降低 abundant secretory mRNAs，支持 ER stress/UPR 在肝细胞中可能通过降低 secretory protein burden 来适应（`paper.md:127-129`）。
- **Steatosis**：`Insig1`、`Eif2s1/Aars`、`Pten` 都导致 lipid droplet accumulation，但转录程序不同，说明相似形态 phenotype 可以来自不同机制（`paper.md:131-137`）。

### 复现和代码匹配情况

整体代码匹配度是 **medium**。

匹配较好的部分：

- RCA-MERFISH 图像配准、spot/trace extraction、molecule decoding/filtering；
- XGBoost coding-vs-blank molecule classifier 和 5% misidentification threshold；
- Cellpose 分割流程、2D-to-3D mask merge；
- molecule-to-cell assignment 和 AnnData export；
- Scanpy preprocessing、Harmony、Leiden、DE/correlation helper。

重要缺口：

- VQ-VAE/deep autoencoder 实现未找到；
- 论文中 top 20 PCs + K=10 KNN label-transfer classifier 未找到精确实现；
- Figure 6 的 tissue-zone segmentation 规则有论文描述，但未找到直接代码；
- 每个 figure 的完整统计脚本没有全部暴露，尤其 energy-distance tests 和 Benjamini-Yekutieli scoring。

因此，这个 repo 更像是“RCA-MERFISH 处理和扰动分析的 reusable software”，而不是完整的一键复现所有图的代码包。读这篇文章时，应该把 paper-verified 方法、code-verified 实现和未找到的 reproducibility gaps 分开理解。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

Perturb-Multimodal, or Perturb-Multi, addresses the problem of measuring how genetic perturbations alter cell state inside intact tissue. Standard pooled perturbation screens can scale through sequencing, but they usually lose spatial organization, morphology, and protein-localization phenotypes. Imaging-based screens preserve morphology and spatial context, but often lack transcriptome-wide readouts. This paper combines both readout types in fixed mouse liver tissue to build multimodal genotype-phenotype maps (`paper.md:25-35`, `paper.md:39-50`).

### Prior Limitations

The paper positions Perturb-Multi against three limitations:

- In vivo Perturb-seq can profile causal transcriptional effects but tissue dissociation loses spatial and morphological information (`paper.md:31-33`).
- Existing imaging-based pooled screens can map perturbations to visual phenotypes, but do not by themselves provide genome-wide transcriptional readouts in native tissue (`paper.md:29-35`).
- Liver physiology depends on spatial zonation, stress responses, and lipid-droplet morphology, so single-modality screens can miss phenotypes that are visible only through imaging or only through sequencing (`paper.md:93-137`).

### Proposed Method and Novelty

Perturb-Multi links pooled in vivo CRISPR perturbations to paired imaging and sequencing phenotypes in fixed tissue. The experimental design uses lentiviral sgRNA/barcode delivery in Cas9 mice, adjacent-section fixed-cell Perturb-seq, and RCA-MERFISH/protein imaging. The computational workflow converts these readouts into per-cell perturbation labels, RNA/protein intensities, spatial coordinates, morphology embeddings, and integrated cell-state annotations (`paper.md:43-49`, `paper.md:73-83`, `paper.md:275-306`).

Main novelty:

- A fixed-tissue assay pairing transcriptome-wide Perturb-seq with high-content tissue imaging.
- RCA-MERFISH detection of endogenous mRNAs and perturbation barcodes in morphology-preserved tissue.
- Machine-learning filtered molecule decoding and Cellpose-based cell segmentation feeding AnnData-style single-cell matrices.
- Morphology embeddings from a VQ-VAE-style autoencoder with auxiliary classification tasks.
- Joint genotype-phenotype analysis across sequencing, protein/RNA imaging intensity, subcellular morphology, and tissue-zone context.

### Method Overview

The pipeline is:

```text
sgRNA/barcode mosaic liver
  -> fixed-cell Perturb-seq on adjacent sections
  -> RCA-MERFISH/protein imaging on tissue sections
  -> image registration and molecule decoding
  -> XGBoost/blank-barcode filtering at 5% false-positive target
  -> Cellpose segmentation and 3D mask merging
  -> molecule-to-cell assignment and AnnData export
  -> preprocessing, Harmony integration, Leiden clustering
  -> wildtype-to-perturbed label transfer
  -> perturbation-level scoring, DE, correlation, and spatial/morphology analyses
```

The paper describes the VQ-VAE morphology model in detail but without a displayed objective equation. The loss terms are named in prose: latent loss, mean-squared reconstruction loss, protein/RNA classification loss, and cell-type or diet-condition classification loss (`paper.md:295-305`).

### Evaluation and Results

The paper evaluates Perturb-Multi at several levels.

Screen quality:

- In the large in vivo screen, the library targets 202 genes with two sgRNAs each plus 50 controls (`paper.md:71-75`).
- Imaging produced about 79,000 analyzed single-perturbation cells; sequencing produced about 55,000 analyzed single-perturbation cells (`paper.md:75-77`).
- Alb-targeting sgRNAs reduced Alb mRNA in both Perturb-seq and imaging, and Gapdh-targeting sgRNAs reduced anti-GAPDH signal, supporting perturbation-call accuracy (`paper.md:79-83`).

Multimodal phenotype signal:

- Perturb-seq found 109/406 targeting sgRNAs with significant transcriptional effects versus 0/50 controls.
- Imaging found 84/406 targeting sgRNAs and 3/50 controls with significant morphology/intensity effects.
- Transcriptional and morphological perturbation effects were positively correlated overall, but still captured different phenotypes (`paper.md:81-83`).

Biological examples:

- Zonation: perturbations in Wnt-related and metabolism-related genes shift periportal/pericentral expression programs. Spatial imaging suggests cells changed expression state without obvious migration or zone-specific survival changes (`paper.md:117-123`).
- Stress response: Sel1l knockout increases calreticulin and UPR gene expression while reducing abundant secretory mRNAs, suggesting an in vivo liver-specific stress adaptation (`paper.md:127-129`).
- Steatosis: Insig1, Eif2s1/Aars, and Pten perturbations converge on lipid-droplet accumulation but show distinct transcriptional programs (`paper.md:131-137`).

Figures 1-7 and Figure S4 visually support these claims: Figure 1/S4 define the workflow, Figure 2 establishes the reference atlas and morphology embeddings, Figure 3 validates screen calls, Figure 4 shows joint phenotype maps, and Figures 5-7 show biological discoveries from multimodal readouts.

### Code-Paper Match and Reproducibility

Overall code-paper fidelity is **medium**.

Code-verified exact or close matches:

- Fiducial registration and shift application (`registration.py:107-142`).
- Spot preprocessing, spot finding, and trace extraction (`spot_decoding.py:239-352`).
- XGBoost coding-vs-blank molecule classifier and 5% misidentification threshold (`barcode_classifier.py:10-112`, `merfish.py:313-338`).
- Cellpose segmentation orchestration and z-plane mask merging (`segment.py:33-205`, `cellpose_segment.py:15-146`).
- Molecule-to-cell assignment and AnnData export (`molecules.py:40-182`).
- Scanpy preprocessing, Harmony integration, Leiden clustering, and DE/correlation helpers (`sc_processing.py:14-142`, `perturbations.py:7-79`, `barcodes.py:58-91`).

Important gaps:

- The VQ-VAE/deep autoencoder implementation was not found in the checked-in repo search scope, despite being central to the morphology embedding analysis.
- The exact K=10 KNN label-transfer classifier described in the paper was not located; related nearest-neighbor and label-transfer helpers exist.
- The paper's tissue-zone segmentation rule is described in STAR Methods, but no direct implementation was found in searched source.
- Figure-level scripts for every statistic, including energy-distance tests and Benjamini-Yekutieli scoring, were not fully located.

The repository therefore supports substantial reuse of the imaging/analysis pipeline, but it is not a complete one-command reproduction package for all paper figures.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
