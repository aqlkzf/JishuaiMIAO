---
layout: default
permalink: /paper-atlas/igof-perturb-seq-astrocyte-tf-atlas-43bfcbbe/
title: "iGOF-Perturb-seq astrocyte TF atlas"
nav: false
description: "iGOF-Perturb-seq 的核心是：用带条形码的 AAV 在活体星形胶质细胞中逐一过表达 TF，以单核转录组读出每次扰动，再把单 TF 的 DEG 汇聚为共同基因程序和疾病方向，最后用功能实验与 5XFAD 模型检验最重要的预测。 它最大的贡献既是 955 个 TF 的功能图谱，也是把“高通量状态预测”推进到“动物体内因果验证”的完整链条。"
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
      <span>Perturbation Resources</span>
      <span>Science · 2026</span>
    </div>
    <h1>iGOF-Perturb-seq astrocyte TF atlas</h1>
    <p>Mapping transcription factor functions in astrocytes using in vivo gain-of-function Perturb-seq</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1126/science.adw2156" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for iGOF-Perturb-seq astrocyte TF atlas">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/shendurelab/single-cell-ko-screens" target="_blank" rel="noopener noreferrer" aria-label="Open code for iGOF-Perturb-seq astrocyte TF atlas">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 在活体星形胶质细胞中给转录因子逐一“加油门”：iGOF-Perturb-seq 方法解读

论文：*Mapping transcription factor functions in astrocytes using in vivo gain-of-function Perturb-seq*（Science, 2026；DOI: `10.1126/science.adw2156`）

### 1. 这项工作真正要解决什么问题

传统 Perturb-seq 多用 CRISPR 敲除或抑制来问“缺少某个基因会怎样”。但许多转录因子在成年星形胶质细胞中的基础表达很低，继续向下敲未必能产生容易检测的表型；而疾病状态又常常伴随转录因子异常激活。因此本文反过来做 **gain-of-function（GOF）**：把一个转录因子的开放阅读框（ORF）送入单个星形胶质细胞，再用单核 RNA 测序读取该细胞的转录反应。

最终得到的不是一张简单的“TF—靶基因”表，而是三层地图：

1. 每个 TF 扰动引起哪些差异表达基因；
2. 多个 TF 是否收敛到共同的通路、基因程序和细胞功能；
3. 哪些 TF 能把炎症或阿尔茨海默病模型中的星形胶质细胞状态推向更有利的方向。

这里的“活体”很重要：AAV 在小鼠脑内感染星形胶质细胞，转录组是在真实组织环境中读取的，而不是只在培养皿中筛选。

### 2. 输入、输出与总体流程

输入是约 1200 个小鼠转录因子 ORF。每个 ORF 后连接一个唯一的 16 bp 条形码；论文最终获得 1089 个序列正确的构建。长读长测序用于确认“哪个条形码对应哪个 TF”，超过 93% 的条形码能以高于 80% 的准确率完成配对，九个不可靠构建被移除。

每个 AAV 构建同时携带：

- 受短 GFAP 启动子 `gfaABC(1)D` 驱动的 TF ORF，使表达偏向星形胶质细胞；
- ZsGreen 报告基因；
- 可在单核 RNA 测序数据中捕获的 TF 条形码。

AAV-PHP.eB 经眶后静脉注射进入成年小鼠，剂量为每只约 $2.5\times10^{11}$ 个病毒颗粒。论文估计约 10% 的 ACSA-2 阳性星形胶质细胞被感染。之后分离细胞核，同时读取转录组和 TF 条形码，建立“细胞—扰动—转录表型”的对应关系。

### 3. 为什么必须先筛出单扰动细胞

一个细胞可能同时收到多个病毒。如果直接把它归给读数最高的 TF，第二个 TF 的效应就会混进来。论文因此只保留推断为 MOI=1 的细胞。本地 Zenodo 脚本 `1MOI_cell_calling/pipeline.all.sh` 给出的核心规则是：

$$
R_1 \ge 2,\qquad \frac{R_1}{R_2} \ge 1.5,
$$

其中 $R_1$ 和 $R_2$ 是该细胞中第一、第二高 TF 条形码的 reads 数。通过这一过滤后，初始约 40 万个高质量细胞档案缩减为 130,341 个单扰动细胞。其中约 95% 是星形胶质细胞，包括 1,167 个 ZsGreen 对照和 121,807 个 TF 扰动星形胶质细胞，覆盖 955 个 TF，平均每个 TF 约 130 个细胞，但最少的 TF 只有 3 个细胞。

这个尾部样本量是解释结果时的重要边界：平均覆盖度不错，不代表每个 TF 的统计强度都相同。

### 4. 从单个 TF 到差异表达签名

对每个 TF，作者把携带该 TF 的星形胶质细胞与 ZsGreen 对照比较。本地 `zenodo_code/DEGs_calling_pathway_correlation/getDEGs.r` 直接调用 Seurat v5 的 logistic-regression 检验，并设置：

- `logfc.threshold = 0.15`
- `min.pct = 0.25`
- `test.use = "LR"`

可把每个基因的比较概念化为：

$$
\log\frac{P(Y=1)}{1-P(Y=1)}=\beta_0+\beta_1 x_g+\cdots,
$$

其中 $Y$ 表示细胞属于 TF 扰动组还是对照组，$x_g$ 是基因 $g$ 的表达；$\beta_1$ 检验该基因是否与扰动身份相关。论文部分汇总使用原始 $P<0.05$ 和表达方向来定义签名，而不是始终采用严格的多重检验校正，因此大规模跨 TF 比较时应把这些结果理解为候选效应，而非所有基因都已获得同等强度的确认。

另一个技术偏差来自 AAV 包装：较长的 TF ORF 在质粒库、病毒包装和感染后的细胞中逐步耗损。因此“某个长 TF 没有明显效应”可能包含递送效率不足，而不一定表示它没有生物功能。

### 5. 先用已知星形胶质细胞功能检验筛选是否可信

作者没有只展示转录组聚类，而是选取预测命中做功能实验：

- 突触形成：Fam170a、Zfp319、Nkx2-1 增强，Carhsp1、Tfap2e、Dmrtc2 减弱；
- 谷氨酸摄取：Rora、Zfp639、Zbtb6 被实验验证；
- 突触体吞噬：Meis2、Zfp688、Erf1 被验证，Meis2 还在体内显示对 PSD95 阳性突触物质吞噬的影响。

对 Zfp319、Zfp639 和 Meis2 的 loss-of-function 实验产生与过表达相反的表型。这种“GOF 预测—功能测量—LOF 反向验证”链条比只看 DEG 更有说服力，因为它说明筛到的 TF 不只是改变一些 marker，而是真正影响星形胶质细胞功能。

### 6. cNMF：把 955 个 TF 压缩为可解释的共同程序

若逐个阅读 955 份 DEG 列表，很难看出 TF 之间的共同机制。作者使用 consensus non-negative matrix factorization（cNMF），把非负表达矩阵近似分解为：

$$
X\approx WH,
$$

其中 $W$ 描述每个细胞使用各个基因程序的强度，$H$ 描述每个程序由哪些基因组成。再根据 TF 扰动后对程序的推动方向，把 TF 归纳为五类共功能模块：

1. 星形胶质细胞身份与基础功能；
2. 神经退行性疾病相关程序；
3. 星形胶质细胞—神经元相互作用；
4. 免疫程序；
5. 癌症相关程序。

这里的模块不是“TF 直接结合了同一批靶基因”的证明；它首先表示这些 TF 在转录表型上收敛。完整 cNMF 执行代码未在当前本地 Zenodo 解包范围中找到，因此该部分可按论文理解方法和结果，但不能仅凭当前代码目录逐命令复现。

### 7. 通路相似性与 hdWGCNA：从两条路线找 TF 组合

作者又从通路层面比较每个 TF。DEG 经 WebGestalt、g:Profiler 或 DAVID 做富集；局部分析还用 UCell 分别计算上调和下调基因集分数，并取净活性：

$$
S_{\text{net}}=S_{\text{up}}-S_{\text{down}}.
$$

本地 `eachTF_perturbation_correlation.analysis.kegg.r` 读取各 TF 的 KEGG 富集结果，构建通路向量并计算 TF 间相关性。这样可识别“基因不同但落在相同功能通路”的扰动。

论文还使用 hdWGCNA 建立共表达网络。若两个基因的表达相关系数为 $r_{ij}$，邻接强度可概括为：

$$
a_{ij}=|r_{ij}|^{\beta},\qquad \beta=3.
$$

分析保留至少 5% 细胞表达的基因，以 $k=25$ 聚合 metacell，并在样本间做协调，最终得到五个共表达模块和六个 TF 簇。通路相关性问的是“功能输出是否相似”，WGCNA 问的是“基因是否形成稳定的共表达网络”，两者互相补充。当前 Zenodo 目录仅保留 WGCNA 说明或不完整入口，没有足够执行文件重建论文全部 hdWGCNA 流程，因此对应关系为 Partial。

### 8. 从健康图谱转向疾病候选 TF

作者将 iGOF 签名与公开疾病单细胞数据中的星形胶质细胞状态比较，用来预测哪些 TF 可能推动或逆转疾病相关表达程序。这一步是相关性匹配：如果某 TF 的 GOF 签名与疾病状态同向，它可能是状态驱动者；若反向，则可能是干预候选。它不能单独证明因果，所以后续专门设计了炎症筛选和疾病模型验证。

在 LPS 诱导的炎症环境中，作者对候选 TF 再做一轮 iGOF-Perturb-seq，并根据免疫通路及反应性星形胶质细胞 marker 的下调程度排序。本地 `subTFs_Perturb-seq_under_LPS/LPS.rankMerge_down.plot.r` 能看到候选排序、通路和 marker 汇总逻辑。Ferd3l 因能压低炎症/反应性程序而被选中。

### 9. Ferd3l 在 5XFAD 模型中的验证意味着什么

作者在 5XFAD 阿尔茨海默病小鼠中进行脑范围、星形胶质细胞偏向的 Ferd3l 过表达。结果包括：

- Y-maze 与新物体识别行为改善；
- C3、GFAP 等反应性指标下降；
- 神经元损失和 Aβ 相关病理减轻；
- 单核 RNA 测序显示神经毒性星形胶质细胞比例、炎症程序以及部分异常细胞通信下降。

相反，在炎症或 5XFAD 背景下降低 Ferd3l 会使表型恶化。这支持 Ferd3l 对疾病相关星形胶质细胞状态具有因果调节作用。不过结论仍限于小鼠模型和本文递送条件，不能直接外推为已经证实的人类治疗靶点。当前本地代码包也未找到完整的 5XFAD 行为学、下游单核分析与 CellChat 执行脚本，因此论文证据存在，但代码复现状态应标为 Not found。

### 10. 直接靶点与网络枢纽如何区分

论文用 CUT&Tag 辅助区分直接和间接效应：若 DEG 同时对应于 TF 结合峰，并且该峰位于转录起始位点上下游约 5 kb 内，则视为直接候选靶基因；其余 DEG 属于间接候选。本地 `TFs_target_gene_analysis/cutTag_deg_overlap_analysis.R` 实现了峰—基因窗口重叠与 DEG 合并。

随后用 STRING 构建蛋白互作网络，保留 combined score 不低于 400 的边，并结合多种中心性指标寻找共用 hub gene。本地 `moduleTFs_cohubGene_identification/identify_co_hub_genes.v3.R` 可对应这部分。需要注意，CUT&Tag 的近 TSS 重叠和 STRING 网络都提供“候选机制”，并不等价于逐一完成了结合位点功能验证。

### 11. 代码来源纠错与实现对应关系

这个工作区原先把 `single-cell-ko-screens` 记为主代码仓库，这是一个来源错配。该 GitHub 仓库是 Shendure/Trapnell 的通用单细胞 KO 筛选条码工具；其中 `get_barcodes.py` 可解释通用条码抽取，但不是本文全套 iGOF 分析代码。

本文特异的主代码证据来自 Zenodo record `17622140`，本地目录为 `zenodo_code/`。据此，代码—论文对应关系应写成：

| 论文环节 | 本地证据 | 对应程度 |
|---|---|---|
| 条形码抽取工具 | `single-cell-ko-screens/get_barcodes.py` | Partial，通用辅助工具 |
| 单扰动/MOI 判定 | `zenodo_code/1MOI_cell_calling/pipeline.all.sh` | Exact |
| TF 对照 DEG | `zenodo_code/DEGs_calling_pathway_correlation/getDEGs.r` | Exact |
| KEGG 通路相似性 | `zenodo_code/DEGs_calling_pathway_correlation/eachTF_perturbation_correlation.analysis.kegg.r` | Exact |
| LPS 候选排名 | `zenodo_code/subTFs_Perturb-seq_under_LPS/LPS.rankMerge_down.plot.r` | Exact/Partial，核心排名可见 |
| CUT&Tag—DEG 重叠 | `zenodo_code/TFs_target_gene_analysis/cutTag_deg_overlap_analysis.R` | Exact |
| PPI hub 分析 | `zenodo_code/moduleTFs_cohubGene_identification/identify_co_hub_genes.v3.R` | Exact |
| cNMF 全流程 | 当前本地解包范围未找到 | Not found |
| 完整 hdWGCNA 流程 | 仅说明或不完整入口 | Partial |
| 5XFAD 下游与 CellChat | 当前本地解包范围未找到 | Not found |

因此，这个工作区的总体代码忠实度应评价为 **中等**：关键的 MOI、DEG、通路、LPS、CUT&Tag 和 PPI 分析有直接脚本，但并非论文全部结果都能从当前归档一键重跑。

### 12. 阅读结果时必须保留的边界

1. 一个 TF 只选择一个 ORF/异构体，不能覆盖该基因所有剪接形式。
2. 短 GFAP 启动子和 PHP.eB 的区域、细胞亚型及物种偏好会影响覆盖；“全脑”样本也不等于所有脑区均匀采样。
3. 条形码是病毒构建的代理读数，不是 TF 蛋白表达的直接测量，可能出现误归属或表达失败。
4. 长 ORF 的递送耗损会造成 TF 间不均衡。
5. 每个 TF 的细胞数差异很大，最少只有 3 个细胞；弱覆盖 TF 的阴性结论尤其谨慎。
6. 部分筛选阈值使用原始 $P$ 值，大规模比较存在多重检验风险。
7. 转录相似性、峰附近重叠和 PPI 网络都用于提出机制，不应自动写成已证实的直接调控。
8. Ferd3l 的强验证来自小鼠 LPS 与 5XFAD 模型，尚不能直接推出人类疗效。

### 13. 一句话抓住这套方法

iGOF-Perturb-seq 的核心是：**用带条形码的 AAV 在活体星形胶质细胞中逐一过表达 TF，以单核转录组读出每次扰动，再把单 TF 的 DEG 汇聚为共同基因程序和疾病方向，最后用功能实验与 5XFAD 模型检验最重要的预测。** 它最大的贡献既是 955 个 TF 的功能图谱，也是把“高通量状态预测”推进到“动物体内因果验证”的完整链条。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Mapping Transcription Factor Functions in Astrocytes Using In Vivo Gain-of-Function Perturb-seq

### Motivation and Novelty

Astrocytes regulate synapses, glutamate handling, blood-brain barrier support, neuroinflammation, and neurodegenerative disease states. TFs are central regulators of these functions, but existing maps of astrocyte TF function are incomplete because many perturbation studies are in vitro, loss-of-function, or small-scale. The paper introduces iGOF-Perturb-seq, an in vivo gain-of-function platform that links barcoded TF overexpression to single-nucleus transcriptomes in astrocytes.

Compared with Perturb-seq (Cell, 2016) and CROP-seq (Nature Methods, 2016), the main novelty is not barcode-linked single-cell perturbation itself; it is the in vivo, astrocyte-targeted, ~1000-TF gain-of-function scale and the extension to pathological screening. Compared with recent in vivo CRISPR perturbation work such as Renz et al. (Nature, 2024), this study targets gain-of-function TF biology rather than smaller loss-of-function screens.

### Method Overview

The authors synthesize ~1200 mouse TF ORFs, retain 1089 QC-passing TF constructs, attach unique 16-bp barcodes, and package them into AAV-PHP.eB vectors under a short GFAP promoter. After systemic injection, ZsGreen+ cells are enriched and profiled by snRNA-seq. TF barcode reads are matched to cell barcodes, and analysis focuses on astrocytes with MOI = 1.

Downstream analysis compares each TF perturbation with ZsGreen controls to identify DEGs, uses marker-gene rules to nominate TFs for astrocyte functions, applies cNMF to identify gene programs and cofunctional TF modules, scores pathway effects with KEGG/GO/Reactome and UCell, and uses hdWGCNA to identify coexpression modules. Public disease datasets are then used to prioritize disease-associated TFs. A separate LPS inflammatory iGOF screen identifies Ferd3l as a candidate suppressor of reactive/neurotoxic astrocyte states, followed by 5XFAD mouse validation.

### Evaluation

The platform yields 130,341 MOI=1 cells, mostly astrocytes, and supports analysis of 955 TFs with at least three astrocytes per TF. Functional validations show that selected TFs predicted by marker analysis alter synaptogenesis, glutamate uptake, and phagocytosis. cNMF module analysis predicts Maff mitochondrial oxidative stress function, and arrayed validation supports that prediction. Pathway and hdWGCNA analyses identify TF groups converging on neurodegenerative disease-like, metabolic, synaptic, and inflammatory programs.

The strongest disease result is Ferd3l. Under LPS-induced inflammation, Ferd3l suppresses immune-related KEGG pathways and reactive/neurotoxic astrocyte markers. In 5XFAD mice, astrocyte-specific Ferd3l overexpression improves Y-maze and novel object recognition performance, reduces C3/GFAP reactive astrocyte markers, partially rescues neuronal counts, and shifts snRNA-seq signatures toward reduced neuroinflammation and improved communication.

The main caution is that atlas-wide TF functions are predictions unless individually validated. Disease-associated TF maps are signature-overlap hypotheses, not direct causal proof for every candidate.

### Reproducibility

Reproducibility rating: **4 / 5**.

The paper provides extensive methods, public sequencing accessions, named software versions, and a custom code archive at Zenodo. The acquired GitHub repository verifies the generic barcode extraction and assignment layer, including barcode correction, UMI-based chimera filtering, and barcode metadata merging. The Zenodo archive adds paper-specific scripts for MOI calling, Seurat DEG calling, pathway-correlation heatmaps, disease-correlation visualization, LPS immune-pathway ranking, CUT&Tag-DEG target overlap, and PPI hub-gene analysis.

The remaining limitations are practical rather than total absence of code. The full cNMF gene-program archive is large and was not downloaded in this targeted audit, the WGCNA archive contains only minimal material, and the 5XFAD cell-cell communication/phenotype analysis scripts were not found. The pipeline also depends on large raw data deposits, AAV library resources, and wet-lab steps that cannot be reproduced from code alone.

### Key Takeaway

iGOF-Perturb-seq is best understood as a scalable in vivo perturbation resource and screening framework. Its core biological contribution is a TF-function atlas for astrocytes and a demonstration that pathological-state screening can identify therapeutic-like regulators such as Ferd3l. Its core reproducibility limitation is that reproduction requires combining large public sequencing data, Zenodo analysis archives, and wet-lab resources; the generic barcode repository alone is insufficient.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
