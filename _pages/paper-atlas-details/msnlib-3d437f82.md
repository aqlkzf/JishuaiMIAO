---
layout: default
permalink: /paper-atlas/msnlib-3d437f82/
title: "MSnLib"
nav: false
description: "MSnLib 不是一个新的预测模型，而是一个面向 untargeted metabolomics 的开放 MS^n^ 光谱资源和生成流程。它把化合物标准品、元数据清洗、正/负离子模式的高通量 Orbitrap MS^n^ 采集、mzmine 自动处理和开放数据发布串成一条流程，输出可用于小分子注释和机器学习训练的多级碎裂光谱库。"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>MSnLib</h1>
    <p>MS^n^Lib: efficient generation of open multi-stage fragmentation mass spectral libraries</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02813-0" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for MSnLib">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/corinnabrungs/msn_tree_library" target="_blank" rel="noopener noreferrer" aria-label="Open code for MSnLib">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MSnLib 方法中文解读

### 一句话概览

MSnLib 不是一个新的预测模型，而是一个面向 untargeted metabolomics 的开放 MS^n^ 光谱资源和生成流程。它把化合物标准品、元数据清洗、正/负离子模式的高通量 Orbitrap MS^n^ 采集、mzmine 自动处理和开放数据发布串成一条流程，输出可用于小分子注释和机器学习训练的多级碎裂光谱库。

### 1. 生物学问题与建模目标

代谢组学中，一个检测到的峰只有能匹配到可靠参考光谱时才容易解释。现有开放库主要是 MS2，公开 MS^n^ 数据很少；商业库虽然大，但不便开放下载和训练模型。MSnLib 的目标是扩大开放参考空间，而不是直接证明某个样本里的未知代谢物身份。

因此，这里的“建模目标”更准确地说是资源工程目标：让每个物理化合物标准品有干净结构元数据、可追踪的采集文件、经过质量控制的 MS^n^ tree，以及可导出的 `.json`、`.mgf`、`.msp` 光谱条目。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| 化合物元数据 | `metadata_file` | 标准品、plate/well、结构和名称信息 | `doc_code.md` |
| 唯一样本 ID | `unique_sample_id` | 连接元数据行和采集文件名 | `metadata_cleanup.py:123-158` |
| 清洗后结构 | SMILES/InChI/InChIKey | 用于质量、注释和库间比较 | `rdkit_mol_identifiers.py:127-178` |
| 单同位素质量 | `monoisotopic_mass` | mzmine 按 adduct/fragment 计算前体质量的基础 | `rdkit_mol_identifiers.py:84-89` |
| 采集序列表 | Xcalibur sequence CSV | 正/负离子模式采集任务 | `sequence_creation.py:68-143` |
| MS^n^ tree | MS1-MS5 fragmentation tree | 多级碎裂路径 | 论文 Fig. 1、Extended Data Fig. 2 |
| 光谱库条目 | JSON/MGF/MSP | 最终开放参考光谱 | 论文 Methods；

### 3. 方法主流程

1. 收集七个化合物库，覆盖天然产物、FDA 药物、生物活性化合物、scaffold、peptidomimetic 等来源。
2. 用 Python 清洗元数据：统一列名，生成 `library_plate_well_id` 形式的唯一 ID，去盐，标准化结构，计算 SMILES、InChIKey、logP、monoisotopic mass 等字段。
3. 可选查询 PubChem、ChEMBL、DrugBank、DrugCentral、LOTUS、Broad Institute、NPClassifier/ClassyFire 等资源；代码中这些查询由开关控制，有些本地/私有数据库默认关闭。
4. 用 `sequence_creation.py` 生成 Orbitrap/Xcalibur 采集序列表，让文件名包含唯一 ID，并分别跑 positive 和 negative ion mode。
5. 通过 dual-pump flow injection 和 data-dependent acquisition 采集 MS1 到 MS5 的碎裂树。Extended Data Fig. 3 显示高 AGC 和 60k resolution 对 MS3-5 信号质量有帮助。
6. 用 mzmine 导入 raw/mzML，做 mass detection、MS^n^ tree building、基于样本已知组成的 local database search、precursor purity 检查、spectral merging 和 library export。
7. 用 InChIKey first block、TMAP、UpSet、FBMN、MCES/Tanimoto 等方式评估覆盖范围和光谱质量。

### 4. 数学目标与直觉

论文没有编号公式，核心是几个规则化转换。

结构清洗后计算单同位素质量：

$$
\text{structure} \rightarrow \text{monoisotopic mass}, \text{InChIKey}, \text{SMILES}
$$

这个量不是学习出来的参数，而是把化合物结构转成 mzmine 可检索的质量和标识符。库间覆盖比较使用 InChIKey 的第一段，故意忽略 stereochemistry；这有利于大规模比较，但不能回答立体异构体是否都被覆盖。

光谱相似性使用 weighted cosine、m/z tolerance 和最少匹配 fragment 数；结构相似性使用 Tanimoto 和 MCES。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| 元数据准备和唯一 ID | `metadata_cleanup.py:46-101`, `metadata_cleanup.py:123-158` | 读表、创建 row/sample ID、缓存 parquet | ✓ Exact |
| 结构标准化和质量计算 | `rdkit_mol_identifiers.py:127-178` | 去盐、ChEMBL/RDKit 标准化、计算 identifiers | ✓ Exact |
| Prefect 编排和数据库查询 | `metadata_cleanup_prefect.py:260-397` | 按开关运行 PubChem/ChEMBL/DrugBank/LOTUS 等查询 | ✓ Exact |
| 采集序列生成 | `sequence_creation.py:68-143`, `sequence_creation.py:184-297` | 生成正/负离子 Xcalibur sequence CSV | ✓ Exact |
| TMAP/可视化 | `tmap_plotting.py:43-123` | 画 chemical-space projection | ~ Partial |
| MCES 结构相似性 | `my_mces.py:24-169` | 调用 myopic_mces 计算图编辑距离 | ✓ Exact |
| mzmine MS^n^ tree 生成和导出 | Not found | 论文链接到外部 `mzmine/mzmine3` 和补充 batch 文件 | ✗ Not found |

### 6. 结果如何解读

Fig. 1 证明流程结构清楚：元数据、采集、mzmine 处理三段互相衔接。Fig. 2 支持两个核心结论：正/负离子模式互补，MSnLib 与 GNPS、MoNA、MassBank EU、NIST23、mzCloud 相比有大量新增覆盖。Extended Data Fig. 3 支持采集参数优化，Extended Data Fig. 4 支持化学空间互补，Extended Data Fig. 5 支持 MCEBIO MS2 光谱在分子网络中的化学一致性。

这些结果能说明 MSnLib 是一个大规模、开放、互补的参考资源；不能说明它在所有真实样本上都能显著提高注释，也不能把未进一步调查的 microbial metabolite match 当作已验证发现。

### 7. 局限性与未验证部分

- 完整复现需要大规模原始数据、Zenodo/MassIVE 数据、mzmine batch/mzwizard 文件和很多 notebook，不是一个轻量级脚本可以重跑。
- 一些数据库查询需要本地文件或访问权限，代码默认关闭部分资源。
- `tmap_plotting.py` 等脚本含有 hardcoded Windows path，迁移运行需要改路径和准备数据。
- InChIKey first-block 比较会忽略 stereochemistry，因此覆盖结论不能过度解释成立体化学覆盖。

### 8. 快速阅读路线

1. 先读 `summary.md`，了解论文贡献和可复现性判断。
2. 再读 `doc_method.md`，按阶段理解从元数据到光谱库的完整流程。
3. 读 `doc_code.md`，区分哪些论文步骤由本地 Python 代码验证，哪些属于 mzmine/补充文件。
4. 读 `figure_analysis.md`，看每张图支持了什么、不能支持什么。
5. 最后查 `claude_notes.md`，看证据表、缺口和隐藏实现细节。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MSnLib

### Motivation And Novelty

MSnLib tackles a practical bottleneck in untargeted metabolomics: compound identification depends on reference spectra, but open resources contain abundant MS2 spectra and very limited public multi-stage fragmentation (`MS^n^`, `n > 2`) data. Proprietary libraries such as mzCloud contain large MSn collections, but their data are not openly downloadable for general tools or machine-learning training.

The novelty is not a new prediction model. MSnLib is a resource and workflow paper: it combines collaborative compound sourcing, Python metadata cleanup, high-throughput flow-injection Orbitrap MSn acquisition, automated mzmine processing, and open deposition. The resulting resource contains spectra for 30,008 unique compounds, with 357,065 MS2 and more than 2.3 million MSn spectra after merging/deduplication.

Compared resources include GNPS (Nature Biotechnology, 2016), MassBank (Journal of Mass Spectrometry, 2010), MoNA, mzCloud (commercial, accessed 2024), NIST23 (commercial, 2023), Wiley, METLIN (Analytical Chemistry, 2018), and prior spectral-tree work (Metabolomics, 2012; Rapid Communications in Mass Spectrometry, 2012; TrAC, 2015). The key limitation cited is not algorithmic accuracy alone, but scarcity and closed access of MSn reference data.

### Method Overview

The workflow has three main stages. First, compound metadata are cleaned and standardized. The local Python repository verifies this part: it creates unique sample IDs, removes salts, standardizes structures with RDKit/ChEMBL, computes identifiers and monoisotopic masses, and optionally enriches rows through public or local databases.

Second, cleaned metadata are used to generate positive and negative acquisition sequences for flow-injection Orbitrap MSn acquisition. The method uses pooled standards, short injections, dual-pump flow injection, optimized AGC/resolution settings, dynamic exclusion, and MS1-MS5 data-dependent fragmentation.

Third, mzmine imports raw/mzML data, builds MSn trees, annotates spectra against sample-constrained metadata, performs quality checks, merges spectra, filters weak spectra, and exports open library formats. This analysis did not verify mzmine Java source locally because the workspace acquired `corinnabrungs/msn_tree_library`, not `mzmine/mzmine3`.

### Evaluation

The paper evaluates MSnLib as a resource. It reports 87% coverage across the available compound libraries, 30,008 detected unique compounds, and more than 2.3 million MSn spectra. Fig. 2 shows that positive and negative ionization modes are complementary and that MSnLib contributes many compounds beyond open and commercial comparison libraries.

Extended figures support chemical-property diversity, acquisition design, method optimization, chemical-space coverage, and spectral-network quality. A public bacterial-culture dataset test shows that MSnLib adds 21 unique annotations beyond other combined open libraries, including 14 added drugs; seven possible microbial metabolites were not further investigated.

### Reproducibility

**Rating: 3/5.** The paper and repository provide useful public artifacts: open paper text, figures, a cloned metadata/sequence Python repository, Zenodo/MassIVE/GNPS data links, and supplementary batch/configuration files. The local code strongly supports metadata cleanup and sequence generation.

Reproducibility is limited because the full published resource requires large raw/library datasets, mzmine processing outside the acquired repository, optional private/local database access, and notebook-heavy analyses with hardcoded paths. A reader can understand and partially rerun the metadata/sequence layer, but recreating the complete 2.3-million-spectrum resource is a large experimental and computational effort.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
