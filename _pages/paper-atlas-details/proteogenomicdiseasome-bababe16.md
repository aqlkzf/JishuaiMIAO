---
layout: default
permalink: /paper-atlas/proteogenomicdiseasome-bababe16/
title: "ProteogenomicDiseasome"
nav: false
description: "血浆蛋白既可能参与疾病因果过程，也可能只是组织损伤、免疫反应或代偿机制的结果。单看患者血液中的蛋白–疾病相关性，很难区分原因与结果；单看遗传工具变量，又可能被水平多效性、错误效应基因和测量平台偏差误导。这项研究的目标，是把大规模蛋白 pQTL、疾病 GWAS 和实测蛋白的前瞻/患病关联放进同一框架，形成“遗传调控—疾病风险—血液标志物”的证据三角。"
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
      <span>Atlases &amp; Resources</span>
      <span>Cell · 2026</span>
    </div>
    <h1>ProteogenomicDiseasome</h1>
    <p>Multi-cohort proteogenomic analyses reveal genetic effects across the proteome and diseasome</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2026.03.049" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 蛋白质组–疾病组图谱：从 pQTL 到疾病机制与生物标志物的证据三角化

### 1. 研究问题：血浆蛋白变化究竟意味着什么

血浆蛋白既可能参与疾病因果过程，也可能只是组织损伤、免疫反应或代偿机制的结果。单看患者血液中的蛋白–疾病相关性，很难区分原因与结果；单看遗传工具变量，又可能被水平多效性、错误效应基因和测量平台偏差误导。这项研究的目标，是把大规模蛋白 pQTL、疾病 GWAS 和实测蛋白的前瞻/患病关联放进同一框架，形成“遗传调控—疾病风险—血液标志物”的证据三角。

研究对 38 个队列、最多 78,664 名欧洲血统参与者中测量的 1,161 个血浆蛋白靶标进行汇总分析。结果得到 14,690 个区域 sentinel variants，并经贝叶斯精细定位形成 24,738 个独立 credible sets，覆盖 1,116 个蛋白。这里的规模很重要，但更重要的是作者明确区分了 *cis*-pQTL 与 *trans*-pQTL：前者靠近编码该蛋白的基因，通常具有更清晰的生物学先验；后者可能通过分泌、糖基化、受体–配体、蛋白复合物或远端组织途径改变循环蛋白，信息更丰富，也更容易多效。

### 2. 第一层：从多队列蛋白 GWAS 到可信 pQTL

每个队列先对蛋白水平做 GWAS，再通过 METAL 合并效应。固定效应逆方差模型通常可写为：

$$\hat\beta=\frac{\sum_k w_k\hat\beta_k}{\sum_k w_k},\qquad w_k=\frac{1}{SE_k^2}.$$

论文 Methods 明确描述 fixed-effects inverse-variance meta-analysis，并对变异质量、等位基因频率、异质性和蛋白数做校正。公开脚本确实声明 marker、allele、EAF、beta、SE，并过滤 `INFO>0.8` 与 `0.001≤EAF≤0.999`；但最后调用的是 `ANALYZE RANDOM`（`01_meta_analysis/00_METAL_script.sh:1-18,52-55`）。这是本工作区最重要的纸码差异：公开文件可能是示例模板，而不是产生论文最终数字的完整命令。不能因为文件名叫 METAL 就把论文的固定效应结果视为已由该脚本逐字复现。

作者再用 SuSiE 对每个区域精细定位。SuSiE 把区域关联信号表示为若干个稀疏单效应之和，并为每个变异给出 posterior inclusion probability（PIP）及 credible-set 归属。代码尝试不同的信号数 $L=2\ldots10$，导出每个变异的 PIP 和每个 credible set 的 top variant（`02_finemapping/01_susie_finemapping.R:141-160,214-230`）。

另一个差异是 LD 清理阈值：论文写 credible set 代表变异间不应有 $r^2>0.1$，代码实际用 `value >= .25` 排除 top variants 仍高度相关的候选模型（同文件 `174-205`）。因此 24,738 credible sets 是论文报告的结果，但仅凭公开脚本和缺失的私有输入不能从头重算并确认该精确数量。

### 3. 第二层：为什么 *trans*-pQTL 需要效应基因指派

一个 *trans*-pQTL 可以离目标蛋白的编码基因很远。作者不是简单把最近基因当作 effector，而是在 1 Mb 窗口收集多类证据：距离与 VEP 后果、GTEx 共定位、rare-variant burden、OmniPath 配体–受体/复合物关系，以及 KEGG/Reactome 通路共享。

由于缺少通用“真值”标签，作者构建三套 pseudo-true-positive（PTP）：已知配体–受体或复合物、功能性变异、以及显著 gene burden。每一套都训练 10 个随机森林：按 LD 区域而非蛋白划分 70/30 训练测试，使用重复三折交叉验证、ROSE 采样处理类别失衡，并用 Kappa 选择模型（`03_trans_pQTL_assignment/gene_annotator.R:32-84`）。对候选基因，三套分类器各取 10 个模型预测概率的中位数，再相加为 0–3 的 candidate gene score。

这个分数是“多源注释与已知正例相似度”，不是某基因成为真正效应基因的后验概率。PTP 标签本身带有知识库偏好；强研究基因、经典通路和蛋白互作更容易获得高分。论文用 STRING PPI 做部分外部验证并报告 552 个重叠，但公开仓库中没有清楚的 STRING 验证流程，因此该精确数字保持 `Not found` 边界。

Figure 3 进一步把高分 effector genes 投影到通路、组织和细胞类型。N-linked glycosylation、血小板和肝细胞等富集说明许多循环蛋白的 *trans* 调控来自加工、分泌与跨器官稳态，而非目标蛋白自身基因附近。这是富集证据，不代表所有命中基因都在同一细胞内直接调控目标蛋白。

### 4. 第三层：多效性既是信号，也是 MR 的危险源

Figure 4 显示大量 *trans*-pQTL 同时关联多个蛋白和非蛋白表型。作者按“蛋白数”和“GWAS 表型数”区分 molecular、phenotypic 与 unspecific pleiotropy。多效性有两面：它能揭示 LTBR、糖基化或免疫通路等系统机制，也会破坏 MR 的排除限制假设。

研究用 *cis*-pQTL、特异 *trans*-pQTL，以及二者组合构造不同 instrument sets。对多个工具变量，逆方差加权 MR 可写为：

$$\hat\theta_{IVW}=\frac{\sum_j w_j\,(\beta_{Yj}/\beta_{Xj})}{\sum_j w_j}.$$

代码实现单/双 SNP IVW、多 SNP多方法 MR、Cochran Q 和 leave-one-out 异质性筛除（`04_cis_MR_coloc_FinnGen/02_github_MR_pipeline.R:190-280`）。值得注意的是，代码将“异常”定义为去掉某 SNP 后的 $Q$ 低于 `median(Q)-3SD`；它操作性地寻找造成高异质性的工具，但并不保证清除所有水平多效。

作者同时要求蛋白与疾病在区域内共定位。共定位的 PP H4>0.8 表示两种性状较可能共享同一遗传信号，能降低“同一区域不同因果变异”的错误解释；但共享变异仍可能通过另一条路径同时影响蛋白和疾病，所以 MR+coloc 是更强的遗传支持，不是绝对因果证明。

Figure 5 最有价值的地方是展示反例：有些 *cis* 与 *trans* MR 一致，如 PCSK9–冠心病；有些却不支持甚至方向相反，如 SOST。论文由此说明，盲目加入 *trans*-pQTL 会显著降低与 *cis* 结果的一致性。不同来源的调控可能改变“血浆测得的蛋白量”，却不等价于改变疾病相关组织中的蛋白功能。

### 5. 第四层：实测蛋白与疾病发生的观察性证据

UK Biobank 的 biomarker 分析把疾病分成 prevalent 与 incident。对 incident disease，代码先排除入组前病例和前六个月事件，以减少反向因果，然后以年龄为时间尺度拟合 Cox 模型，并检查 Schoenfeld residuals；还按 2、5、10、18 年窗口估计时间变化效应（`05_biomarker_analysis/02_github_association_testing.R:45-116`）。对 prevalent disease，则使用 logistic regression。

Cox 模型形式为：

$$h(t\mid P,C)=h_0(t)\exp(\beta_P P+\gamma^\top C),$$

其中 $P$ 是标准化蛋白水平，$C$ 包括性别、BMI、吸烟、饮酒、技术变量等。即使调整充分，$\beta_P$ 仍可能反映亚临床疾病、药物、器官功能或其他未测混杂。因此 Figure 6 的关键不是报告海量显著 biomarker，而是将其与遗传结果比较：52,887 个显著前瞻蛋白–疾病关联中，只有极少数获得方向一致的高置信遗传支持；遗传支持的 193 对中，也只有不到四分之一与 biomarker 方向一致。

这类不一致不是分析失败，而是研究的主要信息：遗传效应接近终身微小扰动，实测蛋白是特定时点的综合状态读数，两者回答的问题不同。补偿机制和组织内/循环池差异都能造成方向不一致。

### 6. 疾病组与药物重定位应怎样解释

Figure 6–7 把 pQTL 关联的蛋白集合与疾病 biomarker signatures 做富集，并结合 pQTL 本身是否为相同疾病的 GWAS locus。例如 SHROOM3 位点关联的蛋白集合富集于 proteinuria biomarker，提示循环蛋白谱可以读取肾脏致病过程。TYK2 missense variant 对多种免疫蛋白的 *trans* 作用，与类风湿关节炎、银屑病和甲状腺功能减退风险以及 TYK2 抑制剂适应证相吻合。

这些结果适合用于机制假设、患者分层或药物重定位优先级，不应直接写成临床疗效证明。一个药物靶点的遗传模拟通常是终身、低强度且方向特定的，真实药物则有剂量、组织分布和脱靶效应；循环蛋白 signature 也需要独立临床队列验证。

### 7. 七张主图的阅读顺序

- Figure 1：全基因组 *cis/trans*-pQTL 与 credible-set 图谱。
- Figure 2：哪些蛋白结构与分泌特征更容易受到遗传调控。
- Figure 3：*trans* effector genes 指向糖基化、血小板、肝脏和细胞类型通路。
- Figure 4：蛋白层与疾病层的多效性分类及通路解释。
- Figure 5：*cis* 与特异 *trans* MR 的一致和冲突。
- Figure 6：遗传推断、incident biomarker、prevalent biomarker 的三角比较。
- Figure 7：TYK2 等位点如何连接免疫蛋白 signature、疾病风险与药物重定位。

最稳妥的总结是：本研究不是用单一 MR 宣布“蛋白导致疾病”，而是系统展示哪些结论在 *cis* 遗传、*trans* 调控、共定位和实测 biomarker 之间收敛，哪些则明确冲突。它的价值正来自把冲突保留下来；主要复现边界则是公开脚本为示例性归档、私有中间数据缺失，以及 METAL 与精细定位阈值存在纸码差异。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Multi-Cohort Proteogenomic Diseasome

### Motivation And Novelty

Most disease-associated variants are non-coding, making it difficult to identify the genes and mechanisms that connect genetic risk to disease. Plasma proteins are useful intermediates because they are measurable at scale, can act as biomarkers, and often sit close to drug-target biology. Prior proteogenomic resources established many protein quantitative trait loci (pQTLs), but disease interpretation has often relied on *cis*-pQTLs near a protein's cognate gene.

This study extends that view by treating *trans*-pQTLs as interpretable biological signals rather than only as pleiotropic liabilities. The paper combines proteogenomic meta-analysis across 38 studies and up to 78,664 participants, identifies 24,738 fine-mapped pQTL credible sets across 1,116 proteins, assigns candidate effector genes for distal loci, and triangulates pQTL evidence with disease genetics and measured-protein biomarker associations.

Compared methods and resources:

| Method / Resource | Journal | Year | Role In This Paper |
|---|---:|---:|---|
| Sun et al. plasma proteomic GWAS | Nature | 2018 | Prior broad plasma proteogenomic atlas, mostly smaller and less trans-mechanism focused |
| Ferkingstad et al. plasma proteome genetics | Nature Genetics | 2021 | Prior large plasma proteome genetics resource |
| Pietzner et al. proteo-genomic disease convergence | Science | 2021 | Prior protein-disease convergence framework emphasizing genetic evidence |
| Sun et al. UK Biobank plasma proteomics | Nature | 2023 | UKBB Olink proteogenomic resource used as a key comparison/input context |
| Eldjarn et al. plasma proteomics comparisons | Nature | 2023 | Large plasma proteomics genetics/disease comparison resource |
| Dhindsa et al. rare-variant protein associations | Nature | 2023 | Rare-burden evidence used as candidate effector-gene annotation |
| ProGeM | Nucleic Acids Research | 2019 | Inspiration for candidate causal gene prioritization at molecular QTLs |

### Method Overview

The pipeline starts from Olink plasma protein measurements and genotype data. Cohort-level protein GWAS summary statistics are meta-analyzed, regional sentinel loci are selected, and SuSiE fine-mapping produces independent credible variant sets. pQTLs are labeled as *cis* or *trans* using a 500 kb cognate-gene boundary and are filtered for confidence using significance, direction, and heterogeneity rules.

The central interpretive step is *trans*-pQTL effector-gene assignment. For genes near distal loci, the paper collects annotations such as distance, VEP consequence, GTEx colocalization, rare-burden evidence, ligand-receptor links, protein-complex membership, and KEGG/Reactome pathway links. Three Random Forest classifier families are trained from pseudo-true-positive sets and their median prediction scores are summed into a candidate-gene score.

Top trans effector genes are then analyzed for pathway, tissue, and cell-type enrichment. This reveals N-linked glycosylation, platelet biology, cytokine/immune pathways, hepatocytes, and immune-cell types as recurring regulatory systems for circulating proteins. Disease follow-up combines cis/trans MR, colocalization, GWAS Catalog pleiotropy, UKBB Cox models for incident disease, logistic models for prevalent disease, and pQTL-protein signature overlap tests.

### Evaluation

The paper's main empirical result is the scale and structure of the pQTL catalog: 14,690 regional sentinel variants and 24,738 fine-mapped pQTL credible sets, including 5,040 *cis* and 19,698 *trans* pQTLs. Most fine-mapped pQTLs pass high-confidence criteria. The figures show that distal trans regulation is pervasive rather than incidental.

The biological evaluation is strongest at the systems level. Protein features associated with secretion and processing predict pQTL architecture. Random Forest-prioritized trans effector genes enrich for coherent pathways and cell types, with N-linked glycosylation as the dominant recurring pathway. Pleiotropy analysis shows that many trans loci bridge protein associations and disease-associated GWAS regions.

The disease evaluation is appropriately cautious. cis MR and colocalization identify high-confidence protein-disease links, but cis and trans instruments can disagree. Genetic and measured-protein biomarker evidence overlap only partly. The paper uses this non-convergence as a core point: genetically causal targets, distal regulators, and clinically useful measured biomarkers are related but not interchangeable.

The translational examples are plausible but hypothesis-generating. FURIN and cardiovascular disease, NT-proBNP and heart failure, SHROOM3 and proteinuria, and TYK2-linked autoimmune protein signatures show how the catalog can generate mechanistic and repurposing hypotheses. These examples still require experimental or clinical validation before being treated as drug-development conclusions.

### Reproducibility

**Rating: 3 / 5.**

The analysis is conceptually reproducible and the released repository contains scripts for the major stages: METAL meta-analysis, SuSiE fine-mapping, trans-pQTL effector-gene assignment, pathway/tissue/cell enrichment, MR/colocalization, and biomarker association testing. The code aligns well with many STAR Methods details.

The score is not higher because the repository is not a runnable package. Its README states that the scripts are illustrative, many scripts contain private paths and missing intermediate data, and no environment lockfile or test workflow is provided. Exact numerical claims depend on cohort data, UKBB access, FinnGen files, curated annotations, GWAS Catalog snapshots, and generated intermediate tables that are not included. A notable ambiguity is that the released METAL script calls `ANALYZE RANDOM`, while the paper describes inverse-variance fixed-effects meta-analysis.

The practical result: a knowledgeable analyst with access to the same private data and annotations could reconstruct the workflow, but an outside reader cannot reproduce the full paper end to end from the public repository alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
