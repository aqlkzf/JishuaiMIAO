---
layout: default
permalink: /paper-atlas/hubmap-3d-human-reference-atlas-271d7b25/
title: "HuBMAP_3D_Human_Reference_Atlas"
nav: false
description: "人体图谱并不只是“收集很多单细胞数据”。真正困难的是：不同团队研究不同器官、采用不同实验技术、使用不同细胞命名和空间坐标，得到的数据彼此难以对齐。已有参考系往往只覆盖单个器官，例如 Waxholm Space 是发表于 Nature Methods 2023 的脑三维图谱；"
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
    <h1>HuBMAP_3D_Human_Reference_Atlas</h1>
    <p>Human BioMolecular Atlas Program (HuBMAP): 3D Human Reference Atlas construction and usage</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/cns-iu/hra-construction-usage-supporting-information" target="_blank" rel="noopener noreferrer" aria-label="Open code for HuBMAP_3D_Human_Reference_Atlas">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## HuBMAP 3D Human Reference Atlas 方法详解

### 1. 这篇论文究竟在解决什么问题？

人体图谱并不只是“收集很多单细胞数据”。真正困难的是：不同团队研究不同器官、采用不同实验技术、使用不同细胞命名和空间坐标，得到的数据彼此难以对齐。已有参考系往往只覆盖单个器官，例如 Waxholm Space 是发表于 *Nature Methods* 2023 的脑三维图谱；2019 年 *Cell* 的工作提出了全身 Common Coordinate Framework（CCF）的方向，但把解剖、细胞、标志物、三维位置、实验数据和软件基础设施真正连接起来，仍需要跨联盟的标准、工具与持续发布流程（`paper.md:14-20,360-361`）。

HuBMAP 的 Human Reference Atlas（HRA）要建立的是一个健康成年人体的“可计算参照系”：

- 在解剖尺度上知道器官、功能组织单位（FTU）和更细结构之间的包含关系；
- 在细胞尺度上知道某类细胞位于哪些结构、由哪些基因或蛋白标志；
- 在空间尺度上知道组织块在标准三维器官中的位置、大小和旋转；
- 在数据尺度上把转录组、空间蛋白组和组织学结果映射到共同术语；
- 在工程尺度上把图谱发布成知识图谱、文件、API 和可交互界面。

因此，这不是一个单模型论文，而是一套“标准化数据对象 + 空间注册 + 分子注释 + 图谱富集 + 发布基础设施”的联合方法。

### 2. HRA 的核心创新

#### 2.1 三棵相互连接的树

HRA 用 ASCT+B 表把三类知识连接起来：

1. **Anatomical Structures（AS）**：器官与组织结构的 `part_of` 层级；
2. **Cell Types（CT）**：细胞的 `is_a` 类型层级，以及细胞与结构的 `located_in` 关系；
3. **Biomarkers（B）**：用于识别细胞的基因、蛋白、代谢物、蛋白质形态和脂质。

每个对象尽量映射到 Uberon、FMA、Cell Ontology、PCL、HGNC 等稳定本体。没有正式本体项时先保留临时 ID，再通过社区流程补入本体。Fig. 1 的灰色交叉连线直观展示了各种二维/三维对象、OMAP、分割数据和注释参考如何回连到这三棵树。

#### 2.2 共同的三维空间参照

HRA 的 Registration User Interface（RUI）让专家把组织块放进标准三维器官，记录组织块的 UUID、尺寸、位置、旋转、相交的解剖结构以及操作者和日期。快速交互时使用包围盒碰撞，富集阶段再用表面网格计算更精确的相交体积（`paper.md:166-168,266-270,296-298`）。

空间注册的价值是：不同供体、不同实验和不同数据门户的组织块不再只是一个“lung”或“kidney”标签，而能落在同一器官模型中的可比较位置。

#### 2.3 多种实验路线最终汇聚到共同术语

HRA 不要求所有数据使用同一种实验技术，而是要求不同路线产出可以对齐的中间表示。

```text
sc/snRNA-seq:  cell × gene
      → Azimuth / CellTypist / popV
      → 细胞类型标签
      → cell type × gene 均值矩阵
                         ┐
                         ├→ ASCT+B / 本体术语 → HRA
空间蛋白组: 图像 + OMAP  ┘
      → 校正 / 拼接 / 细胞分割
      → 细胞类型注释
      → cell type × protein 均值矩阵
```

转录组工作流从 HuBMAP、SenNet、GTEx 和 CZ CELLxGENE 获取 H5AD 数据，按供体–数据集拆分，并通过三类注释工具生成细胞汇总及元数据。空间成像工作流则完成照明校正、背景扣除、拼接、细胞/细胞核分割，输出 OME-TIFF 和单细胞特征，再利用抗体通道与 OMAP 进行细胞类型注释（`paper.md:146-152,272-284`）。

跨技术或跨切片比较还需要空间配准。STalign（*Nature Communications*, 2023）把细胞位置栅格化，并通过仿射和微分同胚变换对齐结构匹配的图像；连续切片可由 MATRICS-A、SectionAligner 或 3DCellComposer 重建为三维组织体（`paper.md:286-292,474`）。

### 3. 从原始对象到可发布图谱

完整的数据生产链可以压缩为七步：

```text
① 专家编制 ASCT+B / OMAP / AVR / 2D-3D 对象
                         ↓
② 组织块三维注册并记录供体、样本和操作 provenance
                         ↓
③ 转录组注释或空间图像分割、注释、配准
                         ↓
④ 用 crosswalk 把工具标签映射到 HRA 与本体术语
                         ↓
⑤ 转换为 LinkML 结构，执行结构和语义验证
                         ↓
⑥ OWL 推理与外部元数据富集，构建 RDF 知识图谱
                         ↓
⑦ 生成 HRApop / HRAlit / VCCF，并通过 LOD、API、Portal 发布
```

其中第五步非常关键。LinkML 先检查字段、类型、URL 和缺失值；随后语义检查确认本体项真实存在、关系与 Uberon/CL 等可信本体一致。ASCT+B 还接受专家与 EBI 的严格审阅（`paper.md:324-326`）。富集阶段会把隐含的传递关系显式化、调用外部 API 补充元数据，并把标准化对象合并为 RDF/Turtle 图谱（`paper.md:116-126`）。

### 4. 两个重要的图谱富集结果

#### 4.1 HRApop：给解剖结构附上细胞群证据

一个数据集要进入 HRApop，必须同时满足：

1. 已通过 RUI 进行空间注册；
2. 有细胞类型群数据；
3. 来自经过质量控制的数据门户，或已经过同行评议发表。

HRApop v0.10.2 检查了 9,613 个单细胞转录组 H5AD 和 74 个单细胞蛋白组数据集，最终 553 个满足条件。论文用“注册位置和细胞群都已知”的数据优化与验证它，随后为缺失信息的数据预测细胞注释或空间来源，包括 2,004 个 HuBMAP、166 个 SenNet 和 4,789 个 CZ CELLxGENE 数据集（`paper.md:304-312`）。

#### 4.2 HRAlit：把图谱对象连接到论文、作者和资助

HRAlit 把 HRA 对象与 7,103,180 篇论文、583,117 位作者、896,680 个资助项目和 1,816 个实验数据集连接起来。论文报告的网络包含 8,694,233 个节点和 14,096,735 条边，可用于寻找领域专家、关键证据和资助趋势（`paper.md:300-302`）。

### 5. 两个 usage preview 怎么理解？

#### 5.1 肺组织 VCCF：细胞离血管有多远

Fig. 3a 比较健康肺与支气管肺发育不良（BPD）肺。每个非内皮细胞被连接到最近的血管内皮细胞核，图中用彩色“辐条”显示连接，并比较不同细胞类型的距离分布。

在本地 supporting code 中，二维距离被直接实现为

$$
d_{ij}=\sqrt{(x_i-x_j^{v})^2+(y_i-y_j^{v})^2}.
$$

脚本保留当前最小距离，搜索阈值初始为 250 个坐标单位；若未找到候选则写入 `-1`（`step_1_vccf_splitter_file.py:47-75`）。后续代码把细胞和血管坐标转换成多边形与连线，最后栅格化为多通道 OME-TIFF。

图像上，BPD 行在支气管和肺动脉附近显示更密集的细胞–血管连接与更靠近零点的距离分布。但该图没有给出样本量、置信区间或显著性检验，因此应理解为病例级生物学预览，而不是群体统计结论。

#### 5.2 肠道层级结构：从细胞到 FTU

Fig. 3b 把同一空间组织逐级抽象：

```text
细胞类型
  → n=10 邻近窗口聚类得到 neighborhood
  → n=100 窗口聚类得到 community
  → n=300 窗口聚类得到 major tissue unit / FTU
  → 用跨层网络显示组成关系
```

这一思路把局部细胞混合模式提升为更大的组织结构。图像能直观看到细胞类型、neighborhood、community 与 FTU 的四层连接，但没有展示参数敏感性、聚类稳定性或外部真值比较。对应实现位于论文列出的独立 repository，在当前 supplied snapshot 中为 `Not found`。

### 6. 论文如何验证 HRA？

这不是传统“方法 A 准确率高于方法 B”的 benchmark。证据主要来自四类：

- **规模与覆盖：** HRA v2.0 有 4,499 个独特解剖结构、1,195 个细胞类型、2,089 个标志物、33 张 ASCT+B 表和 65 个三维参考对象；
- **结构与语义质量：** LinkML、本体检查、专家和 EBI 审阅；
- **应用预览：** 肺 VCCF 与肠道层级组织分析；
- **真实使用：** 论文报告超过 119 万次 HRA Portal 请求、52 万次 API 请求，Azimuth 处理超过 3.66 亿个细胞（`paper.md:210-212`）。

补充表 1 同时揭示了覆盖不均：有些器官的 H5AD、三维结构或注释参考丰富，有些则很少甚至没有。因此，“器官出现在图谱中”不等于它已经拥有同等强度的实验和注释证据。

### 7. 代码与论文到底匹配到什么程度？

对完整论文而言，当前 acquired repository 的 fidelity 是 **low**；对 Fig. 3a 的二维肺 VCCF supporting path，则存在明确匹配。

直接核验到的五个 Python 文件完成：

```text
配置的肺细胞 CSV
  → 合并并标准化坐标/标签
  → 按区域拆分
  → 计算最近内皮细胞和距离
  → 生成细胞/连线几何与颜色
  → 写出多通道 OME-TIFF mask
```

主要复现风险包括硬编码 Windows 路径、固定文件名、`micro_per_pixel=1`、无随机种子的人造几何、硬编码细胞类型，以及缺少测试、环境锁文件和完整 workflow runner。Fig. 3a 的距离分布绘图与完整 Vitessce 配置也没有在 Mapper 限定范围内找到。

必须保留的边界是：当前快照没有定位到 atlas-wide DO/KG 构建、三维 VCCF、HRApop、Portal 微服务或 Fig. 3b 聚类实现。这些是 `Not found in supplied snapshot`，不能推断为论文列出的其他公开仓库也没有实现。

### 8. 最值得记住的三点

2. **多模态整合依靠“汇聚到共同表示”。** 不同实验不必共享原始格式，但必须映射到统一的细胞类型、标志物和空间对象。
3. **它的优势与复现难点来自同一件事：联邦化。** HRA 能整合 30 多个团队和 50 多个算法，也意味着完整复现依赖许多数据源、容器、API、云/本地资源和独立版本仓库。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## HuBMAP 3D Human Reference Atlas — Summary

### Problem

Human tissue atlases often use organ- or project-specific coordinates, vocabularies and processing pipelines. Waxholm Space, for example, is a 3D brain atlas reported in *Nature Methods* (2023), while colon work has used a one-dimensional distance reference; these systems do not generally map into a shared whole-body coordinate framework (`paper.md:14-16,360-361`). HuBMAP's Human Reference Atlas (HRA) addresses the larger integration problem: representing healthy adult anatomy from organs to cells and biomarkers, registering new tissue data in 3D, and making the resulting multimodal evidence computable and reusable.

### What the Paper Introduces

This *Nature Methods* (2025) Resource paper describes HRA v2.0 as a linked ecosystem of:

- expert-authored ASCT+B anatomy/cell/biomarker tables;
- ontology-aligned 2D FTU illustrations and 3D reference organs;
- OMAP antibody panels and validation reports;
- experimental datasets mapped by 3D tissue registration, transcriptomic cell annotation or spatial proteomic workflows;
- atlas-enriched products such as HRApop and HRAlit;
- linked-open-data releases, APIs, portals and a hybrid cloud/microservices infrastructure.

The sixth release covers 4,499 unique anatomical structures, 1,195 cell types and 2,089 biomarkers, with 33 ASCT+B tables and 65 3D reference objects (`paper.md:8-10`).

### High-Level Workflow

```text
expert digital objects + ontology mappings
                    │
experimental tissue → 3D registration / segmentation / cell annotation
                    │
            LinkML normalization
                    │
      structural + semantic validation
                    │
 OWL/metadata enrichment → HRA knowledge graph
                    │
 HRApop / HRAlit / VCCF → APIs and user interfaces
```

Transcriptomic cell-by-gene matrices are annotated with tools such as Azimuth, CellTypist and popV and aggregated into HRA-aligned cell-type/biomarker matrices. Spatial assays use validated panels, segmentation, annotation and optional 2D/3D alignment.

### Evaluation and Evidence

The paper evaluates the resource through scale, validation, adoption and usage previews rather than a conventional single-metric benchmark.

- **Atlas scale:** 1,192 modeled anatomical structures with 516 unique ontology IDs, 3,742 rendered cells in 22 FTUs, 13 OMAPs linked to 197 AVRs and 553 datasets used for HRApop (`paper.md:108-114`).
- **HRApop:** 553 of 9,687 considered transcriptomic/proteomic datasets met spatial, cell-population and quality criteria; HRApop was then used to predict missing annotation or spatial origin for 2,004 HuBMAP, 166 SenNet and 4,789 CZ CELLxGENE datasets (`paper.md:304-312`).
- **Validation:** LinkML structural checks, ontology-semantic checks and expert/EBI review are applied to HRA digital objects (`paper.md:324-326`).
- **Usage previews:** Fig. 3 shows nearest-vasculature cell-distance analysis in healthy versus BPD lung and a four-level cell-type → neighborhood → community → FTU representation in intestine (`paper.md:184-208,314-322`).
- **Operational use:** the paper reports 1,194,130 HRA Portal requests, 524,358 API requests and Azimuth processing of more than 366 million cells over the stated reporting windows (`paper.md:210-212`).

The figures support the architecture and workflow clearly, but the previews do not provide a conventional accuracy comparison, uncertainty analysis or population-level statistical test.

### Reproducibility and Code Match

**Reproducibility rating: 3/5.** Data, SOPs and code are broadly public, and Supplementary Tables 2–3 enumerate many repositories. The paper describes more than 50 algorithms from more than 30 teams, so reproduction requires a distributed software/data ecosystem rather than one repository.

The acquired snapshot at commit `18be7e5077d99b74e1e42079b1872c80ab4248aa` has **low fidelity to the full paper** but meaningful fidelity to one preview. Five verified Python files support the Fig. 3a 2D lung VCCF path: normalize cell CSVs, split regions, compute nearest endothelial cells, create link geometry/colors and write OME-TIFF masks. They use hard-coded Windows paths, fixed/hard-coded cell conventions and no verified workflow runner or tests. Code for atlas-wide construction, 3D VCCF, HRApop, portal services and Fig. 3b hierarchical clustering is `Not found` in this supplied snapshot; those components are distributed across other repositories listed by the paper.

### Main Limitations

- Organ, assay and cell-annotation coverage is uneven; Supplementary Table 1 includes organs with few or no supporting datasets or annotation references.
- Many anatomical structures and cell types remain unmapped or temporarily represented pending ontology additions (`paper.md:130-136,218-220`).
- Cell states and demographic representativeness are incomplete, and several 3D workflows remain under development.
- The full platform is operationally complex: reproducibility depends on external datasets, containers, cloud/on-premises services, APIs and many independently versioned repositories.
- The supplied supporting code demonstrates only a narrow 2D visualization path and cannot reproduce the complete HRA release.

### Bottom Line

The paper's contribution is a practical, extensible standard for connecting expert anatomy, molecular cell identities, spatial tissue registration and multimodal experimental data in one versioned human-body reference. Its strongest evidence is the breadth of linked resources, formal validation and real deployment. Its central reproducibility challenge is the same as its strength: HRA is a federated atlas infrastructure, not a self-contained algorithm package.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
