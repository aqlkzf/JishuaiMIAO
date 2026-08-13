---
layout: default
permalink: /paper-atlas/lifetimehematopoiesis-36d0d4ea/
title: "LifetimeHematopoiesis"
nav: false
wide: true
description: "这篇论文最重要的认识是：人类 HSC 在一生中并不是简单地从“多能”线性走向“髓系偏向”，而是在“偏向某一条谱系的强度”和“同时访问全部谱系程序的总程度”两个不同维度上重排；胎儿 HSC 总体程序开放、单谱系偏向较弱，老年 HSC 总体预激活较低、但单谱系偏向更强。"
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
    <h1>LifetimeHematopoiesis</h1>
    <p>The dynamics of hematopoiesis over the human lifespan</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 人类全生命周期造血动态图谱：方法详解

### 这篇论文要解决什么问题？

人的造血系统并不是从胎儿到老年始终以同一种方式工作。胎儿期需要快速建立血液和免疫系统，儿童期淋巴细胞生成旺盛，成年后逐渐偏向髓系和红系输出，衰老又会改变造血干细胞（HSC）的数量、状态和疾病风险。

过去的单细胞研究通常只覆盖一个局部年龄段，例如胎肝、脐带血或成人骨髓。把不同实验室、不同技术和不同处理流程的数据直接拼在一起，会把“年龄差异”和“批次差异”混在一起。论文实际测试了 Harmony（*Nature Methods*, 2019）、Scanorama（*Nature Biotechnology*, 2019）、scVI（*Nature Methods*, 2018）、Seurat 集成（*Cell*, 2019）等方法；九个公开数据集经过校正后仍有很高的 kBET 拒绝率，也不能稳定恢复儿童期淋巴生成高峰。

因此，作者的核心策略不是提出新的批次校正算法，而是用尽可能一致的实验流程，重新构建一个覆盖人类几乎整个生命历程的 HSPC 单细胞图谱。

### 数据与主要产物

研究包含：

- 26 位供者；
- 22 个年龄时间点；
- 从受孕后 10 周到 77 岁；
- 胎肝、脐带血和出生后骨髓；
- 质控后保留 58,041 个 CD34⁺ 造血干/祖细胞和 40,618 个基因；
- 最终定义 22 个 HSPC 转录状态和 7 个年龄阶段。

七个年龄阶段是：第一孕期、第二孕期、围产期、儿童期、青春期、成人期和老年期。

### 整体计算流程

```text
统一处理的跨年龄 CD34+ 样本
        ↓
inDrop 单细胞测序与 GRCh38 比对
        ↓
逐样本归一化 → Seurat 集成 → PCA
        ↓
kNN/SNN 图 → Louvain 聚类 → 质控与注释
        ↓
58,041 个细胞、22 个 HSPC 状态的生命周期图谱
        ↓
┌──────────────────────────────────────┐
│ 状态比例/PCA                         │
│ PBA 与 StatOT 命运概率               │
│ cNMF 基因表达程序（GEP）             │
│ GEP 互斥关系与谱系分叉               │
│ 单谱系优势和总谱系预激活评分         │
└──────────────────────────────────────┘
        ↓
胎儿 CD69+ HSC 功能验证 + AML 年龄状态分析
```

### 第一步：构建统一的单细胞图谱

每个样本先归一化到每细胞 10,000 个转录本并做对数变换，再选择 2,000 个高变基因。Seurat 集成使用 2,000 个 anchors 和 30 个维度；随后用前 30 个主成分建立 10 近邻图，并以 Louvain SNN、分辨率 0.8 聚类。

作者先去除平均检测基因数低于 400、UMI 低于 1,000、线粒体比例高于 15% 的低质量簇，又去除表达 *ALB* 或 *LYVE1* 的肝细胞/内皮污染簇。31 个初始簇根据表达和丰度合并为 22 个最终状态。DoubletFinder 预测约 6.8% 的潜在双细胞，但去除后主要 UMAP、谱系结构和 marker 基本不变。

图谱显示，所有年龄大体共享同一个分化流形，但不同区域的细胞密度随年龄改变：

- 早期胎儿偏髓系；
- 第二孕期 HSC/MPP 扩增；
- 出生时红系比例下降；
- 儿童期淋巴生成显著增强；
- 成年后逐渐偏髓系、红系和巨核系；
- 老年期 HSC/MPP 比例再次增加。

这说明年龄主要改变“各种状态被使用的比例”，而不是每个年龄都产生一套完全独立的分化结构。

### 第二步：用 PBA 和 StatOT 推断命运概率

论文用两个不同模型估计单细胞向各终末谱系分化的概率。

#### PBA

Population balance analysis 把细胞表达状态构成一个 (k=20) 的近邻图，并指定七类终末“sink”。主要输入是：

- 细胞 × 基因表达矩阵；
- 细胞 × 谱系 sink 矩阵；
- 扩散常数 (D=0.2)。

初始 sink 通量设为

$$
f_{0,l}=\frac{1}{D}.
$$

之后迭代调整每个谱系的通量，使预测的总命运概率接近观察到的终末谱系比例。每个细胞最终得到被各谱系 sink 吸收的概率。

#### StatOT

Stationary optimal transport 把系统描述为带细胞增殖/死亡的稳态扩散—漂移过程，输出细胞到细胞的转移矩阵。作者对每个年龄点设置总计 100 个 sinks，在 50 维 PCA 空间中计算耦合，并令熵正则化参数为

$$
\epsilon=\bar{C},
$$

其中 \(\bar{C}\) 是代价矩阵的平均值。

PBA 和 StatOT 得到相近的年龄趋势：早期胎儿髓系概率较高，儿童期淋巴概率较高，成年后再次偏髓系，老年红系概率上升。需要注意，两者使用同一批细胞和相同的终末 sink，因此“一致”表示跨模型稳定性，并不是完全独立的实验验证。

### 第三步：用 cNMF 提取基因表达程序

作者在未集成的表达矩阵上运行 cNMF，以避免丢失基因。根据稳定性和误差曲线，选择 35 个成分，local-density threshold 为 0.15。每个程序包含一组基因贡献分数，每个细胞则有 35 个 GEP usage 分数。

其中六个主要程序对应：

- 单核/树突细胞；
- 巨核细胞；
- 嗜碱/肥大细胞；
- 淋巴细胞；
- 粒细胞；
- 红细胞。

这些“核心谱系 GEP”在不同年龄仍然存在，但它们会与年龄特异的辅助程序合作。例如儿童期淋巴辅助程序富含增殖、核酸代谢、高迁移率族蛋白、泛素和微管相关基因；第一孕期则出现辅助单核细胞程序。

### 第四步：寻找随年龄变化的谱系基因

对在至少 3% 谱系相关细胞中表达的基因，作者在每个年龄计算“基因表达—命运概率”的相关系数。设某基因在各年龄的相关系数为 (c_g(t_i))，先用三次样条拟合 (s_g(t))，再计算

$$
V_g=\int \left(s'_g(t)\right)^2dt.
$$

这个量衡量该基因与谱系命运的关系随时间变化得有多剧烈。论文称其为“Sobolev norm”，但实际上只用了导数的 (L_2) 项，而不是完整的 Sobolev 2-范数。

低 (V_g) 的基因更像贯穿一生的核心谱系基因；高 (V_g) 的基因则可能只在某个年龄窗口参与谱系承诺。

### 第五步：从 GEP 互斥关系推断谱系分叉

作者把细胞分成 HSC、MPP 和更晚期祖细胞三层。在每个年龄、每一层内，计算六个谱系 GEP 两两之间的 Pearson 相关。Bonferroni 校正后 (P<0.05) 的负相关被视为两个谱系程序不能同时高使用，由此画出“最小可能分叉图”。

这不是直接的谱系追踪。它只说明哪些谱系程序在转录层面出现互斥。论文也承认，这种方法没有考虑某一谱系占绝对优势的情况，可能高估祖细胞的真实潜能。

老年祖细胞几乎没有显著的 GEP 负相关，提示谱系隔离变弱。作者用单细胞克隆培养进行验证：成人祖细胞大多产生一到两个谱系，而老年祖细胞更常产生三到五个谱系。这为“老年祖细胞转录分叉减少、功能潜能更宽”提供了独立证据。

### 第六步：区分“单谱系偏向”和“总预激活程度”

设细胞 (i) 的六个谱系 GEP usage 为 (u_{i,l})，其中最大值为

$$
m_i=\max_l u_{i,l},
$$

其余五个 usage 的平均值为 \(\bar{u}_{i,-\max}\)。

除法型单谱系优势分数为

$$
R_i=\frac{m_i}{\bar{u}_{i,-\max}},
$$

减法型分数为

$$
S_i=m_i-\bar{u}_{i,-\max},
$$

总谱系预激活分数为

$$
T_i=\sum_{l=1}^{6}u_{i,l}.
$$

除法型分数更适合回答“一个 HSC 是否明显偏向某条谱系”；减法型分数更适合回答“它的绝对承诺程度有多强”。Extended Data Fig. 6 中，除法型 GEP 分数与胎儿、成人、老年克隆输出的年龄级别趋势高度一致（(R^2=0.9258)），减法型则几乎不相关（(R^2=0.0036)）；但减法型更能区分 HSC 与祖细胞的总体承诺程度。

关键发现是：

- 胎儿 HSC 的单谱系优势较低，但六个谱系程序的总使用量高；
- 老年 HSC 更容易明显偏向一个谱系，但总 GEP 使用量较低。

因此，“更偏向某一谱系”不等于“整体分化预激活更强”。

### 第七步：发现并验证胎儿特异 HSC 状态

cNMF 找到一个中孕期高使用的 fetal-HSC-GEP 和一个老年高使用的 elderly-HSC-GEP。fetal-HSC-GEP 与 *CD69* 表达相关。

由于 CD69 也可能是激活或组织处理造成的，作者做了多层验证：

1. 该程序在中孕期而不是最早处理样本达到高峰；
2. 在六个独立人类数据集和小鼠数据中复现；
3. 出生后这些 GEP 基因附近的 DNA 甲基化更高；
4. 直接分选胎儿 CD69⁺ 与 CD69⁻ HSC/MPP 做功能实验。

CD69⁺ 细胞在限制稀释培养中有更高克隆形成率和更多多谱系克隆；移植到 NSG 小鼠后，CD69⁺ 细胞在更低剂量下仍能长期植入，并产生更多多谱系输出。

这部分是论文最强的因果链条：计算程序 → 可分选表面标志 → 体外克隆功能 → 体内移植功能。结论应表述为 CD69 富集高功能胎儿 HSC，而不是 CD69 是所有年龄通用的纯 HSC 标志。

### 第八步：把正常年龄状态投射到白血病

作者用正常图谱训练 SingleCellNet 分类器，再分析 AML 和 B-ALL。B-ALL 主要对应淋巴祖细胞状态，AML 则表现出较强的髓系和祖细胞异质性。

对 257 个 BeatAML 样本，分类器给出胎儿、围产、儿童、成人和老年相似度。层次聚类分成“老年富集”和“混合年龄”两类；这两类患者的实际年龄分布相近，但混合年龄 AML 生存更差。

图中使用的年龄复合分数可写为

$$
A=\frac{a_{adult}+a_{pediatric}+a_{perinatal}+a_{fetal}}{a_{elderly}}.
$$

此外，七个转录因子形成

$$
TF=\frac{DLX2+NPAS1+ZFX}{ARNT2+BNC2+NPAS3+RORB}.
$$

BeatAML 中年龄分数和 TF 分数都能分层生存；但 TCGA 中只有年龄分数明显复现（(P=0.02)），TF 分数仅为趋势（(P=0.07)）。而且阈值是在 BeatAML 中反复搜索、选择生存差异最显著的值，存在过拟合风险。因此它们目前是研究型关联指标，不是可直接临床使用的固定模型。

### 可重复性与缺口

可获得的资源包括：

- dbGaP 原始数据：`phs002750`；
- GEO 处理后数据：`GSE189161`；
- 在线浏览界面：`https://lifetimecd34.hlilab.org`；
- 主文 Methods 和 Supplementary Notes；
- 各第三方工具的公开实现。

但论文明确说明没有生成新代码，也没有发布该研究自己的端到端分析仓库。当前来源中没有找到：完整 marker/sink 列表、PBA 通量更新与停止条件、GEP 时间多项式次数、Sobolev 数值积分细节、固定 AML 阈值、运行环境锁定文件和生成全部图的脚本。

因此，这项工作的数据资源和概念分析具有较高复用价值，但若要逐图精确重现，需要重新搭建大量研究专用流程。

### 一句话理解

这篇论文最重要的认识是：人类 HSC 在一生中并不是简单地从“多能”线性走向“髓系偏向”，而是在“偏向某一条谱系的强度”和“同时访问全部谱系程序的总程度”两个不同维度上重排；胎儿 HSC 总体程序开放、单谱系偏向较弱，老年 HSC 总体预激活较低、但单谱系偏向更强。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## The dynamics of hematopoiesis over the human lifespan

### Problem

Human hematopoietic stem and progenitor cells (HSPCs) must change their lineage output as physiological demands shift from fetal development through childhood, adulthood and aging. Previous single-cell studies covered restricted age windows, making it difficult to distinguish genuine lifespan biology from differences in tissue handling, sequencing and analysis.

The authors first demonstrate this limitation empirically. They aggregate nine published HSPC scRNA-seq datasets and test five integration approaches, including Harmony (*Nature Methods*, 2019), Scanorama (*Nature Biotechnology*, 2019), scVI (*Nature Methods*, 2018) and Seurat integration (*Cell*, 2019). All retain high kBET rejection rates and fail to recover expected features such as the childhood lymphoid surge. The central response is therefore not another batch-correction algorithm, but a uniformly generated atlas sampled across almost the entire human lifespan.

### What the paper contributes

The study profiles 26 donors at 22 timepoints from 10 postconception weeks to age 77. After quality control, the atlas contains 58,041 CD34⁺ HSPCs and 40,618 genes, organized into 22 transcriptional states and seven age phases.

The analysis combines several established tools:

- Seurat-based normalization, integration, PCA, kNN/SNN graph construction and Louvain clustering;
- SingleCellNet (*Cell Systems*, 2019) for state validation and atlas-to-leukemia transfer;
- cNMF (*eLife*, 2019) for gene-expression programs (GEPs);
- population balance analysis (PBA; *PNAS*, 2018) and stationary optimal transport (StatOT; *PLoS Computational Biology*, 2021) for fate probabilities;
- correlation and spline-derivative (“Sobolev norm”) analyses for age-varying lineage genes;
- clonal culture and xenotransplantation for functional validation.

The novelty lies in their coordinated use on a lifespan-spanning, uniformly processed dataset and in the derived distinction between lineage dominance and total lineage priming.

### High-level method

```text
uniformly processed CD34+ specimens across age
          ↓
58,041-cell integrated atlas and 22 HSPC states
          ↓
state abundance + PBA/StatOT fate probabilities
          ↓
cNMF lineage programs and age-dependent GEP usage
          ↓
GEP anticorrelations → inferred lineage branching
          ↓
dominance / total-priming scores
          ↓
fetal HSC state validation + leukemia age-state transfer
```

The atlas shows a non-monotonic sequence of hematopoietic priorities: early fetal myeloid output, midgestation HSC/MPP expansion, a perinatal/childhood lymphoid program, increasing adult myeloerythroid output and elderly HSC/MPP expansion.

cNMF yields 35 programs, including six lineage GEPs. Core lineage programs remain recognizable across life, but auxiliary programs are recruited at particular ages. A pediatric lymphoid program contains proliferation and nucleic-acid-metabolism genes, while an early fetal monocyte program accompanies first-trimester myeloid output.

PBA and StatOT independently produce similar age-dependent fate patterns. The two models use the same cells and terminal sink definitions, so their agreement is best viewed as cross-model consistency rather than independent validation.

The paper then defines two lineage-dominance scores for a cell's six lineage-GEP usages: a ratio of the largest usage to the average of the other five, and a subtraction of that average from the largest usage. The total-priming score is the sum of all six usages. This reveals that fetal HSCs have relatively low single-lineage bias but high total lineage-program access, whereas elderly HSCs have higher single-lineage dominance but lower overall priming.

### Main evidence and results

#### 1. A coherent lifespan atlas

The UMAP preserves shared lineage topology across ages while the density of states changes substantially. State-composition PCA separates childhood, fetal/perinatal and adult/elderly programs. Marker expression and SingleCellNet comparisons support the 22 state annotations.

#### 2. Age-specific lineage fate and branching

PBA and StatOT recover high early-fetal myeloid probability, childhood lymphoid probability, a later shift back toward myeloid output and increased elderly erythroid probability. Pairwise anticorrelations between lineage GEPs are used to construct minimal branching maps at HSC, MPP and progenitor levels.

Elderly progenitors have few significant lineage-GEP anticorrelations, suggesting weaker transcriptional segregation. A clonal assay supports broader functional potency: adult progenitors mostly generate one or two lineages, whereas elderly progenitors more frequently generate three to five.

#### 3. A fetal CD69-associated HSC state

cNMF identifies fetal- and elderly-enriched HSC programs. *CD69* marks the fetal program. Because CD69 can respond to activation or processing, the authors test the signal in independent datasets, mouse HSPCs and methylation data, then prospectively isolate fetal CD69⁺ and CD69⁻ Lineage⁻CD34⁺CD38⁻ cells.

CD69⁺ fetal cells are more clonogenic, produce more multilineage colonies and engraft NSG mice more efficiently with more multilineage output. This is the strongest mechanistic result: a computationally identified program leads to a prospectively isolated, functionally distinct fetal HSC-enriched population.

#### 4. Developmental age signatures in leukemia

SingleCellNet classifiers trained on the normal atlas divide 257 BeatAML tumors into elderly-enriched and mixed-age transcriptional states, independently of the patient's chronological age. Mixed-age AMLs have worse survival. A ratio combining fetal, perinatal, pediatric and adult similarity relative to elderly similarity strengthens the separation.

Seven transcription factors define another score associated with BeatAML survival. In TCGA, the atlas-derived age score replicates ((P=0.02)), whereas the TF score shows only a trend ((P=0.07)). The robust conclusion is therefore that normal developmental-age programs have prognostic association in AML; the seven-TF score is less secure.

### Important limitations

- The atlas is cross-sectional across different donors, not longitudinal within individuals.
- Childhood sampling is sparse, and donor cell counts are unequal.
- GEP anticorrelation infers minimal compatible branching states; it is not lineage tracing and may overestimate progenitor potency.
- PBA requires hand-adjusted sink fluxes, and the paper does not report the full update rule, stopping criterion or sink-marker list.
- The paper calls one GEP comparison “Spearman correlation” but describes computing Pearson correlation, leaving a textual ambiguity.
- The best-fit polynomial degree for GEP-age curves and numerical details for the spline/Sobolev calculation are not reported.
- AML and TF thresholds were chosen iteratively to maximize survival significance in BeatAML, creating an overfitting risk. Only the age score clearly replicates in TCGA.
- The paper-specific glue code, notebooks, exact environment and random seeds were not released.

### Reproducibility

**Rating: 3/5 — reusable data and substantial method detail, but incomplete exact re-execution.**

Available resources include raw sequencing data in dbGaP (`phs002750`), processed data in GEO (`GSE189161`), a navigable web interface (`https://lifetimecd34.hlilab.org`), detailed Methods and Supplementary Notes, and public third-party implementations of the major tools.

However, the paper states that no new code was generated. There is no paper-owned analysis repository, no end-to-end scripts for reproducing the figures, and several paper-specific choices are incompletely specified. The atlas is strong as a biological reference and starting point for new analysis, but exact figure-level reproduction would require reconstructing substantial workflow logic.

### Bottom line

This work provides a coherent single-cell reference of human HSPC maturation from early gestation to old age. Its most useful conceptual contribution is that “lineage bias” and “total priming” are separate axes: fetal HSCs broadly access lineage programs with relatively little single-lineage dominance, whereas elderly HSCs show stronger individual-lineage bias but weaker total priming. The CD69 functional experiments give biological weight to the computational atlas, while the AML analysis demonstrates a promising—though still exploratory—disease application of developmental age states.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
